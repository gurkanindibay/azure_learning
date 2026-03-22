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

### Restricting Azure Storage Access to a Specific Virtual Network

**Question:** You want to ensure that an Azure Storage account is only accessible from a specific Azure virtual network without exposing the storage account to the public internet. Which Azure feature should you use to accomplish this?

- **A)** ExpressRoute Peering
- **B)** ExpressRoute Private Link
- **C)** Azure Service Endpoint
- **D)** Azure Private Link Service
- **E)** Network Security Groups

**Correct Answer: D**

**Explanation:**

Azure Private Link Service allows you to access Azure services, such as Azure Storage, privately from your virtual network. It creates a private endpoint in your virtual network, enabling you to access the storage account without exposing it to the public internet.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | **ExpressRoute Peering** is used to connect your on-premises network to Azure over a private connection. It does not provide a way to restrict access to an Azure Storage account from a specific virtual network without exposing it to the public internet. |
| **B** | ❌ Incorrect | **ExpressRoute Private Link** allows you to access Azure PaaS services over a private connection. While it provides a private connection, it does not specifically address the requirement of restricting access to an Azure Storage account from a specific virtual network without exposing it to the public internet. |
| **C** | ❌ Incorrect | **Azure Service Endpoint** enables you to secure your Azure Storage account by restricting access to specific virtual networks. However, it does not provide a way to completely isolate the storage account from the public internet — the service still uses its public IP address. |
| **D** | ✅ Correct | **Azure Private Link Service** creates a private endpoint in your virtual network with a private IP address, enabling you to access the storage account without exposing it to the public internet. This is the correct choice when you need complete isolation from the public internet. |
| **E** | ❌ Incorrect | **Network Security Groups (NSGs)** are used to filter network traffic to and from Azure resources. While NSGs can help control access to resources, they do not provide a way to restrict access to an Azure Storage account from a specific virtual network without exposing it to the public internet. |

**Key Distinction — Service Endpoint vs Private Link:**

| Feature | Service Endpoint | Private Link |
|---------|------------------|--------------|
| **Public IP** | Service still uses public IP | Private IP assigned in your VNet |
| **Internet Exposure** | Public endpoint still exists | Can fully disable public access |
| **On-premises Access** | Not supported | Supported via VPN/ExpressRoute |
| **Data Exfiltration** | Limited protection | Strong protection (specific resource) |

> **Exam Tip**: When the question specifically mentions "without exposing to the public internet", **Azure Private Link** is the correct answer. Service Endpoints secure the route but do not eliminate public IP exposure.
>
> **Domain**: Design, implement, and manage connectivity services (20–25%)
>
> **Reference**: [Azure Private Link overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)

### Public IP Address SKU for Dynamic IP Allocation

**Question:** You are the owner of an application and must use dynamic IP addresses for specific resources on your virtual network (VNet). What SKU should you use?

- **A)** Standard SKU
- **B)** Basic SKU
- **C)** Hybrid SKU
- **D)** Compiled SKU

**Correct Answer: B**

**Explanation:**

Public IP addresses can be created using a **Basic** or **Standard** SKU. A Basic SKU can assign the public IP address through **dynamic or static** allocation. However, when using a Standard SKU, the public IP always uses the **static allocation** method. It's important to note that Hybrid SKU and Compiled SKU are not valid options for Azure public IP addresses.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | **Standard SKU** public IPs always use the static allocation method. They do not support dynamic IP address assignment. |
| **B** | ✅ Correct | **Basic SKU** public IP addresses can be assigned through dynamic or static allocation methods, making it the correct choice when you need dynamic IP addresses on your VNet. |
| **C** | ❌ Incorrect | **Hybrid SKU** is not a valid SKU type for Azure public IP addresses. Only Basic and Standard SKUs exist. |
| **D** | ❌ Incorrect | **Compiled SKU** is not a valid SKU type for Azure public IP addresses. |

**Key Concept — Public IP Allocation Methods:**

| SKU | Dynamic Allocation | Static Allocation |
|-----|-------------------|-------------------|
| **Basic** | ✅ Supported | ✅ Supported |
| **Standard** | ❌ Not supported | ✅ Always static |

> **Exam Tip**: When a question asks about **dynamic IP allocation**, the answer is always **Basic SKU**. Standard SKU only supports static allocation.
>
> **Reference**: [Public IP addresses in Azure | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses)

---

## References

- [Hub-Spoke VNet Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Virtual Network Peering](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)
- [ExpressRoute + VPN Failover](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager)
- [Private Link Architecture](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [About Point-to-Site VPN](https://learn.microsoft.com/en-us/azure/vpn-gateway/point-to-site-about)
