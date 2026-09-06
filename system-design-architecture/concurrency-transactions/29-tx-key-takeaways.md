---
type: System Design
title: "Concurrency & Transactions — Payment Race Condition Takeaways"
description: "Reusable concurrency and idempotency strategies from a payment-service incident that caused duplicate charges."
generated: { by: process:okf-migrate, at: 2026-07-10T00:00:00Z }
---

# 29. Concurrency & Transactions — Payment Race Condition Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [A Race Condition in Our Payment Service Charged 14,000 Customers Twice](../../articles/concurrency-transactions/payment-service-race-condition-duplicate-charges.md)
> **Related**: [Concurrency & Transactions](concurrency-transactions.md#tx-04-idempotency), [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key), [Race Condition](../../reference-dictionary/concurrency-runtimes.md#race-condition)

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [tx-21](#tx-21-check-then-act-race-in-payment-retries) | Concurrent retries bypass a duplicate check | Check-then-act race |
| [tx-22](#tx-22-coverage-without-concurrency-scenarios) | High coverage misses timing-dependent failures | Concurrency-focused testing |
| [tx-23](#tx-23-atomic-idempotency-key-persistence) | A retry can execute the external charge twice | Atomic idempotency-key persistence |
| [tx-24](#tx-24-idempotency-state-lifecycle) | Pre-recorded keys can become stale or orphaned | Idempotency state lifecycle |

## tx-21: Check-then-act race in payment retries

| | |
|:---|:---|
| **Problem** | Two requests for the same checkout arrive while the first request is still waiting on the payment provider. Both read "not recorded" and both charge the customer. |
| **Root cause** | The duplicate check and the state-changing action are separated by an external call, so the check is not atomic with the business operation. |

**Strategy**: Treat a check followed by a write as a concurrency boundary. Persist a request-specific idempotency key before calling the payment provider, and make the persistence operation atomic or protected by a uniqueness constraint.

**Tradeoff**: The database write adds a persistence step before the payment call, but it closes the duplicate-execution window that a post-provider lookup leaves open.

## tx-22: Coverage without concurrency scenarios

| | |
|:---|:---|
| **Problem** | Unit, integration, and staging tests can pass while simultaneous identical requests still produce duplicate side effects. |
| **Root cause** | Sequential tests verify whether the guard exists, but not whether two requests can observe the same pre-write state at the same time. |

**Strategy**: Add a deterministic concurrent-request test that sends identical requests together, controls the provider delay, and asserts one external charge plus one replayed result. Repeat the check against the real persistence layer where possible.

**Tradeoff**: Timing-sensitive tests require more setup and can be harder to keep deterministic, but they exercise the failure mode that line coverage cannot represent.

## tx-23: Atomic idempotency-key persistence

| | |
|:---|:---|
| **Problem** | A service needs to return the original result for a retry without issuing a second charge. |
| **Root cause** | The idempotency key is recorded only after the external provider succeeds, leaving concurrent requests free to start duplicate work. |

**Strategy**: Generate one key per business action, record it before the external call, and associate the key with the eventual result. A duplicate request should retrieve the original outcome rather than invoke the provider again.

**Tradeoff**: The key store must survive retries and concurrent access, and the system must define what a duplicate receives while the original request is still in progress.

## tx-24: Idempotency state lifecycle

| | |
|:---|:---|
| **Problem** | Recording a key before the provider call prevents duplicates but can leave records for failed or abandoned transactions. |
| **Root cause** | Idempotency state now exists before the business operation has a final outcome, so it needs lifecycle management independent of the payment provider. |

**Strategy**: Model pending, completed, and failed outcomes; reconcile or clean up orphaned records; and choose a key-retention period that matches the client retry window and business action.

**Tradeoff**: A short retention period reduces storage but can admit late duplicates; a long period improves replay protection but can block legitimate retries and increases operational storage and cleanup work.
