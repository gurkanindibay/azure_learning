---
type: Article
title: "Designing a User Activity Tracking System at Massive Scale"
source: "https://codefarm0.medium.com/designing-a-user-activity-tracking-system-at-massive-scale-af856b6c4393"
author:
  - "Arvind Kumar"
published: 2026-01-19
created: 2026-06-28
description: "How Kafka Becomes the Right Choice — A Real Interview Deep Dive"
domain: messaging
tags:
  - "kafka"
  - "system-design"
  - "event-driven"
  - "consumer-lag"
  - "stream-processing"
---

# Designing a User Activity Tracking System at Massive Scale

> **Source**: [Medium / codefarm0](https://codefarm0.medium.com/designing-a-user-activity-tracking-system-at-massive-scale-af856b6c4393)

## How Kafka Becomes the Right Choice — A Real Interview Deep Dive

Strong system design interviews don’t start with tools.  
They start with **constraints**.

When candidates jump straight to Kafka, databases, or queues, experienced interviewers usually stop them — not because the tool is wrong, but because the *reasoning* is missing.

This deep dive walks through a realistic interview conversation where Kafka **emerges naturally** as the solution to a user activity tracking problem — exactly how it happens in real interviews and real systems.

> **Source**: [Medium / codefarm0](https://codefarm0.medium.com/designing-a-user-activity-tracking-system-at-massive-scale-af856b6c4393)

> Parent story to see more such questions overview — [10 Real-World Kafka Scenarios Interviewers Love to Ask](https://medium.com/@codefarm0/10-real-world-kafka-scenarios-interviewers-love-to-ask-21d5f19fc1d8)

## What the Interviewer Is Evaluating

This question isn’t about Kafka knowledge.

It evaluates whether the candidate:

- starts from **requirements, not tools**
- understands failure as a normal state
- designs for reuse and replay
- avoids premature optimization
- knows why Kafka fits — not just how to use it

## Interview Conversation

**Interviewer (Jai):**  
“Imagine you’re asked to build a user activity tracking system. Clicks, views, scrolls — everything. Traffic spikes heavily during campaigns. How would you approach this?”

**Candidate (Sara):**  
“I’d first understand how this data is used before choosing any technology.”

**Jai:**  
“Fair. What do you want to know?”

**Sara:**

- Is this data used only for analytics, or also for real-time decisions?
- How critical is ordering?
- Is data loss acceptable?
- Who are the consumers — one team or many over time?

**Jai:**  
“Analytics today, possibly real-time use later. Ordering matters per user. Data loss is not acceptable. Multiple teams will consume it.”

**Sara:**  
“That already rules out a simple log-based or in-memory solution.”

“We need something that can handle bursty traffic, persist data durably, allow multiple independent consumers, and support replay.”

**Jai:**  
“So what kind of system fits that?”

**Sara:**  
“A distributed append-only event log fits best here.”

**Jai:**  
“Go on.”

**Sara:**  
“At this point, a system like Kafka makes sense — not because it’s popular, but because it matches the constraints.”

She explains:

- it decouples producers from consumers
- it handles high-throughput ingestion
- it retains data for reprocessing
- it supports consumer groups without duplication

**Jai:**  
“Okay, assume Kafka. How do you think about ingestion?”

**Sara:**  
“These producers live inside user-facing services, so my first priority is not slowing down user flows.”

- asynchronous publishing
- bounded retries
- short timeouts
- observability instead of blocking

“If Kafka slows down, we degrade analytics — not checkout or navigation.”

**Jai:**  
“And traffic spikes?”

**Sara:**  
“Spikes are expected. Kafka absorbs them, but producers still need batching and compression to avoid CPU and network saturation.”

**Jai:**  
“How do you structure the events?”

**Sara:**  
“As immutable facts.”

She explains:

- minimal but expressive schemas
- no downstream assumptions
- versioned carefully

“These events will outlive the service that created them.”

**Jai:**  
“What about ordering?”

**Sara:**  
“Ordering is scoped per user. That informs partitioning strategy, but I wouldn’t prematurely optimize partition count.”

**Jai:**  
“Let’s talk consumers.”

**Sara:**  
“I assume consumers will always be slower than producers.”

- consumer lag is expected
- replay must be safe
- processing must be idempotent

“A system that can’t replay safely isn’t production-ready.”

**Jai:**  
“Multiple teams consume the data later. Any risks?”

**Sara:**  
“Yes — treating events like internal DTOs.”

- schemas are contracts
- backward compatibility is enforced
- breaking changes are treated as migrations

“Kafka topics become public APIs whether you want them to or not.”

**Jai:**  
“Let’s talk about consumers. Say one of the analytics consumers starts lagging behind. How worried are you?”

**Sara:**  
“Lag by itself doesn’t worry me. Unbounded lag does.”

She explains calmly:

“In Kafka-based systems, lag is a normal operating condition. Producers and consumers are intentionally decoupled, so I expect consumers to fall behind during spikes.”

**Jai:**  
“So when does it become a problem?”

**Sara:**  
“When lag keeps growing even after traffic normalizes, or when it starts impacting downstream SLAs.”

“That’s usually a signal that something else is wrong — not Kafka.”

**Jai:**  
“Like what?”

**Sara:**  
“Most often:

- inefficient consumer processing logic,
- external system slowness,
- or a bad deployment that reduced consumer throughput.”

“Adding more consumers blindly can actually make things worse because of rebalances.”

**Jai:**  
“How do you design consumers with this in mind?”

**Sara:**  
“I design them assuming they *will* crash, restart, and replay data.”

- offsets are committed only after successful processing
- processing logic is idempotent
- side effects are guarded

“If replaying data causes corruption or duplication, the system isn’t safe.”

**Jai:**  
“What does replay mean in practice here?”

**Sara:**  
“It means I can reset offsets intentionally — for bugs, schema changes, or new logic — and reprocess historical data without fear.”

She pauses.

“Replay isn’t an edge case. It’s a core feature we design for.”

**Jai:**  
“Do all consumers need the same guarantees?”

**Sara:**  
“No.”

She explains:

“Analytics consumers can tolerate delay and reprocessing. Real-time consumers might need tighter bounds. Each consumer group defines its own trade-offs.”

“That’s the benefit of Kafka’s model — one event stream, multiple independent consumption semantics.”

**Jai:**  
“What’s the biggest mistake teams make with lag?”

**Sara:**  
“They treat zero lag as success.”

“A healthy system has controlled lag. Chasing zero lag usually leads to over-scaling, unstable consumer groups, and fragile deployments.”

## Closing Thought

Consumer lag and replay aren’t failure modes — they’re **design features**.

Kafka works well in production not because it avoids failure,  
but because it **makes failure survivable**.

In this scenario, the real signal of experience is not how fast a consumer processes events,  
but how confidently the system can fall behind — and recover.

***

## Further Reading

- [10 Real-World Kafka Scenarios Interviewers Love to Ask](https://codefarm0.medium.com/10-real-world-kafka-scenarios-interviewers-love-to-ask-21d5f19fc1d8)
- [Apache Kafka | Kafka Deep Dive | Kafka Interview Questions — Curated List](https://medium.com/@codefarm0/list/apache-kafka-kafka-deep-dive-kafka-interview-questions-1baa0804c957)