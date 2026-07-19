---
type: Article
title: "How Uber Conquered Database Overload: From Static Rate-Limiting to Intelligent Load Management"
description: "Uber's journey from quota-based rate limiting to a unified, priority-aware load shedding engine (Cinnamon) for their distributed databases Docstore and Schemaless, achieving ~70% reduction in P99 latency and 80% throughput increase under overload."
source: "https://www.uber.com/gb/en/blog/from-static-rate-limiting-to-intelligent-load-management/"
author: "Dhyanam Vaidya, Prathamesh Deshpande, Mike Ma, Chaitanya Yalamanchili"
created: 2026-07-19
---

# How Uber Conquered Database Overload: From Static Rate-Limiting to Intelligent Load Management

> **Source**: [Uber Engineering Blog](https://www.uber.com/gb/en/blog/from-static-rate-limiting-to-intelligent-load-management/)
> **Authors**: Dhyanam Vaidya, Prathamesh Deshpande, Mike Ma, Chaitanya Yalamanchili

## Introduction

Uber's thousands of microservices handle traffic for over 170 million monthly active users across rides, Uber Eats, drivers, and couriers. At the heart of this infrastructure are [Docstore](https://www.uber.com/gb/en/blog/schemaless-sql-database/) and [Schemaless](https://www.uber.com/gb/en/blog/schemaless-part-one-mysql-datastore/), Uber's in-house distributed databases built on top of MySQL. These databases span thousands of clusters, store tens of petabytes of operational data, and serve tens of millions of requests per second with billions of rows read or updated.

At this scale, even minor overloads cascade: a brief spike ripples outward, downstream services time out, retries pile up, and degradation amplifies into broader failure. In a multitenant environment, fairness is also critical — no single tenant should hog all resources. The article chronicles how Uber built an intelligent load manager that detects overload from multiple signals to keep databases stable and fair under pressure.

## Docstore and Schemaless Architecture

Docstore supports transactions with full CRUD operations; Schemaless is optimized for append-only workloads. Both share a common architectural foundation:

- **Stateless query engine**: Query planning, request routing, sharding, schema management, authorization, request parsing, and validation.
- **Stateful storage engine**: Transaction management, connection pooling, consensus (Raft), and replication. Data is sharded across partitions, each with one leader and two followers.
- **Control plane**: Orchestration and cluster management.

Each partition is backed by MySQL nodes with locally attached NVMe SSDs, built for high-throughput, low-latency workloads.

## Challenges

### Quota-Based Rate Limiting (Failed Approach)

The initial approach used quota-based rate limiting in the stateless query engine layer:

- Assign each read/write request a capacity unit cost based on bytes processed
- Grant users fixed quotas; return HTTP 429 when exceeded
- Store quota usage in a central Redis cache

**Why it failed**:

1. **Added complexity**: Every request required a Redis call — a new point of failure and an extra network hop.
2. **Tracking overhead**: The stateless routing layer needed real-time health/load info for thousands of partitions.
3. **Imprecise cost model**: Due to MySQL scanning/filtering, a full table scan returning one row was assigned the same cost as a single-row lookup.
4. **Static quotas**: Required frequent manual adjustments from stakeholders; ineffective in multitenant environments.

**Crucial insight**: Overload management must live as close to the storage nodes as possible.

### Identifying the Right Signal

Simple QPS-based rate limiting is too coarse. **Concurrency** — the number of operations in flight — is more effective. Per Little's Law: `Concurrency = Throughput × Latency`. In stateful systems, concurrency maps closely to resource usage.

### Balancing Resilience and Fairness

Two parallel requirements:
- During system-wide stress: shed by priority (low-priority first)
- During single-tenant noise: per-tenant rate limiting independent of global load

## Foundation: CoDel + Scorecard + Regulators

### CoDel (Controlled Delay)

Borrowed from networking (bufferbloat prevention), CoDel sheds based on **queue wait time** rather than queue length. Implemented with three independent queues:

| Queue | Purpose |
|:---|:---|
| Read | Point lookups and light queries |
| Write | Insert, update, upsert operations |
| Slow | Long-running operations (scans, deletes, replication) |

**Adaptive LIFO**: Under normal load, FIFO. Under pressure, switches to LIFO — favoring newer requests that still have a chance to succeed, shedding stale work, and failing fast.

### Scorecard Engine

A rule-based admission control component enforcing **per-tenant concurrency limits** in multitenant environments. Primary benefit: incident containment — isolates misbehaving tenants without disrupting others, and reduces blast radius during overload.

### Regulators

Plug-in, node-local overload detectors for behaviors that don't surface in concurrency saturation:

| Regulator | Purpose |
|:---|:---|
| Write bytes | Limits concurrent write volume to prevent I/O saturation |
| Partition key | Throttles traffic targeting hot partition keys |
| Memory | Tracks free process memory; throttles when low |
| Goroutines | Tracks total goroutine count; throttles when exceeding threshold |

### What Worked

- CoDel queues prevented runaway resource exhaustion; improved stability
- Scorecard engine isolated misbehaving tenants

### Limitations

- CoDel treated all requests equally (no priority awareness)
- Fixed queue timeouts and static inflight limits required frequent manual tuning
- Thundering herd: all rejected requests retried at once, triggering repeated overload cycles
- Lack of traffic differentiation meant high-priority requests were dropped

## Evolution: Cinnamon Replaces CoDel

[Cinnamon](https://www.uber.com/gb/en/blog/cinnamon-using-century-old-tech-to-build-a-mean-load-shedder/) is a priority-aware load shedder that makes smarter shedding decisions by considering:

- **Request rank**: Derived from explicit priority or calling service identity
- **Dynamic system state**: Real-time latency and error rate signals
- **Relative importance**: Tiering model from t0 (critical infrastructure) to t5 (least critical)

With priority awareness, the queue structure simplified to just read and write queues — long-running operations were marked with lower priority instead of having a separate queue.

### Performance Gains

- Requests ranked; low-priority shed first; user-facing flows protected
- Queue timeout thresholds adapt using P90 latency metrics (no manual tuning)
- **Auto Tuner** dynamically adjusts inflight limits to maximize throughput
- **PID-based control** absorbs pressure without overreacting — prevents premature shedding, reduces unnecessary 429s, and eliminates thundering herd effects

## The Unified Load Shedding Engine

### Centralizing Overload Decisions

Enhanced Cinnamon to support **pluggable external signals** (e.g., follower commit lag), enabling globally informed, priority-aware shedding within a single admission control path.

**BYOS (Bring Your Own Signal)** ethos: pluggable framework for embedding new overload signals and routing them to the right control path — shedding broadly by priority or precisely by caller.

Previously, external components using token-bucket-based rate limiters handled remote shedding decisions — easy to build but ineffective at scale, causing split-brain behaviors and globally suboptimal decisions.

### Results

| Metric | Before (Token Bucket) | After (Cinnamon) | Improvement |
|:---|:---|:---|:---|
| Throughput under overload | 3,000 QPS | 5,400 QPS | **+80%** |
| P99 latency (upsert) | 3.1 s | 1.0 s | **~70% reduction** |
| Peak goroutines | 150,000 | 10,000 | **~93% reduction** |
| Max heap usage | 5-6 GB spikes | ~1 GB | **~60% reduction** |

PID regulation makes shedding smooth and stable (like a dimmer switch) rather than reactive and abrupt (like a hammer).

## Lessons Learned

1. **Prioritization is paramount**: Protect critical, user-facing traffic first.
2. **Fail fast, don't block**: Rejecting early reduces wasted work, keeps latencies predictable, prevents OOMs.
3. **PID regulation for stable shedding**: Reactive shedding based solely on error rates overcorrects. PID brings balance by incorporating system history and directional trends.
4. **Place control close to the source of truth**: The best shedding decisions happen where the state lives — the storage layer in stateful systems.
5. **Embrace dynamism**: Avoid static configurations; the system should adapt to context.
6. **Invest in visibility and monitoring**: Track what's being shed, why, and how each component contributes to system pressure.
7. **Simplicity over complexity**: A meta-principle guiding all other decisions.

## Related Topics

- **Load Shedding**: [Reference Dictionary](../reference-dictionary/resilience.md#load-shedding)
- **Circuit Breaker**: [Reference Dictionary](../reference-dictionary/resilience.md#circuit-breaker)
- **Backpressure**: [Reference Dictionary](../reference-dictionary/resilience.md#backpressure)
- **Bulkhead**: [Reference Dictionary](../reference-dictionary/resilience.md#bulkhead)
- **Thundering Herd**: [Reference Dictionary](../reference-dictionary/resilience.md#thundering-herd)
