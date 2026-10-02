---
type: System Design
title: "PostgreSQL Single-Node Write Scaling — Key Takeaways"
description: "Architectural analysis of six single-node PostgreSQL write-throughput levers: asynchronous commits, ingestion batching (multi-value INSERT and COPY protocol), HOT updates via fillfactor, WAL buffer and checkpoint tuning, declarative partitioning, and NVMe/PgBouncer topology."
generated: { by: process:format-agent, at: 2026-10-03T00:00:00+03:00 }
---

# 42. PostgreSQL Single-Node Write Scaling — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)  
> **Source**: [How to Scale PostgreSQL to 100,000 Writes Per Second Without Sharding](../../articles/databases/how-to-scale-postgresql-to-100k-writes-per-second-without-sharding.md)

> **Also see**: [Query Performance & Optimization](query-performance.md) (`db-01`–`db-07`), [Database Decisions](database-decisions.md) (`db-08`–`db-17`), [Sharding & Partitioning Strategies](sharding-partitioning-strategies.md) (`db-19`–`db-24`), [Connection Pool Sizing & Contention](41-db-key-takeaways.md) (`db-50`–`db-54`)  
> **Dictionary**: [Write-Ahead Log (WAL)](../../reference-dictionary/databases.md#write-ahead-log-wal), [B-Tree Page Split](../../reference-dictionary/databases.md#b-tree-page-split), [Connection Pooling](../../reference-dictionary/databases.md#connection-pooling), [HOT Update](../../reference-dictionary/databases.md#hot-update), [Asynchronous Commit](../../reference-dictionary/databases.md#asynchronous-commit), [fillfactor](../../reference-dictionary/databases.md#fillfactor), [PostgreSQL COPY Protocol](../../reference-dictionary/databases.md#postgresql-copy-protocol), [Checkpoint](../../reference-dictionary/databases.md#checkpoint)  
> **Azure Services**: [Azure Database for PostgreSQL Flexible Server](../../architecture-azure/data/)  
> **Taxonomy Reference**: §3.3 Data Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`db-55`](#db-55-per-write-fsync-bottleneck-synchronous-commit-as-the-primary-write-throughput-ceiling) | Each individual transaction commit blocks on `fsync()`, capping throughput well below NVMe's theoretical IOPS ceiling | Set `synchronous_commit = off` for loss-tolerant workloads; the WAL writer batches flushes every `wal_writer_delay` (default 10 ms), trading a narrow durability window for 5–10× commit throughput |
| [`db-56`](#db-56-100000-individual-inserts-100000-round-trips-ingestion-batching-as-the-first-multiplier) | Inserting rows one at a time creates one network round trip, one SQL parse, and one transaction boundary per row, collapsing throughput under high write load | Switch to multi-value INSERT batches (500–1,000 rows) or the binary COPY protocol; COPY bypasses the SQL parser entirely and achieves 3–5× higher throughput than multi-row INSERT |
| [`db-57`](#db-57-secondary-index-write-amplification-every-index-multiplies-the-heap-write-cost) | A table with N secondary indexes multiplies the cost of each row write by N+1, causing index page splits and sustained high IOPS even for simple ingestion | Minimize secondary indexes on write-heavy tables; set `fillfactor < 100` to reserve space for HOT in-place updates that skip all index updates when the modified column is not indexed |
| [`db-58`](#db-58-aggressive-checkpointing-under-high-wal-volume-produces-forced-checkpoint-write-spikes) | Default `max_wal_size = 1 GB` exhausts in seconds under 100k writes/sec, triggering immediate forced checkpoints that stall all backend workers | Raise `max_wal_size` to 32–64 GB, extend `checkpoint_timeout` to 15 min, and set `checkpoint_completion_target = 0.9` to spread dirty-page I/O evenly across the timeout window |
| [`db-59`](#db-59-time-range-partitioning-keeps-active-b-trees-memory-resident-and-enables-instant-data-pruning) | A large monolithic table accumulates a massive B-Tree that spills from `shared_buffers` to disk, adding read I/O to every write and making data expiry prohibitively expensive | Use declarative RANGE partitioning by time; each partition's compact B-Tree fits in RAM, and old partitions are dropped instantly (`DROP TABLE`) with zero heap rewrite overhead |
| [`db-60`](#db-60-hardware-topology-separating-wal-and-data-storage-and-bounding-connections-via-pgbouncer) | Checkpoint flushes and WAL writes sharing the same NVMe controller compete for I/O bandwidth; thousands of idle PostgreSQL processes cause CPU context-switching overhead | Dedicate separate NVMe controllers to `pg_wal` and `base`; front PostgreSQL with PgBouncer in transaction pooling mode, keeping active backend connections at 50–100 |

---

## db-55: Per-Write fsync Bottleneck — Synchronous Commit as the Primary Write Throughput Ceiling

| | |
|:---|:---|
| **Problem** | PostgreSQL's default `synchronous_commit = on` executes an `fsync()` syscall for every transaction commit, forcing the kernel to flush WAL data to non-volatile storage before returning success to the client. A fast NVMe drive handles 10,000–40,000 IOPS; 100,000 independent blocking `fsync()` calls per second from separate threads saturate this budget long before application-layer write logic does. |
| **Root cause** | Every commit creates a hard dependency on physical persistence latency. Even with sub-millisecond NVMe drives, serialized per-commit fsyncs create a throughput ceiling that cannot be overcome by adding more CPU cores or RAM. |

**Strategy**: Enable `synchronous_commit = off` for loss-tolerant workloads (telemetry, event feeds, activity logs, metrics). The WAL writer process batches and flushes WAL blocks every `wal_writer_delay` (default 10 ms), reducing physical I/O calls by several orders of magnitude. Combine with `wal_buffers = 64MB` to absorb write bursts without premature flushes.

**Tradeoff**: Database structural consistency and crash-recovery guarantees are unchanged — `synchronous_commit = off` cannot cause database corruption. The only risk is losing up to 10–20 ms of committed-but-unflushed transactions if the host suffers a hard crash (power loss, kernel panic). Inappropriate for financial ledgers, payment records, or any domain where data loss is unacceptable.

**Cross-references**: [WAL Buffer & Checkpoint Tuning (db-58)](#db-58-aggressive-checkpointing-under-high-wal-volume-produces-forced-checkpoint-write-spikes), [Write-Ahead Log (WAL)](../../reference-dictionary/databases.md#write-ahead-log-wal), [Asynchronous Commit](../../reference-dictionary/databases.md#asynchronous-commit)

---

## db-56: 100,000 Individual INSERTs = 100,000 Round Trips — Ingestion Batching as the First Multiplier

| | |
|:---|:---|
| **Problem** | High-throughput applications that issue one `INSERT` per logical write create a per-row cost of: one network round trip, one SQL parse, one query plan, and one transaction boundary allocation. Even through a persistent connection pool, this overhead compounds across tens of thousands of concurrent writes and collapses application throughput before the database becomes the bottleneck. |
| **Root cause** | PostgreSQL's query execution cycle (parse → bind → execute → sync) has fixed overhead that doesn't amortize across a single-row insert. Each row pays the full cost individually. |

**Strategy**:

1. **Multi-value INSERT batches**: Buffer 500–1,000 rows at the application layer (a short time window or record count threshold) and submit a single multi-value INSERT statement. One round trip and one parse covers 1,000 writes.
2. **Binary COPY protocol**: For maximum throughput, use the `COPY … FROM STDIN WITH (FORMAT binary)` path, which completely bypasses the SQL parser, planner, and rewriter. Native driver libraries (`pgcopy` in Go, `NpgsqlCopyBinaryImporter` in .NET, `asyncpg` `copy_records_to_table` in Python) stream binary-encoded rows directly into heap pages. Benchmarks consistently show 3–5× higher throughput versus parameterized multi-row INSERT.

**Tradeoff**: Batching introduces application-level buffering logic and adds latency for individual writes (rows must accumulate before the flush fires). The binary COPY protocol sacrifices SQL-level error granularity; a constraint violation aborts the entire batch, requiring the application to retry with the offending row isolated.

**Cross-references**: [PostgreSQL COPY Protocol](../../reference-dictionary/databases.md#postgresql-copy-protocol), [Per-Write fsync (db-55)](#db-55-per-write-fsync-bottleneck-synchronous-commit-as-the-primary-write-throughput-ceiling)

---

## db-57: Secondary Index Write Amplification — Every Index Multiplies the Heap Write Cost

| | |
|:---|:---|
| **Problem** | A table with four secondary B-Tree indexes requires five distinct page writes per inserted row: one to the heap and one to each index leaf page. Under high write rates, index page splits cause cascading upper-level page splits, each generating additional dirty pages and WAL entries. The effective write IOPS consumed is N+1 times the logical insert rate. |
| **Root cause** | B-Tree indexes are separate on-disk structures; every indexed column value must be inserted into the corresponding B-Tree. Page splits — triggered when a leaf page fills — propagate upward through the tree, potentially rewriting multiple levels. |

**Strategy**:

1. **Minimize secondary indexes on write-heavy ingestion tables**: Retain only the primary key and indexes required by the write-path query itself. Defer analytical indexes to a read replica or a materialized view refresh schedule.
2. **HOT Updates via `fillfactor`**: Set `fillfactor = 80` (or lower) on tables with frequent `UPDATE` patterns. The reserved 20% slack space on each heap page allows PostgreSQL's Heap-Only Tuple (HOT) optimization to update a row in-place within the same page, skipping all secondary index updates for columns that are not indexed. HOT updates generate no index churn and no additional WAL index entries.

```sql
ALTER TABLE active_sessions SET (fillfactor = 80);
```

**Tradeoff**: Removing secondary indexes degrades read query performance on write-heavy tables; reads must perform sequential scans or rely on the primary key. Setting a low `fillfactor` wastes storage space (each page stores fewer rows at rest). HOT optimization only fires when the updated columns are not part of any index and there is space on the same page.

**Cross-references**: [HOT Update](../../reference-dictionary/databases.md#hot-update), [fillfactor](../../reference-dictionary/databases.md#fillfactor), [B-Tree Page Split](../../reference-dictionary/databases.md#b-tree-page-split)

---

## db-58: Aggressive Checkpointing Under High WAL Volume Produces Forced Checkpoint Write Spikes

| | |
|:---|:---|
| **Problem** | PostgreSQL's default `max_wal_size = 1 GB` is exhausted in seconds under 100,000 writes/sec, triggering immediate forced checkpoints. Each forced checkpoint writes every dirty shared-buffer page to disk synchronously, spiking disk write latency and stalling all backend workers during the I/O burst. The application experiences periodic write latency spikes that are difficult to diagnose as checkpoint-related. |
| **Root cause** | When WAL volume between two consecutive checkpoints exceeds `max_wal_size`, the checkpointer abandons its scheduled cadence and immediately flushes. This concentration of disk writes produces a sawtooth I/O pattern that saturates the NVMe write bandwidth. |

**Strategy**: Raise `max_wal_size` to 32–64 GB to allow WAL accumulation between checkpoints. Extend `checkpoint_timeout` to 15 minutes and set `checkpoint_completion_target = 0.9` so the checkpointer spreads dirty page writes across 90% of the timeout window (13.5 min), producing a flat I/O profile instead of periodic spikes. Increase `wal_buffers` to 64 MB to absorb burst writes into in-memory WAL buffers before they hit disk.

```ini
wal_buffers = 64MB
max_wal_size = 64GB
min_wal_size = 8GB
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
```

**Tradeoff**: Larger WAL sizes and longer checkpoint intervals increase crash recovery time; after a crash, PostgreSQL must replay more WAL records before becoming available. Disk space for WAL files increases proportionally to `max_wal_size`. Monitor checkpoint frequency with `pg_stat_bgwriter` to confirm forced checkpoints have been eliminated.

**Cross-references**: [Write-Ahead Log (WAL)](../../reference-dictionary/databases.md#write-ahead-log-wal), [Checkpoint](../../reference-dictionary/databases.md#checkpoint), [Per-Write fsync (db-55)](#db-55-per-write-fsync-bottleneck-synchronous-commit-as-the-primary-write-throughput-ceiling)

---

## db-59: Time-Range Partitioning Keeps Active B-Trees Memory-Resident and Enables Instant Data Pruning

| | |
|:---|:---|
| **Problem** | A single monolithic high-volume table accumulates billions of rows with a correspondingly massive B-Tree index that no longer fits in `shared_buffers`. Every write must navigate deep index levels that are evicted from RAM, adding random disk reads to an already I/O-bound write path. Data expiry via `DELETE WHERE recorded_at < cutoff` causes massive heap bloat, WAL amplification, and autovacuum pressure. |
| **Root cause** | B-Tree height grows logarithmically with table size. As index pages exceed `shared_buffers` capacity, cache eviction causes random I/O on the index path for every write. `DELETE` on large tables creates dead tuple bloat that must be cleaned by autovacuum, which competes for I/O bandwidth with active writes. |

**Strategy**: Use PostgreSQL native declarative RANGE partitioning by time column. Each daily (or weekly) partition is a separate physical heap and index file with a compact, dense B-Tree sized for the partition's row count. Active partition B-Trees fit entirely in `shared_buffers`, eliminating index-page disk reads from the write path. Old partitions are dropped instantly:

```sql
DROP TABLE metrics_2026_09_01;  -- instant, zero heap rewrite, zero WAL amplification
```

This is **not sharding** — all partitions live on the same PostgreSQL server instance and are accessed through the parent partitioned table without application-layer awareness.

**Tradeoff**: Cross-partition queries (especially date range scans spanning many partitions) have overhead from the partition pruner evaluating partition bounds. If queries frequently span many historical partitions, consider columnar storage or a dedicated OLAP system. Partition maintenance (creating future partitions, dropping expired ones) requires operational automation (pg_partman or custom cron jobs).

**Cross-references**: [Sharding & Partitioning Strategies](sharding-partitioning-strategies.md), [Database Decisions](database-decisions.md)

---

## db-60: Hardware Topology — Separating WAL and Data Storage, and Bounding Connections via PgBouncer

| | |
|:---|:---|
| **Problem** | When the WAL (`pg_wal`) and the main cluster data directory (`base`) share the same NVMe controller, checkpoint flush operations compete directly with WAL write operations for I/O bandwidth. Simultaneously, thousands of idle client connections each fork a dedicated PostgreSQL OS process, causing CPU context-switching overhead that degrades query throughput at high concurrency. |
| **Root cause** | PostgreSQL's process-per-connection architecture was designed for moderate concurrency. Each OS process consumes ~5–10 MB of RAM and incurs kernel scheduling overhead. WAL writes are sequential and latency-sensitive; checkpoint flushes are bursty and bandwidth-heavy — routing both through the same controller creates mutual interference. |

**Strategy**:
1. **Dedicated NVMe controllers**: Place `pg_wal` (WAL directory) on one physical NVMe drive and `base` (cluster data directory) on a separate NVMe drive or controller. This ensures checkpoint I/O never contends with WAL write I/O.
2. **PgBouncer in transaction pooling mode**: Place PgBouncer between the application and PostgreSQL. Keep active server-side PostgreSQL connections between 50 and 100 (matching available CPU cores × 2). PgBouncer multiplexes thousands of application connections onto this small pool, eliminating the process-fork and context-switching overhead. Use transaction pooling mode (not session pooling) to maximize multiplexing efficiency.

**Tradeoff**: Separate NVMe drives increase hardware cost. PgBouncer in transaction pooling mode prohibits the use of session-level features (prepared statements bound to session, `SET LOCAL`, advisory locks, `LISTEN/NOTIFY`) unless the application explicitly resets state between transactions. Monitor PgBouncer queue depth to detect pool saturation.

**Cross-references**: [Connection Pooling](../../reference-dictionary/databases.md#connection-pooling), [Connection Pool Sizing & Contention](41-db-key-takeaways.md) (`db-50`–`db-54`)
