---
type: Azure Service
title: "Private Endpoints & Service Endpoints Guide"
description: "See [README](./index.md) for overview."
tags: [networking]
timestamp: 2026-06-14T00:00:00Z
---

# Private Endpoints & Service Endpoints Guide

See [README](./index.md) for overview.

## Table of Contents

- [1. Private Endpoints](#1-private-endpoints)
- [2. Service Endpoints](#2-service-endpoints)
- [3. Comparison](#3-comparison)
- [4. When to Use Each](#4-when-to-use-each)

---

## 1. Private Endpoints

### 1.1 What is a Private Endpoint?

A **Private Endpoint** is a **consumer-side** network interface that connects you privately and securely to a service powered by Azure Private Link. The private endpoint uses a private IP address from your VNet, effectively bringing the service into your VNet.

> **Key Concept**: Private Endpoints are always created and owned by the **consumer** (the party accessing the service). The consumer deploys the Private Endpoint in their own VNet and receives a private IP address. The **provider** side exposes its service via a Private Link Service or is a supported Azure PaaS service. This consumer/provider separation is fundamental to Private Link architecture.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Your VNet                                │
│    ┌────────────────────────────────────────────────────────┐   │
│    │                    Subnet                               │   │
│    │   ┌─────────┐         ┌─────────────────┐              │   │
│    │   │   VM    │────────▶│ Private Endpoint │             │   │
│    │   │10.0.1.4 │         │    10.0.1.5      │             │   │
│    │   └─────────┘         └────────┬────────┘             │   │
│    └────────────────────────────────┼────────────────────────┘   │
│                                     │                            │
│                            Private Link Connection               │
│                                     │                            │
└─────────────────────────────────────┼────────────────────────────┘
                                      ▼
                         ┌────────────────────────┐
                         │   Azure PaaS Service   │
                         │  (Storage, SQL, etc.)  │
                         └────────────────────────┘
```

### 1.2 How Private Endpoints Work

1. **Create a Private Endpoint** in your VNet subnet
2. **A private IP address** is assigned from the subnet
3. **A network interface (NIC)** is created for the endpoint
4. **DNS resolution** must be configured to resolve the service FQDN to the private IP
5. **Traffic flows** through the Microsoft backbone network, never the public internet

**Key Points:**
- The PaaS service's public endpoint can optionally be disabled
- Traffic from the VNet to the service uses the private IP
- The private endpoint is a read-only network interface

### 1.3 Private Link Service

**Private Link Service** allows you to expose your own services via private endpoints.

| Component | Description |
|-----------|-------------|
| **Private Link Service** | Your service behind a Standard Load Balancer |
| **Private Endpoint** | Consumer's connection point to your service |
| **NAT IP** | IP address used for source NAT |

**Architecture:**
```
Consumer VNet                              Provider VNet
┌─────────────┐                           ┌─────────────────────┐
│  Private    │                           │  Private Link       │
│  Endpoint   │──── Private Link ────────▶│  Service            │
│             │                           │       │             │
└─────────────┘                           │       ▼             │
                                          │  Load Balancer      │
                                          │       │             │
                                          │       ▼             │
                                          │  Backend VMs        │
                                          └─────────────────────┘
```

### 1.4 When to Use Private Link Service

**Azure Private Link Service** is the recommended solution when you need to expose your own application (hosted on load-balanced Azure VMs) to consumers while meeting the following requirements:

| Requirement | Why Private Link Service Works |
|-------------|--------------------------------------|
| **Accessible from other Azure tenants** | Consumers in different Azure AD tenants can create private endpoints to connect to your Private Link Service |
| **Isolated from the public internet** | All traffic flows over the Microsoft backbone network, never traversing the public internet |
| **Private access from customer VNets** | Consumers connect via private endpoints in their own VNets with private IP addresses |

**Cross-Tenant Architecture:**
```
Provider VNet (Tenant A)              Consumer VNet (Tenant B)
┌──────────────────────────┐          ┌──────────────────────┐
│  Standard Load Balancer  │          │   Consumer App       │
│  (Frontend: 10.0.1.4)    │          │   (VM or Service)    │
└────────────┬─────────────┘          └────────────┬─────────┘
             │                                     │
             │                                     ▼
             │                       ┌──────────────────────┐
             │                       │ Private Endpoint     │
             │                       │ (172.16.1.5)         │
             │                       └──────────┬───────────┘
             │                                  │
             │◀─────── Private Link ───────────│
             │                                  │
             ▼                                  │
  ┌──────────────────┐                         │
  │ Backend Pool     │◀────────────────────────┘
  │ ┌────┐ ┌────┐   │
  │ │VM1 │ │VM2 │   │
  │ └────┘ └────┘   │
  └──────────────────┘
```

**Why Private Link Service?**
- Service Provider Model: You expose a **Private Link Service** that multiple consumers can connect to
- Consumer Creates Private Endpoint: Consumers in other tenants deploy private endpoints in their own VNets
- No Configuration per Customer: Unlike VNet peering or VPNs, no need to configure each consumer
- Automatic Isolation: Each consumer's traffic is isolated; consumers cannot see each other
- Approval Workflow: You can auto-approve or require manual approval

### 1.5 Private Endpoint Connection Management (Provider / Resource Owner)

When a consumer creates a Private Endpoint to your resource (Azure PaaS service or your own Private Link Service), the **Private Link resource owner** has full control over the connection lifecycle. The resource owner can perform the following actions:

| Action | Description |
|--------|-------------|
| **Review** | View all private endpoint connection details — connection name, state, consumer subscription, and the private endpoint resource ID |
| **Approve** | Accept a pending private endpoint connection. Once approved, traffic can flow from the consumer's private endpoint to the provider's resource |
| **Reject** | Deny a pending or even an already-approved private endpoint connection. A rejected connection prevents any data exchange |
| **Delete** | Remove a private endpoint connection from **any state** (Pending, Approved, or Rejected). Deleting the connection on the provider side causes the consumer's private endpoint to enter a disconnected state |

> **Exam Tip:** The Private Link resource owner can perform **all four actions** on private endpoint connections: review, approve, reject, and delete (from any state). This is a distinct set of capabilities from the consumer, who can only create or delete their own Private Endpoint resource.

**Connection States:**

```
Consumer creates          Resource owner
Private Endpoint          reviews request
       │                        │
       ▼                        ▼
  ┌──────────┐    ┌───────────────────────────┐
  │ Pending  │───▶│  Approve  │  Reject       │
  └──────────┘    └─────┬─────────────┬───────┘
                        │             │
                        ▼             ▼
                  ┌──────────┐  ┌──────────┐
                  │ Approved │  │ Rejected │
                  └────┬─────┘  └────┬─────┘
                       │             │
                       ▼             ▼
                 ┌──────────────────────┐
                 │  Delete (any state)  │
                 └──────────────────────┘
```

**Connection State Transitions:**

| State | Consumer Can | Resource Owner Can |
|-------|-------------|-------------------|
| **Pending** | Delete their PE | Approve, Reject, or Delete |
| **Approved** | Delete their PE, send traffic | Reject or Delete |
| **Rejected** | Delete their PE | Delete |
| **Disconnected** | Delete their PE | — (connection removed on provider side) |

**Approval Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Auto-Approval** | Connections from specified subscriptions are automatically approved | Trusted internal subscriptions, same-organization consumers |
| **Manual Approval** | Resource owner must explicitly approve each connection | Cross-tenant or external consumers, stricter security requirements |

**Azure CLI — Managing Private Endpoint Connections:**

```bash
# List all private endpoint connections on a resource
az network private-endpoint-connection list \
  --resource-group MyRG \
  --name MyStorageAccount \
  --type Microsoft.Storage/storageAccounts

# Approve a pending connection
az network private-endpoint-connection approve \
  --resource-group MyRG \
  --resource-name MyStorageAccount \
  --name MyPEConnection \
  --type Microsoft.Storage/storageAccounts

# Reject a connection
az network private-endpoint-connection reject \
  --resource-group MyRG \
  --resource-name MyStorageAccount \
  --name MyPEConnection \
  --type Microsoft.Storage/storageAccounts

# Delete a connection (works from any state)
az network private-endpoint-connection delete \
  --resource-group MyRG \
  --resource-name MyStorageAccount \
  --name MyPEConnection \
  --type Microsoft.Storage/storageAccounts
```

**Reference:** [Manage Private Endpoint connections | Microsoft Learn](https://learn.microsoft.com/en-us/azure/private-link/manage-private-endpoint)

### 1.6 DNS Configuration

Proper DNS configuration is **critical** for private endpoints. The service FQDN must resolve to the private IP address.

**DNS Resolution Options:**

| Option | Description | Use Case |
|--------|-------------|----------|
| **Azure Private DNS Zone** | Automatic DNS resolution in VNet | Recommended for Azure-native solutions |
| **Custom DNS Server** | Forward queries to Azure DNS | Hybrid environments |
| **Host File** | Manual entry on each machine | Testing only |

**Private DNS Zone Names for Common Services:**

| Service | Private DNS Zone |
|---------|------------------|
| Azure Storage (Blob) | `privatelink.blob.core.windows.net` |
| Azure Storage (File) | `privatelink.file.core.windows.net` |
| Azure SQL Database | `privatelink.database.windows.net` |
| Azure Cosmos DB | `privatelink.documents.azure.com` |
| Azure Key Vault | `privatelink.vaultcore.azure.net` |
| Azure Container Registry | `privatelink.azurecr.io` |

**DNS Resolution Flow:**
```
Application queries: mystorageaccount.blob.core.windows.net
         │
         ▼
CNAME: mystorageaccount.privatelink.blob.core.windows.net
         │
         ▼
Private DNS Zone resolves to: 10.0.1.5 (private endpoint IP)
```

### 1.7 DNS for Hybrid/On-Premises Access

When on-premises clients need to access Azure PaaS services through Private Endpoints, DNS resolution requires special configuration.

**The Challenge:**
- On-premises clients cannot directly query Azure Private DNS zones
- The Azure-provided DNS (168.63.129.16) is only accessible from within Azure VMs
- Public DNS zones return public IPs, bypassing the private endpoint

**Solution: DNS Forwarder**

```
On-Premises DNS Server
       │
       ├── Conditional Forwarder for contoso.com
       └──▶ Forwards to VM1 (DNS Forwarder in Azure)
                    │
                    ▼
            VM1 (Azure VNet)
                    │
                    ├── Conditional Forwarder
                    └──▶ Forward to 168.63.129.16 (Azure-Provided DNS)
                             │
                             ▼
                    Private DNS Zone
                    (Linked to VNet)
                             │
                             ▼
                    Resolves to PE IP (10.0.2.5)
```

**Configuration:**
- **VM1**: Acts as DNS forwarder in Azure VNet with access to private DNS zones
- **On-Premises DNS**: Forwards queries to VM1
- **Private DNS Zone**: Linked to VNet, resolves to private endpoint IPs

**Why 168.63.129.16?**
- Special Azure wireserver IP accessible **only from within Azure VMs**
- Automatically resolves names in **private DNS zones linked to the VNet**
- Cannot be reached directly from on-premises networks

**Why NOT Public DNS?**
- Public DNS resolves to public IP addresses
- Exposes traffic to the public internet
- Defeats the purpose of private connectivity

**Why NOT Azure DNS Private Resolver?**
- Resolver is for **hybrid scenarios** (on-premises ↔ Azure)
- Not required when both resources are in the same VNet
- Adds complexity for pure Azure-to-Azure scenarios

### 1.8 Supported Services

Private Endpoints are supported for:

| Category | Services |
|----------|----------|
| **Storage** | Blob, File, Queue, Table, Data Lake Gen2 |
| **Databases** | SQL Database, Cosmos DB, PostgreSQL, MySQL, MariaDB |
| **Analytics** | Synapse Analytics, Event Hubs, Service Bus |
| **Security** | Key Vault |
| **Containers** | Container Registry, Kubernetes Service |
| **AI/ML** | Cognitive Services, Machine Learning |
| **Integration** | App Configuration, Event Grid |
| **Compute** | App Service, Functions (Premium plan) |

### 1.9 Benefits

| Benefit | Description |
|---------|-------------|
| **Security** | Traffic never traverses the public internet |
| **Data Exfiltration Protection** | Only access specific resources, not entire services |
| **On-premises Access** | Connect via VPN/ExpressRoute to private endpoints |
| **Cross-region** | Access services in different regions privately |
| **No Public IP Required** | Resources don't need public IPs to access PaaS services |

### 1.10 Common Scenarios

**Securing with Private Endpoint:**

```
App Service (VNet-integrated) ──▶ Private Endpoint ──▶ Storage Account
                                   (Private IP)       (Public: Disabled)
```

**On-Premises Access:**
```
On-Prem Server ──VPN──▶ Azure VNet ──▶ Private Endpoint ──▶ SQL DB
```

---

## 2. Service Endpoints

### 2.1 What are Service Endpoints?

**Service Endpoints** extend your VNet identity to Azure services, enabling secure access over an optimized route.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your VNet (10.0.0.0/16)                      │
│  ┌─────────────────────┐                                        │
│  │   Subnet            │                                        │
│  │   Service Endpoint: │                                        │
│  │   Microsoft.Storage │─────────▶ Azure Storage Account        │
│  │                     │           (Public endpoint secured     │
│  │   ┌─────┐           │            to allow only this VNet)    │
│  │   │ VM  │           │                                        │
│  │   └─────┘           │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Traffic goes over Azure backbone (optimized route)
- Service still uses its **public IP address**
- VNet identity is presented to the service
- Service firewall rules can restrict to specific VNets
- No additional cost

### 2.2 How They Work

Virtual Network service endpoints provide secure and direct connectivity to Azure services over an optimized route over the Azure backbone network. Endpoints allow you to secure your critical Azure service resources to only your virtual networks.

Service Endpoints enable private IP addresses in the VNet to reach the endpoint of an Azure service without needing a public IP address on the VNet.

### 2.3 Practical Example

**Scenario:** Ensuring traffic travels via Microsoft backbone

Your on-premises network has a VPN gateway. You have:
- **vgw1**: Virtual network gateway
- **storage1**: Storage account
- **Vnet1**: Virtual network (forced tunneling enabled)
- **VM1**: Virtual machine in Vnet1

**Requirement:** All traffic from VM1 to storage1 travels on Microsoft backbone

**Solution:** Service Endpoints ✅

| Why It Works |
|---|
| Provides secure and direct connectivity to Azure Storage over optimized route via Azure backbone |
| When you enable service endpoint for Azure Storage on the subnet where VM1 is located |
| Traffic from VM1 to storage1 uses Azure backbone instead of internet or VPN |

---

## 3. Comparison

> **Important**: A **Private Endpoint is a consumer-side resource**. It is created in the **consumer's VNet** and represents the consumer's private connection to a service. The consumer owns and manages the Private Endpoint, while the provider exposes its service via Private Link. This means:
> - The **consumer** decides where to place the Private Endpoint and which subnet/IP to use
> - The **provider** has no access to the consumer's VNet — only the Private Link connection is shared
> - The **provider** can approve or reject Private Endpoint connection requests
> - Multiple consumers can each create their own Private Endpoints to the same provider service, fully isolated from each other

**Consumer vs Provider Model:**
```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│         CONSUMER SIDE           │     │          PROVIDER SIDE          │
│                                 │     │                                 │
│  Private Endpoint (10.0.1.5)   │────▶│  Private Link Service / PaaS   │
│  - Created by consumer          │     │  - Exposes the service          │
│  - Lives in consumer's VNet     │     │  - Approves connections         │
│  - Consumer manages DNS         │     │  - Provider manages backend     │
└─────────────────────────────────┘     └─────────────────────────────────┘
```

| Feature | Service Endpoint | Private Endpoint (Consumer-Side) |
|---------|------------------|----------------------------------|
| **Ownership** | Configured on consumer's subnet | Created in consumer's VNet as a consumer-owned resource |
| **IP Address Used** | Service's public IP | Private IP from consumer's VNet |
| **Traffic Path** | Azure backbone (optimized) | Azure backbone (Private Link) |
| **On-premises Access** | Not supported | Supported via VPN/ExpressRoute |
| **Cross-region** | Limited | Fully supported |
| **DNS Changes** | Not required | Required (consumer must configure) |
| **Cost** | Free | Per hour + data processing |
| **Data Exfiltration Protection** | Limited (entire service) | Strong (specific resource) |
| **Disable Public Access** | No (public IP still used) | Yes (can fully disable) |
| **Multi-tenant isolation** | N/A | Each consumer gets isolated connection |

---

## 4. When to Use Each

**Use Service Endpoints when:**
- Simple setup is needed
- Cost is a concern
- Traffic only originates from Azure VNet
- Basic network isolation is sufficient
- Example: VMs accessing Storage Account

**Use Private Endpoints when:**
- On-premises resources need access
- You want to disable public access completely
- Cross-region private connectivity is needed
- Data exfiltration protection is critical
- Compliance requires no public IP exposure
- Example: App Service to SQL Database with complete public isolation

---

## Related Reading

- [Private Endpoint Overview](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [Service Endpoints Overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-service-endpoints-overview)
- [Private DNS Resolution](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
