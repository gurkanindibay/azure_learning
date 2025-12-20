# Azure Database for MySQL High Availability Options

## Table of Contents

- [Overview](#overview)
- [High Availability Architecture](#high-availability-architecture)
  - [Same-Zone High Availability](#same-zone-high-availability)
  - [Zone-Redundant High Availability](#zone-redundant-high-availability)
- [Disaster Recovery Options](#disaster-recovery-options)
  - [Geo-Redundant Backup](#geo-redundant-backup)
  - [Read Replicas](#read-replicas)
- [Comparison of HA and DR Options](#comparison-of-ha-and-dr-options)
- [Failover Mechanisms](#failover-mechanisms)
- [SLA Comparison](#sla-comparison)
- [RPO and RTO](#rpo-and-rto)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)
- [Cost Considerations](#cost-considerations)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure Database for MySQL Flexible Server provides multiple high availability and disaster recovery options to meet different business continuity requirements. Understanding the differences between these options is crucial for designing resilient database solutions.

### Key Concepts

| Term | Description |
|------|-------------|
| **High Availability (HA)** | Protection against failures within a region |
| **Disaster Recovery (DR)** | Protection against regional failures |
| **Zone Redundancy** | Replicas spread across availability zones |
| **Geo-Redundancy** | Data replicated to a paired Azure region |

---

## High Availability Architecture

Azure Database for MySQL Flexible Server offers two HA deployment models:

### Same-Zone High Availability

**Description:** Primary and standby servers deployed in the same availability zone.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Same-Zone High Availability                     │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 Availability Zone 1                      │   │
│   │                                                          │   │
│   │   ┌──────────────┐         ┌──────────────┐             │   │
│   │   │   Primary    │◄───────►│   Standby    │             │   │
│   │   │   Server     │  Sync   │   Server     │             │   │
│   │   │              │  Repl   │              │             │   │
│   │   │  ┌────────┐  │         │  ┌────────┐  │             │   │
│   │   │  │  Data  │  │         │  │  Data  │  │             │   │
│   │   │  │  Disk  │  │         │  │  Disk  │  │             │   │
│   │   │  └────────┘  │         │  └────────┘  │             │   │
│   │   └──────────────┘         └──────────────┘             │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ✅ Protection: Hardware/VM failures                            │
│   ❌ No protection: Zone-wide outages                            │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Replication** | Synchronous |
| **Failover** | Automatic |
| **RTO** | 60-120 seconds |
| **RPO** | 0 (zero data loss) |
| **Protection Scope** | Hardware, VM, storage failures |
| **SLA** | 99.99% |

**Use Cases:**
- Applications requiring HA within same zone
- Lower latency requirements (no cross-zone traffic)
- Cost-sensitive deployments needing HA

### Zone-Redundant High Availability

**Description:** Primary and standby servers deployed in different availability zones within the same region.

```
┌─────────────────────────────────────────────────────────────────┐
│               Zone-Redundant High Availability                   │
│                                                                  │
│   ┌────────────────────┐         ┌────────────────────┐         │
│   │ Availability Zone 1│         │ Availability Zone 2│         │
│   │                    │         │                    │         │
│   │  ┌──────────────┐  │  Sync   │  ┌──────────────┐  │         │
│   │  │   Primary    │◄─┼────────►┼─►│   Standby    │  │         │
│   │  │   Server     │  │  Repl   │  │   Server     │  │         │
│   │  │              │  │         │  │              │  │         │
│   │  │  ┌────────┐  │  │         │  │  ┌────────┐  │  │         │
│   │  │  │  Data  │  │  │         │  │  │  Data  │  │  │         │
│   │  │  │  Disk  │  │  │         │  │  │  Disk  │  │  │         │
│   │  │  └────────┘  │  │         │  │  └────────┘  │  │         │
│   │  └──────────────┘  │         │  └──────────────┘  │         │
│   └────────────────────┘         └────────────────────┘         │
│                                                                  │
│   ✅ Protection: Zone-wide outages, hardware failures            │
│   ❌ No protection: Regional outages                             │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Replication** | Synchronous |
| **Failover** | Automatic |
| **RTO** | 60-120 seconds |
| **RPO** | 0 (zero data loss) |
| **Protection Scope** | Zone failures, hardware, VM, storage |
| **SLA** | 99.99% |

**Use Cases:**
- Production workloads requiring zone-level protection
- Mission-critical applications
- Compliance requirements for zone separation

---

## Disaster Recovery Options

### Geo-Redundant Backup

**Description:** Backups are stored in a geo-paired Azure region for cross-region disaster recovery.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Geo-Redundant Backup                          │
│                                                                  │
│   Primary Region (East US)         Paired Region (West US)      │
│   ┌────────────────────┐           ┌────────────────────┐       │
│   │                    │           │                    │       │
│   │  ┌──────────────┐  │  Async    │  ┌──────────────┐  │       │
│   │  │   MySQL      │──┼──Backup──►┼─►│   Backup     │  │       │
│   │  │   Server     │  │  Copy     │  │   Storage    │  │       │
│   │  └──────────────┘  │           │  │   (GRS)      │  │       │
│   │                    │           │  └──────────────┘  │       │
│   │  ┌──────────────┐  │           │                    │       │
│   │  │   Backup     │  │           │  Restore creates   │       │
│   │  │   Storage    │  │           │  new server        │       │
│   │  │   (Local)    │  │           │                    │       │
│   │  └──────────────┘  │           │                    │       │
│   └────────────────────┘           └────────────────────┘       │
│                                                                  │
│   ✅ Protection: Regional outages                                │
│   ⚠️ Manual restore required                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Replication** | Asynchronous (backup copy) |
| **Failover** | Manual (restore to new server) |
| **RTO** | Hours (depends on database size) |
| **RPO** | Up to backup frequency (typically < 1 hour) |
| **Protection Scope** | Regional disasters |
| **Cross-Region** | ✅ Yes (paired region) |

**Key Points:**
- ✅ Recommended for cross-region DR with minimal complexity
- ⚠️ Requires manual restore - NOT automatic failover
- ⚠️ New server created during restore (new endpoint)
- ⚠️ Application connection string update required

> **Exam Tip:** Geo-redundant backup is the recommended solution for cross-region business continuity in Azure Database for MySQL Flexible Server. It provides regional disaster recovery with minimal configuration complexity.

### Read Replicas

**Description:** Asynchronous read replicas for read scaling, NOT for high availability or disaster recovery.

```
┌─────────────────────────────────────────────────────────────────┐
│                       Read Replicas                              │
│                                                                  │
│   ┌──────────────┐         ┌──────────────┐                     │
│   │   Primary    │  Async  │   Replica    │                     │
│   │   Server     │────────►│   Server     │                     │
│   │              │  Repl   │              │                     │
│   │  Reads ✅    │         │  Reads ✅    │                     │
│   │  Writes ✅   │         │  Writes ❌   │                     │
│   └──────────────┘         └──────────────┘                     │
│                                                                  │
│   Purpose: Read scale-out, NOT high availability                 │
│   ⚠️ No automatic failover                                       │
│   ⚠️ Replication lag possible                                    │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Replication** | Asynchronous |
| **Failover** | ❌ No automatic failover |
| **Purpose** | Read scaling |
| **Cross-Region** | Limited support |
| **HA/DR Solution** | ❌ No |

> **Important:** Read replicas are NOT a business continuity solution. They do not provide automatic failover and should not be used for high availability or disaster recovery purposes.

---

## Comparison of HA and DR Options

### High Availability Options (Within Region)

| Feature | Same-Zone HA | Zone-Redundant HA |
|---------|--------------|-------------------|
| **Deployment** | Same zone | Different zones |
| **Replication** | Synchronous | Synchronous |
| **Failover** | Automatic | Automatic |
| **RPO** | 0 | 0 |
| **RTO** | 60-120 seconds | 60-120 seconds |
| **Zone Protection** | ❌ No | ✅ Yes |
| **Cost** | Lower | Higher |

### Disaster Recovery Options (Cross-Region)

| Feature | Geo-Redundant Backup | Read Replicas |
|---------|---------------------|---------------|
| **Cross-Region** | ✅ Yes (paired region) | ⚠️ Limited |
| **Automatic Failover** | ❌ No | ❌ No |
| **RPO** | Backup frequency | Replication lag |
| **RTO** | Hours | N/A (manual promotion) |
| **Recommended for DR** | ✅ Yes | ❌ No |
| **Use Case** | Regional disaster recovery | Read scaling |

### Complete HA/DR Matrix

| Option | Within Region | Cross-Region | Auto Failover | RPO | RTO |
|--------|---------------|--------------|---------------|-----|-----|
| **Same-Zone HA** | ✅ | ❌ | ✅ | 0 | ~1-2 min |
| **Zone-Redundant HA** | ✅ | ❌ | ✅ | 0 | ~1-2 min |
| **Geo-Redundant Backup** | ❌ | ✅ | ❌ | < 1 hour | Hours |
| **Read Replicas** | ✅ | ⚠️ | ❌ | Variable | N/A |

---

## Failover Mechanisms

### Automatic Failover (HA Configurations)

```
┌─────────────────────────────────────────────────────────────────┐
│                 Automatic Failover Process                       │
│                                                                  │
│   1. Failure Detection                                          │
│      └─► MySQL health monitoring detects primary failure         │
│                                                                  │
│   2. Failover Initiation                                        │
│      └─► Standby server promoted to primary                      │
│                                                                  │
│   3. DNS Update                                                 │
│      └─► Endpoint automatically points to new primary            │
│                                                                  │
│   4. Application Reconnection                                   │
│      └─► Clients reconnect using same connection string          │
│                                                                  │
│   Total Time: 60-120 seconds                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Manual Failover Scenarios

| Scenario | Action Required |
|----------|-----------------|
| **Planned Maintenance** | Use planned failover (minimal downtime) |
| **Testing DR** | Manual failover to test recovery |
| **Regional Disaster** | Restore from geo-redundant backup |

### Failover Types

| Type | Trigger | Data Loss | Downtime |
|------|---------|-----------|----------|
| **Automatic** | System detects failure | Zero | 60-120 sec |
| **Planned** | User-initiated | Zero | ~30 sec |
| **Forced** | User-initiated (emergency) | Possible | ~30 sec |

---

## SLA Comparison

| Configuration | SLA | Downtime/Year | Downtime/Month |
|---------------|-----|---------------|----------------|
| **No HA** | 99.9% | 8.76 hours | 43.8 minutes |
| **Same-Zone HA** | 99.99% | 52.56 minutes | 4.38 minutes |
| **Zone-Redundant HA** | 99.99% | 52.56 minutes | 4.38 minutes |

---

## RPO and RTO

### Recovery Point Objective (RPO)

| Configuration | RPO | Data Loss Risk |
|---------------|-----|----------------|
| **Same-Zone HA** | 0 | Zero (synchronous replication) |
| **Zone-Redundant HA** | 0 | Zero (synchronous replication) |
| **Geo-Redundant Backup** | Up to 1 hour | Based on backup frequency |
| **Read Replicas** | Variable | Replication lag |

### Recovery Time Objective (RTO)

| Configuration | RTO | Notes |
|---------------|-----|-------|
| **Same-Zone HA** | 60-120 seconds | Automatic failover |
| **Zone-Redundant HA** | 60-120 seconds | Automatic failover |
| **Geo-Redundant Backup** | Hours | Manual restore required |

---

## Configuration Examples

### Azure CLI - Create Zone-Redundant HA Server

```bash
# Create a MySQL Flexible Server with Zone-Redundant HA
az mysql flexible-server create \
  --resource-group myResourceGroup \
  --name myserver \
  --location eastus \
  --sku-name Standard_D4ds_v4 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --high-availability ZoneRedundant \
  --zone 1 \
  --standby-zone 2 \
  --admin-user myadmin \
  --admin-password 'ComplexPassword123!'
```

### Azure CLI - Create Same-Zone HA Server

```bash
# Create a MySQL Flexible Server with Same-Zone HA
az mysql flexible-server create \
  --resource-group myResourceGroup \
  --name myserver \
  --location eastus \
  --sku-name Standard_D4ds_v4 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --high-availability SameZone \
  --admin-user myadmin \
  --admin-password 'ComplexPassword123!'
```

### Azure CLI - Enable Geo-Redundant Backup

```bash
# Create server with geo-redundant backup
az mysql flexible-server create \
  --resource-group myResourceGroup \
  --name myserver \
  --location eastus \
  --sku-name Standard_D4ds_v4 \
  --geo-redundant-backup Enabled \
  --admin-user myadmin \
  --admin-password 'ComplexPassword123!'
```

### Azure CLI - Perform Manual Failover

```bash
# Initiate planned failover
az mysql flexible-server failover \
  --resource-group myResourceGroup \
  --name myserver

# Force failover (emergency)
az mysql flexible-server failover \
  --resource-group myResourceGroup \
  --name myserver \
  --forced
```

### ARM Template - Zone-Redundant HA

```json
{
  "type": "Microsoft.DBforMySQL/flexibleServers",
  "apiVersion": "2023-06-30",
  "name": "[parameters('serverName')]",
  "location": "[parameters('location')]",
  "sku": {
    "name": "Standard_D4ds_v4",
    "tier": "GeneralPurpose"
  },
  "properties": {
    "administratorLogin": "[parameters('adminLogin')]",
    "administratorLoginPassword": "[parameters('adminPassword')]",
    "storage": {
      "storageSizeGB": 128
    },
    "highAvailability": {
      "mode": "ZoneRedundant",
      "standbyAvailabilityZone": "2"
    },
    "availabilityZone": "1",
    "backup": {
      "geoRedundantBackup": "Enabled",
      "backupRetentionDays": 35
    }
  }
}
```

---

## Best Practices

### 1. Choose the Right HA Configuration

| Requirement | Recommended Configuration |
|-------------|--------------------------|
| Zone failure protection | Zone-Redundant HA |
| Cost optimization with HA | Same-Zone HA |
| Regional disaster recovery | Geo-Redundant Backup |
| Read scaling | Read Replicas (not for HA) |

### 2. Enable Geo-Redundant Backup for DR

```
✅ DO: Enable geo-redundant backup for production
✅ DO: Test restore procedure regularly
✅ DO: Document restore runbook
❌ DON'T: Rely on read replicas for DR
```

### 3. Configure Connection Retry Logic

```python
# Python example - Connection retry
import mysql.connector
from mysql.connector import Error
import time

def create_connection_with_retry(config, max_retries=5):
    for attempt in range(max_retries):
        try:
            connection = mysql.connector.connect(**config)
            return connection
        except Error as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
```

### 4. Monitor HA Health

```bash
# Check HA status
az mysql flexible-server show \
  --resource-group myResourceGroup \
  --name myserver \
  --query "highAvailability"
```

### 5. Regular Failover Testing

```
✅ DO: Test failover monthly
✅ DO: Document failover time
✅ DO: Verify application reconnection
✅ DO: Test geo-restore procedure quarterly
```

---

## Cost Considerations

### HA Configuration Costs

| Configuration | Additional Cost |
|---------------|-----------------|
| **No HA** | Base cost only |
| **Same-Zone HA** | ~2x compute (standby server) |
| **Zone-Redundant HA** | ~2x compute + cross-zone traffic |

### Geo-Redundant Backup Costs

| Component | Cost Factor |
|-----------|-------------|
| **Backup Storage** | ~$0.095/GB/month (GRS) |
| **Restore** | New server provisioned |

### Cost Optimization Tips

1. **Use Same-Zone HA** when zone protection isn't required
2. **Right-size standby** - same tier required but can be smaller
3. **Monitor backup storage** - retention affects costs
4. **Consider backup-only DR** for non-critical workloads

---

## Practice Questions

### Question 1
**Your company needs to implement a business continuity solution for Azure Database for MySQL Flexible Server that provides cross-region disaster recovery with minimal complexity. Which option should you choose?**

A. Zone-Redundant High Availability  
B. Read Replicas  
C. Geo-Redundant Backup  
D. Same-Zone High Availability

<details>
<summary>Answer</summary>

**C. Geo-Redundant Backup**

Geo-redundant backup is the recommended solution for cross-region disaster recovery in Azure Database for MySQL Flexible Server. It stores backups in a paired region with minimal configuration complexity.

- Zone-Redundant HA only protects within a region
- Read Replicas are not a DR solution
- Same-Zone HA only protects within a zone

</details>

### Question 2
**What is the RPO (Recovery Point Objective) for Zone-Redundant High Availability in Azure Database for MySQL Flexible Server?**

A. Up to 1 hour  
B. Up to 5 minutes  
C. 0 (zero data loss)  
D. Depends on replication lag

<details>
<summary>Answer</summary>

**C. 0 (zero data loss)**

Zone-Redundant HA uses synchronous replication between primary and standby servers, ensuring zero data loss during failover.

</details>

### Question 3
**Which statement about Read Replicas in Azure Database for MySQL Flexible Server is TRUE?**

A. Read replicas provide automatic failover  
B. Read replicas are the recommended DR solution  
C. Read replicas use synchronous replication  
D. Read replicas are designed for read scaling, not HA/DR

<details>
<summary>Answer</summary>

**D. Read replicas are designed for read scaling, not HA/DR**

Read replicas use asynchronous replication and do not provide automatic failover. They are intended for offloading read workloads, not for high availability or disaster recovery.

</details>

---

## References

- [High Availability in Azure Database for MySQL - Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-high-availability)
- [Business Continuity Overview](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-business-continuity)
- [Backup and Restore](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-backup-restore)
- [Read Replicas](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-read-replicas)
- [Azure Database for MySQL Flexible Server SLA](https://azure.microsoft.com/en-us/support/legal/sla/mysql/)
