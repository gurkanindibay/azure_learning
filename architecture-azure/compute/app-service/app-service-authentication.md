# Azure App Service Authentication (Easy Auth)

## Table of Contents

- [Overview](#overview)
- [What is Easy Auth?](#what-is-easy-auth)
- [Supported Identity Providers](#supported-identity-providers)
- [Authentication Flow](#authentication-flow)
- [Configuring Unauthenticated Request Behavior](#configuring-unauthenticated-request-behavior)
  - [Available Actions](#available-actions)
  - [Require Authentication](#require-authentication)
  - [Allow Anonymous](#allow-anonymous)
  - [Return HTTP 401 Unauthorized](#return-http-401-unauthorized)
  - [Return HTTP 403 Forbidden](#return-http-403-forbidden)
  - [Redirect to Custom Page](#redirect-to-custom-page)
- [Group-Based Authorization with Microsoft Entra ID](#group-based-authorization-with-microsoft-entra-id)
  - [Overview](#overview-1)
  - [End-to-End Setup Process](#end-to-end-setup-process)
  - [Implementation Example](#implementation-example)
- [Managed Service Identity (Managed Identity)](#managed-service-identity-managed-identity)
  - [What is Managed Identity?](#what-is-managed-identity)
  - [Types of Managed Identities](#types-of-managed-identities)
  - [Using Managed Identity with Azure Key Vault](#using-managed-identity-with-azure-key-vault)
  - [Using Managed Identity with Other Azure Services](#using-managed-identity-with-other-azure-services)
  - [Managed Identity vs Service Principal](#managed-identity-vs-service-principal)
  - [Best Practices for Managed Identity](#best-practices-for-managed-identity)
- [Practice Questions](#practice-questions)
  - [Question 1: Blocking Unauthenticated Requests with Microsoft Entra ID](#question-1-blocking-unauthenticated-requests-with-microsoft-entra-id)
  - [Question 2: Token Validation in ASP.NET Core Web APIs](#question-2-token-validation-in-aspnet-core-web-apis)
  - [Question 3: Extending Session Expiration for App Service Authentication](#question-3-extending-session-expiration-for-app-service-authentication)
  - [Question 4: TLS Mutual Authentication Client Certificate Validation](#question-4-tls-mutual-authentication-client-certificate-validation)
  - [Question 5: Configuring Authorization with Microsoft Entra ID Group Membership Claims](#question-5-configuring-authorization-with-microsoft-entra-id-group-membership-claims)
  - [Question 6: Using Application Roles vs Group Claims for Authorization](#question-6-using-application-roles-vs-group-claims-for-authorization)
  - [Question 7: Securing App Service with Azure Key Vault and Managed Identity](#question-7-securing-app-service-with-azure-key-vault-and-managed-identity)
  - [Question 8: Enabling Single Sign-On for Entra ID Joined Devices](#question-8-enabling-single-sign-on-for-entra-id-joined-devices)
- [Token Validation for Web APIs](#token-validation-for-web-apis)
  - [Understanding Token Validation Libraries](#understanding-token-validation-libraries)
  - [Implementing JWT Validation](#implementing-jwt-validation)
- [Configuring Easy Auth with Azure CLI](#configuring-easy-auth-with-azure-cli)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure App Service provides built-in authentication and authorization support (commonly called "Easy Auth"), allowing you to sign in users and access data by writing minimal or no code in your web app, RESTful API, or mobile back end.

## What is Easy Auth?

Easy Auth is a feature that runs as a middleware component on the same VM as your App Service application. When enabled, every incoming HTTP request passes through it before being handled by your application code.

**Key Benefits:**
- No code changes required in your application
- Supports multiple identity providers out of the box
- Handles token validation, session management, and identity injection
- Works with any language or framework

## Supported Identity Providers

| Provider | Sign-in Endpoint | How-To Guidance |
|----------|------------------|-----------------|
| **Microsoft Entra ID** | `/.auth/login/aad` | Configure Microsoft Entra ID |
| **Microsoft Account** | `/.auth/login/microsoftaccount` | Configure Microsoft Account |
| **Facebook** | `/.auth/login/facebook` | Configure Facebook |
| **Google** | `/.auth/login/google` | Configure Google |
| **Twitter** | `/.auth/login/twitter` | Configure Twitter |
| **GitHub** | `/.auth/login/github` | Configure GitHub |
| **Apple** | `/.auth/login/apple` | Configure Apple |
| **OpenID Connect** | `/.auth/login/<providerName>` | Configure custom OpenID Connect provider |

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User Request Flow                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User ──► App Service ──► Easy Auth Middleware ──► Your Application │
│                               │                                      │
│                               ▼                                      │
│                    ┌─────────────────────┐                          │
│                    │  Authentication     │                          │
│                    │  Check              │                          │
│                    └─────────────────────┘                          │
│                               │                                      │
│              ┌────────────────┼────────────────┐                    │
│              ▼                ▼                ▼                    │
│         Authenticated    Unauthenticated   Token Refresh            │
│         (Pass through)   (Action based    (Auto refresh)            │
│                          on config)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Configuring Unauthenticated Request Behavior

When configuring Easy Auth, you must decide how the service handles unauthenticated requests. This is a critical security decision.

### Available Actions

| Action | Behavior | Use Case |
|--------|----------|----------|
| **Require authentication** | Blocks unauthenticated requests and redirects to sign-in | Secure apps requiring all users to authenticate |
| **Allow anonymous** | Passes unauthenticated requests to application | Mixed content apps with public and protected areas |
| **Return HTTP 401** | Returns 401 Unauthorized without redirect | APIs where clients handle authentication |
| **Return HTTP 403** | Returns 403 Forbidden | Explicitly deny access without authentication option |

### Require Authentication

**This is the recommended option when you want to block all unauthenticated access.**

When configured:
- All unauthenticated requests are blocked
- Users are automatically redirected to the identity provider sign-in page
- After successful authentication, users are redirected back to the original URL
- Provides the best user experience for web applications

```bash
# Configure Easy Auth with Microsoft Entra ID - Require Authentication
az webapp auth update \
  --name <app-name> \
  --resource-group <resource-group> \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-allowed-token-audiences https://<app-name>.azurewebsites.net
```

### Allow Anonymous

When configured:
- Unauthenticated requests pass through to your application
- Your application code must handle authentication checks
- Useful for apps with both public and protected content

```bash
# Configure Easy Auth to allow anonymous access
az webapp auth update \
  --name <app-name> \
  --resource-group <resource-group> \
  --enabled true \
  --action AllowAnonymous
```

### Return HTTP 401 Unauthorized

When configured:
- Unauthenticated requests receive HTTP 401 status
- No automatic redirect to sign-in
- Client applications must handle the 401 and initiate authentication
- **Creates poor user experience for browser-based apps** as users see an error instead of a login prompt

### Return HTTP 403 Forbidden

When configured:
- Unauthenticated requests receive HTTP 403 status
- Indicates the resource exists but access is denied
- No opportunity for authentication

### Redirect to Custom Page

When configured:
- Unauthenticated requests are redirected to a custom URL
- **Does not automatically enforce authentication**
- Requires additional implementation to ensure users actually authenticate
- The custom page must handle the authentication flow

## Group-Based Authorization with Microsoft Entra ID

### Overview

Group-based authorization allows you to control access to your Azure Web App based on a user's membership in Microsoft Entra ID (formerly Azure AD) groups. This approach enables you to implement role-based access control (RBAC) by mapping security groups to application roles or permission levels.

**Key Concepts:**
- **groupMembershipClaims**: A setting in the Microsoft Entra ID application manifest that controls whether group memberships are included in tokens
- **groups claim**: A claim in the JWT token that contains an array of group Object IDs the user belongs to
- **Role mapping**: Your application logic that maps group IDs to specific permissions or roles

### End-to-End Setup Process

#### Step 1: Create Microsoft Entra ID Groups

First, create security groups in Microsoft Entra ID that represent your permission levels:

```bash
# Create groups for different permission levels
az ad group create --display-name "WebApp-Admins" --mail-nickname "webapp-admins"
az ad group create --display-name "WebApp-Normal" --mail-nickname "webapp-normal"
az ad group create --display-name "WebApp-Readers" --mail-nickname "webapp-readers"

# Note the Object IDs returned - you'll need these for your application
```

#### Step 2: Assign Users to Groups

```bash
# Get user Object ID
USER_ID=$(az ad user show --id user@contoso.com --query id -o tsv)

# Get group Object ID
ADMIN_GROUP_ID=$(az ad group show --group "WebApp-Admins" --query id -o tsv)

# Add user to group
az ad group member add --group $ADMIN_GROUP_ID --member-id $USER_ID
```

#### Step 3: Register Microsoft Entra ID Application

```bash
# Create app registration
az ad app create \
  --display-name "MyWebApp" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "https://mywebapp.azurewebsites.net/.auth/login/aad/callback"

# Get the Application (client) ID
APP_ID=$(az ad app list --display-name "MyWebApp" --query [0].appId -o tsv)
```

#### Step 4: Configure groupMembershipClaims in Application Manifest

You need to modify the application manifest to include group memberships in tokens:

**Option A: Using Azure Portal**
1. Navigate to Azure Portal → Microsoft Entra ID → App registrations
2. Select your application
3. Click on "Manifest" in the left menu
4. Find the `groupMembershipClaims` property
5. Change the value from `null` to `"All"` or `"SecurityGroup"`
6. Click "Save"

**Option B: Using Azure CLI**

```bash
# Download the current manifest
az ad app show --id $APP_ID > manifest.json

# Edit manifest.json and change:
# "groupMembershipClaims": null
# to:
# "groupMembershipClaims": "All"

# Or use jq to modify it programmatically
jq '.groupMembershipClaims = "All"' manifest.json > manifest-updated.json

# Update the application
az ad app update --id $APP_ID --set groupMembershipClaims=All
```

**groupMembershipClaims Options:**

| Value | Description |
|-------|-------------|
| `null` | No groups included in tokens (default) |
| `"SecurityGroup"` | Only security groups included |
| `"All"` | Security groups, distribution groups, and directory roles |
| `"ApplicationGroup"` | Only groups assigned to the application |

#### Step 5: Configure App Service Authentication

```bash
# Enable App Service authentication with Microsoft Entra ID
az webapp auth update \
  --name mywebapp \
  --resource-group myResourceGroup \
  --enabled true \
  --action LoginWithAzureActiveDirectory \
  --aad-client-id $APP_ID \
  --aad-token-issuer-url "https://sts.windows.net/<tenant-id>/" \
  --token-store true
```

#### Step 6: Implement Authorization Logic in Your Application

Now implement the code to read group claims and determine permissions:

**ASP.NET Core Example:**

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Define your group IDs (get these from Azure Portal)
        var adminGroupId = "12345678-1234-1234-1234-123456789abc";
        var normalGroupId = "87654321-4321-4321-4321-cba987654321";
        var readerGroupId = "11111111-2222-3333-4444-555555555555";

        services.AddAuthorization(options =>
        {
            // Define policies based on group membership
            options.AddPolicy("AdminOnly", policy =>
                policy.RequireClaim("groups", adminGroupId));
                
            options.AddPolicy("NormalOrAbove", policy =>
                policy.RequireClaim("groups", adminGroupId, normalGroupId));
                
            options.AddPolicy("ReaderOrAbove", policy =>
                policy.RequireClaim("groups", adminGroupId, normalGroupId, readerGroupId));
        });

        services.AddControllersWithViews();
    }
}

// Use in controllers
[Authorize(Policy = "AdminOnly")]
public class AdminController : Controller
{
    public IActionResult Index()
    {
        return View();
    }
}

[Authorize(Policy = "ReaderOrAbove")]
public class ReportsController : Controller
{
    public IActionResult Index()
    {
        // Get user's groups from claims
        var groups = User.Claims
            .Where(c => c.Type == "groups")
            .Select(c => c.Value)
            .ToList();
            
        return View();
    }
}
```

**Node.js/Express Example:**

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();

// Group IDs from Microsoft Entra ID
const GROUPS = {
    admin: '12345678-1234-1234-1234-123456789abc',
    normal: '87654321-4321-4321-4321-cba987654321',
    reader: '11111111-2222-3333-4444-555555555555'
};

// Middleware to extract and validate groups
function checkGroupMembership(requiredGroups) {
    return (req, res, next) => {
        // App Service passes the JWT token in headers
        const token = req.headers['x-ms-token-aad-access-token'];
        
        if (!token) {
            return res.status(401).json({ error: 'Unauthorized' });
        }
        
        // Decode token (App Service already validated it)
        const decoded = jwt.decode(token);
        const userGroups = decoded.groups || [];
        
        // Check if user belongs to any required group
        const hasAccess = requiredGroups.some(group => 
            userGroups.includes(group)
        );
        
        if (!hasAccess) {
            return res.status(403).json({ error: 'Forbidden' });
        }
        
        req.user = {
            groups: userGroups,
            isAdmin: userGroups.includes(GROUPS.admin),
            isNormal: userGroups.includes(GROUPS.normal),
            isReader: userGroups.includes(GROUPS.reader)
        };
        
        next();
    };
}

// Use middleware in routes
app.get('/admin', 
    checkGroupMembership([GROUPS.admin]), 
    (req, res) => {
        res.json({ message: 'Admin area', user: req.user });
    }
);

app.get('/reports', 
    checkGroupMembership([GROUPS.admin, GROUPS.normal, GROUPS.reader]), 
    (req, res) => {
        res.json({ message: 'Reports area', user: req.user });
    }
);
```

#### Step 7: Test the Configuration

1. **Verify group claims in token:**

```bash
# Access the token endpoint (when logged in)
curl https://mywebapp.azurewebsites.net/.auth/me
```

The response should include the groups claim:

```json
[
  {
    "access_token": "eyJ0eXAiOi...",
    "user_claims": [
      {
        "typ": "groups",
        "val": "12345678-1234-1234-1234-123456789abc"
      },
      {
        "typ": "groups",
        "val": "87654321-4321-4321-4321-cba987654321"
      }
    ]
  }
]
```

2. **Test authorization:**
   - Log in as a user who is only in the "WebApp-Readers" group
   - Try to access an admin-only endpoint
   - Verify you receive a 403 Forbidden response
   - Access a reader-allowed endpoint and verify success

### Implementation Example

**Complete ASP.NET Core Implementation:**

```csharp
// Program.cs
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add Microsoft Entra ID authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

// Configure authorization policies
builder.Services.AddAuthorization(options =>
{
    var config = builder.Configuration.GetSection("Authorization:Groups");
    
    options.AddPolicy("RequireAdminRole", policy =>
        policy.RequireClaim("groups", config["Admin"]));
        
    options.AddPolicy("RequireNormalRole", policy =>
        policy.RequireClaim("groups", config["Admin"], config["Normal"]));
        
    options.AddPolicy("RequireReaderRole", policy =>
        policy.RequireClaim("groups", 
            config["Admin"], 
            config["Normal"], 
            config["Reader"]));
});

builder.Services.AddRazorPages();
builder.Services.AddControllers();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapRazorPages();
app.MapControllers();

app.Run();
```

```json
// appsettings.json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "CallbackPath": "/signin-oidc"
  },
  "Authorization": {
    "Groups": {
      "Admin": "12345678-1234-1234-1234-123456789abc",
      "Normal": "87654321-4321-4321-4321-cba987654321",
      "Reader": "11111111-2222-3333-4444-555555555555"
    }
  }
}
```

```csharp
// Controllers/AdminController.cs
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[Authorize(Policy = "RequireAdminRole")]
[ApiController]
[Route("api/[controller]")]
public class AdminController : ControllerBase
{
    [HttpGet]
    public IActionResult GetAdminData()
    {
        var userGroups = User.Claims
            .Where(c => c.Type == "groups")
            .Select(c => c.Value);
            
        return Ok(new 
        { 
            message = "Admin data",
            groups = userGroups 
        });
    }
}
```

**Key Considerations:**

1. **Group ID Limits**: If a user belongs to more than 200 groups, Microsoft Entra ID will not include the groups claim. Instead, it includes an `_claim_names` claim with a link to Microsoft Graph to retrieve groups.

2. **Token Size**: Including many groups can increase token size. Consider using `ApplicationGroup` instead of `All` if you only need specific groups.

3. **Security**: Store group IDs in configuration (Azure Key Vault, App Configuration) rather than hardcoding them.

4. **Caching**: Consider caching group membership lookups to improve performance.

5. **Testing**: Always test with users in different groups to ensure authorization logic works correctly.

## Managed Service Identity (Managed Identity)

### What is Managed Identity?

**Managed Identity** (formerly known as Managed Service Identity or MSI) is an Azure feature that provides Azure services with an automatically managed identity in Microsoft Entra ID. This identity can be used to authenticate to any service that supports Microsoft Entra ID authentication, without storing credentials in your code.

**Key Benefits:**
- ✅ **No credential management** - Azure automatically creates and manages the identity
- ✅ **Automatic rotation** - Credentials are rotated automatically by Azure
- ✅ **Zero secrets in code** - No need to store connection strings, passwords, or keys
- ✅ **Enhanced security** - Reduces the risk of credential leaks
- ✅ **Simplified configuration** - Easier to set up than service principals
- ✅ **Built-in compliance** - All access is logged for audit trails

**How It Works:**

```
┌─────────────────────────────────────────────────────────────────────┐
│              Managed Identity Authentication Flow                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. App Service enables Managed Identity                            │
│     └─► Azure creates identity in Entra ID                          │
│                                                                      │
│  2. Grant permissions to the identity                                │
│     └─► Assign RBAC roles or access policies                        │
│                                                                      │
│  3. App requests token from Azure Instance Metadata Service (IMDS)  │
│     └─► GET http://169.254.169.254/metadata/identity/oauth2/token   │
│                                                                      │
│  4. Azure returns access token                                       │
│     └─► Token is automatically managed and rotated                  │
│                                                                      │
│  5. App uses token to access Azure services                         │
│     └─► Key Vault, Storage, SQL Database, etc.                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Types of Managed Identities

Azure supports two types of managed identities:

#### 1. System-Assigned Managed Identity

A managed identity that is tied directly to an Azure resource. When you enable it, Azure creates an identity for the resource in the Microsoft Entra ID tenant.

**Characteristics:**
- ✅ **Lifecycle tied to resource** - Deleted when resource is deleted
- ✅ **One-to-one relationship** - Each resource has its own unique identity
- ✅ **Simple setup** - Just toggle "On" in Azure Portal
- ✅ **Strong isolation** - Each app has separate permissions
- ✅ **No management overhead** - Automatically cleaned up

**Enable System-Assigned Identity:**

```bash
# Enable system-assigned managed identity
az webapp identity assign \
    --name <app-name> \
    --resource-group <resource-group>

# Get the principal ID
az webapp identity show \
    --name <app-name> \
    --resource-group <resource-group> \
    --query principalId \
    --output tsv
```

**When to Use:**
- Single app accessing Azure services
- You want automatic cleanup when app is deleted
- Strong security isolation per application
- Simple scenarios with 1:1 mapping

#### 2. User-Assigned Managed Identity

A standalone Azure resource that can be assigned to one or more Azure resources. The identity's lifecycle is independent of the resources it's assigned to.

**Characteristics:**
- ✅ **Independent lifecycle** - Persists after resource deletion
- ✅ **Reusable** - Can be shared across multiple resources
- ✅ **Centralized management** - Single identity for multiple apps
- ✅ **Persistent permissions** - Permissions survive resource redeployment

**Create and Assign User-Assigned Identity:**

```bash
# Create user-assigned managed identity
az identity create \
    --name <identity-name> \
    --resource-group <resource-group>

# Get the identity resource ID
identityId=$(az identity show \
    --name <identity-name> \
    --resource-group <resource-group> \
    --query id \
    --output tsv)

# Assign to App Service
az webapp identity assign \
    --name <app-name> \
    --resource-group <resource-group> \
    --identities $identityId

# Get the principal ID for permission assignment
principalId=$(az identity show \
    --name <identity-name> \
    --resource-group <resource-group> \
    --query principalId \
    --output tsv)
```

**When to Use:**
- Multiple apps need the same permissions
- You want identity to persist across redeployments
- Centralized permission management
- Sharing access across different resource types

**Comparison:**

| Feature | System-Assigned | User-Assigned |
|---------|----------------|---------------|
| **Created by** | Enabling on resource | Explicit creation |
| **Lifecycle** | Tied to resource | Independent |
| **Can be shared** | ❌ No | ✅ Yes |
| **Cleanup** | Automatic | Manual |
| **Use case** | Single app | Multiple apps with same permissions |
| **Isolation** | ✅ Strong | ⚠️ Shared (less isolation) |
| **Management** | Per-resource | Centralized |

### Using Managed Identity with Azure Key Vault

Azure Key Vault is one of the most common use cases for Managed Identity, allowing you to securely store and retrieve secrets without embedding them in your code.

#### Step 1: Enable Managed Identity on App Service

```bash
# Enable system-assigned managed identity
az webapp identity assign \
    --name mywebapp \
    --resource-group myResourceGroup
```

#### Step 2: Grant Key Vault Access

You can grant access using either **Access Policies** (classic) or **RBAC** (recommended).

**Option A: Using Access Policies**

```bash
# Get the principal ID
principalId=$(az webapp identity show \
    --name mywebapp \
    --resource-group myResourceGroup \
    --query principalId \
    --output tsv)

# Grant Key Vault access
az keyvault set-policy \
    --name mykeyvault \
    --object-id $principalId \
    --secret-permissions get list \
    --key-permissions get list \
    --certificate-permissions get list
```

**Option B: Using RBAC (Recommended)**

```bash
# Enable RBAC on Key Vault (if not already enabled)
az keyvault update \
    --name mykeyvault \
    --resource-group myResourceGroup \
    --enable-rbac-authorization true

# Assign role to the managed identity
az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $principalId \
    --scope /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.KeyVault/vaults/mykeyvault
```

**Available Key Vault RBAC Roles:**

| Role | Permissions |
|------|-------------|
| **Key Vault Secrets User** | Read secret contents |
| **Key Vault Secrets Officer** | Read, write, delete secrets |
| **Key Vault Crypto User** | Perform cryptographic operations |
| **Key Vault Certificate User** | Read certificate contents |
| **Key Vault Reader** | Read metadata (not secret values) |

#### Step 3: Access Key Vault from Application Code

**C# / .NET:**

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Certificates;

public class KeyVaultService
{
    private readonly SecretClient _secretClient;
    private readonly KeyClient _keyClient;
    private readonly CertificateClient _certificateClient;

    public KeyVaultService(IConfiguration configuration)
    {
        var keyVaultUrl = configuration["KeyVault:Url"]; // https://mykeyvault.vault.azure.net/
        
        // DefaultAzureCredential automatically uses Managed Identity when running in Azure
        var credential = new DefaultAzureCredential();

        _secretClient = new SecretClient(new Uri(keyVaultUrl), credential);
        _keyClient = new KeyClient(new Uri(keyVaultUrl), credential);
        _certificateClient = new CertificateClient(new Uri(keyVaultUrl), credential);
    }

    // Get a secret
    public async Task<string> GetSecretAsync(string secretName)
    {
        KeyVaultSecret secret = await _secretClient.GetSecretAsync(secretName);
        return secret.Value;
    }

    // Get multiple secrets
    public async Task<Dictionary<string, string>> GetSecretsAsync(params string[] secretNames)
    {
        var secrets = new Dictionary<string, string>();
        
        foreach (var secretName in secretNames)
        {
            var secret = await _secretClient.GetSecretAsync(secretName);
            secrets[secretName] = secret.Value;
        }
        
        return secrets;
    }

    // Set a secret
    public async Task SetSecretAsync(string secretName, string secretValue)
    {
        await _secretClient.SetSecretAsync(secretName, secretValue);
    }
}

// Usage in Startup.cs / Program.cs
public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        
        // Register KeyVaultService
        builder.Services.AddSingleton<KeyVaultService>();
        
        var app = builder.Build();
        
        // Use KeyVault secrets in configuration
        var keyVaultService = app.Services.GetRequiredService<KeyVaultService>();
        var connectionString = await keyVaultService.GetSecretAsync("SqlConnectionString");
        
        app.Run();
    }
}
```

**Node.js / JavaScript:**

```javascript
const { SecretClient } = require('@azure/keyvault-secrets');
const { DefaultAzureCredential } = require('@azure/identity');

class KeyVaultService {
    constructor(keyVaultUrl) {
        // DefaultAzureCredential automatically uses Managed Identity in Azure
        const credential = new DefaultAzureCredential();
        this.client = new SecretClient(keyVaultUrl, credential);
    }

    // Get a secret
    async getSecret(secretName) {
        const secret = await this.client.getSecret(secretName);
        return secret.value;
    }

    // Get multiple secrets
    async getSecrets(...secretNames) {
        const secrets = {};
        for (const name of secretNames) {
            secrets[name] = await this.getSecret(name);
        }
        return secrets;
    }

    // Set a secret
    async setSecret(secretName, secretValue) {
        await this.client.setSecret(secretName, secretValue);
    }
}

// Usage
const keyVaultUrl = process.env.KEY_VAULT_URL; // https://mykeyvault.vault.azure.net/
const kvService = new KeyVaultService(keyVaultUrl);

// Get connection string
const connectionString = await kvService.getSecret('SqlConnectionString');

// Get multiple secrets
const secrets = await kvService.getSecrets('ApiKey', 'DatabasePassword', 'StorageAccount');
console.log(secrets.ApiKey);
```

**Python:**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class KeyVaultService:
    def __init__(self, key_vault_url):
        # DefaultAzureCredential automatically uses Managed Identity in Azure
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_url, credential=credential)
    
    def get_secret(self, secret_name):
        """Get a single secret"""
        secret = self.client.get_secret(secret_name)
        return secret.value
    
    def get_secrets(self, *secret_names):
        """Get multiple secrets"""
        return {name: self.get_secret(name) for name in secret_names}
    
    def set_secret(self, secret_name, secret_value):
        """Set a secret"""
        self.client.set_secret(secret_name, secret_value)

# Usage
key_vault_url = "https://mykeyvault.vault.azure.net/"
kv_service = KeyVaultService(key_vault_url)

# Get connection string
connection_string = kv_service.get_secret("SqlConnectionString")

# Get multiple secrets
secrets = kv_service.get_secrets("ApiKey", "DatabasePassword", "StorageAccount")
print(secrets["ApiKey"])
```

#### Common Key Vault Use Cases with Managed Identity

| Use Case | Secret Name Example | Description |
|----------|---------------------|-------------|
| **Database Connection** | `SqlConnectionString` | Store connection strings securely |
| **API Keys** | `OpenAI-ApiKey`, `Stripe-ApiKey` | Third-party service credentials |
| **OAuth Secrets** | `GitHub-ClientSecret` | OAuth client secrets for authentication |
| **Storage Accounts** | `StorageAccountKey` | Azure Storage access keys |
| **Service Principals** | `ServicePrincipal-Secret` | Credentials for other service principals |
| **Encryption Keys** | `DataEncryptionKey` | Keys for application-level encryption |
| **Certificates** | `TLS-Certificate` | SSL/TLS certificates |
| **Redis Cache** | `Redis-ConnectionString` | Cache connection strings |

### Using Managed Identity with Other Azure Services

Managed Identity can authenticate to any Azure service that supports Microsoft Entra ID authentication.

#### Azure SQL Database

```csharp
using Microsoft.Data.SqlClient;
using Azure.Identity;
using Azure.Core;

public class SqlService
{
    private readonly string _connectionString;
    
    public SqlService(IConfiguration configuration)
    {
        var server = configuration["Sql:Server"];
        var database = configuration["Sql:Database"];
        
        // Connection string without password
        _connectionString = $"Server={server}; Database={database}; Authentication=Active Directory Default;";
    }
    
    public async Task<List<Product>> GetProductsAsync()
    {
        using var connection = new SqlConnection(_connectionString);
        await connection.OpenAsync();
        
        using var command = new SqlCommand("SELECT * FROM Products", connection);
        using var reader = await command.ExecuteReaderAsync();
        
        var products = new List<Product>();
        while (await reader.ReadAsync())
        {
            products.Add(new Product
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1)
            });
        }
        
        return products;
    }
}
```

**Grant SQL Access:**

```sql
-- Connect to SQL Database as an admin and run:
CREATE USER [mywebapp] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [mywebapp];
ALTER ROLE db_datawriter ADD MEMBER [mywebapp];
```

#### Azure Storage

```csharp
using Azure.Identity;
using Azure.Storage.Blobs;

public class StorageService
{
    private readonly BlobServiceClient _blobServiceClient;
    
    public StorageService(IConfiguration configuration)
    {
        var storageAccountUrl = configuration["Storage:Url"]; // https://mystorageaccount.blob.core.windows.net/
        
        // Use Managed Identity to authenticate
        var credential = new DefaultAzureCredential();
        _blobServiceClient = new BlobServiceClient(new Uri(storageAccountUrl), credential);
    }
    
    public async Task<string> UploadFileAsync(string containerName, string fileName, Stream content)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        await containerClient.CreateIfNotExistsAsync();
        
        var blobClient = containerClient.GetBlobClient(fileName);
        await blobClient.UploadAsync(content, overwrite: true);
        
        return blobClient.Uri.ToString();
    }
}
```

**Grant Storage Access:**

```bash
# Assign Storage Blob Data Contributor role
az role assignment create \
    --role "Storage Blob Data Contributor" \
    --assignee $principalId \
    --scope /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.Storage/storageAccounts/mystorageaccount
```

#### Azure Service Bus

```csharp
using Azure.Identity;
using Azure.Messaging.ServiceBus;

public class ServiceBusService
{
    private readonly ServiceBusClient _client;
    
    public ServiceBusService(IConfiguration configuration)
    {
        var serviceBusNamespace = configuration["ServiceBus:Namespace"]; // myservicebus.servicebus.windows.net
        
        var credential = new DefaultAzureCredential();
        _client = new ServiceBusClient(serviceBusNamespace, credential);
    }
    
    public async Task SendMessageAsync(string queueName, string message)
    {
        var sender = _client.CreateSender(queueName);
        await sender.SendMessageAsync(new ServiceBusMessage(message));
    }
}
```

**Grant Service Bus Access:**

```bash
# Assign Service Bus Data Sender role
az role assignment create \
    --role "Azure Service Bus Data Sender" \
    --assignee $principalId \
    --scope /subscriptions/<subscription-id>/resourceGroups/myResourceGroup/providers/Microsoft.ServiceBus/namespaces/myservicebus
```

#### Azure Cosmos DB

```csharp
using Microsoft.Azure.Cosmos;
using Azure.Identity;

public class CosmosDbService
{
    private readonly CosmosClient _client;
    
    public CosmosDbService(IConfiguration configuration)
    {
        var cosmosDbUrl = configuration["CosmosDb:Url"];
        
        var credential = new DefaultAzureCredential();
        _client = new CosmosClient(cosmosDbUrl, credential);
    }
    
    public async Task<T> GetItemAsync<T>(string databaseId, string containerId, string itemId, string partitionKey)
    {
        var container = _client.GetContainer(databaseId, containerId);
        var response = await container.ReadItemAsync<T>(itemId, new PartitionKey(partitionKey));
        return response.Resource;
    }
}
```

**Summary of Azure Services Supporting Managed Identity:**

| Service | SDK / Library | Required Role |
|---------|--------------|---------------|
| **Key Vault** | `Azure.Security.KeyVault.*` | Key Vault Secrets User |
| **SQL Database** | `Microsoft.Data.SqlClient` | SQL DB Contributor (or SQL User) |
| **Storage** | `Azure.Storage.Blobs` | Storage Blob Data Contributor |
| **Service Bus** | `Azure.Messaging.ServiceBus` | Service Bus Data Sender/Receiver |
| **Event Hubs** | `Azure.Messaging.EventHubs` | Event Hubs Data Sender/Receiver |
| **Cosmos DB** | `Microsoft.Azure.Cosmos` | Cosmos DB Built-in Data Contributor |
| **App Configuration** | `Azure.Data.AppConfiguration` | App Configuration Data Reader |
| **Container Registry** | `Azure.Containers.ContainerRegistry` | AcrPull |
| **Microsoft Graph** | `Microsoft.Graph` | Various Graph API permissions |

### Managed Identity vs Service Principal

Understanding when to use Managed Identity versus a Service Principal is crucial for secure Azure application design.

| Aspect | Managed Identity | Service Principal |
|--------|-----------------|-------------------|
| **Credential Storage** | ❌ Not required (Azure manages) | ✅ Required (secret or certificate) |
| **Credential Rotation** | ✅ Automatic | ❌ Manual |
| **Security Risk** | ✅ Low (no exposed secrets) | ⚠️ Higher (secret can leak) |
| **Setup Complexity** | ✅ Simple (one command) | ⚠️ Complex (create + store credentials) |
| **Use Case** | Azure resources (App Service, VMs, Functions) | Non-Azure apps, CI/CD pipelines, scripts |
| **Lifecycle Management** | ✅ Automatic (tied to resource) | ❌ Manual |
| **Multi-tenant Apps** | ❌ Not supported | ✅ Supported |
| **Cost** | ✅ Free | ✅ Free |
| **Audit Trail** | ✅ Built-in | ✅ Built-in |
| **When to Use** | **Always for Azure-hosted apps** | Only when Managed Identity isn't available |

**When You MUST Use Service Principal:**
- Applications running **outside Azure** (on-premises, other clouds)
- **CI/CD pipelines** (GitHub Actions, Azure DevOps) - though GitHub has OIDC option
- **Multi-tenant applications** that need to access customer tenants
- Legacy systems that don't support Managed Identity

**When to Use Managed Identity (Preferred):**
- ✅ Azure App Service
- ✅ Azure Functions
- ✅ Azure Virtual Machines
- ✅ Azure Container Instances
- ✅ Azure Kubernetes Service (AKS)
- ✅ Azure Logic Apps
- ✅ Azure Data Factory
- ✅ Any Azure resource that supports it

**Migration from Service Principal to Managed Identity:**

```bash
# Before (with Service Principal)
az webapp config appsettings set \
    --name mywebapp \
    --resource-group myResourceGroup \
    --settings \
    KeyVault__ClientId="<client-id>" \
    KeyVault__ClientSecret="<client-secret>" \
    KeyVault__TenantId="<tenant-id>"

# After (with Managed Identity)
# 1. Enable Managed Identity
az webapp identity assign \
    --name mywebapp \
    --resource-group myResourceGroup

# 2. Grant permissions (no secrets needed!)
principalId=$(az webapp identity show \
    --name mywebapp \
    --resource-group myResourceGroup \
    --query principalId \
    --output tsv)

az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $principalId \
    --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<kv-name>

# 3. Remove the secret app settings (no longer needed!)
az webapp config appsettings delete \
    --name mywebapp \
    --resource-group myResourceGroup \
    --setting-names KeyVault__ClientId KeyVault__ClientSecret KeyVault__TenantId
```

### Best Practices for Managed Identity

#### 1. Always Use DefaultAzureCredential

The `DefaultAzureCredential` class automatically uses the best available credential:
- Managed Identity when running in Azure
- Visual Studio credentials when developing locally
- Azure CLI credentials as fallback
- Environment variables if configured

```csharp
// ✅ Recommended - Works everywhere
var credential = new DefaultAzureCredential();

// ❌ Avoid - Only works with Managed Identity
var credential = new ManagedIdentityCredential();
```

#### 2. Prefer System-Assigned for Most Scenarios

System-assigned managed identities provide better security isolation:

```bash
# ✅ Recommended for single app scenarios
az webapp identity assign --name myapp --resource-group myRG

# ⚠️ Use only when multiple apps need same permissions
az webapp identity assign --name myapp --resource-group myRG --identities <user-assigned-id>
```

#### 3. Apply Least Privilege Principle

Grant only the minimum permissions needed:

```bash
# ✅ Good - Specific role for specific resource
az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $principalId \
    --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<kv>

# ❌ Bad - Too broad permissions
az role assignment create \
    --role "Contributor" \
    --assignee $principalId \
    --scope /subscriptions/<subscription-id>
```

#### 4. Use RBAC Instead of Access Policies for Key Vault

RBAC provides better granularity and integrates with Azure's permission model:

```bash
# ✅ Recommended - RBAC
az keyvault update --name mykeyvault --enable-rbac-authorization true
az role assignment create --role "Key Vault Secrets User" --assignee $principalId --scope <kv-scope>

# ⚠️ Legacy - Access Policies (being deprecated)
az keyvault set-policy --name mykeyvault --object-id $principalId --secret-permissions get list
```

#### 5. Test Locally with Azure CLI or Visual Studio

`DefaultAzureCredential` works locally without code changes:

```bash
# Login with Azure CLI
az login

# Your app will automatically use your Azure CLI credentials locally
# and Managed Identity when deployed to Azure
```

#### 6. Handle Transient Failures

Implement retry logic for token acquisition:

```csharp
using Polly;

var retryPolicy = Policy
    .Handle<Azure.RequestFailedException>()
    .WaitAndRetryAsync(3, retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));

await retryPolicy.ExecuteAsync(async () =>
{
    var secret = await secretClient.GetSecretAsync("MySecret");
    return secret.Value;
});
```

#### 7. Monitor and Audit Access

Enable diagnostic logging for Key Vault and other services:

```bash
# Enable Key Vault diagnostic logs
az monitor diagnostic-settings create \
    --name KeyVaultAudit \
    --resource <key-vault-resource-id> \
    --logs '[{"category": "AuditEvent", "enabled": true}]' \
    --workspace <log-analytics-workspace-id>
```

#### 8. Document Your Managed Identities

Maintain documentation of which identities have access to what resources:

```yaml
# Example: managed-identities.yml
app-services:
  - name: mywebapp
    managed-identity:
      type: system-assigned
      principal-id: "12345678-1234-1234-1234-123456789abc"
    permissions:
      - resource: keyvault/mykeyvault
        role: Key Vault Secrets User
      - resource: storage/mystorageaccount
        role: Storage Blob Data Contributor
```

#### 9. Separate Identities for Different Environments

Use different managed identities for dev, staging, and production:

```bash
# Development
az webapp identity assign --name mywebapp-dev --resource-group dev-rg

# Production
az webapp identity assign --name mywebapp-prod --resource-group prod-rg

# Different identities prevent dev apps from accessing prod resources
```

#### 10. Clean Up Unused Identities

Remove managed identities that are no longer needed:

```bash
# Remove system-assigned identity
az webapp identity remove --name myapp --resource-group myRG

# Delete user-assigned identity
az identity delete --name myidentity --resource-group myRG
```

## Practice Questions

### Question 1: Blocking Unauthenticated Requests with Microsoft Entra ID

**Question:** You are configuring Azure App Service authentication (Easy Auth) for a web app. Users should authenticate using their Microsoft Entra ID credentials from your organization's tenant. After successful authentication, unauthenticated requests should be blocked. Which action should you configure for unauthenticated requests?

**Options:**
- A) Require authentication
- B) Redirect to custom page
- C) Allow anonymous
- D) Return HTTP 401 Unauthorized

**Correct Answer: A) Require authentication**

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Require authentication** ✅ | The 'Require authentication' action ensures that all unauthenticated requests are blocked and users are redirected to sign in with Microsoft Entra ID before accessing the application. This provides the best user experience while enforcing security. |
| **B) Redirect to custom page** ❌ | Redirecting to a custom page doesn't automatically enforce authentication; it would require additional implementation to ensure users authenticate before accessing protected resources. |
| **C) Allow anonymous** ❌ | The 'Allow anonymous' action permits unauthenticated requests to pass through to the application, which does not meet the requirement to block unauthenticated access. |
| **D) Return HTTP 401 Unauthorized** ❌ | Returning HTTP 401 without redirecting to authentication would block access but wouldn't provide users a way to authenticate, creating a poor user experience. |

**Key Takeaway:** When you need to block unauthenticated access AND provide a seamless authentication experience, always choose **"Require authentication"**. This option both enforces security and handles the redirect to the identity provider automatically.

---

### Question 2: Token Validation in ASP.NET Core Web APIs

**Question:** You are developing a web API using ASP.NET Core that will be deployed to Azure App Service. The API must validate access tokens from client applications. You need to choose the appropriate method to validate the tokens. Which approach should you use?

**Options:**
- A) Use ASP.NET JWT middleware with IdentityModel extensions for .NET
- B) Use MSAL.NET to validate the tokens directly
- C) Use Azure App Service authentication module only
- D) Use Microsoft Graph SDK for token validation

**Correct Answer: A) Use ASP.NET JWT middleware with IdentityModel extensions for .NET**

**Explanation:**
ASP.NET Core web APIs should use the **ASP.NET JWT middleware** for token validation. The validation is done by the **IdentityModel extensions for .NET** library, not by MSAL.NET. This is the standard approach for validating access tokens in protected web APIs.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **MSAL.NET** | MSAL.NET is designed for **acquiring tokens**, not for validating them. Token validation in web APIs should be handled by middleware that can properly verify the token's signature, issuer, audience, and expiration. |
| **App Service authentication module only** | While App Service authentication (Easy Auth) can handle authentication, web APIs still need to implement **proper token validation in code** to verify the token's claims and ensure it's valid for the specific API. |
| **Microsoft Graph SDK** | Microsoft Graph SDK is for **calling Microsoft Graph API**, not for validating tokens. It doesn't provide token validation functionality needed for protecting your own web API. |

**Key Takeaway:** 
- **MSAL.NET** = Token **acquisition** (client-side)
- **IdentityModel extensions for .NET** = Token **validation** (server-side/API)
- **Microsoft Graph SDK** = Calling Graph API
- **Easy Auth** = Platform-level authentication, but doesn't replace code-level token validation in APIs

---

### Question 3: Extending Session Expiration for App Service Authentication

**Question:** You need to extend the session expiration for App Service authentication to allow users to remain authenticated for longer periods. What should you configure?

**Options:**
- A) Modify the access token lifetime in Azure AD
- B) Enable token auto-renewal in MSAL configuration
- C) Configure token lifetime policy in the application code
- D) Set token-refresh-extension-hours using Azure CLI

**Correct Answer: D) Set token-refresh-extension-hours using Azure CLI**

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Modify the access token lifetime in Azure AD** ❌ | The grace period applies only to the App Service authenticated session, not to the access tokens from the identity providers. No grace period exists for expired provider tokens. Modifying AD token lifetime won't affect App Service session. |
| **B) Enable token auto-renewal in MSAL configuration** ❌ | MSAL handles token renewal for acquired tokens but doesn't control App Service authentication session lifetime, which is managed separately by the App Service platform. |
| **C) Configure token lifetime policy in the application code** ❌ | Token lifetime for App Service authentication is managed at the platform level, not in application code. The session extension must be configured through App Service settings. |
| **D) Set token-refresh-extension-hours using Azure CLI** ✅ | To extend the default expiration window, run the following Azure CLI command in Azure Cloud Shell: `az webapp auth update --resource-group <group_name> --name <app_name> --token-refresh-extension-hours <hours>`, which extends the App Service authenticated session grace period. |

**Azure CLI Command:**

```bash
# Extend the token refresh extension hours
az webapp auth update \
  --resource-group <group_name> \
  --name <app_name> \
  --token-refresh-extension-hours <hours>
```

**Key Takeaway:** App Service authentication session lifetime is managed at the **platform level** using Azure CLI or Azure Portal settings, not through identity provider configurations (Azure AD), client libraries (MSAL), or application code. The `token-refresh-extension-hours` parameter specifically controls how long the App Service authenticated session remains valid.

---

### Question 4: TLS Mutual Authentication Client Certificate Validation

**Question:** You are developing an Azure Web App. You configure TLS mutual authentication for the web app. You need to validate the client certificate in the web app. Where is the client certificate located and what encoding type is used?

**Options:**
- A) Client certificate location: Client cookie. Encoding type: URL.
- B) Client certificate location: HTTP message body. Encoding type: Base64.
- C) Client certificate location: HTTP request header. Encoding type: Unicode.
- D) Client certificate location: HTTP request header. Encoding type: Base64.

**Correct Answer: D) Client certificate location: HTTP request header. Encoding type: Base64.**

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Client cookie with URL encoding** ❌ | Storing the client certificate in the client cookie with URL encoding is not a common or recommended practice for validating client certificates in an Azure Web App. Client certificates are typically transmitted in the HTTP request header for validation. |
| **B) HTTP message body with Base64 encoding** ❌ | Storing the client certificate in the HTTP message body with Base64 encoding is not a standard method for validating client certificates in an Azure Web App. Client certificates are usually sent in the HTTP request header for validation purposes. |
| **C) HTTP request header with Unicode encoding** ❌ | Storing the client certificate in the HTTP request header with Unicode encoding is not the correct approach. While client certificates are transmitted in the HTTP request header, Unicode encoding is not typically used for this purpose. |
| **D) HTTP request header with Base64 encoding** ✅ | Storing the client certificate in the HTTP request header with Base64 encoding is the correct method for validating client certificates in an Azure Web App. The client certificate is included in the `X-ARR-ClientCert` HTTP request header with Base64 encoding to ensure secure transmission and proper validation within the web application. |

**How TLS Mutual Authentication Works in Azure App Service:**

1. **Enable client certificates** - Configure your App Service to require client certificates
2. **Client sends certificate** - The client includes its certificate during the TLS handshake
3. **App Service forwards certificate** - The platform extracts the certificate and forwards it in the `X-ARR-ClientCert` request header
4. **Application validates** - Your application code reads and validates the Base64-encoded certificate from the header

**Code Example (C#):**

```csharp
public void ValidateClientCertificate(HttpRequest request)
{
    // Get the client certificate from the request header
    string clientCertHeader = request.Headers["X-ARR-ClientCert"];
    
    if (!string.IsNullOrEmpty(clientCertHeader))
    {
        // Decode the Base64-encoded certificate
        byte[] certBytes = Convert.FromBase64String(clientCertHeader);
        var certificate = new X509Certificate2(certBytes);
        
        // Validate the certificate (thumbprint, issuer, expiration, etc.)
        // ...
    }
}
```

**Key Takeaway:** In Azure App Service with TLS mutual authentication enabled, the client certificate is transmitted in the **`X-ARR-ClientCert` HTTP request header** using **Base64 encoding**. This allows your application code to extract and validate the certificate for authentication purposes.

---

### Question 5: Configuring Authorization with Microsoft Entra ID Group Membership Claims

**Question:** You are developing a website that will run as an Azure Web App. Users will authenticate by using their Microsoft Entra ID credentials. You plan to assign users one of the following permission levels for the website: `admin`, `normal`, and `reader`. A user's Microsoft Entra ID group membership must be used to determine the permission level. You need to configure authorization. 

**Solution:** Create a new Microsoft Entra ID application. In the application's manifest, set value of the `groupMembershipClaims` option to All. In the website, use the value of the groups claim from the JWT for the user to determine permissions. 

Does the solution meet the goal?

**Correct Answer: Yes**

**Explanation:** Yes, the solution meets the goal. By setting the `groupMembershipClaims` option to All in the Microsoft Entra ID application's manifest, all group memberships for the user will be included in the JWT token. This allows the website to access the groups claim from the JWT token and determine the user's permission level based on their group membership.

**Why the "No" Explanation is Incorrect:** The "No" explanation states that setting `groupMembershipClaims` to All includes group memberships but doesn't specify how to use them. However, the solution explicitly states "In the website, use the value of the groups claim from the JWT for the user to determine permissions," which provides the necessary logic to map group memberships to permission levels.

**Key Takeaway:** To include group membership information in JWT tokens for authorization purposes, set `groupMembershipClaims` to "All" in the Microsoft Entra ID application manifest. Your application code can then read the `groups` claim from the JWT to implement role-based access control.

---

### Question 6: Using Application Roles vs Group Claims for Authorization

**Question:** You are developing a website that will run as an Azure Web App. Users will authenticate by using their Microsoft Entra ID credentials. You plan to assign users one of the following permission levels for the website: `admin`, `normal`, and `reader`. A user's Microsoft Entra ID group membership must be used to determine the permission level. You need to configure authorization.

**Solution:** Create a new Microsoft Entra ID application. In the application's manifest, define application roles that match the required permission levels for the application. Assign the appropriate Microsoft Entra ID group to each role. In the website, use the value of the roles claim from the JWT for the user to determine permissions.

Does the solution meet the goal?

**Correct Answer: No**

**Explanation:** 

This solution **does NOT meet the goal** as stated. The question specifically asks to use "**Microsoft Entra ID group membership**" to determine permission levels. However, the proposed solution actually uses **Application Roles**, which is a different authorization mechanism.

**Why This Solution is Problematic:**

While the solution described would technically work for authorization, it misunderstands the distinction between two different approaches:

1. **Group-Based Authorization (What the question asks for):**
   - Uses the `groups` claim in the JWT
   - Requires setting `groupMembershipClaims` in the manifest
   - Application reads group Object IDs directly from the token
   - Groups are managed in Microsoft Entra ID independently of the application

2. **App Roles-Based Authorization (What the solution proposes):**
   - Uses the `roles` claim in the JWT
   - Requires defining `appRoles` in the application manifest
   - Groups are **assigned to roles**, creating an abstraction layer
   - Application reads role names from the token instead of group IDs

**The Correct Explanation:**

The "Yes" explanation is misleading because it states the solution "may not effectively determine the permission level based on group membership." This is inaccurate. The App Roles approach **can** effectively determine permissions, but it doesn't use group membership **directly** as the question requires—it uses groups assigned to roles, which is an indirect approach.

**Comparison of Both Approaches:**

| Aspect | Group Claims Approach | App Roles Approach |
|--------|----------------------|--------------------|
| **Claim Type** | `groups` | `roles` |
| **Manifest Setting** | `groupMembershipClaims: "All"` | Define `appRoles` array |
| **What's in Token** | Group Object IDs (GUIDs) | Role names (strings) |
| **Group Assignment** | Users/groups added to Entra ID groups | Groups assigned to app roles |
| **Application Logic** | Maps group IDs to permissions | Maps role names to permissions |
| **Decoupling** | Tight coupling to Entra ID groups | Abstraction layer between groups and permissions |
| **Meets Question Goal** | ✅ Yes - uses group membership directly | ❌ No - uses roles (groups assigned to roles) |

**When to Use Each Approach:**

**Use Group Claims When:**
- You want direct group membership authorization
- Your groups already exist and are managed in Entra ID
- You want to avoid defining roles in the application manifest
- The question specifically asks to use group membership

**Use App Roles When:**
- You want application-specific role names (more readable than GUIDs)
- You need to decouple application permissions from Entra ID group structure
- You want role names to appear in the Azure Portal UI for assignments
- You prefer semantic role names (`"Admin"`) over group IDs
- You need to support users being assigned to roles directly (not just groups)

**Implementation Comparison:**

**Group Claims Approach (Correct for this question):**

```json
// Application Manifest
{
  "groupMembershipClaims": "All"
}
```

```csharp
// Application Code - Maps group IDs to permissions
var adminGroupId = "12345678-1234-1234-1234-123456789abc";
var normalGroupId = "87654321-4321-4321-4321-cba987654321";
var readerGroupId = "11111111-2222-3333-4444-555555555555";

var userGroups = User.Claims
    .Where(c => c.Type == "groups")
    .Select(c => c.Value)
    .ToList();

if (userGroups.Contains(adminGroupId))
{
    // User has admin permissions
}
```

**App Roles Approach (What the solution proposes):**

```json
// Application Manifest
{
  "appRoles": [
    {
      "allowedMemberTypes": ["User"],
      "description": "Admin users have full access",
      "displayName": "Admin",
      "id": "<unique-guid>",
      "isEnabled": true,
      "value": "Admin"
    },
    {
      "allowedMemberTypes": ["User"],
      "description": "Normal users have standard access",
      "displayName": "Normal",
      "id": "<unique-guid>",
      "isEnabled": true,
      "value": "Normal"
    },
    {
      "allowedMemberTypes": ["User"],
      "description": "Readers have read-only access",
      "displayName": "Reader",
      "id": "<unique-guid>",
      "isEnabled": true,
      "value": "Reader"
    }
  ]
}
```

```csharp
// Application Code - Uses role names instead of group IDs
var roles = User.Claims
    .Where(c => c.Type == ClaimTypes.Role)
    .Select(c => c.Value)
    .ToList();

if (roles.Contains("Admin"))
{
    // User has admin permissions
}

// Or use role-based authorization
[Authorize(Roles = "Admin")]
public class AdminController : Controller { }
```

**Then Assign Groups to Roles (additional step not required for group claims):**
- Azure Portal → Enterprise Applications → Your App → Users and groups
- Add assignment → Select your Entra ID group → Select the role → Assign

**Key Takeaway:** 

When a question specifically asks to use **"Microsoft Entra ID group membership"** to determine permissions, you should use the **group claims approach** (`groupMembershipClaims` + `groups` claim). Using **App Roles** with groups assigned to those roles is a valid and often preferred authorization pattern in practice, but it doesn't directly answer the question as stated because it introduces an abstraction layer. The question tests your understanding of the difference between direct group-based authorization and role-based authorization with group assignments.

**Best Practice in Real-World Scenarios:**

While the group claims approach is what the question asks for, **App Roles are generally considered a best practice** for production applications because:
1. More maintainable (readable role names vs GUIDs)
2. Better separation of concerns (app roles vs infrastructure groups)
3. More flexible (users can be assigned directly or via groups)
4. Better Azure Portal UX for managing assignments

However, for exam questions, always answer based on what is explicitly asked, not what you would do in practice.

---

### Question 7: Securing App Service with Azure Key Vault and Managed Identity

**Question:** You are developing an e-Commerce Web App. You want to use Azure Key Vault to ensure that sign-ins to the e-Commerce Web App are secured by using Azure App Service authentication and Microsoft Entra ID. What should you do on the e-Commerce Web App?

**Options:**
1. Run the `az keyvault secret` command.
2. Enable Microsoft Entra ID Connect.
3. Enable Managed Service Identity (MSI).
4. Create a Microsoft Entra ID service principal.

**Correct Answer: 3) Enable Managed Service Identity (MSI).**

**Explanation:**

Enabling **Managed Service Identity (MSI)**, now commonly referred to as **Managed Identity**, on the e-Commerce Web App allows the App Service to authenticate to Azure services (including Azure Key Vault) without storing credentials in the code. This is essential for securing sign-ins to the e-Commerce Web App using Azure App Service authentication and Microsoft Entra ID.

**How Managed Identity Works with App Service and Key Vault:**

1. **Enable Managed Identity** on the App Service
2. **Grant Key Vault Access** to the Managed Identity (via access policies or RBAC)
3. **App Service authenticates to Key Vault** using its Managed Identity (no credentials needed)
4. **Retrieve secrets securely** for authentication configuration and other sensitive data

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|--------------|
| **Run the `az keyvault secret` command** ❌ | The `az keyvault secret` command is used to manage secrets in Azure Key Vault (create, read, update, delete), but it is not directly related to securing sign-ins to the e-Commerce Web App using Azure App Service authentication and Microsoft Entra ID. This command doesn't establish the authentication mechanism needed for the App Service to access Key Vault securely. |
| **Enable Microsoft Entra ID Connect** ❌ | Microsoft Entra ID Connect (formerly Azure AD Connect) is a tool used to synchronize on-premises Active Directory with Microsoft Entra ID in hybrid identity scenarios. It is not relevant to configuring authentication for an Azure Web App or enabling secure access to Key Vault. This option confuses hybrid identity synchronization with cloud application authentication. |
| **Create a Microsoft Entra ID service principal** ❌ | While creating a service principal could technically be used for authentication, it requires managing credentials (client secret or certificate), which defeats the purpose of using a secrets management solution like Key Vault. Managed Identity is the preferred approach because it eliminates the need to manage and rotate credentials manually. Service principals require storing secrets somewhere, creating a "chicken and egg" problem. |

**Managed Identity vs Service Principal:**

| Aspect | Managed Identity | Service Principal |
|--------|-----------------|-------------------|
| **Credential Management** | Automatic (Azure manages) | Manual (you manage) |
| **Secret Storage** | Not required | Required (secret or certificate) |
| **Rotation** | Automatic | Manual |
| **Security** | Higher (no exposed secrets) | Lower (risk of leaked credentials) |
| **Use Case** | Azure resources accessing Azure services | Applications running outside Azure, automation scripts |
| **Best Practice for App Service** | ✅ Recommended | ❌ Not recommended |

**Implementation Steps:**

**1. Enable Managed Identity on App Service:**

```bash
# Enable system-assigned managed identity
az webapp identity assign \
    --name <app-name> \
    --resource-group <resource-group>
```

**2. Grant Key Vault Access to the Managed Identity:**

```bash
# Get the principal ID of the managed identity
principalId=$(az webapp identity show \
    --name <app-name> \
    --resource-group <resource-group> \
    --query principalId \
    --output tsv)

# Grant Key Vault access (using Access Policies)
az keyvault set-policy \
    --name <keyvault-name> \
    --object-id $principalId \
    --secret-permissions get list

# OR grant Key Vault access (using RBAC - recommended)
az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $principalId \
    --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.KeyVault/vaults/<keyvault-name>
```

**3. Access Key Vault from Application Code:**

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

// Use DefaultAzureCredential which automatically uses Managed Identity in Azure
var client = new SecretClient(
    new Uri("https://<keyvault-name>.vault.azure.net/"),
    new DefaultAzureCredential());

// Retrieve a secret
KeyVaultSecret secret = await client.GetSecretAsync("ConnectionString");
string connectionString = secret.Value;
```

**Benefits of Using Managed Identity with Key Vault:**

1. **No credentials in code** - Eliminates the risk of exposing secrets in source code
2. **Automatic credential rotation** - Azure manages the identity credentials and rotates them automatically
3. **Simplified configuration** - No need to manage client secrets or certificates
4. **Enhanced security** - Follows the principle of least privilege with granular access control
5. **Audit trail** - All Key Vault access is logged for compliance and security monitoring

**Common Use Cases:**

- Storing database connection strings
- API keys and authentication tokens
- Certificates for HTTPS/TLS
- OAuth client secrets
- Encryption keys
- Any sensitive configuration data

**Key Takeaway:** 

To enable an Azure App Service to securely access Azure Key Vault for storing authentication secrets and configuration, you should **enable Managed Service Identity (Managed Identity)**. This provides a secure, credential-free way for your App Service to authenticate to Azure Key Vault without storing any secrets in your application code or configuration.

---

### Question 8: Enabling Single Sign-On for Entra ID Joined Devices

**Scenario:** You plan to deploy an Azure web app named App1 that will use Microsoft Entra ID authentication. App1 will be accessed from the internet by users at your company. All users have computers that run Windows 10 and are joined to Microsoft Entra ID. You need to recommend a solution to ensure that users can connect to App1 without being prompted for authentication and can access App1 only from company-owned computers.

**Question:** What should you recommend to enable users to connect to App1 without being prompted for authentication?

**Options:**
1. A Microsoft Entra app registration
2. A Microsoft Entra managed identity
3. Microsoft Entra Application Proxy

**Correct Answer: 1) A Microsoft Entra app registration**

**Explanation:**

A **Microsoft Entra app registration** is the correct solution because it allows App1 to be integrated with Microsoft Entra ID for authentication. When users' Windows 10 devices are Microsoft Entra joined and single sign-on (SSO) is configured properly (using modern authentication protocols like OpenID Connect or SAML), users can access the application without being prompted for credentials. The app registration enables this integration and defines permissions, redirect URIs, and authentication flows, which are essential for enabling seamless SSO.

**How SSO Works with Microsoft Entra App Registration:**

1. **App Registration** - Create an app registration in Microsoft Entra ID that represents App1
2. **Configure Authentication** - Set up OpenID Connect or SAML authentication flows in the app registration
3. **Device Join** - Users' Windows 10 devices are Microsoft Entra joined
4. **Seamless SSO** - When users access App1, their device credentials are automatically used for authentication
5. **No Prompt** - Users are signed in without entering credentials because their device is already authenticated

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **A Microsoft Entra managed identity** ❌ | Managed identities are used for allowing **Azure resources** (like VMs, App Services, Function Apps) to securely access other Azure services (like Key Vault, Storage, SQL Database) without needing credentials. They are **not used for user authentication or enabling single sign-on** for end-users accessing applications. Managed identities provide service-to-service authentication, not user authentication. |
| **Microsoft Entra Application Proxy** ❌ | Microsoft Entra Application Proxy is used to provide **remote access to on-premises applications** by publishing them through Azure. Since App1 is a web app deployed in Azure (not on-premises), Application Proxy is not needed. Application Proxy is specifically designed for hybrid scenarios where you need to expose internal, on-premises web applications to external users securely. |

**Comparison of Microsoft Entra Components:**

| Component | Purpose | Use Case |
|-----------|---------|----------|
| **App Registration** | Integrate applications with Entra ID for user authentication and SSO | Web apps, mobile apps, APIs that need user authentication |
| **Managed Identity** | Allow Azure resources to authenticate to Azure services without credentials | App Service accessing Key Vault, Function App accessing Storage |
| **Application Proxy** | Provide secure remote access to on-premises applications | Publishing internal SharePoint, internal web apps to external users |

**Complete Solution for SSO with Device Restrictions:**

To fully meet the requirements (SSO + company-owned devices only), you would need:

1. **Microsoft Entra App Registration** ✅ - Enables SSO for authenticated users
2. **Conditional Access Policy** - Restrict access to Microsoft Entra joined or compliant devices
3. **Device Compliance Policies** - Define what constitutes a "company-owned" device

**Implementation Steps:**

**1. Create App Registration:**

```bash
# Create app registration
az ad app create \
    --display-name "App1" \
    --sign-in-audience AzureADMyOrg \
    --web-redirect-uris "https://app1.azurewebsites.net/.auth/login/aad/callback"

# Get the Application (client) ID
appId=$(az ad app list --display-name "App1" --query "[0].appId" -o tsv)
```

**2. Configure App Service Authentication:**

```bash
# Enable Easy Auth with the app registration
az webapp auth microsoft update \
    --name app1 \
    --resource-group myResourceGroup \
    --client-id $appId \
    --issuer "https://login.microsoftonline.com/<tenant-id>/v2.0" \
    --allowed-audiences "api://$appId"

# Require authentication for all requests
az webapp auth update \
    --name app1 \
    --resource-group myResourceGroup \
    --enabled true \
    --action LoginWithAzureActiveDirectory
```

**3. Create Conditional Access Policy for Device Compliance:**

In Microsoft Entra admin center:
- Navigate to **Security** → **Conditional Access** → **Policies** → **New policy**
- **Users**: Select your organization's users
- **Target resources**: Select "App1" (the app registration)
- **Conditions** → **Device platforms**: Windows
- **Grant**: Require device to be marked as compliant OR Require Microsoft Entra joined device
- Enable policy

**Key Benefits of App Registration for SSO:**

| Benefit | Description |
|---------|-------------|
| **Seamless Authentication** | Users automatically signed in when accessing from Entra ID joined devices |
| **Modern Protocols** | Support for OpenID Connect, OAuth 2.0, SAML 2.0 |
| **Centralized Identity** | Single identity source for all organizational apps |
| **Conditional Access Integration** | Apply device compliance, location, risk-based policies |
| **No Credential Storage** | No passwords or credentials stored in the application |
| **Audit Trail** | All sign-ins logged in Entra ID sign-in logs |

**Key Takeaway:**

To enable **single sign-on for Azure web apps** where users from Microsoft Entra joined devices can access without authentication prompts, you must create a **Microsoft Entra app registration**. This establishes the trust relationship between your web app and Microsoft Entra ID, enabling modern authentication protocols and seamless SSO. Managed identities are for service-to-service authentication, not user authentication. Application Proxy is for on-premises app publishing, not for cloud-native Azure web apps.

**Reference:**
- [Microsoft Entra Application Proxy Overview](https://learn.microsoft.com/en-us/entra/identity/app-proxy/overview-what-is-app-proxy)
- [Microsoft Entra Managed Identities Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Configure App Service Authentication](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad)

---

## Token Validation for Web APIs

### Understanding Token Validation Libraries

When building protected web APIs, it's crucial to understand the purpose of different authentication libraries:

| Library | Purpose | Use Case |
|---------|---------|----------|
| **MSAL.NET** | Acquire tokens | Client applications that need to get tokens |
| **IdentityModel extensions for .NET** | Validate tokens | Web APIs that need to verify incoming tokens |
| **Microsoft.AspNetCore.Authentication.JwtBearer** | JWT middleware | ASP.NET Core apps that need to authenticate requests |
| **Microsoft Graph SDK** | Call Graph API | Applications that need to access Microsoft Graph |

### Implementing JWT Validation

**ASP.NET Core - Program.cs:**

```csharp
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.Identity.Web;

var builder = WebApplication.CreateBuilder(args);

// Add JWT Bearer authentication using Microsoft Identity Platform
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();
builder.Services.AddControllers();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
```

**appsettings.json:**

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "<your-tenant-id>",
    "ClientId": "<your-api-client-id>",
    "Audience": "api://<your-api-client-id>"
  }
}
```

**Protected Controller:**

```csharp
[ApiController]
[Route("api/[controller]")]
[Authorize]  // Requires valid JWT token
public class WeatherController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        // Access claims from the validated token
        var userId = User.FindFirst("oid")?.Value;
        var scope = User.FindFirst("scp")?.Value;
        
        return Ok(new { Message = "Protected data", UserId = userId });
    }
}
```

### Token Validation Process

The JWT middleware performs the following validations:

```
┌─────────────────────────────────────────────────────────────┐
│                    JWT Token Validation                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ✅ Signature Validation                                  │
│     └── Verify token signed by trusted issuer               │
│                                                              │
│  2. ✅ Issuer Validation                                     │
│     └── Check 'iss' claim matches expected issuer           │
│                                                              │
│  3. ✅ Audience Validation                                   │
│     └── Check 'aud' claim matches your API's client ID      │
│                                                              │
│  4. ✅ Expiration Validation                                 │
│     └── Check 'exp' claim to ensure token not expired       │
│                                                              │
│  5. ✅ Not Before Validation                                 │
│     └── Check 'nbf' claim to ensure token is active         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

> ⚠️ **Important**: Even when using Easy Auth at the platform level, your API code should still validate tokens to ensure proper claim verification and to avoid relying solely on infrastructure-level security.

## Configuring Easy Auth with Azure CLI

### Enable Authentication with Microsoft Entra ID

```bash
# Step 1: Create an App Registration in Microsoft Entra ID
az ad app create --display-name "<app-name>"

# Step 2: Configure Easy Auth on the App Service
az webapp auth microsoft update \
  --name <app-name> \
  --resource-group <resource-group> \
  --client-id <client-id> \
  --client-secret <client-secret> \
  --tenant-id <tenant-id> \
  --issuer https://login.microsoftonline.com/<tenant-id>/v2.0

# Step 3: Set authentication to require login
az webapp auth update \
  --name <app-name> \
  --resource-group <resource-group> \
  --enabled true \
  --action LoginWithAzureActiveDirectory
```

### Using Azure Portal

1. Navigate to your App Service in Azure Portal
2. Select **Authentication** from the left menu
3. Click **Add identity provider**
4. Select **Microsoft** as the identity provider
5. Configure the tenant and app registration settings
6. Under **Restrict access**, select **Require authentication**
7. Click **Add**

## Mixed Authentication: Public and Protected Routes

When you need some endpoints to be publicly accessible while others require authentication, use the **"Allow anonymous"** setting and handle authentication at the route/endpoint level in your application code.

### How It Works

| Configuration | Behavior |
|---------------|----------|
| **Easy Auth: Allow Anonymous** | All requests (authenticated or not) pass through to your app |
| **Your App Code** | Checks authentication on specific routes and enforces access |

### Example Scenarios

```
Public endpoints (no auth required):
  GET /api/products          → Anonymous ✅
  GET /api/health           → Anonymous ✅

Protected endpoints (auth required):
  POST /api/orders          → Requires authentication 🔐
  GET /api/user/profile     → Requires authentication 🔐
```

### Implementation Examples

**ASP.NET Core - Using `[Authorize]` and `[AllowAnonymous]` attributes:**

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    [HttpGet]
    [AllowAnonymous]  // Public endpoint
    public IActionResult GetProducts() { ... }

    [HttpPost]
    [Authorize]  // Requires authentication
    public IActionResult CreateProduct() { ... }
}
```

**Node.js/Express - Middleware-based:**

```javascript
// Public route
app.get('/api/products', (req, res) => { ... });

// Protected route with auth check
app.post('/api/orders', requireAuth, (req, res) => { ... });

function requireAuth(req, res, next) {
    if (!req.headers['x-ms-client-principal']) {
        return res.status(401).send('Unauthorized');
    }
    next();
}
```

### Azure CLI Configuration for Mixed Auth

```bash
# Enable Easy Auth with Allow Anonymous
az webapp auth update \
  --name <app-name> \
  --resource-group <resource-group> \
  --enabled true \
  --action AllowAnonymous
```

### Key Considerations

| Aspect | Detail |
|--------|--------|
| **Easy Auth Setting** | Set to "Allow anonymous" |
| **Token Availability** | If user IS authenticated, Easy Auth still provides tokens/claims in headers |
| **Your Responsibility** | Check `X-MS-CLIENT-PRINCIPAL` header or use framework auth |
| **Flexibility** | Full control over which routes require auth |

This approach gives you:
- ✅ Public pages/APIs (anonymous access)
- 🔐 Protected pages/APIs (require authentication)
- 🔄 Mixed pages (show different content based on auth status)

## Authentication vs Authorization with Easy Auth

When using **"Require authentication"**, Easy Auth handles authentication completely, but **authorization is still your responsibility**.

| Concern | Easy Auth Handles? | Your App Handles? |
|---------|-------------------|-------------------|
| **Authentication** (Who is the user?) | ✅ Yes - blocks unauthenticated requests | ❌ No need |
| **Authorization** (What can the user do?) | ❌ No | ✅ Yes - you must implement |

### What Easy Auth Does (with Require Authentication):
- ✅ Validates the user's identity
- ✅ Blocks all unauthenticated requests
- ✅ Passes user claims/tokens to your app via headers (`X-MS-CLIENT-PRINCIPAL`)

### What Your App Still Needs to Do:
- 🔐 **Authorization logic** - Check if the authenticated user has permission to access a specific resource
- 👤 **Role-based access** - "Is this user an Admin or a Reader?"
- 📦 **Resource-level permissions** - "Can this user edit THIS specific order?"

## Implementing RBAC with Easy Auth

You can implement **Role-Based Access Control (RBAC)** by leveraging **App Roles** from Microsoft Entra ID.

### Step 1: Define App Roles in App Registration

In Azure Portal → Microsoft Entra ID → App Registrations → Your App → App roles:

```json
{
  "appRoles": [
    {
      "id": "a1b2c3d4-...",
      "allowedMemberTypes": ["User"],
      "displayName": "Admin",
      "value": "Admin",
      "description": "Administrators can manage all resources"
    },
    {
      "id": "e5f6g7h8-...",
      "allowedMemberTypes": ["User"],
      "displayName": "Reader",
      "value": "Reader", 
      "description": "Readers can only view resources"
    }
  ]
}
```

### Step 2: Assign Users to Roles

Azure Portal → Enterprise Applications → Your App → Users and groups → Add user/group → Select role

### Step 3: Access Roles in Your Application

Easy Auth passes the roles in the `X-MS-CLIENT-PRINCIPAL` header (base64 encoded JSON).

**ASP.NET Core - Using `[Authorize(Roles)]` attribute:**

```csharp
[ApiController]
[Route("api/[controller]")]
public class AdminController : ControllerBase
{
    [HttpGet("users")]
    [Authorize(Roles = "Admin")]  // Only Admin role can access
    public IActionResult GetAllUsers() { ... }

    [HttpGet("reports")]
    [Authorize(Roles = "Admin,Reader")]  // Admin OR Reader can access
    public IActionResult GetReports() { ... }
}
```

**Reading Claims Manually from Easy Auth Headers:**

```csharp
[ApiController]
public class OrdersController : ControllerBase
{
    [HttpDelete("orders/{id}")]
    public IActionResult DeleteOrder(int id)
    {
        // Get the principal from Easy Auth header
        var principalHeader = Request.Headers["X-MS-CLIENT-PRINCIPAL"].FirstOrDefault();
        
        if (string.IsNullOrEmpty(principalHeader))
            return Unauthorized();

        var principal = JsonSerializer.Deserialize<ClientPrincipal>(
            Convert.FromBase64String(principalHeader));

        // Check roles
        if (!principal.Roles.Contains("Admin"))
        {
            return Forbid("Only Admins can delete orders");
        }

        // Proceed with deletion
        return Ok();
    }
}

public class ClientPrincipal
{
    public string IdentityProvider { get; set; }
    public string UserId { get; set; }
    public string UserDetails { get; set; }
    public IEnumerable<string> Roles { get; set; }
    public IEnumerable<ClientPrincipalClaim> Claims { get; set; }
}
```

**Node.js/Express - Middleware-based:**

```javascript
function requireRole(...allowedRoles) {
    return (req, res, next) => {
        const principalHeader = req.headers['x-ms-client-principal'];
        
        if (!principalHeader) {
            return res.status(401).send('Unauthorized');
        }

        const principal = JSON.parse(
            Buffer.from(principalHeader, 'base64').toString('utf8')
        );

        const userRoles = principal.claims
            .filter(c => c.typ === 'roles')
            .map(c => c.val);

        const hasRole = allowedRoles.some(role => userRoles.includes(role));
        
        if (!hasRole) {
            return res.status(403).send('Forbidden - insufficient role');
        }

        req.user = principal;
        next();
    };
}

// Usage
app.delete('/api/orders/:id', requireRole('Admin'), (req, res) => {
    // Only Admins reach here
});

app.get('/api/reports', requireRole('Admin', 'Reader'), (req, res) => {
    // Admins and Readers can access
});
```

### RBAC Implementation Summary

| Step | Where | Action |
|------|-------|--------|
| 1. Define Roles | Entra ID App Registration | Create App Roles |
| 2. Assign Roles | Enterprise Application | Assign users/groups to roles |
| 3. Enable Easy Auth | App Service | Set to "Require authentication" |
| 4. Read Roles | Your Application | Check `X-MS-CLIENT-PRINCIPAL` or use `[Authorize(Roles)]` |

## Best Practices

1. **Use "Require authentication" for secure applications** - This provides both security and a good user experience
2. **Use "Allow anonymous" carefully** - Only when you have mixed public/private content and handle auth in code
3. **Avoid "Return HTTP 401"** for web apps - It doesn't provide a way for users to authenticate
4. **Use HTTPS** - Always enable HTTPS-only to protect authentication tokens
5. **Configure token store** - Enable token store to cache tokens and reduce identity provider calls
6. **Set appropriate token lifetimes** - Balance security with user experience
7. **Use managed identities** - For backend service authentication, use managed identities instead of Easy Auth

## References

- [Authentication and authorization in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
- [Configure Microsoft Entra ID authentication](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad)
- [Authentication flows in App Service](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization#authentication-flow)
