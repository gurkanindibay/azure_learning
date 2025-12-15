# Azure Virtual Machines - High Availability and Dedicated Hosts

## Table of Contents

- [Overview](#overview)
- [Availability Zones](#availability-zones)
- [Azure Dedicated Hosts](#azure-dedicated-hosts)
- [Virtual Machine Scale Sets (VMSS)](#virtual-machine-scale-sets-vmss)
- [High Availability Architecture](#high-availability-architecture)
- [Practice Questions](#practice-questions)

---

## Overview

Azure Virtual Machines provide various options for ensuring high availability and resiliency. This document covers key concepts including availability zones, dedicated hosts, and virtual machine scale sets to design solutions that can survive datacenter and zone failures.

---

## Availability Zones

**Availability Zones** are physically separate locations within an Azure region. Each zone is made up of one or more datacenters equipped with independent power, cooling, and networking.

### Key Characteristics

- **Physical Separation**: Each availability zone is a separate physical location
- **Zone Count**: Azure regions that support availability zones have **3 zones**
- **Fault Isolation**: Zones are isolated from each other to protect against datacenter failures
- **Low Latency**: Zones within a region are connected with high-speed, low-latency networks
- **Zone Redundancy**: Deploy resources across multiple zones for high availability

### Benefits

✅ **Datacenter-level fault tolerance** - Survive single datacenter failures  
✅ **99.99% VM uptime SLA** - When VMs are deployed across zones  
✅ **Low-latency connectivity** - Between zones in the same region  
✅ **Regional resilience** - Multiple independent infrastructure locations  

### Multi-Zone Resiliency

To maintain availability even if **multiple availability zones fail**, distribute resources across all 3 zones:

- **1 zone deployment**: No zone-level redundancy
- **2 zone deployment**: Survives 1 zone failure
- **3 zone deployment**: Survives up to 2 zone failures ✅

---

## Azure Dedicated Hosts

**Azure Dedicated Hosts** provide physical servers dedicated to your organization, allowing you to deploy Azure VMs on hardware that no other customers share.

### Key Characteristics

- **Physical Isolation**: Entire physical server dedicated to your organization
- **Compliance**: Meets regulatory requirements for hardware isolation
- **Control**: Choose VM families and sizes on the host
- **Visibility**: See the physical host and maintenance schedules
- **Cost**: Billed per dedicated host, not per VM

### Host Groups

**Host Groups** are logical containers for dedicated hosts:

- **Zone Mapping**: Each host group can be mapped to a specific availability zone
- **VM Placement**: VMs are deployed to hosts within the host group
- **High Availability**: Use multiple host groups across zones for resiliency
- **Fault Domains**: Distribute hosts across fault domains within a zone

### When to Use Dedicated Hosts

✅ Regulatory compliance requiring hardware isolation  
✅ Control over maintenance windows and host updates  
✅ Bring-your-own-license (BYOL) scenarios (SQL Server, Windows Server)  
✅ Organizations requiring dedicated infrastructure  
✅ Workloads with specific hardware requirements  

---

## Virtual Machine Scale Sets (VMSS)

**Virtual Machine Scale Sets** allow you to create and manage a group of load-balanced VMs that can automatically increase or decrease based on demand or schedule.

### Key Characteristics

- **Auto-scaling**: Automatically add or remove VM instances based on metrics
- **Load Balancing**: Built-in integration with Azure Load Balancer or Application Gateway
- **High Availability**: Deploy across availability zones and fault domains
- **Large Scale**: Support for up to 1,000 VM instances (3,000 with single placement group disabled)
- **Uniform Management**: Apply updates and configurations to all instances

### Scaling Options

1. **Manual Scaling**: Set a specific instance count
2. **Scheduled Scaling**: Scale based on time/date
3. **Metric-Based Scaling**: Scale based on performance metrics (CPU, memory, etc.)
4. **Custom Metric Scaling**: Scale based on application-specific metrics

### Benefits for High Availability

✅ **Automatic scaling** - Respond to load changes dynamically  
✅ **Zone distribution** - Spread instances across availability zones  
✅ **Self-healing** - Replace unhealthy instances automatically  
✅ **Rolling updates** - Update instances without downtime  
✅ **Load balancing** - Distribute traffic evenly across healthy instances  

---

## High Availability Architecture

### Architecture Pattern: Multi-Zone Deployment with Dedicated Hosts

For workloads requiring:
- High availability across zone failures
- Automatic scaling capabilities
- Dedicated hardware for compliance
- Resiliency even if two zones fail

**Recommended Architecture**:

```
Azure Region (East US)
│
├─ Availability Zone 1
│  │
│  └─ Host Group 1
│     ├─ Dedicated Host 1  ←  [VM1] [VM2] (from VMSS 1)
│     ├─ Dedicated Host 2  ←  [VM3] [VM4] (from VMSS 1)
│     └─ Dedicated Host N  ←  [VM...] 
│
├─ Availability Zone 2
│  │
│  └─ Host Group 2
│     ├─ Dedicated Host 1  ←  [VM5] [VM6] (from VMSS 2)
│     ├─ Dedicated Host 2  ←  [VM7] [VM8] (from VMSS 2)
│     └─ Dedicated Host N  ←  [VM...]
│
└─ Availability Zone 3
   │
   └─ Host Group 3
      ├─ Dedicated Host 1  ←  [VM9]  [VM10] (from VMSS 3)
      ├─ Dedicated Host 2  ←  [VM11] [VM12] (from VMSS 3)
      └─ Dedicated Host N  ←  [VM...]
```

**Key:**
- Each zone has 1 Host Group
- Each Host Group contains multiple Dedicated Hosts (physical servers)
- Each zone has 1 VMSS that places VMs onto those Dedicated Hosts
- VMs from the scale set run ON the dedicated hosts

### Design Principles

1. **3 Host Groups**: One per availability zone for zone-level isolation
   - Each host group contains one or more dedicated hosts (physical servers)
   - Host groups are mapped to a specific availability zone

2. **3 VM Scale Sets**: One per zone, each configured to deploy VMs onto the dedicated hosts
   - VMSS instances (VMs) are placed ON the dedicated hosts within the host group
   - Each VMSS is zone-specific and targets its corresponding host group

3. **Zone Redundancy**: Distribute workload across all 3 zones
   - Each zone operates independently
   - Failure of 2 zones still leaves 1 zone operational

4. **Automatic Scaling**: VMSS provides dynamic scaling based on demand
   - As VMSS scales out, new VMs are placed on available dedicated hosts
   - As VMSS scales in, VMs are removed but dedicated hosts remain

5. **Dedicated Infrastructure**: Host groups ensure hardware isolation
   - Physical servers are dedicated to your organization
   - VMs from scale sets run on these dedicated physical hosts

### Understanding the Relationship: Host Group vs. VM Scale Set

**They are SEPARATE but LINKED concepts:**

#### Host Group (Physical Infrastructure)
- **What it is**: A container for dedicated hosts (physical servers)
- **Purpose**: Provides the physical hardware where VMs will run
- **Contains**: One or more dedicated hosts (actual physical machines)
- **Always present**: Exists regardless of how many VMs are running

#### VM Scale Set (VM Management)
- **What it is**: A service that creates and manages VMs automatically
- **Purpose**: Handles auto-scaling (adding/removing VMs based on demand)
- **Contains**: Configuration and rules for VMs
- **Dynamic**: Number of VMs changes based on load

#### The Connection

**Step 1: Configuration (Setup Time)**
```
You create:
  1. Host Group 1 (with dedicated hosts inside)
  2. VMSS 1 (configured to TARGET Host Group 1)
     
The VMSS is told: "When you create VMs, place them on 
                   the dedicated hosts in Host Group 1"
```

**Step 2: Runtime (When Traffic Arrives)**
```
Low traffic:
  VMSS 1 has 2 VMs → Both placed on Dedicated Hosts in Host Group 1
  
High traffic:
  VMSS 1 scales to 10 VMs → All 10 placed on Dedicated Hosts in Host Group 1
  
Traffic drops:
  VMSS 1 scales down to 3 VMs → Only 3 VMs remain on Dedicated Hosts
  
Note: Host Group and Dedicated Hosts remain unchanged
```

#### Analogy

Think of it like a **parking lot and cars**:

```
Host Group = Parking Lot (fixed infrastructure)
  ├─ Dedicated Host 1 = Parking Spot A
  ├─ Dedicated Host 2 = Parking Spot B
  └─ Dedicated Host 3 = Parking Spot C

VMSS = Car Rental Service (manages vehicles)
  - Adds cars when demand is high
  - Removes cars when demand is low
  - All cars PARK in the assigned parking lot (Host Group)
  
The parking lot (Host Group) doesn't go away when cars leave.
The cars (VMs) are placed IN the parking spots (Dedicated Hosts).
```

#### Visual Example

```
Before VMSS Scales Out:
  Host Group 1
    ├─ Dedicated Host A  [VM1] [VM2]      ← 2 VMs running
    └─ Dedicated Host B  [empty]          ← No VMs yet

After VMSS Scales Out (more traffic):
  Host Group 1
    ├─ Dedicated Host A  [VM1] [VM2] [VM3] [VM4]  ← 4 VMs now
    └─ Dedicated Host B  [VM5] [VM6]              ← 2 VMs added

After VMSS Scales In (less traffic):
  Host Group 1
    ├─ Dedicated Host A  [VM1]            ← Only 1 VM left
    └─ Dedicated Host B  [empty]          ← VMs removed

Note: Host Group and Dedicated Hosts A & B never change!
```

#### Key Takeaway

**Host Group** = The **WHERE** (physical location/infrastructure)  
**VM Scale Set** = The **MANAGER** (decides how many VMs to create)  
**VMs** = Placed **ONTO** the dedicated hosts **INSIDE** the host group

The VMSS doesn't "contain" the Host Group. Instead, the VMSS is **configured** to deploy its VMs **to** the Host Group's dedicated hosts.

### Resiliency Guarantees

| Configuration | Zones | Can Survive |
|--------------|-------|-------------|
| Single zone | 1 | Datacenter failures only |
| Two zones | 2 | 1 zone failure |
| **Three zones** | **3** | **Up to 2 zone failures** ✅ |

---

## Practice Questions

### Question 1: High-Availability Solution with Dedicated Hosts (Litware Inc.)

**Scenario**: Refer to the Litware Inc. case study. You plan to migrate App1 to Azure. You need to recommend a high-availability solution for App1. The solution must meet the resiliency requirements.

**Resiliency Requirements for App1**:
- The app must be hosted in an Azure region that supports availability zones
- It must maintain availability even if two availability zones fail
- It must be hosted on Azure virtual machines that support automatic scaling
- It must be deployed to Azure dedicated hosts

**Question**: What should you include in the recommendation?

**Options**:

A) Number of host groups: 1  
   Number of virtual machine scale sets: 0

B) Number of host groups: 2  
   Number of virtual machine scale sets: 1

C) **Number of host groups: 3**  
   **Number of virtual machine scale sets: 3**

D) Number of host groups: 6  
   Number of virtual machine scale sets: 0

E) Number of host groups: 6  
   Number of virtual machine scale sets: 0

F) Number of host groups: 1  
   Number of virtual machine scale sets: 1

