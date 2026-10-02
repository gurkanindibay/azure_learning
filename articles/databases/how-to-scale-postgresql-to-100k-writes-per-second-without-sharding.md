---
type: Article
title: "How to Scale PostgreSQL to 100,000 Writes Per Second Without Sharding"
description: "Six single-node optimization levers — asynchronous commits, ingestion batching, HOT updates, WAL tuning, declarative partitioning, and hardware topology — that can push a single PostgreSQL primary past 100,000 writes per second before sharding becomes necessary."
generated: { by: process:format-agent, at: 2026-10-03T00:00:00+03:00 }
---

# How to Scale PostgreSQL to 100,000 Writes Per Second Without Sharding

> **Domain**: Databases — PostgreSQL write throughput optimization  
> **Parent**: [Databases — Source Articles](index.md)  
> **Takeaways**: [42. PostgreSQL Single-Node Write Scaling — Key Takeaways](../../system-design-architecture/databases/42-db-key-takeaways.md)

Before introducing multi-node sharding, modern hardware and deliberate tuning of PostgreSQL's engine mechanics can push a **single primary instance** past **100,000 writes per second**.

Achieving this requires eliminating disk sync bottlenecks, batching engine operations, reducing index update overhead, and tuning PostgreSQL's Write-Ahead Log (WAL).

---

## 1. Eliminate the Per-Write fsync Bottleneck

By default, PostgreSQL prioritizes durability over raw throughput. Every transaction commit executes an `fsync()` syscall, forcing disk platters or NVMe controller caches to flush WAL data to non-volatile storage before acknowledging success.

A fast NVMe drive can handle 10,000 to 40,000 IOPS. It cannot handle 100,000 individual blocking `fsync()` calls per second from independent threads.

### The Fix: Asynchronous Commits

If your application can tolerate losing a few milliseconds of data during a hard host crash (e.g., telemetry, events, activity feeds, metrics), enable **asynchronous commits**:

```sql
-- In postgresql.conf or session-level:
synchronous_commit = off
wal_writer_delay = 10ms
```

- When `synchronous_commit = off`, the transaction returns success immediately after the WAL record is written to PostgreSQL's in-memory WAL buffer, without waiting for the physical disk flush.
- The internal `walwriter` process flushes WAL blocks every `wal_writer_delay` (default 10ms) or when buffers fill.
- **Durability Trade-off:** Database consistency and crash recovery guarantees remain completely intact. A crash will not corrupt your database; you only risk losing unwritten commits from the last 10–20 ms interval.

---

## 2. Ingestion Batching: Ditch Single INSERT Statements

Executing 100,000 individual `INSERT INTO tbl VALUES (...)` statements creates 100,000 network round trips, SQL parses, and transaction boundary allocations per second. Even with persistent connection pools, this collapses application throughput.

### Strategy A: Multi-Value INSERT Batches

Aggregate incoming writes at the application layer (e.g., buffering in Redis or memory for 10ms or 500 records) and flush them as multi-row inserts:

```sql
INSERT INTO event_logs (device_id, event_type, payload, created_at)
VALUES
  (101, 'ping', '{"temp": 22}', NOW()),
  (102, 'alert', '{"temp": 85}', NOW()),
  -- ... up to 500-1,000 rows per batch
  (500, 'ping', '{"temp": 21}', NOW());
```

A batch of 1,000 rows incurs the parsing and transaction overhead of **one** query while committing 1,000 writes.

### Strategy B: The COPY Protocol (Maximum Throughput)

For sheer ingestion volume, the PostgreSQL streaming `COPY` protocol bypasses standard query parsing and execution planning entirely.

Using native driver stream APIs (like `pgcopy` in Go, `COPY FROM STDIN BINARY` in Node/Python, or `NpgsqlCopyBinaryImporter` in .NET), data streams directly into raw table pages:

```sql
COPY event_logs (device_id, event_type, payload, created_at)
FROM STDIN WITH (FORMAT binary);
```

Benchmark tests routinely show `COPY` streaming achieving 3x to 5x higher throughput compared to parameterized multi-row `INSERT` queries.

---

## 3. Prune Secondary Indexes & Leverage HOT Updates

Secondary indexes severely penalize write workloads. If a table contains five indexes, writing a single row requires updating the table's heap page plus **five separate B-Tree index pages**.

