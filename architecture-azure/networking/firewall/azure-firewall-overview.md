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

1. **DNAT Rules** - Destination Network Address Translation rules
2. **Network Rules** - Layer 3/4 filtering rules
3. **Application Rules** - Layer 7 (FQDN-based) filtering rules

Rule processing follows this priority order:
1. DNAT rules are processed first
2. Network rules are processed second
3. Application rules are processed last

Within each rule type, rules are processed by priority (lower number = higher priority).

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

## References

- [Azure Firewall Policy rule sets](https://learn.microsoft.com/en-us/azure/firewall/policy-rule-sets)
- [Azure Firewall Policy overview](https://learn.microsoft.com/en-us/azure/firewall-manager/policy-overview)
- [Azure Firewall known issues](https://learn.microsoft.com/en-us/azure/firewall/firewall-known-issues)
- [What is Azure Firewall?](https://learn.microsoft.com/en-us/azure/firewall/overview)

---

**Domain**: Design Infrastructure Solutions