---

**Correct Answer**: **C) Number of host groups: 3, Number of virtual machine scale sets: 3**

---

### Explanation

**Why 3 Host Groups and 3 VM Scale Sets?**

This configuration is correct because it satisfies all the resiliency requirements:

- **VMs from the scale set are placed onto dedicated hosts** in the host group
- As demand increases/decreases, VMSS adds/removes VMs on the dedicated infrastructure
#### 1. **Survive Two Availability Zone Failures** ✅
configured to deploy its VMs onto dedicated hosts within the corresponding host group:

| Availability Zone | Host Group | Contains | VM Scale Set | VMs Placed |
|------------------|------------|----------|--------------|------------|
| Zone 1 | Host Group 1 | Dedicated Hosts 1-N | VMSS 1 | VMs deployed ONTO hosts in HG1 |
| Zone 2 | Host Group 2 | Dedicated Hosts 1-N | VMSS 2 | VMs deployed ONTO hosts in HG2 |
| Zone 3 | Host Group 3 | Dedicated Hosts 1-N | VMSS 3 | VMs deployed ONTO hosts in HG3 |

**Key Point**: The VM Scale Set doesn't "contain" the host group. Rather, the VMSS is **configured** to place its VM instances onto the dedicated hosts **within** the host group.
Initial: Zone 1 ✅ | Zone 2 ✅ | Zone 3 ✅
Failure 1: Zone 1 ❌ | Zone 2 ✅ | Zone 3 ✅ → Still Available
Failure 2: Zone 1 ❌ | Zone 2 ❌ | Zone 3 ✅ → Still Available
Result: App1 continues running in Zone 3


