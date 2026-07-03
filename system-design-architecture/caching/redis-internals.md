---
type: System Design
title: "Redis Internals — Key Takeaways"
description: "I/O multiplexing, hash slots, Copy-on-Write persistence, Morris probabilistic counter, UNLINK async deletion, and server-assisted client-side caching"
timestamp: 2026-06-15T00:00:00Z
---

# 31. Redis Internals — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [If You Only Know 'Redis is Single-Threaded', You Know Nothing](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)
> **Purpose**: Extract reusable architectural patterns from the Redis internals deep-dive.

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Cache stampede, invalidation, anti-patterns, eviction, request coalescing
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — TTL, eviction policies, cache-aside, cache stampede, request coalescing, PER algorithm
> **Taxonomy Reference**: §7.3 Caching Strategies

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-06](#cache-06) | Multi-threaded servers waste CPU on context-switching & lock contention | I/O Multiplexing with single-threaded event loop |
| [cache-07](#cache-07) | Consistent hashing requires rehashing all keys when cluster topology changes | Fixed hash slots (16,384) with CRC16 routing |
| [cache-08](#cache-08) | Writing full memory snapshot to disk blocks the main thread | fork() + Copy-on-Write for non-blocking persistence |
| [cache-09](#cache-09) | Full per-key frequency counters are memory-prohibitive at scale | 8-bit Morris probabilistic counter with time decay |
| [cache-10](#cache-10) | DEL blocks the main thread while freeing memory for large keys | UNLINK — synchronous keyspace removal + async memory free |
| [cache-11](#cache-11) | TTL-based client-side caching is guesswork on freshness | Server-assisted client-side caching with TRACKING invalidation |
| [cache-12](#cache-12) | Counting unique items requires O(n) memory with exact approaches | Probabilistic cardinality estimation with bounded memory (HyperLogLog) |
| [cache-13](#cache-13) | Single-bucket estimates are skewed by unlucky hash values | Harmonic mean across M buckets for outlier-resistant aggregation |
| [cache-14](#cache-14) | Computing unique users across time windows requires storing all IDs | HLL merging (PFMERGE) for automatic cross-window deduplication |
| [cache-15](#cache-15) | Tracking unique users through conversion funnels requires heavy queries | One HLL counter per funnel step for real-time analytics |

---

## cache-06: I/O Multiplexing — Single-Threaded Event Loop

> **Source**: [§"1. Single-Threaded, But Not Blocking: I/O Multiplexing"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | Multi-threaded servers waste CPU cycles on context-switching, lock contention, and thread scheduling overhead — especially under high concurrency |
| **Root cause** | One-thread-per-connection model forces the OS to schedule between blocked threads, each waiting on I/O |

**Strategy**: Use a **single-threaded event loop** with OS-level I/O multiplexing (epoll on Linux, kqueue on BSD/macOS). One thread monitors all open file descriptors and reacts only when data is ready — never blocking, never context-switching.

```
Traditional multi-threaded:          Redis event loop:
Thread 1 -> Conn A (waiting)         +------------------+
Thread 2 -> Conn B (waiting)         |  epoll/kqueue     |
Thread 3 -> Conn C (working)         |  monitors all FDs |
                                     +--------+---------+
Problem: threads block,                      | "data ready on C"
context-switch, contend on locks             v
                                     +------------------+
                                     | Process conn C    |
                                     | Return to loop    |
                                     +------------------+
                                     Result: zero locks, zero
                                     context switches, microsecond latency
```

| Tradeoff | Detail |
|:---|:---|
| **CPU-bound ops block everything** | A single slow command blocks all other clients — mitigated by async operations (UNLINK), background threads (RDB), and pipelining |
| **Cannot exploit multi-core** | One event loop = one core for command processing; scaling requires multiple Redis instances or Redis Cluster |
| **Predictable latency** | No thread-scheduling jitter — 99th percentile latency stays in microseconds |

> **Also see**: [Async & Concurrency Patterns](stream-processing/async-concurrency-patterns.md) — Thread pool exhaustion, post-commit dispatch
> **Dictionary**: [I/O Multiplexing](../../reference-dictionary/caching.md#io-multiplexing)
> **Azure**: Azure Cache for Redis uses the same event-loop architecture; Premium tier adds persistence via RDB/AOF
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-07: Hash Slots — Fixed-Partition Data Distribution

> **Source**: [§"2. Hash Slots, Not Consistent Hashing"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | Consistent hashing requires rehashing existing keys when nodes are added or removed, causing unpredictable data movement and potential hot spots |
| **Root cause** | Consistent hashing maps keys to a continuous ring; topology changes shift key ownership boundaries unpredictably |

**Strategy**: Use **16,384 fixed hash slots** with CRC16(key) mod 16384. Each cluster node owns a range of slots. When rebalancing, move slot ownership between nodes — keys don't need rehashing, only the slot-to-node mapping changes.

```
+-------------+   +-------------+   +-------------+
|   Node A    |   |   Node B    |   |   Node C    |
| slots 0-5460|   |5461-10922   |   |10923-16383  |
+-------------+   +-------------+   +-------------+
       ^                 ^                 ^
       +-----------------+-----------------+
                  CRC16(key) % 16384
                  routes here
```

| Tradeoff | Detail |
|:---|:---|
| **Less flexible than consistent hashing** | 16,384 slots is a fixed number; can't grow beyond that granularity |
| **Predictable rebalancing** | Adding a node means migrating a slice of slots — bounded, operationally simple |
| **No key rehashing** | Keys stay where they are; only slot->node mapping changes |
| **Manual slot migration** | Unlike consistent hashing's automatic rebalancing, Redis Cluster requires explicit CLUSTER SETSLOT commands |

> **Also see**: [API & Network Design](api-network/api-network-design.md) — Consistent hash routing for API gateways
> **Dictionary**: [Hash Slots](../../reference-dictionary/caching.md#hash-slots)
> **Azure**: Azure Cache for Redis Enterprise tier supports Redis Cluster with automatic sharding
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-08: Copy-on-Write Persistence — Non-Blocking Snapshots

> **Source**: [§"3. Fork + Copy-on-Write: How RDB Persistence Works Without Downtime"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | Writing the entire in-memory dataset to disk while serving production traffic should block everything — but it doesn't |
| **Root cause** | Naive approach: serialise all data from the main thread blocks all client requests for the duration of the dump |

**Strategy**: Use fork() to create a child process that sees a consistent snapshot of memory at fork time. The parent continues serving traffic. Linux **Copy-on-Write (COW)** ensures only pages modified after the fork get duplicated in physical memory — unchanged pages are shared.

```
Redis parent (serving traffic)
        |
        |-- fork() -------------------+
        |                             |
        v                             v
Parent continues serving     Child writes memory
writes/reads normally        snapshot to disk (dump.rdb)
        |                             |
        |  Modified page? -> OS dups  |
        |  (COW kicks in)   only that page
        |                             |
        |              dump.rdb done  |
        |<--------- child exits ------+
```

| Tradeoff | Detail |
|:---|:---|
| **Memory overhead proportional to write rate** | During the snapshot window, every write causes a COW page duplication — high write throughput can double memory usage temporarily |
| **Not crash-safe** | RDB snapshots are point-in-time; data written between snapshots is lost on crash (mitigated by AOF append-only file) |
| **fork() latency** | On large instances (tens of GB), fork() itself can take hundreds of milliseconds — mitigated by fork-time-sleep in Redis 7 |
| **Zero service interruption** | The parent process never pauses — clients see no impact |

> **Also see**: [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md) — Isolation levels, distributed locks
> **Dictionary**: [Copy-on-Write Persistence](../../reference-dictionary/caching.md#copy-on-write-persistence)
> **Azure**: Azure Cache for Redis Premium supports RDB persistence with configurable backup frequency
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-09: Morris Probabilistic Counter — 8-Bit LFU Eviction

> **Source**: [§"4. LFU With an 8-Bit Counter"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | Tracking access frequency per key for millions of keys with a real integer counter would consume prohibitive memory (8+ bytes per key) |
| **Root cause** | A full 32-bit or 64-bit counter per key is ~8x the space budget most caches can afford for metadata |

**Strategy**: Use a **Morris probabilistic counter** — only 8 bits per key. The counter increments with decreasing probability as its value grows, approximating frequency ~ 2^counter (logarithmic scale). Additionally, the counter **decays over time** so stale-popular keys don't hold their position forever.

```python
def morris_increment(counter: int) -> int:
    # Higher counter = lower probability of incrementing
    # Prevents saturation while approximating log scale
    probability = 1.0 / (counter * 10 + 1)
    if random() < probability:
        return counter + 1
    return counter
```

| Tradeoff | Detail |
|:---|:---|
| **Approximation, not precision** | Counter value c maps to ~2^c actual accesses — fine for eviction ranking, not for billing/accounting |
| **Time decay is tunable** | lfu-decay-time controls how fast old accesses lose weight — 0 = no decay, 1 = fastest decay |
| **8-bit ceiling** | Max counter value is 255, representing ~2^255 accesses (far beyond practical need) |
| **Memory: 1 byte per key** | vs 4-8 bytes for a standard counter — 4-8x memory savings |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-04-eviction-policies) — LRU vs LFU policy selection
> **Dictionary**: [Morris Probabilistic Counter](../../reference-dictionary/caching.md#morris-probabilistic-counter)
> **Azure**: Azure Cache for Redis supports allkeys-lfu and volatile-lfu eviction policies using this counter
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-10: UNLINK — Non-Blocking Key Deletion

> **Source**: [§"5. UNLINK Is Not DEL"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | DEL blocks the main thread while freeing memory for large keys (e.g., a set with 5 million elements) — stalling all other clients |
| **Root cause** | DEL synchronously removes the key from the keyspace AND frees all associated memory in the same main-thread operation |

**Strategy**: Use **UNLINK** — it removes the key from the keyspace synchronously (instant) and delegates the memory freeing to a background thread. The key disappears from the client's perspective immediately; the memory cleanup happens asynchronously without blocking the main event loop.

```
DEL large_key:
  Main thread -> unlinks key -> frees all memory -> resumes
                                (blocks here)

UNLINK large_key:
  Main thread -> removes key from keyspace -> resumes immediately
                                                 |
                               background thread <+
                               handles memory free async
```

| Tradeoff | Detail |
|:---|:---|
| **Slightly higher memory watermark** | Freed memory isn't reclaimed instantly — peak memory may be higher during async cleanup |
| **Not needed for small keys** | Overhead of scheduling async work outweighs benefit for small keys; use DEL for keys <~100 elements |
| **Redis 4.0+ only** | UNLINK was introduced in Redis 4.0; older versions only have DEL |
| **Also applies to FLUSHDB/FLUSHALL** | FLUSHDB ASYNC and FLUSHALL ASYNC use the same lazy-free mechanism |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-02-cache-invalidation) — Cache-Aside with explicit delete on write
> **Dictionary**: [UNLINK (Async Deletion)](../../reference-dictionary/caching.md#unlink-async-deletion)
> **Azure**: Azure Cache for Redis 4.0+ supports UNLINK; use it for TTL-based eviction cleanup in production
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-11: Server-Assisted Client-Side Caching (TRACKING)

> **Source**: [§"6. Client-Side Caching With Server Invalidation (Redis 6+)"](../../articles/caching/If You Only Know ‘Redis is Single-Threaded’, You Know Nothing.md)

| | |
|:---|:---|
| **Problem** | Client-side caching with TTL-only freshness is guesswork — clients either serve stale data or make unnecessary round-trips to revalidate |
| **Root cause** | Without server involvement, clients have no way to know when cached data has been modified by another client |

**Strategy**: Redis 6+ **TRACKING** enables server-assisted client-side caching. Clients register with CLIENT TRACKING ON, and Redis pushes invalidation messages whenever a tracked key is modified. Clients evict their local copy on invalidation and fetch fresh data on the next read — achieving **zero stale reads** with **fewer round trips**.

```
Without TRACKING:                      With TRACKING:
Client -> GET key -> Redis -> value    Client -> CLIENT TRACKING ON -> Redis
Client caches locally (TTL guess)      Client -> GET key -> Redis -> value
Client reads stale until TTL expires   Client caches locally

                                       Later:
                                       App updates key -> Redis
                                       Redis -> invalidation msg -> Client
                                       Client -> cache evicted
                                       Next read -> fresh data

Result: zero stale reads, fewer round trips
```

| Tradeoff | Detail |
|:---|:---|
| **Server memory overhead** | Redis must maintain an invalidation table mapping clients to tracked keys — tracking-table-max-keys limits this |
| **Protocol complexity** | Requires RESP3 protocol support in the client library; not all clients implement it |
| **Broadcast mode alternative** | BCAST mode avoids the per-key invalidation table by broadcasting all key modifications — more memory-efficient but less precise |
| **Opt-in** | Clients must explicitly enable tracking; no backward-compatibility impact |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-01-cache-stampede) — Cache stampede prevention, PER algorithm
> **Dictionary**: [Server-Assisted Client-Side Caching](../../reference-dictionary/caching.md#server-assisted-client-side-caching)
> **Azure**: Azure Cache for Redis Enterprise tier supports RESP3 and TRACKING for low-latency client-side caching
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-12: HyperLogLog — Probabilistic Cardinality Estimation with Bounded Memory

> **Source**: [HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory](../../articles/databases/hyperloglog-cardinality-estimation.md)

| | |
|:---|:---|
| **Problem** | Counting unique items (cardinality) requires O(n) memory with exact approaches — a `COUNT(DISTINCT)` over billions of rows consumes gigabytes of RAM and slows to a crawl under concurrent load |
| **Root cause** | To count unique items exactly, you must remember every item you've ever seen; memory requirement scales linearly with cardinality |

**Strategy**: Use the **leading-zero observation** from the Flajolet-Martin algorithm: the maximum number of leading zeros in hashed values is a probabilistic estimator of cardinality. HyperLogLog improves this by splitting into `M` buckets (using first bits of the hash) and using the **harmonic mean** across bucket values — which naturally dampens outlier bias without needing to discard values. Memory is O(M) regardless of dataset size.

```
Exact counting:                        HyperLogLog:
Input size → memory = O(n)             Input size → memory = O(M) ≈ 12 KB
1B unique items → ~8 GB RAM            1B unique items → 12 KB RAM
                                        Error: ~0.81% (Redis, M=16384)
```

| Tradeoff | Detail |
|:---|:---|
| **Approximate only (~1-2% error)** | Unsuitable for billing, legal, or financial exact-count requirements |
| **Not enumerable** | You cannot retrieve which elements were added — only the estimated count |
| **Hash-function dependent** | A poor hash function destroys uniformity and inflates error |
| **Small-set inaccuracy** | Below ~100 elements, error can be higher than the stated bound |

> **Also see**: [Databases & Query Performance](../databases/query-performance.md) — COUNT(DISTINCT) optimization, query planning
> **Dictionary**: [HyperLogLog](../../reference-dictionary/architecture-patterns.md#hyperloglog), [Cardinality Estimation](../../reference-dictionary/databases.md#cardinality-estimation), [Bloom Filter](../../reference-dictionary/databases.md#bloom-filter)
> **Azure**: [Azure Cache for Redis](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/) supports PFADD/PFCOUNT/PFMERGE natively with ≤12 KB per HLL structure
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-13: Harmonic Mean for Outlier-Resistant Aggregation

> **Source**: [HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory](../../articles/databases/hyperloglog-cardinality-estimation.md)

| | |
|:---|:---|
| **Problem** | Single-bucket Flajolet-Martin estimates are skewed by one unlucky hash value with many leading zeros — one outlier can ruin the entire estimate |
| **Root cause** | A single maximum across all values is inherently fragile; one extreme observation dominates the result |

**Strategy**: Split the hash space into `M` buckets and compute the **harmonic mean** ($M / \sum(1/2^{\text{bucket}[i]})$) instead of geometric or arithmetic mean. The harmonic mean naturally gives less weight to large outliers — no sorting, no discarding, just a smarter average. This is what distinguishes HyperLogLog from its predecessors (LogLog used geometric mean; SuperLogLog discarded 30% of buckets).

```
Flajolet-Martin (1985):   Single bucket → max(L) → 2^max(L)       — fragile
LogLog (2003):             M buckets → geometric mean              — still outlier-sensitive
SuperLogLog (2007):        M buckets → discard top 30% → mean     — wastes storage + CPU
HyperLogLog (2007):        M buckets → harmonic mean              — elegant, no waste

Standard error comparison (M=1024):
  LogLog:        1.3/√M ≈ 4.1%
  SuperLogLog:   1.05/√M ≈ 3.3%
  HyperLogLog:   1.04/√M ≈ 3.25%
```

| Tradeoff | Detail |
|:---|:---|
| **Harmonic mean is less intuitive** | Developers may need to understand why it works — the math is less familiar than arithmetic mean |
| **Same memory as LogLog** | No extra storage needed vs. the sorting overhead of SuperLogLog |
| **Near-optimal** | The 1.04/√M error bound is provably close to the theoretical minimum for this class of estimators |

> **Also see**: [cache-12](#cache-12) — Full HyperLogLog algorithm description
> **Dictionary**: [HyperLogLog](../../reference-dictionary/architecture-patterns.md#hyperloglog)
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-14: HLL Merging for Time-Window Deduplication

> **Source**: [HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory](../../articles/databases/hyperloglog-cardinality-estimation.md)

| | |
|:---|:---|
| **Problem** | Computing unique users across a week requires storing all user IDs for 7 days — daily counts can't simply be summed because the same user may appear on multiple days |
| **Root cause** | Cardinality is not additive: |A ∪ B| ≠ |A| + |B| when A ∩ B ≠ ∅ |

**Strategy**: HLL counters are **mergeable** — Redis PFMERGE combines multiple HLL structures into one whose estimate approximates the true union cardinality. The merge is lossless with respect to the bucket maxima (max of corresponding buckets). Daily HLL counters can be merged into a weekly counter that automatically deduplicates returning users across days.

```
Day 1 HLL: users {u1, u2, u3, u4}     → ~4
Day 2 HLL: users {u2, u5, u6}         → ~3  (u2 returns)
Day 3 HLL: users {u1, u7, u8, u9}     → ~4  (u1 returns)

PFMERGE(week)  →  ~9 unique (not 4+3+4=11)

Memory: 3 × 12 KB = 36 KB for daily + 12 KB for merged = 48 KB total
vs. storing all 11 user IDs per day × 7 days ≈ hundreds of MB
```

| Tradeoff | Detail |
|:---|:---|
| **Merged estimate has same error as individual** | Merging doesn't compound error — the union estimate is as accurate as a single HLL |
| **Cannot un-merge** | Once merged, you can't extract per-day contributions — store daily HLLs separately if drill-down is needed |
| **Merge is O(M)** | PFMERGE iterates over all buckets; fast for M=16384 but not zero-cost |

> **Also see**: [cache-12](#cache-12) — HyperLogLog algorithm, [cache-15](#cache-15) — Funnel analytics
> **Dictionary**: [HyperLogLog](../../reference-dictionary/architecture-patterns.md#hyperloglog)
> **Azure**: Azure Cache for Redis supports PFMERGE for combining HLL structures across time windows or dimensions
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-15: Funnel Analytics with HLL Counters

> **Source**: [HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory](../../articles/databases/hyperloglog-cardinality-estimation.md)

| | |
|:---|:---|
| **Problem** | Tracking unique users through a conversion funnel (homepage → product → cart → checkout → purchase) traditionally requires heavy JOIN queries on user-event tables, which become prohibitively slow at scale |
| **Root cause** | Computing per-step unique counts AND step-to-step drop-off requires either a full user-event table in fast storage or expensive batch jobs |

**Strategy**: Maintain **one HLL counter per funnel step**. Each step records unique users reaching that stage. The counts are real-time, memory-efficient (~12 KB per step), and mergeable. Drop-off between steps is computed as the percentage difference — no need to join or scan event tables.

```
Funnel steps with HLL:
  homepage:     PFADD funnel:homepage:2024-01-15 u1 u2 u3 u4 u5  → ~5
  product_page: PFADD funnel:product_page:...     u1 u2 u3       → ~3  (40% drop-off)
  add_to_cart:  PFADD funnel:add_to_cart:...      u1 u2          → ~2  (33% drop-off)
  checkout:     PFADD funnel:checkout:...         u1             → ~1  (50% drop-off)
  purchase:     PFADD funnel:purchase:...         u1             → ~1  (0% drop-off)

Total memory: 5 steps × 12 KB = 60 KB
```

| Tradeoff | Detail |
|:---|:---|
| **Approximate drop-off rates** | Drop-off percentages inherit the ~1% HLL error — acceptable for analytics, not for revenue reporting |
| **Cannot answer 'which users dropped off'** | HLL only gives counts; to identify specific users who abandoned, you need the raw event log |
| **Per-step counters are independent** | Each step's HLL doesn't know about other steps — funnel coherence depends on consistent event instrumentation |

> **Also see**: [cache-12](#cache-12) — HyperLogLog algorithm, [cache-14](#cache-14) — HLL merging
> **Dictionary**: [HyperLogLog](../../reference-dictionary/architecture-patterns.md#hyperloglog), [Cardinality Estimation](../../reference-dictionary/databases.md#cardinality-estimation)
> **Azure**: Combine Azure Cache for Redis HLL with Azure Event Hubs for real-time funnel analytics at scale
> **Taxonomy**: §7.3 Caching Strategies
