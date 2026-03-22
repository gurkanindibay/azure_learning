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

### P2S VPN Supported Protocols

**Question:** You create a Point-to-Site (P2S) VPN gateway connection to connect an individual client computer to your virtual network securely. Which of the following protocols can be used by the Point-to-Site VPN?

- **A)** OpenVPN protocol
- **B)** Secure Socket Tunneling Protocol (SSTP)
- **C)** IKEv2 VPN
- **D)** Any of the above

**Correct Answer: D**

**Explanation:**

Azure Point-to-Site VPN supports **all three** of these protocols. Each serves different platforms and use cases:

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ✅ Valid (but incomplete) | **OpenVPN** is an SSL/TLS-based protocol supported on Windows, macOS, Linux, Android, and iOS. It is the recommended protocol for P2S VPN connections due to its broad platform support and flexibility. |
| **B** | ✅ Valid (but incomplete) | **SSTP (Secure Socket Tunneling Protocol)** is a Microsoft proprietary SSL-based VPN protocol. It is supported **only on Windows** client devices. SSTP can traverse most firewalls since it uses TCP port 443 (HTTPS). |
| **C** | ✅ Valid (but incomplete) | **IKEv2 VPN** is an IPsec-based VPN protocol with native support on **macOS and iOS**. It also works on Windows. It is a standards-based solution that provides strong security. |
| **D** | ✅ Correct | **All three protocols** — OpenVPN, SSTP, and IKEv2 — are supported by Azure P2S VPN Gateway. The choice depends on client platform requirements and organizational needs. |

**Protocol comparison:**

| Protocol | Base Technology | Supported Platforms | Key Advantage |
|----------|----------------|---------------------|---------------|
| **OpenVPN** | SSL/TLS | Windows, macOS, Linux, Android, iOS | Broadest platform support |
| **SSTP** | SSL/TLS | Windows only | Firewall-friendly (TCP 443) |
| **IKEv2** | IPsec | Windows, macOS, iOS | Native macOS/iOS support |

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

### NSG Default Rules

**Question:** Azure automatically generates default rules in each user-created NSG. Choose the non-default rule from the options provided.

- **A)** AllowVNetInBound
- **B)** AllowAzureLoadBalancerInBound
- **C)** DenyAllInBound
- **D)** AllowInternetOutBound
- **E)** AllowAllInBound

**Correct Answer: E**

**Explanation:**

Azure creates a set of default rules for every Network Security Group (NSG). These default rules cannot be deleted but can be overridden by higher-priority rules. **AllowAllInBound** is not a default rule — allowing all inbound traffic by default would be a significant security risk.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | **AllowVNetInBound** is a default inbound rule that allows all incoming traffic originating from within the virtual network (and peered VNets). Priority: 65000. |
| **B** | ❌ Incorrect | **AllowAzureLoadBalancerInBound** is a default inbound rule that allows health probe traffic from the Azure Load Balancer. Priority: 65001. |
| **C** | ❌ Incorrect | **DenyAllInBound** is a default inbound rule that blocks all remaining inbound traffic not matched by higher-priority rules. Priority: 65500. |
| **D** | ❌ Incorrect | **AllowInternetOutBound** is a default outbound rule that allows all outbound traffic destined for the internet. Priority: 65001. |
| **E** | ✅ Correct | **AllowAllInBound** is **not** a default NSG rule. There is no default rule that allows all inbound traffic. By default, inbound traffic is denied unless it comes from the VNet or the Azure Load Balancer. |

**Default NSG rules summary:**

| Direction | Rule Name | Priority | Action |
|-----------|-----------|----------|--------|
| **Inbound** | AllowVNetInBound | 65000 | Allow traffic from VNet |
| **Inbound** | AllowAzureLoadBalancerInBound | 65001 | Allow Azure LB probes |
| **Inbound** | DenyAllInBound | 65500 | Deny all other inbound |
| **Outbound** | AllowVNetOutBound | 65000 | Allow traffic to VNet |
| **Outbound** | AllowInternetOutBound | 65001 | Allow outbound to internet |
| **Outbound** | DenyAllOutBound | 65500 | Deny all other outbound |

