# Azure SQL Migration Guide

## Table of Contents

- [Introduction](#introduction)
- [Migration Best Practices](#migration-best-practices)
- [Migration Tools Comparison](#migration-tools-comparison)
  - [Azure Database Migration Service (DMS)](#azure-database-migration-service-dms)
  - [Azure Migrate](#azure-migrate)
  - [SQL Server Migration Assistant (SSMA)](#sql-server-migration-assistant-ssma)
  - [Data Migration Assistant (DMA)](#data-migration-assistant-dma)
  - [Azure Data Studio](#azure-data-studio)
- [Tool Selection Guide](#tool-selection-guide)
- [Migration Workflow](#migration-workflow)
- [Real-World Migration Scenarios](#real-world-migration-scenarios)
- [References](#references)

## Introduction

Migrating SQL Server databases to Azure requires careful planning and selection of the right tools. This guide provides comprehensive information about available migration tools, best practices, and step-by-step workflows to ensure successful migration to Azure SQL Database, Azure SQL Managed Instance, or SQL Server on Azure VMs.

### Key Migration Considerations

- **Downtime requirements**: Online vs offline migration
- **Database size**: Small (< 50 GB), Medium (50-500 GB), Large (> 500 GB)
- **Source version**: SQL Server version compatibility
- **Target platform**: SQL Database, Managed Instance, or Azure VMs
- **Network connectivity**: ExpressRoute, VPN, or public internet
- **Administrative effort**: Fully managed vs self-managed tools

## Migration Best Practices

### From SQL Server to SQL Database

1. **Assess compatibility** - Use Azure SQL Migration extension
2. **Test with Azure SQL Database** - Validate application compatibility
3. **Use Data Migration Assistant** - Identify blocking issues
4. **Consider Elastic Database Tools** - For sharding scenarios
5. **Test thoroughly** - Performance and functionality

### From SQL Server to Managed Instance

1. **Check compatibility** - Near 100% compatible
2. **Use Azure Database Migration Service** - Online or offline migration
3. **Plan networking** - VNet integration required
4. **Test failover** - Validate disaster recovery
5. **Monitor performance** - Compare with on-premises

## Migration Tools Comparison

When migrating SQL Server databases to Azure, several tools are available. Understanding the purpose and best use cases for each tool is critical for choosing the right solution.

### Azure Database Migration Service (DMS)

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

**When to Use**: Use Azure Database Migration Service when you need a fully managed migration solution that minimizes administrative overhead. It's ideal for offline migrations where downtime is acceptable and you want the service to handle most of the complexity automatically.

---

### Azure Migrate

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

---

### SQL Server Migration Assistant (SSMA)

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

---

### Data Migration Assistant (DMA)

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

---

### Azure Data Studio

**Azure Data Studio** is a cross-platform database tool that provides a modern editor experience with IntelliSense, code snippets, source control integration, and an integrated terminal. When combined with the Azure SQL Migration extension, it becomes a powerful tool for minimal-downtime migrations.

**Key Features**:
- Cross-platform support (Windows, macOS, Linux)
- Connects immediately to Azure SQL and SQL Server instances
- Integrates with Azure Database Migration Service through extensions
- Supports online migration scenarios for minimal downtime
- Modern, lightweight alternative to SQL Server Management Studio
- Supports SQL Server 2008 and newer versions
- Built-in migration assessment and execution capabilities via Azure SQL Migration extension

**Best For**:
- ✅ Online migrations requiring minimal downtime
- ✅ Migrating from SQL Server 2008+ to Azure SQL Managed Instance
- ✅ Cross-platform migration scenarios
- ✅ Developers and DBAs preferring modern tooling
- ✅ Small to medium-sized database migrations (< 100 GB) with downtime concerns
- ✅ When continuous availability during migration is critical

**Migration Capabilities with Azure SQL Migration Extension**:
- Online migration with minimal downtime
- Offline migration support
- Pre-migration assessment
- Migration progress monitoring
- Automatic retry and error handling
- Integration with Azure Database Migration Service backend

**Limitations**:
- ❌ Requires Azure SQL Migration extension installation
- ❌ May require additional configuration for complex network scenarios
- ❌ Not as feature-complete as SSMS for some administrative tasks

**When to Use**: Use Azure Data Studio when migrating SQL Server databases to Azure SQL Managed Instance with the primary requirement of **minimizing downtime**. The online migration capabilities through the Azure SQL Migration extension make it ideal for production databases that need to remain available during migration. For offline migrations where administrative effort minimization is more important than downtime, Azure Database Migration Service alone may be sufficient.

---

## Tool Selection Guide

| Scenario | Recommended Tool | Alternative Tools |
|----------|------------------|-------------------|
| **Offline SQL Server to SQL Managed Instance migration** | Azure Database Migration Service | - |
| **Online SQL Server to SQL Managed Instance migration (minimal downtime)** | Azure Data Studio (with Azure SQL Migration extension) | Azure Database Migration Service |
| **Assessment and discovery** | Azure Migrate | Data Migration Assistant |
| **Compatibility assessment** | Data Migration Assistant | Azure Migrate |
| **Oracle to Azure SQL migration** | SQL Server Migration Assistant | - |
| **MySQL to Azure SQL migration** | SQL Server Migration Assistant | Azure Database Migration Service |
| **Large-scale infrastructure migration** | Azure Migrate + Azure Database Migration Service | - |

## Migration Workflow

### Migration Workflow for SQL Server to Azure SQL Managed Instance

**Recommended Approach**:

#### 1. Assessment Phase
- Use **Azure Migrate** for discovery and resource sizing
- Use **Data Migration Assistant (DMA)** for detailed compatibility analysis
- Review assessment reports and identify potential blockers

#### 2. Planning Phase
- Determine target Azure SQL configuration
- Plan networking (VNet integration for Managed Instance)
- Schedule downtime for offline migration
- Test migration in non-production environment

#### 3. Migration Phase
- Use **Azure Database Migration Service** for actual migration
- Choose online or offline migration mode
- Monitor migration progress through Azure portal

#### 4. Validation Phase
- Verify data integrity
- Test application connectivity
- Validate performance
- Conduct user acceptance testing

#### 5. Cutover Phase
- Switch applications to Azure SQL Managed Instance
- Monitor performance and errors
- Maintain on-premises backup for rollback period

---

## Real-World Migration Scenarios

### Scenario 1: Offline Migration with Minimal Administrative Effort

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

---

### Scenario 2: Online Migration with Minimal Downtime

**Question**: You have an on-premises Microsoft SQL Server 2008 instance that hosts a 50-GB database. You need to migrate the database to an Azure SQL Managed Instance. The solution must minimize downtime. What should you use?

**Answer**: **Azure Data Studio**

**Explanation**: Azure Data Studio is the correct choice for minimizing downtime during migration because:
- It is a cross-platform database tool supporting database development and management across different operating systems
- Provides immediate connection capabilities to Azure SQL and SQL Server instances
- Supports migrating on-premises SQL Server 2008 instances to Azure SQL Managed Instance
- Optimized for minimal downtime migration scenarios through online migration capabilities
- Integrates with Azure Database Migration Service through the Azure SQL Migration extension

**Key Distinction**: While Azure Database Migration Service is excellent for offline migrations with minimal administrative effort, **Azure Data Studio with the Azure SQL Migration extension** is specifically designed for **online migrations that minimize downtime**. This is the critical difference for scenarios where keeping the database available during migration is the primary requirement.

**Why Other Tools Are Not Suitable**:

**Azure Migrate**:
- Offers comprehensive tools for discovery, assessment, and migration (Azure Migrate: Discovery and Assessment, Migration and Modernization)
- Optimizes evaluation of on-premises SQL Server instances and databases
- Facilitates migration to Azure SQL Managed Instance, Azure SQL Database, or SQL Server on Azure VMs
- Extends capabilities to web applications (Azure App Service, Azure Kubernetes Service)
- Handles large-scale data migrations using Azure Data Box products
- Seamless integration with other Azure services and ISV tools
- **Limitation**: Not the most suitable tool for minimal downtime migrations of individual databases. Better suited for large-scale infrastructure migrations and assessment phases.

**WANdisco LiveData Platform for Azure**:
- Offers continuous data transfer and downtime elimination
- Provides full control of bandwidth consumption
- **Limitation**: Not suitable for smaller-scale migrations (50-GB database). Designed for continuous data transfer which implies ongoing operations rather than one-time migration with minimal downtime. The continuous transfer model doesn't align with the goal of a quick, minimal-downtime migration scenario.

**SQL Server Management Studio (SSMS)**:
- Integrated environment for managing SQL infrastructure
- Provides access, configuration, administration, and development features
- Supports SQL Server, Azure SQL Database, Azure SQL Managed Instance, SQL Server on Azure VMs, and Azure Synapse Analytics
- Comprehensive utility with graphical tools and script editors
- **Limitation**: Primarily designed for database management, not specifically as a dedicated tool for seamless, minimal-downtime database migration. While it supports data import and export, it doesn't optimize for downtime reduction when migrating 50-GB databases from SQL Server 2008 to Azure SQL Managed Instance.

**Key Takeaway**: For **minimal downtime** migrations, use Azure Data Studio. For **minimal administrative effort** with offline migrations, use Azure Database Migration Service. Understanding this distinction is crucial for selecting the right tool.

**References**:
- [What is Azure Data Studio](https://learn.microsoft.com/en-us/azure-data-studio/what-is-azure-data-studio)
- [Tutorial: Migrate SQL Server to Azure SQL Managed Instance online using Azure Data Studio](https://learn.microsoft.com/en-us/azure/dms/tutorial-sql-server-managed-instance-online-ads)
- [Azure Migrate Services Overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
- [WANdisco LiveData Platform Key Benefits](https://learn.microsoft.com/en-us/azure/storage/blobs/migrate-gen2-wandisco-live-data-platform#key-benefits-of-wandisco-livedata-platform-for-azure)
- [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/sql/ssms/sql-server-management-studio-ssms?view=sql-server-ver16)

---

### Scenario 3: Migrating SQL Server Data to Azure Cosmos DB

**Question**: You plan to import data from your on-premises environment into Azure. The data sources are:
- A Microsoft SQL Server 2014 database → Target: An Azure SQL database
- A table in a Microsoft SQL Server 2016 database → Target: An Azure Cosmos DB for NoSQL account

Which tool should you use to migrate the data from the table in the SQL Server 2016 database to Azure Cosmos DB?

**Answer**: **Azure Cosmos DB Data Migration Tool**

**Explanation**: Azure Cosmos DB Data Migration Tool is the correct choice for this scenario because:
- It is specifically designed to migrate data from various sources, including SQL Server, to Azure Cosmos DB for NoSQL
- It supports importing data from SQL Server tables and converting relational data into JSON documents suitable for Cosmos DB
- It handles the schema transformation required when moving from a relational database structure to a NoSQL document model
- It provides a straightforward migration path for structured data to Cosmos DB's document-oriented storage
- It is optimized for one-time or periodic data migration scenarios from relational databases to Cosmos DB

**Why Other Tools Are Not Suitable**:

**AzCopy**:
- Designed for transferring blobs and files to and from Azure Storage (Azure Blob Storage, Azure Files)
- Operates at the storage level for unstructured data
- Does not handle structured data migration or schema transformation
- **Limitation**: Not designed for migrating relational data from SQL Server to Cosmos DB. It cannot convert table structures to JSON documents or handle the data format transformations required for NoSQL migration.

**Data Management Gateway**:
- Used to enable on-premises data access for Azure Data Factory
- Acts as a bridge for Azure Data Factory to access on-premises data sources
- Facilitates hybrid data integration scenarios
- **Limitation**: Not a migration tool itself, but rather a connectivity component. It doesn't perform direct migration tasks or data transformation. It's used for ongoing data integration workflows, not for one-time migration projects.

**Data Migration Assistant (DMA)**:
- Designed for assessing and migrating SQL Server databases to Azure SQL Database or Azure SQL Managed Instance
- Identifies compatibility issues when upgrading to modern SQL Server versions
- Provides recommendations for performance and reliability improvements within SQL Server ecosystem
- **Limitation**: Only works within the SQL Server ecosystem (on-premises SQL Server to Azure SQL services). It cannot migrate data to Azure Cosmos DB or handle relational-to-NoSQL transformations.

**Key Considerations for SQL Server to Cosmos DB Migration**:
- Understand your data model transformation needs (relational to document-based)
- Plan for denormalization and embedding of related data
- Consider partitioning strategy for Cosmos DB
- Evaluate performance requirements and throughput (RU/s) needs
- Test queries and application logic with the new NoSQL model

**References**:
- [Azure Cosmos DB Data Migration Tool](https://learn.microsoft.com/en-us/azure/cosmos-db/import-data)
- [Migrate Data to Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/sql/migrate-relational-to-cosmos-db-sql-api)
- [AzCopy Overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Data Management Gateway for Azure Data Factory](https://learn.microsoft.com/en-us/azure/data-factory/v1/data-factory-data-management-gateway)

---

### Scenario 4: Migrating Multi-Database Applications with Cross-Database Queries

**Question**: You manage an application instance that consumes data from multiple databases. Application code references database tables using a combination of the server, database, and table name (three-part naming convention). You need to migrate the application data to Azure. To which two Azure services could you migrate the application to achieve the goal?

**Answer**: **SQL Server in Azure Virtual Machine** and **Azure SQL Managed Instance**

**Explanation**:

**SQL Server in Azure Virtual Machine** is correct because:
- Provides full control over the SQL Server instance, identical to on-premises behavior
- Preserves the existing database structure without modifications
- Supports multi-database references using three-part naming (server.database.table)
- Offers maximum compatibility with on-premises SQL Server features and configurations
- Requires minimal or no changes to existing application code
- Ideal for "lift-and-shift" scenarios where application code cannot be easily modified
- Allows complete administrative access for custom configurations and settings

**Azure SQL Managed Instance** is correct because:
- Supports cross-database queries natively, unlike Azure SQL Database
- Fully supports three-part naming conventions (server.database.schema.table) required for multi-database applications
- Provides near 100% compatibility with on-premises SQL Server features
- Offers a platform-as-a-service (PaaS) option, reducing management overhead compared to VMs
- Ideal for lifting and shifting complex applications with minimal code changes
- Supports SQL Agent jobs, linked servers, and other enterprise features
- Provides automatic patching, backups, and high availability

**Why Other Options Are Not Suitable**:

**SQL Server Stretch Database**:
- Designed specifically for archival purposes, extending "cold" data to Azure
- Only allows specific tables to be migrated to Azure for long-term storage
- Does not support cross-database queries or complex multi-database applications
- Primarily for data archiving scenarios, not full application migration
- **Limitation**: Cannot serve as a complete migration target for applications with multi-database dependencies. It's a hybrid solution for archiving historical data while keeping active data on-premises.

**Azure SQL Database**:
- Each database is an isolated deployment unit in Azure SQL Database
- Does not support cross-database queries using three-part naming in a straightforward manner
- Databases cannot reference each other directly using standard T-SQL syntax
- Would require significant application redesign to work around this limitation
- **Limitation**: While elastic queries can provide some cross-database functionality, they come with significant limitations, performance overhead, and require extensive configuration. The application would need substantial refactoring to eliminate three-part naming references, which contradicts the requirement of migrating the application "as-is."

**Migration Decision Criteria**:

| Consideration | SQL Server on Azure VM | Azure SQL Managed Instance |
|--------------|------------------------|---------------------------|
| **Management Overhead** | High (full VM management) | Low (PaaS, managed service) |
| **Cross-Database Support** | ✅ Full support | ✅ Full support |
| **SQL Server Compatibility** | ✅ 100% | ✅ Near 100% |
| **Administrative Control** | Complete | Limited (managed service) |
| **Automatic Updates** | Manual | Automatic |
| **Cost** | Higher (VM + licensing) | Moderate (PaaS pricing) |
| **Best For** | Maximum control needed | Minimal management overhead |

**Key Takeaway**: When migrating applications with cross-database dependencies:
- **Choose SQL Server on Azure VM** if you need complete administrative control, have custom configurations, or require specific SQL Server features
- **Choose Azure SQL Managed Instance** if you want a managed PaaS solution with reduced operational overhead while maintaining cross-database query support
- **Avoid Azure SQL Database** for applications heavily dependent on cross-database queries
- **Avoid SQL Server Stretch Database** for full application migrations (it's only for archival scenarios)

**References**:
- [SQL Server on Azure VMs Overview](https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/sql-server-on-azure-vm-iaas-what-is-overview)
- [Azure SQL Managed Instance Overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview)
- [Cross-Database Queries in SQL Managed Instance](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/features-comparison)
- [Azure SQL Database Limitations](https://learn.microsoft.com/en-us/azure/azure-sql/database/features-comparison)
- [SQL Server Stretch Database](https://learn.microsoft.com/en-us/sql/sql-server/stretch-database/stretch-database)

---

## Quick Decision Matrix

Use this matrix to quickly identify the right tool for your migration scenario:

| Your Requirement | Use This Tool |
|------------------|---------------|
| **Offline migration + Minimize admin effort** | Azure Database Migration Service |
| **Online migration + Minimize downtime** | Azure Data Studio (with Azure SQL Migration extension) |
| **Assessment before migration** | Azure Migrate or Data Migration Assistant |
| **Migrating from Oracle/MySQL** | SQL Server Migration Assistant (SSMA) |
| **Large-scale (100+ databases)** | Azure Database Migration Service |
| **SQL Server 2008 to Azure SQL MI** | Azure Data Studio (online) or Azure DMS (offline) |
| **SQL Server to Azure Cosmos DB** | Azure Cosmos DB Data Migration Tool |
| **Cross-database queries + Full control** | SQL Server on Azure VM |
| **Cross-database queries + PaaS** | Azure SQL Managed Instance |

---

## References

### Microsoft Documentation

- [Azure Database Migration Service Overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [What is Azure Data Studio](https://learn.microsoft.com/en-us/azure-data-studio/what-is-azure-data-studio)
- [Azure SQL Migration Extension](https://learn.microsoft.com/en-us/azure/dms/migration-using-azure-data-studio)
- [Azure Migrate Overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
- [SQL Server Migration Assistant](https://learn.microsoft.com/en-us/sql/ssma/sql-server-migration-assistant)
- [Data Migration Assistant](https://learn.microsoft.com/en-us/sql/dma/dma-overview)
- [Compare Migration Tools](https://learn.microsoft.com/en-us/sql/sql-server/migrate/dma-azure-migrate-compare-migration-tools)

### Tutorials

- [Tutorial: Migrate SQL Server to Azure SQL Managed Instance online using Azure Data Studio](https://learn.microsoft.com/en-us/azure/dms/tutorial-sql-server-managed-instance-online-ads)
- [Tutorial: Migrate SQL Server to Azure SQL Managed Instance offline using Azure Database Migration Service](https://learn.microsoft.com/en-us/azure/dms/tutorial-sql-server-managed-instance-offline-ads)
- [Assess SQL Server databases for migration to Azure SQL](https://learn.microsoft.com/en-us/sql/dma/dma-assesssqlonprem)

---

**Last Updated**: December 2025  
**Document Version**: 1.0
