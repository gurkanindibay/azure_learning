---
type: System Design
title: "Authentication & Authorization — Key Takeaways"
description: "Eight security concepts that separate confused vocabulary debates from coherent auth architecture."
timestamp: 2026-06-17T00:00:00Z
---

# 36. Authentication & Authorization — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md)
> **Author**: Lets Learn Now
> **Purpose**: Extract reusable architectural patterns for identity, authentication, authorization, and secure service communication.

> **Also see**: [API & Network Design](api-network/api-network-design.md), [Reverse Proxy, LB & API Gateway](api-network/reverse-proxy-lb-gateway.md), [HSM & Cryptography](../../reference-dictionary/hsm-cryptography.md)
> **Dictionary**: [Authentication](../../reference-dictionary/security-iam.md#authentication), [Authorization](../../reference-dictionary/security-iam.md#authorization), [JWT](../../reference-dictionary/security-iam.md#jwt-json-web-token), [OAuth2](../../reference-dictionary/security-iam.md#oauth2), [mTLS](../../reference-dictionary/hsm-cryptography.md#mtls-mutual-tls), [Zero Trust](../../reference-dictionary/security-iam.md#zero-trust)
> **Taxonomy Reference**: §6.1 Security Foundations · §6.2 Identity Architecture · §6.3 Network Security

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [auth-01](#auth-01-identity-authentication-and-authorization-are-separate-layers) | Engineers conflate identity, authentication, and authorization | Model them as three distinct security layers |
| [auth-02](#auth-02-server-sessions-dont-scale-to-microservices) | Stateful sessions become a bottleneck in distributed systems | Stateless tokens carry identity claims |
| [auth-03](#auth-03-jwt-is-signed-not-encrypted) | Treating JWT as encrypted secrets leaks data or invites misuse | JWT is a signed, tamper-evident container with short expiry |
| [auth-04](#auth-04-oauth2-is-delegated-authorization-not-authentication) | Using OAuth2 as a direct authentication mechanism | OIDC adds the identity layer on top of OAuth2 delegation |
| [auth-05](#auth-05-service-to-service-communication-needs-mtls) | User tokens alone cannot authenticate microservices to each other | Mutual TLS verifies both peers via certificates |
| [auth-06](#auth-06-perimeter-security-fails-inside-microservices) | Assuming internal network traffic is trustworthy | Zero Trust verifies every request, service, and action |
| [auth-07](#auth-07-external-and-internal-apis-need-different-security-models) | Applying one auth model to all APIs | External APIs use OAuth2+JWT+gateway; internal APIs use mTLS+service identity |

---

## auth-01: Identity, Authentication, and Authorization Are Separate Layers

> **Source**: [Identity vs Authentication vs Authorization](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#identity-vs-authentication-vs-authorization)

| | |
|:---|:---|
| **Problem** | Architecture discussions mix up "who you are," "prove it," and "what you can do," leading to misplaced controls. |
| **Key Concept** | Treat **identity**, **authentication**, and **authorization** as three independent layers. |

**Strategy**: Design each layer separately. Identity establishes the subject (`user = xyz`). Authentication proves that claim (password, OTP, biometrics). Authorization evaluates permissions (`can_transfer_money`). Keep the layers explicit in code and in diagrams so controls are applied at the right boundary.

**Tradeoff**: A layered model adds more components and more round-trips than a naive "logged-in = can-do-anything" check, but it prevents authorization logic from leaking into authentication code and enables fine-grained policy evolution.

---

## auth-02: Server Sessions Don’t Scale to Microservices

> **Source**: [The Original Way: Sessions](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#the-original-way:-sessions)

| | |
|:---|:---|
| **Problem** | Server-side sessions require shared session storage, sticky sessions, and cross-service lookups that break down in microservice and mobile/API environments. |
| **Key Concept** | Replace session lookups with **stateless tokens** that carry identity. |

**Strategy**: After login, issue a signed token (e.g., JWT) that contains the user identifier and claims. Each service validates the token locally using a shared secret or public key instead of calling a session store. This removes the need for sticky load balancing and central session state.

**Tradeoff**: Stateless tokens lose the instant revocation semantics of server sessions. To compensate, keep expiry short and pair tokens with a refresh-token flow or a small revocation/blocklist service for high-risk operations.

---

## auth-03: JWT Is Signed, Not Encrypted

> **Source**: [JWT (The Most Misunderstood Thing)](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#jwt-the-most-misunderstood-thing)

| | |
|:---|:---|
| **Problem** | Teams treat JWT as confidential data and store sensitive fields in the payload, or assume decoding requires a secret. |
| **Key Concept** | JWT is **signed** and tamper-evident, not encrypted; anyone can read it, but no one can modify it without invalidating the signature. |

**Strategy**: Use JWT only for identity claims and non-sensitive permissions. Validate the signature on every service that accepts it. Set a short expiry (`exp`) so a leaked token has a narrow blast radius. If the payload must remain confidential, encrypt it separately (e.g., JWE) or keep sensitive data server-side and reference it by ID.

**Tradeoff**: Short-lived tokens increase refresh traffic and complicate long-lived background jobs, but they limit the window of abuse and reduce the need for a global token revocation system.

---

## auth-04: OAuth2 Is Delegated Authorization, Not Authentication

> **Source**: [OAuth2 (Another Misunderstood Concept)](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#oauth2-another-misunderstood-concept)

| | |
|:---|:---|
| **Problem** | "Login with Google" is often described as "OAuth2 authentication," but OAuth2 itself only delegates access authorization. |
| **Key Concept** | Use **OpenID Connect (OIDC)** on top of OAuth2 when you need authenticated identity. |

**Strategy**: Let the identity provider authenticate the user and return an ID token (OIDC) plus an access token (OAuth2). The ID token proves who the user is; the access token proves what the client is allowed to access on the resource server. Keep the roles distinct: Resource Owner = user, Client = application, Authorization Server = identity provider, Resource Server = API.

**Tradeoff**: Delegation removes the need for your application to handle passwords, but it creates a hard dependency on the identity provider's availability and requires careful token scope design to avoid over-permissioning.

---

## auth-05: Service-to-Service Communication Needs mTLS

> **Source**: [mTLS (Critical for Microservices)](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#mtls-critical-for-microservices)

| | |
|:---|:---|
| **Problem** | A valid user token proves who the user is, but it does not prove that the calling microservice itself is legitimate. |
| **Key Concept** | **Mutual TLS (mTLS)** authenticates both sides of an internal connection with certificates. |

**Strategy**: Issue short-lived certificates to every service and enforce mTLS for internal traffic. Both `payment-service` and `account-service` present and validate each other's certificates. This ensures that even if an attacker breaches the network perimeter, unauthorized services cannot call protected internal APIs.

**Tradeoff**: Certificate provisioning, rotation, and revocation add significant operational complexity. A service mesh (Istio, Linkerd) can automate this, but it introduces another control plane to operate.

---

## auth-06: Perimeter Security Fails Inside Microservices

> **Source**: [Zero Trust Architecture](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#zero-trust-architecture)

| | |
|:---|:---|
| **Problem** | Legacy architectures assume anything inside the corporate network is trusted, so a single breach grants lateral movement. |
| **Key Concept** | **Zero Trust** means "trust nothing, verify everything." |

**Strategy**: Authenticate every request, authenticate every service, authorize every action, and encrypt all communication. Apply the same skepticism to internal service calls as to external user calls. Combine user-token validation at the edge (API Gateway) with mTLS and service-level authorization inside the cluster.

**Tradeoff**: Pervasive verification adds latency, certificate management, and policy enforcement overhead. However, it shrinks the blast radius of a compromise because an attacker must defeat multiple controls to move laterally.

---

## auth-07: External and Internal APIs Need Different Security Models

> **Source**: [Internal vs External API Security](../../articles/security/If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again.md#internal-vs-external-api-security)

| | |
|:---|:---|
| **Problem** | Applying the same auth mechanism to public customer APIs and private microservice APIs creates either weak internal security or poor external UX. |
| **Key Concept** | Match the security model to the threat model and caller type. |

**Strategy**: For **external APIs**, use OAuth2 + JWT, an API Gateway for centralized validation, rate limiting, and a WAF. For **internal APIs**, use mTLS certificates, service identity, and optionally a service mesh. A call from `payment-service` to `ledger-service` should be authenticated by certificates, not by a user token.

**Tradeoff**: Maintaining two security stacks increases complexity and requires teams to understand two credential lifecycles, but it correctly separates user-centric authorization from service-centric identity.

---
