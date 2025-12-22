# Azure SQL Deployment Decision Guide: Scenarios & Best Practices

## Overview

Choosing the right Azure SQL deployment option can be challenging given the variety of products, tiers, and compute models available. This document provides real-world scenarios to help you make informed decisions.

---

## Azure SQL Product Family at a Glance

| Product | Best For | Key Characteristics |
|---------|----------|---------------------|
| **Azure SQL Database (Single)** | Modern cloud apps, SaaS | Fully managed, auto-scaling options |
| **Azure SQL Database (Elastic Pool)** | Multiple databases with variable usage | Shared resources, cost optimization |
| **Azure SQL Managed Instance** | Lift-and-shift migrations | Near 100% SQL Server compatibility |
| **SQL Server on Azure VMs** | Full SQL Server control | OS-level access, legacy features |

---

## Part 1: Deployment Type Scenarios

### Scenario 1: Startup Building a New SaaS Application

**Context:**
- New cloud-native application
- Unpredictable workload patterns
- Small development team (no dedicated DBA)
- Budget-conscious, pay-per-use preferred

**Recommendation:** ✅ **Azure SQL Database - Single Database (Serverless)**

**Why:**
- Zero infrastructure management
- Auto-pause when inactive (cost savings)
- Auto-scaling based on workload
- Built-in high availability
- No need to predict capacity upfront

**Configuration:**
```
Tier: General Purpose (Serverless)
vCores: 0.5 - 4 (auto-scale)
Auto-pause delay: 60 minutes
```

---

### Scenario 2: Multi-Tenant SaaS Platform with 50+ Customer Databases

**Context:**
- Each customer has their own database
- Usage varies significantly between customers
- Some databases are very active, others barely used
- Need predictable monthly costs

**Recommendation:** ✅ **Azure SQL Database - Elastic Pool**

**Why:**
- Share resources across multiple databases
- Cost-effective for databases with varying usage patterns
- Individual database limits within pool
- Single management point for multiple databases
- Average utilization typically 20-30% more efficient than single databases

**Configuration:**
```
Tier: General Purpose (Elastic Pool)
eDTUs: 200 or vCores: 4-8
Max databases: 100+
Per-database limits: Max 100 eDTU / Min 0 eDTU
```

**Cost Comparison Example:**
| Approach | Monthly Cost (Estimate) |
|----------|------------------------|
| 50 Single S2 Databases | ~$3,750 |
| 1 Elastic Pool (200 eDTU) | ~$750 |
| **Savings** | **~80%** |

---

### Scenario 3: Migrating Legacy Enterprise ERP System

**Context:**
- On-premises SQL Server 2016 with 500GB database
- Uses SQL Agent Jobs, Service Broker, CLR assemblies
- Cross-database queries required
- Linked servers to other databases
- Compliance requires minimal code changes

**Recommendation:** ✅ **Azure SQL Managed Instance**

**Why:**
- Near 100% compatibility with SQL Server
- Supports SQL Agent, Service Broker, CLR
- Native VNet integration
- Cross-database queries supported
- Minimal application changes required

**Configuration:**
```
Tier: General Purpose
vCores: 8-16
Storage: 1TB
Backup retention: 35 days
```

**Migration Approach:**
1. Use Azure Database Migration Service
2. Online migration with minimal downtime
3. Maintain existing T-SQL code
4. Keep SQL Agent jobs as-is

---

### Scenario 4: Mission-Critical Trading Platform

**Context:**
- Sub-millisecond latency requirements
- Zero data loss tolerance (RPO = 0)
- 99.995% availability required
- Real-time analytics on live data
- 24/7 operations globally

**Recommendation:** ✅ **Azure SQL Database - Business Critical** or **SQL Managed Instance - Business Critical**

**Why:**
- Local SSD storage for lowest latency
- Built-in read replicas (no extra cost)
- Zone redundancy available
- In-memory OLTP included
- 99.995% SLA with zone redundancy

