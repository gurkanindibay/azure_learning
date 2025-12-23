# Azure High Performance Computing (HPC) and Specialized Compute Solutions

## Table of Contents

- [Overview](#overview)
- [Azure CycleCloud](#azure-cyclecloud)
- [Practice Questions](#practice-questions)
  - [Question 1: HPC Cluster Provisioning with Third-Party Scheduler](#question-1-hpc-cluster-provisioning-with-third-party-scheduler)

---

## Overview

Azure provides specialized compute services designed for High Performance Computing (HPC) workloads that require massive parallel processing, custom schedulers, and dynamic resource management. This document covers Azure services and solutions for provisioning, managing, and orchestrating HPC clusters.

### What is High Performance Computing (HPC)?

**High Performance Computing (HPC)** refers to the practice of aggregating computing power to achieve much higher performance than traditional desktop computers, enabling the processing of large-scale computational problems.

#### HPC Characteristics

- **Parallel Processing**: Breaks complex problems into smaller tasks executed simultaneously
- **High Throughput**: Processes large volumes of calculations quickly
- **Custom Schedulers**: Uses specialized job schedulers (PBS, Slurm, LSF, etc.)
- **Dynamic Scaling**: Automatically scales resources based on workload demands
- **Interconnect Requirements**: Requires high-speed, low-latency networking (InfiniBand, RDMA)

#### Common HPC Use Cases

✅ **Scientific research** - Molecular modeling, genomics, climate simulation  
✅ **Engineering simulations** - Computational fluid dynamics (CFD), finite element analysis (FEA)  
✅ **Financial modeling** - Risk analysis, Monte Carlo simulations  
✅ **Artificial intelligence** - Deep learning model training  
✅ **Media rendering** - Video processing, 3D animation  
✅ **Oil and gas** - Seismic analysis, reservoir simulation

---

## Azure CycleCloud

**Azure CycleCloud** is a service designed for creating, managing, operating, and optimizing HPC clusters in Azure. It provides a comprehensive solution for provisioning and orchestrating HPC environments with support for third-party and custom job schedulers.

### Key Features

#### 1. **Cluster Orchestration**

- **Automated provisioning** - Deploy and configure HPC clusters automatically
- **Multi-scheduler support** - Works with PBS, Slurm, LSF, Grid Engine, and custom schedulers
- **Template-based deployment** - Use pre-built or custom cluster templates
- **Infrastructure as Code** - Define cluster configurations declaratively

#### 2. **Dynamic Resource Management**

- **Auto-scaling** - Automatically add/remove nodes based on job queue
- **Cost optimization** - Scale down idle resources to minimize costs
- **Multiple VM types** - Mix different VM sizes within the same cluster
- **Spot VM integration** - Use Azure Spot VMs for cost-effective compute

#### 3. **Scheduler Integration**

**Supported Schedulers:**

| Scheduler | Description | Common Use Cases |
|-----------|-------------|------------------|
| **Slurm** | Simple Linux Utility for Resource Management | Research, academic HPC |
| **PBS Pro** | Portable Batch System | Enterprise HPC, commercial |
| **IBM Spectrum LSF** | Load Sharing Facility | Financial services, life sciences |
| **Grid Engine** | Sun Grid Engine / Univa Grid Engine | Engineering, manufacturing |
| **HTCondor** | High Throughput Computing | Distributed computing |
| **Custom** | Your own scheduler | Specialized requirements |

#### 4. **Monitoring and Management**

- **Web-based UI** - Intuitive interface for cluster management
- **CLI support** - Command-line interface for automation
- **Real-time monitoring** - Track cluster health, job status, resource utilization
- **Cost tracking** - Monitor spending across clusters and projects

#### 5. **Storage Integration**

- **Azure NetApp Files** - High-performance NFS for HPC workloads
- **Azure Blob Storage** - Object storage for data lakes
- **BeeGFS** - Parallel file system for HPC
- **Lustre** - High-performance parallel file system
- **NFS/SMB** - Traditional network file systems

---

### Azure CycleCloud Architecture

#### Basic Architecture

```plaintext
┌─────────────────────────────────────────────────────────────┐
│                    AZURE CYCLECLOUD                         │
│                   (Management Layer)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CycleCloud Application (Web UI + API)             │   │
│  │  ├─ Cluster Templates                               │   │
│  │  ├─ Auto-scaling Engine                             │   │
│  │  ├─ Scheduler Integration                           │   │
│  │  └─ Monitoring & Reporting                          │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Provisions & Manages
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    HPC CLUSTER IN AZURE                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  HEAD NODE (Scheduler + Management)                  │  │
│  │  ├─ Job scheduler (Slurm/PBS/LSF/etc.)              │  │
│  │  ├─ Cluster management software                      │  │
│  │  └─ User access portal                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            │ Schedules jobs                 │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  COMPUTE NODES (Worker VMs)                          │  │
│  │                                                       │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │  │
│  │  │ Node 1  │  │ Node 2  │  │ Node 3  │  │ Node N  │ │  │
│  │  │ (VM)    │  │ (VM)    │  │ (VM)    │  │ (VM)    │ │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │  │
│  │                                                       │  │
│  │  Auto-scales based on job queue                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                            │ Access shared storage          │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SHARED STORAGE                                       │  │
│  │  ├─ Azure NetApp Files (NFS)                         │  │
│  │  ├─ BeeGFS / Lustre                                  │  │
│  │  └─ Azure Blob Storage                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### How Azure CycleCloud Works

#### Cluster Lifecycle Management

**1. Cluster Template Definition**

```plaintext
Define cluster configuration:
├─ Scheduler type (Slurm, PBS, etc.)
├─ VM types and sizes
├─ Network configuration
├─ Storage mounts
├─ Auto-scaling rules
└─ Software packages to install
```

**2. Cluster Provisioning**

```plaintext
CycleCloud provisions:
├─ Virtual network and subnets
├─ Head node VM
├─ Initial compute node VMs
├─ Storage resources
├─ Network security groups
└─ Load balancers (if needed)
```

**3. Scheduler Configuration**

```plaintext
CycleCloud configures scheduler:
├─ Installs scheduler software
├─ Sets up job queues
├─ Configures node groups
├─ Establishes auto-scaling policies
└─ Integrates monitoring
```

**4. Dynamic Auto-Scaling**

```plaintext
Runtime behavior:
├─ User submits job to queue
├─ Scheduler evaluates resource needs
├─ CycleCloud detects pending jobs
├─ Automatically provisions additional VMs
├─ New nodes join cluster
├─ Job executes
├─ After completion, idle nodes are removed
└─ Cost savings from scale-down
```

---

### Benefits of Azure CycleCloud for HPC

#### ✅ **Scheduler Flexibility**

- Works with existing third-party schedulers
- No need to rewrite job submission scripts
- Familiar environment for HPC users
- Custom scheduler support

#### ✅ **Cost Optimization**

- Pay only for compute resources when jobs are running
- Auto-scale down idle resources
- Use Azure Spot VMs for non-critical workloads
- Mix VM types to optimize cost/performance ratio

#### ✅ **Simplified Management**

- Single pane of glass for cluster management
- Automated provisioning and configuration
- Pre-built templates for common scenarios
- Integrated monitoring and troubleshooting

#### ✅ **Enterprise Ready**

- Integration with Azure Active Directory
- Role-based access control (RBAC)
- Budget tracking and cost allocation
- Audit logging and compliance

#### ✅ **Performance**

- Support for RDMA-enabled VMs (InfiniBand)
- High-performance networking
- Low-latency interconnects
- GPU acceleration support

---

### When to Use Azure CycleCloud

**Use Azure CycleCloud When:**

✅ Migrating on-premises HPC clusters to Azure  
✅ Need to support third-party job schedulers (Slurm, PBS, LSF)  
✅ Require dynamic auto-scaling based on job queue  
✅ Want to minimize management overhead  
✅ Need cost-effective burst capacity for peak workloads  
✅ Have complex HPC workflows with custom requirements

**Don't Use Azure CycleCloud When:**

❌ Running simple parallel jobs (use Azure Batch instead)  
❌ Don't need a traditional HPC scheduler  
❌ Workload fits containerized orchestration (use AKS)  
❌ Need managed HPC service without infrastructure management  

---

### Azure CycleCloud vs. Other Azure Services

| Feature | Azure CycleCloud | Azure Batch | Azure HPC Cache | Azure VMss |
|---------|------------------|-------------|-----------------|------------|
| **Purpose** | HPC cluster orchestration | Managed batch processing | Storage caching | VM scaling |
| **Scheduler** | Third-party (Slurm, PBS, LSF) | Built-in | N/A | N/A |
| **Management** | Self-managed with automation | Fully managed | Fully managed | Self-managed |
| **Auto-scaling** | Job queue-based | Job queue-based | N/A | Metric-based |
| **Custom config** | High flexibility | Limited | Limited | Medium |
| **Use case** | Traditional HPC workloads | Simple batch jobs | Storage acceleration | General compute scaling |
| **Learning curve** | Medium | Low | Low | Low |

---

### Comparison: Azure Services for Compute Management

| Service | Primary Purpose | HPC Support | Scheduler Integration |
|---------|-----------------|-------------|----------------------|
| **Azure CycleCloud** ✅ | HPC cluster orchestration | Yes, native support | Third-party schedulers |
| **Azure Automation** | Task automation, configuration management | No | No scheduler support |
| **Azure Lighthouse** | Cross-tenant management | No | No HPC capabilities |
| **Azure Purview** | Data governance | No | Not for compute |
| **Azure Batch** | Managed batch processing | Yes, for simple jobs | Built-in scheduler only |

---

## Practice Questions

### Question 1: HPC Cluster Provisioning with Third-Party Scheduler

#### Scenario

You plan to provision a **High Performance Computing (HPC) cluster** in Azure that will use a **third-party scheduler** (such as Slurm, PBS Pro, or IBM Spectrum LSF).

You need to recommend a solution to **provision and manage the HPC cluster nodes**.

**Question:** What should you include in the recommendation?

---

#### Options

A. Azure Purview  
B. Azure CycleCloud  
C. Azure Lighthouse  
D. Azure Automation

---

**Correct Answer:** **B. Azure CycleCloud**

---

### Detailed Explanation

#### Why Azure CycleCloud is Correct

**Azure CycleCloud** is specifically designed for provisioning, managing, and orchestrating HPC clusters in Azure with support for third-party and custom job schedulers.

##### 1. **Native Third-Party Scheduler Support** ✅

Azure CycleCloud provides **built-in integration** with popular third-party HPC schedulers:

- **Slurm** (Simple Linux Utility for Resource Management)
- **PBS Pro** (Portable Batch System)
- **IBM Spectrum LSF** (Load Sharing Facility)
- **Grid Engine** (Univa Grid Engine)
- **HTCondor**
- **Custom schedulers**

**How it works:**

```plaintext
CycleCloud Integration with Third-Party Scheduler:

1. Select scheduler type (e.g., Slurm)
2. CycleCloud automatically:
   ├─ Installs scheduler software
   ├─ Configures head node as scheduler master
   ├─ Sets up compute nodes as workers
   ├─ Establishes job queue monitoring
   └─ Enables auto-scaling based on queue depth

3. Users submit jobs using native scheduler commands:
   $ sbatch my_job.sh  (for Slurm)
   $ qsub my_job.sh    (for PBS)
   $ bsub < my_job.sh  (for LSF)

4. CycleCloud responds to scheduler needs:
   ├─ Monitors job queue
   ├─ Provisions VMs when jobs are pending
   ├─ Terminates VMs when idle
   └─ Optimizes cost automatically
```

##### 2. **Complete Cluster Lifecycle Management** ✅

CycleCloud handles the entire HPC cluster lifecycle:

**Provisioning:**
- Deploys head nodes, compute nodes, storage
- Configures networking and security
- Installs and configures scheduler software
- Sets up shared storage (NFS, BeeGFS, Lustre)

**Management:**
- Auto-scaling based on job queue depth
- Node health monitoring
- Cluster updates and patching
- Cost tracking and optimization

**Orchestration:**
- Coordinates scheduler with cloud resources
- Manages VM lifecycle
- Handles node failures and replacements
- Enables hybrid cloud scenarios

##### 3. **HPC-Specific Features** ✅

Features specifically designed for HPC workloads:

| Feature | Description | Benefit |
|---------|-------------|---------|
| **RDMA support** | InfiniBand/RDMA-enabled VMs | Low-latency MPI communication |
| **GPU integration** | NVIDIA GPU VM support | AI/ML and rendering workloads |
| **Node arrays** | Heterogeneous VM types | Mix VM sizes per job requirements |
| **Placement groups** | VM proximity placement | Minimize network latency |
| **Spot VM support** | Azure Spot VMs in cluster | Cost optimization |
| **Burst capacity** | On-demand scaling | Handle peak workloads |

##### 4. **Pre-Built Templates** ✅

CycleCloud provides ready-to-use templates:

```plaintext
Available Templates:
├─ Slurm cluster
├─ PBS Pro cluster
├─ Grid Engine cluster
├─ LSF cluster
├─ Custom HPC cluster
├─ GPU cluster
├─ Hybrid on-premises + cloud
└─ Research computing environment
```

##### 5. **Cost Optimization** ✅

Built-in cost management for HPC:

```plaintext
Cost Optimization Features:
├─ Auto-scale down idle nodes
├─ Use Spot VMs for fault-tolerant jobs
├─ Mix VM types (general purpose + compute optimized)
├─ Budget alerts and tracking
├─ Project-based cost allocation
└─ Detailed usage reports
```

---

### Why Other Options Are Incorrect

#### A. Azure Purview ❌

**What it is:**
- **Data governance service**
- Used for data discovery, classification, and cataloging
- Manages data lineage across Azure and on-premises

**Why incorrect:**

❌ **Not a compute service** - Purview is about data governance, not compute provisioning  
❌ **No cluster management** - Cannot provision or manage VMs  
❌ **No scheduler support** - Has no concept of job schedulers  
❌ **Wrong domain** - Data governance vs. compute orchestration

**Use Purview for:**
- Discovering data assets across your organization
- Classifying sensitive data
- Understanding data lineage
- Managing data compliance

**Example scenario that WOULD use Purview:**
```plaintext
Scenario: Need to classify and catalog data across 
         multiple Azure storage accounts
Solution: Azure Purview ✅
```

---

#### C. Azure Lighthouse ❌

**What it is:**
- **Cross-tenant management service**
- Used by service providers to manage customer resources
- Enables delegated access across Azure AD tenants

**Why incorrect:**

❌ **Not for HPC** - Designed for multi-tenant management, not HPC orchestration  
❌ **No scheduler integration** - Cannot work with third-party HPC schedulers  
❌ **No cluster provisioning** - Doesn't provision or configure compute resources  
❌ **Management delegation only** - Provides access control, not resource orchestration

**Use Lighthouse for:**
- Managed service providers (MSPs) managing customer environments
- Cross-tenant resource management
- Delegated administration
- Multi-customer operations at scale

**Example scenario that WOULD use Lighthouse:**
```plaintext
Scenario: MSP needs to manage Azure resources for 50 customers
Solution: Azure Lighthouse ✅
```

---

#### D. Azure Automation ❌

**What it is:**
- **Process automation service**
- Used for configuration management, update management, and task automation
- Runs PowerShell/Python scripts (runbooks)

**Why incorrect:**

❌ **No native HPC support** - Not designed for HPC workloads  
❌ **No scheduler integration** - Cannot integrate with Slurm, PBS, LSF  
❌ **Manual orchestration** - Would require extensive custom scripting  
❌ **Not cluster-aware** - No understanding of HPC cluster concepts  
❌ **High maintenance** - Building HPC capabilities from scratch is complex

**Could you build HPC management with Automation?**

Technically possible but not recommended:

```plaintext
What you'd need to build:
├─ Custom scripts for VM provisioning
├─ Scheduler installation and configuration
├─ Auto-scaling logic based on job queue
├─ Node health monitoring
├─ Storage configuration
├─ Network setup
├─ Cost tracking
└─ Error handling and recovery

Result: Months of development, high maintenance,
        missing features, no support for edge cases

vs.

Azure CycleCloud: All of the above, pre-built,
                 tested, and supported ✅
```

**Use Azure Automation for:**
- VM start/stop scheduling
- Patch management
- Configuration drift remediation
- General task automation

**Example scenario that WOULD use Automation:**
```plaintext
Scenario: Automatically shut down dev VMs at 7 PM daily
Solution: Azure Automation with scheduled runbook ✅
```

---

### Comparison Summary

| Requirement | Azure CycleCloud | Azure Automation | Azure Lighthouse | Azure Purview |
|-------------|------------------|------------------|------------------|---------------|
| **HPC cluster provisioning** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Third-party scheduler support** | ✅ Yes (Slurm, PBS, LSF) | ❌ No | ❌ No | ❌ No |
| **Auto-scaling for HPC** | ✅ Yes, job queue-based | ❌ Manual scripting | ❌ No | ❌ No |
| **Node lifecycle management** | ✅ Automated | ⚠️ Manual via scripts | ❌ No | ❌ No |
| **Built-in monitoring** | ✅ Yes | ⚠️ Basic | ✅ Yes (delegation) | ✅ Yes (data) |
| **Cost optimization** | ✅ Built-in | ❌ Manual | ❌ No | ❌ No |
| **Complexity** | 🟢 Low | 🔴 High (DIY) | 🟢 Low | 🟢 Low |

---

### Real-World Implementation Example

#### Scenario: Research Institution HPC Migration

**Background:**
- On-premises HPC cluster with 500 nodes
- Uses Slurm workload manager
- Peak usage: 2 weeks per month
- Off-peak: 100 nodes idle

**Solution with Azure CycleCloud:**

```plaintext
Step 1: Deploy CycleCloud
├─ Install CycleCloud application in Azure
├─ Configure Azure subscription integration
└─ Set up authentication with Azure AD

Step 2: Create Slurm Cluster Template
├─ Select Slurm cluster template
├─ Configure:
│  ├─ Head node: Standard_D8s_v3
│  ├─ Compute nodes: HBv3 (HPC optimized)
│  ├─ Storage: Azure NetApp Files (NFS)
│  ├─ Network: InfiniBand for RDMA
│  └─ Auto-scale: 0-500 nodes

Step 3: Deploy Cluster
├─ CycleCloud provisions infrastructure
├─ Installs and configures Slurm
├─ Mounts shared storage
└─ Cluster ready in ~20 minutes

Step 4: User Migration
├─ Users submit jobs same way: sbatch job.sh
├─ No changes to job scripts
├─ Transparent cloud bursting
└─ Seamless experience

Results:
├─ Cost savings: 60% (scale down during off-peak)
├─ Setup time: 1 day (vs. weeks for custom solution)
├─ Management overhead: Minimal
└─ User satisfaction: High (no retraining needed)
```

---

### Architecture Comparison

#### Traditional Approach (Azure Automation)

```plaintext
❌ Complex DIY Solution:

User → Manual Scripts → Azure Automation → Custom Logic
                           ├─ VM provisioning scripts
                           ├─ Scheduler installation scripts
                           ├─ Monitoring scripts
                           ├─ Scaling logic scripts
                           └─ Error handling scripts
                                  ↓
                          Months of development
                          High maintenance burden
                          Missing features
                          Error-prone
```

#### CycleCloud Approach

```plaintext
✅ Turnkey Solution:

User → CycleCloud UI/CLI → Azure CycleCloud → Third-Party Scheduler
                               ↓
                         Pre-built templates
                         Automated provisioning
                         Integrated monitoring
                         Native scheduler support
                         Production-ready
```

---

### Key Takeaways

1. **Azure CycleCloud is Purpose-Built for HPC**
   > CycleCloud is specifically designed for provisioning and managing HPC clusters with third-party schedulers. It's the only Azure service that provides native support for Slurm, PBS, LSF, and other HPC schedulers.

2. **Third-Party Scheduler Support is Built-In**
   > Unlike Azure Automation or other services, CycleCloud has pre-built integrations with popular HPC schedulers, eliminating the need for custom development.

3. **Complete Lifecycle Management**
   > CycleCloud handles provisioning, configuration, auto-scaling, monitoring, and cost optimization automatically, reducing management overhead significantly.

4. **Azure Automation is for General Automation**
   > While Azure Automation can run scripts and automate tasks, it's not designed for HPC cluster orchestration and would require extensive custom development.

5. **Know the Service Purpose**
   > - **CycleCloud:** HPC cluster orchestration
   > - **Automation:** General task automation
   > - **Lighthouse:** Cross-tenant management
   > - **Purview:** Data governance

---

### Exam Tips

> **Remember:** When you see "HPC cluster" + "third-party scheduler" in an exam question, the answer is **Azure CycleCloud**.

> **Key phrase to watch for:** "third-party scheduler" - This immediately rules out Azure Batch (which has its own built-in scheduler) and points to CycleCloud.

> **Don't be fooled by:** Azure Automation - While it can automate tasks, it's not designed for HPC and doesn't have scheduler integration.

> **Service purpose clarity:**
> - Purview = Data governance
> - Lighthouse = Cross-tenant management  
> - Automation = Task automation
> - CycleCloud = HPC orchestration

---

### Reference Links

**Official Documentation:**
- [Azure CycleCloud Overview](https://learn.microsoft.com/en-us/azure/cyclecloud/overview)
- [Azure CycleCloud Concepts](https://learn.microsoft.com/en-us/azure/cyclecloud/concepts/core)
- [Create a Slurm Cluster with CycleCloud](https://learn.microsoft.com/en-us/azure/cyclecloud/how-to/slurm)
- [Azure Automation Overview](https://learn.microsoft.com/en-us/azure/automation/automation-intro)
- [Azure Lighthouse Overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Microsoft Purview Overview](https://learn.microsoft.com/en-us/purview/purview)

**Related Topics:**
- Azure Batch (managed batch processing service)
- Azure HPC Cache (storage caching for HPC)
- RDMA-enabled VMs for HPC
- Azure NetApp Files for HPC storage
- InfiniBand networking in Azure

**Domain:** Design Infrastructure Solutions

---

**Document Version:** 1.0  
**Last Updated:** December 13, 2025  
**Author:** Azure Learning Documentation

---

End of Document
