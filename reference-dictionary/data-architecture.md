---
type: Reference
title: "Data Architecture & Distributed Systems"
description: "**CAP Theorem** — in a distributed system, you can guarantee only two of three: Consistency, Availability, Partition Tolerance."
timestamp: 2026-06-28T00:00:00Z
---

# Data Architecture & Distributed Systems

> **Domain**: Data mesh, data fabric, medallion architecture, distributed system theory (CAP), scaling patterns, and data governance models.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| CAP Theorem | [`#cap-theorem`](#cap-theorem) |
| Vertical vs Horizontal Scaling | [`#vertical-vs-horizontal-scaling`](#vertical-vs-horizontal-scaling) |
| Replication | [`#replication`](#replication) |
| Sharding | [`#sharding`](#sharding) |
| Data Catalog | [`#data-catalog`](#data-catalog) |
| Polyglot Persistence | [`#polyglot-persistence`](#polyglot-persistence) |
| Data Fabric | [`#data-fabric`](#data-fabric) |
| Data Mesh | [`#data-mesh`](#data-mesh) |
| Data Product | [`#data-product`](#data-product) |
| Federated Governance | [`#federated-governance`](#federated-governance) |
| Practical Decentralization | [`#practical-decentralization`](#practical-decentralization) |
| Medallion Architecture | [`#medallion-architecture`](#medallion-architecture) |
| Semantic Layer | [`#semantic-layer`](#semantic-layer) |

---

## CAP Theorem

In a distributed system, you can guarantee only **two of three**: **C**onsistency (all nodes see the same data), **A**vailability (every request gets a response), **P**artition Tolerance (system works despite network partitions). Since network partitions are inevitable, the real choice is CP (sacrifice availability during partition) or AP (sacrifice strong consistency during partition).

| Choice | Use Case | Example |
|:---|:---|:---|
| **CP** | Financial ledgers, inventory counts | HBase, Zookeeper, etcd |
| **AP** | Social feeds, shopping carts, search indexes | Cassandra, DynamoDB, Cosmos DB |

### Key Characteristics
- **PACELC extension**: When Partitioned, choose A or C. Else (no partition), choose Latency or Consistency
- **Tunable consistency**: Modern databases offer configurable consistency levels (e.g., Cosmos DB 5 levels, Cassandra QUORUM)
- **Not binary**: CAP is a spectrum — most systems are neither purely CP nor purely AP

**Also see**: [Replication](#replication) · [Sharding](#sharding) · [Vertical vs Horizontal Scaling](#vertical-vs-horizontal-scaling)

---

## Vertical vs Horizontal Scaling

Two strategies for handling increased load:
- **Vertical scaling (scale up)**: Buy a bigger machine — more CPU, RAM, disk. Simple but hits physical limits and becomes exponentially expensive. Single point of failure.
- **Horizontal scaling (scale out)**: Add more machines behind a load balancer. Scales infinitely, adds fault tolerance, but requires stateless design and data partitioning.

| | Vertical (Scale Up) | Horizontal (Scale Out) |
|:---|:---|:---|
| **Complexity** | Low | High (requires LB, stateless services) |
| **Cost curve** | Linear then exponential | Linear per node |
| **Fault tolerance** | Single point of failure | Tolerates node failures |
| **Scaling limit** | Hardware ceiling | Theoretically infinite |

### When to Use
- **Vertical**: Early-stage apps, legacy monoliths, databases with licensing per-core
- **Horizontal**: Cloud-native apps, stateless services, high-availability requirements

**Also see**: [CAP Theorem](#cap-theorem) · [Replication](#replication) · [Sharding](#sharding)

---

## Replication

Copying data to multiple servers so that **reads can scale horizontally** and the system survives individual server failures. Writes go to the primary; reads can go to any replica. The tradeoff is **replication lag** — replicas may return stale data for milliseconds to seconds after a write.

### Key Characteristics
- **Read scalability**: N replicas = up to N× read throughput
- **Fault tolerance**: Primary fails → promote replica
- **Replication lag**: Asynchronous replication means stale reads from replicas

### When to Use
- Read-heavy workloads where slightly stale data is acceptable
- Disaster recovery and geographic distribution

### When NOT to Use
- Write-heavy workloads (replication adds overhead, doesn't help write throughput)
- When every read must reflect the latest write (use primary reads or synchronous replication)

**Also see**: [Sharding](#sharding) · [CAP Theorem](#cap-theorem)

---

## Sharding

Splitting a database into **smaller, independent pieces (shards)** so that writes and storage scale horizontally. Each shard handles a subset of data — typically by key range or hash. Enables write scalability beyond what a single machine can handle.

### Key Characteristics
- **Write scalability**: N shards = up to N× write throughput
- **Key-based routing**: Same key → same shard → consistent data locality
- **No cross-shard joins**: Application must handle data that spans shards

### When to Use
- Write-heavy workloads exceeding single-machine capacity
- Data volumes too large for a single database

### When NOT to Use
- When cross-shard queries are frequent (complexity may outweigh benefit)
- Small datasets that fit on a single machine (premature optimization)

**Also see**: [Replication](#replication) · [Vertical vs Horizontal Scaling](#vertical-vs-horizontal-scaling) · [CAP Theorem](#cap-theorem)
> **Cross-reference**: Also defined in [`data-concurrency.md`](data-concurrency.md#sharding) with a concurrency/transaction focus.

---

## Data Catalog

A **centralized inventory of data assets** with searchable metadata, ownership, lineage, and schema information. A real data catalog is not a dusty Confluence page — it is a living system that helps producers and consumers discover, understand, and trust data.

### Key Characteristics
- Searchable metadata and documentation
- Ownership and stewardship assignments
- Data lineage and provenance tracking
- Integration with data quality and governance tools

### When to Use
- More than a handful of data producers or consumers
- Compliance or audit requirements demand traceability
- Teams waste time hunting for the "right" dataset or its owner

### When NOT to Use
- Very small, static datasets with one consumer
- When curation discipline is absent (becomes stale metadata graveyard)

### Also see
- [Data Mesh](#data-mesh)
- [Federated Governance](#federated-governance)

---

## Polyglot Persistence

An architectural approach where **different services (or different read models within a single service) each use the data store best suited to their access patterns**, rather than sharing a single database technology across the system.

### Key Characteristics
- **Fit-for-purpose stores**: RDBMS for strong consistency and relational queries; document stores for flexible schema; key-value stores for low-latency single-key lookups; search engines for full-text and faceted queries
- **Service autonomy**: each service owns its data store — no shared schema, no cross-service joins
- **CQRS enabler**: the pattern is the operational foundation of CQRS read models — each query model independently selects its optimal store

### When to Use
- Command side needs ACID transactions; read side needs low-latency key lookups or full-text search
- Different teams own different services and should not be constrained by a shared schema
- Scaling requirements differ radically between services (e.g., write-heavy transactional service vs. read-heavy reporting service)

### When NOT to Use
- Small teams or early-stage products where the operational overhead of multiple stores outweighs the benefits
- When strong cross-service consistency is required (cross-store distributed transactions are expensive)

### Also see
- [CQRS](cqrs-event-driven.md#cqrs) · [Database Per Service](architecture-patterns.md#database-per-service) · [Microservices](architecture-patterns.md#microservices)

---

## Data Fabric

A **metadata-driven, automation-focused data architecture** that connects disparate data sources and tools through unified discovery, governance, and integration layers. Data Fabric is not a replacement for Data Mesh — it solves different layers, mostly automation and metadata.

### Key Characteristics
- Unified metadata layer across distributed data
- AI/ML-driven data discovery and classification
- Automated data integration and pipeline generation
- Governance and policy enforcement across silos

### When to Use
- Heterogeneous data landscape with many sources and tools
- Need for automated discovery, lineage, and policy enforcement
- Data Mesh alone leaves metadata and integration gaps

### When NOT to Use
- As a silver bullet to fix organizational ownership problems
- When the real issue is lack of data-product discipline, not integration plumbing

### Also see
- [Data Mesh](#data-mesh)
- [Practical Decentralization](#practical-decentralization)

---

## Data Mesh

A **decentralized socio-technical approach to data architecture** where domain-oriented teams own their data as products. Data Mesh shifts data ownership from central data teams to domain teams, supported by federated governance and a self-serve data platform.

### Key Characteristics
- Domain-oriented decentralized data ownership
- Data as a product (governed, versioned, documented, with SLAs)
- Self-serve data infrastructure platform
- Federated computational governance

### When to Use
- Organization has mature domain teams with stable ownership
- Central data team is a persistent bottleneck
- Domains are willing and able to treat data as a product

### When NOT to Use
- Teams rotate frequently or lack data-engineering skills
- Governance culture is weak (becomes "decentralized chaos with documentation")
- Organization expects platform purchase to substitute for operating-model change

### Also see
- [Data Product](#data-product)
- [Federated Governance](#federated-governance)
- [Practical Decentralization](#practical-decentralization)

---

## Data Product

A **curated, reusable data asset** exposed with clear semantics, quality guarantees, versioning, documentation, and ownership. A data product is not a dashboard, a random table, or a CSV that happens to be in S3.

### Key Characteristics
- Defined owner and consumers
- Explicit SLAs (freshness, quality, availability)
- Versioned schema and interface
- Documented semantics and usage contracts

### When to Use
- Data is consumed by multiple teams or systems
- Data quality and reliability directly affect decisions
- Data Mesh or decentralized ownership model is in use

### When NOT to Use
- One-off exploratory analysis
- Ad-hoc exports with no clear consumer or maintenance owner

### Also see
- [Data Mesh](#data-mesh)
- [Data Catalog](#data-catalog)

---

## Federated Governance

A **governance model** where central standards are set globally but applied locally by domain teams. It combines centralized policy definition with domain-level execution, automated enforcement, and audit-friendly evidence.

### Key Characteristics
- Central standards + domain-applied rules
- Automation-first enforcement (schema checks, quality gates, access controls)
- Audit-friendly logs and lineage
- Not 17 Notion pages no one will ever read

### When to Use
- Decentralized data ownership with compliance or audit requirements
- Need to balance standardization with domain autonomy
- Policy-as-code and automated checks are feasible

### When NOT to Use
- When central team tries to enforce everything manually
- When governance is treated as documentation theater rather than executable policy

### Also see
- [Data Mesh](#data-mesh)
- [Data Fabric](#data-fabric)

---

## Practical Decentralization

A **hybrid data-architecture approach** that keeps the benefits of decentralized domain ownership while retaining centralized platform, security, and governance guardrails. It solves most Data Mesh pain with a smaller organizational leap: domains own logic, not the whole planet.

### Key Characteristics
- Central platform team owns infrastructure, tooling, security, and cost guardrails
- Domain teams own transformations, business logic, data definitions, and data contracts
- Shared semantic layer aligns metrics across domains
- Federated governance with automation-first enforcement

### When to Use
- Organization wants decentralized data but lacks full Data Mesh maturity
- Repeated attempts at pure decentralization produced chaos
- Need a pragmatic middle ground between centralization and domain autonomy

### When NOT to Use
- As an excuse to skip governance entirely
- When the central platform team is too weak to provide reliable guardrails

### Also see
- [Data Mesh](#data-mesh)
- [Semantic Layer](#semantic-layer)
- [Federated Governance](#federated-governance)

---

## Medallion Architecture

A **data architecture pattern** that organizes data processing into three sequential stages: **Bronze** (raw, ingested data), **Silver** (cleaned, transformed data), and **Gold** (business-ready, analytics-friendly data). Originally popularized by Databricks' lakehouse architecture, it provides a simple mental model for data quality progression.

### Key Characteristics
- Three canonical layers: Bronze (raw/immutable), Silver (cleansed/enriched), Gold (aggregated/business-ready)
- Each layer adds structure and quality — Bronze is schema-on-read, Silver is validated, Gold is modeled for consumption
- Pipeline-centric by design: organizes data by processing stage, not by business domain
- Best suited for batch-oriented, centralized, stable-source environments

### When to Use
- Small to mid-scale data platforms with stable data sources
- Batch workloads dominate (daily/hourly ETL/ELT)
- Centralized data engineering team with clear ownership
- Getting started with a lakehouse architecture — it's an excellent starting point

### When NOT to Use
- As a permanent organizational model — layers should not become team boundaries
- Streaming-first or real-time workloads without adapting to Kappa architecture
- Multi-domain, multi-team platforms without adding data-product and contract layers
- As a substitute for domain-driven ownership, semantic layers, or schema contracts

### Also see
- [Data Mesh](#data-mesh)
- [Data Product](#data-product)
- [Semantic Layer](#semantic-layer)
- [Practical Decentralization](#practical-decentralization)

---

## Semantic Layer

A **shared abstraction layer** that centralizes metric definitions, dimensions, and business logic so consumers query consistent, governed semantics instead of each domain reinventing metrics.

### Key Characteristics
- Canonical metric definitions and calculations
- Reusable dimensions, filters, and aggregations
- Decouples BI tools from raw data models
- Reduces tribal knowledge and metric drift

### When to Use
- Multiple teams or tools consume the same KPIs
- Metric definitions vary by domain or dashboard
- Self-serve analytics is hampered by inconsistent semantics

### When NOT to Use
- Single-consumer analytics with simple, stable metrics
- When central team cannot keep up with domain change velocity

### Also see
- [Data Mesh](#data-mesh)
- [Data Product](#data-product)

---

> **Convention**: Every term anchor follows `domain-file.md#lowercase-hyphenated-term`. Always link to the primary definition, never to a cross-reference.
