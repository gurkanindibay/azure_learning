# System Design Interview: Problem → Strategy Reference

> **Sources**: Derived from [20 Design Interview Questions](../articles/medium/20-design-interview-questions.md), [Discord Data Architecture](../articles/medium/discord-data-architecture-master-class.md), and [Kafka Concepts](../articles/medium/kafka-concepts-that-every-architect-should-master.md)  
> **Purpose**: Look up a problem by architecture domain and find the strategy, tradeoff, and Azure implementation.  
> **Reference scheme**: Each problem is identified by a **domain prefix** (`db-`, `tx-`, `cache-`, `api-`, `broker-`) for self-documenting cross-references.

---

## Architecture Domains

| Domain | File | ID Range | Topics |
|:---|:---|:---|:---|
| 📊 **Databases & Query Performance** | [`01-databases-query-performance.md`](01-databases-query-performance.md) | `db-01` – `db-06` | UUID indexing, Pagination, Composite indexes, N+1, Hot partitions, DB migration at scale |
| 🔒 **Concurrency & Transactions** | [`02-concurrency-transactions.md`](02-concurrency-transactions.md) | `tx-01` – `tx-04` | Double-booking, Isolation levels, Distributed locks, Idempotency |
| ⚡ **Caching Architecture** | [`03-caching-architecture.md`](03-caching-architecture.md) | `cache-01` – `cache-05` | Cache stampede, Invalidation, Anti-patterns, Eviction, Request coalescing |
| 🌐 **APIs & Network Design** | [`04-api-network-design.md`](04-api-network-design.md) | `api-01` – `api-05` | Versioning, Rate limiting, Large uploads, Async tasks, Consistent hash routing |
| 📨 **Message Brokers & Async** | [`05-message-brokers-async.md`](05-message-brokers-async.md) | `broker-01` – `broker-07` | Broker selection, Offset commits, Poison messages, Ordering, Stream processing, Producer durability, Multi-consumer-group dedup |
| ☁️ **Azure Service Mapping** | [`07-azure-service-mapping.md`](07-azure-service-mapping.md) | — | Problem domain → Azure service quick lookup |

---

## ⚡ Quick Diagnostic Table

