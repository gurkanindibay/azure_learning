---
type: Architecture Pattern
title: "The RED Method"
description: "The **RED Method** is a monitoring methodology specifically designed for **request-driven services** (microservices, APIs, web applications). It was created by Tom Wilkie at Weave Works and focuses..."
tags: [reliability-performance-operations]
timestamp: 2026-06-14T00:00:00Z
---

# The RED Method

## Table of Contents

- [Overview](#overview)
- [What is the RED Method?](#what-is-the-red-method)
- [The Three Metrics](#the-three-metrics)
  - [Rate](#rate)
  - [Errors](#errors)
  - [Duration](#duration)
- [When to Use RED](#when-to-use-red)
- [Implementation Guide](#implementation-guide)
- [Dashboard Design](#dashboard-design)
- [Alerting Strategies](#alerting-strategies)
- [RED by Service Type](#red-by-service-type)
- [RED vs. Golden Signals](#red-vs-golden-signals)
- [Common Pitfalls](#common-pitfalls)
- [Tools and Examples](#tools-and-examples)

---

## Overview

The **RED Method** is a monitoring methodology specifically designed for **request-driven services** (microservices, APIs, web applications). It was created by Tom Wilkie at Weave Works and focuses on three key metrics that directly reflect user experience.

```
┌─────────────────────────────────────────────────────────────────┐
│                      THE RED METHOD                              │
│                                                                  │
│              For every service, monitor:                         │
│                                                                  │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│    │     RATE     │  │    ERRORS    │  │   DURATION   │        │
│    │              │  │              │  │              │        │
│    │  Requests    │  │   Failed     │  │   Response   │        │
│    │  per second  │  │   requests   │  │     time     │        │
│    │              │  │              │  │              │        │
│    └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
│    "How busy?"       "How broken?"      "How slow?"             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## What is the RED Method?

### Origin

Created by **Tom Wilkie** (Weaveworks/Grafana Labs) as a simplified monitoring approach for microservices architectures. It distills monitoring to the three most essential metrics for request-driven services.

### Philosophy

> "For every service, monitor request **Rate**, request **Errors**, and request **Duration**"

The RED Method prioritizes **simplicity** and **consistency**—by using the same three metrics across all services, teams can quickly understand any service's health.

### Key Principles

1. **Simplicity**: Three metrics cover essential service health
2. **Consistency**: Same metrics across all services
3. **User-centric**: Metrics reflect what users experience
4. **Actionable**: Deviations directly indicate problems

---

## The Three Metrics

### Rate

**Definition**: The number of requests your service is handling per second.

```
┌─────────────────────────────────────────────────────────────────┐
│                          RATE                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  What it measures:    Request throughput                         │
│  Unit:                Requests per second (req/s)                │
│  Dimension by:        Endpoint, method, status, client           │
│                                                                  │
│  Why it matters:                                                 │
│  ═════════════════                                               │
│  • Indicates service demand/load                                 │
│  • Helps with capacity planning                                  │
│  • Detects traffic anomalies (spikes, drops)                    │
│  • Correlates with business metrics                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Rate Metrics to Track

| Metric | Description | Use Case |
|--------|-------------|----------|
| Total request rate | All requests/sec | Overall load |
| Rate by endpoint | Requests/sec per API endpoint | Endpoint-specific load |
| Rate by status | Requests/sec by HTTP status | Success vs. failure distribution |
| Rate by client | Requests/sec by caller | Identify heavy users |

#### Rate Calculation

```python
# Prometheus PromQL
rate(http_requests_total[5m])

# By endpoint
sum(rate(http_requests_total[5m])) by (endpoint)

# Success vs. failure
sum(rate(http_requests_total{status=~"2.."}[5m]))  # Success
sum(rate(http_requests_total{status=~"5.."}[5m]))  # Errors
```

#### Rate Patterns to Watch

```
Normal Pattern:
────────────────────────────────────
     │  ╭──────────────╮
Rate │ ╱              ╲   Daily peak
     │╱                ╲
     └────────────────────────────► Time
       6am            6pm

Anomaly: Sudden Drop (potential outage)
────────────────────────────────────
     │  ╭─────╮
Rate │ ╱      │
     │╱       ╰─────────  ⚠️ Alert!
     └────────────────────────────► Time

Anomaly: Sudden Spike (attack or viral content)
────────────────────────────────────
     │              ╭─────
Rate │              │      ⚠️ Alert!
     │──────────────╯
     └────────────────────────────► Time
```

---

### Errors

**Definition**: The number of requests that are failing per second.

```
┌─────────────────────────────────────────────────────────────────┐
│                         ERRORS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  What it measures:    Failed request count/rate                  │
│  Units:               Errors/sec or Error rate (%)               │
│  Dimension by:        Error type, endpoint, error code           │
│                                                                  │
│  Error Categories:                                               │
│  ═════════════════                                               │
│  • HTTP 5xx         - Server errors (your fault)                 │
│  • HTTP 4xx         - Client errors (usually their fault)        │
│  • Timeouts         - Request exceeded time limit                │
│  • Business errors  - Application-level failures                 │
│  • Partial failures - Degraded responses                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Error Metrics to Track

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Error count | `sum(errors)` | Absolute failure volume |
| Error rate | `errors / total * 100` | Percentage of failures |
| Error by type | `sum(errors) by (type)` | Root cause distribution |
| Error by endpoint | `sum(errors) by (endpoint)` | Problem hotspots |

#### Error Rate Calculation

```python
# Prometheus PromQL - Error Rate
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) 
* 100

# By endpoint
sum(rate(http_requests_total{status=~"5.."}[5m])) by (endpoint)
/
sum(rate(http_requests_total[5m])) by (endpoint)
* 100
```

#### Error Classification Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR CLASSIFICATION                          │
├──────────────┬────────────┬──────────────┬─────────────────────┤
│ Status Code  │ Category   │ Severity     │ Typical Cause       │
├──────────────┼────────────┼──────────────┼─────────────────────┤
│ 400          │ Client     │ Low          │ Bad request format  │
│ 401          │ Client     │ Low          │ Not authenticated   │
│ 403          │ Client     │ Low          │ Not authorized      │
│ 404          │ Client     │ Low          │ Resource not found  │
│ 429          │ Client     │ Medium       │ Rate limited        │
├──────────────┼────────────┼──────────────┼─────────────────────┤
│ 500          │ Server     │ High         │ Internal error      │
│ 502          │ Server     │ High         │ Bad gateway         │
│ 503          │ Server     │ Critical     │ Service unavailable │
│ 504          │ Server     │ High         │ Gateway timeout     │
└──────────────┴────────────┴──────────────┴─────────────────────┘

Note: Focus on 5xx errors - these indicate problems within your control
```

---

### Duration

**Definition**: The distribution of time it takes to handle requests (latency).

```
┌─────────────────────────────────────────────────────────────────┐
│                        DURATION                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  What it measures:    Request response time                      │
│  Unit:                Milliseconds (ms) or seconds (s)           │
│  Track as:            HISTOGRAM (not average!)                   │
│  Key percentiles:     P50, P90, P95, P99, P99.9                 │
│                                                                  │
│  Why histogram over average:                                     │
│  ═══════════════════════════                                     │
│  • Averages hide outliers                                        │
│  • Percentiles show distribution                                 │
│  • P99 reveals worst-case experience                            │
│  • Better for SLO definition                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Duration Percentiles Explained

```
                    Duration Distribution
════════════════════════════════════════════════════════════════

Request
Count   │
        │ ████
        │ █████
        │ ██████
        │ ███████
        │ ████████
        │ █████████
        │ ██████████  ▲           ▲            ▲           ▲
        │ ███████████ │           │            │           │
        │ ████████████│           │            │           │
        └─────────────┼───────────┼────────────┼───────────┼──► Time
                      │           │            │           │
                     P50        P90          P95         P99
                    50ms      150ms        250ms       800ms

        │◄────────────┤
        50% of users  │
        are here      │◄──────────┤
                      90% of users│
                      are here    │◄───────────┤
                                  95% of users │
                                  are here     │◄──────────┤
                                               99% here    │
                                                          1% worst
                                                          experience
```

#### Duration Metrics to Track

| Percentile | Description | Typical SLO |
|------------|-------------|-------------|
| P50 | Median - typical experience | < 100ms |
| P90 | Most users | < 200ms |
| P95 | Nearly all users | < 500ms |
| P99 | Tail latency | < 1000ms |
| P99.9 | Extreme outliers | < 2000ms |

#### Duration Calculation

```python
# Prometheus PromQL - Percentiles from histogram
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))  # P50
histogram_quantile(0.90, rate(http_request_duration_seconds_bucket[5m]))  # P90
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))  # P95
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # P99

# By endpoint
histogram_quantile(0.99, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
```

---

## When to Use RED

### Ideal Use Cases

| Service Type | RED Applicability | Notes |
|--------------|-------------------|-------|
| REST APIs | ✅ Excellent | Primary use case |
| GraphQL APIs | ✅ Excellent | Track by operation |
| gRPC services | ✅ Excellent | Native support |
| Web applications | ✅ Excellent | Include page loads |
| Microservices | ✅ Excellent | Per-service metrics |
| Serverless functions | ✅ Good | Track invocations |

### Less Suitable For

| System Type | Better Alternative | Reason |
|-------------|-------------------|--------|
| Databases | USE Method | Resource-focused |
| Caches | USE Method | Utilization matters more |
| Message queues | Modified RED | Add queue depth |
| Infrastructure | USE Method | CPU, memory, disk focus |

---

## Implementation Guide

### Step 1: Instrument Your Service

```python
# Python with OpenTelemetry
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider

meter = metrics.get_meter("my-service")

# RATE - Counter for request count
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total HTTP requests",
    unit="requests"
)

# ERRORS - Counter for error count
error_counter = meter.create_counter(
    name="http_errors_total",
    description="Total HTTP errors",
    unit="errors"
)

# DURATION - Histogram for latency
request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration",
    unit="s"
)

# Usage
def handle_request(request):
    start = time.time()
    status = "success"
    
    try:
        response = process(request)
    except Exception as e:
        status = "error"
        error_counter.add(1, {"endpoint": request.path, "error": type(e).__name__})
        raise
    finally:
        duration = time.time() - start
        request_counter.add(1, {"endpoint": request.path, "status": status})
        request_duration.record(duration, {"endpoint": request.path})
    
    return response
```

### Step 2: Define Labels/Dimensions

```yaml
# Recommended labels for RED metrics
labels:
  # Common labels
  - service: "payment-api"
  - version: "v2.1.0"
  - environment: "production"
  
  # Request-specific labels
  - endpoint: "/api/v1/payments"
  - method: "POST"
  - status_code: "200"
  
  # Error-specific labels (for error counter)
  - error_type: "timeout"
  - error_code: "PAYMENT_FAILED"
```

### Step 3: Configure Histogram Buckets

```python
# Choose buckets appropriate for your service
duration_buckets = [
    0.005,  # 5ms
    0.01,   # 10ms
    0.025,  # 25ms
    0.05,   # 50ms
    0.1,    # 100ms
    0.25,   # 250ms
    0.5,    # 500ms
    1.0,    # 1s
    2.5,    # 2.5s
    5.0,    # 5s
    10.0,   # 10s
]

# For fast services (cache, simple APIs)
fast_buckets = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]

# For slow services (data processing, reports)
slow_buckets = [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
```

---

## Dashboard Design

### RED Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SERVICE: Order API    ENV: Production    VERSION: 2.1.0    [Last 6h ▼]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │   📊 RATE          │  │   ❌ ERRORS        │  │   ⏱️ DURATION      │    │
│  │                    │  │                    │  │                    │    │
│  │   1,234 req/s      │  │   0.12% error     │  │   P50: 45ms       │    │
│  │   ▲ +5% vs 1h ago  │  │   rate            │  │   P99: 320ms      │    │
│  │                    │  │   ✅ Healthy      │  │   ✅ Healthy      │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                     RATE OVER TIME                                     │ │
│  │  2K ─┤                        ╭────────────────────                    │ │
│  │      │                   ╭───╯                                         │ │
│  │  1K ─┤──────────────────╯─────────────────────────────────────        │ │
│  │      │                                                                  │ │
│  │   0 ─┴────────┬────────┬────────┬────────┬────────┬────────┬─────    │ │
│  │             -6h      -5h      -4h      -3h      -2h      -1h   Now     │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │       ERROR RATE OVER TIME      │  │      DURATION PERCENTILES       │ │
│  │  5% ─┤                          │  │  1s ─┤                  ╭────   │ │
│  │      │                          │  │      │             ╭───╯ P99    │ │
│  │  2% ─┤                          │  │500ms─┤         ╭──╯             │ │
│  │      │     ╭╮                   │  │      │    ╭───╯     P95         │ │
│  │  0% ─┤─────╯╰───────────────    │  │100ms─┤───╯──────────── P50      │ │
│  │      └────────────────────────  │  │      └──────────────────────    │ │
│  └─────────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    BY ENDPOINT                                         │ │
│  │  Endpoint          Rate       Errors    P50      P99                  │ │
│  │  ─────────────────────────────────────────────────────────            │ │
│  │  /api/orders       800/s      0.1%      35ms     250ms    ✅          │ │
│  │  /api/payments     300/s      0.3%      80ms     450ms    ✅          │ │
│  │  /api/inventory    134/s      1.2%      45ms     890ms    ⚠️          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Alerting Strategies

### Alert Rules

```yaml
groups:
  - name: red_alerts
    rules:
      # RATE: Traffic anomaly detection
      - alert: TrafficSpike
        expr: |
          rate(http_requests_total[5m]) > 
          2 * avg_over_time(rate(http_requests_total[5m])[1h:5m])
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Traffic spike detected - 2x normal"
          
      - alert: TrafficDrop
        expr: |
          rate(http_requests_total[5m]) < 
          0.5 * avg_over_time(rate(http_requests_total[5m])[1h:5m])
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Traffic dropped below 50% of normal"

      # ERRORS: Error rate thresholds
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          / sum(rate(http_requests_total[5m])) by (service)
          > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error rate >1% for {{ $labels.service }}"
          
      - alert: CriticalErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          / sum(rate(http_requests_total[5m])) by (service)
          > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate >5% for {{ $labels.service }}"

      # DURATION: Latency thresholds
      - alert: HighP99Latency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency >1s for {{ $labels.service }}"
          
      - alert: LatencyDegradation
        expr: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 
          3 * histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket[1h])) by (le, service)
          )
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "P99 latency 3x higher than 1h average"
```

### Alert Priority Matrix

| Metric | Condition | Severity | Action |
|--------|-----------|----------|--------|
| Rate | Drop >50% | Critical | Immediate investigation |
| Rate | Spike >200% | Warning | Check for attack/anomaly |
| Errors | Rate >1% | Warning | Investigate within 1h |
| Errors | Rate >5% | Critical | Page on-call |
| Duration | P99 >1s | Warning | Investigate |
| Duration | P99 >3x baseline | Critical | Page on-call |

---

## RED by Service Type

### REST API

```yaml
metrics:
  rate:
    - http_requests_total{method, endpoint, status}
  errors:
    - http_requests_total{status=~"5.."}
    - http_requests_total{status=~"4.."}  # separate tracking
  duration:
    - http_request_duration_seconds{method, endpoint}
```

### GraphQL API

```yaml
metrics:
  rate:
    - graphql_operations_total{operation_name, operation_type}
  errors:
    - graphql_errors_total{operation_name, error_type}
  duration:
    - graphql_operation_duration_seconds{operation_name}
```

### gRPC Service

```yaml
metrics:
  rate:
    - grpc_server_handled_total{service, method, code}
  errors:
    - grpc_server_handled_total{code!="OK"}
  duration:
    - grpc_server_handling_seconds{service, method}
```

### Serverless Function

```yaml
metrics:
  rate:
    - function_invocations_total{function_name, trigger_type}
  errors:
    - function_errors_total{function_name, error_type}
  duration:
    - function_duration_seconds{function_name}
```

---

## RED vs. Golden Signals

```
┌─────────────────────────────────────────────────────────────────┐
│              RED METHOD vs. GOLDEN SIGNALS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RED METHOD                    GOLDEN SIGNALS                    │
│  ══════════                    ══════════════                    │
│                                                                  │
│  ┌──────────┐                  ┌──────────────┐                 │
│  │   Rate   │◄────────────────►│   Traffic    │                 │
│  └──────────┘                  └──────────────┘                 │
│       Same concept, different name                               │
│                                                                  │
│  ┌──────────┐                  ┌──────────────┐                 │
│  │  Errors  │◄────────────────►│    Errors    │                 │
│  └──────────┘                  └──────────────┘                 │
│       Identical                                                  │
│                                                                  │
│  ┌──────────┐                  ┌──────────────┐                 │
│  │ Duration │◄────────────────►│   Latency    │                 │
│  └──────────┘                  └──────────────┘                 │
│       Same concept, different name                               │
│                                                                  │
│                                ┌──────────────┐                 │
│       NOT IN RED ─────────────►│  Saturation  │                 │
│                                └──────────────┘                 │
│       RED doesn't include saturation                             │
│       (resource-level metric)                                    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  When to use which:                                              │
│  • RED: Simple, request-focused services                         │
│  • Golden Signals: When you also need resource visibility        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Pitfalls

### 1. Using Averages for Duration

```
❌ Bad: Average response time = 150ms
   Problem: Hides bimodal distributions and tail latency

✅ Good: P50=45ms, P95=200ms, P99=800ms
   Benefit: Shows true distribution
```

### 2. Not Separating Error Types

```
❌ Bad: Total error count = 500
   Problem: Mixes client errors (400s) with server errors (500s)

✅ Good: 
   - 5xx errors: 50 (server problems - you need to fix)
   - 4xx errors: 450 (client issues - monitor, don't alert)
```

### 3. Too Many Label Dimensions

```
❌ Bad: Labels = {user_id, request_id, timestamp, ...}
   Problem: Cardinality explosion, expensive storage

✅ Good: Labels = {endpoint, method, status_code}
   Benefit: Manageable cardinality, useful aggregations
```

### 4. Ignoring Error Rate During Low Traffic

```
❌ Bad: Alert when errors > 100/s
   Problem: Misses issues during low-traffic periods

✅ Good: Alert when error_rate > 1%
   Benefit: Works at any traffic level
```

---

## Tools and Examples

### Prometheus Metrics Definition

```python
from prometheus_client import Counter, Histogram

# RED Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

# Note: Errors are derived from REQUEST_COUNT where status=~"5.."
```

### Grafana Dashboard JSON (Key Panels)

```json
{
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "targets": [{
        "expr": "sum(rate(http_requests_total[5m]))",
        "legendFormat": "Total req/s"
      }]
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "targets": [{
        "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
        "legendFormat": "Error %"
      }]
    },
    {
      "title": "Duration Percentiles",
      "type": "timeseries",
      "targets": [
        {"expr": "histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))", "legendFormat": "P50"},
        {"expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))", "legendFormat": "P95"},
        {"expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))", "legendFormat": "P99"}
      ]
    }
  ]
}
```

---

## Summary

| Metric | What It Measures | Key Questions |
|--------|------------------|---------------|
| **Rate** | Request throughput | How busy is the service? |
| **Errors** | Failure count/rate | How often are requests failing? |
| **Duration** | Response time distribution | How long are requests taking? |

### Key Takeaways

1. **Simple and consistent** - Same three metrics for every service
2. **User-focused** - Metrics directly reflect user experience
3. **Use histograms** for duration, not averages
4. **Separate error types** - 5xx vs. 4xx have different meanings
5. **Combine with USE** for complete visibility (resources + requests)

---

## Related Documentation

- [Golden Signals](03-golden-signals.md) - More comprehensive methodology
- [USE Method](05-use-method.md) - Resource-focused monitoring
- [SLI/SLO/SLA](01-sli-slo-sla.md) - Setting reliability targets based on RED metrics
