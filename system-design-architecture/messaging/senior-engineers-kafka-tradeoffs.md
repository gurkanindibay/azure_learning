---
type: System Design
title: "Message Brokers & Async — Key Takeaways"
description: "Senior Engineers Don't Start With Kafka — Architectural Tradeoffs and Requirement-First Design"
generated: { by: process:okf-migrate, at: 2026-06-28T00:00:00Z }
---

# Message Brokers & Async — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Senior Engineers Don't Start With Kafka (They Start With This)](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md)
> **Purpose**: Architectural decision-making patterns — starting with requirements and tradeoffs before selecting messaging infrastructure.

> **Also see**: [Message Brokers & Async](message-brokers-async.md), [Resilience Patterns](../resilience/)
> **Dictionary**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Caching](../../reference-dictionary/caching.md), [Event-Driven Architecture](../../reference-dictionary/cqrs-event-driven.md)
> **Taxonomy Reference**: §2.2 Application Software Architecture, §3.3 Event-Driven & Messaging

---

## Contents

- [broker-66: Requirements First — Don't Start With Tools](#broker-66) — Naming technologies too early produces the wrong architecture.
- [broker-67: Read Path Separation — Readers Kill Systems](#broker-67) — The write side is easy; massive concurrent reads are the real scalability threat.
- [broker-68: Idempotency Is Non-Negotiable](#broker-68) — Without duplicate protection, retries corrupt business data.
- [broker-69: Kafka Decouples, Business Logic Delivers Value](#broker-69) — Kafka is infrastructure; insights come from application logic.
- [broker-70: Caching Over Database for Read-Heavy Workloads](#broker-70) — Compute once, cache, serve millions.
- [broker-71: Design for Failure, Not Success](#broker-71) — Distributed systems are recovery systems; happy-path thinking creates brittle architectures.

---

## broker-66: Requirements First — Don't Start With Tools

> **Source**: [§"The Biggest Mistake"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#the-biggest-mistake)

| | |
|:---|:---|
| **Problem** | Engineers presented with a system design problem immediately name technologies (Kafka, Flink, Cassandra) without understanding constraints. This produces architecture optimized for the wrong layer. |
| **Root cause** | Tools are treated as starting points rather than answers derived from requirements. |

> **Strategy**: Before selecting any technology, answer: What is the throughput? What latency do users expect? How many readers are there? Is consistency critical? Can we tolerate data loss? Is traffic uniform or bursty? Architecture is about constraints, not tools.
>
> **Tradeoff**: Requirement-first design takes more upfront analysis time but prevents costly architectural mismatches. Tool-first design is faster initially but risks building the wrong system.
>
> **Cross-reference**: [Pragmatic System Design](../system-design-interview/pragmatic-takeaways.md#prag-01) · [Architecture Principles](../../articles/software-architecture/architecture-principles.md)

---

## broker-67: Read Path Separation — Readers Kill Systems

> **Source**: [§"The Read Side Is Where Systems Die"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#the-read-side-is-where-systems-die), [§"Separation of Read and Write Paths"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#separation-of-read-and-write-paths-changes-everything)

| | |
|:---|:---|
| **Problem** | National-scale events produce moderate write traffic but enormous read traffic. 100 million simultaneous read requests hitting the primary database directly cause cascading failure. |
| **Root cause** | Failing to separate read and write concerns — one database forced to handle both durability (writes) and massive throughput (reads). |

> **Strategy**: Separate read and write paths. The write path prioritizes durability, consistency, ordering, and data correctness. The read path prioritizes low latency, massive throughput, and fast responses. Use caches (Redis) and CDNs to absorb read traffic; let the database focus on writes.
>
> **Tradeoff**: Read/write separation adds architectural complexity (cache invalidation, eventual consistency). The alternative — a single system handling both — collapses under read pressure at scale.
>
> **Cross-reference**: [CQRS for Fintech](../cqrs-fintech/cqrs-fintech.md) · [Caching Architecture](../caching/) · [Azure CDN](../../architecture-azure/networking/cdn/)

---

## broker-68: Idempotency Is Non-Negotiable

> **Source**: [§"Idempotency Matters More Than Fancy Architecture"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#idempotency-matters-more-than-fancy-architecture)

| | |
|:---|:---|
| **Problem** | Duplicate events from network failures, dropped connections, double-submits, and retries cause data corruption — 50,000 votes become 100,000. |
| **Root cause** | Systems assume exactly-once delivery when networks guarantee at-most-once or at-least-once. |

> **Strategy**: Assign every event a unique identity (idempotency key). On duplicate arrival, recognize and safely ignore. This applies at every layer: API endpoints, Kafka consumers, database writes. Idempotency is simple, boring, and absolutely critical.
>
> **Tradeoff**: Idempotency adds key-storage overhead and lookup latency per operation. The cost of NOT implementing it is data corruption that is often irreversible.
>
> **Cross-reference**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency) · [Kafka Producer Ack & Idempotency](kafka-producer-ack-idempotency.md) · [Concurrency & Transactions](../concurrency-transactions/)

---

## broker-69: Kafka Decouples, Business Logic Delivers Value

> **Source**: [§"Kafka Isn't the Star of the Show"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#kafka-isnt-the-star-of-the-show)

| | |
|:---|:---|
| **Problem** | Engineers treat Kafka as the hero of the architecture, over-investing in infrastructure while under-investing in the business logic that generates actual value. |
| **Root cause** | Confusing infrastructure capability (message transport) with business capability (insight generation). |

> **Strategy**: Understand Kafka's role precisely — it decouples producers from consumers, absorbs bursts, provides durability, and allows replay. Kafka is the highway; your business logic is the destination. Invest proportionally in both. For simple requirements, Kafka consumers + PostgreSQL may suffice — Flink is overkill.
>
> **Tradeoff**: Adding Kafka introduces operational complexity (cluster management, monitoring, offset tracking). The benefit — producer-consumer decoupling — must justify this cost. If requirements are simple, a direct database write with polling may be sufficient.
>
> **Cross-reference**: [Kafka Concepts](../../articles/messaging/kafka-concepts-that-every-architect-should-master.md) · [Kafka Offset Commit Strategies](kafka-offset-commit-strategies.md) · [Apache Iggy](apache-iggy.md)

---

## broker-70: Caching Over Database for Read-Heavy Workloads

> **Source**: [§"Caching Is More Important Than Databases"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#caching-is-more-important-than-databases)

| | |
|:---|:---|
| **Problem** | Millions of users requesting the same computed result (e.g., "Who's leading?"). Each request hitting the database directly causes unnecessary load and latency. |
| **Root cause** | Engineers optimize database choice while neglecting the caching layer — the real scalability hero sits in front, not behind. |

> **Strategy**: Compute results once, cache them (Redis for dynamic data, CDN for static summaries), serve everyone from cache. The database handles writes; the cache absorbs reads. This is the single highest-leverage scalability pattern for read-heavy workloads.
>
> **Tradeoff**: Caching introduces staleness — cached results may lag behind the source of truth. For election results where seconds-old data is acceptable, this tradeoff is worth it. For systems requiring strong consistency, cache carefully or not at all.
>
> **Cross-reference**: [Caching Architecture](../caching/) · [Redis Internals](../caching/redis-internals.md) · [Azure Redis Cache](../../architecture-azure/data/redis/)

---

## broker-71: Design for Failure, Not Success

> **Source**: [§"Design for Failure, Not Success"](../../articles/software-architecture/senior-engineers-dont-start-with-kafka.md#design-for-failure-not-success)

| | |
|:---|:---|
| **Problem** | Systems designed only for the happy path fail catastrophically when anything goes wrong — and in distributed systems, something always goes wrong. |
| **Root cause** | Assuming infrastructure is reliable rather than designing recovery mechanisms into the architecture from day one. |

> **Strategy**: For every component, ask "When this breaks, what happens next?" Design explicit recovery paths: What if Kafka goes down? What if consumers fall behind? What if a region loses connectivity? What if operators accidentally resubmit results? Distributed systems are recovery systems — design them accordingly.
>
> **Tradeoff**: Failure-first design requires additional engineering effort upfront (circuit breakers, retry policies, dead letter queues, fallback mechanisms). The alternative — optimistic design — saves upfront cost but creates unpredictable production outages.
>
> **Cross-reference**: [Resilience Patterns](../resilience/) · [Circuit Breaker Honesty](../resilience/circuit-breaker-honesty.md) · [Defensive Coding](../../articles/resilience/defensive-coding-approach.md)
