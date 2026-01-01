# Azure Network Watcher

Azure Network Watcher provides tools to monitor, diagnose, view metrics, and enable or disable logs for resources in an Azure virtual network. It is designed to monitor and repair the network health of IaaS (Infrastructure-as-a-Service) products which includes Virtual Machines, Virtual Networks, Application Gateways, Load balancers, etc.

## Key Capabilities

- **Monitoring**: Monitor communication between a virtual machine and an endpoint.
- **Diagnostics**: Diagnose network traffic filtering problems to or from a VM.
- **Logging**: Enable NSG flow logs to view information about ingress and egress IP traffic through a Network Security Group.

## Network Watcher Tools Summary

| Tool | Best Use Scenario | What It Does |
|------|-------------------|--------------|
| **IP Flow Verify** | Determine if a specific packet is allowed or denied to/from a VM | Checks effective NSG rules for a given VM; returns allow/deny decision and the rule name that caused it |
| **NSG Diagnostics** | Troubleshoot NSG rules affecting traffic flow | Provides detailed diagnostics for NSG rules, showing which rules apply to specific traffic |
| **Next Hop** | Diagnose VM routing issues | Shows the next hop type and IP address for traffic from a VM to a destination |
| **Connection Troubleshoot** | Test connectivity between Azure resources or to external endpoints | Tests TCP/ICMP connectivity and provides latency, probe status, and failure reasons |
| **Packet Capture** | Capture and analyze network packets for deep inspection | Records packets to/from a VM for detailed protocol-level analysis |
| **VPN Troubleshoot** | Diagnose VPN gateway and connection issues | Provides diagnostics for VPN gateways and site-to-site VPN connections |
| **NSG Flow Logs** | Log and audit all network traffic through NSGs | Records all traffic flowing through NSGs for compliance, auditing, and analysis |
| **Traffic Analytics** | High-level analysis of network traffic patterns and trends | Aggregates NSG flow log data for visualization of traffic volume, top talkers, and security insights |
| **Connection Monitor** | Continuous monitoring of network connectivity | Monitors connectivity between endpoints over time, alerting on failures or latency changes |
| **Topology** | Visualize network architecture | Generates a visual diagram of resources in a virtual network and their relationships |
| **Effective Security Rules** | View all security rules applied to a network interface | Shows the aggregated effective security rules from all NSGs applied to a NIC |

### Tool Selection Guide

| Troubleshooting Question | Recommended Tool |
|--------------------------|------------------|
| Is a specific packet being allowed or denied to my VM? | **IP Flow Verify** |
| What route is my traffic taking? | **Next Hop** |
| Can my VM reach a specific endpoint? | **Connection Troubleshoot** |
| What does the actual network traffic look like? | **Packet Capture** |
| Why is my VPN connection failing? | **VPN Troubleshoot** |
| What are the traffic patterns across my network? | **Traffic Analytics** |
| Is my connectivity stable over time? | **Connection Monitor** |
| What security rules are effective on my VM's NIC? | **Effective Security Rules** / **NSG Diagnostics** |

## Troubleshooting Scenarios

### Scenario: Analyzing VM Connectivity Issues (Allow/Deny)

**Context:**
Your company has deployed several virtual machines (VMs) on-premises and to Azure. Azure ExpressRoute has been deployed and configured for on-premises to Azure connectivity. Several VMs are exhibiting network connectivity issues.

**Goal:**
You need to analyze the network traffic to determine whether packets are being allowed or denied to the VMs.

**Proposed Solution:**
Use the **Azure Traffic Analytics** in Azure Network Watcher to analyze the network traffic.

**Evaluation:**
Does the solution meet the goal? **No**.

**Explanation:**
Azure Traffic Analytics provides high-level insights based on NSG flow logs but does not offer packet-level visibility or detailed VM-level allow/deny decisions. It is designed for aggregated analysis at the virtual network level, not for troubleshooting individual VM connectivity issues. Since the scenario involves identifying whether packets are being specifically allowed or denied to individual virtual machines, Traffic Analytics is not the appropriate tool.

Key limitations of Traffic Analytics for this scenario:
- Provides aggregated flow-level insights such as traffic volume, top talkers, protocol usage, and security alerts
- Does not show real-time allow/deny decisions for specific packets or connections
- Not suitable for troubleshooting individual VM connectivity issues where you need to determine whether a particular packet is allowed or blocked

