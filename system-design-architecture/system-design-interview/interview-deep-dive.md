---
type: System Design
title: "System Design Learning Roadmap — Key Takeaways"
description: "Vertical vs horizontal scaling, caching, CAP theorem, replication, sharding, and real-world design patterns — a no-BS system design learning guide"
timestamp: 2026-06-16T00:00:00Z
---

# 34. System Design Learning Roadmap — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [How I Finally Learned System Design (After Feeling Totally Lost)](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)
> **Purpose**: Extract reusable architectural concepts and learning patterns from the system design self-study roadmap.

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — 7-phase interview structure, NFR quantification, quorum vs consensus
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Caching](../../reference-dictionary/caching.md)
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
| [sdi-22](#sdi-22) | Starting to draw before clarifying requirements | Requirements first, architecture second — interview as conversation |
| [sdi-23](#sdi-23) | Ignoring what the company actually cares about | Tailor the design to the company's known engineering priorities |
| [sdi-24](#sdi-24) | Optimizing for scale you'll never reach | Design for current scale + one order of magnitude, not three |
| [sdi-25](#sdi-25) | Presenting solutions like universal facts | Every choice needs a justification and an explicit trade-off |
| [sdi-26](#sdi-26) | Knowing where components go but not why | Explain the reasoning, failure modes, and invalidation strategy |
| [sdi-27](#sdi-27) | Memorizing patterns instead of learning to think | Decompose the problem and adapt when requirements change |

---

## sdi-16: Vertical vs Horizontal Scaling — The Pizza Shop Analogy

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — NFR quantification, scaling assessment
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure VM scale sets (horizontal), Azure vertical scaling via resizing
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-17: Caching Fundamentals — Keep Popular Results Ready

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Cache stampede, invalidation, eviction policies
> **Dictionary**: [Caching](../../reference-dictionary/caching.md)
> **Azure**: Azure Cache for Redis, Azure CDN
> **Taxonomy**: §7.3 Caching Strategies

---

## sdi-18: Latency vs Throughput — Two Different Goals

> **Source**: [§"2. System Design for Beginners: The Stop Overcomplicating It Phase"](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — NFR quantification
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-19: CAP Theorem — The Triangle of Sadness

> **Source**: [§"3. How to Learn System Design from Scratch (The No-BS Roadmap)" / Phase 2](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [Databases & Query Performance](databases/query-performance.md) — DB selection, CAP in practice
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Cosmos DB offers 5 consistency levels from Strong to Eventual — tunable CAP
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-20: Replication & Sharding — Scale Beyond One Database

> **Source**: [§"3. How to Learn System Design from Scratch (The No-BS Roadmap)" / Phase 3](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [Databases & Query Performance](databases/query-performance.md) — Hot partitions, DB migration at scale
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure SQL Database geo-replication, Cosmos DB automatic sharding, Hyperscale for large databases
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## sdi-21: Design Tradeoffs — There Is No "Best" Design

> **Source**: [§"4. Real-World Thinking" and "Final Thoughts"](../../articles/system-design-interview/How I Finally Learned System Design (After Feeling Totally Lost).md)

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

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — Trade-off maturity, decision frameworks
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Well-Architected Framework — tradeoffs across Cost, Security, Reliability, Operations, Performance
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-22: Clarify Before You Draw

> **Source**: [§"Mistake 1: They Start Drawing Before They Start Thinking"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Candidate starts drawing boxes before understanding what problem the system actually solves |
| **Root cause** | Treating the interview as a template-filling exercise rather than a requirements conversation |

**Strategy**: Spend the first 10–15 minutes asking clarifying questions before touching the whiteboard. Cover primary use case, read-to-write ratio, geographic scope, and the consistency vs availability trade-off. State assumptions explicitly so the interviewer can correct them.

| Clarifying question | Why it matters |
|:---|:---|
| "Feed generation or photo upload?" | Determines hot path and storage/caching strategy |
| "What is the read-to-write ratio?" | Drives cache sizing, database choice, and fan-out strategy |
| "Global users or single region?" | Affects CDN, replication, and latency requirements |
| "Consistency or availability?" | Determines whether to favor ACID or eventual consistency |

| Tradeoff | Detail |
|:---|:---|
| **Slower start, better fit** | Asking questions delays diagramming but produces an architecture that matches the actual constraints |
| **Template dumping looks confident but fails** | Reciting a memorized stack signals pattern matching, not design thinking |

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — 7-phase interview structure
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure Well-Architected Framework — requirements drive service selection
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-23: Design for the Company, Not the Textbook

> **Source**: [§"Mistake 2: They Ignore What the Company Actually Cares About"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Architecture is technically sound but ignores the specific priorities of the hiring company |
| **Root cause** | One-size-fits-all thinking; not calibrating the design to the interviewer's organizational context |

**Strategy**: Before the interview, research the company's publicly known engineering values. During the interview, ask which non-functional requirements matter most and weight your trade-offs accordingly.

| Company | Typical priority | Implication for design discussion |
|:---|:---|:---|
| **Google/Meta** | Infinite scale, social graph, real-time delivery | Emphasize partitioning, replication, and latency at billion-user scale |
| **Amazon** | Cost efficiency and operational rigor | Lead with cost estimates, reserved capacity, and simplest viable architecture |
| **Netflix** | Resilience above all | Discuss chaos engineering, regional failover, and graceful degradation |
| **Fintech** | Correctness and consistency | Favor ACID, idempotency, and audit trails over raw throughput |

| Tradeoff | Detail |
|:---|:---|
| **Generic correctness vs contextual fit** | A textbook answer can be technically perfect and still fail because it does not address the interviewer's real concerns |
| **Company-specific vocabulary matters** | Using the same terms the company uses (e.g., "blast radius," "error budget") signals preparation |

> **Also see**: [Pragmatic System Design](system-design-interview/pragmatic-takeaways.md) — user metrics and operational reality
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure Well-Architected Framework pillars — Cost Optimization, Reliability, Performance Efficiency
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-24: Design for Reality, Not Fantasy Scale

> **Source**: [§"Mistake 3: They Optimize for Scale They’ll Never Reach"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Candidate designs for 1B requests/second when the company handles 5K |
| **Root cause** | Confusing "planning for growth" with overengineering; inability to estimate realistic scale |

**Strategy**: Target current scale plus one order of magnitude. Choose the simplest technology that satisfies the constraints, and make the next scaling decision explicit and reversible.

| Scenario | Over-engineered choice | Pragmatic choice |
|:---|:---|:---|
| Dataset fits on one disk | Cassandra cluster | PostgreSQL |
| 100 events/second task queue | Kafka cluster | RabbitMQ or in-process queue |
| Single monolith with low traffic | Kubernetes | Single VM or container instance |
| 2M-user URL shortener | Custom distributed ID generator | Single-node DB + cache |

| Tradeoff | Detail |
|:---|:---|
| **Simplicity vs future-proofing** | Designing for +1 order of magnitude keeps the system evolvable without paying complexity costs today |
| **Resume-driven design is a red flag** | Choosing trendy distributed tools for trivial scale signals poor judgment |

> **Also see**: [Pragmatic System Design](system-design-interview/pragmatic-takeaways.md) — solve today's problems
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Databases](../../reference-dictionary/databases.md)
> **Azure**: Azure Database for PostgreSQL, Azure Service Bus, Azure Container Apps — scale vertically first
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-25: Defend Every Decision with Trade-offs

> **Source**: [§"Mistake 4: They Present Solutions Like They’re Facts"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Candidate asserts technology choices as universally correct without justification |
| **Root cause** | Memorized "best" stacks instead of understanding constraints and alternatives |

**Strategy**: For every technology choice, present the decision in the form: "I choose X over Y because of constraint Z. The trade-off is W." If you do not know the alternative, say so and explain how you would evaluate it.

| Choice | Weak answer | Strong answer |
|:---|:---|:---|
| Redis vs Memcached | "Redis is better." | "Redis for data structures and persistence; Memcached for pure, simple caching." |
| Microservices vs monolith | "We need microservices." | "Start with monolith until team/scale boundaries justify the operational cost of services." |
| NoSQL vs SQL | "NoSQL scales better." | "SQL if relationships and ACID matter; NoSQL if flexible schema and horizontal write scale matter." |
| Kafka vs RabbitMQ | "Kafka is the standard." | "Kafka for high-throughput event log; RabbitMQ for complex routing and lower volume." |

| Tradeoff | Detail |
|:---|:---|
| **Conviction vs intellectual honesty** | Strong opinions need to be paired with the conditions under which they are wrong |
| **Speed vs depth** | Justifying each choice takes longer but is the primary signal of seniority in system design |

> **Also see**: [Databases & Query Performance](databases/query-performance.md) — SQL vs NoSQL, CAP in practice
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Caching](../../reference-dictionary/caching.md), [Messaging](../../reference-dictionary/messaging.md)
> **Azure**: Azure Cache for Redis, Azure Cosmos DB, Azure Service Bus, Azure Event Hubs
> **Taxonomy**: §2.1 Application Architecture Styles

---

## sdi-26: Explain the Why, Not Just the Where

> **Source**: [§"Mistake 5: They Can’t Explain Why"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Candidate can place components on a diagram but cannot explain their purpose or failure behavior |
| **Root cause** | Memorized the visual layout without understanding the mechanics underneath |

**Strategy**: For each component, be ready to explain why it is there, what happens on the happy path, what happens on failure, and how the system recovers. Use concrete numbers where possible (cache hit rate, p99 latency, replication lag).

| Component | Why it is there | What to explain |
|:---|:---|:---|
| **Cache** | Reduce DB load and latency | Hit rate, miss behavior, invalidation strategy, eviction policy |
| **Load balancer** | Distribute traffic and enable horizontal scaling | Health checks, session affinity, failover |
| **Message queue** | Decouple producers and consumers | Ordering guarantees, retries, DLQ, consumer lag |
| **Database replica** | Scale reads and improve availability | Replication lag, stale reads, failover |

| Tradeoff | Detail |
|:---|:---|
| **Diagram completeness vs operational depth** | A simple diagram with deep explanations beats a crowded diagram with shallow explanations |
| **Memorization vs debugging skill** | In production, "that's where it goes" does not help when cache hit rate drops to 40% |

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — cache invalidation, eviction, stampede
> **Dictionary**: [Caching](../../reference-dictionary/caching.md), [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure Cache for Redis, Azure Load Balancer, Azure SQL Database geo-replication
> **Taxonomy**: §7.3 Caching Strategies

---

## sdi-27: Pattern Matching Is Not Design

> **Source**: [§"Mistake 6: They Memorized Patterns Instead of Learning to Think"](../../articles/system-design-interview/I’ve Reviewed 50+ System Design Interviews. These 6 Mistakes Eliminated 90% of Candidates..md)

| | |
|:---|:---|
| **Problem** | Candidate freezes when the interviewer changes one requirement |
| **Root cause** | Relied on memorized templates instead of learning to decompose problems and reason from first principles |

**Strategy**: Practice deriving designs from requirements rather than recalling templates. When a requirement changes, identify which assumptions it invalidates and adjust the affected components only.

| Pattern matcher | Actual designer |
|:---|:---|
| "Design Twitter → use template X" | "Break Twitter into posting, timeline, fan-out, search, and media — then choose per constraint" |
| Recites token bucket for rate limiter | Adapts token bucket when asked about purchasable quota by adding account-specific buckets |
| Adds Redis because diagrams have Redis | Adds Redis only after proving the workload is read-heavy and cacheable |

| Tradeoff | Detail |
|:---|:---|
| **Template speed vs adaptability** | Templates get you started faster but break down under novel constraints |
| **Breadth vs depth** | Knowing fewer patterns deeply and how to compose them beats knowing many patterns superficially |

**Adaptive design framework**:

1. Clarify the problem
2. Define constraints (scale, latency, consistency, cost)
3. Start with the simplest design that could work
4. Identify bottlenecks
5. Optimize with explicit trade-off discussions
6. Explain why for every decision

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — trade-off maturity and decision frameworks
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)
> **Azure**: Azure Well-Architected Framework — make trade-offs explicit across pillars
> **Taxonomy**: §2.1 Application Architecture Styles
