# Azure Identity & Principal Objects

This document provides a **complete, structured explanation** of Azure identity concepts:
- App Registration
- Service Principal
- Enterprise Application
- Managed Identity

It also includes:
- A relationship diagram
- Lifecycle comparison
- Decision trees

---

## Table of Contents

- [1. Core Concepts Overview](#1-core-concepts-overview)
- [2. Definitions](#2-definitions)
  - [App Registration](#app-registration)
  - [Service Principal](#service-principal)
  - [Enterprise Application](#enterprise-application)
  - [Managed Identity](#managed-identity)
- [3. Relationship Diagram](#3-relationship-diagram)
- [4. Lifecycle Comparison](#4-lifecycle-comparison)
- [5. Decision Tree: Choosing the Right Identity](#5-decision-tree-choosing-the-right-identity)
- [6. Access & Governance Decision Tree](#6-access--governance-decision-tree)
- [7. Rule of Thumb](#7-rule-of-thumb)
- [8. One-Line Mental Model](#8-one-line-mental-model)

---

## 1. Core Concepts Overview

| Concept | What it Really Is |
|------|-------------------|
| App Registration | Application definition (blueprint) |
| Service Principal | Tenant-specific identity object |
| Enterprise Application | Admin & portal view of a service principal |
| Managed Identity | Azure-managed service principal tied to a resource |

---

## 2. Definitions

### App Registration
Defines an application's authentication model and capabilities.
- Creates an **Application object**
- Defines secrets, certificates, scopes, and roles
- Global and tenant-independent

---

### Service Principal
The **actual identity** used by Entra ID at runtime.
- Exists per tenant
- Appears in tokens and logs
- Evaluated for permissions and RBAC

---

### Enterprise Application
A **management experience** over a Service Principal.
- User & group assignment
- Conditional Access
- SSO and sign-in monitoring

---

### Managed Identity
An Azure-created Service Principal.
- No visible credentials
- Automatic rotation
- Tied to Azure resource lifecycle

---

## 3. Relationship Diagram

```
                        App Registration
                      (Application Object)
                               |
                               | creates
                               v
                      Service Principal
                    (Tenant-specific Identity)
                               |
            ----------------------------------------
            |                                      |
            v                                      v
   Enterprise Application                   Managed Identity
 (Admin & Governance View)            (Azure-managed SP)
```

### Service Principal Creation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ┌───────────────────┐              ┌───────────────────┐                  │
│   │  App Registration │              │  Managed Identity │                  │
│   │  (Multi-tenant or │              │  (System/User     │                  │
│   │   Single-tenant)  │              │   Assigned)       │                  │
│   └─────────┬─────────┘              └─────────┬─────────┘                  │
│             │                                  │                            │
│             │ creates                          │ creates                    │
│             │                                  │ (automatically)            │
│             ▼                                  ▼                            │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                                                                 │       │
│   │                      SERVICE PRINCIPAL                          │       │
│   │              (The Actual Identity in Entra ID)                  │       │
│   │                                                                 │       │
│   │   • Used in token evaluation                                    │       │
│   │   • Appears in audit logs                                       │       │
│   │   • RBAC permissions assigned here                              │       │
│   │                                                                 │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                  │                                          │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │                                                                 │       │
│   │                   ENTERPRISE APPLICATION                        │       │
│   │              (Azure Portal View / UI Layer)                     │       │
│   │                                                                 │       │
│   │   • NOT a separate object - just a portal blade                 │       │
│   │   • Displays Service Principal properties                       │       │
│   │   • Manage user/group assignments                               │       │
│   │   • Configure Conditional Access                                │       │
│   │   • Monitor sign-in logs                                        │       │
│   │                                                                 │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight:** Both App Registrations and Managed Identities ultimately create a **Service Principal**. The Enterprise Application is simply the Azure Portal's administrative view of that Service Principal — it's not a separate identity object.


---

## 4. Lifecycle Comparison

### App Registration
```
Create App Registration
 → Create Service Principal
 → Create Secret / Certificate
 → Manually Rotate Credentials
 → App runs anywhere
```

### Managed Identity
```
Enable Managed Identity on Resource
 → Azure creates Service Principal
 → Azure manages credentials
 → Auto-rotation
 → Identity removed with resource
```

---

## 5. Decision Tree: Choosing the Right Identity

```
Does the workload run in Azure?
        |
       Yes
        |
Can it use Azure-native auth?
        |
       Yes ------------------> Use Managed Identity
        |
       No
        |
Use App Registration + Service Principal
```

```
Does the workload run outside Azure?
        |
       Yes
        |
Use App Registration + Service Principal
```

---

## 6. Access & Governance Decision Tree

```
Need to control user or group access?
        |
       Yes
        |
Configure Enterprise Application:
 - Assign users/groups
 - Assign app roles
 - Apply Conditional Access
 - Monitor sign-ins
```

---

## 7. Rule of Thumb

```
Runs in Azure        → Managed Identity
Runs outside Azure  → App Registration
Needs secrets       → App Registration
Needs zero secrets  → Managed Identity
Access control      → Enterprise Application
Token evaluation    → Service Principal
```

---

## 8. One-Line Mental Model

App Registration defines the app.  
Service Principal is the identity.  
Enterprise Application governs access.  
Managed Identity removes secrets.
