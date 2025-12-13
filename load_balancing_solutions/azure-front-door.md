# Azure Front Door

## Overview

**Layer/scope:** Global Layer 7 (HTTP/HTTPS) load balancer with CDN-like caching and Web Application Firewall (WAF) options.

**Purpose:** Provides a global entry point for HTTP APIs with fast failover, SSL offloading, URL-based routing, caching, and DDoS resiliency. Useful when your consumers span multiple regions.

## Key Features

- Anycast-based global load balancing with health probes
- URL path and header rewriting
- Policies for rate limiting, IP restrictions, and WAF (managed rule sets)
- Built-in caching and compression for acceleration
- WebSocket and HTTP/2 support

## Typical Topology

Front Door sits closest to the public Internet, forwarding traffic to backend pools (App Service, API Management, Virtual Machine Scale Sets, or a regional Front Door).

## Why Use It as a Proxy

Azure Front Door can protect and accelerate APIs while acting as a single global endpoint, especially for multi-region or multi-tenant workloads.

## Pricing Tiers

### Front Door Standard

**Pricing Components**:
- **Base fee**: ~$35/month per profile
- **Outbound data transfer**: 
  - First 10 TB: ~$0.087/GB
  - 10-50 TB: ~$0.083/GB
  - 50+ TB: ~$0.070/GB
- **Requests**: ~$0.0095 per 10,000 requests
- **Rules engine**: Free (up to 100 rules)

**Features**:
- ✅ Global load balancing
- ✅ SSL offload
- ✅ Custom domains
- ✅ URL rewrite/redirect
- ✅ Caching
- ✅ Health probes
- ✅ Session affinity
- ❌ No WAF
- ❌ No Private Link
- ❌ No advanced routing

**Best For**: Basic global load balancing and CDN needs without security requirements

### Front Door Premium

**Pricing Components**:
- **Base fee**: ~$330/month per profile
- **Outbound data transfer**: Same as Standard
- **Requests**: ~$0.0095 per 10,000 requests
- **WAF policy**: ~$31.50/month per policy
- **Managed rules**: ~$20/month per rule set
- **Custom rules**: ~$5/month per rule (first 5 free)

**Features**:
- ✅ All Standard features
- ✅ Azure Web Application Firewall (WAF)
- ✅ Private Link to origin
- ✅ Bot protection
- ✅ Advanced routing
- ✅ Enhanced caching
- ✅ Microsoft-managed rule sets
- ✅ Custom WAF rules

**Best For**: Enterprise applications requiring global scale with security (WAF, DDoS protection)

**Cost Example (Premium)**:
```
Setup: 1M requests, 100 GB data transfer, 1 WAF policy with 2 managed rule sets
- Base: $330/month
- Requests: 100 × $0.0095 = $0.95
- Data transfer: 100 × $0.087 = $8.70
- WAF policy: $31.50
- Managed rules: 2 × $20 = $40
Total: ~$411/month
```

## Cost Optimization Strategies

- ✅ Use Standard tier if WAF not required
- ✅ Enable caching to reduce origin requests
- ✅ Consolidate multiple profiles where possible
- ✅ Monitor data transfer and optimize response sizes
- ⚠️ WAF rules add significant cost ($20-50/month per rule set)

## Common Use Cases

1. **Global API facade plus governance:** Use Azure Front Door for resilience and acceleration, with APIM behind it to enforce policies and provide the developer portal.

2. **Multi-region web applications:** Provide a single global entry point with automatic failover between regions.

3. **Content acceleration:** Cache static and dynamic content at edge locations worldwide.

## Architecture Patterns

### Pattern: Global Web App with Security
```
Internet → Front Door Premium → Regional App Gateways → Backends
Cost: ~$800/month (Front Door + 2 regional gateways)
```

### Pattern: Enterprise API Platform
```
Internet → Front Door Premium → API Management Premium → Backends
Cost: ~$3,500/month (minimal scale)
```

## Integration with Other Services

- **Azure API Management**: Place APIM behind Front Door for global API governance
- **Azure Application Gateway**: Use regional Application Gateways behind Front Door for additional Layer 7 controls
- **Azure App Service**: Direct integration with App Service backends
- **Azure Monitor**: Full integration for logging and diagnostics

## Best Practices

1. Enable caching to reduce load on backend services
2. Use health probes to ensure traffic only goes to healthy backends
3. Implement rate limiting and IP restrictions via WAF policies
4. Use Front Door Premium for production workloads requiring security
5. Configure custom domains with SSL certificates
6. Monitor metrics and logs via Azure Monitor

## When to Choose Front Door

Choose Azure Front Door when you need:
- ✅ Global Layer 7 load balancing across multiple regions
- ✅ CDN-like caching and content acceleration
- ✅ Web Application Firewall at the edge
- ✅ Fast failover between regions
- ✅ Single global endpoint for multi-region applications

Don't choose Front Door when:
- ❌ You only need regional load balancing (use Application Gateway)
- ❌ You need Layer 4 TCP/UDP balancing (use Load Balancer)
- ❌ Budget is very limited and you don't need global reach (use Traffic Manager)

## Real-World Scenario: Multi-Region App Service Deployment

### Scenario
Deploy an Azure App Service web app with multiple instances across multiple Azure regions requiring:
- Maintain access during regional outages
- Azure Web Application Firewall (WAF) support
- Cookie-based affinity (session persistence)
- URL routing capabilities

### Solution: Azure Front Door

**Why Azure Front Door is the correct choice:**

1. **Global High Availability**: As a global Layer 7 load balancer, Front Door provides automatic failover across multiple Azure regions, ensuring continued access even if an entire region experiences an outage.

2. **Integrated WAF Protection**: Front Door integrates with Azure Web Application Firewall (WAF) to provide centralized protection against web vulnerabilities and attacks (OWASP Top 10, bot protection, custom rules).

3. **Session Affinity**: Supports cookie-based affinity (session affinity), ensuring that requests from the same client are consistently routed to the same backend instance, which is critical for stateful applications.

4. **Advanced Routing**: Provides URL-based routing capabilities, enabling traffic distribution based on URL path patterns or host headers, allowing you to route different parts of your application to different backend pools.

### Why Other Services Don't Fit

**Azure Application Gateway** ❌
- While it supports WAF, URL routing, and session affinity
- It is a **regional service** and does not provide global failover or routing between multiple regions
- Cannot maintain access during regional outages

**Azure Load Balancer** ❌
- Operates at **Layer 4** (TCP/UDP) only
- No support for WAF, session affinity, or URL-based routing
- Designed for basic VM-level load balancing, not web application scenarios

**Azure Traffic Manager** ❌
- Provides **DNS-based** traffic distribution across regions
- No support for WAF, session affinity, or URL routing
- Only handles DNS resolution, not actual traffic routing
- Primarily used for DNS-level failover and latency-based routing

### Key Takeaway
For multi-region web applications requiring high availability, security (WAF), and advanced Layer 7 features (session affinity, URL routing), **Azure Front Door** is the only service that meets all requirements.

## References

- [Azure Front Door pricing](https://azure.microsoft.com/en-us/pricing/details/frontdoor/)
- [Azure Front Door documentation](https://learn.microsoft.com/en-us/azure/frontdoor/)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
