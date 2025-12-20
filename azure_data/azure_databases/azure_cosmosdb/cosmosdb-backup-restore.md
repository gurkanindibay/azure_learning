# Azure Cosmos DB Backup and Restore

## Overview

Azure Cosmos DB provides built-in backup capabilities to protect your data. There are two primary backup modes available: **Continuous backup** and **Periodic backup**. Understanding the differences between these options is crucial for designing your data protection strategy.

## Backup Modes Comparison

| Feature | Continuous Backup | Periodic Backup |
|---------|-------------------|-----------------|
| **Restore granularity** | Point-in-time (any second) | Last available backup only |
| **Retention period** | 7 days or 30 days (configurable) | Configurable (hours/days) |
| **Restore method** | Self-service via Azure Portal/CLI/PowerShell | Support ticket required |
| **Recovery Point Objective (RPO)** | Seconds | Hours (depends on interval) |
| **Cost** | Additional storage cost for change history | Included (limited retention) |
| **Serverless support** | ❌ No | ✅ Yes |
| **Provisioned throughput support** | ✅ Yes | ✅ Yes |

## Continuous Backup (Point-in-Time Restore)

### What is Continuous Backup?

Continuous backup automatically maintains a continuous backup of your data, allowing you to restore to **any point in time** within the retention period. This is a **self-service** solution that doesn't require opening a support ticket.

### Key Features

- **Point-in-time restore (PITR)**: Restore data to any second within the retention window
- **Self-service restoration**: Restore directly from Azure Portal, CLI, or PowerShell
- **Two retention tiers**:
  - **7-day retention**: Lower cost option
  - **30-day retention**: Extended protection for compliance requirements
- **Automatic backup**: No manual intervention required
- **Granular recovery**: Restore entire account, database, or container

### Supported APIs

Continuous backup supports all Azure Cosmos DB APIs:
- ✅ NoSQL (Core) API
- ✅ MongoDB API
- ✅ Cassandra API
- ✅ Gremlin API
- ✅ Table API

### Limitations

- ❌ **Not available for Serverless accounts** (only Provisioned throughput)
- ❌ Cannot restore to the same account (must restore to a new account)
- ❌ Some features may have limited support during preview

### When to Use Continuous Backup

- Applications requiring **low RPO** (Recovery Point Objective)
- Scenarios where you need to restore to a **specific point in time**
- **Self-service** restoration requirements without waiting for support
- Compliance requirements mandating **30-day retention**
- Protection against **accidental deletions** or **data corruption**

## Periodic Backup

### What is Periodic Backup?

Periodic backup takes full backups of your data at regular intervals. This is the default backup mode and is included at no additional cost.

### Key Features

- **Scheduled backups**: Configurable backup interval (minimum 1 hour)
- **Configurable retention**: Set number of backup copies to retain
- **Geo-redundant storage**: Backups stored in geo-redundant storage by default
- **Included cost**: No additional charge for backup storage (with limits)

### Limitations

- ❌ **Support ticket required** for restoration
- ❌ Can only restore to the **last available backup**
- ❌ No point-in-time granularity
- ❌ Longer **RTO** (Recovery Time Objective) due to support process

### When to Use Periodic Backup

- Cost-sensitive scenarios where continuous backup overhead is not justified
- Applications with **less stringent RPO requirements**
- Serverless accounts (only option available)
- Development/test environments

## Why NOT Azure Backup or MARS for Cosmos DB?

### Azure Backup

**Azure Backup** is designed for:
- Azure Virtual Machines
- Azure Files
- SQL Server in Azure VMs
- SAP HANA databases
- Azure Blobs

❌ **Azure Backup does NOT support Azure Cosmos DB directly**. Cosmos DB has its own built-in backup mechanisms.

### Microsoft Azure Recovery Services (MARS) Agent

**MARS Agent** is designed for:
- On-premises Windows servers
- Windows client machines
- Azure VMs (file/folder level backup)

❌ **MARS is not applicable to Azure Cosmos DB**. It's a file-based backup solution for Windows systems.

## Exam Scenario

> **Question**: You have an Azure solution that uses the Azure Cosmos DB for MongoDB API. You need to ensure that you can restore data in the solution to any point in time from the last 30 days by using a self-service solution. Which backup solution should you use?

| Option | Correct? | Explanation |
|--------|----------|-------------|
| Azure Backup | ❌ | Azure Backup doesn't support Cosmos DB. It's designed for VMs, Azure Files, and SQL databases in VMs. |
| **Azure Cosmos DB Continuous backup** | ✅ | Continuous backup provides point-in-time restore capability with 30-day retention and is a self-service solution. |
| Microsoft Azure Recovery Services (MARS) | ❌ | MARS is for backing up files and folders from Windows machines, not for PaaS services like Cosmos DB. |
| Azure Cosmos DB Periodic backup | ❌ | Periodic backup only allows restoration to the last backup point, not to any point in time. Also requires a support ticket (not self-service). |

### Key Decision Factors

The question specifies three critical requirements:
1. **Point-in-time restore** → Only Continuous backup provides this
2. **30-day retention** → Continuous backup supports 7-day or 30-day tiers
3. **Self-service solution** → Continuous backup allows self-service restore; Periodic requires support ticket

## Configuration

### Enabling Continuous Backup (Azure CLI)

```bash
# Create a new account with continuous backup (30-day retention)
az cosmosdb create \
    --name mycosmosaccount \
    --resource-group myResourceGroup \
    --backup-policy-type Continuous \
    --continuous-tier Continuous30Days \
    --locations regionName=eastus

# Update existing account to continuous backup
az cosmosdb update \
    --name mycosmosaccount \
    --resource-group myResourceGroup \
    --backup-policy-type Continuous \
    --continuous-tier Continuous30Days
```

### Point-in-Time Restore (Azure CLI)

```bash
# Restore to a specific point in time
az cosmosdb restore \
    --target-database-account-name restoredaccount \
    --account-name mycosmosaccount \
    --resource-group myResourceGroup \
    --restore-timestamp "2024-01-15T10:30:00Z" \
    --location eastus
```

## Best Practices

1. **Choose backup mode based on RPO requirements**
   - Critical data: Continuous backup with 30-day retention
   - Non-critical data: Periodic backup may suffice

2. **Test restore procedures regularly**
   - Validate that restores work as expected
   - Document the restore process

3. **Consider multi-region deployments**
   - Combine backup with multi-region writes for maximum availability

4. **Monitor backup status**
   - Use Azure Monitor to track backup operations
   - Set up alerts for backup failures

## Summary

| Requirement | Recommended Solution |
|-------------|---------------------|
| Point-in-time restore | Continuous backup |
| Self-service restore | Continuous backup |
| 30-day retention | Continuous backup (Continuous30Days tier) |
| Lowest cost | Periodic backup |
| Serverless accounts | Periodic backup (only option) |
| Compliance requirements | Continuous backup with 30-day retention |

---

## Related Topics

- [Cosmos DB Capacity Modes](./cosmosdb-capacity-modes.md)
- [Cosmos DB Multi-Region Configurations](./cosmosdb-multi-region-configurations.md)
- [Cosmos DB API Comparison](./cosmosdb-api-comparison.md)
