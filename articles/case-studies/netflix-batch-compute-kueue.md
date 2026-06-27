---
type: Article
title: "How Netflix Simplified Batch Compute with Kueue"
description: "Netflix's migration of millions of batch workloads from a custom Compute Managed Batch (CMB) system to Kueue, a Kubernetes-native job queueing system, including tenant hierarchy mapping, fair-sharing with preemption, and zero-lift migration strategy."
source: "https://netflixtechblog.com/how-netflix-simplified-batch-compute-with-kueue-87860682629c"
author: "Alvin Bao, Alex Petrov, Jennifer Lai, Aidan Sherr, Samartha Chandrashekar"
published: 2026-06-23
timestamp: 2026-06-27T00:00:00Z
---

# How Netflix Simplified Batch Compute with Kueue

> **Source**: [Netflix Technology Blog](https://netflixtechblog.com/how-netflix-simplified-batch-compute-with-kueue-87860682629c)  
> **Related**: [AI/ML Infrastructure](../../system-design-architecture/ai-ml-infrastructure/) — for extracted takeaways

## Overview

Netflix transitioned its compute infrastructure to be more Kubernetes-native by incorporating [Kueue](https://kueue.sigs.k8s.io/), a cloud-native job queueing system for batch workloads, replacing the custom queuing and scheduling logic in their homegrown managed batch solution **Compute Managed Batch (CMB)**.

This article covers the motivation, migration strategy, architecture, and results of moving millions of batch jobs to Kueue.

## Brief Overview of CMB and Titus

CMB is a managed batch solution that allows users and applications to execute and manage workloads that run to completion. Using a tenant hierarchy, workloads are managed and queued with ordered execution through priorities, and capacity is managed on a per-tenant basis.

Workloads submitted to CMB run on [Titus](https://medium.com/netflix-techblog/titus-the-netflix-container-management-platform-is-now-open-source-f868c9fb5436), Netflix's container platform. Titus provides workload federation across multiple cells (Kubernetes clusters) and federated capacity reservations, meaning CMB can talk to a single Titus endpoint without worrying about the underlying cell/cluster topology.

### CMB Tenant Hierarchy

Tenants provide a grouping mechanism for jobs submitted on behalf of organizations, platforms, or applications. Users organize tenants to match their team and application ownership structure.

Tenants are associated with a capacity configuration defining:
- **Weight**: Used for fair sharing
- **Resource dimensions**: CPU, memory, etc.

There are two types of tenants:

1. **Internal Tenants** — Facilitate creation of a tree of tenants. Their children can be both internal and leaf tenants. Internal tenants do not accept work and have no associated queues.
2. **Leaf Tenants** — Accept work and have queues associated with them. Cannot have children.

Capacity comes in two types:

**Reserved Capacity**
- For internal tenants: fair-shared across the subtree and usable by leaf tenants under that internal tenant.
- For leaf tenants: partitions capacity within the hierarchy so other tenants cannot reserve the same resources. Not shared with any other tenant.

**Shared Capacity**
- A global pool that any tenant can burst into, in addition to reserved capacity.
- Reservations are not required to use CMB.
- Fair-shared across tenants, but only at admission — CMB had **no preemption**, so once a job was admitted, it ran to completion regardless of shifts in fair-share demand.

> **Key insight**: Kueue changes the semantics for **both** types of capacity by introducing preemption-based fair sharing.

## Why Kueue?

CMB was created in 2018, before or alongside many open-source batch compute offerings. Over time, features CMB offered (fair sharing, hierarchical tenants, capacity management, priority queuing) became available in open-source projects. Developing new features like preemption became increasingly difficult because CMB was far removed from the underlying Kubernetes cluster.

Netflix chose Kueue for five reasons:

1. **Non-disruptive scheduling**: Unlike YuniKorn or Volcano, Kueue does not replace pod scheduling by the kube-scheduler, allowing integration with existing Titus scheduling profiles.
2. **Adoption momentum and innovation pace**.
3. **Multi-tenant quota management** over heterogeneous hardware.
4. **Flexible workload primitives**: Operates on `v1.Pod` and `batch/v1.Job`, and supports higher-level abstractions such as RayJob/RayCluster.
5. **Native features Netflix wanted**: Preemption, all-or-nothing scheduling, topology-aware scheduling.

## Migrating to Kueue

The migration initiative was called **Netflix Batch**. Key tenets:

1. **Zero lift for end users** — completely transparent migration
2. **No regressions** in container launch rate and overall max throughput
3. **Replace CMB queuing and scheduling** with Kueue

### Architecture Changes

The key difference: queuing and scheduling is deferred to Kueue, which is enabled in each Kueue-enabled Titus cell. Titus federation routes jobs to Kueue cells using a custom Kueue router.

Under the hood, tenant enrollment converts:
- **Internal tenants** → [Cohorts](https://kueue.sigs.k8s.io/docs/concepts/cohort/)
- **Leaf tenants** → [ClusterQueue](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/) + [LocalQueue](https://kueue.sigs.k8s.io/docs/concepts/local_queue/)
- **Capacity configuration** → Resource flavors and nominal quotas

### Lessons Learned

1. **API parity derisking**: Maintaining API parity with the existing system (vs exposing a new API surface) and migrating underlying components first derisked the project by unstacking bets while ensuring no customer disruption.
2. **Migrate the hardest first**: Migrating the largest and most complex customer first built confidence for the rest, resulting in the production migration lasting only 4 weeks.
3. **Load test with production-like QPS**: Kueue required much higher QPS, Burst, and groupKindConcurrency than default configuration to meet throughput needs. This was derisked early via load tests in a development environment mimicking Titus.

## Current State of Kueue at Netflix

Kueue is fully rolled out in production, managing millions of batch workloads. Future directions include enrolling more Titus batch workloads and productionizing fair sharing and preemption for better utilization.

### Fair Sharing and Preemption

With Kueue, [Preemption-based Fair Sharing](https://kueue.sigs.k8s.io/docs/concepts/fair_sharing/#preemption-based-fair-sharing) allows Netflix Batch to:
- Maintain reservation semantics while lending resources to other tenants when reservations are idle
- Preempt lower-priority workloads for higher-priority workloads

Benefits for customers:
- Tenants can use more idle capacity from reservations
- Submit more jobs without starvation risk
- Quicker turnaround for business-critical workloads

Example preemption configuration:

```yaml
apiVersion: kueue.x-k8s.io/v1beta2
kind: ClusterQueue
metadata:
  name: "team-a-cq"
spec:
  preemption:
    reclaimWithinCohort: Any
    withinClusterQueue: LowerPriority
```

With these features deployed, Netflix Compute has seen a **significant increase in average resource utilization**.

## Key Concepts Summary

| Concept | Description |
|:---|:---|
| **Kueue** | Kubernetes-native job queueing system for batch workloads |
| **Titus** | Netflix's container management platform (Kubernetes-based, open source) |
| **CMB** | Compute Managed Batch — Netflix's legacy custom batch solution |
| **Cohort** | Kueue concept: group of ClusterQueues that can borrow/lend unused quota |
| **ClusterQueue** | Kueue concept: cluster-scoped queue with resource quotas and preemption config |
| **LocalQueue** | Kueue concept: namespace-scoped queue for user-facing job submission |
| **Fair Sharing** | Weighted allocation of resources across tenants |
| **Preemption** | Evicting lower-priority workloads to admit higher-priority ones |
| **Reserved Capacity** | Capacity partitioned within hierarchy, not shared with other tenants |
| **Shared Capacity** | Global pool any tenant can burst into |

## Acknowledgement

This work would not have been possible without the great work of the entire Compute team at Netflix.
