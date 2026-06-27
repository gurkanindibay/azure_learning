---
type: System Design
title: "Kafka Design Patterns — Key Takeaways"
description: "11 reusable Kafka patterns covering state management, reliability, ordering, large-payload handling, distributed transactions, and stream-table joins."
timestamp: 2026-06-26T00:00:00Z
---

# 53. Kafka Design Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)
> **Purpose**: Extract reusable Kafka architectural patterns from the overview article covering all 11 patterns.

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md), [CQRS Fintech Takeaways](cqrs-fintech/cqrs-fintech.md)
> **Dictionary**: [Messaging](../../reference-dictionary/messaging.md), [CQRS & Event-Driven](../../reference-dictionary/cqrs-event-driven.md), [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Data & Concurrency](../../reference-dictionary/data-concurrency.md)
> **Taxonomy Reference**: §3 Integration & Communication Architecture, §4.3 Streaming & Real-Time Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [broker-24](#broker-24) | Need a complete audit trail and ability to replay state | Store events immutably in Kafka; derive state by replay |
| [broker-25](#broker-25) | Reads and writes scale at different rates; multiple views required | Separate write path (Kafka commands) from read-optimized stores |
| [broker-26](#broker-26) | Consumers repeatedly fetch context from the producer service | Embed the full state in each event to eliminate round-trips |
| [broker-27](#broker-27) | Messages exceed broker size limits; large payloads bloat the log | Store payload in external storage; send only a reference in Kafka |
| [broker-28](#broker-28) | Poison-pill messages block the consumer pipeline indefinitely | Quarantine unprocessable messages in a dedicated DLQ topic |
| [broker-29](#broker-29) | At-least-once delivery causes duplicate side-effects | Design consumers to be idempotent using deduplication stores |
| [broker-30](#broker-30) | Database write and Kafka publish must be atomic across systems | Write to an outbox table in the same DB transaction; publish separately |
| [broker-31](#broker-31) | Consumers need only the latest state per key, not the full history | Use a compacted topic (`cleanup.policy=compact`) as a key-value store |
| [broker-32](#broker-32) | Events for the same entity must be processed in strict order | Route by entity key so all messages for that key land on one partition |
| [broker-33](#broker-33) | A real-time stream needs to be joined with slowly-changing reference data | Treat the reference data as a Kafka table; join stream to table in ksqlDB |
| [broker-34](#broker-34) | Distributed transactions across microservices without 2PC | Choreography saga: each service publishes success/failure events; compensate on failure |

---

## broker-24: Event Sourcing on Kafka

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Applications need a full audit trail of every state change, the ability to replay history, and temporal queries ("what did the entity look like at time T?"). |
| **Root cause** | Storing only current state destroys history. Kafka's append-only log is naturally suited for immutable event sequences. |

**Strategy**: Publish every state-changing event to Kafka as an immutable record. Consumers rebuild current state by replaying from the earliest offset. Use schema registry for safe evolution; back topics to S3 for infinite retention.

| Tradeoff | Detail |
|:---|:---|
| **Auditability** | Complete, tamper-evident event history |
| **Replay cost** | Rebuilding state from offset 0 grows linearly with event volume; use snapshots to bound cost |
| **Schema evolution** | Breaking changes require careful versioning (Glue Schema Registry, Confluent Schema Registry) |

> **Also see**: [CQRS Fintech — cqrs-01](cqrs-fintech/cqrs-fintech.md#cqrs-01), [SQL System Design — sqld-03](databases/sql-system-design.md#sqld-03)
> **Dictionary**: [Event Sourcing](../../reference-dictionary/cqrs-event-driven.md#event-sourcing), [Projection](../../reference-dictionary/cqrs-event-driven.md#projection)

---

## broker-25: CQRS on Kafka

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Write throughput (1 K writes/s) and read throughput (100 K reads/s) have fundamentally different scaling requirements; a single model cannot serve both optimally. |
| **Root cause** | A unified read-write model forces the same data structure to satisfy both strong-consistency writes and fast, flexible reads. |

**Strategy**: Commands go to a Kafka topic. A consumer (Kafka Streams, Lambda, or ksqlDB) asynchronously projects events into read-optimized stores (DynamoDB, Aurora, OpenSearch). Reads bypass the command path entirely.

| Tradeoff | Detail |
|:---|:---|
| **Read scalability** | Read stores are independently scaled and purpose-built per query shape |
| **Eventual consistency** | Reads lag behind writes by the consumer processing latency |
| **Operational complexity** | Multiple stores to keep in sync; projection failures require replay |

> **Also see**: [CQRS Fintech Takeaways](cqrs-fintech/cqrs-fintech.md), [Global Payment CQRS](cqrs-fintech/global-payment-system.md)
> **Dictionary**: [CQRS](../../reference-dictionary/cqrs-event-driven.md#cqrs), [Read Model](../../reference-dictionary/cqrs-event-driven.md#read-model), [Command Side](../../reference-dictionary/cqrs-event-driven.md#command-side)

---

## broker-26: Event Carried State Transfer

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Downstream consumers need contextual data from the producing service on every event, resulting in chatty synchronous calls that add latency and tight coupling. |
| **Root cause** | Publishing only an identifier forces consumers to call back to the source, creating runtime dependencies and extra network hops. |

**Strategy**: Embed the complete consumer-relevant state in the event payload. Consumers act without additional fetches. Enforce a stable contract through schema registry; monitor payload size (stay under broker limits, typically 1 MB).

| Tradeoff | Detail |
|:---|:---|
| **Decoupling** | Consumers are independent of the producer's internal data store |
| **Payload size** | Large payloads increase broker disk and network usage; combine with Claim Check for payloads > 1 MB |
| **Schema coupling** | Consumers depend on the event schema; breaking changes still require coordination |

> **Also see**: [Claim Check — broker-27](#broker-27), [Message Brokers & Async](messaging/message-brokers-async.md)
> **Dictionary**: [Event Carried State Transfer](../../reference-dictionary/cqrs-event-driven.md#event-carried-state-transfer), [Event-Driven Architecture](../../reference-dictionary/cqrs-event-driven.md#event-driven-architecture)

---

## broker-27: Claim Check Pattern

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Message payloads (PDFs, images, large JSON) exceed Kafka's per-message size limit, causing producer failures and broker overload. |
| **Root cause** | Kafka is optimized for small, high-throughput messages; it is not a blob store. |

**Strategy**: Upload the large payload to external object storage (e.g., S3). Send a small Kafka message containing only the storage reference (bucket, key, optional presigned URL). Consumers fetch the payload on demand.

| Tradeoff | Detail |
|:---|:---|
| **Broker efficiency** | Kafka traffic stays small; broker disk and network load is reduced |
| **Extra latency** | Consumer must make a secondary fetch from object storage |
| **Storage lifecycle** | Set expiry/lifecycle rules on the object store to prevent unbounded growth |

> **Also see**: [Message Brokers & Async — broker-01](messaging/message-brokers-async.md#broker-01-broker-selection)
> **Dictionary**: [Claim Check Pattern](../../reference-dictionary/architecture-patterns.md#claim-check)

---

## broker-28: Dead Letter Queue (DLQ)

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | A malformed or permanently unprocessable message ("poison pill") blocks the consumer and halts all downstream processing on that partition. |
| **Root cause** | Synchronous retry loops on a failing message hold the consumer's offset, starving healthy messages behind it. |

**Strategy**: After exhausting retries, publish the failed message to a `<topic>.dlq` topic and commit the offset to advance past the poison pill. Separately monitor DLQ depth with alerts; replay or discard after human inspection.

| Tradeoff | Detail |
|:---|:---|
| **Pipeline health** | Main processing continues without blocking on unprocessable messages |
| **Data loss risk** | DLQ messages are quarantined, not reprocessed automatically; requires operational attention |
| **Observability** | DLQ message count is a leading indicator of upstream schema or logic issues |

> **Also see**: [Message Brokers — broker-03](messaging/message-brokers-async.md#broker-03-poison-messages)
> **Dictionary**: [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq), [Poison Message](../../reference-dictionary/messaging.md#poison-message)

---

## broker-29: Idempotent Consumer

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Kafka's at-least-once delivery causes duplicate messages on consumer restarts or rebalances, leading to double-charges, duplicate emails, or double-incremented counters. |
| **Root cause** | Exactly-once semantics require transactional producer + consumer configuration with significant throughput cost; at-least-once is the practical default. |

**Strategy**: Before processing, check an idempotency store (DynamoDB with TTL, Redis SETNX) keyed on `message-key + partition + offset`. If already processed, skip; otherwise process and mark as done atomically.

| Tradeoff | Detail |
|:---|:---|
| **Correctness** | Eliminates duplicate side-effects regardless of delivery semantics |
| **Extra I/O** | One idempotency check per message; use TTL to bound store size |
| **Complexity** | Requires careful atomic check-and-mark; two-phase check with DB transactions |

> **Also see**: [Message Brokers — broker-02](messaging/message-brokers-async.md#broker-02-offset-commit-failure), [Concurrency — tx-04](concurrency-transactions/concurrency-transactions.md#tx-04-idempotency)
> **Dictionary**: [Idempotent Consumer](../../reference-dictionary/messaging.md#idempotent-consumer), [At-Least-Once Semantics](../../reference-dictionary/messaging.md#at-least-once-semantics)

---

## broker-30: Transactional Outbox

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | A service must atomically update a database and publish a Kafka event; a crash between the two steps causes either a missing event or a ghost event with no matching DB record. |
| **Root cause** | Databases and Kafka are separate transactional systems — there is no distributed coordinator spanning both. |

**Strategy**: Write the business record and an outbox row in the **same local DB transaction**. A separate poller or CDC connector (Debezium) reads committed outbox rows and publishes to Kafka, then marks them sent.

| Tradeoff | Detail |
|:---|:---|
| **Atomicity** | DB write and event publish are effectively coupled through the outbox table |
| **Latency** | Adds poller delay (ms–s) between DB commit and Kafka message visibility |
| **Operational overhead** | Outbox table must be monitored; growth indicates a publishing failure |

> **Also see**: [Concurrency — tx-07](concurrency-transactions/concurrency-transactions.md#tx-07-post-commit-confirmation-and-events), [CQRS Fintech — cqrs-07](cqrs-fintech/cqrs-fintech.md)
> **Dictionary**: [Outbox Pattern](../../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [Dual-Write Problem](../../reference-dictionary/cqrs-event-driven.md#dual-write-problem)

---

## broker-31: Compacted Topic

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | A changelog stream contains many historical values per key; new consumers must replay the entire log to learn current state, even though only the latest value matters. |
| **Root cause** | Default time/size-based retention is agnostic to key uniqueness; it cannot collapse history to latest-per-key. |

**Strategy**: Configure `cleanup.policy=compact`. Kafka's log compactor removes all but the latest message for each key. New consumers starting from the beginning receive only the current state per key — effectively bootstrapping from a key-value snapshot.

| Tradeoff | Detail |
|:---|:---|
| **Bootstrap efficiency** | New consumers get current state without replaying full history |
| **No time-travel** | Historical values are deleted; combine with event-sourcing topics for full history |
| **Compaction lag** | The dirty log is compacted asynchronously; very recent old values may still be visible briefly |

> **Also see**: [Stream-Table Duality — broker-33](#broker-33), [Event Sourcing — broker-24](#broker-24)
> **Dictionary**: [Compacted Topic](../../reference-dictionary/messaging.md#compacted-topic)

---

## broker-32: Partition Key / Ordering Pattern

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | Events for the same entity (order, user, device) must be processed in arrival order, but routing messages across all partitions destroys per-entity ordering. |
| **Root cause** | Kafka guarantees ordering only within a single partition; messages from the same producer can land on different partitions without a key. |

**Strategy**: Set the Kafka message key to the entity identifier (e.g., `order_id`). Kafka's default partitioner hashes the key to a fixed partition, ensuring all messages for that entity land on the same partition and are consumed in order.

| Tradeoff | Detail |
|:---|:---|
| **Per-entity ordering** | Strict ordering within a key, with full parallelism across different keys |
| **Hot partition risk** | Low-cardinality keys (e.g., `status=active`) cause skewed partition load |
| **Consumer parallelism** | Max concurrency = partition count; add partitions before scaling consumers |

> **Also see**: [Message Brokers — broker-04](messaging/message-brokers-async.md#broker-04-message-ordering), [Real-Time Messaging — broker-18](messaging/real-time-messaging.md#broker-18)
> **Dictionary**: [Partition](../../reference-dictionary/messaging.md#partition), [Message Ordering](../../reference-dictionary/messaging.md#message-ordering)

---

## broker-33: Stream-Table Duality

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | A real-time event stream (clicks, transactions) must be enriched with slowly-changing reference data (user profiles, product catalog), but polling a database per event is too slow and creates tight coupling. |
| **Root cause** | Streams and tables are treated as separate abstractions requiring a synchronous bridge, when Kafka already supports both views of the same data. |

**Strategy**: Model reference data as a Kafka table backed by a compacted topic (latest-per-key). Use ksqlDB or Kafka Streams to join the event stream to the table in-process, with local state stores for sub-millisecond lookups.

| Tradeoff | Detail |
|:---|:---|
| **Join latency** | Local state store joins are sub-millisecond vs network-hop DB queries |
| **State store size** | Reference tables that exceed available memory spill to disk (RocksDB); size appropriately |
| **Reprocessing** | Stream-table joins are sensitive to table bootstrap order; replay requires coordinating both |

> **Also see**: [Stream Processing — flink-01](stream-processing/stream-processing-flink.md), [Compacted Topic — broker-31](#broker-31)
> **Dictionary**: [Stream-Table Duality](../../reference-dictionary/messaging.md#stream-table-duality), [Compacted Topic](../../reference-dictionary/messaging.md#compacted-topic)

---

## broker-34: Saga (Choreography)

> **Source**: [11 Kafka Design Patterns for Every Backend Engineer](../../articles/messaging/11 Kafka Design Patterns for Every Backend Engineer.md)

| | |
|:---|:---|
| **Problem** | A business workflow spans multiple microservices (order → payment → inventory) and must be atomic, but two-phase commit (2PC) across services introduces deadlocks and tight coupling. |
| **Root cause** | 2PC requires a distributed coordinator that holds locks for the duration of the transaction; this is impractical for long-running, loosely-coupled services. |

**Strategy**: Each service performs its local transaction and publishes a success or failure event to Kafka. Downstream services listen and react. On failure, the failing service publishes a compensation event; each upstream service listens and executes a compensating transaction (undo).

| Tradeoff | Detail |
|:---|:---|
| **Loose coupling** | No central coordinator; services are independently deployable |
| **Debugging complexity** | A distributed transaction is visible only by correlating events across multiple topics |
| **Compensation design** | Compensating transactions must be idempotent and must cover all failure modes upfront |

> **Also see**: [Concurrency — tx-09](concurrency-transactions/concurrency-transactions.md), [Design Patterns — dp-11](software-architecture/design-patterns.md)
> **Dictionary**: [Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern)
