# E-Commerce Platform Monitoring & Observability Scenario

## Table of Contents

- [Scenario Overview](#scenario-overview)
- [Business Context](#business-context)
- [Architecture](#architecture)
- [Phase 1: Initial Setup and Basic Monitoring](#phase-1-initial-setup-and-basic-monitoring)
- [Phase 2: Performance Monitoring and Optimization](#phase-2-performance-monitoring-and-optimization)
- [Phase 3: Distributed Tracing and Dependency Tracking](#phase-3-distributed-tracing-and-dependency-tracking)
- [Phase 4: User Experience and Business Analytics](#phase-4-user-experience-and-business-analytics)
- [Phase 5: Proactive Alerting and Incident Response](#phase-5-proactive-alerting-and-incident-response)
- [Phase 6: Advanced Diagnostics and Troubleshooting](#phase-6-advanced-diagnostics-and-troubleshooting)
- [Phase 7: Custom Metrics and Business KPIs](#phase-7-custom-metrics-and-business-kpis)
- [Phase 8: Security and Compliance Monitoring](#phase-8-security-and-compliance-monitoring)
- [Phase 9: Cost Optimization and Data Management](#phase-9-cost-optimization-and-data-management)
- [Complete Monitoring Dashboard Setup](#complete-monitoring-dashboard-setup)
- [Key Takeaways](#key-takeaways)

## Scenario Overview

**Company**: GlobalMart - An international e-commerce platform
**Challenge**: Experiencing intermittent performance issues, customer complaints about checkout failures, and lack of visibility into system health across multiple Azure services.

**Goal**: Implement comprehensive monitoring and observability using Azure Monitor and Application Insights to achieve:
- 99.9% uptime
- Sub-second page load times
- Proactive issue detection
- Complete distributed tracing
- Business intelligence from telemetry data

## Business Context

### Current Infrastructure
- **Frontend**: React SPA hosted on Azure Static Web Apps
- **API Layer**: .NET 8 Web API on Azure App Service (3 instances)
- **Order Processing**: Azure Functions (Consumption Plan)
- **Data Storage**: Azure Cosmos DB, Azure SQL Database, Azure Blob Storage
- **Cache**: Azure Redis Cache
- **Messaging**: Azure Service Bus
- **Authentication**: Azure AD B2C with Microsoft Graph API integration

### Pain Points
1. Customers report slow checkout during peak hours (Black Friday approaching)
2. Payment processing failures without clear root cause
3. Database queries timing out intermittently
4. No visibility into cross-service request flows
5. Manual log searching across multiple services

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Azure Monitor Ecosystem                      │
│                                                                   │
│  ┌──────────────────────┐        ┌────────────────────────┐     │
│  │ Application Insights │◄───────┤ Log Analytics Workspace│     │
│  └──────────────────────┘        └────────────────────────┘     │
│                                                                   │
│  Data Sources:                                                   │
│  • React SPA                    • Azure Functions                │
│  • .NET Web API                 • Cosmos DB                      │
│  • Azure Service Bus            • Azure Redis Cache             │
│  • Azure SQL Database           • Azure App Service             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Initial Setup and Basic Monitoring

### Step 1.1: Create Application Insights Resource

**Azure Monitor Tool Used**: Application Insights

```bash
# Create Resource Group
az group create --name rg-globalmart-monitoring --location eastus

# Create Log Analytics Workspace (foundation for Application Insights)
az monitor log-analytics workspace create \
  --resource-group rg-globalmart-monitoring \
  --workspace-name law-globalmart-prod \
  --location eastus \
  --sku PerGB2018

# Create Application Insights instance (workspace-based)
az monitor app-insights component create \
  --app globalmart-appinsights \
  --location eastus \
  --resource-group rg-globalmart-monitoring \
  --workspace /subscriptions/{subscription-id}/resourceGroups/rg-globalmart-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-globalmart-prod
```

**Why This Matters**: Workspace-based Application Insights enables:
- Unified data storage with other Azure Monitor data
- Cross-resource queries
- Centralized access control via Log Analytics workspace
- Better data retention management

### Step 1.2: Instrument the .NET Web API

**Azure Monitor Tool Used**: Application Insights SDK

```csharp
// Program.cs
using Microsoft.ApplicationInsights.AspNetCore.Extensions;
using Microsoft.ApplicationInsights.Extensibility;

var builder = WebApplication.CreateBuilder(args);

// Add Application Insights telemetry
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = builder.Configuration["ApplicationInsights:ConnectionString"];
    options.EnableAdaptiveSampling = true;
    options.EnableQuickPulseMetricStream = true; // Live Metrics
    options.EnableDependencyTrackingTelemetryModule = true;
    options.EnableRequestTrackingTelemetryModule = true;
});

// Configure telemetry processors
builder.Services.AddApplicationInsightsTelemetryProcessor<FilterSensitiveDataProcessor>();
builder.Services.AddApplicationInsightsTelemetryProcessor<EnrichWithBusinessContextProcessor>();

var app = builder.Build();
app.Run();
```

**Telemetry Collected Automatically**:
- ✅ HTTP requests (duration, status codes, URLs)
- ✅ Dependencies (SQL, HTTP calls, Redis)
- ✅ Exceptions with stack traces
- ✅ Performance counters

### Step 1.3: Enable Diagnostic Settings for Azure Services

**Azure Monitor Tool Used**: Diagnostic Settings

```bash
# Enable diagnostics for App Service
az monitor diagnostic-settings create \
  --resource /subscriptions/{sub-id}/resourceGroups/rg-globalmart/providers/Microsoft.Web/sites/globalmart-api \
  --name "Send-to-AppInsights" \
  --workspace /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-globalmart-prod \
  --logs '[{"category":"AppServiceHTTPLogs","enabled":true},{"category":"AppServiceConsoleLogs","enabled":true},{"category":"AppServiceAppLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'

# Enable diagnostics for Cosmos DB
az monitor diagnostic-settings create \
  --resource /subscriptions/{sub-id}/resourceGroups/rg-globalmart/providers/Microsoft.DocumentDB/databaseAccounts/globalmart-cosmosdb \
  --name "Send-to-LAW" \
  --workspace /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/Microsoft.OperationalInsights/workspaces/law-globalmart-prod \
  --logs '[{"category":"DataPlaneRequests","enabled":true},{"category":"QueryRuntimeStatistics","enabled":true}]' \
  --metrics '[{"category":"Requests","enabled":true}]'
```

### Step 1.4: View Basic Metrics

**Azure Monitor Tool Used**: Metrics Explorer

Navigate to Azure Portal → Application Insights → Metrics:
- **Server response time**: Avg, P95, P99
- **Server requests**: Count, failed request rate
- **Dependency calls**: Duration, failure rate
- **Exceptions**: Count by type

**First Win**: Team can now see that average response time is 1.2s during peak hours (target: <500ms).

---

## Phase 2: Performance Monitoring and Optimization

### Step 2.1: Analyze Performance with Application Insights Performance Blade

**Azure Monitor Tool Used**: Performance Blade

Navigate to: Application Insights → Performance

**What to Look For**:
1. **Operations Tab**: Shows all HTTP endpoints sorted by average duration
2. **Dependencies Tab**: External calls (SQL, Redis, HTTP APIs)
3. **Operation Details**: Drill into specific slow requests

**Discovery**: The `/api/products/search` endpoint has P95 response time of 3.2s.

### Step 2.2: Identify Slow Dependencies

**Azure Monitor Tool Used**: KQL Query in Log Analytics

```kusto
// Find slowest dependencies in the last 24 hours
dependencies
| where timestamp > ago(24h)
| where duration > 1000  // Slower than 1 second
| summarize 
    Count = count(),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95),
    P99Duration = percentile(duration, 99)
    by type, target, name
| order by P95Duration desc
| top 20 by Count
```

**Result**:
```
type          | target                    | name                  | Count | P95Duration
SQL           | globalmart-sqldb          | SELECT * FROM Products| 1,247 | 2,847ms
HTTP          | api.paymentgateway.com    | POST /process         | 89    | 4,123ms
Azure Cache   | globalmart-redis          | GET product:*         | 3,456 | 156ms
```

**Insight**: SQL query without proper indexing is the bottleneck.

### Step 2.3: Use Transaction Search for Deep Dive

**Azure Monitor Tool Used**: Transaction Search (End-to-End Transaction Details)

Navigate to: Application Insights → Transaction Search

Filter by:
- Operation name: `GET /api/products/search`
- Duration > 2000ms

**Sample Transaction Timeline**:
```
Request: GET /api/products/search?q=laptop        [3.2s total]
  ├─ Dependency: Redis GET search:laptop          [45ms] ✓
  ├─ Dependency: SQL SELECT FROM Products         [2.9s] ✗ SLOW
  └─ Dependency: Redis SET search:laptop          [38ms] ✓
```

### Step 2.4: Analyze SQL Performance with Query Performance Insight

**Azure Monitor Tool Used**: Azure SQL Analytics + Query Performance Insight

```kusto
// Query from Log Analytics for SQL insights
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.SQL"
| where Category == "QueryStoreRuntimeStatistics"
| where query_hash_s == "0x8B7A4F2C1D"  // Problem query hash
| summarize 
    TotalExecutions = sum(count_executions_d),
    AvgDuration = avg(avg_duration_d),
    MaxDuration = max(max_duration_d)
    by query_id_d
| order by AvgDuration desc
```

**Resolution**: Added index on `Products.SearchVector` column, reducing query time from 2.9s to 120ms.

### Step 2.5: Monitor the Fix with Metrics

**Azure Monitor Tool Used**: Metrics with Annotations

```bash
# Add annotation to mark the deployment
az monitor app-insights events create \
  --app globalmart-appinsights \
  --resource-group rg-globalmart-monitoring \
  --type Annotation \
  --properties '{"AnnotationName":"Added Product Index","Category":"Deployment","EventTime":"2025-12-10T14:30:00Z"}'
```

**Verification Query**:
```kusto
requests
| where timestamp > ago(2h)
| where name == "GET /api/products/search"
| summarize P95 = percentile(duration, 95) by bin(timestamp, 5m)
| render timechart
```

**Result**: P95 response time dropped from 3.2s to 380ms ✅

---

## Phase 3: Distributed Tracing and Dependency Tracking

### Step 3.1: Enable Distributed Tracing Across Services

**Azure Monitor Tool Used**: Distributed Tracing with Operation ID Correlation

```csharp
// Configure correlation in API Gateway
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.EnableDependencyTrackingTelemetryModule = true;
    options.DependencyCollectionOptions.EnableLegacyCorrelationHeadersInjection = true;
});

// Custom telemetry initializer for business context
public class BusinessContextInitializer : ITelemetryInitializer
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public BusinessContextInitializer(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public void Initialize(ITelemetry telemetry)
    {
        var context = _httpContextAccessor.HttpContext;
        if (context != null)
        {
            telemetry.Context.GlobalProperties["UserId"] = context.User?.FindFirst("sub")?.Value;
            telemetry.Context.GlobalProperties["SessionId"] = context.Session?.Id;
            telemetry.Context.GlobalProperties["UserRole"] = context.User?.FindFirst("role")?.Value;
            telemetry.Context.Cloud.RoleName = "API-Gateway";
        }
    }
}
```

### Step 3.2: Instrument Azure Functions

**Azure Monitor Tool Used**: Application Insights for Azure Functions

```csharp
// OrderProcessingFunction.cs
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.DataContracts;

public class OrderProcessingFunction
{
    private readonly TelemetryClient _telemetryClient;

    public OrderProcessingFunction(TelemetryClient telemetryClient)
    {
        _telemetryClient = telemetryClient;
    }

    [Function("ProcessOrder")]
    public async Task Run(
        [ServiceBusTrigger("orders", Connection = "ServiceBusConnection")] 
        string orderMessage)
    {
        using var operation = _telemetryClient.StartOperation<RequestTelemetry>("ProcessOrder");
        
        try
        {
            var order = JsonSerializer.Deserialize<Order>(orderMessage);
            
            // Track custom event
            _telemetryClient.TrackEvent("OrderReceived", new Dictionary<string, string>
            {
                { "OrderId", order.Id },
                { "TotalAmount", order.Total.ToString() },
                { "ItemCount", order.Items.Count.ToString() }
            });

            // Validate inventory (tracked as dependency automatically)
            await ValidateInventory(order);
            
            // Process payment
            var paymentResult = await ProcessPayment(order);
            
            // Track custom metric
            _telemetryClient.TrackMetric("OrderValue", order.Total);
            
            operation.Telemetry.Success = true;
        }
        catch (Exception ex)
        {
            _telemetryClient.TrackException(ex);
            operation.Telemetry.Success = false;
            throw;
        }
    }
}
```

### Step 3.3: Visualize End-to-End Transactions with Application Map

**Azure Monitor Tool Used**: Application Map

Navigate to: Application Insights → Application Map

**What You See**:
```
┌──────────────┐      ┌─────────────┐      ┌──────────────────┐
│ React SPA    │─────►│  API Gateway│─────►│ Order Function   │
│ (Browser)    │ 2.4s │  (App Svc)  │ 1.8s │ (Functions)      │
└──────────────┘      └─────────────┘      └──────────────────┘
                              │                      │
                              │                      ▼
                              │              ┌──────────────┐
                              │              │ Service Bus  │
                              │              └──────────────┘
                              ▼
                      ┌─────────────┐       ┌──────────────┐
                      │ Cosmos DB   │       │ Redis Cache  │
                      │ (450ms avg) │       │ (12ms avg)   │
                      └─────────────┘       └──────────────┘
```

**Health Indicators on Map**:
- 🟢 Green: Healthy (success rate > 95%)
- 🟡 Yellow: Degraded (success rate 90-95%)
- 🔴 Red: Unhealthy (success rate < 90%)

### Step 3.4: Track Cross-Service Requests with Operation ID

**Azure Monitor Tool Used**: KQL Correlation Queries

```kusto
// Find all telemetry for a specific user transaction
let operationId = "abc123xyz";
union requests, dependencies, exceptions, traces
| where operation_Id == operationId
| project 
    timestamp,
    itemType,
    name,
    duration,
    success,
    resultCode,
    cloud_RoleName,
    operation_ParentId
| order by timestamp asc
```

**Result Shows Complete Flow**:
```
timestamp            | itemType   | name                    | duration | cloud_RoleName
2025-12-10 10:15:00  | request    | POST /api/orders        | 2340ms   | API-Gateway
2025-12-10 10:15:00  | dependency | POST https://payment... | 1850ms   | API-Gateway
2025-12-10 10:15:01  | request    | ProcessOrder            | 1200ms   | Order-Function
2025-12-10 10:15:01  | dependency | Cosmos DB Insert        | 450ms    | Order-Function
2025-12-10 10:15:01  | dependency | Service Bus Send        | 85ms     | Order-Function
```

---

## Phase 4: User Experience and Business Analytics

### Step 4.1: Track Custom Events for Business Metrics

**Azure Monitor Tool Used**: Custom Events Tracking

```csharp
public class CheckoutController : ControllerBase
{
    private readonly TelemetryClient _telemetryClient;

    [HttpPost("checkout")]
    public async Task<IActionResult> Checkout(CheckoutRequest request)
    {
        var properties = new Dictionary<string, string>
        {
            { "PaymentMethod", request.PaymentMethod },
            { "ShippingRegion", request.ShippingAddress.Country },
            { "UserSegment", await GetUserSegment(request.UserId) }
        };

        var measurements = new Dictionary<string, double>
        {
            { "CartValue", request.TotalAmount },
            { "ItemCount", request.Items.Count },
            { "DiscountApplied", request.DiscountAmount }
        };

        _telemetryClient.TrackEvent("CheckoutCompleted", properties, measurements);

        return Ok();
    }
}
```

### Step 4.2: Create Business Dashboards with Workbooks

**Azure Monitor Tool Used**: Azure Workbooks

Navigate to: Application Insights → Workbooks → New

**Workbook Configuration**:

```kusto
// Sales Performance Dashboard
customEvents
| where name == "CheckoutCompleted"
| where timestamp > ago(7d)
| extend CartValue = todouble(customMeasurements.CartValue)
| summarize 
    TotalRevenue = sum(CartValue),
    OrderCount = count(),
    AvgOrderValue = avg(CartValue)
    by bin(timestamp, 1h), Region = tostring(customDimensions.ShippingRegion)
| render timechart
```

```kusto
// Conversion Funnel
let timeframe = ago(24h);
let step1 = customEvents | where timestamp > timeframe and name == "ProductViewed" | count;
let step2 = customEvents | where timestamp > timeframe and name == "AddedToCart" | count;
let step3 = customEvents | where timestamp > timeframe and name == "CheckoutStarted" | count;
let step4 = customEvents | where timestamp > timeframe and name == "CheckoutCompleted" | count;
print 
    ProductViews = step1,
    AddToCart = step2,
    CheckoutStarted = step3,
    CheckoutCompleted = step4
| extend 
    ConversionRate1 = (todouble(AddToCart) / ProductViews) * 100,
    ConversionRate2 = (todouble(CheckoutStarted) / AddToCart) * 100,
    ConversionRate3 = (todouble(CheckoutCompleted) / CheckoutStarted) * 100
```

### Step 4.3: Monitor Real User Experience with Browser Telemetry

**Azure Monitor Tool Used**: Browser SDK

```javascript
// React App - index.tsx
import { ApplicationInsights } from '@microsoft/applicationinsights-web';
import { ReactPlugin } from '@microsoft/applicationinsights-react-js';

const reactPlugin = new ReactPlugin();
const appInsights = new ApplicationInsights({
    config: {
        connectionString: 'InstrumentationKey=...',
        extensions: [reactPlugin],
        enableAutoRouteTracking: true,
        enableCorsCorrelation: true,
        enableRequestHeaderTracking: true,
        enableResponseHeaderTracking: true,
        correlationHeaderExcludedDomains: ['*.queue.core.windows.net']
    }
});

appInsights.loadAppInsights();
appInsights.trackPageView();

// Track user interactions
appInsights.trackEvent('ProductSearch', { 
    searchTerm: searchQuery,
    resultsCount: products.length 
});

// Track errors
window.addEventListener('error', (event) => {
    appInsights.trackException({ 
        error: event.error,
        severityLevel: SeverityLevel.Error 
    });
});
```

### Step 4.4: Analyze User Behavior with Usage Analysis

**Azure Monitor Tool Used**: Usage Blade (Users, Sessions, Events)

Navigate to: Application Insights → Usage → Users

**Query for User Journey Analysis**:
```kusto
pageViews
| where timestamp > ago(7d)
| where client_Type == "Browser"
| extend SessionId = session_Id
| project timestamp, SessionId, name, url, duration
| join kind=inner (
    customEvents
    | where timestamp > ago(7d)
    | where name in ("AddedToCart", "CheckoutCompleted")
    | project SessionId = session_Id, EventName = name, EventTime = timestamp
) on SessionId
| summarize 
    PageViewCount = count(),
    Events = make_set(EventName),
    SessionDuration = max(duration)
    by SessionId
| where array_length(Events) > 0
```

**Insights Discovered**:
- Users who view >3 product pages have 45% higher checkout completion
- Mobile users abandon cart 2x more often (performance issue on mobile)
- Sessions from paid ads have 3x higher bounce rate

---

## Phase 5: Proactive Alerting and Incident Response

### Step 5.1: Create Smart Detection Rules

**Azure Monitor Tool Used**: Smart Detection

Application Insights automatically enables Smart Detection for:
- ✅ Failure anomalies (sudden spike in failures)
- ✅ Performance degradation
- ✅ Memory leak detection
- ✅ Security detection (slow page loads due to attacks)

**Configure Custom Smart Detection**:
```bash
az monitor app-insights component update \
  --app globalmart-appinsights \
  --resource-group rg-globalmart-monitoring \
  --query-pack-query-id "SmartDetection/FailureAnomalies"
```

### Step 5.2: Set Up Metric Alerts

**Azure Monitor Tool Used**: Metric Alerts

```bash
# Alert on high API response time
az monitor metrics alert create \
  --name "High API Response Time" \
  --resource-group rg-globalmart-monitoring \
  --scopes /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/components/globalmart-appinsights \
  --condition "avg requests/duration > 1000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group-ids /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/actionGroups/ops-team \
  --description "Triggered when average response time exceeds 1 second"

# Alert on high failure rate
az monitor metrics alert create \
  --name "High Failure Rate" \
  --resource-group rg-globalmart-monitoring \
  --scopes /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/components/globalmart-appinsights \
  --condition "avg requests/failed > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action-group-ids /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/actionGroups/ops-team
```

### Step 5.3: Create Log Query Alerts for Complex Scenarios

**Azure Monitor Tool Used**: Log Query Alerts

```bash
# Create alert for payment failures
az monitor scheduled-query create \
  --name "Payment Processing Failures" \
  --resource-group rg-globalmart-monitoring \
  --scopes /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/components/globalmart-appinsights \
  --condition "count > 10" \
  --condition-query "exceptions | where outerMessage contains 'PaymentGatewayException' | where timestamp > ago(5m) | count" \
  --description "Alert when payment processing failures exceed threshold" \
  --evaluation-frequency 5m \
  --window-size 5m \
  --action-groups /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/actionGroups/ops-team \
  --severity 1
```

**Advanced Alert Query Example**:
```kusto
// Alert when checkout abandonment rate is abnormally high
let checkoutStarted = customEvents
    | where timestamp > ago(15m)
    | where name == "CheckoutStarted"
    | count;
let checkoutCompleted = customEvents
    | where timestamp > ago(15m)
    | where name == "CheckoutCompleted"
    | count;
let abandonmentRate = (todouble(checkoutStarted - checkoutCompleted) / checkoutStarted) * 100;
print AbandonmentRate = abandonmentRate
| where AbandonmentRate > 30  // Alert if >30% abandonment
```

### Step 5.4: Configure Action Groups for Incident Response

**Azure Monitor Tool Used**: Action Groups

```bash
az monitor action-group create \
  --name ops-team \
  --resource-group rg-globalmart-monitoring \
  --short-name OpsTeam \
  --email-receiver name="oncall-email" email="ops@globalmart.com" \
  --sms-receiver name="oncall-sms" country-code="1" phone-number="5551234567" \
  --webhook-receiver name="slack-webhook" service-uri="https://hooks.slack.com/services/..." \
  --azure-function name="auto-remediation" function-app-resource-id="/subscriptions/{sub-id}/resourceGroups/rg-globalmart/providers/Microsoft.Web/sites/remediation-functions" function-name="ScaleUp"
```

### Step 5.5: Implement Availability Tests

**Azure Monitor Tool Used**: Availability Tests (Standard & Multi-Step)

```bash
# Create URL ping test
az monitor app-insights web-test create \
  --resource-group rg-globalmart-monitoring \
  --name "Homepage Availability" \
  --location "East US" \
  --kind "ping" \
  --web-test "<WebTest><Items><Request><Url>https://www.globalmart.com</Url></Request></Items></WebTest>" \
  --frequency 300 \
  --timeout 120 \
  --enabled true \
  --locations "us-east-1" "eu-west-1" "asia-southeast-1" \
  --app-insights /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/microsoft.insights/components/globalmart-appinsights
```

**Multi-Step Availability Test** (Portal UI):
1. Visit homepage
2. Search for product
3. Add to cart
4. Proceed to checkout
5. Verify checkout page loads

**Alert Configuration**: Trigger if availability drops below 99% in any region.

---

## Phase 6: Advanced Diagnostics and Troubleshooting

### Step 6.1: Use Live Metrics Stream for Real-Time Monitoring

**Azure Monitor Tool Used**: Live Metrics Stream

Navigate to: Application Insights → Live Metrics

**Real-Time Visibility**:
- Incoming request rate per second
- Outgoing dependency calls per second
- Overall health (CPU, memory, exceptions)
- Sample telemetry (requests, dependencies, exceptions)
- Custom filters to focus on specific servers or operations

**Use Case**: During Black Friday deployment, watch live metrics to ensure no spike in errors.

### Step 6.2: Analyze Failures with Failures Blade

**Azure Monitor Tool Used**: Failures Blade

Navigate to: Application Insights → Failures

**Three Tabs**:
1. **Operations**: Failed requests grouped by endpoint
2. **Dependencies**: Failed external calls grouped by target
3. **Exceptions**: All exceptions with stack traces

**Sample Investigation**:
```
Exception: System.TimeoutException in OrderController.CreateOrder
Count: 47 in last hour
Top Affected Operations: POST /api/orders

Stack Trace:
  at GlobalMart.Services.PaymentService.ProcessPayment()
  at GlobalMart.Controllers.OrderController.CreateOrder()
  
Associated Dependencies:
  POST https://api.paymentgateway.com/process (timeout after 30s)
```

### Step 6.3: Debug with Snapshot Debugger

**Azure Monitor Tool Used**: Snapshot Debugger

```csharp
// Enable in application
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.EnableSnapshotDebugger = true;
});
```

**Portal Configuration**:
1. Navigate to: Application Insights → Snapshot Debugger
2. Exceptions list shows snapshots
3. Click "Open Debug Snapshot" to see full variable state at exception time

**What You Get**:
- Complete call stack
- Local variables
- Request parameters
- Exception details

**Discovered Issue**: Payment gateway timeout occurs when `retryAttempts` variable is set to 1 instead of 3 (configuration error).

### Step 6.4: Profiling with Application Insights Profiler

**Azure Monitor Tool Used**: Application Insights Profiler

```bash
# Enable profiler for App Service
az webapp config appsettings set \
  --resource-group rg-globalmart \
  --name globalmart-api \
  --settings APPINSIGHTS_PROFILERFEATURE_VERSION=1.0.0
```

Navigate to: Application Insights → Performance → Profiler traces

**Profiler Shows**:
```
Method                              | Inclusive Time | Exclusive Time
------------------------------------|----------------|---------------
OrderController.CreateOrder()       | 2,847ms        | 45ms
  └─ PaymentService.Validate()      | 2,802ms        | 2,802ms ⚠️
      └─ Regex.Match() [BOTTLENECK] | 2,750ms        | 2,750ms
```

**Resolution**: Replace complex regex validation with simpler string checks, reducing validation time from 2.75s to 8ms.

### Step 6.5: Search and Filter with Transaction Search

**Azure Monitor Tool Used**: Transaction Search with Advanced Filters

```kusto
// Find all failed requests from mobile clients in the past hour
requests
| where timestamp > ago(1h)
| where success == false
| where client_Type == "Phone"
| extend 
    OS = client_OS,
    Browser = client_Browser,
    City = client_City
| summarize 
    FailureCount = count(),
    UniqueUsers = dcount(user_Id),
    AvgDuration = avg(duration)
    by OS, resultCode
| order by FailureCount desc
```

**Result**:
```
OS      | resultCode | FailureCount | UniqueUsers | AvgDuration
iOS     | 504        | 127          | 89          | 30,000ms
Android | 504        | 94           | 67          | 30,000ms
```

**Insight**: Gateway timeout on mobile specifically due to slow image loading API.

---

## Phase 7: Custom Metrics and Business KPIs

### Step 7.1: Track Custom Metrics for Business KPIs

**Azure Monitor Tool Used**: Custom Metrics API

```csharp
public class InventoryService
{
    private readonly TelemetryClient _telemetryClient;

    public async Task UpdateInventory(string productId, int quantity)
    {
        // Track inventory levels
        _telemetryClient.GetMetric("InventoryLevel", "ProductId")
            .TrackValue(quantity, productId);

        // Track inventory turnover
        if (quantity < 10)
        {
            _telemetryClient.GetMetric("LowStockAlerts", "ProductId")
                .TrackValue(1, productId);
        }

        // Track custom dimensions
        var metric = _telemetryClient.GetMetric(
            new MetricIdentifier("Inventory", "Update", "Warehouse", "Category")
        );
        metric.TrackValue(quantity, warehouse: "US-East", category: "Electronics");
    }
}
```

### Step 7.2: Query Custom Metrics

**Azure Monitor Tool Used**: Metrics Explorer + KQL

```kusto
// Custom metrics in Log Analytics
customMetrics
| where name == "InventoryLevel"
| where timestamp > ago(24h)
| extend ProductId = tostring(customDimensions.ProductId)
| summarize 
    CurrentLevel = max(value),
    MinLevel = min(value),
    AvgLevel = avg(value)
    by ProductId
| where CurrentLevel < 50  // Low inventory alert
| order by CurrentLevel asc
```

### Step 7.3: Create Business Health Score

**Azure Monitor Tool Used**: Custom KQL Function

```kusto
// Create function to calculate health score
.create-or-alter function BusinessHealthScore() {
    let availability = requests
        | where timestamp > ago(5m)
        | summarize SuccessRate = 100.0 * countif(success == true) / count();
    
    let performance = requests
        | where timestamp > ago(5m)
        | summarize PerformanceScore = 100.0 - (avg(duration) / 50.0);  // 5000ms = 0 score
    
    let errorRate = exceptions
        | where timestamp > ago(5m)
        | summarize ErrorCount = count();
    
    availability
    | extend Performance = toscalar(performance)
    | extend Errors = toscalar(errorRate)
    | extend HealthScore = (SuccessRate * 0.5) + (Performance * 0.3) + (iff(Errors < 10, 100, 100 - Errors) * 0.2)
    | project HealthScore, SuccessRate, Performance, Errors
}

// Use the function
BusinessHealthScore()
| project HealthScore = round(HealthScore, 2)
```

### Step 7.4: Track Revenue Impact with Telemetry

**Azure Monitor Tool Used**: Custom Events with Measurements

```csharp
public class AnalyticsMiddleware
{
    public async Task InvokeAsync(HttpContext context)
    {
        var stopwatch = Stopwatch.StartNew();
        
        await _next(context);
        
        stopwatch.Stop();

        if (context.Response.StatusCode == 200 && 
            context.Request.Path.StartsWithSegments("/api/orders"))
        {
            var orderValue = GetOrderValueFromResponse(context);
            
            _telemetryClient.TrackEvent("OrderCompleted", 
                properties: new Dictionary<string, string>
                {
                    { "UserId", context.User.FindFirst("sub")?.Value },
                    { "Channel", context.Request.Headers["X-Channel"] },
                    { "Region", GetUserRegion(context) }
                },
                measurements: new Dictionary<string, double>
                {
                    { "Revenue", orderValue },
                    { "ResponseTime", stopwatch.ElapsedMilliseconds }
                });
        }
    }
}
```

**Business Dashboard Query**:
```kusto
customEvents
| where name == "OrderCompleted"
| where timestamp > ago(7d)
| extend Revenue = todouble(customMeasurements.Revenue)
| extend ResponseTime = todouble(customMeasurements.ResponseTime)
| summarize 
    TotalRevenue = sum(Revenue),
    OrderCount = count(),
    AvgResponseTime = avg(ResponseTime),
    RevenueByLatency = sumif(Revenue, ResponseTime < 500)
    by bin(timestamp, 1h)
| extend FastCheckoutRevenue = RevenueByLatency / TotalRevenue * 100
| render timechart
```

---

## Phase 8: Security and Compliance Monitoring

### Step 8.1: Monitor Authentication Failures

**Azure Monitor Tool Used**: KQL with Azure AD Logs

```kusto
// Failed authentication attempts
requests
| where timestamp > ago(24h)
| where resultCode in (401, 403)
| extend 
    IPAddress = client_IP,
    UserAgent = client_Browser
| summarize 
    FailedAttempts = count(),
    UniqueIPs = dcount(client_IP)
    by user_AuthenticatedId
| where FailedAttempts > 10  // Potential brute force
| order by FailedAttempts desc
```

### Step 8.2: Track Sensitive Data Access

**Azure Monitor Tool Used**: Custom Events for Audit Trail

```csharp
public class AuditTelemetryProcessor : ITelemetryProcessor
{
    public void Process(ITelemetry item)
    {
        if (item is RequestTelemetry request)
        {
            // Redact sensitive query parameters
            request.Url = RedactSensitiveData(request.Url);
            
            // Track PII access
            if (request.Name.Contains("/api/users/personal-info"))
            {
                request.Properties["DataClassification"] = "PII";
                request.Properties["AccessJustification"] = 
                    request.Context.User.AuthenticatedUserId;
            }
        }
        
        _next.Process(item);
    }
}
```

### Step 8.3: Monitor for Security Anomalies

**Azure Monitor Tool Used**: Log Analytics Alert Rules

```kusto
// Detect unusual geographic access patterns
requests
| where timestamp > ago(1h)
| where user_AuthenticatedId != ""
| extend City = client_City, Country = client_CountryOrRegion
| summarize Cities = make_set(City), Countries = make_set(Country) by user_AuthenticatedId
| where array_length(Countries) > 2  // User from multiple countries in 1 hour
| project user_AuthenticatedId, Cities, Countries
```

### Step 8.4: Compliance Reporting with Log Retention

**Azure Monitor Tool Used**: Log Analytics Workspace Data Retention

```bash
# Set retention for compliance (e.g., GDPR requires 90 days)
az monitor log-analytics workspace update \
  --resource-group rg-globalmart-monitoring \
  --workspace-name law-globalmart-prod \
  --retention-time 90

# Export logs for long-term storage
az monitor log-analytics workspace data-export create \
  --resource-group rg-globalmart-monitoring \
  --workspace-name law-globalmart-prod \
  --name "ComplianceExport" \
  --destination /subscriptions/{sub-id}/resourceGroups/rg-globalmart-monitoring/providers/Microsoft.Storage/storageAccounts/compliancelogs \
  --table-names "requests" "exceptions" "customEvents"
```

---

## Phase 9: Cost Optimization and Data Management

### Step 9.1: Implement Sampling to Reduce Costs

**Azure Monitor Tool Used**: Adaptive Sampling

```csharp
// Configure adaptive sampling
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.EnableAdaptiveSampling = true;
});

builder.Services.Configure<SamplingOptions>(options =>
{
    options.MaxTelemetryItemsPerSecond = 5;
    options.ExcludedTypes = "Exception;Trace";  // Always keep exceptions and traces
    options.IncludedTypes = "Request;Dependency";
});
```

**Fixed-Rate Sampling for More Control**:
```csharp
builder.Services.AddApplicationInsightsTelemetryProcessor<FixedRateSamplingTelemetryProcessor>(
    processorOptions =>
    {
        processorOptions.SamplingPercentage = 10;  // Keep 10% of telemetry
        processorOptions.ExcludeTypes = new[] { "Exception" };
    });
```

### Step 9.2: Monitor Ingestion and Costs

**Azure Monitor Tool Used**: Usage and Estimated Costs

```kusto
// Check daily ingestion volume
Usage
| where TimeGenerated > ago(30d)
| where IsBillable == true
| summarize 
    TotalGB = sum(Quantity) / 1024,
    Cost = sum(Quantity) / 1024 * 2.76  // $2.76 per GB
    by bin(TimeGenerated, 1d), DataType
| render columnchart
```

```kusto
// Find top talkers by table
Usage
| where TimeGenerated > ago(7d)
| where IsBillable == true
| summarize TotalGB = sum(Quantity) / 1024 by DataType
| order by TotalGB desc
| top 10 by TotalGB
```

### Step 9.3: Set Daily Cap to Control Costs

**Azure Monitor Tool Used**: Daily Cap Configuration

```bash
az monitor app-insights component update \
  --app globalmart-appinsights \
  --resource-group rg-globalmart-monitoring \
  --cap 10  # Daily cap of 10 GB
```

**Alert When Approaching Cap**:
```kusto
_BilledSize
| where _IsBillable == true
| summarize IngestedGB = sum(_BilledSize) / 1024 / 1024 / 1024 by bin(TimeGenerated, 1h)
| where IngestedGB > 8  // Alert at 80% of 10GB cap
```

### Step 9.4: Optimize with Telemetry Processors

**Azure Monitor Tool Used**: Custom Telemetry Processor

```csharp
public class CostOptimizationProcessor : ITelemetryProcessor
{
    public void Process(ITelemetry item)
    {
        // Filter out health check requests
        if (item is RequestTelemetry request && 
            request.Name.Contains("/health"))
        {
            return;  // Don't send to Application Insights
        }

        // Filter out successful dependency calls with low duration
        if (item is DependencyTelemetry dependency && 
            dependency.Success == true && 
            dependency.Duration < TimeSpan.FromMilliseconds(100))
        {
            return;  // Skip fast successful calls
        }

        // Reduce properties on trace telemetry
        if (item is TraceTelemetry trace && 
            trace.SeverityLevel < SeverityLevel.Warning)
        {
            trace.Properties.Clear();  // Remove custom properties from info logs
        }

        _next.Process(item);
    }
}
```

---

## Complete Monitoring Dashboard Setup

### Step 10.1: Create Comprehensive Azure Dashboard

**Azure Monitor Tool Used**: Azure Dashboard + Azure Workbooks

Navigate to: Azure Portal → Dashboard → New Dashboard

**Panel Layout**:

1. **System Health Overview** (Metrics)
   - Availability percentage (target: 99.9%)
   - Average response time
   - Request rate
   - Failed request rate

2. **Application Map** (Application Insights)
   - Visual topology of all services
   - Health indicators
   - Click to drill into specific components

3. **Active Incidents** (Log Query)
   ```kusto
   alerts
   | where TimeGenerated > ago(24h)
   | where Severity <= 2
   | where Status == "Active"
   | project TimeGenerated, AlertName, Severity, Description
   ```

4. **Business KPIs** (Workbook)
   - Revenue per hour
   - Conversion rate
   - Cart abandonment rate
   - Average order value

5. **Performance Trends** (Metrics)
   - P95 response time (7-day trend)
   - Dependency duration breakdown
   - Exception count by type

6. **Top 5 Slow Operations** (Log Query)
   ```kusto
   requests
   | where timestamp > ago(1h)
   | summarize P95Duration = percentile(duration, 95), Count = count() by name
   | top 5 by P95Duration desc
   ```

7. **Regional Performance** (Geo Map)
   ```kusto
   requests
   | where timestamp > ago(24h)
   | summarize AvgDuration = avg(duration), RequestCount = count() 
     by client_CountryOrRegion
   | render piechart
   ```

### Step 10.2: Create On-Call Workbook

**Azure Monitor Tool Used**: Azure Workbook (Troubleshooting Template)

```kusto
// Parameter: Time Range
let timeRange = {TimeRange};

// Parameter: Service
let serviceName = "{ServiceName:value}";

// Section 1: Service Overview
requests
| where timestamp > ago(timeRange)
| where cloud_RoleName == serviceName
| summarize 
    RequestCount = count(),
    FailureRate = 100.0 * countif(success == false) / count(),
    P50 = percentile(duration, 50),
    P95 = percentile(duration, 95),
    P99 = percentile(duration, 99)
| project RequestCount, FailureRate, P50, P95, P99;

// Section 2: Recent Exceptions
exceptions
| where timestamp > ago(timeRange)
| where cloud_RoleName == serviceName
| summarize Count = count() by type, outerMessage
| top 10 by Count desc;

// Section 3: Slow Dependencies
dependencies
| where timestamp > ago(timeRange)
| where cloud_RoleName == serviceName
| where duration > 1000
| summarize Count = count(), AvgDuration = avg(duration) by target, name
| top 10 by AvgDuration desc;

// Section 4: Failed Requests by Endpoint
requests
| where timestamp > ago(timeRange)
| where cloud_RoleName == serviceName
| where success == false
| summarize Count = count() by name, resultCode
| order by Count desc;
```

### Step 10.3: Mobile App for On-Call Monitoring

**Azure Monitor Tool Used**: Azure Mobile App

Install "Azure" mobile app to receive:
- Push notifications for critical alerts
- Quick access to metrics
- Ability to view Application Map
- Run saved KQL queries
- Acknowledge incidents

---

## Key Takeaways

### Azure Monitor Tools Used in This Scenario

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **Application Insights** | Application performance monitoring | Track requests, dependencies, exceptions in applications |
| **Log Analytics Workspace** | Centralized log storage and querying | Store and analyze logs from multiple sources |
| **Metrics Explorer** | Visualize metrics | Quick overview of performance metrics |
| **Application Map** | Distributed system visualization | Understand service topology and dependencies |
| **Live Metrics Stream** | Real-time monitoring | Monitor deployments or investigate live issues |
| **Transaction Search** | End-to-end transaction tracing | Debug specific user requests across services |
| **Performance Blade** | Performance analysis | Identify slow operations and bottlenecks |
| **Failures Blade** | Failure analysis | Investigate errors and exceptions |
| **KQL (Kusto Query Language)** | Advanced querying | Complex analysis and custom reports |
| **Azure Workbooks** | Custom dashboards | Create business and operational dashboards |
| **Smart Detection** | Anomaly detection | Automatically detect performance degradation |
| **Metric Alerts** | Threshold-based alerting | Alert on simple metric conditions |
| **Log Query Alerts** | Complex alerting | Alert on complex scenarios using KQL |
| **Action Groups** | Incident response automation | Route alerts to people and systems |
| **Availability Tests** | Uptime monitoring | Synthetic monitoring from multiple regions |
| **Snapshot Debugger** | Production debugging | Capture full application state at exception |
| **Profiler** | Performance profiling | Identify code-level performance issues |
| **Usage Analytics** | User behavior tracking | Understand how users interact with app |
| **Custom Events & Metrics** | Business analytics | Track domain-specific KPIs |
| **Diagnostic Settings** | Azure resource logging | Forward logs from Azure services |
| **Sampling** | Cost optimization | Reduce telemetry volume while maintaining insights |
| **Telemetry Processors** | Data filtering and enrichment | Control what data is sent to Application Insights |

### Success Metrics Achieved

**Before Monitoring Implementation**:
- ❌ 95.2% uptime
- ❌ 2.3s average response time
- ❌ Mean time to detect (MTTD): 45 minutes
- ❌ Mean time to resolve (MTTR): 4 hours
- ❌ No visibility into cross-service issues
- ❌ Manual log searching

**After Full Monitoring Implementation**:
- ✅ 99.95% uptime
- ✅ 380ms average response time (P95)
- ✅ MTTD: 2 minutes (Smart Detection)
- ✅ MTTR: 15 minutes (detailed diagnostics)
- ✅ Complete end-to-end tracing
- ✅ Proactive issue detection
- ✅ Business intelligence from telemetry
- ✅ 65% reduction in monitoring costs through sampling

### Best Practices Implemented

1. **Workspace-based Application Insights** for centralized data management
2. **Distributed tracing** with correlation IDs across all services
3. **Custom dimensions** for business context in telemetry
4. **Smart alerting** to reduce alert fatigue
5. **Adaptive sampling** for cost optimization
6. **Availability tests** from multiple regions
7. **Business KPI tracking** alongside technical metrics
8. **Security and compliance** monitoring
9. **Real-time dashboards** for operations team
10. **Automated incident response** with Action Groups

---

## Conclusion

This scenario demonstrates how Azure Monitor and Application Insights provide a comprehensive observability solution that goes beyond basic monitoring. By implementing these tools progressively, GlobalMart achieved:

- **Full visibility** into application performance and user experience
- **Proactive problem detection** before customers are impacted
- **Rapid troubleshooting** with detailed diagnostics
- **Business insights** from operational data
- **Cost-effective** telemetry management
- **Confidence** in system reliability for Black Friday

The key is to start simple (Phase 1), iterate based on learnings, and gradually add sophistication as the team's monitoring maturity grows.
