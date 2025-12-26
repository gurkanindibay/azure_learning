# Message Routing Patterns

Patterns for directing message flow through the system based on content, rules, or dynamic configuration.

## Table of Contents

- [Content-Based Router](#content-based-router)
- [Message Filter](#message-filter)
- [Dynamic Router](#dynamic-router)
- [Recipient List](#recipient-list)
- [Splitter](#splitter)
- [Aggregator](#aggregator)
- [Resequencer](#resequencer)
- [Composed Message Processor](#composed-message-processor)
- [Scatter-Gather](#scatter-gather)
- [Routing Slip](#routing-slip)
- [Process Manager](#process-manager)

---

## Content-Based Router

Route based on message content.

```mermaid
graph LR
    I[Input] --> CBR[Content-Based Router]
    CBR -->|order.priority == high| HQ[High Priority Queue]
    CBR -->|order.priority == normal| NQ[Normal Queue]
    CBR -->|order.priority == low| LQ[Low Priority Queue]
```

```python
def route(message):
    priority = message.body.order.priority
    routing_table = {
        "high": "high-priority-queue",
        "normal": "normal-queue",
        "low": "low-priority-queue"
    }
    return routing_table.get(priority, "default-queue")
```

### Real-World Scenario

An e-commerce platform routes orders by region: US orders go to US fulfillment center, EU orders to EU warehouse, and APAC orders to Singapore hub—based on the shipping address country.

---

## Message Filter

Remove unwanted messages.

```mermaid
graph LR
    I[All Messages] --> F[Filter]
    F -->|Pass| O[Output]
    F -->|Block| X[Discard]
```

### Real-World Scenario

A social media analytics pipeline filters out bot-generated tweets (based on account age and posting frequency) before sentiment analysis, reducing processing costs by 40%.

---

## Dynamic Router

Route based on external configuration.

```mermaid
graph LR
    I[Input] --> DR[Dynamic Router]
    RC[(Route Config)] --> DR
    DR --> D1[Destination 1]
    DR --> D2[Destination 2]
```

### Real-World Scenario

A multi-tenant SaaS platform routes customer data to different processing pipelines based on their subscription tier, configured in a database that can be updated without redeployment.

---

## Recipient List

Send to multiple recipients.

```mermaid
graph LR
    I[Input] --> RL[Recipient List]
    RL --> R1[Recipient 1]
    RL --> R2[Recipient 2]
    RL --> R3[Recipient 3]
```

### Real-World Scenario

When a customer places an order, the order confirmation is sent to: email service, SMS service, mobile push notification, and the customer's account history—all determined by their communication preferences.

---

## Splitter

Break composite message into parts.

```mermaid
graph LR
    subgraph "Input"
        CM[Composite Message]
    end
    CM --> S[Splitter]
    S --> M1[Message 1]
    S --> M2[Message 2]
    S --> M3[Message 3]
```

### Real-World Scenario

An e-commerce order with 5 items is split into 5 separate messages, each sent to the appropriate warehouse (electronics, clothing, books) for parallel fulfillment.

---

## Aggregator

Combine related messages.

```mermaid
graph LR
    M1[Message 1] --> A[Aggregator]
    M2[Message 2] --> A
    M3[Message 3] --> A
    A --> CM[Combined Message]
```

### Completion Strategies

| Strategy | Description |
|----------|-------------|
| **Wait for All** | All correlated messages received |
| **First** | First message received |
| **Timeout** | Time limit reached |
| **Custom Condition** | Business logic determines completion |

### Real-World Scenario

A price comparison website sends requests to 10 airline APIs, aggregates responses with a 3-second timeout, and returns the best prices found—even if some airlines don't respond in time.

---

## Resequencer

Restore message order.

```mermaid
graph LR
    M3[Msg 3] --> R[Resequencer]
    M1[Msg 1] --> R
    M2[Msg 2] --> R
    R --> O1[Msg 1]
    R --> O2[Msg 2]
    R --> O3[Msg 3]
```

### Real-World Scenario

A financial trading system receives market data packets over UDP (which may arrive out of order) and resequences them by timestamp before feeding to the trading algorithm.

---

## Composed Message Processor

Process composite messages as a unit.

```mermaid
graph LR
    CM[Composite] --> S[Splitter]
    S --> R[Router]
    R --> P1[Processor 1]
    R --> P2[Processor 2]
    P1 --> A[Aggregator]
    P2 --> A
    A --> O[Output]
```

### Real-World Scenario

An insurance quote request is split by coverage type (auto, home, life), routed to specialized underwriting engines, then aggregated into a single bundled quote for the customer.

---

## Scatter-Gather

Broadcast to multiple recipients and aggregate responses.

```mermaid
graph TB
    I[Request] --> B[Broadcast]
    B --> S1[Service 1]
    B --> S2[Service 2]
    B --> S3[Service 3]
    S1 --> A[Aggregator]
    S2 --> A
    S3 --> A
    A --> O[Combined Response]
```

### Real-World Scenario

A hotel booking site broadcasts availability requests to 50 hotels simultaneously, gathers responses, and presents the customer with a sorted list by price within 2 seconds.

---

## Routing Slip

Define message route dynamically.

```json
{
  "routingSlip": ["step1", "step2", "step3"],
  "currentStep": 0,
  "payload": {...}
}
```

```mermaid
graph LR
    I[Input] --> RS[Routing Slip]
    RS -->|Step 1| S1[Service 1]
    S1 -->|Step 2| S2[Service 2]
    S2 -->|Step 3| S3[Service 3]
    S3 --> O[Output]
```

### Real-World Scenario

A loan application flows through Credit Check → Income Verification → Collateral Evaluation → Final Approval, with the route defined at submission based on loan type (mortgage vs. personal).

---

## Process Manager

Maintain state of multi-step processing.

```mermaid
stateDiagram-v2
    [*] --> Received
    Received --> Validated: Validate
    Validated --> Processing: Start Processing
    Processing --> Completed: Complete
    Processing --> Failed: Error
    Completed --> [*]
    Failed --> [*]
```

### Real-World Scenario

An order fulfillment saga tracks state across: Order Created → Payment Authorized → Inventory Reserved → Shipped → Delivered, handling compensations if any step fails.

---

## Related Topics

- [Message Construction Patterns](./02-message-construction-patterns.md)
- [Message Transformation Patterns](./04-message-transformation-patterns.md)
- [EIP Overview](./README.md)
