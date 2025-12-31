# Azure Storage Account Firewall and Virtual Network Security

## Overview

Azure Storage accounts can be secured by configuring firewall rules and virtual network access controls. This ensures that only authorized networks and services can access the storage account resources.

## Key Concepts

### Network Access Configuration

Azure Storage supports two primary network access modes:

1. **All networks**: Storage account is accessible from any network (default)
2. **Selected networks**: Access is restricted to specific virtual networks and IP ranges

### Virtual Network Service Endpoints

When using selected networks mode, you can:
- Add specific virtual network subnets that should have access
- Configure IP address ranges for internet or on-premises access
- Enable exceptions for trusted Microsoft services

## Critical Configuration Points

### 1. Virtual Network Subnet Requirements

**Important**: Only VMs within explicitly allowed subnets can access the storage account.

- The virtual network's address space alone is NOT sufficient
- You must add the specific subnet to the allowed list
- VMs must be on an enabled subnet to have connectivity

### 2. Trusted Microsoft Services Exception

The "Allow trusted Microsoft services to access this storage account" checkbox is critical for:

- **Azure Backup**: Requires this exception to back up unmanaged disks
- **Azure Site Recovery**: Needs access for replication
- **Azure Monitor**: For diagnostics and logging
- Other Microsoft services that need to access the storage account

**Without this exception enabled**: Azure Backup and other trusted services **cannot** access the storage account, even if they are Microsoft first-party services.

## Practical Example: Exam Scenario

### Configuration Shown

**Storage Account Settings:**
- Access Mode: Selected networks
- VNet Configuration:
  - VNet Name: VNet1
  - VNet Address Space: 10.2.0.0/16
  - Configured Subnet: Prod (10.2.0.0/24) - Enabled
- Trusted Microsoft Services: ❌ NOT enabled

### Question 1: VM Network Connectivity

**Question**: The virtual machines on the 10.2.9.0/24 subnet will have network connectivity to the file shares in the storage account [answer choice].

**Answer**: **never**

**Explanation**:
- VNet1's address space is 10.2.0.0/16
- Only one subnet is configured: 10.2.0.0/24 (Prod)
- This subnet provides addresses: 10.2.0.0 - 10.2.0.255
- VMs on 10.2.9.0/24 subnet (10.2.9.0 - 10.2.9.255) are **outside** the allowed subnet range
- Even though 10.2.9.0/24 is within the VNet's overall address space (10.2.0.0/16), the specific subnet is not added to the storage account's allowed networks

**Key Takeaway**: The VNet address space is irrelevant if the corresponding subnet is not explicitly added to the storage account's network rules.

### Question 2: Azure Backup Capability

**Question**: Azure Backup will be able to back up the unmanaged hard disks of the virtual machines in the storage account [answer choice].

**Answer**: **never**

**Explanation**:
- The "Allow trusted Microsoft services to access this storage account" checkbox is **NOT checked**
- Azure Backup is a trusted Microsoft service
- Without this exception enabled, Azure Backup cannot access the network-restricted storage account
- This applies regardless of backup schedules or VM configurations

**Key Takeaway**: Even Microsoft's own services need explicit permission via the trusted services exception when network restrictions are enabled.

### Question 3: VM Disk Upload and Access Configuration

**Scenario**:
You have an Azure subscription with a storage account named account1. You plan to:
- Upload disk files (.vhd) from on-premises network (public IP: 131.107.1.0/24)
- Use these disk files to provision VM1
- Attach VM1 to VNet1 (IP address space: 192.168.0.0/24)
- Prevent all other access to account1

**Question**: Which two actions should you perform to meet the requirements?

**Correct Answers**:

1. **From the Networking blade of account1, select Selected networks**
   - **Why**: This restricts access to only specified networks/IP ranges
   - **Impact**: Prevents all other access to the storage account (meets security requirement)
   - **Result**: Enhances security by denying all traffic except explicitly allowed sources

2. **From the Networking blade of account1, add the 131.107.1.0/24 IP address range**
   - **Why**: Allows the on-premises network to upload disk files
   - **Configuration**: Add to "Firewall" → "Address range" section
   - **Result**: Enables VHD upload from on-premises (meets upload requirement)

**Additional Configuration Needed** (after upload):

3. **From the Networking blade of account1, add VNet1**
   - **Why**: Allows VM1 to attach and access the VHD disks
   - **When**: Required after upload is complete, before VM provisioning
   - **Result**: Enables VM1 to access its disk files (meets attachment requirement)

**Analysis of Other Options**:

❌ **From the Service endpoints blade of VNet1, add a service endpoint**
- **Purpose**: Enhances performance and security for VNet-to-Storage connectivity
- **Not Mandatory**: Access can be granted through storage account networking settings alone
- **Benefit**: Improves latency and enables private IP routing
- **When Useful**: Production environments requiring optimal performance

❌ **From the Networking blade of account1, select Allow trusted Microsoft services**
- **Purpose**: Enables Azure Backup, Site Recovery, and other Microsoft services
- **Not Required**: This scenario doesn't involve trusted Microsoft services
- **Use Case**: Enable when using Azure Backup for unmanaged disks or Site Recovery

