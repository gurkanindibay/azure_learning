# Azure Architecture Documentation

This repository contains Azure-specific architecture documentation, service guides, and best practices.

## Structure

```
architecture-azure/
├── compute/                   # Compute services
│   ├── aks/                   # Azure Kubernetes Service
│   ├── app-service/           # Azure App Service
│   ├── container-apps/        # Azure Container Apps
│   ├── container-instances/   # Azure Container Instances
│   ├── functions/             # Azure Functions
│   ├── virtual-machines/      # Azure VMs
│   ├── service-fabric/        # Azure Service Fabric
│   ├── static-web-apps/       # Azure Static Web Apps
│   └── hpc/                   # High Performance Computing
├── data/                      # Data services
│   ├── databases/             # SQL, Cosmos DB, PostgreSQL
│   ├── storage/               # Azure Storage
│   ├── redis/                 # Azure Cache for Redis
│   ├── data-factory/          # Azure Data Factory
│   ├── data-explorer/         # Azure Data Explorer
│   └── bi-solutions/          # BI and analytics
├── networking/                # Networking services
│   ├── virtual-wan/           # Azure Virtual WAN
│   ├── firewall/              # Azure Firewall
│   └── load-balancing/        # Load balancing solutions
├── security/                  # Security services
│   ├── entra-id/              # Microsoft Entra ID
│   ├── key-vault/             # Azure Key Vault
│   ├── rbac/                  # Role-based access control
│   └── bastion/               # Azure Bastion
├── integration/               # Integration services
│   ├── logic-apps/            # Azure Logic Apps
│   ├── event-grid/            # Azure Event Grid
│   ├── event-hubs/            # Azure Event Hubs
│   ├── service-bus/           # Azure Service Bus
│   └── api-management/        # Azure API Management
├── container-registry/        # Azure Container Registry
├── observability/             # Monitoring services
│   ├── application-insights/  # Application Insights
│   └── azure-monitor/         # Azure Monitor
├── governance/                # Governance services
│   ├── policy/                # Azure Policy
│   ├── lighthouse/            # Azure Lighthouse
│   └── resource-management/   # Resource management
├── migration/                 # Migration services
├── cost-management/           # Cost optimization
└── devops/                    # DevOps and IaC
```

## Topics Covered

- **Compute**: VMs, AKS, Container Apps, Functions, App Service
- **Data**: SQL, Cosmos DB, Storage, Redis, Data Factory
- **Networking**: Virtual WAN, Firewall, Load Balancing, CDN
- **Security**: Entra ID, Key Vault, RBAC, Bastion
- **Integration**: Logic Apps, Event Grid, Event Hubs, Service Bus
- **Observability**: Application Insights, Azure Monitor
- **Governance**: Policy, Lighthouse, Resource Management
- **Migration**: Azure Migrate, Resource Mover
- **Cost Management**: Cost optimization and Hybrid Benefit

## Related Repositories

- [architecture-general](../architecture-general/) - Cloud-agnostic architecture documentation
