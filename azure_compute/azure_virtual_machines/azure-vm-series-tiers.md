# Azure Virtual Machine Series and Tiers

## Table of Contents

- [Overview](#overview)
- [VM Naming Convention](#vm-naming-convention)
- [General Purpose VMs](#general-purpose-vms)
- [Compute Optimized VMs](#compute-optimized-vms)
- [Memory Optimized VMs](#memory-optimized-vms)
- [Storage Optimized VMs](#storage-optimized-vms)
- [GPU Accelerated VMs](#gpu-accelerated-vms)
- [High Performance Compute (HPC)](#high-performance-compute-hpc)
- [Burstable VMs](#burstable-vms)
- [Confidential Computing VMs](#confidential-computing-vms)
- [VM Series Comparison](#vm-series-comparison)
- [Choosing the Right VM Series](#choosing-the-right-vm-series)

---

## Overview

Azure offers a wide variety of virtual machine sizes optimized for different workloads. Each VM series is designed to provide optimal performance for specific use cases, from general-purpose computing to specialized workloads like AI/ML training, high-performance computing, and graphics rendering.

### Key Factors in VM Selection

| Factor | Description |
|--------|-------------|
| **vCPU** | Number of virtual CPUs |
| **Memory** | Amount of RAM in GiB |
| **Temp Storage** | Local SSD storage for temporary data |
| **Max Data Disks** | Number of data disks that can be attached |
| **Max IOPS** | Input/Output operations per second |
| **Network Bandwidth** | Expected network throughput |
| **Premium Storage** | Support for Premium SSDs |
| **Accelerated Networking** | SR-IOV support for low-latency networking |

---

## VM Naming Convention

Azure VM names follow a specific pattern that indicates their capabilities:

```
[Family] + [Sub-family]* + [# of vCPUs] + [Constrained vCPUs]* + [Additive Features] + [Accelerator Type]* + [Version]

Example: Standard_D8s_v5
         │        │││ │
         │        │││ └─ Version 5
         │        ││└─── Premium storage capable (s)
         │        │└──── 8 vCPUs
         │        └───── D family (General Purpose)
         └────────────── Standard tier
```

### Common Suffixes

| Suffix | Meaning |
|--------|---------|
| **s** | Premium Storage capable |
| **d** | Local temp disk (NVMe or SCSI) |
| **i** | Isolated size (dedicated to single customer) |
| **l** | Low memory (less memory per vCPU) |
| **m** | Memory intensive (more memory per vCPU) |
| **t** | Tiny memory (least memory per vCPU) |
| **a** | AMD processor |
| **p** | ARM processor |
| **b** | Block storage performance |
| **C** | Confidential computing |

### Version Numbers

- **v2, v3, v4, v5**: Newer versions offer better price-performance
- Higher versions typically use newer generation processors
- Always prefer latest version for new deployments when available

---

## General Purpose VMs

General purpose VMs provide a balanced ratio of CPU to memory, suitable for a variety of workloads.

### D-Series (Dv2, Dv3, Dv4, Dv5, Dsv2, Dsv3, Dsv4, Dsv5)

**Best For**: Development/test environments, small-to-medium databases, low-to-medium traffic web servers

| Series | vCPU:Memory Ratio | Premium Storage | Temp Disk | Use Cases |
|--------|-------------------|-----------------|-----------|-----------|
| **Dv5** | 1:4 | No | No | General workloads |
| **Dsv5** | 1:4 | ✅ Yes | No | Production workloads |
| **Ddsv5** | 1:4 | ✅ Yes | ✅ NVMe | Workloads needing local temp storage |
| **Dasv5** | 1:4 | ✅ Yes | No | AMD-based, cost-effective |
| **Dpsv5** | 1:4 | ✅ Yes | No | ARM-based, best price-performance |

**Key Features**:
- ✅ Balanced CPU-to-memory ratio (1:4)
- ✅ SR-IOV / Accelerated Networking support
- ✅ Available in most regions
- ✅ Wide range of sizes (2 to 96 vCPUs)

### A-Series (Av2)

**Best For**: Entry-level workloads, development, test servers

| Series | vCPU:Memory Ratio | Premium Storage | Notes |
|--------|-------------------|-----------------|-------|
| **Av2** | Variable | ❌ No | Entry-level, economical |

**Key Features**:
- ✅ Cost-effective for basic workloads
- ❌ Limited performance compared to D-series
- ❌ No Premium Storage support

---

## Compute Optimized VMs

Compute optimized VMs have a high CPU-to-memory ratio, ideal for CPU-intensive workloads.

### F-Series (Fsv2)

**Best For**: Batch processing, gaming servers, analytics, CPU-intensive applications

| Series | vCPU:Memory Ratio | Premium Storage | Max vCPUs | Use Cases |
|--------|-------------------|-----------------|-----------|-----------|
| **Fsv2** | 1:2 | ✅ Yes | 72 | High CPU workloads |
| **Fasv6** | 1:2 | ✅ Yes | 64 | AMD-based compute |
| **Fpsv6** | 1:2 | ✅ Yes | 64 | ARM-based compute |

**Key Features**:
- ✅ Highest CPU-to-memory ratio
- ✅ Intel Turbo Boost Technology
- ✅ Best for compute-bound applications
- ✅ SR-IOV support

### Typical Workloads

- Web servers with high traffic
- Batch processing jobs
- Application servers
- Gaming servers
- Video encoding

---

## Memory Optimized VMs

Memory optimized VMs offer high memory-to-CPU ratios for memory-intensive workloads.

### E-Series (Ev3, Ev4, Ev5, Esv3, Esv4, Esv5)

**Best For**: Relational databases, medium-to-large caches, in-memory analytics

| Series | vCPU:Memory Ratio | Premium Storage | Max Memory | Use Cases |
|--------|-------------------|-----------------|------------|-----------|
| **Esv5** | 1:8 | ✅ Yes | 672 GiB | Databases, SAP |
| **Edsv5** | 1:8 | ✅ Yes | 672 GiB | Databases with temp storage |
| **Easv5** | 1:8 | ✅ Yes | 672 GiB | AMD-based, cost-effective |
| **Epsv5** | 1:8 | ✅ Yes | 208 GiB | ARM-based |

**Key Features**:
- ✅ High memory-to-vCPU ratio (1:8)
- ✅ Ideal for SQL Server, Oracle databases
- ✅ SR-IOV support
- ✅ Premium Storage support

### M-Series (Memory Intensive)

**Best For**: Very large databases, SAP HANA, mission-critical enterprise workloads

| Series | Max vCPUs | Max Memory | Premium Storage | Use Cases |
|--------|-----------|------------|-----------------|-----------|
| **Msv2** | 192 | 4 TB | ✅ Yes | SAP HANA, large DBs |
| **Mdsv2** | 192 | 4 TB | ✅ Yes | With local temp disk |
| **Mv2** | 416 | 12 TB | ✅ Yes | Largest memory VMs |

**Key Features**:
- ✅ Largest memory offerings in Azure
- ✅ Up to 12 TB RAM
- ✅ SAP HANA certified
- ✅ Mission-critical workloads
- ⚠️ Most expensive memory-optimized option

---

## Storage Optimized VMs

Storage optimized VMs provide high disk throughput and I/O for data-intensive workloads.

### L-Series (Lsv2, Lsv3)

**Best For**: Big data, SQL/NoSQL databases, data warehousing, large transactional databases

| Series | Local NVMe Storage | Max Throughput | Max IOPS | Use Cases |
|--------|-------------------|----------------|----------|-----------|
| **Lsv3** | Up to 7.68 TB | 5+ GB/s | 400K+ | High IOPS workloads |
| **Lasv3** | Up to 7.68 TB | 5+ GB/s | 400K+ | AMD-based |

**Key Features**:
- ✅ High local NVMe SSD storage
- ✅ Extremely high IOPS
- ✅ Low latency local storage
- ✅ Ideal for Cassandra, MongoDB, Elasticsearch

### Typical Workloads

- NoSQL databases (Cassandra, MongoDB, Redis)
- Data warehousing
- Large transactional databases
- Log analytics
- Search engines (Elasticsearch)

---

## GPU Accelerated VMs

GPU VMs are designed for compute-intensive, graphics-intensive, and visualization workloads.

### NC-Series (Compute GPU)

**Best For**: AI/ML training, deep learning, CUDA-based applications

| Series | GPU | GPU Memory | Use Cases |
|--------|-----|------------|-----------|
| **NCv3** | NVIDIA V100 | 16-32 GB | AI/ML training |
| **NCasT4_v3** | NVIDIA T4 | 16 GB | Inference, light training |
| **NC A100 v4** | NVIDIA A100 | 80 GB | Large-scale AI training |

**Key Features**:
- ✅ NVIDIA CUDA cores
- ✅ Tensor cores for AI acceleration
- ✅ NVLink for multi-GPU communication
- ❌ Not optimized for disk IOPS
- ❌ Higher cost than general-purpose VMs

### NV-Series (Visualization GPU)

**Best For**: Remote visualization, streaming, VDI, 3D rendering, graphics-intensive applications

| Series | GPU | GPU Memory | Use Cases |
|--------|-----|------------|-----------|
| **NVv3** | NVIDIA M60 | 8-16 GB | Virtual desktops, RemoteFX |
| **NVadsA10 v5** | NVIDIA A10 | 24 GB | Professional graphics |
| **NVsv3** | NVIDIA M60 | 8-16 GB | Streaming workloads |

**Key Features**:
- ✅ OpenGL and DirectX support
- ✅ NVIDIA GRID licensing
- ✅ Remote desktop experiences
- ✅ 3D visualization and CAD applications

### ND-Series (Deep Learning)

**Best For**: Large-scale deep learning training, HPC simulations

| Series | GPU | GPU Memory | Use Cases |
|--------|-----|------------|-----------|
| **NDv2** | 8x NVIDIA V100 | 256 GB total | Multi-GPU training |
| **ND A100 v4** | 8x NVIDIA A100 | 640 GB total | Largest AI workloads |

**Key Features**:
- ✅ Multiple high-end GPUs
- ✅ NVLink and NVSwitch interconnect
- ✅ InfiniBand networking
- ✅ Designed for distributed deep learning

---

## High Performance Compute (HPC)

HPC VMs are designed for computationally intensive workloads requiring high-speed networking.

### H-Series and HB-Series

**Best For**: Fluid dynamics, finite element analysis, molecular modeling, weather simulation

| Series | Max vCPUs | InfiniBand | Use Cases |
|--------|-----------|------------|-----------|
| **HBv4** | 176 | ✅ 400 Gb/s NDR | HPC, simulations |
| **HBv3** | 120 | ✅ 200 Gb/s HDR | MPI workloads |
| **HX** | 176 | ✅ 400 Gb/s NDR | Memory-bound HPC |

### HC-Series

**Best For**: Dense compute, financial modeling, seismic processing

| Series | Max vCPUs | InfiniBand | Use Cases |
|--------|-----------|------------|-----------|
| **HC** | 44 | ✅ 100 Gb/s EDR | Compute-intensive HPC |

**Key Features**:
- ✅ InfiniBand networking for MPI
- ✅ High memory bandwidth
- ✅ RDMA capable
- ✅ Ideal for tightly coupled parallel workloads

---

## Burstable VMs

Burstable VMs accumulate CPU credits during idle periods and use them for burst performance.

### B-Series (Bsv2, Basv2, Bpsv2)

**Best For**: Variable workloads, dev/test, small databases, microservices, low-traffic web servers

| Series | Processor | Premium Storage | Base CPU % | Use Cases |
|--------|-----------|-----------------|------------|-----------|
| **Bsv2** | Intel | ✅ Yes | Variable | General burstable |
| **Basv2** | AMD | ✅ Yes | Variable | AMD burstable |
| **Bpsv2** | ARM | ✅ Yes | Variable | ARM burstable |

### CPU Credit System

```
How B-Series Works:

Idle Time (Low CPU usage):
  └─ VM accumulates CPU credits
  └─ Credits stored for later use
  └─ Lower cost than consistent CPU VMs

Peak Time (High CPU demand):
  └─ VM consumes accumulated credits
  └─ Can burst to 100% CPU
  └─ Maintains performance during peaks

Credit Exhausted:
  └─ VM runs at baseline CPU level
  └─ Reduced performance until credits rebuild
```

### Credit Accumulation Example

| VM Size | Baseline CPU | Max Credits | Burst Duration at 100% |
|---------|-------------|-------------|------------------------|
| B2s | 40% | 60 credits | ~30 minutes |
| B4ms | 90% | 108 credits | ~1 hour |
| B8ms | 135% | 162 credits | Sustained burst |

**Key Features**:
- ✅ Most cost-effective for variable workloads
- ✅ Ideal for workloads with predictable peak periods
- ✅ CPU credits accumulate during idle times
- ⚠️ Performance drops when credits exhausted
- ⚠️ Not suitable for consistently high CPU workloads

### Best Practices for B-Series

1. **Monitor Credit Balance**: Use Azure Monitor to track CPU credits
2. **Right-size VMs**: Choose a size that maintains credits during typical usage
3. **Predictable Peaks**: Best for workloads like:
   - 8 AM - 9 AM business hours
   - Scheduled batch jobs
   - Development environments used during work hours

---

## Confidential Computing VMs

Confidential VMs provide hardware-based protection for data in use.

### DC-Series

**Best For**: Sensitive data processing, healthcare, financial services, regulatory compliance

| Series | Technology | TEE | Use Cases |
|--------|------------|-----|-----------|
| **DCsv2** | Intel SGX | SGX Enclaves | Sensitive computations |
| **DCsv3** | Intel SGX | SGX Enclaves | Larger enclave memory |
| **DCasv5** | AMD SEV-SNP | Full VM TEE | Confidential VMs |
| **DCadsv5** | AMD SEV-SNP | Full VM TEE | With local disk |
| **ECasv5** | AMD SEV-SNP | Memory optimized | Confidential databases |

**Key Features**:
- ✅ Hardware-based Trusted Execution Environment (TEE)
- ✅ Data encrypted in memory
- ✅ Protection from cloud operator access
- ✅ Attestation capabilities
- ✅ Regulatory compliance (HIPAA, GDPR)

---

## VM Series Comparison

### Quick Reference: Choosing by Workload

| Workload | Recommended Series | Key Feature |
|----------|-------------------|-------------|
| General web apps | D-series | Balanced CPU/memory |
| SQL Server | DS-series, E-series | Premium Storage, high IOPS |
| SAP HANA | M-series | Very high memory |
| AI/ML Training | NC-series, ND-series | NVIDIA GPUs |
| Remote Visualization | NV-series | Graphics GPU |
| Variable workloads | B-series | CPU credits, cost savings |
| Big Data / NoSQL | L-series | High local NVMe storage |
| HPC / Simulations | HB-series, HC-series | InfiniBand, RDMA |
| Confidential data | DC-series | Hardware TEE |
| Batch processing | F-series | High CPU ratio |

### Cost Comparison (Relative)

```
Most Expensive ──────────────────────────────────────── Least Expensive
    │                                                        │
    ▼                                                        ▼
 M-series   ND-series   NC-series   E-series   D-series   B-series
 (Memory)   (AI/ML)     (GPU)       (Memory)   (General)  (Burstable)
```

### Feature Support Matrix

| Series | Premium Storage | SR-IOV | Temp Disk Options | GPU | InfiniBand |
|--------|-----------------|--------|-------------------|-----|------------|
| D-series | ✅ (s variants) | ✅ | ✅ (d variants) | ❌ | ❌ |
| E-series | ✅ (s variants) | ✅ | ✅ (d variants) | ❌ | ❌ |
| F-series | ✅ | ✅ | ✅ | ❌ | ❌ |
| M-series | ✅ | ✅ | ✅ | ❌ | ❌ |
| L-series | ✅ | ✅ | ✅ (NVMe) | ❌ | ❌ |
| B-series | ✅ (s variants) | ✅ | ✅ | ❌ | ❌ |
| NC-series | ✅ | ✅ | ✅ | ✅ | Some |
| NV-series | ✅ | ✅ | ✅ | ✅ | ❌ |
| ND-series | ✅ | ✅ | ✅ | ✅ | ✅ |
| HB-series | ✅ | ✅ | ✅ | ❌ | ✅ |
| DC-series | ✅ | ✅ | ✅ (d variants) | ❌ | ❌ |

---

## Choosing the Right VM Series

### Decision Tree

```
Start
  │
  ├─ Need GPU?
  │   ├─ Yes → AI/ML Training? → NC-series, ND-series
  │   │        Graphics/VDI? → NV-series
  │   │
  │   └─ No → Continue ↓
  │
  ├─ Need very high memory (>1TB)?
  │   ├─ Yes → M-series
  │   └─ No → Continue ↓
  │
  ├─ Need high local storage IOPS?
  │   ├─ Yes → L-series
  │   └─ No → Continue ↓
  │
  ├─ Need InfiniBand / HPC?
  │   ├─ Yes → HB-series, HC-series
  │   └─ No → Continue ↓
  │
  ├─ Variable workload with peaks?
  │   ├─ Yes → B-series (Burstable)
  │   └─ No → Continue ↓
  │
  ├─ Memory-intensive (databases)?
  │   ├─ Yes → E-series
  │   └─ No → Continue ↓
  │
  ├─ Compute-intensive (CPU bound)?
  │   ├─ Yes → F-series
  │   └─ No → D-series (General Purpose)
```

### Cost Optimization Tips

1. **Use B-series** for development/test and variable workloads
2. **Reserved Instances** - Save up to 72% with 1 or 3-year commitments
3. **Spot VMs** - Up to 90% discount for interruptible workloads
4. **Right-size VMs** - Monitor and adjust based on actual usage
5. **Azure Hybrid Benefit** - Use existing Windows Server/SQL licenses
6. **Latest versions** - Newer series often have better price-performance

---

## Reference Links

- [Azure VM Sizes Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes)
- [General Purpose VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-general)
- [Compute Optimized VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-compute)
- [Memory Optimized VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-memory)
- [Storage Optimized VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-storage)
- [GPU Accelerated VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-gpu)
- [HPC VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-hpc)
- [B-series Burstable VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-b-series-burstable)
- [Confidential Computing VMs](https://learn.microsoft.com/en-us/azure/confidential-computing/virtual-machine-options)
- [VM Naming Conventions](https://learn.microsoft.com/en-us/azure/virtual-machines/vm-naming-conventions)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

---
