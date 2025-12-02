# Azure RBAC Permission Models

## Table of Contents

- [Overview](#overview)
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
