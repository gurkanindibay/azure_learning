---
type: System Design Case
title: "Real-Time Gaming Leaderboard"
description: "Design a real-time, highly scalable gaming leaderboard system supporting millions of concurrent players, sub-second score updates, fast top-N and relative rank lookups using Redis Sorted Sets and distributed sharding."
tags: [system-design, distributed-systems, redis, skip-list, caching, gaming, serverless]
timestamp: 2026-08-22T00:00:00Z
---

# Real-Time Gaming Leaderboard

> **Source**: *System Design Interview – An Insider's Guide: Volume 2* by Alex Xu & Sahn Lam  
> **ByteByteGo Chapter**: 26  
> **Topic**: In-Memory Data Structures, Skip Lists, Redis Sorted Sets, Range Sharding, Scatter-Gather Queries

---

## 1. Understand the Problem and Establish Design Scope

A gaming leaderboard tracks and displays player rankings in real-time based on competitive scores earned during matches or tournaments. Leaderboard systems are also used in fitness tracking apps, coding platforms, and sales gamification.

```mermaid
flowchart LR
    subgraph ClientTier["Client Tier"]
        P["Mobile Game Client"]
    end

    subgraph AppTier["Application Services"]
        GS["Game Service<br/>(Server Authoritative)"]
        LS["Leaderboard Service<br/>(Rank Engine)"]
    end

    subgraph DataTier["Data & Cache Tier"]
        REDIS[("Redis In-Memory<br/>(Sorted Sets / ZSET)")]
        RDB[("Relational DB / Ledger<br/>(MySQL Match Audit)")]
    end

    P -->|1. Win Match| GS
    GS -->|2. Verify & Increment Score| LS
    LS -->|3. ZINCRBY / ZREVRANK| REDIS
    LS -->|4. Async Match Ledger| RDB
    P -->|5. GET Top 10 / Rank| LS
```

---

### Interview Clarification & Scope

> **Candidate:** How is the score calculated and awarded?  
> **Interviewer:** Players earn points by winning matches (1 point per win in our basic model).
>
> **Candidate:** What is the leaderboard lifespan?  
> **Interviewer:** Tournaments run monthly; each month a new leaderboard is instantiated.
>
> **Candidate:** What leaderboard queries must be supported?  
> **Interviewer:** 
> 1. Display the **Top 10 players**.
> 2. Show a specific player's **exact global rank**.
> 3. Display the **relative rank window** (e.g., 4 places above and 4 places below the player).
>
> **Candidate:** What is the scale of the game?  
> **Interviewer:** **5 million Daily Active Users (DAU)** and **25 million Monthly Active Users (MAU)**. Players play an average of 10 matches per day.
>
> **Candidate:** How should ties be handled?  
> **Interviewer:** Same score can share rank, or break ties by whichever player reached the score first (earlier timestamp).
>
> **Candidate:** Is real-time presentation required?  
> **Interviewer:** Yes, score updates and leaderboard position shifts must reflect near real-time ($< 500\text{ ms}$).

---

### Requirements Summary

#### Functional Requirements
1. **Submit Score**: Atomically increment a player's score upon winning a match.
2. **Top $N$ Leaderboard**: Fetch the top 10 global players with scores and profile info.
3. **Player Rank Lookup**: Return a player's exact rank and current score.
4. **Relative Position Window**: Return $K$ players immediately above and below a given player.

#### Non-Functional Requirements
- **Real-Time Responsiveness**: Score updates and rank queries must return in $< 50\text{ ms}$.
- **High Concurrency & Scalability**: Support $2{,}500\text{ write QPS}$ (up to $250{,}000\text{ QPS}$ under global scale).
- **High Availability & Durability**: Survives Redis cache crashes with zero loss of persistent match history.

---

### Back-of-the-Envelope Estimation

