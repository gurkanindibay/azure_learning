---
type: System Design
title: "AI/ML Infrastructure — Batch Compute with Kueue (Netflix)"
description: "Key architectural takeaways from Netflix's migration of batch compute to Kueue: tenant hierarchy with reserved/shared capacity, open-source scheduling adoption, zero-lift migration strategy, and preemption-based fair sharing."
timestamp: 2026-06-27T00:00:00Z
---

# AI/ML Infrastructure — Batch Compute with Kueue (Netflix)

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [How Netflix Simplified Batch Compute with Kueue](../../articles/case-studies/netflix-batch-compute-kueue.md)
> **Taxonomy Reference**: §4.2 Machine Learning & AI Infrastructure

> **Also see**: [AI/ML Infrastructure Patterns](ai-ml-infrastructure.md) — RAG, LLM cost optimization, Vector search
> **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md) — Preemption, Fair Sharing, Tenant Hierarchy

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`ai-04`](#ai-04-tenant-hierarchy--two-tier-capacity-model) | How to fairly allocate compute across many tenants with different priorities? | Two-tier tenant hierarchy with Reserved + Shared capacity pools |
| [`ai-05`](#ai-05-open-source-adoption-criteria-for-batch-scheduling) | Custom batch scheduler becomes unmaintainable — how to choose an open-source replacement? | Kueue: queue manager that doesn't replace kube-scheduler |
| [`ai-06`](#ai-06-zero-lift-infrastructure-migration) | How to migrate millions of production workloads without disrupting users? | API parity + hardest-first migration + load testing at production QPS |
| [`ai-07`](#ai-07-preemption-based-fair-sharing) | Reserved capacity sits idle while other tenants starve — how to safely share it? | Preemption-based fair sharing: reclaimWithinCohort + withinClusterQueue |
| [`ai-08`](#ai-08-kueue-tenant-mapping) | How to map an existing custom tenant model onto Kueue primitives? | Internal→Cohort, Leaf→ClusterQueue+LocalQueue, Capacity→ResourceFlavor |

---

## ai-04: Tenant Hierarchy & Two-Tier Capacity Model

| | |
|:---|:---|
| **Problem** | Large organizations need to allocate batch compute across teams with different priorities while guaranteeing throughput for critical workloads. A flat queue with simple priorities is insufficient for complex organizational structures. |
| **Key Concept** | A **two-tier tenant hierarchy** (Internal + Leaf) combined with **dual capacity pools** (Reserved + Shared) provides both fairness guarantees and elasticity. |

> **Source**: [§"CMB Tenant Hierarchy"](../../articles/case-studies/netflix-batch-compute-kueue.md#cmb-tenant-hierarchy)

### Strategy

- **Internal Tenants**: Build a tree hierarchy matching organizational structure. They aggregate capacity but don't accept work directly.
- **Leaf Tenants**: Accept jobs and have associated queues. Cannot have children.
- **Reserved Capacity**: Partitioned within the hierarchy so other tenants cannot reserve the same resources. Guarantees throughput for critical tenants.
- **Shared Capacity**: A global pool any tenant can burst into, fair-shared at admission time.

### Tradeoff

- **Without preemption**: Once a job is admitted from shared capacity, it runs to completion regardless of shifts in fair-share demand. A low-priority job admitted during a lull can block a high-priority job submitted moments later.

> **Cross-reference**: [Architecture Principles — Separation of Concerns](../software-architecture/architecture-principles.md)

---

## ai-05: Open-Source Adoption Criteria for Batch Scheduling

| | |
|:---|:---|
| **Problem** | A custom-built batch scheduler (CMB, built 2018) accumulated years of feature work (fair sharing, hierarchical tenants, capacity management, priority queuing) but became too far removed from the underlying Kubernetes cluster to add modern features like preemption. How to choose an open-source replacement? |
| **Key Concept** | **Kueue** is a Kubernetes-native job queueing system that manages admission and queuing **without replacing the kube-scheduler**, enabling integration with existing scheduling profiles while adding preemption, all-or-nothing scheduling, and topology-aware scheduling. |

> **Source**: [§"Why Kueue?"](../../articles/case-studies/netflix-batch-compute-kueue.md#why-kueue)

### Strategy

Netflix chose Kueue over alternatives (YuniKorn, Volcano) based on five criteria:

1. **Non-disruptive scheduling**: Does not replace pod scheduling — integrates with existing kube-scheduler profiles
2. **Adoption momentum**: Active community and innovation pace
3. **Multi-tenant quota management**: Over heterogeneous hardware
4. **Flexible workload primitives**: Operates on `v1.Pod`, `batch/v1.Job`, RayJob/RayCluster
5. **Native features**: Preemption, all-or-nothing scheduling, topology-aware scheduling — features Netflix would have had to build themselves

### Tradeoff

- **Kueue is a queue manager, not a scheduler**: It decides *when* a job can run but delegates *where* to the kube-scheduler. This preserves scheduling optimizations but means Kueue cannot influence pod placement decisions.
- **Platform coupling**: Adopting Kueue ties the platform to the Kubernetes ecosystem's evolution pace and API changes.

> **Cross-reference**: [Architecture Principles — Loose Coupling](../software-architecture/architecture-principles.md)

---

## ai-06: Zero-Lift Infrastructure Migration

| | |
|:---|:---|
| **Problem** | Migrating millions of production batch jobs from a custom scheduler (CMB) to a new open-source system (Kueue) without disrupting any end users or causing throughput regressions. |
| **Key Concept** | **API parity + hardest-first migration + production-scale load testing** derisks the migration by keeping the user-facing contract identical while replacing the underlying implementation. |

> **Source**: [§"Migrating to Kueue"](../../articles/case-studies/netflix-batch-compute-kueue.md#migrating-to-kueue)

### Strategy

Three key tenets:

1. **API parity**: Maintain the exact same API surface — users submit and manage jobs identically. Only the underlying queuing/scheduling component changes.
2. **Hardest customer first**: Migrate the largest and most complex tenant first. If it works for them, it works for everyone. Production migration completed in 4 weeks.
3. **Load test at production scale**: Kueue required significantly higher QPS, Burst, and groupKindConcurrency than defaults. Validated in a dev environment mimicking production Titus topology before rollout.

Architecture: Titus federation routes jobs to Kueue-enabled cells via a custom Kueue router — the federation layer decouples job submission from scheduling implementation.

### Tradeoff

- **API parity constrains innovation**: Keeping the API identical to the legacy system means you cannot introduce new Kueue-native features through the API during migration. New capabilities must wait until after migration is complete.
- **Hardest-first risk**: If the most complex customer fails, it can delay the entire migration. Mitigated by the ability to roll back individual tenants with a single click.

> **Cross-reference**: [Architecture Principles — Fail Fast](../software-architecture/architecture-principles.md)

---

## ai-07: Preemption-Based Fair Sharing

| | |
|:---|:---|
| **Problem** | Reserved capacity sits idle when its owning tenant has no work, while other tenants starve for resources. Without preemption, there's no way to reclaim idle reserved capacity for higher-priority work. |
| **Key Concept** | **Preemption-based fair sharing** allows tenants to use idle reserved capacity from other tenants while maintaining reservation semantics — lower-priority workloads are evicted when the owner needs resources back or when higher-priority work arrives. |

> **Source**: [§"Fair Sharing and Preemption"](../../articles/case-studies/netflix-batch-compute-kueue.md#fair-sharing-and-preemption)

### Strategy

Kueue's preemption configuration operates at two levels:

```yaml
preemption:
  reclaimWithinCohort: Any        # Preempt any lower-priority job in the cohort
  withinClusterQueue: LowerPriority  # Preempt lower-priority jobs within same queue
```

- **reclaimWithinCohort: Any** — When a tenant needs its reserved capacity back, preempt *any* lower-priority workload across the cohort, regardless of which tenant it belongs to.
- **withinClusterQueue: LowerPriority** — Within a single tenant's queue, preempt lower-priority jobs to admit higher-priority ones.

### Results

- **Higher utilization**: Tenants lend idle reserved capacity to others
- **No starvation risk**: Reservation semantics preserved — owners can reclaim capacity
- **Faster turnaround**: Business-critical workloads jump the queue via preemption
- Netflix observed a **significant increase in average resource utilization** after deployment

### Tradeoff

- **Preemption is disruptive**: Evicted jobs lose work and must restart. This is acceptable for batch workloads (which are restartable by nature) but would be unacceptable for serving workloads.
- **Configuration complexity**: Preemption policies must balance fairness with stability — overly aggressive preemption causes thrashing.

> **Cross-reference**: [Resilience Patterns](../resilience/resilience-patterns.md)
> **Dictionary**: [Preemption](../../reference-dictionary/architecture-patterns.md#preemption), [Fair Sharing](../../reference-dictionary/architecture-patterns.md#fair-sharing)

---

## ai-08: Kueue Tenant Mapping

| | |
|:---|:---|
| **Problem** | An existing custom tenant hierarchy (Internal + Leaf tenants with Reserved/Shared capacity) must be mapped onto Kueue's native primitives (Cohorts, ClusterQueues, LocalQueues, ResourceFlavors) without losing semantics. |
| **Key Concept** | A **direct structural mapping** from custom tenant concepts to Kueue primitives enables transparent migration: Internal tenants → Cohorts, Leaf tenants → ClusterQueue + LocalQueue, Capacity config → Resource flavors + Nominal quotas. |

> **Source**: [§"Migrating to Kueue"](../../articles/case-studies/netflix-batch-compute-kueue.md#migrating-to-kueue)

### Strategy

| CMB Concept | Kueue Concept | Semantics Preserved |
|:---|:---|:---|
| Internal Tenant | [Cohort](https://kueue.sigs.k8s.io/docs/concepts/cohort/) | Group of queues that can borrow/lend unused quota |
| Leaf Tenant | [ClusterQueue](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/) + [LocalQueue](https://kueue.sigs.k8s.io/docs/concepts/local_queue/) | ClusterQueue: cluster-scoped quotas + preemption config; LocalQueue: namespace-scoped submission point |
| Reserved Capacity | ResourceFlavor + NominalQuota | Guaranteed resource allocation scoped to a ClusterQueue |
| Shared Capacity | Cohort-level borrowing | Unused quota from any ClusterQueue in the cohort is available to others |
| Priority Queuing | withinClusterQueue preemption | LowerPriority jobs evicted for higher-priority ones |

### Tradeoff

- **Leaky abstraction risk**: Not all CMB semantics map cleanly to Kueue. Custom behaviors (e.g., CMB's admission-only fair sharing without preemption) require rethinking when moving to Kueue's preemption-based model.
- **One-click rollback**: Each tenant can be individually enrolled/rolled back via UI, limiting blast radius during migration.

> **Cross-reference**: [Architecture Principles — Single Source of Truth](../software-architecture/architecture-principles.md)
