# Azure Event Hubs Service Tiers

## Table of Contents

- [Overview](#overview)
- [Service Tiers Comparison](#service-tiers-comparison)
- [Basic Tier](#basic-tier)
- [Standard Tier](#standard-tier)
- [Premium Tier](#premium-tier)
- [Dedicated Tier](#dedicated-tier)
- [Throughput Units vs Processing Units vs Capacity Units](#throughput-units-vs-processing-units-vs-capacity-units)
- [Detailed Feature Comparison](#detailed-feature-comparison)
- [Performance Characteristics](#performance-characteristics)
- [Choosing the Right Tier](#choosing-the-right-tier)
- [Pricing Considerations](#pricing-considerations)
- [Migration Between Tiers](#migration-between-tiers)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Event Hubs offers four pricing tiers: **Basic**, **Standard**, **Premium**, and **Dedicated**. Each tier is designed for different event streaming scenarios with varying throughput capabilities, features, and pricing models. The tier determines the ingress/egress limits, retention period, and advanced features available.

## Service Tiers Comparison

| Feature | Basic | Standard | Premium | Dedicated |
|---------|-------|----------|---------|-----------|
| **Throughput Model** | TUs | TUs | PUs | CUs |
| **Max Throughput Units (TUs)** | 20 | 20 (40 with support) | N/A | N/A |
| **Processing Units (PUs)** | ❌ | ❌ | 1-16 | N/A |
| **Capacity Units (CUs)** | ❌ | ❌ | ❌ | 1-20+ |
| **Ingress per TU** | 1 MB/s or 1000 events/s | 1 MB/s or 1000 events/s | N/A | N/A |
| **Egress per TU** | 2 MB/s or 4096 events/s | 2 MB/s or 4096 events/s | N/A | N/A |
| **Max Retention** | 1 day | 7 days | 90 days | 90 days |
| **Partitions per Namespace** | 10 per TU (max 20) | 10 per TU (max 40) | Unlimited | Unlimited |
| **Max Event Size** | 256 KB | 256 KB (1 MB with Kafka) | 1 MB | 1 MB |
| **Consumer Groups** | 1 (default only) | 20 per Event Hub | 100 per Event Hub | 1000 per Event Hub |
| **Capture to Storage** | ❌ | ✅ | ✅ | ✅ |
| **Kafka Support** | ❌ | ✅ | ✅ | ✅ |
| **Schema Registry** | ❌ | ✅ | ✅ | ✅ |
| **Auto-Inflate** | ❌ | ✅ | ✅ (auto-scale) | ✅ |
| **VNet Integration** | ❌ | ✅ | ✅ | ✅ |
| **Private Endpoints** | ❌ | ❌ | ✅ | ✅ |
| **Availability Zones** | ❌ | ❌ | ✅ | ✅ |
| **Customer-Managed Keys** | ❌ | ❌ | ✅ | ✅ |
| **Resource Type** | Shared | Shared | Isolated | Fully Dedicated |
| **SLA** | 99.9% | 99.9% | 99.95% | 99.99% |
| **Best For** | Dev/Test | Production | Enterprise | Very High-Scale |

## Basic Tier

### Characteristics

- **Entry-level tier** for development and testing
- **Throughput Units (TUs)** - Up to 20 TUs
- **1 day retention** only
- **Single consumer group** (default only)
- **Shared infrastructure**
- **No Kafka support**
- **No Capture feature**
- **256 KB event size**
- **99.9% SLA**

### Throughput Specifications

**Per TU:**
- **Ingress**: 1 MB/s or 1,000 events/s (whichever comes first)
- **Egress**: 2 MB/s or 4,096 events/s (whichever comes first)
- **Storage**: 84 GB (1 day × 1 MB/s × 24 hours)

**Maximum (20 TUs):**
- **Ingress**: 20 MB/s or 20,000 events/s
- **Egress**: 40 MB/s or 81,920 events/s

### When to Use

✅ **Use Basic tier when:**
- Development and testing environments
- Learning Event Hubs
- Low-volume event streaming
- Short-term data retention (1 day sufficient)
- Cost is primary concern
- No need for multiple consumer groups
- Simple event ingestion scenarios

❌ **Don't use Basic when:**
- Need Kafka protocol support
- Require Capture to storage
- Need multiple consumer groups
- Retention >1 day required
- Production workloads

### Code Example

```bash
# Create Basic tier namespace
az eventhubs namespace create \
  --name mybasicnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Basic \
  --capacity 1

# Create Event Hub
az eventhubs eventhub create \
  --namespace-name mybasicnamespace \
  --resource-group myResourceGroup \
  --name myeventhub \
  --partition-count 2 \
  --message-retention 1
```

**.NET Example:**
```csharp
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;

// Create producer client
var producerClient = new EventHubProducerClient(
    connectionString,
    eventHubName
);

// Send events
var eventBatch = await producerClient.CreateBatchAsync();
for (int i = 0; i < 100; i++)
{
    var eventData = new EventData($"Event {i}");
    if (!eventBatch.TryAdd(eventData))
    {
        await producerClient.SendAsync(eventBatch);
        eventBatch = await producerClient.CreateBatchAsync();
        eventBatch.TryAdd(eventData);
    }
}

if (eventBatch.Count > 0)
{
    await producerClient.SendAsync(eventBatch);
}
```

### Limitations

- ❌ **1 consumer group** only (default)
- ❌ **1 day retention** maximum
- ❌ **No Kafka** protocol support
- ❌ **No Capture** to storage
- ❌ **No Schema Registry**
- ❌ **No auto-inflate**
- ❌ **Limited partitions** (20 max)

### Cost Example

- **Base price**: ~$11/month per TU
- **Ingress**: Included in TU price
- **Egress**: First 84 GB/day free per TU
- Most cost-effective for learning and testing

## Standard Tier

### Characteristics

- **Production-ready tier** with full features
- **Throughput Units (TUs)** - Up to 20 TUs (40 with support request)
- **Up to 7 days retention**
- **20 consumer groups** per Event Hub
- **Kafka 1.0+ support**
- **Capture to Storage/Data Lake**
- **Auto-inflate** capability
- **VNet service endpoints**
- **Schema Registry**
- **99.9% SLA**

### Throughput Specifications

**Per TU:**
- **Ingress**: 1 MB/s or 1,000 events/s
- **Egress**: 2 MB/s or 4,096 events/s
- **Storage**: 588 GB (7 days × 1 MB/s × 24 hours)

**Maximum (20 TUs, expandable to 40):**
- **Ingress**: 20-40 MB/s
- **Egress**: 40-80 MB/s

### Advanced Features

#### 1. Kafka Support

```python
# Kafka producer configuration
from confluent_kafka import Producer

config = {
    'bootstrap.servers': 'mystandard namespace.servicebus.windows.net:9093',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': '$ConnectionString',
    'sasl.password': 'Endpoint=sb://...',
}

producer = Producer(config)
producer.produce('myeventhub', value='Hello from Kafka')
producer.flush()
```

#### 2. Capture to Storage

```bash
# Enable Capture
az eventhubs eventhub update \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name myeventhub \
  --enable-capture true \
  --capture-interval 300 \
  --capture-size-limit 314572800 \
  --destination-name EventHubArchive.AzureBlockBlob \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/mystorage \
  --blob-container mycapturecontainer \
  --archive-name-format '{Namespace}/{EventHub}/{PartitionId}/{Year}/{Month}/{Day}/{Hour}/{Minute}/{Second}'
```

**Capture Configuration:**
- **Time window**: 60-900 seconds
- **Size window**: 10-500 MB
- **Format**: Avro (default)
- **Destination**: Azure Storage or Data Lake

#### 3. Auto-Inflate

```bash
# Enable auto-inflate (automatically scale TUs)
az eventhubs namespace create \
  --name mystandardnamespace \
  --resource-group myResourceGroup \
  --sku Standard \
  --capacity 1 \
  --enable-auto-inflate true \
  --maximum-throughput-units 10
```

**Auto-inflate behavior:**
- Automatically increases TUs when traffic exceeds capacity
- Scales up to configured maximum
- Prevents throttling during traffic spikes
- Scales back down after traffic decreases

#### 4. Schema Registry

```csharp
using Azure.Data.SchemaRegistry;
using Azure.Identity;
using Microsoft.Azure.Data.SchemaRegistry.ApacheAvro;

// Create schema registry client
var schemaRegistryClient = new SchemaRegistryClient(
    fullyQualifiedNamespace: "mystandard namespace.servicebus.windows.net",
    credential: new DefaultAzureCredential()
);

// Create serializer
var serializer = new SchemaRegistryAvroSerializer(
    schemaRegistryClient,
    groupName: "myschemagroup"
);

// Serialize with schema
var order = new Order { Id = "123", Amount = 99.99 };
BinaryData serializedData = await serializer.SerializeAsync(order);

// Send to Event Hub
var eventData = new EventData(serializedData);
await producerClient.SendAsync(new[] { eventData });
```

### When to Use

✅ **Use Standard tier when:**
- Production event streaming applications
- Need Kafka protocol compatibility
- Require multiple consumer groups
- Need Capture for data lake integration
- Retention between 1-7 days required
- Auto-scaling desired (auto-inflate)
- Integration with existing Kafka applications
- Schema evolution management needed

### Complete Example: Standard Tier Setup

```bash
# Create Standard namespace with auto-inflate
az eventhubs namespace create \
  --name mystandardnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard \
  --capacity 2 \
  --enable-auto-inflate true \
  --maximum-throughput-units 10

# Create Event Hub with Capture
az eventhubs eventhub create \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --name orders \
  --partition-count 4 \
  --message-retention 3 \
  --enable-capture true \
  --capture-interval 300 \
  --capture-size-limit 314572800 \
  --destination-name EventHubArchive.AzureBlockBlob \
  --storage-account /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/mystorage \
  --blob-container eventhubs-capture

# Create consumer groups
az eventhubs eventhub consumer-group create \
  --namespace-name mystandardnamespace \
  --eventhub-name orders \
  --name inventory-processor

az eventhubs eventhub consumer-group create \
  --namespace-name mystandardnamespace \
  --eventhub-name orders \
  --name analytics-processor

# Enable VNet service endpoint
az eventhubs namespace network-rule-set update \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --default-action Deny

az eventhubs namespace network-rule-set add \
  --namespace-name mystandardnamespace \
  --resource-group myResourceGroup \
  --subnet /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/myVNet/subnets/mySubnet
```

### Cost Example

- **Base price**: ~$22/month per TU
- **Ingress**: Included
- **Capture**: $0.10 per GB captured
- **Egress**: First 84 GB/day free per TU, then $0.028/GB
- **Schema Registry**: $0.04 per million operations

## Premium Tier

### Characteristics

- **Enterprise-grade tier** with dedicated capacity
- **Processing Units (PUs)** - 1-16 PUs
- **Up to 90 days retention**
- **100 consumer groups** per Event Hub
- **1 MB event size**
- **Dedicated CPU and memory** (isolated)
- **Predictable performance**
- **Auto-scaling**
- **Private endpoints**
- **Availability zones**
- **Customer-managed keys**
- **99.95% SLA**

### Processing Units (PUs)

Premium tier uses **Processing Units** instead of Throughput Units:

- **1 PU** ≈ **11-13 TUs** equivalent capacity
- **Dedicated resources** per PU
- **Auto-scales** within configured range
- **Predictable latency**

**Capacity per PU:**
- **Ingress**: ~11-13 MB/s
- **Egress**: ~22-26 MB/s
- **Concurrent connections**: Thousands
- **Storage**: Up to 10 TB per namespace

```bash
# Create Premium namespace
az eventhubs namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Premium \
  --capacity 1 \
  --zone-redundant true
```

### Premium Features

#### 1. Large Event Size (1 MB)

```csharp
// Send 1 MB event (Premium only)
var largePayload = new byte[1 * 1024 * 1024]; // 1 MB
var eventData = new EventData(largePayload);
await producerClient.SendAsync(new[] { eventData });
```

#### 2. Extended Retention (90 days)

```bash
# Configure 90-day retention
az eventhubs eventhub create \
  --namespace-name mypremiumnamespace \
  --resource-group myResourceGroup \
  --name myeventhub \
  --partition-count 8 \
  --message-retention 90
```

#### 3. Private Endpoints

```bash
# Create private endpoint
az network private-endpoint create \
  --name eh-private-endpoint \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet privateSubnet \
  --private-connection-resource-id $(az eventhubs namespace show --name mypremiumnamespace --resource-group myResourceGroup --query id -o tsv) \
  --group-id namespace \
  --connection-name ehConnection

# Disable public access
az eventhubs namespace update \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --public-network-access Disabled
```

#### 4. Availability Zones

```bash
# Zone redundancy enabled by default in Premium
az eventhubs namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 2 \
  --zone-redundant true
```

**Benefits:**
- Automatic replication across 3 availability zones
- Protection against datacenter failures
- No additional configuration needed

#### 5. Customer-Managed Keys (CMK)

```bash
# Enable encryption with customer-managed key
az eventhubs namespace encryption create \
  --namespace-name mypremiumnamespace \
  --resource-group myResourceGroup \
  --encryption-config key-name=mykey \
    key-vault-uri=https://mykeyvault.vault.azure.net \
    user-assigned-identity=/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/myidentity
```

#### 6. Auto-Scaling

```bash
# Premium auto-scales between min and max PUs
az eventhubs namespace create \
  --name mypremiumnamespace \
  --resource-group myResourceGroup \
  --sku Premium \
  --capacity 1 \
  --enable-auto-inflate true \
  --maximum-throughput-units 16
```

**Auto-scaling behavior:**
- Scales up when throughput exceeds current capacity
- Scales down when traffic decreases
- No manual intervention required
- Charged for actual PUs used

### When to Use

✅ **Use Premium tier when:**
- Enterprise production workloads
- Need predictable, low-latency performance
- Large event sizes (>256 KB)
- Extended retention (>7 days, up to 90)
- VNet integration and private endpoints required
- Compliance requirements (CMK, network isolation)
- High availability (zone redundancy)
- Many consumer groups (up to 100)
- Mission-critical applications
- High-throughput scenarios

### Cost Example

- **1 PU**: ~$1,290/month
- **2 PU**: ~$2,580/month
- **4 PU**: ~$5,160/month
- **8 PU**: ~$10,320/month
- **16 PU**: ~$20,640/month
- **Ingress/Egress**: Included
- **Storage**: Included (up to 10 TB)

## Dedicated Tier

### Characteristics

- **Fully dedicated cluster** for single tenant
- **Capacity Units (CUs)** - 1-20+ CUs
- **Maximum throughput** and isolation
- **Up to 90 days retention**
- **1,000 consumer groups** per Event Hub
- **Unlimited namespaces** per cluster
- **Unlimited Event Hubs** per namespace
- **Complete resource isolation**
- **Fixed monthly cost** regardless of usage
- **99.99% SLA**
- **Best performance** and scale

### Capacity Units (CUs)

Dedicated tier uses **Capacity Units**:

- **1 CU** ≈ **100-200 TUs** equivalent capacity
- **Fully dedicated infrastructure**
- **No noisy neighbor** issues
- **Predictable performance** at scale

**Capacity per CU (approximate):**
- **Ingress**: 100-200 MB/s
- **Egress**: 200-400 MB/s
- **Events**: 100K-200K events/s
- **Storage**: Multiple TBs

```bash
# Create Dedicated cluster (requires support request)
# Note: Dedicated clusters require minimum 1 CU commitment
az eventhubs cluster create \
  --name mydedicatedcluster \
  --resource-group myResourceGroup \
  --location eastus \
  --capacity 1

# Create namespace in dedicated cluster
az eventhubs namespace create \
  --name mynamespace \
  --resource-group myResourceGroup \
  --cluster-name mydedicatedcluster \
  --location eastus
```

### Dedicated Features

#### 1. Bring Your Own Key (BYOK) - Cluster Level

```bash
# Enable CMK at cluster level (all namespaces encrypted)
az eventhubs cluster update \
  --name mydedicatedcluster \
  --resource-group myResourceGroup \
  --encryption-config key-name=clusterkey \
    key-vault-uri=https://mykeyvault.vault.azure.net
```

#### 2. Multiple Namespaces

```bash
# Create multiple namespaces in same cluster (no additional cost)
az eventhubs namespace create --name namespace1 --cluster-name mydedicatedcluster
az eventhubs namespace create --name namespace2 --cluster-name mydedicatedcluster
az eventhubs namespace create --name namespace3 --cluster-name mydedicatedcluster
```

#### 3. Unlimited Event Hubs

```bash
# No limit on Event Hubs per namespace
for i in {1..100}; do
  az eventhubs eventhub create \
    --namespace-name namespace1 \
    --name eventhub$i \
    --partition-count 32
done
```

### When to Use

✅ **Use Dedicated tier when:**
- Very high-scale event streaming (>1 TB/day)
- Need complete resource isolation
- Multiple production workloads requiring separation
- Predictable, fixed monthly costs preferred
- Highest performance requirements
- Compliance requirements for dedicated infrastructure
- Need >16 PUs worth of capacity
- Mission-critical, large-scale applications
- Multi-tenant SaaS platforms

### Cost Example

- **1 CU**: ~$8,000/month (fixed)
- **2 CU**: ~$16,000/month
- **Scaling**: Can scale CUs up/down
- **All features included**: Ingress, egress, storage, features
- **Cost-effective** at very high volumes

**Cost comparison at high scale:**
```
Scenario: 100 TB/month ingress

Standard (20 TUs): ~$440 + egress charges = ~$3,000/month
Premium (16 PUs): ~$20,640/month
Dedicated (1 CU): ~$8,000/month ✓ Most cost-effective
```

## Throughput Units vs Processing Units vs Capacity Units

### Comparison Table

| Metric | TU (Basic/Standard) | PU (Premium) | CU (Dedicated) |
|--------|-------------------|--------------|----------------|
| **Ingress** | 1 MB/s | ~11-13 MB/s | ~100-200 MB/s |
| **Egress** | 2 MB/s | ~22-26 MB/s | ~200-400 MB/s |
| **Events/sec** | 1,000 in / 4,096 out | ~11K-13K in | ~100K-200K in |
| **Resource Type** | Shared | Isolated | Fully Dedicated |
| **Max Units** | 20-40 | 16 | 20+ |
| **Auto-scale** | Yes (Standard) | Yes | N/A (fixed capacity) |
| **Cost Model** | Per TU | Per PU | Per CU (flat fee) |

### Capacity Equivalents

```
1 CU ≈ 8-16 PUs ≈ 100-200 TUs

Example:
- 20 TUs (Standard max) = ~1.5-2 PUs = ~0.15-0.20 CUs
- 8 PUs (Premium) = ~100 TUs = ~0.5-0.8 CUs
- 1 CU (Dedicated) = ~100-200 TUs = ~8-16 PUs
```

## Detailed Feature Comparison

### Event Processing

| Feature | Basic | Standard | Premium | Dedicated |
|---------|-------|----------|---------|-----------|
| **Max Event Size** | 256 KB | 256 KB (1 MB Kafka) | 1 MB | 1 MB |
| **Batch Size** | 256 KB | 256 KB | 1 MB | 1 MB |
| **Partitions per Hub** | 32 | 32 | 100 | 100 |
| **AMQP Protocol** | ✅ | ✅ | ✅ | ✅ |
| **Kafka Protocol** | ❌ | ✅ | ✅ | ✅ |
| **HTTP Protocol** | ✅ | ✅ | ✅ | ✅ |

### Data Management

| Feature | Basic | Standard | Premium | Dedicated |
|---------|-------|----------|---------|-----------|
| **Retention Period** | 1 day | 1-7 days | 1-90 days | 1-90 days |
| **Capture to Storage** | ❌ | ✅ | ✅ | ✅ |
| **Schema Registry** | ❌ | ✅ | ✅ | ✅ |
| **Geo-DR** | ❌ | ✅ | ✅ | ✅ |

### Security & Network

| Feature | Basic | Standard | Premium | Dedicated |
|---------|-------|----------|---------|-----------|
| **VNet Service Endpoints** | ❌ | ✅ | ✅ | ✅ |
| **Private Endpoints** | ❌ | ❌ | ✅ | ✅ |
| **IP Filtering** | ❌ | ✅ | ✅ | ✅ |
| **Managed Identity** | ✅ | ✅ | ✅ | ✅ |
| **Customer-Managed Keys** | ❌ | ❌ | ✅ | ✅ |
| **Availability Zones** | ❌ | ❌ | ✅ | ✅ |

## Performance Characteristics

### Throughput Comparison

```
Dedicated (1 CU):    ████████████████████████████████ ~150 MB/s ingress
Premium (16 PU):     ████████████████████████████████ ~200 MB/s ingress
Premium (8 PU):      ████████████████ ~100 MB/s ingress
Premium (1 PU):      ██ ~12 MB/s ingress
Standard (20 TU):    ████ ~20 MB/s ingress
Standard (1 TU):     █ ~1 MB/s ingress
Basic (20 TU):       ████ ~20 MB/s ingress
Basic (1 TU):        █ ~1 MB/s ingress
```

### Latency Characteristics

**End-to-end latency (publish + consume):**

| Tier | P50 | P95 | P99 |
|------|-----|-----|-----|
| **Basic** | 10ms | 50ms | 100ms |
| **Standard** | 8ms | 30ms | 60ms |
| **Premium** | 3ms | 8ms | 15ms |
| **Dedicated** | 2ms | 5ms | 10ms |

## Choosing the Right Tier

### Decision Tree

```
Start
│
├─ Need >100 MB/s sustained throughput?
│  └─ YES → Dedicated
│  └─ NO → Continue
│
├─ Need private endpoints or >256 KB events?
│  └─ YES → Premium or Dedicated
│  └─ NO → Continue
│
├─ Need Kafka support or Capture?
│  └─ YES → Standard, Premium, or Dedicated
│  └─ NO → Continue
│
├─ Production workload?
│  └─ YES → Standard (minimum)
│  └─ NO → Continue
│
└─ Development/testing or simple scenarios?
   └─ YES → Basic
```

### Selection by Use Case

| Use Case | Recommended Tier | Reasoning |
|----------|------------------|-----------|
| **Learning Event Hubs** | Basic | Low cost, API compatible |
| **Dev/Test** | Basic or Standard | Based on feature needs |
| **IoT Telemetry** | Standard or Premium | Capture, Kafka, scale |
| **Click stream Analytics** | Standard or Premium | High volume, retention |
| **Financial Transactions** | Premium or Dedicated | Low latency, CMK, isolation |
| **Kafka Migration** | Standard or Premium | Kafka compatibility |
| **Real-time Analytics** | Premium | Performance, features |
| **Multi-tenant SaaS** | Dedicated | Isolation, multiple namespaces |
| **Large Enterprise** | Dedicated | Scale, predictable cost |

## Pricing Considerations

### Cost Comparison Scenarios

**Scenario 1: Low Volume (1 GB/day)**

| Tier | Monthly Cost |
|------|-------------|
| Basic (1 TU) | ~$11 |
| Standard (1 TU) | ~$22 |
| Premium (1 PU) | ~$1,290 |
| Dedicated (1 CU) | ~$8,000 |

**Winner**: Basic or Standard

**Scenario 2: Medium Volume (100 GB/day)**

| Tier | Monthly Cost |
|------|-------------|
| Basic (20 TU) | ~$220 |
| Standard (10 TU) | ~$220 + egress |
| Premium (1 PU) | ~$1,290 |
| Dedicated (1 CU) | ~$8,000 |

**Winner**: Standard

**Scenario 3: High Volume (5 TB/day)**

| Tier | Monthly Cost |
|------|-------------|
| Standard (40 TU) | ~$880 + high egress |
| Premium (8 PU) | ~$10,320 |
| Dedicated (1 CU) | ~$8,000 ✓ |

**Winner**: Dedicated

### Cost Optimization Strategies

1. **Use Auto-Inflate (Standard)**
   ```bash
   # Scale TUs automatically
   az eventhubs namespace create \
     --enable-auto-inflate true \
     --maximum-throughput-units 10
   ```

2. **Batch Events**
   ```csharp
   // Reduce operations by batching
   var batch = await producerClient.CreateBatchAsync();
   foreach (var evt in events)
   {
       batch.TryAdd(new EventData(evt));
   }
   await producerClient.SendAsync(batch);
   ```

3. **Optimize Retention**
   ```bash
   # Don't over-retain
   az eventhubs eventhub create \
     --message-retention 3  # Only keep 3 days if sufficient
   ```

4. **Right-size Partitions**
   ```bash
   # Balance parallelism vs cost
   az eventhubs eventhub create \
     --partition-count 4  # Not always 32
   ```

## Migration Between Tiers

### Upgrade Paths

**Basic → Standard:**
```bash
# Direct upgrade supported
az eventhubs namespace update \
  --name mybasicnamespace \
  --resource-group myResourceGroup \
  --sku Standard \
  --capacity 2
```

**Standard → Premium:**
```bash
# Requires migration (different namespace)
# 1. Create Premium namespace
az eventhubs namespace create \
  --name mypremiumnamespace \
  --sku Premium \
  --capacity 1

# 2. Migrate Event Hubs and consumer groups
# 3. Update application endpoints
# 4. Cutover traffic
```

**Premium → Dedicated:**
```bash
# Requires cluster creation and migration
# 1. Create Dedicated cluster
az eventhubs cluster create --name mycluster --capacity 1

# 2. Create namespace in cluster
az eventhubs namespace create \
  --name mynamespace \
  --cluster-name mycluster

# 3. Migrate data and cutover
```

### Migration Considerations

- ✅ Basic ↔ Standard: Direct upgrade/downgrade
- ⚠️ Standard → Premium: Requires new namespace
- ⚠️ Premium → Dedicated: Requires cluster + migration
- ❌ No downtime migration for Premium/Dedicated
- ⚠️ Connection string changes required

## Exam Questions and Scenarios

### Question 1: Kafka Support

**Scenario:** Your team wants to migrate an existing Kafka application to Azure Event Hubs without changing application code.

**Question:** What is the minimum tier required?

**Answer:** **Standard**

**Reasoning:**
- ✅ Standard supports Kafka 1.0+ protocol
- ❌ Basic does not support Kafka
- ✅ Premium and Dedicated also support, but more expensive

### Question 2: Large Events

**Scenario:** Your application needs to send events that are 500 KB each.

**Question:** Which tier(s) support this requirement?

**Answer:** **Premium or Dedicated**

**Reasoning:**
- ❌ Basic: Maximum 256 KB
- ❌ Standard: Maximum 256 KB (except Kafka)
- ✅ Premium: Up to 1 MB
- ✅ Dedicated: Up to 1 MB

### Question 3: Extended Retention

**Scenario:** You need to retain events for 30 days for compliance purposes.

**Question:** Which tier is required?

**Answer:** **Premium or Dedicated**

**Reasoning:**
- ❌ Basic: Maximum 1 day retention
- ❌ Standard: Maximum 7 days retention
- ✅ Premium: Up to 90 days retention
- ✅ Dedicated: Up to 90 days retention

### Question 4: Network Isolation

**Scenario:** Security policy requires Event Hubs to be accessible only from private network, not public internet.

**Question:** Which tier provides this capability?

**Answer:** **Premium or Dedicated**

**Reasoning:**
- ❌ Basic: No private endpoints
- ❌ Standard: Only service endpoints (not fully private)
- ✅ Premium: Private endpoints supported
- ✅ Dedicated: Private endpoints supported

### Question 5: Automatic Throughput Scaling

**Scenario:** A company processes streaming data using Azure Event Hubs. During peak hours, incoming data rate exceeds the allocated throughput units, causing throttling. The solution must automatically scale throughput units based on demand between 2 and 20 units.

**Question:** What should you configure?

**Answer:** **Enable Auto-inflate with maximum throughput units set to 20**

**Reasoning:**
- ✅ **Auto-inflate** automatically increases throughput units when the ingress or egress limits are exceeded
- ✅ Setting the maximum to 20 ensures scaling stays within the required range
- ✅ The minimum of 2 is maintained by initial configuration (capacity setting)
- ✅ Auto-inflate is a built-in feature for Standard tier that provides immediate, automatic scaling

**Why other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| Implement event-driven scaling using Azure Functions | Requires custom implementation and introduces latency in scaling decisions. Auto-inflate provides immediate, automatic scaling without custom code. |
| Configure Azure Event Hubs Premium with processing units auto-scaling | Premium tier uses processing units (PUs), not throughput units. The requirement specifically mentions throughput units, indicating Standard tier with Auto-inflate. |
| Configure autoscale rules in Azure Monitor with throughput unit metrics | Event Hubs doesn't support autoscale rules for throughput units through Azure Monitor. Auto-inflate is the built-in scaling feature for throughput units. |

**Configuration Example:**
```bash
# Create namespace with initial 2 TUs and auto-inflate up to 20 TUs
az eventhubs namespace create \
  --name mystreamingnamespace \
  --resource-group myResourceGroup \
  --location eastus \
  --sku Standard \
  --capacity 2 \
  --enable-auto-inflate true \
  --maximum-throughput-units 20
```

> **Exam Tip:** When you need automatic throughput scaling in Azure Event Hubs Standard tier, always use **Auto-inflate**. It's the built-in feature specifically designed for this purpose and doesn't require custom code or Azure Monitor integration.

### Question 6: Standard Tier Throughput Units Scaling Beyond 20 TUs

**Scenario:** You are developing a solution that uses Azure Event Hubs with the Standard tier. The namespace currently has 20 throughput units and needs to scale to 30 throughput units.

**Question:** What should you do?

**Answer:** **File a support ticket to request the increase**

**Reasoning:**
- ✅ **Standard-tier namespaces can have up to 20 throughput units through self-serve**, but require filing a support ticket to increase beyond 20 TUs up to the **maximum of 40 TUs**
- Self-serve experience (Azure portal, CLI, PowerShell) only allows up to 20 TUs for Standard tier
- Microsoft must manually approve and enable the increased limit

**Why other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| Enable Auto-inflate to scale automatically | Auto-inflate can automatically scale throughput units but is still limited to the **20 TU self-serve maximum** without a support ticket. It cannot exceed the account's configured limit. |
| Use the portal to increase to 30 TUs directly | The self-serve experience (portal, CLI, PowerShell) only allows up to **20 TUs** for Standard tier; increasing beyond this requires a support ticket. |
| Upgrade to the Dedicated tier | While Dedicated tier supports more capacity, filing a support ticket is the **appropriate and cost-effective solution** for Standard tier scaling beyond 20 TUs. Upgrading to Dedicated is unnecessary and significantly more expensive. |

**Key Limits Summary:**

| Tier | Self-Serve TU Limit | Maximum TU Limit (with Support) |
|------|--------------------|---------------------------------|
| Basic | 20 TUs | 20 TUs |
| Standard | 20 TUs | 40 TUs |

> **Exam Tip:** Remember the **20 TU self-serve limit** for Standard tier. If you need more than 20 TUs (up to 40), you must **file a support ticket**. Auto-inflate helps with automatic scaling but doesn't bypass this limit.

> **Important:** Auto-inflate's maximum throughput units setting is also limited to your account's throughput unit limit. If your account limit is 20 TUs, auto-inflate can only scale up to 20 TUs.

## Best Practices

### General Best Practices

1. **Choose Appropriate Partition Count**
   ```bash
   # Balance parallelism vs cost
   # Rule: partitions = max concurrent consumers
   az eventhubs eventhub create --partition-count 8
   ```

2. **Use Batching**
   ```csharp
   // Improve throughput and reduce cost
   var batch = await producerClient.CreateBatchAsync();
   foreach (var evt in events.Take(100))
   {
       batch.TryAdd(new EventData(evt));
   }
   await producerClient.SendAsync(batch);
   ```

3. **Implement Checkpointing**
   ```csharp
   // Track progress to avoid reprocessing
   var processor = new EventProcessorClient(
       blobContainerClient,
       consumerGroup,
       connectionString,
       eventHubName
   );
   
   processor.ProcessEventAsync += async (args) =>
   {
       // Process event
       await ProcessEventAsync(args.Data);
       
       // Checkpoint
       await args.UpdateCheckpointAsync();
   };
   ```

4. **Monitor Throttling**
   ```bash
   # Check for throttling metrics
   az monitor metrics list \
     --resource $(az eventhubs namespace show --query id -o tsv) \
     --metric ThrottledRequests IncomingMessages
   ```

### Premium/Dedicated Best Practices

1. **Use Private Endpoints**
   ```bash
   # Secure Premium/Dedicated namespaces
   az network private-endpoint create \
     --name eh-pe \
     --vnet-name myVNet \
     --subnet privateSubnet
   ```

2. **Enable Zone Redundancy**
   ```bash
   # For high availability
   az eventhubs namespace create \
     --sku Premium \
     --zone-redundant true
   ```

3. **Implement CMK**
   ```bash
   # For compliance
   az eventhubs namespace encryption create \
     --encryption-config key-name=mykey
   ```

4. **Monitor Processing Units**
   ```bash
   # Optimize PU usage
   az monitor metrics list \
     --metric CaptureBacklog IncomingBytes OutgoingBytes
   ```

## References

- [Event Hubs pricing tiers](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-premium-overview)
- [Event Hubs pricing](https://azure.microsoft.com/en-us/pricing/details/event-hubs/)
- [Event Hubs quotas and limits](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-quotas)
- [Event Hubs Dedicated](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-dedicated-overview)
- [Kafka on Event Hubs](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview)
- [Event Hubs Capture](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-capture-overview)