> **Exam Tip**: Remember that NSGs follow a "deny by default" model for inbound traffic. The only inbound traffic allowed by default is from the VNet itself and from the Azure Load Balancer. There is no **AllowAllInBound** rule.
>
> **Domain**: Design, implement, and manage security for virtual networking (10–15%)
>
> **Reference**: [Azure network security groups overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)

### NSG Rules for Azure Bastion Remote Administration

**Question:** As an Azure system administrator, you are responsible for migrating your company's on-premises servers to Azure. Your manager has asked you to configure an NSG (Network Security Group) to enable remote server administration from Azure Bastion and a VPN connection. The company's subnet range is 10.0.0.0/16, and you have been allocated a subnet range of 10.0.1.0/24 for the servers. The NSG has been assigned to the subnet. What rules should be configured in the NSG to allow remote server administration?

- **A)** Allow inbound traffic on port 3389 from any source IP address to any destination IP address in the 10.0.0.0/16 subnet.
- **B)** Allow inbound traffic on port 22 from any source IP address to any destination IP address in the 10.0.1.0/24 subnet.
- **C)** Allow inbound traffic from the AzureBastionSubnet to any destination IP address in the 10.0.1.0/24 subnet.
- **D)** Allow inbound traffic on port 22 from the public IP address of the VPN gateway to any destination IP address in the 10.0.0.0/16 subnet.

**Correct Answer: C**

**Explanation:**

Azure Bastion provides secure, managed RDP/SSH connectivity to VMs without exposing them to the public internet. NSG rules should be scoped to the **AzureBastionSubnet** as the source and limited to the specific server subnet (10.0.1.0/24), following the principle of least privilege.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | Allowing port 3389 from **any** source to the entire 10.0.0.0/16 subnet opens RDP access far too broadly. This violates the principle of least privilege and exposes all servers in the VNet — not just those in the allocated 10.0.1.0/24 range. |
| **B** | ❌ Incorrect | Allowing port 22 from **any** source to the 10.0.1.0/24 subnet restricts the destination correctly but still allows SSH from any source IP, which is insecure. It also only covers SSH and does not account for RDP-based administration. |
| **C** | ✅ Correct | Allowing inbound traffic from the **AzureBastionSubnet** to the 10.0.1.0/24 subnet is the correct approach. Azure Bastion acts as a secure jump box — traffic originates from the AzureBastionSubnet, so scoping the source to that subnet ensures only Bastion-initiated sessions reach the servers. This covers both RDP (3389) and SSH (22) through Bastion. |
| **D** | ❌ Incorrect | Allowing port 22 from the VPN gateway's public IP to the entire 10.0.0.0/16 subnet is overly broad. The destination should be scoped to 10.0.1.0/24 (the allocated server subnet), not the entire VNet. Additionally, using the public IP of the VPN gateway as source is not the typical pattern — VPN traffic arrives from the on-premises address space, not the gateway's public IP. |

**Azure Bastion traffic flow:**
```
Admin (Browser)
    │
    │ HTTPS (port 443)
    ▼
Azure Bastion (AzureBastionSubnet)
    │
    │ RDP (3389) or SSH (22) — private network
    ▼
Target VM (10.0.1.0/24)
    └─ NSG allows inbound from AzureBastionSubnet
```

**Key security principles:**
- **Least privilege**: Only allow traffic from AzureBastionSubnet, not from "any" source
- **Subnet scoping**: Restrict destination to the allocated 10.0.1.0/24 subnet, not the entire 10.0.0.0/16 VNet
- **Bastion model**: Azure Bastion eliminates the need to expose RDP/SSH ports to the public internet

