---
type: System Design Case
title: "Nearby Friends"
description: "Design a real-time, high-throughput location-sharing system (like Facebook Nearby Friends or Apple Find My) handling 334,000 update QPS and 13 million fan-out deliveries per second using WebSockets, Redis Pub/Sub, and distributed spatial filtering."
tags: [system-design, distributed-systems, nearby-friends, websockets, redis-pubsub, real-time, geospatial, zookeeper]
generated: { by: process:okf-migrate, at: 2026-08-22T00:00:00Z }
---

# Nearby Friends

> **Source**: *System Design Interview – An Insider's Guide: Volume 2* by Alex Xu & Sahn Lam  
> **ByteByteGo Chapter**: 18  
> **Topic**: Real-Time Dynamic Location Fan-Out, WebSockets, Channel-per-User Redis Pub/Sub, Spatial Distance Calculation

---

## 1. Understand the Problem and Establish Design Scope

Unlike static business proximity searches (Chapter 17), **Nearby Friends** tracks highly dynamic moving users, continuously computing proximity ($< 5\text{ miles}$) between mutual friends and fanning out real-time location updates.

```mermaid
flowchart LR
    subgraph Users["Mobile Users (Location Updates every 30s)"]
        U1["Alice (Moving)"]
        U2["Bob (Friend - 1.2 miles away)"]
        U3["Charlie (Friend - 12 miles away)"]
    end

    subgraph RealTimeCore["Nearby Friends Backend"]
        WS["Stateful WebSocket Cluster"]
        PUBSUB["Redis Pub/Sub Mesh"]
    end

    U1 -->|1. Push Coordinates| WS
    WS -->|2. Broadcast via Alice's Channel| PUBSUB
    PUBSUB -->|3. Distribute to Subscribers| WS
    WS -->|4. Distance = 1.2 mi <= 5 mi: Forward Update| U2
    WS -.->|5. Distance = 12 mi > 5 mi: Drop Update| U3
```

![Archify diagram: Nearby Friends real-time location fan-out](resources/nearby-friends/nearby-friends-websocket-fanout.png)

[Open the interactive Archify diagram](resources/nearby-friends/nearby-friends-websocket-fanout.html)

---

### Interview Clarification & Scope

> **Candidate:** What is considered "nearby"?  
> **Interviewer:** Within a **$5\text{ mile (8 km)}$ radius** (straight-line Euclidean/Haversine distance).
>
> **Candidate:** How frequently do mobile clients report locations?  
> **Interviewer:** Every **$30\text{ seconds}$** while the app is active. Inactive users ($> 10\text{ minutes}$) disappear from friend lists.
>
> **Candidate:** What is the daily scale and concurrency?  
> **Interviewer:** **100 Million DAU**, with **10 Million concurrent active users**. An average user has $400$ friends ($10\%$ online concurrently).

---

### Back-of-the-Envelope Estimation

| Metric / Dimension | Calculation | Estimated Value |
|:---|:---|:---|
| **Concurrent Active Users** | $100\text{M DAU} \times 10\%$ | $10{,}000{,}000\text{ concurrent users}$ |
| **Location Update Interval** | Given | $30\text{ seconds}$ |
| **Location Ingress QPS** | $\frac{10{,}000{,}000}{30\text{ sec}}$ | $\approx \mathbf{334{,}000\text{ Update QPS}}$ |
| **Average Online Friends** | $400\text{ friends} \times 10\%\text{ online}$ | $40\text{ online friends/user}$ |
| **Egress Fan-Out Throughput** | $334{,}000\text{ QPS} \times 40\text{ online friends}$ | $\approx \mathbf{13{,}360{,}000\text{ updates/sec}}$ |

> [!IMPORTANT]
> The primary engineering bottleneck is handling **13.3+ Million fan-out messages per second** across persistent WebSocket connections with minimal CPU and memory overhead.

---

## 2. High-Level Architecture: Channel-per-User Pub/Sub

```mermaid
flowchart TD
    subgraph IngressTier["Mobile Clients & Edge"]
        USER_A["User A (Mobile)"]
        USER_B["User B (Friend)"]
        LB["Layer 4 / Layer 7 Load Balancer"]
    end

    subgraph StatefulTier["WebSocket Cluster"]
        WS1["WebSocket Server 1<br/>(Holds User A Connection)"]
        WS2["WebSocket Server 2<br/>(Holds User B Connection)"]
    end

    subgraph PubSubMesh["Distributed Message Bus (Redis Pub/Sub)"]
        CH_A["Channel: user_A_updates"]
        CH_B["Channel: user_B_updates"]
    end

    subgraph StorageTier["Cache & Database Fleet"]
        LOC_CACHE[("Redis Location Cache<br/>(user_id -> lat, lon, TTL=10m)")]
        LOC_HIST[("Location History DB<br/>(Cassandra / ClickHouse)")]
        USER_DB[("User & Friendship Graph DB")]
    end

    USER_A <-->|Persistent WebSocket| WS1
    USER_B <-->|Persistent WebSocket| WS2
    
    WS1 -->|1. Write Coordinates & Reset TTL| LOC_CACHE
    WS1 -->|2. Append Log| LOC_HIST
    WS1 -->|3. Publish (lat, lon)| CH_A
    
    CH_A -->|4. Fan-Out to Subscribers| WS2
    WS2 -->|5. Compute Distance <= 5mi -> Push| USER_B
```

