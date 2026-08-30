---
type: System Design Case
title: "Distributed Message Queue"
description: "Design a high-throughput, horizontally scalable distributed message queue (like Apache Kafka or Pulsar) featuring append-only commit logs, zero-copy data transfer, partition replication (ISR), and transactional exactly-once delivery."
tags: [system-design, distributed-systems, message-queue, kafka, pulsar, commit-log, zero-copy, isr, exactly-once]
timestamp: 2026-08-22T00:00:00Z
---

# Distributed Message Queue

> **Source**: *System Design Interview – An Insider's Guide: Volume 2* by Alex Xu & Sahn Lam  
> **ByteByteGo Chapter**: 20  
> **Topic**: Append-Only Commit Logs, Zero-Copy I/O, Partitioning & ISR Replication, Consumer Group Rebalancing, Exactly-Once Semantics

---

## 1. Understand the Problem and Establish Design Scope

A distributed message queue provides high-throughput, low-latency, and durable publish-subscribe messaging between decoupled distributed microservices.

```mermaid
flowchart LR
    subgraph Producers["Message Producers"]
        P1["Order Service"]
        P2["Payment Service"]
    end

    subgraph BrokerCluster["Distributed Broker Cluster (Kafka)"]
        TOPIC["Topic: orders (3 Partitions)"]
        P_0["Partition 0 (Leader: B1)"]
        P_1["Partition 1 (Leader: B2)"]
        P_2["Partition 2 (Leader: B3)"]
        TOPIC --> P_0 & P_1 & P_2
    end

    subgraph ConsumerGroups["Consumer Groups"]
        subgraph GroupA["Group A (Shipping)"]
            C1["Consumer A1"]
            C2["Consumer A2"]
        end
        subgraph GroupB["Group B (Analytics)"]
            C3["Consumer B1"]
        end
    end

    Producers -->|Batch Publish| TOPIC
    P_0 --> C1
    P_1 --> C2
    P_2 --> C2
    P_0 & P_1 & P_2 --> C3
```

---

### Interview Clarification & Scope

> **Candidate:** What delivery models should be supported?  
> **Interviewer:** Both **point-to-point** (competing workers within a consumer group) and **publish-subscribe** (independent consumer groups).
>
> **Candidate:** What are the message retention and ordering requirements?  
> **Interviewer:** Configurable retention (e.g., $14\text{ days}$). Messages must be strictly ordered **within each partition**.
>
> **Candidate:** What delivery semantics are required?  
> **Interviewer:** Support configurable semantics: **At-most-once**, **At-least-once**, and **Exactly-once**.
>
> **Candidate:** What are the performance and scale targets?  
> **Interviewer:** High throughput (millions of messages per second), sub-10ms delivery latency, and petabyte-scale durable log storage.

---

## 2. Core Architecture: Topics, Partitions, and Consumer Groups

```mermaid
classDiagram
    class Topic {
        +String name
        +int partitionCount
        +int replicationFactor
    }

    class Partition {
        +int partitionId
        +Broker leader
        +List~Broker~ inSyncReplicas
        +long logEndOffset
        +long highWatermark
    }

    class ConsumerGroup {
        +String groupId
        +List~Consumer~ members
        +Map~Partition, Long~ committedOffsets
    }

    Topic "1" *-- "many" Partition
    ConsumerGroup "1" --> "many" Partition : assigns
```

![Archify diagram: distributed message queue log and replication](resources/distributed-message-queue/distributed-message-queue-log-replication.png)

[Open the interactive Archify diagram](resources/distributed-message-queue/distributed-message-queue-log-replication.html)

### Partitioning Rules
- **Keyed Messages**: $\text{Partition} = \text{hash}(\text{message\_key}) \pmod{\text{partition\_count}}$ (Guarantees strict per-entity ordering).
- **Keyless Messages**: Round-robin / sticky batching across partitions for uniform load distribution.

---

## 3. High-Throughput Storage Engine: Append-Only Segment Logs

General-purpose SQL/NoSQL databases degrade under heavy random write loads. A distributed queue structures each partition as an **append-only sequence of immutable disk segment files**:

```mermaid
flowchart TD
    PARTITION["Partition 0 Directory: /data/topic-0/"]
    
    subgraph Segments["Log Segments (e.g., 1 GB per segment)"]
        S1["0000000000.log (Oldest - Closed)"]
        S2["0000050000.log (Closed)"]
        S3["0000100000.log (<b>Active Segment - Writing New Appends</b>)"]
    end

    subgraph IndexFiles["Memory-Mapped Sparse Index (.index)"]
        I1["0000100000.index<br/>[Offset 100001 -> Byte Position 0]<br/>[Offset 100004 -> Byte Position 4096]"]
    end

    PARTITION --> Segments
    S3 <--> I1
```

---

### Three Pillars of Maximum I/O Performance

```mermaid
flowchart LR
    subgraph P1["1. Sequential Disk I/O"]
        SEQ["Sequential writes bypass disk head seek penalties, achieving 600+ MB/s on HDDs & GB/s on NVMe."]
    end

    subgraph P2["2. OS Page Cache"]
        CACHE["Brokers rely on Linux Kernel Page Cache. Hot messages read by consumers never hit physical disk!"]
    end

    subgraph P3["3. Zero-Copy (sendfile)"]
        ZERO["sendfile() transfers bytes directly from OS Page Cache to Network Socket without copying to User Space."]
    end
```