> **Exam Tip**: When a question involves Azure Bastion, the NSG source should be the **AzureBastionSubnet** service tag. Azure Bastion handles both RDP and SSH, so you do not need separate port-specific rules from external sources.
>
> **Domain**: Design, implement, and manage security for virtual networking (10–15%)
>
> **Reference**: [Azure Bastion NSG access | Microsoft Learn](https://learn.microsoft.com/en-us/azure/bastion/bastion-nsg)

### Listing ExpressRoute Circuits in a Resource Group

**Question:** You have been tasked with configuring the ExpressRoute circuits. Additionally, you need to retrieve a list of all ExpressRoute circuits in a Resource Group. Which command would you use?

- **A)** `Get-AzExpressRouteCircuit -ResourceGroup`
- **B)** `Get-AzExpressRouteCircuit -ResourceGroupName`
- **C)** `Get-AzAllExpressRouteCircuit`
- **D)** `Get-AzExpressRouteCircuitStats`

**Correct Answer: B**

**Explanation:**

The `Get-AzExpressRouteCircuit` cmdlet retrieves ExpressRoute circuit information from your Azure subscription. When used with the `-ResourceGroupName` parameter, it lists all circuits within that specific Resource Group.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | The parameter `-ResourceGroup` is **not valid** for the `Get-AzExpressRouteCircuit` cmdlet. The correct parameter name is `-ResourceGroupName`. PowerShell cmdlets are strict about parameter names. |
| **B** | ✅ Correct | `Get-AzExpressRouteCircuit -ResourceGroupName <name>` is the correct command to list all ExpressRoute circuits within a specific Resource Group. |
| **C** | ❌ Incorrect | `Get-AzAllExpressRouteCircuit` is **not a valid Azure PowerShell cmdlet**. There is no such command in the Az module. |
| **D** | ❌ Incorrect | `Get-AzExpressRouteCircuitStats` is used to get the **combined primary and secondary path traffic statistics** of an ExpressRoute circuit, not to list circuits. |

**Common ExpressRoute PowerShell commands:**

| Command | Purpose |
|---------|---------|
| `Get-AzExpressRouteCircuit -ResourceGroupName <RG>` | List all circuits in a Resource Group |
| `Get-AzExpressRouteCircuit -Name <name> -ResourceGroupName <RG>` | Get a specific circuit |
| `Get-AzExpressRouteCircuitStats` | Get traffic statistics for a circuit |
| `New-AzExpressRouteCircuit` | Create a new ExpressRoute circuit |
| `Remove-AzExpressRouteCircuit` | Delete an ExpressRoute circuit |

> **Exam Tip**: Pay close attention to the exact parameter names in PowerShell cmdlets. `-ResourceGroup` and `-ResourceGroupName` are different — only the latter is valid for `Get-AzExpressRouteCircuit`.
>
> **Domain**: Design, implement, and manage connectivity services (20–25%)
>
> **Reference**: [Get-AzExpressRouteCircuit | Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/az.network/get-azexpressroutecircuit)

### Application Gateway Health Probe Source IP Address

**Question:** When using Azure Application Gateway Probes, which IP address is used by the Application Gateway as the source IP for health probes if you have a group of backend servers with public IP addresses?

- **A)** Application Gateway's backend public IP address
- **B)** Application Gateway's backend private IP address
- **C)** Application Gateway's frontend public IP address
- **D)** Application Gateway's frontend private IP address

**Correct Answer: C**

**Explanation:**

Azure Application Gateway maintains the health of all resources in its backend pool by performing regular health checks. If any resource is found to be unhealthy, it is automatically removed from the pool. The **source IP address** used for health probes depends on the type of endpoint in the backend pool.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | The Application Gateway does not use a backend IP address as the source for health probes. The probe originates from the Application Gateway itself, not from backend resources. |
| **B** | ❌ Incorrect | Similar to Option A, the Application Gateway does not use a backend IP address as the source for health probes. |
| **C** | ✅ Correct | When the backend server address has a **public endpoint**, the Application Gateway uses its **frontend public IP address** as the source IP for health probes. |
| **D** | ❌ Incorrect | The frontend private IP address is not used as the source for probes to public backend endpoints. However, if the backend server has a **private endpoint**, the source IP comes from the Application Gateway subnet's private IP address space. |

**Health probe source IP rules:**

| Backend Endpoint Type | Probe Source IP |
|-----------------------|-----------------|
| **Public IP** | Application Gateway's **frontend public IP** |
| **Private IP** | Private IP from the **Application Gateway subnet** |

