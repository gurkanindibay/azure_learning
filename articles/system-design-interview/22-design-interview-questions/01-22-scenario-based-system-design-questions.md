---
type: Article
title: "22 Scenario-Based System Design Questions That Reveal How Real Systems Actually Break"
description: "*By Arvind Kumar · 5 min read · May 22, 2026*"
timestamp: 2026-06-14T00:00:00Z
---

# 22 Scenario-Based System Design Questions That Reveal How Real Systems Actually Break

*By Arvind Kumar · 5 min read · May 22, 2026*

> **Source**: Originally published on [Medium](https://medium.com/@arvindkumar/22-scenario-based-system-design-questions)

---

Every developer eventually reaches a point where learning syntax, frameworks, and APIs is no longer enough.

You start asking bigger questions:

- Why do production systems fail even when the code looks correct?
- Why does scaling suddenly become painful at 10 million users?
- Why do companies like Netflix, Uber, Amazon, and WhatsApp invest so heavily in distributed systems engineering?
- And most importantly… **why do system design interviews rarely ask textbook questions anymore?**

Because modern engineering interviews are no longer testing whether you can define "load balancing" or "caching."

They test whether you can **think through chaos**. Real-world chaos — the kind where:

- Payments get deducted but orders fail
- Kafka delivers duplicate events
- Movie tickets get double booked
- Redis crashes an entire platform
- One slow microservice silently takes down everything

> Instead of asking *"What is Kafka?"*, interviewers now ask: *"Your notification service processed the same Kafka event twice and users received duplicate notifications. How would you fix it?"*

That single question reveals your understanding of distributed systems, reliability engineering, scalability, failure handling, architecture tradeoffs, and production maturity.

---

## Table of Contents

| # | Question | Key Concepts |
|---|----------|-------------|
| 1 | [URL Shortener Crashes During IPL Finals](#1-url-shortener-crashes-during-ipl-finals) | Read-heavy, CDN, Redis, hot keys |
| 2 | [WhatsApp Duplicate Messages](#2-whatsapp-duplicate-messages) | At-least-once, idempotency, deduplication |
| 3 | [Swiggy Shows Wrong Rider Location](#3-swiggy-shows-wrong-rider-location) | Real-time streaming, GPS polling, eventual consistency |
| 4 | [BookMyShow Sells Same Seat Twice](#4-bookmyshow-sells-same-seat-twice) | Race conditions, distributed locking |
| 5 | [Netflix Buffering After New Release](#5-netflix-buffering-after-new-release) | CDN, auto scaling, cache prewarming |
| 6 | [Uber Surge Pricing During Rain](#6-uber-surge-pricing-during-rain) | Stream processing, dynamic pricing |
| 7 | [Amazon Cart Shows Old Data](#7-amazon-cart-shows-old-data) | Cache invalidation, session consistency |
| 8 | [Instagram Notification Storm](#8-instagram-notification-storm) | Fanout, queue systems, backpressure |
| 9 | [Payment Deducted But Order Failed](#9-payment-deducted-but-order-failed) | Saga pattern, distributed transactions |
| 10 | [YouTube Video Processing Pipeline](#10-youtube-video-processing-pipeline) | Chunk processing, async workflows |
| 11 | [Kafka Duplicate Event Processing](#11-kafka-duplicate-event-processing) | Offset management, exactly-once |
| 12 | [Order Events Out of Sequence](#12-order-events-out-of-sequence) | Event ordering, Kafka partitions |
| 13 | [Notification Service Crashes During Flash Sale](#13-notification-service-crashes-during-flash-sale) | Backpressure, rate limiting |
| 14 | [Instagram Avoids JOINs at Scale](#14-instagram-avoids-joins-at-scale) | Denormalization, NoSQL tradeoffs |
| 15 | [DynamoDB Hot Partition Problem](#15-dynamodb-hot-partition-problem) | Partition keys, sharding |
| 16 | [Redis Cache Causes Production Outage](#16-redis-cache-causes-production-outage) | Cache stampede, TTL jitter |
| 17 | [AI Chatbot Gives Wrong Answers](#17-ai-chatbot-gives-wrong-answers) | RAG, hallucinations, vector databases |
| 18 | [AI Platform Becomes Very Expensive](#18-ai-platform-becomes-very-expensive) | Token reduction, model routing, caching |
| 19 | [AI Search Feels Slow](#19-ai-search-feels-slow) | Vector indexing, ANN search |
| 20 | [OTP Service Fails During Peak Traffic](#20-otp-service-fails-during-peak-traffic) | Rate limiting, retry storms |
| 21 | [One Microservice Takes Down Entire Platform](#21-one-microservice-takes-down-entire-platform) | Circuit breakers, bulkheads |
| 22 | [API Gateway Becomes a Bottleneck](#22-api-gateway-becomes-a-bottleneck) | Gateway scaling, edge caching |

---

### 1. URL Shortener Crashes During IPL Finals

| | |
|:---|:---|
| **Scenario** | Your URL shortener normally handles traffic well. But during IPL finals, a celebrity shares a shortened URL and the redirect service starts failing. |
| **Concepts** | Read-heavy architecture, CDN usage, Redis caching, hot key problems, database bottlenecks, horizontal scaling |

#### Why It Breaks

A URL shortener is fundamentally **read-heavy** — every click triggers a redirect lookup. During a viral event like IPL finals, a single short code (e.g., `bit.ly/ipl-final`) can receive millions of requests per minute. The failure chain typically goes:

1. **Hot key saturation** — One Redis node holds the mapping for `ipl-final` and gets hammered beyond capacity
2. **Database thundering herd** — If the cache expires, all concurrent requests hit the DB simultaneously
3. **Connection pool exhaustion** — The DB runs out of connections under the spike
4. **Cascading timeouts** — Upstream load balancers mark the service as unhealthy

#### Solution Architecture

**Layer 1 — CDN-Level Redirect (Edge Caching)**

The most effective fix: push the redirect to the edge. Instead of `302 Temporary`, return `301 Permanent` redirects for stable URLs and let the CDN cache the response at hundreds of PoPs worldwide.

```http
HTTP/1.1 301 Moved Permanently
Location: https://example.com/long-url
Cache-Control: public, max-age=86400, s-maxage=604800
```

The CDN serves the redirect without ever hitting your origin. This single change can absorb 99%+ of viral traffic.

**Layer 2 — Redis Cluster with Consistent Hashing**

Distribute short codes across a Redis cluster using consistent hashing so no single node becomes a hot spot:

| Strategy | Description |
|----------|-------------|
| **Shard by short code hash** | `CRC32(shortCode) % 16384` maps to a Redis slot |
| **Read replicas per shard** | 2-3 read replicas per primary to absorb read spikes |
| **Local in-memory cache** | Each app instance caches top 1000 URLs in-process (using Caffeine or Guava cache) |

**Layer 3 — Database Optimization**

```sql
-- Covering index: avoid table row lookup
CREATE INDEX idx_short_code_url ON url_mappings(short_code) 
  INCLUDE (original_url, expires_at);

-- Partition by creation date for efficient archival
CREATE TABLE url_mappings (...) PARTITION BY RANGE (created_at);
```

**Layer 4 — Connection Pool Tuning**

```java
HikariConfig config = new HikariConfig();
config.setMaximumPoolSize(50);
config.setMinimumIdle(10);
config.setConnectionTimeout(3000);    // Fail fast — don't queue connections
config.setIdleTimeout(600000);
config.setMaxLifetime(1800000);
```

#### Trade-Offs

| Approach | Pro | Con |
|----------|-----|-----|
| 301 + CDN edge caching | Near-zero origin load | Can't expire or change URLs quickly |
| Redis cluster | Linear read scaling | Operational complexity |
| DB read replicas | Simple to add | Still slower than Redis |
| In-process cache | Zero network latency | Stale data risk, memory pressure |

> **Azure Mapping**: Azure Front Door (global edge caching) → Azure Cache for Redis (Enterprise tier with clustering) → Azure SQL Hyperscale (read replicas). Use Front Door's rule engine to set `Cache-Control` headers per path pattern.

---

### 2. WhatsApp Duplicate Messages

| | |
|:---|:---|
| **Scenario** | Users complain they occasionally receive the same message twice. |
| **Concepts** | At-least-once delivery, retry mechanisms, idempotency, message deduplication, distributed retries |

> This question quickly exposes whether someone truly understands distributed systems reliability.

#### Why It Breaks

Duplicate messages are inevitable in any distributed messaging system. The culprit is the **at-least-once delivery guarantee** combined with retry logic. Here's the typical sequence:

1. Producer sends message to broker (Kafka, RabbitMQ, etc.)
2. Consumer receives and processes the message (e.g., saves to DB, sends notification)
3. Consumer's acknowledgement is delayed or lost (network glitch, GC pause, crash)
4. Broker assumes failure and **re-delivers** the same message
5. Consumer processes it again → **duplicate!**

The message WAS processed successfully the first time — but the broker never got the confirmation.

#### Solution Architecture

**Approach 1 — Idempotency Keys (Recommended for Most Cases)**

Embed a unique `idempotency_key` in each message. The consumer checks a deduplication store before processing:

```java
@Service
public class MessageProcessor {
    private final RedisTemplate<String, String> redis;
    private final MessageRepository repository;
    
    public void process(MessageEvent event) {
        String dedupKey = "processed:" + event.getIdempotencyKey();
        
        // SET NX (only set if not exists) with TTL
        Boolean isNew = redis.opsForValue()
            .setIfAbsent(dedupKey, "1", Duration.ofHours(24));
        
        if (Boolean.FALSE.equals(isNew)) {
            log.warn("Duplicate event skipped: {}", event.getIdempotencyKey());
            return; // Already processed — skip
        }
        
        repository.save(toEntity(event));
    }
}
```

**Approach 2 — Database Unique Constraint**

Use the database as the source of truth for deduplication:

```sql
CREATE TABLE processed_messages (
    idempotency_key VARCHAR(128) PRIMARY KEY,
    processed_at     TIMESTAMP DEFAULT NOW()
);

-- Consumer inserts: works if new, fails silently if duplicate
INSERT INTO processed_messages (idempotency_key)
VALUES (:key)
ON CONFLICT (idempotency_key) DO NOTHING;
```

If the insert succeeds → process the message. If it conflicts → already processed, skip it.

**Approach 3 — Exactly-Once Semantics (Kafka Transactions)**

For payment/financial systems where duplicates are absolutely unacceptable:

```java
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, 
          StreamsConfig.EXACTLY_ONCE_V2);
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

> ⚠️ Exactly-once has a ~20-30% throughput penalty. Only use when duplicates are truly unacceptable.

#### Decision Framework

```
Can your system tolerate occasional duplicates?
  ├─ YES → At-least-once + idempotency key (simplest, fastest, most common)
  └─ NO  → Is throughput > 100K msg/s?
            ├─ YES → At-least-once + DB unique constraint
            └─ NO  → Exactly-once semantics (Kafka transactions)
```

> **Azure Mapping**: Azure Service Bus natively supports duplicate detection via `MessageId` with a configurable deduplication window (up to 7 days). For custom dedup, use Azure Cache for Redis with `SETNX`.

---

### 3. Swiggy Shows Wrong Rider Location

| | |
|:---|:---|
| **Scenario** | The delivery partner is still 3 km away, but the app shows him outside the customer's house. |
| **Concepts** | Real-time streaming, GPS polling intervals, eventual consistency, WebSockets, geo-distributed systems |

#### Why It Breaks

This is a **stale data + bad interpolation** problem. GPS coordinates are not streamed continuously — they arrive every 5-10 seconds. Between updates, the frontend extrapolates the rider's position assuming constant velocity. If the rider stops at a traffic light or takes a detour, that extrapolation is completely wrong.

The root cause: **dead reckoning without error correction**. The client predicts future position based on last known velocity — which fails whenever behavior changes (stopping, turning, U-turns).

#### Solution Architecture

**Approach 1 — Server-Side Interpolation with ETA Correction**

The backend, not the client, should compute the displayed position. Use the ETA from the routing engine as a constraint:

```python
def compute_display_position(rider_location, route, eta_seconds):
    """
    Place rider icon at the point along the route that matches the ETA,
    NOT at the raw GPS location.
    """
    total_distance = route.total_distance_meters
    speed = total_distance / eta_seconds  # m/s
    
    # Rider is at most this far along the route
    max_progress = total_distance - (speed * 60)  # 1 min buffer
    
    return route.interpolate_position(
        progress=min(rider_location.route_progress, max_progress)
    )
```

**Approach 2 — Adaptive Polling with Geofencing**

| Rider State | Polling Interval | Reason |
|-------------|-----------------|--------|
| Moving on highway | 5 seconds | Predictable path |
| Approaching customer (< 500m) | 1-2 seconds | High accuracy needed |
| Stopped (traffic light) | 10 seconds | No movement, save battery |
| Inside delivery geofence | Every second | Customer is watching closely |

**Approach 3 — Kalman Filter with Sensor Fusion**

```javascript
// Client-side: fuse GPS with device sensors
const position = kalmanFilter({
    gps: rawGps,              // Every 5s, ±5m accuracy
    accelerometer: accel,     // Every 100ms, detect stops
    gyroscope: gyro,          // Every 100ms, detect turns
    lastKnownRoute: route     // Map-matched road segment
});

// Only send significant changes
if (distanceChanged > 10 || stateChanged) {
    websocket.send({ lat, lng, speed, heading, state });
}
```

#### Key Insight

> Don't show raw GPS coordinates to users. Show a **smoothed, route-constrained, ETA-adjusted** position. The goal is perceptual accuracy, not GPS precision.

> **Azure Mapping**: Azure Web PubSub for WebSocket connections at scale, Azure Maps for route calculation and geofencing, Azure Stream Analytics for real-time location processing.

---

### 4. BookMyShow Sells Same Seat Twice

| | |
|:---|:---|
| **Scenario** | Two users successfully booked the same movie seat simultaneously. |
| **Concepts** | Race conditions, distributed locking, optimistic locking, pessimistic locking, transactions |

> Classic concurrency problem. Still one of the best interview questions.

#### Why It Breaks

Two concurrent requests both check seat availability (both see "available"), and both proceed to book. The `SELECT` and `UPDATE` are not atomic — the time gap between them is the race condition window. In a distributed system with multiple application servers, even `SELECT FOR UPDATE` on one connection doesn't prevent another server from doing the same thing.

#### Solution Architecture

**Approach 1 — Optimistic Locking with Version Column (Best for Low Contention)**

```sql
-- Schema: add a version column
ALTER TABLE seats ADD COLUMN version INT DEFAULT 0;

-- Atomic booking attempt
UPDATE seats 
SET status = 'booked', user_id = :userId, version = version + 1
WHERE id = 'A3' 
  AND status = 'available' 
  AND version = :expectedVersion;

-- Check rows affected: 1 = success, 0 = someone else got it
```

```java
@Transactional
public BookingResult bookSeat(String seatId, String userId) {
    int updated = seatRepository.bookSeat(seatId, userId, 
        seatRepository.getVersion(seatId));
    
    if (updated == 0) {
        throw new SeatAlreadyBookedException("Seat already taken");
    }
    // Proceed with payment...
}
```

**Approach 2 — SELECT ... FOR UPDATE (Pessimistic — High Contention)**

When contention is extreme (front-row seats at a blockbuster premiere):

```sql
BEGIN TRANSACTION;
SELECT * FROM seats WHERE id = 'A3' AND status = 'available' FOR UPDATE;
-- If row returned, it's locked — no one else can touch it
UPDATE seats SET status = 'booked', user_id = :userId WHERE id = 'A3';
COMMIT;
```

⚠️ Add a lock timeout so users don't block everyone: `SET lock_timeout = '5s';`

**Approach 3 — Redis Distributed Lock with Reservation**

A two-phase approach: reserve → pay → confirm. The reservation puts a short-lived lock (5 minutes) in Redis. If payment isn't completed in time, the lock auto-expires and the seat becomes available again.

```java
String lockKey = "seat:" + showId + ":" + seatId;
Boolean acquired = redis.opsForValue()
    .setIfAbsent(lockKey, userId, Duration.ofMinutes(5));
```

#### Trade-Off Comparison

| Approach | Contention Level | Throughput | Complexity |
|----------|-----------------|------------|------------|
| Optimistic (version column) | Low | Very high | Low |
| Pessimistic (FOR UPDATE) | High | Lower | Low |
| Redis distributed lock | Medium | High | Medium |
| Atomic compare-and-swap | Any | Very high | Low |

#### ⚠️ Race Condition in Optimistic Locking?

A common concern: *does the read-before-write gap in optimistic locking create a race condition?*

**No — it's correct, but it has a UX problem under high contention.** The `UPDATE ... WHERE version = :expectedVersion` is a single atomic statement. If two transactions both read `version = 0`, only ONE `UPDATE` succeeds — the other sees `0 rows affected` and correctly rejects the booking. The version column acts as a compare-and-swap (CAS) guard.

**However, there's a "false hope" problem.** During peak sales, hundreds of users may simultaneously see a seat as "available," click "Book," enter payment details, and only then discover it's gone. That gap between `SELECT` and `UPDATE` creates wasted work and poor UX.

**The fix for high-contention seats**: skip the `SELECT` entirely — use a **blind atomic UPDATE**:

```java
// No prior SELECT — just attempt the atomic write
int updated = seatRepository.bookIfAvailable(seatId, userId);
// UPDATE seats SET status='booked', user_id=? WHERE id=? AND status='available'
// 1 row → booked; 0 rows → already taken
```

This eliminates the read-before-write window. No version column needed — the `status='available'` check is sufficient.

> **Azure Mapping**: Azure SQL Database supports optimistic concurrency via row version. Azure Cache for Redis for distributed locks. Cosmos DB offers optimistic concurrency via `_etag` on documents.

---

### 5. Netflix Buffering After New Season Release

| | |
|:---|:---|
| **Scenario** | A massively popular show gets released and millions start streaming simultaneously. |
| **Concepts** | CDN architecture, auto scaling, traffic spikes, cache prewarming, load balancing |

#### Why It Breaks

Netflix's normal traffic might be 10 Tbps globally. A Stranger Things season premiere can spike to 50+ Tbps in the first hour. The failure chain:

1. **Origin server overload** — CDN cache misses cascade to origin
2. **Cold cache penalty** — New content hasn't been cached at edge PoPs yet
3. **Encoding pipeline backlog** — Not all quality variants are ready in every region
4. **Last-mile congestion** — ISP peering points saturate

#### Solution Architecture

**Layer 1 — Open Connect (Netflix's Custom CDN)**

Netflix built their own CDN appliances placed **inside ISP data centers** — not in traditional edge PoPs. This is called Open Connect. Key design decisions:

- **Pre-positioning**: Popular content is pushed (not pulled) to appliances during off-peak hours
- **Nightly sync**: Appliances download predicted-popular titles between 2-6 AM local time
- **Tiered storage**: SSD for hottest content, HDD for the long tail

**Layer 2 — Adaptive Bitrate Streaming (ABR)**

Each video is encoded at multiple bitrates (360p → 4K). The client dynamically switches based on available bandwidth and buffer health:

```javascript
function selectBitrate(bandwidth, bufferHealth) {
    if (bufferHealth < 5)  return LOWEST;        // Survival mode
    if (bufferHealth < 15) return CONSERVATIVE;
    if (bandwidth > 15000) return UHD_4K;
    return bandwidth * 0.9;                       // 90% of measured bandwidth
}
```

**Layer 3 — Cache Prewarming Strategy**

For a new season release, Netflix pre-encodes and distributes the first 2 episodes 48 hours before release. They upload manifests to all Open Connect appliances and run synthetic playback tests from each region to warm edge caches.

**Layer 4 — Graceful Degradation**

| Condition | Degradation Response |
|-----------|---------------------|
| Bandwidth drops | Switch to lower bitrate (seamless, < 1s) |
| CDN node saturated | Redirect to next nearest node |
| All CDN nodes busy | Fall back to lower-bitrate-only mode |
| Encoding variant missing | Serve closest available bitrate |

> **Azure Mapping**: Azure CDN (from Microsoft or Akamai/Verizon), Azure Media Services for encoding, Azure Front Door for global routing. For Netflix-like architecture, Azure Stack Edge appliances could serve as on-premise caching nodes at ISPs.

---

### 6. Uber Surge Pricing During Rain

| | |
|:---|:---|
| **Scenario** | It starts raining heavily and suddenly ride prices become 3x. |
| **Concepts** | Stream processing, real-time analytics, demand vs supply computation, dynamic pricing systems, Kafka pipelines |

#### Why It Breaks

Surge pricing is a real-time supply-demand matching problem. When rain starts, three things happen simultaneously:

1. **Demand spikes** — Everyone requests rides at once (5-10x normal)
2. **Supply shrinks** — Drivers go offline or stop accepting new rides
3. **Trip duration increases** — Slower traffic means fewer trips/hour per driver

The pricing engine must react in **sub-second** latency across millions of geo-cells, or the supply-demand imbalance worsens.

#### Solution Architecture

**Data Pipeline (Lambda Architecture)**

The system combines real-time stream processing with historical batch analysis:
- **Speed layer** (Flink/Spark Streaming): Processes real-time ride requests and driver locations per geo-cell every 2 seconds
- **Batch layer** (HDFS/S3): Computes historical surge patterns — e.g., "rain in this neighborhood at 6 PM = 2.3x average surge"
- **Serving layer**: Blends both to produce the final surge multiplier

**Real-Time Supply-Demand per Geo-Cell**

```python
def compute_surge_multiplier(geo_cell_id):
    # Real-time window (last 2 minutes)
    open_requests = redis.get(f"demand:{geo_cell_id}:open")
    available_drivers = redis.get(f"supply:{geo_cell_id}:available")
    
    if available_drivers == 0:
        return MAX_SURGE  # e.g., 5.0x
    
    current_ratio = open_requests / available_drivers
    
    # Historical baseline for this geo-cell + weather + time
    historical_surge = ml_model.predict(
        geo_cell_id, weather='heavy_rain', hour=datetime.now().hour
    )
    
    # Blend: 70% real-time, 30% historical (smooths oscillations)
    raw_multiplier = (0.7 * current_ratio * BASE_PRICE) + (0.3 * historical_surge)
    return clamp(raw_multiplier, MIN=1.0, MAX=5.0)
```

**Key Design Decisions**

| Decision | Rationale |
|----------|-----------|
| H3 hexagonal grid | Equal area cells, no pole distortion, 16 resolution levels |
| 2-minute windows | Balances freshness vs noise |
| Per geo-cell, not global | Surge in one neighborhood doesn't affect another |
| Blend real-time + historical | ML dampens oscillations; real-time catches sudden changes |
| Cap at 5x | Prevents PR disasters during emergencies |

> Pure ratio-based surge causes oscillations: high price → fewer requests → ratio drops → low price → more requests → ratio spikes. The ML model dampens this feedback loop.

> **Azure Mapping**: Azure Event Hubs (Kafka-compatible) for ride events, Azure Stream Analytics or HDInsight (Flink) for real-time computation, Azure Cache for Redis for geo-cell counters, Azure Maps for H3 geo-spatial indexing.

---

### 7. Amazon Cart Shows Old Data

| | |
|:---|:---|
| **Scenario** | A user removes an item from cart on mobile, but it still appears on laptop. |
| **Concepts** | Cache invalidation, distributed cache sync, session consistency, event-driven updates |

> One of the hardest problems in computer science: *"Cache invalidation and naming things."*

#### Why It Breaks

The user has two active sessions (mobile + laptop), each potentially hitting different backend instances with different local caches. Even if you delete the cache key after the write, there's a **race window** where a concurrent read can fetch the old data and re-populate the cache before the invalidation completes.

#### Solution Architecture

**Approach 1 — Cache-Aside with Write Invalidation**

The golden rule: **always write to DB first, then invalidate cache**. The reverse order risks caching stale data after invalidation.

```java
public void removeItem(String userId, String itemId) {
    // Step 1: Update DB (source of truth)
    cartRepository.removeItem(userId, itemId);
    
    // Step 2: Invalidate cache
    redis.delete("cart:" + userId);
    
    // Step 3: Emit event for other instances
    eventBus.publish(new CartUpdatedEvent(userId, "item_removed", itemId));
}
```

**Approach 2 — Event-Driven Cache Invalidation**

Publish a `CartUpdated` event with a version number. All interested services check the version before serving cached data. If the version is stale, they re-fetch from the database.

```java
// On cart change:
eventBus.publish(new CartUpdatedEvent(userId, newVersion));

// On cache read:
CachedCart cached = redis.get("cart:" + userId);
if (cached == null || cached.version < getCurrentVersion(userId)) {
    // Re-fetch from DB
    cached = cartRepository.getCart(userId);
    redis.set("cart:" + userId, cached);
}
```

**Approach 3 — Sticky Sessions + Session-Level Cache**

Route the same user always to the same server. The cache lives in that server's memory, avoiding network round-trips entirely. This works well for single-device scenarios but doesn't fully solve the multi-device problem.

| Pro | Con |
|-----|-----|
| Zero network latency for cache reads | Server restart loses all caches |
| No distributed cache needed | Uneven load if some users are heavy |
| Simple implementation | Multi-device problem not fully solved |

#### Decision Framework

```
Single device, simple app → Sticky sessions + in-memory cache
Multiple devices, < 100K users → Cache-aside with Redis
Multiple devices, > 100K users → Event-driven invalidation
Global scale (Amazon) → CDN-level caching + DynamoDB DAX
```

> **Azure Mapping**: Azure Cache for Redis with Pub/Sub for invalidation events, Azure Cosmos DB (session consistency level for cart data), Azure Event Grid for event-driven cache updates.

---

### 8. Instagram Notification Storm

| | |
|:---|:---|
| **Scenario** | A celebrity uploads a post and millions of notifications need to be delivered instantly. |
| **Concepts** | Fanout architecture, queue systems, async processing, push notification scalability, backpressure handling |

#### Why It Breaks

When Cristiano Ronaldo posts, Instagram needs to notify ~600 million followers. If you try this synchronously — enumerate all followers, send push to each — it would take hours at typical push notification rates. This is the **fanout problem**: one event fans out to millions of recipients. Doing it naively saturates push notification providers (FCM/APNs), exhausts database connections, and overflows message queues.

#### Solution Architecture

**Layer 1 — Tiered Fanout Strategy**

Instagram doesn't notify all 600M followers the same way:

| Follower Type | Count | Strategy | Latency Target |
|---------------|-------|----------|---------------|
| **Close friends** (frequently interacted) | ~100-500 | Instant push notification | < 1 second |
| **Active followers** (daily active users) | ~100K-1M | Batched push via queue | < 5 minutes |
| **Casual followers** | ~100M+ | Show in feed only (pull, not push) | Next app open |

**Layer 2 — Fanout-on-Write (Push Model for Normal Users)**

For active followers, pre-compute the feed at write time. When a non-celebrity posts, batched writes insert the post into each active follower's feed in Redis. This makes reads a simple sorted set lookup — no JOINs, no computation at read time.

**Layer 3 — Fanout-on-Read (Pull Model for Celebrities)**

Celebrity posts are NOT pre-computed into follower feeds. Instead, when a follower opens the app, the system merges in recent celebrity posts at read time. This avoids writing 600M rows for a single post.

**Layer 4 — Notification Queue with Backpressure**

Use a bounded queue to prevent memory exhaustion. Drain in batches, respecting FCM/APNs rate limits (typically ~1000/sec per project). Group notifications by device token to collapse multiple notifications into one.

#### The Hybrid Approach (What Instagram Actually Uses)

```
For 99.9% of users: Fanout-on-write (pre-compute feed at post time)
For celebrity users:  Fanout-on-read (merge at app-open time)
For notifications:    Tiered (push for close friends, pull for rest)
```

> **Azure Mapping**: Azure Notification Hubs for multi-platform push (APNs/FCM), Azure Service Bus topics with multiple subscriptions for fanout, Azure Cosmos DB for feed storage (low-latency reads), Azure Functions for fanout-on-write workers.

---

### 9. Payment Deducted But Order Failed

| | |
|:---|:---|
| **Scenario** | Money gets deducted successfully, but order creation fails. |
| **Concepts** | Saga pattern, distributed transactions, compensation workflows, retry handling, idempotency keys |

> Probably the most important modern distributed systems question.

#### Why It Breaks

In a monolith, you'd wrap payment + order creation in a single ACID transaction. In microservices, the Payment Service and Order Service have separate databases. The payment succeeds (money leaves the user's account), but the order fails to create (inventory issue, DB constraint violation, network error). Now you have money deducted with no order to show for it — a critical business failure.

#### Solution Architecture: The Saga Pattern

A **saga** is a sequence of local transactions, each with a **compensating transaction** to undo it if something fails later.

**Orchestration-Based Saga (Central Coordinator)**

```java
@Service
public class CreateOrderSaga {
    
    public OrderResult execute(CreateOrderRequest request) {
        // Step 1: Create order in PENDING state
        Order order = orderService.createPending(request);
        
        try {
            // Step 2: Process payment (with idempotency key!)
            PaymentResult payment = paymentService.charge(
                new PaymentRequest(order.getId(), request.getAmount())
                    .withIdempotencyKey(order.getId() + "_payment")
            );
            
            if (!payment.isSuccess()) {
                orderService.markCancelled(order.getId(), "Payment failed");
                return OrderResult.failed("Payment declined");
            }
            
            // Step 3: Reserve inventory
            InventoryResult inventory = inventoryService.reserve(
                new ReserveRequest(order.getItems())
                    .withIdempotencyKey(order.getId() + "_inventory")
            );
            
            if (!inventory.isSuccess()) {
                // COMPENSATION: refund the payment
                paymentService.refund(payment.getTransactionId());
                orderService.markCancelled(order.getId(), "Inventory unavailable");
                return OrderResult.failed("Out of stock");
            }
            
            // Step 4: All good → confirm
            orderService.markConfirmed(order.getId());
            return OrderResult.success(order.getId());
            
        } catch (Exception e) {
            // Compensation for partial failures
            compensate(order, payment);
            throw e;
        }
    }
}
```

#### Compensation Patterns

| Failure Point | Compensation |
|---------------|-------------|
| Payment fails | Cancel order (no money moved) |
| Inventory fails after payment | **Refund** payment + cancel order |
| Shipping fails after inventory | **Release** inventory + **refund** payment + cancel order |
| Order confirmation fails | Manual intervention (all prior steps already committed) |

> The golden rule: **if you can't compensate, make it the last step.** Don't ship before inventory is confirmed. Don't charge before the order is valid.

#### Idempotency: The Critical Ingredient

Every step MUST be idempotent. Use an idempotency key (e.g., `orderId + "_payment"`) that the payment gateway stores. On retry, the gateway returns the cached result instead of charging again.

> **Azure Mapping**: Azure Durable Functions for orchestration-based sagas (built-in state management and retry), Azure Service Bus for choreography-based event routing, Azure SQL Database with idempotency key tables.

---

### 10. YouTube Video Processing Pipeline

| | |
|:---|:---|
| **Scenario** | A user uploads a 4K video and expects streaming support quickly. |
| **Concepts** | Chunk processing, distributed workers, encoding pipelines, async workflows, storage optimization |

#### Why It Breaks

Processing a 4K video isn't a single task — it's a **DAG of dependent jobs**. For a 2-hour 4K video, you might need 1000+ chunks × 5+ resolutions = 5000+ encoding jobs, totaling hours of CPU time. But users expect "processing" to take minutes, not hours.

The challenge: split the work into independent units, process them in parallel across hundreds of workers, then stitch the results back together — all while making the lowest resolution available as quickly as possible.

#### Solution Architecture

**Stage 1 — Chunk Splitting (Immediate)**

Split the video into 5-second segments at keyframe boundaries (GOP-aligned chunking). This ensures clean cuts that don't require re-encoding at boundaries.

```bash
ffmpeg -i input.mp4 -c copy -map 0 -f segment \
       -segment_time 5 -segment_format mpegts \
       -reset_timestamps 1 chunk_%03d.ts
```

**Stage 2 — Parallel Transcoding**

Push chunks to a worker queue. Each worker independently transcodes one chunk to one resolution. Scale horizontally — YouTube reportedly runs millions of encoding tasks concurrently. Use hardware encoders (GPU/ASIC) for 10-50x speedup over CPU encoding.

**Stage 3 — Stitching + Packaging**

Once all chunks for a resolution are ready, stitch them and create DASH/HLS manifests so the player can dynamically switch between quality levels during playback.

**Stage 4 — Progressive Availability**

Don't wait for all resolutions. Release the lowest resolution first, then upgrade as higher qualities become available:

```
t+30s:  360p available → user can start watching
t+2min: 720p available → player auto-switches up
t+5min: 1080p available
t+15min: 4K available
```

#### Optimization Techniques

| Technique | Impact |
|-----------|--------|
| GOP-aligned chunking | No re-encoding of keyframes at boundaries |
| Per-title encoding | Simpler videos get lower bitrate, saving CPU + storage |
| Hardware encoders (GPU/ASIC) | 10-50x faster than CPU encoding |
| Two-pass skipped for low-res | Single-pass VBR good enough for ≤ 720p |
| Warm pool of encoder instances | Avoid cold start latency |

> **Azure Mapping**: Azure Media Services (managed encoding at scale), Azure Batch for large-scale parallel transcoding jobs, Azure Functions for lightweight chunk orchestration, Azure Blob Storage for chunk storage with lifecycle management.

---

### 11. Kafka Duplicate Event Processing

| | |
|:---|:---|
| **Scenario** | A notification consumer accidentally processes duplicate Kafka events. |
| **Concepts** | Offset management, consumer retries, exactly-once semantics, idempotent consumers |

> A very common real production issue.

#### Why It Breaks

Kafka's default delivery guarantee is **at-least-once**. Duplicates arise from three main scenarios:

1. **Consumer commits offset AFTER processing but crashes**: On restart, it re-processes the last batch
2. **Rebalance during processing**: A partition gets reassigned to another consumer before the first one commits
3. **Producer retries**: A producer with `retries=3` and `acks=1` can produce duplicates if the leader fails after writing but before sending the acknowledgement

The most dangerous pattern is `enable.auto.commit=true` combined with processing that has side effects (sending emails, charging payments).

#### Solution Architecture

**Approach 1 — Idempotent Consumer with Redis (Recommended)**

Use the event's business key as an idempotency key. Check Redis with `SETNX` before processing:

```java
@KafkaListener(topics = "notifications")
public void onMessage(ConsumerRecord<String, NotificationEvent> record) {
    String dedupKey = "processed:notifications:" + record.key();
    
    Boolean isNew = redisTemplate.opsForValue()
        .setIfAbsent(dedupKey, "1", Duration.ofHours(48));
    
    if (Boolean.FALSE.equals(isNew)) {
        return; // Already processed — skip
    }
    
    notificationSender.send(record.value());
}
```

**Approach 2 — Database-Level Deduplication**

```sql
INSERT INTO sent_notifications (event_id, user_id, message, sent_at)
VALUES (:eventId, :userId, :message, NOW())
ON CONFLICT (event_id) DO NOTHING;
```

If the insert succeeds → process. If it conflicts → already processed.

**Approach 3 — Exactly-Once Semantics (Kafka Transactions)**

```java
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, 
          StreamsConfig.EXACTLY_ONCE_V2);
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

> ⚠️ Exactly-once has a ~20-30% throughput penalty. Reserve it for payments and financial transactions.

#### Decision Matrix

| Approach | Duplication Risk | Performance Overhead | Complexity |
|----------|-----------------|---------------------|------------|
| Auto-commit + no dedup | High ❌ | None | None |
| Manual commit + Redis dedup | Near zero ✅ | ~1ms Redis call | Low |
| DB unique constraint | Zero ✅ | DB insert latency | Low |
| Exactly-once (Kafka EOS) | Zero ✅ | ~20-30% throughput ↓ | High |

> **Azure Mapping**: Azure Event Hubs supports idempotent producers. Azure Cache for Redis for consumer-side dedup with `SETNX`. Azure SQL's `MERGE` for upsert-based deduplication.

---

### 12. Order Events Out of Sequence

| | |
|:---|:---|
| **Scenario** | "Order Delivered" arrives before "Order Shipped." |
| **Concepts** | Event ordering, Kafka partitions, sequence numbers, event consistency |

#### Why It Breaks

Events travel through different paths and can arrive out of order due to:
- **Producer retries**: A retried "Order Shipped" event gets queued behind the newer "Order Delivered" event
- **Multi-partition writes**: Events written to different Kafka partitions have no ordering guarantee across partitions
- **Async processing**: Different consumers process events at different speeds

#### Solution Architecture

**Approach 1 — Same Partition Key (Kafka-Guaranteed Ordering)**

Kafka guarantees order **within a partition**. Use the order ID as the partition key — ALL events for a given order go to the same partition and are processed in order.

```java
ProducerRecord<String, OrderEvent> record = new ProducerRecord<>(
    "order-events",
    order.getId().toString(),  // Partition key: all events for this order
    event
);
```

⚠️ This limits throughput per order (one consumer thread per partition), but orders are independent so total throughput scales with partition count.

**Approach 2 — Sequence Numbers (Application-Level Ordering)**

Embed a monotonically increasing sequence number in each event. The consumer buffers out-of-order events and processes them once the gap is filled:

```java
public class OrderEvent {
    private String orderId;
    private long sequenceNumber; // 1, 2, 3, ...
    private OrderStatus status;
}

// Consumer: buffer out-of-order events in a TreeMap
// Process when sequence numbers are contiguous
```

**Approach 3 — State Machine Validation**

Instead of trusting event order, validate state transitions. If the current state is `CREATED` and you receive `DELIVERED`, you know something's wrong — buffer it and wait for the missing `SHIPPED` event.

```java
public enum OrderStatus {
    CREATED, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

public void applyEvent(Order order, OrderEvent event) {
    if (!isValidTransition(order.getStatus(), event.getStatus())) {
        bufferForRetry(order.getId(), event, Duration.ofMinutes(5));
        return;
    }
    order.setStatus(event.getStatus());
}
```

#### Comparison

| Approach | Ordering Guarantee | Throughput | Late Event Handling |
|----------|-------------------|------------|-------------------|
| Same partition key | Strong (within key) | Limited per key | N/A (never out of order) |
| Sequence numbers | Strong | High | Buffered, re-sequenced |
| State validation | Eventual | High | Rejected, retried later |

> **Azure Mapping**: Azure Event Hubs preserves order within a partition (use `PartitionKey`). Cosmos DB change feed delivers events in order per partition key range. Service Bus sessions guarantee FIFO for messages with the same `SessionId`.

---

### 13. Notification Service Crashes During Flash Sale

| | |
|:---|:---|
| **Scenario** | A massive sale begins and notification systems start timing out. |
| **Concepts** | Backpressure, queue buffering, rate limiting, load shedding |

#### Why It Breaks

During a flash sale, three forces converge on the notification service:

1. **High volume**: Millions of "sale started" notifications go out in seconds
2. **External dependency limits**: FCM/APNs rate-limit at ~1000 messages/second per project
3. **Cascading failure**: As notifications queue up, connection pools exhaust, timeouts cascade upstream to the sale service, which propagates to checkout

#### Solution Architecture

**Layer 1 — Queue-Based Buffering (Decouple Immediately)**

Don't send notifications synchronously. Enqueue and acknowledge immediately. The HTTP response says "notifications queued" — not "notifications sent."

```java
@PostMapping("/flash-sale/start")
public ResponseEntity<?> startFlashSale(@RequestBody FlashSale sale) {
    flashSaleService.save(sale);
    
    for (NotificationBatch batch : partitionUsers(sale.getTargetUsers(), 1000)) {
        notificationQueue.send(batch); // Returns immediately — fire and forget
    }
    
    return ResponseEntity.accepted().body(Map.of(
        "status", "started",
        "notifications", "queued" // Not "sent"!
    ));
}
```

**Layer 2 — Rate-Limited Dispatch Worker**

The worker respects downstream provider limits using a token bucket:

```java
private final RateLimiter fcmLimiter = RateLimiter.create(1000.0); // 1000/sec

@Scheduled(fixedDelay = 100)
public void dispatchBatch() {
    List<NotificationTask> batch = queue.poll(500);
    for (NotificationTask task : batch) {
        if (!fcmLimiter.tryAcquire(50, TimeUnit.MILLISECONDS)) {
            queue.requeue(task); // Put back, try later
            continue;
        }
        sendNotification(task);
    }
}
```

**Layer 3 — Priority-Based Load Shedding**

When the queue exceeds 90% capacity, start dropping low-priority notifications:

| Priority | Notification Type | Drop Strategy |
|----------|-------------------|---------------|
| P0 | Transactional (OTP, payment confirm) | Never drop |
| P1 | Time-sensitive promo (flash sale live) | Drop after 5 min staleness |
| P2 | Marketing (weekly deals) | Drop silently, send tomorrow |
| P3 | Social (likes, comments) | Batch into daily digest |

**Layer 4 — Provider Failover**

```
Primary: FCM Push → Fallback 1: APNs (iOS) → Fallback 2: SMS → Fallback 3: In-app inbox
```

Use a circuit breaker around each provider. When one fails, seamlessly fail over to the next.

> **Azure Mapping**: Azure Service Bus with sessions for FIFO per user, Azure Notification Hubs with per-tag rate limiting, Azure Functions for queue-triggered dispatch workers, Azure Redis for rate limiter token buckets.

---

### 14. Instagram Avoids JOINs at Scale

| | |
|:---|:---|
| **Scenario** | Why do large social media platforms often avoid complex relational JOIN queries? |
| **Concepts** | Denormalization, read optimization, NoSQL tradeoffs, query performance |

#### Why It Breaks

Consider Instagram's "show 20 most recent posts from people I follow" query. In SQL, this would JOIN the `posts`, `follows`, `users`, `likes`, and `comments` tables. For a user following 1000 people, this query scans potentially millions of rows, sorts them all by time, and returns the top 20. At Instagram's scale (~500M daily active users), this would require scanning billions of rows per query.

Even with perfect indexes, the JOIN of hot tables creates **lock contention** and **buffer pool thrashing** — the database spends more time managing locks than serving data.

#### Solution Architecture

**Approach 1 — Denormalized Feed Table (Pre-Computation)**

Instagram pre-computes each user's feed. Instead of JOINs at read time, they compute at write time. Each user has a feed table with denormalized data (author name, avatar URL, like count, comment count) already embedded:

```sql
CREATE TABLE user_feed (
    user_id BIGINT,
    post_id BIGINT,
    author_username VARCHAR(50),    -- Denormalized
    author_avatar_url VARCHAR(500), -- Denormalized
    like_count INT,                -- Updated async
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, created_at, post_id)
) WITH CLUSTERING ORDER BY (created_at DESC);
```

Now the read is a single partition lookup — no JOINs, sub-millisecond latency.

The cost is **write amplification**: when Cristiano Ronaldo posts, you write 600M rows. But this is acceptable because reads are 1000x more frequent than writes, the write is async, and it's done in batches.

**Approach 2 — Selective Fanout (Hybrid)**

Only fanout to recently active followers. Inactive followers get the post merged in at read time (fanout-on-read). This reduces write amplification by 100-1000x for celebrities.

**Approach 3 — Async Counters**

Likes and comments counts are stored as counters in Redis, updated asynchronously. Periodically flushed to the database in batches. This avoids lock contention on hot post rows.

```java
// When someone likes a post: atomic increment in Redis (no DB lock!)
redis.zincrby("post:likes", 1, postId);

// Periodically flush to DB in batches
@Scheduled(fixedDelay = 5000)
public void flushLikeCounts() {
    // Batch update: UPDATE posts SET like_count = like_count + delta
}
```

#### Trade-Off Summary

| Approach | Read Speed | Write Cost | Consistency | Storage |
|----------|-----------|------------|-------------|---------|
| Normalized + JOINs | Slow at scale | Low | Strong | Low |
| Denormalized feed | Instant | Very high (fanout) | Eventual | High |
| Hybrid fanout | Fast | Moderate | Eventual | Moderate |
| Async counters | Fast | Low | 5-10 sec lag | Low |

> **Azure Mapping**: Azure Cosmos DB (Cassandra API) for denormalized feeds with partition-per-user, Azure Cache for Redis for async counters, Azure Functions for fanout-on-write workers.

---

### 15. DynamoDB Hot Partition Problem

| | |
|:---|:---|
| **Scenario** | One celebrity account suddenly receives massive traffic and performance degrades. |
| **Concepts** | Partition keys, sharding strategies, hot partitions, traffic distribution |

#### Why It Breaks

DynamoDB (and similar distributed databases) partitions data by the partition key hash. If one partition key gets disproportionate traffic, that single partition becomes a bottleneck — regardless of your total provisioned capacity. If you've provisioned 10,000 WCU across 10 partitions, but one celebrity partition receives 8,000 WCU of traffic, that partition gets throttled at its 1,000 WCU limit while 9 other partitions sit idle.

#### Solution Architecture

**Approach 1 — Write Sharding with Random Suffix**

Instead of `PK = celebrity_id`, use `PK = celebrity_id#N` where `N` is a random number (0-9). This distributes writes across 10 logical partitions.

```java
int shard = ThreadLocalRandom.current().nextInt(10);
String partitionKey = celebrityId + "#" + shard;
dynamoDb.putItem(partitionKey, ...);
```

On reads, query all 10 shards in parallel and merge the results. Trade-off: reads now require N parallel queries instead of 1.

**Approach 2 — DAX (DynamoDB Accelerator) as Read Buffer**

Place a DAX cluster (in-memory cache) in front of DynamoDB. DAX absorbs read spikes with sub-millisecond latency, shielding DynamoDB from hot partition throttling. This works well for read-heavy workloads but doesn't help with write-heavy hot keys.

**Approach 3 — Tiered Storage with TTL**

Separate hot data (last 24 hours in Redis) from warm data (DynamoDB) and cold data (S3 for analytics). Most traffic hits Redis, which handles hot keys effortlessly.

#### Decision Framework

| Traffic Pattern | Solution |
|-----------------|----------|
| Predictable spikes (scheduled events) | Pre-warm with higher provisioned capacity |
| Unpredictable celebrity spikes | Write sharding + DAX |
| Steady high traffic per key | Redesign partition key (e.g., `timestamp#user`) |
| Read-heavy, write-light | DAX cache |
| Read-heavy, write-heavy | Write sharding + read fanout |

> **Azure Mapping**: Azure Cosmos DB uses logical partitions that elastically scale — hot partitions are automatically split and redistributed. For write-heavy hot keys, use synthetic partition keys. Azure Cache for Redis (Enterprise tier) provides < 1ms reads for hot data.

---

### 16. Redis Cache Causes Production Outage

| | |
|:---|:---|
| **Scenario** | Millions of cache entries expire simultaneously and databases suddenly melt down. |
| **Concepts** | Cache stampede, TTL jitter, request coalescing, multi-level caching |

> Extremely common in real systems.

#### Why It Breaks

The **cache stampede** (also called "dog piling" or "thundering herd"): when a popular cache key expires, all concurrent requesters see a cache miss simultaneously, and ALL of them hit the database with the same expensive query. Imagine 1000 concurrent users all triggering `SELECT * FROM products WHERE trending=true` at the exact same instant. The database gets crushed under 1000 identical heavy queries.

#### Solution Architecture

**Approach 1 — TTL Jitter (Preventative, Simplest)**

Never set the same TTL for all entries. Add random jitter to spread expirations:

```java
// BAD: All expire at the same time
redis.set(key, value, Duration.ofHours(1));

// GOOD: Expire randomly between 50-70 minutes
int baseTtl = 3600;
int jitter = ThreadLocalRandom.current().nextInt(1200); // ±10 min
redis.set(key, value, Duration.ofSeconds(baseTtl + jitter));
```

This spreads re-computation across a 20-minute window instead of a single instant.

**Approach 2 — Probabilistic Early Expiration (PER)**

Before the TTL expires, probabilistically refresh the cache. When TTL < 20% of the original, there's a 30% chance the request will trigger a background refresh. This ensures only a fraction of requests ever hit the database.

**Approach 3 — Request Coalescing (Locking)**

When a cache miss occurs, only ONE request computes the value. Others wait on a distributed lock (Redis `SETNX`):

```java
String lockKey = "lock:refresh:" + key;
Boolean acquired = redis.opsForValue()
    .setIfAbsent(lockKey, "1", Duration.ofSeconds(10));

if (Boolean.TRUE.equals(acquired)) {
    // I'm the designated refresher
    String fresh = expensiveDbQuery(key);
    redis.set(key, fresh, Duration.ofHours(1));
    redis.delete(lockKey);
} else {
    // I'm a waiter — poll cache until value appears
    for (int i = 0; i < 20; i++) {
        Thread.sleep(100);
        String value = redis.get(key);
        if (value != null) return value;
    }
    // Timeout: fall through to DB as last resort
    return expensiveDbQuery(key);
}
```

**Approach 4 — Multi-Level Cache (Defense in Depth)**

| Level | Technology | TTL | Purpose |
|-------|-----------|-----|---------|
| L1 | App in-memory (Caffeine) | 30 sec | Absorb micro-spikes |
| L2 | Redis cluster | 10-60 min | Shared cache, medium latency |
| L3 | DB query cache (Materialized View) | 1 hour | Last resort before full scan |

If L1 has the data (e.g., 30-second in-memory cache), it absorbs the stampede before it reaches Redis or the database.

> **Azure Mapping**: Azure Cache for Redis (Premium with clustering), Redis `SET NX` for distributed locking, Azure SQL's Query Store for materializing frequent queries.

---

### 17. AI Chatbot Gives Wrong Answers

| | |
|:---|:---|
| **Scenario** | Your AI assistant confidently returns incorrect information. |
| **Concepts** | Hallucinations, RAG architecture, vector databases, prompt engineering, context management |

> Modern system design now includes AI infrastructure too.

#### Why It Breaks

LLMs generate text probabilistically — they predict the next token based on training data patterns. They have no concept of "truth." Hallucinations come from:

1. **Training data gaps**: The model was trained on data up to a cutoff date and doesn't know about recent events
2. **Context window limitations**: Relevant information falls outside the context window (even 128K tokens can be insufficient for large knowledge bases)
3. **Poor retrieval**: The RAG system retrieves irrelevant or outdated documents, giving the model wrong "facts" to work with
4. **Over-confidence**: The model presents speculation or extrapolation as established fact

#### Solution Architecture: RAG (Retrieval-Augmented Generation)

The core idea: ground the LLM's response in retrieved documents rather than relying on its training data alone.

**1. Chunking Strategy**

How you split documents dramatically affects retrieval quality:

| Strategy | Best For | Example |
|----------|----------|---------|
| Fixed-size (512 tokens) | General docs | Split by paragraphs |
| Semantic chunking | Technical docs | Split at section boundaries |
| Overlapping sliding window | FAQ-style | 256-token chunks, 64-token overlap |
| Hierarchical | Long documents | Chunk → Summary → Document |

**2. Prompt Engineering to Reduce Hallucination**

```
System: Answer questions SOLELY based on the provided context. If the context 
doesn't contain enough information, say "I don't have enough information to 
answer that question." Do NOT speculate.

Context: {retrieved_chunks}

Instructions:
- Cite the specific source document for each claim
- If multiple sources conflict, note the discrepancy
- Use direct quotes when possible
- Mark confidence level: [High/Medium/Low]
```

**3. Guardrails and Validation**

Before returning an answer, validate it:
- Does the answer contradict the source context? (Use NLI models)
- Is every factual claim grounded in a retrieved chunk?
- Did the model refuse to answer when it should have?

```python
def validate_answer(question, context_chunks, generated_answer):
    # Check: Every factual claim must be grounded in context
    claims = extract_claims(generated_answer)
    for claim in claims:
        if not any(claim_supported(claim, chunk) for chunk in context_chunks):
            return fallback_response(f"Unverified claim: {claim}")
    return generated_answer
```

#### Grounding Spectrum

```
Pure LLM (no RAG)       RAG + Prompting       RAG + Validation      Human-in-loop
[Most hallucinations] ←────────────────────→ [Fewest hallucinations]
[Cheapest]              ←────────────────────→ [Most expensive]
```

> **Azure Mapping**: Azure OpenAI Service for LLM hosting, Azure AI Search for vector/hybrid search, Azure Cosmos DB for MongoDB vCore (native vector support), Azure AI Content Safety for guardrails and hallucination detection.

---

### 18. AI Platform Becomes Very Expensive

| | |
|:---|:---|
| **Scenario** | Your LLM bill unexpectedly explodes after launch. |
| **Concepts** | Prompt optimization, token reduction, model routing, caching responses, hybrid AI architectures |

> This is becoming one of the hottest engineering discussions right now.

#### Why It Breaks

LLM costs are driven by **token count** (input + output tokens). Seemingly small design choices can explode costs:

```
One GPT-4 call with 4000-token context + 500-token output:
  = 4,500 tokens × $0.03/1K + 500 × $0.06/1K 
  = $0.135 + $0.03 = $0.165 per call

At scale: 100K users/day × 5 queries × $0.165 = $82,500/day = $2.5M/month 💸
```

Common cost drivers: oversized context (sending entire conversation history every call), wrong model selection (using GPT-4 for classification), no caching (same question asked 10,000 times at $0.10 each), and verbose system prompts.

#### Solution Architecture

**Layer 1 — Model Router**

Route each request to the cheapest model that can handle it:

```python
class ModelRouter:
    def route(self, request):
        if request.task_type == TaskType.CLASSIFICATION:
            return ModelConfig(model="gpt-3.5-turbo", max_tokens=50)   # Tiny model
        if request.task_type == TaskType.SUMMARIZATION:
            return ModelConfig(model="gpt-4o-mini", max_tokens=200)    # Mid-tier
        if request.task_type == TaskType.COMPLEX_REASONING:
            cached = self.semantic_cache.lookup(request.prompt)         # Check cache
            if cached: return ModelConfig(model="CACHE_HIT", cost=0)
            return ModelConfig(model="gpt-4o", max_tokens=500)         # Only if needed
```

**Layer 2 — Semantic Cache**

Cache LLM responses by semantic similarity, not exact string match. For FAQ and support bots, this can reduce costs by **60-80%**. If a user asks "How do I reset my password?" and another asks "I forgot my password, help!", the semantic cache recognizes they're the same question and returns the cached response.

**Layer 3 — Context Window Optimization**

- Compress the system prompt to essential instructions only (reduce from 2000 → 300 tokens)
- Summarize old conversation messages, keep only recent ones verbatim
- Truncate retrieved documents to the most relevant passages

**Layer 4 — Prompt Compression**

```text
BEFORE (verbose, ~200 tokens):
"You are an expert customer support assistant for ACME Corp, a leading 
provider of cloud-based widget management solutions. Your role is to help 
customers with technical issues, billing questions, account management..."

AFTER (compressed, ~50 tokens → 4x cheaper):
"ACME support bot. Rules: Answer from KB only. No speculation → escalate. 
Hours: M-F 9-5 EST."
```

#### Cost Reduction Impact

| Technique | Cost Reduction | Quality Impact |
|-----------|---------------|----------------|
| Model routing | 40-60% | None (right model for right task) |
| Semantic caching | 60-80% (FAQ bots) | None (identical semantics) |
| Context optimization | 20-30% | Minimal |
| Prompt compression | 10-30% | None (lossless compression) |

> **Azure Mapping**: Azure OpenAI Service with provisioned throughput for predictable pricing, Azure AI Search for semantic caching, Azure Cosmos DB (vCore) for vector cache storage, Azure API Management for rate limiting and quota enforcement.

---

### 19. AI Search Feels Slow

| | |
|:---|:---|
| **Scenario** | Users complain that semantic search takes too long. |
| **Concepts** | Vector indexing, ANN search, embedding optimization, recall vs latency tradeoffs |

#### Why It Breaks

Semantic search involves multiple steps, each adding latency: embedding generation (100-300ms), vector similarity search across millions of embeddings (50-200ms), optional reranking with a cross-encoder (100-500ms), and LLM response generation (500-3000ms). Total: 1.2-4.5 seconds — which feels painfully slow compared to traditional keyword search (~10-50ms).

#### Solution Architecture

**Layer 1 — Approximate Nearest Neighbor (ANN) with Index Tuning**

Exact KNN on 10M vectors is O(N) — far too slow. ANN sacrifices a small amount of recall for massive speed gains:

| Algorithm | Speed | Recall | Memory | Best For |
|-----------|-------|--------|--------|----------|
| HNSW | Very Fast | ~98% | High | Low-dim (≤ 384), in-memory |
| IVF + PQ | Fast | ~95% | Low | High-dim (≥ 768), disk-backed |
| DiskANN | Medium | ~99% | Very Low | Billion-scale, SSD-based |

**Layer 2 — Hybrid Search (Sparse + Dense)**

Combine fast keyword search (BM25, ~5ms) with semantic vector search (~100ms). Show keyword results immediately, then refine with semantic results. The fusion uses Reciprocal Rank Fusion (RRF) to merge rankings.

**Layer 3 — Streaming for Perceived Performance**

Show results as they become available — don't wait for everything:
1. Return keyword results immediately (fast first paint)
2. Compute embeddings and refine with semantic results
3. Generate LLM-powered summary (if needed)

**Layer 4 — Embedding Model Selection**

Smaller models = faster embeddings with acceptable quality trade-off:

| Model | Dimension | Speed (sentences/sec) | Use Case |
|-------|-----------|----------------------|----------|
| `all-MiniLM-L6-v2` | 384 | 14,000 | Real-time search |
| `bge-small-en` | 384 | 10,000 | Balanced |
| `text-embedding-3-small` | 512 | 5,000 | OpenAI ecosystem |
| `text-embedding-3-large` | 3072 | 1,000 | Offline/batch only |

#### Latency Budget (Target: < 700ms)

| Component | Target | Optimization |
|-----------|--------|-------------|
| Embedding generation | < 50ms | Smaller model, GPU, batching |
| Vector search | < 30ms | HNSW, ef_search tuning |
| Reranking | < 100ms | Only rerank top-20, not top-100 |
| LLM generation | < 500ms | Streaming, short outputs |

> **Azure Mapping**: Azure AI Search with vector search (HNSW indexing), Azure Kubernetes Service for self-hosted vector DBs with GPU nodes, Azure OpenAI `text-embedding-3-small` for balanced speed/quality.

---

### 20. OTP Service Fails During Peak Traffic

| | |
|:---|:---|
| **Scenario** | Users stop receiving OTPs during login spikes. |
| **Concepts** | Rate limiting, retry storms, provider failover, queue buffering |

#### Why It Breaks

OTP delivery involves a third-party SMS provider with hard limits (e.g., 500 OTP/sec). When traffic spikes to 2000 OTP/sec, 1500/sec get rejected. Then the **retry storm** begins: users who don't receive OTPs tap "Resend" repeatedly — turning 2000 requests into 8000+. The provider melts down completely.

This is a classic amplification feedback loop: failed requests → user retries → more failed requests → more retries.

#### Solution Architecture

**Layer 1 — Client-Side Debouncing (Prevent Retry Storms)**

Disable the resend button for 30 seconds after each request:

```javascript
let cooldown = 30; // seconds
resendButton.disabled = true;

const interval = setInterval(() => {
    resendButton.textContent = `Resend in ${--cooldown}s`;
    if (cooldown <= 0) {
        clearInterval(interval);
        resendButton.disabled = false;
        resendButton.textContent = "Resend OTP";
    }
}, 1000);
```

**Layer 2 — Token Bucket Rate Limiter (Prevent Provider Overload)**

```java
private final RateLimiter limiter = RateLimiter.create(500.0); // 500/sec

public OtpResult sendOtp(String phone, String otp) {
    if (!limiter.tryAcquire(1, TimeUnit.SECONDS)) {
        return OtpResult.rateLimited("High demand — try again in a moment");
    }
    return smsProvider.send(phone, "Your OTP: " + otp);
}
```

**Layer 3 — Multi-Provider with Circuit Breaker Failover**

```
Provider priority chain: Twilio (primary) → Sinch (secondary) → AWS SNS (fallback)
```

Each provider has its own circuit breaker. When the primary opens, traffic automatically flows to the secondary. When the secondary opens, it falls to SNS.

**Layer 4 — Queue Buffering with Load Shedding**

Use a bounded queue (e.g., 50,000 capacity). Store OTP hashes immediately so users can verify even if delivery is delayed. If the queue is full, return a "try again later" response instead of accepting the request and crashing.

#### Mitigation Summary

| Problem | Solution |
|---------|----------|
| Provider rate limit exceeded | Token bucket rate limiter at gateway |
| User retry storm | Client-side debouncing (30s cooldown) |
| Single provider failure | Multi-provider with circuit breaker failover |
| Traffic spike overflows memory | Bounded queue + load shedding |
| OTP expires before delivery | Store OTP first, deliver async with 5-min TTL |

> **Azure Mapping**: Azure Communication Services for SMS (built-in retry + delivery reports), Azure API Management with rate-limiting policies, Azure Cache for Redis for OTP storage with TTL, Azure Service Bus queue for buffered dispatch.

---

### 21. One Microservice Takes Down Entire Platform

| | |
|:---|:---|
| **Scenario** | A single unhealthy service triggers cascading failures everywhere. |
| **Concepts** | Circuit breakers, bulkheads, timeouts, resilience engineering |

> This is where microservices become dangerous if poorly designed.

#### Why It Breaks

The cascade: Payment Service slows down (DB connection leak) → Order Service threads all block waiting for Payment responses → API Gateway threads all block waiting for Order → ALL services become unreachable, even completely healthy ones like Inventory and Notifications.

The root cause: **synchronous calls with unbounded wait times and shared thread pools**. One slow dependency consumes all available threads, starving other dependencies.

#### Solution Architecture

**Pattern 1 — Circuit Breaker**

Stop calling a failing service after a threshold of failures. This prevents wasting resources on doomed calls.

```java
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
public PaymentResponse validatePayment(PaymentRequest request) {
    return paymentClient.validate(request);
}

public PaymentResponse paymentFallback(PaymentRequest request, Exception e) {
    // Graceful degradation: allow order with "payment pending" status
    log.warn("Payment service unavailable — proceeding with pending status");
    return PaymentResponse.pending();
}
```

Configuration: Open the circuit if 50% of calls fail or are slow (>2s). Stay open for 30 seconds, then try a few requests (half-open state) before closing again.

**Pattern 2 — Bulkhead (Thread Pool Isolation)**

Assign separate thread pools to each downstream dependency. If Payment Service stalls, only its thread pool is affected — Inventory and other services continue working normally.

```java
@Bean("paymentExecutor")
public ExecutorService paymentExecutor() {
    return new ThreadPoolExecutor(10, 20, 60L, TimeUnit.SECONDS,
        new LinkedBlockingQueue<>(100),
        new ThreadPoolExecutor.CallerRunsPolicy() // Apply backpressure
    );
}
```

**Pattern 3 — Timeouts Everywhere**

Never wait indefinitely. Set aggressive timeouts: connect timeout (2s), socket timeout (3s), and a `@TimeLimiter` annotation that fails fast if a call exceeds its deadline.

**Pattern 4 — Retry with Exponential Backoff**

Retries without backoff amplify the problem. Use exponential backoff with jitter: 500ms → 1s → 2s between attempts. This gives the downstream service time to recover.

#### The Resilience Stack

```
Request → Timeout (fail fast, don't hang)
        → Retry (transient failures, with backoff + jitter)
        → Circuit Breaker (persistent failures, stop trying)
        → Bulkhead (isolate failure, protect other services)
        → Fallback (graceful degradation)
```

| Pattern | What It Does | When to Use |
|---------|-------------|-------------|
| Timeout | Caps wait time | Always — every call needs a deadline |
| Retry | Retries transient failures | Network blips, brief outages |
| Circuit Breaker | Stops calling dead services | Persistent failures |
| Bulkhead | Isolates thread pools | Protect other services from one bad dependency |
| Fallback | Returns degraded response | When all else fails |

> **Azure Mapping**: Azure API Management has built-in circuit breaker and retry policies. Azure Monitor detects cascading failures. Azure Load Testing for chaos engineering and resilience validation.

---

### 22. API Gateway Becomes a Bottleneck

| | |
|:---|:---|
| **Scenario** | Your API gateway starts slowing down all requests. |
| **Concepts** | Authentication overhead, gateway scaling, edge caching, request routing optimization |

#### Why It Breaks

The API gateway is the **single entry point** for all traffic. Every request passes through it. Common bottlenecks stack up: JWT validation on every request (10-50ms), TLS termination (CPU-intensive), JSON parsing and transformation (500 MB/sec at scale), logging/metrics generation, and connection pooling to all backend services.

At 10,000 req/sec, 20ms of auth overhead alone consumes 200 CPU-cores worth of processing — just for authentication.

#### Solution Architecture

**Layer 1 — Move Auth to the Edge (Token Introspection Caching)**

Don't call the auth service on every request. Cache token validation results for 60 seconds:

```java
// Cache: "auth:token:{hash}" → user context, TTL = min(token.expiry, 60s)
String cached = redis.get("auth:token:" + hash(token));
if (cached != null) {
    setUserContext(exchange, cached);  // Skip auth service call entirely
} else {
    User user = authService.validate(token);
    redis.set("auth:token:" + hash(token), user, Duration.ofSeconds(60));
}
```

Result: Auth overhead drops from 20ms to < 1ms for 95%+ of requests.

**Layer 2 — Offload TLS Termination**

Terminate TLS at a hardware load balancer or CDN edge (CloudFront, Azure Front Door), not at the application gateway. Internal traffic between the load balancer and gateway uses plain HTTP within the VPC. This reduces gateway CPU usage by 30-50%.

**Layer 3 — Response Caching at the Gateway**

Cache responses for idempotent GET requests (product lists, configuration, reference data). A 60-second cache on high-traffic endpoints can eliminate 90%+ of backend calls.

**Layer 4 — Horizontal Scaling**

API gateways are stateless — scale them horizontally behind a load balancer. Use Kubernetes HPA (Horizontal Pod Autoscaler) with CPU and memory targets. For burst protection, configure pod over-provisioning or keep a warm pool.

**Layer 5 — Rate Limiting Before Backend**

Stop abusive traffic at the gateway — don't let it reach backend services. Use Redis-backed token bucket rate limiters configured per API key or IP address.

#### Bottleneck Mitigation Summary

| Bottleneck | Fix | Impact |
|-----------|-----|--------|
| Auth validation per request | Token caching (60s TTL) | 95%+ CPU reduction for auth |
| TLS termination | Offload to CDN/load balancer | 30-50% CPU reduction |
| Repeated identical responses | Gateway-level response cache | 90%+ reduction for cacheable endpoints |
| Abusive clients | Rate limiting at edge | Prevents backend saturation |
| Connection setup overhead | Connection reuse + keep-alive | 20% latency improvement |

> **Azure Mapping**: Azure Front Door (global TLS termination + caching), Azure Application Gateway (layer-7 routing + WAF), Azure API Management (rate limiting, auth caching, response caching, circuit breaking), Azure Cache for Redis (token cache + rate limiter storage).

---

## Domain Summary

| Domain | Questions | Core Skills |
|--------|-----------|-------------|
| **Caching & CDN** | #1, #5, #7, #16 | Redis, CDN, invalidation, stampede prevention |
| **Messaging & Async** | #2, #8, #11, #12, #13 | Kafka, idempotency, ordering, backpressure |
| **Concurrency & Transactions** | #4, #9 | Locks, sagas, distributed transactions |
| **Real-Time & Streaming** | #3, #6 | GPS, WebSockets, stream processing |
| **Scalability & Resilience** | #14, #15, #20, #21, #22 | Sharding, circuit breakers, rate limiting |
| **AI/ML Infrastructure** | #17, #18, #19 | RAG, vectors, LLM cost optimization |
| **Media Processing** | #10 | Chunking, encoding pipelines |

---

## Final Thoughts

The biggest shift happening in software engineering interviews is this:

> **Companies are no longer hiring developers who only know frameworks. They are hiring engineers who understand failure.**

Because at scale: networks fail, retries happen, caches become inconsistent, databases slow down, queues overflow, AI systems hallucinate, and traffic behaves unpredictably.

So while preparing for interviews, don't just memorize architecture diagrams.

Instead, train yourself to think like this: *"What happens when this system breaks under real production pressure?"*

That single mindset shift can completely change how you approach distributed systems, backend engineering, scalability, reliability, and architecture interviews.

> **Designing systems is easy. Designing systems that survive chaos is the real skill.**

---

*Originally published by Arvind Kumar on [Medium](https://medium.com/@arvindkumar).*

> **Source URL**: [22 Scenario-Based System Design Questions](https://medium.com/@arvindkumar/22-scenario-based-system-design-questions)
>
> **Taxonomy Reference**: §7.1 Reliability & Resilience, §3.3 Event-Driven Architecture, §2.2 Concurrency, §4.1 Data & Analytics
> **Related**: [20 Design Interview Questions](20-design-interview-questions.md) | [System Design Reference](../../system-design-architecture/README.md) | [Kafka Anti-Patterns](kafka-anti-patterns/01-kafka-mistakes-breaking-your-system.md)
