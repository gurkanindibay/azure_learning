# On-Premises Data Gateway

The On-premises Data Gateway is a bridge that provides secure data transfer between on-premises data sources and several Microsoft cloud services. It enables cloud services to access on-premises data without requiring a VPN or exposing on-premises servers to the public internet.

## Supported Cloud Services

| Service | Use Case |
|---------|----------|
| **Azure Logic Apps** | Workflow automation with on-premises data |
| **Power BI** | Reports and dashboards from on-premises data |
| **Power Apps** | Custom apps connecting to on-premises data |
| **Power Automate** | Automated flows with on-premises systems |
| **Azure Analysis Services** | Data modeling from on-premises sources |
| **Power Virtual Agents** | Chatbots accessing on-premises data |

---

## Architecture Overview

The On-premises Data Gateway solution consists of **two components**:

1. **On-Premises Component**: The gateway software installed on a Windows Server in your datacenter
2. **Azure Component**: A **Connection Gateway Resource** created in Azure that represents the cloud-side configuration

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AZURE CLOUD                                     │
│                                                                              │
│  ┌─────────────────┐    ┌──────────────────────────┐    ┌────────────────┐  │
│  │  Cloud Service  │───►│  Connection Gateway      │───►│  Azure Relay   │  │
│  │  (Logic Apps,   │    │  Resource                │    │  (Service Bus) │  │
│  │   Power BI,     │    │  • Cloud-side config     │    │                │  │
│  │   Power Apps)   │    │  • Links to on-prem GW   │    │                │  │
│  └─────────────────┘    └──────────────────────────┘    └───────┬────────┘  │
│                                                                  │          │
└──────────────────────────────────────────────────────────────────│──────────┘
                                                                   │
                                                    Outbound HTTPS (443)
                                                    (No inbound ports required)
                                                                   │
┌──────────────────────────────────────────────────────────────────│──────────┐
│                         ON-PREMISES DATACENTER                   │          │
│                                                                  │          │
│  ┌───────────────────────────────────────────────────────────────▼───────┐  │
│  │                    On-Premises Data Gateway                           │  │
│  │  • Installed on Windows Server (with internet access)                 │  │
│  │  • Initiates outbound connection to Azure Relay                       │  │
│  │  • Acts as bridge between Azure and on-prem resources                 │  │
│  │  • Registered with Azure account during setup                         │  │
│  └───────────────────────────────────────────────────────────┬───────────┘  │
│                                                              │              │
│                              ┌────────────────────────────────▼───────────┐ │
│                              │        Data Sources                        │ │
│                              │        • SQL Server                        │ │
│                              │        • Oracle Database                   │ │
│                              │        • File System                       │ │
│                              │        • SharePoint Server                 │ │
│                              └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Two-Part Architecture

| Component | Location | Purpose |
|-----------|----------|----------|
| **On-Premises Data Gateway** | On-premises Windows Server | Software that connects to data sources and communicates with Azure |
| **Connection Gateway Resource** | Azure Portal | Cloud-side configuration that cloud services reference to use the gateway |

---

## Key Characteristics

| Feature | Description |
|---------|-------------|
| **Communication** | Uses Azure Relay for secure, encrypted communication |
| **Outbound Only** | Only requires outbound connectivity on port 443 (HTTPS) |
| **No VPN Required** | Works without VPN or ExpressRoute connections |
| **No Public Exposure** | On-premises servers don't need internet access or public endpoints |
| **Encryption** | All data is encrypted in transit |
| **Multi-Service** | Single gateway can serve multiple Azure/Microsoft services |

---

## Supported Data Sources

- **SQL Server** (all versions)
- **Oracle Database**
- **IBM DB2**
- **IBM Informix**
- **File System**
- **SAP**
- **SharePoint Server (on-premises)**
- **Teradata**
- **MySQL**
- **PostgreSQL**

---

## On-Premises Data Gateway Installation

### Prerequisites

