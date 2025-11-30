# Azure Service Bus Detailed Reference

## Table of Contents
- [1. Overview](#1-overview)
- [2. Core Concepts](#2-core-concepts)
  - [Queues](#queues)
  - [Topics and Subscriptions](#topics-and-subscriptions)
- [2.1. Queue vs Topic Usage Guidelines](#21-queue-vs-topic-usage-guidelines)
  - [When to Use Queues (Point-to-Point)](#when-to-use-queues-point-to-point)
  - [When to Use Topics (Publish-Subscribe)](#when-to-use-topics-publish-subscribe)
  - [Decision Matrix](#decision-matrix)
  - [Hybrid Patterns](#hybrid-patterns)
  - [Performance Considerations](#performance-considerations)
  - [Cost Implications](#cost-implications)
  - [Filter Usage in Topics](#filter-usage-in-topics)
- [2.2. Message Routing Patterns](#22-message-routing-patterns)
  - [Simple Request/Reply](#simple-requestreply)
  - [Multicast Request/Reply](#multicast-requestreply-)
  - [Multiplexing (Session-Based)](#multiplexing-session-based)
  - [Multiplexed Request/Reply](#multiplexed-requestreply)
  - [Pattern Comparison Matrix](#pattern-comparison-matrix)
  - [Choosing the Right Pattern](#choosing-the-right-pattern)
  - [Exam Key Points](#exam-key-points)
- [3. Advanced Features](#3-advanced-features)
  - [Dead-Letter Queues (DLQ)](#dead-letter-queues-dlq)
  - [Message Sessions (FIFO)](#message-sessions-fifo)
  - [Transactions](#transactions)
  - [Duplicate Detection](#duplicate-detection)
  - [Scheduled Delivery](#scheduled-delivery)
- [4. Data Integration Model: Push-Pull (Hybrid)](#4-data-integration-model-push-pull-hybrid)
  - [Publisher Side (Push)](#publisher-side-push)
  - [Consumer Side (Pull with Push Characteristics)](#consumer-side-pull-with-push-characteristics)
  - [Benefits](#benefits)
  - [Considerations](#considerations)
- [5. Tiers](#5-tiers)
- [6. Best Practices](#6-best-practices)

## 1. Overview
Azure Service Bus is a fully managed enterprise message broker with message queues and publish-subscribe topics. It is used to decouple applications and services.

- **Primary Use Case:** High-value enterprise messaging, order processing, financial transactions.
- **Protocol Support:** AMQP, SBMP, HTTP.

## 2. Core Concepts

### Queues
- **Model:** Point-to-point communication.
- **Behavior:** Sender sends a message; Receiver pulls it. Once processed, the message is removed.
- **Benefit:** Load leveling (producer produces faster than consumer can process).

### Topics and Subscriptions
- **Model:** Publish/Subscribe.
- **Behavior:** Sender sends to a Topic. Multiple Subscriptions can exist. Each subscription gets a copy of the message (potentially filtered).
- **Filters:** SQL Filters or Correlation Filters determine which messages end up in which subscription.

## 2.1. Queue vs Topic Usage Guidelines

### When to Use Queues (Point-to-Point)

#### ✅ Use Queues When:
- **Single Consumer Processing:** Only one consumer should process each message
- **Load Distribution:** Multiple consumers competing for work (competing consumer pattern)
- **Command Processing:** Executing specific actions or commands
- **Work Queue Pattern:** Background job processing
- **Order Processing:** Sequential processing by single consumer type
- **Resource-Intensive Tasks:** Tasks that should not be duplicated

#### Queue Use Cases:
```
📋 Order Processing System
Producer: E-commerce website
Consumer: Order fulfillment service
Reason: Each order should be processed exactly once

📋 Image Processing Queue
Producer: Upload service
Consumer: Image resize workers (multiple instances)
Reason: Only one worker should process each image

📋 Email Queue
Producer: Application events
Consumer: Email service
Reason: Each email should be sent exactly once

📋 Payment Processing
Producer: Checkout service
Consumer: Payment processor
Reason: Critical that payments aren't duplicated
```

### When to Use Topics (Publish-Subscribe)

#### ✅ Use Topics When:
- **Multiple Consumer Types:** Different services need the same message
- **Event Broadcasting:** Notifying multiple systems about events
- **Fan-Out Pattern:** One message triggers multiple workflows
- **Audit/Logging:** Multiple systems need to log the same event
- **Microservices Communication:** Event-driven architecture
- **Business Event Propagation:** Domain events affecting multiple bounded contexts

#### Topic Use Cases:
```
📢 User Registration Event
Publisher: User service
Subscribers: 
  - Email service (welcome email)
  - Analytics service (track signup)
  - CRM service (create lead)
  - Notification service (admin alert)
Reason: Single event triggers multiple workflows

📢 Order Status Changed
Publisher: Order service
Subscribers:
  - Inventory service (update stock)
  - Shipping service (prepare shipment)
  - Customer service (send notification)
  - Analytics service (track metrics)
Reason: Multiple systems react to order changes

📢 Payment Completed
Publisher: Payment service
Subscribers:
  - Order service (update status)
  - Invoice service (generate receipt)
  - Loyalty service (award points)
  - Fraud service (analyze patterns)
Reason: Payment completion affects multiple domains
```

### Decision Matrix

| Scenario | Queue | Topic | Reason |
|----------|-------|-------|--------|
| Process each message exactly once | ✅ | ❌ | Queues ensure single consumption |
| Multiple services need same data | ❌ | ✅ | Topics broadcast to all subscribers |
| Load balancing across workers | ✅ | ❌ | Queue distributes work among consumers |
| Event-driven microservices | ❌ | ✅ | Topics enable loose coupling |
| Critical business transactions | ✅ | ❌ | Queues prevent duplicate processing |
| Audit trail requirements | ❌ | ✅ | Topics allow multiple audit consumers |
| Background job processing | ✅ | ❌ | Queues manage work distribution |
| System integration events | ❌ | ✅ | Topics enable system decoupling |

### Hybrid Patterns

#### Queue → Topic Chain
```
1. Critical processing via Queue (ensures single processing)
2. Success event published to Topic (notifies other systems)

Example:
[Order] → Queue → [Payment Processor] → Topic → [Multiple Services]
```

#### Topic → Queue Fan-Out
```
1. Event published to Topic
2. Each subscriber has its own Queue for reliable processing

Example:
[User Event] → Topic → Multiple Queues → [Dedicated Workers]
```

### Performance Considerations

#### Queues
- **Throughput:** Higher for single consumer scenarios
- **Latency:** Lower overhead, direct message delivery
- **Scaling:** Scale by adding competing consumers
- **Resource Usage:** Lower memory footprint

#### Topics
- **Throughput:** Depends on number of subscriptions
- **Latency:** Slight overhead for message copying
- **Scaling:** Scale by managing subscription filters
- **Resource Usage:** Higher due to message duplication

### Cost Implications

#### Queues
- **Messages:** Pay per message operation
- **Storage:** Pay for message storage duration
- **Connections:** Fewer connections needed

#### Topics
- **Messages:** Pay per message × number of subscriptions
- **Storage:** Higher storage costs due to copies
- **Connections:** More connections for multiple subscribers

### Filter Usage in Topics

#### SQL Filters
```sql
-- Route by message properties
Region = 'US' AND Priority > 5

-- Route by custom properties
EventType = 'OrderCreated' AND Amount > 1000

-- Complex routing logic
CustomerTier IN ('Gold', 'Platinum') AND EventSource = 'WebApp'
```

#### Correlation Filters (Performance Optimized)
```
-- Simple property matching (faster than SQL)
CorrelationId = 'user-events'
Label = 'high-priority'
ContentType = 'application/json'
```

## 2.2. Message Routing Patterns

Azure Service Bus supports several message routing patterns for different communication scenarios:

### Simple Request/Reply
- **Model:** One-to-one communication with response.
- **Mechanism:** Publisher sends message to a queue, consumer processes it and sends reply to a dedicated reply queue.
- **Use Case:** Synchronous-like communication in asynchronous messaging systems.
- **Limitation:** Single consumer processes each message; multiple subscribers cannot consume the same message.

```
[Publisher] → Queue → [Consumer] → Reply Queue → [Publisher]
```

**Example:**
```
Order Service → Order Queue → Payment Processor → Reply Queue → Order Service
```

### Multicast Request/Reply ✅
- **Model:** One-to-many communication pattern with optional responses.
- **Mechanism:** Publisher sends message to a **Topic**, multiple subscribers with different subscriptions can consume the message. Each subscriber can optionally send a reply back to the publisher.
- **Use Case:** Broadcasting requests or events where multiple services need to process and potentially respond independently.
- **Key Feature:** Multiple subscribers become eligible to consume the message simultaneously, and each can send their own reply.

```
                                      ┌→ [Subscription 1] → [Consumer 1] → Reply Queue 1 ┐
[Publisher] → Topic (Request Message) ├→ [Subscription 2] → [Consumer 2] → Reply Queue 2 ├→ [Publisher receives replies]
                                      └→ [Subscription 3] → [Consumer 3] → Reply Queue 3 ┘
```

**Example:**
```
                                       ┌─ Inventory Service ─ Inventory Reply ─┐
Order Service ─→ Order Status Topic ─→ ├─ Shipping Service ─ Shipping Reply ───├─→ Order Service (aggregates)
                                       └─ Payment Service ── Payment Reply ────┘
```

**When to Use:**
- Need to notify multiple independent services about an event
- Each service may respond differently to the same message
- Loose coupling between publisher and multiple consumers required

### Multiplexing (Session-Based)
- **Model:** Multiple streams of related messages through a single queue.
- **Mechanism:** Uses **Message Sessions** to group related messages by `SessionId`.
- **Use Case:** Processing ordered sequences of related messages (e.g., all orders for a specific customer).
- **Limitation:** Only one consumer can lock a session at a time; multiple subscribers cannot consume the same session messages.

```
[Publisher A] → SessionId: User1 → Queue → [Consumer locks User1 session]
[Publisher B] → SessionId: User2 → Queue → [Consumer locks User2 session]
[Publisher C] → SessionId: User3 → Queue → [Consumer locks User3 session]
```

**Example:**
```
Multiple Order Sources → Order Queue (with SessionId per customer) → Worker processes all orders for one customer in sequence
```

**Session Benefits:**
- FIFO guarantee within a session
- State management per session
- Prevents processing of related messages out of order

### Multiplexed Request/Reply
- **Model:** Multiple publishers sharing a single reply queue.
- **Mechanism:** Publishers send messages with unique `ReplyToSessionId` or `CorrelationId`, allowing them to share a common reply queue.
- **Use Case:** Efficient resource usage when many publishers need responses but don't want individual reply queues.
- **Limitation:** Messages cannot be consumed by multiple subscribers; each reply goes to the original requester.

```
[Publisher A] → Request Queue → [Consumer] → Shared Reply Queue → [Publisher A receives its reply]
[Publisher B] → Request Queue → [Consumer] → Shared Reply Queue → [Publisher B receives its reply]
[Publisher C] → Request Queue → [Consumer] → Shared Reply Queue → [Publisher C receives its reply]
```

**Example:**
```
Multiple Microservices → Payment Processing Queue → Payment Processor → Shared Reply Queue → Each service gets its own reply
```

**Implementation Details:**
- Use `CorrelationId` to match requests with replies
- Use `ReplyToSessionId` for session-based reply routing
- More efficient than creating separate reply queues per publisher

### Pattern Comparison Matrix

| Pattern | Multiple Consumers | Reply Support | Sessions Required | Primary Entity |
|---------|-------------------|---------------|-------------------|----------------|
| Simple Request/Reply | ❌ No | ✅ Yes | ❌ No | Queue |
| Multicast Request/Reply | ✅ Yes | ✅ Yes (optional) | ❌ No | **Topic** |
| Multiplexing | ❌ No (per session) | ❌ No | ✅ Yes | Queue |
| Multiplexed Request/Reply | ❌ No | ✅ Yes | ✅ Optional | Queue |

### Choosing the Right Pattern

#### Use Multicast Request/Reply When:
- ✅ Multiple independent services need to process the same message
- ✅ Broadcasting events to multiple subscribers
- ✅ Fan-out scenarios where one event triggers multiple workflows
- ✅ Event-driven microservices architecture

#### Use Simple Request/Reply When:
- ✅ One-to-one communication with expected response
- ✅ Single service should process each request
- ✅ Synchronous-like behavior needed

#### Use Multiplexing When:
- ✅ Need to process related messages in order (FIFO)
- ✅ Grouping messages by entity (customer, order, user)
- ✅ State management required per message group
- ✅ Single queue serving multiple logical streams

#### Use Multiplexed Request/Reply When:
- ✅ Many publishers need replies but want to share infrastructure
- ✅ Optimizing resource usage (fewer queues)
- ✅ Publishers can identify their own replies via correlation

### Exam Key Points

**Question Pattern Recognition:**
> "Publisher can send messages into a **topic** and **multiple subscribers** can become eligible to consume the messages"

**Answer:** **Multicast Request/Reply**

**Why Other Options Are Wrong:**
- **Simple Request/Reply:** Uses queue, single consumer only
- **Multiplexing:** Single queue with sessions, cannot be consumed by multiple subscribers
- **Multiplexed Request/Reply:** Shared reply queue, but messages go to specific requesters, not multiple subscribers

## 3. Advanced Features

### Dead-Letter Queues (DLQ)
A sub-queue for holding messages that cannot be delivered or processed.
- **Reasons:** Max delivery count exceeded, TTL expired, filter evaluation exceptions, or explicit dead-lettering by consumer.

### Message Sessions (FIFO)
- **Function:** Guarantees ordered processing of unbounded sequences of related messages.
- **Mechanism:** Messages with the same `SessionId` are locked by a single receiver.

### Transactions
Supports atomic operations. You can send a message, delete a message, and update state within a single transaction scope.

### Duplicate Detection
Service Bus can automatically remove duplicate messages sent within a specific time window based on `MessageId`.

#### How It Works
- **MessageId Property:** When duplicate detection is enabled, Service Bus tracks the `MessageId` of all messages within a configurable time window (up to 7 days, default 10 minutes).
- **Automatic Deduplication:** If a message with the same `MessageId` is sent within the detection window, the duplicate is silently discarded.
- **Tier Requirement:** Available in Standard and Premium tiers only (not Basic).

#### Configuration

```bash
# Enable duplicate detection at queue creation
az servicebus queue create \
  --namespace-name mynamespace \
  --resource-group myResourceGroup \
  --name myqueue \
  --enable-duplicate-detection true \
  --duplicate-detection-history-time-window P1D  # 24 hours (ISO 8601 duration)
```

```csharp
// Send messages with duplicate detection
var sender = client.CreateSender("financial-transactions-queue");

// First message
var message1 = new ServiceBusMessage("Transaction data")
{
    MessageId = "txn-12345"  // TransactionId as MessageId
};
await sender.SendMessageAsync(message1);

// Duplicate message (same MessageId within detection window)
var message2 = new ServiceBusMessage("Transaction data")
{
    MessageId = "txn-12345"  // Same MessageId - will be silently dropped
};
await sender.SendMessageAsync(message2);  // No error, but message is discarded
```

#### Exam Scenario: Financial Transaction Duplicate Detection

**Scenario:** You are developing a solution that processes financial transactions using Azure Service Bus. The solution must ensure that duplicate transactions are automatically detected within a 24-hour window. Transaction messages contain a `TransactionId` property that uniquely identifies each transaction.

**Correct Answer:** Enable duplicate detection on the queue and set `MessageId` to the `TransactionId` value when sending messages.

**Why This Works:**
- Duplicate detection uses the `MessageId` property to identify duplicates
- Configure detection window to 24 hours (`P1D` in ISO 8601 format)
- Duplicates are automatically discarded without any additional application logic

#### Common Misconceptions

| Approach | Why It's Wrong |
|----------|----------------|
| **Enable sessions and set SessionId to TransactionId** | Sessions are for message ordering and stateful processing, not duplicate detection. Setting SessionId creates separate sessions per transaction instead of detecting duplicates. |
| **Enable dead-lettering and check for duplicates** | Dead-lettering handles failed messages, not duplicates. Messages go to DLQ after processing failures, not when duplicates are detected. |
| **Enable autoforwarding for duplicate checking** | Autoforwarding chains queues/subscriptions for routing, not deduplication. Would require custom logic rather than built-in detection. |

#### Best Practices
- Always set a meaningful `MessageId` based on your business identifier (e.g., TransactionId, OrderId)
- Configure appropriate detection window based on your retry/failure scenarios
- Remember that duplicate detection must be enabled at queue/topic creation time
- Use idempotent message processing as a complementary strategy

### Scheduled Delivery
Messages can be sent to a queue/topic but remain invisible to consumers until a specific scheduled time.

## 4. Data Integration Model: Push-Pull (Hybrid)

Service Bus follows a **hybrid push-pull** delivery model:

### Publisher Side (Push)
- **Senders actively push messages** to Service Bus queues or topics.
- Messages are sent via AMQP, SBMP, or HTTP protocols.
- Messages are immediately persisted in the queue/topic.
- Sender receives acknowledgment once the message is stored.

### Consumer Side (Pull with Push Characteristics)
- **Receivers pull messages**, but with push-like behavior through long polling.
- Two receive modes:
  - **Peek-Lock (default):** Message is locked for processing, must be explicitly completed or abandoned.
  - **Receive-and-Delete:** Message is immediately removed upon receipt.
- Service Bus supports **message sessions** for ordered, FIFO processing.
- Consumers can use **event-driven listeners** (SDK abstractions) that continuously poll but appear like push.

### Benefits
- **Guaranteed delivery:** Messages persist until explicitly completed.
- **Order preservation:** Sessions guarantee FIFO within a session.
- **Load leveling:** Queue acts as buffer between fast producers and slow consumers.
- **Transactional support:** Atomic operations across multiple messages.

### Considerations
- Consumers must actively receive messages (even with SDK abstractions).
- Message lock duration limits processing time (renewable).
- Dead-letter queue requires explicit handling and monitoring.
- More complex than Event Grid but offers stronger guarantees.

## 5. Tiers
- **Basic:** Queues only, no topics.
- **Standard:** Queues & Topics, variable latency, shared resources.
- **Premium:** Dedicated resources (Messaging Units), predictable latency, support for large messages (up to 100 MB), VNET integration.

## 6. Best Practices
- **Peek-Lock vs Receive-and-Delete:** Always use Peek-Lock for reliability (default). It allows abandoning the message if processing fails.
- **Prefetch Count:** Increase prefetch count for high throughput scenarios to reduce round-trips.
- **Exception Handling:** Handle `MessageLockLostException` (processing took too long) and `ServiceBusException` (transient errors).
