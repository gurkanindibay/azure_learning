---
type: Reference
title: "Caching Architecture"
description: "When a **popular cache key expires** and many concurrent requests simultaneously hit the database to recompute it — crushing the database with redundant work."
timestamp: 2026-06-14T00:00:00Z
---

# Caching Architecture

> **Domain**: Cache stampede, invalidation, eviction, TTL, and caching anti-patterns.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Cache Stampede | [`#cache-stampede`](#cache-stampede) |
| Cache-Aside Pattern | [`#cache-aside-pattern`](#cache-aside-pattern) |
| Cache Invalidation | [`#cache-invalidation`](#cache-invalidation) |
| TTL (Time-To-Live) | [`#ttl-time-to-live`](#ttl-time-to-live) |
| Eviction Policies | [`#eviction-policies`](#eviction-policies) |
| Request Coalescing | [`#request-coalescing`](#request-coalescing) |
| PER Algorithm | [`#per-algorithm`](#per-algorithm) |

---

## Cache Stampede

When a **popular cache key expires** and many concurrent requests simultaneously hit the database to recompute it — crushing the database with redundant work.

### Solutions

| Strategy | Mechanism | Complexity |
|:---|:---|:---|
| **Lock-on-Miss** | First request acquires lock, computes, others wait | Medium |
| **PER (Probabilistic Early Recomposition)** | Refresh probabilistically before expiry | Low |
| **External Refresh** | Background job refreshes before TTL expires | Medium |
| **GETEX** (Redis 6.2+) | Atomic get + TTL reset | Low |

**Also see**: [Request Coalescing](#request-coalescing), [PER Algorithm](#per-algorithm) · [Resilience](resilience.md#thundering-herd)

---

## Cache-Aside Pattern

Application code manages the cache explicitly: check cache → on miss, load from DB → store in cache → return.

```
GET /users/123
  → Check Redis for "user:123"
  → Cache miss → SELECT * FROM users WHERE id=123
  → Store in Redis: SET user:123 <data> EX 300
  → Return to client
```

| When to Use | When NOT |
|:---|:---|
| General-purpose caching | Write-heavy data (use write-through) |
| Read-heavy workloads | Data requiring strong consistency |

**Also see**: [Cache Invalidation](#cache-invalidation), [TTL](#ttl-time-to-live)

---

## Cache Invalidation

The process of **removing or updating stale cached data** when the source of truth changes. One of the hardest problems in computer science (Phil Karlton).

| Strategy | Mechanism |
|:---|:---|
| **Explicit delete on write** | DELETE cache key when DB updates |
| **TTL as safety net** | Data expires automatically after N seconds |
| **CDC-based invalidation** | Debezium reads DB WAL → invalidates cache |

> **Rule**: Always have a TTL safety net. Explicit invalidation can fail; TTL ensures eventual correctness.

**Also see**: [Cache-Aside Pattern](#cache-aside-pattern), [TTL](#ttl-time-to-live)

---

## TTL (Time-To-Live)

The duration after which a cache entry **automatically expires**. TTL serves as both a freshness guarantee and an invalidation safety net.

| TTL Strategy | Use Case |
|:---|:---|
| **Short TTL (seconds)** | Real-time data where staleness is unacceptable |
| **Medium TTL (minutes)** | Dashboard data, user profiles |
| **Long TTL (hours/days)** | Reference data, configuration |

> **Key insight**: TTL is always a **safety net** — not the primary freshness mechanism. Explicit invalidation + TTL = defense in depth.

**Also see**: [Cache Invalidation](#cache-invalidation), [Eviction Policies](#eviction-policies)

---

## Eviction Policies

The strategy for **which keys to remove** when the cache is full.

| Policy | Mechanism | Redis Config |
|:---|:---|:---|
| **LRU (Least Recently Used)** | Evicts least recently accessed | `allkeys-lru` |
| **LFU (Least Frequently Used)** | Evicts least frequently accessed | `allkeys-lfu` |
| **TTL** | Evicts keys closest to expiry | `volatile-ttl` |
| **Random** | Evicts random keys | `volatile-random` |
| **Noeviction** | Rejects writes when full | `noeviction` |

> For session stores: `volatile-ttl`. For general caches: `allkeys-lru` or `allkeys-lfu`.

**Also see**: [TTL](#ttl-time-to-live)

---

## Request Coalescing

Deduplicating **in-flight identical requests** so that only one request hits the backend while others wait for the same result. Prevents thundering-herd on cache misses.

```
Request 1: GET /expensive-report → starts computation
Request 2: GET /expensive-report → finds in-flight promise → waits
Request 3: GET /expensive-report → finds in-flight promise → waits
Request 1: computation done → resolves all three
```

**Also see**: [Cache Stampede](#cache-stampede)

---

## PER Algorithm

**Probabilistic Early Recomposition** — refresh a cache key **before** it expires, with a probability that increases as expiry approaches. This smooths the load and avoids the all-at-once stampede.

```
time_until_expiry = TTL - (now - last_updated)
probability = 1 - (time_until_expiry / TTL)
if random() < probability:
    refresh_cache()  # Early recomputation
```

**Also see**: [Cache Stampede](#cache-stampede)
