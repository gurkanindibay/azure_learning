---
type: System Design Case
title: "Design A Chat System"
description: "Design a real-time, globally distributed chat application (like WhatsApp or Facebook Messenger) supporting 1-on-1 messaging, group chats, WebSocket bidirectional communication, online presence heartbeats, and NoSQL message history."
tags: [system-design, distributed-systems, chat-system, websockets, presence-service, cassandra, real-time, message-sync]
timestamp: 2026-08-22T00:00:00Z
---

# Design A Chat System

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 13  
> **Topic**: Real-Time Communication, WebSockets vs. Long-Polling, Presence Service, Multi-Device Synchronization, Message Ordering

---

## 1. Understand the Problem and Establish Design Scope

A modern chat application enables instantaneous text exchange across 1-on-1 conversations and small group chats, maintaining online presence and delivering push alerts when users are offline.

```mermaid
flowchart LR
    subgraph Clients["Active Clients"]
        U1["User A (Sender)"]
        U2["User B (Receiver)"]
    end

    subgraph ChatBackend["Real-Time Distributed Chat Core"]
        WS1["Chat Server 1 (WebSocket)"]
        WS2["Chat Server 2 (WebSocket)"]
        STORE[("NoSQL Message Store<br/>(Cassandra / HBase)")]
        PRESENCE[("Presence Server<br/>(Redis Heartbeats)")]
    end

    U1 <-->|Persistent WebSocket| WS1
    U2 <-->|Persistent WebSocket| WS2
    WS1 <--> STORE & PRESENCE
    WS2 <--> STORE & PRESENCE
```

---

### Interview Clarification & Scope

> **Candidate:** What types of chat should the system support?  
> **Interviewer:** Both **1-on-1 private chat** and **group chat (maximum 100 members)**.
>
> **Candidate:** What is the daily scale?  
> **Interviewer:** **50 Million Daily Active Users (DAU)**.
>
> **Candidate:** What are the key features?  
> **Interviewer:** Real-time text messaging, online/offline presence status, multi-device synchronization, and push notifications for offline users. Media attachments are out of scope.
>
> **Candidate:** What are the message retention and latency SLAs?  
> **Interviewer:** Store chat history permanently; message delivery latency must be **$< 100\text{ ms}$**.

---

## 2. Communication Protocols: Polling vs. WebSocket

```mermaid
flowchart TD
    subgraph ProtocolOptions["Client-Server Communication Protocols"]
        P1["<b>1. Short Polling</b><br/>Client queries server every 1s.<br/>❌ Wastes massive compute & network handshakes; returns empty responses."]
        P2["<b>2. Long Polling</b><br/>Server holds request open until a new message arrives.<br/>❌ Periodic timeouts; sender and receiver may connect to different stateless servers."]
        P3["<b>3. WebSocket (Recommended)</b><br/>Bidirectional, persistent full-duplex TCP connection initialized via HTTP upgrade.<br/>✅ Low latency overhead, instant server-push, efficient keep-alive frames."]
    end
```

---

## 3. High-Level Architecture

The system decouples into **stateless services** (HTTP REST for auth, profile, discovery) and **stateful services** (persistent WebSocket chat servers and presence servers).

![Real-time chat architecture showing WebSocket servers, Redis session presence, Cassandra history, and offline push delivery.](resources/13-chat-system/chat-system-architecture.png)

**Diagram:** Redis maps recipients to active WebSocket servers, while Cassandra provides durable message history and the push gateway handles offline recipients. [Open the interactive chat architecture diagram](resources/13-chat-system/chat-system-architecture.html).

```mermaid
flowchart TD
    subgraph IngressTier["Clients & Edge"]
        C_A["User A (Online)"]
        C_B["User B (Online)"]
        C_C["User C (Offline)"]
    end

    subgraph StatelessTier["Stateless HTTP API Gateway"]
        AUTH["Auth & User Profile Service"]
        REG["Service Discovery (ZooKeeper)"]
    end

    subgraph StatefulTier["Stateful Real-Time Tier"]
        WS_A["Chat Server 1 (WebSocket)"]
        WS_B["Chat Server 2 (WebSocket)"]
        PRESENCE["Presence Service (Heartbeat Manager)"]
    end

    subgraph DataStorage["Distributed Storage & Queues"]
        REDIS[("Redis Cache Cluster<br/>(Presence & Session Mapping)")]
        MSG_DB[("Message Store (Cassandra)<br/>(Append-Only Chat History)")]
        PUSH["Push Notification Gateway<br/>(APNs / FCM)"]
    end

    C_A <-->|WebSocket| WS_A
    C_B <-->|WebSocket| WS_B
    
    WS_A & WS_B <--> REDIS
    WS_A & WS_B --> MSG_DB
    WS_A -->|Target Offline| PUSH --> C_C
    PRESENCE <--> REDIS
```

---

## 4. Data Models & Storage Architecture

