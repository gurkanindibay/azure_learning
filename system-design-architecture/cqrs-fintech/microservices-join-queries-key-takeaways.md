---
type: System Design
title: "Microservices Join Queries — Key Takeaways"
description: "Solving cross-service data aggregation: API Composition for simple queries, CQRS read models with CDC for complex filtering, and when to choose each."
timestamp: 2026-07-17T00:00:00Z
---

# Microservices Join Queries — Key Takeaways

> **Parent**: [CQRS in System Design — Key Takeaways](cqrs-in-system-design-key-takeaways.md)
> **Source**: [Solving Join Queries in Microservices — API Composition vs CQRS](../../articles/software-architecture/microservices-join-queries-solutions.md) — Umesh Kumar Yadav, 2026-07-04
> **Purpose**: Extract practical patterns for replacing SQL JOINs across microservice boundaries: when API Composition suffices, when CQRS read models become necessary, and how CDC-backed denormalization enables complex cross-service queries.
> **Also see**: [CQRS for Fintech](cqrs-fintech.md), [API Design Patterns](../api-network/api-network-design.md)
> **Dictionary**: [Reference Dictionary](../../reference-dictionary/) — definitions for [API Composition](../../reference-dictionary/api-design.md#api-composition), [CQRS](../../reference-dictionary/cqrs-event-driven.md#cqrs), [Read Model](../../reference-dictionary/cqrs-event-driven.md#read-model), [Eventual Consistency](../../reference-dictionary/cqrs-event-driven.md#eventual-consistency), [Change Data Capture](../../reference-dictionary/data-concurrency.md#change-data-capture), [Denormalization](../../reference-dictionary/data-architecture.md#denormalization)
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`cqrs-44`](#cqrs-44-api-composition-is-the-pragmatic-first-step-before-cqrs) | SQL JOINs disappear across service boundaries | Aggregate data in application memory via API Composition for simple cross-service queries |
| [`cqrs-45`](#cqrs-45-cross-service-filtering-is-the-scaling-cliff-for-api-composition) | Filtering and pagination across services breaks API Composition | Fetch-then-filter creates a combinatorial explosion of network calls; it is the signal to adopt CQRS |
| [`cqrs-46`](#cqrs-46-cdc-backed-read-models-solve-cross-service-query-complexity) | Complex queries need pre-joined data without tight coupling | Use CDC/Kafka to feed a denormalized read model (e.g., Elasticsearch) that answers complex queries in one call |

---

## cqrs-44: API Composition Is the Pragmatic First Step Before CQRS

| | |
|:---|:---|
| **Problem** | After decomposing a monolith into microservices, a simple query like "show me the order with customer, product, and payment details" now requires data from four independent services, each with its own database. SQL JOINs are no longer possible. |
| **Root cause** | Database-per-service isolation prevents direct cross-database queries. The convenience of a single `JOIN` across normalized tables vanishes, and the team must decide how to reassemble related data at the application layer. |

**Strategy**: Designate one service as the **API Composer**. It calls each downstream service sequentially, collects their responses, and assembles the result in application memory. This is the simplest pattern — no new infrastructure, no event pipelines, no denormalized stores.

```text
Client → OrderQueryService → UserService.getUser(id)
                            → ProductService.getProduct(id)
                            → PaymentService.getPayment(orderId)
                            → assemble OrderResponse in memory
```

**Tradeoff**: API Composition adds per-request latency (fan-out calls are serial or parallel but still bounded by the slowest service). It works well for detail pages and dashboards with a small, fixed set of services. It breaks down when you need to filter or paginate across services — see [cqrs-45](#cqrs-45-cross-service-filtering-is-the-scaling-cliff-for-api-composition).

> **Key insight**: API Composition is not a failure to adopt CQRS — it is the correct starting point for most teams. Introduce CQRS only when API Composition shows concrete pain at scale.

**Cross-reference**: See [CQRS in System Design — Key Takeaways](cqrs-in-system-design-key-takeaways.md#cqrs-43-adopt-cqrs-only-when-the-system-fights-back) on when the system fights back.

---

## cqrs-45: Cross-Service Filtering Is the Scaling Cliff for API Composition

| | |
|:---|:---|
| **Problem** | A query like "find 10 orders from VIP customers for fresh products" requires filtering across the Order, User, and Product services. With API Composition, the orchestrator must fetch batches, filter in memory, and keep fetching until it accumulates enough results — a combinatorial explosion of network calls. |
| **Root cause** | Each service owns only its own predicate (`userLevel = VIP`, `category = Fresh`). No single service can evaluate the full filter. The API Composer must brute-force: fetch N orders → filter by product → filter by user → if < 10 results, fetch more — repeating until satisfied. |

**Strategy**: Recognize this pattern as the signal to move from API Composition to CQRS. When queries span predicates across multiple services, a pre-joined, denormalized read model becomes necessary.

```text
API Composition (fails at scale):
  fetch 10 orders → 7 fresh products → 5 VIP users → only 5 results
  fetch 10 more → 6 fresh → 4 VIP → total 9
  fetch 10 more → 8 fresh → 6 VIP → total 15 ✓ (after 30+ service calls)

CQRS (one call):
  Elasticsearch: { userLevel: "VIP", category: "Fresh", size: 10 }
```

**Tradeoff**: The fetch-then-filter loop works for trivial volumes but degrades exponentially with data size. The inflection point — where paginated cross-service filtering becomes intolerably slow or expensive — is the right moment to introduce a read model.

> **Key insight**: Don't optimize this pattern with caching or parallel fan-out. Cross-service filtering with pagination is a structural problem, not a performance problem. The fix is architectural: move the filter evaluation to a single data store that holds pre-joined data.

**Cross-reference**: See [cqrs-40](cqrs-in-system-design-key-takeaways.md#cqrs-40-queries-need-shape-and-speed-not-canonical-state) on why read models should be shaped for queries, not normalized for writes.

---

## cqrs-46: CDC-Backed Read Models Solve Cross-Service Query Complexity

| | |
|:---|:---|
| **Problem** | Teams need fast, complex queries (filtering, full-text search, aggregations, pagination) across data owned by multiple microservices, but cannot couple services by sharing databases or adding synchronous fan-out calls. |
| **Root cause** | Each microservice owns its data and publishes changes asynchronously. Without a consolidated query surface, every cross-service question becomes a distributed join problem. |

**Strategy**: Build a **denormalized read model** (e.g., Elasticsearch, materialized views) that is fed by Change Data Capture (CDC) or event streams (Kafka, Debezium) from each source service. Each service publishes its data changes; the read model consumes them and maintains a wide, pre-joined document or table. Queries hit this single store — no JOINs, no fan-out.

```text
MySQL (User DB, Product DB, Order DB)
  → CDC/Kafka/Debezium
    → Elasticsearch (denormalized order documents)
      → Query Service (single-call reads)
```

**Tradeoff**: This introduces eventual consistency — the read model lags behind the write model by milliseconds to seconds. For search, reporting, and analytics this is acceptable. For workflows requiring strict read-your-writes consistency, you must either avoid the read model for that path or design around the lag. It also adds operational complexity: Kafka, Debezium/Canal, and Elasticsearch must be deployed, monitored, and maintained.

> **Key insight**: The denormalized read model is not a source of truth — it is a disposable projection. It can be rebuilt from the authoritative event log or write-side database at any time. Treat it as a cache with a well-defined rebuild path.

**Cross-reference**: See [CQRS for Fintech — Key Takeaways](cqrs-fintech.md#cqrs-07-read-models-are-replaceable-the-ledger-is-sacred) on read-model rebuildability. See [Change Data Capture](../../reference-dictionary/data-concurrency.md#change-data-capture) for CDC fundamentals.
