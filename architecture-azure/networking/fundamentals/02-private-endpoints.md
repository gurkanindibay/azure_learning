---
type: Azure Service
title: "Azure Networking Fundamentals - Private Endpoints"
description: "A **Private Endpoint** is a network interface that connects you privately and securely to a service powered by Azure Private Link. The private endpoint uses a private IP address from your VNet, eff..."
tags: [networking]
timestamp: 2026-06-14T00:00:00Z
---

# Azure Networking Fundamentals - Private Endpoints

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

#### 3.3.1 When to Use Private Link Service

**Azure Private Link Service** is the recommended solution when you need to expose your own application (hosted on load-balanced Azure VMs) to consumers while meeting the following requirements:

| Requirement | How Private Link Service Addresses It |
|-------------|--------------------------------------|
| **Accessible from other Azure tenants** | Consumers in different Azure AD tenants can create private endpoints to connect to your Private Link Service |
| **Isolated from the public internet** | All traffic flows over the Microsoft backbone network, never traversing the public internet |
| **Private access from customer VNets** | Consumers connect via private endpoints in their own VNets with private IP addresses |

**Key Architecture Concept - Provider vs Consumer:**

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     CROSS-TENANT PRIVATE LINK SERVICE ARCHITECTURE                   │
│                                                                                      │
│   TENANT A (Service Provider)                    TENANT B (Consumer)                │
│   ┌────────────────────────────────┐            ┌────────────────────────────────┐  │
│   │  Provider VNet (10.0.0.0/16)   │            │  Consumer VNet (172.16.0.0/16) │  │
│   │                                │            │                                │  │
│   │  ┌──────────────────────────┐  │            │  ┌──────────────────────────┐  │  │
│   │  │  Standard Load Balancer  │  │            │  │     Consumer App         │  │  │
│   │  │  (Frontend IP: 10.0.1.4) │  │            │  │     (VM or Service)      │  │  │
│   │  └────────────┬─────────────┘  │            │  └────────────┬─────────────┘  │  │
│   │               │                │            │               │                │  │
│   │               ▼                │            │               ▼                │  │
│   │  ┌──────────────────────────┐  │            │  ┌──────────────────────────┐  │  │
│   │  │  Backend Pool            │  │            │  │     Private Endpoint     │  │  │
│   │  │  ┌────┐ ┌────┐ ┌────┐   │  │◀───────────┼──│     (172.16.1.5)         │  │  │
│   │  │  │VM1 │ │VM2 │ │VM3 │   │  │  Private   │  │                          │  │  │
│   │  │  └────┘ └────┘ └────┘   │  │  Link      │  └──────────────────────────┘  │  │
│   │  └──────────────────────────┘  │  Connection│                                │  │
│   │               ▲                │            │  Traffic flows over Microsoft  │  │
│   │               │                │            │  backbone - NO public internet │  │
│   │  ┌──────────────────────────┐  │            │                                │  │
│   │  │  Private Link Service    │  │            └────────────────────────────────┘  │
│   │  │  (NAT IP: 10.0.2.x)      │  │                                                │
│   │  │  - Exposes the LB        │  │            TENANT C (Another Consumer)         │
│   │  │  - Controls access       │  │            ┌────────────────────────────────┐  │
│   │  └──────────────────────────┘  │            │  Consumer VNet (192.168.0.0/16)│  │
│   │                                │            │                                │  │
│   └────────────────────────────────┘            │  ┌──────────────────────────┐  │  │
│                                                 │  │     Private Endpoint     │  │  │
│                                                 │  │     (192.168.1.10)       │──┼──┘
│                                                 │  └──────────────────────────┘  │
│                                                 └────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.2 Private Link Service vs Alternative Solutions

When designing networking for cross-tenant or multi-customer access to your application, consider:

