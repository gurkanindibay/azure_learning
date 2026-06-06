# How to Structure Any System Design Interview in 45 Minutes

*By Kunal Sinha · 12 min read · Dec 21, 2025*

> **Source**: Originally published on [Medium](https://medium.com/@sinha.k/5bdf54236c4b)

---

System design interviews are notoriously overwhelming. With limited time and endless moving parts, it’s tempting to linger in familiar territory — leaving little room for the deep dive where expertise truly shines. After exploring various frameworks, I’ve synthesized a structured roadmap that balances technical breadth with the ticking clock. This template helps you move systematically through the foundations so you can focus on the complex trade-offs that matter.

---

## Table of Contents

- [Phase 1: Requirements (~5 min)](#phase-1-requirements-5-min)
- [Phase 2: Back-of-the-Envelope Math (~2 min)](#phase-2-back-of-the-envelope-math-2-min)
- [Phase 3: Core Entities (~3 min)](#phase-3-core-entities-3-min)
- [Phase 4: API Design (~5 min)](#phase-4-api-design-5-min)
- [Phase 5: High-Level Design (5–7 min)](#phase-5-high-level-design-57-min)
- [Phase 6: Deep Dive (~15 min)](#phase-6-deep-dive-15-min)
- [Phase 7: Trade-offs (2–3 min)](#phase-7-trade-offs-23-min)
- [Quick Reference](#quick-reference)

---

## Phase 1: Requirements (~5 min)
This is where most candidates lose the interview before it begins. Resist the urge to draw boxes.

### Checkpoint: Identify Your Actors

**Goal:** Know who uses the system before defining what it does.

**Action:** List all actors — User, Admin, Merchant, External System.

> **Script:** “Before diving into features, let me clarify the actors: end users, merchants, and an admin for disputes. Does that scope sound right?”

**Trap:** Only designing for the end user. Admins and external integrations often drive half the requirements.

### Checkpoint: Define Core Flows

**Goal:** Nail down 2–3 “P0” user journeys that drive the architecture.

**Action:** For each flow, decide if it’s synchronous (user waits) or asynchronous (background processing).

> **Script:** “The two critical flows are: user initiates payment (sync, returns `201`) and merchant views settlement report (async, returns `202` and emails when ready).”

**Trap:** Forcing synchronous processing for tasks that don’t need it. Ask: “Does the user actually need to wait?”

### Checkpoint: Define Failure Paths

**Goal:** Show the interviewer you think beyond the happy path.

**Action:** For each P0 flow, answer: “What happens when X fails?”

> **Script:** “If the payment gateway times out, we’ll retry with exponential backoff. After 3 failures, we notify the user and log for manual review.”

**Trap:** Only designing for success. Interviewers love asking “what if this fails?” — beat them to it.

### Checkpoint: Lock Down Your Non-Functional Requirements

**Goal:** Get specific numbers on paper so you can justify decisions later.

**Action:** Pick ONE from each category:

| Category | Options |
|----------|---------|
| Latency | `< 200ms` / `< 1s` / `< 10s` |
| Consistency | Strong / Read-after-write / Eventual |
| Correctness | Exactly-once / At-least-once |

> **Script:** “For a payment system, I’d target P99 latency under 500ms, strong consistency to prevent double-charges, and exactly-once semantics via idempotency keys.”

**Caveat:** Consistency comes with architectural cost. Strong consistency typically requires leader-based replication or quorum writes, which limits write scalability. We’ll address the mechanism in the deep dive.

**Trap:** Saying “highly available AND strongly consistent” without clarifying behavior during network partitions. You can have both normally — but during a partition, which do you sacrifice?

---

## Phase 2: Back-of-the-Envelope Math (~2 min)
The goal isn’t precision — it’s identifying the order of magnitude and where bottlenecks will appear.

### Checkpoint: Estimate QPS

**Goal:** Know if you’re building for 100 QPS or 100,000 QPS — the architecture differs dramatically.

**Action:** Use the 10⁵ shortcut: `Daily requests ÷ 100,000 ≈ QPS`

> **Script:** “50 million daily payments divided by 100,000 gives us roughly 500 QPS average. At peak, maybe 3x that — so 1,500 QPS. That’s comfortably handled by a single primary database.”

**Trap:** Calculating 86,400 seconds precisely. Use 100,000. Precision matters less than identifying the bottleneck.

### Checkpoint: Estimate Storage

**Goal:** Know if you need a single database or distributed storage.

**Action:** Calculate `(Daily writes × Size) × 365 × 5 years`

> **Script:** “500 QPS × 1KB per record × 86,400 seconds × 365 days × 5 years = roughly 70TB. We’ll need to think about archival or sharding.”

**Trap:** Calculating bandwidth for a text-only app. Focus on what actually matters for your system.

### Checkpoint: Estimate Cache Size

**Goal:** Know if caching fits in a single Redis instance or needs a cluster.

**Action:** Use the 80/20 rule — 20% of data serves 80% of reads. Size for hot data only.

> **Script:** “We have 10 million active users. If we cache the last 10 transactions per user at 1KB each, that’s 100GB — fits in a single large Redis instance.”

**Trap:** Forgetting peak vs. average. Design for 3–5x average traffic to handle spikes.

---

## Phase 3: Core Entities (~3 min)
Think of this as defining the “nouns” of your system.

### Checkpoint: Define Your Core Entities

**Goal:** Establish the 3–4 main objects that drive your data model.

**Action:** For each entity, identify: ID (UUID), foreign keys, status, and timestamps (`created_at`, `updated_at`, `deleted_at`).

> **Script:** “The core entities are `User`, `Merchant`, `Payment`, and `Transaction`. `Payment` has a UUID, references `user_id` and `merchant_id`, has a status enum, and timestamps for auditing.”

**Trap:** Over-normalizing. Don’t define 20 tables in a 45-minute interview. Stick to 3–4 core entities.

### Checkpoint: Choose Your ID Strategy

**Goal:** Avoid leaking business information through IDs.

**Action:** Use UUIDs or Snowflake IDs for external identifiers. Never expose auto-incrementing integers.

> **Script:** “We’ll use UUIDs for payment IDs exposed to merchants. Auto-increment IDs leak volume information and enable enumeration attacks.”

**Caveat:** Random UUIDs (v4) make poor primary keys in relational databases — they’re not sortable, causing index fragmentation and slow inserts. Consider these alternatives:

| Alternative | Rationale |
|-------------|-----------|
| Auto-increment as internal PK, UUID as separate `external_id` column | B-tree friendly PK + safe external ID |
| UUIDv7 or ULID | Time-sortable and index-friendly |
| Snowflake IDs | Sortable, unique, encode timestamp |

> **Script (if asked):** “Internally we use auto-increment for the primary key since it’s B-tree friendly. The UUID is a secondary indexed column for external lookups.”

**Trap:** Using auto-incrementing integers as public identifiers. Competitors can estimate your transaction volume.

### Checkpoint: Plan for Deletion

**Goal:** Meet compliance requirements without losing audit trails.

**Action:** Default to soft deletes with a `deleted_at` timestamp.

> **Script:** “For GDPR and financial compliance, we’ll soft-delete with a `deleted_at` flag. Hard deletes happen only after the legally required retention period.”

**Trap:** Hard deleting financial or user data. This often violates compliance requirements.

---

## Phase 4: API Design (~5 min)
Think of this as defining the “verbs” of your system.

### Checkpoint: Version Your API

**Goal:** Enable future changes without breaking existing clients.

**Action:** Always include version in the path: `/api/v1/resource`

> **Script:** “All endpoints are versioned — `/api/v1/payments`. This lets us evolve the API without breaking existing merchant integrations.”

**Trap:** Forgetting versioning. You’ll regret it when you need to make breaking changes.

### Checkpoint: Design for Idempotency

**Goal:** Make retries safe for all write operations.

**Action:** Accept an `Idempotency-Key` header. Store it and return the cached response on duplicates.

> **Script:** “Merchants include an `Idempotency-Key` header. If we see a duplicate key, we return the original response. This prevents double-charges on network retries.”

**Caveat:** Not all clients are sophisticated enough to generate idempotency keys. If idempotency is critical, the server must have fallback mechanisms:

| Mechanism | How It Works |
|-----------|-------------|
| **Natural keys** | Deduplicate on business attributes (e.g., `user_id + merchant_id + amount + timestamp` within a 5-minute window) |
| **Unique constraints** | Database-level enforcement (e.g., one pending payment per user-merchant pair) |
| **Request fingerprinting** | Hash the request body and deduplicate on the hash |

> **Script (if asked):** “We accept client-provided idempotency keys, but for critical flows like payments, we also enforce server-side deduplication using a natural key — user, merchant, amount, and a 5-minute window. Belt and suspenders.”

**Trap:** Assuming the network is reliable. Clients will retry. Make it safe — even if they don’t send an idempotency key.

### Checkpoint: Use Cursor-Based Pagination

**Goal:** Keep pagination stable even when new data is inserted.

**Action:** Return a `next_cursor` (Base64 string). Client passes it back for the next page.

> **Script:** “We return a `next_cursor` token instead of page numbers. This keeps results stable even if new transactions come in between page loads.”

**Trap:** Using offset-based pagination. Inserts between requests cause items to be skipped or duplicated.

### Checkpoint: Standardize Errors

**Goal:** Make debugging possible in production.

**Action:** Every error response includes: `code`, `message`, and `request_id`.

> **Script:** “All errors return a structured response with an error code, human-readable message, and `request_id` for tracing. Merchants can quote the `request_id` when contacting support.”

**Trap:** Missing request IDs. Without them, debugging production issues becomes a nightmare.

---

## Phase 5: High-Level Design (5–7 min)
Draw the happy path first. Optimization comes later.

### Checkpoint: Draw the Entry Point

**Goal:** Show the standard path from user to service and clarify what each layer does.

**Action:** Draw: `DNS → Load Balancer → API Gateway → Services`

**API Gateway responsibilities** (mention 2–3 of these):

| Responsibility | Description |
|---------------|-------------|
| Authentication | Validate JWT tokens, reject unauthenticated requests before they hit services |
| Rate Limiting | Enforce per-user or per-merchant limits (e.g., 1000 req/min) |
| Request ID Generation | Attach a globally unique `request_id` to every request for distributed tracing |
| Request Validation | Basic schema validation, reject malformed requests early |
| Routing | Direct traffic to the appropriate downstream service |

> **Script:** “Traffic enters through our load balancer, then hits the API gateway. The gateway handles three things: it validates the JWT and rejects unauthenticated requests, enforces rate limits per merchant, and generates a global `request_id` that propagates through all downstream services for tracing. Only then does the request hit our payment service.”

**Trap:** Drawing one big box labeled “Server” or treating API Gateway as just a passthrough. The gateway is your first line of defense — show you understand what it does.

### Checkpoint: Show the Async Path

**Goal:** Demonstrate you understand not everything needs synchronous processing — and that there are trade-offs in how you implement async.

**Action:** For `202 Accepted` flows, choose your write strategy:

#### Option A: Database First (Transactional Outbox)

```
API → Database → Outbox Poller/CDC → Queue → Worker
```

| Characteristic | Behavior |
|---------------|----------|
| Traceability | Request is immediately trackable (you can return an ID) |
| Queryability | User can query status right away |
| Bottleneck | DB can become a bottleneck at high scale |

#### Option B: Queue First

```
API → Queue → Worker → Database
```

| Characteristic | Behavior |
|---------------|----------|
| Throughput | Higher throughput, scales horizontally |
| Traceability | Request is “in flight” until worker processes it — not queryable yet |
| Risk | Risk of message loss if queue isn’t durable |

**When to use which:**

| Strategy | When | Example |
|----------|------|---------|
| **DB First** | User needs immediate confirmation or status tracking. Scale is moderate (< 10k writes/sec). | Payment initiation — user needs a transaction ID immediately. |
| **Queue First** | Fire-and-forget is acceptable. Scale is high. | Analytics events, activity logs, notifications. |

> **Script:** “For payment initiation, I’d write to the database first using the transactional outbox pattern — the user needs an ID immediately to track their payment. For activity logging, I’d write directly to Kafka since it’s fire-and-forget and we need the throughput.”

**Trap:** Writing directly to Kafka for user-facing flows where they expect immediate traceability. The user asks “where’s my payment?” and you have no record yet.

### Checkpoint: Justify Your Database Choice

**Goal:** Show you’re choosing technology based on requirements, not habit.

**Action:** State your choice and why:

| Type | Strengths |
|------|-----------|
| **SQL** | Transactions, complex queries, strong consistency |
| **NoSQL** | Flexible schema, horizontal scaling, high write throughput |

> **Script:** “Payments require ACID transactions, so we’ll use Postgres for the core payment data. Activity logs can go to DynamoDB since they’re append-only and high-volume.”

**Trap:** Choosing a database without justification. Always tie it back to your requirements.

---

## Phase 6: Deep Dive (~15 min)
Now apply your NFRs to solve the bottlenecks you identified in Phase 2.

### Checkpoint: Address Consistency

**Goal:** Understand the mechanisms behind consistency guarantees and their trade-offs.

**Action:** Know the difference between quorum and consensus — they’re not the same.

#### Quorum (`W + R > N`)

| Aspect | Detail |
|--------|--------|
| What it does | Ensures overlap between write and read replicas |
| Example | `W=2, R=2, N=3` — at least one node has the latest write |
| Used in | Cassandra, DynamoDB, Riak |
| Gives you | Tunable consistency, high availability, scalable writes |
| Trade-off | Potential for conflicts in leaderless/multi-writer setups; needs conflict resolution (last-write-wins, vector clocks, CRDTs) |

#### Consensus (Raft, Paxos, Zab)

| Aspect | Detail |
|--------|--------|
| What it does | Every participating node must agree before proceeding |
| Used for | Leader election, distributed locks, config changes, critical state transitions |
| Gives you | True agreement across nodes — no conflicts |
| Trade-off | Higher latency, reduced availability during partitions |

**When to use which:**

| Mechanism | Use Case |
|-----------|----------|
| **Quorum** | Regular read/write operations at scale. Acceptable for most data paths. |
| **Consensus** | Critical coordination only — leader election, distributed transactions, payment state machine transitions. Don’t use for regular data operations; the latency overhead isn’t worth it. |

> **Script:** “For regular reads and writes, quorum is sufficient — we configure `W=2, R=2, N=3`. But for payment state transitions, we need stronger guarantees. We use a Raft-based coordinator to ensure all nodes agree before we mark a payment as captured. Consensus adds latency, but for money movement, correctness beats speed.”

**Caveat:** Leaderless or multi-writer replication gives you high availability and scalable writes — but you lose strong consistency. If you go this route, you’ll need a conflict resolution strategy. For payments, that’s usually not acceptable.

**Trap:** Confusing quorum with consensus. Quorum ensures overlap; consensus ensures agreement. Using consensus for every write will kill your throughput — reserve it for critical paths.

### Checkpoint: Address Scalability

**Goal:** Show how the system handles growth beyond your initial estimates.

**Action:** If Write QPS > 10k, explain sharding. State your sharding key and why.

> **Script:** “If we grow beyond 10k writes per second, we’ll shard by `merchant_id`. This keeps each merchant’s data co-located and avoids cross-shard queries for their dashboards.”

**Trap:** Hand-waving sharding. You must explain the sharding key and why it was chosen. Bad keys create hot spots.

### Checkpoint: Address Latency

**Goal:** Show how you’ll meet your P99 latency target.

**Action:** Introduce caching strategically — Redis for hot data, CDN for static assets.

> **Script:** “To hit our 200ms P99 target, we’ll cache merchant configurations and recent transaction lookups in Redis. Cache TTL of 60 seconds with write-through invalidation.”

**Trap:** Adding caching before you’ve identified the bottleneck. Let your math guide your optimizations.

### Checkpoint: Implement Idempotency

**Goal:** Prove your system won’t double-charge on retries.

**Action:** Show a check-then-act pattern with database constraints.

> **Script:** “The `idempotency_key` is a unique constraint. We `INSERT` with `ON CONFLICT DO NOTHING`, then return the existing record if it was a duplicate. This is atomic — no race conditions.”

**Trap:** Implementing idempotency in application code without database constraints. Race conditions will bite you.

### Checkpoint: Handle Failures

**Goal:** Show the system degrades gracefully.

**Action:** Cover three patterns:

| Pattern | Mechanism |
|---------|-----------|
| **Circuit breaker** | Stop calling failing services |
| **Retry with backoff** | `1s → 2s → 4s` with jitter |
| **Dead letter queue** | Capture failed jobs for inspection |

> **Script:** “If the payment gateway fails 5 times in 10 seconds, we trip the circuit breaker and return a `503` for 30 seconds. This prevents cascade failures. Failed async jobs go to a DLQ for manual review.”

**Trap:** Unbounded retries. Retrying forever without backoff can DDoS your own system during outages.

### Checkpoint: Set Timeout Hierarchy

**Goal:** Ensure timeouts cascade correctly from edge to database.

**Action:** Set timeouts in descending order: `Client > Gateway > Service > Database`

> **Script:** “Timeouts cascade: client at 10s, gateway at 8s, service at 5s, database at 2s. This ensures the user gets a clean timeout error rather than a hanging request.”

**Trap:** Setting the database timeout higher than the client timeout. The client gives up, but the database keeps working — wasting resources.

### Checkpoint: Add Observability

**Goal:** Show you can debug this system in production.

**Action:** Mention: metrics (P99 latency, error rates), distributed tracing (`request_id` across services), and alerting thresholds.

> **Script:** “We’ll track P50/P95/P99 latency and 5xx rates in Datadog. Every request gets a trace ID that propagates through all services. We page on-call if error rate exceeds 1% for 5 minutes.”

**Trap:** Treating observability as optional. In production, you can’t fix what you can’t see.

---

## Phase 7: Trade-offs (2–3 min)
This is where senior candidates distinguish themselves.

### Checkpoint: Acknowledge Limitations

**Goal:** Show architectural maturity by identifying gaps before the interviewer does.

**Action:** Proactively mention 1–2 things you didn’t address.

> **Script:** “We haven’t covered multi-region failover. For a payment system, I’d recommend active-passive with async replication and a 30-second RPO. Happy to go deeper if that’s useful.”

**Trap:** Being defensive. Don’t wait for the interviewer to find holes — call them out yourself.

### Checkpoint: Mention Alternatives

**Goal:** Prove you considered other approaches.

**Action:** Briefly mention a road not taken and why.

> **Script:** “We could use event sourcing instead of a traditional database. It would give us a perfect audit trail, but adds complexity we don’t need at this scale.”

**Trap:** Presenting your design as the only option. Good architects know trade-offs.

### Checkpoint: Identify the Next Bottleneck

**Goal:** Show you’re thinking about evolution, not just the current state.

**Action:** Name what breaks at 10x or 100x scale.

> **Script:** “At 100x scale, the single Redis becomes a bottleneck. We’d move to Redis Cluster, or evaluate a distributed cache like EVCache.”

**Trap:** Over-engineering the future into V1. Discuss improvements, but don’t build them yet.

---

## Quick Reference

| Rule | Value |
|------|-------|
| QPS | Daily total ÷ 100,000 |
| Peak traffic | 3–5x average |
| Cache size | 20% of hot data |
| Latency target | `< 200ms` user-facing |
| Sharding trigger | `> 10k` write QPS |
| Retry pattern | Exponential backoff with jitter |
| Deletion default | Soft delete with `deleted_at` |
| ID strategy | UUIDs externally, auto-increment internally |

---

## Final Thought
The goal isn’t to memorize this template — it’s to internalize the rhythm. Each phase builds on the previous. Skip a step, and your design will have gaps.

Practice it once. Then again. By the third time, you won’t need the template — the structure will be instinct.

> This template will be my reference point for future system design posts. When I walk through designing a payment system or a notification service, I’ll follow this same sequence. If something feels unfamiliar in those posts, come back here.