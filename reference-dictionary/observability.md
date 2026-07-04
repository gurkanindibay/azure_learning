---
type: Reference
title: "Observability"
description: "**Observability** — the ability to understand a system's internal state from its external outputs: logs, metrics, and traces."
timestamp: 2026-07-04T00:00:00Z
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
| Error Budget | [`#error-budget`](#error-budget) |
| Blameless Postmortem | [`#blameless-postmortem`](#blameless-postmortem) |
| Real User Monitoring (RUM) | [`#real-user-monitoring-rum`](#real-user-monitoring-rum) |
| Configuration Propagation | [`#configuration-propagation`](#configuration-propagation) |
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

