# Azure Functions - Cosmos DB Triggers
## Table of Contents

- [Overview](#overview)
- [Cosmos DB Bindings and Triggers](#cosmos-db-bindings-and-triggers)
  - [Types of Cosmos DB Integration](#types-of-cosmos-db-integration)
- [Cosmos DB Trigger](#cosmos-db-trigger)
  - [How It Works](#how-it-works)
  - [Change Feed Basics](#change-feed-basics)
  - [Trigger Configuration](#trigger-configuration)
  - [Important Parameters](#important-parameters)
    - [feedPollDelay](#feedpolldelay)
    - [maxItemsPerInvocation](#maxitemsperinvocation)
    - [startFromBeginning](#startfrombeginning)
    - [leaseCollectionName](#leasecollectionname)
    - [createLeaseCollectionIfNotExists](#createleasecollectionifnotexists)
- [Practice Question](#practice-question)
  - [Question: Processing Cosmos DB Changes with Minimal Latency](#question-processing-cosmos-db-changes-with-minimal-latency)
- [Cosmos DB Input Binding](#cosmos-db-input-binding)
  - [Purpose](#purpose)
  - [Configuration](#configuration)
  - [SQL Query Support](#sql-query-support)
- [Cosmos DB Output Binding](#cosmos-db-output-binding)
  - [Purpose](#purpose-2)
  - [Configuration](#configuration-2)
- [Complete Example: Change Feed Processing](#complete-example-change-feed-processing)
  - [Scenario](#scenario)
- [Best Practices](#best-practices)
  - [Performance Optimization](#performance-optimization)
  - [Cost Optimization](#cost-optimization)
  - [Reliability and Error Handling](#reliability-and-error-handling)
  - [Security Best Practices](#security-best-practices)
- [Common Scenarios](#common-scenarios)
  - [Scenario 1: Real-Time Data Synchronization](#scenario-1-real-time-data-synchronization)
  - [Scenario 2: Materialized Views](#scenario-2-materialized-views)
  - [Scenario 3: Event Streaming to Event Hub](#scenario-3-event-streaming-to-event-hub)
  - [Scenario 4: Data Enrichment](#scenario-4-data-enrichment)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
- [Monitoring and Diagnostics](#monitoring-and-diagnostics)
  - [Key Metrics to Monitor](#key-metrics-to-monitor)
  - [Monitoring Change Feed Lag](#monitoring-change-feed-lag)
  - [Setting Up Alerts](#setting-up-alerts)
- [Configuration Reference](#configuration-reference)
  - [Cosmos DB Trigger Properties](#cosmos-db-trigger-properties)
  - [Connection String Format](#connection-string-format)
- [Azure CLI Commands](#azure-cli-commands)
  - [Create Function App with Cosmos DB](#create-function-app-with-cosmos-db)
- [Additional Resources](#additional-resources)
- [Related Topics](#related-topics)


## Overview

Azure Functions provides native integration with Azure Cosmos DB through triggers and bindings. The Cosmos DB trigger uses the Azure Cosmos DB Change Feed to listen for inserts and updates across partitions, enabling real-time, event-driven architectures.

## Cosmos DB Bindings and Triggers

### Types of Cosmos DB Integration

| Type | Direction | Purpose | Use Case |
|------|-----------|---------|----------|
| **Trigger** | Input | Responds to changes in Cosmos DB | Process new/updated documents |
| **Input Binding** | Input | Reads documents from Cosmos DB | Retrieve documents by ID |
| **Output Binding** | Output | Writes documents to Cosmos DB | Save processed results |

## Cosmos DB Trigger

### How It Works

The Cosmos DB trigger uses the **Change Feed** feature of Azure Cosmos DB to monitor a container for changes (inserts and updates). When changes occur, the trigger automatically invokes your function.

**Architecture:**
```
Azure Cosmos DB Container
    ↓ (Change Feed)
Change Feed Processor (managed by Azure Functions)
    ↓ (Detects changes)
Azure Function Triggered
    ↓ (Processes changes)
Output (e.g., another container, queue, etc.)
```

**Key Components:**
1. **Monitored Container**: The container being watched for changes
2. **Leases Container**: Stores checkpoint information for tracking processed changes
3. **Change Feed Processor**: Reads changes and distributes them across function instances
4. **Function**: Your code that processes the changes

### Change Feed Basics

The Azure Cosmos DB Change Feed:
- Captures inserts and updates (not deletes)
- Provides a persistent, ordered log of changes
- Enables reading changes from a specific point in time
- Supports multiple consumers (parallel processing)
- Is available for all APIs (SQL, MongoDB, Cassandra, Gremlin, Table)

### Trigger Configuration

**Function.json (JavaScript/Python/PowerShell):**
```json
{
  "type": "cosmosDBTrigger",
  "name": "documents",
  "direction": "in",
  "connectionStringSetting": "CosmosDBConnection",
  "databaseName": "MyDatabase",
  "collectionName": "Container1",
  "leaseCollectionName": "leases",
  "createLeaseCollectionIfNotExists": true,
  "leasesCollectionThroughput": 400,
  "feedPollDelay": 5000,
  "maxItemsPerInvocation": 100,
  "startFromBeginning": false
}
```

**C# (.NET) - Attributes:**
```csharp
[FunctionName("CosmosDBTriggerFunction")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases",
        CreateLeaseCollectionIfNotExists = true,
        FeedPollDelay = 5000,
        MaxItemsPerInvocation = 100)]
    IReadOnlyList<Document> documents,
    ILogger log)
{
    if (documents != null && documents.Count > 0)
    {
        log.LogInformation($"Processing {documents.Count} documents");
        foreach (var doc in documents)
        {
            log.LogInformation($"Document Id: {doc.Id}");
            // Process document
        }
    }
}
```

### Important Parameters

#### feedPollDelay

Controls the delay (in milliseconds) between polling the partition for new changes after all current changes are processed.

- **Default**: 5000 (5 seconds)
- **Minimum**: 0 (immediate polling, higher RU consumption)
- **Purpose**: Balances responsiveness vs cost
- **Impact**: Lower values = faster detection, higher costs

**Example:**
```csharp
[CosmosDBTrigger(
    databaseName: "MyDatabase",
    collectionName: "Container1",
    ConnectionStringSetting = "CosmosDBConnection",
    FeedPollDelay = 0)] // Read changes immediately
```

#### maxItemsPerInvocation

The maximum number of items received per function invocation.

- **Default**: No limit (all available items)
- **Purpose**: Controls batch size
- **Impact**: Affects throughput and memory usage

#### startFromBeginning

Determines whether to read from the beginning of the change feed history or start from the current moment.

- **Default**: false (start from now)
- **true**: Process all historical changes
- **false**: Process only new changes

#### leaseCollectionName

The name of the container that stores lease information (checkpoints).

- **Required**: Yes
- **Purpose**: Tracks processing progress across partitions
- **Best Practice**: Use a separate container named "leases"

#### createLeaseCollectionIfNotExists

Whether to automatically create the leases container.

- **Default**: false
- **Recommendation**: true for development, false for production

## Practice Question

### Question: Processing Cosmos DB Changes with Minimal Latency

**Scenario:**
You have an Azure subscription that contains an Azure Cosmos DB Core (SQL) API account. The account hosts two Azure Cosmos DB containers named Container1 and Container2.

You have an Azure Functions app named FunctionApp1.

You plan to create a function in FunctionApp1 that will process changes to Container1, and then write the results to Container2.

You need to ensure that the function reads the changes to Container1 immediately. The solution must minimize costs.

**Question:**
What should you do?

**Options:**

1. ❌ Configure FunctionApp1 to use the Consumption plan
   - **Incorrect**: While the Consumption plan is cost-effective, the hosting plan itself does not control how quickly the Cosmos DB trigger polls for changes. The Consumption plan is already the default and most cost-effective option for event-driven workloads, but it doesn't directly affect change feed polling frequency. The polling behavior is determined by the trigger configuration, not the hosting plan.

2. ❌ Configure FunctionApp1 to use the Premium plan
   - **Incorrect**: The Premium plan provides benefits like pre-warmed instances, VNet integration, and no cold starts, but it does not affect how frequently the change feed processor polls for new changes. Upgrading to Premium would increase costs significantly without solving the immediate reading requirement. The polling delay is controlled by the function's trigger configuration, not the hosting plan tier.

3. ✅ Set the feedPollDelay parameter of the function to 0
   - **Correct**: The `feedPollDelay` parameter controls the delay (in milliseconds) between polling the Cosmos DB container for new changes after all current changes are drained. By default, this value is 5000ms (5 seconds), which introduces a delay between when a change occurs and when the function processes it. Setting `feedPollDelay` to 0 eliminates this delay, ensuring the function polls for and reads changes immediately. This approach achieves the requirement without upgrading the hosting plan, making it the most cost-effective solution. The trade-off is slightly higher RU consumption on the Cosmos DB container due to more frequent polling.

4. ❌ Set the feedPollDelay parameter of the function to -1
   - **Incorrect**: Setting `feedPollDelay` to -1 is invalid and would likely result in an error or default to a standard value. The `feedPollDelay` parameter expects a non-negative integer value in milliseconds. Negative values are not supported in the Cosmos DB trigger configuration. The correct value to minimize delay is 0, not -1.

## Cosmos DB Input Binding

### Purpose

Input bindings allow you to read one or more documents from Cosmos DB when your function executes.

### Configuration

**C# Example:**
```csharp
[FunctionName("GetDocument")]
public static IActionResult Run(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        Id = "{Query.id}",
        PartitionKey = "{Query.partitionKey}")]
    dynamic document,
    ILogger log)
{
    if (document == null)
    {
        return new NotFoundResult();
    }
    
    return new OkObjectResult(document);
}
```

**Function.json Example:**
```json
{
  "type": "cosmosDB",
  "name": "document",
  "direction": "in",
  "connectionStringSetting": "CosmosDBConnection",
  "databaseName": "MyDatabase",
  "collectionName": "Container1",
  "id": "{Query.id}",
  "partitionKey": "{Query.partitionKey}"
}
```

### SQL Query Support

You can also use SQL queries to retrieve multiple documents:

```csharp
[FunctionName("GetDocuments")]
public static IActionResult Run(
    [HttpTrigger(AuthorizationLevel.Function, "get")] HttpRequest req,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        SqlQuery = "SELECT * FROM c WHERE c.category = {Query.category}")]
    IEnumerable<dynamic> documents,
    ILogger log)
{
    return new OkObjectResult(documents);
}
```

## Cosmos DB Output Binding

### Purpose

Output bindings allow you to write documents to Cosmos DB from your function.

### Configuration

**C# Example:**
```csharp
[FunctionName("ProcessAndSave")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases")]
    IReadOnlyList<Document> input,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "Container2",
        ConnectionStringSetting = "CosmosDBConnection")]
    out dynamic output,
    ILogger log)
{
    output = new
    {
        id = Guid.NewGuid().ToString(),
        processedCount = input.Count,
        timestamp = DateTime.UtcNow
    };
    
    log.LogInformation($"Processed {input.Count} documents");
}
```

**Multiple Documents:**
```csharp
[FunctionName("ProcessMultiple")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases")]
    IReadOnlyList<Document> input,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "Container2",
        ConnectionStringSetting = "CosmosDBConnection")]
    IAsyncCollector<dynamic> output,
    ILogger log)
{
    foreach (var doc in input)
    {
        await output.AddAsync(new
        {
            id = Guid.NewGuid().ToString(),
            sourceId = doc.Id,
            processed = true,
            timestamp = DateTime.UtcNow
        });
    }
}
```

## Complete Example: Change Feed Processing

### Scenario

Process changes from Container1, transform the data, and write results to Container2.

**C# Implementation:**
```csharp
using System;
using System.Collections.Generic;
using Microsoft.Azure.Documents;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;

public static class CosmosDBChangeFeedProcessor
{
    [FunctionName("ProcessChanges")]
    public static async Task Run(
        [CosmosDBTrigger(
            databaseName: "MyDatabase",
            collectionName: "Container1",
            ConnectionStringSetting = "CosmosDBConnection",
            LeaseCollectionName = "leases",
            CreateLeaseCollectionIfNotExists = true,
            FeedPollDelay = 0,
            MaxItemsPerInvocation = 100)]
        IReadOnlyList<Document> documents,
        [CosmosDB(
            databaseName: "MyDatabase",
            collectionName: "Container2",
            ConnectionStringSetting = "CosmosDBConnection")]
        IAsyncCollector<dynamic> outputDocuments,
        ILogger log)
    {
        if (documents != null && documents.Count > 0)
        {
            log.LogInformation($"Processing {documents.Count} documents from Container1");
            
            foreach (var doc in documents)
            {
                try
                {
                    // Transform the document
                    var transformedDoc = new
                    {
                        id = Guid.NewGuid().ToString(),
                        sourceId = doc.Id,
                        originalData = JObject.Parse(doc.ToString()),
                        processedAt = DateTime.UtcNow,
                        status = "processed"
                    };
                    
                    // Write to Container2
                    await outputDocuments.AddAsync(transformedDoc);
                    
                    log.LogInformation($"Processed document: {doc.Id}");
                }
                catch (Exception ex)
                {
                    log.LogError($"Error processing document {doc.Id}: {ex.Message}");
                }
            }
            
            log.LogInformation($"Successfully processed {documents.Count} documents");
        }
    }
}
```

**local.settings.json:**
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet",
    "CosmosDBConnection": "AccountEndpoint=https://myaccount.documents.azure.com:443/;AccountKey=..."
  }
}
```

**Application Settings (Azure Portal):**
- Name: `CosmosDBConnection`
- Value: Your Cosmos DB connection string

## Best Practices

### Performance Optimization

1. **Set appropriate feedPollDelay**
   - Use 0 for near-real-time processing
   - Use 5000-10000ms for cost-effective batch processing
   - Balance latency requirements with RU consumption

2. **Configure maxItemsPerInvocation**
   - Limit batch size to prevent timeouts
   - Typical range: 100-1000 items
   - Consider function execution time limits

3. **Use dedicated leases container**
   - Store leases in a separate container
   - Provision appropriate throughput (400 RU/s minimum)
   - Enable autoscale for variable workloads

4. **Optimize partition strategy**
   - Ensure containers use effective partition keys
   - Distribute changes evenly across partitions
   - Avoid hot partitions

### Cost Optimization

1. **Right-size throughput**
   - Use autoscale for variable workloads
   - Monitor RU consumption
   - Optimize query patterns

2. **Batch processing**
   - Increase `feedPollDelay` for non-critical workloads
   - Process multiple items per invocation
   - Use `maxItemsPerInvocation` to control batch size

3. **Lease container management**
   - Use minimum throughput for leases (400 RU/s)
   - Enable autoscale if needed
   - Monitor lease container size

4. **Use Consumption plan**
   - Default choice for event-driven workloads
   - Pay only for execution time
   - Automatic scaling

### Reliability and Error Handling

1. **Implement retry logic**
   - Handle transient failures
   - Use exponential backoff
   - Log errors for monitoring

2. **Handle poison documents**
   - Catch exceptions per document
   - Don't let one bad document block the batch
   - Log problematic documents for investigation

3. **Monitor processing**
   - Use Application Insights
   - Track processing lag
   - Set up alerts for failures

4. **Checkpoint management**
   - Leases container handles checkpoints automatically
   - Don't delete leases manually (can cause reprocessing)
   - Back up lease container for disaster recovery

### Security Best Practices

1. **Use managed identities**
   - Avoid storing connection strings in code
   - Enable system-assigned or user-assigned identity
   - Grant appropriate RBAC permissions

2. **Store connection strings securely**
   - Use Azure Key Vault
   - Reference secrets via app settings
   - Never commit connection strings to source control

3. **Apply least privilege**
   - Grant only necessary permissions
   - Use role-based access control (RBAC)
   - Separate read and write permissions

4. **Enable private endpoints**
   - Use VNet integration (Premium/Dedicated plans)
   - Restrict Cosmos DB to private network
   - Disable public access when possible

## Common Scenarios

### Scenario 1: Real-Time Data Synchronization

**Use Case**: Sync changes between two Cosmos DB containers

```csharp
[FunctionName("SyncContainers")]
public static async Task Run(
    [CosmosDBTrigger(
        databaseName: "SourceDB",
        collectionName: "SourceContainer",
        ConnectionStringSetting = "SourceCosmosDB",
        LeaseCollectionName = "leases",
        FeedPollDelay = 0)]
    IReadOnlyList<Document> documents,
    [CosmosDB(
        databaseName: "TargetDB",
        collectionName: "TargetContainer",
        ConnectionStringSetting = "TargetCosmosDB")]
    IAsyncCollector<Document> output)
{
    foreach (var doc in documents)
    {
        await output.AddAsync(doc);
    }
}
```

### Scenario 2: Materialized Views

**Use Case**: Create aggregated views from raw data

```csharp
[FunctionName("MaterializedView")]
public static async Task Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "RawEvents",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases")]
    IReadOnlyList<Event> events,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "Aggregations",
        ConnectionStringSetting = "CosmosDBConnection")]
    IAsyncCollector<dynamic> aggregations,
    ILogger log)
{
    var grouped = events.GroupBy(e => e.Category);
    
    foreach (var group in grouped)
    {
        var aggregate = new
        {
            id = $"{group.Key}_{DateTime.UtcNow:yyyyMMddHH}",
            category = group.Key,
            count = group.Count(),
            totalValue = group.Sum(e => e.Value),
            timestamp = DateTime.UtcNow
        };
        
        await aggregations.AddAsync(aggregate);
    }
}
```

### Scenario 3: Event Streaming to Event Hub

**Use Case**: Stream Cosmos DB changes to Event Hub for downstream processing

```csharp
[FunctionName("StreamToEventHub")]
public static async Task Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "Events",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases",
        FeedPollDelay = 0)]
    IReadOnlyList<Document> documents,
    [EventHub("eventhub-name", Connection = "EventHubConnection")]
    IAsyncCollector<string> eventHubMessages,
    ILogger log)
{
    foreach (var doc in documents)
    {
        await eventHubMessages.AddAsync(doc.ToString());
    }
    
    log.LogInformation($"Streamed {documents.Count} events to Event Hub");
}
```

### Scenario 4: Data Enrichment

**Use Case**: Enrich documents with additional data before saving

```csharp
[FunctionName("EnrichDocuments")]
public static async Task Run(
    [CosmosDBTrigger(
        databaseName: "MyDatabase",
        collectionName: "RawData",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases")]
    IReadOnlyList<RawDocument> documents,
    [CosmosDB(
        databaseName: "MyDatabase",
        collectionName: "EnrichedData",
        ConnectionStringSetting = "CosmosDBConnection")]
    IAsyncCollector<dynamic> output,
    ILogger log)
{
    foreach (var doc in documents)
    {
        // Enrich with external data
        var enrichedData = await GetEnrichmentData(doc.Id);
        
        var enrichedDoc = new
        {
            id = Guid.NewGuid().ToString(),
            originalId = doc.Id,
            data = doc,
            enrichment = enrichedData,
            processedAt = DateTime.UtcNow
        };
        
        await output.AddAsync(enrichedDoc);
    }
}

private static async Task<object> GetEnrichmentData(string id)
{
    // Fetch additional data from external source
    return new { additionalInfo = "enriched data" };
}
```

## Troubleshooting

### Common Issues

**Problem**: Changes not being detected
- **Causes**: 
  - Incorrect connection string
  - Leases container doesn't exist
  - Function not running
- **Solutions**:
  - Verify connection string in app settings
  - Check if leases container exists or enable auto-creation
  - Ensure function app is running

**Problem**: Duplicate processing
- **Causes**:
  - Leases container was deleted
  - Multiple function apps using same leases
  - Function crashing before checkpoint
- **Solutions**:
  - Don't delete leases container
  - Use unique lease collection name per function
  - Implement idempotent processing logic

**Problem**: High RU consumption
- **Causes**:
  - Low `feedPollDelay` value
  - Too many function instances
  - Inefficient processing logic
- **Solutions**:
  - Increase `feedPollDelay` if immediate processing isn't required
  - Limit maximum instance count
  - Optimize function code

**Problem**: Processing lag
- **Causes**:
  - High volume of changes
  - Slow processing logic
  - Insufficient throughput
- **Solutions**:
  - Increase `maxItemsPerInvocation`
  - Optimize function performance
  - Scale up hosting plan
  - Increase Cosmos DB throughput

**Problem**: Function timeouts
- **Causes**:
  - Too many items per invocation
  - Long-running operations
  - External service delays
- **Solutions**:
  - Reduce `maxItemsPerInvocation`
  - Use async patterns
  - Implement timeouts for external calls
  - Consider Durable Functions for long-running workflows

## Monitoring and Diagnostics

### Key Metrics to Monitor

**Azure Functions Metrics:**
- Function execution count
- Function execution duration
- Function failures
- Function execution units

**Cosmos DB Metrics:**
- Request units consumed
- Total requests
- Throttled requests
- Change feed processing lag

**Application Insights:**
- Custom metrics
- Exception tracking
- Performance traces
- Dependency calls

### Monitoring Change Feed Lag

Use the Cosmos DB SDK to monitor change feed lag:

```csharp
var estimator = monitoredContainer.GetChangeFeedEstimatorBuilder()
    .WithLeaseContainer(leaseContainer)
    .WithPollInterval(TimeSpan.FromSeconds(30))
    .Build();

using (var iterator = estimator.GetCurrentStateIterator())
{
    while (iterator.HasMoreResults)
    {
        var estimations = await iterator.ReadNextAsync();
        foreach (var estimation in estimations)
        {
            log.LogInformation(
                $"Lease {estimation.LeaseToken}: {estimation.EstimatedLag} items behind");
        }
    }
}
```

### Setting Up Alerts

**Azure Monitor Alert Rules:**

1. **High RU consumption alert**:
   - Metric: Request Units
   - Condition: > 80% of provisioned RUs
   - Action: Send notification

2. **Function failure alert**:
   - Metric: Function Failures
   - Condition: > 5 failures in 5 minutes
   - Action: Send notification, trigger runbook

3. **Processing lag alert**:
   - Custom metric: Change feed lag
   - Condition: > 1000 documents behind
   - Action: Send notification

## Configuration Reference

### Cosmos DB Trigger Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `databaseName` | string | Database name | Required |
| `collectionName` | string | Monitored container name | Required |
| `connectionStringSetting` | string | App setting with connection string | Required |
| `leaseCollectionName` | string | Lease container name | "leases" |
| `createLeaseCollectionIfNotExists` | bool | Auto-create lease container | false |
| `leasesCollectionThroughput` | int | RU/s for lease container | 400 |
| `feedPollDelay` | int | Delay between polls (ms) | 5000 |
| `maxItemsPerInvocation` | int | Max items per function call | No limit |
| `startFromBeginning` | bool | Process historical changes | false |
| `preferredLocations` | string | Comma-separated regions | Empty |
| `useMultipleWriteLocations` | bool | Enable multi-region writes | false |

### Connection String Format

```
AccountEndpoint=https://<account-name>.documents.azure.com:443/;AccountKey=<account-key>;
```

## Azure CLI Commands

### Create Function App with Cosmos DB

```bash
# Create resource group
az group create --name MyResourceGroup --location eastus

# Create storage account
az storage account create \
  --name mystorageaccount \
  --resource-group MyResourceGroup \
  --location eastus \
  --sku Standard_LRS

# Create Cosmos DB account
az cosmosdb create \
  --name mycosmosaccount \
  --resource-group MyResourceGroup \
  --locations regionName=eastus

# Create database
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group MyResourceGroup \
  --name MyDatabase

# Create containers
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group MyResourceGroup \
  --database-name MyDatabase \
  --name Container1 \
  --partition-key-path "/id"

az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group MyResourceGroup \
  --database-name MyDatabase \
  --name Container2 \
  --partition-key-path "/id"

az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group MyResourceGroup \
  --database-name MyDatabase \
  --name leases \
  --partition-key-path "/id" \
  --throughput 400

# Create Function App
az functionapp create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --consumption-plan-location eastus \
  --runtime dotnet \
  --functions-version 4

# Get Cosmos DB connection string
az cosmosdb keys list \
  --name mycosmosaccount \
  --resource-group MyResourceGroup \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv

# Set connection string in Function App
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings "CosmosDBConnection=<connection-string>"
```

## Additional Resources

- [Azure Cosmos DB trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger)
- [Azure Cosmos DB input binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-input)
- [Azure Cosmos DB output binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-output)
- [Change feed in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed)
- [Quickstart: Respond to database changes using Azure Functions](https://learn.microsoft.com/en-us/azure/cosmos-db/sql/change-feed-functions)

## Related Topics

- Azure Functions hosting plans
- Azure Cosmos DB partitioning strategies
- Change feed processor
- Durable Functions for complex workflows
- Azure Functions best practices
