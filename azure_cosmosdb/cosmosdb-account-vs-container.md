# Azure Cosmos DB: Database Account vs Container

## Table of Contents

1. [Overview](#overview)
2. [Database Account](#database-account)
   - [What is a Database Account?](#what-is-a-database-account)
   - [Key Characteristics](#key-characteristics)
   - [Account-Level Features](#account-level-features)
3. [Container](#container)
   - [What is a Container?](#what-is-a-container)
   - [Key Characteristics](#key-characteristics-1)
   - [Container-Level Features](#container-level-features)
4. [Resource Hierarchy](#resource-hierarchy)
5. [Key Differences](#key-differences)
6. [Comparison Table](#comparison-table)
7. [Practical Examples](#practical-examples)
8. [When to Use Multiple Accounts vs Multiple Containers](#when-to-use-multiple-accounts-vs-multiple-containers)
9. [Best Practices](#best-practices)
10. [Change Feed](#change-feed)
    - [What is Change Feed?](#what-is-change-feed)
    - [Azure Functions Cosmos DB Trigger](#azure-functions-cosmos-db-trigger)
    - [Lease Collection Concept](#lease-collection-concept)
11. [Practice Question](#practice-question)

---

## Overview

Azure Cosmos DB has a hierarchical structure where **Database Account** and **Container** represent different levels of the resource hierarchy. Understanding the difference between them is crucial for proper architecture and management of your Cosmos DB resources.

---

## Database Account

### What is a Database Account?

A **Database Account** (also called Cosmos DB Account) is the top-level resource in Azure Cosmos DB. It represents your entire Cosmos DB instance and serves as the entry point for all operations.

```
Azure Subscription
    ↓
Resource Group
    ↓
Database Account ← YOU ARE HERE (Top Level)
    ↓
Database
    ↓
Container
    ↓
Items
```

### Key Characteristics

1. **Globally Unique Endpoint**
   - Each account has a unique endpoint URL: `https://<account-name>.documents.azure.com:443/`
   - This endpoint is used to connect to your Cosmos DB account

2. **Account-Wide Settings**
   - Default consistency level (Strong, Bounded Staleness, Session, Consistent Prefix, Eventual)
   - Geo-replication configuration
   - Multi-region write settings
   - Network security rules (firewalls, VNets)
   - Backup policies
   - Encryption settings

3. **Authentication & Security**
   - Master keys (primary and secondary)
   - Resource tokens
   - Azure Active Directory (Azure AD) integration
   - IP-based access control
   - VNet service endpoints

4. **Cost & Billing**
   - Billing is tracked at the account level
   - All databases and containers within the account contribute to the total cost
   - Regional pricing applies based on account location

5. **Global Distribution**
   - Accounts can be replicated across multiple Azure regions
   - Read and write regions are configured at the account level
   - Multi-region writes can be enabled account-wide

### Account-Level Features

| Feature | Description |
|---------|-------------|
| **Consistency Level** | Default consistency model for all reads (can be overridden per request) |
| **Geo-Replication** | Distribute data across multiple Azure regions |
| **Multi-Region Writes** | Enable writes in all replicated regions |
| **Backup & Restore** | Automatic backups configured at account level |
| **Private Endpoints** | Secure network connectivity via Azure Private Link |
| **Firewall Rules** | Control which IPs can access the account |
| **Keys & Tokens** | Account-level authentication credentials |
| **Monitoring** | Azure Monitor metrics and logs at account level |

---

## Container

### What is a Container?

A **Container** is a logical unit within a database that stores items (documents, rows, nodes, etc.). Containers are where your actual data lives and where throughput (RU/s) is provisioned.

```
Database Account
    ↓
Database
    ↓
Container ← YOU ARE HERE (Data Storage Level)
    ↓
Items (Documents)
```

### Key Characteristics

1. **Data Storage**
   - Containers store items (documents in NoSQL API)
   - Can hold unlimited amount of data (automatically scales)
   - Items are organized by partition key

2. **Partition Key**
   - Every container must have a partition key defined at creation
   - Partition key determines how data is distributed across partitions
   - Cannot be changed after container creation
   - Example: `/userId`, `/categoryId`, `/region`

3. **Throughput Provisioning**
   - Throughput (Request Units per second - RU/s) can be provisioned at container level
   - Minimum: 400 RU/s (manual) or 100 RU/s (autoscale)
   - Can be shared across containers using database-level throughput
   - Autoscale or manual throughput options

4. **Indexing Policy**
   - Each container has its own indexing policy
   - Defines which properties are indexed and how
   - Can be customized per container
   - Default: automatic indexing of all properties

5. **Unique Keys**
   - Containers can enforce uniqueness constraints
   - Defined at container creation time
   - Ensures specific properties have unique values within a partition

6. **Time to Live (TTL)**
   - TTL can be configured per container
   - Automatically deletes items after specified time
   - Can be set at container level (default) and overridden per item

### Container-Level Features

| Feature | Description |
|---------|-------------|
| **Partition Key** | Logical grouping for data distribution and scalability |
| **Throughput (RU/s)** | Provisioned capacity for read/write operations |
| **Indexing Policy** | Custom indexing strategy for query optimization |
| **Unique Keys** | Enforce uniqueness constraints within partitions |
| **TTL (Time to Live)** | Automatic expiration and deletion of items |
| **Change Feed** | Read-only log of changes to container items |
| **Stored Procedures** | Server-side JavaScript code execution |
| **Triggers** | Pre-triggers and post-triggers for items |
| **User-Defined Functions** | Custom functions for queries |
| **Conflict Resolution** | Policies for multi-region write conflicts |

---

## Resource Hierarchy

Complete hierarchy from top to bottom:

```
┌───────────────────────────────────────────────────┐
│        Azure Subscription                         │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│        Resource Group                             │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│        Database Account                           │
│  • Global endpoint                                │
│  • Consistency level                              │
│  • Geo-replication                                │
│  • Security & authentication                      │
│  • Backup & restore                               │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│        Database (Logical Grouping)                │
│  • Namespace for containers                       │
│  • Optional: shared throughput                    │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│        Container (Data Storage)                   │
│  • Partition key                                  │
│  • Throughput (RU/s)                              │
│  • Indexing policy                                │
│  • Items/documents                                │
└───────────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────────┐
│        Items (Documents/Records)                  │
│  • Your actual data                               │
│  • JSON documents (NoSQL API)                     │
└───────────────────────────────────────────────────┘
```

---

## Key Differences

### 1. **Scope & Purpose**

| Aspect | Database Account | Container |
|--------|-----------------|-----------|
| **Scope** | Top-level Azure resource | Data storage within a database |
| **Purpose** | Entry point and global configuration | Store and manage actual data items |
| **Analogy** | Like a SQL Server instance | Like a SQL table |

### 2. **Configuration**

| Aspect | Database Account | Container |
|--------|-----------------|-----------|
| **Endpoint** | Has unique global endpoint | Accessed via account endpoint |
| **Consistency** | Sets default consistency level | Inherits account default (can override) |
| **Replication** | Configures geo-distribution | Data automatically replicated |
| **Security** | Account-level authentication | No separate authentication |

### 3. **Data & Throughput**

| Aspect | Database Account | Container |
|--------|-----------------|-----------|
| **Data Storage** | No direct data storage | Stores actual items/documents |
| **Partition Key** | N/A | Must define at creation |
| **Throughput** | N/A | Provisioned at container or database level |
| **Scaling** | Account-wide limits | Individual container scaling |

### 4. **Cost & Billing**

| Aspect | Database Account | Container |
|--------|-----------------|-----------|
| **Billing Unit** | Account is billed for all usage | Containers consume throughput (RU/s) |
| **Cost Factors** | Storage + throughput + operations | Provisioned RU/s + storage consumed |

### 5. **Management**

| Aspect | Database Account | Container |
|--------|-----------------|-----------|
| **Creation** | Created via Azure Portal/CLI/ARM | Created within a database |
| **Deletion** | Deletes all databases and containers | Deletes all items within |
| **Migration** | Complex (account-level move) | Easier (container-level copy) |

---

## Comparison Table

| Feature | Database Account | Container |
|---------|-----------------|-----------|
| **Level in Hierarchy** | Top level (root) | Third level (under Database) |
| **Contains** | Databases | Items (documents) |
| **Endpoint** | Has unique URL endpoint | No separate endpoint |
| **Authentication** | Master keys, AAD | Uses account authentication |
| **Consistency Level** | Sets default | Inherits from account |
| **Geo-Replication** | Configured here | Automatically replicated |
| **Multi-Region Writes** | Enabled/disabled here | Automatically supported |
| **Throughput (RU/s)** | N/A | Provisioned here or at database level |
| **Partition Key** | N/A | Required at creation |
| **Indexing Policy** | N/A | Customizable per container |
| **Data Storage** | No direct storage | Stores items |
| **TTL** | N/A | Configurable per container |
| **Change Feed** | N/A | Available per container |
| **Pricing** | All resources billed to account | RU/s + storage costs |
| **Can be Moved** | Between subscriptions | Between databases (with effort) |
| **Creation Time** | Minutes | Seconds |
| **Deletion Impact** | Deletes everything | Deletes all items only |

---

## Practical Examples

### Creating Account and Container via .NET SDK

```csharp
using Microsoft.Azure.Cosmos;

// 1. ACCOUNT LEVEL: Connect to Database Account
string endpoint = "https://mycosmosaccount.documents.azure.com:443/";
string accountKey = "<your-account-key>";

// Create client - represents connection to the account
CosmosClient client = new CosmosClient(endpoint, accountKey);

// 2. DATABASE LEVEL: Create or get database
Database database = await client.CreateDatabaseIfNotExistsAsync("ecommerce-db");

// 3. CONTAINER LEVEL: Create container with partition key
ContainerProperties containerProperties = new ContainerProperties
{
    Id = "products",
    PartitionKeyPath = "/categoryId",
    // Container-specific indexing policy
    IndexingPolicy = new IndexingPolicy
    {
        Automatic = true,
        IndexingMode = IndexingMode.Consistent
    },
    // Container-specific TTL
    DefaultTimeToLive = -1  // -1 means no default TTL
};

// Provision throughput at container level
Container container = await database.CreateContainerIfNotExistsAsync(
    containerProperties,
    throughput: 400  // 400 RU/s
);

// 4. ITEM LEVEL: Add data to container
var product = new
{
    id = "product-1",
    categoryId = "electronics",
    name = "Laptop",
    price = 999.99
};

await container.CreateItemAsync(product, new PartitionKey("electronics"));
```

### Account-Level vs Container-Level Operations

```csharp
// ACCOUNT-LEVEL: Check account properties
AccountProperties accountProperties = await client.ReadAccountAsync();
Console.WriteLine($"Account ID: {accountProperties.Id}");
Console.WriteLine($"Read Regions: {string.Join(", ", accountProperties.ReadableRegions)}");
Console.WriteLine($"Write Regions: {string.Join(", ", accountProperties.WritableRegions)}");
Console.WriteLine($"Consistency: {accountProperties.Consistency.DefaultConsistencyLevel}");

// CONTAINER-LEVEL: Check container properties
ContainerProperties containerProps = await container.ReadContainerAsync();
Console.WriteLine($"Partition Key: {containerProps.PartitionKeyPath}");
Console.WriteLine($"Default TTL: {containerProps.DefaultTimeToLive}");
Console.WriteLine($"Indexing Mode: {containerProps.IndexingPolicy.IndexingMode}");

// Get container throughput
int? throughput = await container.ReadThroughputAsync();
Console.WriteLine($"Container Throughput: {throughput} RU/s");
```

### Azure CLI Examples

```bash
# ACCOUNT-LEVEL: Create Cosmos DB account
az cosmosdb create \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 \
  --default-consistency-level Session \
  --enable-automatic-failover true

# ACCOUNT-LEVEL: Add region to account
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 \
              regionName=westus failoverPriority=1

# DATABASE-LEVEL: Create database
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group myResourceGroup \
  --name ecommerce-db

# CONTAINER-LEVEL: Create container
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myResourceGroup \
  --database-name ecommerce-db \
  --name products \
  --partition-key-path "/categoryId" \
  --throughput 400
```

---

## When to Use Multiple Accounts vs Multiple Containers

### Use Multiple Database Accounts When:

1. **Different Regions/Geo-Distribution**
   - You need completely separate regional deployments
   - Regulatory requirements for data sovereignty

2. **Different Consistency Requirements**
   - Applications need different default consistency levels
   - Cannot be changed dynamically per request sufficiently

3. **Isolation & Security**
   - Complete isolation between environments (dev/test/prod)
   - Different Azure AD or authentication requirements
   - Separate billing and cost tracking

4. **Different Backup Policies**
   - Applications need different backup/restore schedules
   - Different retention policies

5. **Performance Isolation**
   - Mission-critical apps need guaranteed isolation
   - Prevent one application from affecting another

### Use Multiple Containers (Within Same Account) When:

1. **Different Data Types**
   - Users, Orders, Products, Reviews (different schemas)
   - Each entity type needs different partition key

2. **Different Throughput Needs**
   - Hot data needs high RU/s
   - Cold data needs minimal RU/s

3. **Different Indexing Requirements**
   - Some data needs full-text search indexing
   - Other data needs minimal indexing for cost savings

4. **Different Data Lifecycle**
   - Some data expires (needs TTL)
   - Other data is permanent

5. **Cost Optimization**
   - Share database-level throughput across containers
   - Allocate dedicated throughput only where needed

6. **Easier Management**
   - Single account, single endpoint, single authentication
   - Easier to manage and monitor

---

## Best Practices

### Database Account Best Practices

1. **Use a Single Account When Possible**
   - Simpler management and monitoring
   - Lower costs (one set of replicated regions)
   - Share resources efficiently

2. **Configure Consistency Appropriately**
   - Session consistency is default and sufficient for most scenarios
   - Use Strong only when absolutely necessary (impacts performance)

3. **Enable Geo-Replication for Production**
   - At least 2 regions for high availability
   - Use automatic failover for disaster recovery

4. **Secure Your Account**
   - Use Azure AD authentication where possible
   - Rotate keys regularly
   - Enable firewall rules and VNet integration
   - Use Private Endpoints for sensitive data

5. **Monitor Account Health**
   - Set up Azure Monitor alerts
   - Track availability, latency, and throttling
   - Monitor across all regions

### Container Best Practices

1. **Choose Partition Key Carefully**
   - High cardinality (many unique values)
   - Even distribution of data and requests
   - Commonly used in queries
   - Cannot be changed after creation!

2. **Right-Size Throughput**
   - Start with minimum (400 RU/s) and scale up
   - Use autoscale for variable workloads
   - Consider database-level throughput for multiple containers

3. **Optimize Indexing**
   - Include only necessary properties
   - Exclude large properties (arrays, nested objects)
   - Use composite indexes for common query patterns

4. **Use TTL When Appropriate**
   - Automatically clean up expired data
   - Reduce storage costs
   - Examples: session data, logs, temporary records

5. **Plan for Change Feed**
   - Use for real-time processing, analytics, or sync scenarios
   - Dedicate a lease container for change feed tracking

6. **Name Containers Meaningfully**
   - Use clear, descriptive names
   - Follow naming conventions: `users`, `orders`, `products`
   - Avoid special characters

---

## Change Feed

### What is Change Feed?

The **Change Feed** in Azure Cosmos DB is a persistent, ordered log of changes made to a container. It captures all insert and update operations on items in chronological order, making it ideal for real-time data processing, event-driven architectures, and data synchronization scenarios.

#### Key Characteristics of Change Feed

1. **Captures All Changes**
   - Records all inserts and updates to items in a container
   - Does NOT capture delete operations (use TTL flags as workaround)
   - Maintains changes for each logical partition

2. **Ordered by Partition**
   - Changes are ordered within each partition key
   - No guaranteed order across different partitions
   - Ensures consistency within partition boundaries

3. **Persistent and Durable**
   - Changes are stored and available for consumption
   - Retention period matches the container's backup retention
   - Can process historical changes from any point in time

4. **Multiple Consumers**
   - Multiple applications can read the same change feed independently
   - Each consumer tracks its own position (checkpoint)
   - Consumers don't affect each other

5. **Scalable Processing**
   - Automatically scales with container's partition count
   - Distributes processing across multiple workers
   - Load balancing handled automatically

#### Change Feed Use Cases

| Use Case | Description |
|----------|-------------|
| **Event-Driven Processing** | Trigger actions when data changes (e.g., send notifications) |
| **Real-Time Analytics** | Stream changes to analytics systems for real-time insights |
| **Data Synchronization** | Sync data between Cosmos DB containers or external systems |
| **Materialized Views** | Update aggregated or denormalized views based on source changes |
| **Audit Logging** | Track all changes for compliance and auditing |
| **Cache Invalidation** | Update caches when underlying data changes |
| **Search Index Updates** | Keep search indexes (e.g., Azure Cognitive Search) in sync |

#### Change Feed Consumption Models

**1. Change Feed Processor (Recommended)**
```csharp
// Using Change Feed Processor (push model)
Container monitoredContainer = client.GetContainer("db1", "Container1");
Container leaseContainer = client.GetContainer("db1", "leases");

ChangeFeedProcessor processor = monitoredContainer
    .GetChangeFeedProcessorBuilder<MyDocument>("myProcessor", HandleChangesAsync)
    .WithInstanceName("worker1")
    .WithLeaseContainer(leaseContainer)
    .Build();

await processor.StartAsync();

async Task HandleChangesAsync(
    IReadOnlyCollection<MyDocument> changes,
    CancellationToken cancellationToken)
{
    foreach (var doc in changes)
    {
        Console.WriteLine($"Processing change: {doc.id}");
        // Process each changed document
    }
}
```

**2. Azure Functions Cosmos DB Trigger (Simplified)**
```csharp
// Azure Function automatically handles change feed
[FunctionName("ProcessInventoryChanges")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "db1",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases",
        CreateLeaseCollectionIfNotExists = true)]
    IReadOnlyList<Document> documents,
    ILogger log)
{
    foreach (var doc in documents)
    {
        log.LogInformation($"Document modified: {doc.Id}");
    }
}
```

---

### Azure Functions Cosmos DB Trigger

The **Azure Cosmos DB Trigger** for Azure Functions is a serverless way to process changes from a Cosmos DB container's change feed. It automatically monitors a container and invokes your function whenever changes occur.

#### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Cosmos DB Account                        │
│  ┌────────────────────┐         ┌─────────────────────┐    │
│  │  Container1        │         │  Lease Container    │    │
│  │  (Monitored)       │         │  (Coordination)     │    │
│  │                    │         │                     │    │
│  │  [Item Updated]────┼────────►│  [Checkpoint]       │    │
│  │  [Item Inserted]   │         │  [Partition Leases] │    │
│  └────────────────────┘         └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
           │                                │
           │ Change Feed                    │ Lease Management
           ▼                                ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure Functions Runtime                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CosmosDB Trigger                                    │   │
│  │  • Polls change feed                                 │   │
│  │  • Manages leases automatically                      │   │
│  │  • Invokes function with batches of changes          │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Function1 (Your Code)                               │   │
│  │  • Processes changed documents                       │   │
│  │  • Updates inventory data                            │   │
│  │  • Performs business logic                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Key Components

**1. Monitored Container**
- The container you want to watch for changes
- Example: `Container1` storing inventory data
- Every insert/update triggers the change feed

**2. Lease Container**
- A separate container that stores checkpoint information
- Tracks which changes have been processed
- Enables resumption from last processed point after failures
- Coordinates multiple function instances for load balancing

**3. Azure Function**
- Your code that processes the changes
- Automatically invoked when changes are detected
- Receives batches of changed documents

#### Trigger Configuration Properties

| Property | Description | Default | Importance |
|----------|-------------|---------|------------|
| `databaseName` | Name of the database containing the monitored container | Required | High |
| `collectionName` | Name of the container to monitor (e.g., Container1) | Required | High |
| `ConnectionStringSetting` | App setting containing Cosmos DB connection string | Required | High |
| `LeaseCollectionName` | Name of the lease container | "leases" | High |
| `CreateLeaseCollectionIfNotExists` | Auto-create lease container if missing | false | High |
| `LeaseCollectionPrefix` | Prefix for lease documents (enables multiple functions) | null | Medium |
| `FeedPollDelay` | Delay between polling for changes (milliseconds) | 5000 | Medium |
| `MaxItemsPerInvocation` | Max documents per function invocation | Unlimited | Medium |
| `StartFromBeginning` | Process all historical changes on first run | false | Low |

#### Why Functions Might Fail to Run

**Common Issues:**

1. **Missing Lease Container**
   - Lease container doesn't exist
   - **Solution**: Set `CreateLeaseCollectionIfNotExists = true`

2. **Insufficient Throughput**
   - Lease container has insufficient RU/s
   - Monitored container is throttled
   - **Solution**: Provision at least 400 RU/s for lease container

3. **Connection String Issues**
   - Wrong connection string in app settings
   - Connection string missing or invalid
   - **Solution**: Verify `ConnectionStringSetting` points to correct app setting

4. **Lease Conflicts**
   - Multiple functions using same lease container without prefix
   - **Solution**: Use different `LeaseCollectionPrefix` for each function

5. **Function Timeout**
   - Processing takes too long for large batches
   - **Solution**: Set `MaxItemsPerInvocation` to smaller value

6. **Permissions**
   - Function doesn't have read/write access to containers
   - **Solution**: Verify connection string has appropriate permissions

---

### Lease Collection Concept

The **Lease Container** (also called Lease Collection) is a critical component for reliably processing Cosmos DB change feed. It acts as a distributed coordination system that tracks progress and manages work distribution.

#### What is a Lease Container?

A lease container is a separate Cosmos DB container that stores checkpoint information for change feed processing. Each lease document represents one logical partition of the monitored container.

**Important: Lease Container is NOT a Queue for Change Data**

A common misconception is that the lease container stores the actual change data. This is incorrect:

- **Lease Container Purpose**: Stores only checkpoint metadata and coordination information
- **Change Feed Location**: The actual change data remains in the monitored container (Container1)
- **Analogy**: Think of it like a bookmark in a book:
  - The **change feed** = The book itself (contains all the content)
  - The **lease container** = Your bookmark (tracks where you stopped reading)

```
┌─────────────────────────────────────┐
│  Container1 (Monitored)             │
│  ┌──────────────────────────────┐   │
│  │  Change Feed (Built-in Log)  │   │  ← Actual change data lives here
│  │  • Doc A inserted             │   │
│  │  • Doc B updated              │   │
│  │  • Doc C updated              │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
                ↓
         Function reads from
                ↓
┌─────────────────────────────────────┐
│  Lease Container                    │
│  ┌──────────────────────────────┐   │
│  │  Checkpoint Info ONLY        │   │  ← Just tracking metadata
│  │  • Partition 0: position 123 │   │
│  │  • Partition 1: position 456 │   │
│  │  • Owner: instance-1         │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

The lease container helps your function remember "I've processed changes up to this point" so it can resume correctly after a restart or failure, but it never stores the actual changed documents.

#### Lease Container Purpose

1. **Checkpoint Management**
   - Tracks the last processed position in the change feed
   - Enables resumption after failures or restarts
   - Prevents duplicate processing of changes

2. **Load Distribution**
   - Coordinates work across multiple function instances
   - Automatically distributes partitions among workers
   - Ensures each partition is processed by only one instance at a time

3. **Fault Tolerance**
   - If one function instance fails, another can take over
   - Lease expires after timeout, allowing rebalancing
   - Guarantees at-least-once delivery of changes

#### Lease Document Structure

Each lease document contains:

```json
{
  "id": "Container1..partition-0",
  "_etag": "\"00000000-0000-0000-0000-000000000000\"",
  "Owner": "function-instance-1",
  "ContinuationToken": "{\"V\":2,\"Rid\":\"...\",\"Continuation\":[...]}",
  "Timestamp": "2025-11-24T10:30:00Z",
  "ExpiresAt": "2025-11-24T10:31:00Z"
}
```

| Field | Description |
|-------|-------------|
| `id` | Identifies the partition (format: `{prefix}{containerName}..partition-{N}`) |
| `Owner` | Function instance currently processing this partition |
| `ContinuationToken` | Checkpoint position in the change feed |
| `Timestamp` | Last update time |
| `ExpiresAt` | Lease expiration time |

#### LeaseCollectionPrefix Property

The `LeaseCollectionPrefix` is used when multiple Azure Functions need to process the same container's change feed independently.

**Without Prefix:**
```csharp
// Function 1 - processes all changes
[CosmosDBTrigger(
    databaseName: "db1",
    collectionName: "Container1",
    LeaseCollectionName = "leases")]
```

**With Prefix (Multiple Functions):**
```csharp
// Function 1 - inventory updates
[CosmosDBTrigger(
    databaseName: "db1",
    collectionName: "Container1",
    LeaseCollectionName = "leases",
    LeaseCollectionPrefix = "inventory")]

// Function 2 - analytics processing
[CosmosDBTrigger(
    databaseName: "db1",
    collectionName: "Container1",
    LeaseCollectionName = "leases",
    LeaseCollectionPrefix = "analytics")]
```

**Common Misconception**: Setting `LeaseCollectionPrefix = "ALL"` does NOT make the function process all partitions. The prefix is just a string identifier to separate different consumers' lease documents in the same lease container.

#### Lease Container Requirements

1. **Partition Key**: Must be `/id`
2. **Throughput**: Minimum 400 RU/s recommended
3. **Location**: Can be in same or different database
4. **Naming**: Commonly named `leases`, but can be any valid name
5. **Creation**: Can be auto-created with `CreateLeaseCollectionIfNotExists = true`

#### Best Practices for Lease Container

```csharp
// Recommended configuration
[FunctionName("ProcessChanges")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "db1",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases",                    // Dedicated lease container
        CreateLeaseCollectionIfNotExists = true,           // Auto-create if missing
        LeaseCollectionPrefix = "inventory-processor",     // Unique prefix per function
        LeasesCollectionThroughput = 400,                  // Minimum throughput
        FeedPollDelay = 1000,                              // Check every second
        MaxItemsPerInvocation = 100)]                      // Process 100 docs at a time
    IReadOnlyList<Document> documents,
    ILogger log)
{
    log.LogInformation($"Processing {documents.Count} changes");
    foreach (var doc in documents)
    {
        // Process each changed document
    }
}
```

---

## Practice Question

### Azure Cosmos DB Change Feed Processing with Azure Functions

**Scenario:**

You have an Azure resource group that contains the following:
- An Azure Cosmos DB account named **Account1**
- An Azure function named **Function1**

Account1 contains:
- A database named **db1**
- A container named **Container1** that stores inventory data for a warehouse
- The data in Container1 is updated frequently

**Requirements:**
- Function1 must process updates to Container1 whenever data changes occur

**Problem:**
- Users report that the inventory data is inaccurate
- You discover that Function1 sometimes fails to run

**Question:**

You need to ensure that Function1 executes when data in Container1 is created or updated.

What should you do?

**Select only one answer:**

**A.** Configure Azure Event Grid to send the change feed of Container1 to the Event Grid topic to which Function1 is subscribed.

**B.** Configure Container1 to connect to an Azure Functions app. Connect the Azure Functions app to Function1.

**C.** Ensure that Function1 is listening to the change feed of Container1 by using the Azure Cosmos DB trigger. ✅

**D.** Ensure that the value of the LeaseCollectionPrefix property for Function1 is ALL.

---

### Answer: C ✅

**Ensure that Function1 is listening to the change feed of Container1 by using the Azure Cosmos DB trigger.**

---

### Detailed Explanation

#### Why Option C is Correct

The **Azure Cosmos DB Trigger** is the correct and recommended solution for the following reasons:

1. **Built-In Change Feed Integration**
   - The Cosmos DB trigger is specifically designed to process changes from a container's change feed
   - It automatically monitors Container1 and invokes Function1 whenever inserts or updates occur
   - No additional infrastructure or configuration needed

2. **Guaranteed Ordered Processing**
   - Change feed maintains order of changes within each partition
   - Ensures changes are processed in the sequence they occurred
   - Critical for maintaining data accuracy in inventory systems

3. **Automatic Checkpoint Management**
   - Uses lease container to track processed changes
   - Automatically resumes from last checkpoint after failures
   - Prevents missing or duplicate processing of changes

4. **Reliability and Fault Tolerance**
   - If Function1 fails, it automatically retries from the last checkpoint
   - Multiple instances can process different partitions in parallel
   - Built-in error handling and retry mechanisms

5. **Directly Addresses the Problem**
   - The issue is that Function1 "sometimes fails to run"
   - This indicates the trigger is not properly configured or missing
   - Implementing the Cosmos DB trigger ensures Function1 always executes on changes

**Correct Implementation:**

```csharp
[FunctionName("Function1")]
public static void Run(
    [CosmosDBTrigger(
        databaseName: "db1",
        collectionName: "Container1",
        ConnectionStringSetting = "CosmosDBConnection",
        LeaseCollectionName = "leases",
        CreateLeaseCollectionIfNotExists = true)]
    IReadOnlyList<Document> documents,
    ILogger log)
{
    foreach (var doc in documents)
    {
        log.LogInformation($"Processing inventory change: {doc.Id}");
        // Process inventory update
    }
}
```

---

#### Why Option A is Incorrect

**"Configure Azure Event Grid to send the change feed of Container1 to the Event Grid topic to which Function1 is subscribed."**

**Problems:**

1. **Additional Complexity**
   - Requires Event Grid integration setup
   - Adds extra components to maintain
   - More points of failure

2. **No Guaranteed Ordered Processing**
   - Event Grid does NOT guarantee order of event delivery
   - Events may arrive out of sequence
   - Critical issue for inventory data where order matters

3. **No Built-In Checkpointing**
   - Event Grid doesn't provide automatic checkpoint management
   - Must implement custom tracking of processed changes
   - Risk of missing changes or duplicate processing

4. **Not the Direct Solution**
   - While Event Grid can work with Cosmos DB, it's not the recommended approach for change feed processing
   - Cosmos DB trigger is purpose-built for this scenario

**When to use Event Grid:**
- Broadcasting events to multiple subscribers
- Loosely coupled event-driven architectures
- When order is not critical

---

#### Why Option B is Incorrect

**"Configure Container1 to connect to an Azure Functions app. Connect the Azure Functions app to Function1."**

**Problems:**

1. **Invalid Configuration**
   - Cosmos DB containers don't "connect" to Azure Functions directly
   - This is not a valid Azure configuration option
   - Misunderstands the relationship between services

2. **Vague and Non-Specific**
   - Doesn't specify HOW the connection would work
   - Doesn't address change feed processing
   - Doesn't explain the trigger mechanism

3. **Misses the Core Requirement**
   - Doesn't mention change feed at all
   - Doesn't explain how changes would be detected
   - Doesn't provide checkpoint or reliability mechanism

**The correct relationship:**
- Azure Function uses Cosmos DB Trigger (binding)
- Trigger monitors container's change feed
- Function invoked when changes occur

---

#### Why Option D is Incorrect

**"Ensure that the value of the LeaseCollectionPrefix property for Function1 is ALL."**

**Problems:**

1. **Misunderstands LeaseCollectionPrefix Purpose**
   - `LeaseCollectionPrefix` is a string identifier to separate different consumers
   - It does NOT control which partitions are processed
   - Setting it to "ALL" has no special meaning - it's just a prefix string

2. **All Partitions Processed by Default**
   - The Cosmos DB trigger automatically processes all partitions
   - No special configuration needed to process all changes
   - The trigger distributes work across all partitions automatically

3. **Doesn't Address Reliability**
   - The prefix affects lease document naming, not reliability
   - Doesn't solve the problem of Function1 failing to run
   - The issue is likely missing trigger configuration, not lease prefix

4. **Wrong Focus**
   - The problem is Function1 "sometimes fails to run"
   - This suggests trigger is not configured, not a lease prefix issue
   - Need to ensure trigger is properly set up first

**Correct Use of LeaseCollectionPrefix:**

```csharp
// Use prefix when multiple functions process same container
// Function 1 - inventory updates
[CosmosDBTrigger(
    LeaseCollectionPrefix = "inventory-processor")]  // Unique prefix

// Function 2 - analytics
[CosmosDBTrigger(
    LeaseCollectionPrefix = "analytics-processor")]  // Different prefix
```

---

### Key Takeaways

1. **Use Azure Cosmos DB Trigger for Change Processing**
   - Purpose-built for processing container changes
   - Handles checkpointing, retries, and load balancing automatically
   - Most reliable solution for change feed scenarios

2. **Lease Container is Essential**
   - Required for checkpoint management
   - Enables fault tolerance and resumption
   - Set `CreateLeaseCollectionIfNotExists = true` to auto-create

3. **Event Grid vs Cosmos DB Trigger**
   - Event Grid: Broadcasting events, no guaranteed order
   - Cosmos DB Trigger: Change feed processing, ordered within partition

4. **LeaseCollectionPrefix**
   - Used to separate multiple consumers of same change feed
   - Not related to processing "all" partitions
   - All partitions are processed by default

---

### References

- [Azure Functions Cosmos DB Trigger Documentation](https://learn.microsoft.com/azure/azure-functions/functions-bindings-cosmosdb-v2-trigger)
- [Change Feed in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/change-feed)
- [Change Feed Processor](https://learn.microsoft.com/azure/cosmos-db/change-feed-processor)

---

## Summary

### Database Account
- **What**: Top-level Azure resource and entry point
- **Purpose**: Global configuration, authentication, and geo-distribution
- **Contains**: Databases → Containers → Items
- **Key Features**: Endpoint, consistency, replication, security, billing

### Container
- **What**: Data storage unit within a database
- **Purpose**: Store and manage items/documents
- **Contains**: Items (documents, rows, nodes)
- **Key Features**: Partition key, throughput, indexing, TTL, Change Feed

### Change Feed
- **What**: Persistent log of all inserts and updates
- **Purpose**: Enable real-time processing of data changes
- **Consumed By**: Azure Functions Cosmos DB Trigger, Change Feed Processor
- **Key Features**: Ordered within partition, automatic checkpointing, fault-tolerant

### Remember
- **Account** = The "server" or "instance" (configuration and entry point)
- **Container** = The "table" (where your data lives)
- **Items** = The "rows" or "documents" (your actual data)
- **Change Feed** = The "transaction log" (record of all changes)
- **Lease Container** = The "checkpoint store" (tracks processing progress)

Understanding this hierarchy is crucial for designing scalable, cost-effective, and well-architected Azure Cosmos DB solutions.