1. **Windows Server**: Windows Server 2016 or later (Windows 10/11 for development)
2. **.NET Framework**: .NET Framework 4.7.2 or later
3. **Network**: Outbound HTTPS connectivity to Azure (port 443)
4. **Memory**: Minimum 8 GB RAM recommended
5. **CPU**: 64-bit processor
6. **Storage**: SSD recommended for better performance

### Installation Steps

1. Download the On-premises data gateway installer from Azure portal or Power Platform admin center
2. Run the installer on a server in the same network as your data sources
3. Sign in with your Azure or Microsoft 365 account
4. Register the gateway with a unique name
5. Select the Azure region (important: must match Connection Gateway Resource region)

### Best Practices for Installation

- Install on a dedicated server (not on the data source server itself)
- Ensure the gateway server has reliable uptime
- Place the gateway close to data sources to minimize latency
- Use a service account for running the gateway service

---

## Connection Gateway Resource (Azure Component)

The **Connection Gateway Resource** is the Azure-side representation of your on-premises data gateway. It must be created in Azure to allow cloud services to connect to your on-premises gateway installation.

### What It Does

- **Links Azure services to on-premises gateway**: Acts as the cloud endpoint that services reference
- **Enables secure data transfer**: Works with Azure Relay to facilitate encrypted communication
- **Manages gateway configuration**: Stores connection settings and authentication details

### Creating a Connection Gateway Resource

1. Navigate to **Azure Portal** → **Create a resource**
2. Search for **"On-premises data gateway"**
3. Configure the resource:
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Choose or create a resource group
   - **Name**: Provide a name for the gateway resource
   - **Region**: Must match the region selected during on-premises gateway installation
   - **Installation Name**: Select the registered on-premises gateway

### Key Points

| Aspect | Details |
|--------|----------|
| **Prerequisite** | On-premises gateway must be installed and registered first |
| **Region Matching** | Azure resource region must match the gateway installation region |
| **One-to-One Mapping** | Each on-premises gateway maps to one Azure gateway resource |
| **Required for Azure Services** | Azure services cannot use on-premises connectors without this resource |

---

## High Availability

### Gateway Cluster

For production workloads, you can create a gateway cluster with multiple gateway installations:

- **Load Balancing**: Requests are distributed across gateway members
- **Failover**: If one gateway is unavailable, requests route to other members
- **Scalability**: Add more gateways to handle increased load

### Cluster Configuration

1. Install additional gateways on separate servers
2. During installation, choose "Add to an existing gateway cluster"
3. Select the primary gateway to join

---

## Comparison: On-Premises Connectivity Options

| Solution | Supported Services | Use Case | Limitations |
|----------|-------------------|----------|-------------|
| **On-Premises Data Gateway** | Logic Apps, Power BI, Power Apps, Power Automate, Azure Analysis Services | Backend data connectivity to databases and file systems | Requires gateway installation on-premises |
| **Hybrid Connection Manager** | Azure App Service, Azure Functions | Web apps and functions connecting to on-prem TCP resources | **NOT supported for Logic Apps or Power Platform** |
| **Azure AD Application Proxy** | Web applications | Publishing internal web apps to external users with SSO | For web app access, not database connectivity |
| **Web Application Proxy** | ADFS, Web applications | Publishing web apps, ADFS federation | For web app publishing, not Azure service integration |
| **VPN Gateway** | All Azure services | Site-to-site or point-to-site VPN | Requires VPN infrastructure setup |
| **ExpressRoute** | All Azure services | Dedicated private connection | Higher cost, requires provider setup |

---

## Exam Scenarios

### Scenario 1: What to Deploy On-Premises

**Given:**
- Azure subscription linked to a hybrid Microsoft Entra tenant
- On-premises datacenter with NO VPN connection to Azure
- Server1 running Microsoft SQL Server 2016 (prevented from accessing the internet)
- An Azure service (Logic App, Power BI, etc.) requires access to a database on Server1

