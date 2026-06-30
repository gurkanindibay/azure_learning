---
type: Article
title: "Designing a Debit Card Processing System: PIN Authentication, Bank Integration & Real-Time Balance Checks"
description: "System design deep-dive into debit card processing covering PIN verification, real-time balance checks, bank integration with multiple protocols (ISO 8583, REST, SOAP), transaction limits enforcement, reversal handling, and scaling to 10,000+ TPS with sub-second latency."
source: "https://codefarm0.medium.com/designing-a-debit-card-processing-system-pin-authentication-bank-integration-real-time-balance-5c07a4f76ffd"
author: "Arvind Kumar (CodeFarm)"
published: 2026-02-26
created: 2026-06-30
timestamp: 2026-06-30T00:00:00Z
tags:
  - fintech
  - system-design
  - payment-systems
  - debit-card
---

# Designing a Debit Card Processing System: PIN Authentication, Bank Integration & Real-Time Balance Checks

How do debit card payments work? When a customer swipes their debit card at a POS terminal or uses it at an ATM, how does the system verify the PIN, check the account balance, and process the transaction in real-time? How do you design a system that integrates with multiple banks' core banking systems while handling millions of transactions with sub-second latency?

**Concepts**: Debit Card Authorization, PIN Verification, Real-Time Balance Checking, Bank Core System Integration, Transaction Limits, ATM/POS Processing, Card Activation, Transaction Reversal, Bank Settlement

