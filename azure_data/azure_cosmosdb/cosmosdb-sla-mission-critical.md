# Azure Cosmos DB SLA for Mission-Critical Applications

## Table of Contents

- [Overview](#overview)
- [Why Cosmos DB for Mission-Critical Applications](#why-cosmos-db-for-mission-critical-applications)
- [Azure Cosmos DB SLA Guarantees](#azure-cosmos-db-sla-guarantees)
  - [Latency SLA](#latency-sla)
  - [Throughput SLA](#throughput-sla)
  - [Availability SLA](#availability-sla)
  - [Consistency SLA](#consistency-sla)
- [Comparison with Other Azure Storage Solutions](#comparison-with-other-azure-storage-solutions)
  - [Azure Cosmos DB vs Azure Data Lake Storage Gen2](#azure-cosmos-db-vs-azure-data-lake-storage-gen2)
  - [Azure Cosmos DB vs Azure Blob Storage](#azure-cosmos-db-vs-azure-blob-storage)
  - [Azure Cosmos DB vs Azure SQL](#azure-cosmos-db-vs-azure-sql)
- [Decision Matrix: Choosing Storage for Mission-Critical Applications](#decision-matrix-choosing-storage-for-mission-critical-applications)
- [Practice Question](#practice-question)
- [References](#references)

## Overview

When designing storage solutions for **mission-critical applications**, one of the most important requirements is predictable performance. This means having **Service Level Agreements (SLAs)** that guarantee not just availability, but also **latency** and **throughput** for operations.

**Azure Cosmos DB** is the only Azure storage service that provides comprehensive SLAs covering:
- Write latency
- Read latency
- Throughput
- Consistency
- Availability

## Why Cosmos DB for Mission-Critical Applications

Azure Cosmos DB is specifically designed for mission-critical workloads that require:

| Requirement | Cosmos DB Capability |
|-------------|---------------------|
| **Predictable Performance** | SLA-backed single-digit millisecond latency |
| **High Throughput** | Elastic scaling with guaranteed throughput |
| **Global Distribution** | Multi-region writes with automatic failover |
| **High Availability** | 99.999% availability with multi-region configuration |
| **Data Consistency** | Five consistency levels with SLA guarantees |

## Azure Cosmos DB SLA Guarantees

### Latency SLA

Azure Cosmos DB provides **SLA-backed latency guarantees** at the **99th percentile**:

| Operation Type | Latency Guarantee (P99) |
|----------------|------------------------|
| **Point Reads** | < 10 milliseconds |
| **Point Writes** | < 10 milliseconds |
| **Indexed Queries** | < 10 milliseconds |

**Key Points:**
- **Single-digit millisecond latency** for both reads and writes
- Latency is measured at the **99th percentile**, meaning 99% of operations complete within the guaranteed time
- This guarantee applies globally regardless of the number of regions

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cosmos DB Latency SLA                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Point Reads:   ████████░░  < 10ms (P99)                      │
│   Point Writes:  ████████░░  < 10ms (P99)                      │
│   Queries:       ████████░░  < 10ms (P99) for indexed queries  │
│                                                                 │
│   ✓ Guaranteed in SLA                                          │
│   ✓ Financially backed                                         │
│   ✓ Applies to all regions                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Throughput SLA

Azure Cosmos DB guarantees the **provisioned throughput** you configure:

| Throughput Type | SLA Guarantee |
|-----------------|---------------|
| **Provisioned RU/s** | 100% of configured throughput available |
| **Autoscale** | Scales up to configured maximum |
| **Burst Capacity** | Handles short-term spikes |

**Key Points:**
- When you provision 10,000 RU/s, you are **guaranteed** to have 10,000 RU/s available
- Throughput is distributed evenly across all partitions
- SLA violation occurs if throttling happens below provisioned capacity

### Availability SLA

| Configuration | Availability SLA |
|---------------|------------------|
| Single Region (Single Write) | 99.99% |
| Multi-Region (Single Write) | 99.99% (reads), 99.99% (writes) |
| Multi-Region (Multi Write) | **99.999%** |

**Note:** 99.999% availability means less than **5.26 minutes of downtime per year**.

### Consistency SLA

Azure Cosmos DB guarantees consistency according to the selected consistency level:

| Consistency Level | Guarantee |
|-------------------|-----------|
| **Strong** | Linearizability |
| **Bounded Staleness** | Consistent Prefix + bounded lag |
| **Session** | Consistent Prefix within session |
| **Consistent Prefix** | Reads never see out-of-order writes |
| **Eventual** | Eventual convergence |

All consistency guarantees are **backed by SLA**.

## Comparison with Other Azure Storage Solutions

### Azure Cosmos DB vs Azure Data Lake Storage Gen2

| Feature | Azure Cosmos DB | Azure Data Lake Storage Gen2 |
|---------|-----------------|------------------------------|
| **Primary Use Case** | Transactional workloads | Big data analytics |
| **Latency SLA** | ✅ Yes (< 10ms P99) | ❌ No |
| **Throughput SLA** | ✅ Yes | ❌ No |
| **Availability SLA** | ✅ Yes (up to 99.999%) | ✅ Yes (availability only) |
| **Write Latency** | Single-digit milliseconds | Not guaranteed |
| **Best For** | Mission-critical transactions | Data lakes, analytics pipelines |

**Why ADLS Gen2 is NOT suitable for mission-critical transactional applications:**
- Optimized for **throughput over latency**
- Designed for **batch processing**, not real-time transactions
- No SLA for operation-level latency
- Best suited for **analytical workloads**, not OLTP

### Azure Cosmos DB vs Azure Blob Storage

| Feature | Azure Cosmos DB | Azure Blob Storage |
|---------|-----------------|-------------------|
| **Primary Use Case** | NoSQL database | Object storage |
| **Latency SLA** | ✅ Yes (< 10ms P99) | ❌ No |
| **Throughput SLA** | ✅ Yes | ❌ No |
| **Availability SLA** | ✅ Yes (up to 99.999%) | ✅ Yes (availability/durability) |
| **Consistency SLA** | ✅ Yes (5 levels) | ❌ No |
| **Best For** | Transactional data | Unstructured blob data |

**Why Blob Storage is NOT suitable for mission-critical transactional applications:**
- Provides SLAs for **availability and durability**, not latency
- Designed for **storing large objects**, not transactional records
- No guaranteed response time for read/write operations
- Best suited for **media files, backups, static content**

### Azure Cosmos DB vs Azure SQL

| Feature | Azure Cosmos DB | Azure SQL |
|---------|-----------------|-----------|
| **Primary Use Case** | NoSQL, globally distributed | Relational database |
| **Latency SLA** | ✅ Yes (< 10ms P99) | ❌ No (performance tiers exist, not SLA) |
| **Throughput SLA** | ✅ Yes (RU/s guarantee) | ❌ No (DTU/vCore capacity, not SLA) |
| **Availability SLA** | ✅ Yes (up to 99.999%) | ✅ Yes (up to 99.995%) |
| **Write Latency Guarantee** | ✅ SLA-backed | ❌ Not SLA-backed |
| **Best For** | Global apps, flexible schema | Relational data, ACID transactions |

**Why Azure SQL is NOT the best choice for latency/throughput SLA requirements:**
- SLA covers **availability**, not individual operation performance
- Performance varies based on tier, but **not guaranteed by SLA**
- No explicit SLA for **write latency** or **throughput**
- Better suited when **relational features** are the primary requirement

## Decision Matrix: Choosing Storage for Mission-Critical Applications

| Requirement | Cosmos DB | ADLS Gen2 | Blob Storage | Azure SQL |
|-------------|-----------|-----------|--------------|-----------|
| Write Latency SLA | ✅ | ❌ | ❌ | ❌ |
| Read Latency SLA | ✅ | ❌ | ❌ | ❌ |
| Throughput SLA | ✅ | ❌ | ❌ | ❌ |
| Consistency SLA | ✅ | ❌ | ❌ | ❌ |
| Availability SLA | ✅ | ✅ | ✅ | ✅ |
| Multi-Region Writes | ✅ | ❌ | ❌ | ❌ |
| Global Distribution | ✅ | Limited | Limited | Limited |

```
┌────────────────────────────────────────────────────────────────────────┐
│     Storage Solution Selection for Mission-Critical Applications       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  Need SLA for:                                                         │
│  ┌─────────────────┐                                                   │
│  │ Write Latency?  │──Yes──► Azure Cosmos DB ◄──────────────┐         │
│  └────────┬────────┘                                         │         │
│           │ No                                               │         │
│           ▼                                                  │         │
│  ┌─────────────────┐                                         │         │
│  │ Throughput?     │──Yes──────────────────────────────────►─┘         │
│  └────────┬────────┘                                                   │
│           │ No                                                         │
│           ▼                                                            │
│  ┌─────────────────────────────────────────────┐                       │
│  │ What type of data?                          │                       │
│  ├─────────────────────────────────────────────┤                       │
│  │ Big data analytics    ──► ADLS Gen2         │                       │
│  │ Unstructured objects  ──► Blob Storage      │                       │
│  │ Relational data       ──► Azure SQL         │                       │
│  │ Transactional NoSQL   ──► Cosmos DB         │                       │
│  └─────────────────────────────────────────────┘                       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Practice Question

### Scenario: Mission-Critical Application Storage Recommendation

**Question:**

You need to recommend a storage solution for the records of a mission-critical application.

The solution must provide a **Service Level Agreement (SLA) for the latency of write operations** and the **throughput**.

What should you include in the recommendation?

| Option | Answer |
|--------|--------|
| A. Azure Data Lake Storage Gen2 | ❌ Incorrect |
| B. Azure Blob Storage | ❌ Incorrect |
| C. Azure SQL | ❌ Incorrect |
| D. Azure Cosmos DB | ✅ **Correct** |

### Explanation

**Azure Cosmos DB is correct** because it is the **only option** among the choices that provides a Service Level Agreement (SLA) not just for availability, but also for:
- **Write latency** (< 10ms at P99)
- **Read latency** (< 10ms at P99)
- **Throughput** (guaranteed provisioned RU/s)
- **Consistency** (five consistency levels)

Cosmos DB guarantees **single-digit millisecond latency at the 99th percentile** for both read and write operations, making it ideal for mission-critical applications that require predictable performance. It also allows for:
- **Scaling throughput elastically**
- **Multi-region writes**
- **Built-in high availability**

**Azure Data Lake Storage Gen2 is incorrect** because:
- Optimized for big data analytics, not transactional workloads
- Does not offer SLAs for operation-level latency or throughput
- Not designed for mission-critical transactional applications

**Azure Blob Storage is incorrect** because:
- Provides SLAs only for availability and durability
- No SLA for specific operation latencies or throughput
- Suited for large-scale object storage, not transactional performance

**Azure SQL is incorrect** because:
- Offers high availability and performance tiers
- Does **not** provide SLAs for write latency or throughput at the same level of granularity as Cosmos DB
- SLA mainly covers availability, not individual performance metrics

### Key Takeaway

> When an exam question asks about **SLA for latency and/or throughput**, **Azure Cosmos DB** is almost always the correct answer because it is the only Azure service that provides comprehensive, financially-backed SLAs for these performance metrics.

## References

- [Introduction to Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/introduction)
- [Azure Cosmos DB SLA](https://azure.microsoft.com/en-us/support/legal/sla/cosmos-db/)
- [Latency guarantees in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels-tradeoffs)
- [Introduction to Azure Data Lake Storage Gen2](https://learn.microsoft.com/en-us/training/modules/introduction-to-azure-data-lake-storage/2-azure-data-lake-gen2)
- [Introduction to Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction)
- [Azure SQL Database Overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview?view=azuresql)
