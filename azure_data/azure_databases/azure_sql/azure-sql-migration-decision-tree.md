# Azure SQL Migration Decision Tree

## Table of Contents

- [Overview](#overview)
- [Quick Decision Summary](#quick-decision-summary)
- [Decision Tree: Service Selection](#decision-tree-service-selection)
  - [Step 1: Assess Control Requirements](#step-1-assess-control-requirements)
  - [Step 2: Evaluate SQL Server Compatibility Needs](#step-2-evaluate-sql-server-compatibility-needs)
  - [Step 3: Determine Application Architecture](#step-3-determine-application-architecture)
- [Decision Tree: Tier Selection](#decision-tree-tier-selection)
  - [Azure SQL Database Tiers](#azure-sql-database-tiers)
  - [Azure SQL Managed Instance Tiers](#azure-sql-managed-instance-tiers)
  - [SQL Server on Azure VMs](#sql-server-on-azure-vms)
- [Visual Decision Flowchart](#visual-decision-flowchart)
- [Feature-Based Decision Matrix](#feature-based-decision-matrix)
- [Migration Scenarios and Recommendations](#migration-scenarios-and-recommendations)
- [Cost Considerations](#cost-considerations)
- [Migration Tool Selection](#migration-tool-selection)
- [References](#references)

---

## Overview

Migrating an on-premises SQL Server database to Azure requires choosing the right **service** (SQL Database, Managed Instance, or SQL Server on VMs) and the appropriate **tier** (General Purpose, Business Critical, Hyperscale). This document provides a structured decision tree to guide you through these choices.

### Azure SQL Services at a Glance

| Service | Type | Best For | Compatibility | Management |
|---------|------|----------|---------------|------------|
| **Azure SQL Database** | PaaS | Modern cloud-native apps | ~95% | Fully managed |
| **Azure SQL Managed Instance** | PaaS | Lift-and-shift migrations | ~100% | Fully managed |
| **SQL Server on Azure VMs** | IaaS | Full SQL Server control | 100% | Self-managed |

---

## Quick Decision Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    QUICK SERVICE SELECTION                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Need 100% SQL Server compatibility + OS access?                             │
│  ├── YES → SQL Server on Azure VMs                                          │
│  └── NO                                                                      │
│       │                                                                      │
│       ├── Need CLR, SQL Agent, Cross-DB queries, Service Broker?            │
│       │   ├── YES → Azure SQL Managed Instance                              │
│       │   └── NO                                                             │
│       │       │                                                              │
│       │       └── Modern cloud app OR new development?                       │
│       │           ├── YES → Azure SQL Database                               │
│       │           └── NO → Azure SQL Managed Instance                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Service Selection

### Step 1: Assess Control Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│               DO YOU NEED FULL OS/SQL SERVER CONTROL?            │
│                                                                  │
│  Consider YES if you require:                                    │
│  • Custom SQL Server configuration                               │
│  • OS-level access for third-party software                      │
│  • Cluster/failover cluster instances                            │
│  • Features not available in PaaS (FILESTREAM, etc.)             │
│  • Specific SQL Server version requirements                      │
│  • Custom backup strategies beyond 35-day retention              │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────┐                                    ┌─────┐            │
│   │ YES │ ──────────────────────────────────►│ SQL │            │
│   └─────┘                                    │ VM  │            │
│                                              └─────┘            │
│   ┌─────┐                                                       │
│   │ NO  │ ──────────► Continue to Step 2                        │
│   └─────┘                                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Decision Criteria for SQL Server on Azure VMs:**

| Requirement | Why SQL Server on VMs? |
|-------------|----------------------|
| FILESTREAM | Not supported in PaaS options |
| SQL Server Reporting Services (SSRS) | Requires VM deployment |
| SQL Server Integration Services (SSIS) on same server | Traditional deployment model |
| SQL Server Analysis Services (SSAS) | Requires VM deployment |
| Failover Cluster Instances | Not supported in PaaS |
| Specific SQL Server version | PaaS uses latest compatible |
| Third-party backup tools | OS access required |
| Custom OS configuration | Full control needed |

---

### Step 2: Evaluate SQL Server Compatibility Needs

```
┌─────────────────────────────────────────────────────────────────┐
│            DO YOU NEED INSTANCE-LEVEL FEATURES?                  │
│                                                                  │
│  Instance-level features include:                                │
│  • SQL Server Agent for job scheduling                           │
│  • Cross-database queries (3-part naming)                        │
│  • Linked servers                                                │
│  • Service Broker                                                │
│  • CLR (Common Language Runtime)                                 │
│  • Database Mail                                                 │
│  • Distributed transactions                                      │
│  • Multiple databases in single instance                         │
│  • Replication (transactional, merge, snapshot)                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────┐                               ┌──────────────────┐    │
│   │ YES │ ─────────────────────────────►│ SQL Managed      │    │
│   └─────┘                               │ Instance         │    │
│                                         └──────────────────┘    │
│   ┌─────┐                                                       │
│   │ NO  │ ──────────► Continue to Step 3                        │
│   └─────┘                                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Instance-Level Feature Comparison:**

| Feature | SQL Database | Managed Instance | SQL VM |
|---------|-------------|------------------|--------|
| SQL Server Agent | ❌ Elastic Jobs | ✅ Full | ✅ Full |
| Cross-DB Queries | ❌ Limited | ✅ Full | ✅ Full |
| Linked Servers | ❌ No | ✅ Yes | ✅ Yes |
| Service Broker | ❌ No | ✅ Yes | ✅ Yes |
| CLR | ❌ Limited | ✅ Full | ✅ Full |
| Database Mail | ❌ No | ✅ Yes | ✅ Yes |
| Distributed TX | ❌ No | ✅ Yes | ✅ Yes |
| Replication | ❌ Subscriber only | ✅ Full | ✅ Full |

---

### Step 3: Determine Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              WHAT IS YOUR APPLICATION SCENARIO?                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SCENARIO A: Modern Cloud-Native Application                 │ │
│  │ • New application development                               │ │
│  │ • Microservices architecture                                │ │
│  │ • Single-database design                                    │ │
│  │ • No legacy dependencies                                    │ │
│  │                                                             │ │
│  │ ────────────────────────► Azure SQL Database                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SCENARIO B: Multi-Tenant SaaS Application                   │ │
│  │ • Multiple databases with similar schemas                   │ │
│  │ • Variable usage patterns across tenants                    │ │
│  │ • Cost optimization for multiple DBs                        │ │
│  │                                                             │ │
│  │ ────────────────────────► Azure SQL Database (Elastic Pool) │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SCENARIO C: Lift-and-Shift Migration                        │ │
│  │ • Existing SQL Server application                           │ │
│  │ • Minimal code changes desired                              │ │
│  │ • Need high compatibility                                   │ │
│  │                                                             │ │
│  │ ────────────────────────► Azure SQL Managed Instance        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SCENARIO D: Intermittent or Development Workload            │ │
│  │ • Unpredictable usage patterns                              │ │
│  │ • Development/test environment                              │ │
│  │ • Cost optimization priority                                │ │
│  │                                                             │ │
│  │ ────────────────────────► Azure SQL Database (Serverless)   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Tier Selection

### Azure SQL Database Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AZURE SQL DATABASE - TIER SELECTION                       │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Is database size > 4 TB?                                                 ││
│  │ ├── YES ──► HYPERSCALE                                                   ││
│  │ └── NO                                                                   ││
│  │     │                                                                    ││
│  │     ├── Do you need < 2ms latency or built-in read replicas?            ││
│  │     │   ├── YES ──► BUSINESS CRITICAL                                   ││
│  │     │   └── NO                                                          ││
│  │     │       │                                                           ││
│  │     │       ├── Is workload intermittent/unpredictable?                 ││
│  │     │       │   ├── YES ──► GENERAL PURPOSE (Serverless)                ││
│  │     │       │   └── NO ──► GENERAL PURPOSE (Provisioned)                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Tier Comparison Table

| Criteria | General Purpose | Business Critical | Hyperscale |
|----------|-----------------|-------------------|------------|
| **Max Storage** | 4 TB | 4 TB | 100 TB |
| **Latency** | 5-10ms | 1-2ms | 1-2ms (local) |
| **SLA** | 99.99% | 99.99% (99.995% zone) | 99.99% |
| **Read Replicas** | ❌ No | ✅ 1 free | ✅ Up to 4 |
| **Storage Type** | Remote (Premium) | Local SSD | Distributed |
| **Backup Speed** | Standard | Standard | Fast (instant) |
| **Scale Speed** | Hours | Hours | Minutes |
| **Auto-pause** | ✅ Serverless only | ❌ No | ❌ No |
| **Starting Price** | ~$360/mo (2 vCore) | ~$900/mo (2 vCore) | ~$500/mo (2 vCore) |

#### Serverless vs Provisioned Decision

```
┌─────────────────────────────────────────────────────────────────┐
│           SERVERLESS OR PROVISIONED COMPUTE?                     │
│                                                                  │
│  Choose SERVERLESS if:                                           │
│  ✅ Workload is intermittent or unpredictable                    │
│  ✅ Can tolerate few seconds resume delay                        │
│  ✅ Dev/test environment                                         │
│  ✅ Want auto-pause to save costs                                │
│  ✅ Usage is < 50% of the time                                   │
│                                                                  │
│  Choose PROVISIONED if:                                          │
│  ✅ Consistent 24/7 workload                                     │
│  ✅ Cannot tolerate any connection delay                         │
│  ✅ Production with predictable usage                            │
│  ✅ Need Business Critical tier                                  │
│  ✅ Using Hyperscale tier                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Azure SQL Managed Instance Tiers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                SQL MANAGED INSTANCE - TIER SELECTION                         │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ Do you need ANY of these?                                               ││
│  │ • Sub-millisecond latency                                               ││
│  │ • In-Memory OLTP                                                        ││
│  │ • Built-in read replicas                                                ││
│  │ • Higher availability (99.995%)                                         ││
│  │                                                                         ││
│  │ ├── YES ──► BUSINESS CRITICAL                                           ││
│  │ └── NO ──► GENERAL PURPOSE                                              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

| Criteria | General Purpose | Business Critical |
|----------|-----------------|-------------------|
| **Max Storage** | 16 TB | 4 TB |
| **Latency** | 5-10ms | 1-2ms |
| **SLA** | 99.99% | 99.99% |
| **In-Memory OLTP** | ❌ No | ✅ Yes |
| **Read Replicas** | ❌ No | ✅ 1 included |
| **Storage Type** | Remote | Local SSD |
| **Starting Price** | ~$730/mo (4 vCore) | ~$1,900/mo (4 vCore) |

---

### SQL Server on Azure VMs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                SQL SERVER ON AZURE VMs - TIER SELECTION                      │
│                                                                              │
│  VM Series Selection:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ What is your primary workload type?                                     ││
│  │                                                                         ││
│  │ OLTP / Transaction Processing:                                          ││
│  │ ├── Memory-intensive ──► E-series (Memory Optimized)                    ││
│  │ └── Balanced ──► D-series (General Purpose)                             ││
│  │                                                                         ││
│  │ Data Warehousing / Analytics:                                           ││
│  │ └── ──► M-series (Memory Optimized - Large)                             ││
│  │                                                                         ││
│  │ Development / Testing:                                                  ││
│  │ └── ──► B-series (Burstable) or D-series                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  High Availability Options:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ • Always On Availability Groups (AOAG) - Recommended                    ││
│  │ • Failover Cluster Instances (FCI) with Storage Spaces Direct          ││
│  │ • Azure Site Recovery for disaster recovery                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Visual Decision Flowchart

```
                        ┌──────────────────────────┐
                        │   On-Premises SQL Server │
                        │   Migration to Azure     │
                        └───────────┬──────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │ Need 100% SQL Server compatibility │
                    │ + OS/hardware control?            │
                    └───────────────┬───────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
              ┌─────────┐                    ┌─────────┐
              │   YES   │                    │   NO    │
              └────┬────┘                    └────┬────┘
                   │                              │
                   ▼                              ▼
        ┌─────────────────────┐    ┌───────────────────────────────┐
        │ SQL Server on       │    │ Need instance-level features? │
        │ Azure VMs           │    │ (SQL Agent, CLR, Cross-DB,    │
        │                     │    │  Service Broker, Linked       │
        │ Choose:             │    │  Servers)                     │
        │ • VM Size           │    └───────────────┬───────────────┘
        │ • HA Option (AOAG)  │                    │
        │ • Disk Config       │    ┌───────────────┴───────────────┐
        └─────────────────────┘    ▼                               ▼
                             ┌─────────┐                    ┌─────────┐
                             │   YES   │                    │   NO    │
                             └────┬────┘                    └────┬────┘
                                  │                              │
                                  ▼                              ▼
                    ┌─────────────────────┐    ┌────────────────────────────┐
                    │ Azure SQL Managed   │    │ What's your scenario?      │
                    │ Instance            │    └───────────────┬────────────┘
                    │                     │                    │
                    │ Choose Tier:        │    ┌───────────────┼───────────────┐
                    │ • General Purpose   │    ▼               ▼               ▼
                    │ • Business Critical │ ┌────────┐  ┌────────────┐  ┌───────────┐
                    └─────────────────────┘ │ Single │  │ Multi-     │  │ Variable  │
                                            │ Modern │  │ Tenant     │  │ Workload  │
                                            │ App    │  │ SaaS       │  │           │
                                            └───┬────┘  └─────┬──────┘  └─────┬─────┘
                                                │             │               │
                                                ▼             ▼               ▼
                                            ┌────────┐  ┌──────────┐  ┌────────────┐
                                            │ SQL DB │  │ Elastic  │  │ Serverless │
                                            │ Single │  │ Pool     │  │            │
                                            └───┬────┘  └────┬─────┘  └─────┬──────┘
                                                │            │              │
                                                └────────────┼──────────────┘
                                                             │
                                                             ▼
                                            ┌────────────────────────────────┐
                                            │ Choose Service Tier:           │
                                            │                                │
                                            │ • DB > 4TB? ──► Hyperscale    │
                                            │ • Need <2ms latency?           │
                                            │   ──► Business Critical        │
                                            │ • Standard workload?           │
                                            │   ──► General Purpose          │
                                            └────────────────────────────────┘
```

---

## Feature-Based Decision Matrix

Use this matrix to quickly identify which service supports your required features:

| Feature Requirement | SQL Database | Elastic Pool | Managed Instance | SQL VM |
|---------------------|-------------|--------------|------------------|--------|
| **Compatibility & Features** |||||
| SQL Server 2022 Features | Partial | Partial | Full | Full |
| CLR Stored Procedures | ❌ | ❌ | ✅ | ✅ |
| SQL Server Agent | ❌ | ❌ | ✅ | ✅ |
| Cross-Database Queries | ❌ | ❌ | ✅ | ✅ |
| Service Broker | ❌ | ❌ | ✅ | ✅ |
| Linked Servers | ❌ | ❌ | ✅ | ✅ |
| Database Mail | ❌ | ❌ | ✅ | ✅ |
| FILESTREAM | ❌ | ❌ | ❌ | ✅ |
| SSRS/SSIS/SSAS | ❌ | ❌ | ❌ | ✅ |
| **Management & Scaling** |||||
| Fully Managed | ✅ | ✅ | ✅ | ❌ |
| Auto-patching | ✅ | ✅ | ✅ | Optional |
| Serverless Compute | ✅ | ❌ | ❌ | ❌ |
| Elastic Scaling | ❌ | ✅ | ❌ | ❌ |
| Max Storage | 4TB/100TB* | 4TB | 16TB | Unlimited |
| **High Availability** |||||
| Built-in HA | ✅ | ✅ | ✅ | Manual |
| Zone Redundancy | ✅ | ✅ | ✅ | Manual |
| Read Replicas | BC/HS only | BC only | BC only | Manual |
| **Networking** |||||
| VNet Integration | Private Endpoint | Private Endpoint | Native VNet | Full |
| Public Endpoint | ✅ | ✅ | Optional | ✅ |
| Hybrid Connectivity | Limited | Limited | ✅ | ✅ |

*Hyperscale tier supports up to 100TB

---

## Migration Scenarios and Recommendations

### Scenario 1: Legacy ERP System Migration

**Characteristics:**
- Multiple databases with cross-database queries
- SQL Server Agent jobs
- CLR procedures
- Linked servers to other systems

**Recommendation:** ✅ **Azure SQL Managed Instance**

```
Reason: Near 100% compatibility ensures minimal application changes
Tier: General Purpose (unless low latency required)
```

---

### Scenario 2: Modern SaaS Application (Single Tenant per DB)

**Characteristics:**
- 50+ customer databases
- Similar schemas
- Variable usage patterns
- Cost optimization important

**Recommendation:** ✅ **Azure SQL Database - Elastic Pool**

```
Reason: Shared resources optimize costs across multiple databases
Tier: General Purpose Pool
Sizing: Start with 100 eDTUs or 10 vCores, scale based on usage
```

---

### Scenario 3: New Cloud-Native Microservice

**Characteristics:**
- Single isolated database
- No legacy dependencies
- Modern application design
- Need rapid development

**Recommendation:** ✅ **Azure SQL Database - Single Database**

```
Reason: Simple, isolated, fully managed
Tier: General Purpose Serverless (for dev)
      General Purpose Provisioned (for prod)
```

---

### Scenario 4: Large Data Warehouse Migration

**Characteristics:**
- 10TB+ database size
- Complex analytics queries
- Need fast backup/restore
- Multiple read workloads

**Recommendation:** ✅ **Azure SQL Database - Hyperscale**

```
Reason: Only option supporting 100TB, fast scaling, multiple read replicas
Alternative: Consider Azure Synapse Analytics for pure analytics
```

---

### Scenario 5: Application Requiring Full SQL Server Control

**Characteristics:**
- FILESTREAM usage
- SSRS reports on same server
- Custom backup solutions
- Specific SQL Server version required

**Recommendation:** ✅ **SQL Server on Azure VMs**

```
Reason: Full control and 100% compatibility
VM Series: E-series for memory-intensive, D-series for balanced
HA: Always On Availability Groups
```

---

### Scenario 6: Dev/Test Environment

**Characteristics:**
- Used only during business hours
- Variable and unpredictable usage
- Cost is primary concern
- Can tolerate brief connection delays

**Recommendation:** ✅ **Azure SQL Database - Serverless**

```
Reason: Auto-pause saves costs, per-second billing
Configuration: 
  - Min vCores: 0.5
  - Max vCores: 4
  - Auto-pause: 1 hour
Savings: Up to 80% vs provisioned
```

---

## Cost Considerations

### Cost Optimization Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                    COST OPTIMIZATION PATH                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Do you have SQL Server licenses with Software Assurance?        │
│  ├── YES ──► Use Azure Hybrid Benefit (save up to 55%)          │
│  └── NO ──► Consider license-included pricing                    │
│                                                                  │
│  Is workload < 50% utilization over time?                        │
│  ├── YES ──► Consider Serverless compute                         │
│  └── NO ──► Use Provisioned compute                              │
│                                                                  │
│  Do you have multiple databases with variable load?              │
│  ├── YES ──► Use Elastic Pool (shared resources)                 │
│  └── NO ──► Use Single Database                                  │
│                                                                  │
│  Can you commit to 1-3 year usage?                               │
│  ├── YES ──► Use Reserved Capacity (save up to 80%)              │
│  └── NO ──► Use Pay-as-you-go                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Monthly Cost Comparison (Estimated)

| Configuration | General Purpose | Business Critical | Hyperscale |
|---------------|-----------------|-------------------|------------|
| **SQL Database (4 vCore, 100GB)** | ~$750 | ~$1,900 | ~$1,100 |
| **Elastic Pool (4 vCore, 5 DBs)** | ~$750 | ~$1,900 | N/A |
| **Managed Instance (4 vCore)** | ~$730 | ~$1,900 | N/A |
| **SQL VM (D4s_v3 + license)** | ~$650 | N/A | N/A |

*Prices are approximate and vary by region. Check Azure Pricing Calculator for current rates.*

---

## Migration Tool Selection

```
┌─────────────────────────────────────────────────────────────────┐
│                 MIGRATION TOOL DECISION TREE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Is downtime acceptable?                                         │
│  │                                                              │
│  ├── YES (Offline Migration)                                     │
│  │   └── Azure Database Migration Service (DMS)                  │
│  │       • Fully managed                                         │
│  │       • Minimal admin effort                                  │
│  │       • Large-scale support                                   │
│  │                                                              │
│  └── NO (Online Migration - Minimal Downtime)                    │
│      └── Azure Data Studio + SQL Migration Extension             │
│          • Online replication                                    │
│          • Cutover when ready                                    │
│          • Minimal downtime                                      │
│                                                                  │
│  Pre-Migration Assessment:                                       │
│  • Azure Migrate - Discovery & sizing                            │
│  • Data Migration Assistant (DMA) - Compatibility check          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Scenario | Tool | Purpose |
|----------|------|---------|
| Assessment & Discovery | Azure Migrate | Resource discovery, sizing, cost estimation |
| Compatibility Check | Data Migration Assistant | Identify blocking issues |
| Offline Migration | Azure Database Migration Service | Automated migration |
| Online Migration (min downtime) | Azure Data Studio + Extension | Continuous sync |
| Non-SQL Server source | SQL Server Migration Assistant | Oracle, MySQL, DB2 |

---

## Migration Checklist

### Pre-Migration

- [ ] Assess database compatibility using Data Migration Assistant
- [ ] Inventory all databases, sizes, and dependencies
- [ ] Identify instance-level features in use (CLR, SQL Agent, etc.)
- [ ] Review application connection strings
- [ ] Plan network connectivity (VNet, private endpoints)
- [ ] Calculate target sizing and costs

### Service Selection

- [ ] Determine if PaaS or IaaS is required
- [ ] Choose between SQL Database, Managed Instance, or VM
- [ ] Select appropriate service tier
- [ ] Decide on compute tier (Serverless vs Provisioned)

### Tier Selection

- [ ] Evaluate database size requirements
- [ ] Assess latency and performance needs
- [ ] Consider high availability requirements
- [ ] Review read replica needs
- [ ] Calculate cost implications

### Post-Migration

- [ ] Validate data integrity
- [ ] Test application connectivity
- [ ] Compare performance to baseline
- [ ] Update connection strings
- [ ] Configure monitoring and alerts

---

## References

- [Azure SQL Documentation](https://learn.microsoft.com/en-us/azure/azure-sql/)
- [Choose the Right Azure SQL Service](https://learn.microsoft.com/en-us/azure/azure-sql/azure-sql-iaas-vs-paas-what-is-overview)
- [Azure SQL Database Service Tiers](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tiers-general-purpose-business-critical)
- [Azure SQL Managed Instance Overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview)
- [Azure Database Migration Service](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Azure Hybrid Benefit](https://azure.microsoft.com/en-us/pricing/hybrid-benefit/)