#### 2. **Dedicated Hosts with Zone Isolation** ✅

- **Host Groups** are logical containers for dedicated hosts
- **3 host groups** (one per zone) provide:
  - Hardware isolation per zone
  - Zone-level fault isolation
  - Compliance with dedicated infrastructure requirements

#### 3. **Automatic Scaling** ✅

- **Virtual Machine Scale Sets (VMSS)** provide automatic scaling
- **3 VM scale sets** (one per zone) enable:
  - Independent scaling in each zone
  - Zone-specific capacity management
  - Dynamic response to load changes

#### 4. **Zone-to-Host-Group Mapping**

Each VM scale set is deployed to its corresponding host group in a specific zone:

| Availability Zone | Host Group | VM Scale Set | Purpose |
|------------------|------------|--------------|---------|
| Zone 1 | Host Group 1 | VMSS 1 | Dedicated hosts + auto-scaling |
| Zone 2 | Host Group 2 | VMSS 2 | Dedicated hosts + auto-scaling |
| Zone 3 | Host Group 3 | VMSS 3 | Dedicated hosts + auto-scaling |

---

### Why Other Options Are Incorrect

**A) 1 host group, 0 VM scale sets** ❌
- **No zone redundancy**: Single zone deployment cannot survive any zone failures
- *Region
     ├─ Zone 1: Host Group 1 (contains Dedicated Hosts)
     │           └─ VMSS 1 (VMs placed ON hosts in HG1)
     │
     ├─ Zone 2: Host Group 2 (contains Dedicated Hosts)
     │           └─ VMSS 2 (VMs placed ON hosts in HG2)
     │contain dedicated hosts (physical servers) that meet regulatory requirements for hardware isolation while maintaining zone redundancy. VMSS instances are placed onto these dedicated hosts.

