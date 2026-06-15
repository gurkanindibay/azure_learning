---
type: Reference
title: "Caching Architecture"
description: "When a **popular cache key expires** and many concurrent requests simultaneously hit the database to recompute it — crushing the database with redundant work."
timestamp: 2026-06-14T00:00:00Z
---

# Caching Architecture

> **Domain**: Cache stampede, invalidation, eviction, TTL, and caching anti-patterns.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Cache Stampede | [`#cache-stampede`](#cache-stampede) |
| Cache-Aside Pattern | [`#cache-aside-pattern`](#cache-aside-pattern) |
| Cache Invalidation | [`#cache-invalidation`](#cache-invalidation) |
| TTL (Time-To-Live) | [`#ttl-time-to-live`](#ttl-time-to-live) |
| Eviction Policies | [`#eviction-policies`](#eviction-policies) |
| Request Coalescing | [`#request-coalescing`](#request-coalescing) |
| PER Algorithm | [`#per-algorithm`](#per-algorithm) |
| I/O Multiplexing | [`#io-multiplexing`](#io-multiplexing) |
| Hash Slots | [`#hash-slots`](#hash-slots) |
| Copy-on-Write Persistence | [`#copy-on-write-persistence`](#copy-on-write-persistence) |
| Morris Probabilistic Counter | [`#morris-probabilistic-counter`](#morris-probabilistic-counter) |
| UNLINK (Async Deletion) | [`#unlink-async-deletion`](#unlink-async-deletion) |
| Server-Assisted Client-Side Caching | [`#server-assisted-client-side-caching`](#server-assisted-client-side-caching) |

---

## Cache Stampede

When a **popular cache key expires** and many concurrent requests simultaneously hit the database to recompute it — crushing the database with redundant work.

### Solutions

| Strategy | Mechanism | Complexity |
|:---|:---|:---|
| **Lock-on-Miss** | First request acquires lock, computes, others wait | Medium |
| **PER (Probabilistic Early Recomposition)** | Refresh probabilistically before expiry | Low |
| **External Refresh** | Background job refreshes before TTL expires | Medium |
| **GETEX** (Redis 6.2+) | Atomic get + TTL reset | Low |

**Also see**: [Request Coalescing](#request-coalescing), [PER Algorithm](#per-algorithm) · [Resilience](resilience.md#thundering-herd)

---

## Cache-Aside Pattern

Application code manages the cache explicitly: check cache → on miss, load from DB → store in cache → return.

```
GET /users/123
  → Check Redis for "user:123"
  → Cache miss → SELECT * FROM users WHERE id=123
  → Store in Redis: SET user:123 <data> EX 300
  → Return to client
```

| When to Use | When NOT |
|:---|:---|
| General-purpose caching | Write-heavy data (use write-through) |
| Read-heavy workloads | Data requiring strong consistency |

**Also see**: [Cache Invalidation](#cache-invalidation), [TTL](#ttl-time-to-live)

---

## Cache Invalidation

The process of **removing or updating stale cached data** when the source of truth changes. One of the hardest problems in computer science (Phil Karlton).

| Strategy | Mechanism |
|:---|:---|
| **Explicit delete on write** | DELETE cache key when DB updates |
| **TTL as safety net** | Data expires automatically after N seconds |
| **CDC-based invalidation** | Debezium reads DB WAL → invalidates cache |

> **Rule**: Always have a TTL safety net. Explicit invalidation can fail; TTL ensures eventual correctness.

**Also see**: [Cache-Aside Pattern](#cache-aside-pattern), [TTL](#ttl-time-to-live)

---

## TTL (Time-To-Live)

The duration after which a cache entry **automatically expires**. TTL serves as both a freshness guarantee and an invalidation safety net.

| TTL Strategy | Use Case |
|:---|:---|
| **Short TTL (seconds)** | Real-time data where staleness is unacceptable |
| **Medium TTL (minutes)** | Dashboard data, user profiles |
| **Long TTL (hours/days)** | Reference data, configuration |

> **Key insight**: TTL is always a **safety net** — not the primary freshness mechanism. Explicit invalidation + TTL = defense in depth.

**Also see**: [Cache Invalidation](#cache-invalidation), [Eviction Policies](#eviction-policies)

---

## Eviction Policies

The strategy for **which keys to remove** when the cache is full.

| Policy | Mechanism | Redis Config |
|:---|:---|:---|
| **LRU (Least Recently Used)** | Evicts least recently accessed | `allkeys-lru` |
| **LFU (Least Frequently Used)** | Evicts least frequently accessed | `allkeys-lfu` |
| **TTL** | Evicts keys closest to expiry | `volatile-ttl` |
| **Random** | Evicts random keys | `volatile-random` |
| **Noeviction** | Rejects writes when full | `noeviction` |

> For session stores: `volatile-ttl`. For general caches: `allkeys-lru` or `allkeys-lfu`.

**Also see**: [TTL](#ttl-time-to-live)

---

## Request Coalescing

Deduplicating **in-flight identical requests** so that only one request hits the backend while others wait for the same result. Prevents thundering-herd on cache misses.

```
Request 1: GET /expensive-report → starts computation
Request 2: GET /expensive-report → finds in-flight promise → waits
Request 3: GET /expensive-report → finds in-flight promise → waits
Request 1: computation done → resolves all three
```

**Also see**: [Cache Stampede](#cache-stampede)

---

## PER Algorithm

**Probabilistic Early Recomposition** — refresh a cache key **before** it expires, with a probability that increases as expiry approaches. This smooths the load and avoids the all-at-once stampede.

```
time_until_expiry = TTL - (now - last_updated)
probability = 1 - (time_until_expiry / TTL)
if random() < probability:
    refresh_cache()  # Early recomputation
```

**Also see**: [Cache Stampede](#cache-stampede)

---

## I/O Multiplexing

An OS-level mechanism (`epoll` on Linux, `kqueue` on BSD/macOS) that allows a single thread to monitor multiple file descriptors (network connections) and react only when data is ready — without blocking on any individual connection. This is the foundation of Redis's single-threaded event loop that achieves microsecond latency at 100K+ concurrent connections.

### Key Characteristics
- **Non-blocking**: The thread never waits on I/O; it polls and reacts
- **Event-driven**: Kernel notifies when a file descriptor becomes readable/writable
- **Zero context-switching**: One thread, no lock contention, no scheduler overhead

### When to Use
- High-concurrency I/O-bound servers (Redis, nginx, Node.js)
- When thread-per-connection models exhaust memory or CPU on context-switching

### When NOT to Use
- CPU-bound workloads (one slow operation blocks everything)
- When you need to exploit multi-core for command processing (scale with multiple instances instead)

**Also see**: [Hash Slots](#hash-slots) · [UNLINK (Async Deletion)](#unlink-async-deletion)

---

## Hash Slots

Redis Cluster's data distribution mechanism: **16,384 fixed slots** where keys are mapped via `CRC16(key) % 16384`. Each cluster node owns a contiguous range of slots. When rebalancing, slot ownership moves between nodes — keys are not rehashed, only the slot-to-node mapping changes.

### Key Characteristics
- **Fixed cardinality**: 16,384 slots — enough granularity for up to ~1,000 nodes
- **CRC16-based**: Deterministic, fast hash function with uniform distribution
- **Slot migration**: `CLUSTER SETSLOT` moves slots between nodes without rehashing keys

### When to Use
- Redis Cluster deployments where predictable data placement matters
- When operational simplicity around rebalancing is more important than automatic redistribution

### When NOT to Use
- Standalone Redis (no clustering needed)
- When you need automatic, zero-touch rebalancing (consistent hashing is more automatic)

**Also see**: [I/O Multiplexing](#io-multiplexing) · Consistent Hashing (in [API Design](../reference-dictionary/api-design.md))

---

## Copy-on-Write Persistence

Redis's RDB snapshot mechanism: `fork()` creates a child process that sees a consistent memory snapshot, while the parent continues serving traffic. Linux Copy-on-Write (COW) ensures only memory pages modified after the fork are duplicated — unchanged pages are shared between parent and child. Memory overhead is proportional to write rate during the snapshot window, not dataset size.

### Key Characteristics
- **Non-blocking**: Parent process never pauses for persistence
- **Point-in-time consistent**: Child sees memory exactly as it was at fork()
- **COW efficiency**: Only modified pages consume extra memory

### When to Use
- Production Redis instances that need periodic backups without downtime
- Disaster recovery scenarios where point-in-time recovery is acceptable

### When NOT to Use
- Crash-safety requirements stricter than point-in-time (use AOF instead or in addition)
- Very high write throughput on memory-constrained instances (COW can double memory usage)

**Also see**: [Morris Probabilistic Counter](#morris-probabilistic-counter) · [UNLINK (Async Deletion)](#unlink-async-deletion)

---

## Morris Probabilistic Counter

An 8-bit probabilistic data structure used by Redis for LFU (Least Frequently Used) eviction. Instead of storing a precise access count, it approximates frequency logarithmically: `frequency ≈ 2^counter`. The counter increments with decreasing probability as its value grows, and decays over time so stale-popular keys eventually lose their ranking.

### Key Characteristics
- **Logarithmic scale**: 8 bits can represent up to ~2^255 accesses
- **Probabilistic increment**: `P(increment) = 1 / (counter * 10 + 1)`
- **Time decay**: `lfu-decay-time` parameter controls how fast old accesses lose weight
- **Extreme memory efficiency**: 1 byte per key vs 4–8 bytes for a standard counter

### When to Use
- LFU eviction at scale (millions of keys) where per-key memory matters
- Eviction ranking (relative ordering) — not precise counting

### When NOT to Use
- Billing, metering, or any use case requiring exact counts
- When access patterns are uniform (all keys equally likely — eviction policy doesn't matter)

**Also see**: [Eviction Policies](#eviction-policies) · [Copy-on-Write Persistence](#copy-on-write-persistence)

---

## UNLINK (Async Deletion)

Redis 4.0+ command that removes a key from the keyspace synchronously (instant) while delegating memory freeing to a background thread. Unlike `DEL`, which blocks the main thread for the entire operation, `UNLINK` prevents multi-second stalls when deleting large data structures (lists, sets, sorted sets, hashes with millions of elements).

### Key Characteristics
- **Synchronous keyspace removal**: Key disappears from client view immediately
- **Asynchronous memory free**: Background thread handles the expensive part
- **Lazy-free mechanism**: Also applies to `FLUSHDB ASYNC` / `FLUSHALL ASYNC`

### When to Use
- Deleting large keys (sets, lists, hashes with >100 elements) in production
- TTL-based eviction cleanup where DEL could cause latency spikes

### When NOT to Use
- Small keys (<100 elements) — scheduling overhead outweighs benefit
- Redis versions <4.0 (use DEL, accept the blocking behavior)

**Also see**: [I/O Multiplexing](#io-multiplexing) · [Server-Assisted Client-Side Caching](#server-assisted-client-side-caching)

---

## Server-Assisted Client-Side Caching

Redis 6+ feature (via `CLIENT TRACKING ON`) where the server pushes invalidation messages to clients when tracked keys are modified. This replaces TTL-based guesswork with guaranteed freshness: clients evict their local copy on invalidation and fetch fresh data on the next read. Achieves **zero stale reads** with **fewer round trips**.

### Key Characteristics
- **Server-pushed invalidations**: No client polling or TTL guessing
- **RESP3 protocol**: Requires client library support for RESP3
- **Two modes**: Default (per-key invalidation table) and BCAST (broadcast all modifications)
- **Opt-in**: Clients must explicitly enable; no impact on non-tracking clients

### When to Use
- Latency-sensitive applications that cache data client-side and need guaranteed freshness
- Scenarios where TTL-based caching causes unacceptable staleness or round-trip overhead

### When NOT to Use
- When client libraries don't support RESP3
- Simple caching scenarios where TTL-based freshness is acceptable
- When server memory for the invalidation table is a constraint (use BCAST mode or skip)

**Also see**: [Cache Invalidation](#cache-invalidation) · [TTL](#ttl-time-to-live) · [UNLINK (Async Deletion)](#unlink-async-deletion)
