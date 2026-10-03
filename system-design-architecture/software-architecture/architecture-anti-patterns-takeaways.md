---
type: System Design
title: "Architecture Anti-Patterns — Key Takeaways"
description: "Ten timing anti-patterns where valid architecture practices are adopted before the problem they solve actually exists, and the heuristics for applying them at the right moment."
generated: { by: process:format-agent, at: 2026-09-30T23:12:00+03:00 }
---

# Architecture Anti-Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [10 Popular Architecture Practices That Do More Harm Than Good](../../articles/software-architecture/10-popular-architecture-practices-harm.md) by Vinod Pal, 2026-09-27

> **Also see**: [Architecture Principles](architecture-principles.md) · [Microservices Patterns](29-svc-key-takeaways.md) · [Resilience Patterns](../resilience/resilience-patterns.md)
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md) · [Resilience](../../reference-dictionary/resilience.md) · [Messaging](../../reference-dictionary/messaging.md)
> **Taxonomy Reference**: §2.6 Design Patterns

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [arch-22](#arch-22-big-design-upfront) | Design decisions made on the day you know the least | Design only decisions that are expensive to undo |
| [arch-23](#arch-23-premature-scale) | Scaling for imagined traffic before it exists | Scale for measured bottlenecks, not anticipated ones |
| [arch-24](#arch-24-configuration-explosion) | Every future need becomes a configurable path | Configuration multiplies untested code paths |
| [arch-25](#arch-25-premature-vendor-abstraction) | Wrapping vendors "in case we switch" loses features | Defer abstraction until you have two real backends |
| [arch-26](#arch-26-premature-microservices) | Service boundaries before team topology matches | Modular monolith first; extract services when blocked |
| [arch-27](#arch-27-queue-without-ownership) | Queues hide failures silently | Queues need DLQ alerts, age monitoring, and a clear owner |
| [arch-28](#arch-28-cache-as-fix) | Caching over a slow query creates hidden dependency | Fix the root cause; cache buys time only |
| [arch-29](#arch-29-bloated-api-gateway) | Gateway accumulates business logic | Gateway for cross-cutting concerns; BFF for client-specific logic |
| [arch-30](#arch-30-temporal-coupling-via-source-of-truth) | One central service becomes a runtime bottleneck | Separate read copies (via events) from write ownership |
| [arch-31](#arch-31-chasing-nines) | Availability target exceeds what hard dependencies allow | Set availability from business cost and dependency SLA |

---

## arch-22: Big Design Upfront

> **Source**: [§"1. Designing the Full Architecture Upfront"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#1-designing-the-full-architecture-upfront)

| | |
|:---|:---|
| **Problem** | Big design docs are written before any code, committing the team to assumptions made on the day they know the least. Six months later, diagrams show one system and production runs another. |
| **Root cause** | Upfront design conflates decisions that are expensive to reverse (data models, public APIs) with decisions that are not (framework choices, infra tooling). |

**Strategy**: Split decisions by reversibility. Spend design time on the hard-to-reverse group. Record each decision in a short **Architecture Decision Record (ADR)** with the reasoning. Pick something reasonable and move on for everything else.

**Tradeoff**: ADR discipline adds overhead. Without it, however, rationale disappears and successors repeat the same analysis — or silently undo it.

**Cross-reference**: [arch-20 Simplicity Over Completeness](architecture-principles.md#arch-20-simplicity-over-completeness) · [Architecture Decision Record](../../reference-dictionary/architecture-patterns.md#architecture-decision-record-adr)

---

## arch-23: Premature Scale

> **Source**: [§"2. Designing for Scale From Day One"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#2-designing-for-scale-from-day-one)

| | |
|:---|:---|
| **Problem** | Teams launch with clusters, event streams, and autoscaling for a few hundred users, paying for scale every day before needing it. The guess about which component will bottleneck is usually wrong. |
| **Root cause** | Scaling anxiety causes teams to distribute the bottleneck risk across the entire system uniformly instead of profiling real traffic. |

**Strategy**: Identify the one number most likely to hurt first (peak requests, data volume, write rate). Plan for the growth that number already shows. Start migrations early — they always take longer than expected.

**Tradeoff**: Deferring scale can require a rewrite during a growth spike. The window for a safe migration is narrower than it looks.

**Cross-reference**: [arch-19 Scaling = Removing Unnecessary Waiting](architecture-principles.md#arch-19-scaling--removing-unnecessary-waiting) · [arch-21 Data Flow First, Technology Second](architecture-principles.md#arch-21-data-flow-first-technology-second)

---

## arch-24: Configuration Explosion

> **Source**: [§"3. Making the System Configurable for Future Needs"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#3-making-the-system-configurable-for-future-needs)

| | |
|:---|:---|
| **Problem** | Adding settings for imagined future needs multiplies code paths. Config changes bypass code review and testing pipelines. Unused paths rot. When the imagined need finally arrives, its rules look nothing like the guess — so you rewrite it and also rip out the old one. |
| **Root cause** | Speculative generalization (YAGNI violation) driven by feature anxiety. |

**Strategy**: Add a configuration option only when a real second customer has a real different need. Treat config like code: version it, validate it, and test all combinations you ship. Kill switches and feature flags are the exception — they are incident-response levers with clear owners.

**Tradeoff**: Stricter config discipline can slow response to future customers. The discipline pays back in reduced production incidents caused by config drift.

**Cross-reference**: [Knight Capital case study (2012)](../../articles/software-architecture/10-popular-architecture-practices-harm.md#3-making-the-system-configurable-for-future-needs) · [YAGNI](../../reference-dictionary/architecture-patterns.md#yagni)

---

## arch-25: Premature Vendor Abstraction

> **Source**: [§"4. Hiding Vendors Behind Abstractions"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#4-hiding-vendors-behind-abstractions)

| | |
|:---|:---|
| **Problem** | Generic abstraction layers ("in case we switch databases") expose only 20% of what the vendor offers, because the layer can only express the common subset. You maintain two systems. When a performance problem requires a vendor-specific feature, you either break the abstraction or accept the slow path. |
| **Root cause** | Lock-in fear triggered before any actual lock-in pain. |

**Strategy**: Defer abstraction until you have two real backends to abstract over. When abstraction is warranted, keep it thin, owned, and testable. Measure vendor-migration probability against cost of daily abstraction overhead.

**Tradeoff**: Direct vendor usage creates genuine migration work later. Abstraction creates daily friction and feature gaps immediately.

**Cross-reference**: [arch-06 Loose Coupling](architecture-principles.md#arch-06-loose-coupling)

---

## arch-26: Premature Microservices

> **Source**: [§"5. Splitting the System into Microservices Early"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#5-splitting-the-system-into-microservices-early)

| | |
|:---|:---|
| **Problem** | Early service splits add network calls, distributed tracing, separate deployments, and failure surfaces. Service boundaries become inter-team contracts that are harder to change than internal interfaces. When one team owns all services, microservices add overhead without the organizational benefit. |
| **Root cause** | Architecture chosen ahead of team topology. |

**Strategy**: Start with a **modular monolith** — clear internal module boundaries without network complexity. Extract a service only when you have an actual forcing function: a team blocked on another team, a component that needs an independent release cadence, or a clear scaling requirement for one part.

**Tradeoff**: Modular monoliths can become tightly coupled over time without enforced module boundaries (compile-time or test-time checks).

**Cross-reference**: [Distributed Monolith](distributed-monolith.md) (`svc-01`) · [Microservices Patterns](29-svc-key-takeaways.md) · [Modular Monolith](../../reference-dictionary/architecture-patterns.md#modular-monolith)

---

## arch-27: Queue Without Ownership

> **Source**: [§"6. Putting a Queue Between Every Service"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#6-putting-a-queue-between-every-service)

| | |
|:---|:---|
| **Problem** | Async queues hide failures: orders process, payments succeed, dashboards are green — but no items are delivered. Silent failure is harder to diagnose than a synchronous exception. |
| **Root cause** | The dual-write problem: saving data and publishing an event are two separate writes. If one fails, data drifts. At-least-once delivery means consumers receive duplicates. |

**Strategy**: Use the **Outbox Pattern** — save the event in the same database transaction as the state change. A separate relay process publishes confirmed events. Every consumer must be **idempotent**. Alert on the **dead letter queue (DLQ)**. Monitor the **age of the oldest message**, not just queue depth.

**Tradeoff**: The outbox pattern adds a relay process and polling overhead. Without it, dual-write failures cause silent data drift that surfaces as customer support tickets.

**Cross-reference**: [Outbox Pattern](../../reference-dictionary/messaging.md#outbox-pattern) · [Idempotency](../../reference-dictionary/architecture-patterns.md#idempotency) · [arch-08 Idempotency](architecture-principles.md#arch-08-idempotency) · [DLQ](../../reference-dictionary/kafka.md#dead-letter-queue-dlq)

---

## arch-28: Cache as Fix

> **Source**: [§"7. Adding a Cache to Make It Fast"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#7-adding-a-cache-to-make-it-fast)

| | |
|:---|:---|
| **Problem** | Caching over a slow query hides the root cause (often an N+1 query pattern). Over time, the database is sized for cached traffic. When the cache restarts under peak load, every request hits the database simultaneously — a **thundering herd** — and the system cannot survive without the cache. |
| **Root cause** | Cache treats a symptom (latency) without addressing the cause (query inefficiency), creating a hard runtime dependency. |

**Strategy**: Fix the slow query first. Then cache genuinely read-heavy data that can tolerate staleness. Set TTL from business impact: *"How long can this value be wrong before it hurts?"*. Use **request coalescing** (only one request refills a missing key; others wait) to prevent stampedes on cache miss.

**Tradeoff**: Fixing the underlying query takes more time upfront. Caching is faster to ship but creates fragility that grows invisibly.

**Cross-reference**: [Thundering Herd](../../reference-dictionary/resilience.md#thundering-herd) · [Request Coalescing](../../reference-dictionary/architecture-patterns.md#request-coalescing) · [N+1 Query](../../reference-dictionary/databases.md#n1-query)

---

## arch-29: Bloated API Gateway

> **Source**: [§"8. Routing Every Request Through an API Gateway"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#8-routing-every-request-through-an-api-gateway)

| | |
|:---|:---|
| **Problem** | The gateway becomes the easiest place to add business logic. It grows into a second backend owned by one team. Every other team waits in its deploy queue. One bad gateway deploy takes down every client simultaneously. |
| **Root cause** | Convenience proximity: the gateway is the first place code can intercept all traffic, so it accumulates logic that should live in services. |

**Strategy**: Restrict the gateway to **cross-cutting concerns** — auth, rate limits, TLS termination, and routing. For client-specific response shaping, use the **Backend for Frontend (BFF) pattern**: a small backend owned by the client team, with an independent release cadence.

**Tradeoff**: Multiple BFFs duplicate some cross-cutting logic. A single gateway is simpler to operate but creates a team bottleneck at scale.

**Cross-reference**: [Reverse Proxy, LB & API Gateway Takeaways](../api-network/reverse-proxy-lb-gateway.md) · [BFF](../../reference-dictionary/architecture-patterns.md#backend-for-frontend-bff)

---

## arch-30: Temporal Coupling via Source of Truth

> **Source**: [§"9. Keeping One Central Service as the Source of Truth"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#9-keeping-one-central-service-as-the-source-of-truth)

| | |
|:---|:---|
| **Problem** | A central service that owns a data domain is called live on every request from every other service. When it slows during peak traffic, every dependent flow slows with it. Ownership has become a runtime dependency. |
| **Root cause** | **Temporal coupling** — the correctness of one service's work depends on another service being available at that exact moment. |

**Strategy**: Separate write ownership from read availability. The central service owns all writes. Other services maintain a local read replica updated via events. Reads can proceed even when the owner is degraded. Reserve live calls for data that must be exact at the moment of use (e.g., account balance before a payment).

**Tradeoff**: Local copies can be stale. Events arrive late, duplicated, or out of order. Copies drift and need a rebuild mechanism. Total implementation cost is significantly higher than live calls.

**Cross-reference**: [CQRS Takeaways](../cqrs-fintech/cqrs-fintech.md) · [arch-05 Single Source of Truth](architecture-principles.md#arch-05-single-source-of-truth) · [Temporal Coupling](../../reference-dictionary/architecture-patterns.md#temporal-coupling)

---

## arch-31: Chasing Nines

> **Source**: [§"10. Aiming for the Highest Availability You Can Get"](../../articles/software-architecture/10-popular-architecture-practices-harm.md#10-aiming-for-the-highest-availability-you-can-get)

| | |
|:---|:---|
| **Problem** | Sales commits to 99.99% uptime before engineering evaluates what it requires. Multi-region setups are drawn on whiteboards — but your system cannot exceed the availability of the hardest dependency in its request path. |
| **Root cause** | Availability targets are set as marketing commitments rather than calculated from dependency SLAs and business impact. |

**Strategy**: Calculate your theoretical availability ceiling from all hard dependencies. Set the availability target from business impact (what does an outage hour actually cost?). Agree on an **error budget** and pause feature work when it runs out. Many systems do well at 99.9% with a warm standby rather than a full multi-region active-active topology.

**Tradeoff**: Lower targets reduce engineering overhead but may not satisfy regulated industries or large enterprise clients. Higher targets can be achieved with redundancy, retries, caching, and graceful fallbacks — these raise the effective number without requiring multi-region.

**Cross-reference**: [Resilience Patterns](../resilience/resilience-patterns.md) · [Error Budget](../../reference-dictionary/observability.md#error-budget) · [SLO/SLA](../../reference-dictionary/observability.md#slo-service-level-objective)
