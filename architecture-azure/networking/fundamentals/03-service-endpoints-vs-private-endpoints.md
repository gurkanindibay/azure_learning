---
type: Azure Service
title: "Azure Networking Fundamentals - Service Endpoints vs Private Endpoints"
description: "**Service Endpoints** extend your VNet identity to Azure services, enabling secure access over an optimized route."
tags: [networking]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Networking Fundamentals - Service Endpoints vs Private Endpoints

## 4. Service Endpoints vs Private Endpoints

### 4.1 Service Endpoints

**Service Endpoints** extend your VNet identity to Azure services, enabling secure access over an optimized route.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your VNet (10.0.0.0/16)                      │
│  ┌─────────────────────┐                                        │
│  │   Subnet            │                                        │
│  │   Service Endpoint: │                                        │
│  │   Microsoft.Storage │─────────▶ Azure Storage Account        │
│  │                     │           (Public endpoint secured     │
│  │   ┌─────┐           │            to allow only this VNet)    │
│  │   │ VM  │           │                                        │
│  │   └─────┘           │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Traffic goes over Azure backbone (optimized route)
- Service still uses its **public IP address**
- VNet identity is presented to the service
- Service firewall rules can restrict to specific VNets
- No additional cost

**How Service Endpoints Work:**

Virtual Network (VNet) service endpoints provide secure and direct connectivity to Azure services over an optimized route over the Azure backbone network. Endpoints allow you to secure your critical Azure service resources to only your virtual networks.

Service Endpoints enables private IP addresses in the VNet to reach the endpoint of an Azure service without needing a public IP address on the VNet.

#### 4.1.1 Critical Clarification: Who Gets the Private IP?

This is a commonly misunderstood concept. When we say "Service Endpoints enables private IP addresses in the VNet," we mean:

- **Your VMs (source)** use their **private IP addresses** when connecting to the Azure service
- **NOT** that the Azure service itself gets a private IP address inside your VNet

Compare this with **Private Endpoints**, which is the opposite:

| | **Service Endpoint** | **Private Endpoint** |
|---|---|---|
| **Who uses private IP?** | Your VMs (source IPs) | Azure service (destination IP) |
| **Azure service has...** | **Public IP** (but firewall-restricted) | **Private IP inside your VNet** |
| **DNS resolution** | Resolves to Azure service's **public IP** | Resolves to the **private IP** in your VNet |
| **Example** | Traffic from `10.0.1.5` (private) → `storage.blob.core.windows.net` (public IP, but only accepts from your VNet) | Traffic from `10.0.1.5` (private) → `storageXXXX.privatelink.blob.core.windows.net` (resolves to private IP) |

> **Key Takeaway**: Both involve "private IPs," but they apply to different directions. Service Endpoints make your VMs appear to come from private IPs. Private Endpoints make the Azure service appear as a private resource inside your VNet.

**Practical Scenario: Ensuring Traffic Travels via Microsoft Backbone**

**Scenario:**
Your on-premises network contains a VPN gateway. You have an Azure subscription with:
- **vgw1**: Virtual network gateway (Gateway for Site-to-Site VPN to the on-premises network)
- **storage1**: Storage account (Standard performance tier)
- **Vnet1**: Virtual network (Enabled forced tunneling)
- **VM1**: Virtual machine (Connected to Vnet1)

**Requirement:** Ensure all traffic from VM1 to storage1 travels across the Microsoft backbone network.

**Solution Comparison:**

| Option | Why It Works / Doesn't Work |
|--------|---------------------------|
| **Service Endpoints** ✅ | Provides secure and direct connectivity to Azure Storage over an optimized route over the Azure backbone network. When you enable a service endpoint for Azure Storage on the subnet where VM1 is located, traffic from VM1 to storage1 will use the Azure backbone network instead of going through the internet or the VPN gateway. |
| **Network Security Group (NSG)** ❌ | NSGs control traffic flow by allowing or denying traffic based on rules, but they don't determine the network path. They don't ensure traffic uses the Microsoft backbone. |
| **Azure AD Application Proxy** ❌ | Used for providing secure remote access to on-premises web applications. Not relevant for VM-to-storage connectivity. |
| **Azure Firewall** ❌ | A network security service that filters traffic, but doesn't force traffic to use the Microsoft backbone network. |

**Key Takeaway:**
> Service endpoints ensure that traffic between Azure resources (VM1) and Azure services (storage1) stays on the Microsoft backbone network, providing better security and performance. This is the correct solution when you need to optimize and secure traffic between Azure VMs and Azure PaaS services.

### 4.2 Service Endpoint Policies

