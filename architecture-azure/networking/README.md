# Azure Networking

> **Taxonomy Reference**: §5 Cloud & Infrastructure / Platform Architecture (see [architecture_taxonomy_reference.md](../../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md))

## Quick Navigation

| Category | Description | Key Documents |
|----------|-------------|---------------|
| **[Guides](guides/01-index.md)** | Comprehensive modular study guides | [Index & Decision Tree](guides/01-index.md), [VNet Fundamentals](guides/00-networking-fundamentals.md), [Scenarios](guides/07-scenarios.md) |
| **[Connectivity](connectivity/)** | VPN, DNS, hybrid connections | [VPN Gateway](connectivity/azure-vpn-gateway.md), [DNS](connectivity/azure-dns.md) |
| **[Load Balancing](load-balancing/)** | Traffic distribution & CDN | [Comparison](load-balancing/azure-load-balancing-services-comparison.md), [Front Door](load-balancing/azure-front-door.md) |
| **[Security](security/)** | Firewalls & network security | [Firewall](security/azure-firewall-overview.md), [Security Comparison](security/azure-network-security-services-comparison.md) |
| **[Monitoring](monitoring/)** | Diagnostics & observability | [Network Watcher](monitoring/azure-network-watcher.md) |
| **[Virtual WAN](virtual-wan/)** | Hub-based global transit | [Virtual WAN](virtual-wan/azure-virtual-wan.md), [When to Use](virtual-wan/when_to_use_azure_virtual_wan.md) |

## Directory Structure

```
networking/
├── guides/               # Modular study guides (start here)
│   ├── 00-networking-fundamentals.md   # VNets, subnets, NSGs, peering
│   ├── 01-index.md                     # Master index & decision tree
│   ├── 02-vnet-fundamentals.md         # VNet core concepts & routing
│   ├── 03-private-endpoints-guide.md   # Private connectivity to PaaS
│   ├── 04-vpn-private-link-guide.md    # VPN vs Private Link decision
│   ├── 05-expressroute-bgp-guide.md    # ExpressRoute & BGP routing
│   ├── 06-relay-hybrid-connections-guide.md  # Relay & hybrid connections
│   ├── 07-scenarios.md                 # Practical architecture patterns
│   ├── 08-best-practices.md            # Design guidelines
│   └── 09-express-route-models.md      # ExpressRoute connectivity models
├── connectivity/         # VPN, DNS, hybrid connections
│   ├── azure-vpn-gateway.md            # VPN types, SKUs, protocols
│   ├── azure-dns.md                    # Public/private DNS zones
│   └── practice-questions-vpn-gateway.md  # AZ-700 exam prep
├── load-balancing/       # Traffic distribution services
│   ├── azure-load-balancing-services-comparison.md  # Master comparison
│   ├── azure-load-balancer.md          # Layer 4
│   ├── azure-application-gateway.md    # Layer 7 + WAF
│   ├── azure-front-door.md             # Global Layer 7 + CDN
│   ├── azure-traffic-manager.md        # DNS-based routing
│   ├── azure-cdn.md                    # Content delivery
│   ├── azure-gateway-load-balancer.md  # NVA chaining
│   └── azure-api-management-policy-inheritance.md  # APIM policies
├── security/             # Network security services
│   ├── azure-firewall-overview.md      # Managed firewall, policy hierarchy
│   └── azure-network-security-services-comparison.md  # NSG vs Firewall vs WAF
├── monitoring/           # Diagnostics & observability
│   └── azure-network-watcher.md        # IP Flow, packet capture, diagnostics
└── virtual-wan/          # Global transit networking
    ├── azure-virtual-wan.md            # Components, routing, costs
    └── when_to_use_azure_virtual_wan.md  # Decision guide
```

## Where to Start

1. **New to Azure networking?** Start with [Networking Fundamentals](guides/00-networking-fundamentals.md)
2. **Choosing a service?** Use the [Decision Tree in the Index](guides/01-index.md)
3. **Load balancing decision?** See the [Load Balancing Comparison](load-balancing/azure-load-balancing-services-comparison.md)
4. **Hybrid connectivity?** Read [ExpressRoute & BGP](guides/05-expressroute-bgp-guide.md) and [VPN Gateway](connectivity/azure-vpn-gateway.md)
5. **Exam prep (AZ-700)?** Check [Practice Questions](connectivity/practice-questions-vpn-gateway.md) and scenario sections in each guide

## Cross-References

> **General Pattern**: [Cloud & Infrastructure Architecture](../../architecture-general/05-cloud-infrastructure-platform-architecture/)
> **Security Architecture**: [Network Security](../../architecture-general/06-security-architecture/6.3-network-security/)
