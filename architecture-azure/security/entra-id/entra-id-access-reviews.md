# Microsoft Entra ID Access Reviews

## Overview

Microsoft Entra ID Access Reviews is a feature within Microsoft Entra ID Identity Governance that enables organizations to efficiently manage group memberships, access to enterprise applications, and role assignments. Access reviews help ensure that only the right people have the right access to resources, reducing security risks and maintaining compliance.

---

## Table of Contents

1. [What Are Access Reviews?](#what-are-access-reviews)
2. [Key Features](#key-features)
3. [Use Cases](#use-cases)
4. [How Access Reviews Work](#how-access-reviews-work)
5. [Configuration Options](#configuration-options)
6. [Licensing Requirements](#licensing-requirements)
7. [Best Practices](#best-practices)
8. [Comparison with Alternative Solutions](#comparison-with-alternative-solutions)
9. [Exam Scenarios](#exam-scenarios)

---

## What Are Access Reviews?

Access reviews are systematic evaluations of user access to resources within your organization. They allow designated reviewers (such as managers, resource owners, or the users themselves) to attest whether users still need their current access permissions.

### Key Capabilities

- **Automated Review Cycles**: Schedule recurring reviews (monthly, quarterly, annually)
- **Email Notifications**: Automatically send review requests to designated reviewers
- **Auto-remediation**: Automatically revoke access if not approved during review
- **Audit Trail**: Maintain compliance records of all access decisions
- **Minimal Development**: Built-in feature requiring no custom code or scripting

---

## Key Features

### 1. Multiple Review Types

- **Group Membership Reviews**: Review who has access to security or Microsoft 365 groups
- **Application Access Reviews**: Review user access to enterprise applications
- **Azure Resource Role Reviews**: Review RBAC role assignments for Azure resources
- **Privileged Role Reviews**: Review assignments to privileged roles (via PIM)

### 2. Flexible Reviewer Options

- **Managers**: Automatic assignment based on organizational hierarchy
- **Resource Owners**: People responsible for specific resources
- **Self-Review**: Users review their own access
- **Designated Reviewers**: Specific individuals or groups

### 3. Automation Features

- **Auto-Apply Results**: Automatically remove access when not approved
- **Recommendations**: AI-powered suggestions based on sign-in activity
- **Escalation**: Forward to backup reviewers if primary doesn't respond
- **Recurrence**: Set up ongoing review cycles without manual intervention

---

## Use Cases

### 1. External Vendor Access Management

Regularly verify that external vendors, contractors, or partner developers still require access to your resources.

**Example**: Review Fabrikam developers' RBAC permissions to Application1 monthly.

### 2. Privileged Access Governance

Ensure users with elevated permissions (like Global Administrator) still need those roles.

### 3. Guest User Access

Review external guest users' access to shared resources and applications.

### 4. Compliance Requirements

Meet regulatory requirements for periodic access certification (SOX, HIPAA, ISO 27001).

### 5. Application Access Lifecycle

Ensure users who change roles or leave the organization have appropriate access updates.

---

## How Access Reviews Work

### Review Workflow

```
1. Create Review
   ↓
2. Configure Settings (frequency, reviewers, auto-actions)
   ↓
3. Review Starts → Email sent to reviewers
   ↓
4. Reviewers Approve/Deny access
   ↓
5. Review Ends
   ↓
6. Results Applied (manual or automatic)
   ↓
7. Access Modified (if denied or not reviewed)
   ↓
8. Next Review Cycle (if recurring)
```

### Decision Outcomes

| Reviewer Decision | Result |
|------------------|--------|
| **Approve** | User retains access |
| **Deny** | Access is removed (immediately or at review end) |
| **No Response** | Configurable: keep access, remove access, or apply recommendation |
| **System Recommendation** | Based on last sign-in activity (typically 90 days) |

---

## Configuration Options

### Review Schedule

- **One-time**: Single review at a specific time
- **Recurring**: Weekly, monthly, quarterly, semi-annually, or annually
- **Custom**: Define specific start and end dates

### Auto-Apply Settings

```yaml
Auto-apply results to resource: Enabled/Disabled

If reviewers don't respond:
  - Keep access
  - Remove access
  - Apply recommendations
  
Enable reviewer decision helpers:
  - Show last sign-in date
  - Show recommendation (inactive users)
```

### Notifications

- **Start notification**: Sent when review begins
- **Reminder notifications**: Periodic reminders during review period
- **Completion notification**: Sent to review creator when complete

---

## Licensing Requirements

Access Reviews require specific Microsoft licenses:

| Feature | Required License |
|---------|-----------------|
| **Basic Access Reviews** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **Access Reviews for Applications** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **Access Reviews for Groups** | Microsoft Entra ID P2 or Microsoft Entra ID Governance |
| **Privileged Access Reviews** | Microsoft Entra ID P2 + PIM |

**Note**: Microsoft 365 E5 includes Microsoft Entra ID P2.

---

## Best Practices

### 1. Start Small and Scale

Begin with high-risk resources or privileged roles before expanding to all access reviews.

### 2. Use Appropriate Reviewers

- **Managers**: Best for general access reviews
- **Resource Owners**: Best for application-specific access
- **Self-Review**: Supplement with manager approval for higher risk

### 3. Configure Auto-Remediation

Enable automatic access removal for unreviewed permissions to reduce administrative overhead.

### 4. Set Reasonable Review Periods

- **Privileged Access**: Monthly or quarterly
- **Standard Application Access**: Quarterly or semi-annually
- **Guest Users**: Quarterly

### 5. Enable Recommendations

Use system recommendations based on sign-in activity to help reviewers make informed decisions.

### 6. Monitor and Audit

Regularly review completion rates and decision patterns to ensure effectiveness.

---

## Comparison with Alternative Solutions

### Access Reviews vs. Custom Automation

| Aspect | Access Reviews | Azure Automation Runbooks |
|--------|---------------|--------------------------|
| **Development Effort** | Minimal (built-in UI) | High (custom scripting) |
| **Email Notifications** | Automatic | Custom code required |
| **Response Tracking** | Built-in | Custom database needed |
| **Auto-Remediation** | Native feature | Custom logic required |
| **Audit Trail** | Automatic | Must implement |
| **Maintenance** | Microsoft-managed | Self-managed |
| **Cost** | License-based | Compute + development time |

**Azure Automation Options:**
- `Get-AzRoleAssignment`: Retrieves role assignments but requires custom workflow logic
- `Get-AzureADUserAppRoleAssignment`: Gets app role assignments but needs full custom implementation

### Access Reviews vs. Privileged Identity Management (PIM)

| Feature | Access Reviews | PIM |
|---------|---------------|-----|
| **Purpose** | Periodic access verification | Just-in-time privileged access |
| **Scope** | All access types | Privileged roles only |
| **Review Type** | Regular scheduled reviews | Time-bound activations |
| **Best For** | Ongoing access governance | Elevated privilege management |

**Note**: PIM can be used *with* access reviews for privileged role assignments.

---

## Exam Scenarios

### Scenario 1: Verifying Developer Access to Custom Application

**Question:**

You have an Azure subscription that contains a custom application named Application1. Application1 was developed by an external company named Fabrikam, Ltd. Developers at Fabrikam were assigned role-based access control (RBAC) permissions to the Application1 components. All users are licensed for the Microsoft 365 E5 plan.

You need to recommend a solution to verify whether the Fabrikam developers still require permissions for Application1. The solution must meet the following requirements:

- To the manager of the developers, send a monthly email message that lists the access permissions to Application1.
- If the manager does not verify an access permission, automatically revoke that permission.
- Minimize development effort.

What should you recommend?

**Options:**

A. Create an Azure Automation runbook that runs the `Get-AzRoleAssignment` cmdlet  
B. Create an Azure Automation runbook that runs the `Get-AzureADUserAppRoleAssignment` cmdlet  
C. In Microsoft Entra Privileged Identity Management, create a custom role assignment for the Application1 resources  
D. In Microsoft Entra ID, create an access review of Application1

**Correct Answer: D**

**Explanation:**

**Why D is correct:**

"In Microsoft Entra ID, create an access review of Application1" is the correct solution because:

1. **Built-in Email Notifications**: Access reviews automatically send monthly email notifications to the designated reviewer (the manager) listing all access permissions that need verification.

2. **Automatic Revocation**: If the manager does not respond to the review, the system can be configured to automatically revoke unverified access, ensuring permissions are continuously monitored without manual intervention.

3. **Minimal Development Effort**: This is a built-in feature requiring no custom code, scripts, or workflow logic. Simply configure the review through the Azure portal or Microsoft Graph API.

4. **Licensing Available**: Microsoft 365 E5 includes Microsoft Entra ID P2, which provides access to Access Reviews functionality.

5. **Comprehensive Audit Trail**: All review decisions are logged for compliance and governance purposes.

**Why other options are incorrect:**

**Option A - Azure Automation with Get-AzRoleAssignment:**
- ❌ Requires custom scripting to retrieve role assignments
- ❌ Must build custom logic to send emails to managers
- ❌ Needs custom workflow to track manager responses
- ❌ Must implement custom remediation logic to revoke permissions
- ❌ Requires ongoing maintenance and monitoring
- ❌ Violates "minimize development effort" requirement

**Option B - Azure Automation with Get-AzureADUserAppRoleAssignment:**
- ❌ Also requires extensive custom development
- ❌ Must create entire notification and tracking system
- ❌ Needs custom database for response tracking
- ❌ Complex error handling and retry logic needed
- ❌ High development and operational overhead

**Option C - Privileged Identity Management (PIM) Custom Role Assignment:**
- ❌ PIM is designed for **just-in-time privileged access**, not periodic access reviews
- ❌ Does not provide automated monthly review emails to managers
- ❌ Not designed for reviewing standard RBAC permissions on custom applications
- ❌ Does not offer the same automatic review and cleanup workflow
- ❌ Better suited for time-bound role activations rather than ongoing access verification

**Solution Architecture:**

```yaml
Access Review Configuration:
  Name: "Fabrikam Developer Access Review - Application1"
  Review Type: "Azure Resource Roles"
  Scope: "Application1 RBAC Assignments"
  Reviewers: "Manager of each developer"
  Frequency: "Monthly"
  Duration: "7-14 days"
  
  Auto-apply results: Enabled
  If reviewers don't respond: "Remove access"
  
  Notifications:
    - Start: Email to manager with access list
    - Reminder: 3 days before end
    - Completion: Summary to review creator
```

**References:**
- [Access Reviews Overview](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Create an Access Review](https://learn.microsoft.com/en-us/entra/id-governance/create-access-review)
- [Manage User Access with Access Reviews](https://learn.microsoft.com/en-us/entra/id-governance/manage-user-access-with-access-reviews)

**Domain**: Design Identity, Governance, and Monitoring Solutions

---

## Additional Resources

### Microsoft Learn Documentation

- [What are access reviews?](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)
- [Plan an access review deployment](https://learn.microsoft.com/en-us/entra/id-governance/deploy-access-reviews)
- [Create an access review of groups and applications](https://learn.microsoft.com/en-us/entra/id-governance/create-access-review)
- [Complete an access review](https://learn.microsoft.com/en-us/entra/id-governance/complete-access-review)

### PowerShell/CLI Management

```powershell
# Microsoft Graph PowerShell commands for Access Reviews
Connect-MgGraph -Scopes "AccessReview.ReadWrite.All"

# Create an access review
New-MgIdentityGovernanceAccessReviewDefinition -BodyParameter @{
    displayName = "Monthly Application1 Access Review"
    scope = @{
        "@odata.type" = "#microsoft.graph.principalResourceMembershipsScope"
        principalScopes = @(...)
        resourceScopes = @(...)
    }
}

# Get access review decisions
Get-MgIdentityGovernanceAccessReviewDecision -AccessReviewScheduleDefinitionId $reviewId
```

---

## Summary

Microsoft Entra ID Access Reviews provide a comprehensive, low-effort solution for managing and governing user access to resources. Key takeaways:

✅ **Built-in feature** requiring minimal development effort  
✅ **Automated workflows** for notifications and remediation  
✅ **Flexible reviewer options** (managers, owners, self-review)  
✅ **Compliance-ready** with full audit trails  
✅ **Cost-effective** compared to custom automation solutions  
✅ **Scalable** across multiple resource types and applications  

For scenarios requiring periodic verification of access permissions with automatic remediation, Access Reviews are the recommended Azure-native solution.
