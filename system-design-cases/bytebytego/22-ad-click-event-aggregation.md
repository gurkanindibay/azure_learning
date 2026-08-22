---
type: System Design Case
title: "Ad Click Event Aggregation"
description: "Design a distributed, real-time ad click event aggregation system at Google/Meta scale supporting exactly-once processing, windowed rollups, star schema filtering, and fault-tolerant stream analytics."
tags: [system-design, distributed-systems, stream-processing, kafka, flink, time-series]
timestamp: 2026-08-22T00:00:00Z
---

# Ad Click Event Aggregation

> **Source**: *System Design Interview – An Insider's Guide: Volume 2* by Alex Xu & Sahn Lam  
> **ByteByteGo Chapter**: 22  
> **Topic**: Real-Time Stream Processing, Distributed Event Aggregation, Exactly-Once Semantics, Star Schema, Hotspot Mitigation

---

## 1. Understand the Problem and Establish Design Scope

Ad click event aggregation is a foundational subsystem of digital advertising platforms (such as Google Ads, Meta Ads, and Amazon Advertising). It aggregates raw ad click streams into actionable real-time metrics used for **advertiser billing**, **budget pacing**, **real-time bidding (RTB) feedback**, and **analytics dashboards**.

```mermaid
flowchart LR
    subgraph Sources["Ad Click Sources"]
        S1["Web Browsers"]
        S2["Mobile Apps"]
        S3["App Servers"]
    end

    subgraph Ingestion["Ingestion & Streaming"]
        L["Log Collector"] --> K1["Raw Event Stream<br/>(Kafka Topic)"]
        K1 --> AGG["Stream Aggregator<br/>(MapReduce / Flink DAG)"]
        AGG --> K2["Aggregated Stream<br/>(Kafka Topic)"]
    end

    subgraph Storage["Storage Layer"]
        K2 --> W["DB Writer"]
        W --> DB[("Aggregated DB<br/>(Cassandra / ClickHouse)")]
        K1 --> RAW[("Raw Log Store<br/>(S3 / Parquet)")]
    end

    subgraph Consumers["Downstream Consumers"]
        DB --> Q["Query Service"]
        Q --> DASH["Real-Time Dashboards"]
        Q --> BILL["Ads Billing Engine"]
        Q --> RTB["Real-Time Bidding (RTB)"]
    end

    Sources --> L
```

---

### Interview Clarification & Scope

> **Candidate:** What is the format of the input data?  
> **Interviewer:** Input data consists of log files appended across multiple application servers. Each event contains: `ad_id`, `click_timestamp`, `user_id`, `ip`, and `country`.
>
> **Candidate:** What is the expected data volume?  
> **Interviewer:** 1 billion ad clicks per day across 2 million unique active ads. The event volume grows roughly 30% year-over-year.
>
> **Candidate:** What are the most important queries the system must support?  
> **Interviewer:** Three primary queries:
> 1. **Ad Click Count**: Return the aggregated click count for a specific `ad_id` over the last $M$ minutes.
> 2. **Top $N$ Popular Ads**: Return the top 100 most-clicked ads in the past 1 minute (both $N$ and time window configurable).
> 3. **Attribute Filtering**: Support dynamic filtering by `ip`, `user_id`, or `country` for the above queries.
>
> **Candidate:** What edge cases should we prepare for?  
> **Interviewer:** 
> - Events arriving late (out-of-order data).
> - Duplicate event deliveries (from client retries or network drops).
> - System component outages and state recovery.
>
> **Candidate:** What are the latency requirements?  
> **Interviewer:** End-to-end latency of a few minutes is acceptable for reporting and billing. (Note: RTB auctions require sub-second latency, but downstream billing and aggregation tolerate 1–3 minutes).

---

### Requirements Summary

#### Functional Requirements
1. **Per-Ad Click Aggregation**: Aggregate click counts for any `ad_id` across sliding/tumbling windows of $M$ minutes.
2. **Top $N$ Query**: Return the top $N$ most-clicked ads over the past $M$ minutes updated every minute.
3. **Multi-Dimensional Filtering**: Support filtering queries by dimensions such as `country`, `ip`, and `user_id`.
4. **Data Recalculation**: Support historical data replay and backfilling if a bug or corruption occurs.