**Configuration:**
```
Tier: Business Critical
vCores: 16-32
Zone Redundancy: Enabled
Read replicas: 1-3 (included)
In-Memory OLTP: Enabled
```

---

### Scenario 5: Data Warehouse with Massive Historical Data

**Context:**
- 50TB+ database size
- Complex analytical queries
- Data grows 5TB annually
- Need fast query performance
- Occasional bulk data loads

**Recommendation:** ✅ **Azure SQL Database - Hyperscale**

**Why:**
- Up to 100TB storage capacity
- Instant backups regardless of size
- Fast database restores
- Distributed storage architecture
- Up to 4 read replicas
- Independent compute and storage scaling

**Configuration:**
```
Tier: Hyperscale
vCores: 8-24 (scale as needed)
Storage: Auto-grows to 100TB
Read replicas: 2-4 for reporting
```

**Hyperscale Benefits for Large Databases:**
| Capability | Traditional Tiers | Hyperscale |
|------------|------------------|------------|
| Max Size | 4TB | 100TB |
| Backup Time | Hours | Seconds |
| Restore Time | Hours-Days | Minutes |
| Scale Storage | Manual | Automatic |

---

### Scenario 6: Regulatory Compliance with Full OS Control

**Context:**
- Healthcare application (HIPAA compliance)
- Need custom OS-level configurations
- Require specific SQL Server version/edition
- Must install third-party monitoring tools
- Windows failover clustering required

**Recommendation:** ✅ **SQL Server on Azure Virtual Machines**

**Why:**
- Full control over OS and SQL Server
- Any SQL Server version/edition
- Custom security configurations
- Support for legacy features
- Windows Server Failover Clustering
- Third-party tool installation

**Configuration:**
```
VM Size: E8s_v5 (8 vCPUs, 64GB RAM)
SQL Edition: Enterprise
Storage: Premium SSD P30 x 4 (striped)
Availability: Availability Zones or Always On AG
```

---

### Scenario 6a: SQL Server on Azure VMs - VM Series Selection

**Context:**
- Deploying SQL Server on Azure Virtual Machines
- Need to support 15,000+ disk IOPS
- Require SR-IOV (Single Root I/O Virtualization) for low-latency networking
- Cost optimization is important

**Recommendation:** ✅ **DS-series Virtual Machines**

**Why DS-series is correct:**
- **Disk-Intensive Optimization**: DS-series VMs are optimized for disk-intensive workloads and support Premium SSDs
- **High IOPS Support**: Can deliver well beyond 15,000 disk IOPS depending on VM size and disk configuration
- **SR-IOV Support**: Enables low-latency, high-throughput network performance critical for database workloads
- **Cost-Effective**: General-purpose VMs that balance performance and cost for SQL Server workloads
- **Ideal Use Case**: SQL Server workloads requiring both high disk performance and cost efficiency

**Why NOT NC-series:**
- ❌ Designed for GPU-intensive compute workloads (machine learning, AI model training)
- ❌ More expensive than necessary for database workloads
- ❌ Not optimized for disk IOPS or database operations
- ❌ Poor fit for SQL Server deployments

**Why NOT NV-series:**
- ❌ Optimized for graphics-intensive applications (remote visualization)
- ❌ Uses GPU acceleration not beneficial for database workloads
- ❌ Not designed for high disk IOPS
- ❌ Results in unnecessary cost and suboptimal performance for SQL Server

**VM Series Comparison for SQL Server:**

| VM Series | Primary Use Case | IOPS Optimization | SR-IOV | Cost for SQL Server |
|-----------|------------------|-------------------|--------|---------------------|
| **DS-series** | Disk-intensive, general purpose | ✅ High (Premium SSD) | ✅ Yes | ✅ Cost-effective |
| NC-series | GPU compute (ML/AI) | ❌ Not optimized | ✅ Yes | ❌ Expensive, overkill |
| NV-series | GPU visualization | ❌ Not optimized | ✅ Yes | ❌ Expensive, wrong fit |

