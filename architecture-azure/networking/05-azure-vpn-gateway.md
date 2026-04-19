# Azure VPN Gateway

## Table of Contents

- [1. Overview](#1-overview)
- [2. VPN Gateway vs Virtual Network Gateway](#2-vpn-gateway-vs-virtual-network-gateway)
  - [2.1 The Terminology Clarification](#21-the-terminology-clarification)
  - [2.2 Virtual Network Gateway Types](#22-virtual-network-gateway-types)
  - [2.3 VPN Types: PolicyBased vs RouteBased](#23-vpn-types-policybased-vs-routebased)
- [3. What is Azure VPN Gateway?](#3-what-is-azure-vpn-gateway)
  - [3.1 Definition](#31-definition)
  - [3.2 Key Characteristics](#32-key-characteristics)
  - [3.3 Architecture Components](#33-architecture-components)
- [4. VPN Gateway Types and Scenarios](#4-vpn-gateway-types-and-scenarios)
  - [4.1 Site-to-Site (S2S) VPN](#41-site-to-site-s2s-vpn)
  - [4.2 Point-to-Site (P2S) VPN](#42-point-to-site-p2s-vpn)
  - [4.3 VNet-to-VNet VPN](#43-vnet-to-vnet-vpn)
- [5. Gateway SKUs and Performance](#5-gateway-skus-and-performance)
  - [5.1 SKU Comparison](#51-sku-comparison)
  - [5.2 Choosing the Right SKU](#52-choosing-the-right-sku)
- [6. Gateway Subnet Requirements](#6-gateway-subnet-requirements)
- [7. High Availability and Redundancy](#7-high-availability-and-redundancy)
  - [7.1 Active-Standby Configuration](#71-active-standby-configuration)
  - [7.2 Active-Active Configuration](#72-active-active-configuration)
  - [7.3 Zone-Redundant Gateways](#73-zone-redundant-gateways)
- [8. VPN Protocols and Encryption](#8-vpn-protocols-and-encryption)
  - [8.1 IPsec/IKE Protocols](#81-ipsecike-protocols)
  - [8.2 BGP Support](#82-bgp-support)
- [9. On-Premises Equivalent](#9-on-premises-equivalent)
  - [9.1 Hardware VPN Devices](#91-hardware-vpn-devices)
  - [9.2 Software VPN Solutions](#92-software-vpn-solutions)
  - [9.3 Validated VPN Devices for Azure](#93-validated-vpn-devices-for-azure)
- [10. VPN Gateway vs Other Connectivity Options](#10-vpn-gateway-vs-other-connectivity-options)
  - [10.1 VPN Gateway vs ExpressRoute](#101-vpn-gateway-vs-expressroute)
  - [10.2 VPN Gateway vs VNet Peering](#102-vpn-gateway-vs-vnet-peering)
  - [10.3 VPN Gateway vs Azure Bastion](#103-vpn-gateway-vs-azure-bastion)
- [11. Common Use Cases](#11-common-use-cases)
- [12. Configuration Best Practices](#12-configuration-best-practices)
- [13. Troubleshooting](#13-troubleshooting)
- [14. Pricing Considerations](#14-pricing-considerations)
- [15. Related Services](#15-related-services)
- [16. References](#16-references)

---

## 1. Overview

**Azure VPN Gateway** is a critical component for establishing secure, encrypted connections between your Azure virtual networks and other networks. It enables hybrid cloud architectures by bridging on-premises infrastructure with Azure resources over the public internet using industry-standard IPsec/IKE protocols.

**Key Value Proposition:**
- Encrypted tunnels over public internet (no dedicated line required)
- Lower cost compared to ExpressRoute
- Quick deployment (hours vs weeks)
- Supports multiple connection types (S2S, P2S, VNet-to-VNet)

---

## 2. VPN Gateway vs Virtual Network Gateway

### 2.1 The Terminology Clarification

**Important:** VPN Gateway and Virtual Network Gateway are **NOT different services**. This is a common source of confusion.

```
┌─────────────────────────────────────────┐
│   Virtual Network Gateway               │
│   (Azure Resource Type)                 │
│                                         │
│   ┌──────────────┐   ┌──────────────┐  │
│   │ VPN Gateway  │   │ ExpressRoute │  │
│   │   (Type 1)   │   │   Gateway    │  │
│   │              │   │   (Type 2)   │  │
│   └──────────────┘   └──────────────┘  │
└─────────────────────────────────────────┘
```

**Virtual Network Gateway** is the **resource type** in Azure.  
**VPN Gateway** is a **specific type** of Virtual Network Gateway.

### 2.2 Virtual Network Gateway Types

When you create a Virtual Network Gateway in Azure, you must specify a **gateway type**:

| Gateway Type | Protocol | Use Case |
|--------------|----------|----------|
| **Vpn** | IPsec/IKE over internet | Encrypted tunnels over public internet |
| **ExpressRoute** | Private connection | Dedicated private connection via service provider |

**In Azure Portal:**
```bash
# When creating a Virtual Network Gateway, you choose:
Gateway type: Vpn ← This creates a "VPN Gateway"
          or: ExpressRoute ← This creates an "ExpressRoute Gateway"

VPN type: Route-based (recommended) or Policy-based
```

**Azure CLI Example:**
```bash
az network vnet-gateway create \
  --name MyVpnGateway \
  --resource-group MyResourceGroup \
  --gateway-type Vpn \          # ← This makes it a "VPN Gateway"
  --vpn-type RouteBased \
  --sku VpnGw1 \
  --vnet MyVNet \
  --public-ip-address MyGatewayIP
```

### 2.3 VPN Types: PolicyBased vs RouteBased

When creating a Virtual Network Gateway with gateway type **Vpn**, you must also specify a **VPN type**. There are exactly **two valid VPN types**: **PolicyBased** and **RouteBased**.

> **Exam Tip:** The only valid VPN types are **PolicyBased** and **RouteBased**. Values like "IntervalBased", "LinkBased", or "StatusBased" do not exist.

#### PolicyBased VPN

PolicyBased VPNs (previously called **static routing** gateways) encrypt and direct packets through IPsec tunnels based on **traffic selectors** (combinations of source/destination address prefixes).

| Aspect | Detail |
|--------|--------|
| **Routing method** | Policy-based (static) — traffic selectors define which traffic goes through the tunnel |
| **IKE version** | IKEv1 only |
| **S2S tunnels** | Supports only **1** S2S connection |
| **P2S support** | ❌ Not supported |
| **Active-active** | ❌ Not supported |
| **BGP** | ❌ Not supported |
| **VNet-to-VNet** | ❌ Not supported |
| **SKU** | Basic only |
| **Use case** | Legacy on-premises VPN devices that require policy-based routing |

#### RouteBased VPN

RouteBased VPNs (previously called **dynamic routing** gateways) use routes in the IP forwarding or routing table to direct packets into their corresponding tunnel interfaces. Each tunnel interface encrypts/decrypts packets.

| Aspect | Detail |
|--------|--------|
| **Routing method** | Route-based (dynamic) — any-to-any traffic selectors; routes/forwarding table directs traffic |
| **IKE version** | IKEv1 and IKEv2 |
| **S2S tunnels** | Up to 30 (depending on SKU) |
| **P2S support** | ✅ Supported |
| **Active-active** | ✅ Supported |
| **BGP** | ✅ Supported |
| **VNet-to-VNet** | ✅ Supported |
| **SKU** | All SKUs (Basic through VpnGw5AZ) |
| **Use case** | Recommended for most scenarios |

#### Comparison Summary

| Feature | PolicyBased | RouteBased |
|---------|-------------|------------|
| **S2S connections** | 1 | Up to 30 |
| **P2S** | ❌ | ✅ |
| **IKEv2** | ❌ | ✅ |
| **Active-active** | ❌ | ✅ |
| **BGP** | ❌ | ✅ |
| **ExpressRoute coexistence** | ❌ | ✅ |
| **VNet-to-VNet** | ❌ | ✅ |
| **Multiple on-premises sites** | ❌ | ✅ |
| **Transit routing** | ❌ | ✅ |

> **Best Practice:** Always choose **RouteBased** unless you have a specific legacy device that only supports PolicyBased. RouteBased is required for P2S, VNet-to-VNet, multi-site connections, active-active configuration, BGP, and coexistence with ExpressRoute.

**Azure CLI — specifying VPN type:**
```bash
# RouteBased (recommended)
az network vnet-gateway create --vpn-type RouteBased ...

# PolicyBased (legacy only)
az network vnet-gateway create --vpn-type PolicyBased ...
```

**Reference:** [VPN Gateway configuration settings — VPN type | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-gateway-settings#vpntype)

---

## 3. What is Azure VPN Gateway?

### 3.1 Definition

An **Azure VPN Gateway** is a specific instance of a Virtual Network Gateway configured to send encrypted traffic between:
- An Azure virtual network and on-premises locations (Site-to-Site)
- Individual client computers and Azure virtual networks (Point-to-Site)
- Azure virtual networks and other Azure virtual networks (VNet-to-VNet)

### 3.2 Key Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Deployment** | Deployed in a dedicated subnet called **GatewaySubnet** |
| **Redundancy** | Minimum 2 VMs deployed (managed by Azure, invisible to user) |
| **IP Addressing** | Requires a public IP address for external connectivity |
| **Protocols** | IPsec (Internet Protocol Security) and IKE (Internet Key Exchange) |
| **Encryption** | Strong encryption (AES-256) for data in transit |
| **Routing** | Route-based (dynamic) or Policy-based (static) |

### 3.3 Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│ Azure Virtual Network (10.0.0.0/16)                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ GatewaySubnet (10.0.255.0/27)                  │    │
│  │  ┌──────────────────────────────────────┐      │    │
│  │  │ VPN Gateway                          │      │    │
│  │  │ - Primary VM (Active)                │      │    │
│  │  │ - Secondary VM (Standby)             │      │    │
│  │  │ - Public IP: 40.112.123.45          │      │    │
│  │  └──────────────────────────────────────┘      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Application Subnet (10.0.1.0/24)               │    │
│  │  - Web Servers                                 │    │
│  │  - Application VMs                             │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                   IPsec/IKE Tunnel
                   (Encrypted over Internet)
                          │
┌─────────────────────────────────────────────────────────┐
│ On-Premises Network (192.168.0.0/16)                    │
│                                                          │
│  ┌──────────────────────────────────────┐              │
│  │ VPN Device (Hardware/Software)       │              │
│  │ - Public IP: 203.0.113.10           │              │
│  └──────────────────────────────────────┘              │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Internal Servers                               │    │
│  │  - Domain Controllers                          │    │
│  │  - File Servers                                │    │
│  │  - Database Servers                            │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 4. VPN Gateway Types and Scenarios

### 4.1 Site-to-Site (S2S) VPN

**Purpose:** Connect an entire on-premises network to an Azure virtual network.

**Architecture:**
```
On-Premises Network ←→ VPN Device ←→ Internet ←→ Azure VPN Gateway ←→ Azure VNet
```

**Requirements:**
- VPN device on-premises (hardware or software)
- Public IPv4 address on the VPN device
- Properly configured IPsec/IKE parameters

**Use Cases:**
- Hybrid cloud deployments
- Disaster recovery scenarios
- Migrating workloads to Azure
- Accessing Azure resources from corporate network

**Configuration:**
```
┌─────────────────────────────────────────┐
│ Azure VPN Gateway Configuration         │
├─────────────────────────────────────────┤
│ Gateway Type: Vpn                       │
│ VPN Type: Route-based                   │
│ SKU: VpnGw1                             │
│ Virtual Network: Production-VNet        │
│ Gateway Subnet: 10.0.255.0/27          │
│ Public IP: VpnGateway-PIP              │
└─────────────────────────────────────────┘
          ↓ Connection
┌─────────────────────────────────────────┐
│ Local Network Gateway                   │
│ (Represents on-premises)                │
├─────────────────────────────────────────┤
│ IP Address: 203.0.113.10 (on-prem VPN) │
│ Address Space: 192.168.0.0/16          │
│ BGP Settings: (optional)                │
└─────────────────────────────────────────┘
```

### 4.2 Point-to-Site (P2S) VPN

**Purpose:** Connect individual client computers to an Azure virtual network.

**Architecture:**
```
Remote Worker Laptop ←→ VPN Client ←→ Internet ←→ Azure VPN Gateway ←→ Azure VNet
```

**Supported Protocols:**
- **OpenVPN** (SSL/TLS-based, recommended)
- **SSTP** (SSL-based, Windows only)
- **IKEv2** (IPsec, macOS/iOS native support)

**Authentication Methods:**
- Azure certificate authentication
- Azure Active Directory (OpenVPN only)
- RADIUS authentication

**Authentication Method Details:**

| Method | How It Works | Use Case |
|--------|-------------|----------|
| **Azure Certificate** | Client certificates installed on each device; validated by the gateway | Small teams, dev/test environments |
| **Azure Active Directory** | Users authenticate with Azure AD credentials (OpenVPN only) | Cloud-native organizations using Azure AD |
| **RADIUS Server** | Gateway delegates authentication to a RADIUS server, which can integrate with AD Domain Services | Enterprises using on-premises Active Directory domain credentials |

> **Important — RADIUS + Active Directory Integration:**
> When users need to authenticate to a P2S VPN using their **Active Directory domain credentials**, a **RADIUS server** is required. The Azure VPN Gateway does not communicate directly with an AD Domain Controller for P2S authentication. Instead, the flow is:
>
> ```
> VPN Client → Azure VPN Gateway → RADIUS Server → AD Domain Controller
> ```
>
> The RADIUS server (e.g., Windows NPS — Network Policy Server) acts as the intermediary that validates credentials against Active Directory. An AD Domain Controller alone is **not sufficient** — the RADIUS server is the required component that bridges P2S VPN authentication with AD domain authentication.

**P2S Routing and Topology Changes:**

> **Critical — VPN Client Re-download After Topology Changes:**
> P2S VPN routing depends on the client OS, the VPN protocol (SSTP or IKEv2), and the network topology. If you make **any changes to your network topology** — such as adding VNet peering, modifying address spaces, or changing gateway configurations — **Windows P2S VPN clients must re-download and reinstall the VPN client configuration package**. The routes embedded in the client configuration are static and do **not** update automatically.
>
> This applies to both SSTP (Windows only) and IKEv2 clients. S2S VPN connections are not affected because their routing is handled at the gateway level.
>
> See: [About P2S VPN routing](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-point-to-site-routing)

**Use Cases:**
- Remote workers accessing Azure VMs
- Development/testing access
- Administrators managing Azure resources
- Telecommuters needing secure access

**Configuration Example:**
```
┌─────────────────────────────────────────┐
│ P2S VPN Configuration                   │
├─────────────────────────────────────────┤
│ Address Pool: 172.16.0.0/24            │
│ Tunnel Type: OpenVPN (SSL)             │
│ Authentication: Azure AD                │
│ Root Certificate: (for cert auth)       │
│ Client Config Download: Available       │
└─────────────────────────────────────────┘
```

### 4.3 VNet-to-VNet VPN

**Purpose:** Connect two Azure virtual networks using encrypted VPN tunnels.

**Architecture:**
```
Azure VNet 1 ←→ VPN Gateway 1 ←→ Azure Backbone ←→ VPN Gateway 2 ←→ Azure VNet 2
```

**When to Use:**
- VNets in different regions (cross-region connectivity)
- VNets in different subscriptions
- When encryption is required (unlike VNet Peering)
- Multi-region disaster recovery

**Alternative:** VNet Peering (faster, lower latency, no encryption overhead)

**Comparison with VNet Peering:**

| Aspect | VNet Peering | VNet-to-VNet VPN |
|--------|--------------|------------------|
| **Latency** | Very low (Azure backbone) | Higher (encryption overhead) |
| **Encryption** | No | Yes (IPsec) |
| **Cost** | Lower (data transfer only) | Higher (gateway hours + data) |
| **Bandwidth** | High | Limited by gateway SKU |
| **Setup Complexity** | Simple | More complex |
| **Use Case** | Most scenarios | When encryption required |

---

## 5. Gateway SKUs and Performance

### 5.1 SKU Comparison

| SKU | S2S/VNet-to-VNet Tunnels | P2S Connections | Aggregate Throughput | BGP | Zone-Redundant |
|-----|--------------------------|-----------------|----------------------|-----|----------------|
| **Basic** | Max. 10 | Max. 128 | 100 Mbps | ❌ | ❌ |
| **VpnGw1** | Max. 30 | Max. 250 | 650 Mbps | ✅ | ❌ |
| **VpnGw2** | Max. 30 | Max. 500 | 1 Gbps | ✅ | ❌ |
| **VpnGw3** | Max. 30 | Max. 1000 | 1.25 Gbps | ✅ | ❌ |
| **VpnGw1AZ** | Max. 30 | Max. 250 | 650 Mbps | ✅ | ✅ |
| **VpnGw2AZ** | Max. 30 | Max. 500 | 1 Gbps | ✅ | ✅ |
| **VpnGw3AZ** | Max. 30 | Max. 1000 | 1.25 Gbps | ✅ | ✅ |

**Important Notes:**
- **Basic SKU**: Legacy, not recommended for production
- **AZ SKUs**: Deployed across Availability Zones (higher SLA)
- **Throughput**: Aggregate (shared across all tunnels)
- **BGP**: Required for active-active and complex routing scenarios

### 5.2 Choosing the Right SKU

**Decision Matrix:**

```
High availability required + Regional presence in AZ-enabled region?
  → YES: VpnGw1AZ/2AZ/3AZ

Need > 30 S2S tunnels or > 1000 P2S users?
  → Consider multiple gateways or ExpressRoute

Throughput requirements:
  → < 650 Mbps: VpnGw1
  → 650 Mbps - 1 Gbps: VpnGw2
  → > 1 Gbps: VpnGw3 or ExpressRoute

Budget-constrained dev/test?
  → Basic (but be aware of limitations)

Production workload?
  → Minimum VpnGw1, preferably VpnGw1AZ or higher
```

---

## 6. Gateway Subnet Requirements

**GatewaySubnet** is a special subnet required for VPN Gateway deployment.

**Naming:** MUST be named exactly `GatewaySubnet` (case-sensitive)

**Sizing Recommendations:**

| Scenario | Minimum | Recommended |
|----------|---------|-------------|
| **VPN Gateway only** | /29 (8 IPs) | /27 (32 IPs) |
| **VPN + ExpressRoute coexistence** | /27 | /26 (64 IPs) |
| **Future expansion** | /27 | /26 or larger |

**Why larger is better:**
- Each gateway instance requires IP addresses
- Active-active requires additional IPs
- Cannot resize GatewaySubnet after resources are deployed
- Planning for future needs

**Example Configuration:**
```
Virtual Network: 10.0.0.0/16
├── AppSubnet: 10.0.1.0/24
├── DatabaseSubnet: 10.0.2.0/24
└── GatewaySubnet: 10.0.255.0/27  ← Must be named exactly this
```

**What gets deployed in GatewaySubnet:**
- VPN Gateway VMs (2 for standard deployment)
- Internal load balancer (for active-active)
- Public IP address associations

---

## 7. High Availability and Redundancy

### 7.1 Active-Standby Configuration

**Default deployment mode.**

```
┌─────────────────────────────────────┐
│ VPN Gateway                         │
│                                     │
│  ┌─────────────┐                   │
│  │ Primary VM  │ ◄─── Active       │
│  │ 10.0.255.4  │                   │
│  └─────────────┘                   │
│                                     │
│  ┌─────────────┐                   │
│  │ Secondary VM│ ◄─── Standby      │
│  │ 10.0.255.5  │                   │
│  └─────────────┘                   │
│                                     │
│  Public IP: 40.112.123.45          │
└─────────────────────────────────────┘
```

**Behavior:**
- Only one VM actively handles traffic
- Automatic failover on maintenance or failure
- Brief interruption during failover (seconds to minutes)
- Single public IP address

**Failover Scenarios:**
- Planned maintenance (Azure updates)
- Unplanned hardware failure
- Network connectivity issues

### 7.2 Active-Active Configuration

**Enhanced availability with dual tunnels.**

```
┌─────────────────────────────────────┐
│ VPN Gateway (Active-Active)         │
│                                     │
│  ┌─────────────┐                   │
│  │ Primary VM  │ ◄─── Active       │
│  │ 10.0.255.4  │                   │
│  │ PIP1: 40.112.123.45            │
│  └─────────────┘                   │
│         │                           │
│         └────────┐ Both            │
│                  │ Forwarding       │
│         ┌────────┘                  │
│         │                           │
│  ┌─────────────┐                   │
│  │ Secondary VM│ ◄─── Active       │
│  │ 10.0.255.5  │                   │
│  │ PIP2: 40.112.123.46            │
│  └─────────────┘                   │
└─────────────────────────────────────┘
        │              │
        └──────┬───────┘
               │
     Two IPsec Tunnels
               │
┌─────────────────────────────────────┐
│ On-Premises VPN Device              │
│ (Must support multiple tunnels)    │
│  - Tunnel 1 to PIP1                │
│  - Tunnel 2 to PIP2                │
└─────────────────────────────────────┘
```

**Requirements:**
- BGP must be enabled
- On-premises VPN device must support multiple tunnels
- Two public IP addresses required
- VpnGw1 or higher SKU

**Benefits:**
- No interruption during failover
- Load balancing across tunnels
- Higher aggregate throughput

### 7.3 Zone-Redundant Gateways

**Available with AZ SKUs (VpnGw1AZ, VpnGw2AZ, VpnGw3AZ).**

```
┌─────────────────────────────────────────────┐
│ Azure Region (e.g., East US 2)              │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Zone 1   │  │ Zone 2   │  │ Zone 3   │ │
│  │          │  │          │  │          │ │
│  │  VPN GW  │  │  VPN GW  │  │  VPN GW  │ │
│  │ Instance │  │ Instance │  │ Instance │ │
│  └──────────┘  └──────────┘  └──────────┘ │
│                                             │
│  Automatically distributed across zones    │
└─────────────────────────────────────────────┘
```

**Benefits:**
- Protection from zone-level failures
- Higher SLA (99.99% vs 99.95%)
- Required for mission-critical workloads

**Requirements:**
- Must be in a region that supports Availability Zones
- Zone-redundant public IP address

---

## 8. VPN Protocols and Encryption

### 8.1 IPsec/IKE Protocols

**Azure VPN Gateway uses industry-standard protocols:**

| Component | Purpose | Supported Versions |
|-----------|---------|-------------------|
| **IKE** | Key exchange and tunnel establishment | IKEv1, IKEv2 |
| **IPsec** | Data encryption and authentication | ESP (Encapsulating Security Payload) |

**Default Encryption Parameters:**
```
IKE Phase 1 (Main Mode):
- Encryption: AES256
- Integrity: SHA256
- DH Group: DHGroup2 (1024-bit)
- SA Lifetime: 28,800 seconds (8 hours)

IKE Phase 2 (Quick Mode):
- Encryption: AES256 or GCMAES256
- Integrity: SHA256 or GCMAES256
- PFS Group: PFS2048
- SA Lifetime: 27,000 seconds (~7.5 hours)
```

**Custom IPsec/IKE Policies:**

Azure VPN Gateway allows you to configure **custom IPsec/IKE policies** on S2S VPN and VNet-to-VNet connections, rather than using Azure's default policy sets. This gives you precise control over the cryptographic algorithms and key strengths used for a connection.

#### Supported Algorithms and Parameters

| Parameter | Supported Values |
|-----------|-----------------|
| **IKE Encryption** | GCMAES256, GCMAES128, AES256, AES192, AES128, DES3, DES |
| **IKE Integrity** | SHA384, SHA256, SHA1, MD5 |
| **DH Group** | DHGroup24, ECP384, ECP256, DHGroup14, DHGroup2048, DHGroup2, DHGroup1 |
| **IPsec Encryption** | GCMAES256, GCMAES192, GCMAES128, AES256, AES192, AES128, DES3, DES, None |
| **IPsec Integrity** | GCMAES256, GCMAES192, GCMAES128, SHA256, SHA1, MD5 |
| **PFS Group** | PFS24, ECP384, ECP256, PFS2048, PFS2, PFS1, None |
| **SA Lifetime** | Minimum 300 seconds / maximum 102,400,000 KB |

> **Important:** When using GCMAES for IPsec Encryption, you must select the same GCMAES algorithm and key length for IPsec Integrity (e.g., GCMAES256 for both). You cannot mix GCMAES with non-GCMAES integrity algorithms.

#### Step-by-Step Workflow: Configure IPsec/IKE Policy for S2S VPN

The correct sequence for creating and configuring a custom IPsec/IKE policy on a site-to-site VPN connection is:

```
Step 1: Create a VNet and a VPN Gateway
     ↓
Step 2: Create a Local Network Gateway (represents on-premises)
     ↓
Step 3: Create an IPsec/IKE policy (select algorithms & parameters)
     ↓
Step 4: Create the S2S VPN connection with the IPsec/IKE policy attached
     ↓
Step 5: Add, update, or remove IPsec/IKE policy on an existing connection
```

> **Key Insight:** You must create the VNet and VPN gateway **before** the local network gateway because the gateway deployment establishes the GatewaySubnet and public IP. The IPsec/IKE policy object must be created **before** the connection so it can be referenced during connection creation. Policy updates happen **after** the connection exists.

**Full PowerShell workflow:**

```powershell
# ── Step 1: Create VNet and VPN Gateway ──
$subnet = New-AzVirtualNetworkSubnetConfig -Name "Subnet1" -AddressPrefix "10.0.1.0/24"
$gwSubnet = New-AzVirtualNetworkSubnetConfig -Name "GatewaySubnet" -AddressPrefix "10.0.255.0/27"

$vnet = New-AzVirtualNetwork -Name "MyVNet" -ResourceGroupName "MyRG" `
  -Location "EastUS" -AddressPrefix "10.0.0.0/16" -Subnet $subnet, $gwSubnet

$gwSubnetRef = Get-AzVirtualNetworkSubnetConfig -Name "GatewaySubnet" -VirtualNetwork $vnet
$gwPip = New-AzPublicIpAddress -Name "VpnGatewayPIP" -ResourceGroupName "MyRG" `
  -Location "EastUS" -AllocationMethod Dynamic

$gwIpConfig = New-AzVirtualNetworkGatewayIpConfig -Name "gwIpConfig" `
  -SubnetId $gwSubnetRef.Id -PublicIpAddressId $gwPip.Id

$vpnGateway = New-AzVirtualNetworkGateway -Name "MyVpnGateway" -ResourceGroupName "MyRG" `
  -Location "EastUS" -IpConfigurations $gwIpConfig -GatewayType Vpn `
  -VpnType RouteBased -GatewaySku VpnGw1

# ── Step 2: Create Local Network Gateway ──
$localGateway = New-AzLocalNetworkGateway -Name "OnPremGateway" -ResourceGroupName "MyRG" `
  -Location "EastUS" -GatewayIpAddress "203.0.113.10" `
  -AddressPrefix "192.168.0.0/16"

# ── Step 3: Create Custom IPsec/IKE Policy ──
$ipsecPolicy = New-AzIpsecPolicy `
  -IkeEncryption AES256 `
  -IkeIntegrity SHA384 `
  -DhGroup DHGroup24 `
  -IpsecEncryption AES256 `
  -IpsecIntegrity SHA256 `
  -PfsGroup PFS24 `
  -SALifeTimeSeconds 27000 `
  -SADataSizeKilobytes 102400000

# ── Step 4: Create S2S Connection with IPsec/IKE Policy ──
$connection = New-AzVirtualNetworkGatewayConnection -Name "MyS2SConnection" `
  -ResourceGroupName "MyRG" -Location "EastUS" `
  -VirtualNetworkGateway1 $vpnGateway `
  -LocalNetworkGateway2 $localGateway `
  -ConnectionType IPsec `
  -SharedKey "YourPreSharedKey123!" `
  -IpsecPolicies $ipsecPolicy

# ── Step 5: Update IPsec/IKE Policy on Existing Connection ──
$updatedPolicy = New-AzIpsecPolicy `
  -IkeEncryption AES256 `
  -IkeIntegrity SHA256 `
  -DhGroup DHGroup14 `
  -IpsecEncryption GCMAES256 `
  -IpsecIntegrity GCMAES256 `
  -PfsGroup PFS2048 `
  -SALifeTimeSeconds 14400 `
  -SADataSizeKilobytes 102400000

Set-AzVirtualNetworkGatewayConnection `
  -VirtualNetworkGatewayConnection $connection `
  -IpsecPolicies $updatedPolicy

# ── Remove IPsec/IKE Policy (revert to Azure defaults) ──
Set-AzVirtualNetworkGatewayConnection `
  -VirtualNetworkGatewayConnection $connection `
  -IpsecPolicies @()
```

> **Exam Tip:** The correct step sequence is **b → a → c → d → e** (VNet/VPN Gateway → Local Network Gateway → Create IPsec/IKE Policy → Create S2S Connection with Policy → Update/Remove Policy). You cannot create a connection before both gateways exist, and you cannot attach a policy that hasn't been defined yet.

**Reference:** [Configure IPsec/IKE policy for S2S VPN or VNet-to-VNet connections | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/ipsec-ike-policy-howto)

### 8.2 BGP Support

**Border Gateway Protocol (BGP)** enables dynamic routing between Azure and on-premises networks.

**Benefits:**
- Automatic route updates
- Multi-site failover
- Active-active gateway support
- ExpressRoute + VPN coexistence

**BGP Configuration:**
```
┌─────────────────────────────────────┐
│ Azure VPN Gateway                   │
│ BGP ASN: 65515 (Azure)             │
│ BGP Peer IP: 10.0.255.254          │
└─────────────────────────────────────┘
         │ BGP Peering
         │ (Route Exchange)
         │
┌─────────────────────────────────────┐
│ On-Premises VPN Device              │
│ BGP ASN: 65001 (Customer)          │
│ BGP Peer IP: 192.168.255.1         │
└─────────────────────────────────────┘
```

**When to Use BGP:**
- Multiple on-premises locations
- Active-active gateway configuration
- Dynamic routing requirements
- Integration with ExpressRoute

---

## 9. On-Premises Equivalent

### 9.1 Hardware VPN Devices

Azure VPN Gateway's on-premises equivalent is a **VPN device** at your datacenter or office that establishes the IPsec tunnel to Azure.

**Common Hardware VPN Devices:**

| Vendor | Product Examples | Notes |
|--------|------------------|-------|
| **Cisco** | ASA 5500-X Series, ISR 4000 Series | Most common, well-documented |
| **Fortinet** | FortiGate Series | Next-gen firewall with VPN |
| **Palo Alto** | PA-Series Firewalls | Enterprise-grade, threat prevention |
| **Juniper** | SRX Series | Service routers with VPN |
| **pfSense** | pfSense Appliance | Open-source, cost-effective |
| **SonicWall** | TZ/NSa Series | SMB to enterprise |
| **Ubiquiti** | EdgeRouter Series | Cost-effective for small deployments |
| **WatchGuard** | Firebox Series | SMB focus |

### 9.2 Software VPN Solutions

**For scenarios without dedicated hardware:**

| Software | Platform | Use Case |
|----------|----------|----------|
| **Windows Server RRAS** | Windows Server | Small deployments |
| **pfSense** | FreeBSD/x86 | Open-source firewall |
| **VyOS** | Linux | Open-source router |
| **strongSwan** | Linux | Open-source IPsec |
| **OpenSwan** | Linux | IPsec VPN (legacy) |
| **Sophos XG** | Virtual Appliance | Firewall + VPN |
| **Fortinet FortiGate VM** | Virtual Appliance | Enterprise virtual firewall |

### 9.3 Validated VPN Devices for Azure

Microsoft maintains a list of **validated VPN devices** tested for compatibility with Azure VPN Gateway.

**Validation Process:**
- Tested by Microsoft and device partners
- Configuration scripts provided
- Known to work with Azure VPN Gateway

**Validation Levels:**
- ✅ **Validated**: Fully tested, configuration samples available
- ⚠️ **Compatible**: Should work, but not explicitly tested
- ❌ **Not supported**: Known incompatibilities

**Example Configuration (Cisco ASA):**
```
crypto ikev2 policy 1
 encryption aes-256
 integrity sha256
 group 2
 prf sha256
 lifetime seconds 28800

crypto ipsec ikev2 ipsec-proposal AZURE-PROPOSAL
 protocol esp encryption aes-256
 protocol esp integrity sha-256

tunnel-group 40.112.123.45 type ipsec-l2l
tunnel-group 40.112.123.45 ipsec-attributes
 ikev2 remote-authentication pre-shared-key <YOUR-KEY>
 ikev2 local-authentication pre-shared-key <YOUR-KEY>

access-list AZURE-ACL extended permit ip 192.168.0.0 255.255.0.0 10.0.0.0 255.255.0.0

crypto map AZURE-MAP 1 match address AZURE-ACL
crypto map AZURE-MAP 1 set peer 40.112.123.45
crypto map AZURE-MAP 1 set ikev2 ipsec-proposal AZURE-PROPOSAL
```

**On-Premises Architecture:**
```
┌──────────────────────────────────────────────┐
│ Corporate Network                            │
│                                              │
│  ┌────────────┐      ┌──────────────────┐  │
│  │ Internal   │──────│ VPN Device       │  │
│  │ Network    │      │ (Firewall/Router)│  │
│  │ 192.168.x.x│      │                  │  │
│  └────────────┘      │ Public IP:       │  │
│                      │ 203.0.113.10     │  │
│  - Domain Controllers│                  │  │
│  - File Servers      └──────────────────┘  │
│  - Applications             │               │
│  - Databases                │               │
│                             │               │
└─────────────────────────────┼───────────────┘
                              │
                        Internet
                              │
                  IPsec/IKE Tunnel (Encrypted)
                              │
┌─────────────────────────────┼───────────────┐
│ Azure Virtual Network       │               │
│                      ┌──────────────────┐  │
│                      │ Azure VPN Gateway│  │
│                      │                  │  │
│                      │ Public IP:       │  │
│                      │ 40.112.123.45    │  │
│                      └──────────────────┘  │
│                             │               │
│  ┌────────────┐             │               │
│  │ Azure VNet │─────────────┘               │
│  │ 10.0.x.x   │                             │
│  └────────────┘                             │
│                                              │
│  - Azure VMs                                 │
│  - Azure SQL Database                        │
│  - Azure Storage                             │
└──────────────────────────────────────────────┘
```

---

## 10. VPN Gateway vs Other Connectivity Options

### 10.1 VPN Gateway vs ExpressRoute

| Aspect | VPN Gateway | ExpressRoute |
|--------|-------------|--------------|
| **Connection Type** | Public internet (encrypted) | Private dedicated circuit |
| **Bandwidth** | Up to 1.25 Gbps (VpnGw3) | 50 Mbps to 100 Gbps |
| **Latency** | Variable (internet-dependent) | Low, predictable |
| **Setup Time** | Hours | Weeks to months |
| **Cost** | Lower ($140-$560/month + data) | Higher ($55-$51,300/month + port fees) |
| **Encryption** | Yes (IPsec) | No (private connection, optional MACsec) |
| **SLA** | 99.95% (99.99% for AZ) | 99.95% |
| **Use Case** | Cost-effective hybrid connectivity | Mission-critical, high-bandwidth |
| **Failover Option** | Can backup ExpressRoute | Primary connectivity |

**Hybrid Approach:**
```
Primary Path: ExpressRoute (high bandwidth, low latency)
         +
Backup Path: VPN Gateway (failover, cost-effective)
```

### 10.2 VPN Gateway vs VNet Peering

| Aspect | VPN Gateway (VNet-to-VNet) | VNet Peering |
|--------|----------------------------|--------------|
| **Purpose** | Connect VNets with encryption | Connect VNets directly |
| **Encryption** | Yes (IPsec) | No (traffic stays on Azure backbone) |
| **Latency** | Higher (encryption overhead) | Very low (Azure backbone) |
| **Bandwidth** | Limited by gateway SKU | High (no gateway bottleneck) |
| **Cost** | Gateway hours + data transfer | Data transfer only |
| **Cross-Region** | Yes (natively) | Yes (requires **Global VNet Peering**) |
| **Cross-Subscription** | Yes (same Azure AD tenant) | Yes (same or different Azure AD tenants) |
| **Cross-Tenant** | No (VNets must be in subscriptions linked to the same Azure AD tenant) | Yes (VNets can be in subscriptions associated with separate Azure AD tenants) |
| **Name Resolution** | Default Azure name resolution works across VPN Gateway connections | Default Azure name resolution does **not** work across peered VNets — requires Azure DNS Private Zones or custom DNS |
| **Hub-and-Spoke Routing** | Spoke-to-spoke routing works through the gateway without additional appliances | Requires a **router/NVA** (e.g., Azure Firewall) in the hub VNet for spoke-to-spoke traffic forwarding |
| **Transitivity** | Can route between connected VNets via the gateway | **Not transitive** — requires explicit peering between each pair or hub-based routing with NVA + UDRs |
| **When to Use** | Encryption required, cross-tenant not needed, or name resolution needed without custom DNS | Most scenarios (faster, cheaper); preferred when cross-tenant support is needed |

#### Hub-and-Spoke: VNet Peering vs VPN Gateway

When building a hub-and-spoke topology, the choice between VNet peering and VPN Gateways affects several design decisions:

| Design Consideration | VPN Gateway | VNet Peering |
|---------------------|-------------|--------------|
| **Spoke-to-spoke communication** | Traffic routes through the hub gateway automatically | Requires NVA/Azure Firewall in hub + UDRs on spoke subnets |
| **External connectivity (on-premises)** | Hub gateway handles both VNet-to-VNet and on-prem tunnels | Separate VPN/ExpressRoute gateway needed in hub; spokes use **gateway transit** |
| **DNS/Name resolution** | Works natively across VPN-connected VNets | Must deploy Azure DNS Private Zones or custom DNS server in hub |
| **Cross-region spokes** | Supported natively | Requires **Global VNet Peering** (additional cost, Basic ILB not supported) |
| **Cross-subscription spokes** | Supported (same Azure AD tenant only) | Supported (same or different Azure AD tenants) |
| **Scalability** | Limited by gateway SKU tunnel count (e.g., 30 S2S for VpnGw1) | Up to 500 peerings per VNet (default limit) |
| **Performance** | Bounded by gateway SKU throughput | Near line-rate (no gateway bottleneck) |

> **Exam Tip**: A common question pattern asks whether VNets in a hub-and-spoke model must be in the same region. The answer: VPN Gateways support cross-region natively; VNet peering also supports cross-region but only through **Global VNet Peering**. The statement "VNet peering VNets must be in the same region" is **incorrect** — it was true before Global VNet Peering was introduced.

> **Reference**: [Azure Virtual Network peering | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)

### 10.3 VPN Gateway vs Azure Bastion

**Different purposes, not alternatives:**

| Aspect | VPN Gateway | Azure Bastion |
|--------|-------------|---------------|
| **Purpose** | Network-to-network connectivity | Secure RDP/SSH access to VMs |
| **Scope** | Full network access | Individual VM access only |
| **Client Required** | Yes (VPN client) | No (browser-based) |
| **Use Case** | Hybrid connectivity, remote access | Secure VM management |
| **Protocol** | IPsec/IKE | RDP/SSH over TLS |
| **Network Traffic** | All protocols | RDP (3389) / SSH (22) only |

**Can be used together:**
- VPN Gateway for network connectivity
- Azure Bastion for secure VM management (no public IPs on VMs)

---

## 11. Common Use Cases

### Use Case 1: Hybrid Cloud Architecture

**Scenario:** Enterprise wants to extend on-premises datacenter to Azure for scalability.

```
┌────────────────────────────┐
│ On-Premises Datacenter     │
│ - Active Directory         │
│ - File Servers             │
│ - Legacy Applications      │
└────────────┬───────────────┘
             │
      Site-to-Site VPN
             │
┌────────────┴───────────────┐
│ Azure Virtual Network      │
│ - Azure AD Connect         │
│ - Web Applications         │
│ - SQL Database             │
└────────────────────────────┘
```

**Benefits:**
- Seamless integration with on-premises
- Burst to cloud for peak capacity
- Gradual migration strategy

### Use Case 2: Multi-Region Disaster Recovery

**Scenario:** Application deployed in multiple Azure regions with encrypted connectivity.

```
┌────────────────────┐          ┌────────────────────┐
│ East US            │          │ West US            │
│ Primary Region     │◄────────►│ DR Region          │
│ - Production App   │  VNet-   │ - Standby App      │
│ - SQL Primary      │  to-VNet │ - SQL Secondary    │
└────────────────────┘   VPN    └────────────────────┘
```

**Benefits:**
- Encrypted data replication
- Automatic failover support
- Compliance with encryption requirements

### Use Case 3: Remote Workforce Access

**Scenario:** Remote employees need secure access to Azure resources.

```
┌──────────────────┐
│ Remote Workers   │
│ - Laptops        │
│ - Tablets        │
└────────┬─────────┘
         │
  Point-to-Site VPN
         │
┌────────┴─────────┐
│ Azure VNet       │
│ - VMs            │
│ - Azure Files    │
│ - Internal Apps  │
└──────────────────┘
```

**Benefits:**
- Azure AD authentication
- No VPN hardware required
- Granular access control

### Use Case 4: Branch Office Connectivity

**Scenario:** Multiple branch offices connecting to centralized Azure resources.

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Branch 1     │        │ Branch 2     │        │ Branch 3     │
│ New York     │        │ London       │        │ Tokyo        │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                    Site-to-Site VPN
                               │
                    ┌──────────┴─────────┐
                    │ Azure Hub VNet     │
                    │ - Shared Services  │
                    │ - Central DB       │
                    │ - Applications     │
                    └────────────────────┘
```

**Benefits:**
- Centralized management
- Consistent security policies
- Cost-effective WAN replacement

### Use Case 5: Development/Test Environments

**Scenario:** Developers need secure access to Azure test environments.

```
┌────────────────────┐
│ Developer Laptops  │
└────────┬───────────┘
         │
  Point-to-Site VPN
  (Azure AD Auth)
         │
┌────────┴─────────────┐
│ Azure Test VNet      │
│ - Dev VMs            │
│ - Test Databases     │
│ - Staging Apps       │
└──────────────────────┘
```

**Benefits:**
- No public IPs on test VMs
- Azure AD integration
- Quick setup/teardown

---

## 12. Configuration Best Practices

### 1. Gateway Subnet Sizing
```
✅ DO: Use /27 or /26 for GatewaySubnet
❌ DON'T: Use /29 (minimum but not recommended)

Reasoning: Allows for gateway upgrades and future expansion
```

### 2. Use Route-Based VPN
```
✅ DO: Select "Route-based" VPN type
❌ DON'T: Use "Policy-based" unless required by legacy device

Reasoning: Route-based supports:
- IKEv2
- Multiple tunnels
- Active-active configuration
- BGP
```

### 3. Enable BGP for Complex Topologies
```
✅ DO: Enable BGP for multi-site or active-active
❌ DON'T: Use static routes for dynamic environments

Reasoning: BGP provides automatic failover and route updates
```

### 4. Implement Active-Active for Production
```
✅ DO: Deploy active-active for mission-critical workloads
❌ DON'T: Rely on active-standby for zero downtime requirements

Reasoning: Eliminates interruption during maintenance
```

### 5. Use Zone-Redundant Gateways
```
✅ DO: Use VpnGw1AZ/2AZ/3AZ SKUs for production
❌ DON'T: Deploy non-AZ gateways in regions that support AZs

Reasoning: Higher SLA (99.99% vs 99.95%)
```

### 6. Plan IP Address Space Carefully
```
✅ DO: Ensure on-premises and Azure address spaces don't overlap
❌ DON'T: Use overlapping CIDR ranges

Example:
  On-Prem: 192.168.0.0/16
  Azure:   10.0.0.0/8
  P2S Pool: 172.16.0.0/16
```

### 7. Implement Network Security Groups
```
✅ DO: Use NSGs for granular traffic control
❌ DON'T: Rely solely on VPN for security

Reasoning: Defense in depth - VPN + NSGs + application security
```

### 8. Monitor and Alert
```
✅ DO: Configure Azure Monitor alerts for:
  - Tunnel connection status
  - Bandwidth utilization
  - Gateway health
  
❌ DON'T: Set up VPN without monitoring
```

### 9. Test Failover Scenarios
```
✅ DO: Regularly test failover procedures
❌ DON'T: Assume failover works without testing

Test scenarios:
- Primary tunnel failure
- Gateway maintenance
- BGP route changes
```

### 10. Document Configuration
```
✅ DO: Maintain documentation of:
  - IPsec parameters
  - BGP ASN numbers
  - Shared keys (in Key Vault)
  - On-premises device configuration
  
❌ DON'T: Rely on tribal knowledge
```

---

## 13. Troubleshooting

### Common Issues and Solutions

#### Issue 1: VPN Tunnel Not Connecting

**Symptoms:**
- Connection status shows "Not Connected"
- Traffic not flowing between networks

**Troubleshooting Steps:**
```
1. Verify IPsec/IKE parameters match on both ends
   - Encryption algorithm
   - Integrity algorithm
   - DH Group
   - PFS Group

2. Check pre-shared key
   - Must match exactly (case-sensitive)

3. Verify public IP addresses
   - Azure gateway public IP
   - On-premises public IP

4. Check on-premises firewall rules
   - UDP 500 (IKE)
   - UDP 4500 (NAT-T)
   - IP Protocol 50 (ESP)

5. Review Azure diagnostics
   - Connection resource -> Diagnose & solve problems
   - Check IKE diagnostic logs
```

#### Issue 2: Intermittent Connectivity

**Symptoms:**
- Connection drops randomly
- Tunnel re-establishes automatically

**Possible Causes:**
```
1. NAT-T (NAT Traversal) issues
   Solution: Ensure UDP 4500 is allowed

2. DPD (Dead Peer Detection) timeout
   Solution: Adjust DPD timers on on-premises device

3. Internet connection instability
   Solution: Check ISP connectivity, consider ExpressRoute

4. Aggressive mode vs Main mode mismatch
   Solution: Ensure both ends use same IKE mode
```

#### Issue 3: Low Throughput

**Symptoms:**
- Data transfer slower than expected
- Bandwidth not matching gateway SKU

**Troubleshooting Steps:**
```
1. Verify gateway SKU
   - Check actual throughput limits for your SKU

2. Check for bandwidth throttling
   - Azure Monitor metrics: Gateway Bandwidth

3. Verify encryption overhead
   - IPsec adds ~10-15% overhead

4. Test with multiple parallel connections
   - Single TCP stream may not max out throughput

5. Check on-premises device capacity
   - May be bottleneck, not Azure gateway

6. Consider active-active configuration
   - Doubles potential throughput
```

#### Issue 4: BGP Routes Not Propagating

**Symptoms:**
- BGP peer status shows "Connected" but routes missing
- Traffic not routing correctly

**Troubleshooting Steps:**
```
1. Verify BGP configuration
   - ASN numbers correct on both ends
   - BGP peer IPs configured properly

2. Check route filters/policies
   - On-premises device may be filtering routes

3. Review route limits
   - Default limit: 4000 routes per VPN gateway

4. Verify BGP timers
   - Keepalive and hold timers must be compatible

5. Check Azure effective routes
   - Portal -> Virtual Network -> Subnet -> Effective Routes
```

#### Issue 5: Point-to-Site Client Can't Connect

**Symptoms:**
- VPN client connection fails
- Authentication errors

**Troubleshooting Steps:**
```
1. Verify client certificate
   - Must be issued by root certificate uploaded to Azure
   - Certificate not expired

2. Check Azure AD authentication (if used)
   - User has required permissions
   - Conditional access policies not blocking

3. Re-download VPN client configuration
   - Configuration may be outdated

4. Verify address pool not exhausted
   - P2S address pool has available IPs

5. Check client device firewall
   - Allow OpenVPN/SSTP/IKEv2 traffic
```

#### Issue 6: P2S Client Can't Reach Peered VNets (But S2S Can)

**Symptoms:**
- P2S VPN client connects to the gateway VNet successfully
- S2S VPN can reach peered VNets from on-premises
- P2S client **cannot** reach resources in peered VNets

**Root Cause:**
After topology changes (e.g., adding VNet peering), Windows P2S VPN clients retain stale routing tables from the previously downloaded client configuration. The VPN client configuration package contains static routes that are not automatically updated.

**Resolution:**
```
1. On the P2S client machine (e.g., Windows 11):
   - Download the latest VPN client configuration package from the Azure portal
   - Reinstall the VPN client configuration
   - Reconnect to the P2S VPN

2. Verify in Azure Portal:
   - VPN Gateway → Point-to-site configuration → Download VPN client

3. This applies to:
   - Any topology change (peering, address spaces, gateway config)
   - Windows clients using SSTP or IKEv2
   - All P2S-connected clients need the updated package
```

> **Key takeaway:** Enabling BGP or changing peering transit settings will **not** fix this — the issue is that the P2S client has outdated routes. Always re-download the VPN client package after topology changes.

### Diagnostic Tools

**Azure Portal:**
- Connection Resource -> Diagnose & solve problems
- VPN Gateway -> VPN troubleshoot
- Network Watcher -> VPN troubleshoot

**Azure CLI:**
```bash
# Check connection status
az network vpn-connection show \
  --name MyS2SConnection \
  --resource-group MyRG \
  --query connectionStatus

# Check gateway health
az network vnet-gateway show \
  --name MyVpnGateway \
  --resource-group MyRG
```

**PowerShell:**
```powershell
# Get connection status
Get-AzVirtualNetworkGatewayConnection -Name MyS2SConnection -ResourceGroupName MyRG

# Get BGP peers
Get-AzVirtualNetworkGatewayBGPPeerStatus -VirtualNetworkGatewayName MyVpnGateway -ResourceGroupName MyRG

# Get learned routes
Get-AzVirtualNetworkGatewayLearnedRoute -VirtualNetworkGatewayName MyVpnGateway -ResourceGroupName MyRG
```

**Azure Monitor:**
- Metrics: Gateway Bandwidth, Tunnel Bandwidth, P2S Connection Count
- Logs: Gateway Diagnostic Logs, IKE Diagnostics

---

## 14. Pricing Considerations

### Gateway Costs

**VPN Gateway is billed as:**
1. **Gateway hours** (per hour, regardless of usage)
2. **Outbound data transfer**

**Pricing Tiers (as of 2025, approximate):**

| SKU | Monthly Cost (730 hours) | Additional Features |
|-----|--------------------------|---------------------|
| **Basic** | ~$27/month | Legacy, limited features |
| **VpnGw1** | ~$140/month | BGP, Active-Active |
| **VpnGw2** | ~$365/month | Higher throughput |
| **VpnGw3** | ~$560/month | Maximum throughput |
| **VpnGw1AZ** | ~$160/month | Zone redundancy |
| **VpnGw2AZ** | ~$395/month | Zone redundancy |
| **VpnGw3AZ** | ~$605/month | Zone redundancy |

**Data Transfer Costs:**
- Inbound: Free
- Outbound: ~$0.087/GB (first 10 TB, decreases with volume)

**Cost Optimization Tips:**

```
1. Right-size the SKU
   - Don't over-provision for "just in case"
   - Start with VpnGw1, scale up if needed

2. Use VNet Peering instead of VNet-to-VNet VPN
   - Lower latency, lower cost
   - Use VPN only when encryption required

3. Leverage hub-spoke topology
   - Share a single VPN gateway across multiple VNets
   - Use gateway transit

4. Monitor egress data transfer
   - Optimize data sync schedules
   - Use Azure services to minimize egress

5. Consider ExpressRoute for high-bandwidth scenarios
   - VPN may be more expensive at scale (data transfer costs)

6. Delete unused gateways
   - You pay per hour even if not used
   - Can redeploy when needed (30-45 minutes)
```

**Example Cost Calculation:**

**Scenario:** Small company with on-premises connectivity

```
VPN Gateway (VpnGw1):         $140/month
Data transfer (100 GB out):   $8.70/month
───────────────────────────────────────
Total:                        ~$148.70/month
```

**Scenario:** Enterprise with active-active, zone-redundant gateway

```
VPN Gateway (VpnGw2AZ):       $395/month
Data transfer (1 TB out):     $87/month
───────────────────────────────────────
Total:                        ~$482/month
```

---

## 15. Related Services

### Services that Integrate with VPN Gateway

| Service | Integration | Use Case |
|---------|-------------|----------|
| **Azure Firewall** | Route traffic through firewall after VPN | Centralized security inspection |
| **Azure Route Server** | Exchange routes between VPN and NVAs | Complex routing scenarios |
| **ExpressRoute** | Coexist for redundancy | ER primary, VPN backup |
| **Azure Bastion** | Secure VM access without public IPs | Secure management |
| **Azure DNS** | Private DNS resolution | Hybrid DNS scenarios |
| **Virtual WAN** | Hub-spoke topology at scale | Global connectivity |
| **Azure Monitor** | Gateway monitoring and alerts | Operational visibility |
| **Network Watcher** | VPN diagnostics and troubleshooting | Network troubleshooting |

### Complementary Services

- **Azure Active Directory**: P2S authentication
- **Azure Key Vault**: Store pre-shared keys securely
- **Azure DDoS Protection**: Protect gateway public IPs
- **Log Analytics**: Centralized log analysis

---

## 16. References

### Official Documentation
- [Azure VPN Gateway Documentation](https://learn.microsoft.com/en-us/azure/vpn-gateway/)
- [VPN Gateway Design](https://learn.microsoft.com/en-us/azure/vpn-gateway/design)
- [Validated VPN Devices](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-devices)
- [VPN Gateway FAQ](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-vpn-faq)
- [About P2S VPN Routing](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-point-to-site-routing)

### Azure Learning Resources
- [VPN Gateway Learning Path](https://learn.microsoft.com/en-us/training/modules/connect-on-premises-network-with-vpn-gateway/)
- [Azure Network Engineer Associate Certification](https://learn.microsoft.com/en-us/certifications/azure-network-engineer-associate/)

### Related Documentation in This Repository
- [Azure Networking Fundamentals](./01-networking-fundamentals.md)
- [VPN vs Private Link Guide](./06-vpn-private-link-guide.md)
- [ExpressRoute & BGP Guide](./07-expressroute-bgp-guide.md)
- [Azure Load Balancer](./16-azure-load-balancer.md)
- [Practice Questions: VPN Gateway](./25-practice-questions-vpn-gateway.md)

---

## Summary

**Key Takeaways:**

1. **VPN Gateway is a TYPE of Virtual Network Gateway** (not a separate service)
2. **Three main scenarios:** Site-to-Site, Point-to-Site, VNet-to-VNet
3. **On-premises equivalent:** Hardware VPN devices (Cisco, Fortinet, etc.) or software solutions
4. **High availability:** Active-active configuration with BGP for zero-downtime failover
5. **Zone redundancy:** Use AZ SKUs for 99.99% SLA
6. **Cost considerations:** Gateway hours + data transfer, right-size the SKU
7. **Security:** IPsec/IKE encryption with AES-256
8. **When to use:** Hybrid connectivity, remote access, DR scenarios
9. **Alternatives:** ExpressRoute (dedicated), VNet Peering (faster, unencrypted)
10. **Best practice:** Use route-based VPN with BGP for production workloads
