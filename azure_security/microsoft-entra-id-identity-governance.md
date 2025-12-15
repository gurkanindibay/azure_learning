# Microsoft Entra ID Identity Governance

## Overview

Microsoft Entra ID Identity Governance is a comprehensive suite of identity lifecycle management capabilities within Microsoft Entra ID that helps organizations balance security and productivity. It provides tools to ensure the right people have the right access to the right resources at the right time, while maintaining visibility and control over that access.

---

## Table of Contents

1. [What is Identity Governance?](#what-is-identity-governance)
2. [Core Components](#core-components)
3. [Identity Governance vs Related Services](#identity-governance-vs-related-services)
4. [Access Reviews](#access-reviews)
5. [Entitlement Management](#entitlement-management)
6. [Privileged Identity Management (PIM)](#privileged-identity-management-pim)
7. [Identity Lifecycle Management](#identity-lifecycle-management)
8. [Common Use Cases](#common-use-cases)
9. [Decision Guide: Choosing the Right Feature](#decision-guide-choosing-the-right-feature)
10. [Licensing Requirements](#licensing-requirements)
11. [Best Practices](#best-practices)
12. [Exam Scenarios](#exam-scenarios)

---

## What is Identity Governance?

Identity Governance addresses the challenge of managing identity and access lifecycle at scale. As organizations grow, manually managing who has access to what becomes unsustainable and error-prone. Identity Governance automates and governs this process.

### The Four Pillars of Identity Governance

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    Microsoft Entra ID Identity Governance                 │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Access Reviews  │  │  Entitlement    │  │    Privileged   │         │
│  │                 │  │  Management     │  │    Identity     │         │
│  │ • Periodic      │  │                 │  │    Management   │         │
│  │   verification  │  │ • Self-service  │  │                 │         │
│  │ • Guest access  │  │   access        │  │ • JIT access    │         │
│  │   review        │  │ • B2B           │  │ • Privileged    │         │
│  │ • Role review   │  │   collaboration │  │   roles         │         │
│  │ • Compliance    │  │ • Access        │  │ • Approval      │         │
│  │                 │  │   packages      │  │   workflows     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │              Lifecycle Workflows (Preview)                   │        │
│  │  • Joiner/Mover/Leaver automation                           │        │
│  │  • HR-driven provisioning                                    │        │
│  │  • Attribute-based access                                    │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Objectives

| Objective | How Identity Governance Addresses It |
|-----------|-------------------------------------|
| **Security** | Reduce risk by ensuring access is appropriate and time-bound |
| **Compliance** | Automate access certification and maintain audit trails |
| **Productivity** | Enable self-service access without IT bottlenecks |
| **Efficiency** | Automate repetitive access management tasks |
| **Visibility** | Provide complete audit trails for all access decisions |

---

## Core Components

### Component Overview

| Component | Purpose | Key Capability |
|-----------|---------|----------------|
| **Access Reviews** | Periodic verification of access | "Do they still need this access?" |
| **Entitlement Management** | Self-service access provisioning | "How do they get access?" |
| **Privileged Identity Management** | Just-in-time privileged access | "When do they need elevated access?" |
| **Lifecycle Workflows** | Automated identity lifecycle | "What happens when they join/leave?" |

### How Components Work Together

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Identity Lifecycle Flow                            │
└─────────────────────────────────────────────────────────────────────────┘

                    JOINER                    MOVER                    LEAVER
                      │                         │                         │
                      ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Lifecycle Workflows                                  │
│  • Provision accounts    • Update access based    • Deprovision         │
│  • Assign initial access   on role change         • Remove all access   │
│  • Send welcome email    • Trigger access review  • Disable account     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Entitlement Management                               │
│  • User requests access package via MyAccess portal                      │
│  • Approval workflow processes request                                   │
│  • Access granted with expiration                                        │
│  • B2B guest automatically provisioned (if external)                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Access Reviews                                       │
│  • Periodic review of access package assignments                         │
│  • Manager/owner validates continued need                                │
│  • Auto-revoke if not approved                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                Privileged Identity Management (PIM)                      │
│  • Eligible assignments for privileged roles                             │
│  • Just-in-time activation with approval                                 │
│  • Time-bound privileged access                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Identity Governance vs Related Services

### Understanding the Differences

A common exam confusion is distinguishing between Identity Governance features and other Microsoft Entra services:

| Service | Purpose | NOT Used For |
|---------|---------|--------------|
| **Identity Governance** | Access lifecycle, reviews, entitlements | Risk detection, authentication |
| **Identity Protection** | Risk-based conditional access, compromised accounts | Access reviews, provisioning |
| **Conditional Access** | Access policies based on conditions | Periodic reviews, privilege escalation |
| **PIM** | Just-in-time privileged access | Standard access provisioning |

### Quick Decision Matrix

| Scenario | Solution |
|----------|----------|
| "Monthly review of guest user access" | **Access Reviews** (Identity Governance) |
| "External users need to request access" | **Entitlement Management** (Identity Governance) |
| "Admin needs temporary elevated access" | **PIM** (Identity Governance) |
| "Detect risky sign-ins" | **Identity Protection** (NOT Governance) |
| "Block access from untrusted locations" | **Conditional Access** (NOT Governance) |
| "Sync on-premises AD to cloud" | **Entra Connect** (NOT Governance) |

---

## Access Reviews

Access Reviews enable organizations to regularly verify that users still need their current access. This is essential for compliance and security hygiene.

### When to Use Access Reviews

✅ **Use Access Reviews when:**
- Monthly/quarterly verification of who has access
- Reviewing guest user access to applications
- Validating privileged role assignments
- Meeting compliance requirements (SOX, HIPAA, ISO)
- Identifying and removing stale access

❌ **Do NOT use Access Reviews for:**
- Granting initial access (use Entitlement Management)
- Just-in-time privilege escalation (use PIM)
- Detecting compromised accounts (use Identity Protection)

### Access Review Configuration

```yaml
Access Review: "Monthly Fabrikam Guest Access Review"

Scope:
  Review Type: Application access
  Application: App1
  Users: Guest users only
  
Reviewers:
  Primary: External sponsor (Fabrikam account manager)
  Fallback: Resource owner (if no response in 7 days)
  
Schedule:
  Frequency: Monthly
  Duration: 14 days
  Start Date: First Monday of month
  
Actions:
  If approved: Maintain access
  If denied: Remove access immediately
  If no response: Remove access (configurable)
  
Notifications:
  Start: Email to reviewers
  Reminder: Day 7, Day 10
  Completion: Email to admin
```

### Access Review Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Access Review Workflow                        │
└─────────────────────────────────────────────────────────────────┘

Day 1: Review Starts
├─> Email sent to Fabrikam Account Manager
├─> "Review which Fabrikam users still need App1 access"
│
Day 1-14: Review Period
├─> Manager reviews each user
├─> Options: Approve / Deny / Don't know
├─> System shows recommendations (based on sign-in activity)
│
Day 14: Review Ends
├─> Results auto-applied (if configured)
├─> Denied users lose access
├─> No-response users: configurable action
│
Audit:
└─> Complete log of all decisions for compliance
```

📚 **Detailed Documentation:** [entra-id-access-reviews.md](entra-id-access-reviews.md)

---

## Entitlement Management

Entitlement Management automates access request workflows, enabling self-service access while maintaining governance. It's particularly powerful for B2B collaboration scenarios.

### When to Use Entitlement Management

✅ **Use Entitlement Management when:**
- External partners need to request access to your apps
- Self-service access requests with approval workflows
- Bundling multiple resources into access packages
- Automating B2B guest user provisioning
- Time-bound access with automatic expiration

❌ **Do NOT use Entitlement Management for:**
- Periodic review of existing access (use Access Reviews)
- Just-in-time admin access (use PIM)
- Risk-based access decisions (use Conditional Access)

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Access Package** | Bundle of resources users can request (apps, groups, sites) |
| **Catalog** | Container for access packages and resources |
| **Policy** | Rules defining who can request and approval requirements |
| **Connected Organization** | External Entra tenant for B2B collaboration |

### Entitlement Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│               Entitlement Management Workflow                    │
└─────────────────────────────────────────────────────────────────┘

1. External User (Fabrikam) browses MyAccess portal
   └─> https://myaccess.microsoft.com
   └─> Sees available access packages from Contoso

2. User requests "App1 Access for Partners"
   └─> Provides business justification
   └─> Specifies duration needed

3. Approval Workflow
   └─> Contoso resource owner receives request
   └─> Reviews justification
   └─> Approves or denies

4. Automatic Provisioning (if approved)
   └─> B2B invitation sent to user@fabrikam.com
   └─> Guest account created in Contoso tenant
   └─> App1 access granted
   └─> Access expires after defined period

5. Lifecycle Management
   └─> Access review triggered before expiration
   └─> Access automatically removed when expired
   └─> Guest account cleanup (configurable)
```

📚 **Detailed Documentation:** [entra-id-entitlement-management.md](entra-id-entitlement-management.md)

---

## Privileged Identity Management (PIM)

PIM provides just-in-time privileged access, reducing the security risks of standing admin privileges.

### When to Use PIM

✅ **Use PIM when:**
- Administrators need temporary elevated access
- Approval required before privilege escalation
- Time-bound admin access with automatic revocation
- Audit trail of all privileged operations
- Break-glass account management

❌ **Do NOT use PIM for:**
- Regular (non-privileged) access provisioning
- Service-to-service authentication (use Managed Identity)
- Periodic access reviews of non-privileged roles
- B2B guest access management

### PIM vs Access Reviews vs Entitlement Management

| Feature | PIM | Access Reviews | Entitlement Management |
|---------|-----|----------------|----------------------|
| **Timing** | On-demand | Scheduled | On-demand |
| **Duration** | Hours | N/A (review-based) | Days/Months |
| **Purpose** | Privilege escalation | Access verification | Access provisioning |
| **Target** | Admin roles | Any access | Resource bundles |
| **Approval** | Before activation | After access (recertification) | Before access |

📚 **Detailed Documentation:** [microsoft-entra-privileged-identity-management.md](microsoft-entra-privileged-identity-management.md)

---

## Identity Lifecycle Management

### Joiner-Mover-Leaver (JML) Process

Identity Governance provides automation for the employee lifecycle:

```
JOINER (New Employee)                    
├─> HR system triggers workflow          
├─> Account automatically created        
├─> Basic access assigned based on role  
├─> Welcome email sent                   
├─> Manager notified                     

MOVER (Role Change)
├─> HR system detects department change
├─> Old department access reviewed
├─> New department access assigned
├─> Access review triggered for old access

LEAVER (Termination)
├─> HR system triggers workflow
├─> All access revoked
├─> Account disabled
├─> Manager receives offboarding checklist
├─> Data retention policies applied
```

### Lifecycle Workflows

Lifecycle Workflows (part of Identity Governance) automate common tasks:

| Workflow Type | Trigger | Common Actions |
|---------------|---------|----------------|
| **Joiner** | User created, employeeHireDate | Provision accounts, assign groups |
| **Mover** | Attribute change (department, title) | Update access, trigger review |
| **Leaver** | User disabled, employeeLeaveDateTime | Revoke access, send notifications |

---

## Common Use Cases

### Use Case 1: External Partner Access (Contoso + Fabrikam)

**Scenario:** Fabrikam users need access to Contoso's App1. Access must be reviewed monthly.

**Solution Architecture:**

```yaml
Step 1: Entitlement Management (Initial Access)
  - Create connected organization for Fabrikam
  - Create access package: "App1 - External Partners"
  - Policy: Fabrikam users can request, resource owner approves
  - Duration: 90 days with access review

Step 2: Access Reviews (Ongoing Verification)
  - Monthly review of App1 guest access
  - Reviewer: Fabrikam account manager
  - Auto-remove if denied or no response

Step 3: Automatic Cleanup
  - Access expires after 90 days unless renewed
  - Guest accounts can be cleaned up after inactivity
```

### Use Case 2: Temporary Admin Access

**Scenario:** Developers occasionally need Contributor access to production Azure resources.

**Solution:** Use PIM (NOT Entitlement Management)

```yaml
PIM Configuration:
  Role: Contributor
  Scope: Production Resource Group
  Assignment: Eligible
  
  Activation:
    Duration: 4 hours max
    Require MFA: Yes
    Require Justification: Yes
    Require Approval: Yes (Operations Manager)
```

### Use Case 3: Compliance Access Certification

**Scenario:** SOX compliance requires quarterly access certification for finance applications.

**Solution:** Use Access Reviews

```yaml
Access Review:
  Scope: Finance application access
  Frequency: Quarterly
  Reviewers: Department managers
  
  Compliance:
    Auto-apply results: Yes
    Export decisions for audit
    Retain records for 7 years
```

---

## Decision Guide: Choosing the Right Feature

### Quick Reference Chart

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Which Identity Governance Feature?                    │
└─────────────────────────────────────────────────────────────────────────┘

Question: "Who should have access?"
├─> Periodic verification → ACCESS REVIEWS
├─> Self-service request → ENTITLEMENT MANAGEMENT
└─> Temporary admin → PIM

Question: "When do they need access?"
├─> Always (with review) → ENTITLEMENT MANAGEMENT + ACCESS REVIEWS
├─> On-demand (hours) → PIM
└─> Time-bound (days/months) → ENTITLEMENT MANAGEMENT

Question: "What type of access?"
├─> Application access → ENTITLEMENT MANAGEMENT / ACCESS REVIEWS
├─> Privileged roles → PIM
├─> Guest access → ENTITLEMENT MANAGEMENT
└─> Group membership → ACCESS REVIEWS / ENTITLEMENT MANAGEMENT
```

### Scenario-Based Decision Tree

| If the requirement mentions... | Use... |
|-------------------------------|--------|
| "Monthly review" or "quarterly review" | Access Reviews |
| "Remove if no longer needed" | Access Reviews |
| "External users request access" | Entitlement Management |
| "B2B collaboration" | Entitlement Management |
| "Access packages" | Entitlement Management |
| "Temporary admin access" | PIM |
| "Just-in-time" | PIM |
| "Privilege escalation" | PIM |
| "Approval before activation" | PIM (or Entitlement Management for non-admin) |
| "Minimize development effort" | Any Identity Governance feature (built-in) |

---

## Licensing Requirements

| Feature | License Required |
|---------|-----------------|
| **Access Reviews** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **Entitlement Management** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **PIM for Entra Roles** | Microsoft Entra ID P2 |
| **PIM for Azure Resources** | Microsoft Entra ID P2 |
| **Lifecycle Workflows** | Microsoft Entra ID Governance |

**Note:** Microsoft 365 E5 includes Microsoft Entra ID P2.

---

## Best Practices

### 1. Layer Your Governance

Use multiple features together for comprehensive governance:

```
Initial Access → Entitlement Management
       ↓
Ongoing Verification → Access Reviews
       ↓
Privileged Access → PIM
       ↓
Lifecycle Events → Lifecycle Workflows
```

### 2. Delegate Appropriately

- **IT**: Manages governance framework and policies
- **Business Owners**: Manage their catalogs and access packages
- **Managers**: Review their team's access
- **Resource Owners**: Approve access to their resources

### 3. Automate Where Possible

- Enable auto-apply for access reviews
- Set access expiration in entitlement management
- Configure automatic cleanup for denied access
- Use HR-driven lifecycle workflows

### 4. Maintain Audit Trails

All Identity Governance features provide comprehensive logging:
- Access review decisions
- Access package requests and approvals
- PIM activations
- Lifecycle workflow executions

### 5. Start with High-Risk Areas

Prioritize governance for:
1. Privileged roles (Global Admin, etc.)
2. Guest/external user access
3. Sensitive applications
4. Compliance-regulated resources

---

## Exam Scenarios

### Scenario 1: Guest User Monthly Access Review (Contoso Case Study)

**Question:**

Contoso, Ltd. has a business partnership with Fabrikam, Inc. Fabrikam users access some Contoso applications over the internet by using Microsoft Entra ID guest accounts.

**Identity Requirements:**
> "Every month, an account manager at Fabrikam must review which Fabrikam users have access permissions to App1. Accounts that no longer need permissions must be removed as guests. The solution must minimize development efforts."

Which service should you implement to meet the identity requirements?

**Options:**

A. Microsoft Entra ID Identity Governance  
B. Microsoft Entra ID Identity Protection  
C. Microsoft Entra Privileged Identity Management (PIM)  
D. Azure Automation

**Correct Answer: A - Microsoft Entra ID Identity Governance**

**Explanation:**

**Why A is correct:**

The requirement describes a **recertification process** or **access review**, which is a core feature of Microsoft Entra ID Identity Governance (specifically, Access Reviews). Key indicators:

- ✅ **"Every month"** → Periodic/scheduled review = Access Reviews
- ✅ **"Review which users have access"** → Access verification = Access Reviews
- ✅ **"Remove if no longer needed"** → Auto-remediation = Access Reviews
- ✅ **"Minimize development efforts"** → Built-in feature, no custom code

**Configuration:**

```yaml
Access Review: "Monthly Fabrikam App1 Access Review"

Scope:
  Application: App1
  Users: Guest users from Fabrikam
  
Reviewers:
  Type: External (Fabrikam Account Manager)
  
Schedule:
  Frequency: Monthly
  Duration: 14 days
  
Actions:
  If denied or no response: Remove guest access
```

**Why other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B - Identity Protection** | Detects risky sign-ins and compromised accounts. Does NOT perform periodic access reviews. |
| **C - PIM** | Manages just-in-time privileged access. Does NOT perform monthly access reviews of guest users. |
| **D - Azure Automation** | Requires custom scripting. Contradicts "minimize development efforts" requirement. |

**Key Distinction:**

| Requirement | Solution |
|-------------|----------|
| "Review who has access monthly" | **Access Reviews** |
| "Temporary admin access" | **PIM** |
| "Detect compromised accounts" | **Identity Protection** |

**Reference(s):**
- [Access Reviews Overview](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Identity Governance Overview](https://learn.microsoft.com/en-us/entra/id-governance/identity-governance-overview)

**Domain:** Design Identity, Governance, and Monitoring Solutions

---

### Scenario 2: External Partner Self-Service Access

**Question:**

Contoso needs to allow users from partner organization Fabrikam to request access to a collaboration application. The solution should:
- Allow Fabrikam users to request access without IT involvement
- Require approval from Contoso resource owner
- Automatically expire access after 90 days
- Minimize administrative overhead

Which service should you use?

**Options:**

A. Microsoft Entra Access Reviews  
B. Microsoft Entra Entitlement Management  
C. Microsoft Entra Privileged Identity Management  
D. Azure AD B2B direct invitation

**Correct Answer: B - Microsoft Entra Entitlement Management**

**Explanation:**

This scenario describes **self-service access provisioning** with approval workflow and automatic expiration—exactly what Entitlement Management provides.

Key indicators:
- ✅ **"Request access without IT"** → Self-service = Entitlement Management
- ✅ **"Require approval"** → Approval workflow = Entitlement Management
- ✅ **"Automatically expire"** → Time-bound access = Entitlement Management
- ✅ **External users** → B2B + Access Packages = Entitlement Management

**Why other options are incorrect:**
- **Access Reviews (A)**: Reviews existing access, doesn't provision new access
- **PIM (C)**: For privileged role activation, not application access provisioning
- **B2B direct invitation (D)**: No self-service, no approval workflow, no automatic expiration

---

### Scenario 3: Distinguishing PIM from Access Reviews

**Question:**

A developer needs temporary Contributor access to a production resource group to deploy an emergency fix. Access should:
- Last no more than 4 hours
- Require approval from the operations manager
- Be automatically revoked after the time limit
- Be fully audited

Which solution should you use?

**Options:**

A. Microsoft Entra Access Reviews  
B. Microsoft Entra Entitlement Management  
C. Microsoft Entra Privileged Identity Management  
D. Azure RBAC with time-limited assignments

**Correct Answer: C - Microsoft Entra Privileged Identity Management**

**Explanation:**

This scenario describes **just-in-time privileged access**—the core purpose of PIM.

Key indicators:
- ✅ **"Temporary access" (hours)** → JIT access = PIM
- ✅ **"Privileged role" (Contributor)** → Privileged access = PIM
- ✅ **"Require approval"** → Approval workflow = PIM
- ✅ **"Automatically revoked"** → Time-bound activation = PIM

**Why other options are incorrect:**
- **Access Reviews (A)**: For periodic verification, not on-demand access
- **Entitlement Management (B)**: For access packages (days/months), not privileged role activation (hours)
- **Azure RBAC (D)**: No built-in approval workflow or automatic revocation

---

## Related Documentation

- [Access Reviews](entra-id-access-reviews.md) - Periodic access verification
- [Entitlement Management](entra-id-entitlement-management.md) - Self-service access and B2B
- [Privileged Identity Management](microsoft-entra-privileged-identity-management.md) - Just-in-time privileged access
- [Azure RBAC](azure-rbac-permission-models.md) - Role-based access control fundamentals
- [Azure Identity Overview](azure_identity_overview.md) - Service principals and managed identities

---

## Additional Resources

### Microsoft Learn Documentation

- [What is Identity Governance?](https://learn.microsoft.com/en-us/entra/id-governance/identity-governance-overview)
- [Access Reviews Overview](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Entitlement Management Overview](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview)
- [PIM Overview](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Lifecycle Workflows](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

---

## Summary

Microsoft Entra ID Identity Governance provides a comprehensive suite of tools for managing the identity and access lifecycle:

| Feature | Purpose | Key Question Answered |
|---------|---------|----------------------|
| **Access Reviews** | Periodic verification | "Should they still have this access?" |
| **Entitlement Management** | Self-service provisioning | "How do they get access?" |
| **PIM** | Just-in-time privileges | "When do they need elevated access?" |
| **Lifecycle Workflows** | Automation | "What happens when they join/move/leave?" |

**Key Exam Tips:**
- "Monthly review" or "periodic review" → **Access Reviews**
- "External users request access" → **Entitlement Management**
- "Temporary admin access" → **PIM**
- "Detect risky sign-ins" → **Identity Protection** (NOT Governance)
- "Minimize development effort" → Any Identity Governance feature (built-in)

Identity Governance is essential for organizations seeking to balance security, compliance, and productivity in managing access to their resources.