6. **Scaling with Dedicated Hosts**
   > When a VM scale set scales out, new VM instances are placed onto available capacity on the dedicated hosts within the specified host group. The dedicated hosts remain provisioned even when VMSS scales in.
     └─ Zone 3: Host Group 3 (contains Dedicated Hosts)
                 └─ VMSS 3 (VMs placed ON hosts in HG3)
    or auto-scaling requirements

**B) 2 host groups, 1 VM scale set** ❌
- **Insufficient zones**: Only 2 zones means can survive only 1 zone failure
- **Requirement**: Must survive 2 zone failures, which requires 3 zones
- **Single VMSS**: Cannot properly distribute across zones with dedicated hosts

**D & E) 6 host groups, 0 VM scale sets** ❌
- **Over-provisioned**: Only 3 availability zones exist, 6 host groups is unnecessary
- **No automatic scaling**: Without VMSS, cannot meet auto-scaling requirement
- **No clear benefit**: Additional host groups don't improve resiliency beyond 3 zones

**F) 1 host group, 1 VM scale set** ❌
- **No zone redundancy**: Single zone deployment
- **Cannot survive**: Any zone failure, let alone 2 zone failures
- **Does not meet**: Multi-zone resiliency requirement

---

### Key Takeaways

1. **3 Availability Zones = Maximum Resiliency**
   > To survive 2 zone failures in Azure, deploy across all 3 availability zones in the region

2. **Host Groups = Zone Mapping**
   > One host group per availability zone ensures dedicated hosts are zone-isolated

3. **VMSS = Auto-Scaling + HA**
   > Virtual machine scale sets provide both automatic scaling and high availability across zones

4. **Architecture Pattern**:
   ```
   3 Zones → 3 Host Groups → 3 VM Scale Sets
   Each VMSS mapped to its zone's host group
   Result: Survives up to 2 zone failures with auto-scaling
   ```

5. **Dedicated Hosts for Compliance**
   > Host groups + dedicated hosts meet regulatory requirements for hardware isolation while maintaining zone redundancy

---

### Question 2: Migrating On-Premises App with Custom COM Components

**Scenario**: You plan to move a web app named App1 from an on-premises data center to Azure.

**App Characteristics**:
- App1 depends on a custom COM component that is installed on the host server
- Must be available to users if an Azure data center becomes unavailable
- Costs must be minimized

**Question**: What should you include in the recommendation to host App1 in Azure?

**Options**:

A) In two Azure regions, deploy a load balancer and a web app

B) In two Azure regions, deploy a load balancer and a virtual machine scale set

C) **Deploy a load balancer and a virtual machine scale set across two availability zones**

D) In two Azure regions, deploy an Azure Traffic Manager profile and a web app

---

**Correct Answer**: **C) Deploy a load balancer and a virtual machine scale set across two availability zones**

---

### Explanation

**Why Load Balancer + VM Scale Set across Two Availability Zones?**

#### 1. **COM Component Requirement → Virtual Machines Required** ✅

