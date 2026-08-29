---
type: System Design Case
title: "Design YouTube"
description: "Design a planetary-scale video sharing and streaming platform (like YouTube or Netflix) featuring DAG-based video transcoding pipelines, multi-bitrate adaptive bitrate streaming (HLS/DASH), CDN edge delivery, and pre-signed upload optimization."
tags: [system-design, distributed-systems, video-streaming, youtube, hls, dash, transcoding, cdn, dag-pipeline]
timestamp: 2026-08-22T00:00:00Z
---

# Design YouTube

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 15  
> **Topic**: Video Ingestion & Transcoding Pipelines, Adaptive Bitrate Streaming (HLS/DASH), CDN Bandwidth Cost Optimization, DAG Schedulers

---

## 1. Understand the Problem and Establish Design Scope

A video streaming platform enables content creators to upload high-definition videos and allows global viewers to stream content adaptively across diverse network conditions and device resolutions.

```mermaid
flowchart LR
    subgraph UploadTier["1. Ingestion Pipeline"]
        CREATOR["Content Creator"] -->|Upload Original Video| S3_TEMP["Raw Blob Storage"]
        S3_TEMP --> DAG["DAG Transcoding Engine"]
        DAG --> S3_ENCODED["Encoded Video Chunks (1080p, 720p, 480p)"]
    end

    subgraph StreamingTier["2. Edge Streaming"]
        S3_ENCODED --> CDN["Global CDN Edge Network"]
        CDN -->|"Adaptive Bitrate Stream (HLS/DASH)"| VIEWER["Viewer (Mobile / Web / TV)"]
    end
```

---

### Interview Clarification & Scope

> **Candidate:** What are the primary features to support?  
> **Interviewer:** **Video uploading** and **smooth video streaming** across multiple resolutions. Comments and likes are out of scope.
>
> **Candidate:** What client platforms must be supported?  
> **Interviewer:** Web browsers, mobile apps (iOS/Android), and Smart TVs.
>
> **Candidate:** What is the daily scale and video size limit?  
> **Interviewer:** **5 Million Daily Active Users (DAU)**; maximum video file size is **1 GB** (average $300\text{ MB}$).
>
> **Candidate:** Can we leverage cloud infrastructure?  
> **Interviewer:** Yes, leverage cloud object storage (S3) and global CDNs (CloudFront/Akamai).

---

### Back-of-the-Envelope Estimation

| Metric / Dimension | Calculation | Estimated Value |
|:---|:---|:---|
| **Daily Active Users (DAU)** | Given | $5{,}000{,}000\text{ DAU}$ |
| **Daily Video Uploads (10% DAU)** | $5\text{M} \times 10\%$ | $500{,}000\text{ videos uploaded/day}$ |
| **Daily Storage Requirement** | $500\text{K} \times 300\text{ MB}$ | $\mathbf{150\text{ TB/day}}$ |
| **5-Year Raw Storage Capacity** | $150\text{ TB} \times 365 \times 5$ | $\approx \mathbf{273\text{ PB}}$ |
| **Daily Video Views (5 views/user)** | $5\text{M} \times 5$ | $25{,}000{,}000\text{ video views/day}$ |
| **Daily CDN Outflow Bandwidth** | $25\text{M views} \times 300\text{ MB} \times 8\text{ bits} / 86{,}400$ | $\approx \mathbf{694\text{ Gbps Egress}}$ |

---

## 2. High-Level Architecture & End-to-End Pipelines

