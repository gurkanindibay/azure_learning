---
type: Index
title: "Concurrency & Transactions"
description: "System-design problems and strategies for distributed concurrency, transaction isolation, idempotency, and causal consistency."
timestamp: 2026-06-27T00:00:00Z
---

# Concurrency & Transactions

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for handling concurrent operations, distributed transactions, isolation levels, idempotency, and causal ordering in distributed systems.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [concurrency-transactions.md](concurrency-transactions.md) | `tx-01` – `tx-07`, `tx-19` – `tx-21` | Double-booking, Isolation levels, Distributed locks, Idempotency, Database invariants, Post-commit events, Concurrency vs parallelism vs async, Decision framework, Amdahl's Law |
| [transaction-patterns.md](transaction-patterns.md) | `tx-08` – `tx-12` | Inventory reservation, Saga orchestration, Compensating transactions, Payment idempotency, Subdomain consistency |
| [idempotency-hidden-costs.md](idempotency-hidden-costs.md) | `tx-13` – `tx-18` | Idempotency state explosion, False confidence, Money bugs, Observability gaps, End-to-end idempotency, Success semantics |
| [29-tx-key-takeaways.md](29-tx-key-takeaways.md) | `tx-21` – `tx-24` | Check-then-act races, Concurrent-request testing, Atomic idempotency-key persistence, Idempotency state lifecycle |
| [45-tx-key-takeaways.md](45-tx-key-takeaways.md) | `tx-25` – `tx-30` | Business vs. retry identity, Atomic insert-or-fail, Gateway transaction reference, Layered duplicate protection, Idempotent consumers, Exactly-once as idempotent outcome |
| [30-tx-key-takeaways.md](30-tx-key-takeaways.md) | `tx-31` – `tx-36` | Redis edge protection, Queue-based serialization, Reservation-payment decoupling, Idempotency tokens, Multi-region inventory, Layered flash-sale defense |
| [amazon-checkout-scaling-takeaways.md](amazon-checkout-scaling-takeaways.md) | `tx-37` – `tx-41` | Scaling vs. inventory protection, Pessimistic-lock contention cascade, Distributed reservation-expiry cleanup, Eventual consistency as product decision, Impossible-state prevention |
| [causal-consistency.md](causal-consistency.md) | — | Causal ordering, Happens-before relationships, Vector clocks |

## Cross-References

- **Dictionary**: [Data/Concurrency](../../reference-dictionary/data-concurrency.md), [CQRS/Events](../../reference-dictionary/cqrs-event-driven.md)
- **Azure**: [Azure SQL](../../architecture-azure/data/)
- **Related**: [Databases](../databases/), [Resilience](../resilience/), [Messaging](../messaging/)
- **Taxonomy**: §2.3 Concurrency & Asynchronous Processing
