# Azure Networking Fundamentals - Common Networking Scenarios

## 9. Common Networking Scenarios

### 9.1 Securing Azure Storage with Private Endpoint

```
┌─────────────────────────────────────────────────────────────┐
│ VNet: 10.0.0.0/16                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Subnet: 10.0.1.0/24                                 │   │
│  │  ┌──────────┐        ┌─────────────────┐            │   │
│  │  │ App      │───────▶│ Private Endpoint │            │   │
│  │  │ Service  │        │ 10.0.1.5        │            │   │
│  │  └──────────┘        └────────┬────────┘            │   │
│  └───────────────────────────────┼─────────────────────┘   │
└──────────────────────────────────┼──────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Storage Account              │
                    │ Public access: Disabled      │
                    │ Private endpoint: Enabled    │
                    └──────────────────────────────┘
```

**Configuration Steps:**
1. Create a private endpoint for the storage account
2. Link to Private DNS Zone `privatelink.blob.core.windows.net`
3. Disable public network access on storage account
4. Application connects using standard storage connection string

### 9.2 Securing Azure SQL Database

```csharp
// Connection string remains the same
// DNS resolves to private IP automatically
var connectionString = "Server=myserver.database.windows.net;Database=mydb;...";
```

**DNS Resolution:**
- `myserver.database.windows.net` → CNAME → `myserver.privatelink.database.windows.net` → `10.0.1.6`

### 9.3 Securing Azure Key Vault

Private endpoints for Key Vault are commonly used to:
- Allow VMs to retrieve secrets without public internet
- Enable App Services (VNet-integrated) to access secrets
- Support on-premises applications via VPN

**Key Vault Network Settings:**
| Setting | Value |
|---------|-------|
| Public network access | Disabled |
| Private endpoint connections | Enabled |
| Firewall | Allow trusted Microsoft services |

### 9.4 Securing Azure Cosmos DB

Cosmos DB supports private endpoints for each API type:

| API | Private DNS Zone |
|-----|------------------|
| SQL (Core) | `privatelink.documents.azure.com` |
| MongoDB | `privatelink.mongo.cosmos.azure.com` |
| Cassandra | `privatelink.cassandra.cosmos.azure.com` |
| Gremlin | `privatelink.gremlin.cosmos.azure.com` |
| Table | `privatelink.table.cosmos.azure.com` |

### 9.5 App Service to Azure SQL Database Private Connectivity

When connecting an Azure App Service web app to an Azure SQL Database via private connection, you need to configure a Virtual Network with **at least 2 subnets**:

1. **VNet Integration Subnet** - For App Service outbound connectivity
2. **Private Endpoint Subnet** - For Azure SQL Database private endpoint

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              APP SERVICE TO SQL DATABASE PRIVATE CONNECTIVITY               │
│                                                                              │
│  Virtual Network: 10.0.0.0/16 (East US)                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  Subnet 1: VNet Integration (10.0.1.0/24)                            │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                                                              │    │   │
│  │  │  ┌─────────────────┐     VNet Integration                   │    │   │
│  │  │  │   Webapp1       │─────────────────────────────┐          │    │   │
│  │  │  │  (App Service)  │                             │          │    │   │
│  │  │  └─────────────────┘                             │          │    │   │
│  │  │                                                  │          │    │   │
│  │  └──────────────────────────────────────────────────┼──────────┘    │   │
│  │                                                     │                │   │
│  │  Subnet 2: Private Endpoints (10.0.2.0/24)         │                │   │
│  │  ┌──────────────────────────────────────────────────┼──────────┐    │   │
│  │  │                                                  │          │    │   │
│  │  │  ┌─────────────────┐                             │          │    │   │
│  │  │  │ Private Endpoint │◀────────────────────────────┘          │    │   │
│  │  │  │   10.0.2.5      │                                        │    │   │
│  │  │  └────────┬────────┘                                        │    │   │
│  │  │           │                                                  │    │   │
│  │  └───────────┼──────────────────────────────────────────────────┘    │   │
│  │              │ Private Link                                          │   │
│  └──────────────┼───────────────────────────────────────────────────────┘   │
│                 │                                                            │
│                 ▼                                                            │
│  ┌───────────────────────────────────────┐                                  │
│  │          Azure SQL Database           │                                  │
│  │              DB1                       │                                  │
│  │  Public endpoint: DISABLED            │                                  │
│  │  Private endpoint: 10.0.2.5           │                                  │
│  └───────────────────────────────────────┘                                  │
│                                                                              │
│  Result: All traffic between Webapp1 and DB1 stays on Azure backbone        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why 2 Subnets Are Required:**

| Subnet | Purpose | Key Requirement |
|--------|---------|-----------------|
| **VNet Integration Subnet** | Enables App Service to make outbound calls into the VNet | Must be **delegated** to `Microsoft.Web/serverFarms`. Cannot contain other resources |
| **Private Endpoint Subnet** | Hosts the private endpoint NIC for SQL Database | Cannot be delegated to App Service. Private endpoints have specific subnet requirements |

