---
type: System Design
title: "Cache Invalidation & Distributed Session Consistency — Key Takeaways"
description: "Three failure modes of cache invalidation, event-driven invalidation with outbox pattern, cross-region cache synchronization, and monitoring strategies for cache consistency."
generated: { by: process:okf-migrate, at: 2026-07-24T00:00:00Z }
---

# 5. Cache Invalidation & Distributed Session Consistency — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Amazon Cart Shows Old Data — Cache Invalidation and Distributed Session Consistency](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md)

Problems and strategies for cache invalidation in distributed systems, drawn from the Amazon cart stale-data interview scenario. Covers three compounding failure modes, event-driven invalidation architecture, cross-device session consistency, and monitoring the invalidation pipeline.

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| `cache-34` | Cache not invalidated on write | Write-through vs write-around contract |
| `cache-35` | Stale cache replica serves read | Replication lag + session affinity + version stamps |
| `cache-36` | Silent partial failure of invalidation | Event-driven invalidation + outbox pattern + TTL safety net |
| `cache-37` | Cross-device session inconsistency | Cross-region event bus + eventual consistency tradeoff |
| `cache-38` | Invalidation pipeline observability | Six metrics to catch failures before users do |

---

## cache-34: Cache Not Invalidated on Write

> **Source**: [Amazon Cart Cache Invalidation Deep Dive](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md) — Failure Mode 1

| | |
|:---|:---|
| **Problem** | User removes cart item on mobile → opens laptop → item still in cart |
| **Root cause** | Write path updates the database but never touches the cache; cache is populated only on read miss (write-around), so post-write reads hit stale cached data |

**Strategy**: Adopt a **write-through** contract: every write must invalidate or update the cache synchronously before returning success to the client.

```
WRITE: DB UPDATE → cache DEL cart:{userId} → return success
READ:  cache GET → miss → DB SELECT → cache SET cart:{userId} (TTL: 300s)
```

**Write strategy comparison**:

| Strategy | Write Path | Stale Window | Best For |
|:---|:---|:---|:---|
| Write-Around | `App → DB` (cache skipped) | Until TTL or next read | Write-heavy, infrequently-read data |
| Write-Through | `App → Cache → DB` | None | Read-after-write consistency |
| Write-Behind | `App → Cache ⇢ DB` | Until async flush | Write-heavy, loss-tolerant data |

**Tradeoff**: Write-through adds latency to every write (dual-write to cache + DB). For cart systems, read-after-write correctness outweighs the write-latency cost. For write-heavy analytics, write-around + TTL may be more appropriate.

