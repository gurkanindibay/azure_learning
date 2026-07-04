---
type: Article
title: "How Kafka Really Works: Lessons from a 60M+ Events/Day Production Pipeline"
source: "https://medium.com/learnwithnk/kafka-under-the-hood-the-architecture-secrets-that-make-it-scale-bdb4bd9cf398"
author: "Nadeem Khan (NK)"
published: 2026-02-07
created: 2026-07-04
description: "A deep dive into Kafka internals — log segments, partition-level replication, offset tracking, and the append-only architecture that enables 60M+ events/day throughput."
tags:
  - kafka
  - messaging
  - distributed-systems
  - event-driven
---

# How Kafka Really Works: Lessons from a 60M+ Events/Day Production Pipeline

> **Source**: [Medium](https://medium.com/learnwithnk/kafka-under-the-hood-the-architecture-secrets-that-make-it-scale-bdb4bd9cf398)
> **Author**: Nadeem Khan (NK)
> **Published**: 2026-02-07

I still remember my first Kafka production setup in 2022. I was streaming changes from Postgres WAL into Salesforce using a couple of Spring services. At the time, I treated Kafka like a regular message queue. Produce here, consume there, move on. I assumed messages disappeared after being read and that offsets were just counters. Everything worked completely fine.

But as traffic grew to 60M+ events per day, I realised I was using Kafka without truly understanding it.

That curiosity led me down a rabbit hole of very practical questions:

- Is Kafka basically a database?
- How is Kafka able to handle high write throughput?
- Where does the data actually live?
- How does Kafka store events?
- How is Kafka scalable and fault-tolerant?
- What happens to a message once it is read by a consumer?
- How do consumers keep their place?

This post is simply my attempt to answer those questions clearly, using the mental models that finally made Kafka click for me.

## Is Kafka Basically a Database?

Kafka behaves like a highly scalable, fault-tolerant event store built on an append-only log. Producers append events, consumers read them, and Kafka persists everything on disk.

The key difference from traditional message queues like RabbitMQ is how data disappears:

- Consumers do not delete data. They only move their offsets, which represent their read position.
- Data is removed based on retention policies such as time or size, not consumption.

Think of Kafka as an immutable log with a collection of digital bookmarks.

## How Does Kafka Store Events?

Initially, I assumed Kafka might use something like a heap or a dictionary to store events.

That mental model is completely wrong.

Kafka writes events into large log segments. Each segment consists of three files:

1. .log contains the raw records
2. .index provides a sparse offset index
3. .timeindex supports timestamp-based lookups

Kafka keeps appending to the active segment until it reaches a size limit, typically around 1GB. Once that happens, Kafka rolls to a new segment.

If a record arrives that would overflow the current segment, Kafka closes the current segment early and creates a new segment for that record. Records are never split across segments and are always atomic.

This simple append-only design is a major reason Kafka performs so well.

## Where the Data Lives?

My initial thought was that within a broker, there would be a folder for a topic, and within that folder, log segments for each partition. But instead, I learned that the

- Topics (Logical): Just stream names or labels.
- Partitions (Physical): The true units of storage and ordering.
- Brokers (Machines): The servers that host partitions.

A topic is only a logical grouping. The partition is the physical log stored on a broker’s disk.

This architecture enables Kafka’s scalability. By distributing partitions of a single topic across many machines, you can achieve parallel processing at scale.

## How Is Kafka Able to Handle High Write Throughput?

Kafka achieves high throughput primarily through sequential disk writes, batching, and partition-level parallelism.

Producers simply append events to logs, avoiding expensive random I/O. Combined with OS page cache and efficient network transfer, this allows Kafka to sustain extremely high write rates.

Instead of treating each message as an isolated operation, Kafka treats streams of events as continuous logs.

## How is Kafka Scalable and fault-tolerant?

Replication in Kafka happens at the partition level.

Each partition has one leader and multiple followers:

- Producers and consumers communicate only with the leader.
- Followers continuously replicate the leader’s data.

Replication is controlled by the replication factor. A common production configuration uses a replication factor of 3, storing three copies of data across different brokers.

This allows Kafka to lose a broker while still maintaining a majority, balancing durability with storage cost.

## How Does Kafka Maintain Consistency?

Kafka allows you to trade availability for consistency through configuration.

Two important settings are:

- acks=all
- min.insync.replicas=2

There is a common misconception that acks=all means the leader waits for every replica to respond.

In reality, it waits for all in-sync replicas to be available. When combined with min. insync.replicas=2, Kafka will only acknowledge a write after at least two replicas have safely persisted the data.

This creates a clear durability contract between Kafka and producers.

## What Happens to a Message Once It Is Read?

Kafka never deletes data when consumers read it.

Instead, Kafka tracks offsets per partition and per consumer group.

Because the data remains in place and only offsets move, multiple independent consumers can process the same data at different speeds without interfering with each other.

This is what enables fan-out, reprocessing, and replay.

## Final Takeaway

What began as a straightforward pipeline from Postgres to Salesforce eventually scaled to over 60 million events per day. Kafka handled the growth effortlessly, while I struggled to keep up.

That experience led me to rethink my initial “message queue” perspective and adopt a distributed, append-only event log model instead. Understanding partitions, offsets, log segments, and in-sync replicas made Kafka feel far less mysterious and much more logical.

If there’s one lesson to remember, it’s this: Kafka scales so well because it treats every event as an immutable fact, not just a temporary message. Everything else follows from this principle.

In a future blog post, I will share my setup for scaling Kafla to handle 60M+ events/day.

Happy Learning.

Follow me on [LinkedIn](https://www.linkedin.com/in/nadeem-khan-75135210a/) and [Medium](https://codewithnk.com/) for more such content.