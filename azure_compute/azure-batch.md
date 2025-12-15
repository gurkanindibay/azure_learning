# Azure Batch

## Table of Contents

- [Overview](#overview)
- [Batch Account Modes](#batch-account-modes)
- [Node Types](#node-types)
- [Practice Questions](#practice-questions)
  - [Question 1: Cost-Optimized Batch Solution with MPI Applications](#question-1-cost-optimized-batch-solution-with-mpi-applications)
  - [Question 2: 3D Geometry Calculation with Inter-Node Communication](#question-2-3d-geometry-calculation-with-inter-node-communication)

---

## Overview

**Azure Batch** is a managed service that enables you to run large-scale parallel and high-performance computing (HPC) batch jobs in Azure. It handles job scheduling and compute resource management automatically, allowing you to focus on your application logic rather than infrastructure management.

### Key Features

- **Automatic scaling** - Dynamically adjust compute resources based on workload
- **Job scheduling** - Built-in scheduler for task orchestration
- **Cost optimization** - Support for low-priority (spot) VMs
- **HPC support** - Run Message Passing Interface (MPI) applications
- **Cross-platform** - Support for Windows and Linux workloads

### Common Use Cases

✅ **Parallel processing** - Media transcoding, financial risk modeling  
✅ **Scientific simulations** - Molecular dynamics, climate modeling  
✅ **Data processing** - ETL pipelines, image processing  
✅ **Rendering** - 3D animation, visual effects  
✅ **Testing** - Large-scale test execution

---

## Batch Account Modes

Azure Batch offers two account modes that determine how compute resources are managed and billed:

### 1. Batch Service Mode (Recommended)

**Description:**  
In Batch service mode, the Azure Batch service manages the underlying infrastructure, including VM allocation, networking, and storage. The compute resources are hosted in Microsoft's subscription, and you're billed only for the resources consumed by your pools and jobs.

**Characteristics:**

- **Simplified management** - Azure handles infrastructure provisioning and management
- **No VNet requirement** - Pools are created in Microsoft-managed virtual networks
- **Production-ready** - Recommended for most production workloads
- **Built-in networking** - Automatic networking configuration
- **Cost-effective** - Pay only for compute resources used

**When to Use:**

✅ Standard production batch workloads  
✅ When you don't need custom networking configurations  
✅ When you want minimal infrastructure management overhead  
✅ For most MPI and parallel processing scenarios

**Example Scenarios:**

- Media transcoding pipelines
- Financial risk calculations
- Scientific simulations
- Data processing jobs

---

### 2. User Subscription Mode

**Description:**  
In user subscription mode, Batch VMs and associated infrastructure (storage accounts, public IPs) are created directly in your Azure subscription. This provides more control over networking and resource configuration but requires additional setup and management.

**Characteristics:**

- **Custom networking** - Deploy pools into your own virtual networks (VNet)
- **Azure Hybrid Benefit** - Apply Windows Server or SQL Server licenses for cost savings
- **Resource visibility** - VMs appear as resources in your subscription
- **More control** - Full control over networking, security, and resource configuration
- **Additional setup** - Requires Key Vault for secrets management

**When to Use:**

✅ Need custom VNet integration (private endpoints, hybrid connectivity)  
✅ Want to leverage Azure Hybrid Benefit for Windows workloads  
✅ Require specific network security configurations  
✅ Need direct access to VM resources for troubleshooting

**Requirements:**

- Azure Key Vault for storing Batch account authentication key
- Pre-configured virtual network (if using custom networking)
- Proper RBAC permissions for VM deployment

---

### Batch Service vs. User Subscription Mode

| Feature | Batch Service Mode | User Subscription Mode |
|---------|-------------------|------------------------|
| **Management** | Fully managed by Azure | Managed in your subscription |
| **Networking** | Microsoft-managed VNet | Your custom VNet |
| **Resource visibility** | Hidden from subscription | Visible in subscription |
| **Azure Hybrid Benefit** | ❌ Not available | ✅ Available |
| **Setup complexity** | ⭐ Simple | ⭐⭐⭐ Complex |
| **Production use** | ✅ Recommended | ✅ For specific needs |
| **Cost optimization** | Good | Better (with Hybrid Benefit) |
| **Use case** | Standard workloads | Custom networking needs |

**Microsoft Recommendation:**  
Use **Batch service mode** for most production scenarios unless you have specific requirements for custom networking or need to leverage Azure Hybrid Benefit.

---

## Node Types

Azure Batch supports two types of compute nodes with different cost and availability characteristics:

### 1. Dedicated Virtual Machines

**Description:**  
Dedicated VMs are reserved exclusively for your Batch workloads and are not subject to eviction. They provide guaranteed compute capacity and are suitable for production workloads requiring reliability and predictability.

**Characteristics:**

- **Guaranteed capacity** - No risk of eviction
- **Stable performance** - Consistent resource availability
- **Higher cost** - Standard Azure VM pricing
- **Production-ready** - Suitable for critical workloads
- **Long-running jobs** - Ideal for extended execution times

**When to Use:**

✅ Production workloads requiring timely completion  
✅ Long-running jobs that cannot tolerate interruption  
✅ MPI applications with tightly coupled tasks  
✅ Time-sensitive batch processing  
✅ Jobs with strict SLAs

**Example Scenarios:**

- Production MPI simulations
- Financial reporting with deadlines
- Critical data processing pipelines
- Time-sensitive rendering jobs

---

### 2. Low-Priority (Spot) Virtual Machines

**Description:**  
Low-priority VMs leverage Azure's surplus capacity at significantly reduced costs (up to 80% discount). However, they can be preempted (evicted) without notice when Azure needs the capacity back, making them suitable only for fault-tolerant workloads.

**Characteristics:**

- **Cost savings** - Up to 80% cheaper than dedicated VMs
- **Preemptible** - Can be evicted at any time without warning
- **No SLA** - No availability guarantees
- **Best-effort** - Capacity depends on Azure surplus
- **Automatic retries** - Batch can automatically retry preempted tasks

**When to Use:**

✅ Development and testing environments  
✅ Short-running, stateless tasks  
✅ Fault-tolerant batch jobs  
✅ Cost-sensitive workloads without strict deadlines  
✅ Embarrassingly parallel workloads (independent tasks)

**When NOT to Use:**

❌ Production workloads with strict SLAs  
❌ Long-running, tightly coupled MPI applications  
❌ Jobs that cannot tolerate interruption  
❌ Time-critical processing

**Example Scenarios:**

- Development environment testing
- Non-critical image processing
- Exploratory data analysis
- Training jobs that support checkpointing

---

### Dedicated vs. Low-Priority VMs

| Feature | Dedicated VMs | Low-Priority VMs |
|---------|--------------|------------------|
| **Cost** | Standard pricing | Up to 80% discount |
| **Availability** | ✅ Guaranteed | ⚠️ Best-effort |
| **Eviction risk** | ❌ None | ✅ Can be preempted |
| **Production use** | ✅ Recommended | ❌ Not recommended |
| **Long-running jobs** | ✅ Suitable | ❌ Not suitable |
| **MPI applications** | ✅ Suitable | ❌ Not suitable |
| **Development/Test** | ✅ Works | ✅ Cost-effective |
| **SLA** | ✅ Yes | ❌ No |

---

## Practice Questions

### Question 1: Cost-Optimized Batch Solution with MPI Applications

#### Scenario

You are designing a **cost-optimized solution** that uses Azure Batch to run **two types of jobs** on Linux nodes:

1. **First job type**: Short-running tasks for a **development environment**
2. **Second job type**: Long-running **Message Passing Interface (MPI) applications** for a **production environment** that requires **timely job completion**

You need to recommend the **pool type** (account mode) and **node type** for each job type. The solution must:

- **Minimize compute charges**
- **Leverage Azure Hybrid Benefit wherever possible**

**Question:** What should you recommend for the **second job type** (production MPI workloads)?

---

#### Options

A. Batch service mode with low-priority virtual machines  
B. User subscription mode with low-priority virtual machines  
C. User subscription mode with dedicated virtual machines  
D. Batch service mode with dedicated virtual machines ✅

---

**Correct Answer:** **D. Batch service mode with dedicated virtual machines**

---

### Detailed Explanation

#### Why Batch Service Mode with Dedicated VMs is Correct ✅

The second job type involves **long-running, production-grade MPI workloads** that require **timely and uninterrupted execution**. Let's analyze why this is the optimal choice:

##### 1. **Dedicated Virtual Machines are Essential for Production MPI**

**MPI (Message Passing Interface) Characteristics:**

- **Tightly coupled tasks** - MPI applications consist of multiple processes that communicate frequently
- **Long execution times** - Simulations and computations can run for hours or days
- **Cannot tolerate interruption** - Eviction would cause the entire job to fail and restart
- **Performance-sensitive** - Requires consistent, predictable compute resources

**Why Dedicated VMs:**

```plaintext
MPI Job Execution Pattern:

┌─────────────────────────────────────────────────┐
│  MPI Job (e.g., Climate Simulation)            │
│                                                 │
│  Node 1 ←→ Node 2 ←→ Node 3 ←→ Node 4         │
│    ↓         ↓         ↓         ↓             │
│  Continuous communication (MPI_Send/Recv)      │
│                                                 │
│  If ANY node is preempted:                     │
│  ❌ Entire job fails                            │
│  ❌ All progress lost                           │
│  ❌ Must restart from beginning                 │
└─────────────────────────────────────────────────┘

✅ Dedicated VMs guarantee all nodes remain available
❌ Low-priority VMs risk preemption = job failure
```

**Production Requirements:**

- **Timely completion** - Production workloads have deadlines and SLAs
- **Reliability** - Must complete without interruption
- **Cost predictability** - Avoid wasted compute from job restarts
- **Performance consistency** - Guaranteed resources for complex calculations

---

##### 2. **Batch Service Mode is Recommended for Production Workloads**

**Why Batch Service Mode:**

Microsoft recommends **Batch service mode** for production scenarios because:

✅ **Simplified management** - Azure handles infrastructure provisioning and management  
✅ **Production-optimized** - Designed for reliable, at-scale batch processing  
✅ **Built-in best practices** - Automatic configuration follows Azure best practices  
✅ **Reduced overhead** - No need to manage VNets, Key Vaults, or networking  
✅ **Faster deployment** - Quick setup without complex prerequisites

**Batch Service Mode Benefits for MPI:**

```plaintext
Production MPI Workload Flow:

1. Submit MPI Job
   ↓
2. Batch Service Mode:
   ├─ Automatically provisions dedicated VMs
   ├─ Configures high-performance networking (RDMA if needed)
   ├─ Sets up inter-node communication
   └─ Monitors job execution
   ↓
3. MPI Job Executes:
   ├─ All nodes guaranteed available
   ├─ Predictable performance
   └─ Reliable completion
   ↓
4. Job completes successfully
   └─ Resources automatically cleaned up
```

**When User Subscription Mode Makes Sense:**

User subscription mode is better suited for:

- Custom VNet integration requirements
- Hybrid connectivity needs (ExpressRoute, VPN)
- Specific network security policies
- Organizations with Windows Server licenses (Azure Hybrid Benefit)

**For this scenario:**  
Since the focus is on **reliability and production stability**, and there's no mention of custom networking requirements, **Batch service mode** is appropriate and simplifies deployment without requiring additional infrastructure setup.

---

##### 3. **Cost Optimization Consideration**

**Question asks to "minimize compute charges"** - but with constraints:

- Must support **production workloads**
- Requires **timely job completion**
- Cannot risk **interruption**

**Analysis:**

❌ **Low-priority VMs** - Cheapest but unsuitable:
- Risk of preemption = job failure
- MPI jobs must restart completely if interrupted
- Wasted compute from failed runs
- Cannot guarantee timely completion
- **Total cost higher** due to reruns

✅ **Dedicated VMs** - Higher unit cost but optimal:
- Guaranteed completion
- No wasted compute from interruptions
- Predictable costs
- Meets production requirements
- **Lower total cost** (no reruns needed)

**Cost Formula:**

```plaintext
Low-Priority Option (❌ Not Suitable):
Cost = (Low VM Price × Hours) + (Failed Job Reruns × Hours)
Risk = High (preemption unpredictable)
Completion = Not guaranteed

Dedicated Option (✅ Correct):
Cost = Standard VM Price × Hours
Risk = None
Completion = Guaranteed
```

**Azure Hybrid Benefit Note:**

The question mentions leveraging Azure Hybrid Benefit "wherever possible." However:

- Azure Hybrid Benefit applies to **Windows Server** and **SQL Server** licenses
- This scenario uses **Linux nodes**
- Hybrid Benefit is **not applicable** to Linux VMs
- User subscription mode's advantage (Hybrid Benefit) doesn't apply here

---

#### Why Other Options Are Incorrect

##### ❌ A. Batch Service Mode with Low-Priority Virtual Machines

**Why Incorrect:**

Low-priority VMs are **fundamentally unsuitable** for production MPI workloads:

**Reasons:**

1. **Preemption Risk** - Can be evicted without notice
   ```plaintext
   MPI Job Progress:
   
   Hour 1-5: Running successfully (50% complete)
   Hour 6: Node preempted ❌
   Result: Entire job fails, all progress lost
   Action: Must restart from beginning
   ```

2. **MPI Cannot Checkpoint** - Most MPI applications don't support mid-execution checkpointing
   - If one node fails, the entire distributed computation fails
   - Cannot resume from interruption point

3. **Production Requirements Violated**:
   - Cannot guarantee "timely job completion"
   - No SLA for availability
   - Unpredictable execution time

4. **Cost Actually Higher**:
   - While per-hour cost is lower, total cost can be higher
   - Failed jobs waste compute resources
   - Multiple restarts consume more total hours

**Example:**

```plaintext
8-hour MPI job on low-priority VMs:

Attempt 1: Runs 6 hours → Preempted → 6 hours wasted
Attempt 2: Runs 4 hours → Preempted → 4 hours wasted
Attempt 3: Completes 8 hours → Success

Total compute hours: 6 + 4 + 8 = 18 hours
vs.
Dedicated VMs: 8 hours guaranteed
```

**When Low-Priority VMs ARE Appropriate:**

✅ Development/testing workloads  
✅ Short-running, independent tasks  
✅ Fault-tolerant batch jobs  
✅ Non-critical processing

---

##### ❌ B. User Subscription Mode with Low-Priority Virtual Machines

**Why Incorrect:**

This option has **two problems**:

1. **Low-priority VMs** - Same issues as Option A (unsuitable for production MPI)
2. **Unnecessary complexity** - User subscription mode adds management overhead without benefits

**Additional Issues:**

- Requires Key Vault setup
- Requires VNet configuration
- More complex deployment
- Azure Hybrid Benefit not applicable (Linux nodes)
- No advantage over Batch service mode for this scenario

**This is the worst option** - combines production-inappropriate node type with unnecessary complexity.

---

##### ❌ C. User Subscription Mode with Dedicated Virtual Machines

**Why Incorrect (But Close):**

This option uses the **correct node type** (dedicated VMs) but the **suboptimal pool mode**.

**Issues with User Subscription Mode Here:**

1. **Unnecessary Complexity**:
   - Requires Azure Key Vault for secrets
   - Requires pre-configured VNet
   - More setup and management overhead
   - Adds operational complexity without benefits

2. **No Stated Requirements for User Subscription Features**:
   - No mention of custom networking needs
   - No hybrid connectivity requirements
   - No specific security policy requirements
   - Azure Hybrid Benefit not applicable (Linux nodes)

3. **Microsoft Recommendation**:
   - Microsoft recommends **Batch service mode** for production workloads
   - User subscription mode is for **specialized scenarios**

**When This Would Be Correct:**

User subscription mode with dedicated VMs would be appropriate if:

✅ Requirements explicitly mention custom VNet integration  
✅ Need private endpoints or hybrid connectivity  
✅ Windows nodes requiring Azure Hybrid Benefit  
✅ Specific network security policies mandated

**For this scenario:**  
Since there's no mention of these requirements, and the goal is to minimize costs while meeting production needs, **Batch service mode** is the simpler and more appropriate choice.

---

### Summary Table: Job Type Recommendations

| Job Type | Environment | Node Type | Pool Mode | Reasoning |
|----------|-------------|-----------|-----------|-----------|
| **First** (Short-running) | Development | Low-priority VMs | Batch service | Cost-optimized, fault-tolerant, non-critical |
| **Second** (Long MPI) | Production | Dedicated VMs ✅ | Batch service ✅ | Reliability, timely completion, production SLA |

---

### Key Takeaways

1. **Production MPI workloads** require **dedicated VMs** due to:
   - Long execution times
   - Tightly coupled inter-node communication
   - Cannot tolerate interruption
   - Need predictable completion times

2. **Batch service mode** is Microsoft's recommendation for:
   - Standard production workloads
   - Simplified management
   - Reliable execution
   - Scenarios without custom networking needs

3. **Low-priority VMs** are only suitable for:
   - Development/testing
   - Short, independent tasks
   - Fault-tolerant workloads
   - Cost-sensitive, non-critical processing

4. **User subscription mode** should be chosen when:
   - Custom VNet integration required
   - Azure Hybrid Benefit needed (Windows)
   - Specific networking/security requirements exist

5. **Cost optimization** doesn't always mean "cheapest per hour":
   - Total cost includes failed runs and reruns
   - Production reliability often results in lower total cost
   - Guaranteed completion > Lower hourly rate for critical workloads

---

### Reference(s)

- [Choose Batch Account Mode](https://learn.microsoft.com/en-us/azure/batch/batch-account-create-portal#choose-account-mode)
- [Azure Batch Spot VMs](https://learn.microsoft.com/en-us/azure/batch/batch-spot-vms)
- [Use Low-Priority VMs with Azure Machine Learning Batch](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-low-priority-batch)
- [Azure Batch Technical Overview](https://learn.microsoft.com/en-us/azure/batch/batch-technical-overview)

---

**Domain:** Design Infrastructure Solutions

---

### Question 2: 3D Geometry Calculation with Inter-Node Communication

#### Scenario

You are designing a solution that calculates **3D geometry from height-map data**. You need to recommend a solution that meets the following requirements:

- **Performs calculations in Azure**
- **Ensures that each node can communicate data to every other node**
- **Maximizes the number of nodes** to calculate multiple scenes as fast as possible
- **Minimizes the amount of effort** to implement the solution

**Question:** Which two actions should you include in the recommendation?

---

#### Options

A. Enable parallel file systems on Azure  
B. Create a render farm that uses virtual machines  
C. Create a render farm that uses virtual machine scale sets  
D. Create a render farm that uses Azure Batch ✅  
E. Enable parallel task execution on compute nodes ✅

---

**Correct Answers:** **D. Create a render farm that uses Azure Batch** and **E. Enable parallel task execution on compute nodes**

---

### Detailed Explanation

#### Why Azure Batch is Correct ✅

**Azure Batch** is specifically designed for running large-scale parallel and high-performance computing (HPC) workloads in Azure. For 3D geometry calculation scenarios, Azure Batch provides:

**Key Benefits:**

1. **Automatic Job Scheduling** - Built-in scheduler handles task orchestration
2. **Pool Scaling** - Automatically scales compute nodes based on workload
3. **Task Distribution** - Distributes tasks efficiently across multiple nodes
4. **Inter-Node Communication** - Supports node-to-node data sharing, essential for 3D geometry processing
5. **Minimal Implementation Effort** - Handles infrastructure management, job queuing, and scaling automatically

**Architecture for 3D Geometry Processing:**

```plaintext
Azure Batch Architecture for 3D Geometry:

┌─────────────────────────────────────────────────────────┐
│  Azure Batch Service                                     │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Compute Pool (Auto-scaling)                      │   │
│  │                                                    │   │
│  │  Node 1 ←──────→ Node 2 ←──────→ Node 3          │   │
│  │    ↑               ↑               ↑              │   │
│  │    │               │               │              │   │
│  │    └───────────────┼───────────────┘              │   │
│  │          Inter-node Communication                 │   │
│  │                                                    │   │
│  │  Each node processes height-map data              │   │
│  │  and shares computed geometry results             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Job Scheduler → Task Queue → Auto-scaling               │
└─────────────────────────────────────────────────────────┘
```

---

#### Why Enable Parallel Task Execution is Correct ✅

**Enabling parallel task execution** on compute nodes allows each node to process multiple scenes or calculations concurrently. This is critical for:

1. **Maximizing Resource Utilization** - Each compute node can run multiple tasks simultaneously
2. **Improving Throughput** - Process more 3D scenes in less time
3. **Optimizing Performance** - Fully utilize available CPU/GPU resources on each node

**Parallel Task Execution Benefits:**

```plaintext
Without Parallel Tasks:          With Parallel Tasks:
┌───────────────────┐           ┌───────────────────┐
│  Compute Node     │           │  Compute Node     │
│  ┌─────────────┐  │           │  ┌─────┐ ┌─────┐  │
│  │  Task 1     │  │           │  │Task1│ │Task2│  │
│  │  (Running)  │  │           │  └─────┘ └─────┘  │
│  └─────────────┘  │           │  ┌─────┐ ┌─────┐  │
│                   │           │  │Task3│ │Task4│  │
│  Tasks 2-4:       │           │  └─────┘ └─────┘  │
│  ⏳ Waiting...    │           │                   │
└───────────────────┘           └───────────────────┘

Time to complete 4 tasks:       Time to complete 4 tasks:
4x (sequential)                 1x (parallel)
```

**Configuration in Azure Batch:**

- Set `taskSlotsPerNode` to allow multiple concurrent tasks per node
- Configure based on available CPU cores and memory
- Enables efficient processing of multiple 3D scenes simultaneously

---

#### Why Other Options Are Incorrect

##### ❌ A. Enable Parallel File Systems on Azure

**Why Incorrect:**

While high-performance parallel file systems (like Azure HPC Cache or Lustre) can help with I/O-intensive workloads, they:

- Are **not necessary** for enabling inter-node communication
- Do **not enable** parallel task execution
- Add **complexity** to the implementation (contrary to "minimize effort")
- Are overkill for this scenario's requirements

**When Parallel File Systems ARE Appropriate:**

✅ Extremely large datasets requiring shared storage  
✅ HPC workloads with heavy file I/O  
✅ When multiple nodes need simultaneous access to large files

**For This Scenario:**  
Inter-node communication and parallel task execution are the requirements - Azure Batch handles these natively without needing specialized file systems.

---

##### ❌ B. Create a Render Farm that Uses Virtual Machines

**Why Incorrect:**

Using standalone virtual machines requires:

1. **Manual Provisioning** - Must deploy and configure each VM manually
2. **Manual Scaling** - No automatic scaling based on workload
3. **Manual Job Distribution** - Must build orchestration logic yourself
4. **Manual Inter-Node Communication** - Must configure networking manually
5. **High Implementation Effort** - Contradicts the "minimize effort" requirement

**Comparison:**

```plaintext
Virtual Machines (Manual):        Azure Batch (Managed):
┌──────────────────────────┐     ┌──────────────────────────┐
│ YOU must manage:         │     │ Azure manages:           │
│ ├─ VM provisioning       │     │ ├─ VM provisioning       │
│ ├─ Auto-scaling logic    │     │ ├─ Auto-scaling          │
│ ├─ Job scheduling        │     │ ├─ Job scheduling        │
│ ├─ Task distribution     │     │ ├─ Task distribution     │
│ ├─ Load balancing        │     │ ├─ Load balancing        │
│ └─ Inter-node networking │     │ └─ Inter-node networking │
│                          │     │                          │
│ Effort: ⭐⭐⭐⭐⭐ High    │     │ Effort: ⭐ Low           │
└──────────────────────────┘     └──────────────────────────┘
```

---

##### ❌ C. Create a Render Farm that Uses Virtual Machine Scale Sets

**Why Incorrect:**

Virtual Machine Scale Sets (VMSS) provide auto-scaling and load balancing, but:

1. **Designed for Stateless Applications** - Optimized for web servers, not HPC batch jobs
2. **No Built-in Job Orchestration** - Must build task scheduling yourself
3. **No Native Node Communication** - Lacks built-in inter-node communication capabilities
4. **Higher Implementation Effort** - Must build much of the orchestration logic yourself

**VMSS vs Azure Batch:**

| Feature | VMSS | Azure Batch |
|---------|------|-------------|
| **Auto-scaling** | ✅ Yes | ✅ Yes |
| **Load balancing** | ✅ Yes | ✅ Yes |
| **Job scheduling** | ❌ Manual | ✅ Built-in |
| **Task distribution** | ❌ Manual | ✅ Built-in |
| **Inter-node communication** | ❌ Manual setup | ✅ Native support |
| **HPC optimization** | ❌ No | ✅ Yes |
| **Implementation effort** | High | Low |
| **Best for** | Web apps, APIs | Batch processing, HPC |

**VMSS is Better For:**

✅ Stateless web applications  
✅ API backends  
✅ Microservices

**Azure Batch is Better For:**

✅ Batch processing  
✅ HPC workloads  
✅ 3D rendering  
✅ Parallel computations

---

### Summary: Why Azure Batch + Parallel Task Execution

| Requirement | Azure Batch | Parallel Task Execution |
|-------------|-------------|-------------------------|
| Performs calculations in Azure | ✅ Native Azure service | ✅ Runs on Azure compute |
| Inter-node communication | ✅ Built-in support | ✅ Enables data sharing |
| Maximize nodes for speed | ✅ Auto-scaling pools | ✅ Multiple tasks per node |
| Minimize implementation effort | ✅ Managed service | ✅ Simple configuration |

---

### Key Takeaways

1. **Azure Batch** is the ideal choice for:
   - Large-scale parallel computing
   - 3D rendering and geometry processing
   - Workloads requiring inter-node communication
   - Scenarios needing automatic scaling and job management

2. **Parallel task execution** maximizes throughput by:
   - Running multiple tasks concurrently on each node
   - Utilizing all available compute resources
   - Processing multiple scenes simultaneously

3. **Avoid manual VM management** when:
   - Azure Batch can handle the orchestration
   - Minimizing implementation effort is a priority
   - Built-in scheduling and scaling are beneficial

4. **VMSS is not optimal** for HPC batch jobs because:
   - Designed for stateless application scaling
   - Lacks job orchestration capabilities
   - Requires building custom scheduling logic

---

### Reference(s)

- [Azure Batch Technical Overview](https://learn.microsoft.com/en-us/azure/batch/batch-technical-overview)
- [Run Tasks Concurrently on Batch Compute Nodes](https://learn.microsoft.com/en-us/azure/batch/batch-parallel-node-tasks)
- [Azure Batch Rendering](https://learn.microsoft.com/en-us/azure/batch/batch-rendering-service)

---

**Domain:** Design Infrastructure Solutions

---
