# Secure Access to Azure Storage

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

### Question 1: Container Access with Entra ID and RBAC

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

### Key Takeaway

When the question asks for:
- **Microsoft Entra ID credentials** + **RBAC** + **Container access**
- **Answer**: User Delegation SAS (only option that supports Entra ID and RBAC)

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
