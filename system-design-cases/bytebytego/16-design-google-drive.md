---
type: System Design Case
title: "Design Google Drive"
description: "Design a cloud file storage and synchronization platform (like Google Drive or Dropbox) featuring block-level chunking, delta sync, content-addressable deduplication, conflict resolution, and WebSocket notification sync."
tags: [system-design, distributed-systems, google-drive, dropbox, delta-sync, block-storage, deduplication, s3]
generated: { by: process:okf-migrate, at: 2026-08-22T00:00:00Z }
---

# Design Google Drive

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 16  
> **Topic**: Cloud Storage, Block-Level Delta Synchronization, Content-Addressable Deduplication, File Revision Trees

---

## 1. Understand the Problem and Establish Design Scope

Google Drive and Dropbox allow users to store files securely in the cloud, synchronize modifications across multiple devices (desktop, mobile, web), track version history, and collaborate via shared folders.

```mermaid
flowchart LR
    subgraph ClientDevices["User Devices"]
        D1["Desktop Client (Mac/PC)"]
        D2["Mobile Phone (iOS/Android)"]
    end

    subgraph DrivePlatform["Cloud Synchronization Engine"]
        BLOCK_SVC["Block Server<br/>(Delta Chunking & Compression)"]
        META_SVC["Metadata Server<br/>(File Tree & Versions)"]
        S3_STORAGE[("Cloud Object Storage (S3)<br/>(Encrypted 4MB Chunks)")]
    end

    D1 -->|1. Edit File & Upload Modified Chunks| BLOCK_SVC
    BLOCK_SVC --> S3_STORAGE
    BLOCK_SVC --> META_SVC
    META_SVC -.->|2. Push Change Notification| D2
    D2 -->|3. Download Only Delta Chunks| S3_STORAGE
```

![Archify diagram: Google Drive block delta synchronization](resources/google-drive/google-drive-delta-sync.png)

[Open the interactive Archify diagram](resources/google-drive/google-drive-delta-sync.html)

---

### Interview Clarification & Scope

> **Candidate:** What are the primary user features?  
> **Interviewer:** **File upload/download**, **cross-device synchronization**, **revision history**, and **change notifications**. Real-time collaborative doc editing (like Google Docs) is out of scope.
>
> **Candidate:** What is the scale and file size limit?  
> **Interviewer:** **10 Million Daily Active Users (DAU)**. Files up to **10 GB** are supported.
>
> **Candidate:** What are the security and bandwidth requirements?  
> **Interviewer:** Files must be encrypted at rest and in transit. Minimize bandwidth consumption using **delta sync and data compression**.

---

### Back-of-the-Envelope Estimation

| Metric / Dimension | Calculation | Estimated Value |
|:---|:---|:---|
| **Registered Users / DAU** | $50\text{M registered} / 10\text{M active}$ | $10{,}000{,}000\text{ DAU}$ |
| **Free Storage Allocation** | $50\text{M users} \times 10\text{ GB free}$ | $\mathbf{500\text{ PB total allocated}}$ |
| **Daily File Uploads** | $10\text{M users} \times 2\text{ uploads/day}$ | $20{,}000{,}000\text{ uploads/day}$ |
| **Average Upload QPS** | $\frac{20{,}000{,}000}{86{,}400\text{ sec}}$ | $\approx \mathbf{240\text{ QPS}}$ |
| **Peak Upload QPS** | $2 \times \text{Average QPS}$ | $\approx \mathbf{480\text{ QPS}}$ |

---

## 2. Core Storage Architecture: Block-Level Delta Synchronization

Uploading entire $10\text{ GB}$ files upon minor text edits wastes massive client bandwidth and saturates network pipes. The system uses **Block-Level Chunking & Delta Sync**:

```mermaid
flowchart TD
    FILE["Original File: Document.pdf (12 MB)"] --> CHUNK["Chunker (Split into 4 MB Blocks)"]
    
    subgraph Blocks["4 MB Content-Addressable Blocks"]
        B1["Block 1 (Hash: 0x8a3f...)"]
        B2["Block 2 (Hash: 0x9b1c...)"]
        B3["Block 3 (Hash: 0x4f2a...)"]
    end
    
    CHUNK --> B1 & B2 & B3

    subgraph EditScenario["User Modifies Only Page 2"]
        EDIT_FILE["Modified File: Document.pdf"] --> EDIT_CHUNK["Re-Chunk"]
        EDIT_CHUNK --> EB1["Block 1 (Hash: 0x8a3f -> Unchanged)"]
        EDIT_CHUNK --> EB2["Block 2 (Hash: 0x7c8e -> <b>MODIFIED!</b>)"]
        EDIT_CHUNK --> EB3["Block 3 (Hash: 0x4f2a -> Unchanged)"]
    end

    EB2 -->|Upload ONLY Modified Block 2 (4 MB)| S3[("Object Storage")]
```

### Key Technical Optimizations
1. **Delta Sync**: Only modified blocks are uploaded and synced across devices, reducing network transfer by $>90\%$.
2. **Deduplication**: Chunks are content-addressed by SHA-256 hash. If another user uploaded the same block, storage is de-duplicated instantly.
3. **Compression & Encryption**: Blocks are compressed using GZIP/Snappy and encrypted with AES-256 before leaving the client.

---

## 3. High-Level Architecture