> **Important**: Private endpoints cannot be deployed in a subnet that is delegated to App Service VNet Integration. This is why **two separate subnets** are required.

**Configuration Steps:**

1. **Create a Virtual Network** with address space (e.g., 10.0.0.0/16)
2. **Create Subnet 1** for VNet Integration (e.g., 10.0.1.0/24)
   - Delegate to `Microsoft.Web/serverFarms`
3. **Create Subnet 2** for Private Endpoints (e.g., 10.0.2.0/24)
   - Enable private endpoint network policies if needed
4. **Configure App Service VNet Integration** using Subnet 1
5. **Create Private Endpoint** for Azure SQL Database in Subnet 2
6. **Link Private DNS Zone** `privatelink.database.windows.net` to the VNet
7. **Disable public network access** on Azure SQL Database (optional but recommended)

**DNS Name Resolution for Private Connectivity:**

To ensure DNS names resolve to private IP addresses within the VNet, you must configure a **Private DNS Zone**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DNS RESOLUTION WITH PRIVATE DNS ZONE                      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Virtual Network                                                     │   │
│  │                                                                       │   │
│  │  ┌─────────────────┐                    ┌─────────────────────────┐  │   │
│  │  │    Webapp1      │──── DNS Query ────▶│   Private DNS Zone      │  │   │
│  │  │                 │     for DB1.       │   privatelink.database. │  │   │
│  │  │                 │     database.      │   windows.net           │  │   │
│  │  │                 │     windows.net    │                         │  │   │
│  │  │                 │                    │   A Record:             │  │   │
│  │  │                 │◀── Returns ────────│   DB1 → 10.0.2.5       │  │   │
│  │  │                 │    10.0.2.5        │   (Private IP)          │  │   │
│  │  └─────────────────┘                    └─────────────────────────┘  │   │
│  │          │                                        │                   │   │
│  │          │ Connects to                            │ Linked to VNet   │   │
│  │          │ 10.0.2.5                               │                   │   │
│  │          ▼                                        │                   │   │
│  │  ┌─────────────────┐                              │                   │   │
│  │  │ Private Endpoint │◀─────────────────────────────┘                   │   │
│  │  │   10.0.2.5      │                                                  │   │
│  │  └────────┬────────┘                                                  │   │
│  └───────────┼───────────────────────────────────────────────────────────┘   │
│              │ Private Link                                                  │
│              ▼                                                               │
│  ┌───────────────────────────────────────┐                                  │
│  │          Azure SQL Database (DB1)     │                                  │
│  └───────────────────────────────────────┘                                  │
│                                                                              │
│  Result: DNS resolution stays within VNet, traffic remains private          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**DNS Resolution Options Comparison:**

| Option | Use for Private Connectivity? | Explanation |
|--------|-------------------------------|-------------|
| **Private DNS Zone** | ✅ **Correct** | Resolves DNS names to private IPs within the VNet. Traffic stays private and secure |
| **Public DNS Zone** | ❌ **Incorrect** | Resolves to public IP addresses, exposing traffic to the public internet |
| **Azure DNS Private Resolver** | ❌ **Not Required** | Used for querying private DNS zones from on-premises networks. Not needed for intra-VNet resolution |

**Why Private DNS Zone?**
- Automatically resolves service FQDNs to private endpoint IPs
- DNS resolution happens entirely within the Virtual Network
- No traffic traverses the public internet
- Seamless integration with Azure PaaS private endpoints

**Why NOT Public DNS Zone?**
- Public DNS zones resolve to public IP addresses
- Traffic would be routed over the public internet
- Defeats the purpose of private connectivity
- Violates security requirements for private communication

**Why NOT Azure DNS Private Resolver?**
- Private Resolver is designed for **hybrid scenarios** (on-premises ↔ Azure)
- Allows on-premises networks to query Azure private DNS zones
- Not required when both resources (App Service and SQL) are within the same VNet
- Adds unnecessary complexity for pure Azure-to-Azure private connectivity

**Exam Scenarios:**

| Question | Answer |
|----------|--------|
| "Create a virtual network that contains at least ___" for private connectivity between App Service and SQL Database | **2 subnets** |
| "From the virtual network, configure name resolution to use ___" | **A private DNS zone** |

**Why Not 1 Subnet?**
- App Service VNet Integration requires a **delegated subnet**
- Private endpoints **cannot be placed** in delegated subnets
- These are Azure platform limitations that enforce network isolation

**Why Not 3 Subnets?**
- Two subnets are the **minimum requirement**
- A third subnet might be used for other resources (VMs, other services) but is not required for basic App Service to SQL connectivity

**References:**
- [Private endpoint limitations](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview#limitations)
- [Virtual network service endpoints](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-service-endpoints-overview)
- [App Service VNet Integration](https://learn.microsoft.com/en-us/azure/app-service/overview-vnet-integration)
- [Azure Private DNS overview](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Azure DNS Private Resolver overview](https://learn.microsoft.com/en-us/azure/dns/dns-private-resolver-overview)

---