- **Custom COM components** require Windows-based virtual machines
- **Azure App Service (Web Apps) does NOT support** custom COM components
- **VMs provide full OS access** needed to install and run COM components
- Options A and D are immediately eliminated due to using Web Apps

#### 2. **Data Center Availability → Availability Zones Provide Resiliency** ✅

**Availability Zones vs. Multiple Regions**:

| Approach | Availability | Cost | Complexity |
|----------|-------------|------|------------|
| **2 Availability Zones** | Survives datacenter failure | Lower | Simple |
| 2 Azure Regions | Survives regional failure | Higher | Complex |

- **Availability zones** are physically separate datacenters within a region
- Deploying across **2 zones** protects against datacenter-level failures
- Each zone has independent power, cooling, and networking
- Meets requirement: "available if an Azure data center becomes unavailable"

#### 3. **Cost Minimization → Single Region Deployment** ✅

**Cost Comparison**:

```
Single Region (2 Zones):
  ✅ Lower networking costs (intra-region traffic)
  ✅ Single load balancer
  ✅ Simplified management
  ✅ Lower data transfer costs

Multiple Regions:
  ❌ Higher networking costs (cross-region replication)
  ❌ Traffic Manager + multiple load balancers
  ❌ Complex data synchronization
  ❌ Higher data transfer costs
```

#### 4. **Architecture**

```
Azure Region (e.g., East US)
│
├─ Availability Zone 1
│  ├─ VM Scale Set Instance 1
│  ├─ VM Scale Set Instance 2
│  └─ [COM Component installed on each VM]
│
├─ Availability Zone 2
│  ├─ VM Scale Set Instance 3
│  ├─ VM Scale Set Instance 4
│  └─ [COM Component installed on each VM]
│
└─ Azure Load Balancer
   └─ Distributes traffic across both zones
```

**Benefits**:
- ✅ High availability across zones
- ✅ Auto-scaling with VMSS
- ✅ Load balancer distributes traffic
- ✅ Cost-effective single-region deployment
- ✅ Supports custom COM components

---

### Why Other Options Are Incorrect

**A) Two Azure regions, deploy a load balancer and a web app** ❌
- **Web Apps cannot host COM components** - This is the fundamental blocker
- Azure App Service has a managed environment without full OS access
- Custom COM components require Windows Server with full administrative control

**B) Two Azure regions, deploy a load balancer and a virtual machine scale set** ❌
- **Correct technology choice** (VMs support COM), but **wrong scope**
- Deploys across **multiple regions** → significantly higher cost
- **Violates cost minimization requirement**
- Cross-region deployment costs:
  - Cross-region data transfer fees
  - Duplicate infrastructure in each region
  - Complex geo-replication setup
- Availability zones provide sufficient datacenter resilience at lower cost

**D) Two Azure regions, deploy an Azure Traffic Manager profile and a web app** ❌
- **Traffic Manager** provides global load balancing across regions ✅
- **Web Apps** cannot run custom COM components ❌
- Same fundamental issue as Option A
- Even with global distribution, incompatible technology choice

---

### Key Takeaways

1. **COM Components = Virtual Machines Only**
   > Azure Web Apps operate in a managed sandbox environment and cannot install or run custom COM components. Full Windows Server VMs are required.

2. **Datacenter Availability = Availability Zones**
   > Availability zones provide datacenter-level resiliency within a region. Each zone is an independent facility with separate power, cooling, and networking.

3. **Cost Optimization = Avoid Multi-Region When Possible**
   > Multi-region deployments significantly increase costs through data transfer fees, duplicate infrastructure, and complex replication. Use availability zones for datacenter resiliency within a single region.

4. **VM Scale Sets = Automatic Scaling + High Availability**
   > VMSS provides both auto-scaling capabilities and the ability to distribute instances across availability zones, combining elasticity with resiliency.

5. **Load Balancer for Zone Distribution**
   > Azure Load Balancer distributes traffic across VMs in different availability zones, ensuring requests are served even if one zone fails.

---

### Question 3: SQL Server on Azure VMs - VM Series Selection

**Scenario**: You need to deploy an instance of SQL Server on Azure Virtual Machines. The solution must meet the following requirements:

- Support 15,000 disk IOPS
- Support SR-IOV (Single Root I/O Virtualization)
- Minimize costs

**Question**: What should you include in the solution for the virtual machine series?

**Options**:

A) **DS**

B) NC

C) NV

---

**Correct Answer**: **A) DS**

---

