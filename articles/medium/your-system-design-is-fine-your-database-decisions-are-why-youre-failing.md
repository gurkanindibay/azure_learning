---
type: Article
title: "Your System Design Is Fine. Your Database Decisions Are Why You're Failing."
source: "https://medium.com/@kanishks772/your-system-design-is-fine-your-database-decisions-are-why-youre-failing-58dd75bc6417"
author:
  - "[[The Latency Gambler]]"
published: 2026-04-24
timestamp: 2026-06-18T00:00:00Z
description: "A system-design interview guide to the database decisions that actually matter: SQL vs NoSQL, ACID, indexing, scaling reads/writes, CAP, sharding, isolation levels, storage internals, and distributed transactions."
tags:
  - clippings
  - databases
  - system-design
---

# Your System Design Is Fine. Your Database Decisions Are Why You're Failing

*Most engineers can draw boxes and arrows. The ones who get the offer know what lives inside those boxes.*

There's a pattern in system design interviews at top companies. Candidates sketch a clean architecture load balancers, microservices, caches and then freeze the moment someone asks: *"How would you handle write contention at scale?"* or *"Walk me through your sharding strategy."*

The system design wasn't the problem. The database layer was.

Here are the concepts that actually get tested, and what you need to know about each one.

![Database decisions overview - AI generated image](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*IL31TJVS4W-Kiyrs3_40OA.png)

## The Foundation You Cannot Skip

### SQL vs NoSQL — It's a Data Model Choice, Not a Trend

Stop treating this as a popularity contest. The decision comes down to your access patterns.

```text
Use SQL when:                        Use NoSQL when:
- Complex joins are common           - Schema changes frequently
- ACID guarantees are required       - Horizontal scale is priority
- Data has a fixed schema            - Access is key-value or document-based
- Reports and aggregations matter    - Latency at scale matters more than consistency
```

A social feed's post metadata? NoSQL fits. A payment ledger? SQL, no question.

### ACID — What It Actually Means Under Load

Most people can recite the acronym. Few can explain *why* it matters when 10,000 concurrent users hit the same table.

- **Atomicity**: Partial writes don't exist. The transaction commits fully or rolls back entirely.
- **Consistency**: A write that violates a constraint never lands in the database.
- **Isolation**: Concurrent transactions behave as if they ran serially at varying degrees (more on isolation levels below).
- **Durability**: Once committed, data survives a crash.

### Indexing — Where Interviews Get Separated

```sql
-- Without index: full table scan, O(n)
SELECT * FROM orders WHERE customer_id = 9821;

-- With index on customer_id: B-tree lookup, O(log n)
CREATE INDEX idx_customer ON orders(customer_id);

-- Composite index - column ORDER matters
CREATE INDEX idx_customer_date ON orders(customer_id, created_at);
-- This helps: WHERE customer_id = X AND created_at > Y
-- This does NOT use the index: WHERE created_at > Y (leading column missing)
```

An index speeds up reads but adds overhead on every write. Know when to add them and when not to.

### Scaling Reads

```text
┌─────────────┐
Write ─────────►│  Primary DB │
                └──────┬──────┘
                       │  Replication
          ┌────────────┼────────────┐
          ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Replica 1│ │ Replica 2│ │ Replica 3│
    └──────────┘ └──────────┘ └──────────┘
          ▲            ▲            ▲
          └────────────┴────────────┘
                   Read traffic
```

**Read replicas** handle read-heavy workloads by distributing SELECT queries across copies of your data. The tradeoff: replication lag. A user might write a post and briefly not see it on a replica that hasn't caught up.

**Database caching** (Redis, Memcached) sits in front of the database entirely. Serve hot data from memory sub-millisecond latency instead of milliseconds from disk.

```python
def get_user_profile(user_id):
    cache_key = f"user:{user_id}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - hit the database
    user = db.query("SELECT * FROM users WHERE id = %s", user_id)
    redis.setex(cache_key, 3600, json.dumps(user))  # TTL: 1 hour
    return user
```

## Scaling Writes

This is where most candidates stumble.

### CAP Theorem — The Real Constraint

In a distributed system, during a network partition, you get two choices:

```text
Consistency
            /\
           /  \
          /    \
         / CP  AP\
        /---------\
Partition ──────── Availability
Tolerance
```

- **CP systems** (e.g., HBase, Zookeeper): Stay consistent, reject requests when partition happens
- **AP systems** (e.g., Cassandra, DynamoDB): Stay available, allow stale reads during partition

There is no "CA" in a distributed system. Partitions happen. Pick your tradeoff.

### Sharding — Split the Data, Multiply the Complexity

