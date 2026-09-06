---
type: System Design
title: "Redis Rate Limiting Patterns — Key Takeaways"
description: "Atomic token bucket with Lua, sorted-set rolling windows, concurrent request limiting, gradual load shedding, and fail-open pattern — production patterns from Stripe and ClassDojo for distributed rate limiting."
generated: { by: process:okf-migrate, at: 2026-07-03T00:00:00Z }
---

# 62. Redis Rate Limiting Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Redis Rate Limiting — Solving Distributed Race Conditions](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)
> **Purpose**: Extract reusable distributed rate limiting patterns using Redis atomic primitives — token bucket, rolling windows, concurrent limiting, and load shedding.

> **Also see**: [Redis Internals](redis-internals.md) — I/O multiplexing, hash slots, COW persistence, Morris counter, UNLINK
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — Redis sorted sets, TTL; [Data Concurrency](../../reference-dictionary/data-concurrency.md) — Distributed lock, atomic conditional update; [API Design](../../reference-dictionary/api-design.md) — Rate limiting, hierarchical rate limiting
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-17](#cache-17) | Check-then-act race condition lets multiple servers consume the same token | Atomic token bucket via Lua script (`redis.eval`) |
| [cache-18](#cache-18) | Fixed windows allow 2× bursting at window boundaries | Sorted-set rolling window with MULTI/EXEC atomic block |
| [cache-19](#cache-19) | Count-per-window doesn't protect against concurrent resource exhaustion | Concurrent request limiter using sorted set as active tracker |
| [cache-20](#cache-20) | Rate limiting dependency becomes a single point of failure | Fail-open pattern — allow traffic when Redis is unreachable |
| [cache-21](#cache-21) | System-wide overload from legitimate traffic overwhelms infrastructure | Gradual load shedding with priority classification and ramp |

---

## cache-17: Atomic Token Bucket via Lua Script

> **Source**: [§"Approach 1: Token Bucket with Lua"](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)

| | |
|:---|:---|
| **Problem** | In a distributed rate limiter, Server A reads `tokens=1`, Server B reads `tokens=1` simultaneously — both decide "allow" and both deduct, giving the user 2 requests for the price of 1 |
| **Root cause** | Classic **check-then-act race condition**: the read and write are separate operations across the network, creating a window where another process reads stale state |

**Strategy**: Execute the entire check-and-update logic inside a **Lua script** on Redis. Lua scripts in Redis run atomically — no other command interleaves. The read (get tokens), calculation (replenish), decision (allow/reject), and write (set new tokens) happen as one uninterruptible unit.

```lua
-- Core logic (simplified):
local last_tokens = redis.call("get", tokens_key) or capacity
local delta = math.max(0, now - last_refreshed)
local filled_tokens = math.min(capacity, last_tokens + (delta * rate))
local allowed = filled_tokens >= requested
if allowed then
  redis.call("setex", tokens_key, ttl, filled_tokens - requested)
end
return { allowed, new_tokens }
```

The token bucket also supports **burst tolerance**: setting capacity higher than rate allows well-behaved clients to burst after idle periods without being penalized. Stripe uses `CAPACITY = 5 * REPLENISH_RATE`.

| Tradeoff | Detail |
|:---|:---|
| **Redis dependency** | If Redis is down, rate limiting stops working — mitigated by fail-open (see cache-20) |
| **Lua script complexity** | Debugging atomic scripts is harder than application code; logic must be kept simple |
| **Burst vs. strict enforcement** | Token bucket allows short bursts (by design); use rolling windows when strict per-second limits are required |

> **Also see**: [Concurrency & Transactions](../concurrency-transactions/) — Atomic conditional update, distributed lock
> **Dictionary**: [Atomic Conditional Update](../../reference-dictionary/data-concurrency.md#atomic-conditional-update), [Rate Limiting](../../reference-dictionary/api-design.md#rate-limiting)
> **Azure**: Azure Cache for Redis supports Lua scripting (`EVAL`/`EVALSHA`); Premium tier provides Redis persistence for script recovery

---

## cache-18: Sorted-Set Rolling Window with MULTI/EXEC

> **Source**: [§"Approach 3: Sorted Sets for Rolling Windows"](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)

| | |
|:---|:---|
| **Problem** | Fixed-window rate limiting (e.g., 100 req/min with windows at `:00`–`:60`) allows an attacker to send 100 requests at `:59` and 100 at `:01` — 200 requests in 2 seconds with no throttling triggered |
| **Root cause** | Fixed windows reset at calendar boundaries; a burst straddling the boundary doubles the effective rate |

**Strategy**: Use a **Redis sorted set** where each member is a request timestamp and the score is the timestamp value. The window is "the last N seconds ending right now" — always rolling. All operations run inside a `MULTI`/`EXEC` block for atomicity:

```
1. ZREMRANGEBYSCORE key 0 (now - interval)  → drop expired timestamps
2. ZRANGE key 0 -1                          → fetch remaining (requests in window)
3. ZADD key now now                         → record this attempt
4. EXPIRE key interval                      → auto-cleanup TTL
5. If count >= MAX_REQUESTS → reject
```

**Java (Jedis)** — all four commands wrapped in a single `multi()`/`exec()` block:

```java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.Transaction;
import redis.clients.jedis.Response;

boolean isRateLimited(Jedis jedis, String userId, int maxRequests, long windowMs) {
    String key = "rate_limit:" + userId;
    long now = System.currentTimeMillis();
    long windowStart = now - windowMs;

    Transaction tx = jedis.multi();
    tx.zremrangeByScore(key, 0, windowStart);            // ① drop expired
    Response<Set<String>> rangeResp = tx.zrange(key, 0, -1); // ② fetch window
    tx.zadd(key, (double) now, String.valueOf(now));      // ③ record attempt
    tx.expire(key, (int) (windowMs / 1000));               // ④ auto-cleanup TTL
    tx.exec();

    int requestCount = rangeResp.get().size();             // count from ②
    return requestCount >= maxRequests;
}
```

> `Response<T>` is a deferred handle — its value is populated only after `exec()` completes. The entire block runs atomically: no other client can interleave between the `ZRANGE` count and the `ZADD`.

ClassDojo adds a `minDifference` parameter — a minimum gap between consecutive requests — preventing micro-bursts even within the allowed rate.

**Trade-off**: Blocked requests are still recorded in the sorted set, so a constantly-over-limit user stays over-limit indefinitely. This is correct for abuse cases but means recovery requires the user to stop sending requests entirely for a full window.

| Tradeoff | Detail |
|:---|:---|
| **Memory cost** | O(requests in window) — every request timestamp stored; acceptable for per-user limits (~100s of entries) but expensive for global counters |
| **Atomicity** | MULTI/EXEC guarantees no interleaving but doesn't roll back on failure; the ZADD always succeeds even if the limit was hit |
| **Precision** | Timestamp-based, so as precise as the clock resolution (milliseconds); no boundary gaming possible |

> **Also see**: [Caching Architecture](caching-architecture.md) — Cache stampede, request coalescing
> **Dictionary**: [Redis Sorted Sets](../../reference-dictionary/caching.md#redis-sorted-sets), [Rate Limiting](../../reference-dictionary/api-design.md#rate-limiting)
> **Azure**: Azure Cache for Redis supports all sorted-set commands (`ZREMRANGEBYSCORE`, `ZRANGE`, `ZADD`) and MULTI/EXEC transactions

---

## cache-19: Concurrent Request Limiting via Active Tracker

> **Source**: [§"Approach 4: Concurrent Request Limiting"](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)

| | |
|:---|:---|
| **Problem** | Count-per-window rate limiting (e.g., 100 req/min) doesn't prevent 50 users from simultaneously kicking off expensive 30-second operations — the system runs out of threads/connections even though each user is within their rate limit |
| **Root cause** | Rate limiting by count measures *throughput*, not *concurrency*; expensive long-running operations consume resources for the entire duration, not just at request time |

**Strategy**: Track in-flight requests using a sorted set as an **active request tracker**. Each request adds a unique ID on start and removes it on finish. An atomic Lua script checks `ZCARD` (current count) before `ZADD` (add new request):

```lua
local count = redis.call("zcard", key)
if count < capacity then
  redis.call("zadd", key, timestamp, request_id)
  return {true, count}
end
return {false, count}
```

The application must wrap work in an `ensure`/`finally` block that calls `ZREM` — otherwise crashed workers leave ghost entries that permanently consume capacity until TTL expiry.

| Tradeoff | Detail |
|:---|:---|
| **Ghost entries on crash** | If a worker crashes without executing the cleanup, the entry persists until TTL — mitigated by `ZREMRANGEBYSCORE` on stale entries before each check |
| **Per-user granularity** | Each user gets their own sorted set key; this doesn't limit global concurrency — combine with load shedding (cache-21) for system-wide protection |
| **TTL sizing** | TTL must exceed the maximum expected operation duration; too short and long-running ops get prematurely cleaned, freeing capacity incorrectly |

> **Also see**: [Resilience Patterns](../resilience/) — Circuit breaker, bulkhead
> **Dictionary**: [Distributed Lock](../../reference-dictionary/data-concurrency.md#distributed-lock), [Bulkhead](../../reference-dictionary/resilience.md#bulkhead)
> **Azure**: Azure Cache for Redis `ZRANGEBYSCORE` can clean stale entries; combine with Azure Functions timeout for serverless concurrent limiting

---

## cache-20: Fail-Open Pattern for Rate Limiting

> **Source**: [§"Approach 1: Token Bucket with Lua" — rescue block](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)

| | |
|:---|:---|
| **Problem** | If Redis goes down and the rate limiter blocks all traffic, a Redis outage becomes indistinguishable from a full site outage — an infrastructure dependency becomes a hard failure point |
| **Root cause** | Treating the rate limiter as a **hard dependency** — every request must pass through it — means Redis availability gates all application availability |

**Strategy**: **Fail open**: catch Redis connection errors and allow requests through. The `rescue RedisError` block returns without raising a rate-limit error, letting traffic flow. Stripe reports their observed Redis failure rate at ~0.01%, making the trade-off overwhelmingly favorable — you'd rather let 0.01% of requests through unchecked than block 100% of traffic.

```ruby
begin
  allowed, tokens_left = redis.eval(SCRIPT, keys, args)
rescue RedisError => e
  logger.error("Redis rate limiter failed: #{e}")
  return  # allow the request — fail open
end
raise RateLimitError.new(429) unless allowed
```

| Tradeoff | Detail |
|:---|:---|
| **Abuse during outage** | During Redis downtime, rate limiting is effectively disabled — mitigated by monitoring + alerting on Redis error rates |
| **Not universal** | Fail-open is correct for rate limiting but wrong for authentication or authorization — those should fail closed |
| **Requires monitoring** | The `logger.error` call is critical; without observability, you won't know Redis is down and rate limiting is silently disabled |

> **Also see**: [Resilience Patterns](../resilience/) — Circuit breaker, fail-safe vs fail-secure
> **Dictionary**: [Circuit Breaker](../../reference-dictionary/resilience.md#circuit-breaker), [Fail-safe vs Fail-secure](../../reference-dictionary/resilience.md#fail-safe-vs-fail-secure)
> **Taxonomy**: §6.3 Resilience Patterns

---

## cache-21: Gradual Load Shedding with Priority Classification

> **Source**: [§"Approach 5: Load Shedding"](../../articles/caching/redis-rate-limiting-distributed-race-conditions.md)

| | |
|:---|:---|
| **Problem** | Per-user rate limiting doesn't protect against system-wide overload — 10,000 well-behaved users each within their individual limits can still collectively overwhelm infrastructure during a traffic spike |
| **Root cause** | Rate limiting protects *users from themselves*; it doesn't protect the *system from everyone at once* |

**Strategy**: **Gradual load shedding** with request priority. Stripe categorizes traffic: critical (payments, auth) is never shed; non-critical (analytics, reporting) is shed first. Shedding ramps gradually to avoid oscillation:

| Zone | Utilization | Action |
|:---|:---|:---|
| Normal | 0% – 70% | No shedding |
| Dead zone | 70% – 80% | Hold current shed rate (don't react to spikes) |
| Overloaded | 80% – 100% | Increase shed probability linearly |

Key timing parameters: wait **28 seconds** before starting to shed (confirm it's sustained, not a measurement spike); ramp to full shed rate over **~120 seconds** (avoid sharp changes that cause oscillation).

```python
SHED_START_DELAY = 28      # seconds before shedding begins
FULL_SHED_RAMP_TIME = 120  # seconds to reach 100% shed rate
```

| Tradeoff | Detail |
|:---|:---|
| **Classification overhead** | Every request must be categorized as critical vs. non-critical — requires upfront design of priority tiers |
| **Non-critical work loss** | During sustained overload, non-critical traffic (analytics, reporting) may be dropped for minutes — acceptable if the alternative is total outage |
| **Tuning required** | The delay and ramp parameters (28s, 120s) are system-specific; wrong values cause either premature shedding or slow reaction |

> **Also see**: [Resilience Patterns](../resilience/) — Circuit breaker, backpressure, graceful degradation
> **Dictionary**: [Load Shedding](../../reference-dictionary/resilience.md#load-shedding), [Backpressure](../../reference-dictionary/resilience.md#backpressure), [Graceful Degradation](../../reference-dictionary/resilience.md#graceful-degradation)
> **Azure**: Azure Load Balancer + Application Gateway can complement application-layer shedding; Azure Monitor metrics drive utilization checks
> **Taxonomy**: §7.2 Performance Architecture

---

## Layered Defense Architecture

The five patterns compose into a three-layer defense:

```
Incoming Request
       │
       ▼
┌──────────────────────────────┐
│  Layer 1: Request Rate Limit │  cache-17 (Token Bucket) or cache-18 (Rolling Window)
│  Per-user abuse protection   │
└──────────────┬───────────────┘
               │ pass
               ▼
┌──────────────────────────────┐
│  Layer 2: Concurrent Limit   │  cache-19 (Active Request Tracker)
│  Resource exhaustion guard   │
└──────────────┬───────────────┘
               │ pass
               ▼
┌──────────────────────────────┐
│  Layer 3: Load Shedder       │  cache-21 (Gradual Shedding)
│  System-wide overload guard  │
└──────────────┬───────────────┘
               │ pass
               ▼
        Application Logic
```

All three layers share **cache-20** (fail-open) as a cross-cutting concern — if Redis is unreachable, every layer degrades gracefully rather than blocking traffic.

> **Also see**: [Resilience Patterns](../resilience/) — Defense in depth, resilience stack
> **Dictionary**: [Defense in Depth](../../reference-dictionary/resilience.md#defense-in-depth)
