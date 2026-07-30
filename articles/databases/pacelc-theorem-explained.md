---
type: Article
title: "PACELC Theorem Explained — Distributed Systems Series"
description: "An exploration of the PACELC theorem, which extends CAP theorem by addressing latency-consistency tradeoffs in the absence of network partitions, with practical data replication examples."
source: "https://medium.com/distributed-systems-series/pacelc-theorem-explained-distributed-systems-series-9c509febb8f8"
author: "Lohith Chittineni"
published: 2023-10-06
created: 2026-07-31
tags:
  - distributed-systems
  - pacelc
  - cap-theorem
  - data-replication
  - consistency
  - latency
---

# PACELC Theorem Explained — Distributed Systems Series

> **Source**: [Medium — Distributed Systems Series](https://medium.com/distributed-systems-series/pacelc-theorem-explained-distributed-systems-series-9c509febb8f8)
> **Author**: Lohith Chittineni
> **Published**: 2023-10-06

## Overview

This article explores the trade-offs that system designers face in distributed systems and databases through the **PACELC Theorem** ("pass-elk"), which extends the popular CAP Theorem.

> **Related Reading**: [CAP Theorem Explained — Distributed Systems Series](https://medium.com/distributed-systems-series/cap-theorem-explained-distributed-systems-series-a42c7eae9dae)

## What Is PACELC Theorem?

PACELC is an acronym that stands for:

| Letter | Term |
|:---|:---|
| **P** | Partition |
| **A** | Availability |
| **C** | Consistency |
| **E** | Else |
| **L** | Latency |
| **C** | Consistency |

The theorem states:

> *"If there is a partition (P), how does the system trade off availability and consistency (A and C); else (E), when the system is running normally in the absence of partitions, how does the system trade off latency and consistency (L and C)."*
> — [Daniel J. Abadi](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)

## Why PACELC Exists

In CAP Theorem, when there is no partition tolerance (stable network, no node failures), the system can offer both full consistency and availability (CA). However, CAP assumes this is not practical and focuses on AP (Available & Partition-Tolerant) or CP (Consistent & Partition-Tolerant) systems.

PACELC addresses the gap: **even when there are no network partitions, there are still tradeoffs to consider — specifically between latency and consistency.**

- **Latency** is always present, whether a partition exists or not.
- In CAP, full availability can be thought of as 0 latency; no availability = 100% latency.
- PACELC gives latency explicit attention when partitions do not exist.

## Synchronous vs. Asynchronous Communication

| Mode | Behavior |
|:---|:---|
| **Synchronous** | Once a request is sent, it requires a response before the next task can continue (blocking). |
| **Asynchronous** | Once a request is sent, it does not require an immediate response; other tasks can continue (non-blocking). |

## Data Replication Strategies

### 1. Preprocessing Data Replication (Consistent, High Latency)

A preprocessing system sits between clients and data nodes. All replica nodes agree on the order of update requests via the preprocessor, maintaining consistency. However, latency increases because:

- Requests must pass through the preprocessor for ordering/sequencing.
- The preprocessor may be geographically distant from clients.

### 2. Synchronous Data Replication (Consistent, High Latency)

A primary node accepts all writes; replica/secondary nodes accept reads. After a write, the primary updates all replicas synchronously and waits for all acknowledgments before allowing reads. This ensures consistency but increases latency because the system is limited by the slowest (farthest) replica node.

### 3. Asynchronous Data Replication I (Consistent, High Latency)

The primary node sends asynchronous updates to replicas (no waiting for acknowledgment). All reads and writes are routed through the primary node. Consistency is maintained because the primary is the single source of truth, but latency increases due to routing all requests to the primary.

### 4. Asynchronous Data Replication II (Inconsistent, Low Latency)

The primary performs asynchronous updates to replicas, and reads can be served by any replica node. This may produce inconsistent reads (stale data from replicas that haven't yet received the latest update). Sequence numbers can help detect the latest value. Latency is low because reads don't need acknowledgment from the primary.

### 5. Asynchronous Data Replication III — Hybrid (Medium Consistency, Medium Latency)

A hybrid approach: the primary sends synchronous updates to a subset of replicas and asynchronous updates to the rest. This balances consistency and latency.

The quorum formula determines the behavior:

- **R + W > N**: Consistency is maintained, but with latency overhead.
- **R + W ≤ N**: Latency is reduced, but asynchronous reads may return inconsistent data.

Where:
- **R**: synchronous READ replicas
- **W**: synchronous WRITE replicas
- **N**: total number of replica nodes

## Key Design Factors

When weighing consistency vs. latency in distributed systems, consider:

1. **Synchronous vs. asynchronous calls** between data nodes
2. **Geographical distance** between nodes for data routing
3. **How many nodes** should be available for reads and writes in the cluster (quorum configuration)

## Conclusion

PACELC serves as an extension of CAP Theorem, proposing additional questions about tradeoffs system designers must consider. Neither CAP nor PACELC provides an absolute answer — designers must weigh the tradeoffs based on their specific requirements.

## References

- [Daniel J. Abadi — PACELC Original Paper](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [Daniel J. Abadi — Blog Post on PACELC Motivation](http://dbmsmusings.blogspot.com/2010/04/problems-with-cap-and-yahoos-little.html)
- [CAP Theorem Explained — Distributed Systems Series](https://medium.com/distributed-systems-series/cap-theorem-explained-distributed-systems-series-a42c7eae9dae)
