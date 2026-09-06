---
type: Azure Service
title: "Azure Messaging Services: Transaction Quick Reference"
description: "Need Transactions? ──┬─→ YES ──→ Service Bus"
tags: [integration]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Messaging Services: Transaction Quick Reference
## Table of Contents

- [⚡ Quick Decision Guide](#quick-decision-guide)
- [📊 Transaction Support at a Glance](#transaction-support-at-a-glance)
- [🔑 Key Transaction Patterns](#key-transaction-patterns)
  - [Service Bus: Full Transactions](#service-bus-full-transactions)
  - [Event Hubs: Manual Idempotency](#event-hubs-manual-idempotency)
  - [Event Grid: HTTP-Based Acknowledgment](#event-grid-http-based-acknowledgment)
- [🎯 When to Use Each Service](#when-to-use-each-service)
  - [🏆 Service Bus: Transactional Workflows](#service-bus-transactional-workflows)
  - [📈 Event Hubs: High-Volume Streaming](#event-hubs-high-volume-streaming)
  - [⚡ Event Grid: Event Distribution](#event-grid-event-distribution)
- [⚠️ Common Pitfalls](#common-pitfalls)
  - [Service Bus](#service-bus)
  - [Event Hubs](#event-hubs)
  - [Event Grid](#event-grid)
- [🔒 Reliability Patterns](#reliability-patterns)
  - [Pattern 1: Idempotency (All Services)](#pattern-1-idempotency-all-services)
  - [Pattern 2: Store-Then-Process (Event Grid/Hubs)](#pattern-2-store-then-process-event-gridhubs)
  - [Pattern 3: Transaction Scope (Service Bus Only)](#pattern-3-transaction-scope-service-bus-only)
- [📝 Delivery Guarantees Comparison](#delivery-guarantees-comparison)
  - [Service Bus](#service-bus-2)
  - [Event Hubs](#event-hubs-2)
  - [Event Grid](#event-grid-2)
- [🔧 Error Handling Strategies](#error-handling-strategies)
  - [Service Bus: Abandon or Dead-Letter](#service-bus-abandon-or-dead-letter)
  - [Event Hubs: Manual Retry or Dead-Letter](#event-hubs-manual-retry-or-dead-letter)
  - [Event Grid: HTTP Status Code](#event-grid-http-status-code)
- [💡 Best Practices Summary](#best-practices-summary)
  - [Service Bus](#service-bus-3)
  - [Event Hubs](#event-hubs-3)
  - [Event Grid](#event-grid-3)
- [🎓 Decision Flowchart](#decision-flowchart)
- [📚 Additional Resources](#additional-resources)
- [🎯 Quick Commands Reference](#quick-commands-reference)
  - [Service Bus](#service-bus-4)
  - [Event Hubs](#event-hubs-4)
  - [Event Grid](#event-grid-4)


## ⚡ Quick Decision Guide

```
Need Transactions? ──┬─→ YES ──→ Service Bus
                     │
                     └─→ NO ──┬─→ High Volume Stream? ──→ Event Hubs
                               │
                               └─→ Event Distribution? ──→ Event Grid
```

---

## 📊 Transaction Support at a Glance

| Feature | Service Bus | Event Hubs | Event Grid |
|---------|:-----------:|:----------:|:----------:|
| **Send Transaction** | ✅ | ⚠️ | ❌ |
| **Receive Transaction** | ✅ | ❌ | ❌ |
| **Rollback** | ✅ | ❌ | ❌ |
| **Message Lock** | ✅ | ❌ | ❌ |
| **Exactly-Once** | ✅ | ❌ | ❌ |
| **Dead-Letter Queue** | ✅ | ❌ | ⚠️ |

---

## 🔑 Key Transaction Patterns

### Service Bus: Full Transactions

```csharp
// ✅ ATOMIC: All succeed or all fail
using (var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
{
    var message = await receiver.ReceiveMessageAsync();
    await ProcessAsync(message);
    await database.SaveAsync();
    await receiver.CompleteMessageAsync(message);
    scope.Complete(); // COMMIT
}
```

**Guarantees:**
- ✅ Message locked during processing
- ✅ Rollback on failure (message returns to queue)
- ✅ Coordinates with database transactions
- ✅ Exactly-once processing possible

---

### Event Hubs: Manual Idempotency

```csharp
// ⚠️ NO TRANSACTION: Must handle duplicates
async Task ProcessEventAsync(ProcessEventArgs args)
{
    var eventId = args.Data.MessageId;
    
    // Check if already processed
    if (await IsProcessed(eventId))
        return; // Skip duplicate
    
    try
    {
        await ProcessAsync(args.Data);
        await MarkAsProcessed(eventId);
        await args.UpdateCheckpointAsync(); // ONLY checkpoint on success
    }
    catch
    {
        // Don't checkpoint - will retry
        throw;
    }
}
```

**Guarantees:**
- ⚠️ No message lock (events not locked)
- ⚠️ Must implement idempotency
- ⚠️ Checkpoint separate from processing
- ✅ Can replay from any offset

---

### Event Grid: HTTP-Based Acknowledgment

```csharp
// ❌ NO TRANSACTION: HTTP status determines retry
[HttpPost]
public async Task<IActionResult> HandleEvent([FromBody] EventGridEvent[] events)
{
    foreach (var evt in events)
    {
        if (await IsProcessed(evt.Id))
            continue; // Idempotency check
        
        try
        {
            await StoreEventAsync(evt); // Store first (durability)
            _ = Task.Run(() => ProcessAsync(evt)); // Background process
        }
        catch
        {
            return StatusCode(500); // Trigger retry
        }
    }
    return Ok(); // 200 = delivered
}
```

**Guarantees:**
- ❌ No message lock
- ❌ No rollback (once 200 returned)
- ⚠️ Must implement idempotency
- ✅ Automatic retries on 5xx

---

## 🎯 When to Use Each Service

### 🏆 Service Bus: Transactional Workflows

**Use When:**
- ✅ Transactions are critical
- ✅ Exactly-once processing required
- ✅ Order processing, payments, financial transactions
- ✅ Need rollback capability
- ✅ Multi-step workflows (sagas)

**Examples:**
- 💰 Payment processing
- 📦 Order fulfillment
- 🏦 Banking transactions
- 📊 Inventory management

---

### 📈 Event Hubs: High-Volume Streaming

**Use When:**
- ✅ Millions of events per second
- ✅ Need to replay historical data
- ✅ Multiple consumers at different speeds
- ⚠️ Can implement idempotency
- ⚠️ Eventual consistency acceptable

**Examples:**
- 📡 Telemetry ingestion (IoT)
- 📊 Log aggregation
- 🔍 Real-time analytics
- 📉 Time-series data

---

### ⚡ Event Grid: Event Distribution

**Use When:**
- ✅ Event-driven architecture
- ✅ Fast event fanout (push model)
- ✅ Azure service integration
- ✅ Serverless triggers
- ⚠️ Can implement idempotency

**Examples:**
- 🔔 Notification systems
- 🔄 Microservices events
- 🤖 Automation workflows
- 🎨 Media processing pipelines

---

## ⚠️ Common Pitfalls

### Service Bus
```csharp
// ❌ WRONG: Complete before processing
await receiver.CompleteMessageAsync(message);
await ProcessAsync(message); // If this fails, message is lost!

// ✅ RIGHT: Complete after processing
await ProcessAsync(message);
await receiver.CompleteMessageAsync(message);
```

### Event Hubs
```csharp
// ❌ WRONG: Checkpoint before processing
await args.UpdateCheckpointAsync();
await ProcessAsync(args.Data); // If this fails, event is lost!

// ✅ RIGHT: Checkpoint after processing
await ProcessAsync(args.Data);
await args.UpdateCheckpointAsync();
```

### Event Grid
```csharp
// ❌ WRONG: Return 200 before storing
return Ok();
await StoreAsync(evt); // This never runs!

// ✅ RIGHT: Store before returning 200
await StoreAsync(evt);
return Ok();
```

---

## 🔒 Reliability Patterns

### Pattern 1: Idempotency (All Services)
```csharp
// Always check if already processed
if (await IsProcessed(messageId))
    return; // Skip duplicate

await ProcessAsync(message);
await MarkAsProcessed(messageId);
```

### Pattern 2: Store-Then-Process (Event Grid/Hubs)
```csharp
// Store event first (durability)
await StoreAsync(event);

// Process asynchronously
_ = Task.Run(() => ProcessAsync(event));

// Return success quickly
return Ok();
```

### Pattern 3: Transaction Scope (Service Bus Only)
```csharp
// Coordinate multiple operations
using (var scope = new TransactionScope())
{
    await operation1.ExecuteAsync();
    await operation2.ExecuteAsync();
    await operation3.ExecuteAsync();
    scope.Complete(); // All or nothing
}
```

---

## 📝 Delivery Guarantees Comparison

### Service Bus
- ✅ **Exactly-Once:** With duplicate detection + Peek-Lock
- ✅ **At-Least-Once:** Default with Peek-Lock
- ⚠️ **At-Most-Once:** With Receive-and-Delete (not recommended)

### Event Hubs
- ✅ **At-Least-Once:** Checkpoint-based replay
- ⚠️ **Exactly-Once:** Must implement idempotency
- ❌ **At-Most-Once:** Not supported

### Event Grid
- ✅ **At-Least-Once:** Automatic retries
- ⚠️ **Exactly-Once:** Must implement idempotency
- ❌ **At-Most-Once:** Not supported (except 4xx errors)

---

## 🔧 Error Handling Strategies

### Service Bus: Abandon or Dead-Letter
```csharp
try
{
    await ProcessAsync(message);
    await receiver.CompleteMessageAsync(message);
}
catch (TransientException)
{
    await receiver.AbandonMessageAsync(message); // Retry
}
catch (PermanentException)
{
    await receiver.DeadLetterMessageAsync(message); // Manual review
}
```

### Event Hubs: Manual Retry or Dead-Letter
```csharp
int retries = 0;
while (retries < maxRetries)
{
    try
    {
        await ProcessAsync(eventData);
        await args.UpdateCheckpointAsync();
        break; // Success
    }
    catch
    {
        retries++;
        if (retries >= maxRetries)
            await SaveToDeadLetterAsync(eventData); // Manual
        else
            await Task.Delay(TimeSpan.FromSeconds(Math.Pow(2, retries)));
    }
}
```

### Event Grid: HTTP Status Code
```csharp
try
{
    await ProcessAsync(evt);
    return Ok(); // 200 = success
}
catch (TransientException)
{
    return StatusCode(500); // Event Grid retries
}
catch (InvalidDataException)
{
    return BadRequest(); // 400 = no retry, dead-letter
}
```

---

## 💡 Best Practices Summary

### Service Bus
1. ✅ Always use Peek-Lock mode
2. ✅ Use TransactionScope for multi-operation atomicity
3. ✅ Enable duplicate detection for exactly-once
4. ✅ Set appropriate lock duration for processing time
5. ✅ Monitor dead-letter queue regularly

### Event Hubs
1. ✅ Implement idempotent processing
2. ✅ Checkpoint only after successful processing
3. ✅ Store processed event IDs to prevent duplicates
4. ✅ Use batch processing for efficiency
5. ✅ Implement manual dead-letter mechanism

### Event Grid
1. ✅ Implement idempotent webhook handlers
2. ✅ Store events before processing (durability)
3. ✅ Return 200 quickly, process asynchronously
4. ✅ Return 5xx for transient errors (triggers retry)
5. ✅ Configure dead-letter blob storage

---

## 🎓 Decision Flowchart

```
┌─────────────────────────────────────┐
│ Do you need ACID transactions?     │
└─────────────┬───────────────────────┘
              │
              ├─ YES → Service Bus
              │         ├─ One consumer per message? → Queue
              │         └─ Multiple consumers? → Topic
              │
              └─ NO
                  │
                  ├─ Millions of events/sec? → Event Hubs
                  │                             └─ Implement idempotency
                  │
                  └─ Event-driven fanout? → Event Grid
                                            └─ Implement idempotency
```

---

## 📚 Additional Resources

- **Service Bus Transactions:** [azure_service_bus_details.md](azure_service_bus_details.md)
- **Event Hubs Details:** [azure_event_hubs_details.md](azure_event_hubs_details.md)
- **Event Grid Details:** [azure_event_grid_details.md](azure_event_grid_details.md)
- **Full Comparison:** [azure_messaging_transactional_nature.md](azure_messaging_transactional_nature.md)

---

## 🎯 Quick Commands Reference

### Service Bus
```csharp
// Transactional receive
using var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled);
var msg = await receiver.ReceiveMessageAsync();
await ProcessAsync(msg);
await receiver.CompleteMessageAsync(msg);
scope.Complete();
```

### Event Hubs
```csharp
// Idempotent process
if (!await IsProcessed(evt.MessageId)) {
    await ProcessAsync(evt);
    await MarkProcessed(evt.MessageId);
}
await args.UpdateCheckpointAsync();
```

### Event Grid
```csharp
// Durable webhook
await StoreAsync(evt);
_ = Task.Run(() => ProcessAsync(evt));
return Ok();
```