**Implementation Steps**:

```
Phase 1: Enable On-Premises Upload
1. Storage Account → Networking
2. Select "Selected networks"
3. Firewall section → Add IP range: 131.107.1.0/24
4. Save configuration
5. Upload VHD files from on-premises

Phase 2: Configure VM Access
6. Networking blade → Virtual networks section
7. Add VNet1 (192.168.0.0/24)
8. Optionally add service endpoint on VNet1 subnet
9. Save configuration
10. Provision VM1 and attach disks
```

**Key Insights**:

| Requirement | Configuration | Why |
|-------------|---------------|-----|
| Upload disks from on-premises | Add 131.107.1.0/24 IP range | Allows access from public IP space |
| Prevent other access | Select "Selected networks" | Restricts to explicit allow list |
| VM1 access to disks | Add VNet1 to allowed networks | VM needs to read VHD during boot/operation |
| Enhanced security (optional) | Service endpoint on VNet1 | Private IP routing, better performance |

**Security Best Practice**: Use "Selected networks" mode as the foundation, then explicitly add only required sources (on-premises IP + VNet). This follows the principle of least privilege.

## Best Practices

### 1. Network Security Configuration

```
✅ DO:
- Add specific subnets that need access
- Use the minimum required network access
- Enable service endpoints on VNet subnets
- Document which subnets have access and why

❌ DON'T:
- Assume VNet address space automatically grants access
- Forget to add required subnets
- Leave "All networks" enabled in production
```

### 2. Trusted Services Exception

```
✅ DO:
- Enable trusted services when using:
  - Azure Backup
  - Azure Site Recovery
  - Azure Monitor/diagnostics
  - Azure DevOps (for artifact storage)
- Review which Microsoft services need access

❌ DON'T:
- Disable trusted services without understanding impact
- Assume Microsoft services bypass network rules automatically
```

### 3. Firewall Rules

- Add public IP ranges for on-premises access
- Use CIDR notation for IP ranges
- Test access after configuration changes
- Monitor access logs to verify rules

## Configuration Steps

### Enable Network Restrictions

1. Navigate to Storage Account → Settings → Networking
2. Under "Firewalls and virtual networks":
   - Select "Selected networks"
3. Under "Virtual networks":
   - Click "+ Add existing virtual network"
   - Select the VNet and specific subnet(s)
   - Click "Add"
4. Under "Firewall" (optional):
   - Add IP address ranges for internet/on-premises access
5. Under "Exceptions":
   - ✅ Check "Allow trusted Microsoft services to access this storage account"
   - Configure logging/metrics exceptions as needed
6. Click "Save"

### Verify Configuration

```bash
# Test connectivity from allowed subnet
az storage blob list --account-name <storage-account-name> --container-name <container>

# Test connectivity from non-allowed network (should fail)
# Run from VM or network not in allowed list
az storage blob list --account-name <storage-account-name> --container-name <container>
# Expected: Connection error
```

## Common Issues and Solutions

### Issue 1: VMs Cannot Access Storage

**Symptoms**: VMs on VNet cannot access storage account

**Solutions**:
1. Verify the VM's subnet is added to allowed networks
2. Ensure service endpoint is enabled on the subnet
3. Check NSG rules aren't blocking traffic
4. Verify the VM's IP is within the subnet range

### Issue 2: Azure Backup Failing

**Symptoms**: Backup jobs fail with access denied errors

**Solutions**:
1. Enable "Allow trusted Microsoft services" checkbox
2. Verify backup vault has necessary permissions
3. Check if storage account is in same region as backup vault

### Issue 3: Unexpected Access Denials

**Symptoms**: Services that should have access are blocked

**Troubleshooting**:
1. Check diagnostic logs: Storage Account → Monitoring → Diagnostic settings
2. Review activity log for access attempts
3. Verify service endpoint configuration on subnet
4. Ensure no conflicting NSG rules

## Security Implications

### Defense in Depth

Network restrictions provide an additional security layer:
- **Network Layer**: Firewall and VNet rules
- **Identity Layer**: Azure AD authentication and RBAC
- **Data Layer**: Encryption at rest and in transit

### Compliance Considerations

- Many compliance frameworks require network isolation
- Document network access patterns for audits
- Regularly review and update network rules
- Use Azure Policy to enforce network restrictions

## Related Topics

- [Azure Storage Security](azure-storage-security-overview.md)
- [Azure VNet Service Endpoints](../../networking/azure-networking-fundamentals.md)
- [Azure Private Link for Storage](azure-storage-private-endpoints.md)
- [Azure Backup Overview](../../governance/azure-site-recovery-backup.md)

## References

- [Configure Azure Storage firewalls and virtual networks](https://learn.microsoft.com/azure/storage/common/storage-network-security)
- [Azure Storage security recommendations](https://learn.microsoft.com/azure/storage/blobs/security-recommendations)
- [Trusted access based on managed identity](https://learn.microsoft.com/azure/storage/common/storage-network-security#trusted-access-based-on-a-managed-identity)
