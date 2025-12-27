# Error Budgets: Balancing Reliability and Velocity

## Table of Contents

- [Overview](#overview)
- [What is an Error Budget?](#what-is-an-error-budget)
- [Calculating Error Budgets](#calculating-error-budgets)
- [Error Budget Policies](#error-budget-policies)
- [Burn Rate and Alerts](#burn-rate-and-alerts)
- [Error Budget in Practice](#error-budget-in-practice)
- [Decision Framework](#decision-framework)
- [Implementation Guide](#implementation-guide)
- [Common Challenges](#common-challenges)
- [Tools and Dashboards](#tools-and-dashboards)

---

## Overview

An **error budget** is the maximum amount of unreliability you can tolerate while still meeting your SLO. It transforms the tension between "ship features fast" and "keep systems reliable" into a data-driven decision framework.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ERROR BUDGET CONCEPT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   SLO: 99.9% availability                                                   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                      │  │
│   │  ████████████████████████████████████████████████████████████████   │  │
│   │  ├──────────────────────────────────────────────────────────────┤   │  │
│   │  │                       99.9%                                   │   │  │
│   │  │                    Required Uptime                            │   │  │
│   │  │                   (SLO Commitment)                            │   │  │
│   │  ├──────────────────────────────────────────────────────────────┤░░│  │
│   │                                                                   │░░│  │
│   │                                                                   │░░│  │
│   │                                                        ERROR     │░░│  │
│   │                                                        BUDGET    │░░│  │
│   │                                                        (0.1%)    │░░│  │
│   │                                                                   │░░│  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   Error Budget = 100% - SLO = 100% - 99.9% = 0.1%                          │
│                                                                              │
│   In time: 0.1% of 30 days = 43.2 minutes of allowed downtime              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What is an Error Budget?

### Definition

An **error budget** quantifies the acceptable amount of failure over a given time period. It's derived directly from your SLO:

```
Error Budget = 100% - SLO Target
```

### The Core Insight

```
┌─────────────────────────────────────────────────────────────────┐
│              THE ERROR BUDGET PHILOSOPHY                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Traditional Thinking:                                           │
│  ════════════════════                                            │
│  "Zero downtime is the goal"                                     │
│  • Creates conflict between development and operations           │
│  • Discourages any risk-taking                                   │
│  • Reliability is never "enough"                                 │
│                                                                  │
│  Error Budget Thinking:                                          │
│  ══════════════════════                                          │
│  "Some downtime is acceptable and even valuable"                 │
│  • Defines exactly how much unreliability is OK                  │
│  • Creates shared ownership between teams                        │
│  • Enables calculated risk-taking for innovation                 │
│                                                                  │
│  Key principle:                                                  │
│  ══════════════                                                  │
│  "Users don't notice the difference between 99.99% and 100%     │
│   uptime, but they DO notice if you never ship new features"    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why Error Budgets Matter

| Benefit | Description |
|---------|-------------|
| **Shared Ownership** | Dev and Ops share responsibility for the budget |
| **Data-Driven Decisions** | Objective basis for release/stability trade-offs |
| **Risk Management** | Enables calculated risk-taking |
| **Alignment** | Aligns business, product, and engineering goals |
| **Velocity Control** | Natural brake when reliability degrades |

---

## Calculating Error Budgets

### Basic Formula

```
Error Budget (%) = 100% - SLO (%)

Error Budget (time) = Total Time × Error Budget (%)

Error Budget (requests) = Total Requests × Error Budget (%)
```

### Error Budget by SLO Level

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   ERROR BUDGETS BY SLO LEVEL                                │
├──────────┬─────────────┬─────────────┬─────────────┬───────────────────────┤
│   SLO    │ Error Budget│  Per Month  │  Per Quarter│      Per Year         │
├──────────┼─────────────┼─────────────┼─────────────┼───────────────────────┤
│  99%     │    1.0%     │  7.3 hours  │  21.9 hours │    3.65 days          │
│  99.5%   │    0.5%     │  3.6 hours  │  10.9 hours │    1.83 days          │
│  99.9%   │    0.1%     │  43.8 min   │  2.2 hours  │    8.76 hours         │
│  99.95%  │    0.05%    │  21.9 min   │  1.1 hours  │    4.38 hours         │
│  99.99%  │    0.01%    │  4.38 min   │  13.1 min   │    52.6 min           │
│  99.999% │    0.001%   │  26.3 sec   │  1.3 min    │    5.26 min           │
└──────────┴─────────────┴─────────────┴─────────────┴───────────────────────┘
```

### Calculation Examples

#### Example 1: Availability-Based Budget

```
Service: Payment API
SLO: 99.9% availability over 30 days
Total time: 30 days × 24 hours × 60 minutes = 43,200 minutes

Error Budget = 100% - 99.9% = 0.1%
Error Budget (minutes) = 43,200 × 0.001 = 43.2 minutes

You can afford 43.2 minutes of downtime per month.
```

#### Example 2: Request-Based Budget

```
Service: Search API
SLO: 99.95% of requests successful
Monthly traffic: 100,000,000 requests

Error Budget = 100% - 99.95% = 0.05%
Error Budget (requests) = 100,000,000 × 0.0005 = 50,000 failed requests

You can afford 50,000 failed requests per month.
```

#### Example 3: Latency-Based Budget

```
Service: Product Catalog
SLO: 99% of requests complete in < 200ms
Monthly traffic: 50,000,000 requests

Error Budget = 100% - 99% = 1%
Error Budget (slow requests) = 50,000,000 × 0.01 = 500,000 requests

You can afford 500,000 requests exceeding 200ms per month.
```

### Multi-SLI Error Budget

```
When you have multiple SLIs, each has its own budget:

Service: E-Commerce Platform

SLI 1: Availability
  SLO: 99.9%
  Budget: 43.2 min/month

SLI 2: Latency (P99 < 500ms)
  SLO: 99%
  Budget: 1% of requests can be slow

SLI 3: Error Rate
  SLO: 99.5%
  Budget: 0.5% of requests can fail

Track each budget separately!
The most depleted budget determines overall health.
```

---

## Error Budget Policies

### What is an Error Budget Policy?

An **error budget policy** defines what happens when the budget is consumed. It creates consequences that drive behavior.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ERROR BUDGET POLICY                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Budget Status         │  Actions                                           │
│  ══════════════════════╪════════════════════════════════════════════════   │
│                        │                                                     │
│  Budget > 50%          │  ✅ Normal operations                              │
│  (Healthy)             │  • Ship features freely                            │
│                        │  • Experiment with changes                         │
│                        │  • Take calculated risks                           │
│                        │                                                     │
│  Budget 25-50%         │  ⚠️ Caution                                        │
│  (Warning)             │  • Review upcoming risky changes                   │
│                        │  • Increase testing for deployments                │
│                        │  • Consider deferring major changes                │
│                        │                                                     │
│  Budget 0-25%          │  🔶 Restricted                                     │
│  (Critical)            │  • Only deploy bug fixes and reliability work      │
│                        │  • Freeze feature releases                         │
│                        │  • Focus on stability improvements                 │
│                        │                                                     │
│  Budget Exhausted      │  🔴 Frozen                                         │
│  (Depleted)            │  • Stop all non-essential changes                  │
│                        │  • Emergency reliability focus                     │
│                        │  • Requires executive approval for releases        │
│                        │                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sample Error Budget Policy Document

```yaml
# error_budget_policy.yaml

service: payment-api
slo: 99.9% availability
budget_window: 30 days rolling

policy:
  healthy:
    threshold: "> 50% budget remaining"
    actions:
      - "Normal development velocity"
      - "Feature releases allowed"
      - "Experiments allowed"
    approval_required: "Team lead"
    
  warning:
    threshold: "25-50% budget remaining"
    actions:
      - "Risky deployments require SRE review"
      - "Increase canary duration to 2 hours"
      - "Daily error budget review"
    approval_required: "Engineering Manager"
    
  critical:
    threshold: "< 25% budget remaining"
    actions:
      - "Feature freeze"
      - "Only bug fixes and reliability improvements"
      - "Mandatory rollback plan for all changes"
      - "Twice-daily error budget review"
    approval_required: "Director of Engineering"
    
  exhausted:
    threshold: "0% budget remaining"
    actions:
      - "Complete deployment freeze"
      - "All hands on reliability"
      - "Incident review for budget depletion"
      - "Recovery plan required"
    approval_required: "VP of Engineering"

exceptions:
  - "Security patches always allowed"
  - "Regulatory compliance changes always allowed"
  - "Revenue-critical hotfixes with executive approval"
```

---

## Burn Rate and Alerts

### What is Burn Rate?

**Burn rate** measures how quickly you're consuming your error budget relative to the ideal rate.

```
                     Current error rate
Burn Rate = ──────────────────────────────────────
             Ideal error rate (budget / window)


Burn Rate = 1.0 → Consuming budget exactly on pace
Burn Rate = 2.0 → Consuming budget 2x faster than sustainable
Burn Rate = 0.5 → Consuming budget at half the sustainable rate
```

### Burn Rate Calculation Example

```
SLO: 99.9% availability (0.1% error budget)
Window: 30 days

Ideal error rate = 0.1% / 30 days = 0.00333% per day

If current error rate = 0.01% (last day):
Burn Rate = 0.01% / 0.00333% = 3.0

Interpretation: At this rate, you'll exhaust your monthly 
budget in 10 days instead of 30.
```

### Multi-Window Burn Rate Alerting

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-WINDOW BURN RATE ALERTS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  The challenge: Single-window alerts either miss slow burns or              │
│  alert too aggressively on brief spikes.                                    │
│                                                                              │
│  Solution: Use multiple windows with different burn rates                   │
│                                                                              │
│  ┌────────────────┬────────────────┬────────────────┬─────────────────┐    │
│  │  Alert Level   │  Long Window   │  Short Window  │  Burn Rate      │    │
│  ├────────────────┼────────────────┼────────────────┼─────────────────┤    │
│  │  Page (2% budget│  1 hour        │  5 minutes     │  14.4x          │    │
│  │  in 1 hour)    │                │                │                 │    │
│  ├────────────────┼────────────────┼────────────────┼─────────────────┤    │
│  │  Page (5% budget│  6 hours       │  30 minutes    │  6x             │    │
│  │  in 6 hours)   │                │                │                 │    │
│  ├────────────────┼────────────────┼────────────────┼─────────────────┤    │
│  │  Ticket (10%   │  3 days        │  6 hours       │  1x             │    │
│  │  in 3 days)    │                │                │                 │    │
│  └────────────────┴────────────────┴────────────────┴─────────────────┘    │
│                                                                              │
│  Logic: Alert fires when BOTH windows exceed threshold                      │
│  This prevents alerting on brief spikes while catching sustained issues    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Prometheus Alert Rules for Burn Rate

```yaml
groups:
  - name: error_budget_alerts
    rules:
      # Fast burn - high severity (2% budget in 1 hour)
      # Burn rate 14.4 = 0.1% * 30 days * 24 hours / (0.1% budget * 1 hour / 0.02)
      - alert: ErrorBudgetFastBurn
        expr: |
          (
            # Long window: 1 hour
            sum(rate(http_requests_total{status=~"5.."}[1h])) 
            / sum(rate(http_requests_total[1h]))
          ) > (14.4 * 0.001)
          and
          (
            # Short window: 5 minutes
            sum(rate(http_requests_total{status=~"5.."}[5m])) 
            / sum(rate(http_requests_total[5m]))
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error budget burn rate - 2% budget consumed in 1 hour"
          
      # Slow burn - medium severity (10% budget in 3 days)  
      - alert: ErrorBudgetSlowBurn
        expr: |
          (
            # Long window: 3 days
            sum(rate(http_requests_total{status=~"5.."}[3d])) 
            / sum(rate(http_requests_total[3d]))
          ) > (1 * 0.001)
          and
          (
            # Short window: 6 hours
            sum(rate(http_requests_total{status=~"5.."}[6h])) 
            / sum(rate(http_requests_total[6h]))
          ) > (1 * 0.001)
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Slow error budget burn - 10% budget in 3 days"
```

---

## Error Budget in Practice

### Monthly Budget Review Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONTHLY ERROR BUDGET REVIEW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Week 1: Review Period Opens                                                 │
│  ═══════════════════════════                                                │
│  • Generate error budget report                                              │
│  • Identify budget consumption by incident                                   │
│  • Note any policy violations                                                │
│                                                                              │
│  Week 2: Analysis                                                            │
│  ═════════════════                                                           │
│  • Root cause analysis of major budget consumers                             │
│  • Identify patterns                                                         │
│  • Assign action items                                                       │
│                                                                              │
│  Week 3: Planning                                                            │
│  ════════════════                                                            │
│  • Plan reliability improvements                                             │
│  • Adjust deployment schedule if needed                                      │
│  • Update runbooks                                                           │
│                                                                              │
│  Week 4: Execution & Prep                                                    │
│  ═════════════════════════                                                   │
│  • Implement improvements                                                    │
│  • Prepare next month's deployment plan                                      │
│  • Communicate budget status to stakeholders                                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Error Budget Report Template

```
═══════════════════════════════════════════════════════════════════
                    ERROR BUDGET REPORT
                    Service: Payment API
                    Period: November 2025
═══════════════════════════════════════════════════════════════════

SUMMARY
───────────────────────────────────────────────────────────────────
SLO Target:           99.9% availability
Budget Allocation:    43.2 minutes
Budget Consumed:      28.5 minutes (66%)
Budget Remaining:     14.7 minutes (34%)
Status:               ⚠️ WARNING

BUDGET CONSUMPTION BREAKDOWN
───────────────────────────────────────────────────────────────────
Incident         │ Duration │ % of Budget │ Root Cause
─────────────────┼──────────┼─────────────┼─────────────────────
INC-2025-1101    │ 15 min   │ 35%         │ Database failover
INC-2025-1108    │ 8 min    │ 19%         │ Bad deployment
INC-2025-1115    │ 5.5 min  │ 13%         │ Third-party API
─────────────────┼──────────┼─────────────┼─────────────────────
TOTAL            │ 28.5 min │ 66%         │

POLICY STATUS
───────────────────────────────────────────────────────────────────
Current Policy:   WARNING (25-50% remaining)
Restrictions:     
  • Risky deployments require SRE approval
  • Increased canary duration (2 hours)
  
RECOMMENDATIONS
───────────────────────────────────────────────────────────────────
1. Improve database failover automation (35% of budget)
2. Enhance deployment rollback speed (19% of budget)
3. Add circuit breaker for third-party API (13% of budget)

NEXT MONTH OUTLOOK
───────────────────────────────────────────────────────────────────
Planned releases: 4
Risk assessment: Medium
Expected budget consumption: 40-50%
```

---

## Decision Framework

### Using Error Budget for Decisions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR BUDGET DECISION MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        Budget Status                                         │
│                 Healthy    Warning    Critical    Exhausted                  │
│                 (>50%)    (25-50%)   (0-25%)      (0%)                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Major          ✅         ⚠️          ❌          ❌                        │
│  Feature        Go ahead   Review     Defer       No way                    │
│                           with SRE                                          │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Minor          ✅         ✅          ⚠️          ❌                        │
│  Feature        Go ahead   Go ahead   Review      Defer                     │
│                                       required                               │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Bug Fix        ✅         ✅          ✅          ✅                        │
│                 Go ahead   Go ahead   Priority    Emergency                 │
│                                       boost       priority                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Reliability    ✅         ✅          ✅          ✅                        │
│  Work           Schedule   Priority   High        Emergency                 │
│                                       priority    priority                   │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Experiment/    ✅         ⚠️          ❌          ❌                        │
│  A-B Test       Go ahead   Limited    Defer       No way                    │
│                           scope                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Trade-off Scenarios

```
Scenario 1: Budget is Healthy, Want to Ship Risky Feature
────────────────────────────────────────────────────────────
Budget: 70% remaining
Feature: Major rewrite of payment processing

Decision Framework:
1. Estimate risk: Could cause 10 minutes downtime (worst case)
2. Budget impact: 10 min / 43.2 min = 23% of budget
3. Post-release budget: 70% - 23% = 47% (still healthy)
4. Decision: ✅ Proceed with extra monitoring

Scenario 2: Budget is Low, Critical Business Feature Needed
────────────────────────────────────────────────────────────
Budget: 15% remaining
Feature: Black Friday sale feature (business critical)

Decision Framework:
1. Business value: Very high (significant revenue)
2. Risk: Medium (new code, tested thoroughly)
3. Mitigation: Canary release, instant rollback ready
4. Decision: ✅ Proceed with maximum precautions + exec approval

Scenario 3: Budget Exhausted, Minor Feature Ready
────────────────────────────────────────────────────────────
Budget: 0% remaining
Feature: UI improvement (nice-to-have)

Decision Framework:
1. Business value: Low-medium
2. Risk: Low (frontend only)
3. Current priority: Reliability recovery
4. Decision: ❌ Defer until next month
```

---

## Implementation Guide

### Step 1: Define Your SLOs

```yaml
# slo_definitions.yaml
services:
  payment-api:
    availability:
      target: 99.9%
      window: 30d
      measurement: "successful HTTP responses / total responses"
      
    latency:
      target: 99%
      threshold: 500ms
      window: 30d
      measurement: "requests under 500ms / total requests"
      
  user-service:
    availability:
      target: 99.5%
      window: 30d
```

### Step 2: Calculate Budgets

```python
def calculate_error_budget(slo_target: float, window_days: int) -> dict:
    """Calculate error budget from SLO."""
    error_budget_percent = 100 - slo_target
    
    # Time-based budget
    total_minutes = window_days * 24 * 60
    budget_minutes = total_minutes * (error_budget_percent / 100)
    
    return {
        "slo_target": slo_target,
        "error_budget_percent": error_budget_percent,
        "window_days": window_days,
        "budget_minutes": round(budget_minutes, 1),
        "budget_hours": round(budget_minutes / 60, 2),
    }

# Example
budget = calculate_error_budget(slo_target=99.9, window_days=30)
# Output: {'slo_target': 99.9, 'error_budget_percent': 0.1, 
#          'window_days': 30, 'budget_minutes': 43.2, 'budget_hours': 0.72}
```

### Step 3: Track Budget Consumption

```python
from prometheus_client import Gauge, Counter
from datetime import datetime, timedelta

# Metrics for tracking
error_budget_total = Gauge(
    'error_budget_total_minutes',
    'Total error budget in minutes',
    ['service']
)

error_budget_consumed = Gauge(
    'error_budget_consumed_minutes',
    'Consumed error budget in minutes',
    ['service']
)

error_budget_remaining = Gauge(
    'error_budget_remaining_percent',
    'Remaining error budget as percentage',
    ['service']
)

def update_error_budget_metrics(service: str, 
                                 total_requests: int,
                                 failed_requests: int,
                                 slo_target: float,
                                 window_days: int):
    """Update error budget metrics."""
    
    # Calculate current error rate
    actual_error_rate = failed_requests / total_requests if total_requests > 0 else 0
    allowed_error_rate = (100 - slo_target) / 100
    
    # Budget in request terms
    budget_total_requests = total_requests * allowed_error_rate
    budget_consumed_requests = failed_requests
    
    # As percentage
    budget_remaining_pct = max(0, 
        (budget_total_requests - budget_consumed_requests) / budget_total_requests * 100
    ) if budget_total_requests > 0 else 100
    
    # Update metrics
    error_budget_remaining.labels(service=service).set(budget_remaining_pct)
```

### Step 4: Create Dashboards

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ERROR BUDGET DASHBOARD                               [Rolling 30 Days ▼]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    BUDGET REMAINING BY SERVICE                         │ │
│  │                                                                        │ │
│  │  Payment API     ████████████████████████░░░░░░░░   62%  ✅           │ │
│  │  User Service    ██████████████████████████████░░   78%  ✅           │ │
│  │  Search API      ████████████░░░░░░░░░░░░░░░░░░░░   32%  ⚠️           │ │
│  │  Inventory       ████████████████████████████████   95%  ✅           │ │
│  │  Notification    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   12%  🔴           │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │     BURN RATE (Payment API)     │  │    BUDGET TREND (30 days)       │ │
│  │                                 │  │                                  │ │
│  │  Current: 1.2x  ⚠️              │  │  100%─┤                          │ │
│  │                                 │  │       │╲                         │ │
│  │  At this rate, budget will      │  │   75%─┤ ╲                        │ │
│  │  exhaust in: 22 days            │  │       │  ╲                       │ │
│  │                                 │  │   50%─┤   ╲────────────         │ │
│  │  ┌─────────────────────────┐   │  │       │              ╲────       │ │
│  │  │  0.5x  1x   2x   5x 10x │   │  │   25%─┤                    ╲     │ │
│  │  │   │    ▼    │    │   │  │   │  │       │                          │ │
│  │  └─────────────────────────┘   │  │    0%─┴──┬──┬──┬──┬──┬──┬──┬    │ │
│  │       OK   ⚠️   🔴  🔴  🔴     │  │       Day 1        Today  Day 30  │ │
│  └─────────────────────────────────┘  └─────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    RECENT BUDGET-CONSUMING EVENTS                      │ │
│  │                                                                        │ │
│  │  Time           │ Service     │ Duration │ Budget Impact │ Cause      │ │
│  │  ────────────────────────────────────────────────────────────────────  │ │
│  │  Nov 15, 14:30  │ Notification│ 8 min    │ 18%           │ Deploy bug │ │
│  │  Nov 12, 09:15  │ Search API  │ 12 min   │ 28%           │ DB timeout │ │
│  │  Nov 10, 22:00  │ Payment API │ 5 min    │ 12%           │ Provider   │ │
│  │                                                                        │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Common Challenges

### Challenge 1: Getting Buy-In

```
Problem: Teams resist "allowing" failures

Solutions:
───────────────────────────────────────────────────────
1. Frame as "reliability investment"
   • "We're investing 0.1% to maintain 99.9%"
   
2. Show the trade-off clearly
   • "99.99% = 52 min/year budget vs 99.9% = 8.76 hours"
   • "That extra 9 costs 10x more engineering effort"
   
3. Start with a pilot service
   • Prove the concept, then expand
   
4. Get executive sponsorship
   • Present as risk management, not "allowing failures"
```

### Challenge 2: Attribution

```
Problem: Hard to attribute budget consumption to causes

Solutions:
───────────────────────────────────────────────────────
1. Automate incident tracking
   • Link monitoring alerts to incidents
   • Track duration automatically
   
2. Categorize consumption
   • Infrastructure vs. code vs. dependencies
   • Planned vs. unplanned
   
3. Use deployment markers
   • Correlate budget consumption with releases
   
4. Integrate with incident management
   • PagerDuty, Opsgenie integration
```

### Challenge 3: Gaming the System

```
Problem: Teams manipulate metrics to preserve budget

Examples:
• Lowering SLO targets
• Excluding certain errors
• Resetting budget windows

Solutions:
───────────────────────────────────────────────────────
1. Lock SLO definitions
   • Require approval for SLO changes
   
2. Audit metric definitions
   • Regular review of what counts as success/failure
   
3. External validation
   • Compare internal metrics to external monitoring
   
4. Tie to business outcomes
   • Correlate with user complaints, revenue impact
```

---

## Tools and Dashboards

### Error Budget Tools

| Tool | Features | Integration |
|------|----------|-------------|
| **Google Cloud SLO** | Native error budgets, burn rate | GCP services |
| **Nobl9** | Dedicated SLO platform | Multi-cloud |
| **Datadog SLO** | Visual budgets, alerts | Full-stack |
| **Prometheus + Grafana** | Flexible, open source | Custom metrics |
| **Sloth** | SLO/Error budget generator | Prometheus |
| **OpenSLO** | Standard SLO definition format | Portable |

### Prometheus Recording Rules

```yaml
groups:
  - name: error_budget_calculations
    rules:
      # 30-day error budget remaining (percentage)
      - record: error_budget:remaining:ratio
        expr: |
          1 - (
            sum(increase(http_requests_total{status=~"5.."}[30d]))
            /
            (sum(increase(http_requests_total[30d])) * 0.001)
          )
        labels:
          slo: "99.9% availability"
          
      # Current burn rate
      - record: error_budget:burn_rate:1h
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) / 0.001
```

---

## Summary

| Concept | Definition |
|---------|------------|
| **Error Budget** | Maximum acceptable unreliability (100% - SLO) |
| **Burn Rate** | Speed of budget consumption vs. sustainable rate |
| **Policy** | Rules for actions based on budget status |
| **Window** | Time period for budget calculation |

### Key Takeaways

1. **Error budgets quantify risk** - Make trade-offs explicit
2. **Policies drive behavior** - Create consequences for budget depletion
3. **Burn rate enables proactive alerting** - Catch slow degradation
4. **Shared ownership** - Both dev and ops own the budget
5. **Data-driven decisions** - Objective basis for velocity vs. reliability

---

## Related Documentation

- [SLI/SLO/SLA](01-sli-slo-sla.md) - Foundation for error budgets
- [MTTR/MTTF/MTBF](06-mttr-mttf-mtbf.md) - Reliability time metrics
- [Golden Signals](03-golden-signals.md) - What to measure
