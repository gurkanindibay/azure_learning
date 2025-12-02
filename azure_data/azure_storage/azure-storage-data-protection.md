# Azure Storage Data Protection Features

## Table of Contents

- [Overview](#overview)
- [Point-in-Time Restore](#point-in-time-restore)
  - [What is Point-in-Time Restore?](#what-is-point-in-time-restore)
  - [Key Features](#key-features)
  - [Prerequisites](#prerequisites)
  - [Limitations](#limitations)
  - [How to Enable](#how-to-enable)
  - [Performing a Restore](#performing-a-restore)
- [Soft Delete](#soft-delete)
  - [Soft Delete for Blobs](#soft-delete-for-blobs)
  - [Soft Delete for Containers](#soft-delete-for-containers)
- [Blob Versioning](#blob-versioning)
- [Azure Backup for Blobs](#azure-backup-for-blobs)
- [Immutable Storage for Blob Data](#immutable-storage-for-blob-data)
  - [Time-Based Retention Policy](#time-based-retention-policy)
  - [Legal Hold](#legal-hold)
  - [Immutability Policy Comparison](#immutability-policy-comparison)
- [Blob Index Tags](#blob-index-tags)
  - [Blob Index Tags vs Other Blob Attributes](#blob-index-tags-vs-other-blob-attributes)
- [Feature Comparison](#feature-comparison)
- [Exam Question Analysis](#exam-question-analysis)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Storage provides multiple data protection features to help you recover from accidental deletion or corruption. Understanding the differences between these features is crucial for both exam preparation and real-world implementation.

| Feature | Scope | Protection Type | Use Case |
|---------|-------|-----------------|----------|
| **Point-in-Time Restore** | Block blob data | Restore to earlier state | Accidental deletion/corruption recovery |
| **Soft Delete for Blobs** | Individual blobs | Retain deleted blobs | Recover deleted blobs |
| **Soft Delete for Containers** | Containers | Retain deleted containers | Recover deleted containers |
| **Blob Versioning** | Individual blobs | Maintain previous versions | Track and restore previous versions |
| **Azure Backup** | Storage account | Operational backup | Enterprise backup solution |

## Point-in-Time Restore

### What is Point-in-Time Restore?

**Point-in-time restore** protects against accidental deletion or corruption by enabling you to **restore block blob data to an earlier state**. This feature is useful when:

- A user or application accidentally deletes data
- An application error corrupts data
- Testing scenarios require reverting a data set to a known state before running further tests

> 💡 **Exam Tip**: Point-in-time restore is the feature that allows you to restore **one or more containers** to an earlier state. This is different from soft delete which only recovers deleted items.

### Key Features

- **Granular Restore**: Restore specific containers or ranges of blobs
- **Restore to Any Point**: Restore data to any point within the retention period
- **Non-Destructive**: Creates a new restore point without affecting current data
- **Container-Level Restore**: Can restore entire containers to a previous state

### Prerequisites

Point-in-time restore requires the following features to be enabled:

1. **Blob Versioning** - Must be enabled
2. **Soft Delete for Blobs** - Must be enabled
3. **Change Feed** - Must be enabled
4. **Block Blobs Only** - Only works with block blobs (not append or page blobs)

### Limitations

- Only available for **block blobs** (not append blobs or page blobs)
- Only works with **general-purpose v2** or **premium block blob** storage accounts
- Cannot restore blobs in archive tier
- Cannot restore blob index tags
- Maximum retention period: 365 days
- Hierarchical namespace (HNS) accounts are not supported

### How to Enable

**Azure Portal:**
1. Navigate to your storage account
2. Go to **Data protection** under **Data management**
3. Enable **Turn on point-in-time restore for containers**
4. Set the retention period (1-365 days)

**Azure CLI:**
```bash
az storage account blob-service-properties update \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --enable-restore-policy true \
    --restore-days 7 \
    --enable-versioning true \
    --enable-delete-retention true \
    --delete-retention-days 14 \
    --enable-change-feed true
```

**PowerShell:**
```powershell
Enable-AzStorageBlobRestorePolicy `
    -ResourceGroupName <resource-group-name> `
    -StorageAccountName <storage-account-name> `
    -RestoreDays 7
```

### Performing a Restore

**Azure Portal:**
1. Navigate to your storage account
2. Go to **Data protection**
3. Click **Restore containers**
4. Select the restore point (date and time)
5. Choose containers or blob ranges to restore
6. Click **Restore**

**Azure CLI:**
```bash
# Restore all containers to a specific point in time
az storage blob restore \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --time-to-restore "2025-01-15T12:00:00Z"

# Restore specific container ranges
az storage blob restore \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --time-to-restore "2025-01-15T12:00:00Z" \
    --blob-range "[{start-range: 'container1/', end-range: 'container1-0'}]"
```

## Soft Delete

### Soft Delete for Blobs

Blob soft delete protects individual blobs by retaining deleted blobs for a specified retention period.

**Key Characteristics:**
- Retains deleted blobs and their versions
- Configurable retention period (1-365 days)
- Deleted blobs can be restored within retention period
- Works with all blob types (block, append, page)

**Restoring Soft-Deleted Blobs:**

To restore a soft-deleted blob within the retention period, use the **Undelete Blob** operation:

```bash
# Azure CLI - List soft-deleted blobs
az storage blob list \
    --account-name <storage-account-name> \
    --container-name <container-name> \
    --include d

# Azure CLI - Undelete a blob
az storage blob undelete \
    --account-name <storage-account-name> \
    --container-name <container-name> \
    --name <blob-name>
```

```csharp
// .NET SDK - Undelete a blob
BlobClient blobClient = containerClient.GetBlobClient("myblob.txt");
await blobClient.UndeleteAsync();
```

> ⚠️ **Important Restrictions on Soft-Deleted Blobs:**
> - Soft-deleted blobs **cannot be used as a source** for copy operations
> - They must be **explicitly undeleted** before they can be copied or accessed
> - Creating a new blob with the same name does **not** restore the soft-deleted version
> - Lifecycle management policies **cannot** restore soft-deleted blobs

**Enable via Azure CLI:**
```bash
az storage account blob-service-properties update \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --enable-delete-retention true \
    --delete-retention-days 14
```

### Soft Delete for Containers

Container soft delete protects against accidental container deletion.

**Key Characteristics:**
- Retains deleted containers and their contents
- Configurable retention period (1-365 days)
- Deleted containers can be restored with original name (if available)
- Container name is released after a brief period

> ⚠️ **Important**: Soft delete for containers protects the **container itself**, while point-in-time restore allows you to restore the **data within containers** to a previous state.

**Enable via Azure CLI:**
```bash
az storage account blob-service-properties update \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --enable-container-delete-retention true \
    --container-delete-retention-days 14
```

## Blob Versioning

Blob versioning automatically maintains previous versions of a blob when it's modified or deleted.

**Key Characteristics:**
- Automatic version creation on modification
- Each version has a unique version ID
- Versions can be restored to become the current version
- Required for point-in-time restore

**Enable via Azure CLI:**
```bash
az storage account blob-service-properties update \
    --account-name <storage-account-name> \
    --resource-group <resource-group-name> \
    --enable-versioning true
```

## Azure Backup for Blobs

Azure Backup provides operational backup for blob data, offering a more comprehensive backup solution.

**Key Characteristics:**
- Continuous backup with no scheduled backup jobs
- Restore to any point in time within retention period
- Managed through Azure Backup Center
- Supports cross-region restore (with GRS accounts)
- Different from storage account's built-in features

## Immutable Storage for Blob Data

Immutable storage enables you to store business-critical data in a WORM (Write Once, Read Many) state. When configured, data cannot be modified or deleted for a specified interval. Azure Blob Storage supports two types of immutability policies:

### Time-Based Retention Policy

A time-based retention policy stores blob data in a WORM state for a **specified interval**. When set, objects can be created and read, but not modified or deleted until the retention period expires.

**Key Characteristics:**
- Requires specifying a **retention duration upfront**
- Can be **locked** or **unlocked**
- **Unlocked policy**: Can be removed or modified, but still requires specifying a retention duration
- **Locked policy**: Cannot be removed; retention period can only be extended, never shortened
- After retention expires, objects can be deleted but **not overwritten (modified)**

**Operations Allowed Based on Retention Status:**

| Operation | During Retention Period | After Retention Expires |
|-----------|------------------------|------------------------|
| **Create** | ✅ Allowed | ✅ Allowed |
| **Read** | ✅ Allowed | ✅ Allowed |
| **Modify (Overwrite)** | ❌ Not Allowed | ❌ Not Allowed |
| **Delete** | ❌ Not Allowed | ✅ Allowed |

> ⚠️ **Important**: Even after the retention period expires, blobs **cannot be overwritten or modified**. Only deletion becomes allowed. This is a key exam concept!

**Types:**

| Policy State | Can Modify Retention? | Can Delete Policy? | Use Case |
|--------------|----------------------|-------------------|----------|
| **Unlocked** | Yes | Yes | Testing, adjusting retention before committing |
| **Locked** | Extend only | No | Compliance requirements with known duration |

### Legal Hold

A **legal hold** stores immutable data **until the legal hold is explicitly cleared**. Unlike time-based retention policies, legal holds do not require specifying a retention duration.

**Key Characteristics:**
- **No retention duration required** - ideal when duration is unknown
- Objects can be created and read, but not modified or deleted
- Must be **explicitly cleared** to allow modifications/deletions
- Multiple legal holds can be applied with different tags
- Perfect for legal proceedings where retention duration is uncertain

**When to Use Legal Hold:**
- Legal proceedings with unknown duration
- Regulatory investigations
- Any scenario where data must be preserved indefinitely until an external event concludes

### Immutability Policy Comparison

| Feature | Time-Based Retention (Unlocked) | Time-Based Retention (Locked) | Legal Hold |
|---------|--------------------------------|------------------------------|------------|
| **Duration Required** | Yes | Yes | No |
| **Can Remove Policy** | Yes | No | Yes (by clearing hold) |
| **Can Modify Duration** | Yes | Extend only | N/A |
| **Best For** | Testing, adjustable compliance | Strict compliance with known duration | Unknown duration, legal proceedings |

## Blob Index Tags

Blob index tags provide a way to categorize and search for blobs using custom key-value pairs. Unlike other blob attributes, index tags are **automatically indexed** by Azure Storage and are **queryable across the entire storage account**.

**Key Characteristics:**
- Support up to 10 key-value tag pairs per blob
- Keys can be 1-128 characters; values can be 0-256 characters
- Tags are **automatically indexed** for efficient searching
- Support **account-wide queries** using the Find Blobs by Tags operation
- Can be set during blob upload or added/modified later
- Available for block blobs, append blobs, and page blobs

**Setting Blob Index Tags:**

```bash
# Azure CLI - Set tags during upload
az storage blob upload \
    --account-name <storage-account-name> \
    --container-name <container-name> \
    --name <blob-name> \
    --file <local-file> \
    --tags "project=marketing" "status=active" "year=2025"

# Azure CLI - Set tags on existing blob
az storage blob tag set \
    --account-name <storage-account-name> \
    --container-name <container-name> \
    --name <blob-name> \
    --tags "project=marketing" "status=complete"
```

**Querying Blobs by Tags:**

```bash
# Azure CLI - Find blobs across entire storage account
az storage blob filter \
    --account-name <storage-account-name> \
    --tag-filter "project = 'marketing' AND status = 'active'"
```

```csharp
// .NET SDK - Find blobs by tags
BlobServiceClient serviceClient = new BlobServiceClient(connectionString);
string query = "@container = 'mycontainer' AND status = 'active'";
await foreach (TaggedBlobItem blobItem in serviceClient.FindBlobsByTagsAsync(query))
{
    Console.WriteLine($"Blob: {blobItem.BlobName}");
}
```

### Blob Index Tags vs Other Blob Attributes

| Attribute | Automatically Indexed | Queryable Across Account | Custom Key-Value Pairs | Use Case |
|-----------|----------------------|-------------------------|----------------------|----------|
| **Blob Index Tags** | ✅ Yes | ✅ Yes | ✅ Yes | Searchable custom metadata, data categorization |
| **Blob Metadata** | ❌ No | ❌ No | ✅ Yes | Custom data stored with blob (requires listing/downloading to access) |
| **Blob Properties** | ❌ No | ❌ No | ❌ No (system-defined) | System attributes like Content-Type, Last-Modified |
| **Container Metadata** | ❌ No | ❌ No | ✅ Yes | Container-level custom data (not blob-level) |

> 💡 **Exam Tip**: When you need to implement **searchable custom key-value pairs across a storage account**, use **Blob Index Tags**. They are the only attribute type that is automatically indexed and supports account-wide queries.

## Feature Comparison

| Feature | Restores What? | Scope | Requires Other Features |
|---------|---------------|-------|------------------------|
| **Point-in-Time Restore** | Container data to earlier state | One or more containers | Versioning, Soft Delete, Change Feed |
| **Soft Delete (Blobs)** | Deleted individual blobs | Individual blobs | None |
| **Soft Delete (Containers)** | Deleted containers | Entire container | None |
| **Blob Versioning** | Previous blob versions | Individual blob versions | None |
| **Azure Backup** | Blob data to any point | Storage account | Backup vault |

## Exam Question Analysis

### Question: Restoring Containers to an Earlier State

**Question:**
Which feature of Azure Storage Account allows you to restore one or more containers to an earlier state?

**Options:**
- A) Azure Backup
- B) Soft delete
- C) Soft delete for containers
- D) Point-in-time restore ✅

**Correct Answer: D) Point-in-time restore**

**Explanation:**
Point-in-time restore protects against accidental deletion or corruption by enabling you to restore block blob data to an earlier state. Point-in-time restore is useful when:
- A user or application accidentally deletes data
- An application error corrupts data
- Testing scenarios require reverting a data set to a known state before running further tests

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Azure Backup** | Provides operational backup but is a separate Azure service, not a storage account feature for point-in-time container restore |
| **Soft delete** | Recovers deleted blobs, but doesn't restore containers to a previous state |
| **Soft delete for containers** | Recovers deleted containers, but doesn't restore container data to a previous point in time |

**Key Distinction:**
- **Point-in-time restore**: Restores data **to a previous state** (time-based restoration)
- **Soft delete**: Recovers **deleted items** (deletion recovery)

---

### Question: Restoring a Soft-Deleted Blob

**Question:**
You have a blob container with soft delete enabled for a 30-day retention period. A blob was deleted 20 days ago and you need to restore it. Which method should you use?

**Options:**
- A) Call the Undelete Blob operation on the soft-deleted blob using its name ✅
- B) Copy the soft-deleted blob to a new blob using the Copy Blob operation
- C) Use lifecycle management policy to automatically restore soft-deleted blobs
- D) Create a new blob with the same name to automatically restore the soft-deleted version

**Correct Answer: A) Call the Undelete Blob operation on the soft-deleted blob using its name**

**Explanation:**
The **Undelete Blob** operation is specifically designed to restore soft-deleted blobs within the retention period. Since the blob was deleted 20 days ago and the retention is 30 days, it can be successfully restored using this operation.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Copy Blob operation** | Soft-deleted blobs **cannot be used as a source** for copy operations. They must first be undeleted before they can be copied |
| **Lifecycle management policy** | Lifecycle management policies **cannot restore** soft-deleted blobs. They can only transition, delete, or manage blobs based on conditions, not perform restore operations |
| **Create new blob with same name** | Creating a new blob with the same name **doesn't restore** the soft-deleted blob; it creates an entirely new blob. The soft-deleted version remains separate and must be explicitly undeleted |

**Key Takeaway:**
Soft-deleted blobs exist in a special state where they:
- Can be listed (with include deleted flag)
- Can be undeleted using the Undelete Blob operation
- **Cannot** be read, copied, or used until explicitly undeleted

---

### Question: Immutability Policy for Unknown Retention Duration

**Question:**
A company is implementing Azure Storage immutability for compliance requirements. They need a solution where data retention duration is unknown and can be removed when legal proceedings conclude. Which immutability policy type should they use?

**Options:**
- A) Unlocked time-based retention policy
- B) Legal hold ✅
- C) Time-based retention policy with automatic extension
- D) Time-based retention policy with 1 year duration

**Correct Answer: B) Legal hold**

**Explanation:**
A **legal hold** stores immutable data until the legal hold is explicitly cleared. When a legal hold is set, objects can be created and read, but not modified or deleted. This is ideal when retention duration is unknown, such as during legal proceedings that may conclude at an unpredictable time.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Unlocked time-based retention policy** | While unlocked policies can be removed, they still require specifying a retention duration upfront, which doesn't meet the requirement of unknown duration |
| **Time-based retention policy with automatic extension** | Time-based retention policies require a specified duration and don't support indefinite retention based on external events like legal proceedings |
| **Time-based retention policy with 1 year duration** | After the retention period has expired, objects can be deleted but not overwritten. A fixed duration doesn't suit scenarios where the retention period is unknown |

**Key Distinction:**
- **Time-based retention**: Requires a **known duration** specified upfront
- **Legal hold**: **No duration required** - retention continues until explicitly cleared

**Domain:** Implement Azure security

---

### Question: Operations Allowed After Time-Based Retention Expires

**Question:**
A storage account has a container with a locked time-based retention policy set for 90 days. After 100 days, what operations are allowed on the blobs in this container?

**Options:**
- A) Read and modify only
- B) Read only
- C) Create, read, modify, and delete
- D) Delete only ✅

**Correct Answer: D) Delete only**

**Explanation:**
When a time-based retention policy is set, objects can be created and read, but not modified or deleted during the retention period. After the retention period has expired (100 days > 90 days), objects can be **deleted but not overwritten**. 

The question asks what operations are allowed - and the key insight is that **create and read were always allowed** (both during and after retention). The only operation that **changes** after the retention period expires is **delete** - it becomes allowed. Modify/overwrite is **never** allowed, even after retention expires.

> 💡 **Key Concept**: Time-based retention policies enforce WORM (Write Once, Read Many) semantics. The "Write Once" restriction (no modifications/overwrites) is **permanent** and never lifted, even after retention expires. Only the deletion restriction is lifted after the retention period.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Read and modify only** | Modification (overwriting) is **never allowed** even after the retention period expires. The WORM policy permanently prevents overwrites |
| **Read only** | After the retention period expires, both read and **delete** operations are allowed, not just read operations. Also, create is always allowed |
| **Create, read, modify, and delete** | Modify operations are **never allowed** on existing blobs under time-based retention, even after retention expires |

**Complete Operations Summary:**

| Operation | During Retention Period | After Retention Expires | Notes |
|-----------|------------------------|------------------------|-------|
| **Create new blobs** | ✅ Allowed | ✅ Allowed | Always allowed - new blobs can be added anytime |
| **Read existing blobs** | ✅ Allowed | ✅ Allowed | Always allowed - this is the "Read Many" in WORM |
| **Modify/Overwrite existing blobs** | ❌ Not Allowed | ❌ Not Allowed | **Never allowed** - this is the "Write Once" in WORM |
| **Delete existing blobs** | ❌ Not Allowed | ✅ Allowed | Only operation that changes after expiry |

> ⚠️ **Exam Tip**: The question asks what is "allowed" after 100 days. While create, read, AND delete are all allowed after expiry, the answer is "delete only" because that's the **only operation that wasn't previously allowed** and becomes available after the retention period expires.

**Domain:** Implement Azure security

---

### Question: Implementing Searchable Custom Key-Value Pairs for Blobs

**Question:**
You need to implement a solution that automatically indexes blob data for searching based on custom key-value pairs. The solution must support queries across the entire storage account. What should you configure?

**Options:**
- A) Blob properties
- B) Blob metadata
- C) Container metadata
- D) Blob index tags ✅

**Correct Answer: D) Blob index tags**

**Explanation:**
Blob index tags are automatically indexed and support querying across the entire storage account using key-value pairs, making them ideal for implementing searchable custom metadata.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Blob properties** | Blob properties contain system-defined attributes that are not customizable and cannot be used for custom key-value indexing |
| **Blob metadata** | Blob metadata is not automatically indexed and cannot be queried directly; it requires downloading or listing blobs to access the metadata values |
| **Container metadata** | Container metadata is stored at the container level and is not automatically indexed or searchable across the storage account |

**Key Distinction:**
- **Blob Index Tags**: Automatically indexed, queryable across account, custom key-value pairs ✅
- **Blob Metadata**: Custom key-value pairs but NOT indexed or directly queryable
- **Blob Properties**: System-defined only, not customizable
- **Container Metadata**: Container-level only, not indexed

**Domain:** Develop for Azure storage

## Best Practices

1. **Enable All Protection Features**: For maximum protection, enable versioning, soft delete, and point-in-time restore together

2. **Set Appropriate Retention Periods**: 
   - Consider compliance requirements
   - Balance storage costs with recovery needs
   - Point-in-time restore retention should be ≤ soft delete retention

3. **Test Restore Procedures**: Regularly test your restore procedures to ensure they work as expected

4. **Monitor Costs**: Data protection features increase storage usage; monitor and manage costs

5. **Understand Feature Dependencies**:
   ```
   Point-in-Time Restore
   └── Requires: Blob Versioning
   └── Requires: Soft Delete for Blobs
   └── Requires: Change Feed
   ```

6. **Choose the Right Feature**:
   - Accidental deletion → Soft delete
   - Data corruption → Point-in-time restore
   - Compliance/audit → Blob versioning
   - Enterprise backup → Azure Backup

## References

- [Point-in-time restore for block blobs](https://docs.microsoft.com/en-us/azure/storage/blobs/point-in-time-restore-overview)
- [Soft delete for blobs](https://docs.microsoft.com/en-us/azure/storage/blobs/soft-delete-blob-overview)
- [Soft delete for containers](https://docs.microsoft.com/en-us/azure/storage/blobs/soft-delete-container-overview)
- [Blob versioning](https://docs.microsoft.com/en-us/azure/storage/blobs/versioning-overview)
- [Azure Backup for blobs](https://docs.microsoft.com/en-us/azure/backup/blob-backup-overview)
