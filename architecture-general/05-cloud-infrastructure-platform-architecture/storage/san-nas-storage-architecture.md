---
type: Architecture Pattern
title: "SAN and NAS: Storage Architecture Guide"
description: "**SAN (Storage Area Network)** and **NAS (Network Attached Storage)** are the two dominant enterprise network storage architectures. Both decouple physical storage from individual servers — enablin..."
tags: [cloud-infrastructure-platform-architecture]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# SAN and NAS: Storage Architecture Guide

> **Taxonomy Reference**: §5.2 Infrastructure Architecture  
> **Azure Implementation**: See [Azure Files](../../../architecture-azure/data/storage/07-azure-files-overview.md), [Azure Managed Disks](../../../architecture-azure/data/storage/)

## Table of Contents

- [Overview](#overview)
- [SAN — Storage Area Network](#san--storage-area-network)
  - [How SAN Works](#how-san-works)
  - [SAN Protocols](#san-protocols)
  - [SAN Topologies](#san-topologies)
- [NAS — Network Attached Storage](#nas--network-attached-storage)
  - [How NAS Works](#how-nas-works)
  - [NAS Protocols](#nas-protocols)
- [SAN vs. NAS: Key Differences](#san-vs-nas-key-differences)
- [Real-World Use Cases](#real-world-use-cases)
  - [SAN Use Cases](#san-use-cases)
  - [NAS Use Cases](#nas-use-cases)
- [On-Premises Deployments](#on-premises-deployments)
  - [On-Premises SAN](#on-premises-san)
  - [On-Premises NAS](#on-premises-nas)
- [Cloud Equivalents and Usages](#cloud-equivalents-and-usages)
  - [Cloud SAN Equivalents](#cloud-san-equivalents)
  - [Cloud NAS Equivalents](#cloud-nas-equivalents)
  - [Hybrid Architectures](#hybrid-architectures)
- [Decision Framework: SAN vs. NAS](#decision-framework-san-vs-nas)
- [Unified Storage Systems](#unified-storage-systems)
- [Summary](#summary)

---

## Overview

**SAN (Storage Area Network)** and **NAS (Network Attached Storage)** are the two dominant enterprise network storage architectures. Both decouple physical storage from individual servers — enabling centralized management, high availability, and scalable capacity — but they do so at different layers of the networking stack and serve different workload profiles.

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Storage Architecture Spectrum                  │
│                                                                      │
│  Direct-Attached     Network-Attached       Storage Area             │
│  Storage (DAS)       Storage (NAS)          Network (SAN)            │
│                                                                      │
│  Server ──── Disk    Server ──── NAS ───    Server ──── SAN          │
│              (local)       (file protocol)        (block protocol)   │
│                            CIFS / NFS              iSCSI / FC        │
└──────────────────────────────────────────────────────────────────────┘
```

| Attribute          | DAS               | NAS                    | SAN                       |
|--------------------|-------------------|------------------------|---------------------------|
| Access level       | Block (local)     | File                   | Block (network)           |
| Shared access      | No                | Yes                    | Yes                       |
| Protocol           | SATA, SAS, NVMe   | NFS, SMB/CIFS, AFP     | FC, iSCSI, FCoE, NVMe-oF  |
| Network required   | No                | Ethernet (LAN)         | Dedicated SAN fabric      |
| Complexity         | Low               | Medium                 | High                      |
| Cost               | Low               | Medium                 | High                      |

---

## SAN — Storage Area Network

A **Storage Area Network** is a dedicated high-speed network that provides block-level storage access to servers. From the perspective of the operating system, a SAN volume appears as a locally attached disk — the network transport is transparent.

### How SAN Works

```
┌─────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│  App Server │     │    SAN Fabric        │     │  Storage Array   │
│             │     │  (FC switches /      │     │                  │
│  OS sees a  │────▶│   iSCSI switches)    │────▶│  LUN 1  LUN 2   │
│  local disk │     │                      │     │  LUN 3  LUN 4   │
└─────────────┘     └──────────────────────┘     └──────────────────┘
                          Block I/O
```

1. The server's **Host Bus Adapter (HBA)** connects to the SAN fabric.
2. The SAN fabric routes **block-level I/O requests** to specific **Logical Unit Numbers (LUNs)** on the storage array.
3. The OS formats the LUN with a filesystem (NTFS, ext4, XFS) — the storage system itself has no knowledge of the filesystem.
4. Multiple servers can share the same SAN fabric but typically access **dedicated LUNs** (shared LUNs require a cluster filesystem such as OCFS2 or VMFS).

### SAN Protocols

| Protocol           | Transport     | Description                                                          |
|--------------------|---------------|----------------------------------------------------------------------|
| **Fibre Channel (FC)**  | FC fabric     | Purpose-built, low-latency, high-throughput. Gold standard for enterprise SAN. |
| **iSCSI**          | Ethernet / IP | SCSI commands encapsulated in TCP/IP. Lower cost, uses standard NICs. |
| **FCoE**           | Ethernet      | Fibre Channel frames over Ethernet — converged network adapters (CNAs). |
| **NVMe-oF**        | RDMA / TCP    | NVMe protocol over a fabric. Extremely low latency; emerging standard for all-flash arrays. |

### SAN Topologies

**Point-to-Point** — Direct single cable between one server and one storage array. Simple but not scalable.

```
┌────────────┐              ┌───────────────┐
│   Server   │──────────────│ Storage Array │
└────────────┘              └───────────────┘
```

---

**Arbitrated Loop (FC-AL)** — All devices share a single loop. Legacy; failure of one device can disrupt the loop.

```
         ┌────────────┐
    ┌────│   Server   │────┐
    │    └────────────┘    │
    │                      │
┌───────────────┐     ┌────────────┐
│ Storage Array │     │  Server 2  │
└───────────────┘     └────────────┘
    │                      │
    └──────────────────────┘
              Loop
```

---

**Switched Fabric (FC-SW)** — Each device connects to a dedicated FC switch port. Most common topology today; any device can communicate with any other through the fabric.

```
┌────────────┐    ┌────────────┐    ┌────────────┐
│  Server A  │    │  Server B  │    │  Server C  │
└──────┬─────┘    └──────┬─────┘    └──────┬─────┘
       │                 │                 │
       │    ┌────────────┴─────────────┐   │
       └────│     FC Switch (Fabric)   │───┘
            └────────────┬─────────────┘
                         │
              ┌──────────┴──────────┐
              │    Storage Array    │
              │   (LUN 1 / LUN 2)   │
              └─────────────────────┘
```

For production environments, always deploy **dual fabric** (two independent switches) so that a single switch failure does not interrupt storage access.

Each server has **two HBAs**: HBA-A connects to Switch A, and HBA-B connects to Switch B. Both switches independently reach the storage array (via Controller A and Controller B respectively).

```
        Server A                      Server B
  ┌──────────────────┐          ┌──────────────────┐
  │ HBA-A  │  HBA-B  │          │ HBA-A  │  HBA-B  │
  └───┬────┴────┬────┘          └───┬────┴────┬────┘
      │         │                   │         │
      │         │     (Fabric B)    │         │
      │         └───────────────────┼─────────┼──────┐
      │                             │         │      │
      │              (Fabric A)     │         │      │
      └─────────────────────────────┘         │      │
      │                                       │      │
      ▼  (HBA-A from both servers)            │      │
┌─────────────────────────────────┐           │      │
│     FC Switch A  (Fabric A)     │           │      │
└────────────────┬────────────────┘           │      │
                 │                            │      │
                 │                            ▼      ▼  (HBA-B from both servers)
                 │                 ┌─────────────────────────────────┐
                 │                 │     FC Switch B  (Fabric B)     │
                 │                 └────────────────┬────────────────┘
                 │                                  │
                 ▼                                  ▼
    ┌────────────────────────────────────────────────────┐
    │                   Storage Array                    │
    │                                                    │
    │  ┌──────────────────┐      ┌──────────────────┐   │
    │  │   Controller A   │      │   Controller B   │   │
    │  │  (Switch A port) │      │  (Switch B port) │   │
    │  └──────────────────┘      └──────────────────┘   │
    │                  shared disk pool                  │
    └────────────────────────────────────────────────────┘
```

**Path summary:**

| Server   | HBA   | → Switch      | → Storage Controller | Fabric  |
|----------|-------|---------------|----------------------|---------|
| Server A | HBA-A | FC Switch A   | Controller A         | Fabric A |
| Server A | HBA-B | FC Switch B   | Controller B         | Fabric B |
| Server B | HBA-A | FC Switch A   | Controller A         | Fabric A |
| Server B | HBA-B | FC Switch B   | Controller B         | Fabric B |

Multipathing software (MPIO on Windows, DM-Multipath on Linux) load-balances I/O across both active paths and automatically fails over to the surviving fabric if one switch or cable fails.

---

## NAS — Network Attached Storage

A **Network Attached Storage** device is a file server connected to a standard Ethernet network, exposing storage as shared **file system namespaces** (directories/shares) over standard file-sharing protocols.

### How NAS Works

```
┌─────────────┐
│  App Server │──── SMB/CIFS (Windows shares)  ──┐
└─────────────┘                                   │
┌─────────────┐                                   ▼
│  App Server │──── NFS (Linux/UNIX mounts) ───▶ NAS Device
└─────────────┘                                   (file system + storage)
┌─────────────┐
│  App Server │──── HTTP / S3-compatible ─────┘
└─────────────┘
```

1. The NAS device includes its own **OS and file system** (e.g., NetApp ONTAP, ZFS, Btrfs).
2. Clients mount remote shares — the NAS manages all file system operations including metadata, locking, and permissions.
3. Multiple clients can concurrently read and write the same directories with file-level locking.
4. NAS runs on standard **Ethernet/IP networks**, sharing bandwidth with other traffic unless dedicated interfaces are configured.

### NAS Protocols

| Protocol          | Port       | Use Case                                                  |
|-------------------|------------|-----------------------------------------------------------|
| **NFS v3/v4**     | TCP 2049   | Linux/UNIX workloads; stateless (v3) and stateful (v4)    |
| **SMB/CIFS**      | TCP 445    | Windows file shares; Active Directory integration         |
| **AFP**           | TCP 548    | Legacy Apple macOS environments                           |
| **iSCSI (block)** | TCP 3260   | Some NAS devices also serve block volumes (unified NAS)   |
| **S3-compatible** | TCP 443/80 | Object access layer over NAS (e.g., NetApp StorageGRID)   |
| **FTP/SFTP**      | TCP 21/22  | Simple file transfer; limited enterprise use              |

---

## SAN vs. NAS: Key Differences

| Dimension               | SAN                                            | NAS                                              |
|-------------------------|------------------------------------------------|--------------------------------------------------|
| **Access type**         | Block-level (raw disk)                         | File-level (directory/file paths)                |
| **OS/filesystem**       | Managed by the **server**                      | Managed by the **NAS device**                    |
| **Sharing model**       | Dedicated LUN per server (typically)           | Concurrent multi-client file sharing             |
| **Network**             | Dedicated SAN fabric (FC) or VLAN (iSCSI)     | Standard Ethernet LAN                            |
| **Latency**             | Sub-millisecond (FC); low (iSCSI)              | Higher (file protocol overhead)                  |
| **Throughput**          | Very high (8/16/32 Gbps FC, 25/100 GbE iSCSI) | High (1/10/25 GbE; limited by protocol overhead) |
| **Scalability**         | Scale to petabytes; complex                    | Scale to petabytes; simpler                      |
| **Cost**                | High (FC HBAs, FC switches, array)             | Lower (commodity Ethernet)                       |
| **Management**          | Complex (zoning, masking, multipathing)        | Simpler (share permissions, quotas)              |
| **Backup integration**  | Snapshot/clone at array level (very fast)      | Snapshot/clone; NFS/SMB-level backup agents      |
| **Primary workloads**   | Databases, VMs, high-IOPS apps                 | File collaboration, home directories, media      |

---

## Real-World Use Cases

### SAN Use Cases

#### Relational Databases (Oracle, SQL Server, PostgreSQL)
Databases require **predictable, low-latency block I/O**. SAN provides dedicated LUNs with guaranteed IOPS and sub-millisecond latency. Storage-level snapshots enable near-instant database backups without downtime.

```
Oracle RAC Cluster
  Node A ──┐
           ├── Shared LUN (ASM disk groups) ──▶ SAN Array
  Node B ──┘
  (Cluster filesystem coordinates shared block access)
```

#### VMware vSphere / Hyper-V Virtualization
VM hypervisors store VM disk images (VMDK, VHD) on SAN LUNs formatted with **VMFS** or **NTFS Cluster Shared Volumes (CSV)**. This enables:
- **vMotion / Live Migration** — move running VMs between hosts
- **High Availability** — restart VMs on surviving hosts after failure
- **Storage vMotion** — move VM disks between storage arrays with zero downtime

#### SAP HANA / ERP Systems
In-memory databases demand the highest IOPS and lowest latency available. All-flash SAN arrays with NVMe-oF provide the storage performance these workloads require.

#### High-Performance Computing (HPC)
Parallel workloads that write large sequential files at extreme throughput (simulation output, genomics pipelines).

---

### NAS Use Cases

#### Enterprise File Collaboration
Teams share project files, documents, and assets from a central NAS. Active Directory integration provides per-user/group permissions identical to local drives.

#### Home Directory and Profile Storage
User home directories mounted over NFS (Linux) or SMB (Windows) from a central NAS. Roaming profiles follow users across workstations.

#### Media Asset Management (MAM)
Video production workflows require large file repositories accessible by multiple editing workstations simultaneously. NAS with high-throughput NFS/SMB is the industry standard.

#### Software Development Shared Artifacts
Build outputs, container images, and compiled binaries shared across CI/CD agents via NFS mounts.

#### Backup Target (NFS/CIFS Backup Destinations)
Backup software (Veeam, Commvault, Veritas) targets NAS shares for secondary backup copies. NAS snapshots provide an additional local recovery tier.

#### Analytics / Data Lakes (On-Premises)
Raw data landing zones for Hadoop, Spark, or data science workflows ingesting CSV, Parquet, or JSON files over NFS.

---

## On-Premises Deployments

### On-Premises SAN

**Reference Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                  Production Data Center                 │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│  │ Server A │   │ Server B │   │ Server C │            │
│  │ (HBA ×2) │   │ (HBA ×2) │   │ (HBA ×2) │            │
│  └─────┬────┘   └────┬─────┘   └────┬─────┘            │
│        │              │              │                   │
│  ┌─────▼──────────────▼──────────────▼────┐             │
│  │        FC Switch Fabric (Dual)          │             │
│  │   Switch A ────────────── Switch B      │             │
│  └──────────────────┬───────────────────--┘             │
│                     │                                   │
│           ┌─────────▼─────────┐                         │
│           │   Storage Array   │                         │
│           │  (Dual Controller)│                         │
│           │  SSD / NVMe Tier  │                         │
│           │  HDD Capacity Tier│                         │
│           └───────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

**Key on-premises SAN vendors:**
- **Dell EMC PowerStore / PowerMax** — enterprise-grade, NVMe-oF
- **NetApp AFF (All Flash FAS)** — ONTAP OS; SAN + NAS unified
- **Pure Storage FlashArray** — 100% NVMe, Fibre Channel and iSCSI
- **HPE Alletra / Primera** — AI-driven storage, 100% NVMe
- **IBM FlashSystem** — NVMe end-to-end, data reduction

**Design considerations:**
- Always deploy **dual SAN fabric** (A-fabric and B-fabric) for redundancy
- Configure **multipathing** (MPIO on Windows, DM-Multipath on Linux) on all servers
- Use **zoning** (hard zoning by WWN) to isolate servers from unauthorized LUNs
- Size for peak IOPS and bandwidth, not just capacity
- Plan for **LUN masking** and access control from day one

---

### On-Premises NAS

**Reference Architecture:**

```
┌───────────────────────────────────────────────────────┐
│                Production Data Center                 │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Server A │  │ Server B │  │ Desktop  │            │
│  │ NFS mount│  │SMB share │  │ (SMB)    │            │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘            │
│        │             │              │                  │
│  ┌─────▼─────────────▼──────────────▼───┐             │
│  │       Core LAN / Storage VLAN         │             │
│  └──────────────────┬────────────────────┘            │
│                     │                                 │
│           ┌─────────▼──────────┐                      │
│           │   NAS Head (×2)    │                      │
│           │  Active-Active     │                      │
│           │  ONTAP / OneFS     │                      │
│           └─────────┬──────────┘                      │
│                     │                                 │
│           ┌─────────▼──────────┐                      │
│           │   Disk Shelf Pool  │                      │
│           │  (SSD + HDD tiers) │                      │
│           └────────────────────┘                      │
└───────────────────────────────────────────────────────┘
```

**Key on-premises NAS vendors:**
- **NetApp FAS / ONTAP** — industry-leading; unified NAS + SAN
- **Dell EMC Isilon (PowerScale)** — scale-out NAS for large unstructured data
- **Synology / QNAP** — SMB/mid-market NAS appliances
- **IBM Elastic Storage Server** — GPFS-based scale-out NAS for HPC
- **Windows Server with DFS-N** — software-defined NAS on commodity hardware

**Design considerations:**
- Deploy **NAS clusters** for active-active high availability
- Separate storage traffic onto a dedicated VLAN or physical network
- Configure **NFSv4.1 pNFS** for parallel file system access in high-performance scenarios
- Use **tiered storage** (SSD for hot data, HDD for warm/cold) to balance cost and performance
- Enable **deduplication and compression** for file server and backup workloads (typically 2–5× reduction)

---

## Cloud Equivalents and Usages

### Cloud SAN Equivalents

Cloud providers do not expose raw SAN infrastructure, but their **block storage services** are functionally equivalent to SAN LUNs.

| On-Premises SAN | Azure Equivalent              | AWS Equivalent        | GCP Equivalent        |
|-----------------|-------------------------------|-----------------------|-----------------------|
| LUN (HDD)       | Azure Managed Disk (Standard HDD) | EBS (sc1/st1)     | Persistent Disk (Standard) |
| LUN (SSD)       | Azure Managed Disk (Premium SSD) | EBS (gp3/io2)      | Persistent Disk (SSD) |
| LUN (Ultra)     | Azure Ultra Disk              | EBS (io2 Block Express) | Hyperdisk Extreme  |
| SAN Snapshot    | Azure Managed Disk Snapshot   | EBS Snapshot          | Persistent Disk Snapshot |
| SAN Clone       | Azure Managed Disk (from snapshot) | EBS (from AMI)   | Disk clone from snapshot |
| Shared LUN      | Azure Shared Disks            | EBS Multi-Attach      | Hyperdisk Multi-writer |

**Azure Ultra Disk** is the closest cloud equivalent to an all-flash SAN for latency-sensitive workloads:
- Sub-millisecond latency
- Up to 160,000 IOPS and 2,000 MB/s throughput per disk
- Dynamically adjustable IOPS/throughput without re-provisioning

```
Azure VM (SAP HANA)
  └─── Azure Ultra Disk (/hana/data)     → ~0.1ms latency, 160K IOPS
  └─── Azure Premium SSD (/hana/log)     → ~1ms latency, 20K IOPS
  └─── Azure Standard HDD (/hana/backup) → archival tier
```

---

### Cloud NAS Equivalents

Cloud-managed file services replicate NAS functionality as fully managed services.

| On-Premises NAS        | Azure Equivalent         | AWS Equivalent  | GCP Equivalent         |
|------------------------|--------------------------|-----------------|------------------------|
| SMB/CIFS share         | Azure Files (SMB)        | Amazon FSx for Windows | Filestore (SMB via GCVE) |
| NFS share              | Azure Files (NFS) / Azure NetApp Files | Amazon EFS / FSx for ONTAP | Filestore (NFS) |
| NetApp ONTAP           | Azure NetApp Files (ANF) | FSx for NetApp ONTAP | Cloud Volumes ONTAP |
| Isilon / PowerScale    | Azure Files (large-scale) | Amazon EFS      | Filestore Enterprise  |
| NAS snapshots          | ANF Snapshots / Azure Files snapshots | EFS Backups | Filestore Snapshots |

**Azure NetApp Files (ANF)** is the premium cloud NAS:

> **What is ANF?** Azure NetApp Files is a Microsoft Azure service that runs genuine NetApp ONTAP storage hardware inside Azure datacenters and exposes it as a fully managed NAS service. You provision a *capacity pool* (minimum 4 TiB), carve *volumes* from it, and mount those volumes over NFS or SMB — without managing any VMs, OS, or storage controllers. Because the underlying hardware is physical NetApp equipment (not virtualised commodity disks), ANF delivers the same sub-millisecond latency and enterprise data-management features (snapshots, clones, replication, deduplication) as an on-premises NetApp array.

- Fully managed NetApp ONTAP as a service
- Sub-millisecond latency (physical NetApp hardware in Microsoft datacenters)
- NFS v3/v4.1 and SMB 3.x protocols
- Service tiers: Standard (16 MB/s per TiB), Premium (64 MB/s per TiB), Ultra (128 MB/s per TiB)
- Supports SAP HANA, Oracle Database, AVD (Azure Virtual Desktop) profile shares

```
Azure Kubernetes Service (AKS)
  └─── PersistentVolumeClaim (ReadWriteMany)
       └─── Azure NetApp Files (NFS v4.1)
            ├─ Pod A reads /data/models/
            ├─ Pod B reads /data/models/      ← concurrent NFS access
            └─ Pod C writes /data/output/
```

---

### Hybrid Architectures

Many enterprises maintain on-premises SAN/NAS while extending to the cloud, creating hybrid storage fabrics.

#### Hybrid NAS: Cloud-Tiering

```
On-Premises NAS ──── Azure File Sync Agent ────▶ Azure Files (cloud tier)
   (hot files cached locally)                      (all files in cloud)
   
Hot files accessed locally at NAS speeds.
Cold files transparently recalled from Azure Files when accessed.
```

**Azure File Sync** enables on-premises Windows Server to act as a cache for Azure Files, tiering cold data to the cloud while keeping hot data local.

#### Hybrid SAN: Storage Replication

```
On-Premises SAN ──── ExpressRoute ────▶ Azure Site Recovery
(Primary LUNs)         (private link)      (replicated VMs)
                                           (Azure Managed Disks)
```

**Azure Site Recovery** replicates on-premises VM disk data (from SAN LUNs or DAS) to Azure Managed Disks for disaster recovery. RPO as low as 30 seconds for VMware workloads.

#### Cloud-Native Apps with NAS

```
App Service (Web App)
Container Apps
  └── Azure Files mount ──▶ SMB share (persistent state)
  
Azure Kubernetes Service
  └── PVC (ReadWriteMany) ──▶ Azure NetApp Files (NFS)
```

---

## Decision Framework: SAN vs. NAS

```
What type of data access does your workload require?
│
├── Raw block I/O (database files, VM disk images, swap) ──▶ SAN
│   ├── Latency < 1ms, > 50K IOPS?  ──▶ All-Flash SAN (FC or NVMe-oF)
│   ├── Latency 1-5ms, moderate IOPS? ──▶ iSCSI SAN or Cloud Block Storage
│   └── Cloud? ──▶ Premium/Ultra Managed Disk (Azure) / EBS io2 (AWS)
│
└── File sharing (multiple clients, named files, directories) ──▶ NAS
    ├── Windows clients / Active Directory? ──▶ SMB/CIFS NAS
    ├── Linux/UNIX workloads? ──▶ NFS NAS
    ├── Both protocols? ──▶ Unified NAS (NetApp, ANF)
    ├── Very large unstructured data? ──▶ Scale-out NAS (Isilon / EFS)
    └── Cloud? ──▶ Azure Files / Azure NetApp Files / Amazon EFS
```

| Scenario                                | Recommended  | Why                                                   |
|-----------------------------------------|--------------|-------------------------------------------------------|
| Oracle / SQL Server database            | SAN          | Block-level access, max IOPS, storage snapshots       |
| VMware vSphere VMs                      | SAN          | VMFS shared storage; vMotion and HA                   |
| SAP HANA                                | SAN (or ANF) | Sub-ms latency required; ANF certified for SAP HANA   |
| Windows file server                     | NAS (SMB)    | Multi-user file sharing with AD permissions           |
| Linux build/CI servers (shared code)    | NAS (NFS)    | Concurrent read/write, simple POSIX semantics         |
| Video editing shared storage            | NAS (NFS)    | Large sequential reads; multi-editor concurrent access|
| Kubernetes persistent shared volumes    | NAS (NFS)    | ReadWriteMany PVCs require file protocol              |
| Disaster recovery / cloud bursting      | Cloud block  | Azure Managed Disks replicated via ASR                |
| Home directories / user profiles        | NAS (SMB)    | Roaming profiles, per-user quotas                     |
| Backup target                           | NAS          | Dedup/compression; backup software NAS integration    |

---

## Unified Storage Systems

Modern enterprise storage arrays often provide **both** SAN block and NAS file access from the same hardware platform, eliminating the need to choose one exclusively.

**NetApp ONTAP** is the canonical example:
- Single storage OS managing SAN (iSCSI, FC, NVMe-oF) and NAS (NFS, SMB) simultaneously
- Shared storage pool with independent performance tiers
- Single management plane (ONTAP System Manager, REST API)
- Available on-premises (AFF/FAS) and in the cloud as Azure NetApp Files or Amazon FSx for NetApp ONTAP

```
NetApp ONTAP Unified Array
  ├── SAN LUNs ──▶ iSCSI / FC / NVMe-oF ──▶ Database servers, VMware ESXi
  └── NAS Volumes ──▶ NFS / SMB ──▶ Linux app servers, Windows file server
       (same underlying storage pool — capacity shared)
```

**Other unified systems:** Dell EMC PowerStore, HPE Alletra, IBM FlashSystem

---

## Summary

| Factor               | Choose SAN                                  | Choose NAS                                      |
|----------------------|---------------------------------------------|-------------------------------------------------|
| Access model         | Block (raw disk semantics)                  | File (path/directory semantics)                 |
| Workload type        | Databases, VM images, high-IOPS apps        | File shares, collaboration, backup targets      |
| Concurrency          | One server per LUN (unless cluster FS)      | Many clients per share simultaneously           |
| Latency requirement  | Sub-millisecond                             | Low milliseconds acceptable                     |
| Protocol knowledge   | Fibre Channel, iSCSI, NVMe-oF              | NFS, SMB/CIFS                                   |
| Infrastructure cost  | Higher (FC HBAs, dedicated fabric)          | Lower (standard Ethernet)                       |
| Cloud equivalent     | Managed Disks / EBS / Persistent Disk       | Azure Files / ANF / EFS / Filestore             |
| Managed cloud option | Azure Ultra/Premium Disk                    | Azure NetApp Files, Azure Files                 |

Both technologies have evolved significantly: on-premises SAN and NAS are now predominantly **all-flash**, while cloud-managed equivalents abstract away hardware entirely. For greenfield cloud deployments, block and file storage services deliver comparable performance with zero infrastructure management overhead.

---

*Related: [Azure Files Overview](../../../architecture-azure/data/storage/07-azure-files-overview.md) | [Azure Storage Redundancy](../../../architecture-azure/data/storage/01-azure-storage-redundancy-options.md)*
