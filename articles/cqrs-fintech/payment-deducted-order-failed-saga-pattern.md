---
type: Article
title: "Payment Deducted But Order Failed: System Design Deep Dive on the Saga Pattern and Distributed Transactions"
source: "https://codefarm0.medium.com/payment-deducted-but-order-failed-system-design-deep-dive-on-the-saga-pattern-and-distributed-025b27cb2e0a"
author: "Arvind Kumar"
published: 2026-07-22
created: 2026-08-01
description: "System Design Real Scenarios — A Popular Interview Question That Tests the Saga Pattern, Compensation Workflows, Idempotency Keys, Retry Handling, and Distributed Transaction Coordination"
---

# Payment Deducted But Order Failed: System Design Deep Dive on the Saga Pattern and Distributed Transactions

> **Source**: [Medium — codefarm0](https://codefarm0.medium.com/payment-deducted-but-order-failed-system-design-deep-dive-on-the-saga-pattern-and-distributed-025b27cb2e0a)
> **Author**: Arvind Kumar
> **Published**: 2026-07-22



> *Money left the customer’s account. The order was never created. Now what?*

This is the nightmare scenario for every e-commerce platform. The payment gateway returned “success.” The payment service recorded the charge. Then something went wrong — the inventory service was down, the database timed out, or the order service crashed mid-transaction. The money is gone. The order does not exist. The customer has nothing to show for their payment.

Fixing this is not about writing better code. It is about accepting a fundamental constraint of distributed systems: **you cannot have ACID transactions across independent services**. Each service has its own database. There is no global transaction coordinator that can atomically commit or roll back across all of them.

---

Interviewers love this question because it is the most common real-world distributed systems failure and reveals whether you understand:

## Concepts at a Glance

- Why distributed transactions are fundamentally different from single-database transactions
- The Saga pattern and how it replaces ACID across microservices
- Choreography-based sagas vs orchestrator-based sagas
- Compensation workflows — how to undo a completed step when a later step fails
- Idempotency keys for safe retries without duplicate charges
- The outbox pattern for reliable event publication
- Crash recovery — what happens when the orchestrator itself fails

In the previous episode, we explored fanout architecture for push notifications. Today, we step into the most critical reliability problem in distributed systems.

Let’s watch how the conversation unfolds.

## The Scenario

**Arvind (Interviewer):**  
A customer places an order. The payment is deducted successfully from their card. But the order creation fails — the inventory service returns an error. The customer is charged but has no order. How do you prevent this? And if it happens, how do you recover?

**Arjun (Candidate):**  
Let me map the happy path first. An e-commerce order touches at least three services.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*dRxXcV-Oj3RgUPaFThUFXg.png)

When every service responds correctly, the order flows through payment, inventory, and notification. But each arrow between services is a network call. Each call can fail. Each service has its own database with independent transaction boundaries.

The failure scenario:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*mPyolqjN5tbIJuPO6jvKKA.png)

The order service called payment first, then inventory. Payment succeeded. Inventory failed. The order cannot be fulfilled, but the money was already charged. The system is in an inconsistent state.

## Why Not a Distributed Transaction?

**Arvind:**  
Could you use a two-phase commit (2PC) across all three services?

**Arjun:**  
Two-phase commit requires a global coordinator that asks every participant to prepare, then commit. In theory, it works. In practice, it fails for three reasons:

***2PC problems in microservices:***

- **Blocking**: Participants hold locks while waiting for the coordinator’s decision. If the coordinator crashes, locks are held until recovery — potentially minutes or hours.
- **Availability**: Every participant must be available during the prepare phase. If inventory is down, the entire transaction blocks.
- **No cross-database standard**: MySQL, PostgreSQL, DynamoDB, and Redis do not speak a common transaction protocol.

Microservice architectures deliberately avoid distributed transactions. Instead, they use the Saga pattern.

## The Saga Pattern

**Arvind:**  
Explain the Saga pattern. How does it solve this?

**Arjun:**  
A saga is a sequence of local transactions where each step has a compensating transaction that undoes it.

Instead of one global ACID transaction, the saga breaks the workflow into individual steps:

