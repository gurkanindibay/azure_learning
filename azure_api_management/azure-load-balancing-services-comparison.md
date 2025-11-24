# Azure Load Balancing and Traffic Management Services - Feature Comparison

This document provides a comprehensive feature-based comparison of Azure's load balancing and traffic management services to help you choose the right service for your needs.

## Services Overview

- **Azure Load Balancer**: Layer 4 (TCP/UDP) load balancer for distributing network traffic
- **Azure Application Gateway**: Layer 7 (HTTP/HTTPS) web traffic load balancer with WAF capabilities
- **Azure API Management**: API gateway for managing, securing, and analyzing APIs
- **Azure Traffic Manager**: DNS-based global traffic load balancer
- **Azure Front Door**: Global Layer 7 load balancer with CDN and WAF capabilities

## Feature Comparison Table

| Feature | Load Balancer | Application Gateway | API Management | Traffic Manager | Front Door |
|---------|--------------|---------------------|----------------|-----------------|------------|
| **OSI Layer** | Layer 4 (Transport) | Layer 7 (Application) | Layer 7 (Application) | DNS-based | Layer 7 (Application) |
| **Protocol Support** | TCP, UDP | HTTP, HTTPS, WebSocket | HTTP, HTTPS, WebSocket, SOAP | All protocols | HTTP, HTTPS |
| **Global vs Regional** | Regional | Regional | Global/Regional | Global | Global |
| **Load Balancing Algorithms** | Hash-based, Source IP affinity | Round robin, Weighted, Cookie-based | Various policies | Priority, Weighted, Performance, Geographic | Priority, Weighted, Latency, Session affinity |
| **SSL/TLS Termination** | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **SSL/TLS Offloading** | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **End-to-End SSL** | ❌ No | ✅ Yes | ✅ Yes | N/A | ✅ Yes |
| **WAF (Web Application Firewall)** | ❌ No | ✅ Yes | ❌ No (Partner solutions) | ❌ No | ✅ Yes |
| **DDoS Protection** | Basic | Basic (Standard with DDoS) | Basic | Basic | ✅ Standard included |
| **URL-based Routing** | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Path-based Routing** | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Host-based Routing** | ❌ No | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Cookie-based Affinity** | ❌ No | ✅ Yes | ✅ Yes (via policies) | ❌ No | ✅ Yes |
| **Session Persistence** | ✅ Source IP affinity | ✅ Cookie-based | ✅ Policy-based | ❌ No | ✅ Session affinity |
| **Health Probes** | ✅ TCP, HTTP, HTTPS | ✅ HTTP, HTTPS, custom | ✅ Yes | ✅ HTTP, HTTPS, TCP | ✅ HTTP, HTTPS |
| **Auto-scaling** | ❌ No (zone redundant) | ✅ Yes | ✅ Yes | N/A | ✅ Yes |
| **CDN Integration** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Built-in |
| **Caching** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **API Gateway Features** | ❌ No | ❌ No | ✅ Yes (full) | ❌ No | ❌ Limited |
| **Rate Limiting/Throttling** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes (rules engine) |
| **API Versioning** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **API Transformations** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Developer Portal** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **OAuth/JWT Validation** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ Limited |
| **Request/Response Transformation** | ❌ No | ❌ No | ✅ Yes | ❌ No | ❌ Limited |
| **IP Whitelisting/Blacklisting** | ✅ Yes (NSG) | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Custom Domain Support** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Wildcard Certificate Support** | ✅ Yes | ✅ Yes | ✅ Yes | N/A | ✅ Yes |
| **HTTP to HTTPS Redirect** | ❌ No | ✅ Yes | ✅ Yes (via policies) | ❌ No | ✅ Yes |
| **URL Rewrite** | ❌ No | ✅ Yes | ✅ Yes (via policies) | ❌ No | ✅ Yes |
| **Compression** | ❌ No | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **WebSocket Support** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **HTTP/2 Support** | ❌ No | ✅ Yes | ✅ Yes | N/A | ✅ Yes |
| **Private Endpoints** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes (Premium) |
| **VNet Integration** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes (Private Link) |
| **Cross-Region Load Balancing** | ❌ No | ❌ No | ✅ Yes (multi-region) | ✅ Yes | ✅ Yes |
| **Geo-based Routing** | ❌ No | ❌ No | ✅ Yes (via policies) | ✅ Yes | ✅ Yes |
| **Failover Support** | ✅ Yes (within region) | ✅ Yes (within region) | ✅ Yes (multi-region) | ✅ Yes | ✅ Yes |
| **Traffic Splitting (A/B Testing)** | ❌ No | ✅ Limited | ✅ Yes | ✅ Yes (weighted) | ✅ Yes |
| **Built-in Analytics** | ✅ Basic metrics | ✅ Metrics + diagnostics | ✅ Comprehensive | ✅ Metrics | ✅ Comprehensive |
| **Azure Monitor Integration** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Logging** | ✅ Diagnostics | ✅ Access + diagnostics | ✅ Request + diagnostics | ✅ Query logs | ✅ Access + diagnostics |
| **Pricing Model** | Per rule + data processed | Per hour + data processed | Per API call + gateway units | Per DNS query + endpoints | Per hour + data processed |
| **SLA** | 99.99% | 99.95% | 99.95%-99.99% | 99.99% | 99.99% |

