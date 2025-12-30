# Azure Virtual Machine Disk Management

## Table of Contents

- [Overview](#overview)
- [Disk Types](#disk-types)
- [Attaching and Detaching Data Disks](#attaching-and-detaching-data-disks)
  - [Minimizing Downtime When Moving Disks](#minimizing-downtime-when-moving-disks)
  - [Detach Operation](#detach-operation)
  - [Attach Operation](#attach-operation)
- [Best Practices](#best-practices)
- [Practice Questions](#practice-questions)

---

## Overview

Azure Virtual Machines use disks for operating system storage, temporary storage, and persistent data storage. Understanding how to manage these disks efficiently, including attaching and detaching operations, is crucial for maintaining high availability and minimizing downtime.

---

## Disk Types

Azure VMs use several types of disks:

### OS Disk
- **Purpose**: Contains the operating system and boot volume
- **Required**: Every VM must have one OS disk
- **Persistence**: Data persists across reboots and VM restarts
- **Size**: Varies by OS image (typically 127 GB to 2 TB)

### Data Disks
- **Purpose**: Store application data, databases, and user files
- **Optional**: VMs can have zero or more data disks
- **Portable**: Can be detached and attached to different VMs
- **Maximum**: Varies by VM size (from 2 to 64+ data disks)
- **Persistence**: Data persists independently of the VM lifecycle

### Temporary Disk
- **Purpose**: Short-term storage for page/swap files
- **Ephemeral**: Data is lost when VM is stopped/deallocated
- **Not for persistent data**: Should not store critical data
- **Included**: Automatically provisioned with most VM sizes

---

## Attaching and Detaching Data Disks

Data disks can be moved between Azure VMs by detaching from one VM and attaching to another. This is a common operation for scenarios such as:

- Migrating data between VMs
- Sharing storage across different VMs (at different times)
- VM replacement or upgrade scenarios
- Disaster recovery operations

### Minimizing Downtime When Moving Disks

When you need to attach a data disk from one Azure VM to another, the **order of operations** is critical to minimize downtime.

#### Correct Procedure (Minimal Downtime)

**Step 1: Detach the data disk from the source VM** ✅ **FIRST ACTION**

```bash
# Azure CLI - Detach disk (VM can remain running)
az vm disk detach \
  --resource-group MyResourceGroup \
  --vm-name SourceVM \
  --name MyDataDisk
```

**Step 2: Attach the data disk to the target VM**

```bash
# Azure CLI - Attach disk to target VM
az vm disk attach \
  --resource-group MyResourceGroup \
  --vm-name TargetVM \
  --name MyDataDisk
```

#### Why This Order Minimizes Downtime

✅ **No VM shutdown required** - Both VMs can remain running during the operation  
✅ **Disk detachment is safe while VM runs** - Azure safely detaches the disk from the running source VM  
✅ **Disk attachment is safe while VM runs** - The target VM can be running when the disk is attached  
✅ **Only application-level impact** - Applications using the disk need to release file handles, but the VM stays operational  

### Detach Operation

**Detaching a data disk** removes the disk from a VM but preserves the disk and its data in Azure Storage.

#### Key Characteristics

- **Source VM state**: Can be **running or stopped** (preferably running to minimize downtime)
- **Data preservation**: Disk and all data remain intact in Azure Storage
- **No VM reboot**: The source VM does not require a restart
- **Billing**: Disk storage continues to be billed even when detached
- **Safety**: The disk cannot be attached to multiple VMs simultaneously (except with shared disks feature)

#### When to Detach

Before you can attach a disk to another VM, it **must be detached** from its current VM. A data disk can only be attached to **one VM at a time** (unless using Azure Shared Disks feature).

#### Detach Methods

**Azure Portal**:
1. Navigate to the source VM
2. Go to **Disks** section
3. Select the data disk
4. Click **Detach**
5. Confirm the operation

**Azure CLI**:
```bash
az vm disk detach \
  --resource-group MyResourceGroup \
  --vm-name SourceVM \
  --name MyDataDisk
```

**Azure PowerShell**:
```powershell
$vm = Get-AzVM -ResourceGroupName "MyResourceGroup" -Name "SourceVM"
Remove-AzVMDataDisk -VM $vm -Name "MyDataDisk"
Update-AzVM -ResourceGroupName "MyResourceGroup" -VM $vm
```

**ARM Template** (update VM configuration):
```json
{
  "properties": {
    "storageProfile": {
      "dataDisks": [
        // Remove the disk object from the array
      ]
    }
  }
}
```

### Attach Operation

**Attaching a data disk** connects an existing managed disk to a VM, making it available for use by the operating system.

#### Key Characteristics

- **Target VM state**: Can be **running or stopped** (preferably running to minimize downtime)
- **Disk availability**: Disk must be in an **unattached** state (or use shared disk feature)
- **Region requirement**: Disk and VM must be in the **same Azure region**
- **No VM reboot**: The target VM does not require a restart (OS will detect the new disk)
- **LUN assignment**: Disk is assigned a Logical Unit Number (LUN) automatically or manually
- **OS detection**: Modern operating systems detect the new disk automatically (hot-plug)

#### Attach Methods

**Azure Portal**:
1. Navigate to the target VM
2. Go to **Disks** section
3. Click **+ Add data disk**
4. Select **Existing disk**
5. Choose the disk and click **Save**

**Azure CLI**:
```bash
az vm disk attach \
  --resource-group MyResourceGroup \
  --vm-name TargetVM \
  --name MyDataDisk
```

**Azure PowerShell**:
```powershell
$vm = Get-AzVM -ResourceGroupName "MyResourceGroup" -Name "TargetVM"
$disk = Get-AzDisk -ResourceGroupName "MyResourceGroup" -DiskName "MyDataDisk"

$vm = Add-AzVMDataDisk -VM $vm `
  -Name "MyDataDisk" `
  -CreateOption Attach `
  -ManagedDiskId $disk.Id `
  -Lun 0

Update-AzVM -ResourceGroupName "MyResourceGroup" -VM $vm
```

**ARM Template**:
```json
{
  "properties": {
    "storageProfile": {
      "dataDisks": [
        {
          "lun": 0,
          "name": "MyDataDisk",
          "createOption": "Attach",
          "managedDisk": {
            "id": "/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Compute/disks/MyDataDisk"
          }
        }
      ]
    }
  }
}
```

---

## Best Practices

### Disk Movement Operations

✅ **Always detach first** - Before attaching to another VM, ensure the disk is detached from the source  
✅ **Keep VMs running** - Both source and target VMs can remain running during detach/attach operations  
✅ **Verify application state** - Ensure applications have released file handles before detaching  
✅ **Use managed disks** - Managed disks simplify disk operations and lifecycle management  
✅ **Same region requirement** - Disks can only be attached to VMs in the same Azure region  

### Minimizing Downtime

✅ **Plan the operation** - Identify dependencies and coordinate with application teams  
✅ **Graceful shutdown of apps** - Stop applications using the disk rather than the entire VM  
✅ **Quick detach/attach** - The actual detach and attach operations are very fast  
✅ **Post-attach verification** - Verify the disk is accessible and mounted correctly in the target VM  

### Avoiding Common Mistakes

❌ **Don't stop source VM first** - Unnecessary downtime; detach works on running VMs  
❌ **Don't stop target VM** - Unnecessary downtime; attach works on running VMs  
❌ **Don't delete the source VM** - Extreme action that causes data loss; just detach the disk  
❌ **Don't forget to mount** - After attaching, the disk may need to be mounted in the OS  
❌ **Don't attempt concurrent attachment** - A disk can only be attached to one VM at a time (except shared disks)  

---

## Practice Questions

### Question 1: Moving Data Disk Between VMs with Minimal Downtime

**Scenario**: You have an Azure virtual machine (VM) that has a single data disk. You have been tasked with attaching this data disk to another Azure VM.

**Requirement**: Make sure that your strategy allows for the virtual machines to be offline for the least amount of time possible.

**Question**: Which of the following is the action you should take FIRST?

**Options**:

A) Stop the VM that includes the data disk

B) Stop the VM that the data disk must be attached to

C) **Detach the data disk**

D) Delete the VM that includes the data disk

---

**Correct Answer**: **C) Detach the data disk**

---

### Explanation

**Why Detach the Data Disk FIRST?**

#### 1. **No VM Shutdown Required** ✅

- **Data disks can be detached while the VM is running**
- Azure safely detaches the disk from the source VM without requiring a shutdown
- The source VM remains operational during the detach operation
- Only the applications actively using the disk are affected, not the entire VM

#### 2. **Minimizes Total Downtime** ✅

**Detach-first approach**:
```
Source VM State:    [Running] → [Running]     (0 downtime)
Detach Operation:   [Detach disk]            (seconds)
Target VM State:    [Running] → [Running]     (0 downtime)
Attach Operation:   [Attach disk]            (seconds)

Total VM Downtime: 0 minutes ✅
Total Disk Downtime: <1 minute (detach + attach)
```

**Stop-first approach** (INCORRECT):
```
Source VM State:    [Running] → [Stopped] → [Running]
                    (Stop VM = minutes of downtime)
Detach Operation:   [Detach disk]
Target VM State:    [Running] → [Running]
Attach Operation:   [Attach disk]

Total VM Downtime: Several minutes ❌
Total Disk Downtime: Several minutes
```

#### 3. **Disk Portability Prerequisite** ✅

- A data disk **must be detached** before it can be attached to another VM
- You cannot attach a disk that is currently attached to a different VM
- Detaching is a **required first step**, making it the logical starting point

#### 4. **Safe and Non-Destructive** ✅

- Detaching a disk **preserves all data** on the disk
- The disk remains in Azure Storage and can be reattached later
- No data loss or corruption risk
- Reversible operation if needed

---

### Why Other Options Are Incorrect

**A) Stop the VM that includes the data disk** ❌

**Why it's wrong**:
- **Unnecessary downtime** for the source VM
- Stopping a VM deallocates it, causing several minutes of downtime
- **Detaching a disk does NOT require stopping the VM**
- Applications running on the source VM are unnecessarily interrupted
- The entire VM and all its services become unavailable

**Impact**:
```
Source VM downtime: 5-10 minutes ❌
  ├─ Stop/deallocate: 2-3 minutes
  ├─ Detach disk: 10-30 seconds
  ├─ Start/allocate: 2-3 minutes
  └─ Applications restart: 1-2 minutes

Could have been: 0 minutes with detach-only approach
```

**When this might be needed**:
- If the application has file locks preventing safe detach (rare)
- If you need to ensure absolutely no I/O operations during detach
- Generally NOT recommended as the first action

---

**B) Stop the VM that the data disk must be attached to** ❌

**Why it's wrong**:
- **Completely unnecessary** - Attaching a disk does NOT require stopping the target VM
- Modern operating systems support **hot-plug** for disks
- Azure automatically assigns the disk to the VM and the OS detects it
- Causes unnecessary downtime on the target VM
- Services on the target VM are interrupted for no reason

**Impact**:
```
Target VM downtime: 5-10 minutes ❌
  ├─ Stop/deallocate: 2-3 minutes
  ├─ Attach disk: 10-30 seconds
  ├─ Start/allocate: 2-3 minutes
  └─ Applications restart: 1-2 minutes

Could have been: 0 minutes with hot-attach
```

**Key point**: Azure VMs support attaching disks while running. The disk appears in the operating system and can be mounted without a reboot.

---

**D) Delete the VM that includes the data disk** ❌

