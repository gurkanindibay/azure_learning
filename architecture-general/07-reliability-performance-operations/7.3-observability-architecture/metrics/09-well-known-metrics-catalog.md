---
type: Architecture Pattern
title: "Well-Known Metrics Catalog"
description: "This document catalogs **well-known, commonly used metrics** across different domains of software engineering, operations, and business. Each metric includes its category, typical usage, and applic..."
tags: [reliability-performance-operations]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Well-Known Metrics Catalog

## Table of Contents

- [Overview](#overview)
- [Metrics by Category](#metrics-by-category)
  - [Infrastructure Metrics](#infrastructure-metrics)
  - [Application Performance Metrics](#application-performance-metrics)
  - [Business Metrics](#business-metrics)
  - [Security Metrics](#security-metrics)
  - [DevOps Metrics](#devops-metrics)
  - [User Experience Metrics](#user-experience-metrics)
  - [Database Metrics](#database-metrics)
  - [Network Metrics](#network-metrics)
- [Metrics by Business Area](#metrics-by-business-area)
- [Metrics Selection Guide](#metrics-selection-guide)
- [Implementation Best Practices](#implementation-best-practices)

---

## Overview

This document catalogs **well-known, commonly used metrics** across different domains of software engineering, operations, and business. Each metric includes its category, typical usage, and applicable business areas.

```
┌─────────────────────────────────────────────────────────────────┐
│                    METRICS CATALOG STRUCTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 CATEGORY         🎯 USAGE FIELD        🏢 BUSINESS AREA     │
│  What type of        Where is it           Which teams or       │
│  metric is it?       typically used?       domains use it?      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Metrics by Category

### Infrastructure Metrics

Infrastructure metrics measure the health and performance of underlying systems.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **CPU Utilization** | Percentage of CPU capacity in use | Resource monitoring | Platform Engineering, SRE | Percentage (%) |
| **Memory Utilization** | Percentage of RAM in use | Resource monitoring | Platform Engineering, SRE | Percentage (%) |
| **Disk I/O** | Read/write operations per second | Storage performance | Platform Engineering | IOPS |
| **Disk Space Usage** | Percentage of disk capacity used | Capacity planning | Infrastructure, FinOps | Percentage (%) |
| **Network Throughput** | Data transferred per time unit | Network monitoring | Network Engineering | Mbps/Gbps |
| **Container CPU/Memory** | Resource usage per container | Container orchestration | DevOps, Platform Engineering | Various |
| **Pod Restart Count** | Number of Kubernetes pod restarts | Container health | Platform Engineering | Count |
| **Node Availability** | Percentage of time nodes are operational | Infrastructure reliability | SRE | Percentage (%) |

```
┌─────────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE METRICS PYRAMID                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌───────────┐                            │
│                    │ Application│                           │
│                    └─────┬─────┘                            │
│               ┌──────────┴──────────┐                       │
│               │    Containers/VMs    │                      │
│               └──────────┬──────────┘                       │
│          ┌───────────────┴───────────────┐                  │
│          │     Compute/Storage/Network    │                 │
│          └───────────────┬───────────────┘                  │
│     ┌────────────────────┴────────────────────┐             │
│     │          Physical Infrastructure         │            │
│     └──────────────────────────────────────────┘            │
│                                                              │
│  Monitor from bottom-up for infrastructure metrics          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Application Performance Metrics

Metrics that measure how well applications serve users.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Response Time** | Time to complete a request | API/Service monitoring | Development, SRE | Milliseconds |
| **Throughput (TPS/RPS)** | Transactions/Requests per second | Load testing, capacity | Performance Engineering | Count/sec |
| **Error Rate** | Percentage of failed requests | Reliability monitoring | SRE, Development | Percentage (%) |
| **Request Count** | Total number of requests | Traffic analysis | Product, Engineering | Count |
| **P50/P95/P99 Latency** | Percentile response times | Performance SLIs | SRE, Development | Milliseconds |
| **Concurrent Users** | Active users at a given time | Capacity planning | Product, Infrastructure | Count |
| **Queue Depth** | Messages waiting in queue | Async processing | Development, SRE | Count |
| **Cache Hit Ratio** | Percentage of requests served from cache | Performance optimization | Development | Percentage (%) |
| **Garbage Collection Time** | Time spent in GC | JVM/CLR performance | Development | Milliseconds |
| **Thread Pool Utilization** | Active threads vs. pool size | Application tuning | Development | Percentage (%) |

---

### Business Metrics

Metrics that directly relate to business outcomes and KPIs.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Conversion Rate** | Percentage completing desired action | E-commerce, Marketing | Product, Marketing | Percentage (%) |
| **Revenue Per Transaction** | Average revenue per completed transaction | Financial analysis | Finance, Product | Currency |
| **Cart Abandonment Rate** | Percentage of abandoned shopping carts | E-commerce | Product, Marketing | Percentage (%) |
| **Customer Acquisition Cost (CAC)** | Cost to acquire a new customer | Marketing ROI | Marketing, Finance | Currency |
| **Customer Lifetime Value (CLV)** | Predicted revenue from a customer | Business strategy | Product, Finance | Currency |
| **Daily/Monthly Active Users (DAU/MAU)** | Unique users in time period | User engagement | Product | Count |
| **Churn Rate** | Percentage of customers lost | Customer retention | Product, Customer Success | Percentage (%) |
| **Net Promoter Score (NPS)** | Customer loyalty indicator | Customer satisfaction | Customer Success | Score (-100 to 100) |
| **Average Order Value (AOV)** | Average transaction amount | E-commerce | Product, Finance | Currency |
| **Feature Adoption Rate** | Percentage using new features | Product success | Product | Percentage (%) |

```
┌─────────────────────────────────────────────────────────────┐
│               BUSINESS METRICS FUNNEL                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    Visitors  ──────────────────────────────────►  Traffic   │
│         │                                                    │
│         ▼                                                    │
│    Signups   ──────────────────────────────────►  CAC       │
│         │                                                    │
│         ▼                                                    │
│    Active Users ───────────────────────────────►  DAU/MAU   │
│         │                                                    │
│         ▼                                                    │
│    Conversions ────────────────────────────────►  CVR       │
│         │                                                    │
│         ▼                                                    │
│    Revenue  ───────────────────────────────────►  CLV/AOV   │
│         │                                                    │
│         ▼                                                    │
│    Retention ──────────────────────────────────►  Churn     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Security Metrics

Metrics for measuring security posture and incident response.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Mean Time to Detect (MTTD)** | Average time to detect threats | Security operations | Security, SOC | Time (hours/minutes) |
| **Mean Time to Respond (MTTR)** | Average time to respond to incidents | Incident response | Security, SOC | Time (hours/minutes) |
| **Failed Login Attempts** | Count of authentication failures | Access monitoring | Security | Count |
| **Vulnerability Count by Severity** | Open vulnerabilities by CVSS | Vulnerability management | Security, Development | Count |
| **Patch Compliance Rate** | Percentage of systems patched | Compliance | Security, IT Operations | Percentage (%) |
| **Security Incidents** | Number of security incidents | Security monitoring | Security, SOC | Count |
| **Phishing Click Rate** | Percentage clicking phishing tests | Security awareness | Security, HR | Percentage (%) |
| **Privileged Access Usage** | Admin/elevated access patterns | Access control | Security, Compliance | Count/Time |
| **Encryption Coverage** | Percentage of encrypted data | Data protection | Security, Compliance | Percentage (%) |
| **Firewall Rule Violations** | Blocked connection attempts | Network security | Security, Network | Count |

---

### DevOps Metrics

Metrics measuring software delivery and operational efficiency.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Deployment Frequency** | How often code is deployed | Delivery velocity | DevOps, Development | Deployments/day |
| **Lead Time for Changes** | Time from commit to production | Delivery efficiency | DevOps, Development | Time (hours/days) |
| **Change Failure Rate** | Percentage of failed deployments | Deployment quality | DevOps, SRE | Percentage (%) |
| **Mean Time to Recovery (MTTR)** | Time to restore service | Incident management | SRE, DevOps | Time (minutes/hours) |
| **Build Success Rate** | Percentage of successful builds | CI/CD health | DevOps, Development | Percentage (%) |
| **Test Coverage** | Percentage of code tested | Quality assurance | Development, QA | Percentage (%) |
| **Code Review Turnaround** | Time to review PRs | Development velocity | Development | Time (hours) |
| **Infrastructure as Code Coverage** | Percentage managed by IaC | Infrastructure maturity | DevOps, Platform | Percentage (%) |
| **Automated Test Pass Rate** | Percentage of passing tests | Quality assurance | QA, Development | Percentage (%) |
| **Environment Provisioning Time** | Time to create new environment | Platform efficiency | Platform Engineering | Time (minutes) |

```
┌─────────────────────────────────────────────────────────────┐
│                  DORA METRICS (DevOps Research)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  VELOCITY METRICS              STABILITY METRICS            │
│  ════════════════              ═════════════════            │
│                                                              │
│  📈 Deployment               📉 Change Failure              │
│     Frequency                   Rate                         │
│     How often?                  How reliable?                │
│                                                              │
│  ⏱️  Lead Time for           🔧 Mean Time to                │
│     Changes                     Recovery                     │
│     How fast?                   How quickly fixed?           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Elite Performers:                                   │    │
│  │  • Multiple deploys per day                         │    │
│  │  • Lead time < 1 hour                               │    │
│  │  • Change failure rate < 15%                        │    │
│  │  • MTTR < 1 hour                                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### User Experience Metrics

Metrics measuring how users perceive and interact with applications.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Apdex Score** | Application Performance Index | User satisfaction | SRE, Product | Score (0-1) |
| **Page Load Time** | Time to fully load a page | Frontend performance | Frontend, UX | Seconds |
| **First Contentful Paint (FCP)** | Time to first content render | Core Web Vitals | Frontend | Seconds |
| **Largest Contentful Paint (LCP)** | Time to largest content render | Core Web Vitals | Frontend | Seconds |
| **First Input Delay (FID)** | Time to first interaction response | Core Web Vitals | Frontend | Milliseconds |
| **Cumulative Layout Shift (CLS)** | Visual stability score | Core Web Vitals | Frontend | Score (0-1) |
| **Time to Interactive (TTI)** | Time until page is interactive | Frontend performance | Frontend, UX | Seconds |
| **Bounce Rate** | Percentage leaving after one page | User engagement | Product, Marketing | Percentage (%) |
| **Session Duration** | Average time spent per session | User engagement | Product | Time (minutes) |
| **Task Success Rate** | Percentage completing tasks | Usability | UX, Product | Percentage (%) |
| **Error Rate (Client-Side)** | JavaScript errors encountered | Frontend reliability | Frontend, Development | Count/Percentage |

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE WEB VITALS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │     LCP     │  │     FID     │  │     CLS     │         │
│  │  Loading    │  │ Interactivity│  │  Visual    │         │
│  │  Performance│  │             │  │  Stability  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Good:    ≤ 2.5s       ≤ 100ms        ≤ 0.1               │
│  Needs    2.5-4s       100-300ms      0.1-0.25             │
│  Poor:    > 4s         > 300ms        > 0.25               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Database Metrics

Metrics for monitoring database health and performance.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Query Response Time** | Time to execute queries | Database performance | DBA, Development | Milliseconds |
| **Queries Per Second (QPS)** | Query throughput | Database load | DBA | Count/sec |
| **Connection Pool Utilization** | Active vs. available connections | Connection management | DBA, Development | Percentage (%) |
| **Lock Wait Time** | Time spent waiting for locks | Contention analysis | DBA | Milliseconds |
| **Deadlock Count** | Number of deadlocks | Concurrency issues | DBA | Count |
| **Replication Lag** | Delay between primary and replica | High availability | DBA, SRE | Seconds |
| **Index Hit Ratio** | Percentage of queries using indexes | Query optimization | DBA | Percentage (%) |
| **Buffer Pool Hit Ratio** | Cache effectiveness | Memory optimization | DBA | Percentage (%) |
| **Transaction Rate** | Completed transactions per second | Database throughput | DBA | TPS |
| **Table Size Growth** | Rate of data growth | Capacity planning | DBA, FinOps | GB/month |
| **Slow Query Count** | Queries exceeding threshold | Performance tuning | DBA, Development | Count |

---

### Network Metrics

Metrics for monitoring network health and performance.

| Metric | Description | Usage Field | Business Area | Unit |
|--------|-------------|-------------|---------------|------|
| **Bandwidth Utilization** | Percentage of available bandwidth used | Capacity planning | Network Engineering | Percentage (%) |
| **Packet Loss** | Percentage of dropped packets | Network reliability | Network Engineering | Percentage (%) |
| **Latency (RTT)** | Round-trip time for packets | Network performance | Network Engineering | Milliseconds |
| **Jitter** | Variation in packet latency | Voice/Video quality | Network Engineering | Milliseconds |
| **DNS Resolution Time** | Time to resolve DNS queries | DNS performance | Network Engineering | Milliseconds |
| **TCP Retransmission Rate** | Percentage of retransmitted packets | Network quality | Network Engineering | Percentage (%) |
| **Connection Count** | Active network connections | Load analysis | Network Engineering | Count |
| **SSL/TLS Handshake Time** | Time to establish secure connection | Security performance | Security, Network | Milliseconds |
| **Load Balancer Health** | Healthy backend instances | Traffic distribution | SRE, Network | Count/Percentage |
| **CDN Cache Hit Ratio** | Percentage served from CDN cache | Content delivery | Frontend, Network | Percentage (%) |

---

## Metrics by Business Area

### E-Commerce

| Category | Key Metrics |
|----------|-------------|
| Business | Conversion Rate, Cart Abandonment, AOV, Revenue |
| Performance | Page Load Time, Checkout Latency, API Response Time |
| Infrastructure | Throughput during sales events, Auto-scaling triggers |
| User Experience | Apdex, Core Web Vitals, Session Duration |

### Financial Services

| Category | Key Metrics |
|----------|-------------|
| Business | Transaction Volume, Revenue, Fraud Rate |
| Security | Failed Logins, MTTD, Encryption Coverage |
| Compliance | Audit Trail Completeness, Patch Compliance |
| Performance | Transaction Latency, System Availability |

### SaaS Platforms

| Category | Key Metrics |
|----------|-------------|
| Business | MRR/ARR, Churn Rate, DAU/MAU, Feature Adoption |
| Performance | API Latency (P99), Uptime, Error Rate |
| DevOps | Deployment Frequency, Lead Time, MTTR |
| User Experience | Apdex, NPS, Task Success Rate |

### Healthcare

| Category | Key Metrics |
|----------|-------------|
| Compliance | HIPAA Audit Logs, Access Controls, Encryption |
| Availability | System Uptime, RPO/RTO for critical systems |
| Performance | Response Time for critical workflows |
| Security | Unauthorized Access Attempts, Data Breach Indicators |

### Gaming

| Category | Key Metrics |
|----------|-------------|
| User Experience | Latency (P99), Frame Time, Matchmaking Time |
| Business | DAU, Session Duration, In-App Purchase Rate |
| Infrastructure | Server Tick Rate, Concurrent Players, Region Latency |
| Performance | API Response Time, Asset Load Time |

### Media & Streaming

| Category | Key Metrics |
|----------|-------------|
| User Experience | Buffer Ratio, Start Time, Video Quality Score |
| Business | Watch Time, Subscriber Growth, Content Engagement |
| Infrastructure | CDN Performance, Origin Server Load |
| Performance | Bitrate, Rebuffering Events, Time to First Byte |

---

## Metrics Selection Guide

### Step 1: Identify Your Domain

```
┌─────────────────────────────────────────────────────────────┐
│                 METRICS SELECTION WORKFLOW                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│     ┌─────────────┐                                         │
│     │  What are   │                                         │
│     │  you        │                                         │
│     │  monitoring?│                                         │
│     └──────┬──────┘                                         │
│            │                                                 │
│     ┌──────┴──────────────────────────────────┐             │
│     │               │              │           │             │
│     ▼               ▼              ▼           ▼             │
│ ┌───────┐     ┌──────────┐   ┌─────────┐  ┌────────┐       │
│ │Infra  │     │Application│   │Business │  │ User   │       │
│ │       │     │           │   │         │  │        │       │
│ └───┬───┘     └─────┬─────┘   └────┬────┘  └───┬────┘       │
│     │               │              │           │             │
│     ▼               ▼              ▼           ▼             │
│  USE Method    Golden Signals   KPIs        Apdex          │
│  CPU/Memory    RED Method       Conversions  Core Web      │
│  Disk/Network  Latency/Errors   Revenue      Vitals        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 2: Match Metrics to Goals

| Goal | Recommended Metrics |
|------|---------------------|
| Improve reliability | SLI/SLO, Error Rate, MTTR, Availability |
| Optimize performance | P95/P99 Latency, Throughput, Cache Hit Ratio |
| Reduce costs | Resource Utilization, Efficiency ratios, Cost per transaction |
| Improve user experience | Apdex, Core Web Vitals, Conversion Rate |
| Accelerate delivery | DORA metrics, Lead Time, Deployment Frequency |
| Enhance security | MTTD, MTTR, Vulnerability Count, Compliance Rate |

### Step 3: Define Thresholds

| Metric Type | Approach |
|-------------|----------|
| Latency | Use percentiles (P50, P95, P99) not averages |
| Error Rate | Set based on SLO (e.g., 99.9% success = 0.1% error budget) |
| Utilization | Yellow at 70%, Red at 85% |
| Business | Baseline from historical data, trend analysis |

---

## Implementation Best Practices

### 1. Start with the Basics

```
┌─────────────────────────────────────────────────────────────┐
│              METRICS IMPLEMENTATION STAGES                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  STAGE 1: Foundation                                        │
│  ═══════════════════                                        │
│  • Infrastructure metrics (CPU, Memory, Disk)               │
│  • Basic application metrics (Errors, Latency)              │
│  • Availability monitoring                                   │
│                                                              │
│  STAGE 2: Service Level                                     │
│  ══════════════════════                                     │
│  • Define SLIs and SLOs                                     │
│  • Implement Golden Signals / RED Method                    │
│  • Error budgets                                            │
│                                                              │
│  STAGE 3: Business Alignment                                │
│  ═══════════════════════════                                │
│  • Business KPIs linked to technical metrics                │
│  • User experience metrics (Apdex, Core Web Vitals)         │
│  • Cost and efficiency metrics                              │
│                                                              │
│  STAGE 4: Advanced                                          │
│  ═════════════════                                          │
│  • Predictive metrics and anomaly detection                 │
│  • Custom business-specific metrics                         │
│  • Correlation and causation analysis                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Naming Conventions

Follow a consistent naming pattern:

```
<namespace>_<metric_name>_<unit>

Examples:
- http_request_duration_seconds
- database_connections_active_count
- cache_hit_ratio_percent
- orders_total_count
```

### 3. Labeling Strategy

Use labels/dimensions wisely:

| Label | Purpose | Example Values |
|-------|---------|----------------|
| `service` | Service identification | `api-gateway`, `payment-service` |
| `environment` | Deployment environment | `prod`, `staging`, `dev` |
| `region` | Geographic location | `us-east-1`, `eu-west-1` |
| `status_code` | HTTP response code | `200`, `500`, `404` |
| `method` | HTTP method | `GET`, `POST`, `PUT` |

### 4. Avoid Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Too many metrics | Focus on actionable metrics tied to SLOs |
| Averages hide problems | Use percentiles (P95, P99) |
| Alert fatigue | Implement proper thresholds and aggregation |
| Missing context | Add proper labels and documentation |
| Siloed metrics | Correlate business and technical metrics |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│              METRICS QUICK REFERENCE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  INFRASTRUCTURE         APPLICATION         BUSINESS         │
│  ───────────────        ───────────         ────────         │
│  • CPU %                • Response Time     • Conversion %   │
│  • Memory %             • Error Rate        • Revenue        │
│  • Disk IOPS            • Throughput        • DAU/MAU        │
│  • Network Mbps         • P99 Latency       • Churn %        │
│                                                              │
│  SECURITY               DEVOPS              USER EXPERIENCE  │
│  ────────               ──────              ───────────────  │
│  • MTTD/MTTR            • Deploy Freq       • Apdex          │
│  • Failed Logins        • Lead Time         • LCP/FID/CLS    │
│  • Vuln Count           • Change Fail %     • Bounce Rate    │
│  • Patch %              • MTTR              • Session Time   │
│                                                              │
│  DATABASE               NETWORK                              │
│  ────────               ───────                              │
│  • Query Time           • Packet Loss                        │
│  • QPS                  • Latency (RTT)                      │
│  • Connections          • Bandwidth %                        │
│  • Replication Lag      • DNS Time                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [SLI/SLO/SLA](01-sli-slo-sla.md) - Service level metrics foundation
- [Golden Signals](03-golden-signals.md) - The four essential signals
- [RED Method](04-red-method.md) - Request-driven service metrics
- [USE Method](05-use-method.md) - Resource-focused metrics
- [Apdex Score](07-apdex-score.md) - User satisfaction scoring

---

*Last Updated: December 2025*
