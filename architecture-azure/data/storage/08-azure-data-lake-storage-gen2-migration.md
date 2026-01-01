# Azure Data Lake Storage Gen2 - Migration and Data Transfer

## Table of Contents

- [Overview](#overview)
- [What is Azure Data Lake Storage Gen2?](#what-is-azure-data-lake-storage-gen2)
- [Storage Account Requirements for Data Lake Storage Gen2](#storage-account-requirements-for-data-lake-storage-gen2)
- [Migration Tools Comparison](#migration-tools-comparison)
  - [AzCopy](#azcopy)
  - [Azure File Sync](#azure-file-sync)
  - [Robocopy](#robocopy)
  - [Azure Storage Mover](#azure-storage-mover)
- [Migration Scenarios](#migration-scenarios)
  - [Scenario 1: Network-Attached Storage to Data Lake Storage Gen2](#scenario-1-network-attached-storage-to-data-lake-storage-gen2)
- [Practice Questions](#practice-questions)
- [Related Learning Resources](#related-learning-resources)

---

## Overview

Azure Data Lake Storage Gen2 is the result of converging the capabilities of Azure Data Lake Storage Gen1 with Azure Blob Storage. It provides a hierarchical file system optimized for big data analytics while maintaining all the benefits of Blob Storage, including cost-effective tiered storage, high availability, and strong consistency.

## What is Azure Data Lake Storage Gen2?

**Azure Data Lake Storage Gen2** is a set of capabilities built on Azure Blob Storage that enables big data analytics. It combines:

- **Hierarchical Namespace (HNS)**: Organizes objects into a hierarchy of directories and subdirectories
- **Blob Storage Features**: Cost-effective storage tiers, high availability, disaster recovery
- **Hadoop-Compatible Access**: Works with Apache Hadoop, Spark, and other analytics frameworks
- **Fine-Grained Security**: Directory and file-level access control with POSIX permissions

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Hierarchical Namespace** | Enabled on storage accounts to organize blobs into directories and subdirectories |
| **Performance** | Optimized for analytics workloads with high-throughput data processing |
| **Compatibility** | Works with Azure Blob Storage APIs and Azure Data Lake Storage Gen2 APIs |
| **Security** | Supports Azure RBAC and POSIX-like ACLs for fine-grained access control |

---

## Directory Organization in Azure Storage

Understanding how different Azure Storage types support directory organization is crucial for designing efficient content organization strategies.

### Directory Support Across Storage Types

| Storage Type | Hierarchical Namespace Required | True Directory Support | Organization Method |
|--------------|--------------------------------|------------------------|---------------------|
| **Blob Container (HNS Enabled)** | ✅ Yes | ✅ Yes | True directories with filesystem semantics |
| **Blob Container (HNS Disabled)** | ❌ No | ❌ No | Simulated directories using naming conventions (delimiters) |
| **Azure File Share** | N/A | ✅ Yes | Native directory support (SMB/NFS file system) |

### Blob Containers: Hierarchical Namespace Impact

#### With Hierarchical Namespace Enabled (Data Lake Storage Gen2)

When hierarchical namespace is enabled on a storage account, blob containers gain **true directory support**:

- **Real directories**: Directories are actual objects in the filesystem, not just naming conventions
- **Atomic operations**: Directory rename and delete operations are atomic
- **Performance**: More efficient directory operations (list, rename, delete)
- **ACLs**: Support for POSIX-compliant access control lists at directory and file level
- **Organization**: Can organize content with true hierarchical structure

```
container/
├── directory1/
│   ├── subdirectory1/
│   │   └── file.txt
│   └── file2.txt
└── directory2/
    └── file3.txt
```

**Use Case**: When you need to organize blob storage content using directories, hierarchical namespace must be enabled.

#### Without Hierarchical Namespace (Standard Blob Storage)

Without hierarchical namespace, blob containers only **simulate** directories using naming conventions:

- **Flat namespace**: All blobs are stored in a flat namespace
- **Delimiter-based**: Uses forward slash (`/`) in blob names to simulate folders
- **Not true directories**: Directories don't exist as separate entities
- **Performance limitation**: Operations like renaming a "directory" require copying all blobs
- **Example**: Blob named `folder/subfolder/file.txt` appears as if in directories, but it's just a blob name

**Limitation**: Cannot truly organize content with directories - only simulates folder structure through naming.

### Azure File Shares: Native Directory Support

Azure File Shares provide **native directory support** regardless of the storage account configuration:

- **True filesystem**: Operates as a traditional file system with real directories
- **SMB/NFS protocols**: Supports standard file sharing protocols
- **Independent of HNS**: Does not require hierarchical namespace (different service than Blob Storage)
- **Directory operations**: Full support for create, delete, rename, and navigate directories
- **Cross-platform**: Works with Windows, Linux, and macOS clients

**Use Case**: Ideal for applications requiring shared file storage with traditional file system semantics.

### Practical Example: Content Organization

**Scenario**: You need to organize storage account content using directories.

**Available Storage Resources**:
- `storage1` (Hierarchical namespace: Yes)
  - `cont1` (blob container)
  - `share1` (file share)
- `storage2` (Hierarchical namespace: No)
  - `cont2` (blob container)
  - `share2` (file share)

**Question**: Which containers and file shares can you use to organize content with true directories?

**Answer**: 
- ✅ `cont1`: Blob container with hierarchical namespace enabled → supports true directories
- ✅ `share1`: Azure File share → native directory support
- ✅ `share2`: Azure File share → native directory support
- ❌ `cont2`: Blob container without hierarchical namespace → only simulates directories

**Explanation**:
- Blob containers require hierarchical namespace to support true directory organization
- Azure File Shares always support native directories regardless of storage account settings
- Without hierarchical namespace, blob containers can only simulate directories through naming conventions, which doesn't meet the requirement for true directory-based organization

### Best Practices

1. **For Blob Storage Organization**: Enable hierarchical namespace on the storage account to unlock true directory support
2. **For File Sharing**: Use Azure File Shares which natively support directories through SMB/NFS protocols
3. **Plan Ahead**: Hierarchical namespace cannot be disabled once enabled - design your storage strategy carefully
4. **Migration Consideration**: Migrating from flat namespace to hierarchical namespace requires creating a new storage account

---

## Storage Account Requirements for Data Lake Storage Gen2

To enable Azure Data Lake Storage Gen2 capabilities, you must use a **general-purpose v2 (GPv2) storage account** with **hierarchical namespace enabled**. This configuration is essential for accessing advanced features like directory-level ACLs and multi-level folder structures.

### Key Requirements

| Requirement | Solution | Why It Matters |
|-------------|----------|----------------|
| **Petabyte-scale storage** | General-purpose v2 with HNS enabled | Supports up to 5 PiB account capacity with blob storage |
| **Blob storage** | General-purpose v2 account | Native blob storage support with all three blob types (block, append, page) |
| **Multiple folder levels** | Hierarchical namespace enabled | Enables unlimited directory depth (3+ levels of subfolders) |
| **Access Control Lists (ACLs)** | Hierarchical namespace enabled | Provides POSIX-compliant ACLs at directory and file level |

### Storage Account Type Comparison

When selecting a storage account type for large-scale blob storage with folder structures and ACLs, it's important to understand the differences:

| Storage Account Type | Supports Hierarchical Namespace? | Supports ACLs? | Best Use Case |
|---------------------|----------------------------------|----------------|---------------|
| **General-purpose v2 (GPv2) with HNS** | ✅ Yes | ✅ Yes | **Data Lake Storage Gen2**: Big data analytics, hierarchical folders, fine-grained permissions |
| Premium Block Blob | ❌ No | ❌ No | Low-latency scenarios requiring high transaction rates |
| Premium Page Blob | ❌ No | ❌ No | IaaS virtual hard disks (VHDs) for Azure VMs |
| Premium File Share | N/A (different service) | ✅ Yes (SMB ACLs) | Azure Files service, not Blob Storage |

### Why General-Purpose v2 with Hierarchical Namespace?

**General-purpose v2 storage accounts with hierarchical namespace enabled** are the correct choice when you need:

1. **Blob Storage**: Data must be stored as blobs (block blobs, append blobs, or page blobs)
2. **Large-Scale Storage**: Support for petabyte-level data storage
3. **Hierarchical Folder Structure**: Three or more levels of nested directories/subfolders
4. **Fine-Grained Permissions**: Directory-level and file-level ACLs using POSIX-compliant permissions
5. **Analytics Workloads**: Integration with big data tools like Apache Hadoop, Azure Databricks, Azure Synapse Analytics

### What Doesn't Work

❌ **Premium Block Blob Storage**
- Does not support hierarchical namespace
- Cannot organize blobs into directories with multiple levels
- Does not support ACLs at directory or file level
- Best for: Low-latency, high-throughput scenarios without folder structure requirements

❌ **Premium Page Blob Storage**
- Designed for VM disk storage (VHDs), not general-purpose data storage
- Does not support hierarchical namespace or ACLs
- Best for: Azure VM operating system and data disks

❌ **Premium File Share Storage**
- Part of Azure Files service, not Blob Storage
- Uses SMB protocol with SMB ACLs (different from POSIX ACLs)
- Does not meet the requirement of storing data in **blob storage**
- Best for: File shares requiring SMB protocol access

### Enabling Hierarchical Namespace

When creating a storage account, you must enable hierarchical namespace to unlock Data Lake Storage Gen2 capabilities:

```bash
# Azure CLI: Create GPv2 storage account with hierarchical namespace
az storage account create \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --hierarchical-namespace true
```

```powershell
# PowerShell: Create GPv2 storage account with hierarchical namespace
New-AzStorageAccount `
  -ResourceGroupName "myResourceGroup" `
  -Name "mystorageaccount" `
  -Location "eastus" `
  -SkuName "Standard_LRS" `
  -Kind "StorageV2" `
  -EnableHierarchicalNamespace $true
```

> **⚠️ Important Note**: Hierarchical namespace **cannot be disabled** after it's enabled on a storage account. Plan your account configuration carefully before enabling this feature.

---

## Migration Tools Comparison

When migrating data to Azure Data Lake Storage Gen2, several tools are available. Each has specific use cases and limitations.

### AzCopy

**AzCopy** is a command-line utility designed for high-performance data transfer to and from Azure Storage.

#### Key Features
- ✅ **Native support for Azure Data Lake Storage Gen2** (hierarchical namespace enabled accounts)
- ✅ **High-speed transfers** with parallelism and automatic retry logic
- ✅ **Resumable uploads** to handle network interruptions
- ✅ **Cross-platform** support (Windows, Linux, macOS)
- ✅ **Supports large datasets** (TBs to PBs)
- ✅ **Authentication options**: Azure AD, SAS tokens, account keys

#### Best Use Cases
- Bulk data migration from on-premises to Azure
- Migrating large volumes of unstructured data (JSON, CSV, logs, etc.)
- One-time or scheduled data transfers
- Migration to Data Lake Storage Gen2 (HNS-enabled accounts)

#### Syntax Example
```bash
# Copy files to Data Lake Storage Gen2
azcopy copy 'C:\local\data\*' 'https://storage1.dfs.core.windows.net/container/path' --recursive

# Copy with SAS token
azcopy copy 'C:\local\data\*' 'https://storage1.dfs.core.windows.net/container/path?sv=...' --recursive
```

---

### Azure File Sync

**Azure File Sync** enables you to centralize your file shares in Azure Files while maintaining local caching of files on Windows Server.

#### Key Features
- ✅ **Synchronizes Windows Server file shares** with Azure Files
- ✅ **Cloud tiering** to free up local storage
- ✅ **Multi-site access** to the same file share
- ❌ **Does NOT support Data Lake Storage Gen2** (hierarchical namespace)

#### Limitations
- ⚠️ Designed for **Azure Files**, not Azure Blob Storage or Data Lake Storage Gen2
- ⚠️ Requires Windows Server (not suitable for cross-platform scenarios)
- ⚠️ Optimized for file server synchronization, not bulk migration

#### Best Use Cases
- Syncing on-premises Windows file servers with Azure Files
- Branch office scenarios with centralized file storage
- Disaster recovery for file servers

---

### Robocopy

**Robocopy** is a Windows command-line tool for copying files and directories.

#### Key Features
- ✅ Robust file copying between Windows systems
- ✅ Supports local and network paths
- ❌ **No native support for Azure Storage APIs**
- ❌ **Cannot directly upload to Data Lake Storage Gen2**

#### Limitations
- ⚠️ Limited to Windows environments
- ⚠️ Requires mounting Azure Storage as network drive or intermediate steps
- ⚠️ No native Azure authentication support

#### Best Use Cases
- Local file migrations on Windows
- Network file share migrations between Windows servers
- Not suitable for direct Azure migrations

---

### Azure Storage Mover

**Azure Storage Mover** is a fully managed migration service for moving on-premises file shares to Azure.

#### Key Features
- ✅ Fully managed migration service
- ✅ Supports on-premises file shares
- ⚠️ **Still in preview** (limited production readiness)
- ⚠️ **Primarily optimized for Azure Blob Storage and Azure Files**
- ⚠️ Limited optimization for Data Lake Storage Gen2 (HNS-enabled accounts)

#### Limitations
- ⚠️ Preview status (not GA)
- ⚠️ Less mature than AzCopy for Data Lake Storage Gen2 scenarios
- ⚠️ May have region availability limitations

#### Best Use Cases
- Managed migrations from on-premises file servers to Azure Files
- Scenarios requiring minimal setup and management
- Future use as the service matures

---

## Migration Scenarios

### Scenario 1: Network-Attached Storage to Data Lake Storage Gen2

#### Problem Statement

You have a network-attached storage (NAS) device that hosts a file share containing **1 TB of JSON files**.

You have an Azure subscription with a storage account named **storage1** that has **hierarchical namespace enabled** (Azure Data Lake Storage Gen2).

**Question**: What tool should you use to migrate the files to storage1?

#### Answer Options

| Tool | Correct? | Explanation |
|------|----------|-------------|
| **AzCopy** | ✅ **Correct** | AzCopy is the optimal choice for this scenario because it natively supports Data Lake Storage Gen2 (hierarchical namespace enabled). It provides high-speed parallel transfers, resumable uploads, and handles large datasets efficiently. AzCopy can be run from any machine with network connectivity to Azure and is specifically designed for bulk data transfers to Azure Storage. |
| **Azure File Sync** | ❌ Incorrect | Azure File Sync is designed for synchronizing on-premises Windows Server file shares with Azure Files, not for migrating data to Data Lake Storage Gen2. It does not natively support hierarchical namespace and is optimized for file server replication, not bulk migration of unstructured JSON files. |
| **Robocopy** | ❌ Incorrect | Robocopy is a Windows-based file copying tool for local or networked Windows environments. It does not support direct uploads to Azure Data Lake Storage Gen2 and lacks native Azure Storage API support, making it unsuitable for this scenario. |
| **Azure Storage Mover** | ❌ Incorrect | While Azure Storage Mover is intended for migrating on-premises file shares to Azure, it is still in preview and is primarily optimized for Azure Blob Storage and Azure Files, rather than Data Lake Storage Gen2. It lacks the same level of optimization and maturity as AzCopy for hierarchical namespace-enabled accounts. |

#### Recommended Solution

**Use AzCopy** to migrate the 1 TB of JSON files from the network-attached storage to storage1.

#### Implementation Steps

1. **Install AzCopy** on a machine with network access to both the NAS device and Azure
   ```bash
   # Download and install AzCopy
   # https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10
   ```

2. **Authenticate to Azure Storage**
   ```bash
   # Option 1: Azure AD authentication
   azcopy login
   
   # Option 2: Use SAS token (generate from Azure portal)
   ```

3. **Copy files from NAS to Data Lake Storage Gen2**
   ```bash
   # Mount NAS share or access via network path
   # Copy to Data Lake Storage Gen2
   azcopy copy '/path/to/nas/share/*' \
     'https://storage1.dfs.core.windows.net/container/path' \
     --recursive \
     --overwrite=false \
     --log-level=INFO
   ```

4. **Monitor and verify the transfer**
   ```bash
   # AzCopy provides progress updates and creates logs
   # Verify file count and sizes after transfer completes
   ```

#### Why AzCopy is the Best Choice

| Requirement | How AzCopy Meets It |
|-------------|---------------------|
| **Large dataset (1 TB)** | Optimized for high-speed parallel transfers |
| **Hierarchical namespace** | Native support for Data Lake Storage Gen2 |
| **JSON files** | Handles any file type without restrictions |
| **Reliability** | Resumable uploads, automatic retries |
| **Performance** | Multi-threaded transfers for maximum throughput |
| **Flexibility** | Cross-platform, multiple authentication options |

---

## Practice Questions

### Question 1: Migration Tool Selection

**Scenario**: You need to migrate 1 TB of JSON files from a network-attached storage device to an Azure storage account with hierarchical namespace enabled.

**Question**: Which tool should you use?

**Options**:
- A) Azure File Sync
- B) AzCopy
- C) Robocopy
- D) Azure Storage Mover

<details>
<summary>Click to reveal answer</summary>

**Correct Answer**: B) AzCopy

**Explanation**:
- **AzCopy** is specifically designed for transferring large amounts of data to Azure Blob Storage and Azure Data Lake Storage Gen2. It supports hierarchical namespace-enabled accounts and provides high-speed, resumable transfers.
- **Azure File Sync** is for synchronizing Windows Server file shares with Azure Files, not Data Lake Storage Gen2.
- **Robocopy** cannot directly upload to Azure Storage and lacks native Azure API support.
- **Azure Storage Mover** is still in preview and primarily optimized for Azure Files/Blob Storage, not Data Lake Storage Gen2.

</details>

---

### Question 2: Hierarchical Namespace Understanding

**Question**: What is the primary benefit of enabling hierarchical namespace on an Azure storage account?

**Options**:
- A) Lower storage costs
- B) Organization of blobs into directories and subdirectories for big data analytics
- C) Automatic data encryption at rest
- D) Increased storage capacity limits

<details>
<summary>Click to reveal answer</summary>

**Correct Answer**: B) Organization of blobs into directories and subdirectories for big data analytics

**Explanation**:
Hierarchical namespace (HNS) enables Azure Data Lake Storage Gen2 capabilities, allowing blobs to be organized into a directory structure similar to a file system. This is essential for big data analytics workloads that require efficient directory operations and POSIX-compliant access controls. Storage costs, encryption, and capacity limits are independent of HNS.

</details>

---

### Question 3: Storage Account Configuration for Large-Scale Requirements

**Scenario**: You need to recommend an Azure Storage solution that meets the following requirements:

- The storage must support 1 PB of data
- The data must be stored in blob storage
- The storage must support three levels of subfolders
- The storage must support Access Control Lists (ACLs)

**Question**: What should you include in the recommendation?

**Options**:
- A) A premium storage account that is configured for page blobs
- B) A premium storage account that is configured for block blobs
- C) A premium storage account that is configured for file shares and supports large file shares
- D) A general-purpose v2 storage account that has hierarchical namespace enabled

