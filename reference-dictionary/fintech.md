# Fintech-Specific Terms

> **Domain**: Financial technology patterns — reconciliation, limits, risk decisions, ledger design, and financial state management.
> **Parent**: [Reference Dictionary](README.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Reconciliation | [`#reconciliation`](#reconciliation) |
| Limit Reservation | [`#limit-reservation`](#limit-reservation) |
| Risk Actions | [`#risk-actions`](#risk-actions) |
| Financial States | [`#financial-states`](#financial-states) |
| Ledger (Double-Entry) | [`#ledger-double-entry`](#ledger-double-entry) |

---

## Reconciliation

The continuous process of verifying that **internal records match external reality** — comparing the ledger against payment rails, settlement files, and provider responses. Reconciliation detects mismatches, explains discrepancies, and enables corrections without mutating original entries.

### Reconciliation Questions

```
Do my records match the outside world?
Does my ledger match the payment rail?
Do customer-visible states match financial states?
Do reversals make sense?
Do failed transactions have clear final outcomes?
Do pending transactions eventually resolve?
```

### Architecture Implications

| Layer | Designed For |
|:---|:---|
| **Customer view** | Clarity — "where is my money?" |
| **Operations view** | Mismatch detection, failure reasons, settlement references, correction history |
| **Ledger** | Never compromised for reconciliation convenience |

> **Key insight**: A serious fintech system should **expect** mismatch — distributed systems are messy. The goal is detection, explanation, and correction without damaging ledger truth.

**Also see**: [CQRS & Event-Driven: Ledger](cqrs-event-driven.md#ledger)

---

## Limit Reservation

The **command-side operation** that atomically reserves a portion of a customer's limit before money moves. Limits must be reserved with strong consistency (pessimistic locking) — never checked from a projection or cache.

### Real-World Questions Limits Must Handle

| Question | Answer |
|:---|:---|
| Does a pending transfer consume the limit? | Yes — reserve immediately |
| Does a failed transfer release it? | Yes — release on deterministic failure |
| Does a reversed transfer restore it? | Yes — restore as a new limit event |
| Do different payment methods share limits? | Configurable per product |
| What if two transfers arrive simultaneously? | Lock on customer limit row |
| What if risk rejects after reservation? | Release the reservation |

| Side | Responsibility | Mechanism |
|:---|:---|:---|
| **Command** | Reserve limit atomically | `SELECT FOR UPDATE`, strong consistency |
| **Query** | Display remaining allowance | Eventually consistent, cacheable |

**Also see**: [CQRS & Event-Driven: Command Side](cqrs-event-driven.md#command-side) · [Data & Concurrency: Pessimistic Locking](data-concurrency.md#pessimistic-locking)

---

## Risk Actions

Risk decisions that are **posted as new entries** rather than mutating or deleting original financial events. Risk changes its mind as new signals arrive — but it never rewrites history.

### The Immutable Chain

```
TRANSFER_POSTED   ← Original event (immutable)
FRAUD_SUSPECTED   ← Risk detection (new entry)
ACCOUNT_FROZEN    ← Risk decision (new entry)
TRANSFER_REVERSED ← Correction (new entry)
```

### Wrong vs Right

| ❌ Wrong | ✅ Right |
|:---|:---|
| Delete the original transfer | Post a reversal entry |
| Mutate status to "fraudulent" | Add `FRAUD_SUSPECTED` as a separate event |
| Hide uncomfortable history | Make the mess explainable |

> A system that deletes or mutates uncomfortable financial history is not clean. It is unsafe.

**Also see**: [Financial States](#financial-states) · [CQRS & Event-Driven: Ledger](cqrs-event-driven.md#ledger)

---

## Financial States

Precisely defined lifecycle states for financial transactions. Every term must mean exactly one thing across the entire system — product, engineering, support, and operations.

| State | Must NOT Mean | Must Mean |
|:---|:---|:---|
| **Success** | "Accepted but settlement may fail" | "Transaction is complete and settled" |
| **Available** | "Available unless a delayed hold arrives" | "Available for immediate use, no pending claims" |
| **Failed** | "Failed for customer, maybe pending externally" | "Definitively not processed; no money moved" |
| **Reversed** | "Deleted" | "A correcting entry was posted; original remains" |
| **Pending** | "We have no idea" | "Awaiting a specific, named external confirmation" |

> A fintech system with unclear words becomes unclear code → unclear behavior → customer mistrust. This is domain modeling, not copywriting.

**Also see**: [Risk Actions](#risk-actions), [Reconciliation](#reconciliation) · [CQRS & Event-Driven: CQRS](cqrs-event-driven.md#cqrs)

---

## Ledger (Double-Entry)

An **append-only, immutable record of financial movement** using double-entry accounting — every transaction has a matching debit and credit that sum to zero.

### Principles

| Principle | Violation Consequence |
|:---|:---|
| **Append-only** | Editing entries destroys audit trail |
| **Debit = Credit** | Unbalanced entries mean lost or created money |
| **Corrections are new entries** | Deleting history is fraud, even if accidental |
| **Immutable history** | The past is needed by support, compliance, finance, and the customer |

### Ledger vs Balance Table

| Aspect | Ledger | Balance Table |
|:---|:---|:---|
| **Operation** | Append balanced entries | Overwrite a number |
| **Correction** | Post a reversal entry | Quietly edit the past |
| **Auditability** | Full movement history | Last value only |
| **Debit = Credit** | Enforced | Not enforced |

> **The golden rule of fintech**: "The ledger is the truth. The balance is a derived view."

**Also see**: [CQRS & Event-Driven: Ledger](cqrs-event-driven.md#ledger), [Projection](cqrs-event-driven.md#projection) · [Reconciliation](#reconciliation)
