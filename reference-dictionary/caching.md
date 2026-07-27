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

| Category / Term | Anchor |
|:---|:---|
| **Read Strategies** | |
| Cache-Aside Pattern | [`#cache-aside-pattern`](#cache-aside-pattern) |
| Server-Assisted Client-Side Caching | [`#server-assisted-client-side-caching`](#server-assisted-client-side-caching) |
| **Write Strategies** | |
| Write-Through | [`#write-through`](#write-through) |
| Write-Behind | [`#write-behind`](#write-behind) |
| Write-Around | [`#write-around`](#write-around) |
| **Invalidation & Freshness** | |
| Cache Invalidation | [`#cache-invalidation`](#cache-invalidation) |
| Event-Driven Invalidation | [`#event-driven-invalidation`](#event-driven-invalidation) |
| TTL (Time-To-Live) | [`#ttl-time-to-live`](#ttl-time-to-live) |
| Version Stamps | [`#version-stamps`](#version-stamps) |
| Session Affinity | [`#session-affinity`](#session-affinity) |
| Cross-Region Invalidation | [`#cross-region-invalidation`](#cross-region-invalidation) |
| **Cache Failures & Resiliency** | |
| Cache Stampede | [`#cache-stampede`](#cache-stampede) |
| PER Algorithm | [`#per-algorithm`](#per-algorithm) |
| Request Coalescing | [`#request-coalescing`](#request-coalescing) |
| Stale Read Rate | [`#stale-read-rate`](#stale-read-rate) |
| Eviction Policies | [`#eviction-policies`](#eviction-policies) |
| Cache Hit Ratio | [`#cache-hit-ratio`](#cache-hit-ratio) |
| **Hot Key Patterns** | |
| Hot Key | [`#hot-key`](#hot-key) |
| Hot Key Detection | [`#hot-key-detection`](#hot-key-detection) |
| Dedicated Hot-Key Tier | [`#dedicated-hot-key-tier`](#dedicated-hot-key-tier) |
| Counter Sharding | [`#counter-sharding`](#counter-sharding) |
| Adaptive Request Routing | [`#adaptive-request-routing`](#adaptive-request-routing) |
| Timeline Cache | [`#timeline-cache`](#timeline-cache) |
| Celebrity Cache | [`#celebrity-cache`](#celebrity-cache) |
| Edge Pre-positioning | [`#edge-pre-positioning`](#edge-pre-positioning) |
| **Redis Internals** | |
| Redis Cluster | [`#redis-cluster`](#redis-cluster) |
| I/O Multiplexing | [`#io-multiplexing`](#io-multiplexing) |
| Lua Scripting (Redis) | [`#lua-scripting-redis`](#lua-scripting-redis) |
| Hash Slots | [`#hash-slots`](#hash-slots) |
| Copy-on-Write Persistence | [`#copy-on-write-persistence`](#copy-on-write-persistence) |
| Morris Probabilistic Counter | [`#morris-probabilistic-counter`](#morris-probabilistic-counter) |
| MULTI/EXEC (Redis Transactions) | [`#multiexec-redis-transactions`](#multiexec-redis-transactions) |
| UNLINK (Async Deletion) | [`#unlink-async-deletion`](#unlink-async-deletion) |
| Redis Sorted Sets | [`#redis-sorted-sets`](#redis-sorted-sets) |
| SET NX (Redis) | [`#set-nx-redis`](#set-nx-redis) |
| **Advanced Mitigations** | |
| Single-Flight Execution | [`#single-flight-execution`](#single-flight-execution) |
| Soft TTL | [`#soft-ttl`](#soft-ttl) |
| Probabilistic Early Invalidation | [`#probabilistic-early-invalidation`](#probabilistic-early-invalidation) |

---

### Read Strategies

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

### Write Strategies

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

## Write-Behind

A caching pattern where data is written to the cache **synchronously** and the write to the backing store is deferred — executed asynchronously on a background schedule. Maximizes write throughput but risks data loss if the cache fails before the flush completes.

### Key Characteristics
- **Async flush**: Cache acknowledges write immediately; DB update happens later
- **Write batching**: Multiple writes can be coalesced into fewer DB operations
- **Data loss risk**: Cache failure before flush = lost writes (unacceptable for transactional data)
- **High write throughput**: Write latency is cache-only; DB is not on the critical path

### When to Use
- Write-heavy workloads where throughput trumps immediate durability (analytics counters, view counts, metrics)
- Scenarios where the data can be reconstructed or is non-critical
- When paired with a durable cache (Redis with AOF persistence) to reduce loss window

### When NOT to Use
- Financial transactions, inventory counts, or any data where loss is unacceptable
- When the backing store cannot keep up with the async flush rate (builds unbounded backlog)
- Without monitoring on the flush lag — unbounded lag means unbounded data loss on failure

**Also see**: [Write-Through](#write-through) · [Cache-Aside Pattern](#cache-aside-pattern) · [Cache Invalidation](#cache-invalidation)

---

## Write-Around

A caching write strategy where writes **bypass the cache entirely** and go directly to the database. The cache is populated only on subsequent reads (cache-aside on read). This avoids filling the cache with data that may never be read, but leaves a window where the cache serves stale data until the entry expires or is explicitly invalidated.

> **Key insight**: Write-around optimizes for cache efficiency (only cache what's actually read), but at the cost of read-after-write consistency. After a write, the next read will hit stale cached data unless the cache is explicitly invalidated.

### Key Characteristics
- **Write path skips cache**: `App → DB`, no cache interaction on write
- **Cache populated on read miss**: First read after a write triggers DB → cache fill
- **Stale window**: Between write and cache invalidation/expiry, reads get old data
- **Cache-efficient**: Only frequently-read data enters the cache; write-only data never does

### When to Use
- Write-heavy workloads where most written data is never read back
- Scenarios where cache eviction pressure from infrequently-read data is a concern
- When paired with explicit invalidation on write to close the stale-data window

### When NOT to Use
- Read-after-write consistency is required (use write-through instead)
- Cart systems, user profiles, or any data where the user expects to see their own writes immediately
- Without explicit invalidation or short TTL — stale data will persist

**Also see**: [Write-Through](#write-through) · [Write-Behind](#write-behind) · [Cache-Aside Pattern](#cache-aside-pattern) · [Cache Invalidation](#cache-invalidation)

---

### Invalidation & Freshness

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

## Event-Driven Invalidation

A cache invalidation strategy where data changes are published as events to a message bus, and cache layers subscribe to those events to invalidate or update their local copies. Decouples the write path from cache management and provides reliable, replayable invalidation with persistent event storage.

> **Key insight**: Direct cache invalidation calls from the application are fire-and-forget — if the cache is down or the network drops the invalidation, the stale data lives forever. Event-driven invalidation with a persistent message queue turns invalidation into a recoverable operation: events survive cache restarts and network failures.

### Key Characteristics
- **Decoupled invalidation**: Writers publish "data changed" events; cache consumers react independently
- **Persistent events**: Message queue retains events if consumers are down; replay on recovery
- **Multiple consumers**: Redis, CDN, search index — all subscribe to the same event stream
- **Atomic with outbox pattern**: DB write and event publication are transactional

### When to Use
- Multi-layered caching (Redis + CDN + local) where all layers must stay consistent
- Geo-distributed deployments requiring cross-region cache invalidation
- Systems where cache unavailability during writes is unacceptable (events queue up)

### When NOT to Use
- Single-node deployments with simple cache-aside — direct invalidation is simpler
- When the message bus itself becomes a reliability bottleneck
- Ultra-low-latency paths where the async nature of event-driven invalidation is too slow

**Also see**: [Cache Invalidation](#cache-invalidation) · [Outbox Pattern](../cqrs-event-driven.md#outbox-pattern) · [Cross-Region Invalidation](#cross-region-invalidation) · [Write-Through](#write-through)

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

## Version Stamps

A cache consistency mechanism where each cache entry carries a version number, and clients include their last-known version in read requests. If the cache has a newer version, it returns the data. If the cache has an older or different version, it treats it as a cache miss and fetches from the database.

> **Key insight**: Version stamps turn the cache consistency problem from "is this data stale?" into "is this version the latest?" — a much simpler question. The database is the version authority; the cache is just a potentially-outdated copy.

### Key Characteristics
- **Monotonically increasing versions**: Each write increments the version in the database
- **Client-driven staleness check**: Client sends its last-seen version; cache compares and either serves or redirects to DB
- **No global invalidation needed**: Stale cache entries are naturally bypassed when a client with a newer version reads
- **Tombstone-free**: Old versions can coexist; they are simply never served to clients who know about newer versions

### When to Use
- Multi-device scenarios where the same user may access data from different cache nodes
- Systems where TTL-based invalidation is too slow but event-driven invalidation is too complex
- Optimistic concurrency control — version stamps double as conflict detection

### When NOT to Use
- Anonymous/unauthenticated traffic where clients can't carry version state
- Write-heavy workloads where the version churn is high and cache entries are invalidated before they can be read
- When the client cannot be trusted to report its version honestly (use server-side tracking instead)

**Also see**: [Session Affinity](#session-affinity) · [Cache Invalidation](#cache-invalidation) · [Optimistic Locking](../data-concurrency.md#optimistic-locking)

---

## Session Affinity

Also known as **sticky sessions** — routing all requests from the same user (or session) to the same backend or cache node. Ensures that a user consistently reads from the same cache replica, avoiding stale reads caused by replication lag between cache nodes.

> **Key insight**: Session affinity is a consistency workaround, not a scalability pattern. It trades load-balancing precision for read-your-writes consistency within a single cache cluster. When a user switches devices or regions, session affinity breaks — cross-device consistency requires additional mechanisms like version stamps or cross-region invalidation.

### Key Characteristics
- **User-to-node pinning**: Requests from the same session are routed to the same cache shard
- **Consistency within node**: No replication lag because reads and writes hit the same node
- **Fragile across devices**: Mobile and laptop may hit different nodes in different regions
- **Load imbalance risk**: Hot users can overload their pinned node

### When to Use
- Single-region deployments where read-your-writes consistency matters
- Combined with version stamps as a belt-and-suspenders approach for cache consistency
- Session state that changes infrequently and is accessed from a single device at a time

### When NOT to Use
- Multi-device scenarios where users switch between mobile, laptop, and tablet
- Geo-distributed deployments where the same user may be routed to different regions
- As the sole consistency mechanism — always pair with TTL or version stamps as a safety net

**Also see**: [Version Stamps](#version-stamps) · [Cache Invalidation](#cache-invalidation) · [Replication Lag](../data-architecture.md#replication-lag) · [Cross-Region Invalidation](#cross-region-invalidation)

---

## Cross-Region Invalidation

The mechanism by which a cache invalidation performed in one geographic region is propagated to cache nodes in all other regions, ensuring that users see consistent data regardless of which data center serves their request. Typically implemented via cross-region message queue replication (e.g., Kafka MirrorMaker).

> **Key insight**: Within a single region, event-driven invalidation can achieve near-real-time consistency. Across regions, you are bound by the speed of light and WAN latency — cross-region invalidation is inherently eventually consistent. The design question is not "how do I make it instant?" but "how short is the inconsistency window, and is it acceptable?"

### Key Characteristics
- **Message queue replication**: Kafka topics mirrored across regions; invalidation events propagate globally
- **Seconds-scale delay**: Cross-region replication adds 100ms–2s depending on geographic distance
- **Eventual consistency**: Stale reads are possible during the propagation window; TTL caps the maximum staleness
- **Regional autonomy**: Each region can operate independently if the replication link fails

### When to Use
- Global user base where the same user may be routed to different regions
- Multi-region active-active deployments with local caches
- Cart systems, user profiles, or any data where cross-device consistency matters

### When NOT to Use
- Single-region deployments — event-driven invalidation within the region is sufficient
- When cross-region replication latency exceeds the acceptable staleness window
- Strongly consistent data (inventory, payments) — read directly from the database instead

**Also see**: [Event-Driven Invalidation](#event-driven-invalidation) · [Session Affinity](#session-affinity) · [Replication Lag](../data-architecture.md#replication-lag) · [CAP Theorem](../architecture-patterns.md#cap-theorem)

### Cache Failures & Resiliency

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

## Stale Read Rate

A monitoring metric that measures the percentage of cache reads that return data older than the current value in the database. Calculated by comparing the cache entry's timestamp (or version) against the database's current timestamp on a sample of reads.

> **Key insight**: Stale read rate is the canary for cache invalidation health. A rising stale read rate means your invalidation pipeline is broken — events are not being delivered, TTLs are too long, or replication lag is growing. Catch it before users do.

### Key Characteristics
- **Sampling-based**: Not measured on every read — a configurable sample rate balances accuracy vs overhead
- **Requires timestamp/version**: Both cache and database must carry comparable timestamps
- **Layered monitoring**: Each cache layer (Redis, CDN, local) has its own stale read rate
- **Leading indicator**: Rises before users notice — unlike complaint-driven detection

### When to Use
- Production monitoring of cache invalidation pipelines
- Alerting: page when stale read rate exceeds threshold (e.g., >1% for 5 minutes)
- Capacity planning: correlate stale read rate with replication lag and event processing lag

### When NOT to Use
- Systems where staleness is acceptable by design (e.g., analytics dashboards with known 1-hour lag)
- When the overhead of timestamp comparison on every sampled read is unacceptable
- Without a clear SLO — measuring stale reads without an action threshold is just noise

**Also see**: [Cache Hit Ratio](#cache-hit-ratio) · [TTL](#ttl-time-to-live) · [Event-Driven Invalidation](#event-driven-invalidation) · [Cache Invalidation](#cache-invalidation)

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

## Cache Hit Ratio

The percentage of requests served directly from the cache without needing to query the backing store (database, origin server, etc.). Calculated as `hits / (hits + misses) × 100`.

> **Key insight**: In read-heavy systems, the cache hit ratio is the single most important performance metric. A drop from 99% to 95% means the database sees 5× more traffic — enough to cascade into a full outage during viral events.

### Key Characteristics
- **Layered measurement**: Each caching layer (CDN → Redis → local in-memory) has its own hit ratio; each drop signals a different problem
- **Inverse relationship with database load**: `database QPS = total requests × (1 - cache_hit_ratio)`
- **TTL sensitivity**: Longer TTLs increase hit ratio but trade off freshness; shorter TTLs reduce hit ratio but keep data current
- **Key distribution matters**: A 99% hit ratio on 1M unique keys behaves differently than a 99% hit ratio where 1% of keys have a 0% hit rate (hot-key skew)

### When to Use
- Monitoring the health of caching layers in production
- Setting SLOs for cache performance (e.g., "CDN hit ratio must stay above 98%")
- Capacity planning — determining how much database capacity is needed based on expected hit ratio and traffic
- Debugging cache-related incidents: a sudden drop in hit ratio is the earliest signal of a problem

### When NOT to Use
- As a standalone metric without per-key granularity — overall hit ratio can hide hot-key problems
- Write-heavy workloads where cache hit ratio is naturally low and not the primary concern
- When cache performance is not the bottleneck (e.g., CPU-bound computation, not I/O-bound lookups)

### Also see
- [Hot Key](#hot-key) · [CDN](../networking.md#cdn) · [TTL](#ttl-time-to-live) · [Eviction Policies](#eviction-policies)

---

### Hot Key Patterns

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

## Edge Pre-positioning

Placing content at the **network edge before demand arrives**, so that the cache is already warm when the first user requests it. The opposite of lazy/pull-through caching, where the first request triggers the cache fill.

> **Key insight**: At scale, reacting to demand is already too late. Pre-positioning decouples cache population from user requests, so peak demand does not coincide with peak system load.

### Key Characteristics
- **Predictive fill**: Content is copied to edge nodes during quiet hours based on demand forecasting
- **ISP-level placement**: Appliances sit inside ISP data centers or internet exchange points, minimizing last-mile latency
- **Region-specific catalog**: Each edge node holds only the slice of the catalog its region is most likely to request
- **Zero cold-start for premieres**: New releases are pre-loaded before the launch window, eliminating the origin stampede

### When to Use
- Large-scale content delivery where central origin would be overwhelmed (streaming, software downloads, game updates)
- Scheduled releases or premieres with predictable demand spikes
- Read-heavy workloads where pre-computing results is cheaper than computing on every request
- Bandwidth-sensitive deployments where egress costs from a central location are prohibitive

### When NOT to Use
- Highly dynamic content that changes unpredictably (real-time feeds, user-generated content with no release schedule)
- Small catalogs where the storage cost of full replication outweighs the latency benefit
- When demand is truly unpredictable and prediction accuracy would be too low to justify pre-filling
- Low-traffic deployments where lazy caching is sufficient

### Also see
- [CDN](../networking.md#cdn) · [Cache-Aside Pattern](#cache-aside-pattern) · [Hot Key](#hot-key) · [Cache Stampede](#cache-stampede)

### Redis Internals

## Redis Cluster

Redis's native sharding mechanism that distributes data across multiple Redis nodes using **hash slots** (CRC16). Each key is mapped to one of 16,384 hash slots, and each node in the cluster is responsible for a subset of those slots.

> **Key insight**: Redis Cluster distributes _keys_ evenly across nodes, but not _load_. A single hot key maps to exactly one hash slot on one node — scaling the cluster size does not increase throughput for that key. This is why hot-key mitigation (replication, local cache, request coalescing) is required on top of Redis Cluster.

### Key Characteristics
- **Hash-slotted sharding**: CRC16(key) % 16384 determines the slot; slots are assigned to nodes in contiguous ranges
- **Automatic failover**: Each shard can have replicas; if a primary fails, a replica is promoted
- **Client-side routing**: Clients maintain a slot-to-node map and route directly to the correct node (no proxy)
- **Hash tags**: `{user:123}:profile` and `{user:123}:settings` map to the same slot, enabling multi-key operations

### When to Use
- Horizontally scaling Redis beyond a single node's memory capacity
- High-availability deployments requiring automatic failover
- Workloads with high cardinality keys where load is naturally distributed
- Multi-key operations that can be co-located using hash tags

### When NOT to Use
- Hot-key workloads where a single key dominates traffic — Redis Cluster alone will not help; combine with replication strategies
- Write-heavy single-key workloads where the key must be the serialization point
- Simple deployments where a single Redis instance with read replicas is sufficient
- When cross-slot transactions are required (not supported in cluster mode)

### Also see
- [Hash Slots](#hash-slots) · [Hot Key](#hot-key) · [Cache Replication](../data-architecture.md#cache-replication) · [Request Coalescing](#request-coalescing)

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

## Lua Scripting (Redis)

Redis's built-in Lua interpreter that allows executing custom scripts atomically on the server. Scripts run inside `EVAL` / `EVALSHA` and execute as a single uninterruptible unit — no other Redis command can interleave. This is the foundation for building race-condition-free multi-step operations like token-bucket rate limiters, distributed locks, and atomic check-and-update workflows without relying on client-side coordination.

### Key Characteristics
- **Atomic execution**: The entire script runs without interruption; no other client's commands execute until the script completes
- **Server-side logic**: Computation happens on the Redis server, eliminating network round-trips for multi-step operations
- **Script caching**: `EVALSHA` caches the script by SHA1 hash, reducing bandwidth after the first invocation
- **Sandboxed**: Lua scripts cannot access the filesystem, network, or external libraries — they can only call Redis commands

### When to Use
- Multi-step atomic operations where read and write must not be interleaved (e.g., token bucket check + deduct)
- Complex conditional logic that can't be expressed as a single Redis command
- Reducing round-trips: combine multiple GET/SET/INCR into one `EVAL` call

### When NOT to Use
- Simple single-command operations (`INCR`, `SET`, `ZADD` are already atomic individually)
- Long-running scripts (block all other clients; keep scripts under a few milliseconds)
- When the logic is better tested and maintained in application code and atomicity isn't required

### Example: Atomic Token-Bucket Check-and-Deduct

```lua
-- EVAL this script: redis-cli EVAL "$(cat rate_limiter.lua)" 2 user:123:tokens user:123:ts 10 50 1719876543 1
local tokens_key   = KEYS[1]
local timestamp_key = KEYS[2]
local rate      = tonumber(ARGV[1])  -- tokens/sec refill
local capacity  = tonumber(ARGV[2])  -- max burst
local now       = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])  -- usually 1

local last_tokens = tonumber(redis.call("get", tokens_key)) or capacity
local last_ts     = tonumber(redis.call("get", timestamp_key)) or 0
local delta       = math.max(0, now - last_ts)
local filled      = math.min(capacity, last_tokens + delta * rate)

if filled >= requested then
  redis.call("setex", tokens_key, 60, filled - requested)
  redis.call("setex", timestamp_key, 60, now)
  return {1, filled - requested}  -- allowed
end
return {0, filled}  -- rejected
```

> The entire read→calculate→decide→write runs atomically. No other client can interleave between the `get` and `set`.

### Also see
- [MULTI/EXEC (Redis Transactions)](#multiexec-redis-transactions) · [Atomic Conditional Update](../data-concurrency.md#atomic-conditional-update) · [Rate Limiting](../api-design.md#rate-limiting)

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

## MULTI/EXEC (Redis Transactions)

Redis's transaction mechanism that batches multiple commands into an **atomic, isolated** execution block. Commands between `MULTI` and `EXEC` are queued and executed sequentially without interleaving from other clients. Unlike SQL transactions, MULTI/EXEC does not support rollback — all queued commands execute, even if some fail. Used for atomic multi-step operations like rolling-window rate limiters and cache invalidation patterns.

### Key Characteristics
- **Atomic batch**: All commands in the block execute as one uninterrupted unit — no other client interleaves
- **No rollback**: If one command fails (e.g., wrong type), remaining commands still execute — errors must be handled client-side
- **Optimistic locking with WATCH**: `WATCH key` + `MULTI`/`EXEC` enables compare-and-set: the transaction aborts if watched keys are modified before EXEC
- **Isolation only**: Provides isolation, not atomicity in the ACID sense — partial failures are possible

### When to Use
- Batching related operations that must not be interleaved (e.g., `ZREMRANGEBYSCORE` + `ZRANGE` + `ZADD` + `EXPIRE` for rolling-window rate limiting)
- Implementing check-and-set with `WATCH` when Lua scripting is overkill
- Simple transactional workflows where rollback isn't needed

### When NOT to Use
- When rollback on failure is required — use application-level compensating transactions instead
- Complex conditional logic — Lua scripts are more expressive and avoid extra round-trips
- When a single atomic command (`INCR`, `SETNX`, `HSET`) is sufficient

### Example: Rolling-Window Rate Limiter (Node.js)

```javascript
// Atomic window: remove old entries → count remaining → record this request
const key = `rate_limit:${userId}`;
const now = Date.now();
const windowStart = now - 60_000;  // 60-second rolling window

const results = await client
  .multi()
  .zremrangebyscore(key, 0, windowStart)  // ① drop expired
  .zrange(key, 0, -1)                     // ② fetch current window
  .zadd(key, now, now.toString())          // ③ record this attempt
  .expire(key, 60)                         // ④ auto-cleanup TTL
  .exec();

const requestCount = results[1].length;    // count from step ②
const limited = requestCount >= 100;       // 100 req/min limit
```

**Java (Jedis)**:

```java
import redis.clients.jedis.Jedis;
import redis.clients.jedis.Transaction;
import redis.clients.jedis.Response;

boolean isRateLimited(Jedis jedis, String userId, int maxRequests, long windowMs) {
    String key = "rate_limit:" + userId;
    long now = System.currentTimeMillis();
    long windowStart = now - windowMs;

    Transaction tx = jedis.multi();
    tx.zremrangeByScore(key, 0, windowStart);       // ① drop expired
    Response<Set<String>> rangeResp = tx.zrange(key, 0, -1); // ② fetch window
    tx.zadd(key, (double) now, String.valueOf(now)); // ③ record attempt
    tx.expire(key, (int) (windowMs / 1000));          // ④ auto-cleanup TTL
    tx.exec();

    int requestCount = rangeResp.get().size();        // count from step ②
    return requestCount >= maxRequests;
}
```

> All four commands execute as one uninterrupted block — no race between `ZRANGE` and `ZADD`. Even if two requests arrive simultaneously, each sees the other's addition. The `Response<Set<String>>` is a future-like handle — its value is available only after `exec()` completes.

### Also see
- [Lua Scripting (Redis)](#lua-scripting-redis) · [Atomic Conditional Update](../data-concurrency.md#atomic-conditional-update) · [Rate Limiting](../api-design.md#rate-limiting)

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

---

## SET NX (Redis)

The Redis `SET key value NX` command — "set if not exists." It atomically creates a key only if it does not already exist, returning `OK` on success and `(nil)` if the key was already present. This is the foundational primitive for building lightweight deduplication gatekeepers, distributed locks, and idempotency filters.

```
Consumer receives event with eventId = "abc-123"
  → Redis: SET event:abc-123 "processing" NX EX 300
    ├─ Returns OK     → First time seeing this event → process it
    └─ Returns (nil)  → Duplicate → discard immediately
```

### Key Characteristics
- **Atomic check-and-set**: The existence check and set happen in a single atomic operation — no race condition between check and write
- **Always pair with TTL**: Use `EX` or `PX` to set an expiry; without it, keys accumulate indefinitely and cause memory leaks
- **Sub-millisecond latency**: Redis serves SET NX in microseconds, making it suitable as a high-throughput pre-filter
- **TTL should exceed retry window**: Set the TTL longer than the broker's maximum retry window to cover all possible duplicate deliveries

### When to Use
- Deduplication gatekeeper before expensive business logic in event-driven consumers
- Lightweight distributed lock for non-critical operations (cache refresh, job dedup)
- Ensuring only one consumer instance processes a given event at a time

### When NOT to Use
- As the sole deduplication mechanism — Redis can lose keys on eviction or restart; always pair with DB constraints
- For correctness-critical locking (use Redlock or ZooKeeper with fencing tokens instead)

**Also see**: [Deduplication Store](../messaging.md#deduplication-store), [Atomic Deduplication](../messaging.md#atomic-deduplication), [Idempotency](../cqrs-event-driven.md#idempotency), [TTL](#ttl-time-to-live)

---

### Advanced Mitigations

## Single-Flight Execution

A cache-stampede mitigation pattern that **collapses concurrent duplicate requests for the same cache key into a single database query**. When multiple requests arrive simultaneously for a key that is not in cache, only one request is allowed to query the database; all other requests wait for and share that single result. Also known as request coalescing or deduplication-at-the-gate.

```
Requests A, B, C simultaneously request key "user:123"
  → Cache miss for all three
  → Request A acquires the "flight lock" for "user:123"
  → Requests B, C wait on the lock
  → Request A: SELECT * FROM users WHERE id=123
  → Request A: SET user:123 <data> EX 300
  → Requests B, C: receive the cached result from A
```

### Key Characteristics
- **Lock-per-key granularity**: Only requests for the same key block each other; requests for different keys proceed independently
- **Reduces DB load to O(1)**: Regardless of how many concurrent requests arrive, the database receives exactly one query per unique key
- **In-memory coordination**: Typically implemented with an in-process lock or concurrent map, not an external service

### When to Use
- High-traffic endpoints where a cache miss would trigger hundreds of identical database queries
- Cold-start scenarios after a cache flush or deployment restart
- Any cache-aside pattern where the cache miss penalty is expensive (complex queries, external API calls)

### When NOT to Use
- When cache hit rates are already above 99% — the coordination overhead exceeds the benefit
- When the database query is trivially cheap (e.g., primary key lookup on an indexed table)
- Across service instances — in-process locks don't work across instances; use a distributed lock or let each instance query independently

### Also see
- [Cache Stampede](#cache-stampede) · [PER Algorithm](#per-algorithm) · [Request Coalescing](#request-coalescing) · [Cache-Aside Pattern](#cache-aside-pattern)

---

## Soft TTL

A cache-freshness pattern where the **cache entry embeds its own logical expiration time** separately from Redis's physical TTL. A background worker detects entries approaching their soft expiry and proactively refreshes them before the hard TTL deletes the key. This prevents cache-stampede cold starts by ensuring popular keys never truly expire — they are refreshed in the background while still serving traffic.

```
Cache entry: { data: {...}, softExpiresAt: 1720000000 }
Redis TTL:   EX 600 (10 minutes hard expiry)
Soft TTL:    480 seconds (8 minutes — refresh before hard expiry)

At t=480s: Background worker sees softExpiresAt is in the past
  → Worker: SELECT * FROM users WHERE id=123
  → Worker: SET user:123 <new_data> EX 600
  → Meanwhile: existing (slightly stale) data is still served
```

### Key Characteristics
- **Dual-expiry design**: Soft expiry triggers refresh; hard (Redis) TTL is the safety net
- **No cache misses during refresh**: The old value remains available while the new value is being computed
- **Requires background workers**: A scheduler or cron job must periodically scan for keys nearing soft expiry

### When to Use
- Keys that are expensive to compute and have predictable refresh cadences
- Data where serving slightly stale data is acceptable but cache misses are not (e.g., user profiles, configuration, feature flags)
- Hot keys that, if they expire, would trigger a stampede

### When NOT to Use
- When data freshness requirements are strict (e.g., financial balances, inventory counts)
- When the dataset is too large to scan for soft-expiry — use event-driven invalidation instead
- When the operational complexity of background workers outweighs the benefit

### Also see
- [TTL](#ttl-time-to-live) · [Cache Stampede](#cache-stampede) · [Event-Driven Invalidation](#event-driven-invalidation) · [Probabilistic Early Invalidation](#probabilistic-early-invalidation)

---

## Probabilistic Early Invalidation

A cache-refresh optimization that uses an **algorithm to probabilistically refresh cache entries before they expire**, based on request frequency. The more often a key is accessed, the earlier it gets refreshed — spreading refresh load across time rather than concentrating it at expiration. This is also known as the XFetch algorithm or probabilistic recaching.

### Key Characteristics
- **Rate-adaptive**: Refresh probability increases as time-to-expiry decreases and as request rate increases
- **No central coordinator**: Each cache read independently decides whether to trigger a refresh based on a probability function
- **Smooths refresh spikes**: Instead of all hot keys refreshing at once, refreshes are distributed across the expiration window

### When to Use
- Systems with many hot keys that expire at similar times (scheduled cache rebuilds, TTL-aligned deployments)
- When single-flight execution alone is insufficient because the stampede spans many different keys

### When NOT to Use
- When the dataset is small and refresh is cheap — the probabilistic logic adds unnecessary complexity
- When strict consistency is required — probabilistic refresh always has a chance of serving stale data

### Also see
- [Cache Stampede](#cache-stampede) · [Soft TTL](#soft-ttl) · [PER Algorithm](#per-algorithm) · [Single-Flight Execution](#single-flight-execution)
