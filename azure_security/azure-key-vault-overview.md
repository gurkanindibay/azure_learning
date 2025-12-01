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
