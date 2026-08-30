---
type: System Design Case
title: "Design A Notification System"
description: "Design a high-volume, multi-channel notification engine (APNs, FCM, SMS, Email) supporting dedicated channel message queues, template rendering, deduplication, user opt-out preferences, and reliable delivery."
tags: [system-design, distributed-systems, notification-system, push-notification, apns, fcm, twilio, message-queues]
timestamp: 2026-08-22T00:00:00Z
---

# Design A Notification System

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 11  
> **Topic**: Multi-Channel Delivery (APNs, FCM, Twilio, SendGrid), Dedicated Message Queues, Deduplication, Notification Templates

---

## 1. Understand the Problem and Establish Design Scope

A modern notification system delivers soft real-time transactional alerts, marketing promotions, and user updates across mobile push, SMS, and email.

```mermaid
flowchart LR
    subgraph Senders["Internal Microservices"]
        BILLING["Billing Service"]
        ORDER["Order Service"]
        MARKET["Marketing Service"]
    end

    subgraph CoreEngine["Notification Engine"]
        GATEWAY["Notification API Gateway"]
    end

    subgraph Channels["Multi-Channel Delivery"]
        APNS["APNs (iOS)"] --> D_IOS["iOS Device"]
        FCM["FCM (Android)"] --> D_AND["Android Device"]
        TWILIO["Twilio (SMS)"] --> D_SMS["Mobile Phone"]
        SENDGRID["SendGrid (Email)"] --> D_MAIL["Email Client"]
    end

    Senders --> GATEWAY
    GATEWAY --> Channels
```

---

### Interview Clarification & Scope

> **Candidate:** What communication channels must be supported?  
> **Interviewer:** **iOS Push (APNs)**, **Android Push (FCM)**, **SMS (Twilio/Nexmo)**, and **Email (SendGrid/Mailchimp)**.
>
> **Candidate:** What is the daily notification volume?  
> **Interviewer:** 
> - **10 Million Mobile Push Notifications**
> - **1 Million SMS Messages**
> - **5 Million Emails**
>
> **Candidate:** Can users configure opt-out preferences and quiet hours?  
> **Interviewer:** Yes, users can opt-out of specific notification categories and configure quiet hours.
>
> **Candidate:** How should transient third-party vendor downtime be handled?  
> **Interviewer:** Must guarantee at-least-once delivery with automated exponential retries without blocking other channels.

---

## 2. High-Level Architecture & Multi-Queue Isolation

To prevent an outage or rate-limiting in one external vendor (e.g., Twilio) from blocking critical push notifications, **each delivery channel is decoupled with an independent message queue**.

![Notification architecture showing preference checks, delivery logging, channel-specific queues, independent workers, and external providers.](resources/notification-system/notification-system-architecture.png)

**Diagram:** Triggering services pass validated notifications through preference checks and durable logging before channel-isolated queues fan out to independently retrying workers. [Open the interactive notification architecture diagram](resources/notification-system/notification-system-architecture.html).

```mermaid
flowchart TD
    subgraph TriggerTier["Triggering Services"]
        SVC1["Billing Service"]
        SVC2["Order Service"]
        SVC3["Social Service"]
    end

    subgraph IngressTier["Notification Core Tier"]
        GW["Notification API Servers<br/>(Auth, Rate Limit, Validation)"]
        CACHE[("Redis Cache<br/>(User Preferences & Tokens)")]
        DB[("Notification DB<br/>(Logs & Metadata)")]
    end

    subgraph QueueTier["Channel-Specific Message Queues"]
        Q_IOS["iOS APNs Queue"]
        Q_AND["Android FCM Queue"]
        Q_SMS["SMS Twilio Queue"]
        Q_MAIL["Email SendGrid Queue"]
    end

    subgraph WorkerTier["Dedicated Channel Workers"]
        W_IOS["iOS Worker Fleet"]
        W_AND["Android Worker Fleet"]
        W_SMS["SMS Worker Fleet"]
        W_MAIL["Email Worker Fleet"]
    end

    subgraph ExternalProviders["Third-Party Gateways"]
        P_APNS["Apple APNs"]
        P_FCM["Google FCM"]
        P_SMS["Twilio / Nexmo"]
        P_MAIL["SendGrid / AWS SES"]
    end

    TriggerTier --> GW
    GW <--> CACHE & DB
    
    GW -->|Route by Channel| Q_IOS & Q_AND & Q_SMS & Q_MAIL
    
    Q_IOS --> W_IOS --> P_APNS
    Q_AND --> W_AND --> P_FCM
    Q_SMS --> W_SMS --> P_SMS
    Q_MAIL --> W_MAIL --> P_MAIL
```

---

## 3. Data Model & Device Token Gathering

