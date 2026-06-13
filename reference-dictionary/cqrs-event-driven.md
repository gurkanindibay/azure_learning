# CQRS, Event Sourcing & Event-Driven Patterns

> **Domain**: Command/query separation, event-driven architecture, projections, and related patterns.
> **Parent**: [Reference Dictionary](README.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| CQRS | [`#cqrs`](#cqrs) |
| Command Side | [`#command-side`](#command-side) |
| Query Side | [`#query-side`](#query-side) |
| Event Sourcing | [`#event-sourcing`](#event-sourcing) |
| Projection | [`#projection`](#projection) |
| Read Model | [`#read-model`](#read-model) |
| Ledger | [`#ledger`](#ledger) |
| Outbox Pattern | [`#outbox-pattern`](#outbox-pattern) |
| Idempotency | [`#idempotency`](#idempotency) |
| Dual-Write Problem | [`#dual-write-problem`](#dual-write-problem) |
| Event-Driven Architecture | [`#event-driven-architecture`](#event-driven-architecture) |

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

## Query Side

The **read path** in CQRS — responsible for serving data to humans, optimized for speed and UX. Query models can be denormalized, cached, and purpose-built. They are replaceable and eventually consistent.

**Consumers**: Customer app, support dashboard, risk analyst view, operations reconciliation, finance reports.

**Must NOT**: Become the source of financial truth. Never use a query-side value to approve money movement.

**Also see**: [CQRS](#cqrs), [Projection](#projection), [Read Model](#read-model)

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

**Also see**: [Outbox Pattern](#outbox-pattern), [Dual-Write Problem](#dual-write-problem) · [API Design](api-design.md#idempotency-key) · [Data & Concurrency](data-concurrency.md)

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
