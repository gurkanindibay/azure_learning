# Reliability, Performance & Operations – Patterns Reference

This document provides a detailed reference of patterns for **reliability, performance, and operations** in distributed systems and cloud-native architectures.

---

## Table of Contents

<details>
<summary><a href="#71-reliability-architecture">7.1 Reliability Architecture</a></summary>

  - [High Availability (HA)](#high-availability-ha)
  - [Disaster Recovery (DR)](#disaster-recovery-dr)
  - [Fault-Tolerant Architecture](#fault-tolerant-architecture)
  - [Chaos Engineering Architecture](#chaos-engineering-architecture)
  - [Resilience Patterns](#resilience-patterns)
</details>

<details>
<summary><a href="#72-performance-architecture">7.2 Performance Architecture</a></summary>

  - [Low-Latency Architecture](#low-latency-architecture)
  - [Caching Architecture](#caching-architecture)
  - [Load Balancing Architecture](#load-balancing-architecture)
  - [Edge Optimization](#edge-optimization)
  - [Performance Patterns](#performance-patterns)
</details>

<details>
<summary><a href="#73-observability-architecture">7.3 Observability Architecture</a></summary>

  - [Logging Architecture](#logging-architecture)
  - [Metrics Architecture](#metrics-architecture)
  - [Distributed Tracing](#distributed-tracing)
  - [Monitoring Architecture](#monitoring-architecture)
  - [Observability Patterns](#observability-patterns)
</details>

---

## 7.1 Reliability Architecture

Reliability architecture focuses on ensuring systems remain operational and can recover from failures gracefully.

### High Availability (HA)

High Availability ensures systems remain accessible with minimal downtime.

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Active-Active** | Multiple instances handle traffic simultaneously | Global applications, maximum availability |
| **Active-Passive** | Standby instance takes over on primary failure | Cost-sensitive HA, regional failover |
| **N+1 Redundancy** | One extra instance beyond minimum required | Planned maintenance without downtime |
| **Geographic Redundancy** | Instances across multiple regions/zones | Disaster tolerance, latency optimization |

**Key Metrics:**
- Availability percentage (99.9%, 99.99%, etc.)
- Recovery Time Objective (RTO)
- Recovery Point Objective (RPO)

---

### Disaster Recovery (DR)

Disaster Recovery ensures business continuity after catastrophic failures.

| Strategy | RTO | RPO | Cost | Description |
|----------|-----|-----|------|-------------|
| **Backup & Restore** | Hours | Hours | $ | Restore from backups when disaster occurs |
| **Pilot Light** | Minutes-Hours | Minutes | $$ | Minimal always-on infrastructure, scale up on disaster |
| **Warm Standby** | Minutes | Seconds-Minutes | $$$ | Scaled-down replica ready to scale up |
| **Hot Standby / Multi-Site** | Seconds | Near-zero | $$$$ | Full replica running, instant failover |

**DR Planning Considerations:**
- Data replication strategy (sync vs async)
- Failover automation
- Failback procedures
- Regular DR drills

---

### Fault-Tolerant Architecture

Fault tolerance allows systems to continue operating despite component failures.

| Approach | Description |
|----------|-------------|
| **Redundancy** | Duplicate critical components |
| **Replication** | Copy data across multiple nodes |
| **Graceful Degradation** | Reduce functionality rather than fail completely |
| **Fail-Safe Defaults** | Safe state when failures occur |
| **Isolation** | Contain failures to prevent cascade |

---

### Chaos Engineering Architecture

Proactively test system resilience by introducing controlled failures.

| Principle | Description |
|-----------|-------------|
| **Hypothesis-Driven** | Define expected behavior before experiments |
| **Minimize Blast Radius** | Start small, limit impact |
| **Run in Production** | Real environment reveals real issues |
| **Automate Experiments** | Continuous resilience validation |

**Common Chaos Experiments:**
- Instance termination
- Network latency injection
- Dependency failure simulation
- Resource exhaustion (CPU, memory, disk)
- Clock skew

**Tools:** Chaos Monkey, Gremlin, Litmus, Azure Chaos Studio

---

### Resilience Patterns

Patterns that help systems recover from and adapt to failures.

#### Circuit Breaker Pattern

Prevents cascading failures by stopping calls to failing services.

```
States:
┌─────────┐    failure threshold    ┌──────┐
│ CLOSED  │ ────────────────────▶  │ OPEN │
└─────────┘                         └──────┘
     ▲                                  │
     │         timeout expires          ▼
     │                            ┌──────────┐
     └─────── success ◀────────── │HALF-OPEN│
                                  └──────────┘
```

| State | Behavior |
|-------|----------|
| **Closed** | Requests flow normally, failures counted |
| **Open** | Requests fail immediately (fail fast) |
| **Half-Open** | Limited requests allowed to test recovery |

---

#### Retry Pattern

Automatically retry failed operations with configurable strategies.

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Immediate Retry** | Retry instantly | Transient glitches |
| **Fixed Interval** | Wait fixed time between retries | Simple scenarios |
| **Exponential Backoff** | Double wait time each retry | Overloaded services |
| **Exponential with Jitter** | Backoff + random delay | Prevent thundering herd |

**Best Practices:**
- Set maximum retry count
- Only retry idempotent operations
- Use circuit breaker to stop retrying failing services

---

#### Bulkhead Pattern

Isolates components to prevent failure propagation.

| Type | Description |
|------|-------------|
| **Thread Pool Isolation** | Separate thread pools per dependency |
| **Connection Pool Isolation** | Dedicated connection pools |
| **Process Isolation** | Separate processes/containers |
| **Service Isolation** | Separate service instances |

```
┌─────────────────────────────────────────┐
│              Application                 │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Pool A   │  │ Pool B   │  │ Pool C │ │
│  │ Service1 │  │ Service2 │  │ Service3│ │
│  └──────────┘  └──────────┘  └────────┘ │
└─────────────────────────────────────────┘
If Service2 fails, only Pool B is affected
```

---

#### Timeout Pattern

Bound the time spent waiting for responses.

| Consideration | Guidance |
|---------------|----------|
| **Connection Timeout** | Time to establish connection |
| **Read Timeout** | Time to receive response |
| **Total Timeout** | End-to-end operation time |
| **Cascading Timeouts** | Upstream timeout > downstream timeout |

---

#### Fallback Pattern

Provide alternative responses when primary operation fails.

| Strategy | Description |
|----------|-------------|
| **Default Value** | Return safe default |
| **Cached Response** | Return last known good value |
| **Alternative Service** | Call backup service |
| **Graceful Degradation** | Reduced functionality |
| **Queue for Later** | Store request for retry |

---

#### Rate Limiting Pattern

Protect services from overload by limiting request rates.

| Algorithm | Description |
|-----------|-------------|
| **Token Bucket** | Tokens replenish at fixed rate, requests consume tokens |
| **Leaky Bucket** | Requests queue and process at fixed rate |
| **Fixed Window** | Count requests in fixed time windows |
| **Sliding Window** | Rolling window for smoother limiting |

---

#### Health Check Pattern

Enable systems to monitor component health.

| Type | Purpose |
|------|---------|
| **Liveness** | Is the service running? (restart if not) |
| **Readiness** | Is the service ready to accept traffic? |
| **Startup** | Has the service finished initializing? |
| **Deep Health** | Check dependencies and downstream services |

---

## 7.2 Performance Architecture

Performance architecture focuses on optimizing response times, throughput, and resource efficiency.

### Low-Latency Architecture

Minimize response time for time-sensitive applications.

| Technique | Description |
|-----------|-------------|
| **In-Memory Computing** | Keep data in RAM for fast access |
| **Connection Pooling** | Reuse connections to avoid setup overhead |
| **Async Processing** | Non-blocking I/O operations |
| **Colocation** | Place services near data and users |
| **Optimized Serialization** | Use efficient formats (protobuf, MessagePack) |

---

### Caching Architecture

Store frequently accessed data closer to consumers.

#### Cache Placement Patterns

| Pattern | Location | Use Case |
|---------|----------|----------|
| **Client-Side Cache** | Browser/App | Static assets, user preferences |
| **CDN Cache** | Edge locations | Static content, media |
| **API Gateway Cache** | Gateway layer | API responses |
| **Application Cache** | Service memory | Computed results, sessions |
| **Distributed Cache** | Dedicated cache cluster | Shared data across instances |
| **Database Cache** | DB query cache | Query results |

#### Cache Strategies

| Strategy | Description | Consistency |
|----------|-------------|-------------|
| **Cache-Aside (Lazy Loading)** | App checks cache, loads from DB on miss | Eventually consistent |
| **Read-Through** | Cache loads from DB transparently | Eventually consistent |
| **Write-Through** | Write to cache and DB simultaneously | Strong consistency |
| **Write-Behind (Write-Back)** | Write to cache, async write to DB | Eventually consistent |
| **Refresh-Ahead** | Proactively refresh before expiry | Eventually consistent |

#### Cache Invalidation

| Method | Description |
|--------|-------------|
| **TTL (Time-To-Live)** | Automatic expiration after duration |
| **Event-Based** | Invalidate on data change events |
| **Version-Based** | Include version in cache key |
| **Manual Purge** | Explicit invalidation API |

---

### Load Balancing Architecture

Distribute traffic across multiple instances.

#### Load Balancing Algorithms

| Algorithm | Description | Use Case |
|-----------|-------------|----------|
| **Round Robin** | Rotate through instances sequentially | Equal capacity instances |
| **Weighted Round Robin** | Proportional distribution by weight | Different capacity instances |
| **Least Connections** | Route to instance with fewest connections | Long-lived connections |
| **Least Response Time** | Route to fastest responding instance | Performance optimization |
| **IP Hash** | Route based on client IP | Session affinity without cookies |
| **Random** | Random instance selection | Simple, stateless |

#### Load Balancer Types

| Type | OSI Layer | Features |
|------|-----------|----------|
| **L4 (Transport)** | Layer 4 | TCP/UDP, fast, connection-based |
| **L7 (Application)** | Layer 7 | HTTP, content-based routing, SSL termination |
| **Global Load Balancer** | DNS-based | Geographic routing, failover |

---

### Edge Optimization

Process data and serve content closer to users.

| Pattern | Description |
|---------|-------------|
| **CDN** | Cache static content at edge locations |
| **Edge Computing** | Run compute at edge nodes |
| **Edge Functions** | Serverless functions at CDN edge |
| **Edge Caching** | Dynamic content caching at edge |

---

### Performance Patterns

#### Connection Pool Pattern

Maintain a pool of reusable connections.

| Parameter | Description |
|-----------|-------------|
| **Min Pool Size** | Minimum connections to maintain |
| **Max Pool Size** | Maximum connections allowed |
| **Idle Timeout** | Close idle connections after duration |
| **Connection Lifetime** | Maximum age of connection |

---

#### Batching Pattern

Combine multiple operations into single batch.

| Benefit | Description |
|---------|-------------|
| **Reduced Overhead** | Fewer round trips |
| **Better Throughput** | Bulk processing efficiency |
| **Network Efficiency** | Less protocol overhead |

**Considerations:**
- Batch size limits
- Latency vs throughput tradeoff
- Partial failure handling

---

#### Throttling Pattern

Control resource consumption rate.

| Strategy | Description |
|----------|-------------|
| **Request Throttling** | Limit requests per time window |
| **Bandwidth Throttling** | Limit data transfer rate |
| **Resource Throttling** | Limit CPU/memory usage |
| **Priority-Based** | Different limits per tier/customer |

---

#### Async Request-Reply Pattern

Handle long-running operations without blocking.

```
Client          API             Worker
  │              │                │
  ├──Request────▶│                │
  │◀──202 + URL──┤                │
  │              ├──Queue Job────▶│
  │              │                ├──Process
  │──Poll URL───▶│                │
  │◀──202────────┤                │
  │              │◀──Complete─────┤
  │──Poll URL───▶│                │
  │◀──200+Result─┤                │
```

---

#### Materialized View Pattern

Pre-compute and store query results.

| Benefit | Description |
|---------|-------------|
| **Query Performance** | Avoid complex joins at read time |
| **Denormalization** | Optimized read schema |
| **Cross-Service Data** | Aggregate from multiple sources |

**Refresh Strategies:**
- Scheduled rebuild
- Incremental update
- Event-driven update

---

## 7.3 Observability Architecture

Observability provides insight into system behavior through logs, metrics, and traces.

### The Three Pillars of Observability

| Pillar | Purpose | Data Type |
|--------|---------|-----------|
| **Logs** | Record discrete events | Text/structured records |
| **Metrics** | Measure system state over time | Numeric time series |
| **Traces** | Track request flow across services | Span trees |

---

### Logging Architecture

Capture and aggregate system events for analysis.

#### Log Levels

| Level | Purpose | Example |
|-------|---------|---------|
| **TRACE** | Fine-grained debug info | Method entry/exit |
| **DEBUG** | Diagnostic information | Variable values |
| **INFO** | Normal operations | Request completed |
| **WARN** | Potential issues | Retry occurred |
| **ERROR** | Failures | Exception caught |
| **FATAL** | Critical failures | System shutdown |

#### Structured Logging

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "order-service",
  "traceId": "abc123",
  "message": "Order processed",
  "orderId": "ORD-456",
  "customerId": "CUST-789",
  "duration_ms": 150
}
```

#### Log Aggregation Patterns

| Pattern | Description |
|---------|-------------|
| **Centralized Logging** | Ship all logs to central store |
| **Log Shipping** | Agent pushes logs to aggregator |
| **Log Streaming** | Stream logs via message queue |
| **Sidecar Logging** | Sidecar container collects logs |

**Tools:** ELK Stack, Splunk, Azure Monitor, Datadog, Loki

---

### Metrics Architecture

Collect numeric measurements over time.

#### Metric Types

| Type | Description | Example |
|------|-------------|---------|
| **Counter** | Cumulative, only increases | Total requests |
| **Gauge** | Point-in-time value | Current memory usage |
| **Histogram** | Distribution of values | Request latency buckets |
| **Summary** | Quantiles over sliding window | P95 latency |

#### Key Metrics Categories

| Category | Metrics |
|----------|---------|
| **RED (Services)** | Rate, Errors, Duration |
| **USE (Resources)** | Utilization, Saturation, Errors |
| **Golden Signals** | Latency, Traffic, Errors, Saturation |

#### Metrics Collection Patterns

| Pattern | Description |
|---------|-------------|
| **Push Model** | Service pushes metrics to collector |
| **Pull Model** | Collector scrapes metrics endpoint |
| **StatsD** | Push UDP packets for aggregation |
| **Prometheus** | Pull-based scraping with exporters |

**Tools:** Prometheus, Grafana, Azure Monitor, CloudWatch, Datadog

---

### Distributed Tracing

Track requests across service boundaries.

#### Tracing Concepts

| Concept | Description |
|---------|-------------|
| **Trace** | End-to-end request journey |
| **Span** | Single operation within trace |
| **Context Propagation** | Pass trace ID across services |
| **Baggage** | Metadata carried with trace |

#### Trace Structure

```
Trace ID: abc-123
│
├─ Span: API Gateway (50ms)
│  │
│  ├─ Span: Auth Service (10ms)
│  │
│  └─ Span: Order Service (35ms)
│     │
│     ├─ Span: Database Query (15ms)
│     │
│     └─ Span: Payment Service (18ms)
│        │
│        └─ Span: External Payment API (12ms)
```

#### Sampling Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Head-Based** | Decide at trace start | Consistent, simple |
| **Tail-Based** | Decide after trace complete | Keep interesting traces |
| **Rate-Based** | Sample percentage of traces | Control volume |
| **Priority-Based** | Sample based on attributes | Focus on important flows |

#### Tracing Instrumentation APIs

Unlike logs and metrics which can often be collected passively, **distributed tracing requires specialized APIs/SDKs** because traces must be explicitly managed throughout their lifecycle.

| Requirement | Why API is Needed |
|-------------|-------------------|
| **Trace/Span Lifecycle** | Create, start, and end spans programmatically |
| **Context Propagation** | Inject/extract trace context across service boundaries |
| **Span Attributes** | Add metadata (tags, events, status codes) |
| **Sampling Decisions** | Control which traces are recorded |
| **Export Configuration** | Send trace data to backends |

**Instrumentation Approaches:**

| Approach | Description | Effort |
|----------|-------------|--------|
| **Auto-Instrumentation** | Agent/library automatically instruments common frameworks | Low |
| **Manual Instrumentation** | Developer explicitly creates spans via SDK | High |
| **Hybrid** | Auto for frameworks, manual for business logic | Medium |

**Example Flow (Conceptual):**

```
// Service A - Start trace at entry point
tracer = TracerProvider.GetTracer("order-service")
span = tracer.StartSpan("process-order")
span.SetAttribute("orderId", orderId)

// Inject context into outgoing HTTP headers
propagator.Inject(currentContext, httpRequest.Headers)

// ... call Service B ...

span.End()

// -------------------------------------------

// Service B - Extract context and continue trace
parentContext = propagator.Extract(httpRequest.Headers)
childSpan = tracer.StartSpan("validate-payment", parentContext)

// Child span automatically linked to parent trace
childSpan.SetAttribute("paymentMethod", method)
childSpan.End()
```

**Key APIs/SDKs:**
- **OpenTelemetry SDK** - Modern standard (recommended)
- **Application Insights SDK** - Azure APM
- **Jaeger/Zipkin Clients** - Backend-specific libraries

**Standards:** OpenTelemetry, W3C Trace Context, Jaeger, Zipkin

#### Tracing Performance Considerations

Tracing introduces overhead that must be carefully managed in production systems.

| Impact Area | Description |
|-------------|-------------|
| **CPU Overhead** | Creating spans, serializing context, and exporting data consume CPU cycles |
| **Memory Overhead** | Spans and attributes are held in memory until exported |
| **Latency** | Context injection/extraction adds microseconds to each request |
| **Network Overhead** | Exporting traces to backends consumes bandwidth |
| **Storage Costs** | High-volume traces require significant backend storage |

**Typical Overhead:**

| Scenario | Latency Impact |
|----------|----------------|
| **Auto-instrumentation** | ~1-5% increase |
| **Manual instrumentation** | Depends on span count |
| **Synchronous export** | Significant (avoid!) |
| **Async batch export** | Minimal |
| **High-cardinality attributes** | Increased memory/storage |

**Mitigation Strategies:**

| Strategy | Benefit |
|----------|---------|
| **Use sampling** | Reduces volume; don't trace 100% in high-traffic production |
| **Async export** | Never block requests waiting for trace export |
| **Batch exports** | Reduce network calls by batching spans |
| **Limit span attributes** | Avoid high-cardinality data (e.g., user IDs as attributes) |
| **Head-based sampling** | Decide early to avoid wasted instrumentation work |
| **Tail-based sampling** | Keep only interesting traces (errors, slow requests) |

**Sampling Trade-offs:**

| Sample Rate | Overhead | Visibility |
|-------------|----------|------------|
| **100%** | High | Complete - see every request |
| **10%** | Low | Statistical - representative sample |
| **1%** | Minimal | High-traffic systems only |
| **Adaptive** | Variable | Adjusts based on traffic/errors |

> **Best Practice:** Start with a low sample rate in production and increase only for specific debugging sessions or error conditions. Use tail-based sampling to automatically capture problematic traces.

---

### Monitoring Architecture

Actively watch systems and alert on anomalies.

#### Monitoring Types

| Type | Focus |
|------|-------|
| **Infrastructure Monitoring** | Servers, containers, networks |
| **Application Monitoring (APM)** | Application performance |
| **Real User Monitoring (RUM)** | Actual user experience |
| **Synthetic Monitoring** | Simulated transactions |
| **Business Monitoring** | Business KPIs |

#### Alerting Patterns

| Pattern | Description |
|---------|-------------|
| **Threshold Alerts** | Alert when metric crosses threshold |
| **Anomaly Detection** | ML-based unusual behavior detection |
| **Rate of Change** | Alert on rapid changes |
| **Composite Alerts** | Multiple conditions combined |

#### Alert Best Practices

| Principle | Description |
|-----------|-------------|
| **Actionable** | Every alert should have clear action |
| **Severity Levels** | Critical, Warning, Info |
| **Runbooks** | Link to remediation procedures |
| **Avoid Alert Fatigue** | Tune thresholds, dedupe alerts |
| **On-Call Rotation** | Sustainable incident response |

---

### Observability Patterns

#### Correlation ID Pattern

Track related events across systems.

```
Request → API Gateway → Service A → Service B → Database
           │              │            │           │
    correlationId    correlationId  correlationId  correlationId
       = xyz           = xyz         = xyz         = xyz
```

---

#### Health Endpoint Pattern

Expose health status via HTTP endpoint.

```
GET /health
{
  "status": "healthy",
  "checks": {
    "database": { "status": "healthy", "latency_ms": 5 },
    "cache": { "status": "healthy", "latency_ms": 1 },
    "external-api": { "status": "degraded", "latency_ms": 500 }
  },
  "version": "1.2.3"
}
```

---

#### Dashboard Pattern

Visualize system state for operators.

| Dashboard Type | Content |
|----------------|---------|
| **Overview** | High-level system health |
| **Service Dashboard** | Per-service metrics |
| **Infrastructure** | Resource utilization |
| **Business** | Business metrics, KPIs |
| **Incident** | Real-time incident view |

---

#### Log Correlation Pattern

Link logs, metrics, and traces together.

| Field | Purpose |
|-------|---------|
| **Trace ID** | Link to distributed trace |
| **Span ID** | Link to specific operation |
| **Request ID** | Correlation across logs |
| **User ID** | Track user journey |
| **Session ID** | Group user session |

---

## Summary: Pattern Quick Reference

### Reliability Patterns

| Pattern | Purpose |
|---------|---------|
| Circuit Breaker | Prevent cascading failures |
| Retry | Handle transient failures |
| Bulkhead | Isolate failures |
| Timeout | Bound response time |
| Fallback | Alternative on failure |
| Rate Limiting | Prevent overload |
| Health Check | Monitor component health |

### Performance Patterns

| Pattern | Purpose |
|---------|---------|
| Caching | Reduce latency, load |
| Connection Pool | Reuse connections |
| Batching | Reduce round trips |
| Throttling | Control consumption |
| Async Request-Reply | Handle long operations |
| Materialized View | Pre-compute results |

### Observability Patterns

| Pattern | Purpose |
|---------|---------|
| Structured Logging | Queryable log data |
| Distributed Tracing | Track request flow |
| Correlation ID | Link related events |
| Health Endpoint | Expose service health |
| Dashboard | Visualize system state |

---

**Status:** Living document – patterns should be selected based on specific system requirements and constraints.
