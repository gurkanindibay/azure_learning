---
type: System Design
title: "Hot Keys & Skewed Workloads — Key Takeaways"
description: "Replication, local caching, counter sharding, hot-key detection, and dedicated hot tiers for celebrity/hot-key problems"
generated: { by: process:okf-migrate, at: 2026-06-27T12:00:00Z }
---

# 61. Hot Keys & Skewed Workloads — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [How Do You Design a System Where 1% of Data Causes 90% of the Load?](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)
> **Purpose**: Extract reusable strategies for taming hot keys, celebrity problems, and skewed cache/database workloads.

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Cache stampede, invalidation, anti-patterns, eviction, request coalescing
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — Hot key, cache stampede, request coalescing, counter sharding
> **Taxonomy Reference**: §7.2 Performance Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-12](#cache-12) | A single read-heavy key melts one shard while others sit idle | Hot-key read replication |
| [cache-13](#cache-13) | Distributed cache is overwhelmed by repeated reads of the same key | Local (L1) in-process cache |
| [cache-14](#cache-14) | A single write-heavy counter becomes a bottleneck | Counter sharding |
| [cache-15](#cache-15) | Viral keys appear unpredictably and must be handled automatically | Hot-key detection + adaptive routing |
| [cache-16](#cache-16) | Hot-key traffic starves normal queries on shared infrastructure | Dedicated hot-key tier |

---

## cache-12: Hot-Key Read Replication

> **Source**: [§"Principle 1: Replicate Hot Data"](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)

| | |
|:---|:---|
| **Problem** | A single read-heavy key (e.g., `user:taylorswift`) concentrates 500K req/s on one cache shard; the node melts while 99 others are idle |
| **Root cause** | Hash-based sharding distributes *keys* evenly, not *load*; access patterns follow a power law |

**Strategy**: Maintain **N read replicas** of a hot key and spread reads across them. Writes update a primary and fan out to all replicas; reads pick a replica at random.

```python
def get_hot_key(key):
    replica_id = random.randint(0, NUM_REPLICAS - 1)
    replica_key = f"{key}:replica:{replica_id}"
    result = cache.get(replica_key)
    return result if result else cache.get(key)
```

| Tradeoff | Detail |
|:---|:---|
| **Read pressure drops linearly** | 500K req/s ÷ 10 replicas = 50K req/s per node |
| **Write amplification** | Every write must update N replicas — acceptable when reads dominate |
| **Replica consistency** | Replicas may lag milliseconds behind the primary |
| **Worse for write-heavy keys** | Counters, inventory, and rate limiters need a different strategy (see [cache-14](#cache-14)) |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-05-request-coalescing-in-flight-deduplication) — Request coalescing
> **Dictionary**: [Hot Key](../../reference-dictionary/caching.md#hot-key)
> **Azure**: Azure Cache for Redis supports clustered read replicas; Premium/Enterprise tiers scale replica count independently
> **Taxonomy**: §7.2 Performance Architecture

---

## cache-13: Local (L1) In-Process Cache

> **Source**: [§"Principle 2: Add a Local Cache Layer"](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)

| | |
|:---|:---|
| **Problem** | Even a replicated distributed cache is hit hundreds of thousands of times per second for the same hot key |
| **Root cause** | Every application instance repeatedly fetches the same value from the shared cache |

**Strategy**: Add a short-TTL **local in-process cache** (L1) in front of the distributed cache (L2) and database (L3). Hot keys stay warm in every app instance, collapsing shared-cache pressure by orders of magnitude.

```python
def get_with_local_cache(key, ttl_seconds=5):
    entry = local_cache.get(key)
    if entry and entry[1] > time.time():
        return entry[0]
    value = redis.get(key) or db.query(key)
    local_cache[key] = (value, time.time() + ttl_seconds)
    return value
```

| Tradeoff | Detail |
|:---|:---|
| **Massive downstream reduction** | 50 instances × 1 miss per 5 s ≈ 10 req/s to Redis vs. 500K req/s without local cache |
| **Staleness** | Each instance may serve slightly stale data until its TTL expires |
| **Memory per instance** | Every app node holds its own copy — bounded by TTL and key cardinality |
| **Best for immutable hot data** | Celebrity profiles, product pages, config flags |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-02-cache-invalidation) — Cache invalidation
> **Dictionary**: [Hot Key](../../reference-dictionary/caching.md#hot-key)
> **Azure**: Azure Cache for Redis Enterprise supports RESP3 `CLIENT TRACKING` for server-assisted client-side caching
> **Taxonomy**: §7.2 Performance Architecture

---

## cache-14: Counter Sharding

> **Source**: [§"Principle 3: Shard the Hot Key Itself"](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)

| | |
|:---|:---|
| **Problem** | A single write-heavy key such as a global like counter receives 100K writes/sec on one node |
| **Root cause** | Replication amplifies writes; the key itself must serialize every update |

**Strategy**: **Shard the counter** into N sub-keys. Writes pick a random shard; reads sum all shards via a pipeline.

```python
NUM_COUNTER_SHARDS = 100

def increment_like(post_id):
    shard = random.randint(0, NUM_COUNTER_SHARDS - 1)
    redis.incr(f"post:{post_id}:likes:shard:{shard}")

def get_like_count(post_id):
    pipe = redis.pipeline()
    for shard in range(NUM_COUNTER_SHARDS):
        pipe.get(f"post:{post_id}:likes:shard:{shard}")
    return sum(int(r or 0) for r in pipe.execute())
```

| Tradeoff | Detail |
|:---|:---|
| **Write load spreads** | 100K writes/sec ÷ 100 shards = 1K writes/sec per shard |
| **Read cost increases** | A read now issues N GETs and sums them — adds latency |
| **Not atomic** | Concurrent increments across shards still sum correctly, but the read is a point-in-time aggregate |
| **Use only for write-heavy hot keys** | Read-heavy keys are cheaper to replicate (see [cache-12](#cache-12)) |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-05-request-coalescing-in-flight-deduplication) — Request coalescing
> **Dictionary**: [Counter Sharding](../../reference-dictionary/caching.md#counter-sharding)
> **Azure**: Azure Cache for Redis Cluster distributes shards across nodes; choose shard count ≥ node count for even spread
> **Taxonomy**: §7.2 Performance Architecture

---

## cache-15: Hot-Key Detection & Adaptive Request Routing

> **Source**: [§"Principle 4: Detect and Adapt to Hot Spots"](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)

| | |
|:---|:---|
| **Problem** | You cannot predict which key will go viral; manual intervention is too slow |
| **Root cause** | Power-law traffic means rare, unexpected keys suddenly dominate load |

**Strategy**: **Detect** hot keys in real time with per-key access counters over a sliding window, then **adapt** by automatically promoting them to replicated/cache-isolated state and routing requests accordingly.

```python
class HotKeyDetector:
    def __init__(self, window_seconds=60, threshold=100):
        self.counts = defaultdict(int)
        self.window = window_seconds
        self.threshold = threshold
        self.last_reset = time.time()

    def record_access(self, key):
        if time.time() - self.last_reset > self.window:
            self.counts.clear()
            self.last_reset = time.time()
        self.counts[key] += 1
        if self.counts[key] == self.threshold:
            self.promote_to_hot(key)

    def promote_to_hot(self, key):
        value = cache.get(key)
        for i in range(NUM_REPLICAS):
            cache.set(f"{key}:replica:{i}", value, ttl=300)
        hot_key_registry.add(key)
```

| Tradeoff | Detail |
|:---|:---|
| **Self-healing** | System responds to viral spikes without human intervention |
| **Detection overhead** | Counting every access adds CPU/memory; use approximate/frequency-sketch structures at scale |
| **False positives** | A short burst can trigger unnecessary replication; add hysteresis or cooldown |
| **Routing layer complexity** | The proxy or client must learn the hot-key registry and prefer replicas |

> **Also see**: [Caching Architecture](caching/caching-architecture.md#cache-01-cache-stampede) — Cache stampede prevention
> **Dictionary**: [Hot Key Detection](../../reference-dictionary/caching.md#hot-key-detection), [Adaptive Request Routing](../../reference-dictionary/caching.md#adaptive-request-routing)
> **Azure**: Azure Front Door + Azure Cache for Redis can route celebrity content to a dedicated edge/cache profile
> **Taxonomy**: §7.2 Performance Architecture

---

## cache-16: Dedicated Hot-Key Tier

> **Source**: [§"Principle 5: Isolate Hot Paths"](../../articles/caching/How Do You Design a System Where 1% of Data Causes 90% of the Load.md)

| | |
|:---|:---|
| **Problem** | A viral hot key exhausts connection pools, CPU, and bandwidth shared with normal traffic, causing cascading latency |
| **Root cause** | Hot and cold keys share the same shards, network links, and process resources |

**Strategy**: Physically or logically **isolate hot paths** in a dedicated tier with its own replicas, memory, and bandwidth. The hot tier scales independently so a spike cannot starve cold queries.

```
┌─────────────────┐      ┌─────────────────┐
│   Hot-Key Tier  │      │  Normal Cache   │
│  (celebrity     │      │   (long-tail    │
│   profiles,     │◄────►│    traffic)     │
│   viral posts)  │      │                 │
└─────────────────┘      └─────────────────┘
```

| Tradeoff | Detail |
|:---|:---|
| **Blast-radius containment** | A hot-key spike no longer degrades normal traffic |
| **Independent scaling** | Add replicas/memory to the hot tier only |
| **Operational complexity** | Two tiers to monitor, deploy, and tune |
| **Routing requirement** | Requests must be classified and sent to the correct tier |

> **Also see**: [News Feed Takeaways](case-studies/news-feed.md#feed-01-hybrid-fanout-to-control-write-amplification) — Celebrity cache / hybrid fanout
> **Dictionary**: [Dedicated Hot-Key Tier](../../reference-dictionary/caching.md#dedicated-hot-key-tier)
> **Azure**: Azure Cache for Redis Enterprise supports multiple clusters; place hot data on a higher-tier cluster with more replicas
> **Taxonomy**: §7.2 Performance Architecture