**Key concept:**
```
Backend has Public IP:
  Health Probe Source → Application Gateway Frontend Public IP

Backend has Private IP:
  Health Probe Source → Private IP from Application Gateway Subnet
```

> **Exam Tip**: The source IP of health probes matches the endpoint type of the backend — public backends get probed from the frontend public IP, private backends get probed from the Application Gateway subnet's private IP space.
>
> **Domain**: Design and implement core networking infrastructure (20–25%)
>
> **Reference**: [Azure Application Gateway configuration overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/application-gateway/configuration-overview)

---

## Q: Traffic Manager — Weighted routing priority

When distributing traffic across a set of endpoints using the **Weighted Routing** method, you may want to prioritize a certain resource. What weight value should be assigned to this particular resource?

- **A)** 0
- **B)** 1
- **C)** 10
- **D)** 100
- **E)** 1000

**Correct Answer: E**

**Explanation:**

In the **Weighted routing method** of Traffic Manager, each endpoint is assigned a weight value between **1 and 1000**. This weight value is optional — if not provided, Traffic Manager uses a default weight of **1**. The higher the weight value, the higher the priority of the endpoint. Therefore, assigning a weight of **1000** gives an endpoint the highest possible priority.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A (0)** | ❌ Incorrect | Only weights between 1 and 1000 are valid. 0 is outside the allowed range. |
| **B (1)** | ❌ Incorrect | 1 is the lowest possible weight and represents the lowest priority. |
| **C (10)** | ❌ Incorrect | 10 is a valid weight but does not ensure the highest priority. |
| **D (100)** | ❌ Incorrect | 100 is a valid weight but does not guarantee the highest priority for the endpoint. |
| **E (1000)** | ✅ Correct | 1000 is the maximum weight value, giving the endpoint the highest possible priority. |

**Weight distribution formula:**
```
Traffic % for endpoint = (Endpoint Weight / Sum of All Weights) × 100

Example:
  Endpoint A: Weight 1000
  Endpoint B: Weight 1
  Endpoint C: Weight 1
  → Endpoint A receives: 1000/1002 ≈ 99.8% of traffic
```

> **Exam Tip**: Traffic Manager weighted routing supports weights from 1 to 1000. Default is 1. To give an endpoint the highest priority, assign weight 1000.
>
> **Domain**: Design and implement core networking infrastructure (20–25%)
>
> **Reference**: [Azure Traffic Manager routing methods | Microsoft Learn](https://learn.microsoft.com/en-us/azure/traffic-manager/traffic-manager-routing-methods#weighted-traffic-routing-method)

---

## Q: Azure virtual public IP address for platform resources

Which virtual public IP address facilitates a communication channel to Azure platform resources?

- **A)** 168.63.129
- **B)** 168.63.129.16
- **C)** 164.63.129.16
- **D)** 168.0.0.16
- **E)** 255.0.0.0

**Correct Answer: B**

**Explanation:**

`168.63.129.16` is a virtual public IP address that creates a communication channel for Azure platform resources. Customers can define any address space for their private VNet in Azure, so representing Azure platform resources with a unique public IP address is essential. This IP address is also known as the Azure **wireserver** and is used by all VMs in Azure to communicate with platform services.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A (168.63.129)** | ❌ Incorrect | This is not a valid IPv4 address — it is missing the fourth octet. |
| **B (168.63.129.16)** | ✅ Correct | This is the virtual public IP address used as a communication channel to Azure platform resources (wireserver). |
| **C (164.63.129.16)** | ❌ Incorrect | The first octet is wrong — it should be **168**, not 164. |
| **D (168.0.0.16)** | ❌ Incorrect | The second and third octets are wrong — the correct address is 168.**63.129**.16. |
| **E (255.0.0.0)** | ❌ Incorrect | This is a subnet mask, not an Azure platform IP address. |

**What does 168.63.129.16 do?**
```
168.63.129.16 provides:
├─ Health probe source for Azure Load Balancer
├─ DNS resolution (Azure-provided DNS)
├─ DHCP relay for obtaining a dynamic IP
├─ VM agent heartbeat (guest agent communication)
└─ Platform metadata and licensing (e.g., IMDS, KMS activation)
```

