# Azure Networking Scenarios Guide

See [README](./README.md) for overview.

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
- Provider exposes service via **Azure Private Link Service**
- Traffic never leaves Microsoft network

**Architecture (Custom SaaS with Private Link Service):**

```
Consumer Side (Per Customer)                    Provider Side (SaaS Provider)
┌──────────────────────┐                       ┌──────────────────────────────┐
│ Customer A - VNet A  │                       │ Provider VNet                │
│ (10.1.0.0/24)        │                       │                              │
│  ┌────────────────┐  │                       │  ┌────────────────────────┐  │
│  │ Private        │  │── Private Link ──────▶│  │ Private Link Service   │  │
│  │ Endpoint       │  │                       │  │ (NAT IP: 10.100.0.x)  │  │
│  └────────────────┘  │                       │  └──────────┬───────────┘  │
└──────────────────────┘                       │             │              │
                                               │             ▼              │
┌──────────────────────┐                       │  ┌────────────────────────┐  │
│ Customer B - VNet B  │                       │  │ Standard Load Balancer │  │
│ (10.2.0.0/24)        │                       │  │ (Frontend: 10.100.1.4) │  │
│  ┌────────────────┐  │                       │  └──────────┬───────────┘  │
│  │ Private        │  │── Private Link ──────▶│             │              │
│  │ Endpoint       │  │                       │             ▼              │
│  └────────────────┘  │                       │  ┌────────────────────────┐  │
└──────────────────────┘                       │  │ Backend Pool           │  │
                                               │  │ ┌────┐ ┌────┐ ┌────┐ │  │
┌──────────────────────┐                       │  │ │VM1 │ │VM2 │ │VM3 │ │  │
│ Customer C - VNet C  │                       │  │ └────┘ └────┘ └────┘ │  │
│ (10.3.0.0/24)        │                       │  └────────────────────────┘  │
│  ┌────────────────┐  │                       │                              │
│  │ Private        │  │── Private Link ──────▶│                              │
│  │ Endpoint       │  │                       └──────────────────────────────┘
│  └────────────────┘  │
└──────────────────────┘
```

**Architecture (Azure PaaS-Only SaaS — no Private Link Service needed):**

```
Customer A          Customer B          Customer C
  VNet A              VNet B              VNet C
(10.1.0.0/24)      (10.2.0.0/24)      (10.3.0.0/24)
    │                   │                   │
    ├─ Private          ├─ Private          ├─ Private
    │  Endpoint         │  Endpoint         │  Endpoint
    └───────────────────┼───────────────────┘
                        │
              Azure PaaS Service
           (Azure SQL / Storage / etc)
         (Built-in Private Link support)
```

**Key Components:**

| Component | Role | Required When |
|-----------|------|---------------|
| **Private Link Service** | Provider-side resource that exposes your custom service behind a Standard Load Balancer | SaaS runs custom workloads (VMs, containers behind LB) |
| **Private Endpoint** | Consumer-side NIC with private IP in customer's VNet | Always — this is how customers connect |
| **Standard Load Balancer** | Routes traffic to backend pool on provider side | Custom SaaS with Private Link Service |
| **NAT IP Configuration** | Source NAT for consumer traffic on provider side | Custom SaaS with Private Link Service |

**Private Link Service Workflow:**
1. **Provider** deploys application behind a **Standard Load Balancer**
2. **Provider** creates a **Private Link Service** referencing the load balancer frontend IP
3. **Provider** shares the service **alias** (e.g., `myservice.{guid}.region.azure.privatelinkservice`) with customers
4. **Customer** creates a **Private Endpoint** in their VNet using the alias
5. **Provider** approves (or auto-approves) the connection request
6. Customer traffic flows privately over the Microsoft backbone

**Visibility & Access Control:**
- **RBAC only**: Restrict to subscriptions in the same Microsoft Entra tenant
- **Restricted by subscription**: Limit to a trusted set of subscriptions (cross-tenant)
- **Anyone with alias**: Public exposure, any consumer can request a connection

**Benefits:**
- ✅ No internet exposure
- ✅ Per-customer access control
- ✅ Private DNS per customer
- ✅ Compliance-friendly (no data crosses public internet)
- ✅ Cross-tenant connectivity without VNet peering or VPNs
- ✅ Each consumer's traffic is isolated; consumers cannot see each other
- ✅ Auto-approval for trusted subscriptions

