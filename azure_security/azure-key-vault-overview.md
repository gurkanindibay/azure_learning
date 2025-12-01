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
