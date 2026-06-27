---
type: System Design
title: "Kafka Reliability & Ordering — Production Deep-Dive Key Takeaways"
description: "Production-depth insights from the Kafka reliability and ordering patterns series: dual-write failure modes, outbox publisher options (Debezium vs polling), DynamoDB conditional writes for idempotency, hot-partition mitigation, partition sizing, DLQ with persistent retry tracking, and retry topics with exponential backoff and jitter."
timestamp: 2026-06-26T00:00:00Z
---

# 54. Kafka Reliability & Ordering — Production Deep-Dive Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md)
> **Part 1 Overview**: [Kafka Design Patterns Overview — broker-24 to broker-34](messaging/kafka-design-patterns.md)
> **Purpose**: Extract production-depth engineering insights from the Part 2 deep-dive that go beyond the high-level overview.

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md), [Resilience Patterns](resilience/resilience-patterns.md)
> **Dictionary**: [Messaging](../../reference-dictionary/messaging.md), [CQRS & Event-Driven](../../reference-dictionary/cqrs-event-driven.md), [Resilience](../../reference-dictionary/resilience.md), [Data & Concurrency](../../reference-dictionary/data-concurrency.md)
> **Taxonomy Reference**: §3 Integration & Communication Architecture, §7 Reliability, Performance & Operations

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [broker-35](#broker-35) | Dual writes between DB and Kafka fail in three distinct ways | DB-first, Kafka-first, and retry-retry all produce different corruptions — outbox is the only safe path |
| [broker-36](#broker-36) | Choosing an outbox publisher: latency vs complexity vs volume | Debezium CDC for high-throughput, Lambda polling for simplicity, LISTEN/NOTIFY for mid-range PostgreSQL |
| [broker-37](#broker-37) | Making idempotency checks atomic under concurrent consumers | `attribute_not_exists(pk)` conditional write in DynamoDB provides a lock-free atomic check-and-set |
| [broker-38](#broker-38) | Low-cardinality partition keys create hot partitions | Use high-cardinality entity IDs as keys; apply salting only when ordering can be sacrificed |
| [broker-39](#broker-39) | How many partitions to provision for a topic | Apply four rules: consumer count, throughput target, broker limits, growth headroom |
| [broker-40](#broker-40) | DLQ retry counts lost when consumer restarts | Persist retry counts in DynamoDB with TTL so retries survive consumer crashes |
| [broker-41](#broker-41) | Transient failures need delay between retries without sleeping the consumer thread | Route to dedicated retry topics per delay tier (`retry_1s`, `retry_5s`, `retry_30s`) |
| [broker-42](#broker-42) | Synchronized retries hammer the recovering system in waves | Exponential backoff with full jitter desynchronizes retry storms |

---

## broker-35: Dual-Write Failure Modes

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Transactional Outbox

| | |
|:---|:---|
| **Problem** | An application that writes to a database and then to Kafka (or vice versa) produces different corruptions in each failure scenario, all of which are invisible at the application layer. |
| **Root cause** | Two independent transactional systems cannot be atomically coordinated without a distributed transaction coordinator — which Kafka does not support. |

**Strategy**: Recognize the three distinct failure scenarios before choosing a solution:

| Scenario | What fails | Outcome |
|:---|:---|:---|
| **DB-first** | Kafka send fails after DB commit | Ghost order: stored in DB, invisible to downstream services |
| **Kafka-first** | DB insert fails after Kafka send | Phantom order: downstream services process an order that doesn't exist |
| **Retry-retry** | DB succeeds on attempt 1; Kafka send retried → duplicate send | Double-charged customer; same event published twice |

All three scenarios are reliably prevented only by the Transactional Outbox: write business data + outbox record in a single DB transaction, publish from the outbox asynchronously.

| Tradeoff | Detail |
|:---|:---|
| **Safety** | Eliminates all three failure modes — exactly once DB write, at-least-once Kafka publish |
| **Latency** | Introduces milliseconds to seconds of delay between DB commit and Kafka delivery |
| **Simplicity** | Application code simplifies (no Kafka client in hot path), but infrastructure adds an outbox publisher |

> **Also see**: [Transactional Outbox Overview — broker-30](messaging/kafka-design-patterns.md#broker-30), [tx-07](concurrency-transactions/concurrency-transactions.md#tx-07-post-commit-confirmation-and-events)
> **Dictionary**: [Outbox Pattern](../../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [Dual-Write Problem](../../reference-dictionary/cqrs-event-driven.md#dual-write-problem)

---

## broker-36: Outbox Publisher Selection

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Transactional Outbox

| | |
|:---|:---|
| **Problem** | The outbox publisher can be implemented in three distinct ways, each with different tradeoffs in latency, throughput, complexity, and database compatibility. Choosing the wrong one for the volume class causes either unnecessary complexity or a performance ceiling. |
| **Root cause** | There is no single implementation of the outbox publisher that is optimal across all throughput bands and database engines. |

**Strategy**: Apply this decision matrix:

| Option | Latency | Max throughput | Complexity | DB compatibility |
|:---|:---|:---|:---|:---|
| **Lambda polling** | Up to polling interval (e.g., 100 ms) | < 1 K events/s | Low | Any RDBMS |
| **Debezium + MSK Connect** (CDC) | Milliseconds | Thousands of events/s | High | PostgreSQL, MySQL, Oracle, SQL Server |
| **PostgreSQL LISTEN/NOTIFY** | Milliseconds | Up to ~500 events/s | Medium | PostgreSQL only |

**Debezium CDC** reads from the database replication log (not the table), adding minimal load to the database and achieving near-zero latency. It uses the outbox event router transformation to auto-route each outbox record to the correct Kafka topic by `aggregate_type`.

**Lambda polling** is simpler but adds periodic DB load and up to the polling interval of latency. It requires locking or idempotent marking to prevent multiple pollers from publishing the same record.

| Tradeoff | Detail |
|:---|:---|
| **CDC overhead** | Debezium requires a database account with replication privileges and adds connector operational burden |
| **Polling simplicity** | Lambda polling works with any database but introduces latency and polling-induced load |
| **Scalability ceiling** | Both Debezium (single-task outbox router) and polling face a throughput limit; shard the outbox table to scale beyond it |

> **Also see**: [broker-35 Dual-Write Failure Modes](#broker-35), [Message Brokers — broker-01](messaging/message-brokers-async.md#broker-01-broker-selection)
> **Dictionary**: [Outbox Pattern](../../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [Change Data Capture](../../reference-dictionary/data-concurrency.md#change-data-capture)

---

## broker-37: Atomic Idempotency Check with DynamoDB Conditional Writes

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Idempotent Consumer

| | |
|:---|:---|
| **Problem** | A check-then-set idempotency implementation (read → decide → write) allows two concurrent consumers to both see no existing record and both process the same message — exactly the race condition idempotency must prevent. |
| **Root cause** | Separate read and write operations are not atomic; between the read and the write another actor can win the race. |

**Strategy**: Use DynamoDB's `attribute_not_exists(pk)` conditional write. This is a single, atomic server-side operation: the write succeeds only if the item does not already exist. The losing consumer receives a `ConditionalCheckFailedException` and skips processing.

```
Key = SHA-256(topic + ":" + partition + ":" + offset)
DynamoDB.PutItem(key, TTL=now+7d, ConditionExpression="attribute_not_exists(pk)")
→ Succeeds  → First consumer: process the message
→ Fails (ConditionalCheckFailedException) → Duplicate: skip processing
```

Set TTL to the replay window (typically 7 days) to auto-expire old markers without manual cleanup. Use SHA-256 of `topic:partition:offset` as the key — never the message content, because the same content may legitimately appear at different offsets.

| Tradeoff | Detail |
|:---|:---|
| **Atomicity** | No race condition possible — DynamoDB guarantees the check-and-set is atomic |
| **Extra latency** | One DynamoDB write per message (single-digit ms); acceptable for most workloads |
| **Cost** | DynamoDB on-demand mode scales cost with message volume; batch idempotency writes for very high throughput |

> **Also see**: [Idempotent Consumer Overview — broker-29](messaging/kafka-design-patterns.md#broker-29), [tx-04](concurrency-transactions/concurrency-transactions.md#tx-04-idempotency)
> **Dictionary**: [Idempotent Consumer](../../reference-dictionary/messaging.md#idempotent-consumer), [Exactly-Once Semantics](../../reference-dictionary/messaging.md#exactly-once-semantics)

---

## broker-38: Hot Partition and Partition Key Salting

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Partition Key / Ordering

| | |
|:---|:---|
| **Problem** | A low-cardinality partition key (e.g., `country_code`, `status`) routes a disproportionate share of traffic to one partition, saturating a single consumer while the others sit idle — wasting the parallelism provided by the partition layout. |
| **Root cause** | Kafka hashes the key modulo partition count; a key with only a few distinct values maps most traffic to a small subset of partitions. |

**Strategy**: Choose a high-cardinality entity identifier (`order_id`, `user_id`, `device_id`) as the key. The hash distributes billions of possible values across all partitions, keeping load even.

When high cardinality is impossible (e.g., a "system-wide config" key), apply **salting** — append a random suffix (`config:3`) to spread load — but understand the tradeoff:

| Approach | Ordering | Load distribution |
|:---|:---|:---|
| **Entity ID key** (e.g., `order_123`) | Strict per-entity ordering ✓ | Even if entity cardinality is high ✓ |
| **Low-cardinality key** (e.g., `US`) | Per-partition ordering ✓ | Heavily skewed ✗ (hot partition) |
| **Salted key** (e.g., `config:3`) | No per-entity ordering ✗ | Even across all partitions ✓ |

**Monitoring**: Alert when the coefficient of variation (CV) of `BytesInPerPartition` exceeds 1.0 — this indicates a highly skewed distribution.

| Tradeoff | Detail |
|:---|:---|
| **Ordering vs distribution** | Salting sacrifices ordering to regain even load; only use when ordering is not required |
| **Partition change risk** | Adding partitions changes which partition a key hashes to, breaking ordering for pre-change keys |

> **Also see**: [Partition Key Overview — broker-32](messaging/kafka-design-patterns.md#broker-32), [Message Brokers — broker-04](messaging/message-brokers-async.md#broker-04-message-ordering)
> **Dictionary**: [Hot Partition](../../reference-dictionary/messaging.md#hot-partition), [Partition](../../reference-dictionary/messaging.md#partition), [Message Ordering](../../reference-dictionary/messaging.md#message-ordering)

---

## broker-39: Partition Count Decision Framework

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Partition Key / Ordering

| | |
|:---|:---|
| **Problem** | Under-partitioning limits throughput and consumer parallelism; over-partitioning wastes broker memory, slows leader elections, and increases rebalance time. |
| **Root cause** | Partition count is immutable-by-key (changing it rekeys existing messages); it must be set correctly up front for the topic's expected lifetime. |

**Strategy**: Apply all four rules and take the maximum:

| Rule | Formula | Example |
|:---|:---|:---|
| **1. Consumer ceiling** | Partitions ≥ max expected consumers | 20 consumer replicas → ≥ 20 partitions |
| **2. Throughput target** | Partitions ≥ target MB/s ÷ 100 MB/s per partition | 500 MB/s → ≥ 5 partitions |
| **3. Broker limit** | Partitions ≤ broker-type limit (check MSK docs) | `kafka.m5.xlarge` → ≤ 1 500 |
| **4. Growth headroom** | Add 20–30% buffer for 12–24 months growth | Final estimate × 1.25 |

**Practical guidance**: For most systems, 50–200 partitions is the sweet spot. Start conservatively and plan a partition-increase event (with consumer downtime or duplicate handling) if you outgrow it.

| Tradeoff | Detail |
|:---|:---|
| **Adding partitions later** | Possible, but breaks key-to-partition mapping — all existing consumers must be able to handle out-of-order events during the transition |
| **Over-partitioning cost** | Each partition has a memory footprint on brokers and coordinators; excessive partition count increases leader election time on broker failures |

> **Also see**: [Message Brokers — broker-05](messaging/message-brokers-async.md#broker-05-stream-processing), [broker-32 Partition Key](messaging/kafka-design-patterns.md#broker-32)
> **Dictionary**: [Partition](../../reference-dictionary/messaging.md#partition), [Consumer Group](../../reference-dictionary/messaging.md#consumer-group)

---

## broker-40: DLQ with Persistent Retry Tracking

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Dead Letter Queue

| | |
|:---|:---|
| **Problem** | In-memory retry counts are reset when a consumer restarts. A message that reached retry limit 2 out of 3 before the crash is treated as fresh on the next startup, potentially doubling the intended retry budget and delaying DLQ routing. |
| **Root cause** | Consumer memory is ephemeral; only an external durable store preserves per-message retry state across process restarts. |

**Strategy**: Store retry counts in DynamoDB keyed by `topic:partition:offset` with a short TTL (24 hours). On each failure, increment the counter with a `PutItem` (overwrite is safe — it only adds 1 to the count). When `retry_count >= max_retries`, route to DLQ and delete the counter.

**DLQ envelope**: include the original message's topic/partition/offset, the error type and message, the retry count, and the timestamp — so operators can triage failures without inspecting the consuming application logs.

**DLQ Replay Tool**: maintain a replay script that reads the DLQ, restores original key and value, and republishes to the main topic. Always run in `dry_run=True` mode first to inspect what would be replayed before committing.

| Tradeoff | Detail |
|:---|:---|
| **Persistence cost** | One DynamoDB write per retry attempt; negligible cost compared to message loss |
| **Replay ordering** | Replayed messages get new offsets and may arrive after newer events; design consumers to handle out-of-order replay or replay during a maintenance window |
| **DLQ growth** | Set topic retention (e.g., 30 days) and CloudWatch alarms on DLQ lag; a growing DLQ is a signal of systemic upstream issues |

> **Also see**: [DLQ Overview — broker-28](messaging/kafka-design-patterns.md#broker-28), [Resilience Patterns — resilience-01](resilience/resilience-patterns.md)
> **Dictionary**: [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq), [Poison Message](../../reference-dictionary/messaging.md#poison-message)

---

## broker-41: Retry Topics for Delayed Retry Without Consumer Sleep

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Retry with Backoff

| | |
|:---|:---|
| **Problem** | Implementing exponential backoff with `time.sleep()` inside a consumer stalls partition processing and blocks all messages behind the failing one for the full wait period. |
| **Root cause** | A sleeping consumer holds its partition assignment; the backoff delay must be externalized to allow other messages on unaffected partitions to continue. |

**Strategy**: Route failed messages to dedicated **retry topics**, one per delay tier (e.g., `order_events.retry_1s`, `order_events.retry_5s`, `order_events.retry_30s`, `order_events.dlq`). Each retry consumer reads the `scheduled_at` timestamp embedded in the message and waits only until that timestamp before processing.

```
Main topic → fails → retry_1s (delay=1s)
retry_1s   → fails → retry_5s (delay=5s)
retry_5s   → fails → retry_30s (delay=30s)
retry_30s  → fails → DLQ (quarantine)
```

The main consumer never sleeps — it commits the offset and routes the failed message immediately. The delay is absorbed entirely by the retry consumer.

**Envelope schema**: wrap the original message payload with `retry_metadata` containing `stage`, `error_type`, `error_message`, `failed_at`, `retry_count`, and `scheduled_at`. Consumers use `scheduled_at` to determine when to actually process.

| Tradeoff | Detail |
|:---|:---|
| **Main-topic throughput** | Never blocked by a retrying message; only the retry consumer is delayed |
| **Topic proliferation** | 3–4 extra topics per main topic; manageable with naming conventions |
| **Ordering** | Retried messages arrive as new messages with new offsets; per-entity ordering is not preserved across retry tiers |

> **Also see**: [DLQ — broker-40](#broker-40), [Resilience Patterns — resilience-01](resilience/resilience-patterns.md), [broker-28 DLQ Overview](messaging/kafka-design-patterns.md#broker-28)
> **Dictionary**: [Retry Topic](../../reference-dictionary/messaging.md#retry-topic), [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq)

---

## broker-42: Exponential Backoff with Jitter (Thundering Herd Prevention)

> **Source**: [11 Kafka Design Patterns - Reliability & Ordering Deep Dive](../../articles/medium/11%20Kafka%20Design%20Patterns%20-%20Reliability%20%26%20Ordering%20Deep%20Dive.md) — Retry with Backoff

| | |
|:---|:---|
| **Problem** | When all consumers in a group experience the same transient failure simultaneously and retry after the same fixed delay, they produce synchronized waves of load that repeatedly overwhelm the recovering downstream system. |
| **Root cause** | Deterministic retry timing causes all clients to collide at exactly the same instant — the thundering herd problem applied to retry logic. |

**Strategy**: Use **full jitter** on top of exponential backoff:

```
delay = min(base × 2^attempt, max_delay)
jittered_delay = random.uniform(0, delay)    # full jitter: random between 0 and max
```

Full jitter is preferred over additive jitter because it spreads retries over the entire delay window, not just a narrow band around the deterministic value.

**Caps**: always set `max_tries` and `max_time` to prevent infinite retry loops. After the cap is exceeded, route to DLQ. A typical configuration: base=1s, max_delay=60s, max_tries=5.

| Tradeoff | Detail |
|:---|:---|
| **Load smoothing** | Jitter converts synchronized retry spikes into a smooth, distributed load on the recovering service |
| **Longer tail latency** | Some requests wait longer than the deterministic minimum; acceptable for transient failures |
| **Retry budget** | `max_tries × max_delay` defines the total retry budget; size it to outlast the expected outage duration |

> **Also see**: [Retry Topics — broker-41](#broker-41), [Resilience Patterns — resilience-01](resilience/resilience-patterns.md), [Circuit Breaker Honesty — cb-01](resilience/circuit-breaker-honesty.md)
> **Dictionary**: [Exponential Backoff](../../reference-dictionary/resilience.md#exponential-backoff), [Thundering Herd](../../reference-dictionary/resilience.md#thundering-herd)
