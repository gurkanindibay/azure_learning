# Azure Firewall Overview

Azure Firewall is a managed, cloud-based network security service that protects your Azure Virtual Network resources. It's a fully stateful firewall as a service with built-in high availability and unrestricted cloud scalability.

## Azure Firewall Policy

Azure Firewall Policy is a top-level resource that contains security and operational settings for Azure Firewall. You can use policies to manage rule sets that Azure Firewall uses to filter traffic.

### Policy Hierarchy and Parent-Child Inheritance

Azure Firewall supports a hierarchical policy structure where policies can inherit rules from a parent policy. This enables centralized management of mandatory security rules across multiple firewall deployments.

#### Key Concepts

- **Parent Policy**: Contains mandatory/base rules that should apply to all child policies
- **Child Policy**: Inherits rules from parent and can add additional rules specific to its scope
- **Rule Inheritance**: Child policies automatically inherit all rules from their parent policy

#### Regional Requirement for Parent-Child Policies

> **⚠️ Important**: When using parent-child policy inheritance, **a parent policy must be in the same region as the child policy** to be linked. This is a Microsoft-enforced requirement.

This means:
- Parent policies are **logically global** in concept
- But **physically regional** in deployment for inheritance purposes
- Each region with child policies requires its own parent policy

### Exam Scenario: Parent Policy Deployment

**Question**: You have the following Azure Firewall policies:

| Policy Name | Region |
|-------------|--------|
| US-Central-Firewall-policy | Central US |
| US-East-Firewall-policy | East US |
| EU-Firewall-policy | West Europe |

You need to deploy a new Azure Firewall policy that will contain mandatory rules for all Azure Firewall deployments. The new policy will be configured as a parent policy for the existing policies.

**What is the minimum number of additional Azure Firewall policies you should create?**

- 0
- 1
- 2
- **3** ✅

**Answer**: **3 additional policies are required.**

**Explanation**:
While Azure Firewall policies are logically global, when using parent-child policy inheritance, Microsoft enforces that **a parent policy must be in the same region as the child policy** to be linked.

Given the existing policies:
- `US-Central-Firewall-policy` is in **Central US**
- `US-East-Firewall-policy` is in **East US**
- `EU-Firewall-policy` is in **West Europe**

To configure parent-child relationships for each existing regional policy, you need to create **one parent policy per region**:
1. Parent policy in **Central US** (for US-Central-Firewall-policy)
2. Parent policy in **East US** (for US-East-Firewall-policy)
3. Parent policy in **West Europe** (for EU-Firewall-policy)

This ensures each child policy can inherit mandatory rules from a parent policy located in the same region, complying with Azure's policy scoping requirements.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Azure Firewall Policy Hierarchy                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Central US              East US               West Europe              │
│   ┌──────────────┐       ┌──────────────┐      ┌──────────────┐         │
│   │Parent Policy │       │Parent Policy │      │Parent Policy │         │
│   │(Mandatory    │       │(Mandatory    │      │(Mandatory    │         │
│   │ Rules)       │       │ Rules)       │      │ Rules)       │         │
│   └──────┬───────┘       └──────┬───────┘      └──────┬───────┘         │
│          │                      │                     │                  │
│          ▼                      ▼                     ▼                  │
│   ┌──────────────┐       ┌──────────────┐      ┌──────────────┐         │
│   │US-Central-   │       │US-East-      │      │EU-Firewall-  │         │
│   │Firewall-     │       │Firewall-     │      │policy        │         │
│   │policy        │       │policy        │      │              │         │
│   │(Child)       │       │(Child)       │      │(Child)       │         │
│   └──────────────┘       └──────────────┘      └──────────────┘         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Policy Rule Sets

Azure Firewall Policy rule collections are organized into:

1. **DNAT Rules** - Destination Network Address Translation rules. DNAT translates and filters inbound internet traffic to your private subnet IP addresses. When a DNAT rule is configured, the firewall's public IP address receives the inbound traffic and translates it to the target private IP address, allowing external clients to reach internal resources without exposing them directly.
2. **Network Rules** - Layer 3/4 filtering rules
3. **Application Rules** - Layer 7 (FQDN-based) filtering rules

Rule processing follows this priority order:
1. DNAT rules are processed first
2. Network rules are processed second
3. Application rules are processed last

