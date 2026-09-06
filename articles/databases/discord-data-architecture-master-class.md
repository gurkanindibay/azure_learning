---
type: Article
title: "Discord's Trillion-Message Architecture Is a Distributed Systems Masterclass"
description: "*From a single MongoDB replica to 4 trillion messages — here's every engineering decision that actually mattered.*"
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Discord's Trillion-Message Architecture Is a Distributed Systems Masterclass

> **Originally published**: May 15, 2026 · 5 min read  
> **Source**: [Discord Engineering Blog](https://discord.com/blog/how-discord-stores-trillions-of-messages) — Bo Ingram

---

*From a single MongoDB replica to 4 trillion messages — here's every engineering decision that actually mattered.*

Most teams never hit the scale where their database becomes a liability. **Discord hit it twice.**

In 2015, a single MongoDB replica stored all messages. By November that year, the count crossed 100 million and MongoDB was falling apart under write pressure. They migrated to **Cassandra**. By 2022, that Cassandra cluster had grown to **177 nodes** storing trillions of messages — and it was buckling again. This is the story of what they did next, and why every decision is worth studying.

![Discord Data Architecture](images/discord-data-architecture-master-class/discord-data-architecture.png)

---

## 1. The Data Model: Partitioning By Design

Discord's message schema is deceptively simple:

```sql
CREATE TABLE messages (
  channel_id    bigint,
  bucket        int,         -- static time window
  message_id    bigint,      -- Snowflake ID (chronologically sortable)
  author_id     bigint,
  content       text,
  PRIMARY KEY   ((channel_id, bucket), message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

The partition key is `(channel_id, bucket)`. This keeps messages for a given channel and time window co-located across nodes — great for range reads, **dangerous under load**.

### The Hot Partition Problem

A popular server with hundreds of thousands of concurrent users sends a torrent of traffic to a single partition. Cassandra handles this with unbounded concurrency — it just queues up queries. Latency climbs. Other queries behind the hot one suffer. And since Discord uses **quorum consistency**, any node serving that partition starts bleeding latency outward.

```
Cassandra Cluster (quorum reads/writes)
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Node A  │    │  Node B  │    │  Node C  │
│          │◄───│ hot part │───►│          │
│  normal  │    │ ●●●●●●●● │    │  normal  │
│  latency │    │ OVERLOAD │    │  latency │
│   <5ms   │    │  >125ms  │    │   <5ms   │
└──────────┘    └──────────┘    └──────────┘
        quorum = must wait for 2/3 nodes
        → hot node poisons the whole query
```

> A single busy channel could degrade the experience for **every user on the platform**. That's the core failure mode.

---

## 2. The Fix: A Rust Service Layer

Rather than just swapping the database, Discord added an **intermediary layer** — multiple copies of the same Rust Data Service, sitting between the API monolith and the database clusters.

> **What are Svc1, Svc2, Svc3?** They are **identical replicas** of the same Rust binary, running on different machines/containers — like 3 pods of a microservice. The only difference is which channels hash to which instance.

### The Problem, Visualized

```
WITHOUT the service layer:                  WITH the service layer:

  500 users request #general                 500 users request #general
       │                                           │
  ┌────┼────┬────┐                    ┌───────────┼───────────┐
  ▼    ▼    ▼    ▼                     ▼           ▼           ▼
 Svc1 Svc2 Svc3 Svc4              Svc1         Svc2         Svc3
  │    │    │    │             (handles     (handles     (handles
  │    │    │    │             #random)     #general)    #memes)
  │    │    │    │                │        ╔═══════╗      │
  └────┼────┼────┘                │        ║coalesce║      │
       ▼    ▼                     │        ║ 499→1  ║      │
  ┌─────────────────┐             │        ╚═══╤════╝      │
  │  Cassandra Node  │ ← 500      │            │           │
  │     OVERLOAD     │   queries  │       1 DB query       │
  └─────────────────┘             │            │           │
                                  ▼            ▼           ▼
                           ┌──────────────────────────────────┐
                           │         Cassandra Node           │
                           │      handles 1 query (not 500)   │
                           └──────────────────────────────────┘
```

Two mechanisms work together — routing **concentrates** the heat, coalescing **extinguishes** it:

### 2.1 Consistent Hash-Based Routing — Concentrates the Heat

```
hash(channel_id) % num_services  →  which Svc instance handles this channel

  #general  → hash → Svc2    (all 500 requests land here)
  #memes    → hash → Svc3    (unaffected by #general's traffic)
  #random   → hash → Svc1    (unaffected by #general's traffic)
```

| What this does | Why it matters |
|---|---|
| Hot channel traffic is **pinned** to one instance | Other instances stay cold — they serve their own channels at full speed |
| All 500 requests meet at the **same place** | Without this, coalescing can't work because each instance only sees a fraction of requests |

### 2.2 Request Coalescing — Extinguishes the Heat

**First, why can 500 user requests collapse into 1 DB query?** Because they aren't 500 *different* queries — they're the same query, 500 times:

```
User A opens #general → "show latest 50 messages"
User B opens #general → "show latest 50 messages"
User C opens #general → "show latest 50 messages"
   ⋮
User 500 opens #general → "show latest 50 messages"

ALL translate to the identical DB query:

  SELECT * FROM messages
  WHERE channel_id = 789 AND bucket = 42
  ORDER BY message_id DESC
  LIMIT 50;
```

Why identical? Because Discord's partition key is `(channel_id, bucket)`:

```sql
PRIMARY KEY ((channel_id, bucket), message_id)
--            ^^^^^^^^^^^^^^^^^^^
--            Same for ALL users reading the same channel right now
```

The `message_id` varies per individual message, but the **partition key** — the part that routes to a Cassandra node — is always `(channel_id=789, bucket=42)`. Every user reading #general hits the same partition. That's what the coalescer keys on.

**How the coalescer works**, step by step:

Inside Svc2, a `HashMap` tracks in-flight DB queries:

```
inflight: {
    ("channel_789", bucket_42): <currently-running-DB-query>
}
```

Timeline when 500 requests hit Svc2 simultaneously:

```
Time ──────────────────────────────────────────────────────────────►

Req #1:   [map empty] [issues DB query] [stores handle in map] ..... [DB responds]
                                                                     [wakes all 500]
                                                                     [removes from map]
Req #2:        [map has handle!] [subscribes to it] ................. [wakes up]
Req #3:             [map has handle!] [subscribes] .................. [wakes up]
...
Req #500:           [map has handle!] [subscribes] .................. [wakes up]

Cassandra:                              [1 query executing] ......... [1 response]
                                        (not 500 — same query, same answer)
```

```rust
// What actually runs inside Svc2
async fn get_messages(key: PartitionKey) -> Result<Messages> {
    // Is someone ALREADY fetching this exact partition?
    if let Some(handle) = self.inflight.get(&key) {
        // YES — I'm requests #2 through #500. Just wait.
        return handle.subscribe().await;
    }
    // NO — I'm request #1. Start the DB query.
    let handle = self.spawn_db_query(key.clone());
    self.inflight.insert(key, handle.clone());  // publish so others subscribe
    let result = handle.await;                   // wait for DB
    self.inflight.remove(&key);                  // clean up for next batch
    result
}
```

**The key insight**: All 500 requests share the **same Rust `Future`**. When the DB responds, that one future resolves and wakes all 500 waiters simultaneously — each gets the same result set. The DB executed 1 query, not 500, because the query was always the same.

> **Common misconception**: *"But each user has different scroll position / wants different messages!"* — In practice, a hot channel has most users reading the **latest messages** (same bucket, same range). For users reading older buckets, those get separate coalescer entries — but they're far fewer and don't cause hot partition problems.

### Why Both Mechanisms Must Work Together

| | Coalescing only | Routing only | **Both** |
|---|---|---|---|
| Reduces DB queries? | ⚠️ Partial (only per-instance) | ❌ Still 500 queries | ✅ 500→1 |
| Isolates hot from cold channels? | ❌ Hot scatters everywhere | ✅ Hot pinned to one instance | ✅ |
| Cold-channel latency unaffected? | ❌ All instances hit | ✅ Only one instance hit | ✅ |

Without routing, 500 requests scatter across 4 instances (125 each). Each instance coalesces 125→1. The DB still gets 4 queries — better than 500, but 4× worse than it could be. With routing, all 500 arrive at Svc2 → 500→1. That's the difference.

This alone changed the pressure profile on the database significantly — **before any migration happened**.

---

## 3. Why ScyllaDB, Not More Cassandra

ScyllaDB is API-compatible with Cassandra — same CQL, same drivers, same replication model. But the internals are **fundamentally different**.

|                      | Cassandra                              | ScyllaDB       |
| -------------------- | -------------------------------------- | -------------- |
| Language             | Java (JVM)                             | C++            |
| GC pauses            | Yes — frequent source of latency spikes | None           |
| Thread model         | Shared thread pool                     | Shard-per-core |
| p99 read latency     | 40–125ms                               | ~15ms          |
| p99 write latency    | 5–70ms                                 | ~5ms           |

### The GC Problem

The garbage collector was Discord's biggest operational pain. Long GC pauses would cause node instability bad enough that an **on-call engineer had to manually reboot nodes** and babysit them back to health. That toil disappears with C++.

### Shard-per-Core Architecture

Each CPU core owns its data slice and processes requests independently — no lock contention between shards, better isolation between hot and cold workloads.

### The Result

> **177 Cassandra nodes → 72 ScyllaDB nodes** handling the same data with **better performance**.

---

## 4. The Migration: 3 Months → 9 Days

Moving trillions of live messages without downtime is the kind of problem that looks impossible — until someone just does it.

| Plan | Tool | Estimated |
| ---- | ---- | --------- |
| Initial | ScyllaDB's Spark migrator | **3 months** |
| Final | Custom Rust migrator | **9 days** |

Discord's engineers extended their existing Rust data service library into a **custom migrator**. It reads token ranges from the source, checkpoints progress locally via **SQLite** (restartable, no lost work), and firehoses data into ScyllaDB at full throughput.

### Migration Strategy

| Technique | Purpose |
| --------- | ------- |
| **Dual-writes** | New messages written to both databases simultaneously throughout the migration |
| **Automated validation** | A percentage of reads compared across both clusters to confirm correctness |
| **SQLite checkpoints** | Restartable migration — no lost progress on failure |

### The Tombstone Edge Case

At **99.9999% completion**, a range of tombstones (deleted records) caused the migrator to hang. A compaction of that token range cleared it. Switch-over was clean — **users noticed nothing**.

---

## 5. What This Architecture Actually Teaches

A few things worth internalizing:

### Abstractions Buy You Time

The data service layer gave Discord a place to solve hot partition problems **without touching the database**. When they eventually did migrate the database, the surrounding system was already better.

### Rewriting in Rust Isn't a Meme Here

The migration tool, written in an afternoon, cut estimated time by **95%**. Rust's performance characteristics and fearless concurrency weren't marketing — they were necessary.

### Database Compatibility ≠ Database Equivalence

ScyllaDB speaks Cassandra's language but executes fundamentally differently. The same query on the same schema can have **wildly different runtime behavior** depending on the underlying implementation.

### Prove the Migration with Data, Not Confidence

Dual-writes plus automated read comparison is the only way to migrate at this scale without gambling. Gut feelings about data correctness don't survive 4 trillion records.

---

## Key Takeaways for Architects

| Lesson | Application |
| ------ | ----------- |
| Hot partitions are the universal scaling bottleneck | Design partition keys for even distribution; use caching/coalescing layers |
| Service layers decouple migration from application logic | Add indirection before you need it — it makes future changes cheaper |
| Database API compatibility ≠ performance equivalence | Always benchmark your actual workload, not just the API surface |
| Rust is viable for performance-critical data infrastructure | GC-free, shard-per-core, and zero-cost abstractions are real advantages |
| Live migrations need dual-writes + automated validation | Never trust a migration without continuous correctness verification |
| SQLite is an excellent checkpoint store | Lightweight, portable, restartable — perfect for migration tools |

---

**Source**: [Discord Engineering Blog — How Discord Stores Trillions of Messages](https://discord.com/blog/how-discord-stores-trillions-of-messages) by Bo Ingram
