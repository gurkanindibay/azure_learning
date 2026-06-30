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
| Bank Adapter | [`#bank-adapter`](#bank-adapter) |
| Debit Card Authorization | [`#debit-card-authorization`](#debit-card-authorization) |
| Financial States | [`#financial-states`](#financial-states) |
| ISO 8583 | [`#iso-8583`](#iso-8583) |
| KYC (Know Your Customer) | [`#kyc-know-your-customer`](#kyc-know-your-customer) |
| Ledger (Double-Entry) | [`#ledger-double-entry`](#ledger-double-entry) |
| Limit Reservation | [`#limit-reservation`](#limit-reservation) |
| Merchant Onboarding | [`#merchant-onboarding`](#merchant-onboarding) |
| Payment Gateway | [`#payment-gateway`](#payment-gateway) |
| Payment Method Aggregation | [`#payment-method-aggregation`](#payment-method-aggregation) |
| Payment Processor | [`#payment-processor`](#payment-processor) |
| Real-Time Balance Checking | [`#real-time-balance-checking`](#real-time-balance-checking) |
| Reconciliation | [`#reconciliation`](#reconciliation) |
| Risk Actions | [`#risk-actions`](#risk-actions) |
| Settlement | [`#settlement`](#settlement) |
| Smart Routing | [`#smart-routing`](#smart-routing) |
| Transaction Reversal | [`#transaction-reversal`](#transaction-reversal) |

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

## ISO 8583

The **international standard for financial transaction card-originated messages** — the binary protocol used by card networks and core banking systems to exchange authorization, financial, and reversal messages between acquirers and issuers.

### Key Characteristics
- **Binary protocol** — compact, fixed-format messages optimized for low-latency financial networks
- **Standard message types**: 0100 (authorization request), 0110 (authorization response), 0200 (financial request), 0420 (reversal request)
- **Bitmap-based fields**: each message includes a bitmap indicating which data elements are present
- **Legacy but pervasive**: still used by most traditional banks' core banking systems worldwide

### When to Use
- Integrating with legacy core banking systems that speak ISO 8583 natively
- High-volume payment switches where binary protocol efficiency matters
- Debit card networks and ATM/POS transaction processing

### When NOT to Use
- Modern/digital-only banks that expose REST APIs — prefer JSON/HTTPS for simplicity
- When the integration team lacks ISO 8583 expertise — the learning curve is steep

### Also see
- [Bank Adapter](#bank-adapter) — the abstraction layer that hides ISO 8583 complexity
- [Debit Card Authorization](#debit-card-authorization) — the use case that drives ISO 8583 integration

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

## Real-Time Balance Checking

The **architectural requirement** that every debit card transaction authorization must verify the account balance against the issuing bank's live core banking system — never against a cached or projected balance. Cached balances serve only the non-critical balance inquiry API.

### Key Characteristics
- **Authorization path**: always fetches live balance from the bank; cache is never the authority for money movement
- **Write-through cache for inquiries**: after a successful debit, immediately write the new balance to cache — the cache is always as fresh as the last transaction
- **Cache key**: `balance:{account_number}` — per-account, distributed (Redis)
- **Cache used only for display**: balance inquiry API reads from cache; if cache miss, falls back to bank

### When to Use
- Debit card systems where balance accuracy is non-negotiable for every transaction
- High-volume systems that need fast balance inquiries without hitting the bank for every display

### When NOT to Use
- Credit card systems that check credit limits rather than account balances
- Closed-loop wallet systems where the balance is internal and strongly consistent by design

### Also see
- [Debit Card Authorization](#debit-card-authorization) — the full authorization pipeline
- [Write-Through Cache](../reference-dictionary/caching.md#write-through) — the caching pattern used
- [CQRS: Ledger vs Balance](../reference-dictionary/cqrs-event-driven.md#ledger) — the deeper principle (ledger is truth, balance is derived)

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

## Bank Adapter

An **architectural component** that abstracts differences between bank protocols (ISO 8583, REST, SOAP) behind a common interface, allowing the authorization service to communicate with any bank uniformly regardless of the underlying protocol.

### Key Characteristics
- **Common interface** — `verifyPIN`, `checkBalance`, `debitAccount`, `creditAccount`, `reverseTransaction`
- **Protocol-specific handlers** — one implementation per protocol (ISO 8583 handler, REST handler, SOAP handler)
- **Per-bank connection pooling** — 10–50 connections per bank, reused across requests
- **Per-bank circuit breaker** — isolates bank failures so one slow bank doesn't degrade the entire system

### When to Use
- Integrating with multiple banks that use different protocols
- When new banks must be onboarded without modifying the core authorization logic
- Payment systems where bank protocol diversity is a given, not a design choice

### When NOT to Use
- Single-bank systems where protocol abstraction adds unnecessary complexity
- When all banks use the same protocol and there is no diversity to abstract

### Also see
- [ISO 8583](#iso-8583) — one of the protocols the adapter abstracts
- [Adapter Pattern](../reference-dictionary/architecture-patterns.md#adapter-pattern) — the generic GoF pattern this implements
- [Circuit Breaker](resilience.md#circuit-breaker) — the per-bank failure isolation mechanism

---

## Debit Card Authorization

The **real-time process** of validating a debit card transaction through multiple sequential gates: card status check, PIN verification, limit enforcement, balance inquiry, and bank debit — all within sub-second latency.

### Key Characteristics
- **Multi-stage pipeline**: card status → PIN → limits → balance → bank debit, in strict order
- **Fail-fast rejection**: cheap, deterministic checks (card blocked, limit exceeded) run before expensive bank API calls
- **PIN verification via HSM**: PIN never in plaintext; verified through encrypted comparison
- **Real-time balance check**: always fetches live balance from the issuing bank, never authorizes against cache

### When to Use
- Debit card transactions at POS terminals, ATMs, and online gateways
- Any payment flow requiring PIN + balance + limits in a single authorization decision

### When NOT to Use
- Credit card authorization, which involves credit limit checks rather than balance checks
- Pre-authorized recurring payments where PIN is not required per transaction

### Also see
- [Real-Time Balance Checking](#real-time-balance-checking) — the balance verification step in the pipeline
- [PIN Verification](../reference-dictionary/hsm-cryptography.md#pin-verification) — the PIN security component
- [Limit Reservation](#limit-reservation) — the limit enforcement step
- [Transaction Reversal](#transaction-reversal) — what happens when authorization succeeds but the transaction later fails

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

---

## Merchant Onboarding

The **end-to-end process** of verifying a merchant's identity and business legitimacy before allowing them to accept payments through a gateway. Combines KYC, risk scoring, account provisioning, and API credential issuance.

### Key Characteristics
- **Document collection**: business registration, tax ID, bank details, address proof
- **Automated verification**: OCR extraction + external data source validation
- **Risk scoring**: automated score drives approve / manual-review / reject decision
- **API key generation**: cryptographically secure keys, SHA256 hash stored, plain key shown once

### When to Use
- Any platform that lets third-party merchants collect money from customers
- Before enabling live transactions; test credentials can be issued earlier

### When NOT to Use
- For closed-loop wallet systems where the operator is the only merchant
- When regulatory jurisdiction does not require merchant verification

### Also see
- [KYC](#kyc-know-your-customer) — the identity-verification sub-process
- [Payment Gateway](#payment-gateway) — the system merchants are onboarded into

---

## Payment Method Aggregation

The **architectural pattern** of supporting multiple payment instruments — cards, UPI, wallets, net banking — through a single unified gateway interface, abstracting method-specific complexity from merchants.

### Key Characteristics
- **Unified API**: one endpoint initiates payments regardless of underlying method
- **Method-specific routing**: each method maps to one or more provider integrations
- **Fall-forward**: if a method fails, the customer can retry with another method
- **Method distribution tracking**: understand customer preference and provider performance per method

### When to Use
- E-commerce, SaaS billing, or any checkout that must maximize payment success rate
- Markets where customers strongly prefer local payment methods (UPI in India, iDEAL in Netherlands)

### When NOT to Use
- Single-method systems where aggregation adds no value
- When method-specific compliance requirements conflict with unified processing

### Also see
- [Payment Gateway](#payment-gateway) · [Smart Routing](#smart-routing)

---

## Settlement

The **process of transferring cleared funds from the gateway or processor to the merchant's bank account** after deducting fees. Settlement cycles define how long the merchant waits to receive money.

### Key Characteristics
- **Settlement cycles**: T+1 (next day), T+2 (two days), T+0 (same day — premium)
- **Net settlement**: total transaction amount minus gateway fees, refunds, and chargebacks
- **Reconciliation prerequisite**: settlement should only happen after transactions are reconciled
- **Dispute handling**: settled funds may be clawed back for chargebacks or fraud

### When to Use
- Any payment system where the merchant does not receive funds in real time
- When risk management requires a holding period before releasing funds

### When NOT to Use
- Real-time peer-to-peer transfers where funds move directly between accounts
- Closed-loop systems where balance is internal and never leaves the platform

### Also see
- [Payment Processor](#payment-processor) — the entity that initiates settlement
- [Reconciliation](#reconciliation) — the verification step before settlement

---

## Smart Routing

A **multi-factor scoring algorithm** that selects the optimal payment provider for each transaction based on real-time metrics rather than static rules.

### Key Characteristics
- **Scored factors**: cost, latency, success rate, provider health, current load, merchant preference
- **Normalization**: lower-is-better metrics (cost, latency) use inverse normalization; higher-is-better (success rate) use direct
- **Health override**: circuit-breaker OPEN forces provider score to zero regardless of other factors
- **Decision caching**: identical routing contexts cached for 1–5 minutes to reduce compute at scale

### When to Use
- Multi-provider payment gateways optimizing for cost, success rate, or latency
- Peak traffic events where provider performance diverges significantly

### When NOT to Use
- Single-provider setups where there is no choice
- When regulatory or contractual requirements mandate a specific provider for certain transactions

### Also see
- [Payment Gateway](#payment-gateway) · [Circuit Breaker](resilience.md#circuit-breaker) · [Payment Method Aggregation](#payment-method-aggregation)

---

## Transaction Reversal

The **corrective operation** that reverses a previously authorized debit when the downstream transaction fails after the bank has already debited the account. Reversals are posted as new ledger entries — never as deletions or mutations of the original transaction.

### Key Characteristics
- **Confirm before reversing**: on timeout or ambiguous bank response, poll the bank first — don't auto-reverse without knowing the outcome
- **Idempotency guard**: each reversal has a unique `reversal_id`; duplicate reversal requests return the existing result
- **Retry with backoff**: max 3 retries with 30-second timeout; if all fail, flag for manual intervention
- **Reversal types**: FULL (entire amount) or PARTIAL (partial refund/correction)

### When to Use
- Debit card transactions that fail after the bank has debited (network error, merchant cancellation)
- Dispute resolution where investigation finds in the customer's favor
- Any money movement system where "the money left but the service wasn't delivered"

### When NOT to Use
- As a substitute for idempotency — reversals fix problems; idempotency prevents them
- For transactions that were definitively declined by the bank (no money moved, nothing to reverse)

### Also see
- [Debit Card Authorization](#debit-card-authorization) — the authorization that may need reversing
- [Risk Actions](#risk-actions) — reversals should be posted as new entries, not mutations
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency) — the guard that prevents double reversals
- [Settlement](#settlement) — reversals affect settlement calculations
