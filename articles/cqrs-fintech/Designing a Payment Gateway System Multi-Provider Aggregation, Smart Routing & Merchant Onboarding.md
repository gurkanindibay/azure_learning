---
type: Article
title: "Designing a Payment Gateway System: Multi-Provider Aggregation, Smart Routing & Merchant Onboarding"
source: "https://codefarm0.medium.com/designing-a-payment-gateway-system-multi-provider-aggregation-smart-routing-merchant-onboarding-80f634cb0534"
author:
  - "[[Arvind Kumar]]"
published: 2026-03-17
created: 2026-06-25
description: "System design deep-dive into payment gateway architecture covering multi-provider aggregation, smart routing algorithms, merchant onboarding, fee calculation, reconciliation, and settlement at 20K TPS scale."
tags:
  - "clippings"
  - "fintech"
  - "system-design"
---

# Designing a Payment Gateway System: Multi-Provider Aggregation, Smart Routing & Merchant Onboarding

How does a payment gateway work? When a merchant wants to accept payments from customers using multiple payment methods (Cards, UPI, Wallets, Net Banking), how does the gateway route transactions to the best provider, handle failures, and ensure high availability? How do you design a system that aggregates multiple payment providers while optimizing for cost, latency, and success rate?

**Concepts**: Payment Gateway, Multi-Provider Integration, Smart Routing Algorithm, Payment Method Aggregation, Merchant Onboarding, Fee Calculation, Reconciliation, Circuit Breaker, Load Balancing, Provider Failover

