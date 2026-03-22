# Azure Networking Scenarios Guide

See [Index](./01-index.md) for overview.

## Hub-and-Spoke VNet Architecture

**When to use:**
- Multiple business units/departments
- Centralized security and monitoring
- Shared services (firewall, DNS, proxy)
- Cost optimization

**Architecture:**

```
On-Premises
    │ Site-to-Site VPN
    │ or ExpressRoute
    ▼
    Hub VNet (10.0.0.0/24)
    ├─ Firewall
    ├─ Bastion Host
    ├─ DNS Server
    └─ Gateway
         │
         ├─ VNet Peering (no gateway needed)
         │
    ┌────┼────┬─────┐
    ▼    ▼    ▼     ▼
Spoke1 Spoke2 Spoke3 Spoke4
(10.1) (10.2) (10.3) (10.4)
```

**Key Points:**
- Hub handles all external connections
- Spokes communicate through hub
- All traffic can be inspected at hub
- Cost efficient: single gateway, multiple vnets

**UDR Configuration in Spokes:**
```
Destination: Internet (0.0.0.0/0)
Next Hop: Hub Firewall (10.0.0.10)
User Defined: Yes
```

---

## Multi-Region Active-Active

**When to use:**
- High availability across regions
- Disaster recovery
- Low latency for global users
- Compliance/data residency

**Architecture:**

```
North America                          Europe
┌─────────────────────┐          ┌─────────────────────┐
│ East US VNet        │          │ West Europe VNet    │
│ ├─ App Service      │          │ ├─ App Service      │
│ ├─ SQL (Primary)    │          │ ├─ SQL (Failover)   │
│ └─ Cache            │          │ └─ Cache            │
└────────┬────────────┘          └────────┬────────────┘
         │                               │
         └─ Global Peering ─────────────┘
           (or Service Fabric)
         
         Traffic → Geo-routed
         (Azure Traffic Manager)
```

**Connectivity Options:**

| Option | Latency | Cost | Use |
|--------|---------|------|-----|
| **VNet Peering** | Low | Low | Managed globally |
| **ExpressRoute Global Reach** | Very Low | High | Mission critical |
| **Site-to-Site VPN** | Medium | Low | Cost-conscious |

**Failover Setup:**
```
Primary Region:   SQL Server (Transactional replication)
Secondary Region: SQL Server (Read replicas for App)
                  Auto-failover groups handle switching
```

---

## Hybrid Cloud with ExpressRoute + VPN (Failover)

**When to use:**
- Ensure connectivity SLA (99.95%+)
- Private primary, internet backup
- Avoid connectivity loss

**Architecture:**

```
On-Premises                Azure
    │                   ┌──────────────┐
    ├─ ExpressRoute     │ VNet         │
    │ (Primary)         │ 10.0.0.0/24  │
    │ 99.95% SLA        └──────────────┘
    ├─ BGP advertises            ▲
    │ via ExpressRoute            │
    │                        (Traffic)
    │                             │
    │ ┌──────────────────────────┼───────┐
    │ ▼ (if ExpressRoute fails)   │       │
    └─ Site-to-Site VPN ──────────┘       │
      (Backup, manually enabled)      
                                   Uses Best Route:
                                   1. ExpressRoute
                                   2. VPN (if #1 down)
```

**BGP Weight Configuration:**
```
ExpressRoute route:  Weight 200 (preferred)
VPN route:          Weight 100 (failover)
```

**Cost Considerations:**
```
✯ ExpressRoute:      Fixed $100-200/month
✯ VPN:              Fixed $30-50/month  
✯ Both together:    Only ~$150/month total
                    = Insurance for 99.95% availability
```

---

## Private Endpoints for Multi-Tenant SaaS

**Scenario:**
- SaaS platform serving multiple customers
- Each customer gets dedicated Private Endpoint
- Traffic never leaves Microsoft network

**Architecture:**

```
Customer A          Customer B          Customer C
  VNet A              VNet B              VNet C
(10.1.0.0/24)      (10.2.0.0/24)      (10.3.0.0/24)
    │                   │                   │
    ├─ Private          ├─ Private          ├─ Private
    │  Endpoint         │  Endpoint         │  Endpoint
    └───────────────────┼───────────────────┘
                        │
                   SaaS Service
                        │
              (Azure SQL / Storage / etc)
```

