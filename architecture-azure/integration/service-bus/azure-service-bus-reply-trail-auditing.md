# Azure Service Bus:  Reply Trail Auditing Guide

## Overview

This document explains how to implement a reply trail auditing solution using Azure Service Bus, particularly for scenarios like hazard notification systems where audit trails are critical.

## Key Properties for Reply Trail Auditing

| Property | Type | Purpose |
|----------|------|---------|
| `MessageId` | System/User | Uniquely identifies each individual message |
| `SessionId` | User | Groups related messages into a logical session |
| `CorrelationId` | User | Links reply messages to their original request |
| `ReplyToSessionId` | User | Specifies which session should receive the reply |

## Why Both SessionId and CorrelationId Are Needed

### SessionId Alone Is Not Enough

`SessionId` groups multiple messages into a conversation but cannot identify individual request-reply pairs within that session. 

### The Solution:  Combine Both

- **SessionId → ReplyToSessionId**: Ensures replies are routed to the correct session
- **MessageId → CorrelationId**: Links each reply to its specific originating message

## Scenario:  Hazard Notification System

### Architecture

```
┌──────────────────┐         ┌─────────────────┐         ┌──────────────────┐
│  Signaling       │         │  Azure Service  │         │  Alarm           │
│  Server          │────────▶│  Bus            │────────▶│  Controllers     │
│                  │         │                 │◀────────│                  │
└──────────────────┘         └─────────────────┘         └──────────────────┘
     (Publisher)                                              (Subscribers)
```

### Message Flow Example

#### Step 1: Original Hazard Messages (Same Session, Different Alarms)

```
Session: "building-A-alarms"
├── Message 1: Fire Alarm       (MessageId: "msg-001")
├── Message 2: Gas Leak Alarm   (MessageId: "msg-002")
└── Message 3: Flood Alarm      (MessageId: "msg-003")
```

#### Step 2: Audit Reply Messages (With Correlation)

```
Session: "building-A-alarms"
├── Reply A: Fire Alarm Activated      (CorrelationId: "msg-001")
├── Reply B: Gas Leak Alarm Activated  (CorrelationId: "msg-002")
└── Reply C: Flood Alarm Activated     (CorrelationId: "msg-003")
```

## Implementation

### Sending a Hazard Message (Publisher)

```csharp
using Azure.Messaging.ServiceBus;

// Create the hazard message
var hazardMessage = new ServiceBusMessage("Fire alarm triggered in Zone 3")
{
    MessageId = Guid.NewGuid().ToString(),
    SessionId = "building-A-alarms",
    ApplicationProperties =
    {
        { "AlarmType", "Fire" },
        { "Zone", "3" },
        { "Severity", "High" }
    }
};

// Send the message
await sender.SendMessageAsync(hazardMessage);
```

### Receiving and Creating Audit Reply (Subscriber)

```csharp
using Azure.Messaging.ServiceBus;

// Process received hazard message
async Task ProcessHazardMessage(ServiceBusReceivedMessage hazardMessage)
{
    // Activate the alarm
    await ActivateAlarm(hazardMessage);

    // Create audit reply message
    var auditMessage = new ServiceBusMessage($"Alarm activated:  {hazardMessage.ApplicationProperties["AlarmType"]}")
    {
        // New unique ID for this audit message
        MessageId = Guid. NewGuid().ToString(),

        // Link to original message for audit trail
        CorrelationId = hazardMessage.MessageId,

        // Route reply to the correct session
        ReplyToSessionId = hazardMessage.SessionId,

        // Include audit details
        ApplicationProperties =
        {
            { "OriginalAlarmType", hazardMessage.ApplicationProperties["AlarmType"] },
            { "ProcessedAt", DateTime.UtcNow.ToString("O") },
            { "ControllerName", Environment.MachineName }
        }
    };

    // Send audit message to audit queue
    await auditSender.SendMessageAsync(auditMessage);
}
```

### Querying Audit Trail

```csharp
// Find all audit records for a specific hazard message
async Task<List<ServiceBusReceivedMessage>> GetAuditTrail(string originalMessageId)
{
    var auditRecords = new List<ServiceBusReceivedMessage>();

    await foreach (var message in auditReceiver.ReceiveMessagesAsync())
    {
        if (message. CorrelationId == originalMessageId)
        {
            auditRecords.Add(message);
        }
    }

    return auditRecords;
}
```

## Property Assignment Summary

| Original Message Property | Reply Message Property | Purpose |
|---------------------------|------------------------|---------|
| `MessageId` | `CorrelationId` | Links audit record to specific alarm event |
| `SessionId` | `ReplyToSessionId` | Routes reply to correct session |

## Common Mistakes to Avoid

### ❌ Incorrect Approaches

| Incorrect Assignment | Reason |
|---------------------|--------|
| `MessageId` → `DeliveryCount` | `DeliveryCount` is read-only and tracks delivery attempts |
| `SessionId` → `SequenceNumber` | `SequenceNumber` is read-only and system-assigned |
| `SequenceNumber` → `DeliveryCount` | Both are system-managed properties |
| `MessageId` → `SequenceNumber` | `SequenceNumber` is read-only |

### ✅ Correct Approach

| Correct Assignment | Reason |
|-------------------|--------|
| `MessageId` → `CorrelationId` | Correlates related messages for auditing |
| `SessionId` → `ReplyToSessionId` | Maintains session context for replies |

## Visual Representation

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HAZARD MESSAGE                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  MessageId:     "abc-123"  ─────────────────────┐                  │  │
│  │  SessionId:    "building-A-alarms"  ───────┐   │                  │  │
│  │  Content:      "Fire Alarm Triggered"      │   │                  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                                    │   │
                              ┌─────────────────────┘   │
                              │                         │
                              ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AUDIT REPLY MESSAGE                                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  MessageId:        "xyz-789"  (new unique ID)                     │  │
│  │  CorrelationId:    "abc-123"  ◀─────────────────────────────────┐ │  │
│  │  ReplyToSessionId: "building-A-alarms"  ◀───────────────────┐   │ │  │
│  │  Content:          "Fire Alarm Activated - Audit Record"    │   │ │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Benefits of This Approach

1. **Complete Audit Trail**: Every alarm activation can be traced back to its original trigger
2. **Session Integrity**: Related messages stay within their logical session
3. **Scalability**: Works with multiple alarms and controllers simultaneously
4. **Compliance**: Meets audit requirements by maintaining clear message relationships
5. **Query Capability**: Easy to retrieve all audit records for a specific event

## References

- [Azure Service Bus Message Sessions](https://docs.microsoft.com/en-us/azure/service-bus-messaging/message-sessions)
- [Azure Service Bus Message Properties](https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messages-payloads)
- [Request-Reply Pattern with Service Bus](https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-queues-topics-subscriptions)