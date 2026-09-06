---
type: System Design
title: "Kafka Performance & Integration Patterns — Production Deep-Dive Key Takeaways"
description: "Production-depth insights from the Kafka performance and integration series: orphaned S3 object cleanup in Claim Check, lazy loading vs presigned URL decision, S3 lifecycle cost management, local RocksDB state for zero-network stream-table joins, late-arriving data grace periods, compensating transaction design in Saga Choreography, and choreography vs orchestration tradeoffs."
generated: { by: process:okf-migrate, at: 2026-06-26T00:00:00Z }
---

# 56. Kafka Performance & Integration Patterns — Production Deep-Dive Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md)
> **Overview (Part 1)**: [Kafka Design Patterns Overview — broker-24 to broker-34](messaging/kafka-design-patterns.md)
> **Part 2**: [Kafka Reliability & Ordering — broker-35 to broker-42](messaging/kafka-reliability-ordering.md)
> **Part 3**: [Kafka Data & State — broker-43 to broker-51](messaging/kafka-data-state.md)
> **Purpose**: Extract production-depth engineering insights from the final part of the series, covering Claim Check, Stream-Table Duality, and Saga Choreography.

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md)
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Messaging](../../reference-dictionary/messaging.md), [Data & Concurrency](../../reference-dictionary/data-concurrency.md)
> **Taxonomy Reference**: §3 Integration & Communication Architecture, §4.3 Streaming & Real-Time Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [broker-52](#broker-52) | S3 upload succeeds but Kafka send fails — payload stranded with no consumer | Record orphan in DynamoDB immediately; Lambda cleanup job deletes stale objects daily |
| [broker-53](#broker-53) | Consumer must load a 200 MB file into memory to process a Claim Check message | Threshold decision: < 50 MB → download payload; ≥ 50 MB → generate presigned URL for direct streaming |
| [broker-54](#broker-54) | Claim Check payloads accumulate indefinitely, increasing S3 costs | S3 lifecycle: Glacier at 30 days, delete at 90 days; S3 is ~23× cheaper per GB than MSK broker storage |
| [broker-55](#broker-55) | Stream-table join requires a database call on every event — latency and fan-out | Kafka Streams materialises the KTable in local RocksDB; join is a local lookup, zero network calls |
| [broker-56](#broker-56) | Late-arriving events miss their window and are silently dropped | Add a `grace` period to windowed aggregations to accept events that arrive up to N seconds late |
| [broker-57](#broker-57) | Compensating transactions in Saga fail because services only listen for the immediately preceding failure event | Each service must subscribe to ALL upstream failure events that require its compensation, not just the adjacent one |
| [broker-58](#broker-58) | Pure choreography becomes untraceable as saga step count grows | Use AWS Step Functions orchestration for sagas with > 5 steps or complex branching; choreography for simple linear flows |

---

## broker-52: Orphaned S3 Object Cleanup in Claim Check

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Claim Check

| | |
|:---|:---|
| **Problem** | Claim Check producers upload the payload to S3 first, then send a Kafka message referencing it. If the Kafka send fails (timeout, broker unavailable), the payload sits in S3 indefinitely with no consumer ever fetching it — consuming storage and creating a compliance risk for PII data. |
| **Root cause** | S3 upload and Kafka send are two independent operations with no atomic coordination. Failure between the two leaves the system in an inconsistent state. |

**Strategy**: Implement an explicit orphan-tracking mechanism as a compensating step on Kafka failure:

```python
try:
    future = producer.send(topic, key=key, value=claim_check_message)
    future.get(timeout=10)
except Exception:
    # S3 upload succeeded but Kafka failed — record the orphan
    orphan_table.put_item(Item={
        's3_key': s3_key,
        'aggregate_id': aggregate_id,
        'orphaned_at': datetime.utcnow().isoformat(),
        'reason': 'kafka_send_failed'
    })
    raise
```

Deploy a **Lambda cleanup function** (triggered daily via EventBridge) that:
1. Lists S3 objects older than 24 hours under the `attachments/` prefix
2. Checks the orphan tracking table for each object
3. Deletes any object that is recorded as orphaned (never referenced in a successful Kafka message)

Alternatively, use an S3 `temp/` prefix with a 1-day lifecycle policy for all uploads until the Kafka send succeeds, then move the object to the permanent prefix.

| Tradeoff | Detail |
|:---|:---|
| **Orphan tracking overhead** | One DynamoDB write per failed Kafka send — negligible at normal failure rates |
| **Cleanup latency** | Daily Lambda cleanup means orphaned PII data can persist up to 24 hours |
| **Two-write atomicity** | Still not atomic; orphan record could also fail to write — accept this as a best-effort mechanism |

> **Also see**: [Claim Check Overview — broker-27](messaging/kafka-design-patterns.md#broker-27), [DLQ — broker-28](messaging/kafka-design-patterns.md#broker-28)
> **Dictionary**: [Claim Check](../../reference-dictionary/messaging.md#claim-check)

---

## broker-53: Lazy Loading vs Presigned URL Decision in Claim Check

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Claim Check

| | |
|:---|:---|
| **Problem** | A Claim Check consumer that downloads every payload into memory before processing will OOM on large files (100 MB video, 500 MB ML weights) and add unnecessary latency for every message, even those that only need metadata inspection. |
| **Root cause** | Treating all claim checks identically regardless of payload size leads to either memory exhaustion (always download) or missed optimisation (always presign). |

**Strategy**: Apply a **size-based dispatch** in the consumer:

```python
if claim_check.get('size_bytes', 0) < 50 * 1024 * 1024:  # < 50 MB
    # Download directly — fast path for small payloads
    payload = download_payload(claim_check)
    handler(metadata, payload, claim_check)
else:
    # Large file — generate time-limited presigned URL
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': s3_bucket, 'Key': s3_key},
        ExpiresIn=3600  # 1 hour
    )
    handler(metadata, None, claim_check, presigned_url=url)
```

The presigned URL lets downstream systems (video processors, ML inference engines) **stream directly from S3** without routing the bytes through the consumer.

| Decision dimension | Download | Presigned URL |
|:---|:---|:---|
| Payload size | < ~50 MB | ≥ 50 MB |
| Consumer memory | Must fit in heap | Only URL string in heap |
| Latency | Adds S3 download RTT | Consumer delegates to downstream |
| Use case | PDF text extraction, small images | Video processing, ML inference |

| Tradeoff | Detail |
|:---|:---|
| **URL expiry** | Presigned URLs must be consumed before expiry (typically 15 min – 1 hr); long-running downstream jobs need a fresh URL or an IAM-based approach |
| **Caching** | Frequently accessed small payloads should be cached locally (TTL-backed file cache) to avoid repeated S3 downloads for the same claim check key |

> **Also see**: [Claim Check Overview — broker-27](messaging/kafka-design-patterns.md#broker-27), [broker-52 Orphaned Object Cleanup](#broker-52)
> **Dictionary**: [Claim Check](../../reference-dictionary/messaging.md#claim-check)

---

## broker-54: S3 Lifecycle Policies for Claim Check Cost Management

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Claim Check

| | |
|:---|:---|
| **Problem** | Claim Check payloads accumulate in S3 indefinitely unless explicitly managed. Without lifecycle policies, storage costs grow linearly with message volume. Large media files, ML artefacts, and log dumps can accumulate to terabytes within months. |
| **Root cause** | S3 storage is not automatically reclaimed; lifecycle management is an explicit, per-bucket operational concern that is easy to overlook during initial implementation. |

**Strategy**: Attach S3 lifecycle rules to the Claim Check bucket at provisioning time:

```json
{
  "Rules": [
    {
      "Id": "TransitionToGlacier",
      "Prefix": "attachments/",
      "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
    },
    {
      "Id": "DeleteAfter90Days",
      "Prefix": "attachments/",
      "Expiration": {"Days": 90}
    },
    {
      "Id": "DeleteOrphanedTemp",
      "Prefix": "attachments/temp/",
      "Expiration": {"Days": 1}
    }
  ]
}
```

**Cost comparison**:
| Tier | Cost (us-east-1) | Suitable for |
|:---|:---|:---|
| S3 Standard | ~$0.023/GB | Active Claim Check objects (0–30 days) |
| S3 Glacier | ~$0.004/GB | Archive (30–90 days) |
| MSK broker storage (EBS) | ~$0.10/GB | Kafka topic retention (NOT suitable for large payloads) |

S3 Standard is already ~**4.3× cheaper** than MSK EBS; Glacier is ~**25× cheaper**.

| Tradeoff | Detail |
|:---|:---|
| **Glacier retrieval latency** | Glacier retrieval takes minutes to hours; only use for archival, not active processing |
| **Lifecycle granularity** | Apply different rules per `prefix` to avoid archiving frequently accessed reference data |

> **Also see**: [Claim Check Overview — broker-27](messaging/kafka-design-patterns.md#broker-27), [S3 Archiving — broker-44](messaging/kafka-data-state.md#broker-44)
> **Dictionary**: [Claim Check](../../reference-dictionary/messaging.md#claim-check), [Event Sourcing](../../reference-dictionary/cqrs-event-driven.md#event-sourcing)

---

## broker-55: Local RocksDB State Enables Zero-Network-Call Stream-Table Joins

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Stream-Table Duality

| | |
|:---|:---|
| **Problem** | A clickstream processing 10,000 events/second needs to enrich each event with user profile data (country, membership tier, preferences). A database lookup per event costs ~1 ms each = 10 seconds of database time per second of stream — the system falls behind instantly. A shared cache causes invalidation complexity and adds a network hop. |
| **Root cause** | Centralised storage (database, cache) cannot serve the per-event throughput of a high-volume stream without becoming the bottleneck. |

**Strategy**: Use Kafka Streams' **KTable** to materialise the reference table **locally on each stream processor instance**. Kafka Streams keeps a co-partitioned RocksDB copy of the user profiles KTable on the same host as the click event consumer. The join is a local RocksDB lookup — no network call.

```java
// Build the join topology
KStream<String, ClickEvent> clicks = builder.stream("clickstream");
KTable<String, UserProfile> users = builder.table(
    "user_profiles",
    Materialized.as("user-profile-store")  // RocksDB store name
);

// Join: local lookup, no network call
KStream<String, EnrichedClick> enriched = clicks.leftJoin(
    users,
    (click, profile) -> enrich(click, profile)
);
```

**Why it works**:
- Kafka Streams partitions both the stream topic and the table topic by the same key (`user_id`)
- Each processor instance handles the same key space for both — so every click event is on the same instance as its user profile
- The KTable update stream (user profile changes) keeps the local RocksDB current in real time

| Tradeoff | Detail |
|:---|:---|
| **Table size limit** | RocksDB is disk-backed but local; practical limit ~10–50 GB per partition before join latency degrades |
| **Rebalance cost** | When a Streams instance restarts, it must restore its RocksDB from the changelog topic — can take seconds to minutes for large tables |
| **Partition co-location requirement** | Stream and table topics must have the same partition count and key scheme; mismatches trigger a repartition step |

> **Also see**: [Stream-Table Duality Overview — broker-33](messaging/kafka-design-patterns.md#broker-33), [Compacted Topic — broker-31](messaging/kafka-design-patterns.md#broker-31)
> **Dictionary**: [Stream-Table Duality](../../reference-dictionary/messaging.md#stream-table-duality), [KTable](../../reference-dictionary/messaging.md#ktable), [Compacted Topic](../../reference-dictionary/messaging.md#compacted-topic)

---

## broker-56: Late Arriving Data Grace Period in Windowed Aggregations

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Stream-Table Duality

| | |
|:---|:---|
| **Problem** | A 1-minute tumbling window closes at T+60s. A click event with event timestamp T+45s arrives at T+65s (20 seconds late due to network delay). Kafka Streams drops the event because the window it belongs to has already been emitted and closed — the aggregation result is silently wrong. |
| **Root cause** | Windowed aggregations must close windows to emit results. Closing requires deciding when "enough time has passed to assume no more late events will arrive." Without a grace period, the default is zero tolerance for lateness. |

**Strategy**: Add a **`grace` period** to the window definition:

```java
enriched
    .groupByKey()
    .windowedBy(
        TimeWindows
            .ofSizeWithNoGrace(Duration.ofMinutes(1))
            .grace(Duration.ofSeconds(10))  // Accept events up to 10s late
    )
    .aggregate(...);
```

Events that arrive after the window closes but within the grace period are **re-ingested into the closed window** and trigger an updated result emission. The window emits multiple times — once at close, and again for each late event received within the grace period.

| Grace period | Detail |
|:---|:---|
| `0` (default) | No tolerance for lateness; events arriving after window close are dropped |
| `10s` | Accept events up to 10 seconds late; suitable for events delayed by broker consumer lag |
| `5min` | Suitable for mobile clients with intermittent connectivity; increases state retention cost |

| Tradeoff | Detail |
|:---|:---|
| **State retention** | Kafka Streams must retain window state for the duration of the grace period; larger grace = more memory/disk |
| **Downstream duplicates** | Downstream consumers of the aggregation receive multiple results per window (initial + each late update); must handle idempotently |

> **Also see**: [Stream-Table Duality Overview — broker-33](messaging/kafka-design-patterns.md#broker-33), [Idempotent Consumer — broker-29](messaging/kafka-design-patterns.md#broker-29)
> **Dictionary**: [Stream-Table Duality](../../reference-dictionary/messaging.md#stream-table-duality), [Kafka Transactions](../../reference-dictionary/messaging.md#kafka-transactions)

---

## broker-57: Compensating Transaction Design in Saga Choreography

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Saga Choreography

| | |
|:---|:---|
| **Problem** | A Saga has 3 steps: book flight → book hotel → book car. The car booking fails. The hotel service cancels correctly. But the flight service only listens for `HotelBookingFailed` — it misses `CarBookingFailed` and never cancels the flight. The saga terminates with a dangling confirmed flight. |
| **Root cause** | In choreography, each service independently decides when to compensate based on the events it subscribes to. Without explicit design of the full compensation graph, services subscribe too narrowly and leave partial saga state unrecovered. |

**Strategy**: For each forward operation a service performs, enumerate **all upstream failure events** that must trigger its compensation. The compensation handler must be **idempotent** — multiple failure events may fire.

```python
# Flight service: subscribes to failure events from ALL subsequent steps
if event_type == 'StartSaga':
    book_flight(saga_id)
elif event_type in ('HotelBookingFailed', 'CarBookingFailed'):
    # Either downstream failure requires flight cancellation
    cancel_flight(saga_id)   # Idempotent: safe to call multiple times
    publish(FlightCancelledEvent(saga_id))
```

**Compensation graph for a 3-step saga (Flight → Hotel → Car)**:
| Step that failed | Services that must compensate |
|:---|:---|
| Flight fails | (none — no prior steps to undo) |
| Hotel fails | Flight service cancels flight |
| Car fails | Hotel service cancels hotel; Flight service cancels flight |

Each compensation must also handle the case where the forward operation never completed (e.g., flight was never booked when car failure arrives after rebalance).

| Tradeoff | Detail |
|:---|:---|
| **Fan-out of failure events** | Each failure event is consumed by every participating service — O(N) consumers per failure topic |
| **Idempotency requirement** | A service may receive the same failure event twice (rebalance, retry); `cancel_flight()` must be a no-op if already cancelled |
| **Observability gap** | With pure choreography, no single component knows the full saga state; compensation debugging requires correlating events across multiple consumer group logs by `saga_id` |

> **Also see**: [Saga Choreography Overview — broker-34](messaging/kafka-design-patterns.md#broker-34), [Idempotent Consumer — broker-29](messaging/kafka-design-patterns.md#broker-29)
> **Dictionary**: [Compensating Transaction](../../reference-dictionary/data-concurrency.md#compensating-transaction), [Saga](../../reference-dictionary/data-concurrency.md#saga-pattern), [Event-Driven Architecture](../../reference-dictionary/cqrs-event-driven.md#event-driven-architecture)

---

## broker-58: Choreography vs Orchestration — When to Use Each

> **Source**: [11 Kafka Design Patterns - Performance & Integration Deep Dive](../../articles/messaging/11 Kafka Design Patterns - Performance & Integration Deep Dive.md) — Saga Choreography

| | |
|:---|:---|
| **Problem** | Engineers default to Kafka choreography for all sagas. For sagas with 6+ steps, conditional branches, or parallel compensation paths, pure choreography becomes untraceable — compensations are scattered across services, debugging requires correlating logs from 5+ consumers, and new step additions require modifying every existing service's event subscription list. |
| **Root cause** | Choreography optimises for decoupling but sacrifices observability and cognitive tractability at scale. Orchestration trades decoupling for centralised visibility. |

**Strategy**: Apply this decision matrix:

| Dimension | Choreography (Kafka) | Orchestration (Step Functions) |
|:---|:---|:---|
| Saga steps | 3–5 linear steps | 6+ steps or complex branching |
| Coupling tolerance | Services may not know each other | Central coordinator is acceptable |
| Observability need | Low (correlate by `saga_id` in logs) | High (visual workflow state machine) |
| Latency | Lower (direct event consumption) | Higher (Step Functions overhead: ~100 ms/state) |
| Deployment complexity | Low (services already in Kafka) | Higher (Step Functions state machine definition) |
| Rollback complexity | Explicit compensation events per service | Catch blocks in state machine definition |

**AWS Step Functions** provides a managed orchestrator that supports:
- Catch/retry blocks per step
- Visual state machine diagram
- Built-in saga completion tracking
- Integration with Lambda, ECS, DynamoDB, SQS

```json
"BookHotel": {
  "Type": "Task",
  "Resource": "arn:aws:lambda:...:function:book-hotel",
  "Next": "BookCar",
  "Catch": [{
    "ErrorEquals": ["HotelUnavailable"],
    "Next": "CompensateFlight"
  }]
}
```

| Tradeoff | Detail |
|:---|:---|
| **Choreography strength** | Pure Kafka path, no additional AWS service cost, lower latency per step, natural fit for event-driven teams |
| **Orchestration strength** | Centralised state visibility, visual debugging, built-in retry and timeout management, handles compensation routing automatically |

> **Also see**: [Saga Choreography Overview — broker-34](messaging/kafka-design-patterns.md#broker-34), [broker-57 Compensating Transaction Design](#broker-57)
> **Dictionary**: [Compensating Transaction](../../reference-dictionary/data-concurrency.md#compensating-transaction), [Saga](../../reference-dictionary/data-concurrency.md#saga-pattern)