### Why Key-Value / Wide-Column NoSQL (Cassandra)?
1. **Chat Read-to-Write Ratio**: High write volume ($1:1$ or $1:2$ read/write).
2. **Access Patterns**: Users fetch recent messages sequentially ($O(1)$ range scans on partition key `chat_id` sorted by `message_id`).
3. **Horizontal Scaling**: Scales linearly across petabytes of historical chat logs.

```mermaid
erDiagram
    MESSAGE_1ON1 {
        bigint message_id PK
        bigint chat_id FK
        bigint sender_id
        bigint recipient_id
        text content
        timestamp created_at
    }

    MESSAGE_GROUP {
        bigint message_id PK
        bigint channel_id FK
        bigint sender_id
        text content
        timestamp created_at
    }
```

> [!NOTE]
> `message_id` is a 64-bit Snowflake integer that is **monotonically increasing per chat session**, guaranteeing strict chronological message ordering across devices.

---

## 5. Design Deep Dive

### 1. 1-on-1 Message Delivery Flow

```mermaid
sequenceDiagram
    autonumber
    actor Alice as User A (Sender)
    participant WS1 as Chat Server 1
    participant Redis as Redis Session Map
    participant DB as Cassandra Store
    participant WS2 as Chat Server 2
    actor Bob as User B (Receiver)

    Alice->>WS1: 1. Send Message (to: Bob, text: "Hey!")
    WS1->>WS1: 2. Generate Snowflake message_id (1001)
    WS1->>DB: 3. Persist Message in Cassandra
    WS1->>Redis: 4. Lookup Bob's active Chat Server
    Redis-->>WS1: Bob is on Chat Server 2
    WS1->>WS2: 5. Forward Message (to: Bob, msg_id: 1001) via internal RPC
    WS2->>Bob: 6. Push Message over active WebSocket connection
    WS2-->>WS1: 7. Delivery ACK
    WS1-->>Alice: 8. Message Sent ACK (Status: DELIVERED)
```

---

### 2. Small Group Chat Delivery (Max 100 Members)

For small groups ($\le 100\text{ members}$), a **Message Sync Queue per Member** model provides low latency:

```mermaid
flowchart LR
    ALICE["Alice (Sender)"] --> WS["Chat Server"]
    WS --> DB[("Cassandra Store")]
    
    WS --> Q_BOB["Bob's Message Queue"] --> BOB["Bob's App"]
    WS --> Q_CHARLIE["Charlie's Message Queue"] --> CHARLIE["Charlie's App"]
    WS --> Q_DAVID["David's Message Queue"] --> DAVID["David's App"]
```

- Each user has a message inbox queue. When Alice sends a message to the group, the chat server copies the message into Bob, Charlie, and David's inboxes.
- For WeChat and WhatsApp, this model is fast and eliminates complex group locking.

---

### 3. Online Presence & Heartbeat Engine

```mermaid
flowchart TD
    CLIENT["Client Device"] -->|1. Heartbeat Ping every 5s| PRESENCE_SVC["Presence Service"]
    PRESENCE_SVC -->|2. SET user:101:online = 1 (TTL: 30s)| REDIS[("Redis Presence Store")]
    
    CLIENT -.->|Network Drops / No Ping for 30s| EXPIRE["Redis Key Expires"]
    EXPIRE --> PUBLISH["Publish User 101 OFFLINE Event via Redis Pub/Sub"]
    PUBLISH --> FRIENDS["Notify Connected Friends"]
```

- **Heartbeat Mechanism**: Client sends a heartbeat ping to the presence server every $5\text{ seconds}$.
- **Status Expiration**: If no heartbeat is received within $30\text{ seconds}$, the presence status automatically transitions to **Offline**.

---

## 6. Wrap Up & Summary

### Architectural Summary Mindmap

```mermaid
mindmap
  root((Chat System))
    Protocol
      WebSocket for Bi-Directional Push
      Stateless HTTP for Login & Profile
    Storage Tier
      Cassandra Wide-Column for Message History
      Redis for Session & Presence Mapping
    Real-Time Messaging
      1-on-1: Session Map Lookup + Internal RPC
      Group: Inbox Copy per Member (<100 users)
      Offline: Fallback to APNs / FCM Push
    Presence
      Periodic Heartbeat (5s interval, 30s TTL)
      Redis Pub/Sub Fan-Out to Online Friends
```

| Component | Design Choice | Core Rationale |
|:---|:---|:---|
| **Protocol** | WebSockets | Full-duplex persistent connection minimizes TCP handshake latency. |
| **Message Store** | Apache Cassandra | High-velocity append-only writes with sequential chronological reads. |
| **Session Routing** | Redis Global Session Map | Instantly maps `user_id -> chat_server_ip` for cross-node message forwarding. |
| **Presence** | Heartbeat Lease with 30s TTL | Prevents false offline flaps caused by brief mobile network disconnections. |

---

## References

1. Erlang at Facebook (Chat System Architecture): https://www.infoq.com/presentations/erlang-facebook/
2. Discord: How Discord Scaled to 5,000,000 Concurrent Users: https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users
3. Apache Cassandra for Messaging Workloads: https://cassandra.apache.org/
