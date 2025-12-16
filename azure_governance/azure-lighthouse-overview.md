# Azure Lighthouse Overview

## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Azure Delegated Resource Management](#azure-delegated-resource-management)
  - [Managing Tenant vs Customer Tenant](#managing-tenant-vs-customer-tenant)
  - [Logical Projection](#logical-projection)
- [Benefits](#benefits)
- [Capabilities](#capabilities)
- [Supported Scenarios](#supported-scenarios)
  - [Service Provider Scenarios](#service-provider-scenarios)
  - [Enterprise Scenarios](#enterprise-scenarios)
- [Cross-Tenant Management Experiences](#cross-tenant-management-experiences)
  - [Centralized Log Collection Across Multiple Tenants](#centralized-log-collection-across-multiple-tenants)
- [Onboarding Customers](#onboarding-customers)
  - [ARM Template Onboarding](#arm-template-onboarding)
  - [Azure Marketplace Offers](#azure-marketplace-offers)
  - [Onboarding Scope Levels](#onboarding-scope-levels)
- [Authorization and RBAC](#authorization-and-rbac)
  - [Supported Roles](#supported-roles)
  - [Eligible Authorizations](#eligible-authorizations)
- [Security Best Practices](#security-best-practices)
- [Azure Lighthouse vs Other Solutions](#azure-lighthouse-vs-other-solutions)
- [Pricing and Availability](#pricing-and-availability)
- [Limitations](#limitations)
- [Practice Questions](#practice-questions)

## Overview

Azure Lighthouse enables **multi-tenant management** with scalability, higher automation, and enhanced governance across resources. It allows service providers and enterprises to manage resources across multiple Microsoft Entra tenants from a single managing tenant.

**Key Value Proposition:**
- Service providers can manage customer Azure resources without switching tenants
- Enterprises with multiple tenants can centralize management operations
- Customers maintain full control and visibility over delegated access

```
┌─────────────────────────────────────────────────────────────────┐
│                    Managing Tenant                               │
│                 (Service Provider/Central IT)                    │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   User A     │  │   User B     │  │   Group C    │           │
│  │  (Reader)    │  │ (Contributor)│  │   (Owner)    │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
            Azure Delegated Resource Management
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Customer Tenant A          │ Customer Tenant B                  │
│ ┌───────────────────────┐  │ ┌───────────────────────┐         │
│ │ Delegated Subscription │  │ │ Delegated Resource    │         │
│ │ or Resource Groups     │  │ │ Groups                │         │
│ └───────────────────────┘  │ └───────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Azure Delegated Resource Management

Azure delegated resource management is the core mechanism of Azure Lighthouse. It allows:

- **Logical projection** of resources from customer tenant to managing tenant
- Users in managing tenant work on resources **without switching contexts**
- No need for guest accounts in customer tenants
- All actions logged in customer's Activity Log

| Aspect | Description |
|--------|-------------|
| **Access Model** | Users access resources through their own tenant credentials |
| **Authentication** | Azure Resource Manager validates delegation via registration resources |
| **Authorization** | Based on role assignments defined during onboarding |
| **Auditing** | All activity logged in customer's tenant Activity Log |

### Managing Tenant vs Customer Tenant

| Tenant Type | Description | Examples |
|-------------|-------------|----------|
| **Managing Tenant** | The tenant that performs management operations | Service provider's tenant, Central IT tenant |
| **Customer/Managed Tenant** | The tenant that delegates resources | Customer's production tenant, Subsidiary's tenant |

### Logical Projection

Azure Lighthouse creates a **logical projection** of resources from the customer tenant to the managing tenant:

```
Customer Tenant (contoso.com)
├── Subscription: Prod-001
│   ├── RG-WebApp
│   └── RG-Database
│
│   Registration Definition ────┐
│   Registration Assignment ────┤
│                               │
└──────────────────────────────┘
                                │
                                ↓ (Logical Projection)
Managing Tenant (msp.com)       │
├── My Customers Page ──────────┘
│   └── View: contoso.com
│       ├── Subscription: Prod-001
│       │   ├── RG-WebApp
│       │   └── RG-Database
```

**Key Points:**
- No data or resources are physically moved
- Access flows **only** from managing tenant to customer tenant
- Customer can revoke access at any time

## Benefits

### For Service Providers

| Benefit | Description |
|---------|-------------|
| **Management at Scale** | Manage multiple customers from single tenant |
| **Single Sign-On** | Use own credentials to access all customer resources |
| **Unified Tooling** | Use same APIs, CLI, and tools across all customers |
| **Granular Access** | Define specific permissions per customer |
| **Reduced Complexity** | No need for separate accounts per customer |

### For Customers

| Benefit | Description |
|---------|-------------|
| **Full Visibility** | See all service provider actions in Activity Log |
| **Precise Control** | Define exactly which resources are delegated |
| **Easy Revocation** | Remove access at any time |
| **No Account Overhead** | No guest accounts to manage |
| **Compliance** | Maintain audit trail and compliance |

### For Enterprises

| Benefit | Description |
|---------|-------------|
| **Centralized Management** | Single team manages resources across tenants |
| **Consistent Governance** | Apply uniform policies across acquisitions |
| **Simplified Operations** | Reduce tenant switching and context changes |
| **Scalable Architecture** | Handle growing number of tenants efficiently |

## Capabilities

Azure Lighthouse provides four main capabilities:

### 1. Azure Delegated Resource Management

```bash
# Users in managing tenant can directly access customer resources
# Example: Listing VMs in delegated subscription

az vm list \
  --subscription "Customer-Subscription-ID" \
  --output table

# Works seamlessly without tenant switching
```

### 2. Azure Portal Experiences

**My Customers Page (Managing Tenant View):**
- View all customers with delegated resources
- Navigate directly to customer subscriptions
- See aggregated view across customers

**Service Providers Page (Customer View):**
- View all service providers with access
- See delegated scopes and permissions
- Manage and revoke delegations

### 3. ARM Template Deployment

```bash
# Onboard customer using ARM template
az deployment sub create \
  --name "lighthouse-onboarding" \
  --location "eastus" \
  --template-uri "https://raw.githubusercontent.com/Azure/Azure-Lighthouse-samples/master/templates/delegated-resource-management/subscription/subscription.json" \
  --parameters "subscription.parameters.json"
```

### 4. Managed Service Offers (Azure Marketplace)

- Publish public or private offers
- Customers purchase/accept to onboard
- Automated onboarding process

## Supported Scenarios

### Service Provider Scenarios

| Scenario | Description |
|----------|-------------|
| **Managed Services** | MSPs managing multiple customer environments |
| **Consulting Services** | Consultants needing temporary access |
| **Security Operations** | SOC teams monitoring customer security |
| **DevOps Services** | Managing CI/CD pipelines across customers |
| **Cloud Migration** | Helping customers migrate to Azure |

**Example: Managed Security Provider**

```
MSP Tenant (security-msp.com)
│
├── Security Analysts Group ──────────┬──────────────┐
│   (Security Reader role)            │              │
│                                     ↓              ↓
│                              Customer A      Customer B
│                              (Financial)     (Healthcare)
│
├── Incident Response Group ──────────┬──────────────┐
│   (Contributor role)                │              │
│                                     ↓              ↓
│                              Customer A      Customer B
│                              (Security RG)   (Security RG)
```

### Enterprise Scenarios

| Scenario | Description |
|----------|-------------|
| **Multi-Tenant Organization** | Managing acquired companies |
| **Subsidiary Management** | Central IT managing subsidiaries |
| **Regional Compliance** | Meeting regional data residency requirements |
| **Development Isolation** | Separate dev/test tenants |

**Example: Enterprise with Acquisitions**

```
Parent Company Tenant (parentco.com)
│
├── Central Platform Team ────────────┬─────────────────┐
│   (Platform management)             │                 │
│                                     ↓                 ↓
│                              Acquired Co A     Acquired Co B
│                              (subsidiary1.com) (subsidiary2.com)
│
├── Security Team ────────────────────┬─────────────────┐
│   (Security monitoring)             │                 │
│                                     ↓                 ↓
│                              All Subscriptions  All Subscriptions
```

## Cross-Tenant Management Experiences

Azure Lighthouse enables cross-tenant management for many Azure services:

### Supported Services

| Service Category | Services |
|-----------------|----------|
| **Compute** | Azure Arc-enabled servers, Virtual Machines, AKS |
| **Security** | Microsoft Defender for Cloud, Microsoft Sentinel |
| **Monitoring** | Azure Monitor, Log Analytics |
| **Management** | Azure Policy, Azure Automation, Azure Backup |
| **Networking** | Azure Virtual Network, Azure Firewall |
| **Identity** | Azure AD (limited) |

### Service-Specific Capabilities

**Microsoft Defender for Cloud:**
```
Managing Tenant
│
├── View unified security posture across all customers
├── Apply security policies at scale
├── Monitor compliance across customer tenants
└── Respond to security alerts centrally
```

**Azure Arc:**
```
Managing Tenant
│
├── Manage hybrid servers across customers
├── Apply consistent policies to on-premises servers
├── GitOps configuration for Kubernetes clusters
└── Unified management of multi-cloud resources
```

**Azure Policy:**
```
Managing Tenant
│
├── Deploy policies to customer subscriptions
├── Monitor compliance across tenants
├── Remediate non-compliant resources
└── Enforce governance standards
```

### Centralized Log Collection Across Multiple Tenants

One of the most powerful use cases for Azure Lighthouse is **collecting logs from virtual machines across multiple subscriptions and tenants** into a single Log Analytics workspace.

**Scenario: Multi-Subscription Windows Security Event Collection**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CENTRALIZED LOG COLLECTION WITH LIGHTHOUSE               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Managing Tenant (Central Operations)                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │          Central Log Analytics Workspace                     │    │   │
│  │  │          (Receives logs from all VMs)                        │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                              ▲                                        │   │
│  │                              │                                        │   │
│  │           ┌──────────────────┼──────────────────┐                   │   │
│  │           │                  │                  │                    │   │
│  └───────────┼──────────────────┼──────────────────┼────────────────────┘   │
│              │                  │                  │                         │
│  ┌───────────▼─────┐ ┌─────────▼────────┐ ┌──────▼────────────┐            │
│  │ Tenant A        │ │ Tenant B         │ │ Tenant C          │            │
│  │ Subscription 1  │ │ Subscription 2   │ │ Subscription 3    │            │
│  │ Subscription 2  │ │                  │ │ Subscription 4    │            │
│  │                 │ │                  │ │ Subscription 5    │            │
│  │ ┌────┐ ┌────┐  │ │ ┌────┐ ┌────┐   │ │ ┌────┐ ┌────┐     │            │
│  │ │ VM │ │ VM │  │ │ │ VM │ │ VM │   │ │ │ VM │ │ VM │     │            │
│  │ └────┘ └────┘  │ │ └────┘ └────┘   │ │ └────┘ └────┘     │            │
│  └─────────────────┘ └─────────────────┘ └───────────────────┘            │
│                                                                              │
│  Each tenant delegates subscriptions to managing tenant via Lighthouse      │
│  Log Analytics agent installed from central workspace collects events       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Why Azure Lighthouse is the Correct Solution:**

| Requirement | How Lighthouse Addresses It |
|-------------|----------------------------|
| Collect from multiple subscriptions | Connect to different tenants from single pane |
| Different Microsoft Entra tenants | Cross-tenant management without guest accounts |
| Single Log Analytics workspace | Centralized workspace in managing tenant |
| Install monitoring agents | Deploy agents from central location |
| Windows security events | Full Azure Monitor integration |

**Implementation Steps:**

1. **Onboard each tenant's subscriptions** to Azure Lighthouse
2. **Create a central Log Analytics workspace** in the managing tenant
3. **Install Azure Monitor Agent** on VMs across all delegated subscriptions
4. **Configure Data Collection Rules** to collect Windows security events
5. **Query logs centrally** from the single workspace

```bash
# From managing tenant - list all delegated VMs across tenants
az vm list --query "[].{Name:name, Sub:id}" --output table

# Deploy Azure Monitor Agent to VMs in delegated subscription
az vm extension set \
  --resource-group "RG-VMs" \
  --vm-name "VM-01" \
  --name "AzureMonitorWindowsAgent" \
  --publisher "Microsoft.Azure.Monitor" \
  --subscription "Delegated-Subscription-ID"
```

**Why NOT These Alternatives:**

| Alternative | Why It Doesn't Work |
|-------------|---------------------|
| **Azure Event Grid** | Event Grid is a messaging service for event-driven architectures. It triggers integrations based on events but cannot collect VM logs across tenants |
| **Azure Purview (Microsoft Purview)** | Purview is for data governance, security, and management across your data estate. It does not configure or collect logs from VMs |
| **Direct Log Analytics connection** | Without Lighthouse, you cannot manage VMs in different tenants from a single location |

## Onboarding Customers

### ARM Template Onboarding

**Step 1: Prepare Parameters File**

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "mspOfferName": {
      "value": "Contoso Managed Services"
    },
    "mspOfferDescription": {
      "value": "Managed services offering for Contoso customers"
    },
    "managedByTenantId": {
      "value": "<managing-tenant-id>"
    },
    "authorizations": {
      "value": [
        {
          "principalId": "<group-or-user-id>",
          "roleDefinitionId": "acdd72a7-3385-48ef-bd42-f606fba81ae7",
          "principalIdDisplayName": "Support Team (Reader)"
        },
        {
          "principalId": "<group-or-user-id>",
          "roleDefinitionId": "b24988ac-6180-42a0-ab88-20f7382dd24c",
          "principalIdDisplayName": "Operations Team (Contributor)"
        }
      ]
    }
  }
}
```

**Step 2: Deploy Template**

```bash
# Deploy at subscription scope
az deployment sub create \
  --name "lighthouse-deployment" \
  --location "eastus" \
  --template-file "subscription.json" \
  --parameters @subscription.parameters.json

# Deploy at resource group scope
az deployment group create \
  --name "lighthouse-deployment" \
  --resource-group "RG-WebApp" \
  --template-file "rg.json" \
  --parameters @rg.parameters.json
```

**Step 3: Verify Delegation**

```bash
# In managing tenant - list delegations
az managedservices assignment list \
  --subscription "Customer-Subscription-ID"

# In customer tenant - view service providers
az managedservices definition list
```

### Azure Marketplace Offers

| Offer Type | Visibility | Use Case |
|------------|------------|----------|
| **Public** | All Azure customers | General managed services |
| **Private** | Specific customers only | Custom service agreements |

**Publishing Process:**
1. Create offer in Partner Center
2. Define plans with authorizations
3. Submit for certification
4. Customer accepts offer → automatic onboarding

### Onboarding Scope Levels

| Scope | Description | Use Case |
|-------|-------------|----------|
| **Subscription** | Entire subscription delegated | Full management |
| **Resource Group** | Specific resource groups delegated | Partial management |
| **Multiple Resource Groups** | Several RGs in one deployment | Targeted access |

```
Customer Subscription (Prod-001)
│
├── RG-WebApp ──────────── Delegated to MSP
├── RG-Database ────────── Delegated to MSP
├── RG-Network ─────────── Delegated to MSP
├── RG-Compliance ──────── NOT Delegated (internal only)
└── RG-Finance ─────────── NOT Delegated (sensitive data)
```

> **Note:** You cannot onboard an entire management group in one deployment. Use Azure Policy to onboard subscriptions within a management group.

## Authorization and RBAC

### Supported Roles

Azure Lighthouse supports most Azure built-in roles with some restrictions:

**✅ Supported Roles:**

| Role | Use Case |
|------|----------|
| Reader | View-only access |
| Contributor | Full resource management (no RBAC) |
| Virtual Machine Contributor | VM-specific management |
| Storage Account Contributor | Storage management |
| Network Contributor | Network management |
| Security Reader | Security monitoring |
| Log Analytics Reader/Contributor | Monitoring access |
| Managed Services Registration Assignment Delete Role | Remove delegations |

**❌ Not Supported:**

| Role | Reason |
|------|--------|
| Owner | Security risk - full control including RBAC |
| User Access Administrator | Can modify access permissions |
| Roles with DataActions | Data plane access not supported |
| Classic subscription admin roles | Legacy roles |

### Eligible Authorizations

Eligible authorizations use Azure AD Privileged Identity Management (PIM) for just-in-time access:

```
Managing Tenant
│
├── Regular Authorization ────────────────────────┐
│   (Permanent Reader access)                     │
│                                                 ↓
│                                          Always Active
│
├── Eligible Authorization ───────────────────────┐
│   (Contributor when activated)                  │
│                                                 ↓
│                                          Must Elevate
│                                          (Time-limited)
```

**Benefits:**
- Minimize standing privileged access
- Audit elevation requests
- Require justification for elevated access
- Time-bound elevated permissions

**Requirements:**
- Microsoft Entra ID P2 license required
- Must define approvers (optional)

## Security Best Practices

### 1. Require Multi-Factor Authentication

```
Managing Tenant Configuration
│
├── Enforce MFA for all users
├── Apply Conditional Access policies
└── Note: Customer tenant policies don't apply to
    managing tenant users accessing delegated resources
```

### 2. Use Principle of Least Privilege

```
✅ Best Practice:
├── Assign Reader role for monitoring-only scenarios
├── Assign specific roles (VM Contributor) instead of Contributor
├── Use eligible authorizations for elevated access
└── Assign to groups, not individual users

❌ Avoid:
├── Assigning Contributor when Reader is sufficient
├── Using same permissions for all customers
└── Assigning directly to users instead of groups
```

### 3. Use Groups for Authorization

```json
// Good: Assign to group
{
  "principalId": "<security-group-id>",
  "roleDefinitionId": "acdd72a7-3385-48ef-bd42-f606fba81ae7",
  "principalIdDisplayName": "Support Team"
}

// Avoid: Assign to individual user
{
  "principalId": "<user-id>",
  "roleDefinitionId": "acdd72a7-3385-48ef-bd42-f606fba81ae7",
  "principalIdDisplayName": "John Doe"
}
```

### 4. Monitor Activity Logs

```bash
# Customer can view all service provider activity
az monitor activity-log list \
  --subscription "Customer-Subscription-ID" \
  --query "[?authorization.action]" \
  --output table

# Filter for managing tenant activity
az monitor activity-log list \
  --subscription "Customer-Subscription-ID" \
  --query "[?claims.managedByTenantId]"
```

### 5. Implement Conditional Access

| Policy | Description |
|--------|-------------|
| **MFA Required** | Require MFA for all access |
| **Compliant Devices** | Require managed devices |
| **Location-Based** | Restrict access by location |
| **Risk-Based** | Block high-risk sign-ins |

## Azure Lighthouse vs Other Solutions

| Feature | Azure Lighthouse | B2B Guest Access | AOBO (CSP) |
|---------|-----------------|------------------|------------|
| **Account Required** | No guest account needed | Guest account in each tenant | Admin Agent role |
| **Granular Permissions** | Yes, any built-in role | Yes, RBAC | No, full admin access |
| **Scale** | Unlimited customers | Management overhead per tenant | Limited to CSP customers |
| **Customer Visibility** | Full activity logging | Standard audit logs | Limited visibility |
| **Access Revocation** | Instant, customer-controlled | Remove guest account | Remove CSP relationship |
| **Multi-Tenant Tools** | Built-in (My Customers page) | Manual tenant switching | Partner Center |

### When to Use Each

| Solution | Best For |
|----------|----------|
| **Azure Lighthouse** | MSPs, cross-tenant enterprise management, consulting |
| **B2B Guest** | Collaboration, project-based access |
| **AOBO** | CSP partners managing customer subscriptions |

## Pricing and Availability

| Aspect | Details |
|--------|---------|
| **Cost** | Free - no additional charges |
| **Availability** | All Azure regions (public cloud) |
| **National Clouds** | Supported within each national cloud |
| **Cross-Cloud** | Cannot delegate across cloud boundaries |

## Limitations

### Delegation Limitations

| Limitation | Description |
|------------|-------------|
| **No Management Group Delegation** | Cannot delegate entire management group |
| **No Cross-Cloud** | Cannot delegate between national clouds |
| **No Owner Role** | Owner role cannot be assigned |
| **No DataActions** | Roles with data plane access not supported |

### Service Limitations

| Service | Limitation |
|---------|------------|
| **Azure AD** | Limited to certain operations |
| **Backup Vault Workloads** | Some workloads not fully supported |
| **Azure Kubernetes Service** | Some features require direct access |

### Operational Limitations

| Limitation | Description |
|------------|-------------|
| **Conditional Access** | Customer policies don't apply to managing tenant users |
| **Activity Log Retention** | Standard 90-day retention in customer tenant |
| **Nested Groups** | May have delayed access propagation |

## Practice Questions

### Question 1: Centralized Log Collection from Multiple Tenants

**Scenario:**
You have five Azure subscriptions. Each subscription is linked to a separate Microsoft Entra tenant and contains virtual machines that run Windows Server 2022.

You plan to collect Windows security events from the virtual machines and send them to a single Log Analytics workspace.

You need to recommend a solution that meets the following requirement:
- Collects event logs from multiple subscriptions across different tenants

**Question:**
What should you recommend?

**Options:**

1. **Azure Event Grid** ❌
   - Event Grid is a messaging service based on events
   - Used to trigger integrations between systems based on certain events
   - Cannot collect logs from VMs in different tenants

2. **Azure Lighthouse** ✅
   - Enables cross-tenant management from a single managing tenant
   - Connect to all five subscriptions across different tenants
   - Install Log Analytics agent from central workspace
   - Collect logs easily to a single workspace
   - No guest accounts needed in each tenant

3. **Azure Purview (Microsoft Purview)** ❌
   - Provides centralized control over data governance, security, and management
   - Works across Azure, other cloud providers, or on-premises data
   - Cannot configure log collection from VMs in different tenants

4. **Azure Monitor directly** ❌
   - Cannot manage resources across different tenants without Lighthouse
   - Would require separate configuration in each tenant

**Answer:** Azure Lighthouse

**Explanation:**
Azure Lighthouse enables you to connect to different tenants and manage resources from a single pane of glass. Using Lighthouse, you can delegate access from all five subscriptions (even though they're in different tenants), then install the Azure Monitor Agent from your central Log Analytics workspace and collect the Windows security events easily into a single location.

**References:**
- [Azure Event Grid Overview](https://learn.microsoft.com/en-us/azure/event-grid/overview)
- [Azure Lighthouse Overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Microsoft Purview Overview](https://learn.microsoft.com/en-us/purview/purview)

---

### Question 2: Cross-Tenant Access (Service Provider)

**Scenario:**
Contoso (a managed service provider) needs to manage Azure resources for three customers: Customer A, Customer B, and Customer C. They want to:
- View all customer resources from a single portal
- Use their own credentials without guest accounts
- Allow customers to audit all actions

**Question:**
Which solution should Contoso use?

**Options:**

1. **Create guest accounts in each customer tenant** ❌
   - Requires managing multiple accounts
   - Context switching between tenants
   - Doesn't scale well

2. **Azure Lighthouse with delegated resource management** ✅
   - Single sign-on with own credentials
   - My Customers page for unified view
   - Full activity logging in customer tenants
   - No guest accounts needed

3. **Request Owner access in each customer tenant** ❌
   - Owner role not supported in Lighthouse
   - Security risk
   - Doesn't address unified management

4. **Use Azure AD B2B collaboration** ❌
   - Requires guest accounts
   - More management overhead
   - Doesn't provide unified view

**Answer:** Azure Lighthouse with delegated resource management

---

### Question 3: Role Assignment

**Scenario:**
You are onboarding a customer to Azure Lighthouse. Your operations team needs to manage virtual machines, but should not have access to modify RBAC permissions or access data in storage accounts.

**Question:**
Which role should you assign?

**Options:**

1. **Owner** ❌
   - Not supported in Azure Lighthouse
   - Too many permissions

2. **Contributor** ❌
   - More permissions than needed
   - Can modify all resources

3. **Virtual Machine Contributor** ✅
   - Specific to VM management
   - Cannot modify RBAC
   - Cannot access storage data
   - Follows least privilege

4. **Reader** ❌
   - Cannot manage VMs (view only)
   - Insufficient permissions

**Answer:** Virtual Machine Contributor

---

### Question 4: Enterprise Multi-Tenant

**Scenario:**
Your enterprise has acquired two companies, each with their own Microsoft Entra tenant. You want your central IT team to manage all three tenants without:
- Creating accounts in each tenant
- Switching contexts constantly
- Losing audit capabilities

**Question:**
What is the recommended approach?

**Options:**

1. **Merge all tenants into one** ❌
   - Complex and risky
   - May violate compliance requirements
   - Disrupts existing operations

2. **Use Azure Lighthouse to delegate from acquired tenants** ✅
   - Central IT manages from parent tenant
   - No account creation needed
   - Full audit trail maintained
   - Quick to implement

3. **Create service accounts in each tenant** ❌
   - Management overhead
   - Security risk with shared accounts
   - Not recommended practice

4. **Use VPN connections between tenants** ❌
   - Doesn't address management challenge
   - Network connectivity ≠ management access

**Answer:** Use Azure Lighthouse to delegate from acquired tenants

---

### Question 5: Security Best Practice

**Scenario:**
Your managing tenant has 10 support engineers who need Reader access to customer resources. Occasionally, some engineers need Contributor access for incident response.

**Question:**
What is the most secure authorization configuration?

**Options:**

1. **Assign Contributor to all engineers permanently** ❌
   - Violates least privilege
   - Unnecessary standing access
   - Increases risk

2. **Assign Reader permanently, use eligible authorization for Contributor** ✅
   - Permanent access only for what's needed
   - Just-in-time elevated access
   - Requires justification for elevation
   - Follows security best practices

3. **Create separate accounts for Contributor access** ❌
   - Management overhead
   - Doesn't leverage PIM benefits
   - Not recommended

4. **Assign Reader to a group, Contributor to individuals** ❌
   - Still has standing Contributor access
   - Difficult to audit individual access

**Answer:** Assign Reader permanently, use eligible authorization for Contributor

---

### Question 6: Onboarding Scope

**Scenario:**
A customer wants to delegate management of their web application resources but keep their financial system resources private. They have:
- Subscription: Prod-001
  - RG-WebApp
  - RG-WebAPI
  - RG-Database
  - RG-Finance (should remain private)

**Question:**
What should you onboard to Azure Lighthouse?

**Options:**

1. **The entire subscription** ❌
   - Would include RG-Finance
   - Violates customer requirement

2. **Individual resource groups: RG-WebApp, RG-WebAPI, RG-Database** ✅
   - Excludes RG-Finance
   - Meets customer requirement
   - Granular control

3. **The management group containing the subscription** ❌
   - Cannot onboard management groups directly
   - Would include all subscriptions

4. **Only RG-WebApp** ❌
   - Insufficient - database and API also needed
   - Would require separate management access

**Answer:** Individual resource groups: RG-WebApp, RG-WebAPI, RG-Database

---

## Summary

### Key Points

| Aspect | Key Information |
|--------|-----------------|
| **What** | Multi-tenant management solution |
| **How** | Azure delegated resource management |
| **Cost** | Free |
| **Scope** | Subscriptions or Resource Groups |
| **Security** | Full audit, customer-controlled access |
| **Roles** | Most built-in roles (except Owner) |

### When to Use Azure Lighthouse

| Use Case | Recommended |
|----------|-------------|
| MSP managing multiple customers | ✅ Yes |
| Enterprise with multiple tenants | ✅ Yes |
| Temporary consulting access | ✅ Yes |
| Single tenant management | ❌ Not needed |
| Data plane access needed | ❌ Not supported |

### Quick Reference Commands

```bash
# List delegations in customer subscription
az managedservices assignment list

# View service providers (customer view)
az managedservices definition list

# Remove delegation
az managedservices assignment delete --assignment <id>

# List all customers (managing tenant)
# Use Azure Portal → My customers
```

---

## References

- [Azure Lighthouse Overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Azure Lighthouse Architecture](https://learn.microsoft.com/en-us/azure/lighthouse/concepts/architecture)
- [Onboard a Customer](https://learn.microsoft.com/en-us/azure/lighthouse/how-to/onboard-customer)
- [Recommended Security Practices](https://learn.microsoft.com/en-us/azure/lighthouse/concepts/recommended-security-practices)
- [Azure Lighthouse Samples](https://github.com/Azure/Azure-Lighthouse-samples)
- [Cross-Tenant Management Experiences](https://learn.microsoft.com/en-us/azure/lighthouse/concepts/cross-tenant-management-experience)
- [Enterprise Scenarios](https://learn.microsoft.com/en-us/azure/lighthouse/concepts/enterprise)

---

**Last Updated:** December 2025
