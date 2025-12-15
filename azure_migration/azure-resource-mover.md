# Azure Resource Mover

## Overview

**Azure Resource Mover** is a native Azure service designed to move Azure resources between resource groups, subscriptions, and regions. It simplifies the process of relocating Azure-native resources while maintaining dependencies and minimizing downtime.

## Key Capabilities

- **Move between Resource Groups**: Relocate resources within the same subscription
- **Move between Subscriptions**: Transfer resources to different subscriptions
- **Move between Regions**: Migrate resources across Azure regions
- **Dependency Management**: Automatically identifies and handles resource dependencies
- **Validation**: Pre-move validation to identify potential issues

---

## When to Use Azure Resource Mover

| Scenario | Use Azure Resource Mover? |
|----------|---------------------------|
| Move Azure VM to different resource group | ✅ Yes |
| Move Azure VM to different subscription | ✅ Yes |
| Move Azure VM to different region | ✅ Yes |
| Migrate on-premises VM to Azure | ❌ No - Use Azure Migrate |
| Manage on-premises resources from Azure | ❌ No - Use Azure Arc |
| Cross-tenant resource management | ❌ No - Use Azure Lighthouse |

---

## Supported Resources

Azure Resource Mover supports moving many Azure resource types, including:

- **Virtual Machines** (and associated resources like disks, NICs)
- **Virtual Networks**
- **Network Security Groups**
- **Public IP Addresses**
- **Availability Sets**
- **Load Balancers**
- **SQL Databases**
- **Storage Accounts**

---

## Move Process

### Moving Between Resource Groups

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Azure Subscription                            │
│                                                                      │
│  ┌──────────────────────┐         ┌──────────────────────┐         │
│  │   Resource Group 1   │         │   Resource Group 2   │         │
│  │        (RG1)         │         │        (RG2)         │         │
│  │                      │         │                      │         │
│  │  ┌─────────────┐    │  Move   │                      │         │
│  │  │    VM1      │────┼────────►│  ┌─────────────┐    │         │
│  │  │  (Azure VM) │    │         │  │    VM1      │    │         │
│  │  └─────────────┘    │         │  │  (Azure VM) │    │         │
│  │                      │         │  └─────────────┘    │         │
│  └──────────────────────┘         └──────────────────────┘         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Steps to Move Resources

1. **Prepare**: Identify resources to move and their dependencies
2. **Validate**: Run validation to check for move restrictions
3. **Initiate Move**: Start the move operation
4. **Monitor**: Track progress in the Azure portal
5. **Verify**: Confirm resources are functioning in the new location

---

## Resource Move Methods

### Method 1: Azure Portal

1. Navigate to the resource or resource group
2. Select **Move** → **Move to another resource group** (or subscription/region)
3. Select target resource group
4. Review and confirm

### Method 2: Azure CLI

```bash
# Move VM to another resource group
az resource move \
  --destination-group "RG2" \
  --ids "/subscriptions/{sub-id}/resourceGroups/RG1/providers/Microsoft.Compute/virtualMachines/VM1"
```

### Method 3: Azure PowerShell

```powershell
# Move VM to another resource group
Move-AzResource -DestinationResourceGroupName "RG2" `
  -ResourceId "/subscriptions/{sub-id}/resourceGroups/RG1/providers/Microsoft.Compute/virtualMachines/VM1"
