---
type: Azure Service
title: "Azure Networking Fundamentals - Summary Table"
tags: [networking]
timestamp: 2026-06-14T00:00:00Z
---

# Azure Networking Fundamentals - Summary Table

## 11. Summary Table

| Concept | Key Points |
|---------|------------|
| **VNet** | Isolated network in Azure; region-scoped; contains subnets |
| **Subnet** | Segment of VNet; 5 reserved IPs; can have NSGs and route tables |
| **VNet Peering** | Connect VNets; non-transitive; same or different regions |
| **NSG** | Filter traffic with allow/deny rules; priority-based |
| **VPN Gateway** | Connects networks (S2S) or users (P2S) via encrypted tunnel over internet |
| **ExpressRoute** | Private dedicated connection to Azure; higher bandwidth and reliability than VPN |
| **ExpressRoute Global Reach** | Interconnects on-premises sites via Microsoft backbone; enables multi-site connectivity |
| **BGP (Border Gateway Protocol)** | Dynamic routing protocol for ExpressRoute; enables automatic failover and path optimization |
| **Private Link** | Technology enabling private connectivity to Azure PaaS services |
| **Private Endpoint** | Network interface with private IP to access PaaS services; requires DNS |
| **Service Endpoint** | Optimized route to Azure services; uses public IP; free |
| **Private DNS Zone** | Automatic DNS resolution for private endpoints |
| **Azure Relay** | Cloud rendezvous point enabling outbound-only connections; supports WCF Relays and Hybrid Connections |
| **Hybrid Connections** | Connect App Service to on-premises via Azure Relay; no VPN needed; Windows HCM required |
| **Virtual WAN** | Hub-based global transit network; supports ExpressRoute, S2S VPN, and VNet connections ([see dedicated doc](../10-azure-virtual-wan.md)) |

---