> **Dictionary**: [Write-Around](../../reference-dictionary/caching.md#write-around), [Write-Through](../../reference-dictionary/caching.md#write-through), [Cache-Aside Pattern](../../reference-dictionary/caching.md#cache-aside-pattern), [Cache Invalidation](../../reference-dictionary/caching.md#cache-invalidation)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/)
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-35: Stale Cache Replica

> **Source**: [Amazon Cart Cache Invalidation Deep Dive](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md) — Failure Mode 2

| | |
|:---|:---|
| **Problem** | Write-through applied, cache invalidated — but a read hits a replica that hasn't received the invalidation yet |
| **Root cause** | Replication lag between primary cache node (where invalidation was applied) and replica (that served the read) |

**Strategy — three approaches ranked by consistency strength**:

| Approach | Mechanism | Consistency | Tradeoff |
|:---|:---|:---|:---|
| **Strong consistency** | Read from primary cache node only | Strong | Slower; primary becomes bottleneck |
| **Session affinity** | Route same user to same cache node | Read-your-writes (single device) | Fails across devices/regions |
| **Version stamps** | Cache entries carry version; client sends last-known version | Client-driven staleness detection | Requires client cooperation |

**Version stamps in practice**:
```
Client: GET /cart/{userId}  (lastVersion: 42)
Cache:  version 44 in cache → return (version 44, data)  ✓ fresh
Cache:  version 41 in cache → treat as MISS → DB → return (version 44, data)  ✗ stale bypassed
```

**Tradeoff**: Session affinity is simpler but fragile (breaks across devices). Version stamps are more robust but require clients to carry state. The winning approach: **belt-and-suspenders** — session affinity as the primary routing hint, version stamps as the correctness guarantee, TTL as the ultimate safety net.

> **Dictionary**: [Session Affinity](../../reference-dictionary/caching.md#session-affinity), [Version Stamps](../../reference-dictionary/caching.md#version-stamps), [Replication Lag](../../reference-dictionary/data-architecture.md#replication-lag)
> **Azure**: [Azure Cache for Redis — Clustering](../../architecture-azure/data/)
> **Taxonomy**: §7.3 Caching Strategies

---

## cache-36: Silent Partial Failure of Invalidation

> **Source**: [Amazon Cart Cache Invalidation Deep Dive](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md) — Failure Mode 3

| | |
|:---|:---|
| **Problem** | DB write succeeds, cache invalidation is sent — but silently dropped. Cache serves stale data indefinitely. |
| **Root cause** | Direct cache invalidation calls are fire-and-forget. If the cache is under memory pressure, the invalidation message is evicted. If the network drops the packet, no retry. The application thinks both succeeded. |

**Strategy**: **Event-driven invalidation with outbox pattern + TTL safety net**.

```
WRITE PATH (with outbox):
  BEGIN TRANSACTION
    UPDATE cart_items SET ... WHERE user=U AND item=X
    INSERT INTO outbox (event_type: "cart_changed", payload: {userId: U})
  COMMIT

  Outbox poller → publishes to Kafka/RabbitMQ

CONSUMERS:
  Redis Cache Consumer → DEL cart:{userId}
  CDN Edge Consumer   → PURGE /cart/{userId}
  Search Index Consumer → UPDATE search index

SAFETY NET:
  Every cache entry: TTL = 300s
```

**Why event-driven beats direct invalidation**:

| Property | Direct Invalidation | Event-Driven + Outbox |
|:---|:---|:---|
| Atomicity with DB write | ❌ Two separate operations | ✅ Outbox in same transaction |
| Survives cache downtime | ❌ Invalidation lost | ✅ Event persists in queue |
| Multiple cache layers | ❌ N separate calls | ✅ One event, N consumers |
| Retry on failure | ❌ Manual | ✅ Queue retains until ack |
| Extensibility | ❌ Modify write path | ✅ Add consumer, no write changes |

**Tradeoff**: Event-driven invalidation adds infrastructure complexity (message queue, outbox poller, schema registry). For a single-node cache with low stakes, direct invalidation + TTL is simpler. For production cart systems with multiple cache layers across regions, event-driven is the only reliable approach.

> **Dictionary**: [Event-Driven Invalidation](../../reference-dictionary/caching.md#event-driven-invalidation), [Outbox Pattern](../../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [TTL](../../reference-dictionary/caching.md#ttl-time-to-live)
> **Azure**: [Azure Event Hubs](../../architecture-azure/integration/event-hubs/), [Azure Cache for Redis](../../architecture-azure/data/)
> **Related**: [Messaging Patterns](../messaging/)
> **Taxonomy**: §7.3 Caching Strategies, §3.3 Event-Driven & Messaging

---

## cache-37: Cross-Device Session Consistency

> **Source**: [Amazon Cart Cache Invalidation Deep Dive](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md) — Cross-Device Consistency section

| | |
|:---|:---|
| **Problem** | User removes item on mobile in London (EU-West) → flies to New York → opens laptop → request hits US-East cache → stale data |
| **Root cause** | Cache invalidation in one region does not propagate to other regions. Cross-device consistency is a session routing problem, not just a cache problem. |

**Strategy**: **Cross-region invalidation bus** — Kafka MirrorMaker replicates invalidation events across regions. Each region's cache consumers process both local and remote invalidation events.

```
EU-West:  WRITE → Outbox → Kafka (EU-West)  ──MirrorMaker──→  Kafka (US-East)
              ↓                                                    ↓
         Redis EU-West (invalidated)                        Redis US-East (invalidated)

User in US-East: READ → US-East cache → MISS → DB (fresh data) ✓
```

**CAP tradeoff**: Cross-region cache invalidation is inherently **eventually consistent**. The propagation window (100ms–2s) means stale reads are possible. The design question: is the inconsistency window acceptable?

| Data Type | Consistency Required | Strategy |
|:---|:---|:---|
| Cart contents | Eventual (seconds) | Cross-region invalidation + 5-min TTL |
| Inventory count | Strong (real-time) | Read from DB directly, optimistic locking |
| Payment state | Strong (real-time) | No cache; strongly consistent store |

**Tradeoff**: For cart data, eventual consistency is acceptable because (1) the database is source of truth, (2) TTL caps staleness at 5 minutes, and (3) cross-region device switches are rare within seconds. For inventory or payments, skip the cache entirely.

> **Dictionary**: [Cross-Region Invalidation](../../reference-dictionary/caching.md#cross-region-invalidation), [Event-Driven Invalidation](../../reference-dictionary/caching.md#event-driven-invalidation), [CAP Theorem](../../reference-dictionary/architecture-patterns.md#cap-theorem)
> **Azure**: [Azure Front Door](../../architecture-azure/networking/front-door/), [Azure Event Hubs — Geo-DR](../../architecture-azure/integration/event-hubs/)
> **Taxonomy**: §7.3 Caching Strategies, §5.2 Global Distribution

---

## cache-38: Cache Invalidation Observability

> **Source**: [Amazon Cart Cache Invalidation Deep Dive](../../articles/caching/amazon-cart-cache-invalidation-deep-dive.md) — Monitoring section

| | |
|:---|:---|
| **Problem** | Cache invalidation failures are silent — users notice before engineers do |
| **Root cause** | Monitoring dashboards track generic cache metrics (hit ratio, latency) but not invalidation-specific signals |

**Strategy**: Track six invalidation-specific metrics that surface problems before users report them:

| # | Metric | What it catches | Alert threshold |
|:---|:---|:---|:---|
| 1 | **Cache hit ratio delta after writes** | Invalidation not working | Hit ratio stays high after writes |
| 2 | **Invalidation event processing lag** | Consumer falling behind | > 30s lag for 5 min |
| 3 | **Stale read rate** | Cache serving old data | > 1% for 5 min |
| 4 | **Outbox replay lag** | Events piling up, invalidation delayed | > 60s lag |
| 5 | **TTL expiry percentage** | Event-driven path failing | > 10% expirations (not explicit invalidations) |
| 6 | **Cross-region replication delay** | Global invalidation lag | > 2s P99 |

**Metric interrelationships**:

```
Outbox replay lag ↑ → Invalidation processing lag ↑ → Stale read rate ↑ → TTL expiry % ↑
                                                                                  ↓
                                                                        Cache hit ratio
                                                                        stays abnormal after writes
```

**Tradeoff**: These metrics require timestamp/version instrumentation on both cache entries and database rows — adding ~8 bytes per row. For high-throughput systems, sample at 1% to balance accuracy against overhead. The observability cost is minimal compared to the cost of serving stale data to users.

> **Dictionary**: [Stale Read Rate](../../reference-dictionary/caching.md#stale-read-rate), [Cache Hit Ratio](../../reference-dictionary/caching.md#cache-hit-ratio), [TTL](../../reference-dictionary/caching.md#ttl-time-to-live), [Event-Driven Invalidation](../../reference-dictionary/caching.md#event-driven-invalidation)
> **Azure**: [Azure Monitor](../../architecture-azure/observability/), [Application Insights](../../architecture-azure/observability/)
> **Related**: [Resilience Patterns](../resilience/)
> **Taxonomy**: §7.3 Caching Strategies, §7.1 Observability & Monitoring