**Benefits:**
- ✅ No internet exposure
- ✅ Per-customer access control
- ✅ Private DNS per customer
- ✅ Compliance-friendly (no data crosses public internet)

---

## Microservices with Service Mesh (AKS)

**Scenario:**
- Containerized microservices
- Inter-pod communication needs control
- Service discovery + load balancing

**Architecture:**

```
VNet: 10.0.0.0/24
│
├─ AKS Cluster
│  │
│  ├─ Frontend SVC → Service (80)
│  │   └─ Pod (envoy sidecar)
│  │
│  ├─ API SVC → Service (8080)
│  │   └─ Pod (envoy sidecar)
│  │
│  └─ Database SVC → Service (5432)
│      └─ Pod (envoy sidecar)
│
└─ Service Mesh Control Plane
   (Istio/Linkerd)
   ├─ Route traffic
   ├─ Load balance
   ├─ Retry logic
   └─ Circuit breaking
```

**Networking Components:**
- **Service**: DNS name + internal load balancer
- **Sidecar Proxies**: Control traffic between pods
- **Network Policies**: NSG rules at pod level

---

## Isolated Workload (PCI-DSS Compliance)

**Scenario:**
- Payment processing workload
- Isolation required
- Restricted access only

**Architecture:**

```
Corporate VNet (10.0.0.0/16)
├─ General workloads (no restrictions)
│
Isolated VNet (10.10.0.0/24)  ← Separate from corporate
├─ Payment processing only     
├─ NSG: Deny all inbound
├─ NSG: Allow only from App Gateway
├─ NSG: App → Database only (port 5432)
├─ NSG: Encrypted storage access only
│
Azure Firewall
├─ Rules: Payment VNet ↔ External only if whitelisted
├─ Rules: Logging enabled
├─ DLP: Block credit card patterns
```

**No Peering:**
```
Isolated VNet ─X─ Corporate VNet
(Cannot communicate)

↓

Application Gateway (DMZ)
├─ Validates input
├─ Routes to Isolated VNet only if approved
└─ Logs all traffic (audit trail)
```

---

## Disaster Recovery (Site to Site)

**Scenario:**
- Primary datacenter fails completely
- Failover to secondary within 15 minutes
- Acceptable data loss: 1 hour

**Architecture:**

```
Site A (Primary)         Site B (Failover)
New York                 Los Angeles
    │                           │
    ├─ ExpressRoute Circuit A   ├─ ExpressRoute Circuit B
    │  (BGP Weight: 200)        │  (BGP Weight: 100)
    │                           │
    └─ Azure Region 1 ──────────┘ ─ Azure Region 2
       (App Service/SQL)              (Cold standby)
```

**Failover Process:**
```
Normal:  Traffic → Region 1 (primary)
         BGP weights: Region1=200, Region2=100
         Region 2 receives read-only replicas

Failure: Region 1 ExpressRoute down
         BGP withdraws Region 1 routes
         Traffic → Region 2 (automatic)
         DNS updated (Azure Traffic Manager)
         Region 2 promoted to primary
         
Impact:  15-30 minute outage
         1 hour of data loss (acceptable RTO/RPO)
```

---

## Direct Access to PaaS from On-Premises (Private Link)

**Scenario:**
- On-prem app needs Azure SQL Database
- Cannot use public internet (compliance)
- Need low latency

**Architecture:**

```
On-Premises                         Azure
Application     VPN→Firewall→   Private Endpoint
    │                                 │
    │ Query: db.company.internal     │
    │                            (DNS redirect)
    │                                 │
    └─────────────────────────────────┘
                    ▼
            Azure SQL Database
            (private subnet)
            10.0.1.0/24
```

**DNS Resolution:**
```
On-Prem DNS:
  db.company.internal → 10.0.1.10 (Private Endpoint IP)

Connection Flow:
  1. App queries db.company.internal
  2. Resolves to 10.0.1.10 (private VNet IP)
  3. VPN carries traffic to Azure
  4. Reaches private endpoint
  5. Mapped to Azure SQL (no public IP needed)
```

---

## Key Decision Points

### Choosing Connectivity

```
Question: Need to connect cloud to on-premises?
    ├─ YES
    │   ├─ Performance critical?
    │   │   ├─ YES → ExpressRoute
    │   │   └─ NO → Site-to-Site VPN
    │   │
    │   └─ Need failover?
    │       ├─ YES → ExpressRoute + VPN
    │       └─ NO → Single option
    │
    └─ NO → Cloud-only architecture
```

