---
type: Article
title: "Behind the Scenes: Evolving Netflix's Ads Event Pipeline for Live — Part II"
description: "How Netflix re-architected its revenue-critical Ads Event Pipeline for live events by replacing synchronous Metadata Registry writes with an Apache Flink stateful stream-stream join, route-to-data cross-region forwarding, and deterministic canary cutovers."
source: "https://netflixtechblog.medium.com/behind-the-scenes-evolving-netflixs-ads-event-pipeline-for-live-part-ii-826ebf9ad9fb"
author: "Kinesh Satiya, Yogesh Nagarur (Netflix Technology Blog)"
published: 2026-08-17
timestamp: 2026-08-23T00:00:00Z
---

# Behind the Scenes: Evolving Netflix’s Ads Event Pipeline for Live — Part II

> **Source**: [Netflix Technology Blog](https://netflixtechblog.medium.com/behind-the-scenes-evolving-netflixs-ads-event-pipeline-for-live-part-ii-826ebf9ad9fb) by [Kinesh Satiya](https://www.linkedin.com/in/kineshsatiya/) and [Yogesh Nagarur](https://www.linkedin.com/in/yogeshnagarur/)  
> **Related**: [Part I: Building a Robust Ads Event Processing Pipeline](netflix-ads-event-processing-pipeline.md), [Stream Processing Takeaways](../../system-design-architecture/stream-processing/netflix-ads-event-processing-takeaways.md), [Stream Processing (Flink)](../../system-design-architecture/stream-processing/stream-processing-flink.md)

## Introduction

In [Part 1 of this series](netflix-ads-event-processing-pipeline.md), we shared how Netflix built the Ads Event pipeline and approached it as a system design problem: replacing fragmented pipelines with centralized collection, enrichment, and a standard data contract. The result was **Ads Event Publisher**, the system that collects ad telemetry from client devices, *enriches* it with the context of the ad that was actually served, and publishes a single, unified stream of ad events to every downstream consumer: frequency capping, metrics, billing, measurement partners, and reporting. Any member viewing or account details that move through this pipeline end-to-end are encrypted and handled in accordance with Netflix’s strict privacy and security practices to safeguard member PII.

If ad serving is the **"brain"** and ad events are the **"heartbeats"** that feed it, then enrichment is what gives each heartbeat its meaning, turning a bare *"\[Somebody\] watched an ad to completion"* signal into *"this campaign, this creative, at this price, for this break."* Part 1 described that enrichment step as a single box in the architecture. This post is about what was inside that box, and why we rebuilt it.

Part 1 ended with a look at what was on the horizon: ads on live streams, de-duplication, and richer data signals. A single project delivered all three by rebuilding the Ads Event Publisher around stateful stream processing. We replaced a database lookup with a real-time streaming join in **Apache Flink**, which let the system scale for Live, took a dependency off the critical path, and replaced the engine of a high-traffic pipeline without downtime.

```
+-----------------------------------------------------------------------------------------+
|                                    AD SERVING PATH                                      |
|                                                                                         |
|   +---------------+     Ad Request      +---------------------+   Logs Serving Decision |
|   | Client Device | ------------------> | Netflix Ad Server   | --------------------+   |
|   |               | <------------------ |                     |                     |   |
|   +---------------+   Opaque Ad Token   +---------------------+                     |   |
+-----------|-------------------------------------------------------------------------|---+
            | (Playback Heartbeats)                                                   |
            v                                                                         v
+-------------------------------+                                       +-------------------------------+
| Kafka Client Events Topic     |                                       | Kafka Ad Responses Topic      |
+-------------------------------+                                       +-------------------------------+
            \                                                                       /
             \                                                                     /
              v                                                                   v
+-------------------------------------------------------------------------------------------------+
|                       Apache Flink Stateful Stream-Stream Join Pipeline                         |
|                                                                                                 |
|   1. Normalize      2. Cross-Region Forward     3. KeyedCoProcessJoin    4. In-Stream Dedup     |
|   (Format Agnostic)    (Route to Data)             (60-min TTL Window)      (Keyed Hash State)  |
+-------------------------------------------------------------------------------------------------+
                                                |
                                                v Enriched Canonical Events Stream
            +--------------------+--------------+--------------+--------------------+
            |                    |                             |                    |
            v                    v                             v                    v
    [Frequency Capping]   [Real-Time Metrics]          [Ad Verification 3P]   [Billing & Offline]
```

---

## A Quick Recap: Enrichment and the Metadata Registry

When an ad is served, the ad server knows everything about it: the campaign, the creative, the price of the impression, the targeting context, and the tracking URLs that measurement partners expect us to fire. The client device, by contrast, knows almost nothing: just an opaque token and *when* to send each event. Enrichment is the act of reuniting the two.

In the architecture from Part 1, that reunion happened through the **Ads Metadata Registry**, a Key-Value store:

- When the ad server made a decision, it **wrote the metadata** for that impression into the registry.
- It encoded only reference identifiers into the opaque token returned to the device, keeping the token small.
- Later, when the client fired an event carrying that token, the Ads Event Publisher decoded the token, **looked up the metadata** in the registry, and stitched the two together into an enriched ad event.

```
[Legacy Phase 1 Design: Synchronous Metadata Registry]

Ad Server ──── (1. Sync Write Full Metadata) ───► [ Globally Replicated KV Store ]
    │                                                            ▲
    ▼ (2. Return Small Token)                                    │ (4. Lookup Metadata)
Client Device ──── (3. Send Event + Token) ───► Ads Event Publisher
                                                       │
                                                       ▼ (5. Emit Enriched Event)
                                                Downstream Sinks
```

This design served us well. The registry was globally replicated, which gave us a useful property almost for free: an event arriving in *any* region could find its metadata regardless of where the ad was decided. It future-proofed the token against ever-growing metadata, and it carried us through the first phase of Netflix’s advertising growth.

However, as we looked ahead—especially to ads on live streams—the limits of this design became clear.

---

## Why We Needed to Evolve

The forcing function was **Live**. Netflix’s live slate has grown rapidly, from NFL games to blockbuster fight nights to the FIFA Women’s World Cup 2027, and viewership keeps growing. That traffic looks nothing like Subscription Video on Demand (SVOD): a single event can surge toward tens of millions of concurrent viewers within minutes, then drain just as fast when it ends. Building the ad pipeline for Live meant building for that trajectory.

To see why the old design could not get there, consider the numbers. When Netflix streamed the Jake Paul vs. Mike Tyson fight to more than 100 million viewers, a single ad break at that scale generated an enormous volume of ad events. Serving those ads in the old design would have meant writing metadata for each of them to the Metadata Registry and waiting for acknowledgment before the ads could serve: millions of must-succeed database writes per second on the ad-serving critical path.

That pattern created three core problems at Live scale:

1. **It was a scaling bottleneck**: Every ad and every ad break is a write. Multiply that by tens of millions of concurrent viewers, keep it non-lossy (a dropped write is a dropped ad, and lost revenue), add Live’s spiky on/off pattern, and the write load becomes enormous. Adding nodes reshuffles data across a cluster to rebalance it; doing that in the middle of a live event could slow or fail the very writes you are adding capacity for. That left pre-scaling for peak in advance as the only option.
2. **Hard dependencies on the critical path**: Serving an ad meant a synchronous, must-succeed write to the registry, followed by a wait for acknowledgment. Every system on the critical path is one more thing that can stop an ad from serving. The metadata registry had no fallback, so an unhealthy registry meant serving stopped. Taking hard dependencies off that path was mandatory.
3. **Event freshness risks**: If writing slowed down under load, or lookups timed out, events spilled into retries and dead-letter queues, and enriched ad events were delivered late. Systems like real-time frequency capping cannot tolerate late arrivals—they need events under a strict sub-second SLA to decide whether the next selected ad can run without breaking advertiser policies.

So we asked a simple question: *the ad server already knows and logs everything about the ad it served. Does it really need to write that to a database on the hot path? Can we match that against the downstream Kafka stream of client events, which is always there, after the fact?*

The write leaves the critical path entirely; no shared datastore outage can stop serving, and enrichment becomes something we scale elastically with Live rather than a cluster we babysit.

Matching two streams after the fact is a **streaming join**, and that is where Flink comes in.

---

## Why Apache Flink

We chose **Apache Flink** because near-real-time, **stateful stream processing** is exactly what it is built for, and because it has deep, production-tested platform support at Netflix. Just as important, we already knew how to run it. As Part 1 noted, our Ads Sessionizer is a large stateful Flink job, so operating one at scale, tuning state, checkpoints, and recovery under production load, was familiar ground for the team. Enrichment on Flink was built on that experience rather than starting from scratch.

---

## The New Architecture

At its core, the new Ads Event Publisher is built as an Apache Flink streaming job. Each event moves through a handful of stages:

1. **Normalize**: Client events arrive from several sources, including SVOD, live, playback, and embedded ad breaks, each with a slightly different shape. We first normalize them into a common canonical form.
2. **Re-route**: Client events and response events may appear in different regions; we inspect and reroute them to the correct job-processing region for a successful join.
3. **Join**: The heart of the job: we match each client event to the ad-serving response for the same impression, enriching it with the full serving context using a custom `KeyedCoProcessFunction`.
4. **Deduplicate**: Revenue-bearing events are de-duplicated in-stream so nothing is counted twice.
5. **Publish**: We extract measurement beacons for our partners and route the enriched ad event to downstream consumers.

```
+-----------------------------------------------------------------------------------------+
|                               Apache Flink Processing Topography                        |
|                                                                                         |
|   [Client Event Stream]      [Ad Server Decision Stream]                                |
|             |                             |                                             |
|             v                             v                                             |
|   +-------------------+         +-------------------+                                   |
|   | 1. Normalization  |         | 1. Normalization  |                                   |
|   +-------------------+         +-------------------+                                   |
|             |                             |                                             |
|             v                             v                                             |
|   +-------------------------------------------------+                                   |
|   | 2. Region Re-Router (Forward to Serving Region) |                                   |
|   +-------------------------------------------------+                                   |
|             |                             |                                             |
|             +--------------+--------------+                                             |
|                            | (KeyBy Impression ID)                                      |
|                            v                                                            |
|   +-------------------------------------------------+                                   |
|   | 3. KeyedCoProcessFunction Join (60-min TTL)     |                                   |
|   |    - Response exists  -> Enrich immediately     |                                   |
|   |    - Event arrives 1st-> Buffer in state        |                                   |
|   |    - TTL Expiration   -> Unmatched / DLQ        |                                   |
|   +-------------------------------------------------+                                   |
|                            |                                                            |
|                            v                                                            |
|   +-------------------------------------------------+                                   |
|   | 4. In-Stream Keyed Deduplication (Hash ID State)|                                   |
|   +-------------------------------------------------+                                   |
|                            |                                                            |
|                            v                                                            |
|   +-------------------------------------------------+                                   |
|   | 5. Output Dispatch & Partner Beacon Extraction  |                                   |
|   +-------------------------------------------------+                                   |
+-----------------------------------------------------------------------------------------+
```

### The Stream-Stream Join Mechanics

Client events and ad serving responses arrive on separate streams at different times. The job holds recent responses in memory and matches events against them over a **60-minute window**. Three scenarios occur:

- **The response is already there** when an event arrives → enrich it on the spot.
- **The event arrives first** → buffer it in state for a configurable duration (60 minutes) until the matching response shows up, then enrich it.
- **No response arrives within the window** → mark the event as *unmatched* for later offline recovery.

We built the join as a custom Flink operator (a `KeyedCoProcessFunction`) rather than a built-in windowed join. We do not need strict time-window ordering semantics because downstream consumers handle ordering; we simply match each client event to its response by key. Owning the operator at its lowest API level lets us control the matching state directly, including state TTL policies and how unmatched events are flushed to dead-letter queues.

Why 60 minutes? Roughly **99.999%** of events reach the job well within that window. Extending the window further would only bloat operator state and slow down checkpoints for a negligible gain. The remaining 0.001% is captured via an offline batch recovery path.

---

## Cross-Region: Matching Events Where Their Data Lives

The legacy Metadata Registry handled cross-region enrichment via a globally replicated key-value store. An event landing in any region could read its metadata from the local replica.

In a streaming join, the two sides of the join live in different places:
- The **ad serving response** stays in the region where the ad was served.
- The **client event** is fired by the user device, which can roam: a member might start an ad on home Wi-Fi (*us-east-1*) and transition to mobile cellular (*us-west-2*) mid-stream.

```
[Cross-Region Route-to-Data Pattern]

   Region: us-west-2 (Client Landed)                 Region: us-east-1 (Ad Served)
+------------------------------------+             +------------------------------------+
| 1. Client Event arrives with token |             | Ad Server logs Decision to Kafka   |
|    Token contains: "orig=us-east-1"|             | (Decision waits in Flink state)    |
|                                    |             |                                    |
| 2. Re-router inspects origin tag   |             |                                    |
| 3. Forwards event via Kafka topic  | ──────────► | 4. Receives forwarded event        |
|    to us-east-1                    | (WAN Link)  | 5. Performs local Flink stream join|
+------------------------------------+             +------------------------------------+
```

Replicating every region's serving responses to all other regions worldwide was rejected due to extreme cost and wasteful compute.

Instead, Netflix solved this as a **routing problem**:
1. Encode the **serving region** directly into the opaque ad token issued to the client.
2. When a client event arrives in a region that did not serve the ad, the ingestion layer decodes the origin region and **forwards the event to the serving region's stream**.
3. Only the small fraction of genuinely cross-region events incurs a cross-region network hop.

---

## Catching the Long Tail of Late-Arriving Events

For the remaining 0.001% of events delayed beyond the 60-minute in-stream window (e.g., disconnected devices, paused playback resumed hours later, or downstream vendor delays):

```
+------------------------------------------------------------------------------------+
|                                Tiered Ingestion Architecture                       |
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
+------------------------------------------------------------------------------------+
```

1. Unmatched events expire from Flink state and are routed to a **Dead-Letter Queue (DLQ)** in durable storage (S3 / Data Lake).
2. An hourly **Apache Spark batch job**, orchestrated by **Maestro** (Netflix's workflow orchestrator), joins these stragglers against the long-term serving responses persisted in the data warehouse.
3. The repaired events are re-published into downstream canonical sinks, ensuring 100% financial and billing reconciliation without penalizing real-time memory footprints.

---

## What Was Hard: Engineering Challenges

### 1. Keeping the Core Lean
Operating a stateful streaming join at live-event scale required strict discipline: **the job’s only job is matching events**. Side lookups, external RPCs, or heavy business transformations were strictly moved off the hot path to ensure the join engine sustains massive bursts without backpressure.

### 2. In-Stream Keyed Deduplication
At-least-once transport means duplicate events occur during client retries or network reconnections. For billing, duplicates cannot be counted.
- **Deterministic Hashing**: Each event is hashed into a stable ID based on immutable fields (`ad_id`, `event_type`, `playback_offset`).
- **Keyed Local State**: Flink keys the stream by this hash ID, ensuring all copies route to the same operator instance. A short-TTL managed state store remembers seen IDs locally, eliminating external database check-and-write roundtrips and eliminating race conditions.
- **Tiered Guarantees**: In-stream dedup eliminates over 99.99% of duplicates. The unique event ID is retained in the canonical output so financial billing systems can perform secondary deduplication over multi-day batch accounting windows.

### 3. Zero-Downtime Production Rollout

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
        │ - Events hash to [0..99]                                      │
        │ - Threshold selects single authoritative publisher per event  │
        +───────────────────────────────────────────────────────────────+
                                        │
                                        ▼ Authoritative Output
                             Downstream Consumers
```

- **Shared Enrichment Logic**: Core enrichment logic was extracted into a shared library imported by both the legacy service and the Flink job, ensuring audit diffs detected only true pipeline infrastructure discrepancies.
- **Side-by-Side Shadow Auditing**: Both pipelines ingested 100% of live traffic in parallel; automated audit jobs continuously compared outputs, achieving >99.99% parity before cutover.
- **Deterministic Traffic Dial**: Random percentage splits would cause duplicate downstream events. Instead, a **deterministic hash of an event key** decided which pipeline published the authoritative event. Raising the dial threshold gradually shifted partitions from legacy to Flink with instant rollback capability.
- **Decommissioning**: Once 100% cutover was validated region-by-region, ad server writes to the Metadata Registry were shut off, and the legacy service and datastore were completely decommissioned.

---

## Results and Architectural Takeaways

1. **Eliminated Critical-Path Serving Dependencies**: Ad serving no longer performs synchronous, blocking database writes. Serving latency and availability are decoupled from backend datastore health.
2. **Elastic Scaling for Live Spikes**: The streaming pipeline easily scales to hundreds of thousands of events per second during live sports ad breaks (NFL, Tyson-Paul).
3. **Route-to-Data Beats Global Replication**: Forwarding occasional cross-region client events to the serving region is significantly more cost-effective than globally replicating all ephemeral ad responses.
4. **Lean In-Stream State with Tiered Batch Recovery**: Bounding streaming state to a 60-minute window keeps Flink checkpoints small and fast, while scheduled Spark batch recovery captures the 0.001% long tail.
5. **Earned Cutover via Deterministic Shadow Audits**: Running parallel pipelines and diffing live output before deterministic hash cutover guarantees zero disruption for revenue-critical systems.
