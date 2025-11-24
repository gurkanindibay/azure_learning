# Application Insights - Exam Questions

## Overview

**Application Insights** is an extensible Application Performance Management (APM) service for developers and DevOps professionals. It helps you monitor your live applications and automatically detect performance anomalies.

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
