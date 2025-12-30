# Self-Service Password Reset (SSPR) in Microsoft Entra ID

## Overview

Self-Service Password Reset (SSPR) is a Microsoft Entra ID (formerly Azure Active Directory) feature that enables users to reset their passwords without contacting IT support. SSPR reduces helpdesk burden while empowering users to regain access to their accounts quickly and securely.

---

## Table of Contents

1. [What is SSPR?](#what-is-sspr)
2. [Enabling SSPR](#enabling-sspr)
   - [Assignment Scope](#assignment-scope)
   - [Supported Identity Types](#supported-identity-types)
3. [Configuration Requirements](#configuration-requirements)
4. [Authentication Methods](#authentication-methods)
5. [Licensing Requirements](#licensing-requirements)
6. [Best Practices](#best-practices)
7. [Exam Scenarios](#exam-scenarios)

---

## What is SSPR?

Self-Service Password Reset allows users to:
- Reset forgotten passwords
- Unlock accounts
- Change passwords without administrator intervention

**Key Benefits:**
- Reduces IT support workload
- Improves user productivity
- Enhances security through multi-factor verification
- Provides 24/7 availability for password recovery

---

## Enabling SSPR

### Assignment Scope

SSPR can be enabled for three different scopes in the Azure portal:

| Scope | Description | Use Case |
|-------|-------------|----------|
| **None** | SSPR is disabled for all users | Default state, or when SSPR is not needed |
| **Selected** | SSPR is enabled for specific groups | Pilot deployment or specific departments |
| **All** | SSPR is enabled for all users in the tenant | Organization-wide deployment |

### Supported Identity Types

**IMPORTANT:** SSPR can **ONLY** be assigned to **groups**, not to individual users.

#### Eligible Group Types

SSPR can be enabled for:

✅ **Security Groups**  
✅ **Microsoft 365 Groups** (formerly Office 365 Groups)

#### Not Eligible

❌ **Individual Users** - Cannot be assigned SSPR directly in the Azure portal  
❌ **Dynamic Groups** - While technically supported, best practice is to use static groups for SSPR

---

## Configuration Requirements

When configuring SSPR, administrators must specify:

### 1. Authentication Methods

Users must register authentication methods to verify their identity:

| Method | Description | Security Level |
|--------|-------------|----------------|
| **Mobile app notification** | Microsoft Authenticator push notification | High |
| **Mobile app code** | Time-based one-time password (TOTP) | High |
| **Email** | Verification code sent to alternate email | Medium |
| **Mobile phone** | SMS or voice call verification | Medium |
| **Office phone** | Voice call to desk phone | Medium |
| **Security questions** | Pre-configured questions and answers | Low |

**Recommendation:** Require at least **2 methods** for password reset to enhance security.

### 2. Number of Methods Required

Specify how many authentication methods users must provide:
- **Minimum:** 1 method
- **Recommended:** 2 methods for enhanced security

### 3. On-Premises Integration

For hybrid environments with on-premises Active Directory:
- Enable **Password Writeback** to synchronize password changes back to on-premises AD
- Requires **Microsoft Entra Connect** with writeback permissions

---

## Authentication Methods

### Recommended Configuration

```
Number of methods required to reset: 2
Methods available to users:
  ✅ Mobile app notification (Microsoft Authenticator)
  ✅ Mobile app code (TOTP)
  ✅ Email
  ✅ Mobile phone
  ⚠️ Security questions (disabled for enhanced security)
```

### Security Questions

If using security questions:
- Minimum **3 questions** required to register
- Minimum **3 questions** required to reset
- Pre-defined or custom questions available
- **Not recommended** for high-security environments

---

## Licensing Requirements

SSPR functionality varies by license tier:

| Feature | Free/Office 365 | Premium P1 | Premium P2 |
|---------|-----------------|------------|------------|
| **SSPR for cloud users** | ✅ | ✅ | ✅ |
| **SSPR for hybrid users** | ❌ | ✅ | ✅ |
| **Password writeback** | ❌ | ✅ | ✅ |
| **On-premises password reset** | ❌ | ✅ | ✅ |
| **Activity logs** | Limited | ✅ Full | ✅ Full |
| **Group-based SSPR assignment** | ✅ | ✅ | ✅ |

**Note:** Microsoft 365 Business licenses include SSPR for cloud-only accounts.

---

## Best Practices

### 1. **Use Groups for Assignment**
Always assign SSPR to security groups or Microsoft 365 groups, never to individual users. This ensures:
- Scalable management
- Easier auditing
- Consistent policy application

### 2. **Start with Pilot Group**
Begin with a pilot group before organization-wide rollout:
```
Selected → Pilot Security Group → Monitor → All users
```

### 3. **Require Multiple Authentication Methods**
Configure users to register at least 2 authentication methods to ensure they can reset passwords even if one method is unavailable.

### 4. **Enable Password Writeback for Hybrid Environments**
Ensure password changes sync back to on-premises Active Directory using Microsoft Entra Connect.

### 5. **User Communication and Training**
- Notify users about SSPR availability
- Provide registration instructions
- Share self-help documentation
- Monitor adoption metrics

### 6. **Disable Security Questions for High-Security Environments**
Security questions are the least secure method and should be avoided in environments with strict security requirements.

### 7. **Monitor SSPR Activity**
Regularly review:
- Registration rates
- Reset success/failure rates
- Authentication method usage
- Audit logs for suspicious activity

---

## Exam Scenarios

### Scenario 1: Enabling SSPR for Specific Groups

**Question:**  
You have an Azure subscription with the following Microsoft Entra identities:

| Name | Type |
|------|------|
| User1 | User |
| Group1 | Security group |
| Group2 | Microsoft 365 group |

You need to enable self-service password reset (SSPR). For which identities can you enable SSPR in the Azure portal?

**Options:**
- A) User1, Group1, and Group2
- B) Group1 and Group2 only
- C) User1 only
- D) Group1 only

**Correct Answer:** **B) Group1 and Group2 only**

---

#### Explanation

**Why Group1 and Group2?**
- SSPR can **only** be assigned to **groups** in Azure portal
- Both **Security Groups** (Group1) and **Microsoft 365 Groups** (Group2) are supported
- Individual users cannot be directly assigned SSPR policies

**Why NOT User1?**
- SSPR cannot be enabled for individual users directly
- Users gain SSPR access by being members of groups that have SSPR enabled

**Configuration Path:**
```
Azure Portal → Microsoft Entra ID → Password reset → Properties
  → Self-service password reset enabled: Selected
  → Select group: Group1 or Group2
```

**Important Notes:**
1. When "Selected" is chosen, you must specify one or more groups
2. Users in the selected groups can use SSPR
3. Users NOT in the selected groups cannot use SSPR (unless "All" is selected)
4. The "All" option enables SSPR for every user in the tenant

---

### Scenario 2: SSPR Assignment Limitation

**Question:**  
An administrator wants to enable SSPR for specific high-priority users (executives) without creating a group. Is this possible?

**Answer:** **No**

**Explanation:**
- SSPR must be assigned to groups
- To enable SSPR for specific individuals:
  1. Create a Security Group
  2. Add the target users to the group
  3. Assign SSPR to the group

**Workaround:**
```powershell
# Create a security group
New-AzureADGroup -DisplayName "SSPR-Executives" -MailEnabled $false -SecurityEnabled $true -MailNickName "SSPRExec"

# Add users to the group
Add-AzureADGroupMember -ObjectId <GroupObjectId> -RefObjectId <UserObjectId>

# Enable SSPR for the group in Azure Portal
```

---

### Scenario 3: Hybrid Environment SSPR

**Question:**  
Your organization has a hybrid identity environment with Microsoft Entra Connect. Users need to reset passwords that sync back to on-premises Active Directory. What must be configured?

**Answer:**
1. **Enable SSPR** for user groups
2. **Configure Password Writeback** in Microsoft Entra Connect
3. Ensure **Microsoft Entra ID Premium P1 or P2** licenses are assigned
4. Grant appropriate **permissions** for the Entra Connect service account in on-premises AD

**Configuration Steps:**
1. In Azure Portal: Enable SSPR for selected groups
2. In Entra Connect: Enable "Password writeback" feature
3. Verify connectivity between Entra ID and on-premises AD
4. Test password reset and verify synchronization

---

## Summary

| Aspect | Details |
|--------|---------|
| **Assignment** | Groups only (Security Groups or Microsoft 365 Groups) |
| **Individual Users** | Cannot be assigned directly |
| **Scope Options** | None, Selected, All |
| **Minimum Methods** | 1 (recommended: 2) |
| **Licensing** | Free for cloud-only, Premium P1+ for hybrid |
| **Writeback** | Requires Entra Connect + Premium P1+ |

---

## Related Documentation

- [Microsoft Entra Identity Governance](microsoft-entra-id-identity-governance.md)
- [Conditional Access Policies](conditional-access-policies.md)
- [Microsoft Entra Authentication Methods](entra-id-authentication-integration-scenarios.md)

---

## References

**Official Microsoft Documentation:**
- [Plan Microsoft Entra self-service password reset deployment](https://learn.microsoft.com/en-us/entra/identity/authentication/howto-sspr-deployment)
- [Enable SSPR in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/authentication/tutorial-enable-sspr)
- [SSPR Licensing Requirements](https://learn.microsoft.com/en-us/entra/identity/authentication/concept-sspr-licensing)
- [Configure Password Writeback](https://learn.microsoft.com/en-us/entra/identity/authentication/tutorial-enable-sspr-writeback)

**Domain:** Design Identity, Governance, and Monitoring Solutions