| Symptom | Likely Problem | Strategy | Ref |
|:---|:---|:---|:---:|
| "Page 100 is as fast as page 1, but page 10,000 times out" | OFFSET-based pagination | Keyset pagination | [`db-02`](01-databases-query-performance.md#db-02-keyset-pagination) |
| "Same user's data scattered across disk, inserts are slow" | Random UUID primary key | Time-sorted IDs | [`db-01`](01-databases-query-performance.md#db-01-random-uuid-indexing) |
| "101 queries for a page that should need 2" | N+1 lazy loading | Eager/batch loading | [`db-04`](01-databases-query-performance.md#db-04-n1-query-problem) |
| "Query filters by `user_id` and sorts by `created_at` — slow" | Missing composite index | Composite index design | [`db-03`](01-databases-query-performance.md#db-03-composite-index-vs-separate-indexes) |
| "One popular channel slows down the ENTIRE database cluster" | Hot partition + quorum amplification | Request coalescing + consistent hash routing | [`db-05`](01-databases-query-performance.md#db-05-hot-partition-problem) |
| "Need to migrate 4 trillion records without downtime" | Naive migration tooling | Dual-writes + checkpointed custom migrator | [`db-06`](01-databases-query-performance.md#db-06-database-migration-at-scale) |
| "Two users booked the same seat" | Race condition on check-then-act | DB-level locking or optimistic concurrency | [`tx-01`](02-concurrency-transactions.md#tx-01-double-booking) |
| "Transaction anomalies under concurrent writes" | Wrong isolation level | Isolation level escalation | [`tx-02`](02-concurrency-transactions.md#tx-02-isolation-levels) |
| "Lock expired during GC pause, two writers corrupted data" | Distributed lock without fencing | Fencing tokens | [`tx-03`](02-concurrency-transactions.md#tx-03-distributed-locks) |
| "Customer charged twice on retry" | Non-idempotent endpoint | Idempotency keys | [`tx-04`](02-concurrency-transactions.md#tx-04-idempotency) |
| "Database crushed when popular cache key expired" | Cache stampede | PER or lock-on-miss | [`cache-01`](03-caching-architecture.md#cache-01-cache-stampede) |
| "Stale cache after profile update" | Missing invalidation | Cache-aside + explicit delete + TTL | [`cache-02`](03-caching-architecture.md#cache-02-cache-invalidation) |
| "Adding Redis made the system slower" | Low cache hit rate | Break-even analysis | [`cache-03`](03-caching-architecture.md#cache-03-caching-anti-patterns) |
| "Users randomly logged out under load" | Wrong eviction policy | volatile-ttl for sessions | [`cache-04`](03-caching-architecture.md#cache-04-eviction-policies) |
| "500 users open the same page — DB crushed by 500 identical queries" | No request deduplication | In-flight request coalescing | [`cache-05`](03-caching-architecture.md#cache-05-request-coalescing-in-flight-deduplication) |
| "Old mobile app crashes after API change" | Breaking payload change | Add-only + versioning | [`api-01`](04-api-network-design.md#api-01-api-versioning) |
| "Client sends 2× allowed requests at window boundary" | Fixed window rate limiting | Sliding window log | [`api-02`](04-api-network-design.md#api-02-rate-limiting) |
| "5 GB upload kills the app server" | In-memory file handling | Presigned URLs or chunked upload | [`api-03`](04-api-network-design.md#api-03-large-file-uploads) |
| "40-second PDF generation times out HTTP connection" | Synchronous long-running task | 202 Accepted + polling | [`api-04`](04-api-network-design.md#api-04-long-running-tasks) |
| "Hot entity traffic scatters across instances — coalescing barely helps" | No request affinity | Consistent hash-based routing | [`api-05`](04-api-network-design.md#api-05-consistent-hash-based-routing) |
| "Using Kafka for 100msg/s task queue with complex routing" | Wrong broker choice | RabbitMQ for task queues | [`broker-01`](05-message-brokers-async.md#broker-01-broker-selection) |
| "Duplicate processing after consumer crash" | Uncommitted offset | Idempotent consumer design | [`broker-02`](05-message-brokers-async.md#broker-02-offset-commit-failure) |
| "One bad message blocks the entire queue" | Poison message without DLQ | DLQ + retry limits + alerting | [`broker-03`](05-message-brokers-async.md#broker-03-poison-messages) |
| "Messages processed out of order across consumers" | No partition key | Entity-level partitioning | [`broker-04`](05-message-brokers-async.md#broker-04-message-ordering) |
| "Payment events lost after Kafka broker crash" | Producer `acks=1` without replication | `acks=all` + idempotent producer | [`broker-06`](05-message-brokers-async.md#broker-06-producer-durability-tuning) |
| "Two consumer groups in different regions write duplicates to same DB" | Independent consumer groups | Single group ID, partition-by-region, or MirrorMaker 2 | [`broker-07`](05-message-brokers-async.md#broker-07-multi-consumer-group-duplicate-prevention) |

---

## Related Resources

| Resource | Path |
|:---|:---|
| Original 20 questions article | [`articles/medium/20-design-interview-questions.md`](../articles/medium/20-design-interview-questions.md) |
| Discord data architecture masterclass | [`articles/medium/discord-data-architecture-master-class.md`](../articles/medium/discord-data-architecture-master-class.md) |
| Kafka concepts every architect must master | [`articles/medium/kafka-concepts-that-every-architect-should-master.md`](../articles/medium/kafka-concepts-that-every-architect-should-master.md) |
| Azure event services full comparison | [`architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md`](../architecture-azure/integration/messaging-comparisons/azure_event_services_full_doc.md) |
| Azure messaging transaction quick reference | [`architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md`](../architecture-azure/integration/messaging-comparisons/azure_messaging_transaction_quick_reference.md) |
| Messaging patterns overview | [`architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/messaging-patterns-overview.md) |
| Idempotency store pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/idempotency-store-pattern.md) |
| Saga pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md) |
| Outbox pattern | [`architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md`](../architecture-general/03-integration-communication-architecture/messaging-patterns/outbox-pattern.md) |
| .NET concurrency patterns | [`dotNet_multi_threading/`](../dotNet_multi_threading/) |

---

> **Reminder**: Don't memorize the strategies — understand the pain points that make them necessary. Every answer is about scale, failure, and reality.
