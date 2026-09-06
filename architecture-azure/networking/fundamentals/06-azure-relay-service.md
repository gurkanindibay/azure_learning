---
type: Azure Service
title: "Azure Networking Fundamentals - Azure Relay Service"
description: "**Azure Relay** is a cloud service that enables you to securely expose services running behind a firewall or NAT to the public cloud, without opening inbound firewall ports. It acts as a \"meeting p..."
tags: [networking]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Networking Fundamentals - Azure Relay Service

## 7. Azure Relay Service

### 7.1 What is Azure Relay?

**Azure Relay** is a cloud service that enables you to securely expose services running behind a firewall or NAT to the public cloud, without opening inbound firewall ports. It acts as a "meeting point" in the cloud where both parties (sender and listener) connect outbound.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           AZURE RELAY                                       │
│                                                                             │
│    The "Meeting Point" in the Cloud                                        │
│                                                                             │
│    ┌─────────────────────────────────────────────────────────────────┐    │
│    │                    Azure Relay Namespace                         │    │
│    │                 (mycompany.servicebus.windows.net)              │    │
│    │                                                                  │    │
│    │    ┌──────────────────┐      ┌──────────────────────┐          │    │
│    │    │   WCF Relays     │      │  Hybrid Connections   │          │    │
│    │    │   (Legacy .NET)  │      │  (Modern, Any Client) │          │    │
│    │    └──────────────────┘      └──────────────────────┘          │    │
│    └─────────────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
          ▲                                              ▲
          │                                              │
    Outbound Connection                           Outbound Connection
    (HTTPS/WebSocket)                             (HTTPS/WebSocket)
          │                                              │
          │                                              │
┌─────────┴─────────┐                        ┌──────────┴──────────┐
│  On-Premises      │                        │    Cloud Client     │
│  Service          │                        │    (App Service,    │
│  (Listener)       │                        │     Custom App)     │
│                   │                        │    (Sender)         │
└───────────────────┘                        └─────────────────────┘
     Behind Firewall                              In Azure/Internet
     No Inbound Ports
```

### 7.2 The Problem Azure Relay Solves

**Traditional Problem:**
```
┌─────────────────────┐          ┌─────────────────────┐
│   Cloud Client      │          │   On-Premises       │
│                     │    ✗     │   ┌─────────────┐   │
│   Wants to call     │──────────│───│  Firewall   │   │
│   on-prem service   │  BLOCKED │   └─────────────┘   │
│                     │          │   ┌─────────────┐   │
└─────────────────────┘          │   │   Service   │   │
                                 │   └─────────────┘   │
                                 └─────────────────────┘

Problem: Inbound connections blocked by corporate firewall
Traditional Solution: Open firewall ports (security risk!) or VPN (complex/expensive)
```

**Azure Relay Solution:**
```
┌─────────────────────┐     ┌─────────────────┐     ┌─────────────────────┐
│   Cloud Client      │     │   Azure Relay   │     │   On-Premises       │
│                     │     │                 │     │                     │
│   1. Connect to     │────▶│  3. Routes      │◀────│  2. Listener        │
│      Relay          │     │     messages    │     │     connects OUT    │
│      (outbound)     │     │     between     │     │     to Relay        │
│                     │     │     parties     │     │     (outbound)      │
└─────────────────────┘     └─────────────────┘     └─────────────────────┘

✓ No inbound firewall ports needed
✓ Both sides initiate OUTBOUND connections
✓ Relay acts as the rendezvous point
```

### 7.3 Azure Relay Components

| Component | Description |
|-----------|-------------|
| **Relay Namespace** | Container for relay entities (like `mycompany.servicebus.windows.net`) |
| **WCF Relay** | Supports WCF bindings for .NET applications |
| **Hybrid Connection** | Protocol-agnostic, WebSocket-based connection |
| **Listener** | The on-premises service that registers with the relay |
| **Sender** | The client that wants to communicate with the listener |
| **SAS Policy** | Shared Access Signature for authentication |

**Namespace Structure:**
```
Azure Relay Namespace: mycompany.servicebus.windows.net
├── WCF Relays
│   ├── myservice (NetTcpRelayBinding)
│   └── myapi (BasicHttpRelayBinding)
│
└── Hybrid Connections
    ├── sqlserver-connection
    └── internal-api-connection
