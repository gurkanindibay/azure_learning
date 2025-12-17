# Azure Databricks Overview

Azure Databricks is a unified analytics platform optimized for the Microsoft Azure cloud services platform. It provides a collaborative environment for data engineers, data scientists, and machine learning engineers to work together on big data and AI projects.

## Table of Contents
- [Overview](#overview)
- [Key Characteristics](#key-characteristics)
- [Cluster Configuration Options](#cluster-configuration-options)
- [Practice Questions](#practice-questions)
- [Comparison with Azure Synapse Analytics and Microsoft Fabric](#comparison-with-azure-synapse-analytics-and-microsoft-fabric)
- [When to Use Each Platform](#when-to-use-each-platform)
- [References](#references)

---

## Overview

Azure Databricks is built on Apache Spark and provides:
- **Unified Analytics**: Single platform for data engineering, data science, and machine learning
- **Collaborative Notebooks**: Interactive workspace for teams
- **Optimized Spark**: Enhanced Apache Spark with proprietary optimizations
- **Delta Lake**: Open-source storage layer for reliable data lakes
- **MLflow Integration**: End-to-end machine learning lifecycle management

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Apache Spark Based** | Built on open-source Apache Spark with optimizations |
| **Delta Lake** | ACID transactions on data lakes |
| **Unity Catalog** | Unified governance for data and AI assets |
| **Collaborative Notebooks** | Interactive development environment |
| **Auto-scaling Clusters** | Dynamic resource allocation |
| **MLflow** | ML experiment tracking and model management |

---

## Cluster Configuration Options

When deploying Azure Databricks to support machine learning applications, several cluster configuration options are available:

### Credential Passthrough

**Credential passthrough** allows Azure Databricks clusters to access Azure Data Lake Storage (ADLS) using the identity of the user who is logged in. 

#### Key Benefits:
- **Per-User Access Control**: Access control is enforced at the storage layer based on the user's Microsoft Entra ID permissions
- **Granular Permissions**: Ensures that users (e.g., data engineers) can only access folders they are authorized for
- **Minimal Development Effort**: No need to implement custom access logic in code
- **Native Integration**: Integrates natively with Databricks Premium SKU

#### Use Case:
When data engineers mount an Azure Data Lake Storage account to the Databricks file system and permissions to folders are granted directly to individual data engineers, credential passthrough ensures each engineer can only access their authorized folders.

#### Requirements:
- Requires Azure Databricks **Premium SKU**
- Users must have appropriate Microsoft Entra ID permissions on the storage account

### Managed Identities

**Managed Identities** provide access at the cluster or workspace level, not per-user.

#### Limitations:
- All users share the same identity when accessing storage
- Does **not** allow enforcing per-user folder permissions
- Not suitable when individual user-level access control is required

#### Use Case:
Appropriate when all users in a workspace should have the same level of access to storage resources.

### Secret Scope

**Secret Scope** is used to store and manage secrets, such as credentials and API keys.

#### Characteristics:
- Securely stores sensitive information
- Does **not** enforce per-user access permissions to folders
- Used for managing shared credentials, not for user-level access control

### MLflow

**MLflow** is a tool used to track machine learning experiments and models.

#### Purpose:
- Experiment tracking
- Model versioning
- Model deployment
- Does **not** handle storage access or permission enforcement

### Photon Runtime

**Photon** is an execution engine that enhances query performance.

#### Characteristics:
- High-performance vectorized query engine
- Improves SQL and DataFrame workload performance
- Does **not** provide authentication or folder-level access control functionality

---

## Practice Questions

### Question 1: Machine Learning Application with Per-User Access

**Scenario**: You plan to deploy Azure Databricks to support a machine learning application. Data engineers will mount an Azure Data Lake Storage account to the Databricks file system. Permissions to folders are granted directly to the data engineers.

**Requirements**:
- Ensure that the data engineers can only access folders to which they have permission
- Minimize development effort
- Minimize costs

**Question**: What should you include in the recommendation for "Cluster Configuration"?

**Options**:
- A) Credential passthrough
- B) Managed Identities
- C) MLflow
- D) A runtime that contains Photon
- E) Secret Scope

**Correct Answer**: **A) Credential passthrough**

**Explanation**:

**Credential passthrough** is correct because:
- It allows Azure Databricks clusters to access Azure Data Lake Storage using the identity of the user who is logged in
- Access control is enforced at the storage layer based on the user's Microsoft Entra ID permissions
- Ensures that data engineers can only access folders they are authorized for
- Minimizes development effort because there is no need to implement custom access logic in code
- Integrates natively with Databricks Premium SKU

**Why Other Options Are Incorrect**:

| Option | Reason Not Suitable |
|--------|---------------------|
| **Managed Identities** | Provides access at the cluster or workspace level, not per-user. All users would share the same identity when accessing storage, which does not allow enforcing per-user folder permissions |
| **MLflow** | A tool used to track machine learning experiments and models. It does not handle storage access or permission enforcement |
| **A runtime that contains Photon** | Photon is an execution engine that enhances query performance. It does not provide any functionality related to authentication or folder-level access control |
| **Secret Scope** | Used to store and manage secrets, such as credentials and API keys. It does not enforce per-user access permissions to folders in Azure Data Lake Storage |

**Reference Links**:
- [Azure Databricks Account Settings](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/account)
- [ADLS Credential Passthrough](https://learn.microsoft.com/en-us/azure/databricks/security/credential-passthrough/adls-passthrough)

---

## Comparison with Azure Synapse Analytics and Microsoft Fabric

### Platform Overview Comparison

| Aspect | Azure Databricks | Azure Synapse Analytics | Microsoft Fabric |
|--------|------------------|------------------------|------------------|
| **Primary Focus** | Big data & ML workloads | Enterprise data warehousing | Unified SaaS analytics |
| **Foundation** | Apache Spark | Multiple engines (SQL, Spark) | OneLake + multiple workloads |
| **Deployment Model** | PaaS | PaaS | SaaS |
| **Data Lake Format** | Delta Lake | Parquet/Delta Lake | Delta Lake (OneLake) |
| **Query Language** | SQL, Python, Scala, R | T-SQL, KQL, Spark | T-SQL, KQL, DAX, Spark |
| **Target Users** | Data Engineers, Data Scientists | Data Engineers, BI Analysts | Entire analytics team |

### Detailed Feature Comparison

| Feature | Azure Databricks | Azure Synapse Analytics | Microsoft Fabric |
|---------|------------------|------------------------|------------------|
| **Data Warehousing** | ❌ Not primary use | ✅ Dedicated SQL Pools (MPP) | ✅ Fabric Data Warehouse |
| **Spark Processing** | ✅ Optimized Spark | ✅ Spark Pools | ✅ Data Engineering |
| **Machine Learning** | ✅ MLflow, AutoML | ✅ Azure ML integration | ✅ Data Science workload |
| **Real-Time Analytics** | ⚠️ Structured Streaming | ✅ Data Explorer Pools | ✅ Real-Time Analytics (KQL) |
| **ETL/Data Integration** | ✅ Notebooks, Jobs | ✅ Synapse Pipelines | ✅ Data Factory |
| **BI/Visualization** | ⚠️ Basic (needs Power BI) | ⚠️ Power BI integration | ✅ Native Power BI |
| **Serverless SQL** | ❌ No | ✅ Serverless SQL Pool | ✅ Direct Lake |
| **Governance** | ✅ Unity Catalog | ⚠️ Purview integration | ✅ Built-in + Purview |

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANALYTICS PLATFORM COMPARISON                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │   AZURE DATABRICKS  │  │   AZURE SYNAPSE     │  │  MICROSOFT FABRIC   │  │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤  │
│  │                     │  │                     │  │                     │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │
│  │  │ Unity Catalog │  │  │  │ Synapse Studio│  │  │  │ Fabric Portal │  │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │  │
│  │                     │  │                     │  │                     │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │
│  │  │  Spark Engine │  │  │  │ Dedicated SQL │  │  │  │   OneLake     │  │  │
│  │  │  (Optimized)  │  │  │  │ Pool (MPP)    │  │  │  │ (Unified Lake)│  │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │  │
│  │                     │  │                     │  │                     │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │
│  │  │  Delta Lake   │  │  │  │ Serverless SQL│  │  │  │ Data Factory  │  │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  │ Data Engineer │  │  │
│  │                     │  │                     │  │  │ Data Warehouse│  │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  │ Data Science  │  │  │
│  │  │    MLflow     │  │  │  │  Spark Pools  │  │  │  │ Real-Time     │  │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  │ Power BI      │  │  │
│  │                     │  │                     │  │  └───────────────┘  │  │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │                     │  │
│  │  │    Photon     │  │  │  │ Data Explorer │  │  │                     │  │
│  │  │   (Engine)    │  │  │  │    Pools      │  │  │                     │  │
│  │  └───────────────┘  │  │  └───────────────┘  │  │                     │  │
│  │                     │  │                     │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│                                                                              │
│  Best For:              Best For:                Best For:                   │
│  • ML/AI workloads      • Enterprise DW          • Unified analytics        │
│  • Data Engineering     • OLAP queries           • Power BI-centric orgs    │
│  • Delta Lake           • Mixed workloads        • SaaS simplicity          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pricing Model Comparison

| Aspect | Azure Databricks | Azure Synapse Analytics | Microsoft Fabric |
|--------|------------------|------------------------|------------------|
| **Model** | DBU (Databricks Units) | DWU (Data Warehouse Units) + Spark | CU (Capacity Units) |
| **Compute Billing** | Per-second cluster usage | Per-hour (dedicated), per-query (serverless) | Shared capacity pool |
| **Storage** | Azure Storage (separate) | Azure Storage (separate) | OneLake (included) |
| **Pause/Resume** | ✅ Clusters auto-terminate | ✅ Dedicated pools can pause | ✅ Capacity pause |
| **Reserved Capacity** | ✅ Available | ✅ Available | ✅ Available |

### Storage Layer Comparison

| Aspect | Azure Databricks | Azure Synapse Analytics | Microsoft Fabric |
|--------|------------------|------------------------|------------------|
| **Default Storage** | ADLS Gen2 + Delta Lake | ADLS Gen2 | OneLake (built-in) |
| **Data Format** | Delta Lake (Parquet + logs) | Parquet, Delta Lake | Delta Lake |
| **ACID Transactions** | ✅ Delta Lake | ⚠️ Only with Delta | ✅ OneLake |
| **Data Sharing** | Delta Sharing | Synapse Link | OneLake Shortcuts |
| **Multi-cloud** | ✅ AWS, Azure, GCP | ❌ Azure only | ❌ Azure only |

---

## When to Use Each Platform

### Choose Azure Databricks When:

✅ **Primary focus is machine learning and AI**  
✅ **Heavy data engineering with Spark**  
✅ **Need multi-cloud support** (AWS, Azure, GCP)  
✅ **Already invested in Databricks ecosystem**  
✅ **Complex ETL requiring custom code**  
✅ **Need Unity Catalog for governance**  
✅ **Delta Lake is central to architecture**  

### Choose Azure Synapse Analytics When:

✅ **Enterprise data warehousing is primary need**  
✅ **Need MPP for large-scale SQL analytics**  
✅ **Mixed workloads** (SQL + Spark + real-time)  
✅ **High-concurrency reporting** for thousands of users  
✅ **T-SQL expertise in the team**  
✅ **Need serverless SQL for ad-hoc queries**  
✅ **Already using Azure Data Factory pipelines**  

### Choose Microsoft Fabric When:

✅ **Want a unified SaaS platform** with minimal management  
✅ **Power BI-centric organization**  
✅ **Need all analytics capabilities in one platform**  
✅ **Want single billing model** across all workloads  
✅ **Prefer managed service over infrastructure management**  
✅ **New analytics projects** without existing platform investment  
✅ **Need real-time analytics with KQL**  

### Decision Matrix

| Scenario | Recommended Platform |
|----------|---------------------|
| ML/AI-focused team with Spark expertise | **Azure Databricks** |
| Enterprise DW with OLAP reporting | **Azure Synapse Analytics** |
| Unified analytics for entire organization | **Microsoft Fabric** |
| Multi-cloud data platform | **Azure Databricks** |
| Power BI-first analytics strategy | **Microsoft Fabric** |
| High-concurrency SQL reporting | **Azure Synapse Analytics** |
| Complex streaming + batch ML pipelines | **Azure Databricks** |
| Cost-conscious with variable workloads | **Microsoft Fabric** (capacity sharing) |
| T-SQL heavy workloads | **Azure Synapse Analytics** |
| Real-time log analytics (KQL) | **Synapse** or **Fabric** |

### Integration Scenarios

| Integration Need | Best Platform |
|-----------------|---------------|
| Databricks + Power BI | Use **Databricks SQL** endpoints |
| Synapse + ML | Use **Spark Pools** + Azure ML |
| Fabric + External Delta Lake | Use **Shortcuts** to Databricks Delta Lake |
| Cross-platform data sharing | **Delta Sharing** (Databricks) |

---

## Quick Reference Cheat Sheet

### When Requirements Say...

| Requirement | Answer |
|-------------|--------|
| "Per-user access to ADLS folders" | **Credential Passthrough** (Databricks) |
| "ML experiment tracking" | **MLflow** |
| "High-performance Spark queries" | **Photon Runtime** |
| "Cluster-level storage access" | **Managed Identities** |
| "Store API keys securely" | **Secret Scope** |
| "Big data + ML platform" | **Azure Databricks** |
| "Enterprise data warehouse" | **Azure Synapse Dedicated SQL Pool** |
| "Unified SaaS analytics" | **Microsoft Fabric** |
| "Multi-cloud analytics" | **Azure Databricks** |
| "Power BI-centric organization" | **Microsoft Fabric** |

### Platform Selection Quick Guide

```
                    ┌─────────────────────────────┐
                    │   What's your PRIMARY need? │
                    └─────────────┬───────────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │ ML/AI & Big  │      │ Enterprise   │      │ Unified SaaS │
    │ Data Spark   │      │ DW & OLAP    │      │ Analytics    │
    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
           │                     │                      │
           ▼                     ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │    AZURE     │      │    AZURE     │      │  MICROSOFT   │
    │  DATABRICKS  │      │   SYNAPSE    │      │    FABRIC    │
    └──────────────┘      └──────────────┘      └──────────────┘
```

---

## References

### Azure Databricks
- [Azure Databricks Documentation](https://learn.microsoft.com/en-us/azure/databricks/)
- [Azure Databricks Account Settings](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/account)
- [ADLS Credential Passthrough](https://learn.microsoft.com/en-us/azure/databricks/security/credential-passthrough/adls-passthrough)
- [Unity Catalog](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/)
- [Delta Lake](https://learn.microsoft.com/en-us/azure/databricks/delta/)

### Azure Synapse Analytics
- [Azure Synapse Analytics Overview](https://learn.microsoft.com/en-us/azure/synapse-analytics/overview-what-is)
- [Dedicated SQL Pools](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-overview-what-is)

### Microsoft Fabric
- [Microsoft Fabric Overview](https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview)
- [OneLake Documentation](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)

---

**Last Updated**: December 2025  
**Document Version**: 2.0
