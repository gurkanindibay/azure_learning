---
type: System Design
title: "WhatsApp Duplicate Messages — At-Least-Once Delivery & Idempotency"
description: "Three-layer deduplication strategy, idempotency key pattern, and monitoring for duplicate message detection in distributed messaging systems."
generated: { by: process:okf-migrate, at: 2026-07-18T21:52:51Z }
---

# 31. WhatsApp Duplicate Messages — At-Least-Once Delivery & Idempotency

> **Parent**: [Messaging & Event Streaming](index.md)
> **Source**: [Duplicate Messages in WhatsApp — System Design Interview Deep Dive on At-Least-Once Delivery and Idempotency](../../articles/messaging/whatsapp-duplicate-messages-at-least-once-delivery-idempotency.md)
> **Purpose**: Three-layer deduplication architecture for messaging platforms: client-generated idempotency keys, server-side unique constraints, and receiver-side dedup caches.

> **Also see**: [Kafka Producer Ack & Idempotency](kafka-producer-ack-idempotency.md), [Real-Time Messaging](real-time-messaging.md)
> **Dictionary**: [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [At-Least-Once Delivery](../../reference-dictionary/messaging.md#at-least-once-delivery), [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq)
> **Taxonomy**: §3.3 Event-Driven & Messaging

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| `broker-97` | Lost ACK causes server to retry delivery, user sees duplicate message | At-least-once delivery is the foundation — duplicates are inevitable in unreliable networks |
| `broker-98` | Client-side dedup alone breaks when sender retries or user switches devices | Three-layer dedup: client (idempotency key) → server (unique constraint) → receiver (seen-ID cache) |
| `broker-99` | Server inserts duplicate message if it doesn't check before storing | Message ID as primary key — duplicate inserts fail gracefully at the database level |
| `broker-100` | Server crashes after storing but before sending ACK | Distributed systems trilemma: exactly-once vs high availability vs low latency — pick two |
| `broker-101` | Users report duplicates before engineering detects the problem | Five monitoring signals: dedup cache hit rate, retry rate, ACK latency, duplicate insert attempts, dedup hit ratio |

---

## broker-97: At-Least-Once Delivery — Why Duplicates Are Inevitable

| | |
|:---|:---|
| **Problem** | The receiver's acknowledgment (ACK) is lost due to network failure. The server doesn't know if the message was delivered, so it retries — causing the receiver to see the same message twice. |
| **Root cause** | In a distributed system, networks are unreliable. The server cannot distinguish "ACK lost in transit" from "message never delivered." Retrying is the only safe path when outcome is unknown. |

**Strategy**: Accept that retries produce duplicates and build deduplication into every layer of the system. At-least-once delivery guarantees the message arrives; idempotency guarantees duplicates don't harm the user experience.

**Tradeoff**: At-least-once delivery trades exactly-once purity for availability. Without retries, messages would be silently lost during network partitions. With retries, duplicates are guaranteed but manageable through deduplication.

---

## broker-98: Three-Layer Deduplication Architecture

| | |
|:---|:---|
| **Problem** | A single layer of deduplication (e.g., client-only) fails when the sender retries due to timeout or when the user switches devices. Defense in depth is required. |
| **Root cause** | Each layer protects against a different failure mode. Client dedup catches re-display; server dedup catches re-insertion; receiver dedup catches re-delivery. |

**Strategy**: Implement three independent deduplication layers:

1. **Client-side**: Generate a unique message ID before sending. If the send times out, retry with the **same ID**. The client tracks sent IDs locally to avoid re-displaying already-sent messages.
2. **Server-side**: Use the message ID as a primary key or unique index. Duplicate INSERT attempts fail gracefully (or are detected via `ON CONFLICT DO NOTHING` / `INSERT IGNORE`). The server acknowledges without re-inserting.
3. **Receiver-side**: Maintain a short-lived LRU cache of recently processed message IDs with TTL (minutes, not hours). Old entries expire to save memory. WhatsApp uses a cursor-based approach: track the last received ID per conversation and ignore any message with ID ≤ last known ID.

**Tradeoff**: Three layers add implementation complexity and storage overhead (duplicate ID tracking at each tier), but they provide defense in depth — if one layer misses a duplicate, the next catches it. The receiver cache must balance TTL (too short → missed duplicates after reconnect; too long → memory pressure).

---

## broker-99: Idempotency Key Pattern — Message ID as Primary Key

| | |
|:---|:---|
| **Problem** | Without server-side idempotency, a client retrying the same message creates two database entries, which eventually propagate to the receiver as two distinct messages. |
| **Root cause** | The server treats each request independently instead of recognizing that two requests with the same message ID represent the same logical operation. |

**Strategy**: Make the message ID the database primary key (or put it in a unique constraint). When the server receives a duplicate, the INSERT fails deterministically. The server then acknowledges the duplicate without side effects.

```sql
-- Server-side idempotent insert
INSERT INTO messages (message_id, sender, receiver, content, timestamp)
VALUES (:msg_id, :sender, :receiver, :content, :ts)
ON CONFLICT (message_id) DO NOTHING;
-- Acknowledge to sender regardless of whether row was inserted
```

**Tradeoff**: This requires the client to generate globally unique IDs deterministically (UUIDv4, or hash of content + sender + timestamp). If the client generates different IDs for the same logical message, server dedup fails. The unique constraint also creates a write bottleneck if message_id is the clustering key in a distributed database.

---

## broker-100: Server Crash Between Store and ACK — The Distributed Systems Trilemma

| | |
|:---|:---|
| **Problem** | The server stores the message in the database, then crashes before sending the ACK to the client. The client retries with the same message ID. Without idempotency, this creates a duplicate. |
| **Root cause** | The store-and-ACK sequence is not atomic. A crash between the two operations leaves the system in an uncertain state. |

**Strategy**: The combination of idempotent server storage (broker-99) and client retry with the same ID (broker-98, layer 1) handles this scenario. When the client retries, the server's unique constraint prevents a second insert, and the ACK is returned on the retry.

For delivery to the receiver, the server maintains a **delivery cursor** per client — the last successfully delivered message ID. If the server crashes after storing a message but before incrementing the cursor, the receiver re-requests messages since the last known cursor position, and duplicates are caught by receiver-side dedup (broker-98, layer 3).

**Tradeoff**: This is the classic distributed systems trilemma. You can have at most two of: exactly-once delivery, high availability, or low latency. Real-world systems (WhatsApp, Telegram, Signal) choose high availability + low latency and accept that duplicates will occur, then use idempotency to make them harmless.

---

## broker-101: Monitoring Duplicate Deliveries Before Users Complain

| | |
|:---|:---|
| **Problem** | Duplicate deliveries are silent — they don't cause crashes or error logs. Without proactive monitoring, engineering only learns about the problem when users report it. |
| **Root cause** | Duplicates are handled gracefully (dedup cache hit → discard), which means they produce no error signal. The system appears healthy while delivering degraded UX. |

**Strategy**: Track five metrics to detect duplicate deliveries before users notice:

1. **Duplicate delivery rate** — Percentage of messages where the receiver's dedup cache hit. A healthy system should be under 0.1%. A spike suggests network instability or retry storms.
2. **Retry rate per server node** — Sudden increase on a single node suggests a network partition or degraded NIC. Uniform increase suggests a global issue.
3. **ACK timeout distribution (P95/P99)** — Rising tail latencies predict future retries. If P99 ACK time approaches the retry timeout threshold, nearly 1% of messages will retry.
4. **Duplicate insert attempts on server** — Count of `ON CONFLICT` hits on the message_id unique constraint. A rising trend means clients are retrying more aggressively.
5. **Dedup cache hit ratio on receiver** — Track hit ratio over a sliding window. A ratio consistently above 0.5% warrants investigation.

Alert threshold: if duplicate delivery rate crosses 1%, fire a warning. At 5%, fire a critical alert and investigate retry logic, network health, or dedup cache configuration.

**Tradeoff**: Metric collection adds operational overhead and storage cost. However, the cost of missing duplicate spikes (user churn, support tickets, reputational damage) far outweighs the monitoring cost. Exponential backoff with jitter on retries should also be instrumented — if backoff is not engaging, retry storms can cascade.
