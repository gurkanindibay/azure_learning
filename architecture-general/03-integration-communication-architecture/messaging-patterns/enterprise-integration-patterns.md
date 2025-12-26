# Enterprise Integration Patterns (EIP)

## Table of Contents

- [Introduction](#introduction)
- [Messaging System Patterns](#messaging-system-patterns)
- [Message Construction Patterns](#message-construction-patterns)
- [Message Routing Patterns](#message-routing-patterns)
- [Message Transformation Patterns](#message-transformation-patterns)
- [Messaging Endpoint Patterns](#messaging-endpoint-patterns)
- [System Management Patterns](#system-management-patterns)

## Introduction

Enterprise Integration Patterns (EIP) are a collection of design patterns for integrating enterprise applications. Originally documented by Gregor Hohpe and Bobby Woolf, these patterns provide proven solutions for common integration challenges.

```mermaid
graph TB
    subgraph "Enterprise Integration Landscape"
        A[Application A] --> MC[Message Channel]
        MC --> R[Router]
        R --> MC2[Message Channel]
        MC2 --> T[Translator]
        T --> MC3[Message Channel]
        MC3 --> B[Application B]
    end
```

## Messaging System Patterns

### Message Channel

A virtual pipe that connects sender and receiver.

```mermaid
graph LR
    S[Sender] -->|Message| MC[Message Channel]
    MC -->|Message| R[Receiver]
```

**Channel Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| **Point-to-Point** | Single receiver | Work distribution |
| **Publish-Subscribe** | Multiple receivers | Event broadcasting |
| **Datatype Channel** | Specific message types | Type safety |
| **Invalid Message Channel** | Error messages | Error handling |
| **Dead Letter Channel** | Undeliverable messages | Troubleshooting |

**Real-World Scenario:** An e-commerce platform uses Point-to-Point channels for order processing (one worker handles each order), Pub/Sub for inventory updates (multiple systems need to know), and Dead Letter channels for failed payment notifications requiring manual review.

### Message

The data packet transferred through the messaging system.

```json
{
  "header": {
    "messageId": "msg-123",
    "correlationId": "corr-456",
    "timestamp": "2025-01-01T10:00:00Z",
    "contentType": "application/json",
    "replyTo": "reply-queue"
  },
  "body": {
    "orderId": "ORD-001",
    "items": [...]
  }
}
```

**Real-World Scenario:** A banking system includes correlation IDs in every transaction message, allowing support teams to trace a customer's wire transfer across fraud detection, compliance checking, and ledger update services.

### Pipes and Filters

Process messages through a sequence of processing steps.

```mermaid
graph LR
    I[Input] --> F1[Filter 1]
    F1 --> P1[Pipe]
    P1 --> F2[Filter 2]
    F2 --> P2[Pipe]
    P2 --> F3[Filter 3]
    F3 --> O[Output]
```

**Benefits:**
- Reusable components
- Independent testing
- Flexible composition
- Parallel processing

**Real-World Scenario:** An email processing system passes messages through: Spam Filter → Virus Scanner → Content Classifier → Priority Tagger → Folder Router. Each filter is independently deployable and testable.

### Message Router

Route messages to different channels based on conditions.

```mermaid
graph LR
    I[Input] --> R[Router]
    R -->|Condition A| CA[Channel A]
    R -->|Condition B| CB[Channel B]
    R -->|Default| CD[Channel D]
```

**Real-World Scenario:** A logistics company routes shipment requests to different carriers: FedEx for overnight packages, USPS for standard mail, and freight companies for large items—all based on package weight and delivery speed.

### Message Translator

Convert message format between systems.

```mermaid
graph LR
    A[Format A] --> T[Translator]
    T --> B[Format B]
```

**Real-World Scenario:** A hospital system translates HL7 v2 messages from legacy lab equipment into FHIR JSON format for the modern patient portal, enabling old and new systems to communicate seamlessly.

### Message Endpoint

Application code that connects to the messaging system.

```mermaid
graph LR
    subgraph "Application"
        L[Logic] --> E[Endpoint]
    end
    E --> MC[Message Channel]
```

**Real-World Scenario:** A microservices application uses a standardized endpoint library that handles connection pooling, retry logic, and circuit breakers, so developers focus on business logic rather than messaging infrastructure.

## Message Construction Patterns

### Command Message

Request an action to be performed.

```json
{
  "type": "command",
  "command": "CreateOrder",
  "payload": {
    "customerId": "CUST-123",
    "items": [...]
  }
}
```

**Real-World Scenario:** A food delivery app sends a `PrepareOrder` command to the restaurant's kitchen display system, triggering chefs to start cooking when a customer completes checkout.

### Document Message

Transfer data between systems.

```json
{
  "type": "document",
  "documentType": "Invoice",
  "payload": {
    "invoiceNumber": "INV-001",
    "lineItems": [...],
    "total": 1500.00
  }
}
```

**Real-World Scenario:** An insurance company transfers complete policy documents between the underwriting system and the claims system, including all coverage details, beneficiaries, and terms.

### Event Message

Notify about something that happened.

```json
{
  "type": "event",
  "eventType": "OrderShipped",
  "timestamp": "2025-01-01T15:00:00Z",
  "payload": {
    "orderId": "ORD-001",
    "trackingNumber": "TRK-123"
  }
}
```

**Real-World Scenario:** A stock trading platform publishes `TradeExecuted` events whenever a trade completes, allowing portfolio trackers, tax calculators, and notification services to react independently.

### Request-Reply

Two-way communication with response.

```mermaid
sequenceDiagram
    participant R as Requestor
    participant RQ as Request Channel
    participant S as Service
    participant RC as Reply Channel
    
    R->>RQ: Request (replyTo: RC)
    RQ->>S: Request
    S->>RC: Reply
    RC->>R: Reply
```

**Real-World Scenario:** A travel booking website sends a flight availability request to an airline's reservation system and waits for availability and pricing response before showing results to the customer.

### Return Address

Specify where to send the reply.

```json
{
  "header": {
    "replyTo": "orders/replies",
    "correlationId": "req-123"
  },
  "body": {...}
}
```

**Real-World Scenario:** A distributed order system specifies different reply addresses for web orders (web-replies queue) vs. mobile orders (mobile-replies queue) so responses are routed to the correct frontend.

### Correlation Identifier

Match replies with requests.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Service
    
    C->>S: Request (correlationId: "abc-123")
    S->>C: Reply (correlationId: "abc-123")
    Note over C: Match by correlationId
```

**Real-World Scenario:** A call center system uses correlation IDs to match customer callback requests with agent responses, ensuring the right agent receives the customer's original inquiry context.

### Message Sequence

Break large data into ordered messages.

```json
// Message 1 of 3
{
  "sequenceId": "batch-001",
  "sequenceNumber": 1,
  "sequenceSize": 3,
  "payload": {...}
}
```

**Real-World Scenario:** A video streaming service uploads large video files in 100MB chunks with sequence numbers, allowing the encoding service to reassemble them in order even if chunks arrive out of sequence.

### Message Expiration

Set message time-to-live.

```json
{
  "header": {
    "expiresAt": "2025-01-01T12:00:00Z",
    "ttl": 3600
  },
  "body": {...}
}
```

**Real-World Scenario:** A flash sale system sets 5-minute TTL on discount offers—if the inventory service can't process in time, the offer expires automatically rather than honoring stale prices.

## Message Routing Patterns

### Content-Based Router

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

**Real-World Scenario:** An e-commerce platform routes orders by region: US orders go to US fulfillment center, EU orders to EU warehouse, and APAC orders to Singapore hub—based on the shipping address country.

### Message Filter

Remove unwanted messages.

```mermaid
graph LR
    I[All Messages] --> F[Filter]
    F -->|Pass| O[Output]
    F -->|Block| X[Discard]
```

**Real-World Scenario:** A social media analytics pipeline filters out bot-generated tweets (based on account age and posting frequency) before sentiment analysis, reducing processing costs by 40%.

### Dynamic Router

Route based on external configuration.

```mermaid
graph LR
    I[Input] --> DR[Dynamic Router]
    RC[(Route Config)] --> DR
    DR --> D1[Destination 1]
    DR --> D2[Destination 2]
```

**Real-World Scenario:** A multi-tenant SaaS platform routes customer data to different processing pipelines based on their subscription tier, configured in a database that can be updated without redeployment.

### Recipient List

Send to multiple recipients.

```mermaid
graph LR
    I[Input] --> RL[Recipient List]
    RL --> R1[Recipient 1]
    RL --> R2[Recipient 2]
    RL --> R3[Recipient 3]
```

**Real-World Scenario:** When a customer places an order, the order confirmation is sent to: email service, SMS service, mobile push notification, and the customer's account history—all determined by their communication preferences.

### Splitter

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

**Real-World Scenario:** An e-commerce order with 5 items is split into 5 separate messages, each sent to the appropriate warehouse (electronics, clothing, books) for parallel fulfillment.

### Aggregator

Combine related messages.

```mermaid
graph LR
    M1[Message 1] --> A[Aggregator]
    M2[Message 2] --> A
    M3[Message 3] --> A
    A --> CM[Combined Message]
```

**Completion Strategies:**

| Strategy | Description |
|----------|-------------|
| **Wait for All** | All correlated messages received |
| **First** | First message received |
| **Timeout** | Time limit reached |
| **Custom Condition** | Business logic determines completion |

**Real-World Scenario:** A price comparison website sends requests to 10 airline APIs, aggregates responses with a 3-second timeout, and returns the best prices found—even if some airlines don't respond in time.

### Resequencer

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

**Real-World Scenario:** A financial trading system receives market data packets over UDP (which may arrive out of order) and resequences them by timestamp before feeding to the trading algorithm.

### Composed Message Processor

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

**Real-World Scenario:** An insurance quote request is split by coverage type (auto, home, life), routed to specialized underwriting engines, then aggregated into a single bundled quote for the customer.

### Scatter-Gather

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

**Real-World Scenario:** A hotel booking site broadcasts availability requests to 50 hotels simultaneously, gathers responses, and presents the customer with a sorted list by price within 2 seconds.

### Routing Slip

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

**Real-World Scenario:** A loan application flows through Credit Check → Income Verification → Collateral Evaluation → Final Approval, with the route defined at submission based on loan type (mortgage vs. personal).

### Process Manager

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

**Real-World Scenario:** An order fulfillment saga tracks state across: Order Created → Payment Authorized → Inventory Reserved → Shipped → Delivered, handling compensations if any step fails.

## Message Transformation Patterns

### Envelope Wrapper

Wrap message in standard envelope.

```json
{
  "envelope": {
    "version": "1.0",
    "timestamp": "2025-01-01T10:00:00Z",
    "source": "system-a",
    "correlationId": "corr-123"
  },
  "payload": {
    "actualContent": "..."
  }
}
```

**Real-World Scenario:** A B2B integration gateway wraps partner-specific payloads in a standard envelope containing authentication tokens, timestamps, and routing information before transmission.

### Content Enricher

Add data from external sources.

```mermaid
graph LR
    I[Input Message] --> CE[Content Enricher]
    DB[(External Data)] --> CE
    CE --> O[Enriched Message]
```

**Real-World Scenario:** An order message containing only customer ID is enriched with full customer profile (name, address, loyalty tier) from the CRM database before reaching the fulfillment service.

### Content Filter

Remove unnecessary data.

```mermaid
graph LR
    I[Full Message] --> CF[Content Filter]
    CF --> O[Filtered Message]
```

**Real-World Scenario:** A GDPR-compliant analytics pipeline strips PII (names, emails, addresses) from user events before sending to the data warehouse, keeping only anonymized behavioral data.

### Claim Check

Store large data externally.

```mermaid
sequenceDiagram
    participant P as Producer
    participant DS as Data Store
    participant MB as Message Broker
    participant C as Consumer
    
    P->>DS: Store Large Payload
    DS->>P: Claim Check (Reference)
    P->>MB: Message with Claim Check
    MB->>C: Message with Claim Check
    C->>DS: Retrieve (Claim Check)
    DS->>C: Large Payload
```

**Real-World Scenario:** A document processing service stores 50MB PDF files in blob storage and passes only the blob reference through the message queue, avoiding broker size limits and improving throughput.

### Normalizer

Convert various formats to canonical form.

```mermaid
graph TB
    F1[Format 1] --> N[Normalizer]
    F2[Format 2] --> N
    F3[Format 3] --> N
    N --> CF[Canonical Format]
```

**Real-World Scenario:** A retail company receives product data from suppliers in CSV, XML, and JSON formats—the normalizer converts all to a standard JSON schema before inventory processing.

### Canonical Data Model

Standard data format across systems.

```mermaid
graph TB
    subgraph "Without Canonical Model"
        A1[System A] <-->|AB| B1[System B]
        A1 <-->|AC| C1[System C]
        B1 <-->|BC| C1
    end
    
    subgraph "With Canonical Model"
        A2[System A] <-->|A-CDM| CDM[Canonical Model]
        B2[System B] <-->|B-CDM| CDM
        C2[System C] <-->|C-CDM| CDM
    end
```

**Real-World Scenario:** A healthcare network defines a canonical patient record format—each hospital system (Epic, Cerner, custom) translates to/from this format, avoiding N×N integration complexity.

## Messaging Endpoint Patterns

### Messaging Gateway

Encapsulate messaging access.

```mermaid
graph LR
    subgraph "Application"
        L[Business Logic] --> G[Gateway]
    end
    G --> MS[Messaging System]
```

**Real-World Scenario:** A payment service exposes a simple `processPayment(order)` method to developers—internally, the gateway handles message serialization, queue selection, retries, and acknowledgments.

### Messaging Mapper

Map between domain and message objects.

```python
class OrderMapper:
    def to_message(self, order: Order) -> Message:
        return Message(
            body={
                "orderId": order.id,
                "items": [self.item_to_dict(i) for i in order.items],
                "total": str(order.total)
            }
        )
    
    def from_message(self, message: Message) -> Order:
        return Order(
            id=message.body["orderId"],
            items=[self.dict_to_item(i) for i in message.body["items"]],
            total=Decimal(message.body["total"])
        )
```

**Real-World Scenario:** An e-commerce service maps between rich `Order` domain objects (with calculated fields, validation) and flat JSON message structures suitable for cross-service communication.

### Transactional Client

Coordinate messaging with transactions.

```mermaid
sequenceDiagram
    participant A as Application
    participant DB as Database
    participant MB as Message Broker
    
    A->>A: Begin Transaction
    A->>DB: Update Data
    A->>MB: Send Message
    A->>A: Commit Transaction
```

**Real-World Scenario:** A banking system ensures that account debit and transfer notification message are atomic—either both succeed or both rollback, preventing customers from being notified about failed transfers.

### Polling Consumer

Explicitly request messages.

```python
while True:
    message = queue.receive(timeout=30)
    if message:
        process(message)
        message.acknowledge()
```

**Real-World Scenario:** A batch processing system polls for new data files every 5 minutes, processes them during off-peak hours, giving the team control over resource usage and processing timing.

### Event-Driven Consumer

React to message arrival.

```python
@message_handler("orders-queue")
def handle_order(message):
    process(message)
    return Acknowledge
```

**Real-World Scenario:** A real-time fraud detection system immediately processes each transaction as it arrives, triggering alerts within milliseconds of suspicious activity detection.

### Competing Consumers

Multiple consumers on same queue.

```mermaid
graph LR
    Q[Queue] --> C1[Consumer 1]
    Q --> C2[Consumer 2]
    Q --> C3[Consumer 3]
```

**Real-World Scenario:** An order processing system runs 10 consumer instances on the same queue—during Black Friday, it scales to 100 instances, with orders automatically distributed across all workers.

### Message Dispatcher

Distribute messages to handlers.

```mermaid
graph LR
    MC[Message Channel] --> D[Dispatcher]
    D -->|Type A| HA[Handler A]
    D -->|Type B| HB[Handler B]
    D -->|Type C| HC[Handler C]
```

**Real-World Scenario:** A notification service dispatcher routes messages to the appropriate handler: EmailHandler for email notifications, SMSHandler for texts, and PushHandler for mobile alerts.

### Selective Consumer

Filter messages before consuming.

```python
@message_handler("orders-queue", 
                 filter="priority = 'high'")
def handle_high_priority(message):
    process(message)
```

**Real-World Scenario:** A premium support queue has consumers that only pick up messages where `customer.tier = 'platinum'`, ensuring VIP customers get dedicated fast-track processing.

### Durable Subscriber

Survive disconnections.

```mermaid
sequenceDiagram
    participant S as Subscriber
    participant B as Broker
    
    S->>B: Subscribe (durable=true)
    S->>S: Disconnect
    Note over B: Store messages
    S->>B: Reconnect
    B->>S: Deliver stored messages
```

**Real-World Scenario:** A mobile app's push notification subscriber maintains durability—when a user's phone is offline for hours, all missed notifications are delivered once connectivity is restored.

### Idempotent Receiver

Handle duplicates safely.

```python
processed_ids = set()

def process_message(message):
    if message.id in processed_ids:
        return  # Already processed
    
    do_work(message)
    processed_ids.add(message.id)
```

**Real-World Scenario:** A payment processor tracks processed transaction IDs—if a network retry causes the same payment message to arrive twice, the duplicate is detected and ignored, preventing double charges.

## System Management Patterns

### Control Bus

Manage messaging system.

```mermaid
graph TB
    CB[Control Bus]
    CB -->|Configure| C1[Component 1]
    CB -->|Monitor| C2[Component 2]
    CB -->|Control| C3[Component 3]
```

**Real-World Scenario:** A DevOps team uses a control bus to dynamically adjust log levels, enable/disable features, and update routing rules across 50 microservices without redeployment.

### Detour

Route messages through additional steps.

```mermaid
graph LR
    I[Input] --> S{Detour?}
    S -->|Yes| D[Detour Step]
    D --> N[Normal Route]
    S -->|No| N
    N --> O[Output]
```

**Real-World Scenario:** During a suspected data quality issue, ops enables a detour to route all orders through an additional validation service, then disables it once the issue is resolved.

### Wire Tap

Inspect messages non-intrusively.

```mermaid
graph LR
    I[Input] --> WT[Wire Tap]
    WT --> O[Output]
    WT -->|Copy| M[Monitor]
```

**Real-World Scenario:** A compliance team wire-taps the trading message flow to copy all order messages to an audit system for regulatory reporting, without impacting trading system performance.

### Message History

Track message journey.

```json
{
  "header": {
    "history": [
      {"step": "received", "timestamp": "...", "node": "gateway"},
      {"step": "validated", "timestamp": "...", "node": "validator"},
      {"step": "routed", "timestamp": "...", "node": "router"}
    ]
  },
  "body": {...}
}
```

**Real-World Scenario:** A customer support system includes message history showing the ticket's journey: Received (Web Portal) → Classified (AI Triage) → Assigned (Support Team) → Resolved (Agent), with timestamps for SLA tracking.

### Message Store

Persist messages for retrieval.

```mermaid
graph LR
    P[Producer] --> MS[Message Store]
    MS --> C[Consumer]
    MS --> DB[(Database)]
```

**Real-World Scenario:** An email marketing platform stores all outbound campaign messages in a message store, enabling resend capabilities, campaign analytics, and compliance audits months later.

### Smart Proxy

Track and manage request-reply.

```mermaid
graph LR
    C[Client] --> SP[Smart Proxy]
    SP --> S[Service]
    S --> SP
    SP --> C
```

**Real-World Scenario:** An API gateway acts as a smart proxy for backend services—tracking all pending requests, implementing timeouts, correlating responses, and handling retries transparently.

### Test Message

Verify system health.

```mermaid
graph LR
    TG[Test Generator] -->|Test Message| S[System]
    S -->|Result| TV[Test Verifier]
```

**Real-World Scenario:** A payment processing system sends synthetic test transactions every minute through the entire pipeline, alerting the on-call team if any test fails to complete within expected time.

## Related Topics

- [Messaging Patterns Overview](../messaging-patterns-overview.md)
- [Integration Architecture](../../integration-architecture-overview.md)
- [Event-Driven Architecture](./event-driven-architecture.md)
