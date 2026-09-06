---
type: Article
title: "Idempotency and Deduplication in Distributed Systems"
description: "Practical strategies for handling duplicate events and ensuring correctness in distributed systems — covering the three-layer defense model, idempotency keys, upserts, distributed locks, and the truth about exactly-once semantics."
source: "https://levelup.gitconnected.com/idempotency-and-deduplication-in-distributed-systems-d411a6e0f715"
author: "Nidhi Jain"
published: 2026-05-04
generated: { by: process:okf-migrate, at: 2026-07-25T00:00:00Z }
---

# Idempotency and Deduplication in Distributed Systems

> **Series**: System Design Advanced #2 — Practical Strategies for Handling Duplicate Events and Ensuring Correctness
> **Source**: [Level Up Coding](https://levelup.gitconnected.com/idempotency-and-deduplication-in-distributed-systems-d411a6e0f715)

---

## The Three Delivery Guarantees

Before solving the duplicate problem, you need to understand the trade-offs. Every messaging system makes one of three promises — and each has consequences.

| Guarantee | Description | Reality |
|:---|:---|:---|
| **At-most-once** | Message is delivered 0 or 1 time; no duplicates | Messages can be lost |
| **At-least-once** | Message is delivered 1+ times; no loss | Duplicates are inevitable |
| **Exactly-once** | Message is delivered exactly 1 time | Theoretically impossible in the general case |

Most production systems run on **at-least-once delivery** — because losing a message is worse than processing it twice. This means duplicate handling becomes your responsibility as the consumer author, not the infrastructure's.

---

## Why Duplicates Happen

Duplicates are not bugs — they are a direct consequence of reliability guarantees. Four concrete scenarios cause them in production:

1. **Producer retries**: The producer sends a message, the broker receives and persists it, but the acknowledgment is lost in transit. The producer retries → duplicate on the broker.
2. **Consumer crashes**: The consumer processes a message but crashes before acknowledging it. On restart, the broker redelivers → duplicate to the consumer.
3. **Rebalance-triggered redelivery**: A consumer leaves a consumer group (crash, network partition, scaling event). Its partitions are reassigned to another consumer, which starts from the last committed offset → messages after that offset are reprocessed.
4. **Network partitions**: Transient network failures cause acknowledgment timeouts, triggering retries from both producers and consumers.

---

## Why Exactly-Once Is Fundamentally Hard

The difficulty isn't engineering laziness — it's a fundamental property of distributed systems. Two problems make it theoretically unsolvable in the general case.

### The Two Generals Problem

Two armies on opposite hills must coordinate an attack. They can only communicate via messengers who might be captured:

- General A sends message: "Attack at dawn"
- General B receives it and sends acknowledgment: "Confirmed"
- But what if the acknowledgment messenger is captured?
- General A doesn't know if B got the message
- Should A attack alone? Should A resend?

This maps directly to distributed systems: you can never be certain whether a message was received, and whether an acknowledgment was delivered. There is no perfect coordination over unreliable communication — only trade-offs.

### The Crash Between Process and Acknowledge

A typical consumer flow has four steps:

1. Receive message from broker
2. Process business logic (DB writes, API calls)
3. Commit offset / acknowledge
4. Broker removes message from queue

A crash at step 4 means the work is done but the acknowledgment never arrives. The broker redelivers. Steps 2 and 3 run again on a message already processed. This gap between "work done" and "ack sent" is the fundamental source of consumer-side duplicates — and it cannot be fully closed at the infrastructure level.

There are two ways of solving duplicate events:

1. **Deduplication**: Detecting and removing duplicate messages or requests so they are processed only once.
2. **Idempotency**: Performing the same operation multiple times produces the same result as doing it once.

---

## The Three-Layer Defense Model

Duplicate handling is not one solution — it's three layers working together. Each layer covers the gaps the others miss.

---

### Layer 1: Infrastructure

Deduplication — trying to reduce duplicates before they reach consumers at the queue level — is the first line of defense. Different messaging systems offer different ways of achieving this.

#### SQS FIFO Deduplication

Use `MessageDeduplicationId` on each message. SQS automatically discards duplicates within a 5-minute window.

**Limitation**: Only prevents producer-side duplicates, not consumer-side crashes.

#### Kafka Idempotent Producer

Set `enable.idempotence = true`. Kafka assigns:

- **Producer IDs** and
- **Sequence numbers**

Duplicate writes from producer retries are silently dropped by the broker.

#### Kafka Exactly-Once Semantics (EOS)

Kafka achieves **system-level exactly-once** via:

- Idempotent producer
- Transactions
- Offset commits

But this works **only inside the Kafka ecosystem**. If you have multiple infrastructure components or distributed transactions, this does not work.

#### Deduplication Window

Kafka retains deduplication records at least as long as your message retention period.

> Kafka retains 7 days → keep dedup keys for at least 7 days.
> Delete older records via a scheduled cleanup job.

---

### Layer 2: Application

Sometimes deduplication is not feasible at the infrastructure level — at that point we need idempotency. Consumers must be safe when duplicates arrive.

This is the most important layer. Infrastructure reduces duplicates — application-level idempotency makes the ones that get through harmless.

#### Idempotency Keys — The Most Important Pattern

Every message carries a **unique business identifier**. Before doing any work, check whether you've already processed it.

```
Consumer receives event with idempotencyKey
  → INSERT INTO processed_events (idempotency_key, status)
    VALUES ('evt-123', 'processing')
  ├─ Constraint violation → DUPLICATE (already processed)
  └─ Insert succeeds → Proceed with business logic
```

The **unique constraint on the primary key** handles concurrent duplicates automatically — if two consumers race to process the same message, one insert succeeds and one throws a constraint violation, which you catch and treat as already processed.

#### Upserts Instead of Inserts

Replace `INSERT` with `INSERT ... ON CONFLICT DO UPDATE`. The first execution inserts. The second execution finds a conflict and updates to the same state. No duplicate row, no error.

```sql
INSERT INTO orders (order_id, status, amount)
VALUES ('ord-456', 'CONFIRMED', 99.99)
ON CONFLICT (order_id) DO UPDATE
SET status = EXCLUDED.status,
    amount = EXCLUDED.amount;
```

#### State-Based Guard Conditions

Add a `WHERE` clause guard that makes the update a no-op if the work is already done.

```sql
UPDATE orders
SET status = 'SHIPPED'
WHERE order_id = 'ord-456'
  AND status = 'CONFIRMED';  -- Guard: only ship if confirmed
```

A duplicate `SHIP` command finds `status = 'SHIPPED'` and the `WHERE` clause prevents the redundant update.

#### Natural Idempotent Design — SET over INCREMENT

Design operations to be idempotent by nature. Prefer setting absolute state over relative changes.

| Non-Idempotent | Idempotent |
|:---|:---|
| `UPDATE SET counter = counter + 1` | `INSERT INTO likes (user_id, post_id) VALUES (?, ?)` |
| `UPDATE SET balance = balance - 100` | `INSERT INTO withdrawals (txn_id, amount) VALUES (?, 100)` |
| Relative change — replay doubles it | Absolute fact — replay is harmless |

#### Deterministic Processing for Replay Safety

When replaying events from a checkpoint, your processing logic must always produce the same result for the same input. Non-deterministic logic breaks replay entirely.

| Non-Deterministic | Deterministic |
|:---|:---|
| `current_time = NOW()` | `event_time = event.timestamp` |
| `random_id = UUID()` | `id = event.idempotency_key` |
| External API call during processing | Fetch from cache, replay from event data |

---

### Layer 3: Critical Operations — For Truly Non-Idempotent Actions

Some operations cannot be restructured to be idempotent — charging a payment, sending an SMS, triggering a one-time webhook. Two patterns protect these.

#### Distributed Locks

Use Redis `SETNX` with a TTL to prevent concurrent duplicate execution. The TTL ensures the lock releases even if the consumer crashes mid-processing.

```
Consumer receives payment event
  → Redis SET payment:txn-789 "processing" NX EX 60
    ├─ Returns false → Another consumer is processing, skip
    └─ Returns true  → Acquired lock, proceed with payment
        → Process payment
        → DEL payment:txn-789 (release lock)
```

**The TTL must be longer than your maximum expected processing time.** Too short and the lock expires while still processing, allowing a second consumer to acquire it concurrently.

#### Saga Pattern for Distributed Transactions

For multi-step business transactions across services — charge payment, reserve inventory, send confirmation — a saga breaks the workflow into steps with compensating actions for each.

If step 3 fails, compensating transactions roll back steps 1 and 2.

No two-phase commit, no blocking locks across services — just choreographed forward progress with defined rollback paths.

---

## The Truth About Exactly-Once

"Exactly-once" as a marketing term from Kafka or other systems refers to **exactly-once *within* the messaging system itself** — between producer and broker, or broker and consumer. It does not mean exactly-once across your entire distributed application including external DB writes, API calls, and side effects.

The reality:

| Scope | What "Exactly-Once" Covers |
|:---|:---|
| **Kafka EOS** | Producer → Broker → Consumer delivery and offset commits |
| **Not covered** | External DB writes, third-party API calls, side effects outside Kafka |

True end-to-end exactly-once requires idempotency at the application layer. The messaging system can only guarantee delivery semantics within its own boundaries — everything beyond that is your responsibility.

---

## Key Takeaways

1. **At-least-once is the default reality** in production messaging systems — plan for duplicates, don't assume the infrastructure will prevent them.
2. **The Three-Layer Defense** combines infrastructure deduplication (SQS FIFO, Kafka idempotent producer), application idempotency (idempotency keys, upserts, guard conditions), and distributed locks/sagas for truly non-idempotent operations.
3. **Idempotency keys with unique constraints** are the single most important pattern — they make duplicates harmless by turning them into constraint violations you can safely ignore.
4. **Prefer SET over INCREMENT** — absolute state changes are naturally idempotent; relative changes amplify on replay.
5. **"Exactly-once" in Kafka means exactly-once within Kafka** — not across your entire application. End-to-end idempotency is always an application-layer concern.
