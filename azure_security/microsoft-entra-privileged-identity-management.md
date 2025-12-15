# Microsoft Entra Privileged Identity Management (PIM)

## Overview

Microsoft Entra Privileged Identity Management (PIM) is a service within Microsoft Entra ID (formerly Azure AD) that enables you to manage, control, and monitor access to important resources in your organization. PIM provides just-in-time (JIT) privileged access to Azure resources, reducing the security risks associated with permanent administrative privileges.

---

## Table of Contents

1. [What is Privileged Identity Management?](#what-is-privileged-identity-management)
2. [Key Features](#key-features)
3. [Core Capabilities](#core-capabilities)
4. [Use Cases](#use-cases)
5. [How PIM Works](#how-pim-works)
6. [Configuration Options](#configuration-options)
7. [Licensing Requirements](#licensing-requirements)
8. [PIM vs Other Solutions](#pim-vs-other-solutions)
9. [Best Practices](#best-practices)
10. [Exam Scenarios](#exam-scenarios)

---

## What is Privileged Identity Management?

PIM is a feature of Microsoft Entra ID Identity Governance that helps organizations reduce security risks by:

- **Eliminating standing admin privileges**: Instead of granting permanent administrator access, PIM provides time-bound, approval-based privilege activation
- **Enforcing just-in-time access**: Users activate roles only when needed, for a limited duration
- **Requiring justification and approval**: Role activations can require business justification and approval workflows
- **Providing audit trails**: Complete logging and reporting of all privileged access activities

### Key Capabilities

- **Time-bound role assignments**: Temporary administrator access with configurable duration
- **Approval workflows**: Multi-stage approval for sensitive role activations
- **Multi-Factor Authentication (MFA) enforcement**: Require MFA for role activation
- **Justification requirements**: Users must provide business reasons for privilege escalation
- **Audit logging**: Comprehensive history of role activations and assignments
- **Access reviews integration**: Periodic reviews of privileged role assignments

---

## Key Features

### 1. Just-in-Time Privileged Access

PIM enables organizations to grant privileged access only when needed, rather than maintaining permanent elevated permissions.

**Benefits:**
- Reduces attack surface by minimizing standing privileges
- Limits exposure window for compromised accounts
- Provides better control over who can perform administrative actions
- Enables compliance with least-privilege security principles

### 2. Eligible Role Assignments

Instead of permanent (active) assignments, PIM supports **eligible** assignments where users can activate roles when needed.

```
Permanent Assignment (Traditional):
User → Always has Admin rights → High Security Risk

Eligible Assignment (PIM):
User → Request Activation → Approval (optional) → Time-Limited Admin Access → Auto-Revocation
```

### 3. Approval Workflows

Organizations can configure multi-stage approval processes for sensitive role activations:

- **Self-activation**: User activates without approval (with MFA/justification)
- **Manager approval**: Requires manager's approval before activation
- **Custom approvers**: Designated approvers for specific roles
- **Multi-stage approval**: Multiple approvers in sequence

### 4. Activation Requirements

Organizations can enforce various requirements when users activate privileged roles:

- **Multi-Factor Authentication (MFA)**: Require MFA before activation
- **Business Justification**: Mandatory reason/ticket number for activation
- **Maximum Duration**: Configurable time limits (1-24 hours typical)
- **Notification**: Alerts sent to security teams upon activation

---

## Core Capabilities

### Resource Types Supported by PIM

| Resource Type | Description |
|---------------|-------------|
| **Microsoft Entra Roles** | Directory roles (Global Admin, User Admin, etc.) |
| **Azure Resource Roles** | RBAC roles for subscriptions, resource groups, resources |
| **Privileged Access Groups** | Groups with elevated permissions |

### Role Assignment Types

| Assignment Type | Activation Required | Duration | Use Case |
|----------------|---------------------|----------|----------|
| **Eligible** | Yes | Time-bound or permanent eligibility | Recommended for most admin roles |
| **Active** | No | Permanent or time-bound | Service accounts, break-glass accounts |
| **Activated** | N/A (already activated) | Time-bound (hours) | Current active session from eligible role |

---

## Use Cases

### 1. Quality Assurance Department: Temporary Admin Access

**Scenario:**
The Quality Assurance department needs to create and configure additional web and API applications in a test environment, but should not have permanent administrator access.

**Solution:**
Use Microsoft Entra Privileged Identity Management to grant eligible role assignments for Azure resource management roles (e.g., Contributor, Owner). QA team members can activate these roles when needed for testing, with time-limited access and full audit trails.

**Benefits:**
- ✅ Just-in-time access only when needed
- ✅ Approval workflows for privilege escalation
- ✅ Audit logging for compliance
- ✅ Automatic revocation after time limit
- ✅ No permanent elevated rights

**Configuration:**
```yaml
PIM Role Assignment:
  Role: Contributor
  Scope: Test Resource Group
  Assignment Type: Eligible
  
  Activation Settings:
    - Maximum Duration: 8 hours
    - Require MFA: Yes
    - Require Justification: Yes
    - Require Approval: Yes (Manager)
    
  Notification:
    - Alert security team on activation
    - Send expiration reminder 1 hour before
```

### 2. Break-Glass Account Management

**Scenario:**
Maintain emergency access accounts with Global Administrator privileges that are only used in critical scenarios.

**Solution:**
- Create break-glass accounts with eligible Global Administrator role
- Require approval from multiple senior leaders
- Enforce MFA and comprehensive logging
- Regular access reviews to ensure accounts remain secure

### 3. Third-Party Vendor Access

**Scenario:**
External consultants need temporary access to Azure resources for a specific project.

**Solution:**
- Grant eligible roles with expiration dates aligned to contract duration
- Require business justification for each activation
- Implement approval workflows
- Automatic revocation when contract ends

### 4. Azure Resource Management

**Scenario:**
Developers occasionally need to modify production infrastructure but shouldn't have permanent access.

**Solution:**
- Grant eligible Contributor or Owner roles at resource group level
- Require approval from operations team
- Limit activation duration to 4 hours
- Audit all changes made during activated sessions

---

## How PIM Works

### Step-by-Step Activation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIM Activation Workflow                       │
└─────────────────────────────────────────────────────────────────┘

1. User has Eligible Role Assignment
   └─> User: "QA Engineer"
   └─> Role: "Contributor" (Test Environment)
   └─> Status: Eligible (not active)

2. User Requests Activation
   └─> Navigate to Azure Portal → PIM → My Roles
   └─> Select role and click "Activate"
   └─> Provide justification: "Testing API deployment - Ticket #12345"

3. System Validates Requirements
   └─> MFA Check ✓
   └─> Justification Provided ✓
   └─> Duration: 4 hours (within max limit) ✓

4. Approval Workflow (if configured)
   └─> Request sent to Manager
   └─> Manager reviews justification
   └─> Manager approves/denies request
   └─> User notified of decision

5. Role Activation
   └─> Role becomes Active for specified duration
   └─> User can perform privileged operations
   └─> All actions logged for audit

6. Automatic Deactivation
   └─> After 4 hours, role automatically revoked
   └─> User returns to standard permissions
   └─> Activation summary sent to security team

7. Audit Trail
   └─> Who activated the role
   └─> When it was activated
   └─> Why (justification)
   └─> Approval chain
   └─> Actions performed during active session
   └─> When it was deactivated
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     Microsoft Entra ID Tenant                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │     Privileged Identity Management (PIM)               │    │
│  │                                                         │    │
│  │  ┌───────────────────┐      ┌──────────────────────┐  │    │
│  │  │  Eligible Roles   │      │  Approval Workflows  │  │    │
│  │  │  - Global Admin   │      │  - Manager Approval  │  │    │
│  │  │  - Contributor    │      │  - Security Approval │  │    │
│  │  │  - Owner          │      │  - Auto-approval     │  │    │
│  │  └───────────────────┘      └──────────────────────┘  │    │
│  │                                                         │    │
│  │  ┌───────────────────┐      ┌──────────────────────┐  │    │
│  │  │  Activation Logs  │      │  Access Reviews      │  │    │
│  │  │  - Who            │      │  - Quarterly reviews │  │    │
│  │  │  - When           │      │  - Role validation   │  │    │
│  │  │  - Why            │      │  - Cleanup           │  │    │
│  │  └───────────────────┘      └──────────────────────┘  │    │
│  └────────────────────────────────────────────────────────┘    │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │   Azure Resources    │
                │  - Subscriptions     │
                │  - Resource Groups   │
                │  - Web Apps          │
                │  - Key Vaults        │
                └──────────────────────┘
```

---

## Configuration Options

### Role Settings in PIM

For each role, administrators can configure:

#### Activation Settings
- **Maximum activation duration**: 1-24 hours
- **Require multi-factor authentication**: Yes/No
- **Require justification**: Yes/No
- **Require approval**: Yes/No
- **Approver selection**: Specific users/groups

#### Assignment Settings
- **Allow permanent eligible assignment**: Yes/No
- **Expire eligible assignment after**: X days/months
- **Allow permanent active assignment**: Yes/No (not recommended)
- **Expire active assignment after**: X days/months

#### Notification Settings
- **Send notifications when members activate**
- **Send notifications to approvers**
- **Send notifications when activated roles expire**

### Example Role Configuration

```yaml
Role: Contributor
Scope: Production Resource Group
Type: Azure Resource Role

Activation:
  Maximum Duration: 4 hours
  Require MFA: Yes
  Require Justification: Yes
  Require Approval: Yes
  Approvers:
    - Operations Manager
    - Security Team Lead

Assignment:
  Allow Permanent Eligible: No
  Eligible Assignment Duration: 90 days
  Allow Permanent Active: No

Notifications:
  On Activation:
    - Alert: security-team@company.com
    - Alert: resource-owner@company.com
  On Approval Required:
    - Alert: approvers
  On Expiration:
    - Reminder: User (1 hour before)
```

---

## Licensing Requirements

| Feature | License Required |
|---------|-----------------|
| **PIM for Microsoft Entra Roles** | Microsoft Entra ID P2 or Microsoft 365 E5 |
| **PIM for Azure Resource Roles** | Microsoft Entra ID P2 or Microsoft 365 E5 |
| **PIM for Groups** | Microsoft Entra ID P2 or Microsoft 365 E5 |

**Note**: Users who activate roles using PIM must have an appropriate license, but users who only approve requests or review access do not require licenses.

---

## PIM vs Other Solutions

### PIM vs Access Reviews

| Feature | PIM | Access Reviews |
|---------|-----|----------------|
| **Purpose** | Just-in-time privileged access | Periodic access verification |
| **Access Pattern** | On-demand activation | Ongoing access with periodic review |
| **Scope** | Privileged roles only | All access types (roles, groups, apps) |
| **Duration** | Time-bound (hours) | Permanent until review |
| **Best For** | Elevated privilege management | Regular access governance |
| **Activation** | User-initiated, approval-based | N/A (review-based) |

**Note**: PIM and Access Reviews can be used together. Access Reviews can verify whether users still need their *eligible* PIM role assignments.

### PIM vs Azure RBAC

| Feature | Azure RBAC | PIM |
|---------|-----------|-----|
| **Assignment Type** | Permanent (active) | Eligible + time-bound activation |
| **Activation** | Immediate | On-demand with approval |
| **Audit Detail** | Basic activity logs | Detailed activation history |
| **Security Posture** | Higher risk (standing privileges) | Lower risk (JIT access) |
| **Use Case** | Standard resource access | Privileged/sensitive operations |

### PIM vs Managed Identity

| Feature | Managed Identity | PIM |
|---------|-----------------|-----|
| **Identity Type** | Service identity (workload) | Human user identity |
| **Purpose** | Application-to-Azure authentication | Human just-in-time privilege escalation |
| **Credentials** | Automatically managed by Azure | User credentials + MFA |
| **Use Case** | App Service → Key Vault access | Admin → temporary elevated rights |

**Key Difference**: Managed Identity grants Azure resources (apps, functions) automatic authentication to other services **without credentials**. It does NOT grant human administrators temporary access to manage Azure resources.

---

## Best Practices

### 1. Minimize Permanent Assignments

✅ **Do**: Use eligible assignments for most administrative roles  
❌ **Don't**: Grant permanent active assignments unless absolutely necessary

**Exception**: Break-glass accounts may need active assignments but should be monitored closely.

### 2. Configure Appropriate Activation Duration

- **Short-lived tasks** (configuration changes): 1-2 hours
- **Investigation/troubleshooting**: 4-8 hours
- **Project work**: 8-24 hours
- **Never**: Permanent activation

### 3. Require Multi-Factor Authentication

✅ **Always** require MFA for privileged role activation  
❌ **Never** allow activation without MFA for sensitive roles

### 4. Implement Approval Workflows for Sensitive Roles

Roles that should require approval:
- Global Administrator
- Privileged Role Administrator
- Security Administrator
- Contributor/Owner on production resources
- Custom roles with dangerous permissions

### 5. Regular Access Reviews

- Review eligible role assignments quarterly
- Remove unnecessary eligible assignments
- Validate that users still require privileged access
- Document business justification for continued access

### 6. Monitor and Alert

Configure alerts for:
- High-risk role activations (Global Admin, etc.)
- Multiple failed activation attempts
- Activations outside business hours
- Bulk role activations

### 7. Justification and Documentation

- Require meaningful justifications (ticket numbers, change requests)
- Review activation history regularly
- Correlate activations with change management processes

### 8. Combine with Other Security Controls

- **Conditional Access**: Restrict privileged access to trusted locations/devices
- **Identity Protection**: Monitor for risky sign-ins before allowing activation
- **Azure Policy**: Prevent configuration changes that bypass PIM
- **Privileged Access Workstations (PAW)**: Require dedicated admin workstations

---

## Exam Scenarios

### Scenario 1: Quality Assurance Temporary Admin Access

**Question:**

You have several Azure App Service web apps that use Azure Key Vault to store data encryption keys. Several departments have the following requests to support the web app:

| Department | Request |
|------------|---------|
| Quality Assurance | Create and configure additional web and API applications in the test environment without permanent administrator access |

You need to recommend the appropriate Azure service for the Quality Assurance department request.

Which Azure service should you recommend?

**Options:**

A. Azure Managed Identity  
B. Microsoft Entra Connect  
C. Microsoft Entra Identity Protection  
D. Microsoft Entra Privileged Identity Management

**Correct Answer: D - Microsoft Entra Privileged Identity Management**

**Explanation:**

**Why D is correct:**

**Microsoft Entra Privileged Identity Management (PIM)** is correct because it enables just-in-time (JIT) privileged access to Azure resources. It allows you to assign temporary administrator access based on approval workflows, which is exactly what the Quality Assurance department needs to create and configure additional web and API applications in the test environment without having permanent elevated rights.

**Key Features that Address the Requirement:**
1. **Eligible Role Assignments**: QA users can be made eligible for Contributor or Owner roles on the test resource group
2. **Time-Bound Activation**: When QA needs to create resources, they activate the role for a limited duration (e.g., 4-8 hours)
3. **Approval Workflows**: Can require manager or security team approval before granting access
4. **Automatic Revocation**: After the activation period expires, privileges are automatically removed
5. **Audit Logging**: Complete history of who activated privileges, when, and why
6. **No Permanent Access**: QA never has standing administrator privileges, reducing security risk

**Practical Implementation:**

```yaml
PIM Configuration for QA Department:
  
  Role Assignment:
    Role: Contributor
    Scope: Test Environment Resource Group
    Type: Eligible (not permanent)
    Expiration: None (eligible indefinitely, but activation is temporary)
  
  Activation Settings:
    Maximum Duration: 8 hours
    Require MFA: Yes
    Require Justification: Yes
    Require Approval: Yes
    Approvers:
      - QA Manager
      - Operations Lead
  
  Usage Flow:
    1. QA engineer needs to test new API
    2. Navigates to PIM and activates Contributor role
    3. Provides justification: "Testing payment API - Ticket #5678"
    4. QA manager receives approval request
    5. Upon approval, engineer has 8 hours of Contributor access
    6. After 8 hours, access automatically revoked
    7. Full audit trail maintained for compliance
```

**Why other options are incorrect:**

**Option A - Azure Managed Identity:**
- ❌ Managed Identity is used for granting **Azure resources** (like web apps or functions) the ability to access other services (e.g., Key Vault) without credentials
- ❌ It does NOT grant **human administrators** temporary access to manage Azure resources
- ❌ Managed Identity is for service-to-service authentication, not user privilege management
- ❌ Cannot provide time-bound, approval-based access for QA personnel

**Example of Managed Identity use case (NOT the requirement):**
```
Web App → Uses Managed Identity → Accesses Key Vault
(No credentials needed, automatic authentication)
```

**Option B - Microsoft Entra Connect:**
- ❌ Entra Connect is used to **synchronize on-premises Active Directory identities** with Microsoft Entra ID
- ❌ It does NOT facilitate privileged access or time-bound role assignments
- ❌ It's an identity synchronization tool, not an access management tool
- ❌ Completely unrelated to temporary administrator access

**Option C - Microsoft Entra Identity Protection:**
- ❌ Identity Protection is focused on **detecting and responding to identity-based risks** (e.g., sign-in risk, user risk, compromised accounts)
- ❌ It does NOT grant or manage administrator access
- ❌ It's a threat detection and risk mitigation tool, not a privilege management solution
- ❌ Cannot provide just-in-time role activation

**Comparison Table:**

| Solution | Grants Temporary Admin Access? | Approval Workflows? | For Human Users? | Audit Logging? |
|----------|-------------------------------|---------------------|------------------|----------------|
| **PIM** ✓ | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Comprehensive |
| Managed Identity | ❌ No (service identity) | ❌ No | ❌ No (for resources) | Limited |
| Entra Connect | ❌ No (sync only) | ❌ No | ❌ N/A | ❌ Not applicable |
| Identity Protection | ❌ No (risk detection) | ❌ No | ✅ Yes | ✅ Risk events only |

**Reference(s):**
- [PIM Configuration Overview](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Activate PIM Roles](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-activate-role)
- [PIM Capabilities](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure#what-does-it-do)
- [Identity Protection Overview](https://learn.microsoft.com/en-us/entra/id-protection/overview-identity-protection)

**Domain**: Design Identity, Governance, and Monitoring Solutions

---

### Scenario 2: PIM vs Access Reviews

**Question:**

An organization needs to implement a solution where developers can elevate their privileges to Owner role on production resource groups for emergency fixes. Access should be:
- Time-limited to 2 hours maximum
- Require approval from the operations manager
- Automatically revoked after the time limit
- Fully audited

Which solution should you recommend?

**Options:**

A. Microsoft Entra ID Access Reviews  
B. Microsoft Entra Privileged Identity Management (PIM)  
C. Azure Automation with RBAC role assignment scripts  
D. Azure Policy with deny assignments

**Correct Answer: B - Microsoft Entra Privileged Identity Management (PIM)**

**Explanation:**

This scenario requires **just-in-time** privilege escalation with approval, time-bounds, and automatic revocation - which is exactly what PIM provides.

**Why other options are incorrect:**

- **Access Reviews (A)**: Designed for periodic verification of existing access, not on-demand time-bound activation
- **Azure Automation (C)**: Would require significant custom development and doesn't provide built-in approval workflows
- **Azure Policy (D)**: Used to enforce compliance rules, not to grant temporary elevated access

---

### Scenario 3: Guest User Access Reviews (Identity Governance vs PIM)

**Question:**

Refer to the Contoso Ltd. case study:

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

**Microsoft Entra ID Identity Governance** is correct because the requirement describes a **recertification process** or **access review**, which is a core feature of Identity Governance. It enables organizations to:

- ✅ **Regularly review and validate user access** — especially for guest users (Fabrikam)
- ✅ **Ensure access is removed** if it's no longer needed
- ✅ **Minimize development effort** — built-in and policy-driven solution
- ✅ **Delegate reviews** to external managers (Fabrikam account manager)

**Access Reviews Configuration for This Scenario:**

```yaml
Access Review Configuration:
  Review Name: "Monthly Fabrikam Guest Access Review"
  Scope: Guest users with access to App1
  
  Reviewers:
    Type: External (Fabrikam Account Manager)
    
  Schedule:
    Frequency: Monthly
    Duration: 7 days to complete review
    
  Upon Completion:
    Auto-apply results: Yes
    If reviewer doesn't respond: Remove access
    
  Actions:
    Approved: Maintain guest access
    Denied: Remove guest account permissions
```

**Why other options are incorrect:**

**Option B - Microsoft Entra ID Identity Protection:**
- ❌ Identity Protection focuses on **risk-based conditional access**
- ❌ Detects and responds to **compromised identities** or **sign-in risk events**
- ❌ Does NOT perform access reviews or guest account lifecycle management
- ❌ Wrong purpose: threat detection vs. access governance

**Option C - Microsoft Entra Privileged Identity Management (PIM):**
- ❌ PIM is used for managing **elevated (privileged) role assignments**
- ❌ Provides **just-in-time** access for administrative tasks
- ❌ Does NOT perform **monthly access reviews** of guest users
- ❌ Wrong scope: privilege escalation vs. regular access review

**Option D - Azure Automation:**
- ❌ Would require **custom development and scripting**
- ❌ Contradicts the requirement to **minimize development efforts**
- ❌ No built-in reviewer workflows or approval processes
- ❌ Wrong approach: manual scripting vs. built-in governance

**Key Distinction - When to Use Each Service:**

| Requirement | Correct Solution |
|-------------|------------------|
| "Monthly review of who has access" | **Access Reviews (Identity Governance)** |
| "Remove access if no longer needed" | **Access Reviews (Identity Governance)** |
| "Temporary admin access when needed" | **PIM** |
| "Detect risky sign-ins" | **Identity Protection** |
| "Minimize development effort" | **Built-in services (not Automation)** |

**Visual Comparison:**

```
┌─────────────────────────────────────────────────────────────────┐
│              Identity Governance vs PIM                          │
└─────────────────────────────────────────────────────────────────┘

Access Reviews (Identity Governance):
  Who has access? → Monthly Review → Keep or Remove
  └─> Fabrikam guests → Account manager reviews → Remove if not needed

PIM (Privileged Identity Management):
  Need admin access? → Request Activation → Time-Limited Access
  └─> Developer → Approves → 4 hours of Contributor role → Auto-revoke
```

**Reference(s):**
- [Access Reviews Overview](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Identity Governance Overview](https://learn.microsoft.com/en-us/entra/id-governance/identity-governance-overview)
- [PIM Configuration](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Azure Automation Introduction](https://learn.microsoft.com/en-us/azure/automation/automation-intro)

**Domain**: Design Identity, Governance, and Monitoring Solutions

---

### Scenario 4: When NOT to Use PIM

**Question:**

An Azure Function app needs to read secrets from Azure Key Vault. The function runs continuously and must access Key Vault without user intervention. What should you use?

**Options:**

A. Microsoft Entra Privileged Identity Management  
B. System-Assigned Managed Identity  
C. User-Assigned Managed Identity  
D. Service Principal with certificate authentication

**Correct Answer: B or C - Managed Identity**

**Explanation:**

This is a **service-to-service** authentication scenario, not a human administrator privilege escalation scenario.

- **PIM (A)**: ❌ Incorrect - PIM is for human users needing temporary elevated access, not for automated service authentication
- **Managed Identity (B/C)**: ✅ Correct - Provides automatic credential-free authentication for Azure resources
- **Service Principal (D)**: ✅ Also valid, but Managed Identity is preferred for Azure resources

**Key Distinction:**
- Use **PIM** when: Human administrators need temporary privileged access
- Use **Managed Identity** when: Azure resources (apps, functions) need to authenticate to other Azure services

---

## Additional Resources

### Microsoft Learn Documentation

- [What is Privileged Identity Management?](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)
- [Configure PIM for Azure resources](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-configure-role-settings)
- [Activate PIM roles](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-activate-role)
- [Approve or deny PIM activation requests](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-approval-workflow)
- [PIM deployment plan](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-deployment-plan)

### PowerShell/CLI Management

```powershell
# Microsoft Graph PowerShell for PIM
Connect-MgGraph -Scopes "RoleManagement.ReadWrite.Directory"

# List eligible role assignments
Get-MgRoleManagementDirectoryRoleEligibilitySchedule

# Create an eligible role assignment
New-MgRoleManagementDirectoryRoleEligibilityScheduleRequest -BodyParameter @{
    action = "adminAssign"
    justification = "Temporary access for project"
    roleDefinitionId = "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3" # Contributor
    principalId = "user-object-id"
    directoryScopeId = "/subscriptions/sub-id/resourceGroups/rg-name"
    scheduleInfo = @{
        expiration = @{
            type = "afterDuration"
            duration = "PT8H"  # 8 hours
        }
    }
}

# Activate a role
New-MgRoleManagementDirectoryRoleAssignmentScheduleRequest -BodyParameter @{
    action = "selfActivate"
    justification = "Emergency production fix - Ticket #12345"
    roleDefinitionId = "role-id"
    principalId = "user-object-id"
    directoryScopeId = "/subscriptions/sub-id"
    scheduleInfo = @{
        expiration = @{
            type = "afterDuration"
            duration = "PT4H"  # 4 hours
        }
    }
}
```

---

## Summary

Microsoft Entra Privileged Identity Management is the recommended solution for managing privileged access in Azure. Key takeaways:

✅ **Just-in-time access** - Activate roles only when needed  
✅ **Time-bound activations** - Automatic revocation after defined duration  
✅ **Approval workflows** - Multi-stage approval for sensitive operations  
✅ **MFA enforcement** - Require strong authentication for privilege escalation  
✅ **Comprehensive auditing** - Full trail of who, when, why, and what  
✅ **Reduces attack surface** - Minimizes standing privileges  
✅ **Compliance-ready** - Supports least-privilege principle and governance requirements  

**When to use PIM:**
- Human administrators need temporary elevated access
- Privileged operations should require approval
- Audit trails are required for compliance
- Reducing standing privileges is a security priority

**When NOT to use PIM:**
- Service-to-service authentication (use Managed Identity)
- Permanent, non-privileged access (use standard RBAC)
- Periodic access reviews (use Access Reviews, though they can complement PIM)
- Identity synchronization (use Entra Connect)
- Risk detection (use Identity Protection)

PIM is a cornerstone of zero-trust security architectures and should be implemented for all privileged Azure resource access.
