---
type: System Design Case
title: "Scale From Zero To Millions Of Users"
description: "A foundational guide detailing the step-by-step architectural evolution of scaling a web system from a single-server setup to millions of concurrent users with multi-tier decoupling, caching, CDNs, stateless web tiers, and database sharding."
tags: [system-design, distributed-systems, scalability, caching, cdn, database-sharding, load-balancing, microservices]
timestamp: 2026-08-22T00:00:00Z
---

# Scale From Zero To Millions Of Users

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 02  
> **Topic**: Foundational Scaling Principles, Horizontal vs. Vertical Scaling, Multi-Tier Decoupling, Database Replication & Sharding

---

## 1. Architectural Scaling Roadmap (From 1 to 10M+ Users)

Scaling a system is an iterative journey of eliminating single points of failure (SPOFs), removing bottlenecks, and decoupling tiers.

```mermaid
flowchart TD
    S1["1. Single Server<br/>(App + DB + Storage on 1 Box)"] --> S2["2. Separate Web Tier & Data Tier"]
    S2 --> S3["3. Load Balancer + Horizontal Web Tier"]
    S3 --> S4["4. DB Master-Slave Replication (Read/Write Split)"]
    S4 --> S5["5. Cache Tier (Redis) + CDN (Cloudflare)"]
    S5 --> S6["6. Stateless Web Tier (Shared Session Store)"]
    S6 --> S7["7. Multi-Region Data Centers (GeoDNS)"]
    S7 --> S8["8. Message Queues (Async Workers)"]
    S8 --> S9["9. Database Sharding & Microservices"]
```

### Transaction Load Evolution

The architecture changes when the current tier can no longer absorb the next order of magnitude of active users or peak transaction load. The figures below are illustrative planning estimates for a read-heavy web application; actual capacity depends on request complexity, payload size, storage latency, and availability targets.

```mermaid
flowchart LR
    M1["Stage 1<br/>1 active user<br/>1 peak TPS<br/>Single server"] --> M2["Stage 2<br/>100 active users<br/>10 peak TPS<br/>Separate data tier"]
    M2 --> M3["Stage 3<br/>1,000 active users<br/>100 peak TPS<br/>Load-balanced web tier"]
    M3 --> M4["Stage 4<br/>10,000 active users<br/>1,000 peak TPS<br/>Read replicas"]
    M4 --> M5["Stage 5<br/>100,000 active users<br/>10,000 peak TPS<br/>Cache and CDN"]
    M5 --> M6["Stage 6<br/>500,000 active users<br/>25,000 peak TPS<br/>Stateless web tier"]
    M6 --> M7["Stage 7<br/>1 million active users<br/>50,000 peak TPS<br/>Multi-region routing"]
    M7 --> M8["Stage 8<br/>5 million active users<br/>250,000 peak TPS<br/>Queues and workers"]
    M8 --> M9["Stage 9<br/>10 million plus active users<br/>500,000 plus peak TPS<br/>Sharded data tier"]
```

| Stage | Illustrative active users | Illustrative peak TPS | Architecture response |
|:---|---:|---:|:---|
| 1 | 1 | 1 | Run application, database, and storage on one server. |
| 2 | 100 | 10 | Separate the web tier from the data tier. |
| 3 | 1,000 | 100 | Add a load balancer and multiple web servers. |
| 4 | 10,000 | 1,000 | Add read replicas and route reads separately from writes. |
| 5 | 100,000 | 10,000 | Cache hot data and serve static assets through a CDN. |
| 6 | 500,000 | 25,000 | Move sessions to shared storage and keep web nodes stateless. |
| 7 | 1 million | 50,000 | Route users to nearby regions and replicate data across regions. |
| 8 | 5 million | 250,000 | Move slow work to queues and independently scalable workers. |
| 9 | 10 million plus | 500,000 plus | Shard durable data and split high-volume business capabilities. |

> **Sizing note:** TPS means peak application transactions per second, not necessarily database writes. A single transaction may produce several cache reads, database queries, or asynchronous events.

