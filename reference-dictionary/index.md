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
| 1 | [`cqrs-event-driven.md`](cqrs-event-driven.md) | CQRS, Event Sourcing & Patterns | CQRS, Command Side, Query Side, Event Sourcing, Projection, Read Model, Ledger, Outbox Pattern, Post-Commit Dispatch, Idempotency, Dual-Write Problem, Event-Driven Architecture, Async Workflow, Deterministic Processing, Orchestrator-based Saga |
| 2 | [`resilience.md`](resilience.md) | Resilience & Fault Tolerance | Circuit Breaker, Half-Open State, Bulkhead, Aspect Order, Retry Amplification, Exponential Backoff, Fallback, Timeout, Resilience Stack, Graceful Degradation, Cascading Failure, Thundering Herd, Defense in Depth, Chaos Engineering, Load Shedding, Backpressure, Defensive Programming, Input Validation, Parameterized Query, Virtual Waiting Room, Retry Budget, Provider Failover, Client-Side Resend Backoff, Queue with TTL |
| 3 | [`observability.md`](observability.md) | Observability | Observability, OpenTelemetry, Golden Signals, Error Budget, Blameless Postmortem, Real User Monitoring (RUM), Configuration Propagation, Abuse-Block Counts |
| 4 | [`messaging.md`](messaging.md) | Message Brokers & Async | Kafka vs RabbitMQ, Partition, Consumer Group, Offset Commit, DLQ, Poison Message, Message Ordering, At-Least-Once, Exactly-Once, Redis Streams, Per-Device Inbox, Competing Consumers, Claim Check, Atomic Deduplication, Deduplication Store, Distributed Commit Log, Message Batching, Fanout on Write/Read, Hybrid Fanout, Choreography, Orchestration, Configuration Server, Apache Flink, Three-Layer Deduplication, Stream Sessionization, Stream-Stream Join, In-Stream Keyed Deduplication |
| 5 | [`networking.md`](networking.md) | Networking | Anycast, BGP, PoP, Hub-and-Spoke, DMZ, CDN, Service Mesh, Load Balancer, API Gateway, Consistent Hashing, Nagle's Algorithm / TCP_NODELAY, Zero-Copy Transfer, Network Partition, Robots Exclusion Protocol, Politeness Policy |
| 6 | [`api-design.md`](api-design.md) | API Design Patterns | API Versioning, Rate Limiting, Hierarchical Rate Limiting, Pagination, RFC 7807, Expand-Contract, Idempotency-Key, HATEOAS, Long-Running Operations, Hotlinking, Faceted Search, WebSocket, PRG Pattern, Lazy Subscription, Stateful Gateway |
| 7 | [`data-concurrency.md`](data-concurrency.md) | Data, Concurrency & Transactions | ACID, asyncio, Atomic Conditional Update, Causal Ordering, Change Data Capture (CDC), Compensating Transaction, Distributed Lock, Double-Booking, Exclusion Constraint, Fencing Token, Global Interpreter Lock (GIL), Inventory Reservation, Isolation Levels, Lease-Based Lock, Lock Contention, Lock Ordering, Lock-Transaction Inversion, Optimistic/Pessimistic Locking, Overselling, Saga, Sharding, Task Claiming, Two-Phase Commit (2PC), CRDT, Shard Key, Two Generals Problem, Operational Transformation (OT) |
| 8 | [`caching.md`](caching.md) | Caching Architecture | Cache Stampede, Cache-Aside, Invalidation, TTL, Eviction Policies, Request Coalescing, PER Algorithm, Write-Through, Timeline Cache, Celebrity Cache, Hot Key, Trie Cache, SET NX, Safe Lock Release, Redlock Algorithm |
| 9 | [`fintech.md`](fintech.md) | Fintech-Specific Terms | Reconciliation, Payment Gateway, Payment Processor, KYC, Limit Reservation, Risk Actions, Financial States, Ledger (Double-Entry), Merchant Onboarding, Merchant Transaction Identifier, Payment Method Aggregation, Settlement, Smart Routing, Business Identity, Retry Identity |
| 10 | [`ai-ml-llm.md`](ai-ml-llm.md) | AI/ML, LLM & Agentic AI | LLM, RAG, Vector DB, Embedding, Grounding, Hallucination, Agentic AI, Tool Calling, MCP, Five Levels, Dark Factory, Structure-Aware Chunking, Semantic Chunking, Chunk Inspection Audit |
| 11 | [`dotnet-multithreading.md`](dotnet-multithreading.md) | .NET Multithreading & Async | TAP, Task, async/await, ThreadPool, ConfigureAwait, SemaphoreSlim, Mutex, lock, Barrier, Interlocked, Deadlock |
| 12 | [`azure-services.md`](azure-services.md) | Azure Services (Networking, Identity, Compute, Data, Integration, Observability) | VNet, NSG, Entra ID, Managed Identity, AKS, Cosmos DB, Event Hubs, Service Bus, Azure Monitor, Application Insights |
| 13 | [`architecture-patterns.md`](architecture-patterns.md) | Architecture & Cloud Patterns | DDD, Bounded Context, Ubiquitous Language, Database Per Service, Business Capability, Service Decomposition, Service Discovery, Strangler Fig, Anti-Corruption Layer, Modular Monolith, Shared Kernel, Sidecar, Ambassador, Well-Architected Framework, CAF, Virtual File System (VFS), Microservices, Monolith, Distributed Monolith, Native Extension, Technical Debt, Upstream/Downstream, Circular Dependency, Base62 Encoding, URL Shortener, Key Generation Service, Presence Service, Read/Write Path Separation, Back-of-the-Envelope Estimation, Coordination Cost, Flash Sale, Surge Pricing, Cooldown, URL Frontier, Acceptance-Delivery Separation, Frequency Capping, Transient Metadata Registry, Route-to-Data Pattern |
| 14 | [`deployment-patterns.md`](deployment-patterns.md) | Deployment & Release Patterns | Blue-Green, Canary Deployment, Blue-Green vs Canary, Progressive Delivery, Feature Flag, A/B Testing, Active-Active, Shadow Testing, Deployment Coupling, Pod Affinity, Node Affinity, Topology Spread Constraints, Deterministic Traffic Dialing |
| 15 | [`design-patterns.md`](design-patterns.md) | Design Patterns & Software Engineering Principles | Singleton, Factory Method, Builder, Adapter, Decorator, Proxy, Strategy, Observer, Command, Repository, Golden Hammer, YAGNI, Separation of Concerns, Fail Fast, Single Source of Truth, Loose Coupling, Immutability, Scalability, Architecture Decision Record, Anti-pattern |
| 16 | [`concurrency-runtimes.md`](concurrency-runtimes.md) | Concurrency Models & Language Runtimes | GOMAXPROCS, Goroutine, M:N Scheduling, Tokio, Event Loop, Context Switching, Amdahl's Law, Actor Model, I/O-bound vs CPU-bound, Race Condition, Thread Pool Sizing Formula, CPU Cache Hierarchy, Cache Line, Hardware Prefetching, Pointer Chasing, False Sharing, Memory Stall |
| 17 | [`media-processing.md`](media-processing.md) | Media & Async Processing | GOP-Aligned Chunking, Transcoding, DASH/HLS, Fan-Out/Fan-In, Work Stealing, Embarrassingly Parallel, Quality Ladder, Adaptive Bitrate Streaming (ABR), HLS, MPEG-DASH, Transcoding DAG Model, Selective Forwarding Unit (SFU), Server-Side Ad Insertion (SSAI), Video Ad Serving Template (VAST) |
| 18 | [`hsm-cryptography.md`](hsm-cryptography.md) | HSM & Cryptographic Infrastructure | HSM, LMK, PCI-DSS, Payment HSM, PIN Block Translation, Tokenization (DPAN), 3D Secure, Post-Quantum Cryptography, End-to-End Encryption (E2EE), TLS, mTLS, Man-in-the-Middle Attack |
| 19 | [`java-jvm.md`](java-jvm.md) | Java JVM & Memory Management | JVM Heap, Young/Old Generation, Metaspace, PermGen, GC, Minor/Major/Full GC, GC Pause, G1GC, ZGC, OutOfMemoryError, Memory Leak, ThreadLocal, Heap Dump, Java Flight Recorder, HashMap, Treeification, Virtual Threads, Leyden AOT, Helidon SE, Thread Pinning, Carrier Thread, CallerRunsPolicy |
| 20 | [`databases.md`](databases.md) | Databases & Database Engines | effective_io_concurrency, io_method, io_uring, pg_aios, shared_buffers, B-Tree, Bloom Filter, LSM-Tree, Write-Ahead Log (WAL), Merkle Tree, Anti-Entropy, NoSQL, Apache Cassandra, MongoDB, Masterless Architecture, Durability, Snowflake ID, Composite Shard Key, Cursor Pagination, Partial Index, Connection Pooling, LSN, WALSender, Buffer Pool, UUIDv4/v7, ULID, TSID, Skip List, Ticket Server, Inverted Index, KSUID, Trie (Prefix Tree), SimHash, Non-Blocking Incremental Snapshot, CDC Tombstone, LSN Lag, Monotonic Timestamp Guard |
| 21 | [`security-iam.md`](security-iam.md) | Security, Identity & Access Management | Authentication, Authorization, JWT, OAuth2, Zero Trust, RBAC, ABAC, Least Privilege, Argon2, Salt and Pepper, Replay Attack, TOTP |
| 22 | [`data-architecture.md`](data-architecture.md) | Data Architecture & Distributed Systems | CAP Theorem, Vertical vs Horizontal Scaling, Replication, Sharding, Data Catalog, Polyglot Persistence, Data Fabric, Data Mesh, Data Product, Federated Governance, Practical Decentralization, Medallion Architecture, Semantic Layer, Preemption, Fair Sharing, Tenant Hierarchy |
| 23 | [`geospatial.md`](geospatial.md) | Geospatial & Spatial Indexing | Spatial Index, Geohashing, Quadtree, Google S2, Uber H3, Hilbert Curve, R-Tree, K-D Tree, Map Tile Pyramid, Vector Tiles, Geocoding, Reverse Geocoding, Haversine Distance, Redis Geospatial |

