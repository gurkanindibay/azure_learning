---
type: Reference
title: "Architecture & Design Patterns"
description: "**Domain-Driven Design** — a software design approach centered on domain modeling. The team builds a shared model of the business domain using a precise, agreed-upon language."
timestamp: 2026-06-14T00:00:00Z
---

# Architecture & Design Patterns

> **Domain**: Software architecture patterns, domain-driven design, cloud adoption frameworks, and migration strategies.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Domain-Driven Design (DDD) | [`#ddd`](#ddd) |
| Bounded Context | [`#bounded-context`](#bounded-context) |
| Ubiquitous Language | [`#ubiquitous-language`](#ubiquitous-language) |
| Database Per Service | [`#database-per-service`](#database-per-service) |
| Strangler Fig Pattern | [`#strangler-fig`](#strangler-fig) |
| Anti-Corruption Layer | [`#anti-corruption-layer`](#anti-corruption-layer) |
| Sidecar Pattern | [`#sidecar-pattern`](#sidecar-pattern) |
| Ambassador Pattern | [`#ambassador-pattern`](#ambassador-pattern) |
| Competing Consumers | [`#competing-consumers`](#competing-consumers) |
| Claim Check Pattern | [`#claim-check`](#claim-check) |
| Blue-Green Deployment | [`#blue-green`](#blue-green) |
| Canary Deployment | [`#canary-deployment`](#canary-deployment) |
| Atomic Deduplication | [`#atomic-deduplication`](#atomic-deduplication) |
| Deduplication Store | [`#deduplication-store`](#deduplication-store) |
| Blue-Green vs Canary Deployment | [`#blue-green-vs-canary-deployment`](#blue-green-vs-canary-deployment) |
| Well-Architected Framework | [`#well-architected-framework`](#well-architected-framework) |
| Cloud Adoption Framework (CAF) | [`#caf`](#caf) |
| Hub-and-Spoke Topology | [`#hub-and-spoke`](#hub-and-spoke) |
| DMZ | [`#dmz`](#dmz) |
| Virtual Threads (Project Loom) | [`#virtual-threads`](#virtual-threads) |
| Leyden AOT | [`#leyden-aot`](#leyden-aot) |
| Medallion Architecture | [`#medallion-architecture`](#medallion-architecture) |
| Helidon SE | [`#helidon-se`](#helidon-se) |
| GOMAXPROCS | [`#gomaxprocs`](#gomaxprocs) |
| Goroutine | [`#goroutine`](#goroutine) |
| M:N Scheduling | [`#mn-scheduling`](#mn-scheduling) |
| Thread Pinning | [`#thread-pinning`](#thread-pinning) |
| Carrier Thread | [`#carrier-thread`](#carrier-thread) |
| Tokio | [`#tokio`](#tokio) |
| Semantic Layer | [`#semantic-layer`](#semantic-layer) |
| Vertical vs Horizontal Scaling | [`#vertical-vs-horizontal-scaling`](#vertical-vs-horizontal-scaling) |
| CAP Theorem | [`#cap-theorem`](#cap-theorem) |
| Replication | [`#replication`](#replication) |
| Sharding | [`#sharding`](#sharding) |
| Data Catalog | [`#data-catalog`](#data-catalog) |
| Polyglot Persistence | [`#polyglot-persistence`](#polyglot-persistence) |
| Data Fabric | [`#data-fabric`](#data-fabric) |
| Data Mesh | [`#data-mesh`](#data-mesh) |
| Data Product | [`#data-product`](#data-product) |
| Federated Governance | [`#federated-governance`](#federated-governance) |
| Practical Decentralization | [`#practical-decentralization`](#practical-decentralization) |
| Event Loop | [`#event-loop`](#event-loop) |
| Virtual File System (VFS) | [`#virtual-file-system-vfs`](#virtual-file-system-vfs) |
| Authentication | [`#authentication`](#authentication) |
| Authorization | [`#authorization`](#authorization) |
| JWT (JSON Web Token) | [`#jwt-json-web-token`](#jwt-json-web-token) |
| OAuth2 | [`#oauth2`](#oauth2) |
| Zero Trust | [`#zero-trust`](#zero-trust) |
| RBAC (Role-Based Access Control) | [`#rbac-role-based-access-control`](#rbac-role-based-access-control) |
| ABAC (Attribute-Based Access Control) | [`#abac-attribute-based-access-control`](#abac-attribute-based-access-control) |
| API Gateway | [`#api-gateway`](#api-gateway) |
| Microservices | [`#microservices`](#microservices) |
| Monolith | [`#monolith`](#monolith) |
| Distributed Monolith | [`#distributed-monolith`](#distributed-monolith) |
| Deployment Coupling | [`#deployment-coupling`](#deployment-coupling) |
| Native Extension | [`#native-extension`](#native-extension) |
| Progressive Delivery | [`#progressive-delivery`](#progressive-delivery) |
| Feature Flag | [`#feature-flag`](#feature-flag) |
| A/B Testing | [`#ab-testing`](#ab-testing) |
| Active-Active | [`#active-active`](#active-active) |
| Shadow Testing | [`#shadow-testing`](#shadow-testing) |
| OpenTelemetry | [`#opentelemetry`](#opentelemetry) |
| Golden Signals | [`#golden-signals`](#golden-signals) |
| Error Budget | [`#error-budget`](#error-budget) |
| Blameless Postmortem | [`#blameless-postmortem`](#blameless-postmortem) |
| Technical Debt | [`#technical-debt`](#technical-debt) |
| Upstream System | [`#upstream-system`](#upstream-system) |
| Downstream System | [`#downstream-system`](#downstream-system) |
| Singleton | [`#singleton`](#singleton) |
| Factory Method | [`#factory-method`](#factory-method) |
| Builder (Pattern) | [`#builder-pattern`](#builder-pattern) |
| Adapter (Pattern) | [`#adapter-pattern`](#adapter-pattern) |
| Decorator (Pattern) | [`#decorator-pattern`](#decorator-pattern) |
| Proxy (Pattern) | [`#proxy-pattern`](#proxy-pattern) |
| Strategy (Pattern) | [`#strategy-pattern`](#strategy-pattern) |
| Observer (Pattern) | [`#observer-pattern`](#observer-pattern) |
| Command (Pattern) | [`#command-pattern`](#command-pattern) |
| Repository (Pattern) | [`#repository-pattern`](#repository-pattern) |
| Golden Hammer | [`#golden-hammer`](#golden-hammer) |
| YAGNI | [`#yagni`](#yagni) |
| Circular Dependency | [`#circular-dependency`](#circular-dependency) |
| Configuration Propagation | [`#configuration-propagation`](#configuration-propagation) |
| Least Privilege | [`#least-privilege`](#least-privilege) |
| Separation of Concerns | [`#separation-of-concerns`](#separation-of-concerns) |
| Fail Fast | [`#fail-fast`](#fail-fast) |
| Single Source of Truth | [`#single-source-of-truth`](#single-source-of-truth) |
| Loose Coupling | [`#loose-coupling`](#loose-coupling) |
| Immutability | [`#immutability`](#immutability) |
| Scalability | [`#scalability`](#scalability) |
| Architecture Decision Record | [`#architecture-decision-record`](#architecture-decision-record) |
| Anti-pattern | [`#anti-pattern`](#anti-pattern) |
| Base62 Encoding | [`#base62-encoding`](#base62-encoding) |
| URL Shortener | [`#url-shortener`](#url-shortener) |
| Snowflake ID | [`#snowflake-id`](#snowflake-id) |
| Key Generation Service | [`#key-generation-service`](#key-generation-service) |
| Fanout on Write | [`#fanout-on-write`](#fanout-on-write) |
| Fanout on Read | [`#fanout-on-read`](#fanout-on-read) |
| Hybrid Fanout | [`#hybrid-fanout`](#hybrid-fanout) |
| Hotlinking | [`#hotlinking`](#hotlinking) |
| Presence Service | [`#presence-service`](#presence-service) |
| Faceted Search | [`#faceted-search`](#faceted-search) |
| Defensive Programming | [`#defensive-programming`](#defensive-programming) |
| Input Validation | [`#input-validation`](#input-validation) |
| Parameterized Query | [`#parameterized-query`](#parameterized-query) |
| Real User Monitoring (RUM) | [`#real-user-monitoring-rum`](#real-user-monitoring-rum) |
| Zero-Copy Transfer | [`#zero-copy-transfer`](#zero-copy-transfer) |
| Distributed Commit Log | [`#distributed-commit-log`](#distributed-commit-log) |
| Message Batching | [`#message-batching`](#message-batching) |
| Preemption | [`#preemption`](#preemption) |
| Fair Sharing | [`#fair-sharing`](#fair-sharing) |
| Tenant Hierarchy | [`#tenant-hierarchy`](#tenant-hierarchy) |

---

## DDD

**Domain-Driven Design** — a software design approach centered on domain modeling. The team builds a shared model of the business domain using a precise, agreed-upon language.

**Also see**: [Bounded Context](#bounded-context), [Ubiquitous Language](#ubiquitous-language)

---

## Bounded Context

An **explicit boundary** around a domain model with its own ubiquitous language. Inside the boundary, terms have precise meanings. "Account" in Banking may differ from "Account" in CRM — bounded contexts resolve this.

**Also see**: [DDD](#ddd), [Ubiquitous Language](#ubiquitous-language)

---

## Ubiquitous Language

A **shared, precise terminology** between developers and domain experts within a bounded context. The same word means the same thing to everyone — no translation gaps.

**Also see**: [DDD](#ddd), [Bounded Context](#bounded-context) · [Fintech: Financial States](fintech.md#financial-states)

---

## Database Per Service

A **microservices data pattern** where each service owns and manages its own database. No two services share the same logical data store, enforcing service boundaries and independent deployability.

### Key Characteristics
- **Private schema per service** — other services access data only through the service's API or events
- **Technology fit** — each service can choose SQL, NoSQL, or a specialized store based on its access patterns
- **No shared locks or joins** — cross-service consistency is achieved via APIs, sagas, or events
- **Independent scaling and recovery** — one service's database load does not starve another

### When to Use
- Microservices where teams need autonomous deployment and schema evolution
- Domains with heterogeneous data access patterns (e.g., ACID balances + high-write event logs)

### When NOT to Use
- Early-stage monoliths where cross-table joins and transactions dramatically simplify correctness
- When the organization lacks mature API/event contracts and saga compensation design

### Also see
- [Bounded Context](#bounded-context) · [Saga Pattern](data-concurrency.md#saga-pattern) · [Outbox Pattern](cqrs-event-driven.md#outbox-pattern)

---

## Strangler Fig

An **incremental migration pattern** — gradually replace a legacy system by building new functionality around it until the old system is "strangled" and can be removed. Named after the fig tree that grows around a host tree.

**Also see**: [Anti-Corruption Layer](#anti-corruption-layer)

---

## Anti-Corruption Layer

A **translation layer** that protects a bounded context from external model corruption. Translates between the external model and the internal domain model so neither leaks into the other.

**Also see**: [Bounded Context](#bounded-context), [Strangler Fig](#strangler-fig)

---

## Sidecar Pattern

A **co-located helper container** that supports the main application. Deployed alongside in the same pod (Kubernetes). Example: Envoy proxy handling TLS, routing, and observability for the app container.

**Also see**: [Ambassador Pattern](#ambassador-pattern)

---

## Ambassador Pattern

A **proxy service** that handles connectivity concerns (retry, routing, authentication) on behalf of the main service. Offloads cross-cutting network concerns from the application.

**Also see**: [Sidecar Pattern](#sidecar-pattern)

---

## Competing Consumers

Multiple consumers **pull from a single queue** for load-balanced processing. If one consumer is slow, others pick up the slack. Core pattern for scaling message processing horizontally.

**Also see**: [Messaging](messaging.md)

---

## Claim Check

Store a **large payload in external storage** and pass only a reference (the "claim check") in the message. The reference acts like a coat-check ticket — small enough to traverse the broker, containing all the information the consumer needs to retrieve the full payload.

### Key Characteristics
- **Payload externalised**: large binaries (images, PDFs, ML artefacts) live in S3 or equivalent object storage; the Kafka message carries only `{s3_bucket, s3_key, checksum, size_bytes, content_type}`
- **Size threshold**: Kafka's default maximum message size is 1 MB; payloads > ~100 KB benefit from Claim Check; anything > 1 MB requires it
- **Orphaned object problem**: if S3 upload succeeds but the Kafka send fails, the payload is stranded with no consumer — write the orphan key to a DynamoDB tracking table and run a daily Lambda cleanup job to purge unclaimed objects
- **Lazy loading vs presigned URL**: if payload < ~50 MB, download directly in the consumer; if ≥ 50 MB, generate a time-limited S3 presigned URL and delegate streaming to downstream processors to avoid loading large bytes into consumer memory
- **Lifecycle cost**: S3 Standard (~$0.023/GB) is ~4× cheaper than MSK EBS storage (~$0.10/GB); apply lifecycle policies to transition to S3 Glacier at 30 days and delete at 90 days

### When to Use
- Any message broker with a payload size limit (Kafka 1 MB default, SQS 256 KB)
- Large user uploads: images, PDFs, videos, log files, ML training data
- When payload lifetime policies (GDPR deletion, archiving) must be managed independently of the message log

### When NOT to Use
- Payloads smaller than ~10 KB where the S3 round-trip overhead outweighs the broker savings
- Systems where strict exactly-once guarantees must span both the broker and the object store (two-phase coordination is complex)

### Also see
- [Messaging](messaging.md) · [Event Carried State Transfer](cqrs-event-driven.md#event-carried-state-transfer) · [Messaging: Compacted Topic](messaging.md#compacted-topic)

---

## Blue-Green

Two **identical environments** — Blue (current) and Green (new version). Traffic is switched from Blue to Green for zero-downtime deployments. Rollback is instant: switch back to Blue.

**Also see**: [Canary Deployment](#canary-deployment)

---

## Canary Deployment

Route a **small percentage of traffic** to the new version before full rollout. If error rates spike, the canary is killed and traffic reverts. Safer than Blue-Green for high-risk changes.

**Also see**: [Blue-Green](#blue-green)

---

## Blue-Green vs Canary Deployment

Both strategies separate **deployment** (installing the new version) from **release** (exposing it to users). The difference is how traffic moves:

| Aspect | Blue-Green | Canary Deployment |
|:---|:---|:---|
| Traffic shift | Instant 0% → 100% | Gradual 0% → small % → 100% |
| Rollback speed | Immediate (switch back) | Fast (drain canary) |
| Blast radius | All users if the new version fails | Only canary users |
| Best for | Low-risk changes, predictable rollbacks | High-risk changes, sensitive services |

They are often combined: a Blue-Green pair gives you an isolated environment to canary into before committing all traffic.

```mermaid
graph LR
    subgraph "Blue-Green"
        B[Blue v1<br/>100% traffic] -->|instant cutover| G[Green v2<br/>100% traffic]
        G -.->|rollback| B
    end

    subgraph "Canary"
        O[Old v1<br/>100%] -->|shift 10%| OC[Old 90%<br/>Canary v2 10%]
        OC -->|shift all| C[Canary v2<br/>100%]
        OC -.->|revert| O
    end

    style B fill:#0984e3,color:#ffffff
    style G fill:#27ae60,color:#ffffff
    style O fill:#0984e3,color:#ffffff
    style OC fill:#f39c12,color:#000000
    style C fill:#27ae60,color:#ffffff
```

**Diagram description**: Two deployment patterns shown side by side. Blue-Green (left) switches all traffic instantly from Blue v1 (blue) to Green v2 (green) with a dashed rollback arrow. Canary (right) gradually shifts traffic from Old v1 (blue) to a mix of Old 90% + Canary v2 10% (yellow), then to Canary v2 100% (green), with a dashed revert arrow to the old version.

---

## Well-Architected Framework

Azure's **five pillars** of architectural excellence:

| Pillar | Focus |
|:---|:---|
| **Reliability** | Recover from failures, high availability |
| **Security** | Protect data, identities, and infrastructure |
| **Cost Optimization** | Maximize value, minimize waste |
| **Operational Excellence** | Run and monitor systems in production |
| **Performance Efficiency** | Adapt to changing workload demands |

**Also see**: [CAF](#caf)

---

## CAF

**Cloud Adoption Framework** — Microsoft's structured methodology for cloud adoption: Strategy → Plan → Ready → Adopt → Govern → Manage.

**Also see**: [Well-Architected Framework](#well-architected-framework)

---

## Hub-and-Spoke

A **network topology** where a central hub VNet hosts shared services (firewall, gateway, DNS) and spoke VNets host workloads. All spoke-to-spoke traffic routes through the hub for inspection and control.

**Also see**: [Azure Services: VNet](azure-services.md#vnet)

---

## Atomic Deduplication

A pattern that prevents race conditions in idempotent message processing by using a database `INSERT` with a `UNIQUE` constraint as the deduplication check, rather than a non-atomic check-then-act sequence.

```sql
-- Atomic: only one consumer succeeds
INSERT INTO processed_events (event_id) VALUES ('EVT-8A72F1');
-- UNIQUE(event_id) constraint ensures atomicity
```

### Key Characteristics
- **Database-enforced atomicity**: The database itself (not application logic) guarantees that only one INSERT for a given Event ID succeeds
- **Eliminates check-then-act races**: No gap between "check if processed" and "mark as processed" — they are the same operation
- **Constraint violation = already processed**: Consumers treat the UNIQUE constraint error as a signal to skip processing
- **Portable across stores**: Works with any store that supports atomic conditional inserts (SQL UNIQUE, Redis `SETNX`, DynamoDB conditional put)

### When to Use
- At-least-once consumers where concurrent instances may process the same event
- High-throughput systems where lock-based deduplication would create contention
- Any consumer that must be horizontally scalable while maintaining idempotency

### When NOT to Use
- When the deduplication store does not support unique constraints or conditional writes
- When the business update and dedup record are in different transactional scopes (use Outbox Pattern instead)
- Single-instance consumers where a simple in-memory set suffices

### Also see
- [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---

## Deduplication Store

A **shared, external data store** used by idempotent consumers to track which events have already been processed. It serves as the single source of truth across all consumer instances so that duplicate deliveries are recognized and skipped regardless of which instance receives the redelivery.

### Key Characteristics
- **Shared across instances**: All consumers in a group read and write to the same store — a local in-memory cache is insufficient at scale
- **Atomic conditional inserts**: Typically backed by a database with UNIQUE constraints (relational DB, Redis `SETNX`, DynamoDB conditional put)
- **Retention-bounded**: Entries are purged after a configurable window that exceeds Kafka's maximum redelivery window
- **Per-event granularity**: Keyed by Event ID, not by message offset or partition

### When to Use
- Horizontally scaled consumer groups where duplicate events may land on any instance after a rebalance
- At-least-once messaging systems (Kafka, Event Hubs, Service Bus) where redelivery is a normal occurrence
- Payment, inventory, or order workflows where double-processing is unacceptable

### When NOT to Use
- Single-instance consumers where an in-memory `HashSet<EventId>` suffices
- Systems with true exactly-once delivery guarantees (rare in practice)
- When the deduplication store itself becomes a bottleneck (consider partitioning by Event ID)

### Also see
- [Atomic Deduplication](#atomic-deduplication) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---

## DMZ

**Demilitarized Zone** — an isolated network segment between the untrusted internet and trusted internal network. Hosts internet-facing services that should not have direct access to internal systems.

**Also see**: [Azure Services: Azure Firewall](azure-services.md#azure-firewall)

---

## Virtual Threads

**Project Loom Virtual Threads** — lightweight JVM-managed threads introduced in Java 21. Unlike platform threads (1:1 mapped to OS threads, ~1 MB stack each), virtual threads are managed by the JVM and mapped many-to-few onto platform threads (~hundreds of bytes each). When a virtual thread blocks on I/O, the JVM unmounts it and reassigns the carrier platform thread to another virtual thread.

### Key Characteristics
- Available since Java 21 (JEP 444) as a standard feature
- `Thread.ofVirtual().start(task)` or `Executors.newVirtualThreadPerTaskExecutor()`
- No pool needed — virtual threads are cheap enough to create one-per-task
- Automatic unmounting on blocking I/O (socket read/write, `Thread.sleep()`, `LockSupport.park()`)
- **Pinning risk**: `synchronized` blocks and native calls (JNI) pin the virtual thread to its carrier, blocking the OS thread

### When to Use
- High-concurrency I/O-bound services (HTTP handlers, database calls, message consumers)
- Replacing reactive/async programming models (callback hell) with synchronous-style code
- When you need goroutine-level concurrency scale in Java without rearchitecting to reactive streams

### When NOT to Use
- CPU-bound workloads (virtual threads don't add CPU parallelism — use platform threads + ForkJoinPool)
- Code with pervasive `synchronized` blocks (pinning degrades throughput)
- Pre-Java 21 runtimes (not available; use reactive or CompletableFuture)

### Also see
- [Task / async-await](dotnet-multithreading.md#task) — .NET equivalent async pattern
- [Leyden AOT](#leyden-aot) — complementary startup optimization
- [Helidon SE](#helidon-se) — framework that uses virtual threads for request handling

---

## Leyden AOT

**Project Leyden Ahead-of-Time Compilation** — a JVM feature that captures JIT-optimized native code during training runs and replays it on subsequent starts via an AOT cache. Reduces the JVM warmup penalty (interpreting bytecode, C1/C2 profiling) while retaining peak throughput.

### Key Characteristics
- Two-phase workflow: **training** (record) → **production** (replay from cache)
- JVM flags: `-XX:AOTTraining` (record), `-XX:AOTCache` (replay)
- Cache is version-specific: same JDK version, JVM flags, and classpath required
- Complementary to GraalVM Native Image (Leyden improves JVM startup; GraalVM compiles ahead-of-time to a standalone binary)
- Part of Project Leyden (JEP 483), targeting JDK 24+

### When to Use
- Serverless / containerized Java services with cold-start constraints
- Auto-scaling scenarios where new instances must reach peak throughput quickly
- Services with predictable code paths (training covers production behavior)

### When NOT to Use
- Long-running monolithic services with stable load (JIT eventually reaches similar peak)
- Frequently changing codebases (cache invalidation overhead)
- Environments where cache portability is required (cache is JDK-version-specific)

### Also see
- [Virtual Threads](#virtual-threads) — complementary concurrency optimization
- [Helidon SE](#helidon-se) — lightweight framework that benefits from AOT

---

## Helidon SE

**Helidon SE** — Oracle's lightweight, reactive Java microservices framework. Helidon SE (Standard Edition) provides a minimal web server without dependency injection, designed for small footprint and fast startup. Helidon 4 uses Java virtual threads for request handling, making blocking code efficient at high concurrency.

### Key Characteristics
- Two editions: **SE** (minimal, no DI) and **MP** (MicroProfile, full Jakarta EE)
- Helidon SE WebServer is a compact, programmatic API — no annotations, no classpath scanning
- Built-in support for virtual threads (Helidon 4+)
- ~5 MB hello-world JAR; fast startup even without AOT
- Native integration with Oracle JDK and Leyden AOT

### When to Use
- Small, high-throughput HTTP services where framework overhead matters
- When comparing Java microservice performance to Go (Helidon SE is the closest Java equivalent to Go's `net/http` in terms of framework weight)
- Greenfield services that want virtual threads without Spring Boot's dependency graph

### When NOT to Use
- Teams invested in Spring Boot ecosystem (Spring Boot 3.2+ also supports virtual threads)
- Applications requiring extensive middleware (Helidon MP is the fuller alternative)
- When you need a large ecosystem of third-party integrations (Spring has more)

### Also see
- [Virtual Threads](#virtual-threads) — the concurrency model Helidon SE uses
- [Leyden AOT](#leyden-aot) — complementary startup optimization
- [Azure App Service](azure-services.md#app-service) — deployment target

---

## GOMAXPROCS

**GOMAXPROCS** — a Go runtime environment variable that sets the maximum number of OS threads that can execute Go code simultaneously. Controls the parallelism of the Go scheduler's work-stealing across goroutines.

### Key Characteristics
- Default: `runtime.NumCPU()` (all available CPUs)
- Set via `GOMAXPROCS=N` environment variable or `runtime.GOMAXPROCS(n)` in code
- Does NOT limit goroutine count (goroutines are multiplexed onto GOMAXPROCS OS threads)
- Critical for containerized environments where the container's CPU limit is less than the host's CPU count

### When to Use
- Explicit CPU affinity in benchmarks (matching Java's `ActiveProcessorCount`)
- Containerized Go services where `runtime.NumCPU()` sees the host CPUs, not container limits
- Performance tuning: reducing GOMAXPROCS can reduce GC pressure in CPU-saturated services

### When NOT to Use
- Default is usually correct for non-containerized deployments on dedicated hardware
- Setting GOMAXPROCS > actual available CPUs provides no benefit and may increase scheduling overhead

### Also see
- [Virtual Threads](#virtual-threads) — Java's concurrency model counterpart
- [Azure Container Apps](azure-services.md#container-apps) — containerized deployment target

---

## Goroutine

**Goroutine** — Go's fundamental unit of concurrency. A goroutine is a user-space, lightweight execution context managed entirely by the Go runtime scheduler. It starts with a ~2 KB stack (compared to ~512 KB–1 MB for OS threads) and grows dynamically. When a goroutine blocks on I/O, the Go scheduler parks it and runs another goroutine on the same OS thread — no kernel context switch required.

```go
func getOrder(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    order := db.FindOrder(id) // goroutine yields here, does not block OS thread
    json.NewEncoder(w).Encode(order)
}
// 10,000 of these running costs ~20 MB total stack
// Java platform threads equivalent: ~10 GB
```

### Key Characteristics
- Initial stack ~2 KB; grows in small increments as needed (unlike fixed OS thread stacks)
- Multiplexed onto OS threads via the Go runtime's M:N scheduler (see [M:N Scheduling](#mn-scheduling))
- Channels provide goroutine-safe communication and synchronization — no `synchronized` locks, no pinning risk
- Count is not limited by OS constraints: 50,000+ goroutines is routine in production
- Managed by `GOMAXPROCS` OS-thread pool (see [GOMAXPROCS](#gomaxprocs))

### When to Use
- Any concurrent I/O operation in Go — the idiomatic model is one goroutine per task
- High-concurrency HTTP handlers, background workers, pipeline stages

### When NOT to Use
- Not applicable outside Go (Java equivalent: [Virtual Threads](#virtual-threads); .NET equivalent: async/await tasks)
- Goroutines shared across FFI/CGo boundaries require extra care — CGo calls block the OS thread

### Also see
- [GOMAXPROCS](#gomaxprocs) — controls the OS-thread pool goroutines run on
- [M:N Scheduling](#mn-scheduling) — the scheduling model behind goroutines
- [Virtual Threads](#virtual-threads) — Java's closest equivalent

---

## M:N Scheduling

**M:N Scheduling** (also: *many-to-many threading*) — a concurrency model where M user-space execution contexts (goroutines, virtual threads, fibers) are multiplexed onto N OS threads, where M >> N. The user-space scheduler decides which lightweight context runs on which OS thread, yielding cooperatively or preemptively when a context blocks.

```
M:N Model (e.g., Go goroutines)
================================
Goroutine-1  ╲
Goroutine-2   ╲
Goroutine-3    ──▶  OS Thread-1  (user-space scheduling; no syscall on yield)
Goroutine-4   ╱
Goroutine-5  ╱

vs.

1:1 Model (Java platform threads, pre-Loom)
============================================
Request-1  ──▶  OS Thread-1  (kernel scheduler; syscall on every context switch)
Request-2  ──▶  OS Thread-2
Request-3  ──▶  OS Thread-3
```

### Key Characteristics
- **Low memory footprint**: user-space contexts start at KBs vs OS thread stacks at hundreds of KBs
- **Cheap context switch**: switching between user-space contexts is a function call, not a kernel syscall
- **High multiplexing**: tens of thousands of logical tasks can share a handful of OS threads
- **Implementations**: Go goroutines (runtime scheduler), Java Virtual Threads (JVM carrier threads), Erlang processes, Kotlin coroutines

### When to Use
- I/O-bound, high-concurrency services where tasks spend most of their time waiting
- When per-task memory cost matters (microservices, serverless, embedded)

### When NOT to Use
- Pure CPU-bound workloads benefit more from N = CPU-count platform threads; extra scheduling overhead from M:N adds no value
- When the runtime does not support M:N natively (pre-Loom Java with platform threads is 1:1)

### Also see
- [Goroutine](#goroutine) — Go's implementation of M:N scheduling
- [Virtual Threads](#virtual-threads) — JVM's M:N implementation (Java 21+)
- [GOMAXPROCS](#gomaxprocs) — controls N (OS thread count) in Go's M:N model

---

## Thread Pinning

**Thread Pinning** — a failure mode in JVM Virtual Threads where a virtual thread becomes permanently bound to its carrier OS thread and **cannot be unmounted**, even when blocked on I/O. The carrier thread is held captive, defeating the purpose of virtual threads and reintroducing the platform-thread starvation problem.

Pinning occurs in two situations:
1. The virtual thread holds a `synchronized` monitor lock while blocking
2. The virtual thread executes a native method (JNI/FFI)

```java
// ❌ PINS the carrier thread — OS thread blocked until lock released
synchronized(lock) {
    result = db.query();  // IO here holds the carrier thread hostage
}

// ✅ Virtual thread parks correctly — carrier thread freed immediately
lock.lock();
try {
    result = db.query();  // virtual thread unmounted; carrier runs other VTs
} finally {
    lock.unlock();
}
```

### Key Characteristics
- Silent by default — pinning does not throw an exception or produce a log warning
- Detection: `-Djdk.tracePinnedThreads=full` JVM flag emits stack traces on pin events
- JFR event `jdk.VirtualThreadPinned` available for monitoring
- Common in legacy code using `synchronized` on database/HTTP I/O paths
- Go channels and goroutines have no equivalent pinning risk — scheduler-awareness is native

### When to Use
- Understanding thread pinning is required before enabling virtual threads in any service with existing synchronized blocks

### When NOT to Use
- (Not a pattern to use — a failure mode to detect and eliminate)

### Also see
- [Virtual Threads](#virtual-threads) — the feature thread pinning undermines
- [Carrier Thread](#carrier-thread) — the OS thread that gets pinned
- [Goroutine](#goroutine) — Go's scheduler-native alternative with no pinning concept

---

## Carrier Thread

**Carrier Thread** — in the JVM Virtual Threads model, a carrier thread is the **OS-level platform thread** that a virtual thread is currently mounted onto and executing on. The JVM scheduler mounts and unmounts virtual threads onto carrier threads as they become runnable or block.

```
Virtual Thread lifecycle on a carrier:

  [Runnable] ──mount──▶ [Running on Carrier-1] ──IO block──▶ [Parked]
       ▲                                                          │
       └──────────────────────unmount◀────────────────────────────┘
  Carrier-1 is immediately free to run another virtual thread
```

### Key Characteristics
- Carrier threads form a fixed pool (default: `ForkJoinPool`, size = CPU count)
- A virtual thread is only consuming CPU when mounted on a carrier
- Unmounting on I/O block is the core mechanism enabling high concurrency — carrier threads are never wasted waiting
- **Pinning breaks unmounting**: if the virtual thread holds a `synchronized` lock, the carrier cannot be freed (see [Thread Pinning](#thread-pinning))
- Configurable via `jdk.virtualThreadScheduler.parallelism` system property

### When to Use
- When diagnosing virtual thread performance: check carrier thread pool saturation, not virtual thread count
- Tuning: `jdk.virtualThreadScheduler.parallelism` controls the carrier pool size for CPU-heavy virtual-thread workloads

### When NOT to Use
- Carrier threads are an implementation detail of the JVM; application code should not interact with them directly

### Also see
- [Virtual Threads](#virtual-threads) — the feature carrier threads support
- [Thread Pinning](#thread-pinning) — failure mode where carrier threads get stuck
- [Goroutine](#goroutine) — Go's equivalent where OS threads are the implicit carrier pool

---

## Tokio

**Tokio** — Rust’s asynchronous runtime, providing the event loop, task scheduler, I/O driver, and timer infrastructure needed to run async Rust code in production.

### Key Characteristics
- **Work-stealing scheduler**: tasks are distributed across a pool of OS threads; idle threads steal work from busy threads.
- **Async/await**: built on Rust `async`/`await` and `Future`; the runtime polls tasks to completion.
- **Zero-cost abstractions**: async code compiles to state machines without pervasive runtime allocation.
- **Ecosystem**: `tokio::sync` (channels, locks), `tokio::time`, `tokio::net`, and `tokio::task` cover most async service needs.

### When to Use
- High-concurrency network services in Rust where many connections are handled concurrently on a small thread pool.
- CPU- and latency-sensitive services that benefit from Rust’s ownership model plus async I/O.

### When NOT to Use
- For blocking or CPU-bound work without spawning it on a dedicated thread pool (`spawn_blocking`), or it will stall the async runtime.
- As a default choice when the team has no Rust operational experience; the safety gains come with a learning curve.

### Also see
- [Virtual Threads](#virtual-threads) · [Goroutine](#goroutine) · [Event Loop](#event-loop) · [Global Interpreter Lock](../reference-dictionary/data-concurrency.md#global-interpreter-lock)

---

## Vertical vs Horizontal Scaling

Two strategies for handling increased load:
- **Vertical scaling (scale up)**: Buy a bigger machine — more CPU, RAM, disk. Simple but hits physical limits and becomes exponentially expensive. Single point of failure.
- **Horizontal scaling (scale out)**: Add more machines behind a load balancer. Scales infinitely, adds fault tolerance, but requires stateless design and data partitioning.

| | Vertical (Scale Up) | Horizontal (Scale Out) |
|:---|:---|:---|
| **Complexity** | Low | High (requires LB, stateless services) |
| **Cost curve** | Linear then exponential | Linear per node |
| **Fault tolerance** | Single point of failure | Tolerates node failures |
| **Scaling limit** | Hardware ceiling | Theoretically infinite |

### When to Use
- **Vertical**: Early-stage apps, legacy monoliths, databases with licensing per-core
- **Horizontal**: Cloud-native apps, stateless services, high-availability requirements

**Also see**: [CAP Theorem](#cap-theorem) · [Replication](#replication) · [Sharding](#sharding)

---

## CAP Theorem

In a distributed system, you can guarantee only **two of three**: **C**onsistency (all nodes see the same data), **A**vailability (every request gets a response), **P**artition Tolerance (system works despite network partitions). Since network partitions are inevitable, the real choice is CP (sacrifice availability during partition) or AP (sacrifice strong consistency during partition).

| Choice | Use Case | Example |
|:---|:---|:---|
| **CP** | Financial ledgers, inventory counts | HBase, Zookeeper, etcd |
| **AP** | Social feeds, shopping carts, search indexes | Cassandra, DynamoDB, Cosmos DB |

### Key Characteristics
- **PACELC extension**: When Partitioned, choose A or C. Else (no partition), choose Latency or Consistency
- **Tunable consistency**: Modern databases offer configurable consistency levels (e.g., Cosmos DB 5 levels, Cassandra QUORUM)
- **Not binary**: CAP is a spectrum — most systems are neither purely CP nor purely AP

**Also see**: [Replication](#replication) · [Sharding](#sharding) · [Vertical vs Horizontal Scaling](#vertical-vs-horizontal-scaling)

---

## Replication

Copying data to multiple servers so that **reads can scale horizontally** and the system survives individual server failures. Writes go to the primary; reads can go to any replica. The tradeoff is **replication lag** — replicas may return stale data for milliseconds to seconds after a write.

### Key Characteristics
- **Read scalability**: N replicas = up to N× read throughput
- **Fault tolerance**: Primary fails → promote replica
- **Replication lag**: Asynchronous replication means stale reads from replicas

### When to Use
- Read-heavy workloads where slightly stale data is acceptable
- Disaster recovery and geographic distribution

### When NOT to Use
- Write-heavy workloads (replication adds overhead, doesn't help write throughput)
- When every read must reflect the latest write (use primary reads or synchronous replication)

**Also see**: [Sharding](#sharding) · [CAP Theorem](#cap-theorem)

---

## Sharding

Splitting a database into **smaller, independent pieces (shards)** so that writes and storage scale horizontally. Each shard handles a subset of data — typically by key range or hash. Enables write scalability beyond what a single machine can handle.

### Key Characteristics
- **Write scalability**: N shards = up to N× write throughput
- **Key-based routing**: Same key → same shard → consistent data locality
- **No cross-shard joins**: Application must handle data that spans shards

### When to Use
- Write-heavy workloads exceeding single-machine capacity
- Data volumes too large for a single database

### When NOT to Use
- When cross-shard queries are frequent (complexity may outweigh benefit)
- Small datasets that fit on a single machine (premature optimization)

**Also see**: [Replication](#replication) · [Vertical vs Horizontal Scaling](#vertical-vs-horizontal-scaling) · [CAP Theorem](#cap-theorem)

---

## Data Catalog

A **centralized inventory of data assets** with searchable metadata, ownership, lineage, and schema information. A real data catalog is not a dusty Confluence page — it is a living system that helps producers and consumers discover, understand, and trust data.

### Key Characteristics
- Searchable metadata and documentation
- Ownership and stewardship assignments
- Data lineage and provenance tracking
- Integration with data quality and governance tools

### When to Use
- More than a handful of data producers or consumers
- Compliance or audit requirements demand traceability
- Teams waste time hunting for the "right" dataset or its owner

### When NOT to Use
- Very small, static datasets with one consumer
- When curation discipline is absent (becomes stale metadata graveyard)

### Also see
- [Data Mesh](#data-mesh)
- [Federated Governance](#federated-governance)

---

## Data Fabric

A **metadata-driven, automation-focused data architecture** that connects disparate data sources and tools through unified discovery, governance, and integration layers. Data Fabric is not a replacement for Data Mesh — it solves different layers, mostly automation and metadata.

### Key Characteristics
- Unified metadata layer across distributed data
- AI/ML-driven data discovery and classification
- Automated data integration and pipeline generation
- Governance and policy enforcement across silos

### When to Use
- Heterogeneous data landscape with many sources and tools
- Need for automated discovery, lineage, and policy enforcement
- Data Mesh alone leaves metadata and integration gaps

### When NOT to Use
- As a silver bullet to fix organizational ownership problems
- When the real issue is lack of data-product discipline, not integration plumbing

### Also see
- [Data Mesh](#data-mesh)
- [Practical Decentralization](#practical-decentralization)

---

## Data Mesh

A **decentralized socio-technical approach to data architecture** where domain-oriented teams own their data as products. Data Mesh shifts data ownership from central data teams to domain teams, supported by federated governance and a self-serve data platform.

### Key Characteristics
- Domain-oriented decentralized data ownership
- Data as a product (governed, versioned, documented, with SLAs)
- Self-serve data infrastructure platform
- Federated computational governance

### When to Use
- Organization has mature domain teams with stable ownership
- Central data team is a persistent bottleneck
- Domains are willing and able to treat data as a product

### When NOT to Use
- Teams rotate frequently or lack data-engineering skills
- Governance culture is weak (becomes "decentralized chaos with documentation")
- Organization expects platform purchase to substitute for operating-model change

### Also see
- [Data Product](#data-product)
- [Federated Governance](#federated-governance)
- [Practical Decentralization](#practical-decentralization)

---

## Data Product

A **curated, reusable data asset** exposed with clear semantics, quality guarantees, versioning, documentation, and ownership. A data product is not a dashboard, a random table, or a CSV that happens to be in S3.

### Key Characteristics
- Defined owner and consumers
- Explicit SLAs (freshness, quality, availability)
- Versioned schema and interface
- Documented semantics and usage contracts

### When to Use
- Data is consumed by multiple teams or systems
- Data quality and reliability directly affect decisions
- Data Mesh or decentralized ownership model is in use

### When NOT to Use
- One-off exploratory analysis
- Ad-hoc exports with no clear consumer or maintenance owner

### Also see
- [Data Mesh](#data-mesh)
- [Data Catalog](#data-catalog)

---

## Federated Governance

A **governance model** where central standards are set globally but applied locally by domain teams. It combines centralized policy definition with domain-level execution, automated enforcement, and audit-friendly evidence.

### Key Characteristics
- Central standards + domain-applied rules
- Automation-first enforcement (schema checks, quality gates, access controls)
- Audit-friendly logs and lineage
- Not 17 Notion pages no one will ever read

### When to Use
- Decentralized data ownership with compliance or audit requirements
- Need to balance standardization with domain autonomy
- Policy-as-code and automated checks are feasible

### When NOT to Use
- When central team tries to enforce everything manually
- When governance is treated as documentation theater rather than executable policy

### Also see
- [Data Mesh](#data-mesh)
- [Data Fabric](#data-fabric)

---

## Practical Decentralization

A **hybrid data-architecture approach** that keeps the benefits of decentralized domain ownership while retaining centralized platform, security, and governance guardrails. It solves most Data Mesh pain with a smaller organizational leap: domains own logic, not the whole planet.

### Key Characteristics
- Central platform team owns infrastructure, tooling, security, and cost guardrails
- Domain teams own transformations, business logic, data definitions, and data contracts
- Shared semantic layer aligns metrics across domains
- Federated governance with automation-first enforcement

### When to Use
- Organization wants decentralized data but lacks full Data Mesh maturity
- Repeated attempts at pure decentralization produced chaos
- Need a pragmatic middle ground between centralization and domain autonomy

### When NOT to Use
- As an excuse to skip governance entirely
- When the central platform team is too weak to provide reliable guardrails

### Also see
- [Data Mesh](#data-mesh)
- [Semantic Layer](#semantic-layer)
- [Federated Governance](#federated-governance)

---

## Medallion Architecture

A **data architecture pattern** that organizes data processing into three sequential stages: **Bronze** (raw, ingested data), **Silver** (cleaned, transformed data), and **Gold** (business-ready, analytics-friendly data). Originally popularized by Databricks' lakehouse architecture, it provides a simple mental model for data quality progression.

### Key Characteristics
- Three canonical layers: Bronze (raw/immutable), Silver (cleansed/enriched), Gold (aggregated/business-ready)
- Each layer adds structure and quality — Bronze is schema-on-read, Silver is validated, Gold is modeled for consumption
- Pipeline-centric by design: organizes data by processing stage, not by business domain
- Best suited for batch-oriented, centralized, stable-source environments

### When to Use
- Small to mid-scale data platforms with stable data sources
- Batch workloads dominate (daily/hourly ETL/ELT)
- Centralized data engineering team with clear ownership
- Getting started with a lakehouse architecture — it's an excellent starting point

### When NOT to Use
- As a permanent organizational model — layers should not become team boundaries
- Streaming-first or real-time workloads without adapting to Kappa architecture
- Multi-domain, multi-team platforms without adding data-product and contract layers
- As a substitute for domain-driven ownership, semantic layers, or schema contracts

### Also see
- [Data Mesh](#data-mesh)
- [Data Product](#data-product)
- [Semantic Layer](#semantic-layer)
- [Practical Decentralization](#practical-decentralization)

---

## Semantic Layer

A **shared abstraction layer** that centralizes metric definitions, dimensions, and business logic so consumers query consistent, governed semantics instead of each domain reinventing metrics.

### Key Characteristics
- Canonical metric definitions and calculations
- Reusable dimensions, filters, and aggregations
- Decouples BI tools from raw data models
- Reduces tribal knowledge and metric drift

### When to Use
- Multiple teams or tools consume the same KPIs
- Metric definitions vary by domain or dashboard
- Self-serve analytics is hampered by inconsistent semantics

### When NOT to Use
- Single-consumer analytics with simple, stable metrics
- When central team cannot keep up with domain change velocity

### Also see
- [Data Mesh](#data-mesh)
- [Data Product](#data-product)

---

> **Convention**: Every term anchor follows `domain-file.md#lowercase-hyphenated-term`. Always link to the primary definition, never to a cross-reference.

---

## Event Loop

A concurrency pattern where a single thread continuously polls for and dispatches events or I/O operations, avoiding the need for locks by processing work sequentially. Redis's `ae.c` is a canonical example: ~300 lines of C that powers millions of production systems.

### Key Characteristics

- **Single-threaded by design**: Eliminates lock contention and race conditions entirely — complexity requires justification, not the other way around
- **Event-driven polling**: Continuously checks for network I/O, timers, and signals in a main loop (`aeProcessEvents`)
- **Non-blocking I/O**: Uses mechanisms like `epoll`/`kqueue`/`select` to handle many connections without thread-per-connection overhead

### When to Use

- CPU-light, I/O-heavy workloads where request processing is fast relative to I/O wait time
- Systems where data structure access benefits from lock-free semantics (e.g., in-memory data stores)
- When operational simplicity and debuggability outweigh raw throughput on multi-core machines

### When NOT to Use

- CPU-bound workloads that cannot saturate a single core fast enough for latency requirements
- When vertical scaling limits are hit and horizontal scaling across cores is the only option
- Systems with blocking operations that cannot be offloaded to background threads or async I/O

### Also see

- [Single-Threaded Architecture](../reference-dictionary/dotnet-multithreading.md#single-threaded-architecture)
- [Async I/O patterns](../reference-dictionary/dotnet-multithreading.md)

---

## Virtual File System (VFS)

A kernel-level abstraction layer in Linux that provides a single unified interface (`struct file_operations`) for all filesystem operations, allowing hundreds of different filesystem implementations (ext4, btrfs, NFS, etc.) to coexist behind a common contract. One of the most elegant examples of clean abstraction at scale.

### Key Characteristics

- **Unified interface**: Every filesystem implements the same `file_operations` struct — `open`, `read`, `write`, `release` — regardless of underlying storage
- **Contract-enforced**: The abstraction doesn't leak; it defines a contract and enforces it, enabling Linux to grow for 30+ years without collapsing under its own weight
- **Pluggable backends**: New filesystems can be added without modifying any calling code, making the kernel extensible at the storage layer

### When to Use

- Designing systems where multiple backend implementations must be interchangeable behind a stable API
- When the data model (what is stored) should remain stable while storage strategies (how it's stored) evolve
- Architectural patterns requiring the Strategy pattern at the OS or platform layer

### When NOT to Use

- When the abstraction overhead (vtable dispatch, indirection) is unacceptable for hot-path performance
- Simple systems with only one storage backend where the abstraction cost outweighs flexibility gains
- When backend-specific features need to be exposed directly to callers (the abstraction hides them)

### Also see

- [Event Loop](#event-loop) — another example of deliberate architectural simplicity
- [Content-Addressable Storage](../reference-dictionary/ai-ml-llm.md) — Git's complementary data model

- TODO: When Virtual File System (VFS) is the wrong choice

### Also see

- TODO: Related terms

---

## Authentication

The process of **proving that a claimed identity is genuine**. Authentication answers the question "Are you really who you say you are?" using credentials such as passwords, one-time codes, biometrics, or cryptographic tokens.

### Key Characteristics

- Verifies identity claims, not permissions
- Can be knowledge-based (password), possession-based (OTP device), or inherence-based (biometric)
- Produces an authentication artifact (session cookie, token, certificate) used on subsequent requests

### When to Use

- Every system that must distinguish one user or service from another
- Before any authorization decision is made

### When NOT to Use

- Do not use authentication alone to decide what actions are permitted
- Do not confuse authentication with identity proofing or account recovery

### Also see

- [Authorization](#authorization)
- [JWT](#jwt-json-web-token)
- [OAuth2](#oauth2)

---

## Authorization

The process of **deciding what an authenticated identity is allowed to do**. Authorization evaluates permissions, roles, policies, or attributes against a requested action and resource.

### Key Characteristics

- Operates only after authentication succeeds
- Can be coarse-grained (roles) or fine-grained (attributes, policies)
- Common models include RBAC, ABAC, and ACLs

### When to Use

- Enforcing least privilege
- Multi-tenant or multi-role systems

### When NOT to Use

- Before authentication is completed
- As a substitute for input validation or encryption

### Also see

- [Authentication](#authentication)
- [RBAC](#rbac-role-based-access-control)
- [ABAC](#abac-attribute-based-access-control)

---

## JWT (JSON Web Token)

A compact, URL-safe token format used to transmit **signed claims** between parties. A JWT consists of `header.payload.signature`.

### Key Characteristics

- **Signed, not encrypted** — anyone can read the payload; the signature prevents tampering
- Self-contained: services can validate locally with the right key
- Usually short-lived via the `exp` claim
- Common Bearer token format for stateless API authentication

### When to Use

- Stateless authentication in distributed systems
- Propagating identity and scope claims across microservices

### When NOT to Use

- As a confidential data container (use JWE or server-side storage instead)
- When instant revocation is required without a blocklist or short TTL
- For long-lived server-to-server trust (prefer mTLS)

### Also see

- [OAuth2](#oauth2)
- [mTLS](hsm-cryptography.md#mtls-mutual-tls)

---

## OAuth2

An **authorization framework** that enables a third-party application to obtain limited access to a user's resources without exposing the user's credentials. OAuth2 delegates authorization to a trusted authorization server.

### Key Characteristics

- Roles: Resource Owner, Client, Authorization Server, Resource Server
- Issues access tokens (often JWT) scoped to specific resources
- **Is not an authentication protocol by itself**

### When to Use

- "Login with..." integrations
- Delegating API access on behalf of users
- Third-party client authorization

### When NOT to Use

- As a direct authentication mechanism without OpenID Connect
- When the resource owner and client are the same trusted entity

### Also see

- [JWT](#jwt-json-web-token)
- [Authentication](#authentication)

---

## Zero Trust

A security architecture principle that assumes **no user, device, or service is trustworthy by default**, even inside the network perimeter. Every request must be authenticated, authorized, and encrypted.

### Key Characteristics

- "Trust nothing, verify everything"
- Per-request, per-service authentication and authorization
- Encrypt all communication (TLS/mTLS)
- Least-privilege access

### When to Use

- Microservices and cloud-native architectures
- Regulated environments
- When lateral movement risk must be minimized

### When NOT to Use

- As an excuse to ignore usability and latency budgets
- In simple monoliths where the operational overhead outweighs the threat model

### Also see

- [mTLS](hsm-cryptography.md#mtls-mutual-tls)
- [Authentication](#authentication)

---

## RBAC (Role-Based Access Control)

An authorization model where **permissions are assigned to roles**, and users inherit permissions by being assigned to roles.

### Key Characteristics

- Simplifies permission management for groups of users
- Roles reflect job functions
- Less flexible than ABAC for dynamic or context-aware policies

### When to Use

- Organizations with stable, well-defined roles
- When permission changes follow role changes

### When NOT to Use

- When access decisions need fine-grained context (time, location, device)
- In highly dynamic environments where roles proliferate

### Also see

- [ABAC](#abac-attribute-based-access-control)
- [Authorization](#authorization)

---

## ABAC (Attribute-Based Access Control)

An authorization model where access decisions are based on **attributes of the user, resource, action, and environment**.

### Key Characteristics

- Fine-grained and context-aware
- Policies are expressed as rules over attributes
- More expressive but more complex than RBAC

### When to Use

- Dynamic authorization requirements
- Policy based on context (time, location, data sensitivity)

### When NOT to Use

- When simple role-based access is sufficient
- When policy authoring and debugging overhead is unacceptable

### Also see

- [RBAC](#rbac-role-based-access-control)
- [Authorization](#authorization)

---

## API Gateway

An infrastructure component that sits between clients and backend services, providing cross-cutting concerns such as **authentication, rate limiting, request routing, SSL termination, and protocol translation**.

### Key Characteristics

- Single entry point for external clients
- Centralizes auth validation, logging, and monitoring
- Hides internal service topology
- Often paired with load balancers and WAFs

### When to Use

- Multiple client types (mobile, web, third-party) access the same backend
- Need centralized authentication, rate limiting, or routing

### When NOT to Use

- As a single point of failure without redundancy
- For internal service-to-service communication (prefer service mesh or direct mTLS)

### Also see

- [Rate Limiting](api-design.md#rate-limiting)
- [Reverse Proxy, LB & API Gateway](../system-design-architecture/16-reverse-proxy-lb-api-gateway.md)

---

## Microservices

An architectural style that structures an application as a **collection of loosely coupled services**, each aligned to a business capability, owning its own data and deployable independently.

### Key Characteristics
- **Service boundaries**: usually aligned to bounded contexts or business capabilities
- **Independent deployability**: teams can release, scale and fail over services separately
- **Polyglot persistence**: each service may choose the data store that fits its access patterns
- **Operational overhead**: requires observability, CI/CD, service discovery and graceful degradation

### When to Use
- Large engineering organizations with multiple autonomous teams
- Domains with independently scaling or evolving subsystems

### When NOT to Use
- Early-stage products where a monolith is faster to build and iterate
- When the organization lacks the platform maturity to operate dozens of services

**Also see**: [Monolith](#monolith), [Database Per Service](#database-per-service), [Bounded Context](#bounded-context)

---

## Monolith

A single deployable unit in which all functionality, data access and business logic runs together. A well-factored monolith is often the fastest and simplest path to product-market fit.

### Key Characteristics
- **Single codebase and deployment unit**: everything ships together
- **In-process communication**: no network calls between modules
- **Simpler transactions and consistency**: ACID across the whole data model
- **Can be modular**: a “modular monolith” has clear internal boundaries without service boundaries

### When to Use
- Small teams, early-stage products and rapid iteration
- Domains where cross-module transactions and joins are frequent

### When NOT to Use
- When multiple teams are blocked by a shared deployment cadence
- When one component needs to scale independently by orders of magnitude

**Also see**: [Microservices](#microservices), [Strangler Fig](#strangler-fig)

---

## Distributed Monolith

A **microservices anti-pattern** in which a system is decomposed into separate deployable services but retains tight coupling across service boundaries — delivering the operational complexity of microservices (network overhead, independent deployments, distributed tracing) without the primary benefit: **team and deployment independence**.

### Key Characteristics
- **Shared database schemas** across service boundaries — services join across tables they do not own
- **Synchronous call chains**: Service A calls B calls C; a failure in C propagates to A
- **Coordinated deployments**: deploying one service requires deploying or approving others
- **Implicit contract coupling**: changes to shared libraries or schemas ripple across all consumers
- **Cascading failures**: a single slow downstream service saturates upstream thread pools

### Warning Signs
- You maintain a deployment order spreadsheet
- An on-call incident involves engineers from 3+ services simultaneously
- A two-line config change requires a multi-team Slack war room
- Services share a Postgres schema or an ORM model class

### When to Use
Not applicable — this is an anti-pattern to detect and remediate.

### When NOT to Use
Always avoid. Prefer bounded contexts with database-per-service and async event integration.

### Also see
- [Microservices](#microservices) · [Monolith](#monolith) · [Deployment Coupling](#deployment-coupling) · [Database Per Service](#database-per-service) · [Bounded Context](#bounded-context) · [Strangler Fig](#strangler-fig)
- [Microservices & Service Design — Key Takeaways](../system-design-architecture/48-svc-distributed-monolith-key-takeaways.md#svc-01-distributed-monolith-anti-pattern)

---

## Deployment Coupling

A condition in which deploying one service requires **coordinating the deployment of one or more other services**, eliminating independent deployability — a core benefit of microservices.

### Key Characteristics
- **Deployment order dependencies**: Service B must be deployed before Service A can start
- **Shared schema migrations**: database schema changes must be applied across service boundaries simultaneously
- **Synchronized release trains**: teams are forced to align release schedules rather than deploying on their own cadence
- **Rollback propagation**: rolling back one service breaks others that depend on the new API or schema

### When to Use
Not applicable — this is an anti-pattern.

### When NOT to Use
Always avoid in microservices architectures. Use async events, versioned API contracts, and database-per-service to eliminate deployment dependencies.

### Also see
- [Distributed Monolith](#distributed-monolith) · [Microservices](#microservices) · [Database Per Service](#database-per-service)
- [Microservices & Service Design — Key Takeaways](../system-design-architecture/48-svc-distributed-monolith-key-takeaways.md#svc-02-deployment-coupling-via-synchronous-call-chains)

---

## Native Extension

A **compiled module** (written in a language such as Rust, C, C++, or Cython) that is called from a higher-level runtime to execute a hot or CPU-bound function without rewriting the entire application.

### Key Characteristics
- **Surgical optimization**: targets a single bottleneck function or small module rather than the whole service.
- **FFI boundary**: the extension exposes a callable interface to the host runtime (e.g., Python via PyO3/Cython, Node.js via N-API, Ruby via C extensions).
- **Lower operational churn**: the existing service boundary, deployment pipeline, and team fluency stay mostly intact.

### When to Use
- A profile shows that one CPU-bound function dominates latency or cost.
- The service changes frequently and a full rewrite would impose an unacceptable velocity tax.
- The team needs most of the rewrite’s performance win with a fraction of its cost.

### When NOT to Use
- When the bottleneck is I/O, an algorithm, or a missing index — fixing the root cause is cheaper than adding a foreign build.
- When the FFI and build-tooling complexity outweighs the savings (small or rarely executed functions).

### Also see
- [Strangler Fig](#strangler-fig) · [Anti-Corruption Layer](#anti-corruption-layer) · [Tokio](#tokio) · [Microservices Runtime Performance — Python to Rust Rewrite Takeaways](../system-design-architecture/60-perf-key-takeaways.md#perf-11-native-extension-as-middle-path)

---

## Progressive Delivery

An umbrella term for **gradually exposing new code to users** using techniques such as canary releases, feature flags, blue-green deployments, A/B testing and load-balanced rollouts. It decouples deployment from release.

### Key Characteristics
- **Controlled blast radius**: new code reaches a small subset first
- **Measurable gating**: promote or rollback based on error rates, latency and business metrics
- **User segmentation**: target by region, device, customer tier or random percentage

### When to Use
- High-risk changes in large-scale services
- Products where business metrics must validate a change before full rollout

### When NOT to Use
- For trivial changes where the overhead of gating exceeds the risk
- Without automated rollback and clear success criteria

**Also see**: [Canary Deployment](#canary-deployment), [Blue-Green](#blue-green), [Feature Flag](#feature-flag), [A/B Testing](#ab-testing)

---

## Feature Flag

A software development technique that wraps functionality in a **runtime-controllable toggle**, allowing teams to enable, disable or gradually roll out features without deploying new code.

### Key Characteristics
- **Decouples deploy from release**: code can ship dark and be enabled later
- **Targeted rollout**: per user, per segment, per region or percentage-based
- **Kill switch**: problematic features can be turned off instantly

### When to Use
- Long-running features that must be merged incrementally
- High-risk changes requiring instant rollback
- A/B tests and phased rollouts

### When NOT to Use
- As a substitute for branch-based development discipline (flag debt accumulates)
- When the flag adds runtime complexity without clear value

**Also see**: [Progressive Delivery](#progressive-delivery), [A/B Testing](#ab-testing)

---

## A/B Testing

A controlled experiment where **two or more variants of a product experience are served to different user groups** to measure the impact on a business or user-experience metric.

### Key Characteristics
- **Randomized assignment**: users are bucketed to reduce selection bias
- **Hypothesis and metric**: every test has a primary success metric and stopping criteria
- **Statistical rigor**: requires sufficient sample size and significance testing

### When to Use
- Validating product changes, algorithms or UI designs with real user behavior
- Decisions where multiple options are defensible and data should break the tie

### When NOT to Use
- For changes with clear correctness or safety requirements (prefer canary metrics instead)
- When sample sizes are too small to reach statistical significance

**Also see**: [Feature Flag](#feature-flag), [Progressive Delivery](#progressive-delivery)

---

## Active-Active

A high-availability deployment pattern where **multiple data centers or regions actively serve traffic and accept writes simultaneously**, rather than one being on standby.

### Key Characteristics
- **Traffic served from multiple regions**: lower latency and better fault tolerance
- **Data synchronization**: replicas exchange writes, requiring conflict resolution
- **Complexity trade-off**: adds consistency challenges in exchange for resilience

### When to Use
- Globally distributed users requiring low-latency writes
- Mission-critical systems where a single region failure must be transparent

### When NOT to Use
- When strong consistency is more important than availability during partitions
- Without a clear conflict-resolution strategy (e.g., CRDTs, last-write-wins, custom merge)

**Also see**: [CRDT](data-concurrency.md#crdt-conflict-free-replicated-data-type), [CAP Theorem](#cap-theorem)

---

## Shadow Testing

A validation technique where production traffic is **duplicated and sent to a new version or service without affecting real users**. Responses are compared between the old and new systems to detect regressions.

### Key Characteristics
- **Non-impactful**: users see only the production response; the shadow result is discarded
- **High-fidelity workload**: tests against real traffic patterns, not synthetic loads
- **Comparison metrics**: latency, errors, response payloads and resource usage

### When to Use
- Refactoring or re-platforming systems where behavioral equivalence must be proven
- Load-testing new versions with production-scale traffic

### When NOT to Use
- When the operation has side effects (e.g., payments, writes) that cannot be isolated
- Without a safe way to capture, compare and discard shadow responses

**Also see**: [Canary Deployment](#canary-deployment), [Progressive Delivery](#progressive-delivery)

---

## OpenTelemetry

An **open observability standard and toolchain** for collecting distributed traces, metrics and logs. It provides vendor-neutral APIs, SDKs and the OpenTelemetry Collector for telemetry pipelines.

### Key Characteristics
- **Vendor-neutral**: single instrumentation emits data to many backends (Jaeger, Prometheus, cloud vendors)
- **Three pillars**: traces, metrics and logs under one semantic convention
- **Auto and manual instrumentation**: libraries, agents and explicit code annotations

### When to Use
- Microservices and serverless architectures needing distributed tracing
- Organizations wanting to avoid vendor lock-in for observability tools

### When NOT to Use
- As a replacement for thoughtful SLI/SLO design — telemetry without intent creates noise
- When the operational overhead of collectors and agents is not justified

**Also see**: [Golden Signals](#golden-signals), [Distributed Tracing](azure-services.md#distributed-tracing)

---

## Golden Signals

The four key metrics that provide a **high-level view of system health** in production: latency, traffic, errors and saturation. Popularized by Google’s SRE book.

| Signal | Question it answers |
|:---|:---|
| **Latency** | How long is it taking? |
| **Traffic** | How much demand is hitting the system? |
| **Errors** | How many requests are failing? |
| **Saturation** | How close to full capacity is the system? |

### When to Use
- Defining SLIs and dashboards for any user-facing service
- Incident triage and capacity planning

### When NOT to Use
- As the only metrics — business metrics, cost metrics and custom SLIs are also needed
- Without setting explicit SLO thresholds and alerting policies

**Also see**: [Error Budget](#error-budget), [OpenTelemetry](#opentelemetry)

---

## Error Budget

The amount of **acceptable unreliability** over a period, derived from an SLO. It frames trade-offs between velocity and stability: as long as budget remains, teams can launch freely; when it is exhausted, launches pause until reliability improves.

### Key Characteristics
- **1 - SLO = budget**: a 99.9% SLO leaves a 0.1% error budget
- **Product-level contract**: aligns engineering and product on risk tolerance
- **Policy-driven**: defines when launches are blocked and how to prioritize reliability work

### When to Use
- Services with explicit reliability targets and frequent releases
- Organizations where product wants speed and engineering wants stability guardrails

### When NOT to Use
- For systems without meaningful SLOs or measurable availability
- As a rigid blocker without executive buy-in and a path to restore budget

**Also see**: [Golden Signals](#golden-signals), [Blameless Postmortem](#blameless-postmortem)

---

## Blameless Postmortem

A retrospective practice focused on **understanding systemic causes and improving processes** rather than assigning individual blame. It is foundational to a healthy reliability culture.

### Key Characteristics
- **Psychological safety**: participants can describe mistakes without fear of punishment
- **Actionable outputs**: concrete remediation items with owners and timelines
- **Shared learning**: findings are published broadly so other teams can prevent similar incidents

### When to Use
- After every significant incident or near-miss
- When introducing chaos engineering or major architecture changes

### When NOT to Use
- As a checkbox exercise without follow-through on action items
- When leadership uses it to indirectly assign blame

**Also see**: [Error Budget](#error-budget), [Chaos Engineering](resilience.md#chaos-engineering)

---

## Technical Debt

The **accumulated cost of shortcuts or suboptimal design decisions** that make future changes slower, riskier or more expensive. Like financial debt, it can be strategic if it is tracked and paid down.

### Key Characteristics
- **Visible inventory**: a debt register with estimated impact, risk and payback plan
- **Intentional and accidental**: some debt is taken deliberately to meet a deadline; some is discovered later
- **Interest grows**: untreated debt compounds as the system evolves around it

### When to Use
- Strategic short-term trade-offs with a clear repayment plan
- Refactoring work prioritized by risk and velocity impact

### When NOT to Use
- As an excuse to skip testing, documentation or security in every sprint
- Without a plan to pay it down — unchecked debt becomes a rewrite trigger

**Also see**: [Strangler Fig](#strangler-fig), [Monolith](#monolith), [Microservices](#microservices)

---

## Upstream System

A system or component that **produces data, events or requests that flow into another system**. The upstream direction is the source side of a dependency: if system A calls or emits data that system B consumes, A is upstream of B.

### Key Characteristics
- **Caller / producer / source** in a data or control flow
- **Depends on by downstream**: changes in upstream output can break downstream consumers
- **Context-relative**: the same service can be upstream to one system and downstream to another

### When to Use
- Talking about service dependencies, data lineage, event pipelines or API call chains
- Defining ownership and SLOs (upstream availability affects downstream reliability)

### When NOT to Use
- As a synonym for “client” or “server” without explaining the direction of data flow
- In isolation without clarifying what the dependency relationship actually is

**Also see**: [Downstream System](#downstream-system), [API Gateway](#api-gateway), [Microservices](#microservices)

---

## Downstream System

A system or component that **consumes data, events or requests from another system**. The downstream direction is the consumer side of a dependency: it receives what upstream systems produce.

### Key Characteristics
- **Callee / consumer / sink** in a data or control flow
- **Affected by upstream changes**: schema changes, latency or outages upstream propagate downstream
- **Context-relative**: the same service can be downstream to one system and upstream to another

### When to Use
- Discussing consumers of events, API clients, data subscribers or pipeline outputs
- Planning backward compatibility, fan-out and error handling

### When NOT to Use
- As a synonym for “backend” or “frontend” without describing the flow direction
- When the relationship is peer-to-peer and has no clear producer/consumer direction

### Also see
- [Upstream System](#upstream-system) · [Messaging](messaging.md) · [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture)

---

## Upstream/Downstream Relationship

```mermaid
graph LR
    subgraph Upstreams
        U1[Mobile App]
        U2[Web App]
        U3[Partner API]
    end

    S[Core Platform]

    subgraph Downstreams
        D1[Email Service]
        D2[Data Warehouse]
        D3[Fraud Check]
    end

    U1 -->|requests| S
    U2 -->|requests| S
    U3 -->|requests| S
    S -->|events| D1
    S -->|events| D2
    S -->|events| D3

    style S fill:#8e44ad,color:#ffffff
    style U1 fill:#0984e3,color:#ffffff
    style U2 fill:#0984e3,color:#ffffff
    style U3 fill:#0984e3,color:#ffffff
    style D1 fill:#27ae60,color:#ffffff
    style D2 fill:#27ae60,color:#ffffff
    style D3 fill:#27ae60,color:#ffffff
```

**Diagram description**: Upstream systems (Mobile App, Web App, Partner API) send requests into a Core Platform (purple). The Core Platform then emits events to downstream systems (Email Service, Data Warehouse, Fraud Check) shown in green. Arrows follow the direction of data/control flow from upstream producers to downstream consumers.

---

## Circular Dependency

A situation where two or more components **mutually depend on each other**, directly or transitively. In distributed systems, circular dependencies are especially dangerous when they cross infrastructure boundaries — for example, an observability stack that depends on the same service-discovery layer it monitors. When the dependency fails, the monitoring goes dark, and operators lose the ability to diagnose the very failure that took it down.

### Key Characteristics
- **Direct**: A depends on B, B depends on A
- **Transitive**: A → B → C → A (harder to detect)
- **Infrastructure coupling**: the monitoring plane shares fate with the data plane it observes

### When to Use
- Never intentionally — circular dependencies are an anti-pattern. Always break them with an intermediate abstraction, event bus, or separate infrastructure plane.

### When NOT to Use
- Circular dependencies should be eliminated, not tolerated. Even "stable" circular dependencies create fragility under failure conditions.

### Also see
- [Observability](../reference-dictionary/resilience.md#observability) · [Bulkhead](../reference-dictionary/resilience.md#bulkhead) · [Sidecar Pattern](#sidecar-pattern)

---

## Configuration Propagation

The process by which a **configuration change in one location spreads across a distributed system**. Configuration propagation is one of the most underestimated risks in distributed systems: a single change in one database or config store can reach every machine in a global network within minutes, with no canary or validation step. The Cloudflare 2025 outage is a canonical example — a routine permissions change that doubled a config file size propagated globally and caused every edge machine to panic.

### Key Characteristics
- **Speed**: propagation is typically near-instantaneous, far faster than code deployments
- **Blast radius**: a single invalid config can affect every node simultaneously
- **Implicit trust**: internally-generated configs often bypass the validation applied to user input

### When to Use
- Designing config distribution pipelines — always include canary validation, size/invariant checks, and automatic rollback
- Auditing deployment safety — treat internally-generated config files as untrusted input

### When NOT to Use
- Without a rollback mechanism — the ability to revert a bad config within seconds is non-negotiable
- Without monitoring the propagation itself — alert on unexpected config size changes or propagation delays

### Also see
- [Blast Radius](../reference-dictionary/resilience.md#blast-radius) · [Canary Deployment](#canary-deployment) · [Feature Flag](#feature-flag) · [Progressive Delivery](#progressive-delivery)

---

## Singleton

A **creational pattern** that ensures a class has only one instance and provides a global access point to it. Used for shared resources — configuration managers, connection pools, cache managers — where a single source-of-truth is required.

### Key Characteristics
- Private constructor prevents external instantiation
- Static volatile field + double-checked locking for thread safety
- Lazy initialization: instance created on first access

### When to Use
- JVM-scoped shared resources: feature-flag services, config managers
- Framework-managed singletons (Spring `@Bean`, CDI) preferred over hand-rolled ones

### When NOT to Use
- When the "single instance" assumption will change (e.g., tests need separate instances)
- For objects with mutable state accessed by many threads — leads to contention and hidden coupling

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-01-shared-resource-multiple-instantiation)

---

## Factory Method

A **creational pattern** that defines an interface for creating objects but lets subclasses or a factory function decide which concrete class to instantiate. Clients are decoupled from the creation logic.

### Key Characteristics
- Static factory function or an abstract `createX()` method in a base class
- Returns an interface type, not a concrete type
- Creation logic is centralised — easy to extend via new cases

### When to Use
- Creating protocol-specific clients (HTTP/gRPC/Kafka) based on config
- Plugin architectures where the set of implementations varies at runtime
- When mocking in tests requires swapping implementations

### When NOT to Use
- For trivial, unconditional `new Foo()` calls — the indirection adds no value

### Also see
- [Builder Pattern](#builder-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-02-complex-object-creation-scattered-across-clients)

---

## Builder Pattern

A **creational pattern** that constructs complex objects step-by-step using a fluent API, separating construction from representation and enabling immutability.

### Key Characteristics
- Nested `Builder` class accumulates optional/required fields
- `build()` validates and returns the fully constructed, immutable object
- Eliminates telescoping constructors and invalid intermediate states

### When to Use
- Complex DTOs or value objects with many optional fields
- Constructing requests to external services or configuration objects
- When immutability is required and setter-based construction is unsafe

### When NOT to Use
- Simple objects with ≤2 fields — a plain constructor is clearer
- When the object is mutable by design

### Also see
- [Factory Method](#factory-method) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-03-telescoping-constructors-for-complex-objects)

---

## Adapter Pattern

A **structural pattern** that converts the interface of an existing class into the interface that clients expect. Used to integrate legacy systems or third-party SDKs without modifying them.

### Key Characteristics
- Implements the target interface; holds a reference to the adaptee
- Translates method calls from the target contract to the legacy API
- Encapsulates all integration/translation code in one place

### When to Use
- Wrapping legacy `CSVReader`, third-party SDKs, or external APIs to match internal contracts
- When a domain abstraction must remain clean and external changes should be isolated

### When NOT to Use
- When the interfaces are already compatible — adds unnecessary indirection
- When the legacy code will be replaced soon and temporary coupling is acceptable

### Also see
- [Anti-Corruption Layer](#anti-corruption-layer) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-04-integrating-incompatible-interfaces)

---

## Decorator Pattern

A **structural pattern** that adds behavior to an object dynamically by wrapping it with another object that implements the same interface. Used for cross-cutting concerns (logging, caching, metrics) without modifying the original class.

### Key Characteristics
- Decorator implements the same interface as the wrapped component
- Delegates the core operation to the inner component, adding behavior before/after
- Decorators can be composed in chains

### When to Use
- Adding logging, metrics, caching, or audit to repository or service implementations
- When subclassing would create class explosion for each combination of behaviors

### When NOT to Use
- Deep chains (>3 layers) — hard to debug; prefer an AOP framework instead
- When the added behavior is unconditional and permanent — just modify the class

### Also see
- [Proxy Pattern](#proxy-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-05-adding-cross-cutting-behaviors-without-subclassing)

---

## Proxy Pattern

A **structural pattern** that provides a surrogate for another object to control access, enable lazy initialization, or intercept calls for security/logging. The proxy and the real object share the same interface.

### Key Characteristics
- Virtual proxy: defers creation of the real object until first use
- Protection proxy: checks permissions before delegating
- Remote proxy: marshals calls to a remote object (gRPC stubs)

### When to Use
- Lazy loading of expensive resources (images, large datasets)
- Security checkpoints before delegating to a sensitive operation
- gRPC/stub proxies and remote service clients

### When NOT to Use
- When the proxy introduces unexpected latency that callers cannot anticipate
- When caching is the main goal — prefer the [Decorator Pattern](#decorator-pattern) for explicit caching wrappers

### Also see
- [Decorator Pattern](#decorator-pattern) · [Ambassador Pattern](#ambassador-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-06-controlling-access-and-lazy-initialization)

---

## Strategy Pattern

A **behavioral pattern** that defines a family of algorithms, encapsulates each as an object, and makes them interchangeable. Clients select or inject the desired strategy at construction or runtime.

### Key Characteristics
- Common interface implemented by each concrete strategy
- Strategy is injected into the context (composition over inheritance)
- Open/Closed Principle: add new strategies without modifying the client

### When to Use
- Payment routing: choose strategy based on currency, region, or dynamic rules
- Discount calculation, sorting, risk scoring where the algorithm varies by context
- When algorithm variants need independent testing

### When NOT to Use
- When only one strategy will ever exist — inline the algorithm
- When the strategy selection logic itself becomes more complex than the algorithms

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-07-swappable-algorithms-at-runtime)

---

## Observer Pattern

A **behavioral pattern** that defines a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified automatically.

### Key Characteristics
- Subject maintains a list of observers (listeners); observers register/unregister
- Decouples the event source from its handlers — the publisher knows nothing about consumers
- `CopyOnWriteArrayList` or similar thread-safe collection for concurrent listener registration

### When to Use
- Domain events within a single JVM (user registered, payment processed)
- Reactive UIs where model changes must propagate to multiple view components
- Simple pub/sub within a monolith

### When NOT to Use
- Cross-service events — use an explicit message broker (Kafka, Service Bus) for durability, ordering, and replay
- When listener ordering matters — Observer does not guarantee it
- Watch for memory leaks: always deregister listeners when the consumer is destroyed

### Also see
- [Messaging Dictionary](messaging.md) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-08-decoupling-producers-from-consumers)

---

## Command Pattern

A **behavioral pattern** that encapsulates a request as a standalone object containing all information needed to execute the action. Enables queuing, scheduling, auditing, retry, and undo.

### Key Characteristics
- Command object holds the action, its parameters, and a reference to the receiver
- Commands can be serialized, stored, and replayed
- An `execute()` method is the single invocation point

### When to Use
- Job schedulers and message-based work queues
- GUI actions with undo/redo support
- Audit logs where each state-changing action must be persisted

### When NOT to Use
- Trivial, synchronous, non-replayable operations — the object creation overhead is not justified
- When all you need is a `Runnable` lambda — avoid the formalism

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-09-encapsulating-requests-for-queuing-and-undo)

---

## Repository Pattern

An **enterprise pattern** that abstracts data access behind a domain-oriented interface. The repository maps domain objects to and from the persistence store, keeping the domain model pure and decoupled from persistence technology.

### Key Characteristics
- Interface exposes domain-specific query methods (`findByEmail`, `findActiveOrders`)
- The implementation encapsulates JPA/JDBC/NoSQL details
- Trivially mockable in unit tests — swap with an in-memory implementation

### When to Use
- Any domain where you want to swap persistence technology without touching business logic
- Domain-Driven Design contexts where the domain model must remain clean
- When unit-testing domain logic without a database

### When NOT to Use
- Anemic repositories that only mirror CRUD add indirection with no benefit — use the ORM directly
- Leaky abstractions that expose `EntityManager` or query builders negate the purpose

### Also see
- [DDD](#ddd) · [Database Per Service](#database-per-service) · [CQRS](cqrs-event-driven.md#cqrs) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-10-leaky-data-access-in-domain-logic)

---

## Golden Hammer

An **anti-pattern** where a familiar pattern or tool is applied to every problem regardless of fit. The name comes from "if all you have is a hammer, everything looks like a nail."

### Key Characteristics
- Pattern applied out of habit or comfort, not because it solves the current problem
- Results in over-engineered, hard-to-understand codebases
- Often accompanied by over-abstraction

### When to Use
- N/A — this is an anti-pattern. Recognise and avoid it.

### When NOT to Use
- Always — prefer matching the solution to the actual problem

### Also see
- [YAGNI](#yagni) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-12-choosing-the-right-pattern) · [Pragmatic System Design](../system-design-architecture/18-pragmatic-system-design-takeaways.md)

---

## YAGNI

**You Aren't Gonna Need It** — an extreme programming principle stating that a feature or abstraction should not be added until it is actually needed. Prevents speculative complexity.

### Key Characteristics
- Defer implementation until there is a concrete, current requirement
- Refactor into a pattern when the need arises, not in anticipation of it
- Pairs with KISS (Keep It Simple, Stupid) and incremental design

### When to Use
- When considering whether to add CQRS, Saga, or a complex pattern to a simple domain
- When tempted to build a "framework" for a one-time use case

### When NOT to Use
- Security and compliance requirements — do not defer security controls under YAGNI
- Public API contracts — breaking changes are expensive; design them carefully upfront

### Also see
- [Golden Hammer](#golden-hammer) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-12-choosing-the-right-pattern)

---

## Least Privilege

A security principle stating that every component, service, credential, or user should receive only the minimum permissions necessary to perform its function — nothing more.

### Key Characteristics
- Permissions are scoped to the exact actions required
- Applied at every layer: IAM roles, service accounts, method-level authorization, network ACLs
- Reduces blast radius when credentials are leaked or compromised

### When to Use
- All production systems, especially those handling sensitive data or money
- Microservices and agentic AI systems where tools can mutate state

### When NOT to Use
- As an excuse to block legitimate developer access without a just-in-time elevation path
- When the operational overhead of fine-grained permissions exceeds the risk (rare)

### Also see
- [Zero Trust](#zero-trust) · [RBAC](#rbac-role-based-access-control) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-01-least-privilege)

---

## Separation of Concerns

A design principle that assigns each module, class, or service one well-defined responsibility, keeping internal cohesion high and external coupling low.

### Key Characteristics
- Each component has a single reason to change
- Boundaries are drawn along responsibilities, not along implementation details
- Changes in one concern do not cascade into unrelated concerns

### When to Use
- When a module grows large enough that its tests, reviews, and deployments span multiple teams
- When business capabilities can be clearly distinguished

### When NOT to Use
- When over-separation creates more interfaces and deployment units than a small team can operate
- When premature abstraction hides a simple, cohesive workflow

### Also see
- [Loose Coupling](#loose-coupling) · [Bounded Context](#bounded-context) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-02-separation-of-concerns)

---

## Fail Fast

A reliability principle that detects invalid state or unexpected conditions as early as possible, at the closest boundary to where the problem originates.

### Key Characteristics
- Validates inputs and assumptions at system boundaries
- Rejects bad state before it can propagate downstream
- Surfaces failures loudly rather than swallowing exceptions

### When to Use
- At API boundaries, message consumers, and dependency calls
- In distributed systems where defect cost grows exponentially with distance from source

### When NOT to Use
- When aggressive failure prevents graceful degradation that users depend on
- When it replaces proper error handling with panic-driven code

### Also see
- [Defense in Depth](resilience.md#defense-in-depth) · [Circuit Breaker](resilience.md#circuit-breaker) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-04-fail-fast)

---

## Single Source of Truth

A data principle stating that every important fact has exactly one authoritative location. Derived stores may cache or project the fact, but they do not redefine it.

### Key Characteristics
- One system owns writes for each fact
- Read replicas, caches, search indices, and warehouses are fed from the source
- Eliminates reconciliation drift between competing authorities

### When to Use
- When multiple teams or systems need consistent views of the same entity
- In event-sourced or CDC-driven architectures

### When NOT to Use
- When the single writer becomes a contention or availability bottleneck that cannot be partitioned
- When the domain genuinely requires independent bounded contexts with their own truths

### Also see
- [CQRS](cqrs-event-driven.md#cqrs-command-query-responsibility-segregation) · [Event Sourcing](cqrs-event-driven.md#event-sourcing) · [Dual-Write Problem](cqrs-event-driven.md#dual-write-problem) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-05-single-source-of-truth)

---

## Loose Coupling

An architectural principle in which components interact through stable, well-defined contracts so that changes to one component do not force changes in others.

### Key Characteristics
- Contracts are explicit: schemas, APIs, event schemas, or protocols
- Components can be deployed, scaled, and replaced independently
- Asynchronous communication is preferred where eventual consistency is acceptable

### When to Use
- Microservices, modular monoliths, and multi-team codebases
- Any system where deployment independence is a goal

### When NOT to Use
- When a tightly-knit algorithm or transaction must remain consistent and fast
- When contract governance overhead exceeds the value of independence

### Also see
- [Separation of Concerns](#separation-of-concerns) · [API Gateway](#api-gateway) · [Message Brokers](../system-design-architecture/05-message-brokers-async.md) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-06-loose-coupling)

---

## Immutability

A design principle that avoids mutating state in place by creating new versions of data and preserving history.

### Key Characteristics
- State changes produce new values rather than modifying existing ones
- Eliminates a large class of concurrency bugs and reproducibility issues
- Enables event sourcing, audit trails, and content-addressed artifacts

### When to Use
- Distributed systems with shared state
- ML/AI pipelines where reproducibility depends on frozen datasets, models, and prompts

### When NOT to Use
- When storage cost or query patterns make append-only data impractical
- When every operation must update a single current value and history adds no value

### Also see
- [Event Sourcing](cqrs-event-driven.md#event-sourcing) · [Immutability in Java](../reference-dictionary/java-jvm.md) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-07-immutability)

---

## Scalability

The ability of a system to absorb growth in load — 10x, 100x, or more — without requiring fundamental architectural changes.

### Key Characteristics
- Horizontal scale: add more nodes rather than bigger nodes
- Stateless services, careful partitioning, and elastic resources
- Caching, asynchronous processing, and database sharding planned before they are urgently needed

### When to Use
- Products with planned growth, viral potential, or seasonal spikes
- Any architecture review that asks "what happens if this succeeds?"

### When NOT to Use
- As premature optimization for products with unproven demand
- When horizontal elasticity adds more operational complexity than the team can support

### Also see
- [Vertical vs Horizontal Scaling](#vertical-vs-horizontal-scaling) · [Caching](caching.md) · [Sharding](#sharding) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-09-scalability-by-design)

---

## Architecture Decision Record

A **lightweight document** that captures a significant architectural decision, the context in which it was made, the options considered, and the consequences of the chosen option. Often abbreviated as **ADR**.

### Key Characteristics
- One ADR per decision, kept close to the code or in a dedicated `docs/adr/` folder
- Explains not just *what* was decided but *why*, including rejected alternatives
- Provides a durable record for future maintainers and reviewers

### When to Use
- When choosing between technologies, patterns, or tradeoffs that will be hard to reverse
- When deliberately violating a standard principle, to document the rationale

### When NOT to Use
- For trivial decisions that are obvious to the whole team
- As a substitute for discussion — ADRs capture consensus, not replace it

### Also see
- [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md) · [Technical Debt](#technical-debt)

---

## Anti-pattern

A **common response to a recurring problem** that is usually ineffective and risks being highly counterproductive. Anti-patterns look like solutions but create more problems than they solve.

### Key Characteristics
- Repeatedly observed in real systems
- Often arises from deadline pressure, habit, or misunderstanding a pattern
- Naming an anti-pattern helps teams recognize and avoid it

### When to Use
- In code reviews and architecture reviews to label recurring problematic solutions
- When teaching patterns by contrasting them with what *not* to do

### When NOT to Use
- As a vague insult for any code you dislike — label only well-documented, recurring problems
- To discourage pragmatic shortcuts that are explicitly temporary and tracked

### Also see
- [Golden Hammer](#golden-hammer) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md)

---

## Base62 Encoding

A binary-to-text encoding scheme that uses 62 characters: `0-9`, `a-z`, and `A-Z`. It produces shorter strings than Base64 (which uses 64 characters including `+` and `/`) while remaining URL-safe and human-readable. Commonly used to compress large numeric IDs into short tokens.

### Key Characteristics
- **Alphabet**: 62 URL-friendly characters
- **Compactness**: `62^7 ≈ 3.5 trillion` unique 7-character codes
- **Lexicographic ambiguity**: Case-sensitive (`a` ≠ `A`)

### When to Use
- Short URL aliases, invite codes, reference numbers
- Anywhere a large numeric ID needs a compact, shareable string

### When NOT to Use
- When case insensitivity is required (use Base36)
- When cryptographic entropy is required (use random tokens or hashes)

**Also see**: [URL Shortener](#url-shortener) · [Snowflake ID](#snowflake-id)

---

## URL Shortener

A system that maps long URLs to short, unique aliases and redirects users from the alias to the original URL. The classic design problem separates a write-heavy shortening path from a read-heavy redirect path, using pre-generated IDs, cache-aside reads, and asynchronous analytics.

### Key Characteristics
- **Read-heavy**: Redirect traffic dominates writes (often 100:1)
- **Immutable mappings**: Short codes rarely change after creation
- **Global uniqueness**: No two long URLs may share the same alias
- **Low-latency redirects**: Served from cache at the edge

### When to Use
- Link sharing, tracking, branding (e.g., `short.ly/abc123`)
- Any scenario requiring compact, memorable references to long resources

### When NOT to Use
- When the original URL must be hidden from the service operator
- When deterministic, collision-free generation is impossible to guarantee

**Also see**: [Base62 Encoding](#base62-encoding) · [Key Generation Service](#key-generation-service) · [Cache-Aside Pattern](../reference-dictionary/caching.md#cache-aside-pattern)

---

## Snowflake ID

A distributed unique ID generation algorithm introduced by Twitter. Each ID is a 64-bit integer composed of a timestamp, datacenter ID, worker ID, and sequence number. IDs are roughly time-ordered and unique without coordination beyond worker registration.

### Key Characteristics
- **64-bit**: Fits in a `BIGINT` / `long`
- **Time-ordered**: High bits encode millisecond timestamp
- **Distributed**: Datacenter and worker IDs allow independent generation
- **Sequence number**: Handles up to 4096 IDs per worker per millisecond

### When to Use
- Distributed systems needing unique, sortable IDs
- Primary keys where monotonic time ordering aids indexing

### When NOT to Use
- When strict global monotonicity is required (clock drift can break ordering)
- When IDs must be unpredictable (Snowflake IDs are guessable)

**Also see**: [Key Generation Service](#key-generation-service) · [Base62 Encoding](#base62-encoding)

---

## Key Generation Service

A dedicated service responsible for producing unique identifiers or tokens at scale. In a URL shortener, it pre-allocates disjoint ranges of numeric IDs to workers, who encode them locally as short aliases. This eliminates collision checks on the write path.

### Key Characteristics
- **Range allocation**: Coordinator assigns blocks of IDs to workers
- **Local incrementing**: Workers generate IDs without network calls
- **Fault tolerance**: Lost unused ranges are acceptable at large namespace sizes

### When to Use
- Systems requiring billions of unique, short tokens
- Workloads where write latency and collision-freedom are both critical

### When NOT to Use
- When UUIDs or database sequences are sufficient
- When centralized ID assignment is acceptable and simpler

**Also see**: [Snowflake ID](#snowflake-id) · [URL Shortener](#url-shortener)

---

## Fanout on Write

A distribution model where a new event is propagated to all consumers at write time. In social media, posting a message writes the post ID into every follower's timeline cache immediately. Reads are fast because results are pre-computed.

### Key Characteristics
- **Read-optimized**: Feed loads are O(1)
- **Write amplification**: Each post generates N writes for N followers
- **Latency to readers**: Near zero (data is already present)

### When to Use
- Small-to-medium follower counts
- Read latency is the dominant SLO

### When NOT to Use
- Celebrity accounts with millions of followers (write amplification explodes)
- Systems where producers significantly outnumber consumers

**Also see**: [Fanout on Read](#fanout-on-read) · [Hybrid Fanout](#hybrid-fanout) · [Timeline Cache](../reference-dictionary/caching.md#timeline-cache)

---

## Fanout on Read

A distribution model where events are stored centrally and consumers collect relevant items at read time. In social media, a follower loads their feed by fetching recent posts from each account they follow. Writes are cheap; reads are more expensive.

### Key Characteristics
- **Write-optimized**: Each post generates O(1) writes
- **Read cost grows with followees**: Feed load is O(followees)
- **No write amplification**: Ideal for celebrity producers

### When to Use
- Highly skewed graphs where a few producers have massive audiences
- Systems where reads are infrequent relative to writes

### When NOT to Use
- Feeds with strict latency SLOs and many followees
- Uniform graphs where push would be simpler and faster

**Also see**: [Fanout on Write](#fanout-on-write) · [Hybrid Fanout](#hybrid-fanout)

---

## Hybrid Fanout

A distribution model that combines fanout-on-write for normal users and fanout-on-read for high-follower celebrities. Balances read latency against write amplification by choosing the fanout strategy per producer based on follower count.

### Key Characteristics
- **Threshold-based**: Users below a follower count are pushed; celebrities are pulled
- **Best of both worlds**: Fast reads for most users, bounded write amplification
- **Operational complexity**: Requires separate code paths and caches

### When to Use
- Social networks with highly skewed follower distributions
- Any fanout problem where neither pure push nor pure pull is affordable

### When NOT to Use
- Simple graphs where one strategy clearly dominates
- When operational complexity outweighs the fanout savings

**Also see**: [Fanout on Write](#fanout-on-write) · [Fanout on Read](#fanout-on-read) · [Celebrity Cache](../reference-dictionary/caching.md#celebrity-cache)

---

## Hotlinking

Directly embedding or linking to a resource hosted on another server without re-hosting it. The consuming site gets the benefit (image, video, file) while the hosting site pays the bandwidth and infrastructure costs.

### Key Characteristics
- **Bandwidth theft**: Origin server serves traffic for external sites
- **Common targets**: Images, videos, downloadable files
- **Prevention**: Signed URLs, referrer checks, watermarking, CDN rules

### When to Use
- Intentional sharing with explicit permission (e.g., CDN-hosted assets with hotlink protection)

### When NOT to Use
- Without permission, as it consumes the origin's resources
- For resources whose origin must remain hidden or whose URLs should not be guessable

**Also see**: [API Gateway](#api-gateway) · [CDN](../reference-dictionary/caching.md#cache-aside-pattern)

---

## Presence Service

A component that tracks which users are currently online, on which devices, and which server or gateway holds their active connection.

### Key Characteristics
- Updated by heartbeats, WebSocket pong events, or explicit connect/disconnect
- Typically uses TTL-backed storage to survive unclean disconnects
- Essential for routing real-time messages and showing online status

### When to Use
- Chat, gaming, collaboration, and live collaboration tools
- Any system that needs connection-aware routing

### When NOT to Use
- Stateless request/response APIs without long-lived connections
- When approximate presence is unacceptable

### Also see
- [Redis Streams](messaging.md#redis-streams) · [Fanout on Write](#fanout-on-write)

---

## Faceted Search

A search interface that lets users refine results by applying multiple filters (facets) such as category, brand, price range, and rating.

### Key Characteristics
- Facets are derived from the current result set and update as filters are applied
- Requires a search index that supports aggregations (e.g., Elasticsearch, Azure Cognitive Search)
- Combines full-text relevance with structured, multi-dimensional filtering

### When to Use
- E-commerce catalogs, document repositories, and media libraries
- Any large collection where users browse by multiple dimensions

### When NOT to Use
- Small datasets where simple keyword search is sufficient
- When facet-computation latency exceeds user expectations

### Also see
- [API Gateway](#api-gateway)

---

## Defensive Programming

A software development approach that **writes code with the assumption that it can fail** — proactively guarding against invalid inputs, unexpected states, and external failures rather than reacting after they occur. The goal is to reduce the surface area of bugs and security vulnerabilities before they reach production.

### Key Characteristics
- All external inputs are validated and sanitized before use
- Errors are handled explicitly; unhandled exceptions are treated as design flaws
- Invariants are expressed as executable assertions in development/test builds
- Dependencies (third-party libraries) are regularly audited for vulnerabilities
- Code is designed to degrade gracefully rather than fail catastrophically

### When to Use
- Any user-facing system where inputs originate outside the trust boundary
- Batch or pipeline systems where a single bad record should not halt the entire run
- Security-sensitive paths (authentication, payment, data storage)
- Long-lived systems where dependency drift introduces ongoing CVE risk

### When NOT to Use
- As a substitute for proper architecture — defensive coding reduces bugs but does not fix fundamentally flawed designs
- In performance-critical inner loops where every validation adds measurable overhead

### Also see
- [Fail Fast](#fail-fast) · [Defense in Depth](resilience.md#defense-in-depth) · [Input Validation](#input-validation) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md)

---

## Input Validation

The practice of **verifying that all user-supplied or externally sourced data meets expected criteria** (type, format, range, and length) before it is processed or persisted. Paired with sanitization (escaping or stripping dangerous characters), it is the primary defense against injection attacks and undefined behavior from malformed data.

### Key Characteristics
- Allow-list approach: accept only known-good patterns, reject everything else
- Applied at every system boundary (API layer, message consumer, file parser)
- Distinct from business-rule validation — security validation happens first
- Complements but does not replace parameterized queries or output encoding

### When to Use
- Every endpoint that accepts data from an external caller (HTTP, message queue, file upload)
- Before persisting to a database or passing to a downstream service
- As the first layer of a defense-in-depth stack

### When NOT to Use
- As the sole defense against injection — validation alone cannot replace parameterized queries for SQL or context-aware encoding for HTML
- On already-validated internal data flowing through trusted service boundaries

### Also see
- [Defensive Programming](#defensive-programming) · [Parameterized Query](#parameterized-query) · [Fail Fast](#fail-fast) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md#arch-12-input-validation-as-security-boundary)

---

## Parameterized Query

A database query technique where **user-supplied values are passed as separate parameters** rather than concatenated directly into the SQL string. The database engine treats parameters as data, never as executable SQL, which eliminates SQL injection at the source.

### Key Characteristics
- Parameters are typed and bound after the query structure is compiled
- Works across all major databases (PostgreSQL, MySQL, SQL Server, SQLite)
- Equivalent constructs: prepared statements, stored procedures with bound parameters, ORM-generated queries
- Does not prevent all injection vectors — stored procedure logic can still be vulnerable if it re-concatenates internally

### When to Use
- Every database query that incorporates any external input, regardless of perceived trust level
- Batch inserts and updates that loop over user-supplied records

### When NOT to Use
- Dynamic object identifiers (table names, column names) cannot be parameterized — use a strict allow-list instead
- When stored procedures reconstruct SQL internally — audit the procedure body separately

### Also see
- [Input Validation](#input-validation) · [Defensive Programming](#defensive-programming) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md#arch-12-input-validation-as-security-boundary)

---

## Real User Monitoring (RUM)

An **observability technique that captures performance and interaction data from actual user sessions** in production — as opposed to synthetic monitoring which uses scripted probes. RUM collects metrics such as page load time, first contentful paint, and user-journey completion rates from every real browser or client session.

### Key Characteristics
- Data is collected passively from real users, capturing genuine geographic and device diversity
- Surfaces user-experience degradation that synthetic tests miss (e.g., third-party script slowdowns)
- Raises data privacy considerations: session data may contain PII and requires consent and anonymization
- Common tools: Azure Application Insights (browser SDK), Datadog RUM, New Relic Browser, Google CrUX

### When to Use
- User-facing web or mobile applications where perceived performance directly affects conversion or retention
- When you need to understand how real-world network conditions, device types, and geographies affect experience
- Complementing synthetic monitoring to distinguish real degradation from probe anomalies

### When NOT to Use
- Pure API backends with no browser clients — server-side APM and distributed tracing are more appropriate
- When privacy regulations or user consent cannot be obtained for session data collection

### Also see
- [Observability](resilience.md#observability) · [Golden Signals](#golden-signals) · [OpenTelemetry](#opentelemetry)

---

## Polyglot Persistence

An architectural approach where **different services (or different read models within a single service) each use the data store best suited to their access patterns**, rather than sharing a single database technology across the system.

### Key Characteristics
- **Fit-for-purpose stores**: RDBMS for strong consistency and relational queries; document stores for flexible schema; key-value stores for low-latency single-key lookups; search engines for full-text and faceted queries
- **Service autonomy**: each service owns its data store — no shared schema, no cross-service joins
- **CQRS enabler**: the pattern is the operational foundation of CQRS read models — each query model independently selects its optimal store

### When to Use
- Command side needs ACID transactions; read side needs low-latency key lookups or full-text search
- Different teams own different services and should not be constrained by a shared schema
- Scaling requirements differ radically between services (e.g., write-heavy transactional service vs. read-heavy reporting service)

### When NOT to Use
- Small teams or early-stage products where the operational overhead of multiple stores outweighs the benefits
- When strong cross-service consistency is required (cross-store distributed transactions are expensive)

### Also see
- [CQRS](cqrs-event-driven.md#cqrs) · [Database Per Service](#database-per-service) · [Microservices](#microservices)

---

## Zero-Copy Transfer

An OS-level optimization that transfers data directly from **disk cache to the network socket** without copying it through application memory. In Kafka, the `sendfile()` system call eliminates CPU copies and context switches between kernel and user space, dramatically reducing CPU usage during high-throughput data serving.

### Key Characteristics
- Data path: disk → page cache → network socket (no application buffer involved)
- Eliminates redundant CPU copies and kernel/user context switches
- Available when data is served directly from the OS page cache (not from application-managed buffers)
- Used by Kafka for consumer fetch requests; also employed by Nginx and other high-performance servers

### When to Use
- High-throughput streaming systems where CPU is the bottleneck for data serving
- When consumers read data that is already in the OS page cache (recently produced or frequently read)

### When NOT to Use
- When messages require application-level transformation or encryption before sending
- When data is not in the page cache (misses still require disk reads into application memory first)

### Also see
- [Distributed Commit Log](#distributed-commit-log) · [Message Batching](#message-batching) · [Partition](messaging.md#partition)

---

## Distributed Commit Log

An **append-only, immutable, ordered log** distributed across multiple machines. Unlike a traditional message queue where the broker manages per-message delivery state, a distributed commit log only appends messages sequentially to on-disk logs. Consumers independently track their own read position (offset), removing coordination overhead from the broker. Apache Kafka is the canonical implementation.

### Key Characteristics
- **Append-only**: Messages are never mutated — only appended; enables sequential disk writes at near hardware limit
- **Consumer-managed offsets**: The broker does not track who has read what — consumers commit their own progress
- **Immutable history**: Messages persist based on retention policy (time/size), not consumption status — enables replay
- **Partitioned**: The log is sharded into partitions for horizontal scaling across brokers

### When to Use
- Event streaming and high-throughput messaging where millions of messages per second are required
- Systems that need event replay, audit trails, or long-term event history
- When producers and consumers should be fully decoupled — producers never wait for consumers

### When NOT to Use
- Task queues with per-message acknowledgment and complex routing logic (RabbitMQ is a better fit)
- Low-throughput systems where operational complexity of Kafka outweighs its benefits
- When strict global message ordering across all partitions is required

### Also see
- [Kafka vs RabbitMQ](messaging.md#kafka-vs-rabbitmq) · [Partition](messaging.md#partition) · [Zero-Copy Transfer](#zero-copy-transfer) · [Message Batching](#message-batching)

---

## Message Batching

The practice of **accumulating multiple messages into a single batch** before writing to disk or sending over the network. In Kafka, producers batch messages (controlled by `linger.ms` and `batch.size`) and consumers fetch entire batches at once. Batching converts many small I/O operations into fewer large sequential operations, dramatically improving throughput at the cost of a small increase in latency.

### Key Characteristics
- **Throughput over latency**: Optimizes for messages-per-second rather than per-message delivery time
- **Configurable delay**: `linger.ms` introduces artificial wait time to fill batches before sending
- **Often combined with compression**: Compression is applied at the batch level for better ratios than per-message compression
- **Network efficiency**: Fewer, larger TCP packets reduce per-packet overhead

### When to Use
- High-throughput streaming pipelines where a few milliseconds of additional latency is acceptable
- When network bandwidth or disk I/O is the bottleneck rather than CPU
- Batch processing systems that naturally accumulate messages before processing

### When NOT to Use
- Low-latency use cases where messages must be delivered in single-digit milliseconds
- Systems with very low message rates — batching adds unnecessary delay with no throughput gain
- When message ordering within a batch matters and batches may fail partially

### Also see
- [Zero-Copy Transfer](#zero-copy-transfer) · [Distributed Commit Log](#distributed-commit-log) · [Consumer Lag](messaging.md#consumer-lag)

---

## Preemption

In batch scheduling, **preemption** is the ability to evict a running, lower-priority workload to admit a higher-priority one or to reclaim resources for their owning tenant. Unlike queuing (which decides admission order), preemption operates on already-running jobs — it forcibly stops and requeues them.

### Key Characteristics
- **Priority-based**: Higher-priority jobs can displace lower-priority ones already consuming resources
- **Reclamation**: Idle reserved capacity lent to other tenants can be reclaimed when the owning tenant needs it
- **Graceful vs forceful**: Preempted jobs may receive a SIGTERM with a grace period or an immediate kill
- **Restartable workloads only**: Preemption is safe for batch/idempotent jobs but destructive for serving workloads

### When to Use
- Multi-tenant batch platforms where reserved capacity sits idle while other tenants starve
- Systems requiring priority-based scheduling where business-critical jobs must jump the queue
- Kubernetes-native batch scheduling via Kueue's `reclaimWithinCohort` and `withinClusterQueue` policies

### When NOT to Use
- Serving workloads (HTTP, gRPC) where eviction causes user-visible errors or data loss
- Systems without checkpointing or idempotent job design — preempted jobs lose all progress
- When preemption frequency causes thrashing (jobs repeatedly preempted before completion)

### Also see
- [Fair Sharing](#fair-sharing) · [Tenant Hierarchy](#tenant-hierarchy) · [Kueue (Kubernetes-native job queueing)](azure-services.md) · [Resilience Patterns](../reference-dictionary/resilience.md)

---

## Fair Sharing

A resource allocation strategy where **competing tenants receive a weighted share of available capacity** proportional to their configured weight. When demand exceeds supply, each tenant gets roughly `(weight / total_weight) × total_capacity`. Fair sharing prevents a single heavy tenant from starving others while allowing tenants to burst into unused capacity from others.

### Key Characteristics
- **Weighted allocation**: Tenants with higher weight get proportionally more resources under contention
- **Work-conserving**: Idle capacity from one tenant is immediately available to others — no stranded resources
- **Fairness over time**: Short-term unfairness is acceptable; the guarantee is long-term weighted proportionality
- **With preemption**: When combined with preemption, fair sharing becomes dynamic — lower-priority work can be evicted to restore fair shares

### When to Use
- Multi-tenant platforms where capacity must be divided across teams or business units
- Batch scheduling systems (Kueue, YARN, Mesos) managing heterogeneous workloads
- Cloud resource management where cost attribution and fair access are both required

### When NOT to Use
- Single-tenant systems where the concept of "fairness across tenants" is meaningless
- When strict capacity guarantees (not proportional sharing) are required — use reserved capacity instead
- Very short-term allocation where the overhead of tracking weighted usage exceeds the fairness benefit

### Also see
- [Preemption](#preemption) · [Tenant Hierarchy](#tenant-hierarchy) · [Reserved Capacity](azure-services.md)

---

## Tenant Hierarchy

A **tree-structured organizational model** for multi-tenant systems where tenants are arranged in a parent-child hierarchy. Internal (non-leaf) tenants aggregate capacity for their subtree but don't accept work directly; leaf tenants accept jobs and have associated queues. Capacity can be reserved at any level of the tree.

### Key Characteristics
- **Tree topology**: Internal tenants group and aggregate; leaf tenants execute work
- **Capacity inheritance**: Reserved capacity at an internal tenant is fair-shared across its subtree
- **Organizational mapping**: The hierarchy reflects team structure — an org can use a flat tenant or a deep tree matching ownership boundaries
- **Two capacity pools**: Reserved (partitioned, guaranteed) and Shared (global pool, burst-eligible)

### When to Use
- Large organizations with complex team structures needing hierarchical resource allocation
- Platforms where different business units need guaranteed capacity while sharing a common pool
- Batch compute platforms (Netflix CMB/Titus, Kueue Cohorts/ClusterQueues)

### When NOT to Use
- Small teams where a flat priority queue suffices
- When organizational structure is too fluid — constant hierarchy changes create operational churn
- Without preemption: hierarchical reserved capacity without preemption leaves idle resources stranded

### Also see
- [Fair Sharing](#fair-sharing) · [Preemption](#preemption) · [Cohort/ClusterQueue (Kueue concepts)](https://kueue.sigs.k8s.io/docs/concepts/)

