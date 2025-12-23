# Azure Traffic Manager

## Overview

**Layer/scope:** DNS-based global routing service (not a Layer 4/7 reverse proxy).

**Purpose:** Ensures traffic reaches the healthiest regional endpoint by returning the best IP/DNS name based on priority, performance, or geographic routing methods.

## Key Features

- Multiple routing methods (priority, performance, geolocation, weighted, subnet, multivalue)
- Endpoint health monitoring using HTTP, HTTPS, or TCP probes
- No TLS termination or API policies — Traffic Manager simply answers DNS queries
- Works with Azure or external endpoints (App Service, AKS, on-premises, Front Door, etc.)
- DNS-level failover and load distribution
- Low latency DNS resolution
- Nested profiles for complex scenarios

## Typical Topology

Traffic Manager stands in front of regional endpoints (which may include Front Door, APIM, or Load Balancer) and keeps DNS responses aligned with availability goals.

## Why Use It as a Proxy

It does not proxy traffic itself but provides DNS-level failover and routing to other proxy services; useful when you need simple global traffic controls without an extra hop.

## How Traffic Manager Works

1. **Client makes DNS query** for your application domain
2. **Traffic Manager responds** with the IP address of the best endpoint based on:
   - Routing method configured
   - Endpoint health status
   - Geographic location of client (for some routing methods)
3. **Client connects directly** to the selected endpoint
4. **No traffic flows through Traffic Manager** - it only handles DNS resolution

**Important:** Traffic Manager is NOT a proxy. It only handles DNS routing, not actual traffic.

## Routing Methods

### 1. Priority (Failover)

Route traffic to a primary endpoint, failover to secondary if primary is unhealthy.

**Use Case:** Active-passive disaster recovery

**Configuration:**
- Endpoint 1: Priority 1 (primary)
- Endpoint 2: Priority 2 (secondary)
- Endpoint 3: Priority 3 (tertiary)

**Example:**
```
Primary region: East US (Priority 1)
Secondary region: West US (Priority 2)
→ All traffic goes to East US unless it's unhealthy
```

### 2. Weighted

Distribute traffic across endpoints based on assigned weights.

**Use Case:** 
- A/B testing
- Gradual migration
- Load distribution across regions

**Configuration:**
- Endpoint 1: Weight 70 (70% of traffic)
- Endpoint 2: Weight 20 (20% of traffic)
- Endpoint 3: Weight 10 (10% of traffic)

**Example:**
```
Region A: Weight 80 → 80% of users
Region B: Weight 20 → 20% of users (testing new features)
```

### 3. Performance

Route users to the endpoint with the lowest latency from their location.

**Use Case:** Global applications requiring best performance

**How it works:**
- Traffic Manager maintains Internet Latency Table
- Measures latency from client's location to each endpoint
- Returns endpoint with lowest latency

**Example:**
```
User in Europe → Routed to West Europe endpoint
User in Asia → Routed to Southeast Asia endpoint
User in US → Routed to East US endpoint
```

### 4. Geographic

Route traffic based on geographic location of DNS query origin.

**Use Case:**
- Data sovereignty compliance
- Content localization
- Regional marketing

**Configuration:**
- Endpoint 1: Europe, Middle East, Africa
- Endpoint 2: North America, South America
- Endpoint 3: Asia Pacific

**Example:**
```
User's DNS from Germany → Europe endpoint
User's DNS from Brazil → Americas endpoint
User's DNS from Japan → Asia Pacific endpoint
```

### 5. Multivalue

Return multiple healthy endpoints (up to 8) in DNS response.

**Use Case:** 
- Client-side load balancing
- Additional redundancy

**How it works:**
- Returns multiple healthy endpoint IPs
- Client can choose which to connect to
- Provides built-in failover at client level

### 6. Subnet

Route based on client IP address ranges.

**Use Case:**
- Route specific offices/networks to specific endpoints
- Differentiate internal vs external users
- Compliance requirements

**Configuration:**
```
IP Range 10.0.0.0/8 → Internal endpoint
IP Range 203.0.113.0/24 → Partner endpoint
All others → Public endpoint
```

## Endpoint Types

Traffic Manager supports multiple endpoint types:

### Azure Endpoints
- Azure App Service
- Azure Cloud Services
- Azure Public IP (VMs, Load Balancers)
- Azure App Service Slots

### External Endpoints
- Any public IP outside Azure
- On-premises services with public IPs
- Services in other clouds

### Nested Endpoints
- Other Traffic Manager profiles
- Complex routing scenarios
- Combine routing methods

## Health Monitoring

### Probe Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Protocol** | HTTP, HTTPS, or TCP | HTTPS |
| **Port** | Port to probe | 443 |
| **Path** | HTTP/HTTPS path | / |
| **Interval** | Time between probes | 30 seconds |
| **Timeout** | Time to wait for response | 10 seconds |
| **Tolerated failures** | Failures before marking unhealthy | 3 |

### Probe Frequency Options

