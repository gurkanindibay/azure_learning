---
type: Article
title: "How Uber Handles Trillions of Kafka Messages Without Bringing Everything Down"
source: "https://medium.com/@the_atomic_architect/uber-kafka-trillions-messages-66424e02530c"
author:
  - "The Atomic Architect"
published: 2026-09-12
created: 2026-09-13
description: "How Uber scales Kafka to trillions of messages a day using federated clusters, uReplicator with Apache Helix, Chaperone auditing, consumer proxies, DLQs, and tiered storage."
tags:
  - "kafka"
  - "messaging"
  - "distributed-systems"
  - "system-design"
  - "scalability"
  - "reliability"
---

# How Uber Handles Trillions of Kafka Messages Without Bringing Everything Down

> **Author**: The Atomic Architect  
> **Source**: [Medium](https://medium.com/@the_atomic_architect/uber-kafka-trillions-messages-66424e02530c)  
> **Published**: 2026-09-12  
> **Related Takeaways**: [Uber Kafka at Trillions Scale — Key Takeaways](../../system-design-architecture/messaging/uber-kafka-scale-takeaways.md)  

A look inside the message bus that quietly keeps rides, trips, and payments in sync — and what happens when it starts to wobble

There’s a specific kind of dread that comes from watching a consumer lag graph climb and refusing to level off.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*OK6NKbfJrCQEbTlgUab6ZA.png)

You’ve probably felt a version of it.

A queue that’s supposed to drain in seconds is suddenly ten minutes behind. Somewhere downstream, a service is waiting on data that hasn’t arrived yet. And you’re staring at a dashboard doing mental math on how bad this gets if it doesn’t stop in the next five minutes.

Now imagine that queue isn’t handling a few thousand events an hour.

Imagine it’s carrying location updates from drivers, fare calculations, trip status changes, payment events, and data from thousands of services — all day, every day.

At Uber’s scale, that means more than a trillion messages a day and multiple petabytes of data.

That’s where the interesting engineering begins.

The headline number isn’t what caught my attention, though. Big numbers are cheap. Every company with a technical blog eventually gets around to telling you about its “massive scale.”

The more interesting question is much smaller:

What happens when one message disappears?

One location update. One trip status change. One payment event.

At this scale, message loss isn’t something you can treat as an impossible edge case. With enough moving parts, failures are statistically inevitable.

The real challenge is knowing when something was lost, where it disappeared, and what to do about it.

I spent some time going through Uber’s engineering writeups and conference material to understand how they approached this problem.

What I found wasn’t one magical Kafka optimization.

It was a collection of deliberately boring engineering decisions — each designed to make a specific failure mode smaller, more visible, and easier to recover from.

And that’s what makes the architecture interesting.

## Why “just add more Kafka” eventually stops working

If you’ve used Kafka at a typical company, your mental model is probably straightforward:

Producers write to topics.

Topics are divided into partitions.

Consumer groups read those partitions.

Add more partitions and consumers when you need more throughput.

That model works remarkably well.

Until it doesn’t.

At Uber’s scale, three problems become particularly painful.

### 1. Blast Radius

A Kafka cluster can be extremely reliable and still represent a single failure domain.

A bad broker.

A runaway topic.

A disk problem.

A configuration mistake.

Any of these can affect a significant portion of the workloads sharing the cluster.

If that cluster happens to carry data powering matching, ETAs, pricing, or payments, a cluster-wide problem stops being an infrastructure issue.

It becomes a business outage.

### 2. Geography

Uber operates across multiple regions and data centers.

Its infrastructure is designed around active-active operation, where multiple regions are serving production traffic simultaneously rather than having one primary region sitting around waiting for disaster.

That creates a much harder problem.

Events generated in one region may need to become available somewhere else, and downstream systems need to deal with data regardless of where it originated.

Kafka replication becomes a much more complicated problem when you aren't simply copying data from “primary” to “backup.”

### 3. Trust

At small scale, you can sometimes get away with:

> “We’re pretty sure nothing was dropped.”

At a trillion messages a day, you can’t.

You need evidence.

You need to know that what entered the system actually made it through the pipeline.

And if something disappeared, you need to know where.

Those three problems pushed Uber toward a very different architecture.

## Splitting the Ocean into Lakes: Federated Kafka Clusters

The obvious response to increasing Kafka traffic is to make the cluster bigger.

More brokers.

More disks.

More partitions.

Keep scaling vertically.

Uber eventually ran into the problem with that approach:

**A bigger cluster is still one failure domain.**

Instead, Uber went wide instead of endlessly going tall.

Rather than putting everything into one enormous Kafka cluster, Uber operates multiple federated clusters.

Topics can be distributed across these clusters according to traffic, workload, and criticality, with routing infrastructure abstracting the underlying physical location from applications.

That changes the failure model considerably.

If one cluster has a bad day, it doesn’t necessarily mean the entire Kafka estate has a bad day.