```
Single Row Write With 4 Secondary Indexes:
[Incoming Row]
  |-> Write to Table Heap Page
  |-> Update Index 1 (created_at B-Tree)
  |-> Update Index 2 (user_id B-Tree)
  |-> Update Index 3 (status B-Tree)
  +-> Update Index 4 (device_id B-Tree)
(Results in 5x write amplification and constant index page splits)
```

### Techniques to Minimize Index Amplification

- **Drop Low-Utility Secondary Indexes:** Keep write-heavy ingestion tables strictly minimal. Store high-frequency data with a primary key and at most one or two essential secondary indexes.
- **Lower Table `fillfactor` for HOT Updates (Heap-Only Tuples):** For high-frequency `UPDATE` operations, PostgreSQL's HOT optimization allows updates to stay inside the same data page without modifying secondary indexes, provided the updated column is not indexed:

```sql
-- Reserve 20% empty space on each table page for in-place updates:
ALTER TABLE active_sessions SET (fillfactor = 80);
```

---

## 4. WAL Buffer & Checkpoint Tuning

Default PostgreSQL configuration parameters are tailored for modest servers. Under a write load of 100,000 rows per second, default WAL configurations cause write freezes due to aggressive checkpointing.

Configure the following in `postgresql.conf`:

```ini
# Sizing WAL buffers to handle memory surges
wal_buffers = 64MB

# Increase maximum WAL volume between checkpoints to smooth out disk I/O
max_wal_size = 64GB
min_wal_size = 8GB

# Spread checkpoint writes over time to prevent disk I/O spikes
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
```

### Why This Matters

- **`max_wal_size`:** If set too low (e.g., default 1GB), intense write volume exhausts the threshold in seconds, triggering immediate forced checkpoints. This spikes disk write latency and stalls backend workers.
- **`checkpoint_completion_target = 0.9`:** Instructs the background checkpointer to spread dirty page writes across 90% of the `checkpoint_timeout` window, flattening the I/O curve.

---

## 5. Declarative Table Partitioning (Without Foreign Shards)

Native declarative partitioning is not sharding — it lives on a single PostgreSQL server instance while splitting a massive logical table into separate physical files on disk.

```sql
CREATE TABLE metric_streams (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    device_id INT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL,
    val DOUBLE PRECISION
) PARTITION BY RANGE (recorded_at);

-- Create daily partitions:
CREATE TABLE metrics_2026_09_19 PARTITION OF metric_streams
    FOR VALUES FROM ('2026-09-19 00:00:00+00') TO ('2026-09-20 00:00:00+00');
```

### Performance Advantages

- **Compact Working Index Sets:** Each day's partition retains small, dense B-Trees that fit completely inside `shared_buffers` (RAM), avoiding disk swapping during writes.
- **Instant Pruning (`DROP TABLE`):** Instead of executing slow, bloat-inducing `DELETE FROM metric_streams WHERE recorded_at < NOW() - INTERVAL '30 days'`, simply drop the old partition instantly with zero write overhead.

---

## 6. Hardware & Storage Topology

Pushing 100,000 writes/sec requires sufficient physical hardware bandwidth:

- **Storage:** Dedicated NVMe drives in RAID 10. Split the Write-Ahead Log (`pg_wal`) and the main database cluster (`base`) onto separate physical NVMe drives/controllers so checkpoint flushes never compete with WAL writes.
- **Connections:** Put a high-performance connection pooler like **PgBouncer** (transaction pooling mode) in front of PostgreSQL. PostgreSQL forks a full operating system process per connection; running thousands of open connections causes CPU context switching bottlenecks. Keep active server connections pinned between 50 and 100.

---

## Implementation Checklist

- [ ] Set `synchronous_commit = off` on high-throughput ingestion pipelines.
- [ ] Group row writes into 500–1,000 multi-value batches or use the binary `COPY` protocol.
- [ ] Strip unnecessary secondary indexes from ingestion-heavy tables.
- [ ] Expand `max_wal_size` to 32GB–64GB and set `checkpoint_completion_target = 0.9`.
- [ ] Separate `pg_wal` disk storage from main data storage.
- [ ] Route application traffic through PgBouncer using transaction pooling.
- [ ] Partition high-volume write tables by time ranges to keep active B-Trees resident in memory.

---

Exhaust these single-node optimization levers first. In most engineering workloads, PostgreSQL can comfortably handle enterprise-scale write volumes before distributed multi-node sharding ever becomes necessary.