<details>
<summary>Click to reveal answer</summary>

**Correct Answer**: D) A general-purpose v2 storage account that has hierarchical namespace enabled

**Explanation**:

✅ **A general-purpose v2 storage account with hierarchical namespace enabled** is correct because:
- This configuration enables **Azure Data Lake Storage Gen2** capabilities
- Supports **petabyte-scale storage** (up to 5 PiB capacity)
- Uses **blob storage** as the underlying storage layer
- Hierarchical namespace allows **unlimited directory depth** (3+ levels of subfolders)
- Provides **POSIX-compliant ACLs** at both directory and file level
- Enables fine-grained permissions management required for multi-level folder structures

❌ **Premium storage account for page blobs** is incorrect because:
- Page blobs are designed primarily for **IaaS virtual hard disks** (OS and data disks for Azure VMs)
- Does **not support hierarchical namespace** or directory structures
- Does **not support ACLs** at directory or file level
- Not optimized for general-purpose data storage or analytics workloads

❌ **Premium storage account for block blobs** is incorrect because:
- While block blobs are suitable for storing unstructured data, premium block blob accounts do **not support hierarchical namespace**
- Cannot organize blobs into **multi-level directories**
- Does **not support ACLs** at directory or file level (only container-level permissions)
- Optimized for low-latency, high-throughput scenarios, not hierarchical data organization

