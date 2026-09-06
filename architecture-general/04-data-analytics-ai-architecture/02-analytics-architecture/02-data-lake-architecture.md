---
type: Architecture Pattern
title: "Data Lake Architecture"
description: "A Data Lake is a centralized repository that stores **raw data in its native format** at any scale. Unlike a data warehouse that requires structured, transformed data, a data lake embraces the **sc..."
tags: [data-analytics-ai-architecture, analytics-architecture]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Data Lake Architecture

> **Taxonomy Reference**: §4.2 Analytics Architecture

## Overview

A Data Lake is a centralized repository that stores **raw data in its native format** at any scale. Unlike a data warehouse that requires structured, transformed data, a data lake embraces the **schema-on-read** paradigm — data is stored first, and structure is applied when it's read for analysis.

## Table of Contents

- [Core Principles](#core-principles)
- [Schema-on-Read vs Schema-on-Write](#schema-on-read-vs-schema-on-write)
- [Medallion Architecture](#medallion-architecture)
- [Architecture Diagram](#architecture-diagram)
- [Data Organization](#data-organization)
- [Governance & Catalog](#governance-catalog)
- [Lake vs Warehouse vs Lakehouse](#lake-vs-warehouse-vs-lakehouse)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Schema-on-Read** | Structure applied at query time, not at ingest |
| **Store Everything** | Raw data preserved indefinitely |
| **Multi-Protocol** | Batch, streaming, and interactive from same storage |
| **Open Formats** | Parquet, ORC, Avro, Iceberg — avoid vendor lock-in |
| **Separation of Compute & Storage** | Scale storage and compute independently |
| **Single Copy of Data** | No proliferation of data copies |

## Schema-on-Read vs Schema-on-Write

```mermaid
graph LR
    subgraph "Schema-on-Write (DW)"
        S1[Raw Data] -->|ETL| T1[Transform<br/>to Schema]
        T1 -->|Load| D1[(Structured<br/>Tables)]
    end

    subgraph "Schema-on-Read (Data Lake)"
        S2[Raw Data] -->|Store| D2[(Raw Files<br/>Parquet, JSON)]
        D2 -->|Query Time| T2[Apply Schema]
    end

    style D1 fill:#ff6b6b,color:#fff
    style D2 fill:#4ecdc4,color:#fff
```

| Dimension | Schema-on-Write | Schema-on-Read |
|-----------|----------------|----------------|
| **Agility** | Schema changes require reload | Schema evolves freely |
| **Query speed** | Fast (pre-optimized) | Slower (parse at query time) |
| **Storage format** | Proprietary / optimized | Open formats (Parquet, ORC) |
| **Data retention** | Often summarized | Full history retained |
| **Data science** | Requires ETL for exploration | Direct access to raw data |
| **Governance** | Enforced at ingest | Enforced at query |

## Medallion Architecture

The **medallion architecture** (Bronze → Silver → Gold) is the modern standard for organizing data lakes:

```mermaid
graph TB
    subgraph "Medallion Architecture"
        subgraph "Bronze (Raw)"
            B1[Raw Ingestion]
            B2[Append-Only]
            B3[Original Format]
            B1 --> B2 --> B3
        end

        subgraph "Silver (Curated)"
            S1[Cleansed]
            S2[Conformed]
            S3[Deduplicated]
            B3 --> S1
            S1 --> S2
            S2 --> S3
        end

        subgraph "Gold (Business)"
            G1[Aggregated Views]
            G2[Feature Tables]
            G3[Business KPIs]
            S3 --> G1
            S3 --> G2
            S3 --> G3
        end

        subgraph "Consumption"
            BI[BI / Reporting]
            DS[Data Science]
            ML[ML Training]
            API[Data APIs]
        end

        G1 --> BI
        G2 --> DS
        G2 --> ML
        G3 --> API
    end

    style B3 fill:#cd7f32,color:#fff
    style S3 fill:#c0c0c0,color:#000
    style G3 fill:#ffd700,color:#000
```

### Zone Characteristics

| Zone | Purpose | Data Shape | Access Pattern | Retention |
|------|---------|------------|----------------|-----------|
| **Bronze** | Landing zone, full fidelity | Raw (JSON, CSV, binary) | Append-only | Forever (immutable) |
| **Silver** | Cleaned, validated, joined | Parquet/ORC with schema | Read-heavy, incremental | Policy-based |
| **Gold** | Business-ready aggregates | Star schemas, flat tables | High read concurrency | Rolling window |

## Architecture Diagram

```mermaid
graph TB
    subgraph "Enterprise Data Lake Architecture"
        subgraph "Ingestion Layer"
            BATCH["Batch<br/>Files, DB Dumps"]
            STREAM["Streaming<br/>Kafka, Kinesis"]
            CDC["CDC<br/>Debezium"]
            API_GW[API Gateway]
        end

        subgraph "Storage Layer"
            LANDING[(Landing Zone)]
            BRONZE[(Bronze<br/>Raw Data)]
            SILVER[(Silver<br/>Curated Data)]
            GOLD[(Gold<br/>Business Layer)]

            LANDING --> BRONZE
            BRONZE --> SILVER
            SILVER --> GOLD
        end

        subgraph "Catalog & Governance"
            CATALOG[Data Catalog]
            LINEAGE[Data Lineage]
            GOV[Access Control]
            QUALITY[Data Quality]
        end

        subgraph "Compute & Processing"
            SPARK[Spark / Flink]
            SQL[SQL Engine<br/>Trino, Presto]
            PYTHON[Python / R]
        end

        subgraph "Serving Layer"
            BI[BI / Dashboards]
            NOTEBOOK[Notebooks]
            ML[ML Pipelines]
            API_SRV[Data Service API]
        end

        BATCH --> LANDING
        STREAM --> LANDING
        CDC --> LANDING
        API_GW --> LANDING

        SPARK --> BRONZE
        SPARK --> SILVER
        SQL --> GOLD
        PYTHON --> SILVER
        PYTHON --> GOLD

        GOLD --> BI
        GOLD --> NOTEBOOK
        SILVER --> ML
        GOLD --> API_SRV
    end

    style BRONZE fill:#cd7f32,color:#fff
    style SILVER fill:#c0c0c0,color:#000
    style GOLD fill:#ffd700,color:#000
```

## Data Organization

### File Formats

| Format | Type | Compression | Schema | Query Pushdown |
|--------|------|-------------|--------|----------------|
| **Parquet** | Columnar | Snappy, Gzip, Zstd | Embedded | Column, predicate, partition |
| **ORC** | Columnar | Zlib, Snappy, LZO | Embedded | Column, predicate |
| **Avro** | Row-based | Deflate, Snappy | Embedded | None (row-based) |
| **JSON** | Row-based | Gzip | None | None |
| **Delta Lake** | Columnar + Log | Parquet + JSON | Embedded + Schema evolution | Full (with transaction log) |
| **Iceberg** | Columnar + Metadata | Parquet/ORC/Avro | Embedded + Schema evolution | Full (with metadata layer) |

### Partitioning Strategies

```
Recommended: s3://data-lake/silver/sales/
├── year=2024/
│   ├── month=01/
│   │   ├── region=eu/
│   │   └── region=us/
│   └── month=02/
│       └── ...
└── year=2025/
    └── ...
```

| Strategy | Good For | Anti-Pattern |
|----------|----------|--------------|
| **Date-based** | Time-series, logs | High-cardinality partition keys |
| **Geographic** | Regional analytics | Too many small files |
| **Category** | Balanced distribution | Skewed categories |
| **Hash** | Uniform distribution | Hard to query by value |

## Governance & Catalog

### Data Catalog

A catalog is essential for data lake success — without it, the lake becomes a **data swamp**:

```
Catalog Metadata per Dataset:
├── Schema (columns, types)
├── Lineage (upstream sources, downstream consumers)
├── Statistics (row count, size, partition info)
├── Ownership (team, contact)
├── Classification (PII, sensitivity)
├── Quality metrics (completeness, freshness)
└── Tags (domain, use case, retention policy)
```

### Preventing the Data Swamp

| Anti-Pattern | Solution |
|-------------|----------|
| No schema enforcement | Use Delta Lake / Iceberg for schema evolution |
| No ownership | Assign data stewards per domain |
| No quality checks | Great Expectations, dbt tests |
| No catalog | Implement data catalog (Unity, Purview, Amundsen) |
| No retention policy | Define TTL and archival per zone |
| No access control | Row/column-level security, RBAC |

## Lake vs Warehouse vs Lakehouse

| Dimension | Data Warehouse | Data Lake | Lakehouse |
|-----------|---------------|-----------|-----------|
| **Schema** | Schema-on-write | Schema-on-read | Schema-on-read + enforcement |
| **ACID** | Full ACID | No ACID | ACID via Delta/Iceberg |
| **Data types** | Structured only | All (structured, semi, unstructured) | All |
| **BI speed** | Fast | Slow (needs compute) | Fast (with optimizations) |
| **ML/DS** | Limited | Excellent | Excellent |
| **Cost** | High ($/TB) | Low ($/TB) | Medium |
| **Governance** | Built-in | Add-on required | Built-in |
| **Open format** | Proprietary | Parquet, ORC | Delta, Iceberg, Hudi |

> **Predecessor & Successor**: Data lakes preceded the [Lakehouse Architecture](03-lakehouse-architecture.md), which addresses their ACID and governance shortcomings.

## Decision Framework

```mermaid
graph TD
    Q1{Data variety?} -->|Structured only| DW[Data Warehouse]
    Q1 -->|Semi/unstructured| Q2{Need ACID on lake?}
    Q2 -->|Yes| LAKEHOUSE[Lakehouse<br/>Delta/Iceberg]
    Q2 -->|No| Q3{Have catalog/governance?}
    Q3 -->|Yes| LAKE[Data Lake]
    Q3 -->|No| LAKEWARN["Data Lake +<br/>Invest in governance FIRST"]

    style LAKEHOUSE fill:#4ecdc4,color:#fff
    style LAKE fill:#45b7d1,color:#fff
    style DW fill:#ff6b6b,color:#fff
```

## Related Patterns

- [Data Warehouse Architecture](01-data-warehouse-architecture.md) — Schema-on-write counterpart
- [Lakehouse Architecture](03-lakehouse-architecture.md) — ACID-enabled lake evolution
- [Lambda Architecture](04-lambda-architecture.md) — Batch + streaming over data lake
- [Kappa Architecture](05-kappa-architecture.md) — Stream-only over event log
- [Data Virtualization](../01-data-architecture/04-data-virtualization.md) — Query-time federation without copy

> **Azure Implementation**: See [Azure Data Lake Storage (ADLS) Gen2](../../../architecture-azure/data/storage/), [Microsoft Fabric Lakehouse](../../../architecture-azure/data/), and [Azure Purview](../../../architecture-azure/governance/) for data governance.
