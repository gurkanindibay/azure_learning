# Azure Functions - Configuration Files

## Overview

Azure Functions use configuration files to define function behavior, triggers, bindings, and application settings. Understanding these configuration files is essential for developing, deploying, and managing Azure Functions effectively.

## Table of Contents

- [Key Configuration Files](#key-configuration-files)
- [function.json](#functionjson)
  - [Overview](#overview-1)
  - [Structure](#structure)
  - [Properties](#properties)
  - [Bindings Array](#bindings-array)
  - [Common Trigger Examples](#common-trigger-examples)
  - [Input and Output Bindings](#input-and-output-bindings)
- [host.json](#hostjson)
  - [Overview](#overview-2)
  - [Basic Structure](#basic-structure)
  - [Common Configuration Sections](#common-configuration-sections)
- [local.settings.json](#localsettingsjson)
  - [Overview](#overview-3)
  - [Structure](#structure-1)
  - [Properties](#properties-1)
  - [Required Settings](#required-settings)
- [Practice Question](#practice-question)
- [function.json vs Attributes/Decorators](#functionjson-vs-attributesdecorators)
- [Configuration Hierarchy](#configuration-hierarchy)
- [Common Configuration Scenarios](#common-configuration-scenarios)
- [Securing Configuration](#securing-configuration)
- [Deployment Considerations](#deployment-considerations)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)
- [Custom Handlers](#custom-handlers)
  - [Overview](#overview-4)
  - [Key Concepts](#key-concepts)
  - [How Custom Handlers Work](#how-custom-handlers-work)
  - [Configuration](#configuration)
  - [Custom Handler Requirements](#custom-handler-requirements)
  - [Example: Go Custom Handler](#example-go-custom-handler)
  - [Supported Languages via Custom Handlers](#supported-languages-via-custom-handlers)
  - [Practice Question](#practice-question-1)
  - [Custom Handlers vs Native Language Support](#custom-handlers-vs-native-language-support)
  - [Best Practices for Custom Handlers](#best-practices-for-custom-handlers)
- [Related Topics](#related-topics)

## Key Configuration Files

| File | Purpose | Scope |
|------|---------|-------|
| **function.json** | Defines triggers, bindings, and function-level settings | Per function |
| **host.json** | Configures runtime behavior and global settings | Function app (all functions) |
| **local.settings.json** | Stores app settings and connection strings for local development | Local only (not deployed) |
| **proxies.json** | Defines HTTP proxies (deprecated in Functions v4) | Function app |

## function.json

### Overview

The `function.json` file is the **primary configuration file** for Azure Functions. It defines the function's trigger, bindings, and other configuration settings.

**Key Facts:**
- Every function has **one and only one** `function.json` file
- Located in the function's folder (e.g., `MyFunction/function.json`)
- Defines what triggers the function (HTTP, Timer, Queue, etc.)
- Specifies input and output bindings
- The runtime uses this file to determine events to monitor
- Controls how data is passed into and returned from function execution

### Structure

```json
{
  "disabled": false,
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ],
  "scriptFile": "../dist/MyFunction/index.js",
  "entryPoint": "main"
}
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `disabled` | boolean | Whether the function is disabled |
| `bindings` | array | Array of trigger and binding configurations |
| `scriptFile` | string | Path to the script file containing the function code |
| `entryPoint` | string | Name of the function to execute (for compiled languages) |

### Bindings Array

Each binding in the `bindings` array must include:

| Property | Required | Description |
|----------|----------|-------------|
| `type` | Yes | Type of binding (e.g., `httpTrigger`, `queueTrigger`, `cosmosDBTrigger`) |
| `direction` | Yes | Direction of data flow: `in`, `out`, or `inout` |
| `name` | Yes | Name used in function code to access the binding data |

### Trigger Limit: Exactly One Per Function

**Key Concept**: A function must have **exactly one trigger**. Triggers are what cause a function to run - they define how a function is invoked. Triggers have associated data, which is often provided as the payload of the function.

**Important Rules:**
- A function **cannot** have zero triggers
- A function **cannot** have multiple triggers
- Each function has **exactly one** trigger

This is a fundamental design principle of Azure Functions that ensures clear, predictable function invocation.

### Practice Question: Number of Triggers Per Function

**Question:**

How many triggers can an Azure Function have?

**Options:**

A) Any number

B) 0 or 1

C) 32 maximum

D) Exactly one ✅

---

**Correct Answer: D) Exactly one**

---

**Explanation:**

Triggers are what cause a function to run. A trigger defines how a function is invoked and **a function must have exactly one trigger**. Triggers have associated data, which is often provided as the payload of the function.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Any number** | ❌ Incorrect - Functions are limited to exactly one trigger |
| **B) 0 or 1** | ❌ Incorrect - A function cannot have zero triggers; it must have exactly one |
| **C) 32 maximum** | ❌ Incorrect - There is no such limit; the rule is exactly one trigger |
| **D) Exactly one** | ✅ **Correct** - Every function must have exactly one trigger that defines how it's invoked |

**Visual Example:**

```
✅ Valid Function Configuration:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Trigger: Queue Trigger (1)          │  ← Exactly one trigger
│ Input Binding: Cosmos DB            │  ← Multiple bindings OK
│ Output Binding: Blob Storage        │
│ Output Binding: SendGrid Email      │
└─────────────────────────────────────┘

❌ Invalid - No Trigger:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Input Binding: Cosmos DB            │  ← No trigger = Invalid!
│ Output Binding: Blob Storage        │
└─────────────────────────────────────┘

❌ Invalid - Multiple Triggers:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Trigger: HTTP Trigger               │  ← Two triggers = Invalid!
│ Trigger: Queue Trigger              │
│ Output Binding: Blob Storage        │
└─────────────────────────────────────┘
```

**Triggers vs Bindings:**

| Aspect | Trigger | Bindings |
|--------|---------|----------|
| **Purpose** | Causes function to run | Provides input/output data |
| **Count per function** | **Exactly 1** | 0 to many |
| **Direction** | Always `in` | `in`, `out`, or `inout` |
| **Examples** | HTTP, Queue, Timer, Blob, Cosmos DB | Blob, Cosmos DB, Table, SendGrid |

**Reference:** [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings?tabs=csharp)

---

#### Direction Property Values

All triggers and bindings have a `direction` property in the `function.json` file. The possible values are:

| Value | Description |
|-------|-------------|
| `in` | **Input direction** - Data flows into the function. All triggers use this direction. Input bindings also use this direction to read data from external sources. |
| `out` | **Output direction** - Data flows out of the function. Output bindings use this direction to write data to external destinations. |
| `inout` | **Bidirectional** - Special direction that allows both reading and writing. When using `inout`, only the **Advanced editor** is available via the Integrate tab in the Azure portal. |

**Key Points:**
- For **triggers**, the direction is always `in`
- **Input bindings** use `in`
- **Output bindings** use `out`
- Some bindings support the special `inout` direction for bidirectional data flow

**Reference**: [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings?tabs=csharp)

### Common Trigger Examples

#### HTTP Trigger

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "anonymous",
      "methods": ["get", "post"],
      "route": "items/{id}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

#### Timer Trigger

```json
{
  "bindings": [
    {
      "type": "timerTrigger",
      "direction": "in",
      "name": "myTimer",
      "schedule": "0 */5 * * * *"
    }
  ]
}
```

##### Timer Trigger - TimerInfo Object

When using a Timer Trigger, the function receives a `TimerInfo` object that provides information about the timer invocation. This object includes useful properties for handling late executions.

**TimerInfo Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `Schedule` | TimerSchedule | The timer schedule |
| `ScheduleStatus` | ScheduleStatus | Status information including last/next scheduled times |
| `IsPastDue` | bool | `true` if the function invocation is later than scheduled |

**C# Example - Checking for Late Execution:**
```csharp
[FunctionName("TimerTriggerCSharp")]
public static void Run(
    [TimerTrigger("0 */5 * * * *")] TimerInfo myTimer, 
    ILogger log)
{
    if (myTimer.IsPastDue)
    {
        log.LogInformation("Timer is running late!");
    }
    
    log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
}
```

**When is a Timer Past Due?**
- The function host was stopped or restarted during a scheduled execution
- The function was delayed due to resource constraints
- The app was scaled down and missed a scheduled trigger
- The function app was in a cold start state

---

##### Practice Question: Timer Trigger - IsPastDue

**Question:**

Your function uses the following code. You want to add a message to the log when the function starts late. What code belongs in the missing line?

```csharp
[FunctionName("TimerTriggerCSharp")]
public static void Run(
    [TimerTrigger("0 */5 * * * *")] TimerInfo myTimer, 
    ILogger log)
{
    // >>>>> LINE MISSING HERE <<<<<
    {
        log.LogInformation("Timer is running late!");
    }
    
    log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
}
```

**Options:**

A) `if (TimerTrigger.IsLate)`

B) `if (myTimer.IsPastDue)` ✅

C) `if (myTimer.TriggerTime < DateTime.Now)`

D) `if (myTimer.IsLate)`

---

**Correct Answer: B) `if (myTimer.IsPastDue)`**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) `if (TimerTrigger.IsLate)`** | ❌ Incorrect - `TimerTrigger` is the attribute class, not an instance with properties. You cannot access instance properties from the attribute type itself. |
| **B) `if (myTimer.IsPastDue)`** | ✅ **Correct** - The `TimerInfo` object (named `myTimer` in this function) has an `IsPastDue` property that returns `true` if the function execution is later than scheduled. |
| **C) `if (myTimer.TriggerTime < DateTime.Now)`** | ❌ Incorrect - There is no `TriggerTime` property on `TimerInfo`. While the logic seems reasonable, this property does not exist. |
| **D) `if (myTimer.IsLate)`** | ❌ Incorrect - There is no `IsLate` property on `TimerInfo`. The correct property name is `IsPastDue`. |

**Reference:** [Azure Functions Timer Trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=csharp#ncrontab-expressions)

---

#### Queue Trigger

```json
{
  "bindings": [
    {
      "type": "queueTrigger",
      "direction": "in",
      "name": "myQueueItem",
      "queueName": "myqueue",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

#### Blob Trigger

```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "samples-workitems/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

#### Blob Trigger with Event Grid Source

For processing each blob only once (even if updated multiple times), use Event Grid as the source:

```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "samples-workitems/{name}",
      "connection": "AzureWebJobsStorage",
      "source": "EventGrid"
    }
  ]
}
```

#### Cosmos DB Trigger

```json
{
  "bindings": [
    {
      "type": "cosmosDBTrigger",
      "direction": "in",
      "name": "documents",
      "connectionStringSetting": "CosmosDBConnection",
      "databaseName": "MyDatabase",
      "collectionName": "MyContainer",
      "leaseCollectionName": "leases",
      "createLeaseCollectionIfNotExists": true
    }
  ]
}
```

### Input and Output Bindings

#### Cosmos DB Input Binding

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["get"]
    },
    {
      "type": "cosmosDB",
      "direction": "in",
      "name": "document",
      "connectionStringSetting": "CosmosDBConnection",
      "databaseName": "MyDatabase",
      "collectionName": "MyContainer",
      "id": "{Query.id}",
      "partitionKey": "{Query.partitionKey}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

#### Queue Output Binding

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["post"]
    },
    {
      "type": "queue",
      "direction": "out",
      "name": "outputQueueItem",
      "queueName": "outqueue",
      "connection": "AzureWebJobsStorage"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

## host.json

### Overview

The `host.json` file contains **global configuration options** that affect all functions in a function app.

**Location:** Root of the function app project

### Basic Structure

```json
{
  "version": "2.0",
  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Error",
      "Host.Aggregator": "Trace"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    },
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    },
    "cosmosDB": {
      "connectionMode": "Gateway",
      "protocol": "Https"
    }
  }
}
```

### Common Configuration Sections

#### Function Timeout

```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00"
}
```

**Timeout Limits by Plan:**
| Plan | Default | Maximum |
|------|---------|---------|
| Consumption | 5 minutes | 10 minutes |
| Premium | 30 minutes | Unlimited |
| Dedicated | 30 minutes | Unlimited |

#### HTTP Settings

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100,
      "dynamicThrottlesEnabled": true,
      "hsts": {
        "isEnabled": true,
        "maxAge": "10"
      }
    }
  }
}
```

#### Queue Settings

```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    }
  }
}
```

**Queue Settings Properties:**

| Property | Description | Default |
|----------|-------------|---------|
| `maxPollingInterval` | Maximum interval between queue polls | 00:01:00 |
| `visibilityTimeout` | Time a message is invisible after being dequeued | 00:00:00 (auto) |
| `batchSize` | Number of messages to retrieve per poll | 16 |
| `maxDequeueCount` | Number of times to try processing a message before moving to poison queue | 5 |
| `newBatchThreshold` | Threshold for fetching a new batch of messages | batchSize/2 |

#### Handling Poison Messages with Storage Queues

**Poison messages** are messages that cannot be processed successfully after multiple attempts. Azure Functions provides built-in support for handling poison messages with Azure Storage Queues.

**How it works:**
1. When a message is dequeued, the `dequeueCount` property is incremented
2. If processing fails, the message becomes visible again after `visibilityTimeout`
3. When `dequeueCount` exceeds `maxDequeueCount`, the message is automatically moved to a poison queue
4. The poison queue is named `<originalqueuename>-poison`

**Example Configuration:**
```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30"
    }
  }
}
```

With this configuration:
- A message will be retried **5 times** before being moved to the poison queue
- After each failed attempt, the message is invisible for **30 seconds** before retry

**Important Notes:**
- `maxDequeueCount` must be set to a value greater than 1 for automatic poison queue handling
- Setting `visibilityTimeout` to a high value only delays message visibility; it does **not** handle poison messages
- The poison queue must be monitored separately for manual investigation

#### Logging Configuration

```json
{
  "version": "2.0",
  "logging": {
    "fileLoggingMode": "debugOnly",
    "logLevel": {
      "default": "Information",
      "Host": "Error",
      "Function": "Error",
      "Host.Aggregator": "Information"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request"
      }
    }
  }
}
```

## local.settings.json

### Overview

The `local.settings.json` file stores **app settings, connection strings, and settings** used by local development tools.

**Important:** This file is **not deployed** to Azure. It's used only for local development.

### Structure

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "node",
    "MyCustomSetting": "value",
    "CosmosDBConnection": "AccountEndpoint=https://...",
    "ServiceBusConnection": "Endpoint=sb://..."
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*",
    "CORSCredentials": false
  },
  "ConnectionStrings": {
    "SQLConnection": "Server=..."
  }
}
```

### Properties

| Property | Description |
|----------|-------------|
| `IsEncrypted` | Whether settings are encrypted |
| `Values` | Collection of application settings (key-value pairs) |
| `Host` | Settings for local Function host |
| `ConnectionStrings` | Connection strings (use `Values` for Azure) |

### Required Settings

```json
{
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet|node|python|java|powershell"
  }
}
```

**FUNCTIONS_WORKER_RUNTIME Options:**
- `dotnet` - .NET (C#, F#)
- `dotnet-isolated` - .NET isolated worker
- `node` - JavaScript/TypeScript
- `python` - Python
- `java` - Java
- `powershell` - PowerShell

## Practice Question

### Question 1: Azure Functions Configuration File

**Scenario:**
You are developing an Azure Functions application.

**Question:**
Azure Functions store their configuration settings in which file?

**Options:**

1. ✅ function.json
   - **Correct**: The `function.json` file defines the function's trigger, bindings, and other configuration settings. Every function has one and only one trigger. The runtime uses this config file to determine the events to monitor and how to pass data into and return data from a function execution.

2. ❌ default.js
   - **Incorrect**: There is no `default.js` configuration file in Azure Functions. This is not a standard Azure Functions file.

3. ❌ index.js
   - **Incorrect**: The `index.js` file typically contains the function code in JavaScript/Node.js functions, not the configuration. Configuration is stored in `function.json`.

4. ❌ web.config
   - **Incorrect**: `web.config` is used in traditional ASP.NET applications for IIS configuration. While it may exist in some Azure Functions deployments for specific IIS settings, it is not the primary configuration file for Azure Functions.

---

### Question 2: Blob Trigger - Processing Each Blob Only Once

**Scenario:**
You are developing an Azure Function that processes data from an Azure Blob Storage container. The function should execute whenever a new blob is added to the container. You want to ensure that the function processes each blob only once, even if the blob is updated multiple times.

**Question:**
Which of the following configurations should you apply to the Blob Trigger binding?

**Options:**

1. ❌ Set `dataType` to `binary`
   - **Incorrect**: The `dataType` property specifies the type of data that the function expects to receive from the blob trigger (e.g., `binary`, `string`, `stream`). While this configuration is important for data processing, it does not ensure that the function processes each blob only once, regardless of updates.

2. ❌ Set `blobPath` to the container name
   - **Incorrect**: The `path` property (not `blobPath`) specifies the path within the Azure Blob Storage where the function should look for new blobs. While this configuration is crucial for defining the scope of the trigger, it does not address the requirement of processing each blob only once, even if updated multiple times.

3. ✅ Set `source` to `EventGrid`
   - **Correct**: Setting `source` to `EventGrid` configures the Blob Trigger binding to listen for events from Azure Event Grid instead of using the default polling mechanism. By using Event Grid:
     - The function receives notifications when a new blob is added
     - Event Grid provides **exactly-once delivery semantics** for blob creation events
     - The function processes each blob only once, even if the blob is updated multiple times after creation
     - This is more efficient and reliable than the default storage logs/polling approach

4. ❌ Set `connection` to the storage account connection string
   - **Incorrect**: The `connection` property specifies the app setting name that contains the storage account connection string. This configuration is essential for the function to access the Azure Blob Storage container but does not guarantee that each blob is processed only once.

---

#### Why Event Grid Source is Important

**Default Blob Trigger Behavior (Polling):**
- Uses storage logs or container polling to detect new/updated blobs
- May trigger multiple times for the same blob if it's updated
- Can have delays in detecting new blobs (especially in large containers)
- Less efficient for high-volume scenarios

**Event Grid Source Behavior:**
- Uses Azure Event Grid push-based notifications
- Triggers only on blob creation events (not updates, unless specifically configured)
- Near real-time notifications with low latency
- More reliable and scalable for high-volume scenarios
- **Exactly-once processing** for blob creation events

---

#### Configuration Example

**Default Blob Trigger (Polling - may process updates):**
```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "my-container/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

**Event Grid Source (Process each blob only once):**
```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "my-container/{name}",
      "connection": "AzureWebJobsStorage",
      "source": "EventGrid"
    }
  ]
}
```

**C# Attribute Example:**
```csharp
[FunctionName("BlobTriggerEventGrid")]
public static void Run(
    [BlobTrigger("my-container/{name}", Source = BlobTriggerSource.EventGrid, 
                 Connection = "AzureWebJobsStorage")] Stream myBlob,
    string name,
    ILogger log)
{
    log.LogInformation($"Processing blob: {name}, Size: {myBlob.Length} bytes");
}
```

---

#### Key Differences: Default vs Event Grid Source

| Aspect | Default (Polling) | Event Grid Source |
|--------|-------------------|-------------------|
| **Detection Method** | Storage logs / polling | Push notifications |
| **Latency** | Can be delayed (seconds to minutes) | Near real-time |
| **Trigger on Updates** | Yes (may trigger multiple times) | No (only on creation by default) |
| **Scalability** | Limited by polling frequency | Highly scalable |
| **Reliability** | May miss events in high-volume scenarios | Reliable delivery guarantees |
| **Setup** | Simpler (default) | Requires Event Grid subscription |
| **Cost** | Storage transaction costs | Event Grid costs |

---

#### Setting Up Event Grid for Blob Trigger

To use Event Grid source, you need to:

1. **Create an Event Grid System Topic** for the storage account
2. **Create an Event Subscription** that points to your function app
3. **Configure the Blob Trigger** with `"source": "EventGrid"`

**Azure CLI Example:**
```bash
# Create Event Grid system topic for storage account
az eventgrid system-topic create \
  --name my-storage-topic \
  --resource-group MyResourceGroup \
  --source /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage-account} \
  --topic-type Microsoft.Storage.StorageAccounts

# Create event subscription pointing to the function
az eventgrid system-topic event-subscription create \
  --name my-blob-subscription \
  --system-topic-name my-storage-topic \
  --resource-group MyResourceGroup \
  --endpoint-type azurefunction \
  --endpoint /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{function-app}/functions/{function-name} \
  --included-event-types Microsoft.Storage.BlobCreated
```

---

### Question 3: Handling Poison Messages with Storage Queues

**Scenario:**
You are developing an Azure Function that processes messages from an Azure Storage Queue. The function needs to handle poison messages (messages that cannot be processed successfully after multiple attempts).

**Question:**
Which of the following configurations should you implement to ensure poison messages are moved to a separate queue for further investigation?

**Options:**

1. ❌ Set `visibilityTimeout` to a high value in the queue trigger binding
   - **Incorrect**: Setting `visibilityTimeout` to a high value in the queue trigger binding will only delay the visibility of the message in the queue for processing. It does not handle the scenario of poison messages that cannot be processed successfully after multiple attempts.

2. ✅ Set `maxDequeueCount` to a value greater than 1 in the host.json file
   - **Correct**: Setting `maxDequeueCount` to a value greater than 1 in the `host.json` file allows you to specify the maximum number of times a message can be dequeued before it is considered a poison message. Once the message reaches this limit, it will be automatically moved to a separate queue named `<queuename>-poison` for further investigation.

3. ❌ Manually move poison messages to a dead-letter queue using custom code
   - **Incorrect**: Manually moving poison messages to a dead-letter queue using custom code is not an efficient solution as it requires additional development effort and monitoring. It is better to leverage built-in features of Azure Functions and Azure Storage Queues to handle poison messages automatically.

4. ❌ Enable Dead-lettering in the Storage Queue settings
   - **Incorrect**: Dead-lettering is a feature of **Service Bus Queues**, not Storage Queues, and is not applicable in this scenario. If you were using Service Bus Queues, enabling Dead-lettering would be a good approach as it allows you to automatically move messages that cannot be processed successfully to a separate dead-letter queue. However, for Storage Queues, use `maxDequeueCount` instead.

---

#### Key Differences: Storage Queues vs Service Bus Queues for Poison Messages

| Feature | Storage Queue | Service Bus Queue |
|---------|---------------|-------------------|
| **Poison Message Handling** | `maxDequeueCount` in host.json | Dead-letter queue (built-in) |
| **Poison Queue Name** | `<queuename>-poison` (auto-created) | Dead-letter sub-queue |
| **Configuration Location** | host.json | Service Bus settings |
| **Automatic Movement** | Yes (after maxDequeueCount) | Yes (with dead-lettering enabled) |

#### Configuration Example for Storage Queue Poison Messages

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30",
      "batchSize": 16
    }
  }
}
```

**function.json (Queue Trigger):**
```json
{
  "bindings": [
    {
      "type": "queueTrigger",
      "direction": "in",
      "name": "myQueueItem",
      "queueName": "myqueue",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

With this configuration, if a message from `myqueue` fails processing 5 times, it will automatically be moved to `myqueue-poison`.

**Reference**: [Azure Storage Queue trigger for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)

## function.json vs Attributes/Decorators

### Scripting Languages (JavaScript, Python, PowerShell)

For scripting languages, `function.json` is required and must be created manually:

**Folder Structure:**
```
MyFunctionApp/
├── host.json
├── local.settings.json
├── HttpTriggerFunction/
│   ├── function.json
│   └── index.js (or __init__.py)
└── TimerTriggerFunction/
    ├── function.json
    └── index.js (or __init__.py)
```

### Compiled Languages (C#, Java)

For compiled languages, you can use attributes/decorators instead of `function.json`:

**C# Example:**
```csharp
public static class MyFunction
{
    [FunctionName("HttpTriggerFunction")]
    public static async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest req,
        ILogger log)
    {
        log.LogInformation("C# HTTP trigger function processed a request.");
        return new OkObjectResult("Hello!");
    }
}
```

The `function.json` is generated automatically during the build process for compiled languages.

**Java Example:**
```java
public class Function {
    @FunctionName("HttpTriggerFunction")
    public HttpResponseMessage run(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET, HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION
        ) HttpRequestMessage<Optional<String>> request,
        final ExecutionContext context
    ) {
        context.getLogger().info("Java HTTP trigger processed a request.");
        return request.createResponseBuilder(HttpStatus.OK)
            .body("Hello!")
            .build();
    }
}
```

## Configuration Hierarchy

Azure Functions configuration follows this precedence (highest to lowest):

1. **Environment Variables** (Azure Portal app settings)
2. **local.settings.json** (local development only)
3. **host.json** (runtime configuration)
4. **function.json** (function-specific configuration)

## Common Configuration Scenarios

### Scenario 1: Disable a Function

**Using function.json:**
```json
{
  "disabled": true,
  "bindings": [...]
}
```

**Using App Settings:**
Set `AzureWebJobs.<FUNCTION_NAME>.Disabled` to `true`

### Scenario 2: Configure CORS for Local Development

**local.settings.json:**
```json
{
  "Host": {
    "CORS": "http://localhost:3000,http://localhost:4200",
    "CORSCredentials": true
  }
}
```

### Scenario 3: Set Custom Route Prefix

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "myapi"
    }
  }
}
```

Result: Functions accessible at `/myapi/functionname` instead of `/api/functionname`

### Scenario 4: Remove API Route Prefix

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

Result: Functions accessible at `/functionname` directly

## Securing Configuration

### Best Practices

1. **Never commit secrets to source control**
   - Add `local.settings.json` to `.gitignore`
   - Use Azure Key Vault for production secrets

2. **Use Azure Key Vault references**
   ```json
   {
     "Values": {
       "MySecret": "@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MySecret/)"
     }
   }
   ```

3. **Use Managed Identity**
   - Enable system-assigned or user-assigned managed identity
   - Grant appropriate permissions to access resources

4. **Separate environments**
   - Use different app settings for dev/staging/production
   - Use deployment slots for testing configuration changes

## Deployment Considerations

### Files Deployed vs Not Deployed

| File | Deployed | Notes |
|------|----------|-------|
| `function.json` | ✅ Yes | Required for scripted functions |
| `host.json` | ✅ Yes | Global runtime configuration |
| `local.settings.json` | ❌ No | Local development only |
| `proxies.json` | ✅ Yes | If using proxies (deprecated in v4) |

### Deploying App Settings

App settings from `local.settings.json` must be configured separately in Azure:

**Azure CLI:**
```bash
# Set single setting
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings "MySetting=MyValue"

# Set multiple settings from JSON file
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings @settings.json
```

**Azure Portal:**
1. Navigate to Function App
2. Go to Configuration > Application settings
3. Add/edit settings

## Troubleshooting

### Common Issues

**Problem**: Function not triggering
- Check `function.json` for correct trigger configuration
- Verify connection strings in app settings
- Ensure function is not disabled (`"disabled": false`)

**Problem**: Settings not found in Azure
- Remember `local.settings.json` is not deployed
- Configure app settings in Azure Portal or via CLI

**Problem**: Build errors with attributes
- Ensure NuGet packages are installed
- Check attribute syntax matches the binding version

**Problem**: Host.json settings not applied
- Verify JSON syntax is valid
- Check `"version": "2.0"` is specified
- Restart function app after changes

## Azure Functions Core Tools (Local Development)

### Overview

**Azure Functions Core Tools** is a command-line tool that provides the core runtime and templates for creating Azure Functions, enabling local development and testing before deploying to Azure.

### Key Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Local runtime**: Runs the same Functions runtime that's used in Azure
- **Function templates**: Provides templates to scaffold new functions
- **Local debugging**: Full debugging support in VS Code and Visual Studio
- **Deployment**: Deploy directly to Azure from the command line

### Version Information

| Version | Functions Runtime | Supported OS |
|---------|------------------|--------------|
| 4.x | Functions 4.x | Windows, macOS, Linux |
| 3.x | Functions 3.x | Windows, macOS, Linux |
| 2.x | Functions 2.x | Windows, macOS, Linux |
| 1.x | Functions 1.x | Windows only |

### Installation

**npm (all platforms):**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

**Homebrew (macOS):**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Windows (Chocolatey):**
```bash
choco install azure-functions-core-tools
```

### Common Commands

| Command | Description |
|---------|-------------|
| `func init` | Initialize a new Functions project |
| `func new` | Create a new function from a template |
| `func start` | Start the local Functions runtime |
| `func azure functionapp publish <name>` | Deploy to Azure |
| `func extensions install` | Install binding extensions |

### Local Development Workflow

1. **Initialize project**: `func init MyFunctionApp --worker-runtime dotnet`
2. **Create function**: `func new --name HttpTrigger --template "HTTP trigger"`
3. **Configure settings**: Edit `local.settings.json`
4. **Run locally**: `func start`
5. **Test**: Send requests to `http://localhost:7071/api/HttpTrigger`
6. **Deploy**: `func azure functionapp publish MyFunctionApp`

### Practice Question: Local Development Tools

**Question:**
Which library allows you to develop and test Azure Functions locally before deploying into Azure?

**Options:**

1. ✅ **Core Tools, cross-platform on Windows, macOS and Linux**
   - **Correct**: Azure Functions Core Tools provides the core runtime and templates for creating functions, which enable local development. Version 2.x and later supports development on Windows, Linux, and macOS. It includes the same runtime used in Azure, allowing you to test functions locally with full fidelity before deploying.

2. ❌ Azure Functions compile natively to an EXE and can be run from the command line
   - **Incorrect**: Azure Functions do not compile to standalone EXE files that can be run independently. While .NET-based functions compile to DLLs, they require the Functions runtime (provided by Core Tools locally or the Azure Functions host in the cloud) to execute.

3. ❌ Azure SDK library
   - **Incorrect**: The Azure SDK provides client libraries for interacting with Azure services from your code, but it is not a tool for running or testing Azure Functions locally. The SDK is used within your function code to connect to services like Storage, Cosmos DB, etc.

4. ❌ Azure Functions are cloud only, and cannot be tested locally
   - **Incorrect**: Azure Functions can absolutely be tested locally using Azure Functions Core Tools. Local development is a core feature of the Azure Functions development experience, and Microsoft strongly encourages testing locally before deploying to Azure.

**Reference**: [Azure Functions Core Tools - Develop Azure Functions locally](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local)

## Additional Resources

- [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [host.json reference](https://docs.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Work with Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [Azure Functions app settings reference](https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings)

## Custom Handlers

### Overview

**Custom handlers** are lightweight web servers that receive events from the Azure Functions host. They allow you to use **any language or runtime** that supports HTTP primitives to implement Azure Functions, even if that language is not natively supported by Azure Functions.

### Key Concepts

- **Purpose**: Enable Azure Functions with languages/runtimes not natively supported (e.g., Go, Rust, R, Deno)
- **Architecture**: A custom handler is a web server that receives HTTP requests from the Functions host
- **How it works**: The Functions host forwards trigger and binding data to your custom handler via HTTP requests

### How Custom Handlers Work

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Functions Host                         │
├─────────────────────────────────────────────────────────────────┤
│  Trigger Event (HTTP, Queue, Timer, etc.)                       │
│           ↓                                                     │
│  Functions Host receives event                                  │
│           ↓                                                     │
│  HTTP Request sent to Custom Handler (localhost:port)           │
│           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Custom Handler (Your Web Server)                        │   │
│  │  - Written in any language (Go, Rust, R, etc.)           │   │
│  │  - Receives HTTP POST with trigger/binding data          │   │
│  │  - Processes the request                                 │   │
│  │  - Returns HTTP response with output binding data        │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                     │
│  Functions Host receives response                               │
│           ↓                                                     │
│  Output bindings executed                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration

Custom handlers are configured in the `host.json` file:

```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler",
      "workingDirectory": "",
      "arguments": []
    },
    "enableForwardingHttpRequest": false
  }
}
```

**Configuration Properties:**

| Property | Description |
|----------|-------------|
| `defaultExecutablePath` | The executable to start as the custom handler process |
| `workingDirectory` | Working directory for the executable |
| `arguments` | Command-line arguments to pass to the executable |
| `enableForwardingHttpRequest` | For HTTP triggers only, forwards the original HTTP request instead of the custom handler payload |

### Custom Handler Requirements

For a custom handler to be deployable and executable inside Azure Functions, it must meet the following requirements:

#### 1. Must be a Standalone Executable or Script

The custom handler must be something that can run on the Azure Functions host environment:

| Platform | Executable Format |
|----------|-------------------|
| **Windows** | `.exe`, `.bat`, `.cmd`, or script with interpreter |
| **Linux** | ELF binary, shell script, or script with interpreter |

#### 2. Must be HTTP-Capable

Your custom handler must:
- Start an HTTP server
- Listen on the port specified by `FUNCTIONS_CUSTOMHANDLER_PORT` environment variable
- Accept HTTP POST requests from the Functions host
- Return HTTP responses

#### 3. Request/Response Format

The Functions host sends requests and expects responses in a specific JSON format:

**Incoming Request (from Functions host to your handler):**
```json
{
  "Data": {
    "req": {
      "Url": "https://myfunc.azurewebsites.net/api/hello",
      "Method": "GET",
      "Query": { "name": "World" },
      "Headers": { "Content-Type": ["application/json"] },
      "Body": ""
    }
  },
  "Metadata": {
    "sys": {
      "MethodName": "HttpTrigger",
      "UtcNow": "2025-11-26T12:00:00Z"
    }
  }
}
```

**Expected Response (from your handler back to Functions host):**
```json
{
  "Outputs": {
    "res": {
      "statusCode": 200,
      "body": "Hello, World!",
      "headers": { "Content-Type": "application/json" }
    }
  },
  "Logs": ["Function executed successfully"],
  "ReturnValue": null
}
```

#### 4. Deployment Requirements

Your executable must be included in the deployment package:

```
MyFunctionApp/
├── host.json                 # Points to your executable
├── local.settings.json
├── handler.exe               # Your custom handler (Windows)
├── handler                   # Your custom handler (Linux)
└── HttpTrigger/
    └── function.json         # Function bindings
```

#### 5. Platform Considerations

| Consideration | Requirement |
|---------------|-------------|
| **Architecture** | Must match the Azure Functions host (typically x64) |
| **Dependencies** | All dependencies must be bundled or available on the host |
| **Startup time** | Should start quickly to avoid cold start delays |
| **Port binding** | Must read `FUNCTIONS_CUSTOMHANDLER_PORT` and bind to it |

#### 6. Simplified Mode for HTTP-Only Functions

If you only use HTTP triggers, you can enable `enableForwardingHttpRequest: true` to receive the raw HTTP request instead of the wrapper format:

```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler"
    },
    "enableForwardingHttpRequest": true
  }
}
```

This forwards the original HTTP request directly, making it easier to build standard web servers without needing to parse the custom handler payload format.

### Example: Go Custom Handler

**handler.go:**
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
)

type InvokeRequest struct {
    Data     map[string]json.RawMessage
    Metadata map[string]interface{}
}

type InvokeResponse struct {
    Outputs     map[string]interface{}
    Logs        []string
    ReturnValue interface{}
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
    var invokeRequest InvokeRequest
    json.NewDecoder(r.Body).Decode(&invokeRequest)

    returnValue := "Hello from Go custom handler!"
    
    invokeResponse := InvokeResponse{
        Outputs:     make(map[string]interface{}),
        Logs:        []string{"Function executed successfully"},
        ReturnValue: returnValue,
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(invokeResponse)
}

func main() {
    customHandlerPort, exists := os.LookupEnv("FUNCTIONS_CUSTOMHANDLER_PORT")
    if !exists {
        customHandlerPort = "8080"
    }
    
    http.HandleFunc("/api/HttpTrigger", helloHandler)
    
    fmt.Println("Go custom handler listening on port", customHandlerPort)
    log.Fatal(http.ListenAndServe(":"+customHandlerPort, nil))
}
```

**host.json:**
```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler.exe",
      "workingDirectory": "",
      "arguments": []
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
```

**function.json (HttpTrigger folder):**
```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

### Supported Languages via Custom Handlers

Custom handlers enable Azure Functions with virtually any language that can:
- Create an HTTP server
- Process JSON requests
- Return JSON responses

**Examples of languages you can use:**
- Go
- Rust
- R
- Deno
- PHP
- Ruby
- Swift
- Perl
- Any other language with HTTP capabilities

### Practice Question

**Question:**
Which feature of Azure Functions allows you to use a runtime not currently supported natively by Azure?

**Options:**

1. ✅ **Custom Handlers**
   - **Correct**: Custom handlers are lightweight web servers that receive events from the Azure Functions host. While Azure Functions features many language handlers by default (C#, JavaScript, Python, Java, PowerShell), there are cases where you may want to use other languages or runtimes. Any language that supports HTTP primitives can implement a custom handler.

2. ❌ Durable Functions
   - **Incorrect**: Durable Functions is an extension of Azure Functions that lets you write stateful functions in a serverless environment. It's used for orchestrating workflows and managing state, not for adding support for additional programming languages or runtimes.

3. ❌ Serverless Functions
   - **Incorrect**: Serverless Functions is not a specific feature name in Azure Functions. Azure Functions itself is a serverless compute service, but there is no feature called "Serverless Functions" that enables additional runtime support.

4. ❌ SignalR
   - **Incorrect**: SignalR is a library for adding real-time web functionality to applications. Azure Functions has SignalR Service bindings for building real-time applications, but SignalR does not provide support for additional programming languages or runtimes.

**Reference**: [Azure Functions Custom Handlers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-custom-handlers)

### Custom Handlers vs Native Language Support

| Aspect | Native Language Support | Custom Handlers |
|--------|------------------------|-----------------|
| **Languages** | C#, JavaScript, Python, Java, PowerShell, TypeScript | Any language with HTTP support |
| **Performance** | Optimized for the runtime | Slightly more overhead due to HTTP communication |
| **Configuration** | Minimal setup | Requires host.json customHandler configuration |
| **Bindings** | Full support via attributes/decorators | Full support via function.json |
| **Cold Start** | Standard | Depends on executable startup time |
| **Debugging** | Native IDE support | Requires custom debugging setup |

### Best Practices for Custom Handlers

1. **Keep the handler lightweight**: Minimize startup time to reduce cold starts
2. **Handle errors gracefully**: Return appropriate HTTP status codes and error messages
3. **Log effectively**: Include logs in the response for debugging
4. **Use environment variables**: Read `FUNCTIONS_CUSTOMHANDLER_PORT` for the port to listen on
5. **Test locally**: Use Azure Functions Core Tools for local development and testing

## Related Topics

- Azure Functions hosting plans
- Azure Functions triggers and bindings
- Deployment and CI/CD
- Monitoring with Application Insights
