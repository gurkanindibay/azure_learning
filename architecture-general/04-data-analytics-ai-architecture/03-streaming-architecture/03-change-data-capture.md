---
type: Architecture Pattern
title: "Change Data Capture (CDC)"
description: "Change Data Capture (CDC) is a pattern for **detecting and propagating data changes** from a source database to downstream systems in near real-time. Instead of periodic bulk extracts, CDC captures..."
tags: [data-analytics-ai-architecture, streaming-architecture]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Change Data Capture (CDC)

> **Taxonomy Reference**: §4.3 Streaming & Real-Time Architecture

## Overview

Change Data Capture (CDC) is a pattern for **detecting and propagating data changes** from a source database to downstream systems in near real-time. Instead of periodic bulk extracts, CDC captures row-level insert, update, and delete operations as they occur, enabling event-driven data pipelines.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Architecture Diagram](#architecture-diagram)
- [CDC Approaches](#cdc-approaches)
- [CDC Pipeline Flow](#cdc-pipeline-flow)
- [Pattern: Outbox Pattern](#pattern-outbox-pattern)
- [CDC with Event Sourcing](#cdc-with-event-sourcing)
- [Challenges & Mitigations](#challenges-mitigations)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Concepts

```
Traditional ETL:                      CDC:
┌─────────┐    ┌─────────┐           ┌─────────┐
│ Source  │───→│ Target  │           │ Source  │──→ [INSERT] new row
│  DB     │    │  DB     │           │  DB     │──→ [UPDATE] row modified
└─────────┘    └─────────┘           │         │──→ [DELETE] row removed
                                     └─────────┘
  "Give me everything"              "Tell me what changed"
  Periodic full load                  Continuous, incremental
  Latency: hours                      Latency: seconds
```

## Architecture Diagram

```mermaid
graph TB
    subgraph "CDC Architecture"
        subgraph "Source Database"
            DB[(PostgreSQL /<br/>MySQL / SQL Server)]
            WAL[Write-Ahead Log<br/>/ Binary Log]
            DB --> WAL
        end

        subgraph "CDC Connector"
            READER[Log Reader<br/>Debezium / AWS DMS]
            TRANSFORM[Transform &<br/>Serialize]
            WAL --> READER
            READER --> TRANSFORM
        end

        subgraph "Event Backbone"
            KAFKA[Apache Kafka<br/>CDC Events]
            TRANSFORM --> KAFKA
        end

        subgraph "Downstream Consumers"
            SEARCH[Search Index<br/>Elasticsearch]
            CACHE[Cache<br/>Invalidation]
            DW[(Data<br/>Warehouse)]
            REPLICA[(Read<br/>Replica)]
            ANALYTICS[(Analytics<br/>Lakehouse)]
            STREAM[Stream<br/>Processing]
            NOTIFY[Real-Time<br/>Notifications]
        end

        KAFKA --> SEARCH
        KAFKA --> CACHE
        KAFKA --> DW
        KAFKA --> REPLICA
        KAFKA --> ANALYTICS
        KAFKA --> STREAM
        KAFKA --> NOTIFY
    end

    style DB fill:#ff6b6b,color:#fff
    style KAFKA fill:#4ecdc4,color:#fff
    style READER fill:#45b7d1,color:#fff
```

## CDC Approaches

### Comparison

| Approach | How It Works | Overhead | Latency | Completeness |
|----------|-------------|----------|---------|--------------|
| **Log-Based** | Read database transaction log (WAL/binlog) | Very low | ms | Complete (all changes) |
| **Trigger-Based** | DB triggers on tables write to shadow table | High | ms | Complete |
| **Query-Based (Polling)** | Periodically query with `updated_at > last_run` | Medium | Minutes | Missing intermediate states |
| **Timestamp/Version Column** | Query by `version` or `last_modified` | Medium | Minutes | Misses deletes (soft-delete only) |

### Log-Based CDC (Recommended)

```mermaid
sequenceDiagram
    participant Client as Application
    participant DB as PostgreSQL
    participant WAL as Write-Ahead Log
    participant Debezium as Debezium Connector
    participant Kafka as Kafka
    participant Consumer as Downstream

    Client->>DB: INSERT INTO orders VALUES (...)
    Client->>DB: UPDATE orders SET status='shipped'
    Client->>DB: DELETE FROM orders WHERE id=123

    Note over DB: All changes logged in WAL

    Debezium->>WAL: Read WAL (streaming replication slot)
    WAL-->>Debezium: INSERT event
    WAL-->>Debezium: UPDATE event (before + after)
    WAL-->>Debezium: DELETE event (before image)

    Debezium->>Kafka: Publish to topic "db.orders"
    Kafka-->>Consumer: Consume CDC events
    Consumer->>Consumer: Update search index, cache, data warehouse...
```

### CDC Event Structure

```json
{
  "before": null,
  "after": {
    "id": 1001,
    "customer_id": 42,
    "amount": 99.99,
    "status": "created",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "source": {
    "version": "2.5.0",
    "connector": "postgresql",
    "name": "orders_db",
    "ts_ms": 1705312200000,
    "snapshot": "false",
    "db": "ecommerce",
    "schema": "public",
    "table": "orders",
    "txId": 5678,
    "lsn": 24023128
  },
  "op": "c",           // c=create, u=update, d=delete, r=read (snapshot)
  "ts_ms": 1705312200500
}
```

## CDC Pipeline Flow

```mermaid
graph LR
    subgraph "CDC Pipeline Stages"
        A[Initial<br/>Snapshot] --> B[Streaming<br/>Changes]
        B --> C[Transform<br/>& Route]
        C --> D[Schema<br/>Evolution]
        D --> E[Downstream<br/>Sinks]
    end

    subgraph "Initial Snapshot"
        A1[Lock tables briefly<br/>Read all rows<br/>Release lock]
    end

    subgraph "Ongoing"
        B1[Read WAL/binlog<br/>continuously from<br/>snapshot LSN]
    end

    A -.-> A1
    B -.-> B1

    style A fill:#ff6b6b,color:#fff
    style B fill:#4ecdc4,color:#fff
```

### Schema Evolution

When source schema changes, CDC must handle it gracefully:

```yaml
# Debezium schema change event
{
  "source": { "table": "orders", ... },
  "databaseName": "ecommerce",
  "schemaName": "public",
  "ddl": "ALTER TABLE orders ADD COLUMN discount DECIMAL(5,2)",
  "tableChanges": [...]
}
```

| Schema Change | CDC Behavior | Consumer Action |
|---------------|--------------|-----------------|
| **ADD COLUMN** | New field in after-image | Schema registry updates, consumer adapts |
| **DROP COLUMN** | Field absent from new events | Consumer handles null/missing gracefully |
| **ALTER TYPE** | May break serialization | Requires consumer migration |
| **RENAME TABLE** | New topic (or reconfiguration) | Route to appropriate sink |

## Pattern: Outbox Pattern

When using CDC with microservices, the **Outbox Pattern** ensures reliable event publication:

```mermaid
sequenceDiagram
    participant Service as Order Service
    participant DB as PostgreSQL
    participant CDC as Debezium
    participant Kafka as Kafka

    Note over Service,DB: Transaction boundary
    Service->>DB: BEGIN
    Service->>DB: INSERT INTO orders VALUES (...)
    Service->>DB: INSERT INTO outbox (event_type, payload) VALUES ('OrderCreated', '{...}')
    Service->>DB: COMMIT

    Note over CDC,Kafka: Async (decoupled)
    CDC->>DB: Read WAL → detects outbox table change
    CDC->>Kafka: Publish "OrderCreated" event
```

| Aspect | Outbox Pattern | Direct Kafka Publish |
|--------|---------------|---------------------|
| **Consistency** | Guaranteed (same transaction) | Possible inconsistency (dual-write problem) |
| **Complexity** | Higher (outbox table + cleanup) | Lower |
| **Reliability** | High (CDC guarantees delivery) | Medium (network can fail between DB and Kafka) |
| **Latency** | Slightly higher (CDC polling) | Lower |

## CDC with Event Sourcing

CDC complements the Event Sourcing pattern:

| Pattern | CDC Role |
|---------|----------|
| **CQRS Read Model** | Project writes → optimized read models |
| **Search Index Sync** | Keep Elasticsearch in sync with primary DB |
| **Cache Invalidation** | Publish cache invalidation events on data change |
| **Data Warehouse ETL** | Feed DW incrementally instead of bulk loads |
| **Audit Logging** | Capture every change for compliance |
| **Multi-Region Replication** | Replicate changes across regions |

## Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| **Schema changes break consumers** | Schema registry (Avro/Protobuf), backward-compatible changes |
| **High WAL retention** | Auto-cleanup, monitor replication slot lag |
| **Initial snapshot impact** | Use read replicas, off-peak snapshot |
| **Large transactions** | Debezium chunks large txns, monitor for lag |
| **DDL changes** | Schema change events, consumer compatibility checks |
| **Topic proliferation** | Topic routing strategies, logical replication |
| **Missing deletes (query-based)** | Use log-based CDC, or soft-delete pattern |

## Decision Framework

```mermaid
graph TD
    Q1{Source DB supports<br/>log-based CDC?} -->|Yes| Q2{Can add Kafka/event<br/>infrastructure?}
    Q1 -->|No| Q3{Can add triggers?}

    Q2 -->|Yes| LOG[Log-Based CDC<br/>Debezium + Kafka]
    Q2 -->|No| Q4{Managed CDC service<br/>available?}

    Q3 -->|Yes| TRIGGER[Trigger-Based CDC<br/>+ Polling]
    Q3 -->|No| POLL[Query-Based Polling<br/>with timestamps]

    Q4 -->|AWS| DMS[AWS DMS]
    Q4 -->|Azure| SYNAPSE[Azure Synapse Link]
    Q4 -->|GCP| DATASTREAM[GCP Datastream]

    style LOG fill:#4ecdc4,color:#fff
    style TRIGGER fill:#f9ca24,color:#000
    style POLL fill:#ff6b6b,color:#fff
```

## Related Patterns

- [Stream Processing Architecture](02-stream-processing-architecture.md) — Processing CDC events
- [Real-Time Analytics Architecture](01-real-time-analytics-architecture.md) — Windowing and aggregation on CDC streams
- [Event Sourcing / CQRS](../../02-application-software-architecture/06-design-patterns/) — CDC as event source
- [Kappa Architecture](../02-analytics-architecture/05-kappa-architecture.md) — CDC as immutable event log
- [OLTP Architecture](../01-data-architecture/01-oltp-architecture.md) — Source database considerations

> **Azure Implementation**: See [Azure Synapse Link](../../../architecture-azure/data/) (near-real-time CDC to Synapse), [Azure Data Factory](../../../architecture-azure/data/data-factory/) (CDC with change tracking), [Azure SQL Managed Instance CDC](https://learn.microsoft.com/en-us/azure/azure-sql/), and [Debezium on Azure](https://debezium.io/) for open-source log-based CDC.
