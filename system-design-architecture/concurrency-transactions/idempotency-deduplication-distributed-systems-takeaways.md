---
type: System Design
title: "Idempotency & Deduplication in Distributed Systems — Key Takeaways"
description: "Reusable patterns from a system-design article on idempotency and deduplication: the three-layer defense model, idempotency keys with unique constraints, upsert-based idempotency, state-based guard conditions, SET-over-INCREMENT design, and the true scope of exactly-once semantics."
timestamp: 2026-07-25T00:00:00Z
---

# 47. Idempotency & Deduplication in Distributed Systems — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md) — Nidhi Jain, Level Up Coding, 2026

> **Also see**: [Concurrency & Transactions](concurrency-transactions.md) (tx-04 Idempotency), [Idempotency in Event-Driven Systems](idempotency-event-driven-system-takeaways.md) (tx-48–tx-52), [Idempotency Hidden Costs](idempotency-hidden-costs.md) (tx-13–tx-18)
> **Dictionary**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Idempotency Key](../../reference-dictionary/cqrs-event-driven.md#idempotency-key), [Idempotent Consumer](../../reference-dictionary/messaging.md#idempotent-consumer), [Idempotent Producer](../../reference-dictionary/messaging.md#idempotent-producer), [At-Least-Once Semantics](../../reference-dictionary/messaging.md#at-least-once-semantics), [Exactly-Once Semantics](../../reference-dictionary/messaging.md#exactly-once-semantics), [Deduplication Window](../../reference-dictionary/messaging.md#deduplication-window), [Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern), [Distributed Lock](../../reference-dictionary/data-concurrency.md#distributed-lock), [Upsert](../../reference-dictionary/databases.md#upsert), [Two Generals Problem](../../reference-dictionary/architecture-patterns.md#two-generals-problem), [Deterministic Processing](../../reference-dictionary/architecture-patterns.md#deterministic-processing)
> **Taxonomy Reference**: §2.3 Concurrency & Asynchronous Processing

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [tx-53](#tx-53) | At-least-once delivery makes duplicates inevitable in production | Three-layer defense model: infrastructure → application → critical operations |
| [tx-54](#tx-54) | Consumer crashes between processing and acknowledging create duplicate deliveries | Idempotency keys with DB unique constraints turn duplicates into harmless constraint violations |
| [tx-55](#tx-55) | INSERT-or-fail is not suitable when state should be overwritten on replay | Upserts (INSERT ON CONFLICT DO UPDATE) provide replay-safe writes without errors |
| [tx-56](#tx-56) | Relative state changes amplify on retry, doubling counters and balances | Prefer SET over INCREMENT — absolute state is naturally idempotent |
| [tx-57](#tx-57) | Non-deterministic logic breaks event replay and violates idempotency guarantees | Deterministic processing: replace NOW() with event timestamps, UUID() with idempotency keys |
| [tx-58](#tx-58) | Truly non-idempotent operations (payments, SMS, webhooks) need external coordination | Distributed locks (Redis SETNX) and Saga pattern protect critical one-time actions |

---

## tx-53: The Three-Layer Defense Model for Duplicate Handling

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | A system relying on a single deduplication mechanism (e.g., only DB constraints or only Redis) fails under scale because each layer has distinct failure modes that the other cannot cover. |
| **Root cause** | No single layer is both fast enough for high-throughput filtering and durable enough to guarantee correctness across all failure scenarios. |

**Strategy**: Stack three complementary layers, each covering the gaps of the others:

| Layer | Mechanism | Latency | Failure Mode |
|:---|:---|:---|:---|
| **Infrastructure** | SQS FIFO dedup, Kafka idempotent producer, Kafka EOS | Broker-level | Only prevents producer-side duplicates; doesn't cover consumer crashes |
| **Application** | Idempotency keys, upserts, guard conditions, SET-over-INCREMENT | ~1–10ms | Requires developer discipline; must be designed into every consumer |
| **Critical Operations** | Redis SETNX distributed locks, Saga with compensating transactions | <1ms (lock check) | Adds external dependency; requires TTL tuning and rollback paths |

**Tradeoff**: Three layers add operational complexity but provide defense in depth — each layer catches what the layers above it miss. Infrastructure reduces volume, application makes remaining duplicates harmless, and critical-operation patterns protect the truly non-idempotent actions.

> **Dictionary**: [Idempotent Producer](../../reference-dictionary/messaging.md#idempotent-producer), [Deduplication Window](../../reference-dictionary/messaging.md#deduplication-window), [Exactly-Once Semantics](../../reference-dictionary/messaging.md#exactly-once-semantics)
> **Azure**: Service Bus duplicate detection (infrastructure layer); Azure Cache for Redis SETNX (critical operations layer)

---

## tx-54: Idempotency Keys with Unique Constraints

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | A consumer receives a duplicate event after crashing mid-processing. Without deduplication, it re-executes business logic — potentially charging a customer twice or inserting duplicate rows. |
| **Root cause** | The gap between "work done" and "acknowledgment sent" cannot be closed at the infrastructure level — the broker must redeliver unacknowledged messages. |

**Strategy**: Assign every message a unique business identifier (`idempotencyKey`). Before processing, attempt to insert this key into a deduplication table with a unique constraint. If the insert succeeds, proceed. If it violates the constraint, the message has already been processed — skip it.

```
Receive event with idempotencyKey = "evt-abc123"
  → INSERT INTO idempotency_store (key, status, created_at)
    VALUES ('evt-abc123', 'processing', NOW())
  ├─ UNIQUE constraint violation → DUPLICATE, return success (already processed)
  └─ Insert succeeds → Process business logic → Update status to 'completed'
```

The unique constraint serializes concurrent attempts: if two consumers race on the same key, exactly one insert succeeds. The loser catches the constraint violation and knows the work is already done or in progress.

**Tradeoff**: Requires an additional DB table and a write on every message. For high-throughput systems, the idempotency store can become a bottleneck — partition by `idempotencyKey` hash and apply TTL-based cleanup to bound storage.

> **Dictionary**: [Idempotency Key](../../reference-dictionary/cqrs-event-driven.md#idempotency-key), [Idempotent Consumer](../../reference-dictionary/messaging.md#idempotent-consumer)
> **Azure**: Cosmos DB unique key constraints on `/idempotencyKey`; Azure SQL `UNIQUE` constraint with `IGNORE_DUP_KEY`

---

## tx-55: Upsert-Based Idempotency for Replay-Safe Writes

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | INSERT-or-fail idempotency rejects duplicates with errors, but some workloads require replay to overwrite state safely — for example, reprocessing an order confirmation should update the order to CONFIRMED, not fail because the row already exists. |
| **Root cause** | INSERT-only idempotency conflates "this event was seen before" with "this event should not be applied again." These are different: the first is about deduplication, the second is about correctness of the final state. |

**Strategy**: Replace `INSERT` with `INSERT ... ON CONFLICT DO UPDATE` (upsert). The first execution inserts a new row. Subsequent executions find the conflict and update to the same target state — no error, no duplicate row.

```sql
INSERT INTO orders (order_id, status, amount, updated_at)
VALUES ('ord-456', 'CONFIRMED', 99.99, NOW())
ON CONFLICT (order_id) DO UPDATE
SET status = EXCLUDED.status,
    amount = EXCLUDED.amount,
    updated_at = EXCLUDED.updated_at;
```

The key insight: upsert idempotency works when the target state is stable across replays. If `EXCLUDED.status` were a computed value that changed between retries, upsert would not guarantee correctness.

**Tradeoff**: Upserts are idempotent only when the target values are deterministic given the event payload. If the event carries a timestamp that changes between retries or a computed field, the upsert can produce different results on each replay — violating idempotency. Always verify that all `EXCLUDED.*` values are derived solely from the immutable event data.

> **Dictionary**: [Upsert](../../reference-dictionary/databases.md#upsert), [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency)
> **Azure**: Cosmos DB upsert via SDK; Azure SQL `MERGE` statement or `INSERT ... ON CONFLICT`

---

## tx-56: SET over INCREMENT — Designing for Natural Idempotency

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | A `LikeAdded` event processed twice via `UPDATE counter = counter + 1` inflates the like count by 2. Relative operations amplify on every retry — the error compounds with each duplicate delivery. |
| **Root cause** | Relative state changes (`counter + 1`, `balance - 100`) are non-idempotent by nature. The operation depends on the current state, which changes between the first execution and the retry. |

**Strategy**: Restructure operations to record absolute facts rather than relative changes. An absolute fact is idempotent — recording it once or ten times produces the same final state.

| Non-Idempotent (Relative) | Idempotent (Absolute) |
|:---|:---|
| `UPDATE posts SET like_count = like_count + 1` | `INSERT INTO likes (user_id, post_id) VALUES (42, 789)` |
| `UPDATE account SET balance = balance - 100` | `INSERT INTO withdrawals (txn_id, account_id, amount) VALUES ('txn-001', 42, 100)` |
| `UPDATE inventory SET qty = qty - 1` | `INSERT INTO reservations (reservation_id, sku, qty) VALUES ('res-001', 'SKU-A', 1)` |

The count becomes a derived value: `SELECT COUNT(*) FROM likes WHERE post_id = 789`. The balance becomes `SUM(amount) FROM withdrawals`. Duplicate inserts are rejected by unique constraints on `(user_id, post_id)` or `txn_id`.

**Tradeoff**: Absolute-state design requires more storage (an event/ledger table per fact type) and shifts computation to read time. However, it eliminates an entire class of idempotency bugs and makes the system auditable — every fact is traceable to a specific event.

> **Dictionary**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Event Sourcing](../../reference-dictionary/cqrs-event-driven.md#event-sourcing)
> **Azure**: Cosmos DB with unique keys on composite business identifiers

---

## tx-57: Deterministic Processing for Replay Safety

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | An event replay pipeline produces different results each time because processing logic uses `NOW()`, `UUID()`, or external API calls — breaking the guarantee that the same input always yields the same output. |
| **Root cause** | Non-deterministic functions inject ambient state (current time, random values, network responses) into the processing path. On replay, that ambient state differs, so the output differs. |

**Strategy**: Eliminate all non-deterministic functions from the event processing path. Every value must be derived from the event payload itself.

| Non-Deterministic | Deterministic Replacement |
|:---|:---|
| `created_at = NOW()` | `created_at = event.timestamp` |
| `id = UUID()` | `id = event.idempotency_key` |
| `user_name = userService.getName(userId)` | `user_name = event.user_name` (carried in event) |
| `result = callExternalAPI(payload)` | Cache external results; replay from event-carried snapshot |

**Tradeoff**: Deterministic processing requires events to carry all data needed for processing (event-carried state transfer). This increases event size and couples consumers to the producer's schema. However, it makes event replay a reliable recovery mechanism — re-processing the same event stream always produces the same final state.

> **Dictionary**: [Deterministic Processing](../../reference-dictionary/architecture-patterns.md#deterministic-processing), [Event Carried State Transfer](../../reference-dictionary/cqrs-event-driven.md#event-carried-state-transfer)
> **Azure**: Event Hubs Capture for long-term event retention enabling historical replay

---

## tx-58: Protecting Critical Non-Idempotent Operations

> **Source**: [Idempotency and Deduplication in Distributed Systems](../../articles/concurrency-transactions/idempotency-deduplication-distributed-systems.md)

| | |
|:---|:---|
| **Problem** | Some operations cannot be restructured to be idempotent — charging a credit card, sending an SMS, or triggering a one-time webhook. If a duplicate event reaches these operations, the side effect occurs twice with real-world consequences (double charge, spam). |
| **Root cause** | External side effects are inherently non-idempotent because the external system (payment gateway, SMS provider) does not expose an idempotent interface, and you cannot reverse a sent SMS. |

**Strategy**: Use two complementary patterns for truly non-idempotent actions:

**Distributed Lock (Redis SETNX)**: Before executing the critical operation, acquire an exclusive lock keyed on the business identifier with a TTL. Only the lock holder proceeds.

```
Receive payment event for txn-789
  → Redis SET payment:txn-789 "processing" NX EX 60
    ├─ false → Another instance is handling this, skip
    └─ true  → Charge payment → Send confirmation → DEL payment:txn-789
```

The TTL must exceed the maximum expected processing time. If the consumer crashes, the TTL ensures the lock eventually releases.

**Saga Pattern**: For multi-step workflows (charge → reserve → confirm), decompose into sequential steps, each with a defined compensating action.

| Step | Forward Action | Compensating Action |
|:---|:---|:---|
| 1. Charge payment | `POST /payments` | `POST /payments/{id}/refund` |
| 2. Reserve inventory | `POST /reservations` | `DELETE /reservations/{id}` |
| 3. Send confirmation | `POST /notifications` | (Cannot undo; send correction notice) |

If step 2 fails, compensating transactions undo step 1. No distributed lock held across services — each step completes independently.

**Tradeoff**: Distributed locks add Redis as a critical dependency and require careful TTL tuning. Sagas add operational complexity (compensating actions must be tested, monitored, and guaranteed to eventually succeed). However, for payment, notification, and external-integration use cases, these patterns are the only way to safely handle duplicates when the operation itself cannot be made idempotent.

> **Dictionary**: [Distributed Lock](../../reference-dictionary/data-concurrency.md#distributed-lock), [Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern)
> **Azure**: Azure Cache for Redis for SETNX-based locks; Durable Functions for saga orchestration with compensating actions