**Service Endpoint Policies** allow you to filter virtual network traffic to Azure services, restricting access to only specific Azure service resources.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Your VNet (10.0.0.0/16)                      │
│  ┌─────────────────────────────┐                                │
│  │   Subnet                    │                                │
│  │   Service Endpoint:         │                                │
│  │   Microsoft.Storage         │                                │
│  │                             │     ┌────────────────────┐     │
│  │   Service Endpoint Policy:  │────▶│ storageAccountA ✅  │     │
│  │   Allow only storageAccountA│  ✗  │ storageAccountB ❌  │     │
│  │                             │     └────────────────────┘     │
│  └─────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- Provide **granular control** over which specific Azure service resources are accessible from your VNet
- Help prevent **data exfiltration** by restricting outbound access to only approved Azure resources
- Currently supported for **Azure Storage** (with expanding service support)
- Applied at the **subnet level** alongside service endpoints
- Can filter by specific resource instances, not just service type

**How Service Endpoint Policies Work:**

1. A service endpoint is enabled on the subnet (e.g., `Microsoft.Storage`)
2. A service endpoint policy is created and associated with the subnet
3. The policy defines which specific Azure resources (e.g., specific storage accounts) are allowed
4. Traffic to any other resources of that service type is denied

**Use Cases:**
- Restrict a subnet to only access **approved storage accounts**, preventing users from exfiltrating data to unauthorized storage accounts
- Enforce organizational policies on which Azure service instances can be reached from specific subnets
- Complement NSGs by adding service-level filtering that NSGs cannot provide

> **Important**: Service Endpoint Policies provide data exfiltration protection at the service resource level, which is a significant improvement over basic Service Endpoints that only secure access at the service type level.

### 4.3 What Service Endpoints Do NOT Provide

Understanding what Service Endpoints **cannot** do is equally important for exam preparation:

| Misconception | Reality |
|---------------|---------|
| **End-to-end encryption** | Service Endpoints optimize the routing path over the Azure backbone but do **not** provide encryption. Encryption in transit depends on the protocol used (e.g., HTTPS/TLS) and is configured at the service level, not by Service Endpoints. |
| **Custom routing** | Service Endpoints do **not** allow you to apply custom routing to traffic destined for Azure services. In fact, enabling a Service Endpoint adds a system route with the service's public IP prefixes that **overrides** any custom (UDR) routes for that traffic. |
| **On-premises access** | Service Endpoints only work for traffic originating from within the VNet. On-premises traffic cannot use Service Endpoints (use Private Endpoints instead). |
| **Disabling public access** | Service Endpoints still use the service's public IP address. They restrict **who** can access the service, not the endpoint itself. |

> **Exam Tip**: If a question mentions "custom routing to Azure services" or "end-to-end encryption", Service Endpoints are **not** the correct answer.

### 4.4 Comparison Table

| Feature | Service Endpoint | Private Endpoint |
|---------|------------------|------------------|
| **Destination IP** | Service's **public IP** (firewall-restricted) | **Private IP** inside your VNet |
| **Source IP** | Your VNet's **private IPs** | Your VNet's **private IPs** |
| **Traffic Path** | Azure backbone (optimized) | Azure backbone (Private Link) |
| **On-premises Access** | Not supported | Supported via VPN/ExpressRoute |
| **Cross-region** | Limited | Fully supported |
| **DNS Changes** | Not required | Required (resolves to private IP) |
| **Cost** | Free | Per hour + data processing |
| **Data Exfiltration Protection** | Limited (entire service) | Strong (specific resource) |
| **Disable Public Access** | No (public IP still exists) | Yes (can fully disable) |

### 4.5 When to Use Each

**Use Service Endpoints when:**
- Simple setup is needed
- Cost is a concern
- Traffic only originates from Azure VNet
- Basic network isolation is sufficient

**Use Private Endpoints when:**
- On-premises resources need access
- You want to disable public access completely
- Cross-region private connectivity is needed
- Data exfiltration protection is critical
- Compliance requires no public IP exposure

### 4.6 Practice Question: Restricting Storage Account Access to a Specific VNet

**Question:** You want to ensure that an Azure Storage account is only accessible from a specific Azure virtual network without exposing the storage account to the public internet. Which Azure feature should you use?

- **A)** ExpressRoute Peering
- **B)** ExpressRoute Private Link
- **C)** Azure Service Endpoint
- **D)** Azure Private Link Service
- **E)** Network Security Groups

**Correct Answer: D — Azure Private Link Service**

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ❌ Incorrect | ExpressRoute Peering connects on-premises to Azure over a private connection. It does not restrict storage access from a specific VNet. |
| **B** | ❌ Incorrect | ExpressRoute Private Link provides private PaaS access over ExpressRoute, but does not address VNet-only storage isolation. |
| **C** | ❌ Incorrect | Service Endpoints restrict access to specific VNets but the storage account still uses its **public IP address** — it is not fully isolated from the public internet. |
| **D** | ✅ Correct | Azure Private Link creates a **private endpoint** with a private IP in your VNet. You can then disable public access entirely, ensuring the storage account is never exposed to the public internet. |
| **E** | ❌ Incorrect | NSGs filter traffic to/from Azure resources but cannot restrict PaaS service access to a specific VNet. |