> [Full story for non-members](https://codefarm0.medium.com/80f634cb0534?sk=ceff36c96d75c353e95544a6d94738f5) | [E-Books on Java/Microservices/Springboot](https://topmate.io/codefarm) | [Whatsapp Group](https://www.whatsapp.com/channel/0029VbBoxXI5q08aIWZsUE2X) | [Youtube](https://www.youtube.com/@codefarm0) | [LinkedIn](https://www.linkedin.com/in/codefarm0/)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*DUesv0ufVgM1bS26kozwMw.png)

## A Real-World Problem

**Aadvik (Interviewer):** “Sara, imagine you’re building a payment gateway that aggregates multiple payment providers. Merchants can accept payments via Cards, UPI, Wallets, and Net Banking. The system needs to route transactions to the best provider, handle provider failures, onboard merchants, calculate fees, and reconcile transactions. How do you design this system?”

**Sara (Candidate):** *\[Thoughtful pause\]* “This is a complex aggregation and routing challenge. A payment gateway involves several key components:

1. **Payment Method Aggregation**: Support Cards, UPI, Wallets, Net Banking
2. **Smart Routing**: Route transactions to best provider (cost, latency, success rate)
3. **Multi-Provider Integration**: Integrate with multiple providers per payment method
4. **Provider Failover**: Handle provider failures gracefully
5. **Merchant Onboarding**: KYC, verification, account setup
6. **Fee Calculation**: Calculate fees and commissions dynamically
7. **Reconciliation**: Match transactions with provider responses
8. **Settlement**: Settle funds to merchants”

**Aadvik:** “Exactly. And here’s what makes it interesting: Payment gateways process millions of transactions daily. A typical gateway handles 100,000+ transactions per second during peak times. How do you handle this scale while optimizing routing decisions in real-time?”

**Sara:** “The scale is significant, and routing optimization is critical. We need a highly available, distributed architecture that can make intelligent routing decisions in milliseconds while handling provider failures. Let me start with some clarifying questions to understand the requirements better.”

**Aadvik:** “Great! Ask away.”

**Sara:** “I have several questions:

**Scale and Usage:**

1. What’s the expected transaction volume? Peak TPS?
2. How many merchants are we supporting?
3. How many payment providers per payment method?
4. What’s the average transaction amount?

**Functional Requirements:**

5\. What payment methods do we support? (Cards, UPI, Wallets, Net Banking)  
6\. Do merchants choose providers or do we auto-route?  
7\. What’s the merchant onboarding process?  
8\. How do we calculate fees? (percentage, fixed, tiered)

**Routing & Optimization:**  
9\. What factors determine best provider? (cost, latency, success rate)  
10\. How do we handle provider failures?  
11\. Do we support merchant-specific routing rules?  
12\. How do we balance load across providers?

**Non-Functional Requirements:**  
13\. What’s the acceptable latency for routing decision?  
14\. What’s the availability target?  
15\. How do we ensure transaction reconciliation?”

**Aadvik:** “Excellent questions! Let me give you the requirements:”

## Part 1: Requirements & Core Challenges

### Functional Requirements

1. **Payment Methods:**
- Credit/Debit Cards (Visa, Mastercard, Amex)
- UPI (Unified Payments Interface)
- Digital Wallets (Paytm, PhonePe, etc.)
- Net Banking (Bank transfers)

**2\. Payment Operations:**

- Payment initiation and processing
- Payment status check
- Refund processing (full and partial)
- Payment method selection
- Transaction history

**3\. Merchant Management:**

- Merchant onboarding and KYC
- Merchant account management
- Merchant dashboard and reporting
- API key management
- Webhook configuration

**4\. Payment Routing:**

- Smart routing to best provider
- Multi-provider failover
- Merchant-specific routing rules
- Load balancing across providers
- Cost optimization

**5\. Fee & Settlement:**

- Dynamic fee calculation
- Commission tracking
- Settlement to merchants (T+1, T+2)
- Reconciliation and reporting

**6\. Security & Compliance:**

- PCI-DSS compliance (for card data)
- API authentication (API keys, OAuth)
- Webhook signature verification
- Audit logging

### Non-Functional Requirements

1. **Scale:**
- 1 billion transactions per month
- Average: 380 TPS
- Peak: 20,000+ TPS (during sales events)
- 100,000 merchants
- 50+ payment providers

**2\. Latency:**

- Routing decision: < 50ms (p95)
- Payment initiation: < 500ms (p95)
- Status check: < 200ms (p95)

**3\. Availability:**

- 99.99% uptime (allows ~4 minutes downtime/month)
- Zero data loss
- Automatic failover

**4\. Success Rate:**

- Payment success rate: > 99%
- Provider failover: < 100ms
- Reconciliation accuracy: 100%

**5\. Compliance:**

- PCI-DSS Level 1 (for card processing)
- Regional compliance (GDPR, RBI, etc.)
- Audit logging
- Data retention policies

### Core Challenges

1. **Smart Routing**: Route to best provider considering cost, latency, success rate
2. **Multi-Provider Integration**: Integrate with 50+ providers with different APIs
3. **Provider Failover**: Handle provider failures without transaction loss
4. **Fee Calculation**: Calculate fees dynamically based on multiple factors
5. **Reconciliation**: Match transactions with provider responses accurately
6. **High Volume**: Handle 20,000+ TPS with sub-50ms routing decisions
7. **Merchant Onboarding**: Streamline KYC and verification process
8. **Settlement**: Settle funds to merchants accurately and on time

**Aadvik:** “Also, let’s start by understanding the scale. Payment gateways handle massive volumes. How do you handle this?”

**Sara:** “The scale is significant. Let me break down the numbers:”

## Part 2: Scale & Capacity Planning

### A. Transaction Volume

1. **Monthly Volume:**
- 1 billion transactions per month
- Average: 380 TPS
- Peak: 20,000+ TPS (during sales events: Black Friday, Diwali, etc.)

**2\. Transaction Distribution:**

- Cards: 40% (400M/month)
- UPI: 35% (350M/month)
- Wallets: 20% (200M/month)
- Net Banking: 5% (50M/month)

**3\. Peak Load Scenarios:**

- Black Friday: 25,000+ TPS
- Festival sales: 20,000+ TPS
- Salary day: 15,000+ TPS

### B. Data Storage

1. **Transaction Data:**
- 1B transactions/month × 2KB per transaction = 2TB/month
- Annual: 24TB/year
- Retention: 7 years = 168TB

**2\. Merchant Data:**

- 100K merchants × 10KB per merchant = 1GB
- Transaction history per merchant: ~10GB average

**3\. Provider Data:**

- 50 providers × 5KB per provider = 250KB
- Provider transaction logs: ~500GB/month

**4\. Total Storage:**

- Transaction data: 168TB (7 years)
- Merchant data: 1TB
- Provider data: 42TB (7 years)
- **Total: ~211TB**

### C. Network Bandwidth

1. **Peak TPS: 20,000**
- Request size: 3KB
- Response size: 2KB
- Total: 5KB per transaction

**2\. Peak Bandwidth:**

- 20,000 TPS × 5KB = 100MB/s = 800Mbps
- With overhead: ~1Gbps

**3\. Average Bandwidth:**

- 380 TPS × 5KB = 1.9MB/s = 15Mbps

## Part 3: High-Level Architecture

**Sara:** “Let me design the high-level architecture for the payment gateway. I’ll start with a functional view, then show the detailed architecture.”

### A. High-Level Functional Architecture

**B. Core Functional Components:**

1. **Payment Service**: Main transaction processing, coordinates all operations
2. **Routing Service**: Smart provider selection based on multiple factors
3. **Merchant Service**: Merchant onboarding, management, API key handling
4. **Reconciliation Service**: Match transactions with provider responses
5. **Settlement Service**: Settle funds to merchants

### C. Detailed System Architecture (Scaled)

### D. Core Services

**1\. Payment Service**

- Main transaction processing service
- Coordinates routing, provider calls, fee calculation
- Handles payment initiation, status checks, refunds
- Manages transaction state

**2\. Routing Service**

- **Smart Routing Algorithm**: Selects best provider based on cost, latency, success rate
- **Provider Health Monitoring**: Tracks provider health, latency, success rate
- **Failover Logic**: Automatically fails over to backup provider
- **Load Balancing**: Distributes load across providers

**3\. Merchant Service**

- Merchant onboarding and KYC
- Merchant account management
- API key generation and management
- Merchant dashboard data

**4\. Reconciliation Service**

- Matches transactions with provider responses
- Identifies discrepancies
- Generates reconciliation reports

**5\. Settlement Service**

- Calculates settlement amounts
- Processes settlements to merchants
- Handles settlement disputes

**6\. Fee Calculation Service**

- Calculates fees dynamically
- Supports percentage, fixed, tiered pricing
- Tracks commissions

**7\. Provider Adapter Framework**

- Abstracts provider API differences
- Handles different protocols (REST, SOAP, etc.)
- Circuit breaker for provider failures
- Connection pooling

## Part 4: Smart Routing Algorithm

**Aadvik:** “How do you decide which provider to route a transaction to? This is critical for cost optimization and success rate.”

**Sara:** “Smart routing is the heart of the payment gateway. We use a multi-factor scoring algorithm that considers cost, latency, success rate, and merchant preferences.”

### A. Routing Algorithm: Multi-Factor Scoring

**Routing Decision Factors:**

1. **Cost**: Transaction fee charged by provider
2. **Latency**: Average response time from provider
3. **Success Rate**: Percentage of successful transactions
4. **Provider Health**: Current health status (up/down)
5. **Merchant Preference**: Merchant’s preferred providers
6. **Load**: Current load on provider
7. **Geographic**: Provider’s geographic coverage

### B. Routing Score Calculation

**Provider Score Formula:**

```c
ProviderScore = (
    CostWeight × normalizeCost(cost) +
    LatencyWeight × normalizeLatency(latency) +
    SuccessRateWeight × normalizeSuccessRate(successRate) +
    HealthWeight × normalizeHealth(health) +
    LoadWeight × normalizeLoad(load)
) × MerchantPreferenceMultiplier

Where:
- normalizeCost: Lower cost = higher score (inverse)
- normalizeLatency: Lower latency = higher score (inverse)
- normalizeSuccessRate: Higher success rate = higher score (direct)
- normalizeHealth: Health status (1.0 = healthy, 0.0 = down)
- normalizeLoad: Lower load = higher score (inverse)
- MerchantPreferenceMultiplier: 1.2 if preferred, 1.0 if not
```

**Weight Configuration (example):** Cost 30%, Latency 20%, Success rate 35%, Health 10%, Load 5% (configurable per merchant).

### C. Routing Algorithm Flow

Normalization: cost/latency/load use min–max scaling (lower = higher score); success rate and health use direct 0–1 mapping.

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*OTsoY6jcrjNospDuyd5E5A.png)

