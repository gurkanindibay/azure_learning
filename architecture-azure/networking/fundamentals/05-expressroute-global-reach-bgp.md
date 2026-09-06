---
type: Azure Service
title: "Azure Networking Fundamentals - ExpressRoute Global Reach and BGP"
description: "**Azure ExpressRoute** provides a private, dedicated connection between your on-premises infrastructure and Azure datacenters. Unlike VPN connections that traverse the public internet, ExpressRoute..."
tags: [networking]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Networking Fundamentals - ExpressRoute Global Reach and BGP

## 6. ExpressRoute, Global Reach, and BGP Routing

### 6.1 Azure ExpressRoute Overview

**Azure ExpressRoute** provides a private, dedicated connection between your on-premises infrastructure and Azure datacenters. Unlike VPN connections that traverse the public internet, ExpressRoute connections offer:

| Feature | ExpressRoute | VPN Gateway |
|---------|--------------|-------------|
| **Connection Type** | Private dedicated | Public internet (encrypted) |
| **Bandwidth** | Up to 100 Gbps | Up to 10 Gbps |
| **Latency** | Lower, predictable | Variable |
| **Reliability** | Higher (SLA 99.95%) | Standard |
| **Use Case** | Enterprise, mission-critical | General purpose |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ExpressRoute Architecture                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  On-Premises           ExpressRoute              Azure                       │
│  Data Center           Provider Edge             Region                      │
│  ┌──────────┐         ┌──────────────┐         ┌──────────────┐            │
│  │  Router  │─────────│  Meet-me     │─────────│  Microsoft   │            │
│  │  (BGP)   │ Private │  Location    │ Private │  Enterprise  │            │
│  └──────────┘  Link   │  (Exchange)  │  Link   │  Edge        │            │
│       │               └──────────────┘         └──────────────┘            │
│       │                                               │                     │
│  ┌────▼─────┐                                   ┌─────▼──────┐             │
│  │ Corporate│                                   │ Azure VNet │             │
│  │ Network  │                                   │            │             │
│  └──────────┘                                   └────────────┘             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 ExpressRoute Global Reach

**ExpressRoute Global Reach** enables you to interconnect your on-premises networks through the Microsoft global network. This allows:

- Direct communication between different on-premises sites via Microsoft backbone
- Connectivity between Azure regions and multiple on-premises locations
- Global network transit without traversing the public internet

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ExpressRoute Global Reach                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  On-Premises                Microsoft                  On-Premises           │
│  Site A                     Global Network             Site B                │
│  (New York)                                            (Los Angeles)         │
│  ┌──────────┐             ┌──────────────┐            ┌──────────┐          │
│  │  Router  │─────────────│              │────────────│  Router  │          │
│  │  (BGP)   │ ExpressRoute│   Microsoft  │ExpressRoute│  (BGP)   │          │
│  └──────────┘   Circuit 1 │   Backbone   │  Circuit 2 └──────────┘          │
│                           │              │                                   │
│                           │      │       │                                   │
│                           └──────┼───────┘                                   │
│                                  │                                           │
│                    ┌─────────────┼─────────────┐                            │
│                    │             │             │                            │
│                    ▼             ▼             ▼                            │
│              ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│              │ East US  │ │ West US  │ │ Other    │                        │
│              │ VNet     │ │ VNet     │ │ Regions  │                        │
│              └──────────┘ └──────────┘ └──────────┘                        │
│                                                                              │
│  Global Reach enables Site A ←→ Site B communication via Microsoft network │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Benefits of Global Reach:**
- Private connectivity between geographically dispersed sites
- Lower latency compared to internet-based VPN connections between sites
- Leverages Microsoft's global backbone infrastructure
- Simplified network topology for multi-site organizations

### 6.3 Border Gateway Protocol (BGP) with ExpressRoute

**Border Gateway Protocol (BGP)** is the dynamic routing protocol used with ExpressRoute to exchange routes between your on-premises network and Azure. BGP is essential for:

- **Dynamic Route Advertisement**: Automatically propagate routes between on-premises and Azure
- **Automatic Failover**: Detect failures and reroute traffic without manual intervention
- **Path Optimization**: Select the best path based on route metrics and policies

| BGP Concept | Description |
|-------------|-------------|
| **AS Number (ASN)** | Unique identifier for your network; Azure uses ASN 12076 for public peering |
| **BGP Peering** | Establishing neighbor relationships between routers |
| **Route Advertisement** | Announcing network prefixes to peers |
| **AS-Path** | List of AS numbers a route has traversed |
| **Route Weights** | Local preference values for path selection |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BGP Route Exchange with ExpressRoute                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  On-Premises Router                         Azure (Microsoft Edge)           │
│  ASN: 65001                                 ASN: 12076                       │
│  ┌─────────────────┐                       ┌─────────────────┐              │
│  │                 │   BGP Session         │                 │              │
│  │  Advertises:    │◄─────────────────────►│  Advertises:    │              │
│  │  10.0.0.0/8     │   Route Exchange      │  Azure VNet     │              │
│  │  172.16.0.0/16  │                       │  prefixes       │              │
│  │                 │                       │                 │              │
│  └─────────────────┘                       └─────────────────┘              │
│                                                                              │
│  Result: Both sides learn each other's routes dynamically                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 BGP Route Optimization and Failover

