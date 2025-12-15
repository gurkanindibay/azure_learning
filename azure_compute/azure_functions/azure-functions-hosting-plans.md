# Azure Functions - Hosting Plans
## Table of Contents

- [Overview](#overview)
- [Hosting Plans Comparison](#hosting-plans-comparison)
- [Hosting Plans in Detail](#hosting-plans-in-detail)
  - [1. Consumption Plan](#1-consumption-plan)
  - [2. Premium Plan (Elastic Premium)](#2-premium-plan-elastic-premium)
  - [3. Dedicated Plan (App Service Plan)](#3-dedicated-plan-app-service-plan)
  - [4. App Service Environment (ASE)](#4-app-service-environment-ase)
- [Practice Question](#practice-question)
  - [Question: Selecting the Appropriate Hosting Plan](#question-selecting-the-appropriate-hosting-plan)
  - [Practice Question: Resolving Function Timeout Issues](#practice-question-resolving-function-timeout-issues)
- [Scaling Behavior: Event-Based vs Performance-Based](#scaling-behavior-event-based-vs-performance-based)
  - [Event-Based Scaling (Consumption & Premium)](#event-based-scaling-consumption-premium)
  - [Performance-Based Scaling (Dedicated & ASE)](#performance-based-scaling-dedicated-ase)
  - [Key Differences](#key-differences)
- [Choosing the Right Hosting Plan](#choosing-the-right-hosting-plan)
  - [Decision Tree](#decision-tree)
  - [Use Case Scenarios](#use-case-scenarios)
  - [Practice Question: Scheduled Maintenance Task - Cost-Effective Solution](#practice-question-scheduled-maintenance-task---cost-effective-solution)
- [Configuration Examples](#configuration-examples)
  - [Create Function App with Consumption Plan](#create-function-app-with-consumption-plan)
  - [Create Function App with Premium Plan](#create-function-app-with-premium-plan)
  - [Create Function App with Dedicated Plan](#create-function-app-with-dedicated-plan)
- [Cost Optimization Strategies](#cost-optimization-strategies)
  - [Consumption Plan Tips](#consumption-plan-tips)
  - [Premium Plan Tips](#premium-plan-tips)
  - [Dedicated Plan Tips](#dedicated-plan-tips)
- [Common Azure CLI Commands](#common-azure-cli-commands)
  - [Function App Management](#function-app-management)
  - [Plan Management](#plan-management)
  - [Configuration Commands](#configuration-commands)
- [Best Practices](#best-practices)
  - [General Recommendations](#general-recommendations)
  - [Security Considerations](#security-considerations)
  - [Performance Optimization](#performance-optimization)
  - [Warmup Triggers for Premium Plan](#warmup-triggers-for-premium-plan)
  - [Practice Question: Warmup Trigger Configuration](#practice-question-warmup-trigger-configuration)
  - [ReadyToRun Compilation for .NET Isolated Worker Model](#readytorun-compilation-for-net-isolated-worker-model)
  - [Practice Question: Improving Cold Start Performance](#practice-question-improving-cold-start-performance)
  - [Scaling Configuration](#scaling-configuration)
- [Migration Between Plans](#migration-between-plans)
  - [Consumption → Premium](#consumption-premium)
  - [Consumption/Premium → Dedicated](#consumptionpremium-dedicated)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
- [Additional Resources](#additional-resources)
- [Related Topics](#related-topics)


## Overview

Azure Functions offers multiple hosting plans that determine how your function app scales, the resources available, and the pricing model. Choosing the right hosting plan is critical for meeting your application's performance, scaling, and cost requirements.

## Hosting Plans Comparison

| Feature | Consumption | Premium | Dedicated (App Service) | App Service Environment (ASE) |
|---------|-------------|---------|------------------------|-------------------------------|
| **Pricing Model** | Serverless (pay-per-execution) | Serverless with pre-warmed instances | Always-on pricing | Isolated, dedicated environment |
| **Scaling** | Automatic, event-based | Automatic, event-based | Manual or automatic (performance-based) | Manual or automatic (performance-based) |
| **Cold Start** | Yes | No (pre-warmed instances) | No (always on) | No (always on) |
| **Max Instances** | 200 (Windows), 100 (Linux) | Up to 100 | Limited by App Service plan | Limited by plan |
| **Max Timeout** | 5 min (default), 10 min (max) | Unlimited (30 min default) | Unlimited | Unlimited |
| **VNet Integration** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes (native) |
| **Best For** | Event-driven, sporadic workloads | Production apps needing VNet, no cold starts | Existing App Service infrastructure | High-security, isolated workloads |

## Hosting Plans in Detail

### 1. Consumption Plan

The Consumption plan is the default serverless hosting option for Azure Functions.

**Key Characteristics:**
- **Serverless pricing**: Pay only for the time your functions run
- **Event-based scaling**: Automatically scales based on incoming events
- **Dynamic resource allocation**: Azure allocates compute resources dynamically
- **Cold starts**: Functions may experience cold starts after periods of inactivity
- **Timeout limits**: Maximum execution time of 10 minutes

**Pricing:**
- Charged based on:
  - Number of executions
  - Execution time (GB-seconds)
  - Memory consumption
- Includes 1 million free executions per month
- 400,000 GB-seconds free per month

**When to Use:**
- Event-driven workloads (triggers from queues, HTTP, timers)
- Unpredictable or sporadic traffic patterns
- Cost optimization is a priority
- Short-running functions (< 10 minutes)
- Development and testing environments

**Limitations:**
- Cold starts can impact latency
- No VNet integration
- Limited execution timeout
- Limited control over scaling behavior

### 2. Premium Plan (Elastic Premium)

The Premium plan provides serverless capabilities with enhanced performance and features.

**Key Characteristics:**
- **Pre-warmed instances**: Eliminates cold starts with always-ready instances
- **VNet connectivity**: Full integration with Azure Virtual Networks
- **Unlimited execution duration**: No timeout limits (30-minute default, configurable)
- **More powerful compute**: Premium instance sizes available
- **Event-based scaling**: Like Consumption, but with pre-warmed instances

**Pricing:**
- Based on:
  - Number of core-seconds
  - Memory allocated across pre-warmed and scaled instances
- More expensive than Consumption, but predictable performance

**When to Use:**
- Production applications requiring consistent performance
- Apps needing VNet integration for security
- Functions with longer execution times
- Workloads sensitive to cold starts
- Applications requiring more CPU or memory

**Available SKUs:**
- **EP1**: 1 vCPU, 3.5 GB memory
- **EP2**: 2 vCPU, 7 GB memory
- **EP3**: 4 vCPU, 14 GB memory

### 3. Dedicated Plan (App Service Plan)

Run Functions on the same infrastructure as App Service web apps.

**Key Characteristics:**
- **Always-on**: Functions are always running, no cold starts
- **Predictable pricing**: Fixed monthly cost based on plan tier
- **Performance-based scaling**: Scales based on CPU/memory metrics, not events
- **Full control**: Manage scaling rules and instance count
- **Shared infrastructure**: Use existing App Service plans

**Pricing:**
- Pay for the App Service plan tier (Basic, Standard, Premium)
- Same cost whether functions run or not

**When to Use:**
- You already have underutilized App Service plans
- Long-running functions that need always-on capability
- Predictable, steady workloads
- Need full control over the compute environment
- Require custom images or specific configurations

**App Service Plan Tiers:**
- **Basic (B1-B3)**: Development/testing, no autoscaling
- **Standard (S1-S3)**: Production workloads, autoscaling available
- **Premium V2 (P1v2-P3v2)**: Enhanced performance
- **Premium V3 (P1v3-P3v3)**: Latest generation, best performance

### 4. App Service Environment (ASE)

A fully isolated and dedicated environment for running Azure Functions at high scale.

**Key Characteristics:**
- **Complete isolation**: Runs in your own VNet
- **High scale**: Support for large-scale deployments
- **Dedicated hardware**: Not shared with other customers
- **Enhanced security**: Network isolation, private endpoints
- **Performance-based scaling**: Like App Service, not event-based

**Pricing:**
- Most expensive option
- Pay for:
  - ASE infrastructure (base cost)
  - App Service plans within the ASE
  - Data egress

**When to Use:**
- Regulatory or compliance requirements for isolation
- High-security scenarios
- Very large-scale deployments
- Need for dedicated infrastructure
- Private, isolated network requirements

**ASE Versions:**
- **ASE v3**: Latest version, simplified networking, faster scaling
- **ASE v2**: Legacy version (retiring)

## Practice Question

### Question: Selecting the Appropriate Hosting Plan

**Scenario:**
You plan to create an Azure Functions app named app1.

You need to ensure that app1 will satisfy the following requirements:
- Supports automatic scaling
- Has event-based scaling behavior
- Provides a serverless pricing model

**Question:**
Which hosting plan should you use?

**Options:**

1. ❌ App Service
   - **Incorrect**: The App Service (Dedicated) hosting plan supports autoscaling, but its scaling behavior is **performance-based** (CPU, memory metrics), not **event-based**. Additionally, it uses an **always-on pricing model** where you pay for the compute resources regardless of whether functions are executing, which does not meet the serverless pricing requirement.

2. ❌ App Service Environment
   - **Incorrect**: App Service Environment (ASE) supports autoscaling, but like the Dedicated plan, its scaling behavior is **performance-based**, not **event-based**. ASE also does not provide a serverless pricing model; instead, it uses a dedicated infrastructure model where you pay for the isolated environment and the App Service plans within it, regardless of function execution.

3. ✅ Consumption
   - **Correct**: The Consumption hosting plan satisfies all three requirements:
     - ✅ **Supports automatic scaling**: Automatically scales in and out based on load
     - ✅ **Event-based scaling behavior**: Scales dynamically in response to events (HTTP requests, queue messages, timer triggers, etc.)
     - ✅ **Serverless pricing model**: Pay only for the time your functions execute and the resources consumed (executions + GB-seconds)

4. ❌ Functions Premium
   - **Incorrect**: While the Functions Premium plan supports autoscaling and has event-based scaling behavior, it does **not provide a true serverless pricing model**. The Premium plan requires you to pay for pre-warmed instances that are always running, resulting in a minimum monthly cost regardless of usage. This is beneficial for eliminating cold starts and providing consistent performance, but it doesn't meet the serverless pricing requirement.

---

### Practice Question: Resolving Function Timeout Issues

**Question:**

You develop an HTTP triggered Azure Function app to process Azure Storage blob data. The app is triggered using an output binding on the blob. The app continues to time out after four minutes. The app must process the blob data.

You need to ensure the app does not time out and processes the blob data.

**Proposed Solution:** Configure the app to use an App Service hosting plan and enable the Always On setting.

Does the solution meet the goal?

**Options:**

A) Yes

B) No ✅

---

**Correct Answer: B) No**

---

**Explanation:**

Using an App Service hosting plan and enabling the Always On setting can help keep the Azure Function app warm and prevent cold starts, but it **does not directly address the timeout issue**.

| Aspect | What Always On Does | What It Doesn't Do |
|--------|---------------------|-------------------|
| **Cold Starts** | ✅ Prevents cold starts by keeping the app warm | - |
| **Function Timeout** | ❌ Does not change timeout limits | Does not extend execution time |
| **Execution Duration** | - | ❌ Does not allow longer-running functions |

**The Correct Solution:**

The timeout for Azure Functions is controlled by the `functionTimeout` setting in the **host.json** file. To address the timeout issue and ensure the app processes the blob data without timing out, you should:

1. **Adjust the `functionTimeout` setting** in host.json to allow for longer processing times
2. **Or migrate to a Premium or Dedicated plan** which support unlimited execution duration

**host.json Configuration Example:**

```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00"
}
```

**Timeout Limits by Plan:**

| Plan | Default Timeout | Maximum Timeout |
|------|-----------------|-----------------|
| Consumption | 5 minutes | 10 minutes |
| Premium | 30 minutes | **Unlimited** |
| Dedicated (App Service) | 30 minutes | **Unlimited** |

**Key Takeaways:**
- **Always On** prevents cold starts but doesn't affect execution timeout
- **functionTimeout** in host.json controls execution duration
- For functions requiring more than 10 minutes, use Premium or Dedicated plans
- Consider breaking long-running operations into smaller chunks or using Durable Functions for very long processes

---

## Scaling Behavior: Event-Based vs Performance-Based

### Event-Based Scaling (Consumption & Premium)

Event-based scaling responds directly to the number of events in the trigger source:

**How It Works:**
- Azure monitors the event source (queue depth, Event Hub partition count, HTTP requests)
- Scales out by adding instances when events exceed capacity
- Scales in when event volume decreases
- Each instance processes multiple events concurrently

**Example (Queue Trigger):**
```
Queue Messages: 1,000 → Azure adds instances → 10 instances processing 100 messages each
Queue Messages: 100 → Azure removes instances → 2 instances processing 50 messages each
Queue Empty → Azure scales down to minimum (0 in Consumption, pre-warmed in Premium)
```

**Supported in:**
- Consumption plan ✅
- Premium plan ✅

### Performance-Based Scaling (Dedicated & ASE)

Performance-based scaling responds to resource utilization metrics:

**How It Works:**
- Azure monitors CPU, memory, and other performance metrics
- Scales out when metrics exceed thresholds (e.g., CPU > 80%)
- Scales in when metrics drop below thresholds
- Requires autoscale rules configuration

**Example (CPU Metric):**
```
CPU Usage: 85% → Add 2 instances → CPU Usage: 60%
CPU Usage: 40% → Remove 1 instance → CPU Usage: 50%
CPU Usage: 70% → No change (within threshold)
```

**Supported in:**
- Dedicated (App Service) plan ✅
- App Service Environment ✅

### Key Differences

| Aspect | Event-Based | Performance-Based |
|--------|-------------|-------------------|
| **Trigger** | Number of events | CPU/Memory metrics |
| **Response Time** | Near-instant | Delayed (metrics collection + evaluation) |
| **Granularity** | Per-function scaling | Per-app scaling |
| **Configuration** | Automatic | Requires autoscale rules |
| **Best For** | Event-driven workloads | Request-driven web apps |

## Choosing the Right Hosting Plan

### Decision Tree

```
Start
  │
  ├─ Need network isolation? 
  │   └─ YES → App Service Environment (ASE)
  │   └─ NO → Continue
  │
  ├─ Need VNet integration or no cold starts?
  │   └─ YES → Premium Plan
  │   └─ NO → Continue
  │
  ├─ Already have App Service plan or need always-on?
  │   └─ YES → Dedicated (App Service Plan)
  │   └─ NO → Continue
  │
  └─ Cost-sensitive, event-driven, short-running?
      └─ YES → Consumption Plan
```

### Use Case Scenarios

**Scenario 1: Startup with Sporadic Traffic**
- **Best Choice**: Consumption Plan
- **Reason**: Pay-per-execution model minimizes costs during low usage

**Scenario 2: E-commerce with Peak Hours**
- **Best Choice**: Premium Plan
- **Reason**: Pre-warmed instances handle peak traffic without cold starts

**Scenario 3: Enterprise with Existing App Service Infrastructure**
- **Best Choice**: Dedicated (App Service Plan)
- **Reason**: Leverage existing plans, predictable costs

**Scenario 4: Healthcare App with Compliance Requirements**
- **Best Choice**: App Service Environment (ASE)
- **Reason**: Complete network isolation meets regulatory requirements

**Scenario 5: Scheduled Maintenance Tasks**
- **Best Choice**: Consumption Plan with Timer Trigger
- **Reason**: Pay-per-execution model is ideal for periodic tasks that run on a schedule (e.g., hourly file copy operations)

---

### Practice Question: Scheduled Maintenance Task - Cost-Effective Solution

**Question:**

You have an Azure App Service web app (App1) deployed across multiple instances in two regions. Every hour, you need to run a maintenance task by invoking a PowerShell script that copies files from all the App1 instances. The PowerShell script will run from a central location.

You need to recommend a solution for the maintenance task. The solution must minimize costs.

What should you include in the recommendation?

**Options:**

A) An Azure virtual machine

B) An Azure function app ✅

C) An Azure logic app

D) An Azure App Service WebJob

---

**Correct Answer: B) An Azure function app**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) An Azure virtual machine** | ❌ Incorrect - A virtual machine requires continuous compute provisioning, even when idle, resulting in higher costs and more management overhead. For a task that runs only once per hour, you would be paying for 59+ minutes of idle time every hour, which contradicts the goal to minimize costs. |
| **B) An Azure function app** | ✅ **Correct** - Azure Functions is a serverless compute service ideal for event-driven or scheduled tasks such as running PowerShell scripts on a timer. Using an Azure Function app with a Timer trigger offers a low-cost, serverless solution that scales automatically and incurs charges only when it runs — making it the most cost-efficient and lightweight option for hourly maintenance tasks. |
| **C) An Azure logic app** | ❌ Incorrect - While Logic Apps support automation workflows and can run on schedules, they are typically used for declarative integration and business process automation. Logic Apps are not ideal for PowerShell execution that involves copying files from virtual machines. They also have per-action pricing that can add up for complex operations. |
| **D) An Azure App Service WebJob** | ❌ Incorrect - WebJobs run within an App Service plan, which requires dedicated compute resources. Unless the app is already on the same App Service plan, this introduces unnecessary cost compared to a serverless function app. Additionally, WebJobs require the App Service plan to be always running for triggered jobs. |

**Cost Comparison:**

| Service | Pricing Model | Cost for Hourly Task |
|---------|---------------|---------------------|
| **Azure Functions (Consumption)** | Pay-per-execution | Only charges when running (~$0.000016/GB-s) |
| **Azure VM** | Always-on pricing | Continuous cost 24/7 even when idle |
| **Azure Logic Apps** | Per-action pricing | Cost per trigger + action execution |
| **App Service WebJob** | Included in App Service plan | Requires dedicated App Service plan |

**Azure Function Timer Trigger Configuration:**

For an hourly maintenance task, you would configure a Timer trigger with a CRON expression:

```json
{
  "bindings": [
    {
      "type": "timerTrigger",
      "direction": "in",
      "name": "myTimer",
      "schedule": "0 0 * * * *"
    }
  ]
}
```

The CRON expression `0 0 * * * *` runs the function at the start of every hour (second 0, minute 0, every hour).

**Key Benefits of Azure Functions for Scheduled Tasks:**

1. **Serverless pricing**: Only pay when the function executes
2. **No infrastructure management**: No VMs to patch or maintain
3. **Built-in Timer trigger**: Native support for CRON-based scheduling
4. **PowerShell support**: Azure Functions supports PowerShell as a runtime
5. **Auto-scaling**: Scales automatically if multiple executions overlap
6. **Monitoring**: Built-in integration with Application Insights

**References:**
- [Azure Functions overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Timer trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer)
- [Azure Logic Apps overview](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)
- [Run background tasks with WebJobs in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/webjobs-create)
- [Azure Virtual Machines overview](https://learn.microsoft.com/en-us/azure/virtual-machines/overview)

---

## Configuration Examples

### Create Function App with Consumption Plan

**Azure CLI:**
```bash
# Create resource group
az group create --name MyResourceGroup --location eastus

# Create storage account (required for all plans)
az storage account create \
  --name mystorageaccount \
  --resource-group MyResourceGroup \
  --location eastus \
  --sku Standard_LRS

# Create Function App with Consumption plan
az functionapp create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --consumption-plan-location eastus \
  --runtime dotnet \
  --functions-version 4
```

### Create Function App with Premium Plan

**Azure CLI:**
```bash
# Create Premium plan
az functionapp plan create \
  --name MyPremiumPlan \
  --resource-group MyResourceGroup \
  --location eastus \
  --sku EP1 \
  --is-linux

# Create Function App using Premium plan
az functionapp create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --plan MyPremiumPlan \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4
```

### Create Function App with Dedicated Plan

**Azure CLI:**
```bash
# Create App Service plan
az appservice plan create \
  --name MyAppServicePlan \
  --resource-group MyResourceGroup \
  --location eastus \
  --sku S1 \
  --is-linux

# Create Function App using App Service plan
az functionapp create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --plan MyAppServicePlan \
  --runtime node \
  --runtime-version 18 \
  --functions-version 4
```

## Cost Optimization Strategies

### Consumption Plan Tips

1. **Optimize execution time**: Shorter functions = lower costs
2. **Batch processing**: Process multiple items per execution
3. **Use appropriate triggers**: Choose efficient trigger types
4. **Monitor free tier**: Track usage against free allocation
5. **Cold start mitigation**: Use Premium if cold starts are problematic

### Premium Plan Tips

1. **Right-size instances**: Start with EP1, scale up if needed
2. **Configure minimum instances**: Balance performance vs cost
3. **Use always-ready instances**: Set minimum to handle baseline load
4. **Monitor utilization**: Adjust instance count based on actual usage
5. **Consider reserved capacity**: Commit to reserved instances for discounts

### Dedicated Plan Tips

1. **Share plans**: Run multiple function apps on one plan
2. **Use autoscaling**: Automatically adjust instances based on load
3. **Right-size tier**: Don't over-provision; start small and scale
4. **Leverage existing infrastructure**: Use underutilized App Service plans
5. **Schedule scaling**: Scale down during off-peak hours

## Common Azure CLI Commands

### Function App Management

| Command | Description |
|---------|-------------|
| `az functionapp create` | Create a new Function App |
| `az functionapp list` | List all Function Apps |
| `az functionapp show` | Show details of a Function App |
| `az functionapp delete` | Delete a Function App |
| `az functionapp restart` | Restart a Function App |

### Plan Management

| Command | Description |
|---------|-------------|
| `az functionapp plan create` | Create a Premium plan |
| `az appservice plan create` | Create an App Service plan |
| `az functionapp plan list` | List all Function App plans |
| `az functionapp plan show` | Show plan details |
| `az functionapp plan update` | Update plan configuration |

### Configuration Commands

| Command | Description |
|---------|-------------|
| `az functionapp config appsettings set` | Set application settings |
| `az functionapp config appsettings list` | List application settings |
| `az functionapp deployment source config` | Configure deployment source |
| `az functionapp vnet-integration add` | Add VNet integration (Premium/Dedicated) |

## Best Practices

### General Recommendations

1. **Start with Consumption**: Begin with the Consumption plan for most workloads
2. **Measure before upgrading**: Use Application Insights to understand performance needs
3. **Consider cold starts**: If latency is critical, use Premium or Dedicated plans
4. **Plan for VNet needs**: If you need VNet integration, choose Premium or Dedicated
5. **Monitor costs**: Set up cost alerts and monitor spending patterns

### Security Considerations

1. **Use managed identities**: Avoid storing credentials in code
2. **Enable VNet integration**: Isolate functions from public internet (Premium/Dedicated/ASE)
3. **Configure access restrictions**: Limit inbound traffic to specific IP ranges
4. **Use Key Vault**: Store secrets in Azure Key Vault, not app settings
5. **Enable HTTPS only**: Enforce HTTPS for all function endpoints

### Performance Optimization

1. **Minimize cold starts**: Use Premium plan or always-on for Dedicated plans
2. **Optimize dependencies**: Reduce package size and initialization time
3. **Use async patterns**: Leverage asynchronous programming
4. **Implement retry logic**: Handle transient failures gracefully
5. **Monitor with Application Insights**: Track performance metrics and errors
6. **Enable ReadyToRun compilation**: For .NET isolated worker model apps, use ahead-of-time compilation to improve startup performance
7. **Use warmup triggers**: Initialize dependencies before instances receive traffic (Premium plan)

### Warmup Triggers for Premium Plan

**Overview:**
When using Azure Functions on a Premium plan with pre-warmed instances, you may still experience cold starts when the app scales beyond the pre-warmed instance count. Warmup triggers allow you to initialize dependencies (e.g., database connections, caches, or HTTP clients) before the instance receives traffic.

**Key Points:**
- The warmup trigger function **must be named `warmup`** (case-insensitive)
- This is the **only recognized name** for warmup trigger functions
- Executes when new instances are added during scale-out operations
- Allows you to pre-initialize expensive resources

**Example (C#):**

```csharp
[FunctionName("warmup")]
public static void Warmup([WarmupTrigger] WarmupContext context, ILogger log)
{
    log.LogInformation("Warmup function triggered");
    
    // Initialize dependencies
    // - Database connections
    // - Cache clients
    // - HTTP clients
    // - Other expensive resources
}
```

**Example (JavaScript):**

```javascript
module.exports = async function (context, warmupContext) {
    context.log('Warmup function triggered');
    
    // Initialize dependencies here
};
```

With `function.json`:
```json
{
  "bindings": [
    {
      "type": "warmupTrigger",
      "direction": "in",
      "name": "warmupContext"
    }
  ]
}
```

**Important:** The function name must be exactly `warmup`. Other names like `startup`, `initialize`, or `preload` will **not** work.

---

### Practice Question: Warmup Trigger Configuration

**Question:**

You have an Azure Functions app running on a Premium plan with pre-warmed instances enabled. The app experiences cold starts when scaling beyond the pre-warmed instance count. You need to configure a warmup trigger to initialize dependencies before the instance receives traffic. Which function name should you use for the warmup trigger?

**Options:**

A) startup

B) warmup ✅

C) preload

D) initialize

---

**Correct Answer: B) warmup**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) startup** | ❌ Incorrect - The name `startup` is not the correct naming convention for warmup triggers in Azure Functions. The function must be named `warmup` to work properly. |
| **B) warmup** | ✅ **Correct** - The warmup trigger function must be named `warmup` (case-insensitive) as per Azure Functions requirements. This is the only recognized name for warmup trigger functions that execute when new instances are added during scale-out operations. |
| **C) preload** | ❌ Incorrect - The name `preload` is not recognized for warmup triggers. Azure Functions specifically looks for a function named `warmup` to execute during instance initialization. |
| **D) initialize** | ❌ Incorrect - The name `initialize` is not recognized by Azure Functions for warmup triggers. The function must be specifically named `warmup` to be triggered when new instances are added. |

---

### ReadyToRun Compilation for .NET Isolated Worker Model

**Overview:**
ReadyToRun (R2R) is a form of ahead-of-time (AOT) compilation that can significantly improve startup performance for .NET applications. This is especially valuable for Azure Functions running in a Consumption plan where cold starts are a concern.

**Key Points:**
- Available for .NET isolated worker model functions (not in-process model)
- Requires `FUNCTIONS_WORKER_RUNTIME` to be set to `dotnet-isolated` (not `dotnet`)
- The runtime architecture must match the hosting environment (e.g., `win-x64`, `linux-x64`)
- Reduces JIT (Just-In-Time) compilation overhead during startup

**Configuration:**

To enable ReadyToRun compilation, add the following to your `.csproj` file:

```xml
<PropertyGroup>
  <PublishReadyToRun>true</PublishReadyToRun>
  <RuntimeIdentifier>win-x64</RuntimeIdentifier>
</PropertyGroup>
```

Or for Linux:
```xml
<PropertyGroup>
  <PublishReadyToRun>true</PublishReadyToRun>
  <RuntimeIdentifier>linux-x64</RuntimeIdentifier>
</PropertyGroup>
```

**Important Considerations:**

| Aspect | Description |
|--------|-------------|
| **Worker Runtime** | Must use `dotnet-isolated` for isolated worker model, not `dotnet` |
| **Architecture Match** | Runtime architecture must match hosting environment |
| **Build Size** | ReadyToRun binaries are larger than standard binaries |
| **Cold Start Improvement** | Reduces cold start latency by pre-compiling native code |

**FUNCTIONS_WORKER_RUNTIME Settings:**

| Value | Model | .NET Support |
|-------|-------|--------------|
| `dotnet` | In-process model | .NET 6 (deprecated, ending support Nov 10, 2026) |
| `dotnet-isolated` | Isolated worker model | .NET 6, .NET 7, .NET 8+ |

**Note:** The in-process model (`dotnet`) does not support .NET 8. If you're using .NET 8, you must use the isolated worker model with `FUNCTIONS_WORKER_RUNTIME` set to `dotnet-isolated`.

---

### Practice Question: Improving Cold Start Performance

**Question:**

You have an Azure Functions app that uses the isolated worker model with .NET 8. You need to ensure the app benefits from improved startup performance when running in a Consumption plan. What should you configure?

**Options:**

A) Set FUNCTIONS_WORKER_RUNTIME to dotnet and configure netFrameworkVersion to 8.0

B) Enable ReadyToRun compilation in the project file and ensure the runtime architecture matches the hosting environment ✅

C) Migrate the app from the isolated worker model to the in-process model

D) Configure always-on setting in the App Service plan and scale out to multiple instances

---

**Correct Answer: B) Enable ReadyToRun compilation in the project file and ensure the runtime architecture matches the hosting environment**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Set FUNCTIONS_WORKER_RUNTIME to dotnet** | ❌ Incorrect - `FUNCTIONS_WORKER_RUNTIME` must be set to `dotnet-isolated` for the isolated worker model, not `dotnet`. Setting it to `dotnet` would attempt to use the in-process model which doesn't support .NET 8. |
| **B) Enable ReadyToRun compilation** | ✅ **Correct** - You can compile your function app as ReadyToRun binaries. ReadyToRun is a form of ahead-of-time compilation that can improve startup performance to help reduce the effect of cold starts when running in a Consumption plan. This requires matching the runtime architecture to the hosting environment. |
| **C) Migrate to the in-process model** | ❌ Incorrect - Support will end for the in-process model on November 10, 2026. We highly recommend that you migrate your apps to the isolated worker model for full support. This would be moving backwards and doesn't address the performance requirement. Additionally, the in-process model doesn't support .NET 8. |
| **D) Configure always-on setting** | ❌ Incorrect - The always-on setting is not available in Consumption plans and is only applicable to Premium and Dedicated plans. Scaling out doesn't address cold start performance for individual instances. |

**Visual Comparison:**

```
✅ Correct Configuration for .NET 8 Isolated Worker:
┌─────────────────────────────────────┐
│ .csproj                             │
├─────────────────────────────────────┤
│ <PublishReadyToRun>true</...>       │
│ <RuntimeIdentifier>win-x64</...>    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Application Settings                │
├─────────────────────────────────────┤
│ FUNCTIONS_WORKER_RUNTIME=dotnet-isolated │
└─────────────────────────────────────┘

❌ Invalid Configuration:
┌─────────────────────────────────────┐
│ Application Settings                │
├─────────────────────────────────────┤
│ FUNCTIONS_WORKER_RUNTIME=dotnet     │  ← Wrong! .NET 8 requires isolated model
└─────────────────────────────────────┘
```

**Reference:** [Azure Functions .NET isolated worker process](https://learn.microsoft.com/en-us/azure/azure-functions/dotnet-isolated-process-guide)

### Scaling Configuration

1. **Set appropriate maximum instances**: Prevent runaway scaling costs
2. **Configure scale-out rules**: Define when to add instances (Dedicated/ASE)
3. **Set scale-in rules**: Define when to remove instances
4. **Use pre-warmed instances**: Configure minimum instances (Premium)
5. **Test scaling behavior**: Validate scaling under realistic load

## Migration Between Plans

### Consumption → Premium

**Reasons to Migrate:**
- Eliminate cold starts
- Add VNet connectivity
- Need longer execution times

**Steps:**
1. Create a Premium plan
2. Create a new Function App on the Premium plan
3. Deploy your functions to the new app
4. Update any dependencies (connection strings, bindings)
5. Test thoroughly
6. Redirect traffic to new app
7. Delete old Consumption app

### Consumption/Premium → Dedicated

**Reasons to Migrate:**
- Leverage existing App Service infrastructure
- Need always-on capability
- Want predictable costs

**Steps:**
1. Create or identify an existing App Service plan
2. Change the Function App's hosting plan:
   ```bash
   az functionapp update \
     --name MyFunctionApp \
     --resource-group MyResourceGroup \
     --plan MyAppServicePlan
   ```
3. Configure always-on:
   ```bash
   az functionapp config set \
     --name MyFunctionApp \
     --resource-group MyResourceGroup \
     --always-on true
   ```

## Troubleshooting

### Common Issues

**Problem**: Function experiencing cold starts
- **Solution**: Upgrade to Premium plan or enable always-on (Dedicated)

**Problem**: Timeout errors (exceeded 5-10 minutes)
- **Solution**: Upgrade to Premium or Dedicated plan for unlimited duration

**Problem**: Need VNet integration but on Consumption plan
- **Solution**: Migrate to Premium, Dedicated, or ASE plan

**Problem**: High costs on Premium plan with low usage
- **Solution**: Consider downgrading to Consumption plan

**Problem**: Functions not scaling as expected
- **Solution**: Check host.json settings, verify trigger configuration, review scaling metrics

## Additional Resources

- [Compare Azure Functions hosting options - Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Azure Functions pricing](https://azure.microsoft.com/en-us/pricing/details/functions/)
- [Azure Functions best practices](https://learn.microsoft.com/en-us/azure/azure-functions/functions-best-practices)
- [Azure CLI: az functionapp](https://learn.microsoft.com/en-us/cli/azure/functionapp)

## Related Topics

- Azure Functions triggers and bindings
- Application Insights integration
- Durable Functions
- Function App deployment strategies
- Monitoring and diagnostics