### Explanation

**Why DS-series Virtual Machines?**

#### 1. **High Disk IOPS Support** ✅

- **DS-series VMs** are optimized for disk-intensive workloads
- Support **Premium SSDs** capable of delivering high IOPS
- Can deliver well beyond 15,000 disk IOPS depending on VM size and disk configuration
- Ideal for database workloads like SQL Server that require high disk throughput

#### 2. **SR-IOV Support** ✅

- DS-series VMs support **SR-IOV (Single Root I/O Virtualization)**
- SR-IOV enables low-latency and high-throughput network performance
- Critical for database performance where network I/O matters
- Bypasses the hypervisor for network traffic, reducing latency

#### 3. **Cost-Effective** ✅

- DS-series are **general-purpose VMs**
- More cost-effective than specialized GPU or compute-intensive series
- Optimal price-to-performance ratio for SQL Server workloads
- No unnecessary features that inflate costs

---

### Why Other Options Are Incorrect

**B) NC-series** ❌

- **GPU-intensive compute workloads** - Designed for machine learning and AI model training
- **More expensive** than DS-series for database workloads
- **Not optimized for disk IOPS** or database workloads
- Overkill for SQL Server deployments with unnecessary GPU resources
- Poor fit for SQL Server performance requirements

**C) NV-series** ❌

- **Graphics-intensive applications** - Optimized for remote visualization using GPU acceleration
- **Not designed for high disk IOPS** or database hosting
- Results in **unnecessary cost** for SQL Server deployments
- **Suboptimal performance** for database workloads
- GPU acceleration provides no benefit for SQL Server

---

### Azure VM Series Overview for Database Workloads

| VM Series | Optimized For | Disk IOPS | SR-IOV | Cost | SQL Server Fit |
|-----------|---------------|-----------|--------|------|----------------|
| **DS-series** | Disk-intensive workloads | ✅ High | ✅ Yes | 💰 Moderate | ✅ Excellent |
| NC-series | GPU compute (ML/AI) | ❌ Not optimized | ✅ Yes | 💰💰💰 High | ❌ Poor |
| NV-series | Graphics/Visualization | ❌ Not optimized | ✅ Yes | 💰💰💰 High | ❌ Poor |
| E-series | Memory-intensive | ✅ High | ✅ Yes | 💰💰 Higher | ✅ Good |
| M-series | Memory-optimized (large DBs) | ✅ Very High | ✅ Yes | 💰💰💰 Highest | ✅ Large DBs |

---

### Key Takeaways

1. **DS-series = Balanced Performance for SQL Server**
   > DS-series VMs provide the optimal balance of disk IOPS, network performance (SR-IOV), and cost for SQL Server workloads.

2. **Premium SSD Support is Critical**
   > For high IOPS requirements (15,000+), Premium SSDs paired with DS-series VMs deliver consistent performance for database operations.

3. **Avoid GPU-Optimized Series for Databases**
   > NC-series (compute GPU) and NV-series (visualization GPU) add unnecessary cost without improving database performance.

4. **SR-IOV for Low-Latency Networking**
   > SR-IOV bypasses the hypervisor for network operations, critical for database workloads with high network I/O requirements.

5. **Cost Optimization = Right-Sizing**
   > Choosing the appropriate VM series (DS for disk-intensive workloads) avoids paying for unused GPU or specialized compute capabilities.

---

### Reference Links

- [Dv2 and DSv2-series Virtual Machines](https://learn.microsoft.com/en-us/azure/virtual-machines/dv2-dsv2-series)
- [Azure VM Sizes Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes)
- [NC-series Virtual Machines](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nc-series?tabs=sizebasic)
- [NV-series Virtual Machines](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nv-series?tabs=sizebasic)

---

### Reference Links

- [Migration Checklist When Moving to Azure App Service](https://azure.microsoft.com/en-us/blog/migration-checklist-when-moving-to-azure-app-service/)
- [.NET Application Migration to Azure](https://learn.microsoft.com/en-us/dotnet/azure/migration/app-service)
- [Azure Dedicated Hosts Overview](https://docs.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts)
- [Azure Dedicated Hosts - How To](https://docs.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts-how-to?tabs=portal%2Cportal2)
- [Virtual Machine Scale Sets with Availability Zones](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-use-availability-zones)
- [Azure Availability Zones](https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview)
- [SLA for Virtual Machines](https://azure.microsoft.com/en-us/support/legal/sla/virtual-machines/v1_9/)

---
