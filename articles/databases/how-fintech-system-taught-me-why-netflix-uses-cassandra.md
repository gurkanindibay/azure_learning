---
type: Article
title: "How a Fintech System Taught Me Why Netflix Uses Cassandra"
description: "A first-hand account of MongoDB primary node failure in a fintech loan system, and the architectural lessons that explain why Netflix chose Cassandra's masterless design over document databases."
timestamp: 2026-06-28T00:00:00Z
source: "https://medium.com/@himanshusingour7/how-fintech-systemtaught-me-why-netflix-uses-cassandra-e4752e74d8c3"
author: "Himanshu Singour"
published: 2026-02-05
tags:
  - databases
  - cassandra
  - mongodb
  - system-design
  - fintech
---

# How a Fintech System Taught Me Why Netflix Uses Cassandra

> Something I Understood Only After Breaking a Fintech Loan System

For a long time, I thought database choices were mostly about features.

> Which one is faster.
>
> Which one is more popular.
>
> Which one developers like more.

I understood why Netflix uses Apache Cassandra instead of MongoDB only after working on a real system where things actually broke.

Not in theory.
In production.
With real users.

## The Fintech System I Was Working On

I was part of a team building a loan management system.

Users could apply for loans, see EMI schedules, make repayments, and track their loan status in real time.

Behind the scenes, payment gateways were constantly hitting our system with webhooks whenever a payment happened.

Most of the time, users were just opening the app and checking things like:

- Is my loan active?
- Did my EMI go through?
- Am I overdue?

Simple questions. But the system was busy all the time.

## Why We Chose MongoDB in the Beginning

We chose MongoDB very naturally. There was no long debate.

Loan data fit nicely into documents.

One document per loan. User details inside it. EMI schedule inside it. Repayment history inside it. It felt clean.

Schema flexibility helped a lot.

Business requirements kept changing. New fields were added. Old ones were modified. MongoDB made this easy.

We used a standard setup:

- One primary node for writes
- Secondary nodes for reads

At this stage, everything felt solid. Performance was good. Development was fast. No one complained.

Honestly, MongoDB felt like the right decision.

## When Usage Started Feeling "Real"

As more users came in, traffic patterns changed.

Repayments didn't come evenly throughout the day. They came in waves. Morning reminders.

Evening payments.

Month-end spikes. Payment gateways would suddenly send hundreds of webhooks together.

The primary node started doing more work.

CPU went up. Disk activity increased. Still manageable, but you could feel the pressure building.

Then one day, during a busy repayment window, the primary node slowed down badly.

And then it went down.

## Those Few Minutes in Production

MongoDB did what it's designed to do.
It started electing a new primary.

But during that time, writes stopped.

Some payment updates failed. Some requests timed out. Retry logic kicked in. A few updates ran twice.

Loan states briefly looked wrong in the app.

Users refreshed the app and got confused.

Support messages started coming in. Slack alerts went crazy. Engineers dropped whatever they were doing.

Nothing was permanently broken. No money was lost. But the system *felt fragile*.

That feeling stays with you.

## The Real Problem Wasn't the Crash

The crash wasn't the main issue.

The real issue was that **everything depended on one node**.

As long as the primary was healthy, the system was fine. The moment it struggled, the whole system felt it.

When it died, the system paused to decide who the new leader was.

That's when I started questioning something I had never questioned before:
What if having a "master" is the problem itself?

## Thinking About Netflix After That Incident

Netflix operates in a completely different scale, but the idea is similar.

Millions of people press play, pause, rewind, all the time.

From everywhere. Netflix cannot control traffic. It cannot ask users to wait.

If Netflix goes down, people notice immediately. Social media fills up. Trust drops.

Netflix doesn't design systems assuming machines will behave nicely. They assume machines *will fail*.

That mindset doesn't work well with a single master node.

## Cassandra Feels Weird Until You Understand Why It Exists

When you first look at Cassandra, it feels uncomfortable.

No joins. Limited queries. Eventual consistency. It almost feels like it's missing features.

But then you see the most important thing.

There is no master.

Every node is equal. Any node can accept a write.

Any node can serve a read. If one node disappears, the system doesn't stop to recover leadership.

There is no "election pause".

Failure doesn't stop the system. It just reduces capacity a bit.

At Netflix scale, this is huge.

## Netflix Data Is Actually Very Simple

Netflix's core data is not complicated.

Watch history. Playback position. Recommendations metadata. All of it is usually fetched using a user ID.

The access pattern is known in advance. No complex joins. No heavy aggregations in the hot path.

Cassandra is built exactly for this kind of workload. Massive scale. Simple reads and writes. Constant traffic.

MongoDB can do much more, but Netflix doesn't need those features for their core systems.

## Consistency Means Different Things in Different Businesses

In fintech, consistency feels sacred. Even a small mistake feels scary.

But Netflix is not dealing with money. If your watch position is off by a few seconds, you won't even notice. If Netflix goes down for five minutes, everyone notices.

Netflix chooses availability over perfection.

Cassandra makes that choice very clear and very honest.

## Multi-Region Is Not Optional for Netflix

Netflix runs in multiple regions.

Users should get fast responses from nearby systems. One region going down should not take the service with it.

Cassandra handles this naturally. Data can be replicated across regions. Reads and writes can stay local.

No single region is "in charge".

This is possible with MongoDB too, but it becomes much harder to operate safely at extreme scale.

Netflix prefers boring, predictable operations.

## What I Took Back From This Experience

MongoDB was not a bad choice for our loan system. It matched our needs at that time.

But working on that system taught me something important.

Database choices are not about what works when everything is fine.
They are about how the system behaves when things go wrong.

MongoDB struggles during primary changes.
Cassandra barely notices node failures.

Netflix picked Cassandra because their system is not allowed to pause.
