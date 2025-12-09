# Azure Queue Storage
## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Components](#components)
  - [Message Properties](#message-properties)
- [Azure Queue Storage vs Azure Service Bus](#azure-queue-storage-vs-azure-service-bus)
  - [When to Use Queue Storage](#when-to-use-queue-storage)
  - [When to Use Service Bus](#when-to-use-service-bus)
- [Working with Azure Queue Storage in .NET](#working-with-azure-queue-storage-in-net)
  - [NuGet Package](#nuget-package)
  - [Basic Operations](#basic-operations)
    - [1. Create a Queue Client](#1-create-a-queue-client)
    - [2. Send Messages](#2-send-messages)
    - [3. Peek at Messages (Without Removal)](#3-peek-at-messages-without-removal)
    - [4. Receive Messages (With Removal/Visibility)](#4-receive-messages-with-removalvisibility)
    - [5. Update Messages](#5-update-messages)
    - [6. Get Queue Properties](#6-get-queue-properties)
    - [7. Delete Queue](#7-delete-queue)
- [Common Patterns](#common-patterns)
  - [1. Poison Message Handling](#1-poison-message-handling)
  - [2. Long-Running Processing with Visibility Extension](#2-long-running-processing-with-visibility-extension)
  - [3. Batch Processing](#3-batch-processing)
- [Important Differences: Queue Storage vs Service Bus Methods](#important-differences-queue-storage-vs-service-bus-methods)
  - [Queue Storage (Azure.Storage.Queues)](#queue-storage-azurestoragequeues)
  - [Service Bus (Azure.Messaging.ServiceBus)](#service-bus-azuremessagingservicebus)
  - [Critical Distinction: Peek vs Receive](#critical-distinction-peek-vs-receive)
- [Exam Question Analysis](#exam-question-analysis)
  - [Question: Queue-Based Load Leveling with Visibility Timeout](#question-queue-based-load-leveling-with-visibility-timeout)
  - [Question: Verify Message Presence Without Removal](#question-verify-message-presence-without-removal)
  - [Exam Answer Issues](#exam-answer-issues)
  - [Correct Technical Facts](#correct-technical-facts)
  - [Question: Configuring Retry Attempts for Failed Queue Messages](#question-configuring-retry-attempts-for-failed-queue-messages)
- [Best Practices](#best-practices)
  - [1. Message Processing](#1-message-processing)
  - [2. Performance](#2-performance)
  - [3. Reliability](#3-reliability)
  - [4. Security](#4-security)
  - [5. Cost Optimization](#5-cost-optimization)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
  - [Key Metrics to Monitor](#key-metrics-to-monitor)
  - [Common Issues](#common-issues)
- [Pricing](#pricing)
- [References](#references)


## Overview

Azure Queue Storage is a service for storing large numbers of messages that can be accessed from anywhere in the world via authenticated HTTP or HTTPS calls. A single queue message can be up to 64 KB in size, and a queue can contain millions of messages, up to the total capacity limit of a storage account.

Queue Storage is commonly used to:
- Create a backlog of work to process asynchronously
- Pass messages between different parts of a distributed application
- Decouple application components for better scalability and resilience

## Key Concepts

### Components

1. **Storage Account**: Provides a unique namespace in Azure for your data
2. **Queue**: Contains a set of messages generally processed in FIFO (First In, First Out) order
3. **Message**: A message in any format, up to 64 KB in size
4. **URL Format**: `https://<storage-account>.queue.core.windows.net/<queue>`

### Message Ordering

**Important**: Azure Queue Storage **does not guarantee strict FIFO ordering**. While messages are generally processed in the order they were added under normal conditions, the following scenarios can cause out-of-order processing:

- **Multiple consumers**: When multiple consumers retrieve messages simultaneously
- **Visibility timeouts**: Messages with different visibility timeout values may reappear at different times
- **Failed processing**: Messages that fail and reappear after visibility timeout will be processed out of order relative to newer messages
- **High concurrency**: Under high-load scenarios, message ordering is not guaranteed
- **Message updates**: Updated messages may be reordered in the queue

**If strict FIFO ordering is required**, use **Azure Service Bus Queues with sessions** instead, which provides:
- Guaranteed ordering within a session
- Session-based message grouping
- First-in, first-out delivery guarantees per session

### Message Properties

- **Message ID**: Unique identifier assigned by the service
- **Insertion Time**: When the message was added to the queue
- **Expiration Time**: When the message will expire (default: 7 days, max: forever if set to -1)
- **Visibility Timeout**: Period during which the message is invisible to other consumers after being retrieved
- **Dequeue Count**: Number of times the message has been retrieved
- **Pop Receipt**: Required to delete or update a message after retrieval

## Azure Queue Storage vs Azure Service Bus

### When to Use Queue Storage

- **Basic message queuing**: Simple asynchronous message processing where strict ordering is not critical
- **Cost-effective**: Lower cost for simple scenarios
- **Large message volume**: Handle millions of messages
- **HTTP/HTTPS access**: Access from anywhere via REST API
- **Auditing**: Need detailed tracking of all operations via Storage Analytics
- **Loose ordering requirements**: Application can tolerate messages being processed out of order
### When to Use Service Bus

- **Advanced messaging patterns**: Publish/subscribe, sessions, transactions
- **Message size > 64 KB**: Support for messages up to 256 KB (Standard) or 1 MB (Premium)
- **Guaranteed FIFO ordering**: Strict first-in, first-out delivery with session-based ordering guarantees
- **Duplicate detection**: Automatic detection of duplicate messages
- **Complex routing**: Topic filters and actions
- **Strict ordering requirements**: Application requires messages to be processed in exact orderf duplicate messages
- **Complex routing**: Topic filters and actions

## Working with Azure Queue Storage in .NET

### NuGet Package

```bash
dotnet add package Azure.Storage.Queues
```

### Basic Operations

#### 1. Create a Queue Client

```csharp
using Azure.Storage.Queues;
using Azure.Storage.Queues.Models;

// Connection string approach
string connectionString = "<your-connection-string>";
string queueName = "myqueue";
QueueClient queueClient = new QueueClient(connectionString, queueName);

// Create the queue if it doesn't exist
await queueClient.CreateIfNotExistsAsync();
```

#### 2. Send Messages

```csharp
// Send a single message
await queueClient.SendMessageAsync("Hello, World!");

// Send with visibility timeout (message invisible for 30 seconds)
await queueClient.SendMessageAsync(
    "Delayed message",
    visibilityTimeout: TimeSpan.FromSeconds(30)
);

// Send with time-to-live
await queueClient.SendMessageAsync(
    "Expiring message",
    timeToLive: TimeSpan.FromMinutes(5)
);
```

#### 3. Peek at Messages (Without Removal)

**Important**: Peeking allows you to view messages without removing them from the queue or making them invisible to other consumers.

```csharp
// Peek at a single message (returns null if queue is empty)
PeekedMessage peekedMessage = await queueClient.PeekMessageAsync();
if (peekedMessage != null)
{
    Console.WriteLine($"Peeked message: {peekedMessage.MessageText}");
    Console.WriteLine($"Message ID: {peekedMessage.MessageId}");
}

// Peek at multiple messages (up to 32 messages)
PeekedMessage[] peekedMessages = await queueClient.PeekMessagesAsync(maxMessages: 10);
foreach (var message in peekedMessages)
{
    Console.WriteLine($"Message: {message.MessageText}");
}
```

**Key Points about Peeking:**
- Messages remain in the queue
- Messages remain visible to other consumers
- You cannot delete or update peeked messages (no pop receipt)
- Useful for monitoring queue contents without affecting processing
- Maximum of 32 messages can be peeked at once

#### 4. Receive Messages (With Removal/Visibility)

```csharp
// Receive a single message (makes it invisible for 30 seconds by default)
QueueMessage message = await queueClient.ReceiveMessageAsync();
if (message != null)
{
    Console.WriteLine($"Message: {message.MessageText}");
    Console.WriteLine($"Dequeue count: {message.DequeueCount}");
    
    // Process the message...
    
    // Delete the message after processing
    await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
}

// Receive multiple messages (up to 32 messages)
QueueMessage[] messages = await queueClient.ReceiveMessagesAsync(
    maxMessages: 10,
    visibilityTimeout: TimeSpan.FromMinutes(5)
);

foreach (var msg in messages)
{
    // Process and delete each message
    await ProcessMessageAsync(msg);
    await queueClient.DeleteMessageAsync(msg.MessageId, msg.PopReceipt);
}
```

**Key Points about Receiving:**
- Messages become invisible to other consumers for the visibility timeout period
- Returns a pop receipt required for deletion or updates
- If not deleted within visibility timeout, message reappears in the queue
- Maximum of 32 messages can be received at once

#### 5. Update Messages

```csharp
// Receive a message
QueueMessage message = await queueClient.ReceiveMessageAsync();

if (message != null)
{
    // Update the message content and extend visibility timeout
    UpdateReceipt updateReceipt = await queueClient.UpdateMessageAsync(
        message.MessageId,
        message.PopReceipt,
        "Updated message content",
        TimeSpan.FromSeconds(60) // Extend visibility for 60 more seconds
    );
    
    // Use the new pop receipt for subsequent operations
    await queueClient.DeleteMessageAsync(message.MessageId, updateReceipt.PopReceipt);
}
```

#### 6. Get Queue Properties

```csharp
// Get queue properties including approximate message count
QueueProperties properties = await queueClient.GetPropertiesAsync();
Console.WriteLine($"Approximate message count: {properties.ApproximateMessagesCount}");
Console.WriteLine($"Metadata: {string.Join(", ", properties.Metadata)}");
```

#### 7. Delete Queue

```csharp
await queueClient.DeleteAsync();
```

## Common Patterns

### 1. Poison Message Handling

```csharp
QueueMessage message = await queueClient.ReceiveMessageAsync();

if (message != null)
{
    const int maxDequeueCount = 5;
    
    if (message.DequeueCount > maxDequeueCount)
    {
        // Move to poison queue
        QueueClient poisonQueue = new QueueClient(connectionString, "poison-queue");
        await poisonQueue.SendMessageAsync(message.MessageText);
        await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
    }
    else
    {
        try
        {
            await ProcessMessageAsync(message);
            await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
        }
        catch (Exception ex)
        {
            // Log error, message will reappear after visibility timeout
            Console.WriteLine($"Error processing message: {ex.Message}");
        }
    }
}
```

### 2. Long-Running Processing with Visibility Extension

```csharp
QueueMessage message = await queueClient.ReceiveMessageAsync();

if (message != null)
{
    string currentPopReceipt = message.PopReceipt;
    
    try
    {
        // Start processing
        for (int step = 1; step <= 10; step++)
        {
            // Do some work
            await Task.Delay(1000);
            
            // Extend visibility every few steps to keep the message invisible
            if (step % 3 == 0)
            {
                var updateReceipt = await queueClient.UpdateMessageAsync(
                    message.MessageId,
                    currentPopReceipt,
                    message.MessageText,
                    TimeSpan.FromSeconds(30)
                );
                currentPopReceipt = updateReceipt.PopReceipt;
            }
        }
        
        // Delete after successful processing
        await queueClient.DeleteMessageAsync(message.MessageId, currentPopReceipt);
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
        // Message will reappear after visibility timeout
    }
}
```

### 3. Batch Processing

```csharp
// Process messages in batches
while (true)
{
    QueueMessage[] messages = await queueClient.ReceiveMessagesAsync(
        maxMessages: 32,
        visibilityTimeout: TimeSpan.FromMinutes(2)
    );
    
    if (messages.Length == 0)
    {
        await Task.Delay(1000); // Wait before checking again
        continue;
    }
    
    // Process messages in parallel
    var tasks = messages.Select(async msg =>
    {
        try
        {
            await ProcessMessageAsync(msg);
            await queueClient.DeleteMessageAsync(msg.MessageId, msg.PopReceipt);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing message {msg.MessageId}: {ex.Message}");
        }
    });
    
    await Task.WhenAll(tasks);
}
```

## Important Differences: Queue Storage vs Service Bus Methods

### Queue Storage (Azure.Storage.Queues)

| Method | Description | Returns |
|--------|-------------|---------|
| `PeekMessageAsync()` | Peek at one message without removing | `PeekedMessage` |
| `PeekMessagesAsync(maxMessages)` | Peek at multiple messages (max 32) | `PeekedMessage[]` |
| `ReceiveMessageAsync()` | Retrieve and make invisible one message | `QueueMessage` (with pop receipt) |
| `ReceiveMessagesAsync(maxMessages)` | Retrieve and make invisible multiple messages | `QueueMessage[]` |
| `DeleteMessageAsync()` | Remove message from queue | - |
| `UpdateMessageAsync()` | Update message content/visibility | `UpdateReceipt` |

### Service Bus (Azure.Messaging.ServiceBus)

| Method | Description | Returns |
|--------|-------------|---------|
| `PeekMessageAsync()` | Peek at one message without removing | `ServiceBusReceivedMessage` |
| `PeekMessagesAsync(maxMessages)` | Peek at multiple messages | `IReadOnlyList<ServiceBusReceivedMessage>` |
| `ReceiveMessageAsync()` | Retrieve message (requires lock) | `ServiceBusReceivedMessage` |
| `ReceiveMessagesAsync(maxMessages)` | Retrieve multiple messages | `IReadOnlyList<ServiceBusReceivedMessage>` |
| `CompleteMessageAsync()` | Remove message from queue/subscription | - |
| `AbandonMessageAsync()` | Release message lock | - |

### Critical Distinction: Peek vs Receive

**The exam question confusion stems from mixing Service Bus terminology with Queue Storage:**

- **Queue Storage** uses `PeekMessagesAsync()` (plural) for non-destructive viewing
- **Service Bus** uses `Peek()` and `PeekMessageAsync()` methods
- Both services distinguish between "peek" (view only) and "receive" (retrieve with lock/invisibility)

## Exam Question Analysis

### Question: Queue-Based Load Leveling with Visibility Timeout

**Scenario**: You are implementing a queue-based load leveling pattern using Azure Queue Storage. Messages must be invisible for 5 minutes after being retrieved to allow for processing time. If processing fails, messages should reappear for retry. Which parameter should you configure?

**Options:**

1. **Set `defaultMessageTimeToLive` to 300 seconds when creating the queue** ❌
   - **Wrong**: The `defaultMessageTimeToLive` property sets the default expiration time for messages in the queue, not the visibility timeout during processing.

2. **Set `messageTimeToLive` to 300 seconds in the queue service properties** ❌
   - **Wrong**: Queue service properties don't include a `messageTimeToLive` setting, and this would affect message expiration rather than visibility during processing.

3. **Set `visibilityTimeout` to 300 seconds when calling `GetMessage`** ✅
   - **Correct**: The `visibilityTimeout` parameter in `GetMessage` (or `ReceiveMessageAsync` in .NET SDK) specifies how long a message remains invisible after being retrieved. Setting it to 300 seconds (5 minutes) provides the required processing window before the message reappears if not deleted.

4. **Set `messageTTL` to 300 seconds when calling `PutMessage`** ❌
   - **Wrong**: The `messageTTL` (time-to-live) parameter determines when a message expires and is permanently deleted from the queue, not how long it remains invisible during processing.

**Key Concepts:**

| Parameter | Purpose | When Used |
|-----------|---------|-----------|
| `visibilityTimeout` | How long message is invisible after retrieval | `ReceiveMessageAsync()` / `GetMessage` |
| `timeToLive` / `messageTTL` | When message expires and is deleted | `SendMessageAsync()` / `PutMessage` |
| `defaultMessageTimeToLive` | Default TTL for all messages in queue | Queue creation |

**Code Example:**

```csharp
// Set visibility timeout to 5 minutes (300 seconds) when receiving
QueueMessage message = await queueClient.ReceiveMessageAsync(
    visibilityTimeout: TimeSpan.FromSeconds(300) // 5 minutes
);

if (message != null)
{
    try
    {
        // Process the message within 5 minutes
        await ProcessMessageAsync(message);
        
        // Delete after successful processing
        await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
    }
    catch (Exception ex)
    {
        // If processing fails, message will automatically reappear after 5 minutes
        Console.WriteLine($"Processing failed: {ex.Message}");
    }
}
```

**Domain**: Connect to and consume Azure services and third-party services

---

### Question: Verify Message Presence Without Removal

**Correct Answer: `PeekMessages` (or `PeekMessagesAsync`)**

**Why Each Answer Is Right or Wrong:**

1. **`Peek`** ❌
   - **Issue**: This method doesn't exist in Azure Queue Storage .NET SDK
   - **Confusion**: This is terminology from Azure Service Bus, not Queue Storage
   - The exam answer incorrectly states this is incorrect without explaining that it's not a Queue Storage method

2. **`PeekMessages`** ✅ (or `PeekMessagesAsync`)
   - **Correct**: This is the actual method in `QueueClient` class
   - Returns `PeekedMessage[]` array
   - Messages remain in queue and visible to other consumers
   - Can peek up to 32 messages at once
   - No pop receipt returned (cannot delete or update)

3. **`ReceiveMessages`** ❌ (or `ReceiveMessagesAsync`)
   - **Wrong**: This retrieves messages AND makes them invisible
   - Returns `QueueMessage[]` with pop receipts
   - Violates the "without removing" requirement (makes invisible = temporary removal)
   - Affects other consumers by hiding messages during visibility timeout

4. **`ReceiveMessageAsync`** ❌
   - **Issue**: While this is a valid Queue Storage method (singular form)
   - **Wrong**: Like `ReceiveMessages`, it makes messages invisible
   - **Additional Issue**: The exam explanation incorrectly states this is "used with Azure Service Bus, not Azure Queue Storage"
   - **Truth**: Both services have similar method names but different implementations

### Exam Answer Issues

The provided exam explanation contains inaccuracies:

1. **States `Peek` is used with Service Bus**: While Service Bus has peek methods, so does Queue Storage (`PeekMessages`)
2. **States `ReceiveMessageAsync` is Service Bus only**: This is incorrect - Queue Storage has `ReceiveMessageAsync()` method
3. **Doesn't clarify plural vs singular**: Queue Storage uses `PeekMessagesAsync()` (plural) as the primary method

### Correct Technical Facts

**Queue Storage (`Azure.Storage.Queues` SDK):**
- ✅ `PeekMessageAsync()` - peeks at one message
- ✅ `PeekMessagesAsync(maxMessages)` - peeks at multiple messages (up to 32)
- ✅ `ReceiveMessageAsync()` - receives one message with visibility timeout
- ✅ `ReceiveMessagesAsync(maxMessages)` - receives multiple messages

**Service Bus (`Azure.Messaging.ServiceBus` SDK):**
- ✅ `PeekMessageAsync()` - peeks at one message
- ✅ `PeekMessagesAsync(maxMessages)` - peeks at multiple messages
- ✅ `ReceiveMessageAsync()` - receives one message
- ✅ `ReceiveMessagesAsync(maxMessages)` - receives multiple messages

**Key Difference**: The question context and correct answer should specify `PeekMessagesAsync` to be completely accurate for Queue Storage.

---

### Question: Configuring Retry Attempts for Failed Queue Messages

**Scenario**: You have an Azure Storage Queue that processes messages in batches. When retrieving messages, you need to ensure failed messages are retried up to 5 times before being removed. What should you configure?

**Options:**

1. **Set the message time-to-live to 5 times the processing duration** ❌
   - **Wrong**: Time-to-live controls message expiration, not retry count. Messages expire based on time, not the number of processing attempts.

2. **Enable automatic retry with exponential backoff for 5 attempts** ❌
   - **Wrong**: Queue Storage doesn't have built-in automatic retry with exponential backoff. To handle poison messages, you must manually check the `dequeueCount` of the queue message.

3. **Set `maxDequeueCount` to 5 and implement a poison queue handler** ✅
   - **Correct**: Azure Functions retries the function up to five times for a given queue message, including the first try. If all five attempts fail, the functions runtime adds a message to a poison queue named `<originalqueuename>-poison`.

4. **Configure `visibilityTimeout` to allow 5 retry intervals** ❌
   - **Wrong**: Visibility timeout controls how long a message is hidden after retrieval, not the number of retry attempts. It doesn't automatically track or limit dequeue attempts.

**Key Concepts:**

| Parameter | Purpose | Controls Retries? |
|-----------|---------|-------------------|
| `maxDequeueCount` | Maximum number of times a message can be dequeued before moving to poison queue | ✅ Yes |
| `dequeueCount` | Current number of times the message has been retrieved | Read-only counter |
| `visibilityTimeout` | How long message is invisible after retrieval | ❌ No (timing only) |
| `timeToLive` | When message expires and is permanently deleted | ❌ No (expiration only) |

**Azure Functions Configuration (host.json):**

```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxPollingInterval": "00:01:00",
      "newBatchThreshold": 8
    }
  }
}
```

**Manual Implementation (SDK Approach):**

```csharp
public async Task ProcessMessagesWithRetryAsync(QueueClient queueClient, QueueClient poisonQueueClient)
{
    const int maxDequeueCount = 5;
    
    QueueMessage message = await queueClient.ReceiveMessageAsync();
    
    if (message != null)
    {
        // Check if message has exceeded retry limit
        if (message.DequeueCount > maxDequeueCount)
        {
            // Move to poison queue
            await poisonQueueClient.SendMessageAsync(message.MessageText);
            await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
            Console.WriteLine($"Message moved to poison queue after {message.DequeueCount} attempts");
        }
        else
        {
            try
            {
                await ProcessMessageAsync(message);
                await queueClient.DeleteMessageAsync(message.MessageId, message.PopReceipt);
            }
            catch (Exception ex)
            {
                // Log error - message will reappear after visibility timeout for retry
                Console.WriteLine($"Processing failed (attempt {message.DequeueCount}): {ex.Message}");
            }
        }
    }
}
```

**Important Notes:**
- **Azure Functions Automatic Handling**: When using Azure Functions with Queue triggers, set `maxDequeueCount` in `host.json`. The runtime automatically manages retries and moves failed messages to `<queuename>-poison`.
- **SDK Manual Handling**: When using the SDK directly, you must manually check `DequeueCount` and implement poison queue logic.
- **Poison Queue Naming**: Azure Functions creates poison queues with the naming convention `<originalqueuename>-poison`.

**Domain**: Connect to and consume Azure services and third-party services

## Best Practices

### 1. Message Processing

- Always delete messages after successful processing
- Implement poison message handling for messages that fail repeatedly
- Use appropriate visibility timeout based on processing time
- Extend visibility timeout for long-running operations

### 2. Performance

- Process messages in batches when possible (up to 32 messages)
- Use parallel processing for independent messages
- Consider message size impact (smaller messages = better performance)
- Monitor dequeue count to identify problematic messages

### 3. Reliability

- Implement retry logic with exponential backoff
- Use separate poison queue for failed messages
- Log message processing metrics
- Monitor queue length and processing time

### 4. Security

- Use Managed Identity when possible instead of connection strings
- Enable HTTPS-only traffic
- Implement least-privilege access with Azure RBAC
- Rotate storage account keys regularly

### 5. Cost Optimization

- Delete processed messages promptly
- Set appropriate message TTL
- Clean up poison queues regularly
- Use lifecycle management for old messages

## Monitoring and Troubleshooting

### Key Metrics to Monitor

- **Approximate Message Count**: Number of messages in queue
- **Dequeue Count**: Number of times messages have been retrieved
- **Transaction Count**: Number of operations performed
- **Success/Error Rates**: Operation success vs failures

### Common Issues

1. **Messages Not Being Processed**
   - Check visibility timeout settings
   - Verify consumer is running and has correct permissions
   - Check for exceptions in processing logic

2. **Messages Reappearing**
   - Processing takes longer than visibility timeout
   - Consumer crashes before deleting message
   - Network issues preventing deletion

3. **High Dequeue Count**
   - Processing logic is failing consistently
   - Need to implement poison message handling
   - Message content may be corrupted

## Pricing

Azure Queue Storage pricing includes:
- **Storage costs**: Per GB per month
- **Transaction costs**: Per 10,000 transactions
  - Class 1: Write operations
  - Class 2: Read operations (including peek)
  - All other operations

Queue Storage is generally more cost-effective than Service Bus for simple queuing scenarios.

## References

- [Azure Queue Storage documentation](https://learn.microsoft.com/en-us/azure/storage/queues/)
- [Azure.Storage.Queues NuGet package](https://www.nuget.org/packages/Azure.Storage.Queues/)
- [Create and manage Azure Queue Storage and messages by using .NET](https://learn.microsoft.com/en-us/training/modules/create-manage-azure-queue-storage-messages-dotnet/)
- [Queue Storage vs Service Bus queues](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-azure-and-service-bus-queues-compared-contrasted)
