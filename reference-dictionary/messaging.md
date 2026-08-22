---
type: Reference
title: "Message Brokers & Asynchronous Messaging"
description: "The unit of **parallelism and ordering** in Kafka. Messages within a partition are strictly ordered. Partitions enable horizontal scaling — each partition can be consumed by only one consumer in a ..."
timestamp: 2026-06-14T00:00:00Z
---

# Message Brokers & Asynchronous Messaging

> **Domain**: Message brokers, event streaming, queues, and asynchronous communication patterns.
> **Parent**: [Reference Dictionary](index.md)

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
| Redis Streams | [`#redis-streams`](#redis-streams) |
| Per-Device Inbox | [`#per-device-inbox`](#per-device-inbox) |
| Compacted Topic | [`#compacted-topic`](#compacted-topic) |
| Stream-Table Duality | [`#stream-table-duality`](#stream-table-duality) |
| Hot Partition | [`#hot-partition`](#hot-partition) |
| Retry Topic | [`#retry-topic`](#retry-topic) |
| KTable | [`#ktable`](#ktable) |
| Competing Consumers | [`#competing-consumers`](#competing-consumers) |
| Claim Check | [`#claim-check`](#claim-check) |
| Atomic Deduplication | [`#atomic-deduplication`](#atomic-deduplication) |
| Deduplication Store | [`#deduplication-store`](#deduplication-store) |
| Deduplication Window | [`#deduplication-window`](#deduplication-window) |
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
| Fanout on Write | [`#fanout-on-write`](#fanout-on-write) |
| Fanout on Read | [`#fanout-on-read`](#fanout-on-read) |
| Hybrid Fanout | [`#hybrid-fanout`](#hybrid-fanout) |
| Apache Flink | [`#apache-flink`](#apache-flink) |
| Write-Ahead Buffer | [`#write-ahead-buffer`](#write-ahead-buffer) |
| Log Segment | [`#log-segment`](#log-segment) |
| ISR (In-Sync Replica) | [`#isr-in-sync-replica`](#isr-in-sync-replica) |
| Replication Factor | [`#replication-factor`](#replication-factor) |
| Communication Pattern | [`#communication-pattern`](#communication-pattern) |
| Choreography | [`#choreography`](#choreography) |
| Orchestration | [`#orchestration`](#orchestration) |
| Client-Side Deduplication | [`#client-side-deduplication`](#client-side-deduplication) |
| Delivery Cursor | [`#delivery-cursor`](#delivery-cursor) |
| Configuration Server | [`#configuration-server`](#configuration-server) |
| Config Server | [`#config-server`](#config-server) |
| Dual-Write Migration | [`#dual-write-migration`](#dual-write-migration) |
| Global Secondary Index | [`#global-secondary-index`](#global-secondary-index) |
| Kafka Streams | [`#kafka-streams`](#kafka-streams) |
| Three-Layer Deduplication | [`#three-layer-deduplication`](#three-layer-deduplication) |
| Worker Self-Throttling | [`#worker-self-throttling`](#worker-self-throttling) |
| Progressive Enqueuing | [`#progressive-enqueuing`](#progressive-enqueuing) |

## Client-Side Deduplication

A technique where the **message sender generates a unique message ID** and uses it as an idempotency key. If the send operation times out, the client retries with the **same ID** — enabling the server and receiver to recognize and discard duplicates.

### Key Characteristics
- **Unique ID per message**: Generated client-side (UUID, content hash, or sequence number) before the first send attempt
- **Same ID on retry**: The critical invariant — retries must reuse the original ID, not generate a new one
- **First layer of defense**: Prevents re-insertion at the server and re-display at the receiver

### When to Use
- Any messaging or API system where network timeouts can cause senders to retry
- Multi-device messaging platforms (WhatsApp, Telegram, Signal)
- Payment APIs and financial transactions where duplicate submission must be prevented

### When NOT to Use
- Fire-and-forget telemetry where duplicates are harmless
- Systems where the server assigns message IDs and clients never retry

### Also see
- [Idempotent Consumer](#idempotent-consumer) · [At-Least-Once Semantics](#at-least-once-semantics) · [Producer Acknowledgement](#producer-acknowledgement) · [Idempotency](cqrs-event-driven.md#idempotency)

---

## Delivery Cursor

A **server-side pointer** that tracks the last message successfully delivered to a specific client, enabling the client to catch up after reconnection without re-receiving already-processed messages. The server advances the cursor only after confirming delivery or receiving an ACK from the client.

### Key Characteristics
- **Per-client, per-conversation**: Each recipient has independent cursors for each conversation or channel
- **Monotonic**: Cursors only move forward; a message with ID ≤ cursor value is already delivered
- **Foundation for offline catch-up**: Clients request messages since their last cursor position after reconnecting

### When to Use
- Real-time messaging with multi-device support and offline catch-up
- Any at-least-once delivery system where the server must track per-client progress
- Replacement for per-message ACKs when batch acknowledgment is preferred

### When NOT to Use
- Pub/sub systems where subscribers are ephemeral and don't need catch-up (e.g., live sensor data)
- Systems where the client can independently track and request missing ranges (Kafka consumer with offset management)

### Also see
- [At-Least-Once Semantics](#at-least-once-semantics) · [Per-Device Inbox](#per-device-inbox) · [Offset Commit](#offset-commit) · [Client-Side Deduplication](#client-side-deduplication)

---

## Communication Pattern

A deliberate choice of how components exchange requests or events, including synchronous request-response and asynchronous message-based communication. The choice should follow response-time, coupling, consistency, and throughput requirements.

### Key Characteristics
- Synchronous calls provide an immediate result but couple latency and availability
- Asynchronous messages decouple producers and consumers but require eventual-consistency handling
- The contract includes delivery, ordering, retry, timeout, and failure semantics

### When to Use
- To make communication trade-offs explicit at service boundaries
- When deciding between REST/gRPC and events or queues for a workflow step

### When NOT to Use
- As a technology-first label without identifying the caller's response and consistency needs

### Also see
- [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture) · [Message Ordering](#message-ordering) · [Saga](data-concurrency.md#saga-pattern)

---

## Choreography

A distributed workflow style in which services react to domain events and publish subsequent events without a central coordinator directing every step.

### Key Characteristics
- Each participant owns its local reaction and completion event
- Coupling is expressed through event contracts rather than direct calls
- Failure handling and workflow visibility must be designed explicitly

### When to Use
- Simple, stable workflows where participants can react independently
- Event-driven integrations that benefit from loose temporal coupling

### When NOT to Use
- Long, branching workflows where global progress and compensation are difficult to observe
- When no team can own event contracts and operational tracing

### Also see
- [Orchestration](#orchestration) · [Saga](data-concurrency.md#saga-pattern) · [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture)

---

## Orchestration

A distributed workflow style in which a coordinator directs service actions, tracks progress, and decides how failures are compensated.

### Key Characteristics
- Centralizes workflow state and sequencing
- Makes retries, timeouts, and compensation visible in one place
- The coordinator can become a coupling or availability boundary

### When to Use
- Long-running, branching, or compensation-heavy workflows
- Processes that need explicit progress, auditability, or operator control

### When NOT to Use
- Simple independent reactions where a coordinator adds more coupling than clarity
- Without durable coordinator state and idempotent command handling

### Also see
- [Choreography](#choreography) · [Saga](data-concurrency.md#saga-pattern) · [Idempotency](cqrs-event-driven.md#idempotency)

---

## Configuration Server

A centralized service or managed system that stores, versions, and distributes runtime configuration to multiple application services.

### Key Characteristics
- Separates configuration from application binaries
- Supports versioning, environment-specific values, and controlled refresh
- Requires access control, validation, secret handling, and rollback safeguards

### When to Use
- Many services share environment-specific settings or need coordinated configuration changes
- Configuration must be audited and updated without rebuilding every service

### When NOT to Use
- Small applications where local, version-controlled configuration is simpler and sufficient
- Without a plan for startup failure, stale values, or a bad configuration's blast radius

### Also see
- [Configuration Propagation](observability.md#configuration-propagation) · [Service Discovery](architecture-patterns.md#service-discovery)

**Also known as**: Config Server.

---

## Config Server

An alternate name for [Configuration Server](#configuration-server), the centralized store and distribution mechanism for runtime configuration.

**Also see**: [Configuration Server](#configuration-server)

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

## Redis Streams

A Redis data type that models an append-only log with consumer-group semantics, allowing durable, ordered, fault-tolerant message processing inside Redis.

### Key Characteristics
- Entries are ordered and identified by time-based IDs
- Consumer groups track pending entries and support explicit ACKs
- Memory is bounded via trimming / `MAXLEN`

### When to Use
- Per-device inboxes and lightweight message queues
- Ordered event streams that fit in memory
- Scenarios where a full Kafka cluster is too heavy

### When NOT to Use
- Long-term event storage (prefer Kafka or an event store)
- Very large payloads (use the claim-check pattern)

### Also see
- [Per-Device Inbox](#per-device-inbox) · [Kafka vs RabbitMQ](#kafka-vs-rabbitmq) · [At-Least-Once Semantics](#at-least-once-semantics)

---

## Per-Device Inbox

A messaging pattern that gives each recipient device its own durable queue so delivery and read progress can be tracked independently per device.

### Key Characteristics
- One queue or stream per user-device pair
- Enables offline catch-up and multi-device synchronization
- Usually paired with at-least-once delivery and client-side deduplication

### When to Use
- Real-time messaging with multi-device support
- Push-notification buffering for offline clients

### When NOT to Use
- Simple broadcast use cases where all consumers share one stream
- Systems that can tolerate lossy fan-out

### Also see
- [Redis Streams](#redis-streams) · [At-Least-Once Semantics](#at-least-once-semantics) · [Message Ordering](#message-ordering)

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

## Competing Consumers

Multiple consumers **pull from a single queue** for load-balanced processing. If one consumer is slow, others pick up the slack. Core pattern for scaling message processing horizontally.

**Also see**: [Messaging](messaging.md)

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
- [Messaging](messaging.md) · [Event Carried State Transfer](cqrs-event-driven.md#event-carried-state-transfer) · [Messaging: Compacted Topic](messaging.md#compacted-topic)

---

## Atomic Deduplication

A pattern that prevents race conditions in idempotent message processing by using a database `INSERT` with a `UNIQUE` constraint as the deduplication check, rather than a non-atomic check-then-act sequence.

```sql
-- Atomic: only one consumer succeeds
INSERT INTO processed_events (event_id) VALUES ('EVT-8A72F1');
-- UNIQUE(event_id) constraint ensures atomicity
```

### Key Characteristics
- **Database-enforced atomicity**: The database itself (not application logic) guarantees that only one INSERT for a given Event ID succeeds
- **Eliminates check-then-act races**: No gap between "check if processed" and "mark as processed" — they are the same operation
- **Constraint violation = already processed**: Consumers treat the UNIQUE constraint error as a signal to skip processing
- **Portable across stores**: Works with any store that supports atomic conditional inserts (SQL UNIQUE, Redis `SETNX`, DynamoDB conditional put)

### When to Use
- At-least-once consumers where concurrent instances may process the same event
- High-throughput systems where lock-based deduplication would create contention
- Any consumer that must be horizontally scalable while maintaining idempotency

### When NOT to Use
- When the deduplication store does not support unique constraints or conditional writes
- When the business update and dedup record are in different transactional scopes (use Outbox Pattern instead)
- Single-instance consumers where a simple in-memory set suffices

### Also see
- [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---

## Deduplication Store

A **shared, external data store** used by idempotent consumers to track which events have already been processed. It serves as the single source of truth across all consumer instances so that duplicate deliveries are recognized and skipped regardless of which instance receives the redelivery.

### Key Characteristics
- **Shared across instances**: All consumers in a group read and write to the same store — a local in-memory cache is insufficient at scale
- **Atomic conditional inserts**: Typically backed by a database with UNIQUE constraints (relational DB, Redis `SETNX`, DynamoDB conditional put)
- **Retention-bounded**: Entries are purged after a configurable window that exceeds Kafka's maximum redelivery window
- **Per-event granularity**: Keyed by Event ID, not by message offset or partition

### When to Use
- Horizontally scaled consumer groups where duplicate events may land on any instance after a rebalance
- At-least-once messaging systems (Kafka, Event Hubs, Service Bus) where redelivery is a normal occurrence
- Payment, inventory, or order workflows where double-processing is unacceptable

### When NOT to Use
- Single-instance consumers where an in-memory `HashSet<EventId>` suffices
- Systems with true exactly-once delivery guarantees (rare in practice)
- When the deduplication store itself becomes a bottleneck (consider partitioning by Event ID)

### Also see
- [Atomic Deduplication](#atomic-deduplication) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---

## Deduplication Window

The **time period during which a messaging system retains deduplication state** to detect and discard duplicate messages. Infrastructure-level deduplication (Kafka idempotent producer, SQS FIFO) only works within this bounded window — once it expires, duplicates can pass through undetected.

### Key Characteristics
- **Bounded by retention**: The deduplication window should match or exceed the message retention period (e.g., Kafka retains 7 days → dedup keys kept for 7 days)
- **System-specific**: SQS FIFO has a fixed 5-minute window; Kafka's window is configurable via `max.in.flight.requests` and producer session lifetime
- **Cleanup required**: Stale deduplication records must be purged via scheduled jobs — unbounded growth degrades broker performance
- **Not a substitute for application idempotency**: The window can expire; application-layer idempotency with durable storage is the only permanent guarantee

### When to Use
- Understanding the limits of broker-level deduplication guarantees
- Sizing TTLs for Redis-based dedup stores at the application layer
- Designing cleanup policies for deduplication state in long-running systems

### When NOT to Use
- As the sole deduplication mechanism — always pair with application-layer idempotency
- When messages may be legitimately replayed beyond the window (event sourcing, audit replays)

### Also see
- [Deduplication Store](#deduplication-store) · [Idempotent Producer](#idempotent-producer) · [At-Least-Once Semantics](#at-least-once-semantics)

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

### When to Use
- Windowed aggregations where completeness matters (hourly/daily rollups, billing)
- IoT pipelines where device data can be delayed by hours due to connectivity gaps
- Any streaming use case with a defined SLA for result freshness vs completeness

### When NOT to Use
- Per-event processing with no windowing (each event is processed independently)
- When all producers have guaranteed low-latency delivery (processing-time windows suffice)
- When incomplete windows are acceptable and freshness is the priority

### Also see
- [Event-Time](#event-time) · [Processing-Time](#processing-time) · [Consumer Lag](#consumer-lag)

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

## Fanout on Write

A distribution model where a new event is propagated to all consumers at write time. In social media, posting a message writes the post ID into every follower's timeline cache immediately. Reads are fast because results are pre-computed.

### Key Characteristics
- **Read-optimized**: Feed loads are O(1)
- **Write amplification**: Each post generates N writes for N followers
- **Latency to readers**: Near zero (data is already present)

### When to Use
- Small-to-medium follower counts
- Read latency is the dominant SLO

### When NOT to Use
- Celebrity accounts with millions of followers (write amplification explodes)
- Systems where producers significantly outnumber consumers

**Also see**: [Fanout on Read](#fanout-on-read) · [Hybrid Fanout](#hybrid-fanout) · [Timeline Cache](../reference-dictionary/caching.md#timeline-cache)

---

## Fanout on Read

A distribution model where events are stored centrally and consumers collect relevant items at read time. In social media, a follower loads their feed by fetching recent posts from each account they follow. Writes are cheap; reads are more expensive.

### Key Characteristics
- **Write-optimized**: Each post generates O(1) writes
- **Read cost grows with followees**: Feed load is O(followees)
- **No write amplification**: Ideal for celebrity producers

### When to Use
- Highly skewed graphs where a few producers have massive audiences
- Systems where reads are infrequent relative to writes

### When NOT to Use
- Feeds with strict latency SLOs and many followees
- Uniform graphs where push would be simpler and faster

**Also see**: [Fanout on Write](#fanout-on-write) · [Hybrid Fanout](#hybrid-fanout)

---

## Hybrid Fanout

A distribution model that combines fanout-on-write for normal users and fanout-on-read for high-follower celebrities. Balances read latency against write amplification by choosing the fanout strategy per producer based on follower count.

### Key Characteristics
- **Threshold-based**: Users below a follower count are pushed; celebrities are pulled
- **Best of both worlds**: Fast reads for most users, bounded write amplification
- **Operational complexity**: Requires separate code paths and caches

### When to Use
- Social networks with highly skewed follower distributions
- Any fanout problem where neither pure push nor pure pull is affordable

### When NOT to Use
- Simple graphs where one strategy clearly dominates
- When operational complexity outweighs the fanout savings

**Also see**: [Fanout on Write](#fanout-on-write) · [Fanout on Read](#fanout-on-read) · [Celebrity Cache](../reference-dictionary/caching.md#celebrity-cache)

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

## Dual-Write Migration

A database migration strategy where the application writes to both the old (monolith) and new (sharded) systems simultaneously during a transition period. Dual-write enables zero-downtime migration with instant rollback capability — if the new system misbehaves, traffic is routed back to the old system without data loss.

### Key Characteristics
- **Concurrent writes**: Every write operation targets both old and new systems in the same request path
- **Failure handling**: If the new-system write fails, the old-system write is rolled back or the request is rejected — data consistency across systems is preserved
- **Four-phase process**: Dual-write → batch backfill of historical data → real-time reconciliation → controlled traffic rollout (1% → 10% → 50% → 100%)
- **Rollback safety**: As long as dual-write is active, reverting is a config change, not a data migration

### When to Use
- Migrating a live, high-traffic database table to a sharded architecture without downtime
- Any migration where a big-bang cutover is unacceptable due to 24/7 availability requirements

### When NOT to Use
- When the old and new systems have incompatible data models that cannot be reconciled in real time
- Low-traffic systems where a brief maintenance window is acceptable and simpler
- When write latency doubling (both systems must be written) exceeds the application's latency budget

### Also see
- [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern) · [Dual-Write Problem](../reference-dictionary/cqrs-event-driven.md#dual-write-problem) · [Strangler Fig](../reference-dictionary/architecture-patterns.md#strangler-fig) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)

---

## Global Secondary Index

An index in a distributed database that spans all shards and enables efficient queries on non-shard-key columns without broadcasting to every shard. Unlike a local secondary index (which exists within a single shard), a global secondary index maintains its own sharded storage, mapping the indexed column values to the primary keys and shard locations.

### Key Characteristics
- **Cross-shard coverage**: Index entries are distributed across all shards independently of the base table's sharding scheme
- **Asynchronous maintenance**: Index updates may lag behind base-table writes, introducing eventual consistency
- **Middleware or database-native**: Implemented by ShardingSphere, Spanner, DynamoDB GSIs, or Cosmos DB composite indexes
- **Storage overhead**: The index consumes additional disk and memory proportional to indexed column cardinality

### When to Use
- Query patterns that frequently filter by a non-shard-key column (e.g., `merchant_id` in a `user_id`-sharded orders table)
- When the alternative — broadcasting queries to all shards and merging results — exceeds latency or resource budgets

### When NOT to Use
- When the indexed column has very low cardinality (e.g., `status`) — the index provides little filtering benefit
- When write throughput is the bottleneck and the index update overhead is unacceptable
- When cross-shard queries are rare and scatter-gather is acceptable

### Also see
- [Sharding](data-architecture.md#sharding) · [Shard Key](data-concurrency.md#shard-key) · [Cross-Shard Query](cqrs-event-driven.md#cross-shard-query)

---


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

## Three-Layer Deduplication

A defense-in-depth pattern for distributed messaging systems that applies deduplication at three independent layers: **client-side** (idempotency key on send), **server-side** (unique constraint on message ID), and **receiver-side** (seen-ID cache). Each layer protects against a different failure mode — no single layer can catch all duplicates.

### Key Characteristics
- **Client layer**: Generates a unique message ID and reuses it on retry. Prevents the sender from creating duplicate payloads during timeout-based retries.
- **Server layer**: Uses the message ID as a primary key or unique index. Duplicate INSERT attempts fail deterministically at the database level.
- **Receiver layer**: Maintains a short-lived LRU cache (with TTL) of recently processed message IDs. Discards incoming messages whose ID is already present.
- **Defense in depth**: If layer 1 misses (e.g., client crash and reinstall), layer 2 catches it. If layer 2 misses (e.g., server replication lag), layer 3 catches it.

### When to Use
- Real-time messaging platforms with at-least-once delivery guarantees (WhatsApp, Telegram, Signal)
- Payment processing and financial systems where duplicate transactions are unacceptable
- Any system where network retries can produce semantically identical requests that must not be processed twice

### When NOT to Use
- Append-only telemetry or logging where occasional duplicates are harmless
- Systems with strict low-latency requirements where the storage/check overhead of all three layers is prohibitive — use two layers instead
- Stateless request-response APIs where idempotency keys alone at the server layer suffice

### Also see
- [Client-Side Deduplication](#client-side-deduplication) · [Delivery Cursor](#delivery-cursor) · [Atomic Deduplication](#atomic-deduplication) · [Deduplication Store](#deduplication-store) · [Idempotent Consumer](#idempotent-consumer) · [Idempotency](cqrs-event-driven.md#idempotency)

---

## Worker Self-Throttling

A client-side rate-limiting and traffic-shaping pattern where asynchronous consumer workers actively pace their outbound execution rates to remain strictly within downstream provider limits (such as third-party push notification, SMS, or payment gateways), rather than consuming from the queue at maximum compute speed.

### Key Characteristics
- **Client-side rate limiting**: Workers embed token bucket or leaky bucket limiters to throttle outbound HTTP/RPC dispatch.
- **Queue as healthy buffer**: A growing queue depth is treated as safe, expected backpressure rather than a trigger to blindly spin up more compute.
- **Provider account protection**: Prevents HTTP 429 (Too Many Requests), connection bans, or gateway account suspensions caused by over-aggressive concurrent egress.

### When to Use
- Asynchronous worker fleets making outbound calls to rate-limited third-party APIs (APNs, FCM, Twilio, SendGrid).
- High-fanout background workloads where upstream queue volume exceeds downstream recipient acceptance limits.

### When NOT to Use
- Internal services that support elastic autoscaling and explicit HTTP backpressure headers.
- Workloads where the bottleneck is internal compute rather than external egress quotas.

### Also see
- [Backpressure](resilience.md#backpressure) · [Message Batching](#message-batching) · [Dead Letter Queue (DLQ)](#dead-letter-queue-dlq) · [Rate Limiting](api-design.md#rate-limiting)

---

## Progressive Enqueuing

An architectural pattern for massive fanout or batch operations (e.g. 100M+ user campaigns) where individual jobs are not materialized and dumped into the message queue all at once; instead, the workload is stored as a high-level definition and a background generator service progressively materializes and enqueues small batches over time.

### Key Characteristics
- **Campaign definition decoupling**: The trigger persists metadata and segmentation queries rather than hundreds of millions of individual task records.
- **Smoothed broker ingestion**: Prevents extreme spikes in message broker disk utilization, partition queue memory, and replication overhead.
- **Steady-state processing**: Converts an unmanageable instant burst into a continuous, controllable flow of work.

### When to Use
- Mega-scale push notification campaigns, marketing email blasts, or batch statement generation targeting tens to hundreds of millions of users.
- Large-scale media transcoding or bulk ETL migrations where upfront job creation would overwhelm message brokers.

### When NOT to Use
- Real-time emergency broadcast systems where every recipient must be targeted simultaneously with minimum latency.
- Small-to-medium fanout operations (<1M items) where standard queue durability and partitioning handle the burst without issue.

### Also see
- [Message Batching](#message-batching) · [Partition](#partition) · [Consumer Lag](#consumer-lag) · [Backpressure](resilience.md#backpressure)


