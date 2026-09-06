---
type: Reference
title: "Observability"
description: "**Observability** — the ability to understand a system's internal state from its external outputs: logs, metrics, and traces."
generated: { by: process:okf-migrate, at: 2026-07-04T00:00:00Z }
---

# Observability

> **Domain**: Monitoring, metrics, logging, distributed tracing, SLOs/SLIs, error budgets, incident analysis, and real user monitoring.
> **Parent**: [Reference Dictionary](index.md)

## Contents

| Term | Anchor |
|:---|:---|
| Observability | [`#observability`](#observability) |
| OpenTelemetry | [`#opentelemetry`](#opentelemetry) |
| Golden Signals | [`#golden-signals`](#golden-signals) |
| Latency | [`#latency`](#latency) |
| Error Budget | [`#error-budget`](#error-budget) |
| Blameless Postmortem | [`#blameless-postmortem`](#blameless-postmortem) |
| Real User Monitoring (RUM) | [`#real-user-monitoring-rum`](#real-user-monitoring-rum) |
| Configuration Propagation | [`#configuration-propagation`](#configuration-propagation) |
| Centralized Logging | [`#centralized-logging`](#centralized-logging) |
| Distributed Tracing | [`#distributed-tracing`](#distributed-tracing) |
| Abuse-Block Counts | [`#abuse-block-counts`](#abuse-block-counts) |
| Time-Series Database (TSDB) | [`#time-series-database-tsdb`](#time-series-database-tsdb) |
| Push vs Pull Metrics Collection | [`#push-vs-pull-metrics-collection`](#push-vs-pull-metrics-collection) |
| Gorilla Compression | [`#gorilla-compression`](#gorilla-compression) |
| Downsampling and Rollup | [`#downsampling-and-rollup`](#downsampling-and-rollup) |
| FlameGraph | [`#flamegraph`](#flamegraph) |

---

## Observability

The ability to **understand a system's internal state from its external outputs** — logs, metrics, and traces. Unlike monitoring (which tracks known failure modes), observability enables diagnosing unknown failure modes by letting operators ask arbitrary questions about system behavior without deploying new code.

### Key Characteristics
- **Three pillars**: logs (events), metrics (aggregates), traces (request journeys)
- **Independence**: the observability stack must not depend on the infrastructure it monitors (see [Roblox 2021 outage](resilience.md#correlated-failure-domain))
- **Cardinality**: high-cardinality data (user IDs, request IDs) is essential for debugging, not just aggregate metrics

### When to Use
- Every production system — especially distributed systems where failures are emergent
- Before an incident: structured logs, distributed tracing, and dashboards for golden signals

### When NOT to Use
- As a substitute for testing — observability helps diagnose bugs but doesn't prevent them
- Without a retention policy — storing everything forever is expensive and rarely needed

### Also see
- [Golden Signals](#golden-signals) · [OpenTelemetry](#opentelemetry) · [Blameless Postmortem](#blameless-postmortem)

---

## OpenTelemetry

An **open observability standard and toolchain** for collecting distributed traces, metrics and logs. It provides vendor-neutral APIs, SDKs and the OpenTelemetry Collector for telemetry pipelines.

### Key Characteristics
- **Vendor-neutral**: single instrumentation emits data to many backends (Jaeger, Prometheus, cloud vendors)
- **Three pillars**: traces, metrics and logs under one semantic convention
- **Auto and manual instrumentation**: libraries, agents and explicit code annotations

### When to Use
- Microservices and serverless architectures needing distributed tracing
- Organizations wanting to avoid vendor lock-in for observability tools

### When NOT to Use
- As a replacement for thoughtful SLI/SLO design — telemetry without intent creates noise
- When the operational overhead of collectors and agents is not justified

**Also see**: [Golden Signals](#golden-signals), [Distributed Tracing](azure-services.md#distributed-tracing)

---

## Golden Signals

The four key metrics that provide a **high-level view of system health** in production: latency, traffic, errors and saturation. Popularized by Google’s SRE book.

| Signal | Question it answers |
|:---|:---|
| **Latency** | How long is it taking? |
| **Traffic** | How much demand is hitting the system? |
| **Errors** | How many requests are failing? |
| **Saturation** | How close to full capacity is the system? |

### When to Use
- Defining SLIs and dashboards for any user-facing service
- Incident triage and capacity planning

### When NOT to Use
- As the only metrics — business metrics, cost metrics and custom SLIs are also needed
- Without setting explicit SLO thresholds and alerting policies

**Also see**: [Error Budget](#error-budget), [OpenTelemetry](#opentelemetry)

---

## Latency

The **time delay between initiating a request and receiving a response**. In distributed systems, latency is always present — whether a network partition exists or not — and is one of the four Golden Signals. It is distinct from throughput: a system can have high throughput and high latency, or low throughput and low latency.

### Key Characteristics
- **Measured in percentiles**: p50 (median), p95, p99 are standard; averages hide tail-latency problems
- **Sources**: network round-trip time, serialization/deserialization, disk I/O, lock contention, garbage collection pauses, queue wait time
- **PACELC context**: when no network partition exists (the "E" — Else), the tradeoff is between Latency and Consistency, not Availability and Consistency

### When to Use
- Defining SLIs and SLOs for any user-facing service (latency is a Golden Signal)
- Capacity planning: understanding how latency scales with load
- Comparing synchronous vs. asynchronous replication strategies in distributed databases

### When NOT to Use
- As a standalone metric without throughput context — 5ms latency at 10 RPS is very different from 5ms at 10K RPS
- Confusing latency with response time (response time = latency + processing time)

### Also see
- [Golden Signals](#golden-signals) · [PACELC Theorem](data-concurrency.md#pacelc-theorem) · [Synchronous Replication](data-architecture.md#synchronous-replication)

---

## Error Budget

The amount of **acceptable unreliability** over a period, derived from an SLO. It frames trade-offs between velocity and stability: as long as budget remains, teams can launch freely; when it is exhausted, launches pause until reliability improves.

### Key Characteristics
- **1 - SLO = budget**: a 99.9% SLO leaves a 0.1% error budget
- **Product-level contract**: aligns engineering and product on risk tolerance
- **Policy-driven**: defines when launches are blocked and how to prioritize reliability work

### When to Use
- Services with explicit reliability targets and frequent releases
- Organizations where product wants speed and engineering wants stability guardrails

### When NOT to Use
- For systems without meaningful SLOs or measurable availability
- As a rigid blocker without executive buy-in and a path to restore budget

**Also see**: [Golden Signals](#golden-signals), [Blameless Postmortem](#blameless-postmortem)

---

## Blameless Postmortem

A retrospective practice focused on **understanding systemic causes and improving processes** rather than assigning individual blame. It is foundational to a healthy reliability culture.

### Key Characteristics
- **Psychological safety**: participants can describe mistakes without fear of punishment
- **Actionable outputs**: concrete remediation items with owners and timelines
- **Shared learning**: findings are published broadly so other teams can prevent similar incidents

### When to Use
- After every significant incident or near-miss
- When introducing chaos engineering or major architecture changes

### When NOT to Use
- As a checkbox exercise without follow-through on action items
- When leadership uses it to indirectly assign blame

**Also see**: [Error Budget](#error-budget), [Chaos Engineering](resilience.md#chaos-engineering)

---

## Real User Monitoring (RUM)

An **observability technique that captures performance and interaction data from actual user sessions** in production — as opposed to synthetic monitoring which uses scripted probes. RUM collects metrics such as page load time, first contentful paint, and user-journey completion rates from every real browser or client session.

### Key Characteristics
- Data is collected passively from real users, capturing genuine geographic and device diversity
- Surfaces user-experience degradation that synthetic tests miss (e.g., third-party script slowdowns)
- Raises data privacy considerations: session data may contain PII and requires consent and anonymization
- Common tools: Azure Application Insights (browser SDK), Datadog RUM, New Relic Browser, Google CrUX

### When to Use
- User-facing web or mobile applications where perceived performance directly affects conversion or retention
- When you need to understand how real-world network conditions, device types, and geographies affect experience
- Complementing synthetic monitoring to distinguish real degradation from probe anomalies

### When NOT to Use
- Pure API backends with no browser clients — server-side APM and distributed tracing are more appropriate
- When privacy regulations or user consent cannot be obtained for session data collection

### Also see
- [Observability](#observability) · [Golden Signals](#golden-signals) · [OpenTelemetry](#opentelemetry)

---

## Configuration Propagation

The process by which a **configuration change in one location spreads across a distributed system**. Configuration propagation is one of the most underestimated risks in distributed systems: a single change in one database or config store can reach every machine in a global network within minutes, with no canary or validation step. The Cloudflare 2025 outage is a canonical example — a routine permissions change that doubled a config file size propagated globally and caused every edge machine to panic.

### Key Characteristics
- **Speed**: propagation is typically near-instantaneous, far faster than code deployments
- **Blast radius**: a single invalid config can affect every node simultaneously
- **Implicit trust**: internally-generated configs often bypass the validation applied to user input

### When to Use
- Designing config distribution pipelines — always include canary validation, size/invariant checks, and automatic rollback
- Auditing deployment safety — treat internally-generated config files as untrusted input

### When NOT to Use
- Without a rollback mechanism — the ability to revert a bad config within seconds is non-negotiable
- Without monitoring the propagation itself — alert on unexpected config size changes or propagation delays

### Also see
- [Blast Radius](resilience.md#blast-radius) · [Canary Deployment](deployment-patterns.md#canary-deployment) · [Feature Flag](deployment-patterns.md#feature-flag) · [Progressive Delivery](deployment-patterns.md#progressive-delivery)

---

## Centralized Logging

A logging arrangement that collects structured application and infrastructure logs in a shared searchable system so operators can investigate behavior across service boundaries.

### Key Characteristics
- Uses consistent fields such as timestamp, service, severity, request ID, and trace ID
- Aggregates logs without requiring every operator to access every service instance
- Requires retention, access control, sampling, and protection against sensitive-data leakage

### When to Use
- Distributed systems where a request crosses multiple processes or hosts
- Incident investigation and correlation of failures across services

### When NOT to Use
- As a substitute for metrics and traces
- Without structured fields, retention limits, and a cost budget

### Also see
- [Observability](#observability) · [Distributed Tracing](#distributed-tracing) · [OpenTelemetry](#opentelemetry)

---

## Distributed Tracing

An observability technique that records the path and timing of one logical request across multiple services, using propagated trace and span context.

### Key Characteristics
- A trace groups spans from each participating service
- Context propagation connects downstream work to the originating request
- Sampling and high-cardinality storage require deliberate cost and retention policies

### When to Use
- Debugging latency, errors, and dependency behavior in distributed request paths
- Validating asynchronous workflow handoffs and identifying bottleneck services

### When NOT to Use
- As the only telemetry signal; traces do not replace service-level metrics or structured logs
- Without consistent propagation and instrumentation across service boundaries

### Also see
- [Observability](#observability) · [OpenTelemetry](#opentelemetry) · [Centralized Logging](#centralized-logging)

---

## Abuse-Block Counts

A metric that tracks how many requests were rejected because they were classified as abusive by rate-limiting, fraud-detection, or content-policy checks. It is a security-oriented operational signal used to detect attacks, tune protection thresholds, and verify that abuse controls are active.

### Key Characteristics
- Counts **blocked** requests, not merely throttled or rate-limited ones
- Usually emitted by gateways, WAFs, application-level guards, or anti-abuse services
- Typically segmented by rule, client, endpoint, or region
- Rising counts can indicate an attack, a policy mismatch, or overly aggressive protection

### When to Use
- Operational dashboards alongside [Golden Signals](#golden-signals)
- Alerting on spikes or sustained increases in blocked traffic
- Tuning and capacity planning for rate-limit and abuse-prevention rules

### When NOT to Use
- As a standalone health metric without context about legitimate traffic
- To infer the number of distinct attackers — one actor may trigger many blocks
- To replace detailed abuse investigation or request sampling

### Also see
- [Rate Limiting](api-design.md#rate-limiting) · [Golden Signals](#golden-signals) · [Load Shedding](resilience.md#load-shedding)

---

## Time-Series Database (TSDB)

A **database engine purpose-built to store, index, and query timestamped telemetry, metrics, and event series** (e.g., InfluxDB, Prometheus, TimescaleDB, Amazon Timestream). TSDBs are optimized for append-only sequential writes ordered by time, time-range scanning, and aggressive compression.

### Key Characteristics
- **Append-only ingest model**: Writes are heavily biased toward appending the latest timestamped samples; historical overwrites/updates are rare
- **Specialized columnar time compression**: Employs delta-of-deltas and Gorilla XOR encoding to compress 64-bit timestamps and float values down to 1–2 bytes per sample
- **Automated data lifecycle**: Native retention policies automatically age out raw high-frequency data into downsampled rollup tiers and drop expired partitions
- **Time-bucket aggregation primitives**: Optimized query engines supporting windowed aggregations (`SUM`, `AVG`, `PERCENTILE`, `RATE`) grouped by time buckets

### When to Use
- Infrastructure and application metrics monitoring (CPU, memory, QPS, latency histograms)
- IoT sensor telemetry and industrial SCADA logging
- Real-time algorithmic trading tick data and price charting

### When NOT to Use
- Complex relational business entities requiring ACID transactions and foreign key joins across normalized tables
- Point-in-time document storage with frequent random updates to nested attributes

### Also see
- [Push vs Pull Metrics Collection](#push-vs-pull-metrics-collection) · [Gorilla Compression](#gorilla-compression) · [Downsampling and Rollup](#downsampling-and-rollup)

---

## Push vs Pull Metrics Collection

The **fundamental architectural dichotomy in telemetry collection systems** deciding whether target applications actively send metrics to a collector (Push model) or a centralized collector periodically polls endpoints on target applications (Pull model).

### Key Characteristics
- **Pull Model (e.g., Prometheus, Datadog Agent)**:
  - Collector periodically scrapes HTTP `/metrics` endpoints
  - Built-in liveness detection (if scrape fails, service is down)
  - Prevents monitoring systems from being overwhelmed by flood storms (collector dictates polling frequency)
  - Requires service discovery (Consul, Kubernetes API) to locate ephemeral instances
- **Push Model (e.g., StatsD, AWS CloudWatch, OpenTelemetry Collector push)**:
  - Applications emit metrics over UDP/HTTP directly to ingestion gateways
  - Ideal for ephemeral short-lived serverless functions (AWS Lambda) and batch jobs that terminate before a scraper can poll
  - Requires load balancers and queue buffers in front of the ingestion pipeline to handle traffic spikes

### When to Use
- **Pull**: Long-running microservices, Kubernetes clusters, and infrastructure nodes with stable endpoints
- **Push**: Serverless workloads (Lambda), edge/mobile clients, and short batch jobs

### When NOT to Use
- Pulling from client mobile apps behind NAT/firewalls (impossible without outbound push)
- Pushing unbuffered telemetry from millions of nodes directly to backend databases without an ingestion broker

### Also see
- [Time-Series Database (TSDB)](#time-series-database-tsdb) · [OpenTelemetry](#opentelemetry) · [Golden Signals](#golden-signals)

---

## Gorilla Compression

A **lossless time-series compression algorithm** developed by Facebook (SIGMOD 2015) that compresses regular 64-bit timestamps and 64-bit floating-point metric values in memory down to an average of ~1.37 bytes per sample (over 10x compression ratio).

### Key Characteristics
- **Timestamp Delta-of-Deltas**: Telemetry timestamps are usually sampled at fixed intervals (e.g., every 10 seconds). Computing the difference between successive deltas ($\Delta = (t_i - t_{i-1}) - (t_{i-1} - t_{i-2})$) yields 0 in most cases, encoded in a single bit `0`
- **Floating-Point XOR Compression**: Metric values change slowly between successive measurements. XORing the current float with the previous float ($v_i \oplus v_{i-1}$) yields many leading and trailing zeros, which are bit-packed efficiently
- **Streaming compression**: Compresses streaming telemetry on the fly with minimal CPU overhead, enabling hours of recent metric data to reside entirely in high-speed RAM

### When to Use
- In-memory time-series storage engines (Prometheus TSDB, M3DB, InfluxDB)
- High-frequency IoT telemetry and financial market data recording
- Reducing RAM footprint in real-time metrics monitoring clusters

### When NOT to Use
- Highly chaotic, completely random data where floating-point bits do not repeat
- Unstructured text strings or binary blob payloads

### Also see
- [Time-Series Database (TSDB)](#time-series-database-tsdb) · [Downsampling and Rollup](#downsampling-and-rollup)

---

## Downsampling and Rollup

The **lifecycle data management process in time-series systems** that compacts high-resolution raw metric points (e.g., 10-second intervals) into lower-resolution statistical summaries (e.g., 1-minute, 1-hour, or 1-day intervals) as data ages.

### Key Characteristics
- **Multi-tiered retention**: Raw 10s data kept for 7 days $\rightarrow$ 1m rollups kept for 30 days $\rightarrow$ 1hr rollups kept for 1 year
- **Statistical preservation**: Rollup computation must preserve multiple statistical aggregates (`min`, `max`, `sum`, `count`, `p50`, `p99`); averaging averages distorts extreme spikes
- **Storage cost reduction**: Reduces historical time-series storage footprint by 90–99% while preserving long-term trend analysis capability
- **Fast long-range dashboard queries**: 1-year trend graphs query ~8,760 hourly points rather than 3.1 million raw samples

### When to Use
- Production observability backends managing millions of time series over multi-year retention horizons
- Capacity planning dashboards and seasonal anomaly detection
- Cost optimization in cloud metrics monitoring infrastructure

### When NOT to Use
- High-precision forensic debugging immediately after an active incident (where exact millisecond sample resolution is critical)
- Non-aggregatable categorical logs

### Also see
- [Time-Series Database (TSDB)](#time-series-database-tsdb) · [Gorilla Compression](#gorilla-compression)

---

## FlameGraph

A **hierarchical, interactive visualization of profiled execution software stacks** (created by Brendan Gregg) that plots function call trees along the vertical Y-axis and resource consumption (CPU on-CPU time, off-CPU lock wait time, or memory allocation) along the horizontal X-axis.

### Key Characteristics
- **X-axis represents volume**: The horizontal width of each box represents the percentage of total CPU time or memory consumed by that function and its descendants (alphabetically ordered, not chronological)
- **Y-axis represents stack depth**: The vertical height shows the call stack hierarchy, with parent callers on the bottom and child callees stacked on top
- **"Plates" indicate hotspots**: Wide flat tops ("plateaus") immediately reveal CPU bottlenecks and performance regressions without reading raw text profile logs
- **Interactive zooming**: Allows developers to click and zoom into specific sub-stacks for fine-grained performance diagnosis

### When to Use
- Diagnosing CPU saturation, GC pause overhead, and hot loops in high-throughput backend services
- Analyzing memory allocation churn and lock contention bottlenecks
- Continuous production profiling (e.g., Pyroscope, Parca, Google Cloud Profiler)

### When NOT to Use
- Pure network I/O latency investigations where CPU utilization is near zero (use Distributed Tracing instead)
- Macro-level uptime and error monitoring (use Golden Signals dashboards)

### Also see
- [Observability](#observability) · [Distributed Tracing](#distributed-tracing) · [Latency](#latency)

