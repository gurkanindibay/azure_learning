---
type: System Design
title: "Database Decisions — Key Takeaways"
description: "System-design database decisions: SQL vs NoSQL, ACID, indexing, read replicas, CAP, sharding, isolation levels, B-Tree vs LSM-Tree, WAL, Bloom filters, 2PC, Saga, and CDC."
timestamp: 2026-06-18T00:00:00Z
---

# 38. Database Decisions — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [Your System Design Is Fine. Your Database Decisions Are Why You're Failing](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)
> **Purpose**: Extract reusable database-decision patterns from the source article.

> **Also see**: [Databases & Query Performance](01-databases-query-performance.md) (db-01–db-07), [Concurrency & Transactions](02-concurrency-transactions.md) (tx-01–tx-07), [SQL System Design](19-sql-system-design-takeaways.md) (sqld-01–sqld-08)
> **Dictionary**: [Data, Concurrency & Transactions](../reference-dictionary/data-concurrency.md), [Databases & Database Engines](../reference-dictionary/databases.md), [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Taxonomy Reference**: §4.0 Data Architecture Fundamentals, §4.0.1 Database Performance & Caching, §4.1 Data Architecture, §4.3 Streaming & Real-Time Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [db-08](#db-08-sql-vs-nosql--data-model-choice) | Picking the wrong database model for the workload | SQL vs NoSQL decision framework |
| [db-09](#db-09-acid-guarantees-under-load) | Can't explain transaction guarantees under concurrency | ACID properties mapped to failure modes |
| [db-10](#db-10-indexing--composite-indexes) | Queries scan full tables; interviews separate candidates here | B-tree and composite index design |
| [db-11](#db-11-scaling-reads--read-replicas--caching) | Read traffic overwhelms the primary database | Read replicas + cache-aside with TTL |
| [db-12](#db-12-cap-theorem--partition-tradeoffs) | Believing a distributed DB can be fully consistent and available | CP vs AP partition choice |
| [db-13](#db-13-sharding--horizontal-partitioning--hotspots) | Single-instance write throughput ceiling | Hash/range/geo sharding with consistent hashing |
| [db-14](#db-14-isolation-levels) | Concurrency anomalies (dirty reads, phantoms) | Matching isolation level to anomaly tolerance |
| [db-15](#db-15-storage-engine-internals--b-tree-vs-lsm-tree-wal--bloom-filters) | Storage engine mismatched to workload | B-Tree vs LSM-Tree, WAL, Bloom filters |
| [db-16](#db-16-distributed-transactions--2pc-vs-saga) | Need atomicity across services without a single ACID boundary | 2PC vs Saga with compensating transactions |
| [db-17](#db-17-change-data-capture-cdc) | Keeping caches, search indexes, and analytics DBs in sync | Log-based CDC via Debezium/Kafka |

---

## db-08: SQL vs NoSQL — Data Model Choice

> **Source**: [§"SQL vs NoSQL — It's a Data Model Choice, Not a Trend"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Teams choose a database by hype and later fight the data model. |
| **Root cause** | Selection driven by popularity rather than access patterns, relationships, and consistency needs. |

**Strategy**: Use **SQL** when the workload needs complex joins, a fixed schema, ACID transactions, and reporting/aggregations. Use **NoSQL** when the schema changes frequently, horizontal scale is the priority, access is key-value or document-based, or sub-millisecond latency matters more than strong consistency.

| Tradeoff | Detail |
|:---|:---|
| **SQL** | Strong consistency, query power, and relational integrity; scaling writes usually requires replicas, partitioning, or sharding. |
| **NoSQL** | Elastic horizontal scale and flexible schemas; joins and multi-row transactions often move to application code. |

> **Also see**: [sqld-02: SQL vs NoSQL Decision Framework](19-sql-system-design-takeaways.md#sqld-02-sql-vs-nosql-decision-framework)
> **Dictionary**: [ACID Transactions](../reference-dictionary/data-concurrency.md#acid-transactions)
> **Taxonomy**: §4.0 Data Architecture Fundamentals, §4.1 Data Architecture

---

## db-09: ACID Guarantees Under Load

> **Source**: [§"ACID — What It Actually Means Under Load"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Candidates recite ACID but cannot connect it to real failure modes under concurrency. |
| **Root cause** | Treating ACID as a buzzword instead of a contract between the application and the database. |

**Strategy**: Map each property to a concrete guarantee:
- **Atomicity**: all operations commit or all roll back — no partial writes.
- **Consistency**: the database rejects writes that violate constraints.
- **Isolation**: concurrent transactions behave as if serialized (to a chosen degree).
- **Durability**: committed data survives crashes, usually via a write-ahead log.

| Tradeoff | Detail |
|:---|:---|
| **Stronger guarantees cost throughput** | Full serializability prevents anomalies but serializes execution; relaxing isolation increases concurrency at the risk of anomalies. |
| **Not all databases implement ACID the same way** | Defaults and durability settings vary by engine. |

> **Also see**: [tx-02: Isolation Levels](02-concurrency-transactions.md#tx-02-isolation-levels)
> **Dictionary**: [ACID Transactions](../reference-dictionary/data-concurrency.md#acid-transactions)
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## db-10: Indexing & Composite Indexes

> **Source**: [§"Indexing — Where Interviews Get Separated"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Queries that should be fast turn into full-table scans. |
| **Root cause** | Missing indexes, or composite indexes whose leading columns do not match the query filter order. |

**Strategy**: Add B-tree indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY` predicates. For multi-column filters, use a **composite index** with the most selective / most frequently filtered column first. The leading column must be present in the filter for the index to be usable.

| Tradeoff | Detail |
|:---|:---|
| **Read vs write cost** | Indexes turn O(n) scans into O(log n) lookups, but every write must update every relevant index. |
| **Storage** | Each index is a separate structure that consumes disk and memory. |

> **Also see**: [db-03: Composite Index vs. Separate Indexes](01-databases-query-performance.md#db-03-composite-index-vs-separate-indexes), [sql-05: EXPLAIN Before You Ship](14-sql-query-optimization.md#sql-05-explain-before-you-ship)
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## db-11: Scaling Reads — Read Replicas & Caching

> **Source**: [§"Scaling Reads"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Read traffic saturates the primary database. |
| **Root cause** | All `SELECT` traffic is routed to the single primary node. |

**Strategy**: Distribute read-only traffic to **read replicas** asynchronously replicated from the primary. For hot, cacheable data, add a **cache-aside** layer (Redis/Memcached) with a TTL so reads are served from memory.

| Tradeoff | Detail |
|:---|:---|
| **Replication lag** | A user may write to the primary and briefly not see the change on a replica. |
| **Cache invalidation** | Stale cache entries must be explicitly deleted or allowed to expire; otherwise reads return outdated data. |

> **Also see**: [sqld-01: The SQL Scaling Ladder](19-sql-system-design-takeaways.md#sqld-01-the-sql-scaling-ladder), [cache-02: Cache Invalidation](03-caching-architecture.md#cache-02-cache-invalidation)
> **Dictionary**: [Cache-Aside Pattern](../reference-dictionary/caching.md#cache-aside-pattern)
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## db-12: CAP Theorem — Partition Tradeoffs

> **Source**: [§"CAP Theorem — The Real Constraint"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Designing as if a distributed database can be fully consistent and fully available at all times. |
| **Root cause** | Ignoring network partitions, which are inevitable in distributed systems. |

**Strategy**: When a partition occurs, choose:
- **CP** (Consistency + Partition tolerance): reject writes to stay consistent (e.g., HBase, ZooKeeper).
- **AP** (Availability + Partition tolerance): keep serving reads/writes and accept stale data (e.g., Cassandra, DynamoDB).

There is no "CA" system in practice.

| Tradeoff | Detail |
|:---|:---|
| **CP** | Strong consistency but reduced availability during partitions. |
| **AP** | High availability but applications must tolerate stale reads and resolve conflicts later. |

> **Dictionary**: [CAP Theorem](../reference-dictionary/architecture-patterns.md#cap-theorem)
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## db-13: Sharding — Horizontal Partitioning & Hotspots

> **Source**: [§"Sharding — Split the Data, Multiply the Complexity"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | A single database instance cannot absorb the write volume. |
| **Root cause** | All writes are routed to one node whose CPU, memory, or IOPS ceiling has been reached. |

**Strategy**: Split data horizontally into **shards** using a shard key. Common strategies are hash sharding (even distribution), range sharding (efficient range queries), and geo sharding (data locality). Use **consistent hashing** to minimize key remapping when nodes are added or removed.

| Tradeoff | Detail |
|:---|:---|
| **Operational complexity** | Cross-shard joins and transactions become expensive or impossible; resharding is painful. |
| **Hotspots** | A skewed shard key can concentrate traffic on one shard, negating the benefit. |

> **Also see**: [db-05: Hot Partition Problem](01-databases-query-performance.md#db-05-hot-partition-problem), [api-05: Consistent Hash-Based Routing](04-api-network-design.md#api-05-consistent-hash-based-routing)
> **Dictionary**: [Sharding](../reference-dictionary/data-concurrency.md#sharding), [Consistent Hashing](../reference-dictionary/api-design.md#consistent-hashing)
> **Taxonomy**: §4.1 Data Architecture

---

## db-14: Isolation Levels

> **Source**: [§"Isolation Levels — The One Nobody Studies"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Concurrency anomalies (dirty reads, non-repeatable reads, phantom reads) corrupt application logic. |
| **Root cause** | Using the database default isolation level without checking whether it matches the workload's correctness requirements. |

**Strategy**: Choose the weakest level that still prevents the anomalies your workload cannot tolerate:
- **Read Uncommitted**: fastest, allows all anomalies.
- **Read Committed**: prevents dirty reads.
- **Repeatable Read**: prevents dirty and non-repeatable reads.
- **Serializable**: prevents all anomalies, slowest.

| Tradeoff | Detail |
|:---|:---|
| **Correctness vs performance** | Higher isolation removes anomalies but reduces concurrency and throughput. |
| **Defaults differ** | PostgreSQL defaults to Read Committed; MySQL InnoDB defaults to Repeatable Read. |

> **Also see**: [tx-02: Isolation Levels](02-concurrency-transactions.md#tx-02-isolation-levels)
> **Dictionary**: [Isolation Levels](../reference-dictionary/data-concurrency.md#isolation-levels)
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## db-15: Storage Engine Internals — B-Tree vs LSM-Tree, WAL & Bloom Filters

> **Source**: [§"Storage Internals That Show Up More Than You Think"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Storage engine choice is mismatched to the workload, producing unexpected latency or write amplification. |
| **Root cause** | Treating all databases as black boxes rather than understanding their on-disk structures. |

**Strategy**: Match the engine to the workload:
- **B-Tree** (Postgres, MySQL): read-optimized, in-place updates, random I/O — best for OLTP.
- **LSM-Tree** (Cassandra, RocksDB): write-optimized, append-only with compaction, sequential I/O — best for write-heavy workloads.
- **WAL** (Write-Ahead Log): every durable database uses it; changes are logged before they touch data files so crashes can replay.
- **Bloom filters**: probabilistic membership tests that skip unnecessary disk lookups for non-existent keys.

| Tradeoff | Detail |
|:---|:---|
| **B-Tree** | Fast reads, but updates may cause random I/O and write amplification. |
| **LSM-Tree** | Fast writes, but reads may check multiple levels and compaction creates I/O spikes. |
| **Bloom filter** | Can produce false positives, so a positive result still requires a disk check. |

> **Also see**: [uber-05: B-Tree vs LSM-Tree — Write-Heavy Workloads](06-uber-architecture-case-study.md#uber-05-b-tree-vs-lsm-tree--write-heavy-workloads)
> **Dictionary**: [B-Tree](../reference-dictionary/databases.md#b-tree), [LSM-Tree](../reference-dictionary/databases.md#lsm-tree), [Write-Ahead Log (WAL)](../reference-dictionary/databases.md#write-ahead-log-wal), [Bloom Filter](../reference-dictionary/databases.md#bloom-filter)
> **Taxonomy**: §4.1 Data Architecture

---

## db-16: Distributed Transactions — 2PC vs Saga

> **Source**: [§"Distributed Transactions — The Final Boss"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | A business operation must stay atomic across multiple services or databases. |
| **Root cause** | Database-per-service boundaries break single-ACID transactions. |

**Strategy**: Choose the coordination model that matches your consistency requirement:
- **Two-Phase Commit (2PC)**: a coordinator asks all participants to prepare, then commits. Gives strong consistency but the coordinator is a single point of failure and the protocol blocks on failures.
- **Saga pattern**: a sequence of local transactions with compensating actions. If step 3 fails, steps 2 and 1 are undone. Favors availability and eventual consistency.

| Tradeoff | Detail |
|:---|:---|
| **2PC** | Strong consistency, simple conceptual model, but blocking and fragile during partitions or coordinator failure. |
| **Saga** | Non-blocking and resilient, but requires carefully designed compensations and makes intermediate states visible. |

> **Also see**: [tx-04: Idempotency](02-concurrency-transactions.md#tx-04-idempotency), [sqld-06: Database per Service + Saga Pattern](19-sql-system-design-takeaways.md#sqld-06-database-per-service--saga-pattern)
> **Dictionary**: [Saga Pattern](../reference-dictionary/data-concurrency.md#saga-pattern), [Compensating Transaction](../reference-dictionary/data-concurrency.md#compensating-transaction), [Two-Phase Commit (2PC)](../reference-dictionary/data-concurrency.md#two-phase-commit-2pc)
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## db-17: Change Data Capture (CDC)

> **Source**: [§"Change Data Capture (CDC)"](../articles/medium/your-system-design-is-fine-your-database-decisions-are-why-youre-failing.md)

| | |
|:---|:---|
| **Problem** | Caches, search indexes, and analytics stores drift out of sync with the primary database. |
| **Root cause** | Polling is slow and expensive; dual-writes risk inconsistency under failure. |

**Strategy**: Use **log-based CDC** to stream every committed change from the database's transaction log (WAL, binlog) to downstream consumers via tools like Debezium and Kafka. Consumers update search indexes, analytics DBs, or invalidate caches in near real time.

| Tradeoff | Detail |
|:---|:---|
| **Near-real-time consistency** | Downstream stores are updated within seconds rather than minutes. |
| **Operational complexity** | Requires log connectors, schema evolution handling, and consumer idempotency. |

> **Also see**: [tx-07: Post-Commit Confirmation and Events](02-concurrency-transactions.md#tx-07-post-commit-confirmation-and-events)
> **Dictionary**: [Change Data Capture (CDC)](../reference-dictionary/data-concurrency.md#change-data-capture)
> **Taxonomy**: §4.3 Streaming & Real-Time Architecture
