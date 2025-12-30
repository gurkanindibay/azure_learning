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
- [Tool Comparison](#tool-comparison)
- [Best Practices](#best-practices)
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

---

## References

- [Azure CLI az vm create](https://learn.microsoft.com/en-us/cli/azure/vm?view=azure-cli-latest#az-vm-create)
- [Azure PowerShell New-AzVM](https://learn.microsoft.com/en-us/powershell/module/az.compute/new-azvm)
- [Cloud-Init Documentation](https://cloudinit.readthedocs.io/)
- [Custom Script Extension for Linux](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-linux)
- [Azure VM Extensions Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/overview)
- [Azure Resource Manager Templates](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/overview)
- [Installing CA Certificates on Linux](https://ubuntu.com/server/docs/security-trust-store)
