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
- [KSUID](../reference-dictionary/architecture-patterns.md#ksuid) · [Shard Key](../reference-dictionary/architecture-patterns.md#shard-key) · [Gene-Based Sharding](../reference-dictionary/data-concurrency.md#gene-based-sharding) · [Database ID Strategy](../system-design-architecture/databases/database-id-strategy.md)

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
- [Shard Key](../reference-dictionary/architecture-patterns.md#shard-key) · [Data Skew](../reference-dictionary/data-architecture.md#data-skew) · [Sharding](../reference-dictionary/data-architecture.md#sharding) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)

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
- [Hot Partition](../messaging.md#hot-partition) · [Composite Shard Key](#composite-shard-key) · [Shard Key](../reference-dictionary/architecture-patterns.md#shard-key) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)


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
