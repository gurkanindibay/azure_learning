# Azure Application Gateway

## Overview

**Layer/scope:** Regional Layer 7 load balancer/web application firewall with TLS termination.

**Purpose:** Acts as an HTTP/HTTPS proxy that can rewrite URLs, enforce WAF rules, and integrate with backend pools, making it suitable for container ingress or secure traffic routing in a single region.

## Key Features

- URL-based routing, host-based routing, and multi-site hosting
- Web Application Firewall with OWASP rules
- TLS termination, end-to-end TLS, and certificate management
- Autoscaling (Standard v2/WAF v2) and zone redundancy
- Session affinity (cookie-based)
- Connection draining
- Custom error pages
- HTTP header rewriting
- WebSocket and HTTP/2 support

## Typical Topology

Often front-ends regional services (App Services, AKS, VMs) and can sit between Front Door and backend APIs to provide regional TLS/WAF controls.

## Why Use It as a Proxy

Use when you need Layer 7 security, path-based routing, and WAF capabilities without the governance features of APIM.

## Pricing Tiers

### Application Gateway v2 Standard

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

### Application Gateway v2 WAF

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

## Web Application Firewall (WAF)

### WAF Rule Sets

1. **OWASP Core Rule Set (CRS)**
   - CRS 3.2 (latest)
   - CRS 3.1
   - CRS 3.0
   - Protects against top 10 OWASP vulnerabilities

2. **Microsoft Bot Protection**
   - Known bad bots
   - Good bots (search engines)
   - Unknown bots

### WAF Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Detection** | Logs threats but doesn't block | Testing, tuning rules |
| **Prevention** | Logs and blocks threats | Production protection |

### Common WAF Rules

- SQL injection protection
- Cross-site scripting (XSS) prevention
- Local file inclusion protection
- Remote file inclusion protection
- Protocol enforcement
- Malicious user agent blocking
- Session fixation prevention

### Custom WAF Rules

Create custom rules based on:
- IP address/range
- Geographic location
- Request size
- String matching in headers/body
- Rate limiting per IP
- Custom threat intelligence

## Routing Capabilities

### URL Path-Based Routing

Route requests to different backend pools based on URL path:

```
www.contoso.com/images/* → Image servers
www.contoso.com/api/* → API servers
www.contoso.com/* → Web servers
```

### Multi-Site Hosting

Host multiple websites on single Application Gateway:

```
www.contoso.com → Backend pool 1
www.fabrikam.com → Backend pool 2
blog.contoso.com → Backend pool 3
```

### Host-Based Routing

Route based on hostname in request:
- Different SSL certificates per site
- Different backend pools per site
- Cost-effective multi-tenancy

### Redirection

- HTTP to HTTPS redirection
- External URL redirection
- Path-based redirection
- Query string preservation

## SSL/TLS Configuration

### SSL Termination

- Decrypt traffic at gateway
- Inspect with WAF
- Re-encrypt to backend (optional)
- Offload SSL processing from backends

### End-to-End SSL/TLS

- SSL from client to gateway
- SSL from gateway to backend
- Full encryption path
- Required for compliance scenarios

### Certificate Management

- Upload PFX certificates
- Use Azure Key Vault integration
- Automatic certificate renewal (Key Vault)
- Wildcard certificate support
- Multiple certificates per gateway

### Supported Protocols

- TLS 1.0, 1.1, 1.2, 1.3
- SSL 3.0 (deprecated, disable)
- Configure minimum TLS version
- Custom cipher suites

## Backend Pool Configuration

### Backend Types

- Azure Virtual Machines
- Virtual Machine Scale Sets
- Azure App Services
- Azure Container Instances
- IP addresses (on-premises or external)
- FQDN (Fully Qualified Domain Names)

### Backend Settings

- **Protocol**: HTTP or HTTPS
- **Port**: Backend port number
- **Cookie-based affinity**: Enable/disable
- **Connection draining**: Graceful removal
- **Request timeout**: Backend response timeout
- **Override backend path**: Custom path rewriting
- **Custom probes**: Health check configuration

### Health Probes

Configure custom health probes:
- **Protocol**: HTTP or HTTPS
- **Host**: Custom host header
- **Path**: Health check endpoint
- **Interval**: Time between probes
- **Timeout**: Response timeout
- **Unhealthy threshold**: Failures before marking unhealthy

## Autoscaling Configuration

### Capacity Units

Application Gateway v2 uses capacity units for scaling:
- Dynamically adjusts based on load
- Configure minimum and maximum instances
- Scales automatically within limits

### Scaling Considerations

- **Minimum capacity**: Baseline always available
- **Maximum capacity**: Cost control limit
- **Scale-out time**: ~6-7 minutes
- **Scale-in time**: Gradual to avoid disruption

### Best Practices

1. Set minimum capacity based on baseline load
2. Set maximum capacity based on peak load + buffer
3. Monitor capacity unit consumption
4. Enable autoscale for production workloads
5. Account for scaling time in capacity planning

## Common Use Cases