**Limitations:**
- Private Link Service supported only on **Standard Load Balancer** (not Basic)
- IPv4 traffic only; TCP and UDP only
- Idle timeout of ~5 minutes (use TCP keepalives)
- Up to 8 NAT IP addresses per Private Link Service

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

### Cost Policies vs. High Availability — Datacenter Outage

**Question:** You are designing virtual networks with a focus on **cost control** and **high availability**. General cost-saving policies are in place, but the design must ensure resource availability in the event of a **complete data center outage**.

Which cost-saving policies would need to be **overridden** to meet this requirement? (Select all that apply)

- **A)** Only establish peering connections between virtual networks when it is necessary.
- **B)** Whenever possible, try to keep all resources within a single region.
- **C)** When designing multi-regional deployments, ensuring they are independent of any specific region is important.
- **D)** It is better to deploy resources in availability sets rather than deploying them in multiple availability zones to ensure high availability and fault tolerance.

**Correct Answer: A**

**Explanation:**

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ✅ Correct | Establishing VNet peering only when necessary is a cost-saving rule that reduces unnecessary traffic and costs. However, in a complete datacenter outage, **cross-region peering connections** may be required to keep resources reachable and available. This policy must be overridden to ensure resilience. |
| **B** | ❌ Incorrect | Keeping all resources in a single region is a cost-saving rule that also needs consideration, but the scenario specifically targets the policy most directly in conflict with cross-datacenter availability — which is VNet peering restriction. |
| **C** | ❌ Incorrect (user trap) | Designing multi-regional deployments to be **independent of any specific region** is actually an HA-supportive policy — it improves portability and recovery. This policy should be **maintained**, not overridden. |
| **D** | ❌ Incorrect | Deploying in availability sets rather than availability zones is a cost-saving trade-off, but availability zones/sets are a compute-layer concern, not directly a networking cost-saving policy being overridden in this context. |

**Availability Sets vs. Availability Zones:**

| | Availability Set | Availability Zone |
|---|---|---|
| **Scope** | Within one data center (fault/update domains) | Separate physical data center within a region |
| **Protects against** | Rack failures, planned maintenance | Full data center outage |
| **SLA** | 99.95% | 99.99% |
| **Cost** | Lower | Higher |
| **Use when** | Budget-constrained, rack-level HA sufficient | Data center-level resilience required |

> **Exam Tip**: Availability Sets ≠ data center redundancy. Only **Availability Zones** and **multi-region deployments** protect against a complete data center outage. Questions about "complete data center outage" always point toward zones and multi-region, not availability sets.
>
> **Reference**: [Availability options for Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/availability)

---

### Custom DNS Settings Auto-Propagation in VNets

**Question:** Is the following statement **True or False**?

> "Azure automatically updates DNS server settings for all virtual machines and role instances within the VNet when configuring custom DNS settings."

- **A)** True
- **B)** False

**Correct Answer: B — False**

**Explanation:**

When you configure custom DNS settings on a VNet in Azure, the settings are **not** automatically pushed to existing virtual machines or role instances. Each VM/NIC must be updated individually.

| Aspect | Behaviour |
|--------|-----------|
| **VNet-level custom DNS config** | Applies to **new** VMs/NICs added after the change; existing ones are **not** automatically updated |
| **Existing VMs** | Must be **restarted** (deallocated and reallocated) or have their NIC DNS settings manually updated to pick up the new VNet DNS settings |
| **Per-NIC DNS override** | Each NIC can have its own DNS server settings that override the VNet-level settings — these must also be configured manually |
| **Role instances (Cloud Services)** | Must be redeployed or the DNS settings configured individually |

**Common Misconception:**

> ❌ "Changing DNS servers on the VNet immediately affects all running VMs."

> ✅ Correct behaviour: The DHCP lease must be renewed on the VM for the new DNS setting to take effect. For VMs, this typically requires a **stop (deallocate) and restart**.

**DNS Setting Precedence (highest to lowest):**

