---
type: System Design
title: "Uber Intelligent Load Management — Key Takeaways"
description: "How Uber evolved from static quota-based rate limiting to a unified, priority-aware load shedding engine with PID control, achieving 80% throughput increase and ~70% P99 latency reduction."
timestamp: 2026-07-19T00:00:00Z
---

# Uber Intelligent Load Management — Key Takeaways

> **Parent**: [Resilience Patterns](index.md)
> **Source**: [How Uber Conquered Database Overload](../../articles/resilience/uber-intelligent-load-management.md)
> **Taxonomy Reference**: §7.1 Reliability & Resilience

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`resilience-17`](#resilience-17-static-rate-limiting-fails-at-scale) | Static Rate Limiting Fails at Scale | Storage-layer concurrency shedding beats stateless QPS quotas |
| [`resilience-18`](#resilience-18-codel-and-adaptive-lifo-queuing) | CoDel and Adaptive LIFO Queuing | Shed on queue wait time, switch FIFO→LIFO under pressure |
| [`resilience-19`](#resilience-19-priority-aware-shedding-with-pid-control) | Priority-Aware Shedding with PID Control | Tiered request ranking + PID regulation for smooth, stable shedding |
| [`resilience-20`](#resilience-20-unified-byos-load-shedding-engine) | Unified BYOS Load Shedding Engine | Consolidate local + remote overload signals into one control loop |
| [`resilience-21`](#resilience-21-multitenant-fairness-with-scorecard-engine) | Multitenant Fairness with Scorecard Engine | Per-tenant concurrency limits independent of global load |

---

## resilience-17: Static Rate Limiting Fails at Scale

| | |
|:---|:---|
| **Problem** | A stateless rate limiter (quota + Redis) cannot accurately protect stateful database partitions from overload because it lacks real-time partition health visibility and has an imprecise cost model. |
| **Root cause** | Overload protection placed in the stateless query engine layer — too far from the storage nodes where the actual state and resource exhaustion live. The cost model (bytes processed) treated full table scans identically to single-row lookups. |

**Strategy**: Move overload management to the storage layer and use **concurrency** (in-flight operations) as the overload signal instead of QPS or byte-based quotas. Per Little's Law ($Concurrency = Throughput \times Latency$), concurrency directly reflects resource usage in stateful systems.

**Tradeoff**: Storage-layer shedding requires per-node detection logic and can't leverage centralized quota state, but the accuracy gain and elimination of the Redis dependency far outweigh the added implementation complexity.

**Related**: [Load Shedding](../../reference-dictionary/resilience.md#load-shedding), [Backpressure](../../reference-dictionary/resilience.md#backpressure), [Bulkhead](../../reference-dictionary/resilience.md#bulkhead)

---

## resilience-18: CoDel and Adaptive LIFO Queuing

| | |
|:---|:---|
| **Problem** | FIFO queuing under overload causes old, stale requests to accumulate at the head of the queue while fresh, still-relevant requests sit idle — resulting in wasted work when stale requests are eventually abandoned or retried by clients. |
| **Root cause** | FIFO processes requests strictly in arrival order regardless of whether the request is still viable. Under overload, queue wait time grows and requests become stale before they're processed. |

**Strategy**: Use **CoDel (Controlled Delay)** to shed based on queue wait time (not queue length) and implement **Adaptive LIFO**: under normal load, behave as FIFO; under pressure, switch to LIFO to favor newer requests that still have a chance to succeed. Separate queues per operation type (read, write, slow) provide workload isolation.

**Tradeoff**: LIFO under pressure means some older requests are intentionally starved, but the alternative — processing stale requests that clients have already abandoned — wastes capacity and amplifies overload through retries. Failing fast is better than doing useless work.

**Related**: [CoDel Algorithm](https://queue.acm.org/detail.cfm?id=2209336), [Load Shedding](../../reference-dictionary/resilience.md#load-shedding), [Thundering Herd](../../reference-dictionary/resilience.md#thundering-herd)

---

## resilience-19: Priority-Aware Shedding with PID Control

| | |
|:---|:---|
| **Problem** | A priority-agnostic load shedder (CoDel) drops user-facing and low-priority traffic indiscriminately during overload, causing customer-visible errors and increased on-call load when low-priority async jobs trigger shedding. |
| **Root cause** | CoDel treats all requests equally; there is no mechanism to express that a ride-hailing request (tier 1) matters more than a background GC job (tier 5). |

**Strategy**: Replace CoDel with **Cinnamon**, a priority-aware load shedder that (a) ranks requests by explicit priority or calling service identity in a tiering model (t0–t5), (b) uses a **PID controller** to dynamically adjust queue timeouts and inflight limits based on real-time latency and error signals, and (c) employs an **Auto Tuner** to maximize throughput by continuously adapting concurrency limits.

**Tradeoff**: PID-based control adds tuning complexity (proportional, integral, derivative gains), but eliminates the manual tuning toil of static thresholds and prevents the premature shedding → retry → thundering herd cycle that plagued CoDel.

**Related**: [Cinnamon Load Shedder](https://www.uber.com/gb/en/blog/cinnamon-using-century-old-tech-to-build-a-mean-load-shedder/), [PID Controller for Cinnamon](https://www.uber.com/gb/en/blog/pid-controller-for-cinnamon/), [Cinnamon Auto Tuner](https://www.uber.com/blog/cinnamon-auto-tuner-adaptive-concurrency-in-the-wild/), [Thundering Herd](../../reference-dictionary/resilience.md#thundering-herd)

---

## resilience-20: Unified BYOS Load Shedding Engine

| | |
|:---|:---|
| **Problem** | External token-bucket rate limiters handle remote shedding decisions (e.g., shedding because followers are lagging, not because the local node is overloaded), but they operate outside the admission control path — causing split-brain behaviors where the local shedder and remote shedder make conflicting decisions. |
| **Root cause** | Overload signals are fragmented: concurrency-based signals are handled by the local load shedder while remote signals (follower commit lag) are handled by separate token-bucket components with no coordination. |

**Strategy**: Unify all overload signals into a single **BYOS (Bring Your Own Signal)** pluggable architecture within Cinnamon. Every signal — local concurrency, write bytes, partition key hotspots, memory pressure, goroutine count, or remote follower commit lag — feeds into the same PID-regulated, priority-aware admission control loop. Shedding is either broad-by-priority or precise-by-caller depending on the signal type.

**Tradeoff**: A unified engine is more complex to design and test than independent point solutions, but it eliminates the split-brain problem entirely and makes the system extensible — new overload signals become plugins, not new systems.

**Related**: [Load Shedding](../../reference-dictionary/resilience.md#load-shedding), [Circuit Breaker](../../reference-dictionary/resilience.md#circuit-breaker), [Blast Radius](../../reference-dictionary/resilience.md#blast-radius)

---

## resilience-21: Multitenant Fairness with Scorecard Engine

| | |
|:---|:---|
| **Problem** | A single noisy tenant can saturate shared database resources (concurrency, I/O, memory) without triggering a system-wide overload — load shedding alone won't intervene because global concurrency thresholds aren't crossed, but other tenants experience degraded performance. |
| **Root cause** | Load shedding protects against system-wide overload but is blind to per-tenant resource hogging below the global threshold. |

**Strategy**: Deploy a **Scorecard Engine** — a rule-based, deterministic admission control component that enforces per-tenant concurrency limits independently of system load. It operates in parallel with the load shedder: the shedder handles global overload by priority, the Scorecard caps individual tenants regardless of system state.

**Tradeoff**: Per-tenant limits can reject requests from a tenant that is within its fair-use bounds during low system load, but the predictability and blast-radius containment for incident scenarios (pinpointing the noisy tenant instantly) justifies the occasional false positive.

**Related**: [Bulkhead](../../reference-dictionary/resilience.md#bulkhead), [Blast Radius](../../reference-dictionary/resilience.md#blast-radius), [Rate Limiting](../../reference-dictionary/api-design.md#rate-limiting)

---

## Cross-References

- **Dictionary**: [Resilience & Fault Tolerance](../../reference-dictionary/resilience.md)
- **Taxonomy**: §7.1 Reliability & Resilience
- **Related**: [Circuit Breaker Honesty](circuit-breaker-honesty.md), [Distributed Resilience Patterns](distributed-resilience-patterns.md)