1. **Regional Web Application Front-end**: TLS termination and WAF for web applications
2. **Kubernetes Ingress Controller**: AKS ingress using Application Gateway
3. **Secure API Gateway**: WAF protection for regional APIs
4. **Multi-tenant Applications**: Host multiple sites with different SSL certificates
5. **Internal Load Balancing**: Private Application Gateway for internal services
6. **VPN-Connected Applications**: Distribute traffic from point-to-site and site-to-site VPN connections to backend VMs (alternative to Internal Load Balancer when Layer 7 features needed - see [Azure Load Balancer VPN scenario](azure-load-balancer.md#exam-scenario-vpn-connected-application-load-balancing))

## Architecture Patterns

### Pattern 1: Basic Regional Web App
```
Internet → Application Gateway Standard v2 → App Service
Cost: ~$240/month (gateway only)
```

### Pattern 2: Secure Regional Web App
```
Internet → Application Gateway WAF v2 → App Service
Cost: ~$430/month (gateway only)
```

### Pattern 3: AKS Ingress
```
Internet → Application Gateway WAF v2 → AKS Cluster
```

### Pattern 4: Multi-Region with Front Door
```
Internet → Front Door → Regional App Gateways → Backends
Cost: ~$800/month (Front Door + 2 regional gateways)
```

### Pattern 5: Internal VNet Services
```
VNet → Internal Application Gateway → Private Backends
```

## Integration with Other Azure Services

### Azure Kubernetes Service (AKS)

- **Application Gateway Ingress Controller (AGIC)**
- Native Kubernetes integration
- Automatic configuration via annotations
- Pod-level routing

### Azure App Service

- Native integration with backend pool
- App Service authentication support
- Custom domain support
- SSL certificate management

### Azure Key Vault

- Store SSL certificates securely
- Automatic certificate updates
- Managed identity authentication
- Centralized certificate management

### Azure Monitor

- Metrics and diagnostics
- Access logs
- Performance counters
- WAF logs
- Custom dashboards and alerts

## Best Practices

1. **Use v2 SKU for production** - v1 is legacy and lacks modern features
2. **Enable WAF for public-facing apps** - Protection against common vulnerabilities
3. **Configure autoscaling** - Right-size capacity units automatically
4. **Use Azure Key Vault for certificates** - Automatic renewal and secure storage
5. **Implement health probes** - Monitor backend health accurately
6. **Enable diagnostics** - Send logs to Log Analytics or Storage
7. **Configure NSGs properly** - Allow traffic from GatewayManager service tag
8. **Use zone redundancy** - Deploy across availability zones
9. **Implement connection draining** - Graceful backend updates
10. **Test WAF in detection mode first** - Avoid false positives before enabling prevention

## Cost Optimization Strategies

- ✅ Use Standard v2 if WAF not needed (save ~$144/month)
- ✅ Right-size capacity units (autoscale min/max)
- ✅ Monitor capacity unit consumption
- ✅ Enable connection draining to reduce waste
- ✅ Use aggressive health probes to scale down faster
- ✅ Consolidate multiple applications under one gateway
- ✅ Use internal Application Gateway for private workloads
- ✅ Stop/start dev/test environments when not in use

## When to Choose Application Gateway

Choose Azure Application Gateway when you need:
- ✅ Regional Layer 7 HTTP/HTTPS load balancing
- ✅ Web Application Firewall (WAF) protection
- ✅ SSL/TLS termination and offloading
- ✅ URL or host-based routing
- ✅ Multi-site hosting on single gateway
- ✅ Integration with Azure services (AKS, App Service)
- ✅ VNet-integrated private load balancing

Don't choose Application Gateway when:
- ❌ You need global load balancing (use Front Door)
- ❌ You need Layer 4 TCP/UDP balancing (use Load Balancer)
- ❌ You need API governance and developer portal (use APIM)
- ❌ You need content caching (use Front Door or CDN)
- ❌ Budget is very limited and you don't need Layer 7 features

## Monitoring and Diagnostics

### Key Metrics

- **Throughput**: Bytes per second
- **Unhealthy host count**: Failed health probes
- **Healthy host count**: Passing health probes
- **Total requests**: Request count
- **Failed requests**: HTTP errors
- **Backend response time**: Latency
- **Capacity units**: Current capacity consumption
- **Current connections**: Active connections

### Diagnostic Logs

- **Access logs**: All requests and responses
- **Performance logs**: Performance metrics
- **Firewall logs**: WAF detections and blocks
- **Backend health logs**: Health probe results

### Alerting

Set up alerts for:
- Unhealthy backend host count > 0
- Failed request percentage > threshold
- Capacity units near maximum
- WAF detection/prevention events
- Backend response time > threshold

## Security Considerations

1. **Always enable WAF for public endpoints** - Protection is critical
2. **Use HTTPS for backend connections** - End-to-end encryption
3. **Store certificates in Key Vault** - Secure certificate management
4. **Configure NSGs properly** - Restrict unnecessary access
5. **Enable diagnostic logging** - Security auditing and compliance
6. **Use managed identities** - Secure authentication to Azure services
7. **Implement custom WAF rules** - Additional protection for specific threats
8. **Regular rule reviews** - Keep WAF rules up-to-date
9. **Test in detection mode** - Validate WAF rules before blocking
10. **Monitor WAF logs** - Detect and respond to attacks

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

## References

- [Azure Application Gateway documentation](https://learn.microsoft.com/en-us/azure/application-gateway/)
- [Azure Application Gateway pricing](https://azure.microsoft.com/en-us/pricing/details/application-gateway/)
- [Application Gateway WAF](https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/ag-overview)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)
