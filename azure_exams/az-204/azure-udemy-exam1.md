### Question
Which Azure monitoring service allows you to set alerts to be notified when service incidents and planned maintenance is happening within Azure in regions that may affect you?

**Answer:** Azure Service Health

---

### Question
If you are concerned that your Logic Apps are running in a multi-tenant environment, and want your Logic App to have its own hardware and network, which Azure Service would you need to add?

**Answer:** [Integration Service Environment (ISE)](https://learn.microsoft.com/en-us/azure/integration-environments/overview)

---

### Question
What is the Azure Powershell (Az Module) command for creating a new Web App?

**Answer:** `New-AzWebApp`

---

### Question
What optional service can you enable, for a fee, to protect Azure SQL Database from unusual client behavior and potentially harmful attempts to access or exploit databases?

**Answer:** [Advanced Threat Protection](https://learn.microsoft.com/en-us/azure/security/fundamentals/threat-detection)

---

### Question
What is the maximum file size of a block blob?

**Answer:** 190.7 TB
[Reference](https://docs.microsoft.com/en-us/rest/api/storageservices/Understanding-Block-Blobs--Append-Blobs--and-Page-Blobs?redirectedfrom=MSDN#about-block-blobs)

---

### Question
5 PB is quite a large amount of storage, and very few uses are going to fill that up. Assuming that you will not fill it up, what would be the most likely reason you need to create more than one storage account?

**Answer:** Exceeding the maximum of 20,000 IO operations per second.

---

### Question
You are the developer for Acme Inc. You use Virtual Machines in Azure to provide your web sites to the public. The problem with scaling a virtual machine is that it starts with the basic Windows Server 2016 image, and you will need to find a way to deploy your code to the machine before it's useful. What is the recommended way to deploy your website code to a brand new VM that would be used in automatic scaling?

**Answer:** The custom script VM extension to execute a PowerShell script to do your deployment and configuration.

---

### Question
What is the maximum number of apps you can install in a single App Service free account?

**Answer:** 10
[Reference](https://docs.azure.cn/en-us/azure-resource-manager/management/azure-subscription-service-limits?utm_source=chatgpt.com)

---

### Question
What DNS record is required to link a custom domain name to an Azure App Service so that users can access the app service using the custom domain name? Choose two. Each answer is a complete solution.

**Answer:** CNAME Record, A Record

**Explanation:**
To link a **custom domain name** to an **Azure App Service**, Azure supports **two DNS record types**:

✅ **CNAME record**
- Used for **subdomains** (e.g., `www.example.com`).
- Maps your custom hostname to the Azure App Service’s default hostname (`yourapp.azurewebsites.net`).

✅ **A record**
- Used for **root/apex domains** (e.g., `example.com`).
- Points directly to the App Service’s **IP address** (provided in the Azure Portal).
- Requires adding a **TXT record** for domain verification, but the required *record to link* is the **A record**.

---

### Question
What is the maximum number of virtual machines that a virtual machine scale set can support?

**Answer:** 1000

---

### Question
Which of the following is NOT a way that you can deploy your code into Azure App Service?

**Answer:** Upload the code directly to the Azure Portal website.

---

### Question
What two methods can you use to restrict public Internet access to a Function App?

**Answer:** Removal of HTTP triggers, IP Access restriction.

---

### Question
What is the total maximum capacity of an unmanaged Azure Storage account in North America?

**Answer:** 5 PB

---

### Question
True or false: you can create an Azure Function to run whenever a new email comes into Outlook using it's own native Trigger integration with email.

**Answer:** False

**Explanation:**
Azure Functions does not have a native trigger for Outlook emails. You would typically use Logic Apps for this or use the Microsoft Graph API.

| Category | Triggers |
| --- | --- |
| Core | HTTP, Timer |
| Storage | Blob, Queue |
| Messaging | Service Bus (queue/topic), Event Hub, Kafka, RabbitMQ |
| Database | Cosmos DB change feed |
| Eventing | Event Grid |
| Workflows | Durable Functions triggers |

---

### Question
What optional security feature can you enable for Azure SQL Database or SQL Server that will ensure data remains encrypted while at rest, during movement between client and server, and while the data is in use?

**Answer:** Always Encrypted

---

### Question
You are a developer for Acme Inc. Your company's flagship application is the Wind Monitoring software that Wind Energy farms use to monitor their equipment. At the end of each day, the Wind Collector sends a message that contains all of the days statistics in JSON format which needs to be read, processed, and posted to the database. Which Azure Service is best for processing this type of data?

**Answer:** Service Bus

---

### Question
What is the main benefit of using Privileged Identity Management with Microsoft Entra ID?

**Answer:** Monitoring and protection of superuser accounts, providing a higher level of oversight to those more powerful accounts.
[Reference](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)

---

### Question
Which .NET Framework class contains the EventHubClient for working with Event Hub events?

**Answer:** `Microsoft.ServiceBus.Messaging`

---

### Question
You are a developer for Acme Inc. You have implemented Redis as a caching service and it's going great. You are running on a premium plan, and using the top 53 GB of memory cache. You'd like to increase the memory limit to 106 GB, but Redis does not support that. How can you get more memory when using Azure Redis? Choose the best answer.

**Answer:** Implement the Redis Cluster feature, and add a second shard to double the memory available.

**Explanation:**
Azure Cache for Redis **does not support auto-scaling the cache size**.

It can scale **up/down** to different SKUs, but:
- There is **no auto-scaling based on memory usage**
- You **cannot exceed the maximum memory** of the SKU by adding nodes automatically
- Memory capacity only increases by using **Redis Cluster** and **adding shards**

**How to Increase Memory Above 53 GB**
Azure Redis Premium caps at 53 GB per shard.
To get more:
1. **Enable Redis Cluster**
2. **Add more shards** (e.g., 2 shards → 106 GB total, 4 shards → 212 GB total)

Each shard is effectively a new Redis node that holds a portion of the keyspace.

**Summary**

| Option | Possible? | Result |
| --- | --- | --- |
| Upgrade SKU | ❌ max is 53 GB | Cannot exceed limit |
| Auto-scale Redis | ❌ not supported | Cannot add nodes automatically |
| **Use Redis Cluster** | ✔️ | Can add shards to increase total memory |

If you'd like, I can also explain how Redis clustering works in Azure or show a diagram.