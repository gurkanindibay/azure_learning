# Azure Event Grid Pricing Tiers

## Table of Contents

- [Overview](#overview)
- [Resource Types and Pricing Models](#resource-types-and-pricing-models)
- [Event Grid Basic (Topics)](#event-grid-basic-topics)
- [Event Grid Namespaces (Standard/Premium)](#event-grid-namespaces-standardpremium)
- [Domains Pricing](#domains-pricing)
- [System Topics](#system-topics)
- [Partner Topics](#partner-topics)
- [Detailed Feature Comparison](#detailed-feature-comparison)
- [Performance Characteristics](#performance-characteristics)
- [Choosing the Right Option](#choosing-the-right-option)
- [Pricing Considerations](#pricing-considerations)
- [Migration Paths](#migration-paths)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Event Grid pricing is based on the **resource type** you use rather than traditional service tiers. The main options are:

1. **Event Grid Basic (Topics)** - Pay-per-operation model
2. **Event Grid Namespaces** - MQTT + HTTP with quota-based model (Standard/Premium)
3. **Domains** - Multi-tenant topics
4. **System Topics** - Azure resource events
5. **Partner Topics** - SaaS partner integrations

Each option has different capabilities, pricing models, and use cases.

## Resource Types and Pricing Models

| Resource Type | Pricing Model | Protocol | Best For |
|--------------|---------------|----------|----------|
| **Basic (Topics)** | Per operation | HTTP | Simple event routing |
| **Namespaces (Standard)** | Quota-based | MQTT + HTTP | IoT, pub-sub |
| **Namespaces (Premium)** | Quota-based | MQTT + HTTP | Enterprise IoT |
| **Domains** | Per operation | HTTP | Multi-tenant |
| **System Topics** | Free | HTTP | Azure events |
| **Partner Topics** | Free | HTTP | SaaS integrations |

## Event Grid Basic (Topics)

### Characteristics

- **Pay-per-operation** pricing model
- **HTTP push** delivery
- **CloudEvents and Event Grid schemas**
- **No upfront costs**
- **Serverless** - scales automatically
- **99.99% SLA** for Premium endpoints
- **Push-based** delivery model
- **At-least-once** delivery guarantee

### Pricing Structure

| Operation | Cost |
|-----------|------|
| **First 100,000 operations/month** | Free |
| **Beyond 100,000 operations** | $0.60 per million operations |
| **Advanced filtering** | $0.50 per million operations (additional) |
| **Premium endpoints (private links)** | $0.025 per hour per endpoint |

**What counts as an operation:**
- ✅ Publishing an event to a topic
- ✅ Delivery attempt to a subscriber
- ✅ Event Grid retries (each attempt)
- ✅ Management operations (create/update/delete)

### Core Features

#### 1. Event Publishing

```bash
# Create Event Grid topic
az eventgrid topic create \
  --name mytopic \
  --resource-group myResourceGroup \
  --location eastus

# Get endpoint and key
ENDPOINT=$(az eventgrid topic show --name mytopic --resource-group myResourceGroup --query endpoint -o tsv)
KEY=$(az eventgrid topic key list --name mytopic --resource-group myResourceGroup --query key1 -o tsv)
```

```csharp
// Publish events using .NET SDK
using Azure.Messaging.EventGrid;
using Azure;

var client = new EventGridPublisherClient(
    new Uri(endpoint),
    new AzureKeyCredential(key)
);

var events = new[]
{
    new EventGridEvent(
        subject: "orders/12345",
        eventType: "OrderCreated",
        dataVersion: "1.0",
        data: new { OrderId = "12345", Amount = 99.99 }
    )
};

await client.SendEventsAsync(events);
```

#### 2. Event Subscriptions

```bash
# Create webhook subscription
az eventgrid event-subscription create \
  --name mysubscription \
  --source-resource-id $(az eventgrid topic show --name mytopic --resource-group myResourceGroup --query id -o tsv) \
  --endpoint https://myapp.azurewebsites.net/api/webhook \
  --included-event-types OrderCreated OrderUpdated

# Create subscription with advanced filtering
az eventgrid event-subscription create \
  --name filteredsubscription \
  --source-resource-id $(az eventgrid topic show --name mytopic --resource-group myResourceGroup --query id -o tsv) \
  --endpoint https://myapp.azurewebsites.net/api/webhook \
  --advanced-filter data.Amount NumberGreaterThan 100
```

#### 3. Dead-Letter Configuration

```bash
# Configure dead-letter location
az eventgrid event-subscription create \
  --name mysubscription \
  --source-resource-id $(az eventgrid topic show --name mytopic --query id -o tsv) \
  --endpoint https://myapp.azurewebsites.net/api/webhook \
  --deadletter-endpoint /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/mystorage/blobServices/default/containers/deadletters \
  --max-delivery-attempts 30 \
  --event-ttl 1440
```

#### 4. Retry Policies

```json
{
  "retryPolicy": {
    "maxDeliveryAttempts": 30,
    "eventTimeToLiveInMinutes": 1440
  }
}
```

**Default retry schedule:**
- 10 seconds
- 30 seconds
- 1 minute
- 5 minutes
- 10 minutes
- 30 minutes
- 1 hour
- 3 hours
- Then every 3 hours (up to 24 hours)

### Delivery Targets

Event Grid Basic supports multiple endpoint types:

| Endpoint Type | Use Case |
|--------------|----------|
| **Webhooks** | Custom HTTP endpoints |
| **Azure Functions** | Serverless processing |
| **Azure Storage Queues** | Decoupled processing |
| **Azure Service Bus** | Reliable messaging |
| **Event Hubs** | Streaming scenarios |
| **Hybrid Connections** | On-premises integration |
| **Partner solutions** | Third-party integrations |

### When to Use Event Grid Basic

✅ **Use Event Grid Basic (Topics) when:**
- Simple event routing and distribution
- HTTP-based push delivery sufficient
- Low to moderate event volumes
- Cost-sensitive scenarios (pay only for usage)
- Integration with Azure services
- Webhook-based architectures
- Serverless event-driven applications
- No need for MQTT or IoT protocols

❌ **Don't use Event Grid Basic when:**
- Need MQTT protocol support
- IoT device connectivity required
- Need pull-based consumption model
- Require namespace-level isolation
- Very high-scale IoT scenarios

### Cost Examples

**Scenario 1: Low Volume**
- 50,000 events/month
- Single subscription
- 50,000 operations total
- **Cost**: $0 (within free tier)

**Scenario 2: Medium Volume**
- 5 million events/month
- 3 subscriptions
- 15 million operations total
- **Cost**: (15M - 0.1M) × $0.60/1M = ~$8.94/month

**Scenario 3: High Volume with Advanced Filtering**
- 50 million events/month
- 5 subscriptions with advanced filters
- 250 million operations
- **Cost**: 
  - Base: (250M - 0.1M) × $0.60/1M = ~$150
  - Advanced filtering: 250M × $0.50/1M = ~$125
  - **Total**: ~$275/month

## Event Grid Namespaces (Standard/Premium)

### Overview

**Event Grid Namespaces** introduce a new resource model with:
- **MQTT v3.1.1 and v5** protocol support
- **HTTP push and pull** delivery
- **Quota-based** pricing (not per-operation)
- **IoT-optimized** capabilities
- **Client authentication** with certificates
- **Namespace isolation**

### Standard vs Premium Namespaces

| Feature | Standard | Premium |
|---------|----------|---------|
| **Monthly Base Cost** | Included in quota | Included in quota |
| **Client Connections (MQTT)** | 1,000 per namespace | 10,000 per namespace |
| **Throughput** | 1 MB/s | 10 MB/s |
| **Storage** | 1 GB | 10 GB |
| **Requests/month** | 1 million | 10 million |
| **Availability Zones** | ❌ | ✅ |
| **Private Endpoints** | ❌ | ✅ |
| **Geo-DR** | ❌ | ✅ |
| **SLA** | 99.9% | 99.99% |
| **Use Case** | Development, Small IoT | Production, Large IoT |

### Standard Namespace Pricing

**Base Quota (included):**
- **$100/month** includes:
  - 1,000 MQTT client connections
  - 1 MB/s throughput
  - 1 GB storage
  - 1 million requests/month

**Overage Charges:**
- **Client connections**: $0.10 per connection/month (beyond 1,000)
- **Throughput**: $50 per MB/s/month (beyond 1 MB/s)
- **Storage**: $0.10 per GB/month (beyond 1 GB)
- **Requests**: $0.60 per million (beyond 1 million)

### Premium Namespace Pricing

**Base Quota (included):**
- **$1,000/month** includes:
  - 10,000 MQTT client connections
  - 10 MB/s throughput
  - 10 GB storage
  - 10 million requests/month

**Overage Charges:**
- **Client connections**: $0.08 per connection/month (beyond 10,000)
- **Throughput**: $40 per MB/s/month (beyond 10 MB/s)
- **Storage**: $0.08 per GB/month (beyond 10 GB)
- **Requests**: $0.48 per million (beyond 10 million)

### Namespace Features

#### 1. MQTT Support

```bash
# Create namespace with MQTT enabled
az eventgrid namespace create \
  --name myiotnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --topic-spaces-configuration "{state:Enabled}" \
  --sku standard
```

**MQTT Configuration:**
```python
# MQTT client connection
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="device001")
client.username_pw_set(username="myiotnamespace", password=sas_token)
client.tls_set(ca_certs="path/to/ca.pem")

client.connect("myiotnamespace.westus-1.ts.eventgrid.azure.net", 8883)
client.publish("devices/sensors/temperature", payload='{"temp": 72.5}')
```

#### 2. Client Groups and Topic Spaces

```bash
# Create client group
az eventgrid namespace client-group create \
  --namespace-name myiotnamespace \
  --resource-group myResourceGroup \
  --name sensors \
  --query "subjectMatchesFilter[?operatorType=='StringBeginsWith'].subject" \
  -o tsv

# Create topic space
az eventgrid namespace topic-space create \
  --namespace-name myiotnamespace \
  --resource-group myResourceGroup \
  --name sensor-data \
  --topic-templates "devices/+/temperature" "devices/+/humidity"
```

#### 3. Pull Delivery (HTTP)

```csharp
// Pull-based consumption (new in namespaces)
using Azure.Messaging.EventGrid.Namespaces;

var client = new EventGridClient(
    new Uri("https://myiotnamespace.westus-1.eventgrid.azure.net"),
    new AzureKeyCredential(key)
);

// Receive events
var events = await client.ReceiveCloudEventsAsync(
    topicName: "sensor-data",
    subscriptionName: "analytics-sub",
    maxEvents: 100,
    maxWaitTime: TimeSpan.FromSeconds(60)
);

foreach (var evt in events.Value)
{
    // Process event
    Console.WriteLine($"Event: {evt.Data}");
    
    // Acknowledge
    await client.AcknowledgeCloudEventsAsync(
        topicName: "sensor-data",
        subscriptionName: "analytics-sub",
        lockTokens: new[] { evt.BrokerProperties.LockToken }
    );
}
```

#### 4. Private Endpoints (Premium Only)

```bash
# Create private endpoint for Premium namespace
az network private-endpoint create \
  --name eventgrid-pe \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet privateSubnet \
  --private-connection-resource-id $(az eventgrid namespace show --name myiotnamespace --query id -o tsv) \
  --group-id namespace \
  --connection-name egConnection

# Disable public access
az eventgrid namespace update \
  --name myiotnamespace \
  --resource-group myResourceGroup \
  --public-network-access Disabled
```

### When to Use Namespaces

✅ **Use Event Grid Namespaces when:**
- **IoT scenarios** with MQTT devices
- Need **pull-based** consumption (HTTP pull delivery)
- Require **client authentication** with certificates
- Need **namespace-level isolation**
- High connection count (many concurrent clients)
- Bidirectional communication required
- Predictable monthly costs preferred
- Premium: Enterprise IoT with private networks

❌ **Don't use Namespaces when:**
- Simple HTTP push scenarios (use Basic topics)
- Don't need MQTT protocol
- Very low event volumes (per-operation cheaper)
- Only need Azure service integrations

### Cost Examples for Namespaces

**Standard Namespace Example:**
- 500 MQTT devices connected
- 0.5 MB/s average throughput
- 500 MB storage used
- 500,000 requests/month
- **Cost**: $100/month (all within base quota)

**Standard with Overage:**
- 2,000 MQTT devices
- 1.5 MB/s throughput
- 2 GB storage
- 2 million requests
- **Cost**: 
  - Base: $100
  - Connections: 1,000 × $0.10 = $100
  - Throughput: 0.5 MB/s × $50 = $25
  - Storage: 1 GB × $0.10 = $0.10
  - Requests: 1M × $0.60 = $0.60
  - **Total**: ~$226/month

**Premium Namespace Example:**
- 5,000 MQTT devices
- 5 MB/s throughput
- 5 GB storage
- 5 million requests
- Private endpoints
- **Cost**: $1,000/month (all within base quota)

## Domains Pricing

### Overview

**Event Grid Domains** enable multi-tenant event routing with a single endpoint.

### Pricing

- **Same as Basic Topics**: $0.60 per million operations
- **First 100,000 operations**: Free
- **Advanced filtering**: Additional $0.50 per million

### Features

```bash
# Create domain
az eventgrid domain create \
  --name mydomain \
  --resource-group myResourceGroup \
  --location eastus

# Create domain topic (logical partition)
az eventgrid domain topic create \
  --name customer1 \
  --domain-name mydomain \
  --resource-group myResourceGroup

# Subscribe to domain topic
az eventgrid event-subscription create \
  --name customer1-sub \
  --source-resource-id $(az eventgrid domain topic show --name customer1 --domain-name mydomain --query id -o tsv) \
  --endpoint https://customer1.com/webhook
```

### When to Use Domains

✅ **Use Domains when:**
- Multi-tenant SaaS applications
- Need to route events to different customers
- Centralized event ingestion with tenant isolation
- Single endpoint for multiple logical topics

## System Topics

### Overview

**System Topics** provide events from Azure resources automatically.

### Pricing

- **Free** - No charge for system topic events
- **Only pay for event delivery** (subscriptions)
- Same subscription pricing as Basic topics

### Example

```bash
# Create system topic for Storage account
az eventgrid system-topic create \
  --name mystoragesystemtopic \
  --resource-group myResourceGroup \
  --source /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/mystorage \
  --topic-type Microsoft.Storage.StorageAccounts \
  --location eastus

# Subscribe to blob created events
az eventgrid system-topic event-subscription create \
  --name blobcreated \
  --system-topic-name mystoragesystemtopic \
  --resource-group myResourceGroup \
  --endpoint https://myapp.com/api/blobcreated \
  --included-event-types Microsoft.Storage.BlobCreated
```

### Available System Topics

- Azure Storage (Blob, Queue)
- Azure Container Registry
- Azure IoT Hub
- Azure Key Vault
- Azure App Service
- Azure Resource Manager
- Azure Service Bus
- Azure Event Hubs
- Many more...

## Partner Topics

### Overview

**Partner Topics** enable event integration with SaaS partners.

### Pricing

- **Free** to receive events from partners
- **Pay only for event delivery** (subscriptions)

### Supported Partners

- Auth0
- Microsoft Graph (Microsoft 365)
- SAP
- And more...

## Detailed Feature Comparison

### Protocol Support

| Resource Type | HTTP Push | HTTP Pull | MQTT | WebSockets |
|--------------|-----------|-----------|------|------------|
| **Basic Topics** | ✅ | ❌ | ❌ | ❌ |
| **Namespaces** | ✅ | ✅ | ✅ | ❌ |
| **Domains** | ✅ | ❌ | ❌ | ❌ |
| **System Topics** | ✅ | ❌ | ❌ | ❌ |

### Security Features

| Feature | Basic Topics | Namespaces (Std) | Namespaces (Prem) |
|---------|-------------|------------------|-------------------|
| **Managed Identity** | ✅ | ✅ | ✅ |
| **Private Endpoints** | ✅ (extra cost) | ❌ | ✅ |
| **VNet Integration** | ✅ | ❌ | ✅ |
| **Customer-Managed Keys** | ✅ | ❌ | ✅ |
| **Certificate Auth (MQTT)** | N/A | ✅ | ✅ |
| **IP Filtering** | ✅ | ✅ | ✅ |

### Event Delivery

| Feature | Basic Topics | Namespaces |
|---------|-------------|------------|
| **Delivery Guarantee** | At-least-once | At-least-once |
| **Max Retention** | 24 hours | 7 days |
| **Max Retries** | 30 attempts | Configurable |
| **Dead-Lettering** | ✅ | ✅ |
| **Batching** | ✅ | ✅ |
| **Ordered Delivery** | ❌ | Session-based |

## Performance Characteristics

### Event Grid Basic (Topics)

- **Ingress**: Virtually unlimited (auto-scales)
- **Latency**: Sub-second (P99 < 1s)
- **Throughput**: 5,000+ events/sec per topic
- **Concurrent subscribers**: 500 per topic

### Event Grid Namespaces

**Standard:**
- **MQTT Connections**: 1,000 (base quota)
- **Throughput**: 1 MB/s (base quota)
- **Latency**: <100ms (MQTT publish)

**Premium:**
- **MQTT Connections**: 10,000 (base quota)
- **Throughput**: 10 MB/s (base quota)
- **Latency**: <50ms (MQTT publish)
- **Availability Zones**: 99.99% SLA

## Choosing the Right Option

### Decision Tree

```
Start
│
├─ Need MQTT protocol?
│  └─ YES → Event Grid Namespace (Standard or Premium)
│  └─ NO → Continue
│
├─ Need pull-based delivery?
│  └─ YES → Event Grid Namespace
│  └─ NO → Continue
│
├─ IoT scenario with many devices?
│  └─ YES → Event Grid Namespace Premium
│  └─ NO → Continue
│
├─ Multi-tenant SaaS?
│  └─ YES → Event Grid Domain
│  └─ NO → Continue
│
├─ Azure resource events only?
│  └─ YES → System Topic
│  └─ NO → Continue
│
└─ Simple HTTP event routing?
   └─ YES → Event Grid Basic (Topics)
```

### Selection by Use Case

| Use Case | Recommended Option | Reasoning |
|----------|-------------------|-----------|
| **Azure Resource Events** | System Topics | Free, automatic |
| **Simple Event Routing** | Basic Topics | Pay-per-use, simple |
| **IoT Telemetry** | Namespace (Standard/Premium) | MQTT support |
| **Multi-tenant SaaS** | Domains | Tenant isolation |
| **High-volume Push** | Basic Topics | Auto-scales, cost-effective |
| **Pull-based Consumption** | Namespaces | HTTP pull delivery |
| **Enterprise IoT** | Namespace Premium | Private endpoints, SLA |
| **Serverless Apps** | Basic Topics | Integrates with Functions |

## Pricing Considerations

### Cost Comparison Scenarios

**Scenario 1: Simple Event Routing (1M events/month)**

| Option | Monthly Cost |
|--------|-------------|
| Basic Topics | $0.54 |
| Standard Namespace | $100 |
| Premium Namespace | $1,000 |

**Winner**: Basic Topics

**Scenario 2: IoT (5,000 MQTT devices, 5M events)**

| Option | Monthly Cost |
|--------|-------------|
| Basic Topics (HTTP only) | Not applicable |
| Standard Namespace | ~$500 |
| Premium Namespace | $1,000 |

**Winner**: Standard Namespace (if <10K devices)

**Scenario 3: Enterprise IoT (20K devices, private network)**

| Option | Monthly Cost |
|--------|-------------|
| Standard Namespace | $1,100+ (no private endpoints) |
| Premium Namespace | $1,800 |

**Winner**: Premium Namespace (private endpoints included)

### Cost Optimization Strategies

1. **Use System Topics for Azure Events**
   ```bash
   # Free event source
   az eventgrid system-topic create --source /subscriptions/.../storageAccounts/...
   ```

2. **Batch Events**
   ```csharp
   // Reduce operation count
   await client.SendEventsAsync(batchOf100Events);
   ```

3. **Right-size Namespace Tier**
   ```bash
   # Don't over-provision
   # Use Standard if <10K devices
   az eventgrid namespace create --sku standard
   ```

4. **Use Basic for Simple Routing**
   ```bash
   # Pay-per-use for low volumes
   az eventgrid topic create  # Basic pricing
   ```

## Migration Paths

### Basic Topics → Namespaces

```bash
# No direct migration - parallel deployment
# 1. Create namespace
az eventgrid namespace create --name myns --sku standard

# 2. Update publishers to new endpoint
# 3. Create new subscriptions in namespace
# 4. Cutover traffic
# 5. Decommission old topic
```

**Considerations:**
- Different APIs (EventGridEvent vs CloudEvents)
- Connection strings change
- Protocol changes (HTTP → MQTT if needed)

### Standard → Premium Namespace

```bash
# Requires recreation
# 1. Create Premium namespace
az eventgrid namespace create --name mynewns --sku premium

# 2. Reconfigure clients
# 3. Cutover
# 4. Delete Standard namespace
```

## Exam Questions and Scenarios

### Question 1: IoT Protocol

**Scenario:** You need to connect 10,000 IoT devices using MQTT protocol.

**Question:** Which Event Grid option should you use?

**Answer:** **Event Grid Namespace (Premium)**

**Reasoning:**
- ✅ Namespace supports MQTT
- ✅ Premium supports 10,000+ connections
- ❌ Basic Topics don't support MQTT
- ❌ Standard Namespace base quota only 1,000 connections

### Question 2: Cost Optimization

**Scenario:** You publish 50,000 events/month from Azure Storage to a webhook.

**Question:** What is the most cost-effective option?

**Answer:** **System Topic (Free) + Basic Topic subscription**

**Reasoning:**
- ✅ System Topics are free
- ✅ 50K operations within free tier
- **Cost**: $0

### Question 3: Pull-based Delivery

**Scenario:** Your application needs to pull events on demand rather than receive push notifications.

**Question:** Which option supports this?

**Answer:** **Event Grid Namespace**

**Reasoning:**
- ✅ Namespaces support HTTP pull delivery
- ❌ Basic Topics only support HTTP push
- ❌ System Topics only support push

### Question 4: Multi-tenant Routing

**Scenario:** You have a SaaS application with 1,000 customers, each needing separate event routing.

**Question:** Which Event Grid option is designed for this?

**Answer:** **Event Grid Domains**

**Reasoning:**
- ✅ Domains designed for multi-tenant scenarios
- ✅ Single endpoint, logical partitioning
- ✅ Per-tenant subscriptions

## Best Practices

### General Best Practices

1. **Use System Topics for Azure Events**
   ```bash
   # Free event source for Azure resources
   az eventgrid system-topic create \
     --source /subscriptions/.../providers/Microsoft.Storage/storageAccounts/...
   ```

2. **Implement Dead-Lettering**
   ```bash
   # Don't lose failed events
   az eventgrid event-subscription create \
     --deadletter-endpoint /subscriptions/.../storageAccounts/.../blobServices/default/containers/deadletters
   ```

3. **Use Managed Identities**
   ```bash
   # Avoid connection strings
   az eventgrid event-subscription create \
     --endpoint-type eventhub \
     --delivery-identity-endpoint-type systemassigned
   ```

4. **Monitor Delivery Failures**
   ```bash
   # Track failed deliveries
   az monitor metrics list \
     --resource $(az eventgrid topic show --query id -o tsv) \
     --metric PublishFailCount DeliveryFailCount
   ```

### Namespace Best Practices

1. **Use Client Groups for Authorization**
   ```bash
   # Organize clients by type/permission
   az eventgrid namespace client-group create \
     --name sensors \
     --query subjectMatchesFilter
   ```

2. **Implement Topic Spaces**
   ```bash
   # Define topic hierarchies
   az eventgrid namespace topic-space create \
     --topic-templates "factory/+/sensors/+"
   ```

3. **Enable Private Endpoints (Premium)**
   ```bash
   # Secure IoT communications
   az network private-endpoint create --group-id namespace
   ```

4. **Monitor Connection Count**
   ```bash
   # Track MQTT client connections
   az monitor metrics list --metric MqttConnections
   ```

## References

- [Event Grid pricing](https://azure.microsoft.com/en-us/pricing/details/event-grid/)
- [Event Grid namespaces](https://learn.microsoft.com/en-us/azure/event-grid/namespaces-overview)
- [Event Grid MQTT support](https://learn.microsoft.com/en-us/azure/event-grid/mqtt-overview)
- [Event Grid domains](https://learn.microsoft.com/en-us/azure/event-grid/event-domains)
- [System topics](https://learn.microsoft.com/en-us/azure/event-grid/system-topics)
- [Event Grid quotas](https://learn.microsoft.com/en-us/azure/event-grid/quotas-limits)
