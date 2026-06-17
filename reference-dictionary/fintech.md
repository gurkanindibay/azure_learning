---
type: Reference
title: "Fintech-Specific Terms"
description: "The continuous process of verifying that **internal records match external reality** — comparing the ledger against payment rails, settlement files, and provider responses. Reconciliation detects m..."
timestamp: 2026-06-14T00:00:00Z
---

# Fintech-Specific Terms

> **Domain**: Financial technology patterns — reconciliation, limits, risk decisions, ledger design, and financial state management.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Financial States | [`#financial-states`](#financial-states) |
| KYC (Know Your Customer) | [`#kyc-know-your-customer`](#kyc-know-your-customer) |
| Ledger (Double-Entry) | [`#ledger-double-entry`](#ledger-double-entry) |
| Limit Reservation | [`#limit-reservation`](#limit-reservation) |
| Payment Gateway | [`#payment-gateway`](#payment-gateway) |
| Payment Processor | [`#payment-processor`](#payment-processor) |
| Reconciliation | [`#reconciliation`](#reconciliation) |
| Risk Actions | [`#risk-actions`](#risk-actions) |

---

## Payment Gateway

The **frontend-facing component** that collects and encrypts payment instrument data, authenticates the payer, and requests an authorization from the downstream processor or acquirer. It is the "bouncer" at the entrance of the payment flow.

### Key Characteristics
- **Encrypts sensitive data** (card number, CVV) using TLS and tokenization before forwarding
- **Authenticates the payer** through credentials, 3D Secure, or biometric verification
- **Routes the authorization request** to the appropriate processor or acquirer
- **Narrows PCI-DSS scope** for merchants by keeping raw card data out of merchant systems

### When to Use
- E-commerce checkouts, mobile wallets, and any merchant-facing payment collection
- Multi-processor setups where one gateway abstracts several back-end processors

### When NOT to Use
- As the component that actually moves money or settles with card networks
- As a substitute for processor-level reconciliation and settlement reporting

### Also see
- [Payment Processor](#payment-processor) — the engine that moves money
- [PCI-DSS](../reference-dictionary/hsm-cryptography.md#pci-dss-payment-card-industry-data-security-standard) — the compliance standard gateways help contain

---

## Payment Processor

The **back-end engine** that routes authorization and settlement messages between the merchant, card networks (Visa, Mastercard), and issuing banks. It is the "club infrastructure" that actually moves money from payer to merchant.

### Key Characteristics
- **Talks to card networks and banks** to authorize, capture, and settle transactions
- **Manages merchant settlement** — moving funds to the merchant account after clearing
- **Handles reversals, refunds, and chargebacks** through the card-network message flows
- **Is usually PCI-DSS Level 1 compliant** and stores/tokenizes sensitive instruments

### When to Use
- Any system that must clear and settle card payments
- When the business needs network-level routing, retries, and dispute management

### When NOT to Use
- For simple payer authentication or data collection (use a payment gateway)
- When the only requirement is wallet/top-up movements inside a closed loop

### Also see
- [Payment Gateway](#payment-gateway) — the front-door collector
- [Ledger (Double-Entry)](#ledger-double-entry) — how the system records the movement

---

## KYC (Know Your Customer)

The **regulatory process** of verifying a customer's identity before allowing them to use financial services. KYC reduces fraud, money laundering, and terrorist financing risk.

### Key Characteristics
- **Identity verification** — government ID, selfie matching, document liveness checks
- **Risk scoring** — sanctions lists, politically exposed persons (PEP), adverse media
- **Ongoing monitoring** — periodic re-verification and transaction monitoring
- **Jurisdiction-specific** — different rules per country/regulator

### When to Use
- Onboarding for wallets, bank accounts, lending, trading, or high-value payments
- Before enabling withdrawals, cross-border transfers, or merchant payouts

### When NOT to Use
- For anonymous or low-risk product flows where regulation does not require it
- As a one-time check; KYC is a lifecycle process, not a single gate

### Also see
- [PCI-DSS](../reference-dictionary/hsm-cryptography.md#pci-dss-payment-card-industry-data-security-standard) — payment-card security standard
- [Risk Actions](#risk-actions) — how risk decisions become new ledger entries

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
