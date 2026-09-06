---
type: Article
title: "How Mastering Idempotency Saved Our Event-Driven System"
description: "A real-world case study of fixing duplicate events in a social newsfeed by layering deterministic keys, Redis deduplication, and database constraints."
source: "https://medium.com/@systemdesignwithsage/how-mastering-idempotency-saved-our-event-driven-system-5ecbce1b1bd6"
author: "System Design with Sage"
published: 2026-01-19
generated: { by: process:okf-migrate, at: 2026-07-24T00:00:00Z }
---

# How Mastering Idempotency Saved Our Event-Driven System

> **Source**: [Medium](https://medium.com/@systemdesignwithsage/how-mastering-idempotency-saved-our-event-driven-system-5ecbce1b1bd6)
> **Author**: System Design with Sage
> **Published**: 2026-01-19

## Overview

[Event-driven architectures](https://www.educative.io/courses/grokking-the-product-architecture-interview/event-driven-architecture-protocols) often reveal their weaknesses only at scale. Consider a social newsfeed handling millions of writes per day: a user creates a post, a producer emits an event, and downstream consumers fan out to update followers' timelines. The system feels fast and nicely decoupled, optimized heavily for throughput while quietly assuming ideal delivery behavior.

As traffic grows, unexpected behaviors emerge. Users begin seeing the same post twice in their feeds. Like counts become inconsistent and inaccurate. The system, built on standard asynchronous patterns, contains a fundamental flaw: it assumes every event arrives exactly once, but distributed systems rarely provide that guarantee.

## How Duplicated Events Polluted the Feeds

The root cause was the **at-least-once** delivery guarantee from the message broker. This guarantee ensures no data is lost, but can create duplicate messages as a side effect. Ideally, a consumer processes an event and acknowledges it. In reality, networks fail.

Consider a standard `PostCreated` workflow:

1. The `FeedWriter` service picks up the event, writes the post to the database, and prepares to send an ACK back to the broker.
2. A network timeout occurs, and the broker never receives the ACK.
3. The broker assumes the worker failed, waits for a visibility timeout, and redelivers the same message to a new worker.
4. The second worker has no way of knowing the job is already done. It inserts the same post again.

Because the database uses auto-incrementing primary keys, the duplicate is accepted as a valid new row — creating a "ghost" duplicate.

The problem is worse with aggregations. If a `LikeAdded` event is duplicated, a single user action increments the counter twice. Materialized counter columns (e.g., `posts.like_count`) result in artificially inflated engagement metrics and skewed analytics.

> **Key Insight**: Relying on default broker settings often masks retry loops until high load triggers a cascade of duplicates.

## Designing Idempotent Feed Writer Services

The team adopted **idempotency** — the property where executing the same event multiple times yields the same result. Three specific patterns were implemented:

### 1. Deterministic Keys

Instead of generating random IDs on the write path, keys were derived from the data itself (e.g., a hash of `userId + postId` or a producer-assigned `userActionId`). All retries of the same logical action generate the same primary key. If a duplicate event tries to insert a record, the database safely rejects it via unique constraint violation.

> **Note**: Deterministic keys push deduplication down to the storage engine's unique constraints — they are the first line of defense.

### 2. Atomic State Changes

Stateful operations like `UpdateLikeCount` were redesigned to be atomic. Instead of read-modify-write (read value, add one in memory, write back), the team used atomic increment commands provided by the database. Atomic increments are combined with deduplication, so the increment only happens on the first observation of an action. This prevented race conditions during rapid retries.

### 3. Upsert Logic

When stitching new posts into personalized timelines, upsert commands (insert or update if exists) were used. A replayed event effectively overwrites existing state with identical data rather than creating a duplicate entry.

This architectural shift moved the schema away from surrogate keys unrelated to business logic. Uniqueness enforced at the database level created a hard stop for duplicates slipping past the application layer.

## Using Event IDs and a Deduplication Store

While database constraints handled the storage layer, a gatekeeper was needed to protect expensive compute logic further upstream.

A globally unique `eventId` (UUID) was assigned to every message at the producer level. [Redis](https://redis.io/) was selected as the deduplication store due to its sub-millisecond latency.

### The Redis Gatekeeper

Upon receiving an event, the consumer attempts to set a key in Redis using the `eventId` via the `SET NX` command, which only sets the key if it does not already exist:

- If Redis returns **false**: the event is a duplicate or is currently being processed. Discard it immediately, saving CPU cycles and database I/O.
- If Redis returns **true**: the consumer proceeds with business logic.

> **Practical Tip**: Always set a Time-To-Live (TTL) on deduplication keys to prevent memory leaks from millions of old event IDs.

### Filtering at the Edge

By filtering at the edge of the service, the "thundering herd" of retries never reaches core domain logic. Even if the broker resends a large batch of mostly duplicate messages, consumers reject the vast majority in milliseconds. The TTL is configured to slightly exceed the maximum retry window of the broker, covering failure scenarios where retries happen within minutes of the original event.

This dual-layer approach combines fast filtering in Redis with hard constraints in the database.

## Auditing Idempotency with Event Replays

Confidence in idempotency is only gained after validation under failure conditions. The team validated by replaying massive volumes of historical production logs into a staging environment:

- A full day of raw event data (millions of actions) was replayed to the new consumers.
- Duplicates were intentionally injected and order was shuffled to simulate severe network partitions.
- Downstream side effects (push notifications) were mocked out.

The final state of timeline databases was monitored, comparing row counts and checksums between source and target databases. The before-and-after snapshots matched perfectly. Even when replaying the stream three times in a row, `LikeCount` remained accurate and feeds contained exactly one instance of every post.

> **Key Insight**: Testing with "happy path" data won't reveal concurrency bugs; you must artificially induce chaos in your test environment.

Open-source tools like [Debezium](https://debezium.io/) were used to capture change data for verification.

## Conclusion

Implementing idempotency transformed the newsfeed from a fragile, duplication-prone pipeline into a system that could be retried aggressively without corrupting state. By layering:

1. **Deterministic client-side keys** — first line of defense at the database level
2. **A lightweight Redis gatekeeper** — fast pre-filter using `SET NX` with TTL
3. **Hard database constraints** — unique constraints as the final safety net

The team eliminated duplicate feed entries and inflated counters, even in the face of network failures.

When retrofitting an existing system, start by assigning stable, unique IDs at the producer. Once each user action has a stable, end-to-end traceable ID, deduplication stores and chaos testing become safe to introduce. A system only earns the label "idempotent" if replaying a large batch of historical logs produces the same final state.