Within each rule type, rules are processed by priority (lower number = higher priority).

### Practice Question: Rule Processing Order

**Question**: Clarify the order in which rules/operations are executed in Azure Firewall, regardless of their collection priority, collection group, and policy inheritance. What is the correct sequence of application, network, and DNAT rules?

- A) Application Rules > Network Rules > DNAT Rules
- B) Application Rules > DNAT Rules > Network Rules
- C) DNAT Rules > Application Rules > Network Rules
- D) DNAT Rules > Network Rules > Application Rules ✅
- E) Network Rules > Application Rules > DNAT Rules

**Answer**: **D** ✅

**Explanation**:

In Azure Firewall, the order of processing rules is as follows: **DNAT rules** are processed first, followed by **Network rules**, and then **Application rules**. The processing order is **not affected** by the rule collection priority, rule collection group, or policy inheritance.

- **Option A is incorrect.** The correct order is not Application Rules > Network Rules > DNAT Rules. Application rules are processed last, not first.
- **Option B is incorrect.** The correct order is not Application Rules > DNAT Rules > Network Rules. Application rules are processed last.
- **Option C is incorrect.** The correct order is not DNAT Rules > Application Rules > Network Rules. Application rules are processed after network rules, not before.
- **Option D is correct.** ✅ DNAT Rules > Network Rules > Application Rules is the correct processing sequence.
- **Option E is incorrect.** The correct order is not Network Rules > Application Rules > DNAT Rules. DNAT rules are processed first.

> **Reference**: [Azure Firewall rule processing](https://learn.microsoft.com/en-us/azure/firewall/rule-processing)

## Threat Intelligence

Azure Firewall includes a threat intelligence-based filtering feature that can alert and/or deny traffic from/to known malicious IP addresses and domains.

### Threat Intelligence Modes

| Mode | Behavior |
|------|----------|
| **Off** | Threat intelligence is disabled |
| **Alert only** (default) | High-confidence alerts for malicious traffic |
| **Alert and Deny** | Traffic is alerted and blocked |

### Practice Question: Masking of Threat Intelligence Alerts

**Question**: You have safeguarded your Azure Virtual Network resources with Azure Firewall. You encounter an issue related to **masking of threat intelligence alerts**. Which of the following options can help you resolve this issue? (Select all that apply)

- A) When specifying a port, use "HTTPS" as the value for the "protocol" field.
- B) Set up outbound filtering for ports 80 and 443 by using application rules.
- C) Switch the threat intelligence mode to "Alert and Deny."
- D) Utilize authenticated SMTP relay services.
- E) Utilize IPv4 addresses exclusively.

**Answer**: **B and C** ✅

**Explanation**:

"Masking of threat intelligence alerts" can be resolved by implementing a mitigation strategy:

- **Option A is incorrect.** Using HTTPS as the port protocol value is not the correct mitigation strategy for this issue.
- **Option B is correct.** ✅ Creating outbound filtering for ports 80/443 using application rules resolves the masking of threat intelligence alerts.
- **Option C is correct.** ✅ Changing the threat intelligence mode to "Alert and Deny" can mitigate the issue by ensuring malicious traffic is both alerted and blocked.
- **Option D is incorrect.** Using authenticated SMTP relay services addresses a different Azure Firewall known issue (SMTP relay), not threat intelligence alert masking.
- **Option E is incorrect.** Using only IPv4 addresses addresses the "IPv6 not currently supported" known issue, not threat intelligence alert masking.