**Correct Approach:**
To determine if a packet is allowed or denied to a specific VM, you should use **IP Flow Verify** in Azure Network Watcher. IP Flow Verify evaluates effective NSG rules for a given VM and can determine whether specific traffic is allowed or denied. The information consists of direction, protocol, local IP, remote IP, local port, and remote port. If the packet is denied by a security group, the name of the rule that denied the packet is returned.

---

### Scenario: Analyzing VM Connectivity Issues with VM Insights

**Context:**
Your company has deployed several virtual machines (VMs) on-premises and to Azure. Azure ExpressRoute has been deployed and configured for on-premises to Azure connectivity. Several VMs are exhibiting network connectivity issues.

**Goal:**
You need to analyze the network traffic to determine whether packets are being allowed or denied to the VMs.

**Proposed Solution:**
Install and configure the **Azure Monitoring Agent** and the **Dependency Agent** on all the virtual machines. Use the **VM Insights** in Azure Monitor to analyze the network traffic.

**Evaluation:**
Does the solution meet the goal? **No**.

**Explanation:**
VM Insights in Azure Monitor, enabled through the Azure Monitoring Agent and the Dependency Agent, provides dependency maps and connection data at the process and application level. While it shows which processes are communicating and identifies active TCP connections, it does not determine whether packets are being allowed or denied by network security groups (NSGs), firewall rules, or routing configurations.

**Correct Approach:**
To analyze whether packets are being explicitly allowed or denied, you need to use **Azure Network Watcher**, specifically the **IP Flow Verify** feature. This tool checks effective NSG rules for specific VMs and tells you whether traffic on a given port and protocol is allowed or blocked — which is the correct solution for diagnosing the type of issue described.

---

### Scenario: Enabling Traffic Analytics with Proper Role Assignment

**Context:**
You need to ensure that an Azure Active Directory (Azure AD) user named Admin1 is assigned the required role to enable Traffic Analytics for an Azure subscription.

**Goal:**
Assign the appropriate role to Admin1 to enable Traffic Analytics.

**Proposed Solution:**
Assign the **Traffic Manager Contributor** role at the subscription level to Admin1.

**Evaluation:**
Does the solution meet the goal? **No**.

**Explanation:**
Assigning the Traffic Manager Contributor role does not provide sufficient permissions to manage or enable Traffic Analytics, as this feature is **unrelated to Azure Traffic Manager**.

**Key Points:**
- **Traffic Analytics** is a feature of **Azure Network Watcher** that provides insights into network traffic patterns by analyzing NSG flow logs
- **Azure Traffic Manager** is a DNS-based traffic load balancing service - a completely different service
- The Traffic Manager Contributor role grants permissions only for managing Traffic Manager resources (DNS-based load balancing), not Network Watcher or Traffic Analytics

**Correct Approach:**
To enable Traffic Analytics, Admin1 needs one of the following roles at the subscription level:
- **Network Contributor** - Recommended role that provides permissions to manage all network resources including Network Watcher and Traffic Analytics
- **Owner** or **Contributor** - These broader roles also include the necessary permissions but provide more access than needed

**Required Permissions for Traffic Analytics:**
- Permissions to enable NSG flow logs
- Permissions to configure Log Analytics workspace
- Permissions to read and write Network Watcher resources
- Permissions to access storage accounts (where flow logs are stored)

**Common Misconception:**
Do not confuse Azure Traffic Manager (DNS-based global load balancing) with Traffic Analytics (network flow analysis tool). They are separate services with different purposes and different role requirements.

---

### Scenario: Recording All Connection Attempts to a VM

**Context:**
You have an Azure virtual machine (VM1) in East US region with the following configuration:
- Private IP: 10.0.0.4 (dynamic)
- Network Security Group: NSG1
- Public IP: None
- Availability set: AVSet
- Subnet: 10.0.0.0/24
- Managed disks: No

Your subscription has the following providers registered:
- Authorization, Automation, Resources, Compute, KeyVault, Network, Storage, Billing, Web

**Goal:**
You need to record ALL successful and failed connection attempts to VM1.

**Required Actions (3 correct answers):**

✅ **1. Register the Microsoft.Insights resource provider**
- Microsoft Insights is the resource provider for Azure monitoring and diagnostics
- Required to access monitoring services including Log Analytics and Application Insights
- Essential for enabling logging features needed to collect connection attempt data
- Without this provider, you cannot use advanced monitoring capabilities

