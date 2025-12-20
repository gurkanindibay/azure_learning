# Azure SQL High Availability Options

## Table of Contents

- [Overview](#overview)
- [Azure SQL Product Family HA Comparison](#azure-sql-product-family-ha-comparison)
- [Azure SQL Database High Availability](#azure-sql-database-high-availability)
  - [General Purpose Tier](#general-purpose-tier)
  - [Business Critical Tier](#business-critical-tier)
  - [Hyperscale Tier](#hyperscale-tier)
  - [DTU-Based Tiers](#dtu-based-tiers)
- [Zone Redundancy](#zone-redundancy)
- [Geo-Replication and Failover](#geo-replication-and-failover)
  - [Active Geo-Replication](#active-geo-replication)
  - [Auto-Failover Groups](#auto-failover-groups)
- [Azure SQL Managed Instance HA](#azure-sql-managed-instance-ha)
- [SQL Server on Azure VMs HA](#sql-server-on-azure-vms-ha)
- [SLA Comparison](#sla-comparison)
- [RPO and RTO](#rpo-and-rto)
- [Decision Guide](#decision-guide)
- [Configuration Examples](#configuration-examples)
- [Best Practices](#best-practices)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure SQL provides comprehensive high availability options across its product family. The HA architecture and capabilities differ based on the deployment option (SQL Database, Managed Instance, or VMs) and service tier chosen.

### Key HA Concepts

| Concept | Description |
|---------|-------------|
| **Local Redundancy** | Replicas within same datacenter |
| **Zone Redundancy** | Replicas across availability zones |
| **Geo-Redundancy** | Replicas across Azure regions |
| **Always On** | SQL Server HA technology using availability groups |
| **Failover Groups** | Managed failover between regions |

---

## Azure SQL Product Family HA Comparison

| Feature | SQL Database | SQL Managed Instance | SQL Server on VMs |
|---------|--------------|---------------------|-------------------|
| **Built-in HA** | ✅ Yes | ✅ Yes | ❌ Self-managed |
| **Zone Redundancy** | ✅ Available | ✅ Available | ✅ Manual setup |
| **Auto-Failover Groups** | ✅ Yes | ✅ Yes | ❌ Use Always On |
| **Active Geo-Replication** | ✅ Yes | ❌ No | ❌ Use Always On |
| **SLA** | Up to 99.995% | Up to 99.99% | Based on setup |
| **Management** | Fully managed | Fully managed | Self-managed |

---

## Azure SQL Database High Availability

### General Purpose Tier

**Architecture:** Remote storage with compute redundancy

```
┌─────────────────────────────────────────────────────────────────┐
│               General Purpose High Availability                  │
│                                                                  │
│   Compute Layer                      Storage Layer               │
│   ┌──────────────┐                  ┌─────────────────────────┐ │
│   │   Primary    │                  │   Azure Premium Storage │ │
│   │   Compute    │◄────────────────►│   (LRS or ZRS)          │ │
│   │   Node       │                  │                         │ │
│   └──────────────┘                  │   ┌───────┐ ┌───────┐   │ │
│         │                           │   │ Data  │ │ Data  │   │ │
│         │ Failover                  │   │ Copy 1│ │ Copy 2│   │ │
│         ▼                           │   └───────┘ └───────┘   │ │
│   ┌──────────────┐                  │   ┌───────┐             │ │
│   │   Standby    │                  │   │ Data  │             │ │
│   │   Compute    │                  │   │ Copy 3│             │ │
│   │   Nodes      │                  │   └───────┘             │ │
│   └──────────────┘                  └─────────────────────────┘ │
│                                                                  │
│   ✅ Remote storage provides data durability                     │
│   ⚠️ Failover involves attaching storage to new compute          │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **SLA** | 99.99% |
| **Zone Redundancy** | ✅ Optional |
| **Storage Type** | Azure Premium Storage (remote) |
| **RPO** | < 30 seconds typically |
| **RTO** | < 30 seconds typically |
| **Read Replicas** | ❌ Not included |
| **Zero Data Loss** | ❌ Not guaranteed |

**Failover Behavior:**
- Compute node failure → New compute attaches to remote storage
- Storage provides 3 copies of data (LRS) or across zones (ZRS)
- Transactions in flight may be lost during failover

### Business Critical Tier

**Architecture:** Always On Availability Groups with local SSD storage

```
┌─────────────────────────────────────────────────────────────────┐
│              Business Critical High Availability                 │
│                                                                  │
│   Always On Availability Group (Synchronous Replication)         │
│                                                                  │
│   ┌──────────────┐   Sync    ┌──────────────┐                   │
│   │   Primary    │◄─────────►│  Secondary   │                   │
│   │   Replica    │   Repl    │   Replica    │                   │
│   │              │           │              │                   │
│   │  ┌────────┐  │           │  ┌────────┐  │                   │
│   │  │ Local  │  │           │  │ Local  │  │                   │
│   │  │  SSD   │  │           │  │  SSD   │  │                   │
│   │  └────────┘  │           │  └────────┘  │                   │
│   └──────────────┘           └──────────────┘                   │
│          │                          │                           │
│          │         Sync             │                           │
│          └──────────────────────────┘                           │
│                      │                                          │
│                      ▼                                          │
│              ┌──────────────┐                                   │
│              │  Secondary   │  (Read Scale-Out)                 │
│              │   Replica    │                                   │
│              │  ┌────────┐  │                                   │
│              │  │ Local  │  │                                   │
│              │  │  SSD   │  │                                   │
│              │  └────────┘  │                                   │
│              └──────────────┘                                   │
│                                                                  │
│   ✅ Zero data loss (synchronous replication)                    │
│   ✅ 1 free read replica included                                │
│   ✅ Lowest latency (local SSD)                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **SLA** | 99.99% (99.995% zone-redundant) |
| **Zone Redundancy** | ✅ Optional |
| **Storage Type** | Local SSD |
| **RPO** | 0 (zero data loss) |
| **RTO** | < 30 seconds |
| **Read Replicas** | ✅ 1 included |
| **Zero Data Loss** | ✅ Guaranteed |

**Key Benefits:**
- Uses SQL Server Always On Availability Groups
- Synchronous commit ensures zero data loss
- Free readable secondary for read scale-out
- Lowest I/O latency (1-2ms)

### Hyperscale Tier

**Architecture:** Multi-tier storage with page servers

```
┌─────────────────────────────────────────────────────────────────┐
│                  Hyperscale High Availability                    │
│                                                                  │
│   Compute Tier                                                   │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│   │  Primary   │  │ HA Replica │  │ Named      │                │
│   │  Compute   │  │  (HA)      │  │ Replicas   │                │
│   └────────────┘  └────────────┘  └────────────┘                │
│         │               │               │                        │
│         └───────────────┼───────────────┘                        │
│                         │                                        │
│   ┌─────────────────────┼──────────────────────────────────────┐│
│   │    Page Servers     │                                      ││
│   │   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐           ││
│   │   │ Page  │   │ Page  │   │ Page  │   │ Page  │           ││
│   │   │Server1│   │Server2│   │Server3│   │Server4│           ││
│   │   └───────┘   └───────┘   └───────┘   └───────┘           ││
│   └────────────────────────────────────────────────────────────┘│
│                         │                                        │
│   ┌─────────────────────┼──────────────────────────────────────┐│
│   │    Log Service      │                                      ││
│   │   ┌──────────────────────────────────────┐                 ││
│   │   │         Transaction Log              │                 ││
│   │   │    (Landing Zone for Commits)        │                 ││
│   │   └──────────────────────────────────────┘                 ││
│   └────────────────────────────────────────────────────────────┘│
│                                                                  │
│   ✅ Up to 100 TB storage                                        │
│   ✅ Fast scaling (minutes)                                      │
│   ✅ Up to 4 named read replicas                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **SLA** | 99.99% (99.995% zone-redundant) |
| **Zone Redundancy** | ✅ Available |
| **Storage** | Up to 100 TB |
| **RPO** | < 30 seconds typically |
| **RTO** | < 30 seconds |
| **Read Replicas** | Up to 4 named replicas |
| **Zero Data Loss** | ❌ Not guaranteed |

**Key Benefits:**
- Massive storage capacity (100 TB)
- Fast compute scaling (minutes vs hours)
- Multiple read replicas for scale-out
- Near-instant backups regardless of size

### DTU-Based Tiers

#### Basic and Standard Tiers

| Aspect | Basic | Standard |
|--------|-------|----------|
| **SLA** | 99.99% | 99.99% |
| **Zone Redundancy** | ❌ No | ❌ No |
| **Zero Data Loss** | ❌ No | ❌ No |
| **Active Geo-Replication** | ❌ No | ✅ Yes (S3+) |

#### Premium Tier

**Architecture:** Similar to Business Critical (Always On)

| Aspect | Value |
|--------|-------|
| **SLA** | 99.99% (99.995% zone-redundant) |
| **Zone Redundancy** | ✅ Yes |
| **Zero Data Loss** | ✅ Yes |
| **Read Replicas** | ✅ 1 included |
| **Active Geo-Replication** | ✅ Yes |

> **Key Point:** Premium DTU tier provides same HA capabilities as Business Critical vCore tier, often at lower cost for specific workloads.

---

## Zone Redundancy

### Zone-Redundant Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Zone-Redundant Deployment                      │
│                                                                  │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│   │   Zone 1    │   │   Zone 2    │   │   Zone 3    │           │
│   │             │   │             │   │             │           │
│   │ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌─────────┐ │           │
│   │ │ Primary │ │   │ │Secondary│ │   │ │Secondary│ │           │
│   │ │ Replica │◄┼───┼►│ Replica │◄┼───┼►│ Replica │ │           │
│   │ └─────────┘ │   │ └─────────┘ │   │ └─────────┘ │           │
│   │             │   │             │   │             │           │
│   └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                  │
│   Zone 1 fails → Automatic failover to Zone 2 or 3              │
│   No data loss, minimal downtime                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Zone Redundancy Support by Tier

| Tier | Zone Redundancy | Zero Data Loss | SLA |
|------|-----------------|----------------|-----|
| **Basic (DTU)** | ❌ | ❌ | 99.99% |
| **Standard (DTU)** | ❌ | ❌ | 99.99% |
| **Premium (DTU)** | ✅ | ✅ | 99.995% |
| **General Purpose (vCore)** | ✅ | ❌ | 99.99% |
| **Business Critical (vCore)** | ✅ | ✅ | 99.995% |
| **Hyperscale (vCore)** | ✅ | ❌ | 99.995% |

---

## Geo-Replication and Failover

### Active Geo-Replication

**Description:** Asynchronous replication to up to 4 readable secondary databases in different regions.

```
┌─────────────────────────────────────────────────────────────────┐
│                   Active Geo-Replication                         │
│                                                                  │
│   Primary Region (East US)                                       │
│   ┌──────────────────┐                                          │
│   │                  │                                          │
│   │  Primary DB      │                                          │
│   │  • Reads ✅      │                                          │
│   │  • Writes ✅     │                                          │
│   │                  │                                          │
│   └────────┬─────────┘                                          │
│            │                                                     │
│            │ Async Replication                                   │
│            │                                                     │
│   ┌────────┴────────────────────────────────────────────┐       │
│   │                                                      │       │
│   ▼                    ▼                    ▼            ▼       │
│ ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│ │ West US  │    │ Europe   │    │ Asia     │    │Secondary │   │
│ │Secondary │    │Secondary │    │Secondary │    │    4     │   │
│ │ Reads ✅ │    │ Reads ✅ │    │ Reads ✅ │    │ Reads ✅ │   │
│ │Writes ❌ │    │Writes ❌ │    │Writes ❌ │    │Writes ❌ │   │
│ └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│                                                                  │
│   • Up to 4 readable secondaries                                 │
│   • Independent scale and pricing per replica                    │
│   • Manual or programmatic failover                              │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Max Secondaries** | 4 |
| **Replication** | Asynchronous |
| **RPO** | < 5 seconds |
| **RTO** | < 30 seconds |
| **Failover** | Manual/Programmatic |
| **Secondaries Readable** | ✅ Yes |

**Use Cases:**
- Read scale-out across regions
- Low RTO disaster recovery
- Granular control over failover

### Auto-Failover Groups

**Description:** Managed failover with DNS endpoint for transparent application failover.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Auto-Failover Groups                         │
│                                                                  │
│                    DNS Endpoints                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Read-Write: <fogname>.database.windows.net              │  │
│   │  Read-Only:  <fogname>.secondary.database.windows.net    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│              ┌─────────────┴─────────────┐                      │
│              │                           │                      │
│              ▼                           ▼                      │
│   Primary Region                 Secondary Region               │
│   ┌──────────────────┐          ┌──────────────────┐           │
│   │                  │  Async   │                  │           │
│   │  Primary DB      │◄────────►│  Secondary DB    │           │
│   │  • Reads ✅      │  Repl    │  • Reads ✅      │           │
│   │  • Writes ✅     │          │  • Writes ❌     │           │
│   │                  │          │                  │           │
│   └──────────────────┘          └──────────────────┘           │
│                                                                  │
│   Automatic Failover:                                            │
│   • Grace period configurable (default 1 hour)                   │
│   • DNS automatically updated                                    │
│   • No application changes needed                                │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics:**

| Aspect | Value |
|--------|-------|
| **Max Secondaries** | 1 |
| **Replication** | Asynchronous |
| **RPO** | ~1 hour (configurable) |
| **RTO** | ~1 hour (configurable) |
| **Failover** | Automatic |
| **DNS Management** | ✅ Automatic |

**Use Cases:**
- Minimal administration DR solution
- Transparent application failover
- Cross-region business continuity

### Comparison: Active Geo-Replication vs Auto-Failover Groups

| Feature | Active Geo-Replication | Auto-Failover Groups |
|---------|----------------------|---------------------|
| **Secondaries** | Up to 4 | 1 only |
| **RTO** | < 30 seconds | ~1 hour |
| **RPO** | < 5 seconds | ~1 hour |
| **Failover Type** | Manual/Programmatic | Automatic |
| **DNS Management** | Manual | Automatic |
| **Admin Overhead** | Higher | Lower |
| **Best For** | Read scale-out, low RTO | Simple DR, auto-failover |

---

## Azure SQL Managed Instance HA

### Built-in High Availability

```
┌─────────────────────────────────────────────────────────────────┐
│          SQL Managed Instance High Availability                  │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Virtual Cluster                        │   │
│   │                                                          │   │
│   │   ┌──────────────┐         ┌──────────────┐             │   │
│   │   │   Primary    │◄───────►│   Standby    │             │   │
│   │   │   Instance   │  Sync   │   Instance   │             │   │
│   │   │              │  Repl   │              │             │   │
│   │   └──────────────┘         └──────────────┘             │   │
│   │                                                          │   │
│   │   Deployed in Azure VNet                                 │   │
│   │   Private IP addresses only                              │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Service Tiers

| Tier | Zone Redundancy | Zero Data Loss | Read Replica |
|------|-----------------|----------------|--------------|
| **General Purpose** | ✅ Optional | ❌ | ❌ |
| **Business Critical** | ✅ Optional | ✅ | ✅ 1 included |

### Failover Groups for Managed Instance

```
┌─────────────────────────────────────────────────────────────────┐
│        Managed Instance Failover Group                           │
│                                                                  │
│   Primary Region                    Secondary Region             │
│   ┌──────────────────┐             ┌──────────────────┐         │
│   │                  │             │                  │         │
│   │  MI Instance 1   │◄───────────►│  MI Instance 2   │         │
│   │  (Primary)       │   Async     │  (Secondary)     │         │
│   │                  │   Repl      │                  │         │
│   └──────────────────┘             └──────────────────┘         │
│                                                                  │
│   DNS: <fogname>.database.windows.net                            │
│   (Points to primary, auto-updates on failover)                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> **Note:** SQL Managed Instance supports Auto-Failover Groups but NOT Active Geo-Replication.

---

## SQL Server on Azure VMs HA

### High Availability Options

| Option | Description | Best For |
|--------|-------------|----------|
| **Always On Availability Groups** | SQL Server native HA with synchronous/async replicas | Enterprise HA/DR |
| **Always On Failover Cluster Instances (FCI)** | Shared storage cluster | Instance-level HA |
| **Log Shipping** | Transaction log backup/restore | Simple DR |
| **Database Mirroring** | Deprecated, use Always On | Legacy systems |

### Always On Availability Groups Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│          Always On Availability Groups (VMs)                     │
│                                                                  │
│   Availability Zone 1        Availability Zone 2                 │
│   ┌──────────────────┐      ┌──────────────────┐                │
│   │   SQL Server VM  │      │   SQL Server VM  │                │
│   │   (Primary)      │      │   (Secondary)    │                │
│   │                  │ Sync │                  │                │
│   │  ┌────────────┐  │◄────►│  ┌────────────┐  │                │
│   │  │ AG Replica │  │ Repl │  │ AG Replica │  │                │
│   │  └────────────┘  │      │  └────────────┘  │                │
│   └──────────────────┘      └──────────────────┘                │
│             │                        │                          │
│             └────────────────────────┘                          │
│                        │                                        │
│              ┌─────────┴─────────┐                              │
│              │    Listener       │                              │
│              │   (VNN or DNN)    │                              │
│              └───────────────────┘                              │
│                                                                  │
│   Windows Server Failover Cluster (WSFC) required               │
└─────────────────────────────────────────────────────────────────┘
```

### Network Name Options

| Option | Description | Azure Load Balancer |
|--------|-------------|---------------------|
| **VNN (Virtual Network Name)** | Traditional listener with ILB | Required |
| **DNN (Distributed Network Name)** | SQL 2019+ direct connection | Not required |

---

## SLA Comparison

### Complete SLA Matrix

| Configuration | SLA | Max Downtime/Year |
|---------------|-----|-------------------|
| **Single DB (no zone redundancy)** | 99.99% | 52.56 min |
| **General Purpose (zone-redundant)** | 99.99% | 52.56 min |
| **Business Critical (zone-redundant)** | 99.995% | 26.28 min |
| **Hyperscale (zone-redundant)** | 99.995% | 26.28 min |
| **Premium DTU (zone-redundant)** | 99.995% | 26.28 min |
| **SQL Managed Instance** | 99.99% | 52.56 min |

---

## RPO and RTO

### Recovery Objectives by Configuration

| Configuration | RPO | RTO | Zero Data Loss |
|---------------|-----|-----|----------------|
| **General Purpose** | < 30 sec | < 30 sec | ❌ |
| **Business Critical** | 0 | < 30 sec | ✅ |
| **Hyperscale** | < 30 sec | < 30 sec | ❌ |
| **Premium DTU** | 0 | < 30 sec | ✅ |
| **Active Geo-Replication** | < 5 sec | < 30 sec | ❌ |
| **Auto-Failover Groups** | ~1 hour | ~1 hour | ❌ |

---

## Decision Guide

### Choosing the Right HA Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                    HA Decision Tree                              │
│                                                                  │
│   Need zero data loss?                                          │
│   │                                                              │
│   ├─► YES → Business Critical or Premium DTU                    │
│   │         + Zone redundancy for zone protection                │
│   │                                                              │
│   └─► NO  → Need very large database (>4TB)?                    │
│             │                                                    │
│             ├─► YES → Hyperscale                                │
│             │                                                    │
│             └─► NO  → General Purpose (cost-effective)          │
│                                                                  │
│   Need cross-region DR?                                          │
│   │                                                              │
│   ├─► YES + Need low RTO (<30s) → Active Geo-Replication        │
│   │                                                              │
│   └─► YES + Prefer auto-failover → Auto-Failover Groups         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Reference

| Requirement | Recommended Solution |
|-------------|---------------------|
| Zero data loss + cost optimization | Premium DTU (zone-redundant) |
| Zero data loss + vCore flexibility | Business Critical |
| Very large database | Hyperscale |
| Multiple read replicas (regions) | Active Geo-Replication |
| Simple cross-region DR | Auto-Failover Groups |
| Full SQL Server control | SQL Server on VMs + Always On |

---

## Configuration Examples

### Azure CLI - Enable Zone Redundancy

```bash
# Create zone-redundant Business Critical database
az sql db create \
  --resource-group myResourceGroup \
  --server myServer \
  --name myDatabase \
  --edition BusinessCritical \
  --family Gen5 \
  --capacity 4 \
  --zone-redundant true
```

### Azure CLI - Create Active Geo-Replication

```bash
# Create geo-secondary
az sql db replica create \
  --resource-group myResourceGroup \
  --server myServer \
  --name myDatabase \
  --partner-server myPartnerServer \
  --partner-resource-group myPartnerResourceGroup
```

### Azure CLI - Create Auto-Failover Group

```bash
# Create failover group
az sql failover-group create \
  --resource-group myResourceGroup \
  --server myServer \
  --partner-server myPartnerServer \
  --name myFailoverGroup \
  --failover-policy Automatic \
  --grace-period 1

# Add database to failover group
az sql failover-group update \
  --resource-group myResourceGroup \
  --server myServer \
  --name myFailoverGroup \
  --add-db myDatabase
```

### ARM Template - Zone-Redundant Database

```json
{
  "type": "Microsoft.Sql/servers/databases",
  "apiVersion": "2023-05-01-preview",
  "name": "[concat(parameters('serverName'), '/', parameters('databaseName'))]",
  "location": "[parameters('location')]",
  "sku": {
    "name": "BC_Gen5",
    "tier": "BusinessCritical",
    "capacity": 4
  },
  "properties": {
    "zoneRedundant": true,
    "readScale": "Enabled",
    "requestedBackupStorageRedundancy": "Zone"
  }
}
```

---

## Best Practices

### 1. Enable Zone Redundancy for Production

```
✅ DO: Enable zone redundancy for Business Critical/Premium
✅ DO: Test failover regularly
❌ DON'T: Assume single-zone is sufficient for production
```

### 2. Choose Appropriate DR Strategy

| RTO Requirement | Recommended |
|-----------------|-------------|
| < 30 seconds | Active Geo-Replication |
| < 1 hour | Auto-Failover Groups |
| > 1 hour | Geo-redundant backup |

### 3. Implement Connection Retry Logic

```csharp
// C# Example - Retry policy
var options = new SqlConnectionStringBuilder(connectionString)
{
    ConnectRetryCount = 3,
    ConnectRetryInterval = 10
};
```

### 4. Use Read-Only Routing

```csharp
// Connection string for read intent
var readConnectionString = 
    "Server=myserver.database.windows.net;" +
    "Database=mydb;" +
    "ApplicationIntent=ReadOnly;";
```

### 5. Monitor HA Health

```sql
-- Check replica health
SELECT 
    database_id,
    synchronization_state_desc,
    synchronization_health_desc
FROM sys.dm_database_replica_states;
```

---

## Practice Questions

### Question 1
**Your company requires an Azure SQL Database with zero data loss failover and zone redundancy while minimizing costs. Which tier should you choose?**

A. General Purpose (vCore)  
B. Business Critical (vCore)  
C. Premium (DTU)  
D. Hyperscale (vCore)

<details>
<summary>Answer</summary>

**C. Premium (DTU)**

Premium DTU tier provides zero data loss (Always On) and zone redundancy support, similar to Business Critical, but typically at a lower cost for comparable workloads. It meets all requirements while minimizing costs.

</details>

### Question 2
**Which Azure SQL geo-replication option provides the lowest RTO?**

A. Auto-Failover Groups  
B. Active Geo-Replication  
C. Geo-redundant backup  
D. Zone-redundant deployment

<details>
<summary>Answer</summary>

**B. Active Geo-Replication**

Active Geo-Replication provides RTO < 30 seconds, while Auto-Failover Groups have RTO of approximately 1 hour. Zone-redundant deployment doesn't provide cross-region protection.

</details>

### Question 3
**Which tier provides built-in read scale-out in Azure SQL Database?**

A. General Purpose  
B. Standard (DTU)  
C. Business Critical  
D. Basic (DTU)

<details>
<summary>Answer</summary>

**C. Business Critical**

Business Critical tier includes one free read replica for read scale-out. This replica can be accessed using ApplicationIntent=ReadOnly in the connection string.

</details>

### Question 4
**Your application needs to failover automatically to a secondary region with minimal configuration. Which feature should you use?**

A. Active Geo-Replication  
B. Auto-Failover Groups  
C. Zone-redundant deployment  
D. Always On Availability Groups

<details>
<summary>Answer</summary>

**B. Auto-Failover Groups**

Auto-Failover Groups provide automatic failover with DNS endpoint management, requiring no application changes. Active Geo-Replication requires manual or programmatic failover initiation.

</details>

---

## References

- [Azure SQL Database High Availability](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla)
- [Zone-Redundant Databases](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla-local-zone-redundancy)
- [Active Geo-Replication Overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/active-geo-replication-overview)
- [Auto-Failover Groups Overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/auto-failover-group-overview)
- [SQL Managed Instance High Availability](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/high-availability-sla)
- [SQL Server on Azure VMs High Availability](https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/hadr-cluster-best-practices)
