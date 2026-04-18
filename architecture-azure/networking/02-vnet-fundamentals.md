# Azure Virtual Network (VNet) Fundamentals

See [README](./README.md) for overview.

## Table of Contents

- [1. What is a VNet?](#1-what-is-a-vnet)
- [2. Key Concepts](#2-key-concepts)
- [3. Subnets](#3-subnets)
- [4. Address Space](#4-address-space)
  - [4.1 Subnet Planning for Hybrid Connectivity](#41-subnet-planning-for-hybrid-connectivity)
- [5. VNet Peering](#5-vnet-peering)
  - [5.1 Connecting Virtual Networks Across Subscriptions](#51-connecting-virtual-networks-across-subscriptions)
  - [5.2 Gateway Transit and Connectivity](#52-gateway-transit-and-connectivity)
- [6. Network Security Groups (NSG)](#6-network-security-groups-nsg)
  - [6.1 Service Tags in NSG Rules](#61-service-tags-in-nsg-rules)
- [7. Application Security Groups (ASG)](#7-application-security-groups-asg)
- [8. Network Interfaces (NICs)](#8-network-interfaces-nics)
  - [8.1 Public IP Address SKUs](#81-public-ip-address-skus)
- [9. Virtual Network Traffic Routing](#9-virtual-network-traffic-routing)
  - [9.1 User-Defined Routes (UDR)](#91-user-defined-routes-udr)
  - [9.2 Effective Routes](#92-effective-routes)
  - [9.3 Azure Route Server](#93-azure-route-server)
- [10. Azure Virtual NAT (NAT Gateway)](#10-azure-virtual-nat-nat-gateway)
  - [10.1 What is Azure NAT Gateway?](#101-what-is-azure-nat-gateway)
  - [10.2 How NAT Gateway Works](#102-how-nat-gateway-works)
  - [10.3 Benefits and Use Cases](#103-benefits-and-use-cases)
  - [10.4 Configuration and Best Practices](#104-configuration-and-best-practices)
  - [10.5 Practice Question: NAT Gateway IP Addresses and Subnet Association](#105-practice-question-nat-gateway-ip-addresses-and-subnet-association)
  - [10.6 Practice Question: NAT Characteristics and Limitations](#106-practice-question-nat-characteristics-and-limitations)
  - [10.7 Practice Question: NAT Compatibility and Protocol Support](#107-practice-question-nat-compatibility-and-protocol-support)

---

## 1. What is a VNet?

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

### On-Premises Equivalent

An **Azure Virtual Network** is the cloud equivalent of a **corporate data center LAN**. Think of it as a virtualized version of your office building's network:

| Aspect | On-Premises | Azure VNet |
|--------|------------|-----------|
| **Concept** | Physical local area network (switches, routers, cables) | Logically isolated private cloud network |
| **Network Segmentation** | VLANs on physical switches | Subnets within the VNet |
| **Default Communication** | Devices in same VLAN communicate automatically | Resources in same VNet communicate automatically |
| **Traffic Control** | Firewalls and network ACLs | Network Security Groups (NSGs) |
| **Isolation** | Physical separation + VLAN tagging | Logical isolation (no physical hardware needed) |

The key difference: In Azure, you create a **logical** network without managing physical infrastructure. You define subnets for organization and apply NSGs for security—Azure handles the underlying hardware automatically.

**Real-World Analogy**: If your office building has different departments on different floors, Azure VNet is like designing those floors virtually. Subnets are the departments, NSGs are the security checkpoints, and everything else is managed by Azure.

## 2. Key Concepts

| Concept | Description |
|---------|-------------|
| **Isolation** | VNets are logically isolated from each other |
| **Region-scoped** | A VNet exists within a single Azure region |
| **Subscription-bound** | VNets belong to a single subscription |
| **Segmentation** | Divide VNets into subnets for organization |
| **Communication** | Resources in a VNet can communicate by default |

## 3. Subnets

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

**Intra-VNet Subnet Communication:**

**Key Concept**: Subnets within the same Virtual Network can communicate with each other **by default** - no additional configuration, routing, or peering is required.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SUBNET COMMUNICATION WITHIN SAME VNET                       │
│                                                                              │
│  Virtual Network: 10.0.0.0/16                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │   Subnet A: 10.0.1.0/24          Subnet B: 10.0.2.0/24              │   │
│  │   ┌─────────────────────┐        ┌─────────────────────┐            │   │
│  │   │   ┌─────┐ ┌─────┐  │        │  ┌─────┐ ┌─────┐   │            │   │
│  │   │   │ VM1 │ │ VM2 │  │◀──────▶│  │ VM3 │ │ VM4 │   │            │   │
│  │   │   └─────┘ └─────┘  │  ✅    │  └─────┘ └─────┘   │            │   │
│  │   │                     │ Direct │                     │            │   │
│  │   │   APIM Instance     │ Comm.  │   SQL Server        │            │   │
│  │   └─────────────────────┘        └─────────────────────┘            │   │
│  │                                                                       │   │
│  │   ✅ Default behavior: All subnets in same VNet can communicate      │   │
│  │   ✅ No peering required (peering is for cross-VNet communication)   │   │
│  │   ✅ No additional routing needed                                     │   │
│  │   ✅ Traffic stays within the VNet (Azure backbone)                   │   │
│  │                                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Communication Type | Required Configuration | Example |
|-------------------|------------------------|---------|
| **Same Subnet** | None (automatic) | VM1 ↔ VM2 in Subnet A |
| **Different Subnets (same VNet)** | None (automatic) | VM1 in Subnet A ↔ VM3 in Subnet B |
| **Different VNets** | VNet Peering required | VM in VNet1 ↔ VM in VNet2 |
| **VNet to On-premises** | VPN/ExpressRoute required | Azure VM ↔ On-prem server |

**Why This Matters:**
- **Azure API Management** in one subnet can access **VMs** in another subnet within the same VNet
- **App Services** (VNet-integrated) can reach **databases** or **VMs** in different subnets
- **Network segmentation** using different subnets is for **organization and NSG rules**, not for blocking communication
- NSGs (Network Security Groups) can be used to **restrict** this default communication if needed

**Common Misconception:**
> "I need to configure something for resources in different subnets to communicate"

**Reality:**
> Subnets in the same VNet are just logical divisions. Azure automatically routes traffic between them. The only way to block this communication is by applying **NSG rules**.

## 4. Address Space

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

### 4.1 Subnet Planning for Hybrid Connectivity

When connecting Azure VNets to on-premises networks via **Site-to-Site VPN** or **ExpressRoute**, proper subnet planning is critical to avoid IP address conflicts.

**Key Principle: No Overlapping Address Spaces**

Azure VNets and on-premises networks must use **non-overlapping IP address ranges**. Overlapping addresses cause routing failures and prevent proper communication across the VPN connection.

**Planning Scenario Example:**

Consider the following requirements:
- **On-premises network**: Uses 172.16.0.0/16
- **Azure deployment**: 30 virtual machines on a single subnet
- **Connectivity**: Site-to-Site VPN between on-premises and Azure

**Subnet Size Calculations:**

| Subnet | Total IPs | Azure Reserved IPs | Usable IPs | Notes |
|--------|-----------|-------------------|-----------|-------|
| /27 | 32 | 5 | 27 | Too small for 30 VMs |
| /26 | 64 | 5 | 59 | Adequate for 30 VMs |
| /25 | 128 | 5 | 123 | Good headroom |
| /24 | 256 | 5 | 251 | Recommended for growth |

**Correct vs Incorrect Subnet Choices:**

| Subnet Address | Result | Explanation |
|----------------|--------|-------------|
| **172.16.0.0/16** | ❌ **Incorrect** | Exactly matches on-premises range. Causes IP conflicts and routing failures across VPN. |
| **172.16.1.0/27** | ❌ **Incorrect** | Falls within on-premises 172.16.0.0/16 range. Creates routing conflicts. Also provides only 27 usable IPs, insufficient for 30 VMs. |
| **192.168.1.0/27** | ❌ **Incorrect** | Avoids address space conflict but provides only 27 usable IPs, which is not enough for 30 VMs. |
| **192.168.0.0/24** | ✅ **Correct** | Non-overlapping with on-premises (192.168.x.x ≠ 172.16.x.x). Provides 251 usable IPs, sufficient for 30 VMs with room for growth. |

**Best Practices for Hybrid Connectivity:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   Hybrid Network Planning                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  On-Premises Network                                            │
│  ┌────────────────────────┐                                     │
│  │  172.16.0.0/16         │                                     │
│  │  (1,048,576 addresses) │                                     │
│  └────────────────────────┘                                     │
│              │                                                   │
│              │ Site-to-Site VPN                                 │
│              ▼                                                   │
│  Azure Virtual Network                                          │
│  ┌────────────────────────┐                                     │
│  │  192.168.0.0/16        │ ← Different address space          │
│  │  ┌──────────────────┐  │                                     │
│  │  │ Subnet1          │  │                                     │
│  │  │ 192.168.0.0/24   │  │ ← 251 usable IPs                   │
│  │  │ (30 VMs)         │  │                                     │
│  │  └──────────────────┘  │                                     │
│  │  ┌──────────────────┐  │                                     │
│  │  │ GatewaySubnet    │  │                                     │
│  │  │ 192.168.255.0/27 │  │                                     │
│  │  └──────────────────┘  │                                     │
│  └────────────────────────┘                                     │
│                                                                  │
│  Result: No routing conflicts, seamless connectivity            │
└─────────────────────────────────────────────────────────────────┘
```

**Common Address Space Planning Strategies:**

1. **Document Existing Ranges**: Inventory all on-premises IP ranges before designing Azure networks
2. **Reserve Azure-Specific Ranges**: Use different RFC 1918 ranges for Azure (e.g., if on-prem uses 172.16.x.x, use 10.x.x.x or 192.168.x.x for Azure)
3. **Plan for Growth**: Choose subnet sizes that accommodate future expansion (typically at least 2x current requirements)
4. **Gateway Subnet Sizing**: Minimum /27 for VPN Gateway subnet, /26 or larger recommended for ExpressRoute
5. **Avoid Fragmentation**: Use contiguous address spaces when possible for easier management

**Address Space Isolation Example:**

| Network Location | Address Range | Purpose |
|------------------|---------------|---------|
| On-Premises HQ | 172.16.0.0/16 | Corporate network |
| On-Premises Branch 1 | 172.17.0.0/16 | Branch office |
| Azure Production VNet | 10.0.0.0/16 | Production workloads |
| Azure Dev/Test VNet | 10.1.0.0/16 | Development environment |
| Azure DR VNet | 10.2.0.0/16 | Disaster recovery |

## 5. VNet Peering

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

**Requirements and Limitations:**
- VNets involved in peering must have **non-overlapping IP address spaces**
- Once peered, you **cannot** add or delete address ranges from a VNet's address space
- In a globally peered VNet, resources cannot communicate with the front-end IP of a **Basic** internal load balancer (use **Standard** Load Balancer for global peering)
- Default Azure name resolution does **not** work across peered VNets — use Azure Private DNS zones or custom DNS
- Peering is **not transitive**: if VNet A is peered with VNet B, and VNet B with VNet C, VNet A and C cannot communicate unless explicitly peered
- Creating or modifying a peering causes **no downtime** for resources in either VNet
- Cross-deployment model peering is supported: a VNet created via **Azure Resource Manager** can be peered with a VNet created via the **classic deployment model**

### 5.1 Connecting Virtual Networks Across Subscriptions

**Important**: Virtual networks cannot span subscriptions. Each VNet belongs to a single subscription. To connect VNets in different subscriptions (e.g., Sub1 and Sub2), you have two options:

| Solution | Description | Use Case |
|----------|-------------|----------|
| **Virtual Network Peering** | Direct connection between two VNets across subscriptions | Preferred for most scenarios; low latency, high bandwidth |
| **VPN Gateways (VNet-to-VNet)** | Encrypted VPN tunnel between two VNets | When encryption is required or peering is not feasible |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            CONNECTING VNETS ACROSS SUBSCRIPTIONS                             │
│                                                                              │
│   Subscription: Sub1                      Subscription: Sub2                 │
│   ┌─────────────────────────────┐        ┌─────────────────────────┐        │
│   │  VNet1: 10.1.0.0/16     │            │  VNet2: 10.2.0.0/16     │        │
│   │  ┌─────────────────┐    │            │    ┌─────────────────┐  │        │
│   │  │     VM-A        │    │            │    │     VM-B        │  │        │
│   │  │   10.1.1.4      │    │            │    │   10.2.1.4      │  │        │
│   │  └─────────────────┘    │            │    └─────────────────┘  │        │
│   └───────────┬─────────────┘            └───────────┬─────────────┘        │
│               │                                       │                      │
│               │     Option 1: VNet Peering           │                      │
│               └──────────── ◀─────────────────────────┘                      │
│                         (Direct Connection)                                  │
│                                                                              │
│               │     Option 2: VPN Gateway            │                      │
│               └──────────── ◀════════════════════════┘                      │
│                         (Encrypted Tunnel)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Option 1: Virtual Network Peering (Recommended)**
- Creates a direct, low-latency connection between VNets
- Traffic stays on Azure backbone network (private)
- No encryption overhead (traffic is already within Azure)
- Requires appropriate RBAC permissions in both subscriptions
- Can also peer across different Azure AD tenants

**Option 2: VPN Gateways (VNet-to-VNet)**
- Creates an IPsec/IKE encrypted tunnel between VNets
- Useful when additional encryption is required
- Requires a VPN Gateway in each VNet (GatewaySubnet)
- Higher latency and cost compared to peering
- Can be combined with other S2S VPN connections

**Why Not Azure Private Link?**
Azure Private Link is designed for accessing PaaS services privately, not for connecting entire virtual networks. It creates private endpoints to specific services, not network-to-network connectivity.

> **Exam Tip**: When asked about connecting VNets across subscriptions, the correct answers are **Virtual Network Peering** and **VPN Gateways**. Azure Private Link and ExpressRoute are not solutions for VNet-to-VNet connectivity across subscriptions.

**References:**
- [Design for subscriptions - Microsoft Learn](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-area/resource-org-subscriptions)
- [Configure a VNet-to-VNet VPN gateway connection - Azure Portal](https://learn.microsoft.com/azure/vpn-gateway/vpn-gateway-howto-vnet-vnet-resource-manager-portal)

### 5.2 Gateway Transit and Connectivity

**Gateway transit** lets a peered VNet use the VPN gateway in the **remote VNet** to reach networks **outside** the peering. This avoids deploying a second gateway.

**Explicit definition:** Gateway transit is **not** a separate Azure resource. It is a **VNet peering configuration** that enables a spoke VNet to use the hub VNet's existing **VPN/ExpressRoute gateway** for external connectivity.

**Typical uses:**
- **Site-to-site VPN** from the hub VNet to on-premises
- **VNet-to-VNet** connection to another VNet
- **Point-to-site VPN** for client access

**How it works (hub-and-spoke):**
```
On-Premises
   |
S2S VPN
   |
Hub VNet (has VPN Gateway)
   |  (gateway transit)
   |
Spoke VNet (no gateway)
```

**Key points:**
- A VNet can have **only one** gateway.
- Gateway transit is supported for **regional** and **global** VNet peering.
- The **hub VNet** advertises its gateway; the **spoke VNet** uses that remote gateway.
- Traffic to external networks flows **through the hub gateway**; east-west traffic between VNets still uses peering.

**Configuration terms (portal/API):**
- **Hub peering**: *Allow gateway transit* = Enabled
- **Spoke peering**: *Use remote gateways* = Enabled

**Why it matters:** Gateway transit enables centralized connectivity (single gateway, centralized routing and security) while keeping spokes lightweight and cost-effective.

### 5.3 Allow Forwarded Traffic (Traffic Forwarding in Peering)

**Allow forwarded traffic** is a separate VNet peering setting that controls whether traffic **not originating in the directly peered VNet** can traverse the peering link.

**Why it is needed in hub-and-spoke:**

In a hub-and-spoke topology, spoke VNets communicate with each other *through* the hub. Traffic from VNet1 (Spoke 1) that needs to reach VNet2 (Spoke 2) travels like this:

```
VNet1 → [peering: VNet1↔VNet3] → VNet3 (Hub, VPN Gateway) → [peering: VNet3↔VNet2] → VNet2
```

From VNet3's perspective, when forwarding VNet1's traffic toward VNet2, that traffic was **not originated by VNet3**. Without **Allow Forwarded Traffic** enabled on the VNet3↔VNet2 peering, Azure drops it.

**Topology — Hub without VM or NVA:**

The key point of this pattern is that **VNet3 contains only a VPN Gateway** — no virtual machines, no Network Virtual Appliance (NVA), no firewall. The gateway itself is the routing device. Azure's built-in routing forwards traffic between peered spokes entirely at the platform level.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          East US Region                                        │
│                                                                                │
│   ┌──────────────────────────────────────────────┐                            │
│   │              VNet3 — Hub (10.3.0.0/16)       │                            │
│   │                                              │                            │
│   │   GatewaySubnet (10.3.255.0/27)              │                            │
│   │   ┌──────────────────────────────────────┐   │                            │
│   │   │       VPN Virtual Network Gateway    │   │                            │
│   │   │       (Platform-managed resource)    │   │                            │
│   │   │                                      │   │                            │
│   │   │  ✅ No VMs                           │   │                            │
│   │   │  ✅ No NVA / firewall appliance      │   │                            │
│   │   │  ✅ Routing done by Azure platform   │   │                            │
│   │   └──────────────────────────────────────┘   │                            │
│   └──────────────┬──────────────────┬────────────┘                            │
│                  │                  │                                          │
│     Peering A    │                  │   Peering B                             │
│  AllowFwdTraffic │                  │ AllowFwdTraffic                         │
│  AllowGWTransit  │                  │ AllowGWTransit                          │
│                  │                  │                                          │
│   ┌──────────────┴───┐          ┌───┴──────────────┐                          │
│   │  VNet1 — Spoke   │          │  VNet2 — Spoke   │                          │
│   │  (10.1.0.0/16)   │          │  (10.2.0.0/16)   │                          │
│   │                  │          │                  │                          │
│   │  ┌────┐ ┌────┐   │          │   ┌────┐ ┌────┐  │                          │
│   │  │VM-A│ │VM-B│   │          │   │VM-C│ │VM-D│  │                          │
│   │  └────┘ └────┘   │          │   └────┘ └────┘  │                          │
│   │                  │          │                  │                          │
│   │ UseRemoteGW ✅   │          │ UseRemoteGW ✅   │                          │
│   │ AllowFwdTraf ✅  │          │ AllowFwdTraf ✅  │                          │
│   └──────────────────┘          └──────────────────┘                          │
│                                                                                │
│   VM-A ──► VPN Gateway (VNet3) ──► VM-C  (no NVA involved)                   │
│                                                                                │
│   ✗  VNet1 ↔ VNet2 direct peering  (does NOT exist)                          │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Why no VM or NVA is needed here:**

| Routing role | Without NVA (this pattern) | With NVA |
|---|---|---|
| **Who routes traffic** | Azure VPN Gateway (platform resource) | A VM running a firewall/router OS |
| **Traffic inspection** | ❌ Not inspected — forwarded as-is | ✅ Can deep-inspect, filter, log |
| **Configuration** | Peering settings only | UDRs pointing to NVA private IP |
| **Cost** | Gateway SKU cost only | Gateway + VM/NVA license cost |
| **Use when** | Connectivity is the goal, not inspection | Security inspection of east-west traffic is required |

> **Note:** If you need to inspect spoke-to-spoke traffic (e.g., with Azure Firewall or a third-party NVA), replace the VPN Gateway-only hub with a hub that also contains the firewall, and add User-Defined Routes (UDRs) on each spoke subnet to send `0.0.0.0/0` to the firewall's private IP. This is the full hub-and-spoke with Azure Firewall pattern.

**Full peering configuration matrix for hub-and-spoke via VPN Gateway:**

| Peering Link | Direction | Setting | Value | Purpose |
|---|---|---|---|---|
| VNet1 ↔ VNet3 | VNet1 → VNet3 (spoke side) | Allow Forwarded Traffic | **Enabled** | Allow hub to forward VNet1's traffic onward |
| VNet1 ↔ VNet3 | VNet1 → VNet3 (spoke side) | Use Remote Gateways | Enabled | Spoke uses hub's VPN gateway |
| VNet1 ↔ VNet3 | VNet3 → VNet1 (hub side) | Allow Gateway Transit | Enabled | Hub shares its gateway with spoke |
| VNet1 ↔ VNet3 | VNet3 → VNet1 (hub side) | Allow Forwarded Traffic | **Enabled** | Allow forwarded traffic from other spokes |
| VNet2 ↔ VNet3 | VNet2 → VNet3 (spoke side) | Allow Forwarded Traffic | **Enabled** | Allow hub to forward VNet2's traffic onward |
| VNet2 ↔ VNet3 | VNet2 → VNet3 (spoke side) | Use Remote Gateways | Enabled | Spoke uses hub's VPN gateway |
| VNet2 ↔ VNet3 | VNet3 → VNet2 (hub side) | Allow Gateway Transit | Enabled | Hub shares its gateway with spoke |
| VNet2 ↔ VNet3 | VNet3 → VNet2 (hub side) | Allow Forwarded Traffic | **Enabled** | Allow forwarded traffic from other spokes |

> **No direct peering between VNet1 and VNet2** — all traffic is routed through VNet3 (the hub).

**Comparison: Allow Forwarded Traffic vs. Allow Gateway Transit**

| Setting | Controls | Where Configured | Required For |
|---|---|---|---|
| **Allow Forwarded Traffic** | Traffic that did **not originate** in the directly connected VNet | Both sides of the peering | Spoke-to-spoke communication through hub |
| **Allow Gateway Transit** | Sharing the hub's VPN/ExpressRoute gateway | Hub side of the peering | Spoke VNets reaching on-premises/external networks via hub |
| **Use Remote Gateways** | Using the remote (hub) gateway | Spoke side of the peering | Required when Allow Gateway Transit is enabled on hub |

**Common mistake:** Enabling only gateway transit without enabling forwarded traffic. Gateway transit allows spokes to reach **external/on-premises** networks via the hub gateway, but it does **not** automatically allow spoke-to-spoke traffic to be forwarded through the hub.

## 6. Network Security Groups (NSG)

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

### 6.1 Service Tags in NSG Rules

**Service Tags** represent groups of IP address prefixes from specific Azure services, managed automatically by Azure. They simplify NSG rule creation and maintenance without requiring manual IP address management.

**Benefits of Service Tags:**

| Benefit | Description |
|---------|-------------|
| **Automatic Updates** | Azure manages IP ranges; no manual updates needed |
| **Service-Specific** | Target specific Azure services (Key Vault, Storage, SQL, etc.) |
| **Least Privilege** | Allow only necessary service traffic |
| **Simplified Management** | No need to track changing Azure service IPs |
| **Regional Scope** | Some tags support regional filtering (e.g., `Storage.EastUS`) |

**Common Service Tags:**

| Service Tag | Purpose |
|-------------|---------|
| `AzureKeyVault` | Azure Key Vault service |
| `Storage` | Azure Storage (all regions) |
| `Storage.EastUS` | Azure Storage in specific region |
| `Sql` | Azure SQL Database, SQL Managed Instance |
| `AzureActiveDirectory` | Microsoft Entra ID |
| `AzureLoadBalancer` | Azure infrastructure load balancer |
| `Internet` | Internet-accessible IP space |
| `VirtualNetwork` | All VNet address spaces |

**Exam Scenario: Allowing VMs to Access Key Vault**

**Question:**

You have an Azure subscription that contains:
- 10 virtual machines in East US region
- A key vault named Vault1
- A network security group (NSG) named NSG1

The virtual machines are protected by NSG1, which is configured to **block all outbound traffic to the internet**.

You need to ensure that the virtual machines can access Vault1. The solution must use the **principle of least privilege** and **minimize administrative effort**.

What should you configure as the destination of the outbound security rule for NSG1?

**Options:**

A) An application security group  
B) An IP address range  
C) A service tag ✅  
D) A virtual network

**Answer: C) A service tag**

**Why Service Tags are Correct:**

| Requirement | How Service Tags Address It |
|-------------|----------------------------|
| **Access Key Vault** | `AzureKeyVault` service tag includes all Key Vault IPs |
| **Least Privilege** | Only allows traffic to Key Vault, not entire internet |
| **Minimize Administrative Effort** | Azure automatically updates IP ranges |
| **No Manual Maintenance** | No need to track changing Key Vault IPs |
| **Works Cross-Region** | Tag includes all Key Vault endpoints |

**Why Other Options are Incorrect:**

| Option | Why Incorrect |
|--------|--------------|
| **Application Security Group** | ASGs group VMs for NSG rules, they cannot represent Azure PaaS services like Key Vault |
| **IP Address Range** | Requires manually identifying and maintaining Key Vault IP addresses; error-prone and inefficient as IPs change |
| **Virtual Network** | Key Vault is a PaaS service outside the VNet; this wouldn't allow access |

**Implementation Example:**

```bash
# Add outbound NSG rule to allow Key Vault access
az network nsg rule create \
  --resource-group myResourceGroup \
  --nsg-name NSG1 \
  --name AllowKeyVaultOutbound \
  --priority 100 \
  --direction Outbound \
  --source-address-prefixes VirtualNetwork \
  --destination-address-prefixes AzureKeyVault \
  --destination-port-ranges 443 \
  --protocol Tcp \
  --access Allow \
  --description "Allow VMs to access Azure Key Vault"
```

**NSG Rule Configuration:**

| Property | Value |
|----------|-------|
| **Priority** | 100 (higher than deny-all rule) |
| **Direction** | Outbound |
| **Source** | VirtualNetwork (or specific subnet) |
| **Destination** | **AzureKeyVault** (service tag) |
| **Port** | 443 (HTTPS) |
| **Protocol** | TCP |
| **Action** | Allow |

**Key Takeaways:**
- ✅ Service tags simplify Azure service access through NSGs
- ✅ `AzureKeyVault` tag automatically includes all Key Vault endpoints
- ✅ Azure maintains service tag IP ranges automatically
- ✅ Follows least privilege: only Key Vault access allowed, internet still blocked
- ⚠️ Application Security Groups only work for grouping VMs, not Azure services
- ⚠️ Manual IP ranges require constant maintenance as Azure IPs change

---

## 7. Application Security Groups (ASG)

**Application Security Groups (ASGs)** enable you to group virtual machines based on their application roles or functions, and define network security rules based on those groups instead of explicit IP addresses.

**Why Use ASGs?**

| Challenge | ASG Solution |
|-----------|-------------|
| **IP addresses change frequently** | Group VMs by role, not IP |
| **Managing rules for many VMs** | Single rule applies to entire group |
| **Application-centric security** | Define rules by workload type |
| **Scalability** | Add/remove VMs from group without rule changes |

**How ASGs Work:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Virtual Network (VNET1)                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                        Subnet1                                 │ │
│  │                                                                │ │
│  │   ASG: Web-Servers                 ASG: Management-Servers     │ │
│  │   ┌─────────────────────┐         ┌─────────────────────┐     │ │
│  │   │ ┌────┐ ┌────┐ ┌────┐│         │ ┌────┐ ┌────┐ ┌────┐│     │ │
│  │   │ │ VM │ │ VM │ │ VM ││         │ │ VM │ │ VM │ │ VM ││     │ │
│  │   │ └────┘ └────┘ └────┘│         │ └────┘ └────┘ └────┘│     │ │
│  │   └─────────────────────┘         └─────────────────────┘     │ │
│  │            │                                │                  │ │
│  │            ▼                                ▼                  │ │
│  │    Allow HTTPS (443)                Allow RDP (3389)          │ │
│  │    from Internet                    from Internet              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- ✅ **Application-centric grouping**: Organize VMs by role (Web, App, DB, Management)
- ✅ **Dynamic membership**: VMs can be added/removed without modifying NSG rules
- ✅ **IP address independence**: Rules work regardless of IP changes
- ✅ **Simplified rule management**: One rule for entire application tier
- ✅ **Same subnet support**: VMs in the same subnet can be in different ASGs

**NSG Rules with ASGs:**

```plaintext
Network Security Group: NSG-Subnet1

┌──────────┬───────────────────┬────────────────┬──────────────────┬────────┐
│ Priority │ Name              │ Source         │ Destination      │ Action │
├──────────┼───────────────────┼────────────────┼──────────────────┼────────┤
│ 100      │ Allow-HTTPS-Web   │ Internet       │ ASG:Web-Servers  │ Allow  │
│ 110      │ Allow-RDP-Mgmt    │ Internet       │ ASG:Mgmt-Servers │ Allow  │
│ 200      │ Deny-RDP-Web      │ Any            │ ASG:Web-Servers  │ Deny   │
│ 65500    │ DenyAllInbound    │ Any            │ Any              │ Deny   │
└──────────┴───────────────────┴────────────────┴──────────────────┴────────┘
```

**ASG vs Other Options:**

| Method | Use Case | Limitation |
|--------|----------|------------|
| **ASG** | Group VMs by application role | Works within same VNet only |
| **NSG with IPs** | Static VM IPs | Hard to manage when IPs change |
| **Network Rules (Firewall)** | Cross-VNet, advanced filtering | More complex, higher cost |
| **Azure Firewall** | Enterprise-grade, centralized | Higher cost, more setup |

**Exam Scenario: Grouping VMs by Application Role**

**Question:**

You have a virtual network named VNET1 with a subnet named Subnet1. The organization has two groups of servers:
- **Web Servers**: Should display IIS web page when accessed from the internet
- **Management Servers**: Should allow RDP access from the internet

Requirements:
- ✅ RDP into Management Servers, but NOT Web Servers
- ✅ Web Servers accessible via HTTPS from the internet
- ⚠️ Private IP addresses of VMs change frequently

How would you group virtual machines into Web Servers and Management Servers?

**Options:**
- A) Network Rule
- B) Network Security Groups (NSGs)
- C) Application Security Groups (ASGs) ✅
- D) Azure Firewall

**Answer: C) Application Security Groups (ASGs)**

**Why ASGs are Correct:**

| Requirement | How ASGs Address It |
|-------------|--------------------|
| **Group VMs by role** | Create ASG-WebServers and ASG-ManagementServers |
| **Different access rules per group** | NSG rules reference ASGs as destination |
| **IP addresses change frequently** | ASGs are independent of IP addresses |
| **Allow HTTPS to Web only** | Rule: Allow 443 to ASG-WebServers |
| **Allow RDP to Management only** | Rule: Allow 3389 to ASG-ManagementServers |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Network Rule** | Not a standalone Azure feature for VM grouping |
| **NSG alone** | Would require IP-based rules; doesn't solve IP change problem |
| **Azure Firewall** | Overkill for this scenario; higher cost and complexity |

**Implementation Steps:**

```plaintext
1. Create Application Security Groups:
   → Azure Portal → Application security groups → Create
   → Create "ASG-WebServers" and "ASG-ManagementServers"

2. Associate VMs to ASGs:
   → VM → Networking → Application security groups
   → Add to appropriate ASG based on role

3. Create NSG Rules using ASGs:
   → NSG → Inbound security rules → Add
   → Use ASG as destination instead of IP addresses
```

**References:**
- [Application Security Groups Overview](https://learn.microsoft.com/en-us/azure/virtual-network/application-security-groups)
- [Filter network traffic with NSGs](https://learn.microsoft.com/en-us/azure/virtual-network/tutorial-filter-network-traffic)

---

## 8. Network Interfaces (NICs)

**Network Interfaces (NICs)** are the interconnection between a virtual machine and a virtual network. A NIC enables an Azure VM to communicate with internet, Azure, and on-premises resources.

**Key Concepts:**

| Concept | Description |
|---------|-------------|
| **Purpose** | Connects VM to a virtual network subnet |
| **IP Assignment** | Can have both public AND private IP addresses |
| **One NIC Minimum** | Each VM requires at least one NIC |
| **Multiple NICs** | Larger VM sizes support multiple NICs for network redundancy |
| **Attachment** | Must be attached to a VM in the same location and subscription |

**IP Address Configuration:**

A single NIC can have:
- ✅ **One Private IP Address** (required) - Used for communication within VNet
- ✅ **One Public IP Address** (optional) - Used for internet-facing communication
- ✅ **Multiple IP Configurations** - A single NIC can have multiple private IPs

**Network Interface Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Virtual Machine                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            Network Interface (NIC)                     │  │
│  │                                                        │  │
│  │  Private IP: 10.0.1.4 ────────────► Virtual Network   │  │
│  │  Public IP:  20.1.2.3  ─────────────► Internet        │  │
│  │                                                        │  │
│  │  NSG: Attached to control traffic                     │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Important Characteristics:**

| Characteristic | Details |
|----------------|---------|
| **Subnet Association** | NIC is associated with a specific subnet in a VNet |
| **Security** | NSGs can be applied to NICs for traffic filtering |
| **IP Forwarding** | Can be enabled for routing scenarios |
| **Accelerated Networking** | Can be enabled for improved network performance |
| **DNS Settings** | Can have custom DNS servers configured |

**Multiple NICs per VM:**

Larger VM sizes support multiple NICs:
- **Standard_D2s_v3**: Maximum 2 NICs
- **Standard_D4s_v3**: Maximum 4 NICs
- **Standard_D8s_v3**: Maximum 8 NICs

**Use Cases for Multiple NICs:**
- 🔹 Network virtual appliances (firewalls, load balancers)
- 🔹 Front-end/back-end network separation
- 🔹 Management traffic isolation
- 🔹 High-availability scenarios

**Practice Question: Minimum NICs for VM Deployment**

**Scenario:**

Your company has a Microsoft Entra ID subscription. You need to deploy five virtual machines (VMs) to your company's virtual network subnet.

**Requirements:**
- ✅ Each VM will have both a public and private IP address
- ✅ Inbound and outbound security rules must be identical for all VMs
- ❓ What is the minimum number of network interfaces needed?

**Options:**
- A) 5 ✅
- B) 10
- C) 20
- D) 40

**Correct Answer: A) 5 Network Interfaces**

**Why 5 is Correct:**

| Reasoning | Explanation |
|-----------|-------------|
| **One NIC per VM** | Each VM requires at least one network interface to connect to the VNet |
| **Both IP Types on One NIC** | A single NIC can have BOTH a private IP (required) and a public IP (optional) |
| **No Need for Multiple NICs** | The requirement for both IP types does NOT require separate NICs |
| **Security Rules** | NSGs can be applied at subnet or NIC level to maintain identical rules |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|--------------|
| **10 NICs** | Would mean 2 NICs per VM - unnecessary since one NIC supports both public and private IPs |
| **20 NICs** | Would mean 4 NICs per VM - excessive and not required for this scenario |
| **40 NICs** | Would mean 8 NICs per VM - far more than necessary and wasteful |

**Configuration Breakdown:**

```plaintext
VM1: NIC1 → Private IP: 10.0.1.4, Public IP: 20.1.2.3
VM2: NIC2 → Private IP: 10.0.1.5, Public IP: 20.1.2.4
VM3: NIC3 → Private IP: 10.0.1.6, Public IP: 20.1.2.5
VM4: NIC4 → Private IP: 10.0.1.7, Public IP: 20.1.2.6
VM5: NIC5 → Private IP: 10.0.1.8, Public IP: 20.1.2.7

Total NICs Required: 5
```

**Maintaining Identical Security Rules:**

To ensure identical inbound/outbound rules for all VMs:

| Approach | Implementation |
|----------|----------------|
| **Subnet-Level NSG** | Apply one NSG to the subnet containing all 5 VMs |
| **Application Security Group** | Create an ASG, add all 5 VMs to it, and reference in NSG rules |
| **NIC-Level NSG** | Apply the same NSG to all 5 NICs (more management overhead) |

**Best Practice:**
Use a **subnet-level NSG** or **Application Security Groups** for centralized rule management rather than managing individual NIC-level NSGs.

**Key Takeaway:**
> 🔑 **One NIC can have both public and private IP addresses.** You don't need separate NICs for each IP type. The minimum number of NICs equals the number of VMs.

---

**Practice Question: Network Virtual Appliance with Multiple NICs**

**Scenario:**

You are deploying a network virtual appliance (NVA) in Azure to act as a firewall between your frontend and backend subnets. The architecture requires:

- **Frontend Subnet** (10.0.1.0/24): Web servers that receive traffic from the internet
- **Backend Subnet** (10.0.2.0/24): Database servers that should only be accessible through the NVA
- **Management Subnet** (10.0.3.0/24): For administrative access to the NVA

**Requirements:**
- ✅ NVA must inspect and route traffic between frontend and backend subnets
- ✅ NVA must have dedicated management access isolated from application traffic
- ✅ Each network segment must be on a separate subnet for security policy enforcement
- ✅ Traffic from frontend to backend must pass through the NVA

**Question:** How many network interfaces does the NVA virtual machine require?

**Options:**
- A) 1 NIC
- B) 2 NICs
- C) 3 NICs ✅
- D) 4 NICs

**Correct Answer: C) 3 NICs**

**Why 3 NICs are Required:**

| NIC | Purpose | Subnet | IP Address | Traffic Type |
|-----|---------|--------|------------|--------------|
| **NIC 1** | Frontend Interface | Frontend Subnet | 10.0.1.10 | Receives traffic from web servers |
| **NIC 2** | Backend Interface | Backend Subnet | 10.0.2.10 | Forwards inspected traffic to database servers |
| **NIC 3** | Management Interface | Management Subnet | 10.0.3.10 | Administrative access (SSH/RDP) |

**Architecture Diagram:**

```
                              Internet
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Frontend Subnet      │
                    │   (10.0.1.0/24)        │
                    │  ┌──────┐  ┌──────┐    │
                    │  │ Web1 │  │ Web2 │    │
                    │  └──────┘  └──────┘    │
                    └──────────┬─────────────┘
                               │
                     ┌─────────▼──────────┐
                     │   NVA Firewall     │
                     │                    │
                     │  NIC1: 10.0.1.10   │◄─── Frontend Traffic
                     │  NIC2: 10.0.2.10   │◄─── Backend Traffic
                     │  NIC3: 10.0.3.10   │◄─── Management Access
                     └─────────┬──────────┘
                               │
                    ┌──────────▼─────────────┐
                    │   Backend Subnet       │
                    │   (10.0.2.0/24)        │
                    │  ┌──────┐  ┌──────┐    │
                    │  │ DB1  │  │ DB2  │    │
                    │  └──────┘  └──────┘    │
                    └────────────────────────┘
                    
        Management Subnet (10.0.3.0/24) for NVA admin access
```

**Why Each NIC is Necessary:**

| Reason | Explanation |
|--------|-------------|
| **Network Segmentation** | Each subnet requires a separate NIC for the NVA to participate in that network |
| **Routing Between Subnets** | NVA needs to receive traffic on one NIC and forward to another after inspection |
| **Security Isolation** | Management traffic must be isolated from application traffic |
| **IP Forwarding** | Each NIC can have IP forwarding enabled to route between networks |
| **NSG Policies** | Different NSG rules can be applied to each NIC/subnet |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|--------------|
| **1 NIC** | Cannot route between multiple subnets; NVA would only connect to one subnet |
| **2 NICs** | Could handle frontend-backend routing but lacks isolated management access |
| **4 NICs** | More than needed for this three-subnet scenario |

**Configuration Requirements:**

```plaintext
1. Create the NVA VM with appropriate size:
   → Standard_D4s_v3 or higher (supports 4+ NICs)

2. Attach three NICs during or after VM creation:
   → NIC1 attached to Frontend Subnet
   → NIC2 attached to Backend Subnet
   → NIC3 attached to Management Subnet

3. Enable IP Forwarding on NIC1 and NIC2:
   → Required for routing traffic between subnets
   → Management NIC typically doesn't need IP forwarding

4. Configure User-Defined Routes (UDR):
   → Frontend subnet: Route 10.0.2.0/24 → Next hop: NVA NIC1 (10.0.1.10)
   → Backend subnet: Route 0.0.0.0/0 → Next hop: NVA NIC2 (10.0.2.10)

5. Configure NSGs for each NIC:
   → NIC1: Allow inbound from internet/web servers
   → NIC2: Allow outbound to database servers
   → NIC3: Allow SSH/RDP from admin workstations only
```

**Real-World Use Cases for Multiple NICs:**

| Scenario | NICs Required | Reason |
|----------|---------------|--------|
| **Firewall/NVA** | 2-4 NICs | Separate NICs for each security zone (DMZ, internal, management) |
| **Load Balancer Appliance** | 2 NICs | Frontend for clients, backend for servers |
| **VPN Gateway Appliance** | 2 NICs | Public NIC for VPN, private NIC for internal network |
| **Database Server with Replication** | 2 NICs | Application traffic vs. database replication traffic |
| **Multi-Tier App Component** | 2-3 NICs | Frontend, backend, and management separation |

**Comparison: When You Need 1 NIC vs Multiple NICs:**

| Requirement | NICs Needed | Example |
|-------------|-------------|---------|
| VM needs both public and private IP | **1 NIC** | Standard web server |
| VM needs to route between two networks | **2 NICs** | Simple firewall between subnets |
| VM provides services across three networks | **3 NICs** | NVA with management network |
| VM acts as DMZ appliance | **3-4 NICs** | External, DMZ, internal, management |

**References:**
- [Virtual Network Interfaces](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface)
- [IP addresses in Azure](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses)
- [Multiple NICs in Azure VMs](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/multiple-nics)
- [Network Virtual Appliances in Azure](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/nva-ha)

### 8.1 Public IP Address SKUs

Azure public IP addresses are created using either a **Basic** or **Standard** SKU. The SKU determines the allocation method, security features, availability, and supported scenarios.

**SKU Comparison:**

| Feature | Basic SKU | Standard SKU |
|---------|-----------|--------------|
| **Allocation Method** | Dynamic or Static | **Static only** |
| **Security** | Open by default (NSG optional) | Secure by default (NSG required) |
| **Availability Zones** | Not supported | Zone-redundant or zonal |
| **Routing Preference** | Not supported | Supported (Internet or Microsoft Network) |
| **Global Tier** | Not supported | Supported |
| **SLA** | No SLA | 99.99% SLA |

**Key Distinction — Allocation Methods:**

| SKU | Dynamic Allocation | Static Allocation |
|-----|-------------------|-------------------|
| **Basic** | ✅ Supported | ✅ Supported |
| **Standard** | ❌ Not supported | ✅ Supported (always static) |

- **Dynamic allocation**: IP address is assigned when the public IP is associated with a resource (e.g., VM start). The IP may change when the resource is stopped/deallocated.
- **Static allocation**: IP address is assigned immediately upon creation and remains fixed until the public IP resource is deleted.

> 🔑 **Key Takeaway**: If you need **dynamic IP addresses** for resources on your VNet, you must use a **Basic SKU** public IP. Standard SKU always uses static allocation.

> ⚠️ **Note**: Basic SKU public IPs are planned for retirement. Microsoft recommends using Standard SKU for new deployments. However, for exam purposes, understanding the allocation method differences remains important.

**References:**
- [Public IP addresses in Azure](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses)
- [Create a public IP address - Azure Portal](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/create-public-ip-portal)

---

## 9. Virtual Network Traffic Routing

**Azure routing** determines how network traffic flows between subnets and to external networks. Traffic routing decisions are governed by **route tables** containing routing entries, **system routes** (created automatically by Azure), and **user-defined routes (UDRs)** that you create.

### 9.1 User-Defined Routes (UDR)

**User-Defined Routes** allow you to override Azure's default routing and explicitly control traffic paths within your virtual network.

**Key Concept:**
UDRs let you specify custom destinations and next hops. For example, instead of letting traffic flow directly between subnets, you can force it through a **network virtual appliance (NVA)** like a firewall or router for inspection and logging.

**Route Table Structure:**

```
Route Table: RT-Production
├── Route 1: Destination: 10.0.2.0/24, Next Hop: Virtual Appliance 10.0.1.5
├── Route 2: Destination: 192.168.0.0/16, Next Hop: VPN Gateway
├── Route 3: Destination: 0.0.0.0/0, Next Hop: Internet
└── [System Routes - added automatically]
```

**How UDRs Work:**

1. **Create a Route Table** in your VNet
2. **Define Routes** with destination CIDR and next hop
3. **Associate Route Table** to a subnet
4. **Traffic is evaluated** against routes in order of matching:
   - Most specific (longest CIDR prefix) matches first
   - If no match, system routes apply
   - If still no match, packet is dropped

**Route Components:**

| Component | Description | Example |
|-----------|-------------|---------|
| **Destination** | CIDR block of traffic destination | 192.168.0.0/16, 10.0.2.0/24, 0.0.0.0/0 |
| **Next Hop Type** | Where traffic is sent | Virtual Appliance, VPN Gateway, Virtual Network Gateway, Internet, None |
| **Next Hop IP** | Address of next hop | 10.0.1.5 (NVA), 192.168.1.1 (gateway) |

**Common Next Hop Types:**

| Next Hop Type | Use Case | Example |
|---------------|----------|---------|
| **Virtual Appliance** | Force traffic through NVA (firewall, router) | Route all internet traffic through firewall |
| **Virtual Network Gateway** | Send traffic to VPN/ExpressRoute gateway | Route on-premises traffic to VPN gateway |
| **Internet** | Allow internet access | Default route 0.0.0.0/0 to internet |
| **Virtual Network** | Route within VNet (rarely used - automatic) | Intra-VNet routing |
| **None** | Drop the traffic | Block specific destinations |

**Practical Example: Hub-and-Spoke with NVA Routing**

```
┌───────────────────────────────────────────────────────────────┐
│              Spoke Subnet (10.1.1.0/24)                       │
│         RT-Spoke Applied                                      │
│                                                               │
│  ┌──────────────────────┐                                    │
│  │ VM1 (10.1.1.5)       │                                    │
│  │ Wants to reach:      │                                    │
│  │ 10.2.0.0/16          │                                    │
│  └────────┬─────────────┘                                    │
│           │ Check RT-Spoke routes for 10.2.0.0/16            │
│           │ Found: Destination 10.2.0.0/16 → NVA 10.1.0.10   │
│           ▼                                                   │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Hub Subnet (10.1.0.0/24)                                │  │
│  │ ┌──────────────────────────────────────────────────┐    │  │
│  │ │ NVA Firewall (10.1.0.10)                         │    │  │
│  │ │ - Inspects traffic                               │    │  │
│  │ │ - Logs connections                               │    │  │
│  │ │ - Allows/denies based on                         │    │  │
│  │ │   security policy                                │    │  │
│  │ └────────────┬──────────────────────────────────────┘    │  │
│  └─────────────┼──────────────────────────────────────────────┘    │
│                │ Routes to 10.2.0.0/16  │
│                ▼                        │
│  ┌──────────────────────────────────────┼──────┐            │
│  │ Peered Spoke2 (10.2.0.0/16)         │      │            │
│  │ - Backend database servers          │      │            │
│  └─────────────────────────────────────┼──────┘            │
│                                        │                    │
└───────────────────────────────────────┼────────────────────┘
```

**Route Table Configuration:**

```plaintext
Route Table: RT-Spoke (associated with Spoke1 subnet 10.1.1.0/24)

┌────────────────────────────────────────────────────────────────┐
│ Destination      │ Name              │ Next Hop Type  │ IP     │
├────────────────────────────────────────────────────────────────┤
│ 10.2.0.0/16      │ ToSpoke2          │ Virtual App.   │10.1.0.10│
│ 192.168.0.0/16   │ ToOnPremises      │ VPN Gateway    │  N/A   │
│ 0.0.0.0/0        │ ToInternet        │ Internet       │  N/A   │
│ 10.1.0.0/16      │ (System Route)    │ Virtual Net.   │  N/A   │
└────────────────────────────────────────────────────────────────┘
```

**Why UDRs Matter:**

- ✅ **Security**: Route traffic through firewall for inspection
- ✅ **Network segmentation**: Enforce communication policies between subnets
- ✅ **Traffic control**: Prioritize or redirect traffic to specific paths
- ✅ **Compliance**: Ensure all traffic meets organizational policies

### 9.2 Effective Routes

**Effective Routes** show the actual routes that apply to a specific network interface (NIC), combining system routes, route tables, and route priorities.

**What Are Effective Routes?**

Effective routes are the **consolidated set of routes** Azure evaluates when determining where to send packets from a NIC. They include:
- System routes (automatically created)
- Custom routes from associated route tables
- Routes from BGP (if using ExpressRoute/VPN)

**Why Check Effective Routes?**

When traffic doesn't reach its destination as expected, examining effective routes helps you:
- ✅ Verify route table is correctly associated
- ✅ Confirm routing priority and matching
- ✅ Diagnose routing conflicts or missing routes
- ✅ Understand route precedence

**How to View Effective Routes:**

**Azure Portal Method:**
```
1. Navigate to VM → Networking → Network Interfaces
2. Select NIC → Support + Troubleshooting → Effective Routes
3. Review routes matching destination CIDR blocks
```

**Azure CLI Method:**
```bash
# Get effective routes for a NIC
az network nic show-effective-route-table \
  --resource-group myResourceGroup \
  --name myNIC \
  --output table
```

**Route Matching and Precedence:**

When evaluating routes, Azure uses **longest prefix match** (most specific route wins):

```
VM tries to send to: 192.168.1.5

Available routes:
┌──────────────────────┬───────────┬─────────────────┐
│ Destination          │ Specificity │ Selected?     │
├──────────────────────┼───────────┼─────────────────┤
│ 192.168.1.0/25       │ /25 (most)│ ✅ SELECTED    │
│ 192.168.1.0/24       │ /24       │ ✗ Ignored      │
│ 192.168.0.0/16       │ /16       │ ✗ Ignored      │
│ 0.0.0.0/0            │ /0 (least)│ ✗ Ignored      │
└──────────────────────┴───────────┴─────────────────┘

Result: Traffic sent via 192.168.1.0/25 route (most specific)
```

**System Routes (Always Present):**

| Destination | Next Hop Type | Purpose |
|-------------|---------------|---------|
| VNet address space (e.g., 10.0.0.0/16) | Virtual Network | Intra-VNet communication |
| Connected VNets (peering) | VNet Peering | Cross-VNet traffic |
| 0.0.0.0/0 | Internet | Default internet route |

`System routes always have lower priority than user-defined routes.`

**Exam Scenario: Diagnosing Routing Issues**

**Question:**

VM1 (IP: 10.0.1.5) in Subnet A is unable to reach VM2 (IP: 10.0.2.10) in Subnet B. Both VMs are in the same VNet. You created a route table RT-Custom and associated it to Subnet A, expecting traffic to route through an NVA (10.0.1.10).

When you check effective routes on VM1's NIC:
```
Destination      Next Hop Type      Next Hop IP
10.0.1.0/24      Virtual Network    -
10.0.2.0/24      Virtual Network    -
0.0.0.0/0        Internet           -
```

Why isn't the route to 10.0.2.0/24 going through the NVA?

**Root Cause:**
The custom route table was not properly associated to Subnet A, so only system routes are active. System routes automatically allow intra-VNet communication, which is why you see "10.0.2.0/24 → Virtual Network."

**Solution:**
```
1. Verify route table association to Subnet A
2. Confirm the custom route rule exists:
   Destination: 10.0.2.0/24, Next Hop: Virtual Appliance 10.0.1.10
3. Check NVA has IP forwarding enabled
4. Verify NSG rules allow traffic to NVA
5. Re-check effective routes
```

### 9.3 Azure Route Server

**Azure Route Server** is a fully managed service that simplifies dynamic routing in your Azure Virtual Network. It acts as a central hub that exchanges routes with **Network Virtual Appliances (NVAs)** and **VPN/ExpressRoute gateways** using **BGP (Border Gateway Protocol)**.

**The Problem Azure Route Server Solves:**

| Scenario | Without Route Server | With Route Server |
|----------|---------------------|--------------------|
| NVA route updates | Manual, static routes | Dynamic BGP exchange |
| High availability | Multiple route updates needed | Automatic failover |
| Multi-site routing | Complex manual configuration | Centralized route management |
| On-premises integration | Static routes per site | Dynamic BGP learning |

**How Azure Route Server Works:**

```
┌──────────────────────────────────────────────────────────────────────┐
│                       Azure Virtual Network                          │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Route Server Subnet (Must be named RouteServerSubnet)       │   │
│  │ Hosts: Azure Route Server service                           │   │
│  │                                                              │   │
│  │ ┌────────────────────────────────────────────────────────┐  │   │
│  │ │         Azure Route Server                            │  │   │
│  │ │    (BGP ASN: 65515, IP: 10.0.254.1)                 │  │   │
│  │ │                                                        │  │   │
│  │ │  BGP ↕ NVA1          BGP ↕ NVA2         BGP ↕ VPN GW │  │   │
│  │ └────────┬──────────────────┬──────────────────┬────────┘  │   │
│  └─────────┼──────────────────┼──────────────────┼──────────┘   │
│            │                  │                  │              │
│            ▼                  ▼                  ▼              │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐│
│  │ NVA1 Firewall    │ │ NVA2 Router      │ │  VPN Gateway    ││
│  │ (BGP enabled)    │ │ (BGP enabled)    │ │ (To On-premises)││
│  └──────────────────┘ └──────────────────┘ └─────────────────┘│
│                                                                  │
│  Routes learned via BGP:                                       │
│  - NVA1 advertises: On-premises routes                         │
│  - NVA2 advertises: Branch office routes                       │
│  - VPN GW advertises: On-premises network CIDR                 │
│  - Route Server publishes learned routes to ALL NICs           │
└──────────────────────────────────────────────────────────────────┘
```

**Key Components:**

| Component | Purpose | Details |
|-----------|---------|---------|
| **Route Server** | Central BGP hub | Managed Azure service, no VM needed |
| **BGP Peering** | Route exchange protocol | NVAs configure BGP to peer with Route Server |
| **NVA Advertising** | NVAs announce learned routes | Firewall shares on-premises routes discovered from VPN |
| **Route Injection** | Routes pushed to VNets | Server publishes routes to all connected subnets |

**Benefits of Azure Route Server:**

- ✅ **Automated Route Distribution**: Routes dynamically shared across resources
- ✅ **Failover Support**: NVA failure detected automatically via BGP down
- ✅ **Reduced Manual Configuration**: No static route updates needed
- ✅ **Multi-NVA Load Balancing**: Multiple NVAs can advertise same routes
- ✅ **On-Premises Routing**: Simplifies hybrid routing scenarios

**Azure Route Server vs Manual UDRs:**

| Aspect | Manual UDRs | Azure Route Server |
|--------|------------|-------------------|
| **Route Updates** | Manual (static) | Automatic (dynamic) |
| **NVA Failover** | Must manually update routes | BGP detects, routes withdrawn |
| **Scalability** | Difficult with many routes | Scales to hundreds of routes |
| **Configuration** | Each subnet needs route table | Central, applies to VNet |
| **Learning Time** | Instant (hardcoded) | BGP convergence (seconds) |
| **Use Case** | Simple, stable topologies | Large, dynamic environments |

**Common Use Cases:**

1. **Multi-NVA High Availability**: Two firewalls advertise routes; if one fails, traffic auto-redirects
2. **Branch Site Aggregation**: Multiple branch offices connect to hub NVA; routes learned dynamically
3. **Hybrid Cloud Routing**: On-premises routes dynamically shared via VPN+BGP
4. **Network Scaling**: Add new internal networks; routes automatically propagate

**Configuration Requirements:**

| Item | Requirement |
|------|-------------|
| **Route Server Subnet** | Must exist and be named exactly: `RouteServerSubnet` |
| **Subnet Size** | Minimum /27 (32 addresses) |
| **NVA BGP** | NVA must support BGP (most enterprise firewalls do) |
| **BGP ASN** | NVA uses different ASN than Route Server (65515) |

**Exam Question: Route Server vs UDR**

**Scenario:**

Your organization has a hub-and-spoke network with multiple branch offices connecting through on-premises routers. The hub NVA discovers new branch networks dynamically from the on-premises network.

Currently, whenever a new branch is added, you manually create UDRs and associate them to all spoke subnets. This is becoming unmanageable.

**Question:** What is the best solution?

**Options:**
- A) Create more detailed UDR rules
- B) Deploy Azure Route Server ✅
- C) Use Azure Firewall instead of NVA
- D) Create separate VNets per branch

**Answer: B) Deploy Azure Route Server**

**Why:**
- Route Server automatically learns routes from NVAs via BGP
- New branch routes automatically propagate to all subnets
- No manual UDR updates required for each new branch
- NVA failure is automatically detected and routes withdrawn

---

## 10. Azure Virtual NAT (NAT Gateway)

**Azure NAT Gateway** is a fully managed, highly resilient service that provides outbound internet connectivity for resources in a virtual network. It simplifies outbound connectivity by providing a dedicated, static public IP address for all outbound connections.

### 10.1 What is Azure NAT Gateway?

**NAT Gateway** enables resources in a private subnet (without public IP addresses) to connect to the internet while remaining unreachable from the internet. It replaces the default outbound connectivity method with a more reliable, scalable, and secure solution.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Azure Virtual Network                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │  Subnet (10.0.1.0/24)                                      │    │
│  │                                                            │    │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                      │    │
│  │  │ VM1 │  │ VM2 │  │ VM3 │  │VMSS │  (No public IPs)     │    │
│  │  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘                      │    │
│  │     │        │        │        │                          │    │
│  │     └────────┴────────┴────────┘                          │    │
│  │                    │                                       │    │
│  │                    ▼                                       │    │
│  │            ┌────────────────┐                             │    │
│  │            │  NAT Gateway   │                             │    │
│  │            │ (Attached to   │                             │    │
│  │            │   subnet)      │                             │    │
│  │            └────────┬───────┘                             │    │
│  └─────────────────────┼─────────────────────────────────────┘    │
│                        │                                           │
│                        ▼                                           │
│              Static Public IP(s)                                   │
│              (20.100.50.10)                                        │
└────────────────────────┼───────────────────────────────────────────┘
                         │
                         ▼
                     Internet
```

**Key Characteristics:**

| Feature | Description |
|---------|-------------|
| **Outbound Only** | Provides outbound internet access, blocks unsolicited inbound |
| **Static IP** | Uses static public IP address(es) for all outbound traffic |
| **High Availability** | Zone-redundant by default, 99.9% SLA |
| **No Management** | Fully managed service, no VMs to maintain |
| **SNAT Port Scale** | Up to 64,000 simultaneous outbound connections per IP |
| **Subnet Association** | Attached to subnet(s), applies to all resources in subnet |
| **One Gateway per Subnet** | A single subnet can only have one NAT gateway attached to it |
| **Up to 16 IP Addresses** | Can use up to 16 public IP addresses (any combination of public IPs and public IP prefixes) |

### 10.2 How NAT Gateway Works

**Outbound Traffic Flow:**

```
1. VM initiates outbound connection (e.g., download updates)
   Source: 10.0.1.4:50000  →  Destination: 1.1.1.1:443

2. Traffic reaches NAT Gateway (attached to subnet)
   NAT Gateway performs SNAT (Source Network Address Translation)

3. Translates private IP to public IP:
   Source: 20.100.50.10:10001  →  Destination: 1.1.1.1:443
   (Mapped: 10.0.1.4:50000 → 20.100.50.10:10001)

4. Internet server responds:
   Source: 1.1.1.1:443  →  Destination: 20.100.50.10:10001

5. NAT Gateway translates back:
   Source: 1.1.1.1:443  →  Destination: 10.0.1.4:50000

6. VM receives response
```

**SNAT Port Allocation:**

Each public IP address assigned to NAT Gateway provides:
- **64,000 SNAT ports** for outbound connections
- **Dynamic allocation** across all resources in the subnet
- **Idle timeout:** 4 minutes by default (configurable)

**Example Calculations:**

```
Scenario: 100 VMs making outbound connections

NAT Gateway with 1 Public IP:
  64,000 ports ÷ 100 VMs = 640 ports per VM average

NAT Gateway with 2 Public IPs:
  128,000 ports ÷ 100 VMs = 1,280 ports per VM average

Recommendation: Use multiple IPs if VMs make many concurrent connections
```

### 10.3 Benefits and Use Cases

**Benefits of NAT Gateway:**

| Benefit | Explanation |
|---------|-------------|
| **Security** | VMs have no public IPs, reducing attack surface |
| **Simplified Management** | Single point for outbound connectivity |
| **Static Outbound IP** | Whitelisting on external firewalls easier |
| **High Availability** | Built-in redundancy, no single point of failure |
| **SNAT Port Exhaustion Prevention** | 64K ports per IP, scales with multiple IPs |
| **Performance** | Low latency, high throughput (up to 10 Gbps) |
| **Cost Effective** | No VM costs, pay only for resource and bandwidth |

**Comparison: Default Outbound vs NAT Gateway vs Public IPs**

| Method | How It Works | Pros | Cons |
|--------|--------------|------|------|
| **Default Outbound** | Azure assigns dynamic public IP | Free, automatic | Unpredictable IP, limited SNAT ports |
| **NAT Gateway** | Dedicated gateway with static IP(s) | Static IP, scalable, HA | Additional cost (~$44/month) |
| **Public IP per VM** | Each VM gets public IP | Direct connectivity | Security risk, management overhead |
| **Load Balancer Outbound Rules** | Use LB for outbound | Works with existing LB | Complex configuration |

**Common Use Cases:**

1. **Software Updates & Package Downloads**
   ```
   VMs without public IPs need to:
   ├─ Download OS patches from Microsoft Update
   ├─ Install packages from public repositories (apt, yum, npm)
   └─ Access third-party APIs
   
   Solution: NAT Gateway provides outbound access
   ```

2. **Firewall Whitelisting**
   ```
   Scenario: External SaaS requires IP whitelisting
   
   Without NAT Gateway:
   ├─ Each VM gets different public IP (dynamic)
   └─ Must whitelist many changing IPs
   
   With NAT Gateway:
   ├─ All VMs use same static public IP(s)
   └─ Whitelist only NAT Gateway IP(s)
   ```

3. **Container & Kubernetes Workloads (AKS)**
   ```
   AKS Cluster with many pods:
   ├─ Pods need outbound internet (pull images, call APIs)
   ├─ Default outbound often hits SNAT port limits
   └─ NAT Gateway provides 64K ports per IP
   
   Result: Eliminates connection failures from port exhaustion
   ```

4. **SNAT Port Exhaustion Prevention**
   ```
   Symptoms:
   ├─ Outbound connections fail intermittently
   ├─ "SNAT port exhaustion" errors in logs
   └─ VMs can't reach external services
   
   Root Cause: Default outbound has limited ports (~1,024 per VM)
   Solution: NAT Gateway with 64,000 ports per IP
   ```

5. **Multi-Tenant Applications**
   ```
   Scenario: SaaS platform serving multiple customers
   
   Each customer tenant:
   ├─ Separate subnet with dedicated NAT Gateway
   ├─ Unique static public IP per tenant
   └─ IP-based access control and audit trails
   ```

### 10.4 Configuration and Best Practices

**Basic Configuration Steps:**

```plaintext
1. Create Public IP Address (or reuse existing):
   → Type: Standard (NOT Basic)
   → SKU: Standard
   → Assignment: Static

2. Create NAT Gateway:
   → Idle timeout: 4-120 minutes (default: 4)
   → Attach public IP address(es)
   → Select availability zones (for redundancy)

3. Associate to Subnet:
   → Virtual network → Subnet → NAT Gateway
   → All resources in subnet now use NAT Gateway for outbound
```

**Azure CLI Example:**

```bash
# Create public IP for NAT Gateway
az network public-ip create \
  --resource-group myResourceGroup \
  --name myNATGatewayIP \
  --sku Standard \
  --allocation-method Static

# Create NAT Gateway
az network nat gateway create \
  --resource-group myResourceGroup \
  --name myNATGateway \
  --public-ip-addresses myNATGatewayIP \
  --idle-timeout 10

# Associate NAT Gateway to subnet
az network vnet subnet update \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --name mySubnet \
  --nat-gateway myNATGateway
```

**Best Practices:**

1. **Capacity Planning**
   ```
   Calculate required SNAT ports:
   
   Ports needed = Number of VMs × Avg connections per VM × 1.2 (buffer)
   
   Example: 50 VMs × 500 connections × 1.2 = 30,000 ports
   Result: 1 Public IP (64,000 ports) is sufficient
   
   If > 64,000 ports needed:
   └─ Add multiple public IP addresses (up to 16 IPs = 1,024,000 ports)
   ```

2. **Idle Timeout Configuration**
   ```
   Default: 4 minutes
   Range: 4-120 minutes
   
   Use Cases:
   ├─ Short timeout (4-10 min): General web traffic, APIs
   ├─ Medium timeout (10-30 min): Database connections, file transfers
   └─ Long timeout (30-120 min): Long-running operations, SSH sessions
   
   Trade-off: Longer timeout = fewer port recycling but more ports held
   ```

3. **High Availability**
   ```
   ✓ NAT Gateway is zone-redundant by default (no extra config)
   ✓ Deploy across availability zones for 99.99% SLA
   ✓ No need for multiple NAT Gateways for HA
   
   Zone Configuration:
   └─ Specify zones: [1, 2, 3] when creating NAT Gateway
   ```

4. **Multiple Subnets**
   ```
   Option 1: Shared NAT Gateway (cost-effective)
   ├─ One NAT Gateway attached to multiple subnets
   └─ All subnets share same outbound IP(s)
   
   Option 2: Dedicated NAT Gateway per subnet
   ├─ Each subnet has its own NAT Gateway
   └─ Different outbound IPs per subnet (isolation)
   
   Use dedicated when:
   └─ Compliance requires IP-based tenant isolation
   └─ Different capacity needs per subnet
   ```

5. **Monitoring**
   ```
   Key Metrics to Monitor:
   ├─ SNAT Connection Count (approaching 64K limit?)
   ├─ Bytes/Packets transmitted (bandwidth usage)
   ├─ Dropped packets (capacity issues)
   └─ Connection count per destination (identify heavy users)
   
   Alerts:
   └─ Alert when SNAT connections > 80% of capacity
   └─ Alert on packet drops > 1%
   ```

**Exam Scenario: NAT Gateway vs Alternatives**

**Question:**

You have an Azure subscription with a virtual network containing 100 VMs in a private subnet (no public IP addresses). The VMs need to:
- Download software updates from the internet
- Access external APIs
- Use a consistent, static IP address for external firewall whitelisting

Currently, VMs are experiencing intermittent connection failures due to SNAT port exhaustion.

**Requirements:**
- ✅ Resolve SNAT port exhaustion
- ✅ Provide static outbound IP
- ✅ Minimize management overhead
- ✅ High availability required

**What should you deploy?**

**Options:**
- A) Assign a public IP address to each VM
- B) Deploy Azure NAT Gateway ✅
- C) Configure Azure Firewall for outbound traffic
- D) Use default outbound connectivity

**Answer: B) Deploy Azure NAT Gateway**

**Why NAT Gateway is Correct:**

| Requirement | How NAT Gateway Addresses It |
|-------------|-----------------------------|
| **SNAT Port Exhaustion** | Provides 64,000 ports per public IP (vs ~1,024 default) |
| **Static Outbound IP** | Uses dedicated static public IP address(es) |
| **Management Overhead** | Fully managed, no VMs to maintain |
| **High Availability** | Built-in zone redundancy, 99.9% SLA |
| **Cost** | ~$44/month + bandwidth (more cost-effective than 100 public IPs) |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **Public IP per VM** | 100 IPs to manage; security risk; doesn't solve SNAT issue; expensive |
| **Azure Firewall** | Overkill for this scenario; higher cost (~$1,200/month); more complex |
| **Default Outbound** | Already failing due to SNAT exhaustion; dynamic IP (not static) |

**Implementation:**

```plaintext
1. Create NAT Gateway with 1-2 static public IPs
2. Associate NAT Gateway to VM subnet
3. All 100 VMs automatically use NAT Gateway for outbound
4. Whitelist NAT Gateway IP(s) on external firewalls
5. Monitor SNAT port usage, add IPs if needed

Result:
  ✅ SNAT port exhaustion resolved (64K-128K ports available)
  ✅ Static outbound IP for whitelisting
  ✅ Fully managed, HA solution
  ✅ VMs remain private (no public IPs)
```

**Cost Comparison:**

```
Option A (Public IPs):
  100 VMs × $3.65/month = $365/month
  + Security risk and management overhead

Option B (NAT Gateway): ✅ BEST
  NAT Gateway: $44/month
  Public IP: $3.65/month
  Total: ~$48/month

Option C (Azure Firewall):
  Firewall: $1,200/month
  Public IP: $3.65/month
  Total: ~$1,204/month

Option D (Default Outbound):
  Free, but SNAT exhaustion = broken functionality
```

**NAT Gateway Limitations:**

| Limitation | Workaround |
|------------|------------|
| **Outbound only** | Use Load Balancer or Application Gateway for inbound |
| **IPv4 only** | Does not support IPv6; cannot be deployed on a subnet with an IPv6 prefix |
| **Max 16 public IPs** | Should support up to ~1M concurrent connections |
| **Not for inbound** | Cannot use NAT Gateway for incoming traffic |
| **One NAT gateway per subnet** | A subnet can only have one NAT gateway; use separate subnets if different outbound IPs needed |
| **Cannot span multiple VNets** | A NAT gateway operates within a single virtual network; use separate NAT gateways per VNet |
| **Compatible with Standard LB** | Works alongside Standard SKU Load Balancer, public IP, and public IP prefix resources |
| **Costs apply** | ~$44/month + bandwidth; evaluate if traffic is minimal |

### 10.5 Practice Question: NAT Gateway IP Addresses and Subnet Association

**Question:**

Here are two statements about NAT (Network Address Translation):

1. A NAT gateway resource can use up to sixteen IP addresses.
2. Only one NAT gateway can be attached to a subnet.

Which of the above statement(s) is correct?

**Options:**
- A) Only 1
- B) Only 2
- C) Both 1 and 2
- D) None of them

**Answer: C) Both 1 and 2**

**Explanation:**

Both statements are correct:

| Statement | Correct? | Details |
|-----------|----------|----------|
| **Statement 1** | ✅ Yes | A NAT gateway resource can use up to **16 IP addresses**. These can be any combination of public IP addresses, public IP prefixes, and public IP addresses & prefixes derived from custom IP prefixes (BYOIP). |
| **Statement 2** | ✅ Yes | A single subnet **cannot** have multiple NAT gateways attached to it. Only one NAT gateway can be associated with a subnet at any time. |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **A) Only 1** | Statement 2 is also correct |
| **B) Only 2** | Statement 1 is also correct |
| **D) None of them** | Both statements are correct |

**Key Takeaways:**

```
NAT Gateway Resource Limits:
├─ Max 16 IP addresses per NAT gateway
│   ├─ Public IP addresses
│   ├─ Public IP prefixes
│   └─ Custom IP prefixes (BYOIP)
│
├─ 1 NAT gateway per subnet (cannot attach multiple)
│
└─ 64,000 SNAT ports per IP address
    └─ Max capacity: 16 IPs × 64,000 = 1,024,000 ports
```

> **Reference**: [Virtual Network NAT - Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/nat-gateway/nat-overview)

### 10.6 Practice Question: NAT Characteristics and Limitations

**Question:**

Please read the following statements regarding Network Address Translation (NAT):

1. NAT allows you to share a single public IPv4 address among multiple internal resources.
2. NAT enables you to assign multiple private IPv4 addresses to a single virtual machine.
3. NAT allows you to configure an external IPv4 address on each virtual machine.
4. NAT cannot be used across multiple virtual networks.

Which of the above statements are true?

**Options:**
- A) Only 1 and 2
- B) Only 1 and 3
- C) Only 3 and 4
- D) Only 1 and 4

**Answer: D) Only 1 and 4**

**Explanation:**

To avoid the need to buy an IPv4 address for each resource that requires internet access, a NAT (Network Address Translation) service can be used. This service maps outgoing requests from internal sources to an external IP address, enabling communication. However, one limitation of NAT is that it cannot span across multiple virtual networks.

| Statement | Correct? | Details |
|-----------|----------|----------|
| **Statement 1** | ✅ Yes | NAT allows sharing a single public IPv4 address among multiple internal resources. This is the core purpose of NAT — it performs SNAT to map multiple private IPs to one (or few) public IPs. |
| **Statement 2** | ❌ No | NAT does not assign multiple private IPv4 addresses to a single VM. Assigning multiple private IPs is a NIC-level feature, not a NAT function. |
| **Statement 3** | ❌ No | NAT does not configure an external IPv4 address on each VM. The whole point of NAT is that VMs remain on private IPs and share an external IP at the gateway level. |
| **Statement 4** | ✅ Yes | A NAT gateway is associated with subnets within a single virtual network. It cannot span across multiple virtual networks. |

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **A) Only 1 and 2** | Statement 2 is incorrect — NAT does not assign multiple private IPs to VMs |
| **B) Only 1 and 3** | Statement 3 is incorrect — NAT does not give each VM an external IP |
| **C) Only 3 and 4** | Statement 3 is incorrect — NAT does not give each VM an external IP |

> **Reference**: [Virtual Network NAT - Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/nat-gateway/nat-overview)

### 10.7 Practice Question: NAT Compatibility and Protocol Support

**Question:**

Virtual Network NAT (Network Address Translation) enables virtual networks to have outbound-only Internet connectivity. Select all applicable statements about NAT.

**Options:**
- A) NAT is compatible with standard SKU public IP and public IP prefixes but not with load balancer resources.
- B) NAT can support both IPv4 and IPv6 addresses regardless of which one you are using.
- C) NAT is capable of supporting only IPv4 protocol and not IPv6.
- D) A network address translation (NAT) can cover several virtual networks at once.
- E) Network Address Translation (NAT) cannot extend across multiple virtual networks.