```

### 7.4 WCF Relays

**WCF Relays** are the original relay mechanism, designed for .NET WCF (Windows Communication Foundation) services. They support various WCF bindings that route traffic through Azure.

**WCF Relay Bindings:**

| Binding | Description | Use Case |
|---------|-------------|----------|
| **NetTcpRelayBinding** | Binary, TCP-based | High performance .NET to .NET |
| **BasicHttpRelayBinding** | SOAP/HTTP | Interoperability with non-.NET clients |
| **WebHttpRelayBinding** | REST/HTTP | REST services |
| **NetEventRelayBinding** | Multicast events | Pub/sub scenarios |
| **NetOnewayRelayBinding** | One-way messaging | Fire and forget |

**WCF Relay Architecture:**

```
┌───────────────────────────────────────────────────────────────────┐
│                        Azure Relay                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    WCF Relay Endpoint                        │  │
│  │              sb://mycompany.servicebus.windows.net/myservice │  │
│  └─────────────────────────────────────────────────────────────┘  │
│         ▲                                          ▲               │
│         │ WebSocket/TCP                            │ WebSocket/TCP │
│         │                                          │               │
└─────────┼──────────────────────────────────────────┼───────────────┘
          │                                          │
┌─────────┴─────────┐                    ┌───────────┴───────────┐
│   WCF Client      │                    │   WCF Service         │
│   (.NET)          │                    │   (On-Premises)       │
│                   │                    │                       │
│   var client =    │                    │   ServiceHost host =  │
│   new MyClient(); │                    │   new ServiceHost();  │
│   client.DoWork();│                    │   host.Open();        │
└───────────────────┘                    └───────────────────────┘
```

**Example WCF Service with Relay:**

```csharp
// On-Premises WCF Service (Listener)
ServiceHost host = new ServiceHost(typeof(MyService));

// Add relay endpoint
host.AddServiceEndpoint(
    typeof(IMyService),
    new NetTcpRelayBinding(),
    ServiceBusEnvironment.CreateServiceUri("sb", "mycompany", "myservice")
);

// Add relay credentials
host.Description.Behaviors.Add(new TransportClientEndpointBehavior
{
    TokenProvider = TokenProvider.CreateSharedAccessSignatureTokenProvider(
        "ListenPolicy", "your-sas-key")
});

host.Open();
Console.WriteLine("Service listening via Azure Relay...");
```

```csharp
// Cloud Client (Sender)
var factory = new ChannelFactory<IMyService>(
    new NetTcpRelayBinding(),
    new EndpointAddress(ServiceBusEnvironment.CreateServiceUri("sb", "mycompany", "myservice"))
);

factory.Endpoint.Behaviors.Add(new TransportClientEndpointBehavior
{
    TokenProvider = TokenProvider.CreateSharedAccessSignatureTokenProvider(
        "SendPolicy", "your-sas-key")
});

IMyService client = factory.CreateChannel();
client.DoWork(); // Call goes through Azure Relay to on-premises
```

### 7.5 Hybrid Connections (Azure Relay Feature)

**Hybrid Connections** are the modern, protocol-agnostic relay mechanism. Unlike WCF Relays, they work with any language and platform.

**Key Differences from WCF Relays:**

| Aspect | WCF Relay | Hybrid Connections |
|--------|-----------|-------------------|
| **Protocol** | WCF-specific bindings | WebSocket-based, any TCP protocol |
| **Platform** | .NET only | Any platform (Node.js, Java, .NET, etc.) |
| **Connection** | Service Bus messaging | Direct WebSocket tunnel |
| **Use Case** | Legacy WCF services | Modern applications, App Service |

**Hybrid Connection Architecture:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                           Azure Relay                                   │
│    ┌────────────────────────────────────────────────────────────────┐  │
│    │              Hybrid Connection: "my-sql-connection"             │  │
│    │     Endpoint: mycompany.servicebus.windows.net/my-sql-connection│  │
│    │                                                                  │  │
│    │    ┌──────────────────────────────────────────────────────┐    │  │
│    │    │              WebSocket Rendezvous                     │    │  │
│    │    │                                                        │    │  │
│    │    │   Sender ◀────── Bi-directional Stream ──────▶ Listener│    │  │
│    │    │                                                        │    │  │
│    │    └──────────────────────────────────────────────────────┘    │  │
│    └────────────────────────────────────────────────────────────────┘  │
│              ▲                                           ▲              │
│              │ WebSocket                                 │ WebSocket    │
│              │ (wss://)                                  │ (wss://)     │
└──────────────┼───────────────────────────────────────────┼──────────────┘
               │                                           │
┌──────────────┴──────────────┐          ┌─────────────────┴─────────────┐
│   Sender Application        │          │   Listener Application        │
│   (Cloud/Internet)          │          │   (On-Premises)               │
│                             │          │                                │
│   • App Service             │          │   • Hybrid Connection Manager  │
│   • Azure Functions         │          │   • Custom Listener Code       │
│   • Custom Application      │          │                                │
└─────────────────────────────┘          └────────────────────────────────┘
```

