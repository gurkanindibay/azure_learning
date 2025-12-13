# Azure Data Factory

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Mapping Data Flows](#mapping-data-flows)
  - [Overview](#mapping-data-flows-overview)
  - [Use Cases](#use-cases)
  - [Blob to Data Lake Transformation](#blob-to-data-lake-transformation)
- [When to Use Azure Data Factory](#when-to-use-azure-data-factory)
- [Related Services Comparison](#related-services-comparison)
- [References](#references)

---

## Overview

**Azure Data Factory (ADF)** is a cloud-based ETL (Extract, Transform, Load) and data integration service that enables you to create data-driven workflows for orchestrating data movement and transforming data at scale.

### Key Capabilities
- **Data Integration**: Move data between various sources and destinations
- **Data Transformation**: Transform data using mapping data flows or compute services
- **Orchestration**: Schedule and monitor data pipelines
- **Hybrid Connectivity**: Connect to on-premises data sources using Self-hosted Integration Runtime

---

## Key Features

- **Visual Interface**: Code-free pipeline creation with drag-and-drop interface
- **Native Connectors**: 90+ built-in connectors for various data sources
- **Mapping Data Flows**: Visual, code-free data transformation at scale
- **Control Flow**: Complex workflow orchestration with conditional logic, loops, and parameters
- **Integration Runtime**: Execute data movement and transformation in different network environments
- **Monitoring**: Built-in monitoring and alerting capabilities

---

## Mapping Data Flows

### Mapping Data Flows Overview

**Mapping Data Flows** are a feature of Azure Data Factory that allows you to design and execute data transformations at scale without writing code. They provide a visual interface for building data transformation logic that runs on Apache Spark clusters managed by Azure.

#### Key Features of Mapping Data Flows
- **Code-Free Transformations**: Build complex transformations using visual designers
- **Scalable Processing**: Automatically scales on Spark clusters
- **Rich Transformation Library**: Includes joins, aggregations, lookups, filters, pivots, and more
- **Schema Drift Handling**: Automatically handles changing schemas
- **Debug Mode**: Test transformations interactively before deploying

---

### Use Cases

#### Primary Use Cases for Mapping Data Flows
1. **Data Cleansing and Enrichment**: Clean, validate, and enrich data before loading
2. **Data Migration**: Transform data structure when moving between systems
3. **ETL/ELT Pipelines**: Build comprehensive data transformation workflows
4. **Data Lake Ingestion**: Prepare and optimize data for analytics workloads
5. **Schema Evolution**: Handle changing data schemas automatically

---

### Blob to Data Lake Transformation

#### Scenario: Transform Data from Blob Storage to Data Lake

**Problem Statement**:
You have data files in Azure Blob Storage that need to be transformed and moved to Azure Data Lake Storage.

**Solution**: Use Azure Data Factory with Mapping Data Flows

#### Why Azure Data Factory?

Azure Data Factory is the **correct choice** for this scenario because:

1. **Native Mapping Data Flows Support**: ADF provides built-in mapping data flows for code-free transformations at scale
2. **Seamless Azure Integration**: Native connectivity to both Azure Blob Storage and Azure Data Lake Storage
3. **Purpose-Built for ETL**: Designed specifically for data integration and transformation workflows
4. **Cost-Effective**: No need to provision separate compute resources
5. **Enterprise-Ready**: Includes monitoring, scheduling, and orchestration capabilities

#### Implementation Approach

```
┌─────────────────────────┐
│  Azure Blob Storage     │
│  (Source Data Files)    │
└───────────┬─────────────┘
            │
            │ 1. Read Data
            ▼
┌─────────────────────────┐
│  Azure Data Factory     │
│  ┌───────────────────┐  │
│  │ Mapping Data Flow │  │
│  │ - Filter          │  │
│  │ - Transform       │  │
│  │ - Aggregate       │  │
│  │ - Join            │  │
│  └───────────────────┘  │
└───────────┬─────────────┘
            │
            │ 2. Write Transformed Data
            ▼
┌─────────────────────────┐
│ Azure Data Lake Storage │
│ (Destination)           │
└─────────────────────────┘
```

#### Steps to Implement

1. **Create Source Dataset**: Configure connection to Azure Blob Storage
2. **Create Sink Dataset**: Configure connection to Azure Data Lake Storage
3. **Create Mapping Data Flow**:
   - Add Source transformation
   - Add transformation logic (filter, join, aggregate, etc.)
   - Add Sink transformation
4. **Create Pipeline**: Add Data Flow activity and configure execution parameters
5. **Test and Monitor**: Use Debug mode to test, then schedule and monitor

---

## When to Use Azure Data Factory

### ✅ Use Azure Data Factory When:
- You need **code-free data transformations** at scale
- You're building **ETL/ELT pipelines** across Azure services
- You need to **orchestrate complex workflows** with dependencies
- You require **scheduled or event-driven** data processing
- You need to **integrate on-premises and cloud** data sources
- You want **managed and serverless** data integration

### ❌ Don't Use Azure Data Factory When:
- You need real-time streaming (use Azure Stream Analytics instead)
- You require advanced, code-based transformations (consider Azure Databricks)
- You're doing simple file copies without transformation (use AzCopy)
- You need interactive data exploration (use Azure Synapse Spark)

---

## Related Services Comparison

### Azure Data Factory vs. Alternatives

| Service | Purpose | Best For | Mapping Data Flows | Complexity |
|---------|---------|----------|-------------------|------------|
| **Azure Data Factory** | ETL/data integration | Scheduled pipelines, code-free transformations, data orchestration | ✅ Yes | Medium |
| **Azure Databricks** | Big data processing | Code-based analytics, ML workloads, complex transformations | ❌ No (uses notebooks) | High |
| **Azure Synapse Analytics** | Analytics platform | Unified analytics, SQL and Spark workloads | ✅ Yes (same as ADF) | High |
| **Azure Storage Sync** | File synchronization | On-prem to Azure Files sync | ❌ No | Low |
| **Azure File Sync** | File synchronization | Windows Server to Azure Files cache | ❌ No | Low |
| **Azure Data Box Gateway** | Data transfer appliance | Large data transfers to Azure | ❌ No | Low |

### Why NOT These Alternatives?

#### ❌ Azure Storage Sync
- **Purpose**: Synchronizes on-premises file servers with Azure Files
- **Why Not**: Does not support data transformation or blob-to-data-lake workflows
- **Use For**: Caching Azure Files on Windows Servers

#### ❌ Azure Data Box Gateway
- **Purpose**: Physical/virtual appliance for transferring large volumes of data from on-premises to Azure
- **Why Not**: Designed for data transfer, not in-cloud transformations or orchestrations
- **Use For**: Initial bulk data migration from on-premises

#### ❌ Azure Databricks
- **Purpose**: Apache Spark-based analytics platform
- **Why Not**: Requires code-based transformations (Python/Scala), doesn't use mapping data flows, introduces unnecessary complexity and cost for simple ETL
- **Use For**: Advanced analytics, ML workloads, complex code-based transformations

#### ❌ Azure File Sync
- **Purpose**: Synchronizes files between on-premises Windows Servers and Azure Files
- **Why Not**: Unrelated to blob storage or data transformation use cases
- **Use For**: File server cloud tiering and multi-site file access

---

## Key Decision Points

### When Choosing Between ADF and Databricks

| Requirement | Choose Azure Data Factory | Choose Azure Databricks |
|-------------|--------------------------|------------------------|
| Code-free transformations | ✅ | ❌ |
| Complex Spark code needed | ❌ | ✅ |
| Machine learning workflows | ❌ | ✅ |
| Simple ETL pipelines | ✅ | ❌ |
| Lower cost for basic ETL | ✅ | ❌ |
| Interactive notebooks | ❌ | ✅ |
| Built-in orchestration | ✅ | Requires ADF |

---

## References

- [Azure Data Factory Overview](https://learn.microsoft.com/en-us/azure/data-factory/introduction)
- [Mapping Data Flows Overview](https://learn.microsoft.com/en-us/azure/data-factory/concepts-data-flow-overview)
- [Transform Data Using Mapping Data Flows](https://learn.microsoft.com/en-us/azure/data-factory/transform-data-using-data-flow)
- [Azure Databricks Introduction](https://learn.microsoft.com/en-us/azure/databricks/introduction/)
- [Azure Data Box Gateway Overview](https://learn.microsoft.com/en-us/azure/databox-gateway/data-box-gateway-overview)
- [Azure File Sync Introduction](https://learn.microsoft.com/en-us/azure/storage/file-sync/file-sync-introduction)
- [Azure Data Factory vs Azure Databricks](https://learn.microsoft.com/en-us/azure/architecture/data-guide/technology-choices/data-science-and-machine-learning)

---

## Domain

**Design data storage solutions** - Data integration and transformation
