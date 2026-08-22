---
type: Article
title: "Redis Distributed Locking — Commands, Patterns, and Production Pitfalls"
source: "https://codefarm0.medium.com/redis-distributed-locking-commands-patterns-and-production-pitfalls-397e12fe441b"
author: "Arvind Kumar"
published: 2026-08-08
created: 2026-08-22
description: "How to implement safe distributed locking with Redis: SET NX, Lua unlock scripts, exponential backoff retry, TTL management, and avoiding the transaction boundary race condition."
tags:
  - redis
  - distributed-locks
  - concurrency
  - transactions
  - race-conditions
  - lua
  - spring-boot
---

# Redis Distributed Locking — Commands, Patterns, and Production Pitfalls

How to implement safe distributed locking with Redis: SET NX, Lua unlock scripts, exponential backoff retry, TTL management, and the race condition that almost slipped through.

Master Redis distributed locking with this practical guide. Learn SET NX with TTL, Lua unlock scripts, exponential backoff retry, monitoring commands, and why releasing a lock before the transaction commits causes race conditions.

> [Full story for non-members](https://codefarm0.medium.com/397e12fe441b?sk=31df5ffd5e156a3554d8dde1bc33fba6) | [GitHub Repository](https://github.com/codefarm0/coupon-redemption-system)

![Redis Distributed Locking Overview](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*38gOODOMIG-KGWq5bqTMSQ.png)

Redis is at the heart of the coupon redemption system's race condition prevention. Its `SET NX` command provides the atomic "set if not exists" semantics needed for distributed locks — fast, simple, and battle-tested at companies like GitHub, Twitter, and Stack Overflow.

This article covers every Redis concept the project uses: lock acquisition, safe release, retry logic, monitoring, and a critical lesson about transaction boundaries.

## The Distributed Lock Pattern

A distributed lock must solve four fundamental problems:

1. **Mutual Exclusion**: Only one client can hold the lock at any given time.
2. **Deadlock Freedom**: If a client holding a lock crashes, the lock must eventually be released automatically (lease expiry via TTL).
3. **Fault Tolerance**: The locking mechanism must remain functional even during transient network or node issues.
4. **Safety / Ownership Verification**: A client must never release a lock held by another client.

![Distributed Lock Four Problems](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*aSjjw3fMw2LkIY4Yl31ohw.png)

## 1. Lock Acquisition — SET NX with TTL

The core of Redis locking is `SET key value NX PX timeout`:

```java
// Spring Data Redis implementation
Boolean acquired = redisTemplate.opsForValue()
    .setIfAbsent(lockKey, lockValue, Duration.ofMillis(LOCK_TIMEOUT_MS));
return Boolean.TRUE.equals(acquired);
```

**The Redis command executed:**

```bash
SET coupon:lock:SUMMER50 "uuid-abc-123" NX PX 5000
```

| Parameter | Purpose |
|:---|:---|
| `coupon:lock:SUMMER50` | The lock key — identifies the specific resource |
| `"uuid-abc-123"` | A unique value per request (UUID) — proves ownership |
| `NX` | "Not eXists" — only set if the key does NOT already exist |
| `PX 5000` | Expire after 5,000ms (5 seconds) — prevents deadlocks if the app crashes |

### Why Both NX and PX in One Command?

In older Redis versions, you had to run `SETNX` followed by `EXPIRE`:

```bash
# ❌ DANGEROUS — Two separate commands
SETNX coupon:lock:SUMMER50 "uuid-abc-123"
# If the app crashes HERE, the key never expires! Deadlock.
EXPIRE coupon:lock:SUMMER50 5
```

Redis 2.6.12 added the `NX` and `PX` options to the `SET` command, making acquisition and expiration atomic. Always use the combined command.

## 2. Safe Lock Release — Lua Script

Releasing a lock seems simple: just delete the key (`DEL coupon:lock:SUMMER50`). But there is a subtle race condition.

### The Problem

1. Instance A acquires the lock with a 5-second TTL.
2. Instance A's database transaction takes 6 seconds (GC pause, slow DB, network delay).
3. At 5 seconds, Redis auto-expires Instance A's lock.
4. Instance B acquires the lock (`SET NX` succeeds because the key is gone).
5. Instance A finishes and calls `DEL coupon:lock:SUMMER50`.
6. **Instance A just deleted Instance B's lock!**
7. Instance C acquires the lock. Now Instance B and Instance C both think they hold the lock!

### The Solution

Only delete the key if the value matches the UUID we stored when acquiring the lock:

```lua
-- Lua script executed atomically on Redis
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```

**Spring Boot implementation:**

```java
private static final String UNLOCK_SCRIPT = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """;

@Override
public void releaseLock(String key, String value) {
    redisTemplate.execute(unlockScript, List.of(key), value);
}
```

**Why Lua?** Atomicity. The Lua script runs entirely on the Redis server — no other command can interleave between the `GET` and the `DEL`.

```
Without Lua Script:
Instance A: GET coupon:lock:SUMMER50 → "uuid-abc" (my lock)
// Instance A's lock expires and gets acquired by C
Instance C: SET coupon:lock:SUMMER50 "uuid-xyz" NX → OK
Instance A: DEL coupon:lock:SUMMER50 → ❌ Deletes C's lock!
Instance C: thinks lock is held but it's gone

With Lua Script:
Instance A: GET coupon:lock:SUMMER50 → value matches → DEL
// Only deletes if still our lock
Instance A: Lua returns 1 → lock released safely
```

## 3. Exponential Backoff Retry

When a lock is held by another request, you don't want to hammer Redis with continuous retries. The solution is exponential backoff:

```java
private static final int MAX_LOCK_RETRIES = 10;
private static final long INITIAL_RETRY_DELAY_MS = 50;

private boolean acquireLockWithRetry(String lockKey, String lockValue,
        String couponCode, String username) {
    long delayMs = INITIAL_RETRY_DELAY_MS;
    for (int attempt = 0; attempt < MAX_LOCK_RETRIES; attempt++) {
        boolean acquired = lockStrategy.acquireLock(lockKey, lockValue, LOCK_TIMEOUT_MS);
        if (acquired) {
            logger.info("[LOCK ACQUIRED] Attempt: {}/{}", attempt + 1, MAX_LOCK_RETRIES);
            return true;
        }
        if (attempt < MAX_LOCK_RETRIES - 1) {
            try {
                Thread.sleep(delayMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
            delayMs = Math.min(delayMs * 2, 1000); // Double, cap at 1 second
        }
    }
    logger.warn("[LOCK FAILED] All {} attempts exhausted", MAX_LOCK_RETRIES);
    return false;
}
```

**Retry Sequence Progression:**

```
Attempt 1: immediate (50ms)
Attempt 2: wait 100ms
Attempt 3: wait 200ms
Attempt 4: wait 400ms
Attempt 5: wait 800ms
Attempt 6+: wait 1000ms (capped)
```

![Exponential Backoff Retry](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*uFS2JIkeOwif0WOToV4Z6g.png)

Total wait time: ~4.5 seconds before giving up. The lock TTL is 5 seconds, so by attempt 7–8, a stuck lock would have expired and become available.

**Why not constant 50ms retries?** 100 requests × 50ms × 10 retries = 50,000 Redis calls in 5 seconds. Exponential backoff reduces this to ~1,000 — and prevents the **thundering herd** problem (all instances retrying simultaneously).

## 4. The TTL Bug — Lease Expiration vs Duration

The lock TTL must be **longer** than the maximum expected transaction duration. In this system:

- Redis lock TTL: 5,000ms (5 seconds)
- Max retry duration: ~4.5 seconds
- Database transaction: typically <100ms

If the TTL is too short, the lock expires while the transaction is still running. Another instance acquires the lock, processes the same coupon, and you get **double redemptions**.

If the TTL is too long, a crashed instance holds the lock for the full duration, blocking all other requests.

**Best Practice:** 5 seconds is generous for sub-100ms transactions, but short enough that a crash doesn't block the system for long.

## 5. The Transaction Boundary Bug

This was the most critical finding in the project: **The lock was being released before the database transaction committed.**

```java
// ❌ BAD: Spring @Transactional commits AFTER method execution
@Transactional
public RedeemResponse redeemCoupon(RedeemRequest request) {
    acquireLock();   // Step 1: Lock acquired
    // ... JPA operations (queued, not yet committed to DB!)
    releaseLock();   // Step 2: ❌ Lock released before commit!
}                    // Step 3: Transaction commits (too late!)
```

Another request could acquire the lock between step 2 and step 3, read the old remaining value from MySQL (which hasn't been committed yet), and cause a race condition **even with distributed locking in place**.

### The Fix

Acquire the lock before the transaction starts, and release it strictly after the transaction commits using `TransactionTemplate`:

```java
// ✅ FIXED: Programmatic transaction management
public RedeemResponse redeemCoupon(RedeemRequest request) {
    acquireLock();   // Step 1: Lock acquired

    try {
        return transactionTemplate.execute(status -> {
            // ... JPA operations run & commit inside template boundary
            return processRedemption(request);
        });          // Step 2: Transaction commits
    } finally {
        releaseLock(); // Step 3: Lock released AFTER commit
    }
}
```

**Lesson:** A distributed lock is only as safe as the transaction boundary it protects.

## 6. Monitoring Commands

Useful Redis commands for debugging lock behavior:

### Check Active Locks

```bash
# List all lock keys
KEYS coupon:lock:*

# Inspect a specific lock
GET coupon:lock:SUMMER50
# Returns: "uuid-abc-123"
```

### Check Lock TTL

```bash
# Remaining time before auto-release
TTL coupon:lock:SUMMER50
# Returns: (integer) 3
```

### Monitor Live Operations

```bash
# Watch every Redis command in real-time
docker exec -it coupon-redis redis-cli MONITOR

# Filter for lock-related commands
docker exec -it coupon-redis redis-cli MONITOR | grep "coupon:lock"
```

### Clear All Locks (for testing)

```bash
docker exec -it coupon-redis redis-cli FLUSHALL
```

### Redis CLI Connection

```bash
# Interactive mode
docker exec -it coupon-redis redis-cli

# One-off commands
docker exec -it coupon-redis redis-cli KEYS "coupon:lock:*"
```

## 7. NoLockStrategy — The Race Condition Simulator

To verify the impact of locking, a strategy pattern allows toggling locking off:

```java
public class NoLockStrategy implements LockStrategy {
    @Override
    public boolean acquireLock(String key, String value, long timeoutMs) {
        return true; // Every request "acquires" the lock
    }

    @Override
    public void releaseLock(String key, String value) {
        // No-op - never acquired, never released
    }
}
```

When `coupon.lock.enabled=false`, every redemption request passes through without coordination. The database transaction runs, but without the Redis lock, concurrent requests on different instances read stale data from MySQL.

When running 10 concurrent requests on a coupon with stock 10, without locking, the remaining count drops by only 7 or 8 due to lost updates, demonstrating the race condition.

## 8. Production Considerations

For production Redis locking, consider:

### Redlock Algorithm

For environments where absolute safety matters across multiple Redis nodes, implement the Redlock algorithm — acquire the lock on multiple Redis nodes (typically 5 independent masters) and require a majority ($N/2 + 1$) to succeed.

### Clock Drift

Redis lock safety depends on monotonically increasing clocks. In containers and virtualized environments, clock drift can cause TTL expiration discrepancies. Use NTP-synchronized clocks in production.

### Connection Resilience

Configure appropriate connection timeouts and pooling to prevent application threads from hanging when Redis is experiencing network degradation:

```yaml
spring:
  data:
    redis:
      timeout: 2000ms
      connect-timeout: 1000ms
      lettuce:
        pool:
          max-active: 16
          max-idle: 8
```

## Redis Commands Reference

![Redis Commands Reference](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*c8_ttedwLmTjG7Bk6GTSgw.png)

## Conclusion

Redis distributed locking is simple to implement but has subtle edge cases:

- **Use `SET NX` with TTL** for atomic lock acquisition with deadlock prevention
- **Use a Lua script** for safe unlock (only the owner releases)
- **Use exponential backoff** for retry — prevents thundering herd
- **The lock must span the entire transaction** — releasing before commit creates race conditions
- **Monitor with `KEYS`, `TTL`, and `MONITOR`** during development

The complete Redis lock implementation is available on GitHub:
[https://github.com/codefarm0/coupon-redemption-system](https://github.com/codefarm0/coupon-redemption-system)