> **Reference**: [Azure Firewall known issues](https://learn.microsoft.com/en-us/azure/firewall/firewall-known-issues)

## Azure Firewall vs Azure WAF

Azure Firewall and Azure Web Application Firewall (WAF) serve different purposes and protect against different types of threats:

| Feature | Azure Firewall | Azure WAF |
|---------|---------------|-----------|
| **Type** | Network security service (L3/L4/L7) | Web application security (L7) |
| **Statefulness** | Fully stateful | N/A |
| **High availability** | Built-in | Depends on deployment |
| **Scalability** | Unrestricted cloud scalability | Depends on SKU |
| **Threat intelligence** | Identifies/blocks known malicious IPs and domains | N/A |
| **OWASP CRS** | No | Yes — based on OWASP Core Rule Set |
| **SQL injection protection** | No | Yes |
| **Cross-site scripting (XSS) protection** | No | Yes |
| **Custom rules** | N/A | Match rules and Rate limit rules |

> **See also**: [WAF custom rules](./12-network-security-services-comparison.md#23-azure-web-application-firewall-waf) for details on WAF custom rule types (match rules and rate limit rules).

### Practice Question: Describing Azure Firewall

**Scenario**: "Wheeler Car Dealership" is a company based in Sydney, Australia, that specializes in buying and selling automobiles. They have hired you as an experienced consultant to lead a team session where you will explain the Azure Firewall concept. During the session, you'll need to describe Azure Firewall clearly.

**Question**: Select **two** statements that correctly describe Azure Firewall.

- A) Azure Firewall is a fully stateful service with built-in high availability and unrestricted cloud scalability.
- B) Azure Firewall utilizes the Core Rule Set (CRS) the Open Web Application Security Project (OWASP) developed.
- C) Azure Firewall can identify and block traffic from or to known malicious IP addresses and domains. Additionally, it can generate alerts to notify you of such activities.
- D) Azure Firewall is a security feature that safeguards against SQL injection and cross-site scripting attacks, two common web application security vulnerabilities.

**Answer**: **A and C** ✅

**Explanation**:

- **Option A is correct.** ✅ Azure Firewall is a fully stateful firewall service with built-in high availability and unrestricted cloud scalability.
- **Option B is incorrect.** Azure Firewall is not based on the Core Rule Set (CRS) from the Open Web Application Security Project (OWASP). The OWASP CRS is used by **Azure WAF (Web Application Firewall)**.
- **Option C is correct.** ✅ Azure Firewall can alert and deny traffic from or to known malicious IP addresses and domains through its threat intelligence feature.
- **Option D is incorrect.** Protection against common web vulnerabilities such as SQL injection and cross-site scripting is a feature of **Azure WAF**, not Azure Firewall.

> **Key Distinction**: Azure Firewall is a cloud-native **network security** service that provides intelligent threat protection for cloud workloads. Azure WAF provides centralized protection against common **web application** exploits and vulnerabilities.

> **Reference**: [What is Azure Firewall? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/firewall/overview)

## Azure Firewall vs NSG (Network Security Groups)

Azure Firewall and Network Security Groups (NSGs) are both network security tools, but they operate at different levels and have fundamentally different capabilities:

| Feature | Azure Firewall | NSG |
|---------|---------------|-----|
| **Type** | Managed, cloud-based network security service | Stateful packet filter |
| **OSI Layer** | L3, L4, and L7 | L3 and L4 |
| **FQDN-based filtering** | **Yes** — supports FQDN in application and network rules | **No** — cannot create rules based on domain names |
| **Threat intelligence** | Built-in threat intelligence filtering | No |
| **NAT support** | DNAT and SNAT | No |
| **Scope** | Centralized, VNet-level | Subnet or NIC level |
| **Rule basis** | IP, port, protocol, FQDN, URL, service tags | IP, port, protocol, service tags |
| **Cost** | Paid service (per hour + per GB processed) | Free |
| **Use case** | Centralized network security, internet edge protection | Micro-segmentation, subnet/NIC-level filtering |

> **Key Distinction**: NSGs filter traffic based on IP addresses, ports, and protocols only. Azure Firewall adds **FQDN-based filtering** (domain name resolution), **threat intelligence**, and **centralized policy management** — making it the right choice when you need to allow or block traffic based on domain names.

### Practice question: FQDN-based domain filtering — NSG or Azure Firewall?

**Scenario**: A system administrator at a large enterprise needs to block all data traffic to websites from their network, **except for specific domains** such as `www.getcloudskills.com` and `www.udemy.com`. He wants to know if he should use Network Security Groups (NSGs) to accomplish this.

**Question**: Should the administrator use NSGs to block all website traffic except for specific allowed domains?

- A) Yes
- B) No ✅

**Answer**: **No** ✅

**Explanation**:

A fully qualified domain name (FQDN) refers to the complete domain name of a host or IP address (e.g., `www.getcloudskills.com`). **Azure NSGs do not support creating rules based on FQDNs** — they can only filter traffic using IP addresses, ports, protocols, and service tags.

In this scenario, **Azure Firewall** is the correct solution because:

