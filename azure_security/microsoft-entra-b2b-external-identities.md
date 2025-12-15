# Microsoft Entra B2B External Identities

## Overview

Microsoft Entra B2B (Business-to-Business) collaboration enables organizations to securely share applications and services with guest users from other organizations while maintaining control over corporate data. Guest users use their own work, school, or social identities to access resources in the inviting organization's tenant.

---

## Table of Contents

1. [What is Microsoft Entra B2B?](#what-is-microsoft-entra-b2b)
2. [Key Concepts](#key-concepts)
3. [Guest User vs Cloud-Only User](#guest-user-vs-cloud-only-user)
4. [B2B Collaboration Flow](#b2b-collaboration-flow)
5. [Azure RBAC for External Users](#azure-rbac-for-external-users)
6. [Alternative Approaches Comparison](#alternative-approaches-comparison)
7. [Security and Governance](#security-and-governance)
8. [Common Use Cases](#common-use-cases)
9. [Exam Scenarios](#exam-scenarios)
10. [Best Practices](#best-practices)

---

## What is Microsoft Entra B2B?

Microsoft Entra B2B collaboration is a feature within Microsoft Entra External ID that allows you to invite guest users to collaborate with your organization. With B2B collaboration, you can securely share your company's applications and services with external users while maintaining control over your own corporate data.

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Federated Identity** | External users authenticate using their home organization's credentials |
| **Guest Account** | A user object is created in the inviting tenant with `UserType = Guest` |
| **Existing Credentials** | Users don't need new passwords—they use their existing work or social credentials |
| **Governance** | Full conditional access, audit logging, and access reviews support |
| **RBAC Support** | Guest users can be assigned Azure RBAC roles just like internal users |

---

## Key Concepts

### Identity Types in Microsoft Entra ID

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Microsoft Entra ID User Types                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐     │
│  │     Member Users            │    │      Guest Users             │     │
│  │     (UserType = Member)     │    │      (UserType = Guest)      │     │
│  ├─────────────────────────────┤    ├─────────────────────────────┤     │
│  │                             │    │                              │     │
│  │  • Cloud-only users         │    │  • B2B collaboration users   │     │
│  │  • Synced from on-prem AD   │    │  • Invited external users    │     │
│  │  • Full directory access    │    │  • Limited directory access  │     │
│  │  • Organization employees   │    │  • Partners/contractors      │     │
│  │                             │    │                              │     │
│  └─────────────────────────────┘    └─────────────────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### B2B Guest User Identity Sources

| Identity Source | Description | Authentication |
|-----------------|-------------|----------------|
| **Microsoft Entra ID** | Another Entra tenant | Federated via Entra ID |
| **Microsoft Account** | Personal Microsoft account | Microsoft identity platform |
| **Email one-time passcode** | Any email address | OTP sent to email |
| **Google Federation** | Google accounts | Google identity provider |
| **SAML/WS-Fed IdP** | Custom identity provider | SAML 2.0 or WS-Federation |

---

## Guest User vs Cloud-Only User

Understanding the difference is critical for exam scenarios:

### Cloud-Only User
- Created directly in your Entra tenant
- User manages credentials (password) in your tenant
- Full member access to directory
- **User must remember new credentials**

### Guest User (B2B)
- Identity sourced from external organization
- User authenticates with their **existing credentials**
- Limited directory access by default
- **No new credentials required**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Authentication Comparison                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CLOUD-ONLY USER                    GUEST USER (B2B)                    │
│  ─────────────────                  ────────────────                    │
│                                                                          │
│  User: john@contoso.com             User: alice@fabrikam.com            │
│  Password: Managed in Contoso       Password: Managed in Fabrikam       │
│                                                                          │
│  ┌──────────────┐                   ┌──────────────┐                    │
│  │   Contoso    │                   │   Fabrikam   │                    │
│  │    Tenant    │                   │    Tenant    │                    │
│  │              │                   │              │                    │
│  │  john@       │                   │  alice@      │                    │
│  │  contoso.com │                   │  fabrikam.com│                    │
│  └──────┬───────┘                   └──────┬───────┘                    │
│         │                                  │                            │
│         │ Authenticates                    │ Authenticates              │
│         ▼                                  ▼                            │
│  ┌──────────────┐                   ┌──────────────┐                    │
│  │   Contoso    │                   │   Contoso    │                    │
│  │   Tenant     │                   │   Tenant     │                    │
│  │   (Member)   │                   │   (Guest)    │                    │
│  └──────────────┘                   └──────────────┘                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## B2B Collaboration Flow

### Invitation and Redemption Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    B2B Invitation Flow                                   │
└─────────────────────────────────────────────────────────────────────────┘

     CONTOSO (Inviting Tenant)                 FABRIKAM (Guest's Home Tenant)
     ─────────────────────────                 ─────────────────────────────
              │                                          │
              │ 1. Admin invites alice@fabrikam.com      │
              │────────────────────────────────────────▶ │
              │                                          │
              │ 2. Invitation email sent                 │
              │────────────────────────────────────────▶ │
              │                                          │
              │ 3. Alice clicks "Accept Invitation"      │
              │ ◀────────────────────────────────────────│
              │                                          │
              │ 4. Alice redirected to Fabrikam for auth │
              │                                   ────────│
              │                                          │
              │ 5. Fabrikam authenticates Alice          │
              │                                          │
              │ 6. Token returned to Contoso             │
              │ ◀────────────────────────────────────────│
              │                                          │
              │ 7. Guest account created in Contoso      │
              │    (UserType = Guest)                    │
              │                                          │
              │ 8. Alice can access Contoso resources    │
              │    using her Fabrikam credentials        │
              │                                          │
```

### Guest Account Properties

When a B2B guest is created:

| Property | Value |
|----------|-------|
| **UserType** | Guest |
| **UserPrincipalName** | alice_fabrikam.com#EXT#@contoso.onmicrosoft.com |
| **Mail** | alice@fabrikam.com |
| **Identity Issuer** | fabrikam.com (or other IdP) |

---

## Azure RBAC for External Users

### Assigning Azure Roles to Guest Users

Guest users can be assigned Azure RBAC roles exactly like member users. This enables external partners, contractors, or collaborators to manage Azure resources.

```
┌─────────────────────────────────────────────────────────────────────────┐
│           Azure RBAC Assignment for B2B Guest Users                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────┐         ┌─────────────────┐                       │
│   │   Contoso       │         │    Azure        │                       │
│   │   Entra Tenant  │         │    Subscription │                       │
│   │                 │         │                 │                       │
│   │  ┌───────────┐  │         │  ┌───────────┐  │                       │
│   │  │ Guest:    │  │  RBAC   │  │ Resource  │  │                       │
│   │  │ alice@    │──┼────────▶│  │ Group:    │  │                       │
│   │  │ fabrikam  │  │ Role:   │  │ "DevRG"   │  │                       │
│   │  │ .com      │  │Contributor  │           │  │                       │
│   │  └───────────┘  │         │  └───────────┘  │                       │
│   │                 │         │                 │                       │
│   └─────────────────┘         └─────────────────┘                       │
│                                                                          │
│   Alice authenticates with Fabrikam → Gets token → Accesses Azure       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Role Assignment Process

1. **Invite external user** as B2B guest to Contoso tenant
2. **Guest redeems invitation** and appears in Contoso directory
3. **Assign Azure RBAC role** to guest at appropriate scope (subscription, resource group, or resource)
4. **Guest accesses Azure** using their existing credentials

### Supported Role Assignment Scopes

| Scope | Example | Use Case |
|-------|---------|----------|
| **Management Group** | /providers/Microsoft.Management/managementGroups/mg1 | Enterprise-wide access |
| **Subscription** | /subscriptions/{subscription-id} | Full subscription access |
| **Resource Group** | /subscriptions/{sub}/resourceGroups/{rg} | Project-specific access |
| **Resource** | /subscriptions/{sub}/resourceGroups/{rg}/providers/{rp}/{type}/{name} | Single resource access |

---

## Alternative Approaches Comparison

When granting external users access to Azure resources, there are several options. Here's why B2B guest accounts are the recommended approach:

### Option 1: B2B Guest Accounts ✅ RECOMMENDED

| Aspect | Details |
|--------|---------|
| **How it works** | Invite external users as guests; they authenticate with their home org |
| **Credentials** | Users keep their existing credentials |
| **Governance** | Full conditional access, MFA, audit logging |
| **RBAC** | Full Azure RBAC support |
| **Best for** | Partner collaboration, external developers |

### Option 2: Cloud-Only Accounts ❌ NOT RECOMMENDED

| Aspect | Details |
|--------|---------|
| **How it works** | Create new user accounts in your tenant |
| **Credentials** | Users must manage new credentials |
| **Governance** | Full control but higher admin overhead |
| **Issue** | **Violates "use existing credentials" requirement** |
| **Best for** | Only when users have no external identity |

### Option 3: Forest Trust ❌ NOT APPLICABLE

| Aspect | Details |
|--------|---------|
| **How it works** | Trust relationship between AD DS forests |
| **Scope** | On-premises Active Directory only |
| **Issue** | **Does not apply to Azure RBAC or Entra ID** |
| **Best for** | On-premises resource access between forests |

### Option 4: Microsoft 365 Organization Relationship ❌ NOT APPLICABLE

| Aspect | Details |
|--------|---------|
| **How it works** | Sharing relationship between M365 tenants |
| **Scope** | Calendar free/busy, Teams collaboration |
| **Issue** | **Does not grant Azure RBAC permissions** |
| **Best for** | Microsoft 365 collaboration features only |

### Comparison Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│        Approach Comparison: External User Azure Access                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Requirement: External users need Azure RBAC roles                       │
│              + Must use existing credentials                             │
│                                                                          │
│  ┌────────────────────┬──────────────┬────────────────┐                 │
│  │ Approach           │ Azure RBAC   │ Existing Creds │                 │
│  ├────────────────────┼──────────────┼────────────────┤                 │
│  │ B2B Guest Accounts │     ✅       │      ✅        │  ← CORRECT     │
│  │ Cloud-Only Users   │     ✅       │      ❌        │                 │
│  │ Forest Trust       │     ❌       │      N/A       │                 │
│  │ M365 Org Relation  │     ❌       │      N/A       │                 │
│  └────────────────────┴──────────────┴────────────────┘                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Security and Governance

### Conditional Access for Guest Users

Guest users can be targeted with Conditional Access policies:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                Conditional Access for B2B Guests                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Policy: "Require MFA for Guest Users"                                   │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ Assignments:                                                     │    │
│  │   Users: Guest users                                            │    │
│  │   Cloud apps: All cloud apps (or specific apps)                 │    │
│  │                                                                  │    │
│  │ Conditions:                                                      │    │
│  │   Locations: Any location                                       │    │
│  │                                                                  │    │
│  │ Access controls:                                                 │    │
│  │   Grant: Require multi-factor authentication                    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Guest Access Reviews

Use Access Reviews to periodically validate guest user access:

- Identify stale guest accounts
- Verify continued business need
- Auto-remove access after review denial
- Audit trail for compliance

### Guest User Restrictions

Default guest user permissions can be configured:

| Setting | Options |
|---------|---------|
| **Guest user access restrictions** | Same as members / Limited / Most restrictive |
| **Guest invite restrictions** | Anyone / Members + specific roles / Admins only |
| **Enable guest self-service sign-up** | Yes / No |

---

## Common Use Cases

### Use Case 1: Partner Developer Access

**Scenario:** External developers from a partner company need to work on Azure resources in your subscription.

**Solution:**
1. Invite developers as B2B guests
2. Create a security group for partner developers
3. Assign RBAC role (e.g., Contributor) to the group at resource group scope
4. Developers authenticate with their company credentials

### Use Case 2: External Auditor Access

**Scenario:** External auditors need read-only access to review Azure configurations.

**Solution:**
1. Invite auditors as B2B guests
2. Assign Reader role at appropriate scope
3. Configure conditional access (require MFA, compliant device)
4. Set up access reviews for periodic validation

### Use Case 3: Joint Venture Collaboration

**Scenario:** Two companies forming a joint venture need shared access to Azure resources.

**Solution:**
1. Each company invites the other's users as B2B guests
2. Create cross-tenant security groups
3. Assign RBAC roles based on job function
4. Implement cross-tenant access settings for enhanced security

---

## Identity Governance and B2B

### Can Entitlement Management Be Used?

**Yes!** Microsoft Entra Entitlement Management (part of Identity Governance) can be used to automate B2B guest provisioning and Azure RBAC assignment. However, it's important to understand the relationship:

```
┌─────────────────────────────────────────────────────────────────────────┐
│         B2B Guest Accounts vs Entitlement Management                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  B2B Guest Accounts = FOUNDATIONAL REQUIREMENT                          │
│  ─────────────────────────────────────────────────────────────          │
│  • Must exist for external users to access Azure resources              │
│  • Can be created manually or through automation                        │
│  • Required regardless of how invitation is triggered                   │
│                                                                          │
│  Entitlement Management = AUTOMATION LAYER                              │
│  ─────────────────────────────────────────────────────────────          │
│  • Automates B2B guest invitation through access packages               │
│  • Provides self-service request portal for external users              │
│  • Adds approval workflows, time limits, and governance                 │
│  • Still creates B2B guest accounts under the hood                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Entitlement Management for External Users

Entitlement Management can create access packages that:

| Capability | How It Works |
|------------|--------------|
| **Auto-invite B2B guests** | When external user requests access, guest account is automatically created |
| **Include Azure roles** | Access packages can include Azure resource roles (Contributor, Reader, etc.) |
| **Approval workflows** | Require manager or resource owner approval |
| **Time-limited access** | Set expiration dates for access |
| **Access reviews** | Periodic review of who has access |
| **Connected organizations** | Pre-approve specific external organizations (like Fabrikam) |

### Using Entitlement Management for the Fabrikam Scenario

```
┌─────────────────────────────────────────────────────────────────────────┐
│        Entitlement Management Approach                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Contoso creates Connected Organization for Fabrikam                  │
│                                                                          │
│  2. Contoso creates Access Package:                                      │
│     ┌─────────────────────────────────────────────────────────────┐     │
│     │ Access Package: "Developer Resource Group Access"            │     │
│     │                                                              │     │
│     │ Resources included:                                          │     │
│     │   • Azure Role: Contributor on ResourceGroup "DevRG"         │     │
│     │                                                              │     │
│     │ Policies:                                                    │     │
│     │   • Who can request: Users from Fabrikam (connected org)     │     │
│     │   • Approval: Required (Contoso project manager)             │     │
│     │   • Duration: 6 months (or project duration)                 │     │
│     │   • Access review: Quarterly                                 │     │
│     └─────────────────────────────────────────────────────────────┘     │
│                                                                          │
│  3. Fabrikam developers request access via My Access portal              │
│                                                                          │
│  4. Upon approval:                                                       │
│     • B2B guest account auto-created in Contoso tenant                  │
│     • Contributor role auto-assigned to resource group                  │
│     • Access automatically expires after defined period                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why "Guest Accounts" Is the Exam Answer (Not Entitlement Management)

For the specific exam question, the answer is "create guest accounts" rather than "use Entitlement Management" because:

| Factor | Explanation |
|--------|-------------|
| **Question focus** | Asks what's needed to **enable** role assignment to external users |
| **Fundamental requirement** | Guest accounts are the foundational prerequisite |
| **Entitlement Management** | Is an automation/governance layer, not the core enabler |
| **Answer precision** | The question doesn't mention self-service, automation, or governance |

**Key Insight:** Entitlement Management **creates** B2B guest accounts as part of its workflow. The guest account is still the underlying mechanism that enables Azure RBAC assignment.

### When to Choose Each Approach

| Scenario | Best Approach |
|----------|---------------|
| "External users need Azure RBAC access" (simple) | B2B Guest Accounts |
| "External users should request access themselves" | Entitlement Management |
| "Need approval workflow for external access" | Entitlement Management |
| "Access should automatically expire" | Entitlement Management |
| "Partner organization needs ongoing collaboration" | Entitlement Management + Connected Org |
| "One-time access for specific users" | Manual B2B invitation |

### Exam Question Indicators

```
When the question mentions:              Answer is likely:
─────────────────────────────────────    ────────────────────────────
"Enable external users to access"        B2B Guest Accounts
"Use existing credentials"               B2B Guest Accounts
"Self-service access request"            Entitlement Management
"Access packages"                        Entitlement Management
"External users request access"          Entitlement Management
"Automated provisioning"                 Entitlement Management
"Connected organization"                 Entitlement Management
"Time-limited access with governance"    Entitlement Management
```

---

## Exam Scenarios

### Scenario 1: External Developer Access to Azure Resources

**Question:**

A company named Contoso, Ltd. has a Microsoft Entra tenant that is integrated with Microsoft 365 and an Azure subscription.

Contoso has an on-premises identity infrastructure. The infrastructure includes servers that run Active Directory Domain Services (AD DS) and Microsoft Entra Connect.

Contoso has a partnership with a company named Fabrikam, Inc. Fabrikam has an Active Directory forest and a Microsoft 365 tenant. Fabrikam has the same on-premises identity infrastructure components as Contoso.

A team of 10 developers from Fabrikam will work on an Azure solution that will be hosted in the Azure subscription of Contoso. The developers must be added to the Contributor role for a resource group in the Contoso subscription.

You need to recommend a solution to ensure that Contoso can assign the role to the 10 Fabrikam developers. The solution must ensure that the Fabrikam developers use their existing credentials to access resources.

What should you recommend?

**Options:**

A. In the Microsoft Entra tenant of Contoso, create cloud-only user accounts for the Fabrikam developers.  
B. Configure a forest trust between the on-premises Active Directory forests of Contoso and Fabrikam.  
C. Configure an organization relationship between the Microsoft 365 tenants of Fabrikam and Contoso.  
D. In the Microsoft Entra tenant of Contoso, create guest accounts for the Fabrikam developers.

**Correct Answer: D - In the Microsoft Entra tenant of Contoso, create guest accounts for the Fabrikam developers.**

**Explanation:**

The appropriate way to provide external users (such as Fabrikam developers) access to Azure resources in Contoso's Azure subscription is by inviting them as Microsoft Entra B2B (Business-to-Business) guest users.

**Why Answer D is correct:**
- ✅ B2B guest users can be assigned Azure RBAC roles (Contributor)
- ✅ Guest users authenticate using their existing Fabrikam credentials
- ✅ Supports conditional access, auditing, and governance from Contoso tenant
- ✅ Secure, federated identity experience

**Why other options are incorrect:**

- **Option A (Cloud-only users):** This would create new identities in Contoso's directory and would **not allow the developers to use their existing credentials**, violating the requirement.

- **Option B (Forest trust):** Azure RBAC and Microsoft Entra ID operate in the cloud. Forest trusts are applicable only for **on-premises domain authentication**, not for access to Azure resources.

- **Option C (Organization relationship):** Organizational relationships are used for sharing **calendar availability** and other collaboration features in Microsoft 365, not for assigning RBAC roles in Azure.

**Key Exam Pattern:**

```
When you see:
  • External users need Azure resource access
  • Must use existing credentials
  • Need to assign Azure RBAC roles

The answer is: B2B Guest Accounts
```

### Scenario 2: Minimum Privilege External Access

**Question:**

Your organization needs to grant an external auditor read-only access to an Azure subscription for a compliance review. The auditor:
- Must use their corporate credentials
- Should only see resources in a specific resource group
- Access should be automatically reviewed quarterly

What should you implement?

**Correct Approach:**

1. **Invite auditor as B2B guest** - Allows use of existing credentials
2. **Assign Reader role at resource group scope** - Minimum privilege
3. **Configure Access Reviews** - Quarterly automated review

---

## Best Practices

### Invitation and Onboarding

| Practice | Recommendation |
|----------|----------------|
| **Use groups** | Invite guests and assign to security groups; assign RBAC to groups |
| **Least privilege** | Assign minimum necessary permissions |
| **Scope appropriately** | Assign roles at the narrowest scope needed |
| **Automate cleanup** | Use access reviews to remove stale guests |

### Security

| Practice | Recommendation |
|----------|----------------|
| **Conditional Access** | Require MFA for guest users |
| **Cross-tenant access** | Configure cross-tenant access settings for trusted partners |
| **Monitor sign-ins** | Review guest sign-in logs regularly |
| **Limit permissions** | Restrict guest user default permissions |

### Governance

| Practice | Recommendation |
|----------|----------------|
| **Access Reviews** | Implement quarterly reviews for guest access |
| **Entitlement Management** | Use access packages for self-service guest onboarding |
| **Naming conventions** | Use consistent naming for guest accounts |
| **Documentation** | Maintain records of business justification |

---

## Related Documentation

- [Identity Governance](microsoft-entra-id-identity-governance.md) - Access reviews and entitlement management
- [Access Reviews](entra-id-access-reviews.md) - Periodic access verification
- [Entitlement Management](entra-id-entitlement-management.md) - Self-service access and B2B automation
- [Azure RBAC](azure-rbac-permission-models.md) - Role-based access control fundamentals
- [Privileged Identity Management](microsoft-entra-privileged-identity-management.md) - JIT privileged access

---

## Additional Resources

### Microsoft Learn Documentation

- [What is Microsoft Entra B2B?](https://learn.microsoft.com/en-us/azure/active-directory/external-identities/what-is-b2b)
- [Add B2B collaboration users](https://learn.microsoft.com/en-us/azure/active-directory/external-identities/add-users-administrator)
- [Azure RBAC for external users](https://learn.microsoft.com/en-us/azure/role-based-access-control/role-assignments-external-users)
- [B2B collaboration overview](https://learn.microsoft.com/en-us/azure/active-directory/b2b/what-is-b2b)
- [Cross-tenant access settings](https://learn.microsoft.com/en-us/azure/active-directory/external-identities/cross-tenant-access-overview)

---

## Summary

Microsoft Entra B2B is the recommended solution for granting external users access to Azure resources while allowing them to use their existing credentials.

| Scenario | Solution | Why |
|----------|----------|-----|
| External users need Azure RBAC roles | B2B Guest Accounts | Federated identity + full RBAC support |
| Must use existing credentials | B2B Guest Accounts | Authentication happens at home tenant |
| Need governance and audit | B2B Guest Accounts | Full conditional access and audit support |

**Key Exam Tips:**
- "External users" + "Azure RBAC" → **B2B Guest Accounts**
- "Use existing credentials" → **B2B Guest Accounts** (not cloud-only)
- "Forest trust" → **On-premises only**, not Azure
- "Organization relationship" → **Microsoft 365 features only**, not Azure RBAC
