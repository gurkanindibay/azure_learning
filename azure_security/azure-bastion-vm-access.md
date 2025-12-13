# Azure Bastion - Secure VM Access

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [How Azure Bastion Works](#how-azure-bastion-works)
- [Authentication and Security](#authentication-and-security)
- [Comparison with Other Solutions](#comparison-with-other-solutions)
- [Practice Questions](#practice-questions)

---

## Overview

**Azure Bastion** is a fully managed PaaS service that provides secure and seamless RDP and SSH connectivity to virtual machines directly through the Azure portal over TLS (port 443), without exposing VMs through public IP addresses.

### Key Characteristics

- **Protocol**: Uses TLS over TCP port 443
- **Supported Connections**: RDP (Windows) and SSH (Linux)
- **Access Method**: Through Azure portal (browser-based)
- **No Public IP Required**: VMs don't need public IP addresses
- **Fully Managed**: PaaS service, no maintenance required

---

## Key Features

### Security Benefits

✅ **No Public IP Exposure** - VMs remain protected without public IP addresses  
✅ **TLS Encryption** - All connections encrypted over port 443  
✅ **MFA Support** - Integration with Azure AD and Conditional Access  
✅ **Centralized Access** - All connections through Azure portal  
✅ **NSG Protection** - Can be protected by Network Security Groups  

### Connectivity Features

- **RDP Support**: Native RDP connectivity to Windows VMs
- **SSH Support**: Native SSH connectivity to Linux VMs
- **Port 443**: Uses standard HTTPS port (443) for all connections
- **No VPN Required**: Direct access without VPN or ExpressRoute
- **No Jump Box**: Eliminates need for jump servers or bastion hosts

### Networking Requirements

- **Dedicated Subnet**: Requires a subnet named `AzureBastionSubnet`
- **Minimum Subnet Size**: /26 or larger
- **Virtual Network**: Must be in the same VNet as target VMs

---

## How Azure Bastion Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         User/Administrator                       │
│                                                                  │
│  1. Authenticates with Azure AD + MFA (if required)            │
│  2. Connects via Azure Portal (HTTPS/443)                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ TLS/443
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure Bastion Service                       │
│                   (PaaS - Fully Managed)                        │
│                                                                  │
│  • Terminates TLS connection                                    │
│  • Validates user permissions (RBAC)                            │
│  • Initiates RDP/SSH to target VM                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      │ RDP (3389) or SSH (22)
                      │ Over private network
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Virtual Network                           │
│                                                                  │
│  ┌──────────────────────┐      ┌──────────────────────┐       │
│  │  AzureBastionSubnet  │      │   VM Subnet          │       │
│  │  (/26 or larger)     │      │                      │       │
│  │                      │──────│  VM1 (No public IP)  │       │
│  │  Azure Bastion Host  │      │  VM2 (No public IP)  │       │
│  │                      │      │  VM3 (No public IP)  │       │
│  └──────────────────────┘      └──────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Connection Flow

1. **User Authentication**: User logs into Azure portal with Azure AD credentials
2. **MFA Challenge**: If Conditional Access requires it, MFA is enforced
3. **RBAC Validation**: Azure validates user has appropriate permissions
4. **TLS Connection**: Browser establishes TLS connection to Bastion over port 443
5. **Private Network Access**: Bastion connects to VM using RDP/SSH over private network
6. **Session Established**: User interacts with VM through browser

---

## Authentication and Security

### Azure AD Integration

Azure Bastion integrates with **Azure Active Directory (Azure AD)** and supports:

- **Conditional Access Policies**: Enforce MFA, location-based access, device compliance
- **Multi-Factor Authentication (MFA)**: Require MFA before allowing network connectivity
- **Azure RBAC**: Control who can access which VMs
- **Just-in-Time Access**: Can be combined with Azure AD PIM for temporary access

### Required Permissions

Users need appropriate RBAC roles to connect to VMs via Bastion:

| Role | Scope | Permissions |
|------|-------|-------------|
| **Virtual Machine Contributor** | VM | Full VM management including Bastion access |
| **Reader** | VM | Can view VM and connect via Bastion (read-only access) |
| **Reader** | Azure Bastion resource | Required to see and use Bastion |

### MFA Enforcement

To enforce MFA for VM access through Bastion:

1. Create a **Conditional Access Policy** in Azure AD
2. Target the policy to users/groups requiring VM access
3. Set **Conditions**: 
   - Cloud apps: Azure Management
   - Grant controls: Require MFA
4. Result: Users must complete MFA before accessing Bastion

---

## Comparison with Other Solutions

### Azure Bastion vs Just-in-Time (JIT) VM Access

| Feature | Azure Bastion | JIT VM Access |
|---------|---------------|---------------|
| **Purpose** | Secure RDP/SSH access via browser | Temporary opening of management ports |
| **Public IP Required** | ❌ No | ✅ Yes (on VM or Load Balancer) |
| **Connection Method** | Azure portal over TLS (443) | Direct RDP/SSH to public IP |
| **Port Exposure** | Only 443 (to Bastion) | Temporarily opens 3389/22 |
| **MFA Enforcement** | ✅ Via Conditional Access | ❌ Not natively enforced |
| **TLS/Browser Access** | ✅ Yes | ❌ No |
| **Management Overhead** | Fully managed PaaS | Requires NSG rule management |
| **Use Case** | Production VMs without public IPs | Reducing attack surface on public IPs |

**Key Difference**: 
- **Azure Bastion** is a **connectivity service** that eliminates public IP exposure entirely
- **JIT VM Access** is a **security feature** that temporarily opens ports on VMs that already have public IPs

### Azure Bastion vs Traditional Jump Box

| Feature | Azure Bastion | Traditional Jump Box |
|---------|---------------|---------------------|
| **Infrastructure** | Fully managed PaaS | Self-managed VM |
| **Maintenance** | None required | OS patches, updates, monitoring |
| **Cost** | Pay for Bastion service | Pay for VM + storage + compute |
| **Availability** | 99.9% SLA | Depends on VM configuration |
| **Public IP** | Not required on target VMs | Required on jump box |
| **Security** | Built-in Azure AD + MFA | Manual configuration |

### When to Use Each Solution

#### Use Azure Bastion When:
- ✅ VMs should **not have public IP addresses**
- ✅ Need to enforce **MFA before network access**
- ✅ Want **browser-based access** over TLS (port 443)
- ✅ Require both **RDP and SSH** support
- ✅ Want a **fully managed** solution
- ✅ Need to meet compliance requirements for secure remote access

#### Use JIT VM Access When:
- VMs already have or require public IPs
- Want to reduce attack surface by closing ports when not in use
- Need cost-effective port management (JIT is free with Defender for Cloud)
- Don't need browser-based access

#### Use Traditional VPN/Jump Box When:
- Need to access multiple protocols beyond RDP/SSH
- Require file transfer capabilities
- Have existing jump box infrastructure
- Need to access on-premises resources through hybrid connectivity

---

## Practice Questions

### Question 1: Secure VM Access with MFA

**Scenario**: You have an Azure subscription that contains a virtual network named VNET1 and 10 virtual machines. The virtual machines are connected to VNET1.

You need to design a solution to manage the virtual machines from the internet. The solution must meet the following requirements:

- Incoming connections to the virtual machines must be authenticated by using Azure Multi-Factor Authentication (MFA) before network connectivity is allowed
- Incoming connections must use TLS and connect to TCP port 443
- The solution must support RDP and SSH

**Question**: To provide access to virtual machines on VNET1, use:

A) Just-in-time (JIT) VM access  
B) Azure Web Application Firewall (WAF) in Azure Front Door  
C) Azure Bastion  
D) Azure VPN Gateway  

