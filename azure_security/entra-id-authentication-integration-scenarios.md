# Microsoft Entra ID Authentication Integration Scenarios

## Overview

This document provides comprehensive guidance on integrating Microsoft Entra ID (formerly Azure Active Directory) for authentication in various application scenarios. It covers different authentication methods, protocols, and best practices for implementing secure user authentication across different application types.

---

## Table of Contents

1. [Authentication Methods Overview](#authentication-methods-overview)
2. [Azure App Service Authentication (Easy Auth)](#azure-app-service-authentication-easy-auth)
3. [OpenID Connect and OAuth 2.0 Integration](#openid-connect-and-oauth-20-integration)
4. [Microsoft Entra External ID (formerly Azure AD B2C)](#microsoft-entra-external-id-formerly-azure-ad-b2c)
5. [Microsoft Graph API Integration](#microsoft-graph-api-integration)
6. [Self-Hosted Identity Providers](#self-hosted-identity-providers)
7. [Comparison of Authentication Approaches](#comparison-of-authentication-approaches)
8. [Implementation Scenarios](#implementation-scenarios)
9. [Best Practices and Recommendations](#best-practices-and-recommendations)

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

#### Authorization Code Flow with PKCE (for SPAs and Mobile Apps)

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

#### Implicit Flow (Legacy - Not Recommended)

⚠️ **Deprecated**: Use Authorization Code Flow with PKCE instead

```
Tokens returned directly in URL fragment (less secure)
No refresh tokens
Susceptible to token leakage
```

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
