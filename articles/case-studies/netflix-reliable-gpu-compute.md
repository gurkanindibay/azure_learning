---
type: Article
title: "Reliable GPU Compute for Large Training & Inference Jobs"
description: "How Netflix detects failing GPUs and network fabric, remediates machines automatically with Kubernetes and Karpenter, and enables multi-week distributed training and serving workloads to survive hardware failures."
source: "https://netflixtechblog.com/reliable-gpu-compute-for-large-training-inference-jobs-d62b03a96d7a"
author: "Nick Rutigliano, Argha C, Samartha Chandrashekar"
published: 2026-10-14
generated: { by: process:okf-format, at: 2026-10-16T08:05:00+03:00 }
---

# Reliable GPU Compute for Large Training & Inference Jobs

> **Source**: [Netflix Technology Blog](https://netflixtechblog.com/reliable-gpu-compute-for-large-training-inference-jobs-d62b03a96d7a)  
> **Authors**: [Nick Rutigliano](https://www.linkedin.com/in/nick-rutigliano/), [Argha C](https://www.linkedin.com/in/argha-c/), [Samartha Chandrashekar](https://www.linkedin.com/in/samartha/)  
> **Related**: [AI/ML Infrastructure](../../system-design-architecture/ai-ml-infrastructure/) — for extracted takeaways  
> **Sub-domain**: GPU Cluster Reliability, Hardware Health Diagnostics, Kubernetes Auto-Repair, Distributed ML Systems  

*How Netflix detects failing GPUs and network fabric, remediates machines automatically, and lets long-running training and inference jobs survive hardware loss.*

---

## Overview

Open Netflix, and the home screen is assembled for you: which rows appear, the order they appear in, the titles within them, and the artwork for each title are chosen by machine learning models trained on how hundreds of millions of members watch. Personalization is one of the most widely used systems at Netflix, and members feel it every time they open the app. Like a growing share of Netflix, it runs on GPUs, which train those models and increasingly serve them live.

Those GPUs have to stay healthy for that experience to hold up, and keeping them healthy is harder than it sounds. A single large training job can run for weeks across hundreds of GPUs spread over many machines. It runs as a **gang**: the ranks move in lockstep, exchanging data every step, so the job advances only as fast as its slowest participant and stops entirely if one participant dies. Every GPU, every high-speed network adapter, and every interconnect must keep working throughout the run. At the scale at which modern machine learning runs, individual GPUs and network links can fail during a run, so the underlying platform must be prepared for this and handle it without a person in the loop.

This post describes how Netflix keeps its GPU infrastructure healthy for training and inference:
1. Detecting failing hardware before and during jobs.
2. Automatically remediating a bad machine.
3. Allowing long jobs to survive the loss of a machine.

These training workloads run on Netflix's modern Kubernetes-native Compute platform.

---

## Why GPU Reliability Matters

Netflix aims to entertain the world, and machine learning has been part of how that happens for years, from recommendations that help members find something to watch to systems that help produce and promote titles. As generative AI advances, investments span both sides of the business: for members, through better recommendations and higher-quality promotional assets; and for storytelling, through creative tools for production partners.

All of this runs on GPUs, for both training and inference, and GPU capacity is among the fastest-growing and most expensive parts of the infrastructure. That makes reliability a business concern on two fronts:

- **Availability**: A training run that loses a machine, or an inference service that cannot get healthy capacity, delays work that members and creators depend on.
- **Cost Efficiency**: A GPU sitting idle behind a slow neighbor, or a whole machine pulled from the pool because one device is degraded, becomes capacity paid for and not used. Higher reliability and higher utilization mean more useful work per GPU, which is equivalent to spending less to do the same work.

Inference is a growing share of that GPU footprint as more AI features reach members, so the reliability and efficiency that matter for multi-week training runs increasingly matter for always-on serving too.

---

## Why Basic Health Checks Are Not Enough

Netflix starts from the baseline provided by the cloud provider. Cloud providers run instance status checks on virtual machines:
- A **system status check** for the underlying host’s power, network, and hardware reachability.
- An **instance status check** to verify that the operating system is up and reachable.
- A **check on attached storage**.

Cloud providers emit scheduled maintenance events when planning to retire or reboot a host, and can automatically recover an impaired instance. Netflix uses all of these, and maintenance events feed internal checks. They catch a machine that is down, unreachable, or slated for maintenance, but they stop at the instance level. They confirm the box is up and reachable. They do not verify that each GPU, its on-chip memory, its interconnect, and its network fabric are healthy enough to support distributed training.

The next step most teams take is a GPU-level check to confirm that the driver responds and that the GPUs are visible. That catches a dead or missing GPU, but misses the cases that consume the most debugging time:

1. **Latent hardware faults under load**: A GPU can answer a status query and still be faulty once a workload touches it. A fault in on-chip memory or in the firmware that manages the device can remain invisible until a job allocates memory or runs sustained compute, at which point the job fails or slows.
2. **Degraded network fabric**: A high-speed network adapter may be present but show fewer links than expected. Collective operations still run, but at a fraction of the bandwidth, so the job does not crash. It crawls, and the cause is easy to miss.
3. **Diagnostic tool hangs and missing dependencies**: A check can fail in ways that leave a faulty machine looking healthy. The diagnostic tool can hang when the driver hangs, and a naive check that waits on it hangs too. A binary that the check depends on can go missing after a driver upgrade, causing the check to stop running and report nothing. A check that can silently stop running is worse than no check, because it gives false confidence while the machine keeps working.

Because a distributed training job runs as a gang, any one of these faults on any single machine can degrade or halt the whole job. None of them shows up in an instance-level check or a driver-responds check. The health system must assume the hardware can lie and the tools that inspect it can break.

![Layered checks closing visibility gaps](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*d15z8m06XjWnYeauK7iXfQ.png)

*A machine can pass a basic check and still be faulty. Layered checks, timeouts, a fallback path, and checks that fail when a dependency is missing close these gaps.*

---

## The Four-Layer Approach

Netflix structures reliability across four distinct layers, each catching what the layer below cannot:

1. **Node and hardware health**: Find bad GPUs, network adapters, interconnects, memory errors, and thermal issues, then taint or recycle the machine.
2. **Scheduler and platform**: Retry at the task and job level, validate a machine before it takes work, and drain and recycle machines safely.
3. **Training loop**: Checkpoint and use elastic workers so a job survives losing a machine.
4. **Observability**: Track metrics, service-level objectives (SLOs), and failure attribution across the other three layers.

The first two layers keep hardware problems away from jobs. The third accepts that some loss is unavoidable and makes it cheap. The fourth reveals whether the first three are working.

![Four-layer reliability architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*2lLAu7fFc5rqqiWY2QAbhA.png)

*Four layers: Each catches what the layer below cannot.*

---

## How the Health Checks Work

Checks execute in two tiers:
- **Device-level checks**: Look at each individual GPU.
- **Node-level agent**: Built on the open-source Kubernetes [node-problem-detector](https://github.com/kubernetes/node-problem-detector), runs on every GPU machine every 30 seconds and turns check results into conditions on the Kubernetes node (the same mechanism Kubernetes uses to mark a node `NotReady`). Controllers watch those conditions and decide whether the machine can take on work.

GPU device checks are built on NVIDIA’s [DCGM](https://developer.nvidia.com/dcgm) (Data Center GPU Manager) for driver-reported error codes, uncorrectable memory errors, interconnect integrity, and thermal state. Networking adapter checks inspect the host state for the count and link state of the [Elastic Fabric Adapter](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/efa.html) (EFA) interfaces that carry cross-machine traffic.

![Two-tier health checking architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*73vlwnPR6M7b1cYx43QeGw.png)

*Two-tier health checking. Device-level and node-level checks become Kubernetes node conditions, which controllers then turn into taints, drains, terminates, and replaces.*

Key design principles of the health checks:

- **Failing closed**: If the driver or diagnostic tool is unresponsive, the check times out and marks the machine unhealthy. A check that cannot reach the hardware reports a problem rather than passing, ensuring a wedged driver takes the machine out of rotation rather than hiding behind a hung tool.
- **Kernel log fallback path (`dmesg`)**: Driver error codes are the strongest signal that a GPU has faulted, but the tool that reads them can itself break during certain failure modes. When it does, the platform reads the kernel log `dmesg` directly for those codes, ensuring no Xid or SXid errors are missed.
- **Custom fatal-error map**: Vendor driver error catalogs lag newer GPU generations and do not always match production observations. Netflix maintains a custom mapping of which error codes are fatal for each GPU family. A code that requires resetting the GPU in one generation can be benign in another, and one GPU generation emits a burst of normally-fatal codes on every healthy boot (treated as noise rather than draining fresh machines).
- **No silent no-ops**: A check fails explicitly when a required dependency is missing. Following an upgrade that dropped a binary the network-adapter check relied on, the check had quietly stopped running, allowing machines with missing adapters to ship for days. Now, a missing dependency immediately fails the check.

---

## Turning a Bad Machine into Healthy Capacity, Automatically

When a check fails, the machine’s node condition changes, and controllers take over. The platform distinguishes between two levels of severity:

- **Problem Condition**: Blocks new work from landing while existing jobs continue running. Pulling a running job is disruptive, and many transient issues clear on their own.
- **Failure Condition**: If a problem condition persists beyond a tolerance window, it escalates to a failure condition. The controller evacuates the machine, drains its tasks (overriding normal disruption limits to move rapidly), terminates the host, and provisions a replacement.

### Customizing Karpenter for Graded Node Auto-Repair

Netflix leverages [Karpenter](https://karpenter.sh/) node auto-repair on its compute stack, customized with a policy and controller that maps each node condition to the duration tolerated before acting:
- Fast-fatal errors are actioned within minutes.
- Flaky signals are given a longer observation window.
- A cluster disruption cap prevents bad rollouts of health checks from cascading into tearing down an entire cluster.

![Graded remediation flow](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*E194fQZ3PRUDlq0AU5VQPg.png)

*Graded remediation. A problem is tolerated and may clear; a persistent failure escalates to evacuation and draining, then to a fast in-place fix or termination for confirmed hardware faults.*

### Matching Remediation Action to Fault Type

Replacement is the slowest way to restore capacity. Netflix matches the action to the specific fault:

1. **Kill the offending job**: Clears software wedges and userland driver deadlocks.
2. **Reset a single GPU**: Clears many transient device faults without affecting neighboring hardware.
3. **Reboot the machine**: Clears accumulated firmware state drift over long uptime.
4. **Terminate and replace**: Reserved for hardware that definitively fails trusted diagnostics.

For terminated machines, Netflix records the GPU’s **immutable hardware identifier**, which persists across reboots and instance relaunches even when the EC2/cloud instance changes. This identifier is reported to the cloud provider and maintained on an internal blocklist, ensuring a failing physical device does not quietly rejoin the pool under a new instance identity.

To prevent scheduling race conditions, fresh machines are held until checks have run and settled. Previously, a newly checked machine could be handed to the scheduler while checks were still executing, allowing a job to land moments before a slow check flagged an issue.

---

## Validating a Machine Before It Takes Work

A machine that just booted is not trusted until proven healthy:

1. **System checks**: Verifies kernel, storage, and host reachability.
2. **Topology inspection**: Confirms all GPUs, interconnects, and NUMA/PCIe topologies are present.
3. **GPU diagnostics**: Runs a round of active diagnostics under test load.
4. **Settlement window**: Waits for the health checks to run **twice** before removing the startup taint. Longer checks (such as counting network adapters) take more than one cycle to fire; releasing after a single pass risked admitting work prematurely.

On teardown, deeper diagnostics run and GPU identifiers are recorded into the bad-hardware database to prevent problematic hardware from cycling back into service.

---

## Letting Long Jobs Survive Machine Loss

Even with comprehensive detection and pre-flight validation, hardware will fail mid-run. The platform minimizes the cost of failure:

- **Frequent checkpointing**: Training jobs checkpoint state to object storage. When a machine is lost, jobs resume from the latest healthy checkpoint rather than restarting a multi-week run from scratch.
- **Elastic retryable workers**: Workers can dynamically disconnect, re-attach, and restart.
- **Automated scheduler retries**: The platform scheduler automatically retries failures caused by infrastructure faults.

### Failure Attribution: Platform vs. Application

Automatic retries require accurate failure attribution. Retrying every failure blindly masks genuine application bugs and burns expensive GPU hours looping on unfixable errors.

Example: A class of timeouts in [NCCL](https://developer.nvidia.com/nccl) (NVIDIA Collective Communications Library) appeared to be network faults, but deep tracing revealed they were caused by data-loading pipeline stalls at high worker counts. The GPUs and network fabric were healthy; the root cause was in the CPU/data pipeline. Blindly treating NCCL timeouts as hardware failures would have cycled healthy machines without resolving the issue.

---

## Measuring Reliability: Goodput and SLOs

Netflix tracks GPU reliability against three Service-Level Objectives (SLOs), each partitioned by root cause (hardware, driver, platform, user):

- **Availability**: Amount of GPU capacity available for scheduling at any moment.
- **Job-start success**: Whether a job starts promptly once capacity is allocated.
- **Job success**: Whether a job completes without a platform-induced failure.

Crucially, the fleet optimizes for **goodput**—the percentage of useful computation completed—rather than raw uptime. Because distributed training runs as a gang, a job held back by a single slow GPU can report 100% uptime on an infrastructure dashboard while delivering near-zero effective compute progress.

---

## The Closed Remediation Loop

Hardware reliability operates as a closed continuous loop:

1. **Validate at allocation**: Pre-flight checks, collective communication benchmarks, and pairwise network bandwidth tests run before job admission. Machines failing within the first minute fail before the job lands.
2. **Passive and active monitoring**: Observes driver errors, memory errors, interconnect status, and thermal events during the run.
3. **Systemic view of jobs**: Evaluates the distributed job as a whole to catch slow straggler ranks dragging the gang.
4. **Graded automatic remediation**: Executes targeted recovery (job restart, GPU reset, node reboot, or Karpenter replacement).
5. **Repeat**: Unified across batch schedulers ([Kueue](https://kueue.sigs.k8s.io/)) and distributed compute engines ([Ray](https://www.ray.io/)).

![The reliability loop](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*UpFBA2LWwDLkaujStvIq_g.png)

*The reliability loop: validate, watch, actively check, view the job as a system, remediate, then repeat.*

---

## Sharing GPUs Safely

Not every workload requires an entire GPU, particularly small inference models. Running small inference tasks on dedicated high-end GPUs wastes significant capacity.

### Multi-Instance GPU (MIG) Partitioning

Netflix partitions GPUs using NVIDIA [MIG](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/) for hardware-enforced memory and compute isolation between tenants:
- Faults or memory leaks in one tenant slice cannot impact another slice.
- Partitions can be reconfigured dynamically without rebooting the host machine, enabling the pool to alternate between fine-grained inference slices and full GPUs as demand fluctuates.

![Multi-GPU and multi-tenant isolation](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*1MA62iL5MCRimp5V1Fgmrw.png)

*On a multi-GPU machine, isolate a single faulty GPU, keep the rest in service, and partition healthy GPUs across multiple tenants with memory-level isolation.*

### Kubernetes Dynamic Resource Allocation (DRA)

GPU and network adapter allocation currently relies on traditional Kubernetes device plugins. Netflix is transitioning to Kubernetes **Dynamic Resource Allocation (DRA)**:
- **Topology-aware placement**: GPUs communicating with network adapters or CPUs on the incorrect PCIe root incur substantial cross-socket bandwidth penalties. DRA enables co-scheduling devices aligned with PCIe roots and NUMA domains.
- **Single-device isolation**: With DRA, a multi-GPU host that develops a single faulty GPU can have that specific device cordoned off while keeping the remaining healthy GPUs serving traffic, eliminating unnecessary whole-host evacuations.
- **Expressive requests**: Workloads request abstract hardware capabilities (e.g., minimum memory, tensor core generation) rather than hardcoded GPU models.

---

## Production Results

Deploying layered health checks and automated graded remediation yielded substantial improvements across Netflix's GPU fleet:

- **GPU Node Availability**: Consistently achieved **>99.95%** availability.
- **Job Success Rate**: Rose from **~98% to above 99.5%**.
- **Restoration Latency**: Graded remediation returns capacity in minutes via job kills, device resets, or node reboots, avoiding the multi-minute latency of cold cloud instance replacements.

---

## Future Roadmap

1. **Expanded Active Checks & Burn-in**: Widening synthetic burn-in testing under load to uncover subtle marginal hardware defects before workloads touch nodes.
2. **Topology-Aware Scheduling**: Leveraging DRA with Karpenter to schedule across Compute/IMEX domains, PCIe trees, and NUMA nodes.
3. **Custom Linux Kernel Scheduling (`sched_ext`)**:
   - Prioritizing processes during collective synchronization phases (e.g., AllReduce exchanges) to minimize gang idle time across hundreds of machines.
   - Elevating data-loader process priority to eliminate CPU-to-GPU data starvation bottlenecks.
4. **Thermal Gap Straggler Mitigation**: GPUs running 10–15°C hotter than peers (even within acceptable manufacturer operating limits) set the gang's pace due to thermal throttling; the platform will proactively migrate jobs off hot devices.
5. **Enhanced NCCL RAS Monitoring**: Deeper reliability, availability, and serviceability (RAS) monitoring for NCCL to detect mismatched collectives and communication hangs immediately.

---

## Architectural Summary

| Dimension | Traditional Approach | Netflix GPU Reliability Architecture |
|:---|:---|:---|
| **Health Detection** | Cloud instance status check & `nvidia-smi` driver ping | Two-tier layered checks (DCGM + node-problem-detector + `dmesg` fallback) |
| **Tool Failures** | Hung tools cause checks to block or pass silently | Fail-closed timeouts; checks fail if dependencies are missing |
| **Remediation** | Manual on-call draining & full VM termination | Graded automated remediation (Job kill → GPU reset → Reboot → Replace) |
| **Instance Cycling** | Bad GPUs can rejoin pool under new instance IDs | Immutable GPU hardware IDs recorded and blacklisted |
| **Admission** | Machine released immediately after boot | Startup taint held through two complete check cycles |
| **Fault Attribution** | All job failures treated equally or retried blindly | Automated classification (platform fault vs application bug/stalls) |
| **Resource Allocation** | Static device plugins per node | Dynamic Resource Allocation (DRA) + MIG memory isolation |
| **Fleet Metric** | Node uptime percentage | Distributed goodput (% useful training steps completed) |
