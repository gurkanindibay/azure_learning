# Azure Logic Apps Overview

Azure Logic Apps is a cloud-based platform for creating and running automated workflows that integrate apps, data, services, and systems. It enables enterprise integration solutions with minimal code.

## Key Features

- **Visual Designer**: Build workflows using a visual designer in the Azure portal
- **Pre-built Connectors**: 400+ connectors for Microsoft and third-party services
- **Enterprise Integration**: B2B scenarios with EDI, XML, and flat-file processing
- **Hybrid Connectivity**: Connect to on-premises systems securely

## Workflow Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Consumption** | Multi-tenant, pay-per-execution | Simple integrations, cost-effective for low volume |
| **Standard** | Single-tenant, dedicated resources | Enterprise workloads, better performance isolation |

---

## On-Premises Connectivity for Logic Apps

When Azure Logic Apps needs to access on-premises resources (databases, file systems, applications), the recommended solution is the **On-Premises Data Gateway**.

> **📘 For detailed information about the On-Premises Data Gateway and Connection Gateway Resource, see: [On-Premises Data Gateway](on-premises-data-gateway.md)**

### Why On-Premises Data Gateway for Logic Apps?

The On-premises Data Gateway is the **only supported method** for Logic Apps to connect to on-premises data sources. Key points:

- Uses Azure Relay for secure, encrypted communication
- Only requires outbound HTTPS (443) - no inbound ports
- Works without VPN or ExpressRoute
- On-premises data sources don't need internet access

### Important: Hybrid Connections NOT Supported

**Hybrid Connection Manager** (used by Azure App Service and Azure Functions) is **NOT supported for Logic Apps**. Always use the On-Premises Data Gateway for Logic Apps hybrid connectivity.

---

## Exam Scenarios: Logic Apps to On-Premises SQL Server

The On-premises Data Gateway solution requires components in **both** locations:
- **On-premises**: The gateway software installation
- **Azure**: The connection gateway resource

---

### Scenario 1: What to Deploy On-Premises

**Given:**
- Azure subscription linked to a hybrid Microsoft Entra tenant
- On-premises datacenter with NO VPN connection to Azure
- Server1 running Microsoft SQL Server 2016 (prevented from accessing the internet)
- LogicApp1 requires write access to a database on Server1

**Question:** What should you deploy **on-premises** to enable LogicApp1 to access Server1?

**Answer: On-Premises Data Gateway**

**Why this is correct:**
- Enables secure, encrypted communication between Logic Apps and on-premises SQL Server
- Does NOT require VPN or exposing Server1 to the public internet
- The gateway initiates outbound connections to Azure Relay
- Works even when Server1 has no direct internet access (gateway server needs outbound access only)

**Why other options are incorrect:**

| Option | Reason for Incorrectness |
|--------|-------------------------|
| **Web Application Proxy** | Used for publishing on-premises web applications to the internet, not for Azure service-to-database connectivity |
| **Microsoft Entra Application Proxy Connector** | Used for publishing internal web apps with authentication/SSO, not for backend data connectivity |
| **Hybrid Connection Manager** | Used with Azure Relay for App Services and Functions, **NOT supported for Logic Apps** |

---

### Scenario 2: What to Deploy in Azure

**Given:** (Same scenario as above)
- Azure subscription linked to a hybrid Microsoft Entra tenant
- On-premises datacenter with NO VPN connection to Azure
- Server1 running Microsoft SQL Server 2016 (prevented from accessing the internet)
- LogicApp1 requires write access to a database on Server1

**Question:** What should you deploy **in Azure** to enable LogicApp1 to access Server1?

**Answer: A Connection Gateway Resource**

**Why this is correct:**
- Represents the cloud-side configuration of the On-premises Data Gateway
- Required to allow Azure Logic Apps to connect to on-premises data sources
- Works together with the on-premises gateway installation to enable secure data transfer
- The connection gateway resource in Azure, along with the on-premises gateway installed on another machine that can reach Server1, enables LogicApp1 to send data securely to SQL Server without requiring VPN or direct internet access from Server1

**Why other options are incorrect:**

| Option | Reason for Incorrectness |
|--------|-------------------------|
| **Azure Application Gateway** | Layer 7 load balancer for web applications; cannot enable Logic Apps to access on-premises SQL Server |
| **Azure Event Grid domain** | Used for event-based messaging and notifications, not for direct connectivity to on-premises databases |
| **Enterprise application** | Used to integrate SaaS applications or configure SSO in Microsoft Entra ID; does not facilitate data connectivity to on-premises systems |

---

### Complete Solution Summary

To enable LogicApp1 to write to SQL Server on Server1:

| Location | Component | Purpose |
|----------|-----------|---------|
| **Azure** | Logic App (LogicApp1) | The workflow that needs database access |
| **Azure** | Connection Gateway Resource | Cloud-side configuration linking to on-prem gateway |
| **On-Premises** | On-Premises Data Gateway | Bridge between Azure and on-prem (needs internet access) |
| **On-Premises** | SQL Server 2016 (Server1) | Data source (no internet access needed) |

---

## Connectors for On-Premises Data

Logic Apps provides specific connectors that work with the On-premises data gateway:

### SQL Server Connector (On-Premises)

\`\`\`json
{
  "type": "ApiConnection",
  "inputs": {
    "host": {
      "connection": {
        "name": "@parameters('\$connections')['sql']['connectionId']"
      }
    },
    "method": "post",
    "path": "/datasets/default/tables/@{encodeURIComponent('dbo.Orders')}/items"
  }
}
\`\`\`

### Connection Configuration

When creating a SQL Server connection in Logic Apps for on-premises:

1. **Authentication Type**: Windows or SQL Server authentication
2. **Gateway**: Select your registered On-premises data gateway
3. **Server Name**: On-premises SQL Server hostname
4. **Database Name**: Target database name

---

## References

- [Connect to on-premises data sources from Logic Apps](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-gateway-connection)
- [Azure Logic Apps Overview](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)
- [On-Premises Data Gateway](on-premises-data-gateway.md) - Detailed gateway documentation
