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

### Deployment Flow

```
Configuration:
  VMSS 1 (Zone 1) → configured to use → Host Group 1 → contains → Dedicated Hosts

Runtime:
  VMSS scales out → Creates VM → VM placed ON Dedicated Host
  VMSS scales in  → Removes VM → Dedicated Host remains available
```

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
```

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

### Reference Links

- [Azure Dedicated Hosts Overview](https://docs.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts)
- [Azure Dedicated Hosts - How To](https://docs.microsoft.com/en-us/azure/virtual-machines/dedicated-hosts-how-to?tabs=portal%2Cportal2)
- [Virtual Machine Scale Sets with Availability Zones](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-use-availability-zones)
- [Azure Availability Zones](https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview)
- [SLA for Virtual Machines](https://azure.microsoft.com/en-us/support/legal/sla/virtual-machines/v1_9/)

---
