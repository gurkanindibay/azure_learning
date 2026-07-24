---
type: Article
title: "Amazon Cart Shows Old Data — System Design Deep Dive on Cache Invalidation and Distributed Session Consistency"
source: "https://codefarm0.medium.com/amazon-cart-shows-old-data-system-design-deep-dive-on-cache-invalidation-and-distributed-session-168b69c052fd"
author: "Arvind Kumar"
published: 2026-07-20
created: 2026-07-24
description: "A system design interview scenario exploring cache invalidation strategies, distributed cache synchronization, session consistency, and event-driven updates through the lens of Amazon cart stale-data problem."
tags:
  - "cache-invalidation"
  - "distributed-caching"
  - "event-driven"
  - "session-consistency"
  - "system-design"
timestamp: 2026-07-24T00:00:00Z
---

# Amazon Cart Shows Old Data — System Design Deep Dive on Cache Invalidation and Distributed Session Consistency

> *"There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton*

This is the quote every engineer knows. And this is the interview question that tests whether you truly understand why cache invalidation is hard.

The scenario is painfully relatable: you remove an item from your cart on the mobile app. You open your laptop an hour later. The item is still there. You remove it again. Next day, it is back. Your cart has become a ghost town of things you already decided not to buy.

> [Full story for non-members](https://codefarm0.medium.com/amazon-cart-shows-old-data-system-design-deep-dive-on-cache-invalidation-and-distributed-session-168b69c052fd?sk=546b5f8d1e08773f1ac66392987364d0)

**Concepts at a Glance**

- Why caches exist and the read-vs-write tradeoff
- Write-through, write-around, and write-back cache strategies
- TTL-based invalidation and why it is both savior and curse
- Event-driven invalidation using pub/sub
- Distributed cache synchronization across regional replicas
- Session consistency — why the same user sees different data on different devices
- The CAP implications of keeping caches consistent

## The Scenario

**Arvind (Interviewer):**
A user removes an item from their Amazon cart on the mobile app. Later, they open Amazon on their laptop. The item is still in the cart. They remove it again. A few hours later, it reappears.

The cart data is supposed to be the same everywhere. Why is it not? How would you fix this?

**Meera (Candidate):**
Before I touch the cache, let me understand the cart's write path. Every time the user adds or removes an item, the system must update the cart. The question is: how many components hold a copy of that cart?

There are three distinct failure modes here, and they often compound:

1. The cache was not invalidated on write
2. The cache was invalidated but a stale replica served the read
3. The database write succeeded but the cache update failed silently

## Failure Mode 1: The Cache Was Never Invalidated

> *The simplest explanation: the write path updates the database but forgets to update the cache.*

**Meera:**
This happens when the cache is treated as read-only optimization without a write-through contract. The cart service updates the database on a write. The cache is only populated on a read miss. So after the database update, the cache still holds the pre-write state. The next read hits the cache and gets old data.

The fix is write-through caching: every write updates the cache synchronously before returning.

## Failure Mode 2: Stale Cache Replica

**Meera:**
Even with write-through caching, distributed caches have replicas. When your cache cluster replicates data across nodes, the write might reach one node while the read hits another that has not received the update yet.

This is a replication lag problem. The primary cache node invalidated the entry, but the change has not propagated to the replica that served the read.

The fix here depends on the consistency model:

- **Strong consistency**: Read from the primary cache node. Slower but always correct.
- **Session affinity**: Route the same user's requests to the same cache node. If mobile and laptop requests go to different nodes, this fails.
- **Version stamps**: Every cache entry carries a version. The client sends its last known version. If the cache has a newer version, it returns the data. If the cache has an older version, it treats it as a miss and reads from the database.

## Failure Mode 3: The Silent Partial Failure

**Meera:**
This is the most insidious one. The database write succeeds. The cache invalidation is sent. But the cache node is under memory pressure and evicts the invalidation message before processing it. Or the network between the cart service and cache drops the packet. The cache never gets invalidated.

```
Database: DELETE FROM cart_items WHERE user=U AND item=X  ->  SUCCESS
Cache:    DEL cart:{userId}                                ->  ??? (silently dropped)
```

The service thinks both operations succeeded. The user thinks the item was removed. The cache cheerfully serves stale data until the TTL expires.

**Arvind:**
So TTL is the ultimate safety net?

**Meera:**
TTL is the last line of defense, not the primary strategy.

If every cache entry has a TTL of 10 minutes, the stale data lives for up to 10 minutes. That is 10 minutes of confused users re-removing items. For a cart system, that is unacceptable.

But TTL is essential as a fallback. It prevents stale data from living forever if invalidation fails. The key is to make the TTL short enough that the damage is limited but long enough that the cache hit rate remains high enough to justify having a cache.

For cart data, I would set TTL to 5 minutes and use event-driven invalidation as the primary mechanism. TTL is the crash recovery mechanism.

**Arvind:**
Let us talk about event-driven invalidation. How does it work?

**Meera:**
Instead of the cart service directly calling the cache, every write publishes an event to a message bus. Any interested system can listen and react.

Benefits of event-driven invalidation:

- **Decoupling**: The cart service does not need to know about every cache layer. It just publishes "cart changed." Any system that caches cart data subscribes and handles invalidation in its own way.
- **Reliability**: If the cache is down during the write, the event persists in the message queue. When the cache recovers, it replays unprocessed events and catches up.
- **Extensibility**: Add a new cache layer? Just add a new consumer. No changes to the write path.
- **Atomicity**: Combined with the outbox pattern, the database write and the event publication are atomic. If the DB write fails, the event is never published. If the event publication fails, the DB write is rolled back.

**Arvind:**
What makes cross-device session consistency harder than single-device?

**Meera:**
Single-device consistency is a cache problem. Cross-device consistency is a session routing problem.

When the user removes an item on mobile, the mobile request goes to one cart service instance. That instance invalidates the cache. But the cache invalidation is only useful if all subsequent reads — regardless of device — hit the same cache or a cache that has been invalidated.

The laptop user might be routed to a different data center entirely.

In this setup:

- User in London removes item on mobile. Write goes to EU-West. Cache in EU-West is invalidated. Database is updated.
- Same user opens laptop. Request is routed to EU-West. Cache hit on EU-West is now a miss. Falls through to database. Gets correct state. Good.

But:

- User removes item on mobile in London (EU-West). Then flies to New York and opens laptop. Request goes to US-East. US-East cache still has the old data. Hit. Stale.

The global invalidation bus solves this. When EU-West invalidates its cache, it publishes a cross-region invalidation event. US-East consumes the event and invalidates its local cache. The next read from US-East misses and gets fresh data from the database.

The tradeoff: cross-region replication takes time. During that window, the user might see stale data on the other region. This is eventual consistency between caches.

**Arvind:**
So you cannot achieve strong consistency across regions without sacrificing availability?

**Meera:**
Exactly. This is CAP theorem in practice.

For cart data, eventual consistency is acceptable because:

1. The database is the source of truth. The cache is just an optimization.
2. The TTL ensures the stale data disappears within minutes regardless.
3. The user is unlikely to switch regions within seconds of modifying their cart.

But for systems where consistency matters more — like inventory or payments — you would not use a distributed cache at all. You would read from the database directly, use optimistic locking, or use a strongly consistent storage layer.

## The Complete Architecture

**Meera:**

Key decisions:

- **Write path uses the outbox pattern**: The database write and the event publication are atomic. If the write fails, no event is published. If the event bus is down, the outbox poller retries until it succeeds.
- **Multiple invalidation consumers**: Redis cache, CDN edge cache, and search index all subscribe to the same event. Adding a new cache layer just means adding a new consumer.
- **TTL as the safety net**: Every cache entry has a 5-minute TTL. Even if every invalidation mechanism fails, stale data disappears within 5 minutes.
- **Session affinity is preferred but not required**: If routing consistently sends the same user to the same region, stale reads from cross-region caches are avoided. But the system works correctly without it — just with slightly higher latency during cache misses.
- **Cross-region invalidation via Kafka mirroring**: Kafka topics are replicated across regions. Cache invalidations propagate to all regions within seconds.

## Monitoring the Invalidation System

**Meera:**
I would track:

1. **Cache hit ratio before and after writes** — After a cart update, the hit ratio for that user should drop as the cache is invalidated. If it stays high, invalidation is not working.
2. **Invalidation event processing lag** — Time between event publication and cache invalidation acknowledgement. Growing lag indicates the consumer is falling behind.
3. **Stale read rate** — Percentage of reads where the cache returned data that was newer in the database. Measured by comparing cache timestamp vs database timestamp on reads.
4. **Outbox replay lag** — How far behind the outbox poller is. If events are piling up in the outbox table, invalidation is delayed by minutes.
5. **TTL expiry percentage** — Percentage of cache entries that expire naturally vs being invalidated explicitly. If most entries expire via TTL, the event-driven invalidation path is failing.
6. **Cross-region replication delay** — Time for an invalidation event to propagate from one region to another.

## Conclusion

The Amazon cart stale data problem is not about a single cache bug. It is about understanding that every layer of caching introduces a consistency gap, and that gap must be actively closed — not assumed away.

**The three failure modes**:

1. Cache was never invalidated on write (write-through fixes it)
2. Cache invalidation hit a stale replica (session affinity + version stamps fix it)
3. Cache invalidation was silently lost (event-driven + outbox pattern + TTL safety net fix it)

**The winning architecture**: event-driven invalidation with an outbox pattern as the primary mechanism, short TTL as the safety net, cross-region event replication for geo-distributed setups, and monitoring that catches invalidation failures before users do.

The hardest part of cache invalidation is not the technology. It is accepting that caches are copies of truth, not truth themselves. Once you design for cache failures rather than assuming they will not happen, the system becomes resilient instead of fragile.