```
NIC-level DNS setting  (overrides everything)
        ↓
VNet-level DNS setting  (used if NIC has no override)
        ↓
Azure-provided DNS (168.63.129.16)  (default fallback)
```

> **Exam Tip**: Questions about "automatic" DNS propagation are traps. Azure does **not** push DNS changes to existing VMs/NICs automatically. A restart or manual NIC update is required.
>
> **Reference**: [Name resolution for resources in Azure virtual networks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances)

---

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

### VNet Peering — Meeting All Connectivity Requirements

**Question:** Your team needs to connect virtual networks with the following requirements:
- Transfer data between VNets across **Azure AD tenants**, **subscriptions**, **Azure regions**, and **deployment models**
- Resources in one VNet can communicate with resources in another VNet
- **No downtime** for resources during or after peering setup
- **Low-latency, high-bandwidth** connection between resources in different VNets

Will **Virtual Network Peering** meet all of the above requirements?

- **A)** Yes
- **B)** No

**Correct Answer: A — Yes**

**Explanation:**

Azure VNet Peering (both local and global) satisfies every requirement listed:

| Requirement | Met? | How |
|-------------|------|-----|
| Transfer data across **Azure AD tenants** | ✅ | Cross-tenant peering is supported with appropriate RBAC in both tenants |
| Transfer data across **subscriptions** | ✅ | VNet peering works across different Azure subscriptions |
| Transfer data across **Azure regions** | ✅ | **Global VNet Peering** connects VNets in different Azure regions over the Microsoft backbone |
| Transfer data across **deployment models** | ✅ | A VNet created via **Azure Resource Manager** can be peered with a VNet created via the **classic deployment model** |
| Resources communicate across VNets | ✅ | Peered VNets route traffic using private IPs over the Azure backbone |
| **No downtime** when creating peering | ✅ | Creating or modifying a peering causes **no downtime** for resources in either VNet |
| Low-latency, high-bandwidth | ✅ | Traffic travels over the Azure backbone network, never the public internet |

**VNet Peering Types:**

| Type | Scope | Latency |
|------|-------|---------|
| **Local (Regional) VNet Peering** | VNets in the **same** Azure region | Lowest |
| **Global VNet Peering** | VNets in **different** Azure regions | Low (backbone, no internet) |

> **Exam Tip**: The key differentiators vs. other options — VPN Gateway adds encryption overhead and requires gateway deployment; ExpressRoute is for on-premises connectivity; Private Link is for PaaS service access, not VNet-to-VNet. Only VNet Peering satisfies **all four** requirements simultaneously with zero downtime.

> **Reference**: [Virtual network peering | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)

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

### Azure VNet Name Resolution Without Custom DNS Settings

**Question:** You are tasked with designing name resolution for resources within an Azure Virtual Network (VNet). Which Azure service allows VMs within a VNet to resolve domain names without specifying custom DNS settings?

- **A)** Azure Private DNS
- **B)** Azure Public DNS
- **C)** Azure DNS Private Link Service
- **D)** Azure DNS

**Correct Answer: D**

**Explanation:**

Azure DNS is the built-in DNS service (at `168.63.129.16`) that automatically resolves domain names for VMs within a VNet without any custom DNS configuration.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | **Azure Private DNS** requires explicit configuration — you must create a Private DNS Zone and link it to the VNet. It does not work automatically without custom settings. |
| **B** | ❌ Incorrect | **Azure Public DNS** is a recursive DNS resolver for public domain names on the internet. It does not automatically enable internal VNet name resolution. |
| **C** | ❌ Incorrect | **Azure DNS Private Link Service** allows access to Azure DNS via a private endpoint. It requires explicit setup and is not the default name resolution mechanism. |
| **D** | ✅ Correct | **Azure DNS** (Azure-provided DNS at `168.63.129.16`) is the built-in DNS service that automatically resolves domain names for VMs within a VNet. No custom settings are needed — it works out of the box for VM-to-VM name resolution within the same VNet. |

> **Exam Tip**: When the question asks about DNS resolution that works "without specifying custom DNS settings" or "automatically", the answer is **Azure DNS** (the built-in Azure-provided DNS). Azure Private DNS requires explicit zone creation and VNet linking.
>
> **Domain**: Design and implement core networking infrastructure (20–25%)
>
> **Reference**: [Name resolution for resources in Azure virtual networks | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances)