### D. Provider Health Monitoring

**Health Metrics:**

- **Response Time**: Average latency (last 100 requests)
- **Success Rate**: Percentage of successful transactions (last 1000 requests)
- **Error Rate**: Percentage of errors (last 1000 requests)
- **Circuit Breaker State**: Open/Closed/Half-Open

**Provider health** is a weighted score (response time 30%, success rate 50%, 1−error rate 20%); circuit breaker OPEN forces score 0; status is HEALTHY if score > 0.7 else UNHEALTHY.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Uol4dAKHlxdqiI1nTSw5aw.png)

### E. Routing Flow

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*OFrya_F-BRgSf-i38GQGng.png)

## Part 5: Multi-Provider Integration & Failover

**Aadvik:** “How do you handle provider failures? What happens when a provider is down?”

**Sara:** “Provider failover is critical for high availability. We use circuit breakers and automatic failover to backup providers.”

### A. Provider Failover Strategy

**Failover Flow:**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8H-5EDijpKZ2YLkuGTFlKg.png)

### B. Circuit Breaker Pattern

**Circuit Breaker States:**

1. **Closed**: Normal operation, requests flow through
2. **Open**: Provider is down, fail fast to backup
3. **Half-Open**: Testing if provider recovered

**Circuit Breaker:** Open after N failures (e.g. 5); after timeout (e.g. 60s) go to Half-Open; in Half-Open allow a few probes; on success close, on failure reopen.

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*kmnVGrpI5n8RkDiH41hH6A.png)

### C. Provider Adapter Framework

**Adapter Pattern:**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*GzjGXL51XhNXfHJ2T37viw.png)

**Provider Adapter Interface:** `processPayment`, `checkStatus`, `refund`, `getHealth` — each provider implements this to hide API differences.

### D. Load Balancing Across Providers

**Load Balancing Strategy:**