| Solution | Cross-Tenant Access | Internet Isolation | Per-Customer Config | Recommended For |
|----------|--------------------|--------------------|---------------------|-----------------|
| **Private Link Service** ✅ | Yes - natively supported | Yes - Microsoft backbone only | No - single service, multiple consumers | Multi-tenant SaaS, cross-org services |
| **Private Endpoints** | Consumer-side only | Yes | N/A - consumer creates these | Consuming services, not exposing them |
| **VNet Peering** | Limited - complex setup | Yes | Yes - each tenant requires peering | Same-org, known networks |
| **VPN Gateway** | Possible but complex | Yes | Yes - each tenant requires VPN config | On-premises connectivity |

**Why Private Link Service is the Correct Choice:**

1. **Service Provider Model**: You expose a **Private Link Service** that can be consumed by **any tenant** creating a private endpoint
2. **Consumer Creates Private Endpoint**: Consumers in other tenants deploy private endpoints in their own VNets to connect to your service
3. **No Configuration per Customer**: Unlike VNet peering or VPNs, you don't need to configure anything for each new consumer
4. **Automatic Isolation**: Each consumer's traffic is isolated; consumers cannot see each other
5. **Approval Workflow**: You can auto-approve connections or require manual approval for each consumer

#### 3.3.3 Private Link Service Requirements

| Requirement | Details |
|-------------|---------|
| **Load Balancer SKU** | Standard Load Balancer (Basic SKU not supported) |
| **Frontend IP** | Can be IPv4 only |
| **NAT IP Configuration** | Required - used for source NAT to hide consumer IPs |
| **Visibility** | Control which subscriptions can discover and connect |
| **TCP/UDP Support** | Supports any TCP or UDP protocol on the load balancer |

**References:**
- [What is Azure Private Link Service? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview)
- [Recommend a network architecture solution based on workload requirements | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/design-network-solutions/)

#### 📝 Exam Scenario: Exposing services privately to customers via Microsoft backbone

**Question:**
You want your customers to use Microsoft's backbone to connect from their virtual network to the services in your virtual network. Which Azure service supports this?

- A) ExpressRoute Peering
- B) ExpressRoute Private Link
- C) Azure Service Endpoint
- D) Azure Private Link Service
- E) Network Security Groups

**Correct Answer: D) Azure Private Link Service**

**Explanation:**

Azure Private Link Service allows you to expose your own services (behind an Azure Standard Load Balancer) to consumers as private endpoints within their virtual networks. All traffic flows over the Microsoft backbone network, never traversing the public internet. Consumers create a private endpoint in their VNet and map it to your Private Link Service.

| Option | Correct/Incorrect | Reason |
|--------|-------------------|--------|
| **A) ExpressRoute Peering** | ❌ Incorrect | ExpressRoute provides private connectivity between on-premises networks and Azure, not VNet-to-VNet service exposure to customers |
| **B) ExpressRoute Private Link** | ❌ Incorrect | This is not a valid Azure service name |
| **C) Azure Service Endpoint** | ❌ Incorrect | Service Endpoints enable VNet resources to use private IP addresses to connect to the **public endpoint** of an Azure PaaS service. They do not expose your own services to customers |
| **D) Azure Private Link Service** | ✅ **Correct** | Enables you to expose your service behind a Standard Load Balancer so consumers can create private endpoints in their VNets to connect privately over the Microsoft backbone |
| **E) Network Security Groups** | ❌ Incorrect | NSGs filter network traffic to/from Azure resources but do not provide private connectivity or service exposure |

**Key Distinction — Service Endpoint vs Private Link Service:**

| Aspect | Azure Service Endpoint | Azure Private Link Service |
|--------|----------------------|---------------------------|
| **Direction** | You consume Azure PaaS services | You expose your own services to consumers |
| **Endpoint type** | Routes traffic to PaaS public endpoint via backbone | Creates a private endpoint in consumer's VNet |
| **Cross-tenant** | No | Yes — consumers in any tenant can connect |
| **IP address** | PaaS service keeps its public IP | Consumer gets a private IP in their VNet |

**Reference:** [What is Azure Private Link service? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/private-link/private-link-service-overview)

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

#### 3.4.1 DNS Resolution for Hybrid/On-Premises Connectivity

When on-premises clients need to access Azure PaaS services through Private Endpoints, DNS resolution requires special configuration. Azure Private DNS zones only resolve names for linked virtual networks via Azure-provided DNS.

