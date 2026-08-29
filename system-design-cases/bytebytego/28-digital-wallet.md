---
type: System Design Case
title: "Digital Wallet"
description: "Design a high-throughput, fault-tolerant digital wallet system supporting 1,000,000 TPS, strict ACID financial consistency, event sourcing reproducibility, Raft consensus replication, and distributed Saga transfers."
tags: [system-design, distributed-systems, event-sourcing, cqrs, raft-consensus, high-throughput, fintech, saga]
timestamp: 2026-08-22T00:00:00Z
---

# Digital Wallet

> **Source**: *System Design Interview – An Insider's Guide: Volume 2* by Alex Xu & Sahn Lam  
> **ByteByteGo Chapter**: 28  
> **Topic**: High-Throughput Ledger, Distributed Transactions (2PC vs. TC/C vs. Saga), Event Sourcing, CQRS, Raft Consensus

---

## 1. Understand the Problem and Establish Design Scope

A digital wallet manages electronic account balances, wallet-to-wallet transfers, and balance histories. In high-scale financial platforms (e.g., Alipay, WeChat Pay, PayPal), the wallet subsystem must process millions of transfer requests per second with **zero data loss, absolute transaction atomicity, and complete historical auditability**.

```mermaid
flowchart LR
    subgraph ClientTier["Clients"]
        U1["User A (Sender)"]
        U2["User B (Receiver)"]
    end

    subgraph WalletPlatform["High-Throughput Digital Wallet Platform"]
        COORD["Saga Coordinator / Proxy"]
        P1["Partition 1 (Raft Group A)<br/><b>Account A: -$1</b>"]
        P2["Partition 2 (Raft Group B)<br/><b>Account B: +$1</b>"]
    end

    U1 -->|1. Transfer $1| COORD
    COORD -->|2. Debit Step| P1
    COORD -->|3. Credit Step| P2
    P1 & P2 -.->|CQRS Push Result| COORD
    COORD -->|4. Transfer Complete| U1 & U2
```

---

### Interview Clarification & Scope

> **Candidate:** What core operations should the digital wallet support?  
> **Interviewer:** Focus strictly on **balance transfer operations between two digital wallets**.
>
> **Candidate:** What is the throughput requirement?  
> **Interviewer:** Support **$1{,}000{,}000\text{ Transactions Per Second (1M TPS)}$**.
>
> **Candidate:** What correctness and verification guarantees are expected?  
> **Interviewer:** 
> - Strict ACID transactional correctness (zero lost funds, no negative balances).
> - **Reproducibility**: External auditors must be able to verify account integrity at any historical point in time by replaying deterministic events from the very beginning.
>
> **Candidate:** What is the availability SLA?  
> **Interviewer:** At least **$99.99\%$ (4 nines)** availability. Foreign exchange (FX) is out of scope.

---

### Requirements Summary

#### Functional Requirements
1. **Balance Transfer**: Atomically transfer an amount $X$ from Account A to Account B.
2. **Balance Query**: Return real-time account balances.
3. **Historical Reproducibility**: Reconstruct the exact account balance state at any timestamp $T$ by replaying immutable events.

#### Non-Functional Requirements
- **Ultra-High Throughput**: Handle $1{,}000{,}000\text{ transfers/sec}$ ($2{,}000{,}000\text{ atomic account balance operations/sec}$).
- **Strong Consistency & Atomicity**: No partial transfers; balance sum is strictly conserved.
- **Fault Tolerance**: Automated failover with zero data loss via distributed consensus.

---

### Back-of-the-Envelope Estimation

A single balance transfer command requires two underlying account operations:
1. Deduct $\$X$ from Account A (Debit).
2. Deposit $\$X$ to Account B (Credit).

$$\text{Operation Throughput} = 1{,}000{,}000\text{ transfers/sec} \times 2 = \mathbf{2{,}000{,}000\text{ TPS (2M TPS)}}$$

#### Node Capacity vs. Cluster Sizing
| Per-Node Transaction Capacity | Total Database Nodes Required for 2M TPS |
|:---|:---|
| **$100\text{ TPS}$** (Standard RDBMS disk commit) | $20{,}000\text{ nodes}$ (Prohibitively expensive) |
| **$1{,}000\text{ TPS}$** (Tuned RDBMS with connection pooling) | $2{,}000\text{ nodes}$ |
| **$10{,}000\text{ TPS}$** (In-Memory / Local LSM-Tree Engine) | $\mathbf{200\text{ nodes}}$ |