![Scale-to-millions target architecture showing GeoDNS and CDN at the edge, a load-balanced stateless web tier, cache-aside reads, asynchronous workers, and sharded databases.](resources/scale-to-millions/scale-to-millions-architecture.png)

**Diagram description:** Global users are routed through GeoDNS and a CDN to a load-balanced stateless web tier. The application serves hot reads from cache, sends slow work through a queue to independently scalable workers, and routes durable data to partitioned database shards.

[Open the interactive scale-to-millions target architecture diagram](resources/scale-to-millions/scale-to-millions-architecture.html)

---

## 2. Step-by-Step Scaling Evolution

### Stage 1: Single Server Setup

In the beginning, all application services, databases, and static assets run on a single physical host or virtual machine.

```mermaid
flowchart LR
    USER["User (Browser / Mobile)"] -->|1. DNS Lookup api.mysite.com| DNS["DNS Server"]
    DNS -->|2. Returns Public IP| USER
    USER -->|3. HTTP/HTTPS Request| APP["Single Server<br/>(Web Server + App Logic + MySQL DB)"]
```

#### Request Flow
1. User resolves domain name (`api.mysite.com`) to an IP address via DNS.
2. The client establishes an HTTP/S connection to the single server IP.
3. The server processes business logic, queries its local database, and returns JSON or HTML.

---

### Stage 2: Separate Web Tier and Data Tier

As traffic grows, separating the stateless compute layer from the stateful storage layer allows independent horizontal and vertical scaling.

```mermaid
flowchart LR
    CLIENT["Clients"] --> WEB["Web Tier<br/>(Node.js / Go / Django)"]
    WEB -->|Read / Write| DB[("Data Tier<br/>(PostgreSQL / MySQL)")]
```

#### Relational (SQL) vs. Non-Relational (NoSQL) Selection Matrix

| Criterion | Relational Database (RDBMS) | Non-Relational Database (NoSQL) |
|:---|:---|:---|
| **Examples** | MySQL, PostgreSQL, Oracle | MongoDB, DynamoDB, Cassandra, Redis |
| **Data Schema** | Strict, structured tables with foreign keys | Dynamic schema (Key-Value, Document, Wide-Column, Graph) |
| **ACID & Joins** | Native ACID transactions and complex multi-table `JOIN`s | Eventual consistency; joins executed at the application layer |
| **Best Used When** | Structured transactional data (E-Commerce, Banking, Accounting) | Unstructured data, massive write volume, ultra-low latency, big data |

---

### Stage 3: Load Balancing & Horizontal Web Tier Scaling

Vertical scaling (adding CPU/RAM) has physical ceilings and creates a single point of failure. Horizontal scaling (adding commodity servers behind a Load Balancer) provides high availability.

```mermaid
flowchart TD
    CLIENT["Clients (Web / Mobile)"] -->|Public IP| LB["Layer 7 / Layer 4 Load Balancer<br/>(NGINX / AWS ALB)"]
    
    subgraph WebTier["Stateless Web Server Farm (Private Subnet)"]
        LB -->|Private IP: 10.0.0.1| S1["Web Server 1"]
        LB -->|Private IP: 10.0.0.2| S2["Web Server 2"]
        LB -->|Private IP: 10.0.0.3| S3["Web Server N"]
    end

    S1 & S2 & S3 --> DB[("Primary Database")]
```

- **Health Checks**: The load balancer continuously monitors servers (`GET /healthz`) and removes unresponsive nodes instantly.
- **Security**: Web servers use private IPs and are unreachable directly from the public internet.

---

### Stage 4: Database Master-Slave Replication (Read/Write Separation)

Most web applications are read-heavy (e.g., $90\%$ reads, $10\%$ writes). Master-slave database replication scales read capacity and improves fault tolerance.