```mermaid
flowchart TD
    subgraph Ingress["Clients & DNS"]
        CREATOR["Content Creator"]
        VIEWER["Viewer"]
    end

    subgraph APITier["Stateless API Servers"]
        LB["Load Balancer"]
        API["API Gateway<br/>(Auth, Metadata, Pre-Signed URLs)"]
        META_DB[("Metadata DB<br/>(PostgreSQL / DynamoDB)")]
    end

    subgraph IngestionEngine["Video Processing Pipeline"]
        RAW_S3[("Raw Video Storage (S3)")]
        DAG_SCHED["DAG Task Scheduler & Queue"]
        WORKERS["Transcoding Worker Pool"]
        ENC_S3[("Transcoded Chunks Storage (S3)")]
    end

    subgraph EdgeCDN["Content Delivery Network"]
        CDN["Global Edge CDN (HLS/DASH Chunks)"]
    end

    CREATOR -->|1. Get Pre-Signed URL| LB
    LB --> API <--> META_DB
    API -.->|2. Return S3 Upload URL| CREATOR
    
    CREATOR -->|3. Multipart Direct Upload| RAW_S3
    RAW_S3 -->|4. S3 Event Notification| DAG_SCHED
    DAG_SCHED --> WORKERS
    WORKERS -->|5. Write Multi-Bitrate Chunks & Manifests| ENC_S3
    
    ENC_S3 --> CDN
    VIEWER -->|6. Stream Manifest & Video Chunks| CDN
```

---

## 3. Video Transcoding Pipeline (DAG Architecture)

Raw video formats (e.g., $1\text{ GB}$ ProRes/AVI) cannot be streamed directly to mobile devices. Videos must be encoded into multiple resolutions and modern codecs (H.264, VP9, AV1) split into **$2\text{–}10\text{ second chunks}$** for **Adaptive Bitrate Streaming (HLS/DASH)**.

```mermaid
flowchart TD
    RAW["Uploaded Raw Video (1080p MP4)"] --> SPLIT["Video Splitter (Chunk into 5s Segments)"]
    
    subgraph DAGPipeline["Directed Acyclic Graph (DAG) Parallel Execution"]
        SPLIT --> INSPECT["Inspection (Validate Codec & Resolution)"]
        
        INSPECT --> ENC_1080["Encode 1080p (H.264 & AV1)"]
        INSPECT --> ENC_720["Encode 720p (H.264 & AV1)"]
        INSPECT --> ENC_480["Encode 480p (H.264 & AV1)"]
        INSPECT --> ENC_360["Encode 360p (H.264 & AV1)"]
        
        INSPECT --> THUMB["Thumbnail Extractor"]
        INSPECT --> AUDIO["Audio Track Extractor"]
    end

    ENC_1080 & ENC_720 & ENC_480 & ENC_360 --> MANIFEST["HLS (.m3u8) / DASH (.mpd) Manifest Generator"]
    MANIFEST --> S3_OUT[("Final Transcoded Storage")]
```

---

## 4. Adaptive Bitrate Streaming Protocols

Modern streaming relies on **Adaptive Bitrate (ABR)**: the client's video player continuously measures network bandwidth and dynamically switches video quality chunk-by-chunk.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Mobile Video Player
    participant CDN as Edge CDN

    Client->>CDN: 1. GET master.m3u8 (Master Manifest Index)
    CDN-->>Client: Returns Available Bitrates (1080p, 720p, 480p)
    
    Note over Client: High Bandwidth Detected (50 Mbps)
    Client->>CDN: 2. GET /1080p/segment_001.ts
    CDN-->>Client: 1080p Chunk (5s)
    
    Note over Client: Network Drops / Cellular Congestion (2 Mbps)
    Client->>CDN: 3. GET /480p/segment_002.ts (Smooth Seamless Downshift!)
    CDN-->>Client: 480p Chunk (5s - No buffering freeze!)