Capacity planning becomes a cluster-level problem.

A high-volume workload doesn’t necessarily have to compete for resources with unrelated critical workloads.

And operational changes can be isolated instead of potentially affecting everything simultaneously.

But federation introduces another problem.

Now you have multiple Kafka clusters that need to behave like parts of one larger system.

Data may need to move between them.

Topics may need to be replicated across regions.

And suddenly Kafka replication itself becomes a critical piece of infrastructure.

That’s where **uReplicator** enters the picture.

## The Replication Engine Uber Built Itself: uReplicator

Kafka has historically provided tools such as MirrorMaker for replicating data between clusters.

The basic idea is simple:

Read from one Kafka cluster.

Write to another.

Repeat.

At Uber’s scale, however, the operational behavior of the replication layer mattered just as much as its throughput.

One major problem was rebalancing.

Kafka consumers use a group coordination mechanism to distribute partitions among consumers.

When consumers join or leave, the group can rebalance.

Normally, that’s fine.

But imagine doing this across enormous numbers of topic-partitions and replication workers.

A relatively small failure can trigger coordination work across a large replication fleet.

Replication can stall while assignments are redistributed.

At Uber’s scale, even short interruptions multiplied across many clusters become meaningful.

So Uber built uReplicator, originally developed around 2016, using Apache Helix for coordination and partition assignment.

The important architectural idea was to separate:

**Who should consume a partition?**

from:

**How should that partition actually be consumed?**

A controller layer could use Helix to manage assignments while workers performed the actual replication.

That allowed individual assignments to move without forcing the entire worker fleet into a large coordinated rebalance.

Instead of:

> “Something changed. Everyone stop and figure out the new assignment.”

the system could move a much smaller piece of the workload.

That sounds like a subtle implementation detail.

At this scale, it isn't.

It changes a potentially fleet-wide pause into a localized handoff.

Over time, uReplicator also evolved to handle things such as automatic topic discovery and load redistribution as traffic patterns changed.

The underlying philosophy was simple:

**If a human needs to notice something before the system can recover, the system probably isn't automated enough.**

## Trust, But Verify: Chaperone

This is probably the least glamorous part of the architecture.

And arguably one of the most important.

**Accounting**.

At Uber’s scale, messages can disappear.

Not because engineers are careless.

Because distributed systems contain networks, buffers, brokers, consumers, disks, processes, and machines — all of which can fail.

A proxy can drop a batch.

A consumer can crash before committing an offset.

A network connection can disappear.

A broker can experience a failure at exactly the wrong moment.

The important question isn't:

> “Can we make message loss impossible?”

It’s:

> “How quickly can we prove that message loss happened?”

Uber built **Chaperone** for exactly this purpose.

The concept is surprisingly straightforward.

Messages are tracked as they move through different stages of the pipeline.

Aggregate counts are collected at different tiers.

For example:

- How many messages entered the proxy?
- How many reached the regional Kafka layer?
- How many reached the aggregated cross-datacenter system?

Those counts are then collected and compared.

If the numbers match, the pipeline has evidence that messages weren't lost between those checkpoints.

If they don't, the discrepancy provides a clue about where the loss occurred.

That's a huge difference from simply discovering that something is missing downstream.

You don't want:

> “Somewhere in the pipeline, we seem to have lost data.”

You want:

> “The producer sent 10 million messages. The next tier received 9,999,972. Start looking here.”

That turns an invisible reliability problem into an observable one.

And there's an important lesson here:

**Reliability isn't always about preventing failure. Sometimes it's about making failure measurable.**

## Decoupling Applications from Kafka: Consumer Proxy

Replication wasn't the only place where Kafka's native consumer model created operational complexity.

Every application consuming directly from Kafka has to deal with things like:

- consumer groups
- partition assignment
- rebalancing
- heartbeats
- backpressure
- offsets
- failure recovery

For a handful of services, that's manageable.

For thousands of services, it becomes repeated infrastructure knowledge that every application team has to get right.

Uber addressed this with a Consumer Proxy layer.

Instead of every application directly managing the Kafka consumer lifecycle, the proxy handles much of the Kafka-specific machinery.

The application can interact with a simpler abstraction:

**Give me messages. I'll tell you when I'm done processing them.**

The proxy can handle partition assignment, rebalancing, and backpressure centrally.

It can also communicate with downstream services asynchronously, including over gRPC.

This creates an important separation:

**Application developers don't need to be Kafka experts just to consume an event.**

That's a powerful infrastructure principle.

When an underlying system becomes sufficiently complex, don't necessarily expose all of that complexity to every team using it.

Put the complexity behind a well-designed interface.

## What Happens When a Message Is Poisonous?

Even the best infrastructure can't prevent every downstream processing failure.

Eventually, a consumer encounters:

