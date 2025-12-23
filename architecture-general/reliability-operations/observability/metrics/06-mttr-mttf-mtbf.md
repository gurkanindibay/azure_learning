# MTTR, MTTF, MTBF: Reliability Time Metrics

## Table of Contents

- [Overview](#overview)
- [The Four Key Metrics](#the-four-key-metrics)
  - [MTTD - Mean Time to Detect](#mttd---mean-time-to-detect)
  - [MTTR - Mean Time to Recover/Repair](#mttr---mean-time-to-recoverrepair)
  - [MTTF - Mean Time to Failure](#mttf---mean-time-to-failure)
  - [MTBF - Mean Time Between Failures](#mtbf---mean-time-between-failures)
- [Relationships and Formulas](#relationships-and-formulas)
- [Incident Timeline](#incident-timeline)
- [Measuring and Calculating](#measuring-and-calculating)
- [Industry Benchmarks](#industry-benchmarks)
- [Improving Each Metric](#improving-each-metric)
- [Tools and Implementation](#tools-and-implementation)
- [Common Pitfalls](#common-pitfalls)

---

## Overview

Reliability time metrics quantify how systems fail and recover. These metrics are essential for:

- **Measuring** operational reliability
- **Setting** improvement goals
- **Comparing** against industry standards
- **Planning** for incidents and capacity

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RELIABILITY TIME METRICS                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────┐                                                        │
│   │     MTTD       │  Mean Time to DETECT                                   │
│   │  "How quickly  │  Time from failure occurrence to detection             │
│   │   do we know?" │                                                        │
│   └────────────────┘                                                        │
│                                                                              │
│   ┌────────────────┐                                                        │
│   │     MTTR       │  Mean Time to RECOVER/REPAIR                           │
│   │  "How quickly  │  Time from detection to service restoration            │
│   │   do we fix?"  │                                                        │
│   └────────────────┘                                                        │
│                                                                              │
│   ┌────────────────┐                                                        │
│   │     MTTF       │  Mean Time to FAILURE                                  │
│   │  "How long     │  Average time a system operates before failing         │
│   │   until fail?" │  (For non-repairable items)                           │
│   └────────────────┘                                                        │
│                                                                              │
│   ┌────────────────┐                                                        │
│   │     MTBF       │  Mean Time BETWEEN Failures                            │
│   │  "How often    │  Average time between system failures                  │
│   │   does it fail?│  (For repairable systems)                             │
│   └────────────────┘                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Four Key Metrics

### MTTD - Mean Time to Detect

**Definition**: The average time between when a failure occurs and when it's detected by the team.

```
┌─────────────────────────────────────────────────────────────────┐
│                    MEAN TIME TO DETECT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Formula:                                                        │
│  ════════                                                        │
│                                                                  │
│         Sum of all detection times                               │
│  MTTD = ────────────────────────────                            │
│           Number of incidents                                    │
│                                                                  │
│                                                                  │
│  What it measures:                                               │
│  ═════════════════                                               │
│  • Monitoring effectiveness                                      │
│  • Alerting quality                                              │
│  • Observability maturity                                        │
│                                                                  │
│  Factors that increase MTTD:                                     │
│  ═══════════════════════════                                     │
│  • Missing or inadequate monitoring                              │
│  • Poor alert thresholds                                         │
│  • Alert fatigue (ignored alerts)                                │
│  • Gaps in coverage                                              │
│  • Silent failures                                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### MTTD Example Calculation

```
Incident 1: Failed at 10:00, detected at 10:05  → 5 minutes
Incident 2: Failed at 14:30, detected at 14:32  → 2 minutes
Incident 3: Failed at 09:15, detected at 09:45  → 30 minutes
Incident 4: Failed at 16:00, detected at 16:03  → 3 minutes

MTTD = (5 + 2 + 30 + 3) / 4 = 10 minutes

Note: Incident 3 significantly impacts the average!
Consider tracking median as well.
```

---

### MTTR - Mean Time to Recover/Repair

**Definition**: The average time to restore service after a failure is detected. This is the most commonly tracked reliability metric.

```
┌─────────────────────────────────────────────────────────────────┐
│                   MEAN TIME TO RECOVER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ⚠️ IMPORTANT: MTTR has multiple definitions!                   │
│                                                                  │
│  MTTR (Recovery):                                                │
│  ═══════════════                                                 │
│  Time from DETECTION to SERVICE RESTORED                         │
│  • Used in SRE/DevOps contexts                                  │
│  • Measures operational response                                 │
│                                                                  │
│  MTTR (Repair):                                                  │
│  ══════════════                                                  │
│  Time from DETECTION to ROOT CAUSE FIXED                         │
│  • Used in traditional ITSM                                     │
│  • Includes full remediation                                     │
│                                                                  │
│  MTTR (Resolve):                                                 │
│  ═══════════════                                                 │
│  Time from OCCURRENCE to FULL RESOLUTION                         │
│  • Includes detection time (MTTD + repair time)                 │
│  • Most comprehensive but often confused                         │
│                                                                  │
│  ⚠️ Always clarify which definition you're using!               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### MTTR Formula

```
         Sum of all recovery times
MTTR = ────────────────────────────
          Number of incidents

Where:
Recovery Time = Time service restored - Time incident detected
```

#### MTTR Breakdown

```
                    MTTR Components
════════════════════════════════════════════════════════════════

Detection        Triage           Repair          Validation
────────────────────────────────────────────────────────────────►

│◄───MTTD───►│◄──────────────── MTTR ─────────────────────────►│

│             │            │              │              │
▼             ▼            ▼              ▼              ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│ Failure │ │ Alert   │ │ Diagnose │ │ Fix      │ │ Verify  │
│ Occurs  │ │ Fires   │ │ & Plan   │ │ Applied  │ │ & Close │
└─────────┘ └─────────┘ └──────────┘ └──────────┘ └─────────┘

Typical time:  ~5 min     ~15 min       ~30 min       ~10 min
─────────────────────────────────────────────────────────────────
Total MTTR:                            ~60 minutes
```

#### MTTR vs. MTRS vs. MTTA

| Metric | Full Name | Measures | Start Point | End Point |
|--------|-----------|----------|-------------|-----------|
| **MTTA** | Mean Time to Acknowledge | Response initiation | Alert fired | Human acknowledged |
| **MTTR** | Mean Time to Recover | Service restoration | Detection | Service up |
| **MTRS** | Mean Time to Resolve | Full resolution | Detection | Root cause fixed |

---

### MTTF - Mean Time to Failure

**Definition**: The average time a non-repairable system operates before it fails. Used for components that are replaced rather than repaired.

```
┌─────────────────────────────────────────────────────────────────┐
│                   MEAN TIME TO FAILURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Formula:                                                        │
│  ════════                                                        │
│                                                                  │
│        Total operating time before failures                      │
│  MTTF = ────────────────────────────────────                    │
│             Number of failures                                   │
│                                                                  │
│                                                                  │
│  Key characteristic:                                             │
│  ═══════════════════                                             │
│  Used for NON-REPAIRABLE items                                   │
│  • Hard drives (replaced, not repaired)                          │
│  • Light bulbs                                                   │
│  • Disposable components                                         │
│                                                                  │
│  In software context:                                            │
│  ════════════════════                                            │
│  • Container instances (replaced, not repaired)                  │
│  • Serverless function executions                                │
│  • Ephemeral VMs in auto-scaling groups                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### MTTF Example

```
Scenario: Hard Drive Fleet Analysis

Drive 1: Operated for 25,000 hours before failure
Drive 2: Operated for 32,000 hours before failure
Drive 3: Operated for 28,000 hours before failure
Drive 4: Operated for 35,000 hours before failure
Drive 5: Still running (not counted yet)

MTTF = (25,000 + 32,000 + 28,000 + 35,000) / 4
MTTF = 120,000 / 4
MTTF = 30,000 hours

Interpretation: On average, expect each drive to last ~30,000 hours
```

---

### MTBF - Mean Time Between Failures

**Definition**: The average time between failures for a repairable system. Includes both operating time and repair time.

```
┌─────────────────────────────────────────────────────────────────┐
│                MEAN TIME BETWEEN FAILURES                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Formula:                                                        │
│  ════════                                                        │
│                                                                  │
│         Total operating time                                     │
│  MTBF = ─────────────────────                                   │
│         Number of failures                                       │
│                                                                  │
│  Alternative:                                                    │
│  ════════════                                                    │
│                                                                  │
│  MTBF = MTTF + MTTR                                             │
│                                                                  │
│                                                                  │
│  Key characteristic:                                             │
│  ═══════════════════                                             │
│  Used for REPAIRABLE systems                                     │
│  • Servers (repaired and returned to service)                    │
│  • Network equipment                                             │
│  • Software services                                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### MTBF Timeline Visualization

```
                         MTBF Illustrated
════════════════════════════════════════════════════════════════

TIME ──────────────────────────────────────────────────────────►

     │◄────────────── MTBF ──────────────►│◄────── MTBF ──────►│
     │                                     │                    │
     │◄────── MTTF ────────►│◄── MTTR ──►│◄─── MTTF ────►│◄MTR│
     │                      │             │               │     │
═════╪══════════════════════╪═════════════╪═══════════════╪═════╪══
     │                      │             │               │     │
     │    OPERATING         │   DOWN      │   OPERATING   │DOWN │
     │    (healthy)         │ (repairing) │   (healthy)   │     │
     │                      │             │               │     │
     ▼                      ▼             ▼               ▼     ▼
 ┌───────┐            ┌─────────┐   ┌───────┐       ┌─────────┐
 │ Start │            │ Failure │   │ Fixed │       │ Failure │
 │       │            │   #1    │   │  #1   │       │   #2    │
 └───────┘            └─────────┘   └───────┘       └─────────┘
```

#### MTBF Example

```
Service uptime tracking over 1 year:

Operating Time: 8,500 hours
Number of Failures: 5

MTBF = 8,500 / 5 = 1,700 hours

Interpretation: 
• On average, expect a failure every 1,700 hours (~71 days)
• Higher MTBF = more reliable
```

---

## Relationships and Formulas

### The Complete Picture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    METRIC RELATIONSHIPS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Incident Timeline:                                                         │
│   ═══════════════════                                                        │
│                                                                              │
│   Failure      Detected      Acknowledged     Fixed        Next Failure     │
│      │             │              │             │               │            │
│      ▼             ▼              ▼             ▼               ▼            │
│   ───┬─────────────┬──────────────┬─────────────┬───────────────┬───        │
│      │             │              │             │               │            │
│      │◄── MTTD ───►│              │             │               │            │
│      │             │◄── MTTA ────►│             │               │            │
│      │             │◄─────────── MTTR ─────────►│               │            │
│      │◄────────────────── MTRS ────────────────►│               │            │
│      │◄───────────────────────── MTBF ─────────────────────────►│            │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Key Formulas:                                                              │
│   ═════════════                                                              │
│                                                                              │
│   MTBF = MTTF + MTTR       (For repairable systems)                         │
│                                                                              │
│   MTRS = MTTD + MTTR       (Total resolution time)                          │
│                                                                              │
│                    MTBF                                                      │
│   Availability = ──────────                                                  │
│                  MTBF + MTTR                                                 │
│                                                                              │
│                      1                                                       │
│   Failure Rate = ────────                                                    │
│                    MTBF                                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Availability Calculation

```
                    MTBF
Availability = ────────────── × 100%
               MTBF + MTTR

Example:
MTBF = 720 hours (30 days)
MTTR = 1 hour

Availability = 720 / (720 + 1) = 720 / 721 = 99.86%

To achieve 99.9% availability:
If MTBF = 720 hours:
  0.999 = 720 / (720 + MTTR)
  MTTR = 720 / 0.999 - 720 = 0.72 hours = 43 minutes

Or if MTTR = 1 hour:
  0.999 = MTBF / (MTBF + 1)
  MTBF = 999 hours = 41.6 days
```

---

## Incident Timeline

### Complete Incident Flow

```
                        INCIDENT LIFECYCLE
════════════════════════════════════════════════════════════════════════════

Phase:      FAILURE    DETECTION    RESPONSE    DIAGNOSIS    REPAIR    VERIFY
            ────────────────────────────────────────────────────────────────►

            │          │            │           │            │         │
Time:    10:00      10:05       10:08        10:15       10:45      10:55
            │          │            │           │            │         │
            ▼          ▼            ▼           ▼            ▼         ▼
         ┌──────┐  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐  ┌──────┐
         │System│  │Alert │    │Team  │    │Root  │    │Fix   │  │Verify│
         │fails │  │fires │    │acks  │    │cause │    │deploy│  │& OK  │
         └──────┘  └──────┘    └──────┘    │found │    └──────┘  └──────┘
                                          └──────┘

Metrics:    │◄─MTTD──►│◄─MTTA─►│
            │         │◄──────────── MTTR ─────────────────────►│
            │◄─────────────────── MTRS ────────────────────────►│


Example Values:
─────────────────────────────────────────────────────────────────
MTTD = 5 minutes    (10:05 - 10:00)
MTTA = 3 minutes    (10:08 - 10:05)
MTTR = 50 minutes   (10:55 - 10:05)
MTRS = 55 minutes   (10:55 - 10:00)
```

### Tracking Spreadsheet Example

| Incident | Occurred | Detected | Acknowledged | Resolved | MTTD | MTTA | MTTR | MTRS |
|----------|----------|----------|--------------|----------|------|------|------|------|
| INC-001 | 10:00 | 10:05 | 10:08 | 10:55 | 5m | 3m | 50m | 55m |
| INC-002 | 14:30 | 14:32 | 14:35 | 15:10 | 2m | 3m | 38m | 40m |
| INC-003 | 09:00 | 09:30 | 09:32 | 11:00 | 30m | 2m | 90m | 120m |
| **Average** | | | | | **12.3m** | **2.7m** | **59.3m** | **71.7m** |

---

## Measuring and Calculating

### Data Collection Sources

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCES FOR METRICS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  MTTD Data:                                                      │
│  ══════════                                                      │
│  • Monitoring system timestamps                                  │
│  • Alert firing times                                            │
│  • User-reported incident times                                  │
│  • Log analysis (first error timestamp)                          │
│                                                                  │
│  MTTR Data:                                                      │
│  ══════════                                                      │
│  • Incident management system                                    │
│  • PagerDuty, Opsgenie, VictorOps                               │
│  • Jira Service Management                                       │
│  • Custom ticketing systems                                      │
│                                                                  │
│  MTTF/MTBF Data:                                                 │
│  ═══════════════                                                 │
│  • Uptime monitoring                                             │
│  • Hardware telemetry                                            │
│  • Synthetic monitoring                                          │
│  • Service health dashboards                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Prometheus/Grafana Calculation

```yaml
# Recording rules for reliability metrics

groups:
  - name: reliability_metrics
    rules:
      # Track incident duration
      - record: incident:duration:seconds
        expr: |
          incident_resolved_timestamp_seconds - incident_detected_timestamp_seconds
          
      # MTTR over 30 days
      - record: mttr:30d:seconds
        expr: |
          avg(incident:duration:seconds{resolved="true"} 
              and timestamp > time() - 30*24*60*60)
              
      # MTTD requires correlating failure start with detection
      - record: mttd:30d:seconds
        expr: |
          avg(incident_detected_timestamp_seconds - incident_started_timestamp_seconds)
```

---

## Industry Benchmarks

### MTTR Benchmarks by Maturity

```
                    MTTR BENCHMARKS
════════════════════════════════════════════════════════════════

Maturity Level          │  MTTR Range      │  Characteristics
────────────────────────┼──────────────────┼─────────────────────
                        │                  │
Elite (Top 5%)          │  < 1 hour        │  • Automated detection
                        │                  │  • Automated remediation
                        │                  │  • Chaos engineering
                        │                  │
High Performers         │  1-4 hours       │  • Good observability
(Top 25%)               │                  │  • Runbooks in place
                        │                  │  • Experienced on-call
                        │                  │
Medium Performers       │  4-24 hours      │  • Basic monitoring
(Middle 50%)            │                  │  • Manual processes
                        │                  │  • Knowledge gaps
                        │                  │
Low Performers          │  > 24 hours      │  • Reactive only
(Bottom 25%)            │                  │  • Poor documentation
                        │                  │  • Siloed teams
```

### DORA Metrics (State of DevOps)

| Metric | Elite | High | Medium | Low |
|--------|-------|------|--------|-----|
| **MTTR** | < 1 hour | < 1 day | 1 day - 1 week | > 1 week |
| **Deploy Frequency** | Multiple/day | Weekly-monthly | Monthly-6 months | > 6 months |
| **Lead Time** | < 1 hour | 1 day - 1 week | 1-6 months | > 6 months |
| **Change Fail Rate** | 0-15% | 16-30% | 31-45% | > 45% |

### MTBF by Service Tier

| Tier | Target MTBF | Target MTTR | Availability |
|------|-------------|-------------|--------------|
| Critical (Tier 1) | > 2,160 hours (90 days) | < 15 min | 99.99% |
| Important (Tier 2) | > 720 hours (30 days) | < 1 hour | 99.9% |
| Standard (Tier 3) | > 168 hours (7 days) | < 4 hours | 99.5% |
| Non-critical (Tier 4) | > 24 hours | < 24 hours | 99% |

---

## Improving Each Metric

### Reducing MTTD

```
┌─────────────────────────────────────────────────────────────────┐
│                 STRATEGIES TO REDUCE MTTD                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Improve Monitoring Coverage                                  │
│     ══════════════════════════                                   │
│     • Instrument all services with metrics                       │
│     • Add synthetic monitoring (probes)                          │
│     • Monitor business metrics, not just technical               │
│                                                                  │
│  2. Optimize Alerting                                            │
│     ═════════════════                                            │
│     • Tune thresholds to reduce noise                            │
│     • Use multi-signal alerts (reduce false positives)           │
│     • Implement anomaly detection                                │
│                                                                  │
│  3. Implement Real-User Monitoring (RUM)                         │
│     ═══════════════════════════════════                          │
│     • Detect issues users see before internal alerts             │
│     • Track client-side errors                                   │
│                                                                  │
│  4. Use Distributed Tracing                                      │
│     ══════════════════════                                       │
│     • Identify slow spans across services                        │
│     • Detect partial failures                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Reducing MTTR

```
┌─────────────────────────────────────────────────────────────────┐
│                 STRATEGIES TO REDUCE MTTR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Automate Common Remediations                                 │
│     ═══════════════════════════                                  │
│     • Auto-restart crashed services                              │
│     • Auto-scale on resource exhaustion                          │
│     • Self-healing infrastructure                                │
│                                                                  │
│  2. Create Runbooks                                              │
│     ═════════════════                                            │
│     • Step-by-step guides for known issues                       │
│     • Link runbooks to alerts                                    │
│     • Keep runbooks updated                                      │
│                                                                  │
│  3. Improve On-Call Practices                                    │
│     ═════════════════════════                                    │
│     • Clear escalation paths                                     │
│     • War room procedures                                        │
│     • Dedicated incident commanders                              │
│                                                                  │
│  4. Design for Quick Recovery                                    │
│     ════════════════════════                                     │
│     • Feature flags for quick rollback                           │
│     • Blue-green deployments                                     │
│     • Database migration rollback plans                          │
│                                                                  │
│  5. Practice Incident Response                                   │
│     ══════════════════════════                                   │
│     • Regular game days                                          │
│     • Chaos engineering                                          │
│     • Post-incident reviews                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Increasing MTBF

```
┌─────────────────────────────────────────────────────────────────┐
│                 STRATEGIES TO INCREASE MTBF                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Improve Code Quality                                         │
│     ═══════════════════                                          │
│     • Comprehensive testing                                      │
│     • Code reviews                                               │
│     • Static analysis                                            │
│                                                                  │
│  2. Build Resilient Architecture                                 │
│     ════════════════════════                                     │
│     • Redundancy and failover                                    │
│     • Circuit breakers                                           │
│     • Bulkheads and isolation                                    │
│     • Graceful degradation                                       │
│                                                                  │
│  3. Proactive Maintenance                                        │
│     ══════════════════════                                       │
│     • Regular patching                                           │
│     • Capacity planning                                          │
│     • Performance optimization                                   │
│                                                                  │
│  4. Learn from Failures                                          │
│     ═══════════════════                                          │
│     • Blameless post-mortems                                     │
│     • Track and fix recurring issues                             │
│     • Share learnings across teams                               │
│                                                                  │
│  5. Controlled Change Management                                 │
│     ═════════════════════════                                    │
│     • Smaller, more frequent deployments                         │
│     • Canary releases                                            │
│     • Change failure tracking                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tools and Implementation

### Incident Management Platforms

| Tool | Key Features | MTTR Support |
|------|--------------|--------------|
| **PagerDuty** | Alerting, escalation, analytics | Built-in MTTR reporting |
| **Opsgenie** | Alert management, on-call | MTTR dashboards |
| **VictorOps** | Incident management, collaboration | MTTR analytics |
| **ServiceNow** | ITSM, CMDB, automation | Comprehensive metrics |
| **Jira Service Management** | Ticketing, SLAs | Custom metric tracking |

### Building an MTTR Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RELIABILITY METRICS DASHBOARD                          [Last 30 Days ▼]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ MTTD            │  │ MTTR            │  │ MTBF            │             │
│  │                 │  │                 │  │                 │             │
│  │   8 min         │  │   45 min        │  │   312 hours     │             │
│  │   ▼ -12%        │  │   ▼ -8%         │  │   ▲ +15%        │             │
│  │   vs last month │  │   vs last month │  │   vs last month │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    MTTR TREND (6 Months)                               │ │
│  │  2h ─┤                                                                  │ │
│  │      │  ╭──╮                                                           │ │
│  │ 1.5h─┤ ╱    ╲                                                          │ │
│  │      │╱      ╲      ╭──╮                                               │ │
│  │  1h ─┤        ╲────╱    ╲────╮                                         │ │
│  │      │                        ╲───────────                             │ │
│  │ 30m ─┤                                    ╲────────  Target: 30m       │ │
│  │      └─────┬─────┬─────┬─────┬─────┬─────┬─────┬───                   │ │
│  │          Jul   Aug   Sep   Oct   Nov   Dec   Jan                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐ │
│  │  RECENT INCIDENTS               │  │  MTTR BY SERVICE                │ │
│  │  ────────────────────────────   │  │  ───────────────────────────    │ │
│  │  INC-234: API Timeout           │  │  Payment API:     52 min        │ │
│  │     MTTR: 35 min  ✅             │  │  User Service:    38 min        │ │
│  │                                 │  │  Auth Service:    67 min  ⚠️    │ │
│  │  INC-233: DB Connection Pool    │  │  Search API:      29 min        │ │
│  │     MTTR: 52 min  ✅             │  │  Notification:    45 min        │ │
│  │                                 │  │                                  │ │
│  │  INC-232: Memory Leak           │  │  [View Details →]               │ │
│  │     MTTR: 2h 15min  ⚠️          │  │                                  │ │
│  └─────────────────────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Common Pitfalls

### 1. Inconsistent Definitions

```
❌ Problem: Team A measures MTTR from alert to fix
            Team B measures MTTR from occurrence to fix

✅ Solution: Document and standardize definitions
   • Create a metrics glossary
   • Train all teams on definitions
   • Automate collection to ensure consistency
```

### 2. Gaming the Metrics

```
❌ Problem: Closing incidents as "resolved" before 
            actually fixed to improve MTTR

✅ Solution: 
   • Measure customer-reported issues separately
   • Track recurrence rate
   • Verify resolution before closing
```

### 3. Averaging Hides Problems

```
❌ Problem: Average MTTR = 30 min (looks good!)
            But 10% of incidents take 4+ hours

✅ Solution: 
   • Track percentiles (P50, P90, P99)
   • Set targets for each percentile
   • Investigate outliers
```

### 4. Not Accounting for Severity

```
❌ Problem: All incidents weighted equally
            Minor issue resolved in 5 min = 
            Major outage resolved in 5 min

✅ Solution: 
   • Segment metrics by severity
   • Weight by impact
   • Set different targets per severity
```

---

## Summary

| Metric | Definition | What It Tells You | How to Improve |
|--------|------------|-------------------|----------------|
| **MTTD** | Time to detect | Monitoring effectiveness | Better observability |
| **MTTR** | Time to recover | Response capability | Automation, runbooks |
| **MTTF** | Time to failure | Component reliability | Quality, testing |
| **MTBF** | Time between failures | System reliability | Resilient design |

### Key Takeaways

1. **Define metrics clearly** - Ensure team-wide understanding
2. **Automate collection** - Avoid manual tracking errors
3. **Track trends** - Point-in-time values are less useful
4. **Segment by severity** - Not all incidents are equal
5. **Focus on improvement** - Use metrics to drive action

---

## Related Documentation

- [SLI/SLO/SLA](01-sli-slo-sla.md) - Setting reliability targets
- [Error Budget](02-error-budget.md) - Balancing reliability and velocity
- [RPO/RTO](08-rpo-rto-overview.md) - Recovery objectives for disaster recovery
