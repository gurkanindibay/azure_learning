---
type: System Design
title: "System Design Interview Roadmap: Key Takeaways"
description: "**Trap**: Skipping a phase. Each phase feeds the next — skip requirements and your design has no foundation; skip math and you can't justify decisions; skip trade-offs and you appear junior."
timestamp: 2026-06-14T00:00:00Z
---

# 15. System Design Interview Roadmap: Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)  
> **Source**: [How to Structure Any System Design Interview in 45 Minutes](../../../articles/medium/design-system-interviews.md) — by Kunal Sinha (Dec 2025)  
> **Purpose**: Extract a repeatable 7-phase interview framework with specific scripts, traps, and trade-off patterns that distinguish senior candidates.

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`sdi-01`](#sdi-01-the-7-phase-interview-rhythm) | The 7-Phase Interview Rhythm | Phases build on each other; skip one and gaps appear |
| [`sdi-02`](#sdi-02-actors-before-features) | Actors Before Features | List ALL actors (admin, external systems) before defining features |
| [`sdi-03`](#sdi-03-p0-flows--syncasync-decision--failure-paths) | P0 Flows + Sync/Async + Failure Paths | 2-3 critical flows, sync vs async choice, failure anticipation |
| [`sdi-04`](#sdi-04-nfr-quantification) | NFR Quantification | Pick specific numbers; don't claim "HA + strong" without partition behavior |
| [`sdi-05`](#sdi-05-back-of-the-envelope-math) | Back-of-the-Envelope Math | QPS ≈ daily/100K, peak = 3-5× avg, 80/20 cache rule |
| [`sdi-06`](#sdi-06-id-strategy--soft-deletes) | ID Strategy & Soft Deletes | UUIDs externally, auto-increment internally; soft delete by default |
| [`sdi-07`](#sdi-07-api-design-checklist) | API Design Checklist | Version in path, Idempotency-Key, cursor pagination, structured errors |
| [`sdi-08`](#sdi-08-api-gateway-as-first-line-of-defense) | API Gateway as First Line of Defense | Auth, rate limiting, request ID generation — not just a passthrough |
| [`sdi-09`](#sdi-09-async-path-strategy-db-first-vs-queue-first) | Async Path Strategy | DB First (Transactional Outbox) vs Queue First — traceability vs throughput |
| [`sdi-10`](#sdi-10-quorum-vs-consensus) | Quorum vs Consensus | Quorum for regular ops; consensus only for critical coordination |
| [`sdi-11`](#sdi-11-sharding-key-selection) | Sharding Key Selection | Choose key that keeps primary access on one shard; explain why |
| [`sdi-12`](#sdi-12-idempotency-implementation) | Idempotency Implementation | DB unique constraint + `ON CONFLICT DO NOTHING`; never app-code-only |
| [`sdi-13`](#sdi-13-failure-handling--timeout-hierarchy) | Failure Handling & Timeout Hierarchy | Circuit breaker + backoff + DLQ; Client > Gateway > Service > DB |
| [`sdi-14`](#sdi-14-observability-minimum) | Observability Minimum | P50/P95/P99 latency, 5xx rates, trace IDs, alerting thresholds |
| [`sdi-15`](#sdi-15-senior-differentiator-trade-off-maturity) | Senior Differentiator: Trade-off Maturity | Acknowledge limitations, mention alternatives, identify next bottleneck |

---

## sdi-01: The 7-Phase Interview Rhythm

| | |
|:---|:---|
| **Problem** | Candidates get overwhelmed, linger in familiar territory, and run out of time before the deep dive where expertise shines. |
| **Root cause** | No structured mental model — candidates react to interviewer prompts instead of driving the conversation through a repeatable sequence. |

**Strategy — Follow this sequence; each phase builds on the previous:**

| # | Phase | Time | Deliverable |
|:---|:---|:---|:---|
| 1 | Requirements | ~5 min | Actors, P0 flows, failure paths, NFRs |
| 2 | Back-of-the-Envelope Math | ~2 min | QPS, storage, cache size estimates |
| 3 | Core Entities | ~3 min | 3-4 entities with IDs, FK, timestamps |
| 4 | API Design | ~5 min | Versioning, idempotency, pagination, errors |
| 5 | High-Level Design | 5-7 min | Entry point, async path, database choice |
| 6 | Deep Dive | ~15 min | Consistency, scalability, latency, failures, observability |
| 7 | Trade-offs | 2-3 min | Limitations, alternatives, next bottleneck |

**The meta-principle**:

> The goal isn't to memorize the template — it's to internalize the rhythm. By the third practice run, the structure becomes instinct.

**Trap**: Skipping a phase. Each phase feeds the next — skip requirements and your design has no foundation; skip math and you can't justify decisions; skip trade-offs and you appear junior.

> **Taxonomy**: §2.1 Application Architecture Patterns, §7.1 Reliability & Resilience

---

## sdi-02: Actors Before Features

| | |
|:---|:---|
| **Problem** | Candidates jump straight to features, designing only for the end user. |
| **Root cause** | Tunnel vision on the primary user persona; admins and external integrations often drive half the requirements. |

**Strategy — List all actors first, then derive features from their needs:**

| Actor | Typical Needs |
|:---|:---|
| End User | Core product experience |
| Admin | Dashboards, dispute resolution, configuration |
| Merchant/Partner | Integration, reporting, settlement |
| External System | Webhooks, polling, API consumption |

> **Script**: "Before diving into features, let me clarify the actors: end users, merchants, and an admin for disputes. Does that scope sound right?"

**Trap**: Only designing for the end user. When the interviewer asks "how does admin handle disputes?" you'll have nothing.

> **Related**: [`db-01`](databases/query-performance.md) (UUID indexing), [`tx-01`](concurrency-transactions/concurrency-transactions.md) (double-booking)

---

## sdi-03: P0 Flows + Sync/Async Decision + Failure Paths

| | |
|:---|:---|
| **Problem** | Candidates describe every possible flow or force synchronous processing on async-appropriate tasks. |
| **Root cause** | No prioritization framework; no instinct to classify flows by whether the user waits. |

**Strategy — Three-step flow definition:**

**Step 1: Pick 2-3 P0 flows that drive the architecture.**

**Step 2: For each flow, decide synchronous vs asynchronous:**

| If... | Then... | HTTP Status |
|:---|:---|:---|
| User waits for result | Synchronous | `201 Created` |
| Processing happens later | Asynchronous | `202 Accepted` + notification |

**Step 3: For each P0 flow, answer "What happens when X fails?"**

| Failure | Response |
|:---|:---|
| Payment gateway timeout | Retry with exponential backoff; after 3 failures, notify user + log for manual review |
| Downstream service unavailable | Circuit breaker → `503`; queue for later processing |
| Database write fails | Rollback transaction; return `500` with `request_id` |

> **Script**: "The two critical flows are: user initiates payment (sync, returns `201`) and merchant views settlement report (async, returns `202` and emails when ready). If the payment gateway times out, we'll retry with exponential backoff. After 3 failures, we notify the user and log for manual review."

**Trap**: Only designing for success. Interviewers love asking "what if this fails?" — beat them to it.

> **Related**: [`broker-01`](messaging/message-brokers-async.md) (broker selection), [`resilience-01`](resilience/resilience-patterns.md) (retry storms)

---

## sdi-04: NFR Quantification

| | |
|:---|:---|
| **Problem** | Candidates give vague NFRs ("it should be fast and reliable") that can't justify any architectural decision. |
| **Root cause** | Treating NFRs as checkboxes rather than decision-driving constraints. |

**Strategy — Pick ONE specific value from each category:**

| Category | Options | How to Choose |
|:---|:---|:---|
| Latency | `< 200ms` / `< 1s` / `< 10s` | User-facing interactive → 200ms; dashboard → 1s; report → 10s |
| Consistency | Strong / Read-after-write / Eventual | Money → strong; social media → eventual |
| Correctness | Exactly-once / At-least-once | Payments → exactly-once; analytics → at-least-once |

> **Script**: "For a payment system, I'd target P99 latency under 500ms, strong consistency to prevent double-charges, and exactly-once semantics via idempotency keys."

**Caveat**: Strong consistency requires leader-based replication or quorum writes, which limits write scalability. Acknowledge the cost.

**Trap**: Saying "highly available AND strongly consistent" without clarifying behavior during network partitions. During a partition, which do you sacrifice?

> **Related**: [`sdi-10`](#sdi-10-quorum-vs-consensus) (quorum vs consensus), [`sdi-12`](#sdi-12-idempotency-implementation) (idempotency)

---

## sdi-05: Back-of-the-Envelope Math

| | |
|:---|:---|
| **Problem** | Candidates skip math entirely or calculate with unnecessary precision. |
| **Root cause** | Fear of getting numbers wrong; not knowing the 100,000 shortcut. |

**Strategy — Three estimates, rough order-of-magnitude only:**

| Estimate | Formula | Why It Matters |
|:---|:---|:---|
| **QPS** | `Daily requests ÷ 100,000` | Determines if single DB suffices or you need sharding |
| **Storage (5yr)** | `(Writes/sec × Record size) × 86,400 × 365 × 5` | Determines if you need archival or distributed storage |
| **Cache size** | 20% of hot data (80/20 rule) | Determines if single Redis instance suffices or cluster needed |

| Rule of Thumb | Value |
|:---|:---|
| Peak traffic multiplier | 3–5× average |
| Sharding threshold | `> 10k` write QPS |
| Precision shortcut | Use 100,000, not 86,400 |

> **Script**: "50 million daily payments ÷ 100,000 ≈ 500 QPS average. At 3× peak: 1,500 QPS. That's comfortably handled by a single primary database."

**Trap**: Calculating 86,400 seconds precisely. Use 100,000. Precision matters less than identifying the order of magnitude bottleneck.

> **Related**: [`sdi-11`](#sdi-11-sharding-key-selection) (sharding), [`cache-01`](caching/caching-architecture.md) (cache sizing)

---

## sdi-06: ID Strategy & Soft Deletes

| | |
|:---|:---|
| **Problem** | Exposing auto-increment integers as public IDs leaks business volume and enables enumeration attacks. Using UUIDv4 as primary key destroys B-tree index performance. |
| **Root cause** | Not distinguishing between internal storage concerns and external security concerns. |

**Strategy — Split internal and external IDs:**

| Layer | ID Type | Rationale |
|:---|:---|:---|
| **Internal PK** | Auto-increment `BIGINT` | B-tree friendly — sequential inserts, no fragmentation |
| **External ID** | UUID (separate indexed column) | No information leakage; safe to expose in APIs |
| **Alternative** | UUIDv7 / ULID / Snowflake | Time-sortable if you need sortable external IDs |

**Deletion strategy**: Always soft delete (`deleted_at` timestamp) for compliance (GDPR, financial audit trails). Hard deletes only after legally required retention period.

> **Script**: "Internally we use auto-increment for the primary key since it's B-tree friendly. The UUID is a secondary indexed column for external lookups."

**Trap**: Using auto-increment integers as public identifiers. Competitors can estimate your transaction volume from `order_id: 1042` vs `order_id: 98723`.

> **Related**: [`db-01`](databases/query-performance.md) (UUID indexing), [`db-06`](databases/query-performance.md) (DB migration)

---

## sdi-07: API Design Checklist

| | |
|:---|:---|
| **Problem** | Candidates design APIs without versioning, idempotency, proper pagination, or structured errors — all of which cause production incidents. |
| **Root cause** | Focusing only on happy-path resource design; neglecting operability. |

**Strategy — Four non-negotiable API design decisions:**

| Decision | Implementation | Why |
|:---|:---|:---|
| **Versioning** | `/api/v1/resource` in path | Enables breaking changes without breaking clients |
| **Idempotency** | `Idempotency-Key` header; store + return cached response | Makes retries safe for all write operations |
| **Pagination** | Cursor-based (`next_cursor` Base64 token) | Stable results even when new data is inserted between pages |
| **Errors** | Structured: `{code, message, request_id}` | Debuggable in production; support can trace by `request_id` |

> **Script**: "All endpoints are versioned — `/api/v1/payments`. Merchants include an `Idempotency-Key` header. We return a `next_cursor` token for pagination. Every error includes a `request_id` for tracing."

**Trap**: Using offset-based pagination — inserts between requests cause items to be skipped or duplicated. Missing `request_id` in errors — debugging production becomes impossible.

> **Related**: [`api-01`](api-network/api-network-design.md) (versioning), [`api-02`](api-network/api-network-design.md) (rate limiting), [`tx-04`](concurrency-transactions/concurrency-transactions.md) (idempotency)

---

## sdi-08: API Gateway as First Line of Defense

| | |
|:---|:---|
| **Problem** | Candidates draw one box labeled "Server" or treat the API Gateway as a transparent proxy. |
| **Root cause** | Not understanding that the gateway is the first line of defense — security, rate control, and observability start here. |

**Strategy — The gateway does 5 things before any request hits a service:**

```
DNS → Load Balancer → API Gateway → Services
                         │
                         ├─ 1. Authentication (JWT validation)
                         ├─ 2. Rate Limiting (per user/merchant)
                         ├─ 3. Request ID Generation (global trace ID)
                         ├─ 4. Request Validation (schema check)
                         └─ 5. Routing (to downstream service)
```

| Responsibility | What Happens |
|:---|:---|
| Authentication | Reject unauthenticated requests before they consume service resources |
| Rate Limiting | Enforce per-user or per-merchant limits (e.g., 1000 req/min) |
| Request ID Generation | Attach globally unique `request_id` to every request for distributed tracing |
| Request Validation | Basic schema validation — reject malformed requests early |
| Routing | Direct traffic to the appropriate downstream service |

> **Script**: "The gateway handles three things: it validates the JWT and rejects unauthenticated requests, enforces rate limits per merchant, and generates a global `request_id` that propagates through all downstream services."

**Trap**: Drawing one big box labeled "Server." The gateway is not a passthrough — it's your first line of defense.

> **Related**: [`api-02`](api-network/api-network-design.md) (rate limiting), [`resilience-05`](resilience/resilience-patterns.md) (gateway bottleneck)

---

## sdi-09: Async Path Strategy (DB First vs Queue First)

| | |
|:---|:---|
| **Problem** | Candidates either make everything synchronous or write everything directly to a queue, losing traceability. |
| **Root cause** | Not distinguishing between flows that need immediate confirmation vs fire-and-forget. |

**Strategy — Choose based on traceability requirement:**

#### Option A: Database First (Transactional Outbox)

```
API → Database → Outbox Poller/CDC → Queue → Worker
```

| Characteristic | Behavior |
|:---|:---|
| Traceability | Request is immediately trackable (you can return an ID) |
| Queryability | User can query status right away |
| Bottleneck | DB can become a bottleneck at high scale (> 10k writes/sec) |

#### Option B: Queue First

```
API → Queue → Worker → Database
```

| Characteristic | Behavior |
|:---|:---|
| Throughput | Higher throughput, scales horizontally |
| Traceability | Request is "in flight" — not queryable until worker processes it |
| Risk | Message loss if queue isn't durable |

**Decision matrix:**

| If... | Use... | Example |
|:---|:---|:---|
| User needs immediate confirmation; scale < 10k writes/sec | **DB First** | Payment initiation |
| Fire-and-forget acceptable; scale is high | **Queue First** | Analytics events, activity logs, notifications |

> **Script**: "For payment initiation, I'd write to the database first using the transactional outbox pattern — the user needs an ID immediately. For activity logging, I'd write directly to Kafka since it's fire-and-forget."

**Trap**: Writing directly to Kafka for user-facing flows. The user asks "where's my payment?" and you have no record yet.

> **Related**: [`broker-01`](messaging/message-brokers-async.md) (broker selection), [`broker-05`](messaging/message-brokers-async.md) (stream processing), [`async-03`](stream-processing/async-concurrency-patterns.md) (post-commit dispatch)

---

## sdi-10: Quorum vs Consensus

| | |
|:---|:---|
| **Problem** | Candidates confuse quorum with consensus, using consensus for every write and killing throughput. |
| **Root cause** | Not understanding that these are fundamentally different mechanisms for different problems. |

**Strategy — Know the distinction:**

#### Quorum (`W + R > N`)

| Aspect | Detail |
|:---|:---|
| What it does | Ensures **overlap** between write and read replicas |
| Example | `W=2, R=2, N=3` — at least one node has the latest write |
| Used in | Cassandra, DynamoDB, Riak |
| Gives you | Tunable consistency, high availability, scalable writes |
| Trade-off | Potential conflicts in leaderless setups; needs conflict resolution |

#### Consensus (Raft, Paxos, Zab)

| Aspect | Detail |
|:---|:---|
| What it does | Every node must **agree** before proceeding |
| Used for | Leader election, distributed locks, critical state transitions |
| Gives you | True agreement — no conflicts |
| Trade-off | Higher latency, reduced availability during partitions |

**When to use which:**

| Mechanism | Use Case |
|:---|:---|
| **Quorum** | Regular read/write operations at scale. Acceptable for most data paths. |
| **Consensus** | Critical coordination only — leader election, distributed transactions, payment state machine transitions. |

> **Script**: "For regular reads and writes, quorum is sufficient — we configure `W=2, R=2, N=3`. But for payment state transitions, we use a Raft-based coordinator. Consensus adds latency, but for money movement, correctness beats speed."

**Trap**: Using consensus for every write kills throughput. Quorum ensures overlap; consensus ensures agreement. Reserve consensus for critical paths.

> **Related**: [`tx-02`](concurrency-transactions/concurrency-transactions.md) (isolation levels), [`tx-03`](concurrency-transactions/concurrency-transactions.md) (distributed locks)

---

## sdi-11: Sharding Key Selection

| | |
|:---|:---|
| **Problem** | Candidates hand-wave sharding without explaining the key choice — or choose keys that create hot spots. |
| **Root cause** | Not thinking through primary access patterns before selecting a sharding key. |

**Strategy — The sharding key must keep the primary access pattern on a single shard:**

| If primary access is... | Shard by... | Why |
|:---|:---|:---|
| Merchant dashboard | `merchant_id` | All of one merchant's data co-located; no cross-shard queries |
| User profile | `user_id` | All of one user's data on one shard |
| Time-range analytics | `(tenant_id, date)` | Composite key for multi-tenant time-series |

> **Script**: "If we grow beyond 10k writes per second, we'll shard by `merchant_id`. This keeps each merchant's data co-located and avoids cross-shard queries for their dashboards."

**Trap**: Hand-waving sharding without explaining the key. Bad keys create hot spots (e.g., sharding by `date` when all queries hit today's data).

**Sharding trigger**: `> 10k` write QPS.

> **Related**: [`db-05`](databases/query-performance.md) (hot partitions), [`db-06`](databases/query-performance.md) (DB migration at scale)

---

## sdi-12: Idempotency Implementation

| | |
|:---|:---|
| **Problem** | Candidates implement idempotency in application code without database constraints — race conditions cause double-charges. |
| **Root cause** | Check-then-act in application code is not atomic; two concurrent requests can both pass the check. |

**Strategy — Idempotency MUST be enforced at the database level:**

```
┌─────────────────────────────────────────────────────────┐
│  Client sends Idempotency-Key: abc123                   │
│       ↓                                                 │
│  INSERT INTO payments (idempotency_key, ...)            │
│  VALUES ('abc123', ...)                                 │
│  ON CONFLICT (idempotency_key) DO NOTHING              │
│  RETURNING *                                            │
│       ↓                                                 │
│  If row returned → new request (process normally)       │
│  If no row → duplicate (return cached response)        │
└─────────────────────────────────────────────────────────┘
```

**Fallback when clients can't generate idempotency keys:**

| Mechanism | How It Works |
|:---|:---|
| **Natural keys** | Deduplicate on business attributes within a time window |
| **Unique constraints** | DB-level enforcement (e.g., one pending payment per user-merchant pair) |
| **Request fingerprinting** | Hash the request body and deduplicate on the hash |

> **Script**: "The `idempotency_key` is a unique constraint. We `INSERT` with `ON CONFLICT DO NOTHING`, then return the existing record. This is atomic — no race conditions. Belt and suspenders."

**Trap**: Implementing idempotency in application code without database constraints. Race conditions will bite you.

> **Related**: [`tx-04`](concurrency-transactions/concurrency-transactions.md) (idempotency), [`tx-01`](concurrency-transactions/concurrency-transactions.md) (double-booking)

---

## sdi-13: Failure Handling & Timeout Hierarchy

| | |
|:---|:---|
| **Problem** | Candidates either ignore failures or implement unbounded retries that DDoS their own system. |
| **Root cause** | No systematic failure handling strategy; no understanding of cascading timeouts. |

**Strategy — Three patterns, one hierarchy:**

#### The Failure Handling Triad

| Pattern | Mechanism | When |
|:---|:---|:---|
| **Circuit breaker** | Stop calling failing services after N failures in T seconds; return fallback | Downstream service is degraded |
| **Retry with backoff** | `1s → 2s → 4s` with jitter; max 3 attempts | Transient failures (network blip, timeout) |
| **Dead letter queue** | Capture failed jobs for inspection and manual replay | Non-transient failures (bad data, logic bug) |

#### Timeout Hierarchy (cascading)

```
Client (10s) > Gateway (8s) > Service (5s) > Database (2s)
```

Each layer's timeout must be **shorter** than the layer above it. This ensures the client gets a clean timeout error rather than a hanging request.

> **Script**: "If the payment gateway fails 5 times in 10 seconds, we trip the circuit breaker and return a `503` for 30 seconds. Failed async jobs go to a DLQ. Timeouts cascade: client 10s, gateway 8s, service 5s, database 2s."

**Trap**: Unbounded retries can DDoS your own system. Setting DB timeout higher than client timeout wastes database resources on abandoned requests.

> **Related**: [`resilience-02`](resilience/resilience-patterns.md) (circuit breaker), [`resilience-04`](resilience/resilience-patterns.md) (timeouts & retries), [`resilience-06`](resilience/resilience-patterns.md) (resilience stack)

---

## sdi-14: Observability Minimum

| | |
|:---|:---|
| **Problem** | Candidates treat observability as optional or an afterthought. |
| **Root cause** | In production, you can't fix what you can't see. Observability is architecture, not ops. |

**Strategy — Three pillars, mentioned during design, not after:**

| Pillar | What to Track | Tool Example |
|:---|:---|:---|
| **Metrics** | P50/P95/P99 latency, error rate (5xx %), throughput | Datadog, Prometheus + Grafana |
| **Distributed Tracing** | `request_id` propagated through all services | Jaeger, Zipkin, Datadog APM |
| **Alerting** | Page on-call if error rate > 1% for 5 minutes | PagerDuty, Opsgenie |

> **Script**: "We'll track P50/P95/P99 latency and 5xx rates in Datadog. Every request gets a trace ID that propagates through all services. We page on-call if error rate exceeds 1% for 5 minutes."

**Trap**: Treating observability as optional or "Phase 2." It's not — you can't debug what you can't measure.

> **Related**: Azure Monitor, Application Insights; **Taxonomy**: §7.4 Observability & Monitoring

---

## sdi-15: Senior Differentiator — Trade-off Maturity

| | |
|:---|:---|
| **Problem** | Junior candidates present their design as the only correct option. Senior candidates acknowledge limitations before the interviewer finds them. |
| **Root cause** | Defensiveness — treating gaps as failures rather than conscious trade-offs. |

**Strategy — Three proactive moves that signal seniority:**

| Move | What to Say | Why It Works |
|:---|:---|:---|
| **Acknowledge limitations** | "We haven't covered multi-region failover. I'd recommend active-passive with async replication and a 30-second RPO." | Shows you know what you didn't cover — and you know how you'd solve it |
| **Mention alternatives** | "We could use event sourcing instead of a traditional database. It would give us a perfect audit trail, but adds complexity we don't need at this scale." | Proves you considered other approaches and made a conscious choice |
| **Identify next bottleneck** | "At 100× scale, the single Redis becomes a bottleneck. We'd move to Redis Cluster." | Shows you think about evolution, not just v1 |

> **Script**: "We haven't covered multi-region failover. For a payment system, I'd recommend active-passive with async replication and a 30-second RPO. Happy to go deeper if that's useful."

**Trap**: Being defensive. Don't wait for the interviewer to find holes — call them out yourself. Good architects know every design is a set of trade-offs.

> **Related**: All sections above — this is the meta-skill that ties the framework together.

---

## Quick Reference

| Rule | Value |
|:---|:---|
| QPS shortcut | Daily total ÷ 100,000 |
| Peak traffic multiplier | 3–5× average |
| Cache sizing | 20% of hot data (80/20 rule) |
| Latency target (user-facing) | `< 200ms` P99 |
| Sharding trigger | `> 10k` write QPS |
| Retry pattern | Exponential backoff with jitter |
| Deletion default | Soft delete with `deleted_at` |
| ID strategy | UUIDs externally, auto-increment internally |
| Timeout cascade | `Client > Gateway > Service > Database` |
| Idempotency enforcement | DB unique constraint, not app code |
| Consensus use | Critical coordination only — not regular writes |

---

## Cross-Reference Map

| This Takeaway | Related Sections |
|:---|:---|
| `sdi-04` NFR Quantification | → `sdi-10` Quorum vs Consensus |
| `sdi-06` ID Strategy | → [`db-01`](databases/query-performance.md) UUID indexing |
| `sdi-07` API Design | → [`api-01`](api-network/api-network-design.md) versioning, [`tx-04`](concurrency-transactions/concurrency-transactions.md) idempotency |
| `sdi-09` Async Path | → [`broker-01`](messaging/message-brokers-async.md) broker selection, [`async-03`](stream-processing/async-concurrency-patterns.md) post-commit dispatch |
| `sdi-10` Quorum vs Consensus | → [`tx-02`](concurrency-transactions/concurrency-transactions.md) isolation levels |
| `sdi-12` Idempotency | → [`tx-04`](concurrency-transactions/concurrency-transactions.md) idempotency, [`tx-01`](concurrency-transactions/concurrency-transactions.md) double-booking |
| `sdi-13` Failure Handling | → [`resilience-02`](resilience/resilience-patterns.md) circuit breaker, [`resilience-04`](resilience/resilience-patterns.md) timeouts |
