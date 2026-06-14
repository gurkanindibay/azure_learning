---
type: Architecture Pattern
title: "DORA Metrics"
description: "**DORA Metrics** are four key metrics identified by the DevOps Research and Assessment (DORA) team through years of research. These metrics measure software delivery performance and organizational ..."
tags: [reliability-performance-operations]
timestamp: 2026-06-14T00:00:00Z
---

# DORA Metrics

## Table of Contents

- [Overview](#overview)
- [The Four Key Metrics](#the-four-key-metrics)
  - [1. Deployment Frequency](#1-deployment-frequency)
  - [2. Lead Time for Changes](#2-lead-time-for-changes)
  - [3. Change Failure Rate](#3-change-failure-rate)
  - [4. Mean Time to Recovery (MTTR)](#4-mean-time-to-recovery-mttr)
- [Performance Levels](#performance-levels)
- [The Fifth Metric: Reliability](#the-fifth-metric-reliability)
- [Measuring DORA Metrics](#measuring-dora-metrics)
- [Implementation Strategies](#implementation-strategies)
- [Common Pitfalls](#common-pitfalls)
- [Tools and Platforms](#tools-and-platforms)
- [Improving Your DORA Metrics](#improving-your-dora-metrics)
- [DORA Metrics and Business Outcomes](#dora-metrics-and-business-outcomes)

---

## Overview

**DORA Metrics** are four key metrics identified by the DevOps Research and Assessment (DORA) team through years of research. These metrics measure software delivery performance and organizational performance, providing a data-driven approach to understanding DevOps capabilities.

```
┌─────────────────────────────────────────────────────────────────┐
│                       DORA METRICS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│     VELOCITY (Throughput)          STABILITY (Quality)          │
│     ═════════════════════          ═══════════════════          │
│                                                                  │
│     📈 Deployment                  📉 Change Failure            │
│        Frequency                      Rate                       │
│        "How often do we             "How often do                │
│         deploy?"                     deployments fail?"          │
│                                                                  │
│     ⏱️  Lead Time for              🔧 Mean Time to              │
│        Changes                        Recovery                   │
│        "How fast from commit        "How quickly do we          │
│         to production?"              recover from failures?"    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why DORA Metrics Matter

The DORA research, now part of Google Cloud, has demonstrated that:

1. **High performers excel at all four metrics** - There's no trade-off between speed and stability
2. **These metrics predict organizational performance** - Teams with better DORA metrics have better business outcomes
3. **They're universally applicable** - Work across industries, company sizes, and tech stacks
4. **They drive continuous improvement** - Provide clear targets for DevOps transformation

> "Our research has found that these metrics are predictive of both software delivery performance and organizational performance, including profitability, market share, and customer satisfaction."
> — DORA State of DevOps Report

---

## The Four Key Metrics

### 1. Deployment Frequency

**Definition**: How often an organization successfully releases to production.

```
┌─────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT FREQUENCY                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  WHAT TO MEASURE                                            │
│  ═══════════════                                            │
│  • Successful deployments to production                     │
│  • Per application/service (not aggregate)                  │
│  • Automated AND manual deployments                         │
│                                                              │
│  WHAT NOT TO MEASURE                                        │
│  ═══════════════════                                        │
│  ✗ Deployments to non-production environments               │
│  ✗ Failed deployments                                       │
│  ✗ Rollbacks (count separately)                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why It Matters

- **Faster feedback loops**: More frequent deployments mean faster user feedback
- **Smaller batch sizes**: Reduces risk and complexity per deployment
- **Higher agility**: Ability to respond quickly to market changes
- **Better flow**: Indicates healthy CI/CD pipelines and processes

#### Calculation

```
Deployment Frequency = Number of Successful Deployments / Time Period

Examples:
- Daily deployments: 5 deploys/day
- Weekly deployments: 10 deploys/week
- Monthly: 20 deploys/month
```

#### Performance Benchmarks

| Level | Deployment Frequency |
|-------|---------------------|
| Elite | On-demand (multiple deploys per day) |
| High | Between once per day and once per week |
| Medium | Between once per week and once per month |
| Low | Between once per month and once every six months |

---

### 2. Lead Time for Changes

**Definition**: The time it takes to go from code committed to code successfully running in production.

```
┌─────────────────────────────────────────────────────────────┐
│                 LEAD TIME FOR CHANGES                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │  Code   │───▶│  Build  │───▶│  Test   │───▶│ Deploy  │  │
│  │ Commit  │    │ & CI    │    │ & QA    │    │ to Prod │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │                                             │       │
│       │◄───────────── LEAD TIME ───────────────────▶│       │
│                                                              │
│  Includes:                                                   │
│  • Code review time                                         │
│  • Build time                                               │
│  • Test execution time                                      │
│  • Deployment time                                          │
│  • Any manual approval wait times                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why It Matters

- **Time to value**: How quickly can you deliver value to customers?
- **Process efficiency**: Identifies bottlenecks in your delivery pipeline
- **Competitive advantage**: Faster lead times enable faster innovation
- **Developer experience**: Long lead times frustrate developers

#### Calculation

```
Lead Time = Timestamp(Production Deployment) - Timestamp(Code Commit)

For aggregate metrics:
- Use median or percentiles (P50, P90)
- Avoid averages (can be skewed by outliers)
```

#### What to Include

| Include | Exclude |
|---------|---------|
| Code review wait time | Time before first commit (planning) |
| CI/CD pipeline duration | Feature development time |
| Manual approval wait time | Requirements gathering |
| Deployment execution time | Design and architecture time |

#### Performance Benchmarks

| Level | Lead Time for Changes |
|-------|----------------------|
| Elite | Less than one hour |
| High | Between one day and one week |
| Medium | Between one week and one month |
| Low | Between one month and six months |

---

### 3. Change Failure Rate

**Definition**: The percentage of deployments causing a failure in production that requires remediation (rollback, hotfix, patch, etc.).

```
┌─────────────────────────────────────────────────────────────┐
│                   CHANGE FAILURE RATE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    Total Deployments                         │
│                    ═════════════════                         │
│                           │                                  │
│            ┌──────────────┴──────────────┐                  │
│            │                             │                   │
│            ▼                             ▼                   │
│     ┌─────────────┐              ┌─────────────┐            │
│     │  Successful │              │   Failed    │            │
│     │ Deployments │              │ Deployments │            │
│     └─────────────┘              └─────────────┘            │
│                                        │                     │
│                                        ▼                     │
│                              Requires Remediation:           │
│                              • Rollback                      │
│                              • Hotfix                        │
│                              • Emergency patch               │
│                              • Incident declared             │
│                                                              │
│  Change Failure Rate = Failed Deployments / Total × 100%    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why It Matters

- **Quality indicator**: Measures the effectiveness of your testing and review processes
- **Risk assessment**: Higher rates indicate higher deployment risk
- **Trust metric**: Teams with low CFR can deploy more confidently
- **Process health**: Reflects the maturity of CI/CD practices

#### What Counts as a Failure?

| Counts as Failure | Does NOT Count as Failure |
|-------------------|---------------------------|
| Service degradation requiring rollback | Minor bugs fixed in next release |
| Incidents caused by deployment | Planned feature flags/toggles |
| Emergency hotfixes needed | Configuration changes |
| Customer-impacting issues | Cosmetic issues |
| SLO violations caused by change | Issues caught in canary/staged rollout |

#### Calculation

```
Change Failure Rate = (Failed Deployments / Total Deployments) × 100%

Example:
- 100 deployments in a month
- 8 required rollback or hotfix
- CFR = 8/100 = 8%
```

#### Performance Benchmarks

| Level | Change Failure Rate |
|-------|---------------------|
| Elite | 0-15% |
| High | 16-30% |
| Medium | 16-30% |
| Low | 46-60% |

---

### 4. Mean Time to Recovery (MTTR)

**Definition**: How long it takes to recover from a failure in production (service outage, degradation, or incident).

```
┌─────────────────────────────────────────────────────────────┐
│                  MEAN TIME TO RECOVERY                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Timeline of an Incident:                                   │
│                                                              │
│  ──────────────────────────────────────────────────────────▶│
│  │         │              │              │         │        │
│  Failure   Detection      Response       Resolution Service │
│  Occurs    (Alert)        Begins         Applied    Restored│
│  │         │              │              │         │        │
│  │◄─MTTD──▶│◄───MTTA────▶│◄────MTTR────▶│         │        │
│  │                                                 │        │
│  │◄───────────────── MTTR (Total) ────────────────▶│        │
│                                                              │
│  MTTD = Mean Time to Detect                                 │
│  MTTA = Mean Time to Acknowledge                            │
│  MTTR = Mean Time to Repair/Resolve                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Why It Matters

- **Resilience indicator**: Shows how quickly you can bounce back
- **User impact**: Directly correlates to downtime experienced by users
- **Operational maturity**: Reflects incident response capabilities
- **SLA compliance**: Critical for meeting availability commitments

#### What to Measure

| Include | Considerations |
|---------|---------------|
| Time from incident start to service restoration | Use consistent start/end definitions |
| All production incidents | Track by severity level |
| Both deployment and non-deployment failures | Separate if needed for analysis |

#### Calculation

```
MTTR = Sum of All Recovery Times / Number of Incidents

Example:
- Incident 1: 45 minutes to recover
- Incident 2: 120 minutes to recover
- Incident 3: 30 minutes to recover
- MTTR = (45 + 120 + 30) / 3 = 65 minutes
```

#### Performance Benchmarks

| Level | Time to Restore Service |
|-------|------------------------|
| Elite | Less than one hour |
| High | Less than one day |
| Medium | Between one day and one week |
| Low | More than six months |

---

## Performance Levels

The DORA research categorizes teams into four performance levels:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DORA PERFORMANCE LEVELS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ELITE                                                          │
│  ═════                                                          │
│  • Deploy: On-demand (multiple per day)                         │
│  • Lead Time: < 1 hour                                          │
│  • CFR: 0-15%                                                   │
│  • MTTR: < 1 hour                                               │
│                                                                  │
│  HIGH                                                           │
│  ════                                                           │
│  • Deploy: Daily to weekly                                      │
│  • Lead Time: 1 day to 1 week                                   │
│  • CFR: 16-30%                                                  │
│  • MTTR: < 1 day                                                │
│                                                                  │
│  MEDIUM                                                         │
│  ══════                                                         │
│  • Deploy: Weekly to monthly                                    │
│  • Lead Time: 1 week to 1 month                                 │
│  • CFR: 16-30%                                                  │
│  • MTTR: 1 day to 1 week                                        │
│                                                                  │
│  LOW                                                            │
│  ═══                                                            │
│  • Deploy: Monthly to semi-annually                             │
│  • Lead Time: 1 to 6 months                                     │
│  • CFR: 46-60%                                                  │
│  • MTTR: > 6 months                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Level Comparison

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **Deployment Frequency** | On-demand (multiple/day) | Daily to weekly | Weekly to monthly | Monthly to semi-annually |
| **Lead Time for Changes** | < 1 hour | 1 day - 1 week | 1 week - 1 month | 1 - 6 months |
| **Change Failure Rate** | 0-15% | 16-30% | 16-30% | 46-60% |
| **Time to Restore** | < 1 hour | < 1 day | 1 day - 1 week | > 6 months |

---

## The Fifth Metric: Reliability

In recent years, DORA has added a fifth metric focused on operational performance:

```
┌─────────────────────────────────────────────────────────────┐
│                      RELIABILITY                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Definition: Meeting or exceeding reliability targets        │
│                                                              │
│  Measured through:                                          │
│  • SLO achievement rate                                     │
│  • Availability percentage                                  │
│  • Error budget consumption                                 │
│                                                              │
│  Why Added:                                                 │
│  • Balances velocity with stability                         │
│  • Directly ties to user experience                         │
│  • Aligns with SRE practices                                │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  "Operational performance is a key factor in        │    │
│  │   overall organizational performance"               │    │
│  │                      — DORA 2021 Report             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Measuring DORA Metrics

### Data Sources

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA SOURCES FOR DORA METRICS                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DEPLOYMENT FREQUENCY                                       │
│  ────────────────────                                       │
│  • CI/CD pipeline logs (Jenkins, GitHub Actions, GitLab)    │
│  • Deployment tools (ArgoCD, Spinnaker, Octopus)           │
│  • Change management systems                                │
│                                                              │
│  LEAD TIME FOR CHANGES                                      │
│  ────────────────────                                       │
│  • Version control systems (Git commits)                    │
│  • CI/CD pipeline timestamps                                │
│  • Deployment logs with commit SHA references               │
│                                                              │
│  CHANGE FAILURE RATE                                        │
│  ────────────────────                                       │
│  • Incident management systems (PagerDuty, Opsgenie)        │
│  • Rollback logs from deployment tools                      │
│  • Post-incident reviews/RCAs                               │
│                                                              │
│  MEAN TIME TO RECOVERY                                      │
│  ────────────────────                                       │
│  • Incident management systems                              │
│  • Monitoring/alerting platforms                            │
│  • Status page history                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Measurement Best Practices

| Practice | Description |
|----------|-------------|
| **Automate collection** | Manual tracking is error-prone and unsustainable |
| **Measure per service** | Aggregate metrics hide important variations |
| **Use consistent definitions** | Document what counts as deployment, failure, etc. |
| **Track trends over time** | Point-in-time values are less meaningful |
| **Segment by team/service** | Enable team-level improvement efforts |

### Sample Dashboard Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    DORA METRICS DASHBOARD                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Deployment Frequency │  │ Lead Time for Changes│        │
│  │                      │  │                      │        │
│  │   ████████████ 12/day│  │   P50: 2.3 hours    │        │
│  │   ▲ 20% vs last week │  │   P90: 8.1 hours    │        │
│  │                      │  │   ▼ 15% improvement │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Change Failure Rate  │  │ Mean Time to Recovery│        │
│  │                      │  │                      │        │
│  │   ████░░░░░░░░  8%   │  │   Average: 47 min   │        │
│  │   ▼ 3% vs last month │  │   P90: 2.1 hours    │        │
│  │                      │  │   ▲ 10% slower      │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  Performance Level: HIGH ████████████░░░░░░░░ → ELITE      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Strategies

### Getting Started

```
┌─────────────────────────────────────────────────────────────┐
│              DORA METRICS IMPLEMENTATION ROADMAP             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: Foundation (Weeks 1-4)                            │
│  ═══════════════════════════════                            │
│  □ Define what "deployment" means for your org              │
│  □ Define what "failure" means (requires remediation)       │
│  □ Identify data sources for each metric                    │
│  □ Set up basic tracking (even manual initially)            │
│                                                              │
│  PHASE 2: Automation (Weeks 5-8)                            │
│  ════════════════════════════════                           │
│  □ Integrate with CI/CD pipelines                           │
│  □ Connect to incident management                           │
│  □ Build automated dashboards                               │
│  □ Establish baseline measurements                          │
│                                                              │
│  PHASE 3: Optimization (Ongoing)                            │
│  ═══════════════════════════════                            │
│  □ Set improvement targets                                  │
│  □ Identify bottlenecks and constraints                     │
│  □ Implement improvements                                   │
│  □ Track progress and iterate                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Questions to Answer

| Metric | Key Questions |
|--------|---------------|
| **Deployment Frequency** | What counts as production? Include feature flags? Blue-green switches? |
| **Lead Time** | From first commit or PR merge? Include weekends/holidays? |
| **Change Failure Rate** | What severity counts? Only rollbacks or also hotfixes? |
| **MTTR** | From alert or from actual failure? To full resolution or service restoration? |

---

## Common Pitfalls

### Anti-Patterns to Avoid

```
┌─────────────────────────────────────────────────────────────┐
│                     COMMON PITFALLS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ❌ GAMING THE METRICS                                      │
│     • Splitting deploys artificially to increase frequency  │
│     • Not counting failures to improve CFR                  │
│     • Closing incidents prematurely to improve MTTR         │
│                                                              │
│  ❌ USING METRICS PUNITIVELY                                │
│     • Blaming teams for poor metrics                        │
│     • Creating competition between teams                    │
│     • Tying metrics directly to performance reviews         │
│                                                              │
│  ❌ IGNORING CONTEXT                                        │
│     • Comparing teams with different constraints            │
│     • Not considering regulatory requirements               │
│     • Ignoring team size and maturity differences          │
│                                                              │
│  ❌ FOCUSING ON SINGLE METRICS                              │
│     • Optimizing deployment frequency at cost of quality    │
│     • Reducing lead time by skipping testing                │
│     • All four metrics must improve together                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### What NOT to Do

| Don't | Do Instead |
|-------|------------|
| Compare teams across different contexts | Track team improvement over time |
| Use metrics as punishment | Use metrics to identify improvement opportunities |
| Optimize one metric at expense of others | Balance all four metrics |
| Manually track metrics long-term | Automate data collection |
| Set arbitrary targets | Base targets on current baseline |

---

## Tools and Platforms

### Specialized DORA Tools

| Tool | Description | Best For |
|------|-------------|----------|
| **Google Cloud DORA** | Official DORA quick check | Assessment and benchmarking |
| **LinearB** | Developer workflow analytics | Comprehensive metrics |
| **Sleuth** | DORA metrics automation | CI/CD integration |
| **Swarmia** | Engineering effectiveness | Team-level insights |
| **Faros AI** | Engineering intelligence | Enterprise scale |
| **Jellyfish** | Engineering management | Portfolio view |

### DIY Implementation

| Component | Tools |
|-----------|-------|
| **Data Collection** | Prometheus, OpenTelemetry, custom scripts |
| **Storage** | TimescaleDB, InfluxDB, BigQuery |
| **Visualization** | Grafana, Looker, custom dashboards |
| **CI/CD Integration** | GitHub Actions, GitLab CI, Jenkins plugins |

### GitHub Actions Example

```yaml
# .github/workflows/dora-metrics.yml
name: Track DORA Metrics

on:
  deployment:
    types: [created]
  workflow_run:
    workflows: ["Deploy to Production"]
    types: [completed]

jobs:
  track-deployment:
    runs-on: ubuntu-latest
    steps:
      - name: Record Deployment
        run: |
          curl -X POST ${{ secrets.METRICS_ENDPOINT }} \
            -H "Content-Type: application/json" \
            -d '{
              "event": "deployment",
              "timestamp": "${{ github.event.deployment.created_at }}",
              "commit_sha": "${{ github.sha }}",
              "status": "${{ github.event.deployment.status }}",
              "service": "${{ github.repository }}"
            }'
```

---

## Improving Your DORA Metrics

### Deployment Frequency Improvements

| Improvement | Impact |
|-------------|--------|
| Implement trunk-based development | Reduces merge conflicts, enables continuous deployment |
| Automate testing | Removes manual gates |
| Use feature flags | Decouple deployment from release |
| Reduce batch size | Smaller changes are easier to deploy |

### Lead Time Improvements

| Improvement | Impact |
|-------------|--------|
| Automate CI/CD pipeline | Eliminates manual steps |
| Parallelize tests | Reduces pipeline duration |
| Implement fast feedback | Catch issues earlier |
| Reduce code review wait time | Use async reviews, pair programming |

### Change Failure Rate Improvements

| Improvement | Impact |
|-------------|--------|
| Increase test coverage | Catch bugs before production |
| Implement canary deployments | Limit blast radius |
| Use progressive delivery | Gradual rollout reduces risk |
| Improve code review quality | Catch issues before merge |

### MTTR Improvements

| Improvement | Impact |
|-------------|--------|
| Improve observability | Faster detection and diagnosis |
| Implement runbooks | Standardized response procedures |
| Practice incident response | Team readiness |
| Enable fast rollbacks | Quick mitigation option |

---

## DORA Metrics and Business Outcomes

### Research Findings

The DORA research has consistently shown correlations between software delivery performance and:

```
┌─────────────────────────────────────────────────────────────┐
│             DORA METRICS → BUSINESS OUTCOMES                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ORGANIZATIONAL PERFORMANCE                                  │
│  ══════════════════════════                                 │
│  • Profitability                                            │
│  • Market share                                             │
│  • Productivity                                             │
│                                                              │
│  COMMERCIAL PERFORMANCE                                      │
│  ══════════════════════                                     │
│  • Number of customers                                      │
│  • Operating efficiency                                     │
│  • Customer satisfaction                                    │
│                                                              │
│  NON-COMMERCIAL PERFORMANCE                                  │
│  ═══════════════════════════                                │
│  • Mission achievement                                      │
│  • Quality of products/services                             │
│  • Stakeholder satisfaction                                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Elite performers are 2x more likely to meet or     │    │
│  │  exceed organizational performance goals            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Connecting Technical and Business Metrics

| DORA Metric | Business Impact |
|-------------|-----------------|
| **High Deployment Frequency** | Faster time-to-market, competitive advantage |
| **Low Lead Time** | Quicker response to customer needs |
| **Low Change Failure Rate** | Higher quality, better customer experience |
| **Low MTTR** | Higher availability, better SLA compliance |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                  DORA METRICS QUICK REFERENCE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DEPLOYMENT FREQUENCY        LEAD TIME FOR CHANGES          │
│  ════════════════════        ══════════════════════         │
│  How often to production?    Commit → Production time       │
│  Elite: Multiple/day         Elite: < 1 hour                │
│  High: Daily-Weekly          High: < 1 week                 │
│  Medium: Weekly-Monthly      Medium: < 1 month              │
│  Low: Monthly-Semi-annually  Low: 1-6 months                │
│                                                              │
│  CHANGE FAILURE RATE         MEAN TIME TO RECOVERY          │
│  ═══════════════════         ═════════════════════          │
│  % deploys causing failure   Time to restore service        │
│  Elite: 0-15%                Elite: < 1 hour                │
│  High: 16-30%                High: < 1 day                  │
│  Medium: 16-30%              Medium: < 1 week               │
│  Low: 46-60%                 Low: > 6 months                │
│                                                              │
│  KEY PRINCIPLE: High performers excel at ALL four metrics   │
│  There is NO trade-off between speed and stability!         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [SLI/SLO/SLA](01-sli-slo-sla.md) - Service level metrics for reliability targets
- [Error Budget](02-error-budget.md) - Balancing reliability with velocity
- [MTTR/MTTF/MTBF](06-mttr-mttf-mtbf.md) - Detailed time-based reliability metrics
- [Well-Known Metrics Catalog](09-well-known-metrics-catalog.md) - Comprehensive metrics reference

---

## References

- [DORA State of DevOps Reports](https://dora.dev)
- [Accelerate: The Science of Lean Software and DevOps](https://itrevolution.com/book/accelerate/)
- [Google Cloud DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)

---

*Last Updated: December 2025*