> **Exam Tip**: `168.63.129.16` is a well-known Azure IP that appears in multiple exam contexts — DNS resolution, health probes, and platform communication. It is accessible only from within Azure VMs and is non-routable from the public internet or on-premises.
>
> **Domain**: Design and implement core networking infrastructure (20–25%)
>
> **Reference**: [What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)

---

## Q: Centralized policy enforcement across VNets and subscriptions

When managing your task, it's important to centrally create, enforce, and log policies for applications and network connectivity across virtual networks and subscriptions. Which service would be best suited for this purpose?

- **A)** Azure Front Door
- **B)** Azure Firewall
- **C)** Azure Private Link
- **D)** Azure DNS
- **E)** Azure DDoS Protection

**Correct Answer: B**

**Explanation:**

**Azure Firewall** is a managed, cloud-based network security service that can be centrally used to create, enforce, and log application and network connectivity policies across virtual networks and subscriptions. It is fully stateful, with built-in high availability and unrestricted cloud scalability. Combined with Azure Firewall Manager, it enables centralized policy management across hub-spoke architectures.

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A (Azure Front Door)** | ❌ Incorrect | Azure Front Door is an application delivery network that provides global load balancing and site acceleration for web applications. It does not create or enforce network connectivity policies across VNets. |
| **B (Azure Firewall)** | ✅ Correct | Azure Firewall can centrally create, enforce, and log application and network connectivity policies across virtual networks and subscriptions. It supports DNAT, network, and application rules with hierarchical policy inheritance. |
| **C (Azure Private Link)** | ❌ Incorrect | Azure Private Link allows access to Azure PaaS services (e.g., Azure Storage, SQL Database) and partner services over a private endpoint in your virtual network. It is not a policy enforcement tool. |
| **D (Azure DNS)** | ❌ Incorrect | Azure DNS provides name resolution using Microsoft Azure infrastructure. It does not enforce application or network connectivity policies. |
| **E (Azure DDoS Protection)** | ❌ Incorrect | Azure DDoS Protection offers protection against distributed denial-of-service threats. It does not provide centralized policy creation or enforcement for network connectivity. |

**Azure Firewall centralized policy capabilities:**
```
Azure Firewall Manager
├─ Centralized policy management
├─ Hierarchical policy inheritance (parent → child)
├─ Application rules (Layer 7 FQDN filtering)
├─ Network rules (Layer 3/4 filtering)
├─ DNAT rules (inbound traffic translation)
├─ Threat intelligence-based filtering
└─ Logging and analytics via Azure Monitor
```

> **Exam Tip**: When a question mentions "centrally create, enforce, and log policies" for network connectivity across VNets and subscriptions, the answer is **Azure Firewall**. It is the only service in this list that provides centralized network policy enforcement.
>
> **Domain**: Design and implement core networking infrastructure (20–25%)
>
> **Reference**: [Azure networking services overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/networking/fundamentals/networking-overview)

---

## References

- [Hub-Spoke VNet Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Virtual Network Peering](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-peering-overview)
- [ExpressRoute + VPN Failover](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager)
- [Private Link Architecture](https://learn.microsoft.com/en-us/azure/private-link/private-link-overview)
- [About Point-to-Site VPN](https://learn.microsoft.com/en-us/azure/vpn-gateway/point-to-site-about)
- [Azure Network Security Groups Overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)
- [Azure Bastion NSG Access](https://learn.microsoft.com/en-us/azure/bastion/bastion-nsg)
- [Get-AzExpressRouteCircuit PowerShell Reference](https://learn.microsoft.com/en-us/powershell/module/az.network/get-azexpressroutecircuit)
- [Azure Application Gateway Configuration Overview](https://learn.microsoft.com/en-us/azure/application-gateway/configuration-overview)
- [Azure Traffic Manager Routing Methods](https://learn.microsoft.com/en-us/azure/traffic-manager/traffic-manager-routing-methods)
- [What is IP address 168.63.129.16?](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)
- [Azure Networking Services Overview](https://learn.microsoft.com/en-us/azure/networking/fundamentals/networking-overview)
