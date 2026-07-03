---
type: Article
title: "Redis Rate Limiting — Solving Distributed Race Conditions"
source: "https://medium.com/@kanishks772/how-big-tech-actually-solves-distributed-race-conditions-using-redis-b676e12ea0b8"
author: "The Latency Gambler"
published: 2026-05-19
created: 2026-07-03
description: "Rate limiting across distributed servers using Redis — token bucket with Lua, sorted-set rolling windows, concurrent request limiting, and load shedding, with production patterns from Stripe and ClassDojo."
tags:
  - redis
  - rate-limiting
  - distributed-systems
  - race-conditions
  - lua
  - sorted-sets
  - load-shedding
---

# Redis Rate Limiting — Solving Distributed Race Conditions

Rate limiting is one of those things every developer thinks they understand until they actually have to build it. Slap a counter in Redis, increment it on each request, block when the count gets too high. Done, right?

Not quite. The moment you have more than one server — which is basically always in production — the naive approach breaks in subtle ways that are hard to debug and embarrassing to explain to your users.

This article walks through exactly how production systems at companies like ClassDojo and Stripe approach this problem: what goes wrong with simple implementations, why Redis is the right tool for the distributed case, and the four patterns that actually hold up under real load.

## Why Rate Limiting Is Harder Than It Looks

Before diving into solutions, it's worth being precise about what you're actually trying to solve. Most rate limiting requirements have three dimensions:

1. **How many requests per time window?** (10/minute, 100/second)
2. **What kind of window?** (fixed vs. rolling)
3. **Are you limiting per user, per endpoint, or globally?**

The third question is about *where* the state lives. In a single-process application, you can keep counters in memory. In a distributed system — multiple servers handling requests for the same user — every server needs to see the same counter. That means the state must live outside any individual server.

Redis is the standard answer for this. It's fast (sub-millisecond), it supports atomic operations, and it's designed exactly for shared mutable state across multiple clients.

**Naive architecture (broken):**

```
User request ──> Server A ──> Counter in Server A's memory
              ──> Server B ──> Counter in Server B's memory

Server A thinks user made 8 requests.
Server B thinks user made 6 requests.
User actually made 14 requests.
Nobody blocked them.
```

**Correct architecture:**

```
User request ──> Server A ─┐
             ──> Server B ─┼──> Redis (shared counter)
             ──> Server C ─┘

All servers read and write the same counter.
Limiting actually works.
```

## The Race Condition Nobody Talks About

Moving state to Redis solves the distribution problem but introduces a new one: the race condition.

Consider the token bucket algorithm — the classic approach to rate limiting:

- Each user has a "bucket" of tokens. Each request costs one token.
- Tokens refill over time, up to some maximum capacity.
- If the bucket is empty, the request is rejected.

Here's the broken multi-process version:

```
User has 1 token remaining.

Server A                   Redis                   Server B
────────────────────────────────────────────────────────
GET user:tokens ──────────────────────────────────────>  returns 1
                 <────────────────────────────────────── returns 1 (same time)
GET user:tokens  <──────────────────────────────────────
A sees 1 token, decides "allow"
B sees 1 token, decides "allow"
A: SET user:tokens 0 ──────────────────────────────────>
B: SET user:tokens 0 ──────────────────────────────────>
Both requests went through. The user got 2 for the price of 1.
```

This is a classic **check-then-act race condition**. Between the check (reading the count) and the act (updating the count), another process sneaks in and reads the same stale value.

The fix has to be atomic — the read and write need to happen as a single, uninterruptible operation.

## Approach 1: Token Bucket with Lua (Stripe's Method)

The Stripe engineering team published the canonical solution to this: execute the entire check-and-update logic inside a **Lua script** on Redis.

Lua scripts in Redis execute atomically. No other Redis operation runs while a script is executing. The race condition above is impossible because the read and write are the same operation.

Here's the concept in pseudocode:

```
# Request comes in for user_id
# We have two Redis keys:
#   user_id.tokens     -> how many tokens remain
#   user_id.timestamp  -> when tokens were last calculated

1. Read current tokens and last timestamp
2. Calculate how many tokens have been replenished since last check
3. If replenished + remaining >= requested → allow, subtract tokens
4. Otherwise → reject with 429
5. Write new token count and timestamp atomically
```

And here's the actual Lua script that runs in Redis:

```lua
local tokens_key = KEYS[1]      -- "rate_limiter.user_123.tokens"
local timestamp_key = KEYS[2]   -- "rate_limiter.user_123.timestamp"

local rate      = tonumber(ARGV[1])  -- tokens per second to replenish
local capacity  = tonumber(ARGV[2])  -- maximum tokens in bucket
local now       = tonumber(ARGV[3])  -- current unix timestamp
local requested = tonumber(ARGV[4])  -- tokens this request costs (usually 1)

-- How long until bucket is fully replenished (used for TTL)
local fill_time = capacity / rate
local ttl = math.floor(fill_time * 2)

-- Read current state (default to full bucket on first request)
local last_tokens = tonumber(redis.call("get", tokens_key))
if last_tokens == nil then
  last_tokens = capacity
end
local last_refreshed = tonumber(redis.call("get", timestamp_key))
if last_refreshed == nil then
  last_refreshed = 0
end

-- Calculate tokens earned since last request
local delta = math.max(0, now - last_refreshed)
local filled_tokens = math.min(capacity, last_tokens + (delta * rate))

-- Decision: allow or reject
local allowed = filled_tokens >= requested
local new_tokens = filled_tokens
if allowed then
  new_tokens = filled_tokens - requested
end

-- Write new state (with TTL to auto-clean idle users)
redis.call("setex", tokens_key, ttl, new_tokens)
redis.call("setex", timestamp_key, ttl, now)
return { allowed, new_tokens }
```

And the application-side caller:

```ruby
REPLENISH_RATE = 100   # tokens per second
CAPACITY = 500         # burst capacity (5 seconds of full rate)

def check_rate_limit(user_id)
  keys = [
    "rate_limiter.#{user_id}.tokens",
    "rate_limiter.#{user_id}.timestamp"
  ]
  args = [REPLENISH_RATE, CAPACITY, Time.now.to_i, 1]

  begin
    allowed, tokens_left = redis.eval(SCRIPT, keys, args)
  rescue RedisError => e
    # Important: fail open. Redis being down shouldn't block your API.
    # Monitor this, but don't make Redis a hard dependency.
    logger.error("Redis rate limiter failed: #{e}")
    return  # allow the request
  end

  raise RateLimitError.new(429) unless allowed
end
```

There's an important design decision embedded in the `rescue` block: **fail open**. If Redis goes down, requests get through. The alternative — blocking all traffic when Redis is unreachable — turns a Redis outage into a site outage. Stripe reports their observed Redis failure rate at around 0.01%, making fail-open the right trade-off.

The token bucket also supports **bursting**. Setting `CAPACITY = 5 * REPLENISH_RATE` means a user who hasn't made requests in a while can burst up to 5 seconds of full-rate traffic before being throttled. This is the right behavior for most APIs — occasional bursts from a well-behaved client shouldn't be penalized.

## Approach 2: The Fixed Window Problem (and Why Rolling Windows Matter)

Before getting to the rolling window solution, it's worth understanding exactly what's wrong with fixed windows.

Imagine a limit of 100 requests per minute with a fixed 60-second window:

```
Time:        :00        :60        :120
Window:       [----A----][----B----][----C----]

Attack:
  At :59 → 100 requests (fills window A)
  At :61 → 100 requests (fills window B)

Result: 200 requests in 2 seconds. No throttling triggered.
```

Because the window resets at `:60`, a user can send a burst at the end of one window and the start of the next, effectively doubling the allowed rate.

