# Azure Event Hubs Detailed Reference
## Table of Contents

- [1. Overview](#1-overview)
- [2. Core Concepts](#2-core-concepts)
  - [Namespace](#namespace)
  - [Partitions](#partitions)
  - [Consumer Groups](#consumer-groups)
  - [Throughput Units (TUs) / Processing Units (PUs)](#throughput-units-tus-processing-units-pus)
- [3. Key Features](#3-key-features)
  - [Event Capture](#event-capture)
    - [Cross-Subscription Capture with Managed Identity](#cross-subscription-capture-with-managed-identity)
  - [Apache Kafka Compatibility](#apache-kafka-compatibility)
  - [Schema Registry Considerations](#schema-registry-considerations)
  - [Checkpointing](#checkpointing)
  - [Processing Events with Multiple Instances (Partition Distribution)](#processing-events-with-multiple-instances-partition-distribution)
- [4. Data Integration Model: Push-Pull](#4-data-integration-model-push-pull)
  - [Publisher Side (Push)](#publisher-side-push)
  - [Consumer Side (Pull)](#consumer-side-pull)
  - [Benefits](#benefits)
  - [Considerations](#considerations)
- [5. Architecture & Flow](#5-architecture-flow)
- [6. Access Control (Security)](#6-access-control-security)
  - [Authentication](#authentication)
  - [Application Identity Strategy](#application-identity-strategy)
  - [Authorization](#authorization)
    - [Azure RBAC (Role-Based Access Control)](#azure-rbac-role-based-access-control)
    - [SAS Policies](#sas-policies)
- [7. Best Practices](#7-best-practices)


## 1. Overview
Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second. Data sent to an event hub can be transformed and stored using any real-time analytics provider or batching/storage adapters.

- **Primary Use Case:** Telemetry ingestion, log aggregation, real-time analytics.
- **Protocol Support:** AMQP, HTTPS, Apache Kafka.

## 2. Core Concepts

### Event Hubs Hierarchy

```
Namespace (Container)
    └── Event Hub Instance (Entity)
            ├── Partitions
            └── Consumer Groups
```

| Term | What It Is | Example |
|------|-----------|---------|
| **Namespace** | A management container that holds one or more Event Hubs. Provides a unique FQDN. | `mycompany-eventhubs` → `mycompany.servicebus.windows.net` |
| **Event Hub Instance** | An individual event stream/channel within a namespace. This is the actual entity where events are sent/received. | `telemetry-hub`, `orders-hub`, `logs-hub` |
| **Partition** | Ordered sequences of events within an Event Hub for parallelism. | Partition 0, Partition 1, etc. |
| **Consumer Group** | A view (state, position, offset) of an Event Hub for independent consumption. | `$Default`, `analytics-group` |

> **Database Analogy:** Think of it like a database system:
> - **Namespace** = Database Server
> - **Event Hub Instance** = Individual Database/Table
> - **Partition** = Table partitions/shards

> **Kafka Analogy:** If you're coming from Apache Kafka:
> - **Namespace** = Kafka Cluster
> - **Event Hub Instance** = Kafka Topic
> - **Partition** = Kafka Partition
> - **Consumer Group** = Kafka Consumer Group

### Namespace
A management container for Event Hubs. It provides a unique FQDN and serves as a container for multiple Event Hub instances.

### Event Hub Instance
An individual event stream within a namespace. This is the entity where producers send events and consumers read from. Each Event Hub instance can have multiple partitions and consumer groups.

- **Naming:** Must be unique within a namespace.
- **Kafka Equivalent:** Analogous to a Kafka topic.
- **Authorization:** Can be secured independently from other Event Hubs in the same namespace.

### Partitions
- **Definition:** Ordered sequences of events that are held in an Event Hub.
- **Function:** Partitions are the mechanism for parallelism. As data volume grows, you increase partitions to handle higher throughput.
- **Retention:** Events are retained for a configurable period (1-90 days depending on tier) and cannot be deleted explicitly; they expire.

### Consumer Groups
- **Definition:** A view (state, position, or offset) of an entire event hub.
- **Function:** Enable consuming applications to each have a separate view of the event stream. They read the stream independently at their own pace and with their own offsets.

### Throughput Units (TUs) / Processing Units (PUs)
- **Standard Tier:** Uses TUs. 1 TU = 1 MB/s or 1000 events/s ingress, 2 MB/s or 4096 events/s egress.
- **Premium/Dedicated:** Uses PUs or CUs for isolated resources and predictable latency.

## 3. Key Features

### Event Capture
Automatically capture the streaming data in Azure Blob Storage or Azure Data Lake Storage Gen 2.
- **Format:** Apache Avro (default and only format supported through Azure portal configuration).
- **Trigger:** Time-based (e.g., every 5 mins) or Size-based (e.g., every 100 MB).
- **Tier Availability:** Standard, Premium, and Dedicated tiers (not available in Basic tier).
- **Cost:** No additional administrative costs to run; scales automatically with your throughput.

#### Why Event Hubs Capture vs. Alternatives

| Option | Purpose | Best For |
|--------|---------|----------|
| **Event Hubs Capture** ✅ | Automatically stores streaming data in Blob Storage/ADLS in Avro format | Long-term analysis, no additional cost, automatic scaling |
| **Checkpoint Store with Blob Storage** ❌ | Tracks consumer progress (offsets) | Consumer state management, NOT for storing event data |
| **Stream Analytics with Blob Output** ❌ | Separate service for stream processing with storage output | Complex transformations, but requires additional configuration and cost |
| **Event Hubs Archive** ❌ | Does not exist | N/A - This feature doesn't exist in Event Hubs |

> **Exam Tip:** When asked about automatically storing streaming data for long-term analysis in Azure Blob Storage with Apache Avro format, the answer is **Event Hubs Capture**. Don't confuse it with:
> - **Checkpoint stores** - These track consumer position/offsets, not actual event data
> - **Stream Analytics** - A separate paid service requiring additional setup
> - **Event Hubs Archive** - This feature does not exist; "Capture" is the correct term

#### Supported File Formats for Event Hubs Capture

| Format | Portal Configuration | Notes |
|--------|---------------------|-------|
| **Apache Avro** | ✅ Supported | Default and standard format. Provides a compact binary format with inline schema. |
| **JSON** | ❌ Not Supported | Not available for Event Hubs Capture configuration. |
| **CSV** | ❌ Not Supported | Not available for Event Hubs Capture configuration. |
| **Parquet** | ⚠️ Indirect Only | Only supported through Azure Stream Analytics integration using the no-code editor, not through direct Event Hubs Capture configuration in the portal. |

> **Exam Tip:** When configuring Event Hubs Capture through the Azure portal, **Apache Avro** is the only supported file format. It provides a compact binary format with an inline schema, making it efficient for streaming data capture. If you need Parquet format, you must use Azure Stream Analytics with the no-code editor instead of direct Event Hubs Capture.

#### Cross-Subscription Capture with Managed Identity

When configuring Event Hubs Capture to store data in a storage account that resides in a **different subscription** than the Event Hubs namespace, there are specific requirements to consider:

| Scenario | Requirement |
|----------|-------------|
| **Event Hubs in Subscription A, Storage in Subscription B** | Register the **Microsoft.EventHub Resource Provider** in Subscription B |

**Key Points:**

- **Resource Provider Registration (Required):** When capturing to a storage account in a different subscription, the `Microsoft.EventHub` Resource Provider must be registered in the subscription containing the storage account. This enables cross-subscription capture functionality.

- **Managed Identity Location:** The managed identity (user-assigned or system-assigned) can be created in **either subscription** and assigned appropriate permissions. It does **not** need to be in the same subscription as the storage account.

- **Zone Redundancy:** Not required for cross-subscription capture with managed identity. Zone redundancy is a high-availability feature within a region and is unrelated to cross-subscription scenarios.

- **Private Endpoints:** Not required for managed identity authentication in cross-subscription scenarios. Private endpoints are for network isolation, not authentication.

> **Exam Tip:** When Event Hubs Capture uses managed identity to write to a storage account in a different subscription, ensure the `Microsoft.EventHub` Resource Provider is registered in the target subscription (the one containing the storage account). This is the key requirement for cross-subscription capture to work.

### Apache Kafka Compatibility
Event Hubs provides an endpoint compatible with Kafka producer and consumer APIs. You can use existing Kafka applications without running your own Kafka cluster.
### Schema Registry Considerations
- **No built-in Confluent registry:** Event Hubs does not include a Confluent Schema Registry service. Schema registries are separate services and must be hosted/available to your clients.
- **Typically no code changes:** If your Kafka producers/consumers already use an external schema registry (e.g., Confluent, Apicurio) and standard Kafka serializers (Avro/Protobuf), you usually only need to update serializer configuration (registry URLs and auth) to point to the registry; your application code typically does not require changes.
- **Using Azure Schema Registry:** If you adopt Azure Schema Registry instead of your existing registry, you may need to switch to Azure-compatible serializer libraries or update serializer configuration; this can require minor code or dependency changes.
- **Network & auth:** Ensure any registry (Confluent or Azure) is reachable from your client environment and that client serializers are configured with the correct authentication and TLS settings.

### Checkpointing
Consumers store their position in the partition stream. If a worker fails, a new one picks up from the last checkpoint.

### Processing Events with Multiple Instances (Partition Distribution)

When processing events from an Event Hub with multiple partitions using Azure Functions or other consumers, you need to ensure proper partition distribution and single-instance processing per partition.

#### EventProcessorClient (Recommended Approach)

**EventProcessorClient** is the recommended way to process events from Event Hubs when you need:
- Automatic partition distribution among multiple instances
- Single-instance processing per partition guarantee
- Reliable checkpointing for progress tracking and failure handling

| Component | Purpose |
|-----------|---------|
| **EventProcessorClient** | Automatically distributes partitions among multiple consumer instances |
| **Consumer Group** | Provides isolated view of the event stream for a set of consumers |
| **Blob Storage Checkpoint Store** | Persists checkpoint data to track processing progress |

**How It Works:**
1. Multiple instances of your application use the same consumer group
2. EventProcessorClient automatically coordinates which instance processes which partition
3. Each partition is processed by **only one instance at a time**
4. Progress is checkpointed to blob storage, enabling recovery after failures
5. When instances are added or removed, partitions are automatically rebalanced

**Example Configuration (Azure Functions):**
```csharp
// Azure Functions automatically uses EventProcessorClient under the hood
// when using EventHubTrigger with proper configuration
[FunctionName("ProcessTelemetry")]
public async Task Run(
    [EventHubTrigger("telemetry-hub", 
     Connection = "EventHubConnection",
     ConsumerGroup = "telemetry-processors")] EventData[] events,
    ILogger log)
{
    foreach (var eventData in events)
    {
        // Process event
    }
    // Checkpointing is handled automatically
}
```

#### Alternative Approaches (Not Recommended for This Scenario)

| Approach | Why It's Not Ideal |
|----------|-------------------|
| **Multiple Consumer Groups (one function per group)** | Allows independent consumption of the same events but doesn't provide automatic partition distribution or ensure single-instance processing per partition |
| **Direct Receivers with Manual Partition Assignment** | Requires manual partition assignment and doesn't automatically handle instance failures or rebalancing when instances are added/removed |
| **EventHubTrigger with maxBatchSize=1** | Controls batch size for processing, not partition distribution; doesn't ensure partitions are distributed among multiple instances |

> **Exam Tip:** When you need to process Event Hub events using multiple Azure Functions instances while ensuring each partition is processed by only one instance at a time, use **EventProcessorClient with a consumer group and blob storage for checkpointing**. This combination provides automatic partition distribution, single-instance-per-partition guarantee, and reliable checkpoint-based recovery.

## 4. Data Integration Model: Push-Pull

Event Hubs follows a **push-pull** delivery model:

### Publisher Side (Push)
- **Producers actively push events** to Event Hubs.
- Events are sent via AMQP, HTTPS, or Kafka protocols.
- Producers send events to partitions (either explicitly or via partition key/round-robin).
- Events are immediately written to the partition and persisted.

### Consumer Side (Pull)
- **Consumers actively pull events** from Event Hubs partitions.
- Consumers read from specific partitions at their own pace.
- Each consumer group maintains its own offset (position) in the partition.
- Consumers control when and how fast they read data.

### Benefits
- **High throughput:** Multiple consumers can read from the same partition independently.
- **Replay capability:** Consumers can reset their offset and re-read historical data.
- **Backpressure handling:** Consumers control their read rate, preventing overload.
- **Scalability:** Add partitions and consumers independently.

### Considerations
- Consumers must implement polling logic and checkpoint management.
- Requires consumer-side state management (tracking offsets).
- More complex consumer implementation compared to push models.
- Network bandwidth consumed by continuous polling.

## 5. Architecture & Flow
```
[Producers] --> [Event Hub Namespace]
                    |
                    +--> [Event Hub A]
                          |--> [Partition 1] --+--> [Consumer Group A] --> [App Instance 1]
                          |--> [Partition 2] --|
                          |--> [Partition 3] --+--> [Consumer Group B] --> [Stream Analytics]
```

## 6. Access Control (Security)

### Authentication
Event Hubs supports two primary authentication mechanisms:

1. **Microsoft Entra ID (Recommended):**
   - Authenticate using Azure AD identities (users, groups, or managed identities).
   - Eliminates the need to store connection strings in code.
   - Supports OAuth 2.0.

2. **Shared Access Signatures (SAS):**
   - Uses cryptographic keys to generate tokens with specific permissions and expiry times.
   - Useful for clients that cannot use Entra ID.
   - Can be defined at the Namespace or Event Hub level.

### Application Identity Strategy
Applications connecting to Event Hubs need an identity to be authenticated and authorized.

1. **Managed Identities (Recommended for Azure-hosted apps):**
   - If your app runs on Azure (VM, App Service, AKS, Functions, Container Apps), enable a **System-Assigned** or **User-Assigned** Managed Identity.
   - **No App Registration needed:** The identity is managed by the Azure platform.
   - Grant RBAC roles (e.g., *Azure Event Hubs Data Receiver*) directly to the Managed Identity.
   - **Benefit:** No secrets to rotate or store in code.

2. **App Registrations (Service Principals) (For external/local apps):**
   - If your app runs outside Azure (on-prem, other clouds, or local dev), create an **App Registration** in Entra ID.
   - This creates a **Service Principal**.
   - You must manage a **Client Secret** or **Certificate**.
   - Grant RBAC roles to the Service Principal.
   - **Benefit:** Secure, role-based access for external applications.

### Authorization
Authorization determines what an authenticated principal can do.

#### Authorization Levels

Authorization in Event Hubs can be applied at multiple levels, with the **Event Hub (entity) level** being the most granular:

| Level | RBAC Support | SAS Policy Support | Description |
|-------|--------------|-------------------|-------------|
| **Resource Group** | ✅ Yes | ❌ No | Applies to all namespaces in the group |
| **Namespace** | ✅ Yes | ✅ Yes | Applies to all Event Hubs in the namespace |
| **Event Hub** | ✅ Yes | ✅ Yes | Applies to a specific Event Hub only |
| **Partition** | ❌ No | ❌ No | Authorization cannot be applied at partition level |

**Key Points:**
- **Namespace Level:** Grants access to all Event Hubs within that namespace. Useful for administrative scenarios.
- **Event Hub (Entity) Level:** Most common and recommended for production. Provides security isolation between different Event Hubs.
- **Partition Level:** Not supported. Once you have access to an Event Hub, you have access to all its partitions.

> **Note:** There is no "Topic" concept in Event Hubs (that's a Service Bus term). The equivalent is the **Event Hub entity** itself. If coming from Kafka, think of an Event Hub as analogous to a Kafka topic.

#### Azure RBAC (Role-Based Access Control)
When using Entra ID, assign built-in roles to scopes (Resource Group, Namespace, or Event Hub):
- **Azure Event Hubs Data Owner:** Full access to data (send and receive).
- **Azure Event Hubs Data Sender:** Send access only.
- **Azure Event Hubs Data Receiver:** Receive access only.

#### SAS Policies
When using SAS, policies grant specific rights:
- **Send:** Permission to send events.
- **Listen:** Permission to receive events.
- **Manage:** Permission to manage topology (create/delete consumer groups, etc.) + Send + Listen.

## 7. Best Practices
- **Partition Count:** Set at creation (difficult to change later). Match roughly to expected concurrent consumers.
- **Batching:** Send events in batches to improve throughput.
- **Security:** Use Shared Access Signatures (SAS) or Azure Active Directory (Entra ID) for access control.
- **Geo-Recovery:** Use Geo-Disaster Recovery to replicate namespace metadata (not data) to a secondary region.
