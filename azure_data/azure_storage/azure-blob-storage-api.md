
# Azure Blob Storage API

## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Blob Client Types](#blob-client-types)
  - [Blob Types](#blob-types)
- [Working with Blob Metadata](#working-with-blob-metadata)
  - [What is Blob Metadata?](#what-is-blob-metadata)
  - [Setting Metadata on a Blob](#setting-metadata-on-a-blob)
    - [Method 1: SetMetadataAsync with Dictionary ✅ (Correct)](#method-1-setmetadataasync-with-dictionary--correct)
    - [Method 2: Setting Metadata During Upload](#method-2-setting-metadata-during-upload)
    - [Common Mistakes When Setting Metadata](#common-mistakes-when-setting-metadata)
  - [Reading Metadata from a Blob](#reading-metadata-from-a-blob)
  - [Metadata Naming Rules](#metadata-naming-rules)
- [Working with Blob Properties](#working-with-blob-properties)
  - [What are Blob Properties?](#what-are-blob-properties)
  - [System Properties vs Custom Metadata](#system-properties-vs-custom-metadata)
  - [Setting Blob Properties](#setting-blob-properties)
  - [Reading Blob Properties](#reading-blob-properties)
- [Complete Code Examples](#complete-code-examples)
  - [C# Examples](#c-examples)
  - [Python Examples](#python-examples)
  - [Azure CLI Examples](#azure-cli-examples)
- [Working with Blob Leases](#working-with-blob-leases)
  - [What is a Blob Lease?](#what-is-a-blob-lease)
  - [Lease Duration Rules](#lease-duration-rules)
  - [Acquiring a Blob Lease](#acquiring-a-blob-lease)
  - [Lease Operations](#lease-operations)
- [Exam Question Analysis](#exam-question-analysis)
  - [Question: Uploading Files to Azure Blob Storage](#question-uploading-files-to-azure-blob-storage)
  - [Question: Uploading a File to Azure Blob Storage (SDK Methods)](#question-uploading-a-file-to-azure-blob-storage-sdk-methods)
  - [Question: Setting Custom Metadata on a Blob](#question-setting-custom-metadata-on-a-blob)
  - [Question: Implementing Retry Logic for Large File Uploads](#question-implementing-retry-logic-for-large-file-uploads)
  - [Question: Implementing Blob Lease for Exclusive Write Access](#question-implementing-blob-lease-for-exclusive-write-access)
  - [Question: Storing Custom Application-Specific Data with Blobs](#question-storing-custom-application-specific-data-with-blobs)
  - [Question: HTTPS with Custom Domain for Static Website](#question-https-with-custom-domain-for-static-website)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Blob Storage provides a RESTful API and client SDKs for managing binary large objects (blobs). This document covers the key API operations for working with blob metadata, properties, and common operations using the Azure SDK for .NET, Python, and Azure CLI.

## Key Concepts

### Blob Client Types

| Client | Description | Use Case |
|--------|-------------|----------|
| `BlobServiceClient` | Service-level operations | List containers, get/set service properties |
| `BlobContainerClient` | Container-level operations | Create/delete containers, list blobs, set access policies |
| `BlobClient` | Blob-level operations | Upload, download, set metadata/properties |
| `BlockBlobClient` | Block blob specific operations | Stage blocks, commit block lists |
| `AppendBlobClient` | Append blob specific operations | Append blocks |
| `PageBlobClient` | Page blob specific operations | Write pages, resize |

### Blob Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Block Blob** | Store text and binary data | Images, documents, videos |
| **Append Blob** | Optimized for append operations | Log files, streaming data |
| **Page Blob** | Random read/write operations | VHD files, database files |

## Working with Blob Metadata

### What is Blob Metadata?

Blob metadata consists of user-defined **name-value pairs** that you can associate with a blob. Metadata allows you to store additional information about the blob without modifying its content.

**Key Characteristics:**
- Name-value pairs (key-value)
- Names are case-insensitive
- Both names and values must be strings
- Maximum size: 8 KB total for all metadata
- Does not affect blob content

**Common Use Cases:**
- Track image resolution and color profile
- Store document categorization
- Record processing status
- Maintain audit information
- Tag content for search/filtering

### Setting Metadata on a Blob

#### Method 1: SetMetadataAsync with Dictionary ✅ (Correct)

The **correct** way to set custom metadata on an existing blob is using the `SetMetadataAsync` method with a `Dictionary<string, string>`:

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

// Get blob client
BlobClient blobClient = new BlobClient(connectionString, "images", "photo.jpg");

// ✅ CORRECT: Set custom metadata using SetMetadataAsync
await blobClient.SetMetadataAsync(new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
});
```

**Why This Is Correct:**
- ✅ Uses `SetMetadataAsync` - the dedicated method for setting metadata
- ✅ Provides key-value pairs in a dictionary
- ✅ Directly associates metadata with the blob
- ✅ Does not require re-uploading the blob content

#### Method 2: Setting Metadata During Upload

You can also set metadata when uploading a new blob using `BlobUploadOptions`:

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

BlobClient blobClient = new BlobClient(connectionString, "images", "photo.jpg");

// Set metadata during upload
var uploadOptions = new BlobUploadOptions
{
    Metadata = new Dictionary<string, string>
    {
        { "Resolution", "1920x1080" },
        { "ColorProfile", "sRGB" }
    },
    HttpHeaders = new BlobHttpHeaders
    {
        ContentType = "image/jpeg"
    }
};

await using var fileStream = File.OpenRead("photo.jpg");
await blobClient.UploadAsync(fileStream, uploadOptions);
```

### Common Mistakes When Setting Metadata

#### ❌ Mistake 1: Using SetPropertiesAsync Instead of SetMetadataAsync

```csharp
// ❌ WRONG: SetPropertiesAsync sets HTTP headers, NOT custom metadata
await blobClient.SetHttpHeadersAsync(new BlobHttpHeaders
{
    ContentType = "image/jpeg"
});
```

**Why This Is Wrong:**
- `SetHttpHeadersAsync` (formerly `SetPropertiesAsync`) sets **system properties** like `ContentType`, `ContentEncoding`, etc.
- It does **NOT** set custom metadata
- System properties and custom metadata are different concepts

#### ❌ Mistake 2: Setting Metadata Properties Without Calling SetMetadataAsync

```csharp
// ❌ WRONG: This approach doesn't persist metadata to storage
await blobClient.UploadAsync(fileStream);
blobClient.Metadata["Resolution"] = "1920x1080";
blobClient.Metadata["ColorProfile"] = "sRGB";
await blobClient.SetMetadataAsync(); // This may not work as expected
```

**Why This Is Wrong:**
- Modifying the local `Metadata` collection doesn't automatically sync to Azure
- The `blobClient.Metadata` property may be null or not reflect current state
- Correct approach: Pass metadata dictionary directly to `SetMetadataAsync`

#### ❌ Mistake 3: Incorrect UploadAsync Overload

```csharp
// ❌ WRONG: This overload doesn't exist with these parameters
var metadata = new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
};
await blobClient.UploadAsync(fileStream, new BlobHttpHeaders(), metadata);
```

**Why This Is Wrong:**
- The `UploadAsync` method doesn't have an overload that takes `BlobHttpHeaders` and metadata separately
- Use `BlobUploadOptions` to set both headers and metadata during upload

#### ✅ Correct Alternatives

**Alternative 1: SetMetadataAsync after upload (Two-step approach)**
```csharp
// Step 1: Upload the blob
await blobClient.UploadAsync(fileStream);

// Step 2: Set metadata separately
await blobClient.SetMetadataAsync(new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
});
```

**Alternative 2: BlobUploadOptions during upload (Single-step approach)**
```csharp
// Upload with metadata in one step
await blobClient.UploadAsync(fileStream, new BlobUploadOptions
{
    Metadata = new Dictionary<string, string>
    {
        { "Resolution", "1920x1080" },
        { "ColorProfile", "sRGB" }
    }
});
```

### Reading Metadata from a Blob

```csharp
// Get blob properties (includes metadata)
BlobProperties properties = await blobClient.GetPropertiesAsync();

// Read metadata
foreach (var metadata in properties.Metadata)
{
    Console.WriteLine($"{metadata.Key}: {metadata.Value}");
}

// Access specific metadata values
if (properties.Metadata.TryGetValue("Resolution", out string resolution))
{
    Console.WriteLine($"Resolution: {resolution}");
}
```

### Metadata Naming Rules

| Rule | Valid | Invalid |
|------|-------|---------|
| Must be valid C# identifiers | `Resolution`, `ColorProfile` | `1stValue`, `color-profile` |
| Case-insensitive | `resolution` = `Resolution` | - |
| No special characters | `ImageWidth` | `Image.Width`, `Image/Width` |
| Cannot start with numbers | `Photo1` | `1Photo` |

## Working with Blob Properties

### What are Blob Properties?

Blob properties are **system-defined** attributes that describe the blob. Unlike metadata, properties are set by Azure or through specific API methods.

### System Properties vs Custom Metadata

| Aspect | System Properties | Custom Metadata |
|--------|-------------------|-----------------|
| **Definition** | Predefined by Azure | User-defined |
| **Purpose** | HTTP headers, blob characteristics | Custom tracking information |
| **Set Method** | `SetHttpHeadersAsync` | `SetMetadataAsync` |
| **Examples** | ContentType, ContentEncoding, CacheControl | Resolution, ColorProfile, Author |
| **Read-Only Properties** | ETag, LastModified, BlobType | None (all user-defined) |

### Setting Blob Properties

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

BlobClient blobClient = new BlobClient(connectionString, "documents", "report.pdf");

// Set system properties (HTTP headers)
await blobClient.SetHttpHeadersAsync(new BlobHttpHeaders
{
    ContentType = "application/pdf",
    ContentDisposition = "attachment; filename=report.pdf",
    ContentEncoding = "gzip",
    ContentLanguage = "en-US",
    CacheControl = "max-age=3600"
});
```

**Common System Properties:**

| Property | Description | Example |
|----------|-------------|---------|
| `ContentType` | MIME type of the blob | `image/jpeg`, `application/pdf` |
| `ContentEncoding` | Encoding for content | `gzip`, `deflate` |
| `ContentLanguage` | Language of content | `en-US`, `fr-FR` |
| `ContentDisposition` | How to handle blob | `attachment; filename=file.pdf` |
| `CacheControl` | Caching directives | `max-age=3600` |
| `ContentMD5` | MD5 hash of content | Base64-encoded hash |

### Reading Blob Properties

```csharp
// Get all properties
BlobProperties properties = await blobClient.GetPropertiesAsync();

// Read system properties
Console.WriteLine($"Content Type: {properties.ContentType}");
Console.WriteLine($"Content Length: {properties.ContentLength}");
Console.WriteLine($"Last Modified: {properties.LastModified}");
Console.WriteLine($"ETag: {properties.ETag}");
Console.WriteLine($"Blob Type: {properties.BlobType}");
Console.WriteLine($"Access Tier: {properties.AccessTier}");
Console.WriteLine($"Created On: {properties.CreatedOn}");

// Check if blob is encrypted
Console.WriteLine($"Encrypted: {properties.IsServerEncrypted}");
```

## Complete Code Examples

### C# Examples

#### Complete Metadata and Properties Management

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

public class BlobMetadataManager
{
    private readonly BlobContainerClient _containerClient;

    public BlobMetadataManager(string connectionString, string containerName)
    {
        var blobServiceClient = new BlobServiceClient(connectionString);
        _containerClient = blobServiceClient.GetBlobContainerClient(containerName);
    }

    // Upload blob with metadata and properties
    public async Task UploadWithMetadataAsync(
        string blobName, 
        Stream content,
        string contentType,
        Dictionary<string, string> metadata)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);

        var uploadOptions = new BlobUploadOptions
        {
            HttpHeaders = new BlobHttpHeaders
            {
                ContentType = contentType
            },
            Metadata = metadata
        };

        await blobClient.UploadAsync(content, uploadOptions);
    }

    // Set metadata on existing blob
    public async Task SetMetadataAsync(
        string blobName, 
        Dictionary<string, string> metadata)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        await blobClient.SetMetadataAsync(metadata);
    }

    // Update single metadata value (preserves existing)
    public async Task UpdateMetadataValueAsync(
        string blobName, 
        string key, 
        string value)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        
        // Get existing metadata
        var properties = await blobClient.GetPropertiesAsync();
        var metadata = new Dictionary<string, string>(properties.Value.Metadata);
        
        // Update or add the key
        metadata[key] = value;
        
        // Set updated metadata
        await blobClient.SetMetadataAsync(metadata);
    }

    // Get metadata from blob
    public async Task<IDictionary<string, string>> GetMetadataAsync(string blobName)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        var properties = await blobClient.GetPropertiesAsync();
        return properties.Value.Metadata;
    }

    // Set HTTP headers (system properties)
    public async Task SetPropertiesAsync(
        string blobName,
        string contentType = null,
        string cacheControl = null,
        string contentDisposition = null)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);

        var headers = new BlobHttpHeaders
        {
            ContentType = contentType,
            CacheControl = cacheControl,
            ContentDisposition = contentDisposition
        };

        await blobClient.SetHttpHeadersAsync(headers);
    }

    // Get all properties
    public async Task<BlobProperties> GetPropertiesAsync(string blobName)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        return await blobClient.GetPropertiesAsync();
    }
}

// Usage example
public class Program
{
    public static async Task Main()
    {
        var manager = new BlobMetadataManager(
            "your-connection-string",
            "images"
        );

        // Upload image with metadata
        await using var fileStream = File.OpenRead("photo.jpg");
        await manager.UploadWithMetadataAsync(
            "photos/photo.jpg",
            fileStream,
            "image/jpeg",
            new Dictionary<string, string>
            {
                { "Resolution", "1920x1080" },
                { "ColorProfile", "sRGB" },
                { "Camera", "Canon EOS R5" }
            }
        );

        // Update metadata on existing blob
        await manager.SetMetadataAsync(
            "photos/photo.jpg",
            new Dictionary<string, string>
            {
                { "Resolution", "3840x2160" },
                { "ColorProfile", "Adobe RGB" },
                { "Processed", "true" }
            }
        );

        // Read metadata
        var metadata = await manager.GetMetadataAsync("photos/photo.jpg");
        foreach (var kvp in metadata)
        {
            Console.WriteLine($"{kvp.Key}: {kvp.Value}");
        }
    }
}
```

### Python Examples

```python
from azure.storage.blob import BlobServiceClient, ContentSettings
import os

# Initialize blob service client
connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client("images")

# Upload blob with metadata
def upload_with_metadata(blob_name: str, file_path: str, metadata: dict):
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, "rb") as data:
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type="image/jpeg"),
            metadata=metadata
        )

# Set metadata on existing blob
def set_metadata(blob_name: str, metadata: dict):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.set_blob_metadata(metadata)

# Get metadata from blob
def get_metadata(blob_name: str) -> dict:
    blob_client = container_client.get_blob_client(blob_name)
    properties = blob_client.get_blob_properties()
    return properties.metadata

# Set HTTP headers (system properties)
def set_content_settings(blob_name: str, content_type: str):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.set_http_headers(
        content_settings=ContentSettings(content_type=content_type)
    )

# Usage
upload_with_metadata(
    "photos/photo.jpg",
    "local_photo.jpg",
    {
        "Resolution": "1920x1080",
        "ColorProfile": "sRGB"
    }
)

# Update metadata
set_metadata(
    "photos/photo.jpg",
    {
        "Resolution": "3840x2160",
        "ColorProfile": "Adobe RGB",
        "Processed": "true"
    }
)

# Read metadata
metadata = get_metadata("photos/photo.jpg")
for key, value in metadata.items():
    print(f"{key}: {value}")
```

### Azure CLI Examples

```bash
# Set metadata on a blob
az storage blob metadata update \
    --container-name images \
    --name photos/photo.jpg \
    --metadata Resolution=1920x1080 ColorProfile=sRGB \
    --account-name mystorageaccount

# Get metadata from a blob
az storage blob metadata show \
    --container-name images \
    --name photos/photo.jpg \
    --account-name mystorageaccount

# Set HTTP headers (content-type, cache-control, etc.)
az storage blob update \
    --container-name images \
    --name photos/photo.jpg \
    --content-type "image/jpeg" \
    --content-cache-control "max-age=3600" \
    --account-name mystorageaccount

# Get blob properties (includes metadata)
az storage blob show \
    --container-name images \
    --name photos/photo.jpg \
    --account-name mystorageaccount \
    --query '{name:name, contentType:properties.contentSettings.contentType, metadata:metadata}'

# Upload blob with metadata
az storage blob upload \
    --container-name images \
    --name photos/photo.jpg \
    --file photo.jpg \
    --content-type "image/jpeg" \
    --metadata Resolution=1920x1080 ColorProfile=sRGB \
    --account-name mystorageaccount
```

## Working with Blob Leases

### What is a Blob Lease?

A **blob lease** establishes a lock on a blob for exclusive write and delete access. Leases are useful in distributed applications where multiple processes might try to modify the same blob simultaneously.

**Key Characteristics:**
- Provides exclusive write/delete access to a blob
- Can be acquired, renewed, released, or broken
- Prevents other clients from modifying or deleting the blob while leased
- Essential for implementing pessimistic concurrency control

**Use Cases:**
- Distributed file processing where only one process should write at a time
- Preventing race conditions in multi-instance applications
- Implementing distributed locks across Azure services
- Coordinating access in leader election scenarios

### Lease Duration Rules

| Duration Type | Range | Behavior |
|---------------|-------|----------|
| **Finite Lease** | 15-60 seconds | Automatically expires after the specified duration |
| **Infinite Lease** | -1 (TimeSpan value) | Never expires, must be explicitly released or broken |

**Important:**
- Finite leases must be between **15 and 60 seconds**
- Values outside this range will throw an exception
- Infinite leases require explicit `ReleaseAsync()` or `BreakAsync()` to release

### Acquiring a Blob Lease

To acquire a lease on a blob, you must:
1. Create a `BlobLeaseClient` from the `BlobClient` using `GetBlobLeaseClient()`
2. Call `AcquireAsync()` on the lease client with the desired duration

**✅ Correct Way to Acquire a Lease:**

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Specialized;
using Azure.Storage.Blobs.Models;

// Get the blob client
BlobClient blobClient = new BlobClient(connectionString, "my-container", "myfile.txt");

// Create a lease client from the blob client
BlobLeaseClient leaseClient = blobClient.GetBlobLeaseClient();

// Acquire a 45-second lease (valid range: 15-60 seconds for finite leases)
Response<BlobLease> lease = await leaseClient.AcquireAsync(TimeSpan.FromSeconds(45));

Console.WriteLine($"Lease ID: {lease.Value.LeaseId}");
Console.WriteLine($"Lease Time: {lease.Value.LeaseTime}");
```

**❌ Common Mistakes:**

```csharp
// ❌ WRONG: BlobClient doesn't have AcquireLeaseAsync method
Response<BlobLease> lease = await blobClient.AcquireLeaseAsync(TimeSpan.FromSeconds(45));

// ❌ WRONG: BlobLeaseClient constructor doesn't accept TimeSpan
BlobLeaseClient leaseClient = new BlobLeaseClient(blobClient, TimeSpan.FromSeconds(45));
Response<BlobLease> lease = await leaseClient.AcquireAsync();

// ❌ WRONG: Unnecessary conditions on lease acquisition
BlobLeaseClient leaseClient = blobClient.GetBlobLeaseClient();
Response<BlobLease> lease = await leaseClient.AcquireAsync(
    TimeSpan.FromSeconds(45), 
    conditions: new BlobLeaseRequestConditions { IfMatch = new ETag("*") }
);
```

### Lease Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| **Acquire** | `AcquireAsync(TimeSpan)` | Obtain a new lease on the blob |
| **Renew** | `RenewAsync()` | Extend the lease before it expires |
| **Change** | `ChangeAsync(proposedId)` | Change the lease ID |
| **Release** | `ReleaseAsync()` | Explicitly release the lease |
| **Break** | `BreakAsync()` | Break a lease, allowing others to acquire |

**Complete Example with All Operations:**

```csharp
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Specialized;
using Azure.Storage.Blobs.Models;

public class BlobLeaseManager
{
    private readonly BlobClient _blobClient;
    private BlobLeaseClient _leaseClient;
    private string _leaseId;

    public BlobLeaseManager(string connectionString, string containerName, string blobName)
    {
        _blobClient = new BlobClient(connectionString, containerName, blobName);
        _leaseClient = _blobClient.GetBlobLeaseClient();
    }

    // Acquire a finite lease (15-60 seconds)
    public async Task<string> AcquireLeaseAsync(int durationSeconds = 30)
    {
        var lease = await _leaseClient.AcquireAsync(TimeSpan.FromSeconds(durationSeconds));
        _leaseId = lease.Value.LeaseId;
        return _leaseId;
    }

    // Acquire an infinite lease (never expires)
    public async Task<string> AcquireInfiniteLeaseAsync()
    {
        var lease = await _leaseClient.AcquireAsync(TimeSpan.FromSeconds(-1));
        _leaseId = lease.Value.LeaseId;
        return _leaseId;
    }

    // Renew the lease before it expires
    public async Task RenewLeaseAsync()
    {
        await _leaseClient.RenewAsync();
    }

    // Release the lease when done
    public async Task ReleaseLeaseAsync()
    {
        await _leaseClient.ReleaseAsync();
        _leaseId = null;
    }

    // Break the lease (allows others to acquire immediately or after break period)
    public async Task BreakLeaseAsync(int breakPeriodSeconds = 0)
    {
        await _leaseClient.BreakAsync(TimeSpan.FromSeconds(breakPeriodSeconds));
        _leaseId = null;
    }

    // Modify blob with lease
    public async Task UpdateBlobWithLeaseAsync(Stream content)
    {
        if (string.IsNullOrEmpty(_leaseId))
            throw new InvalidOperationException("Must acquire lease first");

        // Use the lease ID in conditions for write operations
        await _blobClient.UploadAsync(content, new BlobUploadOptions
        {
            Conditions = new BlobRequestConditions { LeaseId = _leaseId }
        });
    }
}
```

**Using the Lease Manager:**

```csharp
var leaseManager = new BlobLeaseManager(connectionString, "documents", "report.pdf");

try
{
    // Acquire a 45-second lease
    string leaseId = await leaseManager.AcquireLeaseAsync(45);
    Console.WriteLine($"Acquired lease: {leaseId}");

    // Perform exclusive operations
    await using var content = new MemoryStream(Encoding.UTF8.GetBytes("Updated content"));
    await leaseManager.UpdateBlobWithLeaseAsync(content);

    // Renew if operation takes longer than expected
    await leaseManager.RenewLeaseAsync();

    // Release when done
    await leaseManager.ReleaseLeaseAsync();
}
catch (RequestFailedException ex) when (ex.ErrorCode == "LeaseAlreadyPresent")
{
    Console.WriteLine("Blob is already leased by another client");
}
```

## Exam Question Analysis

### Question: Uploading Files to Azure Blob Storage

**Scenario:**
You are developing an Azure application that needs to interact with Azure Blob Storage to upload files. You want to ensure that you are using the Azure SDK for .NET correctly.

**Question:**
Which of the following code snippets properly uploads a file to Azure Blob Storage using the Azure.Storage.Blobs library?

---

#### Option A: ❌ INCORRECT

```csharp
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("my-container");
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");
blobClient.UploadAsync(uploadFileStream, true);
```

**Why This Is Wrong:**
- ❌ Calls `UploadAsync` without `await` - the async operation is not awaited
- ❌ The `uploadFileStream` variable is not defined or opened
- ❌ Fire-and-forget async call may complete after method returns
- ❌ No error handling for the async operation

**What Should Be Fixed:**
```csharp
using FileStream uploadFileStream = File.OpenRead("path/to/myfile.txt");
await blobClient.UploadAsync(uploadFileStream, true);  // Add await!
```

---

#### Option B: ✅ CORRECT (Per Exam)

```csharp
BlobClient blobClient = new BlobClient(connectionString, "my-container", "myfile.txt");
using FileStream uploadFileStream = File.OpenRead("path/to/myfile.txt");
blobClient.Upload(uploadFileStream, overwrite: true);
```

**Why This Is Marked Correct:**
- ✅ Correctly creates a `BlobClient` using the constructor with connection string
- ✅ Opens a `FileStream` to read the local file
- ✅ Uses `using` statement for proper stream disposal
- ✅ Specifies `overwrite: true` to handle existing blobs
- ✅ Uses synchronous `Upload` method (valid, though async preferred)

**Note:** Direct `BlobClient` instantiation is valid for simple scenarios.

---

#### Option C: ⚠️ ALMOST CORRECT (Your Answer)

```csharp
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("my-container");
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");
using FileStream uploadFileStream = File.OpenRead("path/to/myfile.txt");
blobClient.Upload(uploadFileStream);
```

**Why This Is Almost Correct:**
- ✅ Uses the **hierarchical client pattern** (BlobServiceClient → BlobContainerClient → BlobClient)
- ✅ This pattern is actually **recommended by Microsoft** for most scenarios
- ✅ Properly creates and disposes the FileStream
- ✅ Valid synchronous upload code
- ⚠️ Missing `overwrite: true` - will throw exception if blob exists
- ⚠️ Uses synchronous method (async preferred but not required)

**The Hierarchical Pattern Is Actually Preferred Because:**
- Better for working with multiple containers/blobs
- Easier to manage shared credentials/options
- Aligns with SDK design philosophy
- More testable (can mock at different levels)

---

#### Option D: ❌ INCORRECT (Outdated SDK)

```csharp
CloudStorageAccount storageAccount = CloudStorageAccount.Parse(connectionString);
CloudBlobClient blobClient = storageAccount.CreateCloudBlobClient();
CloudBlobContainer container = blobClient.GetContainerReference("my-container");
CloudBlockBlob blockBlob = container.GetBlockBlobReference("myfile.txt");
using (var fileStream = File.OpenRead("path/to/myfile.txt"))
{
    blockBlob.UploadFromStream(fileStream);
}
```

**Why This Is Wrong:**
- ❌ Uses **legacy/deprecated** `Microsoft.Azure.Storage.Blob` library (v11 and earlier)
- ❌ `CloudStorageAccount`, `CloudBlobClient`, `CloudBlobContainer` are **obsolete classes**
- ❌ Not part of the modern `Azure.Storage.Blobs` library (v12+)
- ❌ The question specifically asks about `Azure.Storage.Blobs` library

**Modern Equivalent:**
```csharp
// Azure.Storage.Blobs (v12+) - the modern SDK
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("my-container");
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");
using FileStream fileStream = File.OpenRead("path/to/myfile.txt");
await blobClient.UploadAsync(fileStream, overwrite: true);
```

---

### Critical Analysis: Question Quality Issues

This exam question has some inconsistencies:

| Aspect | Option B (Correct) | Option C (Your Answer) |
|--------|-------------------|------------------------|
| **Valid Code** | ✓ Yes | ✓ Yes |
| **Uses Azure.Storage.Blobs** | ✓ Yes | ✓ Yes |
| **Sync vs Async** | Sync `Upload()` | Sync `Upload()` |
| **Client Pattern** | Direct instantiation | Hierarchical (preferred) |
| **Overwrite Parameter** | ✓ Specified | ✗ Missing |

**The Real Difference:** `overwrite: true` parameter

The exam marks Option C as "almost correct" because:
1. It doesn't specify overwrite behavior (defaults to `false`)
2. Will throw `RequestFailedException` if blob already exists

**However**, the exam's criticism of "synchronous method" applies equally to BOTH options - they both use `Upload()` not `UploadAsync()`.

---

### Best Practice: The Ideal Upload Code

```csharp
// ✅ BEST PRACTICE: Hierarchical pattern with async and overwrite
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("my-container");
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");

await using FileStream uploadFileStream = File.OpenRead("path/to/myfile.txt");
await blobClient.UploadAsync(uploadFileStream, overwrite: true);
```

**Or with full options:**

```csharp
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient("my-container");
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");

await using FileStream uploadFileStream = File.OpenRead("path/to/myfile.txt");
await blobClient.UploadAsync(uploadFileStream, new BlobUploadOptions
{
    HttpHeaders = new BlobHttpHeaders
    {
        ContentType = "text/plain"
    },
    Metadata = new Dictionary<string, string>
    {
        { "UploadedBy", "MyApp" },
        { "Version", "1.0" }
    }
});
```

---

### Key Takeaways

| Pattern | When to Use |
|---------|-------------|
| **Direct BlobClient** | Simple single-blob operations |
| **Hierarchical Pattern** | Multiple blobs/containers, shared credentials |
| **Sync Upload** | Console apps, simple scenarios |
| **Async UploadAsync** | Web apps, APIs, better scalability |

**For the Exam, Remember:**
- 🎯 Use `Azure.Storage.Blobs` (v12+), NOT `Microsoft.Azure.Storage.Blob`
- 🎯 `await` async methods properly
- 🎯 Use `overwrite: true` when re-uploading is expected
- 🎯 Dispose streams with `using` statement
- 🎯 Both direct and hierarchical patterns are valid

---

### Question: Uploading a File to Azure Blob Storage (SDK Methods)

**Scenario:**
You are developing an application that requires the ability to store and retrieve large amounts of unstructured data in Azure Blob Storage. You need to implement a solution that allows users to upload files to a specific container in Blob Storage.

**Question:**
Which of the following Azure SDK methods should you use to upload a file to a blob?

---

#### Option A: ❌ INCORRECT - `PutBlockBlobAsync()`

**Why This Is Wrong:**
- ❌ `PutBlockBlobAsync()` is **NOT** the correct method for uploading a file to a blob
- ❌ This method is used for uploading a **block blob**, which is different from uploading a file directly
- ❌ Block blob operations involve staging individual blocks and then committing a block list
- ⚠️ For direct file uploads, you should use higher-level methods that abstract this complexity

**When Block Blob Methods Are Used:**
```csharp
// Block blob operations are for large file uploads with chunking
BlockBlobClient blockBlobClient = containerClient.GetBlockBlobClient("largefile.zip");

// Stage individual blocks
await blockBlobClient.StageBlockAsync(blockId, blockStream);

// Commit the block list
await blockBlobClient.CommitBlockListAsync(blockIds);
```

---

#### Option B: ❌ INCORRECT - `CreateBlobAsync()`

**Why This Is Wrong:**
- ❌ `CreateBlobAsync()` is **NOT** the correct method for uploading a file
- ❌ This method is used for **creating** a new blob in Azure Blob Storage
- ❌ It does **NOT** handle the actual file upload process
- ⚠️ Creating a blob and uploading content are separate operations

**What CreateBlobAsync Does:**
- Creates an empty blob or blob placeholder
- Does not transfer file content from local system

---

#### Option C: ✅ CORRECT - `UploadFromFileAsync()`

**Why This Is Correct:**
- ✅ `UploadFromFileAsync()` is the **correct method** for uploading a file to a blob
- ✅ Allows users to upload a file from the **local file system** directly to a blob
- ✅ Handles the file reading and upload process automatically
- ✅ Simplifies the upload workflow by accepting a file path

**Example Usage:**
```csharp
// Using BlobClient
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");

// Upload directly from a file path
await blobClient.UploadAsync("path/to/local/myfile.txt", overwrite: true);

// Or using the explicit file upload method
await blobClient.UploadAsync(
    path: "path/to/local/myfile.txt",
    options: new BlobUploadOptions
    {
        HttpHeaders = new BlobHttpHeaders { ContentType = "text/plain" }
    }
);
```

**Note:** In the modern Azure.Storage.Blobs SDK (v12+), `UploadAsync()` has overloads that accept a file path directly, which is functionally equivalent to `UploadFromFileAsync()`.

---

#### Option D: ❌ INCORRECT - `UploadBlobAsync()`

**Why This Is Wrong:**
- ❌ `UploadBlobAsync()` does **NOT exist** in the Azure SDK for Blob Storage
- ❌ This is not a valid method for uploading files to Azure Blob Storage
- ⚠️ The correct methods are `UploadAsync()` on `BlobClient` or `UploadBlobAsync()` on `BlobContainerClient`

**Valid Upload Methods in Azure.Storage.Blobs:**

| Method | Class | Description |
|--------|-------|-------------|
| `UploadAsync(Stream)` | `BlobClient` | Upload from a stream |
| `UploadAsync(string path)` | `BlobClient` | Upload from a file path |
| `UploadAsync(BinaryData)` | `BlobClient` | Upload from binary data |
| `UploadBlobAsync(string, Stream)` | `BlobContainerClient` | Create and upload in one call |

---

### Key Takeaways for File Upload Methods

| Method | Valid? | Purpose |
|--------|--------|---------|
| `UploadFromFileAsync()` / `UploadAsync(path)` | ✅ | Upload file from local path |
| `UploadAsync(Stream)` | ✅ | Upload from a stream |
| `PutBlockBlobAsync()` | ❌ | For block blob staging operations |
| `CreateBlobAsync()` | ❌ | Creates blob, doesn't upload content |
| `UploadBlobAsync()` | ❌ | Does not exist on BlobClient |

**For the Exam, Remember:**
- 🎯 Use `UploadAsync()` or `UploadFromFileAsync()` for direct file uploads
- 🎯 Block blob methods are for advanced chunked upload scenarios
- 🎯 Know the difference between creating a blob and uploading content

---

### Question: Setting Custom Metadata on a Blob

**Scenario:**
You are developing an Azure application that stores images in Azure Blob Storage. You need to set custom metadata on a blob to track the image's resolution and color profile.

**Question:**
Which of the following code snippets correctly sets the metadata for a blob in C#?

---

#### Option 1: ❌ INCORRECT

```csharp
await blobClient.SetPropertiesAsync(new BlobHttpHeaders
{
    ContentType = "image/jpeg"
});
```

**Why This Is Wrong:**
- ❌ `SetPropertiesAsync` (or `SetHttpHeadersAsync` in newer SDK versions) sets **HTTP headers/system properties**
- ❌ Does NOT set custom metadata
- ❌ Only sets `ContentType`, which is a system property, not custom metadata
- ⚠️ Resolution and ColorProfile are NOT system properties - they are custom metadata

**What This Actually Does:**
- Sets the blob's MIME type to `image/jpeg`
- Affects how browsers/clients interpret the blob
- Does not store custom tracking information

---

#### Option 2: ✅ CORRECT

```csharp
await blobClient.SetMetadataAsync(new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
});
```

**Why This Is Correct:**
- ✅ Uses `SetMetadataAsync` - the dedicated method for setting custom metadata
- ✅ Provides key-value pairs in a `Dictionary<string, string>`
- ✅ Correctly stores Resolution and ColorProfile as custom metadata
- ✅ Allows tracking of custom information without modifying blob content

**Key Points:**
- `SetMetadataAsync` is specifically designed for custom metadata
- Metadata is stored as name-value pairs
- Can be retrieved later using `GetPropertiesAsync`

---

#### Option 3: ❌ INCORRECT

```csharp
await blobClient.UploadAsync(fileStream);
blobClient.Metadata["Resolution"] = "1920x1080";
blobClient.Metadata["ColorProfile"] = "sRGB";
await blobClient.SetMetadataAsync();
```

**Why This Is Wrong:**
- ⚠️ Modifying `blobClient.Metadata` locally doesn't guarantee sync with Azure
- ⚠️ The `Metadata` property might be null before calling `GetPropertiesAsync`
- ⚠️ This pattern is unreliable and may not work as expected
- ❌ Correct approach is to pass metadata dictionary directly to `SetMetadataAsync`

**What You Should Do Instead:**
```csharp
await blobClient.UploadAsync(fileStream);
await blobClient.SetMetadataAsync(new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
});
```

---

#### Option 4: ❌ INCORRECT

```csharp
var metadata = new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
};
await blobClient.UploadAsync(fileStream, new BlobHttpHeaders(), metadata);
```

**Why This Is Wrong:**
- ❌ This method overload doesn't exist in the Azure SDK
- ❌ `UploadAsync` doesn't accept `BlobHttpHeaders` and metadata as separate parameters
- ❌ Would result in a compile-time error

**Correct Way to Upload with Metadata:**
```csharp
var metadata = new Dictionary<string, string>
{
    { "Resolution", "1920x1080" },
    { "ColorProfile", "sRGB" }
};

await blobClient.UploadAsync(fileStream, new BlobUploadOptions
{
    Metadata = metadata,
    HttpHeaders = new BlobHttpHeaders
    {
        ContentType = "image/jpeg"
    }
});
```

---

### Question: Implementing Retry Logic for Large File Uploads

**Scenario:**
You are developing a .NET application that uploads large files to Azure Blob Storage. You need to implement retry logic to handle transient failures during upload operations.

**Question:**
Which approach should you use?

**Options:**

1. Configure retry policy in the BlobServiceClient after creating the BlobClient.
2. Use BlobRequestOptions parameter in the upload method call.
3. Implement manual retry logic using try-catch blocks around each upload operation.
4. Configure BlobClientOptions with retry properties and pass it to the BlobClient constructor.

**Answer:** Option 4 - Configure BlobClientOptions with retry properties and pass it to the BlobClient constructor.

---

#### Option 1: ❌ INCORRECT

**Configure retry policy in the BlobServiceClient after creating the BlobClient.**

**Why This Is Wrong:**
- ❌ Retry policies must be configured when creating the client through `BlobClientOptions`
- ❌ Cannot be modified after the client is instantiated
- ❌ The SDK doesn't support runtime modification of retry settings

---

#### Option 2: ❌ INCORRECT

**Use BlobRequestOptions parameter in the upload method call.**

**Why This Is Wrong:**
- ❌ `BlobRequestOptions` is from older SDK versions (Microsoft.WindowsAzure.Storage)
- ❌ Doesn't exist in the current Azure.Storage.Blobs SDK
- ❌ The modern SDK uses `BlobClientOptions` for configuring retry behavior

---

#### Option 3: ❌ INCORRECT

**Implement manual retry logic using try-catch blocks around each upload operation.**

**Why This Is Wrong:**
- ❌ Adds unnecessary complexity to your code
- ❌ The SDK provides built-in retry mechanisms through `BlobClientOptions`
- ❌ Manual implementation is error-prone and harder to maintain
- ❌ Built-in retry handles transient failures more efficiently and consistently

---

#### Option 4: ✅ CORRECT

**Configure BlobClientOptions with retry properties and pass it to the BlobClient constructor.**

```csharp
using Azure.Storage.Blobs;
using Azure.Core;

// Configure retry options
var options = new BlobClientOptions
{
    Retry =
    {
        MaxRetries = 5,
        Delay = TimeSpan.FromSeconds(2),
        MaxDelay = TimeSpan.FromSeconds(30),
        Mode = RetryMode.Exponential,
        NetworkTimeout = TimeSpan.FromMinutes(5)
    }
};

// Pass options to the client constructor
var blobServiceClient = new BlobServiceClient(connectionString, options);
var containerClient = blobServiceClient.GetBlobContainerClient("my-container");
var blobClient = containerClient.GetBlobClient("large-file.zip");

// Upload will automatically use configured retry policy
await blobClient.UploadAsync(fileStream, overwrite: true);
```

**Why This Is Correct:**
- ✅ `BlobClientOptions` with retry properties (MaxRetries and Delay) enables automatic retry handling
- ✅ Configures retry behavior at the client level
- ✅ This is the recommended approach for implementing retry logic in the Azure.Storage.Blobs SDK
- ✅ Handles transient failures automatically without additional code
- ✅ Supports exponential backoff for better handling of transient issues

**Key Retry Configuration Properties:**

| Property | Description | Default |
|----------|-------------|--------|
| `MaxRetries` | Maximum number of retry attempts | 3 |
| `Delay` | Initial delay between retries | 0.8 seconds |
| `MaxDelay` | Maximum delay between retries | 1 minute |
| `Mode` | Retry strategy (Fixed or Exponential) | Exponential |
| `NetworkTimeout` | Timeout for network operations | 100 seconds |

**Best Practice Example with Full Configuration:**

```csharp
using Azure.Storage.Blobs;
using Azure.Core;
using System;
using System.IO;
using System.Threading.Tasks;

public class BlobUploadService
{
    private readonly BlobServiceClient _blobServiceClient;

    public BlobUploadService(string connectionString)
    {
        var options = new BlobClientOptions
        {
            Retry =
            {
                MaxRetries = 5,
                Delay = TimeSpan.FromSeconds(2),
                MaxDelay = TimeSpan.FromSeconds(30),
                Mode = RetryMode.Exponential,
                NetworkTimeout = TimeSpan.FromMinutes(10) // Longer timeout for large files
            }
        };

        _blobServiceClient = new BlobServiceClient(connectionString, options);
    }

    public async Task UploadLargeFileAsync(
        string containerName, 
        string blobName, 
        string filePath)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        await containerClient.CreateIfNotExistsAsync();

        var blobClient = containerClient.GetBlobClient(blobName);

        await using var fileStream = File.OpenRead(filePath);
        
        // Retry logic is automatically applied based on BlobClientOptions
        await blobClient.UploadAsync(fileStream, overwrite: true);
    }
}
```

**Reference:**
- [Configure retry options for Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-retry-policy-dotnet)
- [Azure.Core RetryOptions](https://learn.microsoft.com/en-us/dotnet/api/azure.core.retryoptions)

---

### Question: Implementing Blob Lease for Exclusive Write Access

**Scenario:**
You are implementing blob lease functionality in a distributed application to ensure exclusive write access. You need to acquire a lease that automatically expires after 45 seconds if not renewed.

**Question:**
Which code should you use to acquire a blob lease?

---

#### Option A: ❌ INCORRECT

```csharp
Response<BlobLease> lease = await blobClient.AcquireLeaseAsync(TimeSpan.FromSeconds(45));
```

**Why This Is Wrong:**
- ❌ The `BlobClient` class does **NOT** have an `AcquireLeaseAsync` method
- ❌ Lease operations require creating a `BlobLeaseClient` first
- ❌ Must use `GetBlobLeaseClient()` to get the lease client before acquiring a lease

**The Correct Pattern:**
```csharp
// First get a BlobLeaseClient, then acquire the lease
BlobLeaseClient leaseClient = blobClient.GetBlobLeaseClient();
Response<BlobLease> lease = await leaseClient.AcquireAsync(TimeSpan.FromSeconds(45));
```

---

#### Option B: ❌ INCORRECT

```csharp
BlobLeaseClient leaseClient = blobClient.GetBlobLeaseClient();
Response<BlobLease> lease = await leaseClient.AcquireAsync(
    TimeSpan.FromSeconds(45), 
    conditions: new BlobLeaseRequestConditions { IfMatch = new ETag("*") }
);
```

**Why This Is Wrong:**
- ⚠️ Adding `IfMatch` condition with wildcard ETag (`*`) to a lease acquisition is **unnecessary**
- ❌ Lease acquisition does **NOT** require ETag matching conditions
- ❌ May cause issues or unexpected behavior since lease operations don't use ETag matching
- ⚠️ This adds complexity without benefit

**When to Use Conditions:**
- Conditions like `IfMatch` are used for **blob operations** (upload, delete), not for lease acquisition
- Lease acquisition doesn't need to verify blob content hasn't changed

---

#### Option C: ❌ INCORRECT

```csharp
BlobLeaseClient leaseClient = new BlobLeaseClient(blobClient, TimeSpan.FromSeconds(45));
Response<BlobLease> lease = await leaseClient.AcquireAsync();
```

**Why This Is Wrong:**
- ❌ The `BlobLeaseClient` constructor does **NOT** accept a `TimeSpan` parameter for lease duration
- ❌ The constructor signature is `BlobLeaseClient(BlobClient client, string leaseId = null)`
- ❌ The lease duration must be specified in the `AcquireAsync()` method, not in the constructor
- ⚠️ This code would result in a compile-time error

**Correct Constructor Usage:**
```csharp
// Constructor only accepts BlobClient and optional lease ID
BlobLeaseClient leaseClient = new BlobLeaseClient(blobClient); // No TimeSpan!
// or
BlobLeaseClient leaseClient = new BlobLeaseClient(blobClient, existingLeaseId);
```

---

#### Option D: ✅ CORRECT

```csharp
BlobLeaseClient leaseClient = blobClient.GetBlobLeaseClient();
Response<BlobLease> lease = await leaseClient.AcquireAsync(TimeSpan.FromSeconds(45));
```

**Why This Is Correct:**
- ✅ Correctly creates a `BlobLeaseClient` using `GetBlobLeaseClient()` method
- ✅ Acquires a lease with a 45-second duration using `AcquireAsync()`
- ✅ 45 seconds falls within the valid range of **15-60 seconds** for finite leases
- ✅ Uses the proper two-step process: get lease client → acquire lease

**Key Points:**
- `GetBlobLeaseClient()` creates a lease client bound to the blob
- `AcquireAsync(TimeSpan)` acquires the lease with specified duration
- Valid finite lease durations: 15-60 seconds
- Use `-1` (TimeSpan.FromSeconds(-1)) for infinite leases

---

### Key Takeaways for Blob Leases

| Aspect | Details |
|--------|---------|
| **Create Lease Client** | Use `blobClient.GetBlobLeaseClient()` |
| **Acquire Lease** | Use `leaseClient.AcquireAsync(TimeSpan duration)` |
| **Finite Lease Duration** | 15-60 seconds |
| **Infinite Lease** | `TimeSpan.FromSeconds(-1)` |
| **Release Lease** | `leaseClient.ReleaseAsync()` |

**For the Exam, Remember:**
- 🎯 `BlobClient` does NOT have lease methods - must use `BlobLeaseClient`
- 🎯 Use `GetBlobLeaseClient()` to create the lease client
- 🎯 Lease duration goes in `AcquireAsync()`, NOT in the constructor
- 🎯 Valid finite lease: 15-60 seconds
- 🎯 Don't add unnecessary conditions to lease acquisition

---

### Question: Storing Custom Application-Specific Data with Blobs

**Scenario:**
You need to store custom application-specific data with each blob in Azure Storage. The data should be retrievable without downloading the blob content.

**Question:**
What should you use?

**Domain:** Develop for Azure storage

---

#### Option A: ❌ INCORRECT - Blob Snapshots

**Why This Is Wrong:**
- ❌ Blob snapshots create **read-only copies** of blobs at specific points in time
- ❌ Snapshots are designed for **backup and versioning**, not for storing custom metadata
- ❌ Each snapshot is a complete copy of the blob at that moment
- ❌ Not designed for storing custom metadata with blobs

**What Blob Snapshots Are For:**
```csharp
// Create a snapshot - creates a read-only copy of the blob
BlobClient blobClient = containerClient.GetBlobClient("myfile.txt");
Response<BlobSnapshotInfo> snapshot = await blobClient.CreateSnapshotAsync();

// Access the snapshot
string snapshotUri = $"{blobClient.Uri}?snapshot={snapshot.Value.Snapshot}";
```

**Use Cases for Snapshots:**
- Creating point-in-time backups
- Recovering from accidental overwrites or deletions
- Maintaining historical versions of blobs

---

#### Option B: ✅ CORRECT - Blob Metadata

**Why This Is Correct:**
- ✅ Blob metadata consists of **name-value pairs** that can be stored with a blob
- ✅ Metadata can be **retrieved without downloading** the blob content
- ✅ Ideal for storing **custom application-specific data**
- ✅ Supports up to 8 KB of metadata per blob

**Example Usage:**
```csharp
// Set custom metadata
await blobClient.SetMetadataAsync(new Dictionary<string, string>
{
    { "ApplicationId", "MyApp-12345" },
    { "ProcessedBy", "ServiceA" },
    { "Category", "Reports" },
    { "CustomData", "any-application-specific-value" }
});

// Retrieve metadata WITHOUT downloading blob content
BlobProperties properties = await blobClient.GetPropertiesAsync();
foreach (var metadata in properties.Metadata)
{
    Console.WriteLine($"{metadata.Key}: {metadata.Value}");
}
```

**Key Benefits:**
- Stored directly with the blob
- Retrieved via `GetPropertiesAsync()` - no content download needed
- Supports any custom key-value data your application needs
- Can be set during upload or anytime after

---

#### Option C: ❌ INCORRECT - Blob Properties

**Why This Is Wrong:**
- ❌ Blob properties are **system-defined attributes**
- ❌ Properties include `ContentType`, `ContentLength`, `LastModified`, `ETag`, etc.
- ❌ **Cannot** be used to store custom application-specific data
- ❌ Only predefined system properties can be set

**System Properties Examples:**
```csharp
// These are system properties - NOT for custom data
BlobHttpHeaders headers = new BlobHttpHeaders
{
    ContentType = "application/pdf",        // System property
    CacheControl = "max-age=3600",          // System property
    ContentDisposition = "attachment"        // System property
};
await blobClient.SetHttpHeadersAsync(headers);
```

**Blob Properties Are Fixed:**
| Property | Description | Custom? |
|----------|-------------|---------|
| `ContentType` | MIME type | ❌ System-defined |
| `ContentLength` | Size in bytes | ❌ Read-only |
| `LastModified` | Last modification time | ❌ Read-only |
| `ETag` | Version identifier | ❌ Read-only |
| `ContentEncoding` | Encoding type | ❌ System-defined |

---

#### Option D: ❌ INCORRECT - Blob Index Tags

**Why This Is Wrong:**
- ⚠️ Blob index tags **can** store key-value pairs, BUT...
- ❌ They are designed for **searching and filtering** blobs across the storage account
- ❌ Not intended for storing arbitrary application data
- ❌ Limited to 10 tags per blob (vs 8 KB for metadata)
- ❌ Tags are indexed for query operations, not for general data storage

**What Blob Index Tags Are For:**
```csharp
// Set index tags - designed for SEARCHING
await blobClient.SetTagsAsync(new Dictionary<string, string>
{
    { "Status", "Processed" },
    { "Department", "Finance" }
});

// Query blobs by tags across the entire storage account
string query = "@container = 'mycontainer' AND Status = 'Processed'";
await foreach (TaggedBlobItem item in blobServiceClient.FindBlobsByTagsAsync(query))
{
    Console.WriteLine($"Found: {item.BlobName}");
}
```

**Comparison: Metadata vs Index Tags:**

| Feature | Blob Metadata | Blob Index Tags |
|---------|--------------|-----------------|
| **Purpose** | Store custom data | Search and filter blobs |
| **Max Size** | 8 KB total | 10 tags, limited size |
| **Queryable** | No | Yes, across account |
| **Use Case** | App-specific data | Blob organization/discovery |
| **Retrieve Without Content** | ✅ Yes | ✅ Yes |

---

### Key Takeaways for Storing Custom Data

| Option | Purpose | For Custom App Data? |
|--------|---------|---------------------|
| **Blob Metadata** | Store name-value pairs with blob | ✅ Yes - Ideal choice |
| **Blob Properties** | System-defined attributes | ❌ No - System only |
| **Blob Snapshots** | Point-in-time copies | ❌ No - For versioning |
| **Blob Index Tags** | Search/filter blobs | ⚠️ Possible but not intended |

**For the Exam, Remember:**
- 🎯 **Blob Metadata** = Custom application-specific data (retrievable without download)
- 🎯 **Blob Properties** = System-defined attributes only
- 🎯 **Blob Snapshots** = Read-only copies for backup/versioning
- 🎯 **Blob Index Tags** = Search and filter across storage account

---

### Question: HTTPS with Custom Domain for Static Website

**Scenario:**
You have a static website hosted in Azure Blob Storage. You need to serve the website through Azure CDN with HTTPS support on a custom domain.

**Question:**
What must you configure because Azure Storage doesn't natively support this scenario?

---

#### Option A: ✅ CORRECT - Azure CDN to enable HTTPS with custom domains

**Why This Is Correct:**
- ✅ Azure Blob Storage **doesn't natively support HTTPS with custom domains** for static websites
- ✅ Azure CDN provides **HTTPS termination** for custom domains
- ✅ CDN is the **recommended solution** for enabling HTTPS on custom domains for static websites
- ✅ Simple to configure and purpose-built for this scenario

**How It Works:**
1. Enable static website hosting in Azure Blob Storage
2. Create an Azure CDN profile and endpoint
3. Configure the CDN endpoint to use your custom domain
4. Enable HTTPS on the custom domain (CDN provides free managed certificates)

---

#### Option B: ❌ INCORRECT - Azure Traffic Manager with SSL certificates

**Why This Is Wrong:**
- ❌ Traffic Manager is a **DNS-based traffic load balancer**
- ❌ Traffic Manager does **NOT** provide SSL/HTTPS termination
- ❌ It only routes traffic based on DNS - cannot solve the HTTPS custom domain requirement
- ❌ Traffic Manager works at the DNS layer, not the HTTP/HTTPS layer

**What Traffic Manager Is For:**
- Load balancing across multiple Azure regions
- Geographic routing
- Priority-based failover
- Performance-based routing

---

#### Option C: ❌ INCORRECT - Azure Front Door with Web Application Firewall

**Why This Is Wrong:**
- ⚠️ Azure Front Door **can** provide HTTPS and custom domains
- ❌ However, it's **unnecessarily complex** for this scenario
- ❌ Front Door includes global load balancing, caching, and WAF - overkill for a simple static website
- ❌ Azure CDN is the **recommended and simpler solution** for static website HTTPS

**When to Use Front Door:**
- Global load balancing requirements
- Advanced WAF protection needed
- Complex routing rules
- Multi-region deployments

---

#### Option D: ❌ INCORRECT - Azure Application Gateway with SSL termination

**Why This Is Wrong:**
- ❌ Application Gateway is designed for **load balancing web applications**, not serving static content
- ❌ It's **overly complex** for adding HTTPS to static website custom domains
- ❌ Requires a virtual network and more infrastructure
- ❌ Not the appropriate solution for this use case

**When to Use Application Gateway:**
- Layer 7 load balancing for web applications
- SSL offloading for backend servers
- URL-based routing
- Session affinity requirements

---

### Key Takeaways for Static Website HTTPS

| Solution | Can Provide HTTPS? | Recommended? | Why/Why Not |
|----------|-------------------|--------------|-------------|
| **Azure CDN** | ✅ Yes | ✅ **Recommended** | Purpose-built, simple, free managed certs |
| **Azure Front Door** | ✅ Yes | ⚠️ Overkill | Too complex for simple static sites |
| **Traffic Manager** | ❌ No | ❌ No | DNS-only, no HTTPS termination |
| **Application Gateway** | ✅ Yes | ❌ No | Designed for apps, not static content |

**For the Exam, Remember:**
- 🎯 **Azure Blob Storage** does NOT support HTTPS with custom domains for static websites
- 🎯 **Azure CDN** is the recommended solution for HTTPS on custom domains
- 🎯 **Traffic Manager** is DNS-based and cannot provide HTTPS termination

---

### Key Takeaways

| Method | Purpose | Use For |
|--------|---------|---------|
| `SetMetadataAsync` | Set custom key-value pairs | ✅ Custom tracking (Resolution, ColorProfile) |
| `SetHttpHeadersAsync` | Set HTTP headers | System properties (ContentType, CacheControl) |
| `UploadAsync` with `BlobUploadOptions` | Upload blob with settings | Both metadata and headers during upload |

**Remember:**
- 🎯 **Custom Metadata** → Use `SetMetadataAsync` with a `Dictionary<string, string>`
- 🎯 **System Properties** → Use `SetHttpHeadersAsync` with `BlobHttpHeaders`
- 🎯 **During Upload** → Use `BlobUploadOptions` to set both

## Best Practices

### Metadata Best Practices

1. **Use Meaningful Keys**: Choose descriptive, consistent key names
   ```csharp
   // ✅ Good
   { "ImageResolution", "1920x1080" }
   { "ProcessedDate", "2025-01-15" }
   
   // ❌ Bad
   { "x", "1920x1080" }
   { "d", "2025-01-15" }
   ```

2. **Keep Metadata Small**: Total metadata must be under 8 KB
   ```csharp
   // ✅ Good - store reference
   { "ProcessingLogUrl", "https://logs.example.com/12345" }
   
   // ❌ Bad - storing large data
   { "ProcessingLog", "... 50KB of log data ..." }
   ```

3. **Use Consistent Naming Conventions**:
   ```csharp
   // Choose one style and stick with it
   { "imageWidth", "1920" }      // camelCase
   { "ImageWidth", "1920" }      // PascalCase
   { "image_width", "1920" }     // snake_case (use underscores, not hyphens)
   ```

4. **Version Your Metadata Schema**:
   ```csharp
   { "MetadataVersion", "2.0" }
   { "Resolution", "1920x1080" }
   ```

5. **Store Only Strings**: Convert other types appropriately
   ```csharp
   { "ProcessedDate", DateTime.UtcNow.ToString("O") }
   { "FileSize", fileSize.ToString() }
   { "IsProcessed", "true" }
   ```

### Properties Best Practices

1. **Set Correct ContentType**: Ensures proper handling by browsers/clients
   ```csharp
   // For images
   ContentType = "image/jpeg"
   
   // For PDFs
   ContentType = "application/pdf"
   
   // For JSON
   ContentType = "application/json"
   ```

2. **Use CacheControl for Performance**:
   ```csharp
   // Cache static assets
   CacheControl = "max-age=31536000, immutable"
   
   // Don't cache dynamic content
   CacheControl = "no-cache, no-store"
   ```

3. **Set ContentDisposition for Downloads**:
   ```csharp
   // Force download
   ContentDisposition = "attachment; filename=\"report.pdf\""
   
   // Display in browser
   ContentDisposition = "inline; filename=\"report.pdf\""
   ```

### Blob Lease Best Practices

1. **Use Finite Leases for Auto-Expiration**: Set lease duration between 15-60 seconds for auto-expiration
   ```csharp
   // ✅ Good - auto-expires if process crashes
   await leaseClient.AcquireAsync(TimeSpan.FromSeconds(30));
   ```

2. **Renew Leases Before Expiration**: Keep the lease active during long operations
   ```csharp
   // Renew before the 45-second lease expires
   await leaseClient.RenewAsync();
   ```

3. **Release Leases When Done**: Free up resources for other clients
   ```csharp
   await leaseClient.ReleaseAsync();
   ```

4. **Handle Lease Conflicts Gracefully**: Catch exceptions when lease is held by others
   ```csharp
   try
   {
       await leaseClient.AcquireAsync(TimeSpan.FromSeconds(30));
   }
   catch (RequestFailedException ex) when (ex.ErrorCode == "LeaseAlreadyPresent")
   {
       // Handle conflict - blob is leased by another client
   }
   ```

## References

- [Set Blob Metadata - REST API](https://learn.microsoft.com/en-us/rest/api/storageservices/set-blob-metadata)
- [Get Blob Properties - REST API](https://learn.microsoft.com/en-us/rest/api/storageservices/get-blob-properties)
- [Set Blob Properties - REST API](https://learn.microsoft.com/en-us/rest/api/storageservices/set-blob-properties)
- [Azure.Storage.Blobs - .NET SDK](https://learn.microsoft.com/en-us/dotnet/api/azure.storage.blobs)
- [Manage blob properties and metadata with .NET](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-properties-metadata)
- [azure-storage-blob - Python SDK](https://learn.microsoft.com/en-us/python/api/azure-storage-blob/)
- [Lease Blob - REST API](https://learn.microsoft.com/en-us/rest/api/storageservices/lease-blob)
- [BlobLeaseClient Class - .NET SDK](https://learn.microsoft.com/en-us/dotnet/api/azure.storage.blobs.specialized.blobleaseclient)

