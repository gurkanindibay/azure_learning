---
type: Index
title: "Software Architecture"
description: "System-design patterns for software architecture: design patterns (GoF + Enterprise), architecture principles, service design, and Docker optimization."
timestamp: 2026-06-27T00:00:00Z
---

# Software Architecture

> **Parent**: [System Design Interview Reference](../index.md)

Patterns and principles for software architecture: classic design patterns (GoF), enterprise architecture principles, microservice design anti-patterns, and container optimization.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [design-patterns.md](design-patterns.md) | `dp-01` – `dp-12` | Singleton, Factory Method, Builder, Adapter, Decorator, Proxy, Strategy, Observer, Command, Repository, Saga, Pattern selection |
| [architecture-principles.md](architecture-principles.md) | `arch-01` – `arch-21` | Least privilege, Separation of concerns, Defense in depth, Fail fast, Single source of truth, Loose coupling, Immutability, Idempotency, Zero trust, Data flow as unifying pattern, Four-question framework, Bottleneck as data waiting, Scaling as removing waiting, Simplicity over completeness, Data flow first |
| [29-arch-key-takeaways.md](29-arch-key-takeaways.md) | `arch-01` – `arch-07` | Coordination cost, Modular monolith, Idempotency, Async workflows, Outbox pattern, Observability, Developer productivity |
| [distributed-monolith.md](distributed-monolith.md) | `svc-01` – `svc-06` | Distributed monolith anti-pattern, Deployment coupling via synchronous call chains, Strangler Fig + Anti-Corruption Layer recovery, Modular monolith as default, Compile-time module boundaries, In-process contracts and events |
| [dockerfile-optimization.md](dockerfile-optimization.md) | `docker-01` – `docker-08` | Layer ordering, .dockerignore, Multi-stage builds, Cache mounts, Base-image pinning, Build profiling |

## Cross-References

- **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
- **Related**: [System Design Interview](../system-design-interview/), [Performance](../performance/)
- **Taxonomy**: §2.1 Application Architecture Patterns
