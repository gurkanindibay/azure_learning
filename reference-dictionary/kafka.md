---
type: Reference
title: "Apache Kafka"
description: "Kafka-specific terms: topics, partitions, consumer groups, offsets, replication, delivery semantics, Kafka Connect, Kafka Streams, Schema Registry, and operational patterns."
generated: { by: process:okf-migrate, at: 2026-10-03T10:17:00+03:00 }
---

# Apache Kafka

> **Domain**: Apache Kafka — topics, partitions, consumer groups, offsets, delivery semantics, replication, Kafka Connect, Kafka Streams, Schema Registry, and operational patterns.
> **Parent**: [Reference Dictionary](index.md)
> **See also**: [General Messaging](messaging.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Kafka vs RabbitMQ | [`#kafka-vs-rabbitmq`](#kafka-vs-rabbitmq) |
| Partition | [`#partition`](#partition) |
| Consumer Group | [`#consumer-group`](#consumer-group) |
| Offset Commit | [`#offset-commit`](#offset-commit) |
| Dead Letter Queue (DLQ) | [`#dead-letter-queue-dlq`](#dead-letter-queue-dlq) |
| Poison Message | [`#poison-message`](#poison-message) |
| Message Ordering | [`#message-ordering`](#message-ordering) |
| At-Least-Once Semantics | [`#at-least-once-semantics`](#at-least-once-semantics) |
| Exactly-Once Semantics | [`#exactly-once-semantics`](#exactly-once-semantics) |
| Rebalance | [`#rebalance`](#rebalance) |
| Consumer Lag | [`#consumer-lag`](#consumer-lag) |
| Kafka Connect | [`#kafka-connect`](#kafka-connect) |
| Kafka Transactions | [`#kafka-transactions`](#kafka-transactions) |
| Idempotent Consumer | [`#idempotent-consumer`](#idempotent-consumer) |
| Idempotent Producer | [`#idempotent-producer`](#idempotent-producer) |
| Auto Commit | [`#auto-commit`](#auto-commit) |
| Compacted Topic | [`#compacted-topic`](#compacted-topic) |
| Stream-Table Duality | [`#stream-table-duality`](#stream-table-duality) |
| Hot Partition | [`#hot-partition`](#hot-partition) |
| Retry Topic | [`#retry-topic`](#retry-topic) |
| KTable | [`#ktable`](#ktable) |
| Claim Check | [`#claim-check`](#claim-check) |
| Distributed Commit Log | [`#distributed-commit-log`](#distributed-commit-log) |
| Message Batching | [`#message-batching`](#message-batching) |
| Replay (Kafka Reprocessing) | [`#replay-kafka-reprocessing`](#replay-kafka-reprocessing) |
| Producer Acknowledgement | [`#producer-acknowledgement`](#producer-acknowledgement) |
| Schema Registry | [`#schema-registry`](#schema-registry) |
| Schema Contract (Event as Public API) | [`#schema-contract-event-as-public-api`](#schema-contract-event-as-public-api) |
| Event-Time | [`#event-time`](#event-time) |
| Processing-Time | [`#processing-time`](#processing-time) |
| Watermarking | [`#watermarking`](#watermarking) |
| Offset Alignment | [`#offset-alignment`](#offset-alignment) |
| Apache Flink | [`#apache-flink`](#apache-flink) |
| Write-Ahead Buffer | [`#write-ahead-buffer`](#write-ahead-buffer) |
| Log Segment | [`#log-segment`](#log-segment) |
| ISR (In-Sync Replica) | [`#isr-in-sync-replica`](#isr-in-sync-replica) |
| Replication Factor | [`#replication-factor`](#replication-factor) |
| Kafka Streams | [`#kafka-streams`](#kafka-streams) |
| Stream Sessionization | [`#stream-sessionization`](#stream-sessionization) |
| Stream-Stream Join | [`#stream-stream-join`](#stream-stream-join) |
| In-Stream Keyed Deduplication | [`#in-stream-keyed-deduplication`](#in-stream-keyed-deduplication) |
| Deterministic Consumer | [`#deterministic-consumer`](#deterministic-consumer) |
| Resolved State Consumption | [`#resolved-state-consumption`](#resolved-state-consumption) |
| Federated Kafka Clusters | [`#federated-kafka-clusters`](#federated-kafka-clusters) |
| uReplicator | [`#ureplicator`](#ureplicator) |
| Pipeline Audit Service (Chaperone Pattern) | [`#pipeline-audit-service-chaperone-pattern`](#pipeline-audit-service-chaperone-pattern) |
| Consumer Proxy Pattern | [`#consumer-proxy-pattern`](#consumer-proxy-pattern) |
| Kafka Tiered Storage | [`#kafka-tiered-storage`](#kafka-tiered-storage) |
| KRaft | [`#kraft`](#kraft) |
| Cooperative Sticky Assignor | [`#cooperative-sticky-assignor`](#cooperative-sticky-assignor) |
| RecordAccumulator | [`#recordaccumulator`](#recordaccumulator) |
| Avro | [`#avro`](#avro) |
| SASL | [`#sasl`](#sasl) |
| Redpanda | [`#redpanda`](#redpanda) |
| KStream | [`#kstream`](#kstream) |
| Sticky Partitioner | [`#sticky-partitioner`](#sticky-partitioner) |

---

## Kafka vs RabbitMQ

| Aspect | Kafka (Log) | RabbitMQ (Queue) |
|:---|:---|:---|
| **Model** | Append-only distributed log | Smart broker, dumb consumer |
| **Message retention** | Configurable (days/weeks/forever) | Deleted after consumption |
| **Ordering** | Per-partition, strict | Per-queue, can be disrupted by re-queues |
| **Throughput** | Millions msg/s | Tens of thousands msg/s |
| **Best for** | Event streaming, replay, high throughput | Task queues, complex routing, request/reply |
| **Worst for** | Task queues with per-message ACK | Long-term event storage |

> **Rule of thumb**: Use RabbitMQ for task distribution with complex routing. Use Kafka for event streaming, replay, and high-throughput ordered processing.

**Also see**: [Partition](#partition), [Consumer Group](#consumer-group)

---


## Partition

The unit of **parallelism and ordering** in Kafka. Messages within a partition are strictly ordered. Partitions enable horizontal scaling — each partition can be consumed by only one consumer in a group at a time.

| Property | Detail |
|:---|:---|
| **Ordering guarantee** | Within a partition only (not global) |
| **Parallelism** | Number of partitions = max parallel consumers |
| **Key-based routing** | Same key → same partition → ordered processing |

**Also see**: [Consumer Group](#consumer-group), [Message Ordering](#message-ordering)

---


## Consumer Group

A group of Kafka consumers that **cooperatively consume from topics**. Each partition is assigned to exactly one consumer in the group. Adding consumers scales throughput (up to the partition count).

| Property | Detail |
|:---|:---|
| **Load balancing** | Partitions distributed across group members |
| **Scaling** | Add consumers to increase parallelism (up to partition count) |
| **Idle consumers** | Consumers beyond partition count sit idle |

**Also see**: [Partition](#partition), [Rebalance](#rebalance)

---


## Offset Commit

The mechanism by which a consumer **records its progress** in reading a partition. On restart, the consumer resumes from the last committed offset.

| Strategy | Risk |
|:---|:---|
| **Auto-commit** (periodic) | At-least-once — may re-process after crash |
| **Manual commit** (after processing) | At-most-once if commit before processing completes |
| **Manual commit** (before + after) | Closer to exactly-once with idempotent processing |

**Also see**: [At-Least-Once Semantics](#at-least-once-semantics), [Exactly-Once Semantics](#exactly-once-semantics)

---


## Dead Letter Queue (DLQ)

A queue (or Kafka topic) for messages that **cannot be processed** after all retry attempts are exhausted. DLQs prevent poison messages from blocking the entire queue/topic. DLQ messages must be **alerted on** and investigated. In Kafka this is usually called a **Dead Letter Topic (DLT)**.

**Also see**: [Poison Message](#poison-message) · [Resilience](resilience.md)

---


## Poison Message

A message that **repeatedly fails processing** and blocks the queue. Without a DLQ, the message is retried indefinitely, consuming resources and delaying all other messages.

| Mitigation | Detail |
|:---|:---|
| **Max retry count** | Stop retrying after N failures |
| **DLQ** | Move unprocessable messages to a separate queue |
| **Alert on DLQ** | Monitor DLQ depth — every message there is an undelivered event |

**Also see**: [Dead Letter Queue (DLQ)](#dead-letter-queue-dlq)

---


## Message Ordering

The guarantee that messages are **processed in the order they were produced**. In Kafka, ordering is guaranteed per-partition (not globally). In RabbitMQ, ordering can be disrupted by re-queues and consumer acknowledgments.

| Mechanism | Scope |
|:---|:---|
| **Partition key** | Same key → same partition → ordered |
| **MessageGroupId / SessionId** | SQS FIFO / Azure Service Bus sessions |
| **Consistent Hash Exchange** | RabbitMQ plugin for ordered routing |

**Also see**: [Partition](#partition), [Consumer Group](#consumer-group)

---


## At-Least-Once Semantics

A delivery guarantee where **no message is lost**, but messages may be delivered more than once. Consumers **must be idempotent** to handle duplicates safely.

**Required when**: Messages represent financial facts, audit events, or any data where loss is unacceptable.

**Also see**: [Exactly-Once Semantics](#exactly-once-semantics) · [CQRS & Event-Driven: Idempotency](cqrs-event-driven.md#idempotency)

---


## Exactly-Once Semantics

A delivery guarantee where **each message is processed exactly once** — no duplicates, no losses. In Kafka, achieved via idempotent producer + transactional reads. Complex and expensive — at-least-once with idempotent consumers is often sufficient.

**Also see**: [At-Least-Once Semantics](#at-least-once-semantics)

---


## Rebalance

When the **assignment of partitions to consumers changes** — triggered by consumer join/leave, partition addition, or health check failure. During rebalance, the consumer group temporarily stops processing (stop-the-world).

| Mitigation | Detail |
|:---|:---|
| **Cooperative rebalance** (StickyAssignor) | Incremental — only reassigns what's necessary |
| **Static group membership** | `group.instance.id` prevents rebalance on restart |
| **Tune timeouts** | `session.timeout.ms`, `max.poll.interval.ms`, `heartbeat.interval.ms` |

**Also see**: [Consumer Group](#consumer-group), [Partition](#partition)

---


## Consumer Lag

The difference between the **last produced offset** and the **last consumed offset** for a partition. Lag measures how far a consumer is behind the producer. Sustained growth in lag means the consumer cannot keep up with the topic throughput.

| Signal | Interpretation |
|:---|:---|
| **Lag grows** | Consumer is slower than producer or has stalled |
| **Lag spikes after deploy** | New code is slower or blocking on I/O |
| **Lag stays flat** | Consumer keeps up with arrival rate |

**Also see**: [Consumer Group](#consumer-group), [Partition](#partition)

---


## Kafka Connect

A Kafka framework for **moving data between Kafka and external systems** using reusable connectors. Commonly used to archive events to object storage (e.g., S3) for replay, analytics, or compliance.

| Use case | Example |
|:---|:---|
| **Event archival** | Kafka → S3 → data lake for replay months later |
| **Database ingestion** | CDC from PostgreSQL/MySQL into Kafka |
| **Sink to analytics** | Kafka → Elasticsearch/Snowflake |

**Also see**: [Partition](#partition) · [At-Least-Once Semantics](#at-least-once-semantics)

---


## Kafka Transactions

Atomic **consume-process-produce** across Kafka topics. A transactional producer can consume a record, transform it, produce to an output topic, and commit the consumer offset — all as a single atomic unit. Achieves **exactly-once semantics** for Kafka-to-Kafka pipelines.

### Key Characteristics
- **Atomic boundary**: Offset commit + output produce succeed or fail together
- **Requires**: idempotent producer (`enable.idempotence=true`), `transaction-id-prefix`, consumer `isolation.level=read_committed`
- **Performance cost**: ~20-30% throughput reduction vs non-transactional

### When to Use
- Kafka-to-Kafka data pipelines where no duplicates or gaps are acceptable
- Financial processing chains (input topic → transform → output topic)

### When NOT to Use
- When the pipeline involves external systems (use Outbox pattern instead)
- High-throughput pipelines where at-least-once + idempotent consumer is sufficient

**Also see**: [Exactly-Once Semantics](#exactly-once-semantics) · [Idempotent Consumer](#idempotent-consumer)

---


## Idempotent Consumer

A consumer designed so that **processing the same message multiple times produces the same result** as processing it once. This is the universal invariant of reliable message processing: duplicates are inevitable (from rebalances, retries, restarts), and idempotency is the only defense.

### Key Characteristics
- **Duplicate-tolerant**: Same input → same outcome, no side-effect amplification
- **Implementation patterns**: Upsert instead of insert, de-duplication by message key, idempotency keys in database
- **Non-negotiable**: No offset commit strategy can prevent duplicates entirely

### When to Use
- Always — design for idempotency from day one in any message-driven system
- Especially critical for: payments, order processing, inventory updates, audit events

### When NOT to Use
- Append-only log consumers where duplicates are harmless (rare)
- Telemetry/metrics where occasional double-counting is acceptable

**Also see**: [At-Least-Once Semantics](#at-least-once-semantics) · [Kafka Transactions](#kafka-transactions) · [Offset Commit](#offset-commit)

---


## Idempotent Producer

A Kafka producer configured with `enable.idempotence=true` that ensures **no duplicate messages are written to the broker** despite producer retries. Kafka assigns the producer a unique Producer ID (PID) and each message a monotonically increasing sequence number. The broker tracks the last committed sequence number per partition and silently discards any message whose sequence number is less than or equal to the last committed one.

### Key Characteristics
- **PID + sequence number**: Each producer session gets a unique PID; each message within that session gets an incrementing sequence number
- **Broker-side dedup**: The broker maintains a per-partition map of (PID → last committed sequence number) — duplicate writes are dropped before appending to the log
- **Single-partition scope**: Idempotence applies within a single producer session to a single partition; across sessions or partitions, duplicates are still possible
- **Enabled by default in Kafka ≥ 3.0**: `enable.idempotence` defaults to `true` since AK 3.0 (KIP-679)

### When to Use
- Any Kafka producer where duplicate messages would cause incorrect application state
- When combined with `acks=all` for full durability guarantees
- As a prerequisite for Kafka Exactly-Once Semantics (EOS) with transactions

### When NOT to Use
- When producer throughput is the top priority and occasional duplicates are acceptable (logging, metrics)
- When the application layer already has robust idempotency (the producer-level dedup is redundant but harmless)

**Also see**: [Exactly-Once Semantics](#exactly-once-semantics) · [Kafka Transactions](#kafka-transactions) · [Idempotent Consumer](#idempotent-consumer)

---


## Auto Commit

A Kafka consumer mode (`enable-auto-commit: true`) where offsets are **committed periodically on a timer**, independent of whether processing succeeded. The fastest strategy but also the most dangerous: if the consumer crashes after commit but before processing, those messages are **permanently lost**.

### Key Characteristics
- **Decoupled from processing**: Kafka has no visibility into business logic success
- **Timer-based**: Commit fires every `auto.commit.interval.ms` (default 5s)
- **Data loss risk**: Commit before processing = at-most-once in practice

### When to Use
- Logs, metrics, telemetry, clickstream — data where occasional loss is acceptable
- High-throughput pipelines prioritizing speed over correctness

### When NOT to Use
- Business-critical processing (orders, payments, workflows)
- Any system where data loss has regulatory or financial implications

**Also see**: [Offset Commit](#offset-commit) · [At-Least-Once Semantics](#at-least-once-semantics) · [Idempotent Consumer](#idempotent-consumer)

---


## Compacted Topic

A Kafka topic configured with `cleanup.policy=compact`. Instead of deleting messages by time or size, Kafka's log compactor retains only the **latest message for each key**, turning the topic into a fault-tolerant, replicated key-value store that new consumers can bootstrap from.

### Key Characteristics
- **Latest-per-key retention**: All previous values for a key are asynchronously removed
- **Tombstone records**: Publishing a message with a null value deletes the key from the compacted log
- **CDC integration**: Debezium uses compacted topics to publish database changelogs

### When to Use
- Consumers need only the current state per entity (user profile, product price, config)
- New consumers should start from the latest state without replaying full history
- Building a distributed changelog for database tables (CDC / Debezium)

### When NOT to Use
- Full event history is required (use a regular time-retained topic for audit trails)
- Events carry no meaningful key (compaction has no effect without stable keys)

### Also see
- [Partition](#partition) · [Kafka Transactions](#kafka-transactions) · [CQRS & Event-Driven: Event Sourcing](cqrs-event-driven.md#event-sourcing)

---


## Stream-Table Duality

The insight — central to Kafka Streams and ksqlDB — that a **stream** and a **table** are two views of the same underlying data: a stream is a table in motion (each event is a change), and a table is a stream at rest (the accumulated latest state). The two can be converted between each other and joined in real time.

### Key Characteristics
- **Stream → Table**: Aggregate events (e.g., count clicks per user) to produce a materialized view
- **Table → Stream**: Emit a changelog of every row update as a stream of events
- **Stream-Table join**: Enrich each stream event with the corresponding table row (e.g., click + user profile)
- **Local state stores**: Kafka Streams uses RocksDB-backed state stores for sub-millisecond table lookups

### When to Use
- Real-time enrichment: join a high-throughput event stream with slowly-changing reference data
- Materialized views that must update as new events arrive
- Real-time dashboards and monitoring where aggregations must reflect the latest state

### When NOT to Use
- Reference tables too large for available memory (spills to disk, degrading performance)
- Join semantics require point-in-time consistency across both sides (Kafka joins are approximate)

### Also see
- [Compacted Topic](#compacted-topic) · [Partition](#partition) · [Kafka Transactions](#kafka-transactions)

---


## Hot Partition

A Kafka partition that receives a **disproportionately large share of traffic** because too many messages are routed to the same partition. Caused by low-cardinality partition keys (e.g., `country_code`, `status`) where a small number of distinct values map to a small subset of partitions.

### Key Characteristics
- **Throughput ceiling**: only one consumer in a group can read from a partition at a time, so the hot partition becomes a throughput bottleneck for the entire consumer group
- **Uneven broker load**: the broker hosting the hot partition's leader handles all reads and writes for that partition
- **Metric**: coefficient of variation (CV) of `BytesInPerPartition` > 1.0 indicates a severely skewed distribution

### When to Identify
- Partition skew: one consumer is saturated while others are idle
- `BytesInPerPartition` CloudWatch metric shows one partition with multiples of the average load

### How to Mitigate
- Switch to a high-cardinality key (`order_id`, `user_id`, `device_id`) to distribute load across all partitions
- Apply **salting** (append a random suffix to the key) to spread an unavoidably hot key — but this breaks per-key ordering
- Increase partition count and redistribute consumers

### Also see
- [Partition](#partition) · [Message Ordering](#message-ordering) · [Consumer Group](#consumer-group)

---


## Retry Topic

A dedicated Kafka topic used to implement **delayed retry with exponential backoff** without blocking the main consumer. Failed messages are routed to a retry topic tagged with a `scheduled_at` timestamp; a separate retry consumer reads from the topic but waits until the scheduled time before re-processing.

### Key Characteristics
- **Tiered topology**: multiple retry topics per delay tier (`main.retry_1s`, `main.retry_5s`, `main.retry_30s`, `main.dlq`)
- **Non-blocking main consumer**: the main consumer commits the offset and routes the failure immediately — it never sleeps
- **Envelope schema**: the retry message wraps the original payload with metadata (`stage`, `error_type`, `scheduled_at`, `retry_count`)
- **Terminal tier**: after exhausting all retry tiers, the message routes to the Dead Letter Queue

### When to Use
- Transient failures that benefit from a delay before retry (database deadlocks, rate limits, network blips)
- Any system where `time.sleep()` inside a consumer would block partition processing and starve healthy messages

### When NOT to Use
- Permanent failures (schema mismatch, invalid business data) — route directly to DLQ instead of retrying
- Very high throughput where dozens of extra topics become unmanageable

### Also see
- [Dead Letter Queue (DLQ)](#dead-letter-queue-dlq) · [Poison Message](#poison-message) · [Resilience: Exponential Backoff](resilience.md#exponential-backoff)

---


## KTable

The **changelog-backed, locally materialised table** abstraction in Kafka Streams. While a **KStream** represents an unbounded stream of events (append-only, every record is an insert), a **KTable** represents the **current latest value per key** — updated in place as new events arrive from the underlying compacted changelog topic.

### Key Characteristics
- **Backed by a compacted topic**: Kafka maintains the full changelog; the KTable is a live materialised view that keeps only the most recent value per key
- **Local RocksDB store**: each Kafka Streams instance embeds a co-partitioned RocksDB store containing its shard of the KTable — joins require no network calls, only local disk lookups
- **KStream.leftJoin(KTable)**: enriches every stream event with the matching table row (e.g., click event + user profile) at sub-millisecond latency; the join is a local RocksDB `get()` call
- **Partition co-location**: stream and table topics must share the same partition count and key scheme; if they differ, Kafka Streams automatically inserts a repartition step (adds latency and a new topic)
- **KStream vs KTable**: `KStream` is the event-by-event changelog view; `KTable` is the aggregated latest-state view. The two are duals — `stream.groupByKey().reduce(...)` produces a KTable; `table.toStream()` produces a KStream

### When to Use
- Enriching a high-throughput event stream with slowly changing reference data (user profiles, product catalog, device metadata)
- Building materialised views that update incrementally as events arrive, without querying a remote database
- Replacing synchronous per-event database lookups in a stream processor

### When NOT to Use
- Reference tables exceeding local disk capacity (~10–50 GB per partition in practice); joins degrade as RocksDB spills increase
- When you need point-in-time historical lookups (KTable retains only the latest value per key)
- When partition co-location cannot be guaranteed and the repartition overhead is unacceptable

### Also see
- [Stream-Table Duality](#stream-table-duality) · [Compacted Topic](#compacted-topic) · [Kafka Transactions](#kafka-transactions)

---


## Claim Check

Store a **large payload in external storage** and pass only a reference (the "claim check") in the message. The reference acts like a coat-check ticket — small enough to traverse the broker, containing all the information the consumer needs to retrieve the full payload.

### Key Characteristics
- **Payload externalised**: large binaries (images, PDFs, ML artefacts) live in S3 or equivalent object storage; the Kafka message carries only `{s3_bucket, s3_key, checksum, size_bytes, content_type}`
- **Size threshold**: Kafka's default maximum message size is 1 MB; payloads > ~100 KB benefit from Claim Check; anything > 1 MB requires it
- **Orphaned object problem**: if S3 upload succeeds but the Kafka send fails, the payload is stranded with no consumer — write the orphan key to a DynamoDB tracking table and run a daily Lambda cleanup job to purge unclaimed objects
- **Lazy loading vs presigned URL**: if payload < ~50 MB, download directly in the consumer; if ≥ 50 MB, generate a time-limited S3 presigned URL and delegate streaming to downstream processors to avoid loading large bytes into consumer memory
- **Lifecycle cost**: S3 Standard (~$0.023/GB) is ~4× cheaper than MSK EBS storage (~$0.10/GB); apply lifecycle policies to transition to S3 Glacier at 30 days and delete at 90 days

### When to Use
- Any message broker with a payload size limit (Kafka 1 MB default, SQS 256 KB)
- Large user uploads: images, PDFs, videos, log files, ML training data
- When payload lifetime policies (GDPR deletion, archiving) must be managed independently of the message log

### When NOT to Use
- Payloads smaller than ~10 KB where the S3 round-trip overhead outweighs the broker savings
- Systems where strict exactly-once guarantees must span both the broker and the object store (two-phase coordination is complex)

### Also see
- [Claim Check Pattern](../architecture-general/03-integration-communication-architecture/messaging-patterns/claim-check.md) · [Event Carried State Transfer](cqrs-event-driven.md#event-carried-state-transfer) · [Compacted Topic](messaging.md#compacted-topic)

---


## Distributed Commit Log

An **append-only, immutable, ordered log** distributed across multiple machines. Unlike a traditional message queue where the broker manages per-message delivery state, a distributed commit log only appends messages sequentially to on-disk logs. Consumers independently track their own read position (offset), removing coordination overhead from the broker. Apache Kafka is the canonical implementation.

### Key Characteristics
- **Append-only**: Messages are never mutated — only appended; enables sequential disk writes at near hardware limit
- **Consumer-managed offsets**: The broker does not track who has read what — consumers commit their own progress
- **Immutable history**: Messages persist based on retention policy (time/size), not consumption status — enables replay
- **Partitioned**: The log is sharded into partitions for horizontal scaling across brokers

### When to Use
- Event streaming and high-throughput messaging where millions of messages per second are required
- Systems that need event replay, audit trails, or long-term event history
- When producers and consumers should be fully decoupled — producers never wait for consumers

### When NOT to Use
- Task queues with per-message acknowledgment and complex routing logic (RabbitMQ is a better fit)
- Low-throughput systems where operational complexity of Kafka outweighs its benefits
- When strict global message ordering across all partitions is required

### Also see
- [Kafka vs RabbitMQ](messaging.md#kafka-vs-rabbitmq) · [Partition](messaging.md#partition) · [Zero-Copy Transfer](#zero-copy-transfer) · [Message Batching](#message-batching)

---


## Message Batching

The practice of **accumulating multiple messages into a single batch** before writing to disk or sending over the network. In Kafka, producers batch messages (controlled by `linger.ms` and `batch.size`) and consumers fetch entire batches at once. Batching converts many small I/O operations into fewer large sequential operations, dramatically improving throughput at the cost of a small increase in latency.

### Key Characteristics
- **Throughput over latency**: Optimizes for messages-per-second rather than per-message delivery time
- **Configurable delay**: `linger.ms` introduces artificial wait time to fill batches before sending
- **Often combined with compression**: Compression is applied at the batch level for better ratios than per-message compression
- **Network efficiency**: Fewer, larger TCP packets reduce per-packet overhead

### When to Use
- High-throughput streaming pipelines where a few milliseconds of additional latency is acceptable
- When network bandwidth or disk I/O is the bottleneck rather than CPU
- Batch processing systems that naturally accumulate messages before processing

### When NOT to Use
- Low-latency use cases where messages must be delivered in single-digit milliseconds
- Systems with very low message rates — batching adds unnecessary delay with no throughput gain
- When message ordering within a batch matters and batches may fail partially

### Also see
- [Zero-Copy Transfer](#zero-copy-transfer) · [Distributed Commit Log](#distributed-commit-log) · [Consumer Lag](messaging.md#consumer-lag)

---


## Replay (Kafka Reprocessing)

The ability to **reset consumer offsets to an earlier point in the log** and reprocess historical events — for bug fixes, schema migrations, new business logic, or recovery from corruption. In Kafka, replay is possible because messages are retained based on a time/size policy rather than deleted after consumption, unlike traditional message queues.

Replay is not an edge case or recovery mechanism — it is a **core design feature** of event-streaming systems. A system that cannot replay safely (without corruption, duplication, or side-effect damage) is not production-ready.

### Key Characteristics
- **Offset-based**: Consumers reset their position to an earlier offset and resume processing from that point
- **Retention-dependent**: Replay window is bounded by the topic's retention policy (e.g., 7 days, 30 days, or forever for compacted topics)
- **Requires idempotency**: Replaying the same events must produce the same outcome — idempotent consumers are a prerequisite
- **Intentional, not accidental**: Replay is triggered deliberately for migrations or fixes, not as a crash-recovery mechanism (which offset commits handle)

### When to Use
- Deploying a new consumer with enriched logic that must backfill historical data
- Fixing a processing bug where already-consumed events produced incorrect results
- Schema migrations where events must be reprocessed against a new schema version
- Rebuilding read models or projections from the event stream

### When NOT to Use
- As a substitute for proper error handling — replay is for intentional reprocessing, not crash recovery
- When retention is too short to cover the needed replay window
- When side effects are not idempotent and cannot be made idempotent

### Also see
- [Offset Commit](#offset-commit) · [Idempotent Consumer](#idempotent-consumer) · [Distributed Commit Log](#distributed-commit-log) · [Compacted Topic](#compacted-topic)

---


## Producer Acknowledgement

The **confirmation from a Kafka broker to a producer** that a message has been successfully received and (depending on the `acks` setting) replicated. Producer acknowledgements are the bridge between async fire-and-forget publishing and guaranteed delivery.

| `acks` Setting | Behaviour | Durability | Latency |
|:---|:---|:---|:---|
| `acks=0` | Producer does not wait for any acknowledgement | None — messages may be lost | Lowest |
| `acks=1` | Leader broker acknowledges after writing to its local log | Leader-only — lost if leader fails before replication | Low |
| `acks=all` (or `-1`) | Leader waits for all in-sync replicas to acknowledge | Highest — survives up to `min.insync.replicas - 1` failures | Highest |

### Key Characteristics
- **Durability-latency tradeoff**: Stronger acknowledgements (acks=all) increase durability at the cost of producer latency
- **Bounded retries**: Failed acknowledgements trigger retries (configurable via `retries` and `delivery.timeout.ms`)
- **Idempotent producer**: When combined with `enable.idempotence=true`, retries do not produce duplicates
- **Async by default**: Producers send messages asynchronously; the acknowledgement arrives on a callback

### When to Use
- `acks=all` when data loss is unacceptable (financial events, audit logs, user activity with compliance needs)
- `acks=1` when throughput matters more than absolute durability and occasional loss is tolerable
- `acks=0` only for metrics or non-critical telemetry where throughput is paramount

### When NOT to Use
- `acks=0` for any data that feeds business decisions or analytics
- Blindly setting `acks=all` without also configuring `min.insync.replicas` — the setting is meaningless if all replicas are not in-sync

### Also see
- [At-Least-Once Semantics](#at-least-once-semantics) · [Exactly-Once Semantics](#exactly-once-semantics) · [Idempotent Consumer](#idempotent-consumer) · [Message Batching](#message-batching)

---


## Schema Registry

A **centralized service for managing and validating schemas** (Avro, Protobuf, JSON Schema) used by Kafka producers and consumers. The schema registry stores versioned schemas, enforces compatibility rules, and serializes/deserializes data — ensuring that producers and consumers agree on the structure of messages without embedding the schema in every payload.

Without a schema registry, schema changes are silent and breaking — a consumer receives bytes it cannot parse. With a schema registry, incompatible schema changes are rejected at producer registration time, before any data is published.

### Key Characteristics
- **Compatibility enforcement**: BACKWARD, FORWARD, FULL, or NONE — checked at schema registration, not at runtime
- **Schema evolution**: Each schema version is stored immutably; consumers can request the specific version they understand
- **Reduced payload size**: The schema ID (4–8 bytes) is sent with each message instead of the full schema
- **Language-agnostic**: Avro/Protobuf schemas generate code in multiple languages from the same schema definition

### When to Use
- Any Kafka topic consumed by multiple independent teams
- Event streams where the producing service evolves independently of consumers
- Systems with compliance or audit requirements that need a record of schema changes over time

### When NOT to Use
- Single-team internal topics where schema changes are coordinated directly
- Prototypes where schema stability is not yet established
- Very high-throughput topics where the registry lookup adds unacceptable latency (mitigated by client-side caching)

### Also see
- [Schema Contract](#schema-contract-event-as-public-api) · [Backward Compatibility](../api-design.md#backward-compatibility) · [Contract-First Design](../api-design.md#contract-first-design) · [Event Sourcing](../cqrs-event-driven.md#event-sourcing)

---


## Schema Contract (Event as Public API)

The principle that **Kafka topic schemas are public, versioned contracts** between producers and consumers — not internal DTOs that can change freely. Once a topic has multiple independent consumer teams, its schema becomes a shared API with all the governance requirements of a REST or gRPC endpoint: backward compatibility, deprecation windows, and migration paths.

> "Kafka topics become public APIs whether you want them to or not."

### Key Characteristics
- **Backward compatibility is mandatory**: New schema versions must not break existing consumers
- **No downstream assumptions**: Events carry only the data the producer owns; consumers enrich from their own sources
- **Versioned explicitly**: Schema changes are tracked through a schema registry (e.g., Confluent Schema Registry, AWS Glue)
- **Breaking changes are migrations**: Removing or redefining a field is a migration with a planned window, not a code change

### When to Use
- Any Kafka topic consumed by more than one team or service
- Event streams that feed multiple downstream systems (analytics, real-time dashboards, ML pipelines)
- Systems where the producing service evolves independently of consumers

### When NOT to Use
- Internal topics with a single producer and single consumer owned by the same team
- Prototypes or experiments where the schema is still unstable

### Also see
- [Schema Registry](#schema-registry) · [Event Sourcing](../cqrs-event-driven.md#event-sourcing) · [Contract-First Design](../api-design.md#contract-first-design) · [Backward Compatibility](../api-design.md#backward-compatibility)

---


## Event-Time

The timestamp **when an event actually occurred** in the real world, embedded in the event payload by the producer. Contrast with processing-time, which is when the stream processor observed the event. Event-time is the authoritative time for correctness in stream processing.

### Key Characteristics
- **Producer-assigned**: The producing device or service sets the timestamp based on its local clock
- **Immutable in transit**: Once set, event-time is never modified by brokers or consumers
- **Clock skew risk**: Different devices may have different clocks — event-time is only as trustworthy as the producer's clock

### When to Use
- IoT/device data where network delays cause late arrival (event-time tells you *when it happened*, not when you received it)
- Financial transactions where the transaction timestamp matters for regulatory compliance
- Any streaming use case where the business question is "what happened at time T?" not "what did we observe at time T?"

### When NOT to Use
- When producers cannot provide reliable timestamps (no NTP sync, no clock at all)
- Log ingestion where processing-time is sufficient (simple monitoring, debug logs)

### Also see
- [Processing-Time](#processing-time) · [Watermarking](#watermarking)

---


## Processing-Time

The timestamp **when the stream processor receives or observes an event** — the wall-clock time of the processing node. Simpler than event-time but can produce incorrect results when events arrive late or out of order.

### Key Characteristics
- **System-assigned**: Set by the stream processor, not the producer
- **Deterministic per run**: Given the same input stream replayed, processing-time windows produce different results
- **Zero configuration**: No watermarking or lateness handling needed

### When to Use
- Best-effort monitoring dashboards where approximate counts are acceptable
- Simple rate-limiting or throttling based on current throughput
- Prototypes where correctness requirements are not yet defined

### When NOT to Use
- Any use case where "when did it happen?" matters more than "when did we see it?"
- Financial, IoT, or compliance workloads where event-time semantics are required
- Scenarios with significant network delays or batching that cause event-time/processing-time divergence

### Also see
- [Event-Time](#event-time) · [Watermarking](#watermarking)

---


## Watermarking

A **threshold mechanism in stream processing** that defines how long to wait for late-arriving events before closing a time window and emitting results. A watermark with timestamp T declares: "all events with event-time < T have arrived; windows up to T can now be finalized."

### Key Characteristics
- **Lateness bound**: The watermark defines the maximum expected delay between event-time and processing-time
- **Trade-off**: Longer watermark = more complete results but higher latency; shorter watermark = faster results but more missed late events
- **Heuristic by nature**: Watermarks are a best-effort mechanism — some events may still arrive after the watermark

### Example: Tumbling Window with 15s Watermark Buffer

```
Scenario: 1-minute window [12:00:00 - 12:01:00] with 15s allowed lateness.

Timeline:
├─ 12:00:20  Event E1 (Event-Time: 12:00:15) arrives ──► Placed in window [12:00 - 12:01]
├─ 12:01:05  Event E2 (Event-Time: 12:00:50) arrives ──► Placed in window [12:00 - 12:01] (Late, but within buffer)
├─ 12:01:15  System clock reaches 12:01:15            ──► Watermark reaches 12:01:00 (12:01:15 - 15s)
│                                                         WINDOW CLOSES & Emits Result: count = 2
└─ 12:01:25  Event E3 (Event-Time: 12:00:45) arrives ──► Event-Time (12:00:45) < Watermark (12:01:00)
                                                          DROPPED or routed to Dead Letter Queue (DLQ)
```

### When to Use
- Windowed aggregations where completeness matters (hourly/daily rollups, billing)
- IoT pipelines where device data can be delayed by hours due to connectivity gaps
- Any streaming use case with a defined SLA for result freshness vs completeness

### When NOT to Use
- Per-event processing with no windowing (each event is processed independently)
- When all producers have guaranteed low-latency delivery (processing-time windows suffice)
- When incomplete windows are acceptable and freshness is the priority

### Also see
- [Event-Time](#event-time) · [Processing-Time](#processing-time) · [Consumer Lag](#consumer-lag) · [Low-Watermark / High-Watermark](databases.md#low-watermark-high-watermark)

---


## Offset Alignment

The process of **ensuring consumer offsets are consistent across two Kafka clusters** during multi-region disaster recovery or active-active replication. After failing over from a primary to a DR cluster, consumers must resume from the correct offset to avoid data loss or duplication.

### Key Characteristics
- **Cluster-specific offsets**: Offsets are local to each cluster — the offset for the same message differs between primary and DR
- **Consumer offset translation**: Tools like MirrorMaker 2 emit offset translation records (`__consumer_offsets`) to map between clusters
- **Failover window**: The gap between the last committed offset on the primary and the last replicated message on DR determines potential data loss

### When to Use
- Multi-region Kafka deployments with active-passive or active-active replication
- Disaster recovery planning where consumers must fail over to a different cluster
- Migration from one Kafka cluster to another without resetting consumer positions

### When NOT to Use
- Single-cluster deployments (no offset translation needed)
- When consumers can safely start from the earliest or latest offset after failover (non-critical workloads)

### Also see
- [Offset Commit](#offset-commit) · [Consumer Group](#consumer-group) · [Rebalance](#rebalance)

---


## Apache Flink

**Apache Flink** is an open-source, distributed stream processing framework designed for stateful computations over unbounded and bounded data streams. It provides exactly-once consistency guarantees, high throughput with low latency, and sophisticated state management — making it ideal for continuously evolving results like real-time aggregations, leaderboards, and fraud detection.

### Key Characteristics
- **Stateful processing**: Maintains and updates state over time (running totals, session windows, pattern detection) with exactly-once guarantees
- **Event-time processing**: Handles out-of-order events correctly using watermarks, not just processing-time
- **Checkpointing**: Asynchronous, incremental snapshots of operator state for failure recovery without reprocessing the entire stream
- **Unified batch/streaming**: Batch is treated as a special case of streaming (bounded streams), enabling the same code for both paradigms

### When to Use
- Continuously changing results that depend on accumulated state (election totals, leaderboards, real-time dashboards)
- Complex event processing with windowed aggregations, pattern matching (CEP), and multi-stream joins
- Pipelines requiring exactly-once semantics end-to-end (with transactional sinks like Kafka or Iceberg)

### When NOT to Use
- Simple stateless transformations where Kafka Streams or a few Kafka consumers + a database suffice
- When the team lacks operational experience with distributed stream processors — Flink's checkpointing and state backend configuration require expertise
- Batch-only workloads where Spark or a SQL engine provides simpler alternatives

### Also see
- [Kafka (Decoupling)](#) · [Stream Processing](../system-design-architecture/stream-processing/) · [Event-Driven Architecture](../reference-dictionary/cqrs-event-driven.md#event-driven-architecture)


## Write-Ahead Buffer

A **local, durable staging area** placed between an application and a remote message broker (e.g., Kafka). Events are first written synchronously to this local buffer, then asynchronously published to the broker. If the broker is unavailable or the async publish fails, events remain safe in the local buffer and are retried later.

> "Write to local disk first, publish to Kafka second."

### Key Characteristics
- **Durable before publish**: Events survive application crashes, restarts, and extended broker outages
- **Decouples user latency from broker availability**: The user-facing request is acknowledged once the local write completes, not when Kafka confirms
- **Append-only with compaction**: Events are appended, then compacted (deleted) after successful broker publish
- **Common implementations**: Local file on disk, embedded SQLite, RocksDB, or a dedicated WAL library

### When to Use
- Zero-data-loss requirements where async publishing is used to avoid blocking user requests
- Systems where Kafka may experience extended unavailability and in-memory buffers would overflow
- High-throughput ingestion pipelines where every event must be accounted for

### When NOT to Use
- When the broker itself is the system of record and local durability adds unnecessary complexity
- Low-throughput systems where synchronous producer acks with retries are sufficient
- When disk I/O on the producer side would become a bottleneck (measure first)

### Also see
- [Producer Acknowledgement](../messaging.md#producer-acknowledgement) · [At-Least-Once Semantics](../messaging.md#at-least-once-semantics) · [Idempotent Consumer](../messaging.md#idempotent-consumer)

---


## Log Segment

The **physical on-disk storage unit** of a Kafka partition. Each partition is composed of multiple log segment files, not a single monolithic file. Kafka appends records sequentially to the active segment and rolls to a new segment when the size limit is reached.

Each segment consists of three files:
- **`.log`** — Raw binary records appended sequentially; the data file.
- **`.index`** — Sparse offset-to-position mapping for fast lookups (does not index every record).
- **`.timeindex`** — Timestamp-to-offset mapping for time-based seek operations.

### Key Characteristics
- **Atomic records**: A record is never split across segments. If a record would overflow the current segment, Kafka closes the segment early and creates a new one.
- **Immutable once rolled**: Once a segment is closed (rolled), it is never modified — only the active segment receives writes.
- **Default size**: `log.segment.bytes` defaults to 1 GB; segments roll when this threshold is reached or `log.roll.ms` expires.
- **Sparse index**: The `.index` file maps every Nth record to its byte position, not every record — keeps the index small at the cost of occasional in-segment scans.

### When to Use
- Understanding Kafka's disk I/O behavior for capacity planning and performance tuning
- Debugging disk usage: large segments mean fewer files but longer recovery; small segments mean more file descriptors

### When NOT to Use
- Application-level concerns — segments are an internal Kafka implementation detail and should not drive business logic decisions

### Also see
- [Partition](#partition) · [Distributed Commit Log](#distributed-commit-log) · [Replication Factor](#replication-factor)

---


## ISR (In-Sync Replica)

The **subset of partition replicas that are fully caught up with the leader**. An ISR is a follower that has replicated all committed messages from the leader within a configurable time window (`replica.lag.time.max.ms`, default 30 seconds). Only ISR members are eligible to become the new leader during failover.

The ISR set is dynamic: followers that fall behind are removed from the ISR; followers that catch up are re-added. This mechanism ensures that leader election always promotes a replica with a complete copy of committed data.

### Key Characteristics
- **Dynamic membership**: Followers enter and leave the ISR based on replication lag — not a static configuration
- **Lag threshold**: Controlled by `replica.lag.time.max.ms` — if a follower hasn't fetched from the leader within this window, it is removed from the ISR
- **Durability contract**: `acks=all` means the leader waits for all ISR members (not all configured replicas) to acknowledge
- **Minimum ISR**: `min.insync.replicas` sets the floor — if the ISR shrinks below this count, the broker rejects writes

### When to Use
- Configuring durability: `min.insync.replicas=2` with `replication_factor=3` means 2 ISRs must acknowledge each write
- Monitoring cluster health: shrinking ISR count signals network issues or overloaded brokers

### When NOT to Use
- As a static configuration — the ISR is a runtime concept, not a setting you directly control (you control `min.insync.replicas` and `replica.lag.time.max.ms`)

### Also see
- [Replication Factor](#replication-factor) · [Producer Acknowledgement](#producer-acknowledgement) · [Partition](#partition)

---


## Replication Factor

The **number of copies of each partition** maintained across the Kafka cluster. A replication factor of N means each partition has 1 leader and N-1 followers distributed across different brokers. This is the primary mechanism for Kafka's fault tolerance: the cluster can survive up to (replication_factor - 1) broker failures without data loss.

### Key Characteristics
- **Per-topic configuration**: Set at topic creation time via `--replication-factor`; cannot be changed for existing topics without a partition reassignment
- **Common values**: `replication_factor=3` is the production standard — tolerates 2 broker failures while keeping storage cost manageable
- **Storage multiplier**: Total disk usage = data size × replication_factor; plan capacity accordingly
- **Broker distribution**: Followers are placed on different brokers from the leader to ensure broker failure doesn't eliminate all copies

### When to Use
- `replication_factor=3` for all production topics with durability requirements
- `replication_factor=1` only for development or data that can be easily regenerated
- Higher values (5+) for topics with extreme durability requirements and sufficient infrastructure budget

### When NOT to Use
- `replication_factor=1` in production — a single broker failure causes permanent data loss
- Excessively high replication factors that consume storage without proportional durability gains beyond 3–5

### Also see
- [ISR (In-Sync Replica)](#isr-in-sync-replica) · [Producer Acknowledgement](#producer-acknowledgement) · [Partition](#partition) · [Log Segment](#log-segment)

---


## Kafka Streams

A Java library (part of Apache Kafka) for building real-time stream processing applications and microservices. It provides a high-level DSL for stateful operations (joins, aggregations, windowing) directly on Kafka topics, with exactly-once semantics and local state stores backed by RocksDB — no separate cluster required.

### Key Characteristics

- **Embedded library**: Runs inside your application JVM — no separate processing cluster (unlike Flink or Spark)
- **KTable and KStream duality**: KStream is an append-only event log; KTable is a changelog representing the latest state per key — enables stream-table joins
- **Local state with RocksDB**: Stateful operations (aggregations, joins) use embedded RocksDB instances for local state, with changelog topics in Kafka for fault tolerance
- **Exactly-once semantics**: End-to-end exactly-once processing via Kafka transactions — no duplicate results even after consumer rebalances
- **Partition-level parallelism**: Each partition is processed by one stream thread; scaling is achieved by adding threads or instances

### When to Use

- Real-time aggregations and windowed computations directly on Kafka topic data
- Stream-table joins (e.g., enrich event stream with reference data from a compacted topic)
- Applications that need exactly-once processing guarantees without external state stores
- When operational simplicity matters — single library dependency, same Kafka cluster, no additional infrastructure

### When NOT to Use

- Complex event processing requiring advanced windowing semantics (session windows with late-arrival handling) — consider Apache Flink
- SQL-based stream processing preferred by analysts — consider ksqlDB or Flink SQL
- Non-JVM ecosystems where a polyglot processing framework is needed — consider Flink (supports Python, SQL, Java)
- Batch+stream unification (Lambda architecture replacement) — consider Flink or Spark Structured Streaming

### Also see

- [Partition](#partition) · [Consumer Group](#consumer-group) · [KTable](#ktable) · [Exactly-Once Semantics](#exactly-once-semantics) · [Apache Flink](#apache-flink)

---


## Stream Sessionization

A stateful stream processing pattern that aggregates discrete, out-of-order, and asynchronous events into cohesive, higher-level session records based on a common correlation key (e.g., `session_id`, `ad_id`, or `user_id`) and inactivity gap intervals.

### Key Characteristics
- **Keyed State Accumulation**: Stream processing engines (such as Apache Flink or Kafka Streams) maintain managed in-memory/RocksDB state keyed by session identifier, accumulating milestones (e.g. ad start, quartiles, pause, complete, click)
- **Gap-Based Windowing & Watermarks**: Closes session windows dynamically when an inactivity timeout gap elapses or an explicit terminal event is received, utilizing event-time watermarking to handle late-arriving network events
- **Analytical Simplification**: Transforms billions of fragmented telemetry events into clean, pre-aggregated analytical entities for downstream OLAP ingestion, advertiser reporting, and financial accounting

### When to Use
- Advertising platforms tracking multi-stage ad playback telemetry (impressions, quartile heartbeats, completion, user interactions)
- User web/mobile analytics grouping clickstream events into browsing sessions
- IoT and telemetry systems consolidating sensor bursts into distinct diagnostic sessions

### When NOT to Use
- Simple point-in-time threshold alerting where events do not require cross-event state retention
- Purely stateless message transformations or point-to-point event routing

### Also see
- [Apache Flink](#apache-flink) · [Event-Time](#event-time) · [Watermarking](#watermarking) · [Kafka Streams](#kafka-streams)

---


## Stream-Stream Join

A stateful stream processing pattern that correlates and joins two or more independent, unbounded event streams (e.g., ad serving decisions and client playback telemetry, or payment authorizations and settlement callbacks) based on a shared correlation key over a bounded temporal window.

### Key Characteristics
- **Keyed Co-Processing (`KeyedCoProcessFunction`)**: Stream processing engines (such as Apache Flink) partition both streams by a shared correlation ID and manage in-operator state (e.g., `ValueState` or `ListState`) to hold early-arriving records.
- **Asymmetric Arrival Handling**: Either stream can arrive first: if the context record exists in state when the event arrives, enrichment occurs immediately; if the event arrives first, it is buffered until the context record is received.
- **Bounded State TTL & DLQ Flush**: In-operator state is guarded by an expiration timer (e.g., 60 minutes) to prevent unbounded memory growth; records that fail to match within the window expire and are emitted to a Dead-Letter Queue (DLQ) for batch reconciliation.
- **Hot-Path Decoupling**: Replaces synchronous database writes on high-throughput serving paths with asynchronous event log publication, eliminating database write bottlenecks during massive traffic surges (e.g., live sports ad breaks).

### When to Use
- Real-time event enrichment joining high-velocity client telemetry with upstream decision logs (ad tech, clickstream enrichment, IoT sensor correlation).
- Complex event processing (CEP) detecting multi-step transactions occurring across separate event topics within a time boundary.
- Systems requiring elastic auto-scaling where synchronous database lookups create latency bottlenecks or availability risks.

### When NOT to Use
- Static or slowly changing dimension lookups where a broadcast stream, local cache, or distributed cache lookup suffices (Stream-Table join).
- Scenarios requiring cross-stream joins across multi-day or multi-week historical intervals without strict real-time constraints (prefer batch ETL / lakehouse joins).

### Also see
- [Apache Flink](#apache-flink) · [Stream Sessionization](#stream-sessionization) · [In-Stream Keyed Deduplication](#in-stream-keyed-deduplication) · [Claim Check](#claim-check)

---


## In-Stream Keyed Deduplication

A stream processing deduplication pattern where duplicate events generated by upstream at-least-once delivery or client retries are dropped in-memory/in-operator-state without making external database network roundtrips.

### Key Characteristics
- **Deterministic Hash Partitioning**: Computes a stable hash key derived from immutable event payload fields (`Hash(ad_id, event_type, offset)`) and partitions the stream by this hash ID (`keyBy(hash_id)`).
- **Colocated Operator State**: Because identical events hash to the exact same key, all duplicates route to the same stateful task instance. The operator tracks seen IDs in a local state store with a short time-to-live (e.g. 10 minutes).
- **Zero Network Overhead & No Lock Contention**: Completely removes external database check-and-write queries from the hot ingestion path, eliminating database connection exhaustion and race conditions.
- **Tiered Idempotency**: Provides best-effort, sub-second duplicate elimination for >99.99% of stream events, while propagating the unique transaction ID downstream so financial billing systems can perform authoritative idempotent upserts.

### When to Use
- High-velocity stream ingestion pipelines processing hundreds of thousands of events per second where upstream producers retry on transient network blips.
- Ad impression tracking, payment event ingestion, or clickstream counters where duplicate processing causes metric inflation or billing errors.
- Stateful stream joins where duplicates would trigger repeated downstream emissions or corrupt session state.

### When NOT to Use
- Systems where duplicates arrive days or weeks apart beyond the feasible streaming state retention window (handle in batch storage).
- Stateless event pipelines where downstream consumers already execute fully idempotent upserts and have excess capacity.

### Also see
- [Idempotent Consumer](#idempotent-consumer) · [Client-Side Deduplication](#client-side-deduplication) · [Atomic Deduplication](#atomic-deduplication) · [Deduplication Window](#deduplication-window)

---


## Deterministic Consumer

An asynchronous event consumer engineered so that processing a given sequence of events produces the exact same state outcome regardless of execution timing, batching boundaries, network retransmissions, or the number of times the stream is reprocessed from historical offsets.

### Key Characteristics
- **Side-Effect Isolation**: Isolates state projection writes from outbound side effects (such as sending emails, dispatching push notifications, or calling third-party charge APIs).
- **Pure State Transformation**: Treats state updates as pure functions of the previous state and incoming event data ($State_{n} = f(State_{n-1}, Event)$), eliminating dependencies on local system time, non-deterministic random IDs, or ambient environment state.
- **Replay Safety**: Enables replaying millions of historical events to recover from corruptions, rebuild search indexes, or migrate schemas without producing corrupt state or duplicate external interactions.
- **Explicit Version & Timestamp Gating**: Uses event timestamps and domain version checks rather than local arrival order to guard against out-of-order writes.

### When to Use
- Materialized read-model projection consumers in CQRS architectures.
- Stream processing pipelines where jobs may fail and recover from distributed checkpoints or savepoints.
- Consumers that must support on-demand historical replays for auditing, bug fixes, or disaster recovery.

### When NOT to Use
- Real-time notification dispatchers where duplicate delivery during manual replays is intentionally acceptable and side-effect gating adds unnecessary complexity.
- Purely stateless telemetry ingestion pipes that immediately forward raw metrics to an external monitoring vendor.

### Also see
- [Idempotent Consumer](#idempotent-consumer) · [Replay (Kafka Reprocessing)](#replay-kafka-reprocessing) · [Deterministic Processing](cqrs-event-driven.md#deterministic-processing) · [Versioned Aggregates](cqrs-event-driven.md#versioned-aggregates)

---


## Resolved State Consumption

An architectural pattern where downstream services consume already-reconciled, authoritative entity state emitted by the aggregate-owning service, rather than independently consuming and re-ordering raw, out-of-order event streams.

### Key Characteristics
- **Centralized Ordering Logic**: Only the authoritative service owning the aggregate executes version validation, guard checks, and concurrency control.
- **Deduplication of Complexity**: Downstream systems receive clean, monotonically updated state projections (e.g., `OrderStateUpdated { id, version: 3, state: 'COMPLETED' }`) instead of raw, potentially reordered lifecycle deltas (`OrderCreated`, `PaymentCaptured`, `PaymentRefunded`).
- **Elimination of Multi-Implementation Divergence**: Prevents the failure mode where ten different consumer teams each implement subtly different sorting, buffering, or race-resolution rules against the same raw event topic.
- **Contract Boundary Clarity**: Establishes a clean interface between internal domain aggregate transitions and external integration events.

### When to Use
- Multi-service event-driven architectures where downstream services need current entity facts for search indexes, notifications, or reporting.
- High-scale systems where downstream consumer teams should not need deep internal domain context to reason about entity ordering.
- Systems with at-least-once messaging brokers where rebalances and retries frequently invert raw message delivery.

### When NOT to Use
- Event sourcing rebuilds within the owning service itself (the owning service must process the full raw event history).
- Pure event-notification triggers where downstream services immediately call back into the owning service via synchronous RPC for current state.

### Also see
- [Versioned Aggregates](cqrs-event-driven.md#versioned-aggregates) · [Idempotent Consumer](#idempotent-consumer) · [Single Source of Truth](architecture-patterns.md#single-source-of-truth)

---


## Federated Kafka Clusters

An infrastructure architecture pattern where an organization splits its message streaming estate into multiple independent, dedicated Kafka clusters segmented by business domain, workload criticality, data residency, or tenant SLA, rather than scaling a single monolithic cluster.

### Key Characteristics
- **Blast Radius Containment**: A broker crash, runaway topic, misconfigured producer spike, or Zookeeper/KRaft metadata lockup is isolated to a single cluster, preventing enterprise-wide outages.
- **Routing Layer Abstraction**: Client producers interact with a routing gateway or smart SDK that maps logical topic names to physical target clusters, hiding physical cluster endpoints from application code.
- **Workload Tiering**: Allows tailoring cluster configurations (e.g., dedicated Tier-0 NVMe clusters for real-time payments vs. lower-cost, high-retention clusters for batch analytics and telemetry).
- **Independent Maintenance**: Enables rolling OS upgrades, Kafka version patching, and configuration changes cluster-by-cluster without risk to unaffected workloads.

### When to Use
- Large-scale enterprises where messaging throughput exceeds hundreds of thousands of events per second across dozens of independent engineering teams.
- Systems requiring strict physical isolation between high-SLA revenue-generating traffic and loss-tolerant asynchronous background telemetry.
- Multi-region or multi-cloud topologies where data must adhere to regional sovereign boundaries.

### When NOT to Use
- Small-to-medium systems where a single 3-to-5 node Kafka cluster comfortably handles all traffic with low operational overhead.
- Environments lacking automated cluster provisioning and cross-cluster replication tooling.

### Also see
- [Distributed Commit Log](#distributed-commit-log) · [Bulkhead](resilience.md#bulkhead) · [Blast Radius](resilience.md#blast-radius)

---


## uReplicator

An open-source distributed cross-cluster replication engine for Apache Kafka, originally created by Uber, that uses Apache Helix for dynamic partition management to eliminate the fleet-wide stop-the-world rebalance pauses endemic to standard MirrorMaker 1.0.

### Key Characteristics
- **Decoupled Coordination**: Separates partition assignment management (handled centrally by an Apache Helix controller) from data consumption and replication (executed by a fleet of worker nodes).
- **Non-Blocking Dynamic Rebalancing**: When topic partitions are added, removed, or workers fail, Helix reassigns only the impacted partitions directly to healthy workers without triggering full consumer group rebalance cycles across the entire fleet.
- **Dynamic Topic Discovery & Auto-Scaling**: Automatically detects newly created topics and scales replication capacity based on observed partition throughput and consumer lag.
- **High Throughput Across Regions**: Built specifically to sustain multi-datacenter active-active data synchronization at millions of messages per second.

### When to Use
- High-scale multi-cluster Kafka topologies where native MirrorMaker 1 consumer group rebalances cause severe latency spikes and cross-region replication lag.
- Complex replication topologies requiring dynamic partition redistribution and fine-grained workload placement across replication workers.

### When NOT to Use
- Modern Kafka deployments running Kafka 3.x+ where MirrorMaker 2 (KIP-382 built on Kafka Connect) natively provides cooperative rebalancing and dynamic topic replication without requiring an external Apache Helix cluster.
- Simple single-cluster deployments or cross-cluster links with low partition counts.

### Also see
- [Rebalance](#rebalance) · [Consumer Group](#consumer-group) · [Offset Alignment](#offset-alignment)

---


## Pipeline Audit Service (Chaperone Pattern)

An independent end-to-end accounting and auditing pattern for distributed event-driven architectures that collects aggregate message counts across pipeline checkpoints to detect and pinpoint message loss in real time.

### Key Characteristics
- **Tiered Checkpoint Counters**: Collects timestamp-windowed message counters at key infrastructural transitions: edge gateway ingress, regional broker arrival, cross-DC replication, and consumer database sinks.
- **Event-Time Window Bucketing**: Counts are aggregated into deterministic time buckets (e.g., 10-minute windows based on original message creation timestamps) regardless of network latency or arrival time.
- **Discrepancy Localization**: Continuously compares adjacent tier counts; any difference ($\text{Count}_{\text{Tier } N} \neq \text{Count}_{\text{Tier } N+1}$) triggers automated alerts pinpointing the exact network link, buffer, or proxy where loss occurred.
- **Passive Reliability Transformation**: Converts undetectable, silent transit data loss into observable, actionable engineering alerts.

### When to Use
- Enterprise-scale streaming pipelines where even 0.001% message loss represents thousands of dropped business events (e.g., driver location pings, financial ledger items, ride state changes).
- Multi-tier messaging pipelines comprising multiple brokers, proxies, replication bridges, and persistent sinks.

### When NOT to Use
- Small monolithic architectures where producers write directly to an ACID database.
- Low-volume systems where end-to-end distributed tracing (OpenTelemetry span tracking) already provides 100% trace coverage without aggregate statistical counters.

### Also see
- [At-Least-Once Semantics](#at-least-once-semantics) · [Observability](observability.md#observability) · [Event-Time](#event-time)

---


## Consumer Proxy Pattern

An architectural integration pattern where client applications consume messages from a message broker through an intermediate proxy service layer rather than directly embedding broker-specific client libraries.

### Key Characteristics
- **Protocol Encapsulation**: Hides complex broker mechanics—partition assignment, consumer group heartbeats, group rebalances, commit policies, and low-level thread loops—behind simple RPC protocols (e.g., gRPC push/pull or HTTP/2).
- **Simplified Application Contract**: Applications expose a basic processing interface: *receive message batch $\rightarrow$ execute business logic $\rightarrow$ return status code (ACK / NACK / RETRY)*.
- **Centralized Flow Control**: The proxy cluster centrally enforces backpressure, rate limiting, and failure buffering, shielding the broker from client-driven rebalance storms or connection floods.
- **Independent Fleet Evolution**: Broker endpoint migrations, security protocol upgrades (SASL/mTLS), and library updates occur in the proxy layer with zero changes to polyglot microservice codebases.

### When to Use
- Large engineering organizations with thousands of microservices across diverse programming languages (Java, Go, Python, Node.js) where maintaining bespoke Kafka consumer configurations is error-prone.
- Architectures deploying push-based compute layers (e.g., serverless functions, Kubernetes ingress) that cannot sustain persistent Kafka TCP connections and heartbeat loops.

### When NOT to Use
- Ultra-low latency trading or real-time gaming systems where the extra network hop (<2ms) and serialization step cannot be tolerated.
- Simple architectures with only a few microservices in a single language with established broker client libraries.

### Also see
- [Competing Consumers](#competing-consumers) · [Proxy Pattern](design-patterns.md#proxy-pattern) · [Consumer Group](#consumer-group)

---


## Kafka Tiered Storage

A storage architecture for Apache Kafka that decouples high-performance local disk storage from long-term historical retention by offloading sealed log segments to scalable, low-cost cloud object storage.

### Key Characteristics
- **Hot vs. Cold Separation**: Active, append-only log segments and recent reads remain on fast broker-local storage (NVMe/SSD, OS page cache). Sealed segments past a configurable local retention window are copied asynchronously to object storage (e.g., S3, Azure Blob Storage).
- **Transparent Consumer Fetching**: Brokers serve consumer fetch requests seamlessly regardless of whether the requested offset resides on local NVMe or remote object storage, requiring zero changes to consumer code.
- **Stateless Broker Scaling**: Because historical data lives in remote object storage, adding new brokers or rebalancing partitions requires copying only lightweight active segments, reducing rebalance durations from days to minutes.
- **Cost-Effective Infinite Retention**: Reduces storage costs by up to 80-90% compared to local enterprise SSD arrays, enabling Kafka to serve as an economical, permanent event source of truth for analytics and historical backfills.

### When to Use
- Event streams requiring long retention periods (weeks, months, or years) for historical reprocessing, model re-training, or compliance audits.
- Large Kafka clusters where broker disk capacity limits cluster sizing and causes days-long partition rebalance times.

### When NOT to Use
- Workloads with very short retention requirements (e.g., 2 to 4 hours) where all data naturally expires before offloading to object storage.
- On-premise bare-metal deployments without access to high-throughput object storage or S3-compatible endpoints.

### Also see
- [Distributed Commit Log](#distributed-commit-log) · [Log Segment](#log-segment) · [Replay (Kafka Reprocessing)](#replay-kafka-reprocessing)

---


## KRaft

Kafka Raft Metadata Mode (**KRaft**) is a built-in consensus protocol introduced in Apache Kafka 3.x that replaces the external dependency on Apache ZooKeeper for cluster metadata management. KRaft embeds a Raft-based quorum controller directly within the Kafka broker process.

### Key Characteristics
- **No ZooKeeper dependency**: Eliminates the requirement to operate, monitor, and tune a separate ZooKeeper ensemble alongside Kafka.
- **Embedded quorum controller**: A subset of brokers (`process.roles=controller`) forms a Raft quorum that elects a controller and replicates partition metadata via a dedicated internal topic (`__cluster_metadata`).
- **Faster controller failover**: Because metadata is replicated continuously via Raft, controller failover completes in seconds rather than the tens of seconds required under ZooKeeper-based Kafka.
- **Simpler operational topology**: One fewer distributed system to deploy, monitor, and upgrade.
- **GA since Kafka 3.3**: ZooKeeper mode is deprecated and removed in Kafka 4.0.

### When to Use
- All new Kafka deployments on Kafka 3.3 or later — KRaft is the recommended and eventually only mode.
- When simplifying infrastructure by eliminating the ZooKeeper operational burden.

### When NOT to Use
- Legacy Kafka versions below 3.3 that do not support KRaft mode (use ZooKeeper mode for those).
- Migrations in progress — plan a rolling migration from ZooKeeper to KRaft following the official migration tooling.

### Also see
- [Replication Factor](#replication-factor) · [ISR (In-Sync Replica)](#isr-in-sync-replica) · [Distributed Commit Log](#distributed-commit-log)

---


## Cooperative Sticky Assignor

A Kafka consumer group partition assignment strategy that performs **incremental, non-disruptive rebalances** by revoking only the specific partitions that need to move, rather than revoking all partitions from all consumers simultaneously.

### Key Characteristics
- **Incremental rebalance**: Only partitions that must be transferred to a newly joining or departing consumer are revoked. All other consumers continue processing uninterrupted during the rebalance.
- **Sticky**: Re-assigns previously held partitions back to the same consumer after rebalance whenever possible, maximizing local state re-use (critical for Kafka Streams stateful processors).
- **Two-phase protocol**: Requires 2–3 rebalance rounds to reach a stable assignment vs. 1 for the classic assignor, but this is negligible compared to a full stop-the-world pause.
- **Configured via**: `partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor`
- **Available since**: Kafka 2.4 (client) / Kafka 2.5 (broker-side support fully stable).

### When to Use
- All production consumer groups, especially those with stateful processing (Kafka Streams, Flink) where partition migration is expensive.
- Groups prone to Rebalance Storms due to slow startup times or heavy per-batch processing.

### When NOT to Use
- Consumer groups using older Kafka clients (pre-2.4) that do not support the cooperative protocol.
- Simple, stateless consumers where the classic `RangeAssignor` is sufficient and the operational team prefers simplicity.

### Also see
- [Rebalance](#rebalance) · [Consumer Group](#consumer-group) · [Kafka Streams](#kafka-streams)

---


## RecordAccumulator

An in-memory buffer within the Kafka **Producer client** that accumulates outgoing records into batches before transmitting them to the broker. It is the core mechanism behind Kafka's producer-side batching and throughput optimization.

### Key Characteristics
- **Per-partition queues**: The `RecordAccumulator` maintains a separate deque of `ProducerBatch` objects for each topic-partition. Records are appended to the current open batch for their target partition.
- **Batch triggers**: A batch is sent when either `batch.size` bytes are accumulated OR `linger.ms` milliseconds have elapsed since the first record was added — whichever comes first.
- **Compression scope**: Compression (`snappy`, `lz4`, `zstd`) is applied at the batch level inside the `RecordAccumulator`, improving compression ratios by operating on multiple related records together.
- **Backpressure**: If all partition queues are full (controlled by `buffer.memory`), the `send()` call blocks for up to `max.block.ms` before throwing a `TimeoutException`.

### When to Use
- Understanding and tuning Kafka producer throughput by adjusting `batch.size` and `linger.ms`.
- Diagnosing producer-side latency or memory pressure issues.

### When NOT to Use
- `RecordAccumulator` is an internal implementation detail — do not reference it in application business logic. Tune its behavior through the public producer configuration API instead.

### Also see
- [Message Batching](#message-batching) · [Producer Acknowledgement](#producer-acknowledgement) · [Idempotent Producer](#idempotent-producer)

---


## Avro

Apache Avro is a binary data serialization format defined by a JSON schema. In Kafka ecosystems, Avro is the dominant serialization format used alongside a **[Schema Registry](#schema-registry)** to enforce schema contracts between producers and consumers.

### Key Characteristics
- **Schema-embedded binary encoding**: Data is serialized as compact binary (not JSON text). The schema ID (not the full schema) is prepended to each message; the full schema is fetched from the Schema Registry on first use and cached.
- **Schema evolution**: Avro defines formal compatibility modes (BACKWARD, FORWARD, FULL) that allow schemas to evolve without breaking existing producers or consumers, subject to evolution rules (e.g., new fields must have defaults for BACKWARD compatibility).
- **Language neutrality**: Schemas are defined in JSON; code generators (`avro-tools`, `avro-maven-plugin`) produce language-specific classes for Java, Python, Go, etc.
- **Compact on wire**: Removes field names from the binary payload (unlike JSON), yielding 60–80% smaller messages at typical Kafka message sizes.

### When to Use
- Kafka pipelines where multiple teams share topics and schema governance is required to prevent breaking changes.
- High-throughput pipelines where JSON's verbosity is a bandwidth bottleneck.
- Multi-language environments where a language-neutral schema format is needed.

### When NOT to Use
- Simple pipelines with a single producer and consumer in the same codebase — plain JSON is simpler and easier to debug.
- Systems without an operational Schema Registry — Avro without a registry loses its primary governance benefit.
- Event payloads requiring human readability in transit (use JSON or Protobuf with human-readable options).

### Also see
- [Schema Registry](#schema-registry) · [Schema Contract (Event as Public API)](#schema-contract-event-as-public-api) · [Kafka Connect](#kafka-connect)

---


## SASL

**Simple Authentication and Security Layer** (SASL) is a framework that adds authentication support to network protocols without tying the protocol to a specific authentication mechanism. In Apache Kafka, SASL is the standard authentication layer used to verify client identity before allowing connection to a broker.

### Key Characteristics
- **Mechanism-agnostic**: Kafka supports multiple SASL mechanisms: `PLAIN` (username/password in cleartext — use only with TLS), `SCRAM-SHA-256`, `SCRAM-SHA-512` (salted challenge-response, no password on wire), `GSSAPI` (Kerberos), and `OAUTHBEARER` (token-based, for cloud IAM integration).
- **Three-layer Kafka security model**: SASL provides authentication (who are you?). SSL/TLS provides encryption (is traffic encrypted?). ACLs provide authorization (what are you allowed to do?).
- **SASL/SCRAM** is the most common production choice for non-Kerberos environments: it verifies a shared secret using a challenge-response without transmitting the password.
- **SASL/OAUTHBEARER** integrates with cloud identity providers (Azure AD, Okta, AWS IAM) for token-based, short-lived credential authentication.

### When to Use
- Any Kafka cluster that must restrict which clients can connect (i.e., all production clusters).
- `SASL/SCRAM` for on-premise or self-managed Kafka with username/password management.
- `SASL/OAUTHBEARER` for cloud-native Kafka (Confluent Cloud, MSK, Event Hubs) with short-lived token rotation.

### When NOT to Use
- Local development or internal-only test clusters where network-level isolation is sufficient.
- Do not use `SASL/PLAIN` without TLS — passwords are transmitted in cleartext.

### Also see
- [Kafka Connect](#kafka-connect) · [Consumer Group](#consumer-group) · [Security, Identity & Access Management](security-iam.md)

---


## Redpanda

Redpanda is a Kafka-API-compatible streaming platform written in C++ that replaces the Java Virtual Machine (JVM) with a user-space I/O architecture to eliminate Garbage Collection pauses and reduce operational overhead.

### Key Characteristics
- **100% Kafka API compatibility**: Existing Kafka producers, consumers, and admin clients connect to Redpanda without code changes. Kafka Connect, Kafka Streams, and Schema Registry clients are fully compatible.
- **No JVM / No GC**: Written in C++ using the Seastar framework with kernel-bypass I/O (io_uring on Linux). Eliminates JVM GC pauses, providing predictable sub-millisecond tail latencies.
- **No ZooKeeper, no KRaft controller separation**: Redpanda uses its own Raft implementation for all metadata and data replication, with no separate metadata quorum process.
- **Single binary**: The entire cluster (including the equivalent of Kafka's broker + KRaft controller) runs as a single process per node, simplifying deployment.
- **Built-in Schema Registry and REST Proxy**: These are included as first-class features without separate deployments.
- **Higher single-node throughput**: Benchmarks show 2–10× higher throughput per node compared to Apache Kafka at equivalent hardware, primarily due to eliminating GC overhead and using kernel-bypass I/O.

### When to Use
- Latency-sensitive streaming pipelines where JVM GC pauses (even with G1GC or ZGC) are unacceptable.
- Environments where operational simplicity (single binary, no ZooKeeper) is valued over ecosystem maturity.
- Drop-in replacement for Kafka where full API compatibility is required but lower resource cost is desired.

### When NOT to Use
- Organizations heavily invested in Confluent's proprietary ecosystem (ksqlDB, Confluent Control Center), which have no Redpanda equivalents.
- Workloads requiring mature Kafka Streams stateful processing — Redpanda does not implement Kafka Streams natively (use it with an external Flink or consumer-side state store instead).
- Teams who rely on Kafka's large, established community and extensive third-party tooling over Redpanda's growing but smaller ecosystem.

### Also see
- [Kafka vs RabbitMQ](#kafka-vs-rabbitmq) · [Distributed Commit Log](#distributed-commit-log) · [KRaft](#kraft)

---


## KStream

A **KStream** is the primary abstraction in Apache Kafka Streams representing an **unbounded, continuously flowing stream of events**, where each record represents a discrete fact that occurred at a point in time. Unlike a KTable (which represents the latest state per key), a KStream retains every event and never overwrites previous records.

### Key Characteristics
- **Append-only semantics**: Every new record is treated as an independent fact. Two records with the same key are two distinct events, not an update.
- **Stateless and stateful operations**: KStreams support map, filter, flatMap (stateless) as well as windowed aggregations and joins (stateful, backed by a RocksDB local state store).
- **Stream-Table Duality**: A KStream can be converted to a KTable (aggregating or compacting into current state), and a KTable can be converted back into a changelog KStream.
- **Inter-KStream Joins**: Two KStreams can be joined within a time window to correlate related events (e.g., join `orders` and `payments` streams that arrive within 30 seconds of each other).
- **Source and sink**: A KStream reads from one or more Kafka topics (source) and can write results to another Kafka topic (sink) via `.to()` or branch to multiple topics.

### When to Use
- Real-time per-event transformations, enrichment, or routing (e.g., filter fraudulent transactions, enrich orders with user data).
- Windowed aggregations where the history of events within a time window matters (e.g., count orders per product per minute).
- Joining two event streams to detect correlated facts within a time window.

### When NOT to Use
- When you need the current state per key (latest value), not the full event history — use a [KTable](#ktable) instead.
- When your processing logic requires a SQL-like interface — consider ksqlDB on top of Kafka Streams.
- For batch processing of bounded datasets — use Apache Flink or Spark instead of Kafka Streams.

### Also see
- [KTable](#ktable) · [Stream-Table Duality](#stream-table-duality) · [Kafka Streams](#kafka-streams) · [Apache Flink](#apache-flink)

---


## Sticky Partitioner

The **Sticky Partitioner** is Apache Kafka's default producer-side partitioning strategy (since Kafka 2.4) for messages sent **without a Message Key**. Instead of distributing keyless messages one-by-one in round-robin fashion across all partitions, it accumulates messages into a single partition's batch until the batch is full or `linger.ms` expires, then "sticks" to that partition for the next batch — and so on, rotating lazily.

### Key Characteristics
- **Batch-coherent**: All messages accumulated during a single batch window go to the same partition, maximising `batch.size` fill rate and compression effectiveness before rotating.
- **Rotation trigger**: The assignor rotates to the next partition only when the current batch is sent (i.e., when `batch.size` is reached or `linger.ms` elapses), not per-message.
- **Even distribution over time**: Because batches rotate in sequence, partitions receive roughly equal message counts over time — without the per-message overhead of pure round-robin.
- **No ordering guarantee**: As with all keyless partitioning, there is no per-entity ordering guarantee across partitions. Use a Message Key when ordering matters.
- **Replaces legacy Round-Robin Partitioner**: The older `RoundRobinPartitioner` distributed messages one at a time, producing tiny under-filled batches. The Sticky Partitioner eliminates this inefficiency.

### When to Use
- Producing keyless messages where ordering is not required and throughput is the priority (e.g., metrics, click-events, log lines).
- Replacing a low-cardinality Message Key that causes hot partitions — drop the key entirely and let the Sticky Partitioner distribute load evenly.
- Any high-volume pipeline where maximising batch fill rate is more important than per-message partition control.

### When NOT to Use
- When per-entity ordering is required — use a high-cardinality Message Key instead.
- When an external system requires deterministic partition assignment (e.g., a partition-aware consumer that routes to different downstream sinks based on partition number).

### Also see
- [Hot Partition](#hot-partition) · [Message Batching](#message-batching) · [RecordAccumulator](#recordaccumulator) · [Cooperative Sticky Assignor](#cooperative-sticky-assignor)

