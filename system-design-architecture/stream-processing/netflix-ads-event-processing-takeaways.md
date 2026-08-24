---
type: System Design
title: "Netflix Ads Event Processing Pipeline — Key Takeaways"
description: "Architectural takeaways from Netflix's Ads Event Processing Pipeline across VOD and Live: transient KV registries, Flink stream sessionization, stateful stream-stream joins, route-to-data cross-region forwarding, in-stream deduplication, and shadow canary migrations."
timestamp: 2026-08-23T00:00:00Z
---

# Netflix Ads Event Processing Pipeline — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)  
> **Source**: [Part I: Building a Robust Ads Event Processing Pipeline](../../articles/stream-processing/netflix-ads-event-processing-pipeline.md), [Part II: Evolving Netflix's Ads Event Pipeline for Live](../../articles/stream-processing/netflix-ads-event-pipeline-live.md)  
> **Related**: [Stream Processing (Apache Flink)](stream-processing-flink.md), [Async & Concurrency Patterns](async-concurrency-patterns.md), [Message Brokers & Async](../messaging/message-brokers-async.md)  
> **Dictionary**: [Stream-Stream Join](../../reference-dictionary/messaging.md#stream-stream-join), [In-Stream Keyed Deduplication](../../reference-dictionary/messaging.md#in-stream-keyed-deduplication), [Stream Sessionization](../../reference-dictionary/messaging.md#stream-sessionization), [Route-to-Data Pattern](../../reference-dictionary/architecture-patterns.md#route-to-data-pattern), [Deterministic Traffic Dialing](../../reference-dictionary/deployment-patterns.md#deterministic-traffic-dialing), [Server-Side Ad Insertion (SSAI)](../../reference-dictionary/media-processing.md#server-side-ad-insertion-ssai), [Frequency Capping](../../reference-dictionary/architecture-patterns.md#frequency-capping), [Apache Flink](../../reference-dictionary/messaging.md#apache-flink)  
> **Azure Services**: [Azure Stream Analytics](../../architecture-azure/data/), [Event Hubs](../../architecture-azure/integration/), [Azure Cache for Redis](../../architecture-azure/databases/)  
> **Taxonomy Reference**: §3.3 Event-Driven & Messaging, §4.2 Stream Analytics & Real-Time Processing

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`flink-06`](#flink-06-client-side-token-bloat-vs-transient-kv-metadata-registry) | Client-side opaque token bloat under expanding 3P trackers | Transient KV Metadata Registry (Reference Token Pattern) |
| [`flink-07`](#flink-07-disparate-upstream-telemetry-vs-downstream-consumer-coupling) | Disparate upstream telemetry formats break downstream consumers | Centralized Ad Event Publisher with canonical data contracts |
| [`flink-08`](#flink-08-fragmented-event-lifecycles-vs-session-aggregation) | Fragmented, asynchronous ad lifecycle telemetry | Apache Flink Stream Sessionizer for stateful session assembly |
| [`flink-09`](#flink-09-high-latency-feedback-leads-to-ad-over-delivery) | High-latency feedback causes frequency capping violations | Near real-time streaming feedback loop to Ad Server |
| [`flink-10`](#flink-10-streaming-olap-speed-vs-financial-billing-accuracy) | Speed-layer OLAP trade-offs clash with strict billing precision | Dual-track streaming (Flink + Druid) and offline reconciliation |
| [`flink-11`](#flink-11-synchronous-kv-metadata-writes-vs-in-stream-stream-stream-join) | Critical path database write bottleneck during live event traffic surges | Asynchronous Kafka logging & Flink `KeyedCoProcessFunction` join |
| [`flink-12`](#flink-12-full-state-cross-region-replication-vs-route-to-data-event-forwarding) | Wasteful global replication of ephemeral ad decisions across regions | Route-to-Data Pattern: origin-tagged tokens and cross-region forwarding |
| [`flink-13`](#flink-13-infinite-stateful-window-bloat-vs-tiered-bounded-ttl--offline-batch-recovery) | Unbounded stream join state causes large checkpoints and recovery lag | 60-min Flink state TTL paired with hourly Spark/Maestro offline recovery |
| [`flink-14`](#flink-14-external-db-check-and-write-races-vs-keyed-local-state-in-stream-deduplication) | Remote database check-and-write races during high-concurrency event deduplication | Deterministic hash ID partitioning with Flink local in-operator state |
| [`flink-15`](#flink-15-flag-day-cutover-risk-vs-deterministic-hash-keyed-dual-run-canary-dialing) | Catastrophic downtime and revenue risk during revenue pipeline migration | Dual-run shadow auditing with deterministic hash-keyed canary dials |

---

## flink-06: Client-Side Token Bloat vs Transient KV Metadata Registry

| | |
|:---|:---|
| **Problem** | Passing complete tracking metadata, verification URLs, and third-party measurement parameters inside client-cached opaque tokens causes token payload size to grow drastically. On memory-constrained devices (smart TVs, streaming dongles), this risks elevated heap usage, performance degradation, and excessive mobile data consumption. |
| **Root cause** | Coupling tracking metadata persistence directly to the client runtime via self-contained encrypted tokens instead of referencing metadata server-side. |

**Strategy — Transient Key-Value Metadata Registry & Reference Token Pattern**:

```
[Ad Decision Time]
Ad Server / Manager ----> Writes Full Metadata (3P URLs, IDs, Pricing) ----> [Transient KV Registry (Redis / KV)]
         |                                                                                  ^
         +----> Emits Small Reference Token (Ad ID, Record ID, Event Name)                  |
                     |                                                                      |
                     v                                                                      |
             [Client Device]                                                                |
                     | (Sends Callback with Small Token)                                    |
                     v                                                                      |
             [Event Handler] ---------------- Hydrates Full Metadata -----------------------+
                     |
                     +----> Dispatches to External 3P Verification (IAS, DV, Nielsen)
```

1. **Decouple Payload from Token**: Store full tracking metadata in a low-latency, transient Key-Value store with TTL upon ad decision generation.
2. **Reference Identifiers**: Issue client devices lightweight tokens containing only minimal reference keys (`ad_id`, `metadata_record_id`, `event_type`).
3. **Asynchronous Hydration**: When the client reports playback progress (e.g., impression, midpoint), the event handler retrieves the full tracking record from the KV store and executes external vendor calls asynchronously.

**Tradeoff**: Introduces an additional network hop and read dependency on the transient KV store during event ingestion; requires proper cache sizing and TTL policies matching the maximum playback session window.

> **Azure**: Store transient ad metadata in **Azure Cache for Redis** or **Cosmos DB with TTL**; client devices pass lightweight session references.  
> **General**: [Claim Check Pattern](../../architecture-general/03-integration-communication-architecture/messaging-patterns/claim-check.md), [Reference Token Pattern](../../reference-dictionary/architecture-patterns.md#transient-metadata-registry)

---

## flink-07: Disparate Upstream Telemetry vs Downstream Consumer Coupling

| | |
|:---|:---|
| **Problem** | Introducing new advertising formats (video ads, pause ads, display banners, live-stream ads) introduces distinct upstream logging frameworks and schemas. Allowing downstream consumers (billing, reporting, metrics, frequency capping) to directly consume raw client telemetry tightly couples business logic to transport schemas, leading to fragile migrations and duplicated decryption/enrichment logic. |
| **Root cause** | Lack of an anti-corruption layer / canonical data contract between heterogeneous client telemetry ingestion and downstream domain consumers. |

**Strategy — Centralized Ad Event Publisher with Canonical Data Contracts**:

```
[ Video Telemetry ]   [ Display Ads Logs ]   [ Pause Ads Logs ]   [ Live Stream Events ]
         \                     |                     /                     /
          \                    |                    /                     /
           v                   v                   v                     v
      +-----------------------------------------------------------------------+
      |                          Ads Event Publisher                          |
      |   - Token Decryption        - GDPR / Privacy Opt-Out Enforcement      |
      |   - Identifier Hashing      - Canonical Protobuf Schema Normalization |
      +-----------------------------------------------------------------------+
                                           |
                                           v
                       Canonical Event Stream (Apache Kafka)
                                           |
         +--------------------+------------+------------+--------------------+
         |                    |                         |                    |
         v                    v                         v                    v
  [Frequency Capping]   [Ads Metrics (Flink)]   [Ads Sessionizer]    [Ads Event Handler]
```

1. **Centralized Consolidation**: Consolidate repetitive tasks—token decryption, identifier hashing, device enrichment, and privacy/GDPR opt-out filtering—into a single publisher tier.
2. **Canonical Protobuf Schema**: Define a unified, media-agnostic Protocol Buffers data contract that represents ad domain events consistently regardless of source format.
3. **Strict Downstream Isolation**: Downstream systems consume exclusively from the canonical stream, remaining entirely isolated from upstream transport changes or client SDK updates.

**Tradeoff**: The centralized publisher represents a critical aggregation point requiring high availability, massive throughput scaling, and strict backward/forward schema compatibility governance.

> **Azure**: Ingest varied telemetry via **Azure Event Hubs**, normalize via an **Azure Function** or **AKS Event Publisher microservice**, and emit canonical events to downstream topics.  
> **General**: [Canonical Data Model](../../architecture-general/03-integration-messaging-architecture/messaging-patterns/canonical-data-model.md), [Anti-Corruption Layer](../../reference-dictionary/architecture-patterns.md#anti-corruption-layer)

---

## flink-08: Fragmented Event Lifecycles vs Session Aggregation

| | |
|:---|:---|
| **Problem** | Ad playback generates numerous discrete, asynchronous telemetry events over time (`impression`, `start`, `first_quartile`, `midpoint`, `third_quartile`, `complete`, `pause`, `resume`, `click`, `qr_scan`). Downstream analytics, fraud detection, and advertiser reporting require a holistic view of the entire ad viewing session rather than individual detached events. |
| **Root cause** | High-velocity streaming telemetry is point-in-time, whereas analytical decisioning and business reporting are session-oriented. |

**Strategy — Apache Flink Stateful Stream Sessionization**:

```
Raw Telemetry Events (Kafka)
[Impression] ---> [Start] ---> [Q1] ---> [Midpoint] ---> [Q3] ---> [Complete] ---> [Click]
                                      |
                                      v
                      +-------------------------------+
                      |   Apache Flink Sessionizer    |
                      |   (Keyed State by Session ID)  |
                      |   - Window Gap / Activity TTL |
                      |   - Out-of-Order Handling     |
                      |   - State Checkpointing (ABS) |
                      +-------------------------------+
                                      |
                                      v
                      Unified Ad Session Record (Rich Object)
         { ad_id, campaign_id, duration_watched, quartiles_hit: [1,2,3,4], clicked: true }
                                      |
                                      v
                      Downstream OLAP, Billing & Reporting
```

1. **Keyed State Aggregation**: An Apache Flink job partitions events by unique Ad Session ID, accumulating progress milestones and interaction flags in managed operator state.
2. **Session Windowing & Watermarks**: Use event-time watermarking and session gap timers to close windows and emit finalized, enriched session objects once playback completes or times out.
3. **Downstream Simplicity**: Analytical pipelines, impression verification, and reporting systems consume pre-aggregated session records instead of managing complex multi-event SQL joins over billions of raw rows.

**Tradeoff**: Maintaining state for millions of concurrent in-flight sessions requires substantial RocksDB / in-memory state storage in Flink and fine-tuned checkpointing configuration.

> **Azure**: **Azure Stream Analytics** with `SESSIONWINDOW` or self-managed **Apache Flink on AKS / HDInsight** writing aggregated sessions to **Azure Data Lake Storage** / **Synapse Analytics**.  
> **General**: [Stream Sessionization](../../reference-dictionary/messaging.md#stream-sessionization), [Windowing Patterns](stream-processing-flink.md#flink-04-windowing--aggregating-infinite-streams)

---

## flink-09: High-Latency Feedback Leads to Ad Over-Delivery

| | |
|:---|:---|
| **Problem** | Advertisers enforce strict frequency capping (e.g., "show ad at most 2 times per 24 hours per user profile") and campaign budget limits. If ad serving decisions rely on batch or high-latency event processing, recent impressions are not visible in time, causing users to see duplicate ads, violating advertiser policies, and burning campaign budgets prematurely. |
| **Root cause** | Open-loop ad decisioning where serving engines lack real-time feedback from downstream event rendering. |

**Strategy — Closed-Loop Real-Time Streaming Feedback**:

```
                                  +-----------------------+
                                  |    Netflix Ad Server  | <==== Queries Frequency State
                                  |   (Decision "Brain")  |       during Ad Break Decision
                                  +-----------------------+
                                              ^
                                              | Real-Time Feedback Loop
                                              | (In-Memory Counters)
                                  +-----------------------+
                                  |   Frequency Capping   |
                                  |   Consumer Service    |
                                  +-----------------------+
                                              ^
                                              | Near-Real-Time Stream (<1s)
                                  +-----------------------+
                                  |  Ads Event Publisher  |
                                  +-----------------------+
                                              ^
                                              | Telemetry
                                  +-----------------------+
                                  | Client Playback Event | (Heartbeat)
                                  +-----------------------+
```

1. **Closed-Loop Feedback**: Ad events act as "heartbeats" providing immediate feedback to the ad decision "brain".
2. **Sub-Second Stream Ingestion**: The Ad Event Publisher routes impression events to a dedicated real-time Frequency Capping consumer via Kafka.
3. **In-Memory Rolling State**: The Frequency Capping service maintains low-latency distributed counters (keyed by `campaign_id:profile_id:time_window`) which the Ad Server inspects before every ad selection decision.

**Tradeoff**: High-throughput distributed counter state must be fast and highly available; in the event of consumer lag or network isolation, the system must fail-safe (e.g., pessimistic capping or graceful degradation) without halting ad delivery.

> **Azure**: Stream impression events through **Azure Event Hubs** to **Azure Cache for Redis** rolling counters queried by the ad serving API with sub-millisecond latency.  
> **General**: [Real-Time Feedback Loop](../../reference-dictionary/architecture-patterns.md#frequency-capping), [Redis Rolling Window Rate Limiter](../../reference-dictionary/caching.md#sliding-window-rate-limiting)

---

## flink-10: Streaming OLAP Speed vs Financial Billing Accuracy

| | |
|:---|:---|
| **Problem** | Real-time stream processing engines can experience transient network glitches, client retry duplicates, out-of-order deliveries, or minor dropouts. While streaming is ideal for real-time campaign pacing, relying solely on real-time streaming counts for advertiser billing risks invoicing discrepancies and audit failures. |
| **Root cause** | Speed-layer OLAP systems prioritize low latency and dimensional slicing over immutable financial auditability and late-arriving reconciliation. |

**Strategy — Dual-Track Streaming OLAP & Offline Billing Reconciliation**:

```
                             Canonical Ads Event Stream
                                          |
                   +----------------------+----------------------+
                   |                                             |
                   v (Fast Speed Layer)                          v (Accurate Batch Layer)
        +----------------------+                      +----------------------+
        | Apache Flink Job     |                      | Durable Raw Storage  |
        +----------------------+                      | (Data Lake / S3)     |
                   |                                  +----------------------+
                   v                                             |
        +----------------------+                      +----------------------+
        | Apache Druid (OLAP)  |                      | Offline Spark / ETL  |
        +----------------------+                      | Curation & Dedup     |
                   |                                  +----------------------+
                   v                                             |
        [Live Campaign Health]                                   v
        [Budget Pacing Alerts]                        [Financial Billing &   ]
        [Real-Time Dashboards]                        [Revenue Recognition   ]
                   ^                                             |
                   |============= Offline Correction ============|
```

1. **Fast-Path Streaming (Flink → Druid)**: Stream real-time dimensions and metrics into an OLAP engine (Apache Druid) for sub-minute advertiser health reporting, delivery monitoring, and budget capping.
2. **Authoritative Offline Curation**: Concurrently persist immutable raw events to data lake storage. Scheduled batch workflows (Spark / Trino) perform multi-pass deduplication, complex contractual pricing rules, and compliance curation.
3. **Backfill & Reconciliation**: The curated offline dataset backfills and corrects any streaming ingestion anomalies in the OLAP store, ensuring operational dashboards and audited financial invoices converge to 100% agreement.

**Tradeoff**: Operating both streaming (Flink + Druid) and batch (Spark + Data Lake) pipelines increases infrastructure and maintenance complexity; reconciliation processes must be idempotent and automated.

> **Azure**: **Azure Stream Analytics** into **Azure Data Explorer (Kusto)** for real-time OLAP dashboards, paired with **Azure Synapse / Databricks** scheduled batch pipelines writing curated billing records to **Azure Data Lake Storage Gen2**.  
> **General**: [Lambda / Kappa Hybrid Architecture](stream-processing-flink.md#flink-01-lambda-architecture--two-systems-two-codebases), [Medallion Architecture](../../reference-dictionary/data-architecture.md#medallion-architecture)

---

## flink-11: Synchronous KV Metadata Writes vs In-Stream Stream-Stream Join

| | |
|:---|:---|
| **Problem** | During live event broadcasts (such as NFL games or blockbuster fight nights with 100M+ viewers), commercial breaks trigger instant bursts of millions of concurrent ad serving decisions and telemetry events. Writing full ad impression metadata synchronously to a key-value store (the Metadata Registry) on the ad-serving critical path creates an unmanageable database write bottleneck. An outage, latency spike, or throttling event on the datastore directly halts ad serving, causing dropped ads and massive revenue loss. Furthermore, database clusters cannot be safely scaled up mid-event due to partition reshuffling overhead. |
| **Root cause** | Coupling synchronous datastore persistence to the ad-serving hot path instead of decoupling metadata emission via asynchronous log streams and joining them downstream. |

**Strategy — Asynchronous Kafka Logging & Stateful Flink Stream-Stream Join**:

```
[Ad Serving Hot Path]
Ad Server ── (1. Logs Decision Context) ──► Kafka: `ad-decisions` Topic (Fire & Forget)
    │
    ▼ (2. Emits Minimal Token)
Client Device ── (3. Fires Playback Heartbeat) ──► Kafka: `ad-events` Topic
                                                          │
          ┌───────────────────────────────────────────────┘
          │
          ▼
+───────────────────────────────────────────────────────────────────────────+
|                 Apache Flink `KeyedCoProcessFunction` Join                |
|                                                                           |
|   - Keyed by `impression_id`                                              |
|   - Decision arrives first: Store in ValueState (TTL = 60 min)            |
|   - Client event arrives: Match against ValueState -> Emit Enriched Event |
|   - Client event arrives first: Buffer in ListState -> Wait for Decision  |
+───────────────────────────────────────────────────────────────────────────+
                                  │
                                  ▼
                    Enriched Canonical Event Stream
```

1. **Remove Database from Critical Path**: The ad serving engine makes the placement decision, emits a minimal opaque token to the device, and publishes the full decision context asynchronously to a Kafka decision topic. Ad serving never waits on a database write acknowledgment.
2. **Stateful Stream-Stream Join**: An Apache Flink streaming job implements a custom `KeyedCoProcessFunction` partitioned by unique impression ID. When the ad decision arrives, Flink stores it in managed operator state with a 60-minute TTL.
3. **In-Stream Enrichment**: When client playback heartbeats (start, first quartile, midpoint, complete) arrive, Flink matches them in-memory against the stored decision state and outputs enriched canonical ad events in near-real-time (<1 second).

**Tradeoff**: Eliminates database writes as a single point of failure on the ad-serving hot path and enables elastic scaling. However, requires managing stateful streaming infrastructure, operator state TTL policies, and out-of-order stream buffering.

> **Azure**: Ad serving microservices on **AKS** log decisions to **Azure Event Hubs**; **Azure Stream Analytics** (with temporal joins) or **Apache Flink on AKS** matches decisions with device telemetry and writes to downstream event hubs.  
> **General**: [Stream-Stream Join](../../reference-dictionary/messaging.md#stream-stream-join), [Read/Write Path Separation](../../reference-dictionary/architecture-patterns.md#readwrite-path-separation)

---

## flink-12: Full-State Cross-Region Replication vs Route-to-Data Event Forwarding

| | |
|:---|:---|
| **Problem** | In multi-region deployments, client devices may switch networks mid-stream (e.g., connected via home Wi-Fi in `us-east-1` when an ad is decided, then switching to cellular data in `us-west-2` during playback). In a streaming architecture, the ad decision log resides in the serving region's local Kafka cluster. Replicating all ad decision logs globally across every region so that any region can join locally consumes massive WAN bandwidth, creates redundant storage/compute worldwide, and is overwhelmingly wasteful since >99% of events never roam. |
| **Root cause** | Relying on brute-force global data replication rather than smart origin-aware event routing for the small minority of cross-region telemetry events. |

**Strategy — Route-to-Data Pattern (Origin-Tagged Forwarding)**:

```
    Region: us-west-2 (Client Landed)                 Region: us-east-1 (Ad Served)
+────────────────────────────────────+             +────────────────────────────────────+
| 1. Client Event arrives with token |             | Ad Server logs Decision to Kafka   |
|    Token payload:                  |             | (Decision stored in Flink state)   |
|      { "ad_id": "xyz",             |             |                                    |
|        "orig_region": "us-east-1" }|             |                                    |
|                                    |             |                                    |
| 2. Ingestion Router inspects tag   |             |                                    |
| 3. Forwards event via Kafka WAN    | ──────────► | 4. Receives forwarded event        |
|    to us-east-1 router             |             | 5. Executes local Flink join       |
+────────────────────────────────────+             +────────────────────────────────────+
```

1. **Origin Tagging in Token**: When generating the opaque ad token, the ad server embeds the originating serving region identifier into the token metadata.
2. **Edge Region Inspection**: When a client event arrives at any regional ingress gateway, the router inspects the token's origin region tag.
3. **WAN Forwarding**: If the current region matches the origin region, the event is processed locally. If the event landed in a foreign region, the gateway forwards the client event across the inter-region backbone to the origin region where its matching ad decision state already resides.

**Tradeoff**: Replaces multi-region continuous state replication with an event-driven WAN forwarding hop. Only the small fraction (~0.1%) of roaming client events pays the network hop, reducing inter-region data transfer costs by >99%. Requires reliable inter-region broker forwarding pipelines.

> **Azure**: Regional **Azure API Management** or **Event Hubs** ingress gateways inspect origin metadata in tokens and forward cross-region traffic over the **Azure Global Backbone Network** to the originating region's Event Hub.  
> **General**: [Route-to-Data Pattern](../../reference-dictionary/architecture-patterns.md#route-to-data-pattern), [Message Routing](../../reference-dictionary/messaging.md#message-ordering)

---

## flink-13: Infinite Stateful Window Bloat vs Tiered Bounded TTL & Offline Batch Recovery

| | |
|:---|:---|
| **Problem** | Retaining stream join state indefinitely to accommodate extreme late-arriving telemetry (e.g., offline playback resumed hours later, user-paused playback, or delayed third-party engagement beacons) causes Flink RocksDB state size to grow uncontrollably. Massive state size leads to slow checkpointing, longer failover recovery times, high memory pressure, and potential job stalls during live event traffic spikes. |
| **Root cause** | Attempting to solve 100% of edge-case late arrivals within the low-latency streaming layer instead of bounding stream state and offloading the long tail to batch processing. |

**Strategy — Tiered Ingestion Architecture (Bounded Stream TTL + Batch Reconciliation)**:

```
+────────────────────────────────────────────────────────────────────────────────────+
|                               Tiered Ingestion Architecture                        |
|                                                                                    |
|  [ Real-Time Stream (99.999%) ]                     [ Long-Tail Offline (0.001%) ] |
|                                                                                    |
|     Kafka Live Events + Decisions                         Unmatched / DLQ Events   |
|                 │                                                   │              |
|                 ▼                                                   ▼              |
|     +────────────────────────+                             +─────────────────────+ |
|     │ Apache Flink Join      │                             │ Hourly Spark Batch  │ |
|     │ (60-Min In-Memory TTL) │                             │ (Maestro Workflow)  │ |
|     +────────────────────────+                             +─────────────────────+ |
|                 │                                                   │              |
|                 │ Real-Time Output                                  │ Repaired     |
|                 ▼                                                   ▼              |
|    ════════════════════════════ Canonical Event Sinks ════════════════════════════ |
+────────────────────────────────────────────────────────────────────────────────────+
```

1. **Bounded Streaming Window**: Configure the Flink join state with a lean 60-minute TTL. This covers >99.999% of all live and on-demand ad events, keeping operator state small and checkpoints lightweight.
2. **Dead-Letter State Flushing**: Events whose matching decision does not arrive within the 60-minute window expire from Flink state and are routed to an Unmatched / Dead-Letter Queue (DLQ) in data lake storage (S3/ADLS).
3. **Offline Batch Long-Tail Recovery**: An hourly **Apache Spark** batch job, orchestrated by **Maestro**, joins unmatched events against historical ad decision logs stored permanently in the data warehouse. Repaired records are published to downstream canonical sinks.

**Tradeoff**: Retains sub-second checkpointing and high throughput in the real-time streaming pipeline. The 0.001% long tail experiences an hourly processing delay, which is fully acceptable for financial accounting and historical reporting.

> **Azure**: **Azure Stream Analytics** with 60-minute window writes unmatched/expired records to **Azure Data Lake Storage Gen2**; a scheduled **Azure Synapse / Databricks Spark job** performs long-tail joining and reconciles downstream billing datasets.  
> **General**: [Lambda / Kappa Hybrid Architecture](stream-processing-flink.md#flink-01-lambda-architecture--two-systems-two-codebases), [Dead Letter Queue (DLQ)](../../reference-dictionary/messaging.md#dead-letter-queue-dlq)

---

## flink-14: External DB Check-and-Write Races vs Keyed Local State In-Stream Deduplication

| | |
|:---|:---|
| **Problem** | At-least-once streaming delivery and client-side retry mechanisms inevitably produce duplicate ad playback events. For revenue-bearing events feeding advertiser billing, duplicate processing causes erroneous over-billing. In legacy systems, checking and recording seen event IDs against an external database for every event causes high read/write network latency, datastore contention, and race conditions under concurrent traffic spikes. |
| **Root cause** | Relying on remote database roundtrips for deduplication on the hot ingestion path rather than utilizing local, partitioned stream operator state. |

**Strategy — Deterministic In-Stream Deduplication with Keyed Local State**:

```
Client Playback Event ──► Hash ID Generation: MD5(ad_id + event_type + offset)
                                 │
                                 ▼
                     Flink `keyBy(hash_id)`
                                 │
                 +───────────────┴───────────────+
                 │                               │
                 ▼                               ▼
     [Flink Task Slot A]             [Flink Task Slot B]
     - Local State Store (TTL 10m)   - Local State Store (TTL 10m)
     - If hash_id in state: DROP     - If hash_id in state: DROP
     - If new: ADD to state & EMIT   - If new: ADD to state & EMIT
```

1. **Deterministic Event Hashing**: For each event, compute a stable, unique hash identifier derived from immutable fields: `Hash(ad_id, event_type, playback_offset)`.
2. **Keyed Local State Routing**: Flink keys the stream by this hash ID (`keyBy(event_hash)`). All duplicate copies of an event are deterministically routed to the same operator instance.
3. **In-Operator State Lookup**: The operator checks a local state store with a short TTL (e.g., 10 minutes). If seen, the duplicate is dropped immediately with zero network overhead and zero concurrency race conditions.
4. **End-to-End Idempotency**: The stable hash ID is propagated in the enriched output event, allowing downstream batch systems (e.g., billing databases) to enforce secondary idempotent upserts across multi-day windows.

**Tradeoff**: Eliminates external database overhead and race conditions on the hot path. While in-stream state drops >99.99% of duplicates, rare cross-region re-routes or job crash replays may emit duplicates beyond the short TTL window; downstream financial consumers must remain idempotent.

> **Azure**: Partition events by hash key in **Azure Stream Analytics** or **Flink on AKS** using in-memory state; write enriched events with stable transaction IDs into **Azure Cosmos DB** with idempotent document writes.  
> **General**: [In-Stream Keyed Deduplication](../../reference-dictionary/messaging.md#in-stream-keyed-deduplication), [Idempotent Consumer](../../reference-dictionary/messaging.md#idempotent-consumer)

---

## flink-15: Flag-Day Cutover Risk vs Deterministic Hash-Keyed Dual-Run Canary Dialing

| | |
|:---|:---|
| **Problem** | Migrating a revenue-critical, real-time pipeline (feeding advertiser billing, real-time pacing, and frequency capping) via an all-at-once "flag day" switchover carries immense risk of silent data corruption, billing discrepancies, and catastrophic downtime. Conversely, naive percentage-based traffic splits risk double-counting impressions if both pipelines publish the same event, or dropping impressions if routing fails. |
| **Root cause** | Migrating revenue-critical pipelines without deterministic traffic partitioning and side-by-side verification on 100% of live traffic. |

**Strategy — Dual-Run Shadow Auditing with Deterministic Canary Dialing**:

```
                           Live Production Event Stream
                                        │
                    +───────────────────┴───────────────────+
                    │                                       │
                    ▼                                       ▼
        +───────────────────────+               +───────────────────────+
        │ Legacy Pipeline       │               │ Flink Stream Pipeline │
        │ (Metadata Registry)   │               │ (Streaming Join)      │
        +───────────────────────+               +───────────────────────+
                    │                                       │
                    ├──────────► [ Automated Audit ] ◄──────┤
                    │            (Diff Comparison Engine)   │
                    │                                       │
        +───────────────────────────────────────────────────────────────+
        │ Deterministic Hash-Keyed Traffic Dial (0% ──► 100%)           │
        │ - Stable Key Hash: Hash(event_id) % 100                       │
        │ - If hash < Dial_Threshold: Flink publishes                   │
        │ - If hash >= Dial_Threshold: Legacy publishes                 │
        +───────────────────────────────────────────────────────────────+
                                        │
                                        ▼ Exactly-Once Authoritative Output
                             Downstream Consumers
```

1. **Shared Enrichment Logic**: Extract core event business and transformation logic into a shared common library imported by both legacy and Flink engines. This ensures diff audits identify only structural pipeline discrepancies rather than business rule divergence.
2. **Full Dual-Run Shadowing**: Feed 100% of live production traffic to both pipelines simultaneously. Both execute full enrichment logic in parallel without emitting to production sinks.
3. **Automated Continuous Audits**: An automated audit service continuously compares the output streams side-by-side, alerting on any discrepancies until parity exceeds 99.99%.
4. **Deterministic Hash-Keyed Traffic Dial**: To cut over without duplicate publishing, calculate a deterministic hash bucket: `Bucket = Hash(stable_event_key) % 100`. An event is published exclusively by Flink if `Bucket < Threshold`, and by Legacy otherwise.
5. **Gradual Staged Cutover**: Increment the dial threshold (0% → 1% → 10% → 50% → 100%) region by region. Any anomaly allows instant rollback by turning down the dial. Once fully verified at 100%, legacy infrastructure and database writes are completely decommissioned.

**Tradeoff**: Incurs temporary dual-running infrastructure compute costs during the rollout period, but achieves 100% zero-downtime, zero-data-loss migration for mission-critical financial systems.

> **Azure**: Ingest events into **Azure Event Hubs**, fan out to parallel consumer groups on **AKS** running legacy and modern services, compare outputs in an automated auditing function, and route authoritative outputs using **Azure App Configuration** feature dials.  
> **General**: [Deterministic Traffic Dialing](../../reference-dictionary/deployment-patterns.md#deterministic-traffic-dialing), [Shadow Testing](../../reference-dictionary/deployment-patterns.md#shadow-testing), [Canary Deployment](../../reference-dictionary/deployment-patterns.md#canary-deployment)

