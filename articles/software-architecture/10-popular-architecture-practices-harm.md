---
type: Article
title: "10 Popular Architecture Practices That Do More Harm Than Good"
description: "Ten widely adopted architecture practices that cause hidden costs when applied at the wrong stage, and the timing heuristics for using them correctly."
generated: { by: process:format-agent, at: 2026-09-30T23:12:00+03:00 }
---

> **Source**: [10 Popular Architecture Practices That Do More Harm Than Good](https://medium.com/@vndpal/10-popular-architecture-practices-that-do-more-harm-than-good-8c1a278330e5) by Vinod Pal, published 2026-09-27
> **Key Takeaways**: [Architecture Anti-Patterns Takeaways](../../system-design-architecture/software-architecture/architecture-anti-patterns-takeaways.md) (`arch-`)

# 10 Popular Architecture Practices That Do More Harm Than Good

> *If you blindly follow any of them, your system might struggle later.*

Most architecture mistakes don't start with bad advice. They start with good advice, applied too early.

Add a cache. Put a queue between services. Design for millions of users. Hide your database behind an abstraction. Make everything configurable.

The same practices keep showing up in the systems that became painful to change. Each one solved a real problem. The trouble was, the problem hadn't arrived yet, but the cost had.

Your system probably has a few of them. Let's find out which.

## Contents

| Section | Practice |
|:---|:---|
| [§1](#1-designing-the-full-architecture-upfront) | Designing the Full Architecture Upfront |
| [§2](#2-designing-for-scale-from-day-one) | Designing for Scale From Day One |
| [§3](#3-making-the-system-configurable-for-future-needs) | Making the System Configurable for Future Needs |
| [§4](#4-hiding-vendors-behind-abstractions) | Hiding Vendors Behind Abstractions |
| [§5](#5-splitting-the-system-into-microservices-early) | Splitting the System into Microservices Early |
| [§6](#6-putting-a-queue-between-every-service) | Putting a Queue Between Every Service |
| [§7](#7-adding-a-cache-to-make-it-fast) | Adding a Cache to Make It Fast |
| [§8](#8-routing-every-request-through-an-api-gateway) | Routing Every Request Through an API Gateway |
| [§9](#9-keeping-one-central-service-as-the-source-of-truth) | Keeping One Central Service as the Source of Truth |
| [§10](#10-aiming-for-the-highest-availability-you-can-get) | Aiming for the Highest Availability You Can Get |
| [§11](#best-practices) | Best Practices — Decision Heuristics |

---

## 1. Designing the Full Architecture Upfront

A big design doc before any code feels natural. Every box and arrow in place before a single line of code. It feels like the responsible thing to do.

The issue is the timing. You make your biggest decisions on the day you know the least about your users.

Real traffic tends to reveal a problem the doc never planned for. By then, the team has spent months building around assumptions that no longer hold.

Worse, people start defending the doc instead of the product. Six months in, the diagram shows one system and production runs another. Nobody fixes the diagram, because that means admitting it was wrong.

**What works better**: Split decisions into two buckets, based on how painful they are to reverse:

- **Hard to reverse** (design upfront): data models, public APIs, regulated systems, external partner contracts
- **Easy to reverse** (pick and move on): frameworks, infra tooling, internal abstractions

Record each big decision in a short **Architecture Decision Record (ADR)**. Include the reason, so the next team knows what you knew at the time.

> **Rule**: Don't design everything upfront. Design the decisions that are expensive to undo.

---

## 2. Designing for Scale From Day One

Nobody wants to rewrite the system right when growth arrives. So teams launch with clusters, event streams, and autoscaling for a few hundred users.

You pay for that scale every day, long before you need it. New engineers spend weeks learning the infrastructure before they touch the product. Simple features take longer because every change crosses more moving parts.

The bigger issue is that your scaling guess is often wrong. It's hard to predict your bottleneck before real users arrive. So you end up scaling the wrong part of the system.

**Real-world example**: Amazon Prime Video's team built a stream monitoring tool from distributed serverless parts. It ran into scaling limits and high costs. They moved it into one process and cut infrastructure costs by over 90%.

**What works better**:

- Find the one number most likely to hurt you first (peak requests, data size, or write volume)
- Plan for the growth that number is already showing you
- Start the next migration step early — growth won't wait for it

> **Rule**: Don't scale for traffic you imagine. Scale for the bottleneck you can measure.

---

## 3. Making the System Configurable for Future Needs

Someone says, *"We might support other countries one day."* So the team adds settings for currency, language, and tax rules.

Each setting multiplies the paths through your system. Config changes often skip the review and testing that code changes get. One wrong value in production can break prices, emails, or payments. Unused paths also rot.

And when that second country finally shows up, its tax rules look nothing like the ones you guessed. So you rewrite the feature anyway — and you also have to rip out the old one.

**Real-world example**: In 2012, Knight Capital reused an old flag, and a single server missed the new code. That flag woke up dead code, and they lost about $440 million in 45 minutes.

**What works better**:

- Build configuration around a real second customer's real different need, not your guess
- Treat config like code: version it, validate it, and test the combinations you ship
- **Kill switches and feature flags** are the good case — levers you pull during an incident

> **Rule**: Every option you add is a promise to test it.

---

## 4. Hiding Vendors Behind Abstractions

Lock-in sounds scary. So teams wrap the database, the cloud storage, or the message broker in a generic layer *"in case we switch."*

The abstraction hides the features that made you choose that vendor. You use 20% of what the database can do, because the layer above can only express the common parts. You end up with two systems to maintain — the abstraction and the vendor.

The real cost surfaces when you hit a performance problem. The fix is a vendor-specific feature, but the abstraction doesn't expose it. So you either break the abstraction or live with the slow path.

**When abstraction is worth it**:

- You've actually run into lock-in pain before
- You're building a library that genuinely needs to support multiple backends
- The abstraction is owned, tested, and small in scope

> **Rule**: Defer abstraction until you have two real backends to abstract over.

---

## 5. Splitting the System into Microservices Early

Microservices can help large teams ship independently. They also add network calls, distributed tracing, separate deployments, and more failure points.

Every service boundary you draw is a contract. Contracts are harder to change than internal interfaces. The real coordination problem is organizational — multiple teams, each owning a service. Without the team structure to match, the services just add overhead.

**What works better**:

- Start with a modular monolith — clear internal boundaries without network complexity
- Extract services when you have an actual problem: a team that's blocked, a component that needs to scale independently, a different release cadence
- The test: if one team owns all services, microservices are probably hurting you

> **Rule**: Match your architecture to your team topology, not the other way around.

---

## 6. Putting a Queue Between Every Service

Async communication is resilient and decoupled in theory. But a queue is a component you have to operate and monitor. Silent queues hide failures: orders going through, payments succeeding, every dashboard green — but no items delivered.

**The dual-write problem**: Saving data and publishing an event are two separate writes. When one succeeds and the other fails, your data drifts apart.

The **outbox pattern** fixes this by saving the event in the same database transaction. A separate process publishes it later.

Most queues also deliver messages at least once. So every consumer must handle duplicates without side effects (idempotency).

**When queues shine**:

- Work the user doesn't wait on: emails, reports, background processing
- Absorbing traffic spikes
- Fanning one event out to many consumers

**Operating a queue correctly**:

- Alert on the **dead letter queue (DLQ)**
- Watch the **age of the oldest message**, not just the queue length
- Assign a clear owner

> **Rule**: Without alerts and a clear owner, a queue moves your failures somewhere quieter.

---

## 7. Adding a Cache to Make It Fast

A page is slow, management wants it fixed today. A cache drops response time from seconds to milliseconds. Everyone celebrates.

The cache often hides the real problem. A common one is an N+1 query pattern:

```sql
SELECT * FROM products WHERE category_id = 42;
-- then, once for each of 80 products:
SELECT * FROM prices WHERE product_id = ?;
```

Next come stale reads. A price changes, and users see the old value until the entry expires. Invalidation bugs turn into support tickets.

The biggest risk shows up later. Over time, the database gets sized for cached traffic. Then the cache restarts during peak hours. Every request hits the database at once — this is called a **thundering herd**. Your system can no longer survive without the cache.

**Real-world example**: In 2010, a bad config value made Facebook's servers throw away cached data and go straight to the database — all of them, at the same time. Facebook was down for about two and a half hours.

**What works better**:

1. Fix the slow query first
2. Then cache read-heavy data that can tolerate a little staleness
3. Set expiry time from business impact: *"How long can a price be wrong before it hurts the business?"*
4. Use **request coalescing**: let one request refill a missing key while the others wait

> **Rule**: Cache is not a replacement for fixing bad code. It can only buy you time to fix it.

---

## 8. Routing Every Request Through an API Gateway

One entry point for every client sounds clean. Auth, rate limits, and routing all live in one place.

The trouble is that the gateway becomes the easiest place to add logic. Soon it's a second backend owned by one team, and every other team waits in its queue to ship. The blast radius also grows — one bad gateway deploy takes down every client at once.

**What works better**:

- Keep the gateway for **cross-cutting concerns**: auth, rate limits, and routing
- When a client needs custom responses, use the **Backend for Frontend (BFF) pattern** — a small backend owned by the client team, allowing them to ship without waiting on anyone else

> **Rule**: Let the gateway guard the door. Let each team own what's behind it.

---

## 9. Keeping One Central Service as the Source of Truth

Data drifts when every service keeps its own copy. So the team creates one central service that owns it, and everyone calls it live.

The problem is ownership turning into a **runtime dependency**. Other services can read the data only while the owner is up and fast. During peak traffic, the central service slows down, and every dependent flow slows with it.

This is called **temporal coupling** — the correctness of one service's work depends on another service being available at that exact moment.

**One common fix — separate writes from reads**:

- The central service owns every write
- Other services keep a local copy, updated through events
- Local copies can serve reads even when the owner is slow

**Tradeoffs**:

- Local copies can be slightly out of date
- Events may arrive late, duplicated, or out of order
- Copies can drift; you'll need a rebuild mechanism

**When live calls are still right**:

- Data that must be exact at the moment of use (e.g., account balance before a payment)
- Most reference data can tolerate being a few seconds old

> **Rule**: Own data in one place. Don't make every request wait on the owner.

---

## 10. Aiming for the Highest Availability You Can Get

A big client wants 99.99% uptime. Sales says yes before engineering hears about it.

Look at what each extra nine actually buys:

```text
99.9%   → about 8.8 hours of downtime per year
99.99%  → about 52 minutes of downtime per year
```

Each nine costs far more than the last. Multi-region setups add new failure modes: failover bugs and data conflicts.

The bigger constraint: **your system can't be more available than the hard dependencies in its request path**. If your payment provider promises 99.95%, a second region alone won't get you to 99.99%.

**When high availability is worth the cost**:

- Downtime has a direct and large cost (payments, healthcare)
- Many products do well at 99.9% with a warm standby

**How to set the right target**:

1. Define what an outage costs the business
2. Identify dependencies with their own SLA ceilings
3. Agree on an **error budget**, and pause features when you use it up

> **Rule**: Chase the nines your users need, not the ones that sound impressive.

---

## Best Practices

Every practice above solves a real problem. The harm comes when a team adopts it before that problem exists.

Decision heuristics for distinguishing premature vs. timely adoption:

| Heuristic | How to Apply |
|:---|:---|
| **Name the pain first** | If you can't point to a current problem, you're paying for a guess. Write the problem down before you write the design. |
| **Sort by reversibility** | Spend your design time on data models and public APIs. Move fast on anything you can undo in a week. |
| **Measure before you optimize** | Find the slow query, the hot endpoint, or the real load pattern. Then pick the tool. |
| **Count the cost to operate** | Every new moving part needs monitoring and alerts — and someone who understands it during outages. |
| **Plan the exit** | Write down when you would remove a component. It keeps old choices from becoming permanent by default. |

Good architecture is mostly about timing. The right practice at the wrong stage can cost more than no practice at all.

> Next time someone says, *"Why don't you add a cache?"* — ask one thing: *what problem does it fix today?*