#### Non-Functional Requirements
- **High Correctness & Accuracy**: Financial impact is significant; data directly affects billing and advertiser trust. Requires **exactly-once** processing semantics.
- **Low Latency**: End-to-end processing latency must stay under a few minutes.
- **Robust Fault Tolerance**: Node failures must not cause data loss, double-counting, or silent drops.
- **Scalability**: Must scale gracefully to peak loads ($50{,}000\text{ QPS}$) and 30% annual traffic growth.

---

### Back-of-the-Envelope Estimation

| Dimension / Metric | Calculation & Value |
|:---|:---|
| **Daily Active Users (DAU)** | $1\text{ Billion DAU}$ |
| **Daily Ad Clicks** | $1\text{ Billion clicks/day}$ (assuming 1 ad click per user per day on average) |
| **Average Write QPS** | $\frac{10^9\text{ clicks}}{86{,}400\text{ seconds}} \approx 10{,}000\text{ QPS}$ |
| **Peak Write QPS** | $5 \times \text{Average QPS} = 50{,}000\text{ QPS}$ |
| **Total Active Ads** | $2\text{ Million ads}$ |
| **Raw Event Size** | $\approx 100\text{ Bytes (0.1 KB)}$ per event |
| **Daily Raw Storage** | $10^9 \times 0.1\text{ KB} = 100\text{ GB/day}$ |
| **Monthly Raw Storage** | $100\text{ GB/day} \times 30\text{ days} = 3\text{ TB/month}$ |
| **Annual Raw Storage** | $3\text{ TB/month} \times 12\text{ months} = 36\text{ TB/year}$ |

---

## 2. High-Level Design & Core Data Models

### Query API Design

The API serves internal dashboards, advertiser portals, and billing systems.

#### 1. Aggregate Click Count for a Specific Ad
`GET /v1/ads/{ad_id}/aggregated_count`

##### Request Parameters
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `ad_id` | `String` (path) | Yes | Unique identifier of the target ad |
| `from` | `Int64` (epoch sec) | No | Start timestamp of range (defaults to 1 minute ago) |
| `to` | `Int64` (epoch sec) | No | End timestamp of range (defaults to current time) |
| `filter_id` | `String` (query) | No | Pre-computed filter dimension identifier (e.g., US-only) |

##### Response Payload
```json
{
  "ad_id": "ad001",
  "count": 1420,
  "from": 1609459200,
  "to": 1609459260,
  "filter_id": "0012"
}
```

---

#### 2. Get Top $N$ Most-Clicked Ads
`GET /v1/ads/popular_ads`

##### Request Parameters
| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `count` | `Integer` | No | Number of top ads to return ($N$, default: 100) |
| `window` | `Integer` | No | Aggregation window size ($M$) in minutes (default: 1) |
| `filter_id` | `String` | No | Dimension filter strategy identifier |

##### Response Payload
```json
{
  "window_size_min": 1,
  "update_time": 1609459260,
  "ads": [
    { "ad_id": "ad099", "clicks": 28450 },
    { "ad_id": "ad001", "clicks": 19320 },
    { "ad_id": "ad312", "clicks": 14200 }
  ]
}
```

---

### Data Models & Schema Design

The system maintains two distinct categories of data: **Raw Event Data** and **Aggregated Data**.

```mermaid
classDiagram
    class RawClickEvent {
        +String ad_id
        +Timestamp click_timestamp
        +String user_id
        +String ip
        +String country
    }

    class AggregatedAdCount {
        +String ad_id
        +Timestamp click_minute
        +String filter_id
        +Long count
    }

    class TopNPopularAds {
        +Integer window_size
        +Timestamp update_time_minute
        +JSON most_clicked_ads
    }

    class FilterDimension {
        +String filter_id
        +String region
        +String ip_range
        +String user_segment
    }

    RawClickEvent ..> AggregatedAdCount : Stream Processed into
    AggregatedAdCount ..> TopNPopularAds : Reduced into
    FilterDimension --> AggregatedAdCount : Dimension Tag
```

#### Raw vs. Aggregated Data Trade-Off