❌ **Premium file share with large file shares** is incorrect because:
- Azure Files is a **different service** from Blob Storage (uses SMB/NFS protocols)
- Although it supports ACLs and folder structures, it does **not store data in blob storage**
- Not optimized for petabyte-scale blob data scenarios
- Uses SMB ACLs rather than POSIX-compliant ACLs provided by Data Lake Storage Gen2

**Key Takeaway**: When requirements include blob storage, hierarchical folder structures (3+ levels), and ACLs, always choose a **general-purpose v2 storage account with hierarchical namespace enabled** (Data Lake Storage Gen2).

**References**:
- [Azure Data Lake Storage Gen2 Introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- [Hierarchical Namespace](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-namespace)
- [Access Control in Data Lake Storage Gen2](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control)
- [Storage Account Overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)

</details>

---

### Question 4: Enabling HNS for Existing Storage Accounts

**Scenario**: An Oil and Gas company has a core application that offers Business Intelligence (BI) and Analytics features for several clients. However, to implement new features and improve performance, the application needs to utilize hierarchical namespace (HNS) capabilities such as file and directory-level security and faster operations. These capabilities are essential for big data analytics workloads.

The client's data currently resides in fewer than 10 storage accounts, with large amounts of data.

**Question**: What recommendations do you have to unblock new planned features for the application?

**Options**:
- A) Enable the HNS toggle on Storage Accounts configuration in Portal
- B) Enable the HNS through the "az storage account" CLI command
- C) Create an HNS enabled Storage Account and migrate the data
- D) Upgrade current Storage accounts to Data Lake Gen2