✅ **2. Enable Azure Network Watcher in the East US Azure region**
- Network Watcher is a regional service that must be enabled in each region where you want to use it
- Provides network monitoring and diagnostic capabilities
- **Prerequisites**: Must be enabled in the same region as your resources (VM1 is in East US)
- Required before you can enable NSG flow logs or use any Network Watcher tools

✅ **3. Enable Azure Network Watcher flow logs (NSG Flow Logs)**
- **Primary solution** for recording successful and failed connection attempts at the network level
- Captures information about IP traffic flowing through network interfaces
- Records both inbound and outbound traffic through NSGs
- Logs include: source/destination IP, port, protocol, traffic decision (allowed/denied), and timestamp
- Version 2 flow logs also include flow state information (new, established, terminated)

**Why Other Options Are Incorrect:**

❌ **Add an Azure Network Watcher connection monitor**
- Connection Monitor is for **proactive monitoring** of connectivity between specific endpoints
- Tests if a VM **can connect to** another endpoint (outbound connectivity testing)
- Does **NOT** record all incoming connection attempts to a VM
- Use case: Monitoring specific connectivity paths and performance metrics, not comprehensive traffic logging

❌ **Register the Microsoft.LogAnalytics provider**
- Log Analytics is a destination/storage option for flow logs, not a requirement
- Flow logs can be stored in Azure Storage accounts **or** sent to Log Analytics
- While useful for analysis, it's not required to enable flow logging itself
- The critical provider is Microsoft.Insights, not LogAnalytics

❌ **Create an Azure Storage account**
- While a storage account **can** be used as a destination for flow logs, it's optional
- Flow logs can be sent directly to Log Analytics workspace instead
- Therefore, not a **required** step for recording connection attempts
- However, in practice, you typically need either a storage account **or** Log Analytics workspace

**Implementation Steps (Correct Order):**

1. **Register Microsoft.Insights provider** (if not already registered)
   ```bash
   az provider register --namespace Microsoft.Insights
   ```

2. **Enable Network Watcher in East US region**
   ```bash
   az network watcher configure --resource-group <rg-name> --locations eastus --enabled true
   ```

3. **Enable NSG Flow Logs for NSG1**
   ```bash
   az network watcher flow-log create \
     --resource-group <rg-name> \
     --nsg <nsg-name> \
     --name <flow-log-name> \
     --location eastus \
     --storage-account <storage-account-id> \
     --enabled true \
     --retention 7 \
     --format JSON \
     --log-version 2
   ```

**Key Concepts:**

- **NSG Flow Logs** are the cornerstone for recording all connection attempts
- **Flow Log Versions:**
  - Version 1: Basic flow information (5-tuple: source, destination, port, protocol, action)
  - Version 2: Adds flow state (bytes and packets transmitted)
- **Traffic Analytics** (optional): Provides visualization and analysis of flow log data
- **Connection Monitor** vs **Flow Logs**: Different purposes - proactive testing vs passive recording

**What Gets Recorded in NSG Flow Logs:**
- Source and destination IP addresses
- Source and destination ports
- Protocol (TCP/UDP)
- Traffic flow direction (inbound/outbound)
- Allow or deny decision (based on NSG rules)
- Number of packets and bytes
- Flow state (new, established, terminated) in v2

**Best Practice:**
For comprehensive connection monitoring, combine:
- **NSG Flow Logs**: Record all traffic (required for this scenario)
- **Traffic Analytics**: Visualize and analyze patterns
- **Connection Monitor**: Proactively test specific connectivity paths
- **Log Analytics**: Store and query flow log data for long-term analysis

## References

- [IP Flow Verify Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-ip-flow-verify-overview)
- [Traffic Analytics](https://learn.microsoft.com/en-us/azure/network-watcher/traffic-analytics)
- [Network Watcher Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-overview)
- [NSG Flow Logging Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-nsg-flow-logging-overview)
- [VM Insights Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/vminsights-overview)
- [VM Insights Dependency Agent](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/vminsights-dependency-agent)
- [Connection Monitor](https://learn.microsoft.com/en-us/azure/network-watcher/connection-monitor-overview)
- [Resource Providers Registration](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-providers-and-types)