**Question:** What should you deploy **on-premises**?

**Answer: On-Premises Data Gateway**

**Why this is correct:**
- Enables secure, encrypted communication between Azure services and on-premises data sources
- Does NOT require VPN or exposing Server1 to the public internet
- The gateway initiates outbound connections to Azure Relay
- Works even when Server1 has no direct internet access (gateway server needs outbound access only)

**Why other options are incorrect:**

| Option | Reason for Incorrectness |
|--------|-------------------------|
| **Web Application Proxy** | Used for publishing on-premises web applications to the internet, not for Azure service-to-database connectivity |
| **Microsoft Entra Application Proxy Connector** | Used for publishing internal web apps with authentication/SSO, not for backend data connectivity |
| **Hybrid Connection Manager** | Used with Azure Relay for App Services and Functions only, **NOT supported for Logic Apps or Power Platform** |

---

### Scenario 2: What to Deploy in Azure

**Given:** (Same scenario as above)
- Azure subscription linked to a hybrid Microsoft Entra tenant
- On-premises datacenter with NO VPN connection to Azure
- Server1 running Microsoft SQL Server 2016 (prevented from accessing the internet)
- An Azure service requires access to a database on Server1

**Question:** What should you deploy **in Azure**?

**Answer: A Connection Gateway Resource**

**Why this is correct:**
- Represents the cloud-side configuration of the On-premises Data Gateway
- Required to allow Azure services to connect to on-premises data sources
- Works together with the on-premises gateway installation to enable secure data transfer

**Why other options are incorrect:**

| Option | Reason for Incorrectness |
|--------|-------------------------|
| **Azure Application Gateway** | Layer 7 load balancer for web applications; cannot enable Azure services to access on-premises databases |
| **Azure Event Grid domain** | Used for event-based messaging and notifications, not for direct connectivity to on-premises databases |
| **Enterprise application** | Used to integrate SaaS applications or configure SSO in Microsoft Entra ID; does not facilitate data connectivity to on-premises systems |

---

## Complete Solution Summary

To enable Azure cloud services to access on-premises data:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE SOLUTION                                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   AZURE (Deploy these)                ON-PREMISES (Deploy these)           │
│   ─────────────────────               ──────────────────────────           │
│   1. Cloud Service                    1. On-Premises Data Gateway          │
│      (Logic App, Power BI, etc.)         (on a server with internet        │
│                                           access that can reach data)      │
│   2. Connection Gateway Resource                                            │
│      (links to on-prem gateway)       2. Data Sources                       │
│                                          (SQL Server, Oracle, etc.)         │
│                                          (no internet access needed)        │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Monitoring and Management

### Azure Portal

- View gateway status and health
- Monitor connection metrics
- Manage gateway members in a cluster

### Power Platform Admin Center

- Centralized gateway management for Power Platform services
- View all gateways in your tenant
- Manage permissions and sharing

### Logs

- Gateway logs stored locally on the gateway server
- Enable additional logging for troubleshooting
- Use Azure Monitor for cloud-side monitoring

---

## Best Practices

1. **High Availability**: Install gateway on multiple servers and create a gateway cluster
2. **Network Placement**: Install gateway close to data sources to minimize latency
3. **Monitoring**: Use Azure Monitor and gateway logs to track health and performance
4. **Security**: Use Windows authentication where possible; keep gateway software updated
5. **Sizing**: Ensure adequate resources (8 GB+ RAM, SSD storage) for production workloads
6. **Updates**: Keep the gateway software updated to the latest version
7. **Dedicated Server**: Don't install on domain controllers or data source servers

---

## References

- [What is an On-premises data gateway?](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-onprem)
- [Install On-premises data gateway](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-install)
- [On-premises data gateway architecture](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-onprem-indepth)
- [High availability clusters and load balancing](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-high-availability-clusters)
- [Manage on-premises data gateway](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-manage)