**Comparison: Azure DNS vs Azure Private DNS vs Public DNS**

| Feature | Azure DNS (Built-in) | Azure Private DNS | Public DNS |
|---------|---------------------|-------------------|------------|
| **What it is** | Azure-provided resolver at `168.63.129.16` | Private DNS zones linked to VNets | Internet-facing DNS (e.g., Azure DNS public zones, or external providers) |
| **Setup required** | None — automatic | Yes — create zone + link to VNet | Yes — register domain, create zone |
| **Scope** | Within a single VNet | Any linked VNet (cross-VNet possible) | Globally accessible on the internet |
| **Resolves** | Azure resource hostnames (VM, PaaS FQDNs) | Custom private domain names (e.g., `app.internal.contoso.com`) | Public domain names (e.g., `contoso.com`) |
| **Use case** | Default VM-to-VM resolution inside a VNet | Custom internal naming, private endpoint DNS, split-horizon DNS | Hosting public-facing domains |
| **Private endpoint DNS** | ❌ Does not resolve PE private IPs automatically | ✅ Required to resolve private endpoint FQDNs to private IPs | ❌ Resolves to public IP (bypasses private endpoint) |
| **Custom domain names** | ❌ No | ✅ Yes | ✅ Yes |
| **Cross-VNet resolution** | ❌ No | ✅ Yes (via VNet links) | ✅ Yes (internet-routable) |
| **Costs** | Free | Charged per zone + queries | Charged per zone + queries |
| **Split-horizon DNS** | ❌ No | ✅ Yes — same name resolves differently inside vs outside VNet | ❌ No |

---

### Scalable and Robust Application on VMs — Choosing the Right Load Balancing Services

**Question:** Your company is planning to deploy a new application on a fleet of Azure virtual machines (VMs) in the virtual network called "vNet1". Your boss wants you to ensure that the application is scalable and robust, and has provided the following requirements:

- Path-based routing at the **global** level
- Traffic should be load-balanced **within vNet1**
- **100% TLS/SSL offload**
- HTTP requests must be routed **within vNet1**
- **Session affinity** should be supported

To meet these requirements, what actions should you take? (Choose two answers.)

- **A)** Deploy an Application Gateway in front of the virtual machines (VMs) in vNet1
- **B)** Enable Azure Front Door
- **C)** Enable Azure Firewall
- **D)** Enable global load balancing (Azure Load Balancer cross-region)

**Correct Answers: A, B**

**Explanation:**

Both **Application Gateway** and **Azure Front Door** together address every requirement. No single service alone covers the full list — the combination is needed because some requirements are regional (within vNet1) and some are global.

| Requirement | Service | How |
|-------------|---------|-----|
| Path-based routing at the **global** level | **Azure Front Door** | Front Door is a global Layer 7 load balancer with URL/path-based routing, routing traffic to the nearest healthy backend across regions |
| Traffic load-balanced **within vNet1** | **Application Gateway** | Application Gateway is a regional Layer 7 load balancer that deploys inside (or in front of) a VNet and distributes HTTP traffic across the VM backend pool |
| 100% TLS/SSL offload | **Both** | Both Application Gateway and Front Door terminate TLS at the edge, so backend VMs receive plain HTTP — true 100% SSL offload |
| HTTP requests routed **within vNet1** | **Application Gateway** | After TLS is terminated by Application Gateway, it forwards plain HTTP requests to VMs inside vNet1 using path-based or host-based routing rules |
| Session affinity | **Both** | Application Gateway supports **cookie-based session affinity**; Front Door also supports session affinity via its routing rules |

**Why the other options are wrong:**

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **C — Azure Firewall** | ❌ Incorrect | Azure Firewall is a **security** service (Layer 4/7 threat inspection, FQDN filtering). It does **not** provide load balancing, TLS offload, path-based routing, or session affinity. It cannot replace a load balancer in this scenario. |
| **D — Global load balancing (cross-region Azure Load Balancer)** | ❌ Incorrect | Azure Load Balancer operates at **Layer 4 (TCP/UDP)** only. It has no understanding of HTTP paths, cannot perform TLS/SSL offload, and does **not** support session affinity (only source IP affinity). It also does not balance traffic evenly within vNet1 for HTTP workloads. |