<details>
<summary>Click to reveal answer</summary>

**Correct Answer**: D) Upgrade current Storage accounts to Data Lake Gen2

**Explanation**:

✅ **Upgrading current Storage accounts to Data Lake Gen2** is the correct recommendation because:
- **Data Lake Gen2** provides hierarchical namespace capabilities such as file and directory-level security, faster operations, and scalability
- It is well-suited for **big data analytics workloads**
- Azure supports **in-place upgrade** of existing storage accounts to enable hierarchical namespace (Data Lake Gen2)
- This approach allows you to **retain existing data** without requiring a full migration to new storage accounts
- Upgrading enables the application to leverage HNS capabilities and improve performance

❌ **Enable the HNS toggle on Storage Accounts configuration in Portal** is incorrect because:
- There is no simple HNS toggle that can be enabled on existing standard storage accounts through the portal
- Enabling HNS requires a formal upgrade process to Data Lake Storage Gen2

❌ **Enable the HNS through the "az storage account" CLI command** is incorrect because:
- You cannot simply enable HNS on an existing storage account using a CLI toggle
- The upgrade process involves more than just a single CLI command setting

❌ **Create an HNS enabled Storage Account and migrate the data** is incorrect because:
- While this would work, it is not the optimal solution when you can upgrade existing accounts in-place
- Migration involves additional complexity, downtime, and potential data transfer costs
- Azure now supports upgrading existing storage accounts to Data Lake Gen2, making full migration unnecessary

**Key Takeaway**: When existing storage accounts need hierarchical namespace capabilities for big data analytics, **upgrade the storage accounts to Data Lake Storage Gen2** rather than migrating data to new accounts. This preserves existing data and simplifies the transition.

**References**:
- [Upgrade Azure Blob Storage with Azure Data Lake Storage Gen2 capabilities](https://learn.microsoft.com/en-us/azure/storage/blobs/upgrade-to-data-lake-storage-gen2)
- [Azure Data Lake Storage Gen2 Introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)

</details>

---

## Related Learning Resources

### Microsoft Learn Documentation

- [Introduction to Azure Data Lake Storage Gen2](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
- [Get started with AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Azure File Sync planning](https://learn.microsoft.com/en-us/azure/storage/file-sync/file-sync-planning)
- [Azure Storage Mover overview](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview)

### Related Topics

- [Azure Storage Redundancy Options](./01-azure-storage-redundancy-options.md)
- [Azure Storage Secure Access](./02-azure-storage-secure-access.md)
- [Azure Blob Storage API](./03-azure-blob-storage-api.md)
- [Azure Storage Access Tiers and Rehydration](./04-azure-storage-access-tiers-rehydration.md)

---

**Domain**: Design data storage solutions  
**Last Updated**: December 2025
