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
| [concurrency-transactions.md](concurrency-transactions.md) | `tx-01` – `tx-07` | Double-booking, Isolation levels, Distributed locks, Idempotency, Database invariants, Post-commit events |
| [transaction-patterns.md](transaction-patterns.md) | `tx-08` – `tx-12` | Inventory reservation, Saga orchestration, Compensating transactions, Payment idempotency, Subdomain consistency |
| [causal-consistency.md](causal-consistency.md) | — | Causal ordering, Happens-before relationships, Vector clocks |

## Cross-References

- **Dictionary**: [Data/Concurrency](../../reference-dictionary/data-concurrency.md), [CQRS/Events](../../reference-dictionary/cqrs-event-driven.md)
- **Azure**: [Azure SQL](../../architecture-azure/data/)
- **Related**: [Databases](../databases/), [Resilience](../resilience/), [Messaging](../messaging/)
- **Taxonomy**: §2.3 Concurrency & Asynchronous Processing
