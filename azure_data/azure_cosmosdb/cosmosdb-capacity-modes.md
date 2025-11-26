# Azure Cosmos DB Capacity Modes

## Table of Contents

- [Overview](#overview)
- [Capacity Modes Comparison](#capacity-modes-comparison)
- [Provisioned Throughput](#provisioned-throughput)
  - [Characteristics](#characteristics)
  - [When to Use](#when-to-use)
  - [Manual Provisioned Throughput](#manual-provisioned-throughput)
  - [Autoscale Provisioned Throughput](#autoscale-provisioned-throughput)
  - [Shared vs Dedicated Throughput](#shared-vs-dedicated-throughput)
- [Serverless](#serverless)
  - [Characteristics](#characteristics-1)
  - [When to Use](#when-to-use-1)
  - [Limitations](#limitations)
  - [Code Example](#code-example)
- [Detailed Comparison](#detailed-comparison)
- [Choosing the Right Capacity Mode](#choosing-the-right-capacity-mode)
- [Cost Considerations](#cost-considerations)
  - [Provisioned Throughput Pricing](#provisioned-throughput-pricing)
  - [Serverless Pricing](#serverless-pricing)
  - [Cost Comparison Scenarios](#cost-comparison-scenarios)
- [Migration Between Capacity Modes](#migration-between-capacity-modes)
- [Best Practices](#best-practices)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [References](#references)

## Overview

Azure Cosmos DB offers different capacity modes that determine how you're charged for the throughput and storage your database consumes. Choosing the right capacity mode is critical for optimizing cost and performance based on your workload patterns.

## Capacity Modes Comparison

| Feature | Provisioned Throughput | Serverless |
|---------|----------------------|------------|
| **Billing Model** | Pre-provisioned RU/s (hourly) | Consumption-based (per request) |
| **Best For** | Predictable, sustained traffic | Intermittent, unpredictable traffic |
| **RU/s Configuration** | Manual or Autoscale | Automatic (no configuration) |
| **Maximum RU/s** | Unlimited (can scale up) | 5,000 RU/s per container |
| **Storage Limit** | Unlimited | 50 GB per container |
| **SLA** | 99.99% availability | 99.9% availability |
| **Multi-region Writes** | ✅ Supported | ❌ Not supported |
| **Analytical Store** | ✅ Supported | ❌ Not supported |
| **Backup** | Continuous and periodic | Periodic only |
| **Cost When Idle** | Pay for provisioned capacity | No charge |

## Provisioned Throughput

### Characteristics

- Pre-provision throughput measured in **Request Units per second (RU/s)**
- Billed hourly for the throughput you provision
- **Pay even when idle** (you're paying for provisioned capacity)
- Guarantees predictable performance
- Two configuration options:
  1. **Manual/Standard**: Fixed RU/s that you manually adjust
  2. **Autoscale**: Automatically scales RU/s based on usage

### When to Use

✅ **Use Provisioned Throughput when:**
- Sustained, predictable workloads
- Mission-critical applications requiring consistent performance
- High-throughput applications (>5,000 RU/s)
- Need multi-region writes
- Require analytical store (Azure Synapse Link)
- Storage exceeds 50 GB per container
- Cost-effective for steady traffic (continuous usage)

### Manual Provisioned Throughput

**Description:** Fixed amount of RU/s that remains constant until you manually change it.

**Characteristics:**
- Set a specific RU/s value (minimum 400 RU/s)
- Throughput stays constant
- You manually scale up or down based on needs
- Most cost-effective when workload is consistent

**Code Example:**
```csharp
using Microsoft.Azure.Cosmos;

// Create database with manual provisioned throughput
Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(
    id: "MyDatabase",
    throughput: 400 // 400 RU/s
);

// Create container with manual provisioned throughput
Container container = await database.CreateContainerIfNotExistsAsync(
    id: "MyContainer",
    partitionKeyPath: "/customerId",
    throughput: 1000 // 1000 RU/s
);

// Scale up throughput later
await container.ReplaceThroughputAsync(2000); // Scale to 2000 RU/s
```

**Azure CLI:**
```bash
# Create database with manual provisioned throughput
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --name MyDatabase \
  --throughput 400

# Create container with manual provisioned throughput
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --database-name MyDatabase \
  --name MyContainer \
  --partition-key-path "/customerId" \
  --throughput 1000

# Update throughput
az cosmosdb sql container throughput update \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --database-name MyDatabase \
  --name MyContainer \
  --throughput 2000
```

### Autoscale Provisioned Throughput

**Description:** Automatically scales throughput between 10% and 100% of the maximum RU/s based on usage.

**Characteristics:**
- Set maximum RU/s (Tmax)
- System automatically scales between Tmax/10 and Tmax
- Scales up instantly when needed
- Scales down when traffic decreases
- Billed for the **highest RU/s used in each hour**
- Ideal for variable or unpredictable workloads

**Scaling Behavior:**
- Minimum RU/s: Tmax ÷ 10
- Maximum RU/s: Tmax
- Example: If Tmax = 10,000 RU/s
  - Minimum: 1,000 RU/s
  - Maximum: 10,000 RU/s

**Code Example:**
```csharp
using Microsoft.Azure.Cosmos;

// Create database with autoscale
ThroughputProperties autoscaleThroughput = ThroughputProperties.CreateAutoscaleThroughput(4000);

Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(
    id: "MyDatabase",
    throughputProperties: autoscaleThroughput
);

// Create container with autoscale
Container container = await database.CreateContainerIfNotExistsAsync(
    id: "MyContainer",
    partitionKeyPath: "/customerId",
    throughputProperties: ThroughputProperties.CreateAutoscaleThroughput(10000)
);

// Check current throughput
int? currentThroughput = await container.ReadThroughputAsync();
Console.WriteLine($"Current throughput: {currentThroughput} RU/s");

// Update max autoscale throughput
await container.ReplaceThroughputAsync(
    ThroughputProperties.CreateAutoscaleThroughput(20000)
);
```

**Azure CLI:**
```bash
# Create database with autoscale
az cosmosdb sql database create \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --name MyDatabase \
  --max-throughput 4000

# Create container with autoscale
az cosmosdb sql container create \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --database-name MyDatabase \
  --name MyContainer \
  --partition-key-path "/customerId" \
  --max-throughput 10000

# Update max autoscale throughput
az cosmosdb sql container throughput update \
  --account-name mycosmosaccount \
  --resource-group myresourcegroup \
  --database-name MyDatabase \
  --name MyContainer \
  --max-throughput 20000
```

**When to Use Autoscale:**
- Variable traffic patterns
- Unpredictable spikes in usage
- Development/testing environments
- New applications with unknown usage patterns
- Want to avoid manual throughput management

**Cost Comparison: Manual vs Autoscale**

| Scenario | Manual (Fixed 10,000 RU/s) | Autoscale (Max 10,000 RU/s) |
|----------|---------------------------|----------------------------|
| Constant 10,000 RU/s | $X | $1.5X |
| Average 5,000 RU/s | $X (overpaying) | $0.75X - $1.5X |
| Spiky traffic | Manual scaling required | Automatic scaling |

*Note: Autoscale costs approximately 1.5x the manual rate when running at max RU/s*

### Shared vs Dedicated Throughput

**Database-Level (Shared) Throughput:**
- Provision throughput at database level
- Shared across all containers in the database
- Cost-effective for many containers with low individual throughput
- Minimum 400 RU/s (max 1,000,000 RU/s)

```csharp
// Database with shared throughput
Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(
    id: "SharedDatabase",
    throughput: 1000 // Shared across all containers
);

// Containers created without specifying throughput inherit from database
Container container1 = await database.CreateContainerIfNotExistsAsync(
    id: "Container1",
    partitionKeyPath: "/id"
    // No throughput specified - uses shared database throughput
);

Container container2 = await database.CreateContainerIfNotExistsAsync(
    id: "Container2",
    partitionKeyPath: "/id"
    // No throughput specified - uses shared database throughput
);
```

**Container-Level (Dedicated) Throughput:**
- Provision throughput for specific container
- Guaranteed RU/s for that container
- Better performance isolation
- More expensive for many containers

```csharp
// Container with dedicated throughput
Container container = await database.CreateContainerIfNotExistsAsync(
    id: "DedicatedContainer",
    partitionKeyPath: "/customerId",
    throughput: 5000 // Dedicated 5000 RU/s for this container
);
```

**Mix of Shared and Dedicated:**
```csharp
// Database with shared throughput
Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(
    id: "MixedDatabase",
    throughput: 1000
);

// Container using shared throughput
Container sharedContainer = await database.CreateContainerIfNotExistsAsync(
    id: "SharedContainer",
    partitionKeyPath: "/id"
);

// Container with dedicated throughput
Container dedicatedContainer = await database.CreateContainerIfNotExistsAsync(
    id: "HighTrafficContainer",
    partitionKeyPath: "/userId",
    throughput: 10000 // Dedicated throughput
);
```

## Serverless

### Characteristics

- **Consumption-based billing**: Pay only for Request Units consumed
- **No pre-provisioning required**: Automatically allocates resources
- **No charge when idle**: Perfect for intermittent workloads
- Automatic scaling up to 5,000 RU/s per container
- 99.9% availability SLA (vs 99.99% for provisioned)
- Single-region writes only (no multi-region writes)

### When to Use

✅ **Use Serverless when:**
- Development and testing environments
- Intermittent or unpredictable traffic
- New applications with unknown traffic patterns
- Low-volume applications
- Proof-of-concepts and prototypes
- Applications with periods of zero traffic
- Cost optimization for variable workloads
- Storage requirements under 50 GB per container

❌ **Don't use Serverless when:**
- Need sustained throughput > 5,000 RU/s
- Storage exceeds 50 GB per container
- Require multi-region writes
- Need analytical store (Synapse Link)
- Mission-critical applications requiring 99.99% SLA

### Limitations

| Limitation | Serverless | Provisioned |
|-----------|------------|-------------|
| Max RU/s per container | 5,000 | Unlimited |
| Max storage per container | 50 GB | Unlimited |
| Multi-region writes | ❌ | ✅ |
| Analytical store | ❌ | ✅ |
| Backup options | Periodic only | Continuous & Periodic |
| Availability SLA | 99.9% | 99.99% |

### Code Example

```csharp
using Microsoft.Azure.Cosmos;

// Create Cosmos DB account with serverless capacity mode (via Azure Portal or ARM template)
// Note: Capacity mode is set at account creation and cannot be changed later

// Connect to serverless account
CosmosClient cosmosClient = new CosmosClient(
    accountEndpoint: "https://mycosmosaccount.documents.azure.com:443/",
    authKeyOrResourceToken: "<your-key>"
);

// Create database (no throughput parameter needed)
Database database = await cosmosClient.CreateDatabaseIfNotExistsAsync(
    id: "ServerlessDatabase"
    // No throughput parameter - it's serverless!
);

// Create container (no throughput parameter needed)
Container container = await database.CreateContainerIfNotExistsAsync(
    id: "ServerlessContainer",
    partitionKeyPath: "/customerId"
    // No throughput parameter - automatically scales
);

// Use the container normally
ItemResponse<Product> response = await container.CreateItemAsync(
    item: new Product { Id = "1", CustomerId = "customer1", Name = "Widget" },
    partitionKey: new PartitionKey("customer1")
);

// You're only charged for the RUs consumed by this operation
Console.WriteLine($"Request charge: {response.RequestCharge} RU");
```

**Creating Serverless Account (Azure CLI):**
```bash
# Create Cosmos DB account with serverless capacity mode
az cosmosdb create \
  --name myserverlessaccount \
  --resource-group myresourcegroup \
  --locations regionName=eastus \
  --capabilities EnableServerless
```

**ARM Template:**
```json
{
  "type": "Microsoft.DocumentDB/databaseAccounts",
  "apiVersion": "2023-04-15",
  "name": "myserverlessaccount",
  "location": "East US",
  "properties": {
    "databaseAccountOfferType": "Standard",
    "capabilities": [
      {
        "name": "EnableServerless"
      }
    ]
  }
}
```

## Detailed Comparison

### Performance Characteristics

| Aspect | Provisioned (Manual) | Provisioned (Autoscale) | Serverless |
|--------|---------------------|------------------------|------------|
| Throughput Guarantee | Fixed RU/s | Up to max RU/s | Best effort (max 5,000) |
| Scaling Speed | Manual (minutes) | Instant | Instant |
| Minimum RU/s | 400 | Tmax/10 | 0 (when idle) |
| Maximum RU/s | Unlimited | Unlimited | 5,000 |
| Throttling Risk | If usage > provisioned | Rare (auto-scales) | If usage > 5,000 RU/s |

### Feature Support

| Feature | Provisioned | Serverless |
|---------|------------|------------|
| Point-in-time restore | ✅ | ❌ |
| Multi-region writes | ✅ | ❌ |
| Analytical store | ✅ | ❌ |
| Shared database throughput | ✅ | N/A |
| Free tier eligibility | ✅ (400 RU/s + 5 GB free) | ✅ (limited) |
| Change feed | ✅ | ✅ |
| Triggers and stored procedures | ✅ | ✅ |
| Partition key changes | ✅ | ✅ |

## Choosing the Right Capacity Mode

### Decision Tree

```
Start
│
├─ Do you need multi-region writes?
│  └─ YES → Provisioned Throughput
│  └─ NO → Continue
│
├─ Is your storage > 50 GB per container?
│  └─ YES → Provisioned Throughput
│  └─ NO → Continue
│
├─ Do you need > 5,000 RU/s sustained?
│  └─ YES → Provisioned Throughput
│  └─ NO → Continue
│
├─ Do you need analytical store?
│  └─ YES → Provisioned Throughput
│  └─ NO → Continue
│
├─ Is traffic intermittent or unpredictable?
│  └─ YES → Serverless
│  └─ NO → Continue
│
├─ Is this dev/test environment?
│  └─ YES → Serverless
│  └─ NO → Continue
│
├─ Is traffic predictable and sustained?
│  └─ YES → Provisioned (Manual)
│  └─ NO → Continue
│
└─ Traffic is variable but sustained?
   └─ YES → Provisioned (Autoscale)
```

### Use Case Examples

**E-commerce Website (High Traffic)**
- **Choice**: Provisioned Throughput with Autoscale
- **Reason**: Sustained high traffic with predictable spikes during sales
- **Configuration**: Max 50,000 RU/s autoscale

**IoT Data Ingestion (Continuous)**
- **Choice**: Provisioned Throughput (Manual)
- **Reason**: Constant, predictable data ingestion rate
- **Configuration**: Fixed 10,000 RU/s

**Mobile App Backend (Variable)**
- **Choice**: Serverless
- **Reason**: Usage varies throughout day, many idle periods
- **Configuration**: No configuration needed, auto-scales to 5,000 RU/s

**Enterprise Analytics (Synapse Link)**
- **Choice**: Provisioned Throughput
- **Reason**: Requires analytical store for Azure Synapse Link
- **Configuration**: Fixed 5,000 RU/s with analytical store enabled

**Microservices (Multiple Services)**
- **Choice**: Mix of both
- **Reason**: High-traffic services use provisioned, low-traffic use serverless
- **Configuration**: Per-service basis

**Development Environment**
- **Choice**: Serverless
- **Reason**: Intermittent usage, cost optimization
- **Configuration**: Auto-scales when developers are active

## Cost Considerations

### Provisioned Throughput Pricing

**Manual Provisioned:**
- Charged per 100 RU/s per hour
- Example: 1,000 RU/s = $0.008 per hour = ~$5.76/month
- Storage: $0.25 per GB per month

**Autoscale:**
- Charged for maximum RU/s reached in each hour
- Approximately 1.5x the manual rate when at max
- Minimum charge: (Tmax/10) at manual rate
- Example: Max 10,000 RU/s
  - If scales to 10,000: Pay for 10,000 at autoscale rate
  - If scales to 1,000: Pay for 1,000 at autoscale rate

**Cost Formula (Manual):**
```
Monthly Cost = (RU/s ÷ 100) × $0.008 × 730 hours + (Storage GB × $0.25)

Example: 5,000 RU/s with 100 GB storage
= (5000 ÷ 100) × $0.008 × 730 + (100 × $0.25)
= $292 + $25
= $317/month
```

### Serverless Pricing

- **Request Units**: $0.25 per million RU consumed
- **Storage**: $0.25 per GB per month
- **No minimum charge**: Pay only for what you use

**Cost Formula (Serverless):**
```
Monthly Cost = (Total RU consumed ÷ 1,000,000) × $0.25 + (Storage GB × $0.25)

Example: 100 million RU consumed, 20 GB storage
= (100,000,000 ÷ 1,000,000) × $0.25 + (20 × $0.25)
= $25 + $5
= $30/month
```

### Cost Comparison Scenarios

**Scenario 1: Constant Load**
- Traffic: 5,000 RU/s, 24/7
- Storage: 50 GB
- Monthly RU consumption: 13.14 billion RU

| Mode | Monthly Cost |
|------|-------------|
| Manual Provisioned | $317 |
| Autoscale (max 10K) | ~$475 |
| Serverless | $3,285 ❌ |

**Winner**: Manual Provisioned

**Scenario 2: Intermittent Load**
- Traffic: 5,000 RU/s for 2 hours/day
- Storage: 20 GB
- Monthly RU consumption: 1.1 billion RU

| Mode | Monthly Cost |
|------|-------------|
| Manual Provisioned | $317 ❌ |
| Autoscale (max 10K) | ~$475 ❌ |
| Serverless | $280 ✅ |

**Winner**: Serverless

**Scenario 3: Variable Load**
- Traffic: 1,000-10,000 RU/s, varies throughout day
- Average: 5,000 RU/s
- Storage: 100 GB
- Monthly RU consumption: 13.14 billion RU

| Mode | Monthly Cost |
|------|-------------|
| Manual (10K RU/s) | $609 ❌ |
| Autoscale (max 10K) | ~$400-600 |
| Serverless | $3,285 ❌ |

**Winner**: Autoscale

## Migration Between Capacity Modes

**Important**: You **cannot** convert a Cosmos DB account from one capacity mode to another after creation.

### Migration Options

**Option 1: Create New Account + Migrate Data**
```bash
# 1. Create new account with desired capacity mode
az cosmosdb create \
  --name mynewaccount \
  --resource-group myresourcegroup \
  --capabilities EnableServerless

# 2. Use Azure Data Factory or custom code to migrate data
# 3. Update application connection strings
# 4. Delete old account
```

**Option 2: Use Azure Cosmos DB Migration Tool**
- Use `dt.exe` (Data Migration Tool)
- Use Azure Data Factory
- Use custom migration scripts

**Code Example: Data Migration**
```csharp
public async Task MigrateDataAsync(
    string sourceConnectionString,
    string targetConnectionString)
{
    // Source (Provisioned)
    var sourceClient = new CosmosClient(sourceConnectionString);
    var sourceContainer = sourceClient.GetContainer("MyDatabase", "MyContainer");
    
    // Target (Serverless)
    var targetClient = new CosmosClient(targetConnectionString);
    var targetDatabase = await targetClient.CreateDatabaseIfNotExistsAsync("MyDatabase");
    var targetContainer = await targetDatabase.Database.CreateContainerIfNotExistsAsync(
        "MyContainer",
        "/partitionKey"
    );
    
    // Migrate data
    var iterator = sourceContainer.GetItemQueryIterator<dynamic>(
        "SELECT * FROM c"
    );
    
    while (iterator.HasMoreResults)
    {
        var batch = await iterator.ReadNextAsync();
        
        foreach (var item in batch)
        {
            await targetContainer.Container.CreateItemAsync(item);
        }
    }
}
```

## Best Practices

### Provisioned Throughput Best Practices

1. **Start with Manual, Monitor, Then Optimize**
   - Begin with manual provisioned throughput
   - Monitor usage patterns for 1-2 weeks
   - Switch to autoscale if usage is variable

2. **Use Autoscale for Unpredictable Workloads**
   - Better than over-provisioning with manual
   - Prevents throttling during unexpected spikes
   - Cost-effective for variable traffic

3. **Set Appropriate Max RU/s for Autoscale**
   ```csharp
   // Don't over-provision max RU/s
   // Monitor actual usage first
   var maxRUs = actualPeakRUs * 1.2; // 20% buffer
   await container.ReplaceThroughputAsync(
       ThroughputProperties.CreateAutoscaleThroughput(maxRUs)
   );
   ```

4. **Use Shared Throughput Wisely**
   - Good for many small containers
   - Not suitable if one container dominates usage
   - Monitor per-container usage

5. **Monitor and Optimize Partition Keys**
   - Good partition key design reduces RU consumption
   - Avoid hot partitions
   - Monitor partition key distribution

### Serverless Best Practices

1. **Use for Development First**
   - Perfect for dev/test environments
   - Easy to experiment without cost commitments

2. **Monitor Storage Limits**
   ```csharp
   // Check container storage
   var properties = await container.ReadContainerAsync();
   // Plan migration before hitting 50 GB limit
   ```

3. **Be Aware of RU/s Limits**
   - 5,000 RU/s per container
   - If consistently hitting limits, consider provisioned

4. **Implement Retry Logic**
   ```csharp
   // Handle potential throttling
   var cosmosClient = new CosmosClient(
       accountEndpoint,
       authKey,
       new CosmosClientOptions
       {
           MaxRetryAttemptsOnRateLimitedRequests = 9,
           MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
       }
   );
   ```

5. **Plan for Growth**
   - Monitor usage trends
   - Plan migration to provisioned if approaching limits

## Exam Questions and Scenarios

### Question 1: Choosing Capacity Mode

**Scenario**: You're developing a mobile application that will have unpredictable usage patterns. The app is in early stages with less than 100 active users. You expect data storage to remain under 20 GB for the foreseeable future.

**Question**: Which capacity mode should you choose?

**Answer**: **Serverless**

**Reasoning**:
- ✅ Unpredictable usage → Serverless perfect for this
- ✅ Low storage (< 50 GB limit) → Within serverless limits
- ✅ Early stage app → Serverless reduces initial costs
- ✅ Pay only when used → No waste during idle periods

### Question 2: Multi-Region Requirement

**Scenario**: You need to deploy a globally distributed application with multi-region writes for low-latency access worldwide.

**Question**: Which capacity mode can support this requirement?

**Answer**: **Provisioned Throughput**

**Reasoning**:
- ❌ Serverless does NOT support multi-region writes
- ✅ Provisioned supports multi-region writes
- Must use provisioned (manual or autoscale)

### Question 3: Cost Optimization

**Scenario**: Your application runs batch jobs that process data for 2 hours every night. During the day, there's minimal activity. Storage requirements are 30 GB.

**Question**: Which capacity mode is most cost-effective?

**Answer**: **Serverless**

**Reasoning**:
- ✅ Intermittent usage (only 2 hours/day) → Serverless advantage
- ✅ No charge during idle periods → Significant savings
- ✅ Storage under 50 GB → Within limits
- Provisioned would charge for full 24 hours

### Question 4: High-Throughput Application

**Scenario**: Your IoT application needs to consistently process 10,000 RU/s throughout the day with occasional spikes to 15,000 RU/s.

**Question**: Which capacity mode and configuration should you use?

**Answer**: **Provisioned Throughput with Autoscale (max 15,000 RU/s)**

**Reasoning**:
- ❌ Serverless limited to 5,000 RU/s → Cannot meet requirements
- ✅ Provisioned can handle > 5,000 RU/s
- ✅ Autoscale handles spikes automatically → Prevents throttling
- ✅ Cost-effective for variable high-throughput scenarios

## References

- [Choose between provisioned throughput and serverless](https://learn.microsoft.com/en-us/azure/cosmos-db/throughput-serverless)
- [Provisioned throughput in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/set-throughput)
- [Autoscale provisioned throughput](https://learn.microsoft.com/en-us/azure/cosmos-db/provision-throughput-autoscale)
- [Serverless in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/serverless)
- [Request Units in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/request-units)
- [Azure Cosmos DB pricing](https://azure.microsoft.com/en-us/pricing/details/cosmos-db/)