| Storage Strategy | Pros | Cons | Recommendation |
|:---|:---|:---|:---|
| **Raw Data Only** | • Complete fidelity<br>• Full debugging & audit trail<br>• Supports ad-hoc ML model training | • Massive storage growth<br>• Range queries and analytical rollups are unacceptably slow | Use as immutable backup and source for replay |
| **Aggregated Data Only** | • Ultra-fast query response<br>• Compact storage footprint<br>• Optimized for dashboard refresh | • Irreversible loss of raw details<br>• Impossible to backfill new metrics or fix bugs | Use for active queries and dashboards |
| **Hybrid (Store Both)** | • Best of both worlds: fast active queries + full recovery capability | • Additional storage & dual pipeline maintenance overhead | **✅ Recommended Choice** |

---

### Database Selection

```mermaid
flowchart TD
    DataFlow{"Data Nature"}
    
    DataFlow -->|Raw Event Stream| RAW_TIER["Raw Storage Tier"]
    RAW_TIER --> CASS_RAW["Cassandra / HBase\n(High write throughput)"]
    RAW_TIER --> S3_PARQUET["Cloud Object Storage (S3/GCS)\n+ Columnar Parquet/ORC\n(Cost-effective cold storage)"]
    
    DataFlow -->|Aggregated Time-Series| AGG_TIER["Aggregated Storage Tier"]
    AGG_TIER --> CASS_AGG["Cassandra / ScyllaDB\n(Fast row lookups & TTLs)"]
    AGG_TIER --> OLAP["ClickHouse / Apache Pinot\n(Ultra-fast OLAP & vector filters)"]
```

1. **Raw Data Storage**:
   - **Characteristics**: Extremely write-heavy ($10\text{K} - 50\text{K}\text{ QPS}$), append-only, low read frequency (only triggered for batch retraining or disaster recalculations).
   - **Engine Options**: 
     - **NoSQL Key-Value / Wide-Column** (Apache Cassandra / HBase) partitioned by `(date, ad_id)`.
     - **Cloud Object Storage + Parquet** (Amazon S3 / GCS): Stream processors flush batch Parquet files rotated every $10\text{ GB}$ or 15 minutes. Very cost-effective.
2. **Aggregated Data Storage**:
   - **Characteristics**: Both read-heavy (dashboards auto-refreshing for 2M ads) and write-heavy (bulk window updates every minute).
   - **Engine Options**:
     - **Apache Cassandra**: Efficient for time-series range queries with compound primary keys `((ad_id, filter_id), click_minute)`.
     - **ClickHouse / Apache Pinot**: Purpose-built column stores with native streaming ingestion from Kafka and sub-second OLAP rollups.

---

### End-to-End System Architecture

To handle unpredictable traffic spikes without overwhelming downstream consumers, we decouple producers, processors, and storage engines using distributed message queues (**Apache Kafka**).

```
+----------------------------------------------------------------------------------------------------+
|                                    END-TO-END DATA PIPELINE                                        |
+----------------------------------------------------------------------------------------------------+

 [ App Server 1 ] \
 [ App Server 2 ] ---> [ Log Collector ] ---> [ Kafka Topic 1: Raw Events ]
 [ App Server 3 ] /                                    |
                                                       v
                                            [ Stream Aggregator (Flink) ]
                                            +---------------------------+
                                            | • Map / Cleanse           |
                                            | • Tumbling Windows (1 min)|
                                            | • Sliding Windows (M min) |
                                            | • Local Min-Heap (Top N)  |
                                            +---------------------------+
                                                       |
                                                       v
                                            [ Kafka Topic 2: Aggregated ]
                                                       |
                                                       v
                                            [ Database Sink Consumer ]
                                                       |
                                                       v
                                          [ Aggregated DB (Cassandra) ]
                                                       |
                                                       v
                                         [ Query Service & Dashboards ]
```

```mermaid
flowchart TD
    subgraph Ingestion_Stage["1. Event Ingestion"]
        A1["App Server 1"] & A2["App Server 2"] & A3["App Server N"] --> LC["Log Collector / Agent"]
        LC --> K1["Kafka Topic 1<br/>(raw_ad_clicks)"]
    end

    subgraph Stream_Stage["2. Stream Processing (Flink DAG)"]
        K1 --> MAP["Map / Filter Nodes<br/>(Normalize & Key by ad_id)"]
        MAP --> AGG["Aggregate Nodes<br/>(1-min Window Count & Local Heap)"]
        AGG --> RED["Reduce Nodes<br/>(Global Top N Merge)"]
    end

    subgraph Sink_Stage["3. Aggregated Storage & Serving"]
        RED --> K2["Kafka Topic 2<br/>(aggregated_ad_clicks)"]
        K2 --> SINK["DB Writer / Sink Service"]
        SINK --> TSDB[("Aggregated DB<br/>(Cassandra / ClickHouse)")]
        TSDB --> QS["Query Service"]
        QS --> DASH["Real-time Dashboard / Billing API"]
    end

    subgraph Cold_Stage["4. Cold Archival"]
        K1 -.-> S3_WRITER["Archival Consumer"]
        S3_WRITER -.-> S3[("Object Store<br/>(S3 Parquet Archive)")]
    end
```

