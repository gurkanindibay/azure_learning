---
type: Index
title: "Resilience Patterns"
description: "System-design problems and strategies for resilience: circuit breakers, retry patterns, bulkheads, outage anti-patterns, and defensive coding."
timestamp: 2026-06-27T00:00:00Z
---

# Resilience Patterns

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for building resilient distributed systems: circuit breakers, retry patterns, bulkheads, timeouts, outage analysis, and defensive coding practices.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [resilience-patterns.md](resilience-patterns.md) | `resilience-01` – `resilience-06` | Retry storms, Circuit breakers, Bulkheads, Timeouts, Gateway bottlenecks |
| [circuit-breaker-honesty.md](circuit-breaker-honesty.md) | `cb-01` – `cb-07` | Slow-call rate, minimumNumberOfCalls, Breaker vs Bulkhead, Retry amplification, Honest resilience stack, Fallback ladder |
| [famous-outages.md](famous-outages.md) | `resilience-07` – `resilience-11` | Roblox, Cloudflare, Datadog, Meta, Atlassian outages — circular dependencies, blast radius, correlated failures |
| [defensive-coding.md](defensive-coding.md) | `arch-12` – `arch-15` | Input validation, Assertions, Fail-safe batch processing, Defensive dependency management |

## Cross-References

- **Dictionary**: [Resilience](../../reference-dictionary/resilience.md)
- **Azure**: [Azure Reliability](../../architecture-azure/observability/)
- **Related**: [Concurrency & Transactions](../concurrency-transactions/), [Caching](../caching/), [API & Network](../api-network/)
- **Taxonomy**: §7.1 Reliability & Resilience
