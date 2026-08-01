---
type: Article
title: "MICROSOFT: Process 10 Million Events Per Minute — The Real Problem Wasn't Processing Them"
source: "https://medium.com/gitconnected/microsoft-process-10-million-events-per-minute-the-real-problem-wasnt-processing-them-af4d107709df"
author: "Sagar Yadav"
published: 2026-07-01
created: 2026-08-01
description: "High-throughput Kafka pipelines: consumer lag, rebalance storms, hot partitions, backpressure, retry amplification, and why the bottleneck is never where you first look."
---

# MICROSOFT: Process 10 Million Events Per Minute — The Real Problem Wasn't Processing Them

> **Source**: [Medium — gitconnected](https://medium.com/gitconnected/microsoft-process-10-million-events-per-minute-the-real-problem-wasnt-processing-them-af4d107709df)
> **Author**: Sagar Yadav
> **Published**: 2026-07-01

**Most engineers focus on Kafka. Production systems care about everything that happens after Kafka.**

Processing 10 million events every minute sounds like a scaling problem.

It isn’t.

Kafka scales remarkably well. Consumer groups scale. Databases can be sharded. Infrastructure can always be expanded.

What doesn’t scale automatically is coordination.

A retry here creates a storm there. A new consumer triggers a rebalance. One slow event blocks an entire partition. One overloaded database creates hours of lag upstream.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*nrztjUFYlLUuzagUWh_9Tw.png)

Credits: AI

## The Architecture Everyone Draws First

Almost every engineer starts here:

```sh
Producers
    ↓
  Kafka
    ↓
Consumer Group
    ↓
 Database
```

Simple. Scalable. Battle-tested. At first glance, the problem looks solved.

Then production traffic arrives.

## Kafka Isn’t The First Bottleneck

Kafka can comfortably accept a million messages per second. That isn’t where pipelines usually fail.

**The first bottleneck is almost always somewhere downstream.**

Suppose producers publish 100,000 events every second. Consumers can handle 80,000.

Nothing crashes. Kafka keeps accepting every message. Consumers keep working. CPU looks healthy. Memory looks fine. Dashboards are mostly green.

*But every second, another 20,000 events are waiting. Five minutes in, your “real-time” pipeline is processing data that’s already five minutes old. An hour in, users are waiting an hour for notifications that should have arrived in seconds.*

The system isn’t down. It’s simply getting older.

That’s why experienced teams monitor consumer lag almost as carefully as CPU usage. **Lag tells you something CPU never can: the pipeline has started losing the race.** By the time lag becomes obvious on a dashboard, it’s often already hours behind.

## More Consumers Isn’t Always The Answer

When consumers fall behind, the instinct is to add more. It works — until it hits a wall most engineers don’t anticipate.

Kafka guarantees that a partition can only be consumed by one consumer within a consumer group. If the topic has 32 partitions and 32 active consumers, adding a 33rd accomplishes nothing. It joins the group, gets assigned no partitions, and waits.

The compute exists. The throughput doesn’t increase.

The obvious next move is increasing partition count. More partitions, more parallelism. And it works. Until it doesn’t.

## Adding Consumers Can Make The System Slower

Here’s something that doesn’t make it into most tutorials.

Every time a consumer joins or leaves a consumer group, **Kafka triggers a rebalance. Every partition gets redistributed.** During that rebalance, message processing stops across the entire consumer group.

In a stable deployment, this is a brief pause — seconds, maybe. In a system where pods restart frequently, or where autoscaling is configured aggressively, rebalances can happen constantly. The consumer group spends more time redistributing partitions than processing messages.

The throughput curve inverts. Adding servers makes the system slower.

This tends to surface during the first real load test — or, more painfully, during the first time the platform actually needs to scale under pressure. Sticky partition assignment and cooperative rebalancing protocols reduce the disruption, but the problem first has to be recognized as a problem. Most teams encounter it after assuming that more consumers would simply mean more throughput.

