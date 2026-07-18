---
type: Article
title: "Duplicate Messages in WhatsApp — System Design Interview Deep Dive on At-Least-Once Delivery and Idempotency"
source: "https://medium.com/@codefarm0/duplicate-messages-in-whatsapp-system-design-interview-deep-dive-on-at-least-once-delivery-and-cecdc091fc57"
author: "Arvind Kumar"
published: 2026-07-14
created: 2026-07-18
description: "System design interview deep dive on at-least-once delivery semantics, idempotency, three-layer deduplication, and exactly-once processing in messaging platforms like WhatsApp."
tags:
  - messaging
  - idempotency
  - distributed-systems
  - system-design
  - at-least-once-delivery
  - exactly-once
  - whatsapp
---

# Duplicate Messages in WhatsApp — System Design Interview Deep Dive on At-Least-Once Delivery and Idempotency

> **Source**: [Medium — Arvind Kumar](https://medium.com/@codefarm0/duplicate-messages-in-whatsapp-system-design-interview-deep-dive-on-at-least-once-delivery-and-cecdc091fc57)
> **Related**: [Messaging — Key Takeaways](../../system-design-architecture/messaging/), [Reference Dictionary — Messaging](../../reference-dictionary/messaging.md)

This is one of those system design interview questions that seems trivial at first — until you realize it touches almost every fundamental concept in distributed systems reliability.

> \*\* WhatsApp name is used but things apply to any messaging system.

Interviewers love this question because it starts with a simple user complaint ("I received the same message twice") and gradually reveals whether you truly understand:

- At-least-once delivery and why messaging systems are built on it
- Idempotency and how it prevents duplicate processing across layers
- The unavoidable tension between reliability, latency, and consistency
- How real-world platforms like WhatsApp, Telegram, and Signal implement delivery guarantees

## The Scenario

**Arvind (Interviewer):**
Assume we're building a messaging platform similar to WhatsApp.
A sender sends a message. The receiver should get it exactly once.
Users start reporting they occasionally receive the same message twice.
How would you debug this?

**Rahul (Candidate):**
Before jumping to solutions, I want to map the basic message flow.
If I understand the happy path, the failure points become obvious.

This is the ideal flow.
The server stores the message, delivers it, and waits for an acknowledgment.
Once the ACK arrives, the message is marked as delivered.
Nobody sees anything twice.

**Arvind:**
So where does this break?

**Rahul:**
The problem is the ACK step.
In a distributed system, networks are unreliable.
What happens if the receiver's ACK is lost?

The server doesn't know whether the receiver got the message or not.
So it retries.
This is called at-least-once delivery.
The message is guaranteed to arrive — possibly more than once.

**Arvind:**
That explains the symptom.
But how do messaging platforms like WhatsApp handle this without users seeing duplicates?

**Rahul:**
The key is idempotency.
An operation is idempotent if performing it multiple times produces the same result as performing it once.

In WhatsApp, every message has a unique ID.
When the receiver gets a message, they check:
"Have I already processed this ID?"

The receiver maintains a set of recently processed message IDs.
If an incoming message ID already exists, it is silently discarded.
The user never sees the duplicate.

**Arvind:**
Interesting.
But does this deduplication happen only on the client side?
What if the user switches devices?

**Rahul:**
Great question.
Client-side deduplication alone is not enough.
The server also needs to be idempotent.

Imagine this:
The sender's phone sends the same message twice because the first request timed out.

If the server inserts the message without checking, you get two database entries.
That means the receiver will eventually get two messages — even with client-side dedup.

So the server must check:
"Is this message ID already in the database?"
If yes, it simply acknowledges without re-inserting.

**Arvind:**
Now you are talking about exactly-once semantics.
How do most real systems actually implement this?

**Rahul:**
There are three layers:

1. **Client-side deduplication** — Generate a unique message ID before sending. If the send times out, retry with the same ID.
2. **Server-side idempotency** — Store the message ID in a primary key or unique index. Duplicate inserts fail gracefully.
3. **Receiver-side dedup** — Maintain a short-lived cache of seen message IDs. Old entries expire to save memory.

This layered approach means even if one layer fails, another catches the duplicate.

**Arvind:**
What about the distributed retries problem?
If the server crashes after storing but before sending ACK, what happens?

**Rahul:**
That is the classic distributed systems triangle:
You can have exactly-once delivery, or high availability, or low latency — but not all three simultaneously.

The most practical approach real systems use:

- **Client retries with the same message ID** (idempotency key)
- **Server stores a delivery token or cursor** per client
- **Receiver deduplicates aggressively**

WhatsApp specifically uses a technique where:

- Each message has a server-issued ID
- The client tracks the last received ID per conversation
- Any message with an ID less than or equal to the last known ID is ignored

**Arvind:**
Let's zoom out.
If you had to design a reliable messaging system from scratch, what would your architecture look like?

**Rahul:**

Key decisions:

- **Database**: Message ID as primary key. Duplicate inserts are naturally rejected.
- **Delivery Queue**: At-least-once semantics with offset tracking.
- **Receiver Cache**: LRU cache with TTL. Old IDs expire after a few minutes.
- **Backoff**: Exponential backoff with jitter prevents retry storms.

**Arvind:**
One last question.
What monitoring would you put in place to detect duplicate deliveries before users complain?

**Rahul:**
I would track:

1. **Duplicate delivery rate** — Percentage of messages where the receiver's dedup cache hit.
2. **Retry rate per server node** — Sudden increase suggests a network partition.
3. **ACK timeout distribution** — P95/P99 of acknowledgment latency.
4. **Duplicate insert attempts on server** — How many times clients retried with an existing ID.
5. **Dedup cache hit ratio on receiver** — Ideally under 0.1%, but should be monitored.

If duplicate rate crosses a threshold, an alert fires.
Then I can investigate whether the retry logic, network, or dedup cache is misbehaving.

## Conclusion

The WhatsApp duplicate message problem is not about fixing a bug.
It is about accepting a fundamental truth of distributed systems:

> *Reliable delivery requires at-least-once semantics.
> At-least-once semantics produce duplicates.
> Idempotency and deduplication are how you have delivery guarantees without user-facing duplicates.*

The winning strategy is not eliminating retries — it is making retries harmless.

**Three-layer dedup**:

- **Client**: Retry with same message ID
- **Server**: Idempotent storage (unique message ID)
- **Receiver**: Local cache of processed IDs

That is the architecture behind every major messaging platform — whether it's WhatsApp, Telegram, or your own system.