**Traffic Manager** (another common distractor) is DNS-based and does **not** support session affinity or SSL offload either — DNS-level routing has no awareness of HTTP sessions.

**Combined Architecture:**

```
Internet Users
      │
      ▼
Azure Front Door (Global)
  ├─ Global path-based routing (e.g., /api/* → East US, /static/* → CDN)
  ├─ TLS termination (SSL offload — edge POP)
  ├─ Session affinity (optional, Front Door level)
  └─ Health probes to regional backends
      │
      ▼
Application Gateway (Regional — inside / in front of vNet1)
  ├─ TLS termination (SSL offload — regional, for any backend re-encryption)
  ├─ URL/path-based routing to VM backend pools
  ├─ Cookie-based session affinity
  ├─ WAF (optional — WAF v2 SKU)
  └─ Backend pool: VMs in vNet1
      │
      ▼
Virtual Machines in vNet1
  (receive plain HTTP traffic — fully offloaded)
```

**Key Design Principles:**

- **Front Door** sits at the global edge — closest to the user, routes across regions, and terminates TLS at the CDN/POP level.
- **Application Gateway** sits at the regional edge — within or peered to vNet1 — and handles intra-VNet routing, WAF, and further TLS offload before traffic reaches the VMs.
- Together they provide **two tiers of TLS offload**: at the global edge (Front Door) and at the regional boundary (Application Gateway). The VM backend sees only plain HTTP — achieving the "100% TLS offload" requirement.
- **Session affinity** is available at both tiers, ensuring sticky routing works whether the session is tracked at the global or regional level.

**Quick Reference — Feature Support by Service:**

| Feature | App Gateway | Front Door | Azure Firewall | Cross-Region LB |
|---------|:-----------:|:----------:|:--------------:|:---------------:|
| Path-based routing | ✅ Regional | ✅ Global | ❌ | ❌ |
| TLS/SSL offload | ✅ | ✅ | ❌ | ❌ |
| HTTP routing within VNet | ✅ | ❌ (global only) | ❌ | ❌ |
| Session affinity | ✅ Cookie-based | ✅ | ❌ | ❌ |
| Layer | 7 (HTTP) | 7 (HTTP) | 4/7 (security) | 4 (TCP/UDP) |
| Scope | Regional | Global | Regional | Cross-region |

> **Exam Tip**: When a scenario combines **global** requirements (path-based routing across regions) with **regional/VNet** requirements (intra-VNet routing, TLS offload, session affinity), the answer almost always involves **Azure Front Door + Application Gateway** as a tandem. Azure Firewall is a security service — never a load balancer. Azure Load Balancer (even cross-region) is Layer 4 and cannot offload TLS or route by HTTP path.
>
> **Domain**: Design, implement, and manage load balancing (20–25%)
>
> **References**:
> - [Azure Application Gateway overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/application-gateway/overview)
> - [What is Azure Front Door? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/frontdoor/front-door-overview)
> - [Load-balancing options — Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)

---

### Hub-and-Spoke VNet Peering — Traffic Forwarding Configuration

**Question:** You want to establish a Hub-and-Spoke VNet peering connection between two existing VNets (VNet1 and VNet2) in the East US region. Your objective is to allow resources in both VNets to communicate with each other **without using a network virtual appliance**. You have deployed VNet3 in the same region to serve as a hub between the other VNets. You plan to use a **VPN virtual network gateway** to allow VNet1 and VNet2 to communicate with each other through VNet3.

Which VNet peering connections should be configured to allow all forwarded traffic? (Select two)

- **A)** A connection between VNet1 and VNet3 with peering enabled and traffic forwarding enabled.
- **B)** A peering connection between VNet2 and VNet3, with traffic forwarding enabled.
- **C)** Peering connections should be directed only to VNet3, which serves as the hub.
- **D)** Only peering connections that are directed to VNet1 and VNet2 are allowed as spokes.

**Correct Answers: A, B**

**Explanation:**