**Why it's wrong**:
- **Extremely destructive and unnecessary action**
- Deleting the VM does NOT automatically preserve the data disk
- Risk of **accidental data loss** if the disk is configured to delete with the VM
- Causes **maximum downtime** - the source VM is completely destroyed
- Requires recreating the source VM if needed later
- Much more complex than simply detaching the disk

**Consequences**:
```
Source VM state: [DELETED] ❌
  ├─ Complete loss of VM configuration
  ├─ Need to recreate VM from scratch
  ├─ Risk of deleting the data disk if not careful
  └─ Permanent downtime for source VM

Risk factors:
  ⚠️ Data disk may be deleted with VM (depends on settings)
  ⚠️ All VM configurations lost
  ⚠️ Network interfaces and other resources may be deleted
```

**When deletion might be appropriate**:
- When you're permanently decommissioning the source VM
- As part of a VM migration strategy where the old VM won't be used again
- **But NOT as the first step when simply moving a disk**

---

### Optimal Procedure for Minimal Downtime

**Step-by-Step Process**:

1. **Detach the data disk from the source VM** ✅ FIRST
   - Source VM: Remains running
   - Downtime: None for the VM
   - Duration: 10-30 seconds

2. **Attach the data disk to the target VM** ✅ SECOND
   - Target VM: Remains running
   - Downtime: None for the VM
   - Duration: 10-30 seconds

