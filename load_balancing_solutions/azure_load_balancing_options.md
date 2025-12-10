# Azure Load Balancing and Traffic Management - Overview

This document provides an overview of Azure services for load balancing, traffic management, and content delivery. Each service operates at different layers and provides distinct capabilities for routing, securing, and optimizing traffic to your applications.

## 📚 Service Documentation

Detailed documentation for each service has been separated into dedicated files:

- **[Azure Front Door](./azure-front-door.md)** - Global Layer 7 load balancer with CDN and WAF capabilities
- **[Azure API Management (APIM)](./azure_api_management.md)** - API gateway with governance and developer portal
- **[Azure Load Balancer](./azure-load-balancer.md)** - Regional Layer 4 TCP/UDP load balancer
- **[Azure Application Gateway](./azure-application-gateway.md)** - Regional Layer 7 load balancer with WAF
- **[Azure Traffic Manager](./azure-traffic-manager.md)** - DNS-based global traffic routing
- **[Azure CDN](./azure-cdn.md)** - Global content delivery network for caching

## Quick Service Comparison


## Service Quick Reference

### Azure Front Door
**Global Layer 7 load balancer with CDN and WAF**
- Global entry point for multi-region applications
- CDN-like caching and content acceleration
- Web Application Firewall (WAF) capabilities
- [📖 Full Documentation](./azure-front-door.md)

### Azure API Management (APIM)
**Regional API gateway with governance**
- Developer portal and API documentation
- Policy engine for transformations and validation
- Subscription and versioning management
- [📖 Full Documentation](./azure_api_management.md)

### Azure Load Balancer
**Regional Layer 4 TCP/UDP load balancer**
- High-performance TCP/UDP distribution
- Internal and external load balancing
- Most cost-effective load balancing option
- [📖 Full Documentation](./azure-load-balancer.md)

### Azure Application Gateway
**Regional Layer 7 load balancer with WAF**
- URL and host-based routing
- SSL/TLS termination
- Web Application Firewall (WAF)
- [📖 Full Documentation](./azure-application-gateway.md)

### Azure Traffic Manager
**DNS-based global traffic routing**
- DNS-level failover and routing
- Multiple routing methods (priority, performance, geographic)
- Lowest cost global routing option
- [📖 Full Documentation](./azure-traffic-manager.md)

### Azure CDN
**Global content delivery network**
- Static content caching at edge locations
- **HTTPS for custom domains on Blob Storage static websites**
- Free managed SSL certificates
- [📖 Full Documentation](./azure-cdn.md)

## Decision Flow Diagram

The diagram below captures the routing choices for public and private endpoints, showing when to pick Load Balancer, Application Gateway, Front Door, or Traffic Manager combinations.

![Azure load balancing decision flow](assets/azure-load-balancing-decision-flow.png)

## Service Comparison Table

| Service | Layer | Scope | Primary Use Case | Cost (Typical) | Link |
| --- | --- | --- | --- | --- | --- |
| **Front Door** | Layer 7 | Global | Global HTTP load balancing with WAF | $50-1500/month | [Docs](./azure-front-door.md) |
| **API Management** | Layer 7 | Regional | API governance with developer portal | $50-2700/month | [Docs](./azure-api-management.md) |
| **Load Balancer** | Layer 4 | Regional | High-performance TCP/UDP distribution | Free-$100/month | [Docs](./azure-load-balancer.md) |
| **Application Gateway** | Layer 7 | Regional | Regional WAF and SSL termination | $240-800/month | [Docs](./azure-application-gateway.md) |
| **Traffic Manager** | DNS | Global | DNS-based failover and routing | $3-10/month | [Docs](./azure-traffic-manager.md) |
| **CDN** | Layer 7 | Global | Content caching and HTTPS for static sites | $5-20/month | [Docs](./azure-cdn.md) |

### Detailed Feature Comparison

| Feature | Front Door | APIM | Load Balancer | App Gateway | Traffic Manager | CDN |
|---------|-----------|------|---------------|-------------|-----------------|-----|
| **WAF** | ✅ Premium | ❌ | ❌ | ✅ WAF SKU | ❌ | ⚠️ Premium only |
| **Caching** | ✅ | ✅ Policies | ❌ | ❌ | ❌ | ✅ |
| **SSL Termination** | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **API Policies** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Dev Portal** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Health Probes** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Autoscaling** | ✅ | ⚠️ Varies | ⚠️ Standard | ✅ v2 | N/A | ✅ |

## Common Deployment Patterns

### Pattern 1: Static Website with Custom HTTPS Domain
```
Internet → Azure CDN → Azure Blob Storage (Static Website)
Cost: ~$5-20/month
```
**Use Case:** Enable HTTPS for static websites with custom domains

### Pattern 2: Basic Regional Web App
```
Internet → Application Gateway Standard v2 → App Service
Cost: ~$240/month
```
**Use Case:** Regional web application with SSL termination

### Pattern 3: Secure Regional Web App
```
Internet → Application Gateway WAF v2 → App Service
Cost: ~$430/month
```
**Use Case:** Regional web application with security (WAF)

### Pattern 4: Global Web App with Security
```
Internet → Front Door Premium → Regional App Gateways → Backends
Cost: ~$800/month
```
**Use Case:** Multi-region application with global WAF

### Pattern 5: Enterprise API Platform
```
Internet → Front Door Premium → API Management Premium → Backends
Cost: ~$3,500+/month
```
**Use Case:** Enterprise API governance with global distribution