| Dimension / Metric | Calculation | Estimated Value |
|:---|:---|:---|
| **Daily Active Users (DAU)** | Given | $5{,}000{,}000\text{ (5M DAU)}$ |
| **Monthly Active Users (MAU)** | Given | $25{,}000{,}000\text{ (25M MAU)}$ |
| **Average Matches Played** | $10\text{ matches/user/day}$ | $50{,}000{,}000\text{ matches/day}$ |
| **Average Write QPS (Score Increment)** | $\frac{50{,}000{,}000}{86{,}400\text{ sec}} \approx \frac{5 \times 10^7}{10^5}$ | $\approx \mathbf{500\text{ QPS}}$ |
| **Peak Write QPS** | $5\times\text{ average}$ | $\approx \mathbf{2{,}500\text{ QPS}}$ |
| **Top 10 Fetch QPS (Reads)** | $5\text{M logins/day} \div 10^5\text{ sec}$ | $\approx \mathbf{50\text{ QPS}}$ |
| **Entry Storage Size** | `user_id` (24 bytes) + `score` (4 bytes) | $\approx 28\text{ bytes/entry}$ |
| **Redis Monthly Memory Footprint** | $25\text{M MAU} \times 28\text{ bytes} \times 2\text{ (Skip list overhead)}$ | $\approx \mathbf{650\text{ MB to } 1.4\text{ GB}}$ |

> [!NOTE]
> At $5\text{M DAU}$, the entire monthly leaderboard fits in **$< 1.5\text{ GB}$ of memory**, which easily runs on a single Redis instance with master-replica replication.

---

## 2. High-Level Architecture

### Core APIs (RESTful / Internal RPC)

#### 1. `POST /v1/scores` (Internal Server-to-Server Only)
Updates a player's score. Called strictly by Game Servers upon match completion to prevent client tampering.

```json
{
  "userId": "usr_99812",
  "points": 1,
  "gameId": "match_77341",
  "timestamp": 1774329600
}
```

#### 2. `GET /v1/scores` (Top 10 Global Leaderboard)
```json
{
  "data": [
    { "rank": 1, "userId": "usr_alpha", "score": 9840, "avatar": "https://cdn.game/1.png" },
    { "rank": 2, "userId": "usr_bravo", "score": 9510, "avatar": "https://cdn.game/2.png" }
  ],
  "total": 10
}
```

#### 3. `GET /v1/scores/{userId}` (Player Rank & Surrounding Window)
```json
{
  "userId": "usr_99812",
  "rank": 361,
  "score": 1420,
  "surrounding": [
    { "rank": 359, "userId": "usr_359", "score": 1425 },
    { "rank": 360, "userId": "usr_360", "score": 1422 },
    { "rank": 361, "userId": "usr_99812", "score": 1420 },
    { "rank": 362, "userId": "usr_362", "score": 1418 }
  ]
}
```

---

### Why Relational Databases Fail for Real-Time Ranking

In a relational database (e.g., MySQL), computing a player's rank requires a full table scan or index count over millions of changing rows:

```sql
-- Finding rank in MySQL requires scanning all higher scores:
SELECT COUNT(*) + 1 AS rank
FROM leaderboard
WHERE score > (SELECT score FROM leaderboard WHERE user_id = 'usr_99812');
```

- **Time Complexity**: $O(N)$ full table scan.
- **Lock Contention**: Continuous high-frequency write updates invalidate query result caches instantly.

---

### The Redis Sorted Set (ZSET) Solution

Redis **Sorted Sets (`ZSET`)** combine a **Hash Table** ($O(1)$ key lookup) with a **Skip List** ($O(\log N)$ rank lookups and range queries).

```mermaid
flowchart TD
    subgraph ZSET["Redis Sorted Set (ZSET)"]
        direction TB
        HT["Hash Table: user_id ➔ score (O(1) direct lookup)"]
        SL["Skip List: Multi-Level Indexed Linked List (O(log N) rank & range)"]
    end

    ZSET --> C1["<b>ZINCRBY</b> key increment member<br/><i>O(log N)</i>"]
    ZSET --> C2["<b>ZREVRANK</b> key member<br/><i>O(log N) exact rank</i>"]
    ZSET --> C3["<b>ZREVRANGE</b> key start stop WITHSCORES<br/><i>O(log N + M) top-N or window</i>"]
```

#### Skip List Search Mechanics ($O(\log N)$)

