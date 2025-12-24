# Azure Policy - Complete Overview

## Table of Contents

- [Introduction](#introduction)
- [Key Concepts](#key-concepts)
- [Policy Definition](#policy-definition)
- [Policy Effects](#policy-effects)
- [Policy Assignment](#policy-assignment)
- [Managed Identities for Policy](#managed-identities-for-policy)
- [Remediation Tasks](#remediation-tasks)
- [Policy Evaluation](#policy-evaluation)
- [Best Practices](#best-practices)
- [Practice Questions](#practice-questions)

## Introduction

**Azure Policy** is a service in Azure that enables you to create, assign, and manage policies that enforce rules and effects over your resources. These policies help maintain compliance with corporate standards and service level agreements.

### Key Benefits

- **Enforce organizational standards**: Ensure consistency across resources
- **Assess compliance at scale**: Evaluate resources against policies
- **Remediate non-compliant resources**: Automatically fix or flag violations
- **Built-in policies**: Leverage hundreds of pre-built policy definitions
- **Governance**: Apply governance standards across subscriptions

### Azure Policy vs RBAC

| Feature | Azure Policy | RBAC |
|---------|-------------|------|
| **Purpose** | Resource compliance and governance | Access control |
| **What it controls** | Resource properties and configurations | Who can perform actions |
| **Default behavior** | Non-restrictive (allow by default) | Restrictive (deny by default) |
| **Evaluation** | Evaluates existing and new resources | Evaluates user permissions |
| **Example** | "All storage accounts must use HTTPS" | "User can create storage accounts" |

## Key Concepts

### 1. Policy Definition

A **policy definition** describes the compliance conditions and the effect to take if conditions are met. It's a JSON document that defines:

- **If condition**: Resource properties to evaluate
- **Then effect**: Action to take (deny, audit, append, etc.)

**Example Policy Definition Structure:**

```json
{
  "properties": {
    "displayName": "Require SSL on storage accounts",
    "description": "Ensures all storage accounts use HTTPS",
    "mode": "All",
    "parameters": {},
    "policyRule": {
      "if": {
        "allOf": [
          {
            "field": "type",
            "equals": "Microsoft.Storage/storageAccounts"
          },
          {
            "field": "Microsoft.Storage/storageAccounts/supportsHttpsTrafficOnly",
            "notEquals": "true"
          }
        ]
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

### 2. Policy Definition Modes

The **mode** property in a policy definition determines which resource types are evaluated. Understanding modes is crucial for creating effective policies.

**Valid Modes:**

| Mode | Description | Evaluates |
|------|-------------|-----------|
| **All** | Evaluates all resource types and locations within the scope | Resource groups, subscriptions, and all resource types |
| **Indexed** | Evaluates only resource types that support tags and location | Resources that support tags and location properties |

> ⚠️ **Important**: `DoNotAllow` is **NOT** a valid mode for Azure Policy definitions. It is often confused with the `Deny` effect, but mode and effect are different properties.

**When to Use Each Mode:**

| Mode | Use Case | Example |
|------|----------|---------|
| **All** | Policies that need to evaluate all resources including resource groups | Require tags on resource groups |
| **Indexed** | Policies that evaluate specific resource properties like tags or location | Require specific tags on resources |

**Mode in Policy Definition:**

```json
{
  "properties": {
    "displayName": "Require a tag on resources",
    "description": "Enforces a required tag on resources",
    "mode": "Indexed",
    "policyRule": {
      "if": {
        "field": "tags['Environment']",
        "exists": "false"
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

**Key Differences:**

| Aspect | All Mode | Indexed Mode |
|--------|----------|--------------|
| **Resource Groups** | ✅ Evaluated | ❌ Not evaluated |
| **Subscriptions** | ✅ Evaluated | ❌ Not evaluated |
| **Tag-based policies** | ✅ Works | ✅ Works (recommended) |
| **Location-based policies** | ✅ Works | ✅ Works (recommended) |

> 💡 **Best Practice**: Use `Indexed` mode for tag and location policies to avoid evaluating resources that don't support these properties. Use `All` mode when you need to evaluate resource groups or apply policies to all resource types.

### 3. Policy Assignment

A **policy assignment** applies a policy definition to a specific scope:

- Management group
- Subscription  
- Resource group
- Individual resource

### 4. Initiative Definition (Policy Set)

An **initiative** is a collection of policy definitions grouped together. It simplifies management of multiple related policies.

**Example:** Azure Security Benchmark initiative contains 200+ individual policies.

### 4. Policy Parameters

Parameters make policy definitions reusable by allowing values to be specified at assignment time.

```json
{
  "parameters": {
    "allowedLocations": {
      "type": "Array",
      "metadata": {
        "description": "List of allowed Azure regions"
      }
    }
  }
}
```

## Policy Effects

Policy effects determine what happens when a policy rule is matched. Azure supports several effects:

| Effect | Description | Use Case | Modifies Resources |
|--------|-------------|----------|-------------------|
| **Deny** | Prevents resource creation/update | Block non-compliant configurations | No |
| **Audit** | Creates warning event in log | Track non-compliance without blocking | No |
| **Append** | Adds fields to resource | Add required tags during creation | Yes (at creation) |
| **Modify** | Updates properties/tags on resources | Update tags or properties | Yes |
| **DeployIfNotExists** | Deploys resource if doesn't exist | Deploy diagnostic settings, extensions | Yes |
| **AuditIfNotExists** | Audits if related resource doesn't exist | Check for backup configuration | No |
| **Disabled** | Policy evaluation disabled | Temporarily disable policy | No |

### Effect Details

#### Deny
- **Blocks** resource creation or updates that don't meet policy conditions
- Most restrictive effect
- **Use when:** You want to prevent non-compliant resources

```json
{
  "then": {
    "effect": "deny"
  }
}
```

#### Audit
- **Logs** non-compliant resources but allows creation
- Creates warning events in Activity Log
- **Use when:** You want visibility without enforcement

```json
{
  "then": {
    "effect": "audit"
  }
}
```

#### Append
- **Adds** specified fields to resources during creation
- Cannot modify existing resources
- **Use when:** You want to add tags or properties automatically

```json
{
  "then": {
    "effect": "append",
    "details": [
      {
        "field": "tags['Environment']",
        "value": "Production"
      }
    ]
  }
}
```

#### Modify
- **Changes** properties or tags on new or existing resources
- Requires remediation task for existing resources
- **Use when:** You need to update resource properties or tags
- More powerful than append (can update existing resources)

```json
{
  "then": {
    "effect": "modify",
    "details": {
      "roleDefinitionIds": [
        "/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"
      ],
      "operations": [
        {
          "operation": "addOrReplace",
          "field": "tags['Environment']",
          "value": "Production"
        }
      ]
    }
  }
}
```

#### DeployIfNotExists
- **Deploys** a resource if it doesn't exist
- Requires managed identity with appropriate permissions
- **Use when:** You want to ensure companion resources exist
- **Common scenarios:**
  - Enable diagnostic settings
  - Deploy monitoring agents
  - Enable security features (like TDE, Microsoft Defender)

```json
{
  "then": {
    "effect": "deployIfNotExists",
    "details": {
      "type": "Microsoft.Insights/diagnosticSettings",
      "roleDefinitionIds": [
        "/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"
      ],
      "deployment": {
        "properties": {
          "mode": "incremental",
          "template": {
            // ARM template for deployment
          }
        }
      }
    }
  }
}
```

#### AuditIfNotExists
- **Audits** if a related resource doesn't exist
- Doesn't deploy resources (audit only)
- **Use when:** You want to check for companion resources without auto-remediation

```json
{
  "then": {
    "effect": "auditIfNotExists",
    "details": {
      "type": "Microsoft.Sql/servers/databases/transparentDataEncryption",
      "existenceCondition": {
        "field": "Microsoft.Sql/transparentDataEncryption.status",
        "equals": "Enabled"
      }
    }
  }
}
```

### Choosing Between Effects

```
Need to enforce compliance? 
  ↓
  Yes → Need to prevent creation?
         ↓
         Yes → Use DENY
         ↓
         No → Need to modify resources?
              ↓
              Yes → Need to deploy companion resources?
                    ↓
                    Yes → Use DEPLOYIFNOTEXISTS
                    ↓
                    No → Use MODIFY
              ↓
              No → Use AUDIT

  ↓
  No → Just want visibility?
        ↓
        Use AUDIT or AUDITIFNOTEXISTS
```

## Policy Assignment

### Assignment Process

1. **Create/Select policy definition** (or initiative)
2. **Assign to scope** (management group, subscription, resource group)
3. **Configure parameters** (if applicable)
4. **Set enforcement mode** (enabled/disabled)
5. **Configure managed identity** (for deployIfNotExists/modify effects)

### Assignment Structure

```json
{
  "properties": {
    "displayName": "Enforce HTTPS on storage accounts",
    "policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/{id}",
    "scope": "/subscriptions/{subscription-id}",
    "notScopes": [
      "/subscriptions/{subscription-id}/resourceGroups/exempted-rg"
    ],
    "parameters": {
      "effect": {
        "value": "Deny"
      }
    },
    "enforcementMode": "Default"
  }
}
```

### Enforcement Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Default** | Policy is enforced | Normal operations |
| **DoNotEnforce** | Policy logs but doesn't enforce | Testing policies before enforcement |

### Exclusions (NotScopes)

You can exclude specific scopes from policy assignments:

```bash
az policy assignment create \
  --name 'enforce-tags' \
  --policy 'require-tag-policy' \
  --scope '/subscriptions/xxx' \
  --not-scopes '/subscriptions/xxx/resourceGroups/test-rg'
```

## Managed Identities for Policy

Policies with **deployIfNotExists** or **modify** effects require a managed identity to make changes to resources.

### Identity Types

| Type | Creation | Scope | Use Case |
|------|----------|-------|----------|
| **System-assigned** | Auto-created with assignment | Single assignment | Most common, automatic |
| **User-assigned** | Pre-created separately | Multiple assignments | Shared across policies |

### System-Assigned Identity (Recommended)

**When you create a policy assignment through Azure Portal:**
- Azure automatically creates a system-assigned managed identity
- Azure assigns required role based on policy's `roleDefinitionIds`
- Identity is tied to the policy assignment lifecycle

**Benefits:**
- ✅ Automatic creation and management
- ✅ Automatic role assignment
- ✅ No separate identity management needed
- ✅ Deleted automatically when assignment is deleted

### User-Assigned Identity

**When to use:**
- Multiple policy assignments need same identity
- Custom security requirements
- Centralized identity management

**Requires manual steps:**
1. Create user-assigned managed identity
2. Assign required roles to identity
3. Reference identity in policy assignment

### Role Definitions

Policy definitions specify required roles in `roleDefinitionIds`:

```json
{
  "roleDefinitionIds": [
    "/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"
  ]
}
```

Common roles:
- **Contributor**: `b24988ac-6180-42a0-ab88-20f7382dd24c`
- **Owner**: `8e3af657-a8ff-443c-a75c-2fe8c4bcb635`
- **SQL Security Manager**: `056cd41c-7e88-42e1-933e-88ba6a50c9c3`

## Remediation Tasks

**Remediation tasks** apply deployIfNotExists or modify policies to existing non-compliant resources.

### Why Remediation is Needed

- Policies only affect **new** or **updated** resources by default
- Existing resources remain non-compliant
- Remediation tasks force evaluation and correction of existing resources

### When to Use Remediation

1. **After creating new policy assignment**: Fix existing resources
2. **For deployIfNotExists policies**: Deploy missing companion resources
3. **For modify policies**: Update existing resource properties
4. **Compliance requirements**: Bring all resources into compliance

### Creating Remediation Tasks

**Via Azure Portal:**
1. Go to Azure Policy → Compliance
2. Select non-compliant policy assignment
3. Click "Create remediation task"
4. Configure scope and options
5. Execute

**Via Azure CLI:**

```bash
az policy remediation create \
  --name 'remediate-tde' \
  --policy-assignment '/subscriptions/{sub-id}/providers/Microsoft.Authorization/policyAssignments/{assignment-id}' \
  --resource-group 'my-rg'
```

### Remediation Task Lifecycle

```
1. Create remediation task
   ↓
2. Policy evaluates resources
   ↓
3. Identifies non-compliant resources
   ↓
4. Applies policy effect (deploy/modify)
   ↓
5. Resources become compliant
   ↓
6. Task completes
```

### Remediation Options

| Option | Description | Use Case |
|--------|-------------|----------|
| **Scope** | Subscription, resource group, or resource | Target specific resources |
| **Locations** | Filter by Azure regions | Regional remediation |
| **Resource count** | Limit number of resources | Gradual rollout |
| **Parallel deployments** | Concurrent remediation operations | Faster completion |

## Policy Evaluation

### Evaluation Triggers

Policies are evaluated when:

1. **Resource created or updated**
2. **Policy assigned to scope**
3. **Policy definition updated**
4. **Scheduled evaluation** (every 24 hours)
5. **On-demand evaluation** (via API/CLI)

### Evaluation Flow

```
Resource operation requested
  ↓
Policy engine evaluates all applicable policies
  ↓
  ├─ Deny effect → Operation blocked
  ├─ Audit effect → Operation allowed, event logged
  ├─ Append effect → Operation modified, then allowed
  ├─ Modify effect → Operation allowed, remediation queued
  └─ DeployIfNotExists → Operation allowed, deployment queued
  ↓
Compliance state updated
```

### Compliance States

| State | Meaning |
|-------|---------|
| **Compliant** | Resource meets policy requirements |
| **Non-compliant** | Resource violates policy |
| **Conflict** | Multiple policies with conflicting effects |
| **Not started** | Policy not yet evaluated |
| **Exempt** | Resource explicitly exempted |

### On-Demand Evaluation

```bash
# Trigger policy evaluation scan
az policy state trigger-scan --resource-group my-rg

# Check compliance state
az policy state list --resource-group my-rg
```

## Best Practices

### 1. Policy Design

- ✅ Start with built-in policies before creating custom ones
- ✅ Use audit mode first, then switch to deny/enforce
- ✅ Make policies reusable with parameters
- ✅ Document policy purpose and effect clearly
- ✅ Test policies in non-production first

### 2. Policy Assignment

- ✅ Assign at highest appropriate scope (leverage inheritance)
- ✅ Use initiatives for related policies
- ✅ Leverage exclusions sparingly and document reasons
- ✅ Set enforcement mode to DoNotEnforce for testing

### 3. Remediation

- ✅ Plan remediation during maintenance windows
- ✅ Test remediation on small scope first
- ✅ Monitor remediation task progress
- ✅ Review remediation results for failures

### 4. Managed Identity

- ✅ Use system-assigned identities for policy assignments (preferred)
- ✅ Grant least privilege permissions
- ✅ Review role assignments regularly
- ✅ Document custom role assignments

### 5. Monitoring and Compliance

- ✅ Set up alerts for non-compliance
- ✅ Review compliance dashboard regularly
- ✅ Create exemptions with expiration dates
- ✅ Document compliance exceptions

### 6. Naming Conventions

```
Policy Definition: "pol-<purpose>-<scope>"
  Example: pol-require-https-storage

Policy Assignment: "assign-<policy>-<scope>"
  Example: assign-require-https-prod

Initiative: "init-<purpose>"
  Example: init-security-baseline
```

## Practice Questions

### Question 1: TDE Enforcement on Azure SQL

**Scenario:**
You need to configure an Azure policy to ensure that all Azure SQL databases have Transparent Data Encryption (TDE) enabled. The solution must meet security and compliance requirements by automatically enabling TDE on existing and new databases.

**Question:**
Which three actions should you perform in sequence?

**Actions:**

A. Create an Azure policy assignment  
B. Create a user-assigned managed identity  
C. Create an Azure policy definition that uses the Modify effect  
D. Invoke a remediation task  
E. Create an Azure policy definition that uses the deployIfNotExists effect  

**Options:**

1. **1-4-2** ❌
2. **4-3-1** ❌
3. **5-1-4** ✅
4. **3-1-5** ❌
5. **1-4-5** ❌
6. **2-3-1** ❌

**Answer:** 5-1-4 (E → A → D)

**Correct Sequence:**

**Step 1: Create an Azure policy definition that uses the deployIfNotExists effect (E)**

- TDE needs to be enabled on Azure SQL databases as a security feature
- **deployIfNotExists** is the appropriate effect because:
  - It checks if TDE is enabled on the database
  - If not enabled, it automatically deploys/enables TDE
  - This ensures both new and (with remediation) existing databases are compliant
- **Why not Modify?** The Modify effect is for updating properties or tags, not for enabling specific features like TDE that require deployment actions

**Step 2: Create an Azure policy assignment (A)**

- After defining the policy, assign it to the appropriate scope (subscription, resource group, management group)
- The assignment:
  - Activates the policy for the specified scope
  - **Automatically creates a system-assigned managed identity** (when created via Azure Portal)
  - Automatically assigns required roles based on policy's `roleDefinitionIds`
- No separate identity creation is needed

**Step 3: Invoke a remediation task (D)**

- Remediation is required for **existing** Azure SQL databases
- The policy assignment only affects new/updated resources automatically
- Remediation task:
  - Evaluates all existing databases in scope
  - Applies the deployIfNotExists effect to non-compliant databases
  - Enables TDE on databases that don't have it enabled

**Why Other Actions Are Incorrect:**

**B. Create a user-assigned managed identity** ❌
- Not required when creating policy assignment through Azure Portal
- Azure automatically creates a **system-assigned managed identity**
- Azure automatically assigns required roles from policy's `roleDefinitionIds`
- User-assigned identity would only be needed for:
  - Custom scenarios requiring shared identity across policies
  - Manual CLI/PowerShell deployments with specific identity requirements

**C. Create an Azure policy definition that uses the Modify effect** ❌
- Modify effect is for updating resource properties or tags
- TDE enablement requires deployment action, not property modification
- deployIfNotExists is specifically designed for:
  - Deploying companion resources
  - Enabling features that require deployment steps
  - Security features like TDE, diagnostic settings, monitoring agents

**Key Concepts:**

1. **Effect Selection:**
   - **Modify**: Update properties/tags → For metadata changes
   - **DeployIfNotExists**: Deploy resources/features → For TDE, extensions, diagnostics

2. **Managed Identity:**
   - System-assigned: Created automatically with assignment (preferred)
   - User-assigned: Manual creation, for advanced scenarios

3. **Remediation:**
   - Required to fix existing non-compliant resources
   - Policy assignment only affects new/updated resources by default
   - Must be explicitly invoked after assignment

**Reference Links:**
- [Policy Effects - DeployIfNotExists](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effects#deployifnotexists)
- [Policy Assignment Structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/assignment-structure)
- [Remediate Resources](https://learn.microsoft.com/en-us/azure/governance/policy/how-to/remediate-resources)

---

### Question 2: Policy Effect Selection

**Scenario:**
You need to ensure all Azure storage accounts in your organization use HTTPS-only traffic. You want to prevent anyone from creating or updating storage accounts without this setting.

**Question:**
Which policy effect should you use?

**Options:**

1. **Audit** ❌
   - Only logs violations, doesn't prevent
   - Storage accounts without HTTPS could still be created

2. **Deny** ✅
   - Blocks creation/update of non-compliant resources
   - Prevents storage accounts without HTTPS from being created
   - Enforces requirement at resource operation time

3. **DeployIfNotExists** ❌
   - Used for deploying companion resources
   - Can't "deploy" HTTPS setting on storage account
   - Wrong effect for this scenario

4. **Modify** ❌
   - Could work but requires remediation
   - Doesn't prevent initial creation
   - Better to block non-compliant resources upfront

**Answer:** Deny

**Explanation:**
The Deny effect prevents resource operations that don't meet policy conditions. Since the requirement is to enforce HTTPS-only traffic, blocking non-compliant storage accounts at creation time is the most effective approach. This ensures no storage account can exist without HTTPS enabled.

---

### Question 3: Policy Scope and Inheritance

**Scenario:**
Your organization has:
- Root management group
- 3 child management groups (Dev, Test, Prod)
- 15 subscriptions total (5 in each environment)
- Hundreds of resource groups

You need to enforce that all resources have a "CostCenter" tag across all environments.

**Question:**
At which scope should you assign the policy?

**Options:**

1. **Each subscription** ❌
   - Requires 15 policy assignments
   - Difficult to manage
   - Inconsistent enforcement risk

2. **Each management group** ❌
   - Requires 3 policy assignments
   - Better than subscriptions but not optimal
   - Extra management overhead

3. **Root management group** ✅
   - Single policy assignment
   - Automatically applies to all child management groups and subscriptions
   - Leverages policy inheritance
   - Easiest to manage
   - Ensures consistent enforcement

4. **Each resource group** ❌
   - Hundreds of assignments needed
   - Completely unmanageable
   - Prone to errors and inconsistencies

**Answer:** Root management group

**Explanation:**
Policies assigned at management group level automatically inherit to all child management groups, subscriptions, resource groups, and resources. Assigning at the root provides organization-wide enforcement with a single assignment, leveraging Azure's inheritance model for maximum efficiency.

---

### Question 4: Remediation Task Use Case

**Scenario:**
You created a new policy assignment that requires all virtual machines to have the Azure Monitor agent installed (deployIfNotExists effect). After assignment, you notice:

- New VMs created after assignment: Compliant (agent auto-installed)
- Existing VMs created before assignment: Non-compliant (no agent)

**Question:**
What should you do to make existing VMs compliant?

**Options:**

1. **Wait for automatic remediation** ❌
   - Policy assignments don't automatically remediate existing resources
   - Only affects new/updated resources

2. **Manually install agent on each VM** ❌
   - Defeats purpose of automation
   - Prone to errors
   - Doesn't scale

3. **Reassign the policy** ❌
   - Reassignment doesn't trigger remediation
   - Existing resources remain non-compliant

4. **Create a remediation task** ✅
   - Specifically designed for this scenario
   - Applies deployIfNotExists to existing resources
   - Automated and scalable
   - Tracks progress and completion

**Answer:** Create a remediation task

**Explanation:**
Remediation tasks are required to apply deployIfNotExists or modify policies to existing resources. Policy assignments only automatically affect new or updated resources. A remediation task evaluates all resources in scope and applies the policy effect to bring them into compliance.

---

### Question 5: Initiative vs Individual Policies

**Scenario:**
Your security team needs to enforce 25 different security policies across all subscriptions:
- Require HTTPS on storage accounts
- Enable TDE on SQL databases
- Require disk encryption on VMs
- Enable diagnostic logging on all resources
- (21 more policies...)

**Question:**
What is the most efficient approach to assign these policies?

**Options:**

1. **Create 25 individual policy assignments** ❌
   - Requires 25 separate assignments
   - Difficult to manage and maintain
   - Prone to configuration drift
   - Hard to track compliance holistically

2. **Create an initiative with all 25 policies and assign once** ✅
   - Single assignment for all policies
   - Centralized management
   - Unified compliance view
   - Easy to update or modify
   - Consistent parameters across policies

3. **Assign policies to each resource group separately** ❌
   - Hundreds or thousands of assignments
   - Completely unmanageable
   - Inconsistent enforcement

4. **Use Azure Security Center instead** ❌
   - Security Center provides recommendations, not enforcement
   - Doesn't prevent non-compliant resources
   - Complementary but not a replacement for policies

**Answer:** Create an initiative with all 25 policies and assign once

**Explanation:**
Initiatives (policy sets) group related policies together for simplified management. Instead of 25 individual assignments, you create one initiative assignment that includes all policies. This provides centralized management, unified compliance reporting, and consistent enforcement across your environment.

---

### Question 6: Enforcing Location-Based Deployment Restrictions

**Scenario:**
Your company plans to deploy various Azure App Service instances that will use Azure SQL databases. The App Service instances will be deployed at the same time as the Azure SQL databases.

The company has a regulatory requirement to deploy the App Service instances only to specific Azure regions. The resources for the App Service instances must reside in the same region.

You need to recommend a solution to meet the regulatory requirement.

**Proposed Solution:**
You recommend creating resource groups based on locations and implementing resource locks on the resource groups.

**Question:**
Does this meet the goal?

**Options:**

1. **Yes** ❌
2. **No** ✅

**Answer:** No

**Explanation:**

While creating resource groups based on location can help organize resources geographically, and resource locks can prevent deletion or modification of those groups, **neither ensures that new App Service instances can only be deployed to specific Azure regions**.

**Why Resource Groups + Resource Locks Don't Work:**

| Feature | What It Does | What It Doesn't Do |
|---------|--------------|-------------------|
| **Resource Groups by Location** | Organizes resources logically | Doesn't restrict where resources can be deployed |
| **Resource Locks** | Prevents deletion (CanNotDelete) or any changes (ReadOnly) | Doesn't enforce location-based deployment restrictions |

**Resource Locks Purpose:**
- **CanNotDelete**: Prevents accidental deletion of resources
- **ReadOnly**: Prevents any modifications to resources
- Neither lock type enforces geographic restrictions on new deployments

**Correct Solution: Azure Policy**

To meet regulatory requirements that restrict deployments to specific regions, use **Azure Policy** to define and enforce allowed locations:

```json
{
  "properties": {
    "displayName": "Allowed locations",
    "policyType": "BuiltIn",
    "mode": "Indexed",
    "parameters": {
      "listOfAllowedLocations": {
        "type": "Array",
        "metadata": {
          "description": "The list of allowed locations for resources.",
          "strongType": "location",
          "displayName": "Allowed locations"
        }
      }
    },
    "policyRule": {
      "if": {
        "allOf": [
          {
            "field": "location",
            "notIn": "[parameters('listOfAllowedLocations')]"
          },
          {
            "field": "location",
            "notEquals": "global"
          }
        ]
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

**Azure Policy Benefits for Location Restrictions:**

| Benefit | Description |
|---------|-------------|
| **Enforcement** | Denies deployment of resources outside allowed regions |
| **Proactive** | Prevents non-compliant deployments before they happen |
| **Built-in Policy** | "Allowed locations" is a built-in policy ready to use |
| **Scope Control** | Can be applied at management group, subscription, or resource group level |
| **Compliance Reporting** | Provides visibility into any violations |

**Implementation Steps:**

1. **Find the built-in policy**: Search for "Allowed locations" in Azure Policy
2. **Assign the policy**: Apply to appropriate scope (subscription or management group)
3. **Configure parameters**: Specify the allowed Azure regions
4. **Test**: Attempt to deploy a resource to a non-allowed region (should be denied)

**Key Difference:**

| Approach | Purpose | Enforces Location? |
|----------|---------|-------------------|
| Resource Groups + Locks | Organization and protection | ❌ No |
| Azure Policy (Allowed Locations) | Compliance and governance | ✅ Yes |

**Reference Links:**
- [Azure Policy Overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Lock Resources](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/lock-resources)
- [Built-in Policy: Allowed Locations](https://learn.microsoft.com/en-us/azure/governance/policy/samples/built-in-policies#general)

---

### Question 7: Enforcing Location via Resource Group Policy

**Scenario:**
Your company plans to deploy various Azure App Service instances that will use Azure SQL databases. The App Service instances will be deployed at the same time as the Azure SQL databases.

The company has a regulatory requirement to deploy the App Service instances only to specific Azure regions. The resources for the App Service instances must reside in the same region.

You need to recommend a solution to meet the regulatory requirement.

**Proposed Solution:**
You recommend using an Azure Policy initiative to enforce the location of resource groups.

**Question:**
Does this meet the goal?

**Options:**

1. **Yes** ❌
2. **No** ✅

**Answer:** No

**Explanation:**

Azure Policy provides a robust mechanism to enforce location constraints on Azure resources. However, **using an Azure Policy initiative to enforce the location of resource groups does not help in restricting the deployment of App Services to a specific region**. The services can still be deployed to a region that is different than that of the resource group.

**Why Enforcing Resource Group Location Doesn't Work:**

| Aspect | Resource Group Location | Resource Location |
|--------|------------------------|-------------------|
| **Purpose** | Metadata storage location | Actual deployment location |
| **Relationship** | Resources are associated with resource group | Resources can be deployed anywhere regardless of RG location |
| **Policy Impact** | Only controls where RG metadata is stored | Does not restrict resource deployment regions |

**Key Insight: Resource Location Independence**

Azure resources deployed within a resource group **do not inherit the location of the resource group**. A resource group in "East US" can contain:
- App Services deployed in "West Europe"
- SQL Databases deployed in "Southeast Asia"
- Storage Accounts deployed in "Japan East"

The resource group's location only specifies where metadata about the group is stored, not where the resources themselves must reside.

**Correct Solution: Azure Policy Targeting Specific Resource Types**

To meet regulatory requirements, use Azure Policy scoped to the **specific resource types** (not resource groups):

```json
{
  "properties": {
    "displayName": "Restrict App Service and SQL Server locations",
    "policyType": "Custom",
    "mode": "Indexed",
    "parameters": {
      "allowedLocations": {
        "type": "Array",
        "metadata": {
          "description": "The list of allowed locations for App Service and SQL resources"
        }
      }
    },
    "policyRule": {
      "if": {
        "allOf": [
          {
            "anyOf": [
              {
                "field": "type",
                "equals": "Microsoft.Web/sites"
              },
              {
                "field": "type",
                "equals": "Microsoft.Sql/servers"
              }
            ]
          },
          {
            "field": "location",
            "notIn": "[parameters('allowedLocations')]"
          }
        ]
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

**Why Resource Type-Specific Policy Works:**

| Approach | What It Controls | Enforces App Service Region? |
|----------|-----------------|------------------------------|
| Policy on Resource Group location | Only RG metadata location | ❌ No |
| Policy on `Microsoft.Web/sites` type | App Service deployment location | ✅ Yes |
| Policy on `Microsoft.Sql/servers` type | SQL Server deployment location | ✅ Yes |

**Implementation Approach:**

1. **Create or use built-in "Allowed locations" policy**
2. **Scope to specific resource types** using the `type` field:
   - `Microsoft.Web/sites` for App Services
   - `Microsoft.Sql/servers` for Azure SQL
3. **Assign at appropriate scope** (subscription or management group)
4. **Configure allowed regions** in policy parameters
5. **Use Deny effect** to block non-compliant deployments

**Built-in Policy Alternative:**

Azure provides a built-in policy called **"Allowed locations"** that can be applied with resource type filtering to achieve this goal without custom policy definitions.

**Reference Links:**
- [Restrict Resource Regions - Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/manage/azure-server-management/common-policies#restrict-resource-regions)
- [Azure Policy Overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Policy Definition Structure Basics](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-basics)

---

### Question 8: Organizing Resources for Compliance Reports by Department

**Scenario:**
You have an Azure subscription that contains 1,000 resources.

You need to generate compliance reports for the subscription.

The solution must ensure that the resources can be grouped by department.

**Question:**
What should you use to organize the resources?

**Options:**

1. **Application groups and quotas** ❌
2. **Azure Policy and tags** ✅
3. **Administrative units and Azure Lighthouse** ❌
4. **Resource groups and role assignments** ❌

**Answer:** Azure Policy and tags

**Explanation:**

**Why Azure Policy and Tags is Correct:**

Tags allow you to assign metadata to Azure resources, such as the department responsible for each resource. This enables you to logically group resources by department without changing their physical organization (e.g., resource group or region).

| Benefit | Description |
|---------|-------------|
| **Flexible Grouping** | Tag resources with department metadata (e.g., `Department: Finance`, `Department: IT`) |
| **No Physical Reorganization** | Resources can remain in their current resource groups and regions |
| **Compliance Reporting** | Tags can be used in Azure Resource Graph and Microsoft Defender for Cloud for compliance reports |
| **Scalability** | Easily scales across large numbers of resources (1,000+) |
| **Policy Enforcement** | Azure Policy can enforce tagging requirements and audit compliance |

**Using Azure Policy to Enforce Tags:**

Azure Policy can require that all resources have specific tags, such as a "Department" tag:

```json
{
  "properties": {
    "displayName": "Require Department tag on resources",
    "policyType": "Custom",
    "mode": "Indexed",
    "policyRule": {
      "if": {
        "field": "tags['Department']",
        "exists": "false"
      },
      "then": {
        "effect": "deny"
      }
    }
  }
}
```

**Compliance Reporting with Tags:**

Once resources are tagged, you can:
- Use **Azure Resource Graph** to query and report on resources by department
- Generate compliance reports in **Microsoft Defender for Cloud** filtered by tags
- Create **Cost Management** reports grouped by department tags
- Build **Azure Monitor** dashboards organized by department

**Example Azure Resource Graph Query:**

```kusto
Resources
| where tags['Department'] == 'Finance'
| summarize count() by type
```

**Why Other Options Are Incorrect:**

| Option | Reason for Incorrect |
|--------|---------------------|
| **Application groups and quotas** | This concept applies to Azure Virtual Desktop, not general Azure resource organization or compliance reporting |
| **Administrative units and Azure Lighthouse** | Administrative units apply to Microsoft Entra object management (not Azure resources), and Azure Lighthouse is used for cross-tenant management, not resource grouping by department within a tenant |
| **Resource groups and role assignments** | Resource groups are intended for lifecycle and management grouping, not for dynamic or logical grouping by metadata such as department. Compliance reporting is not typically organized by resource group unless specifically structured that way — which limits flexibility compared to tagging |

**Key Concepts:**

1. **Tags vs Resource Groups:**

| Aspect | Tags | Resource Groups |
|--------|------|-----------------|
| **Purpose** | Metadata and logical grouping | Lifecycle management |
| **Flexibility** | Any resource can have any tags | Resources belong to one RG |
| **Compliance Reporting** | Excellent for filtering and grouping | Limited to RG boundaries |
| **Scale** | Unlimited tag combinations | Physical container limitation |

2. **Azure Policy + Tags Workflow:**

```
Define Tag Policy → Assign to Scope → Enforce on New Resources → Remediate Existing → Generate Reports
```

3. **Built-in Tag Policies:**

Azure provides built-in policies for tags:
- Require a tag on resources
- Require a tag on resource groups
- Inherit a tag from the resource group
- Add a tag to resources

**Reference Links:**
- [Azure Policy Overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Tag Resources](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-resources)
- [Azure Resource Graph Overview](https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview)
- [Azure Lighthouse Overview](https://learn.microsoft.com/en-us/azure/lighthouse/overview)
- [Administrative Units](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/administrative-units)

---

### Question 9: Enabling TDE Using ARM Template in Policy

**Scenario:**
You have an Azure subscription that contains 50 Azure SQL databases.

You create an Azure Resource Manager (ARM) template named Template1 that enables Transparent Data Encryption (TDE).

You need to create an Azure Policy definition named Policy1 that will use Template1 to enable TDE for any noncompliant Azure SQL databases.

**Question:**
What should you set the available effect to?

**Options:**

1. **DeployIfNotExists** ✅
2. **EnforceRegoPolicy** ❌
3. **Modify** ❌

**Answer:** DeployIfNotExists

**Explanation:**

**Why DeployIfNotExists is Correct:**

The **DeployIfNotExists** effect allows you to use an ARM template for remediation of non-compliant resources. You can define the nested template in the policy definition and enable Transparent Data Encryption on all non-compliant SQL databases.

| Aspect | DeployIfNotExists Capability |
|--------|------------------------------|
| **ARM Template Support** | ✅ Can embed ARM templates for deployment |
| **Remediation** | ✅ Automatically deploys resources/features |
| **TDE Enablement** | ✅ Can deploy TDE configuration to databases |
| **Existing Resources** | ✅ Works with remediation tasks |

**Policy Structure with ARM Template:**

```json
{
  "then": {
    "effect": "deployIfNotExists",
    "details": {
      "type": "Microsoft.Sql/servers/databases/transparentDataEncryption",
      "existenceCondition": {
        "field": "Microsoft.Sql/transparentDataEncryption.status",
        "equals": "Enabled"
      },
      "roleDefinitionIds": [
        "/providers/Microsoft.Authorization/roleDefinitions/..."
      ],
      "deployment": {
        "properties": {
          "mode": "incremental",
          "template": {
            // Your ARM template (Template1) content here
            // to enable TDE on the database
          }
        }
      }
    }
  }
}
```

**Why Other Options Are Incorrect:**

| Option | Reason for Incorrect |
|--------|---------------------|
| **Modify** | The Modify effect is used to edit/update properties of a resource, typically metadata like tags or public access levels. **It cannot use an ARM template for remediation**, which is required in this scenario. |
| **EnforceRegoPolicy** | This is a **deprecated effect** of Azure Policy. It was used to configure the Open Policy Agent admissions controller with Gatekeeper v2 in Azure Kubernetes Service (AKS). It is not applicable for SQL database TDE configuration. |

**Key Differences: DeployIfNotExists vs Modify**

| Feature | DeployIfNotExists | Modify |
|---------|-------------------|--------|
| **ARM Template Support** | ✅ Yes | ❌ No |
| **Use Case** | Deploy companion resources, enable features | Update properties, tags |
| **TDE Enablement** | ✅ Appropriate | ❌ Not suitable |
| **Remediation Mechanism** | ARM template deployment | Direct property operations |

**When to Use DeployIfNotExists:**

- Enabling features that require deployment (TDE, diagnostics, extensions)
- Deploying companion resources
- Using ARM templates for remediation
- Complex configurations requiring multiple resource changes

**Reference Links:**
- [Policy Effects Overview](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effects)
- [DeployIfNotExists Effect](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-deploy-if-not-exists)

---

### Question 10: Policy Definition Requirements for DeployIfNotExists

**Scenario:**
(Continuation of Question 9)

You have an Azure subscription that contains 50 Azure SQL databases.

You create an Azure Resource Manager (ARM) template named Template1 that enables Transparent Data Encryption (TDE).

You need to create an Azure Policy definition named Policy1 that will use Template1 to enable TDE for any noncompliant Azure SQL databases.

**Question:**
What should you include in the policy definition?

**Options:**

1. **The identity required to perform the remediation task** ❌
2. **The scopes of the policy assignments** ❌
3. **The role-based access control (RBAC) roles required to perform the remediation task** ✅

**Answer:** The role-based access control (RBAC) roles required to perform the remediation task

**Explanation:**

**Why RBAC Roles (roleDefinitionIds) is Correct:**

When defining an Azure Policy with the **DeployIfNotExists** effect, the policy definition **must include the `roleDefinitionIds` property**. This property ensures that the required permissions are assigned to the policy's managed identity so it can remediate non-compliant resources.

Without specifying the RBAC roles, the policy will not be able to perform the deployment actions defined in the ARM template.

**Policy Definition Structure with roleDefinitionIds:**

```json
{
  "then": {
    "effect": "deployIfNotExists",
    "details": {
      "type": "Microsoft.Sql/servers/databases/transparentDataEncryption",
      "roleDefinitionIds": [
        "/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c"
      ],
      "existenceCondition": {
        "field": "Microsoft.Sql/transparentDataEncryption.status",
        "equals": "Enabled"
      },
      "deployment": {
        "properties": {
          "mode": "incremental",
          "template": {
            // ARM template content
          }
        }
      }
    }
  }
}
```

**Why Other Options Are Incorrect:**

| Option | Reason for Incorrect |
|--------|---------------------|
| **The identity required to perform the remediation task** | While a managed identity is required for remediation, **it is not included in the policy definition itself**. The identity is assigned when the policy is applied (during assignment), not when it is defined. Azure automatically creates and assigns the managed identity during policy assignment. |
| **The scopes of the policy assignments** | Policy scope is determined **at the time of assignment**, not during the policy definition. The definition only outlines the rules, effects, and remediation requirements. Scope is set when you assign the policy to a management group, subscription, or resource group. |

**Key Concept: What Goes Where**

| Component | Where It's Defined | When It's Set |
|-----------|-------------------|---------------|
| **RBAC Roles (roleDefinitionIds)** | Policy Definition | At definition creation |
| **Managed Identity** | Policy Assignment | At assignment creation (auto-created) |
| **Scope** | Policy Assignment | At assignment creation |
| **ARM Template** | Policy Definition | At definition creation |
| **Effect** | Policy Definition | At definition creation |

**Purpose of roleDefinitionIds:**

1. **Specifies required permissions** for the managed identity
2. **Azure automatically assigns** these roles to the managed identity during assignment
3. **Enables remediation** by granting necessary access to deploy resources
4. **Required for DeployIfNotExists and Modify** effects

**Common Role Definition IDs:**

| Role | GUID | Use Case |
|------|------|----------|
| **Contributor** | `b24988ac-6180-42a0-ab88-20f7382dd24c` | General resource deployment |
| **SQL Security Manager** | `056cd41c-7e88-42e1-933e-88ba6a50c9c3` | SQL-specific operations |
| **Owner** | `8e3af657-a8ff-443c-a75c-2fe8c4bcb635` | Full control (use sparingly) |

**Reference Links:**
- [Remediate Resources](https://learn.microsoft.com/en-us/azure/governance/policy/how-to/remediate-resources?tabs=azure-portal)
- [Policy Definition Structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure)
- [DeployIfNotExists Effect Basics](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-basics#deployifnotexists)

---

### Question 11: Multi-Subscription Governance Strategy

**Scenario:**
Your organization has multiple Microsoft Azure subscriptions and needs to ensure compliance with specific security policies.

You need to design a governance strategy that enforces these security policies automatically across all subscriptions.

**Question:**
Each correct answer presents part of the solution. Which two actions should you perform? (Choose 2)

**Options:**

1. **Apply security policies to each subscription individually** ❌
2. **Create a management group and apply security policies at this level** ✅
3. **Use Azure Blueprints to define and apply security policies across all subscriptions** ❌
4. **Use Azure Policy to define and assign security policies to the management group** ✅

**Answer:** Options 2 and 4

**Explanation:**

**Why Management Group + Azure Policy is Correct:**

| Correct Action | Benefit |
|----------------|---------|
| **Create a management group and apply security policies at this level** | Ensures consistent compliance across all resources under the group. Leverages Azure's hierarchical structure for efficient policy enforcement. |
| **Use Azure Policy to define and assign security policies to the management group** | Allows for automated compliance enforcement. All subscriptions automatically inherit these policies, providing a scalable governance strategy. |

**Why Other Options Are Incorrect:**

| Option | Reason for Incorrect |
|--------|---------------------|
| **Apply security policies to each subscription individually** | Inefficient and error-prone. Involves manual application and does not offer a scalable solution. |
| **Use Azure Blueprints to define and apply security policies across all subscriptions** | While Azure Blueprints is a more automated approach, it may not fully utilize the hierarchical benefits of management groups. Blueprints are better suited for environment standardization (templates, role assignments) rather than ongoing policy enforcement. |

**Key Concepts:**

1. **Management Group Benefits:**
   - Organize subscriptions into a hierarchy
   - Apply governance conditions at scale
   - Policies, RBAC, and compliance inherit down to child scopes
   - Efficient management across multiple subscriptions

2. **Azure Policy at Management Group Level:**
   - Single assignment affects all child subscriptions
   - Automated compliance evaluation
   - Consistent enforcement across the organization
   - Simplified compliance reporting

3. **Azure Blueprints vs Azure Policy:**

| Feature | Azure Blueprints | Azure Policy |
|---------|------------------|--------------|
| **Purpose** | Environment templates and standardization | Ongoing compliance enforcement |
| **Scope** | Deploy resources, roles, and policies together | Define and enforce resource rules |
| **Use Case** | Initial environment setup | Continuous governance |
| **Hierarchical Benefits** | Limited | Full inheritance support |

**Architecture: Management Group with Azure Policy**

```
┌─────────────────────────────────────────────────┐
│            Root Management Group                 │
│       (Azure Policy assigned here)               │
│                                                  │
│  Policies:                                       │
│  • Require HTTPS on storage                      │
│  • Allowed locations: East US, West US           │
│  • Require tags on resources                     │
└─────────────────────────────────────────────────┘
                    ↓ (inherited)
    ┌───────────────┴───────────────┐
    ↓                               ↓
┌─────────────┐           ┌─────────────┐
│ Production  │           │ Development │
│ Mgmt Group  │           │ Mgmt Group  │
└─────────────┘           └─────────────┘
    ↓                           ↓
┌─────────────┐           ┌─────────────┐
│ Sub-001     │           │ Sub-003     │
│ Sub-002     │           │ Sub-004     │
└─────────────┘           └─────────────┘
```

**Implementation Steps:**

1. **Create Management Group Hierarchy**
   - Design hierarchy based on organizational structure
   - Group subscriptions logically (by environment, department, etc.)

2. **Define Azure Policies**
   - Create custom policies or use built-in definitions
   - Group related policies into initiatives

3. **Assign Policies at Management Group Level**
   - Single assignment propagates to all child scopes
   - Configure parameters and exclusions as needed

4. **Monitor Compliance**
   - Use Azure Policy compliance dashboard
   - Set up alerts for non-compliance
   - Run remediation tasks for existing resources

**Reference Links:**
- [Describe Azure management infrastructure - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/describe-azure-management-infrastructure/)
- [Design for management groups - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/enterprise-scale-organization/)
- [Organize your Azure resources effectively - Cloud Adoption Framework | Microsoft Learn](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-setup-guide/organize-resources)

---

### Question 12: Valid Modes for Azure Policy Definitions

**Question:**
Which of the following is NOT a valid mode for an Azure Policy definition?

**Options:**

1. **Indexed** ❌
2. **All** ❌
3. **DoNotAllow** ✅

**Answer:** DoNotAllow

**Explanation:**

**Why DoNotAllow is NOT a Valid Mode:**

`DoNotAllow` is **not a valid mode** for an Azure Policy definition. This mode is not recognized in Azure Policy and is not used for defining policy enforcement actions. It is often confused with the `Deny` **effect**, but mode and effect are completely different properties in a policy definition.

**Valid Azure Policy Modes:**

| Mode | Description | When to Use |
|------|-------------|-------------|
| **All** | Evaluates all resource types and locations within the scope, including resource groups and subscriptions | When you need to apply policies to resource groups or all resource types |
| **Indexed** | Evaluates only resource types that support tags and location properties | When creating tag or location-based policies (recommended for these scenarios) |

**Mode vs Effect - Important Distinction:**

| Property | Purpose | Valid Values |
|----------|---------|--------------|
| **Mode** | Determines which resource types are evaluated | `All`, `Indexed` |
| **Effect** | Determines action when policy conditions are met | `Deny`, `Audit`, `Append`, `Modify`, `DeployIfNotExists`, `AuditIfNotExists`, `Disabled` |

> ⚠️ **Common Confusion**: `DoNotAllow` might be confused with the `Deny` effect. Remember:
> - **Mode** = What resources to evaluate
> - **Effect** = What action to take

**Why Other Options Are Correct (Valid Modes):**

| Option | Explanation |
|--------|-------------|
| **Indexed** | Valid mode that allows policies to be evaluated against specific resource types that support tags and locations within the scope of the policy assignment |
| **All** | Valid mode that enables policies to be evaluated against all resource types and locations within the scope of the policy assignment, including resource groups and subscriptions |

**Example Policy Definition with Mode:**

```json
{
  "properties": {
    "displayName": "Require tag on resources",
    "description": "Enforces a required tag",
    "mode": "Indexed",  // Valid mode
    "policyRule": {
      "if": {
        "field": "tags['Environment']",
        "exists": "false"
      },
      "then": {
        "effect": "deny"  // This is an EFFECT, not a mode
      }
    }
  }
}
```

**Key Takeaway:**
- **Mode** is about **scope of evaluation** (which resources)
- **Effect** is about **action** (what happens when conditions are met)
- `DoNotAllow` is not a valid value for either property

**Reference Links:**
- [Azure Policy definition structure - mode](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure#mode)
- [Understanding Azure Policy effects](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effects)

**Domain:** Design Azure governance solutions

---

## Summary

### Key Takeaways

1. **Policy Effects:**
   - **Deny**: Block non-compliant resources
   - **Audit**: Log non-compliance without blocking
   - **DeployIfNotExists**: Deploy resources/features automatically
   - **Modify**: Update properties/tags
   - Choose based on enforcement needs

2. **Managed Identity:**
   - System-assigned (automatic) for most scenarios
   - Required for deployIfNotExists and modify effects
   - Azure assigns roles automatically from policy definition

3. **Remediation:**
   - Required for existing resources
   - Policy assignments only affect new/updated resources by default
   - Invoke after creating assignment with deployIfNotExists/modify

4. **Assignment Scope:**
   - Assign at highest appropriate level
   - Leverage inheritance from management groups
   - Use initiatives for related policies

5. **Workflow:**
   ```
   Define Policy → Assign to Scope → Remediate Existing Resources → Monitor Compliance
   ```

### Decision Matrix

| Need | Use This | Notes |
|------|----------|-------|
| Block non-compliant resources | Deny effect | Prevents creation |
| Enable features on resources | DeployIfNotExists | TDE, diagnostics, agents |
| Update tags/properties | Modify effect | Requires remediation |
| Track violations only | Audit effect | No blocking |
| Apply to org-wide | Root management group | Single assignment |
| Group related policies | Initiative | Simplified management |
| Fix existing resources | Remediation task | After assignment |

---

**Last Updated:** December 2025
