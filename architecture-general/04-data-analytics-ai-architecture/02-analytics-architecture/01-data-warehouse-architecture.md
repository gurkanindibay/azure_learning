---
type: Architecture Pattern
title: "Data Warehouse Architecture"
description: "A Data Warehouse (DW) is a centralized repository designed for analytical querying and reporting. It consolidates data from multiple operational sources, transforms it into a consistent format, and..."
tags: [data-analytics-ai-architecture, analytics-architecture]
timestamp: 2026-06-14T00:00:00Z
---

# Data Warehouse Architecture

> **Taxonomy Reference**: §4.2 Analytics Architecture

## Overview

A Data Warehouse (DW) is a centralized repository designed for analytical querying and reporting. It consolidates data from multiple operational sources, transforms it into a consistent format, and optimizes it for complex queries — serving as the "single source of truth" for enterprise analytics.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Architecture Diagram](#architecture-diagram)
- [ETL vs ELT](#etl-vs-elt)
- [Schema Design Approaches](#schema-design-approaches)
- [Kimball vs Inmon](#kimball-vs-inmon)
- [Data Mart Strategy](#data-mart-strategy)
- [Modern Warehouse Architecture](#modern-warehouse-architecture)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Concepts

### The Data Warehouse Value Chain

```
Operational Systems  →  Staging  →  Integration  →  Presentation  →  Consumption
     (OLTP)              (Raw)       (Transform)      (Star Schema)     (BI / ML)
```

| Layer | Purpose | Characteristics |
|-------|---------|-----------------|
| **Staging** | Land raw data as-is | Transient, schema-flexible |
| **Integration** | Clean, conform, deduplicate | Normalized (3NF) or Data Vault |
| **Presentation** | Business-friendly structures | Star/snowflake schemas, aggregates |
| **Consumption** | BI, reports, ML, ad-hoc | Semantic layer, cubes, APIs |

## Architecture Diagram

```mermaid
graph TB
    subgraph "Enterprise Data Warehouse Architecture"
        subgraph "Data Sources"
            S1[(ERP System)]
            S2[(CRM System)]
            S3[(Web / Mobile)]
            S4[(IoT / Sensors)]
            S5[3rd Party APIs]
        end

        subgraph "Staging Area"
            STG[Raw Staging<br/>Landing Zone]
        end

        subgraph "Integration Layer"
            CLEAN[Data Cleansing]
            CONF[Data Conformance]
            DEDUP[Deduplication]
            MDM[Master Data<br/>Management]
            STG --> CLEAN
            CLEAN --> CONF
            CONF --> DEDUP
            DEDUP --> MDM
        end

        subgraph "Presentation Layer"
            DW[(Enterprise<br/>Data Warehouse)]
            DM[Data Marts]
            DW --> DM
        end

        subgraph "Consumption"
            BI[BI Dashboards]
            REPORT[Reports]
            ADHOC[Ad-Hoc SQL]
            ML[ML Pipelines]
            API[Data APIs]
        end

        S1 --> STG
        S2 --> STG
        S3 --> STG
        S4 --> STG
        S5 --> STG

        MDM --> DW
        DM --> BI
        DM --> REPORT
        DM --> ADHOC
        DM --> ML
        DM --> API
    end

    style DW fill:#ff6b6b,color:#fff
    style STG fill:#4ecdc4,color:#fff
    style BI fill:#45b7d1,color:#fff
```

## ETL vs ELT

### ETL (Extract → Transform → Load)

```mermaid
graph LR
    SRC[(Source)] -->|Extract| TRANS[Transform<br/>Engine]
    TRANS -->|Load| DW[(Data<br/>Warehouse)]
```

| Characteristic | ETL |
|---------------|-----|
| **Where transform?** | Before loading into DW |
| **DW content** | Clean, transformed data only |
| **Best for** | On-prem, structured data, compliance |
| **Tool examples** | Informatica, SSIS, Talend, DataStage |

### ELT (Extract → Load → Transform)

```mermaid
graph LR
    SRC[(Source)] -->|Extract| DW[(Data<br/>Warehouse)]
    DW -->|Transform<br/>(in-DB)| RESULT[(Transformed<br/>Views)]
```

| Characteristic | ELT |
|---------------|-----|
| **Where transform?** | Inside the DW (using its compute) |
| **DW content** | Raw + transformed data |
| **Best for** | Cloud DWs (Snowflake, BigQuery, Synapse) |
| **Tool examples** | dbt, Dataform, custom SQL |

### Comparison

| Dimension | ETL | ELT |
|-----------|-----|-----|
| **Data retention** | DW has only transformed data | DW has raw + transformed |
| **Flexibility** | New transforms require re-extract | Re-transform raw data in-place |
| **Compute** | External ETL server | Uses DW compute power |
| **Compliance** | Easier (raw data never leaves source) | Raw data in cloud |
| **Performance** | Less load on DW | Leverages cloud DW scale |

## Schema Design Approaches

For detailed schema design (star/snowflake, SCD types), see [OLAP Architecture](../01-data-architecture/02-olap-architecture.md).

## Kimball vs Inmon

```mermaid
graph TB
    subgraph "Kimball (Bottom-Up)"
        direction TB
        K1[Source Systems]
        K2[Staging]
        K3["Data Marts<br/>(Star Schemas)"]
        K4["Conformed Dimensions<br/>(Bus Architecture)"]
        K1 --> K2 --> K3 --> K4
    end

    subgraph "Inmon (Top-Down)"
        direction TB
        I1[Source Systems]
        I2[Staging]
        I3["Enterprise DW<br/>(Normalized 3NF)"]
        I4["Data Marts<br/>(Dependent)"]
        I1 --> I2 --> I3 --> I4
    end

    style K4 fill:#4ecdc4,color:#fff
    style I3 fill:#ff6b6b,color:#fff
```

| Dimension | Kimball | Inmon |
|-----------|---------|-------|
| **Philosophy** | Bottom-up: Start with data marts | Top-down: Build enterprise DW first |
| **Schema** | Dimensional (star/snowflake) | Normalized (3NF) |
| **Time to value** | Fast (department-level marts) | Slow (enterprise model first) |
| **Complexity** | Lower initial complexity | Higher upfront investment |
| **Governance** | Federated (dept ownership) | Centralized (enterprise ownership) |
| **Best for** | Agile orgs, quick wins | Regulated industries, single source |
| **Integration** | Conformed dimensions (bus) | CIF (Corporate Information Factory) |

### The Real-World Answer

Most organizations adopt a **hybrid approach**: use Kimball dimensional modeling within an Inmon-style enterprise architecture. Modern tools like dbt make this practical.

## Data Mart Strategy

| Type | Description | Pros | Cons |
|------|-------------|------|------|
| **Dependent** | Sourced from enterprise DW | Single source of truth | Requires DW first |
| **Independent** | Direct from operational sources | Fast to build | Data silos, inconsistency |
| **Hybrid** | Some from DW, some direct | Flexible | Governance complexity |

## Modern Warehouse Architecture

```mermaid
graph TB
    subgraph "Modern Cloud DW Architecture"
        subgraph "Ingest"
            BATCH[Batch ETL/ELT]
            STREAM[Streaming Ingest]
            CDC[Change Data Capture]
        end

        subgraph "Storage"
            RAW[(Raw / Bronze)]
            CURATED[(Curated / Silver)]
            PRES[(Presentation / Gold)]
            RAW --> CURATED --> PRES
        end

        subgraph "Compute"
            MPP[MPP Query Engine]
            SERVERLESS[Serverless Compute]
        end

        subgraph "Serving"
            BI[BI Tools]
            NOTEBOOK[Notebooks]
            API[Data API]
            ML[ML Training]
        end

        BATCH --> RAW
        STREAM --> RAW
        CDC --> RAW
        PRES --> MPP
        PRES --> SERVERLESS
        MPP --> BI
        MPP --> NOTEBOOK
        SERVERLESS --> API
        SERVERLESS --> ML
    end

    style RAW fill:#cd7f32,color:#fff
    style CURATED fill:#c0c0c0,color:#000
    style PRES fill:#ffd700,color:#000
```

> **Note**: The bronze/silver/gold naming (medallion architecture) originates from the data lake pattern but is now commonly adopted in modern cloud warehouses as well. See [Data Lake Architecture](02-data-lake-architecture.md) for the origin.

## Decision Framework

```mermaid
graph TD
    Q1{Data volume?} -->|< 100GB| Q2{Need real-time?}
    Q1 -->|100GB - 10TB| Q3{Existing DW?}
    Q1 -->|> 10TB| Q4{Query concurrency?}

    Q2 -->|No| SIMPLE[Simple RDBMS<br/>with views]
    Q2 -->|Yes| Q5{Stream native?}

    Q3 -->|Yes| MIGRATE[Migrate to<br/>Cloud DW]
    Q3 -->|No| KIMBALL[Kimball DW<br/>Agile approach]

    Q4 -->|High| CLOUDDW[Cloud MPP<br/>Snowflake, Synapse]
    Q4 -->|Low| LAKEHOUSE[Lakehouse<br/>Alternative]

    Q5 -->|Yes| KAPPA[Kappa Architecture]
    Q5 -->|No| LAMBDA[Lambda Architecture]

    style Q1 fill:#ff6b6b,color:#fff
    style CLOUDDW fill:#4ecdc4,color:#fff
    style LAKEHOUSE fill:#45b7d1,color:#fff
```

## Related Patterns

- [OLAP Architecture](../01-data-architecture/02-olap-architecture.md) — Dimensional modeling deep-dive
- [Data Lake Architecture](02-data-lake-architecture.md) — Schema-on-read alternative
- [Lakehouse Architecture](03-lakehouse-architecture.md) — Convergence of lake and warehouse
- [Lambda Architecture](04-lambda-architecture.md) — Batch + real-time big data
- [Kappa Architecture](05-kappa-architecture.md) — Stream-only approach

> **Azure Implementation**: See [Azure Synapse Analytics](../../../architecture-azure/data/) (MPP DW), [Microsoft Fabric](../../../architecture-azure/data/) (unified analytics), and [Azure Data Factory](../../../architecture-azure/data/data-factory/) (ETL/ELT orchestration).
