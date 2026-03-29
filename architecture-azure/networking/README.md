# Azure Networking

> **Taxonomy Reference**: §5 Cloud & Infrastructure / Platform Architecture (see [architecture_taxonomy_reference.md](../../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md))

## Learning Path

Follow the numbered guides in order, or jump to a specific topic.

### Core Concepts

| # | Topic | Description |
|---|-------|-------------|
| 01 | [Networking Fundamentals](01-networking-fundamentals.md) | VNets, subnets, NSGs, peering, private endpoints, service endpoints |
| 02 | [VNet Fundamentals](02-vnet-fundamentals.md) | Address spaces, peering, ASGs, NICs, UDRs, Route Server |
| 03 | [Private Endpoints Guide](03-private-endpoints-guide.md) | Private connectivity to Azure PaaS, DNS config, hybrid scenarios |

### Connectivity

| # | Topic | Description |
|---|-------|-------------|
| 04 | [Azure DNS](04-azure-dns.md) | Public/private DNS zones, delegation, hybrid DNS |
| 05 | [Azure VPN Gateway](05-azure-vpn-gateway.md) | S2S, P2S, VNet-to-VNet VPN, SKUs, protocols |
| 06 | [VPN vs Private Link](06-vpn-private-link-guide.md) | Decision guide: when to use VPN vs Private Link |
| 07 | [ExpressRoute & BGP](07-expressroute-bgp-guide.md) | Dedicated connections, peering types, dynamic routing |
| 08 | [ExpressRoute Connectivity Models](08-expressroute-connectivity-models.md) | CloudExchange, point-to-point, IPVPN, ExpressRoute Direct |
| 09 | [Relay & Hybrid Connections](09-relay-hybrid-connections-guide.md) | Azure Relay, Hybrid Connections, firewall-free connectivity |

### WAN & Global Transit

| # | Topic | Description |
|---|-------|-------------|
| 10 | [Azure Virtual WAN](10-azure-virtual-wan.md) | Hub components, routing, ExpressRoute Global Reach, NVAs |
| 11 | [When to Use Virtual WAN](11-when-to-use-virtual-wan.md) | Decision guide: vWAN vs traditional hub-spoke |

### Network Security

| # | Topic | Description |
|---|-------|-------------|
| 12 | [Security Services Comparison](12-network-security-services-comparison.md) | NSG vs ASG vs Firewall vs WAF vs Private Link |
| 13 | [Azure Firewall](13-azure-firewall-overview.md) | Policy hierarchy, rule processing, FQDN filtering |

### Monitoring

| # | Topic | Description |
|---|-------|-------------|
| 14 | [Azure Network Watcher](14-azure-network-watcher.md) | IP Flow Verify, packet capture, connection troubleshoot |

### Load Balancing & Traffic Management

| # | Topic | Description |
|---|-------|-------------|
| 15 | [Load Balancing Comparison](15-load-balancing-services-comparison.md) | Decision flowchart for all Azure load balancing services |
| 16 | [Azure Load Balancer](16-azure-load-balancer.md) | Layer 4, health probes, SKUs, SNAT, zone redundancy |
| 17 | [Azure Application Gateway](17-azure-application-gateway.md) | Layer 7 proxy, WAF, URL routing, TLS termination |
| 18 | [Azure Front Door](18-azure-front-door.md) | Global Layer 7, anycast, WAF, caching, multi-region |
| 19 | [Azure Traffic Manager](19-azure-traffic-manager.md) | DNS-based global routing methods |
| 20 | [Azure CDN](20-azure-cdn.md) | Content delivery, edge caching, HTTPS for Blob Storage |
| 21 | [Azure Gateway Load Balancer](21-azure-gateway-load-balancer.md) | Transparent NVA insertion, VXLAN, security appliances |
| 22 | [API Management Policies](22-azure-api-management-policy-inheritance.md) | APIM policy hierarchy and `<base />` inheritance |

### Scenarios & Exam Prep

| # | Topic | Description |
|---|-------|-------------|
| 23 | [Networking Scenarios](23-networking-scenarios.md) | Hub-spoke, multi-region, practical architecture patterns |
| 24 | [Best Practices](24-best-practices.md) | Zero Trust, defense-in-depth, segmentation, cost tips |
| 25 | [Practice Questions: VPN Gateway](25-practice-questions-vpn-gateway.md) | AZ-700 exam prep — P2S, gateway transit, topology changes |

## Technology Decision Tree

```
What are you trying to connect?

  On-premises → Azure VNet
  └─▶ VPN Gateway (S2S) (#05) or ExpressRoute (#07)

  Individual users → Azure VNet
  └─▶ VPN Gateway (P2S) (#05)

  Azure VNet → Azure PaaS service
  └─▶ Private Endpoint (#03)

  On-premises → Azure PaaS service
  └─▶ VPN + Private Endpoint (#05 + #03)

  Two Azure VNets together
  └─▶ VNet Peering (#02)

  Azure ↔ on-premises (no firewall changes)
  └─▶ Hybrid Connections (#09)

  Choosing a load balancer?
  └─▶ Load Balancing Comparison (#15)
```

## Cross-References

> **General Pattern**: [Cloud & Infrastructure Architecture](../../architecture-general/05-cloud-infrastructure-platform-architecture/)
> **Security Architecture**: [Network Security](../../architecture-general/06-security-architecture/6.3-network-security/)
