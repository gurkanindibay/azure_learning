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

> **See also**: [WAF custom rules](./azure-network-security-services-comparison.md#23-azure-web-application-firewall-waf) for details on WAF custom rule types (match rules and rate limit rules).

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
> **See also**: [NSG overview](../guides/00-networking-fundamentals.md#26-network-security-groups-nsg) for NSG capabilities and limitations

## References

- [Azure Firewall Policy rule sets](https://learn.microsoft.com/en-us/azure/firewall/policy-rule-sets)
- [Azure Firewall Policy overview](https://learn.microsoft.com/en-us/azure/firewall-manager/policy-overview)
- [Azure Firewall known issues](https://learn.microsoft.com/en-us/azure/firewall/firewall-known-issues)
- [What is Azure Firewall?](https://learn.microsoft.com/en-us/azure/firewall/overview)
- [Azure Firewall FQDN filtering in network rules](https://learn.microsoft.com/en-us/azure/firewall/fqdn-filtering-network-rules)

---

**Domain**: Design Infrastructure Solutions
