# Percentiles in Software Architecture

## Table of Contents

- [Overview](#overview)
- [What Are Percentiles?](#what-are-percentiles)
- [Why Percentiles Matter More Than Averages](#why-percentiles-matter-more-than-averages)
- [Common Percentiles in Software Systems](#common-percentiles-in-software-systems)
- [Calculating Percentiles](#calculating-percentiles)
- [Usage Areas and Examples](#usage-areas-and-examples)
  - [API Response Time](#api-response-time)
  - [Database Query Performance](#database-query-performance)
  - [Message Queue Latency](#message-queue-latency)
  - [Load Balancer Health Checks](#load-balancer-health-checks)
  - [CDN Performance](#cdn-performance)
  - [Microservices Communication](#microservices-communication)
  - [User Experience Metrics](#user-experience-metrics)
  - [Batch Processing](#batch-processing)
- [SLA and SLO Definitions](#sla-and-slo-definitions)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Percentile Distribution Visualization](#percentile-distribution-visualization)
- [Common Pitfalls](#common-pitfalls)
- [Best Practices](#best-practices)
- [Tools and Libraries](#tools-and-libraries)
- [References](#references)

## Overview

Percentiles are statistical measures used to understand the distribution of values in a dataset. In software architecture, percentiles are critical for measuring **latency**, **response times**, **throughput**, and other performance metrics. They provide a more accurate picture of system performance than simple averages, especially for understanding the experience of users at the tail end of the distribution.

## What Are Percentiles?

A **percentile** indicates the value below which a given percentage of observations fall.

| Percentile | Meaning |
|------------|---------|
| **P50** (Median) | 50% of values are below this point |
| **P75** | 75% of values are below this point |
| **P90** | 90% of values are below this point |
| **P95** | 95% of values are below this point |
| **P99** | 99% of values are below this point |
| **P99.9** | 99.9% of values are below this point |

### Visual Representation

```
Number of
Requests
    │
    │████
    │████████
    │████████████████
    │██████████████████████████
    │██████████████████████████████████████
    └──────────────────────────────────────────► Latency (ms)
              │       │     │    │
             P50     P90   P95  P99
```

Most requests cluster on the left (fast), with a "long tail" extending right (slow outliers).

### Sorted Distribution Example

If you have 100 API requests sorted by response time:

| Position | Response Time | Percentile |
|----------|---------------|------------|
| 1st | 2ms | Fastest |
| 50th | 15ms | **P50 (Median)** |
| 90th | 45ms | **P90** |
| 95th | 80ms | **P95** |
| 99th | 250ms | **P99** |
| 100th | 2000ms | **P100 (Max)** |

## Why Percentiles Matter More Than Averages

### The Problem with Averages

Averages can be **misleading** because they hide the distribution:

**Example: 100 API requests**
- 99 requests: 10ms each
- 1 request: 1000ms (timeout)

**Average**: (99 × 10 + 1 × 1000) / 100 = **19.9ms** ✅ Looks good!

**But the reality:**
- **P99 = 1000ms** ❌ 1% of users wait 1 second!

### Real-World Impact

| Metric | Average | P99 | User Impact |
|--------|---------|-----|-------------|
| API Response | 50ms | 2000ms | 1% of users experience 2s delays |
| Page Load | 1.2s | 8s | 1 in 100 visitors wait 8 seconds |
| Database Query | 5ms | 500ms | Some queries block for 0.5s |

### Amazon's Famous Quote

> "Every 100ms of latency costs Amazon 1% in sales."

For a site with millions of users, even 1% experiencing poor performance = thousands of unhappy customers.

## Common Percentiles in Software Systems

| Percentile | Common Name | Typical Use |
|------------|-------------|-------------|
| **P50** | Median | Typical user experience |
| **P75** | Upper quartile | Good performance threshold |
| **P90** | - | Common SLO target |
| **P95** | - | Stricter SLO target |
| **P99** | "Two nines" | High-reliability SLO |
| **P99.9** | "Three nines" | Mission-critical systems |
| **P99.99** | "Four nines" | Financial/healthcare systems |

## Calculating Percentiles

### Formula

For a sorted dataset of n values, the k-th percentile position is:

$$P_k = \frac{k}{100} \times (n + 1)$$

### Example Calculation

Dataset (sorted): [2, 5, 8, 12, 15, 18, 22, 25, 30, 35]
n = 10

**Calculate P90:**
$$P_{90} = \frac{90}{100} \times (10 + 1) = 9.9$$

Position 9.9 means: interpolate between 9th value (30) and 10th value (35)
$$P_{90} = 30 + 0.9 \times (35 - 30) = 30 + 4.5 = 34.5$$

### Code Examples

**Python:**
```python
import numpy as np

latencies = [10, 15, 20, 25, 30, 35, 40, 100, 150, 500]

p50 = np.percentile(latencies, 50)   # 32.5
p90 = np.percentile(latencies, 90)   # 185.0
p95 = np.percentile(latencies, 95)   # 342.5
p99 = np.percentile(latencies, 99)   # 468.5

print(f"P50: {p50}ms, P90: {p90}ms, P95: {p95}ms, P99: {p99}ms")
```

**C#:**
```csharp
public static double Percentile(double[] sequence, double percentile)
{
    Array.Sort(sequence);
    int n = sequence.Length;
    double index = (percentile / 100.0) * (n - 1);
    int lower = (int)Math.Floor(index);
    int upper = (int)Math.Ceiling(index);
    
    if (lower == upper)
        return sequence[lower];
    
    return sequence[lower] * (upper - index) + sequence[upper] * (index - lower);
}

// Usage
double[] latencies = { 10, 15, 20, 25, 30, 35, 40, 100, 150, 500 };
Console.WriteLine($"P99: {Percentile(latencies, 99)}ms");
```

**JavaScript:**
```javascript
function percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = (p / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;
    
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

const latencies = [10, 15, 20, 25, 30, 35, 40, 100, 150, 500];
console.log(`P99: ${percentile(latencies, 99)}ms`);
```

## Usage Areas and Examples

### API Response Time

**Scenario:** REST API serving mobile and web clients

| Percentile | Target | Meaning |
|------------|--------|---------|
| P50 | < 100ms | Half of requests are snappy |
| P95 | < 500ms | Most users have good experience |
| P99 | < 2000ms | Even unlucky users don't timeout |

**Prometheus Query:**
```promql
# P99 latency over last 5 minutes
histogram_quantile(0.99, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

**Application Insights (KQL):**
```kql
requests
| where timestamp > ago(1h)
| summarize 
    P50 = percentile(duration, 50),
    P95 = percentile(duration, 95),
    P99 = percentile(duration, 99)
| project P50, P95, P99
```

### Database Query Performance

**Scenario:** SQL database serving an e-commerce application

| Query Type | P50 | P95 | P99 | Action if Exceeded |
|------------|-----|-----|-----|-------------------|
| Simple SELECT | 5ms | 20ms | 50ms | Check indexes |
| JOIN queries | 20ms | 100ms | 300ms | Query optimization |
| Reports | 500ms | 2s | 5s | Move to replica |

**SQL Server Example:**
```sql
-- Find slow queries using percentiles
SELECT 
    qs.query_hash,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY qs.total_elapsed_time/qs.execution_count) 
        OVER() AS P50_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY qs.total_elapsed_time/qs.execution_count) 
        OVER() AS P95_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY qs.total_elapsed_time/qs.execution_count) 
        OVER() AS P99_ms
FROM sys.dm_exec_query_stats qs;
```

**PostgreSQL Example:**
```sql
-- Using pg_stat_statements
SELECT 
    query,
    calls,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY total_time/calls) AS p50_ms,
    percentile_cont(0.95) WITHIN GROUP (ORDER BY total_time/calls) AS p95_ms,
    percentile_cont(0.99) WITHIN GROUP (ORDER BY total_time/calls) AS p99_ms
FROM pg_stat_statements
GROUP BY query, calls
ORDER BY p99_ms DESC
LIMIT 10;
```

### Message Queue Latency

**Scenario:** Azure Service Bus processing order events

| Tier | P50 | P95 | P99 | Use Case |
|------|-----|-----|-----|----------|
| Basic | 50ms | 150ms | 300ms | Dev/Test |
| Standard | 30ms | 80ms | 150ms | Production |
| Premium (1 MU) | 5ms | 8ms | 10ms | Low-latency |
| Premium (4 MU) | 3ms | 5ms | 7ms | Financial |

**Monitoring Example:**
```csharp
// Track message processing latency
var stopwatch = Stopwatch.StartNew();
await ProcessMessageAsync(message);
stopwatch.Stop();

// Report to metrics system
_metrics.RecordLatency("message_processing", stopwatch.ElapsedMilliseconds);

// Metrics system calculates percentiles
// P50, P95, P99 reported to dashboard
```

### Load Balancer Health Checks

**Scenario:** Application Gateway routing to backend services

**Health Check SLO:**
```yaml
health_check:
  interval: 30s
  timeout: 10s
  healthy_threshold: 2
  unhealthy_threshold: 3
  
  # Mark unhealthy if P95 > 5s
  latency_threshold:
    p95: 5000ms
```

**Azure Application Gateway Configuration:**
```json
{
  "healthProbe": {
    "name": "backendProbe",
    "properties": {
      "protocol": "Http",
      "path": "/health",
      "interval": 30,
      "timeout": 10,
      "unhealthyThreshold": 3
    }
  }
}
```

### CDN Performance

**Scenario:** Global content delivery for static assets

| Region | P50 | P90 | P99 |
|--------|-----|-----|-----|
| US East | 15ms | 30ms | 80ms |
| Europe | 25ms | 50ms | 120ms |
| Asia Pacific | 40ms | 80ms | 200ms |

**Azure CDN Analytics (KQL):**
```kql
AzureDiagnostics
| where Category == "AzureCdnAccessLog"
| where TimeGenerated > ago(1h)
| summarize 
    P50 = percentile(timeTaken_d, 50),
    P90 = percentile(timeTaken_d, 90),
    P99 = percentile(timeTaken_d, 99)
    by bin(TimeGenerated, 5m), pop_s
| render timechart
```

### Microservices Communication

**Scenario:** Service mesh with multiple hops

**Per-Service SLO:**
```yaml
services:
  - name: api-gateway
    latency:
      p50: 10ms
      p99: 50ms
      
  - name: user-service
    latency:
      p50: 5ms
      p99: 25ms
      
  - name: order-service
    latency:
      p50: 15ms
      p99: 75ms
```

**Cumulative Latency Problem:**

When services call each other, latencies compound:

```
Client → API Gateway → User Service → Order Service → Database
         10ms           5ms            15ms           3ms
         
Best case (P50): 10 + 5 + 15 + 3 = 33ms
Worst case (P99): 50 + 25 + 75 + 20 = 170ms
```

**Istio Service Mesh Query:**
```promql
# P99 latency for service-to-service calls
histogram_quantile(0.99,
  sum(rate(istio_request_duration_milliseconds_bucket{
    reporter="source",
    destination_service="order-service"
  }[5m])) by (le, source_workload)
)
```

### User Experience Metrics

**Scenario:** Web application Core Web Vitals

| Metric | Good (P75) | Needs Improvement | Poor |
|--------|------------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s - 4s | > 4s |
| **FID** (First Input Delay) | ≤ 100ms | 100ms - 300ms | > 300ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |

**Note:** Google uses **P75** for Core Web Vitals because it represents the experience of most users while still being stricter than median.

**JavaScript Performance Monitoring:**
```javascript
// Collect real user metrics
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    // Send to analytics
    analytics.track('web-vital', {
      name: entry.name,
      value: entry.value,
      id: entry.id
    });
  }
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

### Batch Processing

**Scenario:** ETL job processing millions of records

| Batch Size | P50 | P95 | P99 | Max Allowed |
|------------|-----|-----|-----|-------------|
| 1,000 records | 2s | 5s | 10s | 30s |
| 10,000 records | 15s | 30s | 60s | 5min |
| 100,000 records | 2min | 5min | 10min | 30min |

**Spark Job Monitoring:**
```python
from pyspark.sql import functions as F

# Calculate processing time percentiles
df.groupBy("batch_id").agg(
    F.percentile_approx("processing_time_ms", 0.50).alias("p50"),
    F.percentile_approx("processing_time_ms", 0.95).alias("p95"),
    F.percentile_approx("processing_time_ms", 0.99).alias("p99")
).show()
```

## SLA and SLO Definitions

### Terminology

| Term | Definition | Example |
|------|------------|---------|
| **SLI** (Service Level Indicator) | Metric being measured | P99 latency |
| **SLO** (Service Level Objective) | Internal target | P99 < 200ms |
| **SLA** (Service Level Agreement) | External contract | 99.9% requests < 500ms |

### Example SLO Document

```yaml
service: payment-api
version: 1.0

slos:
  - name: request-latency
    description: "API response time"
    indicators:
      - percentile: 50
        threshold: 100ms
      - percentile: 95
        threshold: 300ms
      - percentile: 99
        threshold: 1000ms
    
  - name: availability
    description: "Successful requests"
    target: 99.9%
    window: 30d
    
  - name: error-rate
    description: "5xx errors"
    target: < 0.1%
    percentile: 99
```

### Azure SLA Examples

| Service | SLA | Latency Guarantee |
|---------|-----|-------------------|
| Azure Service Bus Standard | 99.9% | Variable |
| Azure Service Bus Premium | 99.95% | P99 < 10ms |
| Azure SQL | 99.99% | P99 < 2ms (reads) |
| Cosmos DB | 99.999% | P99 < 10ms |

## Monitoring and Alerting

### Alert Thresholds

**Conservative Approach:**
```yaml
alerts:
  - name: latency-warning
    condition: p95 > 200ms
    duration: 5m
    severity: warning
    
  - name: latency-critical
    condition: p99 > 500ms
    duration: 2m
    severity: critical
    
  - name: latency-emergency
    condition: p99 > 2000ms
    duration: 30s
    severity: emergency
```

**Azure Monitor Alert Rule:**
```json
{
  "criteria": {
    "allOf": [
      {
        "metricName": "requests/duration",
        "metricNamespace": "microsoft.insights/components",
        "operator": "GreaterThan",
        "threshold": 500,
        "timeAggregation": "Percentile99",
        "criterionType": "StaticThresholdCriterion"
      }
    ]
  },
  "actions": {
    "actionGroups": ["/subscriptions/.../actionGroups/ops-team"]
  }
}
```

### Dashboard Queries

**Application Insights:**
```kql
// Latency percentiles over time
requests
| where timestamp > ago(24h)
| summarize 
    P50 = percentile(duration, 50),
    P95 = percentile(duration, 95),
    P99 = percentile(duration, 99)
    by bin(timestamp, 5m)
| render timechart
```

**Grafana + Prometheus:**
```promql
# Multi-percentile panel
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

## Percentile Distribution Visualization

### Histogram

```
Response Time Distribution (1000 requests)
─────────────────────────────────────────
 0-50ms   │████████████████████████████████████████│ 650 (65%)
 50-100ms │████████████████████│ 200 (20%)
100-200ms │██████████│ 100 (10%)
200-500ms │███│ 35 (3.5%)
500ms-1s  │█│ 10 (1%)
   >1s    ││ 5 (0.5%)
          └─────────────────────────────────────────
           P50=35ms  P90=120ms  P95=250ms  P99=800ms
```

### Heatmap (Time-based)

```
Hour │ P50  │ P90  │ P99  │ Traffic
─────┼──────┼──────┼──────┼────────
 00  │ 🟢15 │ 🟢35 │ 🟢80 │ Low
 06  │ 🟢20 │ 🟢45 │ 🟡120│ Medium
 12  │ 🟡30 │ 🟡80 │ 🔴250│ High (peak)
 18  │ 🟡25 │ 🟡60 │ 🟡150│ High
 23  │ 🟢18 │ 🟢40 │ 🟢90 │ Low

🟢 = Good  🟡 = Warning  🔴 = Critical
```

## Common Pitfalls

### 1. Using Averages for SLOs

❌ **Wrong:**
```yaml
slo:
  average_latency: < 100ms  # Hides tail latency!
```

✅ **Correct:**
```yaml
slo:
  p99_latency: < 500ms
```

### 2. Not Accounting for Sample Size

Small samples produce unreliable percentiles:

| Sample Size | P99 Reliability |
|-------------|-----------------|
| 100 | Only 1 data point defines P99 |
| 1,000 | 10 data points for P99 |
| 10,000 | 100 data points for P99 |
| 100,000 | Highly reliable |

**Rule of thumb:** Need at least 1,000 samples for reliable P99.

### 3. Aggregating Percentiles Incorrectly

❌ **Wrong:** Average of P99s from multiple servers
```python
# WRONG: This is mathematically incorrect
p99_avg = (server1_p99 + server2_p99 + server3_p99) / 3
```

✅ **Correct:** Calculate P99 from combined data
```python
# Merge all data, then calculate percentile
all_latencies = server1_data + server2_data + server3_data
p99 = np.percentile(all_latencies, 99)
```

### 4. Ignoring Coordination Omission

When measuring latency during overload:

- System processes 100 req/sec normally
- Under load, only processes 50 req/sec
- Missing requests aren't counted → artificially good percentiles!

**Solution:** Use **coordinated omission correction** or **expected latency** metrics.

### 5. Too Short Time Windows

```yaml
# Too short - noisy, many false alarms
window: 1m

# Better - smooths out noise
window: 5m

# Best for SLOs - stable measurements
window: 30m
```

## Best Practices

### 1. Choose the Right Percentile for Your Use Case

| Use Case | Recommended Percentile |
|----------|----------------------|
| General monitoring | P95 |
| SLO definitions | P99 |
| Critical systems | P99.9 |
| Debugging/investigation | P50, P99, P99.9 |

### 2. Monitor Multiple Percentiles

```yaml
# Always track at least 3 percentiles
metrics:
  - p50   # Typical experience
  - p95   # Most users
  - p99   # Tail latency
```

### 3. Set Appropriate Budgets

**Error Budget Example:**
- SLO: P99 < 500ms for 99.9% of time
- Error budget: 43 minutes/month where P99 can exceed 500ms
- Alert at 50% budget consumed

### 4. Use Histograms for Efficient Storage

Instead of storing every value:
```
Buckets: [10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s, 10s]
Counts:  [500,  300,  150,  80,    40,    20,   8,   2,    0,   0]
```

Percentiles calculated from bucket interpolation.

### 5. Correlate with Business Metrics

```sql
-- Find correlation between latency and conversion
SELECT 
    CASE 
        WHEN response_time_ms <= 100 THEN 'Fast (P50)'
        WHEN response_time_ms <= 500 THEN 'Normal (P90)'
        ELSE 'Slow (P99+)'
    END as latency_bucket,
    COUNT(*) as requests,
    AVG(CASE WHEN converted = 1 THEN 1.0 ELSE 0.0 END) as conversion_rate
FROM user_sessions
GROUP BY latency_bucket;
```

## Tools and Libraries

### Metrics Collection

| Tool | Language | Percentile Support |
|------|----------|-------------------|
| **Prometheus** | Any | histogram_quantile() |
| **StatsD** | Any | Timing metrics |
| **Micrometer** | Java | DistributionSummary |
| **OpenTelemetry** | Any | Histogram instrument |

### Monitoring Platforms

| Platform | Feature |
|----------|---------|
| **Azure Monitor** | percentile() in KQL |
| **Application Insights** | Built-in percentile charts |
| **Datadog** | Distribution metrics |
| **New Relic** | Percentile functions |
| **Grafana** | histogram_quantile() |

### Libraries

**Python:**
```python
# NumPy
import numpy as np
np.percentile(data, [50, 95, 99])

# pandas
import pandas as pd
df['latency'].quantile([0.5, 0.95, 0.99])
```

**Java:**
```java
// Apache Commons Math
DescriptiveStatistics stats = new DescriptiveStatistics();
for (double value : data) {
    stats.addValue(value);
}
double p99 = stats.getPercentile(99);

// HdrHistogram (high-performance)
Histogram histogram = new Histogram(3600000000L, 3);
histogram.recordValue(latencyMs);
long p99 = histogram.getValueAtPercentile(99.0);
```

**Go:**
```go
// Using gonum/stat
import "gonum.org/v1/gonum/stat"

p99 := stat.Quantile(0.99, stat.Empirical, data, nil)
```

## References

- [Google SRE Book - Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)
- [Latency Numbers Every Programmer Should Know](https://gist.github.com/jboner/2841832)
- [How NOT to Measure Latency - Gil Tene](https://www.youtube.com/watch?v=lJ8ydIuPFeU)
- [Prometheus Best Practices - Histograms](https://prometheus.io/docs/practices/histograms/)
- [Azure Monitor Percentiles](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/metrics-aggregation-explained)
- [HdrHistogram - High Dynamic Range Histogram](http://hdrhistogram.org/)
- [Web Vitals - Google](https://web.dev/vitals/)