```mermaid
flowchart LR
    subgraph Level2["Level 2 Index (Skip 4 Nodes)"]
        L2_1["1"] ------> L2_15["15"] ------> L2_60["60"]
    end
    subgraph Level1["Level 1 Index (Skip 2 Nodes)"]
        L1_1["1"] --> L1_8["8"] --> L1_15["15"] --> L1_36["36"] --> L1_60["60"]
    end
    subgraph BaseList["Base Sorted Linked List"]
        B1["1"] --> B4["4"] --> B8["8"] --> B10["10"] --> B15["15"] --> B26["26"] --> B36["36"] --> B45["45"] --> B60["60"]
    end

    L2_15 -.-> L1_15
    L1_36 -.-> B36
```

---

### Core Leaderboard Operations in Redis

```bash
# 1. Player wins a match: Increment score atomically
ZINCRBY leaderboard_2026_09 1 "usr_99812"

# 2. Fetch Top 10 Leaderboard (Descending order with scores)
ZREVRANGE leaderboard_2026_09 0 9 WITHSCORES

# 3. Fetch exact global rank of player
ZREVRANK leaderboard_2026_09 "usr_99812"

# 4. Fetch 4 players above and 4 players below rank 360 (0-indexed: 356 to 364)
ZREVRANGE leaderboard_2026_09 356 364 WITHSCORES
```

---

## 3. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Clients["Game Clients"]
        MOB["Mobile App"]
    end

    subgraph Ingress["Edge & Load Balancing"]
        ALB["Application Load Balancer"]
        API_GW["API Gateway (Auth / Rate Limit)"]
    end

    subgraph Services["Application Tier"]
        GS["Game Match Service"]
        LS["Leaderboard Service"]
    end

    subgraph InMemTier["In-Memory Rank Tier"]
        REDIS_PRI[("Redis Primary<br/>(Active ZSET)")]
        REDIS_REP[("Redis Replica<br/>(Read Replicas)")]
        CACHE[("User Profile Cache<br/>(Top 10 Avatars)")]
    end

    subgraph PersistentTier["Durability & Audit Tier"]
        MYSQL[("MySQL Master<br/>(Match History & Audit)")]
    end

    MOB --> ALB
    ALB --> GS
    ALB --> API_GW
    API_GW --> LS

    GS -->|1. Record Match| MYSQL
    GS -->|2. Async Score Update| LS
    LS -->|ZINCRBY| REDIS_PRI
    REDIS_PRI -->|Async Replication| REDIS_REP
    LS -->|ZREVRANGE / ZREVRANK| REDIS_REP
    LS -->|Fetch Display Names| CACHE
```

---

## 4. Design Deep Dive

### 1. Scaling to 500 Million DAU (250,000 QPS)

If the game expands to **$500\text{M DAU}$**, storage requirements grow to $65\text{ GB}$ and write throughput surges to $250{,}000\text{ QPS}$, exceeding single-node capacity.

#### Strategy A: Fixed Score Range Sharding (Recommended)

Divide players into discrete shards based on their total score ranges:

```mermaid
flowchart LR
    S1["Shard 1<br/>Scores [1 – 100]"]
    S2["Shard 2<br/>Scores [101 – 500]"]
    S3["Shard 3<br/>Scores [501 – 2000]"]
    S4["Shard 4 (Top Players)<br/>Scores [2001 – 10000+]"]
```

- **Top 10 Fetch**: Query strictly the highest shard (`Shard 4`) in $O(1)$ time.
- **Player Rank Lookup**:
  $$\text{Global Rank} = \text{Local Rank in Shard } k + \sum_{i > k} \text{Total Player Count in Shard } i$$
  Total player counts per shard are retrieved in $O(1)$ via Redis `INFO keyspace` or `ZCARD`.

#### Strategy B: Hash Partitioning (Redis Cluster Hash Slots)

```mermaid
flowchart TD
    CLIENT["Leaderboard Service"] --> SCATTER{"Scatter Query to All Shards"}
    SCATTER --> SHARD0["Shard 0: Top 10"]
    SCATTER --> SHARD1["Shard 1: Top 10"]
    SCATTER --> SHARD2["Shard 2: Top 10"]
    SHARD0 & SHARD1 & SHARD2 --> GATHER["Gather & Sort Top 10 in App"]
