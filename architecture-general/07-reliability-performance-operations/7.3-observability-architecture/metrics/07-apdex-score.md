---
type: Architecture Pattern
title: "Apdex Score: Application Performance Index"
description: "**Apdex** (Application Performance Index) is an open standard for measuring user satisfaction with application response time. It converts complex response time data into a single score between 0 an..."
tags: [reliability-performance-operations]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Apdex Score: Application Performance Index

## Table of Contents

- [Overview](#overview)
- [What is Apdex?](#what-is-apdex)
- [The Apdex Formula](#the-apdex-formula)
- [Setting the Threshold (T)](#setting-the-threshold-t)
- [Interpreting Apdex Scores](#interpreting-apdex-scores)
- [Apdex Examples](#apdex-examples)
- [Implementation Guide](#implementation-guide)
- [Apdex vs. Percentiles](#apdex-vs-percentiles)
- [Best Practices](#best-practices)
- [Tools and Platforms](#tools-and-platforms)
- [Limitations and Alternatives](#limitations-and-alternatives)

---

## Overview

**Apdex** (Application Performance Index) is an open standard for measuring user satisfaction with application response time. It converts complex response time data into a single score between 0 and 1, making it easy to understand and communicate application performance.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APDEX SCORE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     0.0 ──────────────────────────────────────────────────────── 1.0        │
│     │                                                              │         │
│     ▼                                                              ▼         │
│   ┌─────┐  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌─────┐   │
│   │  0  │  │   0 - 0.5   │  │  0.5 - 0.7   │  │   0.7 - 0.85  │  │ 0.85│   │
│   │     │  │             │  │              │  │               │  │-1.0 │   │
│   │ ❌  │  │   Poor      │  │    Fair      │  │     Good      │  │  ✅ │   │
│   │     │  │ Unacceptable│  │  Needs work  │  │  Satisfactory │  │Excel│   │
│   └─────┘  └─────────────┘  └──────────────┘  └───────────────┘  └─────┘   │
│                                                                              │
│   "Apdex translates response times into user happiness"                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What is Apdex?

### Definition

Apdex categorizes response times into three zones and calculates a ratio that represents user satisfaction:

- **Satisfied**: Response time ≤ T (threshold)
- **Tolerating**: Response time between T and 4T
- **Frustrated**: Response time > 4T

### Why Use Apdex?

| Challenge | How Apdex Helps |
|-----------|-----------------|
| Complex percentile data | Single, easy-to-understand score |
| Explaining performance to non-technical stakeholders | "Our Apdex is 0.92" vs "P95 is 234ms" |
| Setting meaningful SLOs | Target: Apdex ≥ 0.9 |
| Comparing different services | Normalized 0-1 scale |
| Tracking user experience over time | Consistent measurement |

### The Three Zones

```
                    APDEX RESPONSE TIME ZONES
════════════════════════════════════════════════════════════════

Response
Time
   │
4T ─┼─────────────────────────────────────────────────────────
   │                                                     │
   │                    FRUSTRATED                       │
   │                    User gives up                    │  😠
   │                    or is annoyed                    │
   │                                                     │
 T ─┼─────────────────────────────────────────────────────────
   │                                                     │
   │                    TOLERATING                       │  😐
   │                    User notices delay               │
   │                    but waits                        │
   │                                                     │
 0 ─┼─────────────────────────────────────────────────────────
   │                                                     │
   │                    SATISFIED                        │  😊
   │                    User doesn't notice              │
   │                    any delay                        │
   │                                                     │


Example with T = 500ms:
─────────────────────────────────────────────────────────
Satisfied:   0 - 500ms      (feels instant)
Tolerating:  500ms - 2000ms (noticeable but acceptable)
Frustrated:  > 2000ms       (unacceptable delay)
```

---

## The Apdex Formula

### Basic Formula

```
         Satisfied Count + (Tolerating Count × 0.5)
Apdex = ─────────────────────────────────────────────
                    Total Samples

Or equivalently:

         Satisfied + (Tolerating / 2)
Apdex = ──────────────────────────────
                  Total
```

### Formula Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│                      APDEX FORMULA                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Given:                                                          │
│  • T = Target response time threshold                            │
│  • Satisfied count = Responses where time ≤ T                   │
│  • Tolerating count = Responses where T < time ≤ 4T            │
│  • Frustrated count = Responses where time > 4T                 │
│  • Total = All responses                                         │
│                                                                  │
│  Weighting:                                                      │
│  ══════════                                                      │
│  • Satisfied responses:  weight = 1.0 (fully happy)              │
│  • Tolerating responses: weight = 0.5 (partially happy)          │
│  • Frustrated responses: weight = 0.0 (unhappy)                  │
│                                                                  │
│  Why 0.5 for tolerating?                                         │
│  ═══════════════════════                                         │
│  Users who tolerate delays are "half-satisfied" - they got       │
│  their result but the experience wasn't ideal.                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Mathematical Properties

```
Apdex Properties:
═════════════════

• Range: 0.0 to 1.0
• Perfect score (1.0): All responses satisfy (≤ T)
• Worst score (0.0): All responses frustrated (> 4T)
• Threshold invariant: Score changes with T selection

Score interpretation:
• 1.00 = 100% satisfied
• 0.85 = 85% satisfied + 30% tolerating + 0% frustrated
• 0.50 = 100% tolerating OR 50% satisfied + 0% tolerating
• 0.00 = 100% frustrated
```

---

## Setting the Threshold (T)

### Choosing the Right T Value

```
┌─────────────────────────────────────────────────────────────────┐
│                 SELECTING THRESHOLD (T)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Factors to consider:                                            │
│  ════════════════════                                            │
│                                                                  │
│  1. User expectations for this type of operation                 │
│     • Simple page load: 500ms - 2000ms                          │
│     • API call: 100ms - 500ms                                    │
│     • Complex search: 2000ms - 5000ms                           │
│     • Report generation: 5000ms - 30000ms                       │
│                                                                  │
│  2. Historical performance                                       │
│     • Set T around your current P75 or P80                      │
│     • Then work to improve                                       │
│                                                                  │
│  3. Industry benchmarks                                          │
│     • E-commerce: T = 3 seconds (page load)                     │
│     • API: T = 500ms                                             │
│     • Mobile: T = 2 seconds                                      │
│                                                                  │
│  4. Business requirements                                        │
│     • SLA commitments                                            │
│     • Competitive pressure                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended T Values by Use Case

| Use Case | Recommended T | 4T (Frustrated) | Rationale |
|----------|---------------|-----------------|-----------|
| API endpoint | 500ms | 2s | Users expect quick responses |
| Web page load | 2s | 8s | "2 second rule" for web |
| Mobile app screen | 1.5s | 6s | Mobile users less patient |
| Search query | 1s | 4s | Search should feel instant |
| Report generation | 10s | 40s | Users expect longer wait |
| File upload/download | 5s | 20s | Network operations |
| Dashboard refresh | 3s | 12s | Data visualization |

### T Selection Process

```
1. Start with user research
   └─► What do users expect?

2. Analyze current performance
   └─► What's your P75 response time?

3. Set initial T
   └─► Slightly better than current P75

4. Validate with user feedback
   └─► Does Apdex correlate with satisfaction surveys?

5. Iterate
   └─► Adjust T as you improve performance
```

---

## Interpreting Apdex Scores

### Score Ranges

```
                    APDEX SCORE INTERPRETATION
════════════════════════════════════════════════════════════════

Score Range    │  Rating     │  User Experience
───────────────┼─────────────┼──────────────────────────────────
               │             │
0.94 - 1.00    │  Excellent  │  Users rarely notice any delay
               │             │  Exceptional performance
               │             │
0.85 - 0.93    │  Good       │  Most users satisfied
               │             │  Minor improvements possible
               │             │
0.70 - 0.84    │  Fair       │  Some users frustrated
               │             │  Performance needs attention
               │             │
0.50 - 0.69    │  Poor       │  Many users frustrated
               │             │  Performance is a problem
               │             │
0.00 - 0.49    │  Unacceptable│ Most users frustrated
               │             │  Immediate action required
               │             │
```

### Visual Interpretation

```
Apdex Score Scale:
═══════════════════════════════════════════════════════════════

0.0   0.1   0.2   0.3   0.4   0.5   0.6   0.7   0.8   0.9   1.0
 │─────│─────│─────│─────│─────│─────│─────│─────│─────│─────│
 ├─────────────────────────┤     │     ├───────────┤     ├───┤
        UNACCEPTABLE              │       FAIR      │  GOOD  │EXC
          (Action required)      POOR    (Needs     │       │
                            (Problem)    work)      │       │
                                                    │       │
                                               Target: ≥0.85 │
                                                            │
                                                     Ideal: >0.94
```

### Typical Targets

| Environment | Minimum Target | Goal Target |
|-------------|----------------|-------------|
| Production (critical) | 0.90 | 0.95+ |
| Production (standard) | 0.85 | 0.92+ |
| Staging | 0.80 | 0.90+ |
| Development | 0.70 | 0.85+ |

---

## Apdex Examples

### Example 1: Basic Calculation

```
Scenario: API endpoint with T = 500ms
──────────────────────────────────────────────

1000 total requests:
• 750 requests completed in ≤ 500ms (Satisfied)
• 180 requests completed in 500ms - 2000ms (Tolerating)
• 70 requests completed in > 2000ms (Frustrated)

Apdex = (750 + (180 × 0.5)) / 1000
      = (750 + 90) / 1000
      = 840 / 1000
      = 0.84

Rating: Fair - needs improvement
```

### Example 2: E-Commerce Site

```
Scenario: Product page loads with T = 2 seconds
──────────────────────────────────────────────────

10,000 page views today:
• 7,500 loaded in ≤ 2s (Satisfied)
• 2,000 loaded in 2s - 8s (Tolerating)
• 500 loaded in > 8s (Frustrated)

Apdex = (7,500 + (2,000 × 0.5)) / 10,000
      = (7,500 + 1,000) / 10,000
      = 8,500 / 10,000
      = 0.85

Rating: Good - meets target
```

### Example 3: Comparing Different Periods

```
Week-over-Week Comparison:

Last Week:
• Satisfied: 6,000
• Tolerating: 3,000
• Frustrated: 1,000
• Apdex = (6,000 + 1,500) / 10,000 = 0.75

This Week (after optimization):
• Satisfied: 8,000
• Tolerating: 1,500
• Frustrated: 500
• Apdex = (8,000 + 750) / 10,000 = 0.875

Improvement: +0.125 (from Fair to Good)
```

---

## Implementation Guide

### Step 1: Define Thresholds

```yaml
# apdex_config.yaml
services:
  payment_api:
    threshold_ms: 500
    target_apdex: 0.90
    
  product_catalog:
    threshold_ms: 1000
    target_apdex: 0.85
    
  search_service:
    threshold_ms: 800
    target_apdex: 0.92
    
  report_generator:
    threshold_ms: 10000
    target_apdex: 0.80
```

### Step 2: Instrument Your Code

```python
# Python implementation
import time
from dataclasses import dataclass
from typing import List
from enum import Enum

class ApdexZone(Enum):
    SATISFIED = "satisfied"
    TOLERATING = "tolerating"
    FRUSTRATED = "frustrated"

@dataclass
class ApdexConfig:
    threshold_ms: float
    
    @property
    def tolerating_limit_ms(self) -> float:
        return self.threshold_ms * 4

def classify_response(duration_ms: float, config: ApdexConfig) -> ApdexZone:
    if duration_ms <= config.threshold_ms:
        return ApdexZone.SATISFIED
    elif duration_ms <= config.tolerating_limit_ms:
        return ApdexZone.TOLERATING
    else:
        return ApdexZone.FRUSTRATED

def calculate_apdex(durations_ms: List[float], config: ApdexConfig) -> float:
    if not durations_ms:
        return 1.0
    
    satisfied = 0
    tolerating = 0
    
    for duration in durations_ms:
        zone = classify_response(duration, config)
        if zone == ApdexZone.SATISFIED:
            satisfied += 1
        elif zone == ApdexZone.TOLERATING:
            tolerating += 1
    
    return (satisfied + (tolerating * 0.5)) / len(durations_ms)

# Usage
config = ApdexConfig(threshold_ms=500)
response_times = [100, 200, 450, 600, 1200, 3000, 150, 300]
apdex = calculate_apdex(response_times, config)
print(f"Apdex: {apdex:.2f}")  # Output: Apdex: 0.75
```

### Step 3: Track in Prometheus

```python
from prometheus_client import Histogram, Gauge

# Create histogram with buckets aligned to Apdex thresholds
# For T=500ms: buckets at 500ms (T) and 2000ms (4T)
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['service', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]
)

apdex_score = Gauge(
    'apdex_score',
    'Current Apdex score',
    ['service']
)
```

### Step 4: Calculate Apdex in Prometheus

```yaml
# Prometheus recording rules for Apdex
groups:
  - name: apdex
    rules:
      # Apdex for T=0.5s (500ms)
      - record: apdex:service:5m
        expr: |
          (
            sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m])) by (service)
            +
            sum(rate(http_request_duration_seconds_bucket{le="2.0"}[5m])) by (service)
            -
            sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m])) by (service)
          ) * 0.5
          /
          sum(rate(http_request_duration_seconds_count[5m])) by (service)
          
      # Simplified version
      - record: apdex:simple:5m
        expr: |
          (
            sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
            +
            (
              sum(rate(http_request_duration_seconds_bucket{le="2.0"}[5m]))
              -
              sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
            ) * 0.5
          )
          /
          sum(rate(http_request_duration_seconds_count[5m]))
```

---

## Apdex vs. Percentiles

### Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    APDEX vs. PERCENTILES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  APDEX                              PERCENTILES                              │
│  ═════                              ═══════════                              │
│                                                                              │
│  ✅ Single number (0-1)             ✅ Multiple data points                  │
│  ✅ Easy to explain                 ✅ Detailed distribution view            │
│  ✅ Good for dashboards             ✅ No threshold configuration            │
│  ✅ Consistent scale                ✅ Industry standard                     │
│                                                                              │
│  ❌ Requires threshold selection    ❌ Multiple numbers to track             │
│  ❌ Hides distribution details      ❌ Harder to explain to non-tech         │
│  ❌ Can mask bimodal issues         ❌ Different scales per service          │
│                                                                              │
│  Best for:                          Best for:                                │
│  • Executive dashboards             • Engineering analysis                   │
│  • SLO definitions                  • Debugging performance                  │
│  • Trend comparisons                • Capacity planning                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Scenario | Recommendation |
|----------|----------------|
| Board-level reporting | Apdex |
| Engineering deep-dive | Percentiles |
| Alerting | Both (Apdex for overall, percentiles for specific) |
| SLO definition | Apdex or P95/P99 |
| Root cause analysis | Percentiles |
| Cross-service comparison | Apdex |

### Complementary Usage

```
Dashboard Strategy:
════════════════════════════════════════════════════════

Top Level (Executive):
┌─────────────────────────────────────────┐
│  Apdex: 0.92 ✅                         │
│  Status: Good                           │
└─────────────────────────────────────────┘

Mid Level (Operations):
┌─────────────────────────────────────────┐
│  Apdex: 0.92                            │
│  P50: 180ms  P95: 450ms  P99: 890ms    │
│  Satisfied: 85%  Tolerating: 12%        │
└─────────────────────────────────────────┘

Detail Level (Engineering):
┌─────────────────────────────────────────┐
│  Full histogram distribution            │
│  Percentile breakdown by endpoint       │
│  Latency trends over time               │
│  Slow request traces                    │
└─────────────────────────────────────────┘
```

---

## Best Practices

### 1. Choose T Carefully

```
✅ Do:
• Base T on user research
• Consider operation type
• Start conservative, tighten over time
• Document why you chose your T value

❌ Don't:
• Copy arbitrary values from the internet
• Set T too low (everything frustrated)
• Set T too high (false sense of success)
• Change T frequently (invalidates trends)
```

### 2. Use Different T for Different Operations

```yaml
# Different thresholds for different user journeys
apdex_thresholds:
  checkout_flow:
    threshold: 2000ms
    rationale: "Users accept slightly longer wait during checkout"
    
  product_browse:
    threshold: 500ms
    rationale: "Browsing should feel instant"
    
  search:
    threshold: 800ms
    rationale: "Search results should appear quickly"
    
  report_export:
    threshold: 30000ms
    rationale: "Users expect reports to take time"
```

### 3. Alert on Apdex Changes

```yaml
# Prometheus alerting rules
groups:
  - name: apdex_alerts
    rules:
      - alert: LowApdexScore
        expr: apdex:service:5m < 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Apdex below 0.85 for {{ $labels.service }}"
          
      - alert: ApdexDrop
        expr: |
          apdex:service:5m < (apdex:service:1h * 0.9)
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Apdex dropped >10% for {{ $labels.service }}"
```

### 4. Track Apdex Components

```
Don't just track the final score - track the breakdown:

┌────────────────────────────────────────────────────────┐
│  Service: Payment API                                   │
├────────────────────────────────────────────────────────┤
│  Apdex: 0.87                                           │
│                                                         │
│  Breakdown:                                             │
│  ├── Satisfied:   75% (750 requests)     ████████████  │
│  ├── Tolerating:  20% (200 requests)     ███           │
│  └── Frustrated:   5%  (50 requests)     █             │
│                                                         │
│  This shows you WHERE to focus improvement:            │
│  • Moving tolerating → satisfied = +10% boost          │
│  • Eliminating frustrated = +2.5% boost                │
└────────────────────────────────────────────────────────┘
```

---

## Tools and Platforms

### APM Tools with Built-in Apdex

| Tool | Apdex Support | Configuration |
|------|---------------|---------------|
| **New Relic** | Native | Per-app T configuration |
| **Dynatrace** | Native | Automatic T optimization |
| **AppDynamics** | Native | Custom T per business transaction |
| **Datadog** | Manual | Custom metric calculation |
| **Prometheus/Grafana** | Manual | Recording rules |
| **Elastic APM** | Native | Configurable threshold |

### Grafana Dashboard Example

```json
{
  "title": "Apdex Dashboard",
  "panels": [
    {
      "title": "Apdex Score",
      "type": "gauge",
      "targets": [
        {
          "expr": "apdex:service:5m{service=\"payment-api\"}",
          "legendFormat": "Apdex"
        }
      ],
      "options": {
        "thresholds": {
          "steps": [
            { "value": 0, "color": "red" },
            { "value": 0.5, "color": "orange" },
            { "value": 0.7, "color": "yellow" },
            { "value": 0.85, "color": "green" }
          ]
        }
      }
    },
    {
      "title": "Apdex Trend",
      "type": "timeseries",
      "targets": [
        {
          "expr": "apdex:service:5m",
          "legendFormat": "{{ service }}"
        }
      ]
    }
  ]
}
```

---

## Limitations and Alternatives

### Apdex Limitations

```
┌─────────────────────────────────────────────────────────────────┐
│                    APDEX LIMITATIONS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Bimodal Distribution Hiding                                  │
│     ════════════════════════════                                 │
│     Two different user experiences can produce same Apdex:       │
│     • 50% at 100ms + 50% at 1500ms = Apdex 0.75                 │
│     • 100% at 600ms = Apdex 0.75                                │
│     These are very different experiences!                        │
│                                                                  │
│  2. Threshold Sensitivity                                        │
│     ══════════════════════                                       │
│     Small changes in T dramatically affect score.                │
│     Makes cross-team comparisons tricky.                         │
│                                                                  │
│  3. No Error Consideration                                       │
│     ══════════════════════                                       │
│     Apdex only measures response time.                           │
│     A fast error is still "satisfied" by Apdex.                 │
│                                                                  │
│  4. Fixed 4T Multiplier                                          │
│     ═════════════════════                                        │
│     4T may not match actual user tolerance for all operations.   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Addressing Limitations

```
Solution 1: Use Apdex WITH percentiles
─────────────────────────────────────────
Track both: Apdex for overall health, P50/P95/P99 for details

Solution 2: Modified Apdex with errors
─────────────────────────────────────────
         Satisfied + (Tolerating × 0.5) - Errors
Apdex* = ─────────────────────────────────────────
                      Total

Solution 3: Histogram analysis
─────────────────────────────────────────
Use full histograms to detect bimodal distributions
Alert when distribution shape changes
```

### Alternative Metrics

| Metric | Advantage over Apdex |
|--------|---------------------|
| **P95/P99 latency** | No threshold configuration needed |
| **Error rate** | Captures failures Apdex misses |
| **User satisfaction surveys** | Direct user feedback |
| **Core Web Vitals** | Standardized web metrics |
| **Time to Interactive** | Measures perceived performance |

---

## Summary

| Aspect | Details |
|--------|---------|
| **What** | Single score (0-1) measuring user satisfaction |
| **Formula** | (Satisfied + Tolerating×0.5) / Total |
| **Zones** | Satisfied (≤T), Tolerating (T-4T), Frustrated (>4T) |
| **Good Score** | ≥ 0.85 |
| **Best For** | Executive reporting, SLO definition, trends |

### Key Takeaways

1. **Simple communication** - Single score is easy to understand
2. **Choose T wisely** - Threshold selection is critical
3. **Use with percentiles** - They complement each other
4. **Track components** - Know your satisfied/tolerating/frustrated breakdown
5. **Consider errors** - Apdex alone doesn't capture failures

---

## Related Documentation

- [Percentiles in Software Architecture](../percentiles-in-software-architecture.md) - Detailed percentile guide
- [SLI/SLO/SLA](01-sli-slo-sla.md) - Using Apdex in SLO definitions
- [Golden Signals](03-golden-signals.md) - Latency as a golden signal
