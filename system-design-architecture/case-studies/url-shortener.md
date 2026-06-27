---
type: System Design
title: "URL Shortener — Key Takeaways"
description: "Pre-allocated key generation, cache-aside redirection, CAP trade-offs, and multi-region URL shortening at billion-scale"
timestamp: 2026-06-20T00:00:00Z
---

# 41. URL Shortener — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Question 1: Design a URL Shortener Service (like TinyURL)](../system-design-cases/cases/part-2-url-shortener-system-design.md)
> **Purpose**: Extract reusable architectural patterns from designing a TinyURL-scale URL shortening service.

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Cache stampede, invalidation, eviction policies
> **Dictionary**: [Caching](../../reference-dictionary/caching.md), [API Design](../../reference-dictionary/api-design.md)
> **Taxonomy Reference**: §4.0.1 Database Performance & Caching

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [url-01](#url-01) | How to generate billions of unique short codes without collisions | Pre-allocated ID ranges + Base62 encoding |
| [url-02](#url-02) | Redirecting 10B URLs/month with p99 < 10 ms | Cache-aside Redis + regional DynamoDB fallback |
| [url-03](#url-03) | Custom aliases must be globally unique | Atomic check-and-set with ConditionExpression |
| [url-04](#url-04) | Writes need strong consistency; reads need low latency | CAP split: CP for shortening, AP for redirection |
| [url-05](#url-05) | Analytics on massive click streams without blocking redirects | Async Kafka ingestion + ClickHouse OLAP |

---

## url-01: Unique Short-Code Generation at Scale

> **Source**: [§"High‑Level Architecture"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | Hashing long URLs on-the-fly causes collisions, requires read-before-write retries, and complicates scaling |
| **Root cause** | Deterministic hashes of arbitrary input inevitably collide; collision resolution slows the write path and adds coordination |

**Strategy**: Use a dedicated **Key Generation Service** that pre-allocates disjoint 64-bit integer ranges to each worker. Workers increment their local counter and encode the value as a fixed 7-character **Base62** string (62⁷ ≈ 3.5 trillion codes). If a worker crashes, only its unused range is lost — acceptable because the namespace is enormous.

| Approach | Pros | Cons |
|:---|:---|:---|
| **Pre-allocated ranges** | No collision checks, O(1) generation, scales horizontally | Wastes unused IDs on worker failure; requires a range coordinator |
| **Hash + collision probe** | No coordinator dependency | Read-before-write, retries, hot keys under load |
| **ZooKeeper/etcd ranges** | Strong coordination | Adds consensus dependency, overkill for a counter |

| Tradeoff | Detail |
|:---|:---|
| **Key length vs namespace** | 7 characters balances brevity with trillions of possible codes |
| **Coordinator as SPOF** | Standby coordinator with replicated sequence eliminates the single point of failure |
| **Range size** | Larger ranges reduce coordinator chatter but increase ID waste on failure |

> **Also see**: [System Design Interview Roadmap](system-design-interview/interview-roadmap.md) — Back-of-the-envelope estimation
> **Dictionary**: [Base62 Encoding](../../reference-dictionary/architecture-patterns.md#base62-encoding), [Snowflake ID](../../reference-dictionary/architecture-patterns.md#snowflake-id)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/redis/) for hot-code serving, Cosmos DB (in `architecture-azure/data/databases/`) for durable mappings
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## url-02: Low-Latency Redirection via Cache-Aside

> **Source**: [§"Redirect Flow with Cache‑Aside Pattern and Analytics"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | 10B redirects/month with p99 < 10 ms cannot be served from a database on every request |
| **Root cause** | Database round-trips, cross-region latency, and write-heavy contention make direct DB serving too slow and expensive |

**Strategy**: Separate the read and write paths. Store mappings in a regional NoSQL database (DynamoDB/Cassandra) and keep hot aliases in **Redis with cache-aside** semantics. On a redirect: check Redis; on miss, load from DB, populate Redis, and return 301/302. Active set (~100M entries ≈ 25 GB) easily fits in memory.

| Component | Responsibility | Latency target |
|:---|:---|:---|
| **Redis cache hit** | Serve redirect directly | < 2 ms |
| **Cache miss → DB** | Fallback to strongly consistent DB | < 10 ms p99 |
| **CDN edge** | Cache 301 redirects geographically close to users | Sub-ms for viral URLs |

| Tradeoff | Detail |
|:---|:---|
| **Staleness vs availability** | Cache provides AP semantics; acceptable because short URLs are immutable |
| **Memory cost** | Hot-set caching adds Redis infrastructure but avoids billions of DB reads |
| **Thundering herd** | Viral short codes can saturate a single cache key; mitigate with request coalescing or CDN edge caching |

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Cache stampede, eviction policies
> **Dictionary**: [Cache-Aside Pattern](../../reference-dictionary/caching.md#cache-aside-pattern), [TTL](../../reference-dictionary/caching.md#ttl-time-to-live)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/redis/), Azure Front Door for edge redirects
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## url-03: Atomic Custom Alias Reservation

> **Source**: [§"Custom Alias Flow (Conflict Check)"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | Two clients can propose the same custom alias simultaneously; only one must succeed |
| **Root cause** | Application-level check-then-write races across distributed instances |

**Strategy**: Rely on the database for atomicity. Use DynamoDB `PutItem` with `ConditionExpression: attribute_not_exists(alias)` or an equivalent unique constraint. The first writer wins; the second receives a 409 Conflict. This is a **CP** choice over AP for the write path.

| Tradeoff | Detail |
|:---|:---|
| **Latency cost** | Conditional write is slightly slower than blind write but guarantees correctness |
| **User experience** | Immediate failure (409) is preferable to silently overwriting someone else's alias |
| **No app locks** | Database-level atomicity avoids distributed locking complexity |

> **Also see**: [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md) — Double-booking, database invariants
> **Dictionary**: [ACID](../../reference-dictionary/data-concurrency.md#acid-transactions)
> **Azure**: Cosmos DB unique keys; [Azure Cache for Redis](../../architecture-azure/data/redis/) SET NX for pre-check
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## url-04: Splitting CAP by Operation Type

> **Source**: [§"Consistency vs. Availability Trade‑offs"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | A single CAP choice cannot satisfy both uniqueness guarantees and ultra-low-latency redirects |
| **Root cause** | Strong consistency requires coordination; low-latency reads prefer local serving |

**Strategy**: Make **operation-specific CAP choices**. The shortening path is **CP** — unique aliases are non-negotiable. The redirection path is **AP** — serve from cache, fall back to DB, and accept eventual consistency because aliases are immutable after creation.

| Path | CAP | Mechanism |
|:---|:---|:---|
| **Shorten** | CP | Pre-generated unique IDs + atomic custom-alias condition |
| **Redirect** | AP | Redis cache-aside + DB fallback + stale-cache contingency |

| Tradeoff | Detail |
|:---|:---|
| **Complexity** | Two consistency models in one service require clear documentation and monitoring |
| **Failure mode** | DB outage can still serve redirects from cache; writes pause until coordinator recovers |
| **Correctness** | No two long URLs ever share the same alias, even during partitions |

> **Also see**: [Databases & Query Performance](databases/query-performance.md) — CAP theorem
> **Dictionary**: [CAP Theorem](../../reference-dictionary/architecture-patterns.md#cap-theorem)
> **Azure**: Cosmos DB consistency levels for tunable per-operation guarantees
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## url-05: Decoupled Click Analytics

> **Source**: [§"Redirect Flow with Cache‑Aside Pattern and Analytics"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | Recording every click synchronously would destroy redirect latency SLOs |
| **Root cause** | OLAP writes are slow and bursty; the redirect hot path must stay lean |

**Strategy**: Produce click events to **Kafka** asynchronously during redirect and process them with **Flink** (exactly-once) into **ClickHouse** for analytics. The redirect itself returns immediately; analytics lag is acceptable.

| Component | Role |
|:---|:---|
| **Kafka** | Durable, high-throughput click-event ingestion |
| **Flink** | Exactly-once aggregation and counting |
| **ClickHouse** | Fast OLAP queries over billions of events |

| Tradeoff | Detail |
|:---|:---|
| **Latency vs correctness** | Analytics are eventually consistent but accurate; redirects remain fast |
| **Cost** | Separate analytics pipeline adds infrastructure but keeps primary serving path cheap |
| **Scalability** | Topic partitioning by alias shard balances load |

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md) — Producer durability, exactly-once semantics
> **Dictionary**: [Apache Kafka](../../reference-dictionary/messaging.md#apache-kafka)
> **Azure**: [Azure Event Hubs](../../architecture-azure/integration/event-hubs/) for click ingestion, [Azure Data Explorer](../../architecture-azure/data/analytics/data-explorer/) for OLAP
> **Taxonomy**: §4.2 Analytics Architecture

---

> **Related topics**: [News Feed — Key Takeaways](case-studies/news-feed.md) — Hybrid fanout, timeline caches, celebrity problem
