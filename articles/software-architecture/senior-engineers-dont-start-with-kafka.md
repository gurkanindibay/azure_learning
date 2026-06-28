---
type: Article
title: "Senior Engineers Don't Start With Kafka (They Start With This)"
source: "https://cloudwithazeem.medium.com/senior-engineers-dont-start-with-kafka-they-start-with-this-69d61f0f3152"
author: "Cloud With Azeem"
published: 2026-06-25
created: 2026-06-28
description: "How senior engineers approach system design by starting with requirements and tradeoffs rather than jumping to technology choices like Kafka."
tags:
  - architecture
  - system-design
  - kafka
  - caching
  - resilience
---

# Senior Engineers Don't Start With Kafka (They Start With This)

After studying national-scale systems, I realized most candidates optimize the wrong layer.

![Senior Engineers Don't Start With Kafka (They Start With This)](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*X_j6tiU-8iDSkIaX)

A few months ago, I was reviewing system design questions that frequently appear in Google L5 and senior data engineering interviews.

One question kept showing up:

> "How would you design a data pipeline for a national event?"

1. Sometimes it's an election.
2. Sometimes it's a sporting tournament.
3. Sometimes it's a census or a nationwide logistics operation.

The scenario changes, but the underlying problem stays the same:

**How do you process moderate writes, survive enormous reads, and never lose data?**

What surprised me wasn't the architecture itself. It was how most candidates approached the problem. Almost everyone immediately started talking about **Kafka**, **Flink**, and **Cassandra**. And after studying real production systems, I realized something interesting:

**Senior engineers don't start with Kafka. They start with requirements.**

Ironically, naming technologies too early is often the fastest way to design the wrong system.

## The Biggest Mistake

When I first started learning system design, I made the same mistake. Someone would say:

> "Design an election data pipeline."

And I'd instantly think:

- Kafka for ingestion.
- Flink for processing.
- Cassandra for storage.
- Redis for caching.

Done.

Except that's backwards. Tools are answers. You haven't even understood the question yet. Before touching a single technology, I learned to ask:

- What is the throughput?
- What latency do users expect?
- How many readers are there?
- Is consistency important?
- Can we tolerate data loss?
- Is traffic uniform or bursty?

These questions matter far more than the database you eventually choose. Because architecture is really about **constraints**, not tools.

## The Write Side Is Usually Easy

People hear "national-scale" and imagine billions of events per second. In reality, many national events produce surprisingly manageable write traffic.

Take an election.

Even with hundreds of millions of voters, updates don't arrive continuously. Operators enter them in rounds. Maybe tens of thousands of updates arrive per hour.

That's not difficult.

Modern databases can handle that effortlessly. The real challenge comes later.

## The Read Side Is Where Systems Die

After studying several large-scale architectures, I noticed something interesting. The write side rarely kills systems.

**Readers do.**

Imagine 100 million people checking results simultaneously. Most users don't want complex analytics. They just want answers:

- Who's leading?
- Which candidate won?
- What's happening in my constituency?

If every request hits your database directly, you're finished. Your database becomes the victim of curiosity. And people are incredibly curious during national events.

Nothing generates traffic quite like millions of anxious people refreshing their browser every five seconds.

## Separation of Read and Write Paths Changes Everything

This was probably the most important lesson I learned. Senior engineers rarely force one database to do everything.

Instead, they separate concerns.

### Write Path

The write path focuses on:

- **Durability**
- **Consistency**
- **Ordering**
- **Data correctness**

### Read Path

The read path focuses on:

- **Low latency**
- **Massive throughput**
- **Fast responses**

These are completely different problems. Trying to solve both with a single system is like asking one employee to simultaneously be:

- A cashier
- A chef
- A delivery driver
- And customer support

Eventually, everybody suffers.

## Idempotency Matters More Than Fancy Architecture

One thing I used to underestimate was duplicate events. In theory, every update should arrive once.

In reality?

- Networks fail.
- Connections drop.
- Humans click submit twice.
- Retries happen.

Without protection, the same event may be processed multiple times.

And suddenly:

50,000 votes become 100,000 votes.

That's not a bug. That's a national crisis, which is why I learned that **idempotency** is one of the most underrated concepts in distributed systems.

Every event needs a unique identity. If the same message arrives again, the system should recognize it and safely ignore duplicates.

Simple.

Boring.

Absolutely critical.

## Kafka Isn't the Star of the Show

I like Kafka. But after studying streaming systems, I realized engineers sometimes worship it a little too much. Kafka isn't solving your business problem. It's solving one specific problem:

**Decoupling producers from consumers.**

That's it.

- It absorbs bursts.
- Provides durability.
- Allows replay.

And keeps producers independent from downstream processing.

But Kafka itself doesn't generate insights. Your business logic does. Treating Kafka as the hero is like treating the highway as more important than the destination.

## Why I Prefer Flink for Stateful Systems

For continuously changing results, I would probably choose **Apache Flink**.

Not because it's trendy.

Because state matters.

Imagine keeping track of:

- Candidate totals
- Constituency leaders
- National aggregates
- Winner detection
- Duplicate prevention

These aren't isolated events. They're evolving states. Flink excels at maintaining state over time. But here's something many articles won't tell you:

**Sometimes Flink is overkill.**

If requirements are simple, a few Kafka consumers and PostgreSQL might be enough.

> I've learned that senior engineers don't get rewarded for complexity. They get rewarded for solving problems efficiently.

## Caching Is More Important Than Databases

This was one of my biggest "aha" moments. Suppose 100 million users request:

> "Who's leading nationally?"

Why compute that answer 100 million times?

- Compute it once.
- Cache it.
- Serve everyone.

That's exactly what systems like **Redis** do. And for static summaries? A CDN can serve data faster than your application servers ever could.

Many engineers spend hours debating databases. Meanwhile, the real scalability hero is quietly sitting in front:

**Caching.**

## Design for Failure, Not Success

Happy paths are easy.

Real systems fail.

And after studying production outages, I realized the question isn't:

> "Will something break?"

It's:

> "When something breaks, what happens next?"

What if:

- Kafka goes down?
- Consumers fall behind?
- Networks become unstable?
- A region loses connectivity?
- Operators accidentally resubmit results?

Distributed systems are really recovery systems. Anybody can design for success. Senior engineers design for failure.

## The Lesson

When I first learned system design, I thought the smartest engineers knew every tool.

Now I think differently.

The best engineers I've studied don't begin with technologies.

They begin with tradeoffs.

They ask:

- What are we optimizing?
- What can fail?
- What matters most?
- Where will traffic come from?
- Which complexity can we avoid?

Because architecture isn't about assembling cool components. It's about making good decisions under constraints.

And surprisingly, the answer isn't always Kafka.

## Related Topics

- [Caching Patterns](../../system-design-architecture/caching/)
- [Resilience Patterns](../../system-design-architecture/resilience/)
- [Message Brokers & Kafka](../../system-design-architecture/messaging/)
- [Architecture Principles](architecture-principles.md)

> **Azure Services**: [Event Hubs](../../architecture-azure/integration/event-hubs/), [Redis Cache](../../architecture-azure/data/redis/), [Azure CDN](../../architecture-azure/networking/cdn/)
> **Taxonomy**: §2.2 Application Software Architecture, §3.3 Event-Driven & Messaging
