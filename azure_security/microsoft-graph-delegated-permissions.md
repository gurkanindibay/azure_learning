# Microsoft Graph Delegated Permissions for Signed-In Users
## Table of Contents

- [Overview](#overview)
- [What is Microsoft Graph?](#what-is-microsoft-graph)
  - [Microsoft Graph Scope](#microsoft-graph-scope)
  - [Why This Document Focuses on Security](#why-this-document-focuses-on-security)
  - [Key Insight](#key-insight)
  - [Example Use Cases Beyond Security](#example-use-cases-beyond-security)
  - [Reference](#reference)
- [Question 1: Delegated Permissions](#question-1-delegated-permissions)
- [Question 2: On-Behalf-Of (OBO) Flow](#question-2-on-behalf-of-obo-flow)
- [Understanding Delegated Permissions](#understanding-delegated-permissions)
  - [What Are Delegated Permissions?](#what-are-delegated-permissions)
  - [How Delegated Permissions Work](#how-delegated-permissions-work)
  - [Key Characteristics](#key-characteristics)
- [Why Other Options Are Incorrect](#why-other-options-are-incorrect)
  - [appRoles](#approles)
  - [Application Permissions](#application-permissions)
  - [groupMembershipClaims](#groupmembershipclaims)
- [Implementation Example](#implementation-example)
  - [1. Register the Application in Microsoft Entra ID](#1-register-the-application-in-microsoft-entra-id)
  - [2. Configure Delegated Permissions](#2-configure-delegated-permissions)
  - [3. Example Code (C# with MSAL)](#3-example-code-c-with-msal)
  - [4. Example Code (JavaScript/Node.js with MSAL)](#4-example-code-javascriptnodejs-with-msal)
- [Permission Consent Flow](#permission-consent-flow)
  - [User Consent](#user-consent)
  - [Admin Consent](#admin-consent)
- [Common Delegated Permission Scopes](#common-delegated-permission-scopes)
- [Security Considerations](#security-considerations)
  - [Least Privilege Principle](#least-privilege-principle)
  - [Token Lifetime](#token-lifetime)
  - [Secure Token Storage](#secure-token-storage)
- [OAuth 2.0 On-Behalf-Of (OBO) Flow](#oauth-20-on-behalf-of-obo-flow)
  - [What Is On-Behalf-Of Flow?](#what-is-on-behalf-of-flow)
  - [When to Use OBO Flow](#when-to-use-obo-flow)
  - [How OBO Flow Works](#how-obo-flow-works)
  - [OBO Flow Diagram](#obo-flow-diagram)
  - [Implementation Example](#implementation-example-2)
  - [Why Other Authentication Flows Are Incorrect](#why-other-authentication-flows-are-incorrect)
    - [Authorization Code Flow](#authorization-code-flow)
    - [Client Credentials Flow](#client-credentials-flow)
    - [Implicit Flow](#implicit-flow)
  - [OBO Flow vs Other Flows](#obo-flow-vs-other-flows)
  - [OBO Flow Requirements](#obo-flow-requirements)
  - [OBO Flow Security Considerations](#obo-flow-security-considerations)
- [Continuous Access Evaluation (CAE)](#continuous-access-evaluation-cae)
  - [Question 3: Enabling CAE in MSAL.NET](#question-3-enabling-cae-in-msalnet)
  - [What is Continuous Access Evaluation?](#what-is-continuous-access-evaluation)
  - [How to Enable CAE in MSAL.NET](#how-to-enable-cae-in-msalnet)
  - [Why Other Options Are Incorrect](#why-other-cae-options-are-incorrect)
  - [Handling Claims Challenges](#handling-claims-challenges)
  - [CAE Critical Events](#cae-critical-events)
- [Comparison Table](#comparison-table)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
- [References](#references)
- [Summary](#summary)
  - [For Direct Microsoft Graph Access (Question 1)](#for-direct-microsoft-graph-access-question-1)
  - [For Service Chain with User Identity (Question 2)](#for-service-chain-with-user-identity-question-2)


## Overview

When an Azure App Service web app needs to retrieve Microsoft Entra ID signed-in user information using Microsoft Graph, it must use **delegated permissions**. This document explains the mechanism and the differences between various permission types, as well as the OAuth 2.0 On-Behalf-Of (OBO) flow for delegating user identity through request chains.

## What is Microsoft Graph?

Microsoft Graph is often mentioned in security contexts, which can make it seem like it's only for authentication and identity management. However, **Microsoft Graph is much broader** - it's the unified API gateway to access data and intelligence across the entire Microsoft 365 ecosystem.

### Microsoft Graph Scope

Microsoft Graph provides access to:

1. **Microsoft 365 Core Services**:
   - Bookings, Calendar, Delve
   - Excel, Word, PowerPoint (document data)
   - Microsoft 365 compliance eDiscovery
   - Microsoft Search
   - OneDrive, OneNote
   - Outlook/Exchange (email, contacts)
   - Planner, SharePoint, Teams
   - To Do, Workplace Analytics

2. **Enterprise Mobility and Security Services**:
   - Advanced Threat Analytics
   - Advanced Threat Protection
   - **Azure Active Directory (Microsoft Entra ID)** - User profiles, authentication
   - Identity Manager
   - Intune (device management)

3. **Windows 10 Services**:
   - Activities, devices, notifications
   - Universal Print

4. **Dynamics 365 Business Central**

### Why This Document Focuses on Security

This document focuses on **delegated permissions for accessing user identity information** because:

- Authentication and authorization are foundational requirements
- User profile access is one of the most common Microsoft Graph operations
- Understanding delegated vs application permissions is critical for security
- The same permission model applies whether you're accessing user data, emails, or calendars

### Key Insight

**Microsoft Graph is not just for security** - it's the unified API for **all Microsoft 365 data**, including:
- ✅ Documents (Word, Excel, PowerPoint files in OneDrive/SharePoint)
- ✅ Email and calendar events (Outlook)
- ✅ Teams messages and meetings
- ✅ User profiles and organizational data
- ✅ SharePoint sites and lists
- ✅ Planner tasks
- ❌ NOT Azure resources (use Azure Resource Manager API for that)
- ❌ NOT columnar/relational database data
- ❌ NOT raw JSON/XML documents (though API responses use JSON)

### Example Use Cases Beyond Security

```csharp
// Beyond user profiles, Microsoft Graph can access:

// 1. Read user's emails
var messages = await graphClient.Me.Messages.GetAsync();

// 2. Access calendar events
var events = await graphClient.Me.Events.GetAsync();

// 3. Get files from OneDrive
var files = await graphClient.Me.Drive.Root.Children.GetAsync();

// 4. Send emails as the user
var message = new Message { /* email content */ };
await graphClient.Me.SendMail(message).Request().PostAsync();

// 5. Access Teams data
var teams = await graphClient.Me.JoinedTeams.GetAsync();

// 6. Read SharePoint lists
var lists = await graphClient.Sites["site-id"].Lists.GetAsync();
```

### Reference

For complete details on Microsoft Graph capabilities, see: [Microsoft Graph Overview](https://docs.microsoft.com/en-us/graph/overview)

## Question 1: Delegated Permissions

**Scenario**: An Azure App Service web app (app1) registered in Microsoft Entra ID needs to retrieve signed-in user information using Microsoft Graph.

**Solution**: Configure **delegated permissions**

## Question 2: On-Behalf-Of (OBO) Flow

**Scenario**: You manage a Microsoft Entra ID registered application named app1. App1 calls a web API, which then calls Microsoft Graph. You need to ensure the signed-in user identity is delegated through the request chain.

**Question**: Which authentication flow should you use?

**Options**:
- Authorization code
- **On-Behalf-Of** ✅ (Correct Answer)
- Client credentials
- Implicit

**Solution**: Use the **OAuth 2.0 On-Behalf-Of (OBO) flow**

## Understanding Delegated Permissions

### What Are Delegated Permissions?

Delegated permissions are used by applications that have a **signed-in user present**. These permissions allow the app to act on behalf of the signed-in user when making calls to Microsoft Graph.

### How Delegated Permissions Work

1. **User Signs In**: The user authenticates with Microsoft Entra ID
2. **Consent Process**: Either the user or an administrator consents to the permissions the app requests
3. **Token Acquisition**: The app receives an access token that includes the user's identity
4. **API Calls**: The app makes Microsoft Graph API calls as the signed-in user
5. **Scope Limitation**: The app can only access data that the signed-in user has permission to access

### Key Characteristics

- ✅ Requires a signed-in user
- ✅ App acts on behalf of the user
- ✅ Respects user's permissions and access rights
- ✅ Appropriate for web apps, mobile apps, and SPAs
- ✅ Can be consented by users (for some permissions) or requires admin consent (for sensitive permissions)

## Why Other Options Are Incorrect

### appRoles

**What it is**: An attribute in the application manifest that specifies the collection of roles an app may declare.

**Purpose**: 
- Defines custom application roles
- Roles can be assigned to users, groups, or service principals
- Used for role-based access control (RBAC) within the application

**Why it's not the answer**: 
- Does not grant permissions to access Microsoft Graph
- Only defines roles within the application itself
- Does not enable retrieval of user information from Microsoft Graph

### Application Permissions

**What it is**: Permissions used by apps that run **without a signed-in user present**.

**Purpose**:
- Used by background services, daemons, or server-to-server scenarios
- App acts with its own identity, not on behalf of a user
- Requires administrator consent only

**Examples**:
- Batch processing jobs
- Data synchronization services
- Monitoring and reporting tools

**Why it's not the answer**:
- No signed-in user context
- App acts as itself, not as the user
- Cannot retrieve information specific to a signed-in user
- Would access data based on app's permissions, not user's identity

### groupMembershipClaims

**What it is**: An attribute in the application manifest that configures the groups claim in tokens.

**Purpose**:
- Configures how group membership information is included in tokens
- Can be set to: `None`, `SecurityGroup`, `All`, `ApplicationGroup`, or `DirectoryRole`
- Affects the claims in the user or OAuth 2.0 access token

**Why it's not the answer**:
- Only affects what claims are included in the token
- Does not grant permissions to call Microsoft Graph
- Does not enable the app to retrieve user information via API calls

## Implementation Example

### 1. Register the Application in Microsoft Entra ID

```plaintext
- Navigate to Azure Portal → Microsoft Entra ID → App registrations
- Register app1 as an application
- Note the Application (client) ID and Directory (tenant) ID
```

### 2. Configure Delegated Permissions

```plaintext
- Go to API permissions → Add a permission
- Select Microsoft Graph → Delegated permissions
- Add required permissions:
  - User.Read (read signed-in user's profile)
  - User.ReadBasic.All (read all users' basic profiles)
  - Other permissions as needed
```

### 3. Example Code (C# with MSAL)

```csharp
using Microsoft.Identity.Client;
using Microsoft.Graph;
using Azure.Identity;

// Configure authentication
var scopes = new[] { "User.Read" };

// For web apps using authorization code flow
var options = new InteractiveBrowserCredentialOptions
{
    TenantId = "your-tenant-id",
    ClientId = "your-client-id",
    RedirectUri = new Uri("https://your-app.azurewebsites.net/signin-oidc")
};

var credential = new InteractiveBrowserCredential(options);

// Create Graph client
var graphClient = new GraphServiceClient(credential, scopes);

// Get signed-in user information
var user = await graphClient.Me.GetAsync();

Console.WriteLine($"Display Name: {user.DisplayName}");
Console.WriteLine($"Email: {user.Mail}");
Console.WriteLine($"Job Title: {user.JobTitle}");

// Get user's photo
var photoStream = await graphClient.Me.Photo.Content.GetAsync();
```

### 4. Example Code (JavaScript/Node.js with MSAL)

```javascript
const msal = require('@azure/msal-node');
const graph = require('@microsoft/microsoft-graph-client');

// MSAL configuration
const msalConfig = {
    auth: {
        clientId: 'your-client-id',
        authority: 'https://login.microsoftonline.com/your-tenant-id',
        clientSecret: 'your-client-secret'
    }
};

const cca = new msal.ConfidentialClientApplication(msalConfig);

// Get token on behalf of user
const tokenRequest = {
    scopes: ['User.Read'],
    account: userAccount // obtained during sign-in
};

const response = await cca.acquireTokenSilent(tokenRequest);

// Create Graph client
const client = graph.Client.init({
    authProvider: (done) => {
        done(null, response.accessToken);
    }
});

// Get signed-in user info
const user = await client.api('/me').get();
console.log(`User: ${user.displayName}`);
```

## Permission Consent Flow

### User Consent

```plaintext
1. User attempts to sign in to app1
2. App redirects to Microsoft Entra ID login
3. User sees consent screen listing permissions
4. User grants consent
5. User is redirected back to app with authorization code
6. App exchanges code for access token
7. App can now call Microsoft Graph on behalf of user
```

### Admin Consent

Some permissions require administrator consent:

```plaintext
- Admin navigates to app registration
- Goes to API permissions
- Clicks "Grant admin consent for [organization]"
- All users can now use the app without individual consent
```

## Common Delegated Permission Scopes

| Permission | Description |
|------------|-------------|
| `User.Read` | Read signed-in user's profile |
| `User.ReadWrite` | Read and update signed-in user's profile |
| `User.ReadBasic.All` | Read all users' basic profiles |
| `Mail.Read` | Read user's mail |
| `Mail.Send` | Send mail as the user |
| `Calendars.Read` | Read user's calendars |
| `Files.Read` | Read user's files |
| `People.Read` | Read user's relevant people list |

## Security Considerations

### Least Privilege Principle

- Only request permissions your app actually needs
- Start with minimal permissions and add more as needed
- Be specific: use `User.Read` instead of `User.ReadWrite` if you only need to read

### Token Lifetime

- Access tokens expire (typically after 1 hour)
- Implement token refresh logic
- Use refresh tokens to obtain new access tokens
- Handle token expiration gracefully

### Secure Token Storage

- Never store tokens in client-side code
- Use secure storage mechanisms (KeyVault, encrypted cookies)
- Protect client secrets and credentials
- Use managed identities when possible

## OAuth 2.0 On-Behalf-Of (OBO) Flow

### What Is On-Behalf-Of Flow?

The OAuth 2.0 On-Behalf-Of (OBO) flow is used when an application invokes a service or web API, which in turn needs to call another service or web API. The purpose is to **propagate the delegated user identity and permissions through the request chain**.

### When to Use OBO Flow

Use OBO flow when:
- Your app calls a middle-tier web API
- That web API needs to call a downstream API (like Microsoft Graph)
- You need to maintain the signed-in user's identity through the entire chain
- User permissions should be respected at each level

### How OBO Flow Works

```plaintext
1. User authenticates with app1
2. App1 receives an access token for the user
3. App1 calls middle-tier API with the access token
4. Middle-tier API uses OBO flow to exchange the token for a new token
5. New token contains the user's identity and permissions
6. Middle-tier API calls Microsoft Graph with the new token
7. Microsoft Graph responds based on user's permissions
8. Response flows back through the chain to app1
```

### OBO Flow Diagram

```
User → App1 (Client) → Middle-tier API → Microsoft Graph
         ↓                    ↓                 ↓
    Token (User)      OBO Exchange        User Context
                      (New Token)         Maintained
```

### Implementation Example

**Middle-tier API receiving the token:**

```csharp
using Microsoft.Identity.Client;
using Microsoft.Graph;

// Received access token from app1
string userAccessToken = // from Authorization header

// Configure MSAL for OBO
var app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithClientSecret(clientSecret)
    .WithAuthority(new Uri(authority))
    .Build();

// User assertion from the incoming token
var userAssertion = new UserAssertion(userAccessToken);

// Request new token on behalf of user
var result = await app.AcquireTokenOnBehalfOf(
    new[] { "https://graph.microsoft.com/User.Read" },
    userAssertion)
    .ExecuteAsync();

// Use the new token to call Microsoft Graph
var graphClient = new GraphServiceClient(
    new DelegateAuthenticationProvider((requestMessage) =>
    {
        requestMessage.Headers.Authorization = 
            new AuthenticationHeaderValue("Bearer", result.AccessToken);
        return Task.CompletedTask;
    }));

var user = await graphClient.Me.GetAsync();
```

### Why Other Authentication Flows Are Incorrect

#### Authorization Code Flow

**What it is**: OAuth 2.0 authorization code grant used in apps installed on a device to gain access to protected resources.

**Purpose**:
- Used for initial user authentication
- Obtains access tokens for the app to call APIs
- Typically used by web apps, mobile apps, and SPAs

**Why it's not the answer**:
- Used for the **initial** authentication, not for propagating identity
- Does not handle the middle-tier scenario
- Cannot exchange one token for another while maintaining user context

#### Client Credentials Flow

**What it is**: OAuth 2.0 client credentials grant that permits a web service to use its own credentials instead of impersonating a user.

**Purpose**:
- Service-to-service authentication
- No user context involved
- App acts as itself, not on behalf of a user

**Why it's not the answer**:
- ❌ Does **not** propagate user identity
- ❌ Does **not** maintain user permissions
- ❌ Cannot delegate user context through the chain
- Only suitable for app-only scenarios without users

#### Implicit Flow

**What it is**: A redirection-based flow where the client interacts with the resource owner's user-agent (typically a web browser).

**Purpose**:
- Legacy flow for single-page applications
- Tokens returned directly in URL fragment
- Now superseded by authorization code with PKCE

**Why it's not the answer**:
- ❌ Cannot delegate user permission and identity through chains
- ❌ Not designed for service-to-service calls
- ❌ Deprecated for security reasons
- Only handles initial user authentication in browsers

### OBO Flow vs Other Flows

| Feature | On-Behalf-Of | Authorization Code | Client Credentials | Implicit |
|---------|--------------|-------------------|-------------------|----------|
| User Identity Propagation | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Service Chain Support | ✅ Yes | ❌ No | ❌ No | ❌ No |
| User Context | ✅ Maintained | Initial only | ❌ None | Initial only |
| Use Case | Middle-tier APIs | Initial auth | App-only | Legacy SPAs |
| Delegation Through Chain | ✅ Yes | ❌ No | ❌ No | ❌ No |

### OBO Flow Requirements

1. **Delegated permissions** must be configured on the middle-tier API
2. **API permissions** must include the downstream API (e.g., Microsoft Graph)
3. **Consent** must be granted for all required permissions
4. **Access token** from the client must be valid and contain user information
5. **Client secret or certificate** for the middle-tier app registration

### OBO Flow Security Considerations

- **Token validation**: Always validate incoming tokens before using OBO
- **Scope limitation**: Request only necessary scopes for downstream calls
- **Token caching**: Cache OBO tokens to reduce authentication overhead
- **Error handling**: Handle consent and permission errors gracefully
- **Token lifetime**: Be aware of token expiration in the chain

## Continuous Access Evaluation (CAE)

### Question 3: Enabling CAE in MSAL.NET

**Scenario**: You are developing a web application that accesses Microsoft Graph API. You need to implement Continuous Access Evaluation (CAE) to ensure tokens are revoked immediately when critical events occur.

**Question**: Which code modification should you implement in your MSAL.NET application?

**Options**:
- **Configure the client capabilities by adding `WithClientCapabilities(new[] { "cp1" })` to the application builder** ✅ (Correct Answer)
- Add `WithClaims()` to every token acquisition call in the application
- Configure `WithAuthority()` to use the CAE-enabled endpoint
- Set `EnableContinuousAccessEvaluation = true` in the application configuration

**Solution**: Configure client capabilities with `WithClientCapabilities(new[] { "cp1" })`

### What is Continuous Access Evaluation?

Continuous Access Evaluation (CAE) is a security feature that enables near real-time token revocation when critical security events occur. Instead of waiting for tokens to expire naturally (typically 1 hour), CAE allows tokens to be revoked immediately when:

- A user account is disabled or deleted
- A user's password is changed or reset
- Multi-factor authentication is enabled for the user
- An administrator explicitly revokes all refresh tokens for a user
- High user risk is detected by Microsoft Entra ID Protection
- Network location changes (IP-based policies)

### How to Enable CAE in MSAL.NET

To enable CAE support in your MSAL.NET application, you must advertise client capabilities during application initialization:

```csharp
// Correct implementation - Enable CAE support
var app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithClientSecret(clientSecret)
    .WithAuthority(new Uri($"https://login.microsoftonline.com/{tenantId}"))
    .WithClientCapabilities(new[] { "cp1" })  // Enable CAE support
    .Build();
```

**For public client applications:**

```csharp
var app = PublicClientApplicationBuilder
    .Create(clientId)
    .WithAuthority(new Uri($"https://login.microsoftonline.com/{tenantId}"))
    .WithClientCapabilities(new[] { "cp1" })  // Enable CAE support
    .WithRedirectUri("http://localhost")
    .Build();
```

**Key Points**:
- The `"cp1"` capability signals that the client can handle claim challenges
- This must be set during application builder configuration
- Once configured, CAE-enabled APIs can issue claims challenges to the client

### Why Other CAE Options Are Incorrect

#### Add `WithClaims()` to every token acquisition call

**What it does**: `WithClaims()` is used to respond to claim challenges after they occur.

**Why it's incorrect**:
- ❌ Does not enable CAE support initially
- ❌ Should only be used when responding to a claims challenge from the API
- ❌ Not a proactive configuration, but a reactive response

**Correct usage**: Use `WithClaims()` only when handling a `MsalUiRequiredException` with claims:

```csharp
try
{
    var result = await app.AcquireTokenSilent(scopes, account).ExecuteAsync();
}
catch (MsalUiRequiredException ex) when (ex.Claims != null)
{
    // Respond to claims challenge
    var result = await app.AcquireTokenInteractive(scopes)
        .WithClaims(ex.Claims)  // Use claims from the exception
        .ExecuteAsync();
}
```

#### Configure `WithAuthority()` to use the CAE-enabled endpoint

**What it does**: `WithAuthority()` specifies the token issuing authority (e.g., Microsoft Entra ID endpoint).

**Why it's incorrect**:
- ❌ The authority endpoint remains the same for CAE-enabled applications
- ❌ There is no separate "CAE-enabled" endpoint
- ❌ CAE support is advertised through client capabilities, not endpoint changes

#### Set `EnableContinuousAccessEvaluation = true`

**Why it's incorrect**:
- ❌ There is **no** `EnableContinuousAccessEvaluation` property in MSAL.NET
- ❌ This property does not exist in any MSAL configuration
- ❌ CAE is enabled through client capabilities, not boolean settings

### Handling Claims Challenges

When a CAE-enabled API detects a critical event, it returns a `401 Unauthorized` response with a `WWW-Authenticate` header containing claims. Your application should:

1. **Detect the claims challenge** from the API response
2. **Extract the claims** from the WWW-Authenticate header
3. **Request a new token** using `WithClaims()` with the extracted claims

```csharp
public async Task<string> CallGraphApiWithCaeAsync()
{
    try
    {
        var token = await _app.AcquireTokenSilent(_scopes, _account).ExecuteAsync();
        return await CallApiAsync(token.AccessToken);
    }
    catch (HttpRequestException ex) when (IsClaimsChallenge(ex))
    {
        // Extract claims from the WWW-Authenticate header
        var claims = ExtractClaimsFromResponse(ex);
        
        // Acquire new token with claims challenge
        var token = await _app.AcquireTokenInteractive(_scopes)
            .WithClaims(claims)
            .ExecuteAsync();
            
        return await CallApiAsync(token.AccessToken);
    }
}
```

### CAE Critical Events

| Event | Description | Token Impact |
|-------|-------------|-------------|
| User Disabled | User account disabled in Entra ID | Immediate revocation |
| Password Changed | User changes or resets password | Immediate revocation |
| MFA Enabled | MFA enabled for the user | Re-authentication required |
| Refresh Token Revoked | Admin revokes all refresh tokens | Immediate revocation |
| High Risk Detected | Identity Protection detects risk | Immediate revocation |
| IP Policy Violation | User accesses from blocked location | Claims challenge issued |

### CAE Benefits

- **Enhanced Security**: Near real-time response to security events
- **Reduced Risk Window**: No waiting for 1-hour token expiration
- **Compliance**: Better alignment with zero-trust security models
- **Seamless Integration**: Works with existing MSAL authentication flows

## Comparison Table

| Feature | Delegated Permissions | Application Permissions |
|---------|----------------------|------------------------|
| User Present | ✅ Yes, required | ❌ No user present |
| Acts As | The signed-in user | The application itself |
| Use Case | Web apps, mobile apps | Background services, daemons |
| Consent | User or admin | Admin only |
| Access Scope | Limited to user's permissions | Broad access based on app permissions |
| Token Type | User + app context | App-only context |

## Troubleshooting

### Common Issues

1. **"Insufficient privileges" error**
   - Verify delegated permissions are granted
   - Check if admin consent is required
   - Ensure user has necessary permissions in Entra ID

2. **Token acquisition fails**
   - Verify client ID and tenant ID
   - Check redirect URI configuration
   - Ensure correct authority URL

3. **Consent not appearing**
   - Clear browser cache and cookies
   - Check if admin consent was already granted
   - Verify app registration is not disabled

## References

- [Microsoft Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)
- [Access user photo information by using Microsoft Graph](https://learn.microsoft.com/en-us/training/modules/microsoft-graph/)
- [Delegated vs Application permissions](https://learn.microsoft.com/en-us/graph/auth/auth-concepts)
- [MSAL authentication flows](https://learn.microsoft.com/en-us/azure/active-directory/develop/msal-authentication-flows)

## Summary

### For Direct Microsoft Graph Access (Question 1)

To enable an Azure App Service web app to retrieve Microsoft Entra ID signed-in user information via Microsoft Graph:

1. ✅ **Use delegated permissions** - This is the correct answer
2. Configure appropriate Microsoft Graph delegated permissions (e.g., User.Read)
3. Implement authentication using MSAL or similar library
4. Obtain user consent (or admin consent for organization)
5. Use the access token to call Microsoft Graph APIs on behalf of the signed-in user

### For Service Chain with User Identity (Question 2)

To delegate signed-in user identity through a request chain (App → API → Microsoft Graph):

1. ✅ **Use OAuth 2.0 On-Behalf-Of (OBO) flow** - This is the correct answer
2. Configure delegated permissions on the middle-tier API
3. Middle-tier API exchanges the incoming token for a new token using OBO
4. New token maintains user identity and permissions
5. Middle-tier API calls Microsoft Graph with the OBO token

**Key Distinction**:
- **Delegated permissions** = What permissions the app needs
- **OBO flow** = How to maintain user identity through service chains

Both approaches ensure apps can access user information while maintaining proper security boundaries and respecting the user's permissions within the organization.
