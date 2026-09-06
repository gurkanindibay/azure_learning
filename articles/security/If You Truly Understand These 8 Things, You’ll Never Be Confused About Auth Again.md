---
type: Article
title: "If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again"
description: "A practical walkthrough of identity, authentication, authorization, sessions, JWT, OAuth2, TLS, mTLS, and Zero Trust as layers of one security model."
generated: { by: process:okf-migrate, at: 2026-06-17T00:00:00Z }
---

# If You Truly Understand These 8 Things, You’ll Never Be Confused About Auth Again

> **Author**: [[Lets Learn Now]]  
> **Original**: [Medium Article](https://blog.stackademic.com/if-you-truly-understand-these-8-things-youll-never-be-confused-about-auth-again-6206042f212f)  
> **Published**: 2026-03-28

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*K-xpKphdj0TBMV-oKW0Sqw.png)

Every few months I see the same confusion in architecture discussions.

Someone asks:

> *“Should we use JWT or OAuth?”  
> “Do we still need sessions?”  
> “Why do we need mTLS if we already have tokens?”  
> “What exactly does Zero Trust mean in microservices?”*

And suddenly the meeting becomes a **security vocabulary soup**.

JWT. OAuth. Sessions. Tokens. Certificates. API Gateway. mTLS. Zero Trust.

Everyone knows the terms.  
Very few engineers understand **how these actually fit together in real systems**.

After architecting banking systems, payment platforms, and large microservice ecosystems, I realized something:

The confusion happens because engineers learn these **as isolated concepts**, not as **one connected security story**.

Let’s start from the very beginning.

## Identity vs Authentication vs Authorization

Before anything else, understand this simple model.

Think about entering a **bank vault**.

️⃣ **Identity** → Who are you?  
️⃣ **Authentication** → Prove it  
️⃣ **Authorization** → What are you allowed to do?

Example:

Customer enters banking app.

Identity

```text
user = xyz
```

Authentication

```text
password / OTP / biometrics
```

Authorization

```text
can_view_balance
can_transfer_money
```

Most engineers mix **authentication and authorization**.

They are not the same.

Authentication = proving identity  
Authorization = deciding permissions

## The Original Way: Sessions

Old web systems used **server sessions**.

Flow:

1. User logs in
2. Server creates session
3. Session stored in server memory or Redis
4. Browser receives session cookie

Example:

```text
SESSION_ID = 9823749823
```

Next request:

```text
Cookie: SESSION_ID=9823749823
```

Server checks Redis:

```text
9823749823 → user=pavani
```

## Analogy

Hotel check-in.

Reception gives you a **room key card**.

Every time you enter your room:

You show the key card.

Hotel system knows:

```text
Room 203 → xyz
```

## Problem with Sessions

Sessions work well for **monoliths**.

But microservices changed everything.

Problems:

• session storage scaling  
• sticky sessions in load balancers  
• cross-service authentication  
• mobile / API clients

This led to **token-based authentication**.

## Tokens (The Foundation of Modern APIs)

A **token is simply a digital proof of authentication**.

Example:

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Instead of storing session in server:

The **token itself contains identity**.

This allows **stateless authentication**.

Meaning:

Servers don’t need session storage.

## Analogy

Airport boarding pass.

It already contains:

• passenger name  
• flight  
• seat number

The airport doesn’t need a database lookup every time.

## JWT (The Most Misunderstood Thing)

JWT = **JSON Web Token**

Structure:

```text
HEADER.PAYLOAD.SIGNATURE
```

Example payload:

```text
{
 "user": "xyz",
 "role": "customer",
 "exp": 1712200000
}
```

The signature ensures **the token wasn’t tampered with**.

Key point:

JWT is **not encryption**.

It is **signed data**.

Anyone can decode it.

But they **cannot modify it**.

## Analogy

A **signed government certificate**.

Everyone can read it.

But nobody can change it.

## OAuth2 (Another Misunderstood Concept)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*twtySRXo2_L0qQxwMu7V9w.png)

OAuth2 is **not authentication**.

OAuth2 is **delegated authorization**.

Example:

You click:

```text
Login with Google
```

Google authenticates you.

Then gives your app **permission to access data**.

OAuth roles:

```text
Resource Owner → user
Client → application
Authorization Server → Google
Resource Server → API
```