```

| Partition Strategy | Pros | Cons | Recommendation |
|:---|:---|:---|:---|
| **Fixed Score Range** | Ultra-fast Top 10; simple global rank math. | Needs score mapping cache to know player's current shard. | **Recommended** |
| **Hash Partition (Scatter-Gather)** | Perfectly balanced writes across shards. | High read latency; complex $O(N)$ rank aggregation. | Better for general key-value |

---

### 2. Serverless Cloud Implementation (AWS)

```mermaid
flowchart LR
    MOB["Mobile App"] --> APIGW["Amazon API Gateway"]
    APIGW --> L1["Lambda: UpdateScore"]
    APIGW --> L2["Lambda: GetTop10"]
    APIGW --> L3["Lambda: GetPlayerRank"]
    
    L1 & L2 & L3 --> ECACHE[("Amazon ElastiCache Redis<br/>(Multi-AZ Replication)")]
    L1 --> DDB[("DynamoDB / Aurora<br/>(Persistent Match Ledger)")]
```

- **Amazon API Gateway**: Routes incoming REST requests to stateless Lambda functions.
- **AWS Lambda**: Autoscales horizontally without managing server pools.
- **ElastiCache Redis**: Multi-AZ cluster with automatic failover and read replicas.

---

### 3. Alternative NoSQL Approach (DynamoDB Write Sharding)

For systems strictly standardizing on managed NoSQL without in-memory caches:

```mermaid
flowchart TD
    subgraph DDB_Table["DynamoDB Table + Global Secondary Index (GSI)"]
        direction TB
        GSI["<b>Partition Key (PK):</b> game_name#2026-09#p0...p3<br/><b>Sort Key (SK):</b> score (Descending)"]
    end

    READ["Get Top 10"] --> SG["Scatter-Gather across 4 Partitions"]
    SG --> GSI
```

- **Write Sharding**: Append random partition suffix `game_name#2026-09#p{0..N}` to avoid hot partitions.
- **Percentile Estimation**: When absolute global rank over 500M users is unnecessary, DynamoDB partitions support fast percentile queries ($90\text{th percentile}$, $99\text{th percentile}$).

---

### 4. Advanced Operational Topics

1. **Tie-Breaking with Secondary Timestamps**:
   - If two players have the same score, rank the player who reached the score first higher.
   - Format score as a composite float: $\text{Score} + \left(1 - \frac{\text{Timestamp}}{10^{13}}\right)$.
2. **Disaster Recovery from Match Ledger**:
   - If the Redis cluster suffers total loss, a replay worker iterates through the persistent MySQL `point_ledger` table to execute `ZINCRBY` calls and rebuild the sorted set offline.

---

## 5. Wrap Up & Summary

### Architectural Summary Mindmap

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
  root((Gaming Leaderboard))
    Step 1 Scope
      5M DAU / 25M MAU
      2500 Peak Write QPS
      Sub-Second Real-Time Updates
    Step 2 Architecture
      Server-Authoritative Game Gateway
      Redis Sorted Sets Skip List
      MySQL Persistent Audit Ledger
    Step 3 Deep Dive
      O log N ZINCRBY ZREVRANK ZREVRANGE
      Fixed Score Range Sharding for 500M DAU
      Serverless AWS API Gateway & Lambda
      Composite Score Float Tie-Breaking
```

    ![Archify diagram: real-time gaming leaderboard ranking](resources/real-time-gaming-leaderboard/leaderboard-ranking.visual-check.1440x900.light.png)

    > **Interactive Archify diagram**: [Real-time gaming leaderboard ranking](resources/real-time-gaming-leaderboard/leaderboard-ranking.html)

| Area | Decision | Key Rationale |
|:---|:---|:---|
| **Core Storage** | Redis Sorted Set (`ZSET`) | $O(\log N)$ rank calculation and range queries via Skip List. |
| **Cheating Defense** | Server-authoritative game score dispatch | Client cannot manipulate scores or rank positions. |
| **Scalability (500M DAU)** | Fixed Score Range Partitioning | Isolates top-tier queries to highest shard without scatter-gather overhead. |
| **Durability** | Persistent MySQL match audit log | Enables deterministic offline replay in case of cache outage. |

---

## References

1. Redis Sorted Set Implementation (Skip Lists): https://redis.io/topics/data-types#sorted-sets
2. Amazon ElastiCache for Redis Leaderboards: https://aws.amazon.com/blogs/database/building-a-real-time-gaming-leaderboard-with-amazon-elasticache-for-redis/
3. DynamoDB Write Sharding Pattern: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-sharding.html