### Choosing VNet Design

```
Question: Single VNet or Multi-VNet?
    ├─ Single VNet (< 3 apps)
    │   └─ Simpler management
    │
    ├─ Hub-Spoke (centralized services)
    │   └─ Most common enterprise
    │
    ├─ Full Mesh (all interconnected)
    │   └─ Rare, high complexity
    │
    └─ Isolated (compliance zones)
        └─ Security-critical workloads
```

---

## Exam-Style Questions

### VNet Peering Requirements and Limitations

**Question:** Virtual network peering lets you connect Azure VNets using the Azure backbone network. However, there are specific requirements and limitations associated with VNet peering. Select the appropriate requirements and limitations from the list below. (Select all that apply)

- **A)** It is only possible to peer VNets present in the same region using VNet peering. Peering VNets from different regions is not allowed.
- **B)** In a globally peered VNet, resources in one VNet cannot communicate with the front-end IP addresses of a Basic internal load balancer.
- **C)** The VNets involved in peering must have non-overlapping IP address spaces.
- **D)** You can modify a VNet's address space by adding or deleting address ranges after it is peered with another VNet.
- **E)** You can use default Azure name resolution to resolve names in VNets that are peered with each other.

**Correct Answers: B, C**

**Explanation:**

Virtual network peering connects VNets in the same or different regions using the Azure backbone network. Even after peering, the VNets are still regarded as separate resources.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | **Global VNet Peering** enables you to peer virtual networks from different regions. |
| **B** | ✅ Correct | In a globally peered VNet, resources in one VNet cannot communicate with the front-end IP addresses of a **Basic** internal load balancer. Basic Load Balancer is only supported within the same region. **Standard Load Balancer** is supported in both Global VNet Peering and regional VNet Peering. |
| **C** | ✅ Correct | The VNets that participate in peering must have **non-overlapping IP address spaces**. |
| **D** | ❌ Incorrect | Once two VNets are peered, you **cannot** modify their address space by adding or deleting address ranges. |
| **E** | ❌ Incorrect | You **cannot** use the default Azure name resolution to resolve names in peered VNets. You need Azure Private DNS zones or custom DNS. |

> **Reference**: [Create, change, or delete an Azure virtual network peering | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)

### P2S VPN Authentication with Active Directory Domain

**Question:** What server type is required to authenticate a user who connects via a Point-to-Site (P2S) connection using an Active Directory Domain Server?

- **A)** DNS Server
- **B)** Active Directory Domain Controller only
- **C)** DIAMETER Server
- **D)** RADIUS Server
- **E)** None of these

**Correct Answer: D**

**Explanation:**

AD Domain authentication allows users to connect to Azure using their company or organization's domain credentials. To integrate with the AD server for P2S VPN authentication, a **RADIUS server** is needed.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | A DNS server is used for name resolution, not authentication. |
| **B** | ❌ Incorrect | An AD Domain Controller alone is not sufficient for P2S authentication; a RADIUS server is required as an intermediary. |
| **C** | ❌ Incorrect | DIAMETER is a different AAA protocol not used in Azure P2S VPN scenarios. |
| **D** | ✅ Correct | A **RADIUS server** (e.g., Windows NPS) is required to authenticate P2S VPN users against Active Directory domain credentials. The authentication flow is: `VPN Client → Azure VPN Gateway → RADIUS Server → AD Domain Controller`. |
| **E** | ❌ Incorrect | A RADIUS server is the correct answer. |

**Authentication Flow:**
```
Remote User (P2S VPN Client)
    │
    │ Domain credentials (username/password)
    ▼
Azure VPN Gateway
    │
    │ RADIUS protocol (UDP 1812/1813)
    ▼
RADIUS Server (e.g., Windows NPS)
    │
    │ LDAP / Kerberos
    ▼
Active Directory Domain Controller
    │
    └─ Validates credentials → Returns accept/reject
```

> **Domain**: Design, implement, and manage connectivity services (20–25%)
>
> **Reference**: [About Azure Point-to-Site VPN connections - Azure VPN Gateway | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/point-to-site-about)

---

## References

- [Hub-Spoke VNet Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Virtual Network Peering](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)
- [ExpressRoute + VPN Failover](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager)
- [Private Link Architecture](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [About Point-to-Site VPN](https://learn.microsoft.com/en-us/azure/vpn-gateway/point-to-site-about)