**Hybrid Connection Request Flow:**

```
Step-by-Step Flow:

1. LISTENER REGISTRATION
   On-Premises ──────▶ Azure Relay
   "I'm listening on 'my-sql-connection'"
   (Outbound WebSocket connection, kept alive)

2. SENDER CONNECTS
   App Service ──────▶ Azure Relay
   "Connect me to 'my-sql-connection'"
   (Outbound WebSocket connection)

3. RELAY RENDEZVOUS
   Azure Relay creates a bi-directional channel
   between Sender and Listener WebSockets

4. DATA TRANSFER
   App Service ◀──────▶ Azure Relay ◀──────▶ On-Premises
   TCP data streams through the WebSocket tunnel

5. CONNECTION CLOSE
   Either party can close; relay cleans up
```

### 7.6 WCF Relays vs Hybrid Connections

| Feature | WCF Relay | Hybrid Connections |
|---------|-----------|-------------------|
| **Protocol Support** | WCF bindings only | Any TCP protocol |
| **Language Support** | .NET Framework | Any (Node.js, Java, .NET Core, etc.) |
| **Message Size** | 64 KB - 256 KB | Streaming (no message limit) |
| **Connection Type** | Request/Response or One-way | Bi-directional stream |
| **App Service Integration** | No | Yes (built-in) |
| **Discovery** | ATOM feed | REST API |
| **Recommended For** | Legacy WCF services | New development |

**Decision Guide:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     Which Relay Type?                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Do you have existing WCF services?                             │
│  ├── Yes ──────────────────────────▶ WCF Relay                  │
│  └── No                                                          │
│       │                                                          │
│       ▼                                                          │
│  Are you using App Service/Functions?                           │
│  ├── Yes ──────────────────────────▶ Hybrid Connections         │
│  └── No                              (App Service feature)       │
│       │                                                          │
│       ▼                                                          │
│  Need custom relay logic?                                       │
│  ├── Yes ──────────────────────────▶ Hybrid Connections         │
│  └── No ───────────────────────────▶ Hybrid Connections         │
│                                      (with custom listener)      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.7 Authentication and Security

Azure Relay uses **Shared Access Signature (SAS)** for authentication.

**SAS Policies:**

| Policy Right | Description | Who Uses It |
|--------------|-------------|-------------|
| **Listen** | Register as a listener | On-premises service |
| **Send** | Connect to relay as sender | Cloud clients |
| **Manage** | Create/delete relay entities | Administrators |

**Security Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Relay Namespace                         │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Shared Access Policies                      │   │
│   │  ┌─────────────────┐  ┌─────────────────┐               │   │
│   │  │ ListenPolicy    │  │ SendPolicy      │               │   │
│   │  │ Rights: Listen  │  │ Rights: Send    │               │   │
│   │  │ Key: xxxxx      │  │ Key: yyyyy      │               │   │
│   │  └─────────────────┘  └─────────────────┘               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              TLS 1.2 Encryption (Always)                 │   │
│   │              • Data in transit encrypted                 │   │
│   │              • WebSocket over HTTPS (wss://)            │   │
│   │              • No data stored in relay                   │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.8 Pricing

Azure Relay pricing is based on:

| Component | Cost Basis |
|-----------|------------|
| **Listener Hours** | Per hour per active listener |
| **Hybrid Connection** | Per connection per hour |
| **Messages (WCF)** | Per 10,000 messages |
| **Data Transfer** | Standard Azure data transfer rates |

---

