# Azure Proxy/API Management Solutions

This document summarizes the Azure services you can use as an API proxy or gateway layer. Each service can front-end your APIs, control traffic flows, and enforce policies, but they operate at different layers of the network stack and provide distinct capabilities.

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

## Comparison Table
| Service | Layer | Global/Regional | Policy Engine | Developer Facing | Typical Role |
| --- | --- | --- | --- | --- | --- |
| Azure Front Door | Layer 7 | Global | Limited (WAF/routing) | No | Global entry point + CDN-like acceleration |
| Azure API Management | Layer 7 | Regional (can be fronted by Front Door) | Rich transformation/policy | Yes | API gateway + developer experience |
| Azure Load Balancer | Layer 4 | Regional | None | No | High-performance TCP/UDP distribution |
| Azure Traffic Manager | DNS/global | Global | None | No | DNS-based failover/routing (fronts proxies or endpoints) |
| Azure Application Gateway | Layer 7 | Regional | WAF/policy rules | No | TLS termination + WAF before APIs |

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

## References
- [Confusion between WAF with Application Gateway and FrontDoor when securing custom Web Apps running on Azure VM published to the internet](https://learn.microsoft.com/en-us/answers/questions/1655290/confusion-between-waf-with-application-gateway-and)
- [Azure load balancing overview (architecture guide)](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)


