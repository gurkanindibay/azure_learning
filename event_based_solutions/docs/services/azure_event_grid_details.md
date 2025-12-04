# Azure Event Grid Detailed Reference
## Table of Contents

- [1. Overview](#1-overview)
- [2. Core Concepts](#2-core-concepts)
  - [Events](#events)
  - [Event Sources (Publishers)](#event-sources-publishers)
  - [Topics](#topics)
    - [Topic Types and Authentication](#topic-types-and-authentication)
  - [Event Subscriptions](#event-subscriptions)
  - [Event Handlers](#event-handlers)
- [3. Filtering](#3-filtering)
- [4. Data Integration Model: Push-Push](#4-data-integration-model-push-push)
  - [Publisher Side (Push)](#publisher-side-push)
  - [Subscriber Side (Push)](#subscriber-side-push)
  - [Benefits](#benefits)
  - [Considerations](#considerations)
- [5. Architecture Patterns](#5-architecture-patterns)
  - [Reactive Automation](#reactive-automation)
- [6. Best Practices](#6-best-practices)
- [6. Advanced Features](#6-advanced-features)
  - [Message Schemas](#message-schemas)
  - [Retry & Retry Policies](#retry-retry-policies)
  - [Dead Letter Events](#dead-letter-events)
  - [Access Control & Permissions](#access-control-permissions)
  - [Certificates & TLS](#certificates-tls)
  - [Endpoint Validation](#endpoint-validation)
  - [Delivery Response Handling](#delivery-response-handling)


## 1. Overview
Azure Event Grid is a highly scalable, serverless event broker that lets you integrate applications using events. It simplifies building event-driven architectures.

- **Primary Use Case:** Reactive programming, ops automation, serverless triggers.
- **Mechanism:** Push-push (Event Grid pushes to the subscriber).

## 2. Core Concepts

### Events
The smallest amount of information that fully describes something that happened in the system.

### Event Sources (Publishers)
Where the event comes from.
- **Azure Services:** Blob Storage, Resource Groups, Subscriptions, IoT Hub, Service Bus, etc.
- **Custom Sources:** Your own applications sending events to a Custom Topic.
- **SaaS Sources:** Partner events (e.g., Auth0).

### Topics
The endpoint where publishers send events.
- **System Topics:** Built-in topics for Azure services (hidden management).
- **Custom Topics:** Application-specific topics you create.
- **Partner Topics:** Topics for subscribing to events from third-party SaaS providers.
- **Domains:** Management tool for large numbers of topics (e.g., one topic per customer for a SaaS app).

#### Topic Types and Authentication

Azure Event Grid supports different topic types, each with specific authentication characteristics:

| Topic Type | Description | Authentication Methods | Managed Identity Support |
|------------|-------------|------------------------|-------------------------|
| **System Topic** | Built-in topics for Azure service events | Managed identity only | ✅ Required (no keys/SAS) |
| **Custom Topic** | Application-specific topics you create | Access keys, SAS tokens, Managed identity | ✅ Optional |
| **Domain Topic** | Topics within an Event Grid domain | Access keys, SAS tokens, Managed identity | ✅ Optional |
| **Partner Topic** | Third-party SaaS provider events | Access keys, SAS tokens, Managed identity | ✅ Optional |

##### System Topics (Managed Identity Only)
- **Authentication:** System topics **only support managed identity authentication** and cannot use access keys or SAS tokens.
- **Use Case:** When you need authentication without managing keys or tokens.
- **Automatic Creation:** Created automatically when you subscribe to Azure service events (e.g., Blob Storage, Resource Groups).
- **No Key Management:** Ideal for security-conscious scenarios where credential rotation overhead must be eliminated.

```csharp
// System topics use managed identity - no keys to manage
// Events are published automatically by Azure services
// You only create subscriptions to receive events
```

##### Custom Topics (Key Management Required)
- **Authentication:** Support SAS keys if "Enable authentication using SAS keys" is selected during resource creation.
- **Key Management:** Requires managing access keys or SAS tokens for publishing events.
- **Flexibility:** Offers more control over authentication but adds operational overhead.

```bash
# Create custom topic with SAS key authentication
az eventgrid topic create \
  --name mycustomtopic \
  --resource-group myResourceGroup \
  --location eastus
  
# Get access keys (must be managed/rotated)
az eventgrid topic key list \
  --name mycustomtopic \
  --resource-group myResourceGroup
```

##### Domain Topics
- **Authentication:** Part of Event Grid domains and support the same authentication methods as custom topics.
- **Key Management:** Requires key or SAS token management at the domain level.
- **Use Case:** Multi-tenant scenarios where you need one topic per customer/entity.

##### Partner Topics
- **Authentication:** Used to subscribe to events from third-party SaaS providers.
- **Key Management:** Follow the same authentication model as custom topics, requiring key management.
- **Use Case:** Integrating with external SaaS services like Auth0, SAP, etc.

#### Exam Scenario: Authentication Without Key Management

**Question:** You are developing a solution that publishes events to Azure Event Grid. The solution must use authentication without managing keys or SAS tokens. You need to identify which type of Event Grid topic supports this requirement. Which topic type should you use?

| Option | Explanation |
|--------|-------------|
| **System topic** ✅ | System topics only support managed identity authentication and cannot use access keys or SAS tokens, making them the correct choice when you need authentication without managing keys or tokens. |
| **Domain topic** ❌ | Domain topics are part of Event Grid domains and support the same authentication methods as custom topics, requiring key or SAS token management. |
| **Partner topic** ❌ | Partner topics are used to subscribe to events from third-party SaaS providers and follow the same authentication model as custom topics, requiring key management. |
| **Custom topic** ❌ | Custom topics support SAS keys if "Enable authentication using SAS keys" is selected during resource creation, which means they require key management, violating the requirement. |

**Key Takeaway:** When the requirement specifies "no key or SAS token management," **System topics** are the answer because they exclusively use managed identity authentication.

### Event Subscriptions
The mechanism to route events from a topic to a handler. Contains filtering logic.

### Event Handlers
The app or service reacting to the event.
- **Supported:** Azure Functions, Logic Apps, Webhooks, Event Hubs, Service Bus Queue/Topic, Storage Queue.

## 3. Filtering
Event Grid allows filtering at the subscription level to ensure subscribers only receive relevant events.
- **Event Type Filtering:** Subscribe only to `Microsoft.Storage.BlobCreated`.
- **Subject Filtering:** "Begins with" (`/blobServices/default/containers/logs/`) or "Ends with" (`.jpg`).
- **Advanced Filtering:** Filter based on values in the data payload (e.g., `data.size > 1024`).

## 4. Data Integration Model: Push-Push

Event Grid follows a **push-push** delivery model:

### Publisher Side (Push)
- **Event sources actively push events** to Event Grid topics.
- Publishers (Azure services or custom applications) send events via HTTP POST to the Event Grid endpoint.
- No polling required from Event Grid; events arrive as they occur.

### Subscriber Side (Push)
- **Event Grid actively pushes events** to subscribers.
- Subscribers (webhooks, Azure Functions, Logic Apps, etc.) receive events via HTTP POST.
- Event Grid manages the delivery, retry logic, and failure handling.
- Subscribers must expose an HTTP endpoint to receive events.

### Benefits
- **Low latency:** Events are delivered immediately as they occur.
- **Serverless-friendly:** No need for subscribers to maintain polling loops.
- **Decoupling:** Publishers don't need to know about subscribers; Event Grid handles routing.

### Considerations
- Subscribers must be able to handle incoming HTTP requests.
- Endpoint must be publicly accessible or use private endpoints.
- Requires endpoint validation before event delivery starts.

## 5. Architecture Patterns
### Reactive Automation
- Blob Created → Event Grid → Azure Function → Database Update

## 6. Best Practices
- **Scaling:** Auto-scaling; monitor subscriber endpoints for throttling.
- **Reliability:** Implement idempotent event handlers.

## 6. Advanced Features

### Message Schemas
Event Grid supports multiple schemas for event data:
- **Event Grid Schema:** The default schema with properties like `subject`, `eventType`, `eventTime`, `id`, and `data`.
- **CloudEvents Schema:** An open standard (CNCF) for describing event data, enabling interoperability across different cloud providers and platforms.
- **Custom Input Schema:** Allows mapping custom JSON fields to Event Grid requirements, useful when you cannot change the event publisher's format.

### Retry & Retry Policies
When Event Grid fails to deliver an event to an endpoint, it retries based on a schedule:
- **Schedule:** It uses an exponential backoff policy (e.g., 10s, 30s, 1m, 5m, 10m, 30m, 1h) up to 24 hours.
- **Randomization:** A small randomization factor is added to avoid thundering herd issues.
- **Configurable Policies:**
    - **Max Delivery Attempts:** Configurable between 1 and 30.
    - **Event Time-to-Live (TTL):** Configurable duration (e.g., 1 minute to 1440 minutes) after which the event is dropped if not delivered.

#### Practice Question: Configuring Retry Policy with Dead-Lettering

**Question:** A company uses Azure Event Grid to handle events from blob storage. The solution must retry failed event deliveries with exponential backoff for up to 24 hours before moving events to a dead-letter location. Which configuration should you implement?

| Option | Description |
|--------|-------------|
| A | Set maxDeliveryAttempts to 30 and eventTimeToLiveInMinutes to 1440 with dead-lettering enabled |
| B | Set maxRetryAttempts to 24 and retryInterval to 1 hour with dead-lettering enabled |
| C | Set retryPolicy to exponential and deliveryTimeout to 24 hours with dead-lettering enabled |
| D | Set automaticRetry to true and retryDuration to 24 hours with dead-lettering enabled |

<details>
<summary>Answer</summary>

**Correct Answer: A**

**Explanation:**
- **Option A (Correct):** Event Grid uses exponential backoff by default, and setting `maxDeliveryAttempts` to 30 with `eventTimeToLiveInMinutes` to 1440 (24 hours = 1440 minutes) ensures retries continue for 24 hours before dead-lettering occurs.
- **Option B (Incorrect):** Event Grid doesn't support fixed retry intervals as it uses exponential backoff, and `maxRetryAttempts` and `retryInterval` aren't valid configuration properties for Event Grid event subscriptions.
- **Option C (Incorrect):** Event Grid doesn't have a `retryPolicy` setting as exponential backoff is the default behavior, and `deliveryTimeout` isn't a valid configuration option.
- **Option D (Incorrect):** `automaticRetry` and `retryDuration` aren't valid Event Grid configuration properties. Event Grid automatically retries with exponential backoff, and the retry behavior is controlled by `maxDeliveryAttempts` and `eventTimeToLiveInMinutes`.

</details>

### Dead Letter Events
If an event cannot be delivered after all retry attempts or the TTL expires:
- **Dead Lettering:** You can configure a storage account (blob container) to store these undelivered events.
- **Purpose:** Allows for later analysis, debugging, and manual reconciliation of missed events.
- **Content:** The dead-lettered blob contains the original event payload along with the error reason for the failure.

### Access Control & Permissions
Event Grid divides access between resource (management) operations and data-plane delivery:
- **System/operations level:** Roles such as `Owner`, `Contributor`, `EventGrid Contributor`, and `EventGrid Event Subscription Contributor` control who can create or update topics, event subscriptions, filters, and delivery settings (`Microsoft.EventGrid/*` operations).
- **User/data level:** Publishers use `EventGrid Data Sender` to push events (SAS tokens, managed identity, or keys), and subscribers rely on delivery endpoints that may also require `EventGrid Data Receiver` or custom authentication to consume events safely.
- **Scope:** Assign roles at subscription, resource group, or individual topic level to restrict who can configure routes versus who can send or receive payloads.

### Certificates & TLS
Event Grid requires validated HTTPS endpoints for data delivery and endpoint validation must complete over TLS:
- **Trusted CA:** Delivery endpoints must present certificates issued by public/trusted root CAs (including Azure-managed certificates); self-signed certs are not accepted unless you establish a private endpoint with a custom root capable of being trusted by Event Grid.
- **Hostname match:** The certificate's subject must match the DNS name used during subscription creation, and wildcard certificates are supported when the wildcard covers the specified endpoint domain.
- **Automatic renewal:** Use Azure App Service-managed certificates or Azure Front Door to manage renewal, preventing delivery breaks when certificates expire.
- **Mutual TLS:** Not required for standard Event Grid delivery; if you implement client cert authentication at the endpoint you must ensure Event Grid's requests are allowed through your network controls.

### Endpoint Validation
When an event subscription targets a webhook or HTTP endpoint, Event Grid performs validation before sending business events:
- **Validation event:** Event Grid sends a `Microsoft.EventGrid.SubscriptionValidationEvent` payload that includes a `validationCode` and `validationUrl`.
- **Expected response:** The endpoint must respond within 30 seconds with an HTTP 200 and either echo the `validationCode` in the body or follow the `validationUrl` to confirm ownership.
- **Failed validation:** If the endpoint never acknowledges the validation event or responds with an error, the subscription stays in a `PendingValidation` state and delivery never starts; retry attempts are made but eventually the subscription is disabled.
- **Automation tip:** Functions/Logic Apps listening for Event Grid events should explicitly handle the validation event (check `eventType` and return the code) before processing normal events.

#### Webhook Validation Mechanisms

Event Grid supports two validation mechanisms for webhook endpoints:

| Mechanism | Type | Description | Best For |
|-----------|------|-------------|----------|
| **Synchronous Handshake** | Primary | Webhook echoes the `validationCode` back in the HTTP response body | Most webhook scenarios, simple implementation |
| **Asynchronous Validation** | Alternative | Webhook calls the `validationUrl` to confirm ownership | Scenarios where immediate response isn't possible |

**Synchronous Handshake (Primary Method):**
1. Event Grid sends a `SubscriptionValidationEvent` with a `validationCode`
2. Webhook must respond within 30 seconds with HTTP 200
3. Response body must include: `{ "validationResponse": "<validationCode>" }`
4. Subscription is activated upon successful validation

**Asynchronous Validation (Alternative Method):**
1. Event Grid sends a `SubscriptionValidationEvent` with both `validationCode` and `validationUrl`
2. Webhook can later perform a GET request to the `validationUrl`
3. The `validationUrl` is valid for 5 minutes
4. Useful when webhook cannot respond synchronously

> **Important:** The synchronous handshake is the primary and most commonly used validation mechanism. Bearer token authentication and Mutual TLS are used for securing webhook calls after subscription creation, not for the initial endpoint validation process.

#### Practice Question: Webhook Endpoint Validation

**Question:** You are implementing an Event Grid solution that must validate webhook endpoints. The webhook must prove it can receive events before the subscription is created. Which validation mechanism should you implement?

| Option | Description |
|--------|-------------|
| A | Mutual TLS certificate validation |
| B | Asynchronous validation using a callback URL |
| C | Bearer token authentication in the Authorization header |
| D | Synchronous handshake validation by echoing the validation code |

<details>
<summary>Answer</summary>

**Correct Answer: D**

**Explanation:**
- **Option A (Incorrect):** Mutual TLS provides transport-level security but is not the mechanism used by Event Grid for validating that a webhook endpoint can receive events during subscription creation.
- **Option B (Incorrect):** While Event Grid supports asynchronous validation via `validationUrl` callback, the synchronous handshake is the primary and most commonly used validation mechanism for webhooks.
- **Option C (Incorrect):** Bearer token authentication is used for securing webhook calls after subscription creation, not for the initial endpoint validation process required during subscription setup.
- **Option D (Correct):** Event Grid sends a validation event with a `validationCode` that the webhook must echo back synchronously in the response, proving it can receive and process Event Grid events before the subscription is activated.

</details>

### Delivery Response Handling
When Event Grid receives a `400 (Bad Request)` or `413 (Request Entity Too Large)` during delivery:
- **No retries:** These status codes are treated as permanent failures. Event Grid still makes that single delivery attempt, records the failure, and will not retry that event again even though the subscription stays active.
- **Failure tracking:** The failed delivery is recorded in metrics/logs and, if dead-lettering is enabled, the event is written there for inspection; otherwise the payload is eventually dropped once the TTL expires.
- **Subscription footprint:** The subscription stays enabled so future deliveries continue, but repeated 400/413 responses should trigger troubleshooting of payload size limits and validation logic.
- **Payload guidance:** Split oversized payloads, trim unnecessary properties, and ensure subscribers parse the schema properly to avoid 400 responses.
