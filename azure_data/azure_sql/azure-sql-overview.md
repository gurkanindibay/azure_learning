# Azure SQL - Complete Overview

## Table of Contents

- [Introduction](#introduction)
- [Azure SQL Product Family](#azure-sql-product-family)
- [Azure SQL Database](#azure-sql-database)
  - [Deployment Options](#deployment-options)
  - [Purchasing Models](#purchasing-models)
  - [Service Tiers](#service-tiers)
  - [Compute Tiers](#compute-tiers)
- [Azure SQL Managed Instance](#azure-sql-managed-instance)
- [SQL Server on Azure VMs](#sql-server-on-azure-vms)
- [Pricing Tiers Comparison](#pricing-tiers-comparison)
- [Feature Comparison](#feature-comparison)
- [Decision Guide](#decision-guide)
- [Best Practices](#best-practices)
- [References](#references)

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

✅ **Enable geo-replication** - Disaster recovery across regions  
✅ **Use zone-redundancy** - Protect against datacenter failures  
✅ **Configure failover groups** - Automatic failover capability  
✅ **Test failover procedures** - Ensure recovery processes work  
✅ **Monitor backup status** - Verify backups are successful  
✅ **Use Business Critical** - For mission-critical workloads  

### Security Best Practices

✅ **Enable Azure AD authentication** - Centralized identity management  
✅ **Use private endpoints** - Eliminate public internet exposure  
✅ **Enable Transparent Data Encryption (TDE)** - Encrypt data at rest  
✅ **Use Always Encrypted** - Protect sensitive data  
✅ **Enable Advanced Threat Protection** - Detect anomalous activities  
✅ **Implement row-level security** - Fine-grained access control  
✅ **Enable auditing** - Track database activities  
✅ **Regular security assessments** - Identify vulnerabilities  

### Migration Best Practices

#### From SQL Server to SQL Database
1. **Assess compatibility** - Use Azure SQL Migration extension
2. **Test with Azure SQL Database** - Validate application compatibility
3. **Use Data Migration Assistant** - Identify blocking issues
4. **Consider Elastic Database Tools** - For sharding scenarios
5. **Test thoroughly** - Performance and functionality

#### From SQL Server to Managed Instance
1. **Check compatibility** - Near 100% compatible
2. **Use Azure Database Migration Service** - Online or offline migration
3. **Plan networking** - VNet integration required
4. **Test failover** - Validate disaster recovery
5. **Monitor performance** - Compare with on-premises

### Migration Tools Comparison

When migrating SQL Server databases to Azure, several tools are available. Understanding the purpose and best use cases for each tool is critical for choosing the right solution.

#### Azure Database Migration Service (DMS)

**Azure Database Migration Service** is a fully managed solution designed for smooth migrations from multiple database sources to Azure data platforms, supporting both online and offline scenarios.

**Key Features**:
- Fully managed migration service
- Supports both online and offline migrations
- Minimizes downtime during migration
- Accessible through Azure portal, PowerShell, and Azure CLI
- Powered by Azure SQL Migration extension for Azure Data Studio
- Handles migrations to Azure SQL Database, Azure SQL Managed Instance, and SQL Server on Azure VMs
- Resilient and reliable throughout the migration process
- Minimal user involvement required

**Best For**:
- ✅ Offline migrations with minimal administrative effort
- ✅ Online migrations requiring minimal downtime
- ✅ Large-scale database migrations (50+ databases)
- ✅ Production workloads requiring managed service reliability
- ✅ Migrations to Azure SQL Managed Instance from on-premises SQL Server

**Use Case Example**:
*Migrating an on-premises SQL Server with 50 databases to Azure SQL Managed Instance in an offline scenario with minimal administrative effort.*

#### Azure Migrate

**Azure Migrate** is a comprehensive platform offering tools for discovery, assessment, and migration of servers, databases, and web applications.

**Key Features**:
- Discovery and assessment tools for on-premises resources
- Evaluation of SQL Server instances and databases
- Migration guidance to Azure SQL Managed Instance, Azure SQL Database, or SQL Server on Azure VMs
- Web application assessment and migration to Azure App Service and Azure Kubernetes Service
- Integration with Azure Data Box for large-scale data migrations
- Seamless integration with other Azure services and ISV tools

**Best For**:
- ✅ Assessment and discovery phase of migration planning
- ✅ Understanding migration readiness and compatibility
- ✅ Large-scale infrastructure migrations beyond just databases
- ✅ Migrating entire on-premises environments to Azure
- ✅ Cost estimation and sizing recommendations

**Limitations**:
- ❌ Not optimized for direct offline database migration scenarios
- ❌ Better suited for assessment than execution of migrations
- ❌ Requires additional tools for actual database migration

**When to Use**: Use Azure Migrate for the initial assessment phase to evaluate your on-premises SQL Server instances and determine the best Azure target (SQL Database, SQL Managed Instance, or SQL Server on Azure VMs). Follow up with Azure Database Migration Service for the actual migration execution.

#### SQL Server Migration Assistant (SSMA)

**SQL Server Migration Assistant** is a Microsoft tool designed to automate database migration to SQL Server from various non-Microsoft database platforms.

**Key Features**:
- Automated migration from Microsoft Access, DB2, MySQL, Oracle, and SAP ASE
- Assessment reports for compatibility analysis
- Converts database objects to SQL Server schema
- Ensures compatibility with Azure SQL services
- Schema and code conversion capabilities

**Best For**:
- ✅ Migrating from non-Microsoft database platforms to SQL Server
- ✅ Oracle to SQL Server migrations
- ✅ MySQL to Azure SQL Database migrations
- ✅ DB2 to SQL Server migrations
- ✅ Heterogeneous database migrations

**Limitations**:
- ❌ Not designed for SQL Server to SQL Server migrations
- ❌ Limited automation for offline migration scenarios
- ❌ Requires more manual intervention compared to DMS

**When to Use**: Use SSMA when migrating from Oracle, MySQL, DB2, or other non-Microsoft databases to SQL Server or Azure SQL. For SQL Server to Azure SQL migrations, prefer Azure Database Migration Service.

#### Data Migration Assistant (DMA)

**Data Migration Assistant** is an assessment tool that helps identify compatibility issues and provides recommendations for upgrading to modern SQL Server versions or Azure SQL platforms.

**Key Features**:
- Detects compatibility issues affecting database functionality
- Identifies potential migration blockers
- Provides performance and reliability improvement recommendations
- Assesses readiness for migration to Azure SQL Database or Azure SQL Managed Instance
- Generates detailed assessment reports

**Best For**:
- ✅ Pre-migration assessment and compatibility checks
- ✅ Identifying feature parity issues before migration
- ✅ Understanding potential breaking changes
- ✅ Planning and preparation phase of migration

**Limitations**:
- ❌ Does NOT perform actual database migration
- ❌ Assessment-only tool, requires other tools for migration execution
- ❌ Cannot minimize administrative effort for offline migrations

**When to Use**: Use DMA as a preliminary assessment tool before migration. It helps identify compatibility issues and prepares databases for migration, but you must use Azure Database Migration Service or other tools to perform the actual migration.

#### Tool Selection Guide

| Scenario | Recommended Tool | Alternative Tools |
|----------|------------------|-------------------|
| **Offline SQL Server to SQL Managed Instance migration** | Azure Database Migration Service | - |
| **Online SQL Server to SQL Managed Instance migration** | Azure Database Migration Service | - |
| **Assessment and discovery** | Azure Migrate | Data Migration Assistant |
| **Compatibility assessment** | Data Migration Assistant | Azure Migrate |
| **Oracle to Azure SQL migration** | SQL Server Migration Assistant | - |
| **MySQL to Azure SQL migration** | SQL Server Migration Assistant | Azure Database Migration Service |
| **Large-scale infrastructure migration** | Azure Migrate + Azure Database Migration Service | - |

#### Migration Workflow for SQL Server to Azure SQL Managed Instance

**Recommended Approach**:

1. **Assessment Phase**
   - Use **Azure Migrate** for discovery and resource sizing
   - Use **Data Migration Assistant (DMA)** for detailed compatibility analysis
   - Review assessment reports and identify potential blockers

2. **Planning Phase**
   - Determine target Azure SQL configuration
   - Plan networking (VNet integration for Managed Instance)
   - Schedule downtime for offline migration
   - Test migration in non-production environment

3. **Migration Phase**
   - Use **Azure Database Migration Service** for actual migration
   - Choose online or offline migration mode
   - Monitor migration progress through Azure portal

4. **Validation Phase**
   - Verify data integrity
   - Test application connectivity
   - Validate performance
   - Conduct user acceptance testing

5. **Cutover Phase**
   - Switch applications to Azure SQL Managed Instance
   - Monitor performance and errors
   - Maintain on-premises backup for rollback period

### Real-World Migration Question

**Question**: You have an on-premises Microsoft SQL Server named SQL1 that hosts 50 databases. You plan to migrate SQL1 to Azure SQL Managed Instance. You need to perform an offline migration of SQL1. The solution must minimize administrative effort. What should you include in the solution?

**Answer**: **Azure Database Migration Service (DMS)**

**Explanation**: Azure Database Migration Service is the correct choice for this scenario because:
- It is specifically designed for migrating SQL Server databases to Azure SQL Managed Instance
- It supports offline migration scenarios where downtime is acceptable
- It minimizes administrative effort through full automation and managed service capabilities
- It can handle large-scale migrations (50 databases) efficiently
- It provides resilience and reliability throughout the migration process
- It requires minimal user involvement compared to other migration tools

**Why Other Tools Are Not Suitable**:

- **Azure Migrate**: Better suited for assessment and discovery rather than direct migration execution. While it helps evaluate on-premises resources, it requires additional tools like Azure Database Migration Service for actual migration.

- **SQL Server Migration Assistant (SSMA)**: Designed for migrating from non-Microsoft database platforms (Oracle, MySQL, DB2) to SQL Server. Not optimized for SQL Server to Azure SQL Managed Instance migrations.

- **Data Migration Assistant (DMA)**: An assessment tool that identifies compatibility issues but does NOT perform actual migration. It must be paired with other tools like Azure Database Migration Service to execute the migration.

**References**:
- [Azure Database Migration Service Overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Compare SQL Server Database Migration Tools](https://learn.microsoft.com/en-us/sql/sql-server/migrate/dma-azure-migrate-compare-migration-tools?view=sql-server-ver16#azure-database-migration-service-dms)
- [SQL Server Migration Assistant](https://learn.microsoft.com/en-us/sql/ssma/sql-server-migration-assistant?view=sql-server-ver16#migration-sources)
- [Data Migration Assistant Overview](https://learn.microsoft.com/en-us/sql/dma/dma-overview?view=sql-server-ver16)
- [Azure Migrate Overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)

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
- [Azure Hybrid Benefit](https://learn.microsoft.com/azure/azure-sql/azure-hybrid-benefit)

### Pricing Calculators

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure SQL Database Pricing](https://azure.microsoft.com/pricing/details/azure-sql-database/)
- [Azure SQL Managed Instance Pricing](https://azure.microsoft.com/pricing/details/azure-sql-managed-instance/)

---

**Last Updated**: December 2025  
**Document Version**: 1.0