## Common Features Across Services

### Shared by All Services
- Azure Monitor integration
- Diagnostic logging capabilities
- Custom domain support
- Health monitoring/probes
- Azure RBAC for access control
- Integration with Azure services
- High availability support

### Shared by Layer 7 Services (App Gateway, API Management, Front Door)
- SSL/TLS termination and offloading
- URL-based routing
- Path-based routing
- Host-based routing
- HTTP/HTTPS protocol support
- HTTP to HTTPS redirect
- URL rewrite capabilities
- WebSocket support
- HTTP/2 support

### Shared by Global Services (API Management, Traffic Manager, Front Door)
- Cross-region load balancing
- Global traffic distribution
- Geographic routing capabilities
- Multi-region failover support

## Unique Features

### Azure Load Balancer (Unique)
- Layer 4 TCP/UDP load balancing
- Ultra-low latency
- Support for non-HTTP protocols
- HA Ports for internal load balancing
- Outbound rules for SNAT

### Application Gateway (Unique)
- Native WAF integration at Layer 7
- HTTP header and URL rewrites
- Connection draining
- Multiple site hosting (up to 100 sites)
- v2 SKU with autoscaling

### API Management (Unique)
- Full API lifecycle management
- Developer portal with API documentation
- API versioning and revisions
- Request/response transformations
- Policy-based API governance
- Mock API responses
- API products and subscriptions
- Built-in API analytics
- OAuth 2.0 and OpenID Connect support
- GraphQL API support
- Synthetic GraphQL from REST APIs

### Traffic Manager (Unique)
- Pure DNS-level routing
- Works with any internet-facing service
- Protocol agnostic
- Nested profiles for complex scenarios
- Real user measurements for performance routing

### Front Door (Unique)
- Integrated CDN capabilities
- Global anycast network
- URL-based routing at edge
- Custom WAF rules at edge
- Instant global failover
- Rules engine for advanced routing
- Private Link support for backends
- Native Microsoft network backbone

## Use Case Recommendations

| Scenario | Recommended Service | Reason |
|----------|-------------------|---------|
| Regional VM load balancing | **Load Balancer** | Layer 4, cost-effective, low latency |
| Regional web app with WAF | **Application Gateway** | Layer 7, WAF, regional optimization |
| API management and governance | **API Management** | Full API lifecycle, developer portal, policies |
| Global DNS-based routing | **Traffic Manager** | Protocol agnostic, DNS-based, cost-effective |
| Global web app with CDN | **Front Door** | Edge optimization, CDN, global WAF |
| Multi-region failover | **Traffic Manager** or **Front Door** | Global reach, automatic failover |
| Microservices API gateway | **API Management** | Service orchestration, transformations |
| Static content delivery | **Front Door** | Built-in CDN, edge caching |
| Legacy protocol load balancing | **Load Balancer** | Layer 4 supports all TCP/UDP |
| Complex API policies | **API Management** | Rich policy framework, transformations |

## Combining Services

These services can be combined for enhanced functionality:

1. **Traffic Manager + Application Gateway**: Global routing to regional Application Gateways
2. **Front Door + Application Gateway**: Global edge optimization with regional WAF
3. **API Management + Application Gateway**: API gateway with WAF protection
4. **Load Balancer + Application Gateway**: Layer 4 + Layer 7 in complex architectures
5. **Front Door + API Management**: Global CDN with full API management capabilities

## Decision Flowchart

```
Need load balancing?
├─ Yes
│  ├─ Layer 4 (TCP/UDP)?
│  │  └─ Load Balancer
│  │
│  └─ Layer 7 (HTTP/HTTPS)?
│     ├─ Need API management features?
│     │  └─ API Management
│     │
│     ├─ Global with CDN?
│     │  └─ Front Door
│     │
│     ├─ Global DNS-based?
│     │  └─ Traffic Manager
│     │
│     └─ Regional with WAF?
│        └─ Application Gateway
```

## Pricing Considerations

- **Load Balancer**: Most cost-effective for Layer 4
- **Application Gateway**: Mid-range, charged per instance hour + data processed
- **API Management**: Variable based on tier (Developer, Basic, Standard, Premium)
- **Traffic Manager**: Based on DNS queries and health checks
- **Front Door**: Premium pricing but includes CDN and global network

## Conclusion

Choose your service based on:
1. **Layer requirement**: Layer 4 vs Layer 7
2. **Scope**: Regional vs Global
3. **Features needed**: API management, WAF, CDN, etc.
4. **Budget**: Operational costs and scaling needs
5. **Complexity**: Single region vs multi-region scenarios