---

## 3. End-to-End Location Fan-Out Flow

```mermaid
sequenceDiagram
    autonumber
    actor Alice as User A (Mobile)
    participant WS_A as WebSocket Server 1
    participant Redis_Cache as Redis Location Cache
    participant Redis_PubSub as Redis Pub/Sub (Channel A)
    participant WS_B as WebSocket Server 2
    actor Bob as User B (Friend)

    Alice->>WS_A: 1. Send Location (lat: 37.77, lon: -122.41, ts: 10:00:00)
    par Cache & History Update
        WS_A->>Redis_Cache: 2. SET user:alice (lat, lon, ts) EX 600
    and Publish Update
        WS_A->>Redis_PubSub: 3. PUBLISH channel:alice (lat: 37.77, lon: -122.41)
    end
    
    Redis_PubSub-->>WS_B: 4. Message Delivered to Channel Subscriber (WS_B)
    Note over WS_B: 5. Fetch Bob's cached location & calculate distance
    alt Distance <= 5 miles
        WS_B->>Bob: 6. Push JSON: { friend_id: "alice", distance: "1.2 mi", ts: 10:00:00 }
    else Distance > 5 miles
        WS_B->>WS_B: 7. Drop message (No network overhead sent to Bob)
    end
```

---

## 4. Design Deep Dive: Scaling the Pub/Sub Cluster

### 1. Redis Pub/Sub Sizing & Sharding

To support $10\text{ Million}$ active channels ($1\text{ channel per active user}$):
- Memory per channel subscriber entry: $\approx 20\text{ bytes} \times 40\text{ subscribers} \approx 800\text{ bytes/channel}$.
- Total Channel Memory: $10\text{M channels} \times 800\text{ bytes} \approx \mathbf{8\text{ GB of RAM}}$ (Easily fits across a small Redis cluster).

```mermaid
flowchart TD
    ROUTER["Consistent Hash Ring Router"]
    
    ROUTER -->|channel_id % 3 == 0| R1[("Redis Pub/Sub Node 1")]
    ROUTER -->|channel_id % 3 == 1| R2[("Redis Pub/Sub Node 2")]
    ROUTER -->|channel_id % 3 == 2| R3[("Redis Pub/Sub Node 3")]
```

- **ZooKeeper Service Discovery**: WebSocket servers maintain a dynamic hash ring of Redis Pub/Sub nodes, automatically subscribing to the appropriate shard for each friend channel.

---

### 2. Client Lifecycle (Login, Movement, Logout)

```mermaid
stateDiagram-v2
    [*] --> OFFLINE
    OFFLINE --> ONLINE : App Opens (Establish WebSocket)
    ONLINE --> ACTIVE : Subscribe to all online friends' channels
    ACTIVE --> ACTIVE : Send location update every 30s
    ACTIVE --> OFFLINE : App Closed / 10m TTL Timeout (Unsubscribe all)
```

1. **Client Initialization**:
   - Client opens WebSocket.
   - Server loads friends list from User DB $\rightarrow$ Queries Redis Location Cache to find active friends $\rightarrow$ Subscribes to their Redis channels $\rightarrow$ Returns initial nearby friends list.
2. **Client Teardown**:
   - Connection closes $\rightarrow$ Server unsubscribes from all friend channels $\rightarrow$ Key expires in Redis cache after $10\text{ minutes}$.

---

## 5. Architectural Summary

```mermaid
mindmap
  root((Nearby Friends System))
    Ingress
      334K QPS Location Updates
      Persistent WebSockets (Keep-Alive)
    Message Bus
      Redis Pub/Sub (Channel per User)
      Consistent Hashing Shard Ring
      13.3M Fan-Out Messages / Sec
    Distance Filtering
      Server-Side Distance Calculation
      Drops updates if distance > 5 miles
    Lifecycle
      10-minute TTL expiration for inactive users
      ZooKeeper-driven cluster discovery
```

| Component | Technical Decision | Core Rationale |
|:---|:---|:---|
| **Protocol** | WebSockets | Low-overhead bidirectional communication over cellular networks. |
| **Message Bus** | Channel-per-User Redis Pub/Sub | Lightweight in-memory routing scaling to millions of dynamic channels. |
| **Location Cache** | Redis with 10-minute TTL | Automatic eviction of inactive friends without periodic background cleanup jobs. |
| **Egress Filtering** | Server-Side Distance Drop | Filters out $90\%$ of non-nearby friend updates before sending data over mobile networks. |

---

## References

1. Redis Pub/Sub Documentation: https://redis.io/topics/pubsub
2. Apache ZooKeeper for Cluster Coordination: https://zookeeper.apache.org/
3. Haversine Formula for Great-Circle Distance: https://en.wikipedia.org/wiki/Haversine_formula
