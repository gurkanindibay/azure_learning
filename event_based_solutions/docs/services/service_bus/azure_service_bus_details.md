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
  - [Message Deferral](#message-deferral)
- [4. Data Integration Model: Push-Pull (Hybrid)](#4-data-integration-model-push-pull-hybrid)
  - [Publisher Side (Push)](#publisher-side-push)
  - [Consumer Side (Pull with Push Characteristics)](#consumer-side-pull-with-push-characteristics)
  - [Benefits](#benefits)
  - [Considerations](#considerations)
- [5. Tiers](#5-tiers)
- [6. Exam Scenarios](#6-exam-scenarios)
  - [Exam Question 1: Selecting Technologies for Transactional, Duplicate-Free, Unlimited Storage Messaging](#exam-question-1-selecting-technologies-for-transactional-duplicate-free-unlimited-storage-messaging)
  - [Exam Question 2: FIFO Message Processing for Component Communication](#exam-question-2-fifo-message-processing-for-component-communication)
- [7. Best Practices](#7-best-practices)

## 1. Overview
Azure Service Bus is a fully managed enterprise message broker with message queues and publish-subscribe topics. It is used to decouple applications and services.

- **Primary Use Case:** High-value enterprise messaging, order processing, financial transactions.
- **Protocol Support:** AMQP, SBMP, HTTP.

## 2. Core Concepts

### Namespace
A **namespace** is the Service Bus instance itself — it is the top-level resource that you create in Azure. When you "create a Service Bus," you are creating a namespace.

- **Service Bus Instance:** The namespace represents the deployed Service Bus resource. There is no separate "Service Bus" resource; the namespace is the service.
- **Unique FQDN:** Each namespace provides a unique fully qualified domain name (e.g., `mynamespace.servicebus.windows.net`).
- **Container for Entities:** Holds all messaging entities including queues, topics, and subscriptions.
- **Management Boundary:** Serves as an administrative boundary for:
  - Access control (Shared Access Signatures, Azure AD/Entra ID)
  - Network isolation (Private endpoints, VNET integration in Premium)
  - Billing and resource allocation
  - Tier selection (Basic, Standard, Premium)
- **Connection Scope:** All client connections are established at the namespace level.
- **Transaction Boundary:** Transactions are scoped to a single namespace. You can perform atomic operations across multiple queues/topics within the same namespace, but **cross-namespace transactions are not supported**.

```csharp
// Transaction example - all operations within same namespace
await using var client = new ServiceBusClient(connectionString);

using (var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
{
    // Send to queue1 in namespace
    var sender1 = client.CreateSender("queue1");
    await sender1.SendMessageAsync(new ServiceBusMessage("Message 1"));
    
    // Send to queue2 in same namespace - included in transaction
    var sender2 = client.CreateSender("queue2");
    await sender2.SendMessageAsync(new ServiceBusMessage("Message 2"));
    
    scope.Complete(); // Both messages committed atomically
}
```

```bash
# Create a Service Bus namespace
az servicebus namespace create \
  --name mynamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard
```

**Key Points:**
- Namespace name must be globally unique across Azure
- Tier (SKU) is set at namespace level and applies to all entities within
- Premium tier provides dedicated resources (Messaging Units) per namespace
- Each namespace is isolated from others, providing security and resource boundaries

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

#### Key Characteristics
- **Subqueue Structure:** Dead-letter queues are **not separate entities** but **subqueues of the original queue**. Each queue (and each topic subscription) has its own associated dead-letter queue.
  
  > **What is a Subqueue?** A subqueue is a secondary queue that exists within the context of a parent queue. Unlike regular queues that are created explicitly as top-level entities in a namespace, subqueues are automatically created and managed by Service Bus as part of the parent queue. They share the same namespace and are accessed through the parent queue's path with a special suffix (e.g., `/$deadletterqueue`). Subqueues cannot exist independently—they are always tied to their parent queue's lifecycle.
- **Naming Convention:** The dead-letter queue has a special endpoint: `<queuename>/$deadletterqueue` (e.g., `orders/$deadletterqueue`).
- **Parent Relationship:** The original queue acts as the parent of the dead-letter subqueue.
- **Regular Queue Behavior:** Despite being a subqueue, the DLQ acts like any regular queue - you can receive, peek, and complete messages from it.

#### Reasons for Dead-Lettering
- **Max delivery count exceeded:** When a message fails processing repeatedly and exceeds the maximum delivery attempts configured for the queue.
- **TTL expired:** When a message's time-to-live expires before successful delivery.
- **Filter evaluation exceptions:** When subscription filter evaluation fails for a message.
- **Explicit dead-lettering:** When the consumer application explicitly dead-letters the message using the SDK.

#### Common Misconceptions
| Misconception | Reality |
|---------------|---------|
| Dead-letter queues are separate entities in the namespace | DLQs are subqueues of the original queue, not separate queues |
| Failed messages go to Event Hub | Service Bus doesn't automatically send failed messages to Event Hubs; dead-lettering is handled within Service Bus |
| Failed messages go to Azure Blob Storage | Service Bus doesn't automatically move messages to external storage |
| There's a shared dead-letter queue per namespace | Each queue/subscription has its own associated dead-letter queue |

#### Accessing Dead-Letter Queue

```csharp
// Access dead-letter queue using Azure.Messaging.ServiceBus SDK
var client = new ServiceBusClient(connectionString);

// Create receiver for dead-letter queue
var dlqReceiver = client.CreateReceiver("myqueue", 
    new ServiceBusReceiverOptions 
    { 
        SubQueue = SubQueue.DeadLetter 
    });

// Receive dead-lettered messages
var deadLetteredMessage = await dlqReceiver.ReceiveMessageAsync();

// Inspect dead-letter reason
var deadLetterReason = deadLetteredMessage.DeadLetterReason;
var deadLetterDescription = deadLetteredMessage.DeadLetterErrorDescription;
```

```bash
# View dead-letter queue messages using Azure CLI
az servicebus queue show \
  --namespace-name mynamespace \
  --resource-group myResourceGroup \
  --name myqueue \
  --query "countDetails.deadLetterMessageCount"
```

> **Important:** Messages remain in the dead-letter queue until explicitly processed by an application or tool. They are not automatically deleted or moved elsewhere.

### Message Sessions (FIFO)
- **Function:** Guarantees ordered processing of unbounded sequences of related messages.
- **Mechanism:** Messages with the same `SessionId` are locked by a single receiver.

#### Why Sessions are Required for FIFO

Azure Service Bus queues **do not guarantee FIFO ordering by default**. Standard message delivery follows a general order but can be affected by:
- Multiple competing consumers processing messages concurrently
- Message lock timeouts and redeliveries
- Service Bus internal partitioning and load balancing

**Sessions solve this** by:
1. Grouping messages with the same `SessionId` together
2. Ensuring only **one consumer** can lock and process a session at a time
3. Processing messages within a session strictly in the order they were enqueued

#### Enabling Sessions

```bash
# Create a session-enabled queue
az servicebus queue create \
  --namespace-name mynamespace \
  --resource-group myResourceGroup \
  --name myqueue \
  --enable-session true
```

```csharp
// Create queue with sessions enabled
var queueOptions = new CreateQueueOptions("order-processing-queue")
{
    RequiresSession = true  // Enable FIFO via sessions
};
await adminClient.CreateQueueAsync(queueOptions);
```

#### Sending Session Messages

```csharp
var sender = client.CreateSender("order-processing-queue");

// All messages for OrderId 12345 will be processed in order
var message1 = new ServiceBusMessage("Order created")
{
    SessionId = "Order-12345"
};
var message2 = new ServiceBusMessage("Payment received")
{
    SessionId = "Order-12345"
};
var message3 = new ServiceBusMessage("Order shipped")
{
    SessionId = "Order-12345"
};

await sender.SendMessagesAsync(new[] { message1, message2, message3 });
```

#### Receiving Session Messages

```csharp
// Accept a session and process messages in FIFO order
var sessionReceiver = await client.AcceptSessionAsync(
    "order-processing-queue", 
    "Order-12345");  // Specific session

// Or accept the next available session
var nextSessionReceiver = await client.AcceptNextSessionAsync(
    "order-processing-queue");

// Process messages - guaranteed FIFO within session
while (true)
{
    var message = await sessionReceiver.ReceiveMessageAsync(TimeSpan.FromSeconds(5));
    if (message == null) break;
    
    Console.WriteLine($"Processing: {message.Body}");
    await sessionReceiver.CompleteMessageAsync(message);
}
```

#### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Session Lock** | Only one receiver can process a session at a time |
| **FIFO Guarantee** | Messages within a session are processed in order |
| **Session State** | Arbitrary state (up to 256 KB) can be stored with a session |
| **Multiple Sessions** | Different sessions can be processed concurrently by different consumers |
| **Session Expiration** | Sessions expire when all messages are processed or lock times out |

#### Sessions vs Partitioning

| Feature | Sessions | Partitioning |
|---------|----------|---------------|
| **Purpose** | FIFO ordering | Throughput & availability |
| **FIFO Guarantee** | ✅ Yes (within session) | ❌ No |
| **Concurrent Consumers** | Per session | Across partitions |
| **Use Case** | Ordered processing | High-throughput scenarios |

> **Important:** Partitioning improves throughput and availability but **does not guarantee FIFO processing**. Partitioned queues distribute messages across multiple brokers, which may result in out-of-order delivery.

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

#### Methods for Scheduling Messages

There are two primary approaches to schedule messages in Azure Service Bus:

**1. ScheduleMessageAsync (Recommended for Cancellable Scheduling)**
```csharp
var sender = client.CreateSender("myqueue");
var message = new ServiceBusMessage("Process this in 2 hours");

// Schedule message to appear 2 hours from now
DateTimeOffset scheduledTime = DateTimeOffset.Now.AddHours(2);
long sequenceNumber = await sender.ScheduleMessageAsync(message, scheduledTime);

// Cancel the scheduled message if needed using the sequence number
await sender.CancelScheduledMessageAsync(sequenceNumber);
```

**2. ScheduledEnqueueTime Property with SendMessageAsync**
```csharp
var sender = client.CreateSender("myqueue");
var message = new ServiceBusMessage("Process this in 2 hours")
{
    ScheduledEnqueueTime = DateTimeOffset.Now.AddHours(2)
};

await sender.SendMessageAsync(message);
// Note: This does NOT return a sequence number for cancellation
```

#### Key Differences

| Method | Returns Sequence Number | Cancellation | Use Case |
|--------|------------------------|--------------|----------|
| `ScheduleMessageAsync` | ✅ Yes | Easy - use `CancelScheduledMessageAsync(sequenceNumber)` | When cancellation may be needed |
| `SendMessageAsync` with `ScheduledEnqueueTime` | ❌ No | Complex - must peek message to get sequence number | Fire-and-forget scheduling |

#### Common Misconceptions

| Approach | Why It's Wrong |
|----------|----------------|
| **SendMessageAsync with visibility timeout** | Service Bus doesn't support visibility timeout on send operations. This is an Azure Queue Storage concept, not applicable to Service Bus message scheduling. |
| **ServiceBusProcessor with delay configuration** | ServiceBusProcessor is for **receiving** messages, not for scheduling future message delivery. It cannot schedule messages to appear at a specific future time. |
| **ScheduledEnqueueTime for cancellable messages** | While this works for scheduling, you won't get back the sequence number, making cancellation more complex as you would need to peek the message to get the sequence number first. |

#### Best Practices
- Use `ScheduleMessageAsync` when you need the ability to cancel scheduled messages
- The returned sequence number should be stored if cancellation might be required
- Use `ScheduledEnqueueTime` property for simple fire-and-forget scheduled messages
- Both methods support scheduling messages to queues and topics

### Message Deferral
Message deferral allows a receiver to postpone processing of a message without losing it. When a message is deferred, it remains in the queue but is moved to a deferred state and can only be retrieved using its **sequence number**.

#### When to Use Deferral
- **Dependency Not Ready:** When processing depends on external data that is not yet available (e.g., inventory data unavailable for order processing).
- **Out-of-Order Messages:** When messages arrive out of sequence and you need to process them in a specific order.
- **Temporary Resource Unavailability:** When required resources are temporarily unavailable but expected to become available.

#### How Deferral Works

1. **Receive a message** using Peek-Lock mode
2. **Defer the message** if processing cannot proceed - this moves it to a deferred state
3. **Store the sequence number** - this is the **only way** to retrieve a deferred message later
4. **Retrieve the deferred message** using `ReceiveDeferredMessageAsync` with the stored sequence number

#### Code Example

```csharp
var client = new ServiceBusClient(connectionString);
var receiver = client.CreateReceiver("order-queue");

// Receive message
var message = await receiver.ReceiveMessageAsync();

// Check if inventory data is available
bool inventoryAvailable = await CheckInventoryDataAsync(message);

if (!inventoryAvailable)
{
    // Store the sequence number - REQUIRED for later retrieval
    long sequenceNumber = message.SequenceNumber;
    await StoreSequenceNumberAsync(sequenceNumber); // Persist this!
    
    // Defer the message
    await receiver.DeferMessageAsync(message);
    Console.WriteLine($"Message deferred. Sequence Number: {sequenceNumber}");
}
else
{
    // Process normally
    await ProcessOrderAsync(message);
    await receiver.CompleteMessageAsync(message);
}

// Later, when inventory data becomes available...
long storedSequenceNumber = await GetStoredSequenceNumberAsync();

// Retrieve the deferred message using the sequence number
ServiceBusReceivedMessage deferredMessage = await receiver.ReceiveDeferredMessageAsync(storedSequenceNumber);

// Process and complete
await ProcessOrderAsync(deferredMessage);
await receiver.CompleteMessageAsync(deferredMessage);
```

#### Key Point: What to Store for Retrieval

| Property | Can Retrieve Deferred Message? | Purpose |
|----------|-------------------------------|---------|
| **Sequence Number** | ✅ **YES** | The **only** way to directly retrieve a deferred message using `ReceiveDeferredMessageAsync` |
| Correlation ID | ❌ No | User-defined property for correlating related messages; cannot retrieve deferred messages |
| Lock Token | ❌ No | Used for renewing locks and completing messages; not for retrieving deferred messages |
| Session ID | ❌ No | Used for message sessions and grouping related messages; not for individual deferred messages |
| Message ID | ❌ No | Used for duplicate detection; cannot be used to retrieve deferred messages |

#### Exam Scenario: Order Processing with Inventory Check

**Scenario:** You have an Azure Service Bus queue that receives order messages. A message handler must defer processing when inventory data is unavailable. You need to implement message deferral and later retrieve the deferred message. What should you store to retrieve the deferred message?

**Correct Answer:** The message sequence number

**Why This Works:**
- To retrieve a deferred message, you **must** use the `ReceiveDeferredMessageAsync` method
- This method requires the **sequence number** as a parameter
- The sequence number is the **only** identifier that can directly access a deferred message

**Common Misconceptions:**

| Answer | Why It's Wrong |
|--------|----------------|
| **Correlation ID** | The correlation ID is a user-defined property for correlating related messages but **cannot** be used to retrieve deferred messages directly. |
| **Lock Token** | The lock token is used for renewing locks and completing messages but **cannot** be used to retrieve deferred messages from the queue. |
| **Session ID** | The session ID is used for message sessions and grouping related messages but is **not** used for retrieving individual deferred messages. |

#### Deferred vs Dead-Lettered Messages

| Aspect | Deferred Messages | Dead-Lettered Messages |
|--------|-------------------|------------------------|
| **Location** | Remain in the queue (deferred state) | Moved to dead-letter subqueue |
| **Retrieval** | By sequence number only | By receiving from DLQ like a normal queue |
| **Purpose** | Temporary postponement; intent to process later | Failed/poison messages; may need manual intervention |
| **Automatic Movement** | No (explicitly deferred by application) | Can be automatic (max delivery count, TTL) |
| **Visibility** | Not visible to regular receive operations | Visible in DLQ via receiver |

#### Best Practices
- **Always persist the sequence number** in a durable store (database, cache) when deferring messages
- Use deferral for **temporary** processing delays, not permanent storage
- Consider implementing a background process to periodically check and process deferred messages
- Monitor deferred message counts to prevent buildup
- Set appropriate message TTL to ensure deferred messages don't remain indefinitely

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

## 6. Exam Scenarios

### Exam Question 1: Selecting Technologies for Transactional, Duplicate-Free, Unlimited Storage Messaging

**Scenario:** You are developing an Azure messaging solution. You need to ensure that the solution meets the following requirements:
- Provide transactional support
- Provide duplicate detection
- Store the messages for an unlimited period of time

**Question:** Which two technologies will meet the requirements?

### Answer Analysis

#### ✅ Correct Answer 1: Azure Service Bus Queue

**Why this is CORRECT:**

1. **Transactional Support ✅**
   - Service Bus Queues support atomic transactions across multiple operations
   - Can send, receive, and complete messages within a single transaction scope
   - Ensures all-or-nothing delivery guarantees
   
   ```csharp
   using (var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
   {
       await sender1.SendMessageAsync(new ServiceBusMessage("Message 1"));
       await sender2.SendMessageAsync(new ServiceBusMessage("Message 2"));
       scope.Complete(); // Both committed atomically
   }
   ```

2. **Duplicate Detection ✅**
   - Built-in duplicate detection based on `MessageId` property
   - Configurable detection window (up to 7 days)
   - Available in Standard and Premium tiers
   - Automatically discards duplicate messages without application code
   
   ```csharp
   var message = new ServiceBusMessage("Transaction data")
   {
       MessageId = "txn-12345"  // Unique identifier for deduplication
   };
   await sender.SendMessageAsync(message);
   ```

3. **Unlimited Message Storage ✅**
   - **Messages can be stored indefinitely** by setting Time-To-Live (TTL) to `TimeSpan.MaxValue`
   - Default TTL is 14 days, but can be configured to never expire
   - Messages remain in the queue until explicitly consumed or deleted
   - No automatic expiration when TTL is set to maximum
   
   ```csharp
   // Configure queue with unlimited TTL
   var queueDescription = new QueueDescription("myqueue")
   {
       DefaultMessageTimeToLive = TimeSpan.MaxValue  // Unlimited storage
   };
   ```

**Point-to-Point Messaging:**
- Single consumer processes each message
- Ideal for command processing and work queue patterns
- Messages removed after successful processing

---

#### ✅ Correct Answer 2: Azure Service Bus Topic

**Why this is CORRECT:**

1. **Transactional Support ✅**
   - Same transactional capabilities as Service Bus Queue
   - Supports atomic operations within a single namespace
   - Multiple subscriptions can participate in transactional workflows
   
2. **Duplicate Detection ✅**
   - Same duplicate detection mechanism as queues
   - Configured at the topic level
   - Applies to all subscriptions under the topic
   - Each subscription receives deduplicated messages

3. **Unlimited Message Storage ✅**
   - **Messages stored indefinitely** with TTL set to `TimeSpan.MaxValue`
   - Each subscription independently stores message copies
   - Messages remain until consumed by all interested subscribers
   - No forced expiration with maximum TTL configuration

**Publish-Subscribe Messaging:**
- Multiple subscribers can receive copies of the same message
- Ideal for event broadcasting and fan-out scenarios
- Each subscription acts like an independent queue

**When to Choose Topic Over Queue:**
- Multiple independent services need to process the same message
- Event-driven microservices architecture
- Broadcasting domain events across bounded contexts

---

#### ❌ Incorrect Answer: Azure Storage Queue

**Why this is WRONG:**

1. **No Transactional Support ❌**
   - Azure Storage Queue **does not support transactions** across multiple operations
   - Cannot perform atomic operations on multiple messages
   - Each operation (enqueue, dequeue, delete) is independent
   - No guarantee of all-or-nothing message delivery

2. **No Duplicate Detection ❌**
   - Azure Storage Queue **does not provide built-in duplicate detection**
   - Application must implement custom deduplication logic
   - No automatic tracking of message IDs or deduplication windows
   - Duplicate messages can be processed multiple times

3. **Unlimited Storage ✅ (Only Requirement Met)**
   - Messages can be stored for up to 7 days (not truly unlimited without manual intervention)
   - Default TTL is 7 days, maximum is 7 days
   - Messages automatically expire after 7 days
   - Requires external archiving for longer retention

**When to Use Azure Storage Queue:**
- Simple message queuing without enterprise features
- Cost-sensitive scenarios (lower cost than Service Bus)
- No transactional or deduplication requirements
- High message volumes with simple processing

**Feature Comparison:**

| Feature | Service Bus Queue/Topic | Storage Queue |
|---------|------------------------|---------------|
| **Transactions** | ✅ Yes | ❌ No |
| **Duplicate Detection** | ✅ Yes | ❌ No |
| **Unlimited Storage** | ✅ Yes (TTL = MaxValue) | ⚠️ Limited (7 days max) |
| **Message Size** | Up to 256 KB (1 MB batched) | Up to 64 KB |
| **Ordering (FIFO)** | ✅ Yes (with sessions) | ❌ No guarantee |
| **Dead-Letter Queue** | ✅ Yes | ❌ No |
| **Cost** | Higher | Lower |

---

#### ❌ Incorrect Answer: Azure Event Hub

**Why this is WRONG:**

1. **No Transactional Support (as Required) ❌**
   - Event Hub **does not provide transactional guarantees** in the traditional messaging sense
   - No support for atomic operations across multiple events
   - Events are immediately committed upon receipt
   - Cannot roll back or commit multiple events as a single transaction
   - Designed for high-throughput streaming, not transactional messaging

2. **No Duplicate Detection ❌**
   - Event Hub **does not provide built-in duplicate detection**
   - No automatic tracking of event IDs or deduplication logic
   - Application must implement custom deduplication if needed
   - Duplicate events can be processed multiple times

3. **Different Storage Model ⚠️**
   - Event Hub stores events for a **retention period** (1-90 days, 7 days default)
   - Not designed for indefinite message storage
   - Events are automatically purged after retention period
   - Storage is time-based, not consumption-based

**Event Hub Design Philosophy:**
- **Event streaming** platform, not a message queue
- Optimized for **high-throughput, low-latency** event ingestion
- Multiple consumers can read the same event stream (similar to Kafka)
- Events are **append-only** and cannot be deleted individually
- No concept of message completion or dead-lettering

**When to Use Event Hub:**
- Real-time telemetry and event ingestion
- IoT device data streaming
- Application logging and diagnostics
- Big data scenarios with millions of events per second
- Time-series data collection

**Feature Comparison:**

| Feature | Service Bus | Event Hub |
|---------|-------------|-----------|
| **Use Case** | Enterprise messaging | Event streaming |
| **Transactions** | ✅ Yes | ❌ No |
| **Duplicate Detection** | ✅ Yes | ❌ No |
| **Message Completion** | ✅ Yes (Peek-Lock) | ❌ No (Offset-based) |
| **Dead-Letter Queue** | ✅ Yes | ❌ No |
| **FIFO Ordering** | ✅ Yes (sessions) | ⚠️ Per partition |
| **Throughput** | Moderate (thousands/sec) | Very High (millions/sec) |
| **Message TTL** | Unlimited (configurable) | Retention period (1-90 days) |

---

### Exam Question 2: FIFO Message Processing for Component Communication

**Scenario:** You are designing an app that will include two components. The components will communicate by sending messages via a queue. You need to recommend a solution to process the messages by using a First In, First Out (FIFO) pattern.

**Question:** What should you include in the recommendation?

- A. Storage queues with a custom metadata setting
- B. Azure Service Bus queues with partitioning enabled
- C. Azure Service Bus queues with sessions enabled
- D. Storage queues with a stored access policy

### Answer Analysis

#### ✅ Correct Answer: C. Azure Service Bus queues with sessions enabled

**Why this is CORRECT:**

Azure Service Bus supports First-In, First-Out (FIFO) message processing through the use of **message sessions**. When sessions are enabled:

1. **Session Grouping:** Messages that share the same `SessionId` are grouped together
2. **Ordered Processing:** Messages within a session are processed strictly in order of arrival
3. **Single Consumer Lock:** Only one consumer can lock and process a session at a time, preventing out-of-order processing
4. **Strict FIFO Behavior:** This is the recommended and most reliable method to enforce ordered message handling in Azure

```csharp
// Create session-enabled queue for FIFO processing
var queueOptions = new CreateQueueOptions("fifo-queue")
{
    RequiresSession = true  // Enables FIFO guarantee
};

// Send messages with SessionId for FIFO ordering
var message = new ServiceBusMessage("Process me in order")
{
    SessionId = "workflow-123"  // Messages with same SessionId processed in order
};
```

---

#### ❌ Incorrect Answer: A. Storage queues with a custom metadata setting

**Why this is WRONG:**

Azure Storage queues **do not natively support FIFO guarantees**:

- Messages are generally retrieved in approximate order, but there is **no strict ordering guarantee**
- Under high-throughput conditions, messages may be delivered out of order
- **Custom metadata cannot enforce message ordering** - metadata is for storing additional information, not controlling delivery order
- Storage queues use visibility timeout mechanism which can cause redelivery in different order

---

#### ❌ Incorrect Answer: B. Azure Service Bus queues with partitioning enabled

**Why this is WRONG:**

Partitioning **improves throughput and availability but does NOT guarantee FIFO processing**:

- Partitioned queues distribute messages across **multiple message brokers**
- Each partition operates independently, which may result in **out-of-order delivery**
- Partitioning is designed for **scalability**, not ordering
- Messages sent to different partitions have no ordering relationship

> **Key Insight:** Partitioning is the opposite of FIFO in effect - it intentionally spreads messages to improve throughput at the cost of strict ordering.

---

#### ❌ Incorrect Answer: D. Storage queues with a stored access policy

**Why this is WRONG:**

Stored access policies are completely unrelated to message ordering:

- **Purpose:** Managing Shared Access Signatures (SAS) for authentication and authorization
- **Function:** Control permissions (read, write, delete) and token expiration
- **No Impact on:** Message ordering, queue processing behavior, or delivery sequence

Stored access policies provide security controls, not messaging guarantees.

---

#### Feature Comparison for FIFO Requirements

| Solution | FIFO Support | How It Works |
|----------|--------------|---------------|
| **Service Bus + Sessions** | ✅ Yes | Messages with same SessionId processed in order |
| **Service Bus + Partitioning** | ❌ No | Messages distributed across brokers |
| **Storage Queue + Metadata** | ❌ No | Metadata doesn't control delivery order |
| **Storage Queue + Access Policy** | ❌ No | Security feature, unrelated to ordering |

---

#### References

- [Message Sessions - Azure Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/message-sessions)
- [Azure Storage Queues Introduction](https://learn.microsoft.com/en-us/azure/storage/queues/storage-queues-introduction)
- [Service Bus Partitioning](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-partitioning)
- [Storage SAS Overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)

---

### Summary: Technology Selection Matrix

#### Requirements Analysis

| Requirement | Service Bus Queue | Service Bus Topic | Storage Queue | Event Hub |
|-------------|-------------------|-------------------|---------------|-----------|
| **Transactional Support** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Duplicate Detection** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Unlimited Storage** | ✅ Yes | ✅ Yes | ⚠️ Limited (7 days) | ⚠️ Retention-based |
| **Meets All Requirements** | ✅ YES | ✅ YES | ❌ NO | ❌ NO |

#### Key Differentiators

**Why Service Bus (Queue & Topic) is the ONLY Correct Choice:**

✅ **Enterprise Messaging Features:**
- Atomic transactions across operations
- Built-in duplicate detection with configurable windows
- Truly unlimited message storage with `TimeSpan.MaxValue` TTL
- Dead-letter queues for failed messages
- Message sessions for FIFO ordering
- At-least-once delivery guarantees

✅ **Flexible Message Retention:**
```csharp
// Unlimited storage configuration
var queueDescription = new QueueDescription("financial-transactions")
{
    DefaultMessageTimeToLive = TimeSpan.MaxValue,  // Never expires
    EnableDeadLetteringOnMessageExpiration = true,
    RequiresDuplicateDetection = true,
    DuplicateDetectionHistoryTimeWindow = TimeSpan.FromDays(1)
};
```

❌ **Why Others Don't Meet Requirements:**

**Storage Queue:**
- Lacks enterprise features (transactions, deduplication)
- Limited to 7-day maximum retention
- No built-in reliability mechanisms

**Event Hub:**
- Different architectural model (streaming vs. messaging)
- No transactional support for individual events
- Retention-based storage, not message completion-based
- No duplicate detection or dead-lettering

---

### Decision Tree: Choosing the Right Messaging Service

```
Need enterprise messaging features?
    │
    ├─ Need transactions AND duplicate detection?
    │   └─ ✅ Service Bus (Queue or Topic)
    │       │
    │       ├─ Single consumer?
    │       │   └─ ✅ Service Bus Queue
    │       │
    │       └─ Multiple subscribers?
    │           └─ ✅ Service Bus Topic
    │
    ├─ Simple queuing, cost-sensitive?
    │   └─ ✅ Azure Storage Queue
    │       (Note: No transactions or duplicate detection)
    │
    └─ High-throughput event streaming?
        └─ ✅ Azure Event Hub
            (Note: Different model, not for transactional messaging)
```

---

### Best Practices for Service Bus with Unlimited Storage

#### Configuration Recommendations

```csharp
// Production-grade Service Bus configuration
var queueOptions = new CreateQueueOptions("critical-transactions")
{
    // Unlimited storage
    DefaultMessageTimeToLive = TimeSpan.MaxValue,
    
    // Duplicate detection
    RequiresDuplicateDetection = true,
    DuplicateDetectionHistoryTimeWindow = TimeSpan.FromHours(24),
    
    // Reliability features
    DeadLetteringOnMessageExpiration = true,
    EnableBatchedOperations = true,
    MaxDeliveryCount = 10,
    
    // Ordering (optional)
    RequiresSession = false,  // Set to true if FIFO needed
    
    // Size limits
    MaxSizeInMegabytes = 5120,  // 5 GB
};

await adminClient.CreateQueueAsync(queueOptions);
```

#### Monitoring and Maintenance

✅ **DO:**
- Monitor queue/topic size and message counts
- Implement dead-letter queue processing
- Set up alerts for message backlog
- Use batching for high-throughput scenarios
- Configure appropriate max delivery counts

❌ **DON'T:**
- Set unlimited TTL without monitoring storage growth
- Ignore dead-letter queues (can grow indefinitely)
- Skip duplicate detection for critical business messages
- Use Service Bus for high-volume telemetry (use Event Hub instead)
- Forget to handle transient failures and implement retry logic

#### Cost Considerations with Unlimited Storage

**Important:** While Service Bus supports unlimited message storage by setting TTL to `TimeSpan.MaxValue`, be aware of:

- **Storage costs:** Messages consume namespace storage quota
- **Premium tier benefits:** Dedicated resources, larger message sizes
- **Message size limits:** 256 KB in Standard, up to 100 MB in Premium
- **Pricing model:** Based on operations and message units, not just storage

**Monitor these metrics:**
- Active message count
- Dead-letter message count
- Queue/topic size in MB
- Scheduled message count
- Deferred message count

---

### Exam Tips

> **When asked about messaging solutions requiring transactions, duplicate detection, AND unlimited storage:**
> - ✅ **Correct answers:** Azure Service Bus Queue and/or Azure Service Bus Topic
> - ❌ **Incorrect:** Azure Storage Queue (no transactions/deduplication), Azure Event Hub (different model)

> **Key phrases to recognize:**
> - "Transactional support" → Service Bus only
> - "Duplicate detection" → Service Bus only
> - "Unlimited period of time" → Service Bus with `TimeSpan.MaxValue` TTL
> - "Multiple subscribers" → Service Bus Topic (not Queue)

> **Remember:**
> - Service Bus is the ONLY Azure messaging service that provides all three features together
> - Both Queue and Topic variants support the same core features (transactions, deduplication, unlimited storage)
> - Choose Queue for point-to-point, Topic for publish-subscribe patterns

---

## 7. Best Practices
- **Peek-Lock vs Receive-and-Delete:** Always use Peek-Lock for reliability (default). It allows abandoning the message if processing fails.
- **Prefetch Count:** Increase prefetch count for high throughput scenarios to reduce round-trips.
- **Exception Handling:** Handle `MessageLockLostException` (processing took too long) and `ServiceBusException` (transient errors).