---

### Stream Processing: The MapReduce DAG Model

The aggregation engine decomposes stream computation into a Directed Acyclic Graph (DAG) of specialized computing nodes:

```mermaid
flowchart LR
    subgraph MapStage["Map Phase"]
        SRC["Kafka Consumer"] --> M1["Map Node 1<br/>(Cleanse & Hash)"]
        SRC --> M2["Map Node 2<br/>(Cleanse & Hash)"]
    end

    subgraph AggStage["Aggregate Phase (In-Memory)"]
        M1 -->|ad_id % 3 == 0| AG1["Aggregate Node 0<br/>(Tumbling Window + MinHeap)"]
        M1 -->|ad_id % 3 == 1| AG2["Aggregate Node 1<br/>(Tumbling Window + MinHeap)"]
        M2 -->|ad_id % 3 == 2| AG3["Aggregate Node 2<br/>(Tumbling Window + MinHeap)"]
        M2 -->|ad_id % 3 == 0| AG1
    end

    subgraph ReduceStage["Reduce Phase"]
        AG1 -->|Local Top 100| R["Reduce Node<br/>(Global Top 100 Merge)"]
        AG2 -->|Local Top 100| R
        AG3 -->|Local Top 100| R
        R --> OUT["Emit to Kafka Topic 2"]
    end
```

#### Core Roles in the DAG
1. **Map Node**:
   - Reads raw events from Kafka partitions.
   - Cleanses, filters, and normalizes unstructured fields.
   - Shards and routes records downstream based on `hash(ad_id) % num_aggregate_nodes`.
2. **Aggregate Node**:
   - Maintains in-memory count state for each `ad_id` during the current active time window.
   - Computes local Top $N$ rankings using a local **bounded min-heap** ($O(K \log N)$ space/time).
3. **Reduce Node**:
   - Gathers local Top $N$ candidates from all upstream aggregate nodes.
   - Merges the streams into a definitive **global Top $N$ list** for the time window and emits the result.

---

### Multi-Dimensional Data Filtering (Star Schema)

To support queries like *"Number of clicks for `ad001` in the US on mobile"*, we use a **Star Schema** dimensional modeling approach pre-aggregated directly in the stream:

```mermaid
erDiagram
    FACT_AD_AGGREGATIONS {
        string ad_id PK
        timestamp click_minute PK
        string filter_id FK
        bigint click_count
    }

    DIM_FILTER {
        string filter_id PK
        string country
        string ip_subnet
        string device_type
    }

    DIM_FILTER ||--o{ FACT_AD_AGGREGATIONS : "defines dimension"
```

#### Aggregated Data with Star Schema Dimension
| `ad_id` | `click_minute` | `filter_id` | `count` | Description |
|:---|:---|:---|:---|:---|
| `ad001` | `2021-01-01 00:00:00` | `0012` | 240 | US Traffic Only |
| `ad001` | `2021-01-01 00:00:00` | `0013` | 510 | EU Traffic Only |
| `ad001` | `2021-01-01 00:00:00` | `0000` | 1200 | Global / All Dimensions (`*`) |
| `ad002` | `2021-01-01 00:00:00` | `0012` | 45 | US Traffic Only |

> [!TIP]
> **Star Schema Trade-Off**: Pre-computing dimension combinations guarantees $O(1)$ query lookup speed at runtime. However, having too many dimensions causes combinatorial explosion (*curse of dimensionality*). For dynamic ad-hoc slicing across dozens of dimensions, modern OLAP engines (ClickHouse / Pinot) are preferred over static pre-materialization.

---

## 3. Design Deep Dive

---

### 1. Streaming vs. Batch Processing & Kappa Architecture

