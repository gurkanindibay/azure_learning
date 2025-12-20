# Azure Blob Storage Access Tiers

## Table of Contents

- [Overview](#overview)
- [Storage Account Types](#storage-account-types)
  - [Standard General-Purpose v2](#standard-general-purpose-v2)
  - [Premium Block Blobs](#premium-block-blobs)
  - [Premium File Shares](#premium-file-shares)
  - [Premium Page Blobs](#premium-page-blobs)
- [Storage Account Types Comparison](#storage-account-types-comparison)
  - [Lifecycle Management Policy Support](#lifecycle-management-policy-support)
  - [Exam Scenario: Lifecycle Management Storage Account Selection](#exam-scenario-lifecycle-management-storage-account-selection)
  - [Exam Scenario: Choosing the Right Storage Account Type](#exam-scenario-choosing-the-right-storage-account-type)
  - [Exam Scenario: High-Performance Media Streaming Storage](#scenario-high-performance-media-streaming-storage)
  - [Exam Scenario: Business-Critical Data with Immutability and Resiliency](#scenario-business-critical-data-with-immutability-and-resiliency)
- [Storage Redundancy Options](#storage-redundancy-options)
  - [Locally Redundant Storage (LRS)](#locally-redundant-storage-lrs)
  - [Zone-Redundant Storage (ZRS)](#zone-redundant-storage-zrs)
  - [Geo-Redundant Storage (GRS)](#geo-redundant-storage-grs)
  - [Read-Access Geo-Redundant Storage (RA-GRS)](#read-access-geo-redundant-storage-ra-grs)
  - [Geo-Zone-Redundant Storage (GZRS)](#geo-zone-redundant-storage-gzrs)
  - [Read-Access Geo-Zone-Redundant Storage (RA-GZRS)](#read-access-geo-zone-redundant-storage-ra-gzrs)
- [Redundancy Options Comparison](#redundancy-options-comparison)
  - [Durability and Availability](#durability-and-availability)
  - [Outage Scenario Support](#outage-scenario-support)
  - [Supported Services by Redundancy Type](#supported-services-by-redundancy-type)
  - [Archive Tier Support by Storage Account Type](#archive-tier-support-by-storage-account-type)
- [Available Access Tiers](#available-access-tiers)
  - [Hot Tier](#hot-tier)
  - [Cool Tier](#cool-tier)
  - [Cold Tier](#cold-tier)
  - [Archive Tier](#archive-tier)
- [Tier Comparison](#tier-comparison)
- [Archive Tier Rehydration](#archive-tier-rehydration)
  - [What is Rehydration?](#what-is-rehydration)
  - [Two Methods to Rehydrate Archived Blobs](#two-methods-to-rehydrate-archived-blobs)
    - [Method 1: Copy Blob to Online Tier ✅](#method-1-copy-blob-to-online-tier-)
    - [Method 2: Set Blob Tier Operation ✅](#method-2-set-blob-tier-operation-)
    - [❌ Incorrect Methods](#-incorrect-methods)
      - [Set Blob Properties Operation ❌](#set-blob-properties-operation-)
      - [Snapshot Blob Operation ❌](#snapshot-blob-operation-)
  - [Rehydration Priority](#rehydration-priority)
    - [Standard Priority](#standard-priority)
    - [High Priority](#high-priority)
- [Tier Transition Rules](#tier-transition-rules)
  - [Supported Transitions](#supported-transitions)
  - [Key Points](#key-points)
- [Monitoring Rehydration Status](#monitoring-rehydration-status)
  - [Check Archive Status (.NET)](#check-archive-status-net)
  - [Check Archive Status (Azure CLI)](#check-archive-status-azure-cli)
  - [Check Archive Status (Python)](#check-archive-status-python)
- [Cost Considerations](#cost-considerations)
  - [Storage Costs](#storage-costs)
  - [Rehydration Costs](#rehydration-costs)
  - [Early Deletion Fees](#early-deletion-fees)
- [Choosing the Right Tier - Practical Scenarios](#choosing-the-right-tier---practical-scenarios)
  - [Scenario: 100 GB/day with 30-day retention and rare access](#scenario-100-gbday-with-30-day-retention-and-rare-access)
- [Best Practices](#best-practices)
- [Complete Rehydration Workflow Example](#complete-rehydration-workflow-example)
  - [Scenario: Rehydrate archived log files for analysis](#scenario-rehydrate-archived-log-files-for-analysis)
- [Key Takeaways](#key-takeaways)
  - [✅ Two Valid Rehydration Methods:](#-two-valid-rehydration-methods)
  - [❌ Invalid Methods:](#-invalid-methods)
  - [🎯 Critical Rehydration Requirements:](#-critical-rehydration-requirements)
  - [Remember:](#remember)
- [References](#references)

## Overview

Azure Blob Storage offers different access tiers to help you store blob object data in the most cost-effective manner based on how frequently the data is accessed. The access tier of a blob can be set at the blob level, allowing you to optimize costs based on your specific usage patterns.

## Storage Account Types

Azure Storage offers several types of storage accounts, each supporting different features with its own pricing model. Microsoft recommends using the Azure Resource Manager deployment model for all storage accounts.

### Standard General-Purpose v2

- **Supported Services**: Blob Storage (including Data Lake Storage), Queue Storage, Table Storage, and Azure Files
- **Redundancy Options**: LRS, GRS, RA-GRS, ZRS, GZRS, RA-GZRS
- **Use Case**: Standard storage account type for blobs, file shares, queues, and tables
- **Recommendation**: Recommended for most scenarios using Azure Storage
- **Note**: If you need NFS support in Azure Files, use Premium File Shares instead

### Premium Block Blobs

- **Supported Services**: Blob Storage (including Data Lake Storage) - Block blobs and append blobs only
- **Redundancy Options**: LRS, ZRS
- **Performance**: Uses solid-state drives (SSDs) for low latency and high throughput
- **Use Case**: High transaction rates, smaller objects, or consistently low storage latency requirements
- **Examples**: Real-time analytics, IoT data ingestion, gaming applications

### Premium File Shares

- **Supported Services**: Azure Files only
- **Redundancy Options**: LRS, ZRS
- **Performance**: Uses solid-state drives (SSDs) for low latency and high throughput
- **Use Case**: Enterprise or high-performance scale applications
- **Features**: Supports both SMB and NFS file shares

#### Exam Scenario: Lowest Latency for File Share Access

**Question**: You are planning the deployment of an Azure Storage account that will host a file share. You need to recommend the storage tier for the account. The solution must provide the lowest possible latency for file access.

Which storage tier should you recommend?

| Option | Correct? |
|--------|----------|
| Cool | ❌ |
| Hot | ❌ |
| **Premium** | ✅ **Correct Answer** |
| Transaction optimized | ❌ |

**Answer Explanation:**

**Premium** is the correct answer because:

1. **SSD-Backed Storage**: Premium file shares use solid-state drives (SSDs) which provide significantly lower latency compared to HDD-backed storage tiers.

2. **Designed for Low Latency**: Premium tier is specifically designed for workloads requiring single-digit millisecond latency for file operations.

3. **High Performance**: Premium file shares deliver consistent, high-performance I/O operations essential for latency-sensitive applications.

**Why Other Options Are Incorrect:**

| Option | Why It's Wrong |
|--------|----------------|
| **Cool** | Cool tier is designed for infrequently accessed data with lower storage costs but higher access costs. It uses HDD storage which has higher latency than SSD. Not suitable for scenarios requiring lowest latency. |
| **Hot** | Hot tier is optimized for frequently accessed data but still uses HDD-based storage. While it has lower access costs than Cool tier, it does not provide the lowest possible latency. |
| **Transaction optimized** | Transaction optimized is a tier within Standard file shares (HDD-based) that is optimized for transaction-heavy workloads. While it reduces transaction costs, it does not minimize latency like Premium SSD storage. |

**Azure Files Storage Tiers Comparison:**

| Tier | Storage Type | Latency | Best For |
|------|-------------|---------|----------|
| **Premium** | SSD | Lowest (single-digit ms) | Latency-sensitive workloads, databases, high-performance apps |
| **Transaction optimized** | HDD | Higher | General file shares with heavy transactions |
| **Hot** | HDD | Higher | Frequently accessed file shares |
| **Cool** | HDD | Highest | Infrequently accessed data, archival |

> 💡 **Exam Tip**: When the question specifically asks for **lowest latency** for file shares, always choose **Premium**. Premium is the only file share tier backed by SSDs. The other tiers (Transaction optimized, Hot, Cool) are all Standard tiers backed by HDDs and cannot provide the same low latency.

---

### Premium Page Blobs

- **Supported Services**: Page blobs only
- **Redundancy Options**: LRS, ZRS
- **Performance**: Uses solid-state drives (SSDs) for low latency and high throughput
- **Use Case**: Azure IaaS disks for virtual machines, databases requiring random read/write operations

## Storage Account Types Comparison

| Account Type | Supported Services | Redundancy Options | Performance | Use Case |
|-------------|-------------------|-------------------|-------------|----------|
| **Standard GPv2** | Blobs, Files, Queues, Tables, Data Lake | LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS | Standard | Most scenarios |
| **Premium Block Blobs** | Block blobs, Append blobs | LRS, ZRS | Premium (SSD) | High transactions, low latency |
| **Premium File Shares** | Azure Files | LRS, ZRS | Premium (SSD) | Enterprise file shares, SMB/NFS |
| **Premium Page Blobs** | Page blobs | LRS, ZRS | Premium (SSD) | VM disks, databases |

> **Important**: You cannot change a storage account to a different type after creation. To move data to a different account type, you must create a new account and copy the data.

### Lifecycle Management Policy Support

Lifecycle management policies allow you to automatically transition blobs between access tiers (Hot → Cool → Cold → Archive) or delete blobs based on rules. **Not all storage account types support lifecycle management**.

| Storage Account Type | Performance | Lifecycle Management Support | Notes |
|---------------------|-------------|------------------------------|-------|
| **Standard general-purpose v2** | Standard | ✅ Yes | Full support for tier transitions and deletion rules |
| **BlobStorage (legacy)** | Standard | ✅ Yes | Legacy account type, but supports lifecycle management |
| **Premium block blobs** | Premium | ❌ No | No access tiers (Hot/Cool/Archive) to transition between |
| **Premium file shares** | Premium | ❌ No | Azure Files only, not blob storage |
| **Premium page blobs** | Premium | ❌ No | Page blobs don't support access tiers |

**Key Lifecycle Management Restrictions:**
- ⚠️ Lifecycle management is **ONLY supported** on **Standard performance** storage accounts
- ✅ **Standard general-purpose v2** and **BlobStorage (legacy)** support lifecycle management
- ❌ **Premium storage accounts** (block blobs, file shares, page blobs) do NOT support lifecycle management
- ❌ Access tiers (Hot/Cool/Cold/Archive) are only available on **Standard** blob storage

> 💡 **Exam Tip**: When a question mentions **lifecycle management** or **automatic tier transitions**, immediately filter for **Standard performance** accounts only. Premium accounts use SSDs with no tier hierarchy, so lifecycle policies don't apply.

---

#### Exam Scenario: Lifecycle Management Storage Account Selection

**Question**: You plan to implement two new apps that have the requirements shown in the following table:

| Name | Requirement |
|------|-------------|
| App1 | Use lifecycle management to migrate app data between storage tiers |
| App2 | Store app data in an Azure file share |

You have the following storage accounts:

| Storage Account | Type | Performance |
|----------------|------|-------------|
| Storage1 | Standard general-purpose v2 | Standard |
| Storage2 | Premium block blobs | Premium |
| Storage3 | BlobStorage (legacy) | Standard |
| Storage4 | Premium file shares | Premium |

Which storage accounts should you recommend using for App1?

| Option | Correct? |
|--------|----------|
| Storage1 and Storage2 only | ❌ |
| **Storage1 and Storage3 only** | ✅ **Correct Answer** |
| Storage1, Storage2, and Storage3 only | ❌ |
| Storage1, Storage2, Storage3, and Storage4 | ❌ |

**Answer Explanation:**

**Storage1 and Storage3 only** is the correct answer because:

1. **Storage1 (Standard general-purpose v2)**: Fully supports lifecycle management policies for automatically transitioning blobs between Hot, Cool, Cold, and Archive tiers.

2. **Storage3 (BlobStorage, Standard)**: Also supports lifecycle management. BlobStorage is a legacy account type but still supports tier transitions.

**Why Other Storage Accounts Are Excluded:**

| Storage Account | Why It's Excluded |
|----------------|-------------------|
| **Storage2 (Premium block blobs)** | Premium storage accounts do NOT support lifecycle management. Premium block blobs use SSDs and don't have access tiers (Hot/Cool/Archive) to transition between. |
| **Storage4 (Premium file shares)** | Premium file shares are for Azure Files (SMB/NFS file shares), not blob storage. Lifecycle management is a blob-specific feature and doesn't apply to file shares. |

> 💡 **Exam Tip**: The key differentiator is **Standard vs Premium performance**. Only **Standard general-purpose v2** and **BlobStorage (legacy)** support lifecycle management because they have access tiers to transition between.

---

### Exam Scenario: Choosing the Right Storage Account Type

#### Scenario: High-Performance Storage with Immutability Requirements

**Question**: You need to design a storage solution for an app that will store large amounts of frequently used data. The solution must meet the following requirements:
- Maximize data throughput
- Prevent the modification of data for one year
- Minimize latency for read and write operations

Which Azure Storage account type should you recommend?

| Option | Correct? |
|--------|----------|
| BlobStorage | ❌ |
| **BlockBlobStorage** | ✅ **Correct Answer** |
| FileStorage | ❌ |
| StorageV2 with Premium performance | ❌ |
| StorageV2 with Standard performance | ❌ |

**Answer Explanation:**

**BlockBlobStorage (Premium Block Blobs)** is the correct answer because:

1. **Maximizes Data Throughput**: Premium Block Blob storage accounts use solid-state drives (SSDs), providing significantly higher throughput compared to standard storage accounts.

2. **Prevents Modification for One Year**: Premium Block Blob storage accounts support **immutable storage policies** (WORM - Write Once, Read Many). You can configure a time-based retention policy to prevent data modification and deletion for one year.

3. **Minimizes Latency**: SSD-backed Premium storage delivers **low latency** for both read and write operations, making it ideal for high-performance workloads.

**Why Other Options Are Incorrect:**

| Option | Why It's Wrong |
|--------|----------------|
| **BlobStorage** | Legacy account type (deprecated). Microsoft recommends using General-purpose v2 or Premium Block Blobs instead. Does not offer premium performance. |
| **FileStorage** | Premium File Shares are designed for Azure Files (SMB/NFS file shares), not blob storage. Not suitable for blob workloads requiring immutability. |
| **StorageV2 with Premium performance** | StorageV2 (General-purpose v2) does NOT offer a "Premium performance" tier for blobs. StorageV2 uses Standard HDD/SSD storage. Premium performance for blobs requires Premium Block Blobs account type. |
| **StorageV2 with Standard performance** | While StorageV2 supports immutable storage, Standard performance uses HDDs which cannot maximize throughput or minimize latency like SSDs. |

**Key Decision Factors:**

| Requirement | Why BlockBlobStorage Wins |
|-------------|---------------------------|
| High throughput | SSD-backed storage provides maximum throughput |
| Low latency | Premium storage with SSDs delivers millisecond latency |
| Immutability | Supports time-based retention and legal hold policies |
| Frequent access | Optimized for high transaction rates and frequent access patterns |

> 💡 **Exam Tip**: When you see requirements for **high throughput**, **low latency**, AND **blob storage** together, think **Premium Block Blobs (BlockBlobStorage)**. Don't confuse "Premium" tier options—StorageV2 doesn't have a "Premium" option for blobs; you need a separate Premium Block Blob account type.

> ⚠️ **Important**: Premium Block Blob accounts only support **LRS** and **ZRS** redundancy. If you need geo-redundancy (GRS/GZRS), you must use Standard GPv2.

---

#### Scenario: High-Performance Media Streaming Storage

**Question**: You are planning a storage solution. The solution must meet the following requirements:
- Support at least 500 requests per second
- Support large image, video, and audio streams

Which type of Azure storage account should you provision?

| Option | Correct? |
|--------|----------|
| Premium file shares | ❌ |
| Standard general-purpose v2 | ❌ |
| **Premium block blobs** | ✅ **Correct Answer** |
| Premium page blobs | ❌ |

**Answer Explanation:**

**Premium block blobs** is the correct answer because:

1. **Optimized for Streaming Workloads**: Block blobs are optimized for large-scale data storage and streaming workloads, such as images, videos, and audio files.

2. **High Transaction Rates**: The premium performance tier ensures high throughput and low latency, which is necessary to support at least 500 requests per second.

3. **Media Streaming Design**: Premium block blob storage is specifically designed for workloads requiring high transaction rates and is ideal for media streaming scenarios.

**Why Other Options Are Incorrect:**

| Option | Why It's Wrong |
|--------|----------------|
| **Premium file shares** | Azure Premium File Shares are designed for SMB-based workloads and are not optimized for handling high-performance blob storage or streaming scenarios. They are more suitable for file-based applications rather than large media content storage and delivery. |
| **Standard general-purpose v2** | While General-Purpose v2 (GPv2) accounts provide cost-effective blob storage, standard performance does not guarantee low latency or high transaction rates. It is not the best option for workloads requiring high throughput and real-time streaming. |
| **Premium page blobs** | Page Blobs are used for virtual machine disks (VHDs) and workloads requiring random read/write access to large files. They are not optimized for sequential streaming of large images, videos, or audio files. |

**Key Decision Factors:**

| Requirement | Why Premium Block Blobs Wins |
|-------------|------------------------------|
| 500+ requests/second | Premium tier with SSD-backed storage handles high transaction rates |
| Large media files | Block blobs are designed for storing large binary objects |
| Streaming workloads | Optimized for sequential read patterns common in media streaming |
| Images, videos, audio | Block blobs are the recommended blob type for media content |

> 💡 **Exam Tip**: When you see requirements for **media streaming**, **large files (images/video/audio)**, AND **high request rates**, think **Premium Block Blobs**. Remember: Page blobs = VHDs/disks, File shares = SMB/NFS file access, Block blobs = general object/media storage.

---

#### Scenario: Business-Critical Data with Immutability and Resiliency

**Question**: You plan to develop a new app that will store business-critical data. The app must meet the following requirements:
- Prevent new data from being modified for one year
- Maximize data resiliency
- Minimize read latency

Which storage solution should you recommend for the app?

| Option | Correct? |
|--------|----------|
| Storage Account type: Standard general-purpose v1, Redundancy: Zone-redundant storage (ZRS) | ❌ |
| Storage Account type: Standard general-purpose v1, Redundancy: Locally-redundant storage (LRS) | ❌ |
| Storage Account type: Standard general-purpose v2, Redundancy: Zone-redundant storage (ZRS) | ❌ |
| Storage Account type: Standard general-purpose v2, Redundancy: Locally-redundant storage (LRS) | ❌ |
| **Storage Account type: Premium block blobs, Redundancy: Zone-redundant storage (ZRS)** | ✅ **Correct Answer** |
| Storage Account type: Premium block blobs, Redundancy: Locally-redundant storage (LRS) | ❌ |

**Answer Explanation:**

**Premium block blobs with Zone-redundant storage (ZRS)** is the correct answer because:

1. **Minimizes Read Latency**: Premium block blob storage provides the lowest read latency due to SSD-backed storage, making it the best choice for minimizing read latency.

2. **Maximizes Data Resiliency**: Zone-redundant storage (ZRS) ensures data resiliency by replicating data synchronously across multiple availability zones (at least 3), protecting against data center failures.

3. **Prevents Data Modification**: Azure immutable blob storage policies can be configured to prevent data modification for one year, ensuring compliance with the requirement to keep data unaltered.

**Why Other Options Are Incorrect:**

| Option | Why It's Wrong |
|--------|----------------|
| **Standard GPv1 (any redundancy)** | General-purpose v1 is a legacy account type that doesn't support immutable storage policies. It also uses standard HDD storage which doesn't minimize read latency. Microsoft recommends upgrading to GPv2 or Premium accounts. |
| **Standard GPv2 with ZRS** | While GPv2 with ZRS provides good resiliency and supports immutability, standard performance uses HDD storage which cannot minimize read latency like premium SSD storage. |
| **Standard GPv2 with LRS** | Same latency issue as above, plus LRS only provides single-datacenter redundancy which doesn't maximize data resiliency. |
| **Premium block blobs with LRS** | While this provides low latency and supports immutability, LRS only replicates within a single datacenter. This doesn't maximize data resiliency—ZRS is needed to protect against datacenter-level failures. |

**Key Decision Factors:**

| Requirement | Solution Component | Why |
|-------------|-------------------|-----|
| Minimize read latency | Premium block blobs | SSD-backed storage provides lowest latency |
| Maximize data resiliency | Zone-redundant storage (ZRS) | Replicates across 3+ availability zones |
| Prevent modification for 1 year | Immutable storage policy | Time-based retention policy on Premium block blobs |

> 💡 **Exam Tip**: When you see requirements combining **immutability**, **low latency**, AND **high resiliency**, you need **Premium Block Blobs with ZRS**. Remember:
> - **Low latency** → Premium (SSD) storage
> - **High resiliency** → ZRS (multi-zone) or GRS/GZRS (multi-region)
> - **Immutability** → Supported by Premium Block Blobs and Standard GPv2, NOT by GPv1

> ⚠️ **Important**: Premium Block Blob accounts only support **LRS** and **ZRS** redundancy (no GRS/GZRS). If you need geo-redundancy AND premium performance, you may need to implement cross-region replication manually or use Standard GPv2 with GRS.

## Storage Redundancy Options

Azure Storage maintains multiple copies of your data to protect against planned and unplanned events including hardware failures, network outages, power outages, and natural disasters.

### Locally Redundant Storage (LRS)

- **Replication**: Copies data synchronously within one or more availability zones in the primary region
- **Durability**: At least 99.999999999% (11 nines) over a given year
- **Availability**: At least 99.9% (99% for cool/cold/archive tiers)
- **Cost**: Lowest-cost redundancy option
- **Protection**: Protects against drive, server, and rack failures
- **Limitation**: Does NOT protect against data center disasters (fire, flooding)

**Best for**:
- Data that can be easily reconstructed if lost
- Data governance requirements restricting replication within a region
- Development and testing environments

### Zone-Redundant Storage (ZRS)

- **Replication**: Copies data synchronously across three or more Azure availability zones in the primary region
- **Durability**: At least 99.9999999999% (12 nines) over a given year
- **Availability**: At least 99.9% (99% for cool/cold tiers)
- **Protection**: Protects against zone-level failures while maintaining read/write access
- **Limitation**: Does NOT protect against regional disasters

**Best for**:
- High availability scenarios
- Azure Files workloads (no remounting required during zone failover)
- Applications requiring data to stay within a specific region

### Geo-Redundant Storage (GRS)

- **Replication**: LRS in primary region + asynchronous copy to secondary region (using LRS)
- **Durability**: At least 99.99999999999999% (16 nines) over a given year
- **Availability**: At least 99.9% (99% for cool/cold/archive tiers)
- **Secondary Region**: Data not accessible until failover occurs
- **RPO**: Less than or equal to 15 minutes with Geo Priority Replication

**Best for**:
- Disaster recovery scenarios
- Compliance requirements for geographic redundancy
- Critical data requiring protection against regional outages

### Read-Access Geo-Redundant Storage (RA-GRS)

- **Replication**: Same as GRS
- **Additional Feature**: Read access to secondary region (without failover)
- **Availability**: At least 99.99% (99.9% for cool/cold/archive tiers) for read requests
- **Secondary Endpoint**: `<account-name>-secondary.blob.core.windows.net`

**Best for**:
- Applications requiring high read availability
- Read-heavy workloads that can leverage the secondary region
- Business continuity with minimal downtime

### Geo-Zone-Redundant Storage (GZRS)

- **Replication**: ZRS in primary region + asynchronous copy to secondary region (using LRS)
- **Durability**: At least 99.99999999999999% (16 nines) over a given year
- **Availability**: At least 99.9% (99% for cool/cold tiers)
- **Protection**: Maximum consistency, durability, availability, excellent performance, and disaster recovery resilience

**Best for**:
- Mission-critical applications
- Maximum data protection requirements
- Applications requiring both zone and regional redundancy

### Read-Access Geo-Zone-Redundant Storage (RA-GZRS)

- **Replication**: Same as GZRS
- **Additional Feature**: Read access to secondary region (without failover)
- **Availability**: At least 99.99% (99.9% for cool/cold tiers) for read requests
- **Secondary Endpoint**: `<account-name>-secondary.blob.core.windows.net`

**Best for**:
- Highest availability requirements
- Critical applications with read-heavy workloads
- Enterprise applications requiring maximum protection

## Redundancy Options Comparison

### Durability and Availability

| Parameter | LRS | ZRS | GRS/RA-GRS | GZRS/RA-GZRS |
|-----------|-----|-----|------------|--------------|
| **Durability (per year)** | 11 nines (99.999999999%) | 12 nines (99.9999999999%) | 16 nines (99.99999999999999%) | 16 nines (99.99999999999999%) |
| **Read Availability** | 99.9% | 99.9% | 99.9% (GRS) / 99.99% (RA-GRS) | 99.9% (GZRS) / 99.99% (RA-GZRS) |
| **Write Availability** | 99.9% | 99.9% | 99.9% | 99.9% |
| **Zones in Primary** | 1+ | 3+ | 1+ | 3+ |
| **Secondary Region** | ❌ | ❌ | ✅ | ✅ |
| **Read from Secondary** | ❌ | ❌ | ❌ (GRS) / ✅ (RA-GRS) | ❌ (GZRS) / ✅ (RA-GZRS) |

### Outage Scenario Support

| Scenario | LRS | ZRS | GRS/RA-GRS | GZRS/RA-GZRS |
|----------|-----|-----|------------|--------------|
| Node unavailable | ✅ | ✅ | ✅ | ✅ |
| Data center unavailable | ❌ | ✅ | ✅ (with failover) | ✅ |
| Region-wide outage | ❌ | ❌ | ✅ (with failover) | ✅ (with failover) |
| Read during primary outage | ❌ | ❌ | ❌ (GRS) / ✅ (RA-GRS) | ❌ (GZRS) / ✅ (RA-GZRS) |

### Supported Services by Redundancy Type

| Service | LRS | ZRS | GRS | RA-GRS | GZRS | RA-GZRS |
|---------|-----|-----|-----|--------|------|---------|
| **Blob Storage** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Queue Storage** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Table Storage** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Azure Files** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Azure Managed Disks** | ✅ | ✅ (with limitations) | ❌ | ❌ | ❌ | ❌ |
| **Archive Tier** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |

> **Note**: Archive tier for Blob Storage is NOT supported for ZRS, GZRS, or RA-GZRS accounts.

### Archive Tier Support by Storage Account Type

Not all storage account types support the Archive access tier:

| Storage Account Type | Archive Tier Support | Notes |
|---------------------|---------------------|-------|
| **Standard GPv2** | ✅ Yes | Only with LRS, GRS, or RA-GRS redundancy |
| **Premium Block Blobs** | ❌ No | Premium accounts use SSDs, no archive tier |
| **Premium File Shares** | ❌ No | Azure Files does not support archive tier |
| **Premium Page Blobs** | ❌ No | Premium accounts use SSDs, no archive tier |

**Key Archive Tier Restrictions:**
- ⚠️ Archive tier is **ONLY available** for **Standard General-Purpose v2** storage accounts
- ⚠️ Archive tier is **NOT supported** with zone-redundant options (ZRS, GZRS, RA-GZRS)
- ✅ Archive tier works with **LRS, GRS, and RA-GRS** redundancy only
- ❌ Premium storage accounts (Block Blobs, File Shares, Page Blobs) do **NOT** support archive tier
- ❌ Azure Files does **NOT** support archive tier regardless of account type

## Available Access Tiers

### Hot Tier
- **Use case**: Data that is accessed frequently
- **Characteristics**:
  - Highest storage costs
  - Lowest access costs
  - Optimized for frequent read and write operations
- **Examples**: Active documents, images for websites, streaming media

### Cool Tier
- **Use case**: Data that is infrequently accessed and stored for at least 30 days
- **Characteristics**:
  - Lower storage costs than Hot
  - Higher access costs than Hot
  - Minimum storage duration: 30 days (early deletion fees apply)
- **Examples**: Short-term backup, disaster recovery data, older media content

### Cold Tier
- **Use case**: Data that is rarely accessed and stored for at least 90 days
- **Characteristics**:
  - Lower storage costs than Cool
  - Higher access costs than Cool
  - Minimum storage duration: 90 days (early deletion fees apply)
- **Examples**: Long-term backup data, compliance archives

### Archive Tier
- **Use case**: Data that is rarely accessed and stored for at least 180 days
- **Characteristics**:
  - Lowest storage costs
  - Highest access costs and rehydration costs
  - **Offline tier** - data must be rehydrated before reading
  - Minimum storage duration: 180 days (early deletion fees apply)
  - Rehydration can take several hours
- **Examples**: Long-term archival, compliance data, historical records

## Tier Comparison

| Feature | Hot | Cool | Cold | Archive |
|---------|-----|------|------|---------|
| Storage Cost | Highest | Medium | Lower | Lowest |
| Access Cost | Lowest | Higher | Higher | Highest |
| Availability | 99.9% | 99% | 99% | N/A (offline) |
| Min Storage Duration | None | 30 days | 90 days | 180 days |
| Data Access | Immediate | Immediate | Immediate | Requires rehydration |
| Latency | Milliseconds | Milliseconds | Milliseconds | Hours |

## Archive Tier Rehydration

### What is Rehydration?

Rehydration is the process of moving a blob from the Archive tier (offline) to an online tier (Hot, Cool, or Cold) so that it can be read or modified. Blobs in the Archive tier cannot be read or modified until they are rehydrated.

### Two Methods to Rehydrate Archived Blobs

#### Method 1: Copy Blob to Online Tier ✅

Use the **Copy Blob operation** to copy the archived blob to a new blob in an online tier (Hot or Cool).

**Important Requirement:**
- The destination blob must be in an **online tier** (Hot, Cool, or Cold)
- The destination must be in the **same region** as the source blob
- Cross-region rehydration is not supported

**Advantages:**
- Original blob remains in Archive tier
- No modification to source blob
- Can continue serving requests during rehydration
- New blob is available once copy completes

**Example using Azure CLI:**
```bash
# Copy archived blob to Hot tier
az storage blob copy start \
  --source-container archived-container \
  --source-blob myfile.txt \
  --destination-container active-container \
  --destination-blob myfile.txt \
  --account-name mystorageaccount \
  --tier Hot
```

**Example using REST API:**
```http
PUT https://mystorageaccount.blob.core.windows.net/destination-container/myblob HTTP/1.1
x-ms-access-tier: Hot
x-ms-copy-source: https://mystorageaccount.blob.core.windows.net/source-container/myblob
x-ms-version: 2021-06-08
Authorization: Bearer <token>
```

**Example using .NET SDK:**
```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

// Get source blob client (archived blob)
BlobClient sourceBlob = new BlobClient(
    connectionString, 
    "archived-container", 
    "myfile.txt"
);

// Get destination blob client
BlobClient destBlob = new BlobClient(
    connectionString, 
    "active-container", 
    "myfile.txt"
);

// Copy to Hot tier
CopyFromUriOperation copyOperation = await destBlob.StartCopyFromUriAsync(
    sourceBlob.Uri,
    new BlobCopyFromUriOptions
    {
        AccessTier = AccessTier.Hot
    }
);

// Wait for copy to complete
await copyOperation.WaitForCompletionAsync();
```

**Example using Python SDK:**
```python
from azure.storage.blob import BlobServiceClient, StandardBlobTier

# Initialize blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get source and destination blob clients
source_blob = blob_service_client.get_blob_client(
    container="archived-container",
    blob="myfile.txt"
)
dest_blob = blob_service_client.get_blob_client(
    container="active-container",
    blob="myfile.txt"
)

# Copy blob to Hot tier
dest_blob.start_copy_from_url(
    source_blob.url,
    standard_blob_tier=StandardBlobTier.HOT
)
```

#### Method 2: Set Blob Tier Operation ✅

Use the **Set Blob Tier operation** to change the blob's tier directly from Archive to an online tier.

**Important Requirement:**
- Can only rehydrate to **online tiers** (Hot, Cool, or Cold)
- Cannot rehydrate from Archive to Archive (even in different region)
- The blob remains in the same storage account and region

**Advantages:**
- Changes tier in place
- Same blob URL and properties maintained
- No duplicate storage costs during rehydration

**Disadvantages:**
- Blob is not accessible until rehydration completes
- Cannot serve requests during rehydration

**Example using Azure CLI:**
```bash
# Set blob tier from Archive to Hot
az storage blob set-tier \
  --container-name mycontainer \
  --name myfile.txt \
  --tier Hot \
  --account-name mystorageaccount \
  --rehydrate-priority Standard
```

**Example using REST API:**
```http
PUT https://mystorageaccount.blob.core.windows.net/mycontainer/myblob?comp=tier HTTP/1.1
x-ms-access-tier: Hot
x-ms-rehydrate-priority: Standard
x-ms-version: 2021-06-08
Authorization: Bearer <token>
```

**Example using .NET SDK:**
```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

BlobClient blobClient = new BlobClient(
    connectionString, 
    "mycontainer", 
    "myfile.txt"
);

// Set tier from Archive to Hot
await blobClient.SetAccessTierAsync(
    AccessTier.Hot,
    rehydratePriority: RehydratePriority.Standard
);
```

**Example using Python SDK:**
```python
from azure.storage.blob import BlobServiceClient, StandardBlobTier, RehydratePriority

# Initialize blob service client
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Get blob client
blob_client = blob_service_client.get_blob_client(
    container="mycontainer",
    blob="myfile.txt"
)

# Set blob tier from Archive to Hot
blob_client.set_standard_blob_tier(
    standard_blob_tier=StandardBlobTier.HOT,
    rehydrate_priority=RehydratePriority.standard
)
```

### ❌ Incorrect Methods

#### Set Blob Properties Operation ❌

**This does NOT work for rehydration**. The `Set Blob Properties` operation is used to set system properties such as:
- Content-Type
- Content-Encoding
- Content-Language
- Cache-Control
- Content-MD5

It **cannot** change the access tier.

```csharp
// This sets properties, NOT tier
await blobClient.SetHttpHeadersAsync(new BlobHttpHeaders
{
    ContentType = "application/pdf",
    ContentEncoding = "gzip"
});
```

#### Snapshot Blob Operation ❌

**This does NOT work for rehydration**. The `Snapshot Blob` operation creates a read-only snapshot of a blob at a specific point in time. It does not copy the blob to a different tier or rehydrate it.

```csharp
// This creates a snapshot, does NOT rehydrate
await blobClient.CreateSnapshotAsync();
```

## Rehydration Priority

When rehydrating blobs, you can set the priority:

### Standard Priority
- Default option
- Rehydration can take up to 15 hours
- Lower cost
- Suitable for non-urgent data access

### High Priority
- Faster rehydration (typically completes in less than 1 hour for objects under 10 GB)
- Higher cost
- Suitable for urgent data recovery scenarios

**Example with priority:**
```csharp
await blobClient.SetAccessTierAsync(
    AccessTier.Hot,
    rehydratePriority: RehydratePriority.High
);
```

```bash
az storage blob set-tier \
  --container-name mycontainer \
  --name myfile.txt \
  --tier Hot \
  --rehydrate-priority High \
  --account-name mystorageaccount
```

## Tier Transition Rules

### Supported Transitions

| From | To | Immediate | Notes |
|------|-----|-----------|-------|
| Hot | Cool | Yes | Online to online |
| Hot | Cold | Yes | Online to online |
| Hot | Archive | Yes | Online to offline |
| Cool | Hot | Yes | Online to online |
| Cool | Cold | Yes | Online to online |
| Cool | Archive | Yes | Online to offline |
| Cold | Hot | Yes | Online to online |
| Cold | Cool | Yes | Online to online |
| Cold | Archive | Yes | Online to offline |
| Archive | Hot | No | Requires rehydration (hours), same region |
| Archive | Cool | No | Requires rehydration (hours), same region |
| Archive | Cold | No | Requires rehydration (hours), same region |

### Key Points
- ✅ Transitions between online tiers (Hot, Cool, Cold) are immediate
- ✅ Transitions from online to Archive are immediate
- ⏱️ Transitions from Archive to any online tier require rehydration (several hours)
- 🌍 **Rehydration must occur in the same region** - cross-region rehydration is not supported
- ❌ Cannot rehydrate to Archive tier (must rehydrate to Hot, Cool, or Cold)
- ❌ Cannot read or modify blobs in Archive tier without rehydration first

## Monitoring Rehydration Status

### Check Archive Status (.NET)
```csharp
BlobProperties properties = await blobClient.GetPropertiesAsync();

if (properties.Value.AccessTier == AccessTier.Archive)
{
    Console.WriteLine("Blob is in Archive tier");
}

if (properties.Value.ArchiveStatus != null)
{
    Console.WriteLine($"Archive status: {properties.Value.ArchiveStatus}");
    // Possible values:
    // - rehydrate-pending-to-hot
    // - rehydrate-pending-to-cool
    // - rehydrate-pending-to-cold
}
```

### Check Archive Status (Azure CLI)
```bash
az storage blob show \
  --container-name mycontainer \
  --name myfile.txt \
  --account-name mystorageaccount \
  --query '{tier:properties.blobTier, archiveStatus:properties.archiveStatus}'
```

### Check Archive Status (Python)
```python
properties = blob_client.get_blob_properties()

if properties.blob_tier == 'Archive':
    print("Blob is in Archive tier")

if properties.archive_status:
    print(f"Archive status: {properties.archive_status}")
```

## Cost Considerations

### Storage Costs
- Archive: ~$0.002 per GB/month
- Cold: ~$0.0045 per GB/month
- Cool: ~$0.01 per GB/month
- Hot: ~$0.018 per GB/month

### Rehydration Costs
- Reading data from Archive incurs:
  - Rehydration fee (per GB)
  - Data retrieval fee (per GB)
  - Operations cost

### Early Deletion Fees
Deleting or moving blobs before the minimum storage duration results in a prorated early deletion fee:
- Cool: 30 days minimum
- Cold: 90 days minimum
- Archive: 180 days minimum

## Choosing the Right Tier - Practical Scenarios

### Scenario 1: 100 GB/day with 30-day retention and rare access

**Question**: Your application generates 100 GB of data per day, and you need to keep that data for 30 days before deleting it. You may need to access the data occasionally. You will use a lifecycle rule to automatically delete the data after 30 days, and you won't likely need to read that data. Which is the most cost-effective storage option?

**Answer**: **Azure Blob Storage - Cool Tier** ✅

**Why Cool Tier is correct:**
- Lower storage costs compared to Hot Tier
- Data is infrequently accessed (matches Cool Tier use case)
- 30-day retention aligns with Cool Tier's minimum storage duration
- Still provides immediate access when occasional reads are needed
- Lifecycle rules can automatically delete data after 30 days

**Why other options are not optimal:**

| Option | Why Not Suitable |
|--------|------------------|
| **Hot Tier** ❌ | Designed for frequently accessed data with low latency. Higher storage costs are unnecessary when data won't be read often. |
| **Premium Tier** ❌ | Designed for high-performance scenarios requiring low-latency access. Overkill for data that's rarely accessed and will be deleted after 30 days. |
| **Azure Files** ❌ | File share service suited for shared file storage scenarios, not optimized for large-scale data retention and automatic deletion workflows. |
| **Archive Tier** ❌ | While cheapest for storage, the 180-day minimum retention requirement doesn't match the 30-day deletion need, and rehydration costs/delays make occasional access impractical. |

**Key Decision Factors:**
- **Access frequency**: Rare → Cool or Cold (not Hot)
- **Retention period**: 30 days → Cool Tier (matches minimum duration)
- **Need for immediate access**: Yes (occasionally) → Cool (not Archive)
- **Lifecycle automation**: Cool Tier supports lifecycle policies for automatic deletion

### Scenario 2: Migrating 5 TB of rarely accessed files with 24-hour availability requirement

**Question**: Your on-premises network contains a file server with 5 TB of company files that are accessed rarely. You need to copy the files to Azure Storage with the following requirements:
- Files must be available within 24 hours of being requested
- Storage costs must be minimized

Which two storage solutions achieve this goal?

**Correct Answers:**

1. **Create an Azure Blob storage account configured for Cool default access tier, create a blob container, copy files to the container, and set each file to Archive access tier** ✅

2. **Create a General-Purpose v2 storage account configured for Hot default access tier, create a blob container, copy files to the container, and set each file to Archive access tier** ✅

**Why These Solutions Work:**

Both solutions leverage the **Archive tier**, which provides the **lowest storage cost** in Azure Blob Storage. The key points are:

| Aspect | Explanation |
|--------|-------------|
| **Archive tier cost** | Most cost-effective option at ~$0.002/GB/month (vs. Cool at ~$0.01/GB/month or Hot at ~$0.018/GB/month) |
| **24-hour availability** | Archive rehydration with Standard priority takes **up to 15 hours**, which meets the 24-hour requirement |
| **Upload strategy** | Initial upload via Cool (lower write costs) or Hot (both valid) before transitioning to Archive |
| **Access pattern** | Rarely accessed files align perfectly with Archive tier use case |

**Solution 1 Benefits (Cool → Archive):**
- Lower initial write costs when uploading through Cool tier
- Optimal cost at every stage of the process

**Solution 2 Benefits (Hot → Archive):**
- Higher write costs initially, but same long-term storage cost once in Archive
- Still meets cost minimization requirement through Archive tier

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|--------------|
| **General-Purpose v1 (GPv1) with blob container** ❌ | GPv1 accounts do **NOT support blob access tiers** (Hot, Cool, Archive), making them unsuitable for tiered, cost-optimized storage strategies |
| **General-Purpose v1 (GPv1) with file share** ❌ | GPv1 does not support access tiers, and Azure Files is more expensive than Blob Archive tier for cold data |
| **General-Purpose v2 (GPv2) Cool tier with file share** ❌ | **Azure Files does NOT support Archive tier**. While Cool tier reduces costs compared to Hot, it cannot match the cost-effectiveness of Blob Archive tier (~$0.01/GB vs. ~$0.002/GB/month) |

**Critical Storage Account and Service Tier Support:**

| Storage Account Type | Blob Access Tiers Support | Azure Files Tiers Support |
|---------------------|--------------------------|--------------------------|
| **GPv1** | ❌ No Hot/Cool/Archive support | ❌ No tier support |
| **GPv2** | ✅ Supports Hot/Cool/Cold/Archive | ⚠️ Only Hot/Cool (NO Archive) |
| **Premium** | ❌ No access tiers (SSD-based) | ❌ No access tiers (SSD-based) |

**Key Takeaways:**
- ✅ **Archive tier** is the most cost-effective for rarely accessed data
- ✅ Archive rehydration (**up to 15 hours**) fits within 24-hour availability requirement
- ✅ Use **GPv2** storage accounts for access tier support
- ✅ Use **Blob Storage** (not Azure Files) for Archive tier support
- ❌ GPv1 accounts do NOT support blob access tiers
- ❌ Azure Files do NOT support Archive tier
- 💡 Default account tier (Hot/Cool) only matters during initial upload; final Archive tier determines long-term costs

## Best Practices

1. **Plan rehydration time**: Archive rehydration can take up to 15 hours, so plan accordingly
2. **Use Copy Blob for availability**: If you need the data to remain accessible during rehydration, use Copy Blob
3. **Use Set Blob Tier for cost savings**: If you can wait for rehydration, Set Blob Tier avoids duplicate storage costs
4. **Set appropriate priority**: Use High priority only when necessary due to higher costs
5. **Ensure same region**: Destination blob for rehydration must be in the same region as the source
6. **Target online tiers only**: Can only rehydrate to Hot, Cool, or Cold tiers (not Archive)
7. **Monitor minimum storage durations**: Ensure blobs stay in each tier for the minimum duration to avoid early deletion fees
8. **Consider lifecycle policies**: Automate tier transitions based on age or access patterns
9. **Test rehydration processes**: Validate your rehydration procedures before relying on them in production
10. **Calculate total cost**: Consider storage, access, and rehydration costs when choosing tiers

## Complete Rehydration Workflow Example

### Scenario: Rehydrate archived log files for analysis

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

public async Task RehydrateAndAnalyzeLogsAsync(string connectionString)
{
    BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
    BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("logs");
    
    // List all archived blobs with specific prefix
    await foreach (BlobItem blobItem in containerClient.GetBlobsAsync(
        prefix: "2024/",
        traits: BlobTraits.All))
    {
        if (blobItem.Properties.AccessTier == AccessTier.Archive)
        {
            BlobClient blobClient = containerClient.GetBlobClient(blobItem.Name);
            
            Console.WriteLine($"Rehydrating {blobItem.Name}...");
            
            // Method 1: Set blob tier (in-place rehydration)
            await blobClient.SetAccessTierAsync(
                AccessTier.Hot,
                rehydratePriority: RehydratePriority.High
            );
            
            // Wait for rehydration to complete
            bool isRehydrated = false;
            while (!isRehydrated)
            {
                BlobProperties properties = await blobClient.GetPropertiesAsync();
                
                if (properties.Value.AccessTier == AccessTier.Hot && 
                    properties.Value.ArchiveStatus == null)
                {
                    isRehydrated = true;
                    Console.WriteLine($"{blobItem.Name} rehydrated successfully");
                }
                else
                {
                    Console.WriteLine($"Status: {properties.Value.ArchiveStatus}");
                    await Task.Delay(TimeSpan.FromMinutes(5));
                }
            }
            
            // Now you can read the blob
            BlobDownloadInfo download = await blobClient.DownloadAsync();
            // Process the blob...
        }
    }
}
```

## Key Takeaways

### ✅ Two Valid Rehydration Methods:
1. **Copy Blob Operation** - Copy archived blob to a new blob in Hot, Cool, or Cold tier
2. **Set Blob Tier Operation** - Change the blob's tier directly from Archive to online tier

### ❌ Invalid Methods:
1. **Set Blob Properties** - Only sets HTTP headers and system properties, NOT tier
2. **Snapshot Blob** - Creates read-only snapshots, does NOT rehydrate or change tier

### 🎯 Critical Rehydration Requirements:
- **Destination tier**: Must be an online tier (Hot, Cool, or Cold) - NOT Archive
- **Region**: Destination must be in the **same region** as the source blob
- **Cross-region**: Cross-region rehydration is NOT supported

### Remember:
- Archive is an **offline tier** - blobs must be rehydrated before access
- Rehydration takes time (up to 15 hours with Standard priority)
- Choose Copy Blob for continued availability, Set Blob Tier for cost optimization
- Always rehydrate to online tiers (Hot, Cool, Cold) in the same region
- Consider minimum storage durations to avoid early deletion fees

## References

- [Hot, Cool, and Archive access tiers for blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/access-tiers-overview)
- [Rehydrate an archived blob to an online tier](https://learn.microsoft.com/en-us/azure/storage/blobs/archive-rehydrate-overview)
- [Set Blob Tier operation](https://learn.microsoft.com/en-us/rest/api/storageservices/set-blob-tier)
- [Copy Blob operation](https://learn.microsoft.com/en-us/rest/api/storageservices/copy-blob)
- [Blob Storage pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/)