```mermaid
flowchart TD
    WEB["Web Tier"] -->|Write / Update / Delete| MASTER[("Primary DB (Master)<br/>Accepts All Writes")]
    MASTER -->|Binlog Async Replication| SLAVE1[("Read Replica 1")]
    MASTER -->|Binlog Async Replication| SLAVE2[("Read Replica 2")]
    
    WEB -->|Read Queries| SLAVE1
    WEB -->|Read Queries| SLAVE2
```

- **Failover**: If the Master crashes, a Read Replica is automatically promoted to Master (via orchestrators like Orchestrator / MHA).
- **Replication Lag**: Applications requiring immediate read-after-write consistency must direct critical reads to the Master directly.

---

### Stage 5: Caching Tier & Content Delivery Networks (CDN)

To prevent the database from becoming an I/O bottleneck, hot data is stored in memory (Redis/Memcached), and static media is cached at the edge (CDN).

```mermaid
flowchart LR
    CLIENT["Client"] -->|1. Request Static Asset| CDN["CDN Edge Cache (Cloudflare)"]
    CDN -.->|Cache Miss: Origin Fetch| ORIGIN["Origin Storage / S3"]
    
    CLIENT -->|2. Dynamic API Request| WEB["Web Server"]
    WEB -->|3. Cache Check| CACHE[("Redis Cache Cluster")]
    CACHE -.->|Cache Miss| DB[("Database")]
```

#### Cache Strategies & Considerations
1. **Cache-Aside Pattern**: Application checks cache $\rightarrow$ if miss, queries database $\rightarrow$ writes result back to cache.
2. **Eviction Policies**: LRU (Least Recently Used), LFU (Least Frequently Used), FIFO.
3. **Cache Invalidation & Expiration (TTL)**: Prevent stale data from lingering indefinitely.
4. **Stampede (Thundering Herd) Defense**: Use mutex locking or probabilistic early expiration.

---

### Stage 6: Stateless Web Tier (Shared Session Store)

To allow any web server to handle any incoming user request without session affinity (sticky sessions), session states are moved to a centralized distributed store.

```mermaid
flowchart TD
    CLIENT["Client A (Request 1 -> Server 1, Request 2 -> Server 2)"] --> LB["Load Balancer"]
    
    LB --> S1["Web Server 1 (Stateless)"]
    LB --> S2["Web Server 2 (Stateless)"]
    
    S1 & S2 <--> SESSION[("Centralized Session Store<br/>(Redis / DynamoDB)")]
    S1 & S2 <--> DB[("Database Cluster")]
```

- **Autoscaling**: Stateless web servers can scale dynamically from 2 to 200 nodes during traffic spikes without dropping logged-in sessions.

---

### Stage 7: Multi-Region Data Centers (GeoDNS)

Deploying across multiple geographic regions reduces latency for global users and provides disaster recovery.

```mermaid
flowchart TD
    USER_US["User (North America)"] -->|GeoDNS| DC_US["Data Center: US-East<br/>(Web Tier + Primary DB)"]
    USER_EU["User (Europe)"] -->|GeoDNS| DC_EU["Data Center: EU-West<br/>(Web Tier + Read Replica)"]

    DC_US <-->|Cross-Region DB Replication| DC_EU
```

---

### Stage 8: Message Queues & Asynchronous Worker Pipelines

Decoupling long-running tasks (e.g., video processing, image resizing, email sending) from the web request/response cycle improves user responsiveness.

```mermaid
flowchart LR
    WEB["Web Server (Producer)"] -->|1. Publish Task Event| MQ["Distributed Message Queue<br/>(RabbitMQ / Kafka)"]
    MQ -->|2. Pull Task| W1["Worker Service 1 (Consumer)"]
    MQ -->|2. Pull Task| W2["Worker Service 2 (Consumer)"]
    W1 & W2 -->|3. Update Result| DB[("Database")]
```

---

### Stage 9: Database Scaling (Horizontal Sharding)

When a single database server exhausts storage capacity ($> 10\text{ TB}$) or write IOPS, data is partitioned across multiple database shards.

