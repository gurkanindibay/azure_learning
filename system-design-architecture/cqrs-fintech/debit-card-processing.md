---
type: System Design
title: "Debit Card Processing — Key Takeaways"
description: "Architectural patterns for real-time debit card processing: PIN verification, multi-protocol bank integration, real-time balance checking, limit enforcement, and transaction reversal at scale."
timestamp: 2026-06-30T00:00:00Z
---

# Debit Card Processing — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Designing a Debit Card Processing System](../../articles/cqrs-fintech/designing-debit-card-processing-system.md) — Arvind Kumar (CodeFarm), Feb 2026
> **Purpose**: Extract practical architectural patterns for real-time debit card processing — PIN security, multi-bank integration, balance accuracy under load, limit enforcement, and safe transaction reversal.
> **Also see**: [CQRS for Fintech](cqrs-fintech.md), [Global Payment System](global-payment-system.md), [Payment Gateway](payment-gateway.md), [Resilience Patterns](../resilience/resilience-patterns.md)
> **Dictionary**: [Reference Dictionary](../../reference-dictionary/) — definitions for [ISO 8583](../../reference-dictionary/fintech.md#iso-8583), [Debit Card Authorization](../../reference-dictionary/fintech.md#debit-card-authorization), [Real-Time Balance Checking](../../reference-dictionary/fintech.md#real-time-balance-checking), [Bank Adapter](../../reference-dictionary/fintech.md#bank-adapter), [Transaction Reversal](../../reference-dictionary/fintech.md#transaction-reversal), [PIN Verification](../../reference-dictionary/hsm-cryptography.md#pin-verification)
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging, §7.1 Reliability & Resilience

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`cqrs-27`](#cqrs-27-multi-stage-authorization-pipeline) | Coordinating PIN, limits, balance, and bank debit in one request | Multi-stage authorization pipeline with ordered validation gates |
| [`cqrs-28`](#cqrs-28-bank-adapter-framework-for-multi-protocol-integration) | 100+ banks using ISO 8583, REST, and SOAP simultaneously | Adapter pattern with per-bank protocol handlers and circuit breaker |
| [`cqrs-29`](#cqrs-29-balance-accuracy-never-authorize-against-cache) | Stale cache causing incorrect balance-based approvals | Never use cached balance for auth; write-through cache for inquiries only |
| [`cqrs-30`](#cqrs-30-pin-security-end-to-end-encryption--caching) | PIN exposed in transit or storage | End-to-end encryption + one-way hashing + short-TTL caching |
| [`cqrs-31`](#cqrs-31-multi-dimensional-transaction-limits) | Per-transaction, daily, withdrawal, and monthly limits simultaneously | Real-time limit tracking across dimensions with Redis + async DB |
| [`cqrs-32`](#cqrs-32-transaction-reversal-confirm-before-reversing) | Reversing a transaction that actually succeeded | Confirm failure outcome before reversing; idempotency guard first |
| [`cqrs-33`](#cqrs-33-circuit-breaker-per-bank-with-pending-state-recovery) | One slow bank degrading the entire system | Per-bank circuit breaker with pending transaction state and polling recovery |
| [`cqrs-34`](#cqrs-34-database-sharding-by-bank-id) | Single database bottleneck at 10,000+ TPS | Shard by bank_id + partition by date for horizontal write scaling |

---

## cqrs-27: Multi-Stage Authorization Pipeline

> **Source**: [Article §"Part 3: High-Level Architecture"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-3-high-level-architecture)

| | |
|:---|:---|
| **Problem** | A single debit card transaction requires card validation, PIN verification, limit checking, balance inquiry, and bank debit — all within sub-second latency. The order of these stages matters for both correctness and cost. |
| **Root cause** | Without a defined pipeline, expensive operations (bank API calls) may execute before cheap, deterministic rejections (card blocked, limit exceeded). |

### Authorization Pipeline (Ordered Gates)

```
Request → [1] Card Status Gate → [2] PIN Verification Gate → 
          [3] Limit Check Gate → [4] Balance Check Gate → 
          [5] Bank Debit → Response
```

| Gate | Check | Cost | Failure Action |
|:---|:---|:---|:---|
| **1. Card Status** | Is card ACTIVE? Not BLOCKED/EXPIRED? | DB lookup (cheap) | Decline immediately |
| **2. PIN Verification** | Does PIN hash match? Cached? | Cache or bank call | Decline, increment attempt counter |
| **3. Limit Check** | Within daily/per-txn/withdrawal limits? | Redis + DB | Decline with limit reason |
| **4. Balance Check** | Does bank confirm sufficient funds? | Bank API call | Decline with insufficient funds |
| **5. Bank Debit** | Debit account, get confirmation | Bank API call | Trigger reversal flow if fails |

> **Key insight**: Gates 1–3 are cheap and deterministic — reject early before making expensive bank calls. Gates 4–5 are expensive and external — only reach them when the transaction is almost certainly valid.

**Tradeoff**: Strict ordering prevents unnecessary bank calls but adds pipeline latency. The cheap gates must complete in < 50ms combined to leave budget for the bank calls.

---

## cqrs-28: Bank Adapter Framework for Multi-Protocol Integration

> **Source**: [Article §"Part 7: Bank Integration Architecture"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-7-bank-integration-architecture)

| | |
|:---|:---|
| **Problem** | 100+ banks use different protocols — some legacy (ISO 8583 binary), some modern (REST JSON), some SOAP — but the authorization service must treat them uniformly. |
| **Root cause** | Protocol diversity is inherent; building bank-specific logic into the core authorization service creates unmaintainable coupling. |

### Bank Adapter Strategy

```
Authorization Service
        │
        ▼
┌───────────────────┐
│  Bank Adapter      │  ← Common interface
│  Interface         │
└───┬───────┬───────┘
    │       │       │
    ▼       ▼       ▼
┌──────┐ ┌──────┐ ┌──────┐
│ ISO  │ │ REST │ │ SOAP │    ← Protocol-specific handlers
│ 8583 │ │ API  │ │      │
└──────┘ └──────┘ └──────┘
    │       │       │
    ▼       ▼       ▼
  Bank A  Bank B  Bank C
```

| Protocol | Format | Transport | Typical Banks | Complexity |
|:---|:---|:---|:---|:---|
| **ISO 8583** | Binary | TCP/sockets | Legacy core banking | High (specialized parsing) |
| **REST API** | JSON/XML | HTTPS | Modern/digital banks | Low |
| **SOAP** | XML/WSDL | HTTPS | Enterprise/legacy | Medium |

**Per-adapter concerns**: Connection pooling (10–50 connections per bank), circuit breaker (fail fast when bank is down), keep-alive (60s), timeout (5s).

**Tradeoff**: The adapter layer adds abstraction complexity but isolates protocol-specific code. A new bank protocol can be added without touching the authorization service.

---

## cqrs-29: Balance Accuracy — Never Authorize Against Cache

> **Source**: [Article §"Part 6: Real-Time Balance Checking"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-6-real-time-balance-checking)

| | |
|:---|:---|
| **Problem** | A cached balance says ₹10,000, so the system approves a ₹9,000 transaction — but the actual balance was ₹5,000 because a prior transaction hadn't propagated to the cache yet. |
| **Root cause** | Using a cached/projected balance as the authority for money-movement decisions. |

### The Invariant

```
TRANSACTION AUTHORIZATION:  Always fetch balance from bank (source of truth)
BALANCE INQUIRY API:        Use cached balance if available (via write-through)
```

| Data Path | Source | Consistency | Used For |
|:---|:---|:---|:---|
| **Authorization** | Bank API (live) | Strong (real-time) | Deciding whether to approve |
| **Balance Display** | Write-through cache | Eventually consistent | Showing the customer their balance |

### Write-Through Flow

1. Transaction authorization → fetch balance from bank (never cache)
2. Bank debits account, returns new balance
3. **Immediately** write new balance to cache (`balance:{account_number}`)
4. Next balance inquiry reads from cache
5. Next transaction authorization → fetch from bank again

> **Key insight**: The write-through pattern means the cache is always as fresh as the last transaction. It's never used for authorization, only for non-critical display. This is the same boundary that CQRS enforces for fintech: the command path (authorization) uses strong consistency; the query path (balance display) is eventually consistent.

**Tradeoff**: Every authorization hits the bank API — no latency savings from caching. But correctness for money movement is non-negotiable.

**Cross-reference**: See [cqrs-02: The Ledger Is Truth; Balance Is a Derived View](cqrs-fintech.md#cqrs-02-the-ledger-is-truth-balance-is-a-derived-view) for the deeper principle this applies.

---

## cqrs-30: PIN Security — End-to-End Encryption + Caching

> **Source**: [Article §"Part 5: PIN Verification & Security"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-5-pin-verification--security)

| | |
|:---|:---|
| **Problem** | PIN is the sole authentication factor for debit transactions — if compromised in transit, storage, or verification, the attacker can drain accounts. Yet PIN verification must be fast (< 200ms p95). |
| **Root cause** | Security and latency are in direct tension; caching helps latency but creates a window where a compromised PIN might be cached as "valid." |

### PIN Security Layers

| Layer | Mechanism | Never |
|:---|:---|:---|
| **Transit** | TLS 1.3 + AES-256 encryption | Send plaintext PIN over any channel |
| **Storage** | One-way hash (bcrypt/PBKDF2) | Store plaintext or reversible encryption |
| **Terminal** | Encrypt at point of entry | Expose PIN to terminal application memory |
| **Gateway** | Re-encrypt for bank-specific key | Expose PIN in application logs |
| **Verification** | Compare hash, not plaintext | Compare plaintext PIN values |
| **Caching** | 5-min TTL, encrypted cache keys | Cache beyond PIN change events |

### PIN Verification Caching Strategy

```
Cache key:    hash(card_number + transaction_timestamp)
TTL:          5 minutes (short, security-conscious)
Invalidation: Immediate on PIN change event
Storage:      Redis (distributed, encrypted keys)
```

> **Key insight**: PIN caching trades a 5-minute security window for significantly reduced bank load and improved latency. The window is deliberately short, and PIN change events force immediate invalidation. For the rare case where a stolen PIN is used within 5 minutes of a successful verification, the daily/per-transaction limits act as a secondary defense.

**Tradeoff**: Five minutes of cached "valid" PIN status is a calculated risk. The alternative — hitting the bank HSM for every PIN verification at 10,000 TPS — would either overload the HSM or blow the latency budget.

**Cross-reference**: See [cqrs-04: Limits Belong on the Command Side](cqrs-fintech.md#cqrs-04-limits-belong-on-the-command-side) — limits are the secondary defense when cached auth is wrong.

---

## cqrs-31: Multi-Dimensional Transaction Limits

> **Source**: [Article §"Part 8: Transaction Limits"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-8-transaction-limits)

| | |
|:---|:---|
| **Problem** | A single transaction must be checked against four independent limit dimensions simultaneously — daily, per-transaction, withdrawal, and monthly — each with different reset cadences and tracking granularity. |
| **Root cause** | Limits are not a single number; they are a multi-dimensional constraint space, and missing one check means a fraudulent transaction slips through. |

### Limit Dimensions

| Dimension | Example | Reset | Tracked In |
|:---|:---|:---|:---|
| **Per-Transaction** | ₹25,000 max | N/A (per call) | In-memory |
| **Daily Transaction** | ₹50,000/day | Midnight | Redis + DB |
| **Daily Withdrawal** | ₹20,000/day (ATM only) | Midnight | Redis + DB |
| **Monthly** | ₹500,000/month | Month start | DB |

### Limit Enforcement Strategy

```
1. Check per-transaction limit  →  Reject immediately if exceeded
2. Check daily usage + amount   →  Must stay under daily limit
3. Check withdrawal usage       →  Only if ATM transaction type
4. Check monthly usage          →  Async DB check (cached in Redis)
5. On approval: Update all limits atomically
   - Redis: immediate (real-time tracking)
   - DB: async (persistence)
```

> **Key insight**: Daily and withdrawal limits are tracked in Redis for sub-millisecond reads/writes, with async persistence to the database. This means a Redis failure could temporarily lose limit state — the tradeoff is that at 10,000 TPS, no relational database can handle limit reads for every transaction synchronously.

**Tradeoff**: Redis as the limit authority means limits are eventually persisted, not synchronously. A Redis crash between a successful transaction and the async DB write could allow a customer to slightly exceed their daily limit. The monthly limit (checked from DB) acts as a backstop.

---

## cqrs-32: Transaction Reversal — Confirm Before Reversing

> **Source**: [Article §"Part 11: Transaction Reversal"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-11-transaction-reversal)

| | |
|:---|:---|
| **Problem** | A transaction times out after the bank debited the account. The system doesn't know if the debit succeeded or failed. Triggering an automatic reversal could reverse a successful debit, effectively crediting the customer twice. |
| **Root cause** | Timeout ≠ failure. In distributed systems with external bank APIs, an ambiguous response (no response) must not be treated as a definitive failure. |

### Reversal Decision Matrix

| What Happened | What We Know | Action |
|:---|:---|:---|
| Bank returned explicit decline | Debit did NOT happen | No reversal needed |
| Bank returned explicit success + later failure | Debit happened, downstream failed | Reverse the debit |
| Bank timed out — no response | **Unknown** | Poll bank for status first |
| Network lost mid-transaction | **Unknown** | Transaction → PENDING; poll bank |

### Safe Reversal Flow

```
Transaction fails/timeout
        │
        ▼
┌───────────────────────────┐
│ Is outcome known?         │
│ - Explicit failure? → Reverse │
│ - Ambiguous/Timeout? → Poll │
└───────────────────────────┘
        │ (ambiguous)
        ▼
┌───────────────────────────┐
│ Poll bank for tx status    │
│ - Confirmed: not debited  │ → No reversal
│ - Confirmed: debited      │ → Reverse
│ - Still unknown           │ → Retry poll (max 3)
│ - All polls fail          │ → Flag for manual review
└───────────────────────────┘
```

> **Key insight**: The reversal system must distinguish "I know it failed" from "I don't know what happened." Only the first case triggers an automatic reversal. The second case triggers investigation. This is the same principle as idempotency: don't act on ambiguity.

**Cross-reference**: See [cqrs-05: Risk Creates Actions, Never Rewrites History](cqrs-fintech.md#cqrs-05-risk-creates-actions-never-rewrites-history) — reversals are new ledger entries, not deletions.

---

## cqrs-33: Circuit Breaker Per-Bank with Pending State Recovery

> **Source**: [Article §"Part 12: Failure Handling"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-12-failure-handling)

| | |
|:---|:---|
| **Problem** | With 100+ banks, one slow or unavailable bank can consume connection pool resources, thread pools, and timeout budgets, degrading the entire authorization service — not just transactions for that bank. |
| **Root cause** | Shared infrastructure (connection pools, thread pools) without per-bank isolation means one bad tenant impacts all tenants. |

### Per-Bank Circuit Breaker Design

```
                    ┌──────────────────────┐
                    │  Authorization Svc    │
                    └──────┬───────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Bank A   │ │ Bank B   │ │ Bank C   │
        │ Circuit  │ │ Circuit  │ │ Circuit  │
        │ CLOSED   │ │ OPEN     │ │ CLOSED   │
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              ▼            ▼            ▼
          Bank A       Bank B       Bank C
          (healthy)    (down)       (healthy)
```

| State | Condition | Behavior |
|:---|:---|:---|
| **CLOSED** | Normal operation | Route requests to bank |
| **OPEN** | 5 consecutive failures | Fail fast — don't call bank |
| **HALF-OPEN** | After 30s timeout | Allow 1 probe request |

### Pending State Recovery

When a network failure occurs mid-transaction:
1. Transaction marked PENDING (not DECLINED, not APPROVED)
2. Background poller queries bank for transaction status
3. On confirmation: update transaction to final state (APPROVED/REVERSED)
4. PENDING transactions age out after configurable timeout → manual review

> **Key insight**: Per-bank circuit breakers prevent a single bank outage from becoming a system-wide outage. The PENDING state acknowledges that in distributed systems, "I don't know yet" is a legitimate transaction state — not a bug.

**Tradeoff**: PENDING transactions consume memory and require background polling infrastructure. But the alternative — treating timeouts as failures and auto-reversing — risks double-crediting customers.

---

## cqrs-34: Database Sharding by Bank ID

> **Source**: [Article §"Part 9: Database Design" and "Part 13: Scaling Strategies"](../../articles/cqrs-fintech/designing-debit-card-processing-system.md#part-9-database-design)

| | |
|:---|:---|
| **Problem** | A single PostgreSQL instance cannot handle 10,000+ write TPS from transaction inserts and limit updates across 500M transactions/month. |
| **Root cause** | Monolithic database with all banks' transactions in one instance hits write throughput ceiling. |

### Sharding Strategy

```
                    ┌──────────────┐
                    │  Router      │  ← Routes by bank_id
                    └──────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Shard 1  │    │ Shard 2  │    │ Shard N  │
    │ Banks    │    │ Banks    │    │ Banks    │
    │ 1-33     │    │ 34-66    │    │ 67-100   │
    └──────────┘    └──────────┘    └──────────┘
```

| Strategy | Key | Benefit | Limitation |
|:---|:---|:---|:---|
| **Shard by bank_id** | Each bank's data stays together | Bank-level isolation; easy bank-specific reporting | Uneven shard sizes |
| **Partition by date** | Monthly partitions within shard | Fast archival; efficient range queries | Cross-month queries need UNION |

### Why bank_id Sharding Works for Debit Card Processing

1. **Bank isolation**: A bank's transactions never span shards — settlement per bank is a single-shard query
2. **Operational simplicity**: Adding a new bank = adding it to a shard (or creating a new one)
3. **No cross-shard transactions**: Debit transactions involve exactly one bank
4. **Read replicas per shard**: Each shard can have dedicated replicas for that bank's reporting load

> **Key insight**: Sharding by `bank_id` rather than `card_id` or `transaction_id` aligns the physical data layout with the business boundary. Settlement, reconciliation, and bank-specific reporting are all single-shard operations.

**Tradeoff**: Bank sizes vary dramatically — a shard with 3 large banks may have 10× the load of a shard with 30 small banks. This requires shard rebalancing over time, which is operationally expensive.

---

## Cross-Reference Map

| Takeaway | Related cqrs-* | Related Dictionary | Azure Services |
|:---|:---|:---|:---|
| cqrs-27: Authorization Pipeline | cqrs-01, cqrs-04, cqrs-08 | [Debit Card Authorization](../../reference-dictionary/fintech.md#debit-card-authorization) | — |
| cqrs-28: Bank Adapter | cqrs-13 | [Bank Adapter](../../reference-dictionary/fintech.md#bank-adapter), [ISO 8583](../../reference-dictionary/fintech.md#iso-8583) | — |
| cqrs-29: Balance Accuracy | cqrs-02, cqrs-04 | [Real-Time Balance Checking](../../reference-dictionary/fintech.md#real-time-balance-checking) | — |
| cqrs-30: PIN Security | — | [PIN Verification](../../reference-dictionary/hsm-cryptography.md#pin-verification) | — |
| cqrs-31: Multi-Dimensional Limits | cqrs-04 | [Limit Reservation](../../reference-dictionary/fintech.md#limit-reservation) | — |
| cqrs-32: Safe Reversal | cqrs-03, cqrs-05 | [Transaction Reversal](../../reference-dictionary/fintech.md#transaction-reversal) | — |
| cqrs-33: Per-Bank Circuit Breaker | — | [Circuit Breaker](../../reference-dictionary/resilience.md) | — |
| cqrs-34: Sharding by Bank ID | — | — | — |
