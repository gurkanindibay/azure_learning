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
| Balance Snapshot | [`#balance-snapshot`](#balance-snapshot) |
| Bank Adapter | [`#bank-adapter`](#bank-adapter) |
| Business Identity | [`#business-identity`](#business-identity) |
| Clearing Account | [`#clearing-account`](#clearing-account) |
| Debit Card Authorization | [`#debit-card-authorization`](#debit-card-authorization) |
| Financial States | [`#financial-states`](#financial-states) |
| ISO 8583 | [`#iso-8583`](#iso-8583) |
| KYC (Know Your Customer) | [`#kyc-know-your-customer`](#kyc-know-your-customer) |
| Ledger (Double-Entry) | [`#ledger-double-entry`](#ledger-double-entry) |
| Limit Reservation | [`#limit-reservation`](#limit-reservation) |
| Merchant Onboarding | [`#merchant-onboarding`](#merchant-onboarding) |
| Merchant Transaction Identifier | [`#merchant-transaction-identifier`](#merchant-transaction-identifier) |
| Payment Gateway | [`#payment-gateway`](#payment-gateway) |
| Payment Method Aggregation | [`#payment-method-aggregation`](#payment-method-aggregation) |
| Payment Processor | [`#payment-processor`](#payment-processor) |
| Real-Time Balance Checking | [`#real-time-balance-checking`](#real-time-balance-checking) |
| Reconciliation | [`#reconciliation`](#reconciliation) |
| Retry Identity | [`#retry-identity`](#retry-identity) |
| Risk Actions | [`#risk-actions`](#risk-actions) |
| Settlement | [`#settlement`](#settlement) |
| Smart Routing | [`#smart-routing`](#smart-routing) |
| Transaction Reversal | [`#transaction-reversal`](#transaction-reversal) |
| Multi-Factor Model (Fama-French) | [`#multi-factor-model`](#multi-factor-model) |
| Newey-West t-statistic | [`#newey-west-t-statistic`](#newey-west-t-statistic) |
| Risk Parity | [`#risk-parity`](#risk-parity) |
| Factor Decomposition | [`#factor-decomposition`](#factor-decomposition) |
| Hidden Markov Model (Regime Detection) | [`#hidden-markov-model-regime`](#hidden-markov-model-regime) |
| LMAX Disruptor | [`#lmax-disruptor`](#lmax-disruptor) |
| Order Book | [`#order-book`](#order-book) |
| Matching Engine | [`#matching-engine`](#matching-engine) |
| Price-Time Priority (FIFO Matching) | [`#price-time-priority-fifo-matching`](#price-time-priority-fifo-matching) |
| SWIFT Network | [`#swift-network`](#swift-network) |
| ISO 20022 | [`#iso-20022`](#iso-20022) |
| Kernel Bypass (DPDK/Solarflare) | [`#kernel-bypass-dpdksolarflare`](#kernel-bypass-dpdksolarflare) |

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

## Retry Identity

A **per-execution identifier that represents one specific attempt of a business action** and is reused across retries of that same attempt. The most common implementation is an idempotency key.

### Key Characteristics
- **Generated once per attempt** and resent with every retry of that attempt
- **Different from business identity**: a customer may create one `OrderId` but trigger multiple payment attempts with different retry identities
- **Stored atomically** so that duplicate retries of the same attempt return the original result
- **Has a defined lifetime** matching the client retry window; stale keys may be cleaned up

### When to Use
- Safe retries of mutating operations in distributed systems where timeouts and network failures are expected
- Coordinating outcome with external payment gateways and providers

### When NOT to Use
- As a replacement for business-identifier uniqueness — a new retry identity for an already-completed order can still cause a duplicate charge
- When the operation is inherently non-idempotent and replay would change the outcome

### Also see
- [Business Identity](#business-identity) — the stable business-object identifier
- [Idempotency-Key](../reference-dictionary/api-design.md#idempotency-key) — a concrete retry-identity mechanism
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency)

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

## Balance Snapshot

A periodic, materialized point-in-time record of an account's balance anchored to a specific ledger entry (`as_of_entry_id`). Used to accelerate derived balance computations in append-only ledgers by summing only the unaggregated tail entries (`snapshot.balance + SUM(tail entries)`), without treating the snapshot as the authoritative source of truth.

### How Balance Snapshots Are Maintained
1. **Trigger Strategies**:
   - **Threshold-Based (Tail Count)**: Workers monitor entry volume and trigger a snapshot whenever an account accumulates more than $N$ unaggregated entries (e.g., every 500 or 1,000 entries).
   - **Time-Based (Periodic/EOD)**: Scheduled jobs (hourly or daily End-of-Day) create regular balance checkpoints across all active accounts.
   - **Asynchronous Event-Driven (CDC)**: A Change Data Capture stream (e.g., Debezium, Kafka) consumes append-only entries and incrementally advances snapshots in worker queues without impacting the write path.
2. **Maintenance & Monotonic Advancement**:
   - The worker calculates the delta from the last snapshot point: `new_balance = snapshot.balance + SUM(entries WHERE id > snapshot.as_of_entry_id)` and records the new high-water mark `MAX(entry_id)`.
   - Updates enforce monotonicity (`WHERE new_as_of_entry_id > current_as_of_entry_id`), ensuring background workers remain idempotent and immune to out-of-order execution.
3. **Rolling vs. Historical Snapshots**:
   - **Rolling Operational Snapshot**: A single mutable record per account (`balance_snapshots`) updated continuously to keep live balance reads $O(1)$.
   - **Historical EOD Snapshots**: Immutable daily audit records (`daily_balance_snapshots(account_id, date, closing_balance, eod_entry_id)`) used for regulatory compliance, statement generation, and point-in-time time-travel queries.

### Key Characteristics
- **Performance optimization, not source of truth**: If the snapshot is deleted, corrupted, or stale, the exact authoritative balance is always recoverable from the immutable ledger entries
- **Asynchronous generation**: Materialized via background jobs or worker queues without blocking write transactions
- **Bounded query overhead**: Keeps balance query latency $O(1)$ by constraining the number of entries summed in the query tail
- **Monotonic watermarking**: Anchored to immutable entry IDs (`as_of_entry_id`), ensuring deterministic re-calculation

### When to Use
- Append-only ledgers and event-sourced accounts with high transaction volume
- Read-heavy account dashboard views in banking and digital wallet platforms
- Financial systems requiring point-in-time historical balance lookups for month-end close and audit reports

### When NOT to Use
- Systems storing mutable balances directly on the account entity row
- Accounts with very low transaction volume where on-demand aggregation of all entries is already instantaneous

### Also see
- [Ledger (Double-Entry)](#ledger-double-entry) · [Append-Only Ledger](data-concurrency.md#append-only-ledger) · [Clearing Account](#clearing-account) · [Reconciliation](#reconciliation)

---

## Business Identity

A **stable identifier that represents what the customer is paying for** — independent of any single execution attempt or retry. Examples include `OrderId`, `PaymentIntentId`, `BookingId`, and `InvoiceId`.

### Key Characteristics
- **Tied to the business action**, not the HTTP request or message delivery
- **Survives retries** because the customer intent does not change when the network times out
- **Enforced at the database layer** through unique constraints that prevent the same business object from being processed twice
- **Different from retry identity**: the same order may be retried many times, but it is still one order

### When to Use
- Payment, booking, and invoicing flows where the business object must be processed exactly once regardless of retries
- As a defense-in-depth guard when the idempotency key may vary because of client bugs or different clients

### When NOT to Use
- As a substitute for retry identity when the goal is to replay the same execution attempt safely
- When business rules intentionally allow multiple payments against the same order (e.g., partial payments with separate intents)

### Also see
- [Retry Identity](#retry-identity) — the execution-attempt identifier that complements business identity
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency) — the property both identifiers help enforce

---

## Clearing Account

A dedicated intermediate ledger account used in multi-step, multi-currency, or distributed cross-shard transactions to represent funds in transit. In a distributed Saga (e.g., transferring funds across database shards), money is first transferred from the sender to the clearing account on Shard A, then from the clearing account to the recipient on Shard B.

```text
Step 1 (Shard A): Alice Account: -$100 | In-Flight Clearing Account: +$100 (Sum = 0)
Step 2 (Shard B): In-Flight Clearing Account: -$100 | Bob Account: +$100 (Sum = 0)
```

### Key Characteristics
- **Continuous zero-sum balance invariant**: Every partial transaction step writes a valid debit-credit pair summing to zero, preventing "disappearing" or untracked money
- **Auditable in-flight visibility**: In-flight capital is a queryable balance rather than an ephemeral network state; non-zero clearing balances trending upward immediately alert on stuck transactions
- **Eliminates 2PC distributed locks**: Replaces blocking two-phase commit across shards with an asynchronous, eventually consistent Saga backed by double-entry ledger reconciliation

### When to Use
- Distributed banking architectures where payer and payee accounts reside on separate database shards
- Payment gateway settlements, FX conversions, and inter-bank clearing operations

### When NOT to Use
- Single-database systems where atomic local transactions span both accounts simultaneously
- Non-financial messaging workflows where strict balance preservation is not applicable

### Also see
- [Ledger (Double-Entry)](#ledger-double-entry) · [Reconciliation](#reconciliation) · [Saga Pattern](data-concurrency.md#saga-pattern)
- [Idempotency-Key](../reference-dictionary/api-design.md#idempotency-key) — a common retry-identity implementation

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

## Merchant Transaction Identifier

A **stable reference generated by the merchant and sent to the payment gateway or processor** so the provider can recognize retries of the same transaction and return the existing result instead of charging again.

### Key Characteristics
- **Generated by the merchant system**, not the provider
- **Sent with every authorization or charge request** to the gateway
- **Recognized by the gateway** across the provider's retention window, enabling idempotency even when the merchant loses local state
- **Different from the provider's own transaction ID**: the merchant reference is known before the call and survives crashes

### When to Use
- Payment flows where the merchant service may crash after the gateway succeeds but before the result is persisted locally
- Integrations with payment providers that support merchant-supplied transaction references

### When NOT to Use
- When the payment provider does not support or honor merchant transaction references
- As the only duplicate guard — combine with local idempotency keys and business-identifier constraints for defense in depth

### Also see
- [Payment Gateway](#payment-gateway) — the component that receives the merchant transaction identifier
- [Transaction Reversal](#transaction-reversal) — the corrective operation when the provider cannot deduplicate
- [Idempotency](../reference-dictionary/cqrs-event-driven.md#idempotency)

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

---

## Multi-Factor Model (Fama-French)

A **quantitative finance model** that decomposes stock returns into systematic drivers plus a residual (alpha). The foundational Fama-French three-factor model (1993) uses market beta, size (SMB), and value (HML). Carhart added momentum (1997). Fama-French added profitability (RMW) and investment (CMA) in 2015. Modern hedge funds run seven-factor stacks.

$$R_i - R_f = \alpha + \beta_1(R_m - R_f) + \beta_2(\text{SMB}) + \beta_3(\text{HML}) + \beta_4(\text{MOM}) + \beta_5(\text{RMW}) + \beta_6(\text{CMA}) + \epsilon$$

### Key Characteristics
- **Systematic factors**: Market, size, value, momentum, profitability, investment, low volatility
- **Alpha (α)**: The residual the model cannot explain — what quantitative strategies hunt
- **Factor construction**: Each factor computed independently from price and fundamental data
- **Out-of-sample validation**: Factors must work across multiple market regimes, not just one

### When to Use
- Quantitative portfolio construction and risk decomposition
- Backtesting trading strategies against known risk premia
- Separating genuine alpha from repackaged style exposure

### When NOT to Use
- Short-horizon trading where factor premia may not materialize
- Single-stock analysis without portfolio context
- Markets where factor data is unavailable or unreliable

### Also see
- [Factor Decomposition](#factor-decomposition)
- [Risk Parity](#risk-parity)

---

## Newey-West t-statistic

A **statistical test with autocorrelation-robust standard errors**, used to assess whether a factor's returns are statistically significant after accounting for serial correlation in financial time series. Standard t-tests underestimate standard errors when returns are autocorrelated; Newey-West corrects for this.

### Key Characteristics
- **Autocorrelation-robust**: Accounts for serial correlation up to a specified lag
- **Bootstrap validation**: Typically paired with 10,000-iteration bootstrap resampling for robustness
- **Threshold**: Common significance threshold is t-stat > 2.5 for factor survival
- **In-sample vs out-of-sample**: Degradation above 30% between in-sample and out-of-sample performance typically triggers factor rejection

### When to Use
- Evaluating factor performance in financial time series
- Any statistical test on overlapping or serially correlated returns
- Backtesting where standard errors must account for return autocorrelation

### When NOT to Use
- Independent, non-autocorrelated samples where standard t-tests suffice
- Very short time series where autocorrelation estimation is unreliable
- Non-financial data without serial dependence concerns

### Also see
- [Multi-Factor Model](#multi-factor-model)
- [Factor Decomposition](#factor-decomposition)

---

## Risk Parity

A **portfolio construction method** that allocates weights based on each asset's risk contribution rather than capital allocation. Equal risk contribution ensures no single factor or asset dominates portfolio volatility, even if capital weights are unequal.

### Key Characteristics
- **Risk-weighted, not capital-weighted**: Low-volatility assets get higher capital weights to equalize risk contribution
- **Neutrality constraints**: Often combined with sector, beta, and dollar neutrality
- **Long-short compatible**: Works for both long-only and long-short portfolios
- **Factor-level application**: Applied to factor exposures as well as individual securities

### When to Use
- Multi-factor portfolios where factors have different volatility profiles
- Portfolios requiring balanced risk exposure across diverse strategies
- Institutional portfolios where risk budgeting is a formal constraint

### When NOT to Use
- Single-factor or concentrated portfolios where risk diversification is not the goal
- When accurate covariance estimation is impossible (very short history, regime shifts)
- High-frequency strategies where risk parity rebalancing costs exceed benefits

### Also see
- [Multi-Factor Model](#multi-factor-model)
- [Factor Decomposition](#factor-decomposition)

---

## Factor Decomposition

The process of **regressing portfolio returns against style and macro factors** to isolate what portion of returns comes from known risk premia versus genuine alpha. Only signals where residual alpha survives factor decomposition are considered new alpha; everything else is repackaged style exposure.

### Key Characteristics
- **Regress against known factors**: Market, size, value, momentum, profitability, investment, low volatility
- **Style + macro factors**: Broader decomposition includes sector, currency, and macro-economic factors
- **Residual alpha**: The intercept after controlling for all known factors — the true signal
- **t-statistic threshold**: Residual alpha must exceed statistical significance threshold (typically t > 2.5)

### When to Use
- Validating that a trading strategy produces genuine alpha, not repackaged beta
- Risk attribution in multi-strategy portfolios
- Post-trade analysis to understand return sources

### When NOT to Use
- Single-factor strategies where the factor IS the strategy
- Pre-trade signal generation (factor decomposition is a validation step, not a construction step)
- When the factor set is incomplete and residual alpha may still contain unknown factor exposure

### Also see
- [Multi-Factor Model](#multi-factor-model)
- [Newey-West t-statistic](#newey-west-t-statistic)
- [Risk Parity](#risk-parity)

---

## Hidden Markov Model (Regime Detection)

A **statistical model that segments time series into discrete hidden states (regimes)** based on observable data like volatility and returns. In quantitative finance, HMMs detect whether the market is in a low-volatility bull, high-volatility bear, or transition regime — and kill factors that only work in one regime.

### Key Characteristics
- **Hidden states**: The regime (bull, bear, transition) is not directly observable; inferred from data
- **Observable emissions**: Volatility, returns, and other market data drive state inference
- **Transition probabilities**: Model learns how likely the market is to switch between regimes
- **Regime robustness gate**: A factor that only performs in one regime is beta to that regime, not alpha

### When to Use
- Validating strategy robustness across bull, bear, and sideways markets
- Regime-aware portfolio construction and risk management
- Detecting structural breaks that invalidate historical factor performance

### When NOT to Use
- Very short time series where regime estimation is unreliable
- Strategies with holding periods shorter than the regime detection window
- When regime transitions are too frequent for the HMM to stabilize

### Also see
- [Multi-Factor Model](#multi-factor-model)
- [Factor Decomposition](#factor-decomposition)

---

## LMAX Disruptor

A **high-performance inter-thread messaging framework** designed for low-latency financial trading platforms. It replaces traditional concurrent queues (which suffer from lock contention and cache-line bouncing) with a lock-free, pre-allocated circular ring buffer that uses memory barriers and cache-line padding to achieve millions of operations per second with deterministic sub-microsecond latency.

### Key Characteristics
- **Pre-allocated ring buffer**: Power-of-two array eliminating garbage collection pauses and dynamic allocation overhead
- **Lock-free sequence numbers**: Producers and consumers claim slots using atomic CAS/memory barriers without OS mutex locks
- **Cache-line padding**: Eliminates false sharing by ensuring independent sequence variables sit on distinct CPU L1/L2/L3 cache lines (typically 64 bytes)
- **Batching effect**: Consumers naturally batch-read all available sequence slots when running behind, creating an adaptive backpressure valve

### When to Use
- Ultra-low-latency financial matching engines, crypto exchanges, and digital wallets
- High-throughput event processing pipelines requiring in-memory deterministic sequencing
- Core processing loops where GC pauses or kernel lock context switches cause unacceptable tail latencies

### When NOT to Use
- Standard web request handling where network I/O dominates processing time (>10 ms)
- Multi-node distributed messaging where Kafka, RabbitMQ, or network queues are required
- Low-throughput applications where standard language concurrency primitives (`BlockingQueue`, `Channel`) are much simpler

### Also see
- [Matching Engine](#matching-engine) · [Order Book](#order-book) · [Deterministic Processing](cqrs-event-driven.md#deterministic-processing)

---

## Order Book

A **real-time electronic data structure** that organizes and records all outstanding limit buy orders (bids) and sell orders (asks) for a specific financial asset, sorted by price level and arrival timestamp.

### Key Characteristics
- **Bids and Asks separation**: Bids (highest buy price first, descending) and Asks (lowest sell price first, ascending)
- **Price Levels**: Aggregates total volume available at discrete price points
- **Level 2 / Level 3 Market Data**: Level 2 displays aggregate depth per price level; Level 3 exposes individual orders with unique order IDs
- **In-memory data structures**: Typically implemented with doubly-linked lists bucketed in a B-Tree or radix tree for $O(1)$ order cancellation and $O(1)$ head execution

### When to Use
- Stock, foreign exchange, commodity, and cryptocurrency exchange architectures
- Internal matching and crossing networks in high-frequency trading market makers
- Limit order simulation in quantitative backtesting engines

### When NOT to Use
- Simple inventory reservation systems (e-commerce, hotel booking) where items do not have continuous bid/ask pricing
- Systems where trades execute purely against an automated market maker (AMM) bonding curve without an order book

### Also see
- [Matching Engine](#matching-engine) · [Price-Time Priority (FIFO Matching)](#price-time-priority-fifo-matching) · [LMAX Disruptor](#lmax-disruptor)

---

## Matching Engine

The **core deterministic algorithmic engine of an electronic exchange** that continuously evaluates incoming market and limit orders against the existing Order Book to execute trades and generate fill reports.

### Key Characteristics
- **Deterministic state machine**: Processing the identical stream of order events from a journal produces the exact same execution sequence and account balances
- **Single-threaded core loop**: Avoids concurrency locking overhead by running order matching on a dedicated CPU core pinned to a single thread
- **Execution algorithms**: Supports Price-Time Priority (FIFO), Pro-Rata, and Pegged matching rules
- **Zero dynamic memory allocation**: Pre-allocates order structs at startup to eliminate latency spikes

### When to Use
- Financial exchanges, broker internalizers, and dark pools
- Digital wallet internal ledger balance matching
- High-frequency matching systems requiring predictable p99.99 latency < 10 microseconds

### When NOT to Use
- Distributed, loosely-coupled microservices where network round-trips make microsecond determinism irrelevant
- Asynchronous batch clearing systems where orders are collected and cleared periodically (call auctions)

### Also see
- [Order Book](#order-book) · [Price-Time Priority (FIFO Matching)](#price-time-priority-fifo-matching) · [LMAX Disruptor](#lmax-disruptor) · [Kernel Bypass (DPDK/Solarflare)](#kernel-bypass-dpdksolarflare)

---

## Price-Time Priority (FIFO Matching)

The **standard matching engine execution rule** where orders are prioritized first by the most competitive price, and among orders at identical prices, by the earliest arrival timestamp.

### Key Characteristics
- **Price priority first**: The highest bid (buy) and lowest ask (sell) always trade before less aggressive prices
- **Time priority second**: At a given price level, orders are filled strictly First-In, First-Out (FIFO)
- **Queue position retention**: Modifying an order's size downward preserves queue priority; increasing size or changing price moves the order to the back of the queue
- **Incentivizes liquidity**: Rewards market participants who supply early liquidity and narrow the bid-ask spread

### When to Use
- Equity, equity options, and cryptocurrency limit order books
- Any exchange system balancing fairness, transparency, and liquidity provisioning

### When NOT to Use
- Treasury and short-term interest rate futures markets that use **Pro-Rata** allocation (where fills are distributed proportionally to order size)
- Flash sales or ticket reservations where lottery or randomized queuing is preferred to avoid bot speed advantages

### Also see
- [Order Book](#order-book) · [Matching Engine](#matching-engine)

---

## SWIFT Network

The **Society for Worldwide Interbank Financial Telecommunication** messaging network: a secure, standardized global financial messaging infrastructure connecting over 11,000 financial institutions across 200+ countries. SWIFT does not hold funds or manage bank accounts; it securely transmits financial payment instructions between correspondent banks.

### Key Characteristics
- **Financial messaging, not settlement**: Transmits encrypted instructions; actual monetary settlement occurs across Nostro/Vostro bank accounts or central bank real-time gross settlement (RTGS) rails
- **BIC / SWIFT Code**: 8 or 11-character standardized Business Identifier Code identifying institutions globally
- **Legacy MT messages**: Fixed-format text messages (e.g., MT103 for customer transfers, MT202 for interbank transfers)
- **Migration to MX (ISO 20022)**: Modernizing toward rich XML-based financial information

### When to Use
- Cross-border interbank wire transfers and international remittances
- Trade finance, securities settlement notifications, and corporate treasury treasury reporting

### When NOT to Use
- Domestic retail real-time payment rails (e.g., FedNow, Pix, UPI, SEPA Instant) where domestic clearing houses are faster and cheaper
- Real-time peer-to-peer micropayments

### Also see
- [ISO 20022](#iso-20022) · [ISO 8583](#iso-8583) · [Clearing Account](#clearing-account) · [Settlement](#settlement)

---

## ISO 20022

An **international standard for electronic data interchange between financial institutions** that replaces fragmented, fixed-length legacy message formats (like SWIFT MT) with a unified, XML/JSON structured data dictionary across all financial business domains (payments, securities, cards, trade).

### Key Characteristics
- **Rich structured metadata**: Supports up to 9,000 characters per message with granular remittance details, ultimate debtor/creditor identities, and structured addresses
- **Standardized business areas**: `pacs` (Payment Clearing and Settlement, e.g., `pacs.008`), `pain` (Payment Initiation, e.g., `pain.001`), `camt` (Cash Management, e.g., `camt.053` bank statement)
- **Enhanced compliance & AML**: Unambiguous data fields reduce false positives in sanction screening and anti-money laundering filters
- **Global adoption mandate**: Adopted by SWIFT, FedNow, Target2, and international RTGS systems

### When to Use
- Next-generation payment gateways, real-time gross settlement engines, and banking APIs
- Corporate treasury integration requiring automated end-to-end invoice and remittance reconciliation

### When NOT to Use
- POS terminal transactions where bandwidth constraints favor ISO 8583 bitmap compactness
- Ultra-low latency internal microservice communication where Protobuf/FlatBuffers are orders of magnitude faster

### Also see
- [SWIFT Network](#swift-network) · [ISO 8583](#iso-8583) · [Reconciliation](#reconciliation)

---

## Kernel Bypass (DPDK/Solarflare)

A **networking architecture technique** that allows user-space applications to read and write network packets directly to and from the Network Interface Card (NIC) hardware buffers, completely bypassing the Linux kernel network stack (`sk_buff`, socket layer, and interrupt handlers).

### Key Characteristics
- **Zero OS context switches**: Eliminates syscall overhead and CPU interrupt handling through poll-mode drivers (PMD)
- **Zero-copy memory access**: Directly transfers network packets between NIC hardware and user-space ring buffers (DMA)
- **Hardware technologies**: Data Plane Development Kit (DPDK), Solarflare OpenOnload / EF_VI, RDMA (RoCE)
- **Deterministic microsecond latency**: Drops networking transit latency from ~10–50 microseconds (kernel socket) to sub-microsecond levels (~500–800 nanoseconds)

### When to Use
- High-frequency trading (HFT) matching engines and market data ticker plants
- Telco 5G user-plane network functions (UPF) and high-throughput software packet routers
- Ultra-high performance distributed storage engines (NVMe-over-Fabrics)

### When NOT to Use
- Standard web and enterprise applications where conventional kernel TCP/IP stacks and non-blocking epoll runtimes provide ample performance with full security isolation
- Virtualized multi-tenant environments where the kernel firewall (iptables/nftables) and OS network virtualization are strictly required

### Also see
- [Matching Engine](#matching-engine) · [LMAX Disruptor](#lmax-disruptor)
