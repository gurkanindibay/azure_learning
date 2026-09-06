---
type: System Design
title: "Redis Data Structure Selection — Key Takeaways"
description: "How to choose the right Redis data structure for common architectural problems: leaderboards, unique counting, message queuing, membership testing, and object storage — with tradeoffs and real-world examples."
generated: { by: process:okf-migrate, at: 2026-08-01T00:00:00Z }
---

# 41. Redis Data Structure Selection — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Redis Data Structures — The Backbone of High-Performance Applications](../../articles/caching/redis-data-structures.md)
> **Purpose**: Extract reusable architectural decision patterns for choosing the right Redis data structure.

> **Also see**: [Redis Internals](redis-internals.md) — I/O multiplexing, hash slots, COW persistence
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — Redis Strings, Redis Hashes, Redis Lists, Redis Sets, Redis Sorted Sets, Redis Bitmaps, Cuckoo Filters, Count-Min Sketch, Top-K, Redis Geospatial, RedisTimeSeries
> **Taxonomy Reference**: §7.3 Caching Strategies

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-43](#cache-43) | Developers default to Strings for everything, ignoring memory and performance implications | Data structure selection is a first-order architectural decision |
| [cache-44](#cache-44) | Leaderboards need ranked ordering; task queues need FIFO — same "ordered" requirement, wrong structure | Sorted Sets for score-based ranking, Lists for insertion-order queuing |
| [cache-45](#cache-45) | Counting unique visitors at scale with Sets requires storing every ID | HyperLogLog for approximate unique counting with 12 KB fixed memory |
| [cache-46](#cache-46) | Message queues built on Lists can't replay, can't fan-out, can't acknowledge | Redis Streams for consumer groups, message acknowledgment, and replay |
| [cache-47](#cache-47) | Checking millions of items for membership with Sets consumes GBs of memory | Bloom/Cuckoo Filters for space-efficient probabilistic membership testing |
| [cache-48](#cache-48) | Storing user profiles as flat JSON Strings wastes memory and prevents field-level operations | Hashes for field-level access, atomic increments, and compact encoding |

---

## cache-43: Data Structure Selection Is a First-Order Architectural Decision

> **Source**: [§"Introduction" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | Developers default to `SET`/`GET` for everything because Strings are the simplest mental model — ignoring that Redis offers 10+ specialized data structures, each optimized for different access patterns and memory profiles |
| **Root cause** | Redis is taught as a "key-value store," so engineers treat it as a hash map rather than a data structure server |

**Strategy**: Before writing any Redis code, identify the **access pattern** and **data shape** first, then select the structure that matches:

```
Access Pattern         →  Redis Structure
─────────────────────────────────────────────
Key → single value     →  String (SET/GET)
Key → ordered list     →  List (LPUSH/RPOP for queue)
Key → field→value map  →  Hash (HSET/HGET)
Key → unique items     →  Set (SADD/SISMEMBER)
Key → ranked items     →  Sorted Set (ZADD/ZRANGE)
Key → append-only log  →  Stream (XADD/XREAD)
Key → boolean flags    →  Bitmap (SETBIT/BITCOUNT)
Key → approximate count→  HyperLogLog (PFADD/PFCOUNT)
```

| Tradeoff | Detail |
|:---|:---|
| **More structures = more cognitive load** | Teams must learn 10+ command sets; but the payoff is orders-of-magnitude memory savings and O(1) operations that would be O(N) with naive String workarounds |
| **Wrong structure is silently expensive** | Using a List where a Stream is needed means no consumer groups, no replay; using Strings where Hashes belong means N× per-key metadata overhead |
| **Module dependency lock-in** | RedisBloom and RedisTimeSeries require module installation — not available on managed Redis tiers below Enterprise |

> **Dictionary**: [Redis Strings](../../reference-dictionary/caching.md#redis-strings) · [Redis Hashes](../../reference-dictionary/caching.md#redis-hashes) · [Redis Sorted Sets](../../reference-dictionary/caching.md#redis-sorted-sets) · [Redis Streams](../messaging.md#redis-streams)
> **Also see**: [Redis Hash Encoding Optimization](redis-hash-encoding-optimization-takeaways.md) — Meesho's 90% cost reduction via Hash grouping

---

## cache-44: Leaderboards Need Sorted Sets, Not Lists

> **Source**: [§"5. Sorted Sets (ZSets)" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | A gaming platform stores player rankings in a List — every score update requires finding the player's position, removing them, and re-inserting at the correct rank (O(N)). At 100K+ players, leaderboard updates cascade into seconds of latency. |
| **Root cause** | Lists preserve insertion order but have no notion of score — ranking requires manual reordering on every update |

**Strategy**: Use **Sorted Sets (ZSets)** where each member has an associated score. Redis maintains the ordering automatically: `ZADD` is O(log N), `ZRANGE` retrieves ranks in O(log N + M), and `ZREVRANK` returns a member's rank in O(log N).

```
List (wrong):                         Sorted Set (right):
LPUSH leaderboard "player:42"         ZADD leaderboard 9500 "player:42"
  → player:42 is at position 0          → Redis orders by score automatically
  → score goes up? Find, remove,
    re-insert at new position (O(N))  ZINCRBY leaderboard 200 "player:42"
                                        → Now score=9700, rank updated in O(log N)

                                      ZREVRANGE leaderboard 0 9 WITHSCORES
                                        → Top 10 instantly, no manual sorting
```

**Real-world example**: **Zynga** uses Redis Sorted Sets for real-time leaderboards in games like Words With Friends — millions of players, sub-millisecond rank queries.

| Tradeoff | Detail |
|:---|:---|
| **Memory overhead vs List** | Sorted Sets use a skiplist + hash table internally — ~2× memory of a List for the same elements |
| **Tied scores** | Members with identical scores are ordered lexicographically — predictable but may surprise users expecting chronological tie-breaking |
| **Not for append-only logs** | If you only need insertion-order access, Lists are simpler and use less memory |

> **Dictionary**: [Redis Sorted Sets](../../reference-dictionary/caching.md#redis-sorted-sets) · [Redis Lists](../../reference-dictionary/caching.md#redis-lists)
> **Also see**: [Top-K](../../reference-dictionary/caching.md#top-k) — Probabilistic alternative for tracking top items with bounded memory

---

## cache-45: HyperLogLog for Unique Counting — 12 KB Instead of Gigabytes

> **Source**: [§"7. HyperLogLog" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | A news site wants to count unique daily visitors. With Sets, storing 10 million unique user IDs consumes ~800 MB. At 100 million daily uniques, the Set alone requires 8+ GB — and that's just one day's counter. |
| **Root cause** | Sets store every element explicitly; the memory cost scales linearly with cardinality |

**Strategy**: Use **HyperLogLog** — a probabilistic data structure that estimates cardinality using ~12 KB of fixed memory regardless of how many elements are added. The tradeoff: ~0.81% standard error. For most analytics dashboards, "approximately 9.97 million" is indistinguishable from "exactly 10 million" and costs 70,000× less memory.

```
Set (exact, expensive):               HyperLogLog (approximate, cheap):
SADD daily:visitors "user:1"          PFADD daily:visitors "user:1"
SADD daily:visitors "user:2"          PFADD daily:visitors "user:2"
...                                    ...
SCARD daily:visitors                   PFCOUNT daily:visitors
  → 10,000,000 (exact)                  → ~9,920,000 (0.81% error)
  → Memory: ~800 MB                     → Memory: 12 KB (fixed)
```

**Real-world example**: **Reddit** uses HyperLogLog for counting unique post viewers and subreddit visitors — at their scale (hundreds of millions of daily uniques), exact counting with Sets would consume terabytes of RAM.

| Tradeoff | Detail |
|:---|:---|
| **~0.81% standard error** | Acceptable for dashboards and trend analysis; unacceptable for billing, quota enforcement, or audit trails |
| **Cannot enumerate members** | PFCOUNT returns a number — you cannot ask "which users visited?" Use a Set if you need the actual member list |
| **PFMERGE for cross-window dedup** | Merge daily HLLs into weekly/monthly counters with automatic deduplication — impossible with naive SUM of daily counters |

> **Dictionary**: [HyperLogLog](../databases.md#hyperloglog) · [Redis Sets](../../reference-dictionary/caching.md#redis-sets)
> **Also see**: [Redis Internals](redis-internals.md) — cache-12 through cache-15 cover HLL internals (Morris counter, harmonic mean, PFMERGE, funnel analytics)

---

## cache-46: Streams for Reliable Message Queues — Not Lists

> **Source**: [§"8. Streams" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | A payment processing pipeline uses Redis Lists as a message queue. When a consumer crashes after popping a message (RPOP), that message is **lost forever** — there's no acknowledgment and no replay. When you add a second consumer for scaling, both consumers compete for the same messages with no way to partition the workload. |
| **Root cause** | Lists are a basic FIFO — they have no concept of consumer groups, message ownership, pending entries, or acknowledgment |

**Strategy**: Use **Redis Streams** for message queuing. Streams support consumer groups (multiple consumers reading in parallel without duplicates), message acknowledgment (XACK), pending entry inspection (XPENDING), and replay by ID range (XRANGE). Each message gets a unique, monotonically increasing ID.

```
List (lossy, no fan-out):             Stream (reliable, consumer groups):
RPUSH payments '{"txn":"abc"}'        XADD payments * txn "abc"
RPOP payments                           → "1690000000000-0"
  → Consumer A gets message           XREADGROUP GROUP processors consumer_a
  → Consumer A crashes                  BLOCK 5000 STREAMS payments >
  → Message is GONE                      → Consumer A gets message
                                         → Consumer A crashes
                                       XPENDING payments processors
                                         → Message "1690000000000-0" is PENDING
                                         → Consumer B claims and retries
                                       XACK payments processors "1690000000000-0"
                                         → Message acknowledged, removed from PEL
```

**Real-world example**: **Airbnb** migrated from Redis Lists to Redis Streams for their search indexing pipeline — consumer groups allowed multiple index builders to process property updates in parallel, and XACK eliminated the "lost update on crash" problem that Lists suffered from.

| Tradeoff | Detail |
|:---|:---|
| **More complex than Lists** | Streams require consumer group setup, acknowledgment logic, and pending-entry monitoring — overkill for a simple work queue with no durability requirements |
| **Not a full message broker** | Streams lack routing, dead-letter queues, and replay-to-timestamp that Kafka/RabbitMQ provide natively |
| **Memory-only (unless persisted)** | Without RDB/AOF, stream entries are lost on restart — pair with persistence for production |

> **Dictionary**: [Redis Streams](../messaging.md#redis-streams) · [Redis Lists](../../reference-dictionary/caching.md#redis-lists)
> **Also see**: [Kafka Consumer Mistakes](messaging/kafka-consumer-mistakes.md) — Offset commit patterns, rebalancing

---

## cache-47: Bloom Filters for Membership at 1/1000th the Memory

> **Source**: [§"11.1 Bloom Filters" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | A URL shortener needs to check if a generated short code already exists before assigning it. With 10 billion URLs, storing all short codes in a Set consumes ~800 GB. Checking existence with a database query adds 10 ms latency — unacceptable at 100K requests/second. |
| **Root cause** | Sets store every element exactly; the memory cost makes them impractical for large-scale membership testing |

**Strategy**: Use a **Bloom Filter** (via RedisBloom module) — a probabilistic structure that answers "might this item be in the set?" with configurable false-positive rate. A Bloom Filter for 10 billion items at 0.1% false-positive rate uses ~17 GB — 47× less than a Set. Crucially, Bloom Filters have **zero false negatives**: if it says "not present," the item is guaranteed absent.

```
Set (exact, 800 GB):                  Bloom Filter (probabilistic, 17 GB):
SADD urls "abc123"                    BF.ADD urls "abc123"
SISMEMBER urls "abc123"               BF.EXISTS urls "abc123"
  → 1 (definitely present)              → 1 (probably present, ~0.1% error)
SISMEMBER urls "new456"               BF.EXISTS urls "new456"
  → 0 (definitely absent)               → 0 (definitely absent — no false negatives!)
```

**Real-world example**: **Medium** uses Bloom Filters to check if a URL has already been recommended to a user — at their scale of hundreds of millions of users × thousands of articles, storing every (user, article) pair would require petabytes. The Bloom Filter false-positive rate means ~0.1% of users might not see an article they've never seen — an acceptable UX tradeoff.

| Tradeoff | Detail |
|:---|:---|
| **Cannot delete items** | Standard Bloom Filters are add-only; to remove items, use Cuckoo Filters (CF.DEL) instead |
| **Cannot enumerate members** | BF.EXISTS answers "is X present?" but you cannot ask "what items are in the filter?" |
| **Module dependency** | RedisBloom must be installed — not available on basic/standard managed Redis tiers |

> **Dictionary**: [Bloom Filters](../databases.md#bloom-filter) · [Cuckoo Filters](../../reference-dictionary/caching.md#cuckoo-filters) · [Redis Sets](../../reference-dictionary/caching.md#redis-sets)
> **Also see**: [URL Shortener Viral Hotkey + CDN Caching](url-shortener-viral-hotkey-cdn-takeaways.md) — cache-31 covers CDN caching for URL redirects

---

## cache-48: Hashes Over Strings for Object Storage

> **Source**: [§"3. Hashes" and §"Use Cases"](../../articles/caching/redis-data-structures.md)

| | |
|:---|:---|
| **Problem** | A social media app stores user profiles as JSON strings: `SET user:1001 '{"name":"Ada","age":29,"city":"London","plan":"pro"}'`. Updating just the `plan` field requires: GET → parse JSON → modify → serialize → SET. This is 5 steps, non-atomic, and two users updating different fields can overwrite each other. |
| **Root cause** | Strings treat the entire value as an opaque blob — no field-level access, no atomic partial updates |

**Strategy**: Use **Redis Hashes** where each profile field is a separate hash field. `HSET user:1001 plan "enterprise"` is a single atomic operation. `HINCRBY user:1001 login_count 1` atomically increments a counter without touching other fields. Small hashes also benefit from compact encoding (ziplist/listpack) — less memory than an equivalent JSON String.

```
String (opaque, non-atomic):          Hash (field-level, atomic):
SET user:1001 '{"name":"Ada",         HSET user:1001 name "Ada" age 29
  "age":29,"plan":"pro"}'               city "London" plan "pro"

# Update plan: 5 steps, race-prone     # Update plan: 1 step, atomic
GET user:1001                          HSET user:1001 plan "enterprise"
  → parse JSON, modify plan
  → serialize, SET user:1001          # Increment counter: 1 step
                                        HINCRBY user:1001 login_count 1
# GC pressure from temp strings
# Read-modify-write race condition     # No race: HSET/HINCRBY are atomic
```

**Real-world example**: **Uber** stores driver profiles as Redis Hashes — location, status, rating, vehicle info are separate fields. Dispatch services read only the fields they need (HGET for location, HGET for status) instead of deserializing a 5 KB JSON blob for every matching query.

| Tradeoff | Detail |
|:---|:---|
| **TTL applies to entire hash** | You cannot expire individual fields — if some fields need short TTLs, split them into separate hashes grouped by TTL policy |
| **HGETALL on large hashes is O(N)** | Retrieving all fields becomes expensive above ~500 fields — use HSCAN for iteration or split into multiple hashes |
| **No nested objects** | Hashes are flat field→value; for hierarchical data, use RedisJSON module or serialize nested parts as JSON within hash fields |

> **Dictionary**: [Redis Hashes](../../reference-dictionary/caching.md#redis-hashes) · [Redis Strings](../../reference-dictionary/caching.md#redis-strings) · [ziplist](../../reference-dictionary/caching.md#ziplist)
> **Also see**: [Redis Hash Encoding Optimization](redis-hash-encoding-optimization-takeaways.md) — Meesho's 90% cost reduction via Hash grouping and encoding threshold tuning

---

## Cross-References

- **Dictionary**: [Caching](../../reference-dictionary/caching.md) — All 10 Redis data structure entries
- **Azure**: [Azure Cache for Redis](../../architecture-azure/data/) — Managed Redis supporting core data structures; RedisBloom and RedisTimeSeries available on Enterprise tier
- **Related**: [Redis Internals](redis-internals.md) · [Redis Hash Encoding Optimization](redis-hash-encoding-optimization-takeaways.md) · [Redis Rate Limiting Patterns](redis-rate-limiting-patterns.md)
- **Taxonomy**: §7.3 Caching Strategies
