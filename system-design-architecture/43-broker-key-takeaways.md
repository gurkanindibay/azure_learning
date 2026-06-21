---
type: System Design
title: "Real-Time Messaging — Key Takeaways"
description: "Reusable architectural patterns from designing a global real-time messaging platform: per-conversation Kafka partitioning, per-device Redis Streams inboxes, fan-out strategies, presence, multi-device sync, and reconnection safety."
timestamp: 2026-06-21T00:00:00Z
---

# 43. Real-Time Messaging — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [Question 1: Design a Real-Time Messaging System (like WhatsApp)](../articles/medium/part-3-real-time-messaging-system-design.md)
> **Purpose**: Extract reusable messaging and streaming patterns from a global chat-system design.

> **Also see**: [Message Brokers & Async](05-message-brokers-async.md), [Caching Architecture](03-caching-architecture.md)
> **Dictionary**: [Messaging](../reference-dictionary/messaging.md), [Caching](../reference-dictionary/caching.md), [Data & Concurrency](../reference-dictionary/data-concurrency.md)
> **Taxonomy Reference**: §3 Integration & Communication Architecture, §4.3 Streaming & Real-Time Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [broker-18](#broker-18) | Messages in a chat must stay in order without global coordination | Per-conversation Kafka partitioning keyed by `conversation_id` |
| [broker-19](#broker-19) | Offline devices need durable, individually trackable delivery queues | Per-device Redis Streams inbox with consumer-group ACK |
| [broker-20](#broker-20) | Group messages fan out to many recipients; write amplification vs read latency | Fan-out on write for small groups, fan-out on read for large groups |
| [broker-21](#broker-21) | Users need to know who is online and where their connection lives | Presence service backed by Redis TTL + heartbeats |
| [broker-22](#broker-22) | A user’s phone, laptop, and tablet must show the same conversation order | All devices consume the same ordered, durable message stream |
| [broker-23](#broker-23) | A region-wide reconnect can overwhelm chat servers and databases | Jittered backoff, rate limiting, and warm caches on reconnect |

---

## broker-18: Per-Conversation Kafka Partitioning

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | A chat requires strict ordering per conversation, but global ordering across all chats is unnecessary and would serialize the entire system. |
| **Root cause** | Ordering guarantees in a partitioned log are only valid within a single partition; routing every chat to its own partition gives ordering without global coordination. |

**Strategy**: Hash `conversation_id` to a fixed pool of Kafka partitions (e.g., 256). The producer uses the conversation ID as the partition key so every message for that conversation lands on the same partition. Within the partition, Kafka preserves append order.

```
Partition = abs(hash(conversation_id)) % total_partitions
```

| Tradeoff | Detail |
|:---|:---|
| **Ordering** | Strict per conversation; no global order. |
| **Scalability** | Fixed partition count avoids partition sprawl at billions of conversations. |
| **Hot partition risk** | A viral group chat can still saturate one partition; monitor partition-level throughput. |

> **Also see**: [broker-04 Message Ordering](05-message-brokers-async.md#broker-04-message-ordering)
> **Dictionary**: [Partition](../reference-dictionary/messaging.md#partition), [Message Ordering](../reference-dictionary/messaging.md#message-ordering), [Consistent Hashing](../reference-dictionary/api-design.md#consistent-hashing)
> **Azure**: Event Hubs supports partition keys for per-entity ordering; Service Bus sessions enforce FIFO per session ID.

---

## broker-19: Per-Device Redis Streams Inbox

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | Online users need instant delivery; offline users need a durable queue they can replay when they reconnect, with per-device progress. |
| **Root cause** | A single broadcast topic cannot track which device has consumed which message or survive a consumer restart. |

**Strategy**: After Kafka accepts a message, a fan-out worker writes a lightweight message summary to a Redis Stream per device (`inbox:{user_id}:{device_id}`). Each device consumes its own stream with a consumer group, acknowledging entries after delivery. If a device is offline, entries remain in the stream; on reconnect it replays unacknowledged entries.

| Tradeoff | Detail |
|:---|:---|
| **Checkpoint granularity** | Per-device progress means each device can catch up independently. |
| **Memory cost** | Redis is not infinite; cap stream length or archive old entries to cold store. |
| **At-least-once** | Network flakes cause redelivery; clients deduplicate by `message_id`. |

> **Also see**: [Message Brokers & Async](05-message-brokers-async.md)
> **Dictionary**: [Redis Streams](../reference-dictionary/messaging.md#redis-streams), [Per-Device Inbox](../reference-dictionary/messaging.md#per-device-inbox), [At-Least-Once Semantics](../reference-dictionary/messaging.md#at-least-once-semantics)
> **Azure**: Azure Cache for Redis supports Redis Streams; combine with Event Hubs for the durable ordered log.

---

## broker-20: Fan-Out on Write vs Fan-Out on Read

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | Group chats up to 256 members create a write-amplification vs read-latency tension. |
| **Root cause** | Writing a copy to every member’s inbox guarantees fast reads but multiplies writes; reading a shared group timeline avoids amplification but adds latency on every read. |

**Strategy**: Use a hybrid threshold. For small groups (under ~100 members), fan out on write to each member’s inbox — reads are O(1). For very large groups or channels, store one copy in a group timeline and fan out on read, possibly with a hot cache for active participants.

| Tradeoff | Detail |
|:---|:---|
| **Fan-out on write** | Fast reads, higher write load, more storage. |
| **Fan-out on read** | Lower write cost, higher and less predictable read latency. |
| **Hybrid threshold** | Choose based on group size distribution and read/write ratio. |

> **Also see**: [feed-01 Hybrid Fanout](42-feed-key-takeaways.md#feed-01-hybrid-fanout-to-control-write-amplification)
> **Dictionary**: [Fanout on Write](../reference-dictionary/architecture-patterns.md#fanout-on-write), [Fanout on Read](../reference-dictionary/architecture-patterns.md#fanout-on-read), [Hybrid Fanout](../reference-dictionary/architecture-patterns.md#hybrid-fanout)
> **Azure**: Cosmos DB change feed can push group messages to per-member materialized views; Azure Cache for Redis stores hot timelines.

---

## broker-21: Presence Service with TTL + Heartbeats

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | The system must know which chat server holds a user’s connection and whether the user is online. |
| **Root cause** | WebSocket connections are long-lived and mobile clients disconnect unpredictably; a central registry must tolerate flaky networks. |

**Strategy**: Store presence in a Redis Hash keyed by user, mapping each device to `(chat_server_id, status, last_seen)`. Refresh the TTL on every heartbeat or WebSocket pong; if a client disappears, the entry expires and the user is marked offline. On reconnect, the registry is updated and pending messages are pushed.

| Tradeoff | Detail |
|:---|:---|
| **TTL vs heartbeat frequency** | Shorter TTL gives fresher presence but more heartbeat traffic. |
| **False negatives** | A temporary network blip can mark a user offline; clients should tolerate short transitions. |
| **Thundering herd** | Mass reconnects can hammer the presence store; use jittered reconnection and request coalescing. |

> **Also see**: [broker-23 Reconnection Thundering Herd](#broker-23)
> **Dictionary**: [Presence Service](../reference-dictionary/architecture-patterns.md#presence-service)
> **Azure**: Azure Cache for Redis with TTL keys; front with regional caches to reduce round trips.

---

## broker-22: Multi-Device Sync via Shared Ordered Stream

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | A user logged in on five devices must see the same messages in the same order everywhere. |
| **Root cause** | Each device is an independent consumer with its own network conditions and local clock. |

**Strategy**: Treat the Kafka log (partitioned by conversation) as the single source of truth. The server assigns a monotonic server timestamp and message ID. Every device reads from the same durable stream, so ordering is identical across devices. Eventual cross-device lag is acceptable as long as per-conversation order is preserved.

| Tradeoff | Detail |
|:---|:---|
| **Source of truth** | The broker log, not the client clock, defines order. |
| **Eventual device sync** | A device may lag milliseconds behind another; UI should not jump. |
| **Causal consistency** | Replies are ordered after the messages they reference within a conversation. |

> **Also see**: [Message Ordering](05-message-brokers-async.md#broker-04-message-ordering)
> **Dictionary**: [Causal Ordering](../reference-dictionary/data-concurrency.md#causal-ordering), [Message Ordering](../reference-dictionary/messaging.md#message-ordering)
> **Azure**: Event Hubs capture to Azure Storage lets late-joining devices replay the ordered log.

---

## broker-23: Reconnection Thundering Herd Mitigation

> **Source**: [Question 1: Design a Real-Time Messaging System](../articles/medium/part-3-real-time-messaging-system-design.md)

| | |
|:---|:---|
| **Problem** | When a region or chat-server fleet restarts, millions of clients reconnect simultaneously and can overload backends. |
| **Root cause** | Exponential backoff with the same base interval causes synchronized retry waves; databases also get hit for catch-up reads. |

**Strategy**: Combine jittered exponential backoff on the client, rate-limited connection admission on the gateway, and warm caches for presence and recent messages. Backfill offline messages from Redis Streams first; only fall back to Cassandra history for deep pagination.

| Tradeoff | Detail |
|:---|:---|
| **Jitter** | Desynchronizes clients but increases worst-case reconnect time. |
| **Rate admission** | Protects servers but may reject some clients temporarily. |
| **Cache-first catch-up** | Fast for recent messages; long history remains slower. |

> **Also see**: [cache-05 Request Coalescing](03-caching-architecture.md#cache-05-request-coalescing-in-flight-deduplication), [resilience-01 Retry Storms](10-resilience-patterns.md#resilience-01-otp-service-fails-during-peak-traffic)
> **Dictionary**: [Thundering Herd](../reference-dictionary/resilience.md#thundering-herd), [Request Coalescing](../reference-dictionary/caching.md#request-coalescing)
> **Azure**: Azure Front Door / API Management for connection shaping; Azure Cache for Redis for hot catch-up data.

---
