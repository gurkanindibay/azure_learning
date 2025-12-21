# Azure Data Backup Solutions - Comprehensive Comparison

## Table of Contents

- [Overview](#overview)
- [Executive Summary](#executive-summary)
- [Backup Solutions by Data Service](#backup-solutions-by-data-service)
  - [Azure SQL Database](#azure-sql-database)
  - [Azure SQL Managed Instance](#azure-sql-managed-instance)
  - [SQL Server on Azure VMs](#sql-server-on-azure-vms)
  - [Azure Cosmos DB](#azure-cosmos-db)
  - [Azure Database for MySQL](#azure-database-for-mysql)
  - [Azure Database for PostgreSQL](#azure-database-for-postgresql)
  - [Azure Blob Storage](#azure-blob-storage)
  - [Azure Files](#azure-files)
    - [Backup Storage Location](#backup-storage-location)
    - [Key Differences: Recovery Services Vault vs Backup Vault](#key-differences-recovery-services-vault-vs-backup-vault)
  - [Azure Cache for Redis](#azure-cache-for-redis)
  - [Azure Data Explorer](#azure-data-explorer)
  - [Azure Data Lake Storage Gen2](#azure-data-lake-storage-gen2)
- [Master Comparison Table](#master-comparison-table)
- [Backup Tools Comparison](#backup-tools-comparison)
  - [Azure Backup](#azure-backup)
  - [Azure Site Recovery](#azure-site-recovery)
  - [MARS Agent](#mars-agent)
  - [Native Service Backups](#native-service-backups)
- [Recovery Objectives Comparison](#recovery-objectives-comparison)
- [Decision Matrix](#decision-matrix)
- [Best Practices](#best-practices)
- [Exam Tips](#exam-tips)

---

## Overview

Azure provides various backup and data protection solutions across its data services. The backup approach differs significantly based on whether the service is:

- **PaaS (Platform as a Service)**: Built-in backup mechanisms managed by Azure
- **IaaS (Infrastructure as a Service)**: Requires explicit backup configuration

This document compares backup solutions across all major Azure data services to help you choose the right protection strategy.

---

## Executive Summary

| Data Service | Primary Backup Solution | Self-Service Restore | Max Retention | PITR Support |
|--------------|------------------------|---------------------|---------------|--------------|
| **Azure SQL Database** | Automated backups | ✅ Yes | 35 days (10 years LTR) | ✅ Yes |
| **Azure SQL Managed Instance** | Automated backups | ✅ Yes | 35 days (10 years LTR) | ✅ Yes |
| **SQL Server on Azure VMs** | Azure Backup | ✅ Yes | 99 years | ✅ Yes |
| **Azure Cosmos DB** | Continuous/Periodic backup | ✅/❌ | 30 days (continuous) | ✅ Continuous only |
| **Azure MySQL Flexible Server** | Geo-redundant backup | ❌ (manual restore) | 35 days | ✅ Yes |
| **Azure PostgreSQL Flexible Server** | Geo-redundant backup | ❌ (manual restore) | 35 days | ✅ Yes |
| **Azure Blob Storage** | Azure Backup for Blobs | ✅ Yes | 360 days | ✅ Yes |
| **Azure Files** | Azure Backup | ✅ Yes | 99 years | ❌ Snapshot-based |
| **Azure Cache for Redis** | Data persistence (RDB/AOF) | ✅ Yes | N/A (manual) | ❌ No |
| **Azure Data Explorer** | Follower databases/Export | ✅ Yes | Configurable | ❌ No |
| **Azure Data Lake Gen2** | Azure Backup for Blobs | ✅ Yes | 360 days | ✅ Yes |

---

## Backup Solutions by Data Service

### Azure SQL Database

#### Built-in Automated Backups

Azure SQL Database provides **fully automated backups** without any additional configuration required.

| Backup Type | Frequency | Purpose |
|-------------|-----------|---------|
| **Full Backup** | Weekly | Complete database backup |
| **Differential Backup** | Every 12-24 hours | Changes since last full |
| **Transaction Log Backup** | Every 5-10 minutes | Continuous protection |

#### Backup Features

| Feature | Details |
|---------|---------|
| **Default Retention** | 7 days |
| **Maximum Retention** | 35 days (standard), 10 years (LTR) |
| **Point-in-Time Restore (PITR)** | ✅ Any second within retention |
| **Self-Service Restore** | ✅ Azure Portal, CLI, PowerShell |
| **Geo-Redundant Backup** | ✅ Available (configurable) |
| **Long-Term Retention (LTR)** | ✅ Up to 10 years |
| **Cross-Region Restore** | ✅ With geo-redundant backup |

#### Backup Storage Redundancy Options

| Redundancy | Description | Use Case |
|------------|-------------|----------|
| **LRS** | Locally redundant | Dev/test, cost optimization |
| **ZRS** | Zone-redundant | Regional high availability |
| **GRS** | Geo-redundant | Cross-region disaster recovery |
| **RA-GRS** | Read-access geo-redundant | Cross-region DR with read access |

#### Point-in-Time Restore

```bash
# Restore to a specific point in time
az sql db restore \
  --dest-name restored-db \
  --name original-db \
  --resource-group myResourceGroup \
  --server myserver \
  --time "2024-01-15T14:30:00Z"
```

#### Long-Term Retention (LTR)

```bash
# Configure LTR policy
az sql db ltr-policy set \
  --resource-group myResourceGroup \
  --server myserver \
  --database mydb \
  --weekly-retention P1W \
  --monthly-retention P1M \
  --yearly-retention P1Y \
  --week-of-year 1
```

---

### Azure SQL Managed Instance

#### Backup Characteristics

Azure SQL Managed Instance shares similar backup capabilities with Azure SQL Database but offers additional flexibility.

| Feature | Details |
|---------|---------|
| **Backup Frequency** | Same as SQL Database (Full/Diff/Log) |
| **Default Retention** | 7 days |
| **Maximum Retention** | 35 days (PITR), 10 years (LTR) |
| **Native Backup Support** | ✅ BACKUP TO URL supported |
| **Copy-Only Backups** | ✅ Supported |
| **Self-Service Restore** | ✅ Yes |

#### Unique Capabilities

- **User-Initiated Backups**: Can perform BACKUP TO URL for copy-only backups
- **Backup to Azure Blob Storage**: Direct backup to storage account
- **Cross-Instance Restore**: Restore to different Managed Instance

```sql
-- Copy-only backup to Azure Blob Storage
BACKUP DATABASE [MyDatabase] 
TO URL = 'https://mystorageaccount.blob.core.windows.net/backups/mydb.bak'
WITH COPY_ONLY;
```

---

### SQL Server on Azure VMs

#### Backup Options

SQL Server on Azure VMs provides the most flexibility for backup strategies since you have full OS and SQL Server access.

| Backup Method | Tool | Best For |
|---------------|------|----------|
| **Azure Backup** | Recovery Services Vault | Recommended approach |
| **Native SQL Backup** | SQL Server Management | Traditional backup approach |
| **Third-Party Tools** | Various | Specific requirements |

#### Azure Backup for SQL Server in Azure VMs

| Feature | Details |
|---------|---------|
| **Backup Frequency** | Every 15 minutes (logs) |
| **RPO** | 15 minutes |
| **Retention** | Up to 99 years |
| **Self-Service Restore** | ✅ Yes |
| **Application-Consistent** | ✅ Yes (uses VSS) |
| **Stream Backup** | ✅ No staging location required |

#### Configuration Steps

```bash
# Register SQL VM with SQL IaaS Agent extension
az sql vm create \
  --name mySqlVM \
  --resource-group myResourceGroup \
  --location eastus \
  --license-type PAYG

# Enable auto-backup
az sql vm update \
  --resource-group myResourceGroup \
  --name mySqlVM \
  --backup-schedule-type Automated \
  --full-backup-frequency Daily \
  --full-backup-start-hour 2 \
  --retention-period 30
```

---

### Azure Cosmos DB

#### Backup Modes Comparison

Azure Cosmos DB offers two distinct backup modes:

| Feature | Continuous Backup | Periodic Backup |
|---------|-------------------|-----------------|
| **Restore Granularity** | Point-in-time (any second) | Last available backup only |
| **Retention Period** | 7 or 30 days (configurable) | Configurable (hours/days) |
| **Restore Method** | ✅ Self-service | ❌ Support ticket required |
| **RPO** | Seconds | Hours |
| **Additional Cost** | Yes (storage for change history) | Included |
| **Serverless Support** | ❌ No | ✅ Yes |
| **Provisioned Throughput** | ✅ Yes | ✅ Yes |

#### Continuous Backup (Point-in-Time Restore)

**Key Features:**
- Restore to **any second** within retention window
- **Self-service** restoration via Portal, CLI, PowerShell
- **Two tiers**: 7-day and 30-day retention
- Supports all Cosmos DB APIs (NoSQL, MongoDB, Cassandra, Gremlin, Table)

**Limitations:**
- ❌ Not available for Serverless accounts
- ❌ Must restore to a **new account** (not same account)

```bash
# Enable continuous backup (30-day retention)
az cosmosdb create \
    --name mycosmosaccount \
    --resource-group myResourceGroup \
    --backup-policy-type Continuous \
    --continuous-tier Continuous30Days

# Point-in-time restore
az cosmosdb restore \
    --target-database-account-name restoredaccount \
    --account-name mycosmosaccount \
    --resource-group myResourceGroup \
    --restore-timestamp "2024-01-15T10:30:00Z"
```

#### Why NOT Azure Backup or MARS for Cosmos DB?

| Tool | Supported for Cosmos DB? | Reason |
|------|-------------------------|--------|
| **Azure Backup** | ❌ No | Designed for VMs, Azure Files, SQL in VMs |
| **MARS Agent** | ❌ No | File-based backup for Windows systems only |
| **Cosmos DB Built-in** | ✅ Yes | Native continuous/periodic backup |

---

### Azure Database for MySQL

#### Flexible Server Backup

| Feature | Details |
|---------|---------|
| **Backup Type** | Automated with geo-redundancy option |
| **Retention** | 1-35 days |
| **Point-in-Time Restore** | ✅ Yes |
| **Geo-Redundant Backup** | ✅ Yes (paired region) |
| **Self-Service Restore** | ❌ Manual restoration required |
| **Cross-Region DR** | ✅ Via geo-redundant backup |

#### Business Continuity Options

| Option | Cross-Region DR | Automatic Failover | Best For |
|--------|-----------------|-------------------|----------|
| **Geo-Redundant Backup** ✅ | Yes | No (manual restore) | Regional DR with minimal complexity |
| **Zone-Redundant HA** | No (same region) | Yes | Within-region high availability |
| **Read Replicas** ❌ | No | No | Read scaling, NOT DR |

#### Configuration

```bash
# Create with geo-redundant backup
az mysql flexible-server create \
  --resource-group myResourceGroup \
  --name myserver \
  --location eastus \
  --backup-retention 35 \
  --geo-redundant-backup Enabled
```

---

### Azure Database for PostgreSQL

#### Flexible Server Backup

Similar to MySQL Flexible Server:

| Feature | Details |
|---------|---------|
| **Backup Type** | Automated with geo-redundancy option |
| **Retention** | 7-35 days |
| **Point-in-Time Restore** | ✅ Yes |
| **Geo-Redundant Backup** | ✅ Yes |
| **Self-Service Restore** | ✅ Yes |

---

### Azure Blob Storage

Azure Blob Storage offers the most comprehensive data protection features among Azure storage services.

#### Data Protection Features

| Feature | Purpose | Prerequisites |
|---------|---------|---------------|
| **Point-in-Time Restore** | Restore containers to earlier state | Versioning, Soft Delete, Change Feed |
| **Soft Delete (Blobs)** | Recover deleted blobs | None |
| **Soft Delete (Containers)** | Recover deleted containers | None |
| **Blob Versioning** | Maintain previous versions | None |
| **Azure Backup for Blobs** | Enterprise backup solution | Backup Vault |
| **Immutable Storage** | WORM compliance | None |

#### Feature Comparison

| Feature | Restores What? | Scope | PITR? |
|---------|---------------|-------|-------|
| **Point-in-Time Restore** | Container data to earlier state | Containers | ✅ Yes |
| **Soft Delete (Blobs)** | Deleted individual blobs | Blobs | ❌ No |
| **Soft Delete (Containers)** | Deleted containers | Containers | ❌ No |
| **Blob Versioning** | Previous blob versions | Blobs | ❌ No |
| **Azure Backup for Blobs** | Operational backup | Account | ✅ Yes |

#### Point-in-Time Restore Prerequisites

```
Point-in-Time Restore requires ALL of the following:
├── Blob Versioning ✅
├── Soft Delete for Blobs ✅
├── Change Feed ✅
└── Block Blobs Only (not append or page blobs)
```

#### Enabling Data Protection Features

```bash
# Enable all data protection features
az storage account blob-service-properties update \
    --account-name mystorageaccount \
    --resource-group myResourceGroup \
    --enable-restore-policy true \
    --restore-days 7 \
    --enable-versioning true \
    --enable-delete-retention true \
    --delete-retention-days 14 \
    --enable-container-delete-retention true \
    --container-delete-retention-days 14 \
    --enable-change-feed true
```

#### Azure Backup for Blobs

| Feature | Operational Backup |
|---------|-------------------|
| **Backup Type** | Continuous (no scheduled jobs) |
| **Retention** | 1-360 days |
| **PITR** | ✅ Yes |
| **Management** | Azure Backup Center |
| **Cross-Region Restore** | ✅ With GRS accounts |

---

### Azure Files

#### Azure Backup for Azure Files

| Feature | Details |
|---------|---------|
| **Backup Type** | Snapshot-based |
| **Frequency** | Up to 4 times per day |
| **Retention** | Up to 99 years |
| **Self-Service Restore** | ✅ Yes |
| **Item-Level Recovery** | ✅ Yes (files/folders) |
| **Cross-Region Restore** | ✅ Yes (with GRS) |

#### Backup Storage Location

To automatically back up Azure file shares, you must use a **Recovery Services vault**.

| Storage Option | Suitable for Azure Files Backup? | Notes |
|---------------|----------------------------------|-------|
| **Recovery Services vault** | ✅ **Yes (Recommended)** | Required for Azure Files backup; stores backup data and manages backup policies |
| **Backup Vault** | ❌ No | Used for newer workloads like Azure Disks, Azure Blobs, Azure Database for PostgreSQL |
| **Azure Files in a second region** | ❌ No | This is replication, not backup; doesn't provide point-in-time recovery |
| **Azure Key Vault** | ❌ No | Used for secrets, keys, and certificates; not for data backup |

> **💡 Exam Tip**: When asked about backing up Azure file shares, always choose **Recovery Services vault**. While Backup Vault is a newer vault type, Azure Files backup specifically requires Recovery Services vault. Don't confuse replication (geo-redundant storage) with backup—they serve different purposes.

#### Key Differences: Recovery Services Vault vs Backup Vault

| Aspect | Recovery Services Vault | Backup Vault |
|--------|------------------------|--------------|
| **Azure Files** | ✅ Supported | ❌ Not supported |
| **Azure VMs** | ✅ Supported | ❌ Not supported |
| **SQL Server in VMs** | ✅ Supported | ❌ Not supported |
| **Azure Disks** | ❌ Not supported | ✅ Supported |
| **Azure Blobs** | ❌ Not supported | ✅ Supported |
| **Azure Database for PostgreSQL** | ❌ Not supported | ✅ Supported |

#### Configuration

```bash
# Enable backup for Azure Files
az backup protection enable-for-azurefileshare \
  --vault-name myRecoveryVault \
  --resource-group myResourceGroup \
  --storage-account mystorageaccount \
  --azure-file-share myfileshare \
  --policy-name DailyBackup
```

---

### Azure Cache for Redis

Azure Cache for Redis uses **data persistence** rather than traditional backups.

#### Data Persistence Options

| Feature | RDB Persistence | AOF Persistence |
|---------|-----------------|-----------------|
| **Description** | Point-in-time snapshots | Append-only file (every write) |
| **Performance Impact** | Low | Higher |
| **Data Loss Risk** | Higher (interval-based) | Lower (near real-time) |
| **Storage Cost** | Lower | Higher |
| **Availability** | Premium, Enterprise | Premium, Enterprise |

#### Configuration

```bash
# Enable RDB persistence
az redis update \
  --name myRedisCache \
  --resource-group myResourceGroup \
  --enable-non-ssl-port false \
  --set "redisConfiguration.rdb-backup-enabled=true" \
  --set "redisConfiguration.rdb-backup-frequency=60"
```

#### Export/Import

```bash
# Export Redis data to blob
az redis export \
  --name myRedisCache \
  --resource-group myResourceGroup \
  --prefix mybackup \
  --container "https://mystorageaccount.blob.core.windows.net/backup"
```

---

### Azure Data Explorer

#### Data Protection Strategies

Azure Data Explorer doesn't have traditional backup but offers:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Follower Databases** | Read-only replica in another cluster | DR, load balancing |
| **Continuous Export** | Export to Storage/Data Lake | Long-term archival |
| **One-Time Export** | Manual export to storage | Point-in-time archival |

#### Continuous Export

```kusto
// Create continuous export
.create-or-alter continuous-export MyExport
over (MyTable)
to table ExternalTable
with
(intervalBetweenRuns=1h)
<| MyTable
```

---

### Azure Data Lake Storage Gen2

Data Lake Gen2 inherits blob storage data protection features:

| Feature | Support |
|---------|---------|
| **Point-in-Time Restore** | ✅ Yes |
| **Soft Delete** | ✅ Yes |
| **Blob Versioning** | ✅ Yes |
| **Azure Backup** | ✅ Yes |
| **Immutable Storage** | ✅ Yes |

> **Note**: Hierarchical namespace (HNS) enabled accounts may have some limitations with certain features like Change Feed.

---

## Master Comparison Table

| Data Service | Backup Tool | Self-Service | PITR | Max Retention | Cross-Region | Cost |
|--------------|-------------|--------------|------|---------------|--------------|------|
| **Azure SQL DB** | Built-in | ✅ | ✅ | 35d / 10y LTR | ✅ | Included |
| **SQL MI** | Built-in | ✅ | ✅ | 35d / 10y LTR | ✅ | Included |
| **SQL VM** | Azure Backup | ✅ | ✅ | 99 years | ✅ | Additional |
| **Cosmos DB** | Built-in | ✅/❌ | ✅ (Continuous) | 30 days | ✅ | Included/Additional |
| **MySQL** | Built-in | ❌ | ✅ | 35 days | ✅ | Included |
| **PostgreSQL** | Built-in | ✅ | ✅ | 35 days | ✅ | Included |
| **Blob Storage** | Multiple | ✅ | ✅ | 365d / 99y | ✅ | Varies |
| **Azure Files** | Azure Backup | ✅ | ❌ | 99 years | ✅ | Additional |
| **Redis Cache** | Persistence | ✅ | ❌ | N/A | ❌ | Premium tier |
| **Data Explorer** | Export | ✅ | ❌ | Configurable | ✅ | Storage cost |
| **Data Lake Gen2** | Azure Backup | ✅ | ✅ | 365d / 99y | ✅ | Additional |

---

## Backup Tools Comparison

### Azure Backup

| Supported Workloads | Not Supported |
|--------------------|---------------|
| ✅ Azure VMs | ❌ Azure Cosmos DB |
| ✅ SQL Server in Azure VMs | ❌ Azure Cache for Redis |
| ✅ Azure Files | ❌ Azure Data Explorer |
| ✅ Azure Blobs | |
| ✅ SAP HANA in Azure VMs | |
| ✅ Azure Managed Disks | |
| ✅ Azure Database for PostgreSQL | |

### Azure Site Recovery

| Purpose | Use Cases |
|---------|-----------|
| **Disaster Recovery** | VM failover between regions |
| **Business Continuity** | Application recovery |
| **Migration** | Lift-and-shift to Azure |

| Feature | Azure Site Recovery | Azure Backup |
|---------|-------------------|--------------|
| **RTO** | Minutes to hours | Hours to days |
| **RPO** | Minutes | Daily |
| **Failover** | ✅ Automated | ❌ No |
| **Long-Term Retention** | ❌ No | ✅ 99 years |

### MARS Agent (Microsoft Azure Recovery Services)

| Supported | Not Supported |
|-----------|---------------|
| ✅ On-premises Windows servers | ❌ Azure PaaS services |
| ✅ Windows client machines | ❌ Cosmos DB |
| ✅ Azure VMs (file/folder level) | ❌ Azure SQL Database |

---

## Recovery Objectives Comparison

### RPO (Recovery Point Objective)

| Service | Best Achievable RPO |
|---------|-------------------|
| **Azure SQL Database** | ~5 minutes (log backup frequency) |
| **Cosmos DB (Continuous)** | Seconds |
| **Cosmos DB (Periodic)** | Hours |
| **MySQL/PostgreSQL** | ~5 minutes |
| **Blob Storage (PITR)** | Near real-time |
| **Azure Files** | Up to 4 hours |
| **SQL Server on VM** | 15 minutes |
| **Redis (AOF)** | ~1 second |
| **Redis (RDB)** | Minutes to hours |

### RTO (Recovery Time Objective)

| Service | Typical RTO |
|---------|-------------|
| **Azure SQL Database** | Minutes to hours |
| **Azure SQL Hyperscale** | Minutes (fast restore) |
| **Cosmos DB (Continuous)** | Minutes |
| **MySQL/PostgreSQL** | Hours |
| **Blob Storage** | Minutes to hours |
| **Azure Files** | Minutes |
| **SQL Server on VM** | Hours |

---

## Decision Matrix

### Which Backup Solution to Use?

```
Need to backup...

├── Azure SQL Database/Managed Instance?
│   └── Use: Built-in automated backups + LTR for long-term
│
├── SQL Server on Azure VMs?
│   └── Use: Azure Backup (Recovery Services Vault)
│
├── Azure Cosmos DB?
│   ├── Need PITR & self-service? → Continuous backup
│   ├── Serverless account? → Periodic backup (only option)
│   └── Cost-sensitive? → Periodic backup
│
├── Azure Blob Storage?
│   ├── Need PITR? → Enable Point-in-Time Restore
│   ├── Need enterprise backup? → Azure Backup for Blobs
│   └── Need compliance? → Immutable Storage
│
├── Azure Files?
│   └── Use: Azure Backup (snapshot-based)
│
├── Azure MySQL/PostgreSQL?
│   └── Use: Built-in backups + Geo-redundant backup for DR
│
├── Azure Cache for Redis?
│   └── Use: Data persistence (RDB/AOF) + Export for archival
│
└── Azure Data Explorer?
    └── Use: Continuous export + Follower databases for DR
```

---

## Best Practices

### General Recommendations

1. **Understand RPO/RTO Requirements**
   - Choose backup frequency based on acceptable data loss
   - Plan restore procedures based on acceptable downtime

2. **Test Restore Procedures Regularly**
   - Document restore steps
   - Perform periodic restore drills
   - Validate backup integrity

3. **Implement Multi-Layer Protection**
   ```
   Layer 1: Soft Delete (accidental deletion protection)
   Layer 2: Versioning (change history)
   Layer 3: PITR (point-in-time restore)
   Layer 4: Cross-region backup (disaster recovery)
   Layer 5: Long-term retention (compliance)
   ```

4. **Enable Geo-Redundancy for Critical Data**
   - Configure GRS/RA-GRS for storage accounts
   - Enable geo-redundant backups for databases
   - Plan for cross-region restore scenarios

5. **Monitor Backup Status**
   - Set up Azure Monitor alerts for backup failures
   - Review backup reports regularly
   - Track backup costs

6. **Secure Backup Data**
   - Enable soft delete on Recovery Services Vaults
   - Use encryption (Microsoft-managed or customer-managed keys)
   - Implement RBAC for backup operations
   - Consider immutability for compliance

---

## Exam Tips

### Key Concepts to Remember

| Scenario | Correct Answer |
|----------|---------------|
| Cosmos DB + PITR + Self-service + 30 days | **Continuous backup** |
| Cosmos DB + Serverless | **Periodic backup** (only option) |
| Restore blob containers to earlier state | **Point-in-Time Restore** |
| Recover deleted blobs | **Soft Delete for Blobs** |
| Backup SQL Server on Azure VM | **Azure Backup** (Recovery Services Vault) |
| Azure SQL Database backup | **Built-in automated backups** |
| WORM compliance for blobs | **Immutable Storage** (Time-based or Legal Hold) |
| Unknown retention duration for legal | **Legal Hold** |
| Cross-account blob search | **Blob Index Tags** |

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| Azure Backup supports Cosmos DB | ❌ Cosmos DB has its own backup |
| MARS Agent works for PaaS | ❌ MARS is for Windows file/folder backup |
| Soft delete = Point-in-time restore | ❌ Different purposes |
| Redis has built-in backup | ❌ Uses persistence (RDB/AOF) |
| All tiers support all backup features | ❌ Check tier-specific limitations |

---

## References

- [Azure SQL Database Automated Backups](https://learn.microsoft.com/en-us/azure/azure-sql/database/automated-backups-overview)
- [Azure Cosmos DB Backup and Restore](https://learn.microsoft.com/en-us/azure/cosmos-db/continuous-backup-restore-introduction)
- [Azure Blob Storage Data Protection](https://learn.microsoft.com/en-us/azure/storage/blobs/data-protection-overview)
- [Azure Backup Documentation](https://learn.microsoft.com/en-us/azure/backup/)
- [Azure Site Recovery Documentation](https://learn.microsoft.com/en-us/azure/site-recovery/)
- [Azure Database for MySQL Backup](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-backup-restore)

---

## Related Topics

- [Azure Site Recovery and Backup](../azure_governance/azure-site-recovery-backup.md)
- [Cosmos DB Backup and Restore](./azure_cosmosdb/cosmosdb-backup-restore.md)
- [Azure Storage Data Protection](./azure_storage/06-azure-storage-data-protection.md)
- [Azure SQL Overview](./azure_sql/azure-sql-overview.md)