3. **Mount the disk in the target VM's operating system** (if needed)
   - Connect to target VM via RDP/SSH
   - Initialize disk if first-time use
   - Assign drive letter or mount point
   - Duration: 1-2 minutes

**Total downtime**:
- **Source VM**: 0 minutes
- **Target VM**: 0 minutes
- **Data disk availability**: <1 minute between detach and attach

---

### Best Practices for Disk Migration

#### Before Detaching

✅ **Coordinate with application owners** - Ensure applications can handle the disk being removed  
✅ **Flush pending writes** - Ensure all data is written to disk  
✅ **Gracefully stop applications** - Stop applications using the disk (not the entire VM)  
✅ **Unmount the disk** - Properly unmount the disk in the OS before detaching  
✅ **Document disk details** - Note the disk name, size, LUN, and any special configurations  

#### During Operations

✅ **Monitor the detach operation** - Verify successful detachment before proceeding  
✅ **Verify disk state** - Ensure disk shows as "Unattached" before attaching to target  
✅ **Use same region** - Ensure target VM is in the same Azure region as the disk  
✅ **Check target VM capacity** - Verify target VM can accept another data disk  

#### After Attaching

✅ **Verify disk visibility** - Check that the OS detects the newly attached disk  
✅ **Mount the disk** - Configure the disk in the operating system  
✅ **Test data accessibility** - Verify that data on the disk is accessible and intact  
✅ **Update application configurations** - Point applications to the new disk location/drive letter  
✅ **Monitor performance** - Ensure disk performance meets expectations on the new VM  

