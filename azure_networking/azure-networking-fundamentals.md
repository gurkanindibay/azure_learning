# Azure Networking Fundamentals

## Table of Contents

- [1. Overview](#1-overview)
- [2. Azure Virtual Network (VNet)](#2-azure-virtual-network-vnet)
  - [2.1 What is a VNet?](#21-what-is-a-vnet)
  - [2.2 Key Concepts](#22-key-concepts)
  - [2.3 Subnets](#23-subnets)
  - [2.4 Address Space](#24-address-space)
  - [2.5 VNet Peering](#25-vnet-peering)
  - [2.6 Network Security Groups (NSG)](#26-network-security-groups-nsg)
- [3. Private Endpoints](#3-private-endpoints)
  - [3.1 What is a Private Endpoint?](#31-what-is-a-private-endpoint)
  - [3.2 How Private Endpoints Work](#32-how-private-endpoints-work)
  - [3.3 Private Link Service](#33-private-link-service)
  - [3.4 DNS Configuration](#34-dns-configuration)
  - [3.5 Supported Services](#35-supported-services)
  - [3.6 Benefits of Private Endpoints](#36-benefits-of-private-endpoints)
- [4. Service Endpoints vs Private Endpoints](#4-service-endpoints-vs-private-endpoints)
  - [4.1 Service Endpoints](#41-service-endpoints)
  - [4.2 Comparison Table](#42-comparison-table)
  - [4.3 When to Use Each](#43-when-to-use-each)
- [5. VPN vs Private Link](#5-vpn-vs-private-link)
  - [5.1 Understanding the Fundamental Difference](#51-understanding-the-fundamental-difference)
  - [5.2 Azure VPN Gateway](#52-azure-vpn-gateway)
  - [5.3 Azure Private Link](#53-azure-private-link)
  - [5.4 Detailed Comparison](#54-detailed-comparison)
  - [5.5 Architecture Diagrams](#55-architecture-diagrams)
  - [5.6 Use Case Scenarios](#56-use-case-scenarios)
  - [5.7 Can They Work Together?](#57-can-they-work-together)
  - [5.8 Decision Matrix](#58-decision-matrix)
- [6. Azure Relay Service](#6-azure-relay-service)
  - [6.1 What is Azure Relay?](#61-what-is-azure-relay)
  - [6.2 The Problem Azure Relay Solves](#62-the-problem-azure-relay-solves)
  - [6.3 Azure Relay Components](#63-azure-relay-components)
  - [6.4 WCF Relays](#64-wcf-relays)
  - [6.5 Hybrid Connections (Azure Relay Feature)](#65-hybrid-connections-azure-relay-feature)
  - [6.6 WCF Relays vs Hybrid Connections](#66-wcf-relays-vs-hybrid-connections)
  - [6.7 Authentication and Security](#67-authentication-and-security)
  - [6.8 Pricing](#68-pricing)
- [7. Hybrid Connections (App Service Feature)](#7-hybrid-connections-app-service-feature)
  - [7.1 What are App Service Hybrid Connections?](#71-what-are-app-service-hybrid-connections)
  - [7.2 How Hybrid Connections Work](#72-how-hybrid-connections-work)
  - [7.3 Hybrid Connection Manager](#73-hybrid-connection-manager)
  - [7.4 Use Cases](#74-use-cases)
  - [7.5 Limitations](#75-limitations)
  - [7.6 Hybrid Connections vs VNet Integration vs Private Endpoints](#76-hybrid-connections-vs-vnet-integration-vs-private-endpoints)
- [8. Common Networking Scenarios](#8-common-networking-scenarios)
  - [8.1 Securing Azure Storage with Private Endpoint](#81-securing-azure-storage-with-private-endpoint)
  - [8.2 Securing Azure SQL Database](#82-securing-azure-sql-database)
  - [8.3 Securing Azure Key Vault](#83-securing-azure-key-vault)
  - [8.4 Securing Azure Cosmos DB](#84-securing-azure-cosmos-db)
- [9. Network Architecture Best Practices](#9-network-architecture-best-practices)
- [10. Summary Table](#10-summary-table)

---

## 1. Overview

Azure networking services provide the foundation for connecting and securing Azure resources. Understanding Virtual Networks (VNets) and Private Endpoints is essential because many Azure services reference these concepts for secure connectivity.

Key networking concepts covered in this document:
- **Virtual Networks (VNets)**: Isolated network environments in Azure
- **Private Endpoints**: Private IP connections to Azure PaaS services
- **Service Endpoints**: Optimized routing to Azure services
- **Network Security Groups**: Traffic filtering rules

---

## 2. Azure Virtual Network (VNet)

### 2.1 What is a VNet?

An **Azure Virtual Network (VNet)** is the fundamental building block for your private network in Azure. It enables Azure resources to securely communicate with each other, the internet, and on-premises networks.

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Virtual Network                     │
│                    (Address Space: 10.0.0.0/16)             │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │   Subnet 1          │    │   Subnet 2          │        │
│  │   10.0.1.0/24       │    │   10.0.2.0/24       │        │
│  │  ┌─────┐  ┌─────┐   │    │  ┌─────┐  ┌─────┐  │        │
│  │  │ VM1 │  │ VM2 │   │    │  │ VM3 │  │ AKS │  │        │
│  │  └─────┘  └─────┘   │    │  └─────┘  └─────┘  │        │
│  └─────────────────────┘    └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Key Concepts

| Concept | Description |
|---------|-------------|
| **Isolation** | VNets are logically isolated from each other |
| **Region-scoped** | A VNet exists within a single Azure region |
| **Subscription-bound** | VNets belong to a single subscription |
| **Segmentation** | Divide VNets into subnets for organization |
| **Communication** | Resources in a VNet can communicate by default |

### 2.3 Subnets

Subnets allow you to segment the VNet into smaller networks. Each subnet contains a range of IP addresses from the VNet's address space.

**Subnet Types:**

| Subnet Type | Purpose | Example |
|-------------|---------|---------|
| **Default** | General-purpose resources | VMs, App Services |
| **Gateway** | VPN/ExpressRoute gateways | Must be named `GatewaySubnet` |
| **Bastion** | Azure Bastion host | Must be named `AzureBastionSubnet` |
| **Firewall** | Azure Firewall | Must be named `AzureFirewallSubnet` |
| **Private Endpoint** | Private endpoints for PaaS services | Any name, dedicated for endpoints |

**Reserved Addresses:**
Azure reserves 5 IP addresses in each subnet:
- `x.x.x.0` - Network address
- `x.x.x.1` - Default gateway
- `x.x.x.2, x.x.x.3` - Azure DNS
- `x.x.x.255` - Broadcast address

### 2.4 Address Space

VNets use **CIDR notation** for address space definition. Common private IP ranges:

| Range | CIDR | Available IPs |
|-------|------|---------------|
| 10.0.0.0 - 10.255.255.255 | 10.0.0.0/8 | 16,777,216 |
| 172.16.0.0 - 172.31.255.255 | 172.16.0.0/12 | 1,048,576 |
| 192.168.0.0 - 192.168.255.255 | 192.168.0.0/16 | 65,536 |

**Example Address Planning:**
```
VNet: 10.0.0.0/16 (65,536 addresses)
├── Subnet-Web: 10.0.1.0/24 (256 addresses)
├── Subnet-App: 10.0.2.0/24 (256 addresses)
├── Subnet-DB: 10.0.3.0/24 (256 addresses)
├── Subnet-PrivateEndpoints: 10.0.4.0/24 (256 addresses)
└── GatewaySubnet: 10.0.255.0/27 (32 addresses)
```

### 2.5 VNet Peering

**VNet Peering** connects two VNets, enabling resources to communicate across VNets using private IP addresses.

| Peering Type | Description | Traffic Path |
|--------------|-------------|--------------|
| **Regional Peering** | VNets in the same region | Azure backbone |
| **Global Peering** | VNets in different regions | Azure backbone |

**Key Characteristics:**
- Low latency, high bandwidth connection
- Traffic stays on Microsoft network (no public internet)
- Non-transitive by default (A↔B and B↔C doesn't mean A↔C)
- Can peer across subscriptions and tenants

### 2.6 Network Security Groups (NSG)

**Network Security Groups** contain security rules that filter network traffic to and from Azure resources.

```
┌────────────────────────────────────────────┐
│            Network Security Group          │
├────────────────────────────────────────────┤
│ Inbound Rules                              │
│ ├── Priority 100: Allow HTTPS (443)        │
│ ├── Priority 200: Allow SSH (22) from VNet │
│ └── Priority 65500: Deny All               │
├────────────────────────────────────────────┤
│ Outbound Rules                             │
│ ├── Priority 100: Allow Internet           │
│ └── Priority 65500: Deny All               │
└────────────────────────────────────────────┘
```

**Rule Properties:**
- **Priority**: 100-4096 (lower = higher priority)
- **Source/Destination**: IP, Service Tag, or ASG
- **Protocol**: TCP, UDP, ICMP, or Any
- **Port Range**: Single port or range
- **Action**: Allow or Deny

---

## 3. Private Endpoints

### 3.1 What is a Private Endpoint?

A **Private Endpoint** is a network interface that connects you privately and securely to a service powered by Azure Private Link. The private endpoint uses a private IP address from your VNet, effectively bringing the service into your VNet.

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

### 3.2 How Private Endpoints Work

1. **Create a Private Endpoint** in your VNet subnet
2. **A private IP address** is assigned from the subnet
3. **A network interface (NIC)** is created for the endpoint
4. **DNS resolution** must be configured to resolve the service FQDN to the private IP
5. **Traffic flows** through the Microsoft backbone network, never the public internet

**Key Points:**
- The PaaS service's public endpoint can optionally be disabled
- Traffic from the VNet to the service uses the private IP
- The private endpoint is a read-only network interface

### 3.3 Private Link Service

**Private Link Service** allows you to expose your own services via private endpoints.

| Component | Description |
|-----------|-------------|
| **Private Link Service** | Your service behind a Standard Load Balancer |
| **Private Endpoint** | Consumer's connection point to your service |
| **NAT IP** | IP address used for source NAT |

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

### 3.4 DNS Configuration

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

### 3.5 Supported Services

Private Endpoints are supported for many Azure services:

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

### 3.6 Benefits of Private Endpoints

| Benefit | Description |
|---------|-------------|
| **Security** | Traffic never traverses the public internet |
| **Data Exfiltration Protection** | Only access specific resources, not entire services |
| **On-premises Access** | Connect via VPN/ExpressRoute to private endpoints |
| **Cross-region** | Access services in different regions privately |
| **No Public IP Required** | Resources don't need public IPs to access PaaS services |

---

## 4. Service Endpoints vs Private Endpoints

### 4.1 Service Endpoints

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

### 4.2 Comparison Table

| Feature | Service Endpoint | Private Endpoint |
|---------|------------------|------------------|
| **IP Address Used** | Service's public IP | Private IP from VNet |
| **Traffic Path** | Azure backbone (optimized) | Azure backbone (Private Link) |
| **On-premises Access** | Not supported | Supported via VPN/ExpressRoute |
| **Cross-region** | Limited | Fully supported |
| **DNS Changes** | Not required | Required |
| **Cost** | Free | Per hour + data processing |
| **Data Exfiltration Protection** | Limited (entire service) | Strong (specific resource) |
| **Disable Public Access** | No (public IP still used) | Yes (can fully disable) |

### 4.3 When to Use Each

**Use Service Endpoints when:**
- Simple setup is needed
- Cost is a concern
- Traffic only originates from Azure VNet
- Basic network isolation is sufficient

**Use Private Endpoints when:**
- On-premises resources need access
- You want to disable public access completely
- Cross-region private connectivity is needed
- Data exfiltration protection is critical
- Compliance requires no public IP exposure

---

## 5. VPN vs Private Link

### 5.1 Understanding the Fundamental Difference

**VPN** and **Private Link** are both Azure networking features, but they solve **completely different problems**. Understanding this distinction is crucial for designing secure Azure architectures.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE CORE DIFFERENCE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VPN (Virtual Private Network)                                              │
│  ════════════════════════════                                               │
│  • Connects NETWORKS together (site-to-site)                                │
│  • Connects USERS to a network (point-to-site)                              │
│  • Creates an encrypted TUNNEL over the internet                            │
│  • Extends your on-premises network to Azure                                │
│  • Think: "Network-to-Network bridge"                                       │
│                                                                              │
│  Private Link / Private Endpoint                                            │
│  ═══════════════════════════════                                            │
│  • Connects your VNet to a SPECIFIC Azure PaaS SERVICE                      │
│  • Brings the service INTO your VNet via private IP                         │
│  • No tunnel - direct private connectivity                                  │
│  • Think: "Service-to-Network injection"                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Simple Analogy:**
- **VPN** = Building a private highway between two cities (networks)
- **Private Link** = Opening a private entrance to a store (Azure service) from your building (VNet)

### 5.2 Azure VPN Gateway

**Azure VPN Gateway** creates encrypted connections between networks over the public internet.

**VPN Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| **Site-to-Site (S2S)** | Connects on-premises network to Azure VNet | Branch office to Azure |
| **Point-to-Site (P2S)** | Connects individual devices to Azure VNet | Remote workers |
| **VNet-to-VNet** | Connects two Azure VNets | Multi-region deployments |

**Site-to-Site VPN Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SITE-TO-SITE VPN                                     │
│                                                                              │
│   On-Premises Network                        Azure Virtual Network           │
│   ┌─────────────────────┐                   ┌─────────────────────┐         │
│   │  192.168.0.0/16     │                   │  10.0.0.0/16        │         │
│   │                     │                   │                     │         │
│   │  ┌───────────────┐  │                   │  ┌───────────────┐  │         │
│   │  │ On-Prem       │  │                   │  │  Azure        │  │         │
│   │  │ VPN Device    │  │                   │  │  VPN Gateway  │  │         │
│   │  │ (Router/FW)   │  │                   │  │  (GatewaySubnet)│ │         │
│   │  └───────┬───────┘  │                   │  └───────┬───────┘  │         │
│   │          │          │                   │          │          │         │
│   │  ┌───────┴───────┐  │                   │  ┌───────┴───────┐  │         │
│   │  │ Servers       │  │                   │  │  VMs          │  │         │
│   │  │ Workstations  │  │                   │  │  App Services │  │         │
│   │  │ Databases     │  │                   │  │  (VNet-integrated)│        │
│   │  └───────────────┘  │                   │  └───────────────┘  │         │
│   └──────────┬──────────┘                   └──────────┬──────────┘         │
│              │                                         │                     │
│              │         ┌─────────────────┐             │                     │
│              └─────────┤  IPsec/IKE      ├─────────────┘                     │
│                        │  Encrypted      │                                   │
│                        │  Tunnel         │                                   │
│                        │  (Internet)     │                                   │
│                        └─────────────────┘                                   │
│                                                                              │
│   Result: On-prem devices can access Azure VMs using private IPs (10.x.x.x) │
│           Azure VMs can access on-prem servers using private IPs (192.x.x.x)│
└─────────────────────────────────────────────────────────────────────────────┘
```

**Point-to-Site VPN Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        POINT-TO-SITE VPN                                     │
│                                                                              │
│   Remote Workers                             Azure Virtual Network           │
│                                             ┌─────────────────────┐         │
│   ┌──────────┐                              │  10.0.0.0/16        │         │
│   │ Laptop 1 │───┐                          │                     │         │
│   │(VPN Client)  │                          │  ┌───────────────┐  │         │
│   └──────────┘   │      Internet            │  │  Azure        │  │         │
│                  │    ┌─────────────┐       │  │  VPN Gateway  │  │         │
│   ┌──────────┐   ├───▶│  Encrypted  │──────▶│  │  P2S Config   │  │         │
│   │ Laptop 2 │───┤    │  SSTP/IKEv2 │       │  └───────┬───────┘  │         │
│   │(VPN Client)  │    │  OpenVPN    │       │          │          │         │
│   └──────────┘   │    └─────────────┘       │  ┌───────┴───────┐  │         │
│                  │                          │  │  VMs          │  │         │
│   ┌──────────┐   │                          │  │  Databases    │  │         │
│   │ Phone    │───┘                          │  │  Services     │  │         │
│   │(VPN Client)                             │  └───────────────┘  │         │
│   └──────────┘                              └─────────────────────┘         │
│                                                                              │
│   Result: Individual devices get a VPN client IP and can access             │
│           all resources in the Azure VNet as if they were on the network    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**VPN Gateway SKUs:**

| SKU | S2S Tunnels | P2S Connections | Throughput | Use Case |
|-----|-------------|-----------------|------------|----------|
| **Basic** | 10 | 128 | 100 Mbps | Dev/Test |
| **VpnGw1** | 30 | 250 | 650 Mbps | Small production |
| **VpnGw2** | 30 | 500 | 1 Gbps | Medium production |
| **VpnGw3** | 30 | 1000 | 1.25 Gbps | Large production |
| **VpnGw4** | 100 | 5000 | 5 Gbps | Enterprise |
| **VpnGw5** | 100 | 10000 | 10 Gbps | Large enterprise |

### 5.3 Azure Private Link

**Azure Private Link** enables you to access Azure PaaS services over a private endpoint in your VNet.

**Private Link Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRIVATE LINK / PRIVATE ENDPOINT                      │
│                                                                              │
│   Your Azure Virtual Network                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  10.0.0.0/16                                                         │   │
│   │                                                                       │   │
│   │  Subnet: 10.0.1.0/24                                                 │   │
│   │  ┌─────────────────────────────────────────────────────────────┐    │   │
│   │  │                                                              │    │   │
│   │  │  ┌──────────┐         ┌──────────────────────┐              │    │   │
│   │  │  │   VM     │────────▶│   Private Endpoint   │              │    │   │
│   │  │  │10.0.1.4  │         │   10.0.1.5           │              │    │   │
│   │  │  └──────────┘         │   (NIC with private IP)             │    │   │
│   │  │                       └───────────┬──────────┘              │    │   │
│   │  └───────────────────────────────────┼──────────────────────────┘    │   │
│   └──────────────────────────────────────┼───────────────────────────────┘   │
│                                          │                                   │
│                               Private Link Connection                        │
│                           (Microsoft Backbone Network)                       │
│                                          │                                   │
│                                          ▼                                   │
│                          ┌───────────────────────────────┐                  │
│                          │     Azure PaaS Service        │                  │
│                          │     (Storage, SQL, etc.)      │                  │
│                          │                               │                  │
│                          │  Public endpoint: DISABLED    │                  │
│                          │  Only accessible via PE       │                  │
│                          └───────────────────────────────┘                  │
│                                                                              │
│   Result: VM accesses Storage at 10.0.1.5 (private IP)                      │
│           Traffic NEVER goes to public internet                              │
│           Storage's public endpoint can be completely disabled               │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Private Link Concepts:**

| Concept | Description |
|---------|-------------|
| **Private Link** | The technology/service enabling private connectivity |
| **Private Endpoint** | The actual network interface (NIC) with private IP |
| **Private Link Service** | Expose your own service via Private Link |
| **Private DNS Zone** | Resolves service FQDN to private IP |

### 5.4 Detailed Comparison

| Aspect | VPN | Private Link |
|--------|-----|--------------|
| **Purpose** | Connect networks together | Connect VNet to specific Azure service |
| **What it connects** | Network ↔ Network | VNet → Azure PaaS Service |
| **Traffic path** | Encrypted tunnel over internet | Microsoft backbone (no internet) |
| **On-premises support** | Primary use case | Via VPN/ExpressRoute to VNet |
| **IP addressing** | Full network range access | Single private IP per service |
| **Protocol support** | All IP traffic | All (TCP/UDP) |
| **Latency** | Higher (encryption overhead + internet) | Lower (direct backbone) |
| **Bandwidth** | Limited by SKU (100 Mbps - 10 Gbps) | Limited by service |
| **Setup complexity** | High (gateway, certificates, routing) | Medium (endpoint + DNS) |
| **Cost** | Gateway hourly + data egress | Endpoint hourly + data processed |
| **Use case** | Extend network to Azure | Secure access to Azure services |

### 5.5 Architecture Diagrams

**Scenario: On-premises accessing Azure Storage**

**Option A: VPN Only (Without Private Link)**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     VPN ONLY - NO PRIVATE LINK                               │
│                                                                              │
│  On-Premises          VPN Tunnel            Azure VNet                       │
│  ┌──────────┐      ┌─────────────┐      ┌────────────────┐                  │
│  │  Server  │─────▶│  Encrypted  │─────▶│  VPN Gateway   │                  │
│  └──────────┘      │  Internet   │      └───────┬────────┘                  │
│                    └─────────────┘              │                            │
│                                                 │  Route to Storage          │
│                                                 ▼  (Public IP)               │
│                                    ┌─────────────────────────┐              │
│                                    │   Azure Storage         │              │
│                                    │   *.blob.core.windows.net│             │
│                                    │   (Public endpoint)     │              │
│                                    └─────────────────────────┘              │
│                                                                              │
│  ⚠️  Traffic from VNet to Storage goes over PUBLIC endpoint                 │
│  ⚠️  Storage public IP exposed                                              │
│  ⚠️  Cannot fully lock down Storage                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Option B: VPN + Private Link (Best Practice)**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     VPN + PRIVATE LINK (RECOMMENDED)                         │
│                                                                              │
│  On-Premises          VPN Tunnel            Azure VNet                       │
│  ┌──────────┐      ┌─────────────┐      ┌────────────────┐                  │
│  │  Server  │─────▶│  Encrypted  │─────▶│  VPN Gateway   │                  │
│  └──────────┘      │  Internet   │      └───────┬────────┘                  │
│                    └─────────────┘              │                            │
│                                                 ▼                            │
│                                        ┌───────────────┐                    │
│                                        │ Private       │                    │
│                                        │ Endpoint      │                    │
│                                        │ 10.0.1.5      │                    │
│                                        └───────┬───────┘                    │
│                                                │  Private Link              │
│                                                ▼                            │
│                                    ┌─────────────────────────┐              │
│                                    │   Azure Storage         │              │
│                                    │   Public: DISABLED      │              │
│                                    │   Private only          │              │
│                                    └─────────────────────────┘              │
│                                                                              │
│  ✅ On-prem accesses Storage via PRIVATE IP (10.0.1.5)                      │
│  ✅ Storage public endpoint DISABLED                                        │
│  ✅ All traffic stays private                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.6 Use Case Scenarios

**When to Use VPN:**

| Scenario | Why VPN? |
|----------|----------|
| Remote workers need full Azure VNet access | P2S VPN gives network-level access |
| On-premises servers need to talk to Azure VMs | S2S VPN connects the networks |
| Hybrid Active Directory | DC replication needs network connectivity |
| Lift-and-shift migrations | Applications expect network connectivity |
| Access Azure VMs from on-premises | VPN provides IP-level connectivity |

**When to Use Private Link:**

| Scenario | Why Private Link? |
|----------|-------------------|
| Azure VMs accessing Storage/SQL/Cosmos | Private endpoint removes public exposure |
| Compliance requires no public endpoints | Private Link + disable public access |
| Data exfiltration protection | Can only access specific resource |
| Cross-region private access | Private endpoints work across regions |
| App Service accessing Azure services | VNet integration + Private Endpoint |

**When to Use Both:**

| Scenario | Configuration |
|----------|---------------|
| On-premises accessing Azure PaaS | VPN (network) + Private Link (service) |
| Secure hybrid architecture | VPN for VMs, Private Link for PaaS |
| Enterprise hub-spoke | VPN in hub, Private Link in spokes |

### 5.7 Can They Work Together?

**Yes! VPN and Private Link are complementary, not competing technologies.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              COMPLETE HYBRID ARCHITECTURE                                    │
│                                                                              │
│  On-Premises Data Center                                                     │
│  ┌─────────────────────────────────────────┐                                │
│  │  ┌───────────┐  ┌───────────┐          │                                │
│  │  │ App Server│  │ Database  │          │                                │
│  │  └─────┬─────┘  └─────┬─────┘          │                                │
│  │        │              │                 │                                │
│  │        └──────┬───────┘                 │                                │
│  │               ▼                         │                                │
│  │        ┌─────────────┐                  │                                │
│  │        │ VPN Device  │                  │                                │
│  │        └──────┬──────┘                  │                                │
│  └───────────────┼─────────────────────────┘                                │
│                  │                                                           │
│         ═════════╪═════════  VPN Tunnel (Internet)                          │
│                  │                                                           │
│  Azure           ▼                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Hub VNet (10.0.0.0/16)                                              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │  VPN Gateway    │  │  Azure Firewall │  │  Bastion        │      │   │
│  │  │  (GatewaySubnet)│  │                 │  │                 │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └─────────────────┘      │   │
│  └───────────┼────────────────────┼────────────────────────────────────┘   │
│              │                    │                                         │
│              │    VNet Peering    │                                         │
│              ▼                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Spoke VNet (10.1.0.0/16)                                            │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │  App VMs        │  │  Private        │  │  Private        │      │   │
│  │  │  10.1.1.x       │  │  Endpoint       │  │  Endpoint       │      │   │
│  │  │                 │  │  (Storage)      │  │  (SQL)          │      │   │
│  │  │                 │  │  10.1.2.5       │  │  10.1.2.6       │      │   │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │   │
│  └───────────┼────────────────────┼────────────────────┼────────────────┘   │
│              │                    │                    │                    │
│              │         Private Link Connections        │                    │
│              │                    │                    │                    │
│              ▼                    ▼                    ▼                    │
│        ┌──────────┐        ┌──────────┐        ┌──────────┐                │
│        │   VMs    │        │ Storage  │        │   SQL    │                │
│        │ (IaaS)   │        │ (PaaS)   │        │  (PaaS)  │                │
│        │          │        │ Public:  │        │ Public:  │                │
│        │          │        │ Disabled │        │ Disabled │                │
│        └──────────┘        └──────────┘        └──────────┘                │
│                                                                              │
│  Traffic Flow:                                                               │
│  On-prem App → VPN → Hub → Peering → Spoke VM (10.1.1.x)                   │
│  On-prem App → VPN → Hub → Peering → Private Endpoint → Storage            │
│  Spoke VM → Private Endpoint → SQL (never leaves Azure backbone)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.8 Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DECISION MATRIX                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  What are you trying to connect?                                            │
│  │                                                                           │
│  ├── On-premises network to Azure VNet                                      │
│  │   └── Use: VPN Gateway (Site-to-Site) or ExpressRoute                   │
│  │                                                                           │
│  ├── Individual users to Azure VNet                                         │
│  │   └── Use: VPN Gateway (Point-to-Site)                                  │
│  │                                                                           │
│  ├── Azure VNet to Azure PaaS service (Storage, SQL, etc.)                 │
│  │   └── Use: Private Endpoint                                             │
│  │                                                                           │
│  ├── On-premises to Azure PaaS service                                      │
│  │   └── Use: VPN + Private Endpoint (both)                                │
│  │                                                                           │
│  ├── Two Azure VNets together                                               │
│  │   └── Use: VNet Peering (not VPN, not Private Link)                     │
│  │                                                                           │
│  └── Azure resource to on-premises service                                  │
│      └── Use: VPN or Hybrid Connections (Azure Relay)                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        QUICK REFERENCE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Need network-level connectivity?          → VPN                            │
│  Need to access Azure PaaS privately?      → Private Link                   │
│  Need both?                                → Use both together              │
│  Don't need on-prem connectivity?          → Private Link only              │
│  Migrating VMs to Azure?                   → VPN first, add Private Link   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Azure Relay Service

### 6.1 What is Azure Relay?

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

### 6.2 The Problem Azure Relay Solves

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

### 6.3 Azure Relay Components

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

### 6.4 WCF Relays

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

### 6.5 Hybrid Connections (Azure Relay Feature)

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

### 6.6 WCF Relays vs Hybrid Connections

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

### 6.7 Authentication and Security

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

### 6.8 Pricing

Azure Relay pricing is based on:

| Component | Cost Basis |
|-----------|------------|
| **Listener Hours** | Per hour per active listener |
| **Hybrid Connection** | Per connection per hour |
| **Messages (WCF)** | Per 10,000 messages |
| **Data Transfer** | Standard Azure data transfer rates |

---

## 7. Hybrid Connections (App Service Feature)

### 7.1 What are App Service Hybrid Connections?

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

### 7.2 How Hybrid Connections Work

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

### 7.3 Hybrid Connection Manager

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

### 7.4 Use Cases

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

### 7.5 Limitations

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

### 7.6 Hybrid Connections vs VNet Integration vs Private Endpoints

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

## 8. Common Networking Scenarios

### 8.1 Securing Azure Storage with Private Endpoint

```
┌─────────────────────────────────────────────────────────────┐
│ VNet: 10.0.0.0/16                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Subnet: 10.0.1.0/24                                 │   │
│  │  ┌──────────┐        ┌─────────────────┐            │   │
│  │  │ App      │───────▶│ Private Endpoint │            │   │
│  │  │ Service  │        │ 10.0.1.5        │            │   │
│  │  └──────────┘        └────────┬────────┘            │   │
│  └───────────────────────────────┼─────────────────────┘   │
└──────────────────────────────────┼──────────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │ Storage Account              │
                    │ Public access: Disabled      │
                    │ Private endpoint: Enabled    │
                    └──────────────────────────────┘
```

**Configuration Steps:**
1. Create a private endpoint for the storage account
2. Link to Private DNS Zone `privatelink.blob.core.windows.net`
3. Disable public network access on storage account
4. Application connects using standard storage connection string

### 8.2 Securing Azure SQL Database

```csharp
// Connection string remains the same
// DNS resolves to private IP automatically
var connectionString = "Server=myserver.database.windows.net;Database=mydb;...";
```

**DNS Resolution:**
- `myserver.database.windows.net` → CNAME → `myserver.privatelink.database.windows.net` → `10.0.1.6`

### 8.3 Securing Azure Key Vault

Private endpoints for Key Vault are commonly used to:
- Allow VMs to retrieve secrets without public internet
- Enable App Services (VNet-integrated) to access secrets
- Support on-premises applications via VPN

**Key Vault Network Settings:**
| Setting | Value |
|---------|-------|
| Public network access | Disabled |
| Private endpoint connections | Enabled |
| Firewall | Allow trusted Microsoft services |

### 8.4 Securing Azure Cosmos DB

Cosmos DB supports private endpoints for each API type:

| API | Private DNS Zone |
|-----|------------------|
| SQL (Core) | `privatelink.documents.azure.com` |
| MongoDB | `privatelink.mongo.cosmos.azure.com` |
| Cassandra | `privatelink.cassandra.cosmos.azure.com` |
| Gremlin | `privatelink.gremlin.cosmos.azure.com` |
| Table | `privatelink.table.cosmos.azure.com` |

---

## 9. Network Architecture Best Practices

| Practice | Description |
|----------|-------------|
| **Plan IP addressing** | Avoid overlapping address spaces for peering |
| **Use private endpoints** | For PaaS services requiring high security |
| **Centralize DNS** | Use Azure Private DNS Zones linked to VNets |
| **Subnet delegation** | Reserve subnets for specific services (App Service, etc.) |
| **NSG flow logs** | Enable for traffic visibility and troubleshooting |
| **Hub-spoke topology** | For enterprise deployments with shared services |
| **Use Service Tags** | Simplify NSG rules with Azure service tags |

**Hub-Spoke Architecture:**
```
                    ┌─────────────────────┐
                    │    Hub VNet         │
                    │  ┌───────────────┐  │
                    │  │   Firewall    │  │
                    │  │   VPN Gateway │  │
                    │  │   Bastion     │  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ Spoke VNet 1│     │ Spoke VNet 2│     │ Spoke VNet 3│
    │ (Web tier)  │     │ (App tier)  │     │ (Data tier) │
    └─────────────┘     └─────────────┘     └─────────────┘
```

---

## 10. Summary Table

| Concept | Key Points |
|---------|------------|
| **VNet** | Isolated network in Azure; region-scoped; contains subnets |
| **Subnet** | Segment of VNet; 5 reserved IPs; can have NSGs and route tables |
| **VNet Peering** | Connect VNets; non-transitive; same or different regions |
| **NSG** | Filter traffic with allow/deny rules; priority-based |
| **VPN Gateway** | Connects networks (S2S) or users (P2S) via encrypted tunnel over internet |
| **Private Link** | Technology enabling private connectivity to Azure PaaS services |
| **Private Endpoint** | Network interface with private IP to access PaaS services; requires DNS |
| **Service Endpoint** | Optimized route to Azure services; uses public IP; free |
| **Private DNS Zone** | Automatic DNS resolution for private endpoints |
| **Azure Relay** | Cloud rendezvous point enabling outbound-only connections; supports WCF Relays and Hybrid Connections |
| **Hybrid Connections** | Connect App Service to on-premises via Azure Relay; no VPN needed; Windows HCM required |

---

## Related Resources

- [Azure Virtual Network Documentation](https://docs.microsoft.com/azure/virtual-network/)
- [Azure VPN Gateway Documentation](https://docs.microsoft.com/azure/vpn-gateway/)
- [Azure Private Link Documentation](https://docs.microsoft.com/azure/private-link/)
- [Azure Relay Documentation](https://docs.microsoft.com/azure/azure-relay/)
- [Azure Relay Hybrid Connections](https://docs.microsoft.com/azure/app-service/app-service-hybrid-connections)
- [Network Security Groups](https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview)
- [VNet Peering](https://docs.microsoft.com/azure/virtual-network/virtual-network-peering-overview)
