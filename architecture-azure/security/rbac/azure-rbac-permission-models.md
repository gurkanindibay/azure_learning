# Azure RBAC Permission Models

## Table of Contents

- [Overview](#overview)
- [Understanding Azure RBAC Actions](#understanding-azure-rbac-actions)
  - [What Are RBAC Actions?](#what-are-rbac-actions)
  - [Action Format and Structure](#action-format-and-structure)
  - [Actions vs DataActions](#actions-vs-dataactions)
  - [How Authorization Works](#how-authorization-works)
  - [Wildcards and NotActions](#wildcards-and-notactions)
  - [Built-in Roles = Predefined Action Bundles](#built-in-roles--predefined-action-bundles)
  - [Custom Roles](#custom-roles)
  - [Key Exam Tip: Action vs Role](#key-exam-tip-action-vs-role)
- [Management Plane vs Data Plane](#management-plane-vs-data-plane)
- [Permission Models Comparison](#permission-models-comparison)
  - [Service-Specific Access Policies](#service-specific-access-policies)
  - [Azure RBAC (Role-Based Access Control)](#azure-rbac-role-based-access-control)
- [The Contributor Role Security Problem](#the-contributor-role-security-problem)
  - [Why This Matters](#why-this-matters)
  - [How Azure RBAC Solves This](#how-azure-rbac-solves-this)
- [Azure Services Supporting RBAC Permission Model](#azure-services-supporting-rbac-permission-model)
- [Best Practices](#best-practices)
- [Practice Question: Multi-Tenant RBAC Role Assignments](#practice-question-multi-tenant-rbac-role-assignments)
- [Practice Question: Preventing Contributor Role Data Plane Access](#practice-question-preventing-contributor-role-data-plane-access)
- [Practice Question: Subscription Tenant Migration and Access Elevation](#practice-question-subscription-tenant-migration-and-access-elevation)
- [Practice Question: Azure AD Tenant Creation and User Management Permissions](#practice-question-azure-ad-tenant-creation-and-user-management-permissions)

## Overview

Azure provides two primary approaches for controlling access to resources:

1. **Service-Specific Access Policies** - Traditional model where each service manages its own access control
2. **Azure RBAC (Role-Based Access Control)** - Unified model using Azure's identity and access management

Understanding when to use each model is critical for implementing proper security separation, especially preventing privilege escalation scenarios.

## Understanding Azure RBAC Actions

### What Are RBAC Actions?

In Azure RBAC, **Actions** are the equivalent of **permissions** in traditional RBAC systems. They are the specific operations that Azure allows or denies on resources.

**Standard RBAC vs Azure RBAC Terminology:**

| Traditional RBAC | Azure RBAC |
|------------------|------------|
| Permission | Action |
| Role | Role (built-in or custom) |
| User/Group | Security Principal (user, group, service principal, managed identity) |
| Resource | Scope (subscription, resource group, resource) |

### Action Format and Structure

Azure RBAC actions follow a specific naming convention:

```
{Company}.{ProviderName}/{resourceType}/{action}
```

**Example Breakdown:**
```
Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action
│          │              │                    │
│          │              │                    └── Operation type
│          │              └── Resource path
│          └── Resource provider
└── Company (always Microsoft for Azure)
```

**Common Action Suffixes:**

| Suffix | Meaning | Example |
|--------|---------|--------|
| `/read` | Read/Get operations | `containers/read` |
| `/write` | Create/Update operations | `containers/write` |
| `/delete` | Delete operations | `containers/delete` |
| `/action` | Special operations | `generateUserDelegationKey/action` |
| `/*` | All operations on resource | `storageAccounts/*` |

### Actions vs DataActions

Azure separates permissions into two categories:

| Type | Scope | Description | Example |
|------|-------|-------------|--------|
| **Actions** | Control plane (management) | Managing Azure resources | `listkeys/action`, `generateUserDelegationKey/action` |
| **DataActions** | Data plane (data access) | Accessing data within resources | `blobs/read`, `blobs/write` |

**Why the Separation?**
- Allows granting management permissions without data access
- Example: `Contributor` role can manage storage accounts but cannot read blob data
- Enhances security through principle of least privilege

**Role Definition Example:**
```json
{
  "Name": "Storage Blob Data Reader",
  "Actions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/read",
    "Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action"
  ],
  "DataActions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read"
  ]
}
```

### How Authorization Works

When a user or service calls an Azure API, the authorization flow is:

```
User/Service calls API
        │
        ▼
┌───────────────────────────────────────┐
│ Azure Authorization Check:            │
│                                       │
│ 1. Does caller have role assignment   │
│    at this scope?                     │
│                                       │
│ 2. Does that role include the         │
│    required action?                   │
│                                       │
│ 3. If YES → Allow (200 OK)            │
│    If NO  → Deny (403 Forbidden)      │
└───────────────────────────────────────┘
```

**Example Authorization Flow:**
```csharp
// This API call requires:
// Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action
var key = await blobServiceClient.GetUserDelegationKeyAsync(...);

// Azure checks: Does the caller's assigned role include this action?
// - Storage Blob Data Reader → ✅ Includes action → Allowed
// - Reader                   → ❌ Missing action → 403 Forbidden
```

### Wildcards and NotActions

**Wildcards (`*`):**

Roles can use wildcards for broader permissions:

```
Microsoft.Storage/storageAccounts/*        // All actions on storage accounts
Microsoft.Storage/*/read                   // All read actions in Storage provider
*                                          // All actions (Owner role)
```

**NotActions (Exclusions):**

Roles can exclude specific actions:

```json
{
  "Actions": [
    "Microsoft.Storage/*"
  ],
  "NotActions": [
    "Microsoft.Storage/storageAccounts/delete"
  ]
}
```

This grants all Storage actions **except** delete.

**NotDataActions:**

Similarly, data actions can be excluded:

```json
{
  "DataActions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/*"
  ],
  "NotDataActions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/delete"
  ]
}
```

### Built-in Roles = Predefined Action Bundles

Built-in roles are collections of predefined actions that Microsoft has bundled for common use cases:

```
┌─────────────────────────────────────┐
│   Storage Blob Data Contributor     │  ← Built-in Role
├─────────────────────────────────────┤
│ Actions:                            │
│  • generateUserDelegationKey/action │
│                                     │
│ DataActions:                        │
│  • containers/blobs/read            │  ← Predefined Actions
│  • containers/blobs/write           │     (Permissions)
│  • containers/blobs/delete          │
│  • containers/blobs/move/action     │
│  • containers/blobs/add/action      │
└─────────────────────────────────────┘
```

**Role Assignment Formula:**

```
Role Assignment = Security Principal + Role Definition + Scope
                         │                   │            │
                      (WHO)              (WHAT)       (WHERE)
                                           │
                                    Collection of
                                      Actions
                                   (Permissions)
```

### Custom Roles

If built-in roles don't fit your needs, you can create custom roles with specific actions:

```json
{
  "Name": "Custom Blob Reader with Delegation",
  "Description": "Can read blobs and generate user delegation keys",
  "Actions": [
    "Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action"
  ],
  "NotActions": [],
  "DataActions": [
    "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read"
  ],
  "NotDataActions": [],
  "AssignableScopes": [
    "/subscriptions/{subscription-id}"
  ]
}
```

**Azure CLI to Create Custom Role:**
```bash
az role definition create --role-definition custom-role.json
```

### Key Exam Tip: Action vs Role

When exam questions ask **"which RBAC action is required?"**, they want the specific permission string:

- ✅ **Correct**: `Microsoft.Storage/storageAccounts/blobServices/generateUserDelegationKey/action`
- ❌ **Wrong**: "Storage Blob Data Reader" (this is a role name, not an action)

## Management Plane vs Data Plane

Azure resources have two distinct access planes:

| Plane | Description | Examples | Controlled By |
|-------|-------------|----------|---------------|
| **Management Plane** | Operations on the resource itself | Create, delete, configure resources | Azure RBAC (always) |
| **Data Plane** | Operations on data within the resource | Read secrets, send messages, query data | Access Policies OR Azure RBAC |

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure Resource                            │
├─────────────────────────────────────────────────────────────────┤
│  Management Plane (Azure RBAC)                                  │
│  ├── Create/Delete resource                                     │
│  ├── Configure settings                                         │
│  ├── Manage networking                                          │
│  └── View properties                                            │
├─────────────────────────────────────────────────────────────────┤
│  Data Plane (Access Policy OR Azure RBAC)                       │
│  ├── Read/Write data                                            │
│  ├── Execute operations                                         │
│  └── Access contents                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Permission Models Comparison

### Service-Specific Access Policies

Many Azure services historically used their own access policy models:

| Service | Access Policy Type | Configuration |
|---------|-------------------|---------------|
| **Key Vault** | Vault Access Policies | Per-identity permissions for keys, secrets, certificates |
| **Storage Account** | Shared Access Signatures (SAS), Access Keys | Token-based or key-based access |
| **Service Bus** | Shared Access Policies | Namespace or entity-level policies |
| **Event Hubs** | Shared Access Policies | Namespace or event hub-level policies |

**Characteristics of Access Policies:**
- ✅ Simple to configure for basic scenarios
- ✅ Service-specific granularity
- ❌ Users with management plane write access can grant themselves data plane access
- ❌ No separation between infrastructure admins and security admins
- ❌ Limited audit trail for permission changes
- ❌ Inconsistent model across services

### Azure RBAC (Role-Based Access Control)

Azure RBAC provides a unified permission model across all Azure services:

**Characteristics of Azure RBAC:**
- ✅ Clear separation of duties (management vs security administration)
- ✅ Only Owner and User Access Administrator can assign roles
- ✅ Consistent model across all Azure services
- ✅ Fine-grained built-in roles for each service
- ✅ Scope flexibility (subscription, resource group, resource, or object level)
- ✅ Full audit trail in Azure Activity Log
- ❌ More complex initial setup
- ❌ Requires understanding of RBAC concepts

## The Contributor Role Security Problem

### Why This Matters

The **Contributor** built-in role grants `*/write` permissions on resources, which includes the ability to modify resource configurations. When services use access policies for data plane authorization:

```
┌────────────────────────────────────────────────────────────────────┐
│  Access Policy Model - Security Risk                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User with Contributor Role                                        │
│  ├── Has Microsoft.{Service}/{resource}/write permission           │
│  └── Can modify resource properties INCLUDING...                   │
│       └── Access Policies ──► Grants self data plane access!       │
│                                                                    │
│  Example with Key Vault:                                           │
│  ├── Contributor has Microsoft.KeyVault/vaults/write               │
│  └── Can add access policy granting self Get/List secrets          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Real-World Scenario:**
1. DevOps engineer is assigned **Contributor** role to manage infrastructure
2. Using Access Policy model, they can grant themselves access to production secrets
3. No approval workflow or separation of duties
4. Security team has no control over who accesses sensitive data

### How Azure RBAC Solves This

With Azure RBAC, data plane access is controlled by role assignments, which can only be created by:
- **Owner** role
- **User Access Administrator** role
- Custom roles with `Microsoft.Authorization/roleAssignments/write` permission

```
┌────────────────────────────────────────────────────────────────────┐
│  Azure RBAC Model - Secure                                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  User with Contributor Role                                        │
│  ├── Has Microsoft.{Service}/{resource}/write permission           │
│  └── Can modify resource properties BUT...                         │
│       └── Cannot assign RBAC roles (requires Owner/UAA)            │
│                                                                    │
│  Data Plane Access Requires:                                       │
│  ├── Owner or User Access Administrator to assign role             │
│  └── Specific data plane role (e.g., Key Vault Secrets User)       │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Secure Scenario:**
1. DevOps engineer is assigned **Contributor** role to manage infrastructure
2. Security team (with **User Access Administrator**) controls data plane access
3. Clear separation of duties between infrastructure and security
4. Full audit trail of who granted access and when

## Azure Services Supporting RBAC Permission Model

| Service | RBAC Property/Setting | Data Plane Roles |
|---------|----------------------|------------------|
| **Key Vault** | `enableRbacAuthorization: true` | Key Vault Administrator, Secrets User, Crypto User, etc. |
| **Storage Account** | Default (no shared keys) | Storage Blob Data Reader/Contributor/Owner |
| **Service Bus** | Azure RBAC for data operations | Service Bus Data Receiver/Sender/Owner |
| **Event Hubs** | Azure RBAC for data operations | Event Hubs Data Receiver/Sender/Owner |
| **Cosmos DB** | Azure RBAC for data operations | Cosmos DB Data Reader/Contributor |
| **Azure SQL** | Azure AD authentication | db_datareader, db_datawriter, etc. |

### Enabling Azure RBAC for Key Vault

```bash
# Create new Key Vault with RBAC
az keyvault create \
  --name myKeyVault \
  --resource-group myResourceGroup \
  --enable-rbac-authorization true

# Update existing Key Vault to use RBAC
az keyvault update \
  --name myKeyVault \
  --enable-rbac-authorization true
```

### Enabling Azure RBAC for Storage Account

```bash
# Disable shared key access (enforces Azure AD/RBAC only)
az storage account update \
  --name mystorageaccount \
  --resource-group myResourceGroup \
  --allow-shared-key-access false
```

### Enabling Azure RBAC for Service Bus

```bash
# Service Bus uses RBAC by default for data operations
# Assign data plane roles
az role assignment create \
  --role "Azure Service Bus Data Sender" \
  --assignee user@contoso.com \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ServiceBus/namespaces/{namespace}
```

## Best Practices

### 1. Use Azure RBAC for New Deployments
- Enable Azure RBAC authorization for all services that support it
- Avoid legacy access policy models when possible

### 2. Implement Separation of Duties
| Role | Responsibility | Azure Role |
|------|---------------|------------|
| **Infrastructure Admin** | Deploy and configure resources | Contributor |
| **Security Admin** | Manage access to sensitive data | User Access Administrator |
| **Application** | Access data at runtime | Service-specific data role |

### 3. Apply Principle of Least Privilege
```bash
# Instead of broad access...
# ❌ Key Vault Administrator (full access)

# Use specific roles...
# ✅ Key Vault Secrets User (read secrets only)
# ✅ Key Vault Certificates Officer (manage certificates only)
# ✅ Key Vault Crypto User (use keys for crypto operations)
```

### 4. Use Scope Appropriately
```
Scope Hierarchy (most restrictive to least):
├── Individual Object (e.g., specific secret)
├── Resource (e.g., specific Key Vault)
├── Resource Group
└── Subscription
```

### 5. Audit Role Assignments Regularly
```bash
# List all role assignments for a resource
az role assignment list \
  --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault} \
  --output table
```

### 6. Understand Multi-Tenant RBAC Scope Limitations

#### Important: RBAC Assignments Are Tenant-Scoped

RBAC role assignments, including those at the management group level, are **scoped to a single Microsoft Entra tenant**. This means:

- Each tenant has its own separate management group hierarchy
- Role assignments in one tenant do not apply to resources in another tenant
- You cannot create a single RBAC assignment that spans multiple tenants

**Key Implication:**
In multi-tenant scenarios, you must create separate RBAC role assignments for each tenant to achieve consistent permissions across your organization.

## Practice Question: Multi-Tenant RBAC Role Assignments

**Scenario: Litware Inc. Case Study**

Litware Inc. has the following infrastructure:
- **Tenant 1:** `litware.com` with 10 subscriptions
- **Tenant 2:** `dev.litware.com` with 5 subscriptions

**Requirement:**
Network administrators must be granted the **Network Contributor** role across all virtual networks in both tenants. The solution should:
- Meet authentication and authorization requirements
- Use the minimum number of role assignments possible
- Apply RBAC at the management group level for efficiency

**Question:**
What is the minimum number of RBAC role assignments required?

**Options:**

1. **1** ❌ *Incorrect*
   - A single RBAC assignment cannot span multiple Microsoft Entra tenants, even when applied at the root management group level.

2. **2** ✅ *Correct*
   - **Explanation:** Since RBAC assignments are tenant-scoped, you need one assignment per tenant:
     - **Assignment 1:** Network Contributor role at the root management group of `litware.com` tenant
     - **Assignment 2:** Network Contributor role at the root management group of `dev.litware.com` tenant
   - Each assignment covers all subscriptions within its respective tenant's management group hierarchy.

3. **5** ❌ *Incorrect*
   - This would be required if you were assigning at the subscription level in dev.litware.com only, but management group-level assignments eliminate this need.

4. **10** ❌ *Incorrect*
   - This would be required if you were assigning at the subscription level in litware.com only, but management group-level assignments eliminate this need.

5. **15** ❌ *Incorrect*
   - This would be required if you were assigning at the subscription level for all subscriptions across both tenants, but management group-level assignments eliminate this need.

---

**Key Takeaways:**

1. **RBAC assignments are tenant-scoped:**
   - Each Microsoft Entra tenant requires its own separate role assignments
   - Management group hierarchies are isolated per tenant

2. **Management group benefits:**
   - Applying RBAC at the root management group level cascades permissions to all child subscriptions
   - Reduces the number of assignments needed within a single tenant
   - Cannot eliminate the need for multiple assignments across different tenants

3. **Formula for multi-tenant scenarios:**
   ```
   Minimum assignments = Number of tenants × 1 (when using root management group)
   ```

4. **Real-world application:**
   - Organizations with dev/test isolation in separate tenants
   - Mergers and acquisitions maintaining separate tenant structures
   - Partner organizations with managed service scenarios

## Practice Question: Preventing Contributor Role Data Plane Access

**Scenario:**
You are configuring an Azure service to prevent unauthorized users with Contributor role from granting themselves data plane access.

**Question:**
Which permission model should you implement?

**Options:**

1. **Service-specific access policy with deny assignments** ❌ *Incorrect*
   - When using access policy models, users with Contributor role can still grant themselves access. Deny assignments don't override this fundamental limitation.

2. **Access Policies with restricted permissions** ❌ *Incorrect*
   - Users with Contributor or any role that includes `Microsoft.{Service}/{resource}/write` permissions can grant themselves data plane access by modifying access policies.

3. **Access Policies with Azure AD authentication** ❌ *Incorrect*
   - Access policies allow users with Contributor role to modify them regardless of authentication method. This is a limitation of the access policy model itself.

4. **Azure RBAC** ✅ *Correct*
   - Azure RBAC restricts permission management to **Owner** and **User Access Administrator** roles, providing clear separation between security operations and administrative duties.

---

**Key Takeaway:**

When you need to prevent users with **Contributor** role from granting themselves data plane access to Azure resources, implement the **Azure RBAC permission model**. This model ensures that only users with **Owner** or **User Access Administrator** roles can assign data plane access, providing proper separation of duties between infrastructure management and security administration.

This applies to multiple Azure services including:
- Azure Key Vault
- Azure Storage Accounts
- Azure Service Bus
- Azure Event Hubs
- Azure Cosmos DB
- And others that support Azure RBAC for data plane operations

## Practice Question: Subscription Tenant Migration and Access Elevation

**Scenario:**
You have two Microsoft Entra tenants named `contoso.com` and `fabrikam.com`. Each tenant is linked to 50 Azure subscriptions. `contoso.com` contains two users named User1 and User2.

**Requirements:**
- Ensure that User1 can change the Microsoft Entra tenant linked to specific Azure subscriptions
- If an Azure subscription is linked to a new Microsoft Entra tenant, and no available Microsoft Entra accounts have full subscription-level permissions to the subscription, elevate the access of User2 to the subscription
- The solution must use the principle of least privilege

**Question:**
Which role should you assign to User2?

**Options:**

1. **Co-administrator** ❌ *Incorrect*
   - Co-administrator is a classic administrator role that offers management capabilities at the subscription level
   - However, it **cannot assign RBAC roles** and **does not persist across tenant migrations**
   - It does not meet the requirement of enabling User2 to elevate their own access or manage others

2. **Owner** ✅ *Correct*
   - The **Owner** role in Azure RBAC grants full access to all resources within a subscription, including the **ability to assign roles to others**
   - If assigned the Owner role, User2 can elevate access and delegate permissions, which directly satisfies the requirement
   - This solution aligns with the principle of least privilege, as User2 will have just enough access to manage permissions without being granted unnecessary broader administrative privileges across tenants

3. **Service administrator** ❌ *Incorrect*
   - Service administrator is a classic administrator role that can manage services and subscriptions
   - It **does not have full RBAC integration** and **cannot assign RBAC roles** to other users unless elevated through a global admin or directory-wide operation
   - It is insufficient for self-service elevation or assigning roles to others post-tenant migration

---

**Key Takeaways:**

1. **Tenant Migration Impact on Access:**
   - When an Azure subscription is transferred to a new Microsoft Entra tenant, existing RBAC role assignments may no longer have valid principals in the new tenant
   - This can result in a subscription with no accounts having full permissions

2. **Classic vs RBAC Roles for Tenant Migration:**

   | Role Type | Can Assign RBAC Roles | Persists Across Tenant Migration | Full RBAC Integration |
   |-----------|----------------------|----------------------------------|----------------------|
   | **Owner** | ✅ Yes | N/A (needs reassignment) | ✅ Yes |
   | **Service Administrator** | ❌ No (limited) | ❌ No | ❌ No |
   | **Co-administrator** | ❌ No | ❌ No | ❌ No |

3. **Global Administrator Access Elevation:**
   - A Global Administrator in Microsoft Entra ID can elevate their access to manage all Azure subscriptions and management groups in the tenant
   - This is done through the "Access management for Azure resources" setting in Entra ID properties
   - After elevation, the Global Admin receives the **User Access Administrator** role at the root scope

4. **Best Practice for Tenant Migration:**
   - Plan access recovery before migrating subscriptions to new tenants
   - Ensure at least one account will have Owner or elevated access post-migration
   - Document the recovery process for emergency scenarios

**References:**
- [Azure Built-in Roles - Owner](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#owner)
- [Classic Subscription Administrator Roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/classic-administrators)
- [Elevate Access for Global Administrators](https://learn.microsoft.com/en-us/azure/role-based-access-control/elevate-access-global-admin)
- [Associate or Change Azure Subscription Directory](https://learn.microsoft.com/en-us/entra/fundamentals/how-subscriptions-associated-directory)

## Practice Question: Azure AD Tenant Creation and User Management Permissions

**Scenario:**
You have an Azure subscription that contains the following users in an Microsoft Entra ID tenant named `contoso.onmicrosoft.com`:

| User | Role in contoso.onmicrosoft.com Tenant | Role in Azure Subscription |
|------|---------------------------------------|---------------------------|
| User1 | Global Administrator | N/A |
| User2 | User | Contributor |
| User3 | User | Owner |

User1 creates a new Microsoft Entra ID tenant named `external.contoso.onmicrosoft.com`.

**Question:**
You need to create new user accounts in `external.contoso.onmicrosoft.com`. 

**Solution:** You instruct User3 to create the user accounts.

Does this meet the goal?

**Answer:** ❌ **No**

---

**Explanation:**

In Azure, only a **Global Administrator** can create a new Microsoft Entra ID (Azure AD) tenant. In this scenario:

1. **User1** is a Global Administrator and creates the new Azure AD tenant named `external.contoso.onmicrosoft.com`
2. **User1**, as the creator of the new tenant, automatically becomes the **only Global Administrator** in the new tenant by default
3. **User3** is an **Owner** of an Azure subscription in the original tenant (`contoso.onmicrosoft.com`)

**Why User3 Cannot Create User Accounts:**

- Azure subscription roles (like **Owner** or **Contributor**) are **separate from Azure AD tenant roles** (like **Global Administrator** or **User Administrator**)
- User3's **Owner role** in an Azure subscription **does not grant any permissions** in the new Azure AD tenant
- User3 **does not automatically have access** to the new tenant `external.contoso.onmicrosoft.com` just because they have an Owner role in a subscription linked to the original tenant
- To create user accounts in an Azure AD tenant, a user must have one of the following directory roles:
  - **Global Administrator**
  - **User Administrator**

**How to Meet the Goal:**

User1 must first grant User3 the necessary permissions in the new tenant `external.contoso.onmicrosoft.com` by:
1. Adding User3 as a user in the new tenant (as a guest or member)
2. Assigning User3 the **User Administrator** or **Global Administrator** role in the new tenant

Only after these steps can User3 create user accounts in `external.contoso.onmicrosoft.com`.

---

**Key Takeaways:**

1. **Azure Subscription Roles ≠ Azure AD Tenant Roles:**
   
   | Azure Subscription RBAC Roles | Azure AD Tenant Roles |
   |------------------------------|----------------------|
   | Owner, Contributor, Reader | Global Administrator, User Administrator, etc. |
   | Control access to Azure resources | Control access to directory and user management |
   | Scoped to subscription/resource group/resource | Scoped to the entire tenant |

2. **New Tenant = Fresh Start:**
   - When a new Azure AD tenant is created, it starts with **no inherited permissions** from other tenants
   - The creator (User1) is the only Global Administrator initially
   - Users from other tenants must be explicitly added and granted roles

3. **User Management Permissions:**
   - Creating user accounts requires **directory-level permissions**, not subscription-level permissions
   - Required roles: **Global Administrator** or **User Administrator**
   - **Owner** role at subscription level has **no effect** on Azure AD tenant user management

4. **Multi-Tenant Isolation:**
   - Each Azure AD tenant is completely isolated from others
   - Permissions in one tenant do not carry over to another tenant
   - Cross-tenant access must be explicitly configured

**References:**
- [Azure AD Built-in Roles](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference)
- [Difference between Azure roles and Azure AD roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/rbac-and-directory-admin-roles)
- [Add or delete users in Azure AD](https://learn.microsoft.com/en-us/entra/fundamentals/add-users)
