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

## When to Choose Logic Apps Over Functions and WebJobs

### Scenario: Minimal Development Effort for Integration

When the primary requirement is to **minimize development effort** for integration scenarios, Azure Logic Apps is typically the best choice due to its low-code/no-code approach and extensive pre-built connectors.

---

### Practice Question: Sending Teams Messages from On-Premises App Events

**Given:**
- You have an on-premises app named App1 that supports REST calls and webhooks
- You have an Azure subscription
- You plan to develop a new app named App2 that will send a Microsoft Teams message when a new record is added to App1
- You need to recommend a service to host App2
- **The solution must minimize development effort**

**Question:** What should you recommend?

**Options:**
- A) Azure Functions
- B) Azure Logic Apps
- C) Azure WebJobs

---

### Answer: B ✅

**Correct Answer: B) Azure Logic Apps**

---

### Detailed Explanation

**Option B - Azure Logic Apps** ✅
- **Correct**: Logic Apps provides a low-code/no-code solution to integrate with services using webhooks and REST APIs
- Has **built-in connectors** for HTTP/Webhook triggers and Microsoft Teams actions
- Allows you to automate workflows such as posting a message when a new record is added — all with **minimal development effort**
- Perfect for the requirement: App1 sends a webhook → Logic Apps receives it → Logic Apps sends Teams message
- No custom code required for this integration scenario

**Option A - Azure Functions**
- **Incorrect**: While Azure Functions supports custom code execution in response to events like HTTP requests or webhooks, it requires:
  - More coding and setup
  - Custom authentication implementation
  - Integration with Microsoft Teams APIs (Graph API)
- It's a great choice for custom logic but **not the easiest path** when out-of-the-box connectors are available in Logic Apps

**Option C - Azure WebJobs**
- **Incorrect**: WebJobs are designed to run background processes in App Service environments and:
  - Do NOT provide native support for webhook triggers
  - Do NOT provide native Teams integration
  - Require hosting within an App Service plan
  - Require more development and management overhead

### Comparison Summary: Development Effort

| Service | Webhook Support | Teams Integration | Development Effort | Best For |
|---------|----------------|-------------------|-------------------|----------|
| **Logic Apps** | ✅ Built-in HTTP/Webhook trigger | ✅ Built-in Teams connector | **Minimal** (low-code) | Integration scenarios with connectors |
| **Azure Functions** | ✅ HTTP trigger | ❌ Requires custom code (Graph API) | **Medium** (custom code) | Custom logic and complex processing |
| **WebJobs** | ❌ No native support | ❌ No native support | **High** (custom code + infrastructure) | Background processing within App Service |

### Key Takeaway

> **📘 When minimizing development effort is the primary requirement** for integration scenarios involving webhooks, REST APIs, and connecting to services like Microsoft Teams, **Azure Logic Apps** should be the first choice due to its extensive connector library and visual designer.

---

### Practice Question: Choosing the Right Trigger Type

**Given:** (Same scenario as above)
- You have an on-premises app named App1 that supports REST calls and webhooks
- You have an Azure subscription
- App2 will send a Microsoft Teams message when a new record is added to App1
- You need to recommend the type of **trigger** to use to call App2
- **The solution must minimize development effort**

**Question:** What should you recommend?

**Options:**
- A) Azure Event Grid
- B) Azure Service Bus
- C) HTTP

---

### Answer: C ✅

**Correct Answer: C) HTTP**

---

### Detailed Explanation

**Option C - HTTP** ✅
- **Correct**: App1 **already supports REST calls and webhooks**, which makes an HTTP trigger the simplest and most direct way to invoke App2
- When App1 adds a new record, it can issue a standard **HTTP POST request** (as a webhook) to trigger App2
- Can be implemented using Azure Logic Apps or Azure Functions with an HTTP trigger
- Requires **minimal development effort** and avoids the need for additional infrastructure or messaging layers
- No additional Azure services need to be provisioned

**Option A - Azure Event Grid**
- **Incorrect**: Event Grid is designed for event-driven architectures involving Azure services
- Requires publishers to be **registered within Event Grid**
- While powerful, it adds **unnecessary complexity** for a simple webhook-style interaction between two custom apps
- Overkill for this scenario where a direct HTTP call suffices

**Option B - Azure Service Bus**
- **Incorrect**: Service Bus is used for reliable messaging between distributed systems
- Supports queues and topics with features like retries, ordering, and dead-lettering
- Better suited for **complex message workflows** with guaranteed delivery requirements
- Introduces **more development and operational overhead** than a straightforward HTTP webhook integration
- Requires provisioning and managing additional Azure resources

### Trigger Type Comparison: Development Effort

| Trigger Type | Setup Complexity | Additional Infrastructure | Development Effort | Best For |
|--------------|------------------|--------------------------|-------------------|----------|
| **HTTP** | ✅ Simple endpoint URL | ❌ None required | **Minimal** | Direct webhook/REST integrations |
| **Event Grid** | ⚠️ Publisher registration required | ✅ Event Grid topic/subscription | **Medium** | Azure-native event-driven architectures |
| **Service Bus** | ⚠️ Queue/Topic setup required | ✅ Service Bus namespace | **Higher** | Reliable messaging with retries/ordering |

