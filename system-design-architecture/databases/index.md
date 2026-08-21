---
type: Index
title: "Databases & Query Performance"
description: "System-design problems and strategies for database indexing, pagination, query optimization, SQL system design, and database technology decisions."
timestamp: 2026-06-27T00:00:00Z
---

# Databases & Query Performance

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies covering database indexing, query performance tuning, SQL system design patterns, and database technology selection decisions.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [query-performance.md](query-performance.md) | `db-01` – `db-07` | UUID indexing, Keyset pagination, Composite indexes, N+1 problem, Hot partitions, DB migration at scale, PostgreSQL 18 async I/O |
| [database-decisions.md](database-decisions.md) | `db-08` – `db-17` | SQL vs NoSQL, ACID, Scaling reads/writes, CAP theorem, Sharding, Isolation levels, Storage internals, Distributed transactions, CDC |
| [database-id-strategy.md](database-id-strategy.md) | `db-18` | External UUID/ULID vs internal auto-increment ID strategy |
| [sql-query-optimization.md](sql-query-optimization.md) | `sql-01` – `sql-05` | Index-aware design, SELECT columns, N+1 elimination, CTEs vs subqueries, EXPLAIN ANALYZE |
| [sql-system-design.md](sql-system-design.md) | `sqld-01` – `sqld-08` | Scaling ladder, SQL vs NoSQL, CQRS, Event Sourcing, Row-Level Security, DB per service + Saga, Performance checklist |
| [sharding-partitioning-strategies.md](sharding-partitioning-strategies.md) | `db-19` – `db-24` | Vertical partitioning, Shard key selection, Gene-based sharding with Snowflake ID, Cross-shard queries, Dual-write migration, Composite shard keys |
| [34-db-key-takeaways.md](34-db-key-takeaways.md) | `db-25` – `db-27` | PACELC theorem, Synchronous vs asynchronous replication, Quorum-based hybrid replication (R+W>N) |
| [35-db-key-takeaways.md](35-db-key-takeaways.md) | `db-28` – `db-30` | WAL-based CDC state machine, Replication slot lifecycle, Publication/subscription model for selective CDC |
| [36-db-key-takeaways.md](36-db-key-takeaways.md) | `db-31` – `db-33` | Random UUIDv4 B-tree fragmentation, Time-ordered keys (UUIDv7/ULID), 64-bit TSID/Snowflake vs 128-bit UUID trade-offs |
| [37-db-key-takeaways.md](37-db-key-takeaways.md) | `db-34` – `db-36` | Virtual thread connection storm, Multi-region pool sizing formula, Database backpressure & acquisition latency monitoring |


## Cross-References

- **Dictionary**: [Databases](../../reference-dictionary/databases.md), [Data/Concurrency](../../reference-dictionary/data-concurrency.md)
- **Azure**: [Azure Data Services](../../architecture-azure/data/)
- **Related**: [Concurrency & Transactions](../concurrency-transactions/), [Caching](../caching/)
- **Taxonomy**: §3.3 Data Architecture
