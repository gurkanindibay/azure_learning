---
title: "I will never walk into a backend interview without solving these 20 questions"
author: "Emily"
date: "2026-05-05"
readTime: "7 min read"
source: "Medium"
tags: ["backend", "interview", "system-design", "databases", "caching", "concurrency", "message-brokers"]
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
This is the most common performance bug in modern applications that use ORMs. You query a list of users, and then as you loop through the users, the ORM fires a separate query to fetch each user’s profile. You need to be able to explain how to fix it using **explicit joins** or **eager loading**.

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

If multiple workers need exclusive access to a resource, they need a distributed lock. Using a single Redis instance works until that instance goes down. You should be familiar with algorithms like **Redlock** or systems like **ZooKeeper** / **etcd** that handle distributed consensus.

### 8. How do you implement idempotency for a payment retry endpoint?

Mobile networks drop connections. Clients will retry requests. If a client retries a payment request because they did not receive the success response, you cannot charge their card twice. You need to explain how to use **idempotency keys** and where to store them to guarantee **exactly-once processing**.

---

## Caching Strategy

Everyone knows caching makes things faster. Interviewers want to know if you understand how caching makes things break.

### 9. What causes a cache stampede and how do you prevent it?

When a highly requested cache key expires, thousands of requests miss the cache simultaneously and hit the database at the exact same moment. The database falls over. You need to know how to prevent this using **probabilistic early expiration** or a **lock** to ensure only one thread regenerates the cache.

### 10. If you cache a user profile, how do you invalidate it when they update their email?

Cache invalidation is a genuinely hard problem. You need to explain the difference between a **write-through cache** and a **cache-aside** pattern, and discuss the tradeoffs of setting a short **TTL (Time-To-Live)** versus explicitly deleting the key on every update.

### 11. Why might putting Redis in front of your database actually slow your system down?

Adding a network hop to check a cache takes a few milliseconds. If your cache hit rate is terrible, you are paying the network penalty on every request just to find out the data is not there, and then hitting the database anyway. You should know how to monitor and calculate **cache hit ratios**.

### 12. What eviction policy makes sense for a session store versus a content feed?

Caches run out of memory. When they do, they have to delete something to make room.

| Eviction Policy | Best For | Worst For |
|:---|:---|:---|
| **LRU** (Least Recently Used) | Content feeds, timelines | Session stores |
| **LFU** (Least Frequently Used) | Frequently accessed static data | Real-time data |
| **TTL-only** | Session stores | General-purpose caching |
| **FIFO** (First In, First Out) | Simple queues | Varied-access patterns |

**LRU** makes sense for a content feed. It is a terrible choice for a session store where you might log active users out randomly.

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

They are not interchangeable:

| Feature | RabbitMQ | Kafka |
|:---|:---|:---|
| **Model** | Smart broker, dumb consumers | Dumb broker, smart consumers |
| **Throughput** | Moderate (tens of thousands/s) | High (millions/s) |
| **Message Retention** | Deleted after consumption | Retained (log-based) |
| **Replayability** | No | Yes (offsets) |
| **Routing** | Complex (exchanges, bindings) | Simple (topic-based) |
| **Best For** | Task queues, RPC, complex routing | Event streaming, high-throughput logs |

Kafka is a distributed log built for high throughput and replayability. RabbitMQ is a smart broker built for complex routing and task queues. You need to know which one fits your use case.

### 18. What happens if your Kafka consumer reads a message but fails to commit the offset?

The consumer will read the same message again when it restarts. Your processing logic **must be idempotent**, or you will process the data twice.

### 19. How do you handle poison messages that repeatedly crash your workers?

If a malformed message causes a null pointer exception in your worker, the worker crashes, the message goes back to the queue, and another worker picks it up and crashes — creating an infinite crash loop. You need to explain **Dead Letter Queues (DLQ)** and **retry limits**:

1. Set a maximum retry count (e.g., 3 attempts)
2. After the limit is exhausted, route the message to a **DLQ**
3. Monitor the DLQ and investigate malformed messages manually

### 20. How do you ensure messages are processed in the exact order they were sent?

In a distributed queue with multiple consumers, order is almost impossible to guarantee because consumer A might take longer to process message 1 than consumer B takes to process message 2. You need to explain **partitioning** or **routing keys** that ensure related messages go to the same single consumer thread.

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