> [!NOTE]
> The primary design objective is to maximize single-node throughput using **in-memory caching, sequential append-only disk logging (`mmap`), and localized consensus** to minimize total cluster size.

---

## 2. High-Level Architecture Evolution

### Approach 1: In-Memory Sharded Cache (Redis + ZooKeeper)

```mermaid
flowchart TD
    API["Stateless Wallet Service"] --> ZK["ZooKeeper (Cluster Shard Registry)"]
    API --> R1[("Redis Node 1<br/>Account A (-$1)")]
    API --> R2[("Redis Node 2<br/>Account B (+$1)")]
```

- **Limitation**: If the wallet service crashes after updating Node 1 but before updating Node 2, money is destroyed. **Distributed updates across separate Redis nodes lack atomic transactional guarantees**.

---

### Approach 2: Distributed Database Transactions

To make updates atomic across sharded databases, three distributed transaction protocols are considered:

```mermaid
flowchart LR
    subgraph Protocols["Distributed Transaction Protocols"]
        direction TB
        TwoPC["<b>1. Two-Phase Commit (2PC)</b><br/>Prepare ➔ Commit. Heavy lock-holding, blocking, single coordinator point of failure."]
        TCC["<b>2. Try-Confirm/Cancel (TC/C)</b><br/>App-level reservation. Non-blocking; supports out-of-order execution flags."]
        SAGA["<b>3. Saga (Linear Orchestration)</b><br/>Chained local transactions with compensating rollbacks. Standard for microservices."]
    end
```

#### Comparison: 2PC vs. TC/C vs. Saga

| Dimension | 2-Phase Commit (2PC) | Try-Confirm / Cancel (TC/C) | Saga Pattern |
|:---|:---|:---|:---|
| **Transaction Level** | Database engine layer (XA) | Application business logic | Application business logic |
| **Lock Holding Time** | **Long** (locked until phase 2 ends) | **Short** (unlocked after each phase) | **Short** (unlocked after each step) |
| **Execution Order** | Simultaneous across nodes | Flexible / Parallel | **Strictly Linear Sequence** |
| **Rollback Mechanism** | Database abort | Compensating Cancel transaction | Compensating Rollback transaction |
| **Performance / Latency** | Low throughput, high latency | High throughput | High throughput |

#### Saga Linear Execution Flow ($A \rightarrow C$)

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant ORCH as Saga Coordinator
    participant DB_A as Shard A (Account A)
    participant DB_C as Shard C (Account C)

    User->>ORCH: Transfer $1 from A to C
    ORCH->>DB_A: Step 1: Deduct $1 from A
    DB_A-->>ORCH: Success (A = $0)
    ORCH->>DB_C: Step 2: Deposit $1 to C
    alt Step 2 Succeeds
        DB_C-->>ORCH: Success (C = $1)
        ORCH-->>User: Transfer Complete
    else Step 2 Fails (Account C Frozen)
        DB_C-->>ORCH: ❌ Failure
        ORCH->>DB_A: Compensating Step: Add $1 back to A
        DB_A-->>ORCH: Refund Confirmed
        ORCH-->>User: Transfer Failed (Funds Reverted)
    end
```

---

### Approach 3: Event Sourcing & CQRS

While distributed transactions handle atomicity, they do not provide auditability. **Event Sourcing** stores an immutable sequence of state-changing events as the single source of truth.

```mermaid
flowchart LR
    subgraph EventSourcingModel["Event Sourcing Core Model"]
        CMD["<b>Command</b><br/>(Intent: 'Transfer $1 from A to C')"] --> SM1["<b>Command Validator</b><br/>(Check A Balance >= $1)"]
        SM1 --> EVT["<b>Event Store (FIFO)</b><br/>(Fact: 'Transferred $1 from A to C')"]
        EVT --> SM2["<b>Deterministic State Machine</b><br/>(Apply Event to State)"]
        SM2 --> STATE[("<b>State (Read Model)</b><br/>A: $0, C: $1")]
    end