1. **Round Robin**: Distribute requests evenly
2. **Weighted Round Robin**: Weight based on provider capacity
3. **Least Connections**: Route to provider with least active connections
4. **Response Time Based**: Route to fastest provider

**Load balancer selection:**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ooH9Bt_G0e3me3wXeBjvqg.png)

## Part 6: Fee Calculation Algorithm

**Aadvik:** “How do you calculate fees? Different merchants might have different pricing models.”

**Sara:** “Fee calculation is dynamic and supports multiple pricing models: percentage, fixed, tiered, and hybrid.”

### A. Fee Calculation Models

**1\. Percentage Model:**

```c
Fee = TransactionAmount × PercentageRate
Example: ₹1,000 × 2% = ₹20
```

**2\. Fixed Model:**

```c
Fee = FixedAmount
Example: ₹2 per transaction
```

**3\. Tiered Model:**

```c
Fee = Calculated based on transaction amount tiers
Example:
  - ₹0 - ₹1,000: 2%
  - ₹1,001 - ₹10,000: 1.5%
  - ₹10,001+: 1%
```

**4\. Hybrid Model:**

```c
Fee = FixedAmount + (TransactionAmount × PercentageRate)
Example: ₹2 + (₹1,000 × 1%) = ₹12
```

### B. Fee Calculation Flow (by model)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FB9tITnNkIbb6-KswdmXRg.png)

### C. Fee Calculation Sequence

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*LTK_0rPr-V-X_O6KK-eJ8A.png)

## Part 7: Merchant Onboarding Workflow

**Aadvik:** “How do you onboard merchants? What’s the KYC process?”

**Sara:** “Merchant onboarding involves KYC verification, account setup, and API key generation. We use a workflow-based approach.”

### A. Onboarding Workflow

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*XYZhBr5MSxfhEmrnr8MwSQ.png)

### B. KYC Verification Process

**KYC Documents Required:**

- Business registration certificate
- PAN card
- Bank account details
- Address proof
- Identity proof (for individual merchants)

**KYC Verification Steps:**

1. **Document Upload**: Merchant uploads KYC documents
2. **Document Validation**: Validate document format and completeness
3. **Automated Verification**: OCR and data extraction
4. **Manual Review**: Human review for complex cases
5. **Approval/Rejection**: Approve or request additional documents

**KYC verification flow:** Validate documents → OCR extraction → verify against external sources → risk score → decision: ❤0 approve, 30–70 manual review, >70 reject.

