---
type: Article
title: "Kafka Producer Acknowledgment Failure — Preventing Duplicate Processing"
source: "https://codefarm0.medium.com/system-design-interview-what-happens-if-kafka-receives-an-event-but-the-producer-never-gets-the-6f3456538eae"
author: "Arvind Kumar"
published: 2026-06-27
created: 2026-06-27
description: "How to handle Kafka producer acknowledgment failures and prevent duplicate business processing through idempotent consumers, atomic deduplication, and the Transactional Outbox Pattern."
tags:
  - kafka
  - messaging
  - idempotency
  - distributed-systems
  - system-design
---

# Kafka Producer Acknowledgment Failure — Preventing Duplicate Processing

> **Source**: [Medium — Arvind Kumar](https://codefarm0.medium.com/system-design-interview-what-happens-if-kafka-receives-an-event-but-the-producer-never-gets-the-6f3456538eae)
> **Related**: [Messaging — Key Takeaways](../../system-design-architecture/messaging/), [Reference Dictionary — Messaging](../../reference-dictionary/messaging.md)

## The Core Problem

The most dangerous failures are the ones that leave your system uncertain.

Imagine your Order Service publishes an event to Kafka. The event reaches Kafka successfully. But before Kafka's acknowledgment reaches the producer, the network connection drops. Now the producer has a dilemma: Did Kafka receive the event? Or did the event disappear? There's no way to know.

The safest option is to retry. But what if Kafka had already stored the first event? Now you've published the same business event twice.

**The challenge isn't retrying. The challenge is ensuring retries don't trigger duplicate business actions.**

## The Question

**Aadvik:** Imagine our Order Service publishes an event whenever an order is placed. During publishing, the network fails before the producer receives Kafka's acknowledgment. The producer doesn't know whether the event reached Kafka. So it retries. How would you prevent duplicate processing?

**Akhilesh:** Before discussing solutions, I'd like to clarify something. **The duplicate isn't created because Kafka is unreliable. The duplicate is created because the producer loses certainty.** From the producer's perspective, two possibilities exist: Kafka never received the event, or Kafka received it but the acknowledgment was lost. Since the producer can't distinguish between those two cases, retrying is the only safe option.

**Aadvik:** So retries are unavoidable?

**Akhilesh:** Absolutely. Distributed systems are built around retries. The real question isn't "How do we stop retries?" It's "How do we make retries harmless?"

## The Failure Scenario

![](https://miro.medium.com/v2/resize:fit:1324/format:webp/1*VyKuHWOMINIlnlv7QocyeA.png)

Now Kafka may contain:

```text
OrderCreated
OrderCreated
```

Even though only one order was placed.

**Aadvik:** Isn't that Kafka's problem?

**Akhilesh:** No. Kafka guarantees durability. It doesn't know whether the producer received the acknowledgment. That's outside Kafka's control.

## The Naive Consumer

Suppose the consumer simply processes every message it receives. Imagine both events are identical. The consumer executes:

```text
reduceInventory(orderId);
```

twice. Inventory decreases twice. The customer ordered one phone. Inventory lost two.

## Solution 1: Event IDs

Every event should carry a globally unique **Event ID** (e.g., `EVT-8A72F1`). The ID remains unchanged across retries. Even if the producer publishes the event again, the Event ID stays the same.

**Why this is important**: Retries should represent the same business event, not a new one. Think of it exactly like an idempotency key in payment systems.

## Solution 2: Idempotent Consumer

Before processing an event:

```sql
SELECT *
FROM processed_events
WHERE event_id = 'EVT-8A72F1';
```

- If no record exists: Process the event and store the Event ID.
- If the record already exists: Ignore it.

## The Interview Trap: Race Conditions

Consider this naive check-then-act code:

```java
if (!alreadyProcessed(eventId)) {
    processEvent();
    markProcessed(eventId);
}
```

This has a race condition. Imagine two consumers receive duplicate events almost simultaneously:

- Consumer A checks: `alreadyProcessed = false`
- Before A stores anything, Consumer B checks: `alreadyProcessed = false`
- Both execute business logic. Inventory decreases twice.

## Solution 3: Atomic Deduplication

The insert itself must be atomic:

```sql
INSERT INTO processed_events (event_id)
VALUES ('EVT-8A72F1');
```

With a `UNIQUE(event_id)` constraint. Only one consumer succeeds. Everyone else immediately knows the event was already processed.

## Another Failure Scenario: Crash Between Business Update and Dedup

Suppose the consumer updates inventory successfully, then crashes before storing the Event ID. Kafka redelivers the event. The consumer believes it's seeing it for the first time. Inventory decreases again.

**Fix**: The business update and deduplication record should be part of the **same database transaction**. Either everything commits, or nothing commits.

## Kafka's Idempotent Producer vs. Consumer Idempotency

**Aadvik:** Kafka has idempotent producers. Doesn't that solve duplicates?

**Akhilesh:** It solves a different problem. An idempotent producer prevents duplicate records caused by retries between a producer and a Kafka broker. It does **not** prevent duplicate business processing.

- **Producer idempotency** protects Kafka (no duplicate records in the log).
- **Consumer idempotency** protects the business (no duplicate side-effects).

Those are two different problems.

## Kafka Transactions Don't Solve This Either

Kafka transactions help coordinate reading from Kafka and producing to Kafka atomically. But they don't make your database updates exactly-once. If your consumer updates MySQL, Kafka has no visibility into that. You still need idempotent business logic.

## The Transactional Outbox Pattern

What if the Order Service saves the order to the database successfully, but Kafka publishing fails? The order exists, but no downstream service ever learns about it. **That's why many production systems use the Transactional Outbox Pattern.**

The order and the event are committed together in the same database transaction. A background publisher reliably pushes events to Kafka.

## Scaling Considerations

When consumers scale to 50 instances:
- The deduplication store must be **shared** across all consumers.
- A local in-memory cache won't work — every consumer needs the same view of processed events.

## Deduplication Store Retention

The deduplication table shouldn't grow forever. Options include:
- Time-based cleanup
- TTL in Redis
- Partitioned database tables
- Archive old Event IDs

The retention period should exceed Kafka's maximum redelivery window.

## Exactly-Once Processing: The Reality

In practice, what we achieve is: **Messages may arrive multiple times, but business effects should occur only once.** That's what really matters.

## Design Summary

1. Accept that producer retries are unavoidable.
2. Assign a unique Event ID to every business event.
3. Make consumers idempotent.
4. Store processed Event IDs atomically (UNIQUE constraint).
5. Keep business updates and deduplication in the same transaction.
6. Use Kafka idempotent producers to reduce duplicate writes to Kafka.
7. Use the Transactional Outbox Pattern to avoid lost events.
8. Share the deduplication store across all consumers.
9. Design assuming every message can be delivered more than once.

**The challenge isn't publishing events reliably. The challenge is ensuring duplicate deliveries never become duplicate business operations.** That's the difference between a system that processes messages and a system that processes business events correctly.
