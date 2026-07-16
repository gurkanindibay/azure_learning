---
type: System Design
title: "Cache Idempotency — Key Takeaways"
description: "Reusable retry-safety and deduplication strategies for high-throughput services facing network timeouts."
timestamp: 2026-07-10T00:00:00Z
---

# 30. Cache Idempotency — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Idempotency Keys Prevent Duplicate Side Effects](../../articles/caching/idempotency-keys-prevent-duplicate-side-effects.md)
> **Related**: [Caching Architecture](index.md), [Concurrency & Transactions](../concurrency-transactions/29-tx-key-takeaways.md), [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key), [Deduplication Store](../../reference-dictionary/messaging.md#deduplication-store)
> **Taxonomy Reference**: §7.3 Caching Strategies

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-22](#cache-22-retries-repeat-unknown-outcomes) | A timeout hides whether the original operation completed | Operation identity |
| [cache-23](#cache-23-concurrent-retries-bypass-a-non-atomic-check) | Concurrent retries can both pass a duplicate check | Atomic deduplication state |
| [cache-24](#cache-24-downstream-services-lose-the-original-operation-identity) | A new key on retry defeats downstream deduplication | Key propagation |
| [cache-25](#cache-25-delivery-guarantees-do-not-remove-duplicate-side-effects) | Infrastructure delivery guarantees do not guarantee one business effect | At-least-once plus idempotent consumers |

## cache-22: Retries repeat unknown outcomes

| | |
|:---|:---|
| **Problem** | A network timeout leaves the client unable to tell whether the server rejected the request or completed the business operation. A retry can therefore repeat a side effect such as a charge. |
| **Root cause** | Request completion and client visibility are separate events, so a transport failure does not prove that the business operation failed. |

**Strategy**: Assign one client-generated operation identity, such as an idempotency key, to the business action and reuse it for every retry.

**Tradeoff**: Clients and servers must preserve and validate the key, and the service must retain enough state to recognize retries within the business retry window.

## cache-23: Concurrent retries bypass a non-atomic check

| | |
|:---|:---|
| **Problem** | Two requests with the same key arrive while the first is still processing. If both read an empty deduplication store before either writes a result, both can execute the side effect. |
| **Root cause** | Duplicate detection is separated from state reservation, creating a check-then-act race. |

**Strategy**: Atomically reserve the key with a short-lived lock or use a database unique constraint inside the transaction. Store `IN_PROGRESS`, `COMPLETED`, and `FAILED` states together with the replayable response where appropriate.

**Tradeoff**: Redis provides low-latency coordination but introduces TTL, failure, and serialization concerns; a database constraint is simpler and durable but adds write load and latency.

## cache-24: Downstream services lose the original operation identity

| | |
|:---|:---|
| **Problem** | A service safely deduplicates an incoming request but generates a fresh identifier when calling a payment API or publishing an event. Downstream systems then treat a retry as a new operation. |
| **Root cause** | Operation identity was scoped to one hop instead of the complete side-effect chain. |

**Strategy**: Propagate the original idempotency key through HTTP headers, event metadata, and third-party calls. Never generate a new key for a retry of the same business action.

**Tradeoff**: End-to-end propagation simplifies correlation and deduplication, but the key becomes part of the cross-service contract and needs access-control and privacy review.

## cache-25: Delivery guarantees do not remove duplicate side effects

| | |
|:---|:---|
| **Problem** | At-most-once delivery can lose work, while at-least-once delivery can redeliver work. Neither infrastructure guarantee alone ensures one business effect. |
| **Root cause** | Transport delivery semantics describe message transfer, not whether a consumer's side effect was committed before a crash or timeout. |

**Strategy**: Prefer at-least-once delivery with idempotent consumers that record and reject already-processed operation identities. Make the retention period match the maximum realistic replay window.

**Tradeoff**: Durable deduplication state and replayable responses consume storage and operational capacity; aggressive expiry lowers cost but can admit late duplicates.