```

#### Core Concepts
1. **Command**: An external request/intent (can be rejected if invalid).
2. **Event**: An immutable historical fact (must be deterministic; always executed once validated).
3. **State**: The current balance projection derived by applying all historical events.
4. **Reproducibility**: State at timestamp $T$ is mathematically guaranteed by replaying events from $t_0$ to $T$.

---

## 3. Design Deep Dive: High-Performance Event Sourcing

### 1. File-Based Storage with `mmap` & RocksDB

Each Raft node stores its own local copy of the shard's data on local NVMe. The **committed append-only event log is the source of truth**. RocksDB or SQLite is a rebuildable local projection of that log, used to answer balance queries quickly; it is not a second source of truth. `mmap` is only an efficient way to access the local log file. It does not provide replication or consistency by itself.

```mermaid
flowchart TD
    subgraph NodeArchitecture["Each node in one Raft shard"]
        direction TB
        subgraph MemStore["OS Page Cache & Memory"]
            MMAP["Memory-Mapped Buffer (mmap)"]
            MEM_STATE["In-Memory State Cache"]
        end
        subgraph DiskStore["Sequential NVMe Storage"]
            WAL["Committed Append-Only Event Log<br/>(source of truth)"]
            ROCKS[("Local RocksDB or SQLite<br/>(derived balance projection)")]
            SNAP[("Derived State Snapshot")]
        end
    end

    MMAP --> WAL
    WAL --> ROCKS
    ROCKS <--> MEM_STATE
    ROCKS --> SNAP
```

- **Write order**: The leader appends an event, replicates it through Raft, waits for a quorum, and then marks it committed. Nodes apply committed events to their local projection.
- **Recovery order**: If RocksDB/SQLite or the memory cache is lost, the node restores the latest snapshot and replays later committed events from the log. The log remains authoritative.
- **Snapshots**: Periodic checkpoints saved to HDFS/S3 speed recovery, but a snapshot is a derived checkpoint and can be regenerated from the event log.

---

### 2. High Reliability via Raft Consensus

To eliminate single points of failure, event sourcing nodes are grouped into **3- or 5-node Raft consensus clusters**.

![Raft Consensus for One Wallet Shard](resources/28-digital-wallet/raft-consensus-shard.visual-check.1440x900.light.png)

```mermaid
flowchart TD
    CLIENT["Saga Coordinator"] --> LEADER["Raft Leader (Node 1)<br/>1. Accept Command<br/>2. Append to Local Event Log"]
    
    LEADER -->|Raft Log Replication| F1["Follower 1 (Node 2)"]
    LEADER -->|Raft Log Replication| F2["Follower 2 (Node 3)"]

    F1 & F2 -.->|"Quorum Ack (Majority: 2/3)"| LEADER
    LEADER -->|3. Commit & Apply Event to State| LEADER
    LEADER -->|4. Push Status| CLIENT
```

- **Leader**: Validates incoming commands, appends events to the local WAL, and replicates them to followers.
- **Followers**: Replicate event streams; update local read projections deterministically.
- **Failover**: If the leader crashes, followers elect a new leader in $< 500\text{ ms}$ with zero uncommitted data loss.

---

### 3. Distributed Raft Sharding & CQRS Push Architecture

To achieve $1{,}000{,}000\text{ TPS}$, accounts are partitioned across multiple independent Raft consensus groups. **Sharding chooses the owner partition; Raft replicates that partition.** Raft does not synchronize every account with every database.

For example, Account A may belong to Shard 1 and Account B may belong to Shard 2:

```mermaid
flowchart LR
    ROUTER["Account Router<br/>hash(account_id)"] --> S1L
    ROUTER --> S2L

    subgraph S1["Shard 1: accounts A, D, X"]
        S1L["Node 1: Leader"] --> S1F1["Node 2: Follower"]
        S1L --> S1F2["Node 3: Follower"]
    end

    subgraph S2["Shard 2: accounts B, E, Y"]
        S2L["Node 4: Leader"] --> S2F1["Node 5: Follower"]
        S2L --> S2F2["Node 6: Follower"]
    end