---

## Cross-Domain Terms

Some terms span multiple domains. They are **defined once** in their primary domain and **cross-referenced** from others:

| Term | Primary Definition | Cross-Referenced In |
|:---|:---|:---|
| Compensating Transaction | [`data-concurrency.md#compensating-transaction`](data-concurrency.md#compensating-transaction) | cqrs-event-driven, fintech |
| Idempotency | [`cqrs-event-driven.md#idempotency`](cqrs-event-driven.md#idempotency) | resilience, messaging, api-design, data-concurrency, fintech |
| Idempotency State Explosion | [`cqrs-event-driven.md#idempotency-state-explosion`](cqrs-event-driven.md#idempotency-state-explosion) | resilience, data-concurrency, fintech |
| CQRS | [`cqrs-event-driven.md#cqrs`](cqrs-event-driven.md#cqrs) | fintech, data-concurrency, architecture-patterns |
| Circuit Breaker | [`resilience.md#circuit-breaker`](resilience.md#circuit-breaker) | messaging, api-design, azure-services |
| Rate Limiting | [`api-design.md#rate-limiting`](api-design.md#rate-limiting) | resilience, azure-services |
| Consistent Hashing | [`networking.md#consistent-hashing`](networking.md#consistent-hashing) | caching, messaging |
| Geohashing | [`geospatial.md#geohashing`](geospatial.md#geohashing) | architecture-patterns, caching |
| Redis Geospatial | [`geospatial.md#redis-geospatial`](geospatial.md#redis-geospatial) | caching |
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
| "What is smart routing in payment gateways?" | [`fintech.md#smart-routing`](fintech.md#smart-routing) |
| "How does RAG reduce LLM hallucination?" | [`ai-ml-llm.md#rag`](ai-ml-llm.md#rag) |
| "TAP vs EAP vs APM — which .NET async pattern?" | [`dotnet-multithreading.md#tap`](dotnet-multithreading.md#tap) |
| "What's the difference between Event Hubs and Service Bus?" | [`azure-services.md#event-hubs`](azure-services.md#event-hubs) |
| "What is a Bounded Context in DDD?" | [`architecture-patterns.md#bounded-context`](architecture-patterns.md#bounded-context) |
| "Why can't HSMs scale horizontally?" | [`hsm-cryptography.md#hsm`](hsm-cryptography.md#hsm) |
| "What's the difference between authentication and authorization?" | [`security-iam.md#authentication`](security-iam.md#authentication) |
| "When should I use JWT vs sessions?" | [`security-iam.md#jwt-json-web-token`](security-iam.md#jwt-json-web-token) |
| "What's the difference between TLS and mTLS?" | [`hsm-cryptography.md#mtls-mutual-tls`](hsm-cryptography.md#mtls-mutual-tls) |
| "What's DASH/HLS adaptive streaming?" | [`media-processing.md#dash-hls`](media-processing.md#dash-hls) |
| "What is PostgreSQL 18's io_method setting?" | [`databases.md#io-method`](databases.md#io-method) |
| "What does effective_io_concurrency control?" | [`databases.md#effective-io-concurrency`](databases.md#effective-io-concurrency) |
| "What's the difference between Geohash, Quadtree, and S2?" | [`geospatial.md#spatial-index`](geospatial.md#spatial-index) |
| "When should I use Google S2 vs Uber H3?" | [`geospatial.md#uber-h3`](geospatial.md#uber-h3) |

---

> **Convention**: Every term anchor follows `domain-file.md#lowercase-hyphenated-term`. Always link to the primary definition, never to a cross-reference.