| Requirement | NSG | Azure Firewall |
|-------------|-----|----------------|
| Block all outbound web traffic | ✅ Can block by port (80/443) | ✅ Can block by port |
| Allow specific domains (FQDNs) | ❌ Cannot filter by domain name | ✅ **Application rules support FQDN filtering** |
| DNS-based resolution | ❌ Not supported | ✅ Resolves FQDNs using DNS |

**How Azure Firewall solves this:**
1. Create a **deny-all** application rule for outbound HTTP/HTTPS traffic
2. Create a higher-priority **allow** application rule with the specific FQDNs:
   - `www.getcloudskills.com`
   - `www.udemy.com`
3. Azure Firewall resolves these FQDNs via DNS and allows only matching traffic

> **Reference**: [Azure Firewall FQDN filtering](https://learn.microsoft.com/en-us/azure/firewall/fqdn-filtering-network-rules)
> **See also**: [NSG overview](./01-networking-fundamentals.md#26-network-security-groups-nsg) for NSG capabilities and limitations

## Azure Firewall Manager

**Azure Firewall Manager** is a centralized security management service that provides policy and route management for cloud-based security perimeters. It enables you to manage multiple Azure Firewall instances across regions and subscriptions from a single pane of glass.

### Key capabilities

| Capability | Description |
|-----------|-------------|
| **Centralized policy management** | Create and apply Azure Firewall policies across multiple firewalls |
| **Hierarchical policies** | Author global base (parent) policies and region-specific (child) policies |
| **Secured Virtual Hub** | Deploy Azure Firewall inside a Virtual WAN hub for traffic inspection |
| **Hub Virtual Network** | Deploy Azure Firewall in a standard hub VNet with user-managed routing |
| **Third-party SECaaS** | Integrate third-party Security-as-a-Service providers for internet traffic filtering |
| **Route management** | Centrally manage routes to secured hubs without manually setting up UDRs on spoke VNets |

### Deployment architectures

Azure Firewall Manager supports two network architecture types:

| Architecture | Description | Use case |
|-------------|-------------|----------|
| **Hub Virtual Network** | A standard Azure VNet with Azure Firewall deployed in it. Spoke VNets are peered to the hub. User-defined routes (UDRs) direct traffic through the firewall. | Traditional hub-spoke topology where you manage your own routing and connectivity |
| **Secured Virtual Hub** | An Azure Virtual WAN hub with Azure Firewall deployed inside it. Routing is automatically configured by Virtual WAN. | Large-scale, multi-region deployments where centralized security and simplified routing are needed |

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│             AZURE FIREWALL MANAGER — DEPLOYMENT ARCHITECTURES                    │
│                                                                                  │
│   Hub Virtual Network                    Secured Virtual Hub                     │
│   ┌─────────────────────┐               ┌─────────────────────┐                 │
│   │   Standard VNet     │               │  Virtual WAN Hub    │                 │
│   │  ┌───────────────┐  │               │  ┌───────────────┐  │                 │
│   │  │ Azure Firewall│  │               │  │ Azure Firewall│  │                 │
│   │  └───────┬───────┘  │               │  └───────┬───────┘  │                 │
│   │          │           │               │          │           │                 │
│   │  User-managed UDRs  │               │  Auto-managed routes │                 │
│   └──────────┼──────────┘               └──────────┼──────────┘                 │
│        ┌─────┴─────┐                         ┌─────┴─────┐                      │
│        │  VNet     │                         │  VNet     │                      │
│        │  Peering  │                         │  Conns    │                      │
│   ┌────┴──┐  ┌──┴────┐                 ┌────┴──┐  ┌──┴────┐                   │
│   │Spoke 1│  │Spoke 2│                 │Spoke 1│  │Spoke 2│                   │
│   └───────┘  └───────┘                 └───────┘  └───────┘                   │
│                                                                                  │
│   ✓ Full routing control                ✓ Simplified routing                    │
│   ✓ Any VNet topology                   ✓ Integrated VPN/ER                     │
│   ✗ Manual UDR management               ✓ Azure Firewall Manager native         │
│   ✗ No built-in branch connectivity     ✓ Branch connectivity built-in          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### How Firewall Manager works with policies

Azure Firewall Manager uses **Azure Firewall Policies** (not classic rules) to configure firewalls. A single policy can be applied to multiple firewalls, enabling consistent security across regions.

| Concept | Relationship |
|---------|-------------|
| **Firewall Manager** | Management plane — creates, assigns, and monitors policies |
| **Firewall Policy** | Configuration artifact — contains rule collections (DNAT, Network, Application) |
| **Azure Firewall** | Enforcement point — evaluates traffic against assigned policy |
| **Secured Virtual Hub** | Deployment model — Firewall inside a Virtual WAN hub |

> **Key distinction**: Azure Firewall Manager is the **management service**; Azure Firewall Policy is the **configuration object**. You use Firewall Manager to create and assign policies, but the policy itself is what contains the rules.

### Centralized management across regions

Firewall Manager enables centralized governance for organizations with Azure Firewalls in multiple regions:

1. **Create a base (parent) policy** with mandatory rules (e.g., deny known malicious IPs)
2. **Create region-specific (child) policies** that inherit from the parent and add local rules
3. **Assign policies** to firewalls in each region via Firewall Manager
4. **Monitor compliance** — Firewall Manager shows which firewalls have policies applied

> **Note**: Parent-child policy inheritance requires the parent and child policies to be in the **same region**. See [Policy Hierarchy and Parent-Child Inheritance](#policy-hierarchy-and-parent-child-inheritance) above.

### Practice question: Centralized firewall management and secure hub

**Question**: Your organization wants to centralize the management of multiple Azure Firewalls across different regions. Additionally, there is a need to deploy an Azure Firewall inside a Virtual WAN hub for traffic inspection. Which of the following actions should you take to meet these requirements? (Select two)

- A) Implement Azure Firewall Manager policies. ✅
- B) Deploy Azure Firewall in a Virtual Network.
- C) Configure Azure Firewall with Premium SKU.
- D) Create a secure hub by deploying an Azure Firewall inside an Azure Virtual WAN hub. ✅

