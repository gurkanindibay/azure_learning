---
type: Reference
title: "Resilience & Fault Tolerance"
description: "A resilience pattern that **prevvents cascading failures** by detecting when a downstream service is failing and temporarily stopping calls to it. States: **Closed** (normal), **Open** (failing, ca..."
timestamp: 2026-06-14T00:00:00Z
---

# Resilience & Fault Tolerance

> **Domain**: Circuit breakers, bulkheads, retries, timeouts, and resilience patterns.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Circuit Breaker | [`#circuit-breaker`](#circuit-breaker) |
| Half-Open State | [`#half-open-state`](#half-open-state) |
| Aspect Order | [`#aspect-order`](#aspect-order) |
| Bulkhead | [`#bulkhead`](#bulkhead) |
| Retry Amplification | [`#retry-amplification`](#retry-amplification) |
| Exponential Backoff | [`#exponential-backoff`](#exponential-backoff) |
| Jitter | [`#jitter`](#jitter) |
| Fallback | [`#fallback`](#fallback) |
| Timeout | [`#timeout`](#timeout) |
| Resilience Stack | [`#resilience-stack`](#resilience-stack) |
| Graceful Degradation | [`#graceful-degradation`](#graceful-degradation) |
| Partial Response | [`#partial-response`](#partial-response) |
| Cascading Failure | [`#cascading-failure`](#cascading-failure) |
| Thundering Herd | [`#thundering-herd`](#thundering-herd) |
| Defense in Depth | [`#defense-in-depth`](#defense-in-depth) |
| Chaos Engineering | [`#chaos-engineering`](#chaos-engineering) |
| Load Shedding | [`#load-shedding`](#load-shedding) |
| Backpressure | [`#backpressure`](#backpressure) |
| Blast Radius | [`#blast-radius`](#blast-radius) |
| Correlated Failure Domain | [`#correlated-failure-domain`](#correlated-failure-domain) |
| Fail-safe vs Fail-secure | [`#fail-safe-vs-fail-secure`](#fail-safe-vs-fail-secure) |
| Defensive Programming | [`#defensive-programming`](#defensive-programming) |
| Input Validation | [`#input-validation`](#input-validation) |
| Parameterized Query | [`#parameterized-query`](#parameterized-query) |
| Shadow Testing | [`#shadow-testing`](#shadow-testing) |
| CoDel (Controlled Delay) | [`#codel-controlled-delay`](#codel-controlled-delay) |
| Cinnamon Load Shedder | [`#cinnamon-load-shedder`](#cinnamon-load-shedder) |
| PID-Based Load Shedding | [`#pid-based-load-shedding`](#pid-based-load-shedding) |
| Adaptive LIFO | [`#adaptive-lifo`](#adaptive-lifo) |
| Scorecard Engine | [`#scorecard-engine`](#scorecard-engine) |
| Retry Storm | [`#retry-storm`](#retry-storm) |
| Virtual Waiting Room | [`#virtual-waiting-room`](#virtual-waiting-room) |

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

**Also see**: [Bulkhead](#bulkhead), [Fallback](#fallback), [Half-Open State](#half-open-state), [Resilience Stack](#resilience-stack) · [Messaging](messaging.md)

---

## Half-Open State

The **testing state** between OPEN and CLOSED in a circuit breaker. After `waitDurationInOpenState` expires, the breaker transitions to Half-Open and allows a **limited number of probe calls**. If probes succeed → CLOSED. If they fail → back to OPEN.

| State | Behavior |
|:---|:---|
| **CLOSED** | Normal — all calls pass through |
| **OPEN** | Failing — all calls blocked immediately |
| **HALF-OPEN** | Testing — limited probe calls allowed |

**Also see**: [Circuit Breaker](#circuit-breaker), [Resilience Stack](#resilience-stack)

---

## Aspect Order

The **order in which resilience decorators are composed** matters critically. Wrong ordering creates dangerous behavior.

```
CORRECT:   TimeLimiter → CircuitBreaker → Bulkhead → Retry → Fallback
WRONG:     Retry → Bulkhead → CircuitBreaker → TimeLimiter
```

| Correct Order | Why |
|:---|:---|
| **TimeLimiter first** | Time out before anything else — don't waste resources |
| **CircuitBreaker second** | Stop calling if dependency is broken |
| **Bulkhead third** | Limit concurrent calls to surviving dependencies |
| **Retry fourth** | Retry within the bulkhead (not outside it) |
| **Fallback last** | Return degraded response when all else fails |

> **Key insight**: Retry must be INSIDE the CircuitBreaker — each retry counts toward the breaker's failure rate. If Retry is outside, the breaker never sees failures.

**Also see**: [Resilience Stack](#resilience-stack), [Circuit Breaker](#circuit-breaker), [Retry Amplification](#retry-amplification)

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

## Exponential Backoff

A retry strategy that **increases the wait time between retries exponentially** after each failure. Combined with jitter, it prevents a thundering herd from overwhelming a recovering downstream service.

### Key Characteristics
- **Wait interval grows**: 100 ms → 200 ms → 400 ms → 800 ms → capped maximum
- **Caps at a maximum delay** to avoid unbounded wait times
- **Adds jitter** (randomized offset) to desynchronize retry storms
- **Resets on success** so healthy paths stay fast

### When to Use
- Retrying transient failures from external services, networks, or databases
- Before a circuit breaker opens, to give the dependency time to recover

### When NOT to Use
- For non-retryable errors (4xx client errors, business validation failures)
- When low latency is more important than eventual success

### Also see
- [Retry Amplification](#retry-amplification) · [Circuit Breaker](#circuit-breaker) · [Thundering Herd](#thundering-herd)

---

## Jitter

A **randomized delay** added to retry intervals or scheduled operations to desynchronize clients and prevent thundering-herd effects. Without jitter, clients using the same backoff algorithm retry at identical intervals, creating synchronized waves of traffic that overwhelm recovering systems.

### Key Characteristics
- **Random offset**: a random value (e.g., ±25% of the base interval) added to each retry delay
- **Desynchronization**: prevents multiple clients from retrying at the same instant
- **Works with any backoff strategy**: linear, exponential, or fixed intervals
- **Low cost**: trivial to implement — a single random number per retry attempt

### When to Use
- Every retry implementation in distributed systems — without exception
- Scheduled background jobs that run across multiple instances
- Cache refresh or TTL-based operations where simultaneous expiration causes stampedes

### When NOT to Use
- When deterministic timing is required for correctness (rare in practice)
- As a substitute for proper backoff — jitter alone without increasing intervals still causes storms

### Also see
- [Exponential Backoff](#exponential-backoff) · [Thundering Herd](#thundering-herd) · [Retry Amplification](#retry-amplification)

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

## Partial Response

A degraded result where the service returns **what it can produce** rather than failing entirely when one or more downstream dependencies are unavailable. Instead of returning a 500 error or an empty page, the system omits the broken section and delivers the rest — e.g., showing the user profile without "recent activity" because the activity-feed service is down.

### Key Characteristics
- **Selective omission**: broken subsections are dropped; healthy sections render normally
- **Explicit signaling**: the UI should indicate what was omitted (e.g., "Recommendations unavailable right now") rather than silently hiding it
- **Per-component fallback**: each page section or API response fragment has its own timeout + fallback, so one slow dependency doesn't block everything
- **Sits between full response and full failure** on the fallback ladder

### When to Use
- Dashboards or feeds where multiple backend services contribute to a single view
- API responses that aggregate data from several microservices (GraphQL, BFF pattern)
- Any page where blank space with a note is better than a spinner or error page

### When NOT to Use
- When the missing data is critical to the response's meaning (e.g., a payment confirmation without the amount)
- When partial data would be actively misleading (e.g., a compliance report showing "0 violations" because the audit service timed out)
- As a substitute for fixing the underlying dependency — partial responses are a bridge, not a solution

### Also see
- [Fallback](#fallback) · [Graceful Degradation](#graceful-degradation) · [Circuit Breaker](#circuit-breaker)

---

## Cascading Failure

A failure in one component that **triggers failures in dependent components**, creating a chain reaction that brings down the entire system. Circuit breakers and bulkheads are the primary defenses.

**Also see**: [Circuit Breaker](#circuit-breaker), [Bulkhead](#bulkhead)

---

## Thundering Herd

When many clients or processes **simultaneously retry** after a failure or cache expiration, overwhelming the recovering system. Mitigated by exponential backoff with **jitter** (randomized delay).

**Also see**: [Circuit Breaker](#circuit-breaker), [Retry Amplification](#retry-amplification) · [Caching](caching.md#cache-stampede)

---

## Defense in Depth

A security and reliability principle that **layers multiple independent controls** so that no single failure can compromise the system. In distributed systems this means combining validation, checksums, retries, circuit breakers, encryption, audits and observability rather than relying on one mechanism.

### Key Characteristics
- **Independent layers**: each control protects against a different class of failure or threat
- **No single point of safety**: one layer can fail while others still contain the damage
- **Validation at every boundary**: write path, read path, replication path and downstream consumers

### When to Use
- Systems where silent data corruption or security breaches are unacceptable
- Any architecture moving from a single trust domain to distributed services

### When NOT to Use
- As an excuse for unnecessary complexity in low-risk internal tools
- When layers are not truly independent (multiple layers with the same bug add no value)

### Also see
- [Resilience Stack](#resilience-stack) · [Circuit Breaker](#circuit-breaker) · [Chaos Engineering](#chaos-engineering)

---

## Chaos Engineering

The practice of **deliberately injecting failures** into a production-like system to discover weaknesses before they cause real outages. Coined and popularized by Netflix, it turns “unknown unknowns” into observable, fixable gaps.

### Key Characteristics
- **Hypothesis-driven**: start with a specific failure mode and expected system behavior
- **Production-realistic**: ideally run in production with automatic abort criteria
- **Blast-radius controlled**: use canaries, traffic segmentation and rollback plans

### When to Use
- Mature services with strong observability and rollback mechanisms
- Before high-traffic events or after major architecture changes

### When NOT to Use
- On systems without adequate monitoring or rollback capability
- As a one-off stunt without follow-up remediation

### Also see
- [Defense in Depth](#defense-in-depth) · [Canary Deployment](deployment-patterns.md#canary-deployment)

---

## Load Shedding

A resilience tactic where the system **intentionally drops some traffic** to protect core functionality during overload. The goal is to survive a “success disaster” by sacrificing non-critical requests instead of collapsing entirely.

### Key Characteristics
- **Priority-based**: critical requests are preserved, low-priority or expensive requests are dropped
- **Fast feedback**: rejected clients receive a clear error (e.g., 503 with `Retry-After`) instead of timing out
- **Coordinated**: ideally applied at the edge, API gateway and queue levels

### When to Use
- Sudden traffic spikes that exceed provisioned capacity
- Cascading failure scenarios where a downstream dependency is saturated

### When NOT to Use
- As a substitute for proper capacity planning
- When every request has the same business criticality and cannot be ranked

### Also see
- [Circuit Breaker](#circuit-breaker) · [Rate Limiting](api-design.md#rate-limiting) · [Bulkhead](#bulkhead)

---

## Backpressure

A flow-control mechanism where an **overloaded downstream signals upstream to slow down**, preventing queues from growing unbounded and memory from exhausting. It is the distributed-system equivalent of a pressure-release valve.

### Key Characteristics
- **Upstream-aware**: producers throttle based on consumer capacity (e.g., bounded queues, TCP windowing, gRPC flow control)
- **Bounded queues**: fixed-size buffers force shedding or blocking instead of unbounded growth
- **Propagation**: backpressure should flow end-to-end, not be swallowed at one layer

### When to Use
- Streaming pipelines, message brokers and async I/O where producer and consumer speeds differ
- Any system where unbounded buffering would cause memory exhaustion or tail latency spikes

### When NOT to Use
- When latency is more important than durability (shedding may be preferable to slowing down)
- Without a clear policy for what happens when the bound is reached (block, drop, or reject)

### Also see
- [Load Shedding](#load-shedding) · [Bulkhead](#bulkhead) · [Messaging](messaging.md)

---

## Blast Radius

The **scope of impact** when a component fails or a change goes wrong — measured in terms of users affected, services disrupted, or data corrupted. Minimizing blast radius is a core principle of resilient system design: a failure in one shard, region, or deployment unit should not propagate to the entire system.

### Key Characteristics
- **Bounded by isolation**: bulkheads, sharding, regional independence, and canary deployments all reduce blast radius
- **Proportional to propagation speed**: the faster a change propagates (e.g., global config push), the larger the blast radius
- **Measurable**: can be quantified as number of requests, users, or revenue affected per incident

### When to Use
- Designing deployment pipelines — canary or ring-based rollouts limit blast radius
- Auditing shared infrastructure — ask "if this fails, what else breaks?"
- Reviewing configuration changes — validate blast radius before global propagation

### When NOT to Use
- As the sole metric — a small blast radius with a long MTTR is still dangerous
- Without considering correlated failure domains that amplify a small event

### Also see
- [Bulkhead](#bulkhead) · [Correlated Failure Domain](#correlated-failure-domain) · [Circuit Breaker](#circuit-breaker) · [Canary Deployment](deployment-patterns.md#canary-deployment)

---

## Correlated Failure Domain

A set of components that appear independent but **share a hidden dependency or schedule** that causes them to fail together. The Datadog 2023 outage is a canonical example: five regions on different cloud providers all failed simultaneously because they shared the same OS update schedule.

### Key Characteristics
- **Hidden coupling**: the shared element is often invisible at the architecture level (OS images, update channels, package registries, DNS resolvers)
- **Amplification**: a small trigger (a systemd update) can cascade across all "independent" regions
- **Detection requires auditing**: standard architecture diagrams won't reveal correlated failure domains

### When to Use
- Auditing multi-region deployments — catalog every shared component across regions
- Staggered maintenance windows — ensure no single event can hit all regions simultaneously

### When NOT to Use
- As an argument against standardization — the cure is staggered rollouts, not per-region snowflakes
- Without considering the tradeoff between uniform security posture and blast-radius containment

### Also see
- [Blast Radius](#blast-radius) · [Bulkhead](#bulkhead) · [Defense in Depth](#defense-in-depth)

---

## Fail-safe vs Fail-secure

Two opposing **failure mode design philosophies**. A **fail-safe** system defaults to a safe state when it fails (e.g., an elevator brake engages when power is lost). A **fail-secure** system defaults to a secure/restricted state (e.g., a door locks when power is lost, keeping intruders out). In distributed systems, the Meta 2021 outage illustrates the tension: DNS servers that withdrew BGP routes on health-check failure were fail-safe (prevent routing users to dead servers), but when all servers failed simultaneously, the combined effect was worse than doing nothing.

### Key Characteristics
- **Fail-safe (fail-open)**: prioritize availability — keep serving even if degraded
- **Fail-secure (fail-closed)**: prioritize security/consistency — stop serving rather than risk incorrect behavior
- **Context-dependent**: the same mechanism can be correct for partial failures and catastrophic for total failures

### When to Use
- **Fail-safe**: user-facing services where degraded service is better than no service
- **Fail-secure**: financial transactions, access control, data integrity where correctness > availability

### When NOT to Use
- When the safety mechanism has no "floor" — always model what happens when all instances trigger simultaneously
- Without a human-in-the-loop override for total-failure scenarios

### Also see
- [Circuit Breaker](#circuit-breaker) · [Graceful Degradation](#graceful-degradation) · [Defense in Depth](#defense-in-depth)

---

## Defensive Programming

A software development approach that **writes code with the assumption that it can fail** — proactively guarding against invalid inputs, unexpected states, and external failures rather than reacting after they occur. The goal is to reduce the surface area of bugs and security vulnerabilities before they reach production.

### Key Characteristics
- All external inputs are validated and sanitized before use
- Errors are handled explicitly; unhandled exceptions are treated as design flaws
- Invariants are expressed as executable assertions in development/test builds
- Dependencies (third-party libraries) are regularly audited for vulnerabilities
- Code is designed to degrade gracefully rather than fail catastrophically

### When to Use
- Any user-facing system where inputs originate outside the trust boundary
- Batch or pipeline systems where a single bad record should not halt the entire run
- Security-sensitive paths (authentication, payment, data storage)
- Long-lived systems where dependency drift introduces ongoing CVE risk

### When NOT to Use
- As a substitute for proper architecture — defensive coding reduces bugs but does not fix fundamentally flawed designs
- In performance-critical inner loops where every validation adds measurable overhead

### Also see
- [Fail Fast](#fail-fast) · [Defense in Depth](resilience.md#defense-in-depth) · [Input Validation](#input-validation) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md)

---

## Input Validation

The practice of **verifying that all user-supplied or externally sourced data meets expected criteria** (type, format, range, and length) before it is processed or persisted. Paired with sanitization (escaping or stripping dangerous characters), it is the primary defense against injection attacks and undefined behavior from malformed data.

### Key Characteristics
- Allow-list approach: accept only known-good patterns, reject everything else
- Applied at every system boundary (API layer, message consumer, file parser)
- Distinct from business-rule validation — security validation happens first
- Complements but does not replace parameterized queries or output encoding

### When to Use
- Every endpoint that accepts data from an external caller (HTTP, message queue, file upload)
- Before persisting to a database or passing to a downstream service
- As the first layer of a defense-in-depth stack

### When NOT to Use
- As the sole defense against injection — validation alone cannot replace parameterized queries for SQL or context-aware encoding for HTML
- On already-validated internal data flowing through trusted service boundaries

### Also see
- [Defensive Programming](#defensive-programming) · [Parameterized Query](#parameterized-query) · [Fail Fast](#fail-fast) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md#arch-12-input-validation-as-security-boundary)

---

## Parameterized Query

A database query technique where **user-supplied values are passed as separate parameters** rather than concatenated directly into the SQL string. The database engine treats parameters as data, never as executable SQL, which eliminates SQL injection at the source.

### Key Characteristics
- Parameters are typed and bound after the query structure is compiled
- Works across all major databases (PostgreSQL, MySQL, SQL Server, SQLite)
- Equivalent constructs: prepared statements, stored procedures with bound parameters, ORM-generated queries
- Does not prevent all injection vectors — stored procedure logic can still be vulnerable if it re-concatenates internally

### When to Use
- Every database query that incorporates any external input, regardless of perceived trust level
- Batch inserts and updates that loop over user-supplied records

### When NOT to Use
- Dynamic object identifiers (table names, column names) cannot be parameterized — use a strict allow-list instead
- When stored procedures reconstruct SQL internally — audit the procedure body separately

### Also see
- [Input Validation](#input-validation) · [Defensive Programming](#defensive-programming) · [Defensive Coding Key Takeaways](../system-design-architecture/51-defensive-coding-key-takeaways.md#arch-12-input-validation-as-security-boundary)

---

## Shadow Testing

A **validation technique** where production traffic is replicated and replayed in an isolated, non-production environment to compare the behavior of a legacy system against a new or modified system. Unlike traditional testing, shadow testing uses real production payloads — often morphed to test adversarial edge cases — without affecting live users.

### Key Characteristics
- Replays real production traffic (or morphed variants) against the new system in parallel
- Compares outputs between old and new systems to identify state divergence
- Does not affect production users — the shadow environment is fully isolated
- Can be augmented by AI agents that morph traffic to generate extreme boundary-condition payloads

### When to Use
- Migrating critical systems where even a 0.01% error rate is unacceptable
- Validating stateful systems (e.g., event-driven architectures, CQRS) where unit tests cannot capture real-world complexity
- When you need to catch edge-case mismatches before production cutover

### When NOT to Use
- When production data cannot be replicated due to security, compliance, or PII constraints
- Simple stateless services where integration tests already provide sufficient coverage
- When the cost of running a full parallel environment outweighs the migration risk

### Also see
- [Circuit Breaker](#circuit-breaker)
- [Chaos Engineering](#chaos-engineering)
- [Defense in Depth](#defense-in-depth)
- [Dual-Agent Framework](ai-ml-llm.md#dual-agent-framework)

---

## CoDel (Controlled Delay)

A **queue management algorithm** borrowed from networking (designed to combat bufferbloat) that sheds requests based on **how long they have waited in the queue** rather than on queue length. Under normal load the queue behaves as FIFO; under pressure it switches to **Adaptive LIFO**, favoring newer requests that still have a chance to succeed and shedding stale work that clients have likely already abandoned or retried.

### Key Characteristics
- **Wait-time-based shedding**: tracks minimum queue sojourn time over a sliding interval; sheds when it exceeds the target
- **Adaptive LIFO**: FIFO under normal load, LIFO under pressure — fresh requests jump ahead of stale ones
- **Per-operation-type queues**: typically separated into read, write, and slow queues for workload isolation
- **No static thresholds**: the algorithm self-tunes to observed latency, unlike fixed timeout approaches

### When to Use
- Stateful storage systems where queue buildup directly reflects resource saturation
- Multitenant databases where different operation types (point reads vs. scans) have vastly different latency profiles
- As a first line of defense before priority-aware shedding is implemented

### When NOT to Use
- When all requests have equal business criticality — CoDel is priority-agnostic and will drop critical traffic alongside background work
- Systems where fixed, predictable shedding behavior is preferred over adaptive algorithms
- When the queue is rarely the bottleneck (e.g., CPU-bound systems with negligible queuing)

### Also see
- [Load Shedding](#load-shedding) · [Adaptive LIFO](#adaptive-lifo) · [Cinnamon Load Shedder](#cinnamon-load-shedder) · [Thundering Herd](#thundering-herd)

---

## Cinnamon Load Shedder

A **priority-aware load shedder** developed at Uber that replaces simple CoDel-based shedding with intelligent, ranked request shedding. Cinnamon makes admission decisions by combining **request rank** (derived from explicit priority or calling service identity, tiered t0–t5), **dynamic system state** (real-time latency and error rate signals), and **PID-based control** to adjust queue timeouts and inflight limits smoothly rather than reacting abruptly.

### Key Characteristics
- **Tiered priority model**: t0 (critical infrastructure) through t5 (least critical); t1 is user-facing online traffic
- **PID-regulated**: proportional-integral-derivative control prevents overcorrection and premature shedding
- **Auto Tuner**: dynamically adjusts inflight concurrency limits based on observed latency and error rates
- **Simplified queue structure**: priority tags replace separate slow queues — long-running operations are marked low-priority instead

### When to Use
- Systems with heterogeneous traffic where dropping a ride request is far worse than delaying a background GC job
- When static timeout/ inflight-limit tuning has become a source of operational toil
- Multitenant platforms where fairness and priority must coexist

### When NOT to Use
- Homogeneous workloads where all requests are equally important — simpler shedders suffice
- Systems without the observability infrastructure to support PID tuning
- When the operational complexity of PID gain tuning outweighs the benefits of smoother shedding

### Also see
- [Load Shedding](#load-shedding) · [CoDel](#codel-controlled-delay) · [PID-Based Load Shedding](#pid-based-load-shedding) · [Scorecard Engine](#scorecard-engine) · [Thundering Herd](#thundering-herd)

---

## PID-Based Load Shedding

A **control-theoretic approach to load shedding** that uses a Proportional-Integral-Derivative (PID) controller to dynamically adjust shedding thresholds — queue timeouts, inflight limits, or admission rates — based on real-time system signals (latency, error rate). Unlike simple threshold-based shedding that reacts abruptly, PID control incorporates **history (integral term)** and **trend (derivative term)** to make shedding smooth and anticipatory — like a dimmer switch rather than a hammer.

### Key Characteristics
- **Proportional (P)**: reacts to current error (e.g., how far latency is above target)
- **Integral (I)**: corrects for sustained offset — prevents steady-state error where latency lingers slightly above target
- **Derivative (D)**: dampens oscillation by anticipating the trend — prevents overcorrection
- **Smooth shedding**: avoids the thundering-herd cycle caused by rejecting all requests at once and having them all retry simultaneously

### When to Use
- Systems where static shedding thresholds cause oscillation (shed → recover → overload → shed)
- When premature shedding (rejecting before truly necessary) is causing unnecessary 429s and retry storms
- As the control heart of a unified load shedding engine

### When NOT to Use
- Systems too small or too stable to justify PID tuning complexity
- When the signal being controlled is too noisy for a PID loop to stabilize
- As a standalone mechanism without priority-aware shedding — PID controls *how much* to shed, not *what* to shed

### Also see
- [Cinnamon Load Shedder](#cinnamon-load-shedder) · [Load Shedding](#load-shedding) · [CoDel](#codel-controlled-delay) · [Thundering Herd](#thundering-herd)

---

## Adaptive LIFO

A **queue discipline strategy** where the queue switches from FIFO (First-In-First-Out) to LIFO (Last-In-First-Out) under overload. The insight is that during overload, older requests at the head of the queue have likely already timed out or been abandoned by the client — processing them wastes capacity. By switching to LIFO, the system favors newer requests that still have a chance to succeed, effectively failing fast on stale work.

### Key Characteristics
- **State-dependent discipline**: FIFO in normal operation, LIFO under pressure
- **Transition trigger**: typically based on queue sojourn time exceeding a target (as in CoDel)
- **Waste reduction**: avoids processing requests that clients have already abandoned or will retry
- **Works with any backpressure mechanism**: complementary to rate limiting, circuit breaking, and load shedding

### When to Use
- Storage systems with significant queuing where client timeouts are shorter than queue wait times during overload
- As part of a CoDel or similar adaptive queue management implementation
- Any system where the cost of processing a stale request exceeds the cost of rejecting it

### When NOT to Use
- Systems where request ordering guarantees are required (e.g., strict FIFO queues for event sourcing)
- When client timeout windows are much longer than queue wait times — LIFO provides little benefit
- Standalone — Adaptive LIFO is a queue management tactic, not a complete overload protection strategy

### Also see
- [CoDel](#codel-controlled-delay) · [Load Shedding](#load-shedding) · [Backpressure](#backpressure)

---

## Scorecard Engine

A **rule-based, deterministic admission control component** that enforces **per-tenant concurrency limits** in multitenant systems, operating independently of system-wide load. Unlike load shedding (which triggers only during overload), the Scorecard caps individual tenants at all times — preventing a single noisy neighbor from saturating shared resources without triggering global overload thresholds.

### Key Characteristics
- **Per-tenant concurrency caps**: each tenant has a fixed maximum number of in-flight operations
- **Always-on enforcement**: operates during normal load and overload alike
- **Deterministic rules**: simple, predictable configuration — no adaptive tuning
- **Incident containment**: during outages, instantly pinpoints which tenant is driving excess load

### When to Use
- Multitenant databases or platforms where tenants share the same physical resources
- When a single tenant's background job can saturate I/O without crossing global concurrency thresholds
- As a complement to load shedding — Scorecard handles per-tenant fairness, shedder handles global overload

### When NOT to Use
- Single-tenant systems where per-tenant isolation is architectural rather than enforced
- When tenant workloads are homogeneous and well-behaved — the overhead of per-tenant tracking may not justify the benefit
- As a substitute for load shedding — Scorecard does not protect against system-wide overload

### Also see
- [Bulkhead](#bulkhead) · [Load Shedding](#load-shedding) · [Blast Radius](#blast-radius) · [Rate Limiting](api-design.md#rate-limiting)

---

## Retry Storm

A **self-inflicted cascading failure** where upstream services repeatedly retry failed requests to a degraded downstream service, amplifying the load and turning a partial degradation into a full outage. Unlike a simple traffic spike, a retry storm compounds — every retry that also fails generates more retries, creating a positive feedback loop that acts as a self-inflicted Distributed Denial of Service (DDoS) attack on the recovering service.

### Key Characteristics
- **Amplification factor**: If service A calls service B 1 time but retries 3 times on failure, and every service in the call chain does the same, a single user request can become dozens of retries at the deepest layer
- **Synchronization danger**: Without jitter, retries from many clients align in time, creating a thundering herd pattern that hits the degraded service in synchronized waves
- **Blocks recovery**: The degraded service, already struggling, receives even more traffic from retries — preventing it from ever catching up

### When to Use (mitigations)
- Every retry logic in a distributed system must include **exponential backoff** (increasing wait times between retries) and **jitter** (randomized intervals to desynchronize retry waves)
- **Circuit breakers** should be paired with retries — the breaker opens and blocks all calls before retries amplify the load
- **Retry budgets** limit the total number of retries across all requests, preventing unbounded amplification

### When NOT to Use (plain retries)
- Never use fixed-interval retries without backoff — they guarantee a retry storm under degraded conditions
- Never retry on non-idempotent write operations without idempotency keys
- Never retry indefinitely — always set a maximum retry count or deadline

### Also see
- [Circuit Breaker](#circuit-breaker) · [Exponential Backoff](#exponential-backoff) · [Jitter](#jitter) · [Thundering Herd](#thundering-herd) · [Bulkhead](#bulkhead)

---

## Virtual Waiting Room

A **traffic shaping and admission control architecture pattern** that intercepts extreme surges of incoming web traffic during high-demand events (flash sales, concert ticketing, limited product drops) and offloads excess users into a queue before they can reach transactional backend databases.

### Key Characteristics
- **Edge interception**: Implemented at the CDN/Edge layer (Cloudflare Waiting Room, AWS CloudFront + Lambda@Edge) before requests hit origin infrastructure
- **First-In, First-Out (FIFO) or Randomized queuing**: Users receive a cryptographically signed queue pass token with an estimated wait time and position
- **Controlled admission throttle**: Origin servers set a maximum throughput rate (e.g., 500 users/minute); the waiting room admits only that number of authenticated queue tokens into the checkout flow
- **Database protection**: Completely eliminates database connection exhaustion, row locking contention, and cascading service outages during traffic spikes

### When to Use
- Flash sales, Black Friday e-commerce events, and concert ticket sales (Ticketmaster, Shopify)
- Government portals handling sudden massive public enrollment deadlines
- Vaccine appointment booking and high-demand product releases

### When NOT to Use
- Standard steady-state web applications where autoscaling compute resources handle organic demand
- Essential financial trading systems where placing user orders in artificial queues violates market fairness regulations

### Also see
- [Load Shedding](#load-shedding) · [Rate Limiting](api-design.md#rate-limiting) · [Cascading Failure](#cascading-failure) · [Flash Sale](architecture-patterns.md#flash-sale)


