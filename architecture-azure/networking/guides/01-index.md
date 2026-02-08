# Azure Networking Fundamentals - Index

*This is a modular documentation structure. Detailed content has been split into focused guides.*

## Quick Navigation

📋 **[VNet & Subnet Fundamentals](./02-vnet-fundamentals.md)** - Core VNet concepts, subnets, addressing, peering, NSGs, and routing

🔗 **[Private Endpoints & Service Endpoints](./03-private-endpoints-guide.md)** - Private connectivity to Azure PaaS services

🔐 **[VPN vs Private Link](./04-vpn-private-link-guide.md)** - Understanding VPN gateways and when to use each technology

🌐 **[ExpressRoute & BGP Routing](./05-expressroute-bgp-guide.md)** - Private dedicated connections and dynamic routing

🔄 **[Azure Relay & Hybrid Connections](./06-relay-hybrid-connections-guide.md)** - Connecting on-premises to Azure without VPN

📚 **[Common Networking Scenarios](./07-scenarios.md)** - Practical examples and architecture patterns

✅ **[Best Practices](./08-best-practices.md)** - Design guidelines and recommendations

---

## Overview

Azure networking services provide the foundation for connecting and securing Azure resources. Understanding Virtual Networks (VNets) and Private Endpoints is essential because many Azure services reference these concepts for secure connectivity.

### Key Networking Concepts

- **Virtual Networks (VNets)**: Isolated network environments in Azure
- **Private Endpoints**: Private IP connections to Azure PaaS services
- **Service Endpoints**: Optimized routing to Azure services
- **Network Security Groups**: Traffic filtering rules
- **VPN Gateway**: Encrypted connections between networks
- **ExpressRoute**: Private dedicated connections to Azure
- **Azure Relay**: Cloud-based rendezvous for outbound-only connectivity

---

## Technology Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│                  What are you trying to connect?                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  On-premises network to Azure VNet                              │
│  └─▶ [VPN Gateway (S2S)](./04-vpn-private-link-guide.md)        │
│      [ExpressRoute](./05-expressroute-bgp-guide.md)             │
│                                                                  │
│  Individual users to Azure VNet                                 │
│  └─▶ [VPN Gateway (P2S)](./04-vpn-private-link-guide.md)        │
│                                                                  │
│  Azure VNet to Azure PaaS service                               │
│  └─▶ [Private Endpoint](./03-private-endpoints-guide.md)        │
│                                                                  │
│  On-premises to Azure PaaS service                              │
│  └─▶ [VPN + Private Endpoint](./04-vpn-private-link-guide.md)   │
│                                                                  │
│  Two Azure VNets together                                       │
│  └─▶ [VNet Peering](./02-vnet-fundamentals.md)                  │
│                                                                  │
│  Azure resource to on-premises service (no firewall changes)    │
│  └─▶ [Hybrid Connections](./06-relay-hybrid-connections-guide.md)│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Guide Structures

### VNet Fundamentals
- VNet basics and on-premises equivalents
- Subnets and address space planning
- VNet peering (regional and global)
- Gateway transit configuration
- Network Security Groups and Application Security Groups
- Network Interfaces and multiple NICs
- User-Defined Routes and Effective Routes
- Azure Route Server

### Private Endpoints & Service Endpoints
- Private endpoints for PaaS services
- Private Link Service for cross-tenant exposure
- DNS configuration and hybrid scenarios
- Service endpoints and optimization
- When to use each technology

### VPN vs Private Link
- Understanding the fundamental difference
- VPN Gateway types (S2S, P2S, VNet-to-VNet)
- Private Link architecture
- When to use VPN vs Private Link
- Combining both for hybrid architectures

### ExpressRoute & BGP
- ExpressRoute overview and benefits
- ExpressRoute Global Reach
- Border Gateway Protocol (BGP) routing
- Multi-site failover scenarios
- BGP vs traditional routing protocols

### Relay & Hybrid Connections
- Azure Relay overview
- WCF Relays vs Hybrid Connections
- Hybrid Connection Manager
- Connecting App Service to on-premises resources
- When to use Relay vs VPN vs Private Link

### Scenarios & Best Practices
- Securing Azure Storage with Private Endpoints
- App Service to SQL Database private connectivity
- Hub-spoke network architecture
- IP addressing and on-premises integration
- Network architecture guidelines

---

## Common Exam Questions by Topic

### VNet & Subnets
- How many subnets are required for App Service + SQL Database private connectivity?
- What address space conflict causes routing failures?
- When do resources in different subnets communicate automatically?

### Endpoints & Links
- What's the difference between Private Endpoints and Service Endpoints?
- Which solution allows cross-tenant PaaS exposure?
- How do private endpoints for on-premises clients work?

### Routing & Security
- What's the difference between UDRs and Effective Routes?
- When should you use Azure Route Server instead of manual UDRs?
- How do service tags simplify NSG rules?

