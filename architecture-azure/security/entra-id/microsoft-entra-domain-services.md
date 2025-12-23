# Microsoft Entra Domain Services

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. What is Microsoft Entra Domain Services?](#2-what-is-microsoft-entra-domain-services)
  - [2.1 Key Features](#21-key-features)
  - [2.2 How It Differs from On-Premises AD DS](#22-how-it-differs-from-on-premises-ad-ds)
- [3. Architecture and Components](#3-architecture-and-components)
  - [3.1 Managed Domain Controllers](#31-managed-domain-controllers)
  - [3.2 Synchronization Flow](#32-synchronization-flow)
  - [3.3 Network Integration](#33-network-integration)
- [4. Supported Protocols and Services](#4-supported-protocols-and-services)
  - [4.1 LDAP (Lightweight Directory Access Protocol)](#41-ldap-lightweight-directory-access-protocol)
  - [4.2 Kerberos Authentication](#42-kerberos-authentication)
  - [4.3 NTLM Authentication](#43-ntlm-authentication)
  - [4.4 Domain Join](#44-domain-join)
  - [4.5 Group Policy](#45-group-policy)
- [5. Use Cases and Scenarios](#5-use-cases-and-scenarios)
  - [5.1 Migrating Legacy Applications to Azure](#51-migrating-legacy-applications-to-azure)
  - [5.2 Lift-and-Shift Migrations](#52-lift-and-shift-migrations)
  - [5.3 Azure Virtual Desktop](#53-azure-virtual-desktop)
  - [5.4 Hybrid Identity Scenarios](#54-hybrid-identity-scenarios)
- [6. Identity Solutions Comparison](#6-identity-solutions-comparison)
  - [6.1 Entra Domain Services vs Self-Managed AD DS](#61-entra-domain-services-vs-self-managed-ad-ds)
  - [6.2 Entra Domain Services vs Microsoft Entra ID](#62-entra-domain-services-vs-microsoft-entra-id)
  - [6.3 Entra Domain Services vs Application Proxy](#63-entra-domain-services-vs-application-proxy)
- [7. Deployment and Configuration](#7-deployment-and-configuration)
  - [7.1 Prerequisites](#71-prerequisites)
  - [7.2 Deployment Steps](#72-deployment-steps)
  - [7.3 Network Configuration](#73-network-configuration)
  - [7.4 DNS Configuration](#74-dns-configuration)
- [8. Security and Access Control](#8-security-and-access-control)
  - [8.1 Authentication Methods](#81-authentication-methods)
  - [8.2 Password Hash Synchronization](#82-password-hash-synchronization)
  - [8.3 Security Best Practices](#83-security-best-practices)
  - [8.4 Network Security Groups](#84-network-security-groups)
- [9. Administration and Management](#9-administration-and-management)
  - [9.1 Administrative Accounts](#91-administrative-accounts)
  - [9.2 Group Policy Management](#92-group-policy-management)
  - [9.3 Monitoring and Diagnostics](#93-monitoring-and-diagnostics)
  - [9.4 Backup and Disaster Recovery](#94-backup-and-disaster-recovery)
- [10. Limitations and Constraints](#10-limitations-and-constraints)
  - [10.1 Schema Extensions](#101-schema-extensions)
  - [10.2 LDAP Write Operations](#102-ldap-write-operations)
  - [10.3 Trust Relationships](#103-trust-relationships)
  - [10.4 Forest Functional Level](#104-forest-functional-level)
- [11. Pricing and Licensing](#11-pricing-and-licensing)
  - [11.1 SKU Options](#111-sku-options)
  - [11.2 Cost Considerations](#112-cost-considerations)
- [12. Migration Scenarios](#12-migration-scenarios)
  - [12.1 Migrating LDAP Applications](#121-migrating-ldap-applications)
  - [12.2 Domain Join Migration](#122-domain-join-migration)
  - [12.3 Application Compatibility](#123-application-compatibility)
- [13. Troubleshooting Common Issues](#13-troubleshooting-common-issues)
- [14. Exam Scenarios and Practice Questions](#14-exam-scenarios-and-practice-questions)
  - [14.1 Scenario: LDAP Application Migration](#141-scenario-ldap-application-migration)
  - [14.2 Scenario: Choosing Identity Solutions](#142-scenario-choosing-identity-solutions)
  - [14.3 Scenario: Hybrid Identity Architecture](#143-scenario-hybrid-identity-architecture)
- [15. Best Practices](#15-best-practices)
- [16. Reference Links](#16-reference-links)

---

## 1. Introduction

**Microsoft Entra Domain Services** (formerly Azure AD Domain Services) is a managed domain service that provides Active Directory-compatible services in Azure without the need to deploy, manage, or patch domain controllers.

This service is particularly valuable for organizations that:
- Need to migrate legacy applications to Azure that depend on traditional AD authentication
- Want to eliminate on-premises infrastructure dependencies
- Require LDAP, Kerberos, or NTLM authentication in the cloud
- Need to domain-join Azure VMs without maintaining domain controllers

---

## 2. What is Microsoft Entra Domain Services?

Microsoft Entra Domain Services provides managed domain services such as domain join, group policy, LDAP, and Kerberos/NTLM authentication that are fully compatible with Windows Server Active Directory.

### 2.1 Key Features

| Feature | Description |
|---------|-------------|
| **LDAP Support** | Full LDAP read support, limited write operations |
| **Kerberos & NTLM** | Complete authentication protocol support |
| **Domain Join** | Join Azure VMs (Windows/Linux) to managed domain |
| **Group Policy** | Manage domain-joined machines with GPOs |
| **Managed Service** | Microsoft handles domain controllers, patching, backups |
| **High Availability** | Two domain controllers deployed automatically |
| **Automatic Sync** | One-way sync from Microsoft Entra ID |

### 2.2 How It Differs from On-Premises AD DS

```plaintext
┌─────────────────────────────────────────────────────────────────┐
│                    Traditional AD DS                            │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Full schema control                                          │
│ ✓ Forest/domain trusts                                         │
│ ✓ Complete LDAP write access                                   │
│ ✓ Custom OU structures                                         │
│ ✗ Manual deployment and maintenance                            │
│ ✗ You manage domain controllers                                │
│ ✗ You handle patching and backups                              │
│ ✗ Complex disaster recovery planning                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Microsoft Entra Domain Services                    │
├─────────────────────────────────────────────────────────────────┤
│ ✓ Microsoft manages domain controllers                         │
│ ✓ Automatic patching and updates                               │
│ ✓ Built-in high availability                                   │
│ ✓ Automatic backups                                            │
│ ✓ Syncs with Microsoft Entra ID                                │
│ ✗ No schema extensions                                         │
│ ✗ Limited LDAP write operations                                │
│ ✗ No forest trusts                                             │
│ ✗ Fixed forest functional level                                │
└─────────────────────────────────────────────────────────────────┘
```

**Key Differences:**

| Aspect | On-Premises AD DS | Entra Domain Services |
|--------|-------------------|----------------------|
| **Deployment** | Manual VM setup | Fully managed |
| **Maintenance** | You manage | Microsoft manages |
| **High Availability** | You configure | Built-in (2 DCs) |
| **Backups** | You implement | Automatic |
| **Schema** | Full control | Read-only |
| **Trusts** | Full support | Not supported |
| **Cost** | Infrastructure + licenses | Service fee |

---

## 3. Architecture and Components

### 3.1 Managed Domain Controllers

When you create an Entra Domain Services managed domain, Azure deploys two domain controllers (called "replicas") in your selected region.

```plaintext
┌──────────────────────────────────────────────────────────────┐
│              Microsoft Entra Domain Services                  │
│                    Managed Domain                             │
│                                                               │
│  ┌─────────────────────┐      ┌─────────────────────┐       │
│  │   Domain Controller │      │   Domain Controller │       │
│  │      (Replica 1)    │◄────►│      (Replica 2)    │       │
│  │                     │      │                     │       │
│  │  - LDAP            │      │  - LDAP            │       │
│  │  - Kerberos        │      │  - Kerberos        │       │
│  │  - NTLM            │      │  - NTLM            │       │
│  │  - Group Policy    │      │  - Group Policy    │       │
│  └─────────────────────┘      └─────────────────────┘       │
│                                                               │
│  Deployed in your Azure Virtual Network                      │
└──────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ **Automatic deployment**: Microsoft handles DC setup
- ✅ **Built-in replication**: Two DCs replicate automatically
- ✅ **Regional deployment**: Can add replica sets in other regions
- ✅ **Isolated management**: You cannot RDP/SSH into DCs
- ✅ **Automatic maintenance**: Microsoft handles all updates

### 3.2 Synchronization Flow

Microsoft Entra Domain Services receives identity information through a one-way synchronization from Microsoft Entra ID.

```plaintext
┌──────────────────────────────────────────────────────────────────┐
│                        On-Premises                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │     On-Premises Active Directory                  │           │
│  │  - Users                                         │           │
│  │  - Groups                                        │           │
│  │  - Passwords                                     │           │
│  └────────────────┬─────────────────────────────────┘           │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    │ Microsoft Entra Connect
                    │ (One-way sync)
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Microsoft Entra ID                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │  - Synced users from on-premises                 │           │
│  │  - Cloud-only users                              │           │
│  │  - Groups                                        │           │
│  │  - Password hashes (if enabled)                  │           │
│  └────────────────┬─────────────────────────────────┘           │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    │ Automatic one-way sync
                    │ (every ~5 minutes)
                    ▼
┌──────────────────────────────────────────────────────────────────┐
│            Microsoft Entra Domain Services                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Managed Domain (contoso.com)                    │           │
│  │  - All users from Entra ID                       │           │
│  │  - All groups from Entra ID                      │           │
│  │  - Password hashes (NTLM/Kerberos)               │           │
│  │  - Available for LDAP queries                    │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Sync Details:**

| Source | Target | Direction | Frequency | Content |
|--------|--------|-----------|-----------|---------|
| On-premises AD | Entra ID | One-way | Configurable (30 min default) | Users, groups, passwords |
| Entra ID | Entra Domain Services | One-way | ~5 minutes | Users, groups, password hashes |

**Important Notes:**
- ✅ Changes in Entra ID sync to Domain Services automatically
- ✅ Cloud-only users in Entra ID also sync to Domain Services
- ❌ Changes made in Domain Services do NOT sync back
- ❌ Direct on-premises to Domain Services sync not supported

### 3.3 Network Integration

Entra Domain Services is deployed into an Azure Virtual Network subnet.

```plaintext
┌────────────────────────────────────────────────────────────────┐
│                Azure Virtual Network (VNet)                    │
│                     10.0.0.0/16                                │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Subnet: DomainServicesSubnet                        │     │
│  │  10.0.0.0/24                                         │     │
│  │                                                      │     │
│  │  ┌────────────────┐      ┌────────────────┐        │     │
│  │  │ Domain Replica │      │ Domain Replica │        │     │
│  │  │      DC1       │      │      DC2       │        │     │
│  │  └────────────────┘      └────────────────┘        │     │
│  │                                                      │     │
│  │  Private IPs: 10.0.0.4, 10.0.0.5                    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Subnet: ApplicationSubnet                           │     │
│  │  10.0.1.0/24                                         │     │
│  │                                                      │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │     │
│  │  │   VM1      │  │   VM2      │  │  App Svc   │    │     │
│  │  │ (Domain    │  │ (Domain    │  │  (VNet     │    │     │
│  │  │  joined)   │  │  joined)   │  │  integrated)│    │     │
│  │  └────────────┘  └────────────┘  └────────────┘    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**Network Requirements:**

| Requirement | Description |
|------------|-------------|
| **Dedicated subnet** | Domain Services needs its own subnet |
| **Subnet size** | Minimum /27 CIDR (32 IPs), /24 recommended |
| **NSG rules** | Must allow specific ports (see below) |
| **DNS** | VMs must use Domain Services DNS IPs |
| **No gateway** | Cannot use VPN/ExpressRoute gateway subnet |

---

## 4. Supported Protocols and Services

### 4.1 LDAP (Lightweight Directory Access Protocol)

**Supported Operations:**

| Operation | Supported | Notes |
|-----------|-----------|-------|
| **LDAP Bind** | ✅ Yes | Authenticate users |
| **LDAP Search** | ✅ Yes | Query directory objects |
| **LDAP Read** | ✅ Yes | Read object attributes |
| **LDAP Write** | ⚠️ Limited | See limitations section |
| **LDAPS (636)** | ✅ Yes | Secure LDAP over SSL |
| **LDAP (389)** | ✅ Yes | Standard LDAP |

**LDAP Query Example:**

```plaintext
Application Configuration:
  LDAP Server: contoso.com
  Port: 389 (LDAP) or 636 (LDAPS)
  Base DN: DC=contoso,DC=com
  Bind DN: CN=ServiceAccount,OU=AADDC Users,DC=contoso,DC=com
  Filter: (&(objectClass=user)(sAMAccountName=john.doe))
```

**Common LDAP Use Cases:**
- Legacy applications using LDAP for authentication
- Applications querying user/group information
- Services binding to LDAP for identity verification
- LDAP-based authorization checks

### 4.2 Kerberos Authentication

**Full Kerberos Support:**

```plaintext
┌──────────────────────────────────────────────────────────┐
│               Kerberos Authentication Flow               │
└──────────────────────────────────────────────────────────┘

1. Client → KDC (Domain Controller)
   ├─ Request: Ticket Granting Ticket (TGT)
   └─ Response: TGT encrypted with user password

2. Client → KDC
   ├─ Request: Service Ticket for target resource
   ├─ Presents: TGT
   └─ Response: Service Ticket

3. Client → Application Server
   ├─ Presents: Service Ticket
   └─ Authenticated access granted
```

**Supported:**
- ✅ Kerberos ticket requests
- ✅ Service Principal Names (SPNs)
- ✅ Kerberos delegation
- ✅ Pre-authentication
- ✅ AES encryption

### 4.3 NTLM Authentication

**Full NTLM Support:**

| NTLM Version | Supported | Use Case |
|--------------|-----------|----------|
| **NTLMv1** | ✅ Yes | Legacy compatibility |
| **NTLMv2** | ✅ Yes | Modern NTLM auth |
| **NTLM pass-through** | ✅ Yes | Application auth |

**When NTLM is Used:**
- Legacy applications that don't support Kerberos
- Authentication across non-trusted domains
- Fallback when Kerberos fails
- Specific application requirements

### 4.4 Domain Join

**Supported Operating Systems:**

| OS | Domain Join Support | Notes |
|----|-------------------|-------|
| **Windows Server 2019** | ✅ Yes | Full support |
| **Windows Server 2016** | ✅ Yes | Full support |
| **Windows 10/11** | ✅ Yes | Full support |
| **Ubuntu Linux** | ✅ Yes | Via realm/sssd |
| **Red Hat/CentOS** | ✅ Yes | Via realm/sssd |
| **SUSE** | ✅ Yes | Via realm/sssd |

**Domain Join Process:**

```plaintext
1. Configure DNS to point to Domain Services IPs
2. Join domain using standard domain join tools
3. Authenticate with domain credentials
4. VM becomes part of managed domain
5. Group Policy applies automatically
```

**PowerShell Example:**

```powershell
# Domain join a Windows VM
Add-Computer -DomainName "contoso.com" `
             -Credential (Get-Credential) `
             -Restart
```

**Linux Example:**

```bash
# Domain join Ubuntu/Red Hat
sudo realm join contoso.com -U admin@contoso.com
```

### 4.5 Group Policy

**Supported GPO Features:**

| Feature | Supported | Notes |
|---------|-----------|-------|
| **Built-in GPOs** | ✅ Yes | AADDC Computers, AADDC Users |
| **Custom GPOs** | ✅ Yes | Can create custom policies |
| **Password Policy** | ✅ Yes | Managed via Default Domain Policy |
| **Security Settings** | ✅ Yes | Firewall, audit, etc. |
| **Registry Settings** | ✅ Yes | Configure registry |
| **Software Installation** | ✅ Yes | Deploy software |

**Default OUs:**

```plaintext
contoso.com
  └─ AADDC Computers (OU)
      └─ All domain-joined computers
  └─ AADDC Users (OU)
      └─ All synchronized users
  └─ AADDC DC Administrators (Group)
      └─ Can manage Group Policy
```

---

## 5. Use Cases and Scenarios

### 5.1 Migrating Legacy Applications to Azure

**Problem:**
You have legacy applications that require:
- LDAP authentication
- Kerberos/NTLM
- Domain-joined servers
- Cannot be easily refactored for cloud-native auth

**Solution: Microsoft Entra Domain Services**

```plaintext
┌─────────────────────────────────────────────────────────┐
│              Before Migration (On-Premises)             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Legacy App] ──LDAP──► [On-Premises AD]              │
│  [Server1]    ──NTLM──► [Domain Controller]           │
│                                                         │
└─────────────────────────────────────────────────────────┘

                        ▼ Migration ▼

┌─────────────────────────────────────────────────────────┐
│                After Migration (Azure)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Azure VM]   ──LDAP──► [Entra Domain Services]       │
│  [Legacy App] ──NTLM──► [Managed DCs]                 │
│                                                         │
│  ✅ No code changes required                           │
│  ✅ No on-premises connectivity needed                 │
│  ✅ Microsoft manages infrastructure                   │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ Lift-and-shift migration without application refactoring
- ✅ Eliminate on-premises domain controller dependencies
- ✅ Maintain security policy compliance
- ✅ Reduce infrastructure management overhead

### 5.2 Lift-and-Shift Migrations

**Scenario:**
Migrate entire application stacks to Azure without changes.

```plaintext
On-Premises Stack → Azure Stack

[Web Tier]               [Azure VM - Web Tier]
    ↓                           ↓
[App Tier]       →       [Azure VM - App Tier]
    ↓                           ↓
[DB Tier]                [Azure SQL MI / VM]
    ↓                           ↓
[AD Authentication]      [Entra Domain Services]
```

### 5.3 Azure Virtual Desktop

**Use Case:**
Provide virtual desktops that require domain join and GPO management.

```plaintext
┌────────────────────────────────────────────────────────┐
│           Azure Virtual Desktop Pool                   │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Session │  │  Session │  │  Session │           │
│  │  Host 1  │  │  Host 2  │  │  Host 3  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │             │             │                   │
│       └─────────────┴─────────────┘                   │
│                     │                                  │
│                     │ Domain-joined                    │
│                     ▼                                  │
│       ┌──────────────────────────────┐                │
│       │ Entra Domain Services        │                │
│       │ - User authentication        │                │
│       │ - Group Policy               │                │
│       │ - Profile management         │                │
│       └──────────────────────────────┘                │
└────────────────────────────────────────────────────────┘
```

**Benefits:**
- ✅ FSLogix profile management with domain accounts
- ✅ Group Policy for desktop configuration
- ✅ Single sign-on experience
- ✅ Centralized user management

### 5.4 Hybrid Identity Scenarios

**Architecture:**

```plaintext
┌──────────────────────────────────────────────────────────┐
│                    On-Premises                           │
│                                                          │
│  [On-Premises AD] ──sync──► [Entra Connect]            │
│  [Domain Controllers]              │                     │
│  [User accounts]                   │                     │
└────────────────────────────────────┼─────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────┐
│                   Microsoft Entra ID                     │
│                                                          │
│  [Synced identities]                                    │
│  [Cloud-only users]                                     │
│  [Groups]                                               │
└────────────────────────────────────┼─────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────┐
│            Microsoft Entra Domain Services               │
│                                                          │
│  [Managed domain]                                       │
│  [LDAP/Kerberos/NTLM]                                  │
│  [Legacy app support]                                   │
└──────────────────────────────────────────────────────────┘
```

---

## 6. Identity Solutions Comparison

### 6.1 Entra Domain Services vs Self-Managed AD DS

| Aspect | Entra Domain Services | Self-Managed AD DS on Azure VMs |
|--------|----------------------|--------------------------------|
| **Deployment** | ✅ Fully managed, click to deploy | ❌ Manual VM deployment |
| **Maintenance** | ✅ Microsoft manages | ❌ You manage |
| **Patching** | ✅ Automatic | ❌ Manual patching required |
| **High Availability** | ✅ Built-in (2 DCs) | ❌ Must configure yourself |
| **Backups** | ✅ Automatic | ❌ Must implement |
| **Monitoring** | ✅ Azure Monitor integration | ❌ Must configure |
| **Cost** | Service fee | VM + Storage + Licenses |
| **Schema Control** | ❌ Read-only | ✅ Full control |
| **Forest Trusts** | ❌ Not supported | ✅ Supported |
| **LDAP Write** | ⚠️ Limited | ✅ Full access |
| **Replication to on-prem** | ❌ No | ✅ Yes (if configured) |

**When to use Self-Managed AD DS:**
- Need schema extensions
- Require forest/domain trusts
- Full LDAP write access required
- Bi-directional sync with on-premises needed

**When to use Entra Domain Services:**
- ✅ Want managed service (no DC maintenance)
- ✅ Lift-and-shift legacy apps
- ✅ One-way sync from on-premises is sufficient
- ✅ Don't need schema modifications

### 6.2 Entra Domain Services vs Microsoft Entra ID

| Feature | Entra Domain Services | Microsoft Entra ID (only) |
|---------|----------------------|---------------------------|
| **LDAP** | ✅ Yes | ❌ No |
| **Kerberos** | ✅ Yes | ❌ No |
| **NTLM** | ✅ Yes | ❌ No |
| **Domain Join** | ✅ Yes | ✅ Yes (Entra Join) |
| **Group Policy** | ✅ Yes | ⚠️ Limited (MDM) |
| **Modern Auth** | ⚠️ Limited | ✅ OAuth/OIDC |
| **SaaS Apps** | ❌ Limited | ✅ Excellent |
| **Legacy Apps** | ✅ Excellent | ❌ Limited |
| **Cloud-native Apps** | ⚠️ Possible | ✅ Designed for |

**Decision Tree:**

```plaintext
Does your app need LDAP/Kerberos/NTLM?
    │
    ├─ YES → Use Entra Domain Services
    │
    └─ NO → Does it support modern auth (OAuth/OIDC)?
            │
            ├─ YES → Use Microsoft Entra ID directly
            │
            └─ NO → Consider refactoring or use Entra Domain Services
```

### 6.3 Entra Domain Services vs Application Proxy

| Purpose | Entra Domain Services | Application Proxy |
|---------|----------------------|-------------------|
| **Primary Use** | Provide AD services in Azure | Publish on-premises apps externally |
| **LDAP Support** | ✅ Yes | ❌ No |
| **Authentication** | LDAP/Kerberos/NTLM | ✅ Entra ID/MFA |
| **Location** | Azure-hosted services | On-premises apps |
| **Network Access** | Not required | ✅ Connector to on-premises |
| **Use Case** | Legacy app migration to Azure | Remote access to on-prem apps |

**When to use Application Proxy:**
- ✅ Application stays on-premises
- ✅ Need remote access without VPN
- ✅ Want MFA for on-premises apps
- ✅ App uses HTTP/HTTPS

**When to use Entra Domain Services:**
- ✅ Migrating application to Azure
- ✅ App needs LDAP/Kerberos
- ✅ No on-premises connectivity allowed
- ✅ Need domain join in Azure

---

## 7. Deployment and Configuration

### 7.1 Prerequisites

**Required:**
- ✅ Azure subscription
- ✅ Microsoft Entra ID tenant
- ✅ Virtual network in Azure
- ✅ Proper RBAC permissions

**Recommended:**
- ✅ Password hash sync enabled (if using Entra Connect)
- ✅ Dedicated subnet (/24 or larger)
- ✅ Network Security Group configured
- ✅ Planning for DNS configuration

### 7.2 Deployment Steps

**Step 1: Create Managed Domain**

```plaintext
Azure Portal Navigation:
  → Create a resource
  → Search: "Microsoft Entra Domain Services"
  → Select and Create

Configuration:
  ├─ Subscription: [Select subscription]
  ├─ Resource group: [Create or select]
  ├─ DNS domain name: contoso.com
  ├─ Region: East US
  ├─ SKU: Enterprise (or Standard)
  ├─ Virtual network: [Select VNet]
  └─ Subnet: [Create dedicated subnet]
```

**Step 2: Wait for Deployment**

```plaintext
Deployment Process:
  ├─ Duration: 30-60 minutes
  ├─ Azure provisions 2 domain controllers
  ├─ Configures AD DS features
  ├─ Starts initial sync from Entra ID
  └─ Updates DNS records
```

**Step 3: Configure DNS**

```plaintext
After Deployment:
  ├─ Note the two IP addresses (DC1, DC2)
  ├─ Update VNet DNS servers
  │   └─ VNet → DNS servers → Custom
  │       ├─ Primary: 10.0.0.4
  │       └─ Secondary: 10.0.0.5
  └─ Restart VMs to pick up new DNS settings
```

### 7.3 Network Configuration

**Required Network Security Group Rules:**

| Service | Port | Protocol | Source | Destination | Purpose |
|---------|------|----------|--------|-------------|---------|
| LDAP | 389 | TCP | VNet | Domain subnet | Directory queries |
| LDAPS | 636 | TCP | VNet | Domain subnet | Secure LDAP |
| Kerberos | 88 | TCP/UDP | VNet | Domain subnet | Authentication |
| DNS | 53 | TCP/UDP | VNet | Domain subnet | Name resolution |
| SMB | 445 | TCP | VNet | Domain subnet | File sharing/GPO |
| RPC | 135 | TCP | VNet | Domain subnet | Remote management |
| RPC Dynamic | 49152-65535 | TCP | VNet | Domain subnet | Dynamic RPC |

**NSG Configuration Example:**

```plaintext
Network Security Group: NSG-DomainServices
  
  Inbound Rules:
  ├─ AllowLDAP: Port 389, Source: VirtualNetwork
  ├─ AllowLDAPS: Port 636, Source: VirtualNetwork
  ├─ AllowKerberos: Port 88, Source: VirtualNetwork
  ├─ AllowDNS: Port 53, Source: VirtualNetwork
  ├─ AllowSMB: Port 445, Source: VirtualNetwork
  └─ AllowRPC: Ports 135, 49152-65535, Source: VirtualNetwork
  
  Outbound Rules:
  └─ AllowAll: Permit outbound (for management)
```

### 7.4 DNS Configuration

**VNet DNS Settings:**

```plaintext
Virtual Network: production-vnet
  └─ DNS servers: Custom
      ├─ Primary DNS: 10.0.0.4 (Domain Services DC1)
      └─ Secondary DNS: 10.0.0.5 (Domain Services DC2)
```

**Important:**
- ✅ All VMs must use Domain Services IPs as DNS
- ✅ Update VNet DNS settings, not individual VM DNS
- ✅ Restart VMs after DNS change
- ✅ Verify DNS resolution: `nslookup contoso.com`

---

## 8. Security and Access Control

### 8.1 Authentication Methods

**Supported Methods:**

| Method | Support Level | Use Case |
|--------|--------------|----------|
| **Password** | ✅ Full | Standard authentication |
| **Kerberos** | ✅ Full | Domain-joined machines |
| **NTLM** | ✅ Full | Legacy applications |
| **Certificate** | ⚠️ Limited | Smart card auth (limited) |

### 8.2 Password Hash Synchronization

**For on-premises users to authenticate:**

```plaintext
┌──────────────────────────────────────────────────────────┐
│         Password Hash Sync Requirement                   │
└──────────────────────────────────────────────────────────┘

On-Premises AD
    ↓
    ↓ Microsoft Entra Connect
    ↓ (Must enable password hash sync)
    ↓
Microsoft Entra ID
    ↓
    ↓ Automatic sync
    ↓ (Password hashes for NTLM/Kerberos)
    ↓
Microsoft Entra Domain Services
```

**Configuration in Entra Connect:**

```plaintext
Entra Connect Wizard:
  ├─ Connect to Entra ID
  ├─ Connect to AD DS
  ├─ Sign-in method
  │   └─ ✅ Enable: Password hash synchronization
  └─ Complete configuration
```

**Important:**
- ❌ Without password hash sync, on-prem users **cannot** authenticate to Domain Services
- ✅ Cloud-only users work immediately (no sync required)
- ✅ Enable password hash sync even if using federation

### 8.3 Security Best Practices

**Identity Security:**

| Practice | Implementation |
|----------|---------------|
| **Least Privilege** | Only grant necessary Domain Admin access |
| **MFA for Admins** | Enable MFA for AAD DC Administrators group |
| **Service Accounts** | Use managed service accounts when possible |
| **Password Policy** | Configure via Group Policy |
| **Audit Logging** | Enable Azure Monitor diagnostics |

**Network Security:**

```plaintext
Security Layers:
  ├─ NSG on Domain Services subnet
  │   └─ Restrict source IPs to VNet only
  ├─ LDAPS for encrypted LDAP
  │   └─ Upload custom SSL certificate
  ├─ Network isolation
  │   └─ Dedicated subnet, no public IPs
  └─ Azure Firewall (optional)
      └─ Control outbound traffic
```

### 8.4 Network Security Groups

**Recommended NSG Configuration:**

```plaintext
Priority | Name | Port | Protocol | Source | Action
---------|------|------|----------|--------|-------
100 | AllowKerberos | 88 | TCP/UDP | VirtualNetwork | Allow
110 | AllowDNS | 53 | TCP/UDP | VirtualNetwork | Allow
120 | AllowLDAP | 389 | TCP | VirtualNetwork | Allow
130 | AllowLDAPS | 636 | TCP | VirtualNetwork | Allow
140 | AllowSMB | 445 | TCP | VirtualNetwork | Allow
150 | AllowRPC | 135 | TCP | VirtualNetwork | Allow
160 | AllowRPCDynamic | 49152-65535 | TCP | VirtualNetwork | Allow
4000 | DenyAllInbound | * | * | * | Deny
```

---

## 9. Administration and Management

### 9.1 Administrative Accounts

**Built-in Administrative Groups:**

| Group | Purpose | Membership |
|-------|---------|------------|
| **AAD DC Administrators** | Domain admin equivalent | Managed in Entra ID |
| **AADDC Computers** | Container for domain-joined computers | Automatic |
| **AADDC Users** | Container for synced users | Automatic |

**Managing Administrators:**

```plaintext
Azure Portal:
  → Microsoft Entra ID
  → Groups
  → Find: "AAD DC Administrators"
  → Members
  → Add member: [user@contoso.com]

Result:
  └─ User gains domain admin rights in Domain Services
```

**Important:**
- ✅ AAD DC Administrators = Domain Admins
- ✅ Can manage Group Policy
- ✅ Can reset passwords for domain users
- ❌ Cannot access domain controller VMs directly
- ❌ Cannot extend schema

### 9.2 Group Policy Management

**Managing GPOs:**

```plaintext
From a domain-joined Windows VM:
  ├─ Install RSAT tools
  │   └─ Add-WindowsFeature RSAT-ADDS-Tools
  ├─ Open Group Policy Management Console (gpmc.msc)
  ├─ Connect to: contoso.com
  └─ Manage GPOs:
      ├─ Default Domain Policy (built-in)
      ├─ AADDC Computers Policy (built-in)
      ├─ AADDC Users Policy (built-in)
      └─ Create custom GPOs
```

**Common GPO Tasks:**

| Task | How To |
|------|--------|
| **Password Policy** | Edit Default Domain Policy → Computer Config → Policies → Windows Settings → Security Settings → Account Policies |
| **Firewall Rules** | Create GPO → Computer Config → Policies → Windows Settings → Security Settings → Windows Firewall |
| **Software Deployment** | Create GPO → Computer Config → Policies → Software Settings → Software Installation |
| **Registry Settings** | Create GPO → Computer/User Config → Preferences → Windows Settings → Registry |

### 9.3 Monitoring and Diagnostics

**Azure Monitor Integration:**

```plaintext
Azure Portal:
  → Microsoft Entra Domain Services
  → Diagnostic settings
  → Add diagnostic setting
      ├─ Name: Send to Log Analytics
      ├─ Logs: Select categories
      │   ├─ SystemSecurity
      │   ├─ AccountManagement
      │   ├─ LogonLogoff
      │   └─ ObjectAccess
      └─ Destination: Log Analytics workspace
```

**Available Logs:**

| Log Category | Information |
|--------------|-------------|
| **SystemSecurity** | Security events, authentication |
| **AccountManagement** | Account creation, modification |
| **LogonLogoff** | User logon/logoff events |
| **ObjectAccess** | Resource access attempts |
| **DirectoryServiceAccess** | LDAP queries, bind attempts |

**Monitoring Alerts:**

```plaintext
Common Alerts:
  ├─ Failed authentication attempts (potential brute force)
  ├─ Domain controller health (replica unavailable)
  ├─ Password expiration notifications
  └─ Suspicious account activity
```

### 9.4 Backup and Disaster Recovery

**Automatic Backups:**

| Feature | Details |
|---------|---------|
| **Frequency** | Continuous, automatic |
| **Retention** | Microsoft-managed |
| **Scope** | Entire managed domain |
| **Recovery** | Microsoft support required |

**High Availability:**

```plaintext
Built-in HA:
  ├─ 2 domain controllers per region (minimum)
  ├─ Automatic replication
  ├─ Automatic failover
  └─ SLA: 99.9% availability
```

**Replica Sets (Multi-Region):**

```plaintext
Primary Region: East US
  └─ Replica Set 1: DC1, DC2

Additional Region: West US
  └─ Replica Set 2: DC3, DC4

Benefits:
  ├─ Regional disaster recovery
  ├─ Lower latency for multi-region apps
  └─ Automatic cross-region replication
```

---

## 10. Limitations and Constraints

### 10.1 Schema Extensions

❌ **Not Supported**

- Cannot extend AD schema
- Cannot add custom attributes
- Cannot create new object classes

**Workaround:**
- Use existing AD attributes
- Store custom data in application database
- Use extension attributes (if available)

### 10.2 LDAP Write Operations

⚠️ **Limited Support**

| Operation | Supported? | Notes |
|-----------|-----------|-------|
| **Read attributes** | ✅ Yes | Full read access |
| **Password change** | ✅ Yes | Users can change own passwords |
| **Create users** | ❌ No | Users created in Entra ID |
| **Create OUs** | ❌ No | Use built-in OUs only |
| **Modify groups** | ⚠️ Limited | Some group operations possible |

**How to manage objects:**
- ✅ Create users/groups in Microsoft Entra ID
- ✅ Wait for automatic sync to Domain Services
- ❌ Don't try to create objects directly in Domain Services

### 10.3 Trust Relationships

❌ **Not Supported**

- No forest trusts
- No domain trusts
- No external trusts
- Cannot integrate with other AD forests

**Impact:**
- Domain Services is a standalone managed domain
- Cannot establish trust with on-premises AD
- Cannot extend on-premises domain to Azure

### 10.4 Forest Functional Level

❌ **Fixed by Microsoft**

- Forest functional level managed by Microsoft
- Cannot change forest/domain functional level
- Typically Windows Server 2012 R2 or higher
- Automatic updates by Microsoft

---

## 11. Pricing and Licensing

### 11.1 SKU Options

| SKU | Object Limit | Features | Use Case |
|-----|-------------|----------|----------|
| **Standard** | 25,000 objects | Basic features | Dev/test, small deployments |
| **Enterprise** | Unlimited objects | All features, multi-region | Production environments |

### 11.2 Cost Considerations

**What's Included:**
- ✅ Two domain controllers (replicas)
- ✅ Automatic backups
- ✅ High availability
- ✅ Automatic patching and updates
- ✅ Azure Monitor integration

**Additional Costs:**
- Virtual network (usually minimal)
- VMs (domain-joined resources)
- Storage for VMs
- Network egress (minimal)

**Cost Optimization:**
- Use Standard SKU for non-production
- Right-size VM resources
- Use Azure Hybrid Benefit for Windows Server licenses
- Leverage reserved instances for long-term VMs

---

## 12. Migration Scenarios

### 12.1 Migrating LDAP Applications

**Before Migration:**

```plaintext
On-Premises:
  [Application Server] ──LDAP──► [On-Premises AD]
                        (389/636)  [Domain Controller]
  
  LDAP Config:
    Server: dc01.contoso.local
    Port: 389
    Base DN: DC=contoso,DC=local
    Bind DN: CN=ServiceAccount,OU=Services,DC=contoso,DC=local
```

**After Migration:**

```plaintext
Azure:
  [Azure VM] ──LDAP──► [Entra Domain Services]
  [Application]         [Managed Domain]
  
  LDAP Config (Updated):
    Server: contoso.com
    Port: 389
    Base DN: DC=contoso,DC=com
    Bind DN: CN=ServiceAccount,OU=AADDC Users,DC=contoso,DC=com
```

**Migration Steps:**

```plaintext
1. Deploy Entra Domain Services in Azure
2. Wait for sync to complete
3. Migrate application to Azure VM
4. Update LDAP configuration:
   ├─ LDAP server hostname
   ├─ Distinguished names (DN paths)
   └─ Service account credentials
5. Test LDAP queries
6. Cutover application traffic
7. Decommission on-premises server
```

### 12.2 Domain Join Migration

**Process:**

```plaintext
1. Deploy Entra Domain Services
2. Configure VNet DNS to point to Domain Services
3. Create new Azure VMs
4. Domain-join VMs to managed domain
5. Install applications
6. Migrate data
7. Update DNS/Load Balancer
8. Retire on-premises VMs
```

### 12.3 Application Compatibility

**Compatible Applications:**

| Application Type | Compatibility | Notes |
|-----------------|---------------|-------|
| **SharePoint** | ✅ Yes | Domain-joined servers |
| **SQL Server** | ✅ Yes | Windows Authentication |
| **File Servers** | ✅ Yes | SMB with domain auth |
| **Web Apps (IIS)** | ✅ Yes | Windows Authentication |
| **Custom LDAP Apps** | ✅ Yes | Update connection strings |
| **Linux Apps** | ✅ Yes | Via SSSD/realm |

**Testing Checklist:**

```plaintext
✓ LDAP bind succeeds
✓ User authentication works
✓ Group membership queries return correctly
✓ Kerberos tickets obtained successfully
✓ Domain-joined machines can access resources
✓ Group Policy applies correctly
✓ Application functionality verified
```

---

## 13. Troubleshooting Common Issues

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| **Cannot domain join VM** | DNS not configured | Update VNet DNS to Domain Services IPs |
| **LDAP queries fail** | NSG blocking traffic | Verify NSG allows port 389/636 |
| **Authentication fails** | Password hash sync not enabled | Enable in Entra Connect |
| **Users not found** | Sync not complete | Wait for sync, check Entra ID |
| **Group Policy not applying** | VM not domain-joined | Verify domain membership: `whoami /user` |
| **Cannot bind to LDAP** | Incorrect credentials | Check service account exists in AAD |
| **Slow performance** | Network latency | Check VM placement, use same region |
| **Certificate errors (LDAPS)** | Custom cert not uploaded | Upload valid SSL certificate |

**Diagnostic Commands:**

```powershell
# Windows PowerShell

# Check domain membership
Test-ComputerSecureChannel -Verbose

# Verify DNS resolution
Resolve-DnsName contoso.com

# Test LDAP connectivity
Test-NetConnection -ComputerName contoso.com -Port 389

# Check domain controller
nltest /dclist:contoso.com

# Verify Kerberos
klist tickets

# Force Group Policy update
gpupdate /force
```

```bash
# Linux

# Check domain membership
realm list

# Test LDAP
ldapsearch -H ldap://contoso.com -D "CN=user,OU=AADDC Users,DC=contoso,DC=com" -W -b "DC=contoso,DC=com"

# Verify Kerberos
klist

# Check SSSD status
systemctl status sssd
```

---

## 14. Exam Scenarios and Practice Questions

### 14.1 Scenario: LDAP Application Migration

**Question:**

Your company has the following infrastructure:

- On-premises Active Directory domain that syncs to Microsoft Entra ID
- Server1 running App1 that uses LDAP queries for user authentication
- Plan to migrate Server1 to Azure Subscription1
- Security policy: VMs in Subscription1 must NOT access on-premises network

What should you recommend to ensure App1 continues to function?

**Options:**
A. Active Directory Domain Services role on a VM  
B. Microsoft Entra Domain Services ✅  
C. Microsoft Entra Application Proxy  
D. Azure VPN Gateway  

**Answer: B. Microsoft Entra Domain Services**

**Why:**
- ✅ Provides LDAP support in Azure
- ✅ No on-premises connectivity required
- ✅ Syncs from Microsoft Entra ID automatically
- ✅ Fully managed service
- ✅ Meets security policy requirements

**Why others are wrong:**
- **A**: Requires manual management, may need on-prem connectivity
- **C**: For publishing on-prem apps, doesn't provide LDAP
- **D**: Violates security policy (creates on-prem connection)

### 14.2 Scenario: Choosing Identity Solutions

**Question:**

You need to recommend an identity solution for the following requirements:

- Legacy application requires Kerberos authentication
- Application will run on Azure VMs
- No schema extensions needed
- Don't want to manage domain controllers
- Users synced from on-premises AD

Which solution should you recommend?

**Options:**
A. Microsoft Entra ID only  
B. Self-managed AD DS on Azure VMs  
C. Microsoft Entra Domain Services ✅  
D. Microsoft Entra Connect only  

**Answer: C. Microsoft Entra Domain Services**

**Why:**
- ✅ Provides Kerberos authentication
- ✅ Fully managed (no DC management)
- ✅ Works with synced users
- ✅ No schema extensions needed

**Why others are wrong:**
- **A**: Doesn't support Kerberos protocol
- **B**: Requires managing DCs
- **D**: Only syncs identities, doesn't provide auth services

### 14.3 Scenario: Hybrid Identity Architecture

**Question:**

Your company wants to:
- Keep on-premises Active Directory
- Migrate some applications to Azure
- Migrated apps need domain join capability
- Minimize on-premises dependencies for Azure workloads

What architecture should you recommend?

**Answer:**

```plaintext
On-Premises AD
    ↓
Microsoft Entra Connect (sync)
    ↓
Microsoft Entra ID
    ↓
Microsoft Entra Domain Services (for Azure apps)
```

**Components:**
1. **Keep on-premises AD** - For on-prem applications
2. **Entra Connect** - Sync users to cloud
3. **Entra ID** - Central identity provider
4. **Entra Domain Services** - For legacy Azure apps needing domain join

**Benefits:**
- ✅ Hybrid identity maintained
- ✅ Azure workloads independent of on-premises
- ✅ Single identity source (on-premises AD)
- ✅ Managed domain services in Azure

### 14.4 Scenario: Extending On-Premises AD DS to Azure (Self-Managed DCs)

**Question:**

Your company operates an Active Directory Domain Services (AD DS) forest with a single domain named **company.com** and has several geographic locations. The forest functional level is Windows Server 2016. The company has legacy on-premises applications that depend on AD DS and Kerberos authentication, and there are no plans to rewrite or replace these applications.

The company is exploring options to migrate its applications to the cloud and has acquired an Azure subscription, but Microsoft Entra ID has not been configured.

**Requirements for the test environment:**
- Supports Kerberos authentication from the cloud without needing access to the on-premises network
- Minimizes changes to the applications
- Reduces additional AD management tasks
- Requires minimal effort to configure

**Current Setup:**
- Single virtual network (VNet) in Azure
- Site-to-site (S2S) VPN Gateway connection between the VNet and the on-premises network

**Question:** To complete the setup and test the applications, what steps should you take?

**Options:**
- A) Create a new VNet and create a new AD DS forest root domain on the new VNet
- B) Configure a Microsoft Entra domain named company.com
- C) Deploy one or more domain controllers for company.com on the existing VNet ✅
- D) Create a child domain of company.com on the existing VNet

**Answer: C) Deploy one or more domain controllers for company.com on the existing VNet** ✅

**Why Option C is Correct:**

By deploying domain controllers for the **existing domain (company.com)** on the Azure VNet:

| Requirement | How It's Met |
|-------------|--------------|
| **Kerberos without on-premises access** | Once the Azure DC replicates with on-premises, it has all AD data locally. Kerberos authentication works entirely within Azure |
| **Minimize application changes** | Applications continue using the same domain name, same credentials, same authentication flow - zero changes needed |
| **Reduce AD management tasks** | Single domain means single set of policies, single schema, no trust relationships to manage |
| **Minimal configuration effort** | S2S VPN already exists; just deploy VM, promote to DC, let replication happen automatically |

**How AD Replication Enables "Offline" Kerberos:**

```plaintext
┌─────────────────────────────────────────────────────────────────┐
│                    Initial Setup (VPN Active)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   On-Premises                        Azure VNet                  │
│   ┌─────────────┐    S2S VPN    ┌─────────────┐                │
│   │   DC1       │◄─────────────►│   DC2       │                │
│   │ company.com │  Replication  │ company.com │                │
│   └─────────────┘               └─────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              After Replication (VPN Optional)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Azure VNet                                                     │
│   ┌─────────────┐      ┌─────────────────────┐                 │
│   │   DC2       │◄────►│  Legacy App VMs     │                 │
│   │ company.com │      │  (Kerberos Auth)    │                 │
│   │             │      │                     │                 │
│   │ Has full    │      │ Authenticates       │                 │
│   │ AD replica  │      │ against local DC2   │                 │
│   └─────────────┘      └─────────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Why Other Options Are Incorrect:**

| Option | Problem |
|--------|--------|
| **A) New VNet + new forest** | New forest = new domain, requires trusts, more management, app changes needed |
| **B) Microsoft Entra domain** | Entra ID ≠ AD DS; doesn't provide traditional Kerberos authentication for legacy apps |
| **D) Child domain** | Creates child.company.com - requires app reconfiguration, additional domain to manage |

> **Important:** This scenario requires **self-managed AD DS** (DCs on VMs), NOT Microsoft Entra Domain Services. Why?
> - Entra Domain Services cannot use the same domain name as an existing on-premises domain
> - Full AD DS replication provides complete offline capability
> - Self-managed DCs are part of the same forest/domain

**Key Concepts: AD DS Extension Strategies in Azure**

| Strategy | Use Case | Complexity | Kerberos Support |
|----------|----------|------------|------------------|
| **Extend existing domain (DCs in Azure)** | Lift-and-shift legacy apps with existing domain | Low | ✅ Full native |
| **New child domain** | Organizational separation needed | Medium | ✅ Full native |
| **New forest** | Complete isolation required | High | ✅ Full native (with trusts) |
| **Microsoft Entra Domain Services** | Managed AD DS for cloud workloads (new domain) | Low | ✅ Full native |
| **Microsoft Entra ID only** | Modern cloud-native apps | Low | ❌ Not traditional |

**References:**
- [Deploy AD DS in an Azure Virtual Network](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/identity/adds-extend-domain)
- [Identity Options for Azure](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/identity/)

---

## 15. Best Practices

**Deployment:**
1. ✅ Use dedicated subnet for Domain Services
2. ✅ Size subnet appropriately (/24 recommended)
3. ✅ Enable password hash sync before deploying
4. ✅ Plan domain name carefully (can't be changed)
5. ✅ Deploy in same region as workloads

**Security:**
1. ✅ Enable LDAPS with custom certificate
2. ✅ Restrict NSG rules to necessary ports only
3. ✅ Use MFA for AAD DC Administrators
4. ✅ Enable Azure Monitor diagnostics
5. ✅ Regularly review administrative access
6. ✅ Implement least privilege principle

**Operations:**
1. ✅ Monitor health in Azure Portal
2. ✅ Review security logs regularly
3. ✅ Test disaster recovery procedures
4. ✅ Document GPO changes
5. ✅ Keep application LDAP configs documented

**Performance:**
1. ✅ Deploy VMs in same region as Domain Services
2. ✅ Use VNet peering for multi-VNet scenarios
3. ✅ Consider replica sets for multi-region apps
4. ✅ Monitor LDAP query performance

**Cost Optimization:**
1. ✅ Use Standard SKU for non-production
2. ✅ Right-size VM resources
3. ✅ Use Azure Hybrid Benefit
4. ✅ Review and remove unused resources

---

## 16. Reference Links

**Official Documentation:**
- [Microsoft Entra Domain Services Overview](https://learn.microsoft.com/en-us/entra/identity/domain-services/overview)
- [Create and configure an Entra Domain Services managed domain](https://learn.microsoft.com/en-us/entra/identity/domain-services/tutorial-create-instance)
- [Networking concepts for Domain Services](https://learn.microsoft.com/en-us/entra/identity/domain-services/network-considerations)
- [Compare identity solutions](https://learn.microsoft.com/en-us/entra/identity/domain-services/compare-identity-solutions)
- [Administer Entra Domain Services](https://learn.microsoft.com/en-us/entra/identity/domain-services/manage-domain)

**Tutorial Series:**
- [Tutorial: Create a management VM](https://learn.microsoft.com/en-us/entra/identity/domain-services/tutorial-create-management-vm)
- [Tutorial: Configure LDAPS](https://learn.microsoft.com/en-us/entra/identity/domain-services/tutorial-configure-ldaps)
- [Tutorial: Create a replica set](https://learn.microsoft.com/en-us/entra/identity/domain-services/tutorial-create-replica-set)

**Architecture Guidance:**
- [Hybrid identity documentation](https://learn.microsoft.com/en-us/entra/identity/hybrid/whatis-hybrid-identity)
- [Azure Virtual Desktop with Domain Services](https://learn.microsoft.com/en-us/azure/virtual-desktop/azure-ad-joined-session-hosts)
- [Application migration to Azure](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/migrate/)

**Troubleshooting:**
- [Troubleshoot Domain Services](https://learn.microsoft.com/en-us/entra/identity/domain-services/troubleshoot)
- [Troubleshoot LDAPS](https://learn.microsoft.com/en-us/entra/identity/domain-services/tshoot-ldaps)
- [Troubleshoot domain join](https://learn.microsoft.com/en-us/entra/identity/domain-services/troubleshoot-domain-join)

**Related Topics:**
- Microsoft Entra Connect (directory synchronization)
- Microsoft Entra Application Proxy
- Azure VPN Gateway
- Azure Virtual Desktop
- Azure migrate and modernization

---

**Document Version:** 1.0  
**Last Updated:** December 14, 2025  
**Domain:** Design Identity, Governance, and Monitoring Solutions  
**Author:** Azure Learning Documentation

---

End of Document