Flow simplified:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*gtgcUYtZn1pqwbWLm7T7MQ.png)

```text
User → Google login
Google → access token
App → API with token
```

OAuth tokens are often **JWT tokens**, but they don’t have to be.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*p2fSJyqrFV0xxa2SsfMdeg.png)

## Certificates and TLS

Now let’s move to **network security**.

TLS protects communication:

```text
Client → Server
```

Using **certificates**.

Certificate proves:

```text
This server is really bank.com
```

Without TLS:

Attackers could intercept requests.

This is called:

**Man-in-the-middle attack**

TLS prevents this.

## mTLS (Critical for Microservices)

TLS protects **client → server**.

But inside microservices we need:

**service ↔ service authentication**

This is **mutual TLS (mTLS)**.

Both sides present certificates.

Example:

```text
payment-service ↔ account-service
```

Both verify identity.

This ensures:

Only trusted services communicate.

## Analogy

Imagine a **secure military facility**.

Not only does the guard check visitors.

Visitors also verify the guard is real.

That’s **mutual authentication**.

## How Microservices Actually Communicate Securely

In real production architectures:

Multiple security layers exist.

Typical flow:

```text
User
 ↓
API Gateway
 ↓
Auth Service
 ↓
Microservices
```

Steps:

️⃣ User logs in  
️⃣ Auth service issues **JWT token**  
️⃣ Request goes through **API Gateway**  
️⃣ Gateway validates token  
️⃣ Gateway forwards request to services  
️⃣ Internal services communicate using **mTLS**

So we combine:

```text
JWT + OAuth + TLS + mTLS
```

## Zero Trust Architecture

Modern systems assume:

> *Nothing inside the network is automatically trusted.*

This is **Zero Trust**.

Principles:

️⃣ Verify every request  
️⃣ Authenticate every service  
️⃣ Authorize every action  
️⃣ Encrypt all communication

Even **internal microservices must authenticate**.

Old architecture:

```text
internal network = trusted
```

Modern architecture:

```text
trust nothing
verify everything
```

## Real Banking Architecture Example

Let’s see how a **banking transfer system** works.

Customer opens mobile app.

```text
Mobile App
   ↓
API Gateway
   ↓
Auth Service
   ↓
Account Service
   ↓
Payment Service
   ↓
Fraud Detection
```

Security layers:

User authentication

```text
OAuth2 + JWT
```

External communication

```text
TLS
```

Internal services

```text
mTLS
```

Authorization

```text
RBAC / ABAC
```

Example token payload:

```text
{
 "user": "xyz",
 "account_id": "992233",
 "permissions": ["TRANSFER","VIEW_BALANCE"]
}
```

When transferring money:

Payment service verifies:

```text
token valid?
permission present?
service certificate trusted?
```

## Internal vs External API Security

External APIs require:

• OAuth2  
• JWT  
• API Gateway  
• Rate limiting  
• WAF

Internal APIs use:

• mTLS  
• service identity  
• service mesh (Istio / Linkerd)

Example internal call:

```text
payment-service → ledger-service
```

Authenticated using:

```text
mTLS certificates
```

Not user tokens.

## A Simple Mental Model (Remember This)

Whenever you design security:

Think in **four layers**.

Layer 1 — Identity

```text
Who are you?
```

Layer 2 — Authentication

```text
password / token / certificate
```

Layer 3 — Authorization

```text
what can you do?
```

Layer 4 — Secure transport

```text
TLS / mTLS
```

Everything else is just implementation details.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*MSwV1s8K9s30MFiDh0DHNw.png)

## Final Advice From Architect

Most security discussions become confusing because engineers debate tools instead of **architecture**.

JWT vs OAuth.  
Sessions vs tokens.

These are **not competing ideas**.

They are **pieces of the same system**.

Real systems combine them:

```text
OAuth2 → user authorization
JWT → stateless identity
TLS → secure communication
mTLS → service identity
Zero Trust → architecture principle
```

Once you see them **as layers of a single security model**, everything suddenly makes sense.

And the next time someone asks:

> *“Should we use JWT or OAuth?”*

You’ll smile.

Because you’ll know that question doesn’t even make sense.

If you’re building **microservices in banking, fintech, or large enterprise systems**, mastering these concepts isn’t optional.

It’s the difference between:

A system that merely works.

And a system that **can actually be trusted**.
