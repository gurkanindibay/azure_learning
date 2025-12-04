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
10. [Hierarchical Partition Keys](#hierarchical-partition-keys)
    - [Understanding the 20 GB Logical Partition Limit](#understanding-the-20-gb-logical-partition-limit)
    - [What are Hierarchical Partition Keys?](#what-are-hierarchical-partition-keys)
    - [How Hierarchical Partition Keys Solve the 20 GB Problem](#how-hierarchical-partition-keys-solve-the-20-gb-problem)
    - [Multi-Tenant SaaS Best Practices with Hierarchical Partition Keys](#multi-tenant-saas-best-practices-with-hierarchical-partition-keys)
    - [Query Routing with Hierarchical Partition Keys](#query-routing-with-hierarchical-partition-keys)
11. [Change Feed](#change-feed)
    - [What is Change Feed?](#what-is-change-feed)
    - [Azure Functions Cosmos DB Trigger](#azure-functions-cosmos-db-trigger)
    - [Lease Collection Concept](#lease-collection-concept)
12. [Single Partition Queries vs Cross-Partition Queries](#single-partition-queries-vs-cross-partition-queries)
13. [Practice Questions](#practice-questions)

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
   - **Indexing Modes**:
     - **Consistent**: Updates the index synchronously as items are created, updated, or deleted. Adds overhead to write operations but ensures queries always return up-to-date results.
     - **None**: Disables indexing on the container entirely. Improves bulk write performance significantly. Ideal for bulk import scenarios - after bulk operations complete, you can change the indexing mode back to Consistent.
     - **Lazy** (Deprecated): Previously allowed asynchronous index updates. Not supported for new containers and requires special exemption which is rarely granted.
   - Note: "Automatic" is NOT an indexing mode - it's a separate property (`automatic: true/false`) that controls whether indexing happens automatically.

5. **Unique Keys**
   - Containers can enforce uniqueness constraints
   - Defined at container creation time (cannot be modified after)
   - Ensures specific properties have unique values **within a logical partition**
   - The partition key is implicitly part of the uniqueness scope
   - Use unique key policies (not indexing) to enforce uniqueness
   - Example: Unique key `/emailAddress` with partition key `/companyId` ensures emails are unique per company

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

## Hierarchical Partition Keys

### Understanding the 20 GB Logical Partition Limit

In Azure Cosmos DB, each **logical partition** has a maximum size limit of **20 GB**. A logical partition is defined by the partition key value - all items with the same partition key value belong to the same logical partition.

```
┌─────────────────────────────────────────────────────────────┐
│                    Physical Partition                        │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Logical Part A  │  │ Logical Part B  │                   │
│  │ (TenantId=T1)   │  │ (TenantId=T2)   │                   │
│  │ Max: 20 GB      │  │ Max: 20 GB      │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

**Problem with Standard Partition Keys for Large Tenants:**
- Using `TenantId` as a standard partition key limits each tenant to 20 GB
- Large tenants in multi-tenant SaaS applications can easily exceed this limit
- This creates a ceiling that prevents growth for large customers

### What are Hierarchical Partition Keys?

**Hierarchical partition keys** (also known as subpartitioning) allow you to define a partition key with up to **3 levels of hierarchy**. This feature enables a single logical partition key value (like TenantId) to exceed the 20 GB limit while maintaining efficient query routing.

```
┌─────────────────────────────────────────────────────────────┐
│           Hierarchical Partition Key Structure               │
│                                                              │
│  Level 1: TenantId                                           │
│     ├── Level 2: Year                                        │
│     │      ├── Level 3: Month                                │
│     │      │      └── Items (documents)                      │
│     │      └── ...                                           │
│     └── ...                                                  │
└─────────────────────────────────────────────────────────────┘
```

**Example Configuration:**
```csharp
// Define hierarchical partition key with multiple levels
ContainerProperties containerProperties = new ContainerProperties
{
    Id = "orders",
    PartitionKeyPaths = new List<string> 
    { 
        "/tenantId",    // Level 1: Tenant
        "/year",        // Level 2: Year
        "/month"        // Level 3: Month
    }
};

Container container = await database.CreateContainerIfNotExistsAsync(
    containerProperties,
    throughput: 400
);
```

### How Hierarchical Partition Keys Solve the 20 GB Problem

| Scenario | Standard Partition Key | Hierarchical Partition Key |
|----------|----------------------|---------------------------|
| **Partition Key** | `/tenantId` | `/tenantId`, `/year`, `/month` |
| **Logical Partition Limit** | 20 GB per TenantId | 20 GB per TenantId+Year+Month combination |
| **Large Tenant (100 GB)** | ❌ Exceeds limit | ✅ Distributed across multiple logical partitions |
| **Query by TenantId** | Single partition query | Still efficient - routes to relevant physical partitions |

**With hierarchical partition keys:**
- Data for TenantId="Contoso" is distributed across multiple logical partitions
- Each combination (Contoso, 2025, January), (Contoso, 2025, February), etc. has its own 20 GB limit
- Queries filtering by TenantId still route efficiently to the relevant physical partitions
- No cross-partition query penalty for tenant-specific queries

### Multi-Tenant SaaS Best Practices with Hierarchical Partition Keys

1. **Use TenantId as the First Level**
   - Ensures all tenant data is logically grouped
   - Enables efficient tenant-specific queries
   - Provides data isolation at query level

2. **Choose Second/Third Levels Based on Data Growth Pattern**
   - Time-based: `/year`, `/month` for time-series data
   - Category-based: `/region`, `/productCategory` for e-commerce
   - Entity-based: `/customerId`, `/orderId` for transactional data

3. **Consider Query Patterns**
   - Queries should include partition key levels from left to right
   - `WHERE tenantId = 'X' AND year = '2025'` is efficient
   - `WHERE year = '2025'` without tenantId becomes cross-partition

### Incorrect Approaches for Large Tenant Data

| Approach | Why It's Wrong |
|----------|----------------|
| **Random suffix appended to TenantId** | Scatters tenant data across partitions, making all tenant queries cross-partition operations (inefficient) |
| **Synthetic key combining TenantId and timestamp** | Distributes tenant data across multiple logical partitions but makes tenant-specific queries cross-partition and inefficient |
| **TenantId as standard partition key with increased throughput** | More throughput doesn't change the 20 GB logical partition limit - the data ceiling remains |

### Creating a Container with Hierarchical Partition Keys

**Using Azure CLI:**
```bash
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myResourceGroup \
  --database-name saas-db \
  --name orders \
  --partition-key-path "/tenantId" "/year" "/month"
```

**Using .NET SDK:**
```csharp
using Microsoft.Azure.Cosmos;

// Create container with hierarchical partition key
ContainerProperties properties = new ContainerProperties
{
    Id = "multi-tenant-orders",
    PartitionKeyPaths = new List<string> 
    { 
        "/tenantId", 
        "/year", 
        "/month" 
    }
};

Container container = await database.CreateContainerIfNotExistsAsync(
    properties,
    throughput: 400
);

// Insert item with hierarchical partition key
var order = new
{
    id = "order-001",
    tenantId = "contoso",
    year = "2025",
    month = "11",
    orderId = "ORD-12345",
    amount = 999.99
};

// Specify all levels of the partition key
await container.CreateItemAsync(
    order,
    new PartitionKeyBuilder()
        .Add("contoso")
        .Add("2025")
        .Add("11")
        .Build()
);
```

**Querying with Hierarchical Partition Keys:**
```csharp
// Efficient query - includes first level of partition key
QueryDefinition query = new QueryDefinition(
    "SELECT * FROM c WHERE c.tenantId = @tenantId AND c.year = @year")
    .WithParameter("@tenantId", "contoso")
    .WithParameter("@year", "2025");

// The query routes to relevant physical partitions for this tenant
FeedIterator<Order> iterator = container.GetItemQueryIterator<Order>(query);
```

### Query Routing with Hierarchical Partition Keys

When using hierarchical partition keys, understanding how to structure queries for efficient routing is crucial. The partition key hierarchy determines how queries are routed to physical partitions.

#### Query Routing Rules

| Partition Key Provided | Routing Behavior | Efficiency |
|------------------------|------------------|------------|
| **First level only** (e.g., tenantId) | Routes to all physical partitions containing that value | ✅ Efficient |
| **First + second level** (e.g., tenantId + year) | Routes to narrower set of partitions | ✅ More Efficient |
| **All levels** (e.g., tenantId + year + month) | Routes to specific partition | ✅ Most Efficient |
| **Lower level only** (e.g., userId without tenantId) | Fan-out to ALL partitions | ❌ Inefficient |
| **No partition key** (cross-partition) | Fan-out to ALL partitions | ❌ Inefficient |
| **Wildcards in partition key values** | Not supported | ❌ Invalid |

#### Example: Querying Across All Users for a Tenant

With hierarchical partition keys configured as `['/tenantId', '/userId']`:

```csharp
// EFFICIENT: Provide only tenantId to query all users for a tenant
var queryOptions = new QueryRequestOptions
{
    PartitionKey = new PartitionKeyBuilder()
        .Add("tenant-123")  // Only first level
        .Build()
};

QueryDefinition query = new QueryDefinition(
    "SELECT * FROM c WHERE c.tenantId = @tenantId")
    .WithParameter("@tenantId", "tenant-123");

// Routes to all physical partitions containing tenant-123's data
FeedIterator<Document> iterator = container.GetItemQueryIterator<Document>(query, requestOptions: queryOptions);
```

```csharp
// INEFFICIENT: Cross-partition query without partition key
var queryOptions = new QueryRequestOptions
{
    EnableCrossPartitionQuery = true  // Avoid this when possible
};

// This fans out to ALL physical partitions - very expensive!
FeedIterator<Document> iterator = container.GetItemQueryIterator<Document>(query, requestOptions: queryOptions);
```

```csharp
// INEFFICIENT: Providing only lower-level partition key
var queryOptions = new QueryRequestOptions
{
    PartitionKey = new PartitionKeyBuilder()
        .Add("user-456")  // Only userId without tenantId - BAD!
        .Build()
};

// This causes a fan-out because the hierarchy isn't respected
```

#### Key Takeaways for Query Routing

1. **Always provide partition key values from the top of the hierarchy**
   - Providing `tenantId` alone efficiently routes to tenant-specific partitions
   - You don't need to provide all levels of the hierarchy

2. **Lower-level keys without higher-level keys cause fan-out**
   - Providing `userId` without `tenantId` cannot leverage the partition hierarchy
   - Results in expensive cross-partition queries

3. **Wildcards are NOT supported**
   - You cannot use wildcard patterns in partition key values
   - Must provide actual values for the partition key levels you want to target

4. **Cross-partition queries should be avoided**
   - Enable only when absolutely necessary
   - Always try to include at least the first-level partition key

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

## Practice Questions

### Question 1: Azure Cosmos DB Change Feed Processing with Azure Functions

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

## Single Partition Queries vs Cross-Partition Queries

Understanding the difference between single partition queries and cross-partition queries is crucial for optimizing performance and cost in Azure Cosmos DB.

### What is a Single Partition Query?

A **single partition query** is a query that targets data within a single logical partition. This is achieved by including the partition key in the query's WHERE clause or by specifying it in the request options.

```csharp
// Single partition query - partition key specified
QueryDefinition query = new QueryDefinition(
    "SELECT * FROM c WHERE c.categoryId = @categoryId AND c.price < @maxPrice")
    .WithParameter("@categoryId", "electronics")
    .WithParameter("@maxPrice", 500);

FeedIterator<Product> iterator = container.GetItemQueryIterator<Product>(
    query,
    requestOptions: new QueryRequestOptions
    {
        PartitionKey = new PartitionKey("electronics")  // Targets single partition
    });
```

### What is a Cross-Partition Query?

A **cross-partition query** (also called a fan-out query) is a query that must search across multiple or all partitions because the partition key is not specified or not used in the filter.

```csharp
// Cross-partition query - no partition key specified
QueryDefinition query = new QueryDefinition(
    "SELECT * FROM c WHERE c.price < @maxPrice")
    .WithParameter("@maxPrice", 500);

FeedIterator<Product> iterator = container.GetItemQueryIterator<Product>(
    query,
    requestOptions: new QueryRequestOptions
    {
        MaxConcurrency = -1  // Allow parallel execution across partitions
    });
```

### Benefits of Single Partition Queries

| Benefit | Explanation |
|---------|-------------|
| **Lower Cost (Fewer RUs)** | Single partition queries consume significantly less Request Units (RUs) because they only need to access one partition instead of fanning out to multiple partitions |
| **Faster Execution** | By targeting a single partition, the system can retrieve and process data without coordinating across multiple partitions, resulting in faster execution times |
| **Better Scalability** | Focusing queries on single partitions distributes workload more effectively, reducing overall resource consumption and improving efficiency |
| **Predictable Performance** | Single partition queries offer more consistent and predictable latency since they avoid the overhead of cross-partition coordination |
| **Lower Network Overhead** | Reduced data transfer requirements as only one partition is accessed, leading to quicker response times |
| **Simpler Query Execution** | The system avoids the complexities of coordinating data retrieval across multiple partitions, resulting in a more streamlined operation |

### Comparison Table

| Aspect | Single Partition Query | Cross-Partition Query |
|--------|----------------------|----------------------|
| **RU Consumption** | Lower | Higher (proportional to partitions scanned) |
| **Latency** | Lower, predictable | Higher, variable |
| **Scalability** | Better | Can become a bottleneck |
| **Network Overhead** | Minimal | Higher (fan-out to multiple partitions) |
| **Execution Complexity** | Simple, direct | Complex, requires coordination |
| **Best For** | Point lookups, filtered queries | Aggregations, full scans |

### When Cross-Partition Queries Are Necessary

While single partition queries are preferred, cross-partition queries are sometimes unavoidable:

1. **Aggregations Across All Data**
   - COUNT, SUM, AVG across the entire container
   - Reporting and analytics queries

2. **Searches Without Partition Key**
   - Full-text search across all documents
   - Queries on non-partition key fields

3. **TOP N Queries Globally**
   - Finding top items across all partitions

### Best Practices

1. **Always Include Partition Key When Possible**
   ```csharp
   // Preferred: Include partition key in query
   var query = new QueryDefinition(
       "SELECT * FROM c WHERE c.userId = @userId AND c.status = @status")
       .WithParameter("@userId", "user123")  // Partition key
       .WithParameter("@status", "active");
   ```

2. **Design Partition Keys for Common Query Patterns**
   - Choose partition keys that align with your most frequent queries
   - Ensure queries naturally filter by partition key

3. **Monitor Query Metrics**
   ```csharp
   // Check if query crossed partitions
   FeedResponse<Product> response = await iterator.ReadNextAsync();
   Console.WriteLine($"Request Charge: {response.RequestCharge} RU");
   // Higher RU often indicates cross-partition query
   ```

4. **Use Composite Indexes for Complex Queries**
   - Optimize cross-partition queries that cannot be avoided
   - Reduce RU consumption with proper indexing

### Question 2: Single Partition vs Cross-Partition Query Benefits

**Question:** What is the benefit of using a query that only requires a single partition to execute versus a cross-partition query in Azure Cosmos DB?

**A.** Single partition queries do not require indexing, while cross-partition queries do.

**B.** Single partition queries incur lower costs because they consume less Request Units (RUs) than cross-partition queries. ✅

**C.** Single partition queries perform at the same speed as cross-partition queries, so there is no real advantage.

**D.** Single partition queries can return results that are eventually consistent, while cross-partition queries can only return strong consistency.

---

### Answer: B ✅

**Single partition queries incur lower costs because they consume less Request Units (RUs) than cross-partition queries.**

---

### Detailed Explanation

#### Why Option B is Correct

Single partition queries in Azure Cosmos DB provide several key advantages:

1. **Lower RU Consumption**
   - Queries target only one partition, avoiding the overhead of fanning out to multiple partitions
   - Each partition accessed adds to the total RU cost
   - Cross-partition queries multiply the base cost by the number of partitions scanned

2. **Better Scalability and Performance**
   - By focusing on a single partition, the system distributes workload more effectively
   - Reduces overall resource consumption
   - Improves efficiency of query execution

3. **Predictable Performance**
   - Single partition queries offer consistent latency
   - No coordination overhead across partitions
   - Faster data retrieval and processing

4. **Reduced Network Overhead**
   - Less data transfer required
   - Quicker response times
   - Lower latency for end users

#### Why Other Options Are Incorrect

**Option A - "Single partition queries do not require indexing"**
- **Incorrect**: Both single and cross-partition queries use indexes
- Indexing is independent of partition targeting
- Proper indexing improves performance for all query types

**Option C - "Same speed, no real advantage"**
- **Incorrect**: Single partition queries are significantly faster
- Cross-partition queries have coordination overhead
- The difference in performance can be substantial

**Option D - "Different consistency levels"**
- **Incorrect**: Consistency levels are independent of query partition scope
- Both query types respect the configured consistency level
- Consistency is set at account level or per-request, not per-query type

### Question 3: Multi-Tenant SaaS Application with Large Tenants

**Scenario:**

You are developing a multi-tenant SaaS application using Azure Cosmos DB. You need to ensure that data for large tenants can exceed 20 GB while maintaining efficient query performance within each tenant.

**Question:**

What should you configure?

**Select only one answer:**

**A.** A random suffix appended to TenantId as the partition key

**B.** Hierarchical partition keys with TenantId as the first level ✅

**C.** A synthetic partition key combining TenantId and timestamp

**D.** TenantId as a standard partition key with increased throughput

---

### Answer: B ✅

**Hierarchical partition keys with TenantId as the first level.**

---

### Detailed Explanation

#### Why Option B is Correct

**Hierarchical partition keys** allow a single TenantId to exceed the 20 GB logical partition limit while maintaining efficient query routing to relevant physical partitions.

1. **Overcomes the 20 GB Limit**
   - With hierarchical partition keys, data is distributed across multiple logical partitions
   - Each combination (TenantId + Level2 + Level3) has its own 20 GB limit
   - Large tenants can store hundreds of GB without hitting the ceiling

2. **Maintains Query Efficiency**
   - Queries that include TenantId are routed to the relevant physical partitions
   - No cross-partition query penalty for tenant-specific queries
   - The Cosmos DB engine understands the hierarchy and optimizes routing

3. **Example Configuration**
   ```csharp
   PartitionKeyPaths = new List<string> 
   { 
       "/tenantId",    // Level 1
       "/year",        // Level 2
       "/month"        // Level 3
   }
   ```

#### Why Other Options Are Incorrect

**Option A - Random suffix appended to TenantId**
- **Incorrect**: Random suffixes would scatter tenant data across partitions
- All tenant queries become cross-partition operations
- Severely impacts query performance and increases RU consumption
- Example: `TenantId-abc123`, `TenantId-xyz789` creates different partitions

**Option C - Synthetic partition key combining TenantId and timestamp**
- **Incorrect**: A synthetic key with timestamp would distribute tenant data across multiple logical partitions
- However, tenant-specific queries become cross-partition and inefficient
- The timestamp component doesn't provide hierarchical routing benefits
- Example: `TenantId_2025-11-30T10:30:00` creates a unique partition for each timestamp

**Option D - TenantId as standard partition key with increased throughput**
- **Incorrect**: Using TenantId as a standard partition key still limits each tenant to 20 GB per logical partition
- Increased throughput (RU/s) does NOT change the storage limit
- This doesn't solve the large tenant requirement at all
- More throughput = more operations per second, NOT more storage per partition

---

### Key Takeaways

1. **20 GB Limit is Per Logical Partition**
   - Each unique partition key value has a 20 GB ceiling
   - This is a fundamental Cosmos DB constraint

2. **Hierarchical Partition Keys Extend the Limit**
   - Distribute data across multiple logical partitions
   - Maintain query efficiency with intelligent routing
   - Support up to 3 levels of hierarchy

3. **Random/Synthetic Keys Break Query Efficiency**
   - Spreading data randomly makes targeted queries impossible
   - All tenant queries become expensive fan-out operations

4. **Throughput ≠ Storage Limit**
   - RU/s controls operations per second
   - Does not affect the 20 GB logical partition limit

---

### References

- [Hierarchical Partition Keys in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys)
- [Partitioning and Horizontal Scaling](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview)
- [Multi-tenant SaaS Patterns](https://learn.microsoft.com/azure/cosmos-db/nosql/multi-tenant)

---

### Question 4: Cosmos DB Indexing Mode for Bulk Write Performance

**Question:**
You have an Azure Cosmos DB container that stores IoT sensor data. You need to configure the indexing policy to improve bulk write performance while accepting eventual consistency for queries. Which indexing mode should you use?

**Options:**
- A) Automatic
- B) Consistent
- C) None
- D) Lazy

---

### Answer: C ✅

**Correct Answer: C) None**

---

### Detailed Explanation

**Option A - Automatic**
- **Incorrect**: "Automatic" is not a valid indexing mode
- The indexing policy has an `automatic` property that can be set to `true` or `false`
- The actual indexing modes are: Consistent, None, or the deprecated Lazy mode
- Don't confuse the `automatic` property with indexing modes

**Option B - Consistent**
- **Incorrect**: Consistent indexing mode updates the index synchronously as items are created, updated, or deleted
- This adds overhead to every write operation
- Reduces bulk write performance because each write must wait for the index to be updated
- Best for scenarios where query consistency is critical

**Option C - None** ✅
- **Correct**: Setting the indexing mode to None disables indexing on the container entirely
- This improves bulk write performance significantly because no indexing overhead is incurred
- After bulk operations complete, you can change the indexing mode back to Consistent
- Ideal for bulk import scenarios where you want to load data quickly
- Queries will still work but will perform full scans (which is acceptable during bulk import)

**Option D - Lazy**
- **Incorrect**: Lazy indexing mode is deprecated and not supported for new containers
- New containers cannot select lazy indexing
- Requesting lazy indexing requires a special exemption which is rarely granted
- Previously, it allowed asynchronous index updates but this is no longer available

---

### Key Takeaways

1. **Indexing Modes in Cosmos DB**
   - **Consistent**: Synchronous index updates, always up-to-date queries
   - **None**: No indexing, best for bulk write performance
   - **Lazy**: Deprecated, not available for new containers

2. **"Automatic" is NOT an Indexing Mode**
   - It's a separate boolean property in the indexing policy
   - Controls whether properties are automatically indexed
   - Don't confuse `automatic: true/false` with indexing modes

3. **Bulk Import Strategy**
   - Set indexing mode to `None` before bulk import
   - Perform bulk write operations
   - Change indexing mode back to `Consistent` after import completes
   - This approach significantly reduces RU consumption during import

4. **Trade-offs**
   - `None` mode: Fast writes, but queries perform full scans
   - `Consistent` mode: Slower writes, but efficient queries

---

### References

- [Indexing policies in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/index-policy)
- [Indexing modes in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/index-overview)

---

### Question 5: Unique Key Policy for Email Uniqueness Within Companies

**Question:**
You need to ensure that email addresses are unique within each company in an Azure Cosmos DB container. The partition key is `/companyId`. What should you configure?

**Options:**
- A) Create a unique key policy with path `/emailAddress`
- B) Set `/emailAddress` as the partition key
- C) Create a unique key policy with paths `/companyId` and `/emailAddress`
- D) Create a unique index on `/emailAddress` in the indexing policy

---

### Answer: A ✅

**Correct Answer: A) Create a unique key policy with path `/emailAddress`**

---

### Detailed Explanation

**Option A - Create a unique key policy with path `/emailAddress`** ✅
- **Correct**: A unique key with path `/emailAddress` combined with the partition key `/companyId` ensures email uniqueness within each company (logical partition)
- Unique keys in Cosmos DB are scoped to the logical partition (partition key value)
- This means the same email can exist in different companies, but not within the same company
- This is the correct way to enforce uniqueness constraints per partition

**Option B - Set `/emailAddress` as the partition key**
- **Incorrect**: Changing the partition key to `/emailAddress` would affect data distribution and query patterns
- Partition keys should be chosen based on:
  - Access patterns (how you query the data)
  - Data distribution (avoiding hot partitions)
  - Scalability requirements
- Partition keys are NOT designed for enforcing uniqueness requirements
- This would also break the company-based data organization

**Option C - Create a unique key policy with paths `/companyId` and `/emailAddress`**
- **Incorrect**: Including the partition key `/companyId` in the unique key paths is **redundant**
- The partition key is **implicitly part of the uniqueness constraint scope**
- Unique keys are already scoped to the partition key by design
- Adding `/companyId` to the unique key paths would create an incorrect and unnecessary constraint

**Option D - Create a unique index on `/emailAddress` in the indexing policy**
- **Incorrect**: **Indexing policies do not enforce uniqueness constraints**
- Indexes are for query performance optimization, not data integrity
- Unique keys must be defined in the **unique key policy** at container creation time
- You cannot enforce uniqueness through indexing configuration

---

### Key Concepts: Unique Keys in Cosmos DB

1. **Scope of Unique Keys**
   - Unique keys are scoped to the **logical partition** (partition key value)
   - Uniqueness is enforced **within** each partition, not across the entire container
   - Example: With partition key `/companyId`, unique key `/emailAddress` means:
     - `company1` + `user@example.com` ✅ Allowed
     - `company2` + `user@example.com` ✅ Allowed (different partition)
     - `company1` + `user@example.com` ❌ Rejected (duplicate in same partition)

2. **Unique Key Policy Definition**
   ```json
   {
     "uniqueKeyPolicy": {
       "uniqueKeys": [
         {
           "paths": ["/emailAddress"]
         }
       ]
     }
   }
   ```

3. **Important Constraints**
   - Unique keys must be defined at **container creation time**
   - Cannot be added or modified after the container is created
   - Maximum of 16 paths per unique key
   - Maximum of 10 unique key constraints per container
   - Unique key paths cannot exceed 100 characters

4. **Unique Keys vs Indexing vs Partition Keys**

   | Feature | Purpose | Enforces Uniqueness |
   |---------|---------|---------------------|
   | **Partition Key** | Data distribution & scalability | ❌ No |
   | **Indexing Policy** | Query performance optimization | ❌ No |
   | **Unique Key Policy** | Data integrity constraints | ✅ Yes (within partition) |

---

### References

- [Unique keys in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/unique-keys)
- [Define unique keys for Azure Cosmos DB containers](https://learn.microsoft.com/azure/cosmos-db/how-to-define-unique-keys)

---

### Question 6: Query Routing with Hierarchical Partition Keys

**Question:**
You have an Azure Cosmos DB container with hierarchical partition keys configured as `['/tenantId', '/userId']`. You need to query all documents for a specific tenant across all users. How should you structure your query to ensure it is efficiently routed?

**Options:**
- A) Provide only the tenantId value in the partition key parameter
- B) Enable cross-partition query and omit the partition key
- C) Provide userId only and filter by tenantId in the WHERE clause
- D) Provide both tenantId and a wildcard for userId

---

### Answer: A ✅

**Correct Answer: A) Provide only the tenantId value in the partition key parameter**

---

### Detailed Explanation

**Option A - Provide only the tenantId value in the partition key parameter** ✅
- **Correct**: When using hierarchical partition keys, providing only the first level (tenantId) routes the query to all physical partitions containing that tenant's data
- This efficiently handles the cross-user query requirement without scanning the entire container
- Cosmos DB understands the hierarchy and optimizes routing to only the relevant partitions
- Example:
  ```csharp
  var queryOptions = new QueryRequestOptions
  {
      PartitionKey = new PartitionKeyBuilder()
          .Add("tenant-123")  // Only first level
          .Build()
  };
  ```

**Option B - Enable cross-partition query and omit the partition key**
- **Incorrect**: This would create an inefficient fan-out query across ALL physical partitions in the container
- The query would scan partitions that don't contain the specific tenant's data
- Results in higher RU consumption and longer query times
- Only use cross-partition queries when you truly need data from multiple tenants

**Option C - Provide userId only and filter by tenantId in the WHERE clause**
- **Incorrect**: Providing only a lower-level partition key value (userId) without the higher levels creates a cross-partition query
- The partition key hierarchy must be respected from top to bottom
- This approach fans out to all physical partitions because Cosmos DB cannot route based on userId alone when tenantId is the first level
- The WHERE clause filter happens AFTER the partition routing, so it doesn't help with routing efficiency

**Option D - Provide both tenantId and a wildcard for userId**
- **Incorrect**: Wildcards are NOT supported in partition key values for hierarchical partition keys
- You cannot use patterns like `*`, `%`, or any other wildcard syntax
- This approach is invalid and will result in an error
- To query across all users, simply omit the userId level and provide only tenantId

---

### Key Concepts: Hierarchical Partition Key Query Routing

1. **Top-Down Routing**
   - Provide partition key values starting from the first level
   - You can stop at any level - you don't need all levels
   - Each additional level narrows the query scope

2. **Efficient Query Patterns**
   | Levels Provided | Routing Result |
   |----------------|----------------|
   | tenantId only | Routes to all tenant's partitions |
   | tenantId + userId | Routes to specific user's partition |
   | userId only (without tenantId) | Fan-out to ALL partitions ❌ |

3. **No Wildcard Support**
   - Partition key values must be exact matches
   - Use partial hierarchy (fewer levels) instead of wildcards

4. **Cross-Partition vs Partial Partition Key**
   - Cross-partition: No partition key, scans everything
   - Partial partition key: Provides top levels, efficient routing to subset

---

### References

- [Hierarchical Partition Keys in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/hierarchical-partition-keys)
- [Query items in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/nosql/query/getting-started)

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
