# Azure Files Overview

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Protocols](#protocols)
  - [SMB Protocol](#smb-protocol)
  - [NFS Protocol](#nfs-protocol)
- [Authentication Mechanisms](#authentication-mechanisms)
  - [Supported Authentication Methods](#supported-authentication-methods)
  - [Authentication Method Details](#authentication-method-details)
  - [Authentication Methods NOT Supported](#authentication-methods-not-supported)
- [Storage Tiers](#storage-tiers)
  - [Premium Tier](#premium-tier)
  - [Transaction Optimized Tier](#transaction-optimized-tier)
  - [Hot Tier](#hot-tier)
  - [Cool Tier](#cool-tier)
  - [Storage Tier Comparison](#storage-tier-comparison)
- [Data Protection and Recovery](#data-protection-and-recovery)
  - [Azure File Share Snapshots](#azure-file-share-snapshots)
  - [Soft Delete for File Shares](#soft-delete-for-file-shares)
  - [Data Protection Features NOT Applicable to Azure Files](#data-protection-features-not-applicable-to-azure-files)
- [Supported Operating Systems](#supported-operating-systems)
- [Mounting Azure File Shares](#mounting-azure-file-shares)
  - [Network Requirements](#network-requirements)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Use Cases](#use-cases)
- [Azure Files vs Azure Blob Storage](#azure-files-vs-azure-blob-storage)
- [Azure Files vs Azure NetApp Files](#azure-files-vs-azure-netapp-files)
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

## Authentication Mechanisms

Azure Files supports multiple authentication mechanisms for secure access to your file shares. Understanding which methods are supported is crucial for designing secure storage solutions.

### Supported Authentication Methods

| Authentication Method | Supported | Description |
|-----------------------|-----------|-------------|
| **Microsoft Entra Domain Services** | ✅ Yes | Allows Azure VMs to join a domain and use domain credentials to access Azure Files |
| **On-premises AD DS** | ✅ Yes | Extends on-premises Active Directory to Azure for seamless authentication |
| **Storage Account Keys** | ✅ Yes | Full access authentication using storage account keys |
| **Azure RBAC** | ✅ Yes | Role-based access control for granular permissions on Azure Files |
| **Shared Access Signature (SAS)** | ❌ No | Not supported for Azure Files authentication |
| **Shared Key Authorization** | ❌ No | Not supported by Azure Files |

### Authentication Method Details

#### Microsoft Entra Domain Services

**Microsoft Entra Domain Services** (formerly Azure AD Domain Services) provides managed domain services for Azure, enabling you to:
- Join Azure virtual machines to a domain without deploying domain controllers
- Use domain credentials (username/password) to access Azure file shares
- Apply Group Policy and LDAP support for enterprise scenarios

**Use Case:** Ideal for organizations that want cloud-native domain services without maintaining on-premises AD infrastructure.

#### On-premises Active Directory Domain Services (AD DS)

**On-premises AD DS** integration allows you to:
- Extend your existing on-premises Active Directory environment to Azure
- Use the same domain credentials for both on-premises and Azure file access
- Maintain consistent identity management across hybrid environments
- Leverage existing Group Policies and access controls

**Use Case:** Perfect for hybrid scenarios where organizations already have on-premises AD and want seamless integration with Azure Files.

#### Storage Account Keys

**Storage account keys** provide:
- Full access to the storage account and all its contents
- Two keys are provided for key rotation without downtime
- Should be treated as highly sensitive credentials (like root passwords)

**Best Practices:**
- ⚠️ Safeguard keys to prevent unauthorized access
- ⚠️ Rotate keys regularly
- ⚠️ Use Azure Key Vault to store and manage keys
- ⚠️ Prefer identity-based authentication when possible

#### Azure Role-Based Access Control (Azure RBAC)

**Azure RBAC** enables:
- Fine-grained access control based on roles
- Assignment of specific permissions to users, groups, or service principals
- Built-in roles like "Storage File Data SMB Share Reader" and "Storage File Data SMB Share Contributor"
- Custom role definitions for specific requirements

**Common Roles for Azure Files:**

| Role | Description |
|------|-------------|
| **Storage File Data SMB Share Reader** | Read access to files and directories |
| **Storage File Data SMB Share Contributor** | Read, write, delete access to files and directories |
| **Storage File Data SMB Share Elevated Contributor** | Read, write, delete, modify NTFS permissions |

### Authentication Methods NOT Supported

#### Shared Access Signature (SAS)

**SAS tokens are NOT supported for Azure Files authentication.**

- SAS is designed for granting limited, time-bound access to Azure Blob Storage
- Azure Files requires identity-based or key-based authentication
- For granular access control, use Azure RBAC instead

#### Shared Key Authorization

**Shared Key authorization is NOT supported by Azure Files.**

- This is different from storage account keys
- Shared Key authorization refers to a specific API-level authentication scheme
- Azure Files uses different authentication mechanisms as described above

---

### Practice Question: Azure Files Authentication Mechanisms

**Scenario:**
You are setting up authentication mechanisms for your Azure Storage.

**Question:**
Which of the following can be used to provide secure access to your data in Azure Files? (Choose four)

**Options:**

1. ✅ **Microsoft Entra Domain Services**
2. ❌ **Shared Access Signature**
3. ✅ **Storage account keys**
4. ✅ **On-premises Active Directory Domain Services (AD DS)**
5. ✅ **Azure role-based access control (Azure RBAC)**
6. ❌ **Shared Key authorization**

**Answer:** Options 1, 3, 4, and 5

**Explanation:**

✅ **Microsoft Entra Domain Services** - Correct because it allows you to join Azure virtual machines to a domain and use domain credentials to access files stored in Azure Files.

❌ **Shared Access Signature** - Incorrect because SAS tokens are used for granting limited access to resources in your storage account (primarily Blob Storage), but they are **not considered a secure authentication mechanism for Azure Files**.

✅ **Storage account keys** - Correct because storage account keys can be used for authentication to Azure Files. It is essential to safeguard these keys to prevent unauthorized access.

✅ **On-premises Active Directory Domain Services (AD DS)** - Correct because it allows you to extend your on-premises Active Directory environment to Azure, enabling seamless authentication and access control for files stored in Azure Files.

✅ **Azure role-based access control (Azure RBAC)** - Correct because Azure RBAC allows you to assign specific roles to users or groups, granting them permissions to perform actions on Azure resources, including Azure Files.

❌ **Shared Key authorization** - Incorrect because Shared Key authorization isn't supported by Azure Files.

**Key Takeaway:**
When securing Azure Files, use identity-based authentication methods (Microsoft Entra Domain Services, on-premises AD DS, Azure RBAC) or storage account keys. SAS tokens and Shared Key authorization are **not supported** for Azure Files.

**Domain:** Design data storage solutions

**References:**
- [Overview of Azure Files identity-based authentication](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-active-directory-overview)
- [Enable Microsoft Entra Domain Services authentication on Azure Files](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-identity-auth-domain-services-enable)
- [Enable on-premises AD DS authentication to Azure file shares](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-identity-ad-ds-enable)

---

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
| **Redundancy Options** | LRS, **ZRS** | LRS only ⚠️ | LRS, ZRS, GRS, GZRS | LRS, ZRS, GRS, GZRS |
| **Provisioned Model** | Yes | No (pay-as-you-go) | No (pay-as-you-go) | No (pay-as-you-go) |
| **NFS Support** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Best For** | Transaction-intensive, low-latency workloads | Frequently accessed files | General-purpose file shares | Infrequently accessed data |

> ⚠️ **Important Note on Resiliency**: Transaction Optimized tier does **NOT support ZRS** (Zone-Redundant Storage). If you need both high performance AND highest resiliency (ZRS), **Premium tier is the only option** that meets both requirements. This is a critical exam consideration.

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
   - **Lowest latency** (critical for on-premises applications)
   - **Highest IOPS** (ideal for transaction-intensive workloads)
   - **Fast and consistent throughput**
3. **Highest Resiliency for Premium**: Premium tier supports **ZRS (Zone-Redundant Storage)**, which provides the **highest level of resiliency** by replicating data **synchronously across three availability zones** in a region. This ensures data protection even if an entire availability zone fails.
4. **Predictable Performance**: Provisioned capacity model ensures consistent performance characteristics

**Why Other Options Are Incorrect:**

❌ **Hot is incorrect** because:
- **Hot tier is designed for Blob storage, NOT for Azure Files**
- It is optimized for **frequently accessed blob data** rather than transaction-intensive file operations
- Hot tier in Blob storage context refers to access tiers for blobs, which is a completely different concept from Azure Files storage tiers
- **Important**: Do not confuse Azure Blob Storage access tiers (Hot, Cool, Cold, Archive) with Azure Files storage tiers (Premium, Transaction Optimized, Hot, Cool)

> ⚠️ **Key Distinction**: While Azure Files does have a "Hot" tier, in the context of this question comparing performance options, Hot tier for Azure Files uses HDD-backed storage and is designed for general-purpose file shares with regular access patterns—not for minimizing latency in transaction-intensive scenarios.

❌ **Transaction optimized is incorrect** because:
- Although it is designed for file shares with **frequent access and low latency requirements**, it uses **HDD-based storage**
- HDDs provide **lower performance** compared to Premium's SSD-backed storage
- It's **more cost-effective** but does **not match the performance** required for transaction-intensive workloads
- **Critical**: Transaction optimized tier does **NOT support ZRS**, so it offers a **lower level of resiliency** compared to Premium tier
- The requirement specifically asks for "highest level of resiliency for the selected storage tier"

**Resiliency Comparison:**

| Storage Tier | Supports ZRS | Highest Resiliency Option |
|--------------|--------------|---------------------------|
| **Premium** | ✅ Yes | ZRS (3 availability zones) |
| **Transaction Optimized** | ❌ No | LRS only |
| **Hot** | ✅ Yes | ZRS, GRS, GZRS |
| **Cool** | ✅ Yes | ZRS, GRS, GZRS |

**Key Takeaway:**
For **transaction-intensive workloads with low-latency requirements** that also need **highest resiliency**:
- ✅ Choose **Premium tier** with **ZRS**
- Premium provides: **SSD storage** (lowest latency, highest IOPS) + **ZRS support** (highest resiliency)
- Transaction optimized cannot meet both requirements: while it handles transactions, it lacks ZRS support and uses HDD storage

**Domain:** Design data storage solutions

**References:**
- [Azure Files Planning](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-planning)
- [Create an Azure file share](https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-create-file-share?tabs=azure-portal)
- [Azure Blob Storage Access Tiers](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview)

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

## Data Protection and Recovery

Azure Files provides several mechanisms for protecting your data and enabling recovery from accidental deletions or modifications. Understanding the differences between these features is crucial for implementing the right data protection strategy.

### Azure File Share Snapshots

**Azure File Share snapshots** are the primary mechanism for **retaining file changes and restoring deleted or modified files** within a share.

**Key Characteristics:**
- **Point-in-time copies**: Snapshots capture the state of your entire file share at a specific moment
- **Read-only**: Snapshots are immutable and cannot be modified
- **Incremental**: Only changes since the last snapshot are stored, optimizing storage costs
- **Share-level**: Snapshots are taken at the file share level, not individual files
- **Retention**: You can configure retention policies to automatically delete old snapshots

**Use Cases:**
- ✅ **File-level recovery**: Restore individual files that were accidentally deleted or modified
- ✅ **Ransomware protection**: Recover files to a state before infection
- ✅ **Compliance**: Meet regulatory requirements for data retention
- ✅ **Development/Testing**: Create consistent test environments from production data
- ✅ **Change tracking**: Review file changes over time

**How to Access Snapshots:**
- **Windows**: Use the "Previous Versions" tab in File Explorer
- **Azure Portal**: Browse snapshots and download files directly
- **REST API/PowerShell/CLI**: Programmatic access for automation

**Snapshot Limits:**
- Maximum 200 snapshots per file share
- Snapshots count against share capacity
- Minimum interval between snapshots: None (can be taken immediately)

### Soft Delete for File Shares

**Soft Delete** protects against **accidental deletion of entire file shares**, not individual files.

**Key Characteristics:**
- **Share-level protection only**: Recovers deleted file shares, not individual files within a share
- **Retention period**: 1-365 days (configurable)
- **Cost**: Deleted shares continue to incur storage costs during retention period

**Important Limitation:**
> ⚠️ **Soft Delete does NOT protect individual files.** If someone deletes a file inside a share, Soft Delete will not help you recover it. For file-level recovery, use **Azure File Share snapshots**.

### Data Protection Features NOT Applicable to Azure Files

Several Azure Blob Storage features are often confused with Azure Files capabilities. Understanding these distinctions is important:

| Feature | Applicable to Azure Files? | Notes |
|---------|---------------------------|-------|
| **Blob Versioning** | ❌ No | Blob-specific feature for keeping multiple versions of objects in Blob containers |
| **Blob Lifecycle Management** | ❌ No | Automates blob deletion/tiering based on rules; not applicable to file shares |
| **Blob Soft Delete** | ❌ No | Different from File Share Soft Delete; applies only to blob containers |
| **Point-in-time Restore (Blobs)** | ❌ No | Blob-specific feature for restoring block blobs to a previous state |

### Data Protection Comparison

| Feature | Protects | Recovery Scope | Retention |
|---------|----------|----------------|------------|
| **File Share Snapshots** | Files and folders within a share | Individual files or entire share | Up to 200 snapshots |
| **Soft Delete (File Shares)** | Entire file shares | Whole share only | 1-365 days |
| **Azure Backup (Files)** | Files within a share | Individual files or entire share | Based on backup policy |

---

### Practice Question: Retaining File Changes and Restoring Deleted Files

**Scenario:**
You have been asked to set up an Azure file share for a department in your organization. They require the ability to retain file changes and ensure deleted files can be restored for 14 days.

**Question:**
What should you enable on the Azure file share?

**Options:**
1. ❌ Blob versioning
2. ❌ Soft Delete
3. ❌ Blob lifecycle management
4. ✅ Azure File Share snapshots

**Answer: Azure File Share snapshots**

**Explanation:**

✅ **Azure File Share snapshots is correct** because:
- Snapshots allow you to take **point-in-time copies** of your Azure file share
- You can **restore individual files** to a previous state
- By scheduling regular snapshots, you can retain file changes and ensure deleted files can be restored for a specified period (e.g., 14 days)
- This is the only option that provides the ability to **recover individual files** within a share

❌ **Blob versioning is incorrect** because:
- Blob versioning is a feature for **Azure Blob Storage**, not Azure Files
- It allows you to keep multiple versions of objects in a **Blob storage container**
- This feature is **not applicable to file shares**

❌ **Soft Delete is incorrect** because:
- Soft Delete for Azure Files only protects **entire file shares** from accidental deletion
- It does **NOT** protect individual files within a share
- If someone deletes a file inside a share, Soft Delete **will not help you recover it**
- Use Soft Delete to protect against accidental share deletion, not file deletion

❌ **Blob lifecycle management is incorrect** because:
- This is a feature in **Azure Blob storage** that automates deletion or tiering of older blob versions
- It is **not applicable to Azure file shares**
- It does not provide the ability to retain file changes or restore deleted files

**Key Takeaway:**
For **file-level recovery** in Azure Files:
- ✅ Use **Azure File Share snapshots** - protects individual files
- ❌ Soft Delete only protects the **entire share**, not files within it
- ❌ Blob versioning and lifecycle management are for **Blob Storage only**

**Domain:** Design data storage solutions

**References:**
- [Share snapshots overview](https://learn.microsoft.com/en-us/azure/storage/files/storage-snapshots-files)
- [Enable soft delete on Azure file shares](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-enable-soft-delete)
- [Back up Azure file shares](https://learn.microsoft.com/en-us/azure/backup/azure-file-share-backup-overview)

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

### Network Requirements

Before mounting Azure file shares, ensure that the required network ports are open:

#### Port 445 Requirement

**Port 445** is used for the **SMB (Server Message Block) protocol**, which is what Windows (and other operating systems) use for file sharing and mounting Azure file shares.

| Port | Protocol | Direction | Purpose |
|------|----------|-----------|---------|
| **445** | TCP | Outbound | SMB protocol for file share access |

**Important Considerations:**

- 🔒 **Security Best Practices**: Always ensure you follow security best practices when opening ports, especially when dealing with potentially sensitive data
- ⚠️ **ISP Blocking**: Some Internet Service Providers (ISPs) block port 445 for security reasons. If you experience connection issues:
  - Use a **VPN connection** to bypass ISP restrictions
  - Use **Azure ExpressRoute** for dedicated private connectivity
  - Consider **Azure File Sync** for hybrid scenarios
- ✅ **Test Connectivity**: Before mounting, verify port 445 is accessible using network testing tools

**Common Blocked Ports (NOT used for Azure Files):**

| Port | Protocol | Purpose | Relevant to Azure Files? |
|------|----------|---------|-------------------------|
| **3389** | RDP | Remote Desktop Protocol | ❌ No - Used for remote desktop connections, unrelated to file shares |
| **80** | HTTP | Standard web traffic | ❌ No - Not used for SMB or file share mapping |
| **443** | HTTPS | Secure web traffic | ❌ No - Not used for SMB connections |

**Testing Port 445 Connectivity:**

```powershell
# Windows PowerShell
Test-NetConnection -ComputerName <storage-account>.file.core.windows.net -Port 445

# If TcpTestSucceeded is True, port 445 is accessible
# If TcpTestSucceeded is False, port 445 is blocked
```

```bash
# Linux
nc -zv <storage-account>.file.core.windows.net 445

# macOS
nc -zv <storage-account>.file.core.windows.net 445
```

---

### Practice Question: Mapping Drive to Azure File Share

**Scenario:**
You create an Azure Storage account named **contosostorage**.

You plan to create a file share named **data**.

Users need to map a drive to the data file share from home computers that run Windows 10.

**Question:**
Which outbound port should you open between the home computers and the data file share?

**Options:**
1. ❌ **3389**
2. ✅ **445**
3. ❌ **80**
4. ❌ **443**

**Answer: 445**

**Explanation:**

✅ **Port 445 is correct** because:
- This port is used for the **SMB (Server Message Block) protocol**, which is what Windows uses for file sharing
- When mapping a drive to an Azure file share from Windows, the connection is established over SMB protocol on port 445
- **Note**: Some ISPs block this port, so if you experience issues, a VPN or Azure ExpressRoute connection may be necessary to allow the traffic
- Always ensure you are following security best practices when opening ports, especially when dealing with potentially sensitive data

❌ **Port 3389 is incorrect** because:
- Used for **Remote Desktop Protocol (RDP)** for remote desktop connections
- Completely unrelated to file shares or SMB protocol

❌ **Port 80 is incorrect** because:
- Used for standard **HTTP web traffic**
- Not used for SMB or file share mapping

❌ **Port 443 is incorrect** because:
- Used for secure **HTTPS web traffic**
- Not used for SMB connections

**Key Takeaway:**
When mapping drives to Azure file shares from Windows (or other OS), **port 445** must be open for outbound connections. This is a critical requirement for SMB-based file share access.

**Domain:** Design data storage solutions

**References:**
- [Troubleshoot Azure Files connectivity and access issues (SMB)](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/files-troubleshoot-smb-connectivity)
- [Mount SMB Azure file share on Windows](https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-windows)

---

### Practice Question: UNC Path for Azure File Share

**Scenario:**
You have an Azure subscription named **Subscription1**.

You create an Azure Storage account named **contosostorage**, and then you create a file share named **data**.

**Question:**
Which UNC path should you include in a script that references files from the **data** file share?

**Answer:**

The correct UNC path format for Azure File Shares is:

```
\\[storageaccountname].file.core.windows.net\[FileShareName]
```

For this specific scenario:
```
\\contosostorage.file.core.windows.net\data
```

**UNC Path Component Breakdown:**

| Component | Value | Description |
|-----------|-------|-------------|
| **Storage Account Name** | `contosostorage` | The name of your Azure Storage account |
| **Service Endpoint** | `file.core.windows.net` | The Azure Files service endpoint (constant) |
| **File Share Name** | `data` | The name of the file share you created |

**Common Mistakes to Avoid:**

❌ **Incorrect - Using subscription name:**
```
\\subscription1.file.core.windows.net\data
```
*The subscription name is NOT part of the UNC path*

❌ **Incorrect - Using blob endpoint:**
```
\\contosostorage.blob.core.windows.net\data
```
*`blob.core.windows.net` is for Blob Storage, not Azure Files*

❌ **Incorrect - Wrong service endpoint:**
```
\\contosostorage.core.windows.net\data
```
*Missing the `.file` subdomain*

**Key Points:**
- The UNC path format is **always** `\\[storage-account-name].file.core.windows.net\[share-name]`
- The **storage account name** comes first, not the subscription name
- Use `.file.core.windows.net` endpoint (not `.blob.core.windows.net`)
- The **file share name** comes at the end of the path
- This format is used when mounting drives from Windows, scripting access, or configuring applications

**Usage Example in Script:**

```powershell
# PowerShell script to access Azure File Share
$storageAccountName = "contosostorage"
$shareName = "data"
$storageAccountKey = "your-storage-account-key"

# UNC path format
$uncPath = "\\$storageAccountName.file.core.windows.net\$shareName"

# Map network drive
net use Z: $uncPath /user:Azure\$storageAccountName $storageAccountKey
```

```batch
REM Batch script to map drive
net use Z: \\contosostorage.file.core.windows.net\data /user:Azure\contosostorage STORAGE_ACCOUNT_KEY
```

**Domain:** Design data storage solutions

**References:**
- [Mount SMB Azure file share on Windows](https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-windows)
- [Azure Files UNC path format](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-introduction)

---

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

---

## Azure Files vs Azure NetApp Files

When migrating file servers to Azure, choosing between Azure Files and Azure NetApp Files depends on your protocol interoperability requirements.

### Protocol Support Comparison

| Feature | Azure Files | Azure NetApp Files | Azure Blob Storage |
|---------|-------------|-------------------|-------------------|
| **SMB Support** | ✅ Yes | ✅ Yes | ❌ No |
| **NFS Support** | ✅ Yes (Premium only) | ✅ Yes | ❌ No |
| **Concurrent SMB + NFS** | ❌ No interoperability | ✅ Yes (Dual-protocol) | ❌ No |
| **Windows Clients** | ✅ SMB | ✅ SMB | ❌ REST API only |
| **Unix/Linux Clients** | ✅ NFS/SMB | ✅ NFS/SMB | ❌ REST API only |

### Key Differences

**Azure Files:**
- Supports both SMB and NFS protocols
- **No interoperability** between protocols - a file share can be either SMB OR NFS, not both
- SMB shares and NFS shares are separate and cannot access the same data simultaneously
- NFS support requires Premium tier only

**Azure NetApp Files:**
- Enterprise-grade file storage service
- **Dual-protocol support** with full interoperability between SMB and NFS
- Same data can be accessed concurrently by both Windows (SMB) and Unix (NFS) clients
- Ideal for mixed environments requiring cross-platform file sharing
- Higher performance and more advanced features (snapshots, replication)

### When to Choose Which

| Scenario | Recommended Solution |
|----------|---------------------|
| Windows-only environment | Azure Files (SMB) |
| Linux-only environment | Azure Files (NFS Premium) or Azure NetApp Files |
| Mixed Windows + Unix with interoperability needed | **Azure NetApp Files** |
| Cost-sensitive general file shares | Azure Files |
| High-performance enterprise workloads | Azure NetApp Files |

---

### Practice Question: File Server Migration with Protocol Interoperability

**Scenario:**
You have an on-premises file server that you plan to migrate to Azure.

The existing file server has **Unix clients** that connect by using the **NFS protocol**, and **Windows clients** that connect by using the **SMB protocol**.

**Interoperability between the clients is required.**

**Question:**
To what should you migrate the file server data?

**Options:**
1. ❌ Azure Blob storage
2. ❌ Azure Files
3. ✅ Azure NetApp Files
4. ❌ Azure Table storage

**Answer: Azure NetApp Files**

**Explanation:**

✅ **Azure NetApp Files is correct** because:
- It offers **concurrent support and interoperability** between both SMB-based and NFS-based clients
- **Dual-protocol** capability allows the same file share to be accessed via both SMB (Windows) and NFS (Unix) simultaneously
- This is the only Azure service that provides true protocol interoperability for file storage

❌ **Azure Blob storage is incorrect** because:
- Blob storage does **not offer SMB support**
- It uses REST API for access, not file system protocols
- Not suitable for traditional file server migration scenarios requiring SMB/NFS

❌ **Azure Files is incorrect** because:
- While Azure Files supports both SMB and NFS protocols, **no interoperability between protocols is offered**
- A file share can be configured for either SMB or NFS, but not both at the same time
- Cannot serve the same data to both Windows (SMB) and Unix (NFS) clients concurrently

❌ **Azure Table storage is incorrect** because:
- Table storage is a NoSQL key-value store
- It does **not provide file storage** capabilities
- Does not support SMB or NFS protocols
- Does not meet any of the interoperability requirements

**Key Takeaway:**
When you need **interoperability** between Windows clients (SMB) and Unix clients (NFS) accessing the **same data**, **Azure NetApp Files** is the only Azure solution that supports this requirement.

**Domain:** Design data storage solutions

**References:**
- [Design for Azure Files - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/design-data-storage-solution-for-non-relational-data/4-design-for-azure-files)
- [What is Azure NetApp Files](https://learn.microsoft.com/en-us/azure/azure-netapp-files/azure-netapp-files-introduction)
- [Dual-protocol access for Azure NetApp Files](https://learn.microsoft.com/en-us/azure/azure-netapp-files/dual-protocol-volumes)

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