![](https://miro.medium.com/v2/resize:fit:1152/format:webp/1*PNrq2uvyqIaV3JfIGJpcBQ.png)

### C. API Key Generation

**API Key Structure:**

```c
Format: `sk_live_` + `<32_random_chars>` or `sk_test_` + `<32_random_chars>`
Example: `sk_live_` + `<32_random_chars>`
```

**API key generation:** Cryptographically secure random string (e.g. 32 chars) → prefix `sk_live_` or `sk_test_` → store SHA256 hash only → return plain key once.

## Part 8: Database Design

**Aadvik:** “What data do you need to store? How do you design the database schema?”

**Sara:** “We need to store merchant data, transactions, provider configurations, fees, and more. Here’s the schema:”

### A. Database Schema

**1\. Merchants Table:**

```c
CREATE TABLE merchants (
    merchant_id VARCHAR(50) PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20),
    business_type VARCHAR(50),  -- INDIVIDUAL, COMPANY, PARTNERSHIP
    kyc_status VARCHAR(20) NOT NULL,  -- PENDING, APPROVED, REJECTED
    kyc_verified_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,  -- ACTIVE, INACTIVE, SUSPENDED
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_email (email),
    INDEX idx_kyc_status (kyc_status),
    INDEX idx_status (status)
);
```

**2\. Transactions Table:**

```c
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    merchant_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50),
    payment_method VARCHAR(20) NOT NULL,  -- CARD, UPI, WALLET, NET_BANKING
    provider_id VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    fee_amount DECIMAL(15, 2) NOT NULL,
    net_amount DECIMAL(15, 2) NOT NULL,  -- amount - fee
    status VARCHAR(20) NOT NULL,  -- PENDING, SUCCESS, FAILED, REFUNDED
    provider_transaction_id VARCHAR(100),
    provider_response JSONB,
    failure_reason VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) PARTITION BY RANGE (created_at);
```

**3\. Providers Table:**

```c
CREATE TABLE providers (
    provider_id VARCHAR(50) PRIMARY KEY,
    provider_name VARCHAR(100) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,  -- CARD, UPI, WALLET, NET_BANKING
    api_endpoint VARCHAR(255),
    api_key VARCHAR(255),
    status VARCHAR(20) NOT NULL,  -- ACTIVE, INACTIVE
    cost_percentage DECIMAL(5, 2),  -- Percentage fee
    cost_fixed DECIMAL(10, 2),  -- Fixed fee
    average_latency_ms INT,
    success_rate DECIMAL(5, 2),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_payment_method (payment_method),
    INDEX idx_status (status)
);
```

**4\. Merchant Provider Preferences Table:**

```c
CREATE TABLE merchant_provider_preferences (
    preference_id VARCHAR(50) PRIMARY KEY,
    merchant_id VARCHAR(50) NOT NULL,
    provider_id VARCHAR(50) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    priority INT NOT NULL,  -- Lower number = higher priority
    is_preferred BOOLEAN DEFAULT FALSE,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    UNIQUE KEY uk_merchant_provider_method (merchant_id, provider_id, payment_method),
    INDEX idx_merchant_id (merchant_id)
);
```

**5\. Fee Configuration Table:**

```c
CREATE TABLE fee_configurations (
    fee_config_id VARCHAR(50) PRIMARY KEY,
    merchant_id VARCHAR(50) NOT NULL,
    pricing_model VARCHAR(20) NOT NULL,  -- PERCENTAGE, FIXED, TIERED, HYBRID
    percentage_rate DECIMAL(5, 2),
    fixed_amount DECIMAL(10, 2),
    min_fee DECIMAL(10, 2),
    max_fee DECIMAL(10, 2),
    tier_config JSONB,  -- For tiered pricing
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(merchant_id),
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_effective_from (effective_from)
);
```

**6\. Provider Metrics Table:**

```c
CREATE TABLE provider_metrics (
    metric_id VARCHAR(50) PRIMARY KEY,
    provider_id VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    total_requests INT NOT NULL DEFAULT 0,
    successful_requests INT NOT NULL DEFAULT 0,
    failed_requests INT NOT NULL DEFAULT 0,
    average_latency_ms INT,
    total_amount DECIMAL(15, 2),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    UNIQUE KEY uk_provider_date (provider_id, metric_date),
    INDEX idx_provider_id (provider_id),
    INDEX idx_metric_date (metric_date)
);
```

**7\. Reconciliation Table:**

```c
CREATE TABLE reconciliations (
    reconciliation_id VARCHAR(50) PRIMARY KEY,
    reconciliation_date DATE NOT NULL,
    provider_id VARCHAR(50) NOT NULL,
    gateway_transactions INT NOT NULL,
    provider_transactions INT NOT NULL,
    matched_transactions INT NOT NULL,
    unmatched_transactions INT NOT NULL,
    discrepancy_amount DECIMAL(15, 2),
    status VARCHAR(20) NOT NULL,  -- PENDING, COMPLETED, DISCREPANCY
    created_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
    INDEX idx_reconciliation_date (reconciliation_date),
    INDEX idx_provider_id (provider_id)
);
```

### B. Database Sharding

**Sharding Strategy:**

- Shard transactions table by `merchant_id` (hash-based)
- Each shard handles subset of merchants
- Enables horizontal scaling

**Partitioning:**

- Partition transactions table by date (monthly partitions)
- Archive old partitions
- Improves query performance

## Part 9: API Design

**Aadvik:** “What APIs do you expose? How do you design the API endpoints?”

**Sara:** “We expose APIs for payment processing, merchant management, and reporting. Here are the key endpoints:”

### A. Payment APIs

### 1\. Initiate Payment

**Endpoint:** `POST /api/v1/payments`

**Request:**

```c
{
  "amount": 1000.00,
  "currency": "INR",
  "payment_method": "UPI",
  "customer_id": "cust_123",
  "order_id": "order_456",
  "callback_url": "https://merchant.com/callback",
  "metadata": {
    "product_name": "Product ABC"
  }
}
```

**Response (200 OK):**

```c
{
  "transaction_id": "txn_789",
  "payment_url": "https://gateway.com/pay/txn_789",
  "status": "PENDING",
  "amount": 1000.00,
  "currency": "INR",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2\. Check Payment Status

**Endpoint:** `GET /api/v1/payments/{transaction_id}`

**Response (200 OK):**

```c
{
  "transaction_id": "txn_789",
  "merchant_id": "merchant_123",
  "amount": 1000.00,
  "currency": "INR",
  "fee_amount": 20.00,
  "net_amount": 980.00,
  "status": "SUCCESS",
  "payment_method": "UPI",
  "provider_id": "provider_456",
  "provider_transaction_id": "provider_txn_789",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

### 3\. Process Refund

**Endpoint:** `POST /api/v1/payments/{transaction_id}/refund`

**Request:**

```c
{
  "amount": 500.00,  // NULL for full refund
  "reason": "Customer requested refund"
}
```

**Response (200 OK):**

```c
{
  "refund_id": "ref_123",
  "transaction_id": "txn_789",
  "amount": 500.00,
  "status": "PROCESSING",
  "created_at": "2024-01-15T10:35:00Z"
}
```

### B. Merchant APIs

### 1\. Create Merchant

**Endpoint:** `POST /api/v1/merchants`

**Request:**

```c
{
  "business_name": "ABC Store",
  "email": "merchant@abcstore.com",
  "phone": "+911234567890",
  "business_type": "COMPANY"
}
```

**Response (201 Created):**

```c
{
  "merchant_id": "merchant_123",
  "business_name": "ABC Store",
  "email": "merchant@abcstore.com",
  "kyc_status": "PENDING",
  "status": "INACTIVE",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 2\. Generate API Key

**Endpoint:** `POST /api/v1/merchants/{merchant_id}/api-keys`

**Request:**

```c
{
  "environment": "production"  // or "test"
}
```

**Response (200 OK):**

```c
{
  "api_key": "sk_live_<32_random_chars>",
  "environment": "production",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### C. Reporting APIs

### 1\. Get Transaction History

**Endpoint:** `GET /api/v1/merchants/{merchant_id}/transactions?page=1&limit=20&status=SUCCESS`

**Response (200 OK):**

```c
{
  "transactions": [
    {
      "transaction_id": "txn_789",
      "amount": 1000.00,
      "status": "SUCCESS",
      "payment_method": "UPI",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1000,
    "total_pages": 50
  }
}
```

## Part 10: Reconciliation Algorithm

**Aadvik:** “How do you reconcile transactions with provider responses? This is critical for accuracy.”

**Sara:** “Reconciliation matches our transaction records with provider transaction records to identify discrepancies.”

### A. Reconciliation Algorithm

**Reconciliation Process:**

1. **Fetch Gateway Transactions**: Get all transactions for a provider on a given date
2. **Fetch Provider Transactions**: Get all transactions from provider for the same date
3. **Match Transactions**: Match by transaction ID, amount, timestamp
4. **Identify Discrepancies**: Find unmatched transactions
5. **Generate Report**: Create reconciliation report

**Reconciliation steps:** Fetch gateway and provider transactions for date → match by `provider_transaction_id` (amount exact, timestamp within 5 min) → classify matched / unmatched gateway / unmatched provider → compute discrepancy (sum gateway − sum provider) → store record (COMPLETED or DISCREPANCY).

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*UJbnrL2ZdGLKE3LaGnyOqQ.png)

### B. Reconciliation Flow

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NGKvBVffWWFyVs32FcgaqQ.png)

### C. Reconciliation Scheduling

**Daily Reconciliation:**

- Run reconciliation for each provider daily
- Process previous day’s transactions
- Generate reconciliation reports
- Alert on discrepancies

**Real-Time Reconciliation:**

- Reconcile critical transactions immediately
- Flag discrepancies for manual review
- Auto-retry failed reconciliations

## Part 11: Settlement Processing

**Aadvik:** “How do you settle funds to merchants? What’s the settlement cycle?”

**Sara:** “Settlement processes funds to merchants based on T+1 or T+2 cycles. We calculate net amounts after deducting fees.”

### A. Settlement Flow

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FA9Se1nDa3Sp10rkKOpdZg.png)

