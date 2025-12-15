# Azure Database for MySQL Flexible Server

## Table of Contents

- [1. Overview](#1-overview)
- [2. Business Continuity Solutions](#2-business-continuity-solutions)
  - [Geo-Redundant Backup](#geo-redundant-backup)
  - [High Availability](#high-availability)
  - [Read Replicas](#read-replicas)
- [3. Business Continuity Options Comparison](#3-business-continuity-options-comparison)

## 1. Overview

Azure Database for MySQL Flexible Server is a fully managed database service designed to provide more granular control and flexibility over database management functions and configuration settings than Azure Database for MySQL Single Server.

## 2. Business Continuity Solutions

### Geo-Redundant Backup

Geo-redundant backup (Geo-RA-GRS) is the **recommended solution for cross-region business continuity** when you need to minimize downtime in the event of a regional outage.

| Feature | Description |
|---------|-------------|
| **Storage Location** | Backups are stored in a **paired Azure region** |
| **Failover Type** | Manual restoration required (not automatic) |
| **Use Case** | Regional disaster recovery |
| **Complexity** | Low - minimal additional configuration |
| **Cost** | Moderate - storage costs for geo-redundant backups |

**Key Points:**
- Allows you to restore the server in a different region in case of a regional outage
- Does **not** offer automatic failover or real-time replication
- Provides reasonable recovery times (RTO/RPO)
- Best option when balancing cost, complexity, and recovery requirements

> **Exam Tip:** When asked about implementing a business continuity solution for Azure Database for MySQL Flexible Server that minimizes downtime during failover to a **paired region**, the answer is **Geo-redundant backup**. This is the supported cross-region disaster recovery option for Flexible Server.

### High Availability

Azure Database for MySQL Flexible Server offers zone-redundant and same-zone high availability options for **within-region** availability.

| HA Option | Description |
|-----------|-------------|
| **Zone-Redundant HA** | Primary and standby servers in different availability zones within the same region |
| **Same-Zone HA** | Primary and standby servers in the same availability zone |

> **Note:** High Availability options protect against failures **within a region**, not across regions. For cross-region protection, use Geo-redundant backup.

### Read Replicas

Read replicas in Azure Database for MySQL Flexible Server are used for **read scaling**, not for high availability or disaster recovery.

| Feature | Description |
|---------|-------------|
| **Purpose** | Offload read workloads from the primary server |
| **Failover** | **Not automatic** - replicas are not promoted automatically |
| **Cross-Region** | Not supported by default for cross-region replication |
| **Use Case** | Read-heavy workloads, reporting, analytics |

> **Important:** Read replicas are **not** a business continuity solution. They do not provide automatic failover and cannot be used for cross-region disaster recovery in Flexible Server.

## 3. Business Continuity Options Comparison

| Option | Cross-Region DR | Automatic Failover | Best For |
|--------|-----------------|-------------------|----------|
| **Geo-Redundant Backup** ✅ | Yes (paired region) | No (manual restore) | Regional disaster recovery with minimal complexity |
| **Zone-Redundant HA** | No (same region) | Yes | Within-region high availability |
| **Read Replicas** ❌ | No | No | Read scaling, not DR |
| **Native MySQL Replication** ❌ | N/A | N/A | Not supported in Flexible Server |
| **Azure Premium File Shares** ❌ | N/A | N/A | Not supported - PaaS abstracts storage |

### Unsupported Approaches

| Approach | Why Not Supported |
|----------|-------------------|
| **Store database files in Azure Premium File Shares** | Azure Database for MySQL is a PaaS offering. Database file storage paths are abstracted from users. You cannot directly manage where MySQL stores its files. |
| **Configure native MySQL replication** | Azure Database for MySQL Flexible Server does not support user-configured native replication between flexible servers across regions. It also increases complexity and requires additional management overhead. |
| **Read replicas for cross-region failover** | Read replicas are for read-only scaling, not for HA or failover. They are not automatically promoted in case of failure and do not replicate cross-region by default in Flexible Server. |

## References

- [Backup and restore in Azure Database for MySQL - Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-backup-restore)
- [High availability concepts in Azure Database for MySQL - Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-high-availability)
- [Read replicas in Azure Database for MySQL - Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-read-replicas)
- [Business continuity overview for Azure Database for MySQL - Flexible Server](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/concepts-business-continuity)
