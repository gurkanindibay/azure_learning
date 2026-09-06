---
type: System Design
title: "Concurrency & Transactions — Flash-Sale Inventory Takeaways"
description: "Race conditions, atomic updates, Redis edge protection, queue serialization, and multi-region inventory strategies for flash-sale overselling prevention."
generated: { by: process:okf-migrate, at: 2026-07-18T00:00:00Z }
---

# 30. Concurrency & Transactions — Flash-Sale Inventory Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [System Design Interview: How Would You Avoid Overselling Inventory During a Flash Sale?](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)
> **Related**: [Atomic Inventory Reservation](transaction-patterns.md#tx-08-atomic-inventory-reservation), [Database Invariants](concurrency-transactions.md#tx-06-database-invariants-over-lock-timeouts)
> **Dictionary**: [Atomic Conditional Update](../../reference-dictionary/data-concurrency.md#atomic-conditional-update), [Inventory Reservation](../../reference-dictionary/data-concurrency.md#inventory-reservation), [Overselling](../../reference-dictionary/data-concurrency.md#overselling), [Race Condition](../../reference-dictionary/concurrency-runtimes.md#race-condition), [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Flash Sale](../../reference-dictionary/architecture-patterns.md#flash-sale)
> **Taxonomy Reference**: §2.3 Concurrency & Asynchronous Processing

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [tx-31](#tx-31-redis-edge-protection-for-flash-sale-traffic) | Every request hits the DB during a spike | Redis edge protection (traffic shaping) |
| [tx-32](#tx-32-queue-based-serialization-for-inventory-contention) | Concurrent DB writes create lock contention at scale | Queue-based serialization |
| [tx-33](#tx-33-reservation-payment-decoupling-with-expiry) | Payment failures permanently consume reserved stock | Reservation-payment decoupling with TTL |
| [tx-34](#tx-34-idempotency-token-for-duplicate-purchase-prevention) | Users clicking Buy Now multiple times create duplicate orders | Idempotency tokens for purchase requests |
| [tx-35](#tx-35-multi-region-inventory-consistency) | Global inventory shared across regions | Multi-region inventory partitioning |
| [tx-36](#tx-36-layered-flash-sale-defense-architecture) | No single layer prevents all overselling scenarios | Layered defense architecture |

---

## tx-31: Redis Edge Protection for Flash-Sale Traffic

> **Source**: [§"The Interview Trap" and §"Redis Atomic Decrement"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | During a flash sale, 100K requests compete for 100 items. Even if the database correctly rejects 99.9K requests with atomic conditional updates, processing every request still creates enormous DB pressure. |
| **Root cause** | The database is both the source of truth and the sole gatekeeper, so every request — including those with zero chance of success — must reach it. |

**Strategy**: Preload inventory into Redis before the sale and use `DECR` (atomic decrement) as a fast first gate. Only requests that pass the Redis check proceed to the queue and database. Redis serves as a traffic-shaping layer, not the source of truth.

| Tradeoff | Detail |
|:---|:---|
| **Latency** | Redis rejects impossible requests in sub-millisecond time vs. full DB round-trip. |
| **Consistency** | Redis is eventually consistent with the database; if Redis crashes mid-sale, the DB remains authoritative once recovered. |
| **Complexity** | Adds a cache invalidation and reconciliation path between Redis and the database. |

> **Also see**: [tx-08 Atomic Inventory Reservation](transaction-patterns.md#tx-08-atomic-inventory-reservation)
> **Dictionary**: [Cache-Aside Pattern](../../reference-dictionary/caching.md#cache-aside), [Overselling](../../reference-dictionary/data-concurrency.md#overselling)
> **Azure**: Azure Cache for Redis with active geo-replication; combine with Azure SQL for the authoritative inventory store.

---

## tx-32: Queue-Based Serialization for Inventory Contention

> **Source**: [§"The Next Scaling Problem" and §"Queue-Based Processing"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | When thousands of concurrent buyers compete for the same limited inventory, direct database access creates row-level lock contention on hot SKUs. Even atomic updates serialize at the DB level, creating a throughput bottleneck. |
| **Root cause** | Unrestricted concurrent access to a shared mutable row means every request contends for the same database lock, turning the DB into a serialization point under load. |

**Strategy**: Place a message queue (e.g., Kafka) between the edge and the database. Purchase requests enter the queue and workers process them sequentially per partition, dramatically reducing lock contention. The queue provides back-pressure and fairness guarantees.

| Tradeoff | Detail |
|:---|:---|
| **Throughput** | Sequential processing per partition reduces contention but adds queue latency (milliseconds). |
| **Correctness** | For flash sales, correctness matters more than shaving off milliseconds — selling the 101st item is worse than a slightly slower response. |
| **Scale** | Partition by product SKU so contention for different products is isolated. |

> **Also see**: [tx-06 Database Invariants](concurrency-transactions.md#tx-06-database-invariants-over-lock-timeouts)
> **Dictionary**: [Message Queue](../../reference-dictionary/messaging.md#message-queue), [Backpressure](../../reference-dictionary/messaging.md#backpressure)
> **Azure**: Azure Event Hubs or Service Bus for the queue layer; Azure Functions or AKS for workers.

---

## tx-33: Reservation-Payment Decoupling with Expiry

> **Source**: [§"Inventory Reservation," §"Reservation Workflow," and §"Reservation Expiry"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | If inventory is permanently deducted before payment succeeds, a failed payment leaves inventory unavailable (sold to nobody). If inventory is deducted only after payment, two buyers can pay for the last item simultaneously. |
| **Root cause** | Payment is an external, slow, potentially-failing operation that cannot be part of the same atomic transaction as inventory deduction. |

**Strategy**: Introduce a temporary **reservation** state. Inventory moves from available → reserved atomically (via conditional update). Payment then proceeds independently. If payment succeeds, reserved → sold. If payment fails or times out (e.g., 10-minute TTL), reserved → available. The reservation expiry prevents abandoned checkouts from permanently locking inventory.

| Tradeoff | Detail |
|:---|:---|
| **Availability** | Reserved-but-unpaid inventory is unavailable to other buyers during the TTL window, reducing effective stock during high-traffic periods. |
| **TTL tuning** | Too short: legitimate buyers lose reservations before completing payment. Too long: abandoned carts hold inventory hostage. |
| **Reconciliation** | Requires a background job or scheduled task to release expired reservations reliably. |

> **Also see**: [tx-08 Atomic Inventory Reservation](transaction-patterns.md#tx-08-atomic-inventory-reservation), [tx-09 Saga Orchestration for Checkout](transaction-patterns.md#tx-09-saga-orchestration-for-checkout)
> **Dictionary**: [Inventory Reservation](../../reference-dictionary/data-concurrency.md#inventory-reservation), [Saga Pattern](../../reference-dictionary/cqrs-event-driven.md#saga-pattern)
> **Azure**: Azure SQL Database with row-level locking for the reservation table; Azure Durable Functions for saga orchestration and expiry scheduling.

---

## tx-34: Idempotency Token for Duplicate Purchase Prevention

> **Source**: [§"Preventing Duplicate Purchases"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | A user clicks Buy Now multiple times, refreshes the page, or a network retry sends duplicate purchase requests. Without protection, each attempt creates a new reservation or order. |
| **Root cause** | The purchase endpoint is not idempotent — identical requests produce new side effects instead of returning the same result. |

**Strategy**: Each purchase request carries a unique idempotency key (e.g., `OrderId` or purchase token). The server records the key with its outcome before processing. Duplicate requests with the same key return the cached result instead of creating a new reservation or charge.

| Tradeoff | Detail |
|:---|:---|
| **Key scope** | Keys must be unique per user-intent, not per HTTP request. A page refresh should reuse the same key. |
| **State management** | Idempotency records need a retention policy; keeping them forever accumulates storage, deleting them too early allows replays. |
| **Pending state** | While the first request is in-flight, duplicates must either block or receive a "processing" response — not silently create a second reservation. |

> **Also see**: [tx-23 Atomic Idempotency-Key Persistence](29-tx-key-takeaways.md#tx-23-atomic-idempotency-key-persistence), [tx-24 Idempotency State Lifecycle](29-tx-key-takeaways.md#tx-24-idempotency-state-lifecycle)
> **Dictionary**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Idempotency Key](../../reference-dictionary/api-design.md#idempotency-key)
> **Azure**: Use Azure Cosmos DB with unique-key constraints for idempotency-key storage; combine with Azure API Management for idempotency header enforcement.

---

## tx-35: Multi-Region Inventory Consistency

> **Source**: [§"Multi-Region Challenge"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | Inventory is sold globally from multiple regions (US, Europe, Asia). Each region has its own application instances and potentially its own database. Ensuring global `Total Sold ≤ Total Inventory` requires cross-region coordination. |
| **Root cause** | Inventory is globally shared mutable state. Regional databases cannot independently enforce a global invariant without some form of cross-region synchronization. |

**Strategy**: Choose one of three approaches based on consistency requirements: (1) **Inventory partitioning** — allocate a fixed quota to each region upfront; regions operate independently within their quota. (2) **Centralized allocation** — a single global inventory service serializes all deductions. (3) **Inventory tokens** — pre-generate N tokens representing N items; regions claim tokens and a token can only be claimed once globally.

| Tradeoff | Detail |
|:---|:---|
| **Partitioning** | Simple and fast but can waste inventory if one region undersells while another is sold out. |
| **Centralized** | Guarantees correctness but introduces cross-region latency and a single point of failure. |
| **Tokens** | Balances distribution and correctness but requires token generation and global uniqueness enforcement. |

> **Also see**: [tx-12 Strong vs Eventual Consistency by Subdomain](transaction-patterns.md#tx-12-strong-vs-eventual-consistency-by-subdomain)
> **Dictionary**: [CAP Theorem](../../reference-dictionary/data-concurrency.md#cap-theorem), [Distributed Transactions](../../reference-dictionary/data-concurrency.md#distributed-transactions)
> **Azure**: Azure Cosmos DB with multi-region writes for token storage; Azure Front Door for global routing.

---

## tx-36: Layered Flash-Sale Defense Architecture

> **Source**: [§"The Real Production Design" and §"Lets Conclude"](../../articles/concurrency-transactions/avoid-overselling-inventory-flash-sale.md)

| | |
|:---|:---|
| **Problem** | No single mechanism (atomic update, queue, Redis, or idempotency alone) prevents all overselling scenarios at flash-sale scale. Each layer addresses a different failure mode, and all are needed together. |
| **Root cause** | Overselling is not caused by one failure — it can happen at the edge (too many requests), at the queue (contention), at the database (race conditions), at payment (failed charges), or at the client (duplicate submissions). |

**Strategy**: Deploy a layered defense:

1. **Redis edge layer** — Reject impossible purchases early (100 units, 100K requests → 99.9K rejected at edge).
2. **Queue layer** — Serialize the surviving requests to reduce DB contention.
3. **Reservation layer** — Atomically reserve inventory with conditional updates; decouple from payment.
4. **Database layer** — Maintain authoritative inventory state with ACID guarantees.
5. **Idempotency layer** — Prevent duplicate purchases from retries and refreshes.

| Tradeoff | Detail |
|:---|:---|
| **Complexity** | Five layers mean five things to monitor, tune, and debug. |
| **Latency** | Each layer adds overhead, but the alternative — overselling — is catastrophic for customer trust. |
| **Cost** | Additional infrastructure (Redis, queue, idempotency store) increases operational cost. |

> **Also see**: All tx-31 through tx-35 above; [tx-25 Layered Duplicate Protection](45-tx-key-takeaways.md#tx-25-business-vs-retry-identity)
> **Dictionary**: [Flash Sale](../../reference-dictionary/architecture-patterns.md#flash-sale), [Defense in Depth](../../reference-dictionary/security-iam.md#defense-in-depth)
> **Azure**: Azure Cache for Redis → Event Hubs → Azure SQL (with row-level locking) → Cosmos DB (idempotency); Azure Monitor for cross-layer observability.