```mermaid
flowchart TD
    APP["Application / Sharding Router"] -->|user_id % 4 == 0| SHARD0[("Shard 0 (User IDs: 0, 4, 8...)")]
    APP -->|user_id % 4 == 1| SHARD1[("Shard 1 (User IDs: 1, 5, 9...)")]
    APP -->|user_id % 4 == 2| SHARD2[("Shard 2 (User IDs: 2, 6, 10...)")]
    APP -->|user_id % 4 == 3| SHARD3[("Shard 3 (User IDs: 3, 7, 11...)")]
```

#### Sharding Challenges & Solutions
- **Resharding / Data Movement**: Solved via **Consistent Hashing**.
- **Celebrity / Hotspot Problem**: Append random salts to hot keys (e.g., `celebrity_id_01`).
- **Cross-Shard Joins**: Denormalize data schemas to allow single-shard query execution.

---

## 3. Comprehensive Target Architecture (Serving 10M+ Users)

```mermaid
flowchart TD
    subgraph EdgeTier["Edge & DNS"]
        USER["Global Users"] --> GEODNS["GeoDNS (Route 53)"]
        GEODNS --> CDN["CDN Edge Network"]
    end

    subgraph DC["Primary Cloud Data Center"]
        CDN --> LB["Redundant Load Balancers (Active-Passive)"]
        LB --> WEB1["Stateless Web Tier (Autoscaling Group)"]
        
        WEB1 <--> REDIS[("Distributed Cache Tier (Redis Cluster)")]
        WEB1 <--> SESS[("Shared Session Store")]
        
        WEB1 -->|Async Events| MQ["Message Queue (Kafka / RabbitMQ)"]
        MQ --> WORKERS["Background Processing Worker Pool"]
        
        WEB1 & WORKERS --> ROUTER["Database Sharding Proxy (Vitess / Citus)"]
        ROUTER --> S0[("DB Shard 0")]
        ROUTER --> S1[("DB Shard 1")]
        ROUTER --> SN[("DB Shard N")]
    end
```

---

## 4. Architectural Summary Checklist

```mermaid
mindmap
  root((Scaling from 0 to 10M))
    Web Tier
      Keep web servers stateless
      Deploy behind Layer 7 Load Balancers
      Autoscale on CPU/Request count
    Caching & Edge
      Cache static assets via CDN
      Cache database reads via Redis/Memcached
      Apply TTL and LRU eviction
    Data Tier
      Separate read and write paths (Master-Slave)
      Choose SQL for ACID, NoSQL for unconstrained scale
      Shard databases by high-cardinality partition keys
    Asynchrony & Resilience
      Decouple slow tasks via Message Queues
      Deploy across multiple Geographic Regions
      Implement comprehensive Metrics, Logging & Tracing
```

| Area | Core Technique | Scaling Benefit |
|:---|:---|:---|
| **Compute** | Stateless Web Tier + Load Balancer | Horizontal scaling without state loss; zero-downtime rolling deploys. |
| **Edge** | Content Delivery Network (CDN) | Sub-millisecond latency for static media; shields origin servers. |
| **Memory** | Redis / Memcached Cache-Aside | Eliminates $80\text{–}90\%$ of relational database read load. |
| **Data Reads** | Primary-Replica Replication | Scales read queries across multiple read replicas. |
| **Data Writes** | Horizontal Sharding | Scales write throughput and storage linearly across database instances. |
| **Decoupling** | Asynchronous Message Queues | Isolates background spikes and guarantees eventual consistency. |

---

## References

1. Hypertext Transfer Protocol: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
2. Scaling Memcache at Facebook: https://www.usenix.org/system/files/conference/nsdi13/nsdi13-nishtala.pdf
3. Sharding Pinterest: How we scaled our database to 100M users: https://medium.com/pinterest-engineering/sharding-pinterest-how-we-scaled-our-mysql-fleet-3f341e96ca6f
4. Vitess: Horizontal Scaling for MySQL: https://vitess.io/