> Part of a series on system design, production engineering, and the interview questions that reveal how engineers actually think under pressure. And if you’re preparing for practical engineering interviews or trying to improve production-level thinking beyond just solving DSA problems, I’ve also been exploring platforms like [PracHub](https://prachub.com/?utm_source=medium&utm_campaign=Sagar_Yadav).

## Partitions Trade One Problem For Another

Adding partitions improves parallelism but introduces an ordering problem. Some events must be processed in sequence — customer transactions, state machine transitions. The standard solution is to hash events by a customer or entity ID to the same partition, preserving order.

Until one customer generates dramatically more traffic than everyone else.

Suddenly one partition is receiving 40% of all events. The other 31 sit nearly idle. More servers don’t help — only one consumer can read from that partition. The ceiling isn’t the cluster. It’s that one overloaded partition.

Choosing a different partition key improves distribution but breaks ordering. You’ve solved throughput and introduced a consistency problem. Distributed systems rarely give you both simultaneously.

## One Slow Event Can Block An Entire Partition

This one tends to catch engineers off guard.

Most events take 50 milliseconds to process. One event triggers a call to a slow downstream service. That single event takes 30 seconds.

Kafka guarantees ordering within a partition. Which means every message behind that one event waits. Thousands of perfectly valid events, already received, sitting behind 30 seconds of someone else’s problem.

The consumer isn’t stuck. It’s working exactly as designed — it’s just working on something expensive. Nothing in Kafka’s metrics shows a problem. The consumer is active. The partition is being read. Events just aren’t advancing at the expected rate.

Timeouts on downstream calls, circuit breakers on slow dependencies, and async processing for expensive operations are the practical mitigations. But recognizing this failure mode requires understanding that the bottleneck isn’t always the pipeline — sometimes it’s one piece of business logic that nobody profiled.

## Nobody Told The Producers To Slow Down

When consumers fall behind, the natural response is to process faster. More consumers, more partitions, optimized logic.

What’s less intuitive is the alternative: stop accepting work.

If producers keep generating events faster than consumers can remove them, Kafka slowly becomes the largest database in the system. Retention grows. Storage grows. Recovery time after an outage grows. Consumer lag keeps climbing because the backlog never shrinks.

**The queue has become a warehouse.**

> Eventually the system is processing yesterday’s data — not because anything failed, but because nobody ever told producers to slow down when consumers were behind.

This is backpressure, and it’s a surprisingly senior conversation in most pipeline design discussions. The instinct is to treat Kafka as infinite storage and trust that consumers will eventually catch up. Sometimes they do. But under sustained overload, “eventually catch up” can mean days of delayed processing and a recovery operation that takes longer than the outage it followed.

Sometimes the right answer isn’t “process faster.” It’s “stop accepting work until the system catches up.”

## One Bad Message Can Stop An Entire Partition

A malformed event arrives. Maybe a schema changed without a coordinated rollout. Maybe a producer bug corrupted the payload. The consumer fails, Kafka redelivers, the consumer fails again.

An hour later it’s still trying. Every valid message behind it in that partition is waiting.

The queue is healthy. Kafka is healthy. The consumer is running. The pipeline isn’t moving.

This failure mode is frustrating precisely because every component reports normal status. Nothing in Kafka shows an error. The consumer is active. The only visible symptom is that one partition stopped advancing — a metric most teams don’t have alerting on until after the first time it costs them.

**Dead Letter Queues exist specifically for this. When a message fails beyond a retry threshold, it moves to a separate topic rather than blocking the partition indefinitely.** The pipeline continues; the bad message gets examined separately. It’s an acknowledgment that some messages will be unprocessable, and the right response is to move them aside rather than prove repeatedly that they can’t be handled.

## Retries Can Become Their Own Outage

A downstream service slows from 100ms to two seconds. Consumers start retrying. Every instance retries. Every failed request generates another request.

Traffic to the downstream service doubles, then triples. The service, already struggling, now receives multiples of its original load. What started as a slowdown becomes a complete failure — caused entirely by the systems trying to recover from it.

Each individual retry decision is rational. The aggregate behavior is destructive.

Exponential backoff, jitter, and circuit breakers aren’t throughput optimizations. They’re survival mechanisms — the difference between a degraded service and a cascading outage. In a high-throughput pipeline with many concurrent consumers, the retry amplification factor can be enormous. Getting this wrong once tends to fix it permanently.

## The Bottleneck Moves Downstream

Consumer lag is near zero. Kafka is healthy. Every metric looks good.

Then the database starts receiving 200,000 writes per second.

Adding more consumers accelerates the problem. Index maintenance becomes expensive. Lock contention increases. Replication falls behind. Write latency climbs.

Every optimization to the Kafka layer revealed the next constraint downstream. This is the pattern that repeats in any pipeline built for sustained high throughput: solving one stage’s capacity problem exposes the next stage’s limit.

Kafka solved ingestion. It never promised storage would scale with it. The pipeline is a chain, and the chain is only as fast as its slowest link — wherever that happens to be today.

## The Question Most Engineers Ask Too Late

**Do all 10 million events actually need to be processed immediately?**

**Surprisingly often, the answer is no.**

Analytics pipelines aggregate events into time windows rather than processing each one individually. Metrics systems batch thousands of updates. Recommendation engines work on micro-batches and tolerate seconds of delay without any visible impact on the user experience.

Sometimes delaying processing by a few seconds reduces infrastructure cost dramatically while producing identical outcomes. Understanding what latency the business actually requires — not the latency that feels appropriate for a system called “real-time” — changes the architecture significantly. It’s worth asking before sizing the pipeline.

## What Senior Engineers Actually Ask

At first glance, processing ten million events sounds like a scaling problem.

It isn’t.

The components scale. What doesn’t scale automatically is the coordination between them — the retries that become storms, the consumers that trigger rebalances, the events that block partitions, the lag that accumulates silently while every metric looks healthy.

Engineers rarely ask whether a system *can* process ten million events per minute.

They ask what breaks first when it does.

Because that’s the question production eventually answers for you. The only choice is whether you’ve thought about it in advance or whether you’re thinking about it at 2 AM when the lag graph is pointed straight up.

*Building or debugging event pipelines? I’d enjoy hearing where the bottleneck actually turned out to be.  
Part of a series on system design, production engineering, and the interview questions that reveal how engineers actually think under pressure. And if you’re preparing for practical engineering interviews or trying to improve production-level thinking beyond just solving DSA problems, I’ve also been exploring platforms like* [*PracHub*](https://prachub.com/?utm_source=medium&utm_campaign=Sagar_Yadav)*.*