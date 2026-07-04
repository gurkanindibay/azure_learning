---
type: Article
title: "Payment Events and Duplicate Processing"
source: "https://codefarm0.medium.com/payment-events-and-duplicate-processing-166e33ee9268"
author: "Arvind Kumar"
published: 2026-01-24
created: 2026-07-04
description: "A Real Interview Deep Dive into Idempotency, Retries, and Distributed Correctness"
---

# Payment Events and Duplicate Processing

> **Source**: [Medium — codefarm0](https://codefarm0.medium.com/payment-events-and-duplicate-processing-166e33ee9268)
> **Author**: Arvind Kumar
> **Published**: 2026-01-24

## Introduction

Payment systems are unforgiving.

If a notification is sent twice, users get annoyed.  
If a payment is processed twice, users lose money.

That’s why this scenario discussion is very important. It tests whether you understand a brutal truth of distributed systems:

**Retries are guaranteed. Duplicates are inevitable. Correctness is your responsibility.**

## Interview Conversation

**Interviewer (Jai):**  
You’re working on a payment system. Producers retry on failures. Consumers run in parallel. How do you ensure a payment is never processed twice?

**Candidate (Sara):**  
I don’t try to prevent duplicate delivery. I design the system so duplicate processing is harmless.

**Jai:**  
Why assume duplicates at all?

**Sara:**  
Because failures happen between every boundary.

A producer can send a payment event, crash before receiving an acknowledgment, retry, and Kafka now has two identical events. Kafka is doing the right thing. From the system’s perspective, both events are valid.

So correctness cannot depend on delivery guarantees alone.

**Jai:**  
Okay. Walk me through your mental model.

**Sara:**  
I break the system into three responsibilities:

- event delivery
- business correctness
- external side effects

Kafka helps with the first. Java code and databases enforce the second. External systems must be protected from the third.

**Jai:**  
Show me.

**Sara:**  
At a high level, this is what we’re dealing with.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*aEEtvgU6seCzk45zhaQZqQ.png)

Parallel consumers are good for throughput, but they make duplicates unavoidable.

**Jai:**  
Why not rely on Kafka exactly-once semantics?

**Sara:**  
Because payments don’t end inside Kafka.

Exactly-once guarantees stop at Kafka boundaries. The moment I touch a database, a payment gateway, or an external ledger, Kafka can’t roll anything back.

Exactly-once messaging doesn’t mean exactly-once business effects.

**Jai:**  
So where do you enforce correctness?

**Sara:**  
At the business boundary. Every payment has a globally unique paymentId, and the system treats that ID as immutable truth.

If the same paymentId appears twice, processing it twice must lead to the same final state.

**Jai:**  
How do you enforce that in practice?

**Sara:**  
The database becomes the guardrail.

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*KPljIyS8yl66OuAoFG_sbw.png)

If the insert succeeds, this is the first time we’ve seen the payment.  
If it fails, we already processed it and stop immediately.

No locks. No coordination between consumers. Just deterministic behavior.

**Jai:**  
What about offset commits? Can’t careful offset handling solve this?

**Sara:**  
Offsets track progress, not correctness.

If I commit offsets before writing to the DB, I risk losing payments.  
If I write to the DB before committing offsets, duplicates can happen.

Either way, offsets alone can’t guarantee safety. That’s why idempotency lives outside Kafka.

**Jai:**  
How does this play out in Java code?

**Sara:**  
The consumer logic is simple and strict.

- Deserialize event
- Try to persist paymentId
- If it already exists, exit
- If not, proceed with business logic

The consumer never asks Kafka whether it has seen the event before. Kafka doesn’t know business truth. The database does.

**Jai:**  
What about calling the payment gateway? That’s an external side effect.

**Sara:**  
Exactly. That’s where many systems break.

Charging the user and marking the payment as completed must be two separate, idempotent steps.

If the gateway is called twice with the same paymentId, it must either reject duplicates or behave idempotently itself. If it doesn’t, we wrap it with our own deduplication layer.

**Jai:**  
So payment processing becomes a state machine?

**Sara:**  
Yes. Always.

![](https://miro.medium.com/v2/resize:fit:1210/format:webp/1*4GJTEZExkRwQo8rOm3RZpA.png)

Each transition is safe to retry.  
Each state change is persisted.  
Replay just re-drives the same transitions.

**Jai:**  
Doesn’t all this checking hurt throughput?

**Sara:**  
Only if designed poorly.

A single indexed insert or lookup is cheap. What kills throughput is coordination, locks, and synchronous dependencies.

Idempotency scales well because it removes coordination between consumers.

**Jai:**  
What’s the most common mistake teams make here?

**Sara:**  
They confuse message delivery with business execution.

They say, “Kafka will deliver it once,” instead of asking, “What happens if it doesn’t?”

**Jai:**  
Final question. One sentence philosophy?

**Sara:**  
In payment systems, retries are normal. Duplicates are expected. Correctness is non-negotiable.

## Key Concepts Covered

- Why duplicate events are unavoidable in distributed payment systems
- Separation of delivery guarantees and business correctness
- Idempotency using unique business identifiers
- Why offset management alone is insufficient
- Safe parallel consumption without coordination
- Designing payment state machines that tolerate replay
- Kafka as an enabler, not the source of correctness
