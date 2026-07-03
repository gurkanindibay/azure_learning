---
type: Index
title: "Caching Architecture"
description: "System-design problems and strategies for caching: stampede prevention, invalidation, eviction, Redis internals, and hot-key mitigation."
timestamp: 2026-06-27T00:00:00Z
---

# Caching Architecture

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for designing and operating caching layers, from cache stampede prevention and invalidation to Redis internals and hot-key workload mitigation.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [caching-architecture.md](caching-architecture.md) | `cache-01` – `cache-05` | Cache stampede, Invalidation, Anti-patterns, Eviction policies, Request coalescing |
| [redis-internals.md](redis-internals.md) | `cache-06` – `cache-11` | I/O multiplexing, Hash slots, COW persistence, Morris counter, UNLINK, TRACKING |
| [hot-keys-skewed-workloads.md](hot-keys-skewed-workloads.md) | `cache-12` – `cache-16` | Hot-key replication, Local cache, Counter sharding, Hot-key detection, Dedicated hot-key tier |
| [redis-rate-limiting-patterns.md](redis-rate-limiting-patterns.md) | `cache-17` – `cache-21` | Token bucket Lua, Sorted-set rolling windows, Concurrent limiting, Fail-open, Load shedding |

## Cross-References

- **Dictionary**: [Caching](../../reference-dictionary/caching.md)
- **Azure**: [Azure Cache for Redis](../../architecture-azure/data/)
- **Related**: [Databases](../databases/), [Resilience](../resilience/)
- **Taxonomy**: §7.3 Caching Strategies
