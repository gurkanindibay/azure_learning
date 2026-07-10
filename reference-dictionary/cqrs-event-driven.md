---
type: Reference
title: "CQRS, Event Sourcing & Event-Driven Patterns"
description: "**Command Query Responsibility Segregation** — an architectural pattern that separates write operations (commands, which change state) from read operations (queries, which serve data)."
timestamp: 2026-06-14T00:00:00Z
---

# CQRS, Event Sourcing & Event-Driven Patterns

> **Domain**: Command/query separation, event-driven architecture, projections, and related patterns.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| CQRS | [`#cqrs`](#cqrs) |
| Command Side | [`#command-side`](#command-side) |
| Command Model | [`#command-model`](#command-model) |
| Query Side | [`#query-side`](#query-side) |
| Query Model | [`#query-model`](#query-model) |
| Event Sourcing | [`#event-sourcing`](#event-sourcing) |
| Projection | [`#projection`](#projection) |
| Read Model | [`#read-model`](#read-model) |
| Ledger | [`#ledger`](#ledger) |
| Outbox Pattern | [`#outbox-pattern`](#outbox-pattern) |
| Post-Commit Dispatch | [`#post-commit-dispatch`](#post-commit-dispatch) |
| Idempotency | [`#idempotency`](#idempotency) |
| Idempotency State Explosion | [`#idempotency-state-explosion`](#idempotency-state-explosion) |
| API Idempotency | [`#api-idempotency`](#api-idempotency) |
| Token-Based Idempotency | [`#token-based-idempotency`](#token-based-idempotency) |
| Dual-Write Problem | [`#dual-write-problem`](#dual-write-problem) |
| Event-Driven Architecture | [`#event-driven-architecture`](#event-driven-architecture) |
| Event Carried State Transfer | [`#event-carried-state-transfer`](#event-carried-state-transfer) |
| Aggregate Snapshot | [`#aggregate-snapshot`](#aggregate-snapshot) |
| Cryptographic Erasure | [`#cryptographic-erasure`](#cryptographic-erasure) |
| Event ID | [`#event-id`](#event-id) |
| Eventual Consistency | [`#eventual-consistency`](#eventual-consistency) |
| Event Backbone | [`#event-backbone`](#event-backbone) |
| Async Workflow | [`#async-workflow`](#async-workflow) |

---

## CQRS

**Command Query Responsibility Segregation** — an architectural pattern that separates write operations (commands, which change state) from read operations (queries, which serve data).

| Side | Responsibility | Consistency | Personality |
|:---|:---|:---|:---|
| **Command** | Change financial state | Strong (transactional) | Strict, boring, predictable |
| **Query** | Explain financial state | Eventually consistent | Flexible, fast, human-shaped |

> **Key insight**: Commands protect truth. Queries explain truth. Never confuse the two.

**When to use**: Money-facing systems where the same data must answer fundamentally different questions (can money move? vs what should the customer see?).

**When NOT**: Simple CRUD apps where read and write models are identical.

**Also see**: [Projection](#projection), [Read Model](#read-model), [Ledger](#ledger) · [Fintech Dictionary](fintech.md)

---

## Command Side

The **write path** in CQRS — responsible for accepting, validating, and persisting state changes using strong consistency. The command side protects correctness; it must never depend on read models for approval decisions.

**Command flow**:
```
Receive command → Check idempotency → Validate → Check risk →
Reserve limit → Create ledger entries → Validate balanced →
Commit transaction → Save outbox event → Return result
```

**Must NOT**: Build dashboard responses, perform search queries, depend on cached/projection data for approvals.

**Also see**: [CQRS](#cqrs), [Idempotency](#idempotency), [Ledger](#ledger)

---

## Command Model

The **write-side data model** in CQRS — the structure and validation rules optimized for accepting, validating, and persisting state-changing commands. The command model is the authoritative source of truth for business decisions and is usually strongly consistent.

**Also see**: [Command Side](#command-side), [CQRS](#cqrs)

---

## Query Side

The **read path** in CQRS — responsible for serving data to humans, optimized for speed and UX. Query models can be denormalized, cached, and purpose-built. They are replaceable and eventually consistent.

**Consumers**: Customer app, support dashboard, risk analyst view, operations reconciliation, finance reports.

**Must NOT**: Become the source of financial truth. Never use a query-side value to approve money movement.

**Also see**: [CQRS](#cqrs), [Projection](#projection), [Read Model](#read-model)

---

## Query Model

The **read-side data model** in CQRS — a structure optimized for serving queries quickly, often denormalized, cached, and purpose-built. In most CQRS discussions, "query model" is synonymous with [Read Model](#read-model) or [Projection](#projection).

**Also see**: [Query Side](#query-side), [Read Model](#read-model), [Projection](#projection)

---

## Event Sourcing

A persistence pattern where **state changes are stored as an immutable sequence of events** rather than as a mutable current state. The current state is derived by replaying (projecting) events.

| Aspect | Traditional CRUD | Event Sourcing |
|:---|:---|:---|
| **Storage** | Current state (mutable row) | Sequence of events (append-only) |
| **History** | Lost on update | Every change preserved |
| **Correction** | Overwrite | Append a compensating event |
| **Audit** | Separate log needed | Built-in |

> **Guidance**: Most fintech teams need clean ledger entries and projections before they need full event sourcing. Start with a ledger. Add projections. Adopt event sourcing only when replay and audit requirements demand it.

**Also see**: [Ledger](#ledger), [Projection](#projection) · [Data & Concurrency](data-concurrency.md#acid-transactions)

---

## Projection

A **read-optimized, denormalized view** of event or ledger data, built by consuming and transforming events from an authoritative source. Projections are **derived**, **replaceable**, and **eventually consistent**.

### Key Characteristics

| Characteristic | Meaning |
|:---|:---|
| **Derived** | Built from ledger/event data — does not originate truth |
| **Replaceable** | Can be dropped, rebuilt, or re-materialized at any time |
| **Eventually consistent** | May lag behind the ledger — acceptable for display, unacceptable for decisions |
| **Purpose-built** | Optimized for one specific consumer (dashboard, support screen, mobile timeline) |
| **Disposable** | If corrupted, delete and rebuild — no financial data is lost |

### What a Projection Is NOT

| ❌ Is NOT | Why |
|:---|:---|
| The source of truth | The ledger/event store holds truth; the projection reflects it |
| Used for money-movement decisions | Never ask a projection "can this money move?" |
| Immutable | Projections are rebuilt; immutability belongs to the ledger |
| Authoritative for limits | Limits must be reserved on the command side |

### Projection vs Ledger

| Aspect | Ledger (Source of Truth) | Projection (Derived View) |
|:---|:---|:---|
| **Role** | Records financial facts | Tells a story about those facts |
| **Consistency** | Strong, transactional | Eventually consistent |
| **Mutability** | Append-only, immutable | Freely rebuildable |
| **If lost** | Financial disaster | Rebuild from ledger |
| **Examples** | `ledger_entries` table | Balance view, transaction timeline, risk dashboard |

> **The Golden Rule**: A projection tells the story. The ledger holds the truth. Never confuse the two.

**Also see**: [Read Model](#read-model), [CQRS](#cqrs), [Ledger](#ledger) · [Fintech Dictionary](fintech.md)

---

## Read Model

Synonymous with **projection** in most CQRS contexts. The query-side representation of data — shaped around human understanding rather than financial correctness. Read models answer "what happened?" Projections are the technical mechanism; read models are the conceptual result.

**Also see**: [Projection](#projection), [Query Side](#query-side)

---

## Ledger

An **append-only, immutable record of financial movement** where every entry is balanced (debit = credit). The ledger is the single source of financial truth in a CQRS fintech system.

| Principle | Detail |
|:---|:---|
| **Append-only** | Entries are never mutated after posting |
| **Balanced** | Every transaction has matching debit and credit |
| **Immutable history** | The past is evidence, not garbage |
| **Source of truth** | All projections and read models derive from it |

> Corrections are posted as **new entries** — existing entries are **never** edited or deleted. A reversal is a new entry, not a deletion.

**Also see**: [Projection](#projection), [CQRS](#cqrs) · [Fintech Dictionary](fintech.md#ledger-double-entry)

---

## Outbox Pattern

A pattern that solves the **dual-write problem** — ensuring a database write and a message/event publish happen atomically.

```
WRONG:   DB write → Publish event  (gap: crash between steps)
RIGHT:   DB write + Outbox write (same TX) → Publisher reads outbox → Event published
```

| Principle | Detail |
|:---|:---|
| **Same transaction** | Business data and outbox event committed atomically |
| **Separate publisher** | Dedicated process reads outbox and publishes reliably |
| **At-least-once** | Publisher retries; consumers must be idempotent |
| **Order preserved** | Events published in transaction commit order |

**Also see**: [Dual-Write Problem](#dual-write-problem), [Idempotency](#idempotency) · [Messaging](messaging.md)

---

## Post-Commit Dispatch

The rule that side effects such as events, notifications, and confirmations must be emitted only after the originating database transaction has successfully committed.

```
WRONG:  Check inventory → Emit event → Commit DB  (event may describe a failed write)
RIGHT:  Check inventory → Commit DB → Emit event  (event is a fact)
```

### Key Characteristics
- Prevents confirmations or downstream events for rolled-back transactions
- Often implemented via outbox pattern, CDC, or database post-commit hooks
- Requires idempotency on the consumer side because at-least-once delivery is common

### When to Use
- Sending booking confirmations, payment receipts, or inventory updates
- Any workflow where an external observable must reflect committed state

### When NOT to Use
- When the side effect is purely in-process and does not outlive the transaction
- Do not use this as an excuse to delay user feedback; return a `202 Accepted` or equivalent while the post-commit path completes

**Also see**: [Outbox Pattern](#outbox-pattern), [Dual-Write Problem](#dual-write-problem) · [Data & Concurrency: Change Data Capture](../reference-dictionary/data-concurrency.md#change-data-capture)

---

## Idempotency

The property that ensures **the same business action performed multiple times produces the same result as performing it once**.

```
Client sends:    Transfer { idempotencyKey: "txn-abc-123" }
Server checks:   Have I seen "txn-abc-123" before?
  → If YES:      Return the original result (do NOT process again)
  → If NO:       Process, store key + result, return
```

| Principle | Detail |
|:---|:---|
| **Key belongs to business action** | Not the HTTP request, not the session — the exact intent |
| **Sits before the dangerous part** | Before money moves, before the ledger command |
| **Uses `SELECT FOR UPDATE`** | Prevents race conditions on idempotency key lookup |

> In fintech, idempotency is a financial seatbelt — fastened before the engine starts, not a best-effort log check.

### Hidden Costs at Scale

Idempotency does not remove complexity — it **moves it into time**. Instead of fast, visible failures, systems get slow, invisible ones.

| Hidden Cost | Description |
|:---|:---|
| **State explosion** | Storing keys + outcomes + TTLs at scale creates a secondary datastore with independent failure modes |
| **False confidence** | Teams add more retries once a system is "idempotent," amplifying risk instead of reducing it |
| **Money bugs** | Compensating transactions and auto-reconciliation can temporarily violate financial invariants — the books look right eventually, but the path between states erodes trust |
| **Observability gaps** | Idempotent retries produce successful responses, so standard dashboards show green while failures accumulate as support tickets |
| **Incomplete execution** | A cached "success" response may be returned while downstream side effects are still in progress |

> **Core insight**: If an operation cannot be safely replayed, do not pretend it can. Idempotency must be end-to-end with explicitly modeled side effects, and "success" must mean execution complete — not merely accepted.

**Also see**: [API Idempotency](#api-idempotency), [Token-Based Idempotency](#token-based-idempotency), [Idempotency State Explosion](#idempotency-state-explosion), [Outbox Pattern](#outbox-pattern), [Dual-Write Problem](#dual-write-problem) · [API Design](api-design.md#idempotency-key) · [Data & Concurrency](data-concurrency.md) · [Reconciliation](fintech.md#reconciliation)

---

## Idempotency State Explosion

The **hidden infrastructure cost** of idempotency at scale — storing every idempotency key, its outcome, and managing TTLs creates a secondary datastore that must be as reliable as the primary database.

### Key Characteristics
- **Linear growth**: Storage grows as `request volume × TTL duration` — every unique request consumes a row
- **Independent failure domain**: When the idempotency store is unavailable, the system must either reject requests (fail closed) or risk double execution
- **TTL is a correctness constraint**: Keys must live longer than the maximum retry window plus reconciliation lag; too-short TTLs reintroduce duplicate-processing risk
- **Cleanup is non-trivial**: Premature key deletion is dangerous; deterministic GC processes are safer than request-time eviction

### When to Use
- Planning idempotency storage capacity and failure modes before deploying to production
- Auditing existing idempotent systems for hidden operational risk

### When NOT to Use
- As a reason to avoid idempotency — the alternative (duplicate execution with no safety net) is worse
- As justification for arbitrarily long TTLs — balance safety against storage cost

### Also see
- [Idempotency](#idempotency) · [Outbox Pattern](#outbox-pattern)

---

## Dual-Write Problem

The problem where a service must write to **two independent systems** (e.g., database and message broker) and a failure between the two writes leaves the system in an inconsistent state.

| Scenario | Consequence |
|:---|:---|
| DB write succeeds, event publish fails | Ledger knows; read models don't |
| Event published, DB transaction rolls back | Read models believe a transfer that never happened |

**Solution**: [Outbox Pattern](#outbox-pattern) — write both in the same database transaction.

**Also see**: [Outbox Pattern](#outbox-pattern) · [Data & Concurrency](data-concurrency.md)

---

## Event-Driven Architecture

An architectural style where services communicate by producing and consuming **events** — immutable facts about what happened. Events describe state changes that have already occurred.

| Principle | Detail |
|:---|:---|
| **Events are facts** | "TransferAccepted" not "PleaseTransfer" |
| **Source of truth first** | The ledger commits → the event describes what happened |
| **Events amplify, not fix** | A confused ledger + events = confusion distributed faster |

> **Key insight**: "Let's make it event-driven" does not fix a confused financial model. The question is: "What exactly is the source of truth?" Events are excellent after a trusted command has committed. They are dangerous when used to avoid making the command boundary clear.

**Also see**: [CQRS](#cqrs), [Outbox Pattern](#outbox-pattern) · [Messaging](messaging.md)

---

## Event Carried State Transfer

An event design pattern where events include **all the state information that downstream consumers need** — not just an identifier. This eliminates the need for consumers to call back to the producing service to fetch associated data.

### Key Characteristics
- **Self-contained events**: Each event carries a complete, consumer-usable snapshot of the relevant entity state
- **Eliminates round-trips**: Consumers can act immediately without synchronous back-calls
- **Producer-defined contract**: The producer decides what context to include; consumers cannot request more
- **Payload size growth**: Rich payloads increase message size; combine with the Claim Check pattern for payloads over the broker limit

### When to Use
- Consumers consistently need the same contextual fields alongside the event notification
- Low-latency systems where every additional network call is unacceptable
- Decoupling services so the producer's internal model can evolve independently of consumers (as long as the event contract holds)

### When NOT to Use
- Event payloads would exceed broker message size limits (use [Claim Check](messaging.md#claim-check) instead)
- Sensitive data fields should not be broadcast to all consumers
- The producer state is so large or varied that different consumers need entirely different subsets

### Also see
- [Event-Driven Architecture](#event-driven-architecture) · [CQRS](#cqrs) · [Messaging: Claim Check](messaging.md#claim-check)

---

## Aggregate Snapshot

A **point-in-time serialisation of an event-sourced aggregate's current state**, stored externally alongside the Kafka offset at which it was captured. On consumer restart or new deployment, the snapshot is loaded first and only events after the snapshot offset are replayed — bounding rebuild time to a fixed interval regardless of total event history.

### Key Characteristics
- **Offset-tagged**: the snapshot records the exact Kafka partition offset (or event sequence number) at which it was taken so replay can resume precisely
- **Frequency trade-off**: more frequent snapshots → faster rebuild, higher storage cost; typical intervals are every 1 000 events or every 5 minutes
- **Storage**: DynamoDB (for fast key lookup) or S3 (for large aggregates or cost-sensitivity)
- **Atomicity**: the snapshot must be written in the same transaction as the offset bookmark; a partial snapshot is corrupted state

### When to Use
- Aggregates with millions of events where cold-start replay is unacceptably slow
- Event-sourced consumers that must restart quickly (e.g., serverless or auto-scaling deployments)

### When NOT to Use
- Aggregates with a small event history where full replay takes < 1 second
- Systems where snapshot storage is not available or adds unacceptable operational overhead

### Also see
- [Event Sourcing](#event-sourcing) · [Projection](#projection) · [Messaging: Compacted Topic](messaging.md#compacted-topic)

---

## Cryptographic Erasure

A GDPR compliance technique for **immutable event logs**: encrypt each event containing PII with a **per-user symmetric key**. When the user requests deletion, destroy the key. The events remain physically in the log but are permanently unreadable — satisfying the erasure obligation without mutating the log.

### Key Characteristics
- **Key granularity**: one encryption key per data-subject (user); deleting the key erases all their events across all topics
- **Accepted by regulators**: most Data Protection Authorities accept cryptographic erasure as equivalent to physical deletion when the encryption is provably unrecoverable (AES-256)
- **Key store**: AWS KMS (Customer Managed Keys), HashiCorp Vault, or a dedicated secrets table with strict access controls
- **Performance overhead**: AES-256 GCM encryption adds < 1 ms per event write; key lookup adds one extra service call

### When to Use
- Event-sourced systems subject to GDPR, CCPA, or similar right-to-erasure regulations
- Any immutable log (blockchain, audit trail) where physical deletion would corrupt the chain

### When NOT to Use
- Systems where PII can be kept in a separate, mutable store (simpler: just delete the record)
- When regulatory guidance in the applicable jurisdiction does not accept cryptographic erasure as equivalent to deletion

### Also see
- [Event Sourcing](#event-sourcing) · [Outbox Pattern](#outbox-pattern) · [HSM](../reference-dictionary/hsm-cryptography.md)

---

## Event ID

A **globally unique identifier** assigned to every business event at production time, used by consumers for idempotent deduplication. The Event ID remains unchanged across producer retries so that the same business event always carries the same identifier.

### Key Characteristics
- **Deterministic per business event**: Same logical event → same Event ID across retries, regardless of how many times the producer publishes
- **Consumer-facing**: The Event ID is the key consumers use to check "have I already processed this?"
- **Analogous to idempotency keys**: Functions identically to an idempotency key in payment APIs — the same key means "this is the same action"
- **Producer responsibility**: The producer must generate the ID before the first publish attempt and reuse it on retries

### When to Use
- Any at-least-once messaging system where producers may retry after acknowledgment loss
- Event-driven architectures where duplicate events must not cause duplicate business side-effects
- Payment systems, inventory updates, order processing — any workflow where double-processing is unacceptable

### When NOT to Use
- In systems with true exactly-once delivery guarantees (rare in practice)
- When the consumer can derive idempotency from natural business keys (e.g., `order_id` + `version`)

### Also see
- [Idempotency](#idempotency) · [Token-Based Idempotency](#token-based-idempotency) · [Outbox Pattern](#outbox-pattern) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Atomic Deduplication](../reference-dictionary/messaging.md#atomic-deduplication)

---

## Eventual Consistency

**Eventual Consistency** — a consistency model where updates to a distributed system propagate asynchronously. If no new updates are made, all replicas eventually converge to the same value. During the propagation window, different nodes may serve different (stale) values.

### Key Characteristics
- **Asynchronous replication**: Writes to one node are propagated to other nodes in the background — there is no synchronous quorum wait
- **Convergence guarantee**: Given enough time without new writes, all replicas agree
- **Staleness window**: The period between write and full propagation — milliseconds to seconds in practice
- **Conflict resolution**: Requires a strategy (last-write-wins, CRDTs, application-level merge) when concurrent writes conflict

### When to Use
- High-availability systems where serving any data is better than serving no data (streaming, social feeds, CDN metadata)
- Read-heavy workloads where occasional staleness is acceptable and low latency is paramount
- Multi-region systems where synchronous cross-region writes would add unacceptable latency

### When NOT to Use
- Financial systems where showing a stale balance could mean approving a transaction the account cannot cover
- Any system where consistency is a legal or compliance requirement (audit trails, medical records)
- When the application cannot implement meaningful conflict resolution for concurrent writes

### Also see
- [Masterless Architecture](../reference-dictionary/architecture-patterns.md#masterless-architecture) · [Apache Cassandra](../reference-dictionary/architecture-patterns.md#apache-cassandra) · [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem) · [CQRS](#cqrs) · [Projection](#projection)

---

## Event Backbone

An architectural pattern where **Kafka (or an equivalent distributed log) serves as the central nervous system** connecting all services in a domain. Services publish domain events to topics and react to events from other services — they never call each other directly via synchronous APIs. The log is the single source of truth for what happened in the system.

> "Instead of services calling each other, they publish and react to events independently."

### Key Characteristics
- **Loose coupling**: Services don't know about each other — they only know about event types and topic names
- **Independent deployability**: Each service can be deployed, scaled, and evolved independently
- **Resilience through buffering**: Kafka absorbs downstream slowdowns; producers are never blocked by slow consumers
- **Multi-consumer fan-out**: One event is consumed by N downstream services without additional producer effort

### When to Use
- Microservice ecosystems where synchronous call chains have become a distributed monolith
- Domain-driven systems where bounded contexts produce and consume domain events
- Organizations where different teams own different services and deploy independently

### When NOT to Use
- Simple systems with 2-3 services where direct REST calls are simpler and sufficient
- Latency-sensitive request-response flows where eventual consistency is unacceptable
- Systems where strict transactional consistency across services is required

### Also see
- [Event-Driven Architecture](#event-driven-architecture) · [Event Sourcing](#event-sourcing) · [Eventual Consistency](#eventual-consistency) · [CQRS](#cqrs)

---

## API Idempotency

The guarantee that **multiple identical API requests produce the same side effect as a single request** — regardless of how many times the client sends them. API idempotency is enforced at the server boundary using idempotency keys, token validation, or natural business identifiers, and is essential for safe retries in distributed systems where network failures, timeouts, and at-least-once delivery are the norm.

### Key Characteristics
- **Client-supplied key**: The client generates a unique `Idempotency-Key` header per business action and reuses it across retries
- **Server-enforced**: The server stores processed keys and returns cached results for duplicates — the client never decides "this is a duplicate"
- **Time-bound**: Keys expire after a configurable window (typically 24 hours); retries outside the window are treated as new requests
- **Atomic validation**: Key lookup and business execution must be atomic or use compare-and-swap to prevent race conditions under concurrency

### When to Use
- Payment APIs, order creation, inventory deductions — any mutating endpoint where double-execution causes financial or data corruption
- Any API exposed to mobile clients, retry-happy SDKs, or unreliable networks
- Message consumers processing at-least-once delivery from Kafka, RabbitMQ, or Event Hubs

### When NOT to Use
- Read-only GET endpoints (already idempotent by HTTP semantics)
- Low-stakes operations where occasional duplicates are acceptable and cheaper to clean up than to prevent
- When the idempotency store (Redis, DB) becomes a bigger reliability risk than the duplicate operations it prevents

### Also see
- [Idempotency](#idempotency) · [Token-Based Idempotency](#token-based-idempotency) · [Idempotency-Key](../api-design.md#idempotency-key) · [PRG Pattern](../api-design.md#prg-pattern)

---

## Token-Based Idempotency

A **concrete idempotency strategy** where each mutating request carries a unique, single-use token. The server atomically validates and consumes the token before executing business logic — if the token is missing or already consumed, the request is rejected. Under high concurrency, the token check-and-consume must be a single atomic operation (e.g., Redis Lua script, `SETNX`, or `SELECT FOR UPDATE`) to prevent race-condition-based double execution.

### Key Characteristics
- **Token lifecycle**: Generate → store with TTL → submit with request → atomically validate + delete → reject if missing
- **Atomic consume**: Redis Lua scripts (`GET` + `DEL` in one operation) or database row-level locks prevent concurrent token reuse
- **ULID preferred**: Universally Unique Lexicographically Sortable Identifiers provide time-sortable, globally unique tokens without coordination
- **Short TTL**: Tokens typically expire in 5 minutes — long enough for a single request lifecycle, short enough to limit storage

### When to Use
- High-concurrency scenarios where simple database unique constraints are insufficient (e.g., flash sales, ticket booking)
- APIs where the client cannot provide a natural business key (order creation before an order number exists)
- Combined with state machines and optimistic locking as a defense-in-depth idempotency strategy

### When NOT to Use
- When a natural business key already provides idempotency (e.g., `transaction_id` from a payment gateway)
- Low-throughput systems where a database unique constraint on `request_id` is simpler and sufficient
- When Redis availability is lower than the service's availability target — a token store outage blocks all mutating operations

### Also see
- [API Idempotency](#api-idempotency) · [Idempotency](#idempotency) · [Idempotency-Key](../api-design.md#idempotency-key) · [Optimistic Locking](../data-concurrency.md#optimistic-locking)

---

## Async Workflow

A **coordination pattern that breaks a long-running business process into independent steps executed in response to events**, rather than chaining them inside a single synchronous request. Each step publishes an event when it finishes, and downstream consumers subscribe to those events to perform the next action.

### Key Characteristics

- **Event-driven decomposition**: the initiating request only creates the initial record and publishes an event
- **Loose coupling**: consumers evolve and fail independently without blocking the originating operation
- **Eventual consistency**: downstream state catches up asynchronously rather than in the original transaction
- **Failure isolation**: a failed consumer can retry or land in a DLQ without rolling back upstream work

### When to Use

- Multi-step workflows where steps have different reliability, latency, or scaling requirements
- Cross-service processes where synchronous chaining creates cascading failures
- Checkout, order fulfillment, billing, or notification pipelines

### When NOT to Use

- When the user must observe the final result before the API returns
- When strong transactional consistency across steps is required and cannot be relaxed
- Very short processes where synchronous handling is simpler and fast enough

### Also see

- [Outbox Pattern](#outbox-pattern) · [Event-Driven Architecture](#event-driven-architecture) · [Eventual Consistency](#eventual-consistency) · [CQRS](#cqrs)
- [29-arch-key-takeaways.md](../system-design-architecture/29-arch-key-takeaways.md)
