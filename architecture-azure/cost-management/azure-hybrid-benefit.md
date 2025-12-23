# Azure Hybrid Benefit

## Table of Contents

- [Overview](#overview)
- [What is Azure Hybrid Benefit?](#what-is-azure-hybrid-benefit)
- [Supported Products and Services](#supported-products-and-services)
  - [Windows Server](#windows-server)
  - [SQL Server](#sql-server)
  - [Linux (RHEL and SLES)](#linux-rhel-and-sles)
  - [Azure Kubernetes Service (AKS)](#azure-kubernetes-service-aks)
- [Eligibility Requirements](#eligibility-requirements)
- [License Conversion Rules](#license-conversion-rules)
- [How to Enable Azure Hybrid Benefit](#how-to-enable-azure-hybrid-benefit)
  - [Windows Server VMs](#windows-server-vms)
  - [SQL Server VMs](#sql-server-vms)
  - [Linux VMs](#linux-vms)
  - [Centrally Managed Azure Hybrid Benefit](#centrally-managed-azure-hybrid-benefit)
- [Cost Savings](#cost-savings)
- [Combining with Other Discounts](#combining-with-other-discounts)
- [Best Practices](#best-practices)
- [Common Scenarios](#common-scenarios)
- [Limitations](#limitations)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure Hybrid Benefit is a licensing benefit that helps you significantly reduce the costs of running workloads in the cloud. It allows you to use your on-premises licenses with Software Assurance or qualifying subscription licenses on Azure, paying only for infrastructure costs instead of both infrastructure and software licensing costs.

---

## What is Azure Hybrid Benefit?

**Azure Hybrid Benefit** is a cost-saving program that enables you to:

- **Bring Your Own License (BYOL)**: Use existing on-premises licenses with active Software Assurance on Azure
- **Reduce Costs**: Save up to 40% on Windows VMs, up to 55% on SQL Server, and significant savings on Linux workloads
- **Maximize Investment**: Get more value from existing license investments during cloud migration
- **Flexible Management**: Enable or disable at any time without downtime

### Key Benefits

| Benefit | Description |
|---------|-------------|
| 💰 **Cost Savings** | Significant reduction in compute costs |
| 🔄 **Flexibility** | Switch between license models without redeployment |
| ⚡ **No Downtime** | Changes take effect immediately |
| 📈 **Stackable** | Can be combined with Reserved Instances for additional savings |
| 🌐 **Broad Coverage** | Applies to VMs, SQL Database, AKS, and more |

---

## Supported Products and Services

### Windows Server

Azure Hybrid Benefit for Windows Server allows you to use your on-premises Windows Server licenses to get Windows VMs on Azure at a reduced cost.

**Supported Editions**:
- Windows Server Datacenter
- Windows Server Standard

**Supported Azure Services**:
- Azure Virtual Machines
- Azure Virtual Machine Scale Sets
- Azure Dedicated Hosts
- Azure Local (formerly Azure Stack HCI)
- Azure Kubernetes Service (AKS)

**License Conversion**:
```
Windows Server Datacenter (with SA):
├─ 16 core licenses → Unlimited Windows Server VMs on Azure
├─ Dual-use rights: Run on-premises AND in Azure
└─ No limit on number of VMs

Windows Server Standard (with SA):
├─ 16 core licenses → 2 VMs with up to 8 cores each
├─ OR 1 VM with up to 16 cores
└─ Must choose: On-premises OR Azure (no dual-use)
```

### SQL Server

Azure Hybrid Benefit for SQL Server provides discounts on SQL licensing costs when using existing licenses with Software Assurance.

**Supported Editions**:
- SQL Server Enterprise
- SQL Server Standard

**Supported Azure Services**:
- SQL Server on Azure VMs
- Azure SQL Database (vCore-based)
- Azure SQL Managed Instance
- Azure SQL Elastic Pools
- Azure Data Factory (SSIS)

**Additional SQL Server Benefits**:
```
Free Passive Secondary Replicas:
├─ 1 free passive secondary for High Availability (HA)
├─ 1 free passive secondary for Disaster Recovery (DR)
└─ Cuts licensing cost for Always On deployments by more than half
```

### Linux (RHEL and SLES)

Azure Hybrid Benefit for Linux allows you to switch between pay-as-you-go (PAYG) and bring-your-own-subscription (BYOS) billing models.

**Supported Distributions**:
- Red Hat Enterprise Linux (RHEL)
- SUSE Linux Enterprise Server (SLES)

**Supported Azure Services**:
- Azure Virtual Machines
- Azure Virtual Machine Scale Sets
- Azure Spot Virtual Machines
- Custom Images

**RHEL License Types**:
| License Type | Description |
|--------------|-------------|
| `RHEL_BASE` | Standard RHEL |
| `RHEL_EUS` | Extended Update Support |
| `RHEL_SAPAPPS` | SAP Applications |
| `RHEL_SAPHA` | SAP HA |
| `RHEL_BASESAPAPPS` | Base + SAP Applications |
| `RHEL_BASESAPHA` | Base + SAP HA |
| `RHEL_BYOS` | Bring Your Own Subscription |

**SLES License Types**:
| License Type | Description |
|--------------|-------------|
| `SLES` | Standard SLES |
| `SLES_SAP` | SLES for SAP |
| `SLES_HPC` | SLES for HPC |
| `SLES_BYOS` | Bring Your Own Subscription |

### Azure Kubernetes Service (AKS)

Azure Hybrid Benefit for AKS enables you to use your on-premises Windows Server licenses for Windows node pools.

**Requirements**:
- Windows Server licenses with active Software Assurance
- Follows the same licensing guidance as Windows Server VMs

---

## Eligibility Requirements

### Windows Server Requirements

| Requirement | Details |
|-------------|---------|
| **License Type** | Windows Server Datacenter or Standard core licenses |
| **Software Assurance** | Active Software Assurance or qualifying subscription |
| **Minimum Cores** | 8 core licenses per VM (minimum) |
| **Processor Licenses** | 1 processor license = 16 core licenses |

### SQL Server Requirements

| Requirement | Details |
|-------------|---------|
| **License Type** | SQL Server Enterprise or Standard core licenses |
| **Software Assurance** | Active Software Assurance or core subscription licenses |
| **Licensing Model** | Core-based licensing only (Server+CAL not eligible for AHB features) |
| **IaaS Registration** | SQL VMs must be registered with SQL IaaS Agent Extension |

### Linux Requirements

**Red Hat (RHEL)**:
1. Active or unused RHEL subscriptions eligible for use in Azure
2. Subscriptions enabled via [Red Hat Cloud Access](https://www.redhat.com/en/technologies/cloud-computing/cloud-access) program

**SUSE (SLES)**:
1. Registration with SUSE public cloud program
2. VMs registered with a separate update source

---

## License Conversion Rules

### Windows Server License Conversion

```
Standard Edition:
├─ 16 core licenses → 2 VMs (up to 8 cores each)
├─ 24 core licenses → 3 VMs (up to 8 cores each)
├─ For larger VMs: Allocate licenses equal to VM core count
└─ Example: 12-core VM requires 12 core licenses

Datacenter Edition:
├─ 16 core licenses → Unlimited VMs in Azure
├─ Dual-use rights (run on-premises AND Azure simultaneously)
└─ Best for high-density virtualization scenarios
```

### SQL Server License Conversion

```
SQL Server Enterprise:
├─ 4 core licenses → 4 vCores in Azure SQL
├─ Includes unlimited virtualization rights
└─ Maximum discount: ~55% off pay-as-you-go

SQL Server Standard:
├─ 4 core licenses → 4 vCores in Azure SQL
├─ Limited to licensed servers
└─ Maximum discount: ~49% off pay-as-you-go
```

---

## How to Enable Azure Hybrid Benefit

### Windows Server VMs

**Azure Portal**:
1. Navigate to your VM in the Azure portal
2. Go to **Configuration** > **Licensing**
3. Select **Azure Hybrid Benefit**
4. Confirm you have eligible licenses with Software Assurance

**Azure CLI**:
```bash
# Enable Azure Hybrid Benefit on a Windows VM
az vm update \
  --resource-group myResourceGroup \
  --name myVM \
  --license-type Windows_Server

# Disable Azure Hybrid Benefit
az vm update \
  --resource-group myResourceGroup \
  --name myVM \
  --license-type None
```

**PowerShell**:
```powershell
# Enable Azure Hybrid Benefit
$vm = Get-AzVM -ResourceGroupName "myResourceGroup" -Name "myVM"
$vm.LicenseType = "Windows_Server"
Update-AzVM -ResourceGroupName "myResourceGroup" -VM $vm

# Check current license type
(Get-AzVM -ResourceGroupName "myResourceGroup" -Name "myVM").LicenseType
```

### SQL Server VMs

**Prerequisites**:
- VM registered with SQL IaaS Agent Extension
- Software Assurance for SQL Server licenses

**Azure Portal**:
1. Navigate to your SQL VM
2. Go to **Configure** > **SQL Server License**
3. Select **Azure Hybrid Benefit**
4. Save changes

**Azure CLI**:
```bash
# Enable Azure Hybrid Benefit for SQL Server
az sql vm update \
  --resource-group myResourceGroup \
  --name mySqlVM \
  --license-type AHUB

# Use pay-as-you-go licensing
az sql vm update \
  --resource-group myResourceGroup \
  --name mySqlVM \
  --license-type PAYG
```

### Linux VMs

**Azure Portal**:
1. Navigate to the VM
2. Go to **Operating System** > **Licensing**
3. Select **Yes** to enable Azure Hybrid Benefit
4. Confirm subscription eligibility

**Azure CLI for RHEL**:
```bash
# Install the extension (required for RHEL)
az vm extension set \
  --resource-group myResourceGroup \
  --vm-name myVM \
  --name AHBForRHEL \
  --publisher Microsoft.Azure.AzureHybridBenefit

# Enable BYOS for RHEL
az vm update \
  --resource-group myResourceGroup \
  --name myVM \
  --license-type RHEL_BYOS
```

**Azure CLI for SLES**:
```bash
# Enable BYOS for SLES (no extension needed)
az vm update \
  --resource-group myResourceGroup \
  --name myVM \
  --license-type SLES_BYOS
```

### Centrally Managed Azure Hybrid Benefit

For SQL Server, you can manage Azure Hybrid Benefit at the subscription or billing account level instead of per resource.

**Prerequisites**:
- Enterprise Agreement or Microsoft Customer Agreement
- Appropriate billing role (Enterprise Administrator, Billing Account Owner, etc.)
- SQL VMs registered with SQL IaaS Agent Extension

**Supported Agreement Types**:
| Agreement Type | Required Role | Supported Offer |
|----------------|---------------|-----------------|
| Enterprise Agreement | Enterprise Administrator (full access) | MS-AZR-0017P |
| Microsoft Customer Agreement | Billing account/profile owner or contributor | MS-AZR-0017G |

**Not Available For**:
- WebDirect / Pay-as-you-go
- CSP / Partner-led customers
- Sponsored or MSDN subscriptions

---

## Cost Savings

### Windows Server Savings

```
Example: D4s v3 VM (4 vCPUs, 16 GB RAM)

Pay-as-you-go:                    $280/month
With Azure Hybrid Benefit:        $168/month → 40% savings
With AHB + 3-year Reserved:       $100/month → 64% savings

Annual savings per VM: $2,160 (AHB + 3-year RI)
```

### SQL Server Savings

```
Example: SQL Server Enterprise on D8s v3 VM

Pay-as-you-go:                    $1,500/month
With Azure Hybrid Benefit:        $675/month → 55% savings
With AHB + 3-year Reserved:       $400/month → 73% savings

Annual savings per VM: $13,200 (AHB + 3-year RI)
```

### Linux Savings

```
Example: RHEL D2s v5 VM

Pay-as-you-go:                    $150/month
With Azure Hybrid Benefit (BYOS): $95/month → 37% savings
With AHB + 3-year Reserved:       $36/month → 76% savings

Annual savings per VM: $1,368 (AHB + 3-year RI)
```

---

## Combining with Other Discounts

Azure Hybrid Benefit can be combined with other cost optimization strategies for maximum savings:

### Combination Strategies

```
Strategy                              Typical Combined Savings
─────────────────────────────────────────────────────────────
AHB + 1-year Reserved Instance        → Up to 53%
AHB + 3-year Reserved Instance        → Up to 73%
AHB + Reserved + Dev/Test Pricing     → Up to 80%
AHB + Spot VMs (dev/test only)        → Up to 90%
```

### Savings Stack Example

```
Base Cost (Windows VM): $1,000/month

Apply Azure Hybrid Benefit:
└─ $1,000 × 0.60 = $600/month (40% savings)

Apply 3-year Reserved Instance:
└─ $600 × 0.50 = $300/month (additional 50% savings)

Apply Dev/Test Pricing (if eligible):
└─ $300 × 0.80 = $240/month (additional 20% savings)

Total Savings: $760/month = 76%
```

---

## Best Practices

### License Management

✅ **Inventory Your Licenses**: Document all Windows Server and SQL Server licenses with Software Assurance  
✅ **Track Assignments**: Maintain records of which licenses are assigned to which Azure resources  
✅ **Monitor Expiration**: Set reminders for Software Assurance renewal dates  
✅ **Use Central Management**: Consider centrally managed AHB for SQL Server at scale  

### Compliance

✅ **Stay Compliant**: Ensure you have valid Software Assurance before enabling  
✅ **Verify Eligibility**: Only core-based SQL Server licenses qualify (not Server+CAL)  
✅ **Document Usage**: Keep records for audit purposes  
✅ **Disable Before Expiry**: Disable AHB before Software Assurance expires  

### Optimization

✅ **Combine with Reserved Instances**: Stack AHB with RIs for maximum savings  
✅ **Right-Size First**: Optimize VM sizes before applying AHB  
✅ **Use Azure Pricing Calculator**: Estimate savings before migration  
✅ **Review Periodically**: Reassess license assignments quarterly  

---

## Common Scenarios

### Scenario 1: Windows Server Migration

> **Situation**: A company is migrating 50 Windows Server VMs from on-premises to Azure. They have Windows Server Datacenter licenses with active Software Assurance for 100 cores.
>
> **Solution**: Enable Azure Hybrid Benefit on all 50 VMs. With Datacenter licenses, they have unlimited VM rights and dual-use capability.
>
> **Savings**: ~40% reduction in Windows VM costs = approximately $10,000/month

### Scenario 2: SQL Server on Azure VMs

> **Situation**: An organization needs to run SQL Server Enterprise on Azure VMs for a production database cluster with Always On availability groups.
>
> **Solution**: 
> 1. Enable Azure Hybrid Benefit for SQL Server
> 2. Leverage free passive secondary replica for HA
> 3. Leverage free passive secondary for DR
>
> **Savings**: ~55% on SQL licensing + free HA/DR replicas = significant cost reduction

### Scenario 3: Linux RHEL Workloads

> **Situation**: A company with existing Red Hat subscriptions wants to migrate RHEL workloads to Azure.
>
> **Solution**:
> 1. Enable Red Hat Cloud Access
> 2. Deploy VMs from PAYG images
> 3. Convert to BYOS using Azure Hybrid Benefit
>
> **Savings**: Pay only for infrastructure, use existing RHEL subscriptions

### Scenario 4: Ubuntu Migration (NOT Eligible)

> **Situation**: An application hosted on Ubuntu is being migrated to Azure.
>
> **Important**: Azure Hybrid Benefit does **NOT** apply to Ubuntu or most Linux distributions outside of RHEL and SLES.
>
> **Alternative**: Use Azure Reservations for cost optimization instead.

---

## Limitations

### Windows Server Limitations

| Limitation | Details |
|------------|---------|
| Minimum Cores | 8 core licenses required per VM (minimum) |
| Standard Edition | No dual-use rights (choose on-premises OR Azure) |
| Expiration | Must renew SA or disable AHB before term ends |
| Classic VMs | Only ARM-deployed VMs supported |

### SQL Server Limitations

| Limitation | Details |
|------------|---------|
| Edition Support | Only Standard and Enterprise (not Express, Web, Developer, Evaluation) |
| Licensing Model | Only core-based licensing (not Server+CAL for AHB features) |
| IaaS Extension | SQL VMs must be registered with SQL IaaS Agent Extension |
| Classic VMs | Only ARM-deployed VMs supported |

### Linux Limitations

| Limitation | Details |
|------------|---------|
| Supported Distros | Only RHEL and SLES (not Ubuntu, CentOS, Debian, etc.) |
| Cloud Access | RHEL requires Red Hat Cloud Access enrollment |
| Registration | SLES requires SUSE public cloud program registration |
| Dedicated Hosts | Not eligible if already using AHB for Windows |

---

## Practice Questions

### Question 1: Identifying AHB Eligibility

**Scenario**: Contoso has the following licenses with active Software Assurance:
- Windows Server Standard (64 cores)
- SQL Server Enterprise (32 cores)
- Red Hat Enterprise Linux subscriptions
- Ubuntu Pro subscriptions

Which workloads can benefit from Azure Hybrid Benefit?

**Answer**: Windows Server VMs, SQL Server VMs, and RHEL VMs can use Azure Hybrid Benefit. Ubuntu is NOT eligible for Azure Hybrid Benefit.

---

### Question 2: License Calculation

**Scenario**: You have 48 Windows Server Standard core licenses with Software Assurance. How many 8-core Azure VMs can you run with Azure Hybrid Benefit?

**Answer**: 
- 48 core licenses ÷ 8 cores per VM = 6 VMs
- You can run 6 Azure VMs with up to 8 cores each

---

### Question 3: SQL Server HA/DR Benefits

**Scenario**: A company is deploying SQL Server Enterprise on Azure VMs with Always On availability groups. They need:
- 1 primary replica
- 1 synchronous secondary for HA
- 1 asynchronous secondary for DR

How does Azure Hybrid Benefit help with licensing costs?

**Answer**: With Azure Hybrid Benefit:
- Pay for licensing on the primary replica only
- 1 free passive secondary replica for HA
- 1 free passive secondary replica for DR
- This reduces SQL Server licensing costs by more than 50%

---

### Question 4: Combining Cost Optimization

**Scenario**: What is the maximum cost savings achievable by combining Azure Hybrid Benefit with other discount strategies for a Windows Server VM running a production workload?

**Answer**: 
- Azure Hybrid Benefit: ~40% savings
- 3-year Reserved Instance: Additional ~50% on remaining cost
- Combined: Up to ~73% total savings

For dev/test workloads with Dev/Test pricing, savings can reach ~80%.

---

## References

### Official Documentation

- [Azure Hybrid Benefit Overview](https://azure.microsoft.com/pricing/hybrid-benefit/)
- [Azure Hybrid Benefit for Windows Server](https://learn.microsoft.com/azure/virtual-machines/windows/hybrid-use-benefit-licensing)
- [Azure Hybrid Benefit for SQL Server](https://learn.microsoft.com/azure/azure-sql/azure-hybrid-benefit)
- [Azure Hybrid Benefit for Linux](https://learn.microsoft.com/azure/virtual-machines/linux/azure-hybrid-benefit-linux)
- [Azure Hybrid Benefit for AKS](https://learn.microsoft.com/azure/aks/azure-hybrid-benefit)
- [Centrally Managed Azure Hybrid Benefit for SQL Server](https://learn.microsoft.com/azure/cost-management-billing/scope-level/overview-azure-hybrid-benefit-scope)

### Pricing and Calculators

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure Hybrid Benefit Savings Calculator](https://azure.microsoft.com/pricing/hybrid-benefit/#calculator)

### Licensing Resources

- [Microsoft Licensing Resources](https://www.microsoft.com/licensing/default)
- [Microsoft Product Terms](https://www.microsoft.com/licensing/terms/productoffering/MicrosoftAzure)
- [Windows Server Product Licensing](https://www.microsoft.com/licensing/product-licensing/windows-server)
- [Red Hat Cloud Access](https://www.redhat.com/en/technologies/cloud-computing/cloud-access)
- [SUSE Public Cloud Program](https://www.suse.com/products/public-cloud/)

---

## Summary

| Aspect | Windows Server | SQL Server | Linux (RHEL/SLES) |
|--------|----------------|------------|-------------------|
| **Savings** | Up to 40% | Up to 55% | Up to 37% |
| **Requirement** | Software Assurance | Software Assurance | Cloud Access/Registration |
| **Dual-Use** | Datacenter only | N/A | N/A |
| **Minimum** | 8 cores/VM | N/A | N/A |
| **Combined w/ RI** | Up to 73% | Up to 73% | Up to 76% |
| **Free HA/DR** | No | Yes (passive replicas) | No |
