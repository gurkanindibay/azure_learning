---
type: System Design
title: "Message Brokers & Async — Key Takeaways"
description: "The 5 Kafka Consumer Mistakes That Quietly Destroy Production Systems"
timestamp: 2026-06-15T00:00:00Z
---

# 30. Message Brokers & Async — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [The 5 Kafka Consumer Mistakes That Quietly Destroy Production Systems](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md)
> **Purpose**: Kafka consumer reliability patterns for production messaging pipelines.

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md)
> **Dictionary**: [Consumer Lag](../../reference-dictionary/messaging.md#consumer-lag), [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq), [Kafka Connect](../../reference-dictionary/messaging.md#kafka-connect), [Offset Commit](../../reference-dictionary/messaging.md#offset-commit)
> **Taxonomy Reference**: §3.2 Messaging Patterns, §7.1 Reliability Architecture

---

## Contents

- [broker-01: Committing Offsets Before Processing](#broker-01) — At-least-once delivery is lost when offsets are committed early.
- [broker-02: Not Monitoring Consumer Lag](#broker-02) — Lag is the earliest signal of a stalled consumer.
- [broker-03: Sharing Consumer Groups Across Regions](#broker-03) — Same group ID across regions couples regional failures.
- [broker-04: Short Kafka Retention](#broker-04) — Retention shorter than detection time prevents replay of lost events.
- [broker-05: Missing Dead Letter Topics](#broker-05) — One poison message can starve the whole consumer.

---

## broker-01: Committing Offsets Before Processing

> **Source**: [§"Mistake #1 — Committing Offsets Before Processing"](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md#mistake-1--committing-offsets-before-processing)

| | |
|:---|:---|
| **Problem** | A consumer commits its offset before the business logic finishes. If processing then fails, Kafka treats the message as already consumed and will not redeliver it. |
| **Key Concept** | Offset commit marks the consumer's position in the log, not the success of the side effects produced from the message. |

> **Strategy**: Commit offsets **after** successful processing (manual commit or at-least-once with idempotent handlers). Pair commit with idempotent downstream writes so duplicate redelivery is safe.
>
> **Tradeoff**: Committing after processing improves correctness but can cause reprocessing after a crash if the commit fails. Idempotent handlers are required for true at-least-once semantics.
>
> **Cross-reference**: [Offset Commit](../../reference-dictionary/messaging.md#offset-commit) · [At-Least-Once Semantics](../../reference-dictionary/messaging.md#at-least-once-semantics)

---

## broker-02: Not Monitoring Consumer Lag

> **Source**: [§"Mistake #2 — Not Monitoring Consumer Lag"](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md#mistake-2--not-monitoring-consumer-lag)

| | |
|:---|:---|
| **Problem** | A consumer stalls silently while Kafka keeps accepting events. Without lag alerts, the outage is only discovered when downstream systems or customers report missing data. |
| **Key Concept** | **Consumer lag** = last produced offset − last consumed offset. Sustained growth means the consumer cannot keep up. |

> **Strategy**: Alert on `consumer_group_lag`, `consumer_poll_interval`, and `consumer_heartbeat`. Set thresholds based on business SLA (e.g., max acceptable lag before orders are considered stale).
>
> **Tradeoff**: Fine-grained lag alerts can be noisy during traffic spikes; pair with trend-based alerts and consumer autoscaling where possible.
>
> **Cross-reference**: [Consumer Lag](../../reference-dictionary/messaging.md#consumer-lag) · [Consumer Group](../../reference-dictionary/messaging.md#consumer-group)

---

## broker-03: Sharing Consumer Groups Across Regions

> **Source**: [§"Mistake #3 — Using the Same Consumer Group Across Regions"](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md#mistake-3--using-the-same-consumer-group-across-regions)

| | |
|:---|:---|
| **Problem** | A single `group.id` is reused in multiple regions. Kafka rebalances partitions across all consumers globally, so a regional outage can leave partitions assigned to failed consumers and stop processing in healthy regions. |
| **Key Concept** | Consumer groups are a Kafka scaling/assignment boundary. Regions that need autonomy must have independent groups. |

> **Strategy**: Use region-scoped group IDs (`order-processing-us`, `order-processing-eu`) so each region consumes all partitions independently and regional failures stay isolated.
>
> **Tradeoff**: Independent regional groups process every message in every region, increasing total consumption cost and requiring downstream systems to handle regional duplicates if the topic is not region-partitioned.
>
> **Cross-reference**: [Consumer Group](../../reference-dictionary/messaging.md#consumer-group) · [Partition](../../reference-dictionary/messaging.md#partition)

---

## broker-04: Short Kafka Retention

> **Source**: [§"Mistake #4 — Short Kafka Retention"](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md#mistake-4--short-kafka-retention)

| | |
|:---|:---|
| **Problem** | Retention is set too low (e.g., 7 days). By the time a silent consumer bug is discovered, the missed events have already been deleted and cannot be replayed. |
| **Key Concept** | Kafka retains messages based on `log.retention.hours` / bytes; once deleted, events are gone unless archived elsewhere. |

> **Strategy**: Set retention long enough to exceed mean time to detect consumer failures (commonly 30–90 days in production). Complement Kafka with durable archival such as Kafka Connect → S3 → data lake for replay and audit.
>
> **Tradeoff**: Longer retention increases storage cost and replay time. Archiving to object storage trades immediate random access for much lower cost and indefinite retention.
>
> **Cross-reference**: [Kafka Connect](../../reference-dictionary/messaging.md#kafka-connect) · [Partition](../../reference-dictionary/messaging.md#partition)

---

## broker-05: Missing Dead Letter Topics

> **Source**: [§"Mistake #5 — No Dead Letter Topics"](../../articles/messaging/the-5-kafka-consumer-mistakes-that-quietly-destroy-production-systems-1.md#mistake-5--no-dead-letter-topics)

| | |
|:---|:---|
| **Problem** | A malformed or unprocessable message causes the consumer to retry forever, blocking all subsequent messages in the same partition. |
| **Key Concept** | A **Dead Letter Topic (DLT)** receives messages that fail after a bounded number of retries, preventing consumer starvation. |

> **Strategy**: Configure retry policies and a DLT (e.g., Spring Kafka `@RetryableTopic` or manual try/catch + producer to `-dlt`). Alert on DLT depth and inspect failed messages offline.
>
> **Tradeoff**: DLTs add operational complexity (retry semantics, ordering changes, DLT reprocessing). Retries can also delay processing and violate ordering guarantees within a partition.
>
> **Cross-reference**: [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq) · [Poison Message](../../reference-dictionary/messaging.md#poison-message)
