# Secure Access to Azure Storage

## Table of Contents

- [Overview](#overview)
- [Authentication Methods](#authentication-methods)
  - [Shared Key (Storage Account Keys)](#1-shared-key-storage-account-keys)
  - [Shared Access Signature (SAS)](#2-shared-access-signature-sas)
  - [Microsoft Entra ID (Azure Active Directory)](#3-microsoft-entra-id-azure-active-directory)
  - [Anonymous Public Read Access](#4-anonymous-public-read-access)
- [Shared Access Signature (SAS) Types](#shared-access-signature-sas-types)
  - [Comparison Table](#comparison-table)
  - [Account SAS](#1-account-sas)
  - [Service SAS](#2-service-sas)
  - [User Delegation SAS](#3-user-delegation-sas--most-secure)
  - [Stored Access Policy](#4-stored-access-policy)
- [Service Support for User Delegation SAS](#service-support-for-user-delegation-sas)
  - [Critical Limitation: Blob Storage Only](#critical-limitation-blob-storage-only)
  - [Why Only Blob Storage?](#why-only-blob-storage)
  - [Exam Question: Identifying Supported Services](#exam-question-identifying-supported-services)
  - [Decision Matrix: Choosing SAS Type by Service](#decision-matrix-choosing-sas-type-by-service)
- [Exam Question Analysis](#exam-question-analysis)
  - [Question 1: Container Access with Entra ID and RBAC](#question-1-container-access-with-entra-id-and-rbac)
  - [Question 3: SAS with Microsoft Entra ID Credentials for Enhanced Security](#question-3-sas-with-microsoft-entra-id-credentials-for-enhanced-security)
  - [Question 4: RBAC Action Required for User Delegation Key](#question-4-rbac-action-required-for-user-delegation-key)
- [SAS Security Best Practices](#sas-security-best-practices)
- [RBAC Roles for Storage Access](#rbac-roles-for-storage-access)
  - [Common Built-in Roles](#common-built-in-roles)
  - [Common Azure Storage RBAC Actions Reference](#common-azure-storage-rbac-actions-reference)
  - [Assigning RBAC Roles](#assigning-rbac-roles)
  - [Using Managed Identity with User Delegation SAS](#using-managed-identity-with-user-delegation-sas)
- [Comparison: Authentication Methods](#comparison-authentication-methods)
- [Additional Security Features](#additional-security-features)
  - [Storage Account Firewall](#1-storage-account-firewall)
  - [Storage Firewall Network Rule Types](#storage-firewall-network-rule-types)
  - [Resource Instance Rules](#resource-instance-rules)
  - [Azure Storage Encryption Options](#6-azure-storage-encryption-options)
  - [Exam Question: Multi-Tenant Encryption](#exam-question-multi-tenant-encryption)
- [Troubleshooting SAS Issues](#troubleshooting-sas-issues)
  - [Common Errors and Solutions](#common-errors-and-solutions)
  - [Testing SAS Tokens](#testing-sas-tokens)
- [Quick Reference: When to Use Each SAS Type](#quick-reference-when-to-use-each-sas-type)
- [References](#references)

## Overview

Azure Storage provides multiple layers of security to protect your data and control access. This document covers authentication methods, authorization mechanisms, and Shared Access Signatures (SAS) - focusing on the different SAS types and when to use each.

## Authentication Methods

### 1. Shared Key (Storage Account Keys)

- **Description**: Uses storage account access keys for authentication
- **Characteristics**:
  - Provides full access to all resources in the storage account
  - Two keys available (primary and secondary) for key rotation
  - Least secure option - keys provide complete access
- **Use Cases**: Legacy applications, development/testing
- **Best Practice**: Avoid in production; rotate keys regularly if used

### 2. Shared Access Signature (SAS)

- **Description**: Provides delegated access with specific permissions and time limits
- **Characteristics**:
  - Granular control over permissions and access duration
  - Multiple types available (Account, Service, User Delegation)
  - Can be revoked using stored access policies
- **Use Cases**: Granting temporary access to clients, third-party applications
- **Best Practice**: Use short expiration times and minimal permissions

### 3. Microsoft Entra ID (Azure Active Directory)

- **Description**: Identity-based authentication using Azure AD credentials
- **Characteristics**:
  - Most secure authentication method
  - Supports RBAC (Role-Based Access Control)
  - Works with managed identities for Azure resources
  - No need to store credentials in code
- **Use Cases**: Production applications, service-to-service authentication
- **Best Practice**: Always prefer this method when possible

### 4. Anonymous Public Read Access

- **Description**: Allows public access to blobs and containers without authentication
- **Characteristics**:
  - Can be enabled at blob or container level
  - No authentication required
  - Limited to read-only access
- **Use Cases**: Public websites, CDN content, public downloads
- **Best Practice**: Disable at storage account level unless explicitly needed

## Shared Access Signature (SAS) Types

Azure Storage supports three types of Shared Access Signatures, each designed for different scenarios and security requirements.

### Comparison Table

| Feature | Account SAS | Service SAS | User Delegation SAS |
|---------|-------------|-------------|---------------------|
| **Secured By** | Storage Account Key | Storage Account Key | Microsoft Entra ID |
| **RBAC Support** | No | No | Yes ✅ |
| **Scope** | Account-level (multiple services) | Single service only | Single service only |
| **Services Supported** | Blob, Queue, Table, File | Blob, Queue, Table, File | **Blob only** ⚠️ |
| **Container Access** | Yes | Yes | Yes ✅ |
| **Most Secure** | No | No | Yes ✅ |
| **Can Be Revoked** | Only with key rotation | Via stored access policy | Via Entra ID credentials |
| **Requires Entra ID** | No | No | Yes ✅ |

### 1. Account SAS

**Definition**: Delegates access to resources in one or more storage services at the account level.

**Characteristics**:
- Signed with storage account key
- Can access multiple services (Blob, Queue, Table, File)
- Provides account-level operations
- Cannot be revoked without regenerating account keys

**Syntax Example**:
```
https://myaccount.blob.core.windows.net/?restype=service&comp=properties
&sv=2021-06-08&ss=bf&srt=s&st=2025-01-01T00:00:00Z&se=2025-01-02T00:00:00Z
&sr=c&sp=r&sig=<signature>
```

**When to Use**:
- Need to access multiple storage services with one SAS
- Require account-level operations (e.g., service properties)
- Internal systems where key management is acceptable

**Limitations**:
- ❌ Not secured with Microsoft Entra ID
- ❌ No RBAC support
- ❌ Revocation requires key regeneration (affects all SAS tokens)

**Code Example**:
```csharp
using Azure.Storage;
using Azure.Storage.Sas;
using Azure.Storage.Blobs;

// Create account SAS
var storageAccountKey = "<account-key>";
var accountName = "myaccount";

var sasBuilder = new AccountSasBuilder
{
    Services = AccountSasServices.Blobs | AccountSasServices.Queues,
    ResourceTypes = AccountSasResourceTypes.Service | AccountSasResourceTypes.Container,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1),
    Protocol = SasProtocol.Https
};

sasBuilder.SetPermissions(AccountSasPermissions.Read | AccountSasPermissions.List);

var credential = new StorageSharedKeyCredential(accountName, storageAccountKey);
var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();

Console.WriteLine($"Account SAS: {sasToken}");
```

### 2. Service SAS

**Definition**: Delegates access to a resource in a single storage service (Blob, Queue, Table, or File).

**Characteristics**:
- Signed with storage account key
- Limited to one service type
- Can use stored access policies for revocation
- More granular than Account SAS

**Syntax Example**:
```
https://myaccount.blob.core.windows.net/container1/blob1.txt
?sv=2021-06-08&st=2025-01-01T00:00:00Z&se=2025-01-02T00:00:00Z
&sr=b&sp=r&sig=<signature>
```

**When to Use**:
- Need to grant access to specific blobs, containers, queues, or tables
- Want to use stored access policies for easier management
- Single service access is sufficient

**Stored Access Policy Integration**:
```csharp
// Create stored access policy
var container = new BlobContainerClient(connectionString, "container1");
var policy = new BlobSignedIdentifier
{
    Id = "policy1",
    AccessPolicy = new BlobAccessPolicy
    {
        StartsOn = DateTimeOffset.UtcNow,
        ExpiresOn = DateTimeOffset.UtcNow.AddHours(24),
        Permissions = "r"
    }
};

await container.SetAccessPolicyAsync(permissions: new[] { policy });

// Create service SAS using stored access policy
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Identifier = "policy1" // Reference to stored access policy
};

var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
```

**Limitations**:
- ❌ Not secured with Microsoft Entra ID
- ❌ No RBAC support
- ⚠️ Revocation requires stored access policy or key regeneration

### 3. User Delegation SAS ⭐ (Most Secure)

**Definition**: A SAS secured with Microsoft Entra ID credentials instead of storage account keys.

**Characteristics**:
- Signed with Microsoft Entra ID credentials (user delegation key)
- Supports RBAC permissions
- Can be revoked by revoking the user delegation key
- Most secure SAS type
- Requires Microsoft Entra ID authentication
- **⚠️ IMPORTANT: Only supported for Blob Storage** (not File, Queue, or Table)

**Why It's Most Secure**:
1. ✅ **No Storage Keys Exposed**: Doesn't use account keys
2. ✅ **RBAC Integration**: Uses Azure AD permissions
3. ✅ **Granular Revocation**: Can revoke without affecting other SAS tokens
4. ✅ **Audit Trail**: Tracks who created the SAS via Azure AD
5. ✅ **Identity-Based**: Tied to specific Azure AD identities

**Syntax Example**:
```
https://myaccount.blob.core.windows.net/container1/blob1.txt
?sv=2021-06-08&st=2025-01-01T00:00:00Z&se=2025-01-02T00:00:00Z
&sr=b&sp=r&skoid=<key-oid>&sktid=<tenant-id>&skt=<key-start>&ske=<key-expiry>
&sks=b&skv=2021-06-08&sig=<signature>
```

**When to Use**:
- ✅ Need to secure SAS with Microsoft Entra ID credentials
- ✅ RBAC support is required
- ✅ Maximum security is needed
- ✅ Production environments
- ✅ Compliance requirements mandate identity-based access

**Code Example**:
```csharp
using Azure.Identity;
using Azure.Storage.Blobs;
using Azure.Storage.Sas;

// Authenticate with Azure AD (using DefaultAzureCredential)
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://myaccount.blob.core.windows.net"),
    credential
);

// Get user delegation key (valid for up to 7 days)
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddHours(1)
);

// Create user delegation SAS for container
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c", // "c" for container, "b" for blob
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};

// Set permissions (must match or be subset of user's RBAC permissions)
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read | BlobContainerSasPermissions.List);

// Generate the SAS token
var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
).ToString();

var sasUri = $"https://myaccount.blob.core.windows.net/container1?{sasToken}";
Console.WriteLine($"User Delegation SAS URI: {sasUri}");
```

**Required RBAC Roles** (to create User Delegation SAS):
- `Storage Blob Data Reader` - For read access
- `Storage Blob Data Contributor` - For read/write access
- `Storage Blob Data Owner` - For full access

**Revoking User Delegation SAS**:
```csharp
// Revoke all user delegation keys (invalidates all user delegation SAS tokens)
await blobServiceClient.RevokeUserDelegationKeysAsync();

// This does NOT affect account or service SAS tokens
```

### 4. Stored Access Policy

**Important**: A stored access policy is **NOT** a type of SAS itself. It's a policy that can be associated with a Service SAS to provide additional control.

**Characteristics**:
- Defined at container, queue, table, or file share level
- Can modify or revoke Service SAS tokens that reference it
- Provides centralized management of SAS permissions
- Maximum 5 policies per container/queue/table/share

#### Stored Access Policy Level for Blob Storage

**Exam Question**: At which level should you associate the stored access policy for blob storage?

**Answer**: **Container level**

**Why Container Level?**
- ✅ **Stored access policies for blobs must be associated at the container level**
- ✅ The policy applies to all blobs within that container when generating shared access signatures
- ✅ Enables centralized management of SAS permissions for all blobs in the container

**Why NOT Other Levels?**

| Level | Supports Stored Access Policy? | Notes |
|-------|-------------------------------|-------|
| **Container** | ✅ **Yes** | Required level for blob stored access policies |
| **Individual Blob** | ❌ **No** | Individual blobs can be associated with SAS keys but do not support stored access policies |
| **Blob Service** | ❌ **No** | Can be associated with SAS keys but does not support stored access policies |
| **Storage Account** | ❌ **No** | Can be associated with SAS keys but does not support stored access policies |

**Key Takeaway**: When implementing stored access policies for shared access signatures on blob storage, always associate them at the **container level**.

**Benefits**:
- Change permissions without regenerating SAS tokens
- Revoke access by deleting the policy
- Centralized permission management

**Example**:
```csharp
// Define stored access policy
var container = new BlobContainerClient(connectionString, "container1");

var policy = new BlobSignedIdentifier
{
    Id = "read-policy",
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(7),
        Permissions = "rl" // Read and List
    }
};

await container.SetAccessPolicyAsync(permissions: new[] { policy });

// Create service SAS that references the policy
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c",
    Identifier = "read-policy" // References the stored access policy
};

var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();

// Later: Revoke access by removing the policy
await container.SetAccessPolicyAsync(permissions: Array.Empty<BlobSignedIdentifier>());
```

**Limitations**:
- ❌ Only works with Service SAS (not Account or User Delegation SAS)
- ❌ Still uses storage account keys for signing
- ❌ No Microsoft Entra ID integration

### Modifying SAS Expiry Date After Creation

**Key Concept**: You cannot directly modify the expiry date of a shared access signature after it has been created. However, if you create the SAS using a **stored access policy**, you can modify the constraints (including expiry time) by updating the policy.

**Question**: How can you modify the expiry date and time of a shared access signature after it's already been created?

**Answer**: Create the shared access signature using a stored access policy. When you associate a Service SAS with a stored access policy, the SAS inherits the constraints—the start time, expiry time, and permissions—defined for the stored access policy. You can modify the stored access policy at any time after the SAS has been created.

**What Does NOT Work**:
- ❌ You cannot edit a SAS directly in the Azure Portal SAS blade after creation
- ❌ You cannot modify the expiry date of an ad-hoc SAS (one without a stored access policy)
- ❌ The only way to change an ad-hoc SAS is to recreate it entirely

**Why Stored Access Policy Works**:
- The SAS token references the policy by identifier (not the actual constraints)
- When the SAS is validated, Azure reads the current constraints from the policy
- Updating the policy immediately affects all SAS tokens that reference it

**Example - Extending SAS Expiry via Stored Access Policy**:
```csharp
// Original policy with 7-day expiry
var policy = new BlobSignedIdentifier
{
    Id = "my-policy",
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(7),
        Permissions = "rl"
    }
};
await container.SetAccessPolicyAsync(permissions: new[] { policy });

// ... time passes, need to extend expiry ...

// Update the policy to extend expiry (affects all SAS tokens using this policy)
var updatedPolicy = new BlobSignedIdentifier
{
    Id = "my-policy", // Same identifier
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(30), // Extended to 30 days
        Permissions = "rl"
    }
};
await container.SetAccessPolicyAsync(permissions: new[] { updatedPolicy });

// All existing SAS tokens referencing "my-policy" now have the new expiry date
```

**Best Practice for Flexible SAS Management**:
- Always use stored access policies when you anticipate needing to modify SAS constraints
- Use stored access policies for third-party or partner access where revocation may be needed
- Ad-hoc SAS is suitable only for one-time, short-lived access where modification won't be needed

**Reference**: [Microsoft Doc: Storage SAS Overview](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview)

## Service Support for User Delegation SAS

### Critical Limitation: Blob Storage Only

**User Delegation SAS is ONLY supported for Azure Blob Storage.** This is a key limitation to remember for exams and real-world implementations.

| Storage Service | Account SAS | Service SAS | User Delegation SAS |
|----------------|-------------|-------------|---------------------|
| **Blob** | ✅ Supported | ✅ Supported | ✅ **Supported** |
| **File** | ✅ Supported | ✅ Supported | ❌ **Not Supported** |
| **Queue** | ✅ Supported | ✅ Supported | ❌ **Not Supported** |
| **Table** | ✅ Supported | ✅ Supported | ❌ **Not Supported** |

### Why Only Blob Storage?

**Technical Reasons:**
- Blob Storage has the most mature integration with Microsoft Entra ID
- RBAC roles are well-defined for blob operations
- User delegation key mechanism was designed specifically for blob access
- Other services (File, Queue, Table) still rely on shared key authentication for SAS

**Implications:**
- If you need Entra ID-secured access to File, Queue, or Table → Use Account or Service SAS
- For maximum security with non-Blob services → Use direct Entra ID authentication (not SAS)
- Blob Storage is the only service where you can combine SAS with Entra ID credentials

### Exam Question: Identifying Supported Services

**Question**: You plan to use a shared access signature to protect access to services within a general-purpose v2 storage account. You need to identify the type of service that you can protect by using the user delegation shared access signature.

**Options Analysis:**

#### Blob ✅ **CORRECT**
**Why Correct:**
- ✅ Only storage service that supports User Delegation SAS
- ✅ Full integration with Microsoft Entra ID authentication
- ✅ Supports all RBAC roles for blob operations
- ✅ Can create user delegation keys for blob access

**Example:**
```csharp
// User Delegation SAS works for Blob Storage
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://myaccount.blob.core.windows.net"),
    credential
);

var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    DateTimeOffset.UtcNow,
    DateTimeOffset.UtcNow.AddHours(1)
);

var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    Resource = "c",
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);

var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
);
```

#### File ❌ **INCORRECT**
**Why Wrong:**
- ❌ Does NOT support User Delegation SAS
- ✅ Supports Account SAS
- ✅ Supports Service SAS
- ⚠️ Only shared key-based SAS available

**Available Options for File:**
```csharp
// File service must use Account or Service SAS
var credential = new StorageSharedKeyCredential(accountName, accountKey);

// Service SAS for File Share
var sasBuilder = new ShareSasBuilder
{
    ShareName = "myshare",
    Resource = "s", // Share
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};
sasBuilder.SetPermissions(ShareSasPermissions.Read);

var sasToken = sasBuilder.ToSasQueryParameters(credential);
// Note: Uses StorageSharedKeyCredential, not Azure AD
```

**Alternative for File with Entra ID:**
- Use direct Azure AD authentication (not SAS)
- Requires SMB protocol with Azure AD Domain Services
- Not available for REST API access

#### Queue ❌ **INCORRECT**
**Why Wrong:**
- ❌ Does NOT support User Delegation SAS
- ✅ Supports Account SAS
- ✅ Supports Service SAS
- ⚠️ Only shared key-based SAS available

**Available Options for Queue:**
```csharp
// Queue service must use Account or Service SAS
var credential = new StorageSharedKeyCredential(accountName, accountKey);

// Service SAS for Queue
var sasBuilder = new QueueSasBuilder
{
    QueueName = "myqueue",
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};
sasBuilder.SetPermissions(QueueSasPermissions.Read | QueueSasPermissions.Add);

var sasToken = sasBuilder.ToSasQueryParameters(credential);
// Note: Uses StorageSharedKeyCredential, not Azure AD
```

**Alternative for Queue with Entra ID:**
```csharp
// Use direct Azure AD authentication (not SAS)
var credential = new DefaultAzureCredential();
var queueClient = new QueueClient(
    new Uri("https://myaccount.queue.core.windows.net/myqueue"),
    credential
);

// This uses RBAC directly, not SAS
await queueClient.SendMessageAsync("Hello, World!");
```

#### Table ❌ **INCORRECT**
**Why Wrong:**
- ❌ Does NOT support User Delegation SAS
- ✅ Supports Account SAS
- ✅ Supports Service SAS
- ⚠️ Only shared key-based SAS available

**Available Options for Table:**
```csharp
// Table service must use Account or Service SAS
var credential = new StorageSharedKeyCredential(accountName, accountKey);

// Service SAS for Table
var sasBuilder = new TableSasBuilder(
    tableName: "mytable",
    permissions: TableSasPermissions.Read | TableSasPermissions.Add,
    expiresOn: DateTimeOffset.UtcNow.AddHours(1)
);

var sasToken = sasBuilder.ToSasQueryParameters(credential);
// Note: Uses StorageSharedKeyCredential, not Azure AD
```

**Note:** Azure Table Storage does not currently support direct Azure AD authentication via RBAC for data plane operations.

### Decision Matrix: Choosing SAS Type by Service

```
Need Entra ID + SAS?
│
├─ Blob Storage → User Delegation SAS ✅
│
├─ File Storage → Service SAS + Stored Access Policy ⚠️
│                 (or use SMB with Azure AD Domain Services)
│
├─ Queue Storage → Service SAS + Stored Access Policy ⚠️
│                  (or use direct Azure AD auth without SAS)
│
└─ Table Storage → Service SAS + Stored Access Policy ⚠️
                   (direct Azure AD auth not available)
```

### Key Takeaway for Exams

**Question Pattern:** "Which service supports User Delegation SAS?"
**Answer:** **Blob Storage only**

**Remember:**
- 🎯 User Delegation SAS = Blob Storage ONLY
- 🔐 Most secure SAS type, but limited to blobs
- 📊 File, Queue, Table = Account SAS or Service SAS only
- ✨ For non-blob services needing Entra ID → Use direct authentication (not SAS)

## Exam Question Analysis

### Question 1: Securing SAS Token Generation with Entra ID

**Scenario:**
You plan to generate a shared access signature (SAS) token for read access to a blob in a storage account. You need to secure the token from being compromised.

**Question:**
What should you use?

**Options:**
1. Primary account key
2. Secondary account key
3. Microsoft Entra ID credentials assigned the Contributor role ✅
4. Microsoft Entra ID credentials assigned the Reader role ❌

**Correct Answer: Microsoft Entra ID credentials assigned the Contributor role**

**Detailed Analysis:**

#### Why Microsoft Entra ID Credentials Assigned the Contributor Role is CORRECT ✅

**Key Points:**
- ✅ **Most Secure**: Microsoft Entra ID credentials are required to generate a **User Delegation SAS**
- ✅ **Required Permission**: The account must have the `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey` permission
- ✅ **Built-in Roles with This Permission**:
  - **Contributor** ✅
  - Storage Account Contributor
  - Storage Blob Data Contributor
  - Storage Blob Data Owner
  - Storage Blob Data Reader
  - Storage Blob Delegator

**Why This Prevents Compromise:**
- ❌ No storage account keys exposed in the SAS token
- ✅ Token is signed with a user delegation key from Azure AD
- ✅ Can be revoked without regenerating storage account keys
- ✅ Provides audit trail through Azure AD
- ✅ Integrates with conditional access policies
- ✅ Supports RBAC permissions

**Implementation Example:**
```csharp
// Authenticate with Microsoft Entra ID (Contributor role assigned)
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://mystorageaccount.blob.core.windows.net"),
    credential
);

// Get user delegation key (requires generateUserDelegationKey permission)
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddHours(1)
);

// Create User Delegation SAS for blob read access
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    BlobName = "myblob.txt",
    Resource = "b", // Blob
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};

// Set read permissions
sasBuilder.SetPermissions(BlobSasPermissions.Read);

// Generate the secure SAS token (signed with user delegation key, not account key)
var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
).ToString();

var secureSasUri = $"https://mystorageaccount.blob.core.windows.net/mycontainer/myblob.txt?{sasToken}";
```

**Security Comparison:**

| Method | Signed With | Compromise Risk | Revocation |
|--------|-------------|-----------------|------------|
| **User Delegation SAS** (Entra ID) | User delegation key | ✅ Low - No keys exposed | ✅ Easy - Revoke delegation key |
| **Service/Account SAS** (Account Key) | Storage account key | ❌ High - Key can be extracted | ❌ Hard - Must regenerate keys |

#### Why Primary Account Key is INCORRECT ❌

**Key Points:**
- ❌ **Less Secure**: Account keys can be more easily compromised
- ❌ **Full Access**: Provides complete access to the entire storage account
- ❌ **Difficult Revocation**: Must regenerate keys to revoke access
- ❌ **Key Exposure**: SAS token generation exposes the account key in your code/configuration

**Security Risks:**
```csharp
// ❌ BAD: Using account key to generate SAS
var accountKey = "abc123..."; // Key exposed in code/config
var credential = new StorageSharedKeyCredential(accountName, accountKey);

var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    BlobName = "myblob.txt",
    Resource = "b",
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};

sasBuilder.SetPermissions(BlobSasPermissions.Read);

// SAS is signed with account key - if compromised, full storage access possible
var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
```

**Why It's More Easily Compromised:**
- 🔓 Account key stored in configuration files, code, or environment variables
- 🔓 Key visible in logs, source control, or deployment pipelines
- 🔓 If key is leaked, attacker has full storage account access
- 🔓 Revocation requires regenerating key (affects all applications using it)

#### Why Secondary Account Key is INCORRECT ❌

**Key Points:**
- ❌ **Same Security Issues**: Secondary key has identical security concerns as primary key
- ❌ **Purpose**: Designed for key rotation, not improved security
- ❌ **Still Key-Based**: Does not provide Entra ID security benefits

**Intended Use of Secondary Key:**
```csharp
// Secondary key is for rotation, not security
// Step 1: Applications use primary key
// Step 2: Generate new secondary key
// Step 3: Update applications to use secondary key
// Step 4: Generate new primary key
// Step 5: Update applications back to primary key

// ❌ This doesn't make SAS more secure from compromise
```

**Key Rotation Strategy (Still Not as Secure as Entra ID):**
```bash
# Regenerate secondary key without disrupting apps using primary
az storage account keys renew \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --key secondary

# Update apps to use secondary key, then regenerate primary
az storage account keys renew \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --key primary
```

#### Why Microsoft Entra ID Credentials Assigned the Reader Role is INCORRECT ❌

**Key Points:**
- ❌ **Insufficient Permissions**: Reader role does NOT have the `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey` permission
- ❌ **Cannot Generate User Delegation Key**: Will fail when attempting to create User Delegation SAS
- ⚠️ Reader role provides read-only access to resource metadata, not data plane operations

**What Reader Role Includes:**
```json
// Reader role permissions (limited to control plane)
{
  "permissions": [
    {
      "actions": [
        "*/read"  // Can read resource properties, not data
      ],
      "notActions": [],
      "dataActions": [],  // ❌ No data plane permissions
      "notDataActions": []
    }
  ]
}
```

**Error When Using Reader Role:**
```csharp
// Assuming identity has only Reader role assigned
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://mystorageaccount.blob.core.windows.net"),
    credential
);

try
{
    // ❌ This will FAIL with authorization error
    var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
        DateTimeOffset.UtcNow,
        DateTimeOffset.UtcNow.AddHours(1)
    );
}
catch (Azure.RequestFailedException ex)
{
    // Error: AuthorizationPermissionMismatch
    // The client does not have permission to perform this action
    Console.WriteLine($"Failed: {ex.Message}");
}
```

**Required Roles Comparison:**

| Role | Has generateUserDelegationKey Permission | Can Create User Delegation SAS |
|------|------------------------------------------|-------------------------------|
| **Contributor** | ✅ Yes | ✅ Yes |
| **Storage Account Contributor** | ✅ Yes | ✅ Yes |
| **Storage Blob Data Contributor** | ✅ Yes | ✅ Yes |
| **Storage Blob Data Owner** | ✅ Yes | ✅ Yes |
| **Storage Blob Data Reader** | ✅ Yes | ✅ Yes |
| **Storage Blob Delegator** | ✅ Yes | ✅ Yes |
| **Reader** | ❌ No | ❌ No |

### Key Takeaways

**Question Pattern:** "How to secure SAS token from being compromised?"

**Answer:** Use **Microsoft Entra ID credentials with appropriate permissions** (Contributor or Storage-specific roles)

**Why This Matters:**
1. 🔐 **Security**: User Delegation SAS doesn't expose account keys
2. 🔑 **Revocation**: Can revoke without affecting other applications
3. 📊 **Audit**: Azure AD provides complete audit trail
4. ✅ **Best Practice**: Microsoft-recommended approach for production
5. 🛡️ **Compliance**: Meets security requirements without key management risks

**Minimum Required Permission:**
- Control Plane: `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey`
- Data Plane: Appropriate RBAC role for the operations (e.g., Storage Blob Data Reader for read access)

**Complete Secure Pattern:**
```csharp
// ✅ BEST PRACTICE: Secure SAS generation
public async Task<string> GenerateSecureBlobSasAsync(
    string storageAccountName,
    string containerName,
    string blobName)
{
    // 1. Authenticate with Azure AD (Contributor or Storage role required)
    var credential = new DefaultAzureCredential();
    var blobServiceClient = new BlobServiceClient(
        new Uri($"https://{storageAccountName}.blob.core.windows.net"),
        credential
    );
    
    // 2. Get user delegation key (requires generateUserDelegationKey permission)
    var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
        startsOn: DateTimeOffset.UtcNow,
        expiresOn: DateTimeOffset.UtcNow.AddHours(1)
    );
    
    // 3. Create User Delegation SAS
    var sasBuilder = new BlobSasBuilder
    {
        BlobContainerName = containerName,
        BlobName = blobName,
        Resource = "b",
        StartsOn = DateTimeOffset.UtcNow,
        ExpiresOn = DateTimeOffset.UtcNow.AddHours(1),
        Protocol = SasProtocol.Https // ✅ HTTPS only
    };
    
    sasBuilder.SetPermissions(BlobSasPermissions.Read);
    
    // 4. Generate secure token (no account keys involved)
    var sasToken = sasBuilder.ToSasQueryParameters(
        userDelegationKey.Value,
        storageAccountName
    ).ToString();
    
    // 5. Return secure SAS URI
    return $"https://{storageAccountName}.blob.core.windows.net/{containerName}/{blobName}?{sasToken}";
}
```

### Question 2: Securing SAS for Supplier Access

**Scenario:**
You develop an application that will be accessed by a supplier. The supplier requires a shared access signature (SAS) to access Azure services in your company's subscription. You need to secure the SAS.

**Question:**
Which three actions should you take? Each correct answer presents a complete solution.

**Options:**
1. Always use HTTPS
2. Grant permission to multiple resources
3. Use Azure Monitor and Azure Storage logs to monitor the application
4. Define a stored access policy for a service SAS
5. Set a long expiration time

**Correct Answers:**
1. ✅ **Always use HTTPS**
2. ✅ **Use Azure Monitor and Azure Storage logs to monitor the application**
3. ✅ **Define a stored access policy for a service SAS**

**Detailed Analysis:**

#### 1. Always use HTTPS ✅ **CORRECT**

**Why This Is Correct:**
- SAS tokens contain sensitive authorization information
- HTTPS encrypts the SAS token in transit, preventing interception
- Protocol can be enforced when creating the SAS

**Implementation:**
```csharp
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "supplier-data",
    Resource = "c",
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(2),
    Protocol = SasProtocol.Https // ✅ Force HTTPS only
};
```

**Security Risk of HTTP:**
- SAS token visible in network traffic
- Vulnerable to man-in-the-middle attacks
- Token can be intercepted and reused

**Best Practice:**
```csharp
// ✅ GOOD: Enforce HTTPS
sasBuilder.Protocol = SasProtocol.Https;

// ❌ BAD: Allow HTTP
sasBuilder.Protocol = SasProtocol.HttpsAndHttp;
```

#### 2. Grant permission to multiple resources ❌ **INCORRECT**

**Why This Is Wrong:**
- Violates the **principle of least privilege**
- Increases attack surface if SAS is compromised
- Supplier should only access what they absolutely need

**Security Best Practice:**
- Grant minimal permissions required for the task
- Scope SAS to specific resources (not multiple)
- Limit to single container or blob when possible

**Example of Bad vs. Good Practice:**
```csharp
// ❌ BAD: Account SAS with access to all services
var accountSasBuilder = new AccountSasBuilder
{
    Services = AccountSasServices.All, // ❌ Too broad
    ResourceTypes = AccountSasResourceTypes.All, // ❌ Too broad
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(2)
};

// ✅ GOOD: Service SAS scoped to specific container
var serviceSasBuilder = new BlobSasBuilder
{
    BlobContainerName = "supplier-invoices", // ✅ Specific container
    Resource = "c",
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(2)
};
serviceSasBuilder.SetPermissions(
    BlobContainerSasPermissions.Read | // ✅ Minimal permissions
    BlobContainerSasPermissions.List
);
```

**Impact of Over-Permissioning:**
- If SAS leaked, attacker gains access to multiple resources
- Harder to audit and track access patterns
- Increases compliance risks

#### 3. Use Azure Monitor and Azure Storage logs to monitor the application ✅ **CORRECT**

**Why This Is Correct:**
- Detect suspicious access patterns and potential security breaches
- Monitor for authorization failures (failed SAS attempts)
- Track SAS usage for compliance and auditing
- Alert on unusual activity

**Implementation:**
```csharp
// Enable Storage Analytics logging
var blobServiceClient = new BlobServiceClient(connectionString);
var properties = await blobServiceClient.GetPropertiesAsync();

properties.Value.Logging = new BlobAnalyticsLogging
{
    Version = "1.0",
    Read = true,
    Write = true,
    Delete = true,
    RetentionPolicy = new BlobRetentionPolicy
    {
        Enabled = true,
        Days = 30 // Retain logs for compliance
    }
};

await blobServiceClient.SetPropertiesAsync(properties);
```

**Azure Monitor Integration:**
```bash
# Create alert for failed SAS authentications
az monitor metrics alert create \
    --name "SAS-Authentication-Failures" \
    --resource-group myResourceGroup \
    --scopes /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account} \
    --condition "count AuthenticationError > 10" \
    --window-size 5m \
    --evaluation-frequency 1m
```

**What to Monitor:**
- Authorization failures (potential brute force or leaked tokens)
- Unusual access patterns (time of day, frequency)
- Access from unexpected IP addresses
- Operations performed (read, write, delete)

**Log Analysis Example:**
```kusto
// Query storage logs for SAS authentication failures
StorageBlobLogs
| where AuthenticationType == "SAS"
| where StatusCode >= 400
| summarize FailureCount = count() by AccountName, CallerIpAddress, bin(TimeGenerated, 5m)
| where FailureCount > 10
| order by TimeGenerated desc
```

#### 4. Define a stored access policy for a service SAS ✅ **CORRECT**

**Why This Is Correct:**
- Enables **revocation** without regenerating storage account keys
- Allows **modification** of permissions after SAS is issued
- Provides **centralized management** of multiple SAS tokens
- **Critical for third-party access** where you may need to revoke quickly

**Without Stored Access Policy:**
- Cannot revoke SAS without regenerating account keys
- Regenerating keys invalidates ALL SAS tokens (not just supplier's)
- No way to modify permissions after SAS is issued

**Implementation:**
```csharp
// Step 1: Create stored access policy
var container = new BlobContainerClient(connectionString, "supplier-data");

var policy = new BlobSignedIdentifier
{
    Id = "supplier-read-policy",
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(30),
        Permissions = "rl" // Read and List
    }
};

await container.SetAccessPolicyAsync(permissions: new[] { policy });

// Step 2: Create Service SAS that references the policy
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "supplier-data",
    Resource = "c",
    Identifier = "supplier-read-policy" // ✅ References stored policy
};

var sasToken = sasBuilder.ToSasQueryParameters(
    new StorageSharedKeyCredential(accountName, accountKey)
).ToString();

var sasUri = $"https://{accountName}.blob.core.windows.net/supplier-data?{sasToken}";
// Share this URI with supplier
```

**Revocation Capability:**
```csharp
// If supplier access needs to be revoked immediately
// Option 1: Remove the policy (revokes ALL SAS tokens using it)
await container.SetAccessPolicyAsync(
    permissions: Array.Empty<BlobSignedIdentifier>()
);

// Option 2: Modify policy permissions
var updatedPolicy = new BlobSignedIdentifier
{
    Id = "supplier-read-policy",
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow, // ✅ Immediate expiration
        Permissions = "" // ✅ No permissions
    }
};
await container.SetAccessPolicyAsync(permissions: new[] { updatedPolicy });
```

**Benefits for Supplier Scenario:**
- ✅ Revoke supplier access without affecting other systems
- ✅ Extend or reduce access period as needed
- ✅ Modify permissions without reissuing SAS token
- ✅ Easier audit trail (policy name identifies supplier)

#### 5. Set a long expiration time ❌ **INCORRECT**

**Why This Is Wrong:**
- **Security risk**: If SAS is compromised, attacker has extended access
- Violates **least privilege principle** for time-based access
- Harder to track and audit access patterns
- May not comply with security policies

**Security Best Practice:**
- Use **short expiration times** (hours, not days/months)
- Implement **token renewal mechanism** for legitimate ongoing access
- Balance usability with security

**Example of Bad vs. Good Practice:**
```csharp
// ❌ BAD: Long expiration (1 year)
sasBuilder.ExpiresOn = DateTimeOffset.UtcNow.AddYears(1);

// ✅ GOOD: Short expiration (2 hours) with renewal
sasBuilder.ExpiresOn = DateTimeOffset.UtcNow.AddHours(2);

// ✅ GOOD: Reasonable expiration with stored access policy (30 days)
var policy = new BlobAccessPolicy
{
    PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(30),
    Permissions = "r"
};
```

**Recommended Expiration Times:**

| Scenario | Recommended Expiration |
|----------|----------------------|
| **Ad-hoc access** | 1-2 hours |
| **Daily batch job** | 4-8 hours |
| **Third-party integration** | 1-7 days (with stored policy for revocation) |
| **Long-term supplier access** | Use stored access policy (up to 30 days) + renewal |

**Implementing Token Renewal:**
```csharp
// Supplier application requests new SAS before expiration
public async Task<string> RenewSupplierSasAsync(string supplierId)
{
    // Verify supplier is still authorized
    if (!await IsSupplierAuthorizedAsync(supplierId))
    {
        throw new UnauthorizedAccessException("Supplier access revoked");
    }
    
    // Generate new short-lived SAS
    var sasBuilder = new BlobSasBuilder
    {
        BlobContainerName = $"supplier-{supplierId}",
        Resource = "c",
        StartsOn = DateTimeOffset.UtcNow,
        ExpiresOn = DateTimeOffset.UtcNow.AddHours(4), // ✅ Short expiration
        Identifier = $"supplier-{supplierId}-policy"
    };
    
    var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
    
    // Log renewal for audit
    await LogSasRenewalAsync(supplierId);
    
    return sasToken;
}
```

**Risk Analysis:**

| Expiration Period | Risk Level | Mitigation |
|------------------|-----------|------------|
| **1 hour** | Low | May require frequent renewal |
| **1 day** | Medium | Use stored access policy for revocation |
| **1 month** | High | Requires robust monitoring and revocation plan |
| **1 year** | Very High | ❌ Not recommended - use alternative auth |

### Key Takeaways for Supplier SAS Security

**The Three Pillars:**
1. 🔒 **Transport Security**: Always use HTTPS
2. 📊 **Monitoring**: Use Azure Monitor and Storage logs
3. 🔑 **Revocation Control**: Define stored access policy

**Additional Best Practices:**
- ✅ Grant minimal permissions (least privilege)
- ✅ Use short expiration times
- ✅ Implement IP restrictions when possible
- ✅ Use User Delegation SAS for blob storage (if supplier supports Entra ID)
- ✅ Implement token renewal mechanism
- ✅ Document supplier access in audit logs

**Complete Secure Implementation:**
```csharp
public async Task<string> CreateSecureSupplierSasAsync(string supplierId, string containerName)
{
    var container = new BlobContainerClient(connectionString, containerName);
    
    // 1. Create stored access policy (for revocation)
    var policy = new BlobSignedIdentifier
    {
        Id = $"supplier-{supplierId}-policy",
        AccessPolicy = new BlobAccessPolicy
        {
            PolicyStartsOn = DateTimeOffset.UtcNow,
            PolicyExpiresOn = DateTimeOffset.UtcNow.AddDays(7), // Weekly renewal
            Permissions = "rl" // Read and List only (least privilege)
        }
    };
    
    await container.SetAccessPolicyAsync(permissions: new[] { policy });
    
    // 2. Create Service SAS with stored policy
    var sasBuilder = new BlobSasBuilder
    {
        BlobContainerName = containerName,
        Resource = "c",
        Identifier = $"supplier-{supplierId}-policy",
        Protocol = SasProtocol.Https // ✅ HTTPS only
    };
    
    // 3. Optional: IP restriction
    if (!string.IsNullOrEmpty(supplierIpAddress))
    {
        sasBuilder.IPRange = new SasIPRange(IPAddress.Parse(supplierIpAddress));
    }
    
    var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
    var sasUri = $"https://{accountName}.blob.core.windows.net/{containerName}?{sasToken}";
    
    // 4. Enable logging and monitoring
    await EnableStorageLoggingAsync();
    await CreateMonitoringAlertAsync(supplierId);
    
    // 5. Log SAS creation for audit
    await LogSasCreationAsync(supplierId, containerName, DateTimeOffset.UtcNow.AddDays(7));
    
    return sasUri;
}
```

### Question 2: Container Access with Entra ID and RBAC

**Requirements:**
1. ✅ SAS token secured with Microsoft Entra ID credentials
2. ✅ RBAC support
3. ✅ Support for granting access to containers

**Correct Answer: User Delegation SAS**

**Why Each Answer Is Right or Wrong:**

#### 1. Account SAS ❌
**Why Wrong:**
- ❌ Signed with storage account key, not Entra ID credentials
- ❌ No RBAC support - permissions defined in SAS token itself
- ✅ Does support container access (but fails other requirements)

**Use Case**: Multi-service access where Entra ID is not required

#### 2. User Delegation SAS ✅ **CORRECT**
**Why Correct:**
- ✅ Secured with Microsoft Entra ID credentials (user delegation key)
- ✅ Full RBAC support - uses Azure AD permissions
- ✅ Supports granting access to containers
- ✅ Most secure option

**Additional Benefits:**
- Can be revoked without regenerating storage account keys
- Provides audit trail through Azure AD
- No need to expose storage account keys
- Integrates with conditional access policies

**Code Example for Container Access:**
```csharp
// Authenticate with Azure AD
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://mystorageaccount.blob.core.windows.net"),
    credential
);

// Get user delegation key
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddHours(2)
);

// Create SAS for container access
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c", // Container level
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(2)
};

// Set permissions based on RBAC
sasBuilder.SetPermissions(
    BlobContainerSasPermissions.Read | 
    BlobContainerSasPermissions.List |
    BlobContainerSasPermissions.Write
);

// Generate token
var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
);

var containerSasUri = new BlobContainerClient(
    new Uri($"https://mystorageaccount.blob.core.windows.net/container1?{sasToken}")
);
```

#### 3. Service SAS ❌
**Why Wrong:**
- ❌ Signed with storage account key, not Entra ID credentials
- ❌ No RBAC support
- ✅ Does support container access (but fails other requirements)

**Use Case**: Single-service access with stored access policies for revocation

#### 4. Stored Access Policy ❌
**Why Wrong:**
- ❌ Not a SAS type - it's a policy mechanism for Service SAS
- ❌ Does not secure SAS with Entra ID credentials
- ❌ No direct RBAC support
- ⚠️ Can only be used with Service SAS

**What It Actually Does:**
- Groups Service SAS tokens for centralized management
- Allows modification of permissions without regenerating tokens
- Provides revocation capability for Service SAS

**Use Case**: Managing multiple Service SAS tokens with centralized control

### Question 3: SAS with Microsoft Entra ID Credentials for Enhanced Security

**Scenario:**
You need to create a SAS token for blob storage that uses Microsoft Entra credentials for enhanced security. The SAS must be valid for 5 days.

**Question:**
Which type of SAS should you create?

**Options:**
1. Stored access policy SAS
2. Account SAS
3. Service SAS
4. User delegation SAS ✅

**Correct Answer: User delegation SAS**

**Detailed Analysis:**

#### Why User Delegation SAS is CORRECT ✅

**Key Points:**
- ✅ **Microsoft Entra ID Security**: User delegation SAS is secured with Microsoft Entra ID credentials instead of the account key
- ✅ **Superior Security**: Provides enhanced security as it doesn't expose storage account keys
- ✅ **7-Day Maximum Validity**: The maximum interval over which the user delegation key is valid is **7 days** from the start date
- ✅ **5-Day Period Supported**: Since 5 days is less than the 7-day maximum, this requirement can be fulfilled

**Important Limitation:**
```
User Delegation Key Maximum Validity: 7 days
Requested Validity Period: 5 days ✅ (within limit)
```

**Implementation Example:**
```csharp
// Authenticate with Microsoft Entra ID
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://mystorageaccount.blob.core.windows.net"),
    credential
);

// Get user delegation key (maximum 7 days)
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddDays(5) // ✅ 5 days is within 7-day limit
);

// Create User Delegation SAS
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    BlobName = "myblob.txt",
    Resource = "b",
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddDays(5) // ✅ 5-day validity
};

sasBuilder.SetPermissions(BlobSasPermissions.Read);

var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
).ToString();
```

#### Why Stored Access Policy SAS is INCORRECT ❌

**Key Points:**
- ❌ **Not a Distinct SAS Type**: Stored access policies are a feature that can be associated with Service SAS, not a separate SAS type
- ❌ **Not Supported for User Delegation SAS**: Stored access policies cannot be used with user delegation SAS
- ❌ **Uses Storage Account Key**: Still requires storage account key for signing, not Microsoft Entra credentials

#### Why Account SAS is INCORRECT ❌

**Key Points:**
- ❌ **Secured with Storage Account Key**: Account SAS is signed using the storage account key, NOT Microsoft Entra credentials
- ❌ **Fails Enhanced Security Requirement**: Does not meet the requirement for Microsoft Entra-based authentication
- ❌ **No RBAC Support**: Cannot leverage Azure AD role-based access control

#### Why Service SAS is INCORRECT ❌

**Key Points:**
- ❌ **Secured with Storage Account Key**: Service SAS is signed using the storage account key, NOT Microsoft Entra credentials
- ❌ **Fails Enhanced Security Requirement**: Does not meet the requirement for Microsoft Entra-based authentication
- ❌ **No RBAC Support**: Cannot leverage Azure AD role-based access control

**Comparison Table:**

| SAS Type | Secured By | Entra ID Support | Max Validity for Delegation Key |
|----------|------------|------------------|--------------------------------|
| **User Delegation SAS** | Microsoft Entra ID ✅ | Yes ✅ | 7 days |
| **Account SAS** | Storage Account Key ❌ | No ❌ | N/A |
| **Service SAS** | Storage Account Key ❌ | No ❌ | N/A |
| **Stored Access Policy** | Not a SAS type ❌ | No ❌ | N/A |

### Key Takeaway

When the question asks for:
- **Microsoft Entra ID credentials** + **RBAC** + **Container access**
- **Answer**: User Delegation SAS (only option that supports Entra ID and RBAC)

**User Delegation Key Validity Rule:**
- Maximum validity period: **7 days**
- Any SAS requirement ≤ 7 days can use User Delegation SAS
- For longer periods, consider implementing SAS renewal mechanisms

### Question 4: RBAC Action Required for User Delegation Key

**Scenario:**
You need to request a user delegation key for creating a user delegation SAS.

**Question:**
Which Azure RBAC action must be assigned to the security principal?

**Options:**
1. `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action` ✅
2. `Microsoft.Storage/storageAccounts/listkeys/action`
3. `Microsoft.Storage/storageAccounts/blobServices/write`
4. `Microsoft.Authorization/roleAssignments/write`

**Correct Answer: `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action`**

**Detailed Analysis:**

#### Why `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action` is CORRECT ✅

**Key Points:**
- ✅ **Specific Permission**: This action specifically allows requesting user delegation keys
- ✅ **Required for User Delegation SAS**: A client that creates a user delegation SAS must be assigned an Azure RBAC role that includes this action
- ✅ **Built-in Roles with This Permission**:
  - Storage Blob Data Contributor
  - Storage Blob Data Owner
  - Storage Blob Data Reader
  - Storage Blob Delegator
  - Contributor

**Implementation Example:**
```csharp
// The security principal calling this method must have
// Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddHours(1)
);
```

#### Why `Microsoft.Storage/storageAccounts/listkeys/action` is INCORRECT ❌

**Key Points:**
- ❌ **Wrong Purpose**: The `listkeys` action provides access to storage account keys, NOT user delegation keys
- ❌ **Security Concern**: User delegation SAS specifically avoids using account keys for security
- ❌ **Different Mechanism**: Account keys and user delegation keys are fundamentally different authentication mechanisms

#### Why `Microsoft.Storage/storageAccounts/blobServices/write` is INCORRECT ❌

**Key Points:**
- ❌ **Wrong Scope**: The `write` action allows modifying blob service properties
- ❌ **Doesn't Grant Key Generation**: This permission doesn't include the ability to generate user delegation keys
- ❌ **Different Operation**: Writing to blob services is a data plane operation, while generating delegation keys is a control plane operation

#### Why `Microsoft.Authorization/roleAssignments/write` is INCORRECT ❌

**Key Points:**
- ❌ **Different Service**: This action allows creating role assignments in Azure RBAC
- ❌ **Not Storage Related**: It's an authorization management permission, not a storage permission
- ❌ **Wrong Context**: This doesn't provide any permission to generate user delegation keys for blob storage

**Comparison Table:**

| RBAC Action | Purpose | User Delegation Key? |
|-------------|---------|----------------------|
| `generateUserDelegationKey/action` | Request user delegation keys | ✅ Yes |
| `listkeys/action` | Access storage account keys | ❌ No |
| `blobServices/write` | Modify blob service properties | ❌ No |
| `roleAssignments/write` | Create role assignments | ❌ No |

### Key Takeaway

When implementing user delegation SAS, ensure the security principal has the `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action` permission. This is typically included in:
- **Storage Blob Delegator** - Minimal role specifically for delegation key generation
- **Storage Blob Data Contributor/Owner/Reader** - Data access roles that also include delegation
- **Contributor** - Broader role that includes this permission

## SAS Security Best Practices

### 1. Choose the Right SAS Type

```
High Security Requirements → User Delegation SAS
   ↓
Single Service + Need Revocation → Service SAS + Stored Access Policy
   ↓
Multiple Services → Account SAS
   ↓
Legacy/Development → Storage Account Keys
```

### 2. Minimize Permissions

```csharp
// ❌ BAD: Granting excessive permissions
sasBuilder.SetPermissions(BlobContainerSasPermissions.All);

// ✅ GOOD: Minimal required permissions
sasBuilder.SetPermissions(
    BlobContainerSasPermissions.Read | 
    BlobContainerSasPermissions.List
);
```

### 3. Use Short Expiration Times

```csharp
// ❌ BAD: Long expiration
sasBuilder.ExpiresOn = DateTimeOffset.UtcNow.AddDays(365);

// ✅ GOOD: Short expiration with renewal mechanism
sasBuilder.ExpiresOn = DateTimeOffset.UtcNow.AddHours(1);
```

### 4. Enforce HTTPS Only

```csharp
// ✅ Always enforce HTTPS
sasBuilder.Protocol = SasProtocol.Https;
```

### 5. Use IP Restrictions When Possible

```csharp
// ✅ Restrict to specific IP ranges
sasBuilder.IPRange = new SasIPRange(
    start: IPAddress.Parse("203.0.113.0"),
    end: IPAddress.Parse("203.0.113.255")
);
```

### 6. Implement SAS Revocation Strategy

**For User Delegation SAS:**
```csharp
// Revoke all user delegation keys
await blobServiceClient.RevokeUserDelegationKeysAsync();
```

**For Service SAS with Stored Access Policy:**
```csharp
// Remove the stored access policy
await container.SetAccessPolicyAsync(
    permissions: Array.Empty<BlobSignedIdentifier>()
);
```

**For Account/Service SAS without Policy:**
```csharp
// Regenerate storage account keys (affects ALL SAS tokens)
// Use Azure Portal, CLI, or Management SDK
```

### 7. Monitor SAS Usage

```csharp
// Enable Storage Analytics logging
var blobServiceClient = new BlobServiceClient(connectionString);
var properties = await blobServiceClient.GetPropertiesAsync();

properties.Value.Logging = new BlobAnalyticsLogging
{
    Version = "1.0",
    Read = true,
    Write = true,
    Delete = true,
    RetentionPolicy = new BlobRetentionPolicy
    {
        Enabled = true,
        Days = 7
    }
};

await blobServiceClient.SetPropertiesAsync(properties);
```

### 8. Never Store SAS Tokens in Code

```csharp
// ❌ BAD: Hardcoded SAS token
var sasToken = "sv=2021-06-08&ss=b&srt=sco&sp=rwdlac&...";

// ✅ GOOD: Generate SAS on-demand or store in secure configuration
var sasToken = await GenerateUserDelegationSasAsync();

// ✅ GOOD: Use Azure Key Vault for sensitive configuration
var client = new SecretClient(new Uri(keyVaultUrl), new DefaultAzureCredential());
var secret = await client.GetSecretAsync("storage-sas-token");
```

## RBAC Roles for Storage Access

> **Note:** For a comprehensive guide on Azure RBAC Actions fundamentals (action format, Actions vs DataActions, wildcards, custom roles, etc.), see [Azure RBAC Permission Models](../../azure_security/azure-rbac-permission-models.md#understanding-azure-rbac-actions).

### Common Built-in Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Storage Blob Data Owner** | Full access to blobs and containers | Admin operations |
| **Storage Blob Data Contributor** | Read, write, delete blobs and containers | Application data access |
| **Storage Blob Data Reader** | Read blobs and containers | Read-only access |
| **Storage Queue Data Contributor** | Read, write, delete queue messages | Queue processing |
| **Storage Queue Data Reader** | Read queue messages | Queue monitoring |
| **Storage Queue Data Message Processor** | Peek, receive, delete messages | Queue consumer |
| **Storage Queue Data Message Sender** | Send queue messages | Queue producer |

### Common Azure Storage RBAC Actions Reference

This table lists frequently tested RBAC actions for Azure Storage operations:

| RBAC Action | Description | Use Case |
|-------------|-------------|----------|
| `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action` | Request user delegation keys for creating User Delegation SAS | Creating secure SAS tokens with Entra ID |
| `Microsoft.Storage/storageAccounts/listkeys/action` | List storage account access keys | Legacy applications, account key access |
| `Microsoft.Storage/storageAccounts/regeneratekey/action` | Regenerate storage account keys | Key rotation |
| `Microsoft.Storage/storageAccounts/blobServices/containers/read` | Read container properties and metadata | Listing containers, getting container info |
| `Microsoft.Storage/storageAccounts/blobServices/containers/write` | Create or modify containers | Container management |
| `Microsoft.Storage/storageAccounts/blobServices/containers/delete` | Delete containers | Container cleanup |
| `Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read` | Read blob data | Reading blob content |
| `Microsoft.Storage/storageAccounts/blobServices/containers/blobs/write` | Write blob data | Uploading/modifying blobs |
| `Microsoft.Storage/storageAccounts/blobServices/containers/blobs/delete` | Delete blobs | Removing blobs |
| `Microsoft.Storage/storageAccounts/fileServices/fileshares/read` | Read file share properties | File share access |
| `Microsoft.Storage/storageAccounts/fileServices/fileshares/write` | Create or modify file shares | File share management |
| `Microsoft.Storage/storageAccounts/queueServices/queues/read` | Read queue properties | Queue monitoring |
| `Microsoft.Storage/storageAccounts/queueServices/queues/write` | Create or modify queues | Queue management |
| `Microsoft.Storage/storageAccounts/tableServices/tables/read` | Read table properties | Table access |
| `Microsoft.Storage/storageAccounts/tableServices/tables/write` | Create or modify tables | Table management |

**Key Action Categories:**

| Category | Action Pattern | Example |
|----------|---------------|---------|
| **Key Management** | `listkeys`, `regeneratekey` | Account key operations |
| **Delegation** | `generateUserDelegationKey` | User Delegation SAS |
| **Data Plane - Read** | `*/read` | Reading data/properties |
| **Data Plane - Write** | `*/write` | Creating/modifying resources |
| **Data Plane - Delete** | `*/delete` | Removing resources |

**Which Built-in Roles Include Which Actions:**

| Role | generateUserDelegationKey | listkeys | Data Plane Operations |
|------|---------------------------|----------|----------------------|
| **Owner** | ✅ | ✅ | ✅ (via other roles) |
| **Contributor** | ✅ | ✅ | ❌ (control plane only) |
| **Storage Account Contributor** | ✅ | ✅ | ❌ (control plane only) |
| **Storage Blob Data Owner** | ✅ | ❌ | ✅ Full |
| **Storage Blob Data Contributor** | ✅ | ❌ | ✅ Read/Write/Delete |
| **Storage Blob Data Reader** | ✅ | ❌ | ✅ Read only |
| **Storage Blob Delegator** | ✅ | ❌ | ❌ (delegation only) |
| **Reader** | ❌ | ❌ | ❌ |

### Assigning RBAC Roles

```bash
# Assign Storage Blob Data Contributor to a user
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee user@contoso.com \
    --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}

# Assign to a managed identity
az role assignment create \
    --role "Storage Blob Data Reader" \
    --assignee-object-id {managed-identity-object-id} \
    --assignee-principal-type ServicePrincipal \
    --scope /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Storage/storageAccounts/{storage-account}/blobServices/default/containers/{container}
```

### Using Managed Identity with User Delegation SAS

```csharp
// Application using managed identity
var credential = new ManagedIdentityCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://mystorageaccount.blob.core.windows.net"),
    credential
);

// The managed identity must have appropriate RBAC role assigned
// (e.g., Storage Blob Data Contributor)

// Create user delegation SAS
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    DateTimeOffset.UtcNow,
    DateTimeOffset.UtcNow.AddHours(1)
);

var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c",
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1)
};

sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);

var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
).ToString();
```

## Comparison: Authentication Methods

| Method | Security Level | Complexity | Revocation | RBAC | Use Case |
|--------|---------------|------------|------------|------|----------|
| **Account Keys** | Low | Low | Hard (key rotation) | No | Legacy, Dev/Test |
| **Account SAS** | Medium | Low | Hard | No | Multi-service access |
| **Service SAS** | Medium | Medium | Medium (with policy) | No | Single service |
| **Service SAS + Policy** | Medium | Medium | Easy | No | Managed single service |
| **User Delegation SAS** | High | Medium | Easy | Yes | Production, Modern apps |
| **Azure AD (Direct)** | High | Low | Easy | Yes | Service-to-service |

## Additional Security Features

### 1. Storage Account Firewall

Azure Storage firewall provides network-level security by restricting access to storage accounts based on network rules.

```bash
# Configure network rules
az storage account update \
    --name mystorageaccount \
    --resource-group myresourcegroup \
    --default-action Deny

# Allow specific IP addresses
az storage account network-rule add \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --ip-address 203.0.113.10
```

#### Storage Firewall Network Rule Types

Azure Storage firewalls support the following types of network rules:

| Rule Type | Description | Use Case |
|-----------|-------------|----------|
| **Virtual Network Rules** | Allow traffic from specific VNet subnets using service endpoints | Resources in your VNet that need storage access |
| **IP Rules** | Allow traffic from specific public IP addresses or ranges | On-premises systems or known external IP addresses |
| **Resource Instance Rules** | Allow traffic from specific Azure resource instances | Azure services that cannot use VNet or IP rules |
| **Trusted Service Exceptions** | Allow trusted Microsoft services to bypass firewall | Azure Backup, Azure Site Recovery, etc. |

#### Resource Instance Rules

**Resource instance rules** allow traffic from specific Azure resource instances that cannot be isolated through virtual network or IP address rules. This is the appropriate solution when Azure services need access to your storage account but cannot be configured with traditional network rules.

**When to Use Resource Instance Rules:**
- The Azure service cannot be deployed in a VNet
- The Azure service doesn't have a static public IP address
- The service cannot use service endpoints
- You need to grant access to a specific resource instance, not all resources of that type

**Example - Adding a Resource Instance Rule:**
```bash
# Allow a specific Azure resource instance to access storage
az storage account network-rule add \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --resource-id /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{resource-provider}/{resource-type}/{resource-name}
```

> **Exam Tip**: When an Azure service needs access to a storage account but cannot be included in virtual network or IP rules, **resource instance rules** are the correct solution. Don't confuse this with:
> - **Private endpoint rules** - Not a valid storage firewall rule type. Private endpoints create private connections but are separate from firewall rules.
> - **Service endpoint rules** - Part of virtual network rules and require the service to support service endpoints.
> - **Application rules** - Not a valid Azure Storage firewall rule type.

### 2. Private Endpoints

- Connect to storage account through private IP in your VNet
- Traffic stays on Microsoft backbone network
- Eliminates public internet exposure

### 3. Customer-Managed Keys (CMK)

- Encryption keys stored in Azure Key Vault
- Full control over key rotation and access
- Additional layer of security for data at rest

### 4. Immutable Storage

- WORM (Write Once, Read Many) capability
- Prevent deletion or modification
- Compliance requirements (SEC 17a-4, CFTC, FINRA)

### 5. Soft Delete

- Recover accidentally deleted blobs and containers
- Retention period configurable (1-365 days)
- Protection against accidental data loss

### 6. Azure Storage Encryption Options

Azure Storage automatically encrypts all data at rest using 256-bit AES encryption. However, different encryption options provide varying levels of control and isolation.

#### Encryption Options Comparison

| Encryption Option | Scope | Key Management | Use Case |
|-------------------|-------|----------------|----------|
| **Storage Account Encryption Key** | Entire storage account | Microsoft-managed or customer-managed | Default encryption for all data |
| **Infrastructure Encryption** | Storage account (double encryption) | Microsoft-managed | Compliance requiring double encryption |
| **Encryption Scopes** | Container or blob level | Microsoft-managed or customer-managed per scope | **Multi-tenant data isolation** ✅ |
| **Customer-Provided Keys** | Per-request (Blob only) | Customer provides key with each request | Temporary operations |

#### Storage Account Encryption Key

- **Description**: Default encryption applied to the entire storage account
- **Characteristics**:
  - Single key scope for all data in the account
  - Can use Microsoft-managed keys or customer-managed keys (CMK)
  - Cannot provide different encryption keys for different customers' data
- **Limitation**: ❌ Not suitable when different customers need different encryption keys within the same account

#### Infrastructure Encryption

- **Description**: Provides double encryption at both the service and infrastructure levels
- **Characteristics**:
  - Two layers of encryption with two different encryption algorithms
  - Provides defense against compromise of one encryption algorithm
  - Uses the same key scope as the storage account
- **Limitation**: ❌ Does not allow different keys per customer - same key scope as storage account

#### Encryption Scopes ✅ (Best for Multi-Tenant Isolation)

- **Description**: Enable encryption with a key scoped to a container or an individual blob
- **Characteristics**:
  - Create secure boundaries between data in the same storage account
  - Each scope can use a different encryption key
  - Perfect for multi-tenant scenarios where different customers need different keys
  - Can be Microsoft-managed or customer-managed (Azure Key Vault)
- **Use Case**: **When you need different encryption keys for different customers' data within the same storage account**

**Example - Creating an Encryption Scope:**
```bash
# Create encryption scope with Microsoft-managed key
az storage account encryption-scope create \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --name customerAscope

# Create encryption scope with customer-managed key from Key Vault
az storage account encryption-scope create \
    --account-name mystorageaccount \
    --resource-group myresourcegroup \
    --name customerBscope \
    --key-source Microsoft.KeyVault \
    --key-uri "https://myvault.vault.azure.net/keys/mykey/version"
```

**Example - Creating a Container with Encryption Scope:**
```bash
# Create container with default encryption scope
az storage container create \
    --account-name mystorageaccount \
    --name customer-a-container \
    --default-encryption-scope customerAscope \
    --prevent-encryption-scope-override true
```

#### Customer-Provided Keys

- **Description**: Provide encryption key on each Blob Storage request
- **Characteristics**:
  - Key provided per-request in the request header
  - Only works with Blob Storage operations
  - Key not stored in Azure - must be provided with every request
- **Limitation**: ❌ Doesn't provide persistent encryption boundaries between different customers' data

### Exam Question: Multi-Tenant Encryption

**Question**: You have an Azure Storage account that contains sensitive data from multiple customers. You need to implement encryption with different keys for each customer's data within the same storage account. What should you use?

**Options:**
- A. Infrastructure encryption
- B. Storage account encryption key
- C. Customer-provided keys
- D. Encryption scopes

**Correct Answer: D. Encryption scopes**

**Explanation:**
- **Encryption scopes** enable you to manage encryption with a key that is scoped to a container or an individual blob, allowing you to create secure boundaries between data that resides in the same storage account but belongs to different customers.
- **Infrastructure encryption** provides double encryption at the service and infrastructure levels but uses the same key scope as the storage account, not allowing different keys per customer.
- **Storage account encryption key** applies to the entire storage account and cannot provide different encryption keys for different customers' data within the same account.
- **Customer-provided keys** are provided per-request for Blob Storage operations but don't provide persistent encryption boundaries between different customers' data in the storage account.

## Troubleshooting SAS Issues

### Common Errors and Solutions

#### 1. "AuthenticationFailed: Server failed to authenticate the request"

**Causes:**
- SAS token expired
- Invalid signature (key regenerated)
- Clock skew between client and server

**Solutions:**
```csharp
// Add clock skew tolerance
sasBuilder.StartsOn = DateTimeOffset.UtcNow.AddMinutes(-5);
sasBuilder.ExpiresOn = DateTimeOffset.UtcNow.AddHours(1);
```

#### 2. "AuthorizationPermissionMismatch"

**Causes:**
- User Delegation SAS: User lacks RBAC permissions
- Attempting operation not allowed by SAS permissions

**Solutions:**
- Verify RBAC role assignment
- Check SAS permissions match required operations

#### 3. "ResourceNotFound"

**Causes:**
- Container or blob doesn't exist
- SAS scoped to wrong resource

**Solutions:**
- Verify resource exists
- Check SAS resource type (blob vs container)

### Testing SAS Tokens

```csharp
// Test SAS token
public async Task<bool> TestSasTokenAsync(string sasUri)
{
    try
    {
        var containerClient = new BlobContainerClient(new Uri(sasUri));
        await containerClient.GetPropertiesAsync();
        return true;
    }
    catch (Azure.RequestFailedException ex)
    {
        Console.WriteLine($"SAS test failed: {ex.Status} - {ex.ErrorCode}");
        return false;
    }
}
```

## Quick Reference: When to Use Each SAS Type

### Use User Delegation SAS When:
✅ Security is paramount  
✅ Need RBAC integration  
✅ Want to avoid exposing storage keys  
✅ Production environments  
✅ Compliance requirements  
⚠️ **Working with Blob Storage ONLY** (not supported for File, Queue, or Table)

### Use Service SAS When:
✅ Single service access is sufficient  
✅ Need stored access policy for revocation  
✅ Legacy systems don't support Entra ID  
✅ Simple temporary access scenarios  

### Use Account SAS When:
✅ Need to access multiple services  
✅ Require account-level operations  
✅ Internal systems with key management  
✅ Backward compatibility required  

### Use Stored Access Policy When:
✅ Need to manage multiple Service SAS tokens  
✅ Want centralized permission control  
✅ Need easy revocation without key rotation  
✅ Using Service SAS (doesn't work with others)  

## References

- [Grant limited access with SAS](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
- [Create a user delegation SAS](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-dotnet)
- [Create a service SAS](https://learn.microsoft.com/en-us/azure/storage/blobs/sas-service-create-dotnet)
- [Create an account SAS](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-sas-create-dotnet)
- [Authorize with Azure AD](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory)
- [Secure your Azure Storage account](https://learn.microsoft.com/en-us/training/modules/secure-azure-storage-account/)