A **rolling window** solves this. Instead of "100 requests in this calendar minute," it's "100 requests in any 60-second span ending right now." The window always ends at the present moment.

```
Fixed window (broken):

    :50    :59 :00    :10
    ──────────|──────────
    100 req   | 100 req      <-- 200 req in 20 seconds. Allowed.

Rolling window (correct):
   :50    :59 :00    :10
    ──────────|──────────
    100 req   | checking last 60s... already at 100. Blocked.
```

## Approach 3: Sorted Sets for Rolling Windows (ClassDojo's Method)

The ClassDojo engineering team solved the rolling window problem using [Redis sorted sets](https://redis.io/docs/data-types/sorted-sets/). The key insight: instead of tracking a count, track the actual timestamps of every request. A sorted set is the right data structure for this because:

- Elements are sorted by score (which you set to the timestamp)
- You can remove all elements older than one interval in a single O(log n) command
- The size of the set tells you exactly how many requests happened in the window
- **All operations can be wrapped in a single MULTI/EXEC block** making the whole thing atomic

Here's the algorithm:

```
For user_id and limit of MAX_REQUESTS per INTERVAL:

1. ZREMRANGEBYSCORE user_id 0 (now - INTERVAL)
   → Drop all timestamps older than one interval

2. ZRANGE user_id 0 -1
   → Fetch all remaining timestamps (requests in the window)

3. ZADD user_id now now
   → Record this request attempt

4. EXPIRE user_id INTERVAL
   → Auto-clean after inactivity

5. Count the results from step 2.
   If count >= MAX_REQUESTS → reject (429)
   Else → allow
```

All four Redis commands execute inside a `MULTI` / `EXEC` block — Redis's equivalent of a transaction. Because they're atomic, two simultaneous requests see each other's additions. No race condition.

Here's the Node.js implementation:

```javascript
const redis = require('redis');
const client = redis.createClient();

async function isRateLimited(userId, maxRequests, intervalMs) {
  const now = Date.now();               // microsecond precision timestamp
  const windowStart = now - intervalMs; // oldest allowed timestamp
  const key = `rate_limit:${userId}`;

  // All operations in one atomic block
  const results = await client
    .multi()
    .zremrangebyscore(key, 0, windowStart)   // remove old entries
    .zrange(key, 0, -1)                       // fetch remaining
    .zadd(key, now, now.toString())           // record this attempt
    .expire(key, Math.ceil(intervalMs / 1000)) // set TTL
    .exec();

  const requestsInWindow = results[1].length; // count before this request
  return requestsInWindow >= maxRequests;
}

// Usage
async function handleRequest(req, res, next) {
  const limited = await isRateLimited(
    req.user.id,
    100,   // 100 requests
    60000  // per 60 seconds
  );
  if (limited) {
    return res.status(429).json({ error: 'Rate limit exceeded' });
  }
  next();
}
```

ClassDojo's implementation also adds a `minDifference` parameter — a minimum gap between consecutive requests. This prevents bursting even within the allowed rate:

```javascript
// After fetching the sorted set entries:
const lastRequestTime = entries[entries.length - 1]; // most recent
const timeSinceLast = now - parseInt(lastRequestTime);

if (timeSinceLast < MIN_DIFFERENCE_MS) {
  // Too soon after last request, even if overall count is fine
  return { limited: true, retryAfter: MIN_DIFFERENCE_MS - timeSinceLast };
}
```

**Trade-off**: In this implementation, **blocked requests still get recorded in the sorted set**. If a user keeps hammering after being blocked, each blocked attempt counts toward the window. This means a constantly-over-limit user stays over-limit indefinitely — which is actually the right behavior for abuse cases.

## Approach 4: Concurrent Request Limiting

Rate limiting by count-per-window is great for most APIs. But some workloads are better controlled by **concurrent requests** — how many requests are in-flight at the same time, not how many happened per second.

This is useful for expensive operations: database migrations, report generation, video transcoding. You don't want 50 concurrent users each kicking off a report that takes 30 seconds.

The implementation uses a sorted set differently — as an active request tracker:

```
When request starts:
  1. Clean up entries older than TTL (stale requests that never finished)
  2. Count current in-flight requests
  3. If count < capacity → add this request's unique ID to the set → allow
  4. If count >= capacity → reject with 429

When request finishes:
  5. Remove this request's unique ID from the set
```

Here's the Lua script for the check (atomic `ZCARD` + `ZADD`):

```lua
-- concurrent_requests_limiter.lua
local key      = KEYS[1]
local capacity = tonumber(ARGV[1])
local timestamp = tonumber(ARGV[2])
local id       = ARGV[3]   -- unique ID for this request

local count   = redis.call("zcard", key)   -- current concurrent count
local allowed = count < capacity

if allowed then
  redis.call("zadd", key, timestamp, id)   -- mark this request as active
end

return { allowed, count }
```

And the application wrapper:

```ruby
TTL = 60       # seconds: max allowed request duration
CAPACITY = 20  # max concurrent requests per user

def handle_request(user_id)
  request_id = SecureRandom.hex(8)  # unique per request
  key = "concurrent_requests:#{user_id}"

  # Clean out requests that started but never finished (crashed workers)
  redis.zremrangebyscore(key, '-inf', Time.now.to_i - TTL)

  # Atomic check + add
  allowed, count = redis.eval(
    CONCURRENT_SCRIPT,
    [key],
    [CAPACITY, Time.now.to_i, request_id]
  )
  raise RateLimitError.new(429) unless allowed

  begin
    yield  # do the actual work
  ensure
    # Always clean up, even if the request fails
    redis.zrem(key, request_id)
  end
end
```

The `ensure` block is critical. Whether the request succeeds or fails, the entry gets removed. Without it, any exception would leave a ghost entry that counts against the user's concurrent limit until TTL expiry.

## Approach 5: Load Shedding (When Rate Limiting Isn't Enough)

The patterns above protect individual users from themselves. Load shedders protect the system from everyone at once — including legitimate traffic that's overwhelming the infrastructure.

Stripe's approach categorizes requests by priority. Critical traffic (payment processing) is never shed. Non-critical traffic (analytics, reporting) gets dropped first.

```
Worker utilization thresholds:

  0% ──── 70%:  Normal. No shedding.
  70% ─── 80%:  Dead zone. Watch but don't act.
  80% ─── 100%: Start shedding non-critical traffic.
                Probability of rejection increases linearly.
```

```
Architecture with load shedding:

Internet ──> Load Balancer ──> API Servers
                                    │
                               [Check worker utilization]
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
             utilization < 70%              utilization > 80%
                    │                               │
            Allow all traffic           Shed non-critical traffic
                                        (analytics, reports, etc.)
                                        Keep critical traffic
                                        (payments, auth)
```

The key design principle: shedding must be *gradual*. Don't start dropping traffic the moment utilization crosses 80%. Wait 28+ seconds to confirm it's sustained, not a measurement spike. And don't instantly drop all non-critical traffic — ramp up over ~2 minutes. Sharp changes in shedding cause oscillation and unpredictable failure modes.

```python
# Pseudocode for gradual load shedding
class WorkerUtilizationShedder:
    SHED_START_DELAY = 28      # seconds before shedding begins
    FULL_SHED_RAMP_TIME = 120  # seconds to reach 100% shed rate

    def should_shed(self, utilization):
        if utilization < 0.7:
            # Healthy - reduce shed amount gradually
            self.adjust_shed_rate(decrease=True)
        elif utilization < 0.8:
            # Dead zone - hold current rate
            pass
        else:
            # Overloaded - increase shed amount gradually
            self.adjust_shed_rate(increase=True)
        return random.random() < self.current_shed_probability
```

## Putting It Together: A Production Architecture

Here's how these patterns layer in a real system:

```
Incoming Request
       │
       ▼
┌──────────────────────────────┐
│  Layer 1: Request Rate Limit │  (Token Bucket / Sorted Set)
│  "Is this user over their    │
│   per-second/per-minute cap?"│
└──────────────┬───────────────┘
               │ pass
               ▼
┌──────────────────────────────┐
│  Layer 2: Concurrent Limit   │  (Sorted Set as active tracker)
│  "Is this user running too   │
│   many expensive ops at once?"│
└──────────────┬───────────────┘
               │ pass
               ▼
┌──────────────────────────────┐
│  Layer 3: Load Shedder       │  (Worker utilization check)
│  "Is the system itself under │
│   pressure right now?"       │
└──────────────┬───────────────┘
               │ pass
               ▼
        Application Logic
```

Each layer has a different job. Layer 1 protects against individual user abuse. Layer 2 protects against resource exhaustion from concurrent operations. Layer 3 protects the system as a whole from overload, regardless of who's causing it.

## Comparison: Which Algorithm for Which Problem?

| Algorithm | Use when... |
|:---|:---|
| **Fixed Window** | Accuracy doesn't matter much. Simple systems. (Vulnerable to boundary bursting) |
| **Token Bucket (Lua script)** | Bursty but average-rate-bounded traffic. API limits that allow short bursts. Single atomic script = no race conditions. |
| **Rolling Window (Sorted Set)** | Strict rate enforcement. No boundary gaming. Push notifications, SMS, email rate limits. Space cost: O(requests in window) |
| **Concurrent Limiter (Sorted Set)** | Expensive long-running operations. DB migrations, report generation, uploads. Not about time window — about active count. |
| **Load Shedder** | System-wide overload protection. Protecting critical traffic during incidents. |

## The Redis Properties That Make This Work

It's worth pausing on *why* Redis is the right tool here, not just a popular one.

**Single-threaded command execution.** Redis processes commands one at a time. This means individual commands like `INCR`, `ZADD`, or `ZCARD` are inherently atomic. No two clients can interleave inside a single command.

**Lua scripts are atomic.** Everything inside `redis.eval()` runs as one uninterruptible unit. This is what makes the token bucket Lua script race-condition-free.

**MULTI/EXEC blocks are atomic.** The sorted set approach wraps multiple commands in a transaction. All or nothing — no interleaving from other clients.

**Key expiry.** `EXPIRE` and `SETEX` allow automatic cleanup of rate limit keys when users go idle. No separate garbage collection process needed.

The combination of these properties makes Redis uniquely suited for rate limiting in distributed systems — not because it's fast (though it is), but because it gives you the right atomicity guarantees at the right granularity.

## What Every Junior Engineer Should Take Away

**Race conditions are silent.** The broken token bucket doesn't crash. It doesn't log errors. It just lets a few extra requests through. In production, you won't notice until you're getting spam complaints or your database melts.

**Atomicity is not optional in distributed systems.** Anytime you read-then-write shared state across a network, you have a potential race. The fix is always some form of atomic operation — Lua scripts, MULTI/EXEC, or a compare-and-swap.

**The right data structure matters.** A sorted set isn't just a set with ordering. Its range-delete-by-score operation is what makes rolling windows efficient. Understanding your data structures saves you from building complex state machines to solve problems your database already solves natively.

**Fail open on infrastructure dependencies.** If your rate limiter goes down, the correct behavior is usually to let traffic through — not to treat every request as blocked. A Redis outage shouldn't be indistinguishable from a DDoS.

**Layer your defenses.** No single algorithm handles every scenario. Per-user limits, concurrent operation limits, and system-wide load shedding each solve a different failure mode.

## Sources

- ClassDojo Engineering: "Better Rate Limiting With Redis Sorted Sets" — <https://engineering.classdojo.com/blog/2015/02/06/rolling-rate-limiter/>
- Paul Tarjan (Stripe): "Scaling your API with rate limiters" — <https://gist.github.com/ptarjan/e38f45f2dfe601419ca3af937fff574d>