**Settlement:** Fetch transactions to settle for merchant + date → sum amount and fees for SUCCESS txns → net = total − fees → initiate bank transfer → update settlement status.

### B. Settlement Cycles

**T+1 Settlement:**

- Transactions on Day 1 → Settled on Day 2
- Standard settlement cycle
- Most common for regular merchants

**T+2 Settlement:**

- Transactions on Day 1 → Settled on Day 3
- Extended settlement cycle
- Used for high-risk merchants or special agreements

**T+0 Settlement:**

- Same-day settlement
- Premium feature
- Additional fees may apply

## Part 12: Failure Handling & Resilience

**Aadvik:** “What happens when things go wrong? How do you handle failures?”

**Sara:** “We handle failures gracefully with retries, circuit breakers, and automatic failover.”

### A. Failure Scenarios

**1\. Provider API Unavailable:**

**Problem**: Provider’s API is down

**Mitigation**:

- Circuit breaker opens after threshold failures
- Automatic failover to backup provider
- Queue transactions for retry
- Show merchant: “Payment temporarily unavailable”

**Recovery**: When provider recovers, process queued transactions

**2\. Routing Service Timeout:**

**Problem**: Routing decision times out

**Mitigation**:

- Use cached routing decision
- Fallback to default provider
- Retry routing (max 2 retries)

**Recovery**: Routing service recovers automatically

**3\. Fee Calculation Failure:**

**Problem**: Fee calculation service unavailable

**Mitigation**:

- Use default fee configuration
- Cache fee calculation results
- Retry fee calculation (max 2 retries)

**Recovery**: Fee service recovers, recalculate fees

**4\. Reconciliation Failure:**

**Problem**: Reconciliation process fails

**Mitigation**:

- Retry reconciliation (max 3 retries)
- Flag for manual reconciliation
- Alert operations team

**Recovery**: Manual reconciliation by operations team

**5\. Settlement Failure:**

**Problem**: Bank transfer fails

**Mitigation**:

- Retry settlement (max 3 retries)
- Flag for manual settlement
- Alert operations team

**Recovery**: Manual settlement by operations team

### B. Idempotency

**Why Idempotency is Critical:**

- Network retries can cause duplicate requests
- Merchant might retry payment
- System must handle duplicate requests gracefully

**Implementation:**

- Each payment request has unique `transaction_id`
- Check if transaction\_id already exists
- If exists, return existing transaction status (don’t process again)
- If new, process transaction

**Idempotency Key:**

- Format: `merchant_id + order_id + timestamp`
- Stored in Redis with transaction response
- TTL: 24 hours

## Part 13: Scaling Strategies

**Aadvik:** “How do you scale this system to handle 20,000+ TPS?”

**Sara:** “Scaling requires multiple strategies across different components:”

### A. Horizontal Scaling

**1\. Payment Service:**

- Stateless services → scale horizontally
- Load balancer distributes requests
- Auto-scale based on TPS and latency
- Each instance handles subset of transactions

**2\. Routing Service:**

- Stateless routing decisions
- Scale horizontally
- Cache provider metrics for fast routing

**3\. Provider Adapter:**

- Stateless adapter instances
- Scale horizontally
- Connection pooling per instance

### B. Database Scaling

**1\. Read Replicas:**

- Read replicas for read-heavy workloads
- Separate read and write paths
- Reduces primary database load

**2\. Sharding:**

- Shard transactions table by `merchant_id` (hash-based)
- Each shard handles subset of merchants
- Enables horizontal scaling

**3\. Partitioning:**

- Partition transactions table by date (monthly partitions)
- Archive old partitions
- Improves query performance

### C. Caching Strategy

**Multi-Layer Caching:**

**L1: Application Cache (In-Memory)**

- Cache provider metrics (1 min TTL)
- Cache routing decisions (5 min TTL)
- Cache merchant configurations (10 min TTL)
- LRU eviction, 100MB per instance

**L2: Redis Cache (Distributed)**

- Provider metrics (1 min TTL)
- Routing decisions (5 min TTL)
- Merchant configurations (10 min TTL)
- Transaction status (1 hour TTL)
- Idempotency keys (24 hour TTL)

**L3: Database (Persistent)**

- Source of truth
- Used for writes and cache misses

### D. Provider Integration Scaling

**1\. Connection Pooling:**

- Maintain connection pools per provider
- Pool size: 10–50 connections
- Reuse connections

**2\. Circuit Breaker:**

- Prevent cascading failures
- Fail fast when provider is down
- Automatic recovery

**3\. Load Balancing:**

- Multiple provider adapter instances
- Distribute load across instances
- Health checks

## Part 14: Monitoring & Observability

**Aadvik:** “How do you monitor this system?”

**Sara:** “Comprehensive monitoring is essential for a payment gateway.”

### A. Key Metrics

**1\. Transaction Metrics:**

- Transaction success rate
- Transaction latency (p50, p95, p99)
- Transactions per second (TPS)
- Failed transactions count
- Payment method distribution

**2\. Business Metrics:**

- Total transaction volume (daily, monthly)
- Total transaction value (daily, monthly)
- Active merchants
- Average transaction amount
- Fee revenue

**3\. System Metrics:**

- API response time
- Database query latency
- Redis cache hit rate
- Provider API latency
- Error rates

**4\. Provider Metrics:**

- Provider success rate
- Provider latency
- Provider error rate
- Provider cost per transaction
- Provider health status

**5\. Routing Metrics:**

- Routing decision latency
- Provider selection distribution
- Failover rate
- Cost savings from routing

### B. Alerting Rules

**Critical Alerts:**

- Transaction success rate < 99%
- Transaction latency p95 > 500ms
- Provider API failure rate > 1%
- Database connection pool > 90%
- Error rate > 0.1%

**Warning Alerts:**

- Transaction latency p95 > 300ms
- Cache hit rate < 80%
- Provider API latency > 500ms
- Routing decision latency > 50ms
- Queue depth > 1000

### C. SLOs & SLIs

**Service Level Indicators:**

- Transaction success rate: 99.5%
- Transaction latency: p95 < 500ms
- Routing decision latency: p95 < 50ms
- API availability: 99.99%
- Provider failover time: < 100ms

**Service Level Objectives:**

- 99.5% of transactions complete successfully
- 95% of transactions complete within 500ms
- 99.99% API uptime
- Zero data loss

**Error Budget:**

- 0.5% error budget per month
- If exceeded: stop feature work, focus on reliability

## Part 15: Cost Analysis

