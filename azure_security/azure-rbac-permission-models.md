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
- [Practice Question: Preventing Contributor Role Data Plane Access](#practice-question-preventing-contributor-role-data-plane-access)

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
