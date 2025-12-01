# Azure Identity Concepts: SP, SAMI, UAMI, and Certificate Renewal Flow
## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Service Principal (SP)](#2-service-principal-sp)
  - [Key Characteristics](#key-characteristics)
  - [Why Service Principals Are Needed](#why-service-principals-are-needed)
  - [Authentication with SP](#authentication-with-sp)
  - [Types of Service Principals](#types-of-service-principals)
    - [2.1 Application Service Principal](#21-application-service-principal)
    - [2.2 Managed Identity Service Principal](#22-managed-identity-service-principal)
    - [2.3 Legacy Service Principal](#23-legacy-service-principal)
- [2.4 When to Use Each Service Principal Type](#24-when-to-use-each-service-principal-type)
  - [Key Limitation: Managed Identities and Microsoft Graph](#key-limitation-managed-identities-and-microsoft-graph)
- [2.5 Conditional Access for Workload Identities](#25-conditional-access-for-workload-identities)
  - [Key Features](#key-features)
  - [Requirements](#requirements)
  - [Important Distinctions](#important-distinctions)
- [3. Managed Identities Overview](#3-managed-identities-overview)
- [4. System-Assigned Managed Identity (SAMI)](#4-system-assigned-managed-identity-sami)
  - [Characteristics](#characteristics)
  - [Use Case](#use-case)
- [5. User-Assigned Managed Identity (UAMI)](#5-user-assigned-managed-identity-uami)
  - [Characteristics](#characteristics-2)
  - [Why UAMI Is Managed](#why-uami-is-managed)
  - [Use Case Example](#use-case-example)
- [6. Use Case Scenarios: Choosing UAMI vs SAMI](#6-use-case-scenarios-choosing-uami-vs-sami)
  - [UAMI over SAMI](#uami-over-sami)
  - [SAMI over UAMI](#sami-over-uami)
- [7. Certificate Lifecycle and Renewal Flow](#7-certificate-lifecycle-and-renewal-flow)
  - [Certificate Authentication Flow](#certificate-authentication-flow)
  - [Certificate Renewal Flow (Managed Identity)](#certificate-renewal-flow-managed-identity)
  - [Certificate Renewal Flow (Service Principal via Certificate)](#certificate-renewal-flow-service-principal-via-certificate)
  - [Key Difference](#key-difference)
- [8. Summary Table](#8-summary-table)
- [9. Final Notes](#9-final-notes)
- [10. Central Managed Identity Certificate Renewal Service](#10-central-managed-identity-certificate-renewal-service)
  - [10.1 How It Works](#101-how-it-works)
  - [10.2 High-Level Flow](#102-high-level-flow)
  - [10.3 Why This Exists](#103-why-this-exists)
- [11. Discover the managed identities authentication flow](#11-discover-the-managed-identities-authentication-flow)
  - [11.1 How a system-assigned managed identity works with an Azure virtual machine](#111-how-a-system-assigned-managed-identity-works-with-an-azure-virtual-machine)
  - [11.2 How a user-assigned managed identity works with an Azure virtual machine](#112-how-a-user-assigned-managed-identity-works-with-an-azure-virtual-machine)
- [12. Common Exam Scenario: Multi-Tenant App with Microsoft Graph API](#12-common-exam-scenario-multi-tenant-app-with-microsoft-graph-api)
  - [Scenario](#scenario)
  - [Question](#question)
  - [Answer: Application Service Principal ✓](#answer-application-service-principal)
  - [Why Application Service Principal?](#why-application-service-principal)
  - [Why NOT Managed Identity?](#why-not-managed-identity)
  - [Why NOT Legacy Service Principal?](#why-not-legacy-service-principal)
  - [Architecture Flow](#architecture-flow)
  - [Key Takeaway](#key-takeaway)
- [13. Accessing Azure Key Vault Secrets with Azure SDK for .NET](#13-accessing-azure-key-vault-secrets-with-azure-sdk-for-net)
  - [Scenario](#scenario-1)
  - [Question](#question-1)
  - [Answer Options Analysis](#answer-options-analysis)
  - [Summary: Key Vault Access Best Practices](#summary-key-vault-access-best-practices)
  - [DefaultAzureCredential Authentication Order](#defaultazurecredential-authentication-order)
  - [Complete Example: Accessing Key Vault Secret in ASP.NET Core](#complete-example-accessing-key-vault-secret-in-aspnet-core)
  - [Key Takeaway](#key-takeaway-1)
- [14. Implementing Key Rotation in Azure Key Vault](#14-implementing-key-rotation-in-azure-key-vault)
  - [Scenario](#scenario-2)
  - [Question](#question-2)
  - [Answer Options Analysis](#answer-options-analysis-1)
  - [Summary: Key Vault Key Management Commands](#summary-key-vault-key-management-commands)
  - [Key Rotation Best Practices](#key-rotation-best-practices)
  - [Key Takeaway](#key-takeaway-2)


## 1. Introduction
This document explains the foundational Azure identity concepts required for securing applications and services:
- **Service Principal (SP)**
- **System-Assigned Managed Identity (SAMI)**
- **User-Assigned Managed Identity (UAMI)**
- **Certificate lifecycle and renewal flow**

Diagrams are included in ASCII format.

---

## 2. Service Principal (SP)
A **Service Principal** is the **identity** an application or service uses to authenticate against Azure Active Directory.

### Key Characteristics
- Represents an application or workload.
- Requires **credentials** (client secret or certificate).
- Azure AD issues access tokens to SPs.
- RBAC roles must be assigned to the SP to determine permissions.

### Why Service Principals Are Needed
RBAC determines **what** an identity can do, but not **who** the identity is. The SP provides the identity; RBAC provides the permissions.

### Authentication with SP
- SP authenticates using secret or certificate.
- Azure AD verifies credentials.
- Azure AD issues a token for accessing Azure resources.

```
[App] --(secret/certificate)--> [Azure AD] --(token)--> [Resource]
```

### Types of Service Principals

There are three types of service principals:

#### 2.1 Application Service Principal
- Created when an application is registered in Microsoft Entra ID
- Represents the application in each tenant where it's used
- The **application object** (single instance) lives in the home tenant
- The **application service principal** (multiple instances) exists in each tenant where the app is used
- Used to configure permissions for the application (e.g., Microsoft Graph API access)
- Required for multi-tenant applications to access resources in different tenants

**Use Case:** Multi-tenant App Service web app needing Microsoft Graph API access

```
[Home Tenant - Application Object]
         |
         | Registration
         v
[Tenant1 - Application SP] --grants--> [Microsoft Graph API]
[Tenant2 - Application SP] --grants--> [Microsoft Graph API]
```

#### 2.2 Managed Identity Service Principal
- Automatically created and managed by Azure
- Credentials handled entirely by Azure (no secrets to manage)
- Two types: System-Assigned (SAMI) and User-Assigned (UAMI)
- **Cannot** be used for multi-tenant scenarios or Microsoft Graph API delegation
- Best for Azure resource-to-resource authentication

#### 2.3 Legacy Service Principal
- Applications created before app registrations were introduced
- Apps created through legacy experiences
- Limited functionality compared to modern application service principals
- Not recommended for new applications

---

## 2.4 When to Use Each Service Principal Type

| Scenario | Use | Don't Use | Reason |
|----------|-----|-----------|--------|
| Multi-tenant app accessing Microsoft Graph API | **Application SP** | Managed Identity, Legacy | Application SP is designed for multi-tenant scenarios and can be granted API permissions |
| App Service accessing Azure Key Vault | SAMI or UAMI | Application SP | No need to manage credentials; Azure handles authentication |
| Multiple services sharing same identity | UAMI | SAMI, Application SP | UAMI can be assigned to multiple resources |
| Single VM accessing Storage | SAMI | UAMI, Application SP | Simplest setup for single-resource scenarios |
| CI/CD pipeline authentication | Application SP | Managed Identity | Pipelines run outside Azure and need explicit credentials |
| Delegated user permissions | Application SP | Managed Identity | Managed identities only support application permissions, not delegated |

### Key Limitation: Managed Identities and Microsoft Graph
**Managed Identities (SAMI and UAMI) cannot be used for:**
- Multi-tenant application scenarios
- Accessing Microsoft Graph API with delegated permissions
- Scenarios requiring explicit application registration in Microsoft Entra ID

**Reason:** Managed identities are designed for Azure resource-to-resource authentication within a single tenant. They don't support the application object/service principal separation needed for multi-tenant scenarios.

---

## 2.5 Conditional Access for Workload Identities

### What are Workload Identities?
**Workload identities** are identities used by software workloads (applications, services, scripts, containers) to authenticate and access other services and resources. In Microsoft Entra ID, workload identities include:
- **Application registrations and service principals**
- **Managed identities**

Unlike user identities (humans), workload identities represent non-human entities that need to authenticate programmatically.

### Conditional Access for Workload Identities
**Conditional Access for workload identities** is a feature that enables organizations to apply access policies to service principals, allowing security controls similar to those used for user identities.

### Key Features
- **IP-based blocking**: Block service principals from accessing resources when connecting from outside known public IP ranges
- **Single-tenant support**: Can be applied to single-tenant service principals registered in your tenant
- **Location-based controls**: Enforce location restrictions on automated workloads and applications

### Requirements
- **Workload Identities Premium licenses** are required to use Conditional Access for workload identities
- Service principals must be registered in your tenant

### Important Distinctions

| Feature | Applies To | Use Case |
|---------|------------|----------|
| **Conditional Access for workload identities** | Service Principals | ✅ Block service principals based on IP ranges, location controls for automated workloads |
| **Conditional Access for users** | User identities | ❌ Does NOT affect service principal authentication; user-scoped policies don't apply to service principals |
| **Azure AD Identity Protection** | Risk detection | ❌ Can detect risks but NOT designed for IP-based blocking of service principals |
| **Azure AD Privileged Identity Management (PIM)** | Privileged role management | ❌ Used for just-in-time access and role assignments, NOT location-based access controls |

### Exam Scenario

**Question:** A company needs to block service principals from accessing resources when connecting from outside known IP ranges. The company has Workload Identities Premium licenses. Which Conditional Access feature should they use?

**Answer:** ✅ **Conditional Access for workload identities**

**Why this is correct:**
- Specifically designed for service principal access control
- Enables blocking service principals from outside known public IP ranges
- Requires Workload Identities Premium licenses (which the company has)
- Applies to single-tenant service principals registered in your tenant

**Why other options are incorrect:**
- **Conditional Access for users**: User-scoped policies don't affect service principal authentication
- **Azure AD Identity Protection**: Detects risks but doesn't provide IP-based blocking for service principals
- **Azure AD PIM**: Manages privileged role assignments and just-in-time access, not location-based controls

---

## 3. Managed Identities Overview
Managed Identities (MI) are **Service Principals managed by Azure**. They provide the same identity constructs but automate the credential lifecycle.

Types:
- **System-Assigned Managed Identity (SAMI)**
- **User-Assigned Managed Identity (UAMI)**

Azure automatically:
- Generates and stores the certificate.
- Rotates the credential regularly.
- Issues tokens via local endpoints (IMDS/MSI).

You never create or handle secrets or certificates.

---

## 4. System-Assigned Managed Identity (SAMI)
A SAMI is created and tied to a specific Azure resource.

### Characteristics
- Lifecycle bound to the resource.
- Cannot be shared between services.
- Automatically created and deleted.

### Use Case
Ideal when only **one service** needs a managed identity.

```
[VM/App Service]
     |
     |--(Identity auto-created)
     V
[System-Assigned MI]
```

---

## 5. User-Assigned Managed Identity (UAMI)
A UAMI is an independent Azure resource and can be assigned to **multiple** services.

### Characteristics
- Acts as a shared identity.
- Useful for scaling, multi-instance, multi-region, or cross-service access.
- Still a Service Principal, but fully Azure-managed.

### Why UAMI Is Managed
Azure manages:
- Creation of the underlying SP
- Credential generation
- Credential rotation
- Secure storage

### Use Case Example
Multiple App Services, Functions, and Container Apps sharing the same identity for accessing Key Vault.

```
[App Service A] ----\
[App Service B] ----- > [UAMI]
[Function App] ------/
      |
      V
[Key Vault / Storage / SQL]
```

---

## 6. Use Case Scenarios: Choosing UAMI vs SAMI

### UAMI over SAMI
- Use when multiple resources (App Services, Functions, VMs, Containers) need the same identity to access shared secrets or APIs.
- Prefer for multi-region deployments that must start new instances with identical permissions without reconfiguring identities.
- Choose when you need to pre-provision the identity separately (e.g., during IAM reviews or policy enforcement) and attach it to workloads later.
- Ideal when you want to separate resource lifecycle from identity lifecycle, enabling identity reuse even if individual services are deleted.

### SAMI over UAMI
- Use when a single resource requires access and you want the simplest setup with Azure handling the identity from creation to cleanup.
- Prefer when you do not want to manage another Azure resource (the identity) and you can accept the identity being deleted when the host resource is deleted.
- Choose for short-lived or disposable workloads where creating a dedicated identity per resource matches the workload lifecycle and reduces scope for cross-service permissions.
- Ideal when you want to avoid assigning multiple resources the same permissions unintentionally; each resource gets isolated credentials.

## 7. Certificate Lifecycle and Renewal Flow
Service Principals (including Managed Identities) rely on **certificate-based credentials**.

For SPs:
- You create and manage certificates.
- You handle rotation.

For Managed Identities:
- Azure generates and rotates certificates **automatically**.

### Certificate Authentication Flow
```
[App]
   |
   | 1. Signs request with private key
   V
[Azure AD]
   |
   | 2. Verifies signature using SP public key
   V
[Azure AD issues access token]
```

### Certificate Renewal Flow (Managed Identity)

```
           (Azure Internal Operation)
                  +-----------+
                  | Azure AD  |
                  +-----------+
                         |
                 1. Generate new certificate
                         |
                 2. Update Service Principal
                         |
    +----------------------------------------------+
    | Azure Resource (VM, App Service, Function)    |
    +----------------------------------------------+
                         |
                 3. MSI/IMDS endpoint receives
                    updated identity metadata
                         |
                 4. App continues requesting tokens
                    (no code changes required)
```

### Certificate Renewal Flow (Service Principal via Certificate)
```
You: Generate new certificate
You: Upload new certificate to App Registration
You: Update hosted service to use new certificate
You: Restart/redeploy application
```

### Key Difference
**SP:** You manage everything.
**MI:** Azure manages everything.

---

## 8. Summary Table

| Feature | Service Principal | Application SP | SAMI | UAMI |
|--------|-------------------|----------------|------|------|
| Identity Type | Application identity | Multi-tenant app identity | Managed SP | Managed SP |
| Credential Type | Secret/Cert (manual) | Secret/Cert (manual) | Cert (Azure-managed) | Cert (Azure-managed) |
| Credential Rotation | Manual | Manual | Automatic | Automatic |
| Resource Lifecycle | Independent | Independent | Tied to single service | Independent, reusable |
| Multi-resource use | Yes | Yes | No | Yes |
| Multi-tenant support | Yes | Yes | No | No |
| Microsoft Graph API | Yes | Yes | Limited (app permissions only) | Limited (app permissions only) |
| Best For | General auth, CI/CD | Multi-tenant apps, Graph API | Single-resource workloads | Shared identity scenarios |

---

## 9. Final Notes
- Service Principal is the **foundation** identity.
- **Application Service Principal** is specifically for registered applications and multi-tenant scenarios.
- Managed Identities are **Service Principals with automated credential lifecycle**.
- UAMI is ideal for multi-service, multi-region, and zero-downtime deployments.
- Certificate rotation is fully handled by Azure for Managed Identities.
- **For multi-tenant apps accessing Microsoft Graph API, use Application Service Principal, not Managed Identity.**

---

## 10. Central Managed Identity Certificate Renewal Service
Azure uses an internal, centralized Managed Identity control plane to automatically handle certificate lifecycle for all Managed Identities (SAMI and UAMI).

### 10.1 How It Works
A distributed Azure-internal service manages:
- Certificate generation
- Certificate rotation
- Public key updates in Entra ID
- Secure distribution of new credentials to MSI/IMDS endpoints on compute resources

### 10.2 High-Level Flow
```
[Azure Managed Identity Control Plane]
        |
        | 1. Generate new certificate
        v
[Entra ID - Service Principal]
        |
        | 2. Update public key metadata
        v
[Azure Compute Resource (VM / App Service / Function)]
        |
        | 3. MSI agent fetches updated identity metadata
        v
[MSI Endpoint continues issuing tokens seamlessly]
```

### 10.3 Why This Exists
The centralized MI control plane ensures:
- Zero-downtime certificate rotation
- Secure handling of private keys
- Consistent identity state across regions
- Compliance with security and operational standards
- Fully automated lifecycle with no developer involvement

This automated system is **exclusive to Managed Identities**. Service Principals using secrets or certificates still require **manual credential rotation**.

## 11. Discover the managed identities authentication flow

### 11.1 How a system-assigned managed identity works with an Azure virtual machine
1. Azure Resource Manager receives a request to enable the system-assigned managed identity on a virtual machine.
2. Azure Resource Manager creates a service principal in Microsoft Entra ID for the identity of the virtual machine. The service principal is created in the Microsoft Entra tenant that's trusted by the subscription.
3. Azure Resource Manager configures the identity on the virtual machine by updating the Azure Instance Metadata Service identity endpoint with the service principal client ID and certificate.
4. After the virtual machine has an identity, use the service principal information to grant the virtual machine access to Azure resources. To call Azure Resource Manager, use role-based access control in Microsoft Entra ID to assign the appropriate role to the virtual machine service principal. To call Key Vault, grant your code access to the specific secret or key in Key Vault.
5. Your code that's running on the virtual machine can request a token from the Azure Instance Metadata service endpoint, accessible only from within the virtual machine: http://169.254.169.254/metadata/identity/oauth2/token
6. A call is made to Microsoft Entra ID to request an access token (as specified in step 5) by using the client ID and certificate configured in step 3. Microsoft Entra ID returns a JSON Web Token (JWT) access token.
7. Your code sends the access token on a call to a service that supports Microsoft Entra authentication.

### 11.2 How a user-assigned managed identity works with an Azure virtual machine
1. Azure Resource Manager receives a request to create a user-assigned managed identity.
2. Azure Resource Manager creates a service principal in Microsoft Entra ID for the user-assigned managed identity. The service principal is created in the Microsoft Entra tenant that's trusted by the subscription.
3. Azure Resource Manager receives a request to configure the user-assigned managed identity on a virtual machine and updates the Azure Instance Metadata Service identity endpoint with the user-assigned managed identity service principal client ID and certificate.
4. After the user-assigned managed identity is created, use the service principal information to grant the identity access to Azure resources. To call Azure Resource Manager, use role-based access control in Microsoft Entra ID to assign the appropriate role to the service principal of the user-assigned identity. To call Key Vault, grant your code access to the specific secret or key in Key Vault.
   
        Note: You can also do this step before step 3.
5. Your code that's running on the virtual machine can request a token from the Azure Instance Metadata Service identity endpoint, accessible only from within the virtual machine: http://169.254.169.254/metadata/identity/oauth2/token
6. A call is made to Microsoft Entra ID to request an access token (as specified in step 5) by using the client ID and certificate configured in step 3. Microsoft Entra ID returns a JSON Web Token (JWT) access token.
7. Your code sends the access token on a call to a service that supports Microsoft Entra authentication.

---

## 12. Common Exam Scenario: Multi-Tenant App with Microsoft Graph API

### Scenario
You have an Azure App Service web app (`app1`) registered as a **multi-tenant application** in Microsoft Entra ID tenant (`tenant1`). You need to grant `app1` permission to access the Microsoft Graph API in `tenant1`.

### Question
Which service principal should you use?

### Answer: Application Service Principal ✓

### Why Application Service Principal?
1. **Multi-tenant apps require application objects**: The app is registered in the home tenant (tenant1) with an application object.
2. **Service principal per tenant**: An application service principal is created in tenant1 (and any other tenant where the app is used).
3. **Permission configuration**: The application service principal in tenant1 is used to configure API permissions (like Microsoft Graph).
4. **Microsoft Graph API access**: Application service principals support both application permissions and delegated permissions for Graph API.

### Why NOT Managed Identity?
- **SAMI (System-Assigned Managed Identity)**: ❌
  - Designed for Azure resource-to-resource authentication within a single tenant
  - Cannot represent multi-tenant applications
  - Limited Microsoft Graph API support (application permissions only, no delegated)
  
- **UAMI (User-Assigned Managed Identity)**: ❌
  - Same limitations as SAMI for multi-tenant scenarios
  - Not designed for application registration and consent flows
  - Cannot be used to grant permissions across tenants

### Why NOT Legacy Service Principal?
- **Legacy SP**: ❌
  - Created before modern app registrations
  - Limited functionality
  - Not designed for Microsoft Graph API scenarios

### Architecture Flow
```
[app1 - Multi-tenant App Service]
         |
         | Registered in tenant1
         v
[Application Object in tenant1]
         |
         | Creates
         v
[Application Service Principal in tenant1]
         |
         | Granted permissions
         v
[Microsoft Graph API in tenant1]
```

### Key Takeaway
For **multi-tenant applications** requiring **Microsoft Graph API access**, always use **Application Service Principal**. Managed identities are for Azure resource authentication, not for multi-tenant app scenarios.

---

## 13. Accessing Azure Key Vault Secrets with Azure SDK for .NET

### Scenario
You are developing an application that needs to securely access a database connection string stored in Azure Key Vault. You need to retrieve the secret from the Key Vault using the Azure SDK for .NET.

### Question
Which of the following steps is necessary to retrieve the secret from the Key Vault using the Azure SDK for .NET?

### Answer Options Analysis

#### ✅ Correct Answer: Use `Azure.Identity.DefaultAzureCredential` with `SecretClient`

**Use the `Azure.Identity.DefaultAzureCredential` class to authenticate and then use the `SecretClient` class to access the secret.**

**Why this is correct:**
- `DefaultAzureCredential` is the **recommended way** to authenticate applications with Azure services, including Key Vault
- It automatically tries multiple authentication methods in order (Managed Identity, Visual Studio, Azure CLI, etc.)
- Once authenticated, the `SecretClient` class provides secure access to Key Vault secrets
- This approach follows Azure security best practices

**Implementation Example:**
```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

// Create a SecretClient using DefaultAzureCredential
var client = new SecretClient(
    new Uri("https://your-keyvault.vault.azure.net/"),
    new DefaultAzureCredential());

// Retrieve the secret
KeyVaultSecret secret = await client.GetSecretAsync("DatabaseConnectionString");
string connectionString = secret.Value;
```

**Required NuGet Packages:**
```bash
dotnet add package Azure.Identity
dotnet add package Azure.Security.KeyVault.Secrets
```

---

#### ❌ Incorrect: Use `SecretClient` with `TokenCredential` without authentication

**Use the `Azure.Security.KeyVault.Secrets.SecretClient` class with `TokenCredential` for accessing the secret, but do not need to authenticate the application.**

**Why this is WRONG:**
- While `SecretClient` with `TokenCredential` is a valid approach, **authentication is always required**
- Azure Key Vault requires authentication to ensure secure access to secrets
- Without proper authentication, unauthorized access would be possible
- `TokenCredential` is an abstract class that requires a concrete implementation (like `DefaultAzureCredential`)

**Key Point:** Authentication is **essential** to prevent unauthorized access to secrets stored in Azure Key Vault.

---

#### ❌ Incorrect: Use `Microsoft.Extensions.Configuration.AzureKeyVault` package

**Use the `Microsoft.Extensions.Configuration.AzureKeyVault` package to retrieve the secret automatically when the application starts.**

**Why this is NOT the best choice:**
- The `Microsoft.Extensions.Configuration.AzureKeyVault` package is designed for **configuration providers**, not direct secret access
- It's used to load configuration settings from Key Vault into `IConfiguration` at application startup
- For directly accessing secrets programmatically, `SecretClient` is the appropriate choice
- Different use case: configuration loading vs. direct secret retrieval

**When to use `Microsoft.Extensions.Configuration.AzureKeyVault`:**
```csharp
// Used for loading Key Vault secrets as configuration
builder.Configuration.AddAzureKeyVault(
    new Uri("https://your-keyvault.vault.azure.net/"),
    new DefaultAzureCredential());

// Access as configuration
var connectionString = configuration["DatabaseConnectionString"];
```

**When to use `SecretClient`:**
```csharp
// Used for direct, programmatic secret access
var client = new SecretClient(vaultUri, new DefaultAzureCredential());
var secret = await client.GetSecretAsync("DatabaseConnectionString");
```

---

#### ❌ Incorrect: Use `KeyVaultClient` without authentication

**Use the `KeyVaultClient` class to access the secret directly without any authentication.**

**Why this is WRONG:**
- `KeyVaultClient` is from the older `Microsoft.Azure.KeyVault` package (now deprecated)
- **Authentication is always required** for Key Vault access - this is a fundamental security requirement
- Accessing secrets without authentication would be a severe security vulnerability
- Azure Key Vault enforces authentication through Microsoft Entra ID

**Security Principle:** Never attempt to access Key Vault without proper authentication. Azure Key Vault is designed to protect sensitive information and requires verified identity before granting access.

---

### Summary: Key Vault Access Best Practices

| Approach | Recommended | Use Case |
|----------|-------------|----------|
| `DefaultAzureCredential` + `SecretClient` | ✅ Yes | Direct programmatic secret access |
| `SecretClient` without authentication | ❌ No | Authentication is always required |
| `Microsoft.Extensions.Configuration.AzureKeyVault` | ⚠️ Specific use | Loading secrets as app configuration |
| `KeyVaultClient` (deprecated) | ❌ No | Use modern `SecretClient` instead |

### DefaultAzureCredential Authentication Order

`DefaultAzureCredential` attempts authentication in this order:

1. **Environment Variables** - Uses `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
2. **Workload Identity** - For Kubernetes workloads
3. **Managed Identity** - System-assigned or User-assigned MI
4. **Visual Studio** - Uses VS credentials for local development
5. **Azure CLI** - Uses `az login` credentials
6. **Azure PowerShell** - Uses `Connect-AzAccount` credentials
7. **Interactive Browser** - Opens browser for interactive login

```
┌─────────────────────────────────────────────────────────┐
│           DefaultAzureCredential Flow                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Environment Variables ──► if found, use it         │
│           │                                             │
│           ▼ (not found)                                 │
│  2. Workload Identity ──────► if available, use it     │
│           │                                             │
│           ▼ (not available)                             │
│  3. Managed Identity ───────► if available, use it     │
│           │                                             │
│           ▼ (not available)                             │
│  4. Visual Studio ──────────► if signed in, use it     │
│           │                                             │
│           ▼ (not available)                             │
│  5. Azure CLI ──────────────► if logged in, use it     │
│           │                                             │
│           ▼ (not available)                             │
│  6. Azure PowerShell ───────► if connected, use it     │
│           │                                             │
│           ▼ (not available)                             │
│  7. Interactive Browser ────► prompt user login        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Complete Example: Accessing Key Vault Secret in ASP.NET Core

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var builder = WebApplication.CreateBuilder(args);

// Option 1: Direct SecretClient usage (recommended for specific secret access)
builder.Services.AddSingleton(sp =>
{
    var keyVaultUrl = builder.Configuration["KeyVault:Url"];
    return new SecretClient(new Uri(keyVaultUrl), new DefaultAzureCredential());
});

// Option 2: Configuration provider (for loading multiple secrets as configuration)
builder.Configuration.AddAzureKeyVault(
    new Uri(builder.Configuration["KeyVault:Url"]),
    new DefaultAzureCredential());

var app = builder.Build();

// Using SecretClient in a controller
app.MapGet("/api/data", async (SecretClient secretClient) =>
{
    var secret = await secretClient.GetSecretAsync("DatabaseConnectionString");
    // Use the secret value
    return Results.Ok("Secret retrieved successfully");
});

app.Run();
```

### Key Takeaway

**Always use `DefaultAzureCredential` with `SecretClient`** for accessing Azure Key Vault secrets in .NET applications. This approach:
- Provides seamless authentication across development and production environments
- Automatically uses the most appropriate credential based on the environment
- Follows Azure security best practices
- Supports Managed Identity in production (no secrets to manage)

---

## 14. Implementing Key Rotation in Azure Key Vault

### Scenario
You need to implement key rotation for an RSA key stored in Azure Key Vault. The new key version should be generated based on the key's rotation policy.

### Question
Which Azure CLI command should you use?

### Answer Options Analysis

#### ✅ Correct Answer: `az keyvault key rotate`

```bash
az keyvault key rotate --vault-name myvault --name mykey
```

**Why this is correct:**
- The `rotate` command specifically generates a new version of an existing key based on the key's rotation policy
- This is exactly what's required for implementing key rotation
- Azure Key Vault maintains all previous versions, allowing for seamless transition
- The rotation policy defines the key type, size, and other attributes for the new version

---

#### ❌ Incorrect: `az keyvault key create`

```bash
az keyvault key create --vault-name myvault --name mykey --kty RSA
```

**Why this is WRONG:**
- The `create` command would attempt to create a new key with the same name
- This would fail because the key already exists
- It doesn't generate a new version of an existing key
- Use `create` only for creating new keys, not for rotating existing ones

---

#### ❌ Incorrect: `az keyvault key import`

```bash
az keyvault key import --vault-name myvault --name mykey --pem-file newkey.pem
```

**Why this is WRONG:**
- The `import` command is used to import an externally generated key into Key Vault
- It doesn't generate a new version based on the rotation policy
- Use this when you have a key generated outside of Azure that you want to store in Key Vault

---

#### ❌ Incorrect: `az keyvault key backup`

```bash
az keyvault key backup --vault-name myvault --name mykey --file backup.key
```

**Why this is WRONG:**
- The `backup` command creates a backup file of the key for disaster recovery purposes
- It doesn't generate a new version or implement rotation
- Use this for creating backups that can be restored to another Key Vault in the same Azure geography

---

### Summary: Key Vault Key Management Commands

| Command | Purpose | Use Case |
|---------|---------|----------|
| `az keyvault key rotate` | Generate new key version | ✅ Key rotation based on rotation policy |
| `az keyvault key create` | Create a new key | Initial key creation |
| `az keyvault key import` | Import external key | Bringing externally generated keys into Key Vault |
| `az keyvault key backup` | Create backup file | Disaster recovery preparation |

### Key Rotation Best Practices

1. **Set up rotation policy** - Define automatic rotation schedule using `az keyvault key rotation-policy update`
2. **Use versioning** - Azure Key Vault maintains all key versions, enabling gradual migration
3. **Monitor rotation** - Set up alerts for rotation events using Azure Monitor
4. **Test rotation** - Validate that applications can handle key version changes gracefully

### Key Takeaway

**Use `az keyvault key rotate`** to generate a new version of an existing key based on its rotation policy. This command is specifically designed for key rotation scenarios and ensures compliance with security best practices for cryptographic key management.

---

End of Document

