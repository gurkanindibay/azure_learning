# Microsoft Graph Delegated Permissions for Signed-In Users

## Overview

When an Azure App Service web app needs to retrieve Microsoft Entra ID signed-in user information using Microsoft Graph, it must use **delegated permissions**. This document explains the mechanism and the differences between various permission types.

## Question Context

**Scenario**: An Azure App Service web app (app1) registered in Microsoft Entra ID needs to retrieve signed-in user information using Microsoft Graph.

**Solution**: Configure **delegated permissions**

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

To enable an Azure App Service web app to retrieve Microsoft Entra ID signed-in user information via Microsoft Graph:

1. ✅ **Use delegated permissions** - This is the correct answer
2. Configure appropriate Microsoft Graph delegated permissions (e.g., User.Read)
3. Implement authentication using MSAL or similar library
4. Obtain user consent (or admin consent for organization)
5. Use the access token to call Microsoft Graph APIs on behalf of the signed-in user

This approach ensures the app can access user information while maintaining proper security boundaries and respecting the user's permissions within the organization.