- malformed data
- an unexpected schema
- a software bug
- a temporary dependency failure
- something else the application simply can’t process

Now consider Kafka's partition ordering.

If message #4,502 repeatedly fails, blindly retrying it can prevent the consumer from progressing to #4,503.

One bad record can effectively become a roadblock.

That's where dead-letter queues become useful.

Instead of allowing the consumer to retry the same message forever, the failed message can eventually be moved into a separate topic.

The main stream continues.

The failed message remains available for inspection.

And the team can fix the underlying problem and deliberately replay the message later.

That last part is important.

**Replay should be a feature, not an emergency ritual.**

If your recovery plan is:

> “Someone will SSH into a machine at 3 a.m. and figure out which offsets to reset.”

you don't really have a recovery strategy.

You have a future incident.

A mature event-driven system treats historical data as something that can be intentionally reprocessed.

## Not Everything Needs to Stay Hot: Tiered Storage

There’s another problem that appears when your event history becomes enormous.

Storage.

Kafka traditionally keeps data on broker-local storage.

That's fantastic when consumers are reading recent events.

It's less attractive when you're retaining enormous quantities of historical data for:

- backfills
- analytics
- debugging
- compliance
- recovery

Keeping everything on expensive local disks forever doesn't make much economic sense.

That's where tiered storage comes in.

Recent data can remain on fast local storage.

Older data can be moved to cheaper, more scalable storage.

The important part is that consumers can still access historical data without the entire application architecture needing to care exactly where those bytes physically live.

This is another example of separating concerns.

Hot data gets optimized for speed.

Cold data gets optimized for cost and scale.

And the application doesn't need to know the difference.

## The Real Architecture Isn’t Kafka

If you zoom out, the interesting part isn't really Kafka.

It's the philosophy underneath the architecture.

Federated clusters reduce blast radius.

uReplicator makes cross-cluster replication manageable.

Chaperone makes message loss observable.

Consumer Proxy hides Kafka's operational complexity from application teams.

Dead-letter queues prevent individual bad messages from blocking entire streams.

Replay turns recovery into an intentional operation.

Tiered storage prevents historical data from becoming an ever-growing local-disk problem.

None of these decisions appeared because someone wanted to build the world's most complicated message bus.

They appeared because simpler systems eventually encountered specific failure modes.

One giant cluster was too much of a blast radius.

So they federated.

**Replication rebalancing became too disruptive.**

So they redesigned the replication architecture.

**“We think no messages were lost”** wasn't good enough.

So they built an auditing system.

**Thousands of application teams shouldn't have to understand Kafka internals.**

So they introduced a proxy layer.

**One malformed event shouldn't block everything behind it.**

So they isolated failed messages.

**And historical data shouldn't consume expensive hot storage forever.**

So they introduced tiered storage.

That's the pattern worth remembering.

## The Lesson Isn’t “Build What Uber Built”

The tempting takeaway from an architecture like this is:

> “My system is struggling. Maybe I need federated Kafka clusters and a custom replication engine.”

Probably not.

Most systems don't need Uber's infrastructure.

What they can borrow is the reasoning.

When your system starts approaching its limits, don't just ask:

**“How do I make it bigger?”**

Ask:

**“What happens when this specific component fails?”**

Then ask:

**“How large is the blast radius?”**

Then:

**“How will I know it failed?”**

And finally:

**“How do I recover without making the original problem worse?”**

That mindset scales surprisingly well.

You don't need a trillion messages a day to benefit from it.

A payment processor handling a few thousand transactions can use the same philosophy.

A background job queue can use it.

A file-processing pipeline can use it.

Even a small Kafka deployment can use it.

I've run into the same basic pattern in payment processing: one malformed record shouldn't be allowed to jam an entire batch. Isolate it. Flag it. Keep the healthy work moving. Make replay deliberate.

The scale changes.

The underlying engineering instinct doesn't.

## Fail Small. Fail Loud.

The most interesting thing about Uber's Kafka architecture isn't that it processes an absurd number of messages.

It's that the system was designed around a simple assumption:

**Something will eventually break.**

The goal isn't to build a system where nothing ever fails.

That's unrealistic.

The goal is to make failures:

- small
- observable
- isolated
- recoverable

A bad broker shouldn't become a company-wide outage.

A lost message shouldn't become an invisible data-integrity problem.

A poisoned event shouldn't block an entire partition.

A consumer shouldn't need to understand every Kafka internal.

And historical data shouldn't turn into an infinite storage bill.

That's what makes this architecture interesting.

Not the trillion-message number.

The engineering discipline behind making that number boring.

So the next time your consumer lag graph starts climbing and refuses to level off, don't just ask:

**“How do I make this faster?”**

Ask the more uncomfortable question:

> “When this fails, how small will the failure be — and how quickly will I know?”

That question is useful whether you're running twenty Kafka clusters or one queue on a single server.

And at scale, it might be the question that keeps everything else running.
