# Authentication Methods

> **Taxonomy Reference**: §6 Security Architecture (see [architecture_taxonomy_reference.md](../../10-practicality-taxonomy/architecture_taxonomy_reference.md))

Authentication answers the question: **"Who is the user?"** It verifies that the entity requesting access is who they claim to be, before moving to **Authorization** (what they are allowed to do).

This document is the protocol and implementation deep dive. For identity operating model, governance, lifecycle, and architecture-level decisions, use [6.2 Identity Architecture](../6.2-identity-architecture.md).

For a quick comparison and method selection guide, use [Authentication Methods Overview](../authentication-methods-overview.md).

---

## Table of Contents

- [Overview](#overview)
- [1. Legacy & Basic Methods](#1-legacy--basic-methods)
  - [Basic Authentication](#basic-authentication)
  - [Digest Authentication](#digest-authentication)
- [2. API Key Authentication](#2-api-key-authentication)
- [3. Session-Based (Stateful) Authentication](#3-session-based-stateful-authentication)
- [4. Token-Based (Stateless) Authentication](#4-token-based-stateless-authentication)
  - [Bearer Authentication & JWT](#bearer-authentication--jwt)
  - [Access & Refresh Tokens](#access--refresh-tokens)
- [5. Authorization vs. Identity Protocols](#5-authorization-vs-identity-protocols)
  - [OAuth2](#oauth2-authorization-framework)
  - [OAuth 2.0 + PKCE](#oauth-20--pkce-public-client-mode)
  - [OpenID Connect (OIDC)](#openid-connect-oidc)
  - [OpenID Connect + PKCE](#openid-connect--pkce-recommended-for-spamobile)
- [6. Single Sign-On (SSO) & Identity Protocols](#6-single-sign-on-sso--identity-protocols)
  - [Why OIDC Enables SSO](#why-oidc-enables-sso)
- [Comparison Table](#comparison-table)

---

## Overview

Authentication is the first gate in access control. It establishes **identity** before any permission checks are performed. The method chosen affects security posture, scalability, and user experience.

<details>
<summary>Authentication flow overview</summary>

```
User Request → Authentication ("Who are you?") → Authorization ("What can you do?") → Resource
```

</details>

---

## 1. Legacy & Basic Methods

### Basic Authentication

- **Mechanism**: The client sends a Base64-encoded `username:password` string in the `Authorization` HTTP header.
- **Security**: Insecure on its own — Base64 is trivially reversible. Must always be paired with HTTPS/TLS.
- **Usage**: Generally avoided in modern production systems; occasionally used for internal tooling or simple scripts.

<details>
<summary>Example HTTP header</summary>

```http
Authorization: Basic dXNlcjpwYXNzd29yZA==
```

</details>

### Digest Authentication

- **Mechanism**: Similar to Basic Auth, but credentials are hashed with MD5 before transmission, avoiding plaintext exposure.
- **Status**: Largely obsolete. MD5 is considered cryptographically weak, and more secure alternatives now exist.

---

## 2. API Key Authentication

- **Mechanism**: A unique, random string (the API key) is issued to a client. The client includes it with every request, typically via an `X-API-Key` header or query parameter.
- **Storage**: Keys are stored in a database in hashed form, with associated permissions or scopes.

<details>
<summary>Example HTTP header</summary>

```http
X-API-Key: abc123xyz456
```

</details>

**Pros**:
- Simple to implement and consume
- Well-suited for machine-to-machine (M2M) communication

**Cons**:
- No built-in expiration — must be manually rotated
- If a key is leaked, any bearer can use it until revoked
- Not suitable for representing individual user identity

---

## 3. Session-Based (Stateful) Authentication

- **Mechanism**: The user submits credentials; the server creates a session record and stores it in a session store. A `Session ID` is returned to the client as an HTTP cookie and sent on every subsequent request.

**Session storage options**:

| Store | Characteristics |
|-------|----------------|
| **Redis** | Fast, supports TTL/expiration, ideal for production |
| **In-memory** | Simple; lost if the server process restarts |
| **Database** | Durable; higher latency than in-memory stores |

**Challenge**: The server must maintain session state. This introduces complexity when scaling horizontally across multiple servers — session affinity or a shared store (e.g., Redis) is required.

<details>
<summary>Session-based flow diagram</summary>

```
Client → POST /login → Server creates session → Session ID cookie → Client stores cookie
Client → GET /resource (cookie) → Server looks up session → Authorizes request
```

</details>

---

## 4. Token-Based (Stateless) Authentication

### Bearer Authentication & JWT

- **Bearer pattern**: Any party that possesses ("bears") the token is granted access — no additional identity proof is required.
- **JWT (JSON Web Token)**: A self-contained, signed token encoding claims such as user ID, email, roles, and expiration time.
- **Statelessness**: The server validates the token's cryptographic signature locally, without a database round-trip, making this approach horizontally scalable.

A JWT consists of three Base64URL-encoded parts separated by dots:

<details>
<summary>JWT structure example</summary>

```
header.payload.signature
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMSIsInJvbGUiOiJhZG1pbiJ9.<signature>
```

</details>

<details>
<summary>HTTP Authorization header</summary>

```http
Authorization: Bearer <jwt_token>
```

</details>

**JWT Bearer authentication flow**:

<details open>
<summary>View sequence diagram</summary>

```mermaid
sequenceDiagram
    participant C as Client
    participant AS as Auth Server
    participant API as API Server

    Note over C, AS: 1. Login Phase
    C->>AS: Login with credentials (POST /auth/login)
    Note right of AS: 2. Validate credentials
    Note right of AS: (Stateless - no db lookup needed)
    AS-->>C: 3. Return JWT token

    Note over C, API: 4. Resource Request Phase
    C->>API: Request with Bearer token (Authorization: Bearer eyJ...)
    Note right of API: 5. Verify token signature locally
```

</details>

**Real-world example: Web application accessing a backend REST API**

Consider a task management SPA (Single Page Application) calling a backend API:

```
Client: Web browser running React SPA
Auth Server: JWT issuer (custom auth service)
API Server: RESTful backend (Node.js, .NET, Java microservice)
```

**Step-by-step flow** (plain JWT Bearer — no separate access/refresh tokens):

1. **User logs in** via the web UI (e.g., clicks "Login with email/password")
   
   <details>
   <summary>View code: Login request</summary>
   
   ```javascript
   // Frontend: Send credentials
   POST https://auth.example.com/auth/login
   Content-Type: application/json
   
   {
     "username": "john@example.com",
     "password": "secure_password"
   }
   ```
   
   </details>

2. **Auth Server validates and returns JWT token (access_token)**
   
   <details>
   <summary>View code: Server response</summary>
   
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
     "token_type": "Bearer",
     "expires_in": 3600
   }
   ```
   
   </details>
   
   > **Note**: In plain JWT Bearer (no refresh token), this single token is called `"access_token"` because it grants access to resources. It's NOT paired with a `"refresh_token"` (that's the key difference from OAuth2 pattern shown in the next section).

3. **Frontend stores JWT token** (in memory — secure approach)
   
   <details>
   <summary>View code: Token storage</summary>
   
   ```javascript
   // Frontend: Store access_token in memory (NOT in localStorage)
   // ⚠️ Warning: localStorage is vulnerable to XSS attacks
   let accessToken = response.access_token;
   
   // Alternatively, use in a React hook:
   // const [accessToken, setAccessToken] = useState(response.access_token);
   
   // Note: Token will be lost on page refresh (single token approach has no refresh mechanism)
   ```
   
   </details>

4. **Frontend makes API requests** with the Bearer token
   
   <details>
   <summary>View code: API request</summary>
   
   ```javascript
   // Frontend: Request protected resource
   GET https://api.example.com/api/tasks
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   
   </details>

5. **API Server validates JWT locally**
   
   <details>
   <summary>View code: Token validation</summary>
   
   ```javascript
   // Backend: Verify JWT signature (no DB call needed)
   const decoded = jwt.verify(token, 'secret_key');
   // Extract user ID from decoded.sub (e.g., "john@example.com")
   // Check token expiration from decoded.iat + decoded.exp
   // Verify issuer (decoded.iss === "https://auth.example.com")
   ```
   
   </details>

6. **API returns protected resource**
   
   <details>
   <summary>View code: API response</summary>
   
   ```json
   {
     "tasks": [
       { "id": 1, "title": "Complete project", "completed": false },
       { "id": 2, "title": "Submit report", "completed": true }
     ]
   }
   ```
   
   </details>

**Key characteristics of plain JWT Bearer**:

- ✅ **Simple**: Just one token (JWT) — no separate access/refresh token concept
- ✅ **Stateless**: No session storage needed on API; only signature validation
- ✅ **Scalable**: Multiple API servers can all validate the same JWT without coordination
- ✅ **Fast**: Token validation is a cryptographic operation, not a database lookup
- ✅ **CORS-friendly**: Works across different domains (unlike cookies with strict same-origin policy)

> **Note**: This is **plain JWT Bearer authentication**. If you need token **refresh capability** (to maintain sessions without re-login), see the **"Access & Refresh Tokens"** section below, which describes the OAuth2 pattern with separate access and refresh tokens.

### Access & Refresh Tokens

| Token type | Lifetime | Purpose |
|------------|----------|---------|
| **Access token** | Short (15 min – 1 hour) | Sent with every API request |
| **Refresh token** | Long (days – weeks) | Used to obtain a new access token when the current one expires |

**OAuth2 Access & Refresh Token Flow**:

<details open>
<summary>View sequence diagram</summary>

```mermaid
sequenceDiagram
    participant C as Client
    participant AS as Auth Server
    participant API as API Server

    Note over C,AS: Step 1 – Initial Authentication
    C->>AS: POST /oauth/token<br/>(username + password)
    AS->>AS: Validate credentials
    AS-->>C: 200 OK<br/>{ access_token, refresh_token }
    Note right of C: Store access_token in memory<br/>Store refresh_token in httpOnly cookie

    Note over C,API: Step 2 – Access Protected Resource
    C->>API: GET /api/resource<br/>Authorization: Bearer <access_token>
    API->>API: Verify access_token signature
    API-->>C: 200 OK { data }

    Note over C,API: Step 3 – Access Token Expires
    C->>API: GET /api/resource<br/>Authorization: Bearer <expired_access_token>
    API->>API: Verify token → EXPIRED
    API-->>C: 401 Unauthorized<br/>{ "error": "token_expired" }

    Note over C,AS: Step 4 – Refresh Access Token
    C->>AS: POST /oauth/token/refresh<br/>{ refresh_token }
    AS->>AS: Validate refresh_token<br/>(DB lookup or signature check)
    AS-->>C: 200 OK<br/>{ access_token (new), refresh_token (optional new) }
    Note right of C: Update access_token in memory

    Note over C,API: Step 5 – Retry with New Token
    C->>API: GET /api/resource<br/>Authorization: Bearer <new_access_token>
    API->>API: Verify new token → VALID
    API-->>C: 200 OK { data }
```

</details>

**Key differences from plain JWT Bearer**:

| Aspect | Plain JWT Bearer | Access + Refresh Tokens |
|--------|------------------|------------------------|
| **Tokens issued** | 1 token (access_token only) | 2 tokens (access_token + refresh_token) |
| **Session persistence** | ❌ Lost on page refresh | ✅ Maintained via refresh_token |
| **Token lifetime** | Fixed (e.g., 1 hour) | Access: short / Refresh: long |
| **Revocation** | Hard (must wait for expiry) | Easier (revoke refresh_token) |
| **Security** | Higher exposure (long-lived token) | Lower exposure (short-lived access_token) |

---

**Real-world example: React frontend + .NET backend**

**Frontend (React) — Token management with automatic refresh**:

<details>
<summary>View code: authService.js (Token management)</summary>

```javascript
// authService.js - Token management
import axios from 'axios';

let accessToken = null;

const API_BASE = 'https://api.example.com';

// Login function
export async function login(username, password) {
  const response = await axios.post(`${API_BASE}/auth/login`, {
    username,
    password
  }, {
    withCredentials: true  // Important: Send/receive cookies
  });
  
  // Access token returned in response body
  accessToken = response.data.access_token;
  
  // Refresh token set in httpOnly cookie by server
  // Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict
  
  return response.data;
}

// API call with automatic token refresh on 401
export async function apiCall(endpoint, options = {}) {
  try {
    const response = await axios({
      url: `${API_BASE}${endpoint}`,
      headers: {
        'Authorization': `Bearer ${accessToken}`
      },
      withCredentials: true,  // Send refresh token cookie
      ...options
    });
    
    return response.data;
  } catch (error) {
    // Handle expired access token
    if (error.response?.status === 401) {
      console.log('Access token expired, refreshing...');
      
      // Attempt to refresh token
      try {
        const refreshResponse = await axios.post(
          `${API_BASE}/auth/refresh`,
          {},  // Empty body - refresh token sent via cookie
          { withCredentials: true }
        );
        
        // Update access token in memory
        accessToken = refreshResponse.data.access_token;
        
        // Retry original request with new token
        const retryResponse = await axios({
          url: `${API_BASE}${endpoint}`,
          headers: {
            'Authorization': `Bearer ${accessToken}`
          },
          withCredentials: true,
          ...options
        });
        
        return retryResponse.data;
      } catch (refreshError) {
        // Refresh failed - user must re-login
        console.error('Token refresh failed, redirecting to login');
        accessToken = null;
        window.location.href = '/login';
        throw refreshError;
      }
    }
    
    throw error;
  }
}

// Logout function
export async function logout() {
  await axios.post(`${API_BASE}/auth/logout`, {}, { 
    withCredentials: true 
  });
  
  accessToken = null;
  // Server clears refresh token cookie
}
```

</details>

<details>
<summary>View code: TaskList.jsx (React component)</summary>

```javascript
// TaskList.jsx - React component using the auth service
import React, { useState, useEffect } from 'react';
import { apiCall } from './authService';

function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchTasks() {
      try {
        // apiCall handles token refresh automatically
        const data = await apiCall('/api/tasks');
        setTasks(data.tasks);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchTasks();
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2>My Tasks</h2>
      <ul>
        {tasks.map(task => (
          <li key={task.id}>{task.title}</li>
        ))}
      </ul>
    </div>
  );
}

export default TaskList;
```

</details>

---

**Backend (.NET) — JWT generation and validation**:

<details>
<summary>View code: Program.cs (JWT configuration)</summary>

```csharp
// Program.cs - Configure JWT authentication
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Configure JWT authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
        };
    });

builder.Services.AddAuthorization();
builder.Services.AddControllers();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

</details>

<details>
<summary>View code: AuthController.cs (Login and refresh endpoints)</summary>

```csharp
// AuthController.cs - Login and refresh endpoints
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

[ApiController]
[Route("auth")]
public class AuthController : ControllerBase
{
    private readonly IConfiguration _config;
    
    public AuthController(IConfiguration config)
    {
        _config = config;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        // 1. Validate credentials (check database, hash password, etc.)
        if (!ValidateCredentials(request.Username, request.Password))
        {
            return Unauthorized(new { error = "Invalid credentials" });
        }

        // 2. Generate access token (short-lived: 15 mins)
        var accessToken = GenerateAccessToken(request.Username, expiresInMinutes: 15);

        // 3. Generate refresh token (long-lived: 7 days)
        var refreshToken = GenerateRefreshToken();

        // 4. Store refresh token in database with user ID and expiry
        StoreRefreshToken(request.Username, refreshToken, daysValid: 7);

        // 5. Set refresh token as httpOnly cookie
        Response.Cookies.Append("refresh_token", refreshToken, new CookieOptions
        {
            HttpOnly = true,      // JavaScript cannot access
            Secure = true,        // HTTPS only
            SameSite = SameSiteMode.Strict,  // CSRF protection
            MaxAge = TimeSpan.FromDays(7),
            Path = "/auth"        // Only sent to /auth endpoints
        });

        // 6. Return access token in response body
        return Ok(new 
        { 
            access_token = accessToken,
            token_type = "Bearer",
            expires_in = 900  // 15 minutes in seconds
        });
    }

    [HttpPost("refresh")]
    public IActionResult Refresh()
    {
        // 1. Get refresh token from cookie
        if (!Request.Cookies.TryGetValue("refresh_token", out var refreshToken))
        {
            return Unauthorized(new { error = "No refresh token provided" });
        }

        // 2. Validate refresh token (check database, expiry, etc.)
        var username = ValidateRefreshToken(refreshToken);
        if (username == null)
        {
            return Unauthorized(new { error = "Invalid or expired refresh token" });
        }

        // 3. Generate new access token
        var newAccessToken = GenerateAccessToken(username, expiresInMinutes: 15);

        // 4. Optionally rotate refresh token (generate new one)
        // var newRefreshToken = GenerateRefreshToken();
        // UpdateRefreshToken(username, refreshToken, newRefreshToken);

        // 5. Return new access token
        return Ok(new 
        { 
            access_token = newAccessToken,
            token_type = "Bearer",
            expires_in = 900
        });
    }

    [HttpPost("logout")]
    public IActionResult Logout()
    {
        if (Request.Cookies.TryGetValue("refresh_token", out var refreshToken))
        {
            // Remove refresh token from database
            RevokeRefreshToken(refreshToken);
        }

        // Clear the refresh token cookie
        Response.Cookies.Delete("refresh_token");

        return Ok(new { message = "Logged out successfully" });
    }

    private string GenerateAccessToken(string username, int expiresInMinutes)
    {
        var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:Key"]));
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(JwtRegisteredClaimNames.Sub, username),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new Claim(ClaimTypes.Name, username)
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(expiresInMinutes),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private string GenerateRefreshToken()
    {
        // Generate a secure random token
        var randomBytes = new byte[32];
        using var rng = System.Security.Cryptography.RandomNumberGenerator.Create();
        rng.GetBytes(randomBytes);
        return Convert.ToBase64String(randomBytes);
    }

    // Placeholder methods - implement with your database
    private bool ValidateCredentials(string username, string password) => true;
    private void StoreRefreshToken(string username, string token, int daysValid) { }
    private string ValidateRefreshToken(string token) => "user@example.com";
    private void RevokeRefreshToken(string token) { }
}

public record LoginRequest(string Username, string Password);
```

</details>

<details>
<summary>View code: TasksController.cs (Protected API endpoint)</summary>

```csharp
// TasksController.cs - Protected API endpoint
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

[ApiController]
[Route("api/tasks")]
[Authorize]  // Requires valid JWT access token
public class TasksController : ControllerBase
{
    [HttpGet]
    public IActionResult GetTasks()
    {
        // Extract user from JWT claims
        var username = User.FindFirst(ClaimTypes.Name)?.Value;

        // Fetch user's tasks from database
        var tasks = new[]
        {
            new { id = 1, title = "Complete project", completed = false },
            new { id = 2, title = "Submit report", completed = true }
        };

        return Ok(new { tasks });
    }
}
```

</details>

**Key implementation details**:

- ✅ **Access token** stored in memory (React state/variable) — short-lived (15 min)
- ✅ **Refresh token** stored in httpOnly cookie — long-lived (7 days), JavaScript cannot access
- ✅ **Automatic retry** on 401 — Frontend automatically refreshes token and retries request
- ✅ **Token rotation** (optional) — Generate new refresh token on each refresh for added security
- ✅ **Revocation** — Refresh tokens stored in DB and can be revoked on logout
- ✅ **HTTPS only** — Cookies marked as `Secure` for production environments

> ⚠️ **SECURITY DISCLAIMER: localStorage Storage Risk**
>
> **DO NOT store tokens in `localStorage`** — this is vulnerable to XSS (Cross-Site Scripting) attacks. Any malicious JavaScript on the page can read and steal your token.
>
> | Storage Method | Risk Level | Recommendation |
> |---|---|---|
> | `localStorage` | 🔴 **Critical** | ❌ **Avoid** — XSS attacker can steal token via `localStorage.getItem()` |
> | `sessionStorage` | 🔴 **Critical** | ❌ **Avoid** — Same XSS vulnerability as localStorage |
> | **HTTP-only Cookies** | 🟢 **Secure** | ✅ **Recommended** — Browser automatically sends; JavaScript cannot access |
> | **In-Memory (variable)** | 🟢 **Secure** | ✅ **Recommended** — Lost on page refresh (shorter exposure window) |
> | **Backend BFF** | 🟢 **Secure** | ✅ **Best** — Frontend never sees token; backend handles it |
>
> **Recommended storage strategy**:
> - **Refresh tokens**: Store in **HTTP-only, Secure, SameSite cookies** (set by server in `Set-Cookie` header)
> - **Access tokens**: Keep in **memory only** (JavaScript variable) or use Backend-For-Frontend pattern
> 
> <details>
> <summary>Example of secure refresh token cookie</summary>
>
> ```
> Set-Cookie: refresh_token=eyJ...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/api
> ```
> The browser automatically sends this cookie with requests; JavaScript cannot access it even with XSS.
>
> </details>

---

## 5. Authorization vs. Identity Protocols

### OAuth2 (Authorization Framework)

- **Purpose**: OAuth2 answers *"What can this application access on behalf of the user?"* — for example, allowing an app to read a user's Google Drive files.
- **Important distinction**: OAuth2 is **not** an authentication protocol. It issues an **Access Token** scoped to specific resources, but does not convey who the user is.

<details open>
<summary>OAuth2 sequence diagram</summary>

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client App
    participant AS as Authorization Server
    participant RS as Resource Server

    U->>C: Click "Connect Account"
    C->>AS: Redirect to /authorize?client_id&scope&redirect_uri
    U->>AS: Login + consent
    AS-->>C: Redirect back with authorization_code
    C->>AS: POST /oauth/token (code + client_secret)
    AS-->>C: access_token (+ optional refresh_token)
    C->>RS: GET /resource with Bearer access_token
    RS-->>C: Protected resource data
```

</details>

<details>
<summary>OAuth2 code example (Authorization Code flow)</summary>

```http
GET https://auth.example.com/authorize?
  response_type=code&
  client_id=web-client-123&
  redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback&
  scope=read:files%20write:files&
  state=abc123
```

```http
POST https://auth.example.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=SplxlOBeZQQYbYS6WxSbIA&
redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback&
client_id=web-client-123&
client_secret=top-secret
```

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def50200b7...",
  "scope": "read:files write:files"
}
```

```http
GET https://api.example.com/files
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

</details>

### OAuth 2.0 + PKCE (Public Client Mode)

- **Purpose**: Secure OAuth2 Authorization Code flow for public clients (SPA/mobile) that cannot safely store a client secret.
- **How PKCE helps**: A dynamic per-login secret (`code_verifier`) and derived hash (`code_challenge`) prevent authorization code interception attacks.

**At-a-glance difference (OAuth2 Code vs OAuth2 + PKCE):**

- **Standard OAuth2 Code**: Client proves identity at token endpoint using a **client secret**.
- **OAuth2 + PKCE**: Client proves request ownership using **code_challenge / code_verifier**.
- **Security gain**: Intercepted authorization codes are useless without the original verifier.
- **Best fit**: PKCE is recommended for **SPA/mobile/native apps** (public clients).

<details open>
<summary>OAuth2 + PKCE sequence diagram</summary>

```mermaid
sequenceDiagram
    participant U as User
    participant SPA as SPA / Mobile App
    participant AS as Authorization Server
    participant API as Resource API

  Note over SPA,AS: PKCE difference from standard OAuth2: client uses proof key instead of client_secret
  rect rgb(52, 73, 94)
  SPA->>SPA: [PKCE] Generate code_verifier (per login)
  SPA->>SPA: [PKCE] Derive code_challenge = BASE64URL(SHA256(code_verifier))
  end

    U->>SPA: Click Sign in
  SPA->>AS: GET /authorize?...&code_challenge=...&code_challenge_method=S256
    U->>AS: Authenticate + consent
    AS-->>SPA: Redirect with authorization_code

  rect rgb(52, 73, 94)
  SPA->>AS: [PKCE] POST /oauth/token (code + code_verifier)
  AS->>AS: [PKCE] Verify code_verifier matches stored challenge
  Note right of AS: Without matching verifier, token exchange is rejected
  end

    AS-->>SPA: access_token (+ optional refresh_token, id_token)
    SPA->>API: GET /resource with Bearer access_token
    API-->>SPA: Protected data
```

</details>

<details>
<summary>PKCE code example (JavaScript SPA)</summary>

```javascript
// 1) Create code_verifier + code_challenge
const random = crypto.getRandomValues(new Uint8Array(32));
const codeVerifier = btoa(String.fromCharCode(...random))
  .replace(/\+/g, '-')
  .replace(/\//g, '_')
  .replace(/=/g, '');

const digest = await crypto.subtle.digest(
  'SHA-256',
  new TextEncoder().encode(codeVerifier)
);

const codeChallenge = btoa(String.fromCharCode(...new Uint8Array(digest)))
  .replace(/\+/g, '-')
  .replace(/\//g, '_')
  .replace(/=/g, '');

sessionStorage.setItem('pkce_verifier', codeVerifier);

// 2) Redirect to authorize endpoint
const authUrl = new URL('https://login.example-idp.com/authorize');
authUrl.search = new URLSearchParams({
  client_id: 'spa-client-123',
  response_type: 'code',
  redirect_uri: 'https://app.example.com/callback',
  scope: 'openid profile api.read',
  code_challenge: codeChallenge,
  code_challenge_method: 'S256',
  state: 'state-123'
}).toString();

window.location.href = authUrl.toString();
```

```javascript
// 3) Exchange code for token on callback
const params = new URLSearchParams(window.location.search);
const code = params.get('code');
const verifier = sessionStorage.getItem('pkce_verifier');

const tokenResponse = await fetch('https://login.example-idp.com/oauth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: 'spa-client-123',
    code,
    redirect_uri: 'https://app.example.com/callback',
    code_verifier: verifier
  })
});

const tokens = await tokenResponse.json();
```

</details>

<details>
<summary>PKCE code example (.NET API token validation)</summary>

```csharp
using Microsoft.AspNetCore.Authentication.JwtBearer;

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = "https://login.example-idp.com";
        options.Audience = "api.read";
    });

builder.Services.AddAuthorization();
```

</details>

### OpenID Connect (OIDC)

- **Purpose**: An identity layer built on top of OAuth2 that adds authentication.
- **Mechanism**: In addition to an Access Token, OIDC returns an **ID Token** (a JWT) that contains verified identity claims (name, email, etc.), allowing the application to confirm who the user is.

#### OpenID Connect + PKCE (Recommended for SPA/Mobile)

- **Why this mode**: Public clients (SPA/mobile) should combine OIDC with PKCE because they cannot protect a client secret.
- **What is added**: `code_challenge` in the authorize request and `code_verifier` in token exchange.

<details open>
<summary>OIDC + PKCE sequence diagram</summary>

```mermaid
sequenceDiagram
  participant U as User
  participant APP as SPA / Mobile App
  participant OP as OpenID Provider
  participant API as Resource API

  APP->>APP: Generate code_verifier
  APP->>APP: Derive code_challenge (S256)
  U->>APP: Click Sign in
  APP->>OP: /authorize?scope=openid profile email&code_challenge=...
  U->>OP: Authenticate + consent
  OP-->>APP: Redirect with authorization_code
  APP->>OP: POST /oauth/token (code + code_verifier)
  OP->>OP: Validate verifier against stored challenge
  OP-->>APP: id_token + access_token (+ refresh_token)
  APP->>APP: Validate id_token (iss, aud, exp, nonce)
  APP->>API: Call API with access_token
  API-->>APP: Protected data
```

</details>

<details open>
<summary>OIDC sequence diagram</summary>

```mermaid
sequenceDiagram
    participant U as User
    participant RP as Relying Party (App)
    participant OP as OpenID Provider
    participant API as Resource API

    U->>RP: Click "Sign in"
    RP->>OP: Redirect /authorize?scope=openid profile email
    U->>OP: Authenticate + consent
    OP-->>RP: Redirect with authorization_code
    RP->>OP: POST /oauth/token (code exchange)
    OP-->>RP: id_token + access_token (+ refresh_token)
    RP->>RP: Validate id_token (iss, aud, exp, nonce)
    RP->>API: Call API with access_token
    API-->>RP: Protected API response
```

</details>

<details>
<summary>OIDC code example (ID token + user identity)</summary>

```http
GET https://login.example-idp.com/authorize?
  response_type=code&
  client_id=oidc-web-client&
  redirect_uri=https%3A%2F%2Fapp.example.com%2Fsignin-oidc&
  scope=openid%20profile%20email&
  nonce=n-0S6_WzA2Mj&
  state=af0ifjsldkj
```

```http
POST https://login.example-idp.com/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=Qcb0Orv1r9fF...&
redirect_uri=https%3A%2F%2Fapp.example.com%2Fsignin-oidc&
client_id=oidc-web-client&
client_secret=top-secret
```

```json
{
  "access_token": "eyJraWQiOiJrMSIsImFsZyI6IlJTMjU2In0...",
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImsxIn0.eyJzdWIiOiIyNDgiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJuYW1lIjoiSm9obiBEb2UiLCJpc3MiOiJodHRwczovL2xvZ2luLmV4YW1wbGUtaWRwLmNvbSIsImF1ZCI6Im9pZGMtd2ViLWNsaWVudCIsImV4cCI6MTcwMDAwMDAwMH0.signature",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

```json
{
  "sub": "248",
  "name": "John Doe",
  "email": "user@example.com",
  "iss": "https://login.example-idp.com",
  "aud": "oidc-web-client",
  "exp": 1700000000
}
```

</details>

<details>
<summary>OIDC implementation example (JavaScript + .NET)</summary>

```javascript
// JavaScript (oidc-client-ts): start OIDC login
import { UserManager } from 'oidc-client-ts';

const userManager = new UserManager({
  authority: 'https://login.example-idp.com',
  client_id: 'oidc-web-client',
  redirect_uri: 'https://app.example.com/callback',
  response_type: 'code',
  scope: 'openid profile email api.read'
});

await userManager.signinRedirect();
```

```csharp
// .NET API: validate JWTs issued by the OIDC provider
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = "https://login.example-idp.com";
        options.Audience = "api.read";
    });
```

</details>

| | OAuth2 | OIDC |
|--|--------|------|
| **Type** | Authorization framework | Authentication protocol (extends OAuth2) |
| **Token returned** | Access Token | Access Token + ID Token (JWT) |
| **Answers** | "What can the app do?" | "Who is the user?" |

---

## 6. Single Sign-On (SSO) & Identity Protocols

**Concept**: SSO is a user experience pattern that allows a single login to grant access to multiple services. For example, signing in to Google once provides access to Gmail, Drive, and YouTube without re-authenticating.

### Why OIDC Enables SSO

- **Centralized authentication**: Users authenticate once at an Identity Provider (IdP), not separately in each app.
- **Shared IdP session**: After first login, other applications can reuse the existing IdP session and skip re-login.
- **Standard trust model**: Multiple applications trust the same IdP-issued tokens (`id_token` and optionally `access_token`).
- **Consistent identity claims**: Apps receive a common identity (`sub`, `email`, `name`), enabling seamless cross-app user context.

**Protocols used for SSO**:

| Protocol | Format | Common use cases |
|----------|--------|-----------------|
| **SAML** (Security Assertion Markup Language) | XML | Enterprise and legacy systems (e.g., Salesforce, corporate portals) |
| **OpenID Connect** | JSON / JWT | Modern web and mobile applications (e.g., Google, Microsoft, GitHub) |

<details open>
<summary>SSO sequence diagram (Generic + OIDC-specific notes)</summary>

```mermaid
sequenceDiagram
  participant U as User
  participant AppA as Application A (SP)
  participant IdP as Identity Provider
  participant AppB as Application B (SP)

  Note over U,IdP: Generic: IdP / OIDC: OpenID Provider
  
  U->>AppA: Open App A
  AppA->>IdP: Redirect to login
  Note right of AppA: OIDC: /authorize with PKCE
  
  U->>IdP: Authenticate once
  
  IdP-->>AppA: SSO token/assertion
  Note right of IdP: Generic: SAML assertion or token<br/>OIDC: id_token + access_token (JWT)
  AppA-->>U: Access granted

  U->>AppB: Open App B
  AppB->>IdP: Redirect for authentication
  Note right of AppB: OIDC: /authorize (same IdP)
  
  IdP-->>AppB: Existing session + token/assertion
  Note right of IdP: IdP session reused - no re-login
  AppB-->>U: Access granted (no second login)
  
  Note over U,AppB: User authenticated once, accessed two apps
```

</details>

<details>
<summary>SSO code example (Frontend OIDC redirect)</summary>

```javascript
// React/JS: Start OIDC login with PKCE (SSO via external IdP)
const params = new URLSearchParams({
  client_id: 'web-client-123',
  response_type: 'code',
  scope: 'openid profile email',
  redirect_uri: 'https://app.example.com/callback',
  code_challenge: '<pkce_code_challenge>',
  code_challenge_method: 'S256',
  state: 'state-123',
  nonce: 'nonce-123'
});

window.location.href = `https://login.example-idp.com/authorize?${params.toString()}`;
```

</details>

<details>
<summary>SSO code example (.NET OIDC configuration)</summary>

```csharp
// ASP.NET Core: OIDC-based SSO setup
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;

var builder = WebApplication.CreateBuilder(args);

builder.Services
  .AddAuthentication(options =>
  {
    options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
  })
  .AddCookie()
  .AddOpenIdConnect(options =>
  {
    options.Authority = "https://login.example-idp.com";
    options.ClientId = "mvc-client-123";
    options.ClientSecret = "top-secret";
    options.ResponseType = "code";
    options.SaveTokens = true;
    options.Scope.Add("openid");
    options.Scope.Add("profile");
    options.Scope.Add("email");
  });

builder.Services.AddAuthorization();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.Run();
```

</details>

---

## Comparison Table

| Method | Stateful? | Best for | Key risk |
|--------|-----------|----------|----------|
| Basic Auth | No | Internal/dev tooling | Credentials exposed without HTTPS |
| Digest Auth | No | Legacy systems | MD5 is cryptographically weak |
| API Key | No | M2M / service integrations | No expiration; key leakage |
| Session-based | Yes | Traditional web apps | Scaling complexity; session fixation |
| JWT / Bearer | No | APIs, SPAs, microservices | Token theft; long-lived tokens hard to revoke |
| OAuth2 | No | Delegated authorization | Scope creep; misconfigured redirect URIs |
| OIDC | No | Federated identity / SSO | Token replay; weak ID Token validation |
| SAML / SSO | No | Enterprise SSO | XML complexity; misconfigured assertions |