```mermaid
erDiagram
    USER ||--o{ USER_DEVICE : registers
    USER ||--o{ NOTIFICATION_SETTING : configures
    USER ||--o{ NOTIFICATION_LOG : receives

    USER {
        bigint user_id PK
        varchar email
        varchar phone_number
        timestamp created_at
    }

    USER_DEVICE {
        bigint device_id PK
        bigint user_id FK
        varchar device_token
        varchar device_type
        timestamp last_active_at
    }

    NOTIFICATION_SETTING {
        bigint setting_id PK
        bigint user_id FK
        varchar channel_type
        boolean is_opt_out
        varchar quiet_hours_utc
    }

    NOTIFICATION_LOG {
        varchar event_id PK
        bigint user_id FK
        varchar channel
        varchar status
        int retry_count
        timestamp sent_at
    }
```

---

## 4. Design Deep Dive

### 1. Notification Templates & Parameter Injection

Hardcoding notification strings in backend microservices leads to maintenance nightmares. A centralized template engine injects dynamic parameters into localized, version-controlled templates:

```json
{
  "template_id": "tpl_order_shipped_v2",
  "locale": "en-US",
  "title": "Your Order #{order_id} Has Shipped!",
  "body": "Hi {customer_name}, your package is on the way via {carrier} (Tracking: {tracking_num}).",
  "action_url": "https://mysite.com/track/{tracking_num}"
}
```

---

### 2. Deduplication & Idempotency Check

Network retries can cause duplicate notification submissions. The API gateway validates a unique `event_id` against Redis before queueing:

```mermaid
sequenceDiagram
    autonumber
    participant Svc as Calling Service
    participant GW as Notification Server
    participant Cache as Redis Cache
    participant MQ as Message Queue

    Svc->>GW: POST /v1/notifications/send (event_id: "evt_9981a")
    GW->>Cache: SETNX idemp:evt_9981a 1 (TTL: 24h)
    alt Key Already Exists (Duplicate Submission)
        Cache-->>GW: 0 (Key Exists)
        GW-->>Svc: 200 OK (Duplicate Ignored)
    else Key Stored Successfully (First Time)
        Cache-->>GW: 1 (Success)
        GW->>MQ: Publish Notification to Channel Queue
        GW-->>Svc: 202 Accepted
    end
```

---

### 3. Reliability: Exponential Backoff & Dead Letter Queues (DLQ)

```mermaid
flowchart TD
    WORKER["Notification Worker"] --> SEND["Invoke 3rd-Party Vendor API"]
    SEND --> CHECK{"Success (200 OK)?"}
    
    CHECK -->|Yes| LOG_OK["Update Status = DELIVERED"]
    CHECK -->|No: Network Timeout / 503| RETRY{"Retry Count < 5?"}
    
    RETRY -->|Yes| BACKOFF["Retry Queue (Exponential Backoff + Jitter)"]
    BACKOFF --> WORKER
    
    RETRY -->|No: Max Retries Exceeded| DLQ["Dead Letter Queue (DLQ)<br/>(Alerting & Manual Investigation)"]
```

#### Backoff Formula
$$\text{Delay} = \min\left(300\text{s}, 2^{\text{retry\_count}} \times 1\text{s}\right) \pm \text{Random Jitter}$$

---

### 4. User Notification Fatigue & Rate Limiting
- To avoid annoying users with excessive notifications, enforce a client-level rate limiter (e.g., maximum $5\text{ marketing push notifications per user per hour}$).
- **Quiet Hours Filter**: Check user's local timezone setting before sending non-urgent marketing alerts.

---

## 5. Architectural Summary

### Architectural Summary Mindmap

```mermaid
mindmap
  root((Notification System))
    Channels
      iOS APNs
      Android FCM
      SMS Twilio
      Email SendGrid
    Architecture
      Dedicated Message Queues per Channel
      Stateless Notification API Servers
      Worker Fleet with Auto-Scaling
    Reliability
      Redis Deduplication (SETNX)
      Exponential Backoff Retry + DLQ
      User Opt-out & Quiet Hours Check
```

| Component | Design Choice | System Benefit |
|:---|:---|:---|
| **Queue Topology** | Separate Message Queues per channel | Fault isolation: third-party SMS outage never blocks push notifications. |
| **Deduplication** | Distributed Redis `SETNX` with TTL | Eliminates double-sending notifications to end-user devices. |
| **Worker Scaling** | Horizontally scalable independent worker pools | Scale compute resources independently based on channel queue depth. |
| **Compliance** | Pre-send opt-out preference filtering | Respects user communication preferences and regulatory unsubscribe laws (CAN-SPAM / GDPR). |

---

## References

1. Apple Push Notification service (APNs): https://developer.apple.com/documentation/usernotifications
2. Firebase Cloud Messaging (FCM): https://firebase.google.com/docs/cloud-messaging
3. Twilio Programmable SMS API: https://www.twilio.com/docs/sms
4. SendGrid Email API Best Practices: https://sendgrid.com/docs/
