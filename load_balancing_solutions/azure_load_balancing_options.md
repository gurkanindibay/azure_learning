# Azure Proxy/API Management Solutions

This document summarizes the Azure services you can use as an API proxy or gateway layer. Each service can front-end your APIs, control traffic flows, and enforce policies, but they operate at different layers of the network stack and provide distinct capabilities.

## Table of Contents

- [Azure Front Door](#azure-front-door)
- [Azure API Management (APIM)](#azure-api-management-apim)
- [Azure Load Balancer](#azure-load-balancer)
- [Azure Application Gateway](#azure-application-gateway)
- [Decision Flow Diagram](#decision-flow-diagram)
- [Azure Traffic Manager](#azure-traffic-manager)
- [Azure CDN](#azure-cdn)
- [Comparison Table](#comparison-table)
- [Deployment Patterns](#deployment-patterns)
- [Additional Notes](#additional-notes)
- [Guidance from Microsoft Docs](#guidance-from-microsoft-docs)
- [Pricing Tiers and Cost Comparison](#pricing-tiers-and-cost-comparison)
  - [Azure Front Door Pricing](#azure-front-door-pricing)
    - [Front Door Standard](#front-door-standard)
    - [Front Door Premium](#front-door-premium)
  - [Azure Load Balancer Pricing](#azure-load-balancer-pricing)
    - [Basic Load Balancer](#basic-load-balancer)
    - [Standard Load Balancer](#standard-load-balancer)
  - [Azure Application Gateway Pricing](#azure-application-gateway-pricing)
    - [Application Gateway v2 Standard](#application-gateway-v2-standard)
    - [Application Gateway v2 WAF](#application-gateway-v2-waf)
  - [Azure Traffic Manager Pricing](#azure-traffic-manager-pricing)
  - [Azure CDN Pricing](#azure-cdn-pricing)
  - [Pricing Comparison Table](#pricing-comparison-table)
  - [Service Comparison by Cost and Use Case](#service-comparison-by-cost-and-use-case)
    - [Lowest Cost Options](#lowest-cost-options)
    - [Mid-Range Options](#mid-range-options)
    - [Enterprise Options](#enterprise-options)
    - [Cost Optimization Strategies](#cost-optimization-strategies)
      - [Front Door](#front-door)
      - [Load Balancer](#load-balancer)
      - [Application Gateway](#application-gateway)
      - [Traffic Manager](#traffic-manager)
    - [Decision Guide by Budget and Requirements](#decision-guide-by-budget-and-requirements)
  - [Common Architecture Patterns with Costs](#common-architecture-patterns-with-costs)
    - [Pattern 1: Basic Regional Web App](#pattern-1-basic-regional-web-app)
    - [Pattern 2: Secure Regional Web App](#pattern-2-secure-regional-web-app)
    - [Pattern 3: Global Web App with Security](#pattern-3-global-web-app-with-security)
    - [Pattern 4: Enterprise API Platform](#pattern-4-enterprise-api-platform)
    - [Pattern 5: Simple Multi-Region Failover](#pattern-5-simple-multi-region-failover)
    - [Pattern 6: High-Performance TCP Service](#pattern-6-high-performance-tcp-service)
  - [Key Takeaways](#key-takeaways)
- [References](#references)

## Azure Front Door
- **Layer/scope:** Global Layer 7 (HTTP/HTTPS) load balancer with CDN-like caching and Web Application Firewall (WAF) options.
- **Purpose:** Provides a global entry point for HTTP APIs with fast failover, SSL offloading, URL-based routing, caching, and DDoS resiliency. Useful when your consumers span multiple regions.
- **Key features:** 
  - Anycast-based global load balancing with health probes
  - URL path and header rewriting
  - Policies for rate limiting, IP restrictions, and WAF (managed rule sets)
  - Built-in caching and compression for acceleration
  - WebSocket and HTTP/2 support
- **Typical topology:** Front Door sits closest to the public Internet, forwarding traffic to backend pools (App Service, API Management, Virtual Machine Scale Sets, or a regional Front Door).
- **Why use it as a proxy:** Azure Front Door can protect and accelerate APIs while acting as a single global endpoint, especially for multi-region or multi-tenant workloads.

## Azure API Management (APIM)
- **Layer/scope:** Regional Layer 7 API gateway with a strong developer portal and policy engine.
- **Purpose:** Provides API façade, versioning, subscription keys, policy enforcement (transformations, caching, validation), and analytics.
- **Key features:** 
  - Developer portal with documentation, onboarding, and subscription management
  - Policy engine for rate limiting, JWT validation, CORS, XML/JSON transformation, etc.
  - Backend grouping into products with per-product quotas
  - Integration with Azure Monitor, Application Insights, and alerts
  - Supports SOAP pass-through, REST, GraphQL, and other protocols
- **Typical topology:** APIM is often deployed in front of multiple backends (Logic Apps, Functions, VMs) and can be placed behind Front Door or Azure Application Gateway for hybrid/perimeter scenarios.
- **Why use it as a proxy:** APIM is the go-to service when you need governance, developer experience, analytics, or complex policy-driven behavior for your APIs.

## Azure Load Balancer
- **Layer/scope:** Regional Layer 4 (TCP/UDP) load balancer.
- **Purpose:** Distributes traffic across VMs or VMs scale sets within a region, typically used for internal service-to-service traffic or for simple public TCP endpoints.
- **Key features:**
  - Public and internal (private) frontends
  - Basic or Standard SKU for different performance/SLAs
  - Health probes and session persistence (floating IP)
  - No native Layer 7 inspection or API policies
- **Typical topology:** Load Balancer balances raw TCP traffic for APIs running on VMs or Kubernetes clusters and is often paired with Azure Application Gateway or APIM if Layer 7 functionality is required.
- **Why use it as a proxy:** Use Azure Load Balancer when you need resilient regional TCP/UDP routing for API traffic that does not require HTTP-specific processing.

## Azure Application Gateway
- **Layer/scope:** Regional Layer 7 load balancer/web application firewall with TLS termination.
- **Purpose:** Acts as an HTTP/HTTPS proxy that can rewrite URLs, enforce WAF rules, and integrate with backend pools, making it suitable for container ingress or secure traffic routing in a single region.
- **Key features:**
  - URL-based routing, host-based routing, and multi-site hosting
  - Web Application Firewall with OWASP rules
  - TLS termination, end-to-end TLS, and certificate management
  - Autoscaling (Standard v2/WAF v2) and zone redundancy
- **Typical topology:** Often front-ends regional services (App Services, AKS, VMs) and can sit between Front Door and backend APIs to provide regional TLS/WAF controls.
- **Why use it as a proxy:** Use when you need Layer 7 security, path-based routing, and WAF capabilities without the governance features of APIM.

## Decision Flow Diagram
- The diagram below captures the routing choices for public and private endpoints, showing when to pick Load Balancer, Application Gateway, Front Door, or Traffic Manager combinations.

![Azure load balancing decision flow](assets/azure-load-balancing-decision-flow.png)

## Azure Traffic Manager
- **Layer/scope:** DNS-based global routing service (not a Layer 4/7 reverse proxy).
- **Purpose:** Ensures traffic reaches the healthiest regional endpoint by returning the best IP/DNS name based on priority, performance, or geographic routing methods.
- **Key features:**
  - Multiple routing methods (priority, performance, geolocation, weighted)
  - Endpoint health monitoring using HTTP, HTTPS, or TCP probes
  - No TLS termination or API policies — Traffic Manager simply answers DNS queries
  - Works with Azure or external endpoints (App Service, AKS, on-premises, Front Door, etc.)
- **Typical topology:** Traffic Manager stands in front of regional endpoints (which may include Front Door, APIM, or Load Balancer) and keeps DNS responses aligned with availability goals.
- **Why use it as a proxy:** It does not proxy traffic itself but provides DNS-level failover and routing to other proxy services; useful when you need simple global traffic controls without an extra hop.

## Azure CDN
- **Layer/scope:** Global content delivery network for caching and accelerating static content.
- **Purpose:** Caches static content at edge locations worldwide to reduce latency and offload origin servers. Also provides **HTTPS support for custom domains** on Azure Blob Storage static websites.
- **Key features:**
  - Global network of edge servers (Points of Presence - POPs)
  - Content caching with configurable TTL and cache rules
  - **HTTPS termination for custom domains** (critical for static websites in Blob Storage)
  - Custom domain support with free managed certificates
  - Compression and optimization
  - Geo-filtering and token authentication
  - Integration with Azure Blob Storage, App Service, and custom origins
- **Typical topology:** CDN sits between end users and origin servers (Blob Storage, App Service, custom servers), caching content at edge locations closest to users.
- **Why use it as a proxy:** Use Azure CDN when you need to:
  - **Enable HTTPS on custom domains for Azure Blob Storage static websites** (Blob Storage doesn't natively support HTTPS with custom domains)
  - Accelerate static content delivery globally
  - Reduce load on origin servers
  - Improve performance for geographically distributed users

### Azure CDN vs Azure Front Door

| Feature | Azure CDN | Azure Front Door |
|---------|-----------|------------------|
| **Primary Purpose** | Content caching/delivery | Global load balancing + WAF |
| **HTTPS Custom Domains** | ✅ Yes | ✅ Yes |
| **Static Website Hosting** | ✅ Recommended | ⚠️ Works but overkill |
| **WAF** | ❌ No (Standard) / ✅ Yes (Premium from Edgio) | ✅ Yes |
| **Dynamic Content** | ⚠️ Limited | ✅ Full support |
| **Load Balancing** | ❌ No | ✅ Yes |
| **Cost** | Lower | Higher |

**Key Insight for Exams:**
> Azure Blob Storage does **NOT** natively support HTTPS with custom domains for static websites. You must use **Azure CDN** (recommended) or Azure Front Door to enable HTTPS on custom domains.

### When to Use Azure CDN

| Scenario | Use CDN? | Alternative |
|----------|----------|-------------|
| Static website with custom domain + HTTPS | ✅ **Yes** | Front Door (overkill) |
| Serving images/videos globally | ✅ **Yes** | - |
| API acceleration | ⚠️ Maybe | Front Door preferred |
| WAF protection needed | ❌ No | Front Door or App Gateway |
| Dynamic web application | ❌ No | Front Door |

## Comparison Table
| Service | Layer | Global/Regional | Policy Engine | Developer Facing | Typical Role |
| --- | --- | --- | --- | --- | --- |
| Azure Front Door | Layer 7 | Global | Limited (WAF/routing) | No | Global entry point + CDN-like acceleration |
| Azure API Management | Layer 7 | Regional (can be fronted by Front Door) | Rich transformation/policy | Yes | API gateway + developer experience |
| Azure Load Balancer | Layer 4 | Regional | None | No | High-performance TCP/UDP distribution |
| Azure Traffic Manager | DNS/global | Global | None | No | DNS-based failover/routing (fronts proxies or endpoints) |
| Azure Application Gateway | Layer 7 | Regional | WAF/policy rules | No | TLS termination + WAF before APIs |
| **Azure CDN** | Layer 7 | Global | Cache rules only | No | Content caching + HTTPS for custom domains |

## Deployment Patterns
1. **Global API facade plus governance:** Use Azure Front Door for resilience and acceleration, with APIM behind it to enforce policies and provide the developer portal.
2. **Regional API gateway:** Deploy APIM in each region and optionally attach an internal Front Door to route telemetry-sensitive traffic.
3. **TCP-heavy services:** Use Azure Load Balancer for raw throughput and combine it with APIM or Application Gateway when HTTP-level controls become necessary.

## Additional Notes
- Traffic Manager can provide DNS-based routing, but it does not act as a proxy; it simply resolves to the best endpoint.
- Choose combinations that align with your security, performance, and management requirements.

## Guidance from Microsoft Docs
- The Azure load balancing overview categorizes services as global or regional and HTTP(S) or non-HTTP(S); use global services when you need a centralized control plane across regions and reserve regional services for intra-VNet traffic or zone-redundant scenarios.
- Layer-7 services (Front Door, Application Gateway) can offload TLS/WAF/path routing and are often combined with Load Balancer or Traffic Manager for multi-region coverage, while Load Balancer and Traffic Manager handle any protocol without Layer-7 inspection.
- Application Gateway can live inside a VNet and communicate with back ends over private IPs, which keeps your VMs off the public internet while still providing TLS termination, WAF policies, and TCP/TLS proxying.
- Both Front Door and Application Gateway offer WAF capabilities, but Front Door delivers global Anycast reach (requiring the `AzureFrontDoor.Backend` service tag) while Application Gateway inspects traffic regionally inside your VNet; choose the one that fits your latency, exposure, and integration needs.

## Pricing Tiers and Cost Comparison

### Azure Front Door Pricing

Azure Front Door offers two tiers with different capabilities and pricing models.

#### Front Door Standard

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

#### Front Door Premium

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

---

### Azure Load Balancer Pricing

Azure Load Balancer has two SKUs with different pricing models.

#### Basic Load Balancer

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

#### Standard Load Balancer

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

---

### Azure Application Gateway Pricing

Application Gateway v2 (Standard and WAF) with autoscaling capabilities.

#### Application Gateway v2 Standard

**Pricing Components**:
- **Fixed cost**: ~$0.246/hour (~$179/month) per gateway
- **Capacity units**: ~$0.008/hour per capacity unit (~$5.84/month)
- **Data processed**: ~$0.008 per GB

**Capacity Unit Calculation**:
- 1 capacity unit = max of:
  - 2,500 persistent connections
  - 2.22 Mbps throughput
  - 1 compute unit

**Features**:
- ✅ Autoscaling
- ✅ Zone redundancy
- ✅ Static VIP
- ✅ URL-based routing
- ✅ Multi-site hosting
- ✅ SSL offload/termination
- ✅ Session affinity
- ✅ Connection draining
- ✅ Custom health probes
- ❌ No WAF

**Best For**: Regional Layer 7 load balancing without WAF needs

**Cost Example (Standard)**:
```
Setup: Average 10 capacity units, 200 GB data processed
- Fixed: $179/month
- Capacity units: 10 × $5.84 = $58.40
- Data: 200 × $0.008 = $1.60
Total: ~$239/month
```

#### Application Gateway v2 WAF

**Pricing Components**:
- **Fixed cost**: ~$0.443/hour (~$323/month) per gateway
- **Capacity units**: ~$0.0144/hour per capacity unit (~$10.51/month)
- **Data processed**: ~$0.008 per GB

**Features**:
- ✅ All Standard v2 features
- ✅ Web Application Firewall (WAF)
- ✅ OWASP core rule sets
- ✅ Bot protection
- ✅ Custom WAF rules
- ✅ Geo-filtering
- ✅ Rate limiting
- ✅ DDoS protection

**Best For**: Regional applications requiring Layer 7 security and WAF

**Cost Example (WAF)**:
```
Setup: Average 10 capacity units, 200 GB data processed
- Fixed: $323/month
- Capacity units: 10 × $10.51 = $105.10
- Data: 200 × $0.008 = $1.60
Total: ~$430/month
```

---

### Azure Traffic Manager Pricing

**Pricing Components**:
- **Health checks**: ~$0.54/month per endpoint
- **DNS queries**: ~$0.54 per million queries (first million free)
- **Fast interval health checks**: ~$1.20/month per endpoint (optional)

**Features**:
- ✅ DNS-based routing
- ✅ Multiple routing methods
- ✅ Endpoint monitoring
- ✅ No data plane (DNS only)
- ✅ Global availability
- ❌ No TLS termination
- ❌ No request proxying

**Cost Example**:
```
Setup: 5 endpoints, 2 million DNS queries, standard health checks
- Health checks: 5 × $0.54 = $2.70/month
- DNS queries: (2M - 1M free) × $0.54 = $0.54
Total: ~$3.24/month
```

**Best For**: Low-cost DNS-based global traffic routing

---

### Azure CDN Pricing

Azure CDN offers multiple providers with different pricing models. The most common options are Microsoft CDN (Standard) and CDN from Edgio (formerly Verizon/Akamai).

#### Azure CDN from Microsoft (Standard)

**Pricing Components**:
- **No base fee**: Pay only for data transfer
- **Outbound data transfer** (Zone 1 - North America, Europe):
  - First 10 TB: ~$0.081/GB
  - 10-50 TB: ~$0.075/GB
  - 50-150 TB: ~$0.053/GB
  - 150+ TB: Volume pricing
- **HTTPS custom domain**: Free (managed certificates included)

**Features**:
- ✅ Global edge network
- ✅ Free managed SSL certificates for custom domains
- ✅ Compression (gzip, brotli)
- ✅ Geo-filtering
- ✅ Query string caching
- ✅ Core analytics
- ❌ No WAF
- ❌ No real-time analytics

**Best For**: Simple static content delivery, enabling HTTPS on Blob Storage static websites

#### Azure CDN from Edgio (Premium)

**Pricing Components**:
- **Outbound data transfer**: ~$0.17/GB (varies by region)
- **HTTP requests**: ~$0.0075 per 10,000 requests

**Features**:
- ✅ All Standard features
- ✅ Real-time analytics
- ✅ Advanced rules engine
- ✅ Token authentication
- ✅ Mobile device detection
- ✅ Customizable cache behaviors

**Best For**: Advanced caching scenarios requiring real-time analytics

**Cost Example (Microsoft Standard)**:
```
Setup: Static website with 100 GB/month data transfer, custom HTTPS domain
- Data transfer: 100 × $0.081 = $8.10/month
- HTTPS custom domain: Free
Total: ~$8.10/month
```

**Key Point for Static Websites:**
> Azure CDN is the **most cost-effective solution** for enabling HTTPS on custom domains for Azure Blob Storage static websites. It costs significantly less than Front Door (~$8/month vs ~$50+/month) for simple static content scenarios.

---

### Pricing Comparison Table

| Service | Tier | Monthly Base Cost | Data Processing | Per Request/Rule | WAF Included | SLA |
|---------|------|-------------------|-----------------|------------------|--------------|-----|
| **Front Door** | Standard | ~$35 | ~$0.087/GB | ~$0.95/100K | ❌ No | 99.99% |
| **Front Door** | Premium | ~$330 | ~$0.087/GB | ~$0.95/100K | ✅ Yes (+$32-92) | 99.99% |
| **Load Balancer** | Basic | Free | Free | Free | ❌ No | None |
| **Load Balancer** | Standard | ~$18/rule | ~$0.005/GB | ~$18/rule | ❌ No | 99.99% |
| **App Gateway** | Standard v2 | ~$179 | ~$0.008/GB | ~$6/CU | ❌ No | 99.95% |
| **App Gateway** | WAF v2 | ~$323 | ~$0.008/GB | ~$11/CU | ✅ Yes | 99.95% |
| **Traffic Manager** | N/A | $0 | N/A | ~$0.54/endpoint | ❌ No | 99.99% |
| **Azure CDN** | Microsoft | $0 | ~$0.081/GB | N/A | ❌ No | 99.9% |
| **Azure CDN** | Edgio Premium | $0 | ~$0.17/GB | ~$0.75/100K | ❌ No | 99.9% |

---

### Service Comparison by Cost and Use Case

#### Lowest Cost Options

1. **Traffic Manager** (~$3-10/month)
   - DNS-based routing only
   - No data plane costs
   - Best for simple failover

2. **Azure CDN** (~$5-20/month for typical usage)
   - No base fee, pay per GB
   - Best for static content and HTTPS custom domains
   - **Recommended for Blob Storage static websites**

3. **Load Balancer Basic** (Free)
   - Development/testing only
   - No SLA
   - TCP/UDP only

4. **Load Balancer Standard** (~$20-100/month)
   - Production TCP/UDP
   - High throughput, low cost per GB

#### Mid-Range Options

4. **Front Door Standard** (~$50-150/month)
   - Global HTTP load balancing
   - No WAF
   - CDN-like caching

5. **Application Gateway Standard v2** (~$240-400/month)
   - Regional Layer 7
   - SSL termination
   - URL routing

#### Enterprise Options

6. **Application Gateway WAF v2** (~$430-800/month)
   - Regional WAF
   - OWASP protection
   - Layer 7 security

7. **Front Door Premium** (~$400-1500/month)
   - Global WAF
   - Bot protection
   - Private Link support

---

### Cost Optimization Strategies

#### Front Door
- ✅ Use Standard tier if WAF not required
- ✅ Enable caching to reduce origin requests
- ✅ Consolidate multiple profiles where possible
- ✅ Monitor data transfer and optimize response sizes
- ⚠️ WAF rules add significant cost ($20-50/month per rule set)

#### Load Balancer
- ✅ Use Basic for non-production
- ✅ Minimize number of rules
- ✅ Standard has low data processing costs
- ✅ Combine multiple services under one LB when possible

#### Application Gateway
- ✅ Right-size capacity units (autoscale min/max)
- ✅ Use Standard v2 if WAF not needed (save ~$144/month)
- ✅ Monitor capacity unit consumption
- ✅ Enable connection draining to reduce waste
- ✅ Use aggressive health probes to scale down faster

#### Traffic Manager
- ✅ Already very low cost
- ✅ Avoid fast interval health checks unless needed
- ✅ Reduce number of endpoints where possible

---

### Decision Guide by Budget and Requirements

| Requirement | Recommended Service | Estimated Monthly Cost |
|-------------|---------------------|------------------------|
| **Static website + HTTPS custom domain** | Azure CDN | $5-20 |
| **Global routing, no WAF** | Front Door Standard | $50-150 |
| **Global routing + WAF** | Front Door Premium | $400-1500 |
| **Regional Layer 7, no WAF** | Application Gateway Standard v2 | $240-400 |
| **Regional Layer 7 + WAF** | Application Gateway WAF v2 | $430-800 |
| **Regional Layer 4 production** | Load Balancer Standard | $20-100 |
| **Regional Layer 4 dev/test** | Load Balancer Basic | Free |
| **DNS-based failover** | Traffic Manager | $3-10 |
| **Multi-region with API governance** | Front Door + API Management | $500-3500+ |

---

### Common Architecture Patterns with Costs

#### Pattern 1: Basic Regional Web App
```
Internet → Application Gateway Standard v2 → App Service
Cost: ~$240/month (gateway only)
```

#### Pattern 2: Secure Regional Web App
```
Internet → Application Gateway WAF v2 → App Service
Cost: ~$430/month (gateway only)
```

#### Pattern 3: Global Web App with Security
```
Internet → Front Door Premium → Regional App Gateways → Backends
Cost: ~$800/month (Front Door + 2 regional gateways)
```

#### Pattern 4: Enterprise API Platform
```
Internet → Front Door Premium → API Management Premium → Backends
Cost: ~$3,500/month (minimal scale)
```

#### Pattern 5: Simple Multi-Region Failover
```
Internet → Traffic Manager → Regional endpoints
Cost: ~$5/month
```

#### Pattern 6: High-Performance TCP Service
```
Internet → Load Balancer Standard → VM Scale Set
Cost: ~$20-50/month
```

#### Pattern 7: Static Website with Custom HTTPS Domain
```
Internet → Azure CDN → Azure Blob Storage (Static Website)
Cost: ~$5-20/month
```
**Note**: This is the recommended pattern for enabling HTTPS on custom domains for Azure Blob Storage static websites.

---

### Key Takeaways

✅ **Traffic Manager**: Cheapest option (~$3/month) but DNS-only, no proxying  
✅ **Azure CDN**: Best for static content + HTTPS custom domains (~$5-20/month)  
✅ **Load Balancer Basic**: Free but no SLA, dev/test only  
✅ **Load Balancer Standard**: Best price/performance for Layer 4 (~$20-100/month)  
✅ **Front Door Standard**: Global Layer 7 without WAF (~$50-150/month)  
✅ **Application Gateway Standard v2**: Regional Layer 7 without WAF (~$240/month)  
✅ **Application Gateway WAF v2**: Regional Layer 7 with WAF (~$430/month)  
✅ **Front Door Premium**: Global Layer 7 with WAF (~$400-1500/month)  

⚠️ **Important Factors**:
- WAF adds ~$50-100/month to any service
- Data transfer costs can exceed base costs at scale
- Capacity units (App Gateway) scale with traffic
- Multi-region deployments multiply costs
- Combining services increases complexity and cost
- **Azure Blob Storage static websites don't support HTTPS with custom domains natively — use Azure CDN**

## Exam Questions

### Question 1: Securing App Service Traffic with Application Gateway and WAF

**Scenario:**  
You are developing a web app named `mywebapp1`. `Mywebapp1` uses the address `myapp1.azurewebsites.net`. You protect `mywebapp1` by implementing an Azure Web Application Firewall (WAF). The traffic to `mywebapp1` is routed through an Azure Application Gateway instance that is also used by other web apps. 

**Question:**  
You want to secure all traffic to `mywebapp1` by using SSL. 

**Solution:**  
You open the Azure Application Gateway's HTTP setting and set the `Override backend path` option to `mywebapp1.azurewebsites.net`. You then enable the `Use for App service` option. 

Does this meet the goal?

---

#### ✅ Answer: Yes

**Explanation:**

Yes, this solution meets the goal. By configuring the Azure Application Gateway's HTTP settings with these specific options, you are properly securing the traffic to `mywebapp1`:

**What This Configuration Does:**

1. **Override Backend Path to `mywebapp1.azurewebsites.net`:**
   - This setting ensures that the Application Gateway correctly routes traffic to the specific App Service backend
   - It overrides the default backend path to point to the correct App Service endpoint

2. **Enable "Use for App Service" Option:**
   - This is a critical setting for App Service integration with Application Gateway
   - It ensures proper hostname preservation and SSL/TLS handling
   - Handles the hostname correctly when routing to App Service backends
   - Manages the required headers for App Service to accept the traffic

**How SSL is Secured:**

- Azure Application Gateway provides **SSL/TLS termination** at the gateway level
- Traffic between the client and Application Gateway is encrypted
- The gateway can re-encrypt traffic to the backend (end-to-end SSL) or use HTTP to the backend
- The **WAF** operates on the decrypted traffic at the gateway, inspecting for security threats
- The "Use for App service" option ensures SSL configuration works properly with App Service backends

**Key Points:**
- ✅ All traffic from clients to the gateway is secured with SSL
- ✅ The WAF can inspect traffic for threats (requires decrypted traffic)
- ✅ The backend communication to App Service is properly configured
- ✅ This meets the requirement of securing all traffic to `mywebapp1` by using SSL

**Best Practices:**
- Enable **HTTPS-only** on the App Service itself for end-to-end encryption
- Configure proper health probes to monitor backend availability
- Use Application Gateway's autoscaling features for high availability
- Implement custom WAF rules as needed for additional security

---

### Question 2: Authentication Certificate vs. Complete SSL Configuration

**Scenario:**  
You are developing a web app named `mywebapp1`. `Mywebapp1` uses the address `myapp1.azurewebsites.net`. You protect `mywebapp1` by implementing an Azure Web Application Firewall (WAF). The traffic to `mywebapp1` is routed through an Azure Application Gateway instance that is also used by other web apps.

**Question:**  
You want to secure all traffic to `mywebapp1` by using SSL.

**Solution:**  
You open the Azure Application Gateway's HTTP setting and set the `Override backend path` option to `mywebapp1.azurewebsites.net`. You then add an authentication certificate for `mywebapp1.azurewebsites.net`.

Does this meet the goal?

---

#### ❌ Answer: No

**Explanation:**

No, this solution does **NOT** meet the goal. While the steps described are part of the configuration, they are **insufficient** to fully secure all traffic to `mywebapp1` by using SSL.

**Why This Configuration Is Incomplete:**

1. **Override Backend Path Alone Is Not Enough:**
   - Setting the override backend path configures routing but doesn't establish SSL/TLS settings
   - It only tells the gateway where to send traffic, not how to secure it

2. **Authentication Certificate vs. Complete SSL Configuration:**
   - Adding an authentication certificate is just **one component** of SSL configuration
   - An authentication certificate is used for backend authentication in Application Gateway v1 (legacy)
   - In Application Gateway v2, you should use **trusted root certificates** instead
   - This alone doesn't enable SSL termination at the gateway or configure HTTPS listeners

**What's Missing for Complete SSL Configuration:**

| Missing Component | Purpose | Why It's Needed |
|-------------------|---------|-----------------|
| **HTTPS Listener** | Frontend SSL termination | Accept encrypted traffic from clients |
| **SSL Certificate Binding** | Client-facing encryption | Secure the connection between client and gateway |
| **Backend HTTPS Settings** | Backend encryption | Configure SSL/TLS for backend communication |
| **"Use for App Service" Option** | App Service integration | Ensure proper hostname handling for App Service |
| **HTTPS-Only on App Service** | End-to-end encryption | Force HTTPS on the backend web app |

**Complete SSL Configuration Steps:**

```bash
# 1. Create/upload SSL certificate to Application Gateway
az network application-gateway ssl-cert create \
  --gateway-name myAppGateway \
  --resource-group myResourceGroup \
  --name mySslCert \
  --cert-file certificate.pfx \
  --cert-password <password>

# 2. Create HTTPS listener with SSL certificate
az network application-gateway http-listener create \
  --gateway-name myAppGateway \
  --resource-group myResourceGroup \
  --name httpsListener \
  --frontend-port 443 \
  --ssl-cert mySslCert

# 3. Configure backend HTTP settings with SSL
az network application-gateway http-settings create \
  --gateway-name myAppGateway \
  --resource-group myResourceGroup \
  --name appServiceHttpsSettings \
  --port 443 \
  --protocol Https \
  --host-name-from-backend-pool false \
  --host-name myapp1.azurewebsites.net \
  --probe appServiceProbe

# 4. Enable HTTPS-only on the App Service
az webapp update \
  --name mywebapp1 \
  --resource-group myResourceGroup \
  --https-only true

# 5. Create routing rule to connect listener to backend
az network application-gateway rule create \
  --gateway-name myAppGateway \
  --resource-group myResourceGroup \
  --name httpsRule \
  --http-listener httpsListener \
  --address-pool myBackendPool \
  --http-settings appServiceHttpsSettings
```

**Key Differences from Question 1:**

| Aspect | Question 1 (✅ Correct) | Question 2 (❌ Incomplete) |
|--------|------------------------|---------------------------|
| **HTTP Settings** | Override backend path + **"Use for App Service"** | Override backend path only |
| **Certificate** | Not mentioned (handled by proper HTTPS config) | Authentication certificate added (insufficient) |
| **Completeness** | Complete SSL configuration implied | Missing HTTPS listener, SSL binding, backend HTTPS settings |

**What the Proposed Solution Actually Does:**
- ✅ Routes traffic to the correct App Service backend
- ❌ Does NOT configure HTTPS listener for client connections
- ❌ Does NOT bind SSL certificate for frontend encryption
- ❌ Does NOT configure backend HTTPS settings properly
- ❌ Does NOT enable "Use for App Service" option

**Correct Approach:**
To fully secure all traffic with SSL, you need:
1. **Frontend SSL:** HTTPS listener with SSL certificate binding (client → gateway)
2. **Backend SSL:** HTTPS backend settings with proper configuration (gateway → App Service)
3. **App Service Settings:** Enable HTTPS-only on the App Service itself
4. **Integration Options:** Enable "Use for App Service" for proper hostname handling
5. **Health Probes:** Configure HTTPS health probes to monitor backend health

**Note on Authentication Certificates:**
- **Application Gateway v1:** Uses authentication certificates for backend SSL
- **Application Gateway v2:** Uses trusted root certificates (recommended)
- Authentication certificates alone don't provide complete SSL configuration
- They're just one piece of the backend authentication puzzle

---

## References
- [Confusion between WAF with Application Gateway and FrontDoor when securing custom Web Apps running on Azure VM published to the internet](https://learn.microsoft.com/en-us/answers/questions/1655290/confusion-between-waf-with-application-gateway-and)
- [Azure load balancing overview (architecture guide)](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
- [Azure Front Door pricing](https://azure.microsoft.com/en-us/pricing/details/frontdoor/)
- [Azure Load Balancer pricing](https://azure.microsoft.com/en-us/pricing/details/load-balancer/)
- [Azure Application Gateway pricing](https://azure.microsoft.com/en-us/pricing/details/application-gateway/)
- [Azure Traffic Manager pricing](https://azure.microsoft.com/en-us/pricing/details/traffic-manager/)
- [Azure CDN pricing](https://azure.microsoft.com/en-us/pricing/details/cdn/)
- [Host a static website in Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website)
- [Use Azure CDN to access blobs with custom domains over HTTPS](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-https-custom-domain-cdn)


