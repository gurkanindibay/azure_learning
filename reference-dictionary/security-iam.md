---
type: Reference
title: "Security, Identity & Access Management"
description: "**Authentication** — the process of proving that a claimed identity is genuine. It answers the question 'Are you really who you say you are?'"
timestamp: 2026-06-28T00:00:00Z
---

# Security, Identity & Access Management

> **Domain**: Authentication, authorization, identity protocols, access control models, and security architecture principles.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Authentication | [`#authentication`](#authentication) |
| Authorization | [`#authorization`](#authorization) |
| JWT (JSON Web Token) | [`#jwt-json-web-token`](#jwt-json-web-token) |
| OAuth2 | [`#oauth2`](#oauth2) |
| Zero Trust | [`#zero-trust`](#zero-trust) |
| RBAC (Role-Based Access Control) | [`#rbac-role-based-access-control`](#rbac-role-based-access-control) |
| ABAC (Attribute-Based Access Control) | [`#abac-attribute-based-access-control`](#abac-attribute-based-access-control) |
| Least Privilege | [`#least-privilege`](#least-privilege) |

---

## Authentication

The process of **proving that a claimed identity is genuine**. Authentication answers the question "Are you really who you say you are?" using credentials such as passwords, one-time codes, biometrics, or cryptographic tokens.

### Key Characteristics

- Verifies identity claims, not permissions
- Can be knowledge-based (password), possession-based (OTP device), or inherence-based (biometric)
- Produces an authentication artifact (session cookie, token, certificate) used on subsequent requests

### When to Use

- Every system that must distinguish one user or service from another
- Before any authorization decision is made

### When NOT to Use

- Do not use authentication alone to decide what actions are permitted
- Do not confuse authentication with identity proofing or account recovery

### Also see

- [Authorization](#authorization)
- [JWT](#jwt-json-web-token)
- [OAuth2](#oauth2)

---

## Authorization

The process of **deciding what an authenticated identity is allowed to do**. Authorization evaluates permissions, roles, policies, or attributes against a requested action and resource.

### Key Characteristics

- Operates only after authentication succeeds
- Can be coarse-grained (roles) or fine-grained (attributes, policies)
- Common models include RBAC, ABAC, and ACLs

### When to Use

- Enforcing least privilege
- Multi-tenant or multi-role systems

### When NOT to Use

- Before authentication is completed
- As a substitute for input validation or encryption

### Also see

- [Authentication](#authentication)
- [RBAC](#rbac-role-based-access-control)
- [ABAC](#abac-attribute-based-access-control)

---

## JWT (JSON Web Token)

A compact, URL-safe token format used to transmit **signed claims** between parties. A JWT consists of `header.payload.signature`.

### Key Characteristics

- **Signed, not encrypted** — anyone can read the payload; the signature prevents tampering
- Self-contained: services can validate locally with the right key
- Usually short-lived via the `exp` claim
- Common Bearer token format for stateless API authentication

### When to Use

- Stateless authentication in distributed systems
- Propagating identity and scope claims across microservices

### When NOT to Use

- As a confidential data container (use JWE or server-side storage instead)
- When instant revocation is required without a blocklist or short TTL
- For long-lived server-to-server trust (prefer mTLS)

### Also see

- [OAuth2](#oauth2)
- [mTLS](hsm-cryptography.md#mtls-mutual-tls)

---

## OAuth2

An **authorization framework** that enables a third-party application to obtain limited access to a user's resources without exposing the user's credentials. OAuth2 delegates authorization to a trusted authorization server.

### Key Characteristics

- Roles: Resource Owner, Client, Authorization Server, Resource Server
- Issues access tokens (often JWT) scoped to specific resources
- **Is not an authentication protocol by itself**

### When to Use

- "Login with..." integrations
- Delegating API access on behalf of users
- Third-party client authorization

### When NOT to Use

- As a direct authentication mechanism without OpenID Connect
- When the resource owner and client are the same trusted entity

### Also see

- [JWT](#jwt-json-web-token)
- [Authentication](#authentication)

---

## Zero Trust

A security architecture principle that assumes **no user, device, or service is trustworthy by default**, even inside the network perimeter. Every request must be authenticated, authorized, and encrypted.

### Key Characteristics

- "Trust nothing, verify everything"
- Per-request, per-service authentication and authorization
- Encrypt all communication (TLS/mTLS)
- Least-privilege access

### When to Use

- Microservices and cloud-native architectures
- Regulated environments
- When lateral movement risk must be minimized

### When NOT to Use

- As an excuse to ignore usability and latency budgets
- In simple monoliths where the operational overhead outweighs the threat model

### Also see

- [mTLS](hsm-cryptography.md#mtls-mutual-tls)
- [Authentication](#authentication)

---

## RBAC (Role-Based Access Control)

An authorization model where **permissions are assigned to roles**, and users inherit permissions by being assigned to roles.

### Key Characteristics

- Simplifies permission management for groups of users
- Roles reflect job functions
- Less flexible than ABAC for dynamic or context-aware policies

### When to Use

- Organizations with stable, well-defined roles
- When permission changes follow role changes

### When NOT to Use

- When access decisions need fine-grained context (time, location, device)
- In highly dynamic environments where roles proliferate

### Also see

- [ABAC](#abac-attribute-based-access-control)
- [Authorization](#authorization)

---

## ABAC (Attribute-Based Access Control)

An authorization model where access decisions are based on **attributes of the user, resource, action, and environment**.

### Key Characteristics

- Fine-grained and context-aware
- Policies are expressed as rules over attributes
- More expressive but more complex than RBAC

### When to Use

- Dynamic authorization requirements
- Policy based on context (time, location, data sensitivity)

### When NOT to Use

- When simple role-based access is sufficient
- When policy authoring and debugging overhead is unacceptable

### Also see

- [RBAC](#rbac-role-based-access-control)
- [Authorization](#authorization)

---

## Least Privilege

A security principle stating that every component, service, credential, or user should receive only the minimum permissions necessary to perform its function — nothing more.

### Key Characteristics
- Permissions are scoped to the exact actions required
- Applied at every layer: IAM roles, service accounts, method-level authorization, network ACLs
- Reduces blast radius when credentials are leaked or compromised

### When to Use
- All production systems, especially those handling sensitive data or money
- Microservices and agentic AI systems where tools can mutate state

### When NOT to Use
- As an excuse to block legitimate developer access without a just-in-time elevation path
- When the operational overhead of fine-grained permissions exceeds the risk (rare)

### Also see
- [Zero Trust](#zero-trust) · [RBAC](#rbac-role-based-access-control) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-01-least-privilege)

---

> **Convention**: Every term anchor follows `domain-file.md#lowercase-hyphenated-term`. Always link to the primary definition, never to a cross-reference.
