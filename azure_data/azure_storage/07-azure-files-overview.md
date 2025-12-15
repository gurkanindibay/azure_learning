# Azure Files Overview

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Protocols](#protocols)
  - [SMB Protocol](#smb-protocol)
  - [NFS Protocol](#nfs-protocol)
- [Storage Tiers](#storage-tiers)
  - [Premium Tier](#premium-tier)
  - [Transaction Optimized Tier](#transaction-optimized-tier)
  - [Hot Tier](#hot-tier)
  - [Cool Tier](#cool-tier)
  - [Storage Tier Comparison](#storage-tier-comparison)
- [Supported Operating Systems](#supported-operating-systems)
- [Mounting Azure File Shares](#mounting-azure-file-shares)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Use Cases](#use-cases)
- [Azure Files vs Azure Blob Storage](#azure-files-vs-azure-blob-storage)
- [Key Takeaways](#key-takeaways)
- [References](#references)

## Overview

Azure Files offers **fully managed file shares in the cloud** that are accessible via industry-standard protocols. Azure file shares can be mounted concurrently by cloud or on-premises deployments, making them ideal for shared storage scenarios.

**Key Benefits:**
- Fully managed (no need to manage hardware or OS)
- Shared access across multiple VMs and applications
- Familiar file system interface
- Cross-platform support
- Hybrid cloud scenarios with Azure File Sync

## Key Features

| Feature | Description |
|---------|-------------|
| **Fully Managed** | No need to manage hardware, OS, or patches |
| **Shared Access** | Multiple clients can access simultaneously |
| **Familiar Interface** | Standard file system APIs work as expected |
| **Resilient** | Built for high availability |
| **Programmable** | REST API, client libraries, Azure CLI, PowerShell |
| **Hybrid Support** | Azure File Sync for on-premises caching |

## Protocols

Azure Files supports two industry-standard file sharing protocols:

### SMB Protocol

**Server Message Block (SMB)** is the most commonly used protocol for Azure Files.

- **Versions supported**: SMB 2.1, SMB 3.0, SMB 3.1.1
- **Encryption**: SMB 3.0+ supports encryption in transit
- **Port**: 445 (must be open for mounting)
- **Authentication**: Storage account key, Azure AD Domain Services, on-premises AD DS

### NFS Protocol

**Network File System (NFS)** is supported for Linux workloads.

- **Version**: NFS 4.1
- **Authentication**: Host-based authentication using virtual network rules
- **Use case**: Linux applications requiring POSIX-compliant file system
- **Requirement**: Premium file shares only

| Protocol | Windows | Linux | macOS | Premium Required |
|----------|---------|-------|-------|------------------|
| **SMB** | ✅ | ✅ | ✅ | No |
| **NFS** | ❌ | ✅ | ❌ | Yes |

## Storage Tiers

Azure Files offers different storage tiers optimized for various workload requirements, performance needs, and cost considerations. Understanding these tiers is crucial for selecting the right solution for your use case.

### Premium Tier

**Premium tier** is the highest performance tier, designed for **performance-sensitive and transaction-intensive workloads**.

**Key Characteristics:**
- **Storage Type**: SSD-backed storage (solid-state drives)
- **Performance**: Low latency, high IOPS, consistent throughput
- **Redundancy**: Supports **LRS (Locally Redundant Storage)** and **ZRS (Zone-Redundant Storage)**
- **Use Cases**: 
  - Transaction-intensive applications
  - High-performance databases
  - On-premises applications requiring fast and frequent access
  - Latency-sensitive workloads
- **Billing**: Based on provisioned capacity (you pay for what you provision, not what you use)

**Why Premium for Transaction-Intensive Workloads?**

Premium tier is specifically optimized for scenarios where low latency and high throughput are critical. The SSD-backed infrastructure ensures:
- **Consistent Performance**: Predictable and low-latency responses
- **High IOPS**: Ideal for applications with frequent read/write operations
- **Maximum Resiliency**: ZRS provides highest availability within a region, protecting data even if an entire availability zone fails

### Transaction Optimized Tier

**Transaction optimized tier** is designed for **workloads with high transaction rates** but can tolerate slightly higher latency compared to Premium.

**Key Characteristics:**
- **Storage Type**: HDD-backed storage (hard disk drives)
- **Performance**: Good for frequently accessed files, but with higher latency than Premium
- **Redundancy**: Supports **LRS, ZRS, GRS (Geo-Redundant Storage), and GZRS (Geo-Zone-Redundant Storage)**
- **Use Cases**:
  - Web applications
  - File shares with moderate transaction requirements
  - Team collaboration and file sharing
- **Billing**: Pay for storage used + per-transaction costs

**Comparison with Premium:**
- ✅ **More cost-effective** for moderate workloads
- ❌ **Higher latency** due to HDD-backed storage
- ❌ **Lower IOPS** compared to Premium
- ✅ **Better redundancy options** (includes GRS and GZRS)

### Hot Tier

**Hot tier** is optimized for **general-purpose file shares** with regular access patterns.

**Key Characteristics:**
- **Storage Type**: HDD-backed storage
- **Performance**: Balanced performance for frequently accessed data
- **Redundancy**: Supports **LRS, ZRS, GRS, and GZRS**
- **Use Cases**:
  - Active data that is accessed regularly but not transaction-intensive
  - General-purpose file shares
  - Departmental file shares
- **Billing**: Pay for storage used + per-transaction costs (lower storage costs than transaction optimized)

### Cool Tier

**Cool tier** is designed for **infrequently accessed data** where storage cost optimization is a priority.

**Key Characteristics:**
- **Storage Type**: HDD-backed storage
- **Performance**: Lower performance expectations for infrequently accessed data
- **Redundancy**: Supports **LRS, ZRS, GRS, and GZRS**
- **Use Cases**:
  - Archival data
  - Long-term backup storage
  - Compliance and retention data
- **Billing**: Lowest storage cost + higher per-transaction costs

### Storage Tier Comparison

| Feature | Premium | Transaction Optimized | Hot | Cool |
|---------|---------|----------------------|-----|------|
| **Storage Medium** | SSD | HDD | HDD | HDD |
| **Latency** | Lowest | Moderate | Moderate | Higher |
| **IOPS** | Highest | Good | Moderate | Lower |
| **Storage Cost** | Highest | Moderate-High | Moderate | Lowest |
| **Transaction Cost** | Included in provisioning | Per transaction | Per transaction | Highest per transaction |
| **Redundancy Options** | LRS, ZRS | LRS, ZRS, GRS, GZRS | LRS, ZRS, GRS, GZRS | LRS, ZRS, GRS, GZRS |
| **Provisioned Model** | Yes | No (pay-as-you-go) | No (pay-as-you-go) | No (pay-as-you-go) |
| **NFS Support** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Best For** | Transaction-intensive, low-latency workloads | Frequently accessed files | General-purpose file shares | Infrequently accessed data |

---

### Practice Question: Storage Tier for Transaction-Intensive Workloads

**Scenario:**
You plan to create an Azure storage account that will host file shares. The shares will be accessed from on-premises applications that are **transaction-intensive**.

You need to recommend a solution to **minimize latency** when accessing the file shares. The solution must provide the **highest level of resiliency** for the selected storage tier.

**Question:**
What storage tier should you recommend?

**Options:**
1. ❌ **Hot**
2. ✅ **Premium**
3. ❌ **Transaction optimized**

**Answer: Premium**

**Explanation:**

**Premium is correct** because:
1. **Performance-Optimized**: Premium tier is designed specifically for **performance-sensitive and transaction-intensive workloads**
2. **SSD-Backed Storage**: Uses solid-state drives (SSDs) which provide:
   - **Low latency** (critical for on-premises applications)
   - **High IOPS** (ideal for transaction-intensive workloads)
   - **Consistent throughput**
3. **Highest Resiliency**: Premium tier supports **ZRS (Zone-Redundant Storage)**, which provides the **highest level of resiliency within a region**. ZRS replicates data synchronously across three Azure availability zones, ensuring high availability even if an entire zone goes down.
4. **Predictable Performance**: Provisioned capacity model ensures consistent performance characteristics

**Why Other Options Are Incorrect:**

❌ **Hot is incorrect** because:
- While Hot tier IS available for Azure Files, it is **HDD-backed storage**, not SSD-backed
- It offers relatively low storage costs for frequently accessed data, but does **not provide the low latency** required for transaction-intensive workloads
- Hot tier is designed for **general-purpose file shares** with regular (but not intensive) access patterns
- It cannot deliver the **high IOPS and consistent throughput** needed for on-premises transaction-intensive applications
- The performance characteristics are similar to Transaction Optimized tier, making it unsuitable for performance-critical scenarios

❌ **Transaction optimized is incorrect** because:
- Although it's suitable for **frequently accessed file shares**, it is backed by **HDDs (hard disk drives)**, not SSDs
- HDDs offer **lower performance and higher latency** compared to SSD-backed Premium tier
- It's **more cost-effective** but does **not match the performance** required for transaction-intensive workloads
- While it supports ZRS for resiliency, the **performance characteristics don't meet the low-latency requirement**

**Key Takeaway:**
For **transaction-intensive workloads with low-latency requirements**, always choose **Premium tier** with **ZRS** for the best combination of performance and resiliency. Transaction optimized and Hot tiers, while more cost-effective, cannot deliver the same level of performance due to their HDD-backed storage infrastructure.

**References:**
- [Azure Blob Storage Access Tiers](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview)
- [Azure Storage Account Overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)
- [Azure Files Storage Tiers](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-planning#storage-tiers)

---

### Practice Question: Business Continuity for On-premises File Server

**Scenario:**
You have an on-premises network and an Azure subscription. The on-premises network has several branch offices.

A branch office in Toronto contains a virtual machine named **VM1** that is configured as a file server. Users access the shared files on **VM1** from all offices.

You need to recommend a solution to ensure that the users can access the shared files as quickly as possible if the Toronto branch office is inaccessible.

**Question:**
What should you include in the recommendation?

**Options:**
- a Recovery Services vault and Windows Server Backup
- **an Azure file share and Azure File Sync**
- a Recovery Services vault and Azure Backup
- Azure blob containers and Azure File Sync

**Answer: an Azure file share and Azure File Sync**

**Explanation:**

- **Azure File Sync is correct** because it allows you to replicate on-premises file server data (like **VM1** in Toronto) to an **Azure file share**, enabling centralized cloud storage with local caching servers at other branch offices. If the Toronto branch becomes inaccessible, users can access the files directly from Azure or from another on-premises server that has Azure File Sync configured as a cache/replica, providing high availability and low-latency access across locations.

- **A Recovery Services vault and Windows Server Backup is incorrect** because this combination provides backups for point-in-time recovery and disaster recovery, but it does not provide continuous synchronization or immediate file sharing across branches.

- **A Recovery Services vault and Azure Backup is incorrect** because Azure Backup protects VM1’s data for restore scenarios but does not enable real-time sync or continuous availability for user access.

- **Azure blob containers and Azure File Sync is incorrect** because Azure File Sync works only with **Azure file shares**, not blob containers. Blob storage is optimized for object storage and does not natively support Windows file system semantics or File Sync integration.

**References:**

- https://learn.microsoft.com/en-us/azure/storage/files/storage-sync-files-deployment-guide
- https://learn.microsoft.com/en-us/azure/storage/files/storage-files-introduction
- https://learn.microsoft.com/en-us/azure/backup/backup-overview
- https://learn.microsoft.com/en-us/azure/backup/backup-azure-recovery-services-vault-overview

**Domain:** Design Business Continuity Solutions

---

## Supported Operating Systems

Azure Files SMB file shares are accessible from **Windows, Linux, and macOS** clients.

| Operating System | SMB Support | NFS Support | Notes |
|------------------|-------------|-------------|-------|
| **Windows** | ✅ Yes | ❌ No | Windows 7+ (SMB 2.1+), Windows 8.1+ recommended (SMB 3.0) |
| **Linux** | ✅ Yes | ✅ Yes | Most distributions with CIFS or NFS support |
| **macOS** | ✅ Yes | ❌ No | macOS 10.11 (El Capitan)+ |

### Important Notes:

- **Windows**: Requires port 445 to be open (some ISPs block this port)
- **Linux**: Use `cifs-utils` package for SMB, native NFS support for NFS shares
- **macOS**: Native SMB support via Finder or command line
- **Mobile (Android/iOS)**: Not natively supported for direct mounting

---

### Practice Question: Azure Files Supported Operating Systems

**Question:**
Which operating systems can mount an external drive using Azure File Share?

**Options:**
1. ❌ Windows Only
2. ❌ Windows and Linux Only
3. ✅ Windows, Linux and macOS
4. ❌ Android and iOS Only

**Answer: Windows, Linux and macOS**

**Explanation:**
Azure Files offers fully managed file shares in the cloud that are accessible via the industry standard **Server Message Block (SMB)** protocol or **Network File System (NFS)** protocol. Azure file shares can be mounted concurrently by cloud or on-premises deployments.

**Azure Files SMB file shares are accessible from Windows, Linux, and macOS clients.**

- ✅ **Windows**: Full SMB support (Windows 7 and later)
- ✅ **Linux**: SMB support via CIFS, NFS support for Premium shares
- ✅ **macOS**: SMB support (macOS 10.11 El Capitan and later)
- ❌ **Android/iOS**: Not supported for direct file share mounting

**Reference:** [Introduction to Azure Files](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-introduction)

---

## Mounting Azure File Shares

### Windows

```powershell
# Mount Azure File Share on Windows
$connectTestResult = Test-NetConnection -ComputerName <storage-account>.file.core.windows.net -Port 445
if ($connectTestResult.TcpTestSucceeded) {
    # Mount the drive
    net use Z: \\<storage-account>.file.core.windows.net\<share-name> /user:Azure\<storage-account> <storage-account-key>
}
```

Or using PowerShell cmdlet:
```powershell
# Using New-PSDrive
$storageAccountKey = "<storage-account-key>"
$storageAccountName = "<storage-account>"
$shareName = "<share-name>"

$connectTestResult = Test-NetConnection -ComputerName "$storageAccountName.file.core.windows.net" -Port 445
if ($connectTestResult.TcpTestSucceeded) {
    cmd.exe /C "cmdkey /add:`"$storageAccountName.file.core.windows.net`" /user:`"Azure\$storageAccountName`" /pass:`"$storageAccountKey`""
    New-PSDrive -Name Z -PSProvider FileSystem -Root "\\$storageAccountName.file.core.windows.net\$shareName" -Persist
}
```

### Linux

```bash
# Install cifs-utils (for SMB)
sudo apt-get install cifs-utils

# Create mount point
sudo mkdir /mnt/azurefiles

# Mount the share
sudo mount -t cifs //<storage-account>.file.core.windows.net/<share-name> /mnt/azurefiles \
    -o vers=3.0,username=<storage-account>,password=<storage-account-key>,dir_mode=0777,file_mode=0777,serverino

# For persistent mount, add to /etc/fstab
//<storage-account>.file.core.windows.net/<share-name> /mnt/azurefiles cifs vers=3.0,username=<storage-account>,password=<storage-account-key>,dir_mode=0777,file_mode=0777 0 0
```

For NFS (Premium shares only):
```bash
# Mount NFS share
sudo mount -t nfs <storage-account>.file.core.windows.net:/<storage-account>/<share-name> /mnt/azurefiles -o vers=4,minorversion=1,sec=sys
```

### macOS

```bash
# Mount using Finder
# Go > Connect to Server (Cmd+K)
# Enter: smb://<storage-account>.file.core.windows.net/<share-name>
# Use storage account name as username and storage account key as password

# Or using command line
mount_smbfs //Azure@<storage-account>.file.core.windows.net/<share-name> /Volumes/azurefiles
```

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Lift and Shift** | Migrate on-premises apps that rely on file shares |
| **Shared Application Settings** | Store configuration files accessed by multiple VMs |
| **Diagnostic Data** | Centralize logs and metrics from multiple sources |
| **Dev/Test** | Share tools and utilities across development environments |
| **Containerization** | Persistent storage for containers (AKS, ACI) |
| **Hybrid Scenarios** | Extend on-premises file servers with Azure File Sync |

## Azure Files vs Azure Blob Storage

| Feature | Azure Files | Azure Blob Storage |
|---------|-------------|-------------------|
| **Access Method** | SMB/NFS (file system) | REST API (object storage) |
| **Structure** | Hierarchical (folders/files) | Flat (containers/blobs) |
| **Mounting** | ✅ Direct mount as drive | ❌ No direct mounting |
| **Use Case** | File shares, lift-and-shift | Large-scale unstructured data |
| **POSIX Support** | ✅ Yes (NFS) | ❌ No |
| **Maximum File Size** | 4 TiB (SMB), 4 TiB (NFS) | 190.7 TiB (block blob) |

## Key Takeaways

1. **Cross-Platform Support**: Azure Files SMB shares work on **Windows, Linux, and macOS**
2. **Two Protocols**: SMB (all platforms) and NFS (Linux only, Premium tier)
3. **Port 445 Required**: SMB requires port 445 to be open
4. **Fully Managed**: No infrastructure to maintain
5. **Concurrent Access**: Multiple clients can access the same share simultaneously
6. **Mobile Not Supported**: Android and iOS cannot directly mount Azure File shares

## References

- [Introduction to Azure Files](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-introduction)
- [Mount SMB Azure file share on Windows](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-windows)
- [Mount SMB Azure file share on Linux](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-linux)
- [Mount SMB Azure file share on macOS](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-mac)
- [Azure Files pricing](https://azure.microsoft.com/en-us/pricing/details/storage/files/)