**The Challenge:**
- On-premises clients cannot directly query Azure Private DNS zones
- The Azure-provided DNS (168.63.129.16) is only accessible from within Azure VMs
- Public DNS zones return public IPs, bypassing the private endpoint

**Solution Architecture: DNS Forwarder**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              HYBRID DNS RESOLUTION FOR PRIVATE ENDPOINTS                     │
│                                                                              │
│  On-Premises Network                        Azure Virtual Network (VNET1)   │
│  ┌─────────────────────┐                   ┌─────────────────────────────┐  │
│  │                     │                   │                             │  │
│  │  ┌───────────────┐  │   ExpressRoute    │  ┌───────────────────────┐  │  │
│  │  │ On-Prem       │  │   or VPN          │  │ VM1 (DNS Forwarder)   │  │  │
│  │  │ Client        │──┼───────────────────┼─▶│ Forwards contoso.com  │  │  │
│  │  │               │  │                   │  │ to 168.63.129.16      │  │  │
│  │  └───────────────┘  │                   │  └───────────┬───────────┘  │  │
│  │         │           │                   │              │              │  │
│  │         │ DNS Query │                   │              ▼              │  │
│  │         │ for       │                   │  ┌───────────────────────┐  │  │
│  │         │ sqldb1.   │                   │  │ Azure-Provided DNS    │  │  │
│  │         │ contoso.  │                   │  │ 168.63.129.16         │  │  │
│  │         │ com       │                   │  └───────────┬───────────┘  │  │
│  │         │           │                   │              │              │  │
│  │         ▼           │                   │              ▼              │  │
│  │  ┌───────────────┐  │                   │  ┌───────────────────────┐  │  │
│  │  │ On-Prem DNS   │  │                   │  │ Private DNS Zone      │  │  │
│  │  │ Server        │  │                   │  │ contoso.com           │  │  │
│  │  │ Forwards to   │──┼───────────────────┼─▶│ A Record: PE1 IP      │  │  │
│  │  │ VM1 in Azure  │  │                   │  └───────────┬───────────┘  │  │
│  │  └───────────────┘  │                   │              │              │  │
│  └─────────────────────┘                   │              ▼              │  │
│                                            │  ┌───────────────────────┐  │  │
│                                            │  │ PE1 (Private Endpoint)│  │  │
│                                            │  │ Provides connectivity │  │  │
│                                            │  │ to SQLDB1             │  │  │
│                                            │  └───────────────────────┘  │  │
│                                            └─────────────────────────────┘  │
│                                                                              │
│  Result: On-prem client resolves sqldb1.contoso.com → Private IP of PE1     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example Scenario:**

| Resource | Type | Description |
|----------|------|-------------|
| **VNET1** | Virtual Network | Connected to on-premises via ExpressRoute |
| **VM1** | Virtual Machine | Configured as DNS server/forwarder |
| **PE1** | Private Endpoint | Provides connectivity to SQLDB1 |
| **contoso.com** | Private DNS Zone | Linked to VNET1, contains A record for PE1 |
| **contoso.com** | Public DNS Zone | Contains CNAME record for SQLDB1 (public) |

**Configuration Options Analysis:**

| Configuration | Result | Explanation |
|---------------|--------|-------------|
| **VM1 forwards to 168.63.129.16** | ✅ **Correct** | Azure-provided DNS resolves private DNS zones linked to the VNet. On-prem queries reach VM1 → forwarded to Azure DNS → resolves to PE1's private IP |
| **VM1 forwards to public DNS zone** | ❌ **Incorrect** | Public DNS returns CNAME to public endpoint, bypassing the private endpoint entirely |
| **VNet custom DNS set to 168.63.129.16** | ❌ **Incorrect** | 168.63.129.16 is implicit for Azure VMs; setting it explicitly as custom DNS causes resolution loops/issues |

**On-Premises DNS Configuration Options:**