```

All replicas in Shard 1 contain the committed event history for Account A, while replicas in Shard 2 contain the history for Account B. The Saga coordinator is needed only when one transfer touches accounts in different shards.

```mermaid
sequenceDiagram
    autonumber
    actor User as User A
    participant COORD as Saga Coordinator / Reverse Proxy
    participant P1 as Shard 1 Leader (owns A)
    participant P2 as Shard 2 Leader (owns B)

    User->>COORD: POST /v1/wallet/balance_transfer (A -> B, $1)
    COORD->>COORD: 1. Record Saga in Phase Status Table (Status: STARTED)
    
    Note over COORD,P1: Step 1: Debit Account A
    COORD->>P1: Command: Deduct $1 from A
    P1->>P1: Validate, Generate Event, Replicate via Raft & Apply
    P1-->>COORD: 2. CQRS Push: Event Committed (A balance = $0)
    COORD->>COORD: 3. Update Phase Status (Step 1 SUCCESS)

    Note over COORD,P2: Step 2: Credit Account B
    COORD->>P2: Command: Deposit $1 to B
    P2->>P2: Validate, Generate Event, Replicate via Raft & Apply
    P2-->>COORD: 4. CQRS Push: Event Committed (B balance = $1)
    COORD->>COORD: 5. Update Phase Status (Saga COMPLETE)
    
    COORD-->>User: 200 OK (Transfer Successful)
```

---

The two local Raft commits above are not one global Raft commit. Shard 1 guarantees that its replicas agree about the debit, and Shard 2 guarantees that its replicas agree about the credit. The Saga phase table tracks whether the overall transfer is `STARTED`, `DEBITED`, `COMPLETED`, or needs retry/compensation.

## 4. Balance Check Read Path

A balance query is routed to the shard that owns the requested account. For a financial decision, read from the current leader using a linearizable read (for example, a Raft `ReadIndex`) so the result reflects all committed events. A follower may be used for less-sensitive, eventually consistent views, but it can be stale.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as Wallet API / Router
    participant S1 as Shard 1 Leader (owns Account A)
    participant F1 as Shard 1 Followers

    User->>API: GET /v1/wallets/A/balance
    API->>API: Route by account_id A -> Shard 1
    API->>S1: Linearizable balance read
    S1->>F1: Confirm current Raft commit index
    F1-->>S1: Quorum confirms committed index
    S1->>S1: Read Account A projection at that index
    S1-->>API: Balance = $7, version = 1842
    API-->>User: 200 OK { balance: $7, version: 1842 }
```

The balance projection is a local read model derived from the committed event log. It is not independently reconciled with every other shard: Account A is authoritative in Shard 1, and Account B is authoritative in Shard 2.

## 5. Architectural Summary

### Architectural Comparison Matrix

```mermaid
mindmap
  root((Digital Wallet 1M TPS))
    Step 1 Scope
      1M Transfers/sec = 2M TPS
      Reproducibility & Auditability
      Zero Data Loss Guarantee
    Step 2 Architecture Evolution
      In-Memory Redis: Fast but non-atomic across shards
      2PC Distributed DB: Atomic but slow lock contention
      Saga Pattern: Non-blocking linear compensation
    Step 3 Deep Dive
      Local mmap & Append-Only Event Log
      Raft Consensus Replication Groups
      Distributed Shards with Saga Coordinator
      CQRS Push via Reverse Proxy
```

| Architecture Approach | Throughput Capability | Consistency & Auditability | Failure Recovery |
|:---|:---|:---|:---|
| **In-Memory Cache (Redis)** | High ($> 100\text{K TPS}$) | Poor (No cross-shard atomicity; no history) | High risk of data loss on crash |
| **Distributed 2PC Database** | Low ($< 1\text{K TPS}$) | Strong consistency; poor auditability | Heavy blocking on coordinator failure |
| **Saga on Traditional RDBMS** | Moderate ($10\text{K TPS}$) | High consistency; state overwrites erase history | Complex compensating rollbacks |
| **Distributed Event Sourcing (Raft + mmap)** | **Ultra-High ($> 1\text{M TPS}$)** | **Absolute mathematical reproducibility & audit trail** | **Instant Raft leader election with zero data loss** |

---

## References

1. Designing Data-Intensive Applications (Distributed Transactions & Consensus) by Martin Kleppmann
2. Event Sourcing & CQRS by Martin Fowler: https://martinfowler.com/bliki/CQRS.html
3. In-Search of an Understandable Consensus Algorithm (Raft): https://raft.github.io/raft.pdf
4. The Log: What every software engineer should know about real-time data's unifying abstraction by Jay Kreps: https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying
