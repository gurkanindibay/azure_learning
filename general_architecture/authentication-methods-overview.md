# Authentication Methods Overview

## Table of Contents

- [Introduction](#introduction)
- [Authentication vs Authorization](#authentication-vs-authorization)
- [Authentication Methods Comparison](#authentication-methods-comparison)
- [1. Username and Password](#1-username-and-password)
- [2. Multi-Factor Authentication (MFA)](#2-multi-factor-authentication-mfa)
- [3. API Keys](#3-api-keys)
- [4. OAuth 2.0 and OpenID Connect (OIDC)](#4-oauth-20-and-openid-connect-oidc)
- [5. JWT (JSON Web Tokens)](#5-jwt-json-web-tokens)
- [6. SAML (Security Assertion Markup Language)](#6-saml-security-assertion-markup-language)
- [7. Client Certificate Authentication (mTLS)](#7-client-certificate-authentication-mtls)
- [8. Kerberos](#8-kerberos)
- [9. NTLM](#9-ntlm)
- [10. Biometric Authentication](#10-biometric-authentication)
- [11. SSH Keys](#11-ssh-keys)
- [12. Managed Identities (Azure)](#12-managed-identities-azure)
- [13. Service Principals](#13-service-principals)
- [14. Workload Identity Federation (OIDC)](#14-workload-identity-federation-oidc)
- [15. Shared Access Signatures (SAS)](#15-shared-access-signatures-sas)
- [16. Resource Tokens and Scope Maps (Fine-Grained Access)](#16-resource-tokens-and-scope-maps-fine-grained-access)
  - [Azure Container Registry (ACR) Scope Map Tokens](#azure-container-registry-acr-scope-map-tokens)
  - [Azure Cosmos DB Resource Tokens](#azure-cosmos-db-resource-tokens)
  - [Azure Event Hubs / Service Bus SAS Tokens](#azure-event-hubs--service-bus-sas-tokens)
  - [Azure IoT Hub Device Tokens](#azure-iot-hub-device-tokens)
  - [Azure Notification Hubs SAS Tokens](#azure-notification-hubs-sas-tokens)
  - [Azure SignalR Service Access Tokens](#azure-signalr-service-access-tokens)
- [Decision Matrix](#decision-matrix)
- [Security Comparison](#security-comparison)
- [References](#references)

---

## Introduction

Authentication is the process of verifying the identity of a user, system, or service. Choosing the right authentication method depends on the security requirements, user experience, and the type of system being secured.

---

## Authentication vs Authorization

| Concept | Definition | Example |
|---------|------------|---------|
| **Authentication** | Verifying WHO you are | Logging in with username/password |
| **Authorization** | Verifying WHAT you can do | Checking if user has admin role |

---

## Authentication Methods Comparison

| Method | Security Level | User Experience | Best For |
|--------|---------------|-----------------|----------|
| Username/Password | Low-Medium | Simple | Basic applications |
| MFA | High | Moderate friction | Enterprise, banking |
| API Keys | Low-Medium | Developer-friendly | Public APIs |
| OAuth 2.0/OIDC | High | Good (SSO) | Web/mobile apps |
| JWT | Medium-High | Stateless | APIs, microservices |
| SAML | High | Enterprise SSO | Enterprise federation |
| Client Certificates (mTLS) | Very High | Complex setup | B2B, IoT, Zero Trust |
| Kerberos | High | Transparent (SSO) | Windows domains |
| Managed Identities | Very High | No credentials | Azure cloud services |

---

## 1. Username and Password

### How It Works
User provides a username (or email) and a secret password that is verified against stored credentials.

### Viable Scenarios
- ✅ Simple web applications with low security requirements
- ✅ Internal tools with limited users
- ✅ Legacy systems
- ✅ As a first factor in MFA

### Not Recommended For
- ❌ High-security applications (alone)
- ❌ APIs (use tokens instead)
- ❌ Machine-to-machine communication

### Security Considerations
- Always hash passwords (bcrypt, Argon2)
- Implement rate limiting
- Use HTTPS
- Consider adding MFA

---

## 2. Multi-Factor Authentication (MFA)

### How It Works
Combines two or more factors:
- **Something you know** (password, PIN)
- **Something you have** (phone, hardware token)
- **Something you are** (fingerprint, face)

### Viable Scenarios
- ✅ Enterprise applications
- ✅ Banking and financial services
- ✅ Healthcare systems (HIPAA compliance)
- ✅ Admin/privileged access
- ✅ VPN access
- ✅ Cloud service portals (Azure, AWS, GCP)

### MFA Methods
| Method | Security | Convenience |
|--------|----------|-------------|
| SMS OTP | Medium | High |
| Authenticator App (TOTP) | High | High |
| Push Notification | High | Very High |
| Hardware Token (FIDO2) | Very High | Medium |
| Biometrics | High | Very High |

---

## 3. API Keys

### How It Works
A unique string identifier passed in request headers or query parameters to authenticate API calls.

```http
GET /api/data HTTP/1.1
Host: api.example.com
X-API-Key: abc123xyz789
```

### Viable Scenarios
- ✅ Public APIs with rate limiting
- ✅ Developer portals
- ✅ Third-party integrations
- ✅ Simple service-to-service calls
- ✅ Webhook authentication

### Not Recommended For
- ❌ User authentication
- ❌ High-security APIs
- ❌ When fine-grained permissions are needed

### Security Considerations
- Rotate keys regularly
- Use different keys per environment
- Never expose in client-side code
- Implement rate limiting per key

---

## 4. OAuth 2.0 and OpenID Connect (OIDC)

### How It Works

**OAuth 2.0** - Authorization framework for delegated access
**OpenID Connect** - Identity layer on top of OAuth 2.0 for authentication

```
┌─────────┐                              ┌─────────────────┐
│  User   │                              │ Authorization   │
│         │──── 1. Login Request ───────>│ Server (IdP)    │
│         │<─── 2. Auth Code ───────────│                 │
└─────────┘                              └─────────────────┘
     │                                          │
     │ 3. Auth Code                             │
     ▼                                          │
┌─────────┐                                     │
│  App    │──── 4. Exchange Code ──────────────>│
│         │<─── 5. Access Token + ID Token ─────│
└─────────┘                                     
```

### OAuth 2.0 Grant Types

| Grant Type | Use Case |
|------------|----------|
| Authorization Code | Web apps, mobile apps |
| Authorization Code + PKCE | SPAs, mobile apps (recommended) |
| Client Credentials | Machine-to-machine |
| Device Code | Devices with limited input |
| Refresh Token | Long-lived sessions |

### Viable Scenarios
- ✅ Web applications with social login
- ✅ Mobile applications
- ✅ Single Page Applications (SPAs)
- ✅ Single Sign-On (SSO)
- ✅ Third-party app authorization (e.g., "Login with Google")
- ✅ API authorization with scopes
- ✅ Microservices authentication

### Identity Providers
- Microsoft Entra ID (Azure AD)
- Google Identity
- Okta
- Auth0
- AWS Cognito
- Keycloak

---

## 5. JWT (JSON Web Tokens)

### How It Works
A compact, URL-safe token format containing claims (payload) that is digitally signed.

```
Header.Payload.Signature

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### JWT Structure
| Part | Contains |
|------|----------|
| Header | Algorithm, token type |
| Payload | Claims (user info, expiration) |
| Signature | Verification hash |

### Viable Scenarios
- ✅ Stateless API authentication
- ✅ Microservices communication
- ✅ Mobile app authentication
- ✅ Cross-domain authentication
- ✅ Information exchange between services

### Not Recommended For
- ❌ Session management requiring immediate revocation
- ❌ Storing sensitive data (tokens can be decoded)
- ❌ Long-lived tokens without refresh mechanism

### Security Considerations
- Use short expiration times
- Implement refresh tokens
- Validate all claims
- Use RS256 (asymmetric) for distributed systems

---

## 6. SAML (Security Assertion Markup Language)

### How It Works
XML-based standard for exchanging authentication and authorization data between identity providers (IdP) and service providers (SP).

```
┌─────────┐         ┌─────────────────┐         ┌─────────────────┐
│  User   │         │ Service Provider│         │ Identity Provider│
│         │─── 1. Access Resource ───>│         │     (IdP)        │
│         │         │                 │         │                  │
│         │<── 2. Redirect to IdP ────│         │                  │
│         │                           │         │                  │
│         │──────── 3. Login ─────────────────>│                  │
│         │<─────── 4. SAML Assertion ─────────│                  │
│         │                           │         │                  │
│         │─── 5. SAML Assertion ────>│         │                  │
│         │<── 6. Access Granted ─────│         │                  │
└─────────┘         └─────────────────┘         └─────────────────┘
```

### Viable Scenarios
- ✅ Enterprise Single Sign-On (SSO)
- ✅ Federation between organizations
- ✅ Legacy enterprise applications
- ✅ Government and education sectors
- ✅ B2B partner integrations

### SAML vs OAuth/OIDC

| Aspect | SAML | OAuth 2.0/OIDC |
|--------|------|----------------|
| Format | XML | JSON |
| Token Size | Large | Compact |
| Best For | Enterprise SSO | Web/Mobile apps |
| Complexity | High | Medium |
| Mobile Support | Poor | Excellent |

---

## 7. Client Certificate Authentication (mTLS)

### How It Works
Both client and server present certificates during TLS handshake for mutual authentication.

```
Client                          Server
  |                               |
  |-------- TLS Handshake ------->|
  |<---- Server Certificate ------|
  |<-- Request Client Cert -------|
  |----- Client Certificate ----->|
  |---- Encrypted Connection ---->|
```

### Viable Scenarios
- ✅ **B2B API Communication** - Secure partner integrations
- ✅ **IoT Device Authentication** - Devices authenticating to cloud
- ✅ **Zero Trust Architecture** - Every request authenticated
- ✅ **Financial Services** - High-security transactions
- ✅ **Healthcare** - HIPAA-compliant communications
- ✅ **Government Systems** - Classified/secure networks
- ✅ **Microservices** - Service mesh authentication (Istio, Linkerd)
- ✅ **VPN Authentication** - Certificate-based VPN access

### Not Recommended For
- ❌ Consumer-facing web applications
- ❌ Mobile apps (certificate management is complex)
- ❌ Scenarios requiring easy credential rotation

### Azure Implementation
In Azure App Service, client certificates are forwarded in the `X-ARR-ClientCert` header with Base64 encoding.

---

## 8. Kerberos

### How It Works
Network authentication protocol using tickets to prove identity, commonly used in Windows Active Directory environments.

```
┌─────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Client │         │      KDC        │         │    Service      │
│         │         │ (Key Distribution│         │                 │
│         │         │    Center)      │         │                 │
│         │         │                 │         │                 │
│         │─── 1. Request TGT ───────>│         │                 │
│         │<── 2. TGT ────────────────│         │                 │
│         │                           │         │                 │
│         │─── 3. Request Service ────>│         │                 │
│         │      Ticket (with TGT)    │         │                 │
│         │<── 4. Service Ticket ─────│         │                 │
│         │                           │         │                 │
│         │─── 5. Service Request ───────────────────────────────>│
│         │      (with Service Ticket)│         │                 │
└─────────┘         └─────────────────┘         └─────────────────┘
```

### Viable Scenarios
- ✅ Windows Active Directory environments
- ✅ On-premises enterprise applications
- ✅ SQL Server Windows Authentication
- ✅ File share access
- ✅ Internal web applications (IIS)
- ✅ Hadoop clusters

### Not Recommended For
- ❌ Internet-facing applications
- ❌ Cross-domain scenarios (without federation)
- ❌ Cloud-native applications

---

## 9. NTLM

### How It Works
Legacy Windows authentication protocol using challenge-response mechanism.

### Viable Scenarios
- ✅ Legacy Windows applications
- ✅ Fallback when Kerberos unavailable
- ✅ Workgroup environments (non-domain)

### Not Recommended For
- ❌ New applications (use Kerberos or modern auth)
- ❌ Internet-facing applications
- ❌ Cross-platform scenarios

**Note:** NTLM is considered legacy and should be replaced with Kerberos or modern authentication methods where possible.

---

## 10. Biometric Authentication

### How It Works
Uses unique biological characteristics for identity verification.

### Types
| Type | Example | Security |
|------|---------|----------|
| Fingerprint | Touch ID, Windows Hello | High |
| Facial Recognition | Face ID, Windows Hello | High |
| Iris Scan | Banking, Border Control | Very High |
| Voice Recognition | Phone banking | Medium |

### Viable Scenarios
- ✅ Mobile device unlock
- ✅ Passwordless authentication (FIDO2/WebAuthn)
- ✅ Physical access control
- ✅ Banking applications
- ✅ As a factor in MFA

### Security Considerations
- Biometrics cannot be changed if compromised
- Use as one factor in MFA, not alone
- Store biometric templates securely (on device preferred)

---

## 11. SSH Keys

### How It Works
Asymmetric key pair authentication - private key stays with user, public key on server.

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "user@example.com"

# Copy public key to server
ssh-copy-id user@server.example.com
```

### Viable Scenarios
- ✅ Server administration (Linux/Unix)
- ✅ Git repository access (GitHub, GitLab, Azure DevOps)
- ✅ CI/CD pipeline authentication
- ✅ SFTP file transfers
- ✅ Ansible/automation tools

### Not Recommended For
- ❌ End-user authentication
- ❌ Web application login
- ❌ Mobile applications

---

## 12. Managed Identities (Azure)

### How It Works
Azure automatically manages identity credentials for Azure resources - no secrets to manage.

### Types
| Type | Use Case |
|------|----------|
| **System-assigned** | Tied to single resource lifecycle |
| **User-assigned** | Shared across multiple resources |

### Viable Scenarios
- ✅ Azure VM accessing Azure Key Vault
- ✅ Azure Functions accessing Azure Storage
- ✅ App Service connecting to Azure SQL
- ✅ AKS pods accessing Azure resources
- ✅ Any Azure-to-Azure service communication

### Benefits
- No credentials in code or config
- Automatic credential rotation
- No secret management overhead
- Follows principle of least privilege

---

## 13. Service Principals

### How It Works
Application identity in Microsoft Entra ID (Azure AD) used for automated processes.

### Viable Scenarios
- ✅ CI/CD pipelines (GitHub Actions, Azure DevOps)
- ✅ Terraform/IaC deployments
- ✅ Multi-tenant SaaS applications
- ✅ On-premises apps accessing Azure resources
- ✅ Third-party integrations

### Service Principal vs Managed Identity

| Aspect | Service Principal | Managed Identity |
|--------|-------------------|------------------|
| Credential Management | Manual | Automatic |
| Where Used | Anywhere | Azure resources only |
| Secret Rotation | Manual | Automatic |
| Complexity | Higher | Lower |

---

## 14. Workload Identity Federation (OIDC)

### How It Works
**Workload Identity Federation** allows external workloads (like GitHub Actions, GitLab CI, Kubernetes, etc.) to authenticate to Azure **without storing secrets**. It uses **OpenID Connect (OIDC)** to exchange external identity tokens for Azure access tokens.

This is the **recommended approach** for CI/CD pipelines authenticating to Azure.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     Workload Identity Federation Flow                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐         │
│   │   GitHub        │      │   Microsoft     │      │    Azure        │         │
│   │   Actions       │      │   Entra ID      │      │    Resources    │         │
│   │   Workflow      │      │                 │      │                 │         │
│   └────────┬────────┘      └────────┬────────┘      └────────┬────────┘         │
│            │                        │                        │                   │
│   1. Workflow runs                  │                        │                   │
│   2. GitHub issues   ───────────────>                        │                   │
│      OIDC token                     │                        │                   │
│                                     │                        │                   │
│   3. Token sent to   ───────────────>                        │                   │
│      Microsoft Entra ID             │                        │                   │
│                                     │                        │                   │
│   4. Entra validates:               │                        │                   │
│      - Issuer (GitHub)              │                        │                   │
│      - Subject (repo/branch)        │                        │                   │
│      - Audience                     │                        │                   │
│                                     │                        │                   │
│   5. Azure access    <───────────────                        │                   │
│      token returned                 │                        │                   │
│                                     │                        │                   │
│   6. Access Azure    ───────────────────────────────────────>│                   │
│      resources                      │                        │                   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | Description |
|-----------|-------------|
| **Federated Identity Credential** | Trust configuration in Entra ID that specifies which external tokens to accept |
| **Issuer** | The external identity provider URL (e.g., `https://token.actions.githubusercontent.com`) |
| **Subject** | Identifier for the specific workload (e.g., `repo:org/repo:ref:refs/heads/main`) |
| **Audience** | Expected audience claim (default: `api://AzureADTokenExchange`) |

### Supported External Identity Providers

| Provider | Issuer URL | Use Case |
|----------|------------|----------|
| **GitHub Actions** | `https://token.actions.githubusercontent.com` | CI/CD pipelines |
| **GitLab CI** | `https://gitlab.com` | CI/CD pipelines |
| **Terraform Cloud** | `https://app.terraform.io` | IaC deployments |
| **Kubernetes** | Cluster OIDC issuer | AKS workload identity |
| **Google Cloud** | `https://accounts.google.com` | Cross-cloud workloads |
| **AWS** | STS regional endpoints | Cross-cloud workloads |

### Configuration Options

#### Option 1: With Microsoft Entra Application (Service Principal)

```bash
# 1. Create App Registration
az ad app create --display-name "GitHub-Actions-App"

# 2. Create Service Principal
az ad sp create --id <app-id>

# 3. Add Federated Credential
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "github-federation",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# 4. Assign Role
az role assignment create \
  --assignee <app-id> \
  --role Contributor \
  --scope /subscriptions/<subscription-id>
```

#### Option 2: With User-Assigned Managed Identity

```bash
# 1. Create User-Assigned Managed Identity
az identity create \
  --name github-actions-identity \
  --resource-group myResourceGroup

# 2. Add Federated Credential to the Managed Identity
az identity federated-credential create \
  --name github-federation \
  --identity-name github-actions-identity \
  --resource-group myResourceGroup \
  --issuer https://token.actions.githubusercontent.com \
  --subject repo:myorg/myrepo:ref:refs/heads/main \
  --audiences api://AzureADTokenExchange

# 3. Assign Role
az role assignment create \
  --assignee <managed-identity-client-id> \
  --role Contributor \
  --scope /subscriptions/<subscription-id>
```

### GitHub Actions Workflow Example

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Deploy to Azure
        run: |
          az webapp deploy --name myapp --src-path ./app.zip
```

**Note:** No `AZURE_CLIENT_SECRET` is needed! The authentication happens via OIDC token exchange.

### Subject Claim Patterns for GitHub Actions

| Scenario | Subject Pattern |
|----------|----------------|
| **Specific branch** | `repo:org/repo:ref:refs/heads/main` |
| **Any branch** | `repo:org/repo:ref:refs/heads/*` |
| **Pull requests** | `repo:org/repo:pull_request` |
| **Environment** | `repo:org/repo:environment:production` |
| **Tag** | `repo:org/repo:ref:refs/tags/v1.0` |

### Viable Scenarios
- ✅ **GitHub Actions** deploying to Azure (recommended over service principal secrets)
- ✅ **Azure DevOps pipelines** with workload identity federation
- ✅ **GitLab CI/CD** authenticating to Azure
- ✅ **Terraform Cloud** provisioning Azure infrastructure
- ✅ **AKS Workload Identity** for pods accessing Azure resources
- ✅ **Cross-cloud authentication** (GCP/AWS workloads accessing Azure)
- ✅ **Kubernetes clusters** (any OIDC-enabled cluster)

### Not Recommended For
- ❌ Interactive user authentication
- ❌ On-premises applications without OIDC support
- ❌ Legacy systems that can't issue OIDC tokens

### Workload Identity Federation vs Traditional Service Principal

| Aspect | Traditional Service Principal | Workload Identity Federation |
|--------|-------------------------------|-----------------------------|
| **Secret Storage** | Client secret in GitHub Secrets | No secrets needed |
| **Secret Rotation** | Manual rotation required | No rotation needed |
| **Security Risk** | Secret can be leaked/stolen | No secret to leak |
| **Audit** | Harder to trace | Clear subject claim tracking |
| **Setup Complexity** | Lower | Slightly higher initial setup |
| **Recommendation** | Legacy/fallback | **Preferred approach** |

### AKS Workload Identity

Azure Kubernetes Service supports workload identity for pod-level authentication:

```yaml
# Pod with workload identity
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: my-service-account  # Linked to managed identity
  containers:
    - name: my-app
      image: myregistry.azurecr.io/myapp:latest
```

```bash
# Create federated credential for AKS
az identity federated-credential create \
  --name aks-federation \
  --identity-name my-app-identity \
  --resource-group myResourceGroup \
  --issuer <aks-oidc-issuer-url> \
  --subject system:serviceaccount:my-namespace:my-service-account
```

---

## 15. Shared Access Signatures (SAS)

### How It Works
URI-based tokens that grant limited access to Azure Storage resources.

```
https://account.blob.core.windows.net/container/blob.txt
  ?sv=2021-06-08
  &st=2024-01-01T00:00:00Z
  &se=2024-01-02T00:00:00Z
  &sr=b
  &sp=r
  &sig=signature
```

### Types
| Type | Scope |
|------|-------|
| Account SAS | All services in storage account |
| Service SAS | Single storage service |
| User Delegation SAS | Blob storage (Entra ID backed) |

### Viable Scenarios
- ✅ Temporary file access for users
- ✅ Upload URLs for client applications
- ✅ Cross-organization file sharing
- ✅ Limiting access scope and duration

---

## 16. Resource Tokens and Scope Maps (Fine-Grained Access)

Many Azure services provide **resource-level tokens** that grant fine-grained access to specific resources rather than the entire service. This follows the **principle of least privilege**.

### Overview of Azure Services with Scope-Based Tokens

| Azure Service | Token Type | Scope Level | Use Case |
|--------------|------------|-------------|----------|
| **Container Registry** | Scope Map Tokens | Repository | CI/CD, external partners |
| **Cosmos DB** | Resource Tokens | Container/Document | Multi-tenant apps, user isolation |
| **Event Hubs** | SAS Tokens | Namespace/Event Hub/Consumer Group | Event producers/consumers |
| **Service Bus** | SAS Tokens | Namespace/Queue/Topic | Message senders/receivers |
| **IoT Hub** | Device SAS Tokens | Per device | IoT device authentication |
| **Notification Hubs** | SAS Tokens | Hub level | Push notification clients |
| **SignalR Service** | Access Tokens | Hub/User | Real-time messaging |
| **Storage** | SAS Tokens | Account/Container/Blob | File access |

---

### Azure Container Registry (ACR) Scope Map Tokens

Scope maps define granular permissions that are associated with tokens, providing fine-grained access control to specific repositories without granting access to the entire registry.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Container Registry                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│   │ Scope Map A │      │ Scope Map B │      │ Scope Map C │   │
│   │             │      │             │      │             │   │
│   │ repo1: pull │      │ repo2: push │      │ repo3: *    │   │
│   │ repo1: push │      │ repo2: pull │      │             │   │
│   └──────┬──────┘      └──────┬──────┘      └──────┬──────┘   │
│          │                    │                    │           │
│          ▼                    ▼                    ▼           │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐   │
│   │   Token 1   │      │   Token 2   │      │   Token 3   │   │
│   │  (CI/CD)    │      │  (Dev Team) │      │  (Admin)    │   │
│   └─────────────┘      └─────────────┘      └─────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Scope Map Components

| Component | Description |
|-----------|-------------|
| **Scope Map** | Named collection of repository permissions |
| **Token** | Authentication credential linked to a scope map |
| **Repository** | Target container image repository |
| **Actions** | Permissions: `content/read`, `content/write`, `content/delete`, `metadata/read`, `metadata/write` |

### ACR Scope Map Actions

| Action | Permission | Equivalent Docker Command |
|--------|------------|---------------------------|
| `content/read` | Pull images | `docker pull` |
| `content/write` | Push images | `docker push` |
| `content/delete` | Delete images | `az acr repository delete` |
| `metadata/read` | Read metadata/tags | `az acr repository show-tags` |
| `metadata/write` | Write metadata | Update manifest attributes |

### Creating Scope Maps and Tokens (Azure CLI)

```bash
# Create a scope map with specific permissions
az acr scope-map create \
  --name MyScopeMap \
  --registry myregistry \
  --repository myrepo content/read content/write \
  --repository shared-repo content/read

# Create a token associated with the scope map
az acr token create \
  --name MyToken \
  --registry myregistry \
  --scope-map MyScopeMap

# Generate passwords for the token
az acr token credential generate \
  --name MyToken \
  --registry myregistry \
  --password1
```

### Using Repository-Scoped Tokens

```bash
# Login with repository-scoped token
docker login myregistry.azurecr.io \
  --username MyToken \
  --password <token-password>

# Now only permitted operations work
docker pull myregistry.azurecr.io/myrepo:latest     # ✅ Works
docker push myregistry.azurecr.io/myrepo:latest     # ✅ Works
docker pull myregistry.azurecr.io/other-repo:latest # ❌ Access denied
```

### Viable Scenarios
- ✅ **CI/CD Pipelines** - Grant specific pipeline access to only the repositories it needs
- ✅ **External Partners** - Provide limited access to specific images without full registry access
- ✅ **Development Teams** - Different teams access different repositories
- ✅ **Microservices** - Each service pulls only its own images
- ✅ **Multi-tenant Applications** - Isolate tenant-specific container images
- ✅ **Automated Systems** - IoT devices or edge systems pulling specific images
- ✅ **Security Compliance** - Principle of least privilege access

### Not Recommended For
- ❌ Admin access (use Azure RBAC with Entra ID instead)
- ❌ Interactive user authentication (use `az acr login`)
- ❌ Short-lived access needs (tokens don't expire by default)

### Scope Maps vs Other ACR Authentication

| Method | Scope | Best For |
|--------|-------|----------|
| **Admin Account** | Full registry | Quick testing (not recommended for production) |
| **Azure RBAC** | Registry-level roles | User/service principal access |
| **Scope Map Tokens** | Repository-level | Fine-grained automated access |
| **Managed Identity** | Registry-level | Azure service-to-ACR |

### OAuth 2.0 Scopes (General Concept)

Beyond ACR, scope-based tokens are fundamental to OAuth 2.0:

```
# OAuth 2.0 scope request example
GET /authorize?
  response_type=code&
  client_id=myclient&
  scope=openid profile email api.read api.write&
  redirect_uri=https://myapp.com/callback
```

**Common OAuth Scopes:**

| Scope | Access Granted |
|-------|----------------|
| `openid` | User's identity (ID token) |
| `profile` | User's profile info |
| `email` | User's email address |
| `offline_access` | Refresh tokens |
| `api.read` | Read access to API |
| `api.write` | Write access to API |

### Security Considerations for ACR Tokens
- Rotate token passwords regularly
- Use separate tokens for different purposes
- Monitor token usage with diagnostic logs
- Disable unused tokens promptly
- Follow principle of least privilege

---

### Azure Cosmos DB Resource Tokens

Cosmos DB **Resource Tokens** provide fine-grained access control at the container, partition key, or document level. This is ideal for multi-tenant applications where each user should only access their own data.

#### How It Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Cosmos DB Account                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │
│   │   Database   │    │   Database   │    │   Database   │             │
│   └──────┬───────┘    └──────────────┘    └──────────────┘             │
│          │                                                               │
│   ┌──────┴───────┐                                                      │
│   │  Container   │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│   ┌──────┴─────────────────────────────────────┐                        │
│   │              Partition Keys                 │                        │
│   ├────────────┬────────────┬─────────────────┤                        │
│   │  User123   │  User456   │    User789      │                        │
│   │  (Token A) │  (Token B) │   (Token C)     │                        │
│   │    ↓       │     ↓      │      ↓          │                        │
│   │ Documents  │ Documents  │  Documents      │                        │
│   └────────────┴────────────┴─────────────────┘                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Resource Token Architecture

| Component | Description |
|-----------|-------------|
| **Master Key** | Full access to account (admin only, never expose to clients) |
| **User** | Identity entity in Cosmos DB (not Azure AD user) |
| **Permission** | Access rights linking User to a resource |
| **Resource Token** | Time-limited token derived from Permission |

#### Permission Modes

| Mode | Access Level |
|------|-------------|
| `PermissionMode.All` | Read, write, delete |
| `PermissionMode.Read` | Read only |

#### Creating Resource Tokens (C#)

```csharp
using Microsoft.Azure.Cosmos;

// This runs on your secure backend (never expose master key to clients)
public async Task<string> CreateResourceToken(string userId, string containerId)
{
    // Connect with master key (server-side only)
    var cosmosClient = new CosmosClient(endpoint, masterKey);
    var database = cosmosClient.GetDatabase("MyDatabase");
    
    // Create or get user
    User user = await database.CreateUserAsync(userId);
    
    // Create permission scoped to container and partition key
    PermissionProperties permissionProperties = new PermissionProperties(
        id: $"{userId}-permission",
        permissionMode: PermissionMode.All,
        container: database.GetContainer(containerId),
        resourcePartitionKey: new PartitionKey(userId)  // User can only access their partition
    );
    
    Permission permission = await user.CreatePermissionAsync(permissionProperties);
    
    // Return the resource token to the client
    return permission.Resource.Token;
}
```

#### Using Resource Tokens (Client-Side)

```csharp
// Client uses resource token (no master key exposed)
public async Task<List<Document>> GetUserDocuments(string resourceToken)
{
    var cosmosClient = new CosmosClient(endpoint, resourceToken);
    var container = cosmosClient.GetContainer("MyDatabase", "MyContainer");
    
    // User can only query their own partition
    var query = container.GetItemQueryIterator<Document>(
        "SELECT * FROM c"
    );
    
    var results = new List<Document>();
    while (query.HasMoreResults)
    {
        results.AddRange(await query.ReadNextAsync());
    }
    return results;
}
```

#### Viable Scenarios for Cosmos DB Resource Tokens
- ✅ **Multi-tenant SaaS applications** - Each tenant accesses only their data
- ✅ **Mobile applications** - Users access only their documents
- ✅ **Web applications with user isolation** - Per-user data access
- ✅ **Gaming leaderboards** - Players access their own scores
- ✅ **IoT scenarios** - Devices write to their own partition
- ✅ **Compliance requirements** - Strict data isolation

#### Resource Token Characteristics

| Property | Value |
|----------|-------|
| Default TTL | 1 hour |
| Max TTL | 5 hours |
| Renewable | Yes (server-side) |
| Revocable | Yes (delete permission) |

---

### Azure Event Hubs / Service Bus SAS Tokens

Both Event Hubs and Service Bus use **Shared Access Signature (SAS) tokens** with defined policies that specify permissions.

#### SAS Policy Permissions

| Permission | Event Hubs | Service Bus |
|------------|------------|-------------|
| **Send** | Publish events | Send messages |
| **Listen** | Consume events | Receive messages |
| **Manage** | Create/delete entities | Full control |

#### Creating SAS Tokens

```csharp
// Event Hubs SAS Token generation
using Azure.Messaging.EventHubs;

public string GenerateEventHubSasToken(
    string resourceUri,
    string keyName,
    string key,
    TimeSpan ttl)
{
    var expiry = DateTimeOffset.UtcNow.Add(ttl).ToUnixTimeSeconds();
    var stringToSign = $"{Uri.EscapeDataString(resourceUri)}\n{expiry}";
    
    using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(key));
    var signature = Convert.ToBase64String(hmac.ComputeHash(Encoding.UTF8.GetBytes(stringToSign)));
    
    return $"SharedAccessSignature sr={Uri.EscapeDataString(resourceUri)}" +
           $"&sig={Uri.EscapeDataString(signature)}&se={expiry}&skn={keyName}";
}
```

#### Scope Levels

| Level | Event Hubs | Service Bus |
|-------|------------|-------------|
| **Namespace** | All event hubs | All queues/topics |
| **Entity** | Single event hub | Single queue/topic |
| **Consumer Group** | Specific consumer group | Subscription |

#### Viable Scenarios
- ✅ Sending events from external systems
- ✅ Processing events in consumer applications
- ✅ Temporary access for third-party integrations
- ✅ IoT device telemetry ingestion

---

### Azure IoT Hub Device Tokens

IoT Hub uses **per-device SAS tokens** for authenticating individual IoT devices.

#### How It Works

```
┌──────────────┐         ┌─────────────────────────┐
│  IoT Device  │         │       IoT Hub           │
│              │         │                         │
│  Device ID:  │         │  Device Registry:       │
│  device-001  │────────>│  - device-001 (key)     │
│              │  SAS    │  - device-002 (key)     │
│  SAS Token   │  Token  │  - device-003 (key)     │
└──────────────┘         └─────────────────────────┘
```

#### Device Authentication Options

| Method | Description | Best For |
|--------|-------------|----------|
| **Symmetric Key** | Shared secret per device | Simple scenarios |
| **X.509 Certificate** | Certificate per device | High security |
| **X.509 CA** | CA-signed certificates | Enterprise/manufacturing |
| **TPM Attestation** | Hardware-based | Highest security |

#### Generating Device SAS Token

```python
# Python example for IoT device token generation
from base64 import b64encode, b64decode
from hmac import HMAC
from hashlib import sha256
from time import time
from urllib.parse import quote_plus

def generate_sas_token(uri, key, policy_name, expiry_in_seconds=3600):
    ttl = int(time() + expiry_in_seconds)
    sign_key = f"{quote_plus(uri)}\n{ttl}"
    signature = b64encode(
        HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest()
    ).decode('utf-8')
    
    return f"SharedAccessSignature sr={quote_plus(uri)}&sig={quote_plus(signature)}&se={ttl}&skn={policy_name}"
```

#### Viable Scenarios
- ✅ Individual device authentication
- ✅ Device provisioning at scale (with DPS)
- ✅ Per-device access control
- ✅ Device revocation without affecting others

---

### Azure Notification Hubs SAS Tokens

Notification Hubs uses SAS tokens with different access policies for sending push notifications.

#### Access Policies

| Policy | Permission | Use Case |
|--------|------------|----------|
| **DefaultListenSharedAccessSignature** | Listen | Mobile apps registering for notifications |
| **DefaultFullSharedAccessSignature** | Full | Backend sending notifications |
| **Custom policies** | Configurable | Specific scenarios |

#### Viable Scenarios
- ✅ Mobile app registration for push notifications
- ✅ Backend services sending notifications
- ✅ Segmented notification access

---

### Azure SignalR Service Access Tokens

SignalR Service uses JWT-based access tokens for real-time messaging authentication.

#### Token Structure

```csharp
// Negotiate endpoint returns access token
public class SignalRConnectionInfo
{
    public string Url { get; set; }        // SignalR endpoint
    public string AccessToken { get; set; } // JWT token with claims
}
```

#### Token Claims

| Claim | Description |
|-------|-------------|
| `aud` | SignalR service URL |
| `iat` | Issued at time |
| `exp` | Expiration time |
| `nameid` | User identifier |
| Custom claims | Group memberships, roles |

#### Generating SignalR Access Token (Azure Functions)

```csharp
[FunctionName("negotiate")]
public static SignalRConnectionInfo Negotiate(
    [HttpTrigger(AuthorizationLevel.Anonymous)] HttpRequest req,
    [SignalRConnectionInfo(
        HubName = "chat",
        UserId = "{headers.x-ms-client-principal-id}")] SignalRConnectionInfo connectionInfo)
{
    return connectionInfo;
}
```

#### Viable Scenarios
- ✅ Real-time chat applications
- ✅ Live dashboards and monitoring
- ✅ Collaborative editing
- ✅ Gaming leaderboards
- ✅ User-specific notifications

---

### Comparison of Azure Scope-Based Token Services

| Service | Token Type | Default TTL | Scope Granularity | Revocation |
|---------|------------|-------------|-------------------|------------|
| **ACR** | Scope Map Token | No expiry | Repository | Delete token |
| **Cosmos DB** | Resource Token | 1 hour | Container/Partition/Document | Delete permission |
| **Event Hubs** | SAS Token | Configurable | Namespace/Hub/Consumer Group | Regenerate key |
| **Service Bus** | SAS Token | Configurable | Namespace/Queue/Topic | Regenerate key |
| **IoT Hub** | Device SAS | Configurable | Per device | Remove device |
| **SignalR** | JWT | Configurable | Hub/User | Token expiry |
| **Storage** | SAS Token | Configurable | Account/Container/Blob | Regenerate key |

---

## Decision Matrix

### By Application Type

| Application Type | Recommended Methods |
|------------------|---------------------|
| Public Website | OAuth 2.0/OIDC, Username/Password + MFA |
| Enterprise Web App | SAML, OAuth 2.0/OIDC with corporate IdP |
| Mobile App | OAuth 2.0 + PKCE, Biometrics |
| SPA (Single Page App) | OAuth 2.0 + PKCE |
| REST API | OAuth 2.0, JWT, API Keys |
| B2B API | mTLS, OAuth 2.0 Client Credentials |
| Microservices | JWT, mTLS, Managed Identities |
| IoT Devices | Client Certificates, SAS tokens |
| CI/CD Pipelines (Azure) | **Workload Identity Federation (OIDC)**, Service Principals |
| CI/CD Pipelines (General) | SSH Keys, Service Accounts |
| Azure Services | Managed Identities |
| Container Registry | Scope Map Tokens, Managed Identities |
| AKS Pods | AKS Workload Identity, Managed Identities |

### By Security Requirement

| Security Level | Recommended Methods |
|----------------|---------------------|
| Basic | Username/Password, API Keys |
| Standard | OAuth 2.0/OIDC + MFA |
| High | mTLS, FIDO2, Hardware tokens |
| Critical | mTLS + MFA, Zero Trust architecture |

---

## Security Comparison

| Method | Credential Theft Risk | Replay Attack Risk | Scalability | Revocation Speed |
|--------|----------------------|-------------------|-------------|------------------|
| Password | High | Medium | High | Instant |
| API Key | High | High | High | Instant |
| OAuth/JWT | Low | Low (with short expiry) | Very High | Token expiry |
| SAML | Low | Low | High | Session-based |
| mTLS | Very Low | Very Low | Medium | Certificate revocation |
| Managed Identity | Very Low | Very Low | High | Instant |
| Workload Identity Federation | Very Low | Very Low | High | Instant (no secret) |
| Service Principal (with secret) | Medium | Medium | High | Instant |

---

## References

- [Microsoft Identity Platform Documentation](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Specification](https://openid.net/connect/)
- [SAML 2.0 Specification](http://docs.oasis-open.org/security/saml/v2.0/)
- [Azure Managed Identities](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
- [Workload Identity Federation](https://learn.microsoft.com/en-us/entra/workload-id/workload-identity-federation)
- [GitHub Actions OIDC with Azure](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
- [FIDO2/WebAuthn](https://fidoalliance.org/fido2/)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
