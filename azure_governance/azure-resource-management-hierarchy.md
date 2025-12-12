# Azure Resource Management Hierarchy

## Table of Contents

- [Overview](#overview)
- [Complete Resource Hierarchy](#complete-resource-hierarchy)
- [Hierarchy Levels Explained](#hierarchy-levels-explained)
  - [1. Microsoft Entra Tenant (Azure AD Tenant)](#1-microsoft-entra-tenant-azure-ad-tenant)
  - [2. Management Groups](#2-management-groups)
  - [3. Subscriptions](#3-subscriptions)
  - [4. Resource Groups](#4-resource-groups)
  - [5. Resources](#5-resources)
- [Scope and Inheritance](#scope-and-inheritance)
- [RBAC Scope Hierarchy](#rbac-scope-hierarchy)
- [Azure Policy Inheritance](#azure-policy-inheritance)
- [Management Group Best Practices](#management-group-best-practices)
- [Resource Organization Patterns](#resource-organization-patterns)
- [Multi-Tenant Considerations](#multi-tenant-considerations)
- [Practice Questions](#practice-questions)

## Overview

Azure uses a hierarchical structure to organize and manage cloud resources. Understanding this hierarchy is crucial for:

- **Governance**: Applying policies and compliance standards
- **Access Control**: Implementing RBAC at appropriate scopes
- **Cost Management**: Organizing and tracking expenses
- **Resource Organization**: Structuring resources logically
- **Operational Efficiency**: Managing resources at scale

The hierarchy flows from the most global level (Microsoft Entra Tenant) down to individual resources.

## Complete Resource Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    Microsoft Entra Tenant                        │
│                   (Identity Boundary)                            │
│                   tenant.onmicrosoft.com                         │
│                                                                  │
│  • All users, groups, and applications                           │
│  • Single source of identity                                     │
│  • Can contain multiple subscriptions                            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Root Management Group                          │
│                  (Optional - Organizational Hierarchy)           │
│                                                                  │
│  • Highest level of management group hierarchy                   │
│  • Created automatically per tenant                              │
│  • Policies and RBAC cascade down                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              Management Groups (Organizational Units)            │
│                                                                  │
│  Example Structure:                                              │
│  ├── Production                                                  │
│  │   ├── Corp-Production                                         │
│  │   └── Online-Production                                       │
│  ├── Non-Production                                              │
│  │   ├── Development                                             │
│  │   └── Testing                                                 │
│  └── Sandbox                                                     │
│                                                                  │
│  • Up to 6 levels of depth                                       │
│  • Support 10,000 management groups per tenant                   │
│  • Policy and RBAC inheritance                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Subscriptions                               │
│                    (Billing Boundary)                            │
│                                                                  │
│  Production Subscription (Sub-001)                               │
│  Development Subscription (Sub-002)                              │
│  Testing Subscription (Sub-003)                                  │
│                                                                  │
│  • Billing and cost tracking boundary                            │
│  • Resource quotas and limits                                    │
│  • Single management group parent                                │
│  • Can be moved between management groups                        │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Resource Groups                             │
│                  (Lifecycle Boundary)                            │
│                                                                  │
│  RG-WebApp-Production                                            │
│  RG-Database-Production                                          │
│  RG-NetworkingHub                                                │
│                                                                  │
│  • Logical container for resources                               │
│  • Share same lifecycle (deploy, update, delete together)        │
│  • Single region location (metadata)                             │
│  • Resources can be in different regions                         │
│  • Cannot be nested                                              │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Resources                                │
│                   (Azure Services)                               │
│                                                                  │
│  • Virtual Machines                                              │
│  • Storage Accounts                                              │
│  • SQL Databases                                                 │
│  • App Services                                                  │
│  • Key Vaults                                                    │
│  • ... and 200+ Azure services                                   │
│                                                                  │
│  • Must belong to exactly one resource group                     │
│  • Can be moved between resource groups                          │
│  • Can be in any region                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Hierarchy Levels Explained

### 1. Microsoft Entra Tenant (Azure AD Tenant)

**What It Is:**
- The root level of identity and access management in Azure
- Represents an organization in Azure
- Every Azure account belongs to exactly one tenant
- Identified by a domain name (e.g., `contoso.onmicrosoft.com`)

**Key Characteristics:**

| Aspect | Description |
|--------|-------------|
| **Identity Boundary** | All users, groups, service principals, and managed identities |
| **Directory** | Single Microsoft Entra directory per tenant |
| **Global Uniqueness** | Tenant ID is globally unique (GUID) |
| **Trust Relationship** | Subscriptions trust the tenant for authentication |
| **Multi-Tenant Isolation** | RBAC and policies don't span tenants |

**Example:**
```
Tenant: contoso.onmicrosoft.com
Tenant ID: a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6

Users:
  - john.doe@contoso.com
  - jane.smith@contoso.com

Subscriptions:
  - Production (Sub-001)
  - Development (Sub-002)
  - Testing (Sub-003)
```

**Important Facts:**
- ✅ Can have multiple subscriptions in one tenant
- ✅ Can have multiple management group hierarchies (one per tenant)
- ❌ Cannot share RBAC assignments across tenants
- ❌ Cannot merge tenants easily
- ⚠️ Multi-tenant scenarios require separate configurations

### 2. Management Groups

**What They Are:**
- Organizational containers for subscriptions
- Provide hierarchical structure for governance
- Enable enterprise-scale management
- Optional but recommended for organizations with multiple subscriptions

**Key Characteristics:**

| Aspect | Description |
|--------|-------------|
| **Hierarchy Depth** | Up to 6 levels (not including root) |
| **Maximum Count** | 10,000 management groups per tenant |
| **Root Management Group** | Automatically created per tenant |
| **Single Parent** | Each management group or subscription has one parent |
| **Policy Inheritance** | Policies cascade to all children |
| **RBAC Inheritance** | Role assignments cascade to all children |

**Management Group Hierarchy Example:**

```
Root Management Group (Tenant Root Group)
│
├── Production
│   ├── Corp-Production
│   │   ├── Subscription: Corp-Prod-001
│   │   └── Subscription: Corp-Prod-002
│   │
│   └── Online-Production
│       ├── Subscription: Online-Prod-001
│       └── Subscription: Online-Prod-002
│
├── Non-Production
│   ├── Development
│   │   ├── Subscription: Dev-001
│   │   └── Subscription: Dev-002
│   │
│   └── Testing
│       ├── Subscription: Test-001
│       └── Subscription: Test-002
│
└── Sandbox
    └── Subscription: Sandbox-001
```

**Use Cases:**

| Use Case | Example |
|----------|---------|
| **Policy Enforcement** | Require all production resources to have specific tags |
| **Security Standards** | Enforce encryption on all storage accounts |
| **RBAC at Scale** | Grant Network Contributor to network team across all subscriptions |
| **Cost Management** | View aggregated costs across business units |
| **Compliance** | Apply regulatory compliance policies (PCI-DSS, HIPAA) |

**Management Group Commands:**

```bash
# List all management groups
az account management-group list

# Create management group
az account management-group create \
  --name Production \
  --display-name "Production Management Group"

# Move subscription to management group
az account management-group subscription add \
  --name Production \
  --subscription "Sub-001"

# Assign policy at management group
az policy assignment create \
  --name "require-tags" \
  --policy "require-resource-tags" \
  --scope "/providers/Microsoft.Management/managementGroups/Production"
```

### 3. Subscriptions

**What They Are:**
- Logical containers for resources
- Billing boundary for Azure services
- Provide resource quotas and limits
- Trust a single Microsoft Entra tenant for authentication

**Key Characteristics:**

| Aspect | Description |
|--------|-------------|
| **Billing Boundary** | Separate bill generated for each subscription |
| **Access Control Boundary** | RBAC can be applied at subscription level |
| **Resource Limits** | Quotas apply per subscription (e.g., 980 VMs per region) |
| **Single Tenant** | Must belong to exactly one tenant |
| **Single Parent** | Can belong to one management group at a time |
| **Movable** | Can be moved between management groups |

**Subscription Types:**

| Type | Use Case | Billing |
|------|----------|---------|
| **Free** | Trial/learning | $200 credit for 30 days |
| **Pay-As-You-Go** | Production workloads | Monthly based on usage |
| **Enterprise Agreement (EA)** | Large organizations | Annual commitment |
| **CSP (Cloud Solution Provider)** | Partner-managed | Through partner |
| **Visual Studio** | Dev/Test workloads | Monthly credit included |

**Common Subscription Patterns:**

**Pattern 1: Environment Separation**
```
├── Subscription: Production
├── Subscription: Staging
├── Subscription: Development
└── Subscription: Testing
```

**Pattern 2: Business Unit Separation**
```
├── Subscription: Marketing
├── Subscription: Sales
├── Subscription: Engineering
└── Subscription: Operations
```

**Pattern 3: Application Separation**
```
├── Subscription: WebApp-Production
├── Subscription: MobileApp-Production
├── Subscription: API-Production
└── Subscription: Analytics-Production
```

**Subscription Limits (Selected Examples):**

| Resource | Limit per Subscription |
|----------|------------------------|
| Resource Groups | 980 per subscription |
| Virtual Networks | 1,000 per subscription per region |
| Storage Accounts | 250 per subscription per region |
| Public IP Addresses | 1,000 per region |
| Load Balancers | 1,000 per subscription per region |

**Subscription Commands:**

```bash
# List subscriptions
az account list --output table

# Show current subscription
az account show

# Set active subscription
az account set --subscription "Sub-001"

# Create resource group in subscription
az group create \
  --name RG-WebApp \
  --location eastus \
  --subscription "Sub-001"
```

### 4. Resource Groups

**What They Are:**
- Logical containers for Azure resources
- Lifecycle management boundary
- Share common lifecycle (deployed, updated, deleted together)
- Must exist in a single region (metadata only)

**Key Characteristics:**

| Aspect | Description |
|--------|-------------|
| **Lifecycle Boundary** | Resources deployed and deleted together |
| **Regional Metadata** | Resource group metadata stored in specific region |
| **Resource Regions** | Resources inside can be in any region |
| **Access Control** | RBAC can be applied at resource group level |
| **Cannot Nest** | Resource groups cannot contain other resource groups |
| **Single Subscription** | Must belong to exactly one subscription |

**Resource Group Naming Conventions:**

```
Pattern: RG-{App/Service}-{Environment}-{Region}

Examples:
  - RG-WebApp-Prod-EastUS
  - RG-SQL-Dev-WestEurope
  - RG-Network-Hub-CentralUS
  - RG-Storage-Prod-Global
  - RG-Analytics-Test-EastUS2
```

**Use Cases:**

| Use Case | Example | Why Resource Groups? |
|----------|---------|---------------------|
| **Application Grouping** | Web app + SQL database + Storage | Deploy and delete together |
| **Environment Isolation** | Separate RGs for Dev, Test, Prod | Different access controls |
| **Shared Services** | Networking hub (VNet, Firewall, VPN) | Shared lifecycle |
| **Project-Based** | Resources for specific project | Clear boundaries |
| **Department-Based** | Marketing resources | Separate billing/access |

**Resource Group Structure Example:**

```
Subscription: Production
│
├── RG-WebApp-Frontend-Prod
│   ├── App Service Plan
│   ├── Web App
│   ├── Application Insights
│   └── CDN Profile
│
├── RG-Database-Prod
│   ├── Azure SQL Server
│   ├── SQL Database
│   └── SQL Elastic Pool
│
├── RG-Storage-Prod
│   ├── Storage Account (Data Lake)
│   ├── Storage Account (Blob)
│   └── Storage Account (Files)
│
├── RG-Network-Hub
│   ├── Virtual Network (Hub)
│   ├── Azure Firewall
│   ├── VPN Gateway
│   └── Network Security Groups
│
└── RG-Security-Shared
    ├── Key Vault (Secrets)
    ├── Key Vault (Certificates)
    └── Log Analytics Workspace
```

**Resource Group Best Practices:**

1. **Group by Lifecycle**
   ```
   ✅ Web app and its database together (same lifecycle)
   ❌ Production and development resources together (different lifecycles)
   ```

2. **Consider Access Control**
   ```
   ✅ Separate RG for sensitive data (restricted access)
   ✅ Separate RG for shared resources (broader access)
   ```

3. **Plan for Deletion**
   ```
   ✅ Group temporary/ephemeral resources separately
   ✅ Makes cleanup easier (delete entire RG)
   ```

4. **Use Consistent Naming**
   ```
   ✅ RG-{Project}-{Environment}-{Region}
   ✅ Makes automation and management easier
   ```

**Resource Group Commands:**

```bash
# Create resource group
az group create \
  --name RG-WebApp-Prod \
  --location eastus \
  --tags Environment=Production Project=WebApp

# List resource groups
az group list --output table

# Show resources in resource group
az resource list \
  --resource-group RG-WebApp-Prod \
  --output table

# Delete resource group (deletes all resources)
az group delete \
  --name RG-WebApp-Prod \
  --yes \
  --no-wait

# Lock resource group to prevent deletion
az lock create \
  --name DontDelete \
  --lock-type CanNotDelete \
  --resource-group RG-WebApp-Prod
```

### 5. Resources

**What They Are:**
- Individual Azure services and components
- The actual compute, storage, networking, and other services
- Must belong to exactly one resource group
- Billed at the resource level

**Key Characteristics:**

| Aspect | Description |
|--------|-------------|
| **Single Resource Group** | Must belong to exactly one resource group |
| **Any Region** | Can be in any region regardless of resource group location |
| **Movable** | Can be moved between resource groups (with limitations) |
| **Resource ID** | Unique identifier in Azure |
| **Tags** | Metadata for organization and cost tracking |
| **Locks** | Can be protected from accidental deletion |

**Resource Categories:**

| Category | Examples |
|----------|----------|
| **Compute** | Virtual Machines, App Services, Functions, AKS |
| **Storage** | Blob Storage, File Storage, Disks, Data Lake |
| **Networking** | Virtual Networks, Load Balancers, Application Gateway, VPN |
| **Databases** | SQL Database, Cosmos DB, MySQL, PostgreSQL, Redis |
| **Security** | Key Vault, Security Center, Sentinel |
| **Identity** | Managed Identities, App Registrations |
| **Monitoring** | Log Analytics, Application Insights, Alerts |
| **Integration** | Logic Apps, Service Bus, Event Grid, API Management |

**Resource ID Format:**

```
/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{resource-provider}/{resource-type}/{resource-name}

Example:
/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
  resourceGroups/RG-WebApp-Prod/
  providers/Microsoft.Web/
  sites/mywebapp
```

**Resource Tagging Strategy:**

```bash
# Apply tags to resources
az resource tag \
  --resource-group RG-WebApp-Prod \
  --name mywebapp \
  --resource-type Microsoft.Web/sites \
  --tags \
    Environment=Production \
    Project=WebApp \
    CostCenter=CC-1001 \
    Owner=john.doe@contoso.com \
    Criticality=High

# Common tag schema
Tags:
  - Environment: Production | Staging | Development | Testing
  - Project: ProjectA | ProjectB | ProjectC
  - CostCenter: CC-1001 | CC-1002 | CC-1003
  - Owner: Email of responsible person
  - Department: Engineering | Marketing | Sales
  - Application: WebApp | API | Database
  - Criticality: High | Medium | Low
  - DataClassification: Public | Internal | Confidential | Restricted
```

## Scope and Inheritance

Azure policies, RBAC role assignments, and other settings inherit down the hierarchy.

**Inheritance Flow:**

```
┌──────────────────────────────┐
│    Management Group          │  ← Policy: Require tags
│    (Production)              │  ← RBAC: Reader role for auditors
└──────────────────────────────┘
            ↓ Inherits
┌──────────────────────────────┐
│    Subscription              │  ← Policy: Allowed VM sizes
│    (Prod-001)                │  ← RBAC: Contributor for dev team
└──────────────────────────────┘
            ↓ Inherits
┌──────────────────────────────┐
│    Resource Group            │  ← RBAC: Owner for app team
│    (RG-WebApp-Prod)          │
└──────────────────────────────┘
            ↓ Inherits
┌──────────────────────────────┐
│    Resource                  │  ← RBAC: Specific permissions
│    (Web App)                 │
└──────────────────────────────┘
```

**Effective Permissions:**
- The Web App has ALL policies from Management Group, Subscription, and Resource Group
- The Web App inherits RBAC assignments from all levels
- Lower-level assignments ADD to higher-level assignments
- Deny assignments override Allow assignments

**Inheritance Example:**

```
Management Group: Production
  ├─ Policy: All resources must have "Environment" tag
  ├─ Policy: Encryption required on storage accounts
  ├─ RBAC: Security team has Reader access
  │
  └─ Subscription: Prod-001
      ├─ Policy: Allowed regions = East US, West US
      ├─ RBAC: Platform team has Contributor access
      │
      └─ Resource Group: RG-WebApp-Prod
          ├─ RBAC: App team has Owner access
          │
          └─ Resource: Storage Account
              • Effective Policies:
                  ✓ Must have "Environment" tag (from MG)
                  ✓ Must have encryption enabled (from MG)
                  ✓ Must be in East US or West US (from Subscription)
              • Effective RBAC:
                  ✓ Security team: Reader (from MG)
                  ✓ Platform team: Contributor (from Subscription)
                  ✓ App team: Owner (from Resource Group)
```

## RBAC Scope Hierarchy

**Scope Levels for RBAC:**

| Scope Level | Description | Impact | Use Case |
|-------------|-------------|--------|----------|
| **Management Group** | Applies to all child management groups and subscriptions | Widest | Enterprise-wide roles |
| **Subscription** | Applies to all resource groups and resources | Wide | Subscription-level admins |
| **Resource Group** | Applies to all resources in the group | Moderate | Project team access |
| **Resource** | Applies to single resource only | Narrow | Specific resource access |

**RBAC Assignment Examples:**

```bash
# Management Group scope (widest)
az role assignment create \
  --role "Reader" \
  --assignee "auditors@contoso.com" \
  --scope "/providers/Microsoft.Management/managementGroups/Production"

# Subscription scope
az role assignment create \
  --role "Contributor" \
  --assignee "devteam@contoso.com" \
  --scope "/subscriptions/a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Resource Group scope
az role assignment create \
  --role "Owner" \
  --assignee "appteam@contoso.com" \
  --scope "/subscriptions/.../resourceGroups/RG-WebApp-Prod"

# Resource scope (narrowest)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee "myapp-identity" \
  --scope "/subscriptions/.../resourceGroups/.../providers/Microsoft.KeyVault/vaults/myvault"
```

**Principle of Least Privilege:**

```
✅ Best Practice: Assign at the narrowest scope needed

Example: App needs access to specific Key Vault
  ✅ Assign at Key Vault resource scope
  ❌ Don't assign at subscription scope
  
Example: Team manages all resources in resource group
  ✅ Assign at resource group scope
  ❌ Don't assign at subscription scope
  
Example: Platform team manages all subscriptions
  ✅ Assign at management group scope
  ✅ Appropriate for their responsibility
```

## Azure Policy Inheritance

**Policy Application Hierarchy:**

```
Root Management Group
├─ Policy: Require backup on all VMs
│  └─ Applies to ALL subscriptions and resources
│
└─ Management Group: Production
    ├─ Policy: Require high availability for databases
    │  └─ Applies to Production subscriptions only
    │
    └─ Subscription: Prod-001
        ├─ Policy: Allowed VM SKUs = Standard_D*
        │  └─ Applies to Prod-001 subscription only
        │
        └─ Resource Group: RG-Database-Prod
            • Effective policies:
              ✓ Backup required (from Root MG)
              ✓ High availability required (from Production MG)
              ✓ Only Standard_D* VMs allowed (from Subscription)
```

**Policy Evaluation:**

| Policy Type | Effect | Example |
|-------------|--------|---------|
| **Deny** | Prevents resource creation/modification | Deny VMs in disallowed regions |
| **Audit** | Logs non-compliance (doesn't block) | Audit VMs without backup |
| **Append** | Adds properties to resources | Append tags to all resources |
| **Modify** | Changes resource properties | Enable encryption on storage |
| **DeployIfNotExists** | Deploys resources if conditions met | Deploy diagnostic settings |

**Common Policy Examples:**

```bash
# Require tags on all resources
az policy assignment create \
  --name "require-tags" \
  --policy "require-resource-tags" \
  --scope "/providers/Microsoft.Management/managementGroups/Root" \
  --params '{"tagName": {"value": "Environment"}}'

# Allowed locations
az policy assignment create \
  --name "allowed-locations" \
  --policy "allowed-locations" \
  --scope "/subscriptions/..." \
  --params '{"listOfAllowedLocations": {"value": ["eastus", "westus"]}}'

# Require encryption on storage accounts
az policy assignment create \
  --name "storage-encryption" \
  --policy "storage-account-encryption" \
  --scope "/subscriptions/.../resourceGroups/RG-Storage-Prod"
```

## Management Group Best Practices

### 1. Plan Hierarchy Carefully

```
✅ Good Hierarchy (Aligned with Organization):
Root
├── Production
│   ├── Core-Systems
│   └── Customer-Facing
├── Non-Production
│   ├── Development
│   └── Testing
└── Sandbox

❌ Bad Hierarchy (Too Deep/Complex):
Root
├── Region-US
│   ├── State-NY
│   │   ├── City-NYC
│   │   │   ├── Building-A
│   │   │   │   ├── Floor-1
│   │   │   │   │   └── Department-...
```

### 2. Keep It Simple

```
✅ Recommended depth: 2-3 levels
❌ Avoid: Maximum 6 levels (hard to manage)

Example:
Root → Environment → Business Unit → Subscription
```

### 3. Use for Governance, Not Organization

```
✅ Good Use Cases:
  • Apply security policies
  • Enforce compliance standards
  • RBAC at scale
  • Cost aggregation

❌ Bad Use Cases:
  • Detailed project organization (use tags)
  • Frequent restructuring (use tags)
  • Per-application grouping (use resource groups)
```

### 4. Leverage Policy Inheritance

```
Root Management Group:
  ├─ Policy: Require tags (applies everywhere)
  ├─ Policy: Require encryption
  ├─ RBAC: Security team as Reader

Production Management Group:
  ├─ Policy: High availability required
  ├─ Policy: Backup enabled
  ├─ RBAC: Auditors as Reader

Non-Production Management Group:
  ├─ Policy: Auto-shutdown for VMs
  ├─ Policy: Lower-cost SKUs allowed
  ├─ RBAC: Developers as Contributor
```

### 5. Document Your Hierarchy

```markdown
# Contoso Management Group Structure

## Root Management Group
- **Purpose**: Organization-wide policies and RBAC
- **Policies**: 
  - Require tags: Environment, Project, CostCenter
  - Require encryption for storage and SQL
- **RBAC**: 
  - Security team: Reader
  - Compliance team: Reader

## Production Management Group
- **Purpose**: Production workloads
- **Policies**:
  - High availability requirements
  - Backup policies
  - Allowed regions: East US, West US
- **RBAC**:
  - Platform team: Contributor
  - Auditors: Reader

## Non-Production Management Group
- **Purpose**: Development and testing
- **Policies**:
  - Auto-shutdown for VMs (cost savings)
  - Lower-cost SKUs allowed
- **RBAC**:
  - Development team: Contributor
```

## Resource Organization Patterns

### Pattern 1: Environment-Based

```
Root Management Group
├── Production
│   └── Subscription: Prod-001
│       ├── RG-WebApp-Prod
│       ├── RG-Database-Prod
│       └── RG-Network-Prod
├── Staging
│   └── Subscription: Staging-001
│       ├── RG-WebApp-Staging
│       └── RG-Database-Staging
└── Development
    └── Subscription: Dev-001
        ├── RG-WebApp-Dev
        └── RG-Database-Dev

Benefits:
✅ Clear environment separation
✅ Different policies per environment
✅ Isolated billing
✅ Easy to understand
```

### Pattern 2: Business Unit-Based

```
Root Management Group
├── Marketing
│   └── Subscriptions for Marketing teams
│       ├── RG-CampaignApp-Prod
│       ├── RG-Analytics-Prod
│       └── RG-ContentManagement
├── Sales
│   └── Subscriptions for Sales teams
│       ├── RG-CRM-Prod
│       └── RG-Reporting
└── Engineering
    └── Subscriptions for Engineering teams
        ├── RG-PlatformServices
        ├── RG-APIGateway
        └── RG-SharedInfra

Benefits:
✅ Department-based cost allocation
✅ Clear ownership
✅ Independent governance
```

### Pattern 3: Application-Based

```
Root Management Group
├── Production
│   ├── Subscription: WebApp
│   │   ├── RG-WebApp-Frontend
│   │   ├── RG-WebApp-Backend
│   │   └── RG-WebApp-Database
│   ├── Subscription: MobileApp
│   │   ├── RG-MobileApp-API
│   │   └── RG-MobileApp-Backend
│   └── Subscription: SharedServices
│       ├── RG-NetworkHub
│       ├── RG-Monitoring
│       └── RG-Security
└── Non-Production
    └── (Similar structure for dev/test)

Benefits:
✅ Clear application boundaries
✅ Independent scaling
✅ Separate subscription limits
```

### Pattern 4: Hybrid (Recommended)

```
Root Management Group
│
├── Production
│   ├── Corp (Internal applications)
│   │   ├── Subscription: Corp-Prod-001
│   │   │   ├── RG-IntranetApp-Prod
│   │   │   └── RG-HRSystem-Prod
│   │   └── Subscription: Corp-Prod-002
│   │
│   └── Online (Customer-facing)
│       ├── Subscription: Online-Prod-001
│       │   ├── RG-ECommerce-Frontend
│       │   └── RG-ECommerce-Backend
│       └── Subscription: Online-Prod-002
│
├── Non-Production
│   ├── Development
│   │   └── Subscription: Dev-001
│   │       ├── RG-Dev-Project1
│   │       └── RG-Dev-Project2
│   └── Testing
│       └── Subscription: Test-001
│
└── Platform (Shared services)
    └── Subscription: Platform-001
        ├── RG-Network-Hub
        ├── RG-Monitoring-Shared
        ├── RG-Security-Shared
        └── RG-DevOps-Shared

Benefits:
✅ Combines multiple organization styles
✅ Flexible and scalable
✅ Clear governance boundaries
✅ Realistic for enterprises
```

## Multi-Tenant Considerations

### Understanding Tenant Boundaries

**Critical Fact:** RBAC role assignments and management group hierarchies are **scoped to a single Microsoft Entra tenant**.

```
Tenant 1: contoso.onmicrosoft.com
├── Management Group Hierarchy
├── Subscriptions
├── RBAC Assignments
└── Azure AD Users/Groups

Tenant 2: dev.contoso.onmicrosoft.com
├── Separate Management Group Hierarchy
├── Separate Subscriptions
├── Separate RBAC Assignments
└── Separate Azure AD Users/Groups

❌ Cannot create single RBAC assignment spanning both tenants
❌ Cannot share management group hierarchy
❌ Cannot merge tenants easily
```

### Multi-Tenant Scenarios

**Scenario 1: Development/Test Isolation**
```
Production Tenant: contoso.com
├── 10 production subscriptions
└── Production resources

Dev/Test Tenant: dev.contoso.com
├── 5 development/test subscriptions
└── Development resources

Challenge: Need to grant Network Contributor role across all VNets
Solution: Minimum 2 RBAC assignments (one per tenant)
```

**Scenario 2: Mergers & Acquisitions**
```
Parent Company Tenant: parentco.com
├── Parent company subscriptions

Acquired Company Tenant: acquired.com
├── Acquired company subscriptions

Challenge: Maintain separate tenants for compliance
Solution: Manage governance separately per tenant
```

**Scenario 3: Multi-Tenant SaaS**
```
Service Provider Tenant: provider.com
├── Service infrastructure

Customer Tenant 1: customer1.com
├── Customer-specific resources

Customer Tenant 2: customer2.com
├── Customer-specific resources

Challenge: Manage customer resources in customer tenants
Solution: Azure Lighthouse for cross-tenant management
```

### Multi-Tenant RBAC Formula

```
Minimum RBAC assignments (at management group level) = Number of tenants

Example:
  2 tenants = Minimum 2 assignments
  5 tenants = Minimum 5 assignments
  
Why: Each tenant requires its own RBAC configuration
```

## Practice Questions

### Question 1: Resource Hierarchy Scope

**Scenario:**
You need to ensure all Azure resources in your organization have the tags "Environment" and "CostCenter". You want to apply this with the minimum number of policy assignments.

**Question:**
At which scope should you assign the Azure Policy?

**Options:**

1. **Resource Group** ❌
   - Would require creating policy assignments for each resource group
   - Not efficient for organization-wide requirements

2. **Subscription** ❌
   - Would require creating policy assignments for each subscription
   - Better than resource group but not optimal

3. **Root Management Group** ✅
   - Single policy assignment applies to all subscriptions and resources
   - Most efficient for organization-wide requirements
   - Policies cascade down the entire hierarchy

4. **Individual Resources** ❌
   - Most inefficient approach
   - Would require thousands of policy assignments

**Answer:** Root Management Group

**Explanation:**
Assigning the policy at the root management group level ensures it applies to all child management groups, subscriptions, resource groups, and resources with a single assignment. This leverages policy inheritance and is the most efficient approach for organization-wide requirements.

---

### Question 2: RBAC Assignment Scope

**Scenario:**
Your development team needs Contributor access to all resources in the "RG-WebApp-Dev" resource group. No other resource groups should be accessible.

**Question:**
At which scope should you assign the Contributor role?

**Options:**

1. **Subscription** ❌
   - Grants access to all resource groups in the subscription
   - Violates principle of least privilege

2. **Resource Group** ✅
   - Grants access only to resources in RG-WebApp-Dev
   - Follows principle of least privilege
   - Meets the exact requirement

3. **Management Group** ❌
   - Grants access to multiple subscriptions
   - Far too broad for the requirement

4. **Individual Resources** ❌
   - Would work but requires multiple assignments
   - Not efficient when team needs access to all resources in RG

**Answer:** Resource Group

**Explanation:**
Assigning at the resource group scope provides exactly the access needed—nothing more, nothing less. This follows the principle of least privilege and is the most appropriate scope for team-level access to a specific set of resources.

---

### Question 3: Multi-Subscription Organization

**Scenario:**
Your organization has 15 subscriptions across different business units. You need to enforce that all storage accounts have encryption enabled and that only specific Azure regions are allowed.

**Question:**
What is the most efficient approach?

**Options:**

1. **Create policy assignments in each subscription** ❌
   - Requires 30 policy assignments (2 policies × 15 subscriptions)
   - High management overhead
   - Error-prone

2. **Create policy assignments at root management group** ✅
   - Requires only 2 policy assignments
   - Applies to all subscriptions automatically
   - Centralized management
   - Easy to maintain

3. **Create policy assignments in each resource group** ❌
   - Requires hundreds of policy assignments
   - Extremely inefficient
   - Unmanageable

4. **Use Azure Security Center recommendations only** ❌
   - Recommendations are advisory, not enforced
   - Won't prevent non-compliant resources

**Answer:** Create policy assignments at root management group

**Explanation:**
Management groups provide centralized governance. Two policy assignments at the root level will cascade to all 15 subscriptions, providing consistent enforcement with minimal management overhead.

---

### Question 4: Resource Group Design

**Scenario:**
You are deploying a web application with the following components:
- Front-end web app (App Service)
- Back-end API (App Service)
- SQL Database
- Azure Storage
- Application Insights

All components will be deployed together and deleted together. They all support the same application in production.

**Question:**
How should you organize these resources?

**Options:**

1. **Create separate resource groups for each component** ❌
   - Complicates deployment
   - Makes deletion cumbersome
   - Doesn't align with lifecycle

2. **Create one resource group for all components** ✅
   - Aligns with shared lifecycle
   - Simplifies deployment and deletion
   - Appropriate RBAC scope (app team gets access to all)
   - Easy to manage

3. **Create separate subscriptions for each component** ❌
   - Massive overkill
   - Unnecessary billing complexity
   - Complicates networking

4. **Create management group for the application** ❌
   - Management groups contain subscriptions, not resources
   - Wrong level of hierarchy

**Answer:** Create one resource group for all components

**Explanation:**
Resource groups should align with resource lifecycle. Since all components support the same application and share the same deployment/deletion lifecycle, they belong in a single resource group. This simplifies management and follows Azure best practices.

---

### Question 5: Multi-Tenant RBAC

**Scenario:**
Contoso Inc. has two Microsoft Entra tenants:
- `contoso.com` with 8 subscriptions
- `dev.contoso.com` with 4 subscriptions

You need to grant the Storage Blob Data Reader role to the data science team across all storage accounts in both tenants. You want to use the most efficient approach possible.

**Question:**
What is the minimum number of RBAC role assignments required?

**Options:**

1. **1** ❌
   - RBAC assignments cannot span multiple tenants
   - Single assignment only works within one tenant

2. **2** ✅
   - One assignment per tenant (each at root management group)
   - Each assignment covers all subscriptions in its tenant
   - Minimum required due to tenant isolation

3. **12** ❌
   - This would be subscription-level assignments (8 + 4)
   - Not needed when using management groups

4. **Cannot be done - need separate identities per tenant** ❌
   - Can be done with guest users or per-tenant identities
   - But still requires 2 assignments (one per tenant)

**Answer:** 2

**Explanation:**
RBAC assignments are tenant-scoped. Even when using management groups, you cannot create a single assignment that spans multiple tenants. Therefore, you need one assignment in each tenant's root management group, resulting in a minimum of 2 assignments.

**Key Takeaway:** Tenant boundaries are absolute in Azure. RBAC, policies, and management group hierarchies are all isolated per tenant.

---

### Question 6: Cost Management Hierarchy

**Scenario:**
You want to track and set budgets for costs across multiple projects (ProjectA, ProjectB, ProjectC). Each project uses resources across all 10 subscriptions in your organization.

**Question:**
What is the most appropriate approach?

**Options:**

1. **Create management groups per project and move subscriptions** ❌
   - Subscriptions can only be in one management group
   - Projects span multiple subscriptions
   - Would require restructuring entire subscription hierarchy

2. **Create separate resource groups per project** ❌
   - Projects span multiple subscriptions
   - Resource groups can't span subscriptions
   - Doesn't solve the problem

3. **Apply resource tags per project and use tag-based budgets** ✅
   - Tags can cross subscription boundaries
   - Tag-based budgets can filter across all subscriptions
   - Flexible and doesn't require restructuring
   - Aligns with cross-cutting concerns

4. **Create separate subscriptions per project** ❌
   - Would require 30 subscriptions (3 projects × 10 original subs)
   - Extremely complex to manage
   - Not practical

**Answer:** Apply resource tags per project and use tag-based budgets

**Explanation:**
Management groups and subscriptions create rigid hierarchical boundaries. For cross-cutting concerns like projects that span multiple subscriptions, resource tags provide the flexibility needed. Tag-based budgets allow you to track costs for resources with specific tags regardless of their location in the hierarchy.

---

## Summary

### Key Hierarchy Levels

| Level | Purpose | Key Features |
|-------|---------|--------------|
| **Tenant** | Identity boundary | Single directory, all users/groups |
| **Management Group** | Governance | Policy and RBAC inheritance, 6 levels deep |
| **Subscription** | Billing boundary | Separate billing, resource quotas |
| **Resource Group** | Lifecycle boundary | Deploy/delete together, single region metadata |
| **Resource** | Azure service | Must belong to one resource group |

### Hierarchy Flow Summary

```
Tenant (Identity)
  ↓
Management Groups (Governance)
  ↓
Subscriptions (Billing)
  ↓
Resource Groups (Lifecycle)
  ↓
Resources (Services)
```

### When to Use Each Level

| Need | Use This Level | Why |
|------|---------------|-----|
| Organization-wide policies | Root Management Group | Single assignment, applies everywhere |
| Business unit separation | Management Groups | Hierarchical governance |
| Billing isolation | Subscriptions | Separate bills and quotas |
| Application grouping | Resource Groups | Shared lifecycle |
| Service deployment | Resources | Actual services |
| Cross-cutting concerns | Tags | Flexible, spans hierarchy |

### Best Practices Summary

1. ✅ Plan management group hierarchy carefully (2-3 levels ideal)
2. ✅ Use management groups for governance, not detailed organization
3. ✅ Assign RBAC at the narrowest scope needed
4. ✅ Use tags for cross-cutting concerns (projects, cost centers)
5. ✅ Align resource groups with application lifecycle
6. ✅ Document your hierarchy and naming conventions
7. ✅ Remember: Tenant boundaries are absolute
8. ✅ Leverage policy and RBAC inheritance
9. ✅ Keep subscription count manageable
10. ✅ Use consistent naming conventions

---

**Last Updated:** December 2025