```mermaid
sequenceDiagram
    autonumber
    participant KernelCache as Linux Page Cache
    participant NIC as Network Card (Socket Buffer)
    participant Client as Consumer Client

    Note over KernelCache,NIC: Zero-Copy (sendfile Syscall)
    KernelCache->>NIC: DMA transfer directly from Page Cache to NIC Buffer (0 CPU context switches!)
    NIC-->>Client: Stream bytes over TCP Socket
```

---

## 4. Replication, High Availability & Quorum (ISR)

Each partition maintains a configured number of replicas ($N=3$) distributed across independent broker nodes:

```mermaid
flowchart TD
    PRODUCER["Producer (acks=all)"] --> LEADER["Broker 1 (Partition Leader)"]
    
    subgraph ISRCluster["In-Sync Replicas (ISR)"]
        LEADER
        F1["Broker 2 (Follower 1)"]
        F2["Broker 3 (Follower 2)"]
    end

    LEADER -->|Replicate Log Append| F1 & F2
    F1 & F2 -->>|ACK Replicated| LEADER
    LEADER -->>|High Watermark Advanced -> Commit ACK| PRODUCER
```

### Producer Acknowledgment Levels (`acks`)

| `acks` Level | Description | Durability | Latency |
|:---|:---|:---|:---|
| **`acks = 0`** | Producer sends and does not wait for broker response (Fire & Forget). | Lowest (Data loss on crash) | **Fastest ($< 1\text{ ms}$)** |
| **`acks = 1`** | Producer waits until **Partition Leader** commits to local log. | Medium (Loss if leader dies before replication) | Fast ($2\text{–}5\text{ ms}$) |
| **`acks = all` (`-1`)**| Producer waits until **all In-Sync Replicas (ISR)** commit to log. | **Maximum (Zero data loss)** | Medium ($5\text{–}15\text{ ms}$) |

---

## 5. Consumer Offset Tracking & Rebalancing

```mermaid
flowchart TD
    CONSUMER["Consumer A1 in Group 'shipping'"] -->|1. Poll Messages| BROKER["Broker Partition Leader"]
    BROKER -->>|2. Batch of Messages| CONSUMER
    CONSUMER ->|3. Process Batch & Commit Offset 4500| OFFSETS_TOPIC[("__consumer_offsets Topic<br/>(Compacted Log)")]
```

### Consumer Group Rebalance Protocol
When a consumer joins, crashes, or partitions change:
1. **Group Coordinator** (designated broker) detects missing heartbeats ($> 10\text{s}$).
2. Triggers **Rebalance**: Revokes existing partition assignments.
3. Elects **Group Leader Consumer** to compute a new balanced partition assignment matrix (Range / Round-Robin / Sticky).
4. Synchronizes new partition claims across remaining consumers.

---

## 6. Delivery Semantics: Exactly-Once Processing (EOS)

```mermaid
flowchart LR
    P["Idempotent Producer<br/>(PID + Monotonic Seq#)"] -->|Deduplicated by Broker| B["Broker Log"]
    B -->|Read-Process-Write| TXN["Transactional Coordinator<br/>(2-Phase Commit Atomic Offset + Output)"]
    TXN --> OUT["Downstream Topic"]
```

1. **Idempotent Producer**: Prevents network retry duplicates by tagging each batch with a unique Producer ID (`PID`) and monotonically increasing Sequence Number (`Seq#`).
2. **Transactional Coordinator**: Uses a Two-Phase Commit protocol to atomically commit consumer offsets and produced messages together.

---

## 7. Architectural Summary

```mermaid
mindmap
  root((Distributed Message Queue))
    Core Model
      Topics & Partitions (hash routing)
      Append-Only Segment Files (.log + .index)
      Consumer Groups with Independent Offsets
    Performance
      Sequential Disk I/O
      Linux Page Cache Acceleration
      Zero-Copy sendfile DMA Transfer
    High Availability
      Leader-Follower ISR Replication
      Configurable acks (0, 1, all)
      Automated Group Rebalance
    Semantics
      At-Least-Once (Default)
      Exactly-Once via PID + 2PC Transactions
```

| Subsystem | Architectural Decision | Core Rationale |
|:---|:---|:---|
| **Storage Engine** | Append-Only Disk Segments | Exploits sequential I/O to achieve hardware-limit throughput on low-cost disks. |
| **Data Transfer** | Linux OS `sendfile` Zero-Copy | Eliminates CPU memory copy overhead between kernel page cache and network buffers. |
| **Replication** | In-Sync Replicas (ISR) Quorum | Prevents data loss during leader broker failures while maintaining bounded replication latency. |
| **Scalability** | Horizontal Topic Partitioning | Allows linearly scaling write throughput and consumer parallelism across broker clusters. |

---

## References

1. Kafka: A Distributed Messaging System for Log Processing (Kreps et al. LinkedIn): https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf
2. Apache Kafka Documentation & Architecture: https://kafka.apache.org/documentation/
3. It's Okay to Store Data on Disk (Sequential I/O Benchmarks): https://queue.acm.org/detail.cfm?id=1563874