| Configuration | Result | Explanation |
|---------------|--------|-------------|
| **Forward contoso.com to VM1** | ✅ **Correct** | VM1 is configured as a DNS server within VNET1 and has access to the private DNS zone for contoso.com. VM1 can resolve queries using the private DNS zone linked to VNET1, returning PE1's private IP |
| **Forward contoso.com to public DNS zone** | ❌ **Incorrect** | Public DNS zone contains CNAME record pointing to SQLDB1's public endpoint, which bypasses the private endpoint and exposes traffic over the public internet |
| **Forward contoso.com to 168.63.129.16** | ❌ **Incorrect** | Azure-provided DNS (168.63.129.16) is **only accessible from within Azure VNets**, not from on-premises networks. This IP is non-routable from on-premises, so forwarding would fail |

**Two-Tier DNS Resolution Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COMPLETE DNS RESOLUTION CHAIN                            │
│                                                                              │
│   TIER 1: On-Premises DNS                   TIER 2: Azure DNS Forwarder     │
│   ┌─────────────────────────┐              ┌─────────────────────────┐      │
│   │  On-Premises DNS Server │              │  VM1 (Azure DNS Server) │      │
│   │                         │              │                         │      │
│   │  Conditional Forwarder: │    Query     │  Conditional Forwarder: │      │
│   │  contoso.com ──────────────────────────▶  contoso.com ───────────│──┐   │
│   │       → VM1's IP        │              │       → 168.63.129.16   │  │   │
│   │                         │              │                         │  │   │
│   └─────────────────────────┘              └─────────────────────────┘  │   │
│              ▲                                                          │   │
│              │                                                          ▼   │
│         On-Prem                                          ┌──────────────────┐
│         Client                                           │ Azure-Provided   │
│                                                          │ DNS 168.63.129.16│
│                                                          │ (Only reachable  │
│                                                          │  from Azure VMs) │
│                                                          └────────┬─────────┘
│                                                                   │         │
│                                                                   ▼         │
│                                                          ┌──────────────────┐
│                                                          │ Private DNS Zone │
│                                                          │ A: PE1 → 10.0.x.x│
│                                                          └──────────────────┘
│                                                                              │
│   Key: On-prem CANNOT reach 168.63.129.16 directly, must go through VM1    │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why 168.63.129.16?**

The IP address `168.63.129.16` is a special Azure wireserver IP address that:
- Is available **only from within Azure VMs**
- Automatically resolves names in **private DNS zones linked to the VNet**
- Cannot be reached directly from on-premises networks
- Is used implicitly by Azure VMs when no custom DNS is configured

**DNS Forwarder Configuration Steps:**

1. **Deploy a DNS server VM** (e.g., VM1) in the Azure VNet
2. **Configure conditional forwarding** on VM1 to forward queries for the private endpoint domain (e.g., contoso.com) to `168.63.129.16`
3. **Link the Private DNS Zone** to the VNet containing VM1
4. **Configure on-premises DNS** to forward queries for the domain to VM1's IP address
5. **Ensure network connectivity** between on-premises and VM1 via VPN/ExpressRoute

**Best Practices:**

- Deploy DNS forwarders in a highly available configuration (multiple VMs across availability zones)
- Use Azure DNS Private Resolver as a managed alternative to VM-based DNS forwarders
- Ensure NSG rules allow DNS traffic (UDP/TCP port 53) between on-premises and the DNS forwarder VMs
- Consider using Azure Firewall DNS proxy for centralized DNS management

