---
type: Reference
title: "Databases & Database Engines"
description: "Database engine internals, configuration parameters, and storage-layer concepts."
generated: { by: process:okf-migrate, at: 2026-06-18T00:00:00Z }
---

# Databases & Database Engines

> **Domain**: Database engine internals, storage subsystem behavior, and configuration parameters that affect query execution.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| effective_io_concurrency | [`#effectiveioconcurrency`](#effectiveioconcurrency) |
| io_method | [`#iomethod`](#iomethod) |
| io_uring | [`#iouring`](#iouring) |
| pg_aios | [`#pgaios`](#pgaios) |
| QPS (Queries Per Second) | [`#qps`](#qps) |
| shared_buffers | [`#sharedbuffers`](#sharedbuffers) |
| B-Tree | [`#b-tree`](#b-tree) |
| Bloom Filter | [`#bloom-filter`](#bloom-filter) |
| LSM-Tree | [`#lsm-tree`](#lsm-tree) |
| Write-Ahead Log (WAL) | [`#write-ahead-log-wal`](#write-ahead-log-wal) |
| Merkle Tree | [`#merkle-tree`](#merkle-tree) |
| Anti-Entropy | [`#anti-entropy`](#anti-entropy) |
| NoSQL | [`#nosql`](#nosql) |
| Hash Collision | [`#hash-collision`](#hash-collision) |
| Red-Black Tree | [`#red-black-tree`](#red-black-tree) |
| Cardinality Estimation | [`#cardinality-estimation`](#cardinality-estimation) |
| Apache Cassandra | [`#apache-cassandra`](#apache-cassandra) |
| MongoDB | [`#mongodb`](#mongodb) |
| Masterless Architecture | [`#masterless-architecture`](#masterless-architecture) |
| Durability | [`#durability`](#durability) |
| HyperLogLog | [`#hyperloglog`](#hyperloglog) |
| Upsert | [`#upsert`](#upsert) |
| Snowflake ID | [`#snowflake-id`](#snowflake-id) |
| Composite Shard Key | [`#composite-shard-key`](#composite-shard-key) |
| Write Consolidation | [`#write-consolidation`](#write-consolidation) |
| Key Salting | [`#key-salting`](#key-salting) |
| Cursor Pagination | [`#cursor-pagination`](#cursor-pagination) |
| Partial Index | [`#partial-index`](#partial-index) |
| Connection Pooling | [`#connection-pooling`](#connection-pooling) |
| LSN (Log Sequence Number) | [`#lsn`](#lsn) |
| WALSender | [`#walsender`](#walsender) |
| Buffer Pool | [`#buffer-pool`](#buffer-pool) |
| B-Tree Page Split | [`#b-tree-page-split`](#b-tree-page-split) |
| UUIDv4 | [`#uuidv4`](#uuidv4) |
| UUIDv7 | [`#uuidv7`](#uuidv7) |
| ULID | [`#ulid`](#ulid) |
| TSID | [`#tsid`](#tsid) |
| Connection Storm | [`#connection-storm`](#connection-storm) |
| Connection Acquisition Latency | [`#connection-acquisition-latency`](#connection-acquisition-latency) |
| Database Backpressure | [`#database-backpressure`](#database-backpressure) |
| Skip List | [`#skip-list`](#skip-list) |
| Ticket Server | [`#ticket-server`](#ticket-server) |
| Inverted Index | [`#inverted-index`](#inverted-index) |
| KSUID | [`#ksuid`](#ksuid) |
| Trie (Prefix Tree) | [`#trie-prefix-tree`](#trie-prefix-tree) |
| SimHash | [`#simhash`](#simhash) |
| Non-Blocking Incremental Snapshot | [`#non-blocking-incremental-snapshot`](#non-blocking-incremental-snapshot) |
| CDC Tombstone | [`#cdc-tombstone`](#cdc-tombstone) |
| LSN Lag | [`#lsn-lag`](#lsn-lag) |
| Monotonic Timestamp Guard | [`#monotonic-timestamp-guard`](#monotonic-timestamp-guard) |
| Low-Watermark / High-Watermark | [`#low-watermark-high-watermark`](#low-watermark-high-watermark) |

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

## QPS (Queries Per Second) {#qps}

A performance metric that measures how many database queries (reads, writes, or mixed) a system can handle per second. QPS is the primary throughput indicator for OLTP workloads and is commonly used in capacity planning, benchmarking, and SLO definitions.

### Key Characteristics
- **Read vs. write asymmetry**: read QPS and write QPS are measured separately because writes involve durability overhead (fsync, WAL, replication)
- **Latency-dependent**: QPS is meaningful only when paired with a latency percentile (e.g., "10,000 QPS at p99 < 10 ms"); raw QPS without latency context is misleading
- **Connection pooling matters**: max QPS is often gated by connection-pool size, not CPU; too few connections underutilize the database, too many cause contention
- **Linear scaling range**: QPS scales near-linearly with resources until a bottleneck (CPU, disk I/O, lock contention) saturates

### When to Use
- Capacity planning: estimating how many instances are needed for a target workload
- Benchmarking: comparing database engines, configurations, or hardware (e.g., `pgbench`, `sysbench`)
- SLO/SLA definitions: committing to a throughput ceiling with an accompanying latency bound
- Autoscaling triggers: scaling out when QPS approaches a predefined threshold

### When NOT to Use
- As a standalone metric without latency context — high QPS with high p99 latency is a failing system
- For analytical/OLAP workloads where throughput is better measured in bytes scanned per second or query completion time
- Comparing across fundamentally different workloads (point-lookup QPS ≠ join-heavy QPS)

**Also see**: [shared_buffers](#shared-buffers), [effective_io_concurrency](#effective-io-concurrency), [Durability](#durability)

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

---

## Cardinality Estimation {#cardinality-estimation}

The problem of counting the number of **distinct elements** in a multiset (stream, table column, or dataset). Exact solutions require O(n) memory; probabilistic estimators like HyperLogLog achieve O(1) memory with ~1% error.

### Key Characteristics
- **Exact counting** requires storing every distinct element seen so far — memory scales linearly with cardinality
- **Probabilistic estimation** uses hashing and statistical observation (e.g., leading zeros, bit patterns) to estimate count without storing elements
- **Common estimators**: HyperLogLog (Redis, PostgreSQL), HyperLogLog++ (Google BigQuery), K-Minimum Values (KMV)
- **Real-world use**: Every `COUNT(DISTINCT)` in analytics dashboards at scale is approximate

### When to Use
- Analytics dashboards showing unique users, sessions, or events
- Database query planners estimating result set sizes (PostgreSQL uses HLL internally)
- Network monitoring (unique IPs, unique endpoints)
- Streaming data where buffering all distinct elements is impossible

### When NOT to Use
- Exact counts required for billing, compliance, or financial reporting
- Small datasets where exact counting fits comfortably in memory
- When you need to list or retrieve the actual distinct elements

### Also see
- [HyperLogLog](databases.md#hyperloglog) · [Bloom Filter](#bloom-filter) · [B-Tree](#b-tree)

---

## Apache Cassandra

**Apache Cassandra** — a distributed, masterless NoSQL database designed for high write throughput and continuous availability across multiple regions. Every node is equal: any node can accept writes, any node can serve reads, and there is no single point of failure. Node failures reduce capacity but do not halt the system.

### Key Characteristics
- **Masterless / peer-to-peer architecture**: No primary node — all nodes are equal peers in a ring topology
- **Tunable consistency**: Per-operation consistency level (ANY, ONE, QUORUM, ALL) lets you trade consistency for availability at the query level
- **Linear scalability**: Adding nodes increases capacity linearly; no single bottleneck
- **Multi-region native**: Data can be replicated across regions with local reads and writes; no region is "in charge"
- **Write-optimized**: Append-only commit log + memtable → SSTable design favors writes over complex reads

### When to Use
- High-write-throughput systems where write availability must never pause (streaming, IoT, time-series)
- Multi-region deployments where users expect local-latency reads and writes
- Workloads with known, simple access patterns (key-value lookups, time-range scans) — no ad-hoc joins or aggregations

### When NOT to Use
- Workloads requiring ad-hoc queries, complex joins, or rich aggregations (use SQL or MongoDB)
- Systems where strong consistency is non-negotiable during network partitions (fintech, banking)
- Small datasets where operational complexity of Cassandra outweighs its scaling benefits

### Also see
- [Masterless Architecture](#masterless-architecture) · [Eventual Consistency](../reference-dictionary/cqrs-event-driven.md#eventual-consistency) · [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem) · [MongoDB](#mongodb)

---

## MongoDB

**MongoDB** — a document-oriented NoSQL database that uses a single-primary replication model. One primary node accepts all writes; secondary nodes replicate and can serve reads. When the primary fails, an election selects a new primary — during this pause, writes are blocked.

### Key Characteristics
- **Document model**: JSON-like documents (BSON) with schema flexibility — one document per entity with nested sub-documents
- **Single-primary replication**: Writes always go to the primary; secondaries replicate via oplog
- **Rich query language**: Supports joins (`$lookup`), aggregations, secondary indexes, and ad-hoc queries
- **Leader election**: When the primary fails, an automated election (typically 5–30 seconds) selects a new primary; writes are unavailable during election
- **Horizontal scaling via sharding**: Distributes data across shards by shard key; each shard is its own replica set

### When to Use
- Rapidly evolving schemas where business requirements change frequently
- Document-shaped data (user profiles, loan applications, catalogs) where one document = one entity
- Applications that benefit from rich ad-hoc queries and aggregations

### When NOT to Use
- Systems where write availability during node failure is critical — the election pause is a real operational concern
- Multi-region write-everywhere deployments — primary must be in one region; cross-region writes add latency
- Workloads requiring complex multi-document ACID transactions at high throughput (use SQL)

### Also see
- [Apache Cassandra](#apache-cassandra) · [Masterless Architecture](#masterless-architecture) · [Database Per Service](architecture-patterns.md#database-per-service)

---

## Masterless Architecture

**Masterless Architecture** — a distributed system design where every node is an equal peer with no designated leader. Any node can accept writes and serve reads; node failures reduce total capacity but do not require leader election or halt operations.

### Key Characteristics
- **Peer-to-peer topology**: All nodes share the same role — no primary, no standby, no hierarchy
- **No leader election**: When a node fails, the remaining nodes continue operating without pausing to elect a new leader
- **Graceful degradation**: Failure reduces throughput by ~1/N (where N = node count) rather than causing a full write stall
- **Gossip protocol**: Nodes discover topology and health via peer-to-peer gossip, not a central coordinator

### When to Use
- Write-availability-critical systems where any pause in write acceptance is unacceptable (streaming, CDN control planes)
- Multi-region deployments where no single region can be the write authority
- Systems that must survive arbitrary node failures without operator intervention

### When NOT to Use
- Systems requiring strong consistency guarantees (ACID transactions across nodes) during network partitions
- Small deployments (3–5 nodes) where the operational complexity of masterless coordination outweighs the availability benefit
- Workloads that depend on global ordering or strict serializability

### Also see
- [Apache Cassandra](#apache-cassandra) · [Eventual Consistency](../reference-dictionary/cqrs-event-driven.md#eventual-consistency) · [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem) · [Active-Active](deployment-patterns.md#active-active)

---

## Durability

**Durability** is the guarantee that once a write operation has been acknowledged as successful, the data will persist and survive system failures (power loss, crashes, restarts). It is the "D" in ACID transactions and a fundamental property of any system that cannot afford data loss.

### Key Characteristics
- **Write-ahead logging (WAL)**: Changes are recorded in an append-only log before being applied, enabling recovery after crashes
- **Replication**: Data is copied to multiple nodes/disks so no single failure loses committed writes
- **fsync/Flush**: The system forces data to durable storage (disk) before acknowledging the write to the client — in-memory acknowledgment is NOT durability
- **Separate from availability**: A system can be durable but unavailable (e.g., during recovery); durability guarantees that data will eventually be accessible

### When to Use
- Financial systems where lost transactions are unacceptable
- Event pipelines where every event must be recoverable (Kafka's `acks=all`, replication factor ≥ 3)
- Any system where the cost of data loss exceeds the cost of durability mechanisms

### When NOT to Use
- Ephemeral caches where data is reconstructed from a durable source on restart (Redis as cache, not as primary store)
- Real-time metrics where occasional data loss is acceptable and throughput is prioritized
- Prototypes and experiments where simplicity outweighs data safety

### Also see
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency) · [Event Sourcing](../reference-dictionary/cqrs-event-driven.md#event-sourcing) · [Consistency](../reference-dictionary/data-concurrency.md)
## HyperLogLog {#hyperloglog}

A **probabilistic cardinality estimator** that counts unique elements in a multiset using O(M) memory regardless of dataset size — typically ~12 KB for Redis-grade accuracy (<1% error). Based on the observation that the maximum number of leading zeros in hashed values estimates cardinality.

### Key Characteristics
- **Bounded memory**: Uses `M` buckets (e.g., 16,384 in Redis), each storing a small integer (6 bits); total memory is fixed regardless of input size
- **Harmonic mean aggregation**: Uses harmonic mean across buckets to naturally dampen outlier bias — no need to discard extreme values like predecessor algorithms (SuperLogLog)
- **Mergeable**: Multiple HLL structures can be combined (union) without loss of accuracy — PFMERGE takes the max of corresponding buckets
- **Standard error**: $1.04 / \sqrt{M}$ — with M=16,384, approximately 0.81%
- **Not enumerable**: You cannot retrieve which elements were added, only the estimated count

### When to Use
- Approximate unique counts over massive datasets (analytics dashboards, real-time monitoring)
- When memory efficiency is critical and 1-2% error is acceptable
- Merging unique counts across time windows or dimensions (daily → weekly → monthly)
- Built-in support in Redis (PFADD/PFCOUNT/PFMERGE), PostgreSQL, and Cassandra

### When NOT to Use
- Exact counts required (billing, voting, legal compliance, financial ledgers)
- Dataset is small enough to count exactly in memory (<100K unique items)
- You need to enumerate or retrieve the actual unique elements
- Error tolerance is below 0.5%

### Also see
- [Cardinality Estimation](../databases.md#cardinality-estimation) · [Bloom Filter](../databases.md#bloom-filter) · [Morris Probabilistic Counter](../caching.md#morris-probabilistic-counter) · [Redis Internals Takeaways](../../system-design-architecture/caching/redis-internals.md#cache-12)

---

## Upsert

A database operation that **inserts a row if it does not exist, or updates it if it does** — a portmanteau of "update" and "insert." Upserts are a key building block for idempotent consumers because replaying the same upsert produces the same final state without errors or duplicate rows.

### Key Characteristics
- **Atomic**: The insert-or-update decision is made atomically at the database level — no read-modify-write race
- **Conflict detection**: Uses a unique constraint or primary key to determine whether the row already exists
- **SQL syntax**: `INSERT ... ON CONFLICT (key) DO UPDATE SET ...` (PostgreSQL/SQLite), `MERGE` (SQL Server), `REPLACE` (MySQL), `INSERT ... ON DUPLICATE KEY UPDATE` (MySQL)
- **Idempotent by design**: The same upsert executed N times produces the same row state — no constraint violations, no duplicates

### When to Use
- Idempotent event consumers where replay should overwrite state, not fail
- Data synchronization pipelines where the source of truth is eventually reflected
- Cache refresh patterns where missing entries are populated and stale entries are updated

### When NOT to Use
- When the target state is not stable across replays (e.g., `EXCLUDED.updated_at = NOW()` changes each time)
- When the upsert would overwrite newer data with stale data from a delayed message — pair with version checks or `GREATEST` logic
- When INSERT-only with constraint-violation handling provides clearer auditability of which events were duplicates

### Also see
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency) · [Atomic Conditional Update](../reference-dictionary/data-concurrency.md#atomic-conditional-update) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer)

---

## Snowflake ID

A 64-bit distributed unique identifier originally developed by Twitter, composed of a timestamp (41 bits), a worker/node ID (10 bits), and a sequence number (12 bits). Snowflake IDs are time-sortable, require no central coordinator, and can be generated at very high throughput (~4M IDs/second per worker).

### Key Characteristics
- **64-bit integer**: Compact and index-friendly compared to UUID (128 bits)
- **Time-sortable**: Roughly ordered by creation time — the timestamp is in the high bits
- **Decentralized generation**: Each worker generates IDs independently using its assigned worker ID
- **Customizable bit layout**: The standard layout can be modified — e.g., replacing worker bits with a shard "gene" for routing

### When to Use
- Distributed systems needing unique, roughly time-ordered IDs without coordination
- Order systems, social media posts, any entity that benefits from sortable primary keys
- When UUID size (128-bit) is too large for the storage/index budget

### When NOT to Use
- When cryptographically random IDs are required (use UUIDv4 or random tokens)
- When global total ordering is needed (Snowflake IDs are roughly ordered, not strictly sequenced)
- When worker ID assignment and clock synchronization are too operationally complex

### Also see
- [KSUID](#ksuid) · [Shard Key](data-concurrency.md#shard-key) · [Gene-Based Sharding](data-concurrency.md#gene-based-sharding) · [Database ID Strategy](../system-design-architecture/databases/database-id-strategy.md)

---

## Composite Shard Key

A shard key composed of two or more columns combined to determine shard placement. Composite keys address the hotspot problem by spreading data from a high-traffic entity (e.g., a popular merchant) across multiple shards, while still allowing efficient single-shard queries when all key components are known.

### Key Characteristics
- **Multi-column routing**: `hash(column_a + column_b) % N` distributes data across shards
- **Hotspot mitigation**: A single dimension (e.g., `merchant_id`) that would concentrate traffic is combined with a high-cardinality dimension (e.g., `user_id`)
- **Query tradeoff**: Queries on the full composite key hit one shard; queries on only one component require scatter-gather

### When to Use
- Flash sale or peak-traffic scenarios where single-column shard keys create hotspots
- Systems where one entity (merchant, tenant, region) generates disproportionate write volume

### When NOT to Use
- When all queries naturally include a single, well-distributed key — composite adds complexity with no benefit
- When the composite key components are not available at query time for the dominant access pattern

### Also see
- [Shard Key](data-concurrency.md#shard-key) · [Data Skew](data-architecture.md#data-skew) · [Sharding](data-architecture.md#sharding) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)

---

## Write Consolidation

A write-optimization pattern that **buffers and batches individual writes in application-layer memory** before executing a single bulk write to the database. Instead of issuing N individual INSERT/UPDATE statements for N events, the application accumulates them and flushes in batches — reducing database round-trips, connection overhead, and transaction count.

### Key Characteristics
- **Application-layer batching**: Writes are accumulated in an in-memory buffer (array, ring buffer) and flushed on a timer or threshold
- **Reduced database load**: 1,000 individual INSERTs become 1 bulk INSERT, dramatically reducing I/O and transaction log overhead
- **Tradeoff: durability window**: Data in the buffer but not yet flushed can be lost on process crash

### When to Use
- High-throughput write workloads where individual writes would overwhelm the database (e.g., clickstream ingestion, IoT telemetry, log collection)
- Mitigating hot-partition write pressure — buffer writes to the hot shard and flush in controlled batches
- Systems using LSM-Tree databases (Cassandra, RocksDB) where bulk writes leverage sequential I/O efficiency

### When NOT to Use
- When write durability is critical and loss of unflushed data is unacceptable — write directly to the database or use a write-ahead log
- When write latency must be minimal (real-time systems) — batching adds intentional delay
- When the database already has efficient client-side batching (many drivers batch automatically)

### Also see
- [Hot Partition](../messaging.md#hot-partition) · [Write-Ahead Buffer](../messaging.md#write-ahead-buffer) · [LSM-Tree](#lsm-tree) · [B-Tree](#b-tree)

---

## Key Salting

A **partition-hotspot mitigation technique** where a random suffix ("salt") is appended to the partition key of high-traffic entities, causing their data to spread across multiple physical shards. Reads on a salted key require querying all possible salt values and merging results (scatter-gather). This trades read complexity for write distribution when a single logical key generates disproportionate load.

```
Without salting:
  hash("celebrity_user_42") → Shard 3 (all load on one shard)

With salting (salt range 0-3):
  hash("celebrity_user_42#0") → Shard 3
  hash("celebrity_user_42#1") → Shard 5
  hash("celebrity_user_42#2") → Shard 7
  hash("celebrity_user_42#3") → Shard 1
```

### Key Characteristics
- **Salt cardinality tradeoff**: More salt values → better write distribution but more expensive reads (must query all salts)
- **Hot-key identification prerequisite**: You must first detect which keys are hot before applying salting — salting every key wastes read performance
- **Deterministic salt assignment**: The salt value for a given key must be consistent (e.g., `hash(key) % N`) so writes and reads route to the same shards

### When to Use
- Celebrity-user problems: a single user account generates orders of magnitude more traffic than average
- Flash-sale or peak-traffic scenarios where specific product/merchant IDs become hot
- Any partition-key distribution that appears uniform by key count but is skewed by per-key load

### When NOT to Use
- When the hot-key problem doesn't exist — salting adds unnecessary scatter-gather overhead
- When reads must be single-shard for latency guarantees — the scatter-gather cost may be unacceptable
- When the database natively handles hot partitions (e.g., Cosmos DB automatic partitioning, Cassandra virtual nodes)

### Also see
- [Hot Partition](messaging.md#hot-partition) · [Composite Shard Key](#composite-shard-key) · [Shard Key](data-concurrency.md#shard-key) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)


---

## Cursor Pagination

A pagination technique that encodes the position of the last returned row into an opaque token (cursor) and uses it as the starting point for the next query — `WHERE (created_at, id) < (cursor_val1, cursor_val2) ORDER BY ... DESC LIMIT N`. Unlike offset pagination, cursor pagination uses an index seek rather than scanning and discarding earlier rows, providing stable O(log N) performance regardless of page depth.

### Key Characteristics
- **Stable performance**: Uses index seek — page 1 and page 1000 have the same query cost; no scanning of skipped rows
- **Insert/delete stability**: A cursor points to a fixed position in the data; new rows inserted ahead of the cursor don't shift results (no duplicates or misses)
- **Opaque token**: The cursor value is typically base64-encoded and should be treated as opaque by the client — the server owns cursor format and interpretation
- **No jump-to-page-N**: Cursor pagination only supports forward/backward navigation; random page access requires keyset pagination or offset fallback

### When to Use
- Infinite scroll, live feeds, and real-time data streams where deep pages are common
- APIs serving mobile clients that load data progressively
- High-traffic endpoints where offset pagination would degrade at scale (50M+ rows)

### When NOT to Use
- Admin dashboards requiring jump-to-page-N navigation — use keyset pagination or accept offset for small datasets
- Static datasets where offset pagination with a covering index is sufficient
- When the sort column is not unique — add a tiebreaker column (e.g., `id`) to the cursor to avoid gaps

### Also see
- [Pagination (Cursor vs Offset)](../api-design.md#pagination-cursor-vs-offset) · [B-Tree](#b-tree) · [Index Scan](#index-scan)

---

## Partial Index

A database index built over a filtered subset of rows defined by a `WHERE` clause — `CREATE INDEX ... ON events (tenant_id, created_at) WHERE event_type = 'signup' AND created_at > now() - interval '7 days'`. Only rows matching the predicate are indexed, so most writes bypass the index entirely while the frequently queried subset still benefits from fast index access.

### Key Characteristics
- **Conditional indexing**: Only rows satisfying the `WHERE` clause are included — reduces index size and write maintenance cost
- **Query planner awareness**: The planner uses the partial index when the query's `WHERE` clause matches or is more restrictive than the index predicate
- **Write bypass**: Rows not matching the predicate are inserted without updating the partial index — critical for high-ingest tables where full-index maintenance would bottleneck writes
- **Predicate-dependent**: If query patterns change (e.g., 7-day window becomes 30-day), the index may need rebuilding with an updated predicate

### When to Use
- High-ingest tables (8K+ inserts/sec) where only a small subset of rows (~0.2%) is frequently queried
- Soft-delete patterns: index only `WHERE deleted_at IS NULL` to keep active-row queries fast without indexing deleted rows
- Multi-tenant systems where one tenant's data dominates queries but not writes

### When NOT to Use
- When the filtered subset represents a large fraction of the table — the index maintenance savings are negligible
- When query patterns are diverse and unpredictable — a full composite index may serve more use cases
- When the predicate changes frequently — rebuilding partial indexes adds operational overhead

### Also see
- [Composite Index](#composite-index) · [Covering Index](#covering-index) · [B-Tree](#b-tree) · [Write Amplification](#write-amplification)

---

## Connection Pooling

A technique where a pool of pre-established database connections is maintained and reused across client requests, avoiding the overhead of opening a new TCP connection and performing authentication for every query. A pooler (e.g., PgBouncer) sits between the application and the database, multiplexing many lightweight client connections onto fewer heavyweight backend connections.

### Key Characteristics
- **Connection multiplexing**: Many client connections share a small pool of real database connections — critical when `max_connections` is limited (e.g., RDS defaults)
- **Pool modes**: Transaction mode returns connections to the pool after each transaction (best for stateless REST); Session mode pins one client to one backend for the full session (required for temp tables, prepared statements, `SET` commands)
- **Startup cost avoidance**: TCP handshake, TLS negotiation, and authentication are paid once at pool startup, not per request
- **Resource bounding**: Prevents connection exhaustion — without pooling, N app servers × M connections each can easily exceed database limits

### When to Use
- Any production application with more than a handful of concurrent database clients
- Serverless environments (Lambda) where cold starts would otherwise create connection storms
- Mixed workloads (short REST requests + long analytics jobs) that need different pooling strategies

### When NOT to Use
- Single-user applications or scripts with one connection at a time
- When the application already uses a framework-level connection pool (HikariCP, Sequelize pool) — add PgBouncer when you need cross-application multiplexing
- Embedded databases (SQLite) where connections are in-process and pooling adds unnecessary indirection

### Also see
- [max_connections](#maxconnections) · [Transaction Mode](#transaction-mode) · [Session Mode](#session-mode)

## LSN (Log Sequence Number) {#lsn}

A monotonically increasing byte offset within PostgreSQL's Write-Ahead Log (WAL) stream that uniquely identifies the position of every WAL record. LSNs are the foundational coordination primitive for durability, replication, and crash recovery in PostgreSQL.

### Key Characteristics
- Represents a **byte offset** within the WAL stream, not a timestamp
- Uniquely identifies the position of every change (INSERT, UPDATE, DELETE, COMMIT)
- Used to coordinate **durability** (WAL must be flushed to at least the COMMIT record's LSN), **replication** (subscribers report their flushed LSN), and **recovery** (replay WAL from the last checkpoint's LSN)
- Three critical LSNs govern replication slots: `confirmed_flush_lsn` (subscriber's durable point), `restart_lsn` (oldest WAL needed for safe decoding), and the commit LSN (the LSN of a transaction's COMMIT record)

### When to Use
- Debugging replication lag by comparing `confirmed_flush_lsn` to current WAL write position
- Configuring point-in-time recovery (PITR) targets
- Understanding WAL retention pressure: the gap between `restart_lsn` and `confirmed_flush_lsn` represents WAL that must be retained

### When NOT to Use
- As a timestamp replacement — LSN is a byte offset, not wall-clock time
- For cross-cluster comparison — LSNs are local to each PostgreSQL cluster

### Also see
- [Write-Ahead Log (WAL)](#write-ahead-log-wal) · [Replication Slot](../reference-dictionary/data-architecture.md#replication-slot) · [Logical Replication](../reference-dictionary/data-architecture.md#logical-replication)

## WALSender {#walsender}

A dedicated PostgreSQL backend process that drives logical (and physical) replication by reading WAL records from `pg_wal/`, passing them through the logical decoding machinery, and streaming decoded transactions to subscribers.

### Key Characteristics
- Spawned when a subscriber issues `START_REPLICATION SLOT <slot> LOGICAL <lsn>`
- Reads WAL records **sequentially** from the slot's `confirmed_flush_lsn` using XLogReader
- Passes each record to `LogicalDecodingProcessRecord()` for decoding
- Processes subscriber **feedback messages** to advance the replication slot's `confirmed_flush_lsn`
- One WALSender process per active replication connection

### When to Use
- Understanding replication throughput bottlenecks — the WALSender is the read side of the CDC pipeline
- Debugging why replication has stalled: if the WALSender is active but not advancing, the bottleneck is likely downstream (ReorderBuffer spill, slow subscriber apply)

### When NOT to Use
- As a general-purpose WAL reader — WALSender is tied to a replication slot and streams to a specific subscriber
- For offline WAL analysis — use `pg_waldump` instead

### Also see
- [Write-Ahead Log (WAL)](#write-ahead-log-wal) · [LSN](#lsn) · [Logical Replication](../reference-dictionary/data-architecture.md#logical-replication) · [Replication Slot](../reference-dictionary/data-architecture.md#replication-slot)

---

## Buffer Pool {#buffer-pool}

A dedicated region of system memory (RAM) managed directly by a database engine (e.g., PostgreSQL `shared_buffers`, MySQL `innodb_buffer_pool_size`) used to cache data pages and index pages, avoiding physical disk I/O for read and write operations.

### Key Characteristics
- Caches fixed-size data and index pages (typically 8 KB in PostgreSQL, 16 KB in MySQL InnoDB)
- Employs eviction algorithms (LRU, Clock-sweep) to maintain hot pages in memory
- Modifies pages in-memory as "dirty pages" while logging changes to the Write-Ahead Log (WAL) before flushing to disk asynchronously
- Cache hit ratio (typically >99%) directly dictates transactional query latency and throughput

### When to Use
- Sizing database instances to ensure the active working set (frequently accessed tables and indexes) fits within RAM
- Monitoring database health via buffer pool hit rates (`pg_stat_database.blks_hit / (blks_hit + blks_read)`)

### When NOT to Use
- As a substitute for an external caching layer (Redis) when caching deserialized API responses or cross-service aggregates
- For raw analytical streaming scans that would otherwise sweep and pollute transactional cache pages

### Also see
- [shared_buffers](#shared-buffers) · [B-Tree](#b-tree) · [B-Tree Page Split](#b-tree-page-split) · [Write-Ahead Log (WAL)](#write-ahead-log-wal)

---

## B-Tree Page Split {#b-tree-page-split}

An internal storage operation in B-Tree and B+ Tree indexes where a full data/index page is split into two separate pages (usually moving ~50% of the entries to a newly allocated page) to accommodate an incoming insertion.

### Key Characteristics
- Occurs when an insertion targets a leaf page that has exceeded its page capacity (8 KB / 16 KB)
- Allocates a new physical disk page, rebalances entries, and updates parent branch nodes up the tree
- Causes index fragmentation and drops average page fill factor from ~90–95% down to ~50–60%
- Heavily triggered by random primary keys (e.g., UUIDv4), leading to index bloat and high write amplification

### When to Use
- Diagnosing database write latency degradation and unexplained index file bloat
- Tuning index fill factors (`WITH (fillfactor = 70)`) on tables with heavy random inserts or frequent `UPDATE`s

### When NOT to Use
- Not an application-level API; managed autonomously by the storage engine
- Not problematic for sequential append-only keys where new pages are allocated cleanly at the tail

### Also see
- [B-Tree](#b-tree) · [Buffer Pool](#buffer-pool) · [UUIDv4](#uuidv4) · [UUIDv7](#uuidv7)

---

## UUIDv4 {#uuidv4}

A Universally Unique Identifier generated using 122 bits of pseudo-random or cryptographically secure random entropy (with 6 bits reserved for version `0100` and variant `10`).

### Key Characteristics
- 128-bit identifier formatted as `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- Generated client-side in application code without central coordination or database locks
- Non-enumerable: protects against business metrics leakage and scraping attacks
- Completely un-ordered: causes severe B-tree page splits, buffer pool churn, and index bloat when used as a clustered primary key

### When to Use
- Ephemeral tokens, session identifiers, and API correlation IDs
- Distributed tracing span/trace IDs
- Non-indexed unique attributes or columns indexed via hash indexes

### When NOT to Use
- Clustered primary keys in high-volume relational database tables (PostgreSQL, MySQL InnoDB, SQL Server)
- Foreign keys where sequential join locality and index compactness are required

### Also see
- [UUIDv7](#uuidv7) · [ULID](#ulid) · [TSID](#tsid) · [B-Tree Page Split](#b-tree-page-split)

---

## UUIDv7 {#uuidv7}

A standardized (RFC 9562) Universally Unique Identifier that embeds a 48-bit Unix millisecond timestamp in the leading bits, followed by 12 bits of sub-millisecond precision/counter and 62 bits of random entropy.

### Key Characteristics
- 128-bit standard UUID format natively supported by SQL `UUID` data types
- Lexicographically and chronologically sortable (monotonically increasing over time)
- Preserves B-Tree index append locality, virtually eliminating page splits and buffer pool thrashing
- Decentralized: multiple microservices and client applications generate unique IDs concurrently without collision

### When to Use
- Recommended default primary key strategy for modern relational database tables requiring decentralized ID generation
- Distributed event stores and audit logs requiring time-ordered unique record identifiers
- Multi-region database replication where primary key generation cannot rely on centralized auto-increment sequences

### When NOT to Use
- High-volume systems with extreme memory constraints where 16 bytes per key causes excessive secondary index bloat compared to 64-bit alternatives (TSID/Snowflake)
- Security contexts where exposing record creation timestamps in the identifier leaks business intelligence

### Also see
- [UUIDv4](#uuidv4) · [ULID](#ulid) · [TSID](#tsid) · [Snowflake ID](#snowflake-id) · [B-Tree](#b-tree)

---

## ULID {#ulid}

Universally Unique Lexicographically Sortable Identifier, combining a 48-bit Unix millisecond timestamp with 80 bits of cryptographic randomness, encoded as a 26-character string using Crockford's Base32 alphabet.

### Key Characteristics
- 128-bit binary representation, formatted as a 26-character human-readable string
- Crockford's Base32 alphabet excludes confusing characters (`I`, `L`, `O`, `U`) to prevent human transcription errors
- Monotonically increasing per millisecond (with an incrementing random component within the same millisecond)
- Case-insensitive string sorting matches chronological creation order

### When to Use
- Public-facing URLs, REST API route parameters, and human-readable identifiers
- Document and NoSQL databases (MongoDB, DynamoDB) using string keys
- High-concurrency event ingestion pipelines where string sorting aligns with time ordering

### When NOT to Use
- Relational databases with native 128-bit `UUID` data types (where UUIDv7 is standardized via RFC 9562)
- Systems where case-sensitive Base64 encoding is preferred for shorter character lengths

### Also see
- [UUIDv7](#uuidv7) · [TSID](#tsid) · [UUIDv4](#uuidv4) · [Snowflake ID](#snowflake-id)

---

## TSID {#tsid}

Time-Sorted Unique Identifier, a 64-bit distributed identifier combining a 42-bit millisecond timestamp, a 10-bit Node/Worker ID, and a 12-bit sequence counter.

### Key Characteristics
- 64-bit size fits natively into a standard SQL `BIGINT` / `INT8` (8 bytes vs. 16 bytes for UUIDs)
- Generates up to 4,096 unique IDs per millisecond per node
- Retains sequential B-Tree append locality while halving secondary index and foreign-key storage overhead
- Can be formatted as a compact 13-character Crockford Base32 string for external API exposure

### When to Use
- Ultra-high-volume relational databases where foreign-key storage and RAM consumption are critical bottlenecks
- High-QPS distributed transactional tables needing time-sorted locality within standard 64-bit integer columns

### When NOT to Use
- Multi-service architectures where configuring and managing unique Node/Worker IDs is impractical or adds operational overhead
- Environments requiring zero coordination and collision resistance solely through high random entropy (use UUIDv7 instead)

### Also see
- [Snowflake ID](#snowflake-id) · [UUIDv7](#uuidv7) · [ULID](#ulid) · [B-Tree](#b-tree)

---

## Connection Storm {#connection-storm}

A catastrophic failure mode where a sudden surge of concurrent application threads, autoscaling compute instances, or uncoordinated retries attempts to establish or acquire database connections simultaneously, exhausting database connection limits (`max_connections`) and causing connection acquisition timeouts, memory thrashing, and cascading system outages.

### Key Characteristics
- **Amplification by compute concurrency**: Lightweight thread runtimes (Java virtual threads, Go goroutines) can spawn thousands of concurrent tasks that overwhelm physical connection pools
- **Autoscaling multiplication**: Rapid horizontal scaling of app servers multiplies total open connections across instances ($\text{Instances} \times \text{Pool Size}$), easily breaching database session limits
- **Cascading retry storm**: Connection acquisition timeouts trigger upstream retries, which generate additional connection requests and accelerate database collapse
- **Memory pressure**: In PostgreSQL, every backend connection allocates private memory (work_mem, backend process footprint), leading to OS OOM-kills when connections spike

### When to Use / How to Prevent
- Implement intermediate connection pooling proxies (PgBouncer, AWS RDS Proxy, Azure Database for PostgreSQL built-in PgBouncer)
- Set strict client-side semaphores / bulkheads to limit concurrent database access
- Use exponential backoff with jitter on database connection retry policies
- Downsize per-instance application connection pools (e.g., HikariCP `maximumPoolSize`)

### When NOT to Use / Anti-patterns
- Do not attempt to fix a connection storm by blindly increasing database `max_connections` (this increases lock contention and context switching overhead)
- Do not allow background threads or async batch jobs to share the primary transaction pool without rate limits

### Also see
- [Connection Pooling](#connection-pooling) · [Connection Acquisition Latency](#connection-acquisition-latency) · [Database Backpressure](#database-backpressure)

---

## Connection Acquisition Latency {#connection-acquisition-latency}

The duration an application thread or task waits in a connection pool queue (e.g., HikariCP wait queue) to borrow an active database connection. It is the primary leading indicator of database capacity exhaustion before query latency or CPU saturation becomes visible.

### Key Characteristics
- **Leading health indicator**: Spikes in connection acquisition latency occur before downstream query latency degrades, providing early warning of pending pool exhaustion
- **Pool queue depth**: Reflects the ratio of concurrent database callers to available pool capacity
- **Metric keys**: Commonly exposed as `hikaricp.connections.acquire` (duration), `hikaricp.connections.pending` (threads awaiting a connection), and `hikaricp.connections.timeout` (failed acquisitions)
- **Fast-fail trigger**: When acquisition latency exceeds configured `connectionTimeout`, the pool throws an exception to fail fast rather than hanging indefinitely

### When to Use
- Baseline alerting in APM and observability dashboards (alert when P95 acquisition latency exceeds 50–100ms)
- Capacity planning for connection pool sizing and microservice replica autoscaling
- Diagnosing thread starvation and long-running transaction leaks

### When NOT to Use
- Do not use acquisition latency as a substitute for query execution time monitoring; monitor both together to differentiate pool contention from slow queries

### Also see
- [Connection Pooling](#connection-pooling) · [Connection Storm](#connection-storm) · [Database Backpressure](#database-backpressure)

---

## Database Backpressure {#database-backpressure}

A concurrency control mechanism applied at the application or gateway layer to explicitly throttle and bound the number of concurrent tasks allowed to interact with the database, protecting backend connection pools and database processes from saturation.

### Key Characteristics
- **Resource isolation**: Decouples unbounded compute concurrency (e.g., virtual threads, event loops) from strictly bounded database connection and transaction resources
- **Implementation mechanisms**: Built using client-side semaphores (`java.util.concurrent.Semaphore`), Resilience4j Bulkheads, bounded token buckets, or reactive backpressure (`Flow`, Reactive Streams)
- **Fast rejection & load shedding**: Excess requests queue gracefully up to a configured threshold or fail immediately with HTTP 429 / 503 instead of creating connection queue bloat
- **Protects multi-region clusters**: Enforces local concurrency ceilings per instance, preventing distributed autoscaling from generating a connection flood

### When to Use
- Lightweight thread runtimes (Java virtual threads, Go goroutines, Kotlin coroutines) executing high-volume database operations
- Concurrent fan-out workflows where a single API request executes multiple parallel database queries
- Peak load events (Black Friday, flash sales) to preserve system stability under extreme traffic surges

### When NOT to Use
- Low-throughput or single-threaded background jobs where concurrency naturally remains below pool capacity
- When an intermediate proxy (e.g., PgBouncer in transaction mode) already reliably multiplexes and queues client connections without application-level overhead

### Also see
- [Connection Pooling](#connection-pooling) · [Connection Storm](#connection-storm) · [Connection Acquisition Latency](#connection-acquisition-latency)

---

## Skip List

A **probabilistic multi-level linked list data structure** (invented by William Pugh) that provides $O(\log N)$ search, insertion, and deletion times without requiring complex tree rotations or balance operations. Skip lists power **Redis Sorted Sets (`ZSET`)** and in-memory Memtables in LSM-tree databases (e.g., LevelDB, RocksDB).

### Key Characteristics
- **Hierarchical express lanes**: The bottom layer is a standard sorted linked list containing all elements. Higher levels contain a probabilistic subset of elements (promoted with probability $p=1/2$ or $1/4$), acting as fast-forward express skips
- **Simple lock-free concurrency**: Far easier to implement lock-free concurrent updates (via atomic CAS on pointers) than self-balancing binary search trees (AVL or Red-Black trees)
- **Range query efficiency**: Scanning ranges (`ZRANGEBYSCORE`) is a simple pointer traversal along the bottom linked list once the start node is located
- **Memory footprint**: Consumes approximately $1 / (1 - p)$ pointers per node on average (e.g., ~1.33 pointers per node with $p=1/4$)

### When to Use
- Real-time gaming leaderboards and ranking systems requiring high-frequency rank and score updates
- In-memory sorted index structures in storage engines (Memtables in RocksDB)
- Concurrency runtimes requiring lock-free concurrent ordered maps (`ConcurrentSkipListMap` in Java)

### When NOT to Use
- Disk-based persistent index storage (where B-Trees minimize expensive disk seeks via wide fan-out pages)
- Simple unsorted key-value caching where standard Hash Tables provide $O(1)$ lookup with less memory

### Also see
- [B-Tree](#b-tree) · [Red-Black Tree](#red-black-tree) · [LSM-Tree](#lsm-tree) · [Redis Sorted Sets](caching.md#redis-sorted-sets)

---

## Ticket Server

A **centralized distributed sequence generation architecture pattern** (popularized by Flickr) that uses dedicated relational database instances with auto-increment primary keys to generate globally unique, 64-bit monotonically increasing numerical IDs.

### Key Characteristics
- **`REPLACE INTO` idiom**: Employs SQL replacement logic (e.g., `REPLACE INTO Tickets64 (stub) VALUES ('a'); SELECT LAST_INSERT_ID();`) on a dedicated single-row table to advance the sequence without accumulating dead table rows
- **Multi-master parity distribution**: To prevent a single point of failure (SPOF), two or more ticket servers are deployed with differing `auto_increment_increment` and `auto_increment_offset` parameters (e.g., Server 1 generates odd IDs $1, 3, 5, \dots$ and Server 2 generates even IDs $2, 4, 6, \dots$)
- **Monotonically increasing**: Guarantees strictly increasing integer IDs, making them optimal for database B-Tree index insertions without page fragmentation

### When to Use
- Monolithic systems requiring strictly ordered 64-bit numerical IDs without coordinating complex distributed consensus
- Medium-scale systems where snowflake time-synchronization (NTP clock drift) introduces operational complexity

### When NOT to Use
- Ultra-high throughput distributed systems (>100,000 IDs/sec) where network round-trips to a centralized database create bottlenecks (prefer Twitter Snowflake ID)
- Systems requiring zero dependency on centralized database state

### Also see
- [Snowflake ID](#snowflake-id) · [UUIDv7](#uuidv7) · [ULID](#ulid) · [TSID](#tsid)

---

## Inverted Index

A **search data structure** that maps each term (word, token) to the list of documents containing it. This is the foundational data structure behind full-text search engines (Google Search, Elasticsearch, Lucene). Instead of scanning every document for a query term, the inverted index provides O(1) lookup of the term followed by intersection/union of result lists.

### Key Characteristics
- **Term → Document mapping**: The inverse of a forward index (document → terms)
- **Postings list**: Each term maps to a sorted list of document IDs (and optionally positions, term frequency)
- **Boolean query support**: AND/OR/NOT queries are implemented as set operations on postings lists
- **Skip lists**: Accelerate intersection by skipping over non-matching document IDs

### When to Use
- Full-text search over large document collections
- Log search and observability (Elasticsearch, Splunk)
- Any system where users need keyword-based retrieval from unstructured text

### When NOT to Use
- For exact-match lookups — a hash index or B-tree is simpler and faster
- For relational queries with joins and aggregations — use a SQL database
- When the corpus is small enough for brute-force scan

### Also see
- [B-Tree](#b-tree) · [Skip List](#skip-list) · [Bloom Filter](#bloom-filter)

---

## KSUID

A K-Sortable Unique Identifier. A 20-byte identifier composed of a 4-byte timestamp (seconds since the KSUID epoch) and a 16-byte random payload. KSUIDs are time-sortable, require no worker coordination, and offer higher entropy than ULID.

### Key Characteristics
- **20 bytes**: Larger than UUIDs and Snowflake IDs
- **Time-ordered**: First 4 bytes encode seconds since 2014-05-13
- **No coordination**: Any node can generate KSUIDs independently
- **High entropy**: 128 random bits per ID

### When to Use
- Distributed systems needing sortable IDs without worker ID assignment
- Event streams and distributed logs where higher entropy reduces guessability

### When NOT to Use
- When storage size is constrained (20 bytes per key)
- When millisecond-level ordering is required

### Also see
- [Snowflake ID](#snowflake-id) · [UUIDv7](#uuidv7) · [ULID](#ulid) · [TSID](#tsid) · [Database ID Strategy](../system-design-architecture/databases/database-id-strategy.md)

---

## Trie (Prefix Tree)

A **tree data structure** where keys are usually strings, and each node represents a common character prefix. Rather than storing entire keys in individual nodes, a key's position in the tree defines its string value, enabling fast prefix lookups and autocomplete queries in $O(L)$ time, where $L$ is the length of the search string.

### Key Characteristics
- **Prefix sharing**: Common prefixes are stored once, reducing storage redundancy for dictionaries with high shared prefix ratios
- **$O(L)$ search time**: Lookup, insertion, and deletion times depend strictly on key length $L$, completely independent of the total number of keys $N$ in the dataset
- **Branching factor**: Each node contains an array or hash map of child pointers corresponding to the alphabet size (e.g., 26 for lowercase English, 256 for ASCII)
- **Compact representation**: Can be optimized as a Radix Tree (Patricia Trie) by compressing single-child chains into multi-character edges

### When to Use
- Real-time search autocomplete systems (Google/Amazon search boxes)
- IP routing lookup tables (Longest Prefix Match in network routers)
- Spell checkers, dictionary lookup, and predictive text input

### When NOT to Use
- Pure exact-match key-value lookups where standard Hash Tables provide $O(1)$ lookup with simpler memory layouts
- Datasets with very long keys and few shared prefixes where pointer overhead consumes excessive memory

### Also see
- [Trie Cache](caching.md#trie-cache) · [Geocoding](geospatial.md#geocoding) · [B-Tree](#b-tree)

---

## SimHash

A **locality-sensitive hashing (LSH) algorithm** developed by Moses Charikar that maps large text documents into compact 64-bit or 128-bit integer fingerprints, such that the Hamming distance (number of differing bits) between two fingerprints is directly proportional to the semantic similarity of the original documents.

### Key Characteristics
- **Locality-sensitive**: Unlike cryptographic hash functions (MD5, SHA-256) where a single byte change scrambles the entire hash, SimHash produces similar hashes for similar documents
- **Hamming distance threshold**: Documents with a Hamming distance $\le 3$ bits (out of 64 bits) are typically considered near-duplicates
- **Vector weighting**: Tokenizes document words, computes hash vectors weighted by term frequency (TF-IDF), and sums bit vectors to generate the final binary fingerprint
- **Table Partitioning**: Uses pigeonhole principle (splitting 64-bit keys into 4 tables of 16 bits) to execute sub-millisecond near-duplicate searches across billions of indexed web pages

### When to Use
- Web search crawlers (Google, Bing) detecting duplicate and mirrored web pages at web scale
- Plagiarism detection systems and copyright infringement scanning
- News aggregators clustering duplicate press releases across different media outlets

### When NOT to Use
- Cryptographic security, password hashing, or digital signatures where collision resistance is required
- Short strings (under 50 words) where token frequency vectorization lacks statistical significance

### Also see
- [Inverted Index](#inverted-index) · [Bloom Filter](#bloom-filter) · [HyperLogLog](#hyperloglog)

---

## Non-Blocking Incremental Snapshot

A **database bootstrapping technique** (pioneered by Netflix's DBLog framework) that captures a full baseline snapshot of an active, multi-million-row database table without acquiring table-level read locks (`LOCK TABLE ... IN SHARE MODE`) or blocking application write traffic. It works by interleaving primary key range chunks with the live transaction log (WAL/Binlog) using low-watermark and high-watermark signals written to a dedicated control table.

### Key Characteristics
- **Zero lock contention**: Reads primary key intervals via standard `SELECT ... WHERE pk >= chunk_start AND pk < chunk_end` queries without blocking concurrent transactional updates.
- **Windowed log deduplication**: For any mutations occurring in the transaction log between the chunk's low-watermark and high-watermark signals, the connector reconciles in-memory state so WAL events supersede snapshot data.
- **Dynamic pause and resume**: Snapshot progress is tracked per chunk in metadata tables, allowing bootstrapping to be paused, throttled during peak OLTP hours, or resumed after node failures.
- **Uniform resource footprint**: Bounds memory and buffer pool usage by scanning small, discrete primary key intervals rather than unbounded table scans.

### When to Use
- Initializing Change Data Capture (CDC) pipelines on large, production-critical tables with strict 24/7 uptime SLAs.
- Adding newly created tables or backfilling missing historical tables into an existing live streaming pipeline.
- Disaster recovery re-syncing where an analytical warehouse must be repopulated without degrading primary database throughput.

### When NOT to Use
- Small, static reference tables where a simple table export or off-peak copy causes negligible lock impact.
- Tables lacking a primary key or unique, monotonically sortable integer index needed for deterministic range chunking.

### Also see
- [Write-Ahead Log (WAL)](#write-ahead-log-wal) · [LSN Lag](#lsn-lag) · [CDC Tombstone](#cdc-tombstone) · [Low-Watermark / High-Watermark](#low-watermark-high-watermark) · [38. CDC Pipeline Scale Failures](../../system-design-architecture/databases/38-db-key-takeaways.md)

---

## CDC Tombstone

An **explicit deletion event marker** emitted by Change Data Capture (CDC) engines (such as Debezium) when a row is physically deleted from the source database (`DELETE FROM table`). It typically contains a deletion operation indicator (e.g., `_cdc_op = 'D'` or a null payload with entity ID key) to signal downstream consumers, stream processors, and cloud data warehouses to remove or soft-delete the corresponding target entity.

### Key Characteristics
- **Prevents zombie records**: Physical database deletes leave no updated timestamp; without tombstones, deleted rows linger permanently as active records in downstream data lakes and warehouses.
- **Preserves partition key**: Carries the source primary key as the broker message key so the deletion event lands on the exact same Kafka partition as preceding inserts and updates.
- **Compact topic support**: Compatible with Kafka log compaction, where a null-payload tombstone instructs broker log cleaners to evict all older record versions with that key.

### When to Use
- Synchronizing relational databases to analytical data warehouses (Snowflake, BigQuery, Databricks Delta Lake) where physical deletes must propagate deterministically.
- Invalidating distributed cache entries (Redis/Memcached) or search indices (Elasticsearch) in real time upon database row deletion.

### When NOT to Use
- Append-only immutable event logs or financial ledgers where physical deletions are prohibited by compliance (use compensatory reversal events instead).
- Systems using application-level soft deletes (`is_deleted = true`), where standard `UPDATE` CDC events convey state change.

### Also see
- [Non-Blocking Incremental Snapshot](#non-blocking-incremental-snapshot) · [Monotonic Timestamp Guard](#monotonic-timestamp-guard) · [Change Data Capture](../data-concurrency.md#change-data-capture)

---

## LSN Lag

The **replication backlog gap** measured as the difference in bytes between the primary database's current Write-Ahead Log Log Sequence Number (`pg_current_wal_lsn()`) and a replication slot's latest confirmed flush position (`confirmed_flush_lsn`). Unlike Kafka consumer lag which only consumes broker memory/disk, unconsumed database LSN lag forces the database engine to retain all WAL segments on disk, risking primary node disk exhaustion.

### Key Characteristics
- **Storage pressure on primary**: The primary database checkpointer cannot recycle or delete WAL files that are newer than the oldest active replication slot's `restart_lsn`.
- **Disk exhaustion vulnerability**: If a CDC consumer or subscriber halts without dropping its slot, WAL files accumulate until database disk space hits 100%, causing a hard database outage.
- **Independent of broker lag**: Consumer lag inside Kafka measures delivery latency to analytical sinks; LSN lag measures extraction latency from the database storage engine itself.

### When to Use
- Primary database health monitoring and alerting (triggering high-priority alerts when replication slot lag exceeds disk safety thresholds).
- Capacity planning for CDC pipelines and Postgres logical replication infrastructure.

### When NOT to Use
- Measuring end-to-end event delivery latency to final consumers (use Kafka consumer group offset lag for downstream queue monitoring).

### Also see
- [LSN (Log Sequence Number)](#lsn) · [WALSender](#walsender) · [Write-Ahead Log (WAL)](#write-ahead-log-wal) · [35. PostgreSQL Logical Replication Takeaways](../../system-design-architecture/databases/35-db-key-takeaways.md)

---

## Monotonic Timestamp Guard

A **conditional update guard clause** used in data warehouse reconciliation queries (e.g., `WHEN MATCHED AND source._cdc_ts > target._cdc_last_updated THEN UPDATE`) that prevents out-of-order, delayed, or retried CDC events from overwriting fresher state in target analytical tables.

### Key Characteristics
- **Idempotent upsert safety**: Guarantees deterministic state reconciliation even when network retransmissions or batch replays deliver historical events after newer updates.
- **Epoch/Timestamp validation**: Compares the transaction commit timestamp (`_cdc_ts`) or database LSN attached to the change event against the target row's recorded watermark.
- **Complement to micro-batch deduplication**: Works in tandem with windowed deduplication (`ROW_NUMBER() OVER (PARTITION BY pk ORDER BY _cdc_ts DESC)`) to ensure correctness across batch boundaries.

### When to Use
- Streaming ingestion pipelines targeting cloud data warehouses (Snowflake, BigQuery, Databricks Delta Lake, Azure Synapse).
- Multi-master or active-active replication systems reconciling concurrent event streams using Last-Write-Wins (LWW) semantics.

### When NOT to Use
- Pure append-only event stores where every mutation is written as a new immutable historical row rather than updating an in-place dimension table.

### Also see
- [CDC Tombstone](#cdc-tombstone) · [Upsert](#upsert) · [Change Data Capture](../data-concurrency.md#change-data-capture)

---

## Low-Watermark / High-Watermark {#low-watermark-high-watermark}

A **synthetic log demarcation protocol** (central to Netflix's DBLog algorithm and modern lock-free CDC engines like Debezium) used to coordinate parallel chunk-based table reads with an active transaction log. A low-watermark ($LW$) signal record is written to a dedicated database table before reading a primary key chunk, and a high-watermark ($HW$) signal is written immediately after the chunk read completes. Changes appearing in the transaction log between $LW$ and $HW$ are reconciled in memory to guarantee snapshot consistency without blocking concurrent database transactions.

### Key Characteristics
- **Transactional signaling**: Generates synthetic WAL/Binlog events by inserting lightweight marker rows into a dedicated signaling table within the source database.
- **Windowed reconciliation**: Captures the exact window of concurrent mutations during a `SELECT` query on a primary key range chunk ($pk \in [start, end)$); any WAL changes between $LW$ and $HW$ overwrite stale chunk values.
- **Non-blocking linearizability**: Achieves serializable snapshot consistency for historical data backfills without acquiring table-level shared locks (`LOCK TABLE`).
- **Generalized boundary concept**: Outside of CDC signaling, high/low watermarks define commit boundaries in distributed logs (e.g., Kafka ISR commit offsets) and hysteresis thresholds for buffer flow control/backpressure.

### Example: Lock-Free Chunk Snapshot with LW/HW Signaling (DBLog Protocol)

```sql
-- Step 1: CDC engine writes Low-Watermark signal to database
INSERT INTO cdc_signal_table (id, type) VALUES ('chunk_101_LW', 'LOG_MARKER');

-- Step 2: Read snapshot chunk in application memory
SELECT id, name, email FROM accounts WHERE id >= 1000 AND id < 2000;
-- (Suppose Row 1042 has email = 'old@example.com' at this moment)

-- Step 3: CDC engine writes High-Watermark signal to database
INSERT INTO cdc_signal_table (id, type) VALUES ('chunk_101_HW', 'LOG_MARKER');
```

```
WAL / Binlog Stream Processing:
[... Normal Live Events ...]
  │
  ├─ 1. Encounter signal 'chunk_101_LW' in WAL  ──► Begin chunk window tracking
  │
  ├─ 2. Encounter live WAL event:               ──► In-memory reconciliation:
  │     UPDATE accounts SET email='new@x.com'       Overwrites Row 1042 with 'new@x.com'
  │     WHERE id = 1042;
  │
  ├─ 3. Encounter signal 'chunk_101_HW' in WAL  ──► Window closes; emit finalized,
  │                                                 consistent chunk 101 to Kafka
  ▼
[... Resume Standard Real-Time Streaming ...]
```

### When to Use
- Implementing or configuring lock-free incremental snapshots on active OLTP database tables.
- Reconciling concurrent application writes with historical data backfills in Change Data Capture (CDC) streaming pipelines.
- Distributed log partition replication where consumers only read up to the replicated High-Watermark.

### When NOT to Use
- Small or static reference tables where a simple table export or off-peak copy causes negligible lock impact.
- Standard streaming event-time windowing where heuristic watermarks (delay thresholds) rather than transactional signal markers are required (see [Watermarking](messaging.md#watermarking)).

### Also see
- [Non-Blocking Incremental Snapshot](#non-blocking-incremental-snapshot) · [Write-Ahead Log (WAL)](#write-ahead-log-wal) · [Watermarking](messaging.md#watermarking) · [38. CDC Pipeline Scale Failures](../../system-design-architecture/databases/38-db-key-takeaways.md#db-38-log-based-cdc-bootstrapping--non-blocking-incremental-snapshots)