In a hub-and-spoke topology, spoke VNets (VNet1 and VNet2) do **not** peer with each other directly. All traffic routes through the hub (VNet3) via its VPN gateway. For this to work, **Allow Forwarded Traffic** must be enabled on each spoke↔hub peering so that traffic originating in one spoke can be forwarded by the hub to the other spoke.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ✅ Correct | A peering connection between VNet1 (spoke) and VNet3 (hub) with **Allow Forwarded Traffic** enabled allows VNet1's traffic to be forwarded through VNet3 toward VNet2, and vice versa. |
| **B** | ✅ Correct | A peering connection between VNet2 (spoke) and VNet3 (hub) with **Allow Forwarded Traffic** enabled allows VNet2's traffic to be forwarded through VNet3 toward VNet1, and vice versa. |
| **C** | ❌ Incorrect | This describes the direction correctly (spokes peer to the hub only), but it is not a complete answer — it does not specify that forwarded traffic must be explicitly enabled. Direction alone is insufficient. |
| **D** | ❌ Incorrect | VNet1 and VNet2 are spokes; they do not accept peering connections *to themselves as hubs*. This statement confuses the hub and spoke roles. |

**Architecture — Peering Configuration:**

```
                    VNet3 (Hub — East US)
                    VPN Gateway
                   /            \
     ┌────────────┴──┐          ┌──┴────────────┐
     │ Peering A     │          │ Peering B     │
     │ Allow Forward │          │ Allow Forward │
     │ Allow GW Trans│          │ Allow GW Trans│
     └──────┬────────┘          └────────┬──────┘
            │                            │
       VNet1 (Spoke)               VNet2 (Spoke)
       Use Remote GW               Use Remote GW
       Allow Forward               Allow Forward
```

**Complete peering settings required:**

| Peering Link | Side | Setting | Value |
|---|---|---|---|
| VNet1 ↔ VNet3 | Hub (VNet3) | Allow Gateway Transit | ✅ Enabled |
| VNet1 ↔ VNet3 | Hub (VNet3) | Allow Forwarded Traffic | ✅ Enabled |
| VNet1 ↔ VNet3 | Spoke (VNet1) | Use Remote Gateways | ✅ Enabled |
| VNet1 ↔ VNet3 | Spoke (VNet1) | Allow Forwarded Traffic | ✅ Enabled |
| VNet2 ↔ VNet3 | Hub (VNet3) | Allow Gateway Transit | ✅ Enabled |
| VNet2 ↔ VNet3 | Hub (VNet3) | Allow Forwarded Traffic | ✅ Enabled |
| VNet2 ↔ VNet3 | Spoke (VNet2) | Use Remote Gateways | ✅ Enabled |
| VNet2 ↔ VNet3 | Spoke (VNet2) | Allow Forwarded Traffic | ✅ Enabled |

**Key distinction — Allow Forwarded Traffic vs. Allow Gateway Transit:**

| Setting | Purpose | Without It |
|---|---|---|
| **Allow Forwarded Traffic** | Permits traffic that did **not originate** in the directly connected VNet to traverse the peering | Spoke-to-spoke traffic is **dropped** at the hub peering boundary |
| **Allow Gateway Transit** | Shares the hub VPN/ExpressRoute gateway with the spoke | Spoke cannot reach external/on-premises networks via hub gateway |
| **Use Remote Gateways** | Instructs the spoke to route external traffic via the hub's gateway | Spoke must have its own gateway (extra cost, extra complexity) |

> **Exam Tip**: "Allow Forwarded Traffic" and "Allow Gateway Transit" serve **different purposes** and are both needed in a hub-and-spoke topology with VPN gateway. Gateway transit covers external connectivity (on-premises or VNet-to-VNet via gateway); forwarded traffic covers spoke-to-spoke routing **through** the hub.
>
> **Domain**: Design, implement, and manage connectivity services (20–25%)
>
> **Reference**: [Hub-spoke network topology in Azure — Azure Architecture Center | Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/networking/architecture/hub-spoke)

---

## References

- [Hub-Spoke VNet Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Virtual Network Peering](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)
- [ExpressRoute + VPN Failover](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager)
- [Private Link Architecture](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [About Point-to-Site VPN](https://learn.microsoft.com/en-us/azure/vpn-gateway/point-to-site-about)
