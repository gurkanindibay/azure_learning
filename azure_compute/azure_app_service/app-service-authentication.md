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
- [Practice Questions](#practice-questions)
  - [Question 1: Blocking Unauthenticated Requests with Microsoft Entra ID](#question-1-blocking-unauthenticated-requests-with-microsoft-entra-id)
  - [Question 2: Token Validation in ASP.NET Core Web APIs](#question-2-token-validation-in-aspnet-core-web-apis)
  - [Question 3: Extending Session Expiration for App Service Authentication](#question-3-extending-session-expiration-for-app-service-authentication)
  - [Question 4: TLS Mutual Authentication Client Certificate Validation](#question-4-tls-mutual-authentication-client-certificate-validation)
  - [Question 5: Configuring Authorization with Microsoft Entra ID Group Membership Claims](#question-5-configuring-authorization-with-microsoft-entra-id-group-membership-claims)
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
