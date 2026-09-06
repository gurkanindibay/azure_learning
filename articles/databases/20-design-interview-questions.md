---
type: Article
title: "I Will Never Walk Into a Backend Interview Without Solving These 20 Questions"
description: "A practical baseline checklist of the specific technical concepts you need to understand before sitting across from a senior engineer."
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# I Will Never Walk Into a Backend Interview Without Solving These 20 Questions

> **Author**: Emily · **Published**: May 5, 2026 · **Read time**: 7 min

A practical baseline checklist of the specific technical concepts you need to understand before sitting across from a senior engineer.

Interviewers are not trying to trick you with unnecessary puzzles. They are checking to see if you have encountered the standard ways that production backend systems break. After failing enough interviews and then eventually moving to the other side of the table to conduct them, I realized that the same twenty core concepts come up constantly. If you can confidently explain the mechanisms, edge cases, and tradeoffs for these twenty questions, you have the foundation to pass a mid-level backend loop. If you cannot answer them, you are hoping the interviewer gives you easy questions instead of actually being prepared.

---

## Table of Contents

1. [Why These Specific Questions Matter](#why-these-specific-questions-matter)
2. [Databases and Query Performance](#databases-and-query-performance)
3. [Concurrency and Transactions](#concurrency-and-transactions)
4. [Caching Strategy](#caching-strategy)
5. [APIs and Network Architecture](#apis-and-network-architecture)
6. [Message Brokers and Asynchronous Processing](#message-brokers-and-asynchronous-processing)
7. [Final Thoughts](#final-thoughts)

---

## Why These Specific Questions Matter

Most people study for backend interviews by reading system design books and trying to memorize architectures. They learn to draw boxes labeled **Database** and **Cache**.

That approach gets you through the initial screening. It falls apart as soon as the interviewer asks a follow-up question about what happens inside those boxes when traffic spikes.

I compiled this list based on the questions that actually get asked in real rooms. I failed many interviews because I did not know the answers to these. I ask them now because they are excellent filters. They separate the people who only know the vocabulary from the people who know how the systems behave under pressure.

> **Key takeaway**: You do not need to memorize textbook answers for these. You need to understand the underlying mechanics well enough to discuss them conversationally.

---

## Databases and Query Performance

Databases are where most applications spend most of their time. You need to know how to get data in and out efficiently when the tables get large.

### 1. What happens when you put an index on a random UUID column?

A lot of developers use UUIDs for primary keys because it makes distributed generation easy — no coordination needed between servers. But standard UUIDv4 values are **cryptographically random**.

**The problem**: Most relational databases use **B-tree indexes** for primary keys. A B-tree is a balanced tree structure where data is stored in sorted order on disk pages (typically 8 KB each). When you insert a new row with a sequential key (like an auto-incrementing integer), the database simply appends it to the rightmost leaf page. When that page fills up, it splits — but the new page is also at the end, so fragmentation is minimal.

With random UUIDs, every insert lands at a **random position** in the tree. This causes:

1. **Page splits everywhere** — The target page is often already full, forcing the database to split it and rewrite both halves. These new pages are scattered across disk.
2. **Buffer pool thrashing** — The working set no longer fits in memory because you are touching pages across the entire index, not just the "hot" rightmost pages.
3. **Write amplification** — Each insert may dirty multiple pages, increasing disk I/O and WAL (Write-Ahead Log) volume.
4. **Index fragmentation** — Over time, pages become partially filled (typically ~50-75%), wasting disk space and making range scans slower.

**How bad is it?** Benchmarks show random UUID inserts can be **2-5x slower** than sequential inserts and consume significantly more disk I/O, especially once the index exceeds available RAM.

**Solutions**:

| Approach | Example | How it helps |
|:---|:---|:---|
| **Time-sorted UUIDs** | UUIDv7, ULID | First 48 bits are a timestamp — inserts are roughly sequential |
| **Sequential IDs** | `BIGSERIAL`, `AUTO_INCREMENT` | Perfectly sequential, minimal fragmentation |
| **Clustered on different key** | Cluster on `(tenant_id, created_at)` | UUID is still the PK but physical ordering follows a business key |
| **Fill factor tuning** | `FILLFACTOR=80` on PostgreSQL | Leaves 20% free space per page to absorb random inserts |

> **Interview tip**: Mention UUIDv7 (RFC 9562) — it is the modern standard that solves this exact problem by encoding a Unix timestamp in the first 48 bits.

### 2. How do you paginate through 50 million rows without using `OFFSET`?

Using `OFFSET` and `LIMIT` works fine for the first few pages. The problem is that the database **must still scan all the rows it skips**.

**Why `OFFSET` is slow**: When you run `SELECT * FROM users ORDER BY id LIMIT 20 OFFSET 1000000`, the database:

1. Executes the full query (scans 1,000,020 rows from the index)
2. Reads all 1,000,020 rows from disk if they are not in the buffer pool
3. Discards the first 1,000,000 rows from the result set
4. Returns the remaining 20 rows

You paid to read 1,000,020 rows just to return 20. The deeper the page, the more rows you scan and throw away — query time grows **linearly** with offset.

**The solution — Keyset Pagination (Cursor-Based Pagination)**:

Instead of saying "skip N rows," you say "give me rows after the last one I saw." The client remembers the last value of the sorted column:

```sql
-- Page 1
SELECT * FROM users ORDER BY id LIMIT 21;
-- Last id seen: 1042

-- Page 2 (instead of OFFSET 20)
SELECT * FROM users ORDER BY id WHERE id > 1042 LIMIT 21;
```

Why `LIMIT 21` when the page size is 20? You fetch one extra row to know if there is a next page — no `COUNT(*)` needed.

**Tradeoffs**:

| Aspect | OFFSET/LIMIT | Keyset Pagination |
|:---|:---|:---|
| **Performance** | Degrades linearly with offset | Constant time regardless of depth |
| **Jump to page N** | Easy (`OFFSET N*20`) | Not possible (must traverse sequentially) |
| **Sort stability** | Tolerates inserts/deletes | New rows can shift the cursor position |
| **Implementation** | Trivial | Requires indexed, unique, sortable column |
| **UX fit** | "Go to page 50" | Infinite scroll / "Load more" |

**The catch**: Keyset pagination requires a **deterministic, unique ordering column** (e.g., `id`, `created_at` with a tiebreaker). If you sort by `last_name` alone and there are 50 "Smiths," you cannot reliably page through them without also ordering by `id` as a tiebreaker.

> **Interview tip**: Mention that GraphQL's Relay Cursor Connections specification and most social media feeds (Twitter, LinkedIn) use cursor-based pagination. Also note that if you truly need "page 50 of 500," you can combine keyset with a `COUNT` estimate — but that is rarely a real user need.

### 3. When would you use a composite index instead of two separate indexes?

If you frequently query a table using two columns together, creating an index on column `A` and a separate index on column `B` is usually the wrong move. The database typically only uses **one index per table scan** (via bitmap index scans, possibly two, but that is less common and less efficient).

**How a composite index works**: Think of a composite index on `(A, B)` like a **phone book sorted by last name, then first name**:

```
Index on (last_name, first_name):
  Smith, Adam    → page 42
  Smith, Bob     → page 42
  Smith, Carol   → page 43
  Taylor, Alice  → page 44
  Taylor, Zoe    → page 45
```

The index stores entries sorted by `A` first, and within matching `A` values, sorted by `B`. All entries with the same `A` value are **contiguous on disk**.

**The Leftmost Prefix Rule**: A composite index on `(A, B)` can efficiently serve:

| Query | Uses index? | Why |
|:---|:---:|:---|
| `WHERE A = ? AND B = ?` | ✅ Full | Both columns matched |
| `WHERE A = ?` | ✅ Partial | Matches the leftmost prefix |
| `WHERE A = ? ORDER BY B` | ✅ Full | Filter on `A`, sort on `B` — no filesort needed |
| `WHERE B = ?` | ❌ No | Skips the leftmost column — cannot use the index |
| `WHERE A = ? AND B > ?` | ✅ Partial | Range scan on `B` within matching `A` values |

**Column order matters**: `(A, B)` and `(B, A)` are different indexes. Choose based on your query patterns:

- If you query by `(user_id, created_at)` → index `(user_id, created_at)` lets you filter by user and sort by date
- If you also query by `created_at` alone → you would need a separate index on `(created_at)`
- If you query by `(user_id, status)` and `(user_id)` alone → a single composite `(user_id, status)` covers both

**Why not just create many single-column indexes?** Each additional index:

- **Slows down writes** — every `INSERT`/`UPDATE`/`DELETE` must update all indexes
- **Consumes disk** — indexes can be larger than the table itself
- **Confuses the planner** — the query optimizer may pick a suboptimal index

> **Interview tip**: Use `EXPLAIN` (PostgreSQL) or `EXPLAIN PLAN` (Oracle) to verify which index the planner actually uses. Mention covering indexes — if all columns in your `SELECT` are in the composite index, the database can answer the query from the index alone (an "index-only scan"), never touching the table.

### 4. What is the N+1 query problem and how do you fix it?

This is the most common performance bug in modern applications that use ORMs. It happens when your code executes **one query to fetch a list, then N additional queries — one for each item in that list**.

**Concrete example**: Imagine a blog where you want to display 20 posts along with each post's author name:

```
1. SELECT * FROM posts LIMIT 20;                    -- 1 query
2. SELECT * FROM users WHERE id = 7;                -- query for post 1's author
3. SELECT * FROM users WHERE id = 12;               -- query for post 2's author
4. SELECT * FROM users WHERE id = 7;                -- query for post 3's author (same author!)
   ... 17 more queries ...
```

That is **21 queries** (1 + 20) when 2 would have sufficed. If you have 100 posts on the page, you get 101 queries. If the author is the same across multiple posts, you still re-fetch them — no caching.

**Why it happens**: ORMs use **lazy loading** by default. When you access `post.author.name`, the ORM checks if the author is already loaded. If not, it issues a separate query. This is convenient during development but catastrophic at scale because:

- **Network round-trips**: Each query is a separate TCP round-trip to the database (0.5–5ms each in the same datacenter, 50–200ms across regions).
- **Connection pool exhaustion**: Each query consumes a database connection. With 100 concurrent requests each firing 101 queries, you need 10,100 connections.
- **Database CPU waste**: The database parses, plans, and executes virtually identical queries repeatedly.

**The impact at scale**: A page that should load in 10ms with a single JOIN takes 500ms+ with N+1. Under load, this cascades into timeouts, connection pool saturation, and cascading failures.

**Solutions**:

| Approach | How it works | Best for |
|:---|:---|:---|
| **Eager Loading** | `Post.includes(:author)` in ActiveRecord / `Post.objects.select_related('author')` in Django — tells the ORM to fetch related data in the same query via JOIN | Simple one-level associations |
| **Batch Loading** | Collect all foreign keys from the parent list, then `SELECT * FROM users WHERE id IN (7, 12, 15, ...)` — one query fetches all authors | When you need fine-grained control |
| **JOINs** | Write a raw `SELECT posts.*, users.name FROM posts JOIN users ON posts.author_id = users.id` | Complex queries where ORM abstraction hurts more than helps |
| **DataLoader Pattern** | A per-request cache that deduplicates and batches database calls (popularized by Facebook's DataLoader for GraphQL) | GraphQL APIs, microservices with many downstream calls |
| **GraphQL `@defer` / DataLoader** | GraphQL resolvers naturally create N+1; DataLoader batches them within a single tick of the event loop | GraphQL backends |

**In practice**: Most ORMs make eager loading a one-liner:

```ruby
# ❌ N+1 — lazy loading
posts = Post.limit(20)
posts.each { |p| puts p.author.name }

# ✅ Eager loading — single JOIN
posts = Post.includes(:author).limit(20)
posts.each { |p| puts p.author.name }
```

**How to detect it in production**:

- **Development**: Rails' `bullet` gem, Django's `nplusone`, Laravel's `barryvdh/laravel-debugbar` log N+1 warnings
- **APM tools**: Datadog, New Relic, and Sentry flag query spikes and repeated similar queries
- **Database logs**: If you see hundreds of identical-looking queries with different IDs in a single request trace, you have N+1
- **Slow query log**: Set `log_min_duration_statement` in PostgreSQL to catch queries taking longer than expected

> **Interview tip**: Don't just say "use eager loading." Explain that the root cause is lazy loading being the ORM default, and that the fix needs to happen at the **data-access layer** — not by sprinkling caching on top. Also mention that over-eager-loading (loading associations you don't need) wastes memory and bandwidth, so you should only load what the view actually renders.

---

## Concurrency and Transactions

Distributed systems do things at the same time. Bad things happen when you do not manage that timing.

### 5. How do you prevent double-booking a ticket in a distributed system?

Checking if a seat is available and then booking it creates a **race condition**. You cannot solve this with a mutex in your application code if you are running multiple servers. You need to know how to use database-level locks, like a `SELECT ... FOR UPDATE` statement, or an **optimistic locking** strategy with version numbers.

### 6. What is the difference between repeatable read and serializable isolation levels?

You do not need a PhD in database theory. But you do need to know that the default isolation level in Postgres allows certain types of race conditions, and you need to know when you have to crank the isolation level up to **serializable** to guarantee absolute correctness.

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|:---|:---:|:---:|:---:|
| Read Uncommitted | ✅ | ✅ | ✅ |
| Read Committed | ❌ | ❌ | ✅ |
| Repeatable Read | ❌ | ❌ | ✅ |
| Serializable | ❌ | ❌ | ❌ |

### 7. How do you implement a distributed lock without creating a single point of failure?

If multiple workers need exclusive access to a shared resource (e.g., only one worker should process a given file, or only one scheduler should trigger a daily report), they need a **distributed lock**. A simple `SETNX` on a single Redis instance works — until that Redis instance goes down. Then every worker is locked out, or worse, the lock is lost and two workers act simultaneously.

The challenge is building a lock that survives individual node failures while maintaining **safety** (only one holder at a time) and **liveness** (someone eventually acquires it).

---

#### Approach 1: Redlock (Redis-based)

The **Redlock algorithm** (proposed by Redis's creator) uses **N independent Redis instances** (typically 5) with no replication between them. To acquire a lock:

1. Generate a **random token** (a unique value to identify this lock holder)
2. Try to `SET lock_name {token} NX PX {ttl}` on **all N instances** in sequence, with a short timeout per attempt
3. If you succeed on a **majority** (at least N/2 + 1, e.g., 3 out of 5) within the total time budget, you hold the lock
4. The **effective lock duration** = TTL − time spent acquiring
5. To release, send `DEL lock_name` to all instances, but only if the value still matches your token (Lua script to make it atomic)

```
Client tries SET NX PX on 5 independent Redis nodes:

  Redis-1: ✅  Redis-2: ✅  Redis-3: ✅  Redis-4: ❌  Redis-5: ✅
                ↑ Majority (4/5): lock acquired
```

**Why this works**: If a minority of Redis instances fail, the quorum still exists. The random token prevents a client from releasing another client's lock.

**Redlock controversy**: Martin Kleppmann (author of *Designing Data-Intensive Applications*) famously argued that Redlock is **unsafe** in certain scenarios — specifically, if a client is paused (GC pause, network delay) longer than the lock TTL, another client can acquire the lock and both operate simultaneously. The counter-argument is that **fencing tokens** solve this (see below).

---

#### Approach 2: ZooKeeper / etcd (Consensus-based)

Systems like **ZooKeeper** and **etcd** use consensus (ZAB / Raft) to maintain a consistent, ordered log. Locking patterns:

**Ephemeral Sequential ZNodes** (ZooKeeper):

1. Every contender creates an **ephemeral, sequential** node under a lock path: `/lock/request-0000000001`, `/lock/request-0000000002`, etc.
2. The client with the **lowest sequence number** holds the lock
3. All other clients set a **watch** on the node just before theirs
4. When the lock holder disconnects or crashes, its ephemeral node is automatically deleted, and the next client in line is notified

```
/lock/request-0000000001  ← Lock holder (ephemeral)
/lock/request-0000000002  ← Watching 0000000001
/lock/request-0000000003  ← Watching 0000000002
```

**Why this is safer**: The lock is tied to a **session**. If the client's TCP connection drops or its heartbeat times out, the session expires and ZooKeeper automatically deletes the ephemeral node. No TTL guessing. No clock drift concerns.

---

#### Comparison

| Aspect | Redlock (Redis) | ZooKeeper / etcd |
|:---|:---|:---|
| **Consistency model** | Best-effort (no consensus) | Strong (Raft/ZAB consensus) |
| **Failure tolerance** | Tolerates minority Redis failures | Tolerates minority node failures |
| **Lock release** | TTL-based (time-bounded) | Session-based (heartbeat) |
| **Complexity** | Moderate (client-side quorum) | Higher (running a ZK/etcd cluster) |
| **Performance** | Lower latency (~1ms) | Higher latency (~5-10ms per operation) |
| **Clock sensitivity** | Yes (TTL depends on clock sync) | No (session heartbeats, not wall clock) |
| **Best for** | High-throughput, short-lived locks | Correctness-critical, longer-lived locks |

---

#### The Fencing Token — the detail most people miss

A distributed lock alone is **not enough** for safety. Consider this scenario:

1. Client A acquires the lock (TTL: 30s)
2. Client A encounters a **long GC pause** (45 seconds)
3. The lock expires on Redis/ZK
4. Client B acquires the lock
5. Client A **resumes** — still thinks it holds the lock
6. Both A and B now write to the shared resource → **corruption**

The fix: every lock acquisition returns a **monotonically increasing fencing token**. The shared resource (e.g., the database or storage system) checks the token on every write and rejects any write with a token lower than the highest it has seen:

```
Client A acquires lock → token 17
Client A is paused (GC) → lock expires
Client B acquires lock → token 18
Client A resumes → tries to write with token 17 → REJECTED (18 > 17)
```

This pushes the safety check to the resource level, where even a "confused" client cannot cause damage.

> **Interview tip**: If you mention Redlock, acknowledge the Kleppmann critique. If the interviewer pushes on safety, bring up fencing tokens — it shows you understand the difference between locking (mutual exclusion) and protecting the resource (write validation). Also mention that in practice, many teams use a simple single-Redis lock with short TTLs for non-critical use cases (cache refresh coordination, job deduplication) because the operational simplicity is worth the risk.

### 8. How do you implement idempotency for a payment retry endpoint?

Mobile networks drop connections. Clients will retry requests. If a client retries a payment request because they did not receive the success response, you cannot charge their card twice. You need to explain how to use **idempotency keys** and where to store them to guarantee **exactly-once processing**.

---

## Caching Strategy

Everyone knows caching makes things faster. Interviewers want to know if you understand how caching makes things break.

### 9. What causes a cache stampede and how do you prevent it?

A **cache stampede** (also called "thundering herd" or "dog-piling") happens when a heavily requested cache key expires, and **all concurrent requests** discover the cache miss at the same time. They all rush to the database to regenerate the value, overwhelming it.

**The scenario**: Imagine a popular product page cached for 5 minutes. At second 301, the cache TTL expires. 200 concurrent users request the product. All 200 requests:
1. Check cache → miss
2. Hit the database with the same expensive query
3. 200 database connections consumed, CPU spikes to 100%, latencies skyrocket
4. Database becomes unresponsive → cascading failures to other services

This is especially dangerous because it's a **positive feedback loop**: as the DB slows down, requests pile up, more connections open, making the DB even slower.

**Prevention strategies**:

#### 1. Probabilistic Early Expiration (PER / "XFetch")

Instead of expiring at a fixed TTL, each read computes a probability of early refresh. The closer to expiry, the higher the probability. In Redis pseudocode:

```python
def should_refresh(ttl_ms, delta=1000, beta=1.0):
    if ttl_ms < 0:
        return True  # already expired
    # As time-to-live shrinks, probability of refresh increases
    return random.random() < delta / (beta * ttl_ms + delta)
```

When the computed probability triggers, **only that one request** recomputes the value while others continue using the stale (but still valid) cached data. This spreads out the refresh load stochastically.

#### 2. Lock-on-Miss (Mutex on Cache Miss)

When a cache miss occurs, only **one request** is allowed to regenerate the value. All other concurrent requests wait for it:

```
Request 1: cache MISS → acquire lock "lock:product:42" → query DB → populate cache → release lock
Request 2: cache MISS → try lock "lock:product:42" → blocked → retry cache → HIT (populated by R1)
Request 3: cache MISS → try lock → blocked → retry → HIT
...
Request 200: same as above → HIT
```

The database only receives **one query** instead of 200. Implementation: `SET lock:product:42 client1 NX EX 5` in Redis.

**Caveat**: If request 1 crashes, the lock must have a TTL so it auto-releases. Also, this adds latency for waiting requests — they block until the value is populated.

#### 3. External Refresh / "Cache Warming"

A background job refreshes the cache **before** it expires, ensuring there's never a gap:
- Cron job runs every 4 minutes to refresh the 5-minute cache
- The cache never truly expires under normal operation
- Downside: increased complexity, and you're computing values that may never be requested

#### 4. Redis `GETEX` (Atomic Get + Expire)

Redis 6.2+ supports `GETEX` which atomically returns a value and updates its TTL. For read-heavy keys, you can extend the TTL on every access so popular keys never expire during traffic:

```
GETEX product:42 EX 300  -- returns value AND resets TTL to 300s
```

**Which to choose?**:

| Strategy | Complexity | Staleness Risk | DB Protection | Best For |
|:---|:---:|:---:|:---:|:---|
| PER (probabilistic) | Low | Low | Good (stochastic) | Most cases |
| Lock-on-miss | Low | None during lock | Excellent | Expensive queries |
| External refresh | High | None | Excellent | Predictably hot keys |
| GETEX sliding TTL | Minimal | None | Good (no expiry) | Perennially hot keys |

> **Interview tip**: Ask whether the data can tolerate brief staleness. If yes → PER is often the simplest. If no → lock-on-miss. If you're already on Redis 6.2+, mention `GETEX`. Also connect this to the broader concept: cache stampedes are a special case of **thundering herd**, which also applies to process scheduling, connection pools, and distributed systems in general.

### 10. If you cache a user profile, how do you invalidate it when they update their email?

Cache invalidation is famously one of the **two hard problems in computer science** (along with naming things and off-by-one errors). The core tension: you want cached data to be **fresh**, but you also want to **avoid database load**. Every invalidation strategy is a tradeoff between these two goals.

**The four cache write patterns**:

#### 1. Cache-Aside (Lazy Loading) — Most Common

The application manages the cache explicitly. On reads, check cache first; on writes, update the database and delete the cache entry.

```
READ:  app → cache (miss) → DB → populate cache → return
WRITE: app → DB (UPDATE users SET email=?) → app → cache (DEL user:42)
```

- ✅ Simple, cache only contains what's actually read
- ❌ First read after write is always a cache miss (cold start per key)
- ❌ Race condition: if read and delete happen in wrong order, stale data can re-enter the cache

#### 2. Write-Through

The cache sits between the app and the database. Every write goes to the cache first, then synchronously to the database.

```
WRITE: app → cache (SET user:42) → DB (UPDATE users...)
READ:  app → cache (always fresh)
```

- ✅ Cache is always consistent with DB
- ❌ Every write touches the cache, even for data nobody reads
- ❌ Higher write latency (two synchronous writes)

#### 3. Write-Behind (Write-Back)

Writes go to the cache first and are **asynchronously** flushed to the database.

```
WRITE: app → cache (SET user:42) → return (fast!)
       cache → DB (async flush, batched)
```

- ✅ Lowest write latency
- ❌ Risk of data loss if cache crashes before flush
- ❌ Hard to implement correctly (needs a persistent cache like Redis with AOF)

#### 4. Refresh-Ahead

The cache proactively refreshes entries before they expire, based on access patterns. If a key is frequently accessed and close to expiry, the cache asynchronously reloads it.

- ✅ Near-zero cache miss latency for hot data
- ❌ Complex to tune; may preload data nobody ultimately requests

**TTL vs explicit invalidation — the tradeoff**:

| Strategy | Freshness | Complexity | DB Load |
|:---|:---|:---|:---|
| **Short TTL only** (e.g., 60s) | At most 60s stale | Minimal | Higher (frequent reloads) |
| **Explicit delete on write** | Immediate | Moderate (must catch all write paths) | Lower |
| **TTL + explicit delete** | Immediate, with safety net | Moderate | Lower (TTL catches missed deletes) |

**The recommended approach**: Use **cache-aside with explicit deletion on writes PLUS a fallback TTL**. The explicit delete handles the happy path; the TTL is a safety net for missed invalidation events, bugs, or operations done outside the application (DB migrations, admin panels).

#### Modern alternative: Change Data Capture (CDC)

Instead of the application managing invalidation, use the database's own change log:

1. **Debezium** (or similar CDC tool) tails the database WAL
2. When a `users` row changes, it emits an event to Kafka
3. A cache-invalidation consumer listens and deletes/updates the relevant cache key

This decouples cache invalidation from application code entirely — the cache stays in sync regardless of which service or tool modified the database.

> **Interview tip**: Quote Phil Karlton: *"There are only two hard things in Computer Science: cache invalidation and naming things."* Then explain that the pragmatic answer is usually cache-aside + explicit delete + TTL safety net. Mention CDC if the interviewer seems interested in scale — it's the approach used by large-scale systems where multiple services write to the same database.

### 11. Why might putting Redis in front of your database actually slow your system down?

Adding a cache seems like a guaranteed win, but it introduces a **network hop** and a **new failure mode**. If your cache hit rate is poor, you are paying the cost of the cache check on every request while still hitting the database.

**The math**: A Redis lookup costs ~0.5–2ms (network + command processing) in the same datacenter. A database query for a simple indexed lookup costs ~1–5ms. So:

| Scenario | Cache Hit Rate | Latency | Net Effect |
|:---|:---:|:---|:---|
| No cache | N/A | DB: 3ms | Baseline: 3ms |
| Cache, 90% hit | 90% | Cache: 1ms (90%) or Cache+DB: 4ms (10%) | **Avg: 1.3ms** ✅ |
| Cache, 50% hit | 50% | Cache: 1ms (50%) or Cache+DB: 4ms (50%) | **Avg: 2.5ms** ⚠️ marginal |
| Cache, 10% hit | 10% | Cache: 1ms (10%) or Cache+DB: 4ms (90%) | **Avg: 3.7ms** ❌ slower! |

At a 10% hit rate, you are adding 1ms to 90% of requests for the privilege of checking an empty cache, then still hitting the database. You've made the system **slower and more complex**.

**When caching hurts more than it helps**:

1. **Low hit rate** — If your access pattern is uniformly distributed (every key is equally likely), caching provides no benefit. The cache just becomes a slower, smaller copy of your database.
2. **Highly volatile data** — If data changes faster than your TTL, you are serving stale data to most users and still hitting the database for writes plus cache updates.
3. **Cache as a SPOF** — If Redis goes down and your application cannot gracefully degrade to the database, you've added a dependency that **reduces** overall availability. Your system is now only as available as Redis × the database.
4. **Serialization overhead** — Complex objects take CPU to serialize/deserialize. For large payloads, the serialization cost may exceed the database query cost.
5. **Operational complexity** — You now have to monitor, scale, patch, and alarm on Redis. That's a non-trivial operational burden for marginal gain.

**How to decide if caching is worth it**:

1. **Measure first** — Profile your database queries. Identify the top 5 slowest/most frequent queries. Only cache those.
2. **Calculate the break-even hit rate** — If `cache_latency + (1 - hit_rate) × db_latency < db_latency`, caching helps. Solve for your numbers.
3. **Monitor cache hit ratio** — Track `hits / (hits + misses)`. In Redis: `INFO stats` shows `keyspace_hits` and `keyspace_misses`. Alert if the ratio drops below your threshold.
4. **Design for cache failure** — Always have a fallback path. Use circuit breakers (e.g., Polly in .NET, resilience4j in Java) so a Redis outage doesn't cascade.

```python
# Anti-pattern: cache or die
value = redis.get(key)
if value:
    return value
return db.query(...)  # what if Redis is down? Connection refused → crash

# Resilient pattern: cache optionally
try:
    value = redis.get(key)
    if value:
        return value
except RedisError:
    metrics.increment("cache.error")  # log and proceed
return db.query(...)  # always works, with or without cache
```

> **Interview tip**: Use the phrase **"don't cache prematurely"** — just like premature optimization. Cache when you have evidence (query logs, APM data) that a specific query is a bottleneck. Also mention that sometimes the right answer is **database query optimization** (adding an index, materializing a view) rather than adding a cache layer.

### 12. What eviction policy makes sense for a session store versus a content feed?

Caches have finite memory. When they fill up, they must **evict** (delete) some entries to make room for new ones. The eviction policy determines **which** entries get removed — and choosing wrong can break your application in subtle ways.

**The core policies**:

| Policy | How it chooses | Algorithmic complexity |
|:---|:---|:---|
| **LRU** (Least Recently Used) | Evicts keys not accessed for the longest time | O(1) with doubly-linked list + hashmap |
| **LFU** (Least Frequently Used) | Evicts keys with the lowest access count | O(log N) with a min-heap (or O(1) with Redis's probabilistic LFU) |
| **FIFO** (First In, First Out) | Evicts the oldest-inserted key regardless of access | O(1) with a queue |
| **TTL-only** | Only evicts keys whose TTL has expired | O(1) per key, but requires scanning |
| **Random** | Evicts a random key | O(1) — surprisingly effective in practice |

#### Redis-specific policies

Redis splits eviction into two dimensions — **which keys** (all keys vs. only keys with TTL) and **how to choose**:

| Redis `maxmemory-policy` | Scope | Eviction Rule |
|:---|:---|:---|
| `noeviction` | — | Error on write when full (default) |
| `allkeys-lru` | All keys | Approximated LRU |
| `allkeys-lfu` | All keys | Approximated LFU (Redis 4.0+) |
| `volatile-lru` | Only keys with TTL | Approximated LRU |
| `volatile-lfu` | Only keys with TTL | Approximated LFU |
| `allkeys-random` | All keys | Random |
| `volatile-random` | Only keys with TTL | Random |
| `volatile-ttl` | Only keys with TTL | Shortest remaining TTL first |

Redis uses **approximate** LRU/LFU — it samples N keys (default 5) and evicts the best candidate from the sample. This is O(N) per eviction rather than maintaining perfect ordering, which is fast enough for practical use.

#### The session store vs. content feed distinction

**Session store** (e.g., `user:session:abc123`):

- Each session key is **tied to one user**. If a user's session is evicted, they are suddenly logged out — a **high-impact, confusing failure**.
- Sessions have a **natural TTL** (e.g., 2 hours of inactivity). You want to respect that TTL, not evict early based on access patterns.
- An active user might have long gaps between requests (reading a long article), so LRU could evict them even though they are still active.
- **Best policy**: `volatile-ttl` or `volatile-lru` with a safety margin. Let TTL govern eviction — sessions expire naturally. If you must evict under memory pressure, evict the session closest to its TTL anyway.

**Content feed** (e.g., `feed:user:42`, `trending:posts`):

- These are **shared, recomputable** values. Evicting them means one user gets a slightly slower request, not a broken experience.
- Access patterns are **highly skewed** (power-law distribution) — 5% of content gets 95% of reads. LFU or LRU naturally retains the hot content.
- **Best policy**: `allkeys-lru` or `allkeys-lfu`. Hot items stay; cold items get evicted. Nobody notices the difference.

**A concrete failure scenario**: A team uses `allkeys-lru` for their Redis session store. During a traffic spike, new sessions push old ones out of memory. A user who logged in 30 minutes ago refreshes the page and gets logged out because their session was evicted — despite being well within the 2-hour TTL. They log in again, creating a new session, further exacerbating memory pressure. The ops team sees a spike in login errors and cannot figure out why.

| Use Case | Recommended Policy | Why |
|:---|:---|:---|
| **User sessions** | `volatile-ttl` | Respect natural expiry; evict near-expiry keys first |
| **Content feeds / timelines** | `allkeys-lru` or `allkeys-lfu` | Hot content stays, cold content goes |
| **Rate limiting counters** | `volatile-ttl` | Each counter has a window TTL — evict expired ones |
| **API response cache** | `allkeys-lru` | Frequently hit endpoints stay cached |
| **Leaderboards** | `noeviction` | You need all data; scale memory instead |
| **Distributed locks** | `noeviction` | Never evict a lock — safety risk |

> **Interview tip**: Don't just name the policies — explain **why** the wrong policy causes a specific, real-world failure. The session-store-vs-content-feed distinction is a classic interview scenario. Also mention that `noeviction` with alerting is underrated: sometimes it's better to fail loudly (and get paged) than silently evict critical data.

---

## APIs and Network Architecture

Your API is a contract. You have to know how to change it safely and protect it from abuse.

### 13. How do you safely change the payload of a live API without breaking existing mobile clients?

Mobile apps live on user devices for years without being updated. If you change a response format and remove a field, old apps will crash. You need to understand **API versioning** via headers or URLs, and how to maintain **backward compatibility**.

### 14. What is the difference between a sliding window log and a fixed window counter for rate limiting?

A **fixed window counter** lets clients burst double their allowed limit right at the boundary between two minutes. A **sliding window** smooths out the limit. You should be able to explain the mechanics and the memory tradeoffs of both approaches.

### 15. How do you design an endpoint that needs to upload a 5 GB video file?

You cannot read a 5 GB file into memory on your application server — it will kill the process. You need to explain **streaming uploads**, **multipart chunking**, or using **presigned URLs** to let the client upload directly to cloud storage.

### 16. How do you handle long-running tasks in a synchronous API request?

If an endpoint triggers a PDF generation that takes forty seconds, the client connection will likely timeout. You need to explain the **asynchronous worker pattern**:

1. The API returns a **`202 Accepted`** with a job ID immediately
2. The client polls a separate endpoint to check the status
3. Optionally, use **webhooks** or **Server-Sent Events** to notify the client upon completion

---

## Message Brokers and Asynchronous Processing

Real systems decouple work. You need to know what happens when those decoupled pieces fail.

### 17. Why would you choose RabbitMQ over Kafka, or vice versa?

They are not interchangeable — each is built around a fundamentally different architecture and solves different problems.

#### The core difference

**Kafka** is a **distributed commit log**. Think of it as a durable, append-only file that multiple consumers can read independently. Producers write to the end of the log; consumers maintain their own read position (offset). Messages are retained for a configurable retention period (typically days to weeks) regardless of whether they've been consumed.

**RabbitMQ** is a **smart message broker**. Think of it as a post office. Producers send messages to exchanges, which route them to queues based on routing rules. Messages are pushed to (or pulled by) consumers, and once acknowledged, they are deleted. The broker tracks which consumer got which message.

#### Architectural comparison

| Dimension | RabbitMQ | Kafka |
|:---|:---|:---|
| **Core abstraction** | Queue (FIFO) | Log (append-only, partitioned) |
| **Message model** | Smart broker routes to consumers | Dumb broker; consumers track their own position |
| **Delivery** | Push-based (broker pushes to consumer) | Pull-based (consumer polls for new data) |
| **Throughput** | ~10K–50K messages/sec | ~1M+ messages/sec (per partition) |
| **Latency** | Very low (microseconds to low ms) | Low (milliseconds) |
| **Message retention** | Deleted after acknowledged consumption | Retained for configurable time (days/weeks) |
| **Replayability** | No — once consumed + acked, gone | Yes — reset offset and re-read the entire history |
| **Consumer model** | Competing consumers (round-robin from queue) | Consumer groups (each consumer reads its own partitions) |
| **Routing flexibility** | Complex: exchanges, bindings, routing keys, headers, topics | Simple: partition keys determine partition assignment |
| **Message ordering** | Per-queue (single consumer processes in order) | Per-partition (within a single partition only) |
| **Protocol** | AMQP 0-9-1 (standardized) | Custom binary protocol (simpler, faster) |
| **Scaling consumers** | Add consumers → they compete (work distribution) | Add consumers → they split partitions (parallelism) |
| **Built-in streaming** | No (deleted after consumption) | Yes (Kafka Streams, ksqlDB) |

#### When to use RabbitMQ

| Use Case | Why RabbitMQ fits |
|:---|:---|
| **Task/job queues** | Workers pick up tasks, process them, acknowledge — the broker handles distribution and retries |
| **RPC / request-reply** | AMQP supports reply-to queues natively; `Direct reply-to` for low latency |
| **Complex routing** | Topic exchanges, header exchanges, alternate exchanges — route messages based on any attribute or pattern |
| **Low-latency messaging** | Sub-millisecond delivery when co-located; ideal for real-time commands |
| **Per-message TTL / dead-lettering** | Set TTL per message or per queue; expired messages auto-route to DLX |
| **Many small, independent queues** | Hundreds of queues with fine-grained routing; RabbitMQ handles this efficiently |

#### When to use Kafka

| Use Case | Why Kafka fits |
|:---|:---|
| **Event streaming / event sourcing** | All events are retained as an immutable log; replay from any point in history |
| **High-throughput ingestion** | Millions of events/sec from clickstreams, IoT sensors, application logs |
| **Multi-consumer fan-out** | Multiple consumer groups read the same data independently at their own pace |
| **Change Data Capture (CDC)** | Database changes streamed to Kafka; consumers react without touching the source DB |
| **Stream processing** | Kafka Streams, ksqlDB, Flink — process, join, aggregate events in real time |
| **Audit / compliance** | All events retained for days or weeks; full replay capability for audits |
| **Event-driven microservices** | Each service owns its consumer group; replay history to rebuild state or fix bugs |

#### The decision flowchart

```
Do you need consumers to replay old messages?
  ├─ YES → Kafka
  └─ NO → Do you need complex routing rules (topics, headers, patterns)?
      ├─ YES → RabbitMQ
      └─ NO → Is throughput > 100K messages/sec?
          ├─ YES → Kafka
          └─ NO → Do you need sub-millisecond latency?
              ├─ YES → RabbitMQ
              └─ NO → Either works; pick the one your team already knows
```

#### The "why not both?" pattern

Many real systems use **both**. Example: an e-commerce platform:

- **Kafka** ingests raw clickstream events, order events, and inventory changes at high volume. Multiple teams replay and analyze this data.
- **RabbitMQ** handles operational commands: "send order confirmation email," "generate invoice PDF," "update loyalty points." These are task-queue workloads where at-least-once delivery with retries matters, and messages should be deleted after processing.

> **Interview tip**: Don't just compare features — explain the **architectural philosophy** difference: log vs. queue. Kafka says "keep everything, let consumers figure out what they need." RabbitMQ says "route precisely, deliver once, delete." Also mention that Kafka's consumer-group model means adding consumers doesn't help if you don't have enough partitions — that's a common gotcha.

### 18. What happens if your Kafka consumer reads a message but fails to commit the offset?

The consumer will read the same message **again** when it restarts or rebalances. Your processing logic **must be idempotent**, or you will process the data twice.

**How Kafka offset commits work**:

In Kafka, the **consumer** is responsible for tracking its position in each partition. This is fundamentally different from RabbitMQ, where the broker tracks what's been delivered. Kafka stores offsets in a special internal topic called `__consumer_offsets`.

```
Partition 0: [msg-0] [msg-1] [msg-2] [msg-3] [msg-4] [msg-5] ...
                                    ↑
                              committed offset = 2
                              (next read: msg-3)
```

The consumer reads messages, processes them, and then **commits** its offset — essentially saying "I've processed everything up to this point." The next time it starts, it resumes from the last committed offset.

**The failure scenario** — step by step:

```
1. Consumer reads  messages 3, 4, 5 (batch of 3)
2. Consumer processes message 3 → writes to DB ✅
3. Consumer processes message 4 → writes to DB ✅
4. Consumer processes message 5 → WRITE FAILS (DB connection lost)
5. Consumer CRASHES before committing offset

Offset still at 2. Consumer restarts.
6. Consumer reads messages 3, 4, 5 again
7. Message 3 is written to DB a SECOND time → DUPLICATE
8. Message 4 is written to DB a SECOND time → DUPLICATE
9. Message 5 is processed again (hopefully succeeds this time)
```

This is **at-least-once** semantics — the default for most Kafka consumers. You are guaranteed not to lose data, but you might process it more than once.

**Commit strategies and their tradeoffs**:

| Strategy | How it works | Risk |
|:---|:---|:---|
| **Auto-commit** (`enable.auto.commit=true`) | Commits every `auto.commit.interval.ms` (default 5s) | Messages processed between commits may be replayed after crash |
| **Commit after each message** | `commitSync()` after every `poll()` | Extremely slow — adds a network round-trip per message |
| **Commit after batch** | `commitSync()` after processing N messages | Best balance; at most N duplicates on failure |
| **Commit before processing** | Commit offset, then process | Risk of data loss — if process fails, offset is already advanced |

**Making your consumer idempotent** — practical patterns:

1. **Upsert instead of insert**: Use `INSERT ... ON CONFLICT (id) DO UPDATE` (PostgreSQL) or `REPLACE INTO` (MySQL). If the same message arrives twice, the second write overwrites rather than duplicates.

2. **Deduplication table**: Maintain a table of processed message IDs. Before processing, check if `message_id` exists. After processing, insert it in the same transaction as your business write.

   ```sql
   BEGIN;
   -- Check if already processed
   SELECT 1 FROM processed_messages WHERE message_id = 'msg-5';
   -- If not found, process and record
   INSERT INTO orders (...) VALUES (...);
   INSERT INTO processed_messages (message_id, processed_at) VALUES ('msg-5', NOW());
   COMMIT;
   ```

3. **Idempotency key in the message**: The producer embeds a UUID in each message. The consumer uses it as a deduplication key. If the same UUID is seen again, skip processing.

4. **Exactly-once semantics (EOS)**: Kafka supports **idempotent producers** and **transactional consumers** (reads + writes in a single atomic transaction). But this comes with a performance penalty and is only available within the Kafka ecosystem — once you write to an external system (database, API), you're back to at-least-once and must handle deduplication yourself.

**Detecting duplicates in production**: Monitor for:
- `UNIQUE` constraint violations on your deduplication key
- Unexpectedly high row counts (double-writes)
- Idempotency key lookup hit rate (should be near-zero in healthy operation)

> **Interview tip**: Start with "Kafka guarantees at-least-once delivery by default." Then explain that exactly-once is possible within Kafka (transactions) but the moment you talk to an external system, you need application-level idempotency. The practical answer is: design all consumers to be idempotent regardless of what the broker promises. Networks fail. Brokers fail. Idempotency is your safety net.

### 19. How do you handle poison messages that repeatedly crash your workers?

A **poison message** is any message that causes the consumer to fail **consistently** — not a transient error like a network timeout, but a deterministic failure: malformed JSON, a missing required field, a null reference, or business-rule violation that the code cannot handle.

**The death loop** — how it unfolds:

```
1. Worker picks up message from queue
2. Worker deserializes → starts processing
3. Processing throws NullPointerException / ValidationError
4. Worker crashes (or rejects the message without ack)
5. Message returns to the queue (NACK / timeout)
6. Another worker (or the same worker after restart) picks it up
7. Crashes again, identically
8. Infinite loop — the message blocks the queue, starving legitimate messages
```

If you have 5 messages in a queue and message #2 is poison, messages #3-5 may never be processed because the broker keeps retrying #2 first (depending on the broker and ordering guarantees).

**The solution — Dead Letter Queue (DLQ) + retry limits**:

The pattern has three components:

| Component | Responsibility |
|:---|:---|
| **Max retry count** | Limit how many times a message can be redelivered before giving up |
| **Dead Letter Queue (DLQ)** | A separate queue where poison messages are moved after exhausting retries |
| **Monitoring & alerting** | Someone (or something) must inspect the DLQ and decide what to do |

**Implementation approaches by broker**:

#### RabbitMQ

RabbitMQ has first-class support for this pattern:

```
Main queue: "orders.process"
  ├─ x-dead-letter-exchange: "orders.dlx"
  ├─ x-message-ttl: (optional, for delayed retry)
  └─ Consumer rejects with `requeue=false` after max retries

DLX routes to: "orders.process.dlq"
  └─ Monitored queue — ops team gets paged when messages arrive here
```

With a **retry count header** pattern:

```python
def process(message):
    retry_count = message.headers.get('x-retry-count', 0)

    try:
        business_logic(message.body)
        channel.basic_ack(message.delivery_tag)  # success
    except TransientError:
        if retry_count < MAX_RETRIES:
            # Republish with incremented retry count, maybe with delay
            headers = message.headers.copy()
            headers['x-retry-count'] = retry_count + 1
            channel.basic_publish(
                exchange='',
                routing_key=message.routing_key,
                body=message.body,
                properties={'headers': headers}
            )
            channel.basic_ack(message.delivery_tag)  # ack original
        else:
            # Exhausted retries → DLQ
            channel.basic_nack(message.delivery_tag, requeue=False)
    except PermanentError:
        # Don't even retry — straight to DLQ
        channel.basic_nack(message.delivery_tag, requeue=False)
```

#### Kafka

Kafka doesn't have a built-in DLQ concept, but the pattern is implemented with:

1. **Retry topic**: A separate topic where failed messages are published with a delay (using a consume-pause-produce pattern or a scheduled delay).
2. **DLT (Dead Letter Topic)**: Messages that exhaust retries are published here.
3. **Consumer commits the offset** even for failed messages — you've "captured" the poison message by moving it to the retry topic or DLT, so don't block the partition.

```
Main topic: "orders"
  └─ Consumer processes → fails → publish to "orders.retry.1"
                                   → commit offset (don't block partition!)

Retry topic: "orders.retry.1"
  └─ Separate consumer → delay → attempt 2
      ├─ Success → commit offset in retry topic
      └─ Fail → publish to "orders.retry.2" → attempt 3
          ├─ Success → done
          └─ Fail → publish to "orders.dlt" (Dead Letter Topic)
```

#### AWS SQS

SQS has this built-in via **redrive policies**:

- `maxReceiveCount`: Number of times a message can be received before moving to DLQ (e.g., 3)
- Dead-letter queue is a separate SQS queue
- Messages in the DLQ retain their original `messageId` and include attributes showing how many times they were received

#### Azure Service Bus

Azure Service Bus has the most sophisticated built-in support:

- `MaxDeliveryCount`: After N deliveries (default 10), the message is **automatically dead-lettered**
- The dead-lettered message includes `DeadLetterReason` and `DeadLetterErrorDescription`
- You can peek, resubmit, or delete dead-lettered messages from the Azure Portal or programmatically

**What to do with messages in the DLQ**:

| Action | When to use |
|:---|:---|
| **Fix the producer** | The message format is wrong — fix the upstream service and resubmit |
| **Fix the consumer** | The consumer has a bug — deploy a fix, then replay from DLQ |
| **Skip and acknowledge** | The message is genuinely invalid (e.g., a cancelled order that was already deleted) — log and ack |
| **Manual intervention** | Complex business-logic failure — a human needs to decide |
| **Alert** | Set up alarms: if DLQ depth > 0 for more than 5 minutes, page the on-call |

**Avoiding poison messages in the first place**:

1. **Schema validation at ingest** — Validate against a schema (Avro, Protobuf, JSON Schema) before the message enters the system. Reject malformed messages at the producer side.
2. **Defensive deserialization** — Never assume a field exists. Use optional chaining, default values, and version-tolerant parsing.
3. **Dead-letter early** — If a message is clearly malformed (missing required field), dead-letter it immediately instead of retrying.

> **Interview tip**: Distinguish between **transient errors** (network blip, DB timeout — should retry) and **permanent errors** (malformed payload, missing data — should dead-letter). The key insight is: retrying a permanent error is worse than useless — it blocks the queue. Also mention that DLQs without monitoring are just a garbage dump — you need alerts, dashboards, and an operational runbook for when messages land there.

### 20. How do you ensure messages are processed in the exact order they were sent?

In a distributed queue with multiple consumers, **global ordering is basically impossible** — and trying to achieve it will destroy your throughput. The key insight is that you almost never need total ordering; you need **ordering within related groups of messages**.

**Why global ordering is hard**:

```
Producer sends:  [A] [B] [C] [D]  (in order)

Queue distributes across 3 consumers:
  Consumer 1: [A] ────── takes 100ms
  Consumer 2: [B] ── takes 20ms   ← finishes first!
  Consumer 3: [C] ──────── takes 150ms

Actual processing order: B → A → C → D
```

Even if all consumers were equally fast, network variance, GC pauses, and OS scheduling make ordering unpredictable across consumers. The only way to guarantee global order is to use **one consumer with one thread** — which limits throughput to what a single CPU core can handle.

**The practical solution — partition by entity**:

Instead of ordering everything globally, you ensure that **all messages for the same entity go to the same partition** (and thus the same consumer). Within a single partition, order is preserved.

```
Messages for user #42:  [msg-1] [msg-2] [msg-3]  → Partition 0 → Consumer A
Messages for user #99:  [msg-1] [msg-2]           → Partition 1 → Consumer B
Messages for user #17:  [msg-1] [msg-2] [msg-3]   → Partition 2 → Consumer C
```

Each user's messages are processed in order, but users are processed in parallel.

**How to implement partitioning**:

#### Kafka

Set the **partition key** on the producer. Kafka hashes the key to determine the partition:

```java
// All events for user #42 go to the same partition
ProducerRecord<String, String> record = new ProducerRecord<>(
    "user-events",        // topic
    "user-42",            // key → determines partition
    eventJson             // value
);
producer.send(record);
```

If you don't set a key, Kafka uses a round-robin partitioner (no ordering guarantee). If you change the number of partitions, the hash distribution changes — messages for `user-42` might move to a different partition, breaking ordering across the migration. Plan partition counts carefully.

#### RabbitMQ

Use the **consistent hash exchange** plugin, or manually route messages to queues:

```
Exchange: "user-events" (consistent-hash-exchange)
  ├─ Queue: "user-events.shard-0"  ← hash("user-42") % 4 = 0
  ├─ Queue: "user-events.shard-1"  ← hash("user-99") % 4 = 1
  ├─ Queue: "user-events.shard-2"  ← hash("user-17") % 4 = 2
  └─ Queue: "user-events.shard-3"
```

Each queue has exactly one consumer, so messages within a shard are processed FIFO.

#### AWS SQS

Use **SQS FIFO queues** (as opposed to Standard queues). FIFO queues guarantee exactly-once processing and first-in-first-out delivery — but at ~300 transactions per second (with batching, up to 3,000 messages/s), far lower than standard queues. For higher throughput, use **message group IDs**:

```
Queue: "orders.fifo" (FIFO)
  Message group: "customer-42" → messages for this customer are FIFO
  Message group: "customer-99" → messages for this customer are FIFO
```

Messages in different groups can be processed in parallel; messages within the same group are strictly ordered.

#### Azure Service Bus

Use **Sessions** — set `SessionId` on messages, and use a session-aware consumer. All messages with the same `SessionId` are delivered in FIFO order to the same consumer.

**What about global ordering when you truly need it?**

Sometimes you do need global order — for example, a financial ledger where every credit and debit must be applied in exact sequence. Pattern: use a **single partition** (Kafka) or a **single FIFO queue** (SQS). Accept the throughput ceiling. If that's not enough:

1. **Sequence numbers in the message**: The producer assigns a monotonically increasing sequence number. The consumer buffers out-of-order messages and only processes them when the next expected sequence number arrives.
2. **Deterministic re-ordering at the consumer**: Write messages to a buffer sorted by timestamp or sequence number. Flush when a configurable window closes or when the next expected message arrives.
3. **Event sourcing with CQRS**: Store all events in order (Kafka single partition), then project them into read models asynchronously. The write side is ordered; the read side is eventually consistent but can scale.

**When order doesn't actually matter**:

Many teams over-engineer ordering. Ask yourself:
- If two users update their profiles at the same time, does the order matter? (No — they're independent.)
- If a user adds an item to a cart and then removes it, but the remove is processed first, what happens? (The cart ends up the same — last-write-wins is fine.)
- If two IoT sensors report temperature at the same time, does order matter? (Probably not — aggregate by time window.)

> **Interview tip**: Start with: "Do you need global ordering or entity-level ordering?" 99% of the time it's entity-level. Then explain partition keys in Kafka, session IDs in Azure Service Bus, message group IDs in SQS FIFO, or consistent-hash exchanges in RabbitMQ. The senior-level answer acknowledges that true global ordering requires sacrificing parallelism and that the interviewer should question whether they truly need it. Also mention the sequence-number buffering pattern for cases where you need ordering across partitions without giving up parallelism entirely.

---

## Final Thoughts

This list looks intimidating if you try to memorize it in a weekend. It is completely manageable if you take the time to understand the problems these concepts solve.

Every single one of these questions is about dealing with **scale**, **failure**, and **reality**:

- The database gets slow.
- The network drops.
- The users send bad data.

Senior engineers spend their days mitigating these exact problems. If you are looking for a structured way to study these concepts in the context of the companies you are actually interviewing with, *PracHub* organizes backend technical rounds by topic and provides the specific follow-up questions that interviewers ask to test your depth.

> **Do not try to memorize the answers. Try to understand the pain points. When you understand the pain points, the answers make sense.**

— *Emily*