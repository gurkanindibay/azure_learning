# The Four Golden Signals

## Table of Contents

- [Overview](#overview)
- [Origin and Philosophy](#origin-and-philosophy)
- [The Four Signals](#the-four-signals)
  - [1. Latency](#1-latency)
  - [2. Traffic](#2-traffic)
  - [3. Errors](#3-errors)
  - [4. Saturation](#4-saturation)
- [Implementation Guidelines](#implementation-guidelines)
- [Alerting on Golden Signals](#alerting-on-golden-signals)
- [Dashboard Design](#dashboard-design)
- [Golden Signals by Service Type](#golden-signals-by-service-type)
- [Relationship to Other Methodologies](#relationship-to-other-methodologies)
- [Common Pitfalls](#common-pitfalls)
- [Tools and Implementation](#tools-and-implementation)

---

## Overview

The **Four Golden Signals** are a monitoring framework introduced by Google in their Site Reliability Engineering (SRE) book. They represent the most critical metrics for understanding the health of a distributed system from a user's perspective.

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE FOUR GOLDEN SIGNALS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ⏱️ LATENCY          📊 TRAFFIC          ❌ ERRORS            │
│    How long does      How much demand     How often do         │
│    it take?           is there?           things fail?         │
│                                                                  │
│                       📈 SATURATION                              │
│                       How "full" is                              │
│                       the system?                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> "If you can only measure four metrics of your user-facing system, focus on these four."
> — Google SRE Book

---

## Origin and Philosophy

### Why Four Signals?

Google's SRE team found that these four metrics provide:

1. **Completeness**: Together they cover the key dimensions of service health
2. **Simplicity**: Easy to understand and implement
3. **Actionability**: Deviations point to specific problem areas
4. **User Focus**: All relate directly to user experience

### When to Use Golden Signals

| Use Case | Applicability |
|----------|---------------|
| Request-driven services (APIs, web apps) | ✅ Excellent |
| Storage systems | ✅ Very Good |
| Batch processing pipelines | ⚠️ Adapt with care |
| Infrastructure (CPU, memory) | ⚠️ Consider USE Method instead |

---

## The Four Signals

### 1. Latency

**Definition**: The time it takes to service a request.

#### Key Distinctions

```
┌─────────────────────────────────────────────────────────────┐
│                      LATENCY TYPES                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SUCCESSFUL REQUEST LATENCY                                  │
│  ═══════════════════════════                                │
│  • Time for requests that complete successfully              │
│  • The "normal" user experience                              │
│  • Track P50, P95, P99 percentiles                          │
│                                                              │
│  FAILED REQUEST LATENCY                                      │
│  ══════════════════════                                      │
│  • Time for requests that fail                               │
│  • Often very different from success latency                │
│  • A fast error can mask slow service degradation           │
│                                                              │
│  ⚠️  CRITICAL: Track these SEPARATELY!                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why Track Failed Request Latency Separately?

```
Scenario: Database is down

Request Timeline:
──────────────────────────────────────────────────────────────►
│                                                              │
│  Normal Request:    ██████████████████████████  (500ms)     │
│                                                              │
│  Failed Request:    ██  (50ms - immediate timeout error)    │
│                                                              │

If you average these together, you might see "improved latency"
when your service is actually failing!
```

#### Measuring Latency

```python
# Good: Measure at multiple percentiles
latency_metrics = {
    "p50": histogram.percentile(50),   # Median - typical experience
    "p90": histogram.percentile(90),   # Most users
    "p95": histogram.percentile(95),   # Catch degradation
    "p99": histogram.percentile(99),   # Tail latency
    "p999": histogram.percentile(99.9) # Worst cases
}

# Track success and failure separately
latency_by_status = {
    "success": filter(requests, status < 400),
    "client_error": filter(requests, status >= 400 AND status < 500),
    "server_error": filter(requests, status >= 500)
}
```

#### Latency Targets Example

| Service Type | P50 | P95 | P99 |
|--------------|-----|-----|-----|
| API Gateway | 50ms | 100ms | 200ms |
| Web Application | 100ms | 300ms | 1000ms |
| Search Service | 200ms | 500ms | 2000ms |
| Batch Processing | N/A | N/A | < SLO |

---

### 2. Traffic

**Definition**: A measure of how much demand is being placed on your system.

#### Traffic Metrics by Service Type

| Service Type | Traffic Metric | Unit |
|--------------|----------------|------|
| Web Service | HTTP requests | req/sec |
| Database | Queries or transactions | queries/sec |
| Streaming | Messages processed | msg/sec |
| Storage | I/O operations | IOPS |
| CDN | Bandwidth | MB/sec |
| Auth Service | Login attempts | logins/min |

#### Traffic Visualization

```
                    Traffic Pattern Analysis
════════════════════════════════════════════════════════════════

Daily Traffic Pattern (req/sec):
                                    Peak Hours
                                   ┌───────────┐
    10K ─                         ╱│           │╲
         │                       ╱ │           │ ╲
     8K ─│                      ╱  │           │  ╲
         │                     ╱   │           │   ╲
     6K ─│                    ╱    │           │    ╲
         │        ╱╲         ╱     │           │     ╲
     4K ─│       ╱  ╲       ╱      │           │      ╲
         │      ╱    ╲     ╱       │           │       ╲
     2K ─│─────╱──────╲───╱────────│───────────│────────╲─────
         │                                                     
         └────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬──
            00:00 03:00 06:00 09:00 12:00 15:00 18:00 21:00 24:00
                              Time of Day

Key Insights:
• Baseline: 2K req/sec (overnight)
• Peak: 10K req/sec (12:00-18:00)
• Ramp-up: 06:00-12:00
• Cool-down: 18:00-22:00
```

#### Traffic Analysis Questions

- **Trend Analysis**: Is traffic growing or declining?
- **Seasonality**: Are there predictable patterns (hourly, daily, weekly)?
- **Correlation**: Does traffic correlate with other events?
- **Capacity Planning**: When will we need more resources?

---

### 3. Errors

**Definition**: The rate of requests that fail, either explicitly or implicitly.

#### Types of Errors

```
┌─────────────────────────────────────────────────────────────┐
│                       ERROR TYPES                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  EXPLICIT ERRORS                                             │
│  ════════════════                                            │
│  • HTTP 5xx responses                                        │
│  • Thrown exceptions                                         │
│  • Failed transactions                                       │
│  • Timeout errors                                            │
│                                                              │
│  IMPLICIT ERRORS                                             │
│  ════════════════                                            │
│  • Wrong answer returned (but HTTP 200)                      │
│  • Slow responses that meet SLA but frustrate users          │
│  • Partial failures (degraded functionality)                 │
│  • Stale data served                                         │
│                                                              │
│  ⚠️  Implicit errors are often harder to detect but          │
│      equally important!                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Error Rate Calculation

```python
# Basic error rate
error_rate = (error_count / total_requests) * 100

# By category
error_breakdown = {
    "5xx_errors": count(status >= 500) / total,
    "4xx_errors": count(status >= 400 AND status < 500) / total,
    "timeout_errors": count(timeout == true) / total,
    "business_errors": count(business_logic_failed) / total
}

# Weighted error rate (some errors are more severe)
weighted_error_rate = (
    (critical_errors * 3) + 
    (major_errors * 2) + 
    (minor_errors * 1)
) / total_requests
```

#### Error Classification

| Category | HTTP Status | Severity | Example |
|----------|-------------|----------|---------|
| Success | 2xx | None | 200 OK |
| Client Error | 4xx | Low | 400 Bad Request |
| Server Error | 5xx | High | 500 Internal Server Error |
| Timeout | N/A | High | Request timeout |
| Business Error | 2xx with error body | Medium | Invalid operation |

---

### 4. Saturation

**Definition**: How "full" your service is—a measure of the system's utilization relative to capacity.

#### Saturation Indicators

```
┌─────────────────────────────────────────────────────────────┐
│                   SATURATION DIMENSIONS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESOURCE SATURATION                                         │
│  ══════════════════                                          │
│  • CPU utilization                                           │
│  • Memory usage                                              │
│  • Disk I/O                                                  │
│  • Network bandwidth                                         │
│                                                              │
│  CAPACITY SATURATION                                         │
│  ════════════════════                                        │
│  • Connection pool usage                                     │
│  • Thread pool exhaustion                                    │
│  • Queue depth                                               │
│  • Open file descriptors                                     │
│                                                              │
│  SERVICE SATURATION                                          │
│  ═══════════════════                                         │
│  • Requests in flight                                        │
│  • Backend connection limits                                 │
│  • Rate limit headroom                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why Saturation Matters

Saturation is a **leading indicator**—it predicts problems before they impact users:

```
                    Saturation vs. Impact Timeline
════════════════════════════════════════════════════════════════

    100% ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
          │                                    ╭───────────
          │                               ╭───╯   IMPACT
          │                          ╭───╯    (user-visible)
     75% ─│─────────────────────────╯─────────────────────────
          │              ╭─────────╮
          │         ╭───╯          ╰───╮
          │    ╭───╯    SATURATION      ╰───╮
     50% ─│───╯     (internal metric)       ╰─────────────────
          │
          │   ⚠️ Alert here!        ❌ Users complaining here
          │        (proactive)              (reactive)
     25% ─│────────────────────────────────────────────────────
          │
          └─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬──►
              00:00 01:00 02:00 03:00 04:00 05:00 06:00  Time

Key: Alert on saturation at 75-80% to prevent user impact
```

#### Saturation Thresholds

| Resource | Warning | Critical | Notes |
|----------|---------|----------|-------|
| CPU | 70% | 85% | Sustained over 5 min |
| Memory | 80% | 90% | Including swap |
| Disk | 80% | 90% | Growth rate matters |
| Connections | 70% | 85% | Of pool maximum |
| Queue Depth | 50% | 80% | Indicates backpressure |

---

## Implementation Guidelines

### Instrumentation Checklist

```
For each service, instrument:

□ LATENCY
  □ Request duration histogram (P50, P95, P99)
  □ Separate success vs. failure latencies
  □ By endpoint/operation
  □ By dependency (database, cache, external API)

□ TRAFFIC
  □ Request rate (req/sec)
  □ By endpoint/operation
  □ By response status
  □ By client/source

□ ERRORS
  □ Error count by type (5xx, 4xx, timeout, business)
  □ Error rate (errors/total)
  □ By endpoint/operation
  □ Error messages/stack traces (sampled)

□ SATURATION
  □ CPU utilization
  □ Memory usage
  □ Connection pool utilization
  □ Thread pool utilization
  □ Queue depths
  □ In-flight requests
```

### OpenTelemetry Example

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

meter = metrics.get_meter(__name__)

# LATENCY - Histogram
request_latency = meter.create_histogram(
    name="http.server.duration",
    description="Duration of HTTP requests",
    unit="ms"
)

# TRAFFIC - Counter
request_count = meter.create_counter(
    name="http.server.request.count",
    description="Number of HTTP requests",
    unit="requests"
)

# ERRORS - Counter
error_count = meter.create_counter(
    name="http.server.error.count",
    description="Number of HTTP errors",
    unit="errors"
)

# SATURATION - Gauge
active_connections = meter.create_observable_gauge(
    name="http.server.active_connections",
    description="Number of active connections",
    unit="connections",
    callbacks=[lambda: get_active_connections()]
)

# Usage in request handler
def handle_request(request):
    start_time = time.time()
    try:
        response = process_request(request)
        request_count.add(1, {"method": request.method, "status": "success"})
        return response
    except Exception as e:
        error_count.add(1, {"method": request.method, "error_type": type(e).__name__})
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        request_latency.record(duration, {"method": request.method})
```

---

## Alerting on Golden Signals

### Alert Priority Matrix

| Signal | Condition | Priority | Response |
|--------|-----------|----------|----------|
| Latency | P99 > 2x baseline | Warning | Investigate |
| Latency | P99 > 5x baseline | Critical | Page on-call |
| Traffic | Drop > 50% | Critical | Immediate investigation |
| Traffic | Spike > 3x normal | Warning | Check for attack/anomaly |
| Errors | Rate > 1% | Warning | Investigate |
| Errors | Rate > 5% | Critical | Page on-call |
| Saturation | > 80% sustained | Warning | Scale or optimize |
| Saturation | > 95% | Critical | Immediate action |

### Alert Examples (Prometheus)

```yaml
groups:
  - name: golden_signals
    rules:
      # LATENCY
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High P99 latency for {{ $labels.service }}"

      # TRAFFIC
      - alert: TrafficDrop
        expr: |
          rate(http_requests_total[5m]) < 
          (rate(http_requests_total[1h] offset 1d) * 0.5)
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Traffic dropped >50% compared to yesterday"

      # ERRORS
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          /
          sum(rate(http_requests_total[5m])) by (service)
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate >5% for {{ $labels.service }}"

      # SATURATION
      - alert: HighCPUSaturation
        expr: |
          avg(rate(container_cpu_usage_seconds_total[5m])) by (pod) 
          / 
          avg(kube_pod_container_resource_limits{resource="cpu"}) by (pod)
          > 0.85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU saturation >85% for {{ $labels.pod }}"
```

---

## Dashboard Design

### Golden Signals Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SERVICE: Payment API                                    [Last 1h ▼]        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐          │
│  │ 📊 TRAFFIC                  │  │ ⏱️ LATENCY                   │          │
│  │                             │  │                              │          │
│  │   Current: 5,234 req/sec    │  │   P50: 45ms    P95: 120ms   │          │
│  │   [▁▂▃▅▆▇█▇▆▅▃▂▁] trend    │  │   P99: 350ms   Max: 1.2s    │          │
│  │                             │  │   [───────────────] trend    │          │
│  └─────────────────────────────┘  └─────────────────────────────┘          │
│                                                                              │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐          │
│  │ ❌ ERRORS                   │  │ 📈 SATURATION                │          │
│  │                             │  │                              │          │
│  │   Error Rate: 0.12%  ✅     │  │   CPU:    ████████░░  78%   │          │
│  │   5xx: 42    4xx: 156       │  │   Memory: ██████░░░░  62%   │          │
│  │   [▁▁▁▁▂▁▁▁▁▁▁▁▁] trend    │  │   Conns:  █████░░░░░  51%   │          │
│  └─────────────────────────────┘  └─────────────────────────────┘          │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ LATENCY DISTRIBUTION (1 hour)                                          │ │
│  │                                                                         │ │
│  │  1s ─┤                                              ╭────────────      │ │
│  │      │                                         ╭───╯                   │ │
│  │500ms─┤                                    ╭───╯       P99              │ │
│  │      │                               ╭───╯                             │ │
│  │200ms─┤                          ╭───╯─────────────────  P95            │ │
│  │      │                     ╭───╯                                       │ │
│  │ 50ms─┤────────────────────╯──────────────────────────  P50            │ │
│  │      │                                                                  │ │
│  │      └───┬───────┬───────┬───────┬───────┬───────┬───────┬─────       │ │
│  │        00:00   00:10   00:20   00:30   00:40   00:50   01:00           │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Golden Signals by Service Type

### API/Web Service

| Signal | Primary Metric | Secondary Metrics |
|--------|----------------|-------------------|
| Latency | Request duration | P50, P95, P99 by endpoint |
| Traffic | HTTP requests/sec | By method, endpoint, status |
| Errors | 5xx error rate | 4xx rate, timeout rate |
| Saturation | CPU, memory, connections | Thread pools, queue depth |

### Database

| Signal | Primary Metric | Secondary Metrics |
|--------|----------------|-------------------|
| Latency | Query duration | By query type, table |
| Traffic | Queries/sec | Reads vs. writes, connections |
| Errors | Failed queries | Deadlocks, timeouts |
| Saturation | Connection pool, IOPS | Buffer pool, disk usage |

### Message Queue

| Signal | Primary Metric | Secondary Metrics |
|--------|----------------|-------------------|
| Latency | Message processing time | End-to-end latency |
| Traffic | Messages/sec | By topic, partition |
| Errors | Failed messages | DLQ rate, poison messages |
| Saturation | Queue depth | Consumer lag, partition count |

### Cache (Redis/Memcached)

| Signal | Primary Metric | Secondary Metrics |
|--------|----------------|-------------------|
| Latency | Get/Set latency | By operation type |
| Traffic | Operations/sec | Hit rate, miss rate |
| Errors | Command failures | Connection errors |
| Saturation | Memory usage | Eviction rate, connections |

---

## Relationship to Other Methodologies

```
┌─────────────────────────────────────────────────────────────────────────┐
│              METHODOLOGY COMPARISON AND OVERLAP                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  GOLDEN SIGNALS          RED METHOD           USE METHOD                │
│  ══════════════          ══════════           ══════════                │
│  (User-centric)          (Services)           (Resources)               │
│                                                                          │
│  ┌─────────────┐         ┌─────────┐          ┌─────────────┐          │
│  │  Latency    │◄───────►│Duration │          │             │          │
│  └─────────────┘         └─────────┘          │             │          │
│                                               │             │          │
│  ┌─────────────┐         ┌─────────┐          │             │          │
│  │  Traffic    │◄───────►│  Rate   │          │             │          │
│  └─────────────┘         └─────────┘          │             │          │
│                                               │             │          │
│  ┌─────────────┐         ┌─────────┐          ┌─────────────┐          │
│  │  Errors     │◄───────►│ Errors  │◄────────►│   Errors    │          │
│  └─────────────┘         └─────────┘          └─────────────┘          │
│                                                                          │
│  ┌─────────────┐                              ┌─────────────┐          │
│  │ Saturation  │◄────────────────────────────►│ Saturation  │          │
│  └─────────────┘                              │ Utilization │          │
│                                               └─────────────┘          │
│                                                                          │
│  Best for:               Best for:            Best for:                 │
│  Overall service         Request-driven       Infrastructure            │
│  health monitoring       microservices        & resources               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Common Pitfalls

### 1. Averaging Latency

```
❌ Bad: Average latency = 150ms
   (Hides tail latency issues)

✅ Good: P50=50ms, P95=200ms, P99=800ms
   (Shows distribution and outliers)
```

### 2. Ignoring Failed Request Latency

```
❌ Bad: Overall latency looks great!
   (But it's because errors are fast)

✅ Good: Separate success/failure latency
   Success P99: 500ms | Failure P99: 50ms
```

### 3. Alert on Absolute Values Only

```
❌ Bad: Alert when latency > 500ms
   (Doesn't account for normal variation)

✅ Good: Alert when latency > 2x historical baseline
   (Adapts to service characteristics)
```

### 4. Missing Saturation

```
❌ Bad: Only monitor latency, traffic, errors
   (Reactive - problems visible only when users impacted)

✅ Good: Include saturation metrics
   (Proactive - predict problems before impact)
```

---

## Tools and Implementation

### Metrics Collection

| Tool | Latency | Traffic | Errors | Saturation |
|------|---------|---------|--------|------------|
| Prometheus | ✅ Histogram | ✅ Counter | ✅ Counter | ✅ Gauge |
| DataDog | ✅ Distribution | ✅ Count | ✅ Count | ✅ Gauge |
| New Relic | ✅ Native | ✅ Native | ✅ Native | ✅ Native |
| CloudWatch | ✅ EMF | ✅ Metric | ✅ Metric | ✅ Metric |
| Azure Monitor | ✅ Custom | ✅ Custom | ✅ Custom | ✅ Custom |

### Quick Start: Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# Define golden signal metrics
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint', 'status'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'error_type']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)
```

---

## Summary

| Signal | Question | Key Insight |
|--------|----------|-------------|
| **Latency** | How long does it take? | User experience speed |
| **Traffic** | How much load? | Demand and capacity |
| **Errors** | How often does it fail? | Reliability |
| **Saturation** | How full is it? | Headroom and risk |

### Key Takeaways

1. **Four metrics cover the essentials** for user-facing services
2. **Track latency by percentiles**, not averages
3. **Separate successful and failed** request latencies
4. **Saturation is a leading indicator**—alert early
5. **Combine with RED/USE** for comprehensive monitoring

---

## Related Documentation

- [RED Method](04-red-method.md) - Simplified for microservices
- [USE Method](05-use-method.md) - Resource-focused monitoring
- [SLI/SLO/SLA](01-sli-slo-sla.md) - Setting reliability targets
