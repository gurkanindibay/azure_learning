---
type: System Design
title: "Azure Service Mapping"
generated: { by: process:okf-migrate, at: 2026-09-06T00:00:00Z }
---

# 7. Azure Service Mapping

> **Parent**: [System Design Interview Reference](../index.md)  
> **Purpose**: Map each problem domain to the Azure service that solves it.

---

## Problem Domain → Azure Service

| Problem Domain | Azure Service | Key Feature |
|:---|:---|:---|
| UUID indexing | Azure SQL, Cosmos DB | Index tuning, automatic indexing |
| Pagination | Cosmos DB | Continuation tokens (native keyset) |
| Composite indexes | Azure SQL | Missing index DMVs, Query Performance Insight |
| N+1 detection | App Insights | Dependency tracking, query aggregation |
| Double-booking | Cosmos DB | Optimistic concurrency (ETags) |
| Distributed locks | Blob Storage | Lease-based distributed lock |
| Idempotency | Service Bus | Duplicate detection window |
| Caching | Azure Cache for Redis | All eviction policies, Redis 6.2+ `GETEX` |
| Rate limiting | API Management | Rate-limit + quota policies |
| Large uploads | Blob Storage | SAS tokens (presigned URLs) |
| Long-running tasks | Durable Functions | Orchestrations with state |
| Messaging (queue) | Service Bus | Queues, topics, sessions, DLQ, transactions |
| Messaging (stream) | Event Hubs | Kafka protocol, partitions, replay |
| Messaging (pub-sub) | Event Grid | Push-based, serverless, filtering |

---

## Related Azure Comparisons

| Resource | Path |
|:---|:---|
| Azure event services full comparison | [`architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md`](../../architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md) |
| Azure messaging transaction quick reference | [`architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md`](../../architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md) |
| Event Hubs vs Kafka | [`architecture-azure/integration/messaging-comparisons/eventhubs_vs_kafka_comparison.md`](../../architecture-azure/integration/messaging-comparisons/eventhubs_vs_kafka_comparison.md) |
| Service Bus vs Kafka | [`architecture-azure/integration/messaging-comparisons/servicebus_vs_kafka_comparison.md`](../../architecture-azure/integration/messaging-comparisons/servicebus_vs_kafka_comparison.md) |

---

## Related General Patterns

| Resource | Path |
|:---|:---|
| Messaging patterns overview | [`architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md`](../../../architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md) |
| Idempotency store pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md`](../../../architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md) |
| Saga pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md`](../../../architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md) |
| Outbox pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md`](../../../architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md) |
| .NET concurrency patterns | [`programming-languages/csharp/dotnet-multi-threading/`](../../programming-languages/csharp/dotnet-multi-threading/) |