| Option | Interval | Cost Impact | Use Case |
|--------|----------|-------------|----------|
| **Standard** | 30 seconds | ~$0.54/month per endpoint | Most scenarios |
| **Fast** | 10 seconds | ~$1.20/month per endpoint | Critical applications requiring rapid failover |

### Health States

- **Online**: Endpoint is healthy and receiving traffic
- **Degraded**: Endpoint failing probes but still configured
- **Disabled**: Endpoint manually disabled
- **Stopped**: Endpoint resource stopped (Azure endpoints only)
- **CheckingEndpoint**: Endpoint being evaluated

## Pricing

**Pricing Components**:
- **Health checks**: ~$0.54/month per endpoint
- **DNS queries**: ~$0.54 per million queries (first million free)
- **Fast interval health checks**: ~$1.20/month per endpoint (optional)

**Cost Example**:
```
Setup: 5 endpoints, 2 million DNS queries, standard health checks
- Health checks: 5 × $0.54 = $2.70/month
- DNS queries: (2M - 1M free) × $0.54 = $0.54
Total: ~$3.24/month
```

**Best For**: Low-cost DNS-based global traffic routing

## Common Use Cases

1. **Disaster Recovery**: Priority routing for active-passive failover
2. **Global Load Distribution**: Performance routing for lowest latency
3. **Regional Compliance**: Geographic routing for data sovereignty
4. **A/B Testing**: Weighted routing to test new features
5. **Multi-Region Applications**: Route to nearest healthy region
6. **Gradual Migration**: Weighted routing to slowly move traffic

## Architecture Patterns

### Pattern 1: Simple Multi-Region Failover
```
Internet → Traffic Manager (Priority) → Regional endpoints
Cost: ~$5/month
```

### Pattern 2: Performance-Based Routing
```
Internet → Traffic Manager (Performance) → 
  ├─> US East endpoint (users in Americas)
  ├─> West Europe endpoint (users in EMEA)
  └─> Southeast Asia endpoint (users in APAC)
```

### Pattern 3: Nested Profiles
```
Internet → Traffic Manager (Geographic) →
  ├─> Europe Traffic Manager (Performance) → EU endpoints
  ├─> Americas Traffic Manager (Performance) → US endpoints
  └─> Asia Traffic Manager (Performance) → Asia endpoints
```

### Pattern 4: A/B Testing
```
Internet → Traffic Manager (Weighted) →
  ├─> Production endpoint (Weight: 90)
  └─> Canary endpoint (Weight: 10)
```

### Pattern 5: Hybrid Scenario
```
Internet → Traffic Manager (Priority) →
  ├─> Azure Front Door (Priority 1)
  └─> On-premises datacenter (Priority 2)
```

## Integration with Other Azure Services

### Azure Front Door
- Use Traffic Manager in front of Front Door for additional routing logic
- Front Door handles WAF and Layer 7 routing
- Traffic Manager handles DNS-level distribution

### Azure Application Gateway
- Traffic Manager routes to different regional Application Gateways
- Each region has its own Application Gateway for Layer 7 features
- Provides both DNS and HTTP-level routing

### Azure Load Balancer
- Traffic Manager routes to public IPs of Load Balancers
- Load Balancer handles Layer 4 distribution within region
- Cost-effective regional distribution

### Azure App Service
- Native integration with App Service endpoints
- Automatic health detection from App Service status
- No additional configuration needed

## Best Practices

1. **Choose the right routing method** for your use case
2. **Configure health probes properly** - use HTTP/HTTPS over TCP when possible
3. **Set appropriate probe intervals** - standard for most cases, fast for critical apps
4. **Monitor endpoint health** via Azure Monitor
5. **Use nested profiles** for complex multi-region scenarios
6. **Test failover scenarios** regularly to ensure proper configuration
7. **Set appropriate TTL** - lower for faster failover, higher for less DNS query cost
8. **Document routing logic** - especially for complex nested configurations
9. **Use multiple endpoints** - don't rely on single endpoint for availability
10. **Monitor DNS query patterns** - understand where your users are coming from

## DNS TTL Considerations

### Time to Live (TTL) Impact

- **Higher TTL (e.g., 300 seconds)**
  - ✅ Fewer DNS queries (lower cost)
  - ✅ Less load on DNS servers
  - ❌ Slower failover (users cache old DNS)
  
- **Lower TTL (e.g., 30 seconds)**
  - ✅ Faster failover
  - ✅ More responsive to endpoint changes
  - ❌ More DNS queries (higher cost)
  - ❌ More load on DNS infrastructure

**Recommendation:** 
- Use 60-120 seconds for most scenarios
- Use 30 seconds for critical applications requiring fast failover
- Consider DNS query costs vs failover speed requirements

## Cost Optimization Strategies