### Pattern 6: Simple Multi-Region Failover
```
Internet → Traffic Manager → Regional endpoints
Cost: ~$5/month
```
**Use Case:** Low-cost DNS-based failover

### Pattern 7: High-Performance TCP Service
```
Internet → Load Balancer Standard → VM Scale Set
Cost: ~$20-50/month
```
**Use Case:** Layer 4 TCP/UDP load balancing

## Decision Guide

### When to Use Each Service

#### Choose **Azure CDN** when:
- ✅ Static website needs HTTPS with custom domain
- ✅ Global content caching required
- ✅ Budget is limited
- ❌ Don't need WAF or load balancing

#### Choose **Traffic Manager** when:
- ✅ Need DNS-based global routing
- ✅ Lowest cost global solution
- ✅ Integration with non-Azure endpoints
- ❌ Don't need traffic inspection or modification

#### Choose **Load Balancer** when:
- ✅ Need Layer 4 TCP/UDP balancing
- ✅ Regional high-performance distribution
- ✅ Cost-effective production solution
- ❌ Don't need Layer 7 features

#### Choose **Application Gateway** when:
- ✅ Regional Layer 7 load balancing
- ✅ WAF protection needed
- ✅ SSL/TLS termination required
- ❌ Don't need global distribution

#### Choose **Front Door** when:
- ✅ Global Layer 7 load balancing
- ✅ Multi-region applications
- ✅ WAF at global scale
- ❌ Don't need API governance

#### Choose **API Management** when:
- ✅ API governance required
- ✅ Developer portal needed
- ✅ Complex policy transformations
- ❌ Don't need only simple routing

## Key Insights for Exams

1. **Azure Blob Storage + HTTPS Custom Domain**
   > Azure Blob Storage does **NOT** natively support HTTPS with custom domains for static websites. You must use **Azure CDN** (recommended) or Azure Front Door.

2. **Traffic Manager is DNS-only**
   > Traffic Manager does not proxy traffic - it only handles DNS resolution. Use it for DNS-level routing to other services.

3. **Layer 4 vs Layer 7**
   > Load Balancer = Layer 4 (TCP/UDP), Application Gateway/Front Door = Layer 7 (HTTP/HTTPS)

4. **WAF Locations**
   > Application Gateway = Regional WAF, Front Door Premium = Global WAF

5. **Cost Optimization**
   > Traffic Manager (~$3-10/month) is cheapest for global routing, Load Balancer Standard (~$20-100/month) is most cost-effective for Layer 4

## Best Practices

1. **Combine services strategically** - Use Traffic Manager or Front Door for global routing, regional services for Layer 7 features
2. **Enable WAF for public endpoints** - Application Gateway or Front Door Premium for security
3. **Use CDN for static content** - Offload static content to CDN to reduce costs and improve performance
4. **Right-size for requirements** - Don't over-engineer; use simplest service that meets needs
5. **Monitor and optimize** - Track metrics, optimize cache rules, and adjust capacity
6. **Security in depth** - Combine multiple layers (WAF, NSG, private endpoints)
7. **Test failover scenarios** - Regularly test failover and disaster recovery
8. **Consider hybrid scenarios** - Many architectures benefit from combining multiple services

## Pricing Summary

Detailed pricing information has been moved to individual service documents. Here's a quick reference:

| Service | Tier | Typical Cost | Link |
|---------|------|--------------|------|
| **CDN** | Microsoft Standard | ~$5-20/month | [Details](./azure-cdn.md#pricing-tiers) |
| **Traffic Manager** | Standard | ~$3-10/month | [Details](./azure-traffic-manager.md#pricing) |
| **Load Balancer** | Basic | Free | [Details](./azure-load-balancer.md#pricing-tiers) |
| **Load Balancer** | Standard | ~$20-100/month | [Details](./azure-load-balancer.md#pricing-tiers) |
| **Front Door** | Standard | ~$50-150/month | [Details](./azure-front-door.md#pricing-tiers) |
| **App Gateway** | Standard v2 | ~$240-400/month | [Details](./azure-application-gateway.md#pricing-tiers) |
| **Front Door** | Premium | ~$400-1500/month | [Details](./azure-front-door.md#pricing-tiers) |
| **App Gateway** | WAF v2 | ~$430-800/month | [Details](./azure-application-gateway.md#pricing-tiers) |

### Cost Optimization Tips

✅ **Use Azure CDN** for static content + HTTPS custom domains (~$5-20/month)  
✅ **Use Traffic Manager** for low-cost DNS failover (~$3-10/month)  
✅ **Use Load Balancer Standard** for Layer 4 production workloads (~$20-100/month)  
✅ **Choose Standard tiers** if WAF not required (saves ~$100-300/month)  
✅ **Combine services strategically** - use right tool for right job  

For detailed pricing breakdowns, cost examples, and optimization strategies, see individual service documentation.

## Related Resources

### Service Documentation
- [Azure Front Door](./azure-front-door.md)
- [Azure API Management](./azure_api_management.md)
- [Azure Load Balancer](./azure-load-balancer.md)
- [Azure Application Gateway](./azure-application-gateway.md)
- [Azure Traffic Manager](./azure-traffic-manager.md)
- [Azure CDN](./azure-cdn.md)

### Microsoft Documentation
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
- [Choose a load balancing service](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)

### Architecture Decision Tree
![Azure load balancing decision flow](assets/azure-load-balancing-decision-flow.png)


