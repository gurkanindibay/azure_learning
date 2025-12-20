# Azure Cosmos DB High Availability Options

## Table of Contents

- [Overview](#overview)
- [High Availability Architecture](#high-availability-architecture)
- [Availability Configurations](#availability-configurations)
  - [Single-Region Configuration](#single-region-configuration)
  - [Multi-Region with Single Write Region](#multi-region-with-single-write-region)
  - [Multi-Region with Multi-Write (Multi-Master)](#multi-region-with-multi-write-multi-master)
- [Availability Zones Support](#availability-zones-support)
- [Automatic Failover](#automatic-failover)
- [SLA Comparison](#sla-comparison)
- [RPO and RTO](#rpo-and-rto)
- [High Availability Best Practices](#high-availability-best-practices)
- [Configuration Examples](#configuration-examples)
- [Cost Considerations](#cost-considerations)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure Cosmos DB is designed from the ground up for **global distribution** and **high availability**. It provides multiple configuration options to achieve different levels of availability, from 99.99% to 99.999% SLA, depending on the deployment configuration.

### Key High Availability Features

| Feature | Description |
|---------|-------------|
| **Automatic Replication** | Data is automatically replicated within and across regions |
| **Availability Zones** | Support for zone-redundant deployments within a region |
| **Multi-Region Writes** | Write to multiple regions simultaneously for highest availability |
| **Automatic Failover** | Automatic failover to secondary regions during outages |
| **No Single Point of Failure** | Distributed architecture eliminates single points of failure |

---

## High Availability Architecture

### Within a Region

Azure Cosmos DB maintains **4 replicas** of your data within each region:

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Azure Region                       │
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│   │  Replica 1  │  │  Replica 2  │  │  Replica 3  │         │
│   │  (Primary)  │  │ (Secondary) │  │ (Secondary) │         │
│   └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│                    ┌─────────────┐                          │
│                    │  Replica 4  │                          │
│                    │ (Secondary) │                          │
│                    └─────────────┘                          │
│                                                              │
│   Quorum-based writes: 3 out of 4 replicas must acknowledge │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- All writes require acknowledgment from a quorum (3 out of 4 replicas)
- Reads can be served from any replica
- Automatic replica recovery if one fails
- Hardware failures are handled transparently

### Across Regions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Multi-Region Architecture                             │
│                                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  │   Primary Region │         │  Secondary Region │         │  Secondary Region │
│  │    (East US)     │◄───────►│    (West US)      │◄───────►│    (Europe)       │
│  │                  │         │                   │         │                   │
│  │  ┌────┐ ┌────┐   │         │  ┌────┐ ┌────┐    │         │  ┌────┐ ┌────┐    │
│  │  │ R1 │ │ R2 │   │ Async   │  │ R1 │ │ R2 │    │ Async   │  │ R1 │ │ R2 │    │
│  │  └────┘ └────┘   │ Replic. │  └────┘ └────┘    │ Replic. │  └────┘ └────┘    │
│  │  ┌────┐ ┌────┐   │         │  ┌────┐ ┌────┐    │         │  ┌────┐ ┌────┐    │
│  │  │ R3 │ │ R4 │   │         │  │ R3 │ │ R4 │    │         │  │ R3 │ │ R4 │    │
│  │  └────┘ └────┘   │         │  └────┘ └────┘    │         │  └────┘ └────┘    │
│  └──────────────────┘         └──────────────────┘         └──────────────────┘
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Availability Configurations

### Single-Region Configuration

**Description:** All data resides in a single Azure region with 4 replicas.

| Aspect | Value |
|--------|-------|
| **SLA** | 99.99% |
| **Replicas** | 4 within region |
| **Failover** | Within region only |
| **Use Case** | Development, single-region apps |

**Limitations:**
- ❌ No protection against regional outages
- ❌ No disaster recovery to another region
- ❌ Higher latency for geographically distributed users

### Multi-Region with Single Write Region

**Description:** One primary write region with multiple read replica regions.

| Aspect | Value |
|--------|-------|
| **SLA (Reads)** | 99.999% |
| **SLA (Writes)** | 99.99% |
| **Write Region** | Single |
| **Read Regions** | Multiple (up to 30+) |
| **Failover** | Automatic or manual to read region |

```
┌─────────────────────────────────────────────────────────────────┐
│              Multi-Region with Single Write                      │
│                                                                  │
│   Write Region                    Read Regions                   │
│   ┌─────────────┐                ┌─────────────┐                │
│   │  East US    │───Replicate───►│  West US    │                │
│   │  Writes ✅  │                │  Reads ✅   │                │
│   │  Reads ✅   │                │  Writes ❌  │                │
│   └─────────────┘                └─────────────┘                │
│         │                        ┌─────────────┐                │
│         └────────Replicate──────►│  Europe     │                │
│                                  │  Reads ✅   │                │
│                                  │  Writes ❌  │                │
│                                  └─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Low-latency reads globally
- ✅ Automatic failover for writes
- ✅ 99.999% read availability
- ✅ Strong consistency available

**Limitations:**
- ⚠️ Writes always go to single region (higher write latency for distant users)
- ⚠️ Failover required if write region fails

### Multi-Region with Multi-Write (Multi-Master)

**Description:** Multiple regions can accept both reads and writes simultaneously.

| Aspect | Value |
|--------|-------|
| **SLA (Reads)** | 99.999% |
| **SLA (Writes)** | 99.999% |
| **Write Regions** | Multiple |
| **Read Regions** | All write regions |
| **Failover** | No failover needed |

```
┌─────────────────────────────────────────────────────────────────┐
│              Multi-Region with Multi-Write                       │
│                                                                  │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐     │
│   │  East US    │◄────►│  West US    │◄────►│  Europe     │     │
│   │  Writes ✅  │      │  Writes ✅  │      │  Writes ✅  │     │
│   │  Reads ✅   │      │  Reads ✅   │      │  Reads ✅   │     │
│   └─────────────┘      └─────────────┘      └─────────────┘     │
│                                                                  │
│   • All regions accept writes                                    │
│   • Automatic conflict resolution                                │
│   • No single point of failure for writes                        │
│   • 99.999% availability for both reads AND writes               │
└─────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Highest availability (99.999% for reads AND writes)
- ✅ Lowest write latency globally
- ✅ No failover needed - all regions active
- ✅ Automatic conflict resolution

**Considerations:**
- ⚠️ Strong consistency NOT available (Bounded Staleness is max)
- ⚠️ Higher cost (RU charges in each write region)
- ⚠️ Conflict resolution policy required

---

## Availability Zones Support

Azure Cosmos DB supports **Availability Zone (AZ)** redundancy within a region for enhanced fault tolerance.

### Without Availability Zones

```
┌─────────────────────────────────────────┐
│           Single Zone/Datacenter         │
│                                          │
│   ┌────┐  ┌────┐  ┌────┐  ┌────┐        │
│   │ R1 │  │ R2 │  │ R3 │  │ R4 │        │
│   └────┘  └────┘  └────┘  └────┘        │
│                                          │
│   Risk: Datacenter failure affects all   │
└─────────────────────────────────────────┘
```

### With Availability Zones

```
┌─────────────────────────────────────────────────────────────────┐
│                    Zone-Redundant Deployment                     │
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│   │    Zone 1   │   │    Zone 2   │   │    Zone 3   │           │
│   │  ┌────┐     │   │  ┌────┐     │   │  ┌────┐     │           │
│   │  │ R1 │     │   │  │ R2 │     │   │  │ R3 │     │           │
│   │  └────┘     │   │  └────┘     │   │  └────┘     │           │
│   │  ┌────┐     │   │             │   │  ┌────┐     │           │
│   │  │ R4 │     │   │             │   │  │    │     │           │
│   │  └────┘     │   │             │   │  └────┘     │           │
│   └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                  │
│   Benefit: Zone failure doesn't affect availability              │
└─────────────────────────────────────────────────────────────────┘
```

### Zone Redundancy Configuration

| Configuration | Availability | Use Case |
|---------------|-------------|----------|
| **No AZ** | Standard within-region HA | Cost-sensitive workloads |
| **With AZ** | Enhanced within-region HA | Production workloads |
| **AZ + Multi-Region** | Maximum availability | Mission-critical apps |

**Enabling Availability Zones:**
- Available in supported regions
- No additional cost for AZ redundancy
- Can be enabled during account creation or added later

---

## Automatic Failover

### Service-Managed Failover

When automatic failover is enabled, Cosmos DB automatically promotes a read region to write region if the current write region becomes unavailable.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Automatic Failover Process                    │
│                                                                  │
│   Normal Operation:                                              │
│   ┌─────────────┐         ┌─────────────┐                       │
│   │  East US    │────────►│  West US    │                       │
│   │  Primary    │         │  Secondary  │                       │
│   │  (Write)    │         │  (Read)     │                       │
│   └─────────────┘         └─────────────┘                       │
│                                                                  │
│   After Failover (East US fails):                               │
│   ┌─────────────┐         ┌─────────────┐                       │
│   │  East US    │         │  West US    │                       │
│   │  (Offline)  │    ──►  │  Primary    │                       │
│   │             │         │  (Write)    │                       │
│   └─────────────┘         └─────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Failover Configuration Options

| Option | Description |
|--------|-------------|
| **Automatic Failover** | Azure automatically fails over if write region unavailable |
| **Manual Failover** | User-initiated failover for planned maintenance |
| **Failover Priority** | Define order of regions for automatic failover |

### Failover Priority Example

```json
{
  "locations": [
    { "locationName": "East US", "failoverPriority": 0 },
    { "locationName": "West US", "failoverPriority": 1 },
    { "locationName": "North Europe", "failoverPriority": 2 }
  ]
}
```

---

## SLA Comparison

| Configuration | Read SLA | Write SLA | Notes |
|---------------|----------|-----------|-------|
| **Single Region** | 99.99% | 99.99% | No cross-region protection |
| **Multi-Region (Single Write)** | 99.999% | 99.99% | Automatic failover available |
| **Multi-Region (Multi-Write)** | 99.999% | 99.999% | Highest availability |
| **With Availability Zones** | +Enhanced | +Enhanced | Additional zone protection |

### SLA Downtime Comparison

| SLA | Max Downtime/Year | Max Downtime/Month |
|-----|-------------------|-------------------|
| **99.99%** | 52.56 minutes | 4.38 minutes |
| **99.999%** | 5.26 minutes | 26.3 seconds |

---

## RPO and RTO

### Recovery Point Objective (RPO)

| Configuration | RPO | Data Loss Risk |
|---------------|-----|----------------|
| **Single Region** | 0 (within region) | Regional failure = potential loss |
| **Multi-Region (Single Write)** | ~0 to seconds | Minimal with async replication |
| **Multi-Region (Multi-Write)** | 0 | No data loss (all regions active) |

### Recovery Time Objective (RTO)

| Configuration | RTO | Notes |
|---------------|-----|-------|
| **Single Region** | Minutes | Depends on failure type |
| **Multi-Region (Automatic Failover)** | < 1 minute | Automatic promotion |
| **Multi-Region (Multi-Write)** | 0 | No failover needed |

---

## High Availability Best Practices

### 1. Enable Multi-Region Replication

```
✅ DO: Deploy to at least 2 regions for production
✅ DO: Enable automatic failover
✅ DO: Set appropriate failover priorities
❌ DON'T: Use single region for production workloads
```

### 2. Enable Availability Zones

```
✅ DO: Enable AZ where available
✅ DO: Combine with multi-region for maximum HA
❌ DON'T: Assume single-zone is sufficient for mission-critical apps
```

### 3. Choose Appropriate Consistency Level

| For High Availability | Recommended Consistency |
|----------------------|------------------------|
| Multi-Region (Single Write) | Session, Consistent Prefix, or Eventual |
| Multi-Region (Multi-Write) | Session, Consistent Prefix, or Eventual |
| Maximum Data Durability | Strong (single write region only) |

### 4. Configure Preferred Regions in SDK

```csharp
// C# SDK Example
CosmosClientOptions options = new CosmosClientOptions()
{
    ApplicationPreferredRegions = new List<string>
    {
        Regions.WestUS,      // Closest region first
        Regions.EastUS,      // Fallback region
        Regions.NorthEurope  // Additional fallback
    }
};
```

### 5. Implement Connection Retry Logic

```csharp
// Retry policy for transient failures
CosmosClientOptions options = new CosmosClientOptions()
{
    MaxRetryAttemptsOnRateLimitedRequests = 9,
    MaxRetryWaitTimeOnRateLimitedRequests = TimeSpan.FromSeconds(30)
};
```

---

## Configuration Examples

### Azure CLI - Enable Multi-Region

```bash
# Add a read region
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --locations regionName=eastus failoverPriority=0 isZoneRedundant=true \
  --locations regionName=westus failoverPriority=1 isZoneRedundant=true
```

### Azure CLI - Enable Multi-Write

```bash
# Enable multi-region writes
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --enable-multiple-write-locations true
```

### Azure CLI - Enable Automatic Failover

```bash
# Enable automatic failover
az cosmosdb update \
  --name mycosmosaccount \
  --resource-group myResourceGroup \
  --enable-automatic-failover true
```

### ARM Template - High Availability Configuration

```json
{
  "type": "Microsoft.DocumentDB/databaseAccounts",
  "apiVersion": "2023-04-15",
  "name": "[parameters('accountName')]",
  "location": "[parameters('location')]",
  "properties": {
    "enableAutomaticFailover": true,
    "enableMultipleWriteLocations": true,
    "locations": [
      {
        "locationName": "East US",
        "failoverPriority": 0,
        "isZoneRedundant": true
      },
      {
        "locationName": "West US",
        "failoverPriority": 1,
        "isZoneRedundant": true
      }
    ]
  }
}
```

---

## Cost Considerations

### Multi-Region Cost Impact

| Cost Factor | Single Region | Multi-Region (Single Write) | Multi-Region (Multi-Write) |
|-------------|---------------|-----------------------------|-----------------------------|
| **RU Cost** | 1x | 1x + read replicas | Nx (N = write regions) |
| **Storage** | 1x | Nx (replicated) | Nx (replicated) |
| **Network Egress** | Minimal | Cross-region transfer | Cross-region transfer |

### Cost Optimization Tips

1. **Start with Single Write**: Most apps don't need multi-write
2. **Use Session Consistency**: Lower RU consumption than Strong
3. **Enable Availability Zones**: No additional cost, enhanced HA
4. **Monitor and Right-size**: Use metrics to optimize RU provisioning

---

## Practice Questions

### Question 1
**Your company requires a Cosmos DB deployment with 99.999% write availability. Which configuration should you use?**

A. Single-region with Availability Zones  
B. Multi-region with single write region  
C. Multi-region with multi-write (multi-master)  
D. Premium tier Cosmos DB

<details>
<summary>Answer</summary>

**C. Multi-region with multi-write (multi-master)**

Only multi-region with multi-write configuration provides 99.999% SLA for both reads AND writes. Single write region configurations only provide 99.99% write SLA.

</details>

### Question 2
**Which consistency levels are available when using multi-region writes in Cosmos DB?**

A. All five consistency levels  
B. Only Eventual consistency  
C. Session, Consistent Prefix, Eventual, and Bounded Staleness  
D. Only Strong and Bounded Staleness

<details>
<summary>Answer</summary>

**C. Session, Consistent Prefix, Eventual, and Bounded Staleness**

Strong consistency is NOT available with multi-region writes because it requires synchronous replication which would negate the benefits of multi-master architecture.

</details>

### Question 3
**What is the maximum number of read regions you can configure in Azure Cosmos DB?**

A. 4  
B. 10  
C. 30+  
D. Unlimited

<details>
<summary>Answer</summary>

**C. 30+**

Azure Cosmos DB supports adding unlimited read regions (practically 30+ Azure regions are available). Each region maintains 4 replicas of your data.

</details>

---

## References

- [High Availability in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/high-availability)
- [Achieve High Availability with Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-manage-database-account#addremove-regions-from-your-database-account)
- [Configure Multi-Region Writes](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-multi-master)
- [Cosmos DB SLA](https://azure.microsoft.com/en-us/support/legal/sla/cosmos-db/)
- [Automatic Failover Configuration](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-manage-database-account#automatic-failover)
- [Availability Zones in Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/high-availability#availability-zone-support)
