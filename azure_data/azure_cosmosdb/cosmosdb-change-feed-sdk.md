# Consuming Azure Cosmos DB for NoSQL Change Feed Using the SDK

## Table of Contents

- [Overview](#overview)
- [Change Feed Architecture](#change-feed-architecture)
- [Core Components](#core-components)
  - [1. Monitored Container](#1-monitored-container)
  - [2. Lease Container](#2-lease-container)
  - [3. Host](#3-host)
  - [4. Delegate](#4-delegate)
- [Complete Working Example](#complete-working-example)
- [Configuration Options](#configuration-options)
  - [Start Position Options](#start-position-options)
  - [Performance Tuning](#performance-tuning)
- [Component Interaction Flow](#component-interaction-flow)
- [Azure Functions with Cosmos DB Trigger](#azure-functions-with-cosmos-db-trigger)
  - [When to Use Azure Functions for Change Feed Processing](#when-to-use-azure-functions-for-change-feed-processing)
  - [How Azure Functions Cosmos DB Trigger Works](#how-azure-functions-cosmos-db-trigger-works)
  - [Key Benefits of Azure Functions Approach](#key-benefits-of-azure-functions-approach)
  - [When to Use SDK vs Azure Functions](#when-to-use-sdk-vs-azure-functions)
- [Advanced Scenarios](#advanced-scenarios)
  - [Multiple Change Feed Processors](#multiple-change-feed-processors)
  - [Monitoring and Observability](#monitoring-and-observability)
- [Best Practices Summary](#best-practices-summary)
- [Common Pitfalls to Avoid](#common-pitfalls-to-avoid)
- [Resources](#resources)

## Overview

The Azure Cosmos DB change feed is a persistent record of changes to a container in the order they occur. It enables you to build efficient and scalable applications that can react to insert and update operations in near real-time. The change feed SDK provides a robust mechanism for consuming these changes with automatic state management and load distribution.

## Change Feed Architecture

The change feed processing architecture consists of four key components that work together to provide a reliable, scalable, and stateful change processing system.

```
┌─────────────────────────────────────────────────────────────┐
│                    Change Feed Processor                     │
│                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────────────┐  │
│  │   Host   │─────▶│ Delegate │─────▶│ Business Logic   │  │
│  └──────────┘      └──────────┘      └──────────────────┘  │
│       │                                                      │
│       │ Coordinates                                          │
│       ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Lease Container (State Store)             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │   │
│  │  │ Lease 1 │  │ Lease 2 │  │ Lease N │  ...         │   │
│  │  └─────────┘  └─────────┘  └─────────┘              │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                      │
│       │ Monitors                                             │
│       ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        Monitored Container (Source Data)             │   │
│  │    ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐          │   │
│  │    │ Doc1 │  │ Doc2 │  │ Doc3 │  │ Doc4 │  ...     │   │
│  │    └──────┘  └──────┘  └──────┘  └──────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Monitored Container

**Description:** The monitored container is the source Azure Cosmos DB container that you want to track for changes. It contains your application data and serves as the primary data store.

**Key Characteristics:**
- **Change Tracking:** Automatically tracks all insert and update operations
- **No Schema Changes:** Delete operations are NOT captured in the change feed
- **Partition-Aware:** Changes are tracked per logical partition
- **Ordered Guarantees:** Changes within a partition are ordered; across partitions they are not

**Important Notes:**
- The monitored container must exist before setting up change feed processing
- Changes are captured at the document level
- The change feed provides the most recent version of each changed document
- Historical versions are not maintained in the change feed

**Example Configuration:**
```csharp
// Reference to the monitored container
Container monitoredContainer = cosmosClient
    .GetDatabase("MyDatabase")
    .GetContainer("MyContainer");
```

### 2. Lease Container

**Description:** The lease container is a separate Azure Cosmos DB container that acts as a distributed state management system. It coordinates change feed processing across multiple consumer instances and tracks the progress of each partition reader.

**Key Characteristics:**
- **State Persistence:** Stores checkpoint information for each logical partition
- **Load Distribution:** Enables automatic work distribution among multiple hosts
- **Fault Tolerance:** Allows consumers to resume from the last processed position after failures
- **Dynamic Rebalancing:** Automatically redistributes partitions when hosts are added or removed

**Lease Document Structure:**
Each lease document in the lease container represents one logical partition of the monitored container and contains:
- **Partition Key:** Identifies which partition is being tracked
- **Owner:** The host instance currently processing this partition
- **Continuation Token:** The position in the change feed (checkpoint)
- **Timestamp:** Last update time
- **Expiration:** Lease timeout information

**Best Practices:**
- Use a dedicated container for leases (don't mix with application data)
- The lease container can be shared across multiple change feed processors monitoring different containers
- Provision adequate throughput (typically 400 RU/s is sufficient)
- Partition key should be `/id` for the lease container

**Example Configuration:**
```csharp
// Reference to the lease container
Container leaseContainer = cosmosClient
    .GetDatabase("MyDatabase")
    .GetContainer("leases");

// The lease container will be automatically created if it doesn't exist
// when using GetChangeFeedProcessorBuilder with automatic initialization
```

**Lease Container Sizing:**
- Number of lease documents = Number of physical partitions in monitored container
- Each lease document is small (~1-2 KB)
- Storage costs are minimal even for large-scale applications

### 3. Host

**Description:** The host is a client application instance that runs the change feed processor. It's responsible for reading changes from the monitored container, managing leases, and coordinating with other host instances.

**Key Characteristics:**
- **Instance Identity:** Each host has a unique name/identifier
- **Lease Ownership:** A host can own and process multiple partition leases
- **Automatic Scaling:** Multiple hosts can run in parallel, automatically distributing work
- **Health Monitoring:** Monitors lease ownership and handles failover scenarios

**Host Responsibilities:**
1. **Lease Acquisition:** Competes with other hosts to acquire partition leases
2. **Change Polling:** Continuously polls the monitored container for changes
3. **Delegation:** Passes batches of changes to the delegate for processing
4. **Checkpoint Management:** Updates lease continuation tokens after successful processing
5. **Rebalancing:** Releases or acquires leases as hosts are added or removed

**Scaling Behavior:**
- **Single Host:** Processes all partitions sequentially or in parallel
- **Multiple Hosts:** Work is distributed automatically
- **Max Parallelism:** One host per physical partition is optimal
- **Dynamic Scaling:** Hosts can be added or removed without downtime

**Example Implementation:**
```csharp
// Create a host instance with a unique name
var hostName = "Host-" + Guid.NewGuid().ToString();

ChangeFeedProcessor processor = monitoredContainer
    .GetChangeFeedProcessorBuilder<MyDocument>(
        processorName: "MyChangeFeedProcessor",
        onChangesDelegate: HandleChangesAsync)
    .WithInstanceName(hostName)  // Unique identifier for this host
    .WithLeaseContainer(leaseContainer)
    .WithStartTime(DateTime.UtcNow.AddHours(-1))  // Start from 1 hour ago
    .WithPollInterval(TimeSpan.FromSeconds(5))    // Check for changes every 5 seconds
    .WithMaxItems(100)                             // Process 100 items per batch
    .Build();

// Start the processor
await processor.StartAsync();
```

**Multiple Host Scenario:**
```csharp
// Host 1 - Processing partitions A, B
// Host 2 - Processing partitions C, D
// Host 3 - Processing partitions E, F

// When Host 2 fails:
// - Host 1 might acquire partition C
// - Host 3 might acquire partition D
// - Processing continues with automatic rebalancing
```

### 4. Delegate

**Description:** The delegate is a user-defined function or method that contains the business logic for processing each batch of changes. It's invoked by the host whenever new changes are detected in a partition.

**Key Characteristics:**
- **Batch Processing:** Receives changes in batches (not individual documents)
- **Async Execution:** Typically implemented as an async method
- **Error Handling:** Responsible for handling exceptions and retry logic
- **Idempotency:** Should be designed to handle duplicate processing

**Delegate Signature:**
```csharp
// Basic delegate signature
Func<IReadOnlyCollection<T>, CancellationToken, Task> onChangesDelegate

// Example implementation
async Task HandleChangesAsync(
    IReadOnlyCollection<MyDocument> changes,
    CancellationToken cancellationToken)
{
    // Your business logic here
}
```

**Delegate Best Practices:**

1. **Process Efficiently:**
```csharp
async Task HandleChangesAsync(
    IReadOnlyCollection<OrderDocument> changes,
    CancellationToken cancellationToken)
{
    foreach (var document in changes)
    {
        // Process each document
        await ProcessOrderAsync(document, cancellationToken);
    }
    
    // Checkpoint is automatically saved after successful completion
}
```

2. **Handle Errors Gracefully:**
```csharp
async Task HandleChangesAsync(
    IReadOnlyCollection<OrderDocument> changes,
    CancellationToken cancellationToken)
{
    var failedItems = new List<OrderDocument>();
    
    foreach (var document in changes)
    {
        try
        {
            await ProcessOrderAsync(document, cancellationToken);
        }
        catch (Exception ex)
        {
            // Log error but continue processing
            _logger.LogError(ex, "Failed to process document {Id}", document.Id);
            failedItems.Add(document);
        }
    }
    
    // Optionally send failed items to dead-letter queue
    if (failedItems.Any())
    {
        await SendToDeadLetterQueueAsync(failedItems);
    }
}
```

3. **Implement Idempotency:**
```csharp
async Task HandleChangesAsync(
    IReadOnlyCollection<OrderDocument> changes,
    CancellationToken cancellationToken)
{
    foreach (var document in changes)
    {
        // Check if already processed (idempotency check)
        if (await IsAlreadyProcessedAsync(document.Id))
        {
            _logger.LogInformation("Document {Id} already processed, skipping", document.Id);
            continue;
        }
        
        // Process the document
        await ProcessOrderAsync(document, cancellationToken);
        
        // Mark as processed
        await MarkAsProcessedAsync(document.Id);
    }
}
```

4. **Leverage Parallelism:**
```csharp
async Task HandleChangesAsync(
    IReadOnlyCollection<OrderDocument> changes,
    CancellationToken cancellationToken)
{
    // Process multiple documents in parallel
    var tasks = changes.Select(doc => 
        ProcessOrderAsync(doc, cancellationToken));
    
    await Task.WhenAll(tasks);
}
```

**Delegate Context:**
The delegate receives:
- **Changes:** A read-only collection of changed documents
- **Cancellation Token:** For graceful shutdown handling
- **Partition Context:** (Optional) Information about the source partition

**Performance Considerations:**
- Keep processing time reasonable to avoid lease timeouts
- Batch operations when possible (e.g., bulk database inserts)
- Use async/await properly to avoid blocking
- Consider implementing circuit breakers for external dependencies

## Complete Working Example

Here's a comprehensive example that brings all components together:

```csharp
using Microsoft.Azure.Cosmos;
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

public class ChangeFeedConsumerExample
{
    private readonly CosmosClient _cosmosClient;
    private readonly string _databaseName = "OrdersDB";
    private readonly string _containerName = "Orders";
    private readonly string _leaseContainerName = "leases";
    
    public ChangeFeedConsumerExample(string connectionString)
    {
        _cosmosClient = new CosmosClient(connectionString);
    }
    
    public async Task StartProcessingAsync()
    {
        // 1. Get reference to monitored container
        Container monitoredContainer = _cosmosClient
            .GetDatabase(_databaseName)
            .GetContainer(_containerName);
        
        // 2. Get reference to lease container
        Container leaseContainer = _cosmosClient
            .GetDatabase(_databaseName)
            .GetContainer(_leaseContainerName);
        
        // 3. Create host with unique instance name
        var hostName = $"OrderProcessor-{Environment.MachineName}-{Guid.NewGuid()}";
        
        // 4. Build the change feed processor
        ChangeFeedProcessor processor = monitoredContainer
            .GetChangeFeedProcessorBuilder<OrderDocument>(
                processorName: "OrderChangeFeedProcessor",
                onChangesDelegate: HandleOrderChangesAsync)  // Delegate
            .WithInstanceName(hostName)                      // Host identity
            .WithLeaseContainer(leaseContainer)              // Lease container
            .WithStartTime(DateTime.UtcNow)                  // Start from now
            .WithPollInterval(TimeSpan.FromSeconds(5))       // Poll every 5 seconds
            .WithMaxItems(100)                                // Batch size
            .WithErrorNotification(HandleErrorAsync)         // Error handler
            .Build();
        
        // 5. Start the processor
        await processor.StartAsync();
        Console.WriteLine($"Change Feed Processor started. Host: {hostName}");
        
        // Keep running until cancelled
        Console.WriteLine("Press any key to stop...");
        Console.ReadKey();
        
        // 6. Stop the processor gracefully
        await processor.StopAsync();
    }
    
    // Delegate: Business logic for processing changes
    private async Task HandleOrderChangesAsync(
        IReadOnlyCollection<OrderDocument> changes,
        CancellationToken cancellationToken)
    {
        Console.WriteLine($"Processing batch of {changes.Count} changes...");
        
        foreach (var order in changes)
        {
            try
            {
                // Implement your business logic here
                Console.WriteLine($"Processing order: {order.Id}, Status: {order.Status}");
                
                // Example: Send notification for new orders
                if (order.Status == "Created")
                {
                    await SendOrderNotificationAsync(order);
                }
                
                // Example: Update inventory
                if (order.Status == "Confirmed")
                {
                    await UpdateInventoryAsync(order);
                }
                
                // Example: Trigger shipment
                if (order.Status == "Shipped")
                {
                    await NotifyShippingServiceAsync(order);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing order {order.Id}: {ex.Message}");
                // Implement dead-letter queue or retry logic here
            }
        }
        
        Console.WriteLine($"Batch processing completed successfully.");
    }
    
    // Error notification handler
    private Task HandleErrorAsync(string leaseToken, Exception exception)
    {
        Console.WriteLine($"Error on lease {leaseToken}: {exception.Message}");
        
        // Implement custom error handling logic
        // - Log to monitoring system
        // - Send alerts
        // - Implement circuit breaker pattern
        
        return Task.CompletedTask;
    }
    
    // Example business logic methods
    private async Task SendOrderNotificationAsync(OrderDocument order)
    {
        // Send email, SMS, or push notification
        await Task.Delay(100); // Simulate async operation
        Console.WriteLine($"  → Notification sent for order {order.Id}");
    }
    
    private async Task UpdateInventoryAsync(OrderDocument order)
    {
        // Update inventory system
        await Task.Delay(100); // Simulate async operation
        Console.WriteLine($"  → Inventory updated for order {order.Id}");
    }
    
    private async Task NotifyShippingServiceAsync(OrderDocument order)
    {
        // Notify shipping service
        await Task.Delay(100); // Simulate async operation
        Console.WriteLine($"  → Shipping service notified for order {order.Id}");
    }
}

// Document model
public class OrderDocument
{
    public string Id { get; set; }
    public string CustomerId { get; set; }
    public string Status { get; set; }
    public decimal TotalAmount { get; set; }
    public List<OrderItem> Items { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

public class OrderItem
{
    public string ProductId { get; set; }
    public int Quantity { get; set; }
    public decimal Price { get; set; }
}
```

## Configuration Options

### Start Position Options

You can configure where the change feed processor should start reading:

```csharp
// Start from the beginning of time
.WithStartTime(DateTime.MinValue)

// Start from a specific point in time
.WithStartTime(DateTime.UtcNow.AddHours(-24))  // Last 24 hours

// Start from now (default)
.WithStartTime(DateTime.UtcNow)

// Continue from last checkpoint (when leases exist)
// This is automatic - no configuration needed
```

### Performance Tuning

```csharp
ChangeFeedProcessor processor = container
    .GetChangeFeedProcessorBuilder<MyDocument>(
        processorName: "MyProcessor",
        onChangesDelegate: HandleChangesAsync)
    .WithInstanceName(hostName)
    .WithLeaseContainer(leaseContainer)
    
    // Polling configuration
    .WithPollInterval(TimeSpan.FromSeconds(5))      // How often to check for changes
    
    // Batch size configuration
    .WithMaxItems(100)                              // Max items per batch
    
    // Lease configuration
    .WithLeaseAcquireInterval(TimeSpan.FromSeconds(13))   // How often to check for leases
    .WithLeaseExpirationInterval(TimeSpan.FromSeconds(60)) // Lease timeout
    .WithLeaseRenewInterval(TimeSpan.FromSeconds(17))     // How often to renew lease
    
    // Error handling
    .WithErrorNotification(HandleErrorAsync)
    
    .Build();
```

## Component Interaction Flow

```
1. Host starts and connects to lease container
   ↓
2. Host acquires one or more partition leases
   ↓
3. Host reads continuation token from lease
   ↓
4. Host polls monitored container for changes
   ↓
5. Changes detected in partition
   ↓
6. Host batches changes and invokes delegate
   ↓
7. Delegate processes business logic
   ↓
8. On success, host updates continuation token in lease
   ↓
9. Go back to step 4 (continuous polling)

If host fails:
- Lease expires after timeout
- Another host acquires the lease
- Processing resumes from last checkpoint
```

## Azure Functions with Cosmos DB Trigger

### When to Use Azure Functions for Change Feed Processing

For scenarios requiring **real-time analytics dashboards** or applications that need to process changes from Azure Cosmos DB with **automatic checkpointing** and **scaling across multiple consumers**, Azure Functions with Cosmos DB trigger is the recommended approach.

#### AZ-204 Exam Scenario

**Question:** You need to implement a real-time analytics dashboard that processes changes from an Azure Cosmos DB container. The solution must automatically handle checkpointing and scale across multiple consumers. Which approach should you use?

**Options and Analysis:**

| Approach | Recommended | Reason |
|----------|-------------|--------|
| **Azure Functions with Cosmos DB trigger** | ✅ **Correct** | Uses the change feed processor behind the scenes, providing automatic checkpointing and scaling across multiple instances without manual implementation |
| Direct change feed API with custom state management | ❌ | Requires implementing custom checkpointing and consumer coordination logic, which is more complex than necessary |
| Change feed pull model with manual checkpointing | ❌ | Requires manual implementation of checkpointing logic and load balancing across consumers, adding unnecessary complexity |
| Polling the container with a timer trigger | ❌ | Inefficient and doesn't provide real-time processing; requires manual change tracking implementation |

### How Azure Functions Cosmos DB Trigger Works

Azure Functions with Cosmos DB trigger uses the **change feed processor library internally**, providing all the benefits without the complexity of manual setup:

```
┌─────────────────────────────────────────────────────────────────┐
│               Azure Functions Runtime                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Cosmos DB Trigger (Built-in)                    │  │
│  │                                                           │  │
│  │  • Automatic lease management                            │  │
│  │  • Automatic checkpointing                               │  │
│  │  • Automatic scaling (multiple instances)                │  │
│  │  • Built-in retry logic                                  │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Your Function Code                           │  │
│  │         (Business Logic Only - No Boilerplate)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Azure Functions Example

```csharp
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

public class CosmosDbChangeFeedFunction
{
    private readonly ILogger _logger;

    public CosmosDbChangeFeedFunction(ILoggerFactory loggerFactory)
    {
        _logger = loggerFactory.CreateLogger<CosmosDbChangeFeedFunction>();
    }

    [Function("ProcessCosmosDBChanges")]
    public void Run(
        [CosmosDBTrigger(
            databaseName: "OrdersDB",
            containerName: "Orders",
            Connection = "CosmosDBConnection",
            LeaseContainerName = "leases",
            CreateLeaseContainerIfNotExists = true)] IReadOnlyList<Order> changes)
    {
        if (changes != null && changes.Count > 0)
        {
            _logger.LogInformation("Processing {Count} changes", changes.Count);
            
            foreach (var order in changes)
            {
                // Process each change - business logic only
                _logger.LogInformation("Order {Id} status: {Status}", 
                    order.Id, order.Status);
                
                // Send to analytics dashboard, update aggregates, etc.
            }
        }
    }
}

public class Order
{
    public string Id { get; set; }
    public string Status { get; set; }
    public decimal Amount { get; set; }
}
```

### Key Benefits of Azure Functions Approach

| Feature | Azure Functions Trigger | Manual SDK Implementation |
|---------|------------------------|---------------------------|
| **Checkpointing** | Automatic | Manual implementation required |
| **Scaling** | Automatic (KEDA-based or consumption plan) | Manual host coordination |
| **Lease Management** | Automatic | Manual lease container setup |
| **Infrastructure** | Serverless (no servers to manage) | Requires hosting infrastructure |
| **Cost Model** | Pay per execution | Pay for always-on infrastructure |
| **Setup Complexity** | Low (configuration-based) | High (code-based) |
| **Error Handling** | Built-in retry policies | Manual implementation |

### Configuration Options

```json
{
  "bindings": [
    {
      "type": "cosmosDBTrigger",
      "name": "changes",
      "direction": "in",
      "databaseName": "OrdersDB",
      "containerName": "Orders",
      "connection": "CosmosDBConnection",
      "leaseContainerName": "leases",
      "createLeaseContainerIfNotExists": true,
      "startFromBeginning": false,
      "maxItemsPerInvocation": 100,
      "preferredLocations": "West US 2"
    }
  ]
}
```

### When to Use SDK vs Azure Functions

| Use Case | Recommendation |
|----------|----------------|
| Real-time analytics dashboard | **Azure Functions** |
| Simple event processing with auto-scaling | **Azure Functions** |
| Complex processing with custom scaling logic | SDK with Change Feed Processor |
| Integration with existing .NET applications | SDK with Change Feed Processor |
| Containerized microservices architecture | SDK with Change Feed Processor |
| Need full control over checkpoint management | SDK with Change Feed Processor |

## Advanced Scenarios

### Multiple Change Feed Processors

You can have multiple processors monitoring the same container for different purposes:

```csharp
// Processor 1: Real-time notifications
ChangeFeedProcessor notificationProcessor = container
    .GetChangeFeedProcessorBuilder<Document>(
        processorName: "NotificationProcessor",
        onChangesDelegate: SendNotificationsAsync)
    .WithInstanceName("NotificationHost")
    .WithLeaseContainer(leaseContainer)
    .Build();

// Processor 2: Analytics and reporting
ChangeFeedProcessor analyticsProcessor = container
    .GetChangeFeedProcessorBuilder<Document>(
        processorName: "AnalyticsProcessor",
        onChangesDelegate: ProcessAnalyticsAsync)
    .WithInstanceName("AnalyticsHost")
    .WithLeaseContainer(leaseContainer)
    .Build();

// Both can run independently with separate checkpoints
```

### Monitoring and Observability

```csharp
private async Task HandleChangesAsync(
    IReadOnlyCollection<MyDocument> changes,
    CancellationToken cancellationToken)
{
    var stopwatch = System.Diagnostics.Stopwatch.StartNew();
    
    try
    {
        // Process changes
        foreach (var doc in changes)
        {
            await ProcessDocumentAsync(doc, cancellationToken);
        }
        
        // Log metrics
        stopwatch.Stop();
        _logger.LogInformation(
            "Processed {Count} documents in {Duration}ms",
            changes.Count,
            stopwatch.ElapsedMilliseconds);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Failed to process batch");
        throw; // Will be caught by error notification handler
    }
}
```

## Best Practices Summary

### Monitored Container
- Design for efficient change tracking (avoid frequent updates to same documents)
- Consider partition key design for balanced change distribution
- Monitor container throughput to avoid throttling

### Lease Container
- Use a dedicated container for leases
- Provision at least 400 RU/s
- Use `/id` as partition key
- Share across processors when appropriate

### Host
- Use descriptive and unique instance names
- Deploy multiple hosts for high availability
- Monitor lease distribution across hosts
- Implement graceful shutdown handling

### Delegate
- Keep processing logic efficient and non-blocking
- Implement proper error handling and retry logic
- Design for idempotency
- Use structured logging for observability
- Consider batch operations for performance
- Implement circuit breakers for external dependencies

## Common Pitfalls to Avoid

1. **Not Handling Deletes:** Change feed doesn't capture deletes. Implement soft deletes if needed.
2. **Lease Container Throttling:** Ensure adequate RU/s provisioned on lease container.
3. **Long-Running Delegates:** Keep processing time reasonable to avoid lease timeouts.
4. **Non-Idempotent Processing:** Always design delegates to handle duplicate processing.
5. **Ignoring Error Handling:** Implement comprehensive error handling and monitoring.
6. **Shared Processor Names:** Each processor monitoring the same container must have a unique name.

## Resources

- [Azure Cosmos DB Change Feed Documentation](https://learn.microsoft.com/azure/cosmos-db/change-feed)
- [Change Feed Processor in .NET SDK](https://learn.microsoft.com/azure/cosmos-db/nosql/change-feed-processor)
- [Change Feed Design Patterns](https://learn.microsoft.com/azure/cosmos-db/nosql/change-feed-design-patterns)
