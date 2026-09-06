---
type: Architecture Pattern
title: "Feature Store Architecture"
description: "A Feature Store is a centralized platform for **defining, storing, serving, and governing ML features**. It bridges the gap between data engineering and ML by ensuring feature consistency across tr..."
tags: [data-analytics-ai-architecture, ai-ml-architecture]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Feature Store Architecture

> **Taxonomy Reference**: §4.4 AI / ML Architecture

## Overview

A Feature Store is a centralized platform for **defining, storing, serving, and governing ML features**. It bridges the gap between data engineering and ML by ensuring feature consistency across training and inference — eliminating training-serving skew and enabling feature reuse across teams.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Architecture Diagram](#architecture-diagram)
- [Offline vs Online Store](#offline-vs-online-store)
- [Feature Engineering Pipeline](#feature-engineering-pipeline)
- [Point-in-Time Correctness](#point-in-time-correctness)
- [Training-Serving Skew](#training-serving-skew)
- [Feature Store Platforms](#feature-store-platforms)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Feature** | A measurable property used as ML model input (e.g., `user_avg_spend_7d`) |
| **Feature Group** | Logical grouping of related features (e.g., `user_features`, `product_features`) |
| **Feature View** | A query-ready combination of features from multiple groups |
| **Offline Store** | Historical feature data for training (data lake/warehouse) |
| **Online Store** | Low-latency feature values for real-time inference (KV store) |
| **Feature Registry** | Catalog of all features: definitions, ownership, lineage, statistics |

## Architecture Diagram

```mermaid
graph TB
    subgraph "Feature Store Architecture"
        subgraph "Data Sources"
            DW[(Data<br/>Warehouse)]
            STREAM[Streaming<br/>Events]
            FILES[Files / APIs]
        end

        subgraph "Feature Engineering"
            BATCH_FEAT[Batch Feature<br/>Computation<br/>Spark / dbt]
            STREAM_FEAT[Streaming Feature<br/>Computation<br/>Flink / Kafka Streams]
            DW --> BATCH_FEAT
            STREAM --> STREAM_FEAT
            FILES --> BATCH_FEAT
        end

        subgraph "Feature Store"
            REGISTRY[(Feature<br/>Registry)]
            OFFLINE[(Offline Store<br/>Data Lake)]
            ONLINE[(Online Store<br/>Redis / DynamoDB)]

            BATCH_FEAT --> OFFLINE
            STREAM_FEAT --> ONLINE
            BATCH_FEAT --> ONLINE

            REGISTRY --- OFFLINE
            REGISTRY --- ONLINE
        end

        subgraph "Consumption"
            TRAIN[Training<br/>Pipeline]
            BATCH_PRED[Batch<br/>Inference]
            REALTIME_PRED[Real-Time<br/>Inference]
            OFFLINE --> TRAIN
            OFFLINE --> BATCH_PRED
            ONLINE --> REALTIME_PRED
        end
    end

    style REGISTRY fill:#ff6b6b,color:#fff
    style OFFLINE fill:#4ecdc4,color:#fff
    style ONLINE fill:#45b7d1,color:#fff
```

## Offline vs Online Store

```mermaid
graph LR
    subgraph "Dual-Store Architecture"
        subgraph "Offline Store"
            direction TB
            O1[Historical Features<br/>Months/Years]
            O2[Point-in-Time Joins]
            O3[Training Dataset<br/>Generation]
            O4[(Data Lake /<br/>Parquet / Delta)]
            O1 --> O2 --> O3 --> O4
        end

        subgraph "Online Store"
            direction TB
            N1[Latest Feature Values<br/>Real-Time]
            N2[Low-Latency Reads<br/>< 10ms]
            N3[Feature Serving<br/>API]
            N4[(Redis / DynamoDB)]
            N1 --> N2 --> N3 --> N4
        end

        subgraph "Synchronization"
            SYNC[Materialize<br/>batch features<br/>to online store]
            O4 -.-> SYNC
            SYNC -.-> N4
        end
    end

    style O4 fill:#4ecdc4,color:#fff
    style N4 fill:#45b7d1,color:#fff
```

| Dimension | Offline Store | Online Store |
|-----------|--------------|--------------|
| **Purpose** | Training, batch inference | Real-time inference |
| **Data** | Full history (months/years) | Latest values only |
| **Latency** | Seconds (Spark queries) | Milliseconds (KV lookup) |
| **Storage** | Data lake (Parquet/Delta) | Redis, DynamoDB, Cassandra |
| **Scale** | TB-PB | GB (latest values) |
| **Consistency** | Point-in-time snapshot | Eventually consistent |
| **Query** | Point-in-time join | Key lookup by entity ID |

## Feature Engineering Pipeline

```python
# Feature definition (conceptual)
@feature(
    name="user_avg_spend_7d",
    entity="user",
    description="Average spend per transaction over last 7 days",
    owner="growth-team",
    freshness="1 hour"
)
def user_avg_spend_7d(transactions: DataFrame) -> DataFrame:
    return (
        transactions
        .filter(col("timestamp") > window(7, "days"))
        .groupBy("user_id")
        .agg(avg("amount").alias("user_avg_spend_7d"))
    )
```

### Feature Types

| Type | Example | Refresh | Computation |
|------|---------|---------|-------------|
| **Static** | `user_country`, `product_category` | Rarely/never | Direct from source |
| **Slowly Changing** | `user_segment`, `user_lifetime_value` | Daily | Batch (Spark/dbt) |
| **Real-Time** | `clicks_last_5min`, `session_page_count` | Continuous | Streaming (Flink) |
| **Derived** | `spend_to_lifetime_ratio` | Same as parents | Post-computation |

## Point-in-Time Correctness

The most critical feature store capability is **point-in-time joins** — ensuring training data doesn't leak future information:

```mermaid
gantt
    title Point-in-Time Join
    dateFormat  YYYY-MM-DD
    axisFormat %b %d

    section User Features
    Feature V1 (value=100) :f1, 2024-01-01, 2024-01-10
    Feature V2 (value=150) :f2, 2024-01-10, 2024-01-20

    section Transactions
    Txn A (2024-01-05)     :milestone, t1, 2024-01-05, 0d
    Txn B (2024-01-15)     :milestone, t2, 2024-01-15, 0d
```

| Transaction | Correct Feature Value | Why |
|-------------|----------------------|-----|
| **Txn A (Jan 5)** | `value=100` (V1) | V1 was active on Jan 5 |
| **Txn B (Jan 15)** | `value=150` (V2) | V2 was active on Jan 15 |

### Leak Example (Wrong)

```
❌ Without PIT correctness:
   Just join latest feature value → ALL transactions get value=150
   → Txn A sees future data → Data Leak → Overly optimistic training metrics
```

## Training-Serving Skew

| Skew Type | Example | Prevention |
|-----------|---------|------------|
| **Feature Definition** | Training uses `log(amount+1)`, inference uses `log(amount)` | Feature Store enforces single definition |
| **Data Distribution** | Training data from US, inference data from EU | Monitor feature distributions per region |
| **Feature Freshness** | Training on daily batch, inference expects real-time | Align feature computation SLAs |
| **Missing Values** | Training imputes with mean, inference gets NULL | Consistent imputation registered in Feature Store |

## Feature Store Platforms

| Platform | Type | Offline | Online | Strengths |
|----------|------|---------|--------|-----------|
| **Feast** | Open-source | Parquet, BigQuery, Snowflake | Redis, DynamoDB, BigTable | Lightweight, cloud-agnostic, PIT joins |
| **Tecton** | Managed | Data warehouse | DynamoDB, Redis | Enterprise, streaming features, monitoring |
| **Databricks Feature Store** | Managed | Delta Lake | DynamoDB, RDS, Cassandra | Native Databricks integration |
| **SageMaker Feature Store** | Managed (AWS) | S3 (Parquet) | DynamoDB | AWS-native, integrated with SageMaker |
| **Vertex AI Feature Store** | Managed (GCP) | BigQuery | Bigtable | GCP-native, integrated with Vertex AI |

## Decision Framework

```mermaid
graph TD
    Q1{Number of ML models?} -->|< 3| Q2{Training-serving skew<br/>a problem?}
    Q1 -->|3-10| Q3{Team using Databricks?}
    Q1 -->|10+| Q4{Cloud strategy?}

    Q2 -->|No| NOFS[No Feature Store yet.<br/>Manual feature engineering OK]
    Q2 -->|Yes| FEAST[Feast<br/>Open-source]

    Q3 -->|Yes| DB_FS[Databricks Feature Store]
    Q3 -->|No| Q5{Need managed solution?}

    Q4 -->|AWS| SAGEMAKER[SageMaker Feature Store]
    Q4 -->|GCP| VERTEX[Vertex AI Feature Store]
    Q4 -->|Multi-cloud| TECTON[Tecton / Feast]

    Q5 -->|Yes| TECTON2[Tecton]
    Q5 -->|No| FEAST2[Feast]

    style FEAST fill:#4ecdc4,color:#fff
    style TECTON fill:#45b7d1,color:#fff
```

## Related Patterns

- [Machine Learning Pipeline Architecture](01-machine-learning-pipeline-architecture.md) — Where Feature Store fits in the pipeline
- [MLOps Architecture](02-mlops-architecture.md) — Governance and monitoring integration
- [Model Training Architecture](04-model-training-architecture.md) — Training data generation from Feature Store
- [Model Inference Architecture](05-model-inference-architecture.md) — Real-time feature serving

> **Azure Implementation**: See [Azure Machine Learning Managed Feature Store](https://learn.microsoft.com/en-us/azure/machine-learning/concept-what-is-feature-store), [Azure Redis Cache](../../../architecture-azure/data/redis/) (online store), and [Azure Data Lake Storage](../../../architecture-azure/data/storage/) (offline store).
