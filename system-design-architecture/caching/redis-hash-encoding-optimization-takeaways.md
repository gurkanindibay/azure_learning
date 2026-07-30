---
type: System Design
title: "Redis Hash Encoding & Cost Optimization — Key Takeaways"
description: "How grouping fields into Redis hashes, tuning encoding thresholds (ziplist/listpack), Lua batching, and Protobuf compression achieved ~90% cost reduction at Meesho."
timestamp: 2026-07-30T00:00:00Z
---

# 40. Redis Hash Encoding & Cost Optimization — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [A 90% Redis Cost Reduction Sounds Impossible Until You Look Under the Hood](../../articles/caching/meesho-redis-90-percent-cost-reduction.md)
> **Purpose**: Extract reusable architectural patterns from Meesho's Redis cost optimization journey.

> **Also see**: [Redis Internals](../caching/redis-internals.md) — I/O multiplexing, hash slots, COW persistence, Morris counter, UNLINK
> **Dictionary**: [Caching](../../reference-dictionary/caching.md) — TTL, Lua Scripting, ziplist, listpack, hash-max-ziplist-entries
> **Taxonomy Reference**: §7.3 Caching Strategies

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [cache-39](#cache-39) | Per-field keys cause O(n) metadata overhead at scale | Group related fields into Redis Hashes to collapse N keys into 1 |
| [cache-40](#cache-40) | Hash encoding silently crosses into expensive hashtable without warning | Tune `hash-max-ziplist-entries` / `hash-max-listpack-entries` to match workload field counts |
| [cache-41](#cache-41) | Multi-step Redis operations incur N round trips | Batch operations in server-side Lua scripts for single-round-trip atomicity |
| [cache-42](#cache-42) | Large uncompressed payloads + missing TTLs leak memory indefinitely | Serialize with Protobuf before storage; enforce TTL on every key |

---

## cache-39: Per-Field Keys → Hash Grouping

> **Source**: [§"Fix One: Group Fields Into Hashes"](../../articles/caching/meesho-redis-90-percent-cost-reduction.md)

| | |
|:---|:---|
| **Problem** | Storing every field as its own Redis key causes per-key metadata overhead (pointers, encoding headers) to multiply linearly with field count — invisible at small scale, devastating at tens of millions of records |
| **Root cause** | Developers default to `SET` for each field because it's the simplest mental model; no one revisits the key structure after early prototyping |

**Strategy**: Group related fields into a single Redis Hash (`HSET`). One key carries one set of metadata overhead regardless of how many fields it holds.

```
Before (per-field keys):             After (Hash grouping):
SET user:1001:name "Asha"      →     HSET user:1001 name "Asha" age 29 city "Bengaluru"
SET user:1001:age 29
SET user:1001:city "Bengaluru"
                                    Result: 3 keys → 1 key
3 × per-key metadata overhead       1 × per-key metadata overhead
```

| Tradeoff | Detail |
|:---|:---|
| **Cannot atomically expire individual fields** | TTL applies to the entire hash key, not individual fields — use separate hashes if fields have independent lifecycles |
| **HGETALL on large hashes** | Retrieving all fields is O(N) where N is field count; acceptable for small-to-medium records, problematic for very wide hashes |
| **No partial field access via TTL** | If some fields need short TTLs and others don't, split them into separate hashes grouped by TTL policy |

> **Dictionary**: [Hash (Redis)](../../reference-dictionary/caching.md#hash-redis) · [TTL (Time-To-Live)](../../reference-dictionary/caching.md#ttl-time-to-live)
> **Also see**: [Hot Keys & Skewed Workloads](../caching/hot-keys-skewed-workloads.md) — Hot-key detection, counter sharding

---

## cache-40: Encoding Threshold Tuning — Keeping Hashes in Compact Mode

> **Source**: [§"Fix Two: Tune the Encoding Threshold"](../../articles/caching/meesho-redis-90-percent-cost-reduction.md)

| | |
|:---|:---|
| **Problem** | Redis silently promotes a Hash from compact encoding (ziplist/listpack) to full hashtable when field count or field size exceeds a threshold — causing memory usage to multiply with no visible warning |
| **Root cause** | Teams leave `hash-max-ziplist-entries` and `hash-max-ziplist-value` at defaults without checking whether those defaults match their actual data shapes |

**Strategy**: Inspect current encoding with `OBJECT ENCODING`, then tune the threshold configuration (`hash-max-ziplist-entries`, `hash-max-ziplist-value`, or their Redis 7+ `listpack` equivalents) so that hashes stay in the compact encoding for your actual field counts and sizes.

```
Compact (listpack/ziplist):         Pointer-based (hashtable):
+----+----+----+----+----+          +--------+  +--------+
|HDR|F1 |F2 |F3 |V1 |V2 |          |bucket[]|→|entry[]|
+----+----+----+----+----+          +--------+  +--------+
Contiguous, cache-friendly           Scattered, pointer-heavy
```

| Tradeoff | Detail |
|:---|:---|
| **Writes on compact-encoded hashes are slower at high field counts** | Compact encoding requires linear scan for field lookup; crossing ~128 fields, hashtable O(1) lookup wins |
| **Threshold is workload-specific** | Default of 128 entries / 64 bytes per value may be too high or too low — measure with your data |
| **Redis 7 changed defaults** | `listpack` replaced `ziplist` as the compact encoding; `hash-max-listpack-entries` and `hash-max-listpack-value` are the new config keys |

> **Dictionary**: [ziplist](../../reference-dictionary/caching.md#ziplist) · [listpack](../../reference-dictionary/caching.md#listpack) · [hash-max-ziplist-entries](../../reference-dictionary/caching.md#hash-max-ziplist-entries)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/) — Enterprise tier supports Redis 7.2+ with listpack encoding

---

## cache-41: Lua Scripting for Multi-Step Atomic Operations

> **Source**: [§"Fix Three: Batch Round Trips With Lua"](../../articles/caching/meesho-redis-90-percent-cost-reduction.md)

| | |
|:---|:---|
| **Problem** | Multi-step Redis operations (read → conditional increment → TTL refresh) require N network round trips, each adding latency and holding connections open under load |
| **Root cause** | Redis commands are atomic individually, but composing them requires the client to orchestrate with sequential calls |

**Strategy**: Move multi-step operations into server-side Lua scripts that execute atomically in a single round trip. Redis guarantees that no other commands interleave during script execution.

```
Before (3 round trips):                    After (1 round trip):
Client → Redis: HGET user:1001 count       Client → Redis: EVAL "<lua-script>" 1 user:1001 300
Client ← Redis: null                                     ↓
Client → Redis: HSET user:1001 count 1         Server-side: HGET → HSET/HINCRBY → EXPIRE → return
Client ← Redis: OK                                All atomic, no interleaving
Client → Redis: EXPIRE user:1001 300
Client ← Redis: 1
```

| Tradeoff | Detail |
|:---|:---|
| **Scripts block the event loop** | Lua scripts run atomically; a long-running script blocks all other clients — keep scripts short and avoid O(N) operations on large data sets |
| **Scripts need version control** | Lua code in Redis is harder to test, deploy, and roll back than application code — treat scripts as infrastructure code |
| **Debugging is harder** | Stack traces from Lua scripts are opaque compared to application-level error handling — add explicit error returns in scripts |
| **Cluster mode: all keys must hash to the same slot** | Use hash tags (`{user:1001}`) to co-locate keys accessed by the same script |

> **Dictionary**: [Lua Scripting (Redis)](../../reference-dictionary/caching.md#lua-scripting-redis)
> **Also see**: [Redis Internals](../caching/redis-internals.md) — I/O multiplexing, single-threaded event loop

---

## cache-42: Payload Compression + TTL Enforcement

> **Source**: [§"Fix Four: Compress Before You Store, and Set Real TTLs"](../../articles/caching/meesho-redis-90-percent-cost-reduction.md)

| | |
|:---|:---|
| **Problem** | Large JSON payloads consume disproportionate memory, and absent TTLs let stale data accumulate indefinitely — a slow, invisible memory leak disguised as "normal growth" |
| **Root cause** | JSON is human-readable but space-inefficient; TTLs are treated as optional rather than mandatory safety nets |

**Strategy**: Serialize payloads with a compact binary format (Protobuf, MessagePack) before writing to Redis, and always set a deliberate TTL. Compression trades memory for CPU — move cost to wherever it's cheaper for your workload.

```
JSON (text):                           Protobuf (binary):
{"name":"Asha","age":29,"city":"...    \x0a\x04Asha\x10\x1d\x1a\x09Bengaluru
~60 bytes                              ~25 bytes (~60% smaller)
```

| Tradeoff | Detail |
|:---|:---|
| **CPU cost of serialization/deserialization** | Protobuf encoding/decoding adds CPU overhead on every read and write — profile to confirm the CPU cost is less than the memory savings |
| **Loss of human-readability for debugging** | Binary payloads can't be inspected with `GET` or Redis CLI without deserialization — add a debug endpoint or keep a small JSON mirror for troubleshooting |
| **Schema evolution** | Protobuf requires schema management; adding/removing fields needs backward-compatible changes |
| **TTL as safety net, not primary invalidation** | TTL ensures eventual cleanup but doesn't guarantee freshness — pair with explicit invalidation for data that changes before expiry |

> **Dictionary**: [TTL (Time-To-Live)](../../reference-dictionary/caching.md#ttl-time-to-live) · [Cache Invalidation](../../reference-dictionary/caching.md#cache-invalidation)
> **Also see**: [Caching Architecture](../caching/caching-architecture.md) — Cache stampede, eviction policies, request coalescing
