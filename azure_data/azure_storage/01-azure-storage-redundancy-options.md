# Azure Storage Redundancy Options

## Table of Contents

- [Overview](#overview)
- [Redundancy in the Primary Region](#redundancy-in-the-primary-region)
  - [Locally Redundant Storage (LRS)](#locally-redundant-storage-lrs)
  - [Zone-Redundant Storage (ZRS)](#zone-redundant-storage-zrs)
- [Redundancy in a Secondary Region](#redundancy-in-a-secondary-region)
  - [Geo-Redundant Storage (GRS)](#geo-redundant-storage-grs)
  - [Geo-Zone-Redundant Storage (GZRS)](#geo-zone-redundant-storage-gzrs)
- [Redundancy Options Comparison](#redundancy-options-comparison)
- [Availability and Durability](#availability-and-durability)
- [Key Exam Points](#key-exam-points)
- [Disaster Recovery and Failover](#disaster-recovery-and-failover)
  - [Failover Procedure for General-Purpose v2 Accounts](#failover-procedure-for-general-purpose-v2-accounts)
  - [Q&A: Disaster Recovery Scenarios](#qa-disaster-recovery-scenarios)
  - [Practice Question: Converting Storage Account Redundancy to GRS](#practice-question-converting-storage-account-redundancy-to-grs)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Storage always stores multiple copies of your data so that it is protected from planned and unplanned events, including:
- Transient hardware failures
- Network or power outages
- Massive natural disasters

Redundancy ensures that your storage account meets its availability and durability targets even in the face of failures. When deciding which redundancy option is best for your scenario, consider the tradeoffs between lower costs and higher availability.

## Redundancy in the Primary Region

Data in an Azure Storage account is always replicated three times in the primary region. Azure Storage offers two options for how your data is replicated in the primary region:

### Locally Redundant Storage (LRS)

**How it works:**
- Replicates your data **3 times** within a single data center in the primary region
- All 3 copies are within a single physical location
- Protects against server rack and drive failures

**Characteristics:**
- **Number of copies**: 3
- **Location**: Single data center
- **Durability**: 99.999999999% (11 nines) over a year
- **Use case**: Lowest-cost option, data can be reconstructed easily, or data is not critical
- **Limitations**: Not protected against data center-level disasters

**Example scenarios:**
- Non-critical data that can be easily reconstructed
- Data governance requirements restrict data to single country/region
- Cost-sensitive applications with low criticality

```bash
# Create storage account with LRS
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_LRS
```

---

#### Practice Question: LRS Data Copies

**Question:**
When deploying an Azure Storage account, and you choose Locally Redundant Storage (LRS), how many copies of your data does Azure keep?

**Options:**
1. ✅ **3**
2. ❌ 1 copy in each Availability Zone
3. ❌ 1
4. ❌ 6

**Answer: 3**

**Explanation:**
Azure Storage always stores multiple copies of your data so that it is protected from planned and unplanned events, including transient hardware failures, network or power outages, and massive natural disasters. Redundancy ensures that your storage account meets its availability and durability targets even in the face of failures.

**Locally redundant storage (LRS) copies your data synchronously three times within a single physical location in the primary region.** LRS is the least expensive replication option, but is not recommended for applications requiring high availability or durability.

**Why other options are incorrect:**
- ❌ **1 copy in each Availability Zone**: This describes ZRS, not LRS. LRS uses a single data center, not availability zones.
- ❌ **1**: Azure Storage always maintains multiple copies for redundancy. A single copy would provide no protection.
- ❌ **6**: This is the number of copies for GRS/GZRS (3 in primary + 3 in secondary region).

**Reference:** [Azure Storage redundancy](https://docs.microsoft.com/en-us/azure/storage/common/storage-redundancy)

---

### Zone-Redundant Storage (ZRS)

**How it works:**
- Replicates your data synchronously across **3 Azure availability zones** in the primary region
- **Important**: Azure keeps **3 copies total** (one copy in each availability zone)
- Each availability zone is a separate physical location with independent power, cooling, and networking

**Characteristics:**
- **Number of copies**: 3 (one in each availability zone)
- **Location**: 3 separate availability zones within the primary region
- **Durability**: 99.9999999999% (12 nines) over a year
- **Use case**: High availability applications, compliance requirements for data to stay within region
- **Protection**: Protects against data center-level failures

**Key Exam Point:**
> **Question**: When deploying an Azure Storage account with Zone Redundant Storage (ZRS), how many copies of your data does Azure keep?
> 
> **Answer**: 3 copies (one copy in each of the 3 availability zones)
> 
> **Common misconception**: Some might think "3 copies in each availability zone" = 9 copies total, but this is **incorrect**. ZRS keeps exactly 3 copies total, distributed across 3 availability zones.

**Example scenarios:**
- Applications requiring high availability
- Mission-critical applications
- Applications that need to continue functioning during zone outages
- Regulatory requirements to keep data within a specific region

```bash
# Create storage account with ZRS
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_ZRS
```

**Supported regions:**
Not all regions support ZRS. Check the Azure documentation for current availability.

## Redundancy in a Secondary Region

For applications requiring high durability, you can replicate data to a secondary region that is hundreds of miles away from the primary region.

### Geo-Redundant Storage (GRS)

**How it works:**
- Copies data synchronously **3 times** within a single physical location in the primary region using LRS
- Then copies data asynchronously to a single physical location in the secondary region
- Data in the secondary region is also replicated **3 times** using LRS

**Characteristics:**
- **Number of copies**: 6 total (3 in primary region + 3 in secondary region)
- **Primary region**: 3 copies using LRS
- **Secondary region**: 3 copies using LRS
- **Durability**: 99.99999999999999% (16 nines) over a year
- **Secondary region access**: Read access requires RA-GRS (Read-Access GRS)
- **Use case**: Maximum durability, disaster recovery

```bash
# Create storage account with GRS
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_GRS
```

### Geo-Zone-Redundant Storage (GZRS)

**How it works:**
- Copies data synchronously across **3 Azure availability zones** in the primary region (ZRS)
- Then copies data asynchronously to a single physical location in the secondary region
- Data in the secondary region is replicated **3 times** using LRS

**Characteristics:**
- **Number of copies**: 6 total (3 in primary region across zones + 3 in secondary region)
- **Primary region**: 3 copies using ZRS (across availability zones)
- **Secondary region**: 3 copies using LRS
- **Durability**: 99.99999999999999% (16 nines) over a year
- **Secondary region access**: Read access requires RA-GZRS (Read-Access GZRS)
- **Use case**: Maximum availability and durability, critical applications

**Example scenarios:**
- Applications requiring highest consistency, durability, and availability
- Mission-critical data that must survive regional disasters
- Wide-area disaster recovery scenarios

```bash
# Create storage account with GZRS
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_GZRS
```

## Redundancy Options Comparison

| Redundancy Option | Number of Copies | Copy Locations | Durability | Use Case | Protects Against |
|------------------|------------------|----------------|------------|----------|------------------|
| **LRS** | 3 | Single data center | 11 nines | Lowest cost, non-critical | Server rack/drive failures |
| **ZRS** | 3 | 3 availability zones | 12 nines | High availability | Data center failures |
| **GRS** | 6 | Primary region (LRS) + Secondary region (LRS) | 16 nines | Disaster recovery | Regional disasters |
| **GZRS** | 6 | Primary region (ZRS) + Secondary region (LRS) | 16 nines | Maximum availability & durability | Zone and regional failures |

## Availability and Durability

### Durability Targets

| Redundancy | Durability (annual) | Description |
|-----------|-------------------|-------------|
| LRS | 99.999999999% (11 9's) | At least 99.999999999% durability of objects |
| ZRS | 99.9999999999% (12 9's) | At least 99.9999999999% durability of objects |
| GRS/RA-GRS | 99.99999999999999% (16 9's) | At least 99.99999999999999% durability of objects |
| GZRS/RA-GZRS | 99.99999999999999% (16 9's) | At least 99.99999999999999% durability of objects |

### Availability SLAs

Availability varies by redundancy option and whether you have read access to the secondary region enabled (RA-GRS, RA-GZRS).

**Primary Region Read Requests:**
- LRS, ZRS, GRS, GZRS: 99.9% (Hot, Cool), 99% (Cold, Archive)

**Secondary Region Read Requests (RA-GRS, RA-GZRS):**
- 99.9% (Hot, Cool), 99% (Cold)

## Key Exam Points

### Question 5 Breakdown

**Question**: When deploying an Azure Storage account, and you choose Zone Redundant Storage (ZRS), how many copies of your data does Azure keep?

**Answer Options:**
1. ❌ 1 - Incorrect (no redundancy)
2. ❌ 3 copies in each Availability Zone - Incorrect (would be 9 copies total)
3. ✅ **3** - Correct
4. ❌ 6 - Incorrect (this would be GRS/GZRS)

**Explanation:**
Zone-redundant storage (ZRS) copies your data **synchronously across three Azure availability zones in the primary region**. This means:
- Total copies: **3**
- Distribution: **1 copy per availability zone**
- **NOT** 3 copies in each zone (which would total 9 copies)

For applications requiring high availability, Microsoft recommends using ZRS in the primary region, and also replicating to a secondary region using GZRS.

### Memory Aid

- **LRS**: 3 copies in 1 location = 3 total
- **ZRS**: 3 zones with 1 copy each = 3 total
- **GRS**: 3 copies in primary (LRS) + 3 in secondary (LRS) = 6 total
- **GZRS**: 3 copies in primary (ZRS) + 3 in secondary (LRS) = 6 total

## Disaster Recovery and Failover

### Failover Procedure for General-Purpose v2 Accounts

When planning disaster recovery for Azure Storage accounts, it's essential to understand the correct sequence of actions for a storage account failover that minimizes downtime and ensures data availability.

#### Requirements for Proper Failover

- Apps must be able to access the storage account after a failover
- Ability to fail back the storage account to the original location
- Minimal downtime during the failover process

#### Correct Failover Sequence

**Step 1: Before a failover, configure geo-redundant storage (GRS) replication for the storage account**

GRS replication is essential before initiating any failover. It ensures that your data is asynchronously replicated to a secondary region, providing a backup in case of a regional disaster. This step must be completed in advance to ensure that the data is available in another region before initiating a failover.

**Key points:**
- GRS replicates data to a secondary region hundreds of miles away from the primary region
- Replication is asynchronous, typically with a 15-minute RPO
- This configuration is a prerequisite for performing a failover

**Step 2: Initiate a failover**

Once GRS replication is configured and the primary region becomes unavailable, you can initiate a failover. This action switches the storage account to the secondary region.

**What happens during failover:**
- DNS entries for the storage account are updated to point to the secondary region
- The secondary region becomes the new primary region
- Applications can continue to access the storage account with minimal downtime
- No changes are required in application connection strings (same endpoint)

**Step 3: After a failover, configure geo-redundant storage (GRS) replication for the storage account**

Once the failover is complete and the storage account is now active in the former secondary region (now the new primary), it's critical to re-enable GRS replication.

**Why this is important:**
- Ensures data continues to be protected by being replicated to a new secondary region
- Maintains high availability and durability standards
- Prepares the storage account for potential future failovers
- Without re-enabling GRS, the account would only have local redundancy (LRS) in the new region

#### Failover Process Diagram

```
STEP 1: Configure GRS Before Failover
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Primary Region (East US)          Secondary Region (West US)  │
│  ┌─────────────────┐               ┌─────────────────┐        │
│  │  Storage Account│──── GRS ─────>│  Storage Account│        │
│  │   (Active)      │  Replication  │   (Passive)     │        │
│  │   ✓ Read/Write  │               │   ✗ No Access   │        │
│  └─────────────────┘               └─────────────────┘        │
│         │                                                       │
│         │ Apps connect here                                    │
│         ▼                                                       │
│   [Application]                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


STEP 2: Initiate Failover (Primary Region Unavailable)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Primary Region (East US)          Secondary Region (West US)  │
│  ┌─────────────────┐               ┌─────────────────┐        │
│  │  Storage Account│    ✗ Outage   │  Storage Account│        │
│  │   (Unavailable) │               │  (Promoting...) │        │
│  │   ✗ Offline     │               │   → Active      │        │
│  └─────────────────┘               └─────────────────┘        │
│                                              │                  │
│                         DNS Update           │                  │
│                         Redirects traffic ───┘                  │
│                                              ▼                  │
│                                        [Application]            │
│                                     (Same endpoint URL)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


STEP 3: After Failover - Re-configure GRS
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Original Region (East US)         New Primary (West US)       │
│  ┌─────────────────┐               ┌─────────────────┐        │
│  │  Storage Account│<──── GRS ─────│  Storage Account│        │
│  │  (New Secondary)│  Replication  │   (Now Primary) │        │
│  │   ✗ No Access   │               │   ✓ Read/Write  │        │
│  └─────────────────┘               └─────────────────┘        │
│                                              │                  │
│                                              │                  │
│                                              ▼                  │
│                                        [Application]            │
│                                     (No changes needed)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Key Points:
• Apps use the same endpoint URL throughout the failover
• DNS automatically redirects traffic to the new primary region
• Re-enabling GRS protects data and enables future failback
• Typical failover time: ~1 hour
```

#### Common Failover Scenarios

**Scenario: Regional Outage**
1. Pre-configured GRS ensures data exists in secondary region
2. Primary region becomes unavailable
3. Initiate customer-managed failover to secondary region
4. Secondary region becomes primary
5. Re-configure GRS to protect data in new primary region

#### Important Considerations

- **Failover time**: Account failover typically takes about one hour
- **Data loss**: Some data loss may occur (up to 15 minutes based on RPO)
- **Billing**: You're billed for the redundancy option configured
- **Failback**: To fail back to the original region, you must perform another failover after the original region is restored
- **Account type**: This procedure applies to general-purpose v2, general-purpose v1, and Blob storage accounts

### Q&A: Disaster Recovery Scenarios

**Q: You plan to use Azure Storage to store data assets. You need to identify the procedure to fail over a general-purpose v2 account as part of a disaster recovery plan. The solution must meet the following requirements:**

- Apps must be able to access the storage account after a failover
- You must be able to fail back the storage account to the original location
- Downtime must be minimized

**Which three actions should you perform in sequence?**

**Available Actions:**
1. After a failover, configure geo-redundant storage (GRS) replication for the storage account
2. Initiate a failover
3. Before a failover, configure zone-redundant storage (ZRS) replication for the storage account
4. Before a failover, configure geo-redundant storage (GRS) replication for the storage account
5. After a failover, configure zone-redundant storage (ZRS) replication for the storage account

**Correct Answer: 4 → 2 → 1**

**Explanation:**

**Action 4 (First)**: Before a failover, configure geo-redundant storage (GRS) replication for the storage account
- GRS replication must be configured in advance to ensure data is available in a secondary region
- This is a prerequisite for being able to perform a failover
- Without GRS, there is no secondary region to fail over to

**Action 2 (Second)**: Initiate a failover
- Switches the storage account to the secondary region
- DNS entries are automatically updated to point to the new primary region
- Applications continue to work without connection string changes
- Minimizes downtime by using pre-replicated data

**Action 1 (Third)**: After a failover, configure geo-redundant storage (GRS) replication for the storage account
- Re-enables geo-replication after the failover is complete
- Ensures continued data protection in the new primary region
- Maintains the ability to perform future failovers if needed
- Without this step, the account would only have LRS protection

**Why other options are incorrect:**

- **ZRS before failover (Action 3)**: ZRS only provides redundancy within a single region and doesn't enable failover to a secondary region
- **ZRS after failover (Action 5)**: While ZRS is good for availability within a region, GRS is necessary to maintain disaster recovery capabilities and enable failback

---

### Practice Question: Storage Solution for Multiple Tables

**Question:**
You need to recommend a data storage solution that meets the following requirements:

- Ensures that applications can access the data by using a REST connection
- Hosts 20 independent tables of varying sizes and usage patterns
- Automatically replicates the data to a second Azure region
- Minimizes costs

What should you recommend?

**Options:**
1. ❌ An Azure SQL Database elastic database pool that uses geo-replication
2. ❌ Tables in an Azure Storage account that use read-access geo-redundant storage (RA-GRS)
3. ✅ **Tables in an Azure Storage account that use geo-redundant storage (GRS)**
4. ❌ An Azure SQL Database that uses active geo-replication

**Answer: Tables in an Azure Storage account that use geo-redundant storage (GRS)**

**Explanation:**

**Why GRS is the correct answer:**
- **Azure Table storage** offers a low-cost, highly durable solution for storing large volumes of semi-structured data using NoSQL key-value storage
- **GRS** provides automatic replication of the data to a secondary Azure region for disaster recovery, fulfilling the requirement for regional redundancy
- While GRS does not offer read access to the secondary region (unlike RA-GRS), the requirement only states that data must be **replicated**—not that it must be readable from the replica
- **REST API support**: Azure Table storage natively supports REST-based access, enabling applications to interact with the data directly through HTTP endpoints
- **Cost-effective**: Table storage with GRS is significantly cheaper than SQL Database solutions for hosting multiple independent tables

**Why other options are incorrect:**

**❌ Tables in an Azure Storage account that use read-access geo-redundant storage (RA-GRS):**
- Although RA-GRS provides read access to the replicated data in the secondary region, it incurs **higher cost** than GRS
- Since the requirement is to **minimize cost** and does not mandate read access from the secondary region, RA-GRS adds unnecessary expense
- RA-GRS is the correct choice only when applications need to read from the secondary region during failover or for load distribution

**❌ An Azure SQL Database elastic database pool that uses geo-replication:**
- While elastic pools can host multiple databases and support geo-replication, this is a **relational database solution** that is **more expensive** than Table storage
- Azure SQL Database does not natively expose data through REST APIs without adding additional service layers or APIs (such as Azure App Service or Azure Functions)
- Elastic pools are designed for scenarios requiring complex queries, transactions, and relational data models—overkill for simple table storage needs
- Cost is significantly higher compared to Table storage

**❌ An Azure SQL Database that uses active geo-replication:**
- Similar to elastic pools, Azure SQL Database is designed for relational data with high availability and performance needs
- **Higher cost** compared to Table storage
- Does not support REST-based interaction natively
- Active geo-replication provides multiple readable secondaries, but at a premium cost that exceeds requirements

**Key Differences: GRS vs. RA-GRS**

| Feature | GRS | RA-GRS |
|---------|-----|---------|
| **Replication** | ✅ Automatic to secondary region | ✅ Automatic to secondary region |
| **Read access to secondary** | ❌ No (only after failover) | ✅ Yes (always available) |
| **Cost** | 💰 Lower | 💰💰 Higher |
| **Use case** | Disaster recovery with cost optimization | Active read from secondary region for load distribution or DR testing |
| **Endpoint** | Single endpoint | Two endpoints (primary + secondary) |

**When to choose:**
- **GRS**: When you need disaster recovery capability but don't need to read from the secondary region (most common scenario)
- **RA-GRS**: When applications need to actively read from the secondary region for load balancing, DR testing, or reducing latency for geographically distributed users

**Azure Table Storage Benefits:**
- **REST API**: Native support for HTTP-based access patterns
- **Scalability**: Handles tables of varying sizes automatically
- **Independence**: Each table can scale independently
- **Cost**: Pay only for storage used, no per-database costs
- **Schema flexibility**: NoSQL structure accommodates varying data patterns

**Reference(s):**
- [Azure Storage redundancy](https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy)
- [Azure Table storage overview](https://learn.microsoft.com/en-us/azure/storage/tables/table-storage-overview)
- [Azure SQL Database REST API](https://learn.microsoft.com/en-us/rest/api/sql/)

**Domain:** Design data storage solutions

---

### Practice Question: Converting Storage Account Redundancy to GRS

**Scenario:**

You have multiple storage accounts defined under your subscription:

| Storage Account | Account Kind | Replication | Access Tier |
|-----------------|--------------|-------------|-------------|
| Store1 | BlobStorage | LRS | Hot |
| Store2 | StorageV2 | ZRS | Cool |
| Store3 | StorageV2 | LRS | Hot |
| Store4 | Storage (v1) | GRS | N/A |

**Question:**
Can you convert Store3 to a GRS account?

**Options:**
1. ✅ **Yes**
2. ❌ No

**Answer: Yes**

---

### Explanation

**Yes, you can convert Store3 to a GRS (Geo-Redundant Storage) account.**

Store3 is a **StorageV2 (general-purpose v2)** account with **LRS** replication. General-purpose v2 accounts support changing the replication type after creation, including conversion to GRS.

**Why the conversion is possible:**

| Factor | Store3 Status | GRS Compatibility |
|--------|---------------|-------------------|
| Account Kind | StorageV2 ✅ | Supported |
| Current Replication | LRS | Can upgrade to GRS |
| Access Tier | Hot | Supported |

**GRS Benefits:**
- **Data replication to a secondary region**: Ensures data durability and high availability in case of a regional outage
- **Disaster recovery capabilities**: Provides protection against regional disasters
- **16 nines durability**: 99.99999999999999% durability over a year

---

### Storage Account Redundancy Conversion Rules

```plaintext
Redundancy Conversion Matrix:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Allowed Conversions:                                          │
│                                                                 │
│  LRS ──────────────────► GRS    ✅ (Store3 scenario)           │
│  LRS ──────────────────► ZRS    ✅ (live migration available)  │
│  LRS ──────────────────► GZRS   ✅                              │
│                                                                 │
│  ZRS ──────────────────► GZRS   ✅                              │
│  ZRS ──────────────────► GRS    ❌ (must go through LRS first) │
│                                                                 │
│  GRS ──────────────────► LRS    ✅                              │
│  GRS ──────────────────► GZRS   ✅ (in supported regions)      │
│                                                                 │
│  GZRS ─────────────────► GRS    ✅                              │
│  GZRS ─────────────────► ZRS    ✅                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### How to Convert Store3 to GRS

**Azure Portal:**
1. Navigate to the storage account (Store3)
2. Under **Settings**, select **Configuration**
3. Change **Replication** from LRS to GRS
4. Click **Save**

**Azure CLI:**

```bash
# Convert Store3 from LRS to GRS
az storage account update \
  --name Store3 \
  --resource-group myResourceGroup \
  --sku Standard_GRS
```

**PowerShell:**

```powershell
# Convert Store3 from LRS to GRS
Set-AzStorageAccount `
  -ResourceGroupName "myResourceGroup" `
  -Name "Store3" `
  -SkuName "Standard_GRS"
```

### Account Kind Compatibility

| Account Kind | Supports GRS | Notes |
|--------------|--------------|-------|
| **StorageV2** (general-purpose v2) | ✅ Yes | Full support, recommended |
| **Storage** (general-purpose v1) | ✅ Yes | Legacy, consider upgrading |
| **BlobStorage** | ✅ Yes | Blob-only accounts |
| **BlockBlobStorage** | ❌ No | Premium only, LRS/ZRS only |
| **FileStorage** | ❌ No | Premium only, LRS/ZRS only |

### Why Other Storage Accounts May Have Limitations

| Storage Account | Can Convert to GRS? | Reason |
|-----------------|---------------------|--------|
| Store1 (BlobStorage, LRS) | ✅ Yes | BlobStorage supports GRS |
| Store2 (StorageV2, ZRS) | ⚠️ Indirect | Must change to LRS first, then to GRS |
| Store3 (StorageV2, LRS) | ✅ Yes | Direct conversion supported |
| Store4 (Storage v1, GRS) | Already GRS | No conversion needed |

### Key Takeaways

1. **StorageV2 accounts support redundancy changes**: Including conversion from LRS to GRS
2. **GRS provides geo-redundancy**: Data is replicated to a secondary region
3. **Conversion is non-disruptive**: No downtime required for the change
4. **Premium storage accounts have limitations**: BlockBlobStorage and FileStorage don't support GRS
5. **ZRS to GRS requires intermediate step**: Must convert to LRS first

**Reference(s):**
- [Change how a storage account is replicated](https://learn.microsoft.com/en-us/azure/storage/common/redundancy-migration)
- [Azure Storage redundancy](https://learn.microsoft.com/en-us/azure/storage/common/storage-redundancy)

**Domain:** Design data storage solutions

---

## Best Practices

1. **Choose ZRS for high availability**: When applications need to continue operating during zone outages
2. **Use GRS/GZRS for disaster recovery**: When data must survive regional disasters
3. **Consider compliance requirements**: Some regulations require data to stay within specific regions (use LRS or ZRS)
4. **Balance cost vs. protection**: Higher redundancy = higher cost but better protection
5. **Evaluate RPO (Recovery Point Objective)**: 
   - LRS/ZRS: Near-zero RPO (immediate replication within region)
   - GRS/GZRS: Asynchronous replication to secondary (typically 15 minutes RPO)
6. **Enable RA-GRS/RA-GZRS when needed**: Provides read access to secondary region data
7. **Understand failover implications**: Automatic failover is not enabled by default for GRS/GZRS
8. **Test disaster recovery**: Regularly test your disaster recovery procedures

## References

- [Azure Storage redundancy](https://docs.microsoft.com/en-us/azure/storage/common/storage-redundancy)
- [Locally redundant storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-redundancy#locally-redundant-storage)
- [Zone-redundant storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-redundancy#zone-redundant-storage)
- [Geo-redundant storage](https://docs.microsoft.com/en-us/azure/storage/common/storage-redundancy#geo-redundant-storage)
- [Azure Storage disaster recovery guidance](https://learn.microsoft.com/en-us/azure/storage/common/storage-disaster-recovery-guidance)
- [Azure Storage SLAs](https://azure.microsoft.com/en-us/support/legal/sla/storage/)
