---
type: Article
title: "Behind the Scenes: Building a Robust Ads Event Processing Pipeline"
description: "How Netflix evolved its advertising event processing architecture from a simple pilot to a centralized, scalable pipeline powered by Kafka, Apache Flink sessionization, and a transient key-value metadata registry."
source: "https://netflixtechblog.com/behind-the-scenes-building-a-robust-ads-event-processing-pipeline-e4e86caf9249"
author: "Kinesh Satiya (Netflix Technology Blog)"
published: 2025-05-09
timestamp: 2026-08-23T00:00:00Z
---

# Behind the Scenes: Building a Robust Ads Event Processing Pipeline

> **Source**: [Netflix Technology Blog](https://netflixtechblog.com/behind-the-scenes-building-a-robust-ads-event-processing-pipeline-e4e86caf9249) by [Kinesh Satiya](https://www.linkedin.com/in/kineshsatiya/)  
> **Related**: [Part II: Evolving Netflix's Ads Event Pipeline for Live](netflix-ads-event-pipeline-live.md), [Stream Processing Takeaways](../../system-design-architecture/stream-processing/netflix-ads-event-processing-takeaways.md), [Stream Processing (Flink)](../../system-design-architecture/stream-processing/stream-processing-flink.md)

## Introduction

In a digital advertising platform, a robust feedback system is essential for the lifecycle and success of an ad campaign. This system comprises diverse sub-systems designed to monitor, measure, and optimize ad campaigns. At Netflix, we embarked on a journey to build a robust event processing platform that not only meets current demands but also scales for future needs.

Ad serving acts like the **"brain"** — making decisions, optimizing delivery, and ensuring the right ad is shown to the right member at the right time. Meanwhile, ad events, emitted after an ad is rendered, function like **"heartbeats"**, continuously providing real-time feedback (oxygen/nutrients) that fuels better decision-making, optimizations, reporting, measurement, and billing:

- Just as the brain relies on continuous blood flow, ad serving depends on a steady stream of ad events to adjust next ad serving decisions, frequency capping, pacing, and personalization.
- If the nervous system stops sending signals (ad events stop flowing), the brain (ad serving) lacks critical insights and starts making poor decisions or fails.
- The healthier and more accurate the event stream (like strong heart function), the better the ad serving system can adapt, optimize, and drive business outcomes.

## The Pilot: Basic Ad Event Handling

In November 2022, Netflix launched a new basic ads plan in partnership with Microsoft. The software systems extended existing Netflix playback systems to play ads. Initially, the system was designed to be simple, secure, and efficient, with an underlying ethos of device-originated and server-proxied operations.

The initial architecture consisted of three main components:
1. **Microsoft Ad Server**
2. **Netflix Ads Manager**
3. **Ad Event Handler**

Each ad served required tracking to ensure the feedback loop functioned effectively, providing the external ad server with insights on impressions, frequency capping (advertiser policy that limits the number of times a user sees a specific ad), and monetization processes.

```
+---------------+     1. Ad Request      +---------------------+     2. VAST Request    +----------------------+
| Client Device | ---------------------> | Netflix Ads Manager | ---------------------> | Microsoft Ad Server  |
|               | <--------------------- |                     | <--------------------- | (VAST Document)      |
+---------------+   3. Opaque Token      +---------------------+     Response           +----------------------+
        |
        | 4. Ad Playback Telemetry (Opaque Token)
        v
+-------------------------------+
| Kafka Telemetry Queue         |
+-------------------------------+
        |
        v
+-------------------------------+     5. Decrypt & Forward     +----------------------+
| Ads Event Handler             | ---------------------------> | Ad Server & 3P       |
| (Kafka Consumer)              |                              | Verification Vendors |
+-------------------------------+                              +----------------------+
```

### Key Workflow of the Pilot System

1. **Client Request**: Client devices request ads during an ad break from Netflix playback systems, which is decorated with information by Ads Manager to request ads from the ad server.
2. **Server-Side Ad Insertion (SSAI)**: The Ad Server sends ad responses using the VAST (Video Ad Serving Template) format.
3. **Netflix Ads Manager**: Parses VAST documents, extracts tracking event information, and creates a simplified response structure for Netflix playback systems and client devices:
   - Tracking information is packed into a structured Protocol Buffers (protobuf) data model.
   - This structure is encrypted to create an opaque token.
   - The final response informs client devices when to send an event and the corresponding token.
4. **Client Device**: During ad playback, client devices send events accompanied by the opaque token. The Netflix telemetry system enqueues these events in Apache Kafka for asynchronous processing.
5. **Ads Event Handler**: A Kafka consumer that reads and decrypts the event payload, forwarding the tracking information encoded back to the ad server and third-party verification vendors (e.g., DoubleVerify, Integral Ad Science, Nielsen).

## The Expansion: Addressing Token Bloat with a Key-Value Registry

As third-party advertising integrations expanded for measurement, tracking, and verification, a critical bottleneck emerged: **growth in the volume of data encapsulated within opaque tokens**.

Because these tokens were cached on client devices, token bloat presented a risk of elevated memory usage on low-power devices (such as smart TVs and streaming sticks) and increased network bandwidth overhead. Furthermore, upcoming business capabilities required additional third-party tracking URLs, metadata, and new event types.

```
                                  +------------------------------+
                                  |    Ads Metadata Registry     |
                                  | (Transient Key-Value Store)  |
                                  +------------------------------+
                                            ^          |
                       Store Ad Metadata    |          | Read Metadata
                       (Record ID + URLs)   |          | on Callback
                                            |          v
+---------------------+              +---------------+     Fetch 3P URLs    +----------------------+
| Netflix Ads Manager |              | Client Device | -------------------> | Ads Event Handler    |
| (Ad Decisioning)    |              | (Holds Ref ID)|                      | (Relays to Vendors)  |
+---------------------+              +---------------+                      +----------------------+
```

### Architectural Shift: Reference Tokens

To strategically address this challenge, Netflix introduced a new persistence layer using a **Key-Value abstraction** between ad serving and event handling: the **Ads Metadata Registry**.

- **Transient Storage**: This service stores rich metadata for each ad served.
- **Reference Identifiers**: The contract between client devices and Ads systems continues using opaque tokens, but instead of containing the full tracking payload, the token contains only lightweight reference identifiers — **Ad ID**, **Metadata Record ID**, and the **Event Name**.
- **Asynchronous Hydration**: Upon callback, the Ads Event Handler reads the tracking information directly from the Ads Metadata Registry to relay details to vendors.

This decoupled client devices from tracking payload growth and future-proofed the platform.

## The Evolution: Centralized In-House Event Processing Pipeline

In January 2024, Netflix invested in building an in-house advertising technology platform. This required the event processing pipeline to attain feature parity with existing systems while enabling rapid iteration for the in-house Netflix Ad Server and upcoming formats (such as Pause ads, Display ads, and Live stream ads).

### Requirements & Challenges

1. **In-House Frequency Capping**: Support real-time frequency capping across campaigns and user profiles.
2. **Impression Pricing & Billing**: Incorporate pricing models and impression curation for advertiser billing and revenue recognition.
3. **Advertiser Reporting & Metrics**: Deliver low-latency campaign performance metrics and centralized reporting APIs.
4. **Disparate Upstream Telemetry**: Accommodate varying logging frameworks from different ad formats (e.g., Display ads using different upstream telemetry than Video ads).

```
+------------------------------------------------------------------------------------+
|                                Upstream Ad Telemetry                               |
|               (Video Ads, Display Ads, Pause Ads, Live Stream Telemetry)           |
+------------------------------------------------------------------------------------+
                                          |
                                          v
+------------------------------------------------------------------------------------+
|                                Ads Event Publisher                                 |
|         (Decryption, Canonical Protobuf Contract, Hashing, Enrichment)             |
+------------------------------------------------------------------------------------+
         |                            |                          |                 |
         v                            v                          v                 v
+------------------+         +------------------+       +------------------+  +------------------+
| Frequency        |         | Ads Metrics      |       | Ads Sessionizer  |  | Ads Event        |
| Capping          |         | (Flink -> Druid) |       | (Apache Flink)   |  | Handler          |
+------------------+         +------------------+       +------------------+  +------------------+
         |                            |                          |                 |
         v                            v                          v                 v
+------------------+         +------------------+       +------------------+  +------------------+
| Ad Server        |         | Campaign Health  |       | Ad Sessions      |  | 3P Verification  |
| Feedback Loop    |         | & Budget Capping |       | (Downstream)     |  | (DV, IAS, etc.)  |
+------------------+         +------------------+       +------------------+  +------------------+
                                      |                          |
                                      +------------+-------------+
                                                   |
                                                   v
                                     +---------------------------+
                                     | Offline Billing & Revenue |
                                     | (Curated Impressions)     |
                                     +---------------------------+
```

### Core Architecture Principles

1. **Centralized Ad Event Publisher**: A unified collection system that consolidates token decryption, data enrichment, identifier hashing, and GDPR compliance into a single step, publishing a canonical, extensible data contract.
2. **Strict Downstream Separation**: All business consumers (frequency capping, metrics, sessionization, billing) sit downstream of the centralized publisher, isolating them from upstream client telemetry changes.
3. **Downstream Sessionization**: An Apache Flink stream processing job aggregates discrete playback events into cohesive **Ad Sessions**, providing a clean analytical abstraction.
4. **Decoupled Real-Time & Offline Workflows**: Real-time Flink streaming feeds Apache Druid OLAP for sub-minute monitoring and budget capping, while robust offline batch workflows curate impressions for financial billing and revenue recognition.

## Real-Time Streaming Components

| Component | Technology | Primary Function |
|:---|:---|:---|
| **Ads Event Publisher** | Centralized Microservice | Ingests telemetry, decrypts tokens, enriches events, hashes identifiers, and emits canonical event streams. |
| **Frequency Capping** | Kafka Consumer / In-Memory State | Tracks per-campaign and per-profile impressions in near real-time to constrain next ad decisioning. |
| **Ads Metrics** | Apache Flink + Apache Druid | Real-time dimensional metrics for campaign delivery health, live dashboards, and budget capping. |
| **Ads Sessionizer** | Apache Flink | Aggregates fragmented playback events (impression, start, quartiles, pause, complete) into unified Ad Sessions. |
| **Ads Event Handler** | Kafka Consumer | Relays tracking signals to external third-party verification vendors (e.g., IAS, DoubleVerify). |
| **Billing & Revenue** | Offline Batch Workflows | Curates validated impressions for exact revenue accounting and advertiser billing. |

## Business Capabilities Enabled

- **Display & Pause Ad Integration**: Reusable ingestion pipeline supporting multiple media formats without altering downstream consumers.
- **Programmatic Buying**: Dynamic bid pricing exchange and multi-tracker dispatch on impression events.
- **GDPR & Privacy Compliance**: Standardized propagation of user opt-out signals throughout Europe.
- **Interactive Event Types**: Native handling of ad clicks and QR code scans alongside video telemetry.

## Key Architectural Takeaways

1. **Strategic, Incremental Evolution**: System design must balance immediate launch needs with long-term extensible abstractions (e.g., moving from client-fat tokens to transient registries, then to unified publishers).
2. **Canonical Data Contracts**: Standardizing Protocol Buffers contracts between serving and event collection allows independent iteration and reliable schema evolution across distributed teams.
3. **Separation of Concerns**: Centralizing transport-level concerns (decryption, enrichment, compliance) protects business consumers from telemetry churn and upstream infrastructure migrations.
