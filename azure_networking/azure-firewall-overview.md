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

## References

- [Azure Firewall Policy rule sets](https://learn.microsoft.com/en-us/azure/firewall/policy-rule-sets)
- [Azure Firewall Policy overview](https://learn.microsoft.com/en-us/azure/firewall-manager/policy-overview)

---

**Domain**: Design Infrastructure Solutions
