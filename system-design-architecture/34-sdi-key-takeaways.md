---
type: System Design
title: "System Design Learning Roadmap — Key Takeaways"
description: "Vertical vs horizontal scaling, caching, CAP theorem, replication, sharding, and real-world design patterns — a no-BS system design learning guide"
timestamp: 2026-06-16T00:00:00Z
---

# 34. System Design Learning Roadmap — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [How I Finally Learned System Design (After Feeling Totally Lost)](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)
> **Purpose**: Extract reusable architectural concepts and learning patterns from the system design self-study roadmap.

> **Also see**: [System Design Interview Roadmap](15-system-design-interview-roadmap.md) — 7-phase interview structure, NFR quantification, quorum vs consensus
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md), [Caching](../reference-dictionary/caching.md)
> **Taxonomy Reference**: §2.1 Application Architecture Styles

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [sdi-16](#sdi-16) | Confusing vertical and horizontal scaling | Vertical = bigger machine; Horizontal = more machines + load balancer |
| [sdi-17](#sdi-17) | Not understanding caching fundamentals | Keep popular results ready so you don't recompute from scratch |
| [sdi-18](#sdi-18) | Confusing latency and throughput | Latency = time per request; Throughput = requests per second |
| [sdi-19](#sdi-19) | Not knowing which two of CAP to sacrifice | CAP Theorem: pick two of Consistency, Availability, Partition Tolerance |
| [sdi-20](#sdi-20) | Single database becomes bottleneck | Replication (copies for safety) + Sharding (splitting for scale) |
| [sdi-21](#sdi-21) | Chasing "the best design" | There are only design tradeoffs — every optimization adds complexity |

---

## sdi-16: Vertical vs Horizontal Scaling — The Pizza Shop Analogy

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | Beginners assume scalability means buying a bigger computer — which hits physical limits and becomes exponentially expensive |
| **Root cause** | Vertical scaling (bigger server) is the intuitive first answer; horizontal scaling (more servers) requires architectural change |

**Strategy**: Think of a pizza shop. When 1,000 people show up, you can't just tell the chef to "cook faster" (vertical scaling). You need more chefs (horizontal scaling) and a host at the door directing customers (load balancer).

```
Vertical Scaling (scale up):         Horizontal Scaling (scale out):
+------------------+                 +----+  +----+  +----+
|  BIGGER SERVER   |                 | S1 |  | S2 |  | S3 |
|  (more CPU/RAM)  |                 +----+  +----+  +----+
+------------------+                      \    |    //
        |                               +-----------+
     Clients                            | Load      |
                                        | Balancer  |
                                        +-----------+
                                             |
                                          Clients
```

| Approach | Pros | Cons |
|:---|:---|:---|
| **Vertical** | Simple, no code changes | Physical limit, expensive, single point of failure |
| **Horizontal** | Infinite scale, fault tolerance | Requires load balancing, stateless design, data partitioning |

| Tradeoff | Detail |
|:---|:---|
| **Vertical is not wrong** | For early-stage apps, a bigger server is simpler and faster to deploy |
| **Horizontal requires redesign** | Session state, file storage, and database must be externalized |

> **Also see**: [System Design Interview Roadmap](15-system-design-interview-roadmap.md) — NFR quantification, scaling assessment
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure VM scale sets (horizontal), Azure vertical scaling via resizing
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-17: Caching Fundamentals — Keep Popular Results Ready

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | Recomputing the same expensive result for every request wastes CPU and adds latency |
| **Root cause** | Not recognizing that read-heavy workloads benefit from pre-computed, stored results |

**Strategy**: Keep the most popular "pizzas" already made on the counter so you don't cook them from scratch every time. Caching is the difference between serving in 50ms (cache hit) and 500ms (compute from scratch).

```
Without caching:                      With caching:
Client -> Server -> DB (every time)   Client -> Cache (hit? return)
                                               |
                                               v (miss)
                                          Server -> DB -> Cache -> Client
```

| Cache Level | What it caches | Example |
|:---|:---|:---|
| **Client-side** | Browser cache, mobile local storage | HTTP Cache-Control headers |
| **CDN** | Static assets, images, video chunks | CloudFront, Akamai |
| **Application cache** | Computed results, API responses | Redis, Memcached |
| **Database cache** | Query results, buffer pool | PostgreSQL shared_buffers, MySQL InnoDB buffer |

| Tradeoff | Detail |
|:---|:---|
| **Staleness** | Cached data may be out of date — TTL and invalidation are essential |
| **Memory cost** | Cache uses RAM which is expensive — evict what's not used |

> **Also see**: [Caching Architecture](03-caching-architecture.md) — Cache stampede, invalidation, eviction policies
> **Dictionary**: [Caching](../reference-dictionary/caching.md)
> **Azure**: Azure Cache for Redis, Azure CDN
> **Taxonomy**: §7.3 Caching Strategies

---

## sdi-18: Latency vs Throughput — Two Different Goals

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | Engineers optimize throughput when the user experience depends on latency, or vice versa |
| **Root cause** | Latency and throughput are conflated as "performance" — but they're independent and often trade off against each other |

**Strategy**: Recognize them as separate metrics. Latency is how long one pizza takes to reach a table. Throughput is how many pizzas you can push out per hour. You want both to be good, but optimizing one often hurts the other.

| | Latency | Throughput |
|:---|:---|:---|
| **Definition** | Time to process one request | Requests processed per unit time |
| **Unit** | Milliseconds (ms) | Requests per second (RPS) |
| **User impact** | Perceived responsiveness | System capacity under load |
| **Optimized by** | Caching, CDN, async, connection pooling | Parallelism, batching, partitioning |

| Tradeoff | Detail |
|:---|:---|
| **Batching increases throughput** | Process 100 messages at once = higher throughput, but each message waits longer (higher latency) |
| **Caching reduces latency** | Pre-computed results = faster response, but cache misses add latency variability (tail latency) |

> **Also see**: [System Design Interview Roadmap](15-system-design-interview-roadmap.md) — NFR quantification
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-19: CAP Theorem — The Triangle of Sadness

> **Source**: [§"3. How to Learn System Design from Scratch (The No-BS Roadmap)" / Phase 2](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | Distributed systems force you to choose between Consistency, Availability, and Partition Tolerance — you cannot have all three |
| **Root cause** | Network partitions are inevitable in distributed systems; during a partition, you must choose between being consistent (refuse writes) or available (accept writes, risk inconsistency) |

**Strategy**: In any distributed system, you can only guarantee two of the three. It's the adult version of "Fast, Cheap, Good — pick two." Prepare to defend your choice.

```
CAP Theorem:
     Consistency
        /\
       /  \
      /    \
     /  CA  \
    /        \
Availability -------- Partition Tolerance
        AP       CP

CA: Single-node databases (no partition tolerance needed)
CP: Sacrifice availability during partition (HBase, MongoDB default)
AP: Sacrifice consistency during partition (Cassandra, DynamoDB, Cosmos DB)
```

| Choice | Sacrifice | Best for | Example Systems |
|:---|:---|:---|:---|
| **CP** (Consistency + Partition Tolerance) | Availability | Financial ledgers, inventory | HBase, Zookeeper, etcd |
| **AP** (Availability + Partition Tolerance) | Strong consistency | Social feeds, shopping carts | Cassandra, DynamoDB, Cosmos DB |
| **CA** (Consistency + Availability) | Partition tolerance | Single-node databases only | PostgreSQL, MySQL (single node) |

| Tradeoff | Detail |
|:---|:---|
| **CAP is a spectrum** | Modern systems tune consistency levels (e.g., Cassandra's QUORUM gives tunable consistency) |
| **PACELC extension** | When there IS a partition (P), choose A or C. Else (E), choose Latency or Consistency |

> **Also see**: [Databases & Query Performance](01-databases-query-performance.md) — DB selection, CAP in practice
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Azure**: Cosmos DB offers 5 consistency levels from Strong to Eventual — tunable CAP
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-20: Replication & Sharding — Scale Beyond One Database

> **Source**: [§"3. How to Learn System Design from Scratch (The No-BS Roadmap)" / Phase 3](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | A single database becomes the bottleneck — both for read throughput and storage capacity |
| **Root cause** | Monolithic database handles all reads and writes; as data and traffic grow, one machine can't keep up |

**Strategy**: Two complementary techniques:
- **Replication**: Copy data to replicas so reads scale horizontally and one server failure doesn't lose data
- **Sharding**: Split data across multiple databases so writes and storage scale horizontally

```
Replication (copy for safety + read scale):    Sharding (split for write scale):
                                               
Primary  →  Replica1                           Shard A: users A-M
   |       /                                    Shard B: users N-Z
   |      /                                     Shard C: users 0-9
   v     v                                             
Replica2                                        Each shard handles its own
                                                reads + writes independently
Writes: Primary only
Reads: Any replica
```

| Technique | Solves | Key Challenge |
|:---|:---|:---|
| **Replication** | Read throughput, fault tolerance | Replication lag (stale reads from replicas) |
| **Sharding** | Write throughput, storage capacity | Cross-shard queries, rebalancing |

| Tradeoff | Detail |
|:---|:---|
| **Replication lag** | Reads from replicas may return stale data — use primary for writes-then-reads |
| **Sharding complexity** | Joins across shards are impossible; denormalize or use application-level joins |
| **Both together** | Real systems use sharded primaries with replicated shard copies |

> **Also see**: [Databases & Query Performance](01-databases-query-performance.md) — Hot partitions, DB migration at scale
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure SQL Database geo-replication, Cosmos DB automatic sharding, Hyperscale for large databases
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## sdi-21: Design Tradeoffs — There Is No "Best" Design

> **Source**: [§"4. Real-World Thinking" and "Final Thoughts"](../articles/medium/How%20I%20Finally%20Learned%20System%20Design%20(After%20Feeling%20Totally%20Lost).md)

| | |
|:---|:---|
| **Problem** | Engineers chase "the best architecture" as if there's one correct answer — then freeze in design discussions |
| **Root cause** | System design is taught as a set of "correct patterns" rather than a framework for evaluating tradeoffs |

**Strategy**: Accept that every design decision is a tradeoff. Adding a cache makes reads faster but introduces staleness and memory cost. Sharding scales writes but breaks cross-shard queries. The goal isn't perfection — it's **thoughtfulness** about which tradeoffs you're making and why.

**Real-world pattern recognition** — study how large systems embody tradeoffs:

| System | Pattern | Tradeoff Made |
|:---|:---|:---|
| **Netflix** | CDN + Microservices | Accepts eventual consistency for global availability |
| **Uber** | Geospatial indexing (H3) | Specialized index for real-time matching, sacrifices general-purpose query flexibility |
| **Twitter/X** | Fan-out on write | Pre-compute timelines at post time (high write amplification) for fast reads |

| Tradeoff | Detail |
|:---|:---|
| **Every optimization adds complexity** | Faster = more components = harder to debug |
| **Theory vs practice** | You won't truly understand until you've seen a system fail in production |
| **Start simple** | Don't design for Twitter-scale when you have 100 users — most complexity is premature |

> **Also see**: [System Design Interview Roadmap](15-system-design-interview-roadmap.md) — Trade-off maturity, decision frameworks
> **Dictionary**: [Architecture Patterns](../reference-dictionary/architecture-patterns.md)
> **Azure**: Well-Architected Framework — tradeoffs across Cost, Security, Reliability, Operations, Performance
> **Taxonomy**: §2.1 Application Architecture Styles