**Aadvik:** “What’s the infrastructure cost for running a payment gateway at this scale?”

**Sara:** “Let me break down the infrastructure costs. I’ll use AWS pricing as reference.”

> **Critical Note:** The cost estimates provided below are **rough approximations and assumptions** based on publicly available pricing information and typical cloud provider rates. These numbers are **NOT actual billing amounts** and should be treated as **illustrative estimates only**.

### A. Infrastructure Components

**1\. Compute (EC2/ECS):**

- Payment services: 30 instances (c5.2xlarge) = ~$4,500/month
- Routing services: 10 instances (c5.xlarge) = ~$1,500/month
- Provider adapters: 20 instances (c5.xlarge) = ~$3,000/month
- **Total Compute: ~$9,000/month**

**2\. Database (RDS PostgreSQL):**

- Primary: db.r5.4xlarge (multi-AZ) = ~$2,000/month
- Read replicas: 5 × db.r5.2xlarge = ~$5,000/month
- **Total Database: ~$7,000/month**

**3\. Caching (ElastiCache Redis):**

- 5 × cache.r5.xlarge = ~$2,500/month
- **Total Cache: ~$2,500/month**

**4\. Messaging (Kafka/MSK):**

- 5 × kafka.m5.large = ~$800/month
- **Total Messaging: ~$800/month**

**5\. Network & Data Transfer:**

- Data transfer: ~$2,000/month
- **Total Network: ~$2,000/month**

**6\. Storage:**

- Transaction data: 168TB × 0.023/GB= 0.023/ *GB* = 4,000/month
- **Total Storage: ~$4,000/month**

**Total Estimated Monthly Cost: ~$25,300/month**

**Note:** Actual costs vary significantly based on:

- Reserved instances (30–70% discount)
- Enterprise discounts
- Actual usage patterns
- Regional pricing differences
- Optimization strategies

## Part 16: Trade-offs & Future Improvements

**Aadvik:** “What trade-offs did you make? What would you improve?”

**Sara:** “Important trade-offs:”

**1\. Routing Algorithm: Complexity vs Optimization**

- **Chosen**: Multi-factor scoring algorithm
- **Trade-off**: More complex routing logic
- **Mitigation**: Cache routing decisions, optimize algorithm
- **Benefit**: Better cost optimization and success rate

**2\. Provider Failover: Latency vs Availability**

- **Chosen**: Automatic failover with circuit breaker
- **Trade-off**: Additional latency on failover
- **Mitigation**: Fast failover (< 100ms), health monitoring
- **Benefit**: High availability, no transaction loss

**3\. Fee Calculation: Real-Time vs Performance**

- **Chosen**: Real-time fee calculation
- **Trade-off**: Additional service call
- **Mitigation**: Cache fee configurations, async calculation
- **Benefit**: Accurate fee calculation

**4\. Reconciliation: Real-Time vs Batch**

- **Chosen**: Daily batch reconciliation
- **Trade-off**: Delayed discrepancy detection
- **Mitigation**: Real-time reconciliation for critical transactions
- **Benefit**: Efficient processing, lower cost

**Aadvik:** “What would you improve if you had more time?”

**Sara:** “Additional improvements:

1. **Machine Learning Routing**: ML-based provider selection using historical data
2. **Predictive Scaling**: ML-based prediction of transaction volume
3. **Advanced Analytics**: Real-time transaction analytics dashboard
4. **A/B Testing**: Test different routing strategies
5. **Cost Optimization**: More aggressive auto-scaling and spot instances
6. **Multi-Region Deployment**: Deploy in multiple regions for resilience
7. **Real-Time Reconciliation**: Real-time transaction matching for all transactions”

## Summary

**Key Takeaways:**

1. **Smart Routing** — Multi-factor algorithm optimizes cost, latency, and success rate
2. **Multi-Provider Integration** — Adapter pattern abstracts provider differences
3. **Provider Failover** — Circuit breaker and automatic failover ensure high availability
4. **Fee Calculation** — Dynamic fee calculation supports multiple pricing models
5. **Reconciliation** — Automated transaction matching identifies discrepancies
6. **Settlement** — Automated settlement processing with T+1/T+2 cycles

**System Handles:**

- 1 billion transactions per month
- 20,000+ TPS (peak)
- 100,000 merchants
- 50+ payment providers
- Sub-500ms payment processing
- 99.99% availability

**Architecture Highlights:**

- **Smart routing algorithm** for cost optimization
- **Multi-provider integration** for high availability
- **Circuit breaker pattern** for resilience
- **Automated reconciliation** for accuracy
- **Comprehensive monitoring** with SLOs

**This architecture powers payment gateway aggregation at massive scale with intelligent routing and high availability!**

> *Liked this deep dive story? If Yes Please* ***👏 Clap(50)*** *|* ***📤 Share*** *|* ***🔔 Follow***