# Microsoft Entra ID Authentication Integration Scenarios

## Overview

This document provides comprehensive guidance on integrating Microsoft Entra ID (formerly Azure Active Directory) for authentication in various application scenarios. It covers different authentication methods, protocols, and best practices for implementing secure user authentication across different application types.

---

## Table of Contents

1. [Authentication Methods Overview](#authentication-methods-overview)
   - [Certificate-Based Authentication (CBA)](#certificate-based-authentication-cba)
   - [FIDO2 Passwordless Authentication](#fido2-passwordless-authentication)
   - [Conditional Access Authentication Context](#conditional-access-authentication-context)
2. [Azure App Service Authentication (Easy Auth)](#azure-app-service-authentication-easy-auth)
3. [OpenID Connect and OAuth 2.0 Integration](#openid-connect-and-oauth-20-integration)
   - [MSAL Client Application Types](#msal-client-application-types)
4. [Microsoft Entra External ID (formerly Azure AD B2C)](#microsoft-entra-external-id-formerly-azure-ad-b2c)
5. [Microsoft Graph API Integration](#microsoft-graph-api-integration)
6. [Self-Hosted Identity Providers](#self-hosted-identity-providers)
7. [Comparison of Authentication Approaches](#comparison-of-authentication-approaches)
8. [Implementation Scenarios](#implementation-scenarios)
9. [Best Practices and Recommendations](#best-practices-and-recommendations)
10. [Exam Scenario Analysis](#exam-scenario-analysis)
    - [Question 1: Authentication with OpenID Connect](#exam-question-1-authentication-with-openid-connect)
    - [Question 2: App Service Authentication (Easy Auth)](#exam-question-2-app-service-authentication-easy-auth)
    - [Question 3: Group-Based Authorization for Azure Web Apps](#exam-question-3-group-based-authorization-for-azure-web-apps)
    - [Question 4: Configuring Entra ID for Azure Blob Storage with RBAC](#exam-question-4-configuring-entra-id-for-azure-blob-storage-with-rbac)
    - [Question 5: Configuring Multifactor Authentication for Web App](#exam-question-5-configuring-multifactor-authentication-for-web-app)

---

## Authentication Methods Overview

### What is Microsoft Entra ID?

Microsoft Entra ID (formerly Azure Active Directory) is Microsoft's cloud-based identity and access management service. It provides:

- **Authentication**: Verifying user identity
- **Authorization**: Determining user permissions
- **Single Sign-On (SSO)**: One login for multiple applications
- **Multi-Factor Authentication (MFA)**: Enhanced security
- **Conditional Access**: Policy-based access control
- **Identity Protection**: Threat detection and response

### Core Authentication Protocols

Microsoft Entra ID supports industry-standard authentication protocols:

| Protocol | Purpose | Use Case |
|----------|---------|----------|
| **OAuth 2.0** | Authorization framework | Delegated access to resources |
| **OpenID Connect** | Authentication layer on OAuth 2.0 | User authentication and SSO |
| **SAML 2.0** | XML-based authentication | Enterprise SSO, legacy apps |
| **WS-Federation** | Legacy Microsoft protocol | Older .NET applications |

### Certificate-Based Authentication (CBA)

**Certificate-Based Authentication (CBA)** allows users to authenticate to Microsoft Entra ID using X.509 certificates on their devices (such as smart cards or hardware tokens) instead of entering a username and password.

#### CBA Authentication Strength Configuration

A key configuration decision for CBA is whether to configure it as **single-factor** or **multifactor** authentication:

| Configuration | Description | MFA Behavior |
|---------------|-------------|--------------|
| **Single-factor** | Certificate provides one factor of authentication | Users must complete additional MFA step |
| **Multifactor** | Certificate satisfies MFA requirements on its own | No additional authentication required |

#### Configuring CBA as Multifactor Authentication

When you need to satisfy MFA requirements **without requiring users to provide additional authentication methods**, you must configure CBA as **multifactor authentication**.

**How it works:**
- The certificate alone counts as both "something you have" (the certificate/device) and "something you know" (the PIN to unlock the certificate)
- Users can complete MFA with their CBA authentication method
- No additional authentication factor is required

**Configuration in Microsoft Entra ID:**
1. Navigate to **Microsoft Entra admin center** → **Protection** → **Authentication methods**
2. Select **Certificate-based authentication**
3. Under **Authentication binding policy**, configure the authentication strength:
   - Set **Protection level** to **Multi-factor authentication**

#### Why Other CBA Configurations Are Incorrect

| Option | Why Incorrect |
|--------|---------------|
| **Configure CBA as single-factor authentication** | If CBA is configured as single-factor, users must use a second authentication method to satisfy MFA, which doesn't meet the requirement of satisfying MFA without additional methods. |
| **Configure CBA with conditional access exclusion** | Excluding CBA from conditional access would bypass security requirements rather than satisfying MFA requirements appropriately. This is a security anti-pattern. |
| **Configure CBA with password authentication** | Adding password authentication would require users to provide additional authentication beyond the certificate, which contradicts the requirement of not requiring additional methods. |

#### CBA Use Cases

✅ **Use CBA as multifactor when:**
- Users have smart cards or hardware tokens
- Need to satisfy MFA requirements with certificate alone
- Implementing phishing-resistant authentication
- Compliance requires hardware-based authentication

✅ **Use CBA as single-factor when:**
- Certificate is just one part of a broader MFA strategy
- Additional verification factors are required by policy
- Implementing defense-in-depth security model

> **Exam Tip:** When asked about configuring CBA to satisfy MFA requirements without requiring additional authentication methods, the answer is always to configure CBA as **multifactor authentication**. This allows the certificate alone to satisfy MFA requirements.

### FIDO2 Passwordless Authentication

**FIDO2 (Fast Identity Online 2)** is a passwordless authentication standard that allows users to sign in to Microsoft Entra ID using security keys or platform authenticators (like Windows Hello) instead of passwords.

#### FIDO2 Overview

FIDO2 security keys provide:
- **Phishing-resistant authentication**: Cryptographic proof tied to the specific website
- **Passwordless experience**: No passwords to remember or type
- **Hardware-based security**: Private keys stored securely on the device
- **Cross-platform support**: Works across different browsers and operating systems

#### FIDO2 Licensing Requirements

| Feature | License Required |
|---------|------------------|
| **FIDO2 registration and sign-in** | No license required (Free) |
| **Conditional Access enforcement** | Microsoft Entra ID Premium P1 or P2 |
| **Advanced reporting and monitoring** | Microsoft Entra ID Premium P2 |

> **Important:** Registration and passwordless sign-in with Microsoft Entra ID doesn't require a license, though Premium licenses enable additional features like enforcement through Conditional Access.

#### FIDO2 Security Key Registration Requirements

Before users can register a FIDO2 security key, certain prerequisites must be met:

| Requirement | Description |
|-------------|-------------|
| **FIDO2 enabled in authentication methods policy** | The FIDO2 authentication method must be enabled for users |
| **Recent MFA completion** | Users must complete MFA within the **past 5 minutes** before registering |
| **Supported browser** | Modern browsers (Edge, Chrome, Firefox, Safari) support FIDO2 |
| **Security key compatibility** | The security key must be FIDO2 certified |

#### Common FIDO2 Registration Issues

| Issue | Symptom | Root Cause |
|-------|---------|------------|
| **MFA not completed recently** | Registration fails | Users must complete MFA within 5 minutes before registration |
| **FIDO2 disabled in policy** | Registration option doesn't appear | FIDO2 must be enabled in authentication methods policy |
| **Unsupported browser** | Registration option may not appear | Use a modern browser that supports WebAuthn |
| **Missing license** | N/A | No license required for basic FIDO2 functionality |

#### Why MFA Must Be Completed Within 5 Minutes

Users must complete multifactor authentication (MFA) within the past five minutes before they can register a passkey (FIDO2). This is a **security requirement** to ensure:
- Proper user verification before allowing passwordless credential registration
- The person registering the security key is the legitimate account owner
- Protection against unauthorized credential registration

#### Why Other Registration Issues Are Less Likely

| Potential Cause | Why It's Less Likely |
|-----------------|---------------------|
| **Unsupported browser** | Most modern browsers support FIDO2 registration. This would typically result in the option not appearing rather than a registration failure. |
| **FIDO2 disabled in policy** | If FIDO2 were disabled in the authentication methods policy, the option to register FIDO2 security keys would not appear at all, rather than failing during the registration process. |
| **Missing Premium license** | Registration and passwordless sign-in don't require a license. Premium licenses only enable additional features like Conditional Access enforcement. |

#### Configuring FIDO2 in Microsoft Entra ID

**Enable FIDO2 Authentication Method:**
1. Navigate to **Microsoft Entra admin center** → **Protection** → **Authentication methods**
2. Select **FIDO2 security key**
3. Enable the method and configure target users/groups
4. Configure any key restrictions (optional)

#### FIDO2 Use Cases

✅ **Use FIDO2 when:**
- Implementing phishing-resistant authentication
- Users need passwordless sign-in experience
- High-security environments requiring hardware-based authentication
- Compliance requires strong authentication methods
- Reducing password-related helpdesk calls

⚠️ **Consider alternatives when:**
- Users don't have access to compatible security keys
- Budget constraints prevent security key distribution
- Legacy systems don't support WebAuthn

> **Exam Tip:** When users report they cannot register their FIDO2 security keys (registration fails), the most likely cause is that they have not completed multifactor authentication within the past five minutes. This MFA requirement ensures proper user verification before allowing passwordless credential registration.

### Conditional Access Authentication Context

**Conditional Access Authentication Context** is a feature in Microsoft Entra ID that enables applications to trigger step-up authentication for specific sensitive actions or resources, rather than requiring the same level of authentication for all operations.

#### Overview

Authentication contexts allow you to:
- **Define granular access controls**: Different authentication requirements for different actions within the same application
- **Implement step-up authentication**: Require additional verification (like MFA) when users perform sensitive operations
- **Create context-aware security**: Apply stronger authentication only when accessing sensitive data or performing critical actions

#### How Authentication Context Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Flow                                 │
│                                                                      │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Normal       │    │ Sensitive Action │    │ Token Request    │  │
│  │ Operations   │───►│ (e.g., financial │───►│ with acrs claim  │  │
│  │ (No step-up) │    │ data access)     │    │                  │  │
│  └──────────────┘    └──────────────────┘    └────────┬─────────┘  │
│                                                        │            │
└────────────────────────────────────────────────────────┼────────────┘
                                                         │
                                                         ▼
                          ┌──────────────────────────────────────────┐
                          │         Microsoft Entra ID               │
                          │                                          │
                          │  1. Receives token request with acrs     │
                          │  2. Evaluates Conditional Access policy  │
                          │  3. Triggers step-up authentication      │
                          │     (e.g., MFA) if required              │
                          │  4. Returns token with auth context      │
                          └──────────────────────────────────────────┘
```

#### Implementing Step-Up Authentication

To implement step-up authentication using authentication context:

**Step 1: Create Authentication Context in Microsoft Entra ID**
```plaintext
Microsoft Entra admin center → Protection → Conditional Access → Authentication context
1. Click "New authentication context"
2. Provide a name (e.g., "Require MFA for sensitive data")
3. Provide a description
4. Assign an ID (c1, c2, c3, etc.)
5. Publish to apps (make available to applications)
```

**Step 2: Create Conditional Access Policy**
```plaintext
1. Create a new Conditional Access policy
2. Under "Cloud apps or actions" → select "Authentication context"
3. Select your created authentication context
4. Under "Grant" → select "Require multifactor authentication"
5. Enable the policy
```

**Step 3: Reference in Application Using the acrs Claim**
```csharp
// Request a token with the authentication context
var scopes = new[] { "api://your-api/.default" };

// Include the acrs (authentication context class reference) claim
var claims = new ClaimsRequest();
claims.AccessToken.Add(new ClaimRequest
{
    Type = "acrs",
    Value = "c1"  // Your authentication context ID
});

var result = await app.AcquireTokenInteractive(scopes)
    .WithClaims(claims.ToString())
    .ExecuteAsync();
```

#### The acrs Claim

The **acrs** (Authentication Context Class Reference String) claim is the key mechanism for triggering authentication context-based policies:

| Property | Description |
|----------|-------------|
| **Claim Name** | `acrs` |
| **Purpose** | Tells Entra ID which authentication context to evaluate |
| **Values** | c1 through c99 (predefined context IDs) |
| **Trigger** | Include in token request to trigger Conditional Access evaluation |

#### Why Other Approaches Don't Work for Step-Up Authentication

| Approach | Why It's Incorrect |
|----------|-------------------|
| **Custom claim validation in application** | Can verify if MFA was completed but **cannot trigger step-up authentication on demand** for specific actions. The application can only read claims, not enforce new authentication requirements. |
| **Sign-in frequency session control** | Controls how often users must re-authenticate but **doesn't provide context-aware step-up authentication** for specific sensitive actions within an application. |
| **Named locations in Conditional Access** | Based on IP addresses or geographic locations, **not application-specific actions or contexts**. Cannot provide step-up authentication for sensitive operations. |

#### Use Cases for Authentication Context

✅ **Use authentication context when:**
- Users access sensitive financial data and need additional MFA
- Administrative actions require step-up authentication
- Compliance requires stronger authentication for specific operations
- Different security levels needed within the same application

#### Exam Scenario: Step-Up Authentication

**Question:** You need to implement step-up authentication in your application using Conditional Access authentication context. Users accessing sensitive financial data must complete additional authentication. What should you configure?

| Option | Correct? | Explanation |
|--------|----------|-------------|
| Implement custom claim validation in your application to check for MFA completion | ❌ | Custom claim validation can verify if MFA was completed but cannot trigger step-up authentication on demand for specific actions. This must be done through authentication context. |
| Configure a Conditional Access policy with a session control for sign-in frequency | ❌ | Sign-in frequency controls how often users must re-authenticate but doesn't provide context-aware step-up authentication for specific sensitive actions within an application. |
| **Create an authentication context in Microsoft Entra ID and reference it using the acrs claim in your application's token request** | ✅ | Authentication contexts allow applications to trigger step-up authentication by including the acrs claim in token requests, which causes Conditional Access to evaluate policies assigned to that specific authentication context and enforce additional requirements like MFA. |
| Create a named location in Conditional Access and require MFA for that location | ❌ | Named locations are based on IP addresses or geographic locations, not application-specific actions or contexts, so they cannot provide step-up authentication for sensitive operations. |

> **Exam Tip:** When implementing step-up authentication for specific sensitive actions within an application, always use **Conditional Access authentication context** with the **acrs claim**. This is the only approach that allows applications to dynamically trigger additional authentication requirements based on the action being performed.

---

## Azure App Service Authentication (Easy Auth)

### Overview

**Azure App Service Authentication**, commonly known as **Easy Auth**, is a built-in authentication and authorization feature of Azure App Service that allows you to sign in users and access data without writing any authentication code in your application.

### ✅ Recommended for Azure App Service Applications

Easy Auth is the **correct and recommended way** to configure authentication in Azure App Service applications using Microsoft Entra ID when you want a quick, secure, and code-free authentication solution.

### Why Easy Auth Is the Best Choice for App Service

1. **Zero Code Required**: Authentication is handled at the platform level
2. **Secure by Default**: Microsoft manages security best practices
3. **Quick Setup**: Configure in minutes through Azure Portal
4. **Multiple Providers**: Supports Entra ID, Facebook, Google, Twitter, and more
5. **Token Management**: Automatic token refresh and session management
6. **Built-in Authorization**: Works with App Service authorization policies

### How Easy Auth Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure App Service                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Authentication Module (Easy Auth)            │   │
│  │                                                           │   │
│  │    1. Intercepts all requests                            │   │
│  │    2. Validates authentication tokens                    │   │
│  │    3. Manages sessions automatically                     │   │
│  │    4. Handles token refresh                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Your Application Code                        │   │
│  │                                                           │   │
│  │    ✅ No authentication code needed                      │   │
│  │    ✅ User info available in request headers             │   │
│  │    ✅ Focus on business logic                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Authentication flow
                              ▼
              ┌────────────────────────────────┐
              │      Microsoft Entra ID        │
              │   (Identity Provider)          │
              └────────────────────────────────┘
```

### Authentication Flow with Easy Auth

```
┌──────────┐                                          ┌────────────────┐
│  User    │  1. Request protected resource           │  App Service   │
│  Browser ├─────────────────────────────────────────►│  (Easy Auth)   │
└──────────┘                                          └───────┬────────┘
                                                              │
     2. Redirect to Entra ID login                           │
     ◄────────────────────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────┐
│      Microsoft Entra ID        │
│  - User enters credentials     │
│  - MFA challenge (if enabled)  │
│  - Consent screen (if needed)  │
└───────────────┬────────────────┘
                │
     3. Return with authorization code
     │
     ▼
┌────────────────────────────────┐
│     App Service (Easy Auth)    │
│  - Exchanges code for tokens   │
│  - Validates tokens            │
│  - Creates session cookie      │
│  - Stores tokens in token store│
└───────────────┬────────────────┘
                │
     4. Redirect to original resource with session
     │
     ▼
┌────────────────────────────────┐
│     Your Application           │
│  - User is authenticated       │
│  - User info in headers        │
│  - Access tokens available     │
└────────────────────────────────┘
```

### Setting Up Easy Auth in Azure Portal

**Step 1: Navigate to Authentication Settings**
```plaintext
Azure Portal → App Service → Authentication
```

**Step 2: Add Identity Provider**
```plaintext
1. Click "Add identity provider"
2. Select "Microsoft" (for Entra ID)
3. Choose configuration options:
   - App registration type: Create new or use existing
   - Supported account types: Single tenant, multi-tenant, or any
4. Click "Add"
```

**Step 3: Configure Authentication Behavior**
```plaintext
Settings → Authentication:
- Restrict access: Require authentication
- Unauthenticated requests: Redirect to identity provider
- Token store: Enabled (recommended)
```

### Setting Up Easy Auth via Azure CLI

```bash
# Enable Easy Auth with Microsoft Entra ID
az webapp auth microsoft update \
    --name <your-app-name> \
    --resource-group <your-resource-group> \
    --client-id <your-app-registration-client-id> \
    --client-secret <your-client-secret> \
    --issuer https://login.microsoftonline.com/<tenant-id>/v2.0

# Configure authentication behavior
az webapp auth update \
    --name <your-app-name> \
    --resource-group <your-resource-group> \
    --enabled true \
    --action RedirectToLoginPage \
    --token-store true
```

### Accessing User Information in Your Application

Easy Auth automatically injects user information into request headers:

**HTTP Headers Available:**
| Header | Description |
|--------|-------------|
| `X-MS-CLIENT-PRINCIPAL-NAME` | Username/email |
| `X-MS-CLIENT-PRINCIPAL-ID` | User's object ID |
| `X-MS-CLIENT-PRINCIPAL-IDP` | Identity provider name |
| `X-MS-CLIENT-PRINCIPAL` | Base64-encoded JWT claims |
| `X-MS-TOKEN-AAD-ACCESS-TOKEN` | Access token (if token store enabled) |
| `X-MS-TOKEN-AAD-ID-TOKEN` | ID token |

**Example: Reading User Info in ASP.NET Core**
```csharp
[ApiController]
[Route("api/[controller]")]
public class UserController : ControllerBase
{
    [HttpGet("profile")]
    public IActionResult GetProfile()
    {
        // No authentication code needed - Easy Auth handles it!
        var userName = Request.Headers["X-MS-CLIENT-PRINCIPAL-NAME"].FirstOrDefault();
        var userId = Request.Headers["X-MS-CLIENT-PRINCIPAL-ID"].FirstOrDefault();
        
        return Ok(new { 
            Name = userName, 
            Id = userId,
            Message = "Authenticated via Easy Auth!"
        });
    }
}
```

**Example: Reading User Info in Node.js/Express**
```javascript
app.get('/api/profile', (req, res) => {
    // No authentication middleware needed!
    const userName = req.headers['x-ms-client-principal-name'];
    const userId = req.headers['x-ms-client-principal-id'];
    
    res.json({
        name: userName,
        id: userId,
        message: 'Authenticated via Easy Auth!'
    });
});
```

### When to Use Easy Auth

✅ **Use Easy Auth when:**
- Hosting on Azure App Service, Azure Functions, or Azure Container Apps
- Want quick authentication setup without code changes
- Need authentication for an existing application
- Building prototypes or MVPs
- Want platform-managed security
- Need multiple identity provider support

⚠️ **Consider other approaches when:**
- Need fine-grained control over authentication flow
- Require custom token validation logic
- Building for platforms other than Azure App Service
- Need offline authentication support

### Easy Auth vs Custom Authentication Code

| Aspect | Easy Auth | Custom Code (MSAL/OIDC) |
|--------|-----------|-------------------------|
| **Setup Time** | Minutes | Hours to days |
| **Code Changes** | None | Significant |
| **Maintenance** | Microsoft managed | Developer managed |
| **Flexibility** | Limited | Full control |
| **Security Updates** | Automatic | Manual |
| **Multiple Providers** | Built-in | Custom implementation |
| **Token Management** | Automatic | Manual |
| **Best For** | App Service apps | Any platform |

### ⚠️ Why Other Approaches Are NOT Recommended for This Scenario

#### ❌ Custom User Database with Manual Token Management

**Why this is WRONG:**
```plaintext
❌ Security vulnerabilities - easy to make mistakes
❌ Increased complexity - reinventing the wheel
❌ No SSO support - users must re-authenticate
❌ Missing enterprise features (MFA, Conditional Access)
❌ Maintenance burden - security updates on you
❌ Not scalable - hard to manage at enterprise level
```

#### ❌ Microsoft Entra External ID for Enterprise Apps

**Why this is NOT the best choice for this scenario:**
```plaintext
⚠️ External ID is designed for consumer-facing applications
⚠️ Requires additional configuration for enterprise scenarios
⚠️ More complex than needed for internal employee authentication
⚠️ Different pricing model (pay-per-authentication)
```

**When External ID IS appropriate:**
- Consumer/customer sign-up and sign-in
- Social identity provider integration (Facebook, Google)
- Custom branding requirements
- Self-service password reset for external users

#### ❌ Custom OAuth 2.0 with Self-Hosted Token Service

**Why this is NOT recommended:**
```plaintext
❌ Unnecessary complexity - Entra ID already provides OAuth 2.0
❌ Security responsibility shifts to you
❌ Loses Entra ID features (MFA, Conditional Access)
❌ No Microsoft ecosystem integration
❌ Higher operational overhead
❌ More attack surface to manage
```

---

## OpenID Connect and OAuth 2.0 Integration

### ✅ Recommended Approach for Most Applications

**OpenID Connect (OIDC)** built on top of **OAuth 2.0** is the **recommended method** for implementing user authentication with Microsoft Entra ID in modern applications.

### Why This Approach Is Recommended

1. **Industry Standard**: Widely adopted, well-documented, and proven
2. **Microsoft Support**: First-class support and extensive SDKs
3. **Security**: Modern security features built-in
4. **Flexibility**: Supports various application types
5. **Token-Based**: Stateless authentication with JWT tokens
6. **SSO Support**: Seamless single sign-on experience

### How It Works

```
┌─────────────┐                               ┌──────────────────┐
│             │  1. Initiate Sign-In          │                  │
│   User      ├──────────────────────────────►│  Application     │
│             │                               │  (app1)          │
└─────────────┘                               └────────┬─────────┘
      │                                                │
      │  2. Redirect to Entra ID                      │
      │  with authentication request                  │
      ▼                                                │
┌─────────────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────┐
│  Microsoft Entra ID                      │
│  (login.microsoftonline.com)             │
└────────┬─────────────────────────────────┘
         │  3. User authenticates
         │  (username/password + MFA)
         │
         ▼
┌──────────────────────────────────────────┐
│  Authentication Success                  │
│  - Issues authorization code             │
│  - Redirects back to app                 │
└────────┬─────────────────────────────────┘
         │
         │  4. Return authorization code
         ▼
┌──────────────────────────────────────────┐
│  Application (app1)                      │
│  - Exchanges code for tokens             │
│  - Receives ID token and access token    │
└────────┬─────────────────────────────────┘
         │
         │  5. Validate ID token
         │  Extract user information
         │  Establish session
         ▼
┌──────────────────────────────────────────┐
│  User is authenticated and authorized    │
└──────────────────────────────────────────┘
```

### Token Types

#### ID Token (OpenID Connect)
- **Purpose**: Contains user identity information
- **Format**: JWT (JSON Web Token)
- **Contains**: User claims (name, email, tenant, etc.)
- **Use Case**: Authentication and user profile information

```json
{
  "aud": "your-client-id",
  "iss": "https://login.microsoftonline.com/tenant-id/v2.0",
  "iat": 1638360000,
  "exp": 1638363600,
  "name": "John Doe",
  "preferred_username": "john.doe@company.com",
  "oid": "user-object-id",
  "tid": "tenant-id",
  "sub": "subject-identifier"
}
```

#### Access Token (OAuth 2.0)
- **Purpose**: Grants access to protected resources
- **Format**: JWT or opaque string
- **Contains**: Scopes and permissions
- **Use Case**: Calling APIs (Microsoft Graph, custom APIs)

### Implementation Examples

#### Scenario 1: ASP.NET Core Web Application

**1. Install Required Packages**

```bash
dotnet add package Microsoft.Identity.Web
dotnet add package Microsoft.Identity.Web.UI
```

**2. Configure in Program.cs**

```csharp
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.Identity.Web;
using Microsoft.Identity.Web.UI;

var builder = WebApplication.CreateBuilder(args);

// Add authentication with Microsoft Entra ID
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

// Add authorization
builder.Services.AddAuthorization(options =>
{
    options.FallbackPolicy = options.DefaultPolicy;
});

// Add Razor Pages and MVC controllers
builder.Services.AddRazorPages()
    .AddMicrosoftIdentityUI();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

// Enable authentication and authorization middleware
app.UseAuthentication();
app.UseAuthorization();

app.MapRazorPages();
app.MapControllers();

app.Run();
```

**3. Configure appsettings.json**

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "ClientSecret": "your-client-secret",
    "CallbackPath": "/signin-oidc",
    "SignedOutCallbackPath": "/signout-callback-oidc"
  }
}
```

**4. Protect Controllers/Pages**

```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

[Authorize]
public class SecureController : Controller
{
    public IActionResult Index()
    {
        // User is authenticated
        var userName = User.Identity.Name;
        var userEmail = User.Claims.FirstOrDefault(c => c.Type == "preferred_username")?.Value;
        
        return View();
    }
}
```

#### Scenario 2: Node.js/Express Application

**1. Install Dependencies**

```bash
npm install @azure/msal-node express express-session
```

**2. Configure MSAL**

```javascript
const express = require('express');
const session = require('express-session');
const msal = require('@azure/msal-node');

const app = express();

// Configure session
app.use(session({
    secret: 'your-session-secret',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true, // Use in production with HTTPS
        httpOnly: true,
        maxAge: 3600000 // 1 hour
    }
}));

// MSAL configuration
const msalConfig = {
    auth: {
        clientId: 'your-client-id',
        authority: 'https://login.microsoftonline.com/your-tenant-id',
        clientSecret: 'your-client-secret'
    },
    system: {
        loggerOptions: {
            loggerCallback(loglevel, message, containsPii) {
                console.log(message);
            },
            piiLoggingEnabled: false,
            logLevel: msal.LogLevel.Info,
        }
    }
};

const confidentialClientApp = new msal.ConfidentialClientApplication(msalConfig);

// Redirect URIs
const redirectUri = 'https://your-app.azurewebsites.net/auth/callback';
const postLogoutRedirectUri = 'https://your-app.azurewebsites.net';

// Login route
app.get('/login', (req, res) => {
    const authCodeUrlParameters = {
        scopes: ['user.read'],
        redirectUri: redirectUri,
    };

    confidentialClientApp.getAuthCodeUrl(authCodeUrlParameters)
        .then((response) => {
            res.redirect(response);
        })
        .catch((error) => {
            console.log(JSON.stringify(error));
            res.status(500).send(error);
        });
});

// Callback route
app.get('/auth/callback', (req, res) => {
    const tokenRequest = {
        code: req.query.code,
        scopes: ['user.read'],
        redirectUri: redirectUri,
    };

    confidentialClientApp.acquireTokenByCode(tokenRequest)
        .then((response) => {
            req.session.user = {
                account: response.account,
                accessToken: response.accessToken
            };
            res.redirect('/profile');
        })
        .catch((error) => {
            console.log(error);
            res.status(500).send(error);
        });
});

// Protected route
app.get('/profile', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/login');
    }
    
    res.send(`Hello ${req.session.user.account.name}!`);
});

// Logout route
app.get('/logout', (req, res) => {
    req.session.destroy(() => {
        const logoutUri = `https://login.microsoftonline.com/your-tenant-id/oauth2/v2.0/logout?post_logout_redirect_uri=${postLogoutRedirectUri}`;
        res.redirect(logoutUri);
    });
});

app.listen(3000, () => {
    console.log('Server is running on http://localhost:3000');
});
```

#### Scenario 3: React Single-Page Application (SPA)

**1. Install MSAL React**

```bash
npm install @azure/msal-browser @azure/msal-react
```

**2. Configure MSAL in index.js**

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import { PublicClientApplication } from '@azure/msal-browser';
import { MsalProvider } from '@azure/msal-react';
import App from './App';

const msalConfig = {
    auth: {
        clientId: 'your-client-id',
        authority: 'https://login.microsoftonline.com/your-tenant-id',
        redirectUri: window.location.origin,
        postLogoutRedirectUri: window.location.origin
    },
    cache: {
        cacheLocation: 'sessionStorage',
        storeAuthStateInCookie: false
    }
};

const msalInstance = new PublicClientApplication(msalConfig);

ReactDOM.render(
    <React.StrictMode>
        <MsalProvider instance={msalInstance}>
            <App />
        </MsalProvider>
    </React.StrictMode>,
    document.getElementById('root')
);
```

**3. Implement Authentication in App.js**

```javascript
import React from 'react';
import { AuthenticatedTemplate, UnauthenticatedTemplate, useMsal } from '@azure/msal-react';

function App() {
    const { instance, accounts } = useMsal();

    const handleLogin = () => {
        instance.loginPopup({
            scopes: ['user.read']
        }).catch(error => {
            console.error(error);
        });
    };

    const handleLogout = () => {
        instance.logoutPopup().catch(error => {
            console.error(error);
        });
    };

    return (
        <div className="App">
            <AuthenticatedTemplate>
                <h1>Welcome, {accounts[0]?.name}!</h1>
                <button onClick={handleLogout}>Sign Out</button>
            </AuthenticatedTemplate>

            <UnauthenticatedTemplate>
                <h1>Please sign in</h1>
                <button onClick={handleLogin}>Sign In</button>
            </UnauthenticatedTemplate>
        </div>
    );
}

export default App;
```

**4. Protected API Calls**

```javascript
import React, { useEffect, useState } from 'react';
import { useMsal } from '@azure/msal-react';

function UserProfile() {
    const { instance, accounts } = useMsal();
    const [userData, setUserData] = useState(null);

    useEffect(() => {
        const request = {
            scopes: ['user.read'],
            account: accounts[0]
        };

        instance.acquireTokenSilent(request)
            .then(response => {
                // Call Microsoft Graph API
                fetch('https://graph.microsoft.com/v1.0/me', {
                    headers: {
                        Authorization: `Bearer ${response.accessToken}`
                    }
                })
                .then(res => res.json())
                .then(data => setUserData(data))
                .catch(error => console.error(error));
            })
            .catch(error => {
                // Fallback to interactive login
                instance.acquireTokenPopup(request)
                    .then(response => {
                        // Retry the API call
                    });
            });
    }, [instance, accounts]);

    return (
        <div>
            {userData && (
                <div>
                    <h2>User Profile</h2>
                    <p>Name: {userData.displayName}</p>
                    <p>Email: {userData.mail || userData.userPrincipalName}</p>
                    <p>Job Title: {userData.jobTitle}</p>
                </div>
            )}
        </div>
    );
}

export default UserProfile;
```

### Required Azure Configuration

**1. Register Application in Azure Portal**

```plaintext
1. Navigate to: Azure Portal → Microsoft Entra ID → App registrations
2. Click "New registration"
3. Enter application name (e.g., "MyWebApp")
4. Select supported account types:
   - Single tenant: Accounts in this organizational directory only
   - Multi-tenant: Accounts in any organizational directory
   - Personal Microsoft accounts: Include consumer accounts
5. Set Redirect URI:
   - Web app: https://your-app.azurewebsites.net/signin-oidc
   - SPA: https://your-app.azurewebsites.net
6. Register the application
```

**2. Configure Authentication**

```plaintext
Go to: Authentication blade
- Add platform if needed (Web, SPA, Mobile)
- Configure redirect URIs
- Enable ID tokens (for OpenID Connect)
- Configure logout URL
- Set supported account types
```

**3. Generate Client Secret (for confidential clients)**

```plaintext
Go to: Certificates & secrets
- Click "New client secret"
- Add description
- Select expiration period
- Copy the secret value (only shown once!)
```

**4. Configure API Permissions (optional)**

```plaintext
Go to: API permissions
- Add Microsoft Graph delegated permissions:
  - User.Read (basic profile)
  - User.ReadBasic.All (all users' basic info)
  - Mail.Read (if accessing email)
  - etc.
- Grant admin consent if required
```

### Authentication Flows

#### Authorization Code Flow (Recommended for Web Apps)

Most secure flow for server-side web applications:

```
1. User → App: Initiate login
2. App → Entra ID: Redirect with authorization request
3. Entra ID → User: Authentication page
4. User → Entra ID: Credentials + MFA
5. Entra ID → App: Authorization code (via redirect)
6. App → Entra ID: Exchange code for tokens (server-side)
7. Entra ID → App: ID token + access token + refresh token
8. App: Validate tokens and create session
```

#### Authorization Code Flow with PKCE (Proof Key for Code Exchange (pronounced "pixy"))(for SPAs and Mobile Apps)

Enhanced security for public clients:

```
1. App: Generate code_verifier and code_challenge
2. User → App: Initiate login
3. App → Entra ID: Authorization request with code_challenge
4. Entra ID → User: Authentication
5. User → Entra ID: Credentials
6. Entra ID → App: Authorization code
7. App → Entra ID: Exchange code + code_verifier for tokens
8. Entra ID: Verify code_challenge matches code_verifier
9. Entra ID → App: Tokens (no refresh token by default)
```

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Authorization Code Flow with PKCE                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐                                              ┌─────────────────┐
│   SPA /     │  1. Generate PKCE parameters                 │   Microsoft     │
│   Mobile    │     code_verifier = random(43-128 chars)     │   Entra ID      │
│   App       │     code_challenge = BASE64URL(SHA256(       │                 │
│             │                      code_verifier))         │                 │
└──────┬──────┘                                              └────────┬────────┘
       │                                                              │
       │  2. Authorization Request                                    │
       │  GET /authorize?                                             │
       │    response_type=code                                        │
       │    &client_id={client_id}                                    │
       │    &redirect_uri={redirect_uri}                              │
       │    &scope=openid profile                                     │
       │    &code_challenge={code_challenge}                          │
       │    &code_challenge_method=S256                               │
       │    &state={state}                                            │
       ├─────────────────────────────────────────────────────────────►│
       │                                                              │
       │                                                              │
       │  3. User authenticates (credentials + MFA if enabled)        │
       │                                                              │
       │                    ┌────────────────────────┐                │
       │                    │  Entra ID Login Page   │                │
       │                    │  - Enter credentials   │                │
       │                    │  - Complete MFA        │                │
       │                    │  - Consent (if needed) │                │
       │                    └────────────────────────┘                │
       │                                                              │
       │  4. Authorization Code returned via redirect                 │
       │  GET {redirect_uri}?code={authorization_code}&state={state}  │
       │◄─────────────────────────────────────────────────────────────┤
       │                                                              │
       │  5. Exchange code for tokens                                 │
       │  POST /token                                                 │
       │    grant_type=authorization_code                             │
       │    &code={authorization_code}                                │
       │    &redirect_uri={redirect_uri}                              │
       │    &client_id={client_id}                                    │
       │    &code_verifier={code_verifier}  ◄── PKCE verification    │
       ├─────────────────────────────────────────────────────────────►│
       │                                                              │
       │                         ┌─────────────────────────────────┐  │
       │                         │  Entra ID verifies:             │  │
       │                         │  SHA256(code_verifier) ==       │  │
       │                         │  code_challenge                 │  │
       │                         │                                 │  │
       │                         │  ✅ Match: Issue tokens         │  │
       │                         │  ❌ No match: Reject request    │  │
       │                         └─────────────────────────────────┘  │
       │                                                              │
       │  6. Tokens returned                                          │
       │  {                                                           │
       │    "access_token": "eyJ...",                                 │
       │    "id_token": "eyJ...",                                     │
       │    "token_type": "Bearer",                                   │
       │    "expires_in": 3600                                        │
       │  }                                                           │
       │◄─────────────────────────────────────────────────────────────┤
       │                                                              │
┌──────┴──────┐                                              ┌────────┴────────┐
│   App       │  7. Use access token to call APIs            │   Protected     │
│   (Tokens   │     Authorization: Bearer {access_token}     │   API           │
│   stored)   ├─────────────────────────────────────────────►│                 │
└─────────────┘                                              └─────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│  PKCE Security Benefit:                                                       │
│                                                                               │
│  Even if an attacker intercepts the authorization code in step 4,            │
│  they CANNOT exchange it for tokens because they don't have the              │
│  original code_verifier that was generated in step 1 and kept secret         │
│  in the client application's memory.                                          │
│                                                                               │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐         │
│  │  code_verifier  │────►│  SHA256 hash    │────►│ code_challenge  │         │
│  │  (secret)       │     │                 │     │ (sent to server)│         │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘         │
│                                                                               │
│  The hash is one-way: you cannot derive code_verifier from code_challenge    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Why PKCE is Required for SPAs:**
- **Public clients cannot store secrets**: SPAs run entirely in the browser where code is visible and cannot securely store client secrets
- **PKCE provides protection**: The code_verifier/code_challenge mechanism ensures that even if the authorization code is intercepted, it cannot be exchanged for tokens without the original code_verifier
- **MSAL.js supports PKCE**: The Microsoft Authentication Library for JavaScript automatically implements PKCE
- **Modern security standard**: PKCE is now the recommended approach for all public clients (SPAs, mobile apps, desktop apps)

#### Implicit Flow (Legacy - Not Recommended)

⚠️ **Deprecated**: Use Authorization Code Flow with PKCE instead

```
Tokens returned directly in URL fragment (less secure)
No refresh tokens
Susceptible to token leakage
```

**Why Implicit Flow is Deprecated for SPAs:**
- **Token exposure in URL**: Access tokens are returned in the URL fragment, making them visible in browser history and potentially logged by servers
- **No refresh tokens**: Users must re-authenticate when tokens expire
- **Security vulnerabilities**: Susceptible to token leakage and replay attacks
- **Modern SPAs should use PKCE**: Authorization code flow with PKCE provides equivalent functionality with better security

#### Client Credentials Flow

Used for server-to-server authentication without user involvement:

```
1. App → Entra ID: Request token with client credentials
2. Entra ID → App: Access token
```

**⚠️ Not Suitable for SPAs:**
- Requires a client secret that must be stored securely
- SPAs cannot safely store client secrets as they run entirely in the browser
- Designed for confidential clients (backend services, daemons) only

#### Resource Owner Password Credentials (ROPC) Flow

⚠️ **Not Recommended**: Application directly handles user credentials

**Why ROPC Should Be Avoided:**
- Application asks users for their password directly, which is a security anti-pattern
- Bypasses modern authentication features like MFA and Conditional Access
- Users cannot use passwordless authentication methods
- Only use as a last resort for legacy application migration

#### OAuth 2.0 Flow Selection Guide for SPAs

| Flow | Recommended for SPAs? | Reason |
|------|----------------------|--------|
| **Authorization Code with PKCE** | ✅ Yes | Provides security for public clients that cannot store secrets |
| **Implicit Grant** | ❌ No (Deprecated) | Tokens exposed in URL, security vulnerabilities |
| **Client Credentials** | ❌ No | Requires client secret that SPAs cannot securely store |
| **Resource Owner Password** | ❌ No | Not secure, bypasses MFA and modern auth features |

#### Exam Question: SPA Authentication Flow

**Question**: You are developing a single-page application (SPA) that needs to authenticate users and call a protected web API. The application uses the Microsoft Authentication Library (MSAL) for JavaScript. Which OAuth 2.0 flow should you use?

- ✅ **Authorization code flow with PKCE** - Single-page applications require Proof Key for Code Exchange (PKCE) when using the authorization code grant flow, and PKCE is supported by MSAL. This flow provides the security needed for public clients that cannot securely store client secrets.
- ❌ **Resource owner password credentials flow** - This flow is not recommended because your application asking a user for their password is not secure, and it bypasses modern authentication features like MFA.
- ❌ **Implicit grant flow** - The implicit grant flow is deprecated for SPAs due to security concerns with tokens being exposed in the URL. Modern SPAs should use the authorization code flow with PKCE instead.
- ❌ **Client credentials flow** - The client credentials flow requires a client secret that you add to the app registration, which SPAs cannot securely store as they run entirely in the browser.

### MSAL Client Application Types

When implementing authentication using the Microsoft Authentication Library (MSAL), it's important to understand the distinction between different types of client applications based on their ability to securely store credentials.

#### Confidential Client Application ✅

**Can securely authenticate with the authorization server using stored credentials**

Confidential client applications run on servers where they can securely store authentication credentials. They can prove their identity to the authorization server using:

- **Managed Identities**: Azure-managed credentials with automatic rotation
- **Client ID and Secret pairs**: Application credentials stored securely
- **Certificates**: X.509 certificates for authentication

**Characteristics:**
- Run on secure servers (web apps, APIs, background services)
- Can safely store application secrets
- Have a dedicated backend component
- Use server-to-server authentication

**Examples:**
- ASP.NET Core Web Applications
- Node.js Express servers
- Azure Functions
- Background daemon services
- Web APIs

**Code Example:**
```csharp
var app = ConfidentialClientApplicationBuilder
    .Create("your-client-id")
    .WithClientSecret("your-client-secret")
    .WithAuthority(new Uri("https://login.microsoftonline.com/your-tenant-id"))
    .Build();
```

#### Public Client Application ❌

**Cannot securely store credentials**

Public client applications run on devices and can't be trusted to safely keep application secrets. They can only access web APIs on behalf of the user using interactive authentication flows.

**Characteristics:**
- Run on user devices or in browsers
- Cannot safely store application secrets
- Rely on user authentication
- Use PKCE for enhanced security

**Types of Public Clients:**

| Type | Description | Example |
|------|-------------|---------|
| **Browser-based applications** | Run entirely in the browser using JavaScript | React SPA, Angular app |
| **Native client applications** | Installed on user devices | iOS app, Android app, Desktop app |
| **Mobile applications** | Run on mobile devices | Xamarin, React Native |

**Code Example (SPA):**
```javascript
const msalInstance = new PublicClientApplication({
    auth: {
        clientId: 'your-client-id',
        authority: 'https://login.microsoftonline.com/your-tenant-id',
        redirectUri: window.location.origin
    }
});
```

#### Comparison Table

| Feature | Confidential Client | Public Client |
|---------|---------------------|---------------|
| **Can store secrets** | ✅ Yes | ❌ No |
| **Runs on** | Servers | User devices/browsers |
| **Authentication methods** | Managed identity, client secret, certificate | User credentials only |
| **Example** | Web API, daemon service | Mobile app, SPA |
| **Recommended flow** | Authorization Code, Client Credentials | Authorization Code with PKCE |

#### Exam Question

**Question**: Which type of client application can securely authenticate with the authorization server using stored credentials?

- ❌ **Browser-based client application** - Public clients running entirely in the browser cannot securely store credentials or secrets
- ❌ **Public client application** - Run on devices and can't be trusted to safely keep application secrets; they can only access web APIs on behalf of the user
- ✅ **Confidential client application** - Can prove their identity using managed identities, client ID and secret pairs, or certificates; they run on servers and can securely store authentication credentials
- ❌ **Native client application** - A subset of public client applications that run on devices and cannot securely store credentials

---

## Microsoft Entra External ID (formerly Azure AD B2C)

### Overview

**Microsoft Entra External ID** (formerly Azure AD B2C) is a customer identity and access management (CIAM) solution for consumer-facing applications.

### When to Use External ID

Use External ID when you need:

- **Consumer Authentication**: Sign up/sign in for customers (not employees)
- **Social Identity Providers**: Facebook, Google, Twitter, etc.
- **Custom User Experiences**: Branded sign-up/sign-in pages
- **Local Accounts**: Email/password or username/password
- **Custom Attributes**: Additional user profile fields
- **Self-Service**: Password reset, profile editing
- **Advanced Policies**: Multi-factor authentication, conditional access

### ⚠️ When NOT to Use External ID

**Do NOT use External ID for:**
- ❌ Internal employee authentication (use standard Entra ID)
- ❌ Simple enterprise applications (OpenID Connect/OAuth 2.0 is simpler)
- ❌ When you don't need social logins or custom branding
- ❌ When standard Entra ID already meets your needs

### External ID vs Standard Entra ID

| Feature | Standard Entra ID | External ID (B2C) |
|---------|------------------|-------------------|
| **Target Audience** | Employees, partners | Consumers, customers |
| **Identity Providers** | Work/school accounts | Social + local accounts |
| **Custom Branding** | Limited | Fully customizable |
| **Custom Policies** | Built-in policies | Custom XML policies |
| **Pricing** | Per user/month | Per authentication |
| **Complexity** | Simple | More complex |
| **Use Case** | Enterprise apps | Consumer apps |

### External ID Architecture

```
┌─────────────────┐
│   Consumer      │
│   Application   │
└────────┬────────┘
         │
         │ 1. Redirect to External ID
         ▼
┌──────────────────────────────────────┐
│  Microsoft Entra External ID Tenant  │
│  (your-tenant.b2clogin.com)          │
├──────────────────────────────────────┤
│  User Flow / Custom Policy           │
│  ┌────────────────────────────────┐  │
│  │  Sign-up/Sign-in Options:      │  │
│  │  - Local account (email/pass)  │  │
│  │  - Facebook                    │  │
│  │  - Google                      │  │
│  │  - Microsoft Account           │  │
│  │  - Twitter                     │  │
│  └────────────────────────────────┘  │
└────────┬─────────────────────────────┘
         │
         │ 2. User authenticates
         │ 3. Return tokens
         ▼
┌─────────────────┐
│   Application   │
│   (Validated    │
│    tokens)      │
└─────────────────┘
```

### Implementation Example

**1. Create External ID Tenant**

```plaintext
1. Azure Portal → Create a resource
2. Search "Azure AD B2C"
3. Create tenant or link existing
4. Configure custom domain (optional)
```

**2. Register Application**

```plaintext
1. External ID tenant → App registrations
2. New registration
3. Set redirect URIs
4. Generate client secret
```

**3. Create User Flow**

```plaintext
1. User flows → New user flow
2. Select flow type:
   - Sign up and sign in
   - Profile editing
   - Password reset
3. Choose identity providers:
   - Local account
   - Social providers (Facebook, Google, etc.)
4. Configure user attributes and claims
5. Customize page layout (optional)
```

**4. Configure ASP.NET Core App**

```csharp
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(options =>
    {
        options.Instance = "https://your-tenant.b2clogin.com/";
        options.Domain = "your-tenant.onmicrosoft.com";
        options.ClientId = "your-client-id";
        options.CallbackPath = "/signin-oidc";
        options.SignedOutCallbackPath = "/signout-callback-oidc";
        
        // User flow name
        options.SignUpSignInPolicyId = "B2C_1_signupsignin1";
        options.ResetPasswordPolicyId = "B2C_1_passwordreset";
        options.EditProfilePolicyId = "B2C_1_profileediting";
    });
```

### Custom Policies (Advanced)

For advanced scenarios, External ID supports **custom policies** using XML:

**Use Cases:**
- Complex user journeys
- Integration with legacy systems
- Custom claims transformations
- Advanced MFA scenarios
- API-based attribute validation

**Example: Custom Policy Structure**

```xml
<TrustFrameworkPolicy xmlns="http://schemas.microsoft.com/online/cpim/schemas/2013/06/trustframeworkpolicy">
  <BasePolicy>
    <TenantId>your-tenant.onmicrosoft.com</TenantId>
    <PolicyId>B2C_1A_TrustFrameworkBase</PolicyId>
  </BasePolicy>
  
  <BuildingBlocks>
    <ClaimsSchema>
      <ClaimType Id="email">
        <DisplayName>Email Address</DisplayName>
        <DataType>string</DataType>
      </ClaimType>
    </ClaimsSchema>
  </BuildingBlocks>
  
  <ClaimsProviders>
    <!-- Identity providers -->
  </ClaimsProviders>
  
  <UserJourneys>
    <!-- Custom user journey -->
  </UserJourneys>
</TrustFrameworkPolicy>
```

### When to Use Custom Policies

✅ **Use custom policies when:**
- User flows are insufficient for your requirements
- Need complex conditional logic in authentication flow
- Integrating with external identity verification services
- Implementing custom MFA solutions
- Need fine-grained control over every step

❌ **Avoid custom policies when:**
- User flows meet your needs (simpler and easier to maintain)
- You're new to External ID (start with user flows)
- Team lacks expertise in XML and identity protocols

---

## Microsoft Graph API Integration

### Overview

The **Microsoft Graph API** is NOT an authentication method but rather an API for accessing Microsoft 365 data after authentication.

### ⚠️ Common Misconception

**Incorrect**: "Use Microsoft Graph API for authentication"

**Correct**: 
1. Authenticate user with Entra ID (OpenID Connect/OAuth 2.0)
2. Obtain access token with appropriate scopes
3. Use access token to call Microsoft Graph API

### Why NOT Use Graph API for Authentication

❌ **Microsoft Graph API directly validates user credentials at runtime**
- This is NOT a valid authentication approach
- Graph API is for accessing resources, not authenticating users
- Credentials should never be validated directly in application code
- Violates security best practices

### Correct Usage Pattern

```
┌──────────────────────────────────────────────────┐
│  Step 1: Authentication                          │
│  ┌────────────┐         ┌──────────────────┐    │
│  │   User     │────────►│  Microsoft       │    │
│  │            │         │  Entra ID        │    │
│  └────────────┘         │  (Authentication)│    │
│                         └────────┬─────────┘    │
│                                  │              │
│                         Returns: │              │
│                         - ID token              │
│                         - Access token          │
└─────────────────────────────────┼───────────────┘
                                  │
                                  │
┌─────────────────────────────────┼───────────────┐
│  Step 2: Access Microsoft Graph API             │
│                                  │              │
│  ┌────────────┐         ┌───────▼──────────┐   │
│  │ Application│────────►│  Microsoft Graph │   │
│  │            │  Bearer │  API              │   │
│  │            │  Token  │                   │   │
│  └────────────┘         └──────────────────┘   │
│                                                 │
│  Access user data, emails, files, etc.         │
└─────────────────────────────────────────────────┘
```

### Proper Implementation

```csharp
// ✅ CORRECT: Authenticate first, then use Graph API
using Microsoft.Identity.Web;
using Microsoft.Graph;

// 1. User authenticates with Entra ID (handled by middleware)
// ID token issued and validated

// 2. Obtain access token for Microsoft Graph
[Authorize]
public class ProfileController : Controller
{
    private readonly GraphServiceClient _graphClient;

    public ProfileController(GraphServiceClient graphClient)
    {
        _graphClient = graphClient;
    }

    public async Task<IActionResult> Index()
    {
        // 3. Call Microsoft Graph with authenticated user's token
        var user = await _graphClient.Me.GetAsync();
        
        return View(user);
    }
}
```

### When to Use Microsoft Graph API

Use Microsoft Graph API **after authentication** to:

- ✅ Read user profile information
- ✅ Access user's emails (Outlook)
- ✅ Get calendar events
- ✅ Read/write files (OneDrive, SharePoint)
- ✅ Access Teams data
- ✅ Manage organizational data (with appropriate permissions)

### Required Permissions

Configure delegated permissions for Microsoft Graph:

```plaintext
Azure Portal → App registrations → API permissions
→ Add a permission → Microsoft Graph → Delegated permissions

Common permissions:
- User.Read: Read signed-in user's profile
- User.ReadBasic.All: Read all users' basic profiles
- Mail.Read: Read user's email
- Calendars.Read: Read user's calendar
- Files.Read: Read user's files
```

---

## Self-Hosted Identity Providers

### Overview

A **self-hosted OpenID Connect provider** is a custom authentication server that you deploy and manage yourself.

### ⚠️ When NOT to Use Self-Hosted Providers

**Avoid self-hosted identity providers for Microsoft Entra ID integration because:**

❌ **Unnecessary Complexity**
- Microsoft Entra ID already provides authentication
- No need to build and maintain your own provider
- Increases operational overhead

❌ **Duplicates Functionality**
- Entra ID is already an OpenID Connect provider
- Self-hosting doesn't add value for Entra ID scenarios

❌ **Security Risks**
- Harder to maintain security patches
- Requires expertise in identity protocols
- Potential for misconfiguration

❌ **Lost Features**
- Miss out on Entra ID features (MFA, Conditional Access, etc.)
- No integration with Microsoft ecosystem
- More work for less functionality

### When You MIGHT Consider Self-Hosted

There are rare scenarios where self-hosted might be appropriate:

✅ **Valid use cases:**
- Need to authenticate against non-Entra ID systems
- Legacy on-premises identity systems without cloud connectivity
- Specific regulatory requirements preventing cloud authentication
- Acting as an identity broker between multiple identity sources
- Research or learning purposes

### Popular Self-Hosted Options

If you must use a self-hosted provider:

| Provider | Language | Features |
|----------|----------|----------|
| **IdentityServer** | .NET/C# | Full-featured, OIDC/OAuth 2.0 |
| **Keycloak** | Java | Open source, comprehensive |
| **Auth0 (self-hosted)** | Node.js | Commercial option |
| **Ory Hydra** | Go | Cloud-native, lightweight |

### Example: IdentityServer (Illustration Only)

```csharp
// ⚠️ NOT RECOMMENDED for Entra ID scenarios
// This is for illustration only

using IdentityServer4;
using IdentityServer4.Models;

public class Config
{
    public static IEnumerable<Client> Clients =>
        new List<Client>
        {
            new Client
            {
                ClientId = "webapp",
                ClientSecrets = { new Secret("secret".Sha256()) },
                AllowedGrantTypes = GrantTypes.Code,
                RedirectUris = { "https://localhost:5001/signin-oidc" },
                AllowedScopes = { "openid", "profile", "api1" }
            }
        };

    public static IEnumerable<ApiScope> ApiScopes =>
        new List<ApiScope>
        {
            new ApiScope("api1", "My API")
        };

    public static IEnumerable<IdentityResource> IdentityResources =>
        new List<IdentityResource>
        {
            new IdentityResources.OpenId(),
            new IdentityResources.Profile()
        };
}
```

### Recommendation

**For Azure/Microsoft Entra ID integration:**

✅ **DO**: Use Microsoft Entra ID as the identity provider with OpenID Connect/OAuth 2.0

❌ **DON'T**: Implement a self-hosted OpenID Connect provider

---

## Comparison of Authentication Approaches

### Decision Matrix

| Scenario | Recommended Approach | Reason |
|----------|---------------------|--------|
| **Azure App Service web app needing quick auth setup** | ✅ Easy Auth (App Service Authentication) | Zero code, secure, quick setup |
| **Enterprise web app with employee authentication** | ✅ OpenID Connect / OAuth 2.0 with Entra ID | Standard, secure, simple |
| **Consumer-facing app with social logins** | ✅ External ID (B2C) | Designed for consumer scenarios |
| **Multi-tenant SaaS application** | ✅ OpenID Connect / OAuth 2.0 (multi-tenant) | Native multi-tenant support |
| **Mobile app authentication** | ✅ OAuth 2.0 with PKCE | Secure for public clients |
| **Single-page application (SPA)** | ✅ OAuth 2.0 with PKCE (MSAL.js) | Modern SPA authentication |
| **Server-to-server (no user)** | ✅ Client Credentials Flow | App-only authentication |
| **Access Microsoft Graph API** | ✅ OAuth 2.0 + delegated permissions | Standard API access pattern |
| **Legacy .NET Framework app** | ✅ WS-Federation or SAML | Backward compatibility |
| **On-premises app with AD** | ✅ ADFS + OpenID Connect | Bridge on-prem to cloud |
| **Custom auth with own user database** | ❌ NOT Recommended | Security risks, complexity |
| **Custom OAuth 2.0 token service** | ❌ NOT Recommended | Unnecessary when Entra ID available |

### Detailed Comparison

#### 0. Azure App Service Authentication (Easy Auth) ✅

**Pros:**
- ✅ Zero authentication code required
- ✅ Quick setup through Azure Portal or CLI
- ✅ Platform-managed security
- ✅ Automatic token management and refresh
- ✅ Supports multiple identity providers
- ✅ Built-in session management
- ✅ Secure by default

**Cons:**
- ❌ Only available for Azure App Service, Functions, Container Apps
- ❌ Limited customization of authentication flow
- ❌ Less control compared to custom implementation

**Best For:**
- Azure App Service hosted applications
- Quick authentication setup
- Existing applications needing auth without code changes
- Prototypes and MVPs

---

#### 1. OpenID Connect / OAuth 2.0 (Recommended) ✅

**Pros:**
- ✅ Industry standard, widely supported
- ✅ Best security practices built-in
- ✅ Extensive Microsoft SDKs and libraries
- ✅ Simple implementation
- ✅ Supports all application types
- ✅ Great documentation and community support
- ✅ Access to full Entra ID feature set

**Cons:**
- ❌ Requires understanding of OAuth/OIDC concepts
- ❌ Token management overhead
- ❌ Redirect-based flows (not suitable for APIs)

**Best For:**
- Web applications (server-side)
- Single-page applications (SPAs)
- Mobile applications
- Desktop applications

---

#### 2. Microsoft Entra External ID (Azure AD B2C) ⚠️

**Pros:**
- ✅ Excellent for consumer scenarios
- ✅ Social identity providers out-of-box
- ✅ Customizable user experience
- ✅ Self-service capabilities
- ✅ Scalable for millions of users

**Cons:**
- ❌ More complex than standard Entra ID
- ❌ Custom policies require expertise
- ❌ Additional cost per authentication
- ❌ Overkill for simple enterprise apps

**Best For:**
- Consumer-facing applications
- Apps requiring social logins
- Custom branding requirements
- Self-service user management

**Avoid For:**
- Internal enterprise applications
- Simple employee authentication
- When standard Entra ID suffices

---

#### 3. Microsoft Graph API ❌ (Not an Authentication Method)

**Pros:**
- ✅ Rich API for Microsoft 365 data
- ✅ Unified API surface
- ✅ Well-documented

**Cons:**
- ❌ NOT for authentication
- ❌ Requires prior authentication
- ❌ Misuse leads to security issues

**Use After Authentication:**
- Access user profile
- Read/send emails
- Access calendar, files, Teams data

**Never Use For:**
- ❌ Direct credential validation
- ❌ User authentication
- ❌ Session management

---

#### 4. Self-Hosted OpenID Connect Provider ❌

**Pros:**
- ✅ Full control over authentication logic
- ✅ Can integrate multiple identity sources
- ✅ Useful for learning

**Cons:**
- ❌ Unnecessary for Entra ID scenarios
- ❌ Complex to implement and maintain
- ❌ Security responsibility on you
- ❌ Miss out on Entra ID features
- ❌ No Microsoft ecosystem integration

**Rarely Appropriate For:**
- Custom identity brokering
- Legacy system integration
- Specific regulatory requirements

**Avoid For:**
- ❌ Standard Azure applications
- ❌ When Entra ID is available
- ❌ Simple authentication needs

---

## Implementation Scenarios

### Scenario 1: Enterprise Web Application

**Requirements:**
- Authenticate employees with work accounts
- Single sign-on (SSO)
- Access Microsoft 365 data

**Solution: OpenID Connect with Microsoft Entra ID**

```plaintext
Architecture:
┌─────────────┐
│  Employee   │
└──────┬──────┘
       │ 1. Access app
       ▼
┌───────────────────┐
│  Azure App Service│
│  Web App          │
└──────┬────────────┘
       │ 2. Redirect to Entra ID
       ▼
┌───────────────────┐
│  Microsoft        │
│  Entra ID         │
│  (SSO enabled)    │
└──────┬────────────┘
       │ 3. Authenticate + MFA
       │ 4. Return tokens
       ▼
┌───────────────────┐
│  Web App          │
│  (Authenticated)  │
│  - Access Graph   │
│  - Business logic │
└───────────────────┘
```

**Implementation:**
- Use Microsoft.Identity.Web for .NET
- Configure OpenID Connect middleware
- Add delegated permissions for Microsoft Graph
- Enable MFA and Conditional Access in Entra ID

---

### Scenario 2: Consumer Mobile Application

**Requirements:**
- Sign up/sign in with email or social accounts
- Custom branded experience
- Millions of users

**Solution: Microsoft Entra External ID (B2C)**

```plaintext
Architecture:
┌─────────────┐
│  Consumer   │
│  Mobile App │
└──────┬──────┘
       │ 1. Sign up/Sign in
       ▼
┌────────────────────────┐
│  External ID Tenant    │
│  User Flow             │
│  ┌──────────────────┐  │
│  │ Choose:          │  │
│  │ - Email/Password │  │
│  │ - Facebook       │  │
│  │ - Google         │  │
│  └──────────────────┘  │
└──────┬─────────────────┘
       │ 2. Authenticate
       │ 3. Return tokens
       ▼
┌─────────────┐
│  Mobile App │
│  (Tokens    │
│   stored)   │
└──────┬──────┘
       │ 4. Call backend API
       ▼
┌─────────────┐
│  Backend    │
│  API        │
└─────────────┘
```

**Implementation:**
- Create External ID tenant
- Configure user flows
- Add social identity providers
- Use MSAL library for mobile (iOS/Android)
- Implement OAuth 2.0 with PKCE

---

### Scenario 3: Multi-Tenant SaaS Application

**Requirements:**
- Support multiple organizations
- Each organization uses their own Entra ID
- Centralized application management

**Solution: Multi-Tenant OpenID Connect**

```plaintext
Architecture:
┌──────────────────────────────────────┐
│  Tenant A (Company A)                │
│  ┌────────────┐    ┌──────────────┐  │
│  │  Employee  │───►│  Entra ID A  │  │
│  └────────────┘    └──────┬───────┘  │
└───────────────────────────┼──────────┘
                            │
                            │ Authenticate
                            ▼
                  ┌──────────────────┐
                  │  SaaS            │
                  │  Application     │
                  │  (Multi-tenant)  │
                  └──────────────────┘
                            ▲
                            │ Authenticate
┌───────────────────────────┼──────────┐
│  Tenant B (Company B)     │          │
│  ┌────────────┐    ┌──────┴───────┐  │
│  │  Employee  │───►│  Entra ID B  │  │
│  └────────────┘    └──────────────┘  │
└──────────────────────────────────────┘
```

**Implementation:**
- Register as multi-tenant application
- Use `/common` or `/organizations` endpoint
- Implement tenant resolution logic
- Store tenant-specific data separately
- Handle admin consent per tenant

**Code Example:**

```csharp
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(options =>
    {
        options.Instance = "https://login.microsoftonline.com/";
        options.TenantId = "common"; // Multi-tenant
        options.ClientId = "your-client-id";
        options.ClientSecret = "your-client-secret";
        
        // Handle tenant resolution
        options.Events = new OpenIdConnectEvents
        {
            OnTokenValidated = async context =>
            {
                var tenantId = context.Principal.FindFirst("tid")?.Value;
                // Resolve and store tenant context
            }
        };
    });
```

---

### Scenario 4: Single-Page Application (React)

**Requirements:**
- Modern React SPA
- User authentication
- Call protected backend API

**Solution: OAuth 2.0 with PKCE using MSAL React**

```plaintext
Architecture:
┌─────────────────┐
│  React SPA      │
│  (Browser)      │
└────┬────────────┘
     │ 1. Login
     ▼
┌────────────────────┐
│  Microsoft         │
│  Entra ID          │
│  (login popup)     │
└────┬───────────────┘
     │ 2. Tokens (PKCE)
     ▼
┌─────────────────┐
│  React SPA      │
│  - Access token │
│  - ID token     │
└────┬────────────┘
     │ 3. API calls with Bearer token
     ▼
┌─────────────────┐
│  Backend API    │
│  (Validates     │
│   token)        │
└─────────────────┘
```

**Implementation:**
- Use @azure/msal-react and @azure/msal-browser
- Configure PublicClientApplication
- Implement login/logout buttons
- Acquire tokens for API calls
- Handle token refresh automatically

---

### Scenario 5: Background Service / Daemon

**Requirements:**
- Server-to-server authentication
- No user interaction
- Access Microsoft Graph or custom APIs

**Solution: Client Credentials Flow**

```plaintext
Architecture:
┌──────────────────┐
│  Background      │
│  Service/Daemon  │
└────┬─────────────┘
     │ 1. Request token (client_credentials)
     │    with client_id + client_secret
     ▼
┌────────────────────┐
│  Microsoft         │
│  Entra ID          │
└────┬───────────────┘
     │ 2. App-only access token
     ▼
┌──────────────────┐
│  Background      │
│  Service         │
└────┬─────────────┘
     │ 3. Call APIs with app-only token
     ▼
┌──────────────────────┐
│  Microsoft Graph API │
│  or Custom API       │
└──────────────────────┘
```

**Implementation:**

```csharp
using Microsoft.Identity.Client;

var app = ConfidentialClientApplicationBuilder
    .Create("your-client-id")
    .WithClientSecret("your-client-secret")
    .WithAuthority(new Uri("https://login.microsoftonline.com/your-tenant-id"))
    .Build();

var result = await app.AcquireTokenForClient(
    new[] { "https://graph.microsoft.com/.default" })
    .ExecuteAsync();

var accessToken = result.AccessToken;

// Use token to call Microsoft Graph
var graphClient = new GraphServiceClient(
    new DelegateAuthenticationProvider(requestMessage =>
    {
        requestMessage.Headers.Authorization = 
            new AuthenticationHeaderValue("Bearer", accessToken);
        return Task.CompletedTask;
    }));

// Access data with app permissions (not user permissions)
var users = await graphClient.Users.GetAsync();
```

**Important:**
- Use **application permissions**, not delegated permissions
- Requires admin consent
- No user context - service acts as itself

#### Exam Question: Authentication Flow for Daemon Apps

**Question**: Your application needs to acquire tokens on behalf of itself without user interaction to access Microsoft Graph API. The application is registered in Microsoft Entra ID. Which authentication flow should you implement?

- ❌ **Integrated Windows Authentication (IWA) flow** - IWA is for desktop and mobile applications that run on domain-joined or Microsoft Entra joined Windows computers, not for service-to-service authentication scenarios.

- ❌ **Authorization code flow** - The authorization code flow requires user interaction to obtain an authorization code, making it unsuitable for applications that need to authenticate without user interaction.

- ✅ **Client credentials flow** - Daemon apps acquire a token for the calling app by using the client credential acquisition methods in MSAL, which require a client secret or certificate that you add to the app registration. This flow is designed for applications authenticating as themselves without user context.

- ❌ **Device code flow** - The device code flow is designed for devices with limited input capabilities and still requires user interaction to complete authentication on another device.

**Key Points:**
- **Client credentials flow** is the only flow that allows an application to authenticate as itself without any user interaction
- Requires application permissions (not delegated permissions) configured in the app registration
- Uses either a client secret or certificate to prove the application's identity
- Common use cases: background services, daemons, scheduled tasks, microservices

---

## Best Practices and Recommendations

### 1. Always Use OpenID Connect / OAuth 2.0 for Entra ID ✅

**Why:**
- Industry standard
- Best security
- Microsoft's recommended approach
- Simple and well-supported

**Implementation:**
```csharp
// ✅ Good practice
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(Configuration.GetSection("AzureAd"));
```

---

### 2. Choose the Right Authentication Flow

| Application Type | Flow |
|-----------------|------|
| **Server-side web app** | Authorization Code Flow |
| **SPA (React, Angular, Vue)** | Authorization Code Flow with PKCE |
| **Mobile app** | Authorization Code Flow with PKCE |
| **Desktop app** | Authorization Code Flow with PKCE or Device Code Flow |
| **Background service** | Client Credentials Flow |
| **Web API called by user** | On-Behalf-Of Flow |

---

### 3. Secure Token Storage

**Web Applications:**
```csharp
// ✅ Store in encrypted session/cookie
// ✅ Use server-side session storage
// ❌ Never expose tokens to client-side JavaScript
```

**Single-Page Applications:**
```javascript
// ✅ Store in memory (MSAL handles this)
// ✅ Use sessionStorage for refresh tokens (with caution)
// ❌ Never store in localStorage (XSS risk)
// ❌ Never store in cookies accessible to JavaScript
```

**Mobile Applications:**
```plaintext
✅ Use secure storage (Keychain on iOS, Keystore on Android)
✅ Enable biometric authentication
❌ Never store in plain text
```

---

### 4. Implement Token Refresh Logic

```csharp
// ✅ Implement token refresh
public async Task<string> GetAccessTokenAsync()
{
    try
    {
        // Try silent token acquisition
        var result = await _app.AcquireTokenSilent(scopes, account)
            .ExecuteAsync();
        return result.AccessToken;
    }
    catch (MsalUiRequiredException)
    {
        // Token expired, need interactive login
        var result = await _app.AcquireTokenInteractive(scopes)
            .ExecuteAsync();
        return result.AccessToken;
    }
}
```

#### MSAL.NET Silent Token Acquisition Best Practices

When working with MSAL.NET, it's crucial to understand when to fall back to interactive authentication. The recommended pattern is:

1. **Always try `AcquireTokenSilent` first** - This attempts to get a token from the cache without user interaction
2. **Fall back to interactive authentication only when `MsalUiRequiredException` is thrown** - This specific exception indicates that user interaction is required

**Why this pattern?**

| Approach | Recommendation | Reason |
|----------|----------------|--------|
| Call `AcquireTokenSilent` first | ✅ **Recommended** | Provides best user experience by avoiding unnecessary login prompts |
| Fall back on `MsalUiRequiredException` | ✅ **Correct** | This exception specifically indicates user interaction is needed |
| Fall back on any exception | ❌ **Incorrect** | Not all exceptions require interactive authentication; only `MsalUiRequiredException` indicates user interaction is needed |
| Fall back after fixed timeout | ❌ **Incorrect** | Ignores actual error conditions; should respond to specific exceptions |
| Use interactive auth as primary | ❌ **Incorrect** | Creates poor user experience with unnecessary login prompts |

#### Exam Question

**Question**: Your application needs to handle scenarios where MSAL.NET cannot acquire tokens silently. According to best practices, when should your application fall back to interactive authentication?

| Option | Correct? | Explanation |
|--------|----------|-------------|
| When any exception occurs during token acquisition | ❌ | Not all exceptions require interactive authentication. Only `MsalUiRequiredException` specifically indicates that user interaction is needed to acquire a token. |
| **When `AcquireTokenSilent` throws `MsalUiRequiredException`** | ✅ | The recommended pattern is to call the `AcquireTokenSilent` method first. If `AcquireTokenSilent` fails, then acquire a token using other methods. If a `MsalUiRequiredException` exception is thrown, the application acquires a token interactively. |
| After a fixed timeout period regardless of the error | ❌ | Falling back based on a timeout ignores the actual error condition. The application should respond to specific exceptions that indicate user interaction is required. |
| Always use interactive authentication as the primary method | ❌ | Your application code should first try to get a token silently from the cache before attempting to acquire a token by other means. Interactive authentication should be a fallback, not the primary method. |

> **Key Takeaway:** Always call `AcquireTokenSilent` first, and only fall back to interactive authentication when `MsalUiRequiredException` is thrown. This provides the best user experience while correctly handling scenarios where user interaction is required.

---

### 5. Use Managed Identities When Possible

For Azure-hosted applications accessing Azure resources:

```csharp
// ✅ Use Managed Identity (no credentials needed)
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;

var client = new SecretClient(
    new Uri("https://your-keyvault.vault.azure.net/"),
    new DefaultAzureCredential()); // Automatically uses Managed Identity

var secret = await client.GetSecretAsync("my-secret");
```

**Benefits:**
- No credentials to manage
- Automatic credential rotation
- Reduced security risk

---

### 6. Implement Proper Error Handling

```csharp
// ✅ Handle authentication errors
try
{
    var result = await _app.AcquireTokenInteractive(scopes).ExecuteAsync();
}
catch (MsalServiceException ex)
{
    // Service error (Entra ID unavailable)
    _logger.LogError(ex, "Authentication service error");
    // Show user-friendly message
}
catch (MsalClientException ex)
{
    // Client error (configuration issue)
    _logger.LogError(ex, "Authentication configuration error");
    // Fix configuration
}
catch (MsalUiRequiredException ex)
{
    // User interaction required
    // Redirect to login
}
```

---

### 7. Enable Logging and Monitoring

```csharp
// ✅ Enable MSAL logging
var app = ConfidentialClientApplicationBuilder.Create(clientId)
    .WithClientSecret(clientSecret)
    .WithLogging((level, message, containsPii) =>
    {
        if (!containsPii)
        {
            _logger.Log(level, message);
        }
    }, LogLevel.Info, enablePiiLogging: false)
    .Build();
```

**Monitor:**
- Failed login attempts
- Token acquisition failures
- Suspicious activity
- Performance metrics

---

### 8. Use Least Privilege Principle

**Permissions:**
```plaintext
✅ Request only necessary permissions
✅ Use delegated permissions when user context exists
✅ Use application permissions only for background services

❌ Don't request admin-level permissions unless required
❌ Don't use application permissions when delegated would work
```

**Example:**
```plaintext
✅ Good: User.Read (read signed-in user)
❌ Bad: User.ReadWrite.All (read/write all users) when you only need the signed-in user
```

---

### 9. Implement Proper Logout

```csharp
// ✅ Proper logout clears session everywhere
public IActionResult Logout()
{
    // Sign out from application
    HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
    
    // Sign out from Entra ID
    var callbackUrl = Url.Action("LoggedOut", "Account", values: null, protocol: Request.Scheme);
    return SignOut(
        new AuthenticationProperties { RedirectUri = callbackUrl },
        OpenIdConnectDefaults.AuthenticationScheme);
}
```

---

### 10. Keep Dependencies Updated

```bash
# Regularly update authentication libraries
dotnet add package Microsoft.Identity.Web --version latest
npm update @azure/msal-browser @azure/msal-react
```

**Why:**
- Security patches
- Bug fixes
- New features
- Performance improvements

---

### 11. Test Authentication Thoroughly

**Test scenarios:**
- ✅ Successful login
- ✅ Failed login (wrong credentials)
- ✅ MFA challenges
- ✅ Token expiration and refresh
- ✅ Logout and session cleanup
- ✅ Concurrent sessions
- ✅ API calls with expired tokens

---

### 12. Document Your Authentication Flow

**Include:**
- Architecture diagram
- Authentication flow sequence
- Required permissions
- Configuration steps
- Troubleshooting guide
- Security considerations

---

## Exam Scenario Analysis

### Exam Question 1: Authentication with OpenID Connect

**Scenario:** You are developing an Azure web application that requires user authentication. You decide to use Microsoft Entra ID for authentication purposes.

**Question:** Which of the following approaches should you use to implement user authentication in your application?

### Answer Analysis

#### ✅ Correct Answer

**Configure the application to use Microsoft Entra ID as an identity provider through OpenID Connect or OAuth 2.0**

**Why this is correct:**
1. **Industry Standard**: OpenID Connect and OAuth 2.0 are proven, widely-adopted protocols
2. **Microsoft Recommended**: This is Microsoft's official recommendation
3. **Secure**: Built-in security best practices
4. **Well-Supported**: Extensive libraries and documentation
5. **Feature-Rich**: Access to all Entra ID capabilities (MFA, Conditional Access, etc.)
6. **Simple**: Straightforward implementation with MSAL libraries
7. **Flexible**: Works for web apps, SPAs, mobile apps

**Implementation summary:**
```csharp
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(Configuration.GetSection("AzureAd"));
```

---

#### ❌ Incorrect: Use Microsoft Entra External ID (Azure AD B2C)

**Why this is NOT recommended for this scenario:**
1. **Wrong Use Case**: External ID is for consumer/customer authentication, not employees
2. **Unnecessary Complexity**: Adds complexity without benefit
3. **Higher Cost**: Pay-per-authentication model
4. **Overkill**: Standard Entra ID is simpler and sufficient
5. **Not Optimized**: Not designed for enterprise employee scenarios

**When to actually use External ID:**
- Consumer-facing applications
- Social login requirements
- Custom branding needs
- Self-service customer identity management

---

#### ❌ Incorrect: Use Microsoft Graph API to validate credentials

**Why this is WRONG:**
1. **Not an Authentication Method**: Graph API is for resource access, not authentication
2. **Security Anti-Pattern**: Never validate credentials directly in code
3. **Violates Best Practices**: Credentials should be handled by identity provider
4. **Missing Features**: No SSO, MFA, Conditional Access
5. **Increased Risk**: Exposing authentication logic to application layer

**Correct use of Graph API:**
- AFTER authentication
- To access user data, emails, files
- With proper delegated/application permissions

---

#### ❌ Incorrect: Implement self-hosted OpenID Connect provider

**Why this is NOT appropriate:**
1. **Reinventing the Wheel**: Entra ID already provides this
2. **Unnecessary Work**: Building what already exists
3. **Maintenance Burden**: Requires ongoing security updates
4. **Missed Features**: Lose Entra ID capabilities
5. **Higher Risk**: Custom implementation more prone to errors
6. **No Integration**: Doesn't integrate with Microsoft ecosystem

**When self-hosted might make sense:**
- Bridging legacy systems (rare)
- Specific regulatory requirements (uncommon)
- Multi-source identity brokering (advanced)

---

### Exam Question 2: App Service Authentication (Easy Auth)

**Scenario:** You are developing a web application that requires user authentication. You want to implement Microsoft Entra ID for user sign-in and management. 

**Question:** Which of the following options is the correct way to configure authentication in your application using Entra ID?

### Answer Options Analysis

#### ❌ Option 1: Implement a custom user database and manage authentication tokens manually

**Why this is WRONG:**
- Implementing a custom user database and managing authentication tokens manually within your application is NOT the ideal approach when utilizing Microsoft Entra ID
- This method introduces security vulnerabilities
- Increases the complexity of managing user authentication
- Loses benefits of Entra ID features (MFA, SSO, Conditional Access)
- Places security responsibility on you instead of Microsoft

---

#### ❌ Option 2: Use Microsoft Entra External ID with MSAL for JavaScript

**Why this is NOT the best choice:**
- Microsoft Entra External ID is designed for **consumer-facing applications**
- May require additional configuration for enterprise scenarios
- More complex than needed for standard enterprise user authentication
- Better suited for apps needing social logins or custom branding
- Different pricing model (pay-per-authentication)

**When External ID IS appropriate:**
- Customer/consumer sign-up and sign-in
- Social identity provider integration (Facebook, Google)
- Self-service user management for external users

---

#### ✅ Option 3: Utilize Azure App Service Authentication (Easy Auth) - CORRECT ANSWER

**Why this is CORRECT:**
1. **Zero Code Required**: Automatically handles user sign-in and authorization without writing any authentication code
2. **Secure by Default**: Microsoft manages security best practices
3. **Convenient**: Simplifies the authentication process significantly
4. **Built-in Features**: 
   - Automatic token management
   - Session handling
   - Token refresh
5. **Multiple Provider Support**: Can use Entra ID, Facebook, Google, Twitter, and more
6. **Platform Managed**: Security updates handled automatically

**Implementation:**
```plaintext
Azure Portal → App Service → Authentication → Add identity provider → Microsoft
```

**No code changes required!** User information is available in request headers:
- `X-MS-CLIENT-PRINCIPAL-NAME`: Username
- `X-MS-CLIENT-PRINCIPAL-ID`: User ID
- `X-MS-TOKEN-AAD-ACCESS-TOKEN`: Access token

---

#### ❌ Option 4: Configure OAuth 2.0 with a custom token service hosted on Azure

**Why this is NOT recommended:**
- Entra ID already has its own OAuth 2.0 authentication mechanisms
- Building a custom token service is unnecessary
- Introduces additional complexity and security risk
- Loses integration with Microsoft ecosystem
- Requires maintaining custom security infrastructure
- Not aligned with Microsoft's recommended practices

---

### Exam Question 3: Group-Based Authorization for Azure Web Apps

**Scenario:** You are developing a website that will run as an Azure Web App. Users will authenticate by using their Microsoft Entra ID credentials. You plan to assign users one of the following permission levels for the website: `admin`, `normal`, and `reader`. A user's Microsoft Entra ID group membership must be used to determine the permission level.

You need to configure authorization.

**Proposed Solution:** Configure and use Integrated Windows Authentication in the website. In the website, query Microsoft Graph API to load the group to which the user is a member.

**Question:** Does the solution meet the goal?

### Answer Analysis

#### ❌ Correct Answer: No

**Why this solution does NOT meet the goal:**

1. **Integrated Windows Authentication (IWA) is NOT appropriate for Azure Web Apps:**
   - IWA is designed for **desktop and mobile applications** running on domain-joined or Microsoft Entra joined Windows computers
   - IWA relies on Kerberos authentication, which requires a domain environment
   - Azure Web Apps are cloud-hosted and don't natively support IWA authentication flows
   - IWA is not the recommended authentication method for web applications hosted in Azure

2. **Querying Microsoft Graph API for group membership is suboptimal:**
   - While technically possible, this approach adds unnecessary complexity
   - Requires additional API calls after authentication
   - Increases latency and potential points of failure
   - Not aligned with Azure AD best practices for role-based authorization

3. **Better Alternatives Exist:**
   - **Azure AD App Roles**: Define application-specific roles (admin, normal, reader) in the app registration
   - **Security Groups with Token Claims**: Configure the app to include group claims in the token
   - **Claims-based authorization**: Process roles/groups directly from the ID token

#### ✅ Recommended Approach: Azure AD App Roles or Security Groups in Token Claims

**Option 1: Azure AD App Roles (Recommended)**

```plaintext
1. Define App Roles in Azure AD App Registration:
   - Navigate to Azure Portal → App registrations → Your app
   - Go to "App roles" → Create app role
   - Create roles: "Admin", "Normal", "Reader"

2. Assign Users/Groups to App Roles:
   - Go to Enterprise Applications → Your app
   - Select "Users and groups" → Add user/group
   - Assign users or groups to the appropriate app role

3. Configure App to Receive Role Claims:
   - The 'roles' claim will automatically be included in the token
```

**Option 2: Security Groups in Token Claims**

```plaintext
1. Configure Token to Include Group Claims:
   - App registrations → Your app → Token configuration
   - Add optional claim → Select "groups"
   - Choose claim type (Security groups, Directory roles, etc.)

2. Map Groups to Permission Levels in Application:
   - Read the 'groups' claim from the token
   - Map group IDs to permission levels in your application logic
```

**Implementation Example (.NET):**
```csharp
// Using App Roles
[Authorize(Roles = "Admin")]
public IActionResult AdminDashboard()
{
    return View();
}

[Authorize(Roles = "Admin,Normal")]
public IActionResult EditContent()
{
    return View();
}

[Authorize(Roles = "Admin,Normal,Reader")]
public IActionResult ViewContent()
{
    return View();
}
```

#### Why Integrated Windows Authentication is Wrong

| Aspect | IWA | Azure AD with OpenID Connect |
|--------|-----|------------------------------|
| **Designed For** | On-premises/domain-joined devices | Cloud applications |
| **Authentication Protocol** | Kerberos | OAuth 2.0 / OpenID Connect |
| **Azure Web App Support** | ❌ Not natively supported | ✅ Fully supported |
| **Group/Role Claims** | Requires additional queries | ✅ Built into token |
| **Cloud-Native** | ❌ No | ✅ Yes |

> **Exam Tip:** When asked about implementing group-based authorization for Azure Web Apps with Microsoft Entra ID, the answer is to use **Azure AD App Roles** or configure **group claims in tokens**. Integrated Windows Authentication is NOT appropriate for cloud-hosted web applications.

---

### Exam Question 4: Configuring Entra ID for Azure Blob Storage with RBAC

**Scenario:** You are developing an ASP.NET Core website that can be used to manage photographs which are stored in Azure Blob Storage containers. Users of the website authenticate by using their Microsoft Entra ID credentials. You implement role-based access control (RBAC) role permissions on the containers that store photographs. You assign users to RBAC roles.

**Question:** You need to configure the website's Microsoft Entra ID Application so that user's permissions can be used with the Azure Blob containers. How should you configure the application?

**Configuration Options:**

| Option | Azure Storage Permission | Azure Storage Type | Microsoft Graph Type |
|--------|-------------------------|-------------------|---------------------|
| A | `client_id` | `application` | `user_impersonation` |
| B | `client_id` | `profile` | `application` |
| C | `user_impersonation` | `delegated` | `delegated` |
| D | `user_impersonation` | `delegated` | `profile` |

### Answer Analysis

#### ✅ Option C: CORRECT ANSWER

**Configuration:**
- **Azure Storage Permission:** `user_impersonation`
- **Azure Storage Type:** `delegated`
- **Microsoft Graph Type:** `delegated`

**Why this is CORRECT:**

1. **`user_impersonation` Permission for Azure Storage:**
   - This is the standard delegated permission scope for Azure Storage
   - Allows the application to access Azure Storage resources on behalf of the signed-in user
   - Enables the application to inherit the user's RBAC permissions
   - When a user accesses blob storage through the app, their assigned RBAC roles are enforced

2. **`delegated` Permission Type for Azure Storage:**
   - Delegated permissions require a signed-in user to be present
   - The application acts on behalf of the user, using their identity and permissions
   - This is exactly what's needed when users authenticate with their Entra ID credentials
   - Azure Storage will check the user's RBAC role assignments (e.g., Storage Blob Data Contributor, Storage Blob Data Reader)

3. **`delegated` Permission Type for Microsoft Graph:**
   - Allows the application to access Microsoft Graph resources on behalf of the signed-in user
   - Even if not explicitly mentioned in the scenario, this is the proper configuration for user-context applications
   - Maintains consistency in permission model across all Azure services

**Additional Explanation:** The configuration with Azure Storage Permission set to `user_impersonation`, Azure Storage Type set to `delegated`, and Microsoft Graph Type set to `delegated` is correct. User_impersonation is the appropriate permission for users to act on behalf of the application, delegated permissions are necessary for accessing resources on behalf of a user, and Microsoft Graph Type should also be set to `delegated` for this scenario.

**How it works:**

```plaintext
┌─────────────────────────────────────────────────────────────┐
│                     Authentication Flow                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. User logs in with Entra ID credentials                  │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
│  2. App requests delegated permissions                      │
│     - Azure Storage: user_impersonation                     │
│     - Microsoft Graph: delegated                            │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
│  3. User consents (or admin pre-consents)                   │
│  ◄──────────────────────────────────────────────────────────│
│                                                              │
│  4. Access token issued with user's identity                │
│  ◄──────────────────────────────────────────────────────────│
│                                                              │
│  5. App accesses Blob Storage with user's token             │
│     - User's RBAC permissions are checked                   │
│     - Storage Blob Data Contributor? → Read/Write           │
│     - Storage Blob Data Reader? → Read only                 │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Configuration Steps:**

```plaintext
1. Register Application in Entra ID:
   Azure Portal → Microsoft Entra ID → App registrations → New registration

2. Configure API Permissions:
   API permissions → Add a permission
   
   For Azure Storage:
   - Select "Azure Storage"
   - Select "Delegated permissions"
   - Check "user_impersonation"
   
   For Microsoft Graph (if needed):
   - Select "Microsoft Graph"
   - Select "Delegated permissions"
   - Add required scopes (e.g., User.Read)

3. Grant Admin Consent (if required):
   API permissions → Grant admin consent for [tenant]

4. Assign RBAC Roles to Users:
   Storage Account → Access Control (IAM) → Add role assignment
   - Storage Blob Data Contributor (read/write)
   - Storage Blob Data Reader (read-only)
   - Assign to users or groups
```

**Code Example (C# with Azure.Identity):**

```csharp
using Azure.Identity;
using Azure.Storage.Blobs;

public class BlobStorageService
{
    private readonly BlobServiceClient _blobServiceClient;

    public BlobStorageService(string storageAccountName)
    {
        // Use DefaultAzureCredential to authenticate
        // This will use the signed-in user's credentials in web apps
        var credential = new DefaultAzureCredential();
        
        string blobUri = $"https://{storageAccountName}.blob.core.windows.net";
        _blobServiceClient = new BlobServiceClient(new Uri(blobUri), credential);
    }

    public async Task<List<string>> ListPhotographsAsync(string containerName)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        var photos = new List<string>();

        // This call will use the user's RBAC permissions
        // If user lacks permissions, this will throw UnauthorizedException
        await foreach (var blobItem in containerClient.GetBlobsAsync())
        {
            photos.Add(blobItem.Name);
        }

        return photos;
    }

    public async Task UploadPhotographAsync(string containerName, string fileName, Stream content)
    {
        var containerClient = _blobServiceClient.GetBlobContainerClient(containerName);
        var blobClient = containerClient.GetBlobClient(fileName);
        
        // This requires Storage Blob Data Contributor role
        await blobClient.UploadAsync(content, overwrite: true);
    }
}
```

**Startup Configuration:**

```csharp
// Program.cs or Startup.cs
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();

// Register blob storage service
builder.Services.AddSingleton<BlobStorageService>(sp => 
    new BlobStorageService("yourstorageaccount"));
```

**appsettings.json:**

```json
{
  "AzureAd": {
    "Instance": "https://login.microsoftonline.com/",
    "Domain": "yourdomain.onmicrosoft.com",
    "TenantId": "your-tenant-id",
    "ClientId": "your-client-id",
    "ClientSecret": "your-client-secret",
    "CallbackPath": "/signin-oidc"
  }
}
```

---

#### ❌ Option A: Incorrect

**Configuration:**
- **Azure Storage Permission:** `client_id`
- **Azure Storage Type:** `application`
- **Microsoft Graph Type:** `user_impersonation`

**Why this is WRONG:**

1. **`client_id` is NOT a permission scope:**
   - `client_id` is an identifier for the application, not a permission
   - Azure Storage API permissions use `user_impersonation` for delegated access
   - This configuration would fail at the permission request stage

2. **`application` type conflicts with user context:**
   - Application permissions are used for service-to-service scenarios (no user present)
   - The scenario explicitly states users authenticate with their Entra ID credentials
   - Application permissions would grant the app access to ALL blobs, ignoring user RBAC

3. **`user_impersonation` for Microsoft Graph is inconsistent:**
   - Mixing application type for Storage with delegated type for Graph is invalid
   - Shows confused understanding of permission models
   - `user_impersonation` is not a standard Microsoft Graph permission name

**Additional Explanation:** The configuration with Azure Storage Permission set to `client_id`, Azure Storage Type set to `application`, and Microsoft Graph Type set to `user_impersonation` is incorrect because user_impersonation typically requires delegated permissions, not application permissions, for accessing resources on behalf of a user.

**Result:** This configuration is invalid and would not work.

---

#### ❌ Option B: Incorrect

**Configuration:**
- **Azure Storage Permission:** `client_id`
- **Azure Storage Type:** `profile`
- **Microsoft Graph Type:** `application`

**Why this is WRONG:**

1. **`client_id` is not a valid permission:**
   - As mentioned above, this is an identifier, not a permission scope
   - Cannot be requested as a permission

2. **`profile` is not a valid Azure Storage permission type:**
   - `profile` is an OpenID Connect scope for user profile information
   - Azure Storage API uses either `delegated` or `application` permission types
   - `profile` has nothing to do with storage access

3. **`application` type for Microsoft Graph is inappropriate:**
   - Application permissions don't require a signed-in user
   - Would grant app-level access instead of user-level access
   - Doesn't align with the scenario where users authenticate

4. **Completely wrong permission model:**
   - This configuration shows fundamental misunderstanding of Azure permissions
   - Mixes unrelated concepts (client_id, profile, application)

**Additional Explanation:** The configuration with Azure Storage Permission set to `client_id`, Azure Storage Type set to `profile`, and Microsoft Graph Type set to `application` is incorrect. The profile type is not relevant for Azure Blob Storage permissions, and the client_id parameter is not suitable for this scenario.

**Result:** This configuration is completely invalid.

---

#### ❌ Option D: Incorrect

**Configuration:**
- **Azure Storage Permission:** `user_impersonation`
- **Azure Storage Type:** `delegated`
- **Microsoft Graph Type:** `profile`

**Why this is WRONG:**

1. **Azure Storage configuration is CORRECT:**
   - `user_impersonation` with `delegated` is the right approach
   - This part would work fine

2. **`profile` is NOT a Microsoft Graph permission type:**
   - `profile` is an OpenID Connect scope, not a permission type
   - Microsoft Graph permission types are `delegated` or `application`
   - `profile` is used for authentication, not for API permissions

3. **Inconsistent permission configuration:**
   - While the Storage configuration is correct, the Graph configuration is invalid
   - Shows incomplete understanding of Azure permission structure

**Why it's close but wrong:**
- Gets 2 out of 3 parameters correct
- However, in exam scenarios, all parameters must be correct
- `profile` as a permission type is a fundamental error

**Additional Explanation:** The configuration with Azure Storage Permission set to `user_impersonation`, Azure Storage Type set to `delegated`, and Microsoft Graph Type set to `profile` is incorrect. The profile type is not relevant for Azure Blob Storage permissions, and the Microsoft Graph Type should be set to `delegated` for accessing resources on behalf of a user.

**Result:** Partially correct, but invalid overall due to wrong Microsoft Graph configuration.

---

### Summary: Understanding Azure Permission Types

#### Delegated Permissions vs Application Permissions

| Aspect | Delegated Permissions | Application Permissions |
|--------|----------------------|------------------------|
| **User Context** | ✅ Requires signed-in user | ❌ No user required |
| **Permissions** | User's permissions | App-level permissions |
| **Use Case** | User acts through app | Background services |
| **RBAC** | ✅ User's RBAC roles enforced | ❌ App has its own RBAC |
| **Consent** | User or admin consent | Admin consent required |
| **Example Scenario** | Photo management web app | Nightly backup job |

#### Azure Storage Permission Scopes

| Permission Scope | Type | Description |
|-----------------|------|-------------|
| **`user_impersonation`** | Delegated | Access storage as the signed-in user |
| **No specific scope name** | Application | Service-level access (uses app's managed identity or service principal) |

#### Microsoft Graph Permission Types

| Type | Use When | Examples |
|------|---------|----------|
| **`delegated`** | User is present | User.Read, Mail.Read, Files.Read |
| **`application`** | Background service | User.Read.All, Mail.Read.All |

> **Exam Tip:** When users authenticate with Entra ID credentials and the app accesses Azure resources on their behalf, ALWAYS use:
> - **Delegated permissions** for the permission type
> - **`user_impersonation`** for Azure Storage
> - This ensures user RBAC permissions are enforced

---

### Key Takeaways for This Scenario

✅ **DO:**
- Use delegated permissions when users authenticate
- Configure `user_impersonation` for Azure Storage
- Assign RBAC roles to users on storage resources
- Use Azure.Identity library for seamless authentication
- Test with users having different RBAC roles

❌ **DON'T:**
- Use application permissions for user-context scenarios
- Use `client_id` as a permission (it's an identifier)
- Use `profile` as a permission type (it's an OIDC scope)
- Mix application and delegated permission types incorrectly
- Forget to assign RBAC roles to users

**Remember:** The combination of Entra ID authentication + delegated permissions + RBAC enables fine-grained, user-specific access control to Azure Storage resources.

---

### Exam Question 5: Configuring Multifactor Authentication for Web App

**Scenario:** You are developing a web app that uses Microsoft Entra ID for authentication. You want to configure the web app to use multifactor authentication.

**Question:** What should you do?

### Answer Options Analysis

#### ❌ Option 1: Enable mobile app authentication

**Why this is WRONG:**
- Enabling mobile app authentication is NOT directly related to configuring multifactor authentication for a web app
- While mobile app authentication (Microsoft Authenticator) can be **part** of multifactor authentication, it is not the only step required
- Mobile app authentication is a **method/factor** that users can use, not the configuration that enforces MFA
- Simply enabling it does not ensure that users will be required to use MFA

**What mobile app authentication actually is:**
- One of several possible second-factor authentication methods
- Includes Microsoft Authenticator app for push notifications or time-based codes
- Can be used after MFA is enforced through Conditional Access

---

#### ❌ Option 2: In Microsoft Entra ID conditional access, enable the baseline policy

**Why this is NOT specifically correct:**
- Baseline policies were **legacy** Conditional Access policies that are now **deprecated**
- They focused on enforcing security requirements for all users in an organization
- They were replaced by more flexible and customizable Conditional Access policies
- While baseline policies could enforce MFA, they are no longer the recommended approach
- Modern Conditional Access policies provide better control and customization

**About baseline policies:**
- Pre-configured security policies that were available in earlier versions of Azure AD
- Provided basic security protections but lacked flexibility
- **Deprecated** in favor of custom Conditional Access policies and security defaults
- Not the current best practice for configuring MFA

---

#### ✅ Option 3: In Microsoft Entra ID, create a conditional access policy - CORRECT ANSWER

**Why this is CORRECT:**

1. **Conditional Access is the primary method for enforcing MFA:**
   - Allows you to define specific conditions under which users must provide MFA
   - Provides granular control over when and how MFA is required
   - Can be applied to specific users, groups, applications, or scenarios

2. **Flexible and customizable:**
   - Target specific applications (your web app)
   - Target specific user groups or roles
   - Define conditions (location, device state, risk level)
   - Control session behavior and access requirements

3. **Modern best practice:**
   - Microsoft's recommended approach for enforcing MFA
   - Part of Microsoft Entra ID Premium P1 or P2 licenses
   - Integrates with other security features like Identity Protection

4. **Meets the scenario requirements:**
   - Specifically configures MFA enforcement for the web app
   - Ensures users authenticate with multiple factors before accessing the app
   - Provides control over authentication requirements

**How Conditional Access works:**

```plaintext
┌─────────────────────────────────────────────────────────────┐
│           Conditional Access Policy Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User attempts to sign in to web app                        │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
│  Conditional Access evaluates policies:                     │
│  • Which user/group? (Assignment)                           │
│  • Which application? (Cloud apps)                          │
│  • From where? (Conditions: location, device, risk)         │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
│  Policy requires MFA:                                        │
│  • Grant access only after MFA                              │
│  ──────────────────────────────────────────────────────────►│
│                                                              │
│  User completes MFA (second factor):                        │
│  • Microsoft Authenticator                                  │
│  • SMS/Phone call                                           │
│  • FIDO2 security key                                       │
│  • Windows Hello                                            │
│  ◄──────────────────────────────────────────────────────────│
│                                                              │
│  Access granted to web app                                  │
│  ◄──────────────────────────────────────────────────────────│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Configuration Steps:**

```plaintext
1. Navigate to Conditional Access:
   Azure Portal → Microsoft Entra ID → Security → Conditional Access

2. Create new policy:
   → New policy → Name: "Require MFA for Web App"

3. Configure Assignments:
   Users:
   - Select users or groups that need MFA
   - Or select "All users"
   
   Cloud apps or actions:
   - Select your web app from the list
   - Or select "All cloud apps" for organization-wide MFA

4. Configure Conditions (optional but recommended):
   Locations:
   - Require MFA when accessing from outside corporate network
   
   Device platforms:
   - Require MFA for specific platforms (iOS, Android, etc.)
   
   Sign-in risk:
   - Require MFA for medium or high-risk sign-ins

5. Configure Access Controls:
   Grant:
   - Select "Grant access"
   - Check "Require multifactor authentication"
   - Can also add: "Require device to be marked as compliant"

6. Enable policy:
   - Set "Enable policy" to "On"
   - Choose "Report-only" for testing first (recommended)
   - Click "Create"

7. Test the policy:
   - Test with a user account
   - Verify MFA prompt appears when accessing the web app
   - Move to "On" after successful testing
```

**Example Conditional Access Policy Configuration:**

| Setting | Value |
|---------|-------|
| **Name** | Require MFA for Web App |
| **Assignments - Users** | All users (or specific group) |
| **Assignments - Cloud apps** | Select your web app |
| **Conditions - Locations** | Any location (or exclude trusted locations) |
| **Access Controls - Grant** | Grant access + Require multifactor authentication |
| **Enable policy** | On |

**Code Example - No changes needed in application code:**

Your web app code remains the same. When users authenticate through Microsoft Entra ID, the Conditional Access policy automatically enforces MFA:

```csharp
// Program.cs or Startup.cs
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization();

// The Conditional Access policy handles MFA enforcement
// No additional code required
```

**What happens from user perspective:**

1. User navigates to your web app
2. App redirects to Microsoft Entra ID sign-in
3. User enters username and password (first factor)
4. **Conditional Access policy triggers**
5. User prompted for second factor (MFA):
   - Microsoft Authenticator push notification
   - Or SMS code
   - Or phone call
   - Or FIDO2 security key
6. After successful MFA, user redirected back to app with token
7. User authenticated and authorized

---

#### ❌ Option 4: Install the Azure Multi-Factor Authentication Server

**Why this is WRONG:**
- Azure Multi-Factor Authentication Server is an **on-premises solution**
- Designed for legacy applications and services that cannot integrate with cloud-based Azure MFA
- Typically used for on-premises VPN, RADIUS-based applications, and legacy systems
- **NOT necessary** for cloud-based web apps using Microsoft Entra ID
- Adds unnecessary complexity and infrastructure maintenance
- Microsoft recommends cloud-based MFA (via Conditional Access) for modern applications

**When Azure MFA Server might be used:**
- On-premises applications that cannot use modern authentication
- RADIUS-based authentication (VPN, network devices)
- IIS-based applications using forms authentication
- Legacy scenarios where cloud integration is not possible

**Why it's wrong for this scenario:**
- The web app already uses Microsoft Entra ID for authentication
- Cloud-based MFA through Conditional Access is the modern, simpler approach
- No need for additional servers or infrastructure
- Azure MFA Server is being phased out by Microsoft

---

### Summary: Configuring MFA for Web Apps with Microsoft Entra ID

#### Comparison of Options

| Option | Purpose | Appropriate for Web App MFA? | Notes |
|--------|---------|------------------------------|-------|
| **Create Conditional Access policy** | ✅ Enforce MFA requirements | ✅ YES - Correct approach | Modern, flexible, recommended |
| **Enable mobile app authentication** | Configure authentication method | ❌ NO - Incomplete | Only enables a method, doesn't enforce |
| **Enable baseline policy** | Legacy security policies | ❌ NO - Deprecated | Use custom Conditional Access instead |
| **Install MFA Server** | On-premises MFA solution | ❌ NO - Wrong architecture | For legacy/on-premises apps only |

#### The Correct Approach: Conditional Access

**Key Benefits:**
- ✅ Cloud-native solution (no infrastructure to manage)
- ✅ Granular control (target specific apps, users, conditions)
- ✅ No code changes required in application
- ✅ Integrates with Microsoft Entra ID seamlessly
- ✅ Supports multiple MFA methods automatically
- ✅ Can enforce additional security controls (compliant devices, etc.)

**MFA Methods Supported (automatically):**
- Microsoft Authenticator app (push notification)
- Microsoft Authenticator app (verification code)
- SMS text message
- Phone call
- FIDO2 security key
- Windows Hello for Business
- Certificate-based authentication

> **Exam Tip:** When asked about configuring MFA for a web app using Microsoft Entra ID, the correct answer is to **create a Conditional Access policy**. This is the modern, cloud-based approach that provides granular control over when and how MFA is enforced.

---

### Additional Considerations

#### Licensing Requirements

| Feature | Required License |
|---------|-----------------|
| **Conditional Access policies** | Microsoft Entra ID Premium P1 or P2 |
| **Security Defaults (basic MFA)** | Free with any Microsoft Entra ID |
| **Risk-based Conditional Access** | Microsoft Entra ID Premium P2 |
| **Identity Protection** | Microsoft Entra ID Premium P2 |

#### Security Defaults vs Conditional Access

**Security Defaults** (simpler but less flexible):
- Free with any Microsoft Entra ID tenant
- Automatically enforces MFA for all users
- No customization or exceptions
- Good for small organizations or quick setup

**Conditional Access** (more control):
- Requires Premium P1 or P2 license
- Granular control over policies
- Target specific apps, users, or conditions
- Better for enterprise scenarios
- **Recommended for the exam scenario**

#### Best Practices

✅ **DO:**
- Use Conditional Access for MFA enforcement
- Test policies in "Report-only" mode first
- Enable MFA for administrator accounts first
- Provide clear communication to users before rollout
- Register multiple MFA methods for redundancy

❌ **DON'T:**
- Rely only on mobile app authentication configuration
- Use deprecated baseline policies
- Install on-premises MFA Server for cloud apps
- Lock yourself out (exclude emergency access accounts)
- Enable policies without testing

---

## Summary and Key Takeaways

### Choose the Right Method

| Scenario | Use This | Don't Use This |
|----------|---------|----------------|
| **Azure App Service app needing quick auth** | ✅ Easy Auth | ❌ Custom implementation |
| **Standard Azure web app** | ✅ OpenID Connect / OAuth 2.0 | ❌ External ID, Graph API, Self-hosted |
| **Consumer app** | ✅ External ID (B2C) | ❌ Standard Entra ID for internal use |
| **Access Microsoft 365 data** | ✅ OAuth 2.0 + Microsoft Graph | ❌ Graph API for authentication |
| **Enterprise authentication** | ✅ Standard Entra ID | ❌ Self-hosted provider |

---

### Authentication Decision Tree

```
Need user authentication?
    │
    ├─ Hosting on Azure App Service?
    │   ├─ Want zero-code solution?
    │   │   └─ ✅ Use: Easy Auth (App Service Authentication)
    │   └─ Need custom control?
    │       └─ ✅ Use: OpenID Connect / OAuth 2.0 with MSAL
    │
    ├─ Internal employees/partners?
    │   └─ ✅ Use: OpenID Connect / OAuth 2.0 with Entra ID
    │
    ├─ External consumers/customers?
    │   ├─ Need social logins or custom branding?
    │   │   └─ ✅ Use: Microsoft Entra External ID (B2C)
    │   └─ Simple email/password?
    │       └─ ✅ Use: OpenID Connect / OAuth 2.0 (can work)
    │
    └─ Background service (no user)?
        └─ ✅ Use: Client Credentials Flow
```

---

### The Golden Rule

**For Azure web applications requiring Microsoft Entra ID authentication:**

✅ **ALWAYS use OpenID Connect / OAuth 2.0 as the identity provider**

❌ **NEVER:**
- Use Graph API to directly validate credentials
- Implement self-hosted providers when Entra ID exists
- Use External ID for simple employee authentication

---

### Quick Reference

| Need | Solution |
|------|----------|
| Zero-code auth for App Service | Easy Auth (App Service Authentication) |
| Authenticate employees | OpenID Connect with Entra ID |
| Authenticate consumers | External ID (B2C) with user flows |
| Access user's Microsoft 365 data | OAuth 2.0 + Microsoft Graph API |
| Service-to-service auth | Client Credentials Flow |
| Propagate user through API chain | On-Behalf-Of (OBO) Flow |
| Mobile/SPA auth | OAuth 2.0 with PKCE |

---

## Additional Resources

### Official Documentation

- [Microsoft identity platform documentation](https://learn.microsoft.com/en-us/entra/identity-platform/)
- [Azure App Service Authentication](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
- [OpenID Connect on Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)
- [OAuth 2.0 authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow)
- [Microsoft Entra External ID documentation](https://learn.microsoft.com/en-us/entra/external-id/)
- [Microsoft Graph API documentation](https://learn.microsoft.com/en-us/graph/)

### Libraries and SDKs

- [Microsoft.Identity.Web (.NET)](https://github.com/AzureAD/microsoft-identity-web)
- [MSAL.NET](https://github.com/AzureAD/microsoft-authentication-library-for-dotnet)
- [MSAL.js (JavaScript)](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [MSAL React](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)
- [MSAL Node.js](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-node)

### Samples

- [Microsoft identity platform code samples](https://learn.microsoft.com/en-us/entra/identity-platform/sample-v2-code)
- [Azure AD B2C samples](https://learn.microsoft.com/en-us/azure/active-directory-b2c/code-samples)

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2025  
**Author:** Azure Learning Documentation

---

End of Document
