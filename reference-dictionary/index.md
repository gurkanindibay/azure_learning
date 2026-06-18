---
type: Reference
title: "Reference Dictionary"
description: "Repo-root reference dictionary for all technical terms used across this repository."
timestamp: 2026-06-18T00:00:00Z
---

# Reference Dictionary

> **Purpose**: Repo-root reference dictionary for all technical terms used across this repository — available to `architecture-azure/`, `architecture-general/`, `system-design-architecture/`, `programming-languages/`, `articles/`, and all other folders. Each file covers one domain; each term has a stable anchor ID for direct linking.

---

## How to Use

### Linking to a Term

From any file in the repo, use a relative path:

```
From system-design-architecture/:  [Projection](../reference-dictionary/cqrs-event-driven.md#projection)
From architecture-azure/:          [Projection](../reference-dictionary/cqrs-event-driven.md#projection)
From articles/medium/:              [Projection](../../reference-dictionary/cqrs-event-driven.md#projection)
From repo root (index.md):         [Projection](reference-dictionary/cqrs-event-driven.md#projection)
```

### Adding a New Term

1. Identify the correct domain file (or create a new one if needed)
2. Add the term in alphabetical order under its domain file
3. Use the format: `### term-name` (lowercase, hyphenated) for the anchor
4. Follow the template: Definition → Key Characteristics → When to Use / When NOT → Also See
5. Update this index if you add a new domain file

### Anchor Convention

- All anchors are lowercase, hyphenated: `#circuit-breaker`, `#rate-limiting`, `#acid-transactions`
- Terms that appear in multiple domains are defined once in their primary domain and cross-referenced from others

---

## Domain Files

| # | File | Domain | Key Terms |
|:---|:---|:---|:---|
| 1 | [`cqrs-event-driven.md`](cqrs-event-driven.md) | CQRS, Event Sourcing & Patterns | CQRS, Command Side, Query Side, Event Sourcing, Projection, Read Model, Ledger, Outbox Pattern, Post-Commit Dispatch, Idempotency, Dual-Write Problem, Event-Driven Architecture |
| 2 | [`resilience.md`](resilience.md) | Resilience & Fault Tolerance | Circuit Breaker, Half-Open State, Bulkhead, Aspect Order, Retry Amplification, Exponential Backoff, Fallback, Timeout, Resilience Stack, Graceful Degradation, Cascading Failure, Thundering Herd, Defense in Depth, Chaos Engineering, Load Shedding, Backpressure |
| 3 | [`messaging.md`](messaging.md) | Message Brokers & Async | Kafka vs RabbitMQ, Partition, Consumer Group, Offset Commit, DLQ, Poison Message, Message Ordering, At-Least-Once, Exactly-Once |
| 4 | [`api-design.md`](api-design.md) | API Design Patterns | API Versioning, Rate Limiting, Pagination, RFC 7807, Expand-Contract, Idempotency-Key, HATEOAS, Long-Running Operations, Consistent Hashing, Nagle's Algorithm / TCP_NODELAY |
| 5 | [`data-concurrency.md`](data-concurrency.md) | Data, Concurrency & Transactions | ACID, Atomic Conditional Update, Change Data Capture (CDC), Compensating Transaction, Distributed Lock, Double-Booking, Exclusion Constraint, Fencing Token, Isolation Levels, Lease-Based Lock, Optimistic/Pessimistic Locking, Saga, Sharding, Two-Phase Commit (2PC), CRDT |
| 6 | [`caching.md`](caching.md) | Caching Architecture | Cache Stampede, Cache-Aside, Invalidation, TTL, Eviction Policies, Request Coalescing, PER Algorithm |
| 7 | [`fintech.md`](fintech.md) | Fintech-Specific Terms | Reconciliation, Payment Gateway, Payment Processor, KYC, Limit Reservation, Risk Actions, Financial States, Ledger (Double-Entry) |
| 8 | [`ai-ml-llm.md`](ai-ml-llm.md) | AI/ML, LLM & Agentic AI | LLM, RAG, Vector DB, Embedding, Grounding, Hallucination, Agentic AI, Tool Calling, MCP, Five Levels, Dark Factory |
| 9 | [`dotnet-multithreading.md`](dotnet-multithreading.md) | .NET Multithreading & Async | TAP, Task, async/await, ThreadPool, ConfigureAwait, SemaphoreSlim, Mutex, lock, Barrier, Interlocked, Deadlock |
| 10 | [`azure-services.md`](azure-services.md) | Azure Services (Networking, Identity, Compute, Data, Integration, Observability) | VNet, NSG, Entra ID, Managed Identity, AKS, Cosmos DB, Event Hubs, Service Bus, Azure Monitor, Application Insights |
| 11 | [`architecture-patterns.md`](architecture-patterns.md) | Architecture & Design Patterns | DDD, Bounded Context, Ubiquitous Language, Database Per Service, Strangler Fig, Anti-Corruption Layer, Sidecar, Blue-Green, Canary, Well-Architected Framework, Virtual Threads, Leyden AOT, Helidon SE, GOMAXPROCS, Authentication, Authorization, JWT, OAuth2, Zero Trust, RBAC, ABAC, API Gateway, Microservices, Monolith, Progressive Delivery, Feature Flag, A/B Testing, Active-Active, Shadow Testing, OpenTelemetry, Golden Signals, Error Budget, Blameless Postmortem, Technical Debt, Upstream System, Downstream System |
| 12 | [`media-processing.md`](media-processing.md) | Media & Async Processing | GOP-Aligned Chunking, Transcoding, DASH/HLS, Fan-Out/Fan-In, Work Stealing, Embarrassingly Parallel |
| 13 | [`hsm-cryptography.md`](hsm-cryptography.md) | HSM & Cryptographic Infrastructure | HSM, LMK, PCI-DSS, Payment HSM, PIN Block Translation, Tokenization (DPAN), 3D Secure, Post-Quantum Cryptography, TLS, mTLS, Man-in-the-Middle Attack |
| 14 | [`java-jvm.md`](java-jvm.md) | Java JVM & Memory Management | JVM Heap, Young/Old Generation, Metaspace, PermGen, GC, Minor/Major/Full GC, G1GC, ZGC, OutOfMemoryError, Memory Leak, ThreadLocal, Heap Dump, Java Flight Recorder |
| 15 | [`databases.md`](databases.md) | Databases & Database Engines | effective_io_concurrency, io_method, io_uring, pg_aios, shared_buffers, B-Tree, Bloom Filter, LSM-Tree, Write-Ahead Log (WAL), Merkle Tree, Anti-Entropy, NoSQL |