- ✅ Already very low cost (~$3-10/month typically)
- ✅ Avoid fast interval health checks unless needed
- ✅ Reduce number of endpoints where possible
- ✅ Use standard probe interval for non-critical applications
- ✅ Monitor DNS query volume to understand costs
- ✅ Higher TTL reduces DNS query costs but slows failover
- ✅ Use nested profiles judiciously (adds endpoint costs)

## Monitoring and Diagnostics

### Key Metrics

- **Endpoint health status**: Current state of each endpoint
- **DNS queries**: Number of DNS queries received
- **Probe health**: Success/failure of health probes
- **Endpoint status by routing method**: How traffic is being distributed

### Azure Monitor Integration

- Configure alerts for endpoint health changes
- Track DNS query patterns over time
- Monitor probe success rates
- Log routing decisions for analysis

### Diagnostic Logs

- Endpoint health probe logs
- DNS query logs
- Profile configuration changes
- Routing method changes

## When to Choose Traffic Manager

Choose Azure Traffic Manager when you need:
- ✅ Low-cost DNS-based global routing
- ✅ Simple failover between regions
- ✅ Geographic or performance-based routing
- ✅ Integration with non-Azure endpoints
- ✅ No additional latency (DNS-only, not a proxy)
- ✅ Integration with existing load balancing services

Don't choose Traffic Manager when:
- ❌ You need Layer 7 features (use Front Door or Application Gateway)
- ❌ You need WAF capabilities (use Front Door or Application Gateway)
- ❌ You need content caching (use Front Door or CDN)
- ❌ You need sub-second failover (DNS caching prevents this)
- ❌ You need to inspect or modify traffic (it's DNS-only)

## Limitations and Considerations

1. **Not a proxy**: Cannot inspect, modify, or cache traffic
2. **DNS caching**: Client/ISP DNS caching can delay failover
3. **No Layer 7 features**: No SSL termination, URL routing, etc.
4. **No WAF**: Cannot protect against web attacks
5. **Internet-facing only**: Works with public IPs/DNS names only
6. **Failover delay**: Depends on TTL + probe interval + DNS propagation
7. **No traffic visibility**: Cannot see actual request/response data
8. **Client DNS dependency**: Routing based on DNS resolver location, not actual client

## Comparison with Other Services

| Feature | Traffic Manager | Front Door | Application Gateway |
|---------|----------------|------------|---------------------|
| **Layer** | DNS | Layer 7 | Layer 7 |
| **Scope** | Global | Global | Regional |
| **Proxies Traffic** | ❌ No | ✅ Yes | ✅ Yes |
| **WAF** | ❌ No | ✅ Yes | ✅ Yes |
| **SSL Termination** | ❌ No | ✅ Yes | ✅ Yes |
| **Caching** | ❌ No | ✅ Yes | ❌ No |
| **Cost** | ~$3-10/month | ~$50-1500/month | ~$240-800/month |
| **Failover Speed** | Minutes (DNS TTL) | Seconds | Seconds |
| **Health Probes** | ✅ Yes | ✅ Yes | ✅ Yes |

## Security Considerations

1. **Public DNS**: All Traffic Manager profiles are publicly resolvable
2. **Endpoint exposure**: Endpoints must have public IPs or DNS names
3. **No authentication**: DNS is unauthenticated by nature
4. **DDoS**: Traffic Manager has built-in DDoS protection
5. **Health probe security**: Secure health probe endpoints appropriately
6. **No data inspection**: Cannot filter or block malicious traffic
7. **DNS hijacking**: Use DNSSEC for additional DNS security
8. **Monitor query patterns**: Detect unusual DNS query patterns

## Advanced Scenarios

### Nested Profiles

Combine routing methods for complex scenarios:

```
Parent Profile: Geographic routing
  ├─> Europe: Nested profile with Performance routing
  │     ├─> West Europe endpoint
  │     └─> North Europe endpoint
  │
  ├─> Americas: Nested profile with Priority routing
  │     ├─> East US endpoint (Priority 1)
  │     └─> West US endpoint (Priority 2)
  │
  └─> Asia: Nested profile with Weighted routing
        ├─> Southeast Asia endpoint (Weight 70)
        └─> East Asia endpoint (Weight 30)
```

### Always On Pattern

Ensure at least one endpoint is always available:

1. Primary region with all traffic
2. Secondary region on standby
3. Traffic Manager with Priority routing
4. Fast health probes for rapid detection
5. Low TTL for quick DNS updates

### Blue-Green Deployment

Use weighted routing for zero-downtime deployments:

1. Blue (current): Weight 100
2. Green (new): Weight 0
3. Test green environment
4. Gradually shift: 90/10, 70/30, 50/50, 0/100
5. Rollback by reversing weights if issues detected

## References

- [Azure Traffic Manager documentation](https://learn.microsoft.com/en-us/azure/traffic-manager/)
- [Azure Traffic Manager pricing](https://azure.microsoft.com/en-us/pricing/details/traffic-manager/)
- [Traffic Manager routing methods](https://learn.microsoft.com/en-us/azure/traffic-manager/traffic-manager-routing-methods)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
