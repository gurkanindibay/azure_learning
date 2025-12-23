# Azure Synapse Link for Azure Cosmos DB

## Table of Contents

- [Overview](#overview)
- [What is Azure Synapse Link?](#what-is-azure-synapse-link)
- [Key Benefits](#key-benefits)
- [Architecture](#architecture)
- [When to Use Azure Synapse Link](#when-to-use-azure-synapse-link)
- [Comparison with Alternative Solutions](#comparison-with-alternative-solutions)
- [Exam Scenario: Analyzing Operational Data](#exam-scenario-analyzing-operational-data)
- [Secure Network Connectivity: Managed Private Endpoints](#secure-network-connectivity-managed-private-endpoints)
- [Configuration Steps](#configuration-steps)
- [Best Practices](#best-practices)
- [Limitations](#limitations)
- [Resources](#resources)

---

## Overview

Azure Synapse Link for Azure Cosmos DB is a cloud-native hybrid transactional and analytical processing (HTAP) capability that enables you to run **near real-time analytics** over operational data in Azure Cosmos DB. It creates a tight, seamless integration between Azure Cosmos DB and Azure Synapse Analytics **without any ETL (Extract, Transform, Load)** processes.

---

## What is Azure Synapse Link?

Azure Synapse Link creates a direct connection between Azure Cosmos DB's **operational store** and an **analytical store**:

- **Operational Store (Row Store)**: Your existing Cosmos DB container that handles transactional workloads (reads, writes, updates)
- **Analytical Store (Column Store)**: A fully isolated, column-oriented store automatically synchronized from the operational store

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Azure Cosmos DB Container                             │
│                                                                              │
│  ┌──────────────────────────┐      ┌──────────────────────────┐            │
│  │   Operational Store      │      │    Analytical Store       │            │
│  │   (Row-Oriented)         │─────▶│    (Column-Oriented)      │            │
│  │                          │ Auto │                           │            │
│  │  • OLTP Workloads        │ Sync │  • OLAP Workloads         │            │
│  │  • Transactional         │      │  • Analytics              │            │
│  │  • Low Latency           │      │  • Aggregations           │            │
│  │  • Point Reads/Writes    │      │  • Complex Queries        │            │
│  └──────────────────────────┘      └──────────────────────────┘            │
│                                              │                               │
│                                              │ No ETL                        │
│                                              ▼                               │
│                              ┌───────────────────────────────┐              │
│                              │   Azure Synapse Analytics     │              │
│                              │                               │              │
│                              │  • Synapse SQL Serverless    │              │
│                              │  • Synapse Spark             │              │
│                              │  • Power BI Integration      │              │
│                              └───────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Benefits

### 1. **No Impact on Transactional Performance**
- Analytical queries run against the analytical store, completely isolated from the operational store
- Your OLTP workloads remain unaffected regardless of analytical query load

### 2. **No ETL Required**
- Automatic synchronization between operational and analytical stores
- Near real-time data availability (typically within 2 minutes)
- No need to build and maintain complex data pipelines

### 3. **Reduced Cost**
- No separate compute or storage resources for ETL
- Column-oriented analytical store is cost-optimized for analytics
- Pay only for analytical storage and Synapse queries

### 4. **Near Real-Time Analytics**
- Data is automatically synchronized to analytical store
- Typical latency: less than 2 minutes
- Enables timely business insights on operational data

### 5. **Fully Managed**
- Microsoft handles all synchronization, indexing, and optimization
- No infrastructure to manage

---

## Architecture

### Hybrid Transactional/Analytical Processing (HTAP)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Application Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Web Apps   │  │  APIs       │  │  Mobile     │  │  IoT        │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│         └────────────────┼────────────────┼────────────────┘               │
│                          │ OLTP Operations                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Azure Cosmos DB                                  │   │
│  │  ┌─────────────────────────┐    ┌─────────────────────────┐        │   │
│  │  │   Transactional Store   │───▶│   Analytical Store      │        │   │
│  │  │   (Row-based)           │    │   (Column-based)        │        │   │
│  │  │                         │    │                         │        │   │
│  │  │  • Fast point reads     │    │  • Optimized for scans  │        │   │
│  │  │  • Low-latency writes   │    │  • Compressed storage   │        │   │
│  │  │  • ACID transactions    │    │  • Auto-indexed         │        │   │
│  │  └─────────────────────────┘    └───────────┬─────────────┘        │   │
│  └─────────────────────────────────────────────┼───────────────────────┘   │
│                                                 │                           │
│                                                 │ Azure Synapse Link        │
│                                                 │ (No ETL)                  │
│                                                 ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Azure Synapse Analytics                           │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│  │  │ Serverless SQL  │  │  Spark Pools    │  │  Dedicated SQL  │     │   │
│  │  │                 │  │                 │  │                 │     │   │
│  │  │ • Ad-hoc queries│  │ • ML/Data Eng   │  │ • Data Warehouse│     │   │
│  │  │ • T-SQL syntax  │  │ • Python/Scala  │  │ • Power BI      │     │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## When to Use Azure Synapse Link

### ✅ Ideal Use Cases

| Scenario | Why Synapse Link Works |
|----------|----------------------|
| **Real-time operational analytics** | Query live operational data without affecting transactions |
| **Daily/hourly analytics on operational data** | Near real-time sync without ETL pipelines |
| **Business intelligence dashboards** | Connect Power BI directly to analytical store |
| **Machine learning on fresh data** | Train models on recent operational data |
| **IoT analytics** | Analyze streaming data stored in Cosmos DB |
| **Combining operational and historical data** | Join Cosmos DB data with data lake in Synapse |

### ❌ When NOT to Use

| Scenario | Better Alternative |
|----------|-------------------|
| Simple change event processing | Use Change Feed with Azure Functions |
| ETL to non-Synapse destinations | Use Change Feed or Azure Data Factory |
| Delete operation tracking | Use Change Feed (delete isn't in analytical store) |
| Sub-second analytics latency | Query operational store directly |

---

## Comparison with Alternative Solutions

### Exam Scenario: Analyzing Operational Data Without Affecting Performance

**Scenario:**
> You have an Azure Synapse Analytics instance (AS1) and an Azure Cosmos DB SQL API account (CDB1). CDB1 hosts a container that stores continuously updated operational data. You need to analyze the operational data daily **without affecting the performance of the operational data store**.

### Solution Comparison

| Solution | Impact on Operational Store | Real-Time Data | Complexity | Verdict |
|----------|---------------------------|----------------|------------|---------|
| **Azure Synapse Link** | ✅ No impact | ✅ Near real-time | Low | ✅ **CORRECT** |
| Azure Cosmos DB Change Feed | ⚠️ Requires additional processing | ✅ Real-time events | High | ❌ Incomplete |
| Azure Data Factory (ADF) | ❌ ETL impacts source | ⚠️ Batch only | Medium | ❌ Performance impact |
| PolyBase | ❌ Not supported for Cosmos DB | ❌ No direct support | High | ❌ Wrong technology |

### Detailed Analysis

#### ✅ Azure Synapse Link for Azure Cosmos DB (CORRECT ANSWER)

**Why it's correct:**
- **No performance impact**: Analytical queries run against a separate analytical store
- **HTAP capability**: Hybrid transactional-analytical processing without data movement
- **No ETL**: Data automatically syncs to analytical store
- **Direct integration**: Native connection between Cosmos DB and Synapse Analytics
- **Near real-time**: Changes are available for analytics within ~2 minutes

```
CDB1 (Operational) ──[Auto Sync]──▶ Analytical Store ──[Synapse Link]──▶ AS1 (Analytics)
       │                                                                      │
       │            No ETL, No Performance Impact                            │
       └─────────────────────────────────────────────────────────────────────┘
```

#### ❌ Azure Cosmos DB Change Feed (INCORRECT)

**Why it's incorrect:**
- Change feed captures changes but **doesn't directly support analytics**
- Requires building a full integration pipeline:
  - Azure Functions or Stream Analytics to process changes
  - Storage account or data lake for staging
  - Additional processing to load into Synapse
- Adds complexity and maintenance overhead
- Not a direct analytical solution

```
CDB1 ──▶ Change Feed ──▶ Azure Functions ──▶ Storage ──▶ Processing ──▶ AS1
                         (Extra Components Required)
```

#### ❌ Azure Data Factory with Cosmos DB and Synapse Connectors (INCORRECT)

**Why it's incorrect:**
- **Introduces ETL overhead** that impacts the operational store
- Copy activities read from the operational store, consuming RUs
- Batch processing introduces latency
- Violates the requirement: "without affecting the performance"

```
CDB1 ◀──[Read RUs Consumed]── ADF ──▶ AS1
         (Performance Impact!)
```

#### ❌ Azure Synapse Analytics with PolyBase (INCORRECT)

**Why it's incorrect:**
- PolyBase is designed for:
  - Azure Data Lake Storage
  - Azure Blob Storage
  - SQL Server
- **PolyBase does NOT support Azure Cosmos DB as a data source**
- Would require intermediate data movement to blob storage first
- Wrong technology choice for this scenario

---

## Configuration Steps

### Step 1: Enable Azure Synapse Link on Cosmos DB Account

```bash
# Using Azure CLI
az cosmosdb update \
  --name <cosmos-account-name> \
  --resource-group <resource-group> \
  --enable-analytical-storage true
```

### Step 2: Enable Analytical Store on Container

When creating a new container:

```bash
az cosmosdb sql container create \
  --account-name <cosmos-account-name> \
  --database-name <database-name> \
  --name <container-name> \
  --partition-key-path "/partitionKey" \
  --analytical-storage-ttl -1  # -1 means infinite retention
```

### Step 3: Connect from Azure Synapse Analytics

In Synapse Studio, create a linked service to Cosmos DB and query using SQL:

```sql
-- Query Cosmos DB analytical store from Synapse SQL Serverless
SELECT TOP 100 *
FROM OPENROWSET(
    'CosmosDB',
    'Account=<account-name>;Database=<database-name>;Key=<key>',
    <container-name>
) AS documents
```

---

## Best Practices

### 1. **Plan Analytical TTL**
- Set appropriate Time-To-Live for analytical store
- `-1` for infinite retention
- Consider storage costs for long retention

### 2. **Design for Analytics**
- Structure documents with analytics in mind
- Avoid deeply nested arrays for frequently queried fields
- Use consistent property names and types

### 3. **Query Optimization**
- Use column projection (SELECT specific columns)
- Apply filters to reduce data scanned
- Leverage partitioning in queries

### 4. **Monitor Sync Latency**
- Track analytical store sync latency
- Alert on unexpected delays
- Typical latency: < 2 minutes

### 5. **Cost Management**
- Analytical storage is charged separately
- Monitor storage growth
- Set appropriate TTL to manage costs

---

## Limitations

| Limitation | Details |
|------------|---------|
| **Supported APIs** | NoSQL, MongoDB, Gremlin (API for Gremlin in preview) |
| **Delete operations** | Deletes are not reflected in analytical store by default |
| **Sync latency** | Near real-time (~2 minutes), not instant |
| **Schema changes** | Adding new properties may require schema refresh |
| **Existing containers** | Cannot enable analytical store on existing containers (must recreate) |
| **Regional availability** | Check documentation for supported regions |

---

## Resources

- [What is Azure Synapse Link for Azure Cosmos DB?](https://learn.microsoft.com/en-us/azure/cosmos-db/synapse-link)
- [Configure Azure Synapse Link](https://learn.microsoft.com/en-us/azure/cosmos-db/configure-synapse-link)
- [Azure Cosmos DB Change Feed](https://learn.microsoft.com/en-us/azure/cosmos-db/change-feed)
- [Load data in Azure Synapse Analytics](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql/load-data-overview)
- [Analytical store pricing](https://azure.microsoft.com/en-us/pricing/details/cosmos-db/)
- [Configure private endpoints for Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-private-endpoints)
- [Configure virtual network service endpoint for Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-vnet-service-endpoint)
- [Managed private endpoints in Azure Synapse Analytics](https://learn.microsoft.com/en-us/azure/synapse-analytics/security/synapse-workspace-managed-private-endpoints)

---

## Summary

**Key Takeaway for Exams:**

When you need to analyze operational data from Azure Cosmos DB using Azure Synapse Analytics **without affecting performance**, **Azure Synapse Link** is the correct answer because:

1. ✅ It creates a zero-impact connection to operational data
2. ✅ It's a native HTAP solution (no ETL required)
3. ✅ It provides near real-time data availability
4. ✅ It's the only option that truly isolates analytical workloads from transactional workloads

**Remember:** Change Feed requires additional processing, ADF impacts performance, and PolyBase doesn't support Cosmos DB directly.

---

## Secure Network Connectivity: Managed Private Endpoints

### Exam Scenario: Secure Traffic Between Azure Synapse and Cosmos DB

**Scenario:**
> You need to integrate Azure Cosmos DB and Azure Synapse. The solution must meet the following requirements:
> - Traffic from an Azure Synapse workspace to the Azure Cosmos DB account must be sent via the **Microsoft backbone network**
> - Traffic from the Azure Synapse workspace to the Azure Cosmos DB account must **NOT be routed over the internet**
> - Implementation effort must be **minimized**
>
> What should you enable when configuring the Azure Cosmos DB account?

### Solution: Managed Private Endpoints ✅

**Managed Private Endpoints** is the correct answer because:

1. ✅ **Microsoft Backbone Network**: Traffic flows through Azure's private network infrastructure, never traversing the public internet
2. ✅ **No Internet Routing**: Private endpoints are associated with a subnet within your Virtual Network (VNet), ensuring traffic stays within Azure's backbone
3. ✅ **Minimal Implementation Effort**: Azure Synapse natively supports managed private endpoints, requiring minimal configuration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Secure Network Architecture                          │
│                                                                              │
│  ┌────────────────────────┐         ┌────────────────────────┐             │
│  │   Azure Synapse        │         │   Azure Cosmos DB      │             │
│  │   Workspace            │         │   Account              │             │
│  │                        │         │                        │             │
│  │  ┌──────────────────┐  │         │  ┌──────────────────┐  │             │
│  │  │ Managed Private  │──┼─────────┼─▶│ Private Endpoint │  │             │
│  │  │ Endpoint         │  │   VNet  │  │                  │  │             │
│  │  └──────────────────┘  │ Backbone│  └──────────────────┘  │             │
│  └────────────────────────┘         └────────────────────────┘             │
│                                                                              │
│              Traffic stays on Microsoft backbone network                     │
│                    ✗ NO public internet routing                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Server-level Firewall Rules** | Controls access based on IP addresses/ranges. Does not address routing traffic via Microsoft backbone network or preventing internet routing. Provides access control, not network path control. |
| **Service Endpoint Policies** | Define routing preferences for Azure services accessing your Cosmos DB account. Designed for scenarios where Azure services need to access Cosmos DB, NOT for traffic originating from Azure Synapse workspace. |

### Key Differences

| Feature | Managed Private Endpoints | Service Endpoints | Firewall Rules |
|---------|--------------------------|-------------------|----------------|
| **Traffic Path** | Microsoft backbone only | Microsoft backbone (outbound) | Internet (filtered) |
| **Internet Routing** | ❌ Never | ⚠️ Possible | ✅ Yes (filtered by IP) |
| **VNet Integration** | ✅ Full private access | ✅ VNet to Azure service | ❌ IP-based only |
| **Implementation** | Minimal (managed by Synapse) | Moderate | Low |
| **Use Case** | Private connectivity from Synapse | VNet to Azure services | IP allowlisting |

### How Managed Private Endpoints Work

1. **Create Managed Private Endpoint**: From Azure Synapse workspace, create a managed private endpoint targeting the Cosmos DB account
2. **Approval**: The Cosmos DB account owner approves the private endpoint connection
3. **Private DNS**: Azure automatically configures DNS to route traffic through the private endpoint
4. **Secure Access**: All traffic from Synapse to Cosmos DB flows through the VNet via Microsoft's backbone

### Configuration in Azure Synapse

```
Azure Synapse Workspace
    │
    └── Manage
         │
         └── Managed private endpoints
              │
              └── + New → Azure Cosmos DB
                        → Select subscription
                        → Select Cosmos DB account
                        → Create
```

### Resources

- [Configure private endpoints for Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-private-endpoints)
- [Configure virtual network service endpoint for Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-configure-vnet-service-endpoint)
- [Managed private endpoints in Azure Synapse Analytics](https://learn.microsoft.com/en-us/azure/synapse-analytics/security/synapse-workspace-managed-private-endpoints)