```mermaid
flowchart TD
    subgraph ClientApp["Desktop / Mobile Client Engine"]
        CHUNKER["Chunker & Hasher"]
        LOCAL_DB[("Local SQLite DB<br/>(Local File States)")]
    end

    subgraph EdgeGateways["API & Notification Gateways"]
        LB["Load Balancer"]
        API["Metadata API Servers<br/>(File Tree, Shares, Versions)"]
        NOTIF["Notification Gateway<br/>(WebSockets / Long Polling)"]
    end

    subgraph BackendTier["Compute & Processing Fleet"]
        BLOCK_SVC["Block Server Fleet"]
        S3_STORAGE[("Cloud Object Storage (S3)<br/>(Raw Encrypted Blocks)")]
        META_DB[("Metadata DB<br/>(PostgreSQL / MySQL)")]
        REDIS[("Metadata Cache (Redis)")]
    end

    ClientApp -->|1. Upload Modified Blocks| BLOCK_SVC --> S3_STORAGE
    ClientApp -->|2. Commit File Version| API
    API <--> META_DB & REDIS
    API -->|3. Publish File Updated Event| NOTIF
    NOTIF -.->|4. Push Sync Event to other Devices| ClientApp
```

---

## 4. Metadata Schema & Conflict Resolution

### Relational Storage Schema (MySQL / Spanner)

```mermaid
erDiagram
    USER ||--o{ FILE_METADATA : owns
    FILE_METADATA ||--o{ FILE_VERSION : tracks
    FILE_VERSION ||--o{ FILE_BLOCK : consists_of

    USER {
        bigint user_id PK
        varchar username
        varchar email
    }

    FILE_METADATA {
        bigint file_id PK
        bigint owner_id FK
        varchar file_name
        varchar file_path
        boolean is_directory
    }

    FILE_VERSION {
        bigint version_id PK
        bigint file_id FK
        int version_number
        bigint total_size
        timestamp created_at
    }

    FILE_BLOCK {
        bigint block_id PK
        bigint version_id FK
        int block_order
        varchar block_hash
        varchar s3_object_key
    }
```

---

### Conflict Resolution Strategy (First-Write-Wins + Branching)

When two devices edit the same file offline and sync simultaneously:

```mermaid
sequenceDiagram
    autonumber
    actor D1 as Device 1 (Alice)
    participant Server as Metadata Server
    actor D2 as Device 2 (Bob)

    Note over D1,D2: Both have local copy: Document.txt (v1)
    D1->>Server: 1. Uploads edit -> Commits Document.txt (v2)
    Server-->>D1: Success (Version 2 Created)
    
    D2->>Server: 2. Attempts upload edit based on stale v1
    Server-->>D2: ❌ Conflict Detected! (Server is already on v2)
    
    D2->>D2: 3. Branching: Renames local file to "Document (Bob's Conflicted Copy).txt"
    D2->>Server: 4. Uploads conflicted copy as new separate file
```

---

## 5. End-to-End File Upload Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client as Drive Client App
    participant BlockSvc as Block Server
    participant S3 as S3 Object Storage
    participant MetaSvc as Metadata Server
    participant Notif as Notification Server
    actor Device2 as Synced Device 2

    Client->>Client: 1. Split modified file into 4MB chunks & compute SHA-256
    Client->>BlockSvc: 2. Check block existence (deduplication check)
    BlockSvc-->>Client: Returns list of missing blocks to upload
    Client->>S3: 3. Upload missing encrypted blocks
    Client->>MetaSvc: 4. Commit metadata (file_id, new version_id, block list)
    MetaSvc->>MetaSvc: 5. Save to Metadata DB & update Redis
    MetaSvc->>Notif: 6. Trigger "FileChangedEvent (file_id)"
    Notif->>Device2: 7. Push change notification via WebSocket
    Device2->>MetaSvc: 8. Get latest block list
    Device2->>S3: 9. Download ONLY missing 4MB blocks
```

---

## 6. Architectural Summary

```mermaid
mindmap
  root((Google Drive))
    Core Architecture
      Block-Level Delta Synchronization (4MB)
      Content-Addressable Deduplication (SHA-256)
      Cold Storage on S3 / Hot Metadata in DB
    Sync Engine
      Local SQLite DB on client devices
      WebSocket Notification Server for change broadcasts
      First-Write-Wins + Conflicted Copy Branching
    Security & Scale
      Client-side AES-256 block encryption
      Multi-AZ S3 durability
```

| Component | Design Decision | System Benefit |
|:---|:---|:---|
| **Chunking** | 4 MB Fixed Block Chunks | Optimizes network throughput, delta retransmissions, and compression efficiency. |
| **Deduplication** | Content-Addressable SHA-256 Hashing | Eliminates redundant storage of identical files across users. |
| **Synchronization**| WebSocket Notification Engine | Instantly notifies other logged-in devices to pull delta blocks. |
| **Conflict Strategy**| First-Write-Wins with Branching | Prevents silent data overwrites by automatically generating conflicted file copies. |

---

## References

1. How We Scaled Dropbox: https://dropbox.tech/infrastructure/how-we-scaled-dropbox
2. Content-Addressable Storage (CAS): https://en.wikipedia.org/wiki/Content-addressable_storage
3. Rsync Algorithm for Remote Delta Synchronization: https://rsync.samba.org/tech_report/
