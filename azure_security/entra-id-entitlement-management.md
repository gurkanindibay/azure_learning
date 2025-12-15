# Microsoft Entra Entitlement Management

## Overview

Microsoft Entra Entitlement Management is an identity governance feature that enables organizations to manage identity and access lifecycle at scale. It automates access request workflows, access assignments, reviews, and expiration for internal and external users. Entitlement Management is particularly valuable for B2B collaboration scenarios where external users need controlled, time-bound access to organizational resources.

---

## Table of Contents

1. [What is Entitlement Management?](#what-is-entitlement-management)
2. [Key Concepts](#key-concepts)
3. [Core Features](#core-features)
4. [Relationship with Access Reviews](#relationship-with-access-reviews)
5. [B2B Collaboration and Cross-Tenant Access](#b2b-collaboration-and-cross-tenant-access)
6. [Access Packages](#access-packages)
7. [Catalogs](#catalogs)
8. [Connected Organizations](#connected-organizations)
9. [Approval Workflows](#approval-workflows)
10. [Licensing Requirements](#licensing-requirements)
11. [Common Use Cases](#common-use-cases)
12. [Best Practices](#best-practices)
13. [Comparison with Alternative Solutions](#comparison-with-alternative-solutions)
14. [Exam Scenarios](#exam-scenarios)

---

## What is Entitlement Management?

Entitlement Management is part of Microsoft Entra ID Governance that helps organizations:

- **Automate access request workflows** for internal and external users
- **Govern B2B guest access** with approval workflows and time-bound assignments
- **Create access packages** that bundle multiple resources (groups, apps, SharePoint sites)
- **Delegate access governance** to business owners and project managers
- **Ensure compliance** with automatic access reviews and expiration policies

### Key Benefits

✅ **Simplified B2B Collaboration**: Automatically invite and provision external users  
✅ **Self-Service Access**: Users request access through MyAccess portal  
✅ **Automated Lifecycle**: Access automatically expires and is removed  
✅ **Governance at Scale**: Manage thousands of external users efficiently  
✅ **Audit and Compliance**: Complete audit trail of all access requests and approvals  
✅ **Reduced Admin Overhead**: Business owners manage access without IT intervention  

---

## Key Concepts

### Identity Governance Lifecycle

```
User Requests Access
        ↓
Approval Workflow (if configured)
        ↓
Access Package Assignment
        ↓
Guest User Invitation (B2B)
        ↓
Resource Provisioning
        ↓
Access Review (periodic)
        ↓
Access Expiration
        ↓
Automatic Cleanup
```

### Core Components

| Component | Description |
|-----------|-------------|
| **Access Package** | Collection of resources (apps, groups, sites) that users can request |
| **Catalog** | Container for access packages and resources |
| **Policy** | Rules defining who can request access and approval requirements |
| **Connected Organization** | External Entra tenant or domain for B2B collaboration |
| **MyAccess Portal** | Self-service portal where users request and manage access |

---

## Core Features

### 1. Self-Service Access Requests

Users can browse available access packages in MyAccess portal and request access without contacting IT.

```
MyAccess Portal: https://myaccess.microsoft.com
```

### 2. Automatic Guest User Provisioning

When external users request access:
1. Entra ID automatically sends B2B invitation
2. Guest user account is created in your tenant
3. Access package resources are assigned
4. User receives email with access instructions

### 3. Time-Bound Access

All access assignments can have expiration dates:
- Fixed date expiration
- Number of days after assignment
- Access reviews before expiration
- Automatic cleanup when expired

### 4. Approval Workflows

Multi-stage approval workflows with:
- Sponsor approval
- Resource owner approval
- Manager approval
- Auto-approval for specific users/groups

### 5. Access Reviews

Periodic reviews of access package assignments to ensure continued need for access.

### 6. Separation of Duties

Prevent users from requesting conflicting access packages that violate policy.

---

## Relationship with Access Reviews

### Overview

**Entitlement Management and Access Reviews are complementary features** within Microsoft Entra ID Identity Governance that work together throughout the access lifecycle. Understanding their relationship is crucial for implementing comprehensive access governance.

### Two Sides of the Same Governance Coin

| Feature | Entitlement Management | Access Reviews |
|---------|----------------------|----------------|
| **Timing** | Before and during access | After access granted |
| **Purpose** | Access provisioning and lifecycle | Periodic access verification |
| **Focus** | *Who gets access* and *for how long* | *Should they still have access?* |
| **Trigger** | User request or admin assignment | Scheduled review cycle |
| **Guest Provisioning** | Yes (automatic B2B) | No |
| **Approval Workflow** | Before access granted | After access (revalidation) |

### How They Work Together in the Access Lifecycle

Entitlement Management and Access Reviews integrate seamlessly in the identity governance lifecycle:

```
1. User Requests Access          ← Entitlement Management
   ↓
2. Approval Workflow             ← Entitlement Management
   ↓
3. Access Package Assignment     ← Entitlement Management
   ↓
4. Guest User Invitation (B2B)   ← Entitlement Management
   ↓
5. Resource Provisioning         ← Entitlement Management
   ↓
6. Access Review (periodic)      ← Access Reviews (Integration Point)
   ↓
7. Access Expiration             ← Entitlement Management
   ↓
8. Automatic Cleanup             ← Entitlement Management
```

**Step 6 is the integration point** where Access Reviews can be configured as part of access package policies to ensure periodic revalidation before expiration.

### Integration in Practice

Access Reviews can be embedded directly into access package policies:

```yaml
Access Package: "App1 Access - Fabrikam Users"
  Duration: 180 days
  
  Review Configuration:
    - Review Type: Before expiration
    - Review Trigger: 15 days before expiration (Day 165)
    - Reviewers: Resource owner or manager
    
  Review Outcomes:
    - Approved → Entitlement Management extends access for another 180 days
    - Denied → Entitlement Management removes access automatically
    - No Response → Based on policy (remove/keep/apply recommendation)
```

### Real-World Scenario: External Partner Access

**Phase 1: Entitlement Management (Initial Provisioning)**

```
Day 1: Fabrikam user requests "App1 Access" package via MyAccess portal
  ↓
Day 2: Resource owner approves request
  ↓
Day 2: Entitlement Management automatically:
  - Creates guest account in Contoso tenant
  - Assigns App1 permissions
  - Sets 90-day expiration
  - Logs all actions for audit
```

**Phase 2: Access Reviews (Periodic Verification)**

```
Day 75: Access Review automatically triggered (15 days before expiration)
  ↓
Day 75: Email sent to manager:
  Subject: "Access Review: Does John still need App1 access?"
  Content: Current permissions, last sign-in, access duration
  ↓
Day 78: Manager reviews and approves
  ↓
Day 90: Entitlement Management processes review result:
  - If approved: Extends access for another 90 days
  - If denied: Removes access and guest permissions
  - If no response: Applies configured policy (typically deny)
```

### Key Differences

#### Entitlement Management (Front-End)
- **When**: Before access is granted
- **What**: Automates access requests, approvals, and provisioning
- **Who**: IT administrators, business owners, requesters
- **Result**: User gets access to resources

#### Access Reviews (Back-End)
- **When**: After access is granted (periodic)
- **What**: Verifies existing access is still needed
- **Who**: Managers, resource owners, users (self-review)
- **Result**: Access continued or revoked

### Complementary Nature

These features are designed to work together, not replace each other:

✅ **Entitlement Management** = "Give the right people access efficiently"  
✅ **Access Reviews** = "Make sure they still need it"

Together, they provide **complete access lifecycle governance**:
- **Provisioning**: Automated, governed, and audited
- **Verification**: Periodic reviews ensure continued business need
- **Cleanup**: Automatic removal when no longer needed

### Configuration Example

```yaml
Access Package: "External Consultant Access"
  
  Entitlement Management Configuration:
    Resources:
      - Application: Project Management Tool
      - Group: Consultant-Access-Group
      - SharePoint: Project Documents Site
    
    Policy:
      Who can request: Connected organizations (partners)
      Approval: Two-stage (sponsor + resource owner)
      Duration: 90 days
      
  Access Review Configuration:
    Enabled: Yes
    Timing: 15 days before expiration
    Reviewers: Resource owner
    If not reviewed: Remove access
    Frequency: Every assignment expiration
```

### Benefits of Integration

1. **Complete Governance**: Covers entire access lifecycle from request to removal
2. **Reduced Risk**: Regular verification ensures access doesn't outlive business need
3. **Compliance**: Automated reviews meet regulatory requirements
4. **Efficiency**: No manual tracking of access expiration or review schedules
5. **Audit Trail**: Complete history of who requested, approved, reviewed, and retained access
6. **Self-Correcting**: System automatically removes unverified access

### When to Use Each

**Use Entitlement Management when you need to**:
- Enable B2B collaboration with external partners
- Automate guest user provisioning
- Create self-service access request workflows
- Delegate access governance to business owners
- Bundle multiple resources into access packages
- Set time-bound access with automatic expiration

**Use Access Reviews when you need to**:
- Periodically verify existing access is still needed
- Review RBAC role assignments
- Audit guest user access
- Meet compliance requirements for access certification
- Identify and remove inactive user access
- Review privileged role assignments

**Use Both Together when you need to**:
- Govern external user access with initial approval AND periodic verification
- Automate B2B collaboration with continuous compliance
- Provide time-bound access with extension based on business need
- Ensure access doesn't outlive project or contract terms
- Maintain comprehensive audit trail for compliance

### Summary

Entitlement Management and Access Reviews are not alternatives—they are **integrated components of a comprehensive identity governance solution**. Entitlement Management handles the "front door" (provisioning, approval, assignment), while Access Reviews handle the "maintenance" (periodic verification, recertification). Together, they ensure that:

✅ The right people get access at the right time  
✅ Access is regularly verified as still needed  
✅ Unnecessary access is automatically removed  
✅ Complete audit trails exist for compliance  
✅ Governance scales across internal and external users  

---

## B2B Collaboration and Cross-Tenant Access

### Enabling External Users to Authenticate to Your Applications

**Scenario**: You have a single-tenant application (App1) in Contoso.com tenant. Users from Fabrikam.com tenant need to authenticate to App1.

**Solution**: Microsoft Entra Entitlement Management

#### Why This Works

1. **Single-Tenant Application Limitation**: Single-tenant apps only authenticate users from the home tenant
2. **Guest User Solution**: External users must be invited as B2B guests into Contoso tenant
3. **Automated B2B Provisioning**: Entitlement Management automates guest invitation and access assignment
4. **Governance and Control**: Approval workflows, time-bound access, and periodic reviews ensure security

#### Configuration Steps

```yaml
Step 1: Create Connected Organization
  Name: "Fabrikam Collaboration"
  Type: "Entra Tenant"
  Tenant ID or Domain: "fabrikam.com"

Step 2: Create Access Package
  Name: "App1 Access for External Partners"
  Resources:
    - App1 (application registration)
    - Security group with App1 permissions
  
Step 3: Configure Policy
  Who can request:
    - Specific connected organizations: Fabrikam
    - All users from the connected organization
  
  Approval:
    - Require approval: Yes
    - Approvers: App1 resource owners
    - Decision timeout: 14 days
  
  Access Duration:
    - Expire assignments: After 90 days
    - Require access reviews: Before expiration
  
  Enable new requests: Yes
```

### B2B Guest User Lifecycle

```
1. Fabrikam user browses MyAccess portal
   ↓
2. Requests "App1 Access for External Partners"
   ↓
3. Email sent to Contoso resource owner for approval
   ↓
4. Upon approval:
   - B2B invitation sent to user@fabrikam.com
   - Guest account created in Contoso tenant
   - User added to App1 security group
   - App1 permissions assigned
   ↓
5. User@fabrikam.com signs in with Fabrikam credentials
   ↓
6. User authenticates to App1 as guest in Contoso tenant
   ↓
7. After 90 days (or based on policy):
   - Access review triggered
   - If not renewed: access automatically removed
   - Guest account can be removed or left for future access
```

---

## Access Packages

### What is an Access Package?

A bundle of resources that users can request in a single operation. Resources can include:

- **Applications**: Enterprise apps registered in Entra ID
- **Groups**: Security groups or Microsoft 365 groups
- **SharePoint Sites**: SharePoint Online team sites
- **Entra Roles**: Directory roles (limited scenarios)

### Access Package Components

```yaml
Access Package: "Project Phoenix - External Consultant Access"

Resources:
  - Application: Phoenix Web App
  - Group: Phoenix-Contributors (with Project Phoenix site permissions)
  - SharePoint: Phoenix Project Site
  - Team: Phoenix Teams channel

Policies:
  - Internal Employees (auto-approval, 180 days)
  - External Consultants (manager approval, 90 days)
  - Emergency Access (CISO approval, 7 days)

Settings:
  Request information: "Business justification required"
  Questions: "Which project phase? (Design/Build/Deploy)"
  Separation of duties: Cannot request "Project Phoenix - Admin"
```

### Policy Types

| Policy Type | Description | Use Case |
|-------------|-------------|----------|
| **Specific Users** | Named users can request | VIP access, executives |
| **Members of Groups** | Group members can request | Department-specific access |
| **Connected Organizations** | Users from specific external tenants | Partner collaboration |
| **All Users (internal)** | Any internal employee | General corporate resources |
| **Direct Assignment** | Admin assigns without request | Mandatory access |

---

## Catalogs

### What is a Catalog?

A catalog is a container that holds:
- Access packages
- Resources (apps, groups, sites)
- Catalog owners and contributors

### Types of Catalogs

1. **General Catalog** (built-in)
   - Default catalog for all tenants
   - Global administrators are owners
   - Good for centralized IT-managed access

2. **Custom Catalogs**
   - Department or project-specific
   - Delegated to business owners
   - Better for decentralized access governance

### Catalog Delegation

```yaml
Catalog: "Marketing Department Resources"

Owners:
  - Marketing VP
  - Marketing IT Lead

Contributors:
  - Marketing Program Managers (can create access packages)

Resources:
  - Marketing Portal app
  - Marketing-Staff group
  - Marketing SharePoint sites
  - Campaign management tools
```

**Benefits of Delegation**:
- Business owners manage their own resources
- IT maintains governance framework
- Faster access provisioning
- Reduced IT ticket volume

---

## Connected Organizations

### What is a Connected Organization?

An external Entra ID tenant or verified domain that you collaborate with regularly.

### Types

1. **Entra Tenant**: External Microsoft Entra tenant with known tenant ID
2. **Domain**: Email domain verified through DNS (e.g., @partner.com)

### Configuration

```yaml
Connected Organization: "Fabrikam Inc."

Type: Entra Tenant
Tenant ID: 12345678-1234-1234-1234-123456789012
Domains: fabrikam.com, fabrikam.co.uk

Sponsors:
  - partner-manager@contoso.com
  - vendor-coordinator@contoso.com

State: Configured (allows access package requests)
```

### States

| State | Description | Access Requests |
|-------|-------------|-----------------|
| **Configured** | Active collaboration partner | Allowed |
| **Proposed** | Pending approval | Not allowed |

---

## Approval Workflows

### Single-Stage Approval

```yaml
Approvers: Resource owners
Timeout: 14 days
Fallback: Auto-deny if no response
```

### Multi-Stage Approval

```yaml
Stage 1:
  Approvers: User's manager
  Timeout: 7 days

Stage 2:
  Approvers: Resource owner
  Timeout: 7 days
  
Stage 3:
  Approvers: Security team
  Timeout: 5 days
```

### Approval Options

- **Internal sponsors**: Designated approvers in your organization
- **External sponsors**: Approvers from connected organizations
- **Manager**: Requester's direct manager (from Entra ID)
- **Specific users**: Named approvers
- **None (auto-approval)**: Instant access for trusted users

### Alternate Approvers

Configure backup approvers if primary doesn't respond within timeout period.

---

## Licensing Requirements

| Feature | Required License |
|---------|-----------------|
| **Entitlement Management** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **B2B Guest Users** | Included with Entra ID P1/P2 (1:5 ratio)* |
| **Access Reviews** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |

*For every Entra ID P1/P2 license, you can invite up to 5 guest users at no additional cost.

**Note**: Microsoft 365 E5 and F5 Security include Microsoft Entra ID P2.

---

## Common Use Cases

### 1. External Partner Collaboration

**Scenario**: Regular collaboration with consulting firms, vendors, and partners.

**Solution**:
- Create connected organizations for each partner
- Create access packages for different project types
- Enable self-service requests with approval
- Set 90-day expiration with reviews

### 2. Contractor Onboarding

**Scenario**: Temporary contractors need time-limited access to specific resources.

**Solution**:
- Create "Contractor Access" packages per department
- Require sponsor and manager approval
- Set fixed expiration date matching contract end
- Automatically remove access when expired

### 3. Project-Based Access

**Scenario**: Cross-functional teams need temporary access to project resources.

**Solution**:
- Create access package per project
- Bundle project app, SharePoint site, and Teams
- Allow internal employees to self-request
- Set project end date as expiration

### 4. Temporary Elevated Access

**Scenario**: Users occasionally need elevated permissions for specific tasks.

**Solution**:
- Create access packages for elevated roles
- Require multi-stage approval
- Set short expiration (hours or days)
- Log all access for audit

### 5. M&A Integration

**Scenario**: Acquired company users need gradual access to parent company resources.

**Solution**:
- Add acquired company as connected organization
- Create phased access packages
- Govern transition with approval workflows
- Review access quarterly

---

## Best Practices

### 1. Start with Connected Organizations

Define your regular external partners as connected organizations to streamline B2B access.

### 2. Use Catalogs for Delegation

Create department-specific catalogs and delegate ownership to business units.

### 3. Always Set Expiration

Every access package assignment should have an expiration date to prevent access sprawl.

### 4. Configure Approval for External Access

Always require approval for external users requesting access to sensitive resources.

### 5. Enable Access Reviews

Configure periodic reviews before expiration to ensure continued business need.

### 6. Bundle Related Resources

Group related resources into access packages (app + group + SharePoint site) for consistency.

### 7. Use Questions for Context

Add custom questions to capture business justification and usage details.

### 8. Monitor MyAccess Analytics

Review request patterns, approval times, and denied requests to optimize policies.

### 9. Separate Duty Controls

Configure incompatible access packages to prevent policy violations.

### 10. Regular Catalog Audits

Periodically review catalogs to remove unused access packages and update resources.

---

## Comparison with Alternative Solutions

### Entitlement Management vs. Manual B2B Invitations

| Aspect | Entitlement Management | Manual Invitations |
|--------|----------------------|-------------------|
| **Scalability** | High (thousands of guests) | Low (manual process) |
| **Approval Workflow** | Built-in, multi-stage | Manual email approval |
| **Access Expiration** | Automatic | Manual tracking needed |
| **Self-Service** | MyAccess portal | Must contact IT |
| **Audit Trail** | Complete, automatic | Manual documentation |
| **Time to Access** | Hours (with approval) | Days (IT tickets) |
| **Governance** | Policy-driven | Ad-hoc |

### Entitlement Management vs. Conditional Access

| Feature | Entitlement Management | Conditional Access |
|---------|----------------------|-------------------|
| **Purpose** | Provision and govern access | Control access based on conditions |
| **Scope** | Who has access (identity lifecycle) | How access is granted (security policy) |
| **User Provisioning** | Yes (creates guest accounts) | No (assumes users exist) |
| **Approval Workflows** | Yes | No |
| **Time-Bound Access** | Yes | No |
| **Best For** | B2B collaboration, access governance | Security controls, MFA enforcement |

**Note**: These are complementary. Use both together:
- **Entitlement Management**: Governs who gets access and for how long
- **Conditional Access**: Enforces security requirements when accessing resources

### Entitlement Management vs. Provisioning Service

| Feature | Entitlement Management | Entra Provisioning Service |
|---------|----------------------|--------------------------|
| **Direction** | Inbound (external→internal) | Outbound (Entra→external systems) |
| **User Type** | B2B guest users | Internal users synced to apps |
| **Governance** | Approval workflows, reviews | Automatic sync based on attributes |
| **Use Case** | External collaboration | SaaS app user management |

### Entitlement Management vs. Access Reviews

| Feature | Entitlement Management | Access Reviews |
|---------|----------------------|----------------|
| **Focus** | Access provisioning and lifecycle | Periodic access verification |
| **Triggers** | User request | Scheduled review |
| **Guest Provisioning** | Yes (automatic) | No |
| **Approval Workflow** | Before access granted | After access granted |
| **Relationship** | Complementary | Part of entitlement lifecycle |

**Integration**: Access reviews can be configured as part of access package policies to ensure periodic revalidation.

---

## Exam Scenarios

### Scenario 1: Enabling Cross-Tenant Authentication for Single-Tenant App

**Question:**

Your company has the divisions shown in the following table:

| Division | Microsoft Entra Tenant |
|----------|----------------------|
| Contoso | contoso.com |
| Fabrikam | fabrikam.com |

Sub1 contains an Azure App Service web app named App1. App1 uses Microsoft Entra for single-tenant user authentication. Users from contoso.com can authenticate to App1.

You need to recommend a solution to enable users in the fabrikam.com tenant to authenticate to App1.

What should you recommend?

**Options:**

A. Enable Microsoft Entra pass-through authentication and update the sign-in endpoint  
B. Use Microsoft Entra entitlement management to govern external users  
C. Configure a Conditional Access policy  
D. Configure the Microsoft Entra provisioning service  
E. Configure Microsoft Entra join  
F. Configure Microsoft Entra Identity Protection  

**Correct Answer: B**

**Explanation:**

**Why B is correct:**

"Use Microsoft Entra entitlement management to govern external users" is the correct solution because:

1. **Single-Tenant App Limitation**: App1 is configured for single-tenant Microsoft Entra ID authentication, meaning it only authenticates users from the Contoso.com tenant. Users from Fabrikam.com cannot directly authenticate because they're in a different tenant.

2. **B2B Guest Access Required**: The solution requires inviting Fabrikam users as B2B guest users into the Contoso tenant. Once invited as guests, they appear in Contoso's directory and can authenticate to App1.

3. **Automated Guest Provisioning**: Entitlement Management automates the B2B invitation process:
   - Fabrikam users request access through MyAccess portal
   - Approval workflow processes the request
   - Guest account automatically created in Contoso tenant
   - App1 access automatically assigned
   - Guest invitation email sent to Fabrikam user

4. **Governance and Compliance**: Entitlement Management provides:
   - **Approval workflows** to control who gets access
   - **Time-bound access** with automatic expiration
   - **Access reviews** to periodically verify continued need
   - **Audit trail** for compliance and security

5. **Scalability**: Supports hundreds or thousands of external users without manual IT intervention.

**Implementation Approach:**

```yaml
Step 1: Create Connected Organization
  Name: "Fabrikam Division"
  Domain: fabrikam.com
  
Step 2: Create Access Package
  Name: "App1 Access - Fabrikam Users"
  Resources:
    - App1 (application)
    - App1-Users (security group)
  
Step 3: Configure Policy
  Who can request: Users from Fabrikam connected organization
  Approval: Required (Resource owner approval)
  Duration: 180 days with access review before expiration
  
Step 4: Publish Access Package
  Portal: https://myaccess.microsoft.com
  
Step 5: Users from Fabrikam Request Access
  - Submit request with justification
  - Receive approval from Contoso resource owner
  - Automatically provisioned as guest
  - Can authenticate to App1
```

**Why other options are incorrect:**

**Option A - Enable Microsoft Entra pass-through authentication and update the sign-in endpoint:**
- ❌ Pass-through authentication is for **on-premises directory synchronization**, not cross-tenant B2B access
- ❌ Allows on-premises AD users to authenticate using on-premises passwords
- ❌ Does not enable users from a separate Entra tenant to access single-tenant apps
- ❌ Fabrikam has its own Entra tenant; this is not an on-premises integration scenario

**Option C - Configure a Conditional Access policy:**
- ❌ Conditional Access **controls how** users access resources (MFA, device compliance, location)
- ❌ Does not **enable** B2B access or change the app's tenant scope
- ❌ Assumes users already exist in the tenant and can authenticate
- ❌ Cannot convert a single-tenant app to accept users from another tenant
- ❌ Useful for securing access, but does not solve the guest provisioning problem

**Option D - Configure the Microsoft Entra provisioning service:**
- ❌ Provisioning service is for **outbound synchronization** (Entra → external systems like SaaS apps)
- ❌ Does not enable **inbound B2B guest access** to single-tenant apps
- ❌ Used for scenarios like provisioning Entra users to ServiceNow, Workday, etc.
- ❌ Does not include approval workflows or governance features needed for external user access

**Option E - Configure Microsoft Entra join:**
- ❌ Entra join is for **device management**, not user authentication
- ❌ Joins devices (Windows 10/11, iOS, Android) to Entra ID
- ❌ Does not enable cross-tenant user authentication
- ❌ Not applicable to app authentication scenarios

**Option F - Configure Microsoft Entra Identity Protection:**
- ❌ Identity Protection is for **detecting and responding to identity-based risks**
- ❌ Detects risky sign-ins, compromised credentials, unusual behavior
- ❌ Does not enable B2B access or guest user provisioning
- ❌ Used for security risk management, not access governance

**Solution Architecture Diagram:**

```
Fabrikam Tenant (fabrikam.com)
  └─ User: john@fabrikam.com
            ↓
     [Requests Access via MyAccess Portal]
            ↓
     [Approval by Contoso Resource Owner]
            ↓
Contoso Tenant (contoso.com)
  ├─ Guest User: john_fabrikam.com#EXT#@contoso.onmicrosoft.com
  ├─ Access Package Assignment
  └─ App1 (Single-Tenant)
            ↓
     [Authenticates with Fabrikam Credentials]
            ↓
     [Accesses App1 as Guest in Contoso Tenant]
```

**Key Takeaway:**

For enabling users from one Entra tenant to authenticate to a single-tenant application in another tenant, **Microsoft Entra Entitlement Management** is the recommended Azure-native solution. It provides automated B2B guest provisioning, approval workflows, time-bound access, and comprehensive governance—all essential for secure cross-tenant collaboration.

**References:**
- [Microsoft Entra Entitlement Management Overview](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview)
- [What is B2B collaboration?](https://learn.microsoft.com/en-us/entra/external-id/what-is-b2b)
- [Configure Entitlement Management for B2B](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-external-users)

**Domain**: Design Identity, Governance, and Monitoring Solutions

---

## Additional Resources

### Microsoft Learn Documentation

- [Entitlement Management Overview](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-overview)
- [Plan an Entitlement Management Deployment](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-deployment-plan)
- [Create an Access Package](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-access-package-create)
- [Manage External Access](https://learn.microsoft.com/en-us/entra/id-governance/entitlement-management-external-users)
- [What is B2B Collaboration?](https://learn.microsoft.com/en-us/entra/external-id/what-is-b2b)

### PowerShell/Microsoft Graph

```powershell
# Connect to Microsoft Graph
Connect-MgGraph -Scopes "EntitlementManagement.ReadWrite.All"

# Create a Connected Organization
$org = New-MgEntitlementManagementConnectedOrganization -DisplayName "Fabrikam Inc." `
    -Description "External partner organization" `
    -State "configured" `
    -IdentitySources @(
        @{
            "@odata.type" = "#microsoft.graph.azureActiveDirectoryTenant"
            tenantId = "12345678-1234-1234-1234-123456789012"
            displayName = "Fabrikam"
        }
    )

# Create an Access Package
$package = New-MgEntitlementManagementAccessPackage -CatalogId $catalogId `
    -DisplayName "App1 Access for External Partners" `
    -Description "Provides access to App1 for Fabrikam users"

# Add Resource to Access Package
New-MgEntitlementManagementAccessPackageResourceRequest -AccessPackageId $package.Id `
    -RequestType "AdminAdd" `
    -CatalogId $catalogId `
    -Resource @{
        originId = $appId
        originSystem = "AadApplication"
    }

# Create Access Package Policy
$policy = New-MgEntitlementManagementAccessPackageAssignmentPolicy `
    -AccessPackageId $package.Id `
    -DisplayName "External User Policy" `
    -DurationInDays 90 `
    -RequestorSettings @{
        allowedRequestors = @(
            @{
                "@odata.type" = "#microsoft.graph.connectedOrganizationMembers"
                connectedOrganizationId = $org.Id
            }
        )
    } `
    -RequestApprovalSettings @{
        isApprovalRequiredForAdd = $true
        stages = @(
            @{
                durationInDays = 14
                primaryApprovers = @(
                    @{
                        "@odata.type" = "#microsoft.graph.singleUser"
                        userId = "resource-owner@contoso.com"
                    }
                )
            }
        )
    }
```

### MyAccess Portal

Users can access the MyAccess portal to:
- Browse available access packages
- Request access
- View current access
- Renew expiring access

```
URL: https://myaccess.microsoft.com
```

---

## Summary

Microsoft Entra Entitlement Management is the Azure-native solution for governing external user access and managing identity lifecycle at scale. Key takeaways:

✅ **B2B Collaboration**: Automates guest user invitation and provisioning  
✅ **Self-Service**: MyAccess portal reduces IT burden  
✅ **Approval Workflows**: Multi-stage approvals ensure governance  
✅ **Time-Bound Access**: Automatic expiration prevents access sprawl  
✅ **Access Reviews**: Periodic revalidation ensures compliance  
✅ **Delegated Administration**: Business owners manage their catalogs  
✅ **Audit Trail**: Complete visibility for compliance and security  
✅ **Cross-Tenant**: Enables single-tenant apps to support external users  

For scenarios requiring external user access to single-tenant applications, Microsoft Entra Entitlement Management with B2B collaboration is the recommended solution, providing automated guest provisioning with comprehensive governance and compliance controls.
