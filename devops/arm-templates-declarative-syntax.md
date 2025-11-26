# ARM Templates: Declarative Syntax

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
