# System Design Interview: Problem → Strategy Reference

> **Source**: Derived from [20 Design Interview Questions](../articles/medium/20-design-interview-questions.md)  
> **Purpose**: Look up a problem by architecture domain and find the strategy, tradeoff, and Azure implementation.

---

## Architecture Domains

| Domain | File | Problems Covered |
|:---|:---|:---|
| 📊 **Databases & Query Performance** | [`01-databases-query-performance.md`](01-databases-query-performance.md) | P1–P4: UUID indexing, Pagination, Composite indexes, N+1 |
| 🔒 **Concurrency & Transactions** | [`02-concurrency-transactions.md`](02-concurrency-transactions.md) | P5–P8: Double-booking, Isolation levels, Distributed locks, Idempotency |
| ⚡ **Caching Architecture** | [`03-caching-architecture.md`](03-caching-architecture.md) | P9–P12: Cache stampede, Invalidation, Anti-patterns, Eviction |
| 🌐 **APIs & Network Design** | [`04-api-network-design.md`](04-api-network-design.md) | P13–P16: Versioning, Rate limiting, Large uploads, Async tasks |
| 📨 **Message Brokers & Async** | [`05-message-brokers-async.md`](05-message-brokers-async.md) | P17–P20: Broker selection, Offset commits, Poison messages, Ordering |
| ☁️ **Azure Service Mapping** | [`07-azure-service-mapping.md`](07-azure-service-mapping.md) | Problem domain → Azure service quick lookup |

---

## ⚡ Quick Diagnostic Table

| Symptom | Likely Problem | Strategy | Go To |
|:---|:---|:---|:---:|
| "Page 100 is as fast as page 1, but page 10,000 times out" | OFFSET-based pagination | Keyset pagination | [P2](01-databases-query-performance.md#p2-keyset-pagination) |
| "Same user's data scattered across disk, inserts are slow" | Random UUID primary key | Time-sorted IDs | [P1](01-databases-query-performance.md#p1-random-uuid-indexing) |
| "101 queries for a page that should need 2" | N+1 lazy loading | Eager/batch loading | [P4](01-databases-query-performance.md#p4-n1-query-problem) |
| "Query filters by `user_id` and sorts by `created_at` — slow" | Missing composite index | Composite index design | [P3](01-databases-query-performance.md#p3-composite-index-vs-separate-indexes) |
| "Two users booked the same seat" | Race condition on check-then-act | DB-level locking or optimistic concurrency | [P5](02-concurrency-transactions.md#p5-double-booking) |
| "Transaction anomalies under concurrent writes" | Wrong isolation level | Isolation level escalation | [P6](02-concurrency-transactions.md#p6-isolation-levels) |
| "Lock expired during GC pause, two writers corrupted data" | Distributed lock without fencing | Fencing tokens | [P7](02-concurrency-transactions.md#p7-distributed-locks) |
| "Customer charged twice on retry" | Non-idempotent endpoint | Idempotency keys | [P8](02-concurrency-transactions.md#p8-idempotency) |
| "Database crushed when popular cache key expired" | Cache stampede | PER or lock-on-miss | [P9](03-caching-architecture.md#p9-cache-stampede) |
| "Stale cache after profile update" | Missing invalidation | Cache-aside + explicit delete + TTL | [P10](03-caching-architecture.md#p10-cache-invalidation) |
| "Adding Redis made the system slower" | Low cache hit rate | Break-even analysis | [P11](03-caching-architecture.md#p11-caching-anti-patterns) |
| "Users randomly logged out under load" | Wrong eviction policy | volatile-ttl for sessions | [P12](03-caching-architecture.md#p12-eviction-policies) |
| "Old mobile app crashes after API change" | Breaking payload change | Add-only + versioning | [P13](04-api-network-design.md#p13-api-versioning) |
| "Client sends 2× allowed requests at window boundary" | Fixed window rate limiting | Sliding window log | [P14](04-api-network-design.md#p14-rate-limiting) |
| "5 GB upload kills the app server" | In-memory file handling | Presigned URLs or chunked upload | [P15](04-api-network-design.md#p15-large-file-uploads) |
| "40-second PDF generation times out HTTP connection" | Synchronous long-running task | 202 Accepted + polling | [P16](04-api-network-design.md#p16-long-running-tasks) |
| "Using Kafka for 100msg/s task queue with complex routing" | Wrong broker choice | RabbitMQ for task queues | [P17](05-message-brokers-async.md#p17-broker-selection) |
| "Duplicate processing after consumer crash" | Uncommitted offset | Idempotent consumer design | [P18](05-message-brokers-async.md#p18-offset-commit-failure) |
| "One bad message blocks the entire queue" | Poison message without DLQ | DLQ + retry limits + alerting | [P19](05-message-brokers-async.md#p19-poison-messages) |
| "Messages processed out of order across consumers" | No partition key | Entity-level partitioning | [P20](05-message-brokers-async.md#p20-message-ordering) |

---

## Related Resources

| Resource | Path |
|:---|:---|
| Original 20 questions article | [`articles/medium/20-design-interview-questions.md`](../articles/medium/20-design-interview-questions.md) |
| Azure event services full comparison | [`architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md`](../architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md) |
| Azure messaging transaction quick reference | [`architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md`](../architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md) |
| Messaging patterns overview | [`architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md) |
| Idempotency store pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md) |
| Saga pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md) |
| Outbox pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md) |
| .NET concurrency patterns | [`dotNet_multi_threading/`](../dotNet_multi_threading/) |

---

> **Reminder**: Don't memorize the strategies — understand the pain points that make them necessary. Every answer is about scale, failure, and reality.
