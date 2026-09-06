---
type: Azure Service
title: "Azure Networking Fundamentals - Hybrid Connections in App Service"
description: "**Hybrid Connections** is an Azure Relay feature that enables Azure App Service and Azure Functions to securely access on-premises resources without requiring firewall changes or VPN infrastructure."
tags: [networking]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Networking Fundamentals - Hybrid Connections in App Service

## 8. Hybrid Connections (App Service Feature)

### 8.1 What are App Service Hybrid Connections?

**Hybrid Connections** is an Azure Relay feature that enables Azure App Service and Azure Functions to securely access on-premises resources without requiring firewall changes or VPN infrastructure.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Azure                                       │
│   ┌─────────────────┐         ┌─────────────────────────────────┐       │
│   │   App Service   │────────▶│      Azure Relay Service        │       │
│   │   or Functions  │         │    (Hybrid Connection Endpoint) │       │
│   └─────────────────┘         └──────────────┬──────────────────┘       │
└──────────────────────────────────────────────┼──────────────────────────┘
                                               │
                                     Outbound HTTPS (443)
                                        WebSocket
                                               │
┌──────────────────────────────────────────────┼──────────────────────────┐
│                        On-Premises Network   │                          │
│   ┌───────────────────────────────┐         │                          │
│   │  Hybrid Connection Manager    │◀────────┘                          │
│   │  (Windows Service)            │                                     │
│   └──────────────┬────────────────┘                                     │
│                  │                                                      │
│                  ▼                                                      │
│   ┌──────────────────────────────┐                                      │
│   │   On-Premises Resource       │                                      │
│   │   (SQL Server, Web Service,  │                                      │
│   │    File Share, etc.)         │                                      │
│   └──────────────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 How Hybrid Connections Work

Hybrid Connections use **Azure Relay** to establish a secure tunnel between Azure services and on-premises resources.

**Connection Flow:**

1. **Hybrid Connection Manager (HCM)** installed on-premises initiates an **outbound** connection to Azure Relay
2. The connection uses **port 443 (HTTPS)** with WebSocket protocol
3. App Service/Functions connects to Azure Relay
4. Azure Relay routes traffic through the established tunnel to HCM
5. HCM forwards the request to the on-premises resource

**Key Characteristics:**

| Feature | Description |
|---------|-------------|
| **Protocol** | TCP-based (HTTP, SQL, custom TCP) |
| **Direction** | Outbound from on-premises (no inbound firewall rules needed) |
| **Port** | Uses port 443 (HTTPS) for relay connection |
| **Authentication** | SAS (Shared Access Signature) tokens |
| **Encryption** | TLS 1.2 encrypted |
| **No VPN Required** | Works without VPN or ExpressRoute |

### 8.3 Hybrid Connection Manager

The **Hybrid Connection Manager (HCM)** is a Windows service that runs on-premises and manages the connection to Azure Relay.

**Requirements:**

| Requirement | Details |
|-------------|---------|
| **Operating System** | Windows Server 2012 or later, Windows 10 |
| **Outbound Connectivity** | Port 443 to Azure Relay endpoints |
| **Memory** | Minimal (~50 MB per connection) |
| **Network Access** | Must reach on-premises target resources |

**HCM Installation Steps:**
1. Create Hybrid Connection in Azure Portal (App Service → Networking → Hybrid Connections)
2. Download HCM installer from Azure Portal
3. Install on a machine that can reach the target resource
4. Configure the connection using the connection string

**Multiple Listeners:**
- You can install HCM on multiple machines for high availability
- Azure Relay load balances across available listeners

### 8.4 Use Cases

| Use Case | Example |
|----------|---------|
| **Database Access** | App Service connecting to on-premises SQL Server |
| **Legacy APIs** | Calling internal REST/SOAP services without exposing them |
| **File Access** | Accessing on-premises file shares |
| **Internal Systems** | Integrating with ERP, CRM, or other LOB applications |
| **Development/Testing** | Connecting to dev resources during migration |

**Example: Connecting to On-Premises SQL Server**

```
Hybrid Connection Configuration:
├── Endpoint Host: sqlserver.internal.company.com
├── Endpoint Port: 1433
└── Relay Namespace: myapp-relay.servicebus.windows.net

Connection String in App Service:
Server=sqlserver.internal.company.com,1433;Database=MyDB;...
```

The application uses the **same connection string** as if it were on-premises. The Hybrid Connection transparently routes traffic through Azure Relay.

### 8.5 Limitations

| Limitation | Description |
|------------|-------------|
| **Windows Only** | HCM runs only on Windows |
| **TCP Only** | No UDP support |
| **No Network Discovery** | Must specify exact hostname:port |
| **App Service Plans** | Requires Basic tier or higher |
| **Connection Limit** | Varies by plan (20-200 connections) |
| **No Wildcard** | Each endpoint requires a separate Hybrid Connection |
| **Latency** | Higher latency than VPN due to relay hop |

**Hybrid Connection Limits by Plan:**

| App Service Plan | Max Hybrid Connections |
|------------------|------------------------|
| Basic | 5 |
| Standard | 25 |
| Premium v2/v3 | 200 |
| Isolated | 200 |

### 8.6 Hybrid Connections vs VNet Integration vs Private Endpoints

| Feature | Hybrid Connections | VNet Integration | Private Endpoints |
|---------|-------------------|------------------|-------------------|
| **Target** | On-premises resources | Azure VNet resources | Azure PaaS services |
| **Setup Complexity** | Low (no VPN needed) | Medium | Medium |
| **Agent Required** | Yes (HCM on Windows) | No | No |
| **Network Changes** | None (outbound only) | Subnet delegation | Subnet + DNS |
| **Protocol** | TCP only | All | All |
| **Latency** | Higher (relay hop) | Lower | Lowest |
| **Cost** | Per connection/hour | Included in plan | Per endpoint/hour |
| **On-premises Access** | Yes | Via VPN/ExpressRoute | Via VPN/ExpressRoute |

**When to Use Each:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Decision Tree                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Need to access on-premises resources?                          │
│  ├── Yes, simple setup needed ──────▶ Hybrid Connections        │
│  ├── Yes, full network integration ──▶ VNet + VPN/ExpressRoute  │
│  └── No                                                          │
│       │                                                          │
│       ▼                                                          │
│  Need to access Azure PaaS services privately?                  │
│  ├── Yes ──────────────────────────▶ Private Endpoints          │
│  └── No, just route optimization ──▶ Service Endpoints          │
│                                                                  │
│  Need App Service to access VNet resources?                     │
│  └── Yes ──────────────────────────▶ VNet Integration           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

