
# Azure Cosmos DB Multi-Region Configurations

## Table of Contents

- [Overview](#overview)
- [Multi-Region Configuration Options](#multi-region-configuration-options)
  - [Single-Region Account](#single-region-account)
  - [Multi-Region with Read Replicas](#multi-region-with-read-replicas)
  - [Multi-Region with Multi-Master (Multi-Region Writes)](#multi-region-with-multi-master-multi-region-writes)
- [Configuration Comparison Table](#configuration-comparison-table)
- [Choosing the Right Configuration](#choosing-the-right-configuration)
  - [Decision Matrix by Workload Type](#decision-matrix-by-workload-type)
  - [Decision Tree](#decision-tree)
- [Consistency Levels and Multi-Region](#consistency-levels-and-multi-region)
- [Cost Considerations](#cost-considerations)
- [Implementation Examples](#implementation-examples)
  - [Azure CLI Examples](#azure-cli-examples)
  - [ARM Template Examples](#arm-template-examples)
  - [SDK Configuration](#sdk-configuration)
- [Best Practices](#best-practices)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure Cosmos DB provides multiple configuration options for distributing data across regions to achieve high availability, low latency, and disaster recovery. Understanding these configurations is crucial for designing globally distributed applications.

### Key Concepts

| Term | Definition |
|------|------------|
| **Read Replica** | A copy of data in another region that can serve read requests but not write requests |
| **Write Region** | A region where write operations are accepted |
| **Multi-Master (Multi-Region Writes)** | Configuration allowing write operations in multiple regions |
| **Geo-Replication** | Automatic replication of data across Azure regions |
| **Failover** | Switching to a secondary region when primary becomes unavailable |

---

## Multi-Region Configuration Options

### Single-Region Account

A single-region account stores all data in one Azure region with no replication to other regions.

```
┌─────────────────────────────────────┐
│          Single Region              │
│         (e.g., East US)             │
│                                     │
│    ┌────────────────────────┐       │
│    │  Cosmos DB Account     │       │
│    │  • Reads ✅            │       │
│    │  • Writes ✅           │       │
│    │  • All data here       │       │
│    └────────────────────────┘       │
└─────────────────────────────────────┘
```

**Characteristics:**
- ✅ Simplest configuration
- ✅ Lowest cost
- ✅ Strong consistency available
- ❌ No high availability across regions
- ❌ Single point of failure
- ❌ Higher latency for remote users
- ❌ No disaster recovery to another region

**Use Cases:**
- Development and testing
- Applications serving a single geographic area
- Cost-sensitive applications with lower availability requirements
- Proof-of-concept applications

### Multi-Region with Read Replicas

A multi-region account with read replicas has one primary write region and multiple read-only replica regions.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Multi-Region with Read Replicas                     │
│                                                                         │
│  ┌──────────────────────┐                                               │
│  │   Primary Region     │        Automatic Replication                  │
│  │    (East US)         │─────────────────────────────────────┐         │
│  │                      │                                     │         │
│  │  ┌───────────────┐   │                                     ▼         │
│  │  │ Write Region  │   │           ┌──────────────────────────────┐   │
│  │  │ • Writes ✅   │   │           │      Read Replicas           │   │
│  │  │ • Reads ✅    │   │           │                              │   │
│  │  └───────────────┘   │           │  ┌────────────┐ ┌────────────┐│   │
│  └──────────────────────┘           │  │  West US   │ │  Europe    ││   │
│                                     │  │ • Reads ✅ │ │ • Reads ✅ ││   │
│                                     │  │ • Writes ❌│ │ • Writes ❌││   │
│                                     │  └────────────┘ └────────────┘│   │
│                                     └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ High availability for reads across regions
- ✅ Low latency reads from local replicas
- ✅ Automatic data replication
- ✅ Automatic failover capability
- ✅ Cost-effective for read-heavy workloads
- ❌ All writes must go to primary region
- ❌ Write latency for remote users
- ❌ Single write region (potential bottleneck)

**Use Cases:**
- **Read-heavy web applications** (80%+ reads)
- Content delivery applications
- Reporting and analytics applications
- Applications with globally distributed read users
- E-commerce product catalogs (frequent reads, infrequent updates)

**How It Works:**
1. All write operations are sent to the primary (write) region
2. Data is automatically replicated to all read replica regions
3. Read operations can be served from any replica region
4. If primary fails, automatic failover promotes a replica to primary

### Multi-Region with Multi-Master (Multi-Region Writes)

Multi-master configuration allows write operations in all replicated regions.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                Multi-Region with Multi-Master Writes                    │
│                                                                         │
│   ┌──────────────────┐    ◄──── Bidirectional ────►  ┌──────────────────┐│
│   │   East US        │          Replication          │   West Europe    ││
│   │                  │                               │                  ││
│   │ ┌─────────────┐  │                               │ ┌─────────────┐  ││
│   │ │Write Region │  │                               │ │Write Region │  ││
│   │ │ • Writes ✅ │  │                               │ │ • Writes ✅ │  ││
│   │ │ • Reads ✅  │  │                               │ │ • Reads ✅  │  ││
│   │ └─────────────┘  │                               │ └─────────────┘  ││
│   └──────────────────┘                               └──────────────────┘│
│           ▲                                                   ▲          │
│           │                                                   │          │
│           │        ┌──────────────────┐                       │          │
│           │        │   Southeast Asia │                       │          │
│           │        │                  │                       │          │
│           │        │ ┌─────────────┐  │                       │          │
│           └────────│ │Write Region │  │───────────────────────┘          │
│                    │ │ • Writes ✅ │  │                                   │
│                    │ │ • Reads ✅  │  │                                   │
│                    │ └─────────────┘  │                                   │
│                    └──────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Low latency writes from any region
- ✅ High availability for both reads and writes
- ✅ No single point of failure
- ✅ Best for write-heavy global applications
- ⚠️ Requires conflict resolution policy
- ⚠️ Higher cost (multi-region write pricing)
- ⚠️ Eventual consistency patterns may be needed
- ❌ Strong consistency NOT available with multi-master

**Use Cases:**
- **Write-heavy global applications**
- Real-time gaming applications
- IoT data ingestion from global devices
- Social media applications
- Collaborative editing applications
- Applications requiring low write latency globally

**Conflict Resolution:**
When writes occur in multiple regions simultaneously, conflicts can occur. Cosmos DB offers:
1. **Last Write Wins (LWW)** - Default, based on `_ts` timestamp
2. **Custom** - User-defined stored procedure for resolution

---

## Configuration Comparison Table

| Feature | Single Region | Multi-Region Read Replicas | Multi-Region Writes |
|---------|---------------|---------------------------|---------------------|
| **Read Latency** | Low (local only) | Low (from local replica) | Low (from local) |
| **Write Latency** | Low (local only) | High for remote users | Low (from local) |
| **Read Availability** | 99.99% | 99.999% | 99.999% |
| **Write Availability** | 99.99% | 99.99% | 99.999% |
| **Disaster Recovery** | ❌ Manual only | ✅ Automatic failover | ✅ Automatic |
| **Strong Consistency** | ✅ Available | ✅ Available | ❌ Not available |
| **Bounded Staleness** | ✅ Available | ✅ Available | ❌ Not available |
| **Conflict Resolution** | Not needed | Not needed | Required |
| **Cost** | Lowest | Medium | Highest |
| **Best For** | Dev/Test, Single region users | Read-heavy global apps | Write-heavy global apps |

### Availability SLAs

| Configuration | Read SLA | Write SLA |
|---------------|----------|-----------|
| Single Region | 99.99% | 99.99% |
| Multi-Region (single write) | 99.999% | 99.99% |
| Multi-Region (multi-write) | 99.999% | 99.999% |

---

## Choosing the Right Configuration

### Decision Matrix by Workload Type

| Workload Type | Read:Write Ratio | Recommended Configuration |
|---------------|------------------|---------------------------|
| **Read-Heavy** | 80%+ reads | Multi-Region with Read Replicas |
| **Write-Heavy** | 50%+ writes | Multi-Region with Multi-Master |
| **Balanced** | 50:50 | Depends on latency requirements |
| **Unknown/Not Specified** | N/A | Consider both; lean toward read replicas for typical web apps |

### Important Note: Workload Pattern Matters!

**⚠️ When exam questions don't specify read vs write patterns:**

Many exam questions about multi-region Cosmos DB configurations don't explicitly state whether the application is read-heavy or write-heavy. In such cases:

1. **Most web applications are read-heavy** (typical 80-90% reads)
2. **"User data access"** usually implies reads
3. **"High availability and low latency access"** without specifying writes typically means read access
4. **Default assumption**: If not specified, assume read-heavy for typical web applications

However, this is an important consideration:
- If the app is **read-heavy** → Read replicas provide low latency reads
- If the app is **write-heavy** → Multi-master provides low latency writes
- **Both configurations** can provide high availability

### Decision Tree

```
Start: Multi-Region Cosmos DB Configuration
│
├─ Is the application read-heavy (>70% reads)?
│  ├─ YES → Multi-Region with Read Replicas ✅
│  │        (Low latency reads from local replicas)
│  │
│  └─ NO → Continue
│
├─ Is the application write-heavy (>50% writes)?
│  ├─ YES → Multi-Region with Multi-Master ✅
│  │        (Low latency writes from any region)
│  │
│  └─ NO → Continue
│
├─ Do you need strong consistency across regions?
│  ├─ YES → Multi-Region with Read Replicas ✅
│  │        (Multi-master doesn't support strong consistency)
│  │
│  └─ NO → Continue
│
├─ Is write latency critical for global users?
│  ├─ YES → Multi-Region with Multi-Master ✅
│  │
│  └─ NO → Multi-Region with Read Replicas ✅
│          (More cost-effective, simpler conflict management)
│
└─ Is this dev/test with budget constraints?
   └─ YES → Single Region ✅
```

---

## Consistency Levels and Multi-Region

### Consistency Availability by Configuration

| Consistency Level | Single Region | Multi-Region (Single Write) | Multi-Region (Multi-Write) |
|-------------------|---------------|----------------------------|---------------------------|
| **Strong** | ✅ | ✅ | ❌ |
| **Bounded Staleness** | ✅ | ✅ | ❌ |
| **Session** | ✅ | ✅ | ✅ |
| **Consistent Prefix** | ✅ | ✅ | ✅ |
| **Eventual** | ✅ | ✅ | ✅ |

**Key Point:** Strong and Bounded Staleness consistency are NOT available with multi-region writes because they require linearizability which cannot be guaranteed across distributed write regions.

---

## Cost Considerations

### Pricing Components

| Component | Single Region | Multi-Region Reads | Multi-Region Writes |
|-----------|---------------|-------------------|---------------------|
| **Provisioned Throughput** | Base rate | Base + replica cost | Base + 2x replica cost |
| **Storage** | Per GB | Per GB × regions | Per GB × regions |
| **Data Transfer** | Minimal | Replication costs | Higher replication costs |

### Cost Multipliers

```
Single Region Cost = Base Cost

Multi-Region Read Replicas Cost = 
  Base Cost + (Replica Regions × Storage Cost) + Replication Transfer

Multi-Region Writes Cost = 
  Base Cost × Number of Write Regions + Storage × Regions + Higher Transfer
```

**Example Cost Comparison (approximate):**

| Configuration | 10,000 RU/s + 100 GB | Relative Cost |
|---------------|----------------------|---------------|
| Single Region (East US) | $584/month | 1x |
| 2 Regions (1 write, 1 read) | $876/month | 1.5x |
| 2 Regions (both write) | $1,168/month | 2x |
| 3 Regions (1 write, 2 read) | $1,168/month | 2x |
| 3 Regions (all write) | $1,752/month | 3x |

---

## Implementation Examples

### Azure CLI Examples

**Create Multi-Region Account with Read Replicas:**
```bash
# Create account with multiple regions (East US primary, West US and Europe as read replicas)
az cosmosdb create \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
  --locations regionName=westus failoverPriority=1 isZoneRedundant=false \
  --locations regionName=westeurope failoverPriority=2 isZoneRedundant=false \
  --default-consistency-level Session \
  --enable-automatic-failover true

# Note: failoverPriority=0 is the primary (write) region
# Other regions are read replicas
```

**Create Multi-Region Account with Multi-Master (Multi-Region Writes):**
```bash
# Create account with multi-region writes enabled
az cosmosdb create \
  --name mymultimasteraccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
  --locations regionName=westeurope failoverPriority=1 isZoneRedundant=true \
  --locations regionName=southeastasia failoverPriority=2 isZoneRedundant=true \
  --default-consistency-level Session \
  --enable-multiple-write-locations true  # This enables multi-master!

# All regions can now accept writes
```

**Add Region to Existing Account:**
```bash
# Add a new read replica region
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 \
  --locations regionName=westus failoverPriority=1 \
  --locations regionName=westeurope failoverPriority=2 \
  --locations regionName=japaneast failoverPriority=3  # New region added
```

### ARM Template Examples

**Multi-Region with Read Replicas:**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.DocumentDB/databaseAccounts",
      "apiVersion": "2023-04-15",
      "name": "mycosmosaccount",
      "location": "East US",
      "properties": {
        "databaseAccountOfferType": "Standard",
        "consistencyPolicy": {
          "defaultConsistencyLevel": "Session"
        },
        "enableAutomaticFailover": true,
        "enableMultipleWriteLocations": false,
        "locations": [
          {
            "locationName": "East US",
            "failoverPriority": 0,
            "isZoneRedundant": true
          },
          {
            "locationName": "West US",
            "failoverPriority": 1,
            "isZoneRedundant": false
          },
          {
            "locationName": "West Europe",
            "failoverPriority": 2,
            "isZoneRedundant": false
          }
        ]
      }
    }
  ]
}
```

**Multi-Region with Multi-Master:**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.DocumentDB/databaseAccounts",
      "apiVersion": "2023-04-15",
      "name": "mymultimasteraccount",
      "location": "East US",
      "properties": {
        "databaseAccountOfferType": "Standard",
        "consistencyPolicy": {
          "defaultConsistencyLevel": "Session"
        },
        "enableAutomaticFailover": true,
        "enableMultipleWriteLocations": true,
        "locations": [
          {
            "locationName": "East US",
            "failoverPriority": 0,
            "isZoneRedundant": true
          },
          {
            "locationName": "West Europe",
            "failoverPriority": 1,
            "isZoneRedundant": true
          },
          {
            "locationName": "Southeast Asia",
            "failoverPriority": 2,
            "isZoneRedundant": true
          }
        ]
      }
    }
  ]
}
```

### SDK Configuration

**Configure Preferred Regions for Read Operations (.NET):**
```csharp
using Microsoft.Azure.Cosmos;

// Configure client to prefer reading from specific regions
CosmosClientOptions options = new CosmosClientOptions
{
    // For read operations, prefer these regions in order
    ApplicationPreferredRegions = new List<string>
    {
        Regions.WestUS,        // First preference
        Regions.EastUS,        // Second preference
        Regions.WestEurope     // Third preference
    },
    
    // Connection settings for better performance
    ConnectionMode = ConnectionMode.Direct,
    
    // Enable multi-master writes (if account supports it)
    ApplicationRegion = null  // Don't set this when using multi-master
};

CosmosClient client = new CosmosClient(
    connectionString: "<connection-string>",
    clientOptions: options
);

// Reads will automatically go to nearest preferred region
// Writes will go to write region (or nearest if multi-master)
```

**Configure for Multi-Master Writes:**
```csharp
using Microsoft.Azure.Cosmos;

// For multi-master, set the local region for writes
CosmosClientOptions options = new CosmosClientOptions
{
    // Set the region where THIS instance is running
    // Writes will go to this region
    ApplicationRegion = Regions.WestEurope,
    
    // For reads, can still specify preferences
    ApplicationPreferredRegions = new List<string>
    {
        Regions.WestEurope,
        Regions.EastUS
    }
};

CosmosClient client = new CosmosClient(
    connectionString: "<connection-string>",
    clientOptions: options
);
```

**Handle Conflict Resolution in Multi-Master:**
```csharp
// When creating container in multi-master account
ContainerProperties containerProperties = new ContainerProperties
{
    Id = "myContainer",
    PartitionKeyPath = "/customerId",
    
    // Configure conflict resolution policy
    ConflictResolutionPolicy = new ConflictResolutionPolicy
    {
        // Option 1: Last Write Wins (default)
        Mode = ConflictResolutionMode.LastWriterWins,
        ResolutionPath = "/_ts"  // Use timestamp for resolution
        
        // Option 2: Custom stored procedure
        // Mode = ConflictResolutionMode.Custom,
        // ResolutionProcedure = "dbs/myDatabase/colls/myContainer/sprocs/resolveConflict"
    }
};

Container container = await database.CreateContainerIfNotExistsAsync(containerProperties);
```

---

## Best Practices

### General Best Practices

1. **Start with Read Replicas for Most Applications**
   - Most web applications are read-heavy
   - Simpler to manage (no conflict resolution)
   - Lower cost
   - Upgrade to multi-master if write latency becomes an issue

2. **Enable Automatic Failover**
   - Always enable for production workloads
   - Ensures high availability without manual intervention
   - Works with both read replicas and multi-master

3. **Use Zone Redundancy for Critical Regions**
   - Provides 99.999% availability within a region
   - Replicates across availability zones
   - Recommended for primary regions

4. **Configure SDK with Preferred Regions**
   - Always set `ApplicationPreferredRegions` or `ApplicationRegion`
   - Ensures reads go to nearest replica
   - Reduces latency for global users

### Multi-Master Best Practices

1. **Choose Appropriate Conflict Resolution**
   - Last Write Wins (LWW) for most scenarios
   - Custom resolution for complex merge logic
   - Test conflict scenarios thoroughly

2. **Design for Eventual Consistency Patterns**
   - Strong consistency not available
   - Design application to handle temporary inconsistencies
   - Use Session consistency for user-specific operations

3. **Monitor Regional Latencies**
   - Track write latencies per region
   - Identify any replication lag issues
   - Set up alerts for anomalies

### Read Replica Best Practices

1. **Plan Failover Priorities Carefully**
   - Set priorities based on capacity and proximity
   - Test failover scenarios regularly
   - Document failover procedures

2. **Consider Strong Consistency Trade-offs**
   - Available with read replicas
   - Increases latency (must wait for quorum)
   - Use only when necessary

---

## Practice Questions

### Question 1: High Availability and Low Latency Access

**Scenario:** You are developing a web application that uses Azure Cosmos DB to store user data. You need to ensure that the application can handle high availability and low latency access to the data across multiple regions.

**Question:** Which of the following configurations should you choose when creating your Azure Cosmos DB account?

**Options:**
- A. Create a multi-region account with write regions in multiple locations.
- B. Create a single-region account and enable multi-master replication.
- C. Create a multi-region account with read replicas in different regions.
- D. Create a single-region account and configure it to use strong consistency.

**Answer:** C ✅

**Explanation:**

**Why C is Correct:**
- **Multi-region with read replicas** provides both high availability and low latency access
- Read operations (most common for web apps) served from local replicas = low latency
- Automatic failover capability = high availability
- Most web applications are read-heavy (80%+ reads), making this configuration optimal

**Why A is Incorrect:**
- Multi-region writes is for **write-heavy** workloads
- The question emphasizes "access to data" suggesting reads
- Does not inherently provide better read performance than read replicas
- Higher cost without clear benefit for typical web apps

**Why B is Incorrect:**
- "Single-region account" contradicts the multi-region requirement
- Cannot enable multi-master on single-region (conceptually invalid)
- Does not provide high availability across regions

**Why D is Incorrect:**
- Single-region = no high availability across regions
- Strong consistency within one region doesn't help global access
- Single point of failure
- No low latency for remote users

---

### Question 2: Write-Heavy Application

**Scenario:** You are building a real-time gaming platform with users worldwide. The application performs frequent write operations as players update their game state. You need minimal latency for both reads and writes globally.

**Question:** Which configuration should you choose?

**Options:**
- A. Single-region with autoscale throughput
- B. Multi-region with read replicas and strong consistency
- C. Multi-region with multi-master writes enabled
- D. Serverless with single region

**Answer:** C ✅

**Explanation:**
- Gaming platforms are typically **write-heavy** (game state updates)
- **Multi-master** allows writes in any region = low write latency globally
- All regions can accept writes = no single point of failure for writes
- Reads also served locally = low read latency

---

### Question 3: Consistency Requirements

**Scenario:** Your financial application requires strong consistency for all read and write operations. The application serves users in multiple continents and needs high availability.

**Question:** Which configuration should you choose?

**Options:**
- A. Multi-region with multi-master writes and strong consistency
- B. Multi-region with read replicas and strong consistency
- C. Single-region with strong consistency
- D. Multi-region with multi-master writes and session consistency

**Answer:** B ✅

**Explanation:**
- **Strong consistency requires single write region** - not available with multi-master
- Multi-region with read replicas supports strong consistency
- Provides high availability (99.999% for reads)
- Trade-off: write latency for remote users (must go to primary region)

**Why A is Incorrect:**
- Multi-master does NOT support strong consistency
- These two options are mutually exclusive

---

### Question 4: Cost-Effective Development Environment

**Scenario:** You need to set up a development environment for testing a globally distributed application. Budget is limited, and you want to simulate multi-region behavior.

**Question:** Which configuration is most cost-effective?

**Options:**
- A. Multi-region with 5 read replicas
- B. Multi-region with multi-master writes in 3 regions
- C. Single-region with serverless capacity mode
- D. Multi-region with 2 regions (1 write, 1 read) with lowest tier

**Answer:** C ✅ (for pure cost savings) or D (for testing multi-region)

**Explanation:**
- **Serverless single-region** is cheapest for dev/test (pay only when used)
- If testing multi-region behavior, **2 regions minimum** needed
- Avoid multi-master and many replicas for dev environments
- Use manual provisioned with minimum RU/s if constant testing needed

---

### Question 5: Workload Pattern Not Specified

**Scenario:** A company is building a global e-commerce platform using Cosmos DB. They need the application to provide fast access for users worldwide. The workload pattern is not specified.

**Question:** Which configuration would you initially recommend?

**Answer:** Multi-region with read replicas ✅

**Reasoning:**
- E-commerce platforms are typically **80-90% reads** (browsing products, viewing orders)
- Read replicas provide fast local reads for global users
- Lower cost than multi-master
- Can upgrade to multi-master later if write patterns indicate need
- Strong consistency available if needed for orders

---

### Question 6: Strong Consistency with Multi-Region Writes

**Scenario:** You have an Azure Cosmos DB account configured with strong consistency and multi-region writes. When you try to enable multi-region writes, the operation fails.

**Question:** What is the cause of this failure?

**Options:**
- A. Strong consistency is not supported with multi-region writes
- B. Missing required Azure permissions for the account
- C. Account tier doesn't support multi-region writes
- D. Insufficient throughput provisioned for multi-region configuration

**Answer:** A ✅

**Explanation:**

**Why A is Correct:**
- Azure Cosmos DB **doesn't support strong consistency with multi-region writes**
- This is because it's impossible to maintain linearizability guarantees across multiple write regions
- Strong consistency requires that reads always return the most recent committed version, which cannot be guaranteed when writes occur in multiple distributed regions simultaneously

**Why B is Incorrect:**
- If permissions were the issue, you wouldn't be able to access the account settings at all, not just multi-region configuration
- Permission issues manifest as access denied errors, not configuration failures

**Why C is Incorrect:**
- Multi-region writes are supported across **all Azure Cosmos DB account tiers**
- The limitation is with the consistency level, not the account tier

**Why D is Incorrect:**
- Throughput requirements don't prevent enabling multi-region writes
- The issue is the incompatible consistency level, not provisioned capacity

**Key Takeaway:** When designing multi-region write configurations, you must use Session, Consistent Prefix, or Eventual consistency levels. If strong consistency is required, use a single write region with read replicas instead.

---

## Summary

| Scenario | Recommended Configuration |
|----------|--------------------------|
| Read-heavy web application | Multi-region with read replicas |
| Write-heavy global application | Multi-region with multi-master |
| Strong consistency required | Multi-region with read replicas (NOT multi-master) |
| Development/Testing | Single-region or serverless |
| Cost-sensitive global app | Multi-region with minimal read replicas |
| Gaming/Real-time collaboration | Multi-region with multi-master |
| Content delivery/CDN | Multi-region with read replicas |
| Financial transactions (ACID) | Multi-region read replicas + strong consistency |

---

## References

- [Distribute data globally with Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/distribute-data-globally)
- [Configure multi-region writes](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-multi-master)
- [High availability with Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/high-availability)
- [Manage consistency levels](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
- [Conflict resolution types and resolution policies](https://learn.microsoft.com/en-us/azure/cosmos-db/conflict-resolution-policies)
- [Automatic and manual failover](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-manage-database-account#automatic-failover)