> [Full story for non-members](https://codefarm0.medium.com/5c07a4f76ffd?sk=f79ebaeb3b04540f97cc494f3ea81a5b)

## A Real-World Problem

**Aadvik (Interviewer):** "Sara, imagine you're building a debit card processing system. Customers can use their debit cards at POS terminals, ATMs, and online. The system needs to verify PINs, check account balances in real-time, enforce transaction limits, and integrate with multiple banks' core banking systems. How do you design this system?"

**Sara (Candidate):** "This is a complex real-time payment processing challenge with direct bank integration. Debit card processing involves several key components:

1. **PIN Verification**: Verify cardholder's PIN securely
2. **Real-Time Balance Checks**: Check account balance before transaction
3. **Bank Integration**: Integrate with multiple banks' core banking systems
4. **Transaction Limits**: Enforce daily and per-transaction limits
5. **ATM/POS Support**: Handle both ATM and POS transactions
6. **Card Management**: Card activation, PIN management, card blocking
7. **Transaction Reversal**: Handle failed transactions and reversals
8. **Settlement**: Daily settlement with banks"

**Aadvik:** "Exactly. And here's what makes it interesting: Debit card processing handles billions of transactions globally. A typical debit card network processes 50,000+ transactions per second during peak times. How do you handle this scale while maintaining real-time balance checks and sub-second latency?"

**Sara:** "The scale is significant, and real-time processing is critical. We need a highly available, distributed architecture that can handle high transaction volumes while maintaining low latency for balance checks and PIN verification."

## Part 1: Requirements & Core Challenges

### Functional Requirements

1. **Transaction Types:** ATM transactions (cash withdrawal, balance inquiry, PIN change), POS transactions (merchant payments, cashback), Online debit card payments (with PIN/OTP)

2. **Card Operations:** Card activation and deactivation, PIN verification and validation, PIN change and reset, Card blocking and unblocking, Card replacement

3. **Transaction Processing:** Real-time authorization (PIN verification + balance check), Transaction reversal (for failed transactions), Balance inquiry, Transaction history

4. **Transaction Limits:** Daily transaction limit (e.g., ₹50,000/day), Per-transaction limit (e.g., ₹25,000/transaction), Daily withdrawal limit (e.g., ₹20,000/day), Monthly transaction limit

5. **Bank Integration:** Integration with multiple banks' core banking systems, Support for different bank protocols (ISO 8583, REST, SOAP), Real-time balance checking, Transaction posting to bank accounts

6. **Security & Compliance:** PCI-DSS compliance for card data, PIN encryption (never store plaintext PIN), Secure PIN transmission, Audit logging

### Non-Functional Requirements

1. **Scale:** 500 million transactions/month, Average: 190 TPS, Peak: 10,000+ TPS, 50 million cardholders, 100+ bank integrations

2. **Latency:** Authorization response: < 1 second (p95), Balance inquiry: < 500ms (p95), PIN verification: < 200ms (p95)

3. **Availability:** 99.99% uptime (~4 minutes downtime/month), Zero data loss, Automatic failover

4. **Security:** PCI-DSS Level 1 compliance, PIN encryption (AES-256), End-to-end encryption, Secure key management

### Core Challenges

1. **Real-Time Balance Checks**: Check account balance in real-time before transaction
2. **Bank Integration Complexity**: Different banks use different protocols and systems
3. **PIN Security**: Never store plaintext PIN, secure PIN transmission
4. **High Volume**: Handle 10,000+ TPS with sub-second latency
5. **Transaction Limits**: Enforce multiple limit types (daily, per-transaction, withdrawal)
6. **Bank Downtime**: Handle bank API failures gracefully
7. **Transaction Reversal**: Handle failed transactions and reversals
8. **Settlement**: Daily settlement with multiple banks

## Part 2: Scale & Capacity Planning

### Transaction Volume

**Monthly Volume:** 500 million transactions/month. Average: 190 TPS. Peak: 10,000+ TPS (during peak hours: 9 AM–11 AM, 6 PM–9 PM).

**Transaction Distribution:** ATM transactions: 60% (300M/month), POS transactions: 35% (175M/month), Online transactions: 5% (25M/month).

**Peak Load Scenarios:** Black Friday: 15,000+ TPS, Salary day: 12,000+ TPS, Festival season: 10,000+ TPS.

### Data Storage

**Transaction Data:** 500M transactions/month × 1KB per transaction = 500GB/month. Annual: 6TB/year. Retention: 7 years = 42TB.

**Card Data:** 50M cardholders × 2KB per card = 100GB.

**Total Storage:** ~52TB (42TB transactions + 100GB card data + ~10TB indexes/metadata).

### Network Bandwidth

**Peak:** 10,000 TPS × 3KB = 30MB/s = 240Mbps (~300Mbps with overhead).

**Average:** 190 TPS × 3KB = 570KB/s = 4.5Mbps.

## Part 3: High-Level Architecture

### Core Functional Components

1. **Authorization Service**: Main transaction processing, coordinates all operations
2. **Card Verification Service**: PIN verification + transaction limit enforcement (merged)
3. **Card Management Service**: Card lifecycle management (activation, PIN change, blocking)
4. **Transaction Reversal Service**: Handles failed transactions and reversals
5. **Bank Adapter**: Abstracts bank protocol differences

### Core Services

**Authorization Service:** Main transaction processing service. Coordinates card verification, balance check, bank debit. Handles transaction authorization end-to-end. Checks balance via bank adapter. Manages transaction state.

**Card Verification Service:** Validates card status (ACTIVE, BLOCKED, EXPIRED) — rejects blocked/expired cards before any further processing. Verifies cardholder PIN, encrypts/decrypts PIN, caches PIN validation results. Enforces daily, per-transaction, withdrawal limits; tracks limit usage; updates limits in real-time.

**Card Management Service:** Card activation, deactivation. PIN change, reset. Card blocking, unblocking.

**Transaction Reversal Service:** Handles failed transactions, reverses transactions, handles dispute resolution.

**Bank Adapter Framework:** Abstracts bank protocol differences. Handles ISO 8583, REST, SOAP protocols. Circuit breaker for bank failures. Connection pooling.

## Part 4: Debit Card Transaction Flow

### ATM Transaction Flow

ATM transactions involve immediate cash withdrawal where the customer's bank debits the account immediately. No merchant is involved. Settlement is direct bank-to-bank.

### POS Transaction Flow

POS transactions are merchant payments where the customer's bank debits the account immediately but the merchant's bank credits the account later (T+1 settlement).

### Key Differences: ATM vs POS

| Aspect | ATM | POS |
|:---|:---|:---|
| **Action** | Immediate cash withdrawal | Merchant payment |
| **Debit timing** | Immediate | Immediate |
| **Merchant** | None | Involved |
| **Settlement** | Direct bank-to-bank | T+1 settlement |

## Part 5: PIN Verification & Security

### PIN Security Architecture

**PIN Storage:** Never store plaintext PIN. Store PIN hash (one-way hash, cannot be reversed). Use secure hashing algorithm (bcrypt, PBKDF2).

**PIN Transmission:** Encrypt PIN before transmission (AES-256). Use TLS 1.3 for all communication. PIN encrypted end-to-end.

### PIN Encryption

**Encryption at Terminal:** PIN encrypted using terminal's encryption key. Encrypted PIN sent to gateway. Terminal never sends plaintext PIN.

**Encryption at Gateway:** Gateway receives encrypted PIN. Re-encrypts PIN for bank transmission. Uses bank-specific encryption key.

**PIN Hashing (Storage):** Bank stores PIN hash (not plaintext). PIN verification: Compare hash of entered PIN with stored hash. One-way hash (cannot reverse).

### PIN Verification Caching

**Why Cache?** Reduces bank API calls, improves latency, reduces bank load.

**Cache Strategy:** Cache PIN validation results. TTL: 5 minutes (short, for security). Cache key: `card_number + transaction_timestamp`. Invalidate on PIN change.

**Cache Implementation:** Redis for distributed caching. Encrypted cache keys. Automatic expiration.

## Part 6: Real-Time Balance Checking

### Balance Check Strategy

Real-time balance checking is critical for debit cards. Balance is checked directly from the bank during transaction authorization using a write-through cache pattern to ensure balance accuracy.

**Critical Rule:** Never use cached balance for transaction authorization. Always get balance from bank during transaction. Cache is updated via write-through after transaction completes.

### Balance Caching: Write-Through Pattern

**Why Cache Balance?** Reduces bank API calls for balance inquiries (not for transactions). Improves latency for balance inquiry API calls. Reduces bank load.

**Write-Through Cache Pattern:**

- No TTL-based caching for transactions — Always get balance from bank during transaction
- Cache updated immediately after transaction — Write-through pattern ensures cache always reflects bank balance
- Cache used only for balance inquiry API — Not used for transaction authorization

**Cache Update Flow:**

1. Transaction authorization: Always check balance from bank
2. Bank debits account and returns new balance
3. Immediately update cache with new balance (write-through)
4. Next balance inquiry uses cached balance (if recent)
5. Next transaction: Always check from bank again

**Cache Key:** `balance:{account_number}` — Per-account caching, distributed cache (Redis).

### Balance Consistency Guarantee

The system prevents stale balance issues by never authorizing against cached data. The cache serves only the non-critical balance inquiry API. If cache miss occurs during inquiry, the system fetches from the bank.

## Part 7: Bank Integration Architecture

### Bank Adapter Framework

Different banks use different protocols. The adapter pattern abstracts protocol differences behind a common interface.

### Bank Adapter Interface

Common operations across all bank adapters:

- `verifyPIN(cardNumber, encryptedPIN) → boolean`
- `checkBalance(accountNumber) → Balance`
- `debitAccount(accountNumber, amount) → TransactionResult`
- `creditAccount(accountNumber, amount) → TransactionResult`
- `reverseTransaction(transactionId) → ReversalResult`

### Protocol Handlers

**ISO 8583 Handler:** Financial messaging standard used by many banks. Binary protocol. Message types: 0100 (authorization), 0200 (financial), 0420 (reversal).

**REST API Handler:** Modern banks use REST APIs. JSON/XML format. HTTP/HTTPS. Easier integration.

**SOAP Handler:** Legacy banks use SOAP. XML format. WSDL-based. More complex integration.

### Circuit Breaker Pattern

Banks can be unavailable. The circuit breaker prevents cascading failures and fails fast when a bank is down.

**States:** Closed (normal operation) → Open (bank unavailable, fail fast) after 5 consecutive failures → Half-Open (testing recovery) after 30 seconds.

### Connection Pooling

Bank connections are expensive to establish. Connection pooling reuses connections to reduce latency.

**Pool Configuration:** 10–50 connections per bank. Keep-alive: 60 seconds. Timeout: 5 seconds.

## Part 8: Transaction Limits

### Limit Types

1. **Daily Transaction Limit:** Maximum amount per day (e.g., ₹50,000/day). Resets at midnight. Tracks total transactions per day.

2. **Per-Transaction Limit:** Maximum amount per transaction (e.g., ₹25,000/transaction). Applied to each transaction. Prevents large fraudulent transactions.

3. **Daily Withdrawal Limit:** Maximum ATM withdrawal per day (e.g., ₹20,000/day). Separate from transaction limit. Tracks ATM withdrawals.

4. **Monthly Transaction Limit:** Maximum amount per month (e.g., ₹500,000/month). Resets at month start.

### Limit Tracking

**Daily Limit Tracking:** Track total transactions per day. Update in real-time. Cache for fast access. Reset at midnight.

**Limit Storage:** Database for persistent storage. Redis for real-time tracking. Update both on transaction.

**Limit Update Flow:**

1. Transaction approved
2. Update daily usage: `current_usage + amount`
3. Update cache (Redis)
4. Update database (async)

## Part 9: Database Design

### Database Schema

**Cards Table:**

```sql
CREATE TABLE cards (
    card_id VARCHAR(50) PRIMARY KEY,
    card_number_hash VARCHAR(255) NOT NULL,  -- Hashed card number
    account_number VARCHAR(50) NOT NULL,
    bank_id VARCHAR(50) NOT NULL,
    card_type VARCHAR(20) NOT NULL,  -- DEBIT, ATM, POS
    pin_hash VARCHAR(255) NOT NULL,  -- Hashed PIN
    status VARCHAR(20) NOT NULL,  -- ACTIVE, BLOCKED, EXPIRED
    daily_limit DECIMAL(15, 2) NOT NULL,
    per_transaction_limit DECIMAL(15, 2) NOT NULL,
    daily_withdrawal_limit DECIMAL(15, 2) NOT NULL,
    issued_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_account_number (account_number),
    INDEX idx_bank_id (bank_id),
    INDEX idx_status (status)
);
```

**Transactions Table:**

```sql
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    card_id VARCHAR(50) NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    bank_id VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,  -- ATM, POS, ONLINE
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    status VARCHAR(20) NOT NULL,  -- PENDING, APPROVED, DECLINED, REVERSED
    decline_reason VARCHAR(255),
    terminal_id VARCHAR(50),
    merchant_id VARCHAR(50),
    authorization_code VARCHAR(50),
    balance_before DECIMAL(15, 2),
    balance_after DECIMAL(15, 2),
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES cards(card_id),
    INDEX idx_card_id (card_id),
    INDEX idx_account_number (account_number),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) PARTITION BY RANGE (created_at);
```

**Daily Limits Table:**

```sql
CREATE TABLE daily_limits (
    limit_id VARCHAR(50) PRIMARY KEY,
    card_id VARCHAR(50) NOT NULL,
    limit_date DATE NOT NULL,
    daily_usage DECIMAL(15, 2) NOT NULL DEFAULT 0,
    withdrawal_usage DECIMAL(15, 2) NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(card_id),
    UNIQUE KEY uk_card_date (card_id, limit_date),
    INDEX idx_limit_date (limit_date)
);
```

**Transaction Reversals Table:**

```sql
CREATE TABLE transaction_reversals (
    reversal_id VARCHAR(50) PRIMARY KEY,
    original_transaction_id VARCHAR(50) NOT NULL,
    reversal_type VARCHAR(20) NOT NULL,  -- FULL, PARTIAL
    amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- PENDING, COMPLETED, FAILED
    reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (original_transaction_id) REFERENCES transactions(transaction_id),
    INDEX idx_original_transaction (original_transaction_id),
    INDEX idx_status (status)
);
```

**Banks Table:**

```sql
CREATE TABLE banks (
    bank_id VARCHAR(50) PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    protocol_type VARCHAR(20) NOT NULL,  -- ISO8583, REST, SOAP
    endpoint_url VARCHAR(255),
    api_key VARCHAR(255),
    status VARCHAR(20) NOT NULL,  -- ACTIVE, INACTIVE
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Database Sharding & Partitioning

**Sharding Strategy:** Shard by `bank_id` (each bank's transactions in separate shard) or by `card_id` (hash-based sharding). Enables horizontal scaling.

**Partitioning:** Partition transactions table by date (monthly partitions). Archive old partitions. Improves query performance.

## Part 10: API Design

### Authorization APIs

**Authorize Transaction:** `POST /api/v1/transactions/authorize`

Request:

```json
{
  "card_number": "4111111111111111",
  "encrypted_pin": "encrypted_pin_data",
  "amount": 1000.00,
  "currency": "INR",
  "transaction_type": "POS",
  "merchant_id": "merchant_123",
  "terminal_id": "terminal_456"
}
```

Response (200 OK):

```json
{
  "transaction_id": "txn_123456",
  "status": "approved",
  "authorization_code": "AUTH789",
  "amount": 1000.00,
  "balance_after": 9000.00,
  "authorized_at": "2024-01-15T10:30:00Z"
}
```

**Balance Inquiry:** `POST /api/v1/balance/inquiry`

### Card Management APIs

**Activate Card:** `POST /api/v1/cards/activate`

**Change PIN:** `PUT /api/v1/cards/pin`

### Transaction APIs

**Get Transaction:** `GET /api/v1/transactions/{transaction_id}`

**Reverse Transaction:** `POST /api/v1/transactions/{transaction_id}/reverse`

## Part 11: Transaction Reversal

### Reversal Philosophy

Transaction reversal is critical. But not every failure means the debit actually went through. On a timeout or ambiguous response, the true outcome is unknown. Triggering an immediate reversal could reverse a transaction that actually succeeded, effectively crediting the customer twice. The system must first confirm the failure before reversing.

### Reversal Scenarios

1. **Transaction Failure After Debit:** Bank debited account but transaction failed (network error, timeout) — must reverse debit.

2. **Merchant Cancellation:** Transaction approved but merchant cancels order — must reverse transaction.

3. **Dispute Resolution:** Customer disputes transaction; investigation finds in favor of customer — must reverse transaction.

### Reversal Timeout

If reversal doesn't complete within 30 seconds, retry (maximum 3 retries). If all retries fail, flag for manual intervention.

## Part 12: Failure Handling

### Failure Scenarios & Mitigations

| Scenario | Mitigation | Recovery |
|:---|:---|:---|
| **Bank API Unavailable** | Circuit breaker opens after 5 failures; queue transactions for retry | Process queued transactions when bank recovers |
| **PIN Verification Timeout** | Retry (max 2); decline if still fails | User retries transaction |
| **Balance Check Timeout** | Retry (max 2); decline if still fails (safety first) | User retries transaction |
| **Transaction Reversal Failure** | Retry (max 3); flag for manual intervention if all fail | Manual reversal by ops team |
| **Network Failure** | Transaction in pending state; poll bank for status | Transaction status updated automatically |

### Idempotency

**Why Critical:** Network retries can cause duplicate requests. Users might retry transactions. The system must handle duplicates gracefully.

**Implementation:** Each transaction request has a unique `transaction_id`. Check if `transaction_id` already exists. If exists, return existing transaction status (don't process again). If new, process the transaction.

## Part 13: Scaling Strategies

### Horizontal Scaling

**Authorization Service:** Stateless services scale horizontally. Load balancer distributes requests. Auto-scale based on TPS and latency.

**Card Verification Service:** Stateless PIN verification and limit checking. Scale horizontally with cached PIN validation and limit usage.

### Database Scaling

**Read Replicas:** For read-heavy workloads. Separate read and write paths. Reduces primary database load.

**Sharding:** Shard transactions table by `bank_id` or `card_id`. Each shard handles a subset of transactions.

**Partitioning:** Monthly partitions. Archive old partitions.

### Multi-Layer Caching

**L1 — Application Cache (In-Memory):** PIN validation results (5 min TTL). Limit usage data. LRU eviction, 100MB per instance.

**L2 — Redis Cache (Distributed):** PIN validation results (5 min TTL). Balance data (write-through, no TTL for transactions). Daily limit usage (24 hour TTL). Transaction status (1 hour TTL).

**L3 — Database (Persistent):** Source of truth. Used for writes and cache misses.

### Bank Integration Scaling

**Connection Pooling:** 10–50 connections per bank. Connection reuse.

**Circuit Breaker:** Prevent cascading failures. Fail fast when bank is down. Automatic recovery.

**Load Balancing:** Multiple bank adapter instances. Health checks.

## Part 14: Monitoring & Observability

### Key Metrics

**Transaction Metrics:** Success rate, latency (p50, p95, p99), TPS, failed transactions count, PIN verification success rate.

**Business Metrics:** Total transaction volume/value (daily, monthly), active cardholders, average transaction amount, transaction type distribution.

**System Metrics:** API response time, database query latency, Redis cache hit rate, bank API latency, error rates.

### Alerting Rules

**Critical Alerts:** Transaction success rate < 99%. Transaction latency p95 > 1 second. Bank API failure rate > 1%. Database connection pool > 90%. Error rate > 0.1%.

**Warning Alerts:** Transaction latency p95 > 500ms. Cache hit rate < 80%. Bank API latency > 500ms. Queue depth > 1000.

### SLOs & SLIs

**Service Level Indicators:** Transaction success rate: 99.9%. Transaction latency: p95 < 1 second. API availability: 99.99%.

**Service Level Objectives:** 99.9% of transactions complete successfully. 95% of transactions complete within 1 second. 99.99% API uptime. Zero data loss.

**Error Budget:** 0.1% per month. If exceeded: stop feature work, focus on reliability.

## Part 15: Cost Analysis

> **Disclaimer**: The cost estimates below are rough approximations based on publicly available pricing. They are illustrative, not actual billing amounts.

**Compute (EC2/ECS):** Authorization services: 20 instances (c5.2xlarge) ~$3,000/month. Bank integration services: 10 instances (c5.xlarge) ~$1,500/month. **Total: ~$4,500/month.**

**Database (RDS PostgreSQL):** Primary: db.r5.4xlarge (multi-AZ) ~$2,000/month. Read replicas: 3 × db.r5.2xlarge ~$3,000/month. **Total: ~$5,000/month.**

**Caching (ElastiCache Redis):** 3 × cache.r5.xlarge ~$1,500/month.

**Messaging (Kafka/MSK):** 3 × kafka.m5.large ~$500/month.

**Network & Data Transfer:** ~$1,000/month.

**Storage:** 42TB × $0.023/GB ~$1,000/month.

**Total Estimated Monthly Cost: ~$13,500/month.**

## Part 16: Trade-offs & Future Improvements

### Key Trade-offs

1. **Balance Cache TTL — Accuracy vs Performance:** 30-second TTL with immediate invalidation after transaction. Slight risk of stale balance with very short window. Benefit: reduced bank API calls, improved latency.

2. **PIN Verification Cache — Security vs Performance:** 5-minute TTL. Slight security risk with very short window. Mitigated by short TTL and invalidation on PIN change.

3. **Bank Protocol Abstraction — Complexity vs Flexibility:** Adapter pattern for multiple protocols. More complex codebase but supports multiple banks with different protocols.

4. **Transaction Limits — Real-Time vs Performance:** Real-time limit checking with additional database queries. Mitigated by caching limit usage and async updates.

### Future Improvements

1. **Advanced Fraud Detection**: ML-based real-time fraud detection
2. **Multi-Region Deployment**: Deploy in multiple regions for resilience
3. **Predictive Scaling**: ML-based prediction of transaction volume
4. **Advanced Analytics**: Real-time transaction analytics dashboard
5. **Cost Optimization**: More aggressive auto-scaling and spot instances
6. **Direct Bank Integration**: Optimize bank integration for lower latency

## Summary

**Key Takeaways:**

1. **PIN Security** — Never store plaintext PIN, encrypt at every step
2. **Real-Time Balance Checks** — Check balance before every transaction
3. **Bank Integration** — Adapter pattern for multiple bank protocols
4. **Transaction Limits** — Enforce daily, per-transaction, withdrawal limits
5. **Transaction Reversal** — Handle failed transactions and reversals
6. **High Availability** — Circuit breakers, retries, failover

**System Handles:** 500 million transactions/month. 10,000+ TPS (peak). 50 million cardholders. 100+ bank integrations. Sub-1-second authorization. 99.99% availability.

**Architecture Highlights:** PIN encryption for security. Real-time balance checks for accuracy. Bank adapter framework for flexibility. Transaction limits for fraud prevention. Comprehensive monitoring with SLOs.
