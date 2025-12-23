# Microsoft Entra ID Audit Logging Architecture

## Overview

Microsoft Entra ID (formerly Azure Active Directory) generates audit logs that track identity-related activities such as user creation, role assignments, sign-ins, and privilege escalations. These logs are critical for security monitoring, compliance, and forensic analysis.

This document covers architectural patterns for capturing, streaming, and storing Microsoft Entra ID audit logs using Azure services.

---

## Table of Contents

- [Audit Log Types](#audit-log-types)
- [Architecture Patterns](#architecture-patterns)
- [Streaming Audit Logs to Event Hubs](#streaming-audit-logs-to-event-hubs)
- [Service Selection for Audit Pipelines](#service-selection-for-audit-pipelines)
- [Common Scenarios](#common-scenarios)
- [Best Practices](#best-practices)

---

## Audit Log Types

Microsoft Entra ID provides several types of logs:

| Log Type | Description | Use Cases |
|----------|-------------|-----------|
| **Audit Logs** | Records of activities like user creation, group modifications, role assignments | Compliance, security auditing, change tracking |
| **Sign-in Logs** | Records of user authentication events, including location, device, and application | Security monitoring, anomaly detection |
| **Provisioning Logs** | Records of user provisioning activities from connected systems | Identity lifecycle management |
| **Risky Sign-ins** | Records of potentially risky authentication attempts | Security incident response |

---

## Architecture Patterns

### Pattern 1: Real-Time Audit Log Streaming to Cosmos DB

This pattern captures identity events in near real-time and stores them in Azure Cosmos DB for analysis and compliance.

```
┌─────────────────────────────────┐
│   Microsoft Entra ID            │
│   (Azure Active Directory)      │
│                                 │
│   • User Creation               │
│   • Role Assignments            │
│   • Audit Logs                  │
└────────────┬────────────────────┘
             │
             │ Diagnostic Settings
             │ (Stream logs)
             ▼
┌─────────────────────────────────┐
│   Azure Event Hubs              │ ◄── Azure service 1
│                                 │
│   • High-throughput ingestion   │
│   • Event streaming platform    │
│   • Buffering & partitioning    │
└────────────┬────────────────────┘
             │
             │ Event trigger
             │
             ▼
┌─────────────────────────────────┐
│   Azure Functions               │ ◄── Azure service 2
│                                 │
│   • Event processing            │
│   • Data transformation         │
│   • Batch writes                │
└────────────┬────────────────────┘
             │
             │ Write documents
             │
             ▼
┌─────────────────────────────────┐
│   Azure Cosmos DB               │
│                                 │
│   • Long-term storage           │
│   • Query & analytics           │
│   • Compliance retention        │
└─────────────────────────────────┘
```

#### Component Selection

**Azure Event Hubs (Azure service 1)**
- ✅ Highly scalable data streaming platform
- ✅ Can capture Microsoft Entra ID audit logs via diagnostic settings
- ✅ Near real-time log streaming
- ✅ Built-in buffering and partitioning
- ✅ Integrates with Azure Functions for downstream processing

**Azure Functions (Azure service 2)**
- ✅ Processes events from Event Hubs
- ✅ Transforms and enriches log data
- ✅ Performs batch writes to Cosmos DB
- ✅ Serverless, auto-scaling compute

---

## Streaming Audit Logs to Event Hubs

### Configuration Steps

1. **Enable Diagnostic Settings in Microsoft Entra ID**
   - Navigate to Microsoft Entra ID → Monitoring → Diagnostic settings
   - Click "Add diagnostic setting"
   - Select log categories: `AuditLogs`, `SignInLogs`, etc.
   - Choose "Stream to an event hub"
   - Select the Event Hubs namespace and hub

2. **Configure Event Hubs**
   - Create an Event Hubs namespace (Standard or Premium tier)
   - Create an event hub with appropriate partition count
   - Configure retention period (1-7 days for Standard, up to 90 days for Premium)

3. **Deploy Azure Functions**
   - Use Event Hubs trigger binding
   - Process events in batches for efficiency
   - Implement retry logic and error handling
   - Write processed data to Cosmos DB

### Example Azure Function (C#)

```csharp
[FunctionName("ProcessEntraAuditLogs")]
public static async Task Run(
    [EventHubTrigger("audit-logs", Connection = "EventHubConnection")] 
    EventData[] events,
    [CosmosDB(
        databaseName: "AuditDb",
        containerName: "AuditLogs",
        Connection = "CosmosDBConnection")] 
    IAsyncCollector<AuditLogDocument> outputDocuments,
    ILogger log)
{
    foreach (var eventData in events)
    {
        string messageBody = Encoding.UTF8.GetString(eventData.EventBody.ToArray());
        var auditLog = JsonSerializer.Deserialize<EntraAuditLog>(messageBody);
        
        var document = new AuditLogDocument
        {
            Id = Guid.NewGuid().ToString(),
            Timestamp = auditLog.TimeGenerated,
            Operation = auditLog.OperationName,
            User = auditLog.InitiatedBy?.User?.UserPrincipalName,
            Result = auditLog.Result,
            Category = auditLog.Category,
            RawLog = messageBody
        };
        
        await outputDocuments.AddAsync(document);
    }
}
```

---

## Service Selection for Audit Pipelines

### Scenario: Capture User Creation and Role Assignment Events

**Question**: You need to design an architecture to capture the creation of users and the assignment of roles. The captured data must be stored in Azure Cosmos DB. Which Azure service should you choose for "Azure service 1"?

**Answer**: **Azure Event Hubs**

#### Why Azure Event Hubs? ✅

Azure Event Hubs is the correct choice because:

1. **High-throughput streaming platform**: Can handle millions of events per second from Microsoft Entra ID
2. **Native integration**: Diagnostic settings in Microsoft Entra ID can directly stream logs to Event Hubs
3. **Near real-time ingestion**: Logs are captured and made available for processing within seconds
4. **Buffering and reliability**: Provides built-in buffering and durability for event data
5. **Downstream processing**: Easily integrates with Azure Functions, Stream Analytics, or other consumers

#### Why NOT Other Services? ❌

| Service | Why It's Incorrect |
|---------|-------------------|
| **Azure Event Grid** | ❌ Optimized for discrete event delivery (e.g., blob created, resource updated), not for high-throughput log streaming. Event Grid is event-driven and reactive, not a streaming platform for audit logs. |
| **Azure Functions** | ❌ A compute service used to *process* events, not to *ingest* logs from Microsoft Entra ID. Functions would be Azure service 2 in this architecture, processing data between Event Hubs and Cosmos DB. |
| **Azure Monitor Logs** | ❌ Used for log analysis and querying (Log Analytics workspace), not for collecting and routing logs to Cosmos DB. It's a destination for logs, not an ingestion service for downstream processing. |
| **Azure Notification Hubs** | ❌ Designed to send push notifications to mobile devices and browsers, not for streaming or processing log data from identity services. |

### Service Comparison for Event Processing

| Capability | Event Hubs | Event Grid | Service Bus |
|-----------|------------|------------|-------------|
| **Purpose** | High-throughput streaming | Discrete event delivery | Enterprise messaging |
| **Throughput** | Millions of events/sec | Thousands of events/sec | Thousands of messages/sec |
| **Use Case** | Log streaming, telemetry | React to state changes | Transactional workflows |
| **Ordering** | Per-partition ordering | No ordering guarantee | FIFO queues available |
| **Retention** | 1-90 days | 24 hours | 14 days max |
| **Integration with Entra ID** | ✅ Native via diagnostic settings | ❌ Not supported | ❌ Not supported |

---

## Common Scenarios

### Scenario 1: Compliance Auditing

**Requirement**: Store all user creation and role assignment events for 7 years to meet regulatory compliance.

**Solution**:
- Stream audit logs from Microsoft Entra ID to Event Hubs
- Process with Azure Functions
- Store in Cosmos DB with appropriate retention policy
- Optionally archive to Azure Storage for long-term retention

### Scenario 2: Security Monitoring

**Requirement**: Detect and alert on suspicious role assignments in real-time.

**Solution**:
- Stream audit logs to Event Hubs
- Use Azure Stream Analytics or Functions to analyze events
- Trigger alerts via Azure Logic Apps or Azure Monitor
- Store events in Cosmos DB for forensic analysis

### Scenario 3: Identity Analytics

**Requirement**: Analyze patterns in user creation and role assignments over time.

**Solution**:
- Capture logs in Event Hubs
- Store in Cosmos DB with appropriate indexing
- Use Azure Synapse Link for Cosmos DB to run analytics
- Create Power BI dashboards for visualization

---

## Best Practices

### Event Hubs Configuration

1. **Partition Count**: Use 4-32 partitions based on throughput requirements
2. **Retention Period**: Configure based on processing SLA (1-7 days for Standard tier)
3. **Capture**: Enable Event Hubs Capture to automatically archive to Azure Storage
4. **Throughput Units**: Start with 2-4 TUs and scale based on ingestion rate

### Azure Functions Processing

1. **Batch Processing**: Process events in batches (default 64 events) for efficiency
2. **Error Handling**: Implement dead-letter queues for failed events
3. **Idempotency**: Use unique IDs to prevent duplicate writes to Cosmos DB
4. **Monitoring**: Enable Application Insights for observability

### Cosmos DB Design

1. **Partition Key**: Choose an appropriate partition key (e.g., `/userId` or `/date`)
2. **Indexing Policy**: Optimize indexing for query patterns
3. **Consistency Level**: Use Session or Consistent Prefix for audit logs
4. **Time-to-Live (TTL)**: Configure TTL for automatic data expiration if needed
5. **Change Feed**: Enable change feed for downstream analytics or archival

### Security Considerations

1. **Managed Identities**: Use managed identities for authentication between services
2. **Private Endpoints**: Deploy services with private endpoints for network isolation
3. **Encryption**: Enable encryption at rest and in transit for all services
4. **Access Control**: Use Azure RBAC to limit access to audit logs
5. **Audit Trail**: Monitor access to the audit logs themselves

---

## Cost Optimization

### Event Hubs
- Use Standard tier for most scenarios (Premium for advanced features)
- Enable auto-inflate to scale throughput units dynamically
- Consider Event Hubs Dedicated for very high throughput (>100 TUs)

### Azure Functions
- Use Consumption plan for variable workloads
- Consider Premium plan for VNet integration or predictable performance
- Monitor execution time and memory usage to optimize costs

### Cosmos DB
- Use provisioned throughput for predictable workloads
- Consider serverless for variable or development workloads
- Enable autoscale to handle traffic spikes efficiently
- Use analytical store for historical query scenarios

---

## References

- [Stream Microsoft Entra logs to Event Hub](https://learn.microsoft.com/en-us/azure/active-directory/reports-monitoring/howto-stream-logs-to-event-hub)
- [Azure Event Hubs Overview](https://learn.microsoft.com/en-us/azure/event-hubs/event-hubs-about)
- [Azure Event Grid Overview](https://learn.microsoft.com/en-us/azure/event-grid/overview)
- [Azure Functions Event Hub Trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-event-hubs-trigger)
- [Azure Cosmos DB Output Binding](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-cosmosdb-v2-output)
- [Azure Notification Hubs Overview](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-overview)
- [Microsoft Entra ID Audit Logs](https://learn.microsoft.com/en-us/azure/active-directory/reports-monitoring/concept-audit-logs)

---

## Related Topics

- [Microsoft Entra Privileged Identity Management](./microsoft-entra-privileged-identity-management.md)
- [Azure Identity Overview](./azure_identity_overview.md)
- [Azure RBAC Permission Models](./azure-rbac-permission-models.md)
- [Entra ID Access Reviews](./entra-id-access-reviews.md)
