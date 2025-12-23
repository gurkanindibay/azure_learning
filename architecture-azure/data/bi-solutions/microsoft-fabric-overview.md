# Microsoft Fabric Overview

Microsoft Fabric is an all-in-one analytics solution for enterprises that covers everything from data movement to data science, real-time analytics, and business intelligence. It offers a comprehensive suite of services including Data Factory, Data Engineering, Data Warehouse, Data Science, Real-Time Analytics, and Power BI.

## Key Characteristics

- **Unified Platform**: Single, integrated environment for all analytics workloads
- **OneLake**: Built-in data lake that serves as the single source of truth for all data
- **SaaS Solution**: Fully managed Software-as-a-Service with minimal infrastructure management
- **Copilot Integration**: AI-powered assistance throughout the platform
- **Lake-centric Architecture**: All data stored in open Delta Lake format

## Core Components

| Component | Description |
|-----------|-------------|
| **Data Factory** | Data integration and ETL/ELT pipelines |
| **Data Engineering** | Spark-based data transformation and processing |
| **Data Warehouse** | T-SQL based analytics with separation of compute and storage |
| **Data Science** | Machine learning model development and deployment |
| **Real-Time Analytics** | Stream processing and real-time data analysis (KQL-based) |
| **Power BI** | Business intelligence and visualization |

## OneLake - The Foundation

OneLake is Microsoft Fabric's unified data lake:

- **Single Data Copy**: Eliminates data silos and duplication
- **Open Format**: Uses Delta Lake (Parquet) format for all data
- **Automatic Discovery**: All data automatically indexed and discoverable
- **Shortcuts**: Connect to external data sources without copying data
- **Cross-Workload Access**: All Fabric workloads access the same data

## Capacity and Licensing

### Capacity Units (CUs)

Microsoft Fabric uses a capacity-based licensing model:

| SKU | Capacity Units | Use Case |
|-----|----------------|----------|
| F2 | 2 CUs | Development/Testing |
| F4 | 4 CUs | Small workloads |
| F8 | 8 CUs | Small to medium workloads |
| F16 | 16 CUs | Medium workloads |
| F32 | 32 CUs | Medium to large workloads |
| F64+ | 64+ CUs | Enterprise workloads |

### Scaling Options

- **Vertical Scaling**: Upgrade/downgrade capacity SKU
- **Pause/Resume**: Pause capacity when not in use to save costs
- **Bursting**: Temporary capacity increase for peak workloads

## Real-Time Analytics in Fabric

Fabric's Real-Time Analytics is powered by Azure Data Explorer technology:

- **KQL Database**: Native Kusto Query Language support
- **Eventstreams**: Real-time data ingestion from multiple sources
- **KQL Querysets**: Save and share KQL queries
- **Real-Time Dashboards**: Live visualizations of streaming data

## Data Warehouse in Fabric

- **T-SQL Support**: Familiar SQL Server syntax
- **Automatic Optimization**: Query optimization without manual tuning
- **Direct Lake Mode**: Query data directly from OneLake without import
- **Cross-Database Queries**: Query across multiple warehouses

## Integration Capabilities

### Data Sources

- Azure services (Blob Storage, SQL Database, Cosmos DB, etc.)
- On-premises data sources via gateway
- Third-party SaaS applications
- Streaming sources (Event Hubs, Kafka, IoT Hub)

### Downstream Integration

- Power BI for visualization
- Azure Machine Learning
- Microsoft 365 applications
- Third-party BI tools via XMLA endpoint

## Security and Governance

| Feature | Description |
|---------|-------------|
| **Row-Level Security** | Restrict data access at row level |
| **Column-Level Security** | Restrict access to specific columns |
| **Data Masking** | Dynamic masking of sensitive data |
| **Sensitivity Labels** | Microsoft Purview integration |
| **Workspace Permissions** | Role-based access control |
| **Endorsement** | Certify and promote trusted content |

## Use Cases

### When to Use Microsoft Fabric

✅ Unified analytics platform for the entire organization  
✅ Consolidating multiple analytics tools into one  
✅ Power BI-centric organizations wanting deeper analytics  
✅ Need for real-time and batch analytics in one platform  
✅ Want managed SaaS with minimal infrastructure overhead  
✅ Replacing Azure Data Lake Analytics (retired)  

### When NOT to Use Microsoft Fabric

❌ Simple, single-purpose analytics needs  
❌ Organizations heavily invested in non-Microsoft ecosystems  
❌ Strict data residency requirements not met by Fabric regions  
❌ Need for fine-grained infrastructure control  

## Migration Paths to Microsoft Fabric

| From | Migration Approach |
|------|-------------------|
| **Azure Data Lake Analytics** | Migrate to Fabric Data Engineering or Data Warehouse |
| **Azure Synapse Analytics** | Gradual migration using Fabric's Synapse compatibility |
| **Power BI Premium** | Automatic upgrade path to Fabric capacity |
| **Azure Data Factory** | Pipeline migration to Fabric Data Factory |
| **Databricks** | Use shortcuts to connect existing Delta Lake |

## Comparison with Standalone Services

| Aspect | Microsoft Fabric | Individual Azure Services |
|--------|------------------|---------------------------|
| **Management** | Single unified platform | Multiple services to manage |
| **Billing** | Single capacity-based billing | Per-service billing |
| **Data Movement** | Minimal (OneLake) | Often requires data copying |
| **Learning Curve** | Learn one platform | Learn multiple tools |
| **Flexibility** | Opinionated architecture | Full customization |
| **Cost Optimization** | Shared capacity model | Independent scaling per service |

## References

- [Microsoft Fabric Overview](https://learn.microsoft.com/en-us/fabric/get-started/microsoft-fabric-overview)
- [OneLake Documentation](https://learn.microsoft.com/en-us/fabric/onelake/onelake-overview)
- [Fabric Pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/)
- [Fabric Capacity and SKUs](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)
