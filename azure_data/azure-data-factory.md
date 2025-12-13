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
- [Practice Questions](#practice-questions)
  - [Question 1: On-Premises Oracle to Azure Databricks Data Pipeline](#question-1-on-premises-oracle-to-azure-databricks-data-pipeline)
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

## Practice Questions

### Question 1: On-Premises Oracle to Azure Databricks Data Pipeline

#### Scenario

You have an **on-premises application named App1** that uses an **Oracle database**.

You plan to use **Azure Databricks** to transform and load data from App1 to an **Azure Synapse Analytics instance**.

You need to ensure that the App1 data is available to Databricks.

**Question:** Which **two Azure services** should you include in the solution?

---

#### Options

A. Azure Data Box Edge  
B. Azure Data Box Gateway  
C. Azure Import/Export service  
D. Azure Data Factory  
E. Azure Data Lake Storage

---

**Correct Answer:** **D. Azure Data Factory** and **E. Azure Data Lake Storage**

---

### Detailed Explanation

This scenario requires a solution to:
1. **Extract** data from on-premises Oracle database
2. **Stage** data in a format accessible to Azure Databricks
3. **Transform** data in Azure Databricks
4. **Load** data into Azure Synapse Analytics

#### Why Azure Data Factory is Correct ✅

**Azure Data Factory** is essential for extracting data from the on-premises Oracle database and orchestrating the data pipeline.

##### 1. **On-Premises Connectivity** ✅

Azure Data Factory provides **Self-hosted Integration Runtime** for connecting to on-premises data sources:

```plaintext
On-Premises Environment
│
├─ Self-hosted Integration Runtime
│  ├─ Installed on-premises server
│  ├─ Establishes secure outbound connection to Azure
│  ├─ Connects to Oracle database locally
│  └─ No inbound firewall rules required
│
└─ Oracle Database (App1)
      ↓
      ↓ Data extraction
      ↓
Azure Data Factory (Cloud)
      ↓
      ↓ Data movement
      ↓
Azure Data Lake Storage
```

**Key capabilities:**
- ✅ Native Oracle connector
- ✅ Self-hosted Integration Runtime for on-premises access
- ✅ No inbound ports required (outbound HTTPS only)
- ✅ Secure data transfer with encryption
- ✅ Incremental data extraction

##### 2. **Code-Free ETL Operations** ✅

Azure Data Factory provides:

- **Copy Activity**: Extract data from Oracle and load to Azure Data Lake Storage
- **Scheduling**: Automated, scheduled data extraction
- **Orchestration**: Coordinate pipeline activities
- **Monitoring**: Track pipeline execution and data movement
- **Error Handling**: Retry logic and error notifications

##### 3. **Integration with Azure Services** ✅

ADF integrates seamlessly with the entire solution:

```plaintext
Azure Data Factory:
├─ Extracts from: Oracle (on-premises)
├─ Writes to: Azure Data Lake Storage
├─ Triggers: Azure Databricks notebooks
└─ Loads to: Azure Synapse Analytics
```

##### 4. **Incremental Load Support** ✅

For ongoing operations, ADF supports:
- **Incremental extraction** - Only extract changed data
- **Watermark patterns** - Track last extraction timestamp
- **Change Data Capture (CDC)** - Capture database changes
- **Scheduled pipelines** - Run at specified intervals

---

#### Why Azure Data Lake Storage is Correct ✅

**Azure Data Lake Storage (ADLS Gen2)** serves as the staging and intermediate storage layer between the data source and Azure Databricks.

##### 1. **Optimized for Big Data Analytics** ✅

ADLS Gen2 is specifically designed for analytics workloads:

- **Hierarchical namespace** - Efficient directory operations
- **Large file support** - Optimized for big data files
- **High throughput** - Parallel data access
- **Cost-effective** - Lower cost than premium storage
- **Analytics-optimized formats** - Parquet, ORC, Delta Lake

##### 2. **Native Integration with Azure Databricks** ✅

Azure Databricks natively reads from ADLS Gen2:

```python
# Azure Databricks can directly read from ADLS Gen2
df = spark.read.format("parquet") \
    .load("abfss://container@storage.dfs.core.windows.net/data/")

# Perform transformations
transformed_df = df.filter(...).groupBy(...).agg(...)

# Write to Synapse Analytics
transformed_df.write \
    .format("sqldw") \
    .option("url", synapse_jdbc_url) \
    .save()
```

**Key benefits:**
- ✅ Direct mount in Databricks
- ✅ No data movement needed
- ✅ Efficient for large-scale data
- ✅ Supports Delta Lake format

##### 3. **Staging Layer for ETL Pipeline** ✅

ADLS serves as the intermediate layer:

```plaintext
ETL Pipeline Flow:

1. Extract (Azure Data Factory)
   Oracle → ADF → ADLS Gen2 (/raw/)
   
2. Transform (Azure Databricks)
   ADLS (/raw/) → Databricks → ADLS (/processed/)
   
3. Load (Azure Databricks or ADF)
   ADLS (/processed/) → Azure Synapse Analytics
```

**Why this architecture?**
- **Decoupling**: Separates extraction from transformation
- **Persistence**: Data persists between pipeline stages
- **Reprocessing**: Can reprocess data without re-extracting
- **Multiple consumers**: Other services can access staged data
- **Cost efficiency**: Store data in cost-effective format

##### 4. **Format Flexibility** ✅

ADLS supports formats optimal for Databricks:

| Format | Use Case | Benefits |
|--------|----------|----------|
| **Parquet** | Columnar storage | High compression, fast queries |
| **Delta Lake** | ACID transactions | Versioning, time travel, ACID |
| **CSV** | Simple data | Human-readable |
| **JSON** | Semi-structured | Nested data support |
| **ORC** | Optimized columnar | Hive compatibility |

**Recommended format:**
```plaintext
Azure Data Factory → Write as Parquet/Delta → ADLS Gen2
                                              ↓
Azure Databricks ← Read Parquet/Delta ← ADLS Gen2
```

---

### Complete Solution Architecture

```plaintext
┌───────────────────────────────────────────────────────────────┐
│                  ON-PREMISES ENVIRONMENT                      │
│                                                               │
│  ┌────────────────────┐     ┌──────────────────────────┐    │
│  │  App1              │     │  Self-hosted Integration │    │
│  │  (Oracle Database) │────▶│  Runtime                 │    │
│  └────────────────────┘     └──────────┬───────────────┘    │
│                                        │                      │
└────────────────────────────────────────┼──────────────────────┘
                                         │
                                         │ Secure outbound HTTPS
                                         │ (No inbound ports)
                                         ▼
┌───────────────────────────────────────────────────────────────┐
│                      AZURE CLOUD                              │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  1. Azure Data Factory ✅                             │    │
│  │     ├─ Oracle connector                               │    │
│  │     ├─ Self-hosted IR integration                     │    │
│  │     ├─ Copy activity (Oracle → ADLS)                 │    │
│  │     └─ Pipeline orchestration                         │    │
│  └─────────────────────┬────────────────────────────────┘    │
│                        │                                      │
│                        │ Writes extracted data                │
│                        ▼                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  2. Azure Data Lake Storage Gen2 ✅                   │    │
│  │     ├─ /raw/ (extracted data from Oracle)            │    │
│  │     ├─ /processed/ (transformed by Databricks)       │    │
│  │     └─ Format: Parquet / Delta Lake                  │    │
│  └─────────────────────┬────────────────────────────────┘    │
│                        │                                      │
│                        │ Reads for transformation             │
│                        ▼                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  3. Azure Databricks                                  │    │
│  │     ├─ Reads from ADLS (/raw/)                       │    │
│  │     ├─ Transforms data (filter, join, aggregate)     │    │
│  │     ├─ Writes back to ADLS (/processed/)             │    │
│  │     └─ Loads to Synapse Analytics                    │    │
│  └─────────────────────┬────────────────────────────────┘    │
│                        │                                      │
│                        │ Writes transformed data              │
│                        ▼                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  4. Azure Synapse Analytics                           │    │
│  │     ├─ Final destination                              │    │
│  │     ├─ Data warehouse                                 │    │
│  │     └─ Analytics and reporting                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

### Why Other Options Are Incorrect

#### A. Azure Data Box Edge ❌

**What it is:**
- Physical edge computing appliance
- Provides local compute, storage, and AI capabilities
- Processes data at the edge before sending to Azure

**Why incorrect:**

❌ **Edge computing device** - Designed for local data processing at remote locations  
❌ **Not for database ETL** - Meant for edge AI/ML scenarios, not Oracle database extraction  
❌ **Physical appliance** - Requires hardware deployment, not suitable for ongoing ETL operations  
❌ **Wrong use case** - Built for edge scenarios (retail stores, factories), not data center database integration

**Use Data Box Edge for:**
- Edge AI/ML inference at remote locations
- Local data preprocessing before cloud upload
- Disconnected or low-bandwidth edge scenarios

**Example scenario that WOULD use Data Box Edge:**
```plaintext
Scenario: Factory with IoT sensors generating data locally,
         need to process at edge before sending to cloud
Solution: Azure Data Box Edge ✅
```

---

#### B. Azure Data Box Gateway ❌

**What it is:**
- Virtual appliance for data transfer
- Bridges on-premises file servers to Azure Blob/File storage
- Designed for continuous data transfer from **file servers**

**Why incorrect:**

❌ **File server focus** - Designed for file-based workloads (SMB/NFS shares), not databases  
❌ **No database connectivity** - Cannot connect to Oracle databases  
❌ **No transformation support** - Simple data transfer only, no ETL capabilities  
❌ **Wrong protocol** - Works with file protocols, not database connections

**Use Data Box Gateway for:**
- Transferring files from on-premises file servers to Azure Storage
- Ongoing file synchronization scenarios
- Tiering cold data to Azure

**Example scenario that WOULD use Data Box Gateway:**
```plaintext
Scenario: Continuous backup of files from on-premises
         file server to Azure Blob Storage
Solution: Azure Data Box Gateway ✅
```

**Comparison:**

| Feature | Data Box Gateway | Azure Data Factory |
|---------|-----------------|-------------------|
| **Data source** | File servers (SMB/NFS) | Databases, files, APIs, SaaS |
| **Protocol** | File protocols | JDBC, ODBC, REST, etc. |
| **Transformation** | None | Full ETL capabilities |
| **Database support** | ❌ No | ✅ Yes (Oracle, SQL Server, etc.) |
| **Orchestration** | ❌ No | ✅ Yes |

---

#### C. Azure Import/Export Service ❌

**What it is:**
- Physical data transfer service
- Ships physical hard drives to Azure data center
- One-time bulk data migration

**Why incorrect:**

❌ **One-time migration** - Designed for initial bulk data transfer, not ongoing operations  
❌ **Physical media** - Requires shipping hard drives to Azure  
❌ **No automation** - Manual process, not suitable for continuous ETL  
❌ **No transformation** - Simple data copy, no ETL capabilities  
❌ **Long latency** - Takes days/weeks due to physical shipping

**Use Import/Export for:**
- Initial migration of large datasets (10+ TB)
- One-time data center migration
- Offline data transfer for security/compliance

**Example scenario that WOULD use Import/Export:**
```plaintext
Scenario: One-time migration of 50 TB of historical data
         from on-premises to Azure with limited bandwidth
Solution: Azure Import/Export service ✅
         (Ship encrypted hard drives to Azure)
```

**This scenario requires:**
- ✅ **Continuous data extraction** - Not one-time
- ✅ **Automated pipelines** - Not manual
- ✅ **Database connectivity** - Not file-based
- ✅ **Transformation capabilities** - Not just data copy

**Therefore, Import/Export is not suitable.**

---

### Comparison Table: Data Transfer Services

| Service | Type | Database Support | Ongoing/One-time | Transformation | Use Case |
|---------|------|------------------|------------------|----------------|----------|
| **Azure Data Factory** ✅ | Cloud service | ✅ Yes | Ongoing | ✅ Yes | ETL pipelines, database integration |
| **Azure Data Lake Storage** ✅ | Storage | N/A | Ongoing | N/A | Analytics data staging |
| **Data Box Edge** | Physical appliance | ❌ No | Ongoing | Limited | Edge computing |
| **Data Box Gateway** | Virtual appliance | ❌ No | Ongoing | ❌ No | File server to cloud |
| **Import/Export** | Physical service | ❌ No | One-time | ❌ No | Bulk offline migration |

---

### Implementation Steps

#### Step-by-Step Implementation

**Phase 1: Set Up Azure Data Factory**

```plaintext
1. Create Azure Data Factory instance
2. Install Self-hosted Integration Runtime on-premises:
   - Download installer from Azure portal
   - Install on server with Oracle access
   - Register with ADF using authentication key
   - Verify connectivity

3. Create Linked Service for Oracle:
   - Connection string to Oracle database
   - Authentication credentials
   - Test connection

4. Create Linked Service for ADLS Gen2:
   - Storage account connection
   - Container/path configuration
   - Authentication (managed identity recommended)
```

**Phase 2: Set Up Azure Data Lake Storage**

```plaintext
1. Create Azure Data Lake Storage Gen2 account:
   - Enable hierarchical namespace
   - Create containers:
     - /raw/oracle/ (for extracted data)
     - /processed/ (for transformed data)

2. Configure access:
   - Grant ADF managed identity Storage Blob Data Contributor role
   - Grant Databricks service principal access
   - Set up folder-level permissions
```

**Phase 3: Create Data Factory Pipeline**

```plaintext
1. Create datasets:
   - Source: Oracle table(s)
   - Sink: ADLS Gen2 Parquet files

2. Create Copy Activity pipeline:
   - Source: Oracle dataset
   - Sink: ADLS Gen2 dataset
   - Mapping: Column mappings
   - Settings: Parallelism, retry policy

3. Configure scheduling:
   - Trigger type: Scheduled
   - Frequency: Hourly/Daily
   - Incremental load: Use watermark column

4. Test and monitor:
   - Debug pipeline
   - Monitor execution
   - Set up alerts
```

**Phase 4: Configure Azure Databricks**

```python
# Mount ADLS Gen2 in Databricks
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": 
    "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": "<client-id>",
  "fs.azure.account.oauth2.client.secret": "<client-secret>",
  "fs.azure.account.oauth2.client.endpoint": 
    "https://login.microsoftonline.com/<tenant-id>/oauth2/token"
}

dbutils.fs.mount(
  source = "abfss://container@storage.dfs.core.windows.net/",
  mount_point = "/mnt/datalake",
  extra_configs = configs
)

# Read data from ADLS
df = spark.read.format("parquet") \
    .load("/mnt/datalake/raw/oracle/")

# Transform data
transformed_df = df \
    .filter(df.status == "active") \
    .groupBy("category") \
    .agg({"amount": "sum"})

# Write to Synapse Analytics
transformed_df.write \
    .format("com.databricks.spark.sqldw") \
    .option("url", synapse_jdbc_url) \
    .option("tempDir", "abfss://temp@storage.dfs.core.windows.net/") \
    .option("forwardSparkAzureStorageCredentials", "true") \
    .option("dbTable", "dbo.SalesAggregated") \
    .mode("overwrite") \
    .save()
```

---

### End-to-End Pipeline Flow

```plaintext
Daily ETL Pipeline:

1. Trigger: Scheduled (e.g., 2 AM daily)
   ├─ Azure Data Factory pipeline starts

2. Extract:
   ├─ ADF connects to Oracle via Self-hosted IR
   ├─ Executes SQL query (incremental: WHERE updated_date > watermark)
   ├─ Reads data from Oracle
   └─ Writes to ADLS: /raw/oracle/2024-12-13.parquet

3. Transform:
   ├─ ADF triggers Databricks notebook
   ├─ Databricks reads from ADLS: /raw/oracle/2024-12-13.parquet
   ├─ Applies transformations (cleansing, enrichment, aggregation)
   └─ Writes to ADLS: /processed/2024-12-13.parquet

4. Load:
   ├─ Databricks reads from: /processed/2024-12-13.parquet
   ├─ Writes to Synapse Analytics using PolyBase
   └─ Updates target tables

5. Monitoring:
   ├─ ADF logs execution metrics
   ├─ Alerts on failures
   └─ Cost tracking dashboard
```

---

### Key Takeaways

1. **Azure Data Factory for Data Movement**
   > Azure Data Factory is the standard service for moving data from on-premises databases to Azure. Its Self-hosted Integration Runtime enables secure connectivity without inbound firewall rules.

2. **Azure Data Lake Storage as Staging Layer**
   > ADLS Gen2 serves as the intermediate storage layer, decoupling data extraction from transformation and providing a persistent, cost-effective staging area optimized for analytics.

3. **Separation of Concerns**
   > - **ADF:** Extracts and orchestrates
   > - **ADLS:** Stores and stages
   > - **Databricks:** Transforms
   > - **Synapse:** Analyzes

4. **Data Box Services are for Physical Transfer**
   > Data Box Edge and Data Box Gateway are physical/virtual appliances for specific edge or file-based scenarios, not for database ETL operations.

5. **Import/Export is for One-Time Migration**
   > Azure Import/Export service is for initial bulk data migration via physical drives, not for ongoing data pipelines.

---

### Exam Tips

> **Remember:** For on-premises database to Azure cloud ETL scenarios, think **Azure Data Factory** (movement + orchestration) + **Azure Data Lake Storage** (staging).

> **Key phrase to watch for:** "on-premises database" + "Azure Databricks" = Need ADF for extraction + ADLS for staging.

> **Don't be fooled by:** Data Box services - They're for specific physical/file-based scenarios, not database ETL.

> **Architecture pattern:** On-prem DB → ADF (extract) → ADLS (stage) → Databricks (transform) → Synapse (load)

---

### Reference Links

**Official Documentation:**
- [Azure Data Factory Introduction](https://learn.microsoft.com/en-us/azure/data-factory/introduction)
- [Self-hosted Integration Runtime](https://learn.microsoft.com/en-us/azure/data-factory/create-self-hosted-integration-runtime)
- [Copy data from Oracle using Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/connector-oracle)
- [Azure Data Lake Storage Gen2 Introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- [Azure Databricks and Azure Data Lake Storage](https://learn.microsoft.com/en-us/azure/databricks/data/data-sources/azure/azure-datalake-gen2)
- [Azure Data Box Gateway Overview](https://learn.microsoft.com/en-us/azure/databox-gateway/data-box-gateway-overview)
- [Azure Data Box Gateway Use Cases](https://learn.microsoft.com/en-us/azure/databox-gateway/data-box-gateway-use-cases)
- [Azure Import/Export Service](https://learn.microsoft.com/en-us/azure/import-export/storage-import-export-service)

**Related Topics:**
- Azure Data Factory pipelines and activities
- Self-hosted Integration Runtime deployment
- Azure Data Lake Storage optimization for analytics
- Azure Databricks data ingestion patterns
- Incremental load patterns with watermarks

**Domain:** Design data storage solutions

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