> **Exam Tip**: When the question says "without exposing to the public internet", the answer is **Private Link / Private Endpoint**, not Service Endpoint. Service Endpoints secure the route but do not eliminate public IP exposure.

### 4.7 Practice Question: Scenarios That Benefit from Service Endpoints

**Question:** You are designing a secure Azure architecture. Which of the following scenarios would benefit from the implementation of Azure Service Endpoints?

- **A)** Restricting access to Azure Storage accounts only from a specific subnet within your VNet
- **B)** Enabling end-to-end encryption for data in transit to Azure services
- **C)** Applying custom routing to network traffic destined for Azure services
- **D)** Implementing a policy that filters outbound traffic from a subnet to an Azure service based on attributes like target service, region, etc.

**Correct Answers: A and D**

| Option | Verdict | Explanation |
|--------|---------|-------------|
| **A** | ✅ Correct | Service Endpoints allow you to secure Azure service resources to only a specific subnet or set of subnets within your virtual network. By enabling a service endpoint on a subnet and configuring the storage account firewall to allow only that VNet/subnet, you restrict access to that specific subnet. |
| **B** | ❌ Incorrect | Service Endpoints do **not** provide end-to-end encryption. They optimize the routing path to use the Azure backbone network, but encryption in transit is handled by the application-layer protocol (e.g., HTTPS/TLS), not by Service Endpoints. |
| **C** | ❌ Incorrect | Service Endpoints do **not** enable custom routing. In fact, enabling a Service Endpoint creates a **system route** with the Azure service's public IP prefixes that takes priority over any custom User-Defined Routes (UDRs). This means Service Endpoints actually **override** custom routing for traffic destined to the service. |
| **D** | ✅ Correct | **Service Endpoint Policies** extend Service Endpoints by providing granular filtering of outbound VNet traffic to Azure services. They allow you to restrict which specific Azure resources (e.g., specific storage accounts) can be accessed from a subnet, filtering based on attributes like the target service resource. |

> **Key Takeaway**: Service Endpoints secure access (who can reach the service) and optimize routing (Azure backbone). They do **not** encrypt traffic or provide custom routing. Service Endpoint Policies add granular resource-level filtering on top of Service Endpoints.

### 4.8 ASCII Diagrams (Quick Visual Guide)

These diagrams summarize the key concepts in exam-friendly form.

#### 4.8.1 App Service VNet Integration (Outbound Only)

```text
								(Public Internet)
											 |
								 [ App Service ]
								 [  Web App     ]
											 |
					Outbound via VNet Integration
											 v
				+----------------------------------+
				| VNet                             |
				|  Delegated Subnet (integration)  |
				|   - private IP per instance      |
				+----------------------------------+
						|                 |            \
						v                 v             v
				[VM/DB]      [Private Endpoint]   [On-prem]
																				 (VPN/ExpressRoute)
```

Key point: VNet Integration provides private **outbound** reachability from the app. It does not by itself provide private inbound access to the app.

#### 4.8.2 Inbound Private Access Uses Private Endpoint

```text
Clients in VNet --> [Private Endpoint] --> [App Service]
												 (private IP)
```

#### 4.8.3 Routing Modes

```text
Option A: Private-only routing
------------------------------
App -> RFC1918/private targets -> VNet
App -> Internet targets         -> Direct Internet egress

Option B: Route-all
-------------------
App -> All outbound traffic -> VNet -> (Firewall/NAT/UDR) -> Destinations
```

#### 4.8.4 Service Endpoint vs Private Endpoint (Traffic Path)

```text
SERVICE ENDPOINT
----------------
Subnet identity allowed by PaaS firewall.
No private IP for the service in your subnet.

[App in VNet] ---> Azure backbone ---> [PaaS public endpoint]
			|
			+-- subnet is trusted/allowed


PRIVATE ENDPOINT
----------------
Private NIC/IP inside your VNet for the PaaS service.

[App in VNet] ---> [Private IP in your subnet] ---> [PaaS service]
												 ^
										DNS must resolve here
```

#### 4.8.5 DNS Requirement for Private Endpoint

```text
Without private DNS:
App -> service FQDN resolves to public IP -> blocked/wrong path

With private DNS zone link:
App -> service FQDN resolves to private IP -> Private Endpoint path works
```

#### 4.8.6 NSG and UDR Scope

```text
NSG/UDR on integration subnet affect:
	- traffic routed into VNet Integration

They do NOT control:
	- inbound HTTP(S) traffic to App Service itself
```

---

