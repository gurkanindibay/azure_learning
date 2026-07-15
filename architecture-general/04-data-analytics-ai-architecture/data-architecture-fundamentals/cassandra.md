---
type: Architecture Pattern
title: "Apache Cassandra"
description: "Distributed, masterless NoSQL database for high write throughput, tunable consistency, and multi-region availability"
timestamp: 2026-07-16T00:00:00Z
---

# Apache Cassandra

> **Taxonomy Reference**: §4.0 Data Architecture Fundamentals (see [Architecture Taxonomy Reference](../../10-practicality-taxonomy/architecture_taxonomy_reference.md))
> **Term Definition**: See [Apache Cassandra](../../../reference-dictionary/databases.md#apache-cassandra)

Apache Cassandra is a distributed, masterless NoSQL database optimized for high write throughput, continuous availability, and linear horizontal scaling across multiple regions.

## Problem

Traditional relational databases struggle with workloads that require:

- Massive write throughput across many nodes
- Continuous uptime during node or region failures
- Low-latency reads and writes in multiple geographic regions
- Elastic scaling without a single point of failure

A single-primary architecture pauses writes during failover and funnels all writes through one node, becoming a bottleneck at scale.

## Solution

Cassandra uses a **masterless, peer-to-peer ring architecture** where every node is equal. Data is partitioned and replicated across the cluster using a partition key hash. Any node can accept reads or writes, and clients connect to the nearest replica for local-latency operations.

```mermaid
graph TB
    C[Client] --> LB[Load Balancer / Driver]
    LB --> N1[Node 1]
    LB --> N2[Node 2]
    LB --> N3[Node 3]
    N1 <--> N2
    N2 <--> N3
    N3 <--> N1
    style N1 fill:#e1f5fe
    style N2 fill:#e1f5fe
    style N3 fill:#e1f5fe
```

## Abstraction Level

- [x] Logical (Design)
- [x] Physical (Implementation)
- [ ] Conceptual (Strategic)
- [ ] Runtime (Operational)

## Core Features

| Feature | Description | Benefit |
|---|---|---|
| **Masterless architecture** | Every node is a peer; no primary/secondary distinction | No single point of failure; no election pause |
| **Tunable consistency** | Per-operation consistency levels: `ANY`, `ONE`, `TWO`, `THREE`, `QUORUM`, `ALL`, `LOCAL_QUORUM`, `EACH_QUORUM` | Trade consistency for latency/availability per query |
| **Linear scalability** | Adding nodes increases throughput and storage capacity proportionally | Scale out cheaply on commodity hardware |
| **Multi-region replication** | Data centers can be added to the replication topology | Local reads/writes for global users |
| **Write-optimized storage** | Append-only commit log + memtable flushed to immutable SSTables | Very high ingest throughput |
| **Built-in repair mechanisms** | Anti-entropy repair, hinted handoff, read repair | Replicas converge without manual intervention |

## Consistency Traits

Cassandra is typically classified as an **AP** system under the [CAP Theorem](cap-theorem.md): it favors availability and partition tolerance over strong consistency. However, consistency is **tunable** per operation.

### Consistency Levels

| Level | Behavior | Typical Use Case |
|---|---|---|
| `ONE` | Acknowledge after first replica responds | Low-latency reads where staleness is acceptable |
| `QUORUM` | Majority of replicas (`(RF/2)+1`) must respond | Balance of consistency and availability |
| `ALL` | All replicas must respond | Strong consistency; write fails if any replica is down |
| `LOCAL_QUORUM` | Majority in the local data center | Avoid cross-region latency while staying consistent |
| `EACH_QUORUM` | Majority in every data center | Strong consistency across regions; higher latency |

The replication factor (`RF`) and consistency level (`CL`) together determine the observed consistency. For example, with `RF=3` and `CL=QUORUM`, writes and reads both require two replicas, guaranteeing read-your-writes consistency.

### Lightweight Transactions (LWT)

For operations that require linearizable semantics — such as inserting a unique custom alias — Cassandra provides `IF NOT EXISTS` writes backed by Paxos. LWT is significantly slower than normal writes and should be used sparingly.

## Data Model

Cassandra data modeling is **query-first**: tables are designed to serve specific access patterns, often denormalizing data rather than joining.

```sql
-- Redirect lookup by short code
CREATE TABLE url_mappings (
    url_part text PRIMARY KEY,
    original_url text,
    redirect_type tinyint,
    expiration_date timestamp
);

-- Time-series clicks partitioned by URL and day
CREATE TABLE click_stats_daily (
    url_part text,
    bucket_day date,
    click_time timestamp,
    region text,
    count counter,
    PRIMARY KEY ((url_part, bucket_day), click_time, region)
);
```

Key modeling rules:

- The **partition key** determines data distribution and query routing.
- **Clustering columns** define sort order within a partition.
- Avoid unbounded partitions; use time bucketing for high-cardinality time series.
- Prefer denormalization over joins; joins are not natively supported.

## When to Use

- High-write-throughput workloads: IoT telemetry, messaging, logging, time-series
- Multi-region applications requiring local read/write latency
- Systems where write availability must continue during node or region failures
- Workloads with well-defined, simple access patterns (key lookups, time-range scans)
- Use cases that can tolerate eventual consistency or explicitly tune consistency per query

## When NOT to Use

- Workloads requiring complex joins, ad-hoc queries, or rich aggregations
- Systems where strong consistency is mandatory during network partitions (e.g., core banking, payment ledgers)
- Small datasets where operational complexity outweighs scaling benefits
- Frequent multi-row transactions or `IF NOT EXISTS` patterns at high throughput

## Implementation Considerations

| Area | Guidance |
|---|---|
| **Partition sizing** | Keep partitions under 100 MB and ideally under a few hundred megabytes to avoid compaction and read issues. |
| **Replication factor** | Use `RF=3` in production per data center; higher RF improves durability but increases write coordination. |
| **Consistency tuning** | Use `LOCAL_QUORUM` for most cross-region workloads; reserve `ALL` for rare strong-consistency needs. |
| **Repair schedule** | Run `nodetool repair` regularly to ensure replicas converge, especially after node outages. |
| **Driver configuration** | Use a data-center-aware driver with token-aware routing to send queries to replicas holding the data. |
| **Monitoring** | Track partition size, compaction backlog, repair progress, and read/write latency p99. |

## Comparison with Alternative Stores

| Characteristic | Cassandra | MongoDB | PostgreSQL |
|---|---|---|---|
| Architecture | Masterless, peer-to-peer | Single-primary replica sets | Single-primary with replicas |
| Consistency | Tunable, eventual by default | Tunable, strong by default | Strong ACID |
| Best workload | High write throughput, time-series | Flexible documents, rich queries | Complex transactions, relational data |
| Multi-region writes | Native, local writes everywhere | Writes routed to primary | Typically single primary |
| Joins | Not supported | Limited `$lookup` | Full SQL joins |
| Scaling model | Horizontal, add nodes | Horizontal via sharding | Vertical + read replicas |

## Related Concepts

- [BASE Properties](base-properties.md) — Availability-first semantics
- [CAP Theorem](cap-theorem.md) — Trade-offs in distributed systems
- [ACID Properties](acid-properties.md) — Strong transaction guarantees
- [Apache Cassandra](../../../reference-dictionary/databases.md#apache-cassandra) — Term definition and characteristics

## Platform-Specific Implementations

> **Azure Implementation**: See [Azure Managed Instance for Apache Cassandra](../../../architecture-azure/data/databases/) for Azure-specific deployment and migration options.