### Key Takeaway

> **📘 When an application already supports webhooks** and the requirement is to minimize development effort, use an **HTTP trigger**. It provides the most direct integration path without introducing additional messaging infrastructure like Event Grid or Service Bus.

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

## High Throughput Mode and Scaling Logic Apps

When a Logic App needs to handle a high volume of requests during peak loads, you need to configure **Workflow settings** to enable **High Throughput Mode**.

### Throughput Limits for Consumption Logic Apps

| Setting | Default Limit | High Throughput Mode |
|---------|---------------|----------------------|
| Actions per 5-minute rolling interval | **100,000** executions | **300,000** executions |

### How to Enable High Throughput Mode

1. In the **Azure portal**, navigate to your Logic App
2. Under **Settings**, select **Workflow settings**
3. Under **Runtime options** → **High throughput**, set to **On**

### Enable via ARM Template

To enable high throughput in an ARM template, add the `runtimeConfiguration` object with `operationOptions` set to `OptimizedForHighThroughput`:

```json
{
  "properties": {
    "runtimeConfiguration": {
      "operationOptions": "OptimizedForHighThroughput"
    }
  }
}
```

---

### Practice Question: Handling High Volume Requests

**Given:**
- A company has developed a Logic App named 'getcloudskills-logicapp'
- The app is designed to respond to HTTP POST or HTTP GET requests
- It should be able to handle up to **200,000 requests in a 5-minute period** during peak loads

**Question:** To ensure the application can handle the expected number of requests, which of the following should be configured?

**Options:**
- A) Workflow settings
- B) API connections
- C) Access control (IAM)
- D) Access keys

---

### Answer: A ✅

**Correct Answer: A) Workflow settings**

---

### Detailed Explanation

**Option A - Workflow settings** ✅
- **Correct**: Multitenant Azure Logic Apps has a default limit on the number of actions that run every 5 minutes (100,000)
- To raise the default value to the maximum (300,000), you can enable **high throughput mode** in Workflow settings
- This setting is found under **Settings** → **Workflow settings** → **Runtime options** → **High throughput**
- Alternatively, you can distribute the workload across multiple logic apps and workflows

**Option B - API connections**
- **Incorrect**: API connections in a Logic App are used to connect to external services or systems
- While important for integrating with external resources, API connections do not directly impact the Logic App's ability to handle a high volume of requests during peak loads

**Option C - Access control (IAM)**
- **Incorrect**: Access control (IAM) in Azure is used to manage user access to Azure resources
- While access control is important for securing the Logic App, it does not directly impact the app's ability to handle a high volume of requests during peak loads

**Option D - Access keys**
- **Incorrect**: Access keys in Azure are used for authentication and authorization purposes
- While access keys are important for securing access to the Logic App, they do not directly impact the app's ability to handle a high volume of requests during peak loads

### Logic Apps Configuration Options Comparison

| Configuration | Purpose | Affects Throughput? |
|---------------|---------|---------------------|
| **Workflow settings** | Runtime options including high throughput mode | ✅ Yes |
| **API connections** | Connect to external services/systems | ❌ No |
| **Access control (IAM)** | Manage user/role permissions (RBAC) | ❌ No |
| **Access keys** | Authentication/authorization tokens | ❌ No |

---

### Additional Strategies for High Load Scenarios

If 300,000 actions per 5 minutes still isn't enough, consider these strategies:

1. **Distribute workload across multiple Logic Apps** - Split your workflow into parent/child workflows
2. **Limit trigger concurrency** - Control how many workflow instances run simultaneously
3. **Disable array debatching (Split On)** - Process arrays in bulk instead of per-item
4. **Use Standard Logic Apps** - Standard tier has **no limit** on actions per interval

### Standard Logic Apps Scaling

For extremely high-throughput scenarios, Standard Logic Apps offer:

- **No action execution limits** per interval
- Support for **multiple storage accounts** (up to 32)
- Target ~100,000 action executions per minute per storage account
- Dynamic scaling based on trigger load and job execution delays
- Prewarmed instances for faster ramp-up during peak loads

### Key Takeaway

> **📘 When you need to handle high volumes of requests in a Consumption Logic App**, enable **High Throughput Mode** in **Workflow settings** to increase the action execution limit from 100,000 to 300,000 per 5-minute interval. For even higher demands, consider using Standard Logic Apps or distributing workload across multiple logic apps.

---

## References

- [Connect to on-premises data sources from Logic Apps](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-gateway-connection)
- [Azure Logic Apps Overview](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)
- [Azure Connectors Introduction](https://learn.microsoft.com/en-us/azure/connectors/introduction)
- [Azure Functions Overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Azure Functions HTTP Webhook Trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)
- [Azure Event Grid Overview](https://learn.microsoft.com/en-us/azure/event-grid/overview)
- [Azure Service Bus Messaging Overview](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview)
- [Run background tasks with WebJobs in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/webjobs-create)
- [On-Premises Data Gateway](on-premises-data-gateway.md) - Detailed gateway documentation
