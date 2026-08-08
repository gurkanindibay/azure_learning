---
type: System Design
title: "System Design Interview — Key Takeaways"
description: "30 real-world system design scenarios with problem→strategy→tradeoff analysis covering APIs, databases, caching, queues, payments, reliability, and scaling."
timestamp: 2026-07-30T00:00:00Z
---

# 33. System Design Interview — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [60+ Real-World System Design Scenarios to Prepare for Your Next Interview (Part 1)](../../articles/system-design-interview/real-world-system-design-scenarios-part-1.md)
> **Taxonomy Reference**: §2.1 Application Architecture Patterns

> **Also see**: [Interview Roadmap](interview-roadmap.md), [Pragmatic Takeaways](pragmatic-takeaways.md)
> **Dictionary**: [API Gateway](../../reference-dictionary/api-design.md#api-gateway), [CQRS](../../reference-dictionary/cqrs-event-driven.md#cqrs), [Circuit Breaker](../../reference-dictionary/resilience.md#circuit-breaker), [Idempotency](../../reference-dictionary/resilience.md#idempotency), [Bloom Filter](../../reference-dictionary/caching.md#bloom-filter), [RAG](../../reference-dictionary/ai-ml-llm.md#retrieval-augmented-generation)

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [sdi-82](#sdi-82) | Mobile app coupled directly to backend services | API Gateway for single entry point |
| [sdi-83](#sdi-83) | N+1 query causing 2.4s P95 latency | Eager-load relations before caching |
| [sdi-84](#sdi-84) | Fixed-window rate limiting allows boundary bursts | Token Bucket for smooth rate limiting |
| [sdi-85](#sdi-85) | Duplicate payment charges from retries | Idempotency-Key for retry-safe writes |
| [sdi-86](#sdi-86) | 500M-row table needs sharding | Directory-based sharding by access pattern |
| [sdi-87](#sdi-87) | Distributed cron job runs on multiple instances | Fencing token with distributed lock |
| [sdi-88](#sdi-88) | Event ordering lost across parallel consumers | FIFO queue with MessageGroupId per entity |
| [sdi-89](#sdi-89) | Stale cache with multiple writers | Cache-aside: DB is source of truth |
| [sdi-90](#sdi-90) | Same DB for reads and writes causes contention | CQRS: separate read/write models |
| [sdi-91](#sdi-91) | Multi-service transaction without 2PC | Orchestration Saga with compensations |
| [sdi-92](#sdi-92) | Webhook timeouts cause duplicate processing | Acknowledge fast, process async |
| [sdi-93](#sdi-93) | High-ingest table needs indexing without write penalty | Partial index on frequently queried subset |
| [sdi-94](#sdi-94) | Multiple workloads exhaust DB connections | PgBouncer: transaction mode vs session mode |
| [sdi-95](#sdi-95) | Risky payment code rollout | Feature flags separate deploy from release |
| [sdi-96](#sdi-96) | 80B-row "seen" check overwhelms DB | Bloom filter for negative lookups |
| [sdi-97](#sdi-97) | Hot partition key on DynamoDB | Write sharding with random suffix |
| [sdi-98](#sdi-98) | Kafka consumer overwhelmed by producer | Rate-limit and load-shed to overflow topic |
| [sdi-99](#sdi-99) | Cache stampede on hot key expiry | Cache pre-warming before TTL expires |
| [sdi-100](#sdi-100) | Stale reads from read replica | Read-your-writes: route post-write to primary |
| [sdi-101](#sdi-101) | Failing downstream dependency cascades | Circuit Breaker + Bulkhead together |
| [sdi-102](#sdi-102) | AI token streaming: WebSocket vs SSE | SSE for one-way browser streams |
| [sdi-103](#sdi-103) | Reliable messaging without duplicates | At-least-once delivery + idempotent consumer |
| [sdi-104](#sdi-104) | Celebrity post crashes feed fanout | Hybrid fanout: write for normal, read for celebrities |
| [sdi-105](#sdi-105) | Deep offset pagination on 50M rows | Cursor pagination with indexed anchor |
| [sdi-106](#sdi-106) | Queue backlog during Black Friday spike | Backpressure: throttle producer, not just scale consumer |
| [sdi-107](#sdi-107) | Cache-database inconsistency after partial failure | Outbox pattern for reliable cache updates |
| [sdi-108](#sdi-108) | LLM answers outdated by weekly product changes | RAG for knowledge freshness |
| [sdi-109](#sdi-109) | 4M-vector semantic search at 300 QPS | Qdrant for payload-filtered ANN search |
| [sdi-110](#sdi-110) | Multi-agent workflow with unordered execution | DAG-based execution for explicit dependencies |
| [sdi-111](#sdi-111) | 100TB file storage backend selection | S3 for shared object storage at scale |

---

## sdi-82: API Gateway for Backend Decoupling

| | |
|:---|:---|
| **Problem** | Mobile app communicates directly with multiple backend services (UserService, OrderService, PaymentService). Each new service forces the client to configure another domain, auth flow, and error format. |
| **Key Concept** | An API Gateway provides a single stable entry point (`api.yourapp.com`) that handles routing, auth, rate limiting, TLS termination, and consistent error responses — decoupling the client from backend service topology. |

> **Strategy**: Route all client requests through an API Gateway. Add new services by registering routes — the mobile app requires no infrastructure changes. The gateway centralizes cross-cutting concerns (auth, logging, rate limiting, versioning).

> **Tradeoff**: Introduces a new infrastructure component to operate. A BFF (Backend for Frontend) is overkill when the problem is routing, not data shape. GraphQL Federation requires schema migration for what is fundamentally a routing problem.

> **Cross-reference**: [Reverse Proxy, LB & API Gateway](api-network/reverse-proxy-lb-gateway.md), [API Design Patterns](api-network/api-design-patterns.md)

---

## sdi-83: Eager-Load Before Caching (N+1)

| | |
|:---|:---|
| **Problem** | `/orders` endpoint fetches 50 orders, then the ORM lazily loads `order.customer` inside a loop: 1 query for orders + 50 queries for customers = 51 queries. P95 latency is 2.4s. |
| **Key Concept** | The simplest fix for an N+1 problem is to remove the lazy-loaded relation using eager loading (`include`, `JOIN`). Fix the query pattern before adding caching, batching, or denormalization. |

> **Strategy**: Use ORM eager-loading (`Prisma.include`, `Sequelize.include`, `TypeORM.relations`) to fetch orders and customers in one database round trip. DataLoader is for GraphQL with many nested resolvers — overkill for one predictable relation. Redis caching doesn't fix the query count, only masks it.

> **Tradeoff**: A JOIN may return duplicate parent rows (orders repeated per customer column), but this is negligible compared to 50 extra round trips.

> **Cross-reference**: [SQL Query Optimization](databases/sql-query-optimization.md)

---

## sdi-84: Token Bucket Over Fixed Window

| | |
|:---|:---|
| **Problem** | Fixed-window rate limiter resets at minute boundaries. 90 requests at 12:59:58 + 90 at 13:00:02 = 180 in 4 seconds, overwhelming the database. |
| **Key Concept** | Token Bucket refills continuously (~1.66 tokens/sec for 100/min) with no boundary reset. After a burst, few tokens have replenished — the second burst is rejected. O(1) storage, straightforward distributed implementation. |

> **Strategy**: Each API key gets a bucket of 100 tokens. Every request consumes 1 token; tokens refill at a steady rate. Provides controlled short bursts with a stable long-term rate. Widely used by public APIs and API gateway platforms.

> **Tradeoff**: Sliding Window Log is more accurate but stores every timestamp (heavy at scale). Leaky Bucket delays requests (adds latency). Fixed Window is the source of the problem.

> **Cross-reference**: [API & Network Design](api-network/api-network-design.md)

---

## sdi-85: Idempotency Key for Payment Safety

| | |
|:---|:---|
| **Problem** | User taps "Pay $499" three times. Three nearly identical requests reach the Payments API. Multiple charges succeed. |
| **Key Concept** | Require an `Idempotency-Key` header. The server processes the payment once, stores the key→response mapping, and returns the stored response on retries. For stronger protection, pass the same key to the payment provider (Stripe, PayPal). |

> **Strategy**: Client generates a unique key before the first attempt. Server stores `key → status + response`. Concurrent requests with the same key wait or receive 409 Conflict. A unique DB constraint is a safeguard, not the primary solution — it can't undo an external payment charge. Distributed locks prevent concurrent execution but not repeated execution across time. Serializable transactions don't cover external side effects.

> **Tradeoff**: Requires durable idempotency-key storage and a TTL policy for key cleanup.

> **Cross-reference**: [Idempotency](../../reference-dictionary/resilience.md#idempotency), [CQRS for Fintech](cqrs-fintech/cqrs-fintech.md)

---

## sdi-86: Directory-Based Sharding by Access Pattern

| | |
|:---|:---|
| **Problem** | PostgreSQL orders table: 500M rows, 80% reads are one customer's recent orders, 15% analytics across date ranges. Range queries went from 40ms to 800ms. |
| **Key Concept** | Choose the shard key by the dominant access pattern. Since 80% of reads are customer-specific, use directory-based sharding: `customer_id → shard_id`. Heavy customers can be moved individually without redistributing the entire dataset. |

> **Strategy**: Map each customer to a specific shard. A customer lookup hits one shard instead of scatter-gathering across all shards. Date-range analytics may still query multiple shards, but the dominant pattern is optimized.

> **Tradeoff**: Hash sharding on `order_id` distributes evenly but scatter-gathers customer history. Range sharding on `created_at` creates a hotspot on the newest shard. Consistent hashing offers less control over individual high-traffic customers.

> **Cross-reference**: [Databases & Query Performance](databases/query-performance.md)

---

## sdi-87: Fencing Token for Distributed Locks

| | |
|:---|:---|
| **Problem** | Three app instances run the same cron job. Redis lock with TTL seems to solve it, but a paused/crashed process may resume after TTL expiry while another instance holds the lock — both write to the same output. |
| **Key Concept** | A fencing token is a monotonically increasing number issued with each lock acquisition. The protected resource (DB, storage) remembers the highest token accepted and rejects writes with lower tokens. The lock decides who may start; the fencing token prevents an expired owner from continuing. |

> **Strategy**: `Redis SETNX` with short TTL + fencing token. Each acquisition increments the token. Downstream systems validate that the token ≥ last accepted. Protects against crashes, network partitions, GC pauses, and expired leases.

> **Tradeoff**: Redlock (multi-node Redis) without fencing tokens still allows stale owners to write. `SELECT ... FOR UPDATE` holds DB connections during long jobs. Optimistic concurrency works only for single idempotent writes, not multi-step reports.

> **Cross-reference**: [Resilience Patterns](resilience/resilience-patterns.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md)

---

## sdi-88: FIFO Queue with Message Group per Entity

| | |
|:---|:---|
| **Problem** | Order events (`created → paid → cancelled`) are published in order but processed in parallel by 5 workers. `cancelled` runs first, state machine rejects `created`, leaving incorrect data. |
| **Key Concept** | Use SQS FIFO with `MessageGroupId = order_id`. Events for the same order are delivered in sequence while different orders (different group IDs) process concurrently — preserving per-entity ordering without sacrificing parallelism. |

> **Strategy**: Partition by entity identifier. Messages in the same group are delivered in order. Different groups use different workers concurrently. No need for consumer-side reorder buffers, sequence tracking, or timeout handling.

> **Tradeoff**: A reorder buffer requires sequence tracking, timeouts, crash recovery, and monitoring — effectively rebuilding FIFO in the application. Saga is for distributed transactions, not entity-level event ordering. Versioning can reject stale events but can't reconstruct missing transitions.

> **Cross-reference**: [Message Brokers & Kafka](messaging/kafka-consumer-mistakes.md)

---

## sdi-89: Cache-Aside with Multiple Writers

| | |
|:---|:---|
| **Problem** | E-commerce catalog: Redis in front of PostgreSQL at 40K RPS. Multiple systems (Admin Panel, Inventory Service, Order Service) all update product data. Customers see outdated prices, incorrect stock. |
| **Key Concept** | Cache-aside: update PostgreSQL first (source of truth), then invalidate the Redis key (`DEL product:123`). The next read misses the cache and repopulates from fresh data. Redis stays a disposable read accelerator. |

> **Strategy**: Always write to the database first, then delete the cache key. If Redis is unavailable, the app reads from PostgreSQL — slower but correct. Used by Shopify, Etsy, and AWS reference designs.

> **Tradeoff**: Write-through can't atomically update Redis + PostgreSQL — if Redis update fails, stale cache remains. Write-behind makes Redis the temporary source of truth (risk of data loss). Read-through doesn't handle multiple-writer invalidation.

> **Cross-reference**: [Caching & Redis Internals](../../reference-dictionary/caching.md#cache-aside), [Redis Internals](caching/redis-internals.md)

---

## sdi-90: CQRS for Divergent Read/Write Shapes

| | |
|:---|:---|
| **Problem** | Orders Service: 8K writes/min (normalized: orders, line_items, payments, shipments, addresses), 40K reads/min (one dashboard card needs 7 joins, reporting pushes CPU to 85%). Indexes and caching already optimized. |
| **Key Concept** | CQRS separates write models (normalized, strongly consistent) from read models (denormalized projections). One dashboard card loads from a single `order_view` record instead of 7 joined tables. Changes flow through Outbox/CDC → Kafka → read-model projector. |

> **Strategy**: Keep the normalized transactional model for writes. Build a separate denormalized projection (Postgres read DB or Elasticsearch) for queries. Dashboard, reports, and searches tolerate eventual consistency; operations needing immediate consistency read from the write DB.

> **Tradeoff**: Read replicas reduce primary pressure but don't remove expensive joins. Denormalizing the write model damages the write path (duplicate data, write amplification). GraphQL/DataLoader can't eliminate expensive DB joins.

> **Cross-reference**: [CQRS](../../reference-dictionary/cqrs-event-driven.md#cqrs), [Architecture Patterns](../../reference-dictionary/architecture-patterns.md)

---

## sdi-91: Orchestration Saga for Multi-Service Transactions

| | |
|:---|:---|
| **Problem** | Order checkout spans 4 services: Order created, Payment charged, Inventory reservation failed, Shipping never started. Customer paid but no inventory. Can't roll back 4 independent DBs with one transaction. |
| **Key Concept** | Orchestration Saga: a central workflow (Temporal, AWS Step Functions, Camunda) coordinates each step and runs compensating actions on failure (Inventory fails → Refund Payment → Cancel Order). Workflow state is durable, observable, and recoverable. |

> **Strategy**: Use an orchestrator for ordered multi-service workflows with clear rollback actions. The orchestrator tracks which step failed and which compensations were executed. Each step is a local transaction + a published event.

> **Tradeoff**: Choreography spreads logic across services — hard to understand who owns the workflow. 2PC requires all participants to support the protocol (Stripe doesn't). Outbox Pattern ensures reliable event publishing but doesn't define workflow order or compensations.

> **Cross-reference**: [Saga Pattern](../../reference-dictionary/cqrs-event-driven.md#saga), [Distributed Transactions](concurrency-transactions/concurrency-transactions.md)

---

## sdi-92: Acknowledge Fast, Process Async (Webhooks)

| | |
|:---|:---|
| **Problem** | Stripe webhook handler has ~10s to return 200. Pod restarts during processing, DB slowdowns cause timeouts, and events arrive out of order (`charge.refunded` before `charge.succeeded`). Duplicate charges and incorrect order states result. |
| **Key Concept** | Verify the HMAC signature (~few ms), write the raw payload to a durable queue (SQS/Kafka/Redis Streams), return 200 immediately. Separate webhook receipt (fast) from webhook processing (slow). Stripe, Shopify, and GitHub recommend this pattern. |

> **Strategy**: Decouple Stripe's delivery deadline from internal processing time. Signature validation takes milliseconds. Once the event is in a durable queue, the webhook endpoint returns 200. If a pod restarts, the message stays in the queue. If the DB is slow, the webhook receiver is unaffected.

> **Tradeoff**: Idempotency key + deduplication table alone doesn't solve the architectural problem — the handler is still synchronous on Stripe's critical path. The idempotency layer should exist inside the async processing flow, not as a replacement for it.

> **Cross-reference**: [Idempotency](../../reference-dictionary/resilience.md#idempotency), [Message Brokers & Kafka](messaging/kafka-consumer-mistakes.md)

---

## sdi-93: Partial Index for High-Ingest Tables

| | |
|:---|:---|
| **Problem** | PostgreSQL events table: 200M rows, 8K inserts/sec, 4 existing indexes. 92% of dashboard queries ask for one tenant's signup events from the last 7 days (~0.2% of rows). Adding a 5th full-table index could push ingestion into failure. |
| **Key Concept** | A partial index with `WHERE event_type = 'signup' AND created_at > now() - interval '7 days'` indexes only the frequently queried subset. Most writes bypass the index entirely, avoiding write amplification while still accelerating the dashboard query. |

> **Strategy**: Index only the rows matching the dominant query predicate. The query planner uses the partial index when the query conditions match. The dashboard gets fast reads; the ingestion pipeline avoids maintaining another large index.

> **Tradeoff**: A covering index with `INCLUDE (payload)` bloats the index with large JSONB data and amplifies every write. A read replica helps with read isolation but doesn't remove the index maintenance cost on the primary. If dashboard requirements change (7 days → 30 days), the partial index may need rebuilding.

> **Cross-reference**: [SQL Query Optimization](databases/sql-query-optimization.md)

---

## sdi-94: PgBouncer — Transaction Mode vs Session Mode

| | |
|:---|:---|
| **Problem** | REST API (400 connections), background workers (long analytics, 30-90s), and Lambda (bursty) all hit one PostgreSQL with max 300 connections. |
| **Key Concept** | Use PgBouncer transaction mode for stateless REST/Lambda (strong multiplexing: 400→~40 backend connections) and session mode for workers that need stable session state (temp tables, prepared statements, cursors, `SET` commands). |

> **Strategy**: Transaction mode returns the connection to the pool after each transaction — perfect for short-lived REST requests. Session mode pins one client connection to one backend connection for the full session — required for workers with session-level state. Run both modes on different PgBouncer ports.

> **Tradeoff**: Transaction mode for everyone breaks workers that depend on session state (temp tables silently fail in production). RDS Proxy solves Lambda cold starts but doesn't give workers session-mode behavior. Moving workers to a read replica changes where connection exhaustion happens, not that it happens.

> **Cross-reference**: [Databases & Query Performance](databases/query-performance.md)

---

## sdi-95: Feature Flags for Risky Payment Rollouts

| | |
|:---|:---|
| **Problem** | Releasing a rewritten checkout write path (Stripe Charges API → PaymentIntents with 3D Secure). Rolling back the app doesn't reverse a payment already charged. Money is at stake. |
| **Key Concept** | Feature flags separate deployment from release. Deploy new code to 100% of tasks disabled, then enable gradually (internal → 1% → 10% → 100%). Rollback is a config change (instant, no redeploy). Selective rollout by customer segment, not random percentage. |

> **Strategy**: Deploy everywhere, release gradually. Keep the old payment path available for days/weeks. If a 3D Secure issue affects only one issuing bank, move those users back to the old path. Kill switch provides instant rollback.

> **Tradeoff**: Canary deployment routes by request, not customer — a single B2B billing job may hit the new version repeatedly. Payment bugs may return 200 OK while charging incorrectly, so standard error-rate alarms are unreliable. Blue/Green switches 100% of traffic at once, creating cross-version race conditions with in-flight webhooks. Rolling deployment mixes old and new versions writing to the same state, risking inconsistency.

> **Cross-reference**: [Deployment Patterns](../../reference-dictionary/deployment-patterns.md#feature-flag)

---

## sdi-96: Bloom Filter for "Has User Seen This?"

| | |
|:---|:---|
| **Problem** | Content feed for 50M users. Every recommendation checks "Has user seen post X?" against an 80B-row PostgreSQL table. P99 latency 600ms. 97% of checks are for unseen posts. False positives acceptable, false negatives survivable. |
| **Key Concept** | Store a Bloom filter per user in Redis (~12KB for 10K seen posts at 1% FPR). If the filter says "definitely not seen," skip PostgreSQL. If "maybe seen," confirm with PostgreSQL. Across 50M users: ~600GB vs ~4TB for Redis SETs. |

> **Strategy**: A Bloom filter provides sub-millisecond "definitely not seen" checks. For the 97% of requests where the answer is "not seen," PostgreSQL is never touched. The 1% false-positive rate (occasionally skipping an unseen post) is acceptable per product requirements. Bloom filters never produce false negatives.

> **Tradeoff**: Redis SET per user provides exact answers but at 4TB across 50M users. Cassandra migration solves storage but not the 120K-RPS point-lookup pattern. Read replicas add capacity but each lookup still requires a DB round trip. This is an efficiency problem, not a capacity problem.

> **Cross-reference**: [Bloom Filter](../../reference-dictionary/caching.md#bloom-filter), [Caching & Redis Internals](caching/redis-internals.md)

---

## sdi-97: Write Sharding for DynamoDB Hot Partitions

| | |
|:---|:---|
| **Problem** | Multi-tenant analytics on DynamoDB. One tenant generates 9,000 writes/sec while 199 others generate ~15 writes/sec each. All events use `tenant_id` as partition key — one physical partition handles the entire hot tenant workload. Throttling and 400ms P99. |
| **Key Concept** | Write sharding: add a random suffix (`tenant_123#0` through `tenant_123#9`) to spread 9,000 writes across 10 partition keys. DynamoDB's hash distributes them across physical partitions. Each shard receives ~900 writes/sec — well below partition limits. |

> **Strategy**: Randomly select a suffix for each write. Reads become scatter-gather (query all 10 suffixes, merge results). For a write-heavy analytics pipeline, this is the correct trade-off — slightly more complex reads for reliable, scalable writes.

> **Tradeoff**: Partition splitting doesn't divide one partition-key value across destinations — the hot key stays hot. Jitter smooths short bursts but doesn't reduce sustained 9,000 writes/sec on one key. Time-bucketed keys (`tenant#YYYY-MM-DD-HH`) just rename the hot partition — all writes in an hour still hit one key.

> **Cross-reference**: [Databases & Query Performance](databases/query-performance.md)

---

## sdi-98: Load-Shed with Overflow Topic (Kafka Backpressure)

| | |
|:---|:---|
| **Problem** | Kafka consumer processes 800 events/sec; producer jumps to 5,000 events/sec sustained. Consumer lag: 12 minutes and growing, memory 89%, JVM near GC death. SLA: every event must be processed, cannot be silently discarded. |
| **Key Concept** | Rate-limit the primary consumer at a sustainable rate (~1,000 events/sec). Route excess events to a durable overflow topic (`events.overflow`). A secondary consumer group processes the overflow during lower traffic. Graceful degradation without data loss. |

> **Strategy**: Keep the primary consumer healthy and heartbeating. Overflow events are stored durably and processed later. Producer continues publishing uninterrupted. The system degrades gracefully by delaying part of the workload rather than failing completely.

> **Tradeoff**: Blocking the producer doesn't work in Kafka's decoupled, pull-based model — there's no direct socket-level backpressure signal. Dropping events violates the SLA. Larger buffers only delay the problem (~4 minutes for 1M buffer at 4,200 events/sec deficit). More consumers may not help if the bottleneck is the downstream DB/HTTP service.

> **Cross-reference**: [Message Brokers & Kafka](messaging/kafka-consumer-mistakes.md), [Backpressure](../../reference-dictionary/messaging.md#backpressure)

---

## sdi-99: Cache Pre-Warming for Stampede Prevention

| | |
|:---|:---|
| **Problem** | Redis cache key expires; 8,000 requests/sec bypass cache and hit PostgreSQL simultaneously (thundering herd). Database comfortable at ~200 req/sec, now overwhelmed. |
| **Key Concept** | Cache pre-warming: a background job refreshes the key before TTL expires (e.g., every 45s for a 60s TTL). The key never becomes cold, so no sudden moment when 8,000 requests fall through to the database. Combine with stale-while-revalidate for safety. |

> **Strategy**: A cron/Lambda/background worker refreshes hot cache keys proactively. Netflix uses this for content metadata; Twitter for celebrity timelines. If the refresh job runs late, continue serving the stale value while rebuilding.

> **Tradeoff**: Request coalescing coordinates only within one process — at 50 instances, you still get 50 DB queries per expiry. Mutex lock blocks thousands of waiting requests (P99 spikes to seconds). Probabilistic early expiry reduces the chance but doesn't eliminate the possibility of a stampede.

> **Cross-reference**: [Cache Stampede](../../reference-dictionary/caching.md#cache-stampede), [Caching & Redis Internals](caching/redis-internals.md)

---

## sdi-100: Read-Your-Writes Consistency

| | |
|:---|:---|
| **Problem** | Read replica reduced P95 from 400ms to 90ms. But customers update their shipping address and confirmation shows the old address. Order deduplication fails because replica doesn't yet have the first order (200ms replication lag). |
| **Key Concept** | Read-your-writes: after a user performs a write, temporarily route that user's subsequent reads to the primary for a few seconds (until the replica catches up). Other users continue reading from the replica, preserving the performance benefit for most traffic. |

> **Strategy**: Track per-user post-write windows (a few seconds). Route reads to primary during this window. Apply the same rule when a read depends on a write that just happened (order deduplication, payment idempotency checks).

> **Tradeoff**: Routing "critical" reads to primary is fragile — what's "critical" is not consistently defined across a growing codebase. Synchronous replication adds 80-120ms to every write and couples primary availability to replica health. Monitoring replica lag doesn't solve the immediate post-write read problem (200ms lag is normal, but the read happens 50ms after the write).

> **Cross-reference**: [Data Consistency](../../reference-dictionary/data-concurrency.md#read-your-writes), [Databases & Query Performance](databases/query-performance.md)

---

## sdi-101: Circuit Breaker + Bulkhead Together

| | |
|:---|:---|
| **Problem** | Checkout calls third-party fraud API (normally 200ms). Fraud API starts timing out after 30s. All 50 checkout connections stuck waiting. P99 latency: 28 seconds. `/cart`, `/orders`, `/health` also fail — one degraded dependency takes down everything. |
| **Key Concept** | Use both patterns: Circuit Breaker stops calling the failing service (OPEN → fail fast → half-open probe) while Bulkhead isolates fraud API connections (10 dedicated) from the rest of checkout (40 separate). The breaker reduces outage duration; the bulkhead prevents cascade while the breaker collects enough failures to open. |

> **Strategy**: Circuit Breaker: after N failures, open and fail fast. Half-open: send one probe, close on success, open on failure. Bulkhead: separate connection pool for fraud API. Together: unhealthy dependency fails quickly while the rest of checkout continues working.

> **Tradeoff**: Circuit Breaker alone doesn't open instantly — before the threshold is reached, the shared pool can still exhaust. Bulkhead alone contains the blast radius but still wastes 10 connections on 30s timeouts. Shorter timeout + retries creates a retry storm against the already degraded service, extending the outage.

> **Cross-reference**: [Circuit Breaker](../../reference-dictionary/resilience.md#circuit-breaker), [Bulkhead](../../reference-dictionary/resilience.md#bulkhead), [Resilience Patterns](resilience/resilience-patterns.md)

---

## sdi-102: Server-Sent Events for AI Token Streaming

| | |
|:---|:---|
| **Problem** | AI chat app: LLM streams ~40 tokens/sec to 50K concurrent browser users. Data is one-way (server→browser). Must handle mobile network switches (Wi-Fi↔LTE) gracefully. |
| **Key Concept** | Server-Sent Events (SSE): one-way HTTP stream with native browser `EventSource` API. Automatic reconnection with `Last-Event-ID` for stream resumption. No protocol upgrade, no custom framing. OpenAI and Anthropic use SSE for streaming APIs. |

> **Strategy**: Submit user prompt via POST, stream generated tokens via SSE (`text/event-stream`). Browser's `EventSource` handles reconnection natively. FastAPI writes events to the stream with minimal overhead.

> **Tradeoff**: WebSockets are full-duplex — paying for bidirectional complexity (sticky sessions, custom reconnect, ping/pong) when the pattern is one-way. gRPC server streaming requires Envoy + gRPC-Web proxy for browser support. Long polling at 40 tokens/sec × 50K users = 2M requests/sec overhead.

> **Cross-reference**: [API & Network Design](api-network/api-network-design.md)

---

## sdi-103: At-Least-Once Delivery + Idempotent Consumer

| | |
|:---|:---|
| **Problem** | Payment Service charges customer, saves to PostgreSQL, then HTTP-calls Notification Service. Request times out. Did it send the email? Retry → duplicate confirmation email. This is the Two Generals Problem — no finite number of retries or acknowledgements provides certainty. |
| **Key Concept** | Accept that duplicate delivery may happen. Use SQS at-least-once delivery + stable idempotency key (`payment_id:email:v1`). Consumer checks a deduplication table before acting. Duplicates become no-ops. No missed notifications, no duplicate emails. |

> **Strategy**: Publish to SQS after payment. Notification Service uses idempotency key to deduplicate. This is the approach Stripe and AWS use. The queue handles delivery uncertainty; idempotency handles duplicates.

> **Tradeoff**: Retry-until-ack creates an infinite regress (what if the ack's ack is lost?). 2PC introduces coordinator as a single point of failure and requires all participants to support the protocol. Outbox Pattern is correct but heavier (CDC pipeline, relay process, cleanup, monitoring) — use when strict DB-level atomicity is required.

> **Cross-reference**: [Idempotency](../../reference-dictionary/resilience.md#idempotency), [Message Brokers & Kafka](messaging/kafka-consumer-mistakes.md)

---

## sdi-104: Hybrid Fanout for Celebrity Accounts

| | |
|:---|:---|
| **Problem** | Feed service: 10M users, 50K posts/day. Celebrity with 2M followers publishes — response time jumps from 20ms to 4s. Fanout-on-write creates 2M cache writes; fanout-on-read requires 500 queries per user to build the feed. |
| **Key Concept** | Hybrid fanout: fanout-on-write for normal accounts (<10K followers), fanout-on-read for celebrities. At read time, merge the precomputed feed cache with live queries for followed celebrity accounts. The number of celebrity accounts a user follows is small and manageable. |

> **Strategy**: Check follower count on publish. Below threshold: push post into followers' Redis feed caches. Above threshold: skip fanout. At read time: merge precomputed cache + live celebrity query. This is the approach Twitter described for handling feeds at scale.

> **Tradeoff**: Fanout-on-write alone creates 2M cache writes per celebrity post — the cache cluster saturates. Fanout-on-read alone makes every feed request expensive (500 lookups + merge + sort). Materialized feed table delays the 2M writes asynchronously but doesn't remove the write amplification.

> **Cross-reference**: [Caching & Redis Internals](caching/redis-internals.md)

---

## sdi-105: Cursor Pagination Over Offset

| | |
|:---|:---|
| **Problem** | 50M-row orders table. Offset pagination (`OFFSET 40 LIMIT 10`) scans and discards early rows. Deep pages: 4.2s query time, table scans increasing. Frontend needs prev/next/jump-to-page, sorted by `created_at DESC`, filtered by `status`. |
| **Key Concept** | Cursor pagination encodes `(created_at, id)` of the last returned row into an opaque token. Next query uses `WHERE (created_at, id) < (cursor_created_at, cursor_id) ORDER BY created_at DESC, id DESC LIMIT 10`. O(log N) via index seek instead of O(N) offset scan. |

> **Strategy**: Return a cursor token with each page. Client sends it back for the next page. For jump-to-page, use keyset pagination with direct `WHERE` clauses. The index on `(created_at DESC, id DESC)` powers both cursor navigation and filtered queries.

> **Tradeoff**: Keyset pagination (direct WHERE) is faster but exposes internal column values. Deferred join (offset on ID-only, then join) helps but still scans early rows. Covering index on offset pagination is a bandage — the fundamental O(N) scan cost remains for deep pages.

> **Cross-reference**: [SQL Query Optimization](databases/sql-query-optimization.md)

---

## sdi-106: Backpressure via Producer Throttling

| | |
|:---|:---|
| **Problem** | SQS order processing: 200 orders/min normal, 4,000/min on Black Friday. Queue: 80K messages and growing, DB CPU 95%. Producers create messages faster than consumers can safely process them. |
| **Key Concept** | Backpressure means reducing the incoming flow, not only increasing outgoing capacity. Rate-limit the producer (Token Bucket/Sliding Window at the API Gateway or publisher middleware). Use queue depth as the throttling signal. The customer-facing checkout can remain responsive — rate-limit only the background event publisher, not the order-acceptance endpoint. |

> **Strategy**: Separate the customer-facing order acceptance (write to DB, return success) from the background event publisher (CDC/polling → SQS). Throttle the background publisher using queue depth as signal. Consumers process backlog at a sustainable rate while the DB recovers.

> **Tradeoff**: Scaling consumers horizontally when the DB is at 95% CPU sends even more concurrent work to an overloaded database. Visibility timeouts and DLQs handle failure, not backpressure — the producer rate is unchanged. SQS delay queues postpone visibility but don't reduce the incoming rate — messages surge when delays expire.

> **Cross-reference**: [Backpressure](../../reference-dictionary/messaging.md#backpressure), [Message Brokers & Kafka](messaging/kafka-consumer-mistakes.md)

---

## sdi-107: Outbox Pattern for Cache Consistency

| | |
|:---|:---|
| **Problem** | Profile update: PostgreSQL write succeeds but Redis invalidation fails. Redis serves stale data for 10 minutes. Three incidents in one month from partial dual-write failures. |
| **Key Concept** | Outbox Pattern: commit the DB update and a cache-update event in one atomic PostgreSQL transaction. A separate consumer reads the outbox event and updates/invalidates Redis. If the consumer crashes, the event persists and can be retried. If Redis is down, events queue until recovery. |

> **Strategy**: Replace dual-write (DB then Redis) with transactional outbox. One atomic transaction: `UPDATE profile + INSERT INTO outbox (cache_update_event)`. Consumer processes outbox events, updating Redis with retry support. Provides replay capability when Redis recovers from an outage.

> **Tradeoff**: Write-through couples the write path to Redis availability (if Redis is slow/down, profile updates fail). Write-behind makes Redis the temporary source of truth (risk of data loss). Write-around avoids dual-write risk but can serve stale data until TTL expires and reduces cache hit ratio for frequently updated data.

> **Cross-reference**: [Outbox Pattern](../../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [Caching & Redis Internals](caching/redis-internals.md)

---

## sdi-108: RAG for Knowledge Freshness

| | |
|:---|:---|
| **Problem** | Customer support chatbot: 15% of answers wrong due to outdated product knowledge. Knowledge base changes weekly (new pricing, features, deprecations). Mid-sized startup, no budget for custom model training. |
| **Key Concept** | RAG (Retrieval-Augmented Generation): convert knowledge base into embeddings → store in vector DB → at query time, retrieve top relevant chunks → add to prompt. The model's reasoning ability is separated from the knowledge it uses. Updating facts is a data-pipeline change, not a retraining cycle. |

> **Strategy**: Chunk product docs → create embeddings → store in vector database. At query time: embed the question → retrieve top-K relevant document chunks → add to LLM context → generate answer using current information. Pricing changes on Monday? Update the doc, regenerate embeddings — bot uses new info immediately.

> **Tradeoff**: Fine-tuning stores knowledge in model weights — needs repeated training cycles when docs change weekly, risks catastrophic forgetting. Fine-tuning + RAG is powerful but overkill as a first step (months of work for a mid-sized startup). Prompt engineering alone can't fit hundreds of pages of docs into context windows.

> **Cross-reference**: [RAG](../../reference-dictionary/ai-ml-llm.md#retrieval-augmented-generation), [AI/ML Infrastructure](ai-ml-infrastructure/ai-ml-infrastructure.md)

---

## sdi-109: Qdrant for High-Concurrency Vector Search

| | |
|:---|:---|
| **Problem** | B2B SaaS semantic search: 4M documents, 1,536-dim embeddings (~24GB), 300 QPS normal, 900 QPS peak. Target: P99 < 100ms. Need tenant/workspace filtering during vector search (not post-filtering). |
| **Key Concept** | Qdrant: Rust-based vector DB with HNSW index optimized for high-throughput ANN search. Native payload filtering applies metadata constraints during vector search (not after) — retrieves results from the correct workspace without recall loss from post-filtering. |

> **Strategy**: Self-host Qdrant for control over HNSW parameters (`m`, `ef_construction`) and memory/disk indexing. Apply `tenant_id`/`workspace_id` filter during ANN search. At 4M vectors and 300 QPS, pgvector's HNSW competes with transactional workload for buffer pool, CPU, and I/O.

> **Tradeoff**: pgvector works for <500K vectors and low concurrency — beyond that, it competes with transactional workload. Pinecone is fully managed but serverless pricing at sustained 300-900 QPS becomes expensive with proprietary lock-in. Weaviate's Kubernetes footprint is heavier than needed for dense-vector search with metadata filtering.

> **Cross-reference**: [Vector Databases](../../reference-dictionary/ai-ml-llm.md#vector-database), [AI/ML Infrastructure](ai-ml-infrastructure/ai-ml-infrastructure.md)

---

## sdi-110: DAG-Based Multi-Agent Orchestration

| | |
|:---|:---|
| **Problem** | Four-agent pipeline (Planner, Researcher, Coder, Reviewer): Researcher sometimes finishes before Planner → Coder starts with incomplete context. Reviewer finds problems but no retry path to Coder. One agent timeout blocks the entire workflow for 40s. No visibility into which agent failed. |
| **Key Concept** | DAG-based execution: model the workflow as a directed acyclic graph. Planner + Researcher → Coder → Reviewer, with Reviewer → Coder retry edge. Independent nodes run in parallel; dependent nodes wait for all upstream completions. Each node has its own timeout. Tools: LangGraph, Temporal, AWS Step Functions, Prefect, Dagster. |

> **Strategy**: Make dependencies explicit in a DAG. Planner and Researcher run in parallel; Coder starts only when both complete. Reviewer→Coder retry is a defined graph edge, not ad-hoc logic. Each node timeout is independent. Execution traces show every node's status, duration, and retry history.

> **Tradeoff**: Centralized orchestrator is sequential by default — parallel execution requires manual code. Choreography via event bus makes "wait for these two agents" hard to express — agents handle orchestration logic themselves, increasing coupling. Supervisor pattern adds latency (every decision passes through the meta-agent) and becomes a central point of failure.

> **Cross-reference**: [Multi-Agent Systems](../../reference-dictionary/ai-ml-llm.md#multi-agent), [Agentic AI](agentic-ai/enterprise-strategic-systems.md)

---

## sdi-111: S3 for Shared Object Storage at Scale

| | |
|:---|:---|
| **Problem** | File upload service: 10TB today, 100TB in 12 months. Upload Service, ML Pipeline, and Audit Service all need access to the same files. File sizes range from 5KB profile pictures to 2GB video exports. |
| **Key Concept** | Amazon S3: managed object storage with no capacity planning. Store S3 object key in PostgreSQL; all services access files by key. At 100TB: ~$2,300/month. Includes versioning, encryption, access control, audit logging, lifecycle policies (auto-archive to Glacier), and S3 event triggers for the ML pipeline. |

> **Strategy**: Upload file → store S3 key → other services read the same object. Lifecycle policies move older files to cheaper storage tiers. S3 events trigger downstream processing automatically. S3 is the default choice for cloud-based file services — move away only when object storage semantics don't fit.

> **Tradeoff**: EBS is a block disk attached to one EC2 instance — doesn't work with horizontal scaling or multi-service access. EFS provides shared POSIX filesystem but at ~$30,000/month for 100TB (13× more than S3) — pays for filesystem behavior the app doesn't need. Self-hosted MinIO shifts reliability responsibility to your team (disk failures, replication, backups, 3am incidents).

> **Cross-reference**: [Azure Services](../../reference-dictionary/azure-services.md)
