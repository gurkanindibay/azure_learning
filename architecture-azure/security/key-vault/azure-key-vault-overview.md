# Azure Key Vault

## Table of Contents

- [Overview](#overview)
  - [What is Azure Key Vault?](#what-is-azure-key-vault)
  - [Key Capabilities](#key-capabilities)
  - [Key Vault Object Types](#key-vault-object-types)
  - [Access Control](#access-control)
  - [Key Vault Properties for Azure Services Integration](#key-vault-properties-for-azure-services-integration)
  - [Pricing Tiers](#pricing-tiers)
  - [Backup and Restore Constraints](#backup-and-restore-constraints)
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
- [Question 4: FIPS 140-3 Level 3 Validation Requirements](#question-4-fips-140-3-level-3-validation-requirements)
  - [Explanation](#explanation-3)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-3)
  - [Key Vault vs Managed HSM Comparison](#key-vault-vs-managed-hsm-comparison)
  - [Key Takeaway](#key-takeaway-3)
- [Question 5: Bring Your Own Key (BYOK) Process for On-Premises HSM](#question-5-bring-your-own-key-byok-process-for-on-premises-hsm)
  - [Explanation](#explanation-4)
  - [Step-by-Step BYOK Process](#step-by-step-byok-process)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-4)
  - [BYOK Process Flow Diagram](#byok-process-flow-diagram)
  - [BYOK vs. Key Generation in Azure](#byok-vs-key-generation-in-azure)
  - [Complete BYOK Example](#complete-byok-example)
  - [Security Considerations](#security-considerations)
  - [Supported HSM Vendors](#supported-hsm-vendors)
  - [Key Takeaway](#key-takeaway-4)
- [Question 6: Key Vault Backup and Restore Disaster Recovery](#question-6-key-vault-backup-and-restore-disaster-recovery)
  - [Scenario](#scenario)
  - [Explanation](#explanation-5)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-5)
  - [Backup and Restore Restrictions](#backup-and-restore-restrictions)
  - [Key Takeaway](#key-takeaway-5)
  - [Reference(s)](#references)
- [Question 7: Key Vault Regional Failover and Continuity](#question-7-key-vault-regional-failover-and-continuity)
  - [Scenario](#scenario-1)
  - [Explanation](#explanation-6)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-6)
  - [Key Vault Availability and Redundancy](#key-vault-availability-and-redundancy)
  - [Key Takeaway](#key-takeaway-6)
  - [Reference(s)](#references-1)
- [Question 8: Authorizing App to Retrieve Secrets - Access Policy vs Role Assignment](#question-8-authorizing-app-to-retrieve-secrets---access-policy-vs-role-assignment)
  - [Scenario](#scenario-2)
  - [Explanation](#explanation-7)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect-7)
  - [Management Plane vs Data Plane Operations](#management-plane-vs-data-plane-operations)
  - [Key Takeaway](#key-takeaway-7)
  - [Reference(s)](#references-2)

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

| Tier | Features | Key Protection | FIPS Validation |
|------|----------|----------------|----------------|
| **Standard** | Secrets, keys, certificates | Software-protected keys | N/A |
| **Premium** | All Standard features + HSM-backed keys | HSM-protected keys | FIPS 140-3 Level 3 |

### Backup and Restore Constraints

Azure Key Vault backup and restore operations are subject to important **geography-based restrictions** to maintain data residency and compliance:

| Constraint | Details | Impact |
|------------|---------|--------|
| **Same Geography Required** | Backups can only be restored to Key Vaults within the **same Azure geography** | Prevents cross-geography data movement |
| **Same Subscription Required** | Backups must be restored within the **same Azure subscription** | Maintains security and ownership boundaries |
| **Region Flexibility** | Can restore to **any region** within the same geography | Enables disaster recovery across regions |
| **Vault Flexibility** | Can restore to **any Key Vault** (not just the original) | Supports migration and DR scenarios |

**Key Points:**
- A backup from a Key Vault in **West US** can be restored to **East US** (same geography: United States)
- A backup from a Key Vault in **West US** **cannot** be restored to **West Europe** (different geography)
- The encrypted backup blob is portable but geography-restricted during restore
- This ensures compliance with data residency requirements and regulatory boundaries

**Geography Examples:**
- **United States**: East US, West US, Central US, North Central US, South Central US, West US 2, West Central US, East US 2
- **Europe**: North Europe, West Europe
- **Asia Pacific**: Southeast Asia, East Asia, Australia East, Australia Southeast
- **Other Regions**: Each major geographic area has its own geography boundary

### Azure Managed HSM

Azure Managed HSM is a fully managed, highly available, single-tenant HSM service for scenarios requiring the highest level of security and compliance.

| Feature | Azure Key Vault Premium | Azure Managed HSM |
|---------|------------------------|-------------------|
| **HSM Type** | Multi-tenant | Single-tenant, dedicated |
| **FIPS Validation** | FIPS 140-3 Level 3 | FIPS 140-3 Level 3 |
| **Key Control** | Microsoft manages HSM | Customer controls HSM |
| **Use Case** | Most enterprise scenarios | Regulatory/compliance requirements needing dedicated HSM |
| **Pricing** | Per operation | Per HSM pool hour |

> **Note:** Both Azure Key Vault Premium and Azure Managed HSM now support **FIPS 140-3 Level 3** validated HSMs after recent firmware updates. Previously, Key Vault Premium only supported FIPS 140-2 Level 2.

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

---

## Question 4: FIPS 140-3 Level 3 Validation Requirements

**Scenario:**
You need to choose between Azure Key Vault Premium and Azure Managed HSM for storing cryptographic keys. Your requirement is FIPS 140-3 Level 3 validation.

**Question:**
Which service should you use?

**Options:**

1. **Azure Managed HSM only** ❌ *Incorrect*

2. **Azure Key Vault Premium only** ❌ *Incorrect*

3. **Neither service supports this requirement** ❌ *Incorrect*

4. **Either Azure Key Vault Premium or Azure Managed HSM** ✅ *Correct*

### Explanation

**Correct Answer: Either Azure Key Vault Premium or Azure Managed HSM**

Both Azure Key Vault Premium and Azure Managed HSM now support **FIPS 140-3 Level 3** validated HSMs after recent firmware updates. This makes either service suitable for meeting FIPS 140-3 Level 3 compliance requirements.

**FIPS 140-3 Level 3** provides:
- Tamper-evident physical security mechanisms
- Identity-based authentication
- Physical or logical separation between interfaces
- Protection against physical tampering attempts

```
FIPS 140-3 Level 3 Compliance Options:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌─────────────────────┐    ┌─────────────────────┐       │
│   │  Key Vault Premium  │    │   Azure Managed HSM │       │
│   │                     │    │                     │       │
│   │  ✅ FIPS 140-3 L3   │    │  ✅ FIPS 140-3 L3   │       │
│   │  Multi-tenant HSM   │    │  Single-tenant HSM  │       │
│   │  Shared infra       │    │  Dedicated infra    │       │
│   │  Lower cost         │    │  Higher cost        │       │
│   └─────────────────────┘    └─────────────────────┘       │
│                                                             │
│   Both options meet FIPS 140-3 Level 3 requirements!        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Azure Managed HSM only** | While Azure Managed HSM supports FIPS 140-3 Level 3, Azure Key Vault Premium has also been upgraded to support the same validation level, so this is not the only option. |
| **Azure Key Vault Premium only** | Azure Key Vault Premium supports FIPS 140-3 Level 3, but it's not the only option as Azure Managed HSM also provides the same validation level. |
| **Neither service supports this requirement** | This is incorrect as both Azure Key Vault Premium and Azure Managed HSM have been upgraded to support FIPS 140-3 Level 3 validated HSMs. |

### Key Vault vs Managed HSM Comparison

| Feature | Azure Key Vault Premium | Azure Managed HSM |
|---------|------------------------|-------------------|
| **FIPS 140-3 Level 3** | ✅ Yes | ✅ Yes |
| **HSM Type** | Multi-tenant (shared) | Single-tenant (dedicated) |
| **Key Sovereignty** | Keys in shared HSM pool | Full control over HSM |
| **Regulatory Compliance** | Most compliance needs | Strictest compliance requirements |
| **Cost Model** | Per-operation pricing | Per HSM pool hour |
| **Best For** | General enterprise use | Financial services, government, healthcare |

### When to Choose Each Option

**Choose Azure Key Vault Premium when:**
- You need FIPS 140-3 Level 3 compliance at lower cost
- Multi-tenant HSM infrastructure is acceptable
- You have standard enterprise security requirements

**Choose Azure Managed HSM when:**
- You need single-tenant, dedicated HSM infrastructure
- Regulations require full key sovereignty
- You need to bring your own key (BYOK) with full control
- You have the strictest compliance requirements (e.g., PCI DSS, HIPAA)

### Key Takeaway

For **FIPS 140-3 Level 3** validation requirements, you can use **either Azure Key Vault Premium or Azure Managed HSM**. Both services have been upgraded to support FIPS 140-3 Level 3 validated HSMs. The choice between them depends on other requirements such as key sovereignty, dedicated vs. shared infrastructure, cost considerations, and specific regulatory compliance needs.

---

## Question 5: Bring Your Own Key (BYOK) Process for On-Premises HSM

**Scenario:**
You are developing an Azure-hosted application that must use an on-premises hardware security module (HSM) key. The key must be transferred to your existing Azure Key Vault by using the Bring Your Own Key (BYOK) process.

**Question:**
Which four actions should you perform in sequence to securely transfer the key to Azure Key Vault?

**Options:**

1. **Box 1:** Create a custom policy definition in Azure Policy. **Box 2:** Generate a Key Exchange Key (KEK). **Box 3:** Retrieve the Key Exchange Key (KEK) public key. **Box 4:** Run the `az keyvault key import` command. ❌ *Incorrect*

2. **Box 1:** Create a custom policy definition in Azure Policy. **Box 2:** Retrieve the Key Exchange Key (KEK) public key. **Box 3:** Generate a key transfer blob file by using the HSM vendor-provided tool. **Box 4:** Run the `az keyvault key import` command. ❌ *Incorrect*

3. **Box 1:** Generate a Key Exchange Key (KEK). **Box 2:** Retrieve the Key Exchange Key (KEK) public key. **Box 3:** Generate a key transfer blob file by using the HSM vendor-provided tool. **Box 4:** Run the `az keyvault key restore` command. ❌ *Incorrect*

4. **Box 1:** Generate a Key Exchange Key (KEK). **Box 2:** Retrieve the Key Exchange Key (KEK) public key. **Box 3:** Generate a key transfer blob file by using the HSM vendor-provided tool. **Box 4:** Run the `az keyvault key import` command. ✅ *Correct*

### Explanation

**Correct Answer: Generate KEK → Retrieve KEK public key → Generate key transfer blob → Import key**

This sequence correctly outlines the steps required to securely transfer an on-premises HSM key to Azure Key Vault using the BYOK (Bring Your Own Key) process:

1. **Generate a Key Exchange Key (KEK)** in Azure Key Vault
2. **Retrieve the KEK public key** from Azure Key Vault
3. **Generate a key transfer blob file** using the HSM vendor-provided tool
4. **Run the `az keyvault key import` command** to import the key into Azure Key Vault

### Step-by-Step BYOK Process

#### Step 1: Generate a Key Exchange Key (KEK)

First, create a KEK in your Azure Key Vault. This key will be used to protect your HSM key during transfer.

```bash
# Generate a KEK in Azure Key Vault
az keyvault key create \
  --vault-name myKeyVault \
  --name myKEK \
  --kty RSA-HSM \
  --size 4096 \
  --ops import

# Verify the KEK was created
az keyvault key show \
  --vault-name myKeyVault \
  --name myKEK
```

```powershell
# PowerShell equivalent
Add-AzKeyVaultKey -VaultName 'myKeyVault' `
  -Name 'myKEK' `
  -Destination 'HSM' `
  -KeyOps import `
  -Size 4096
```

#### Step 2: Retrieve the Key Exchange Key (KEK) Public Key

Download the KEK public key to use with your on-premises HSM tooling.

```bash
# Download the KEK public key
az keyvault key download \
  --vault-name myKeyVault \
  --name myKEK \
  --file KEKforBYOK.publickey.pem
```

```powershell
# PowerShell equivalent
$kek = Get-AzKeyVaultKey -VaultName 'myKeyVault' -KeyName 'myKEK'
[System.IO.File]::WriteAllBytes("KEKforBYOK.publickey.pem", $kek.Key.N)
```

#### Step 3: Generate a Key Transfer Blob Using HSM Vendor-Provided Tool

Use your HSM vendor's tool to wrap your on-premises HSM key with the KEK public key and generate a key transfer blob. This step is vendor-specific.

**Example for Thales nShield HSM:**

```bash
# Use Thales nShield tool to generate key transfer blob
generatekey --generate simple \
  type=RSA size=2048 \
  plainname=myHSMkey \
  nvram=no \
  protect=module \
  ident=key_ident \
  wrap=KEKforBYOK.publickey.pem \
  out=myHSMkey.byok
```

**Example for generic HSM vendor tool:**

```bash
# Vendor-specific command to wrap the key
# This varies by HSM vendor (Thales, SafeNet, etc.)
hsm-tool export-key \
  --key-name myHSMkey \
  --wrap-with-kek KEKforBYOK.publickey.pem \
  --output myHSMkey.byok
```

The key transfer blob (`.byok` file) contains:
- Your HSM key encrypted with the KEK public key
- Key metadata and attributes
- Cryptographic proof of key protection

#### Step 4: Import the Key Transfer Blob into Azure Key Vault

Finally, import the protected key transfer blob into Azure Key Vault.

```bash
# Import the key transfer blob
az keyvault key import \
  --vault-name myKeyVault \
  --name myImportedHSMKey \
  --byok-file myHSMkey.byok \
  --kty RSA-HSM \
  --ops encrypt decrypt sign verify wrapKey unwrapKey
```

```powershell
# PowerShell equivalent
Add-AzKeyVaultKey -VaultName 'myKeyVault' `
  -Name 'myImportedHSMKey' `
  -KeyFilePath 'myHSMkey.byok' `
  -KeyFilePassword $securePwd `
  -Destination 'HSM'
```

**Verify the imported key:**

```bash
# Verify the key was imported successfully
az keyvault key show \
  --vault-name myKeyVault \
  --name myImportedHSMKey
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Create a custom policy definition in Azure Policy first** | Creating an Azure Policy definition is not part of the BYOK process. Azure Policy is for governance and compliance enforcement, not for key transfer operations. The BYOK process is purely about cryptographic key exchange. |
| **Retrieve KEK public key before generating KEK** | You cannot retrieve a KEK public key before the KEK exists. You must first **create** the KEK in Azure Key Vault before you can download its public key. |
| **Use `az keyvault key restore` command** | The `restore` command is for restoring keys from Key Vault backups, not for importing external HSM keys. The correct command for BYOK is `az keyvault key import` with the `--byok-file` parameter. |

### BYOK Process Flow Diagram

```
On-Premises HSM                    Azure Key Vault
┌─────────────────┐                ┌─────────────────┐
│                 │                │                 │
│  HSM Key        │                │   Step 1:       │
│  (to transfer)  │                │   Generate KEK  │
│                 │                │                 │
└─────────────────┘                └────────┬────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │   Step 2:       │
                    ◄──────────────│   Download KEK  │
                    │              │   Public Key    │
                    │              └─────────────────┘
                    │
                    ▼
       ┌─────────────────────────┐
       │   Step 3:               │
       │   Wrap HSM key with KEK │
       │   Generate .byok file   │
       │   (vendor tool)         │
       └───────────┬─────────────┘
                   │
                   │  myHSMkey.byok
                   ▼
           ┌─────────────────┐
           │   Step 4:       │
           │   az keyvault   │──────────►  Key imported
           │   key import    │             securely!
           └─────────────────┘
```

### BYOK vs. Key Generation in Azure

| Aspect | BYOK (Import) | Generate in Azure |
|--------|---------------|------------------|
| **Key Origin** | On-premises HSM | Azure Key Vault HSM |
| **Control** | Full control over key generation | Azure generates key |
| **Compliance** | Meets "customer-generated key" requirements | Standard Azure key management |
| **Process Complexity** | More complex (4 steps) | Simple (1 step) |
| **Use Case** | Regulatory requirements, existing HSM infrastructure | Standard cloud-native applications |
| **Key Never Leaves HSM** | ✅ Yes (wrapped during transfer) | ✅ Yes (generated in Azure HSM) |

### Commands Comparison

| Command | Purpose | Use Case |
|---------|---------|----------|
| `az keyvault key import --byok-file` | Import HSM-protected key | BYOK process |
| `az keyvault key import --pem-file` | Import software-protected key | Software keys |
| `az keyvault key create` | Generate new key in Azure | Standard key generation |
| `az keyvault key restore` | Restore from backup | Disaster recovery |

### Complete BYOK Example

```bash
# Complete BYOK workflow
VAULT_NAME="myKeyVault"
KEK_NAME="myKEK"
IMPORTED_KEY_NAME="myImportedHSMKey"

# Step 1: Generate KEK
az keyvault key create \
  --vault-name $VAULT_NAME \
  --name $KEK_NAME \
  --kty RSA-HSM \
  --size 4096 \
  --ops import

# Step 2: Download KEK public key
az keyvault key download \
  --vault-name $VAULT_NAME \
  --name $KEK_NAME \
  --file KEKforBYOK.publickey.pem

# Step 3: Generate key transfer blob (vendor-specific)
# Use your HSM vendor's tool to create myHSMkey.byok
# Example: ./hsm-tool export-key --wrap-with-kek KEKforBYOK.publickey.pem

# Step 4: Import the key
az keyvault key import \
  --vault-name $VAULT_NAME \
  --name $IMPORTED_KEY_NAME \
  --byok-file myHSMkey.byok \
  --kty RSA-HSM

# Verify import
az keyvault key show \
  --vault-name $VAULT_NAME \
  --name $IMPORTED_KEY_NAME \
  --query "{name:name, keyType:key.kty, managed:attributes.managed}"
```

### Security Considerations

1. **KEK Protection**: The KEK is stored in Azure Key Vault's HSM and never leaves it
2. **Key Transfer Blob**: Your HSM key is encrypted with the KEK during transfer
3. **No Plain Text**: Your HSM key never exists in plain text during the BYOK process
4. **HSM-to-HSM Transfer**: The key is transferred from your on-premises HSM to Azure's HSM without exposure
5. **Audit Trail**: All Key Vault operations are logged in Azure Monitor

### Supported HSM Vendors

Azure Key Vault BYOK supports keys from major HSM vendors:
- **Thales** (formerly nCipher) nShield HSMs
- **SafeNet** Luna HSMs
- **Utimaco** HSMs
- **Futurex** HSMs
- **nCipher** HSMs
- Other PKCS#11-compatible HSMs

### Key Takeaway

The correct BYOK process sequence is:
1. **Generate a Key Exchange Key (KEK)** in Azure Key Vault
2. **Retrieve the KEK public key**
3. **Generate a key transfer blob file** using your HSM vendor's tool
4. **Run `az keyvault key import`** with the `--byok-file` parameter

This process ensures secure transfer of your on-premises HSM key to Azure Key Vault without the key ever being exposed in plain text. The process does **not** involve Azure Policy definitions, and uses `import` (not `restore`) as the final command.
---

## Question 6: Key Vault Backup and Restore Disaster Recovery

### Scenario

You have an Azure web app that uses an Azure key vault named **KeyVault1** in the **West US** Azure region.

You are designing a disaster recovery plan for KeyVault1.

You plan to back up the keys in KeyVault1.

**Question:** You need to identify where you can restore the backup to. What should you identify?

**Options:**
- A. KeyVault1 only
- B. the same region only
- C. the same geography only ✅ *Correct*
- D. any region worldwide

### Explanation

**The same geography only** is correct because when you back up a key, secret, or certificate from Azure Key Vault, the operation creates an **encrypted blob** that can only be restored to another Key Vault within:

1. **The same Azure subscription**
2. **The same Azure geography**

This is a built-in limitation imposed by Azure to maintain **data residency** and **compliance boundaries**. While the backup file is portable and can be downloaded, restoration is restricted to ensure that sensitive data is not moved across geopolitical boundaries unintentionally.

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **any region worldwide** | Although the backup file is downloadable and appears portable, Azure restricts the restore operation to Key Vaults within the same geography and subscription. Attempting to restore the data to a Key Vault outside the original geography will result in a failure. |
| **the same region only** | Azure does **not** limit restore operations strictly to the same region. It allows restoring to any Key Vault within the same geography, which may include multiple regions (for example, both East US and West US fall under the United States geography). |
| **KeyVault1 only** | You can restore the backup to **any Key Vault** within the same geography and subscription—not just the original vault from which it was backed up. This flexibility supports scenarios like disaster recovery or migration within the same geography. |

### Backup and Restore Restrictions

| Aspect | Restriction | Reason |
|--------|-------------|--------|
| **Geography** | Must restore within the same Azure geography | Maintains data residency and compliance boundaries |
| **Subscription** | Must restore within the same Azure subscription | Security and ownership control |
| **Region Flexibility** | Can restore to any region within the same geography | Supports disaster recovery across regions in the same geography |
| **Vault Flexibility** | Can restore to any Key Vault (not just the original) | Enables migration and disaster recovery scenarios |

**Example Geography Groupings:**
- **United States**: East US, West US, Central US, etc.
- **Europe**: North Europe, West Europe, etc.
- **Asia Pacific**: Southeast Asia, East Asia, etc.

**Disaster Recovery Scenario:**
If KeyVault1 in West US becomes unavailable:
- ✅ **Can restore to:** A Key Vault in East US (same geography: United States)
- ✅ **Can restore to:** A Key Vault in Central US (same geography: United States)
- ❌ **Cannot restore to:** A Key Vault in West Europe (different geography)
- ❌ **Cannot restore to:** A Key Vault in Southeast Asia (different geography)

### Key Takeaway

Azure Key Vault backups can be restored to **any Key Vault within the same Azure geography and subscription**, but not to vaults in different geographies. This provides disaster recovery flexibility across regions while maintaining data residency compliance.

**Backup Command:**
```bash
az keyvault key backup --vault-name KeyVault1 --name MyKey --file backup.blob
```

**Restore Command:**
```bash
az keyvault key restore --vault-name KeyVault2 --file backup.blob
```

### Reference(s)

- [Azure Key Vault Backup](https://learn.microsoft.com/en-us/azure/key-vault/general/backup?tabs=azure-cli)
- [Azure Key Vault Disaster Recovery Guidance](https://learn.microsoft.com/en-us/azure/key-vault/general/disaster-recovery-guidance)

---

## Question 7: Key Vault Regional Failover and Continuity

### Scenario

You have an Azure web app named **App1** and an Azure key vault named **KV1**.

App1 stores database connection strings in KV1.

App1 performs the following types of requests to KV1:
- Get
- List
- Wrap
- Delete
- Unwrap
- Backup
- Decrypt
- Encrypt

You are evaluating the continuity of service for App1.

**Question:** You need to identify the following if the Azure region that hosts KV1 becomes unavailable: "To where will KV1 failover?"

**Options:**
- A. A server in the same availability set
- B. A server in the same fault domain
- C. A server in the paired region ✅ *Correct*
- D. A virtual machine in a scale set

### Explanation

**A server in the paired region** is correct because Azure Key Vault is a regional service, but it supports **geo-redundant recovery** by replicating its contents to the paired Azure region if soft-delete and purge protection are enabled.

In the event of a regional outage, Microsoft initiates a **manual failover** of the Key Vault to the paired region to restore access. This ensures continuity of service for applications like App1 that depend on the vault for secrets, encryption keys, or certificates.

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **A server in the same availability set** | Availability sets only apply to Azure virtual machines and are used to ensure high availability within a **single region**, not across regions. Azure Key Vault is a managed service and is not deployed in an availability set. |
| **A server in the same fault domain** | Fault domains provide hardware isolation within a datacenter, which does not help in the case of **regional outages**. They protect against rack-level failures, not region-level disasters. |
| **A virtual machine in a scale set** | Azure Key Vault is a **PaaS service** and is not hosted on user-managed VMs or VM scale sets. Scale sets provide compute scalability, not redundancy for PaaS services like Key Vault. |

### Key Vault Availability and Redundancy

| Feature | Description |
|---------|-------------|
| **Regional Service** | Key Vault is deployed in a specific region. |
| **Data Replication** | Contents are replicated to the **paired region** (if available) for durability. |
| **Failover Mechanism** | Microsoft-managed manual failover in case of critical regional disaster. |
| **Read-Only Access** | During failover, the vault in the paired region is in **read-only mode**. |
| **Failback** | Once the primary region is restored, Microsoft fails back the service. |

### Key Takeaway

Azure Key Vault provides high availability and disaster recovery through **geo-redundancy**. If a region becomes unavailable, the service fails over to the **paired region**. This process is managed by Microsoft and does not require user intervention, but users should be aware that the service might be in read-only mode during the failover period.

### Reference(s)

- [Azure Key Vault Disaster Recovery Guidance](https://learn.microsoft.com/en-us/azure/key-vault/general/disaster-recovery-guidance)
- [Azure Key Vault Overview](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)

---

## Question 8: Authorizing App to Retrieve Secrets - Access Policy vs Role Assignment

### Scenario

**Contoso Ltd. Case Study (AZ-305)**

Contoso, Ltd. is a research company with a main office in Montreal. They have a single Azure subscription and an on-premises Active Directory domain named contoso.com. Contoso has a business partnership with Fabrikam, Inc.

**App1 Requirements:**
- App1 will be a Python web app hosted in Azure App Service requiring a Linux runtime
- App1 will access several services that require third-party credentials and access strings
- The credentials and access strings are stored in Azure Key Vault

**Security Requirements:**
- All secrets used by Azure services must be stored in Azure Key Vault
- Services that require credentials must have the credentials tied to the service instance
- The credentials must NOT be shared between services

**Question:** You need to recommend a solution to ensure that App1 can access the third-party credentials and access strings. The solution must meet the security requirements. What should you use to authorize App1 to retrieve secrets?

**Options:**

1. **An access policy** ✅ *Correct*

2. **A connected service** ❌ *Incorrect*

3. **A private link** ❌ *Incorrect*

4. **A role assignment** ❌ *Incorrect (in this context)*

### Explanation

**Correct Answer: An access policy**

An access policy is the mechanism that allows granular **data-plane permissions** on Azure Key Vault when not using Azure RBAC-based authorization. App1 accesses secrets and credentials stored in Key Vault, which is a **data-plane operation** (i.e., accessing the contents of the Key Vault).

To grant the managed identity of App1 permission to retrieve secrets (such as **Get** access to secrets), you must configure a Key Vault access policy specifically assigning that permission.

This approach aligns with the security requirement:
> "Services that require credentials must have the credentials tied to the service instance. The credentials must NOT be shared between services."

By using a **managed identity** for App1 and granting it an access policy with only the necessary permissions (like `Get` for secrets), each service instance has its own identity and credentials are tied to that specific service.

**Azure CLI Example - Granting Access Policy:**

```bash
# Get the managed identity's object ID
objectId=$(az webapp identity show --name App1 --resource-group myRG --query principalId -o tsv)

# Set the access policy for the managed identity
az keyvault set-policy --name myKeyVault \
  --object-id $objectId \
  --secret-permissions get list
```

**Bicep Example:**

```bicep
resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  name: 'add'
  parent: keyVault
  properties: {
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: app1ManagedIdentity.properties.principalId
        permissions: {
          secrets: ['get', 'list']
        }
      }
    ]
  }
}
```

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **A connected service** | Connected services are relevant to DevOps tooling (e.g., Azure DevOps service connections), not for authorizing an app to retrieve secrets from Key Vault. They are used to establish connections between Azure DevOps pipelines and Azure resources. |
| **A private link** | Private Link secures **network-level access**, ensuring traffic between App1 and Key Vault does not traverse the public internet. However, it does **not provide authorization** to access the secrets. Private Link addresses the "how to connect" question, not the "who can access" question. |
| **A role assignment** | Role assignments are used for **management-plane operations** by default. If the Key Vault is not configured to use Azure RBAC for authorization (which is not mentioned in the case study), role assignments would not grant data-plane access to secrets. |

### Management Plane vs Data Plane Operations

Understanding the difference between management plane and data plane is crucial for Key Vault authorization:

| Plane | Description | Authorization Method | Examples |
|-------|-------------|---------------------|----------|
| **Management Plane** | Operations on the Key Vault resource itself | Azure RBAC (Role Assignments) | Create/delete vault, configure access policies, modify vault properties |
| **Data Plane** | Operations on the contents inside the vault | Access Policies OR Azure RBAC (if enabled) | Get/set secrets, encrypt/decrypt with keys, manage certificates |

**Key Vault Permission Models Comparison:**

| Aspect | Vault Access Policy | Azure RBAC |
|--------|---------------------|------------|
| **Default for new vaults** | Yes (traditional) | No (must be enabled) |
| **Scope** | Per-vault | Subscription, resource group, or vault level |
| **Granularity** | Per-identity permissions | Role-based with inheritance |
| **Data Plane Access** | ✅ Yes | ✅ Yes (when enabled) |
| **Management Plane Access** | ❌ No | ✅ Yes |
| **Best for** | Simple scenarios, legacy apps | Enterprise scenarios, centralized management |

**When to Use Each Model:**

| Use Access Policies When | Use Azure RBAC When |
|--------------------------|---------------------|
| Key Vault RBAC is not enabled (default) | Key Vault RBAC is explicitly enabled |
| You need per-vault granular control | You need centralized access management |
| Working with legacy applications | Implementing enterprise governance |
| Simple single-vault scenarios | Managing multiple vaults consistently |

**Important Note:** If the Key Vault had RBAC authorization enabled, role assignments would be used to grant data-plane access (e.g., the **Key Vault Secrets User** role). But since the case study does not mention RBAC being used, access policies are the correct default answer.

### Key Takeaway

When authorizing an application to retrieve secrets from Azure Key Vault:

1. **Use Access Policies** when Key Vault is using the traditional (default) permission model
2. **Use Role Assignments** only when Azure RBAC is explicitly enabled on the Key Vault
3. **Private Link** secures network connectivity but does not provide authorization
4. **Connected Services** are for DevOps tooling, not application authorization

The recommended pattern is to use a **managed identity** for the application (like App1) and grant it the minimum required permissions through an access policy, ensuring credentials are tied to the specific service instance.

### Reference(s)

- [Azure Policy Overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Azure Key Vault Security Features](https://learn.microsoft.com/en-us/azure/key-vault/general/security-features)
- [Azure RBAC for Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
- [Azure Key Vault Network Security](https://learn.microsoft.com/en-us/azure/key-vault/general/network-security)
- [Azure Key Vault Overview](https://learn.microsoft.com/en-us/azure/key-vault/general/overview)

---

## Question 9: Securing VM Passwords in ARM Templates

### Scenario

You have downloaded an Azure Resource Manager (ARM) template to deploy numerous virtual machines (VMs). The ARM template is based on a current VM, but must be adapted to reference an administrative password. You need to ensure that the password cannot be stored in plain text.

**Question:** Which TWO components should you create?

### Explanation

**Correct Answers:**

1. ✅ **An Azure Key Vault**
2. ✅ **An Access Policy**

#### Solution Component 1: Azure Key Vault

You should create an **Azure Key Vault** to store the administrative password as a secret. Key Vault provides:

- **Secure storage** with encryption at rest and in transit
- **No plain text storage** - passwords are always encrypted
- **Centralized secret management** for all your applications
- **Integration with ARM templates** through parameter references
- **Audit logging** to track who accesses secrets and when
- **Secret rotation capabilities** without changing application code

**Key Vault Integration with ARM Templates:**

Key Vaults can be enabled for template deployment, allowing ARM templates to retrieve secrets during deployment without exposing them in template files.

#### Solution Component 2: Access Policy

You should create an **Access Policy** to control access to the Key Vault secrets. Access policies:

- **Specify who can access secrets** (users, applications, services)
- **Define permission levels** (Get, List, Set, Delete)
- **Ensure only authorized entities** can retrieve the administrative password
- **Control data plane operations** on secrets, keys, and certificates
- **Separate authorization from authentication** for fine-grained control

**Required Permissions for ARM Template Deployment:**
- The deployment identity needs **Get** permission on secrets
- The Key Vault must have `enabledForTemplateDeployment` set to `true`

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Entra ID Identity Protection** | This service detects and responds to identity-based security risks (compromised credentials, risky sign-ins). It does **not provide secure storage** for passwords in ARM templates. Identity Protection is about threat detection, not secret management. |
| **Azure Storage Account** | While Storage Accounts can store data, they are **not designed for secure secret management**. Storing passwords in blobs or files would require manual encryption and key management, lacking the built-in security features of Key Vault (access policies, audit logging, HSM backing). |
| **Azure Policy** | Azure Policy enforces compliance and governance rules across Azure resources. It **cannot store or manage sensitive data**. Policies are for ensuring resources meet organizational standards, not for secret storage. |
| **Backup Policy** | Backup Policies define backup schedules and retention periods for Azure resources. They are completely **unrelated to secret management** and provide no capability for secure password storage. |

### ARM Template Implementation

#### Step 1: Create Key Vault and Store Password

```bash
# Create the Key Vault
az keyvault create \
  --name myVaultName \
  --resource-group myResourceGroup \
  --location eastus \
  --enabled-for-template-deployment true

# Store the admin password
az keyvault secret set \
  --vault-name myVaultName \
  --name vmAdminPassword \
  --value 'YourSecurePassword123!'
```

#### Step 2: Configure Access Policy

```bash
# Grant access to deployment service principal
az keyvault set-policy \
  --name myVaultName \
  --spn <deployment-service-principal-id> \
  --secret-permissions get list
```

#### Step 3: Reference in ARM Template

**Template parameters file (parameters.json):**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "adminPassword": {
      "reference": {
        "keyVault": {
          "id": "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/myVaultName"
        },
        "secretName": "vmAdminPassword"
      }
    }
  }
}
```

**ARM template (template.json):**
```json
{
  "parameters": {
    "adminPassword": {
      "type": "securestring",
      "metadata": {
        "description": "VM administrator password from Key Vault"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2023-03-01",
      "name": "myVM",
      "properties": {
        "osProfile": {
          "adminPassword": "[parameters('adminPassword')]"
        }
      }
    }
  ]
}
```

### Key Vault Properties for Template Deployment

| Property | Purpose | Required for ARM Templates |
|----------|---------|---------------------------|
| `enabledForDeployment` | Allows Azure VMs to retrieve certificates from Key Vault during deployment | No |
| `enabledForTemplateDeployment` | Allows ARM templates to retrieve secrets during deployment | **Yes** |
| `enabledForDiskEncryption` | Allows Azure Disk Encryption to retrieve secrets | No |

### Security Best Practices

1. ✅ **Never store passwords in template files** - Always use Key Vault references
2. ✅ **Use `securestring` parameter type** - Ensures passwords are not logged
3. ✅ **Enable purge protection** - Prevents accidental permanent deletion of secrets
4. ✅ **Enable soft delete** - Allows recovery of deleted secrets
5. ✅ **Use managed identities** - Avoid storing service principal credentials
6. ✅ **Rotate secrets regularly** - Update Key Vault secrets without changing templates
7. ✅ **Monitor Key Vault access** - Use Azure Monitor and diagnostic logs
8. ✅ **Apply least privilege** - Grant only necessary permissions via access policies

### Key Takeaway

To securely deploy VMs with administrative passwords using ARM templates:

1. **Create an Azure Key Vault** and store the password as a secret
2. **Create an Access Policy** granting the deployment identity permission to retrieve secrets
3. **Enable the Key Vault** for template deployment (`enabledForTemplateDeployment: true`)
4. **Reference the secret** in your parameters file using Key Vault reference syntax
5. **Use `securestring`** parameter type in your ARM template

This approach ensures passwords are **never stored in plain text**, access is **controlled and auditable**, and secrets can be **rotated independently** from template deployments.

### Reference(s)

- [Use Azure Key Vault to pass secure parameter value during deployment](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/key-vault-parameter)
- [Azure Key Vault Security Features](https://learn.microsoft.com/en-us/azure/key-vault/general/security-features)
- [Integrate Key Vault with ARM Templates](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/template-tutorial-use-key-vault)