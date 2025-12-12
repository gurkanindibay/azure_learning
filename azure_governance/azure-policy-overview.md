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

### 2. Policy Assignment

A **policy assignment** applies a policy definition to a specific scope:

- Management group
- Subscription  
- Resource group
- Individual resource

### 3. Initiative Definition (Policy Set)

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
