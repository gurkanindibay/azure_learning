# Azure Files Overview

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Protocols](#protocols)
  - [SMB Protocol](#smb-protocol)
  - [NFS Protocol](#nfs-protocol)
- [Supported Operating Systems](#supported-operating-systems)
- [Mounting Azure File Shares](#mounting-azure-file-shares)
  - [Windows](#windows)
  - [Linux](#linux)
  - [macOS](#macos)
- [Use Cases](#use-cases)
- [Azure Files vs Azure Blob Storage](#azure-files-vs-azure-blob-storage)
- [Key Takeaways](#key-takeaways)
- [References](#references)

## Overview

Azure Files offers **fully managed file shares in the cloud** that are accessible via industry-standard protocols. Azure file shares can be mounted concurrently by cloud or on-premises deployments, making them ideal for shared storage scenarios.

**Key Benefits:**
- Fully managed (no need to manage hardware or OS)
- Shared access across multiple VMs and applications
- Familiar file system interface
- Cross-platform support
- Hybrid cloud scenarios with Azure File Sync

## Key Features

| Feature | Description |
|---------|-------------|
| **Fully Managed** | No need to manage hardware, OS, or patches |
| **Shared Access** | Multiple clients can access simultaneously |
| **Familiar Interface** | Standard file system APIs work as expected |
| **Resilient** | Built for high availability |
| **Programmable** | REST API, client libraries, Azure CLI, PowerShell |
| **Hybrid Support** | Azure File Sync for on-premises caching |

## Protocols

Azure Files supports two industry-standard file sharing protocols:

### SMB Protocol

**Server Message Block (SMB)** is the most commonly used protocol for Azure Files.

- **Versions supported**: SMB 2.1, SMB 3.0, SMB 3.1.1
- **Encryption**: SMB 3.0+ supports encryption in transit
- **Port**: 445 (must be open for mounting)
- **Authentication**: Storage account key, Azure AD Domain Services, on-premises AD DS

### NFS Protocol

**Network File System (NFS)** is supported for Linux workloads.

- **Version**: NFS 4.1
- **Authentication**: Host-based authentication using virtual network rules
- **Use case**: Linux applications requiring POSIX-compliant file system
- **Requirement**: Premium file shares only

| Protocol | Windows | Linux | macOS | Premium Required |
|----------|---------|-------|-------|------------------|
| **SMB** | ✅ | ✅ | ✅ | No |
| **NFS** | ❌ | ✅ | ❌ | Yes |

## Supported Operating Systems

Azure Files SMB file shares are accessible from **Windows, Linux, and macOS** clients.

| Operating System | SMB Support | NFS Support | Notes |
|------------------|-------------|-------------|-------|
| **Windows** | ✅ Yes | ❌ No | Windows 7+ (SMB 2.1+), Windows 8.1+ recommended (SMB 3.0) |
| **Linux** | ✅ Yes | ✅ Yes | Most distributions with CIFS or NFS support |
| **macOS** | ✅ Yes | ❌ No | macOS 10.11 (El Capitan)+ |

### Important Notes:

- **Windows**: Requires port 445 to be open (some ISPs block this port)
- **Linux**: Use `cifs-utils` package for SMB, native NFS support for NFS shares
- **macOS**: Native SMB support via Finder or command line
- **Mobile (Android/iOS)**: Not natively supported for direct mounting

---

### Practice Question: Azure Files Supported Operating Systems

**Question:**
Which operating systems can mount an external drive using Azure File Share?

**Options:**
1. ❌ Windows Only
2. ❌ Windows and Linux Only
3. ✅ Windows, Linux and macOS
4. ❌ Android and iOS Only

**Answer: Windows, Linux and macOS**

**Explanation:**
Azure Files offers fully managed file shares in the cloud that are accessible via the industry standard **Server Message Block (SMB)** protocol or **Network File System (NFS)** protocol. Azure file shares can be mounted concurrently by cloud or on-premises deployments.

**Azure Files SMB file shares are accessible from Windows, Linux, and macOS clients.**

- ✅ **Windows**: Full SMB support (Windows 7 and later)
- ✅ **Linux**: SMB support via CIFS, NFS support for Premium shares
- ✅ **macOS**: SMB support (macOS 10.11 El Capitan and later)
- ❌ **Android/iOS**: Not supported for direct file share mounting

**Reference:** [Introduction to Azure Files](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-introduction)

---

## Mounting Azure File Shares

### Windows

```powershell
# Mount Azure File Share on Windows
$connectTestResult = Test-NetConnection -ComputerName <storage-account>.file.core.windows.net -Port 445
if ($connectTestResult.TcpTestSucceeded) {
    # Mount the drive
    net use Z: \\<storage-account>.file.core.windows.net\<share-name> /user:Azure\<storage-account> <storage-account-key>
}
```

Or using PowerShell cmdlet:
```powershell
# Using New-PSDrive
$storageAccountKey = "<storage-account-key>"
$storageAccountName = "<storage-account>"
$shareName = "<share-name>"

$connectTestResult = Test-NetConnection -ComputerName "$storageAccountName.file.core.windows.net" -Port 445
if ($connectTestResult.TcpTestSucceeded) {
    cmd.exe /C "cmdkey /add:`"$storageAccountName.file.core.windows.net`" /user:`"Azure\$storageAccountName`" /pass:`"$storageAccountKey`""
    New-PSDrive -Name Z -PSProvider FileSystem -Root "\\$storageAccountName.file.core.windows.net\$shareName" -Persist
}
```

### Linux

```bash
# Install cifs-utils (for SMB)
sudo apt-get install cifs-utils

# Create mount point
sudo mkdir /mnt/azurefiles

# Mount the share
sudo mount -t cifs //<storage-account>.file.core.windows.net/<share-name> /mnt/azurefiles \
    -o vers=3.0,username=<storage-account>,password=<storage-account-key>,dir_mode=0777,file_mode=0777,serverino

# For persistent mount, add to /etc/fstab
//<storage-account>.file.core.windows.net/<share-name> /mnt/azurefiles cifs vers=3.0,username=<storage-account>,password=<storage-account-key>,dir_mode=0777,file_mode=0777 0 0
```

For NFS (Premium shares only):
```bash
# Mount NFS share
sudo mount -t nfs <storage-account>.file.core.windows.net:/<storage-account>/<share-name> /mnt/azurefiles -o vers=4,minorversion=1,sec=sys
```

### macOS

```bash
# Mount using Finder
# Go > Connect to Server (Cmd+K)
# Enter: smb://<storage-account>.file.core.windows.net/<share-name>
# Use storage account name as username and storage account key as password

# Or using command line
mount_smbfs //Azure@<storage-account>.file.core.windows.net/<share-name> /Volumes/azurefiles
```

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Lift and Shift** | Migrate on-premises apps that rely on file shares |
| **Shared Application Settings** | Store configuration files accessed by multiple VMs |
| **Diagnostic Data** | Centralize logs and metrics from multiple sources |
| **Dev/Test** | Share tools and utilities across development environments |
| **Containerization** | Persistent storage for containers (AKS, ACI) |
| **Hybrid Scenarios** | Extend on-premises file servers with Azure File Sync |

## Azure Files vs Azure Blob Storage

| Feature | Azure Files | Azure Blob Storage |
|---------|-------------|-------------------|
| **Access Method** | SMB/NFS (file system) | REST API (object storage) |
| **Structure** | Hierarchical (folders/files) | Flat (containers/blobs) |
| **Mounting** | ✅ Direct mount as drive | ❌ No direct mounting |
| **Use Case** | File shares, lift-and-shift | Large-scale unstructured data |
| **POSIX Support** | ✅ Yes (NFS) | ❌ No |
| **Maximum File Size** | 4 TiB (SMB), 4 TiB (NFS) | 190.7 TiB (block blob) |

## Key Takeaways

1. **Cross-Platform Support**: Azure Files SMB shares work on **Windows, Linux, and macOS**
2. **Two Protocols**: SMB (all platforms) and NFS (Linux only, Premium tier)
3. **Port 445 Required**: SMB requires port 445 to be open
4. **Fully Managed**: No infrastructure to maintain
5. **Concurrent Access**: Multiple clients can access the same share simultaneously
6. **Mobile Not Supported**: Android and iOS cannot directly mount Azure File shares

## References

- [Introduction to Azure Files](https://docs.microsoft.com/en-us/azure/storage/files/storage-files-introduction)
- [Mount SMB Azure file share on Windows](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-windows)
- [Mount SMB Azure file share on Linux](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-linux)
- [Mount SMB Azure file share on macOS](https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-mac)
- [Azure Files pricing](https://azure.microsoft.com/en-us/pricing/details/storage/files/)
