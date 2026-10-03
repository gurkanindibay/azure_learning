---
type: Reference
title: "Message Brokers & Asynchronous Messaging"
description: "General messaging patterns: choreography, orchestration, fanout strategies, deduplication, Redis Streams, competing consumers, and delivery patterns."
generated: { by: process:okf-migrate, at: 2026-10-03T10:17:00+03:00 }
---

# Message Brokers & Asynchronous Messaging

> **Domain**: General messaging patterns, delivery strategies, deduplication, fanout, and asynchronous communication.
> **Parent**: [Reference Dictionary](index.md)
> **Kafka-specific terms**: See [Apache Kafka Dictionary](kafka.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Client-Side Deduplication | [`#client-side-deduplication`](#client-side-deduplication) |
| Batch Processing vs Stream Processing | [`#batch-processing-vs-stream-processing`](#batch-processing-vs-stream-processing) |
| Delivery Cursor | [`#delivery-cursor`](#delivery-cursor) |
| Communication Pattern | [`#communication-pattern`](#communication-pattern) |
| Choreography | [`#choreography`](#choreography) |
| Orchestration | [`#orchestration`](#orchestration) |
| Configuration Server | [`#configuration-server`](#configuration-server) |
| Config Server | [`#config-server`](#config-server) |
| Redis Streams | [`#redis-streams`](#redis-streams) |
| Per-Device Inbox | [`#per-device-inbox`](#per-device-inbox) |
| Competing Consumers | [`#competing-consumers`](#competing-consumers) |
| Atomic Deduplication | [`#atomic-deduplication`](#atomic-deduplication) |
| Deduplication Store | [`#deduplication-store`](#deduplication-store) |
| Deduplication Window | [`#deduplication-window`](#deduplication-window) |
| Fanout on Write | [`#fanout-on-write`](#fanout-on-write) |
| Fanout on Read | [`#fanout-on-read`](#fanout-on-read) |
| Hybrid Fanout | [`#hybrid-fanout`](#hybrid-fanout) |
| Dual-Write Migration | [`#dual-write-migration`](#dual-write-migration) |
| Global Secondary Index | [`#global-secondary-index`](#global-secondary-index) |
| Three-Layer Deduplication | [`#three-layer-deduplication`](#three-layer-deduplication) |
| Worker Self-Throttling | [`#worker-self-throttling`](#worker-self-throttling) |
| Progressive Enqueuing | [`#progressive-enqueuing`](#progressive-enqueuing) |
| Bounded Deduplication TTL | [`#bounded-deduplication-ttl`](#bounded-deduplication-ttl) |

---

## Client-Side Deduplication

A technique where the **message sender generates a unique message ID** and uses it as an idempotency key. If the send operation times out, the client retries with the **same ID** — enabling the server and receiver to recognize and discard duplicates.

### Key Characteristics
- **Unique ID per message**: Generated client-side (UUID, content hash, or sequence number) before the first send attempt
- **Same ID on retry**: The critical invariant — retries must reuse the original ID, not generate a new one
- **First layer of defense**: Prevents re-insertion at the server and re-display at the receiver

### When to Use
- Any messaging or API system where network timeouts can cause senders to retry
- Multi-device messaging platforms (WhatsApp, Telegram, Signal)
- Payment APIs and financial transactions where duplicate submission must be prevented

### When NOT to Use
- Fire-and-forget telemetry where duplicates are harmless
- Systems where the server assigns message IDs and clients never retry


## Batch Processing vs Stream Processing

**Batch processing** collects data and processes it together at scheduled or trigger-based intervals. **Stream processing** evaluates data continuously as it arrives, reducing result latency while requiring explicit handling for unbounded state, event time, and recovery.

### Key Characteristics
- Batch jobs optimize efficiency for finite or accumulated datasets.
- Stream processors trade simpler bounded execution for continuous low-latency results.
- Hybrid systems often use streaming for operational decisions and batch processing for reconciliation or historical recomputation.

### When to Use
- Use batch processing for periodic reports, large finite transformations, and workloads where latency can be delayed.
- Use stream processing for continuously changing results, alerts, and time-sensitive decisions.

### When NOT to Use
- Do not use streaming for a small, finite job whose latency and state requirements do not justify a continuously running system.
- Do not use batch processing when stale results would violate the product requirement.

### Also see
- [Event-Time](#event-time) · [Watermarking](#watermarking) · [Apache Flink](#apache-flink)

### Also see
- [Idempotent Consumer](#idempotent-consumer) · [At-Least-Once Semantics](#at-least-once-semantics) · [Producer Acknowledgement](#producer-acknowledgement) · [Idempotency](cqrs-event-driven.md#idempotency)

---


## Delivery Cursor

A **server-side pointer** that tracks the last message successfully delivered to a specific client, enabling the client to catch up after reconnection without re-receiving already-processed messages. The server advances the cursor only after confirming delivery or receiving an ACK from the client.

### Key Characteristics
- **Per-client, per-conversation**: Each recipient has independent cursors for each conversation or channel
- **Monotonic**: Cursors only move forward; a message with ID ≤ cursor value is already delivered
- **Foundation for offline catch-up**: Clients request messages since their last cursor position after reconnecting

### When to Use
- Real-time messaging with multi-device support and offline catch-up
- Any at-least-once delivery system where the server must track per-client progress
- Replacement for per-message ACKs when batch acknowledgment is preferred

### When NOT to Use
- Pub/sub systems where subscribers are ephemeral and don't need catch-up (e.g., live sensor data)
- Systems where the client can independently track and request missing ranges (Kafka consumer with offset management)

### Also see
- [At-Least-Once Semantics](#at-least-once-semantics) · [Per-Device Inbox](#per-device-inbox) · [Offset Commit](#offset-commit) · [Client-Side Deduplication](#client-side-deduplication)

---


## Communication Pattern

A deliberate choice of how components exchange requests or events, including synchronous request-response and asynchronous message-based communication. The choice should follow response-time, coupling, consistency, and throughput requirements.

### Key Characteristics
- Synchronous calls provide an immediate result but couple latency and availability
- Asynchronous messages decouple producers and consumers but require eventual-consistency handling
- The contract includes delivery, ordering, retry, timeout, and failure semantics

### When to Use
- To make communication trade-offs explicit at service boundaries
- When deciding between REST/gRPC and events or queues for a workflow step

### When NOT to Use
- As a technology-first label without identifying the caller's response and consistency needs

### Also see
- [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture) · [Message Ordering](#message-ordering) · [Saga](data-concurrency.md#saga-pattern)

---


## Choreography

A distributed workflow style in which services react to domain events and publish subsequent events without a central coordinator directing every step.

### Key Characteristics
- Each participant owns its local reaction and completion event
- Coupling is expressed through event contracts rather than direct calls
- Failure handling and workflow visibility must be designed explicitly

### When to Use
- Simple, stable workflows where participants can react independently
- Event-driven integrations that benefit from loose temporal coupling

### When NOT to Use
- Long, branching workflows where global progress and compensation are difficult to observe
- When no team can own event contracts and operational tracing

### Also see
- [Orchestration](#orchestration) · [Saga](data-concurrency.md#saga-pattern) · [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture)

---


## Orchestration

A distributed workflow style in which a coordinator directs service actions, tracks progress, and decides how failures are compensated.

### Key Characteristics
- Centralizes workflow state and sequencing
- Makes retries, timeouts, and compensation visible in one place
- The coordinator can become a coupling or availability boundary

### When to Use
- Long-running, branching, or compensation-heavy workflows
- Processes that need explicit progress, auditability, or operator control

### When NOT to Use
- Simple independent reactions where a coordinator adds more coupling than clarity
- Without durable coordinator state and idempotent command handling

### Also see
- [Choreography](#choreography) · [Saga](data-concurrency.md#saga-pattern) · [Idempotency](cqrs-event-driven.md#idempotency)

---


## Configuration Server

A centralized service or managed system that stores, versions, and distributes runtime configuration to multiple application services.

### Key Characteristics
- Separates configuration from application binaries
- Supports versioning, environment-specific values, and controlled refresh
- Requires access control, validation, secret handling, and rollback safeguards

### When to Use
- Many services share environment-specific settings or need coordinated configuration changes
- Configuration must be audited and updated without rebuilding every service

### When NOT to Use
- Small applications where local, version-controlled configuration is simpler and sufficient
- Without a plan for startup failure, stale values, or a bad configuration's blast radius

### Also see
- [Configuration Propagation](observability.md#configuration-propagation) · [Service Discovery](architecture-patterns.md#service-discovery)

**Also known as**: Config Server.

---


## Config Server

An alternate name for [Configuration Server](#configuration-server), the centralized store and distribution mechanism for runtime configuration.

**Also see**: [Configuration Server](#configuration-server)

---


## Redis Streams

A Redis data type that models an append-only log with consumer-group semantics, allowing durable, ordered, fault-tolerant message processing inside Redis.

### Key Characteristics
- Entries are ordered and identified by time-based IDs
- Consumer groups track pending entries and support explicit ACKs
- Memory is bounded via trimming / `MAXLEN`

### When to Use
- Per-device inboxes and lightweight message queues
- Ordered event streams that fit in memory
- Scenarios where a full Kafka cluster is too heavy

### When NOT to Use
- Long-term event storage (prefer Kafka or an event store)
- Very large payloads (use the claim-check pattern)

### Also see
- [Per-Device Inbox](#per-device-inbox) · [Kafka vs RabbitMQ](#kafka-vs-rabbitmq) · [At-Least-Once Semantics](#at-least-once-semantics)

---


## Per-Device Inbox

A messaging pattern that gives each recipient device its own durable queue so delivery and read progress can be tracked independently per device.

### Key Characteristics
- One queue or stream per user-device pair
- Enables offline catch-up and multi-device synchronization
- Usually paired with at-least-once delivery and client-side deduplication

### When to Use
- Real-time messaging with multi-device support
- Push-notification buffering for offline clients

### When NOT to Use
- Simple broadcast use cases where all consumers share one stream
- Systems that can tolerate lossy fan-out

### Also see
- [Redis Streams](#redis-streams) · [At-Least-Once Semantics](#at-least-once-semantics) · [Message Ordering](#message-ordering)

---


## Competing Consumers

Multiple consumers **pull from a single queue** for load-balanced processing. If one consumer is slow, others pick up the slack. Core pattern for scaling message processing horizontally.

**Also see**: [Messaging](messaging.md)

---


## Atomic Deduplication

A pattern that prevents race conditions in idempotent message processing by using a database `INSERT` with a `UNIQUE` constraint as the deduplication check, rather than a non-atomic check-then-act sequence.

```sql
-- Atomic: only one consumer succeeds
INSERT INTO processed_events (event_id) VALUES ('EVT-8A72F1');
-- UNIQUE(event_id) constraint ensures atomicity
```

### Key Characteristics
- **Database-enforced atomicity**: The database itself (not application logic) guarantees that only one INSERT for a given Event ID succeeds
- **Eliminates check-then-act races**: No gap between "check if processed" and "mark as processed" — they are the same operation
- **Constraint violation = already processed**: Consumers treat the UNIQUE constraint error as a signal to skip processing
- **Portable across stores**: Works with any store that supports atomic conditional inserts (SQL UNIQUE, Redis `SETNX`, DynamoDB conditional put)

### When to Use
- At-least-once consumers where concurrent instances may process the same event
- High-throughput systems where lock-based deduplication would create contention
- Any consumer that must be horizontally scalable while maintaining idempotency

### When NOT to Use
- When the deduplication store does not support unique constraints or conditional writes
- When the business update and dedup record are in different transactional scopes (use Outbox Pattern instead)
- Single-instance consumers where a simple in-memory set suffices

### Also see
- [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---


## Deduplication Store

A **shared, external data store** used by idempotent consumers to track which events have already been processed. It serves as the single source of truth across all consumer instances so that duplicate deliveries are recognized and skipped regardless of which instance receives the redelivery.

### Key Characteristics
- **Shared across instances**: All consumers in a group read and write to the same store — a local in-memory cache is insufficient at scale
- **Atomic conditional inserts**: Typically backed by a database with UNIQUE constraints (relational DB, Redis `SETNX`, DynamoDB conditional put)
- **Retention-bounded**: Entries are purged after a configurable window that exceeds Kafka's maximum redelivery window
- **Per-event granularity**: Keyed by Event ID, not by message offset or partition

### When to Use
- Horizontally scaled consumer groups where duplicate events may land on any instance after a rebalance
- At-least-once messaging systems (Kafka, Event Hubs, Service Bus) where redelivery is a normal occurrence
- Payment, inventory, or order workflows where double-processing is unacceptable

### When NOT to Use
- Single-instance consumers where an in-memory `HashSet<EventId>` suffices
- Systems with true exactly-once delivery guarantees (rare in practice)
- When the deduplication store itself becomes a bottleneck (consider partitioning by Event ID)

### Also see
- [Atomic Deduplication](#atomic-deduplication) · [Event ID](../reference-dictionary/cqrs-event-driven.md#event-id) · [Idempotent Consumer](../reference-dictionary/messaging.md#idempotent-consumer) · [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern)

---


## Deduplication Window

The **time period during which a messaging system retains deduplication state** to detect and discard duplicate messages. Infrastructure-level deduplication (Kafka idempotent producer, SQS FIFO) only works within this bounded window — once it expires, duplicates can pass through undetected.

### Key Characteristics
- **Bounded by retention**: The deduplication window should match or exceed the message retention period (e.g., Kafka retains 7 days → dedup keys kept for 7 days)
- **System-specific**: SQS FIFO has a fixed 5-minute window; Kafka's window is configurable via `max.in.flight.requests` and producer session lifetime
- **Cleanup required**: Stale deduplication records must be purged via scheduled jobs — unbounded growth degrades broker performance
- **Not a substitute for application idempotency**: The window can expire; application-layer idempotency with durable storage is the only permanent guarantee

### When to Use
- Understanding the limits of broker-level deduplication guarantees
- Sizing TTLs for Redis-based dedup stores at the application layer
- Designing cleanup policies for deduplication state in long-running systems

### When NOT to Use
- As the sole deduplication mechanism — always pair with application-layer idempotency
- When messages may be legitimately replayed beyond the window (event sourcing, audit replays)

### Also see
- [Deduplication Store](#deduplication-store) · [Idempotent Producer](#idempotent-producer) · [At-Least-Once Semantics](#at-least-once-semantics)

---


## Fanout on Write

A distribution model where a new event is propagated to all consumers at write time. In social media, posting a message writes the post ID into every follower's timeline cache immediately. Reads are fast because results are pre-computed.

### Key Characteristics
- **Read-optimized**: Feed loads are O(1)
- **Write amplification**: Each post generates N writes for N followers
- **Latency to readers**: Near zero (data is already present)

### When to Use
- Small-to-medium follower counts
- Read latency is the dominant SLO

### When NOT to Use
- Celebrity accounts with millions of followers (write amplification explodes)
- Systems where producers significantly outnumber consumers

**Also see**: [Fanout on Read](#fanout-on-read) · [Hybrid Fanout](#hybrid-fanout) · [Timeline Cache](../reference-dictionary/caching.md#timeline-cache)

---


## Fanout on Read

A distribution model where events are stored centrally and consumers collect relevant items at read time. In social media, a follower loads their feed by fetching recent posts from each account they follow. Writes are cheap; reads are more expensive.

### Key Characteristics
- **Write-optimized**: Each post generates O(1) writes
- **Read cost grows with followees**: Feed load is O(followees)
- **No write amplification**: Ideal for celebrity producers

### When to Use
- Highly skewed graphs where a few producers have massive audiences
- Systems where reads are infrequent relative to writes

### When NOT to Use
- Feeds with strict latency SLOs and many followees
- Uniform graphs where push would be simpler and faster

**Also see**: [Fanout on Write](#fanout-on-write) · [Hybrid Fanout](#hybrid-fanout)

---


## Hybrid Fanout

A distribution model that combines fanout-on-write for normal users and fanout-on-read for high-follower celebrities. Balances read latency against write amplification by choosing the fanout strategy per producer based on follower count.

### Key Characteristics
- **Threshold-based**: Users below a follower count are pushed; celebrities are pulled
- **Best of both worlds**: Fast reads for most users, bounded write amplification
- **Operational complexity**: Requires separate code paths and caches

### When to Use
- Social networks with highly skewed follower distributions
- Any fanout problem where neither pure push nor pure pull is affordable

### When NOT to Use
- Simple graphs where one strategy clearly dominates
- When operational complexity outweighs the fanout savings

**Also see**: [Fanout on Write](#fanout-on-write) · [Fanout on Read](#fanout-on-read) · [Celebrity Cache](../reference-dictionary/caching.md#celebrity-cache)

---


## Dual-Write Migration

A database migration strategy where the application writes to both the old (monolith) and new (sharded) systems simultaneously during a transition period. Dual-write enables zero-downtime migration with instant rollback capability — if the new system misbehaves, traffic is routed back to the old system without data loss.

### Key Characteristics
- **Concurrent writes**: Every write operation targets both old and new systems in the same request path
- **Failure handling**: If the new-system write fails, the old-system write is rolled back or the request is rejected — data consistency across systems is preserved
- **Four-phase process**: Dual-write → batch backfill of historical data → real-time reconciliation → controlled traffic rollout (1% → 10% → 50% → 100%)
- **Rollback safety**: As long as dual-write is active, reverting is a config change, not a data migration

### When to Use
- Migrating a live, high-traffic database table to a sharded architecture without downtime
- Any migration where a big-bang cutover is unacceptable due to 24/7 availability requirements

### When NOT to Use
- When the old and new systems have incompatible data models that cannot be reconciled in real time
- Low-traffic systems where a brief maintenance window is acceptable and simpler
- When write latency doubling (both systems must be written) exceeds the application's latency budget

### Also see
- [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern) · [Dual-Write Problem](../reference-dictionary/cqrs-event-driven.md#dual-write-problem) · [Strangler Fig](../reference-dictionary/architecture-patterns.md#strangler-fig) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)

---


## Global Secondary Index

An index in a distributed database that spans all shards and enables efficient queries on non-shard-key columns without broadcasting to every shard. Unlike a local secondary index (which exists within a single shard), a global secondary index maintains its own sharded storage, mapping the indexed column values to the primary keys and shard locations.

### Key Characteristics
- **Cross-shard coverage**: Index entries are distributed across all shards independently of the base table's sharding scheme
- **Asynchronous maintenance**: Index updates may lag behind base-table writes, introducing eventual consistency
- **Middleware or database-native**: Implemented by ShardingSphere, Spanner, DynamoDB GSIs, or Cosmos DB composite indexes
- **Storage overhead**: The index consumes additional disk and memory proportional to indexed column cardinality

### When to Use
- Query patterns that frequently filter by a non-shard-key column (e.g., `merchant_id` in a `user_id`-sharded orders table)
- When the alternative — broadcasting queries to all shards and merging results — exceeds latency or resource budgets

### When NOT to Use
- When the indexed column has very low cardinality (e.g., `status`) — the index provides little filtering benefit
- When write throughput is the bottleneck and the index update overhead is unacceptable
- When cross-shard queries are rare and scatter-gather is acceptable

### Also see
- [Sharding](data-architecture.md#sharding) · [Shard Key](data-concurrency.md#shard-key) · [Cross-Shard Query](cqrs-event-driven.md#cross-shard-query)

---


---


## Three-Layer Deduplication

A defense-in-depth pattern for distributed messaging systems that applies deduplication at three independent layers: **client-side** (idempotency key on send), **server-side** (unique constraint on message ID), and **receiver-side** (seen-ID cache). Each layer protects against a different failure mode — no single layer can catch all duplicates.

### Key Characteristics
- **Client layer**: Generates a unique message ID and reuses it on retry. Prevents the sender from creating duplicate payloads during timeout-based retries.
- **Server layer**: Uses the message ID as a primary key or unique index. Duplicate INSERT attempts fail deterministically at the database level.
- **Receiver layer**: Maintains a short-lived LRU cache (with TTL) of recently processed message IDs. Discards incoming messages whose ID is already present.
- **Defense in depth**: If layer 1 misses (e.g., client crash and reinstall), layer 2 catches it. If layer 2 misses (e.g., server replication lag), layer 3 catches it.

### When to Use
- Real-time messaging platforms with at-least-once delivery guarantees (WhatsApp, Telegram, Signal)
- Payment processing and financial systems where duplicate transactions are unacceptable
- Any system where network retries can produce semantically identical requests that must not be processed twice

### When NOT to Use
- Append-only telemetry or logging where occasional duplicates are harmless
- Systems with strict low-latency requirements where the storage/check overhead of all three layers is prohibitive — use two layers instead
- Stateless request-response APIs where idempotency keys alone at the server layer suffice

### Also see
- [Client-Side Deduplication](#client-side-deduplication) · [Delivery Cursor](#delivery-cursor) · [Atomic Deduplication](#atomic-deduplication) · [Deduplication Store](#deduplication-store) · [Idempotent Consumer](#idempotent-consumer) · [Idempotency](cqrs-event-driven.md#idempotency)

---


## Worker Self-Throttling

A client-side rate-limiting and traffic-shaping pattern where asynchronous consumer workers actively pace their outbound execution rates to remain strictly within downstream provider limits (such as third-party push notification, SMS, or payment gateways), rather than consuming from the queue at maximum compute speed.

### Key Characteristics
- **Client-side rate limiting**: Workers embed token bucket or leaky bucket limiters to throttle outbound HTTP/RPC dispatch.
- **Queue as healthy buffer**: A growing queue depth is treated as safe, expected backpressure rather than a trigger to blindly spin up more compute.
- **Provider account protection**: Prevents HTTP 429 (Too Many Requests), connection bans, or gateway account suspensions caused by over-aggressive concurrent egress.

### When to Use
- Asynchronous worker fleets making outbound calls to rate-limited third-party APIs (APNs, FCM, Twilio, SendGrid).
- High-fanout background workloads where upstream queue volume exceeds downstream recipient acceptance limits.

### When NOT to Use
- Internal services that support elastic autoscaling and explicit HTTP backpressure headers.
- Workloads where the bottleneck is internal compute rather than external egress quotas.

### Also see
- [Backpressure](resilience.md#backpressure) · [Message Batching](#message-batching) · [Dead Letter Queue (DLQ)](#dead-letter-queue-dlq) · [Rate Limiting](api-design.md#rate-limiting)

---


## Progressive Enqueuing

An architectural pattern for massive fanout or batch operations (e.g. 100M+ user campaigns) where individual jobs are not materialized and dumped into the message queue all at once; instead, the workload is stored as a high-level definition and a background generator service progressively materializes and enqueues small batches over time.

### Key Characteristics
- **Campaign definition decoupling**: The trigger persists metadata and segmentation queries rather than hundreds of millions of individual task records.
- **Smoothed broker ingestion**: Prevents extreme spikes in message broker disk utilization, partition queue memory, and replication overhead.
- **Steady-state processing**: Converts an unmanageable instant burst into a continuous, controllable flow of work.

### When to Use
- Mega-scale push notification campaigns, marketing email blasts, or batch statement generation targeting tens to hundreds of millions of users.
- Large-scale media transcoding or bulk ETL migrations where upfront job creation would overwhelm message brokers.

### When NOT to Use
- Real-time emergency broadcast systems where every recipient must be targeted simultaneously with minimum latency.
- Small-to-medium fanout operations (<1M items) where standard queue durability and partitioning handle the burst without issue.

### Also see
- [Message Batching](#message-batching) · [Partition](#partition) · [Consumer Lag](#consumer-lag) · [Backpressure](resilience.md#backpressure)

---


## Bounded Deduplication TTL

An operational configuration strategy for consumer-side deduplication stores where processed message identifiers are assigned a finite time-to-live (TTL) sized strictly to exceed the maximum plausible network retry and consumer rebalance horizon, guaranteeing idempotency during active delivery while preventing unbounded storage growth.

### Key Characteristics
- **Bounded Storage Footprint**: Constrains memory and disk usage in distributed caches (e.g., Redis) or database tables to a steady-state volume proportional to current event throughput rather than cumulative historical volume.
- **Redelivery Horizon Sizing**: The TTL duration is derived from the system's operational parameters: $\text{TTL} > \text{MaxProducerRetryWindow} + \text{MaxConsumerRebalanceTimeout} + \text{ConsumerLagMargin}$ (typically 24 to 72 hours).
- **Auto-Eviction**: Relies on database or cache native TTL expiry mechanisms (e.g., Redis key expiration, DynamoDB/Cosmos DB TTL) to prune obsolete records without requiring batch cleanup cron jobs.
- **Layered Defense**: Accompanied by domain version checks or aggregate guards to handle ultra-long-tail duplicates that arrive after the TTL expires.

### When to Use
- High-throughput message consumer pipelines processing millions of events daily.
- Distributed deduplication stores hosted in memory-constrained databases (Redis, Hazelcast) or billable-per-GB serverless databases.
- At-least-once messaging systems where retries and rebalances resolve within hours.

### When NOT to Use
- Financial audit logs and regulatory ledgers where records of processed transactions must be retained permanently.
- Systems that lack aggregate-level version guards and regularly perform manual offset rewinds back weeks or months.

### Also see
- [Idempotent Consumer](#idempotent-consumer) · [Atomic Deduplication](#atomic-deduplication) · [Deduplication Store](#deduplication-store) · [Idempotency State Explosion](cqrs-event-driven.md#idempotency-state-explosion)

---

