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

### Question 1: Identifying ARM Template Used for Resource Deployment

**Scenario:**
Your company has an Azure subscription that includes a storage account, a resource group, a blob container, and a file share. A fellow administrator named Jon Ross used an Azure Resource Manager template to deploy a virtual machine and an Azure Storage account. You need to identify the Azure Resource Manager template that Jon Ross used.

**Solution:** You access the Resource Group blade.

**Does the solution meet the goal?**

**Answer: Yes** ✅

**Explanation:**

Yes, accessing the Resource Group blade allows you to view all the resources deployed within that specific resource group. By navigating to the Resource Group blade, you can:

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

This is the correct and most straightforward approach to identify the Azure Resource Manager template that was used by Jon Ross for the deployment.

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