```

### Protocol Comparison

| Protocol | Developer / Standard | Transport | Video Container | Supported Devices |
|:---|:---|:---|:---|:---|
| **Apple HLS** | Apple | HTTP/S | MPEG-2 TS / fMP4 | iOS, macOS, Safari, Android, Smart TVs |
| **MPEG-DASH** | ISO / MPEG Standard | HTTP/S | ISO Base Media (fMP4) | Android, Chrome, Smart TVs, Xbox |
| **Microsoft Smooth Streaming**| Microsoft | HTTP/S | MP4 Fragmented | Windows, Silverlight, Xbox |

---

## 5. Design Deep Dive: Performance & Cost Optimizations

### 1. Direct Client-to-S3 Upload with Pre-Signed URLs
- **Problem**: Uploading $1\text{ GB}$ videos through application API servers saturates backend network interfaces and ties up server worker threads.
- **Solution**: The client requests a **Pre-Signed S3 Upload URL** from the API server, then streams video chunks directly to S3 via HTTP `PUT` multipart upload.

---

### 2. CDN Bandwidth Cost Optimization (The 80/20 Long-Tail Rule)
- **Problem**: Streaming $694\text{ Gbps}$ directly through public CDN egress costs millions of dollars per month.
- **Cost-Reduction Tactics**:
  1. **Hot vs. Cold Caching**: Cache only the top $20\%$ of popular videos in high-cost CDN edges; serve the remaining $80\%$ long-tail videos directly from optimized low-cost origin video storage.
  2. **Multi-CDN Routing**: Dynamically route video traffic to the most cost-effective CDN provider based on real-time pricing and ISP peering agreements.
  3. **P2P Streaming Assistance**: For live streams with millions of concurrent viewers, leverage WebRTC peer-to-peer chunk sharing among nearby devices.

---

## 6. Architectural Summary

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'primaryColor': '#2d3436',
    'primaryTextColor': '#ffffff',
    'primaryBorderColor': '#1e272e',
    'lineColor': '#576574',
    'cScale0': '#2d3436',
    'cScaleLabel0': '#ffffff',
    'cScale1': '#0984e3',
    'cScaleLabel1': '#ffffff',
    'cScale2': '#27ae60',
    'cScaleLabel2': '#ffffff',
    'cScale3': '#8e44ad',
    'cScaleLabel3': '#ffffff',
    'cScale4': '#d35400',
    'cScaleLabel4': '#ffffff',
    'cScale5': '#c0392b',
    'cScaleLabel5': '#ffffff',
    'cScaleBorder0': '#1e272e',
    'cScaleBorder1': '#0652dd',
    'cScaleBorder2': '#218c74',
    'cScaleBorder3': '#6c5ce7',
    'mindmapRootColor': '#2d3436',
    'mindmapMainColor': '#0984e3',
    'mindmapSecondaryColor': '#27ae60',
    'mindmapTextColor': '#ffffff',
    'mindmapLineColor': '#576574'
  }
}}%%
mindmap
  root((YouTube Architecture))
    Upload Path
      Pre-Signed S3 Multipart Direct Upload
      DAG-Based Transcoding Engine
      Parallel Chunk Encoding (1080p -> 360p)
    Streaming Path
      Adaptive Bitrate Streaming (HLS / DASH)
      m3u8 / mpd Manifest Driven
      Dynamic Bitrate Switching on Bandwidth Fluctuations
    Cost & Scale Optimization
      Hot 20% Videos in CDN
      Long-Tail Videos from Origin Storage
      Multi-CDN Cost Routing
```

| Subsystem | Architectural Decision | Core Rationale |
|:---|:---|:---|
| **Upload Flow** | Pre-Signed S3 Direct Upload | Eliminates intermediate API server bottlenecks and handles parallel multipart uploads. |
| **Transcoding** | DAG Distributed Scheduler | Enables independent, fault-tolerant parallel processing of video resolutions and audio tracks. |
| **Streaming Protocol** | Apple HLS / MPEG-DASH | Enables smooth, buffer-free playback that adapts dynamically to client network bandwidth. |
| **Edge Delivery** | Multi-CDN Edge Tiering | Minimizes latency globally while slashing egress bandwidth costs. |

---

## References

1. Apple HTTP Live Streaming (HLS) Specification: https://developer.apple.com/streaming/
2. Netflix: High Quality Video Encoding at Scale: https://netflixtechblog.com/high-quality-video-encoding-at-scale-d159f3136ced
3. Building a Video Transcoding Pipeline with AWS Step Functions and S3: https://aws.amazon.com/solutions/implementations/video-on-demand-on-aws/