```c
Step 1: Order Service  -> Create order (PENDING)
Step 2: Payment Service -> Charge customer
Step 3: Inventory Service -> Reserve items
Step 4: Order Service -> Confirm order
```

Each step commits to its own database immediately. If step 3 fails, the saga executes compensating actions for steps 2 and 1:

```c
Compensation 1: Payment Service -> Refund customer (undo step 2)
Compensation 2: Order Service  -> Cancel order (undo step 1)
```

The system ends in a consistent state — order cancelled, money returned — without ever needing a global transaction.

## Choreography vs Orchestration

**Arvind:**  
There are two ways to implement sagas: choreography and orchestration. Explain both.

**Arjun:**  
In **choreography**, each service listens for events and decides what to do next. There is no central coordinator.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*bxhQGzJT2hSF_cmhT_oxZw.png)

Each service publishes events after completing its local transaction. Other services subscribe to the events they care about. If a step fails, the service publishes a failure event. Downstream services detect the failure and execute their compensating actions.

In **orchestration**, a central Saga Orchestrator tells each service what to do.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*rCqfp73Yn3SXrhwDyp9qQg.png)

> ***Choreography*** *is lightweight — no central service, no single point of failure. But the flow is implicit and harder to trace. A failure in one service triggers a cascade of events that is difficult to debug.*
> 
> ***Orchestration*** *centralizes the workflow logic. The saga state is stored in the orchestrator. You can pause, resume, retry, and audit. The tradeoff is that the orchestrator becomes a critical dependency.*

For payment workflows, orchestration is almost always the right choice because:

- You need reliable audit trails (who charged what, when, and why)
- You need explicit retry and timeout policies per step
- You need to handle partial failures — some steps succeeded, some failed, some are in-flight
- You need to know the exact state of every in-progress saga

## Idempotency Keys

**Arvind:**  
What happens when the orchestrator sends a “charge customer” command, the payment service processes it, but the response is lost? The orchestrator retries. Now the customer is charged twice.

**Arjun:**  
That is where idempotency keys come in.

Every command from the orchestrator carries an idempotency key — a unique identifier for the operation.

```c
POST /payment/charge
Headers:
  Idempotency-Key: saga-123-step-2-retry-1
Body:
  order_id: 456
  amount: 29.99
```

**The payment service checks**: have I already processed this idempotency key? If yes, return the previous result without charging again. If no, process the charge and store the key with the result.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*lO9BZ7dW3ejt2PxDC2n4YQ.png)

The idempotency store (typically Redis with TTL or a database table with a unique constraint) ensures that duplicate requests are detected and blocked before they reach the payment gateway.

***Idempotency key lifecycle****:*

- Client generates a unique key before sending the request
- Server checks if the key was already processed
- If processed, return cached result (idempotent replay)
- If not processed, execute the operation and store the key with the result
- Key expires after a defined retention period (typically 24–72 hours)

This guarantees that retries never cause duplicate charges, even if the response is lost and the orchestrator retries ten times.

## The Outbox Pattern

**Arvind:**  
The orchestrator needs to publish events after each step. What if the orchestrator updates its database but crashes before publishing the event?

**Arjun:**  
That is the dual-write problem — writing to the database and publishing an event are two separate operations. If one fails and the other succeeds, the system is inconsistent.

The solution is the outbox pattern.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*fu9YF_JZpbn_AaHjAEkALg.png)

The orchestrator writes the saga state update and the outgoing event in the same database transaction. A separate outbox poller reads unprocessed events from the outbox table and publishes them to the message bus. If the orchestrator crashes after committing the transaction but before publishing, the outbox poller ensures the event is eventually published.

This guarantees **exactly-once event publication** — the event is published exactly once because the outbox record is either committed (and will be polled) or not committed (and the transaction is rolled back).

**Arvind:**  
Design the complete order-payment saga system.

**Arjun:**

Key decisions:

- **Orchestrator-based saga**: A central Saga Orchestrator maintains the state machine for each order. It knows which step is active, which steps completed, and which compensations need to run.
- **Idempotency keys on every service call**: Each command from the orchestrator includes an idempotency key. Services check the key before processing. Duplicates return cached results.
- **Outbox pattern on the orchestrator**: Saga state updates and outgoing events are written in the same database transaction. The outbox poller ensures events are eventually published even if the orchestrator crashes.
- **Retry with backoff**: Failed steps are retried with exponential backoff (1s, 4s, 16s, 64s). After 3 retries, the saga moves to the compensation path.
- **Dead letter queue**: Sagas that cannot complete even with compensations (e.g., refund fails) are escalated to a dead letter queue for manual operations team intervention.
- **Event-driven participant communication**: Services do not call each other directly. They listen for events from the orchestrator and publish results back through Kafka.

## Crash Recovery

**Arvind:**  
What happens when the saga orchestrator itself crashes mid-saga?

**Arjun:**  
The saga state is stored in the database. When the orchestrator restarts, it scans for sagas in a PENDING or IN\_PROGRESS state.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Tyz772vrzpYb6QfkI1AQCA.png)

The recovery logic:

1. Scan for incomplete sagas
2. Check which steps have been completed (step records are durable in the saga DB)
3. Resume from the next uncompleted step
4. All commands use idempotency keys, so even if a step was actually completed but the record was lost in the crash, the service returns the cached result and no duplicate work happens

**Arvind:**  
What monitoring matters for a saga-based system?

**Arjun:**

1. **Saga completion rate** — Percentage of sagas that reach the terminal state (CONFIRMED or CANCELLED). Sagas stuck in IN\_PROGRESS for more than 30 minutes indicate a problem.
2. **Mean time to complete a saga** — How long the average order-payment flow takes. Growing time suggests a step is getting slower.
3. **Compensation rate** — Percentage of sagas that required compensations. A rising rate indicates problems in the happy path — inventory failures, payment declines, etc.
4. **Retry count distribution** — How many steps required retries. A step that consistently requires multiple retries is unhealthy.
5. **Idempotency key hit rate** — How many requests were deduplicated. A high rate means the orchestrator is retrying aggressively or the network is unreliable.
6. **Dead letter queue depth** — Sagas that require manual intervention. This should be near zero. If it grows, the compensation paths are failing.
7. **Outbox lag** — Time between event insertion in the outbox table and event publication to Kafka. Growing lag means the outbox poller is underprovisioned.

## Let’s Conclude

The “payment deducted but order failed” problem is not a bug. It is a fundamental consequence of distributed systems where data lives in multiple databases that cannot participate in a global transaction.

> **The solution is not 2PC or distributed transactions. It is the Saga pattern with reliable execution.**

**The winning architecture**:

- **Orchestrator-based saga**: Central state machine per workflow. Explicit step tracking, retry policies, and compensation logic.
- **Idempotency keys on every operation**: Guarantees that retries never cause duplicate charges or duplicate inventory reservations.
- **Outbox pattern**: Saga state updates and events are written atomically. Event publication is guaranteed even after crashes.
- **Compensation workflows**: Every forward step has a corresponding backward step. If the saga fails, compensations restore consistency.
- **Dead letter queue**: Sagas that resist automated recovery are escalated to human operators without data loss.

The system is not “eventually consistent” in the vague sense. It is **provably consistent** — every saga either completes successfully or compensates fully, leaving the system in a known valid state.

**Previously in this series:**  
Instagram Notification Storm

**Next up:**  
YouTube Video Processing Pipeline — Chunk processing, distributed workers, encoding pipelines, async workflows, and storage optimization

> *Liked this deep dive story? If Yes Please* ***👏 Clap(50)*** *|* ***📤 Share*** *|* ***🔔 Follow***

***Below is a collection of all related stories in one place***

## 22 Scenarios for System Design Interview

15 stories

![](https://miro.medium.com/v2/resize:fill:194:194/1*emu5NmEPO594xgR_y-zkTg.png) ![](https://miro.medium.com/v2/resize:fill:194:194/1*mabqXwQOXXV0BOZpaFuuzQ.png) ![](https://miro.medium.com/v2/resize:fill:194:194/1*5Wzb39bglYnbT9KVDifsmg.png)