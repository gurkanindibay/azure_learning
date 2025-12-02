# Azure Key Vault

## Table of Contents

- [Overview](#overview)
  - [What is Azure Key Vault?](#what-is-azure-key-vault)
  - [Key Capabilities](#key-capabilities)
  - [Key Vault Object Types](#key-vault-object-types)
  - [Access Control](#access-control)
  - [Key Vault Properties for Azure Services Integration](#key-vault-properties-for-azure-services-integration)
  - [Pricing Tiers](#pricing-tiers)
- [Question 1: VM Certificate Retrieval During Deployment](#question-1-vm-certificate-retrieval-during-deployment)
  - [Explanation](#explanation)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect)
  - [Key Vault Deployment Properties Comparison](#key-vault-deployment-properties-comparison)
  - [Key Takeaway](#key-takeaway)
  - [Related Learning Resources](#related-learning-resources)
- [Question 2: Secure Storage of Connection Strings with Automatic Rotation](#question-2-secure-storage-of-connection-strings-with-automatic-rotation)
  - [Explanation](#explanation-1)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-1)
  - [Key Takeaway](#key-takeaway-1)
- [Question 3: Preventing Contributor Role Data Plane Access](#question-3-preventing-contributor-role-data-plane-access)
  - [Explanation](#explanation-2)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-2)
  - [Permission Model Comparison](#permission-model-comparison)
  - [Key Takeaway](#key-takeaway-2)

## Overview

### What is Azure Key Vault?

Azure Key Vault is a cloud service for securely storing and accessing secrets. It provides:

- **Centralized secret management** for applications and services
- **Hardware Security Module (HSM)** backed key storage
- **Secure access** through Azure Active Directory authentication
- **Audit logging** of all access to secrets, keys, and certificates
- **Integration** with other Azure services like VMs, App Service, and Azure Functions

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Secrets Management** | Securely store and control access to tokens, passwords, API keys, and other secrets |
| **Key Management** | Create and control encryption keys used to encrypt your data |
| **Certificate Management** | Provision, manage, and deploy SSL/TLS certificates |
| **HSM-backed Keys** | Use hardware security modules to protect keys (Premium tier) |
| **Soft Delete** | Recover deleted vaults and objects within a retention period |
| **Purge Protection** | Prevent permanent deletion during retention period |

### Key Vault Object Types

Azure Key Vault manages three types of objects:

1. **Secrets**: Any sequence of bytes under 25KB (connection strings, passwords, API keys)
2. **Keys**: Cryptographic keys for encryption operations (RSA, EC keys)
3. **Certificates**: X.509 certificates for SSL/TLS, with optional private key management

### Access Control

Key Vault supports two permission models:

| Model | Description | Use Case |
|-------|-------------|----------|
| **Vault Access Policy** | Traditional model with policies per identity | Simple scenarios, legacy applications |
| **Azure RBAC** | Role-based access control at management and data plane | Fine-grained control, recommended for new deployments |

### Key Vault Properties for Azure Services Integration

Azure Key Vault has specific properties that control integration with other Azure services:

| Property | Purpose | Enables |
|----------|---------|---------|
| `enabledForDeployment` | VM certificate retrieval | VMs to retrieve certificates during deployment |
| `enabledForTemplateDeployment` | ARM template secret access | Resource Manager to retrieve secrets during deployments |
| `enabledForDiskEncryption` | Azure Disk Encryption | ADE to retrieve secrets and unwrap keys |
| `enableSoftDelete` | Deletion protection | Recovery of deleted vaults and objects |
| `enablePurgeProtection` | Purge protection | Prevents permanent deletion during retention |

### Pricing Tiers

| Tier | Features | Key Protection |
|------|----------|----------------|
| **Standard** | Secrets, keys, certificates | Software-protected keys |
| **Premium** | All Standard features + HSM-backed keys | HSM-protected keys (FIPS 140-2 Level 2) |

---

## Question 1: VM Certificate Retrieval During Deployment

**Scenario:**
You need to configure an Azure Key Vault to allow virtual machines to retrieve certificates during deployment.

**Question:**
Which property must be set to true?

**Options:**

1. **enabledForTemplateDeployment** ❌ *Incorrect*

2. **enabledForDiskEncryption** ❌ *Incorrect*

3. **enableSoftDelete** ❌ *Incorrect*

4. **enabledForDeployment** ✅ *Correct*

### Explanation

**Correct Answer: enabledForDeployment**

In order for Key Vault to be used with Azure Resource Manager VMs, the **`enabledForDeployment`** property on Key Vault must be set to `true`. This property specifically enables VMs to retrieve certificates from the vault during deployment.

```bicep
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'myKeyVault'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    // Enable VM certificate retrieval during deployment
    enabledForDeployment: true
    accessPolicies: []
  }
}
```

**Azure CLI Example:**

```bash
# Create Key Vault with enabledForDeployment
az keyvault create \
  --name myKeyVault \
  --resource-group myResourceGroup \
  --location eastus \
  --enabled-for-deployment true

# Update existing Key Vault
az keyvault update \
  --name myKeyVault \
  --enabled-for-deployment true
```

**PowerShell Example:**

```powershell
# Create Key Vault with EnabledForDeployment
New-AzKeyVault -Name 'myKeyVault' `
  -ResourceGroupName 'myResourceGroup' `
  -Location 'eastus' `
  -EnabledForDeployment

# Update existing Key Vault
Set-AzKeyVaultAccessPolicy -VaultName 'myKeyVault' `
  -EnabledForDeployment
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **enabledForTemplateDeployment** | This property allows Azure Resource Manager to retrieve **secrets** from the vault during **template deployments** (ARM/Bicep). It's for accessing secrets in deployment templates, not specifically for VM certificate retrieval. |
| **enabledForDiskEncryption** | This property allows **Azure Disk Encryption** to retrieve secrets and unwrap keys from the vault. It's used for encrypting VM disks, not for retrieving certificates during VM deployment. |
| **enableSoftDelete** | This property provides protection against **accidental deletion** by retaining deleted vaults and objects for a retention period (default 90 days). It has nothing to do with VM access to certificates. |

### Key Vault Deployment Properties Comparison

| Property | Purpose | Used By | Scenario |
|----------|---------|---------|----------|
| **enabledForDeployment** | VM certificate retrieval | Azure VMs | Installing certificates on VMs during provisioning |
| **enabledForTemplateDeployment** | Secret access in ARM templates | Azure Resource Manager | Referencing secrets in deployment templates |
| **enabledForDiskEncryption** | Disk encryption keys | Azure Disk Encryption | Encrypting VM OS and data disks |

### Visual Representation

```
                              Azure Key Vault
                    ┌─────────────────────────────────────┐
                    │                                     │
                    │  ┌───────────┐  ┌───────────────┐  │
                    │  │  Secrets  │  │  Certificates │  │
                    │  └───────────┘  └───────────────┘  │
                    │  ┌───────────┐                     │
                    │  │   Keys    │                     │
                    │  └───────────┘                     │
                    │                                     │
                    │  Properties:                        │
                    │  ├─ enabledForDeployment ─────────────────► Azure VMs (certificates)
                    │  ├─ enabledForTemplateDeployment ─────────► ARM Templates (secrets)
                    │  └─ enabledForDiskEncryption ─────────────► Azure Disk Encryption
                    │                                     │
                    └─────────────────────────────────────┘
```

### Common Use Cases for Each Property

**enabledForDeployment = true:**
- Deploying VMs with SSL certificates
- Installing certificates for application authentication
- Setting up VMs that need certificates from Key Vault

**enabledForTemplateDeployment = true:**
- Passing secrets to ARM/Bicep templates
- Deploying resources that need connection strings
- Creating resources with API keys from Key Vault

**enabledForDiskEncryption = true:**
- Enabling Azure Disk Encryption on VMs
- Storing BitLocker/DM-Crypt keys
- Managing disk encryption keys

### Key Takeaway

When you need Azure VMs to retrieve **certificates** from Key Vault during deployment, set **`enabledForDeployment`** to `true`. This is distinct from `enabledForTemplateDeployment` (for ARM template secret access) and `enabledForDiskEncryption` (for Azure Disk Encryption).

### Related Learning Resources
- Configure and manage secrets in Azure Key Vault
- About Azure Key Vault
- Use Azure Key Vault with a virtual machine
- Key Vault deployment properties

---

## Question 2: Secure Storage of Connection Strings with Automatic Rotation

**Scenario:**
A web application needs to store database connection strings securely. The connection strings must be automatically rotated without application changes, and access must be auditable.

**Question:**
What is the most appropriate solution?

**Options:**

1. **Store connection strings in Azure App Configuration with encryption enabled** ❌ *Incorrect*

2. **Store connection strings as secrets in Azure Key Vault with rotation policies configured** ✅ *Correct*

3. **Store connection strings in a storage account with immutability policies enabled** ❌ *Incorrect*

4. **Store connection strings as environment variables in the web application settings** ❌ *Incorrect*

### Explanation

**Correct Answer: Store connection strings as secrets in Azure Key Vault with rotation policies configured**

Azure Key Vault is designed to securely store and tightly control access to tokens, passwords, certificates, API keys, and other secrets like connection strings. Key Vault provides:

- **Secure Storage**: Hardware-backed encryption for sensitive data
- **Automatic Rotation**: Rotation policies can be configured to automatically rotate secrets
- **Full Audit Capabilities**: All access to secrets is logged and auditable
- **No Application Changes**: Applications can reference Key Vault secrets, and rotation happens transparently

```bicep
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'myKeyVault'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableSoftDelete: true
    enablePurgeProtection: true
    accessPolicies: []
  }
}

// Store connection string as a secret
resource dbConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'DatabaseConnectionString'
  properties: {
    value: 'Server=myserver.database.windows.net;Database=mydb;...'
    attributes: {
      enabled: true
    }
  }
}
```

**Azure CLI Example - Setting up rotation policy:**

```bash
# Create a secret with rotation policy
az keyvault secret set \
  --vault-name myKeyVault \
  --name DatabaseConnectionString \
  --value "Server=myserver.database.windows.net;..."

# Configure rotation policy (for supported secret types)
az keyvault secret rotation-policy update \
  --vault-name myKeyVault \
  --name DatabaseConnectionString \
  --auto-rotate-interval 90d
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Azure App Configuration with encryption enabled** | While Azure App Configuration can store configuration data securely, it doesn't provide built-in automatic rotation capabilities for secrets like connection strings. It's designed for application configuration management, not secret lifecycle management. |
| **Storage account with immutability policies** | Storage accounts with immutability policies prevent modification of data, which would actually **prevent rotation**. This solution lacks the secret management features needed for connection strings and is designed for compliance scenarios requiring data immutability. |
| **Environment variables in web application settings** | Environment variables in application settings don't provide automatic rotation capabilities and have limited audit functionality compared to purpose-built secret management solutions. Rotating secrets would require application redeployment or restart. |

### Comparison of Secret Storage Options

| Feature | Key Vault | App Configuration | Storage Account | Environment Variables |
|---------|-----------|-------------------|-----------------|----------------------|
| **Secure Storage** | ✅ HSM-backed | ✅ Encrypted | ✅ Encrypted | ⚠️ Limited |
| **Automatic Rotation** | ✅ Built-in policies | ❌ Not supported | ❌ Not applicable | ❌ Not supported |
| **Audit Logging** | ✅ Full audit trail | ⚠️ Limited | ⚠️ Limited | ❌ No audit |
| **No App Changes for Rotation** | ✅ Transparent | ❌ Requires update | ❌ Not applicable | ❌ Requires restart |
| **Secret Management** | ✅ Purpose-built | ❌ Config-focused | ❌ Not designed for | ❌ Basic |

### Key Takeaway

When you need to store secrets (like connection strings) with requirements for **automatic rotation**, **security**, and **auditability**, **Azure Key Vault** is the purpose-built solution. It provides rotation policies to automatically rotate secrets, comprehensive audit logging, and allows applications to retrieve the latest secret version without code changes.

---

## Question 3: Preventing Contributor Role Data Plane Access

**Scenario:**
You are configuring Azure Key Vault to prevent unauthorized users with Contributor role from granting themselves data plane access.

**Question:**
Which permission model should you implement?

**Options:**

1. **Vault access policy with deny assignments** ❌ *Incorrect*

2. **Access Policies with restricted permissions** ❌ *Incorrect*

3. **Access Policies with Azure AD authentication** ❌ *Incorrect*

4. **Azure RBAC** ✅ *Correct*

### Explanation

**Correct Answer: Azure RBAC**

To mitigate the risk of users with Contributor role granting themselves data plane access, you should implement the **Role-Based Access Control (RBAC) permission model**. Azure RBAC restricts permission management to the **'Owner'** and **'User Access Administrator'** roles, allowing a clear separation between security operations and administrative duties.

With Azure RBAC:
- **Contributor role** users **cannot** grant themselves or others access to Key Vault data plane
- Only users with **Owner** or **User Access Administrator** roles can assign Key Vault data plane roles
- Provides clear separation of duties between infrastructure management and security administration

```bash
# Enable Azure RBAC permission model on Key Vault
az keyvault update \
  --name myKeyVault \
  --resource-group myResourceGroup \
  --enable-rbac-authorization true
```

```bicep
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'myKeyVault'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    // Enable Azure RBAC permission model
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
  }
}
```

**Assigning Key Vault Data Plane Roles:**

```bash
# Assign Key Vault Secrets User role (read secrets only)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee user@contoso.com \
  --scope /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault-name}

# Assign Key Vault Administrator role (full data plane access)
az role assignment create \
  --role "Key Vault Administrator" \
  --assignee admin@contoso.com \
  --scope /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{vault-name}
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Vault access policy with deny assignments** | When using the Access Policy permission model, a user with the Contributor role can still grant themselves access. Deny assignments don't override this fundamental limitation of the access policy model. The access policy model inherently allows users with `Microsoft.KeyVault/vaults/write` permission to modify policies. |
| **Access Policies with restricted permissions** | When using the Access Policy permission model, a user with **Contributor**, **Key Vault Contributor**, or any other role that includes `Microsoft.KeyVault/vaults/write` permissions for the key vault management plane can grant themselves data plane access by setting a Key Vault access policy. This is a fundamental design limitation of access policies. |
| **Access Policies with Azure AD authentication** | Access Policies **always** allow users with Contributor role to modify them regardless of authentication method, as this is a limitation of the access policy model itself. Azure AD authentication doesn't change the permission model's behavior. |

### Permission Model Comparison

| Feature | Access Policy Model | Azure RBAC Model |
|---------|--------------------|-----------------|
| **Contributor can grant self access** | ✅ Yes (Security Risk) | ❌ No (Prevented) |
| **Who can manage data plane access** | Users with `Microsoft.KeyVault/vaults/write` | Owner, User Access Administrator |
| **Separation of duties** | ❌ Limited | ✅ Clear separation |
| **Granular permissions** | ⚠️ Limited (per identity) | ✅ Fine-grained (built-in roles) |
| **Scope flexibility** | Vault level only | Subscription, RG, Vault, or individual object |
| **Recommended for new deployments** | ❌ No | ✅ Yes |

### Key Vault RBAC Built-in Roles

| Role | Description | Scope |
|------|-------------|-------|
| **Key Vault Administrator** | Full access to all data plane operations | Data plane |
| **Key Vault Secrets Officer** | Manage secrets (read, write, delete) | Secrets |
| **Key Vault Secrets User** | Read secret contents | Secrets |
| **Key Vault Certificates Officer** | Manage certificates | Certificates |
| **Key Vault Crypto Officer** | Manage keys | Keys |
| **Key Vault Crypto User** | Perform cryptographic operations | Keys |
| **Key Vault Reader** | Read vault metadata (no secrets) | Metadata |

### The Security Problem with Access Policies

```
Access Policy Model (Security Risk):
┌──────────────────────────────────────────────────────────┐
│  User with Contributor Role                              │
│  ├── Has Microsoft.KeyVault/vaults/write permission      │
│  └── Can modify vault properties including...            │
│       └── Access Policies ──► Grants self data access!   │
└──────────────────────────────────────────────────────────┘

Azure RBAC Model (Secure):
┌──────────────────────────────────────────────────────────┐
│  User with Contributor Role                              │
│  ├── Has Microsoft.KeyVault/vaults/write permission      │
│  └── Can modify vault properties BUT...                  │
│       └── Cannot assign RBAC roles (requires Owner/UAA)  │
└──────────────────────────────────────────────────────────┘
```

### Key Takeaway

When you need to prevent users with **Contributor** role from granting themselves data plane access to Key Vault, implement the **Azure RBAC permission model**. This model restricts permission management to **Owner** and **User Access Administrator** roles only, providing clear separation between security operations and administrative duties. The Access Policy model has a fundamental security limitation where anyone with `Microsoft.KeyVault/vaults/write` permission can grant themselves data plane access.
