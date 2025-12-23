# Azure Service Bus Service Tiers

## Table of Contents

- [Overview](#overview)
- [Service Tiers Comparison](#service-tiers-comparison)
- [Basic Tier](#basic-tier)
- [Standard Tier](#standard-tier)
- [Premium Tier](#premium-tier)
- [Detailed Feature Comparison](#detailed-feature-comparison)
- [Messaging Units (Premium Tier)](#messaging-units-premium-tier)
- [Performance Characteristics](#performance-characteristics)
- [Choosing the Right Tier](#choosing-the-right-tier)
- [Pricing Considerations](#pricing-considerations)
- [Migration Between Tiers](#migration-between-tiers)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Service Bus offers three pricing tiers: **Basic**, **Standard**, and **Premium**. Each tier is designed for different messaging scenarios, with varying features, throughput capabilities, and pricing models. The tier you choose affects the messaging features available, performance guarantees, and cost structure.

## Service Tiers Comparison

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| **Queues** | ✅ | ✅ | ✅ |
| **Topics & Subscriptions** | ❌ | ✅ | ✅ |
| **Max Queue/Topic Size** | 1 GB | 1-5 GB | 1-80 GB |
| **Max Message Size** | 256 KB | 256 KB | 1 MB (100 MB in batches) |
| **Transactions** | ❌ | ✅ | ✅ |
| **Duplicate Detection** | ❌ | ✅ | ✅ |
| **Sessions** | ❌ | ✅ | ✅ |
| **Scheduled Messages** | ❌ | ✅ | ✅ |
| **Dead-letter Queues** | ✅ | ✅ | ✅ |
| **Forwarding** | ❌ | ✅ | ✅ |
| **Resource Type** | Shared | Shared | Dedicated (Messaging Units) |
| **Performance** | Variable | Variable | Predictable |
| **Throughput** | Limited | Moderate | High |
| **Latency** | Variable | Variable | Low, predictable |
| **VNet Integration** | ❌ | ❌ | ✅ |
| **Private Endpoints** | ❌ | ❌ | ✅ |
| **Geo-disaster Recovery** | ❌ | ✅ | ✅ |
| **Availability Zones** | ❌ | ❌ | ✅ |
| **Customer-Managed Keys** | ❌ | ❌ | ✅ |
| **SLA** | None | 99.9% | 99.95% |
| **Best For** | Dev/Test, Simple queues | Production, Pub/Sub | Enterprise, High-throughput |

## Basic Tier

### Characteristics

- **Queue-only** - No topics or subscriptions
- **Shared infrastructure** - Resources shared with other customers
- **Limited features** - Basic messaging only
- **Variable performance** - No performance guarantees
- **Low cost** - Entry-level pricing
- **No SLA** - Best-effort delivery
- **256 KB message size** limit

### When to Use

✅ **Use Basic tier when:**
- Development and testing environments
- Learning Azure Service Bus
- Simple point-to-point messaging (queues only)
- Low message volumes
- Cost is primary concern
- No pub/sub patterns needed
- No advanced features required

❌ **Don't use Basic when:**
- Need topics and subscriptions (pub/sub)
- Require transactions or sessions
- Need performance guarantees
- Production workloads
- Require duplicate detection
- Need scheduled messages

### Limitations

- ❌ **No topics/subscriptions** - Queue-only
- ❌ **No transactions**
- ❌ **No duplicate detection**
- ❌ **No sessions**
- ❌ **No scheduled messages**
- ❌ **No message forwarding**
- ❌ **No geo-disaster recovery**
- ❌ **Variable performance**
- ❌ **No SLA**

### Code Example

```bash
# Create Basic tier namespace
az servicebus namespace create \
  --name mybasicnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Basic

# Create queue (only option in Basic)
az servicebus queue create \
  --namespace-name mybasicnamespace \
  --resource-group myResourceGroup \
  --name myqueue \
  --max-size 1024
```

**.NET Example:**
```csharp
using Azure.Messaging.ServiceBus;

// Connect to Basic tier namespace
var client = new ServiceBusClient(connectionString);
var sender = client.CreateSender("myqueue");

// Send message (max 256 KB)
var message = new ServiceBusMessage("Hello from Basic tier");
await sender.SendMessageAsync(message);

// Receive message
var receiver = client.CreateReceiver("myqueue");
ServiceBusReceivedMessage receivedMessage = await receiver.ReceiveMessageAsync();
await receiver.CompleteMessageAsync(receivedMessage);
```

### Cost Example

- **Base price**: ~$0.05 per million operations
- **No minimum charge**
- Operations include: Send, Receive, Peek
- Most cost-effective for low-volume scenarios

## Standard Tier

### Characteristics

- **Queues AND Topics/Subscriptions** - Full pub/sub support
- **Advanced features** - Transactions, sessions, duplicate detection
- **Shared infrastructure** - Resources shared but better than Basic
- **Variable performance** - Better than Basic, but not guaranteed
- **Pay-per-operation** pricing model
- **99.9% SLA**
- **256 KB message size** limit
- **Geo-disaster recovery** support

### Advanced Features

#### 1. Topics and Subscriptions (Pub/Sub)

```bash
# Create topic
az servicebus topic create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name mytopic \
  --max-size 2048

# Create subscriptions with filters
az servicebus topic subscription create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --topic-name mytopic \
  --name high-priority-sub

# Add SQL filter
az servicebus topic subscription rule create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --topic-name mytopic \
  --subscription-name high-priority-sub \
  --name HighPriorityFilter \
  --filter-sql-expression "Priority='High'"
```

**.NET Example:**
```csharp
// Send to topic
var sender = client.CreateSender("mytopic");
var message = new ServiceBusMessage("Order created")
{
    ApplicationProperties =
    {
        { "Priority", "High" },
        { "OrderType", "Express" }
    }
};
await sender.SendMessageAsync(message);

// Receive from subscription (filtered messages)
var receiver = client.CreateReceiver("mytopic", "high-priority-sub");
ServiceBusReceivedMessage msg = await receiver.ReceiveMessageAsync();
```

#### 2. Sessions (FIFO Guarantee)

```csharp
// Send messages with session
var sender = client.CreateSender("myqueue");
var messages = new[]
{
    new ServiceBusMessage("Order 1") { SessionId = "customer123" },
    new ServiceBusMessage("Order 2") { SessionId = "customer123" },
    new ServiceBusMessage("Order 3") { SessionId = "customer123" }
};
await sender.SendMessagesAsync(messages);

// Receive session messages (guaranteed order)
var sessionReceiver = await client.AcceptSessionAsync(
    "myqueue",
    "customer123"
);

while (true)
{
    var message = await sessionReceiver.ReceiveMessageAsync(TimeSpan.FromSeconds(5));
    if (message == null) break;
    
    Console.WriteLine(message.Body.ToString());
    await sessionReceiver.CompleteMessageAsync(message);
}
```

#### 3. Duplicate Detection

```bash
# Enable duplicate detection (must be set at queue creation)
az servicebus queue create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name myqueue \
  --enable-duplicate-detection true \
  --duplicate-detection-history-time-window PT10M
```

```csharp
// Send messages with duplicate detection
var sender = client.CreateSender("myqueue");

var message1 = new ServiceBusMessage("Important transaction")
{
    MessageId = "txn-12345" // Unique ID for duplicate detection
};

var message2 = new ServiceBusMessage("Important transaction")
{
    MessageId = "txn-12345" // Same ID - will be deduplicated
};

await sender.SendMessageAsync(message1);
await sender.SendMessageAsync(message2); // Silently dropped if within detection window
```

#### 4. Transactions

```csharp
// Atomic transaction across multiple operations
var sender1 = client.CreateSender("queue1");
var sender2 = client.CreateSender("queue2");
var receiver = client.CreateReceiver("inputqueue");

var receivedMessage = await receiver.ReceiveMessageAsync();

using (var scope = new TransactionScope(TransactionScopeAsyncFlowOption.Enabled))
{
    // All operations succeed or fail together
    await sender1.SendMessageAsync(new ServiceBusMessage("Step 1"));
    await sender2.SendMessageAsync(new ServiceBusMessage("Step 2"));
    await receiver.CompleteMessageAsync(receivedMessage);
    
    scope.Complete(); // Commit transaction
}
```

#### 5. Scheduled Messages

```csharp
// Schedule message for future delivery
var message = new ServiceBusMessage("Reminder: Meeting in 1 hour");
var scheduledTime = DateTimeOffset.UtcNow.AddHours(1);

long sequenceNumber = await sender.ScheduleMessageAsync(
    message,
    scheduledTime
);

// Cancel scheduled message if needed
await sender.CancelScheduledMessageAsync(sequenceNumber);
```

#### 6. Auto-forwarding

```bash
# Create queue with auto-forwarding
az servicebus queue create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name sourcequeue \
  --forward-to targetqueue

# Auto-forward from subscription to queue
az servicebus topic subscription create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --topic-name mytopic \
  --name mysub \
  --forward-to myqueue
```

### When to Use

✅ **Use Standard tier when:**
- Production applications
- Need pub/sub patterns (topics/subscriptions)
- Require message filtering and routing
- Need sessions for FIFO guarantees
- Require duplicate detection
- Need scheduled messages
- Variable workload with pay-per-operation model
- Geo-disaster recovery needed
- Multiple subscribers for messages

❌ **Don't use Standard when:**
- Need dedicated resources and predictable performance (use Premium)
- Require very large messages >256 KB (use Premium)
- Need VNet integration (use Premium)
- High-throughput, low-latency requirements (use Premium)

### Code Example: Complete Pub/Sub Pattern

```bash
# Create Standard namespace
az servicebus namespace create \
  --name mystandardnamespace \
  --resource-group myResourceGroup \
  --sku Standard \
  --location eastus

# Create topic
az servicebus topic create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name orders

# Create subscriptions for different services
az servicebus topic subscription create \
  --namespace-name mystandardnamespace \
  --topic-name orders \
  --name inventory-service

az servicebus topic subscription create \
  --namespace-name mystandardnamespace \
  --topic-name orders \
  --name shipping-service

az servicebus topic subscription create \
  --namespace-name mystandardnamespace \
  --topic-name orders \
  --name analytics-service
```

**.NET Publisher:**
```csharp
var sender = client.CreateSender("orders");

var orderMessage = new ServiceBusMessage(JsonSerializer.Serialize(new
{
    OrderId = "ORD-001",
    CustomerId = "CUST-123",
    Amount = 99.99,
    Priority = "High"
}))
{
    ContentType = "application/json",
    Subject = "OrderCreated",
    ApplicationProperties =
    {
        { "OrderType", "Express" },
        { "Region", "US-East" }
    }
};

await sender.SendMessageAsync(orderMessage);
```

**.NET Subscribers:**
```csharp
// Inventory Service
var inventoryReceiver = client.CreateReceiver("orders", "inventory-service");
var message = await inventoryReceiver.ReceiveMessageAsync();
// Process inventory update
await inventoryReceiver.CompleteMessageAsync(message);

// Shipping Service
var shippingReceiver = client.CreateReceiver("orders", "shipping-service");
var message = await shippingReceiver.ReceiveMessageAsync();
// Process shipping label creation
await shippingReceiver.CompleteMessageAsync(message);

// Analytics Service
var analyticsReceiver = client.CreateReceiver("orders", "analytics-service");
var message = await analyticsReceiver.ReceiveMessageAsync();
// Process analytics
await analyticsReceiver.CompleteMessageAsync(message);
```

### Cost Example

- **Base price**: ~$0.05 per million operations
- **Relay hours**: ~$0.013 per relay hour (for topics)
- Variable cost based on actual usage
- Cost-effective for moderate-volume production workloads

## Premium Tier

### Characteristics

- **Dedicated resources** - Messaging Units (MU) provide isolated capacity
- **Predictable performance** - Guaranteed throughput and low latency
- **Large messages** - Up to 1 MB (100 MB with batching)
- **VNet integration** - Private endpoints and service endpoints
- **Availability zones** - Zone redundancy for high availability
- **Customer-managed keys** - Encryption with your own keys
- **99.95% SLA** - Higher availability guarantee
- **Advanced security** - Network isolation options
- **All Standard features** - Plus premium capabilities

### Messaging Units (MU)

Premium tier uses **Messaging Units** for capacity allocation:

- **1 MU**: Base capacity unit
- **2 MU, 4 MU, 8 MU, 16 MU**: Higher capacity levels
- Each MU provides:
  - Dedicated CPU and memory
  - Predictable throughput
  - Isolated from other customers
  - Can be scaled up/down

**Capacity per MU (approximate):**
- **Throughput**: ~1,000 messages/sec (depending on message size)
- **Connections**: Thousands of concurrent connections
- **Storage**: Up to 80 GB per entity

```bash
# Create Premium namespace with 1 MU
az servicebus namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 1 \
  --location eastus

# Scale to 2 MUs
az servicebus namespace update \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --capacity 2
```

### Premium Features

#### 1. Large Message Support

```csharp
// Send 1 MB message (Premium only)
var largePayload = new byte[1 * 1024 * 1024]; // 1 MB
var message = new ServiceBusMessage(largePayload);
await sender.SendMessageAsync(message);

// Batch large messages (up to 100 MB total)
var batch = await sender.CreateMessageBatchAsync();
for (int i = 0; i < 100; i++)
{
    var msg = new ServiceBusMessage(new byte[1024 * 1024]); // 1 MB each
    if (batch.TryAddMessage(msg))
    {
        // Message added to batch
    }
}
await sender.SendMessagesAsync(batch);
```

#### 2. VNet Integration

```bash
# Create Premium namespace with private endpoint
az servicebus namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 1

# Create private endpoint
az network private-endpoint create \
  --name sb-private-endpoint \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet privateSubnet \
  --private-connection-resource-id $(az servicebus namespace show --name mypremiumnamespace --resource-group myResourceGroup --query id -o tsv) \
  --group-id namespace \
  --connection-name sbConnection

# Disable public access
az servicebus namespace network-rule-set update \
  --namespace-name mypremiumnamespace \
  --resource-group myResourceGroup \
  --default-action Deny \
  --public-network-access Disabled
```

#### 3. Availability Zones

```bash
# Create Premium namespace with zone redundancy
az servicebus namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 1 \
  --zone-redundant true \
  --location eastus
```

**Benefits:**
- Automatic replication across 3 availability zones
- Protection against datacenter failures
- No additional configuration needed
- Transparent to application code

#### 4. Customer-Managed Keys (CMK)

```bash
# Create Key Vault and key
az keyvault create \
  --name mykeyvault \
  --resource-group myResourceGroup

az keyvault key create \
  --vault-name mykeyvault \
  --name sb-encryption-key \
  --kty RSA \
  --size 2048

# Enable CMK on namespace
az servicebus namespace encryption create \
  --namespace-name mypremiumnamespace \
  --resource-group myResourceGroup \
  --encryption-config key-name=sb-encryption-key \
    key-vault-uri=https://mykeyvault.vault.azure.net \
    user-assigned-identity=/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identity}
```

#### 5. Geo-Disaster Recovery (Standard & Premium)

```bash
# Set up geo-pairing
az servicebus georecovery-alias set \
  --resource-group myResourceGroup \
  --namespace-name primary-namespace \
  --alias mygeoalias \
  --partner-namespace /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ServiceBus/namespaces/secondary-namespace

# Failover to secondary
az servicebus georecovery-alias fail-over \
  --resource-group myResourceGroup \
  --namespace-name secondary-namespace \
  --alias mygeoalias
```

### When to Use

✅ **Use Premium tier when:**
- Enterprise production workloads
- Need predictable, low-latency performance
- High-throughput requirements (>1,000 msg/sec)
- Large messages (>256 KB)
- VNet integration required for security
- Compliance requirements (CMK, network isolation)
- Mission-critical applications
- Need 99.95% SLA
- Zone redundancy for high availability
- Sensitive to performance variability

### Performance Guarantees

**Latency:**
- **Standard**: Variable (typically 20-100ms)
- **Premium**: Predictable (<10ms P99)

**Throughput per MU:**
- **1 MB messages**: ~100 msg/sec
- **100 KB messages**: ~1,000 msg/sec
- **10 KB messages**: ~5,000 msg/sec
- **1 KB messages**: ~10,000 msg/sec

### Cost Example

- **1 MU**: ~$670/month
- **2 MU**: ~$1,340/month
- **4 MU**: ~$2,680/month
- **8 MU**: ~$5,360/month
- **16 MU**: ~$10,720/month

**Plus messaging operations** (much cheaper than Standard per operation)

## Detailed Feature Comparison

### Messaging Features

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| **Queues** | ✅ | ✅ | ✅ |
| **Topics/Subscriptions** | ❌ | ✅ | ✅ |
| **Dead-letter Queues** | ✅ | ✅ | ✅ |
| **Scheduled Messages** | ❌ | ✅ | ✅ |
| **Message Sessions** | ❌ | ✅ | ✅ |
| **Duplicate Detection** | ❌ | ✅ | ✅ |
| **Transactions** | ❌ | ✅ | ✅ |
| **Auto-forwarding** | ❌ | ✅ | ✅ |
| **Batch Operations** | ✅ | ✅ | ✅ |
| **Prefetch** | ✅ | ✅ | ✅ |

### Message Specifications

| Specification | Basic | Standard | Premium |
|---------------|-------|----------|---------|
| **Max Message Size** | 256 KB | 256 KB | 1 MB (100 MB batch) |
| **Max Queue/Topic Size** | 1 GB | 1-5 GB | 1-80 GB |
| **Max TTL** | 14 days | 14 days | 14 days |
| **Max Lock Duration** | 5 minutes | 5 minutes | 5 minutes |
| **Max Delivery Count** | 10 | 10 | 10 |

### Security & Network

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| **TLS/SSL** | ✅ | ✅ | ✅ |
| **SAS Authentication** | ✅ | ✅ | ✅ |
| **Azure AD/Managed Identity** | ✅ | ✅ | ✅ |
| **IP Firewall** | ❌ | ✅ | ✅ |
| **VNet Service Endpoints** | ❌ | ❌ | ✅ |
| **Private Endpoints** | ❌ | ❌ | ✅ |
| **Customer-Managed Keys** | ❌ | ❌ | ✅ |

### High Availability

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| **Geo-disaster Recovery** | ❌ | ✅ | ✅ |
| **Availability Zones** | ❌ | ❌ | ✅ |
| **SLA** | None | 99.9% | 99.95% |
| **Active Replication** | ❌ | ❌ | ✅ |

## Performance Characteristics

### Throughput Comparison

```
Premium (8 MU):  ████████████████████████████████ ~80,000 msg/sec (1KB)
Premium (4 MU):  ████████████████ ~40,000 msg/sec (1KB)
Premium (2 MU):  ████████ ~20,000 msg/sec (1KB)
Premium (1 MU):  ████ ~10,000 msg/sec (1KB)
Standard:        ██ ~2,000 msg/sec (1KB, variable)
Basic:           █ ~500 msg/sec (1KB, variable)
```

### Latency Characteristics

**End-to-end latency (send + receive):**

| Tier | P50 | P95 | P99 |
|------|-----|-----|-----|
| **Basic** | 50ms | 150ms | 300ms |
| **Standard** | 30ms | 80ms | 150ms |
| **Premium (1 MU)** | 5ms | 8ms | 10ms |
| **Premium (4 MU)** | 3ms | 5ms | 7ms |

## Choosing the Right Tier

### Decision Tree

```
Start
│
├─ Need predictable performance or VNet integration?
│  └─ YES → Premium
│  └─ NO → Continue
│
├─ Need topics/subscriptions (pub/sub)?
│  └─ YES → Standard or Premium
│  └─ NO → Continue
│
├─ Need advanced features (sessions, transactions, duplicate detection)?
│  └─ YES → Standard or Premium
│  └─ NO → Continue
│
├─ Production workload with SLA?
│  └─ YES → Standard or Premium
│  └─ NO → Continue
│
└─ Development/testing or simple queues?
   └─ YES → Basic
```

### Selection by Use Case

| Use Case | Recommended Tier | Reasoning |
|----------|------------------|-----------|
| **Learning Service Bus** | Basic | Low cost, full API compatibility |
| **Dev/Test Simple Queue** | Basic | Cost-effective for development |
| **Event-driven Microservices** | Standard | Topics for pub/sub patterns |
| **Order Processing** | Standard or Premium | Transactions, sessions, reliability |
| **High-volume IoT** | Premium | Throughput, predictable performance |
| **Financial Transactions** | Premium | Low latency, reliability, CMK |
| **Multi-region App** | Standard or Premium | Geo-disaster recovery |
| **Regulated Industry** | Premium | Network isolation, CMK, zones |
| **Real-time Analytics** | Premium | High throughput, low latency |
| **E-commerce Platform** | Premium | Performance, zones, large messages |

## Pricing Considerations

### Cost Comparison

**Scenario 1: Low Volume (100,000 operations/month)**

| Tier | Monthly Cost |
|------|-------------|
| Basic | ~$5 |
| Standard | ~$10 |
| Premium (1 MU) | ~$670 |

**Winner**: Basic or Standard

**Scenario 2: High Volume (100 million operations/month)**

| Tier | Monthly Cost |
|------|-------------|
| Basic | ~$5,000 |
| Standard | ~$5,000 |
| Premium (2 MU) | ~$1,340 + operations |

**Winner**: Premium (predictable cost, better performance)

**Scenario 3: Enterprise with VNet Requirements**

| Tier | Monthly Cost |
|------|-------------|
| Basic | Not supported |
| Standard | Not supported |
| Premium (4 MU) | ~$2,680 |

**Winner**: Premium (only option)

### Cost Optimization Strategies

1. **Right-size Message Units (Premium)**
   ```bash
   # Monitor and adjust MU based on usage
   az servicebus namespace update \
     --name mynamespace \
     --resource-group myResourceGroup \
     --capacity 2
   ```

2. **Use Batching**
   ```csharp
   // Reduce operations count by batching
   var batch = await sender.CreateMessageBatchAsync();
   foreach (var item in items)
   {
       batch.TryAddMessage(new ServiceBusMessage(item));
   }
   await sender.SendMessagesAsync(batch);
   ```

3. **Optimize Message Size**
   - Compress payloads
   - Remove unnecessary data
   - Use references instead of full objects

4. **Choose Appropriate Tier per Environment**
   - Development: Basic
   - Staging: Standard
   - Production: Standard or Premium

## Migration Between Tiers

### Upgrade Path

**Basic → Standard:**
```bash
# Upgrade (preserves queues)
az servicebus namespace update \
  --name mybasicnamespace \
  --resource-group myResourceGroup \
  --sku Standard
```

**Standard → Premium:**
```bash
# Note: Requires data migration (different namespace)
# 1. Create new Premium namespace
az servicebus namespace create \
  --name mynewpremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 1

# 2. Migrate queues and topics (manual or scripted)
# 3. Update application connection strings
# 4. Cutover traffic
# 5. Delete old namespace
```

### Migration Considerations

**Basic ↔ Standard:**
- ✅ Direct upgrade/downgrade supported
- ✅ No data loss
- ✅ Minimal downtime
- ⚠️ Downgrading loses topics/subscriptions

**Standard ↔ Premium:**
- ❌ No direct migration
- ⚠️ Requires new namespace
- ⚠️ Must migrate data
- ⚠️ Application connection string changes

### Migration Script Example

```csharp
// Migrate messages from Standard to Premium
var sourceClient = new ServiceBusClient(sourceConnectionString);
var targetClient = new ServiceBusClient(targetConnectionString);

var sourceReceiver = sourceClient.CreateReceiver("sourcequeue");
var targetSender = targetClient.CreateSender("targetqueue");

// Peek and forward messages
await foreach (var message in sourceReceiver.ReceiveMessagesAsync(maxMessages: 100))
{
    // Forward to target
    var newMessage = new ServiceBusMessage(message.Body)
    {
        ContentType = message.ContentType,
        MessageId = message.MessageId,
        SessionId = message.SessionId
    };
    
    // Copy application properties
    foreach (var prop in message.ApplicationProperties)
    {
        newMessage.ApplicationProperties[prop.Key] = prop.Value;
    }
    
    await targetSender.SendMessageAsync(newMessage);
    await sourceReceiver.CompleteMessageAsync(message);
}
```

## Exam Questions and Scenarios

### Question 1: Topics and Subscriptions

**Scenario:** You need to implement a pub/sub pattern where multiple services subscribe to order events. Each service needs to receive all order messages.

**Question:** What is the minimum tier required?

**Answer:** **Standard**

**Reasoning:**
- ✅ Standard supports topics and subscriptions
- ❌ Basic only supports queues (no topics)
- ✅ Premium also supports but more expensive
- Topics are essential for pub/sub patterns

### Question 2: Message Size Requirements

**Scenario:** Your application needs to send messages that are 500 KB in size.

**Question:** Which tier(s) can support this requirement?

**Answer:** **Premium only**

**Reasoning:**
- ❌ Basic: Maximum 256 KB
- ❌ Standard: Maximum 256 KB
- ✅ Premium: Up to 1 MB (100 MB in batches)
- Must use Premium for messages >256 KB

### Question 3: Network Isolation

**Scenario:** Your company's security policy requires that Service Bus must be accessible only from within your Azure VNet and not from the public internet.

**Question:** Which tier and configuration do you need?

**Answer:** **Premium with Private Endpoints**

**Reasoning:**
- ✅ Only Premium supports Private Endpoints
- ✅ Can disable public access completely
- ❌ Basic and Standard don't support VNet integration
- Premium required for network isolation

### Question 4: Duplicate Prevention

**Scenario:** You need to ensure that duplicate messages are automatically detected and dropped within a 10-minute window.

**Question:** What is the minimum tier required?

**Answer:** **Standard**

**Reasoning:**
- ❌ Basic doesn't support duplicate detection
- ✅ Standard supports duplicate detection
- ✅ Premium also supports (but more expensive)
- Can configure detection time window up to 7 days

### Question 5: Predictable Performance

**Scenario:** Your high-volume trading application requires consistent sub-10ms latency for message processing and cannot tolerate performance variability.

**Question:** Which tier should you use?

**Answer:** **Premium**

**Reasoning:**
- ✅ Premium provides dedicated resources (Messaging Units)
- ✅ Predictable, low latency (<10ms P99)
- ❌ Basic and Standard use shared resources (variable performance)
- ✅ Premium offers 99.95% SLA vs 99.9% for Standard

## Best Practices

### General Best Practices

1. **Start with Standard for Production**
   - Use Basic only for dev/test
   - Standard provides essential features and SLA
   - Upgrade to Premium when needed

2. **Use Topics for Pub/Sub**
   ```csharp
   // Prefer topics over multiple queues for broadcast
   var sender = client.CreateSender("order-events");
   await sender.SendMessageAsync(new ServiceBusMessage("Order created"));
   
   // Multiple subscribers automatically receive
   ```

3. **Enable Sessions for Ordering**
   ```csharp
   // Use sessions when message order matters
   var message = new ServiceBusMessage("Step 1")
   {
       SessionId = "workflow-123" // Groups related messages
   };
   ```

4. **Implement Retry Logic**
   ```csharp
   var clientOptions = new ServiceBusClientOptions
   {
       RetryOptions = new ServiceBusRetryOptions
       {
           MaxRetries = 3,
           Delay = TimeSpan.FromSeconds(1),
           MaxDelay = TimeSpan.FromSeconds(30),
           Mode = ServiceBusRetryMode.Exponential
       }
   };
   ```

### Premium Tier Best Practices

1. **Right-size Messaging Units**
   - Start with 1 MU
   - Monitor throughput and latency
   - Scale up as needed

2. **Use Private Endpoints**
   ```bash
   # Secure premium namespace
   az network private-endpoint create \
     --name sb-pe \
     --vnet-name myVNet \
     --subnet privateSubnet \
     --private-connection-resource-id $(az servicebus namespace show --query id -o tsv)
   ```

3. **Enable Zone Redundancy**
   ```bash
   # For high availability
   az servicebus namespace create \
     --sku Premium \
     --zone-redundant true
   ```

4. **Use Large Messages Efficiently**
   ```csharp
   // Take advantage of 1 MB limit
   var largePayload = CompressData(originalData);
   var message = new ServiceBusMessage(largePayload);
   await sender.SendMessageAsync(message);
   ```

5. **Implement Customer-Managed Keys**
   ```bash
   # For compliance requirements
   az servicebus namespace encryption create \
     --encryption-config key-name=mykey key-vault-uri=https://...
   ```

### Cost Optimization

1. **Batch Messages**
   ```csharp
   // Reduce operation count
   var batch = await sender.CreateMessageBatchAsync();
   foreach (var msg in messages)
   {
       batch.TryAddMessage(msg);
   }
   await sender.SendMessagesAsync(batch);
   ```

2. **Use Prefetch**
   ```csharp
   // Reduce round trips
   var receiverOptions = new ServiceBusReceiverOptions
   {
       PrefetchCount = 100
   };
   var receiver = client.CreateReceiver("myqueue", receiverOptions);
   ```

3. **Clean Up Entities**
   ```bash
   # Remove unused queues/topics
   az servicebus queue delete --name unusedqueue
   az servicebus topic delete --name unusedtopic
   ```

4. **Monitor and Optimize**
   ```bash
   # Check namespace metrics
   az monitor metrics list \
     --resource $(az servicebus namespace show --query id -o tsv) \
     --metric IncomingMessages OutgoingMessages
   ```

## References

- [Service Bus pricing tiers](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-premium-messaging)
- [Service Bus pricing](https://azure.microsoft.com/en-us/pricing/details/service-bus/)
- [Azure Service Bus quotas and limits](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-quotas)
- [Migrate to Premium tier](https://learn.microsoft.com/en-us/azure/service-bus-messaging/migrate-to-premium-messaging)
- [Private endpoints for Service Bus](https://learn.microsoft.com/en-us/azure/service-bus-messaging/private-link-service)
- [Service Bus geo-disaster recovery](https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-geo-dr)
