---
type: System Design
title: "API Idempotency Under High Concurrency — Key Takeaways"
description: "Architectural patterns for guaranteeing API idempotency at scale: token-based validation, Redis atomic Lua scripts, optimistic locking, state machines, and defense-in-depth strategies."
timestamp: 2026-07-03T00:00:00Z
---

# API Idempotency Under High Concurrency — Key Takeaways

> **Parent**: [API & Network Design Reference](index.md)
> **Source**: [How to Guarantee API Idempotency Under High Concurrency](../../articles/api-network/api-idempotency-high-concurrency.md) — by Umesh Kumar Yadav (Jun 2026)
> **Purpose**: Extract reusable patterns for implementing idempotency in distributed systems, from frontend safeguards to server-side atomic operations under high concurrency.

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`apipat-13`](#apipat-13-idempotency-as-a-business-guarantee) | Duplicate requests corrupt financial data | Idempotency is a business guarantee, not just a technical nicety |
| [`apipat-14`](#apipat-14-frontend-vs-backend---defense-in-depth) | Frontend-only protection leaves backend exposed | PRG pattern + button disabling as UX layer; never the sole safeguard |
| [`apipat-15`](#apipat-15-unique-business-identifiers--database-constraints) | How to detect duplicates at the data layer | Request ID + unique constraint as the simplest server-side idempotency |
| [`apipat-16`](#apipat-16-state-machine-for-idempotent-transitions) | Same operation applied to wrong state | State machine prevents invalid transitions (PAID→PAID rejected) |
| [`apipat-17`](#apipat-17-optimistic-locking-for-concurrent-idempotency) | Concurrent writes to same resource cause race conditions | Version-column UPDATE with WHERE version = ? — only one succeeds |
| [`apipat-18`](#apipat-18-redis-atomic-lua-scripts-for-token-based-idempotency) | Token check-then-delete is not atomic under concurrency | Redis Lua scripts combine validation + deletion into one atomic operation |

---

## apipat-13: Idempotency as a Business Guarantee

| | |
|:---|:---|
| **Problem** | A customer clicks "Pay Now" three times because the page is frozen. Without idempotency, they're charged three times — a business-level failure, not just a technical bug. Duplicate orders, double payments, and corrupted financial data are the direct consequences. |
| **Root cause** | Idempotency is often treated as an afterthought ("we'll handle retries later") rather than as a first-class design principle. In distributed systems, at-least-once delivery is the norm (Kafka, RabbitMQ, network retries), making idempotency unavoidable. |

**Strategy**: Treat idempotency as a **business guarantee** — the system must ensure that executing an operation N times produces the same outcome as executing it once. This means every mutating operation needs a unique identifier (transaction ID, request ID, idempotency key) and a deduplication mechanism that spans the entire request lifecycle.

**Tradeoff**: Idempotency adds complexity — every endpoint must carry a unique key, every service must implement deduplication, and token generation adds latency. But for financial, payment, and order systems, this cost is non-negotiable.

> **Also see**: [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key), [API Idempotency](../../reference-dictionary/cqrs-event-driven.md#api-idempotency)
> **Dictionary**: [API Design](../../reference-dictionary/api-design.md), [CQRS & Event-Driven](../../reference-dictionary/cqrs-event-driven.md)
> **Azure Services**: [Azure API Management](../../architecture-azure/integration/)
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging

---

## apipat-14: Frontend vs Backend — Defense in Depth

| | |
|:---|:---|
| **Problem** | Developers often stop at disabling the submit button after click — but this only prevents double-clicks from the same browser tab. It does nothing against network retries, multiple browser tabs, mobile app retries, or message queue redelivery. |
| **Root cause** | Frontend controls operate at the presentation layer — they improve UX but have no authority over what reaches the server. Network proxies, load balancers, service meshes, and message brokers can all introduce duplicate requests independently of the UI. |

**Strategy**: Implement a layered defense:
1. **Frontend layer** (UX): Disable buttons after click, show loading spinner, use PRG pattern (POST → Redirect → GET) to prevent form resubmission on refresh.
2. **Gateway layer**: Rate limiting per user/API key to reduce duplicate volume.
3. **Server layer** (authoritative): Token-based idempotency, unique business identifiers, state machines, and optimistic locking — these are the only layers that can actually prevent duplicate execution.

**Tradeoff**: The PRG pattern requires an extra HTTP round-trip (POST → 302 → GET) and server-side session state for the redirect target. For SPAs and mobile apps, the PRG pattern is less relevant — token-based idempotency is the primary mechanism.

> **Also see**: [API Idempotency](../../reference-dictionary/cqrs-event-driven.md#api-idempotency)
> **Dictionary**: [API Design](../../reference-dictionary/api-design.md)
> **Azure Services**: [Azure Front Door](../../architecture-azure/networking/)
> **Taxonomy Reference**: §2.1 Application Architecture Patterns

---

## apipat-15: Unique Business Identifiers + Database Constraints

| | |
|:---|:---|
| **Problem** | How does the server know if a request has already been processed? Without a unique identifier per request, the server has no way to distinguish between a legitimate retry and a genuine new request. |
| **Root cause** | HTTP is stateless — each request arrives independently. The server needs an explicit deduplication key that the client provides with every mutating request. |

**Strategy**: Require every mutating API call to carry a globally unique identifier — `OrderNo`, `TransactionId`, `RequestId`, or `Idempotency-Key`. The server stores processed IDs in a deduplication table with a unique constraint. Before executing business logic, check `WHERE request_id = ?` — if a row exists, return the cached result instead of re-executing.

**Tradeoff**: The deduplication table grows indefinitely; implement TTL-based cleanup (e.g., expire IDs after 24 hours). For payment gateways and ERP integrations, use the business's natural key (order number, transaction reference) rather than a synthetic token — this aligns with external system expectations.

> **Also see**: [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key)
> **Dictionary**: [API Design](../../reference-dictionary/api-design.md), [Databases](../../reference-dictionary/databases.md)
> **Azure Services**: [Azure SQL](../../architecture-azure/data/), [Cosmos DB](../../architecture-azure/data/databases/azure_cosmosdb/)
> **Taxonomy Reference**: §2.1 Application Architecture Patterns

---

## apipat-16: State Machine for Idempotent Transitions

| | |
|:---|:---|
| **Problem** | Even with unique request IDs, a duplicate payment request arriving after the order has already been shipped should not re-execute the payment logic. The operation's validity depends on the current state of the entity. |
| **Root cause** | Request-level deduplication alone doesn't enforce business rules — it only prevents re-execution of the same request ID. A state transition (e.g., PAID → SHIPPED) needs its own guard. |

**Strategy**: Model business entities as state machines. Define valid transitions explicitly — e.g., `CREATED → PAID → SHIPPED → COMPLETED`. When a payment request arrives for an order that's already `PAID`, the transition `PAID → PAID` is invalid, and the request is rejected regardless of its idempotency key. This is idempotency at the **business logic** layer.

**Tradeoff**: State machines add upfront modeling effort and must be kept in sync with evolving business processes. But for payment, order, and fulfillment workflows where incorrect state transitions cause real financial damage, the cost is justified.

> **Also see**: [Optimistic Locking](#apipat-17-optimistic-locking-for-concurrent-idempotency), [CQRS & Event Sourcing](../../reference-dictionary/cqrs-event-driven.md)
> **Dictionary**: [CQRS & Event-Driven](../../reference-dictionary/cqrs-event-driven.md), [Data Concurrency](../../reference-dictionary/data-concurrency.md)
> **Taxonomy Reference**: §2.1 Application Architecture Patterns

---

## apipat-17: Optimistic Locking for Concurrent Idempotency

| | |
|:---|:---|
| **Problem** | Two concurrent requests to decrement inventory (stock: 10 → 9) both read stock=10, both compute stock=9, and both write stock=9 — losing one deduction. This is the classic lost-update problem under concurrency. |
| **Root cause** | Read-then-write without a concurrency control mechanism allows interleaving. Neither request sees the other's changes because they operate on the same snapshot. |

**Strategy**: Use optimistic locking with a `version` column. The UPDATE statement includes `WHERE version = ?` and increments the version atomically:
```sql
UPDATE product
SET stock = stock - 1, version = version + 1
WHERE id = ? AND version = ?
```
Only one of two concurrent requests succeeds — the other sees zero rows affected and must retry (re-read + re-attempt). This guarantees that each deduction is applied exactly once, even under high concurrency.

**Tradeoff**: Under extreme contention (100+ concurrent requests on the same row), retry storms can degrade throughput. For hot rows (flash sale items), consider pessimistic locking or a queue-based approach. Also, optimistic locking works at the database level — it doesn't prevent duplicate API calls from reaching the database in the first place; pair it with token-based idempotency.

> **Also see**: [Token-Based Idempotency](../../reference-dictionary/cqrs-event-driven.md#token-based-idempotency), [State Machine](#apipat-16-state-machine-for-idempotent-transitions)
> **Dictionary**: [Data Concurrency](../../reference-dictionary/data-concurrency.md), [Databases](../../reference-dictionary/databases.md)
> **Azure Services**: [Azure SQL](../../architecture-azure/data/), [Cosmos DB](../../architecture-azure/data/databases/azure_cosmosdb/) (optimistic concurrency via _etag)
> **Taxonomy Reference**: §7.1 Reliability & Resilience

---

## apipat-18: Redis Atomic Lua Scripts for Token-Based Idempotency

| | |
|:---|:---|
| **Problem** | Under high concurrency, a simple token check-then-delete in application code is not atomic. Thread A checks the token exists, Thread B checks the token exists (before A deletes it), both pass validation, and both execute business logic — duplicate processing. |
| **Root cause** | The read (GET token) and write (DEL token) are two separate Redis commands with a race window between them. Application-level locks add latency and complexity. |

**Strategy**: Use a Redis Lua script that atomically checks and deletes the token in a single operation:
```lua
if redis.call('get', KEYS[1]) == KEYS[2] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```
Redis executes Lua scripts as a single atomic unit — no other command can interleave. For token generation, use ULID (Universally Unique Lexicographically Sortable Identifier) for time-sortable, globally unique tokens with a short TTL (5 minutes).

**Tradeoff**: Redis becomes a critical dependency — if Redis is unavailable, all mutating operations are blocked. Mitigate with Redis Cluster (high availability) and a fallback to database-level unique constraints (degraded but still safe). Also, Lua scripts must be kept simple — complex scripts block the Redis event loop.

> **Also see**: [Unique Business Identifiers](#apipat-15-unique-business-identifiers--database-constraints), [Optimistic Locking](#apipat-17-optimistic-locking-for-concurrent-idempotency)
> **Dictionary**: [Caching](../../reference-dictionary/caching.md), [API Design](../../reference-dictionary/api-design.md)
> **Azure Services**: [Azure Cache for Redis](../../architecture-azure/data/), [Event Hubs](../../architecture-azure/integration/event-hubs/)
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging, §7.1 Reliability & Resilience

---

## Cross-References

- **Related System Design Files**: [API Design Patterns](api-design-patterns.md), [REST API Senior Patterns](rest-api-senior-patterns.md), [Concurrency & Transactions](../concurrency-transactions/concurrency-transactions.md), [Resilience Patterns](../resilience/resilience-patterns.md)
- **Dictionary Terms**: [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key), [API Idempotency](../../reference-dictionary/cqrs-event-driven.md#api-idempotency), [Token-Based Idempotency](../../reference-dictionary/cqrs-event-driven.md#token-based-idempotency), [Optimistic Locking](../../reference-dictionary/data-concurrency.md#optimistic-locking), [PRG Pattern](../../reference-dictionary/api-design.md#prg-pattern)
- **Azure Services**: [Azure Cache for Redis](../../architecture-azure/data/), [Azure SQL](../../architecture-azure/data/), [Azure API Management](../../architecture-azure/integration/)