| Dimension | Online Services | Batch Systems (Offline) | Streaming Systems (Near Real-Time) |
|:---|:---|:---|:---|
| **Responsiveness** | Milliseconds ($< 100\text{ ms}$) | Hours / Days | Sub-second to minutes |
| **Input Data** | Discrete user requests | Bounded historical datasets | **Unbounded continuous streams** |
| **Output** | Response to end user | Materialized tables, reports | **Continuous metric streams, live views** |
| **Tooling** | Web servers, microservices | MapReduce, Spark, Hive | **Apache Flink, Spark Streaming, Kafka Streams** |

```mermaid
flowchart TD
    subgraph LambdaArch["Lambda Architecture (Dual Pipeline)"]
        SRC_L["Raw Events"] --> BATCH_L["Batch Layer (Hadoop/Spark)"]
        SRC_L --> SPEED_L["Speed Layer (Storm/Flink)"]
        BATCH_L --> B_VIEW["Batch Views"]
        SPEED_L --> S_VIEW["Real-Time Views"]
        B_VIEW & S_VIEW --> QUERY_L["Hybrid Query Engine"]
    end

    subgraph KappaArch["Kappa Architecture (Unified Stream Pipeline)"]
        SRC_K["Raw / Historical Log (Kafka/S3)"] --> STREAM_K["Single Stream Processing Engine (Flink)"]
        STREAM_K --> VIEW_K["Real-Time Views (Cassandra / ClickHouse)"]
        VIEW_K --> QUERY_K["Unified Query Engine"]
    end
```

#### Why Kappa Architecture is Selected
- **Lambda Architecture** forces the maintenance of **two separate codebases** (e.g., Spark SQL for batch and Flink for streaming) to compute identical business logic, inevitably leading to code drift and reconciliation discrepancies.
- **Kappa Architecture** uses **one unified stream processing engine** for both live incoming events and historical reprocessing.

---

### 2. Historical Data Recalculation (Replay Flow)

When an aggregation bug is patched or an advertiser requests a historical audit, the system replays historical raw logs without interrupting real-time live ingestion:

```mermaid
sequenceDiagram
    autonumber
    participant S3 as Cold Storage (S3 Raw Logs)
    participant Recalc as Recalculation Service
    participant Stream as Dedicated Flink Sub-Cluster
    participant K2 as Kafka Topic 2 (Aggregated)
    participant DB as Aggregated Database

    Note over Recalc,Stream: Isolated from production stream
    Recalc->>S3: Read historical raw data for time range [T_start, T_end]
    Recalc->>Stream: Stream historical chunks into aggregator
    Stream->>Stream: Apply patched aggregation logic
    Stream->>K2: Output corrected aggregated counts
    K2->>DB: Upsert / Overwrite corrupted time windows
    Note over DB: Corrected state available to dashboards
```

---

### 3. Time Semantics & Watermarking for Late Events

#### Event Time vs. Processing Time

```mermaid
flowchart LR
    E["Event Occurs on Client<br/>(Event Time: 12:00:00)"] -->|Network Lag / Queue Delay| S["Server Processes Event<br/>(Processing Time: 12:04:30)"]
```

| Criteria | Event Time | Processing Time |
|:---|:---|:---|
| **Definition** | Timestamp when the ad click occurred on the client device | System clock timestamp of the stream processing node |
| **Accuracy** | **High**; reflects actual user behavior | **Low**; distorted by network jitter and queue backpressure |
| **Handling Late Data** | Requires watermarking and window buffering | Trivial; no late events by definition |
| **Reliability Risk** | Client clocks may drift or be spoofed | Server NTP clocks are trusted |
| **Decision** | **✅ Recommended for ad billing** | ❌ Not acceptable for billing |

---

#### Handling Late Data with Watermarks

A **Watermark** is a progress metric in event-time processing that informs the system: *"We assume no more events with timestamp $\le t$ will arrive."*

```mermaid
flowchart TD
    subgraph W1["1-Minute Tumbling Window (12:00:00 - 12:01:00)"]
        E1["Event 1 (12:00:15)<br/>Arrives at 12:00:16<br/>[Included on time]"]
        E2["Event 2 (12:00:55)<br/>Arrives at 12:01:08 (Late)<br/>[Captured by Watermark Extension]"]
    end
    
    WM["Watermark Buffer Closes at 12:01:15 (+15s)"]
    
    subgraph W1_LATE["Out-of-Bounds Straggler Events"]
        E3["Event 3 (12:00:58)<br/>Arrives at 12:01:25 (Too Late)<br/>[Sent to DLQ / Batch Reconciliation]"]
    end

    W1 --> WM
    WM -->|Closes Window & Emits Aggregation| OUT["Emit Window Aggregate Count"]
    W1_LATE -.->|Dropped from Real-Time Stream| RECON["Batch Reconciliation Pipeline"]
```

