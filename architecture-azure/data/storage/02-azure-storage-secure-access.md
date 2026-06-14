---
type: Azure Service
title: "Secure Access to Azure Storage"
description: "Azure Storage provides multiple layers of security to protect your data and control access. This document covers authentication methods, authorization mechanisms, and Shared Access Signatures (SAS)..."
tags: [data]
timestamp: 2026-06-14T00:00:00Z
---

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
  - [Question 5: Identity-Based Connection Settings for User-Assigned Managed Identity](#question-5-identity-based-connection-settings-for-user-assigned-managed-identity)
  - [Question 6: Time-Limited Blob Access for Finance Department](#question-6-time-limited-blob-access-for-finance-department)
  - [Question 7: Maximum Security Access Authorization for Blob Storage](#question-7-maximum-security-access-authorization-for-blob-storage)
  - [Question 8: Maximum Security Access Authorization for File Shares](#question-8-maximum-security-access-authorization-for-file-shares)
  - [Question 9: Stored Access Policies and Immutable Storage Limits](#question-9-stored-access-policies-and-immutable-storage-limits)
  - [Question 10: SAS Settings for Enumerate and Download Blobs](#question-10-sas-settings-for-enumerate-and-download-blobs)
  - [Question 11: Configuring Read-Only Container Access with HTTP/HTTPS Support](#question-11-configuring-read-only-container-access-with-httphttps-support)
- [SAS Security Best Practices](#sas-security-best-practices)
- [RBAC Roles for Storage Access](#rbac-roles-for-storage-access)
  - [Common Built-in Roles](#common-built-in-roles)
  - [Common Azure Storage RBAC Actions Reference](#common-azure-storage-rbac-actions-reference)
  - [Assigning RBAC Roles](#assigning-rbac-roles)
  - [Using Managed Identity with User Delegation SAS](#using-managed-identity-with-user-delegation-sas)
- [Attribute-Based Access Control (ABAC)](#attribute-based-access-control-abac)
  - [What is ABAC?](#what-is-abac)
  - [ABAC vs Other Access Control Methods](#abac-vs-other-access-control-methods)
  - [Role Assignment Conditions](#role-assignment-conditions)
  - [Storage Services Supporting RBAC Conditions](#storage-services-supporting-rbac-conditions)
  - [ABAC Use Cases for Storage](#abac-use-cases-for-storage)
  - [Exam Question: ABAC for Tag-Based Access](#exam-question-abac-for-tag-based-access)
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

### Question 5: Identity-Based Connection Settings for User-Assigned Managed Identity

**Scenario:**
You have an Azure App Service that needs to access blob storage using a user-assigned managed identity.

**Question:**
Which properties must you configure in the identity-based connection settings?

**Options:**
1. `managedIdentityType` and `objectID`
2. `credential` and `resourceID`
3. `principalID` and `tenantID`
4. `credential` and `clientID` ✅

**Correct Answer: `credential` and `clientID`**

**Detailed Analysis:**

#### Why `credential` and `clientID` is CORRECT ✅

**Key Points:**
- ✅ **credential**: Required to indicate that managed identity authentication should be used
- ✅ **clientID**: Required to identify which specific user-assigned managed identity to use
- ✅ **Azure Functions/App Service**: These are the correct properties for identity-based connections in Azure Functions bindings and App Service configurations

**Configuration Example (host.json or app settings):**
```json
{
  "AzureWebJobsStorage__accountName": "mystorageaccount",
  "AzureWebJobsStorage__credential": "managedidentity",
  "AzureWebJobsStorage__clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**Why These Properties:**
- `credential`: Tells the Azure SDK to use managed identity instead of connection strings or keys
- `clientID`: Uniquely identifies the user-assigned managed identity (required because a resource can have multiple user-assigned identities)

#### Why `managedIdentityType` and `objectID` is INCORRECT ❌

**Key Points:**
- ❌ **Not Valid Properties**: These are not valid properties for configuring identity-based connections in Azure Storage SDK or Azure Functions bindings
- ❌ **objectID**: While object ID identifies an identity in Entra ID, it's not used in connection settings

#### Why `credential` and `resourceID` is INCORRECT ❌

**Key Points:**
- ❌ **resourceID Not Supported**: While `credential` is required, `resourceID` is not a supported property for configuring user-assigned managed identities in identity-based connections for blob storage
- ⚠️ The correct identifier for user-assigned managed identity is `clientID`, not `resourceID`

#### Why `principalID` and `tenantID` is INCORRECT ❌

**Key Points:**
- ❌ **Identity Properties, Not Connection Properties**: `principalID` and `tenantID` are properties that identify a managed identity in Entra ID, but they are not the correct properties for configuring identity-based connections
- ❌ **Not Used in Bindings**: Azure Functions and App Service bindings don't use these properties for connection configuration

**System-Assigned vs User-Assigned Managed Identity Configuration:**

| Identity Type | credential | clientID Required? |
|--------------|------------|-------------------|
| **System-Assigned** | `managedidentity` | ❌ No (uses the single system identity) |
| **User-Assigned** | `managedidentity` | ✅ Yes (identifies which identity to use) |

**Example: Azure Function Blob Trigger with User-Assigned Managed Identity:**
```csharp
// Function.cs
[FunctionName("ProcessBlob")]
public static void Run(
    [BlobTrigger("samples-workitems/{name}", 
        Connection = "MyStorageConnection")] 
    Stream myBlob,
    string name,
    ILogger log)
{
    log.LogInformation($"Processing blob: {name}");
}
```

```json
// local.settings.json or App Settings
{
  "MyStorageConnection__accountName": "mystorageaccount",
  "MyStorageConnection__credential": "managedidentity",
  "MyStorageConnection__clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**Key Takeaway:**
When using a **user-assigned managed identity** for blob storage access in Azure App Service or Azure Functions:
1. Set `credential` to `managedidentity` to enable identity-based authentication
2. Set `clientID` to the client ID of the specific user-assigned managed identity to use

**Domain:** Develop for Azure storage

### Question 6: Time-Limited Blob Access for Finance Department

**Scenario:**
You have an Azure subscription. The subscription has a blob container that contains multiple blobs. Ten users in the finance department of your company plan to access the blobs during the month of April. You need to recommend a solution to enable access to the blobs during the month of April only.

**Question:**
Which security solution should you include in the recommendation?

**Options:**
1. Conditional Access policies
2. Shared access signatures (SAS) ✅
3. Access keys
4. Certificates

**Correct Answer: Shared access signatures (SAS)**

**Detailed Analysis:**

#### Why Shared Access Signatures (SAS) is CORRECT ✅

**Key Points:**
- ✅ **Time-Limited Access**: SAS allows you to grant limited access to Azure Blob Storage resources for a **specific time window**—in this case, during the month of April
- ✅ **Configurable Permissions**: With SAS, you can configure permissions (e.g., read, write), scope (specific containers or blobs), and **start and expiry times**
- ✅ **Secure and Flexible**: Provides a secure and flexible way to allow temporary access **without exposing storage account access keys**
- ✅ **Granular Control**: Each user can receive their own SAS token with appropriate permissions

**Implementation for April-Only Access:**
```csharp
// Create SAS for April 2025 only
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "finance-data",
    Resource = "c", // Container level
    StartsOn = new DateTimeOffset(2025, 4, 1, 0, 0, 0, TimeSpan.Zero),  // April 1st start
    ExpiresOn = new DateTimeOffset(2025, 4, 30, 23, 59, 59, TimeSpan.Zero), // April 30th end
    Protocol = SasProtocol.Https
};

// Set read and list permissions for finance users
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read | BlobContainerSasPermissions.List);

// Generate SAS token
var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();

// Distribute this SAS URI to finance department users
var sasUri = $"https://{accountName}.blob.core.windows.net/finance-data?{sasToken}";
```

**SAS Benefits for This Scenario:**

| Requirement | SAS Capability |
|-------------|----------------|
| **Time Window (April only)** | ✅ Start and expiry times can be set precisely |
| **Multiple Users (10 users)** | ✅ Same SAS can be shared or individual SAS can be created |
| **Secure Access** | ✅ No need to share storage account keys |
| **Automatic Expiration** | ✅ Access automatically revoked after April 30th |

#### Why Conditional Access Policies is INCORRECT ❌

**Key Points:**
- ❌ **Different Purpose**: Conditional Access policies apply to **user sign-in conditions in Microsoft Entra ID**
- ❌ **Not for Storage Access Control**: They are not used for Azure Storage access control
- ❌ **Cannot Restrict Blob Access**: They cannot restrict blob access based on time windows for shared data
- ⚠️ **Scope**: Conditional Access controls authentication to Azure services, not authorization to storage data

**What Conditional Access Does:**
- Controls who can access Azure resources based on conditions (location, device, risk level)
- Requires MFA based on conditions
- Blocks or grants access to applications
- Does NOT control access to blob storage data

#### Why Access Keys is INCORRECT ❌

**Key Points:**
- ❌ **Full Access**: Access keys grant **full access** to the entire storage account
- ❌ **No Granular Control**: They do not provide granular or **time-limited access**
- ❌ **Security Risk**: Sharing access keys is **less secure** and not recommended for temporary user access
- ❌ **No Expiration**: Keys don't expire automatically—must be manually regenerated

**Security Risks of Using Access Keys:**
```csharp
// ❌ BAD: Access keys grant full account access
var accountKey = "abc123..."; // Anyone with this key has FULL access

// Problems:
// 1. No time limitation - key works indefinitely
// 2. No permission scoping - full read/write/delete access
// 3. Sharing risk - if leaked, entire account is compromised
// 4. No audit trail for individual users
```

#### Why Certificates is INCORRECT ❌

**Key Points:**
- ❌ **Different Use Case**: Certificates are typically used for **client authentication in application or API scenarios**
- ❌ **Not for Temporary Access**: Not designed for temporary or granular access to Azure Storage resources
- ❌ **Complex Management**: Certificate management adds unnecessary complexity for this simple time-limited access requirement
- ❌ **No Built-in Time Limits**: Certificates don't inherently support time-window access control for blob storage

**Comparison Table:**

| Solution | Time-Limited Access | Granular Permissions | Blob Storage Support | Recommended |
|----------|---------------------|---------------------|----------------------|-------------|
| **SAS** | ✅ Yes (start/expiry) | ✅ Yes | ✅ Native | ✅ **Yes** |
| **Conditional Access** | ⚠️ Sign-in only | ❌ No | ❌ No | ❌ No |
| **Access Keys** | ❌ No | ❌ No (full access) | ✅ Yes | ❌ No |
| **Certificates** | ❌ No | ❌ No | ⚠️ Limited | ❌ No |

### Key Takeaways

**Question Pattern:** "Need time-limited/temporary access to blob storage"

**Answer:** Use **Shared Access Signatures (SAS)** because:
1. 🕐 **Time Control**: Configure precise start and expiry times
2. 🔐 **Security**: Don't expose storage account keys
3. 📋 **Granular Permissions**: Specify exactly what operations are allowed
4. 🎯 **Scoped Access**: Limit to specific containers or blobs

**Domain:** Design data storage solutions

**References:**
- [Grant limited access to Azure Storage resources using shared access signatures (SAS)](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
- [Authorize access to data in Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-storage)
- [Delegate access with a shared access signature](https://learn.microsoft.com/en-us/rest/api/storageservices/delegate-access-with-shared-access-signature)
- [Manage storage account access keys](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage?tabs=azure-portal)

### Question 7: Maximum Security Access Authorization for Blob Storage

**Scenario:**
You have an Azure subscription. You plan to deploy five storage accounts that will store block blobs and five storage accounts that will host file shares. The file shares will be accessed by using the SMB protocol.

You need to recommend an access authorization solution for the storage accounts. The solution must meet the following requirements:
- Maximize security
- Prevent the use of shared keys
- Whenever possible, support time-limited access

**Question:**
What should you include in the solution for the blobs?

**Options:**
1. A user delegation shared access signature (SAS) only ✅
2. A shared access signature (SAS) and a stored access policy
3. A user delegation shared access signature (SAS) and a stored access policy

**Correct Answer: A user delegation shared access signature (SAS) only**

**Detailed Analysis:**

#### Why User Delegation SAS Only is CORRECT ✅

**Key Points:**
- ✅ **Maximizes Security**: User Delegation SAS is secured with Microsoft Entra ID credentials, not storage account keys
- ✅ **Prevents Shared Keys**: User Delegation SAS doesn't use storage account keys—it uses a user delegation key obtained via Entra ID authentication
- ✅ **Supports Time-Limited Access**: User Delegation SAS tokens have configurable start and expiry times (validity period can be defined)
- ✅ **Identity-Based Access**: Combines access permissions with Microsoft Entra identities, reducing risk associated with shared keys
- ✅ **Simple and Sufficient**: For the given requirements, User Delegation SAS alone provides everything needed

**Why This is the Best Choice:**
```
Requirement                    │ User Delegation SAS
───────────────────────────────┼─────────────────────
Maximize Security              │ ✅ Entra ID-backed (most secure SAS type)
Prevent Shared Keys            │ ✅ Uses user delegation key, NOT account keys
Support Time-Limited Access    │ ✅ Configurable start/expiry times
Blob Storage Support           │ ✅ Fully supported
```

**Implementation Example:**
```csharp
// Authenticate with Microsoft Entra ID (no storage keys needed)
var credential = new DefaultAzureCredential();
var blobServiceClient = new BlobServiceClient(
    new Uri("https://myaccount.blob.core.windows.net"),
    credential
);

// Get user delegation key (time-limited, from Entra ID)
var userDelegationKey = await blobServiceClient.GetUserDelegationKeyAsync(
    startsOn: DateTimeOffset.UtcNow,
    expiresOn: DateTimeOffset.UtcNow.AddHours(4)  // Time-limited!
);

// Create User Delegation SAS with time limits
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    Resource = "c",
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(4)  // Time-limited access
};
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);

// Generate SAS using user delegation key (NOT account key)
var sasToken = sasBuilder.ToSasQueryParameters(
    userDelegationKey.Value,
    blobServiceClient.AccountName
).ToString();
```

#### Why SAS and Stored Access Policy is INCORRECT ❌

**Key Points:**
- ❌ **Uses Shared Keys**: A standard SAS (Account or Service SAS) with stored access policy is signed using storage account keys
- ❌ **Doesn't Maximize Security**: Shared key-based SAS is less secure than User Delegation SAS
- ❌ **Violates Requirements**: The requirement explicitly states "prevent the use of shared keys"
- ⚠️ **Security Risk**: Combining SAS with stored access policy still relies on account keys for signing

**Why This is Problematic:**
```csharp
// ❌ Service SAS with stored access policy uses account key
var credential = new StorageSharedKeyCredential(accountName, accountKey); // Uses shared key!
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "mycontainer",
    Identifier = "my-policy"  // References stored policy, but STILL uses account key
};
var sasToken = sasBuilder.ToSasQueryParameters(credential);  // Signed with account key
```

#### Why User Delegation SAS and Stored Access Policy is INCORRECT ❌

**Key Points:**
- ❌ **Not Supported**: Stored access policies are **NOT supported for User Delegation SAS**
- ❌ **Invalid Combination**: You cannot associate a stored access policy with a User Delegation SAS
- ❌ **Unnecessary Complexity**: User Delegation SAS alone is simple and sufficient for the requirements
- ✅ **User Delegation SAS Already Has Time Limits**: The SAS token itself supports start/expiry times

**Technical Reason:**
```
┌─────────────────────────────┬───────────────────────────────┐
│ SAS Type                    │ Stored Access Policy Support  │
├─────────────────────────────┼───────────────────────────────┤
│ Account SAS                 │ ❌ Not supported              │
│ Service SAS                 │ ✅ Supported                  │
│ User Delegation SAS         │ ❌ NOT SUPPORTED              │
└─────────────────────────────┴───────────────────────────────┘
```

**Key Insight**: Stored access policies only work with **Service SAS**. Since User Delegation SAS inherently supports time-limited access through its token parameters, there's no need (and no capability) to use stored access policies with it.

### Comparison Table

| Solution | Maximize Security | Prevent Shared Keys | Time-Limited Access | Valid for Blobs |
|----------|-------------------|---------------------|---------------------|------------------|
| **User Delegation SAS only** | ✅ Most secure | ✅ Uses Entra ID | ✅ Built-in support | ✅ **Correct** |
| **SAS + Stored Access Policy** | ⚠️ Less secure | ❌ Uses account key | ✅ Via policy | ❌ Incorrect |
| **User Delegation SAS + Stored Access Policy** | ❌ Invalid | ✅ | ✅ | ❌ Not supported |

### Key Takeaways

**Question Pattern:** "Maximum security for blob storage + prevent shared keys + time-limited access"

**Answer:** Use **User Delegation SAS only** because:
1. 🔐 **Most Secure**: Backed by Microsoft Entra ID credentials
2. 🚫 **No Shared Keys**: Doesn't use storage account keys
3. 🕐 **Time-Limited**: Native support for start and expiry times
4. ✅ **Simple**: No need for stored access policy (which isn't supported anyway)

**Critical Points to Remember:**
- User Delegation SAS is the **only** SAS type that doesn't use storage account keys
- **Stored access policies do NOT work with User Delegation SAS**
- For blob storage with maximum security requirements, User Delegation SAS is always the answer

**Domain:** Design data storage solutions

**References:**
- [Create a user delegation SAS](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-dotnet)
- [Grant limited access to Azure Storage resources using SAS](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
- [Create a stored access policy](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy)

### Question 8: Maximum Security Access Authorization for File Shares

**Scenario:**
You have an Azure subscription. You plan to deploy five storage accounts that will store block blobs and five storage accounts that will host file shares. The file shares will be accessed by using the SMB protocol.

You need to recommend an access authorization solution for the storage accounts. The solution must meet the following requirements:
- Maximize security
- Prevent the use of shared keys
- Whenever possible, support time-limited access

**Question:**
What should you include in the solution for the file shares?

**Options:**
1. Microsoft Entra credentials ✅
2. A user delegation shared access signature (SAS) only
3. A user delegation shared access signature (SAS) and a stored access policy

**Correct Answer: Microsoft Entra credentials**

**Detailed Analysis:**

#### Why Microsoft Entra Credentials is CORRECT ✅

**Key Points:**
- ✅ **Maximizes Security**: Microsoft Entra ID provides identity-based authentication with strong security features
- ✅ **Prevents Shared Keys**: Entra ID credentials don't rely on storage account keys or shared keys
- ✅ **Enhanced Security Features**: Supports Multi-Factor Authentication (MFA) and conditional access policies
- ✅ **Identity-Centric Approach**: User-focused access management through Microsoft Entra identities
- ✅ **SMB Protocol Support**: Azure Files supports Microsoft Entra ID authentication over SMB

**Why This is the Best Choice for File Shares:**
```
Requirement                    │ Microsoft Entra Credentials
───────────────────────────────┼─────────────────────────────────
Maximize Security              │ ✅ Identity-based with MFA support
Prevent Shared Keys            │ ✅ No storage account keys needed
Support Time-Limited Access    │ ✅ Via conditional access policies
File Shares (SMB) Support      │ ✅ Fully supported
```

**Authentication Options for Azure Files with Entra ID:**
- **Azure AD Domain Services (Azure AD DS)**: For cloud-only scenarios
- **On-premises AD DS**: For hybrid scenarios with Azure AD Connect
- **Azure AD Kerberos**: For hybrid identities accessing Azure file shares

**Implementation Approach:**
```powershell
# Enable Azure AD DS authentication for Azure Files
az storage account update \
    --name mystorageaccount \
    --resource-group myResourceGroup \
    --enable-files-aadds true

# Or enable on-premises AD DS authentication
az storage account update \
    --name mystorageaccount \
    --resource-group myResourceGroup \
    --enable-files-adds true \
    --domain-name "contoso.com" \
    --net-bios-domain-name "CONTOSO" \
    --forest-name "contoso.com" \
    --domain-guid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
    --domain-sid "S-1-5-21-xxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxx" \
    --azure-storage-sid "S-1-5-21-xxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxx-xxxxx"
```

**Security Benefits:**
- 🔐 **Strong Authentication**: Leverages Entra ID's robust authentication mechanisms
- 🛡️ **Conditional Access**: Apply policies based on user, device, location, and risk
- 📊 **Audit Logging**: Complete audit trail through Entra ID
- 🔑 **No Key Management**: Eliminates the risk of exposed storage keys

#### Why User Delegation SAS Only is INCORRECT ❌

**Critical Limitation:**
- ❌ **NOT SUPPORTED for File Storage**: User Delegation SAS is **ONLY supported for Blob Storage**
- ❌ **Cannot Use for File Shares**: Azure Files does not support User Delegation SAS
- ❌ **Wrong Service Type**: This option doesn't apply to file shares at all

**User Delegation SAS Service Support:**
```
┌─────────────────────┬─────────────────────────────┐
│ Storage Service     │ User Delegation SAS Support │
├─────────────────────┼─────────────────────────────┤
│ Blob Storage        │ ✅ Supported                │
│ File Storage        │ ❌ NOT SUPPORTED            │
│ Queue Storage       │ ❌ NOT SUPPORTED            │
│ Table Storage       │ ❌ NOT SUPPORTED            │
└─────────────────────┴─────────────────────────────┘
```

**Why This Matters:**
- User Delegation SAS was designed specifically for Blob Storage with Entra ID integration
- For File Shares, you must use either:
  - Microsoft Entra credentials (recommended for maximum security)
  - Service SAS with storage account key (less secure)
  - Storage account key directly (least secure)

#### Why User Delegation SAS and Stored Access Policy is INCORRECT ❌

**Multiple Issues:**
- ❌ **User Delegation SAS Not Supported for Files**: As explained above, User Delegation SAS only works with Blob Storage
- ❌ **Stored Access Policies Not Supported for User Delegation SAS**: Even for blobs, stored access policies cannot be combined with User Delegation SAS
- ❌ **Double Invalid Combination**: This option is invalid on two counts

**Technical Reason:**
```
┌─────────────────────────────┬───────────────────────────────┐
│ SAS Type                    │ Stored Access Policy Support  │
├─────────────────────────────┼───────────────────────────────┤
│ Account SAS                 │ ❌ Not supported              │
│ Service SAS                 │ ✅ Supported                  │
│ User Delegation SAS         │ ❌ NOT SUPPORTED              │
└─────────────────────────────┴───────────────────────────────┘
```

### Comparison: Blob Storage vs File Shares Access Authorization

This question and Question 7 together illustrate a critical distinction:

| Requirement | Blob Storage Solution | File Shares Solution |
|-------------|----------------------|---------------------|
| **Maximize Security** | User Delegation SAS | Microsoft Entra credentials |
| **Prevent Shared Keys** | ✅ User Delegation SAS | ✅ Entra ID |
| **Time-Limited Access** | ✅ SAS expiry times | ✅ Conditional access policies |
| **Why Different?** | User Delegation SAS supported | User Delegation SAS **NOT** supported |

**Key Insight**: The same security requirements lead to **different solutions** depending on the storage service:
- **Blobs** → User Delegation SAS (most secure SAS type, Entra ID-backed)
- **File Shares** → Microsoft Entra credentials directly (User Delegation SAS not available)

### Key Takeaways

**Question Pattern:** "Maximum security for file shares + prevent shared keys + time-limited access"

**Answer:** Use **Microsoft Entra credentials** because:
1. 🔐 **Identity-Based Security**: Strong authentication through Entra ID
2. 🚫 **No Shared Keys**: Eliminates storage account key exposure
3. 🛡️ **Enhanced Features**: MFA, conditional access, and audit logging
4. ⚠️ **User Delegation SAS Not Available**: Cannot use for File Storage

**Critical Points to Remember:**
- User Delegation SAS is **ONLY supported for Blob Storage**
- For File Shares with maximum security, use Microsoft Entra credentials
- Stored access policies do NOT work with User Delegation SAS (even for blobs)
- Azure Files supports Entra ID authentication over SMB protocol

**Domain:** Design data storage solutions

**References:**
- [Define stored access policy](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy)
- [Create user delegation SAS](https://learn.microsoft.com/en-us/rest/api/storageservices/create-user-delegation-sas)
- [Overview of Azure Files identity-based authentication](https://learn.microsoft.com/en-us/azure/storage/files/storage-files-active-directory-overview)

---

### Question 9: Stored Access Policies and Immutable Storage Limits

**Scenario:**
You manage an Azure subscription with a storage account named **storage1**.

**Planned Changes:**
In storage1, you plan to create a new container named **cont2** that has the following access policies:
- Three stored access policies named Stored1, Stored2, and Stored3
- A legal hold for immutable blob storage
- Whenever possible, use directories to organize storage account content

**Question:**
What is the maximum number of additional access policies you can create for cont2?

**Answer Options:**

**Stored access policies:** [Dropdown: 0, 1, 2, 3, 4, 5]  
**Immutable blob storage policies:** [Dropdown: 0, 1, 2, 3, 4, 5]

---

**Correct Answers:**
- **Stored access policies:** 2
- **Immutable blob storage policies:** 0

---

### Explanation

#### Stored Access Policies: 2 Additional Policies

**Azure Limit**: A blob container can have a **maximum of 5 stored access policies**.

**Calculation**:
- Maximum allowed: 5 policies
- Already planned: 3 policies (Stored1, Stored2, Stored3)
- Additional policies possible: 5 - 3 = **2**

**Key Points**:
- ✅ Stored access policies are used with **Service SAS** tokens
- ✅ Maximum **5 policies per container**
- ✅ Policies are defined at the **container level** for blob storage
- ✅ Each policy can have different permissions and expiry times
- ✅ Useful for centralized SAS management and revocation

**What Are Stored Access Policies?**

Stored access policies provide an additional level of control over Service SAS tokens:
- Allow modification of SAS permissions without regenerating tokens
- Enable revocation by deleting the policy
- Centralize permission management for multiple SAS tokens
- Must be created at container level for blob storage

**Example**:
```bash
# Azure CLI - Create stored access policy
az storage container policy create \
    --account-name storage1 \
    --container-name cont2 \
    --name Stored4 \
    --permissions rl \
    --expiry 2026-12-31

# Now you have: Stored1, Stored2, Stored3, Stored4
# Remaining capacity: 1 more policy (5 max - 4 current = 1)
```

**Why the Limit?**
- Azure enforces a **maximum of 5 stored access policies** per container to:
  - Maintain performance
  - Limit metadata size
  - Encourage best practices (avoid excessive policy proliferation)

#### Immutable Blob Storage Policies: 0 Additional Policies

**Azure Configuration**: Once a legal hold is set on a container, **no additional time-based retention policies** can be created at the same time.

**Key Concepts**:

**1. Legal Hold (Already Planned)**
- A legal hold makes blobs immutable until explicitly cleared
- **No retention duration required**
- Perfect for legal proceedings or investigations
- Can have multiple legal holds with different tags

**2. Time-Based Retention Policy**
- A container can have **only ONE time-based retention policy** active
- Specifies a retention duration (e.g., 7 years)
- Can be locked or unlocked
- After retention expires, blobs can be deleted but not modified

**Why 0 Additional Policies?**

The planned configuration includes:
- ✅ **Legal hold** for immutable blob storage (already configured)
- ❌ **Time-based retention policy**: Only **1 allowed per container**

Since the question asks about **immutable blob storage policies** (time-based retention policies), and Azure limits containers to **1 time-based retention policy**, you can add:
- If no time-based retention policy exists: 1 additional policy
- If a time-based retention policy exists: 0 additional policies

However, in this scenario, with a legal hold configured, the most conservative interpretation is that no additional time-based retention policies can be added, giving us **0**.

**Important Distinction**:
| Feature | What It Is | Limit per Container |
|---------|------------|---------------------|
| **Legal Hold** | Immutable storage without fixed duration | Multiple (with different tags) |
| **Time-Based Retention Policy** | Immutable storage with fixed duration | **1 maximum** |
| **Stored Access Policy** | SAS token management policy | **5 maximum** |

**Legal Hold vs Time-Based Retention**:
```
┌─────────────────────────────────────────────────────┐
│ Container: cont2                                    │
├─────────────────────────────────────────────────────┤
│ Legal Hold: ✅ Set (for legal proceedings)          │
│ Time-Based Retention: Can add 1 policy (if needed)  │
│   BUT if legal hold is active, typically you        │
│   would NOT add time-based retention (0 additional) │
└─────────────────────────────────────────────────────┘
```

**Practical Scenario**:
- Legal hold is active → Data is already immutable
- Adding a time-based retention policy would be redundant
- Typically, you use **either** legal hold **or** time-based retention, not both
- In exam context: **0 additional immutable blob storage policies**

### Summary Table

| Policy Type | Maximum per Container | Already Planned | Additional Possible |
|-------------|----------------------|-----------------|---------------------|
| **Stored Access Policies** | 5 | 3 (Stored1, Stored2, Stored3) | **2** |
| **Immutable Blob Storage Policies** | 1 time-based retention | 0 (legal hold only) | **0** |

### Key Takeaways

1. **Stored Access Policies**:
   - Maximum of **5 per container**
   - Used for Service SAS management
   - Defined at container level for blobs

2. **Immutable Storage Policies**:
   - **Legal holds**: Multiple allowed (with tags)
   - **Time-based retention**: Only **1 per container**
   - Legal hold + time-based retention can coexist, but typically use one or the other

3. **Container Limits**:
   - Plan carefully as you approach the 5-policy limit for stored access
   - Consider consolidating policies if approaching limits
   - Legal holds and time-based retention serve different purposes

4. **Best Practices**:
   - Use stored access policies to manage multiple SAS tokens efficiently
   - Use legal holds when retention duration is unknown
   - Use time-based retention for compliance with known duration requirements

**Domain:** Design data storage solutions

**References:**
- [Stored access policies](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy)
- [Immutable storage for blobs](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
- [Legal hold policy](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-legal-hold-overview)

---

### Question 10: SAS Settings for Enumerate and Download Blobs

**Scenario:**
You have an Azure subscription that contains a storage account named **storage1**. The storage1 account contains blobs in a container named **container1**.

You plan to share access to storage1.

You need to generate a shared access signature (SAS). The solution must meet the following requirements:
- Ensure that the SAS can only be used to **enumerate** and **download** blobs stored in container1
- Use the **principle of least privilege**

**Question:**
Which three settings should you enable?

**Answer Options:**

**Allowed services:** ☑️ Blob ☐ File ☐ Queue ☐ Table

**Allowed resource types:** ☐ Service ☐ Container ☐ Object

**Allowed permissions:** ☐ Read ☐ Write ☐ Delete ☐ List ☐ Add ☐ Create ☐ Update ☐ Process ☐ Immutable storage ☐ Permanent delete

**Blob versioning permissions:** ☐ Enables deletion of versions

**Allowed blob index permissions:** ☐ Read/Write ☐ Filter

---

**Correct Answers:**
- **Allowed resource types:** Container ✅
- **Allowed permissions:** Read ✅
- **Allowed permissions:** List ✅

---

### Explanation

#### Allowed Resource Types: Container ✅ **CORRECT**

**Why This Is Correct:**
- **Container** resource type grants access to the content and metadata of any blob in the container, AND to the list of blobs in the container
- This is the appropriate scope for enumerating blobs in a specific container
- Specifying **Object** additionally would be redundant because it is a subset of **Container**

**Key Points:**
- ✅ Container provides access to blob content (download)
- ✅ Container provides access to list blobs (enumerate)
- ✅ Container is the correct scope for container-level operations

**Resource Type Hierarchy:**
```
┌─────────────────────────────────────────────────────────────┐
│ Service                                                      │
│   - Account-level operations (list containers, etc.)        │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Container                                            │   │
│   │   - List blobs in container ✅                       │   │
│   │   - Access blob content and metadata ✅              │   │
│   │                                                      │   │
│   │   ┌──────────────────────────────────────────────┐   │   │
│   │   │ Object                                        │   │   │
│   │   │   - Individual blob operations                │   │   │
│   │   │   - Subset of Container (redundant here)      │   │   │
│   │   └──────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### Why NOT Service ❌

- **Service** provides account-level operations like listing containers
- Not required for accessing blobs within a specific container
- Violates principle of least privilege (too broad)

#### Why NOT Object (Alone) ❌

- **Object** grants access to individual blob operations only
- Does NOT include the ability to list blobs in the container
- Would not satisfy the "enumerate" requirement

**Note:** Selecting **Object** in addition to **Container** would be redundant, not incorrect per se, but violates the principle of least privilege by being overly explicit.

---

#### Allowed Permissions: Read ✅ **CORRECT**

**Why This Is Correct:**
- **Read** permission allows reading the content, blocklist, properties, and metadata of any blob in the container
- This is required to **download** blobs
- Use a blob as the source of a copy operation

**What Read Permission Grants:**
| Operation | Allowed |
|-----------|--------|
| Read blob content | ✅ Yes |
| Read blob properties | ✅ Yes |
| Read blob metadata | ✅ Yes |
| Read blob blocklist | ✅ Yes |
| Get blob (download) | ✅ Yes |
| Source of copy | ✅ Yes |

**Implementation:**
```csharp
// Read permission for downloading blobs
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);
```

---

#### Allowed Permissions: List ✅ **CORRECT**

**Why This Is Correct:**
- **List** permission allows listing blobs in the container (non-recursively)
- This is required to **enumerate** blobs in the container
- Essential for discovering what blobs exist before downloading them

**What List Permission Grants:**
| Operation | Allowed |
|-----------|--------|
| List blobs in container | ✅ Yes |
| Enumerate blob names | ✅ Yes |
| Get container metadata | ✅ Yes (with Read) |

**Implementation:**
```csharp
// List permission for enumerating blobs
sasBuilder.SetPermissions(BlobContainerSasPermissions.List);
```

**Combined Implementation:**
```csharp
// Minimal permissions for enumerate and download
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c", // Container resource type
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(1),
    Protocol = SasProtocol.Https
};

// Read + List = Enumerate and Download
sasBuilder.SetPermissions(
    BlobContainerSasPermissions.Read |   // ✅ Download blobs
    BlobContainerSasPermissions.List     // ✅ Enumerate blobs
);

var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
var sasUri = $"https://storage1.blob.core.windows.net/container1?{sasToken}";
```

---

### Why Other Permissions Are INCORRECT ❌

| Permission | Why Incorrect |
|------------|---------------|
| **Write** | Creates/overwrites blobs - not needed for download/enumerate |
| **Delete** | Deletes blobs - not needed for download/enumerate |
| **Add** | Adds blocks to append blobs - not needed |
| **Create** | Creates new blobs - not needed |
| **Update** | Updates blob metadata - not needed |
| **Process** | Processes blob data - not needed |
| **Immutable storage** | Manages immutable policies - not needed |
| **Permanent delete** | Permanently deletes soft-deleted blobs - not needed |

---

### Principle of Least Privilege Application

**What We Need:**
1. ✅ **Enumerate blobs** → List permission
2. ✅ **Download blobs** → Read permission
3. ✅ **Container scope** → Container resource type

**What We Exclude:**
- ❌ Service resource type (too broad)
- ❌ Object resource type (redundant with Container)
- ❌ Write, Delete, Add, Create permissions (not required)
- ❌ File, Queue, Table services (not relevant to blob storage)

**Minimal SAS Configuration:**
```
┌─────────────────────────────────────────────────┐
│ SAS Configuration for Enumerate & Download      │
├─────────────────────────────────────────────────┤
│ Allowed Services:      Blob only ✅             │
│ Allowed Resource Type: Container ✅             │
│ Allowed Permissions:   Read + List ✅           │
│                                                 │
│ Everything else:       ❌ Not selected          │
└─────────────────────────────────────────────────┘
```

---

### Key Takeaways

**Question Pattern:** "Minimum SAS settings for enumerate and download blobs"

**Answer:**
1. ✅ **Container** resource type (not Object, not Service)
2. ✅ **Read** permission (for downloading)
3. ✅ **List** permission (for enumerating)

**Remember:**
- 🎯 Container includes Object-level access (Object is redundant)
- 🎯 Read is required for downloading blob content
- 🎯 List is required for enumerating blobs in a container
- 🎯 Always apply the principle of least privilege

**Domain:** Design data storage solutions

**References:**
- [Create account SAS](https://learn.microsoft.com/en-us/rest/api/storageservices/create-account-sas)
- [Account SAS permissions](https://learn.microsoft.com/en-us/rest/api/storageservices/create-account-sas#specify-account-sas-permissions)
- [SAS resource types](https://learn.microsoft.com/en-us/rest/api/storageservices/create-account-sas#specify-the-signed-resource-types)

---

### Question 11: Configuring Read-Only Container Access with HTTP/HTTPS Support

**Scenario:**
You have an Azure subscription that contains a storage account named **storage1**. The storage1 account contains a container named **container1**.

You need to configure access to container1. The solution must meet the following requirements:
- Only allow **read access**
- Allow both **HTTP and HTTPS protocols**
- Apply access permissions to **all the content in the container**

**Question:**
What should you use?

**Options:**
1. Azure Content Delivery Network (CDN)
2. a shared access signature (SAS) ✅
3. access keys
4. an access policy

---

**Correct Answer: A Shared Access Signature (SAS)** ✅

---

### Explanation

#### Why Shared Access Signature (SAS) is CORRECT ✅

**A Shared Access Signature (SAS)** is the appropriate solution for the given requirements:

**1. Only Allow Read Access** ✅

SAS tokens allow you to specify precise permissions, such as **read-only access**, for the resources in the storage account.

```csharp
// Create SAS with read-only permissions
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c", // Container level
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(24)
};

// Set read-only permissions
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);

var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
```

**Available SAS Permissions for Blob Containers:**
| Permission | Symbol | Description |
|------------|--------|-------------|
| **Read** | r | Read blob content, properties, metadata ✅ |
| **Write** | w | Create or write blobs |
| **Delete** | d | Delete blobs |
| **List** | l | List blobs in container |
| **Add** | a | Add blocks to append blobs |
| **Create** | c | Create new blobs |

**Key Points:**
- ✅ SAS provides **granular permission control** at the operation level
- ✅ Can restrict to **read-only** access (no write, delete, or modify)
- ✅ Supports **time-limited access** for enhanced security
- ✅ Follows the **principle of least privilege**

---

**2. Allow Both HTTP and HTTPS Protocols** ✅

SAS tokens can be configured to support either **HTTPS only** or **both HTTP and HTTPS protocols**.

```csharp
// Option 1: HTTPS only (most secure)
sasBuilder.Protocol = SasProtocol.Https;

// Option 2: Both HTTP and HTTPS (meets requirement)
sasBuilder.Protocol = SasProtocol.HttpsAndHttp;
```

**Protocol Configuration Options:**
| Protocol Setting | HTTP Allowed | HTTPS Allowed | Use Case |
|-----------------|--------------|---------------|----------|
| `SasProtocol.Https` | ❌ No | ✅ Yes | Production (most secure) |
| `SasProtocol.HttpsAndHttp` | ✅ Yes | ✅ Yes | Legacy compatibility ✅ |

**Key Points:**
- ✅ SAS supports **protocol-level restrictions**
- ✅ Can allow **both HTTP and HTTPS** as required
- ⚠️ **Best practice**: Use HTTPS-only in production; HTTP support is typically for legacy systems

---

**3. Apply Access Permissions to All Content in the Container** ✅

A **container-level SAS** can be created to apply permissions to **all blobs within the container**.

```csharp
// Container-level SAS applies to all blobs in the container
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c", // ✅ "c" = Container (applies to all blobs)
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(24),
    Protocol = SasProtocol.HttpsAndHttp // Both HTTP and HTTPS
};

// Read-only access to all blobs
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read);

var credential = new StorageSharedKeyCredential(accountName, accountKey);
var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();

// SAS URI grants read access to entire container
var containerSasUri = $"https://storage1.blob.core.windows.net/container1?{sasToken}";
```

**SAS Resource Scopes:**
| Resource Type | Symbol | Scope | Use Case |
|---------------|--------|-------|----------|
| **Container** | c | All blobs in container ✅ | Apply permissions to entire container |
| **Blob** | b | Individual blob only | Single blob access |
| **Blob Version** | bv | Specific blob version | Versioned blob access |
| **Blob Snapshot** | bs | Specific blob snapshot | Snapshot access |

**Key Points:**
- ✅ Container-level SAS applies to **all current and future blobs** in the container
- ✅ No need to generate individual SAS tokens for each blob
- ✅ Simplifies access management for bulk content

---

#### Complete Implementation Example

```csharp
using Azure.Storage;
using Azure.Storage.Sas;
using Azure.Storage.Blobs;

// Storage account credentials
var accountName = "storage1";
var accountKey = "<storage-account-key>";
var containerName = "container1";

// Create SAS builder for container
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = containerName,
    Resource = "c", // Container-level access
    StartsOn = DateTimeOffset.UtcNow,
    ExpiresOn = DateTimeOffset.UtcNow.AddHours(24),
    Protocol = SasProtocol.HttpsAndHttp // ✅ Both HTTP and HTTPS
};

// Set read-only permissions
sasBuilder.SetPermissions(BlobContainerSasPermissions.Read); // ✅ Read access only

// Generate SAS token
var credential = new StorageSharedKeyCredential(accountName, accountKey);
var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();

// Construct container SAS URI
var containerSasUri = $"https://{accountName}.blob.core.windows.net/{containerName}?{sasToken}";

Console.WriteLine($"Container SAS URI: {containerSasUri}");

// Users can now access any blob in container1 with read-only access
// Example: https://storage1.blob.core.windows.net/container1/blob1.txt?sv=...
```

**Testing the SAS Token:**
```bash
# Download a blob using the SAS URI (HTTP)
curl "http://storage1.blob.core.windows.net/container1/myfile.txt?sv=2021-06-08&..."

# Download a blob using the SAS URI (HTTPS)
curl "https://storage1.blob.core.windows.net/container1/myfile.txt?sv=2021-06-08&..."

# Both will work because Protocol = HttpsAndHttp
```

---

#### Why Azure Content Delivery Network (CDN) is INCORRECT ❌

**Key Points:**
- ❌ **Purpose Mismatch**: Azure CDN is used for **delivering cached content** to users globally
- ❌ **No Direct Access Control**: CDN does **not configure access permissions** directly for a storage container
- ❌ **Layer of Abstraction**: CDN sits in front of storage, but doesn't replace access control mechanisms
- ⚠️ CDN can **use** SAS tokens for origin access, but is not itself an access control method

**What Azure CDN Actually Does:**
```
┌──────────┐     Caches content     ┌─────────────┐
│   User   │ ◄──────────────────── │  Azure CDN  │
└──────────┘                        └─────────────┘
                                           │
                                           │ Retrieves from origin
                                           │ (may use SAS for access)
                                           ▼
                                    ┌─────────────┐
                                    │  Storage    │
                                    │  Container  │
                                    └─────────────┘
```

**Why It Doesn't Meet Requirements:**
- ❌ CDN doesn't **configure permissions** on the container
- ❌ CDN doesn't **grant read access** - it caches content
- ❌ You would still need **SAS or another access method** for CDN to access the origin

**When to Use Azure CDN:**
- ✅ Reduce latency by caching content at edge locations
- ✅ Offload traffic from origin storage
- ✅ Global content distribution
- ✅ Static website acceleration

---

#### Why Access Keys are INCORRECT ❌

**Key Points:**
- ❌ **Too Broad**: Access keys grant **full control** over the entire storage account
- ❌ **Violates Least Privilege**: Cannot be scoped to read-only or single container
- ❌ **No Granular Control**: No way to restrict to specific permissions or protocols
- ❌ **Security Risk**: If compromised, attacker has complete storage account access

**What Access Keys Provide:**
```csharp
// Access keys grant FULL control - all operations, all services
var connectionString = $"DefaultEndpointsProtocol=https;AccountName=storage1;AccountKey={accountKey}";
var blobServiceClient = new BlobServiceClient(connectionString);

// Can do ANYTHING:
await blobServiceClient.DeleteBlobContainerAsync("container1"); // ✅ Can delete
await blobServiceClient.CreateBlobContainerAsync("newcontainer"); // ✅ Can create
// No way to restrict to read-only!
```

**Access Key Permissions:**
| Requirement | Access Keys | SAS |
|-------------|-------------|-----|
| Read-only access | ❌ Not possible | ✅ Yes |
| Container-specific | ❌ Not possible | ✅ Yes |
| Time-limited | ❌ Not possible | ✅ Yes |
| Protocol restriction | ❌ Not possible | ✅ Yes |
| Granular permissions | ❌ Not possible | ✅ Yes |

**Why They Don't Meet Requirements:**
- ❌ Cannot restrict to **read-only** access
- ❌ Cannot scope to **single container**
- ❌ Cannot limit to **specific protocols**
- ❌ Violates **principle of least privilege**

**When to Use Access Keys:**
- ⚠️ Legacy applications (with plans to migrate)
- ⚠️ Internal admin operations (with key rotation)
- ❌ **Never** for external access or least-privilege scenarios

---

#### Why Access Policy is INCORRECT ❌

**Key Points:**
- ❌ **Not a Standalone Solution**: Access policies (stored access policies) are used **in conjunction with SAS tokens**
- ❌ **Requires SAS**: They define access parameters, but require an **SAS token** for implementation
- ❌ **No Direct Control**: Access policies alone do **not grant access** - they're metadata for SAS

**What Access Policies Actually Are:**

Access policies (stored access policies) are **policy definitions** that can be associated with a **Service SAS** to provide:
- Centralized management of SAS permissions
- Ability to revoke SAS by deleting the policy
- Modification of SAS constraints without regenerating tokens

**Relationship Between Access Policy and SAS:**
```
┌─────────────────────┐
│  Access Policy      │  ◄── Defines permissions, expiry, etc.
│  (Stored Policy)    │      BUT does NOT grant access
└─────────────────────┘
          │
          │ Referenced by
          ▼
┌─────────────────────┐
│   Service SAS       │  ◄── Actually grants access
│   (SAS Token)       │      Uses policy parameters
└─────────────────────┘
```

**Implementation Example:**
```csharp
// Step 1: Create stored access policy (does NOT grant access yet)
var container = new BlobContainerClient(connectionString, "container1");

var policy = new BlobSignedIdentifier
{
    Id = "read-policy",
    AccessPolicy = new BlobAccessPolicy
    {
        PolicyStartsOn = DateTimeOffset.UtcNow,
        PolicyExpiresOn = DateTimeOffset.UtcNow.AddHours(24),
        Permissions = "r" // Read-only
    }
};

await container.SetAccessPolicyAsync(permissions: new[] { policy });

// Step 2: Create SAS that references the policy (THIS grants access)
var sasBuilder = new BlobSasBuilder
{
    BlobContainerName = "container1",
    Resource = "c",
    Identifier = "read-policy" // References the stored access policy
};

var sasToken = sasBuilder.ToSasQueryParameters(credential).ToString();
// ✅ Now users can access with this SAS token
```

**Why Access Policy Alone Doesn't Work:**
- ❌ Access policy is **metadata** stored on the container
- ❌ Does **not generate a token** or URI that users can use
- ❌ Requires **SAS token creation** to actually grant access
- ✅ Useful for **managing SAS tokens**, but not a replacement for them

**When to Use Stored Access Policies:**
- ✅ Centralized management of multiple SAS tokens
- ✅ Need to revoke SAS without regenerating keys
- ✅ Want to modify SAS expiry/permissions after creation
- ✅ **Always used WITH Service SAS**, not instead of it

---

### Comparison Table

| Solution | Read-Only | HTTP/HTTPS Support | Container-Scoped | Direct Access Control | Meets Requirements |
|----------|-----------|-------------------|------------------|----------------------|--------------------|
| **Shared Access Signature (SAS)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ **CORRECT** |
| **Azure CDN** | ❌ N/A | ✅ Yes | ❌ No | ❌ No | ❌ Incorrect |
| **Access Keys** | ❌ No | ✅ Yes | ❌ No | ❌ Full access only | ❌ Incorrect |
| **Access Policy** | ⚠️ With SAS | ⚠️ With SAS | ⚠️ With SAS | ❌ No (requires SAS) | ❌ Incorrect |

---

### Key Takeaways

**Question Pattern:** "Configure container access with specific permission, protocol, and scope requirements"

**Answer:** **Shared Access Signature (SAS)** ✅

**Why SAS is the Correct Choice:**
1. ✅ **Granular Permissions**: Can specify read-only access
2. ✅ **Protocol Control**: Supports HTTP, HTTPS, or both
3. ✅ **Container Scope**: Can apply to all content in a container
4. ✅ **Time-Limited**: Supports expiration for enhanced security
5. ✅ **Least Privilege**: Provides minimum necessary access

**Remember:**
- 🎯 **SAS** = Delegated access with granular control
- 🎯 **Access Keys** = Full account access (not granular)
- 🎯 **Access Policy** = SAS management tool (not standalone)
- 🎯 **CDN** = Content caching/delivery (not access control)

**Domain:** Design data storage solutions

**References:**
- [Grant limited access to Azure Storage resources using SAS](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)
- [Create a service SAS for a container or blob](https://learn.microsoft.com/en-us/azure/storage/blobs/sas-service-create)
- [Define a stored access policy](https://learn.microsoft.com/en-us/rest/api/storageservices/define-stored-access-policy)

---

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

## Attribute-Based Access Control (ABAC)

### What is ABAC?

**Attribute-Based Access Control (ABAC)** builds on Azure RBAC by adding role assignment conditions based on attributes (metadata) in the context of specific actions. ABAC allows you to grant access based on attributes associated with security principals, resources, requests, and the environment.

**Key Concept**: ABAC conditions work with entities that already have an RBAC assignment to a resource. The conditions add additional criteria that must be met before access is granted.

### ABAC vs Other Access Control Methods

| Method | Description | Use Case | Works with RBAC? |
|--------|-------------|----------|------------------|
| **RBAC** | Role-based permissions assigned to identities | General access control | Base layer |
| **ABAC** | Conditions added to RBAC assignments based on attributes | Fine-grained access based on tags or other metadata | ✅ Yes - extends RBAC |
| **ACLs** | POSIX-like access control lists | Azure Data Lake Storage Gen2 hierarchical namespace | ❌ Separate mechanism |
| **SAS** | Token-based delegated access | Temporary access to anyone with the token | ❌ Independent of RBAC |

### Role Assignment Conditions

ABAC role assignment conditions allow you to add "if-then" logic to your role assignments. For Azure Storage, you can create conditions based on:

**Resource Attributes:**
- **Blob index tags** - Tags assigned to individual blobs
- **Container name** - Name of the blob container
- **Blob path** - Path/name of the blob
- **Encryption scope** - Encryption scope of the blob

**Request Attributes:**
- **Blob index tags to set** - Tags being added during write operations
- **Version ID** - Blob version identifier

**Principal Attributes:**
- Custom security attributes assigned to users or service principals

**Example Condition:**
```
(
  (
    !(ActionMatches{'Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read'})
  )
  OR
  (
    @Resource[Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags:Project<$key_case_sensitive$>] StringEquals 'ProjectA'
  )
)
```

This condition allows read access only to blobs tagged with `Project=ProjectA`.

### Storage Services Supporting RBAC Conditions

Not all Azure Storage services support ABAC role assignment conditions. Understanding which services support conditions is critical for designing fine-grained access control solutions.

| Storage Service | Supports RBAC Conditions | Notes |
|-----------------|-------------------------|-------|
| **Blob Containers** (Blob Storage) | ✅ Yes | Full support for conditions based on blob tags, container names, paths, encryption scopes |
| **Queues** (Queue Storage) | ✅ Yes | Support for conditions on queue operations |
| **File Shares** (Azure Files) | ❌ No | Does not support conditions when assigning RBAC roles |
| **Tables** (Table Storage) | ❌ No | Does not support conditions when assigning RBAC roles |

**Key Takeaway:**
> When assigning RBAC roles with conditions to Azure Storage accounts, you can only apply conditions to **Blob Containers** and **Queues**. File shares and tables do not support role assignment conditions.

**Why This Matters:**
- **Design Implications**: If you need fine-grained, attribute-based access control, use Blob Storage or Queue Storage
- **Exam Scenarios**: Questions often test whether you know which services support conditions
- **Migration Considerations**: If moving from file shares to blob storage, you gain the ability to use ABAC conditions

**Example Scenario:**

**Question:** You have an Azure subscription that contains a storage account named storage1. You plan to use conditions when assigning role-based access control (RBAC) roles to storage1. Which storage1 services support conditions when assigning roles?

**Answer:** Containers and queues only

**Why:**
- ✅ **Blob Containers**: Support conditions for fine-grained access control based on tags, paths, and other attributes
- ✅ **Queues**: Support conditions for queue operations
- ❌ **File Shares**: Do not support conditions when assigning RBAC roles
- ❌ **Tables**: Do not support conditions when assigning RBAC roles

**Verification via Azure Portal:**
1. Navigate to your storage account
2. Go to **Access Control (IAM)** → **Add role assignment**
3. Select a role and assignee
4. Click on the **Conditions** tab
5. The condition editor will show supported attributes only for blob and queue operations

### ABAC Use Cases for Storage

| Scenario | ABAC Condition | Example |
|----------|----------------|----------|
| **Department-based access** | Blob tag matches user's department | Users in "Finance" can only read blobs tagged `Department=Finance` |
| **Project-based access** | Blob tag matches assigned project | Users can only access blobs for their assigned projects |
| **Classification-based access** | Blob tag matches security clearance | Users can only access blobs matching their clearance level |
| **Environment isolation** | Container name or path conditions | Dev team can only access `dev-*` containers |

**Configuring ABAC Conditions via Azure CLI:**
```bash
# Create a role assignment with an ABAC condition
az role assignment create \
    --role "Storage Blob Data Reader" \
    --assignee user@contoso.com \
    --scope "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage-account}" \
    --condition "@Resource[Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags:Project<\$key_case_sensitive\$>] StringEquals 'ProjectA'" \
    --condition-version "2.0"
```

**Configuring ABAC Conditions via Azure Portal:**
1. Navigate to the storage account
2. Go to **Access Control (IAM)**
3. Click **Add role assignment**
4. Select the role and assignee
5. Go to the **Conditions** tab
6. Click **Add condition** and use the visual editor or code editor

### Exam Question: ABAC for Tag-Based Access

**Question:**

You have 100 Azure Storage accounts.

Access to the accounts is restricted by using Azure role-based access control (Azure RBAC) assignments.

You need to recommend a solution that uses role assignment conditions based on the tags assigned to individual resources within the storage account.

What should you use to implement role assignment conditions?

- A. Access control lists (ACLs)
- B. Attribute-based access control (ABAC)
- C. Shared access signatures (SAS)

**Answer: B. Attribute-based access control (ABAC)**

**Explanation:**

| Option | Correct? | Reasoning |
|--------|----------|------------|
| **ABAC** | ✅ Yes | ABAC assignments work with the attributes (metadata) of an entity which already has an RBAC assignment. You can add an ABAC condition to an RBAC assignment and allow a certain user to access only those blobs which have a specific tag. This directly addresses the requirement for "role assignment conditions based on tags." |
| **ACLs** | ❌ No | Access Control Lists are used in Azure Data Lake Storage with hierarchical namespace enabled, implementing POSIX-like permissions. ACLs cannot be used with standard Azure Storage accounts without Data Lake Storage Gen2. |
| **SAS** | ❌ No | Shared Access Signatures provide delegated access to storage resources using tokens. SAS tokens work independently of RBAC assignments and grant access to anyone who possesses the token, regardless of their identity or RBAC role. |

**Key Takeaway:**
> When you need to add conditions to existing RBAC assignments based on resource attributes like tags, ABAC is the correct solution. It extends RBAC rather than replacing it.

**References:**
- [Azure RBAC Conditions Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-overview)
- [Azure Storage ABAC Conditions](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-auth-abac)
- [Azure Data Lake Storage Access Control](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control)
- [Azure Storage SAS Overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-sas-overview)

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