**Answer: C and E**

**Explanation:**

| Option | Correct? | Details |
|--------|----------|----------|
| **A** | ❌ No | NAT is compatible with standard SKU public IP, public IP prefix, **and** load balancer resources. It works alongside Standard Load Balancer for inbound/outbound scenarios. |
| **B** | ❌ No | NAT only supports the **IPv4** address family. It cannot be deployed on a subnet with an IPv6 prefix. |
| **C** | ✅ Yes | NAT only supports IPv4. IPv6 traffic is not supported by NAT Gateway. |
| **D** | ❌ No | NAT cannot span across multiple virtual networks. A NAT gateway is scoped to a single virtual network. |
| **E** | ✅ Yes | NAT cannot extend across multiple virtual networks. Each VNet requires its own NAT gateway if outbound NAT is needed. |

**Key Takeaways:**

```
NAT Gateway Compatibility & Protocol Support:
├─ Compatible with:
│   ├─ Standard SKU public IP addresses
│   ├─ Public IP prefixes
│   └─ Standard Load Balancer resources
│
├─ Protocol support:
│   ├─ ✅ IPv4 only
│   └─ ❌ IPv6 not supported
│
└─ Scope:
    ├─ Single virtual network only
    └─ Cannot span multiple VNets
```

> **Reference**: [Virtual Network NAT - Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/nat-gateway/nat-overview)

---

**References:**
- [User-Defined Routes - Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview)
- [Effective Routes - Network Troubleshooting](https://learn.microsoft.com/en-us/azure/virtual-network/manage-route-table)
- [Azure Route Server Documentation](https://learn.microsoft.com/en-us/azure/route-server/overview)
- [Network Virtual Appliances](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/dmz/nva-ha)
- [Azure NAT Gateway Documentation](https://learn.microsoft.com/en-us/azure/virtual-network/nat-gateway/nat-overview)
- [Design virtual networks with NAT Gateway](https://learn.microsoft.com/en-us/azure/virtual-network/nat-gateway/nat-gateway-resource)