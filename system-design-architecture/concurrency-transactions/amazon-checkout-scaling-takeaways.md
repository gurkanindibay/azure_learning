---
type: System Design
title: "Concurrency & Transactions — Checkout Scaling vs. Inventory Protection Takeaways"
description: "Reusable patterns from high-scale checkout: why throughput engineering doesn't prevent overselling, pessimistic-lock serialization bottlenecks, distributed reservation-expiry cleanup, eventual consistency as product decision, and impossible-state prevention as architectural driver."
generated: { by: process:okf-migrate, at: 2026-07-18T00:00:00Z }
---

# Concurrency & Transactions — Checkout Scaling vs. Inventory Protection Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)
> **Related**: [Concurrency & Transactions](concurrency-transactions.md), [Transaction Patterns](transaction-patterns.md), [Flash-Sale Takeaways](30-tx-key-takeaways.md)
> **Dictionary**: [Inventory Reservation](../../reference-dictionary/data-concurrency.md#inventory-reservation), [Overselling](../../reference-dictionary/data-concurrency.md#overselling), [Pessimistic Locking](../../reference-dictionary/data-concurrency.md#pessimistic-locking), [Lock Contention](../../reference-dictionary/data-concurrency.md#lock-contention), [Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern), [Compensating Transaction](../../reference-dictionary/data-concurrency.md#compensating-transaction), [Atomic Conditional Update](../../reference-dictionary/data-concurrency.md#atomic-conditional-update), [Distributed Lock](../../reference-dictionary/data-concurrency.md#distributed-lock), [Impossible State](../../reference-dictionary/data-concurrency.md#impossible-state)
> **Taxonomy Reference**: §2.3 Concurrency & Asynchronous Processing

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [tx-37](#tx-37-scaling-and-inventory-protection-are-orthogonal) | Auto-scaling handles traffic but doesn't prevent overselling | Scaling ≠ inventory protection |
| [tx-38](#tx-38-pessimistic-locking-serialization-bottleneck) | `SELECT FOR UPDATE` on a hot SKU degrades the entire system | Lock-contention cascade |
| [tx-39](#tx-39-distributed-reservation-expiry-cleanup) | Multiple scheduler replicas release the same expired reservations | Cleanup-job coordination |
| [tx-40](#tx-40-eventual-consistency-as-product-decision) | A mid-checkout service outage forces a UX honesty choice | Async confirmation as product decision |
| [tx-41](#tx-41-impossible-state-prevention-as-architectural-driver) | The architecture exists to prevent states that must never occur | Impossible-state prevention |

---

## tx-37: Scaling and Inventory Protection Are Orthogonal

> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)

| | |
|:---|:---|
| **Problem** | A flash sale with healthy auto-scaling, low CPU, and hundreds of pods still oversells inventory. |
| **Root cause** | Throughput engineering (more servers, more pods, better load balancers) does not enforce the invariant "only N units can be sold." These are separate concerns. |

**Strategy**: Treat scaling and inventory protection as independent design dimensions. Scaling addresses request volume; inventory protection addresses the "who gets the last item?" question through atomic conditional updates, reservation models, and idempotency.

| Tradeoff | Detail |
|:---|:---|
| **Separation of concerns** | Scaling can be optimized independently of correctness — but correctness must be designed in, not assumed. |
| **Deceptive metrics** | Healthy CPU/memory/latency dashboards give false confidence; they measure throughput, not consistency. |
| **Design order** | Solve the inventory-protection problem first, then scale it. Doing the reverse means scaling a broken system. |

> **Also see**: [tx-08 Atomic Inventory Reservation](transaction-patterns.md#tx-08-atomic-inventory-reservation), [tx-36 Layered Flash-Sale Defense](30-tx-key-takeaways.md#tx-36-layered-flash-sale-defense-architecture)
> **Dictionary**: [Overselling](../../reference-dictionary/data-concurrency.md#overselling), [Atomic Conditional Update](../../reference-dictionary/data-concurrency.md#atomic-conditional-update)

---

## tx-38: Pessimistic Locking Serialization Bottleneck

> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)

| | |
|:---|:---|
| **Problem** | `SELECT ... FOR UPDATE` on a hot SKU during a flash sale serializes 100K concurrent requests, exhausting connection pools and degrading latency for all customers — including those buying unrelated products. |
| **Root cause** | Pessimistic row locks create a queue at the database layer. Under high contention, the lock becomes a single serialization point that amplifies degradation proportionally to demand. |

**Strategy**: Accept that pessimistic locking is correct but doesn't compose with high concurrency. Move contention away from the database: queue-based serialization (single-writer queue per hot SKU), reservation models that decouple inventory holds from payment, or Redis-based inventory counters with atomic decrement-and-check.

| Tradeoff | Detail |
|:---|:---|
| **Correctness** | `SELECT FOR UPDATE` guarantees no overselling — it's not wrong, just slow at scale. |
| **Blast radius** | A hot-SKU lock doesn't just affect that product; it exhausts shared connection pools, degrading unrelated traffic. |
| **Mitigation** | Partition inventory by SKU, use short-lived reservation TTLs, or serialize at the application layer (queue) rather than the database layer. |

> **Also see**: [tx-32 Queue-Based Serialization](30-tx-key-takeaways.md#tx-32-queue-based-serialization-for-inventory-contention), [tx-03 Distributed Locks](concurrency-transactions.md#tx-03-distributed-locks)
> **Dictionary**: [Pessimistic Locking](../../reference-dictionary/data-concurrency.md#pessimistic-locking), [Lock Contention](../../reference-dictionary/data-concurrency.md#lock-contention)

---

## tx-39: Distributed Reservation-Expiry Cleanup

> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)

| | |
|:---|:---|
| **Problem** | A scheduled job releases expired reservations, but in Kubernetes with N replicas, N schedulers run the same job simultaneously, causing duplicate releases, race conditions, and inventory-count drift. |
| **Root cause** | The cleanup job is stateless cron logic running in a multi-replica environment with no coordination. The same expired rows are visible to every replica. |

**Strategy**: The cleanup mechanism needs the same distributed-coordination properties as the checkout flow itself. Pick one:
- **Leader election**: Only one replica runs the cleanup job (e.g., Kubernetes Lease, etcd).
- **Distributed lock**: Acquire a lock before scanning expired reservations; skip if lock is held.
- **TTL-based expiration in the data store**: Let Redis or the database expire reservations natively (e.g., Redis `EXPIRE`, PostgreSQL `pg_cron` with `FOR UPDATE SKIP LOCKED`). Eliminates the separate cleanup process entirely.

| Tradeoff | Detail |
|:---|:---|
| **Leader election** | Simple but adds infrastructure dependency; failover delay means cleanup pauses briefly. |
| **Distributed lock** | Works but has expiry edge cases — if the lock holder crashes mid-cleanup, the lock must expire before another replica takes over. |
| **Data-store TTL** | Cleanest (no separate job) but doesn't easily trigger business logic on expiry (e.g., sending a notification). |
| **Irony** | Releasing expired reservations is often harder than creating them — it's a distributed coordination problem that looks deceptively like a cron job. |

> **Also see**: [tx-33 Reservation-Payment Decoupling](30-tx-key-takeaways.md#tx-33-reservation-payment-decoupling-with-expiry), [tx-03 Distributed Locks](concurrency-transactions.md#tx-03-distributed-locks)
> **Dictionary**: [Distributed Lock](../../reference-dictionary/data-concurrency.md#distributed-lock), [Inventory Reservation](../../reference-dictionary/data-concurrency.md#inventory-reservation), [Lease-Based Lock](../../reference-dictionary/data-concurrency.md#lease-based-lock)

---

## tx-40: Eventual Consistency as Product Decision

> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)

| | |
|:---|:---|
| **Problem** | Payment succeeds but the inventory service is unavailable — the system can't confirm the reservation synchronously. The customer expects immediate feedback. |
| **Root cause** | Synchronous coordination ties checkout latency directly to the availability of every downstream service. Any service outage blocks the entire flow. |

**Strategy**: Accept that not every operation can be synchronous and reliable. Payment succeeds → publishes a message to a queue → inventory confirms asynchronously. The customer sees "We're confirming your order" rather than "Order placed successfully." This is a product decision, not just a technical one: how long is the customer willing to wait? What does the UI show during that window? What happens if confirmation ultimately fails?

| Tradeoff | Detail |
|:---|:---|
| **UX honesty** | "We're confirming" sets correct expectations; "Order placed" followed by a later cancellation is worse. |
| **Product involvement** | The timeout window, UI copy, and failure-recovery flow must be defined by product, not engineering alone. |
| **Durable state** | The pending order must survive service restarts — a queue or outbox table, not in-memory state. |
| **Compensation** | If inventory confirmation ultimately fails after payment succeeded, a compensating refund must be triggered. |

> **Also see**: [tx-09 Saga Orchestration](transaction-patterns.md#tx-09-saga-orchestration-for-checkout), [tx-10 Compensating Transactions](transaction-patterns.md#tx-10-compensating-transactions)
> **Dictionary**: [Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern), [Compensating Transaction](../../reference-dictionary/data-concurrency.md#compensating-transaction)
> **Azure**: Azure Service Bus sessions or Event Grid for async order confirmation; Durable Functions for saga state management.

---

## tx-41: Impossible-State Prevention as Architectural Driver

> **Source**: [Amazon: 1 Million Users Clicked Checkout At Once](../../articles/concurrency-transactions/amazon-million-users-checkout-scaling.md)

| | |
|:---|:---|
| **Problem** | At scale, components disagree: the payment service thinks the order succeeded, inventory disagrees, a queue retries, a cleanup job releases a reservation. Every component believes it made the correct decision — but the aggregate state is inconsistent. |
| **Root cause** | Distributed systems produce disagreement by default. Without explicit safeguards, the system arrives at states that should be impossible: negative inventory, orders for nonexistent products, customers charged twice. |

**Strategy**: High-traffic checkout systems are designed primarily around preventing impossible states, not maximizing throughput. The architecture — reservations, idempotency keys, saga patterns, queue-based workflows, eventual consistency, cleanup jobs — exists to ensure the business ends up with exactly one version of the truth. Design each component by asking: "What state must never exist?" and build the guardrail that prevents it.

| Tradeoff | Detail |
|:---|:---|
| **Design inversion** | Start from the impossible states, not the happy path. The happy path is easy; the edge cases are the system. |
| **Cross-component** | Impossible states often span services — no single service's correctness guarantee is sufficient. |
| **Observability** | Impossible states must be detectable. If you can't monitor for them, you can't be confident they're prevented. |
| **Simplicity** | Fewer components disagreeing = fewer impossible states. Decouple only when necessary. |

> **Also see**: [tx-36 Layered Flash-Sale Defense](30-tx-key-takeaways.md#tx-36-layered-flash-sale-defense-architecture), [tx-01 Double-Booking](concurrency-transactions.md#tx-01-double-booking)
> **Dictionary**: [Overselling](../../reference-dictionary/data-concurrency.md#overselling), [Double-Booking Problem](../../reference-dictionary/data-concurrency.md#double-booking-problem), [Impossible State](../../reference-dictionary/data-concurrency.md#impossible-state)

---