### Connectivity
- VPN vs Private Link: main differences and use cases
- When to use each: VPN, ExpressRoute, Private Link, Relay
- What enables spoke VNets to use hub VNet's gateway?

### Hybrid Scenarios
- How does Hybrid Connections enable App Service ↔ on-premises access?
- What's the difference between Relay WCF and Hybrid Connections?
- Which requires a VPN, which doesn't?

---

## Key Definitions

| Term | Quick Definition |
|------|------------------|
| **VNet** | Logically isolated network in Azure; logical equivalent of corporate LAN |
| **Subnet** | Segment of VNet; 5 reserved IPs; can have NSGs |
| **VNet Peering** | Direct connection between VNets; non-transitive; works across regions |
| **NSG** | Firewall rules; allow/deny traffic by IP, port, protocol |
| **UDR** | User-defined route; override default routing to force traffic through NVA |
| **Service Tag** | Azure-managed group of IP addresses for a specific service |
| **ASG** | Application Security Group; group VMs by role for NSG rules |
| **NIC** | Network Interface Card; connects VM to VNet; can have public + private IPs |
| **BGP** | Border Gateway Protocol; dynamic routing for ExpressRoute |
| **Gateway Transit** | VNet peering config allowing spokes to use hub's gateway |
| **Private Endpoint** | NIC with private IP for secure access to PaaS services |
| **Service Endpoint** | Optimized route to Azure service; uses service's public IP |
| **VPN** | Encrypted tunnel over internet; connects networks or users |
| **ExpressRoute** | Private dedicated connection to Azure; higher bandwidth + reliability |
| **Private Link** | Technology for private PaaS access via private endpoints |
| **Azure Relay** | Cloud rendezvous for outbound-only connections |
| **Hybrid Connections** | App Service feature using Azure Relay for on-prem access |

---

## Summary Comparison Table

| Technology | Purpose | Who Connects | Traffic Path | Cost | Latency |
|-----------|---------|--------|---|---|----|
| **VNet Peering** | Connect VNets | VNet ↔ VNet | Azure backbone | Per GB | Very Low |
| **VPN Gateway** | Network tunnel | On-prem ↔ Azure, User ↔ Azure | Encrypted internet | Hourly + GB | Medium |
| **ExpressRoute** | Dedicated connection | On-prem ↔ Azure | Private dedicated link | Port + data | Low |
| **Private Endpoint** | PaaS access | VNet/On-prem ↔ PaaS | Private Link backbone | Hourly + processed | Low |
| **Service Endpoint** | PaaS optimization | VNet ↔ PaaS | Azure backbone (public IP) | Free | Low |
| **Azure Relay** | Outbound only | On-prem ↔ Azure (via relay) | Outbound HTTPS/WebSocket | Per listener/hour | Medium |
| **Hybrid Connection** | App Service integration | App Service ↔ On-prem | Outbound via relay | Included in plan | Medium |
| **Azure Firewall** | Network security | East-West + egress | Centralized | Hourly + processed | Low-Medium |

---

## Getting Started

**New to Azure networking?** Start here:
1. Read "[VNet Fundamentals](./02-vnet-fundamentals.md)" to understand core concepts
2. Learn about "[Private Endpoints](./03-private-endpoints-guide.md)" for secure PaaS access
3. Review "[Common Scenarios](./07-scenarios.md)" for practical examples

**Preparing for exams?** Use this structure:
1. Understand the decision matrix above
2. Study each guide for your specific topic area
3. Practice "when to use" scenarios
4. Review exam questions at the end of each guide

**Designing architectures?** Follow these steps:
1. Map out what needs to connect to what
2. Use the decision tree above
3. Read relevant guides for detailed architecture
4. Check "[Best Practices](./08-best-practices.md)"

---

## Related Azure Services

- [Azure Virtual WAN](../azure-virtual-wan.md) - Hub-based global transit network
- [Azure Network Watcher](../azure-network-watcher.md) - Network monitoring and troubleshooting
- [Azure Firewall](../azure-firewall.md) - Managed network security
- [Azure DDoS Protection](../azure-ddos-protection.md) - DDoS mitigation

---

## Microsoft Learn References

- [Azure Virtual Network Documentation](https://docs.microsoft.com/azure/virtual-network/)
- [Azure VPN Gateway Documentation](https://docs.microsoft.com/azure/vpn-gateway/)
- [Azure ExpressRoute Documentation](https://docs.microsoft.com/azure/expressroute/)
- [Azure Private Link Documentation](https://docs.microsoft.com/azure/private-link/)
- [Azure Relay Documentation](https://docs.microsoft.com/azure/azure-relay/)
- [Network Security Groups](https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview)
- [VNet Peering](https://docs.microsoft.com/azure/virtual-network/virtual-network-peering-overview)
- [Azure Networking Best Practices](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/perimeter-networks)

---

## Note

This documentation has been split from a single large file into focused guides for better maintainability. All original content and examples are preserved in the specialized guides linked above.

Last Updated: 2026-02-08
