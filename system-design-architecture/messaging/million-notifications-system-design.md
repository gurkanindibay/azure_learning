---
type: System Design
title: "Million Notifications System Design — Key Takeaways"
description: "System design patterns for large-scale push notification delivery: queue-based async processing, rate limiting, idempotency, batching, DLQs, worker autoscaling, and delivery tracking."
generated: { by: process:okf-migrate, at: 2026-07-16T00:00:00Z }
---

# 34. Million Notifications System Design — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [System Design Interview: Sending 1 Million Notifications Without Overwhelming Your Servers](../../articles/system-design-interview/million-notifications-system-design.md)
> **Purpose**: Extract reusable architectural patterns for designing large-scale notification delivery systems that handle spikey workloads without overwhelming application servers or downstream providers.

> **Also see**: [Message Brokers & Async](message-brokers-async.md), [Kafka Consumer Mistakes](kafka-consumer-mistakes.md)
> **Dictionary**: [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq), [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency), [Rate Limiting](../../reference-dictionary/api-design.md#rate-limiting), [Backpressure](../../reference-dictionary/messaging.md#backpressure)
> **Azure Services**: [Azure Service Bus](../azure-service-mapping/), [Event Hubs](../../architecture-azure/integration/event-hubs/), [Azure Functions](../../architecture-azure/compute/azure-functions/)

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`broker-90`](#broker-90-synchronous-notification-sending-overwhelms-servers) | Synchronous Notification Sending Overwhelms Servers | Decouple generation from delivery with a queue |
| [`broker-91`](#broker-91-downstream-provider-rate-limiting-blocks-workers) | Downstream Provider Rate Limiting Blocks Workers | Rate-limit at the worker layer, not the queue |
| [`broker-92`](#broker-92-worker-crash-after-send-causes-duplicate-delivery) | Worker Crash After Send Causes Duplicate Delivery | Idempotent processing with unique notification IDs |
| [`broker-93`](#broker-93-one-million-api-calls-for-one-million-notifications) | One Million API Calls for One Million Notifications | Batch multiple notifications per API request |
| [`broker-94`](#broker-94-continuously-failing-notifications-clog-the-queue) | Continuously Failing Notifications Clog the Queue | Dead Letter Queue with bounded retries |
| [`broker-95`](#broker-95-hundred-million-user-campaigns-flood-kafka) | Hundred-Million-User Campaigns Flood Kafka | Separate campaign definition from notification generation |
| [`broker-96`](#broker-96-marketing-demands-delivery-tracking-analytics) | Marketing Demands Delivery Tracking Analytics | Async event processing for delivery callbacks |

---

## broker-90: Synchronous Notification Sending Overwhelms Servers

| | |
|:---|:---|
| **Problem** | Sending notifications synchronously inside a request handler ties notification delivery to the application server. At scale (1M notifications), request threads block, memory spikes, CPU explodes, timeouts increase, and the application becomes unavailable. |
| **Root cause** | Notification generation and notification delivery are coupled — the API waits for the provider to confirm each send before returning. |

**Strategy**: Decouple notification generation from delivery. The API creates notification jobs and places them into a queue. Worker services process them asynchronously at a controlled rate. The queue acts as a buffer, absorbing traffic spikes so the application layer stays lightweight.

**Tradeoff**: Adds infrastructure complexity (queue, worker fleet) and eventual-consistency semantics. Users won't get instant confirmation that their notification was sent — they get confirmation that it was accepted. This is almost always the right tradeoff at scale.

---

## broker-91: Downstream Provider Rate Limiting Blocks Workers

| | |
|:---|:---|
| **Problem** | Workers process from the queue as fast as they can, but downstream providers (Firebase, APNs, email gateways) have rate limits. The bottleneck shifts from your servers to the provider. |
| **Root cause** | The system is constrained by the notification provider's throughput, not by worker capacity. |

**Strategy**: Introduce rate limiting at the worker layer. Even if the queue holds 1M messages, workers send only at the rate the provider can handle. The queue absorbs the resulting backlog — a growing queue is often safer than overwhelming a dependency.

**Tradeoff**: Creates a deliberate backlog in the queue, increasing end-to-end latency. This is acceptable for most notification use cases where delivery within seconds is sufficient. For real-time requirements, you need more provider capacity or multi-provider fan-out.

---

## broker-92: Worker Crash After Send Causes Duplicate Delivery

| | |
|:---|:---|
| **Problem** | A worker sends a notification successfully but crashes before acknowledging the message. The queue redelivers it, and the notification is sent twice. |
| **Root cause** | The "at-least-once" delivery semantic of most message queues — redelivery is inevitable when acknowledgments are lost. |

**Strategy**: Make notification processing idempotent. Assign every notification a unique ID (e.g., `NOTIF-1001`). Before sending, insert the ID into a `processed_notifications` table with a unique constraint. If the insert succeeds, send the notification. If it fails (duplicate key), the notification was already processed — skip it.

**Tradeoff**: Adds a database write per notification. For batch-capable providers, the dedup store can be checked once per batch rather than per message. This is the same pattern used in payment systems — retries are inevitable; the goal is making them harmless.

---

## broker-93: One Million API Calls for One Million Notifications

| | |
|:---|:---|
| **Problem** | If each notification requires a separate API call to the provider, 1M notifications means 1M API requests — high network overhead, increased latency, and more opportunities for transient failures. |
| **Root cause** | Per-message API calls don't leverage provider batch support. |

**Strategy**: Use batch APIs whenever the provider supports them. Instead of 1 request = 1 notification, send 1 request = 500 notifications. This reduces 1M requests to 2K requests, dramatically cutting network overhead and failure surface.

**Tradeoff**: Batch APIs may have different error semantics — a single failure in a batch might fail the entire batch. Requires batching logic that handles partial failures, or choosing batch sizes small enough that retrying the whole batch is acceptable.

---

## broker-94: Continuously Failing Notifications Clog the Queue

| | |
|:---|:---|
| **Problem** | Notifications with invalid device tokens, bad email addresses, or provider-rejected payloads will fail on every retry. Retrying forever wastes worker capacity and clogs the queue. |
| **Root cause** | Indistinguishable treatment of transient failures (network blips) and permanent failures (invalid data). |

**Strategy**: Use a Dead Letter Queue (DLQ) with bounded retries. After N failed attempts (with exponential backoff), move the message to a DLQ. Operations teams can inspect the DLQ, fix systemic issues, and replay or discard messages.

**Tradeoff**: Messages in the DLQ are not delivered until manual intervention. For notifications, this is acceptable — a permanently undeliverable notification should not block deliverable ones. Requires operational runbooks for DLQ inspection and replay.

---

## broker-95: Hundred-Million-User Campaigns Flood Kafka

| | |
|:---|:---|
| **Problem** | A campaign targeting 100M users would require placing 100M messages directly into Kafka. Generating all messages at once floods the broker with hundreds of millions of records and may exceed topic capacity. |
| **Root cause** | Campaign definition and notification generation are coupled — the trigger immediately materializes all notification jobs. |

**Strategy**: Separate campaign definition from notification generation. Store the campaign definition (targeting criteria, template, schedule) separately. A generator service progressively creates notification jobs over time, controlling the rate at which messages enter the queue. This avoids flooding the broker.

**Tradeoff**: Adds latency — the last user in a 100M campaign gets their notification later than the first. For marketing campaigns, this is acceptable. For time-critical alerts, you may need a tiered approach: high-priority notifications bypass the progressive generator.

---

## broker-96: Marketing Demands Delivery Tracking Analytics

| | |
|:---|:---|
| **Problem** | Marketing needs real-time analytics: sent, delivered, opened, failed counts. Adding tracking to the notification delivery path couples analytics to delivery and risks affecting throughput. |
| **Root cause** | Mixing the delivery critical path with analytics processing — if analytics slows down, delivery slows down. |

**Strategy**: Process notification provider callbacks asynchronously as separate events. Providers emit webhooks/callbacks for delivery status changes. Route these to a separate event pipeline that updates analytics stores independently from the notification delivery path.

**Tradeoff**: Analytics are eventually consistent with delivery — there's a small window where a notification was delivered but analytics doesn't yet reflect it. This is acceptable for marketing dashboards; the delivery path stays fast and decoupled.