BGP provides powerful mechanisms for optimizing traffic paths and ensuring automatic failover:

**AS-Path Prepending:**
- Makes a route appear longer (less preferred) by adding extra AS numbers
- Used to prefer one path over another for outbound traffic

**Route Weights/Local Preference:**
- Higher weight = more preferred path
- Configured locally on routers to influence path selection

**Multi-Exit Discriminator (MED):**
- Suggests to external peers which entry point to use
- Lower MED = more preferred

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BGP Failover Mechanism                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Normal Operation:                                                           │
│  ┌──────────┐         Primary Path (Preferred)      ┌──────────┐           │
│  │  Azure   │═══════════════════════════════════════│  Site A  │           │
│  │  VNet    │───────────────────────────────────────│ (Primary)│           │
│  │          │         Backup Path (AS-Path longer)  └──────────┘           │
│  │          │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┌──────────┐           │
│  └──────────┘                                       │  Site B  │           │
│                                                     │ (Backup) │           │
│  Failover (Site A fails):                           └──────────┘           │
│  ┌──────────┐                                       ┌──────────┐           │
│  │  Azure   │         Primary Path DOWN             │  Site A  │           │
│  │  VNet    │═══════════════════════════════════════│   (X)    │           │
│  │          │         Backup becomes Active         └──────────┘           │
│  │          │═══════════════════════════════════════┌──────────┐           │
│  └──────────┘                                       │  Site B  │           │
│                                                     │ (Active) │           │
│                                                     └──────────┘           │
│  BGP automatically detects failure and reroutes traffic (no manual action) │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.5 Routing Configuration Comparison

When configuring routing between Azure virtual networks and on-premises locations, you have three main options:

| Routing Method | Type | Dynamic Failover | Path Optimization | Use Case |
|----------------|------|------------------|-------------------|----------|
| **BGP** | Dynamic | ✅ Yes | ✅ AS-path, weights | ExpressRoute, multi-site, automatic failover |
| **User-Defined Routes (UDR)** | Static | ❌ No | ❌ Manual | Specific routing overrides, NVAs |
| **Azure Default Routes** | Automatic | ❌ No | ❌ N/A | Basic connectivity, no customization |

**Why BGP is Required for ExpressRoute:**

- ExpressRoute uses BGP as the routing protocol between on-premises and Azure
- BGP enables dynamic route propagation—routes are learned automatically
- Supports automatic failover when a site or circuit becomes unavailable
- Allows path preference configuration (prefer one path over another)

**Why User-Defined Routes Are Not Suitable for This Scenario:**

- UDRs are static—they don't respond to network changes
- Manual intervention required to update routes during failures
- Cannot dynamically prefer one path over another
- Not designed for multi-site failover scenarios

**Why Azure Default Routes Are Not Suitable:**

- Provide basic routing without customization
- Don't support intelligent failover
- Don't allow path preference configuration

### 6.6 Multi-Site Failover Scenario

**Scenario: Enterprise with Two On-Premises Sites and Two Azure Regions**

**Requirements:**
- On-premises sites: New York and Los Angeles
- Azure virtual networks: East US and West US regions
- Each on-premises site has ExpressRoute Global Reach circuits to both Azure regions
- Outbound traffic to the internet from Azure workloads must route through the closest on-premises site
- If an on-premises site fails, traffic must automatically reroute to the other site

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              Multi-Site ExpressRoute Global Reach Architecture               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                        Microsoft Global Network                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │   ┌──────────────┐                          ┌──────────────┐        │   │
│  │   │  East US     │◄────────────────────────►│  West US     │        │   │
│  │   │  VNet        │    Azure Backbone         │  VNet        │        │   │
│  │   │              │                          │              │        │   │
│  │   └──────┬───────┘                          └───────┬──────┘        │   │
│  │          │                                          │               │   │
│  │          │ ExpressRoute                  ExpressRoute│               │   │
│  │          │ (BGP routing)               (BGP routing) │               │   │
│  │          │                                          │               │   │
│  └──────────┼──────────────────────────────────────────┼───────────────┘   │
│             │                                          │                    │
│             │         Global Reach Link                │                    │
│             │◄────────────────────────────────────────►│                    │
│             │                                          │                    │
│  ┌──────────▼───────┐                        ┌─────────▼────────┐          │
│  │  New York Site   │                        │ Los Angeles Site │          │
│  │  (On-Premises)   │                        │ (On-Premises)    │          │
│  │                  │                        │                  │          │
│  │  ┌────────────┐  │                        │  ┌────────────┐  │          │
│  │  │ Internet   │  │                        │  │ Internet   │  │          │
│  │  │ Breakout   │  │                        │  │ Breakout   │  │          │
│  │  └────────────┘  │                        │  └────────────┘  │          │
│  └──────────────────┘                        └──────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     BGP Configuration for This Scenario                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Path Preference (using AS-Path prepending or BGP weights):                 │
│                                                                              │
│  From East US VNet:                                                         │
│    • Primary path: New York site (shorter AS-path / higher weight)          │
│    • Backup path: Los Angeles site (longer AS-path / lower weight)          │
│                                                                              │
│  From West US VNet:                                                         │
│    • Primary path: Los Angeles site (shorter AS-path / higher weight)       │
│    • Backup path: New York site (longer AS-path / lower weight)             │
│                                                                              │
│  Failover Behavior:                                                         │
│    • If New York site fails → BGP withdraws routes                          │
│    • East US VNet traffic automatically reroutes to Los Angeles             │
│    • No manual intervention required                                        │
│    • When New York recovers → BGP re-advertises routes                      │
│    • Traffic automatically returns to preferred path                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Solution: Use BGP for Routing Configuration**

