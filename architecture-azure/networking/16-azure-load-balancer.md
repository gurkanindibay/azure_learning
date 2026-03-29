# Azure Load Balancer

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Typical Topology](#typical-topology)
- [Why Use It as a Proxy](#why-use-it-as-a-proxy)
- [Pricing Tiers](#pricing-tiers)
  - [Basic Load Balancer](#basic-load-balancer)
  - [Standard Load Balancer](#standard-load-balancer)
- [SKU Comparison](#sku-comparison)
- [Load Balancing Algorithms](#load-balancing-algorithms)
  - [Distribution Modes](#distribution-modes)
- [Health Probes](#health-probes)
  - [Probe Types](#probe-types)
  - [Probe Configuration](#probe-configuration)
  - [Best Practices](#best-practices)
- [Common Use Cases](#common-use-cases)
- [Architecture Patterns](#architecture-patterns)
- [Outbound Connectivity (Standard SKU)](#outbound-connectivity-standard-sku)
  - [Outbound Rules](#outbound-rules)
  - [SNAT Port Allocation](#snat-port-allocation)
- [High Availability Configuration](#high-availability-configuration)
  - [Zone-Redundant Frontend](#zone-redundant-frontend)
  - [Zonal Backend Pools](#zonal-backend-pools)
  - [Cross-Region Load Balancer](#cross-region-load-balancer)
- [Best Practices](#best-practices-1)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [When to Choose Load Balancer](#when-to-choose-load-balancer)
- [Integration with Other Azure Services](#integration-with-other-azure-services)
- [Monitoring and Diagnostics](#monitoring-and-diagnostics)
- [Security Considerations](#security-considerations)
- [Exam Scenario: Multi-Tier Application Load Balancing](#exam-scenario-multi-tier-application-load-balancing)
- [References](#references)

## Overview

**Layer/scope:** Regional Layer 4 (TCP/UDP) load balancer.

**Purpose:** Distributes traffic across VMs or VM scale sets within a region, typically used for internal service-to-service traffic or for simple public TCP endpoints.

## Key Features

- Public and internal (private) frontends
- Basic or Standard SKU for different performance/SLAs
- Health probes and session persistence (floating IP)
- No native Layer 7 inspection or API policies
- High throughput, low latency
- Zone redundancy (Standard SKU)
- HA ports (Standard SKU)
- Outbound rules (Standard SKU)

## Typical Topology

Load Balancer balances raw TCP traffic for APIs running on VMs or Kubernetes clusters and is often paired with Azure Application Gateway or APIM if Layer 7 functionality is required.

## Why Use It as a Proxy

Use Azure Load Balancer when you need resilient regional TCP/UDP routing for API traffic that does not require HTTP-specific processing.

## Pricing Tiers

### Basic Load Balancer

**Pricing**: **FREE**

**Features**:
- ✅ Public and internal load balancing
- ✅ TCP/UDP support
- ✅ Health probes
- ✅ Port forwarding
- ✅ Up to 300 instances
- ❌ No SLA
- ❌ No availability zones
- ❌ Limited to single availability set
- ❌ No outbound rules

**Best For**: Development/testing, non-production workloads

### Standard Load Balancer

**Pricing Components**:
- **Rules**: ~$0.025/hour per rule (~$18.25/month)
- **Data processed**: ~$0.005 per GB

**Features**:
- ✅ 99.99% SLA
- ✅ Availability zone redundancy
- ✅ Up to 1,000 instances
- ✅ HA ports
- ✅ Outbound rules
- ✅ HTTPS health probes
- ✅ Multiple frontends
- ✅ Diagnostic logs

**Best For**: Production workloads requiring high availability

**Cost Example**:
```
Setup: 5 load balancing rules, 500 GB/month data processed
- Rules: 5 × $18.25 = $91.25/month
- Data: 500 × $0.005 = $2.50
Total: ~$94/month
```

## SKU Comparison

| Feature | Basic | Standard |
|---------|-------|----------|
| **Price** | Free | ~$18/rule + $0.005/GB |
| **SLA** | None | 99.99% |
| **Backend Pool Size** | Up to 300 | Up to 1,000 |
| **Health Probes** | HTTP, HTTPS, TCP | HTTP, HTTPS, TCP |
| **Availability Zones** | ❌ No | ✅ Yes |
| **HA Ports** | ❌ No | ✅ Yes |
| **Outbound Rules** | ❌ No | ✅ Yes |
| **Multiple Frontends** | Limited | ✅ Yes |
| **Backend Pool by IP** | ❌ No | ✅ Yes |
| **Diagnostics** | Basic metrics | Azure Monitor integration |
| **Security** | NSG optional | NSG required |

## Load Balancing Algorithms

### Distribution Modes

1. **Five-tuple hash (default)**
   - Source IP
   - Source port
   - Destination IP
   - Destination port
   - Protocol type
   - Provides good distribution across backends

2. **Source IP affinity (session persistence)**
   - Two-tuple (source IP, destination IP)
   - Three-tuple (source IP, destination IP, protocol)
   - Ensures requests from same client go to same backend
   - Useful for stateful applications

## Health Probes

Health probes determine which backend instances receive new connections.

### Probe Types

| Probe Type | Use Case | Configuration |
|------------|----------|---------------|
| **TCP** | Basic connectivity check | Port only |
| **HTTP** | Check HTTP endpoint | Port + path |
| **HTTPS** | Check HTTPS endpoint | Port + path |

### Probe Configuration

- **Interval**: Time between probes (default: 15 seconds)
- **Timeout**: Wait time for response (default: 31 seconds)
- **Unhealthy threshold**: Consecutive failures before marking unhealthy (default: 2)

### Best Practices

- Use HTTP/HTTPS probes over TCP when possible
- Probe a lightweight health endpoint
- Set appropriate intervals based on application needs
- Monitor probe metrics in Azure Monitor

## Common Use Cases

1. **Internal service-to-service communication**: Load balance traffic between microservices
2. **Database clusters**: Distribute connections across database replicas
3. **Virtual machine scale sets**: Balance traffic across auto-scaling VMs
4. **Kubernetes ingress**: Underlying load balancer for AKS services
5. **Legacy applications**: Layer 4 load balancing for non-HTTP protocols

## Architecture Patterns

### Pattern 1: High-Performance TCP Service
```
Internet → Load Balancer Standard → VM Scale Set
Cost: ~$20-50/month
```

### Pattern 2: Internal Microservices
```
VNet → Internal Load Balancer → Backend VMs/Containers
```

### Pattern 3: Multi-tier Application
```
Internet → Application Gateway (Layer 7)
  └─> Load Balancer (Layer 4) → Backend VMs
```

### Pattern 4: Hybrid Application
```
On-premises → VPN Gateway → Internal Load Balancer → Azure VMs
```

## Outbound Connectivity (Standard SKU)

Standard Load Balancer provides explicit outbound connectivity configuration:

### Outbound Rules

- Control outbound NAT behavior
- Configure port allocation
- Set idle timeout
- Multiple frontend IPs for scale

### SNAT Port Allocation

- Prevents SNAT port exhaustion
- Configurable ports per backend instance
- Supports up to 64,000 ports per frontend IP

### Best Practices

1. Use outbound rules for predictable outbound connectivity
2. Allocate sufficient SNAT ports for workload
3. Monitor SNAT port usage
4. Use NAT Gateway for high-scale outbound scenarios

## High Availability Configuration

### Zone-Redundant Frontend

- Frontend IP automatically zone-redundant
- Survives zone failures
- No additional configuration needed

### Zonal Backend Pools

- VMs can be in specific zones
- Load Balancer distributes across healthy zones
- Combine with VM scale sets for auto-scaling

### Cross-Region Load Balancer

- Global Load Balancer tier
- Routes traffic across Azure regions
- Built on top of Standard Load Balancer
- Provides region-level failover

## Best Practices

1. **Always use Standard SKU for production** - Basic has no SLA
2. **Configure health probes properly** - Use HTTP/HTTPS probes with appropriate intervals
3. **Use session affinity when needed** - For stateful applications requiring sticky sessions
4. **Monitor SNAT port usage** - Prevent port exhaustion in outbound scenarios
5. **Implement NSGs** - Required for Standard SKU, provides additional security
6. **Use zone redundancy** - Deploy across availability zones for maximum availability
7. **Right-size backend pool** - Add/remove instances based on load
8. **Configure diagnostic logging** - Enable logs for troubleshooting and monitoring
9. **Use HA ports for internal LB** - Simplifies configuration for all ports
10. **Plan outbound connectivity** - Configure outbound rules explicitly

## Cost Optimization Strategies

- ✅ Use Basic for non-production (free)
- ✅ Minimize number of rules
- ✅ Standard has low data processing costs
- ✅ Combine multiple services under one LB when possible
- ✅ Use NAT Gateway for high-volume outbound traffic (more cost-effective)
- ✅ Monitor and right-size backend pools

## When to Choose Load Balancer

Choose Azure Load Balancer when you need:
- ✅ Layer 4 (TCP/UDP) load balancing
- ✅ High performance and low latency
- ✅ Regional load balancing within a VNet
- ✅ Non-HTTP/HTTPS protocols
- ✅ Internal service-to-service traffic
- ✅ Cost-effective production load balancing

Don't choose Load Balancer when:
- ❌ You need Layer 7 features (use Application Gateway)
- ❌ You need global load balancing (use Front Door or Traffic Manager)
- ❌ You need WAF capabilities (use Application Gateway or Front Door)
- ❌ You need API management features (use APIM)
- ❌ You need content caching (use Front Door or CDN)

## Integration with Other Azure Services

### Azure Application Gateway
- Use Application Gateway in front for Layer 7 capabilities
- Load Balancer handles backend Layer 4 distribution
- Provides defense in depth

### Azure Virtual Machine Scale Sets
- Native integration with VMSS
- Auto-scaling based on load
- Automatic backend pool updates

### Azure Kubernetes Service (AKS)
- LoadBalancer service type creates Azure Load Balancer
- Integrates with cluster autoscaler
- Supports both public and internal services

### Azure Monitor
- Native integration for metrics and logs
- Configure alerts on key metrics
- Use Log Analytics for detailed analysis

## Monitoring and Diagnostics

### Key Metrics

- **Data path availability**: Frontend to backend connectivity
- **Health probe status**: Backend instance health
- **SNAT connection count**: Outbound connection tracking
- **Byte/packet count**: Traffic volume
- **SYN count**: New connection rate

### Diagnostic Logs

- Health probe logs
- Load balancer alert events
- Backend pool health changes

### Best Practices for Monitoring

1. Set up alerts for data path availability below 99%
2. Monitor health probe failures
3. Track SNAT port usage (prevent exhaustion)
4. Review logs for recurring issues
5. Use Azure Monitor workbooks for visualization

## Security Considerations

1. **Network Security Groups (NSGs)**: Required for Standard SKU, configure properly
2. **Private endpoints**: Use internal Load Balancer for private connectivity
3. **DDoS Protection**: Enable Azure DDoS Protection Standard for public IPs
4. **Service endpoints**: Secure backend communication to Azure services
5. **No public IP on VMs**: Use Load Balancer for inbound, NAT Gateway for outbound
6. **Regular security reviews**: Audit NSG rules and access patterns

## Exam Scenario: Multi-Tier Application Load Balancing

### Scenario

A company needs to deploy an application to Azure containing a **web front end** and an **application tier** with the following requirements:

**Internet to Web Front End Requirements:**
- URL-based routing
- Connection draining
- Prevention of SQL injection attacks

**Web Front End to Application Tier Requirements:**
- Port forwarding
- HTTPS health probes
- Availability set as the backend pool

### Solution

| Tier | Recommended Solution | Reason |
|------|---------------------|--------|
| **Internet → Web Front End** | Azure Application Gateway with WAF | Supports URL-based routing, connection draining, and WAF prevents SQL injection attacks |
| **Web Front End → Application Tier** | **Internal Azure Standard Load Balancer** | Supports port forwarding, HTTPS health probes, and availability set as backend pool |

### Why Internal Standard Load Balancer for Application Tier?

✅ **Port Forwarding**: Standard Load Balancer supports inbound NAT rules for port forwarding  
✅ **HTTPS Health Probes**: Standard SKU supports HTTP, HTTPS, and TCP health probes  
✅ **Availability Set Backend**: Supports availability sets as backend pool members  
✅ **Internal Traffic**: Designed for internal service-to-service communication within Azure  

### Why NOT Other Options?

| Option | Why Not Suitable |
|--------|-----------------|
| **Application Gateway with WAF** | Does not support port forwarding; designed for Layer 7 HTTP/HTTPS traffic, not general Layer 4 port forwarding; backend pools don't support availability sets directly |
| **Internal Basic Load Balancer** | Does not support HTTPS health probes (only HTTP and TCP); limited backend pool options |
| **Public Standard Load Balancer** | For internal application tier traffic, an internal load balancer is more appropriate; public LB exposes endpoints to internet |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Azure Application Gateway + WAF                        │
│  • URL-based routing                                                │
│  • Connection draining                                              │
│  • SQL injection prevention                                         │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Web Front End VMs                               │
│                   (in Availability Set)                             │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│           Internal Azure Standard Load Balancer                     │
│  • Port forwarding (Inbound NAT rules)                              │
│  • HTTPS health probes                                              │
│  • Availability set backend pool                                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Application Tier VMs                              │
│                   (in Availability Set)                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Takeaways

1. **Layer 7 vs Layer 4**: Use Application Gateway for HTTP/HTTPS traffic requiring URL routing, WAF, SSL termination. Use Load Balancer for Layer 4 TCP/UDP distribution.

2. **Internal vs Public**: For traffic between internal tiers (web to app), use **Internal** Load Balancer.

3. **Standard vs Basic**: Always use **Standard SKU** for production - it supports HTTPS health probes, has SLA, and offers more features.

4. **Port Forwarding**: Only Load Balancer supports port forwarding via inbound NAT rules - Application Gateway does not.

## Exam Scenario: VPN-Connected Application Load Balancing

### Scenario

You have an Azure subscription where:
- **Home users** access Azure resources via **point-to-site VPN**
- **Customer sites** access Azure resources via **site-to-site VPN**
- **App1** is a line-of-business application running on multiple Windows Server 2016 VMs
- You need to distribute connections to App1 evenly across all VMs

**Question**: What Azure services can you use to load balance traffic to App1?

### Solution Options

#### ✅ Option 1: Internal Load Balancer (Recommended)

**Why This Works:**
- All traffic comes through **VPN connections** (both point-to-site and site-to-site)
- VPN traffic enters the Azure virtual network as **internal network traffic**
- No public internet exposure needed
- Internal Load Balancer provides Layer 4 (TCP/UDP) distribution
- Lower cost than Application Gateway for simple load balancing

**Configuration:**
```bash
# Create internal load balancer
az network lb create \
  --resource-group myResourceGroup \
  --name myInternalLB \
  --sku Standard \
  --vnet-name myVNet \
  --subnet mySubnet \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEndPool

# Add VMs to backend pool
az network nic ip-config address-pool add \
  --address-pool myBackEndPool \
  --lb-name myInternalLB \
  --resource-group myResourceGroup \
  --nic-name myVM1NIC \
  --ip-config-name ipconfig1

# Create health probe
az network lb probe create \
  --resource-group myResourceGroup \
  --lb-name myInternalLB \
  --name myHealthProbe \
  --protocol tcp \
  --port 80

# Create load balancing rule
az network lb rule create \
  --resource-group myResourceGroup \
  --lb-name myInternalLB \
  --name myHTTPRule \
  --protocol tcp \
  --frontend-port 80 \
  --backend-port 80 \
  --frontend-ip-name myFrontEnd \
  --backend-pool-name myBackEndPool \
  --probe-name myHealthProbe
```

**Architecture:**
```
┌──────────────────┐         ┌──────────────────┐
│   Home Users     │         │  Customer Sites  │
│ (Remote workers) │         │  (Branch offices)│
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ Point-to-Site VPN          │ Site-to-Site VPN
         │                            │
         ▼                            ▼
┌────────────────────────────────────────────────┐
│          Azure VPN Gateway                     │
│  • Terminates VPN connections                  │
│  • Routes traffic to virtual network           │
└────────────────┬───────────────────────────────┘
                 │
                 │ Internal Traffic
                 │
                 ▼
┌────────────────────────────────────────────────┐
│     Internal Azure Load Balancer (Standard)    │
│  • Layer 4 TCP/UDP distribution                │
│  • Private IP address in VNet                  │
│  • Health probes to VMs                        │
└────────────────┬───────────────────────────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
      ┌────┐  ┌────┐  ┌────┐
      │VM1 │  │VM2 │  │VM3 │
      │App1│  │App1│  │App1│
      └────┘  └────┘  └────┘
   Windows Server 2016
```

#### ✅ Option 2: Azure Application Gateway

**Why This Works:**
- Application Gateway can have an **internal (private) frontend**
- Provides Layer 7 load balancing with additional features:
  - URL-based routing
  - Session affinity (cookie-based)
  - Web Application Firewall (WAF) capabilities
  - SSL termination
  - Connection draining
- Traffic from VPN connections can route to internal Application Gateway

**When to Choose Application Gateway Over Load Balancer:**
- You need **HTTP/HTTPS-specific features** (URL routing, WAF, SSL offload)
- Application requires **Layer 7 processing**
- You want **session affinity** based on cookies
- Budget allows for higher cost (~$179-323/month vs Load Balancer's ~$18/month)

**Configuration:**
```bash
# Create internal Application Gateway
az network application-gateway create \
  --name myAppGateway \
  --resource-group myResourceGroup \
  --location eastus \
  --vnet-name myVNet \
  --subnet myAppGwSubnet \
  --capacity 2 \
  --sku Standard_v2 \
  --http-settings-cookie-based-affinity Enabled \
  --frontend-port 80 \
  --http-settings-port 80 \
  --http-settings-protocol Http \
  --public-ip-address "" \
  --private-ip-address 10.0.1.10 \
  --servers 10.0.2.4 10.0.2.5 10.0.2.6
```

**Note:** Application Gateway requires a dedicated subnet (/24 recommended).

#### ❌ Option 3: Public Load Balancer (Not Suitable)

**Why This Doesn't Work:**
- Creates a **public IP address** exposed to the internet
- **Unnecessary** since all traffic already comes through VPN
- Increases security risk by exposing backend to internet
- VPN connections don't need public load balancer
- Higher cost with no benefit

**Why Wrong:**
> "The customer sites are connected through VPNs, so there's no need for a public load balancer; an internal load balancer is sufficient."

#### ❌ Option 4: Azure CDN (Not Applicable)

**Why This Doesn't Work:**
- Azure CDN is designed for **content caching and delivery**
- Does **NOT** provide application load balancing
- Cannot distribute traffic across backend VMs
- CDN is for static content, not line-of-business applications

#### ❌ Option 5: Traffic Manager (Not Suitable)

**Why This Doesn't Work:**
- Traffic Manager is a **DNS-based** global traffic distribution service
- Works at the **DNS level**, not as a load balancer
- Routes users to different **Azure regions or endpoints**
- Does NOT distribute traffic across VMs **within** a region
- Cannot provide load balancing for a single application tier

**What Traffic Manager Does:**
- Returns different IP addresses based on routing policy
- Used for multi-region failover or geo-routing
- No awareness of individual VM health within a backend pool

### Comparison Table

| Solution | Layer | Cost | VPN Compatible | Use Case |
|----------|-------|------|----------------|----------|
| **Internal Load Balancer** ✅ | Layer 4 (TCP/UDP) | ~$18/month | ✅ Yes | Simple traffic distribution for VPN-connected users |
| **Application Gateway** ✅ | Layer 7 (HTTP/HTTPS) | ~$179-430/month | ✅ Yes (internal mode) | Advanced HTTP features, WAF, SSL termination |
| **Public Load Balancer** ❌ | Layer 4 | ~$18/month | ⚠️ Unnecessary | Exposes public endpoint (not needed for VPN traffic) |
| **Azure CDN** ❌ | N/A | Varies | ❌ No | Content caching only, not load balancing |
| **Traffic Manager** ❌ | DNS | ~$0.54/million queries | ⚠️ Wrong scope | Multi-region DNS routing, not intra-region load balancing |

### Key Takeaways

1. **VPN Traffic is Internal Traffic**
   - Point-to-site and site-to-site VPNs bring external users into the Azure virtual network
   - Once in the VNet, traffic is treated as internal
   - Use **internal** load balancing solutions

2. **Layer 4 vs Layer 7**
   - **Internal Load Balancer**: Simple, cost-effective Layer 4 distribution
   - **Application Gateway**: Feature-rich Layer 7 with HTTP awareness

3. **Public vs Private**
   - **Never** use public-facing load balancers for VPN-only scenarios
   - Increases security risk unnecessarily

4. **Wrong Tool Categories**
   - **CDN**: Content delivery, not load balancing
   - **Traffic Manager**: DNS routing between regions, not VM-level load balancing

### Decision Flow

```
Do users connect via VPN?
         │
         ▼ Yes
    Internal solution needed
         │
         ▼
Need Layer 7 features? (URL routing, WAF, SSL offload)
         │
         ├─ No ──→ Internal Load Balancer (Recommended)
         │
         └─ Yes ──→ Application Gateway (Internal mode)
```

## References

- [Azure Load Balancer documentation](https://learn.microsoft.com/en-us/azure/load-balancer/)
- [Azure Load Balancer pricing](https://azure.microsoft.com/en-us/pricing/details/load-balancer/)
- [Load Balancer SKU comparison](https://learn.microsoft.com/en-us/azure/load-balancer/skus)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