```
Window [12:00 - 12:01] 
|-----------------------|===============> Watermark closes at 12:01:15
   Click at 12:00:50           ^
   Arrives at 12:01:05 --------+ (Accepted & Included in 12:00 window)

   Click at 12:00:55
   Arrives at 12:01:25 --------> (Rejected: Beyond Watermark -> Sent to Dead Letter Queue / Reconciliation)
```

> [!NOTE]
> **Watermark Trade-Off**: 
> - **Longer watermark buffer** (e.g., 60 seconds): Captures more straggler events $\rightarrow$ higher data accuracy, but increases end-to-end dashboard latency.
> - **Shorter watermark buffer** (e.g., 10 seconds): Lower latency, but misses late events. Missed events are caught by **daily batch reconciliation**.

---

### 4. Windowing Strategies

```mermaid
flowchart TD
    subgraph Tumbling["1. Tumbling (Fixed) Window — 1 Minute"]
        T1["[00:00 - 01:00] (Count: 120)"]
        T2["[01:00 - 02:00] (Count: 155)"]
        T3["[02:00 - 03:00] (Count: 90)"]
    end

    subgraph Sliding["2. Sliding Window — 5-Min Window, 1-Min Slide"]
        S1["[00:00 - 05:00] (Top N)"]
        S2["[00:01 - 05:01] (Top N)"]
        S3["[00:02 - 05:02] (Top N)"]
    end
```

1. **Tumbling (Fixed) Window**:
   - Non-overlapping, fixed-length intervals.
   - **Use Case**: Aggregating per-minute ad click counts.
2. **Sliding Window**:
   - Overlapping intervals that advance by a configurable slide step.
   - **Use Case**: Tracking *"Top 100 ads in the last 5 minutes, updated every 1 minute"*.

---

### 5. Delivery Guarantees & Exactly-Once Semantics

In advertising systems, duplicate processing directly causes **over-billing**, while dropped events cause **under-billing**. Exactly-once processing is mandatory.

```mermaid
flowchart TD
    subgraph ExactlyOncePipeline["End-to-End Exactly-Once Pipeline"]
        K1["Upstream Kafka<br/>(Transactional Producer)"] -->|"1. Idempotent Read with Offsets"| FLINK["Flink Stream Aggregator<br/>(Stateful Checkpointing)"]
        FLINK -->|"2. Two-Phase Commit (2PC)"| K2["Downstream Kafka<br/>(Aggregated Results)"]
        K2 -->|"3. Idempotent Upsert"| DB[("Cassandra / OLAP DB<br/>(Primary Key Deduplication)")]
    end
```

#### Why Standard Offset Commits Cause Duplicates or Data Loss

```mermaid
sequenceDiagram
    autonumber
    participant K1 as Upstream Kafka
    participant Agg as Stream Aggregator
    participant Ext as External Offset Store (S3)
    participant K2 as Downstream Kafka

    Note over Agg: Scenario A: Early Offset Commit (Data Loss)
    Agg->>K1: Read Offsets 100-110
    Agg->>Ext: Commit Offset 110 (BEFORE emitting results)
    Note over Agg: 💥 AGGREGATOR CRASHES!
    Note over Agg: New worker reads offset 110 -> Events 100-110 LOST!

    Note over Agg: Scenario B: Late Offset Commit (Duplicates)
    Agg->>K1: Read Offsets 100-110
    Agg->>K2: Emit Aggregated Result
    Note over Agg: 💥 AGGREGATOR CRASHES before offset 110 committed!
    Note over Agg: New worker re-reads from offset 100 -> Emits DUPLICATE results!
```

#### The Solution: Two-Phase Commit (2PC) & Idempotency
To achieve true end-to-end exactly-once:
1. **Source to Processing Engine**: Distributed snapshots using the **Chandy-Lamport algorithm** (Flink Checkpoints).
2. **Processing Engine to Downstream Queue**: Flink uses Kafka's **Transactional Producer API** with Two-Phase Commit (`2PC`):
   - *Pre-commit*: Write aggregated data into Kafka transaction during snapshot.
   - *Commit*: Mark Kafka transaction as committed only after checkpoint succeeds.
