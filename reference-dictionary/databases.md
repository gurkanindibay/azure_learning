---
type: Reference
title: "Databases & Database Engines"
description: "Database engine internals, configuration parameters, and storage-layer concepts."
timestamp: 2026-06-18T00:00:00Z
---

# Databases & Database Engines

> **Domain**: Database engine internals, storage subsystem behavior, and configuration parameters that affect query execution.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| effective_io_concurrency | [`#effective-io-concurrency`](#effective-io-concurrency) |
| io_method | [`#io-method`](#io-method) |
| io_uring | [`#io-uring`](#io-uring) |
| pg_aios | [`#pg-aios`](#pg-aios) |
| shared_buffers | [`#shared-buffers`](#shared-buffers) |
| B-Tree | [`#b-tree`](#b-tree) |
| Bloom Filter | [`#bloom-filter`](#bloom-filter) |
| LSM-Tree | [`#lsm-tree`](#lsm-tree) |
| Write-Ahead Log (WAL) | [`#write-ahead-log-wal`](#write-ahead-log-wal) |
| Merkle Tree | [`#merkle-tree`](#merkle-tree) |
| Anti-Entropy | [`#anti-entropy`](#anti-entropy) |
| NoSQL | [`#nosql`](#nosql) |
| Hash Collision | [`#hash-collision`](#hash-collision) |
| Red-Black Tree | [`#red-black-tree`](#red-black-tree) |

---

## effective_io_concurrency {#effective-io-concurrency}

A PostgreSQL configuration parameter that tells the query planner how many disk I/O operations the storage layer can execute concurrently. In PostgreSQL 18 the default changed from `1` to `16`, reflecting the assumption that asynchronous I/O can overlap multiple reads.

### Key Characteristics
- Higher values let the planner choose plans that issue more parallel reads
- The optimal value depends on storage latency and throughput, not CPU count
- Only affects planning for read operations that benefit from overlapping I/O

### When to Use
- High-latency cloud volumes where queuing many reads hides round-trip time
- Analytical workloads with cold, scan-heavy queries

### When NOT to Use
- Single local NVMe devices that already saturate bandwidth with few concurrent reads
- Cached or index-bound transactional workloads where disk latency is not the bottleneck

**Also see**: [io_method](#io-method), [io_uring](#io-uring), [shared_buffers](#shared-buffers)

---

## io_method {#io-method}

A PostgreSQL 18 configuration parameter that selects the asynchronous I/O implementation used by the database backend. Changing it requires a server restart.

### Key Characteristics
- `worker` (default): dedicated background I/O processes; portable across operating systems
- `io_uring`: uses the Linux kernel's `io_uring` interface; typically fastest on recent Linux kernels
- `sync`: pre-18 synchronous behavior; escape hatch for regression testing or compatibility

### When to Use
- `worker` as the safe default everywhere
- `io_uring` on recent Linux when benchmarking confirms lower latency
- `sync` only when reproducing pre-18 behavior or investigating a regression

### When NOT to Use
- Do not switch to `io_uring` without a direct A/B benchmark on your workload
- Do not assume the default is wrong; measure first

**Also see**: [io_uring](#io-uring), [effective_io_concurrency](#effective-io-concurrency), [pg_aios](#pg-aios)

---

## io_uring {#io-uring}

A Linux kernel asynchronous I/O interface that lets user-space applications submit many I/O requests and collect completions through shared ring buffers, avoiding per-syscall overhead and enabling efficient overlap of disk latency.

### Key Characteristics
- Submission and completion queues are shared between user space and kernel space
- Supports read, write, and other operations beyond legacy `aio`
- Requires a recent Linux kernel and appropriate permissions

### When to Use
- High-throughput, latency-sensitive storage workloads on Linux
- PostgreSQL 18 deployments where benchmarking shows `io_method = 'io_uring'` outperforms `worker`

### When NOT to Use
- Non-Linux operating systems (use `worker` instead)
- Kernels without stable `io_uring` support
- Workloads where the bottleneck is not disk I/O latency

**Also see**: [io_method](#io-method), [effective_io_concurrency](#effective-io-concurrency)

---

## pg_aios {#pg-aios}

A system view introduced in PostgreSQL 18 that exposes runtime statistics about asynchronous I/O operations.

### Key Characteristics
- Shows in-flight and completed async I/O requests
- Useful for validating that async I/O is active during heavy queries
- Complements `EXPLAIN (ANALYZE, BUFFERS)` for I/O troubleshooting

### When to Use
- Verify async I/O behavior after changing `io_method` or `effective_io_concurrency`
- Correlate query latency with actual async I/O activity

### When NOT to Use
- Not a substitute for `EXPLAIN ANALYZE` for query-plan tuning
- Not meaningful for workloads using `io_method = 'sync'`

**Also see**: [io_method](#io-method), [effective_io_concurrency](#effective-io-concurrency)

---

## shared_buffers {#shared-buffers}

The region of memory PostgreSQL uses to cache table and index blocks. Data already present in `shared_buffers` can be served without reading from disk.

### Key Characteristics
- The primary PostgreSQL cache layer
- Persists across transactions and connections
- Tuned with `shared_buffers` in `postgresql.conf`; typical production values range from 25% to 40% of RAM

### When to Use
- Reduce disk reads for frequently accessed data
- Size large enough to hold hot working set

### When NOT to Use
- Not a query result cache; it caches raw blocks, not query outputs
- Oversizing can starve the OS page cache and hurt performance

**Also see**: [effective_io_concurrency](#effective-io-concurrency)

---

## B-Tree {#b-tree}

A balanced tree data structure that keeps data sorted and allows searches, sequential access, insertions, and deletions in logarithmic time. Most relational databases (PostgreSQL, MySQL, SQL Server) use B-Tree indexes as their default index type.

### Key Characteristics
- Self-balancing: all leaf nodes stay at the same depth, keeping lookups predictable
- Range-friendly: efficient for equality, range, and ordered scans
- Write amplification: updates may split pages and cause random I/O

### When to Use
- Read-heavy OLTP workloads with point lookups and range queries
- Workloads that need stable, predictable query latency

### When NOT to Use
- Append-only or log-like write-heavy workloads (LSM-Tree is usually better)
- Scenarios where sequential write throughput matters more than read latency

**Also see**: [LSM-Tree](#lsm-tree), [Write-Ahead Log (WAL)](#write-ahead-log-wal)

---

## Bloom Filter {#bloom-filter}

A space-efficient probabilistic data structure used to test whether an element is a member of a set. It can return **false positives** but never false negatives, so it is useful for avoiding unnecessary disk lookups.

### Key Characteristics
- Compact: uses a bit array plus multiple hash functions
- False positives possible, false negatives impossible
- No deletion of individual elements in the basic form

### When to Use
- Checking whether a key might exist before doing an expensive disk read (e.g., Cassandra, HBase, RocksDB)
- Reducing I/O in storage engines and caches

### When NOT to Use
- When exact membership is required (use a hash set instead)
- When the false-positive rate cannot be tolerated

**Also see**: [B-Tree](#b-tree), [LSM-Tree](#lsm-tree)

---

## LSM-Tree {#lsm-tree}

A **Log-Structured Merge-Tree** storage engine optimized for high write throughput. Writes are appended to an in-memory structure and later flushed to immutable disk files (SSTables), which are periodically compacted.

### Key Characteristics
- Append-only writes: sequential I/O, low write amplification for ingest-heavy workloads
- Tiered storage: memtable → immutable files → compacted SSTables
- Read amplification: a read may check multiple levels until the key is found

### When to Use
- Write-heavy workloads such as time-series, logging, and event stores
- Systems that need elastic horizontal write scaling (Cassandra, RocksDB, ScyllaDB)

### When NOT to Use
- Read-heavy OLTP with many small range queries (B-Tree is usually better)
- Workloads sensitive to compaction I/O spikes

**Also see**: [B-Tree](#b-tree), [Write-Ahead Log (WAL)](#write-ahead-log-wal), [Bloom Filter](#bloom-filter)

---

## Write-Ahead Log (WAL) {#write-ahead-log-wal}

A durability technique in which every database modification is written to an append-only log before it is applied to the actual data files. If the database crashes, it replays the log to recover committed changes.

### Key Characteristics
- Sequential append: fast to write and fsync
- Crash recovery: unapplied log records are replayed on startup
- Foundation for replication and CDC: many systems stream the WAL to replicas or change-capture consumers

### When to Use
- Any database that must guarantee durability (effectively all transactional stores)
- As the source of truth for replication and change data capture

### When NOT to Use
- Pure in-memory caches that explicitly tolerate data loss on restart
- Systems where durability is not a requirement

**Also see**: [B-Tree](#b-tree), [LSM-Tree](#lsm-tree), [Change Data Capture (CDC)](data-concurrency.md#change-data-capture)

---

## Merkle Tree {#merkle-tree}

A **hash tree** in which every leaf node is the hash of a data block and every non-leaf node is the hash of its children. It enables efficient comparison of large datasets by identifying the smallest divergent subtree instead of scanning every record.

### Key Characteristics
- **Logarithmic divergence detection**: compare root hashes first, then descend only into mismatched branches
- **Tamper evidence**: changing any leaf invalidates all parent hashes up to the root
- **Common in distributed databases**: Cassandra, Dynamo, Riak and Git all use Merkle-tree-like structures for repair or verification

### When to Use
- Verifying data integrity across replicas without full data transfer
- Synchronizing divergent datasets in distributed key-value stores

### When NOT to Use
- When data changes so frequently that tree comparisons are always stale
- For small datasets where a simple hash or direct comparison is cheaper

**Also see**: [Anti-Entropy](#anti-entropy), [Bloom Filter](#bloom-filter)

---

## Anti-Entropy {#anti-entropy}

The process of **detecting and repairing inconsistencies** between replicas in a distributed data store. It is essential for eventually consistent systems where writes may not immediately propagate to every node.

### Key Characteristics
- **Repair mechanisms**: read repair, hinted handoff, and Merkle-tree-based active repair
- **Eventual consistency helper**: speeds up convergence when replicas diverge due to partitions or failures
- **Proactive and reactive**: both background scrubbing and on-read reconciliation

### When to Use
- Distributed databases with replication and partition tolerance
- Systems where silent divergence is more dangerous than temporary inconsistency

### When NOT to Use
- Strongly consistent systems where writes are synchronously replicated (no divergence to repair)
- When repair traffic would itself overwhelm the cluster

**Also see**: [Merkle Tree](#merkle-tree), [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem)

---

## NoSQL {#nosql}

A broad category of data stores that **relax parts of the relational model** — typically schema rigidity, ACID guarantees or join support — to achieve horizontal scalability, flexible schemas or specialized access patterns.

### Key Characteristics
- **Variety of models**: key-value, document, wide-column, graph and time-series stores
- **Horizontal scaling**: designed to shard and replicate across commodity nodes
- **Trade-off spectrum**: from strongly consistent (etcd, Spanner) to eventually consistent (Cassandra, DynamoDB)

### When to Use
- High-write or high-volume workloads that exceed single-node SQL capacity
- Unstructured or rapidly evolving data models
- Geo-distributed deployments requiring tunable consistency

### When NOT to Use
- When complex joins, strong ACID transactions and referential integrity are core requirements
- As a default choice without understanding the consistency and operational trade-offs

**Also see**: [ACID Transactions](data-concurrency.md#acid-transactions), [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem), [Sharding](data-concurrency.md#sharding)

---

## Hash Collision {#hash-collision}

When **two distinct inputs produce the same hash value** and therefore map to the same bucket or slot in a hash-based data structure. Collisions are inevitable in any hash table (pigeonhole principle) and are handled by chaining, open addressing, or treeification.

### Key Characteristics

- **Inevitable** when the key space is larger than the hash space.
- **Handled by chaining**: store colliding entries in a linked list or tree inside the bucket.
- **Performance impact**: degrades average O(1) lookup toward O(n) as collisions cluster.

### When to Use

- N/A — collisions are a property of hash tables, not a choice. The design decision is how to mitigate them.

### When NOT to Use

- Do not ignore collision behavior when building hash tables for untrusted input.
- Do not rely on a small hash space for security-sensitive deduplication or lookups.

**Also see**: [HashMap](../reference-dictionary/java-jvm.md#hashmap), [Bloom Filter](#bloom-filter), [B-Tree](#b-tree)

---

## Red-Black Tree {#red-black-tree}

A **self-balancing binary search tree** that guarantees O(log n) insert, delete, and lookup by enforcing five color-based invariants, including that no two red nodes appear consecutively and every root-to-leaf path has the same number of black nodes.

### Key Characteristics

- **Self-balancing**: tree height stays logarithmic after insertions and deletions.
- **Less strictly balanced than AVL trees** but with faster insertion and deletion.
- **Used inside Java HashMap buckets** (Java 8+) to cap collision-chain lookup at O(log n).

### When to Use

- Sorted maps/sets where consistent O(log n) operations are needed (for example, `java.util.TreeMap`).
- Collision chains in hash tables where linked-list O(n) would be unacceptable.

### When NOT to Use

- When only immutable snapshots are needed and rebuild is cheap (a sorted array may be simpler).
- When a simpler data structure already meets performance requirements.

**Also see**: [HashMap](../reference-dictionary/java-jvm.md#hashmap), [Treeification](../reference-dictionary/java-jvm.md#treeification), [B-Tree](#b-tree)
