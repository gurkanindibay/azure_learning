# Azure Virtual Machines - Deployment and Management

## Table of Contents

- [Overview](#overview)
- [VM Creation Methods](#vm-creation-methods)
  - [Azure CLI](#azure-cli)
  - [Azure PowerShell](#azure-powershell)
  - [Azure Portal](#azure-portal)
  - [ARM Templates](#arm-templates)
- [Custom VM Deployments](#custom-vm-deployments)
  - [Cloud-Init for Linux VMs](#cloud-init-for-linux-vms)
  - [Custom Script Extension](#custom-script-extension)
  - [Installing Trusted Root CA Certificates](#installing-trusted-root-ca-certificates)
- [VM Migration and Movement](#vm-migration-and-movement)
  - [Moving VMs Between Virtual Networks](#moving-vms-between-virtual-networks)
  - [VM Redeployment and Host Migration](#vm-redeployment-and-host-migration)
- [Tool Comparison](#tool-comparison)
- [Best Practices](#best-practices)
- [Virtual Machine Scale Set (VMSS) Provisioning](#virtual-machine-scale-set-vmss-provisioning)
  - [Installing Components During VMSS Provisioning](#installing-components-during-vmss-provisioning)
  - [Methods That Do NOT Work for VMSS Provisioning](#methods-that-do-not-work-for-vmss-provisioning)
  - [Alternative Approaches](#alternative-approaches)
- [Practice Questions](#practice-questions)
- [References](#references)

---

## Overview

Azure Virtual Machines can be deployed and managed using various tools and methods. Each approach offers different capabilities for customization, automation, and integration with existing workflows. Understanding the right tool for your deployment scenario is crucial for efficient VM management.

---

## VM Creation Methods

### Azure CLI

**Azure CLI** is a cross-platform command-line tool for managing Azure resources. It provides comprehensive support for custom deployments including configuration scripts, extensions, and cloud-init.

#### Primary Command: `az vm create`

```bash
# Basic VM creation
az vm create \
  --resource-group myResourceGroup \
  --name myVM \
  --image Ubuntu2204 \
  --admin-username azureuser \
  --generate-ssh-keys

# VM with custom cloud-init script
az vm create \
  --resource-group myResourceGroup \
  --name myVM \
  --image Ubuntu2204 \
  --custom-data cloud-init.txt \
  --admin-username azureuser

# VM with specific size and data disks
az vm create \
  --resource-group myResourceGroup \
  --name myVM \
  --image Ubuntu2204 \
  --size Standard_DS2_v2 \
  --data-disk-sizes-gb 128 256 \
  --admin-username azureuser
```

#### Key Features

| Feature | Support | Description |
|---------|---------|-------------|
| **Custom-Data / Cloud-Init** | ✅ Yes | Execute initialization scripts on first boot |
| **Custom Script Extension** | ✅ Yes | Add extensions for post-deployment configuration |
| **Cross-Platform** | ✅ Yes | Works on Windows, macOS, Linux |
| **Scriptable** | ✅ Yes | Perfect for automation and CI/CD pipelines |
| **JSON Output** | ✅ Yes | Easy to parse for further automation |
| **Trusted Root CA Installation** | ✅ Yes | Via cloud-init or custom script extension |

#### When to Use Azure CLI

✅ **Custom deployments** requiring initialization scripts  
✅ **Automation** and CI/CD pipelines  
✅ **Cross-platform** environments  
✅ **Infrastructure as Code** with shell scripting  
✅ **Adding custom configurations** like trusted root CAs  

---

### Azure PowerShell

**Azure PowerShell** provides cmdlets for managing Azure resources using PowerShell. There are two main modules: the deprecated **AzureRM** and the current **Az** module.

#### Module Evolution

```
┌──────────────────────────────────────────────────────────────┐
│           Azure PowerShell Module Timeline                    │
│                                                               │
│   AzureRM Module (DEPRECATED)                                 │
│   ├─ New-AzureRmVm  ❌ Legacy                                │
│   ├─ Deprecated since December 2018                          │
│   └─ No longer maintained                                    │
│                                                               │
│   Az Module (CURRENT)                                         │
│   ├─ New-AzVM  ✅ Recommended                                │
│   ├─ Active development                                      │
│   ├─ Cross-platform PowerShell Core support                 │
│   └─ All new features                                        │
│                                                               │
│   ⚠️  Create-AzVM does NOT exist (Invalid)                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

#### Valid Cmdlet: `New-AzVM`

```powershell
# Basic VM creation with Az module
New-AzVM `
  -ResourceGroupName "myResourceGroup" `
  -Name "myVM" `
  -Image "Ubuntu2204" `
  -Location "eastus" `
  -Size "Standard_DS2_v2" `
  -Credential (Get-Credential)

# VM with custom configuration
$vmConfig = New-AzVMConfig -VMName "myVM" -VMSize "Standard_DS2_v2"
$vmConfig = Set-AzVMOperatingSystem -VM $vmConfig -Linux `
  -ComputerName "myVM" -Credential (Get-Credential)
$vmConfig = Set-AzVMSourceImage -VM $vmConfig `
  -PublisherName "Canonical" `
  -Offer "0001-com-ubuntu-server-jammy" `
  -Skus "22_04-lts-gen2" `
  -Version "latest"
New-AzVM -ResourceGroupName "myResourceGroup" -Location "eastus" -VM $vmConfig
```

#### PowerShell Module Comparison

| Cmdlet | Module | Status | Recommendation |
|--------|--------|--------|----------------|
| **New-AzureRmVM** | AzureRM | ❌ Deprecated | Do not use for new deployments |
| **New-AzVM** | Az | ✅ Current | Use for PowerShell automation |
| **Create-AzVM** | N/A | ❌ Invalid | Does not exist |

#### Key Features

| Feature | Support | Description |
|---------|---------|-------------|
| **Custom VM Configuration** | ✅ Yes | Granular control over VM settings |
| **Extensions** | ✅ Yes | Add extensions programmatically |
| **Windows PowerShell** | ✅ Yes | Native Windows automation |
| **Object Pipeline** | ✅ Yes | PowerShell object manipulation |
| **Custom Scripts** | ⚠️ Limited | Less flexible than Azure CLI for cloud-init |

#### When to Use Azure PowerShell

✅ **Windows-centric** environments  
✅ **Existing PowerShell** automation  
✅ **Complex VM configurations** with multiple components  
✅ **Integration** with other PowerShell scripts  

⚠️ **Not Ideal For:**
- Direct custom script execution during deployment (use Azure CLI instead)
- Cloud-init based customizations (Azure CLI has better support)

---

### Azure Portal

**Azure Portal** provides a web-based graphical interface for creating and managing VMs.

#### Features

| Feature | Support | Description |
|---------|---------|-------------|
| **Visual Interface** | ✅ Yes | Point-and-click deployment |
| **Wizard-Based** | ✅ Yes | Step-by-step VM creation |
| **Extensions** | ✅ Yes | Add extensions after deployment |
| **Custom Scripts** | ⚠️ Limited | Must configure post-deployment |

#### When to Use Azure Portal

✅ **One-off** deployments  
✅ **Learning** and exploration  
✅ **Visual configuration** preference  

❌ **Not Recommended For:**
- Automated deployments
- Custom initialization scripts
- Repeatable infrastructure

---

### ARM Templates

**Azure Resource Manager (ARM) Templates** provide declarative Infrastructure as Code.

#### Features

| Feature | Support | Description |
|---------|---------|-------------|
| **Declarative Syntax** | ✅ Yes | Define desired state |
| **Extensions** | ✅ Yes | Include custom script extensions |
| **Parameterization** | ✅ Yes | Reusable templates |
| **Version Control** | ✅ Yes | Track infrastructure changes |

#### When to Use ARM Templates

✅ **Infrastructure as Code**  
✅ **Repeatable deployments**  
✅ **Complex multi-resource** scenarios  
✅ **Enterprise** environments  

---

## Custom VM Deployments

### Cloud-Init for Linux VMs

**Cloud-init** is the industry-standard method for customizing Linux VMs during first boot.

#### Example: Installing Trusted Root CA

```yaml
#cloud-config
# cloud-init.txt

package_update: true
package_upgrade: true

write_files:
  - path: /usr/local/share/ca-certificates/custom-ca.crt
    permissions: '0644'
    encoding: b64
    content: |
      LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUR...
      (Base64 encoded certificate)

runcmd:
  - update-ca-certificates
  - systemctl restart your-service
```

#### Deploy with Azure CLI

```bash
az vm create \
  --resource-group myResourceGroup \
  --name myUbuntuVM \
  --image Ubuntu2204 \
  --custom-data cloud-init.txt \
  --admin-username azureuser \
  --generate-ssh-keys
```

#### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Package Management** | Install/update packages on first boot |
| **File Creation** | Write configuration files |
| **Command Execution** | Run arbitrary shell commands |
| **User Management** | Create users and groups |
| **Certificate Installation** | Add trusted root CAs |

---

### Custom Script Extension

**Custom Script Extension** allows you to run scripts on VMs after deployment.

#### Linux Custom Script Extension

```bash
# Add extension to existing VM
az vm extension set \
  --resource-group myResourceGroup \
  --vm-name myVM \
  --name customScript \
  --publisher Microsoft.Azure.Extensions \
  --settings '{"fileUris": ["https://raw.githubusercontent.com/example/install-ca.sh"],"commandToExecute": "./install-ca.sh"}'
```

#### Example: Install CA Script

```bash
#!/bin/bash
# install-ca.sh

# Download custom CA certificate
curl -o /usr/local/share/ca-certificates/custom-ca.crt \
  https://example.com/certs/custom-ca.crt

# Update CA certificates
update-ca-certificates

# Verify installation
ls -la /etc/ssl/certs/ | grep custom-ca
```

---

### Installing Trusted Root CA Certificates

#### Methods Comparison

| Method | Timing | Best For |
|--------|--------|----------|
| **Cloud-Init** | First boot | New VM deployments |
| **Custom Script Extension** | Post-deployment | Existing VMs or complex logic |
| **Manual** | On-demand | Testing, troubleshooting |

#### Cloud-Init Approach (Recommended for New VMs)

```yaml
#cloud-config
write_files:
  - path: /usr/local/share/ca-certificates/company-root-ca.crt
    permissions: '0644'
    content: |
      -----BEGIN CERTIFICATE-----
      MIIDXTCCAkWgAwIBAgIJAKL0UG+mRKZfMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
      ... (certificate content) ...
      -----END CERTIFICATE-----

runcmd:
  - update-ca-certificates
  - echo "CA certificate installed" >> /var/log/custom-init.log
```

#### Custom Script Extension Approach

```bash
# Create script to install CA
cat > install-ca.sh << 'EOF'
#!/bin/bash
set -e

# Certificate content
cat > /usr/local/share/ca-certificates/company-root-ca.crt << 'CERT'
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKL0UG+mRKZfMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
... (certificate content) ...
-----END CERTIFICATE-----
CERT

# Update CA trust store
update-ca-certificates

# Verify
if [ -f /etc/ssl/certs/company-root-ca.pem ]; then
  echo "CA certificate successfully installed"
else
  echo "CA certificate installation failed"
  exit 1
fi
EOF

# Upload script and execute via extension
az vm extension set \
  --resource-group myResourceGroup \
  --vm-name myUbuntuVM \
  --name customScript \
  --publisher Microsoft.Azure.Extensions \
  --protected-settings '{"fileUris": ["https://mystorageaccount.blob.core.windows.net/scripts/install-ca.sh"],"commandToExecute": "bash install-ca.sh"}'
```

---

## Tool Comparison

### Complete Comparison Matrix

| Tool | Custom Deployments | Automation | Cross-Platform | Cloud-Init Support | Scripting | Best For |
|------|-------------------|------------|----------------|-------------------|-----------|----------|
| **az vm create** | ✅✅✅ Excellent | ✅✅✅ | ✅✅✅ | ✅✅✅ Native | ✅✅✅ | Custom deployments, automation, CA installation |
| **New-AzVM** | ✅✅ Good | ✅✅ | ✅✅ | ⚠️ Limited | ✅✅ | PowerShell environments, Windows automation |
| **New-AzureRmVM** | ❌ Deprecated | ❌ | ❌ | ❌ | ❌ | Do not use (legacy) |
| **Create-AzVM** | ❌ Invalid | ❌ | ❌ | ❌ | ❌ | Does not exist |
| **Azure Portal** | ⚠️ Limited | ❌ | ✅✅✅ | ⚠️ Manual | ❌ | One-off deployments, learning |
| **ARM Templates** | ✅✅✅ | ✅✅✅ | ✅✅✅ | ✅✅ | ✅✅✅ | IaC, enterprise deployments |

### Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│              VM Creation Tool Selection                          │
│                                                                  │
│   Need custom deployment with CA installation?                  │
│   ├─ Yes ──► Need automation/scripting?                         │
│   │          ├─ Yes ──► Use Azure CLI (az vm create) ✅         │
│   │          └─ No  ──► Use Azure Portal + Custom Script Ext    │
│   │                                                              │
│   └─ No  ──► Prefer PowerShell?                                 │
│              ├─ Yes ──► Use New-AzVM                            │
│              └─ No  ──► Use az vm create or Portal              │
│                                                                  │
│   Need Infrastructure as Code?                                  │
│   └─ Yes ──► Use ARM Templates or Bicep                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## VM Migration and Movement

### Moving VMs Between Virtual Networks

**Important:** You cannot directly move a virtual machine from one VNet to another. The VM's network interface is permanently bound to its VNet and this binding cannot be changed while the VM exists.

#### The Disk Preservation Approach

When you need to move a VM's workload to a different VNet, follow this process:

1. **Delete the VM while retaining the disk**
   - The OS disk contains all installed applications and configurations
   - When deleting the VM, ensure you keep the OS disk
   - Only the VM resource is deleted, not the attached disks

2. **Create a new VM in the target VNet**
   - Create a new VM in the target resource group or VNet
   - During creation, attach the existing OS disk instead of creating a new one
   - Configure the new VM to connect to the target VNet
   - All applications and data remain intact on the disk

#### Key Limitations

| Operation | Supported | Explanation |
|-----------|-----------|-------------|
| **Move VM between VNets** | ❌ No | VMs cannot be moved between VNets directly |
| **Change NIC's VNet** | ❌ No | Network interfaces are bound to their VNet |
| **Attach/Detach NICs** | ✅ Yes | But cannot change which VNet the NIC belongs to |
| **Move Disks** | ✅ Yes | Disks can be attached to VMs in any VNet |
| **Move between Resource Groups** | ✅ Yes | VM can be moved to different resource group in same VNet |

#### Example Scenario

**Scenario:** You have VM1 in VNet1 (RG1) with a custom application installed. You need to move it to VNet2 (RG2).

**Solution:**

```bash
# Step 1: Note the disk name before deletion
DISK_ID=$(az vm show --resource-group RG1 --name VM1 --query "storageProfile.osDisk.managedDisk.id" -o tsv)

# Step 2: Delete VM1 (keeps the disk by default)
az vm delete --resource-group RG1 --name VM1 --yes

# Step 3: Create new VM in RG2 connected to VNet2, using the existing disk
az vm create \
  --resource-group RG2 \
  --name VM1-New \
  --attach-os-disk $DISK_ID \
  --os-type Linux \
  --vnet-name VNet2 \
  --subnet default
```

**Result:** The custom application is now running in VNet2 with minimal administrative effort (no reinstallation required).

#### Best Practices for VM Network Migration

| Practice | Description |
|----------|-------------|
| **Plan Networking First** | Ensure target VNet has proper subnets, NSGs, and connectivity |
| **Backup Before Migration** | Create snapshots of disks before deletion |
| **Document Dependencies** | Note all attached disks, extensions, and configurations |
| **Update DNS/Application Configs** | New VM will have different IP addresses |
| **Test Connectivity** | Verify network connectivity after recreation |
| **Use Tags** | Tag resources to track migration status |

---

## Best Practices

### VM Deployment Best Practices

| Practice | Description |
|----------|-------------|
| **Use Az Module** | Always use `New-AzVM`, never `New-AzureRmVM` |
| **Prefer Azure CLI for Custom Deployments** | Better cloud-init and custom script support |
| **Use Cloud-Init for Linux** | Industry standard, runs on first boot |
| **Store Scripts in Azure Storage** | Version control and security for custom script extensions |
| **Use Managed Identities** | Avoid hardcoding credentials in scripts |
| **Validate Cloud-Init Syntax** | Test YAML syntax before deployment |
| **Enable Boot Diagnostics** | Troubleshoot initialization failures |
| **Use ARM/Bicep for Production** | Infrastructure as Code for repeatability |

### Security Best Practices

| Practice | Description |
|----------|-------------|
| **Validate Certificates** | Verify CA certificate authenticity before installation |
| **Use HTTPS for Script Downloads** | Prevent man-in-the-middle attacks |
| **Minimize Script Privileges** | Run with least privilege necessary |
| **Enable Disk Encryption** | Azure Disk Encryption for data at rest |
| **Regular Updates** | Keep OS and packages updated |
| **Network Security Groups** | Restrict inbound/outbound traffic |

---

## Virtual Machine Scale Set (VMSS) Provisioning

### Overview

**Virtual Machine Scale Sets (VMSS)** allow you to create and manage a group of load-balanced VMs. The number of VM instances can automatically increase or decrease in response to demand or a defined schedule.

When deploying VMSS with specific software configurations (like web server components), you need to ensure the configuration is applied automatically during provisioning.

### Installing Components During VMSS Provisioning

To install components like web server (IIS) on Windows VMSS during provisioning, you need two key actions:

#### 1. Upload a Configuration Script

Create a PowerShell script (for Windows) or Bash script (for Linux) that installs the required components.

**Example: PowerShell script to install IIS**

```powershell
# install-iis.ps1
# Install IIS Web Server with management tools
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Optional: Enable additional IIS features
Install-WindowsFeature -Name Web-Asp-Net45
Install-WindowsFeature -Name Web-Net-Ext45

# Optional: Start the web service
Start-Service W3SVC

# Optional: Create a simple default page
Set-Content -Path "C:\inetpub\wwwroot\index.html" -Value "Hello from VMSS!"
```

**Upload the script to a location accessible by the VMSS:**
- Azure Storage Blob (recommended)
- GitHub repository (public URL)
- Any publicly accessible HTTPS endpoint

```bash
# Upload script to Azure Storage
az storage blob upload \
  --account-name mystorageaccount \
  --container-name scripts \
  --name install-iis.ps1 \
  --file install-iis.ps1
```

#### 2. Modify the extensionProfile Section of the ARM Template

The **extensionProfile** in the ARM template specifies VM extensions that run after the VM is provisioned. The **Custom Script Extension** downloads and executes your uploaded script.

**ARM Template - extensionProfile Section:**

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Compute/virtualMachineScaleSets",
      "apiVersion": "2021-03-01",
      "name": "myVMSS",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "Standard_DS2_v2",
        "tier": "Standard",
        "capacity": 2
      },
      "properties": {
        "virtualMachineProfile": {
          "storageProfile": {
            "imageReference": {
              "publisher": "MicrosoftWindowsServer",
              "offer": "WindowsServer",
              "sku": "2016-Datacenter",
              "version": "latest"
            }
          },
          "osProfile": {
            "computerNamePrefix": "vmss",
            "adminUsername": "[parameters('adminUsername')]",
            "adminPassword": "[parameters('adminPassword')]"
          },
          "networkProfile": {
            "networkInterfaceConfigurations": [
              {
                "name": "myNicConfig",
                "properties": {
                  "primary": true,
                  "ipConfigurations": [
                    {
                      "name": "myIPConfig",
                      "properties": {
                        "subnet": {
                          "id": "[parameters('subnetId')]"
                        }
                      }
                    }
                  ]
                }
              }
            ]
          },
          "extensionProfile": {
            "extensions": [
              {
                "name": "InstallWebServer",
                "properties": {
                  "publisher": "Microsoft.Compute",
                  "type": "CustomScriptExtension",
                  "typeHandlerVersion": "1.10",
                  "autoUpgradeMinorVersion": true,
                  "settings": {
                    "fileUris": [
                      "https://mystorageaccount.blob.core.windows.net/scripts/install-iis.ps1"
                    ],
                    "commandToExecute": "powershell -ExecutionPolicy Unrestricted -File install-iis.ps1"
                  }
                }
              }
            ]
          }
        },
        "upgradePolicy": {
          "mode": "Automatic"
        }
      }
    }
  ]
}
```

### Methods That Do NOT Work for VMSS Provisioning

| Method | Why It Doesn't Work |
|--------|---------------------|
| **Automation Account** | Automation accounts are for general automation tasks, not for component installation during VMSS provisioning. Custom Script Extension is the recommended approach. |
| **Azure Policy** | Azure policies enforce compliance and governance rules, not deployment-specific configurations like installing software components. |
| **Azure Portal (Create VMSS)** | Simply creating a VMSS doesn't automatically install web server components. You still need Custom Script Extension configuration. |

### Alternative Approaches

| Approach | Description | Best For |
|----------|-------------|----------|
| **Custom Script Extension (Recommended)** | Download and execute scripts during provisioning | VMSS provisioning, flexible configuration |
| **Custom VM Images** | Pre-create an image with IIS installed | Large-scale deployments, faster provisioning |
| **DSC Extension** | Desired State Configuration for Windows | Complex configurations, drift correction |
| **Cloud-Init (Linux)** | Standard Linux initialization | Linux VMSS deployments |

### Azure CLI Example

```bash
# Create VMSS with Custom Script Extension
az vmss create \
  --resource-group myResourceGroup \
  --name myVMSS \
  --image Win2016Datacenter \
  --upgrade-policy-mode automatic \
  --admin-username azureuser \
  --admin-password 'YourSecurePassword123!' \
  --instance-count 2

# Add Custom Script Extension to install IIS
az vmss extension set \
  --resource-group myResourceGroup \
  --vmss-name myVMSS \
  --name CustomScriptExtension \
  --publisher Microsoft.Compute \
  --settings '{"fileUris": ["https://mystorageaccount.blob.core.windows.net/scripts/install-iis.ps1"], "commandToExecute": "powershell -ExecutionPolicy Unrestricted -File install-iis.ps1"}'
```

---

## Practice Questions

### Question 1

**You are planning to deploy an Ubuntu Server virtual machine to your company's Azure subscription. You are required to implement a custom deployment that includes adding a particular trusted root certification authority (CA).**

**Which of the following should you use to create the Virtual Machine?**

A. The New-AzureRmVM cmdlet  
B. The az vm create command  
C. The Create-AzVM cmdlet  
D. The New-AzVM cmdlet

<details>
<summary>Answer</summary>

**B. The az vm create command**

**Explanation:**

The `az vm create` command from **Azure CLI** is the best choice for custom VM deployments that require adding custom configurations like trusted root CA certificates.

**Why Azure CLI is correct:**

1. **Native Cloud-Init Support**: Azure CLI has excellent support for cloud-init, which is the standard way to customize Linux VMs during first boot

2. **Custom-Data Parameter**: Allows you to specify a cloud-init configuration file:
   ```bash
   az vm create --custom-data cloud-init.txt
   ```

3. **Cross-Platform**: Works on Windows, macOS, and Linux, making it flexible for different development environments

4. **Scriptable and Automatable**: Perfect for CI/CD pipelines and Infrastructure as Code workflows

5. **Direct Custom Script Execution**: Easy integration with custom script extensions for post-deployment configuration

**Example for Installing Trusted Root CA:**

```bash
# Create cloud-init file
cat > cloud-init.txt << 'EOF'
#cloud-config
write_files:
  - path: /usr/local/share/ca-certificates/company-ca.crt
    permissions: '0644'
    content: |
      -----BEGIN CERTIFICATE-----
      MIIDXTCCAkWg... (certificate content)
      -----END CERTIFICATE-----
runcmd:
  - update-ca-certificates
EOF

# Deploy VM with custom CA
az vm create \
  --resource-group myResourceGroup \
  --name myUbuntuVM \
  --image Ubuntu2204 \
  --custom-data cloud-init.txt \
  --admin-username azureuser \
  --generate-ssh-keys
```

**Why other options are incorrect:**

| Option | Status | Explanation |
|--------|--------|-------------|
| **A. New-AzureRmVM** | ❌ Incorrect | This cmdlet is from the **deprecated AzureRM module** (deprecated since December 2018). It should not be used for new deployments. Microsoft recommends migrating to the Az module. |
| **C. Create-AzVM** | ❌ Incorrect | **This cmdlet does not exist**. There is no cmdlet named `Create-AzVM` in Azure PowerShell. The correct cmdlet is `New-AzVM` (not Create-AzVM). |
| **D. New-AzVM** | ⚠️ Partially Correct | While this is a valid cmdlet from the current Az module, it does **not support cloud-init as well as Azure CLI** does. PowerShell is better suited for Windows VMs or scenarios where you need complex object manipulation. For Linux custom deployments with initialization scripts, Azure CLI is the better choice. |

**Summary:**

For custom Linux VM deployments requiring trusted root CA installation, **Azure CLI (`az vm create`)** provides the most straightforward and flexible approach with native cloud-init support.

**Reference:** [Azure CLI az vm create](https://learn.microsoft.com/en-us/cli/azure/vm?view=azure-cli-latest#az-vm-create)

</details>

### Question 2

**You need to automate the deployment of 10 Ubuntu VMs, each requiring a custom trusted root CA certificate. Which approach provides the best combination of repeatability and maintainability?**

A. Use Azure Portal and manually configure each VM  
B. Use Azure CLI with cloud-init in a shell script  
C. Use ARM templates with cloud-init  
D. Use PowerShell with New-AzureRmVM cmdlet

<details>
<summary>Answer</summary>

**C. Use ARM templates with cloud-init**

**Explanation:**

For multiple VMs requiring identical custom configuration, **ARM templates with cloud-init** provide the best solution because:

1. **Infrastructure as Code**: ARM templates define the entire infrastructure declaratively
2. **Repeatability**: Same template can be deployed multiple times with consistent results
3. **Version Control**: Templates can be stored in Git for change tracking
4. **Parameterization**: Customize deployments using parameters
5. **Cloud-Init Integration**: Can embed cloud-init configuration in the template
6. **Maintainability**: Single source of truth for infrastructure

**Example ARM Template Snippet:**

```json
{
  "type": "Microsoft.Compute/virtualMachines",
  "properties": {
    "osProfile": {
      "customData": "[base64(variables('cloudInitContent'))]"
    }
  }
}
```

**Why other options are incorrect:**

- **A**: Manual configuration is not scalable or maintainable for 10 VMs
- **B**: Shell scripts work but lack the declarative benefits and Azure integration of ARM templates
- **D**: New-AzureRmVM is deprecated; should never be used

</details>

### Question 3

**You have an Azure subscription that contains two resource groups named RG1 and RG2. RG1 contains a virtual network VNet1. RG2 contains a virtual network VNet2. There is no connectivity between VNet1 and VNet2.**

**An administrator named Admin1 creates an Azure virtual machine named VM1 in RG1. VM1 uses a disk named Disk1 and connects to VNet1. Admin1 then installs a custom application in VM1.**

**You need to move the custom application to VNet2. The solution must minimize administrative effort.**

**Which two actions should you perform?**

A. Create a network interface in RG2  
B. Detach a network interface  
C. Delete VM1  
D. Attach a network interface  
E. Create a new virtual machine  
F. Move a network interface to RG2

<details>
<summary>Answer</summary>

**Correct Answers: C and E**

**C. Delete VM1**  
**E. Create a new virtual machine**

**Explanation:**

You cannot directly move a virtual machine between virtual networks. The VM's network interface is bound to a specific VNet, and this binding cannot be changed. The correct approach is to:

1. **First Action: Delete VM1**
   - Delete the virtual machine while **retaining the OS disk (Disk1)**
   - The disk contains the installed custom application
   - Only the VM compute resource is deleted, not the storage

2. **Second Action: Create a new virtual machine**
   - Create a new VM in RG2 (or RG1, but connected to VNet2)
   - During creation, attach the existing Disk1 as the OS disk
   - Connect the new VM to VNet2
   - The custom application remains intact and functional

**Why this minimizes administrative effort:**
- No need to reinstall the custom application
- No need to reconfigure the application
- No data migration required
- The disk is portable across VMs and VNets

**Why other options are incorrect:**

| Option | Status | Explanation |
|--------|--------|-------------|
| **A. Create a network interface in RG2** | ❌ Incorrect | While technically part of creating a new VM, this is handled automatically during VM creation. Not a standalone required action. |
| **B. Detach a network interface** | ❌ Incorrect | Detaching a NIC doesn't help move the VM to a different VNet. The NIC is bound to VNet1 and cannot be moved to VNet2. |
| **D. Attach a network interface** | ❌ Incorrect | You cannot attach a NIC from VNet1 to make the VM accessible in VNet2. NICs are bound to specific VNets. |
| **F. Move a network interface to RG2** | ❌ Incorrect | Moving a NIC to a different resource group doesn't change which VNet it's connected to. The NIC remains bound to VNet1. |

**Key Concepts:**

- **VMs are not portable** between VNets (must delete and recreate)
- **Disks are portable** across VMs and VNets
- **NICs are bound** to their VNet and cannot be moved between VNets
- **Resource groups** are logical containers; moving resources between them doesn't affect network connectivity

**Step-by-Step Process:**

```bash
# Step 1: Get the OS disk ID before deleting VM
az vm show --resource-group RG1 --name VM1 --query "storageProfile.osDisk.managedDisk.id"

# Step 2: Delete VM1 (disk is retained by default)
az vm delete --resource-group RG1 --name VM1 --yes

# Step 3: Create new VM in RG2 connected to VNet2 using existing disk
az vm create \
  --resource-group RG2 \
  --name VM1 \
  --attach-os-disk /subscriptions/.../Disk1 \
  --os-type Linux \
  --vnet-name VNet2 \
  --subnet default
```

**Reference:** [Move Azure VMs to another region](https://learn.microsoft.com/en-us/azure/resource-mover/tutorial-move-region-virtual-machines)

</details>

### Question 4

**You have an Azure virtual machine named VM1. VM1 was deployed by using a custom Azure Resource Manager template named ARM1.json.**

**You receive a notification that VM1 will be affected by maintenance.**

**You need to move VM1 to a different host immediately.**

**Solution: From the Redeploy blade, you click Redeploy.**

**Does this meet the goal?**

A. Yes  
B. No

<details>
<summary>Answer</summary>

**A. Yes**

**Explanation:**

Clicking **"Redeploy"** from the Redeploy blade (now called **"Redeploy + reapply"** in Azure Portal) is the correct and immediate solution to move a virtual machine to a different physical host.

**Why this solution works:**

1. **Immediate Host Migration**: The redeploy operation moves the VM from its current physical host to a different host within the same Azure region

2. **Bypasses Maintenance**: By redeploying immediately, you move the VM away from the host scheduled for maintenance, avoiding potential downtime during the maintenance window

3. **Configuration Preserved**: All VM configurations, disks, IP addresses (if static), and extensions are preserved during redeployment

4. **Azure-Managed Process**: Azure automatically selects a healthy target host and handles the migration

**How to Perform Redeploy:**

**Via Azure Portal:**
- Navigate to VM1 → Help → Redeploy + reapply → Click "Redeploy"

**Via Azure CLI:**
```bash
az vm redeploy --resource-group myResourceGroup --name VM1
```

**Via PowerShell:**
```powershell
Set-AzVM -Redeploy -ResourceGroupName "myResourceGroup" -Name "VM1"
```

**What Happens During Redeploy:**

| Phase | Action | Impact |
|-------|--------|--------|
| **1. Preparation** | VM configuration captured | No impact yet |
| **2. Shutdown** | VM is stopped | Service unavailable |
| **3. Migration** | VM moved to new host | Downtime (10-15 min) |
| **4. Restart** | VM started on new host | Service resuming |
| **5. Verification** | Health checks performed | Service available |

**Important Considerations:**

| Aspect | Details |
|--------|----------|
| **Downtime** | Expect 10-15 minutes of downtime |
| **Data Preservation** | OS disk and data disks are fully preserved |
| **Temporary Disk** | Data on temporary disk (D: or /mnt) will be lost |
| **IP Address** | Static IPs are preserved; dynamic IPs may change |
| **Same Region** | VM stays in the same region and availability zone |
| **No Manual Configuration** | No need to update ARM template or recreate resources |

**Alternative Solutions That Would NOT Work:**

| Action | Why It Doesn't Meet the Goal |
|--------|------------------------------|
| **Stop and Start** | Returns VM to the same host; doesn't move to different host |
| **Restart** | VM remains on same host |
| **Deallocate** | May or may not move to different host; not guaranteed |
| **Delete and Recreate** | Excessive administrative effort; risk of data loss |

**Best Practices:**

1. **Backup First**: Create a snapshot before redeploying (optional but recommended)
   ```bash
   az snapshot create --resource-group myRG --name VM1-snapshot --source $(az vm show --resource-group myRG --name VM1 --query storageProfile.osDisk.managedDisk.id -o tsv)
   ```

2. **Use Static IPs**: Ensure VM has static IP assignment to avoid connectivity issues

3. **Check Temporary Disk**: Move any important data from temporary disk before redeploying

4. **Schedule Appropriately**: Notify users about the brief downtime window

**Summary:**

The **Redeploy** feature is specifically designed for this scenario. It immediately moves the VM to a different physical host, allowing you to proactively avoid maintenance impact without waiting for the scheduled maintenance window.

**Reference:** 
- [Redeploy Windows VM](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/redeploy-to-new-node-windows)
- [Redeploy Linux VM](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/redeploy-to-new-node-linux)

</details>

### Question 5

**You plan to automate the deployment of a virtual machine scale set that uses the Windows Server 2016 Datacenter image.**

**You need to ensure that when the scale set virtual machines are provisioned, they have web server components installed.**

**Which two actions should you perform? Each correct answer presents part of the solution.**

A. Create an automation account  
B. Upload a configuration script  
C. Modify the extensionProfile section of the Azure Resource Manager template  
D. Create an Azure policy  
E. Create a new virtual machine scale set in the Azure portal

<details>
<summary>Answer</summary>

**Correct Answers: B and C**

**B. Upload a configuration script**  
**C. Modify the extensionProfile section of the Azure Resource Manager template**

**Explanation:**

To install web server components (like IIS) during VMSS provisioning, you need to use the **Custom Script Extension**. This requires two key actions:

**B. Upload a configuration script:**
- Create a PowerShell script (e.g., to install IIS) or Bash script (for Linux)
- Upload the script to a location accessible by the scale set:
  - Azure Storage Blob (recommended)
  - Public URL (GitHub, etc.)
- Example script to install IIS:

```powershell
# install-iis.ps1
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
```

**C. Modify the extensionProfile section of the ARM template:**
- The `extensionProfile` in the ARM template specifies VM extensions for the VMSS
- Include the **Azure Custom Script Extension** to download and execute the uploaded script
- The extension runs automatically during VM provisioning

```json
"extensionProfile": {
  "extensions": [
    {
      "name": "InstallWebServer",
      "properties": {
        "publisher": "Microsoft.Compute",
        "type": "CustomScriptExtension",
        "typeHandlerVersion": "1.10",
        "settings": {
          "fileUris": ["https://storage.blob.core.windows.net/scripts/install-iis.ps1"],
          "commandToExecute": "powershell -ExecutionPolicy Unrestricted -File install-iis.ps1"
        }
      }
    }
  ]
}
```

**Why other options are incorrect:**

| Option | Status | Explanation |
|--------|--------|-------------|
| **A. Create an automation account** | ❌ Incorrect | While automation accounts can be used for general automation, they are **not required for installing components during VMSS provisioning**. The Custom Script Extension is the recommended and direct approach. |
| **D. Create an Azure policy** | ❌ Incorrect | Azure policies enforce **compliance and governance**, not deployment-specific configurations. Policies audit or deny non-compliant resources—they don't install software components. |
| **E. Create a new virtual machine scale set in the Azure portal** | ❌ Incorrect | Simply creating a VMSS in the portal does **not address how to ensure web server components are installed during provisioning**. You still need the Custom Script Extension configuration. |

**Key Concepts:**

| Concept | Description |
|---------|-------------|
| **Custom Script Extension** | VM extension that downloads and executes scripts on VMs |
| **extensionProfile** | ARM template section that defines VM extensions for VMSS |
| **Provisioning-time Configuration** | Scripts run automatically when new VM instances are created |
| **Script Location** | Scripts must be accessible via HTTP/HTTPS URL |

**Alternative Approaches (Not Asked):**

| Approach | When to Use |
|----------|-------------|
| **Custom VM Image** | Pre-install IIS in image for faster provisioning |
| **DSC Extension** | Complex configurations requiring drift correction |
| **cloud-init (Linux)** | Standard Linux VM initialization |

**Summary:**

For Windows VMSS with web server components installed during provisioning:
1. ✅ **Upload a script** (install-iis.ps1) to Azure Storage
2. ✅ **Modify extensionProfile** in ARM template to use Custom Script Extension

**Reference:**
- [Virtual Machine Scale Sets Overview](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/overview)
- [Custom Script Extension for Windows](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-windows)
- [VMSS ARM Template Reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachinescalesets)

</details>

---

## References

- [Azure CLI az vm create](https://learn.microsoft.com/en-us/cli/azure/vm?view=azure-cli-latest#az-vm-create)
- [Azure PowerShell New-AzVM](https://learn.microsoft.com/en-us/powershell/module/az.compute/new-azvm)
- [Cloud-Init Documentation](https://cloudinit.readthedocs.io/)
- [Custom Script Extension for Linux](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-linux)
- [Custom Script Extension for Windows](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-windows)
- [Azure VM Extensions Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/overview)
- [Azure Resource Manager Templates](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)
- [Installing CA Certificates on Linux](https://ubuntu.com/server/docs/security-trust-store)
- [Redeploy Windows VM](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/redeploy-to-new-node-windows)
- [Redeploy Linux VM](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/redeploy-to-new-node-linux)
- [Azure VM Maintenance](https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates)
- [Virtual Machine Scale Sets Overview](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/overview)
- [VMSS ARM Template Reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.compute/virtualmachinescalesets)