**Configuration Example:**
```
VM Series: DS-series (e.g., DS13_v2, DS14_v2)
Premium SSD: P30 or higher for 15,000+ IOPS
Networking: Accelerated networking enabled (SR-IOV)
```

**References:**
- [Dv2 and DSv2-series](https://learn.microsoft.com/en-us/azure/virtual-machines/dv2-dsv2-series)
- [Azure VM Sizes Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes)
- [NC-series (GPU)](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nc-series)
- [NV-series (GPU)](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/nv-series)

---

### Scenario 7: Development and Testing Environment

**Context:**
- Multiple dev/test databases needed
- Used only during business hours (8 hours/day)
- Need to spin up/down environments quickly
- Budget is very limited
- Data is non-production

**Recommendation:** ✅ **Azure SQL Database - Serverless (General Purpose)**

**Why:**
- Auto-pause saves 66%+ on compute costs
- Quick provisioning
- No commitment required
- Scale down during inactive periods
- Pay only for actual usage

**Configuration:**
```
Tier: General Purpose (Serverless)
vCores: 1-2 (min-max)
Auto-pause: 60 minutes of inactivity
Zone redundancy: Disabled (dev/test)
Backup redundancy: LRS (lowest cost)
```

**Cost Savings Example:**
| Model | 8 hrs/day usage | Monthly Cost |
|-------|-----------------|--------------|
| Provisioned (2 vCore GP) | N/A | ~$370 |
| Serverless (0.5-2 vCore) | Auto-pause | ~$80-120 |

---

### Scenario 8: Global E-Commerce Platform

**Context:**
- Users across Americas, Europe, and Asia
- Need low-latency reads globally
- Single source of truth for inventory
- High read-to-write ratio (80:20)
- Peak traffic during sales events

**Recommendation:** ✅ **Azure SQL Database - Business Critical with Active Geo-Replication**

**Why:**
- Readable secondary replicas in multiple regions
- Automatic failover groups
- Low-latency reads from local region
- RPO < 5 seconds for geo-replication
- Auto-failover for disaster recovery

**Architecture:**
```
Primary: East US (Business Critical, 16 vCores)
Secondary 1: West Europe (Read-only replica)
Secondary 2: Southeast Asia (Read-only replica)
Failover: Automatic with Traffic Manager
```

---

## Part 2: Service Tier Decision Scenarios

### Scenario 9: Choosing Between DTU and vCore Models

**DTU Model - Choose When:**
- ✅ Predictable, steady workloads
- ✅ Simpler pricing preference
- ✅ Don't need reserved capacity pricing
- ✅ Smaller databases (< 4TB)

**vCore Model - Choose When:**
- ✅ Need to independently scale compute/storage
- ✅ Want reserved capacity discounts (up to 55% savings)
- ✅ Migrating from on-premises (easier sizing)
- ✅ Need Hyperscale tier
- ✅ Require more control over resources

**DTU to vCore Mapping (Approximate):**
| DTU Tier | Approximate vCore Equivalent |
|----------|------------------------------|
| S0 (10 DTU) | 0.25 vCore |
| S3 (100 DTU) | 2 vCores |
| P1 (125 DTU) | 2 vCores (Business Critical) |
| P4 (500 DTU) | 6 vCores (Business Critical) |

---

### Scenario 10: General Purpose vs Business Critical

**General Purpose - Choose When:**
- ✅ Budget-conscious workloads
- ✅ Latency tolerance up to 5-10ms
- ✅ Standard business applications
- ✅ 99.99% SLA is acceptable
- ✅ Remote storage is acceptable

**Business Critical - Choose When:**
- ✅ Latency-sensitive applications (<2ms)
- ✅ Need built-in read replicas
- ✅ Require 99.995% SLA
- ✅ In-memory OLTP needed
- ✅ Mission-critical workloads

**Performance Comparison:**
| Aspect | General Purpose | Business Critical |
|--------|-----------------|-------------------|
| Storage | Remote (Azure Premium) | Local SSD |
| Latency | 5-10ms | 1-2ms |
| IOPS | 500-7500 | 5000-200000 |
| Read Replicas | Add-on ($) | Included (free) |
| SLA | 99.99% | 99.995% |
| Price | 1x | ~1.7x |

---

### Scenario 11: When to Use Hyperscale

**Hyperscale - Choose When:**
- ✅ Database > 4TB (up to 100TB)
- ✅ Unpredictable growth patterns
- ✅ Need instant backups and fast restores
- ✅ Require multiple read replicas
- ✅ Need independent compute/storage scaling

**Hyperscale - Avoid When:**
- ❌ Database < 1TB (other tiers more cost-effective)
- ❌ Need zone redundancy (not yet supported)
- ❌ Require Business Critical latency
- ❌ Need in-memory OLTP

---

## Part 3: Compute Model Scenarios

### Scenario 12: Serverless vs Provisioned Compute

**Serverless - Choose When:**
- ✅ Unpredictable or intermittent usage
- ✅ Development/test environments
- ✅ New applications with unknown patterns
- ✅ Workloads with idle periods
- ✅ Cost optimization is priority

**Provisioned - Choose When:**
- ✅ Consistent, predictable workloads
- ✅ Production with steady traffic
- ✅ Need reserved capacity pricing
- ✅ Cannot tolerate cold-start delays
- ✅ 24/7 operations

**Cost Analysis Example (100 compute hours/week):**
| Scenario | Serverless | Provisioned |
|----------|------------|-------------|
| 40 hrs/week usage | $85/month | $185/month |
| 80 hrs/week usage | $150/month | $185/month |
| 168 hrs/week (24/7) | $350/month | $185/month |

**Key Insight:** Serverless is cost-effective when utilization < 60-70%

---

## Part 4: Migration-Specific Scenarios

### Scenario 13: SQL Server 2008 R2 End of Support Migration

**Context:**
- Running SQL Server 2008 R2 (end of support)
- Need extended security updates
- Minimal budget for refactoring
- Want to maintain current architecture

**Recommendation:** ✅ **SQL Server on Azure VMs** or **Azure SQL Managed Instance**

**Option A - SQL Server on Azure VMs:**
- Free extended security updates
- Zero code changes
- Fastest migration path
- Later modernize to PaaS

**Option B - Azure SQL Managed Instance:**
- Free extended security updates
- Managed service benefits
- May require minor compatibility fixes
- Better long-term TCO

---

### Scenario 14: Consolidating Multiple Small Databases

**Context:**
- 30 small databases (< 5GB each)
- Shared application infrastructure
- Low individual utilization (< 10% each)
- Need cost optimization

**Recommendation:** ✅ **Elastic Pool (General Purpose)**

**Sizing Calculation:**
```
Total size: 30 x 5GB = 150GB storage
Peak DTU estimate: 30 x 10 DTU x 0.3 (concurrent) = 90 DTU
Recommended pool: 100 eDTU Standard Pool
```

**Alternative for Very Low Usage:** Consider database consolidation into fewer databases if application architecture allows.

---

## Part 5: Quick Decision Matrix

### By Workload Type

| Workload Type | Recommended Product | Recommended Tier |
|---------------|---------------------|------------------|
| Cloud-native SaaS | SQL Database (Single) | GP Serverless |
| Multi-tenant SaaS | SQL Database (Elastic Pool) | GP or BC |
| Lift-and-shift | SQL Managed Instance | GP |
| Mission-critical OLTP | SQL Database/MI | Business Critical |
| Large Data Warehouse | SQL Database | Hyperscale |
| Legacy with full control | SQL Server on VMs | Enterprise |
| Dev/Test | SQL Database | GP Serverless |
| Global distribution | SQL Database | BC + Geo-replication |

### By Primary Concern

| Primary Concern | Recommended Choice |
|-----------------|-------------------|
| **Lowest Cost** | Serverless (GP) with auto-pause |
| **Best Performance** | Business Critical with zone redundancy |
| **Maximum Compatibility** | SQL Managed Instance or SQL on VMs |
| **Largest Scale** | Hyperscale |
| **Simplest Management** | SQL Database (Single) |
| **Multi-database Cost Optimization** | Elastic Pool |
| **Global Low Latency** | BC + Active Geo-Replication |

---

## Part 6: Cost Optimization Tips

### 1. Reserved Capacity
- Commit to 1 or 3 years for up to 55% savings
- Available for vCore model only
- Best for stable, production workloads

### 2. Azure Hybrid Benefit
- Use existing SQL Server licenses
- Up to 55% savings on vCore pricing
- Combine with reserved capacity for 80%+ savings

### 3. Right-Sizing
- Monitor DTU/vCore usage via Azure Monitor
- Scale down over-provisioned resources
- Use auto-scaling for variable workloads

### 4. Dev/Test Pricing
- Use Azure Dev/Test subscription
- Significant discounts on compute
- No production SLAs

### 5. Backup Storage Optimization
- Choose appropriate backup redundancy:
  - LRS: Lowest cost, single region
  - ZRS: Zone redundancy
  - GRS: Cross-region (highest cost)

---

## Part 7: Feature Availability Matrix

| Feature | SQL Database | Elastic Pool | Managed Instance | SQL on VMs |
|---------|--------------|--------------|------------------|------------|
| Serverless | ✅ | ❌ | ❌ | ❌ |
| Elastic scaling | ❌ | ✅ | ❌ | ❌ |
| SQL Agent | ❌ | ❌ | ✅ | ✅ |
| CLR | Limited | Limited | ✅ | ✅ |
| Service Broker | ❌ | ❌ | ✅ | ✅ |
| Linked Servers | ❌ | ❌ | ✅ | ✅ |
| Cross-DB queries | ❌ | ✅ (same pool) | ✅ | ✅ |
| Hyperscale | ✅ | ❌ | ❌ | ❌ |
| Zone Redundancy | ✅ | ✅ | ✅ | Via Availability Zones |
| Read Replicas | ✅ (BC) | ✅ (BC) | ✅ (BC) | ✅ (Always On) |
| OS Access | ❌ | ❌ | ❌ | ✅ |
| **SSIS** | ❌ (Use ADF SSIS-IR) | ❌ (Use ADF SSIS-IR) | ❌ (Use ADF SSIS-IR) | ✅ |
| **SSRS** | ❌ (Use Power BI) | ❌ (Use Power BI) | ❌ (Use Power BI) | ✅ |
| **SSAS** | ❌ (Use Azure AS) | ❌ (Use Azure AS) | ❌ (Use Azure AS) | ✅ |

**Notes on SSIS/SSRS/SSAS:**
- **SSIS**: For PaaS options, use Azure Data Factory with SSIS Integration Runtime (SSIS-IR) to lift-and-shift existing SSIS packages
- **SSRS**: For PaaS options, use Power BI Service with Paginated Reports or host SSRS on a separate Azure VM
- **SSAS**: For PaaS options, use Azure Analysis Services as a fully managed alternative

---

## Summary Decision Flowchart

```
Start
  │
  ├─ Need OS-level access or specific SQL version?
  │   └─ YES → SQL Server on Azure VMs
  │
  ├─ Migrating from on-premises with SQL Agent/CLR/Service Broker?
  │   └─ YES → Azure SQL Managed Instance
  │
  ├─ Multiple databases with variable usage?
  │   └─ YES → Elastic Pool
  │
  ├─ Database > 4TB?
  │   └─ YES → Hyperscale
  │
  ├─ Sub-millisecond latency required?
  │   └─ YES → Business Critical
  │
  ├─ Unpredictable/intermittent workload?
  │   └─ YES → Serverless (General Purpose)
  │
  └─ Default → SQL Database (Single) - General Purpose (Provisioned)
```

---

## Additional Resources

- [Azure SQL Documentation](https://docs.microsoft.com/azure/azure-sql/)
- [Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [DTU Calculator](https://dtucalc.azurewebsites.net/)
- [Azure SQL Migration Guide](https://docs.microsoft.com/azure/azure-sql/migration-guides/)

---

*Last Updated: December 2025*