**Answer**: **A and D** ✅

**Explanation**:

- **Option A is correct.** ✅ Azure Firewall Manager allows centralized management of Azure Firewall instances across multiple regions and subscriptions. It provides a single point for creating and applying firewall policies to all managed firewalls.
- **Option B is incorrect.** Deploying Azure Firewall in a standard Virtual Network creates a hub virtual network deployment, but this does **not** address traffic inspection inside a Virtual WAN hub. This option addresses neither centralized management nor secure hub requirements.
- **Option C is incorrect.** Azure Firewall Premium SKU provides enhanced features (TLS inspection, IDPS, URL filtering, Web categories), but it does not address centralized management or secure hub deployment. SKU selection is independent of management approach.
- **Option D is correct.** ✅ For traffic inspection in a Virtual WAN hub, deploying Azure Firewall inside the hub creates a **Secured Virtual Hub**. This enables centralized traffic inspection for all traffic flowing through the hub (branch-to-internet, branch-to-VNet, VNet-to-internet, VNet-to-VNet).

> **See also**: [Secured Virtual Hub — Azure Virtual WAN](./10-azure-virtual-wan.md#8-secured-virtual-hub-azure-firewall-in-virtual-wan)

> **Reference**: [What is Azure Firewall Manager?](https://learn.microsoft.com/en-us/azure/firewall-manager/overview)
> **Reference**: [Azure Firewall Manager architecture options](https://learn.microsoft.com/en-us/azure/firewall-manager/vhubs-and-vnets)

## References

- [Azure Firewall Policy rule sets](https://learn.microsoft.com/en-us/azure/firewall/policy-rule-sets)
- [Azure Firewall Policy overview](https://learn.microsoft.com/en-us/azure/firewall-manager/policy-overview)
- [Azure Firewall known issues](https://learn.microsoft.com/en-us/azure/firewall/firewall-known-issues)
- [What is Azure Firewall?](https://learn.microsoft.com/en-us/azure/firewall/overview)
- [Azure Firewall FQDN filtering in network rules](https://learn.microsoft.com/en-us/azure/firewall/fqdn-filtering-network-rules)
- [What is Azure Firewall Manager?](https://learn.microsoft.com/en-us/azure/firewall-manager/overview)
- [Azure Firewall Manager architecture options](https://learn.microsoft.com/en-us/azure/firewall-manager/vhubs-and-vnets)

---

**Domain**: Design Infrastructure Solutions
