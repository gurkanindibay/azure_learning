# Resilience & Fault Tolerance

> **Domain**: Circuit breakers, bulkheads, retries, timeouts, and resilience patterns.
> **Parent**: [Reference Dictionary](README.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Circuit Breaker | [`#circuit-breaker`](#circuit-breaker) |
| Bulkhead | [`#bulkhead`](#bulkhead) |
| Retry Amplification | [`#retry-amplification`](#retry-amplification) |
| Fallback | [`#fallback`](#fallback) |
| Timeout | [`#timeout`](#timeout) |
| Resilience Stack | [`#resilience-stack`](#resilience-stack) |
| Graceful Degradation | [`#graceful-degradation`](#graceful-degradation) |
| Cascading Failure | [`#cascading-failure`](#cascading-failure) |
| Thundering Herd | [`#thundering-herd`](#thundering-herd) |

---

## Circuit Breaker

A resilience pattern that **prevvents cascading failures** by detecting when a downstream service is failing and temporarily stopping calls to it. States: **Closed** (normal), **Open** (failing, calls blocked), **Half-Open** (testing recovery).

### Key Configuration

| Parameter | Meaning | Recommended |
|:---|:---|:---|
| `failureRateThreshold` | % of calls that can fail before opening | 50% |
| `slowCallRateThreshold` | % of calls that can be slow before opening | 50% |
| `slowCallDurationThreshold` | What counts as "slow" | 2s |
| `minimumNumberOfCalls` | Minimum calls before breaker evaluates | 10 |
| `slidingWindowSize` | Window for rate calculation | 100 |
| `waitDurationInOpenState` | Time in OPEN before Half-Open | 30s |

> **Key insight**: Monitor slow-call rate as carefully as failure rate. A 6-second successful response is a failed user experience.

**Also see**: [Bulkhead](#bulkhead), [Fallback](#fallback), [Resilience Stack](#resilience-stack) · [Messaging](messaging.md)

---

## Bulkhead

A resilience pattern that **isolates resources** so that a failure in one area does not exhaust resources for the entire system. Named after ship compartments — if one floods, the ship stays afloat.

| Type | Mechanism |
|:---|:---|
| **Thread Pool Bulkhead** | Dedicated thread pool per downstream dependency |
| **Semaphore Bulkhead** | Limits concurrent calls to a dependency |

> **Key insight**: A circuit breaker decides *whether* to call. A bulkhead decides *how many* calls can run concurrently. You need both.

**Also see**: [Circuit Breaker](#circuit-breaker), [Resilience Stack](#resilience-stack)

---

## Retry Amplification

When retries multiply the load on an already-failing system — each failed call triggers N retries, creating **N× original load** at the worst possible time.

**Mitigations**: Circuit breaker must wrap retry (aspect order: Retry → CircuitBreaker), exponential backoff with jitter, max retry limit, retry only on transient errors.

**Also see**: [Circuit Breaker](#circuit-breaker), [Timeout](#timeout) · [Messaging](messaging.md#poison-message)

---

## Fallback

A **degraded but functional response** returned when the primary operation fails. Fallbacks protect user experience when the circuit breaker is OPEN.

**Fallback ladder**: Stale cache → Static default → Degraded experience → Meaningful error.

> **Key insight**: An OPEN circuit breaker with no fallback is not protection — it's just a faster failure.

**Also see**: [Circuit Breaker](#circuit-breaker), [Graceful Degradation](#graceful-degradation)

---

## Timeout

A deadline for how long the system waits for a response. **Without timeouts, a slow downstream can exhaust all threads.**

| Type | Scope |
|:---|:---|
| **Connect Timeout** | Establishing TCP connection |
| **Socket/Read Timeout** | Waiting for response after connection |
| **Total Deadline** | End-to-end, including retries |

**Timeout hierarchy**: `connect_timeout < socket_timeout < total_deadline`

**Also see**: [Resilience Stack](#resilience-stack), [Circuit Breaker](#circuit-breaker)

---

## Resilience Stack

The **ordered composition** of resilience patterns that together create defense in depth.

```
TimeLimiter → CircuitBreaker → Bulkhead → Fallback
```

| Layer | What It Does |
|:---|:---|
| **TimeLimiter** | Caps execution time (fail fast) |
| **CircuitBreaker** | Stops calling broken dependencies |
| **Bulkhead** | Limits concurrent calls (resource isolation) |
| **Fallback** | Returns degraded response when all else fails |

**Also see**: [Circuit Breaker](#circuit-breaker), [Bulkhead](#bulkhead), [Fallback](#fallback), [Timeout](#timeout)

---

## Graceful Degradation

The ability of a system to **continue operating at reduced functionality** rather than failing completely. When a dependency is unavailable, serve stale data, cached results, or limited functionality instead of errors.

**Also see**: [Fallback](#fallback), [Circuit Breaker](#circuit-breaker)

---

## Cascading Failure

A failure in one component that **triggers failures in dependent components**, creating a chain reaction that brings down the entire system. Circuit breakers and bulkheads are the primary defenses.

**Also see**: [Circuit Breaker](#circuit-breaker), [Bulkhead](#bulkhead)

---

## Thundering Herd

When many clients or processes **simultaneously retry** after a failure or cache expiration, overwhelming the recovering system. Mitigated by exponential backoff with **jitter** (randomized delay).

**Also see**: [Circuit Breaker](#circuit-breaker), [Retry Amplification](#retry-amplification) · [Caching](caching.md#cache-stampede)
