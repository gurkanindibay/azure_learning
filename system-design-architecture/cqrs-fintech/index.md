
# CQRS & Fintech

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for CQRS-based fintech systems: command/query separation, ledger design, payment gateways, global payment systems, and reconciliation.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [cqrs-fintech.md](cqrs-fintech.md) | `cqrs-01` – `cqrs-15` | Command/query boundary, Ledger vs balance, Idempotency guard, Limit decisions, Outbox pattern, Projection replaceability, Reconciliation |
| [global-payment-system.md](global-payment-system.md) | `cqrs-16` – `cqrs-21` | Gateway/processor boundary, Database per service, Async messaging, Idempotency, Saga, Circuit breaker + backoff |
| [payment-gateway.md](payment-gateway.md) | `cqrs-22` – `cqrs-26` | Smart routing, Provider adapter + circuit breaker, Dynamic fee calculation, Automated reconciliation, Multi-layer caching |
| [debit-card-processing.md](debit-card-processing.md) | `cqrs-27` – `cqrs-34` | Authorization pipeline, Bank adapter framework, Real-time balance accuracy, PIN security, Multi-dimensional limits, Transaction reversal, Per-bank circuit breaker, Database sharding |
| [payment-events-duplicate-processing.md](payment-events-duplicate-processing.md) | `cqrs-35` – `cqrs-37` | Database-as-guardrail deduplication, Delivery vs business correctness separation, Payment state machine with idempotent transitions |
| [cqrs-in-system-design-key-takeaways.md](cqrs-in-system-design-key-takeaways.md) | `cqrs-38` – `cqrs-43` | Read/write model separation, Command intent, Query projections, Eventual consistency, Minimal CQRS adoption, When to introduce CQRS |
| [microservices-join-queries-key-takeaways.md](microservices-join-queries-key-takeaways.md) | `cqrs-44` – `cqrs-46` | API Composition pattern, Cross-service filtering limits, CDC-backed read models for complex queries |
| [payment-saga-pattern.md](payment-saga-pattern.md) | `cqrs-47` – `cqrs-53` | Saga pattern for payments, Orchestration vs choreography, Idempotency keys, Outbox pattern, Compensation workflows, Crash recovery, Saga monitoring |

## Cross-References

- **Dictionary**: [CQRS/Events](../../reference-dictionary/cqrs-event-driven.md), [Fintech](../../reference-dictionary/fintech.md)
- **Azure**: [Azure Integration](../../architecture-azure/integration/)
- **Related**: [Messaging](../messaging/), [Concurrency & Transactions](../concurrency-transactions/), [Resilience](../resilience/)
- **Taxonomy**: §3.3 Event-Driven & Messaging
