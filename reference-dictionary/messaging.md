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
| Redis Streams | [`#redis-streams`](#redis-streams) |
| Dead Letter Queue (DLQ) | [`#dead-letter-queue-dlq`](#dead-letter-queue-dlq) |
| Per-Device Inbox | [`#per-device-inbox`](#per-device-inbox) |
| Poison Message | [`#poison-message`](#poison-message) |
| Message Ordering | [`#message-ordering`](#message-ordering) |
| At-Least-Once Semantics | [`#at-least-once-semantics`](#at-least-once-semantics) |
| Exactly-Once Semantics | [`#exactly-once-semantics`](#exactly-once-semantics) |
| Kafka Transactions | [`#kafka-transactions`](#kafka-transactions) |
| Rebalance | [`#rebalance`](#rebalance) |
| Consumer Lag | [`#consumer-lag`](#consumer-lag) |
| Kafka Connect | [`#kafka-connect`](#kafka-connect) |
| Idempotent Consumer | [`#idempotent-consumer`](#idempotent-consumer) |
| Auto Commit | [`#auto-commit`](#auto-commit) |

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

