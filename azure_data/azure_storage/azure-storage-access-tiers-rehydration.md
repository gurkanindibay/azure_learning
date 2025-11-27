# Azure Blob Storage Access Tiers

## Table of Contents

- [Overview](#overview)
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

### Scenario: 100 GB/day with 30-day retention and rare access

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
