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
- [Practice Question: Azure AD Device and Group Management Permissions](#practice-question-azure-ad-device-and-group-management-permissions)
- [Practice Question: User Access Administrator Role for Role Assignment](#practice-question-user-access-administrator-role-for-role-assignment)
- [Practice Question: Management Group RBAC Inheritance and Role Permissions](#practice-question-management-group-rbac-inheritance-and-role-permissions)

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

---

## Practice Question: Azure AD Device and Group Management Permissions

**Scenario:**

You have an Azure Active Directory (Microsoft Entra ID) tenant named **Contoso.com** that includes the following users:

| Name | Role |
|------|------|
| User1 | Cloud device administrator |
| User2 | User administrator |

**Contoso.com** includes the following Windows 10 devices:

| Name | Join type |
|------|-----------|
| Device1 | Azure AD registered |
| Device2 | Azure AD joined |

You create the following security groups in **Contoso.com**:

| Name | Membership Type | Owner |
|------|----------------|--------|
| Group1 | Assigned | User2 |
| Group2 | Dynamic Device | User2 |

**Question:**

For each of the following statements, select **Yes** if the statement is true. Otherwise, select **No**.

| Statement | Answer |
|-----------|--------|
| User1 can add Device2 to Group1 | ❌ **No** |
| User2 can add Device1 to Group1 | ✅ **Yes** |
| User2 can add Device2 to Group2 | ❌ **No** |

---

**Explanation:**

### Statement 1: User1 can add Device2 to Group1 - ❌ No

**User1 Role: Cloud Device Administrator**

The **Cloud Device Administrator** role provides the following permissions:
- Enable, disable, and delete devices in Azure AD
- Read Windows 10 BitLocker keys in the Azure portal
- Manage device properties

**What Cloud Device Administrator CANNOT Do:**
- ❌ Manage group memberships (adding devices to groups)
- ❌ Create or delete groups
- ❌ Manage group owners or properties

**Why the Answer is No:**
- User1 has permissions to manage the **device object itself** (enable/disable/delete)
- User1 does **NOT** have permissions to manage **group memberships**
- Adding a device to a group requires either:
  - Being the **group owner**
  - Having **Groups Administrator** role
  - Having **Global Administrator** role

### Statement 2: User2 can add Device1 to Group1 - ✅ Yes

**User2 Role: User Administrator + Group1 Owner**

**User Administrator Role Permissions:**
- Create and manage users and groups
- Manage group memberships
- Reset passwords for non-admin users
- Manage user properties

**Group Owner Permissions:**
- Add or remove group members
- Update group properties
- Delete the group they own

**Why the Answer is Yes:**
- User2 is the **owner of Group1**
- Group1 has **Assigned** membership type (manual membership management)
- Group owners can add any valid member (users or devices) to assigned groups
- Device1 is a valid Azure AD object (registered device) that can be added to groups
- User2's User Administrator role also provides group management permissions

**Important Note:**
- Both **Azure AD registered** and **Azure AD joined** devices can be members of Azure AD groups
- The join type (registered vs joined) does not affect the ability to add devices to assigned groups

### Statement 3: User2 can add Device2 to Group2 - ❌ No

**Group2 Membership Type: Dynamic Device**

**Dynamic Device Groups:**
- Membership is **automatically managed** based on device properties
- Membership rules are defined using device attributes (e.g., OS version, device name, etc.)
- Manual addition or removal of members is **not allowed**

**Why the Answer is No:**
- Group2 uses **Dynamic Device** membership type
- Dynamic groups do not allow manual member management
- **Neither** group owners **nor** administrators can manually add or remove members
- Membership is determined solely by the dynamic membership rule
- To add Device2 to Group2, you would need to:
  1. Modify the dynamic membership rule to include Device2's properties, OR
  2. Change Device2's properties to match the existing rule, OR
  3. Convert Group2 from Dynamic to Assigned membership type

**Key Difference:**
- **Assigned Groups**: Members are manually added/removed by owners or administrators
- **Dynamic Groups**: Members are automatically determined by rules based on object properties

---

**Key Takeaways:**

### 1. Azure AD Administrative Roles and Permissions

| Role | Device Management | Group Management |
|------|------------------|------------------|
| **Cloud Device Administrator** | ✅ Enable/disable/delete devices<br/>✅ Read BitLocker keys<br/>✅ Manage device properties | ❌ Cannot manage group memberships<br/>❌ Cannot add devices to groups |
| **User Administrator** | ✅ Basic device operations<br/>❌ Cannot update or delete devices | ✅ Create/manage groups<br/>✅ Manage group memberships<br/>✅ Add users/devices to groups |
| **Global Administrator** | ✅ Full device management | ✅ Full group management |

### 2. Device Join Types

Both device join types can be members of Azure AD groups:

| Join Type | Description | Group Membership |
|-----------|-------------|------------------|
| **Azure AD Registered** | Personal devices registered to organization<br/>(BYOD scenario) | ✅ Can be group members |
| **Azure AD Joined** | Corporate devices fully joined to Azure AD<br/>(Cloud-only or hybrid) | ✅ Can be group members |

### 3. Group Membership Types

| Membership Type | Management | Who Can Modify |
|----------------|------------|----------------|
| **Assigned** | Manual membership management | Group owners, Groups Administrator, Global Administrator |
| **Dynamic User** | Rule-based automatic membership for users | No manual management - only by changing rules or user properties |
| **Dynamic Device** | Rule-based automatic membership for devices | No manual management - only by changing rules or device properties |

### 4. Group Ownership Permissions

**As a Group Owner, you can:**
- ✅ Add or remove members (for assigned groups only)
- ✅ Update group properties
- ✅ Add or remove other group owners
- ✅ Delete the group

**Group Owners CANNOT:**
- ❌ Modify dynamic group membership rules (requires Groups Administrator or Global Administrator)
- ❌ Add/remove members from dynamic groups
- ❌ Override their own administrative role limitations

### 5. Permission Hierarchy

For adding devices to groups, the following hierarchy applies:

```
Can add device to assigned group:
├── Global Administrator ......................... ✅ Yes (all permissions)
├── Groups Administrator ......................... ✅ Yes (group-specific permissions)
├── Group Owner .................................. ✅ Yes (only for owned groups)
├── User Administrator ........................... ✅ Yes (user and group management)
└── Cloud Device Administrator ................... ❌ No (device-only permissions)

Can add device to dynamic group:
└── No one ....................................... ❌ No (membership is rule-based)
    └── Modify membership rule instead ........... ✅ Groups Administrator or Global Administrator
```

### 6. Exam Tips

**Common Traps:**
- ❌ Assuming Cloud Device Administrator can manage group memberships (they cannot)
- ❌ Assuming group owners can add members to dynamic groups (they cannot)
- ❌ Confusing device management permissions with group management permissions
- ❌ Thinking Azure AD registered devices cannot be group members (they can)

**Key Points to Remember:**
1. **Separate Permissions**: Device management ≠ Group management
2. **Dynamic Groups**: No manual member management allowed
3. **Group Ownership**: Powerful for assigned groups, but limited for dynamic groups
4. **Role Specificity**: Each Azure AD role has specific, non-overlapping permissions

**References:**
- [Azure AD built-in roles - Cloud Device Administrator](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference#cloud-device-administrator)
- [Azure AD built-in roles - User Administrator](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference#user-administrator)
- [Dynamic membership rules for groups in Azure AD](https://learn.microsoft.com/en-us/entra/identity/users/groups-dynamic-membership)
- [Manage group ownership in Azure AD](https://learn.microsoft.com/en-us/entra/fundamentals/how-to-manage-groups)
- [Azure AD registered devices](https://learn.microsoft.com/en-us/entra/identity/devices/concept-device-registration)
- [Azure AD joined devices](https://learn.microsoft.com/en-us/entra/identity/devices/concept-directory-join)

---

## Practice Question: User Access Administrator Role for Role Assignment

**Scenario:**

You have an Azure subscription named Subscription1 that contains a virtual network named VNet1. VNet1 is in a resource group named RG1.

Subscription1 has a user named User1. User1 has the following roles:
- Reader
- Security Admin
- Security Reader

**Requirement:**

You need to ensure that User1 can assign the Reader role for VNet1 to other users.

**Question:**

What should you do?

**Options:**

A. Assign User1 the Network Contributor role for VNet1  
B. Assign User1 the Network Contributor role for RG1  
C. Remove User1 from the Security Reader and Reader roles for Subscription1  
D. Assign User1 the User Access Administrator role for VNet1

---

### Answer: D - Assign User1 the User Access Administrator role for VNet1

### Explanation

**Why Option D is Correct:**

The **User Access Administrator** role is specifically designed to manage access permissions for Azure resources. This role grants the ability to:
- Create, update, and delete role assignments
- Manage user access to Azure resources at the assigned scope
- Delegate role assignment capabilities to others

Since the requirement is to ensure User1 can assign the Reader role for VNet1 to other users, assigning the User Access Administrator role at the VNet1 scope directly achieves this goal.

**Role Assignment Scope:**

```
User1
└── User Access Administrator role (at VNet1 scope)
    └── Can assign any role (including Reader) for VNet1 to other users
```

**Required RBAC Action:**

The User Access Administrator role includes the following critical action:
- `Microsoft.Authorization/roleAssignments/write` - Create and update role assignments

**Why Other Options are Incorrect:**

### Option A: Assign User1 the Network Contributor role for VNet1 ❌

**Network Contributor Role Capabilities:**
- Manage network resources (create, update, delete virtual networks, subnets, NSGs, etc.)
- Configure network settings
- Manage network security

**Why It Doesn't Work:**
- Network Contributor is focused on **managing network resources**, not managing access permissions
- Does **NOT** include `Microsoft.Authorization/roleAssignments/write` permission
- User1 would be able to configure VNet1 but **NOT** assign roles to other users
- This is an example of confusing resource management with access management

**RBAC Actions Comparison:**

| Role | Network Management | Role Assignment |
|------|-------------------|-----------------|
| Network Contributor | ✅ `Microsoft.Network/*` | ❌ No `roleAssignments/write` |
| User Access Administrator | ❌ No network actions | ✅ `Microsoft.Authorization/roleAssignments/*` |

### Option B: Assign User1 the Network Contributor role for RG1 ❌

**Why It Doesn't Work:**
- Same issue as Option A - Network Contributor doesn't include role assignment permissions
- Assigning at RG1 scope instead of VNet1 scope doesn't change the role's capabilities
- User1 would manage all network resources in RG1, but still cannot assign roles

**Scope Considerations:**

```
RG1 (Resource Group)
├── VNet1 (Virtual Network)
├── Storage Account
└── Other Resources

Network Contributor at RG1 scope:
├── ✅ Can manage VNet1 and all other network resources in RG1
└── ❌ Still cannot assign roles for any resource in RG1
```

### Option C: Remove User1 from the Security Reader and Reader roles for Subscription1 ❌

**Why It Doesn't Work:**
- Removing existing roles **does not grant new capabilities**
- User1 would have **less permissions** after removal, not more
- Reader and Security Reader roles are not preventing User1 from assigning roles
- The issue is **lack of User Access Administrator role**, not presence of other roles

**Current vs After Removal:**

| State | Roles | Can Assign Roles? |
|-------|-------|-------------------|
| **Current** | Reader, Security Admin, Security Reader | ❌ No |
| **After Removal** | Security Admin only | ❌ No (same problem) |
| **Correct Solution** | Reader, Security Admin, Security Reader, **User Access Administrator** | ✅ Yes |

---

### Key Concepts

#### 1. Role Assignment Permissions in Azure RBAC

**Only specific roles can assign roles to other users:**

| Role | Scope | Can Assign Roles | Typical Use Case |
|------|-------|------------------|------------------|
| **Owner** | Any scope | ✅ All roles within scope | Full management including access control |
| **User Access Administrator** | Any scope | ✅ All roles within scope | Dedicated access management role |
| **Custom Role** | Defined scopes | Only if includes `roleAssignments/write` | Specific delegation scenarios |

**All other built-in roles (including Contributor):**
- ❌ **Cannot** assign roles to other users
- ❌ **Cannot** modify role assignments
- ❌ **Cannot** manage access permissions

#### 2. Separation Between Resource Management and Access Management

Azure RBAC enforces a clear separation:

```
┌──────────────────────────────────────────────────────────┐
│  Resource Management Roles                               │
│  ├── Contributor: Manage resources, but NOT access       │
│  ├── Network Contributor: Manage network resources       │
│  ├── Storage Account Contributor: Manage storage         │
│  └── Cannot assign roles to others                       │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Access Management Roles                                 │
│  ├── User Access Administrator: Manage role assignments  │
│  ├── Owner: Manage resources AND access                  │
│  └── Can assign roles to others                          │
└──────────────────────────────────────────────────────────┘
```

**Why This Matters:**
- Prevents privilege escalation
- Implements principle of least privilege
- Ensures security team controls who can access resources
- DevOps can manage infrastructure without granting themselves access to sensitive data

#### 3. User Access Administrator vs Owner Role

| Aspect | User Access Administrator | Owner |
|--------|--------------------------|-------|
| **Manage role assignments** | ✅ Yes | ✅ Yes |
| **Manage resources** | ❌ No | ✅ Yes |
| **Typical use case** | Security team managing access | Full administrative control |
| **Principle of least privilege** | ✅ Better - focused on access only | ⚠️ Broader permissions |

**Best Practice:**
- Use **User Access Administrator** when you only need to manage access
- Use **Owner** when you need both resource management and access management
- For the exam scenario, User Access Administrator is the **minimum required permission**

#### 4. Scope-Based Role Assignments

Role assignments are scoped - you can only assign roles within your scope:

```
Subscription1
├── RG1 (Resource Group)
│   └── VNet1 (Virtual Network)
└── RG2 (Resource Group)

User1 with User Access Administrator at VNet1 scope:
├── ✅ Can assign roles for VNet1
├── ❌ Cannot assign roles for RG1
├── ❌ Cannot assign roles for other resources in RG1
└── ❌ Cannot assign roles for Subscription1
```

**Scope Hierarchy:**

| Scope | User1 Can Assign Roles For |
|-------|----------------------------|
| **VNet1** | Only VNet1 |
| **RG1** | VNet1 and all resources in RG1 |
| **Subscription1** | All resources in subscription |

---

### Exam Tips

**Common Traps:**

1. ❌ Confusing resource management roles with access management roles
   - Network Contributor, Storage Account Contributor, etc. **cannot** assign roles
   - Only Owner and User Access Administrator can assign roles

2. ❌ Assuming Contributor role includes role assignment permissions
   - Contributor can manage resources but **NOT** access permissions
   - This is by design for security separation

3. ❌ Thinking you need to remove existing roles to add new capabilities
   - Azure RBAC is additive - you need to **add** User Access Administrator, not remove other roles

4. ❌ Confusing Azure RBAC roles with Microsoft Entra ID (Azure AD) administrative roles
   - User Access Administrator = Azure RBAC role (for Azure resources)
   - User Administrator = Entra ID role (for users/groups in Azure AD)
   - They are different role systems with different permissions

**Key Recognition Patterns:**

When you see these phrases in exam questions:
- "Assign roles to other users" → User Access Administrator or Owner
- "Manage access permissions" → User Access Administrator or Owner  
- "Delegate role assignment" → User Access Administrator or Owner
- "Manage network resources" → Network Contributor (NOT for role assignment)
- "Configure resource settings" → Contributor or resource-specific role (NOT for role assignment)

**Quick Decision Tree:**

```
Question asks: "User needs to assign roles to others"
    │
    ├─── Resource management roles mentioned? 
    │    (Contributor, Network Contributor, etc.)
    │    └─── ❌ These are WRONG - cannot assign roles
    │
    └─── Access management roles mentioned?
         (User Access Administrator, Owner)
         └─── ✅ These are CORRECT - can assign roles
              │
              ├─── User Access Administrator: Minimum required permission
              └─── Owner: Works but gives more permissions than needed
```

---

## Practice Question: Management Group RBAC Inheritance and Role Permissions

### Scenario

You have three Azure subscriptions named **Sub1**, **Sub2**, and **Sub3** that are linked to a Microsoft Entra ID tenant.

The tenant contains:
- A user named **User1**
- A security group named **Group1** (User1 is a member)
- A management group named **MG1**

**Resource Hierarchy:**
- **Sub1** and **Sub2** are members of **MG1**
- **Sub3** is not a member of **MG1**
- **Sub1** contains a resource group named **RG1**
- **RG1** contains five Azure functions

**Role Assignments:**

At **MG1** level:
- **Group1**: Reader role
- **User1**: User Access Administrator role

At **Sub1** and **Sub2** level:
- **User1**: Virtual Machine Contributor role

### Questions

Evaluate the following statements:

| Statement | Yes | No |
|-----------|-----|-----|
| The Group1 members can view the configurations of the Azure functions. | ⭕ | ⭕ |
| User1 can assign the Owner role for RG1. | ⭕ | ⭕ |
| User1 can create a new resource group and deploy a virtual machine to the new group. | ⭕ | ⭕ |

### Correct Answers

| Statement | Answer |
|-----------|--------|
| The Group1 members can view the configurations of the Azure functions. | **Yes** |
| User1 can assign the Owner role for RG1. | **Yes** |
| User1 can create a new resource group and deploy a virtual machine to the new group. | **No** |

### Explanation

#### Statement 1: Group1 members can view Azure function configurations ✅ YES

**Analysis:**
- Group1 has the **Reader** role assigned at **MG1** level
- Sub1 is a member of MG1, so the Reader role **inherits** to Sub1 and all its child resources
- The Reader role provides read-only access to all resources within scope
- RG1 and its Azure functions are within Sub1
- Therefore, Group1 members (including User1) can view the configurations of the Azure functions

**Key Concept:**
- RBAC role assignments at management group level inherit to all subscriptions and resource groups under that management group

#### Statement 2: User1 can assign Owner role for RG1 ✅ YES

**Analysis:**
- User1 has the **User Access Administrator** role at **MG1** level
- This role grants the ability to manage user access to Azure resources
- The User Access Administrator role has these key permissions:
  - `Microsoft.Authorization/*/read` - Read all authorization settings
  - `Microsoft.Authorization/roleAssignments/*` - Manage all role assignments
  - `Microsoft.Support/*` - Create and manage support tickets
- Since MG1 contains Sub1, and Sub1 contains RG1, User1 can assign roles at any scope within the management group hierarchy
- User1 can assign the Owner role (or any other role) for RG1

**Key Concept:**
- User Access Administrator allows managing role assignments but does NOT grant permissions to manage resources themselves
- This role is specifically designed for delegating access management without granting resource management capabilities

#### Statement 3: User1 can create new resource group and deploy VM ❌ NO

**Analysis:**

Let's examine User1's effective permissions:

1. **From MG1 level:**
   - **User Access Administrator**: Only allows managing role assignments, NOT creating resources
   - **Reader** (via Group1 membership): Only read access, no write permissions

2. **From Sub1 and Sub2 level:**
   - **Virtual Machine Contributor**: Allows only VM management operations, NOT resource group creation

**Why User1 cannot create resource groups:**
- Resource group creation requires one of these roles at subscription level:
  - Owner
  - Contributor
  - Custom role with `Microsoft.Resources/subscriptions/resourceGroups/write` permission
- Virtual Machine Contributor only includes:
  - `Microsoft.Compute/virtualMachines/*` - VM operations
  - `Microsoft.Network/*` (some network operations)
  - `Microsoft.Storage/*/read` - Read storage
- It does NOT include `Microsoft.Resources/subscriptions/resourceGroups/write`

**Why User1 cannot deploy VMs to a new resource group:**
- Even if User1 could create the resource group, deploying a VM requires the VM Contributor role at that resource group scope
- User1 only has VM Contributor at Sub1 and Sub2 subscription level
- This doesn't automatically grant access to resources User1 creates

**What User1 COULD do:**
1. User1 could use the User Access Administrator role to assign themselves the Contributor role at Sub1 level
2. Then User1 could create resource groups and deploy VMs
3. However, with the current role assignments, User1 cannot perform these operations

**Key Concept:**
- Role inheritance flows down the hierarchy (Management Group → Subscription → Resource Group → Resource)
- Having a role at subscription level doesn't automatically mean you can create the containers (resource groups) within it
- Virtual Machine Contributor is a targeted role that only manages VMs, not the resource groups that contain them

### Key Takeaways

1. **Management Group Inheritance**
   - Role assignments at management group level cascade down to all child subscriptions and their resources
   - This provides centralized access management across multiple subscriptions

2. **Reader Role Scope**
   - Reader role provides read-only access to all resources within scope
   - Includes viewing resource configurations, but no write or execute permissions

3. **User Access Administrator vs Contributor**
   - **User Access Administrator**: Manages who has access (role assignments only)
   - **Contributor**: Manages resources themselves (create, update, delete)
   - These roles serve different purposes and are often used together

4. **Virtual Machine Contributor Limitations**
   - Virtual Machine Contributor is a resource-specific role
   - It does NOT include permissions to create resource groups
   - Resource group creation requires Contributor or Owner role at subscription level

5. **Effective Permissions**
   - A user's effective permissions are the combination of ALL role assignments (direct and inherited)
   - Multiple role assignments are additive (union of all permissions)
   - Group membership role assignments apply to all members

### Role Permission Reference

| Role | Key Permissions | What It Can Do | What It Cannot Do |
|------|----------------|----------------|-------------------|
| **Reader** | `*/read` | View all resources and configurations | Create, modify, or delete resources; Manage access |
| **User Access Administrator** | `Microsoft.Authorization/roleAssignments/*` | Assign and remove role assignments | Create, modify, or delete resources |
| **Virtual Machine Contributor** | `Microsoft.Compute/virtualMachines/*` | Create, manage, and delete VMs | Create resource groups; Assign roles |
| **Contributor** | `*` (except authorization) | Create, modify, and delete all resources | Assign roles or manage access |
| **Owner** | `*` | Everything including role assignments | Nothing - full control |

**References:**
- [Azure Built-in Roles - User Access Administrator](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#user-access-administrator)
- [Azure Built-in Roles - Owner](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#owner)
- [Assign Azure roles using Azure Portal](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-portal)
- [Understand Azure role assignments](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments)