BGP is the correct choice because:

1. **Dynamic Routing**: BGP automatically propagates routing changes between on-premises and Azure
2. **Automatic Failover**: When a site fails, BGP detects the failure and reroutes traffic without manual intervention
3. **Path Optimization**: AS-path prepending and route weights allow preferring the closest on-premises site
4. **ExpressRoute Integration**: BGP is the native routing protocol for ExpressRoute connections

### 6.7 BGP vs HSRP vs VRRP for Azure Failover

When implementing automatic failover for Azure ExpressRoute connections, it's important to understand why BGP is the only viable option compared to other redundancy protocols:

| Protocol | Type | Scope | Azure ExpressRoute Support | Use Case |
|----------|------|-------|---------------------------|----------|
| **BGP (Border Gateway Protocol)** | Dynamic routing protocol | WAN / Internet | ✅ Supported and required | Cloud-to-on-premises routing, multi-site failover |
| **HSRP (Hot Standby Routing Protocol)** | Gateway redundancy | LAN (Cisco proprietary) | ❌ Not supported | Local network gateway redundancy |
| **VRRP (Virtual Router Redundancy Protocol)** | Gateway redundancy | LAN (Open standard) | ❌ Not supported | Local network gateway redundancy |

**Why BGP is Required for ExpressRoute Automatic Failover:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BGP vs HSRP/VRRP Comparison                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  BGP (Border Gateway Protocol):                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Operates at WAN/Internet level (Layer 3 routing protocol)           │ │
│  │ • Exchanges routing information between autonomous systems            │ │
│  │ • Supports route advertisement withdrawal on failure                  │ │
│  │ • Enables path selection based on AS-path, local preference, MED      │ │
│  │ • Native protocol for Azure ExpressRoute                              │ │
│  │ • Handles cloud-to-on-premises routing dynamically                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  HSRP (Hot Standby Routing Protocol):                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Cisco proprietary protocol                                          │ │
│  │ • Designed for LAN gateway redundancy only                            │ │
│  │ • Provides virtual IP for default gateway failover                    │ │
│  │ • NOT supported by Azure ExpressRoute or Global Reach                 │ │
│  │ • Cannot handle WAN-level or cloud routing failover                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  VRRP (Virtual Router Redundancy Protocol):                                 │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ • Open standard (RFC 5798)                                            │ │
│  │ • Similar to HSRP - designed for LAN gateway redundancy               │ │
│  │ • Provides virtual IP for default gateway failover                    │ │
│  │ • NOT supported by Azure ExpressRoute or Global Reach                 │ │
│  │ • Cannot handle WAN-level or cloud routing failover                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Differences:**

| Aspect | BGP | HSRP/VRRP |
|--------|-----|-----------|
| **Protocol Scope** | WAN / Inter-AS routing | LAN gateway redundancy |
| **Route Exchange** | Full routing table exchange between peers | Virtual IP failover only |
| **Failover Mechanism** | Route withdrawal and re-advertisement | Master/backup election |
| **Path Selection** | Multiple metrics (AS-path, weight, MED, local preference) | Priority-based election |
| **Azure Integration** | Native ExpressRoute protocol | Not applicable |
| **Multi-Site Support** | Yes - routes traffic across geographic locations | No - local network only |

**Automatic Failover with BGP:**

When an on-premises site fails in an ExpressRoute Global Reach configuration:

1. **Detection**: BGP peers detect the failure (via keepalive timeout or BFD)
2. **Route Withdrawal**: The failed site's routes are withdrawn from the BGP routing table
3. **Convergence**: BGP recalculates the best path using remaining available routes
4. **Rerouting**: Traffic automatically shifts to the backup path (alternate on-premises site)
5. **Recovery**: When the failed site recovers, BGP re-advertises routes and traffic returns to the preferred path

This entire process happens automatically without any manual intervention, which is why BGP is the correct answer for handling automatic routing configuration following a failover in ExpressRoute scenarios.

**References:**
- [Border Gateway Protocol (BGP)](https://learn.microsoft.com/en-us/windows-server/remote/remote-access/bgp/border-gateway-protocol-bgp)
- [ExpressRoute Global Reach](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-global-reach)
- [ExpressRoute Routing](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-routing)
- [Virtual Network UDR Overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-udr-overview)

---

