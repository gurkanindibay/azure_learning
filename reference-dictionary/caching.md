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
| Redis Sorted Sets | [`#redis-sorted-sets`](#redis-sorted-sets) |
| Server-Assisted Client-Side Caching | [`#server-assisted-client-side-caching`](#server-assisted-client-side-caching) |
| Write-Through | [`#write-through`](#write-through) |
| Hot Key | [`#hot-key`](#hot-key) |
| Counter Sharding | [`#counter-sharding`](#counter-sharding) |
| Hot Key Detection | [`#hot-key-detection`](#hot-key-detection) |
| Adaptive Request Routing | [`#adaptive-request-routing`](#adaptive-request-routing) |
| Dedicated Hot-Key Tier | [`#dedicated-hot-key-tier`](#dedicated-hot-key-tier) |
| Timeline Cache | [`#timeline-cache`](#timeline-cache) |
| Celebrity Cache | [`#celebrity-cache`](#celebrity-cache) |

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

---

## Write-Through

A caching pattern where data is written to both the cache and the backing store **synchronously** as part of the same write operation. The cache and database remain consistent, but write latency increases because every write waits for both stores.

### Key Characteristics
- **Synchronous dual write**: Every write updates cache and DB before returning success
- **Strong consistency**: Cache is never stale relative to the DB
- **Write amplification**: Each logical write becomes two physical writes

### When to Use
- Data that must be read immediately after writing (author's own timeline, user profiles)
- Workloads where read-after-write consistency is more important than write latency

### When NOT to Use
- Write-heavy workloads where dual-write latency is unacceptable
- Scenarios where cache failures should not block the primary write path

**Also see**: [Cache-Aside Pattern](#cache-aside-pattern) · [Cache Invalidation](#cache-invalidation)

---

## Hot Key

A single cache key that receives a disproportionately large share of traffic, causing one node, slot, or thread to become a bottleneck while the rest of the cluster is underutilized.

### Key Characteristics
- **Skewed access pattern**: 1% of keys can drive 99% of requests in skewed workloads
- **Single-node saturation**: In Redis Cluster, one hot key maps to one slot on one node
- **Amplified by counter patterns**: Rate limiters, like counts, and trending-item caches naturally centralize updates on one key
- **Symptom**: Latency spikes for that key while overall cluster CPU/memory looks healthy

### When to Use
- Skew is unavoidable and the business key is inherently centralized (e.g., a global config flag or a celebrity post)
- When monitoring shows a single key dominating request volume

### When NOT to Use
- Uniform access patterns where no key stands out (solutions add unnecessary complexity)
- As a substitute for proper capacity planning

### Mitigations
| Technique | Mechanism | Tradeoff |
|:---|:---|:---|
| **Key sharding / salting** | Append a random suffix to spread writes across N keys | Reads must aggregate; ordering may be lost |
| **Local caching** | Cache the hot value in application memory | Stale reads; replica consistency challenge |
| **Read replicas / hot-key replication** | Direct read traffic to replicas | Writes still hit the primary; replication lag |
| **Request coalescing** | Collapse in-flight identical reads into one backend call | Helps read-heavy hot keys, not write-heavy ones |
| **Counter sharding** | Split write-heavy counters into N sub-keys | Reads must aggregate; see [Counter Sharding](#counter-sharding) |
| **Hot-key detection** | Auto-detect viral keys and promote them | Adds monitoring/routing complexity; see [Hot Key Detection](#hot-key-detection) |
| **Dedicated hot-key tier** | Isolate hot keys on separate resources | Operational complexity; see [Dedicated Hot-Key Tier](#dedicated-hot-key-tier) |

**Also see**: [Request Coalescing](#request-coalescing) · [Celebrity Cache](#celebrity-cache) · [Rate Limiting](../reference-dictionary/api-design.md#rate-limiting) · [api-09: Hot Key Problem in Distributed Rate Limiters](../system-design-architecture/04-api-network-design.md#api-09-hot-key-problem-in-distributed-rate-limiters)

---

## Timeline Cache

A user-specific pre-computed data structure (commonly a Redis sorted set) that stores references to recent events — such as social-media posts — in reverse-chronological order. Feed reads become O(1) fetches instead of scatter-gather queries across many followees.

### Key Characteristics
- **User-scoped**: One timeline per consumer (`timeline:{user_id}`)
- **Sorted by time**: Score = event timestamp for natural reverse-chronological pagination
- **Bounded size**: Trimmed to the latest N entries (e.g., 1000) to bound memory

### When to Use
- Social feeds, activity streams, notification inboxes where read latency matters
- Fanout-on-write architectures where writes pre-compute read results

### When NOT to Use
- Eventual-consistency-tolerant read paths that can be computed on demand cheaply
- Small graphs where scatter-gather is faster than maintaining per-user caches

**Also see**: [Cache-Aside Pattern](#cache-aside-pattern) · [Celebrity Cache](#celebrity-cache)

---

## Celebrity Cache

A dedicated cache tier for high-follower accounts whose content is read by millions. Instead of fanning every celebrity post into all followers' timelines, the system stores a bounded list of recent celebrity posts and merges them into follower feeds at read time.

### Key Characteristics
- **Isolated hot keys**: Celebrity content is separated from normal timelines to prevent cache storms
- **Bounded list**: Latest N posts per celebrity (e.g., 100), trimmed on new writes
- **Lazy or pre-warmed refresh**: Populated on post creation and refreshed on read miss

### When to Use
- Social networks with highly skewed follower distributions (1% of users have >1M followers)
- Any fanout system where push-all would create unbounded write amplification

### When NOT to Use
- Graphs with uniformly small follower counts — pure push is simpler
- When read-time merging complexity outweighs fanout savings

**Also see**: [Timeline Cache](#timeline-cache) · [Request Coalescing](#request-coalescing)

---

## Counter Sharding

Splitting a single write-heavy hot key (typically a counter) into **N sub-keys** so that writes are distributed across multiple shards or nodes. Reads aggregate the shards to reconstruct the current value.

### Key Characteristics
- **Write distribution**: 100K writes/sec on one key becomes 1K writes/sec across 100 shards
- **Read aggregation**: A read issues N GETs and sums them — adds latency and bandwidth
- **Non-atomic aggregate**: The summed value is a point-in-time snapshot, not a transactional read
- **Random shard selection**: Writers pick a shard uniformly to spread load

### When to Use
- Write-heavy hot keys such as like counters, view counters, inventory counters
- When the read rate is low enough that aggregation cost is acceptable

### When NOT to Use
- Read-heavy hot keys — replication is cheaper (see [Hot Key](#hot-key))
- When the counter must be read atomically or with strong consistency

**Also see**: [Hot Key](#hot-key) · [Request Coalescing](#request-coalescing)

---

## Hot Key Detection

Real-time identification of keys whose request rate is rapidly becoming a bottleneck, usually by counting accesses per key over a sliding window and comparing against a threshold.

### Key Characteristics
- **Sliding-window counters**: Per-key access counts reset periodically to catch bursts
- **Threshold-based promotion**: A key is flagged "hot" when its count crosses a configured threshold
- **Self-healing trigger**: Detected hot keys can be auto-replicated, moved to a hot tier, or cached locally
- **Approximate counting**: At scale, frequency sketches (e.g., Count-Min Sketch) reduce memory overhead

### When to Use
- Traffic patterns are unpredictable (viral content, trending products)
- You want automated mitigation rather than on-call manual intervention

### When NOT to Use
- Known, stable hot keys — pre-provision replicas instead of detecting them
- When false positives would cause expensive, unnecessary reconfiguration

**Also see**: [Hot Key](#hot-key) · [Dedicated Hot-Key Tier](#dedicated-hot-key-tier)

---

## Adaptive Request Routing

Routing read requests for a hot key to **dynamically chosen replicas or tiers** based on real-time load, key temperature, or health signals, rather than always hashing to the same shard.

### Key Characteristics
- **Load-aware routing**: Requests prefer nodes with lower latency or queue depth
- **Hot-key registry**: A control plane tracks currently hot keys and their replica locations
- **Failover**: If a replica melts, traffic shifts to other replicas or the primary
- **Coupled with detection**: Usually driven by hot-key detection output

### When to Use
- Read-heavy hot keys with many replicas
- When a static hash ring cannot absorb traffic spikes

### When NOT to Use
- Uniform workloads where consistent hashing is sufficient
- When routing state itself would become a bottleneck or single point of failure

**Also see**: [Hot Key](#hot-key) · [Hot Key Detection](#hot-key-detection)

---

## Dedicated Hot-Key Tier

A separate cache or serving tier reserved for **hot keys only**, with its own replicas, memory, and bandwidth, so that viral traffic cannot starve normal (cold/long-tail) queries.

### Key Characteristics
- **Resource isolation**: Hot and cold keys do not share connection pools, CPU, or network
- **Independent scaling**: The hot tier can be scaled out without touching the normal tier
- **Traffic classification**: A proxy or client decides whether a key/request belongs to the hot tier
- **Blast-radius reduction**: A spike in one celebrity key does not degrade latency for all other keys

### When to Use
- Highly skewed workloads where a small set of keys dominates traffic
- When mixed hot/cold traffic causes connection pool exhaustion or noisy-neighbor issues

### When NOT to Use
- Uniform access patterns — a second tier adds operational overhead with no benefit
- When the classification/routing layer is more complex than the hot-key problem itself

**Also see**: [Hot Key](#hot-key) · [Celebrity Cache](#celebrity-cache) · [Hot Key Detection](#hot-key-detection)

---

## Redis Sorted Sets

A Redis data structure that stores unique members paired with a numeric score, maintaining them in sorted order via an internal skip-list. Unlike a regular set, sorted sets allow range queries (`ZRANGE`), rank lookups (`ZRANK`/`ZREVRANK`), and score-based retrieval — all in O(log N) time — making them the go-to choice for leaderboards, priority queues, and time-series indices.

### Key Characteristics
- **Automatic ordering**: Members are always sorted by score (and lexicographically for tied scores); no manual `ORDER BY` needed
- **O(log N) operations**: `ZADD`, `ZREVRANK`, `ZREVRANGE` all operate in logarithmic time regardless of set size
- **Score updates**: Changing a member's score re-positions it automatically — ideal for leaderboards with continuous score changes
- **Range queries**: `ZREVRANGE 0 99` fetches Top 100 without scanning the entire set

### When to Use
- Real-time leaderboards and ranking systems with frequent score updates
- Priority queues where items need to be processed in score order
- Time-series data indexed by timestamp with range queries
- Any workload requiring sorted retrieval without `ORDER BY` over millions of rows

### When NOT to Use
- When the dataset exceeds available memory (sorted sets are in-memory; use a disk-based indexed table instead)
- When you need complex multi-column sorting (sorted sets sort by a single score)
- When durability is the primary concern — pair with a persistent database as source of truth

### Also see
- [Cache-Aside Pattern](#cache-aside-pattern) · [TTL](#ttl-time-to-live) · [Sharding](../architecture-patterns.md#sharding) · [Leaderboard Pattern](../architecture-patterns.md#leaderboard-pattern)
