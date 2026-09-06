---
type: System Design
title: "URL Shortener Viral Hot-Key & CDN Redirect Caching — Key Takeaways"
description: "CDN edge caching for HTTP redirects, Redis Cluster hot-key limitations, local in-memory caching, request coalescing, and systematic troubleshooting methodology for read-heavy systems under viral traffic"
generated: { by: process:okf-migrate, at: 2026-07-13T00:00:00Z }
---

# 62. URL Shortener Viral Hot-Key & CDN Redirect Caching — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [URL Shortener Suddenly Crashes During IPL Finals: How Will You Fix?](../../articles/caching/url-shortener-viral-hotkey-cdn-caching.md)
> **Purpose**: Extract reusable strategies for surviving viral traffic spikes in read-heavy systems: CDN edge caching for non-static content, Redis Cluster hot-key limitations, and a structured diagnostic methodology.

> **Also see**: [Hot Keys & Skewed Workloads](caching/hot-keys-skewed-workloads.md) — Hot-key replication, local L1 cache, counter sharding, hot-key detection, dedicated hot-key tier
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — Hot key, request coalescing, CDN, cache hit ratio
> **Taxonomy Reference**: §7.3 Caching Strategies

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-31](#cache-31) | Backend collapses under viral redirect traffic for a single short URL | CDN edge caching for HTTP redirect responses |
| [cache-32](#cache-32) | Redis Cluster hash-based sharding fails to distribute load for a single hot key | Redis Cluster hot-key limitation and mitigation |
| [cache-33](#cache-33) | Operations team lacks a structured approach to debug read-heavy system failures under traffic spikes | Systematic troubleshooting order for read-heavy systems |

---

## cache-31: CDN Edge Caching for HTTP Redirect Responses

> **Source**: [§"CDN? For redirects?"](../../articles/caching/url-shortener-viral-hotkey-cdn-caching.md)

| | |
|:---|:---|
| **Problem** | A single shortened URL receives 25 million redirect requests in minutes; every request hits the backend to resolve the short key to the original URL |
| **Root cause** | Redirect responses (HTTP 301/302) are treated as dynamic, non-cacheable content; no edge caching layer absorbs the read load before it reaches the application |

**Strategy**: Configure CDN edge servers to cache HTTP redirect responses for popular URLs with a short TTL. The CDN returns the `Location` header directly from the edge — millions of requests never reach the backend.

```
Without CDN:
  User → [Internet] → Load Balancer → Redirect Service → Redis → DB

With CDN Edge Redirect Caching:
  User → CDN Edge (cached 302) → Original URL
         │ (cache miss only)
         ▼
  Redirect Service → Redis
```

| Tradeoff | Detail |
|:---|:---|
| **Massive backend offload** | 99%+ of redirect requests served from edge; backend sees only cache misses |
| **Staleness window** | Short TTL (1–5 min) means redirects can be stale if the URL mapping changes — acceptable for URL shorteners where mappings are immutable |
| **CDN cost** | Redirects are tiny responses (few hundred bytes); edge cache eviction churn is negligible |
| **TTL tuning** | Too short = backend still hit heavily; too long = stale redirects; 1–5 minutes is the sweet spot for viral events |

Also see [Hot Keys & Skewed Workloads](caching/hot-keys-skewed-workloads.md#cache-16-dedicated-hot-key-tier) — Dedicated hot-key tier
Dictionary: [CDN](../../reference-dictionary/networking.md#cdn), [Hot Key](../../reference-dictionary/caching.md#hot-key)
Azure: Azure Front Door supports caching HTTP redirect responses at the edge; pair with Azure CDN for global edge distribution
Taxonomy: §7.3 Caching Strategies

---

## cache-32: Redis Cluster Hot-Key Limitation

> **Source**: [§"Redis Cluster alone doesn't completely solve Hot Keys"](../../articles/caching/url-shortener-viral-hotkey-cdn-caching.md)

| | |
|:---|:---|
| **Problem** | Engineers assume Redis Cluster solves hot keys — but hash-based sharding distributes _keys_, not _load_; a single viral key still maps to one shard, which becomes the bottleneck |
| **Root cause** | Redis Cluster uses hash slots (CRC16) to assign keys to shards; all requests for the same key route to the same shard regardless of cluster size |

**Strategy**: Layer multiple strategies on top of Redis Cluster to handle single-key hotspots:

1. **Local in-memory cache (L1)**: Each redirect service instance caches the short-key→URL mapping locally with a short TTL, collapsing millions of Redis calls into periodic refreshes.
2. **Cache replication**: Replicate the hot key across multiple Redis nodes so reads spread across all replicas.
3. **Request coalescing**: When a cache miss occurs, only one backend request fetches the URL; all concurrent requests for the same key await that single result.

```
Redis Cluster (hash-slotted):
  Shard 0: keys hashing to slots 0–5460
  Shard 1: keys hashing to slots 5461–10922   ← "abc123" always lands here
  Shard 2: keys hashing to slots 10923–16383

With replication overlay:
  "abc123" → [Replica A] [Replica B] [Replica C]  ← reads spread 3 ways
```

| Tradeoff | Detail |
|:---|:---|
| **Read distribution** | Replication linearly reduces per-node read pressure; 3 replicas = 3× capacity |
| **Write consistency** | Writes still target the primary shard; acceptable since URL shortener mappings are write-once-read-many |
| **Operational complexity** | Must decide which keys to replicate and when to promote/demote; pairs with hot-key detection |
| **Local cache staleness** | L1 cache serves potentially stale data until TTL expires; 1–5 seconds is typical for redirect lookups |

> **Also see**: [Hot Keys & Skewed Workloads](caching/hot-keys-skewed-workloads.md#cache-12-hot-key-read-replication) — Hot-key read replication, [cache-13](#cache-13) — Local L1 in-process cache
> **Dictionary**: [Hot Key](../../reference-dictionary/caching.md#hot-key), [Redis Cluster](../../reference-dictionary/caching.md#redis-cluster), [Request Coalescing](../../reference-dictionary/caching.md#request-coalescing)
> **Azure**: Azure Cache for Redis Enterprise supports active geo-replication and up to 10 read replicas per cluster
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-33: Systematic Troubleshooting Order for Read-Heavy Systems

> **Source**: [§"My troubleshooting order would be"](../../articles/caching/url-shortener-viral-hotkey-cdn-caching.md)

| | |
|:---|:---|
| **Problem** | When a read-heavy system degrades under traffic spikes, engineers often jump to the wrong layer, scale prematurely, or apply fixes that don't address the actual bottleneck |
| **Root cause** | Read-heavy systems have a layered architecture (CDN → cache → database); failures cascade downward — a CDN misconfiguration looks like a Redis overload, which looks like a database crash |

**Strategy**: Follow a progressive diagnostic methodology, starting from the outermost layer and working inward. Each layer checked before the next prevents misdiagnosis and unnecessary scaling.

```
Troubleshooting order (edge → core):

1. CDN Hit Ratio        ← Is the edge absorbing traffic?
2. Redis Hot Keys       ← Is a single key saturating one shard?
3. Cache Hit Rate       ← Is the caching layer working?
4. Database Read QPS    ← Are reads spilling past the cache?
5. Connection Pool      ← Are connection pools exhausted?
6. Scale Stateless      ← Is the application layer saturated?
   Redirect Services
```

**Monitoring signals at each layer:**

| Layer | Key Metric | Threshold Signal |
|:---|:---|:---|
| CDN | Cache hit ratio (%) | Drop below 90% → backend will see 10× traffic |
| Redis | Per-key access frequency | Single key > 10K req/s → hot key alert |
| Cache | Overall hit rate (%) | Drop below 95% → database read spike imminent |
| Database | Read QPS | Exceeding 80% of provisioned capacity |
| Connection Pool | Pending/active connections | Pending > pool size → requests queueing |
| Application | P95/P99 latency | Exceeding 2× baseline → scale out |

| Tradeoff | Detail |
|:---|:---|
| **Prevents misdiagnosis** | Each layer is eliminated before moving deeper; avoids scaling the database when the CDN is misconfigured |
| **Requires pre-instrumentation** | All metrics must be instrumented and dash-boarded before incidents occur |
| **Adds initial diagnostic time** | Methodical approach takes minutes vs. instant gut-feel; the tradeoff is reliability over speed |
| **Does not replace automated response** | Autoscaling and hot-key detection should run concurrently; the methodology guides the human operator for novel failure modes |

> **Also see**: [Hot Keys & Skewed Workloads](caching/hot-keys-skewed-workloads.md#cache-15-hot-key-detection--adaptive-request-routing) — Hot-key detection & adaptive routing
> **Dictionary**: [Cache Hit Ratio](../../reference-dictionary/caching.md#cache-hit-ratio), [Hot Key Detection](../../reference-dictionary/caching.md#hot-key-detection)
> **Azure**: Azure Monitor + Application Insights for unified metric dashboards across CDN, Redis, and database layers
> **Taxonomy**: §7.3 Caching Strategies

---

## Cross-References

- **Articles**: [URL Shortener Suddenly Crashes During IPL Finals: How Will You Fix?](../../articles/caching/url-shortener-viral-hotkey-cdn-caching.md)
- **Dictionary**: [Caching](../../reference-dictionary/caching.md), [Networking (CDN)](../../reference-dictionary/networking.md)
- **Azure**: [Azure Front Door](../../architecture-azure/networking/front-door/), [Azure Cache for Redis](../../architecture-azure/data/)
- **Related System Design**: [Hot Keys & Skewed Workloads](caching/hot-keys-skewed-workloads.md), [Caching Architecture](caching/caching-architecture.md)
- **Taxonomy**: §7.3 Caching Strategies