---

### Key Takeaways

1. **Detach First = Minimal Downtime**
   > The first action should be to detach the data disk from the source VM. Both the source and target VMs can remain running throughout the operation, resulting in zero VM downtime.

2. **VMs Can Remain Running**
   > Modern Azure VMs support hot-detach and hot-attach operations for data disks. There is no requirement to stop either the source or target VM during the disk move operation.

3. **Stopping VMs is Unnecessary**
   > Stopping VMs (either source or target) adds unnecessary downtime without providing any benefit. Azure handles disk detach and attach operations safely while VMs are running.

4. **Deleting VMs is Destructive**
   > Deleting the source VM is an extreme action that risks data loss and causes maximum downtime. Simply detach the disk to preserve both the VM and its configuration.

5. **Application-Level Coordination**
   > While VMs can remain running, applications using the disk should gracefully release file handles before detaching. This is an application-level concern, not a VM-level requirement.

6. **Disk Detachment is a Prerequisite**
   > A data disk must be in an "Unattached" state before it can be attached to another VM. This makes detaching the logical and required first step.

---

### Real-World Scenario

**Scenario**: Production database server migration

You have:
- **Source VM**: `DB-Server-01` with a 1 TB data disk containing database files
- **Target VM**: `DB-Server-02` (newer, larger VM for better performance)
- **Requirement**: Minimize downtime during migration

**Incorrect approach** (Maximum downtime):
```
1. Stop DB-Server-01                     → 2-3 min downtime
2. Detach data disk                      → 30 seconds
3. Stop DB-Server-02                     → 2-3 min downtime
4. Attach data disk to DB-Server-02      → 30 seconds
5. Start DB-Server-02                    → 2-3 min
6. Start database services               → 1-2 min

Total downtime: 10-15 minutes ❌
```

**Correct approach** (Minimal downtime):
```
1. Stop database services on DB-Server-01     → 30 seconds (app-level)
2. Unmount disk in OS                         → 10 seconds
3. Detach data disk (VM still running)        → 20 seconds
4. Attach data disk to DB-Server-02           → 20 seconds (VM still running)
5. Mount disk in DB-Server-02 OS              → 30 seconds
6. Start database services on DB-Server-02    → 1-2 min

Total downtime: 3-4 minutes ✅
```

**Savings**: 6-11 minutes of downtime avoided by not stopping VMs unnecessarily.

---

### Azure CLI Complete Example

```bash
# Step 1: Stop the application (application-specific command)
# For example, stop SQL Server, web server, etc.
# This is done within the VM, not at the VM level

# Step 2: Detach the data disk from source VM (VM remains running)
az vm disk detach \
  --resource-group MyResourceGroup \
  --vm-name SourceVM \
  --name MyDataDisk

# Step 3: Verify disk is detached
az disk show \
  --resource-group MyResourceGroup \
  --name MyDataDisk \
  --query diskState

# Expected output: "Unattached"

# Step 4: Attach the data disk to target VM (VM remains running)
az vm disk attach \
  --resource-group MyResourceGroup \
  --vm-name TargetVM \
  --name MyDataDisk

# Step 5: Verify disk is attached
az vm show \
  --resource-group MyResourceGroup \
  --name TargetVM \
  --query "storageProfile.dataDisks[].name"

# Step 6: In the target VM OS, mount the disk
# Linux: sudo mount /dev/sdc1 /mnt/data
# Windows: Assign drive letter via Disk Management
```

---

### Comparison Table

| Action | Source VM Downtime | Target VM Downtime | Total Time | Risk Level |
|--------|-------------------|-------------------|------------|------------|
| **Detach disk first** | 0 min | 0 min | <1 min | ✅ Low |
| Stop source VM first | 5-10 min | 0 min | 5-10 min | ⚠️ Medium |
| Stop target VM first | 0 min | 5-10 min | 5-10 min | ⚠️ Medium |
| Delete source VM | Permanent | 0 min | N/A | ❌ High |

---