<details>
<summary><b>Answer</b></summary>

**C) Azure Bastion** ✅

**Explanation**:

**Azure Bastion is correct** because it:
- ✅ Provides secure RDP and SSH connectivity directly through the Azure portal over **TLS (port 443)**
- ✅ Supports integration with **Azure Active Directory (Azure AD)** and **Conditional Access policies**
- ✅ Can enforce **Azure Multi-Factor Authentication (MFA)** through Conditional Access before allowing network-level access
- ✅ Supports both **RDP and SSH** protocols
- ✅ Does not require exposing VMs with public IP addresses
- ✅ All connections are **browser-based** and encrypted over TLS

**Why other options are incorrect**:

**Just-in-time (JIT) VM access** ❌
- While it reduces attack surface by opening management ports only when needed, it:
  - Still requires **public IP addresses** on VMs
  - Does **not natively enforce MFA** at the network connectivity level
  - Does **not provide TLS-based browser access** (uses direct RDP/SSH)
  - Focuses on port management, not authentication enforcement

**Azure Web Application Firewall (WAF) in Azure Front Door** ❌
- WAF and Front Door are designed to protect **web applications** (HTTP/HTTPS traffic)
- They do **not provide RDP or SSH access** to virtual machines
- Not suitable for VM management connectivity

