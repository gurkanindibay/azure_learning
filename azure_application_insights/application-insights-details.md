# Application Insights

## Table of Contents

- [Overview](#overview)
  - [What is Application Insights?](#what-is-application-insights)
  - [Key Capabilities](#key-capabilities)
  - [Telemetry Types](#telemetry-types)
  - [How It Works](#how-it-works)
  - [Integration Points](#integration-points)
  - [Pricing Considerations](#pricing-considerations)
- [Question 1: Telemetry Data Types for User Activity Tracking](#question-1-telemetry-data-types-for-user-activity-tracking)
  - [Explanation](#explanation)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect)
  - [Key Takeaway](#key-takeaway)
  - [Related Learning Resources](#related-learning-resources)
- [Question 2: Root Cause Analysis (RCA) for Application Performance](#question-2-root-cause-analysis-rca-for-application-performance)
  - [Explanation](#explanation-1)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-1)
  - [Key Takeaway](#key-takeaway-1)
  - [Application Insights Capabilities for RCA](#application-insights-capabilities-for-rca)
  - [Related Learning Resources](#related-learning-resources-1)
- [Question 3: Multi-Region Monitoring Strategy for Global Expansion](#question-3-multi-region-monitoring-strategy-for-global-expansion)
  - [Explanation](#explanation-2)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-2)
  - [Multi-Region Monitoring Architecture](#multi-region-monitoring-architecture)
  - [Best Practices for Multi-Region Monitoring](#best-practices-for-multi-region-monitoring)
  - [Key Takeaway](#key-takeaway-2)
  - [Related Learning Resources](#related-learning-resources-2)
- [Question 4: Identifying Slow Requests and Dependencies](#question-4-identifying-slow-requests-and-dependencies)
  - [Explanation](#explanation-3)
  - [Why Other Options Are Less Effective](#why-other-options-are-less-effective)
  - [Application Insights Features Comparison for Performance Troubleshooting](#application-insights-features-comparison-for-performance-troubleshooting)
  - [Key Takeaway](#key-takeaway-3)
  - [Related Learning Resources](#related-learning-resources-3)
- [Question 5: Custom Telemetry Correlation Pattern](#question-5-custom-telemetry-correlation-pattern)
  - [Explanation](#explanation-4)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-3)
  - [Operation Correlation Patterns Comparison](#operation-correlation-patterns-comparison)
  - [Key Takeaway](#key-takeaway-4)
  - [Related Learning Resources](#related-learning-resources-4)
- [Question 6: Adaptive Sampling for Telemetry Volume Control](#question-6-adaptive-sampling-for-telemetry-volume-control)
  - [Explanation](#explanation-5)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-4)
  - [Sampling Methods Comparison](#sampling-methods-comparison)
  - [Key Takeaway](#key-takeaway-5)
  - [Related Learning Resources](#related-learning-resources-5)

## Overview**Application Insights** is an extensible Application Performance Management (APM) service for developers and DevOps professionals. It helps you monitor your live applications and automatically detect performance anomalies.

### What is Application Insights?

Application Insights is a feature of Azure Monitor that provides:
- **Real-time application monitoring** and performance management
- **Automatic detection** of performance anomalies
- **Powerful analytics tools** to help diagnose issues and understand user behavior
- Support for multiple platforms: .NET, Node.js, Java, Python, and more
- Integration with popular development tools and CI/CD pipelines

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Availability Monitoring** | Test your endpoints from worldwide locations to ensure uptime |
| **Performance Monitoring** | Track response times, failure rates, and dependencies |
| **Application Map** | Visual topology of application architecture with health indicators |
| **Live Metrics Stream** | Real-time metrics with sub-second latency |
| **Distributed Tracing** | End-to-end transaction tracking across microservices |
| **Smart Detection** | Automatic alerts on abnormal patterns using machine learning |
| **Usage Analytics** | Track user sessions, page views, and custom events |
| **Profiler** | Capture performance traces for production applications |
| **Snapshot Debugger** | Debug exceptions with full application state |

### Telemetry Types

Application Insights collects several types of telemetry:

1. **Requests**: HTTP requests to your application (response time, status codes, URLs)
2. **Dependencies**: Calls to external services (SQL databases, REST APIs, Azure services)
3. **Exceptions**: Unhandled and handled exceptions with stack traces
4. **Events**: Custom events tracking user actions and business logic
5. **Metrics**: Custom numeric measurements (queue lengths, business KPIs)
6. **Traces**: Diagnostic log messages from your application code
7. **Page Views**: Browser-side telemetry for web applications
8. **Availability Results**: Results from availability tests

### How It Works

1. **Instrumentation**: Add Application Insights SDK to your application or enable auto-instrumentation
2. **Collection**: Telemetry data is collected and sent to Azure
3. **Storage**: Data is stored in a Log Analytics workspace
4. **Analysis**: Use Azure Portal, API, or Power BI to analyze data
5. **Alerting**: Configure alerts based on metrics and anomalies

### Integration Points

- **Azure App Service**: One-click enablement without code changes
- **Azure Functions**: Built-in integration for serverless monitoring
- **Kubernetes & Containers**: Support for AKS and containerized applications
- **DevOps**: Integration with Azure DevOps, GitHub Actions, Jenkins
- **Visual Studio**: Real-time debugging and diagnostics during development

### Pricing Considerations

- **Pay-as-you-go**: Based on data volume ingested
- **Daily cap**: Set limits to control costs
- **Data retention**: 90 days included, up to 730 days available
- **Free tier**: 5 GB per month included with Azure subscription

---

## Question 1: Telemetry Data Types for User Activity Tracking

**Scenario:**
You have an Azure App Service web app. You enable Application Insights for the app.

**Requirement:**
You need to view detailed information about each user who signs in to the app, including what the user does while signed in.

**Question:**
Which type of telemetry data should you filter by using Application Insights?

**Options:**

1. **dependencies** ❌ *Incorrect*
2. **events** ✅ *Correct*
3. **requests** ❌ *Incorrect*
4. **traces** ❌ *Incorrect*

### Explanation

**Correct Answer: Events**

The correct solution is to filter by **events**, because Application Insights events are custom telemetry designed to track user actions and behaviors inside the app, such as:
- Button clicks
- Page navigation
- User interactions
- Custom activities performed while signed in

### Why Other Options Are Incorrect

- **Requests**: Represent incoming HTTP calls to the app and provide details about performance and response codes, but they don't capture what a user does within the app.
- **Dependencies**: Track calls to external resources like databases or APIs, not user activities.
- **Traces**: Log diagnostic information from the application, but are not designed for tracking user behavior.

### Key Takeaway

To understand per-user activity inside the application, **events** are the appropriate telemetry type.

### Related Learning Resources
- Implement Application Insights
- Use Azure Application Insights
- Monitor Azure resources with Azure Monitor

---

## Question 2: Root Cause Analysis (RCA) for Application Performance

**Scenario:**
You deploy a web app named App1 by using Azure DevOps. App1 includes releases for a mobile app and a desktop app.

**Requirements:**
You need to perform a root cause analysis (RCA) to monitor the performance of App1. The solution must meet the following requirements:
- Identify related code that causes load
- Ensure that you can view logs and identify any failures that cause issues with the desktop app
- Minimize administrative effort

**Question:**
What should you use?

**Options:**

1. **Application Insights** ✅ *Correct*
2. **Azure Analytics** ❌ *Incorrect*
3. **Azure Monitor** ❌ *Incorrect*
4. **Log Analytics** ❌ *Incorrect*

### Explanation

**Correct Answer: Application Insights**

Application Insights is the correct solution because it is specifically designed to provide:
- **Deep application performance monitoring**
- **Transaction traces** that show the flow of requests through your application
- **Exception logging** with full stack traces
- **Telemetry that links failures directly to code**, making it ideal for root cause analysis
- Support for both **web and desktop components**
- **Easy integration with DevOps pipelines**
- **Minimal setup** once enabled

### Why Other Options Are Incorrect

- **Azure Monitor**: Provides high-level observability across Azure resources but lacks the detailed code-level diagnostics needed for RCA. It's more focused on infrastructure and resource-level metrics.

- **Log Analytics**: Used to query and analyze log data, often from Application Insights or Azure Monitor, but by itself it does not capture application telemetry. It's a query engine, not a telemetry collection service.

- **Azure Analytics**: Not a valid Azure monitoring service.

### Key Takeaway

For **root cause analysis** that requires code-level diagnostics, exception tracking, and performance monitoring with minimal administrative effort, **Application Insights** is the best choice.

### Application Insights Capabilities for RCA

| Capability | Description |
|------------|-------------|
| **Application Map** | Visualize dependencies and identify performance bottlenecks |
| **Transaction Diagnostics** | End-to-end transaction traces across distributed systems |
| **Live Metrics** | Real-time monitoring of application performance |
| **Failure Analysis** | Automatic detection and analysis of exceptions |
| **Profiler** | Identify code that causes high load |
| **Snapshot Debugger** | Capture snapshots when exceptions occur |
| **Usage Analytics** | Track user behavior and application usage patterns |

### Related Learning Resources
- Implement Application Insights
- Monitor Azure resources with Azure Monitor
- Use Azure Application Insights

---

## Question 3: Multi-Region Monitoring Strategy for Global Expansion

**Scenario:**
An e-commerce platform is planning to expand its services globally. The platform is hosted on Azure and utilizes various Azure services and third-party integrations.

**Requirement:**
You need to design and create a robust monitoring solution that can scale with the expansion and provide insights into the performance of the platform across different regions.

**Question:**
What should you do?

**Options:**

1. **Deploy multiple Application Insights instances for each region and use Azure Monitor to aggregate the data** ✅ *Correct*
2. **Implement a single Application Insights instance with default settings to monitor the entire platform** ❌ *Incorrect*
3. **Create web tests and alerts for each region within a single Application Insights instance** ❌ *Incorrect*
4. **Use manual instrumentation to log user activities and store them in Azure Blob Storage for later analysis** ❌ *Incorrect*

### Explanation

**Correct Answer: Deploy multiple Application Insights instances for each region and use Azure Monitor to aggregate the data**

This is the correct solution because it provides:
- **Regional isolation**: Each region has its own Application Insights instance for localized monitoring
- **Performance optimization**: Telemetry data stays close to the source, reducing latency
- **Scalability**: Each instance can scale independently based on regional load
- **Centralized view**: Azure Monitor aggregates data from all instances for global insights
- **Regional compliance**: Data can be stored in specific regions to meet regulatory requirements
- **Resilience**: Regional failures don't affect monitoring in other regions

### Why Other Options Are Incorrect

- **Single Application Insights instance with default settings**: While simpler to set up, this approach:
  - May not scale effectively for high-volume global traffic
  - Creates a single point of failure
  - Doesn't optimize for regional data residency
  - Can introduce latency for geographically distant regions
  - May not meet data sovereignty requirements

- **Web tests and alerts for each region within a single instance**: This approach:
  - Only addresses availability monitoring, not comprehensive application monitoring
  - Doesn't provide the full suite of telemetry (dependencies, exceptions, custom events)
  - Is just one component of a robust monitoring solution
  - Still relies on a single instance with the same scalability limitations

- **Manual instrumentation with Azure Blob Storage**: This approach:
  - Does not provide real-time monitoring capabilities
  - Requires significant custom development and maintenance effort
  - Lacks built-in analytics, alerting, and visualization tools
  - Doesn't offer automatic anomaly detection
  - Misses out on Application Insights' powerful features like Application Map, Live Metrics, and Smart Detection

### Multi-Region Monitoring Architecture

```
Region 1 (East US)          Region 2 (West Europe)       Region 3 (Southeast Asia)
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ App Service      │        │ App Service      │        │ App Service      │
│ Application      │        │ Application      │        │ Application      │
└────────┬─────────┘        └────────┬─────────┘        └────────┬─────────┘
         │                           │                           │
         ▼                           ▼                           ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ App Insights     │        │ App Insights     │        │ App Insights     │
│ Instance 1       │        │ Instance 2       │        │ Instance 3       │
└────────┬─────────┘        └────────┬─────────┘        └────────┬─────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                          ┌──────────────────────┐
                          │   Azure Monitor      │
                          │  (Aggregated View)   │
                          └──────────────────────┘
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                  ┌──────────────┐      ┌──────────────┐
                  │  Dashboards  │      │   Alerts     │
                  └──────────────┘      └──────────────┘
```

### Best Practices for Multi-Region Monitoring

| Practice | Description |
|----------|-------------|
| **Regional Instances** | Deploy Application Insights in each region where your application runs |
| **Consistent Naming** | Use clear naming conventions (e.g., `appinsights-{app}-{region}`) |
| **Shared Workbooks** | Create Azure Monitor Workbooks that query across all instances |
| **Cross-Region Alerts** | Configure alerts that evaluate metrics across multiple regions |
| **Centralized Log Analytics** | Optionally use a shared Log Analytics workspace for centralized querying |
| **Resource Tagging** | Tag resources with region and environment for easier filtering |
| **Performance Baselines** | Establish regional performance baselines to detect anomalies |

### Key Takeaway

For **global, scalable monitoring** of applications across multiple regions, deploy **multiple Application Insights instances** (one per region) and use **Azure Monitor** to aggregate and analyze data centrally. This provides regional optimization with global visibility.

### Related Learning Resources
- Monitor app performance - Training | Microsoft Learn
- Analyze metrics with Azure Monitor metrics explorer - Training | Microsoft Learn
- Implement Application Insights
- Design a distributed monitoring strategy

---

## Question 4: Identifying Slow Requests and Dependencies

**Scenario:**
You are developing an Azure application that uses Azure Application Insights to monitor performance and usage. You want to ensure that you can effectively troubleshoot issues related to the application's performance.

**Question:**
Which of the following features of Azure Application Insights can you use to identify slow requests and dependencies in your application?

**Options:**

1. **Live Metrics Stream** ✅ *Correct*
2. **Application Map** ❌ *Less Effective*
3. **Performance Counters** ❌ *Less Effective*
4. **Analytics Query** ❌ *Less Effective*

### Explanation

**Correct Answer: Live Metrics Stream**

The **Live Metrics Stream** feature in Azure Application Insights allows you to monitor real-time performance data, including slow requests and dependencies. It provides:

- **Live view of key metrics** with sub-second latency
- **Real-time request and dependency tracking** as they happen
- **Instant visibility** into slow requests and failed dependencies
- **Quick identification and troubleshooting** of performance issues as they occur
- **No sampling** - see all requests in real-time
- **Minimal overhead** - designed for production use

**Key Live Metrics Stream Capabilities:**

| Capability | Description |
|------------|-------------|
| **Incoming Requests** | Real-time view of request rate, duration, and failures |
| **Outgoing Dependencies** | Live monitoring of dependency calls and response times |
| **Exceptions** | Immediate visibility into exceptions as they occur |
| **Performance Counters** | CPU, memory, and other system metrics in real-time |
| **Custom Metrics** | Stream custom telemetry data live |
| **Server Selection** | Filter by specific server instances |

### Why Other Options Are Less Effective

- **Application Map**: Provides a visual representation of the components and dependencies of your application. While it can help you understand the overall architecture and identify which components have issues, it may not be the most effective tool for identifying **specific slow requests and dependencies in real-time**. It's better for architectural overview and dependency health at a glance.

- **Performance Counters**: Allow you to track and monitor system-level performance metrics (CPU, memory, I/O, etc.). While they can provide valuable insights into overall system performance, they may not be as effective as other features for identifying **specific slow requests and dependencies** within your application. They're more about infrastructure health than application-level request tracking.

- **Analytics Query**: Allows you to run custom queries on your application's telemetry data using Kusto Query Language (KQL). While it can help you analyze and visualize performance data in great detail, it may not be the most efficient tool for **quickly identifying and troubleshooting slow requests and dependencies in real-time**. It's better for historical analysis and complex investigations.

### Application Insights Features Comparison for Performance Troubleshooting

| Feature | Best For | Real-Time | Granularity | Use Case |
|---------|----------|-----------|-------------|----------|
| **Live Metrics Stream** | Real-time monitoring | ✅ Yes (sub-second) | Request/dependency level | Quick identification of current issues |
| **Application Map** | Architecture overview | ❌ Near real-time | Component level | Understanding dependencies and bottlenecks |
| **Performance Counters** | System health | ✅ Yes | System level | Infrastructure monitoring |
| **Analytics Query** | Historical analysis | ❌ No (query-based) | Any level | Deep investigation and trend analysis |
| **Transaction Search** | Finding specific requests | ❌ No | Individual request | Debugging specific failures |
| **Profiler** | Code-level diagnostics | ❌ Sampled | Method level | Identifying slow code paths |

### Key Takeaway

For **real-time identification of slow requests and dependencies**, **Live Metrics Stream** is the most effective tool because it provides immediate visibility into performance issues as they occur, allowing for quick troubleshooting without delay.

### Related Learning Resources
- Live Metrics: Monitor and diagnose with 1-second latency
- Application Insights overview
- Monitor Azure resources with Azure Monitor

---

## Question 5: Custom Telemetry Correlation Pattern

**Scenario:**
You are implementing custom telemetry in an Application Insights-enabled application. You need to ensure that all telemetry items generated within a specific operation are correlated together.

**Question:**
Which pattern should you use?

**Options:**

1. **`var telemetry = new EventTelemetry("customEvent"); telemetry.Context.Operation.ParentId = HttpContext.TraceIdentifier; telemetryClient.Track(telemetry);`** ❌ *Incorrect*

2. **`using (var operation = telemetryClient.StartOperation<RequestTelemetry>("operationName")) { /* telemetry code */ }`** ✅ *Correct*

3. **`telemetryClient.Context.Operation.Id = Guid.NewGuid().ToString(); telemetryClient.TrackEvent("customEvent");`** ❌ *Incorrect*

4. **`telemetryClient.TrackRequest("requestName", DateTimeOffset.Now, TimeSpan.FromSeconds(1), "200", true);`** ❌ *Incorrect*

### Explanation

**Correct Answer: Using StartOperation Pattern**

```csharp
using (var operation = telemetryClient.StartOperation<RequestTelemetry>("operationName"))
{
    // All telemetry sent within this block will be automatically correlated
    telemetryClient.TrackEvent("customEvent");
    telemetryClient.TrackTrace("Some trace message");
    // ...
}
```

The **StartOperation** pattern is the correct solution because it:

- **Creates an operation context** that automatically correlates all telemetry items sent within the `using` block
- **Ensures all telemetry shares the same operation ID** for proper correlation
- **Properly handles the lifecycle** of the operation (start and end times)
- **Automatically manages parent-child relationships** between telemetry items
- **Follows the recommended pattern** for distributed tracing in Application Insights

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Setting ParentId manually** | Setting `ParentId` manually on individual telemetry items is **error-prone** and doesn't properly establish operation context for automatic correlation of all telemetry within an operation. Each telemetry item would need to be manually configured. |
| **Setting Operation.Id manually** | Manually setting the `Operation.Id` doesn't establish **proper operation context** and doesn't handle the lifecycle of the operation, potentially causing correlation issues. It also doesn't set up the proper parent-child hierarchy. |
| **TrackRequest alone** | `TrackRequest` alone sends request telemetry but **doesn't establish an operation context** for correlating subsequent telemetry items within the same operation. It's just a single telemetry item, not a correlation mechanism. |

### Operation Correlation Patterns Comparison

| Pattern | Automatic Correlation | Lifecycle Management | Error Handling | Recommended |
|---------|----------------------|---------------------|----------------|-------------|
| **StartOperation** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Manual ParentId** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Manual Operation.Id** | ❌ Partial | ❌ No | ❌ No | ❌ No |
| **TrackRequest only** | ❌ No | ❌ No | ❌ No | ❌ No |

### StartOperation Best Practices

```csharp
// Example: Properly correlated custom operation
using (var operation = telemetryClient.StartOperation<RequestTelemetry>("ProcessOrder"))
{
    try
    {
        // All telemetry within this scope is automatically correlated
        telemetryClient.TrackEvent("OrderReceived", new Dictionary<string, string>
        {
            { "OrderId", orderId }
        });

        // Call to external service - dependency is correlated
        await ProcessPaymentAsync(order);

        telemetryClient.TrackEvent("OrderProcessed");
        
        operation.Telemetry.Success = true;
    }
    catch (Exception ex)
    {
        telemetryClient.TrackException(ex);
        operation.Telemetry.Success = false;
        throw;
    }
}
```

### Key Takeaway

For **correlating all telemetry items within a specific operation**, always use the **`StartOperation<T>`** pattern. It provides automatic correlation, proper lifecycle management, and ensures all telemetry items within the scope share the same operation ID for end-to-end tracing.

### Related Learning Resources
- Telemetry correlation in Application Insights
- Custom operations tracking with Application Insights .NET SDK
- Distributed tracing in Application Insights

---

## Question 6: Adaptive Sampling for Telemetry Volume Control

**Scenario:**
You are developing an ASP.NET Core web application that uses Application Insights for monitoring. You need to implement adaptive sampling to control telemetry volume while maintaining statistical accuracy. The sampling should automatically adjust based on the current telemetry rate.

**Question:**
Which code segment should you use?

**Options:**

1. **`services.ConfigureTelemetryModule<AdaptiveSamplingTelemetryProcessor>((module, o) => { module.MaxTelemetryItemsPerSecond = 5; });`** ✅ *Correct*

2. **`services.AddApplicationInsightsTelemetryProcessor<SamplingTelemetryProcessor>(); services.Configure<SamplingTelemetryProcessor>((processor) => { processor.SamplingPercentage = 10; });`** ❌ *Incorrect*

3. **`services.AddSingleton<ITelemetryProcessor, AdaptiveSamplingTelemetryProcessor>(); services.Configure<ApplicationInsightsServiceOptions>((options) => { options.EnableAdaptiveSampling = true; });`** ❌ *Incorrect*

4. **`services.Configure<TelemetryConfiguration>((config) => { config.DefaultTelemetrySink.TelemetryProcessorChainBuilder.UseSampling(10); });`** ❌ *Incorrect*

### Explanation

**Correct Answer: ConfigureTelemetryModule with AdaptiveSamplingTelemetryProcessor**

```csharp
services.ConfigureTelemetryModule<AdaptiveSamplingTelemetryProcessor>((module, o) => 
{ 
    module.MaxTelemetryItemsPerSecond = 5; 
});
```

Configuring the **AdaptiveSamplingTelemetryProcessor** module with the `MaxTelemetryItemsPerSecond` property enables adaptive sampling that:

- **Automatically adjusts the sampling rate** based on the current volume of telemetry
- **Maintains the specified target telemetry volume** (in this case, 5 items per second)
- **Preserves statistical accuracy** by dynamically adapting to traffic patterns
- **Reduces costs** by limiting telemetry volume during high-traffic periods
- **Increases sampling** during low-traffic periods to maintain visibility

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **SamplingTelemetryProcessor with SamplingPercentage** | The `SamplingTelemetryProcessor` implements **fixed-rate sampling** with a static percentage (10% in this case), not adaptive sampling that automatically adjusts based on telemetry volume. |
| **AddSingleton with EnableAdaptiveSampling** | While this attempts to enable adaptive sampling, it **doesn't configure the `MaxTelemetryItemsPerSecond` parameter** required to control the target telemetry volume for adaptive sampling. The configuration is incomplete. |
| **UseSampling(10) on TelemetryProcessorChainBuilder** | The `UseSampling` method configures **fixed-rate sampling** with a static percentage (10%), not adaptive sampling that automatically adjusts the sampling rate based on telemetry volume. |

### Sampling Methods Comparison

| Sampling Method | Type | Adjustment | Configuration | Best For |
|-----------------|------|------------|---------------|----------|
| **Adaptive Sampling** | Dynamic | Automatic based on volume | `MaxTelemetryItemsPerSecond` | Variable traffic patterns |
| **Fixed-Rate Sampling** | Static | Manual percentage | `SamplingPercentage` | Consistent traffic patterns |
| **Ingestion Sampling** | Server-side | Azure Portal | Percentage in portal | Post-collection filtering |

### Adaptive Sampling Configuration Best Practices

```csharp
// Recommended configuration for adaptive sampling
services.ConfigureTelemetryModule<AdaptiveSamplingTelemetryProcessor>((module, o) => 
{ 
    // Target telemetry items per second
    module.MaxTelemetryItemsPerSecond = 5;
    
    // Optional: Exclude certain telemetry types from sampling
    module.ExcludedTypes = "Event;Exception";
    
    // Optional: Include only specific telemetry types for sampling
    // module.IncludedTypes = "Request;Dependency";
});
```

**Key Configuration Options:**

| Property | Description | Default |
|----------|-------------|---------|
| `MaxTelemetryItemsPerSecond` | Target rate for adaptive sampling algorithm | 5 |
| `ExcludedTypes` | Telemetry types to exclude from sampling | None |
| `IncludedTypes` | Telemetry types to include in sampling | All |
| `MinSamplingPercentage` | Minimum sampling percentage floor | 0.1% |
| `MaxSamplingPercentage` | Maximum sampling percentage ceiling | 100% |

### Key Takeaway

For **adaptive sampling** that automatically adjusts based on telemetry volume while maintaining statistical accuracy, use **`ConfigureTelemetryModule<AdaptiveSamplingTelemetryProcessor>`** with the `MaxTelemetryItemsPerSecond` property. This is the proper way to implement dynamic sampling in ASP.NET Core applications with Application Insights.

### Related Learning Resources
- Sampling in Application Insights
- Configure adaptive sampling for ASP.NET Core applications
- Application Insights for ASP.NET Core applications
