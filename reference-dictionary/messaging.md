# Message Brokers & Asynchronous Messaging

> **Domain**: Message brokers, event streaming, queues, and asynchronous communication patterns.
> **Parent**: [Reference Dictionary](README.md)

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

A queue for messages that **cannot be processed** after all retry attempts are exhausted. DLQs prevent poison messages from blocking the entire queue. DLQ messages must be **alerted on** and investigated.

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
