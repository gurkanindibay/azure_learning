# Azure SQL - Complete Overview

## Table of Contents

- [Introduction](#introduction)
- [Azure SQL Product Family](#azure-sql-product-family)
- [Azure SQL Database](#azure-sql-database)
  - [Deployment Options](#deployment-options)
  - [Purchasing Models](#purchasing-models)
  - [Service Tiers](#service-tiers)
  - [Compute Tiers](#compute-tiers)
  - [High Availability and Zone Redundancy](#high-availability-and-zone-redundancy)
- [Azure SQL Managed Instance](#azure-sql-managed-instance)
- [SQL Server on Azure VMs](#sql-server-on-azure-vms)
- [Pricing Tiers Comparison](#pricing-tiers-comparison)
- [Feature Comparison](#feature-comparison)
- [Decision Guide](#decision-guide)
- [Migration to Azure SQL](#migration-to-azure-sql)
- [Best Practices](#best-practices)
- [Common Scenarios and Recommendations](#common-scenarios-and-recommendations)
- [Key Insights for Exams](#key-insights-for-exams)
- [References](#references)

> 📖 **For comprehensive migration information**, see the dedicated **[Azure SQL Migration Guide](./azure-sql-migration-guide.md)**

## Introduction

**Azure SQL** is a family of managed SQL Server database services running in the Azure cloud. It provides a range of deployment options from fully managed PaaS databases to infrastructure-as-a-service (IaaS) virtual machines, catering to different migration scenarios, workload requirements, and management preferences.

### Key Benefits

- **Fully Managed**: Automated patching, backups, and high availability
- **Built-in Intelligence**: Performance recommendations and automatic tuning
- **Scalability**: Scale up/down or scale out based on demand
- **Security**: Built-in advanced security features
- **Cost Optimization**: Pay only for what you use with flexible pricing models
- **High Availability**: Built-in 99.99%+ SLA

## Azure SQL Product Family

Azure SQL consists of three main products:

| Product | Type | Best For | Management Level |
|---------|------|----------|------------------|
| **Azure SQL Database** | PaaS | Modern cloud applications | Fully managed |
| **Azure SQL Managed Instance** | PaaS | Lift-and-shift migrations | Nearly 100% SQL Server compatibility |
| **SQL Server on Azure VMs** | IaaS | Full SQL Server control | Self-managed |

### Product Selection Flow

```
Need full SQL Server control? 
└─ YES → SQL Server on Azure VMs
└─ NO → Need instance-scoped features?
    └─ YES → SQL Managed Instance
    └─ NO → SQL Database
```

## Azure SQL Database

**Azure SQL Database** is a fully managed platform as a service (PaaS) database engine that handles database management functions including upgrading, patching, backups, and monitoring without user involvement.

### Deployment Options

#### 1. Single Database
**Isolated database with dedicated resources**

- Fully isolated resources
- Independent scaling and management
- Best for modern cloud applications
- Supports serverless compute tier
- Per-second billing available

**Use Cases**:
- Modern SaaS applications
- Microservices architectures
- Development/test environments
- Applications with predictable or unpredictable workloads (serverless)

#### 2. Elastic Pool
**Collection of databases sharing a set of resources**

- Shared resource pool across multiple databases
- Cost-effective for multiple databases
- Pool-level resource management
- Databases can have varying usage patterns

**Use Cases**:
- Multi-tenant SaaS applications
- Multiple databases with complementary usage patterns
- Cost optimization across database portfolio
- Unpredictable usage per database, but predictable aggregate

### Purchasing Models

Azure SQL Database offers two purchasing models:

#### vCore-Based Model (Recommended)

**Virtual Core (vCore)** model provides granular control over compute and storage resources.

**Characteristics**:
- Choose number of vCores (virtual cores)
- Choose memory (tied to vCore count)
- Choose storage independently
- Choose generation (Gen5, newer hardware)
- Better cost optimization
- Hybrid Benefit eligibility

**Components**:
```
Compute (vCores) + Storage (GB) + Backup Storage = Total Cost
```

**vCore Options**:
- 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 32, 40, 64, 80, 128 vCores
- Memory: ~5.1 GB per vCore (Gen5)

#### DTU-Based Model

**Database Transaction Unit (DTU)** is a blended measure of compute, memory, and I/O.

**Characteristics**:
- Simplified pricing - bundled resources
- Fixed ratios of CPU, memory, I/O
- Less flexibility
- Easier to understand for beginners
- No Hybrid Benefit

**DTU Tiers**:
- Basic: 5 DTUs
- Standard: 10, 20, 50, 100, 200, 400, 800, 1600, 3000 DTUs
- Premium: 125, 250, 500, 1000, 1750, 4000 DTUs

### Service Tiers

Azure SQL Database offers three service tiers with different performance and pricing characteristics:

#### General Purpose (Recommended for most workloads)

**Budget-oriented balanced compute and storage**

**Characteristics**:
- Standard availability: 99.99% SLA
- Remote storage (Azure Premium Storage)
- Storage: 1 GB - 4 TB (depends on vCore)
- Latency: 5-10ms
- Backup retention: 7-35 days

**Pricing (vCore)**:
- 2 vCores: ~$360/month
- 4 vCores: ~$720/month
- 8 vCores: ~$1,440/month

**Use Cases**:
- Most business workloads
- Development and test
- Web applications
- Small to medium-sized databases

#### Business Critical (High performance requirements)

**Highest performance and availability**

**Characteristics**:
- Premium availability: 99.99% SLA (99.995% zone-redundant)
- Local SSD storage
- Storage: 1 GB - 4 TB
- Latency: <2ms
- Built-in read replicas (1 free)
- Zone redundancy available

**Pricing (vCore)**:
- 2 vCores: ~$900/month
- 4 vCores: ~$1,800/month
- 8 vCores: ~$3,600/month

**Use Cases**:
- Mission-critical applications
- Low-latency requirements
- High transaction rate
- Read scale-out scenarios

#### Hyperscale (Massive databases)

**Highly scalable storage and compute**

**Characteristics**:
- Storage: Up to 100 TB
- Fast scaling (minutes, not hours)
- Multiple read replicas (up to 4)
- Fast backup and restore
- Independent compute and storage scaling

**Pricing (vCore)**:
- 2 vCores: ~$500/month
- 4 vCores: ~$1,000/month
- Plus storage costs (~$0.12/GB/month)

**Use Cases**:
- Very large databases (> 4 TB)
- Applications requiring rapid scale-up/down
- Need for multiple read replicas
- Fast backup/restore requirements

### Compute Tiers

#### Provisioned Compute

**Fixed resources allocated continuously**

**Characteristics**:
- Fixed compute size (always on)
- Predictable performance
- Billed per hour
- Best for steady workloads

**Pricing Example (General Purpose, 4 vCores)**:
```
Compute: 4 vCores × 24 hours × 30 days = $720/month
Storage: 100 GB × $0.12/GB = $12/month
Total: ~$732/month
```

**Use Cases**:
- Production applications
- Consistent usage patterns
- 24/7 availability requirements

#### Serverless Compute ⭐

**Auto-scaling compute with auto-pause**

**Characteristics**:
- Auto-scales between min and max vCores
- Auto-pauses during inactivity
- Per-second billing
- Automatic resume on connection

**Configuration**:
```
Min vCores: 0.5 - 40
Max vCores: 0.5 - 40
Auto-pause delay: 1 hour - 7 days (or disabled)
```

**Pricing Example (General Purpose, 0.5-4 vCores)**:
```
Active time: 8 hours/day at avg 2 vCores
Paused time: 16 hours/day

Compute: (8 × 2 vCores × 30 days) = ~$144/month
Storage: 100 GB × $0.12/GB = $12/month
Total: ~$156/month (vs $732 provisioned)
```

**Cost Savings**: Up to 80% for intermittent workloads

**Use Cases**:
- Development and test environments
- Unpredictable or intermittent workloads
- Infrequently used applications
- New applications with unknown patterns
- Cost optimization

**Limitations**:
- Only available in General Purpose tier
- Not available in Hyperscale (preview support varies)
- Resume delay (few seconds) on first connection after pause

### Service Tier Comparison Table

| Feature | General Purpose | Business Critical | Hyperscale |
|---------|----------------|-------------------|------------|
| **Use Case** | Most workloads | Mission-critical | Very large databases |
| **Storage Type** | Remote (Premium) | Local SSD | Multi-tier storage |
| **Max Storage** | 4 TB | 4 TB | 100 TB |
| **IOPS** | Up to 7,000 | Up to 200,000+ | Depends on replicas |
| **Latency** | 5-10ms | 1-2ms | 5-10ms (primary) |
| **Read Replicas** | ❌ | ✅ 1 included | ✅ Up to 4 |
| **Zone Redundancy** | ✅ Optional | ✅ Optional | ✅ Available |
| **Backup Retention** | 7-35 days | 7-35 days | 7-35 days |
| **Restore Time** | Depends on size | Depends on size | Fast (minutes) |
| **Serverless** | ✅ | ❌ | ⚠️ Preview | 
| **Price (4 vCore)** | ~$720/mo | ~$1,800/mo | ~$1,000/mo + storage |

### High Availability and Zone Redundancy

Azure SQL Database provides built-in high availability features that vary by service tier. Understanding these capabilities is crucial for designing business continuity solutions.

#### High Availability Architecture by Tier

**vCore-Based Service Tiers (General Purpose, Business Critical, Hyperscale)**:

##### General Purpose (vCore)
- **Standard Availability**: 99.99% SLA
- **Architecture**: Remote storage with compute node redundancy
- **Failover**: Automatic failover to standby replica
- **Zone Redundancy**: ✅ Available (optional configuration)
- **RPO (Recovery Point Objective)**: Typically < 30 seconds
- **RTO (Recovery Time Objective)**: Typically < 30 seconds
- **Data Loss During Failover**: Minimal (transactions in flight may be lost)

##### Business Critical (vCore)
- **Premium Availability**: 99.99% SLA (99.995% with zone redundancy)
- **Architecture**: Always On availability groups with local SSD storage
- **Failover**: Automatic failover with zero data loss
- **Zone Redundancy**: ✅ Available (optional configuration)
- **RPO (Recovery Point Objective)**: **0 (zero data loss)**
- **RTO (Recovery Time Objective)**: Typically < 30 seconds
- **Built-in Read Replicas**: 1 included for read scale-out
- **Data Loss During Failover**: **None** - fully synchronous replication

##### Hyperscale (vCore)
- **Availability**: 99.99% SLA (99.995% with zone redundancy)
- **Architecture**: Multi-tier storage with compute nodes
- **Failover**: Fast failover to standby compute nodes
- **Zone Redundancy**: ✅ Available (optional configuration)
- **RPO**: Typically < 30 seconds
- **RTO**: Typically < 30 seconds
- **Read Replicas**: Up to 4 named replicas
- **Note**: Does not support automatic failover with zero data loss like Business Critical

**DTU-Based Service Tiers (Basic, Standard, Premium)**:

##### Basic (DTU)
- **Availability**: 99.99% SLA
- **Architecture**: Single database instance with basic redundancy
- **Failover**: Automatic but slower recovery
- **Zone Redundancy**: ❌ Not supported
- **RPO**: Up to 60 seconds
- **RTO**: Can be several minutes
- **Use Case**: Non-critical, small workloads only
- **Limitations**: No zone redundancy, no active geo-replication

##### Standard (DTU)
- **Availability**: 99.99% SLA
- **Architecture**: Standard redundancy with remote storage
- **Failover**: Automatic failover to standby
- **Zone Redundancy**: ❌ Not supported
- **RPO**: Typically < 30 seconds
- **RTO**: Typically < 30 seconds
- **Data Loss During Failover**: Possible (transactions in flight)
- **Limitations**: No zone redundancy support

##### Premium (DTU)
- **Premium Availability**: 99.99% SLA (99.995% with zone redundancy)
- **Architecture**: Always On availability groups (similar to Business Critical)
- **Failover**: Automatic failover with zero data loss
- **Zone Redundancy**: ✅ **Supported**
- **RPO (Recovery Point Objective)**: **0 (zero data loss)**
- **RTO (Recovery Time Objective)**: Typically < 30 seconds
- **Active Geo-Replication**: ✅ Supported
- **Built-in Read Replicas**: 1 included for read scale-out
- **Data Loss During Failover**: **None** - fully synchronous replication

#### Zone Redundancy Support Summary

| Tier | Zone Redundancy | Zero Data Loss Failover | Cost Efficiency |
|------|----------------|-------------------------|-----------------|
| **Basic (DTU)** | ❌ No | ❌ No | Lowest cost, minimal HA |
| **Standard (DTU)** | ❌ No | ❌ No | Low cost, basic HA |
| **Premium (DTU)** | ✅ **Yes** | ✅ **Yes** | ✅ **Best for HA + cost** |
| **General Purpose (vCore)** | ✅ Yes | ❌ No | Medium cost |
| **Business Critical (vCore)** | ✅ Yes | ✅ Yes | Highest cost |
| **Hyperscale (vCore)** | ✅ Yes | ❌ No | High cost + scale |

#### Choosing the Right Tier for High Availability

**Scenario: Zero Data Loss + Zone Redundancy + Cost Optimization**

**Requirements**:
1. ✅ Failover between replicas must occur without any data loss (RPO = 0)
2. ✅ Database must remain available during a zone outage
3. ✅ Minimize costs

**Solution**: **Azure SQL Database Premium (DTU)** ⭐

**Why Premium is the Correct Choice**:

1. **Zero Data Loss (RPO = 0)**:
   - Uses Always On availability groups
   - Synchronous replication to secondary replicas
   - Automatic failover with no data loss

2. **Zone Redundancy**:
   - Supports zone-redundant configuration
   - Distributes replicas across availability zones
   - Database remains available during zone failures

3. **Cost Optimization**:
   - Less expensive than Business Critical (vCore)
   - Comparable high availability features
   - Suitable for most mission-critical workloads

**Why Other Tiers Don't Meet Requirements**:

❌ **Basic (DTU)**:
- No zone redundancy support
- Cannot guarantee zero data loss
- Not suitable for mission-critical workloads

❌ **Standard (DTU)**:
- No zone redundancy support
- Possible data loss during failover
- Not designed for high availability scenarios

❌ **Business Critical (vCore)**:
- ✅ Meets all technical requirements
- ❌ More expensive than Premium DTU
- ❌ Does not minimize costs (violates requirement #3)

❌ **Hyperscale (vCore)**:
- ✅ Supports zone redundancy
- ❌ Does not guarantee zero data loss (RPO not 0)
- ❌ Optimized for scale, not zero-data-loss HA
- ❌ Higher cost for features not needed

❌ **General Purpose (vCore)**:
- ✅ Supports zone redundancy
- ❌ Does not guarantee zero data loss
- ❌ Uses remote storage, not Always On

#### Key Insights for Business Continuity Solutions

**For Zero Data Loss Requirements**:
- Choose **Premium (DTU)** or **Business Critical (vCore)**
- Both use Always On availability groups
- Both provide synchronous replication
- Both support zone redundancy

**For Zone Outage Protection**:
- Enable zone-redundant configuration
- Available in: Premium, General Purpose (vCore), Business Critical (vCore), Hyperscale
- NOT available in: Basic, Standard

**For Cost Optimization with High Availability**:
- **Premium (DTU)** offers the best balance
- Provides enterprise-grade HA at lower cost than Business Critical
- Suitable for most mission-critical workloads

**For Active Geo-Replication**:
- Supported in Premium and Business Critical
- Enables read-scale and disaster recovery across regions
- Automatic failover groups provide seamless failover

#### References
- [Azure SQL Database High Availability](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla-local-zone-redundancy?view=azuresql&tabs=azure-powershell)
- [Azure SQL Database Service Tiers (DTU)](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tiers-dtu?view=azuresql)
- [Azure SQL Database Hyperscale](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tier-hyperscale?view=azuresql)

## Azure SQL Managed Instance

**Azure SQL Managed Instance** is a fully managed instance of SQL Server providing near 100% compatibility with SQL Server Enterprise Edition, making it ideal for lift-and-shift migrations.

### Key Features

#### Instance-Scoped Features
- SQL Server Agent
- Service Broker
- Database Mail
- Distributed transactions
- CLR (Common Language Runtime)
- Linked servers
- Cross-database queries

#### Networking
- Deployed in Azure VNet
- Private IP address
- Supports hybrid connectivity (VPN, ExpressRoute)
- Can join managed domain

#### Compatibility
- Near 100% compatibility with SQL Server
- Most SQL Server features supported
- Online migration tools available

### Service Tiers

#### General Purpose

**Cost-effective for most workloads**

**Characteristics**:
- Remote storage (Azure Premium Storage)
- 99.99% availability SLA
- Standard performance

**Pricing**:
- 4 vCores: ~$1,000/month
- 8 vCores: ~$2,000/month
- 16 vCores: ~$4,000/month

#### Business Critical

**High performance and availability**

**Characteristics**:
- Local SSD storage
- 99.99% availability SLA
- Built-in Always On Availability Group
- Free read replica

**Pricing**:
- 4 vCores: ~$2,500/month
- 8 vCores: ~$5,000/month
- 16 vCores: ~$10,000/month

### Use Cases

✅ **Use SQL Managed Instance When**:
- Migrating from SQL Server on-premises
- Need instance-scoped features (SQL Agent, Service Broker)
- Cross-database queries required
- Need managed domain integration
- Lift-and-shift with minimal changes

❌ **Don't Use When**:
- Modern cloud-native application
- Don't need SQL Server specific features
- Cost is primary concern
- Simpler management preferred

## SQL Server on Azure VMs

**SQL Server on Azure Virtual Machines** provides full control over SQL Server and OS, running on IaaS infrastructure.

### Key Features

- Full SQL Server control
- Full OS control
- Any SQL Server version
- Flexible licensing (BYOL, PAYG)
- Custom extensions and configurations
- Windows or Linux

### VM Sizes and Pricing

#### Small (Development/Test)
- **Standard_D2s_v3**: 2 vCores, 8 GB RAM
- SQL Server Standard: ~$190/month
- SQL Server Enterprise: ~$515/month

#### Medium (Production)
- **Standard_D8s_v3**: 8 vCores, 32 GB RAM
- SQL Server Standard: ~$760/month
- SQL Server Enterprise: ~$2,060/month

#### Large (High Performance)
- **Standard_E16s_v3**: 16 vCores, 128 GB RAM
- SQL Server Standard: ~$1,950/month
- SQL Server Enterprise: ~$4,120/month

### Use Cases

✅ **Use SQL Server on VMs When**:
- Need full SQL Server control
- Need OS-level access
- Custom SQL Server configuration required
- Specific SQL Server version needed
- Third-party tools requiring specific setup

❌ **Don't Use When**:
- Want minimal management overhead
- Don't need OS access
- Want automated patching/backups
- PaaS benefits desired

## Pricing Tiers Comparison

### Single Database - General Purpose (Serverless vs Provisioned)

| Configuration | Provisioned | Serverless (50% active) |
|---------------|-------------|-------------------------|
| 2 vCores | $360/month | ~$90/month |
| 4 vCores | $720/month | ~$180/month |
| 8 vCores | $1,440/month | ~$360/month |

**Savings**: Up to 75% for intermittent workloads

### Cross-Product Comparison (8 vCores, General Purpose)

| Product | Monthly Cost | Management | Best For |
|---------|--------------|------------|----------|
| **SQL Database (Provisioned)** | ~$1,440 | Fully managed | Modern apps |
| **SQL Database (Serverless avg)** | ~$360 | Fully managed | Intermittent use |
| **SQL Managed Instance** | ~$2,000 | Fully managed | Migrations |
| **SQL VM (Standard)** | ~$760 | Self-managed | Full control |
| **SQL VM (Enterprise)** | ~$2,060 | Self-managed | Full control + features |

### Service Tier Comparison (SQL Database, 4 vCores)

| Tier | Monthly Cost | IOPS | Max Storage | Best For |
|------|--------------|------|-------------|----------|
| **General Purpose** | ~$720 | ~7,000 | 4 TB | Most workloads |
| **Business Critical** | ~$1,800 | ~200,000 | 4 TB | Mission-critical |
| **Hyperscale** | ~$1,000+ | Varies | 100 TB | Large databases |

## Feature Comparison

### Azure SQL Products Feature Matrix

| Feature | SQL Database | SQL Managed Instance | SQL on VMs |
|---------|--------------|---------------------|------------|
| **Management** | Fully managed | Fully managed | Self-managed |
| **SQL Compatibility** | ~95% | ~100% | 100% |
| **Auto-scaling** | ✅ Serverless | ❌ | ⚠️ Manual |
| **Per-second billing** | ✅ Serverless | ❌ | ❌ |
| **Elastic pools** | ✅ | ✅ Instance pools | ❌ |
| **VNet injection** | ⚠️ Private endpoint | ✅ Native | ✅ Native |
| **SQL Agent** | ❌ | ✅ | ✅ |
| **Cross-DB queries** | ⚠️ Elastic queries | ✅ | ✅ |
| **Linked servers** | ❌ | ✅ Limited | ✅ Full |
| **Service Broker** | ❌ | ✅ | ✅ |
| **CLR** | ❌ | ✅ | ✅ |
| **Backup control** | ❌ Automated | ⚠️ Limited | ✅ Full |
| **Patching control** | ❌ Automated | ❌ Automated | ✅ Full |
| **OS access** | ❌ | ❌ | ✅ |
| **Max DB size** | 4 TB (100 TB Hyperscale) | 16 TB | Unlimited |
| **Geo-replication** | ✅ Active | ✅ Failover groups | ⚠️ Manual |

### Deployment Options Comparison

| Deployment | Resource Sharing | Scaling | Billing | Best For |
|------------|-----------------|---------|---------|----------|
| **Single Database** | Dedicated | Per database | Per database | Individual apps |
| **Elastic Pool** | Shared pool | Pool level | Per pool | Multi-tenant SaaS |
| **Managed Instance** | Instance | Instance level | Per instance | Instance migration |

## Decision Guide

### Question-Based Selection

#### Q1: Do you need full SQL Server and OS control?
- **YES** → SQL Server on Azure VMs
- **NO** → Continue to Q2

#### Q2: Do you need instance-scoped features (SQL Agent, Service Broker, cross-DB queries)?
- **YES** → Azure SQL Managed Instance
- **NO** → Continue to Q3

#### Q3: Is it a new cloud-native application?
- **YES** → Azure SQL Database (Single or Elastic Pool)
- **NO** → Continue to Q4

#### Q4: Do you have unpredictable or intermittent workload?
- **YES** → Azure SQL Database (Serverless)
- **NO** → Azure SQL Database (Provisioned)

#### Q5: Do you have multiple databases with varying usage?
- **YES** → Azure SQL Database (Elastic Pool)
- **NO** → Azure SQL Database (Single)

### Service Tier Selection (SQL Database)

#### Choose General Purpose when:
- ✅ Standard business workload
- ✅ Budget-conscious
- ✅ Storage < 4 TB
- ✅ Latency tolerance (5-10ms)

#### Choose Business Critical when:
- ✅ Mission-critical application
- ✅ Low latency required (<2ms)
- ✅ High transaction rate
- ✅ Need read replicas
- ✅ Zone redundancy needed

#### Choose Hyperscale when:
- ✅ Database > 4 TB
- ✅ Need rapid scaling
- ✅ Multiple read replicas needed
- ✅ Fast backup/restore critical

### Compute Tier Selection

#### Choose Provisioned when:
- ✅ Consistent 24/7 usage
- ✅ Production workload
- ✅ Predictable performance required
- ✅ No tolerance for cold start delay

#### Choose Serverless when:
- ✅ Development/test environments
- ✅ Intermittent usage patterns
- ✅ Cost optimization priority
- ✅ Unpredictable workload
- ✅ Can tolerate resume delay (seconds)

## Best Practices

### Cost Optimization

#### 1. Right-Size Resources
```
❌ Over-provisioned: 8 vCores, 20% avg CPU → $1,440/month
✅ Right-sized: 4 vCores, 60% avg CPU → $720/month
Savings: $720/month (50%)
```

#### 2. Use Serverless for Dev/Test
```
❌ Provisioned 4 vCores 24/7 → $720/month
✅ Serverless 4 vCores, 8hr/day → ~$180/month
Savings: $540/month (75%)
```

#### 3. Leverage Azure Hybrid Benefit
```
❌ Without Hybrid Benefit → $720/month
✅ With Hybrid Benefit (existing license) → $207/month
Savings: $513/month (71%)
```

#### 4. Use Elastic Pools for Multiple DBs
```
❌ 10 databases × $360 each → $3,600/month
✅ Elastic pool for 10 databases → $1,800/month
Savings: $1,800/month (50%)
```

#### 5. Reserved Capacity
```
❌ Pay-as-you-go: $720/month × 12 = $8,640/year
✅ 1-year reserved: ~$6,500/year
✅ 3-year reserved: ~$4,800/year
Savings: Up to 44%
```

### Performance Optimization

✅ **Use appropriate indexes** - Reduces I/O and improves query performance  
✅ **Enable automatic tuning** - AI-powered performance recommendations  
✅ **Use query performance insights** - Identify slow queries  
✅ **Scale up temporarily** - For known peak periods  
✅ **Use read replicas** - Offload read workloads (Business Critical)  
✅ **Implement connection pooling** - Reduce connection overhead  
✅ **Monitor DTU/vCore usage** - Identify bottlenecks  

### High Availability

> 📖 **For detailed high availability and zone redundancy information**, see the [High Availability and Zone Redundancy](#high-availability-and-zone-redundancy) section above.

✅ **Choose the right tier for your HA requirements**:
  - **Zero data loss required**: Premium (DTU) or Business Critical (vCore)
  - **Zone redundancy required**: Premium, General Purpose, Business Critical, or Hyperscale
  - **Cost optimization with HA**: Premium (DTU) offers best balance
  
✅ **Enable zone-redundancy** - Protect against datacenter/zone failures  
✅ **Enable geo-replication** - Disaster recovery across regions  
✅ **Configure failover groups** - Automatic failover capability with zone redundancy
✅ **Test failover procedures** - Ensure recovery processes work  
✅ **Monitor backup status** - Verify backups are successful  
✅ **Understand RPO/RTO requirements** - Select tier that meets objectives  

### Security Best Practices

✅ **Enable Azure AD authentication** - Centralized identity management  
✅ **Use private endpoints** - Eliminate public internet exposure  
✅ **Enable Transparent Data Encryption (TDE)** - Encrypt data at rest  
✅ **Use Always Encrypted** - Protect sensitive data  
✅ **Enable Advanced Threat Protection** - Detect anomalous activities  
✅ **Implement row-level security** - Fine-grained access control  
✅ **Enable auditing** - Track database activities  
✅ **Regular security assessments** - Identify vulnerabilities

#### Azure SQL Database Auditing

**Azure SQL Database Auditing** tracks database events and writes them to an audit log. It helps maintain regulatory compliance, understand database activity, and gain insights into potential security violations.

**Key Requirements and Constraints**:

1. **Regional Constraint for Storage Accounts**
   - The storage account used for storing audit logs **must be in the same region** as the SQL server
   - Example: If your SQL server is in East US, the storage account must also be in East US
   - Cross-region storage is not supported for audit log storage

2. **Service Tier Support**
   - Auditing is supported across all service tiers (Basic, Standard, Premium)
   - Available for all purchasing models (DTU-based and vCore-based)

3. **Storage Options**
   - **Azure Storage Account**: Store audit logs in blob storage
   - **Log Analytics Workspace**: Integrate with Azure Monitor for advanced querying
   - **Event Hub**: Stream audit logs to SIEM tools or external systems

4. **Audit Scope**
   - Database-level auditing: Applies to a specific database
   - Server-level auditing: Applies to all databases on the server

**Example Scenario**:

Given the following Azure resources:

| Resource | Type | Region | Details |
|----------|------|--------|---------|
| SQLsvr1 | SQL Server | East US | - |
| SQLsvr2 | SQL Server | West US | - |
| SQLdb1 | SQL Database | East US | Standard tier on SQLsvr1 |
| SQLdb2 | SQL Database | East US | Standard tier on SQLsvr1 |
| SQLdb3 | SQL Database | West US | Premium tier on SQLsvr2 |
| storage1 | Storage Account | East US | StorageV2 |
| storage2 | Storage Account | Central US | BlobStorage |

**Auditing Compatibility**:
- ✅ SQLdb1 → storage1: **Supported** (same region: East US)
- ✅ SQLdb2 → storage1: **Supported** (same region: East US)
- ❌ SQLdb1 → storage2: **Not supported** (different regions: East US vs Central US)
- ❌ SQLdb3 → storage1: **Not supported** (different regions: West US vs East US)

**Best Practices**:
- Enable auditing at the server level to audit all databases automatically
- Use Log Analytics for long-term retention and advanced analysis
- Configure retention policies based on compliance requirements
- Monitor audit logs regularly for suspicious activities

**Reference**: [Azure SQL Database Auditing Overview](https://learn.microsoft.com/azure/azure-sql/database/auditing-overview)  

### Migration to Azure SQL

For comprehensive information about migrating SQL Server databases to Azure, including detailed tool comparisons, best practices, and step-by-step workflows, see the dedicated **[Azure SQL Migration Guide](./azure-sql-migration-guide.md)**.

**Quick Migration Tool Reference**:

| Your Requirement | Recommended Tool |
|------------------|------------------|
| **Offline migration + Minimize admin effort** | Azure Database Migration Service |
| **Online migration + Minimize downtime** | Azure Data Studio (with Azure SQL Migration extension) |
| **Assessment before migration** | Azure Migrate or Data Migration Assistant |
| **Migrating from Oracle/MySQL** | SQL Server Migration Assistant |

For detailed explanations, real-world scenarios, and migration workflows, refer to the [Azure SQL Migration Guide](./azure-sql-migration-guide.md).

### Migration Tools Comparison (Quick Summary)

**Azure Database Migration Service (DMS)**: Fully managed service for offline migrations with minimal administrative effort. Best for large-scale migrations (50+ databases).

**Azure Data Studio**: Cross-platform tool with Azure SQL Migration extension for online migrations with minimal downtime. Ideal for production databases requiring continuous availability.

**Azure Migrate**: Assessment and discovery platform for migration planning, cost estimation, and compatibility analysis.

**Data Migration Assistant (DMA)**: Assessment-only tool for identifying compatibility issues before migration.

**SQL Server Migration Assistant (SSMA)**: For heterogeneous migrations from Oracle, MySQL, DB2 to SQL Server/Azure SQL.

> 📚 **For detailed tool comparisons, workflows, and real-world scenarios, see the [Azure SQL Migration Guide](./azure-sql-migration-guide.md)**

## Common Scenarios and Recommendations

### Scenario 1: New Modern Web Application
**Requirements**: Auto-scaling, cost optimization, simple management

**Recommendation**: 
- **Azure SQL Database** (Single Database)
- **Serverless** compute tier
- **General Purpose** service tier

**Why**: Modern cloud-native design, per-second billing, auto-scaling, minimal management

### Scenario 2: Multi-Tenant SaaS Application
**Requirements**: Multiple databases, cost efficiency, varying usage patterns

**Recommendation**:
- **Azure SQL Database** (Elastic Pool)
- **Provisioned** compute tier
- **General Purpose** service tier

**Why**: Resource sharing across tenants, cost-effective, pool-level management

### Scenario 3: Migrating SQL Server Enterprise
**Requirements**: Minimal code changes, SQL Agent, cross-database queries

**Recommendation**:
- **Azure SQL Managed Instance**
- **General Purpose** service tier

**Why**: Near 100% SQL Server compatibility, instance-scoped features, lift-and-shift

### Scenario 4: Mission-Critical OLTP Application
**Requirements**: Low latency, high availability, read scale-out

**Recommendation**:
- **Azure SQL Database** (Single Database)
- **Provisioned** compute tier
- **Business Critical** service tier
- **Zone redundancy** enabled

**Why**: <2ms latency, local SSD, built-in read replica, 99.995% SLA

### Scenario 5: Large Data Warehouse
**Requirements**: 10 TB database, multiple read workloads, fast scaling

**Recommendation**:
- **Azure SQL Database** (Hyperscale)
- **Provisioned** compute tier
- **4 read replicas**

**Why**: Up to 100 TB storage, fast scaling, multiple read replicas, cost-effective for large DBs

### Scenario 6: Development and Test Environment
**Requirements**: Used 8 hours/day, cost optimization, temporary databases

**Recommendation**:
- **Azure SQL Database** (Single Database)
- **Serverless** compute tier (0.5-4 vCores)
- **General Purpose** service tier
- **Auto-pause enabled** (60 min)

**Why**: Up to 80% cost savings, pay per second of use, auto-pause during inactivity

### Scenario 7: Enterprise Migration with High Resiliency Requirements (Litware Inc. Case Study)
**Requirements**: 
- Migrating on-premises databases (DB1 and DB2) to Azure
- Must maintain availability if two availability zones in the region fail
- Minimal I/O latency for optimal performance
- Minimal administrative effort and operational complexity
- Near 100% SQL Server feature compatibility
- Support for advanced features like automatic failover and geo-replication

**Recommendation**:
- **Azure SQL Managed Instance**
- **Business Critical** service tier (for optimal I/O latency)
- **Zone-redundant configuration** enabled
- **Geo-replication** for disaster recovery

**Why**: 
- **Resiliency**: Azure SQL Managed Instance supports zone-redundant configuration and automatic failover, ensuring availability even if two availability zones fail. Geo-replication provides additional disaster recovery capabilities.
- **Performance**: Business Critical tier uses local SSD storage, delivering minimal I/O latency required for DB1 and DB2.
- **Minimal Administrative Effort**: As a fully managed PaaS service, it offloads tasks such as automated backups, patching, and high availability setup, significantly reducing operational complexity.
- **SQL Server Compatibility**: Near 100% compatibility with on-premises SQL Server Enterprise Edition, allowing lift-and-shift migrations with minimal code changes.
- **Advanced Features**: Supports enterprise-grade capabilities like SQL Server Agent, Service Broker, cross-database queries, and distributed transactions.

**Why Other Options Are Incorrect**:
- **Single Azure SQL Database**: While it can be made zone-redundant in premium tiers, it lacks the broad SQL Server feature compatibility and enterprise-grade scalability required for complex workloads like DB1 and DB2. It's best suited for standalone or less complex databases.
- **Azure SQL Database Elastic Pool**: Designed for managing multiple databases with varying usage patterns in a cost-effective manner. It does not offer the resiliency features (zone redundancy across multiple zones) or low-latency performance needed for mission-critical databases that must remain available during zone failures.

**Reference Links**:
- [Azure SQL High Availability SLA](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla)
- [Azure SQL Managed Instance PaaS Overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview?view=azuresql)

---

## Exam Practice Questions

### Question 1: Enterprise Database Migration with Resiliency Requirements (Litware Inc.)

**Scenario**: Refer to the Litware Inc. case study. You plan to migrate DB1 and DB2 to Azure. You need to ensure that the Azure database and the service tier meet the resiliency and business requirements.

**Question**: What should you configure for the Database?

**Options**:
- A) A single Azure SQL database
- B) Azure SQL managed instance
- C) An Azure SQL Database elastic pool

**Correct Answer**: **B) Azure SQL managed instance**

**Explanation**:

Azure SQL managed instance is correct because it allows you to bring your on-premises SQL Server databases to Azure with minimal administrative effort while maintaining high compatibility with existing SQL Server features. It supports advanced capabilities like automatic failover, zone-redundant configuration, and geo-replication, which satisfy the requirement to maintain availability if two availability zones in the region fail. Additionally, it is optimized for minimal I/O latency, meeting the performance expectations of DB1 and DB2. As a fully managed service, it also offloads tasks such as backups, patching, and high availability setup, directly supporting the business requirement to minimize both administrative effort and operational complexity.

**Why Other Options Are Incorrect**:

**A single Azure SQL database** is incorrect because it is best suited for standalone or less complex databases and may not support all SQL Server features. While it can be made zone-redundant in premium tiers, it lacks the broad feature compatibility and scalability required for enterprise-grade workloads like DB1 and DB2.

**An Azure SQL Database elastic pool** is incorrect because it is designed to manage multiple databases with varying usage patterns in a cost-effective manner. It does not offer the resiliency features or low-latency performance needed for critical databases that must remain available and performant during zone failures.

**Reference Links**:
- [Azure SQL High Availability SLA](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla)
- [Azure SQL Managed Instance PaaS Overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview?view=azuresql)

**Domain**: Design data storage solutions

---

### Question 2: Service Tier Selection for High-Availability Requirements (Litware Inc.)

**Scenario**: Refer to the Litware Inc. case study. You plan to migrate DB1 and DB2 to Azure. You need to ensure that the Azure database and the service tier meet the resiliency and business requirements.

**Question**: What should you configure for the Service tier?

**Options**:
- A) Hyperscale
- B) Business Critical
- C) General Purpose

**Correct Answer**: **B) Business Critical**

**Explanation**:

**Business Critical** is correct because it is the only tier that meets all three resiliency requirements specified in the case study: 
1. Maintain availability even if two availability zones fail
2. Fail over automatically
3. Minimize I/O latency

The Business Critical tier is built for high-performance transactional workloads and provides zone-redundant configurations through synchronous replication across availability zones. It also uses local SSD-based storage, which ensures low latency and high throughput. Furthermore, since it is a platform-as-a-service (PaaS) offering, it also meets the requirement to minimize administrative effort.

**Why Other Options Are Incorrect**:

**General Purpose** is incorrect because although it offers zone redundancy, it relies on remote storage, which introduces higher I/O latency and lower throughput. This violates the requirement to minimize I/O latency. Additionally, the resiliency through zone redundancy in this tier is not generally available in all regions, making it less reliable for mission-critical workloads that demand proven zone failure resilience.

**Hyperscale** is incorrect because it is designed for extremely large databases and scale-out read scenarios, not high-availability transactional systems. Importantly, Hyperscale does not currently support zone redundancy, so it cannot meet the requirement to maintain availability if two availability zones fail, making it an unsuitable choice in this scenario.

**Reference Links**:
- [Azure SQL Database Service Tiers - When to Choose Business Critical](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tiers-sql-database-vcore?view=azuresql#when-to-choose-this-service-tier-1)
- [Azure SQL High Availability SLA](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla)

**Domain**: Design data storage solutions

---

### Question 3: Azure SQL Database Auditing Storage Requirements

**Scenario**: You have an Azure subscription that contains the following resources:

**SQL Servers**:
| Name | Resource Group | Location |
|------|----------------|----------|
| SQLsvr1 | RG1 | East US |
| SQLsvr2 | RG2 | West US |

**Storage Accounts**:
| Name | Resource Group | Location | Account Kind |
|------|----------------|----------|--------------|
| storage1 | RG1 | East US | StorageV2 (general purpose v2) |
| storage2 | RG2 | Central US | BlobStorage |

**Azure SQL Databases**:
| Name | Resource Group | Server | Pricing Tier |
|------|----------------|--------|--------------|
| SQLdb1 | RG1 | SQLsvr1 | Standard |
| SQLdb2 | RG1 | SQLsvr1 | Standard |
| SQLdb3 | RG2 | SQLsvr2 | Premium |

**Question**: When you enable auditing for SQLdb1, can you store the audit information to storage1?

**Options**:
- A) Yes
- B) No

**Correct Answer**: **A) Yes**

**Explanation**:

Yes is correct because SQLdb1 is a Standard tier Azure SQL Database hosted on SQLsvr1, which is deployed in the East US region. The target storage account storage1 is also located in East US, which meets the requirement for storing audit logs — **the storage account must be in the same region as the SQL server**.

Additionally, SQL auditing is supported for databases in the Standard tier, and since both the database and the storage account reside in the same region, storing audit logs from SQLdb1 to storage1 is fully supported.

**Key Requirements for Azure SQL Database Auditing**:
1. ✅ Storage account must be in the **same region** as the SQL server
2. ✅ Auditing is supported across **all service tiers** (Basic, Standard, Premium)
3. ✅ Both DTU-based and vCore-based purchasing models support auditing

**Analysis of the Scenario**:
- SQLdb1 is on SQLsvr1 (East US) → storage1 (East US): ✅ **Supported** (same region)
- SQLdb1 is on SQLsvr1 (East US) → storage2 (Central US): ❌ **Not supported** (different regions)
- SQLdb3 is on SQLsvr2 (West US) → storage1 (East US): ❌ **Not supported** (different regions)

**Reference**: [Azure SQL Database Auditing Overview](https://learn.microsoft.com/azure/azure-sql/database/auditing-overview)

**Domain**: Design data storage solutions

---

## Key Insights for Exams

### Critical Points

1. **Serverless = Auto-scaling + Per-second billing**
   > Only Single Database supports true per-second billing with auto-scaling via Serverless compute tier

2. **Elastic Pool ≠ Auto-scaling per database**
   > Elastic pools scale at pool level, not individual database level. Resources are shared.

3. **Managed Instance = Near 100% SQL Server compatibility**
   > Choose for lift-and-shift migrations requiring instance-scoped features (SQL Agent, Service Broker)

4. **Business Critical = Local SSD + Read Replica**
   > Business Critical uses local SSD for low latency and includes one free read replica

5. **Hyperscale = Large databases + Fast scaling**
   > Use Hyperscale for databases >4 TB or when rapid scaling is required

6. **Azure Hybrid Benefit = Up to 71% savings**
   > Bring existing SQL Server licenses for significant cost reduction

7. **Zone Redundancy = Higher availability**
   > Zone redundant increases SLA to 99.995% (vs 99.99%)

8. **Single Database vs Elastic Pool**
   > Single DB = dedicated resources | Elastic Pool = shared resources across multiple DBs

9. **Managed Instance for High Resiliency Requirements**
   > When requirements include availability across multiple availability zone failures, minimal I/O latency, and minimal administrative effort, Azure SQL Managed Instance is the correct choice. It supports zone-redundant configuration, automatic failover, geo-replication, and uses local SSD storage (Business Critical tier) for optimal performance while being fully managed.

10. **Auditing Storage Account = Same Region as SQL Server**
   > Azure SQL Database auditing requires the storage account to be in the same region as the SQL server. Cross-region storage is not supported for audit logs. Auditing is supported across all service tiers (Basic, Standard, Premium).

11. **Zero Data Loss Failover = Premium (DTU) or Business Critical (vCore)**
   > Only Premium (DTU) and Business Critical (vCore) tiers provide zero data loss (RPO = 0) during failover. They use Always On availability groups with synchronous replication. For cost optimization with zero data loss and zone redundancy requirements, Premium (DTU) is the most cost-effective option.

12. **Zone Redundancy for High Availability**
   > Basic and Standard (DTU) tiers do NOT support zone redundancy. For zone outage protection, use Premium (DTU), General Purpose (vCore), Business Critical (vCore), or Hyperscale. However, only Premium and Business Critical guarantee zero data loss during failover.

## Quick Reference Cheat Sheet

### When Requirements Say...

| Requirement | Answer |
|-------------|---------|
| "Auto-scales based on workload" | **Serverless** compute tier |
| "Per-second billing" | **Serverless** compute tier |
| "Multiple databases, cost-effective" | **Elastic Pool** |
| "SQL Agent, Service Broker" | **Managed Instance** or **SQL VM** |
| "Lift-and-shift from SQL Server" | **Managed Instance** |
| "Full OS control" | **SQL Server on Azure VMs** |
| "Mission-critical, low latency" | **Business Critical** tier |
| "Database > 4 TB" | **Hyperscale** tier |
| "Development/test environment" | **Serverless General Purpose** |
| "Modern cloud application" | **Single Database** |
| "Availability if two zones fail" | **Managed Instance** with zone redundancy |
| "Minimal I/O latency + minimal admin" | **Managed Instance Business Critical** |
| "High resiliency + enterprise features" | **Managed Instance** with geo-replication |
| "Store audit logs to storage account" | Storage account must be in **same region** as SQL server |
| "Zero data loss + zone redundancy + minimize cost" | **Premium (DTU)** tier |
| "No data loss during failover" | **Premium (DTU)** or **Business Critical (vCore)** |
| "Zone outage protection" | **Premium**, **General Purpose**, **Business Critical**, or **Hyperscale** (NOT Basic/Standard) |
| "RPO = 0 (zero data loss)" | **Premium (DTU)** or **Business Critical (vCore)** only |

## References

### Microsoft Documentation

- [Azure SQL Database Overview](https://learn.microsoft.com/azure/azure-sql/database/sql-database-paas-overview)
- [Serverless Compute Tier](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-overview)
- [Azure SQL Managed Instance](https://learn.microsoft.com/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview)
- [SQL Server on Azure VMs](https://learn.microsoft.com/azure/azure-sql/virtual-machines/windows/sql-server-on-azure-vm-iaas-what-is-overview)
- [vCore Model](https://learn.microsoft.com/azure/azure-sql/database/service-tiers-vcore)
- [DTU Model](https://learn.microsoft.com/azure/azure-sql/database/service-tiers-dtu)
- [Elastic Pools](https://learn.microsoft.com/azure/azure-sql/database/elastic-pool-overview)
- [Service Tiers](https://learn.microsoft.com/azure/azure-sql/database/service-tiers-general-purpose-business-critical)
- [High Availability and Zone Redundancy](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla-local-zone-redundancy?view=azuresql&tabs=azure-powershell)
- [Service Tiers - DTU Model](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tiers-dtu?view=azuresql)
- [Hyperscale Service Tier](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tier-hyperscale?view=azuresql)
- [Azure Hybrid Benefit](https://learn.microsoft.com/azure/azure-sql/azure-hybrid-benefit)
- [Azure SQL Database Auditing](https://learn.microsoft.com/azure/azure-sql/database/auditing-overview)

### Pricing Calculators

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure SQL Database Pricing](https://azure.microsoft.com/pricing/details/azure-sql-database/)
- [Azure SQL Managed Instance Pricing](https://azure.microsoft.com/pricing/details/azure-sql-managed-instance/)

---

**Last Updated**: December 2025  
**Document Version**: 1.0
