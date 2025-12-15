# Azure Virtual WAN

## Table of Contents

- [1. Overview](#1-overview)
- [2. Key Components](#2-key-components)
- [3. Virtual WAN Hub Planning](#3-virtual-wan-hub-planning)
- [4. ExpressRoute and Global Reach](#4-expressroute-and-global-reach)
- [5. Cost Optimization Considerations](#5-cost-optimization-considerations)

---

## 1. Overview

**Azure Virtual WAN** is a networking service that provides optimized and automated branch connectivity to, and through, Azure. It brings together many Azure networking services, such as VPN, ExpressRoute, and Azure Firewall, into a single operational interface.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AZURE VIRTUAL WAN ARCHITECTURE                         │
│                                                                                  │
│                           ┌─────────────────────┐                               │
│                           │   Azure Virtual WAN  │                               │
│                           │    (Orchestration)   │                               │
│                           └──────────┬──────────┘                               │
│                                      │                                          │
│          ┌───────────────────────────┼───────────────────────────┐             │
│          │                           │                           │              │
│          ▼                           ▼                           ▼              │
│   ┌─────────────┐             ┌─────────────┐             ┌─────────────┐       │
│   │  Hub 1      │             │  Hub 2      │             │  Hub 3      │       │
│   │ (East US)   │◄───────────►│(North Europe)│◄───────────►│(Southeast  │       │
│   │             │             │             │             │   Asia)    │       │
│   └──────┬──────┘             └──────┬──────┘             └──────┬──────┘       │
│          │                           │                           │              │
│   ┌──────┴──────┐             ┌──────┴──────┐             ┌──────┴──────┐       │
│   │ ExpressRoute│             │ ExpressRoute│             │ ExpressRoute│       │
│   │ VPN Gateway │             │ VPN Gateway │             │ VPN Gateway │       │
│   │ VNet Conns  │             │ VNet Conns  │             │ VNet Conns  │       │
│   └──────┬──────┘             └──────┬──────┘             └──────┴──────┘       │
│          │                           │                           │              │
│          ▼                           ▼                           ▼              │
│   New York Office            Paris Office               Sydney Office           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- Unified management of VPN, ExpressRoute, and Azure Firewall
- Automated hub-to-hub full mesh connectivity
- Global transit network architecture
- Integration with Azure Monitor for network insights

---

## 2. Key Components

| Component | Description |
|-----------|-------------|
| **Virtual WAN** | Parent resource that contains all hubs and connections |
| **Hub** | Regional network hub with VPN, ExpressRoute, and VNet connections |
| **Hub VPN Gateway** | Provides Site-to-Site VPN connectivity within a hub |
| **ExpressRoute Gateway** | Enables ExpressRoute circuit connectivity |
| **VNet Connection** | Connects spoke VNets to the hub |
| **Hub-to-Hub Connection** | Automatic full mesh connectivity between hubs |

**Virtual WAN Types:**

| Type | Features | Use Case |
|------|----------|----------|
| **Basic** | Site-to-Site VPN only | Simple branch connectivity |
| **Standard** | ExpressRoute, User VPN, VNet connections, Hub-to-hub transit | Enterprise global transit network |

---

## 3. Virtual WAN Hub Planning

When planning Virtual WAN hubs, you need to consider:

1. **One Hub Per Region**: Each Azure region where you need connectivity requires its own hub
2. **ExpressRoute Circuits**: Each hub can connect to ExpressRoute circuits in that region
3. **Latency Requirements**: Place hubs close to your offices for optimal performance
4. **Cost Optimization**: Each hub incurs charges; minimize hubs while meeting requirements

### 📝 Exam Scenario: Global Office Connectivity

**Scenario:**
A company has offices in New York City, Sydney, Paris, and Johannesburg. They have an Azure subscription and plan to deploy a networking solution that:
- Connects to ExpressRoute circuits in East US, Southeast Asia, North Europe, and South Africa
- Minimizes latency by supporting connection in three regions
- Supports Site-to-Site VPN connections
- Minimizes costs

**Question:** What is the minimum number of Azure Virtual WAN hubs required?

**Answer: 3 hubs**

**Explanation:**

Azure Virtual WAN requires deploying at least one hub per region to support ExpressRoute connectivity while minimizing latency. Given the requirements:

| Requirement | Analysis |
|-------------|----------|
| Connect to 4 ExpressRoute regions | Need hubs strategically placed to connect circuits |
| Minimize latency in 3 regions | Need 3 hubs minimum |
| Support S2S VPN | Standard Virtual WAN with VPN capability |
| Minimize costs | Use only 3 hubs instead of 4 |

**Strategic Hub Placement (Example):**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    OPTIMAL 3-HUB DEPLOYMENT                                      │
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│   │   Hub 1         │    │   Hub 2         │    │   Hub 3         │            │
│   │   East US       │◄──►│   North Europe  │◄──►│   Southeast Asia│            │
│   │                 │    │   or            │    │                 │            │
│   │                 │    │   South Africa  │    │                 │            │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘            │
│            │                      │                      │                      │
│            ▼                      ▼                      ▼                      │
│    ┌───────────────┐     ┌───────────────┐      ┌───────────────┐              │
│    │ ExpressRoute  │     │ ExpressRoute  │      │ ExpressRoute  │              │
│    │ Circuit       │     │ Circuit       │      │ Circuit       │              │
│    │ (East US)     │     │ (N.Europe or  │      │ (SE Asia)     │              │
│    │               │     │  S.Africa)    │      │               │              │
│    └───────────────┘     └───────────────┘      └───────────────┘              │
│            │                      │                      │                      │
│            ▼                      ▼                      ▼                      │
│    New York Office        Paris or              Sydney Office                   │
│                          Johannesburg                                           │
│                          Office                                                 │
│                                                                                  │
│   Note: The 4th ExpressRoute circuit can connect via ExpressRoute Global       │
│         Reach or through an adjacent hub with some additional latency.          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Why not 4 hubs?**
- The requirement explicitly states "minimize costs"
- The requirement asks for connectivity "in three regions" specifically
- Using only 3 hubs saves on hub charges while still providing connectivity to all 4 ExpressRoute circuits

**Why not 2 hubs?**
- Would not meet the requirement of "supporting connection in three regions"
- Would result in higher latency for offices further from hubs

---

## 4. ExpressRoute and Global Reach

**ExpressRoute Global Reach** can extend connectivity between ExpressRoute circuits without going through Virtual WAN hubs:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    EXPRESSROUTE GLOBAL REACH                                     │
│                                                                                  │
│   On-Premises Site 1                      On-Premises Site 2                    │
│   (New York)                              (Paris)                               │
│        │                                       │                                │
│        ▼                                       ▼                                │
│   ┌───────────────┐                      ┌───────────────┐                      │
│   │ ExpressRoute  │◄─────────────────────►│ ExpressRoute  │                      │
│   │ Circuit       │    Global Reach       │ Circuit       │                      │
│   │ (East US)     │  (Microsoft Backbone) │ (North Europe)│                      │
│   └───────────────┘                      └───────────────┘                      │
│                                                                                  │
│   Direct site-to-site connectivity without traversing Virtual WAN               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**When to Use ExpressRoute Global Reach:**
- Direct branch-to-branch communication without hub traversal
- Reducing latency for site-to-site traffic
- Complementing Virtual WAN for specific traffic patterns

---

## 5. Cost Optimization Considerations

| Factor | Impact on Cost |
|--------|----------------|
| **Number of Hubs** | Each hub incurs hourly charges |
| **Hub Scale Units** | Higher scale = higher cost but more throughput |
| **VPN Connections** | Per connection charges for Site-to-Site |
| **ExpressRoute** | Separate ExpressRoute circuit and port charges |
| **Data Transfer** | Egress charges for data leaving Azure |

**Cost Optimization Tips:**
1. Deploy hubs only in regions where you need low-latency connectivity
2. Use ExpressRoute Global Reach for site-to-site traffic when possible
3. Right-size hub scale units based on actual throughput needs
4. Consider hub placement that can serve multiple nearby offices

---

## Related Resources

- [Azure Virtual WAN Overview](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-about)
- [Virtual WAN FAQ](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-faq)
- [ExpressRoute Global Reach](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-global-reach)
- [Virtual WAN Global Transit Network Architecture](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-global-transit-network-architecture)
- [Azure Networking Fundamentals](./azure-networking-fundamentals.md)
