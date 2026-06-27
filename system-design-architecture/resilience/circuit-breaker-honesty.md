---
type: System Design
title: "Circuit Breaker Honesty — Key Takeaways"
description: "resilience4j:"
timestamp: 2026-06-14T00:00:00Z
---

# 23. Circuit Breaker Honesty — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Your Circuit Breaker Is Lying to You](../../../articles/resilience/your-circuit-breaker-lying-to-you.md) — The Atomic Architect, Apr 2026
> **Purpose**: Extract the gap between "having a circuit breaker" and "protecting the user experience" — the four lies circuit breakers tell, and how to build an honest resilience stack.
> **Also see**: [Resilience Patterns](resilience/resilience-patterns.md) (`resilience-01`–`resilience-06`), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md), [API Design Patterns](api-network/api-design-patterns.md)
> **Taxonomy Reference**: §7.1 Reliability & Resilience

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`cb-01`](#cb-01-monitor-slow-call-rate-not-just-failure-rate) | "No Errors Means No Problem" | Slow-call threshold matters as much as failure threshold |
| [`cb-02`](#cb-02-minimumnumberofcalls--the-hidden-trap) | Hidden Inside Your Window | `minimumNumberOfCalls` masks failures in low-throughput flows |
| [`cb-03`](#cb-03-circuit-breaker--concurrency-control) | "A Circuit Breaker Controls Load" | Breaker decides *whether* to call, not *how many* — need Bulkhead |
| [`cb-04`](#cb-04-retries-multiply-load) | "Retries Make It Safer" | Retries amplify load; aspect order between Retry and CircuitBreaker matters |
| [`cb-05`](#cb-05-the-honest-resilience-stack) | What an Honest Design Looks Like | TimeLimiter → CircuitBreaker → Bulkhead → Fallback |
| [`cb-06`](#cb-06-fallback-is-the-real-product) | Fallback Is the Real Product | An OPEN breaker with no fallback is not protection |
| [`cb-07`](#cb-07-user-experience-metrics--breaker-state-metrics) | The Metrics I Care About Now | Measure user experience, not just breaker state |

---

## cb-01: Monitor Slow-Call Rate, Not Just Failure Rate

> **Source**: [Article §"The First Lie"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#the-first-lie-no-errors-means-no-problem)

| | |
|:---|:---|
| **Problem** | Teams configure circuit breakers only on failure rate (exceptions) and ignore slow-call rate — latency degrades user experience while dashboards stay green. |
| **Root cause** | Equating "returned 200 OK" with "healthy" — ignoring that a 6-second checkout is a failed user experience. |

### Failure Rate vs Slow-Call Rate

| Metric | What It Catches | What It Misses |
|:---|:---|:---|
| **Failure rate** | Exceptions, HTTP 5xx, timeouts that throw | Successful responses that are too slow |
| **Slow-call rate** | Calls exceeding a latency threshold (e.g., >2s) | Nothing — this is the missing signal |

**Strategy — Configure both thresholds in Resilience4j:**

```yaml
resilience4j:
  circuitbreaker:
    instances:
      catalog:
        slidingWindowSize: 100
        minimumNumberOfCalls: 10
        failureRateThreshold: 50       # Open if 50% of calls fail
        slowCallRateThreshold: 50      # Open if 50% of calls are slow
        slowCallDurationThreshold: 2s  # "Slow" = >2 seconds
        waitDurationInOpenState: 30s
```

> **Key insight**: Slowness is often the **beginning** of real failure. The slow-call threshold catches degradation before it becomes an outage.

**Cross-reference**: This complements [`resilience-02`](resilience/resilience-patterns.md#resilience-02-circuit-breaker--stop-calling-dead-services) which covers circuit breaker fundamentals (states, thresholds, half-open).

---

## cb-02: `minimumNumberOfCalls` — The Hidden Trap

> **Source**: [Article §"The Second Lie"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#the-second-lie-hidden-inside-your-window)

| | |
|:---|:---|
| **Problem** | Circuit breaker never opens despite all calls failing — `minimumNumberOfCalls` hasn't been reached yet. |
| **Root cause** | The breaker cannot calculate failure/slow-call rate until the minimum sample size is met. In low-throughput flows, this may never happen. |

### The Math That Lies

```
minimumNumberOfCalls = 10
Actual calls: 9 terrible calls, all failed
Breaker state: CLOSED ← because 9 < 10
```

**Strategy — Tune `minimumNumberOfCalls` to your traffic profile:**

| Traffic Profile | Recommended `minimumNumberOfCalls` | Why |
|:---|:---|:---|
| **High throughput** (>100 req/s) | 20–50 | Large sample avoids noise |
| **Medium throughput** (10–100 req/s) | 10–20 | Balance responsiveness with stability |
| **Low throughput** (<10 req/s) | 3–5 | Don't let failures hide below the math |
| **Critical path** (single-user impact) | 1–3 | Every failure matters |

### Window Type Selection

| Window Type | Best For | Risk |
|:---|:---|:---|
| **Count-based** | Steady traffic | Misses bursts; overreacts to noise at small sizes |
| **Time-based** | Bursty traffic | Better reflects recent seconds; depends on traffic shape |

> **Key insight**: "The breaker never opened" is not a success metric. It may mean your traffic politely failed below the `minimumNumberOfCalls`.

---

## cb-03: Circuit Breaker ≠ Concurrency Control

> **Source**: [Article §"The Third Lie"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#the-third-lie-a-circuit-breaker-controls-load)

| | |
|:---|:---|
| **Problem** | Teams treat the circuit breaker as a concurrency limiter — assuming it caps how many calls run at once. When the breaker is CLOSED, all threads proceed, turning the dependency into a traffic amplifier under pressure. |
| **Root cause** | Confusing *gatekeeping* (should we call?) with *concurrency limiting* (how many calls at once?). |

### Breaker vs Bulkhead — Different Problems

| Concern | Circuit Breaker | Bulkhead |
|:---|:---|:---|
| **Question it answers** | "Should we even try?" | "How many can try at once?" |
| **When it acts** | After failures accumulate (delayed judgment) | Before calls execute (immediate cap) |
| **What it prevents** | Calling a dead/dying dependency | One slow dependency starving all threads |
| **CLOSED state behavior** | All calls proceed | Capped to `maxConcurrentCalls` |

**Strategy — Always pair a circuit breaker with a bulkhead:**

```java
@Bulkhead(name = "catalog", type = Bulkhead.Type.SEMAPHORE)
@CircuitBreaker(name = "catalog")
public CatalogResponse fetchProduct(String sku) {
    // Bulkhead caps concurrent calls even when breaker is CLOSED
    return catalogRestClient.get()...;
}
```

```yaml
resilience4j:
  bulkhead:
    instances:
      catalog:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms   # Fail fast, don't queue
```

> **Key insight**: "The breaker is not a wall. It is a gatekeeper with delayed judgment. If the crowd is already inside, that judgment arrives late."

**Cross-reference**: See [`resilience-03`](resilience/resilience-patterns.md#resilience-03-bulkhead--thread-pool-isolation) for bulkhead patterns and thread pool isolation.

---

## cb-04: Retries Multiply Load

> **Source**: [Article §"The Fourth Lie"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#the-fourth-lie-retries-make-it-safer)

| | |
|:---|:---|
| **Problem** | Retries amplify load on an already struggling dependency — one user request becomes N downstream calls. Combined with a circuit breaker in the wrong aspect order, they hide each other's failures. |
| **Root cause** | `maxAttempts` includes the initial call; engineers forget the multiplication effect. |

### The Multiplication Math

```
1 user request
  → maxAttempts = 3 (1 initial + 2 retries)
  → 3 downstream calls

Under load: 1000 req/s → 3000 downstream calls
If the dependency is already slow → catastrophic amplification
```

### Aspect Order Matters

In Spring AOP, the default aspect order determines which wraps which:

| Order | Behavior | Risk |
|:---|:---|:---|
| **Retry outside Breaker** | Retry → Breaker: each retry is evaluated by breaker | Retries count toward breaker thresholds (good) |
| **Breaker outside Retry** | Breaker → Retry: breaker opens, retries are blocked | Retries don't add pressure when breaker is OPEN (good) |

**Strategy — Prefer functional chaining for explicit ordering:**

```java
// Explicit order: TimeLimiter → CircuitBreaker → Retry → Bulkhead
DecorateCompletionStage
    .ofCompletionStage(() -> callDownstream())
    .withTimeLimiter(timeLimiter)
    .withCircuitBreaker(circuitBreaker)
    .withRetry(retry)
    .withBulkhead(bulkhead)
    .get();
```

> **Key insight**: "Your dashboard says resilience. Your dependency sees multiplication. Your users see hesitation."

**Cross-reference**: See [`resilience-04`](resilience/resilience-patterns.md#resilience-04-timeouts--retries-with-backoff) for timeout and retry backoff patterns.

---

## cb-05: The Honest Resilience Stack

> **Source**: [Article §"What an Honest Design Looks Like"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#what-an-honest-design-looks-like)

| | |
|:---|:---|
| **Problem** | Teams add a circuit breaker and stop — missing the three other pillars that make resilience actually protect users. |
| **Root cause** | Treating circuit breaker as the destination, not one component in a stack. |

### The Four Pillars of Honest Resilience

| # | Pillar | Implementation | Without It |
|:---|:---|:---|:---|
| 1 | **Fail Fast** | `TimeLimiter` with explicit timeout | Slow responses consume threads, cascade to callers |
| 2 | **Measure Slowness** | Circuit breaker with `slowCallRateThreshold` | Failure-only breaker stays CLOSED during latency degradation |
| 3 | **Limit Concurrency** | `Bulkhead` (semaphore or thread pool) | One slow dependency starves the entire thread pool |
| 4 | **Provide Fallback** | Explicit `fallbackMethod` — cache, stale data, partial response | OPEN breaker returns raw 500; user gets nothing |

### The Stack in Code

```java
@TimeLimiter(name = "catalog")                          // Pillar 1: Fail fast
@Bulkhead(name = "catalog", type = Bulkhead.Type.SEMAPHORE) // Pillar 3: Limit concurrency
@CircuitBreaker(name = "catalog", fallbackMethod = "readFromCache") // Pillars 2+4
public CompletableFuture<CatalogResponse> fetchProduct(String sku) {
    // ...
}
```

### The Architecture

```
User Request
    │
    v
TimeLimiter        ← "You have 2 seconds"
    │
    v
CircuitBreaker     ← "Is the dependency healthy?"
    │                    ├─ CLOSED → proceed
    │                    ├─ OPEN → fallback immediately
    │                    └─ HALF_OPEN → test with 1 call
    │
    v
Bulkhead           ← "Max 10 concurrent calls"
    │
    ├── success ──► Downstream Service
    │
    └── failure ──► Fallback Path (cache → stale → partial → unavailable)
                         │
                         v
                   Useful User Response
```

**Cross-reference**: See [`resilience-06`](resilience/resilience-patterns.md#resilience-06-the-resilience-stack) for composing all resilience patterns.

---

## cb-06: Fallback Is the Real Product

> **Source**: [Article §"What an Honest Design Looks Like"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#what-an-honest-design-looks-like)

| | |
|:---|:---|
| **Problem** | Circuit breaker opens → user gets a raw 500. The downstream service is protected, but the user experience is destroyed. |
| **Root cause** | Teams treat "breaker opened" as the happy ending — it's only the start of controlled degradation. |

### The Fallback Ladder

Design a progressively degraded experience:

```
1. Fresh data from downstream
       ↓ (breaker open / timeout)
2. Cached data (slightly stale, still useful)
       ↓ (cache miss)
3. Static fallback / default values
       ↓ (not applicable)
4. Partial response (degraded but not broken)
       ↓ (nothing available)
5. Graceful unavailable message with retry guidance
```

**Strategy — Always design the fallback alongside the breaker:**

```java
@CircuitBreaker(name = "catalog", fallbackMethod = "readFromCache")
public CompletableFuture<CatalogResponse> fetchProduct(String sku) {
    // Primary path
}

// Fallback: cache → stale → unavailable
private CompletableFuture<CatalogResponse> readFromCache(
        String sku, Throwable t) {
    log.warn("catalog degraded for sku={}, reason={}", sku, t.toString());

    CatalogResponse response = Optional.ofNullable(
            cacheManager.getCache("catalog").get(sku))
        .map(wrapper -> (CatalogResponse) wrapper.get())
        .orElse(CatalogResponse.unavailable(sku));

    return CompletableFuture.completedFuture(response);
}
```

> **Key insight**: "An OPEN breaker can still serve a useful response. A CLOSED breaker can still hide pain. The breaker is the traffic signal before the fallback, not the destination."

---

## cb-07: User Experience Metrics > Breaker State Metrics

> **Source**: [Article §"The Metrics I Care About Now"](../../../articles/resilience/your-circuit-breaker-lying-to-you.md#the-metrics-i-care-about-now)

| | |
|:---|:---|
| **Problem** | Teams monitor breaker state (CLOSED/OPEN/HALF_OPEN) and miss what the user actually experienced. |
| **Root cause** | Measuring the tool's health instead of the user's health. |

### Dashboard vs Reality

| Your Dashboard Says | The User Experienced |
|:---|:---|
| Breaker is CLOSED, 0% failure rate | Checkout took 8 seconds, user left |
| All retries succeeded (after 3 attempts) | Page loaded after 9 seconds of spinner |
| Breaker opened and rejected calls | Raw 500 error with no helpful message |

### The Five Questions

Replace "Is the breaker OPEN?" with:

| # | Question | Signal |
|:---|:---|:---|
| 1 | Did latency get bad **before** failures spiked? | Slow-call rate trend > failure rate trend |
| 2 | Did retries quietly **multiply** pressure? | (Downstream calls) / (User requests) ratio |
| 3 | Did the fallback actually return something **helpful**? | Fallback response quality, not just fallback invocation count |
| 4 | Did we **cap** concurrency, or just measure collapse? | Bulkhead rejection rate + thread pool saturation |
| 5 | Did the dashboard report breaker state, but **hide** the customer experience? | End-to-end user journey latency, not just per-service metrics |

> **Key insight**: "The real maturity test is not 'Do you have a circuit breaker?' — almost everyone has one now. The real question is whether your breaker is telling the truth about the experience your system is creating."

---

## Quick Diagnostic Table

| Symptom | Likely Problem | Strategy | Ref |
|:---|:---|:---|:---:|
| "Breaker stays CLOSED but users complain about slowness" | Only failure rate threshold configured | Add `slowCallRateThreshold` | [`cb-01`](#cb-01-monitor-slow-call-rate-not-just-failure-rate) |
| "All calls fail but breaker never opens" | `minimumNumberOfCalls` not reached | Lower minimum for low-throughput flows | [`cb-02`](#cb-02-minimumnumberofcalls--the-hidden-trap) |
| "One slow downstream starves all other requests" | No bulkhead — breaker doesn't cap concurrency | Add `@Bulkhead` with `maxConcurrentCalls` | [`cb-03`](#cb-03-circuit-breaker--concurrency-control) |
| "Retries amplify load 3x when dependency is slow" | `maxAttempts` too high; aspect order unclear | Lower retries; use functional chaining for explicit order | [`cb-04`](#cb-04-retries-multiply-load) |
| "Breaker opens but users get raw 500" | No fallback method configured | Implement fallback ladder (cache → stale → unavailable) | [`cb-05`](#cb-05-the-honest-resilience-stack), [`cb-06`](#cb-06-fallback-is-the-real-product) |
| "Dashboards green but users angry" | Measuring breaker state, not user experience | Add the five questions to your dashboard review | [`cb-07`](#cb-07-user-experience-metrics--breaker-state-metrics) |