**References:**
- [Private endpoint DNS integration](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns)
- [Azure Private DNS overview](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [What is IP address 168.63.129.16](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)
- [Name resolution for VMs and role instances](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances)

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

### 3.7 Common Scenarios and Use Cases

#### 3.7.1 Ensuring Traffic Stays on Microsoft Backbone Network

**Scenario:** You have an on-premises network connected to Azure via VPN Gateway, and you need to ensure that all traffic from a VM to a Storage Account travels across the Microsoft backbone network (never the public internet).

**Setup:**

| Resource | Type | Description |
|----------|------|-------------|
| **vgw1** | Virtual network gateway | Gateway for Site-to-Site VPN to the on-premises network |
| **storage1** | Storage account | Standard performance tier |
| **Vnet1** | Virtual network | Enabled for forced tunneling |
| **VM1** | Virtual machine | Connected to Vnet1 |

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  ON-PREMISES TO AZURE STORAGE VIA PRIVATE ENDPOINT            │
│                                                                               │
│  On-Premises Network                     Azure Virtual Network (Vnet1)       │
│  ┌─────────────────────┐                ┌──────────────────────────────────┐ │
│  │                     │   VPN Tunnel   │                                  │ │
│  │  On-Prem Resources  │◄───────────────┤  vgw1 (VPN Gateway)              │ │
│  │                     │   (Encrypted)  │                                  │ │
│  └─────────────────────┘                └──────────────┬───────────────────┘ │
│                                                        │                     │
│                                                        ▼                     │
│                                         ┌──────────────────────────────────┐ │
│                                         │  VM1                             │ │
│                                         │  Connected to Vnet1              │ │
│                                         └──────────────┬───────────────────┘ │
│                                                        │                     │
│                                                        │ Private IP          │
│                                                        ▼                     │
│                                         ┌──────────────────────────────────┐ │
│                                         │  Private Endpoint                │ │
│                                         │  (Network Interface)             │ │
│                                         │  Private IP: 10.0.1.5            │ │
│                                         └──────────────┬───────────────────┘ │
│                                                        │                     │
│                                          Private Link Connection            │
│                                         (Microsoft Backbone)                │
│                                                        │                     │
│                                                        ▼                     │
│                                         ┌──────────────────────────────────┐ │
│                                         │  storage1 (Storage Account)      │ │
│                                         │  Public endpoint: DISABLED       │ │
│                                         │  Only accessible via PE          │ │
│                                         └──────────────────────────────────┘ │
│                                                                               │
│  Result: All traffic from VM1 to storage1 uses Private Endpoint              │
│          Traffic NEVER traverses the public internet                         │
│          Communication happens entirely over Microsoft backbone network      │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Solution: Private Endpoints** ✅

**Why Private Endpoints?**

A **private endpoint** is a network interface that uses a private IP address from your virtual network. This network interface connects you privately and securely to a service powered by Azure Private Link. By enabling a private endpoint, you're bringing the service into your virtual network.

**Key Benefits in This Scenario:**

| Aspect | Benefit |
|--------|---------|
| **Traffic Path** | All traffic flows over the Microsoft backbone network via Private Link |
| **No Public Internet** | Traffic never leaves Azure's private network infrastructure |
| **On-Premises Access** | On-premises resources can access the storage account through the VPN connection to the VNet |
| **Private IP Addressing** | VM1 accesses storage1 using a private IP address (e.g., 10.0.1.5) |
| **Public Access Control** | Storage account's public endpoint can be completely disabled |

**Alternative Solutions Comparison:**

| Solution | Keeps Traffic on Backbone? | Explanation |
|----------|----------------------------|-------------|
| **Private Endpoints** | ✅ **Yes** | Creates a network interface with private IP in your VNet. All traffic flows over Private Link via Microsoft backbone |
| **Azure AD Application Proxy** | ❌ **No** | Used for publishing on-premises web applications to external users. Not related to storage connectivity |
| **Azure Peering Service** | ❌ **No** | Optimizes public internet routing to Microsoft services. Still uses public internet paths |
| **Network Security Group (NSG)** | ❌ **No** | Controls traffic filtering (allow/deny rules) but doesn't change the network path. Traffic would still use public endpoints |

**Configuration Steps:**

1. **Create a Private Endpoint** for storage1 in Vnet1
2. **Configure Private DNS Zone** (`privatelink.blob.core.windows.net`) linked to Vnet1
3. **Disable public network access** on storage1 (optional but recommended)
4. **Verify DNS resolution**: VM1 resolves `storage1.blob.core.windows.net` to the private endpoint IP
5. **Test connectivity**: VM1 can now access storage1 via private IP over Microsoft backbone

**Traffic Flow:**
```
On-Premises → VPN Gateway → Vnet1 → VM1 → Private Endpoint → storage1
                   (All via Microsoft Backbone Network)
```

---

