# Azure Load Balancer

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

## References

- [Azure Load Balancer documentation](https://learn.microsoft.com/en-us/azure/load-balancer/)
- [Azure Load Balancer pricing](https://azure.microsoft.com/en-us/pricing/details/load-balancer/)
- [Load Balancer SKU comparison](https://learn.microsoft.com/en-us/azure/load-balancer/skus)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
