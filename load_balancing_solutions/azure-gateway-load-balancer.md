# Azure Gateway Load Balancer

## Overview

**Azure Gateway Load Balancer** is a Layer 4 load balancing service designed specifically for transparently inserting third-party Network Virtual Appliances (NVAs) into the network traffic path. It enables you to chain network security appliances such as firewalls, intrusion detection/prevention systems (IDS/IPS), deep packet inspection (DPI) tools, and other virtual appliances without requiring changes to your application configuration.

### Key Characteristics

- **Layer**: Layer 4 (TCP/UDP)
- **Scope**: Regional
- **Primary Use Case**: Transparent NVA chaining and traffic inspection
- **Deployment Model**: Inline with existing Load Balancers or Public IPs
- **Availability**: 99.99% SLA for Standard SKU

## Table of Contents

- [What is a Network Virtual Appliance (NVA)?](#what-is-a-network-virtual-appliance-nva)
- [Core Features](#core-features)
- [Architecture Patterns](#architecture-patterns)
- [Use Cases](#use-cases)
- [Configuration Components](#configuration-components)
- [Tunnel Protocol (VXLAN)](#tunnel-protocol-vxlan)
- [Pricing](#pricing)
- [Configuration Steps](#configuration-steps)
- [Comparison: Gateway Load Balancer vs Standard Load Balancer](#comparison-gateway-load-balancer-vs-standard-load-balancer)
- [Best Practices](#best-practices)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Integration Scenarios](#integration-scenarios)
- [Limitations and Considerations](#limitations-and-considerations)
- [Security Considerations](#security-considerations)
- [When to Use Gateway Load Balancer](#when-to-use-gateway-load-balancer)
- [Related Services](#related-services)
- [References](#references)

## What is a Network Virtual Appliance (NVA)?

**Network Virtual Appliance (NVA)** is a virtual machine that performs specialized network functions in the cloud, typically security or network optimization tasks. NVAs are the core component that Gateway Load Balancer integrates into your traffic flow.

### Common Types of NVAs

#### Security Appliances
- **Next-Generation Firewalls (NGFW)** - Palo Alto Networks, Fortinet FortiGate, Check Point CloudGuard
- **Intrusion Detection/Prevention Systems (IDS/IPS)** - Cisco Firepower, Trend Micro Deep Security
- **Web Application Firewalls (WAF)** - F5 Advanced WAF, Imperva
- **Advanced Threat Protection (ATP)** - Specialized malware detection and prevention
- **Data Loss Prevention (DLP)** - Monitor and prevent sensitive data exfiltration

#### Network Functions
- **SD-WAN Appliances** - VMware VeloCloud, Cisco Viptela
- **WAN Optimizers** - Riverbed, Silver Peak
- **Deep Packet Inspection (DPI)** - Protocol analysis and application identification
- **Network Monitoring Tools** - Traffic analyzers and performance monitors
- **Load Balancers** - Third-party load balancing solutions

### Key Characteristics of NVAs

1. **Third-Party Software**
   - Typically from established vendors (Palo Alto, Fortinet, Cisco, Check Point, F5)
   - Available in Azure Marketplace or as custom deployments
   - Often enterprise-grade solutions with extensive features

2. **Runs as Azure VMs**
   - Deployed as virtual machines in your subscription
   - Can be single instances or scale sets
   - Requires appropriate VM sizing for performance

3. **Specialized Functionality**
   - Performs tasks beyond Azure-native services
   - Vendor-specific features and protocols
   - Advanced security capabilities

4. **Licensing Requirements**
   - **BYOL (Bring Your Own License)** - Use existing licenses
   - **PAYG (Pay As You Go)** - Per-hour licensing through Azure
   - Costs often exceed infrastructure costs

### Why Use NVAs with Gateway Load Balancer?

- **✅ Existing Investments** - Leverage tools your organization already uses
- **✅ Specific Features** - Vendor-specific capabilities not available in Azure-native services
- **✅ Compliance Requirements** - Meet regulations requiring specific security tools
- **✅ Consistency** - Use same security tools across on-premises and cloud environments
- **✅ Advanced Inspection** - Deep packet inspection, custom protocols, specialized threat detection
- **✅ Multi-Layer Security** - Combine different NVA types for defense in depth

### How Gateway Load Balancer Works with NVAs

Gateway Load Balancer transparently inserts NVAs into your traffic flow:

```
1. Traffic arrives at your Public IP or Load Balancer
2. Gateway LB intercepts and encapsulates traffic (VXLAN)
3. Traffic is distributed to healthy NVA instances
4. NVAs inspect, filter, or monitor the traffic
5. NVAs return traffic to Gateway LB
6. Gateway LB decapsulates and forwards to destination
```

**Key Benefit**: Your applications require **no configuration changes** - the insertion is completely transparent.

## Core Features

### 1. Transparent Insertion
- **Bump-in-the-wire** architecture
- No application configuration changes required
- Traffic automatically flows through NVAs
- Supports both inbound and outbound traffic

### 2. High Availability
- Automatic health monitoring of NVAs
- Traffic distributed across multiple NVA instances
- Zone-redundant deployment support
- Automatic failover for unhealthy appliances

### 3. Scalability
- Auto-scaling support for NVA pools
- Handles up to 100 Gbps throughput
- Elastic scaling based on traffic patterns
- Multiple backend pools supported

### 4. Protocol Support
- All TCP and UDP protocols
- Supports both IPv4 and IPv6
- Preserves original packet information
- Low latency insertion (~microseconds)

### 5. Chaining Capabilities
- Can be chained with Standard Load Balancer
- Works with Public IP addresses
- Supports internal and external traffic flows
- Multiple NVA types in sequence

## Architecture Patterns

### Pattern 1: Public Endpoint Protection
```
Internet → Public IP (with Gateway LB) → Gateway Load Balancer → NVAs → Standard Load Balancer → Backends
```
**Use Case**: Protect public-facing applications with third-party firewall/IPS

### Pattern 2: Internal Traffic Inspection
```
VNET → Internal Load Balancer (with Gateway LB) → Gateway Load Balancer → NVAs → Application VMs
```
**Use Case**: Inspect east-west traffic between internal services

### Pattern 3: Multi-NVA Chaining
```
Traffic → Gateway LB 1 → Firewall NVAs → Gateway LB 2 → IDS/IPS NVAs → Application
```
**Use Case**: Multiple security layers with different NVA types

### Architecture Diagram Concept
```
┌─────────────┐
│   Internet  │
└──────┬──────┘
       │
┌──────▼──────────────┐
│  Public IP Address  │
│  (Gateway LB ref)   │
└──────┬──────────────┘
       │
┌──────▼───────────────┐
│ Gateway Load Balancer│
│  - Health Probes     │
│  - Load Balancing    │
└──────┬───────────────┘
       │
┌──────▼──────────────────────┐
│    NVA Backend Pool          │
│  ┌─────┐  ┌─────┐  ┌─────┐  │
│  │NVA-1│  │NVA-2│  │NVA-3│  │
│  └─────┘  └─────┘  └─────┘  │
└──────┬───────────────────────┘
       │
┌──────▼──────────────┐
│ Standard Load        │
│ Balancer             │
└──────┬───────────────┘
       │
┌──────▼──────────────┐
│  Backend Pool        │
│  (App VMs)           │
└──────────────────────┘
```

## Use Cases

### 1. Security Appliance Integration
**Scenario**: Insert third-party firewall or IPS in front of applications
- Next-generation firewalls (NGFW)
- Intrusion detection/prevention systems
- Advanced threat protection
- **Example**: Palo Alto Networks, Fortinet, Check Point

### 2. Network Monitoring and Analytics
**Scenario**: Deep packet inspection and traffic analysis
- Network performance monitoring
- Application performance management
- Protocol analysis
- Traffic recording and forensics

### 3. Compliance Requirements
**Scenario**: Meet regulatory requirements for traffic inspection
- Financial services compliance (PCI DSS)
- Healthcare regulations (HIPAA)
- Government security standards
- Industry-specific requirements

### 4. Multi-Tenant Environments
**Scenario**: Provide per-tenant security appliances
- Managed service providers (MSPs)
- SaaS platforms with security requirements
- Enterprise multi-tenant applications
- Isolated security policies per customer

### 5. Hybrid Security Solutions
**Scenario**: Integrate on-premises security solutions
- Extend existing security infrastructure to Azure
- Consistent security policies across hybrid cloud
- Centralized security management
- Unified threat intelligence

## Configuration Components

### 1. Frontend IP Configuration
- Public or internal IP address
- IPv4 and IPv6 support
- Zone redundancy options
- Multiple frontend IPs supported

### 2. Backend Pools
- NVA virtual machines or scale sets
- Health probe monitoring
- Load distribution algorithms
- Cross-zone load balancing

### 3. Load Balancing Rules
- Protocol: TCP or UDP
- Port configuration: All ports or specific
- Session persistence options
- Timeout settings

### 4. Health Probes
- TCP or HTTP/HTTPS probes
- Configurable intervals and thresholds
- Automatic unhealthy instance removal
- Recovery detection

### 5. Tunnel Interface
- VXLAN encapsulation
- Preserves original source/destination IPs
- Metadata for traffic identification
- Internal and external identifier support

## Tunnel Protocol (VXLAN)

Gateway Load Balancer uses **VXLAN** (Virtual Extensible LAN) tunneling to preserve packet information:

### VXLAN Headers
- **Outer IP**: Gateway LB ↔ NVA communication
- **VXLAN Header**: Includes internal and external identifiers
- **Inner IP**: Original packet (preserved)

### Identifiers
- **Internal Identifier**: Identifies the connection
- **External Identifier**: Identifies the Gateway LB instance
- Used by NVAs to route return traffic correctly

### NVA Requirements
- Must support VXLAN encapsulation/decapsulation
- Must preserve inner packet integrity
- Should handle identifier metadata
- Return traffic must use same tunnel

## Pricing

### Standard SKU
Gateway Load Balancer uses the **Standard SKU** pricing model:

#### Base Costs
- **Fixed cost**: ~$0.025 per hour (~$18/month)
- **Data processed**: ~$0.005 per GB
- **Rules**: First 5 rules included, $0.01 per additional rule

### Example Monthly Costs

#### Small Deployment (100 GB/month)
```
Fixed cost:     $18/month
Data (100 GB):  $0.50/month
Total:          ~$18.50/month
```

#### Medium Deployment (1 TB/month)
```
Fixed cost:     $18/month
Data (1000 GB): $5/month
Total:          ~$23/month
```

#### Large Deployment (10 TB/month)
```
Fixed cost:      $18/month
Data (10000 GB): $50/month
Total:           ~$68/month
```

#### Enterprise Deployment (50 TB/month)
```
Fixed cost:      $18/month
Data (50000 GB): $250/month
Total:           ~$268/month
```

### Additional Costs to Consider

1. **NVA Costs**: Virtual machine costs for security appliances
   - Typically $100-2000+/month depending on size and licensing
   - Often the primary cost component

2. **Standard Load Balancer**: If chained with existing load balancer
   - ~$18-35/month

3. **NVA Licensing**: Third-party software licenses
   - Varies by vendor (BYOL or PAYG)
   - Can be $500-5000+/month for enterprise appliances

4. **Bandwidth**: Data transfer charges
   - Outbound data transfer rates apply
   - Cross-region data transfer if applicable

### Cost Optimization Tips

✅ **Right-size NVA instances** - Don't over-provision security appliances  
✅ **Use VMSS auto-scaling** - Scale NVAs based on actual traffic  
✅ **Consolidate traffic flows** - Single Gateway LB for multiple applications  
✅ **Monitor health probe frequency** - Reduce unnecessary checks  
✅ **Use BYOL licensing** - Often cheaper than PAYG for consistent workloads  
✅ **Zone-redundant deployment** - Balance cost vs. availability needs  

## Configuration Steps

### Step 1: Create Gateway Load Balancer
```bash
# Create Gateway Load Balancer
az network lb create \
  --resource-group myResourceGroup \
  --name myGatewayLB \
  --sku Standard \
  --type Gateway \
  --frontend-ip-name myFrontend \
  --vnet-name myVnet \
  --subnet mySubnet
```

### Step 2: Create Backend Pool
```bash
# Create backend pool for NVAs
az network lb address-pool create \
  --resource-group myResourceGroup \
  --lb-name myGatewayLB \
  --name myNVAPool \
  --tunnel-interface \
    protocol=VXLAN \
    identifier=900 \
    type=Internal \
    port=10800
```

### Step 3: Create Health Probe
```bash
# Create health probe
az network lb probe create \
  --resource-group myResourceGroup \
  --lb-name myGatewayLB \
  --name myHealthProbe \
  --protocol tcp \
  --port 80 \
  --interval 5 \
  --threshold 2
```

### Step 4: Create Load Balancing Rule
```bash
# Create load balancing rule
az network lb rule create \
  --resource-group myResourceGroup \
  --lb-name myGatewayLB \
  --name myLBRule \
  --protocol All \
  --frontend-port 0 \
  --backend-port 0 \
  --backend-pool-name myNVAPool \
  --probe-name myHealthProbe
```

### Step 5: Associate with Public IP
```bash
# Associate Gateway LB with Public IP
az network public-ip update \
  --resource-group myResourceGroup \
  --name myPublicIP \
  --gateway-load-balancer myGatewayLB
```

### Step 6: Configure NVAs
- Deploy NVA VMs or scale sets
- Configure VXLAN support
- Add to backend pool
- Verify health probe response

## Comparison: Gateway Load Balancer vs Standard Load Balancer

| Feature | Gateway Load Balancer | Standard Load Balancer |
|---------|----------------------|------------------------|
| **Primary Purpose** | NVA insertion | Application load distribution |
| **Traffic Flow** | Transparent bump-in-wire | Endpoint termination |
| **Use Case** | Security appliances | Application backends |
| **Protocol** | Layer 4 (all TCP/UDP) | Layer 4 (TCP/UDP) |
| **Encapsulation** | VXLAN required | None |
| **Backend Types** | NVAs only | Any VM/VMSS |
| **Chaining** | With LB or Public IP | With Gateway LB |
| **Application Changes** | None required | None required |
| **Typical Cost** | $20-150/month | $20-100/month |

## Best Practices

### Design Considerations

1. **NVA Selection**
   - ✅ Choose NVAs with VXLAN support
   - ✅ Verify Azure marketplace compatibility
   - ✅ Test throughput requirements
   - ✅ Consider licensing models

2. **High Availability**
   - ✅ Deploy NVAs across availability zones
   - ✅ Use VM scale sets for auto-scaling
   - ✅ Configure proper health probes
   - ✅ Test failover scenarios

3. **Performance**
   - ✅ Right-size NVA instances for throughput
   - ✅ Monitor latency impact
   - ✅ Use accelerated networking
   - ✅ Optimize NVA configuration

4. **Security**
   - ✅ Secure NVA management interfaces
   - ✅ Use NSGs for defense in depth
   - ✅ Enable diagnostic logging
   - ✅ Implement least privilege access

5. **Monitoring**
   - ✅ Enable Azure Monitor metrics
   - ✅ Configure health probe alerts
   - ✅ Monitor NVA performance
   - ✅ Track data processed volume

### Configuration Best Practices

✅ **Use Standard SKU only** - Gateway LB requires Standard SKU  
✅ **Zone redundancy** - Deploy across zones for 99.99% SLA  
✅ **Health probe tuning** - Balance detection speed vs false positives  
✅ **Session persistence** - Configure if NVAs maintain state  
✅ **Tunnel identifiers** - Use unique identifiers per Gateway LB  
✅ **Documentation** - Maintain network flow diagrams  

### Common Pitfalls to Avoid

❌ **Not testing NVA VXLAN support** - Verify compatibility before production  
❌ **Under-sizing NVA instances** - Can create performance bottleneck  
❌ **Improper health probe config** - May cause unnecessary failovers  
❌ **Missing monitoring** - Hard to troubleshoot without metrics  
❌ **Single zone deployment** - Reduces availability  
❌ **Ignoring latency impact** - NVAs add processing overhead  

## Monitoring and Troubleshooting

### Key Metrics

1. **Data Path Availability**
   - Health probe status
   - Backend instance health
   - Overall availability percentage

2. **Throughput**
   - Bytes processed
   - Packet count
   - Data path throughput

3. **Connection Metrics**
   - SNAT connection count
   - SNAT port usage
   - Connection state

### Diagnostic Logs

Enable diagnostic logging for:
- Load balancer health probe logs
- Resource health events
- Metric data
- Activity logs

### Common Issues

#### Issue 1: NVA Not Receiving Traffic
**Symptoms**: Health probe succeeds but no traffic flows
**Solutions**:
- Verify VXLAN configuration on NVA
- Check tunnel interface parameters
- Validate backend pool membership
- Review NSG rules

#### Issue 2: High Latency
**Symptoms**: Increased response times
**Solutions**:
- Check NVA instance size/performance
- Monitor CPU/memory on NVAs
- Review NVA processing configuration
- Consider scaling out NVA pool

#### Issue 3: Health Probe Failures
**Symptoms**: Intermittent backend unhealthy
**Solutions**:
- Adjust probe interval/threshold
- Verify NVA health probe endpoint
- Check NVA resource utilization
- Review network connectivity

## Integration Scenarios

### With Standard Load Balancer
```
Public IP → Gateway LB → NVAs → Standard LB → Application VMs
```
**Purpose**: Add security inspection to existing load-balanced application

### With Application Gateway
```
Public IP → App Gateway → Gateway LB → NVAs → Backend Pool
```
**Purpose**: Layer 7 routing + Layer 4 security inspection

### With Azure Firewall
```
Internet → Azure Firewall → Gateway LB → NVAs (IDS/IPS) → Application
```
**Purpose**: Combine Azure-native firewall with third-party IDS/IPS

### Multi-Region with Traffic Manager
```
Traffic Manager
├── Region 1: Gateway LB → NVAs → Application
└── Region 2: Gateway LB → NVAs → Application
```
**Purpose**: Global distribution with consistent security posture

## Limitations and Considerations

### Current Limitations

1. **Standard SKU Only**
   - Basic SKU not supported
   - Requires Standard Load Balancer or Standard Public IP

2. **Regional Resource**
   - No cross-region load balancing
   - Deploy per region

3. **VXLAN Requirement**
   - NVAs must support VXLAN
   - Custom encapsulation not supported

4. **Backend Type**
   - Only supports NVA virtual machines
   - Cannot mix with non-NVA backends

5. **Protocol Support**
   - Layer 4 only (TCP/UDP)
   - No Layer 7 features

### Planning Considerations

- **Latency**: Adds microseconds of latency for VXLAN processing
- **Throughput**: NVA capacity becomes limiting factor
- **Cost**: NVA licensing often exceeds infrastructure costs
- **Complexity**: Adds another component to architecture
- **Vendor Support**: Verify Azure support from NVA vendor

## Security Considerations

### Network Security

1. **NVA Management**
   - Isolate management interfaces
   - Use Azure Bastion or VPN
   - Apply NSGs to management NICs
   - Enable MFA for access

2. **Data Plane Security**
   - Ensure NVA traffic inspection is enabled
   - Validate security policies
   - Regular signature updates
   - Monitor for bypasses

3. **Identity and Access**
   - Use managed identities where possible
   - Apply RBAC to Gateway LB resources
   - Audit configuration changes
   - Separate admin roles

### Compliance

- **Audit Logging**: Enable all diagnostic logs
- **Encryption**: Traffic between components uses Azure backbone
- **Compliance Certifications**: Inherits Azure certifications
- **Data Residency**: Regional deployment ensures data locality

## When to Use Gateway Load Balancer

### ✅ Use Gateway Load Balancer When:

- Need to insert third-party security appliances transparently
- Require specific vendor firewall/IPS functionality
- Have compliance requirements for traffic inspection
- Want to leverage existing NVA investments
- Need high-availability for security appliances
- Application cannot be modified for security integration

### ❌ Don't Use Gateway Load Balancer When:

- Azure-native security services meet requirements (Azure Firewall, NSG)
- Don't need transparent NVA insertion
- Simple Layer 4 load balancing is sufficient (use Standard Load Balancer)
- Layer 7 features needed (use Application Gateway or Front Door)
- Cost constraints don't justify NVA licensing
- Latency is critical (NVAs add overhead)

## Related Services

### Complementary Services
- **Azure Firewall**: Native Layer 4-7 firewall service
- **Standard Load Balancer**: Application load distribution
- **Application Gateway**: Layer 7 load balancing with WAF
- **Network Security Groups**: Subnet/NIC level filtering

### Alternative Solutions
- **Azure Firewall Premium**: Native IDS/IPS and TLS inspection
- **Application Gateway WAF**: Layer 7 web application firewall
- **Azure DDoS Protection**: DDoS mitigation service
- **Azure Front Door WAF**: Global web application firewall

## References

### Microsoft Documentation
- [Gateway Load Balancer Overview](https://learn.microsoft.com/azure/load-balancer/gateway-overview)
- [Create Gateway Load Balancer](https://learn.microsoft.com/azure/load-balancer/gateway-create)
- [Chain Gateway Load Balancer](https://learn.microsoft.com/azure/load-balancer/gateway-chain)
- [Gateway Load Balancer Partners](https://learn.microsoft.com/azure/load-balancer/gateway-partners)

### Architecture Guidance
- [NVA High Availability](https://learn.microsoft.com/azure/architecture/reference-architectures/dmz/nva-ha)
- [Network Security Architecture](https://learn.microsoft.com/azure/architecture/framework/security/design-network)

### Related Documentation
- [Main Load Balancing Overview](./azure_load_balancing_options.md)
- [Azure Load Balancer](./azure-load-balancer.md)
- [Azure Application Gateway](./azure-application-gateway.md)

---

**Last Updated**: December 2025  
**Document Version**: 1.0
