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
- [Azure Storage SLAs](https://azure.microsoft.com/en-us/support/legal/sla/storage/)