```text
┌─────────────────────────────┐
 │      Application Layer      │
 └──────┬──────────────┬───────┘
        │              │
user_id % 2 = 0   user_id % 2 = 1
        │              │
 ┌──────▼──────┐ ┌─────▼───────┐
 │   Shard 0   │ │   Shard 1   │
 │ (users 0,2, │ │ (users 1,3, │
 │  4, 6...)   │ │  5, 7...)   │
 └─────────────┘ └─────────────┘
```

Sharding splits data horizontally across machines. The hard problems: cross-shard queries become expensive, resharding when you add nodes is painful, and hotspots (one shard receiving disproportionate traffic) can tank performance. **Consistent hashing** solves the resharding problem by minimizing key remapping when nodes are added or removed.

### Isolation Levels — The One Nobody Studies

```text
Level               | Dirty Read | Non-Repeatable Read | Phantom Read
--------------------|------------|---------------------|-------------
Read Uncommitted    |    YES     |        YES          |    YES
Read Committed      |    no      |        YES          |    YES
Repeatable Read     |    no      |        no           |    YES
Serializable        |    no      |        no           |    no
```

Higher isolation = stronger guarantees = worse performance. Most databases default to Read Committed. PostgreSQL defaults to Read Committed. MySQL InnoDB defaults to Repeatable Read. Know what your database gives you out of the box.

## Storage Internals That Show Up More Than You Think

### B-Tree vs LSM-Tree

```text
B-Tree (PostgreSQL, MySQL):          LSM-Tree (Cassandra, RocksDB):
- Optimized for reads                - Optimized for writes
- In-place updates                   - Append-only, compaction later
- Good for OLTP                      - Good for write-heavy workloads
- Random I/O pattern                 - Sequential I/O pattern
```

### Write-Ahead Log (WAL)

Before any change hits the actual data file, it's written to a log. If the database crashes mid-write, it replays the log on recovery. This is how durability works in practice. Every major database uses this pattern.

### Bloom Filters

```python
# Probabilistic data structure
# "Is this key definitely NOT in the set?"

bloom_filter.add("user:1234")

bloom_filter.check("user:9999")  # → False (definitely not present)
bloom_filter.check("user:1234")  # → True (probably present - go check disk)
```

Bloom filters eliminate unnecessary disk lookups. If the filter says "not present," skip the read entirely. Used in Cassandra, HBase, and Bigtable to avoid ghost reads.

## Distributed Transactions — The Final Boss

### Two-Phase Commit (2PC)

```text
Coordinator ──► "Prepare to commit?" ──► All participants
Coordinator ◄── "Ready" ◄────────────── All participants
Coordinator ──► "Commit!" ─────────────► All participants
```

Atomic across services, but the coordinator is a single point of failure and the protocol blocks during failures. Used when strong consistency is non-negotiable.

### Saga Pattern — The Practical Alternative

```text
Order Service ──► Payment Service ──► Inventory Service
      │                 │                    │
   On fail:         On fail:              On fail:
 Cancel order    Refund payment       Restore inventory
```

Each step has a compensating transaction. If step 3 fails, you run the compensation for steps 2 and 1. No global lock. Eventual consistency instead of strong consistency. This is how most production microservices handle distributed transactions.

### Change Data Capture (CDC)

```text
MySQL Binlog ──► Debezium ──► Kafka ──► Search Index
                                    └──► Analytics DB
                                    └──► Cache Invalidation
```

Stream every database change downstream without polling. Debezium reads the WAL and publishes events to Kafka. Downstream consumers react in near-real time. Essential for keeping multiple data stores in sync.

## The Mental Model That Ties It Together

These topics aren't isolated — they're a hierarchy:

```text
┌─────────────────────────┐
│   Distributed Txns      │  ← Hardest
│  (Saga, 2PC, Quorum)    │
├─────────────────────────┤
│   Storage Internals     │
│  (WAL, B-Tree, Bloom)   │
├─────────────────────────┤
│   Scaling Writes        │
│  (CAP, Sharding, Iso.)  │
├─────────────────────────┤
│   Scaling Reads         │
│  (Replicas, Cache)      │
├─────────────────────────┤
│   Foundations           │
│  (SQL/NoSQL, ACID,Index)│  ← Master here first
└─────────────────────────┘
```

You cannot have a meaningful conversation about sharding without understanding indexing. You cannot reason about the Saga pattern without knowing why 2PC is problematic. The pyramid matters.

## Final Word

System design interviews are not testing whether you can draw a diagram. They're testing whether you understand the *constraints* behind the diagram where data lives, how it gets written, what happens when a node goes down.

The engineers who clear these rounds consistently are not the ones who memorize the most tools. They're the ones who can say: *"Given this workload, this consistency requirement, and this scale, here's the tradeoff I'm making and why."*

That clarity comes from understanding databases from the ground up. Start at the foundation. Work your way to the top.

*If this was useful, follow for more system design and engineering content. Drop a comment with any concepts you'd add to this list.*
