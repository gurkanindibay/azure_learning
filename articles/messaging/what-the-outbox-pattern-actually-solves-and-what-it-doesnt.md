---
type: Article
title: "What the Outbox Pattern Actually Solves — and What It Doesn’t"
source: "https://codefarm0.medium.com/what-the-outbox-pattern-actually-solves-and-what-it-doesnt-450f23f85115"
author:
  - "Arvind Kumar"
published: 2026-09-16
created: 2026-09-17
description: "A deep dive on what the Transactional Outbox pattern actually solves (dual-write atomicity) and what it does not (consumer idempotency, cross-partition ordering, downstream consistency), contrasting polling relays with CDC."
tags:
  - "event-driven-architecture"
  - "kafka"
  - "outbox-pattern"
  - "system-design"
  - "messaging"
  - "cqrs"
---

# What the Outbox Pattern Actually Solves — and What It Doesn’t

> **Series**: Part of the [10 Event-Driven Architecture Questions](10-event-driven-architecture-questions.md) series (Deep Dive on Question 5: *What does the Outbox Pattern solve — and what does it not solve?*)  
> **Author**: Arvind Kumar  
> **Source**: [Codefarm Medium](https://codefarm0.medium.com/what-the-outbox-pattern-actually-solves-and-what-it-doesnt-450f23f85115)

The Outbox Pattern gets memorized as "the fix for dual writes," and that’s correct as far as it goes — it just doesn’t go very far. Teams that stop there tend to ship an outbox table, call the reliability problem solved, and then get surprised by duplicate emails or out-of-order state changes that the pattern was never designed to prevent.

![Outbox Pattern Overview: What it solves vs what it does not](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8vsYt5NNe2aSw2Gq4ysnmA.png)

---

## The Setup

*PR review. Kavya added an outbox table to fix a bug where an order would commit to the database but the corresponding event never reached Kafka.*

**Arvind:** Describe the bug this is fixing, in one sentence.

**Kavya:** We commit the order to the database, then call the Kafka producer as a second step — and if the process crashes or the publish call fails in between, the database says the order exists but no one downstream ever hears about it.

**Arvind:** That’s the dual-write problem — two systems, no shared transaction, and a real gap between them. Show me how the outbox closes it.

---

## The Problem, Before the Fix

![The Dual-Write Problem: Write to DB followed by independent publish call](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9xoe0Rqa724u3VDX2Etoqg.png)

**Kavya:** The outbox fix is to write the event into a table in the *same* database transaction as the order itself. If the transaction commits, both the order and the event-to-be-published exist together. If it rolls back, neither does.

![Transactional Outbox: Atomic write of business data and outbox row](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*fArd98P8EotPBt7bNuERjQ.png)

**Arvind:** So the atomicity problem is solved at the write, not at the publish.

**Kavya:** Right — the relay publishing afterward can fail and retry as many times as it needs to, because the event’s existence no longer depends on that publish call succeeding on the first try.

---

## What’s Actually in That Table

![Outbox Table Schema and Relay Architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*wl5Fm6hyAtSoOLSSPyG8CA.png)

```c
FUNCTION createOrder(orderData):
    BEGIN TRANSACTION
        order = insertOrder(orderData)
        insertOutboxRow(aggregateId: order.id, type: "OrderCreated", payload: order)
    COMMIT

FUNCTION relayLoop():
    LOOP:
        rows = fetchUnpublished(orderBy: created_at, limit: batchSize)
        FOR row IN rows:
            publish(row.event_type, row.payload)
            markPublished(row.id)     // if this crashes before marking, retry - see below
```

---

## Now the Part the PR Missed

**Arvind:** Walk me through what happens if the relay publishes successfully, then crashes before it marks the row as published.

**Kavya:** …it retries, sees the row still marked unpublished, and publishes it again. So the outbox gives at-least-once delivery, not exactly-once.

**Arvind:** Which means?

**Kavya:** Which means the consumer still needs to be idempotent. The outbox guarantees the event *will* be published eventually — it says nothing about a consumer only seeing it once. That’s the dedup pattern from the duplicates question, not something the outbox replaces.

**Arvind:** What about ordering? Your relay polls with `ORDER BY created_at` - does that guarantee order downstream?

**Kavya:** Only if the broker preserves that order too — which means the events need to land on the same partition, keyed by `aggregate_id`, same as any other ordering guarantee we rely on. And even then, that's delivery order, not business-correctness order - a consumer still needs the version check from the consistency question to be safe against redelivery or a slow consumer falling behind.

**Arvind:** So what has the outbox actually bought us, versus what’s still on us?

**Kavya:** It closes the specific gap between "the database committed" and "an event exists to be published." It does not give us exactly-once delivery, it does not give us cross-service ordering by itself, and it does nothing for downstream consistency once the event leaves the relay — that’s still the consumer’s job, and if the flow spans multiple services, it’s still a saga’s job, not the outbox’s.

---

## Solved vs. Still Your Problem

![Comparison: Solved by Outbox vs Still Your Problem](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*VhS1SdBm4A9k4px2nNAI1w.png)

---

## Implementation Choices

**Arvind:** Polling relay, like this PR, versus CDC — when would you reach for the other one?

**Kavya:** A polling relay is simple to reason about but adds load to the database and has a latency floor set by the poll interval. Change data capture — something like Debezium reading the database’s write-ahead log directly — publishes near-instantly and doesn’t hammer the table with polling queries, but it’s more infrastructure to run and operate.

**Arvind:** Either way, what happens to old rows in the outbox table?

**Kavya:** They need to be archived or deleted once published, on a schedule — otherwise the table grows unbounded and the poller’s query gets slower over time, which is an easy thing to miss until it’s already a performance problem.

---

## The Answer, Compressed

**Kavya:** The outbox pattern solves exactly one thing: making the database write and "this event will eventually be published" atomic, so a crash between them can’t lose the event or leave the database out of sync with the world. It doesn’t give exactly-once delivery, doesn’t give ordering beyond what the broker and partition key already provide, and doesn’t touch downstream consistency at all — idempotent consumers, version checks, and sagas are still separate work that has to happen regardless of whether an outbox is in front of them.

---

## Conclusion

The outbox pattern earns its place in almost every service that writes to a database and publishes events — the dual-write bug it fixes is real and easy to hit by accident. The risk is treating it as a complete reliability story instead of one piece of it: it hands off an at-least-once, DB-consistent event stream, and everything downstream — idempotency, ordering, cross-service consistency — is exactly the set of problems the rest of this series already covers.