---

## Cross-Domain Terms

Some terms span multiple domains. They are **defined once** in their primary domain and **cross-referenced** from others:

| Term | Primary Definition | Cross-Referenced In |
|:---|:---|:---|
| Compensating Transaction | [`data-concurrency.md#compensating-transaction`](data-concurrency.md#compensating-transaction) | cqrs-event-driven, fintech |
| Idempotency | [`cqrs-event-driven.md#idempotency`](cqrs-event-driven.md#idempotency) | resilience, messaging, api-design, data-concurrency, fintech |
| CQRS | [`cqrs-event-driven.md#cqrs`](cqrs-event-driven.md#cqrs) | fintech, data-concurrency, architecture-patterns |
| Circuit Breaker | [`resilience.md#circuit-breaker`](resilience.md#circuit-breaker) | messaging, api-design, azure-services |
| Rate Limiting | [`api-design.md#rate-limiting`](api-design.md#rate-limiting) | resilience, azure-services |
| Consistent Hashing | [`api-design.md#consistent-hashing`](api-design.md#consistent-hashing) | caching, messaging |
| HSM | [`hsm-cryptography.md#hsm`](hsm-cryptography.md#hsm) | azure-services, fintech |
| LLM | [`ai-ml-llm.md#llm`](ai-ml-llm.md#llm) | architecture-patterns |
| Task / async-await | [`dotnet-multithreading.md#task`](dotnet-multithreading.md#task) | data-concurrency |

---

## Quick Lookup by Problem

| I need to understand... | Go to... |
|:---|:---|
| "What's the difference between a projection and a read model?" | [`cqrs-event-driven.md#projection`](cqrs-event-driven.md#projection) |
| "How does the outbox pattern prevent dual-writes?" | [`cqrs-event-driven.md#outbox-pattern`](cqrs-event-driven.md#outbox-pattern) |
| "What's the right circuit breaker configuration?" | [`resilience.md#circuit-breaker`](resilience.md#circuit-breaker) |
| "Kafka vs RabbitMQ — which one?" | [`messaging.md#kafka-vs-rabbitmq`](messaging.md#kafka-vs-rabbitmq) |
| "How should I version my API?" | [`api-design.md#api-versioning`](api-design.md#api-versioning) |
| "How do I prevent double-booking?" | [`data-concurrency.md#double-booking`](data-concurrency.md#double-booking) |
| "How do I survive a cache stampede?" | [`caching.md#cache-stampede`](caching.md#cache-stampede) |
| "What does 'reconciliation' mean in fintech?" | [`fintech.md#reconciliation`](fintech.md#reconciliation) |
| "How does RAG reduce LLM hallucination?" | [`ai-ml-llm.md#rag`](ai-ml-llm.md#rag) |
| "TAP vs EAP vs APM — which .NET async pattern?" | [`dotnet-multithreading.md#tap`](dotnet-multithreading.md#tap) |
| "What's the difference between Event Hubs and Service Bus?" | [`azure-services.md#event-hubs`](azure-services.md#event-hubs) |
| "What is a Bounded Context in DDD?" | [`architecture-patterns.md#bounded-context`](architecture-patterns.md#bounded-context) |
| "Why can't HSMs scale horizontally?" | [`hsm-cryptography.md#hsm`](hsm-cryptography.md#hsm) |
| "What's the difference between authentication and authorization?" | [`architecture-patterns.md#authentication`](architecture-patterns.md#authentication) |
| "When should I use JWT vs sessions?" | [`architecture-patterns.md#jwt-json-web-token`](architecture-patterns.md#jwt-json-web-token) |
| "What's the difference between TLS and mTLS?" | [`hsm-cryptography.md#mtls-mutual-tls`](hsm-cryptography.md#mtls-mutual-tls) |
| "What's DASH/HLS adaptive streaming?" | [`media-processing.md#dash-hls`](media-processing.md#dash-hls) |
| "What is PostgreSQL 18's io_method setting?" | [`databases.md#io-method`](databases.md#io-method) |
| "What does effective_io_concurrency control?" | [`databases.md#effective-io-concurrency`](databases.md#effective-io-concurrency) |

---

> **Convention**: Every term anchor follows `domain-file.md#lowercase-hyphenated-term`. Always link to the primary definition, never to a cross-reference.