3. **Downstream Queue to DB Sink**: Idempotent upsert operations in the storage engine using deterministic natural primary keys (`ad_id + click_minute + filter_id`).

---

### 6. Scalability & Hotspot Mitigation

#### Scaling the Message Queue (Kafka)
- **Partition Key**: Partition by `hash(ad_id)`. All events for a specific ad land in the same partition, enabling clean in-memory accumulation.
- **Physical Topic Sharding**: Split large traffic streams across regional topics (e.g., `ad_clicks_us`, `ad_clicks_eu`) to limit the impact of partition rebalances.

```mermaid
flowchart TD
    subgraph HotspotProblem["Hotspot Scenario (Popular Ad)"]
        A_HOT["Ad #999 (Superbowl Ad)<br/>30,000 Clicks/sec"] --> P0["Partition 0<br/>(Overloaded Node!)"]
        A_NORM["Ad #001 (Regular Ad)<br/>5 Clicks/sec"] --> P1["Partition 1<br/>(Idle Node)"]
    end
```

#### Mitigating Hotspots: Two-Stage (Global-Local) Aggregation

When a viral ad generates thousands of clicks per second, a single partition node will bottleneck. We solve this using **Two-Stage Aggregation**:

```mermaid
flowchart TD
    subgraph Stage1["Stage 1: Local Pre-Aggregation (Salted Keys)"]
        E["Raw Click for Ad #999"] --> SALT["Add Salt: hash(ad_id) % 3<br/>Keys: ad999_0, ad999_1, ad999_2"]
        SALT --> L1["Local Aggregator 0<br/>(ad999_0 -> Count: 10,000)"]
        SALT --> L2["Local Aggregator 1<br/>(ad999_1 -> Count: 10,000)"]
        SALT --> L3["Local Aggregator 2<br/>(ad999_2 -> Count: 10,000)"]
    end

    subgraph Stage2["Stage 2: Global Merge"]
        L1 & L2 & L3 --> G["Global Aggregator Node<br/>(Sum: 10k + 10k + 10k = 30,000)"]
        G --> OUT["Write final ad999 Count to Sink"]
    end
```

---

### 7. Fault Tolerance & State Recovery

Stream aggregators maintain stateful windows in memory. If a worker node crashes:

```mermaid
sequenceDiagram
    autonumber
    participant K as Kafka Broker
    participant Snap as Distributed Snapshot (HDFS/S3)
    participant NodeNew as New Aggregator Worker

    Note over Snap: Flink periodically saves checkpoints<br/>(Kafka Offset + Window State + Heap)
    Note over NodeNew: Worker crashes -> Cluster brings up new container
    NodeNew->>Snap: 1. Load state from last verified checkpoint (e.g., Offset: 500,000)
    NodeNew->>K: 2. Request replay from Offset 500,001
    K-->>NodeNew: 3. Stream catch-up delta events
    NodeNew->>NodeNew: 4. Reconstruct in-memory window state
    Note over NodeNew: Ready & processing live stream in sync
```

---

### 8. System Monitoring & Daily Batch Reconciliation

```mermaid
flowchart TD
    subgraph RealTime["Real-Time Streaming Path"]
        LIVE["Kafka Ingestion"] --> FLINK["Flink Stream Aggregator"]
        FLINK --> STREAM_DB[("Real-Time Aggregations")]
    end

    subgraph BatchReconcile["Daily Offline Batch Reconciliation"]
        S3_RAW[("S3 Raw Parquet Logs")] --> SPARK["Spark Batch Job<br/>(Sort by Event Time & Compute Daily Rollup)"]
        SPARK --> BATCH_DB[("Reconciled Batch View")]
    end

    STREAM_DB & BATCH_DB --> RECON["Reconciliation Comparator"]
    RECON -->|"Diff > Threshold"| ALERT["🚨 Discrepancy Alert & Financial Audit"]
    RECON -->|"Diff == 0 or within noise"| OK["✅ Daily Billing Ledger Certified"]
```

#### Critical Operational Metrics
1. **Event Latency Lag**: Difference between `processing_time` and `event_time`. Spikes indicate upstream network lag or queue build-up.
2. **Kafka Consumer Lag (`records-lag-max`)**: Measures backlog growth. Triggers auto-scaling of Flink task slots.
3. **JVM Memory & Garbage Collection**: High memory pressure inside stream operators indicates excessive window sizes or watermark delays.

