---
type: Reference
title: "Architecture & Cloud Patterns"
description: "**Domain-Driven Design** — a software design approach centered on domain modeling. The team builds a shared model of the business domain using a precise, agreed-upon language."
timestamp: 2026-07-04T00:00:00Z
---

# Architecture & Cloud Patterns

> **Domain**: Software architecture patterns, cloud adoption frameworks, networking topology, system design concepts, and migration strategies.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| DDD | [`#ddd`](#ddd) |
| Bounded Context | [`#bounded-context`](#bounded-context) |
| Ubiquitous Language | [`#ubiquitous-language`](#ubiquitous-language) |
| Database Per Service | [`#database-per-service`](#database-per-service) |
| Strangler Fig | [`#strangler-fig`](#strangler-fig) |
| Anti-Corruption Layer | [`#anti-corruption-layer`](#anti-corruption-layer) |
| Architecture Tests | [`#architecture-tests`](#architecture-tests) |
| Modular Monolith | [`#modular-monolith`](#modular-monolith) |
| Shared Kernel | [`#shared-kernel`](#shared-kernel) |
| Sidecar Pattern | [`#sidecar-pattern`](#sidecar-pattern) |
| Ambassador Pattern | [`#ambassador-pattern`](#ambassador-pattern) |
| Well-Architected Framework | [`#well-architected-framework`](#well-architected-framework) |
| CAF | [`#caf`](#caf) |
| Virtual File System (VFS) | [`#virtual-file-system-vfs`](#virtual-file-system-vfs) |
| Microservices | [`#microservices`](#microservices) |
| Monolith | [`#monolith`](#monolith) |
| Distributed Monolith | [`#distributed-monolith`](#distributed-monolith) |
| Deployment Coupling | [`#deployment-coupling`](#deployment-coupling) |
| Native Extension | [`#native-extension`](#native-extension) |
| Technical Debt | [`#technical-debt`](#technical-debt) |
| Upstream System | [`#upstream-system`](#upstream-system) |
| Downstream System | [`#downstream-system`](#downstream-system) |
| Upstream/Downstream Relationship | [`#upstreamdownstream-relationship`](#upstreamdownstream-relationship) |
| Circular Dependency | [`#circular-dependency`](#circular-dependency) |
| Base62 Encoding | [`#base62-encoding`](#base62-encoding) |
| URL Shortener | [`#url-shortener`](#url-shortener) |
| Key Generation Service | [`#key-generation-service`](#key-generation-service) |
| Presence Service | [`#presence-service`](#presence-service) |
| Read/Write Path Separation | [`#readwrite-path-separation`](#readwrite-path-separation) |
| Back-of-the-Envelope Estimation | [`#back-of-the-envelope-estimation`](#back-of-the-envelope-estimation) |
| Business Boundary | [`#business-boundary`](#business-boundary) |
| Coordination Cost | [`#coordination-cost`](#coordination-cost) |
| Business Capability | [`#business-capability`](#business-capability) |
| Service Decomposition | [`#service-decomposition`](#service-decomposition) |
| Service Discovery | [`#service-discovery`](#service-discovery) |
| Pod Affinity | [`#pod-affinity`](#pod-affinity) |
| Node Affinity | [`#node-affinity`](#node-affinity) |
| Topology Spread Constraints | [`#topology-spread-constraints`](#topology-spread-constraints) |
| Replay Attack | [`#replay-attack`](#replay-attack) |
| Flash Sale | [`#flash-sale`](#flash-sale) |
| Three-Layer Deduplication | [`#three-layer-deduplication`](#three-layer-deduplication) |
| Two Generals Problem | [`#two-generals-problem`](#two-generals-problem) |
| Deterministic Processing | [`#deterministic-processing`](#deterministic-processing) |

## Business Capability

A cohesive area of business responsibility that delivers a recognizable outcome and can own its rules, data, and change decisions. Business capabilities are a useful starting point for service boundaries because they describe what the organization does rather than how the code is currently layered.

### Key Characteristics
- Has a clear business outcome and vocabulary
- Can be assigned to an accountable team or domain owner
- Groups related rules and data while minimizing cross-boundary coordination

### When to Use
- Decomposing a monolith into services or bounded contexts
- Evaluating whether a proposed service boundary represents a meaningful business unit

### When NOT to Use
- As the only boundary signal; scaling, consistency, team ownership, and operational cost also matter
- For technical utilities that do not represent independent business responsibility

### Also see
- [Bounded Context](#bounded-context) · [Microservices](#microservices) · [Service Decomposition](#service-decomposition)

---

## Service Decomposition

The process of dividing a system into independently owned modules or services using boundaries such as business capabilities, bounded contexts, data ownership, and scaling needs. Good decomposition reduces coordination; splitting by technical layers usually creates a distributed monolith.

### Key Characteristics
- Starts from business responsibilities rather than controllers or implementation layers
- Assigns ownership of behavior and data to one boundary
- Measures coupling through synchronous calls, shared schemas, and coordinated releases

### When to Use
- When team ownership, independent scaling, or release coupling creates a demonstrated need for separate services
- During incremental extraction from a monolith

### When NOT to Use
- Before the domain boundaries and operational requirements are understood
- When a modular monolith can provide the needed boundaries with less operational overhead

### Also see
- [Business Capability](#business-capability) · [Bounded Context](#bounded-context) · [Distributed Monolith](#distributed-monolith)

---

## Service Discovery

A runtime mechanism for locating healthy instances of a service as instances are created, removed, or moved. Discovery replaces hardcoded endpoints with a registry, platform naming layer, or client-side lookup process.

### Key Characteristics
- Tracks service membership and health
- Resolves logical service names to reachable instances
- Requires policies for stale registrations, timeouts, and registry failure

### When to Use
- Dynamically scaled or frequently redeployed service environments
- Systems where static endpoint configuration cannot keep pace with instance changes

### When NOT to Use
- Small, static deployments where stable platform DNS or a load balancer already provides the needed resolution
- Without health checks, timeouts, and a plan for stale discovery data

### Also see
- [Service Mesh](networking.md#service-mesh) · [Load Balancer](networking.md#load-balancer) · [Microservices](#microservices)

---

## DDD

**Domain-Driven Design** — a software design approach centered on domain modeling. The team builds a shared model of the business domain using a precise, agreed-upon language.

**Also see**: [Bounded Context](#bounded-context), [Ubiquitous Language](#ubiquitous-language)

---

## Bounded Context

An **explicit boundary** around a domain model with its own ubiquitous language. Inside the boundary, terms have precise meanings. "Account" in Banking may differ from "Account" in CRM — bounded contexts resolve this.

> **Note**: A bounded context is a *design-time, semantic* boundary (what terms mean). A [Business Boundary](#business-boundary) is a *runtime, operational* boundary (where correctness is enforced). They complement each other: a Payments bounded context defines the language; the business boundary at the database enforces idempotency.

**Also see**: [DDD](#ddd), [Ubiquitous Language](#ubiquitous-language), [Business Boundary](#business-boundary)

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

## Architecture Tests

Automated tests that verify a codebase obeys its declared **architectural boundaries** — for example, that a module's Core project does not reference another module's Infrastructure project. Often implemented with reflection or dependency-analysis libraries (NetArchTest, ArchUnit, NDepend).

### Key Characteristics
- **Rule-driven**: encode constraints such as "Catalog.Core may not reference Orders.Core"
- **Fast feedback**: run in CI like unit tests and fail the build on violation
- **Living documentation**: make the intended architecture explicit and enforceable
- **Boundary preservation**: prevent the gradual erosion that turns a modular monolith into a big ball of mud

### When to Use
- Modular monoliths or layered architectures where compile-time project structure enforces boundaries
- Codebases where implicit dependencies historically caused regressions
- Teams that want architecture review to be automated and deterministic

### When NOT to Use
- Trivial prototypes where project structure overhead outweighs boundary risk
- When rules are too coarse and produce false positives that teams bypass
- As a substitute for clear domain modeling — tests cannot fix wrong boundaries

### Also see
- [Modular Monolith](#modular-monolith) · [Bounded Context](#bounded-context) · [Separation of Concerns](design-patterns.md#separation-of-concerns)

---

## Modular Monolith

A **single deployment unit** organized internally into clear, self-contained modules aligned to business capabilities or bounded contexts. Each module owns its own domain logic, data access and public contract, but the application is built and deployed as one artifact.

### Key Characteristics
- **Single deployable unit**: one build, one deployment, one runtime process
- **Strong internal boundaries**: modules communicate only through published contracts or events
- **In-process performance**: cross-module calls are method calls, avoiding network latency and serialization
- **Optional extraction path**: a well-isolated module can later be extracted into a separate service when scale or team autonomy demands it

### When to Use
- New products where domain boundaries are still emerging
- Teams without the platform maturity to operate many services
- Workloads where cross-module transactions and joins are common
- Scenarios that need the simplicity of a monolith with the maintainability of clean boundaries

### When NOT to Use
- When independent scaling, deployment or technology choice for a module is already a hard requirement
- Large organizations where multiple autonomous teams are blocked by a shared deployment cadence
- When a single component must scale by orders of magnitude independently

### Also see
- [Monolith](#monolith) · [Microservices](#microservices) · [Bounded Context](#bounded-context) · [Shared Kernel](#shared-kernel) · [Architecture Tests](#architecture-tests)

---

## Shared Kernel

A small, stable subset of the domain model that is **intentionally shared across bounded contexts** because duplicating it would be more costly than coordinating changes. Contains cross-cutting infrastructure, common data types and base classes — but never business logic that belongs inside a specific module.

### Key Characteristics
- **Minimal surface area**: only truly common concepts live in the shared kernel
- **Stable and carefully governed**: changes affect every consumer, so they require coordination
- **No domain logic**: business rules stay inside their owning bounded contexts
- **Infrastructure-friendly**: authentication, logging, base entity types and common DTO primitives are typical residents

### When to Use
- Multiple bounded contexts need the same fundamental concepts (e.g., money, identifiers, base entity behavior)
- Cross-cutting infrastructure concerns are genuinely reused and stable
- The cost of coordination is lower than the cost of duplication and drift

### When NOT to Use
- As a dumping ground for code that does not clearly belong anywhere
- To share business logic that should live inside one bounded context
- When teams cannot agree on ownership and change governance

### Also see
- [Bounded Context](#bounded-context) · [DDD](#ddd) · [Ubiquitous Language](#ubiquitous-language) · [Modular Monolith](#modular-monolith)

---

## Sidecar Pattern

A **co-located helper container** that supports the main application. Deployed alongside in the same pod (Kubernetes). Example: Envoy proxy handling TLS, routing, and observability for the app container.

**Also see**: [Ambassador Pattern](#ambassador-pattern)

---

## Ambassador Pattern

A **proxy service** that handles connectivity concerns (retry, routing, authentication) on behalf of the main service. Offloads cross-cutting network concerns from the application.

**Also see**: [Sidecar Pattern](#sidecar-pattern)

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

- [Event Loop](concurrency-runtimes.md#event-loop) — another example of deliberate architectural simplicity
- [Content-Addressable Storage](ai-ml-llm.md) — Git's complementary data model

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

**Also see**: [Microservices](#microservices), [Modular Monolith](#modular-monolith), [Strangler Fig](#strangler-fig)

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
- [Strangler Fig](#strangler-fig) · [Anti-Corruption Layer](#anti-corruption-layer) · [Tokio](concurrency-runtimes.md#tokio) · [Microservices Runtime Performance — Python to Rust Rewrite Takeaways](../system-design-architecture/60-perf-key-takeaways.md#perf-11-native-extension-as-middle-path)

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
- [Observability](../reference-dictionary/observability.md#observability) · [Bulkhead](../reference-dictionary/resilience.md#bulkhead) · [Sidecar Pattern](#sidecar-pattern)

---

## Geohashing

A **geospatial indexing technique** that encodes a latitude/longitude coordinate pair into a short alphanumeric string (geohash). Nearby locations share a common geohash prefix — the longer the shared prefix, the closer the points. Used for proximity searches, ride-matching, and location-based sharding.

### Key Characteristics
- **Hierarchical**: truncating a geohash gives a larger bounding box (less precision, wider area)
- **Prefix-based proximity**: points with the same prefix are spatially close (with edge-case exceptions at cell boundaries)
- **1D index for 2D space**: enables standard database indexes (B-tree) for spatial queries

### When to Use
- Proximity queries: "find all drivers within 2 km of this rider" (Uber)
- Location-based sharding: partition data by geohash prefix so nearby entities land on the same shard
- When a full spatial database (PostGIS) is overkill and approximate proximity is acceptable

### When NOT to Use
- When exact distance calculations are required — geohash is an approximation; use Haversine or PostGIS
- For point-in-polygon queries (geofencing) — use a spatial library with proper polygon support

### Also see
- [Quadtree](#quadtree) · [Sharding Key Selection](../system-design-architecture/15-interview-roadmap.md#sdi-11-sharding-key-selection)

---

## Quadtree

A **tree data structure** where each internal node has exactly four children, recursively subdividing a 2D space into quadrants. Used for spatial indexing, collision detection, and image compression. In system design, quadtrees enable efficient "find all points within a radius" queries without scanning the entire dataset.

### Key Characteristics
- **Recursive subdivision**: each node represents a rectangular region; split into 4 quadrants when capacity is exceeded
- **Sparse storage**: dense areas get deeper trees; empty areas stay shallow
- **O(log N) spatial queries**: prunes irrelevant branches early

### When to Use
- Ride-matching: find nearby drivers (Uber)
- Map rendering: determine which map tiles to load at a given zoom level (Google Maps)
- Collision detection in games and simulations

### When NOT to Use
- When the dataset is small enough for brute-force distance calculations
- When the data is uniformly distributed — a grid-based spatial index may be simpler
- When updates are frequent and the tree must be rebalanced — consider geohashing instead

### Also see
- [Geohashing](#geohashing) · [Sharding Key Selection](../system-design-architecture/15-interview-roadmap.md#sdi-11-sharding-key-selection)

---

## Selective Forwarding Unit (SFU)

A **WebRTC media server architecture** where each participant sends their media stream to a central server, which selectively forwards it to other participants — without decoding or mixing. Unlike MCU (Multipoint Control Unit), the SFU does not transcode; it routes packets. This is the architecture behind Discord (2.5M+ concurrent voice users) and many modern video conferencing systems.

### Key Characteristics
- **Packet routing, not mixing**: the SFU forwards encoded packets; it does not decode or re-encode media
- **Per-receiver bitrate adaptation**: sends different quality levels (simulcast) to participants based on their available bandwidth
- **Lower CPU cost than MCU**: no transcoding means the server can handle many more concurrent streams
- **End-to-end encryption compatible**: the SFU can forward encrypted packets it cannot read (E2EE with insertable streams)

### When to Use
- Group video/voice calls with >3 participants where peer-to-peer mesh would overwhelm each client's uplink
- When different participants have heterogeneous bandwidth (mobile vs. desktop)
- When end-to-end encryption is required and the server should not access raw media

### When NOT to Use
- For 1:1 calls — peer-to-peer WebRTC is simpler and avoids server cost
- When all participants must receive identical media (e.g., live streaming to viewers) — use CDN/HLS instead
- When legacy interop (PSTN/SIP) is required — MCU may be needed for transcoding

### Also see
- [Adaptive Bitrate Streaming](media-processing.md#adaptive-bitrate-streaming-abr) · [DASH / HLS](media-processing.md#dash-hls)

---

## Inverted Index

A **search data structure** that maps each term (word, token) to the list of documents containing it. This is the foundational data structure behind full-text search engines (Google Search, Elasticsearch, Lucene). Instead of scanning every document for a query term, the inverted index provides O(1) lookup of the term followed by intersection/union of result lists.

### Key Characteristics
- **Term → Document mapping**: the inverse of a forward index (document → terms)
- **Postings list**: each term maps to a sorted list of document IDs (and optionally positions, term frequency)
- **Boolean query support**: AND/OR/NOT queries are implemented as set operations on postings lists
- **Skip lists**: accelerate intersection by skipping over non-matching document IDs

### When to Use
- Full-text search over large document collections
- Log search and observability (Elasticsearch, Splunk)
- Any system where users need keyword-based retrieval from unstructured text

### When NOT to Use
- For exact-match lookups — a hash index or B-tree is simpler and faster
- For relational queries with joins and aggregations — use a SQL database
- When the corpus is small enough for brute-force scan

### Also see
- [MapReduce](data-architecture.md#mapreduce) · [Database Index Types](databases.md)

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

**Also see**: [URL Shortener](#url-shortener) · [Database ID Generation Strategies](../system-design-architecture/databases/database-id-strategy.md)

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

**Also see**: [Base62 Encoding](#base62-encoding) · [Key Generation Service](#key-generation-service) · [Cache-Aside Pattern](../reference-dictionary/caching.md#cache-aside-pattern) · [Database ID Generation Strategies](../system-design-architecture/databases/database-id-strategy.md)

---

## KSUID

A K-Sortable Unique Identifier. A 20-byte identifier composed of a 4-byte timestamp (seconds since the KSUID epoch) and a 16-byte random payload. KSUIDs are time-sortable, require no worker coordination, and offer higher entropy than ULID.

### Key Characteristics
- **20 bytes**: Larger than UUIDs and Snowflake IDs
- **Time-ordered**: First 4 bytes encode seconds since 2014-05-13
- **No coordination**: Any node can generate KSUIDs independently
- **High entropy**: 128 random bits per ID

### When to Use
- Distributed systems needing sortable IDs without worker ID assignment
- Event streams and distributed logs where higher entropy reduces guessability

### When NOT to Use
- When storage size is constrained (20 bytes per key)
- When millisecond-level ordering is required

**Also see**: [Base62 Encoding](#base62-encoding) · [URL Shortener](#url-shortener) · [Database ID Generation Strategies](../system-design-architecture/databases/database-id-strategy.md)

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

**Also see**: [URL Shortener](#url-shortener) · [Database ID Generation Strategies](../system-design-architecture/databases/database-id-strategy.md)

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

## Read/Write Path Separation

**Read/Write Path Separation** is an architectural pattern where the systems handling write operations are physically or logically separated from those handling read operations. Each path is optimized for fundamentally different concerns: the write path prioritizes durability, consistency, and correctness; the read path prioritizes low latency, massive throughput, and responsiveness.

### Key Characteristics
- **Write path** focuses on: durability, consistency, ordering, data correctness, transactional integrity
- **Read path** focuses on: low latency, massive throughput, fast responses, eventual consistency
- **Asymmetric scaling**: Read replicas can scale horizontally independently of the write master
- **CQRS is the formalized version**: Command Query Responsibility Segregation explicitly separates command (write) models from query (read) models

### When to Use
- Read-heavy workloads where reads outnumber writes by 100:1 or more (e.g., election results, news feeds, leaderboards)
- Systems where write consistency requirements conflict with read performance requirements
- National-scale events where millions of concurrent reads would overwhelm a single database

### When NOT to Use
- Write-heavy OLTP systems where read volume is low and read-your-writes consistency is critical
- Simple CRUD applications where the added complexity of separate paths exceeds the benefit
- Early-stage products where the read/write ratio is unknown or unvalidated

### Also see
- [CQRS](cqrs-event-driven.md#cqrs) · [Read Model](cqrs-event-driven.md#read-model) · [Caching](caching.md) · [Database Per Service](#database-per-service)

---

## Back-of-the-Envelope Estimation

A **rough, order-of-magnitude calculation** performed before designing any architecture. Uses simplified math to estimate traffic (QPS), storage, bandwidth, and memory requirements — typically converting DAU into reads/sec using the approximation `daily total / 86,400 ≈ average QPS`, then multiplying by a peak factor (3–5×) for worst-case planning.

### Key Characteristics
- **Order-of-magnitude precision**: The goal is within 2× of reality, not exact numbers — this is sufficient for architectural decisions
- **Peak multiplier**: Average QPS × (3–5) for peak load; 80/20 rule for cache coverage estimation
- **Guides component selection**: Tells you whether a single database, cache, queue, or CDN is plausible
- **Prevents over-engineering**: If a single PostgreSQL instance can handle the load, don't propose sharding

### When to Use
- System design interviews: BEFORE drawing any architecture diagram
- Early-stage capacity planning: do you need 1 server or 100?
- Reality-checking architectural proposals: "We need multi-region active-active for 1K DAU" — the math says no

### When NOT to Use
- As a substitute for load testing with real traffic patterns
- When exact numbers are available from production monitoring (use real data)
- For latency guarantees (estimation covers throughput and storage, not p99 latency)

### Also see
- [Scalability Principles](#) · [Read/Write Path Separation](#read-write-path-separation) · [Latency vs Throughput](#)
- [System Design Interview Roadmap](../system-design-architecture/system-design-interview/interview-roadmap.md#sdi-05-back-of-the-envelope-math)

---

## Business Boundary

The **layer or component within a distributed system where business correctness is enforced**. In event-driven payment systems, the business boundary is the database — not the message broker. Kafka provides delivery guarantees, but idempotency, deduplication, and transaction integrity must be enforced at the database/application layer, because exactly-once semantics stop at Kafka's boundary.

> **Key insight**: "Kafka will deliver it once" is not a correctness guarantee. The question is always "What happens if it doesn't?"

### Key Characteristics
- **Separation of concerns**: Event delivery (messaging), business correctness (database), external side effects (gateway wrappers) are three independent responsibilities
- **Database as authority**: The database's unique constraints on business identifiers are the single source of truth — not the message broker's delivery guarantees
- **Offset-agnostic**: Offset management tracks progress, not correctness; idempotency must live outside the messaging layer
- **Testable**: Correctness becomes independently verifiable without depending on the message broker

### When to Use
- Payment systems and financial applications where duplicate processing is unacceptable
- Any distributed system where at-least-once delivery is the norm and consumers run in parallel
- When integrating with external systems (payment gateways, ledgers) that may not be natively idempotent

### When NOT to Use
- Systems where the message broker and database are the same system (e.g., using Kafka Streams state stores exclusively)
- Truly fire-and-forget workloads where duplicates have no business consequence
- When the messaging infrastructure provides end-to-end transactional guarantees that extend to all external systems (rare in practice)

### Also see
- [Idempotency](cqrs-event-driven.md#idempotency) · [Exactly-Once Semantics](messaging.md#exactly-once-semantics) · [Idempotent Consumer](messaging.md#idempotent-consumer) · [At-Least-Once Delivery](messaging.md#at-least-once-delivery) · [Database-as-Guardrail Pattern](data-architecture.md#database-as-guardrail-pattern)
- [Bounded Context](#bounded-context) — the semantic counterpart: bounded context defines *what terms mean*; business boundary defines *where correctness is enforced*

---


---

## Coordination Cost

The **organizational and runtime overhead required to keep multiple components, services, or teams aligned** as a system grows. Coordination cost rises with the number of interaction paths — every new service, repository, or team boundary adds potential failure modes, communication delays, and deployment dependencies.

### Key Characteristics

- **Compounds through interactions**: complexity grows with relationships, not just component count
- **Spans technology and people**: includes service-to-service contracts, cross-team approvals, and shared release schedules
- **Hidden until it hurts**: often manifests as slow delivery, production incidents, or duplicated work rather than obvious technical debt
- **Reduced by boundaries and contracts**: modular monoliths, stable APIs, and event-driven decoupling lower coordination pressure

### When to Use

- Evaluating whether to split a monolith or keep modules in-process
- Designing ownership boundaries so teams can ship independently
- Explaining why a "simple" microservice architecture is slowing the organization down

### When NOT to Use

- As an excuse to avoid necessary distribution when genuine scale, regulatory, or team-autonomy constraints exist
- When the real bottleneck is implementation quality rather than cross-component coordination

### Also see

- [Modular Monolith](#modular-monolith) · [Distributed Monolith](#distributed-monolith) · [Microservices](#microservices) · [Loose Coupling](../design-patterns.md#loose-coupling)
- [Architecture Principles](../system-design-architecture/software-architecture/architecture-principles.md) · [29-arch-key-takeaways.md](../system-design-architecture/29-arch-key-takeaways.md)

---

## Pod Affinity

A **Kubernetes scheduling rule** that attracts pods to nodes where other specified pods are already running, based on label selectors. Used to colocate frequently communicating workloads on the same node to minimize network latency.

### Key Characteristics
- **Preferred vs Required**: Preferred affinity is a soft constraint (scheduler tries but falls back); Required affinity is a hard constraint (pod won't schedule if unmet)
- **Label-selector based**: Uses `matchLabels` or `matchExpressions` to identify target pods
- **Topology key**: Defines the scope of colocation — `kubernetes.io/hostname` (same node), `topology.kubernetes.io/zone` (same AZ)
- **Namespaces**: Can match pods across namespaces via `namespaceSelector`

### When to Use
- Services that communicate with high frequency (gRPC, REST, caching, database proxies)
- Latency-sensitive workloads where same-node communication (~tens of microseconds) is critical
- Shared cache or sidecar patterns where data locality improves hit rates

### When NOT to Use
- When node failure would take down all colocated replicas of a critical service — prefer spreading across nodes
- CPU or memory-intensive colocated services that would contend for the same node resources
- When the scheduler cannot place pods due to overly restrictive affinity rules (pod starvation)

### Also see
- [Node Affinity](#node-affinity) · [Topology Spread Constraints](#topology-spread-constraints) · [Blast Radius](resilience.md#blast-radius)

---

## Node Affinity

A **Kubernetes scheduling rule** that constrains which nodes a pod can be placed on, based on node labels. Used to target workloads to specific hardware (GPU, SSD, high-memory) or node pools.

### Key Characteristics
- **Preferred vs Required**: Same soft/hard semantics as Pod Affinity — `preferredDuringSchedulingIgnoredDuringExecution` vs `requiredDuringSchedulingIgnoredDuringExecution`
- **Node-selector evolution**: More expressive than the older `nodeSelector` field; supports `In`, `NotIn`, `Exists`, `DoesNotExist`, `Gt`, `Lt` operators
- **Static at schedule time**: Affinity is evaluated at scheduling time only; `IgnoredDuringExecution` means running pods are not evicted if node labels change

### When to Use
- GPU-accelerated inference or training workloads that require specific hardware
- SSD-backed persistent storage nodes for database or stateful workloads
- Dedicated node pools for compliance isolation (PCI-DSS, HIPAA)

### When NOT to Use
- When the required hardware type is available on all nodes — adds unnecessary scheduling constraints
- For simple CPU/memory requirements — use resource `requests` and `limits` instead
- When it limits the scheduler's ability to pack workloads efficiently across the cluster

### Also see
- [Pod Affinity](#pod-affinity) · [Topology Spread Constraints](#topology-spread-constraints)

---

## Topology Spread Constraints

A **Kubernetes scheduling mechanism** that controls how pods are distributed across failure domains (nodes, zones, regions). Balances availability (spreading to survive domain failures) against latency (colocating to minimize network cost).

### Key Characteristics
- **maxSkew**: The maximum allowed imbalance — e.g., `maxSkew: 1` means no domain can have more than 1 extra pod vs the least-populated domain
- **Topology key**: Defines the domain boundary — `topology.kubernetes.io/zone` (AZ-level), `kubernetes.io/hostname` (node-level)
- **WhenUnsatisfiable**: `DoNotSchedule` (hard) or `ScheduleAnyway` (soft — schedules but skew may exceed maxSkew)
- **Counterbalance to affinity**: Where Pod Affinity pulls pods together, Topology Spread pushes them apart

### When to Use
- Ensuring high availability by distributing replicas across availability zones
- Preventing correlated failures where all replicas land on a single node
- Multi-zone deployments where zone-level redundancy is required

### When NOT to Use
- When colocation is more important than spread (use Pod Affinity instead)
- Small clusters where the number of domains exceeds the number of replicas
- When `maxSkew: 1` is too strict for the workload and causes scheduling failures

### Also see
- [Pod Affinity](#pod-affinity) · [Node Affinity](#node-affinity) · [Correlated Failure Domain](resilience.md#correlated-failure-domain)

---

## Replay Attack

An attack in which an adversary captures a valid request or message and sends it again to repeat an operation or gain an unintended effect. Idempotency keys reduce accidental retries but do not replace authentication, authorization, expiry, or ownership checks.

### Key Characteristics
- Reuses a previously valid request rather than forging a new one
- Can repeat a payment, state change, or privileged command if freshness is not verified
- Requires a freshness or uniqueness control such as a nonce, timestamp window, sequence number, or operation key

### When to Use
- Reviewing authenticated APIs and event consumers that accept retried or delayed messages
- Protecting financial operations and other non-idempotent commands from captured requests

### When NOT to Use
- As a substitute for authentication or authorization
- As the sole protection when a client-generated key can be observed and reused by another principal

### Also see
- [Idempotency-Key](api-design.md#idempotency-key)
- [Authentication and Authorization](security-iam.md)

---

## Forward Deployed Engineer (FDE)

An engineering role where the engineer **embeds directly within customer ecosystems**, writing production code alongside the customer's own engineering teams to customize solutions, perform intense troubleshooting, and accelerate product adoption in high-stakes environments — as opposed to providing professional services on an on-demand basis.

### Key Characteristics
- Works hand-in-hand with customer engineering teams rather than at arm's length
- Writes production-grade code, not just demos or prototypes
- Acts as enterprise architect, high-trust client partner, and hands-on engineer simultaneously
- Tightly integrated into customer ecosystem to solve real-world problems realistically
- Bridges the gap between customer deployment realities and long-term platform engineering health

### When to Use
- Enterprise SaaS/platform companies selling to B2B and B2C/B2B2C customers
- High-stakes deployments with aggressive timelines and shifting requirements
- When customers need deep technical customization beyond what professional services can provide

### When NOT to Use
- Simple product implementations that standard customer success teams can handle
- When the customer does not have the engineering maturity to collaborate at a code level
- Short-term, transactional engagements that don't require deep integration

### Also see
- [InnerSource](#innersource)
- [Technical Debt](#technical-debt)
- [Anti-Corruption Layer](#anti-corruption-layer)

---

## InnerSource

Applying **open-source collaboration practices** (transparent code reviews, shared repositories, cross-team contributions) **within an organization's firewall**. InnerSource enables teams to contribute improvements back to core platforms rather than creating isolated forks or workarounds.

### Key Characteristics
- Code is visible and searchable across the organization
- Contributions follow structured review processes like open-source pull requests
- Encourages cross-team collaboration without sacrificing organizational boundaries
- Reduces duplication by making platform improvements discoverable and reusable

### When to Use
- Large organizations with multiple engineering teams building on shared platforms
- When forward-deployed or field teams need to upstream customer-driven improvements
- Platform teams wanting to scale contributions beyond their immediate team

### When NOT to Use
- Tiny organizations where everyone already works in the same repo
- Highly regulated environments where code visibility must be strictly compartmentalized
- When the overhead of cross-team review outweighs the benefit of shared contributions

### Also see
- [Forward Deployed Engineer (FDE)](#forward-deployed-engineer)
- [Shared Kernel](#shared-kernel)
- [Single Source of Truth](design-patterns.md#single-source-of-truth)

---

## MoSCoW Method

A **prioritization framework** that classifies requirements into four buckets: **M**ust have (non-negotiable), **S**hould have (high priority but can be deferred if necessary), **C**ould have (desirable but not critical), and **W**on't have (explicitly out of scope for the current iteration). Used to manage scope under tight deadlines.

### Key Characteristics
- Forces explicit trade-off discussions rather than treating all requirements as equal
- Tier-1 (Must have) items represent the minimum viable delivery
- Provides a structured vocabulary for negotiating scope with stakeholders
- Can be applied to data attributes, features, or any decomposable requirement set

### When to Use
- High-pressure projects with aggressive, non-negotiable deadlines
- When stakeholders keep adding requirements without acknowledging timeline impact
- Data pipeline projects where some fields are compliance-critical and others are nice-to-have analytics

### When NOT to Use
- Exploratory projects where priorities are genuinely unknown and need discovery
- When stakeholders will simply mark everything as "Must" — the framework only works with honest classification
- Trivial projects with few requirements and no prioritization pressure

### Also see
- [YAGNI](design-patterns.md#yagni)
- [Separation of Concerns](design-patterns.md#separation-of-concerns)
- [Technical Debt](#technical-debt)

---

## flash sale

A time-limited, high-traffic sales event where a limited quantity of inventory is offered at significant discount, creating extreme concurrency contention as thousands of buyers compete for a small number of items simultaneously.

### Key Characteristics

- Extreme read/write contention on hot SKUs — orders of magnitude more requests than available inventory
- Requires multi-layer defense: edge traffic shaping → queue serialization → atomic reservation → authoritative DB
- Inventory correctness is paramount; selling the 101st of 100 items is worse than rejecting legitimate buyers
- Typically paired with reservation-expiry workflows to handle payment failures and abandoned checkouts

### When to Use

- Time-limited promotional events with fixed, known inventory caps
- Scenarios where inventory correctness trumps latency (selling too many is worse than being slow)
- Systems that can preload inventory into a fast edge cache (Redis) before the event

### When NOT to Use

- Continuously available inventory with no time pressure — standard e-commerce patterns suffice
- Unbounded or dynamically restocked inventory where exact counts are less critical
- Low-traffic systems where the overhead of multi-layer defense outweighs the risk

### Also see

- [Overselling](data-concurrency.md#overselling)
- [Inventory Reservation](data-concurrency.md#inventory-reservation)
- [Atomic Conditional Update](data-concurrency.md#atomic-conditional-update)
- [Cache-Aside Pattern](caching.md#cache-aside)

---

## Three-Layer Deduplication

A defense-in-depth pattern for distributed messaging systems that applies deduplication at three independent layers: **client-side** (idempotency key on send), **server-side** (unique constraint on message ID), and **receiver-side** (seen-ID cache). Each layer protects against a different failure mode — no single layer can catch all duplicates.

### Key Characteristics
- **Client layer**: Generates a unique message ID and reuses it on retry. Prevents the sender from creating duplicate payloads during timeout-based retries.
- **Server layer**: Uses the message ID as a primary key or unique index. Duplicate INSERT attempts fail deterministically at the database level.
- **Receiver layer**: Maintains a short-lived LRU cache (with TTL) of recently processed message IDs. Discards incoming messages whose ID is already present.
- **Defense in depth**: If layer 1 misses (e.g., client crash and reinstall), layer 2 catches it. If layer 2 misses (e.g., server replication lag), layer 3 catches it.

### When to Use
- Real-time messaging platforms with at-least-once delivery guarantees (WhatsApp, Telegram, Signal)
- Payment processing and financial systems where duplicate transactions are unacceptable
- Any system where network retries can produce semantically identical requests that must not be processed twice

### When NOT to Use
- Append-only telemetry or logging where occasional duplicates are harmless
- Systems with strict low-latency requirements where the storage/check overhead of all three layers is prohibitive — use two layers instead
- Stateless request-response APIs where idempotency keys alone at the server layer suffice

### Also see
- [Client-Side Deduplication](../reference-dictionary/messaging.md#client-side-deduplication) · [Delivery Cursor](../reference-dictionary/messaging.md#delivery-cursor) · [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer)

---

## Two Generals Problem

A **fundamental thought experiment in distributed systems** that proves it is impossible for two parties to reach consensus over an unreliable communication channel with absolute certainty. Two generals must coordinate an attack via messengers who may be captured; no finite exchange of messages can guarantee both generals know the other received the plan — there is always a last message whose acknowledgment cannot be confirmed.

### Key Characteristics
- **Unsolvable in the general case**: No protocol can guarantee both parties agree with 100% certainty over an unreliable channel
- **Maps to distributed systems**: Producer-consumer acknowledgment, two-phase commit, and TCP handshakes all face the same fundamental limitation — you can never be certain the last acknowledgment was received
- **Practical mitigation**: Systems accept probabilistic guarantees (timeouts, retries, idempotency) rather than absolute certainty
- **Originally formulated by Akkoyunlu et al. (1975) and named by Jim Gray (1978)**

### When to Use
- Understanding why exactly-once delivery is theoretically impossible in the general case
- Explaining why at-least-once with idempotency is the pragmatic choice over exactly-once
- Designing systems where the uncertainty of acknowledgment is explicitly accounted for

### When NOT to Use
- As an excuse to avoid building idempotency — the theoretical impossibility of perfect coordination is precisely why idempotency is mandatory
- To argue that distributed systems are inherently unreliable and therefore not worth engineering rigorously

### Also see
- [At-Least-Once Semantics](../reference-dictionary/messaging.md#at-least-once-semantics) · [Exactly-Once Semantics](../reference-dictionary/messaging.md#exactly-once-semantics) · [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency)

---

## Deterministic Processing

A design constraint on event-processing logic requiring that **the same input always produces the same output**, regardless of when or how many times processing occurs. Non-deterministic functions (`NOW()`, `UUID()`, external API calls) are replaced with values carried in the event payload or derived deterministically from it.

### Key Characteristics
- **Event-derived values only**: All processing inputs come from the event payload — no ambient state (clock, random, network)
- **Replay-safe**: The same event stream replayed N times produces identical final state
- **Enables event sourcing**: Deterministic processing is a prerequisite for event replay as a recovery and auditing mechanism
- **Event-carried state transfer**: Events must carry sufficient data for consumers to process without external calls

### When to Use
- Event-sourced systems where replay is used for recovery, migration, or auditing
- Idempotent consumers where non-determinism would break the idempotency guarantee
- Systems requiring provable correctness through replay verification

### When NOT to Use
- When external API enrichment is essential and caching is not feasible (accept that replay may produce slightly different results)
- Simple CRUD consumers where replay is never needed
- When event size constraints prevent carrying all required data in the payload

### Also see
- [Event Sourcing](../reference-dictionary/cqrs-event-driven.md#event-sourcing) · [Event Replay](../reference-dictionary/cqrs-event-driven.md#event-replay) · [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency)
