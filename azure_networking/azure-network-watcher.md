# Azure Network Watcher

Azure Network Watcher provides tools to monitor, diagnose, view metrics, and enable or disable logs for resources in an Azure virtual network. It is designed to monitor and repair the network health of IaaS (Infrastructure-as-a-Service) products which includes Virtual Machines, Virtual Networks, Application Gateways, Load balancers, etc.

## Key Capabilities

- **Monitoring**: Monitor communication between a virtual machine and an endpoint.
- **Diagnostics**: Diagnose network traffic filtering problems to or from a VM.
- **Logging**: Enable NSG flow logs to view information about ingress and egress IP traffic through a Network Security Group.

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

## References

- [IP Flow Verify Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-ip-flow-verify-overview)
- [Traffic Analytics](https://learn.microsoft.com/en-us/azure/network-watcher/traffic-analytics)
- [Network Watcher Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-overview)
- [NSG Flow Logging Overview](https://learn.microsoft.com/en-us/azure/network-watcher/network-watcher-nsg-flow-logging-overview)
- [VM Insights Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/vminsights-overview)
- [VM Insights Dependency Agent](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/vminsights-dependency-agent)
