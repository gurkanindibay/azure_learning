# ARM Templates: Declarative Syntax

## Table of Contents

- [Overview](#overview)
- [Why Declarative Syntax is Better Than Programmatic Approach](#why-declarative-syntax-is-better-than-programmatic-approach)
  - [1. Idempotent Deployments - No Need to Check Resource Existence](#1-idempotent-deployments-no-need-to-check-resource-existence)
  - [2. Consistent and Repeatable Deployments](#2-consistent-and-repeatable-deployments)
  - [3. Full Infrastructure as Code (IaC)](#3-full-infrastructure-as-code-iac)
  - [4. Built-in Dependency Management](#4-built-in-dependency-management)
- [Common Misconceptions](#common-misconceptions)
  - [❌ Incorrect: "Declarative syntax only requires minor changes before each deployment"](#incorrect-declarative-syntax-only-requires-minor-changes-before-each-deployment)
  - [❌ Incorrect: "Declarative syntax compiles into binary form"](#incorrect-declarative-syntax-compiles-into-binary-form)
  - [✅ Note: Both approaches support advanced features](#note-both-approaches-support-advanced-features)
- [Example: Declarative vs Programmatic](#example-declarative-vs-programmatic)
  - [Declarative (ARM Template)](#declarative-arm-template)
  - [Programmatic (Pseudo-code)](#programmatic-pseudo-code)
- [Nested and Linked ARM Templates](#nested-and-linked-arm-templates)
  - [Overview](#overview)
  - [Resource Type for Nested Templates](#resource-type-for-nested-templates)
  - [Key Properties](#key-properties)
  - [Common Misconceptions](#common-misconceptions)
  - [References](#references)
- [ARM Template Features for Resource Dependencies](#arm-template-features-for-resource-dependencies)
  - [dependsOn](#dependson)
  - [reference()](#reference)
  - [conditions](#conditions)
  - [copy](#copy)
  - [Feature Comparison](#feature-comparison)
  - [Best Practice](#best-practice)
- [ARM Templates vs Azure Blueprints](#arm-templates-vs-azure-blueprints)
  - [Key Difference: Connection to Deployed Resources](#key-difference-connection-to-deployed-resources)
  - [Why Blueprints Remain Connected](#why-blueprints-remain-connected)
  - [Policy Definitions](#policy-definitions)
  - [What Blueprints Can Include](#what-blueprints-can-include)
  - [When to Use Each](#when-to-use-each)
- [Securing Sensitive Data in ARM Templates](#securing-sensitive-data-in-arm-templates)
  - [Question: Storing Administrative Passwords Securely](#question-storing-administrative-passwords-securely)
  - [Solution Components](#solution-components)
  - [Why Other Options Are Incorrect](#why-other-options-are-incorrect)
  - [Implementation Example](#implementation-example)
  - [Key Takeaway](#key-takeaway)
- [Related Technologies](#related-technologies)
- [References](#references)

## Overview

ARM (Azure Resource Manager) templates use a **declarative syntax** to define and deploy Azure infrastructure. This approach allows you to describe *what* you want to deploy rather than *how* to deploy it.

## Why Declarative Syntax is Better Than Programmatic Approach

### 1. Idempotent Deployments - No Need to Check Resource Existence

**Key Benefit:** You don't have to check if the resource exists; you simply declare that it should exist.

With declarative syntax:
- You define the desired end state of your infrastructure
- Azure Resource Manager handles the logic of whether to create, update, or skip resources
- Re-running the same template produces the same result without side effects

```json
{
  "type": "Microsoft.Storage/storageAccounts",
  "apiVersion": "2021-02-01",
  "name": "mystorageaccount",
  "location": "eastus",
  "sku": {
    "name": "Standard_LRS"
  },
  "kind": "StorageV2"
}
```

With a programmatic approach, you would need to:
1. Check if the resource exists
2. If it exists, determine if it needs updates
3. If it doesn't exist, create it
4. Handle errors and rollbacks manually

### 2. Consistent and Repeatable Deployments

- Templates ensure the same infrastructure is deployed every time
- Eliminates configuration drift between environments
- Easy to replicate environments (dev, test, production)

### 3. Full Infrastructure as Code (IaC)

ARM templates allow you to deploy an entire Azure infrastructure declaratively, including:
- Virtual machines
- Network infrastructure (VNets, subnets, NSGs)
- Storage systems
- Databases
- Any other Azure resources

### 4. Built-in Dependency Management

Azure Resource Manager automatically:
- Determines the correct order to deploy resources
- Parallelizes deployments where possible
- Handles dependencies between resources

## Common Misconceptions

### ❌ Incorrect: "Declarative syntax only requires minor changes before each deployment"
- Declarative templates are designed to be **reusable without modification**
- Parameters and variables handle environment-specific values

### ❌ Incorrect: "Declarative syntax compiles into binary form"
- ARM templates are JSON files processed directly by Azure Resource Manager
- No compilation step is involved

### ✅ Note: Both approaches support advanced features
- ARM templates **do support** loops, variables, parameters, and functions
- The programmatic approach also supports these features
- This is not a differentiator between the two approaches

## Example: Declarative vs Programmatic

### Declarative (ARM Template)
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-02-01",
      "name": "mystorageaccount",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ]
}
```

### Programmatic (Pseudo-code)
```python
# Check if storage account exists
storage_account = get_storage_account("mystorageaccount")

if storage_account is None:
    # Create new storage account
    create_storage_account(
        name="mystorageaccount",
        location="eastus",
        sku="Standard_LRS"
    )
elif storage_account.sku != "Standard_LRS":
    # Update existing storage account
    update_storage_account(
        name="mystorageaccount",
        sku="Standard_LRS"
    )
else:
    # No action needed
    print("Storage account already exists with correct configuration")
```

## Nested and Linked ARM Templates

### Overview

To deploy complex solutions, you can break your ARM template into many related templates, and then deploy them together through a main template. The related templates can be separate files or template syntax that is embedded within the main template.

### Resource Type for Nested Templates

To include another ARM template within your deployment, use the **`Microsoft.Resources/deployments`** resource type.

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Resources/deployments",
      "apiVersion": "2021-04-01",
      "name": "linkedTemplate",
      "properties": {
        "mode": "Incremental",
        "templateLink": {
          "uri": "https://mystorageaccount.blob.core.windows.net/templates/nested-template.json",
          "contentVersion": "1.0.0.0"
        },
        "parameters": {
          "storageAccountName": {
            "value": "[parameters('storageAccountName')]"
          }
        }
      }
    }
  ]
}
```

### Key Properties

| Property | Description |
|----------|-------------|
| `templateLink.uri` | URI of the external template to include |
| `template` | Inline template definition (for embedded templates) |
| `parameters` | Parameters to pass to the nested template |
| `mode` | Deployment mode (Incremental or Complete) |

### Common Misconceptions

| Resource Type | Actual Purpose |
|---------------|----------------|
| ❌ `Microsoft.Compute/virtualMachines/extensions` | VM extensions, not template linking |
| ❌ `Microsoft.Resources/deploymentScripts` | Running scripts during deployment |
| ❌ `"dependsOn": [ ... ]` | Dependency declaration, not a resource type |
| ✅ `Microsoft.Resources/deployments` | **Correct** - Links/nests ARM templates |

### References

- [Microsoft Docs: Linked and Nested Templates](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/linked-templates?tabs=azure-powershell)

## ARM Template Features for Resource Dependencies

When deploying resources that depend on each other (e.g., subnets that require a VNet to exist first), ARM templates provide several features. Understanding when to use each is critical.

### dependsOn

**Purpose:** Explicitly specify dependencies between resources to control deployment order.

The `dependsOn` property ensures that a resource is created only after its dependencies are successfully deployed.

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Network/virtualNetworks",
      "apiVersion": "2021-02-01",
      "name": "myVNet",
      "location": "[resourceGroup().location]",
      "properties": {
        "addressSpace": {
          "addressPrefixes": ["10.0.0.0/16"]
        }
      }
    },
    {
      "type": "Microsoft.Network/virtualNetworks/subnets",
      "apiVersion": "2021-02-01",
      "name": "myVNet/mySubnet",
      "dependsOn": [
        "[resourceId('Microsoft.Network/virtualNetworks', 'myVNet')]"
      ],
      "properties": {
        "addressPrefix": "10.0.1.0/24"
      }
    }
  ]
}
```

**Use Case:** Ensuring subnets are created only after the VNet is successfully deployed.

### reference()

**Purpose:** Retrieve runtime properties of another resource in the template.

The `reference()` function gets information about an existing or deployed resource, such as its properties or outputs. However, it **does not enforce deployment order**.

```json
{
  "outputs": {
    "vnetAddressSpace": {
      "type": "array",
      "value": "[reference(resourceId('Microsoft.Network/virtualNetworks', 'myVNet')).addressSpace.addressPrefixes]"
    }
  }
}
```

**Note:** While `reference()` can access properties of resources, it is not designed to specify dependencies between resources.

### conditions

**Purpose:** Conditionally deploy resources based on parameter values or expressions.

The `condition` property determines whether a resource should be deployed at all, based on a boolean expression.

```json
{
  "type": "Microsoft.Storage/storageAccounts",
  "apiVersion": "2021-02-01",
  "name": "mystorageaccount",
  "condition": "[equals(parameters('deployStorage'), 'yes')]",
  "location": "[resourceGroup().location]",
  "sku": {
    "name": "Standard_LRS"
  },
  "kind": "StorageV2"
}
```

**Note:** Conditions control *whether* a resource is deployed, not *when* it is deployed relative to other resources.

### copy

**Purpose:** Create multiple instances of a resource using iteration.

The `copy` element allows you to deploy multiple copies of a resource with different property values.

```json
{
  "type": "Microsoft.Storage/storageAccounts",
  "apiVersion": "2021-02-01",
  "name": "[concat('storage', copyIndex())]",
  "location": "[resourceGroup().location]",
  "copy": {
    "name": "storageCopy",
    "count": 3
  },
  "sku": {
    "name": "Standard_LRS"
  },
  "kind": "StorageV2"
}
```

**Note:** The `copy` feature is for creating multiple resource instances, not for specifying dependencies.

### Feature Comparison

| Feature | Purpose | Controls Deployment Order? |
|---------|---------|---------------------------|
| **dependsOn** | Specify resource dependencies | ✅ Yes |
| **reference()** | Retrieve properties of another resource | ❌ No |
| **condition** | Conditionally deploy resources | ❌ No |
| **copy** | Create multiple resource instances | ❌ No |

### Best Practice

When you need to ensure that one resource is created only after another resource is successfully deployed (e.g., subnets after VNet), use **`dependsOn`**. This is the correct and explicit way to define resource deployment order in ARM templates.

## Practice Questions

### Question 1: Reviewing ARM Templates Used for Deployment

**Scenario:**
Your company has an Azure subscription that includes a storage account, a resource group, a blob container, and a file share. A colleague named Jon Ross makes use of a solitary Azure Resource Manager (ARM) template to deploy a virtual machine and an additional Azure Storage account. You want to review the ARM template that was used by Jon Ross.

**Solution:** You access the Resource Group blade.

**Does the solution meet the goal?**

**Answer: Yes** ✅

**Explanation:**

Accessing the Resource Group blade can meet the goal of reviewing the ARM template used by Jon Ross to deploy the virtual machine and additional Azure Storage account. In the Resource Group blade, you can select the resource group where the virtual machine and additional storage account were deployed, and then click on the "Deployments" tab. This will display a list of all deployments made to the resource group, including the ARM template used for the deployment. Therefore, the solution of accessing the Resource Group blade meets the goal of reviewing the ARM template used by Jon Ross.

**Detailed Steps:**

By navigating to the Resource Group blade, you can:

1. **View Deployment History**: The Resource Group blade contains a "Deployments" section that shows all ARM template deployments that have been executed
2. **Access Deployment Details**: Click on any deployment to view:
   - The complete ARM template that was used
   - Input parameters that were provided
   - Deployment outputs
   - Deployment status and logs
3. **Identify the Template**: Review the template content to understand what resources were deployed and how they were configured

**How to Access Deployment History:**

1. Navigate to Azure Portal
2. Go to **Resource Groups**
3. Select the resource group containing the deployed resources
4. In the left menu, click **Deployments** (under Settings)
5. Select the specific deployment to view the ARM template details

**Why This Works:**

Accessing the Resource Group blade is the correct way to review the ARM template used by Jon Ross. By accessing the Resource Group blade, you can see all the resources deployed within that resource group, including the virtual machine and additional Azure Storage account deployed using the ARM template. The Deployments section provides a complete audit trail of all template deployments, making it easy to identify and review the specific template used for any deployment.

**Key Takeaway:**
The Resource Group blade's Deployments section is the primary location in Azure Portal for reviewing historical ARM template deployments, accessing template content, and understanding what resources were created by each deployment.

---

### Question 2: Azure Blueprints Persistent Link

**Scenario:**
Your organization plans to utilize Azure Blueprints to make sure that sets of Azure resources meet company standards, patterns, and requirements. The blueprints in development consist of:
- Role Assignments
- Policy Assignments
- ARM Templates
- Resource Groups

You need to determine the features and capabilities of Azure Blueprints.

**Statement:** Does deploying a resource using a blueprint create a persistent link between the blueprint and the resource?

**Answer: Yes** ✅

**Explanation:**

When you use a blueprint to deploy a resource, it keeps a **persistent link** between the blueprint and the resource. This is different from just using an ARM template alone.

**Key Points:**
- **ARM Templates**: Once deployment completes, the template is disconnected from the deployed resources
- **Azure Blueprints**: Maintains an ongoing connection to deployed resources

**Benefits of the Persistent Link:**
1. **Better Tracking**: You can track which resources were deployed by which blueprint
2. **Compliance Auditing**: Easily verify that resources remain aligned with the blueprint definition
3. **Version Control**: Track which version of the blueprint was used for deployment
4. **Update Propagation**: Updates to the blueprint can be propagated to assigned subscriptions

**Understanding the Persistent Connection:**

The persistent connection (also called "blueprint assignment relationship") is a core differentiator:

| Aspect | ARM Template | Azure Blueprint |
|--------|--------------|-----------------|
| **After Deployment** | Template becomes "orphaned" - no link exists | Blueprint assignment record is maintained |
| **Tracking Origin** | Must manually track which template deployed what | Azure automatically knows which blueprint deployed which resources |
| **Compliance Drift** | No way to detect if resources changed from original state | Can detect and report when resources drift from blueprint definition |
| **Updates** | Must redeploy entire template manually | Can update blueprint and reassign to propagate changes |
| **Audit Trail** | Limited to deployment logs | Full lifecycle tracking with version history |

**How the Persistent Connection Works:**

1. **Blueprint Definition**: You create a blueprint with artifacts (ARM templates, policies, role assignments)
2. **Blueprint Assignment**: When you assign the blueprint to a subscription/management group, Azure creates an **assignment object**
3. **Resource Deployment**: Resources are deployed with metadata linking them to the blueprint assignment
4. **Ongoing Relationship**: The assignment object maintains references to:
   - The blueprint version used
   - All resources deployed
   - Parameter values used during assignment
   - Lock state of resources (if resource locking is enabled)

**Resource Locking with Blueprints:**

Blueprints can apply **resource locks** that even subscription owners cannot remove:
- **Don't Lock**: No locks applied
- **Do Not Delete**: Prevents deletion of blueprint-deployed resources
- **Read Only**: Prevents any modifications to blueprint-deployed resources

This is unique to Blueprints - the lock is enforced by the blueprint assignment, not by standard Azure RBAC.

This persistent connection is one of the fundamental differences between Azure Blueprints and ARM Templates, making Blueprints more suitable for ongoing governance and compliance scenarios.

---

## ARM Templates vs Azure Blueprints

### Key Difference: Connection to Deployed Resources

| Aspect | ARM Templates | Azure Blueprints |
|--------|---------------|------------------|
| **Connection After Deployment** | No connection - once deployment completes, template is disconnected | Remains connected to deployed resources |
| **Ongoing Updates** | Changes to template don't affect deployed resources | Allows ongoing updates and compliance tracking |
| **Primary Purpose** | Deploy infrastructure as code | Define and assign configurations, policies, and role assignments across subscriptions |
| **Scope** | Single deployment | Multi-subscription governance |

### Why Blueprints Remain Connected

Azure Blueprints maintain a connection to deployed resources because:
- They provide **ongoing compliance tracking**
- Resources remain in alignment with the defined blueprint
- Updates to the blueprint can propagate to assigned subscriptions
- Version control and audit trail of what was deployed

### Policy Definitions

**Both** ARM Templates and Azure Blueprints can contain policy definitions:
- ARM templates can include Azure Policy assignments
- Blueprints can reference existing policy definitions to enforce governance

### What Blueprints Can Include

- **Policy Assignments** - Enforce governance rules
- **Role Assignments** - Define access control
- **Resource Groups** - Organize resources
- **ARM Templates** - Deploy infrastructure (artifacts)

### When to Use Each

```
Need one-time infrastructure deployment?
        |
       Yes → Use ARM Templates
        
Need ongoing governance across subscriptions?
        |
       Yes → Use Azure Blueprints

Need to enforce compliance after deployment?
        |
       Yes → Use Azure Blueprints

Need version-controlled, repeatable governance?
        |
       Yes → Use Azure Blueprints
```

### References

- [Azure Blueprints Overview](https://learn.microsoft.com/en-us/azure/governance/blueprints/overview)
- [How Blueprints are Different from Azure Policy](https://learn.microsoft.com/en-us/azure/governance/blueprints/overview#how-its-different-from-azure-policy)
- [Azure Policy Overview](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [ARM Templates Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)

---

## Securing Sensitive Data in ARM Templates

### Question: Storing Administrative Passwords Securely

**Scenario:**
You have downloaded an Azure Resource Manager (ARM) template to deploy numerous virtual machines (VMs). The ARM template is based on a current VM, but must be adapted to reference an administrative password. You need to make sure that the password cannot be stored in plain text.

**Question:** Which TWO components should you create to achieve this goal?

**Correct Answers:**
1. ✅ **An Azure Key Vault**
2. ✅ **An Access Policy**

### Solution Components

#### 1. Azure Key Vault

Azure Key Vault provides secure storage and management of sensitive information such as passwords, cryptographic keys, and certificates.

**Benefits:**
- Passwords are **never stored in plain text**
- Provides **encryption at rest** and **in transit**
- Centralized management of secrets
- Integration with ARM templates through parameter references
- Audit logging of secret access

**Usage in ARM Templates:**
```json
"parameters": {
  "adminPassword": {
    "type": "securestring",
    "metadata": {
      "description": "Admin password from Key Vault"
    }
  }
}
```

#### 2. Access Policy

An Access Policy controls who can access secrets stored in the Key Vault.

**Purpose:**
- Specify **which users, applications, and services** can access Key Vault secrets
- Define **permission levels** (Get, List, Set, Delete secrets)
- Ensure the administrative password is **only accessible to authorized entities**
- Control **data plane operations** on Key Vault objects

**Key Permissions:**
- **Get**: Retrieve secret values
- **List**: List secrets in the vault
- **Set**: Create or update secrets
- **Delete**: Remove secrets

### Why Other Options Are Incorrect

| Option | Why It's Incorrect |
|--------|-------------------|
| **Entra ID Identity Protection** | Identity Protection is designed for detecting and responding to identity-based risks (suspicious sign-ins, leaked credentials). It does not provide secure storage for passwords in ARM templates. |
| **Azure Storage Account** | Storage Accounts are for data storage (blobs, files, queues, tables) but are **not designed for secure secret management**. Passwords stored in Storage Accounts would not have the same security controls as Key Vault. |
| **Azure Policy** | Azure Policies enforce compliance rules and governance across Azure resources. They **cannot securely store or manage sensitive data** like passwords. |
| **Backup Policy** | Backup Policies define backup schedules and retention for Azure resources. They are **unrelated to secret management** and do not provide secure password storage. |

### Implementation Example

#### Step 1: Create Key Vault and Store Secret

```bash
# Create Key Vault
az keyvault create \
  --name myKeyVault \
  --resource-group myResourceGroup \
  --location eastus

# Store admin password as secret
az keyvault secret set \
  --vault-name myKeyVault \
  --name vmAdminPassword \
  --value 'SecurePassword123!'
```

#### Step 2: Create Access Policy

```bash
# Grant access to a service principal
az keyvault set-policy \
  --name myKeyVault \
  --spn <service-principal-id> \
  --secret-permissions get list

# Enable for template deployment
az keyvault update \
  --name myKeyVault \
  --resource-group myResourceGroup \
  --enabled-for-template-deployment true
```

#### Step 3: Reference in ARM Template Parameters

**parameters.json:**
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "adminPassword": {
      "reference": {
        "keyVault": {
          "id": "/subscriptions/{subscription-id}/resourceGroups/{rg-name}/providers/Microsoft.KeyVault/vaults/{vault-name}"
        },
        "secretName": "vmAdminPassword"
      }
    }
  }
}
```

**template.json:**
```json
{
  "type": "Microsoft.Compute/virtualMachines",
  "apiVersion": "2023-03-01",
  "name": "myVM",
  "properties": {
    "osProfile": {
      "computerName": "myVM",
      "adminUsername": "azureuser",
      "adminPassword": "[parameters('adminPassword')]"
    }
  }
}
```

### Key Takeaway

To securely store administrative passwords in ARM templates:

1. **Create an Azure Key Vault** to securely store the password as a secret
2. **Create an Access Policy** to control who can retrieve the secret
3. **Enable the Key Vault for template deployment** (`enabled-for-template-deployment`)
4. **Reference the secret** in your ARM template parameters using Key Vault reference syntax
5. **Never store passwords in plain text** in template files or parameter files

This approach ensures:
- ✅ Passwords are encrypted and secured
- ✅ Access is controlled and auditable
- ✅ Secrets can be rotated without changing templates
- ✅ Compliance with security best practices

---

## Related Technologies

| Technology | Type | Description |
|------------|------|-------------|
| ARM Templates | Declarative | Native Azure JSON templates |
| Bicep | Declarative | Domain-specific language that compiles to ARM |
| Terraform | Declarative | Multi-cloud IaC tool |
| Azure CLI/PowerShell | Imperative/Programmatic | Scripting tools for Azure |
| Azure SDKs | Imperative/Programmatic | Language-specific libraries |

## References

- [Microsoft Docs: ARM Templates Overview](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)
- [Microsoft Docs: Template deployment modes](https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deployment-modes)
