
# Messaging & Event Streaming

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for designing message-based and event-driven systems: broker selection, Kafka consumer patterns, offset management, real-time messaging, and distributed log architecture.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [message-brokers-async.md](message-brokers-async.md) | `broker-01` – `broker-12` | Broker selection, Offset commits, Poison messages, Ordering, Stream processing, Producer durability |
| [kafka-consumer-mistakes.md](kafka-consumer-mistakes.md) | — | 5 Kafka consumer anti-patterns that destroy production systems |
| [kafka-offset-commit-strategies.md](kafka-offset-commit-strategies.md) | — | Auto/manual commit, Batch processing, Transactions, Rebalancing, Strategy selection |
| [real-time-messaging.md](real-time-messaging.md) | — | Per-conversation partitioning, Per-device inboxes, Fan-out, Presence, Multi-device sync |
| [kafka-design-patterns.md](kafka-design-patterns.md) | `broker-13` – `broker-30` | Event Sourcing, CQRS, Event Carried State Transfer, Claim Check, DLQ, Idempotent Consumer, Transactional Outbox, Compacted Topic |
| [kafka-reliability-ordering.md](kafka-reliability-ordering.md) | `broker-31` – `broker-40` | Dual-Write failure modes, Outbox publisher selection, Hot partition mitigation, DLQ retry tracking, Retry topics, Exponential backoff |
| [kafka-data-state.md](kafka-data-state.md) | `broker-41` – `broker-48` | Aggregate snapshots, S3 archiving, Cryptographic erasure, Polyglot persistence, Read-after-write consistency, Out-of-order event upsert |
| [kafka-performance-integration.md](kafka-performance-integration.md) | `broker-49` – `broker-58` | Snapshot+delta bootstrap, Fat Events vs Fetcher, Orphaned S3 cleanup, RocksDB local state joins, Late-arriving data, Choreography vs orchestration |
| [kafka-distributed-log-architecture.md](kafka-distributed-log-architecture.md) | `broker-59` – `broker-62`, `broker-86` – `broker-89` | Log-based architecture, Coordination-free design, Zero-copy transfer, Partition-driven scaling, Immutable event log model, Log segments, Leader-follower replication, acks+ISR consistency |
| [kafka-producer-ack-idempotency.md](kafka-producer-ack-idempotency.md) | `broker-59` – `broker-65` | Producer ack failure, Idempotent consumer, Atomic deduplication, Shared dedup store, Effective exactly-once |
| [senior-engineers-kafka-tradeoffs.md](senior-engineers-kafka-tradeoffs.md) | `broker-66` – `broker-71` | Requirements-first design, Read/write path separation, Idempotency, Kafka role clarity, Caching strategy, Design for failure |
| [apache-iggy.md](apache-iggy.md) | `iggy-01` – `iggy-08` | Kafka alternative landscape, Rust in infrastructure, io_uring, Streaming use-case fit |
| [kafka-user-activity-tracking.md](kafka-user-activity-tracking.md) | `broker-72` – `broker-76` | Constraints-first design, Async publishing degradation, Immutable event contracts, Consumer lag as design feature, Replay-safe idempotency |
| [kafka-pipeline-bottlenecks.md](kafka-pipeline-bottlenecks.md) | `broker-102` – `broker-110` | Consumer lag detection, Rebalance storms, Hot partitions, Slow-event blocking, Backpressure, Poison messages & DLQ, Retry amplification, Downstream bottleneck shifting, Real-time vs batching |
| [kafka-real-world-scenarios.md](kafka-real-world-scenarios.md) | `broker-77` – `broker-85` | Partition key design, Idempotency + offset coordination, Event backbone, Stream aggregation, CDC, Schema governance, Consumer lag, Event-time semantics, Kafka Connect hub |
| [million-notifications-system-design.md](million-notifications-system-design.md) | `broker-90` – `broker-96` | Queue-based async processing, Provider rate limiting, Idempotent notification, Batch delivery, DLQ, Campaign generation scaling, Delivery tracking |
| [whatsapp-duplicate-messages-idempotency.md](whatsapp-duplicate-messages-idempotency.md) | `broker-97` – `broker-101` | At-least-once delivery, Three-layer dedup, Idempotency key, Server-crash recovery, Duplicate monitoring |
| [notifications-at-scale-takeaways.md](notifications-at-scale-takeaways.md) | `broker-111` – `broker-118` | Asynchronous acceptance/delivery decoupling, Durable queue buffering, Worker self-throttling, Idempotent delivery, Batching, DLQs, Progressive enqueuing, Decoupled analytics |

## Cross-References

- **Dictionary**: [Messaging](../../reference-dictionary/messaging.md), [CQRS/Events](../../reference-dictionary/cqrs-event-driven.md)
- **Azure**: [Event Hubs](../../architecture-azure/integration/), [Service Bus](../../architecture-azure/integration/)
- **Related**: [Stream Processing](../stream-processing/), [CQRS & Fintech](../cqrs-fintech/), [Resilience](../resilience/)
- **Taxonomy**: §3.3 Event-Driven & Messaging