```

### Method 4: Azure Resource Mover (for cross-region moves)

For moving resources across regions, use the dedicated Azure Resource Mover service in the portal, which provides a guided experience with dependency tracking.

---

## Comparison: Resource Movement Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **Azure Resource Mover** | Move Azure-native resources between RGs, subscriptions, regions | VM1 is in Azure and needs to move to RG2 |
| **Azure Migrate** | Assess and migrate on-premises workloads TO Azure | VM2 is on-premises and needs to move to Azure |
| **Azure Arc** | Manage on-premises/multi-cloud resources FROM Azure | Manage VM2 from Azure portal without migrating |
| **Azure Lighthouse** | Cross-tenant resource management for service providers | MSP managing customer Azure resources |
| **Data Migration Assistant (DMA)** | Database schema and data migration assessment | SQL Server database migration analysis |

---

## Exam Scenario: Moving Azure VM Between Resource Groups

### Scenario

**Given:**
| Name | Type | Resource Group |
|------|------|----------------|
| VM1 | Azure virtual machine | RG1 |
| VM2 | On-premises virtual machine | Not applicable |

You create a new resource group in Azure named **RG2**.

You need to move the virtual machines to RG2.

**Question:** What should you use to move **VM1**?

### Answer: Azure Resource Mover

**Why this is correct:**
- Azure Resource Mover is a native Azure service specifically designed to move Azure resources
- VM1 is an **Azure virtual machine** currently in RG1
- Azure Resource Mover enables relocation to RG2 without downtime
- Maintains dependencies like virtual networks and disks

**Why other options are incorrect:**

| Option | Reason for Incorrectness |
|--------|-------------------------|
| **Azure Arc** | Used to manage on-premises or multi-cloud resources (like VM2) from within Azure. Does NOT facilitate moving Azure-native resources between resource groups |
| **Azure Lighthouse** | Allows service providers to manage customer tenants. Does NOT support moving resources within a subscription |
| **Azure Migrate** | Designed for assessing and migrating **on-premises** workloads TO Azure, NOT for moving resources already in Azure |
| **Data Migration Assistant (DMA)** | Used to analyze and migrate **database** workloads, not Azure VMs or infrastructure resources |

---

## Key Distinctions to Remember

### Azure Resource Mover vs Azure Migrate

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ON-PREMISES                           AZURE                               │
│                                                                              │
│   ┌─────────┐                          ┌─────────────────────────────────┐  │
│   │   VM2   │                          │                                 │  │
│   │ (On-prem)│                          │   ┌─────────┐     ┌─────────┐  │  │
│   └────┬────┘                          │   │   VM1   │     │   VM1   │  │  │
│        │                               │   │  (RG1)  │────►│  (RG2)  │  │  │
│        │  Azure Migrate                │   └─────────┘     └─────────┘  │  │
│        │  (On-prem TO Azure)           │        Azure Resource Mover     │  │
│        │                               │        (Within Azure)           │  │
│        ▼                               │                                 │  │
│   ┌─────────┐                          │                                 │  │
│   │ VM2 now │                          │                                 │  │
│   │in Azure │                          │                                 │  │
│   └─────────┘                          └─────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Azure Migrate = Move TO Azure (from on-premises)
Azure Resource Mover = Move WITHIN Azure (between RGs, subscriptions, regions)
```

---

## Move Restrictions

Not all resources can be moved. Common restrictions include:

- **Azure AD resources** cannot be moved
- **Some resources require the VM to be stopped** before moving
- **Region-specific resources** may have restrictions for cross-region moves
- **Classic deployment resources** have limited move support

Always check the [Move operation support for resources](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-support-resources) documentation for specific resource types.

---

## Best Practices

1. **Validate First**: Always run validation before moving resources
2. **Check Dependencies**: Understand resource dependencies (NICs, disks, etc.)
3. **Plan Downtime**: Some moves may require brief downtime
4. **Update References**: Update any scripts, automation, or applications that reference old resource paths
5. **Test After Move**: Verify resources work correctly in the new location

---

## References

- [Azure Resource Mover Overview](https://learn.microsoft.com/en-us/azure/resource-mover/overview)
- [Move resources to a new resource group or subscription](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-resource-group-and-subscription)
- [Move operation support for resources](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-support-resources)
- [Azure Arc Overview](https://learn.microsoft.com/en-us/azure/azure-arc/overview)
- [Azure Lighthouse Overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Azure Migrate Overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-overview)
- [Data Migration Assistant Overview](https://learn.microsoft.com/en-us/sql/dma/dma-overview)