**Azure VPN Gateway** ❌
- Provides site-to-site or point-to-site VPN connectivity
- Does not provide TLS over port 443 for RDP/SSH
- Requires VPN client configuration
- Does not meet the browser-based access requirement

**References**:
- [Azure Bastion Overview](https://learn.microsoft.com/en-us/azure/bastion/bastion-overview)
- [Connect to VM using RDP via Bastion](https://learn.microsoft.com/en-us/azure/bastion/bastion-connect-vm-rdp-windows)
- [JIT VM Access](https://learn.microsoft.com/en-us/azure/defender-for-cloud/just-in-time-access-usage)

</details>

---

### Question 2: Bastion Subnet Requirements

**Question**: You are deploying Azure Bastion to provide secure access to VMs in a virtual network. What is the minimum subnet size required for the Azure Bastion subnet?

A) /28  
B) /27  
C) /26  
D) /24  

<details>
<summary><b>Answer</b></summary>

**C) /26** ✅

**Explanation**:

Azure Bastion requires a dedicated subnet named `AzureBastionSubnet` with a minimum size of **/26** (64 IP addresses). This ensures enough IP addresses for the Bastion infrastructure and scaling.

**Subnet Naming**: The subnet **must** be named `AzureBastionSubnet` (case-sensitive).

**Reference**:
- [Azure Bastion Configuration Settings](https://learn.microsoft.com/en-us/azure/bastion/configuration-settings)

</details>

---

### Question 3: Bastion vs JIT

**Question**: Your company has 20 Azure VMs that currently have public IP addresses. Security requirements have changed, and you need to implement a solution that:
- Eliminates public IP addresses on VMs
- Provides browser-based access
- Enforces MFA through Conditional Access

Which solution should you implement?

A) Enable JIT VM access on all VMs  
B) Deploy Azure Bastion and remove public IPs from VMs  
C) Configure Azure Firewall with DNAT rules  
D) Implement Azure Private Link  

<details>
<summary><b>Answer</b></summary>

**B) Deploy Azure Bastion and remove public IPs from VMs** ✅

**Explanation**:

**Azure Bastion** is the correct solution because it:
- ✅ Allows VMs to operate **without public IP addresses**
- ✅ Provides **browser-based access** through Azure portal
- ✅ Supports **MFA enforcement** via Conditional Access policies
- ✅ Provides secure RDP/SSH connectivity over TLS (port 443)

**Why other options are incorrect**:

**JIT VM access** ❌
- Still **requires public IP addresses** on VMs
- Does not provide browser-based access
- Does not natively enforce MFA at connection time

**Azure Firewall with DNAT rules** ❌
- Would still expose public IPs (on the Firewall)
- Does not provide browser-based access
- Adds complexity without meeting requirements

**Azure Private Link** ❌
- Used for accessing Azure PaaS services over private endpoints
- Not designed for VM RDP/SSH access
- Does not provide browser-based management interface

</details>

---

## Summary

Azure Bastion is the **premier solution** for secure remote access to Azure VMs when you need:
- ✅ No public IP exposure on VMs
- ✅ MFA enforcement before network access
- ✅ TLS-encrypted browser-based connectivity
- ✅ Support for both RDP and SSH
- ✅ Fully managed PaaS service

It eliminates the need for jump boxes, VPN configurations, and public IP addresses while providing enterprise-grade security through Azure AD integration and Conditional Access policies.
