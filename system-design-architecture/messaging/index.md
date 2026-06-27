---
type: Index
title: "Messaging & Event Streaming"
description: "System-design problems and strategies for message brokers, Kafka patterns, offset commit strategies, real-time messaging, and distributed log architecture."
timestamp: 2026-06-27T00:00:00Z
---

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
| [kafka-distributed-log-architecture.md](kafka-distributed-log-architecture.md) | — | Log-based architecture, Coordination-free design, Zero-copy transfer, Partition-driven scaling |
| [kafka-producer-ack-idempotency.md](kafka-producer-ack-idempotency.md) | `broker-59` – `broker-65` | Producer ack failure, Idempotent consumer, Atomic deduplication, Shared dedup store, Effective exactly-once |
| [apache-iggy.md](apache-iggy.md) | `iggy-01` – `iggy-08` | Kafka alternative landscape, Rust in infrastructure, io_uring, Streaming use-case fit |

## Cross-References

- **Dictionary**: [Messaging](../../reference-dictionary/messaging.md), [CQRS/Events](../../reference-dictionary/cqrs-event-driven.md)
- **Azure**: [Event Hubs](../../architecture-azure/integration/), [Service Bus](../../architecture-azure/integration/)
- **Related**: [Stream Processing](../stream-processing/), [CQRS & Fintech](../cqrs-fintech/), [Resilience](../resilience/)
- **Taxonomy**: §3.3 Event-Driven & Messaging