---

### 9. Alternative Architecture: Real-Time OLAP Engine

An alternative industry-standard pattern avoids custom aggregation code by streaming raw events directly into a distributed real-time OLAP database:

```mermaid
flowchart LR
    APP["App Servers"] --> K["Kafka Topic"]
    K --> OLAP[("Real-Time OLAP Engine<br/>(ClickHouse / Apache Pinot)")]
    K -.-> ARCHIVE[("S3 Deep Archive")]
    OLAP --> API["Query Service / SQL Dashboards"]
```

#### Trade-Off Comparison
| Feature | Custom Stream DAG (Flink + Cassandra) | Real-Time OLAP (Kafka + ClickHouse / Pinot) |
|:---|:---|:---|
| **Architecture Complexity** | Higher (requires custom DAG operators and 2PC sinks) | **Lower** (Kafka connects directly to ClickHouse tables) |
| **Ad-Hoc Query Flexibility** | Low (only pre-defined dimensions in Star Schema) | **Extremely High** (full SQL slicing across any dimension) |
| **Write Throughput** | Highest (pre-aggregated before DB write) | Very high (vectorized column inserts) |
| **Resource Cost** | Low storage footprint | Higher memory and CPU for indexing |

---

## 4. Summary & Architecture Wrap-Up

```mermaid
flowchart TD
    subgraph SummaryGrid["Ad Click Event Aggregation Summary"]
        direction TB

        C1["Scalability: Partition by hash(ad_id) + Two-stage salting for hotspots"]
        C2["Correctness: Event-time windowing + 15s Watermark + End-to-end 2PC exactly-once"]
        C3["Fault Tolerance: Chandy-Lamport state checkpointing + Deterministic Kafka replay"]
        C4["Storage: S3 Parquet for raw backup + Cassandra/ClickHouse for aggregated rollups"]
        C5["Integrity: End-of-day Spark batch reconciliation against raw event logs"]
    end
```

### Architectural Decisions Matrix

| Challenge | Chosen Solution | Rationale & Trade-Off |
|:---|:---|:---|
| **High Write Scale ($50\text{K}\text{ QPS}$)** | Asynchronous Kafka decoupling + Flink stream aggregation | Prevents backpressure crashes and scales consumers independently |
| **Data Correctness for Billing** | Event-time processing with watermark extensions | Mitigates client clock skew and out-of-order deliveries |
| **Duplicate Prevention** | Two-Phase Commit (2PC) + Idempotent DB upserts | Ensures exact financial figures without double charging |
| **Celebrity Ad Hotspots** | Two-stage (Global-Local) salted pre-aggregation | Distributes write spikes across multiple workers |
| **Data Recalculation** | Kappa Architecture with dedicated historical replay worker | Enables instant bug fixes and auditing using the same codebase |
| **Data Audit & Integrity** | End-of-day offline Spark batch reconciliation | Reconciles edge-case late events and verifies ledger accuracy |

---

## Reference Materials

1. **Clickthrough Rate (CTR)**: [Google Ads Help](https://support.google.com/google-ads/answer/2615875?hl=en)
2. **Display Advertising with RTB and Behavioral Targeting**: [ArXiv Research](https://arxiv.org/pdf/1610.03013.pdf)
3. **Apache Flink End-to-End Exactly-Once Processing**: [Apache Flink Documentation](https://flink.apache.org/features/2018/03/01/end-to-end-exactly-once-apache-flink.html)
4. **Star Schema in Dimensional Modeling**: [Microsoft Architecture Guide](https://docs.microsoft.com/en-us/power-bi/guidance/star-schema)
5. **Martin Kleppmann**: *Designing Data-Intensive Applications*. O'Reilly Media, 2017.
6. **Yelp Ad Stream Aggregation Architecture**: [Yelp Engineering](https://www.youtube.com/watch?v=hzxytnPcAUM)
7. **Uber Real-Time Exactly-Once Ad Processing with Flink & Pinot**: [Uber Engineering](https://eng.uber.com/real-time-exactly-once-ad-event-processing/)
8. **ClickHouse Architecture Overview**: [ClickHouse Docs](https://clickhouse.com/docs)
