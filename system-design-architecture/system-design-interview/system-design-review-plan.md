---
type: System Design
title: "System Design Interview Review Plan — Phase-by-Phase Checklist"
description: "A parallel 29-check review checklist aligned to the 7-phase interview structure. Run each phase's checks before advancing — internalize until the checks become automatic during the real interview."
generated: { by: process:okf-migrate, at: 2026-07-05T00:00:00Z }
---

# System Design Interview Review Plan

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: Synthesized from the [7-Phase Interview Roadmap](interview-roadmap.md) (`sdi-01`–`sdi-15`), [Decision Frameworks](complete-system-design-interview-guide-2026-takeaways.md) (`sdi-35`–`sdi-42`), [Deep Dive Reference](interview-deep-dive.md) (`sdi-16`–`sdi-27`), and [Pragmatic Principles](pragmatic-takeaways.md) (`prag-01`–`prag-08`) — cross-referencing all existing system-design-interview takeaways into a single review checklist.
> **Purpose**: A parallel review thread you run alongside your design during practice. After completing each of the 7 interview phases, run that phase's checklist before advancing to the next. Over time, the checks become instinct — you'll catch gaps before the interviewer does.

---

## How to Use This Plan

1. **During practice**: Follow the [7-phase interview rhythm](interview-roadmap.md#sdi-01-the-7-phase-interview-rhythm) from `sdi-01`. After completing each phase, stop and run the checklist below for that phase. Do NOT advance until every check passes.
2. **During the interview**: Run the summary card at the top of each phase mentally. If you catch a gap, fix it before the interviewer asks.
3. **Memorization order**: Memorize the phase-level summary questions first (the bold one-liners). Then memorize the individual checks. The summary card at the bottom of this document is your flashcard.

> **Prerequisite reading**: [interview-roadmap.md](interview-roadmap.md) (`sdi-01`–`sdi-15`) — this review plan assumes you know the 7-phase structure and the decision frameworks it references.

---

## Contents

| ID | Phase | Checks |
|:---|:---|:---|
| [`sdi-43`–`sdi-46`](#phase-1-requirements--5-min) | Phase 1: Requirements | 4 checks |
| [`sdi-47`–`sdi-49`](#phase-2-back-of-the-envelope-math--2-min) | Phase 2: Math | 3 checks |
| [`sdi-50`–`sdi-52`](#phase-3-core-entities--3-min) | Phase 3: Entities | 3 checks |
| [`sdi-53`–`sdi-57`](#phase-4-api-design--5-min) | Phase 4: API Design | 5 checks |
| [`sdi-58`–`sdi-62`](#phase-5-high-level-design-57-min) | Phase 5: High-Level Design | 5 checks |
| [`sdi-63`–`sdi-68`](#phase-6-deep-dive--15-min) | Phase 6: Deep Dive | 6 checks |
| [`sdi-69`–`sdi-71`](#phase-7-trade-offs-23-min) | Phase 7: Trade-offs | 3 checks |

---

## Phase 1: Requirements (~5 min)

**Phase goal**: Actors, P0 flows, failure paths, NFRs.  
**Summary check**: *"Did I name every actor, attach numbers to NFRs, and confirm scope with the interviewer?"*

---

### sdi-43: All Actors Named

| | |
|:---|:---|
| **Problem** | Candidates design only for the end user. When the interviewer asks "how does admin handle disputes?" there's nothing to show. |
| **Root cause** | Tunnel vision on the primary persona — admins, partners, and external systems drive half the real requirements. |

**Check**: Before moving on, verify your actor list includes:

| Actor | Did I cover them? |
|:---|:---|
| End User | Core product experience |
| Admin / Operator | Dashboards, dispute resolution, configuration, audit logs |
| Partner / Merchant / Third-party | Integration, reporting, settlement, webhooks |
| External System | Polling consumers, upstream data sources, downstream sinks |

> **Script**: "Before diving into features, let me clarify the actors: end users, admins for disputes, and an external payment partner. Does that scope sound right?"

> **Related**: [`sdi-02`](interview-roadmap.md#sdi-02-actors-before-features) (Actors Before Features)

---

### sdi-44: P0 Flows Prioritized and Classified

| | |
|:---|:---|
| **Problem** | Candidates describe every possible flow or force synchronous processing on tasks that should be async. |
| **Root cause** | No prioritization framework; no instinct to classify flows by whether the user waits for completion. |

**Check**: For each P0 flow, answer:

- Is the user waiting for this to complete? → **Sync** (request-response)
- Can the user continue while this completes? → **Async** (queue + eventual consistency)

Pick exactly 2–3 P0 flows. If you listed more than 3, you're not prioritizing — the architecture is driven by the critical path.

> **Related**: [`sdi-03`](interview-roadmap.md#sdi-03-p0-flows--syncasync-decision--failure-paths) (P0 Flows + Sync/Async Decision)

---

### sdi-45: NFRs Quantified with Numbers

| | |
|:---|:---|
| **Problem** | Candidates state NFRs as adjectives: "highly available," "scalable," "secure." These are meaningless for architecture decisions. |
| **Root cause** | NFR quantification is uncomfortable — it forces you to commit to numbers that can be challenged. But unchallenged adjectives are worse. |

**Check**: Every NFR must have a number:

| NFR | Bad (Adjective) | Good (Quantified) |
|:---|:---|:---|
| Availability | "Highly available" | "99.9% uptime, partition-tolerant (AP)" |
| Latency | "Fast" | "P95 < 200ms for reads, P99 < 1s for writes" |
| Throughput | "Scalable" | "10K writes/sec, 100K reads/sec at peak" |
| Consistency | "Consistent" | "Strong consistency for payments, eventual for feed" |
| Durability | "Durable" | "Zero data loss on acknowledged writes" |

> **Related**: [`sdi-04`](interview-roadmap.md#sdi-04-nfr-quantification) (NFR Quantification), [`sdi-05`](interview-roadmap.md#sdi-05-back-of-the-envelope-math) (Back-of-the-Envelope Math)

---

### sdi-46: Scope Confirmed

| | |
|:---|:---|
| **Problem** | Candidates spend 20 minutes designing a feature the interviewer didn't ask for. |
| **Root cause** | Assumption that "I know what this system needs" without a 5-second confirmation question. |

**Check**: Did you explicitly ask: *"Does this scope sound right? Are there any actors or flows I'm missing?"*

This is the single highest-ROI question in the interview. It aligns expectations and shows collaboration.

> **Related**: [`sdi-01`](interview-roadmap.md#sdi-01-the-7-phase-interview-rhythm) (The 7-Phase Interview Rhythm)

---

## Phase 2: Back-of-the-Envelope Math (~2 min)

**Phase goal**: QPS, storage, cache size estimates.  
**Summary check**: *"Did I use the right heuristics, account for overhead, and let math eliminate impossible options?"*

---

### sdi-47: Right Estimation Heuristics

| | |
|:---|:---|
| **Problem** | Wrong estimation shortcuts produce numbers that justify wrong architecture decisions. |
| **Root cause** | Memorizing formulas without understanding the assumptions behind them. |

**Check**: Did you use these heuristics correctly?

| Metric | Heuristic |
|:---|:---|
| QPS (avg) | Daily active users × avg requests per user ÷ 86,400 ≈ DAU / 100K |
| Peak QPS | 3–5× average QPS |
| Storage (raw) | Records/day × size per record × retention days |
| Cache size | Hot data (80/20 rule): 20% of daily active data × replication factor |
| Bandwidth | Peak QPS × average response size |

If your numbers don't roughly match these shortcuts, recheck your assumptions.

> **Related**: [`sdi-05`](interview-roadmap.md#sdi-05-back-of-the-envelope-math) (Back-of-the-Envelope Math)

---

### sdi-48: Overhead Accounted For

| | |
|:---|:---|
| **Problem** | Raw data size estimates miss replication, indexes, metadata, and log overhead — actual storage can be 3–5× the naive estimate. |
| **Root cause** | Thinking of storage as "just the data" rather than "data + everything needed to serve it." |

**Check**: Multiply your raw storage estimate by:

| Factor | Typical Multiplier |
|:---|:---|
| Replication (3× is standard) | 3× |
| Indexes (B-tree, full-text, secondary) | 1.5–2× |
| Write-ahead logs, binlogs, metadata | 1.2–1.5× |
| **Total overhead** | **5–10× raw data** |

> **Related**: [`sdi-19`](interview-deep-dive.md#sdi-19) (CAP Theorem and replication)

---

### sdi-49: Math Eliminates Options

| | |
|:---|:---|
| **Problem** | Candidates design around impossible choices — e.g., "single PostgreSQL instance at 100K writes/sec" — because they didn't let math rule anything out first. |
| **Root cause** | Designing from intuition rather than constraints. Math should eliminate architectures before you invest time in them. |

**Check**: Given your QPS and storage estimates:

| If your numbers say... | Then eliminate... |
|:---|:---|
| > 10K writes/sec on a single DB | Single-instance relational DB — you need sharding or a distributed DB |
| > 1 TB hot data | In-memory caching for everything — you need tiered storage |
| < 100 QPS peak | Microservices, Kafka, multi-region — you're over-engineering (see `prag-01`) |

> **Related**: [`prag-01`](pragmatic-takeaways.md#prag-01-start-with-user-metrics-not-architecture-diagrams) (User Metrics First), [`sdi-35`](complete-system-design-interview-guide-2026-takeaways.md#sdi-35-horizontal-vs-vertical-scaling-decision-framework) (Scaling Decision)

---

## Phase 3: Core Entities (~3 min)

**Phase goal**: 3–4 entities with keys, relationships, and timestamps.  
**Summary check**: *"UUIDs externally, auto-increment internally, soft deletes, explicit cardinalities?"*

---

### sdi-50: ID Strategy — UUID External, Auto-Increment Internal

| | |
|:---|:---|
| **Problem** | Using auto-increment IDs in APIs leaks business metrics (competitors can estimate your growth by incrementing IDs) and creates hot spots in distributed databases. |
| **Root cause** | Auto-increment is the database default; developers don't question it until it causes problems at scale. |

**Check**: For every entity:

| Layer | ID Type | Why |
|:---|:---|:---|
| External (API) | UUID v4 or ULID | Non-enumerable, no coordination, no hot spots |
| Internal (DB PK) | Auto-increment BIGINT | Compact, fast B-tree indexing, efficient JOINs |

> **Related**: [`sdi-06`](interview-roadmap.md#sdi-06-id-strategy--soft-deletes) (ID Strategy & Soft Deletes), [`db-01`](../databases/query-performance.md#db-01) (UUID indexing)

---

### sdi-51: Audit Columns and Soft Deletes

| | |
|:---|:---|
| **Problem** | Adding audit columns and soft-delete support after launch requires a migration across all tables — and you'll always need them eventually. |
| **Root cause** | "We'll add it later" — but later requires downtime and data migration. |

**Check**: Every entity must include:

| Column | Type | Purpose |
|:---|:---|:---|
| `id` | UUID (external) / BIGINT (internal) | Primary identifier |
| `created_at` | TIMESTAMP | Audit trail, debugging, partitioning key |
| `updated_at` | TIMESTAMP | Change detection, cache invalidation |
| `deleted_at` | TIMESTAMP NULL | Soft delete — filter `WHERE deleted_at IS NULL` in every query |

> **Related**: [`sdi-06`](interview-roadmap.md#sdi-06-id-strategy--soft-deletes) (ID Strategy & Soft Deletes)

---

### sdi-52: Relationship Cardinalities Explicit

| | |
|:---|:---|
| **Problem** | Vague relationships ("a user has orders") lead to wrong DB choices — you pick a document DB for a highly relational workload or vice versa. |
| **Root cause** | Skipping cardinality analysis because "I'll figure it out during deep dive" — but the DB choice happens in Phase 5. |

**Check**: For every relationship, state:

| Question | Example |
|:---|:---|
| Cardinality | "One user → many orders (1:N)" |
| Access pattern | "Always query orders by user_id; rarely cross-user" |
| Mutation pattern | "Orders are append-only after creation; status updates are single-field" |

If you have many M:N relationships with JOIN-heavy queries, you need a relational DB. If most access is by a single aggregate root with no cross-entity queries, a document DB is viable.

> **Related**: [`sdi-11`](interview-roadmap.md#sdi-11-sharding-key-selection) (Sharding Key Selection), [`sdi-58`](#sdi-58-database-choice-justified) (DB Choice Justified)

---

## Phase 4: API Design (~5 min)

**Phase goal**: Endpoints with versioning, idempotency, pagination, and structured errors.  
**Summary check**: *"Versioned? Idempotent? Cursor-paginated? Structured errors? Gateway as defense?"*

---

### sdi-53: Version in URL Path

| | |
|:---|:---|
| **Problem** | Header-based versioning hides breaking changes — clients don't know they're on a deprecated version until something breaks. |
| **Root cause** | "Content-Type versioning is more RESTful" — but REST purity trades off observability. |

**Check**: API version is in the URL path:

```
✅  GET /api/v1/orders
❌  GET /api/orders  (with Accept: application/vnd.api+json;version=1)
```

Path versioning is explicit, cacheable by CDNs, and visible in logs and analytics.

> **Related**: [`sdi-07`](interview-roadmap.md#sdi-07-api-design-checklist) (API Design Checklist)

---

### sdi-54: Idempotency on Every Mutation

| | |
|:---|:---|
| **Problem** | Network retries + no idempotency = double charges, duplicate records, inconsistent state. |
| **Root cause** | Assuming "the network is reliable" — it isn't. Every mutation endpoint will be retried. |

**Check**: Every POST, PUT, PATCH, and DELETE accepts:

```
Idempotency-Key: <client-generated-uuid>
```

Backend enforcement: store `(idempotency_key, user_id)` in a database with a unique constraint. On conflict, return the stored response — don't re-execute.

> **Related**: [`sdi-12`](interview-roadmap.md#sdi-12-idempotency-implementation) (Idempotency Implementation), [`sdi-39`](complete-system-design-interview-guide-2026-takeaways.md#sdi-39-effectively-exactly-once-processing) (Exactly-Once Processing)

---

### sdi-55: Cursor Pagination, Not Offset

| | |
|:---|:---|
| **Problem** | Offset pagination (`LIMIT 20 OFFSET 40`) produces duplicates and missing items when rows are inserted or deleted between page requests. |
| **Root cause** | Offset is intuitive — "skip the first N" — but the list changes between requests. |

**Check**: List endpoints use cursor-based pagination:

```
GET /api/v1/orders?cursor=eyJpZCI6MTIzfQ==&limit=20
```

The cursor is an opaque, base64-encoded reference to the last item on the previous page — typically the item's `id` or `created_at` timestamp. Cursor pagination is stable under concurrent writes.

> **Related**: [`sdi-07`](interview-roadmap.md#sdi-07-api-design-checklist) (API Design Checklist)

---

### sdi-56: Structured Error Responses

| | |
|:---|:---|
| **Problem** | Inconsistent error formats across endpoints make debugging a nightmare — one endpoint returns `{"error": "bad request"}`, another returns `{"message": "invalid"}`. |
| **Root cause** | Errors are treated as an afterthought; the happy path gets all the design attention. |

**Check**: Every error response follows a consistent structure:

```json
{
  "error": {
    "code": "INSUFFICIENT_FUNDS",
    "message": "Account balance is below the required amount.",
    "request_id": "req_abc123",
    "trace_id": "trace_xyz789"
  }
}
```

Include `request_id` (generated at the gateway, `sdi-08`) and `trace_id` (propagated through all downstream services) in every response — not just errors.

> **Related**: [`sdi-14`](interview-roadmap.md#sdi-14-observability-minimum) (Observability Minimum), [`sdi-08`](interview-roadmap.md#sdi-08-api-gateway-as-first-line-of-defense) (API Gateway)

---

### sdi-57: Gateway as First Line of Defense

| | |
|:---|:---|
| **Problem** | Candidates treat the API gateway as a transparent proxy — missing its role as the security and resilience boundary. |
| **Root cause** | Gateways are taught as routing tools, not as defense-in-depth. |

**Check**: Your API gateway handles these before traffic reaches your services:

| Responsibility | What Happens at the Gateway |
|:---|:---|
| Authentication | Validate JWT/OAuth token; reject unauthenticated requests |
| Rate limiting | Enforce per-user / per-IP limits; return 429 |
| Request ID | Generate `X-Request-Id` header; inject into all downstream calls |
| Input validation | Reject malformed JSON, oversized payloads, invalid content types |
| TLS termination | Decrypt at the edge; internal traffic over mTLS or private network |

> **Related**: [`sdi-08`](interview-roadmap.md#sdi-08-api-gateway-as-first-line-of-defense) (API Gateway as First Line of Defense)

---

## Phase 5: High-Level Design (5–7 min)

**Phase goal**: Entry point, async path, database choice, caching, load balancing.  
**Summary check**: *"DB justified? Async strategy explicit? Cache pattern matched? Fan-out handled? Load balancer present?"*

---

### sdi-58: Database Choice Justified

| | |
|:---|:---|
| **Problem** | Candidates pick a database because it's trending, not because the workload demands it. "MongoDB because it scales" — without explaining why a relational DB wouldn't. |
| **Root cause** | Trend-driven architecture selection; no framework for matching DB to workload. |

**Check**: Your DB choice must be justified by workload, not trend:

| Workload Signal | DB Type |
|:---|:---|
| Structured data, JOINs, ACID transactions, strict schema | Relational (PostgreSQL, MySQL) |
| Document-oriented, schema-flexible, aggregate-root access | Document (MongoDB, Cosmos DB) |
| Key-value, simple lookups, extreme throughput | Key-Value (Redis, DynamoDB) |
| Time-series, append-heavy, range queries on time | Time-Series (InfluxDB, TimescaleDB) |
| Graph traversal, deep relationships | Graph (Neo4j, Amazon Neptune) |
| Full-text search, fuzzy matching | Search (Elasticsearch) |

Also state your CAP trade-off: CP (consistent under partition) or AP (available under partition). If you said "CA," you're wrong — CA doesn't exist in distributed systems (see `sdi-18`).

> **Related**: [`prag-08`](pragmatic-takeaways.md#prag-08-boring-architecture-wins) (Boring Architecture Wins), [`sdi-18`](interview-deep-dive.md#sdi-18) (CAP Theorem)

---

### sdi-59: Async Strategy — DB-First vs Queue-First

| | |
|:---|:---|
| **Problem** | Async boundaries are drawn without a clear strategy — "we'll use Kafka" without explaining whether the outbox pattern is needed or what happens when the queue is unavailable. |
| **Root cause** | "Queue" is treated as a magic async wand without understanding the two fundamental patterns. |

**Check**: For every async boundary, pick one and justify:

| Pattern | Mechanism | When |
|:---|:---|:---|
| **DB-First** (Transactional Outbox) | Write business data + outbox event in one DB transaction; separate process polls and publishes | Traceability matters; you need to prove the event was emitted for every state change |
| **Queue-First** | Publish directly to the message broker from application code | Throughput matters more than guaranteed emission; event loss is tolerable or detectable |

> **The rule**: When in doubt, choose DB-First. It's harder to implement but impossible to lose events. Queue-First is faster but can drop events on crash between DB commit and queue publish.

> **Related**: [`sdi-09`](interview-roadmap.md#sdi-09-async-path-strategy-db-first-vs-queue-first) (Async Path Strategy), [`sdi-39`](complete-system-design-interview-guide-2026-takeaways.md#sdi-39-effectively-exactly-once-processing) (Exactly-Once Processing)

---

### sdi-60: Cache Strategy Matched to Access Pattern

| | |
|:---|:---|
| **Problem** | Cache-aside is applied everywhere by default — even for write-heavy or consistency-sensitive paths where it's the wrong choice. |
| **Root cause** | Cache-aside is the only pattern taught in most tutorials. |

**Check**: For each cached data path, identify which pattern applies:

| Pattern | Mechanism | Best For | Risk |
|:---|:---|:---|:---|
| **Cache-Aside** | App checks cache → DB on miss → populate | Read-heavy, tolerant of stale data | Cache miss storm on cold start |
| **Write-Through** | Write to cache + DB simultaneously | Consistency-sensitive (inventory counts) | Higher write latency |
| **Write-Behind** | Write to cache → async flush to DB | Write-heavy, loss-tolerant (counters) | Data loss on cache failure |

Also specify your invalidation strategy: TTL (simplest, eventually consistent), explicit invalidation (complex, strongly consistent), or event-driven (real-time, requires pub/sub).

> **Related**: [`sdi-37`](complete-system-design-interview-guide-2026-takeaways.md#sdi-37-cache-strategy-selection-cache-aside-vs-write-through-vs-write-behind) (Cache Strategy Selection), [`cache-02`](../caching/redis-internals.md) (Cache Stampede)

---

### sdi-61: Fan-Out Strategy — Write, Read, or Hybrid

| | |
|:---|:---|
| **Problem** | Social feed and notification systems must fan out content to many consumers. Fan-out on write breaks for users with millions of followers; fan-out on read is slow for active users following many accounts. |
| **Root cause** | Treating all users as having the same follower/following distribution. |

**Check**: If your system fans out content to multiple consumers:

| User Type | Strategy | Why |
|:---|:---|:---|
| Regular users (< few thousand followers) | Fan-out on write | Pre-compute timelines; reads are instant |
| High-follower users (celebrities) | Fan-out on read | Pull their posts at read time; avoid millions of cache writes per post |

> **The hybrid answer**: Classify users at write time by follower count. Regular users get fan-out on write. Celebrity posts are pulled at read time. Merge both result sets.

> **Related**: [`sdi-38`](complete-system-design-interview-guide-2026-takeaways.md#sdi-38-fan-out-on-write-vs-fan-out-on-read) (Fan-out on Write vs Read)

---

### sdi-62: Load Balancer with Routing Strategy

| | |
|:---|:---|
| **Problem** | A load balancer is drawn as a box with no routing strategy — missing the distinction between round-robin, least-connections, and consistent hashing. |
| **Root cause** | "Load balancer" is treated as a solved problem rather than a design decision. |

**Check**: Your load balancer strategy includes:

| Decision | Options |
|:---|:---|
| **Algorithm** | Round-robin (stateless), least-connections (mixed workloads), consistent hashing (sticky sessions, cache affinity) |
| **Health checks** | Active (HTTP `/health` probes) + passive (circuit breaker on 5xx) |
| **SSL termination** | At the LB — internal traffic over private network |
| **Session affinity** | Only if strictly needed (e.g., WebSocket); otherwise stateless |

> **Related**: [`sdi-16`](interview-deep-dive.md#sdi-16) (Vertical vs Horizontal Scaling)

---

## Phase 6: Deep Dive (~15 min)

**Phase goal**: Consistency, scaling, latency, failures, observability.  
**Summary check**: *"Failures walked? Consistency stated? Idempotency end-to-end? Sharding key chosen? Observability defined? 10× check?"*

---

### sdi-63: Failure Modes Walked Through

| | |
|:---|:---|
| **Problem** | Candidates describe the happy path in detail but have nothing when asked "what happens if the database is down?" |
| **Root cause** | Failure analysis is deferred to "later" — but in a senior interview, failure handling IS the deep dive. |

**Check**: Walk through what happens when each component fails:

| Component Fails | What Happens? | Recovery? |
|:---|:---|:---|
| Database | Circuit breaker opens → degraded mode (read from cache, queue writes) | Reconnect + backoff; replay queued writes |
| Cache | Cache miss storm → DB under load → circuit breaker on DB | Gradual cache warm-up; rate-limit DB access |
| Message Queue | Events buffered in outbox table → published when queue recovers | Outbox pattern saves you here |
| External API | Timeout + retry with exponential backoff → DLQ after N failures | Alert on DLQ depth; manual or automated replay |

**Timeout hierarchy**: Client timeout > Gateway timeout > Service timeout > DB timeout. Each downstream timeout must be shorter than the caller's timeout.

> **Related**: [`sdi-13`](interview-roadmap.md#sdi-13-failure-handling--timeout-hierarchy) (Failure Handling & Timeout Hierarchy), [`resilience-05`](../resilience/) (Circuit Breaker)

---

### sdi-64: Consistency Model Stated Explicitly

| | |
|:---|:---|
| **Problem** | Candidates never state their consistency model — they assume "the database handles it" without acknowledging that different parts of the system need different guarantees. |
| **Root cause** | Consistency is treated as binary (consistent vs not) rather than a spectrum. |

**Check**: For each data path, state:

| Consistency Level | Example | Mechanism |
|:---|:---|:---|
| **Strong** | Payment confirmation must reflect the actual balance | Synchronous write to primary; read from primary |
| **Causal** | "If I see a comment, I should see the post it belongs to" | Vector clocks, causal ordering in message broker |
| **Eventual** | "My profile picture will update... eventually" | Async replication; TTL-based cache invalidation |
| **Read-your-writes** | "After I post, my own timeline shows it immediately" | Read from primary for the writing user's own data |

> **Related**: [`sdi-18`](interview-deep-dive.md#sdi-18) (CAP Theorem), [`sdi-10`](interview-roadmap.md#sdi-10-quorum-vs-consensus) (Quorum vs Consensus)

---

### sdi-65: Idempotency End-to-End

| | |
|:---|:---|
| **Problem** | Idempotency is mentioned as "we'll add an idempotency key" without explaining how it's enforced at the database level. |
| **Root cause** | App-code-only idempotency (check-and-set in application code) has a TOCTOU race condition between the check and the write. |

**Check**: Your idempotency implementation includes:

| Layer | Mechanism |
|:---|:---|
| Client | Generates `Idempotency-Key: <UUID>` per operation; retries with the same key |
| API | Validates key presence; passes to service layer |
| Service | Attempts INSERT into `idempotency_keys(key, user_id, response, created_at)` |
| Database | `UNIQUE(key, user_id)` constraint + `ON CONFLICT DO NOTHING` — the atomic guarantee |

If the INSERT succeeds, proceed with business logic and store the response. If it conflicts, return the stored response. The database unique constraint is the only way to make this atomic.

> **Related**: [`sdi-12`](interview-roadmap.md#sdi-12-idempotency-implementation) (Idempotency Implementation), [`tx-03`](../concurrency-transactions/concurrency-transactions.md) (Double-Booking Prevention)

---

### sdi-66: Sharding Key with Cross-Shard Awareness

| | |
|:---|:---|
| **Problem** | Candidates pick a sharding key that evenly distributes data but forces every query to scatter-gather across all shards. |
| **Root cause** | Optimizing for distribution uniformity without considering access patterns. |

**Check**: Your sharding key satisfies:

| Criterion | Why |
|:---|:---|
| Primary access stays on one shard | Avoid scatter-gather queries — they kill performance at scale |
| Even distribution (no hot shards) | A shard receiving 80% of traffic defeats the purpose |
| Suitable for the most frequent query pattern | If 90% of queries are `WHERE user_id = ?`, shard on `user_id` |

**Also state**: What happens when a query MUST cross shards? (Map-reduce pattern, secondary index, or accept the latency hit — but say which.)

> **Related**: [`sdi-11`](interview-roadmap.md#sdi-11-sharding-key-selection) (Sharding Key Selection), [`sdi-20`](interview-deep-dive.md#sdi-20) (Replication + Sharding)

---

### sdi-67: Observability Minimum Defined

| | |
|:---|:---|
| **Problem** | "We'll add monitoring" without specifying what, at what thresholds, with what alerts. |
| **Root cause** | Observability is treated as an ops concern, not a design concern — but unobservable systems can't be debugged. |

**Check**: Specify at minimum:

| Metric | Target | Alert Threshold |
|:---|:---|:---|
| P50 latency | — (baseline) | — |
| P95 latency | < 200ms (reads) | > 500ms for 5 minutes |
| P99 latency | < 1s (writes) | > 2s for 5 minutes |
| Error rate (5xx) | < 0.1% | > 1% for 5 minutes |
| Availability | 99.9% | < 99.5% in any 5-minute window |
| Queue depth / lag | — | > N messages or > T seconds of lag |
| Trace ID propagation | Every request | Missing trace ID = alert |

> **Related**: [`sdi-14`](interview-roadmap.md#sdi-14-observability-minimum) (Observability Minimum)

---

### sdi-68: 10× Scale Check

| | |
|:---|:---|
| **Problem** | Candidates design for hypothetical millions but miss that their design breaks at 10× current load — which is far more likely to happen soon. |
| **Root cause** | Optimizing for the distant future while ignoring the near future. |

**Check**: Ask: *"Will this design hold at 10× current load?"*

| If... | Then... |
|:---|:---|
| Yes, with no changes | Your design is appropriately scoped |
| Yes, with minor changes (read replicas, bigger instances) | Name those changes — that's your growth plan |
| No, it breaks completely | Your design is fragile — re-examine bottlenecks |

One order of magnitude, not three. Design for 10×, sketch for 100×, don't implement for 1000×.

> **Related**: [`sdi-24`](interview-deep-dive.md#sdi-24) (Optimizing for Scale You'll Never Reach), [`prag-06`](pragmatic-takeaways.md#prag-06-solve-todays-problems-not-tomorrows) (Solve Today's Problems)

---

## Phase 7: Trade-offs (2–3 min)

**Phase goal**: Limitations, alternatives, next bottleneck.  
**Summary check**: *"Limitation named? Alternative rejected? Next bottleneck identified?"*

---

### sdi-69: Explicit Limitation Acknowledged

| | |
|:---|:---|
| **Problem** | Candidates present their design as perfect — no weaknesses, no gaps. This is the #1 junior signal. |
| **Root cause** | Fear that admitting a weakness will count against you. The opposite is true — acknowledging trade-offs is the strongest senior signal. |

**Check**: Name at least one thing your design does NOT handle well:

| Example Limitation | Why It's Acceptable |
|:---|:---|
| "Cross-shard queries require scatter-gather and will be slow" | "90% of queries hit a single shard by user_id" |
| "Eventual consistency on the feed means a post might take 2s to appear" | "Users accept this for social feeds; payment flows use strong consistency" |
| "The write path has higher latency because of the outbox pattern" | "Traceability is more important than 50ms of extra latency for financial data" |

> **Related**: [`sdi-15`](interview-roadmap.md#sdi-15-senior-differentiator-trade-off-maturity) (Trade-off Maturity), [`sdi-21`](interview-deep-dive.md#sdi-21) (Design Tradeoffs)

---

### sdi-70: Alternative Considered and Rejected

| | |
|:---|:---|
| **Problem** | Presenting a single solution without showing that you evaluated alternatives makes it look like you picked the first thing that came to mind. |
| **Root cause** | Design is taught as "the right answer" rather than "the best choice among alternatives." |

**Check**: For every major decision, state: *"We could have done X, but we chose Y because [specific reason]."*

| Decision | Alternative | Why Rejected |
|:---|:---|:---|
| SQL vs NoSQL | MongoDB | Relational queries with JOINs across entities — document DB forces denormalization |
| Cache-aside vs Write-through | Write-through | Read-heavy workload tolerates eventual consistency; write-through adds latency we don't need |
| Monolith vs Microservices | Microservices | Single-team startup; monolith pain hasn't materialized yet (see `sdi-36`) |

> **Related**: [`sdi-15`](interview-roadmap.md#sdi-15-senior-differentiator-trade-off-maturity) (Trade-off Maturity), [`sdi-36`](complete-system-design-interview-guide-2026-takeaways.md#sdi-36-monolith-to-microservices-migration-trigger) (Monolith-to-Microservices)

---

### sdi-71: Next Bottleneck Identified

| | |
|:---|:---|
| **Problem** | Candidates stop at "the design works" without showing they understand how systems evolve — what breaks first as the system grows. |
| **Root cause** | Designing for a snapshot instead of a trajectory. |

**Check**: Identify what breaks first as load increases:

| Bottleneck | When | Mitigation |
|:---|:---|:---|
| "The primary database will hit write throughput limits" | ~5× current load | Add read replicas; consider sharding on user_id |
| "The cache will exceed memory as hot data grows" | ~3× current load | Tiered caching: Redis (hot) + SSD (warm); eviction policy tuning |
| "Fan-out on write will slow down for power users with growing follower counts" | ~2× current load | Introduce celebrity threshold; fan-out on read above threshold |

This shows you think in systems, not components — the design is a snapshot of an evolving system.

> **Related**: [`sdi-15`](interview-roadmap.md#sdi-15-senior-differentiator-trade-off-maturity) (Trade-off Maturity)

---

## Summary Card (Memorization Flashcard)

```
PHASE 1 — Requirements:    Actors? P0 + sync/async? Numbers, not adjectives? Confirmed scope?
PHASE 2 — Math:            Right heuristics? Overhead (5-10× raw)? Eliminated impossible options?
PHASE 3 — Entities:        UUID ext + auto-inc int? created_at, updated_at, deleted_at? Cardinalities?
PHASE 4 — API:             /v1/ in path? Idempotency-Key? Cursor pagination? Structured errors? Gateway defense?
PHASE 5 — HLD:             DB justified by workload? DB-first vs queue-first? Cache pattern matched? Fan-out hybrid? LB strategy?
PHASE 6 — Deep Dive:       Failure walkthrough? Consistency spectrum? Idempotency E2E (unique constraint)? Sharding key + cross-shard? P50/P95/P99 + alerts? 10× check?
PHASE 7 — Trade-offs:     Limitation named? Alternative rejected? Next bottleneck?
```

---

## Cross-References

- **Prerequisite**: [interview-roadmap.md](interview-roadmap.md) — 7-phase interview structure and foundational decision frameworks (`sdi-01`–`sdi-15`)
- **Decision Frameworks**: [complete-system-design-interview-guide-2026-takeaways.md](complete-system-design-interview-guide-2026-takeaways.md) — Scaling, caching, rate limiting, CQRS, multi-tenancy (`sdi-35`–`sdi-42`)
- **Pragmatic Principles**: [pragmatic-takeaways.md](pragmatic-takeaways.md) — User metrics first, boring architecture, solve today's problems (`prag-01`–`prag-08`)
- **Deep Dive Reference**: [interview-deep-dive.md](interview-deep-dive.md) — Scaling, caching, CAP theorem, replication, sharding (`sdi-16`–`sdi-27`)
- **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Caching](../../reference-dictionary/caching.md), [Resilience](../../reference-dictionary/resilience.md), [Messaging](../../reference-dictionary/messaging.md), [Databases](../../reference-dictionary/databases.md), [API Design](../../reference-dictionary/api-design.md)
- **Taxonomy**: §2.1 Application Architecture Styles
