# Azure API Manager

## Table of Contents
1. [Purpose](#purpose)
2. [Platform Overview](#platform-overview)
3. [Developer Portal Customization](#developer-portal-customization)
4. [Subscription Keys](#subscription-keys)
5. [Certificates](#certificates)
6. [Simple Usage Examples](#simple-usage-examples)
7. [Policy Sections](#policy-sections)
8. [Networking Configurations](#networking-configurations)
9. [API Versioning](#api-versioning)
10. [Operational Best Practices](#operational-best-practices)
11. [Practice Questions](#practice-questions)

## Purpose
Azure API Manager (API Management) is the turnkey service on Microsoft Azure that lets teams publish, secure, transform, maintain, and monitor APIs. It is designed to sit between consumers (internal applications, partners, or external developers) and backend services, applying consistent security, routing, and transformation policies without touching the target APIs.

## Platform Overview
- **Gateway tier**: Handles inbound requests, enforces policies, and routes calls to backend services. It supports multi-region deployment, virtual network integration, and caching.
- **Publisher portal**: Used by platform owners to configure APIs, products, policies, and developer onboarding.
- **Developer portal**: Self-service interface where consumers discover APIs, read documentation, and obtain credentials.
- **Products**: Group APIs into packages with quotas, rate limits, and visibility rules. Consumers subscribe to products to receive a subscription key.

## Developer Portal Customization

The developer portal in Azure API Management is a fully customizable website where API consumers can discover APIs, read documentation, test APIs interactively, and obtain credentials. When organizations need to customize the portal beyond basic styling, they have several options with varying levels of flexibility.

### Customization Approaches

| Approach | Customization Level | Use Case |
|----------|-------------------|----------|
| **Built-in widgets** | Limited | Basic branding changes, simple modifications |
| **Custom CSS** | Moderate | Styling changes without structural modifications |
| **Self-hosted portal** | Full | Complete customization including custom functionality |

### Built-in Portal Customization

The Azure portal provides built-in customization widgets that allow basic branding changes:
- Logo and favicon customization
- Color scheme modifications
- Basic layout adjustments
- Content editing through the visual editor

**Limitations**: Built-in widgets provide limited options and don't allow adding custom functionality or extensive modifications.

### Self-Hosted Developer Portal

For organizations requiring extensive customization, **self-hosting the developer portal** is the recommended approach. This involves:

1. **Downloading the source code**: The developer portal is open-source and available on GitHub
2. **Modifying the source code directly**: Full access to React-based components, styles, and functionality
3. **Adding custom functionality**: Integrate custom widgets, authentication flows, or business logic
4. **Complete branding control**: Modify every aspect of the portal's appearance and behavior
5. **Hosting on your infrastructure**: Deploy to Azure Static Web Apps, Azure App Service, or any web hosting platform

**Benefits of Self-Hosting**:
- ✅ Full customization capabilities
- ✅ Custom functionality and widgets
- ✅ Complete control over branding and features
- ✅ Integration with existing authentication systems
- ✅ Custom domain and hosting options

**Considerations**:
- Requires development expertise
- Responsible for updates and maintenance
- Need to manage hosting infrastructure

### What Doesn't Work for Full Customization

- **ARM templates**: Azure Resource Manager templates are for infrastructure deployment, not for applying custom CSS or portal customization
- **REST API theme configuration**: The API Management REST API doesn't provide theme configuration endpoints for developer portal customization
- **Built-in widgets alone**: Limited to basic branding and cannot add custom functionality

## Subscription Keys

Subscriptions are the primary mechanism API Management uses to authenticate developers calling your APIs.

- **Subscription key types**
	- `primary key` / `secondary key`: Each subscription has two keys for rotation. Include either key in requests via header (`Ocp-Apim-Subscription-Key`) or query string (`?subscription-key=`).
	- `named values`: Secure storage for connection strings or secrets used in policies.
- **Issuing keys**
	1. Create a product, add APIs, set visibility.
	2. Create a subscription (manually or via invitation email). Assign user/developer.
	3. Retrieve keys from the Azure portal or via the REST API/CLI.
- **Rotation patterns**
	1. Update backend to accept new key, apply to policy if needed.
	2. Regenerate secondary key, swap clients to use the new key.
	3. Regenerate primary key once clients switch, rotate again later.
- **Policy enforcement**
	- Use the `<validate-subscription>` policy to reject requests lacking a valid key.
	- Rate-limit the product to prevent abuse even when a valid key exists.

## Certificates

Certificates protect traffic and enable mutual TLS scenarios.

- **Gateway TLS (HTTPS)**
	- Azure provides gateway certificates automatically. Custom domains require uploading `.pfx` certificates with private keys via the portal or Azure CLI.
	- Renew certificates before expiration and update bindings in the `Custom domains` blade.
- **Client certificate validation**
	- Upload root certificates (PEM) into API Management and reference them in policies.
	- The `<check-header>` or `<certificate>` policy can enforce that the client certificate thumbprint matches approved values for mutual TLS.
- **Backend TLS (Client certs)**
	- When backend services require certificates, add them under `Certificates` → `Add certificate` (upload `.pfx`).
	- Reference them inside `<send-request>` or `<set-backend-service>` policies using `client-certificate` attribute.

## Simple Usage Examples

### CURL request with subscription key
```bash
curl -X GET \
	"https://contoso.azure-api.net/orders?subscription-key=PRIMARY_KEY_VALUE" \
	-H "Accept: application/json"
```

### Requests using header
```bash
curl -X POST \
	https://contoso.azure-api.net/customers \
	-H "Ocp-Apim-Subscription-Key: SECONDARY_KEY_VALUE" \
	-H "Content-Type: application/json" \
	-d '{"name": "Acme"}'
```

### PowerShell example
```powershell
$headers = @{"Ocp-Apim-Subscription-Key" = "PRIMARY_KEY_VALUE"}
Invoke-RestMethod -Uri "https://contoso.azure-api.net/products" -Headers $headers
```

### Applying policies
```xml
<policies>
	<inbound>
		<check-header name="Ocp-Apim-Subscription-Key" exists-action="override" />
		<validate-subscription />
	</inbound>
	<backend>
		<set-backend-service base-url="https://orders.contoso.net" />
	</backend>
</policies>
```

### OAuth 2.0 authentication with JWT validation
```xml
<policies>
	<inbound>
		<validate-jwt header-name="Authorization" failed-validation-httpcode="401" failed-validation-error-message="Unauthorized">
			<openid-config url="https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration" />
			<audiences>
				<audience>api://your-api-client-id</audience>
			</audiences>
			<issuers>
				<issuer>https://sts.windows.net/{tenant-id}/</issuer>
			</issuers>
		</validate-jwt>
		<rate-limit-by-key calls="100" renewal-period="60" counter-key="@(context.Request.IpAddress)" />
	</inbound>
</policies>
```

### Mock responses for testing
```xml
<policies>
	<inbound>
		<base />
		<mock-response status-code="200" content-type="application/json" />
	</inbound>
	<backend>
		<base />
	</backend>
	<outbound>
		<base />
		<set-body>@{
			return new JObject(
				new JProperty("id", 123),
				new JProperty("name", "Sample Course"),
				new JProperty("credits", 3)
			).ToString();
		}</set-body>
	</outbound>
</policies>
```

## Policy Sections

Azure API Management policies are defined within four distinct sections, each executing at a specific point in the request/response lifecycle. Understanding when each section executes is critical for implementing the correct logic.

### Policy Section Overview

| Section | Execution Timing | Purpose | Use Cases |
|---------|-----------------|---------|------------|
| **inbound** | Before backend call | Process incoming requests | Authentication, validation, rate limiting, request transformation |
| **backend** | Configures backend call | Configure how to call the backend | Set backend URL, client certificates, forwarding rules |
| **outbound** | After successful backend response | Process successful responses | Response transformation, caching, header manipulation |
| **on-error** | When an error occurs | Handle errors during processing | Custom error responses, logging, returning cached data on failure |

### Section Details

#### 1. Inbound Section

The **inbound** section processes incoming requests **before** they reach the backend service. Policies here execute in order and can:
- Validate authentication tokens (JWT validation)
- Check subscription keys
- Apply rate limiting and quotas
- Transform request headers and body
- Cache lookup for cached responses

**Key Point**: Inbound policies cannot handle backend errors because they execute before the backend call is made.

#### 2. Backend Section

The **backend** section configures how API Management calls the backend service. Policies here:
- Set the backend service URL
- Configure client certificates for mutual TLS
- Forward requests to specific backends

**Key Point**: The backend section executes **before** the actual backend call is made to configure it. It does not receive or process backend responses or errors.

#### 3. Outbound Section

The **outbound** section processes **successful** responses from the backend. Policies here:
- Transform response headers and body
- Store responses in cache
- Add custom headers to responses
- Format or filter response data

**Key Point**: The outbound section only executes when the backend returns a **successful** response. If the backend returns an error (like 503 Service Unavailable), the outbound section is **skipped**.

#### 4. On-Error Section

The **on-error** section is specifically designed to handle **error conditions** during request processing. This section executes when:
- The backend returns an error response (4xx, 5xx status codes)
- A policy in any section throws an exception
- Any error occurs during the request lifecycle

**Key Point**: The on-error section is the **only** place where you can handle backend failures and implement custom error responses.

### Error Handling Example

Here's an example of handling backend 503 errors with cached data fallback:

```xml
<policies>
	<inbound>
		<base />
		<cache-lookup vary-by-developer="false" vary-by-developer-groups="false" />
	</inbound>
	<backend>
		<base />
	</backend>
	<outbound>
		<base />
		<cache-store duration="3600" />
	</outbound>
	<on-error>
		<choose>
			<when condition="@(context.Response.StatusCode == 503)">
				<!-- Return cached data when backend is unavailable -->
				<cache-lookup-value key="fallback-data" variable-name="cachedResponse" />
				<choose>
					<when condition="@(context.Variables.ContainsKey("cachedResponse"))">
						<return-response>
							<set-status code="200" reason="OK (Cached)" />
							<set-header name="X-Cache-Status" exists-action="override">
								<value>fallback</value>
							</set-header>
							<set-body>@((string)context.Variables["cachedResponse"])</set-body>
						</return-response>
					</when>
					<otherwise>
						<return-response>
							<set-status code="503" reason="Service Temporarily Unavailable" />
							<set-body>{"error": "Service temporarily unavailable. Please try again later."}</set-body>
						</return-response>
					</otherwise>
				</choose>
			</when>
		</choose>
	</on-error>
</policies>
```

### Execution Flow Diagram

```
Client Request
      ↓
┌─────────────────┐
│    INBOUND      │  ← Process incoming request
└────────┬────────┘
         ↓
┌─────────────────┐
│    BACKEND      │  ← Configure backend call
└────────┬────────┘
         ↓
   Backend Service
         ↓
    ┌─────────┐
    │ Success │───→ ┌─────────────────┐
    └────┬────┘     │    OUTBOUND     │  ← Process successful response
         │          └────────┬────────┘
    ┌────┴────┐              ↓
    │  Error  │         Client Response
    └────┬────┘
         ↓
┌─────────────────┐
│    ON-ERROR     │  ← Handle errors
└────────┬────────┘
         ↓
   Client Response
```

### Key Takeaways

- **Error handling belongs in `on-error`**: When you need to handle backend failures (like 503 errors), always use the `on-error` section.
- **`outbound` skips on errors**: The outbound section does not execute when the backend returns an error.
- **`inbound` and `backend` cannot handle backend errors**: These sections execute before the backend response is received.
- **`on-error` is your safety net**: Use it for logging errors, returning custom error messages, or providing fallback responses.

## Azure API Management Pricing Tiers

Azure API Management offers multiple pricing tiers to suit different use cases, from development/testing to enterprise production workloads.

### Pricing Tiers Overview

| Tier | Monthly Cost* | SLA | Max Gateway Units | Calls/sec per Unit | Use Case |
|------|--------------|-----|-------------------|-------------------|----------|
| **Consumption** | Pay-per-use | None | Auto-scale | Variable | Serverless, event-driven |
| **Developer** | ~$50 | None | 1 (non-scalable) | 1,000 | Dev/test, non-production |
| **Basic** | ~$160 | 99.95% | 2 | 1,000 | Small production |
| **Standard** | ~$660 | 99.95% | 4 | 2,500 | Medium production |
| **Premium** | ~$2,800 | 99.99% | 12 per region | 4,000 | Enterprise, multi-region |
| **Isolated** | ~$3,000+ | 99.99% | Dedicated | Custom | Regulatory compliance |

*Prices are approximate and vary by region. Check Azure pricing calculator for accurate costs.

### Tier-by-Tier Breakdown

#### 1. Consumption Tier (Serverless)

**Pricing Model**: Pay-per-execution
- **Base**: ~$3.50 per million executions
- **No fixed monthly cost**
- **First 1 million executions/month**: Free
- **Billed per execution** (API call)

**Features**:
- ✅ Auto-scaling (0 to unlimited)
- ✅ Serverless architecture
- ✅ Built-in caching (external only)
- ✅ OAuth 2.0, OpenID Connect
- ✅ Developer portal
- ❌ No SLA
- ❌ No VNet integration
- ❌ No self-hosted gateway
- ❌ No multi-region deployment
- ❌ No custom domains with CA certificates

**Limits**:
- Max request size: 1 MB
- Max response size: 1 MB
- Max timeout: 230 seconds
- Cached responses: External cache only

**Best For**:
- Event-driven architectures
- Unpredictable/variable traffic
- Development and testing
- Low-volume APIs
- Cost-sensitive scenarios

**Example Cost**:
```
5 million API calls/month:
- First 1M: Free
- Remaining 4M: 4 × $3.50 = $14.00
Total: ~$14/month
```

#### 2. Developer Tier

**Pricing**: ~$50/month (flat rate)

**Features**:
- ✅ All APIs, products, policies
- ✅ Developer portal
- ✅ Built-in cache
- ✅ OAuth 2.0, client certificates
- ✅ Analytics and monitoring
- ❌ No SLA (not for production)
- ❌ No scaling (1 unit only)
- ❌ No VNet integration
- ❌ No multi-region
- ❌ No availability zones

**Limits**:
- 1 gateway unit (non-scalable)
- Up to 1,000 calls/sec
- Max 10 APIs

**Best For**:
- Development and testing
- Proof of concepts
- Learning and training
- Non-production environments

**NOT Recommended For**: Production workloads (no SLA)

#### 3. Basic Tier

**Pricing**: ~$160/month per unit

**Features**:
- ✅ 99.95% SLA
- ✅ Up to 2 gateway units
- ✅ Custom domains
- ✅ Built-in cache
- ✅ Developer portal
- ✅ OAuth 2.0, JWT validation
- ❌ No VNet integration
- ❌ No multi-region
- ❌ No self-hosted gateway

**Limits**:
- Max 2 gateway units
- 1,000 calls/sec per unit
- Max 5 APIs per service

**Best For**:
- Small production workloads
- Single-region deployments
- Simple API management needs
- Budget-conscious projects

**Example Cost**:
```
1 unit: ~$160/month
2 units (scaled): ~$320/month
```

#### 4. Standard Tier

**Pricing**: ~$660/month per unit

**Features**:
- ✅ 99.95% SLA
- ✅ Up to 4 gateway units
- ✅ Custom domains
- ✅ Built-in cache (better performance)
- ✅ VNet integration (external mode)
- ✅ Self-hosted gateway
- ✅ OAuth 2.0, JWT, client certs
- ✅ Azure AD integration
- ❌ No multi-region deployment
- ❌ No internal VNet mode
- ❌ No availability zones

**Limits**:
- Max 4 gateway units
- 2,500 calls/sec per unit
- Unlimited APIs

**Best For**:
- Medium production workloads
- VNet connectivity required
- Hybrid cloud scenarios (self-hosted gateway)
- Growing businesses

**Example Cost**:
```
1 unit: ~$660/month
2 units (scaled): ~$1,320/month
4 units (max scale): ~$2,640/month
```

#### 5. Premium Tier

**Pricing**: ~$2,800/month per unit per region

**Features**:
- ✅ 99.99% SLA (multi-region)
- ✅ Up to 12 gateway units per region
- ✅ Multi-region deployment
- ✅ Availability zones
- ✅ VNet integration (internal & external)
- ✅ Self-hosted gateway (unlimited)
- ✅ Advanced caching
- ✅ Redis cache integration
- ✅ Backup and restore
- ✅ Virtual network injection
- ✅ Full feature set

**Limits**:
- Max 12 units per region
- 4,000 calls/sec per unit
- Unlimited APIs
- Unlimited regions (additional cost per region)

**Best For**:
- Enterprise production workloads
- Mission-critical APIs
- Global applications (multi-region)
- High availability requirements
- Advanced security needs
- Regulatory compliance

**Example Cost**:
```
Single region, 1 unit: ~$2,800/month
Single region, 4 units: ~$11,200/month
Two regions, 2 units each: ~$11,200/month
```

#### 6. Isolated Tier (Premium v2)

**Pricing**: ~$3,000+/month (custom pricing)

**Features**:
- ✅ 99.99% SLA
- ✅ Dedicated compute and network isolation
- ✅ All Premium features
- ✅ Compute isolation for regulatory compliance
- ✅ Network isolation
- ✅ Dedicated infrastructure
- ✅ Private Link support
- ✅ Enhanced security

**Best For**:
- Highly regulated industries (finance, healthcare)
- Data sovereignty requirements
- Enhanced isolation needs
- Compliance requirements (PCI-DSS, HIPAA)

### Feature Comparison Matrix

| Feature | Consumption | Developer | Basic | Standard | Premium | Isolated |
|---------|-------------|-----------|-------|----------|---------|----------|
| **SLA** | ❌ None | ❌ None | ✅ 99.95% | ✅ 99.95% | ✅ 99.99% | ✅ 99.99% |
| **Custom domains** | ❌ Limited | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **VNet integration** | ❌ No | ❌ No | ❌ No | ✅ External | ✅ Internal/External | ✅ Internal/External |
| **Multi-region** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Self-hosted gateway** | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Unlimited | ✅ Unlimited |
| **Availability zones** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Built-in cache** | ❌ External only | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Advanced | ✅ Advanced |
| **Developer portal** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Max scale units** | Auto | 1 | 2 | 4 | 12/region | Custom |
| **Calls/sec per unit** | Variable | 1,000 | 1,000 | 2,500 | 4,000 | Custom |
| **Backup/restore** | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Compute isolation** | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes |

### Scaling and Capacity

#### Calls per Second (Estimated)

| Tier | Per Unit | Max Capacity |
|------|----------|-------------|
| Consumption | Variable | Auto-scales |
| Developer | 1,000 | 1,000 (no scaling) |
| Basic | 1,000 | 2,000 (2 units max) |
| Standard | 2,500 | 10,000 (4 units max) |
| Premium | 4,000 | 48,000 (12 units/region) |
| Isolated | Custom | Custom |

**Note**: Actual throughput depends on:
- Request/response size
- Backend latency
- Policy complexity
- Caching configuration

### Multi-Region Deployment (Premium Only)

**Pricing**: Per region, per unit

**Example**: 3 regions with 2 units each
```
Cost: 3 regions × 2 units × $2,800 = $16,800/month
```

**Benefits**:
- Lower latency (serve from nearest region)
- Higher availability (failover between regions)
- Disaster recovery
- Data residency compliance

### Additional Costs

Beyond the base tier pricing:

| Component | Cost |
|-----------|------|
| **Outbound data transfer** | ~$0.087/GB (first 5 GB free) |
| **Self-hosted gateway** | Included (Standard/Premium), runs on your infrastructure |
| **Azure Monitor/Application Insights** | Separate (data ingestion ~$2.30/GB) |
| **Virtual Network** | Included (VNet itself may have costs) |
| **Custom domains (SSL)** | Certificate costs (free with Let's Encrypt) |
| **Developer portal hosting** | Included |
| **Redis cache** | Separate Azure Cache for Redis costs |

### Choosing the Right Tier

#### Choose **Consumption** if:
- ✅ Traffic is unpredictable or intermittent
- ✅ Cost is the primary concern
- ✅ No SLA required
- ✅ Serverless architecture preferred
- ✅ Event-driven workloads

#### Choose **Developer** if:
- ✅ Development and testing only
- ✅ Learning API Management
- ✅ POC or demo scenarios
- ❌ Never for production

#### Choose **Basic** if:
- ✅ Small production workload
- ✅ Limited budget
- ✅ Single region sufficient
- ✅ No VNet integration needed
- ✅ Up to 2,000 calls/sec sufficient

#### Choose **Standard** if:
- ✅ Medium production workload
- ✅ VNet connectivity required
- ✅ Self-hosted gateway needed
- ✅ Up to 10,000 calls/sec sufficient
- ✅ Single region sufficient

#### Choose **Premium** if:
- ✅ Enterprise/mission-critical workload
- ✅ Multi-region deployment required
- ✅ High availability (99.99% SLA)
- ✅ Advanced caching needed
- ✅ Availability zones required
- ✅ Backup/restore capabilities needed
- ✅ High throughput (48,000+ calls/sec)

#### Choose **Isolated** if:
- ✅ Regulatory compliance (PCI-DSS, HIPAA)
- ✅ Compute isolation required
- ✅ Data sovereignty requirements
- ✅ Enhanced security mandates

### Cost Optimization Tips

1. **Start with lower tiers**: Begin with Basic/Standard, upgrade as needed
2. **Use Consumption for variable traffic**: Pay only for what you use
3. **Right-size capacity**: Monitor usage, scale units appropriately
4. **Leverage caching**: Reduce backend calls and costs
5. **Self-hosted gateway**: Offload traffic to on-premises or edge locations
6. **Monitor closely**: Use Azure Monitor to track usage and optimize
7. **Multi-region carefully**: Only deploy to regions where needed
8. **Developer tier for non-prod**: Use for dev/test, not production
9. **Policy optimization**: Efficient policies reduce processing time
10. **Throttling/quotas**: Prevent abuse and unexpected costs

### Migration Between Tiers

**Possible Migrations**:
- ✅ Developer → Basic/Standard/Premium
- ✅ Basic → Standard/Premium
- ✅ Standard → Premium
- ✅ Consumption → Any dedicated tier
- ❌ Cannot downgrade from Premium to Standard/Basic
- ❌ Cannot migrate to Consumption from dedicated tiers

**Note**: Some migrations require creating a new instance and migrating configuration.

### Real-World Cost Examples

#### Example 1: Startup API (Consumption)
```
Scenario: 2 million API calls/month
- First 1M: Free
- Next 1M: $3.50
Total: $3.50/month
```

#### Example 2: SMB Internal APIs (Basic)
```
Scenario: 5 APIs, 500 calls/sec average
- 1 Basic unit: $160/month
Total: $160/month
```

#### Example 3: Mid-Size Company (Standard)
```
Scenario: 20 APIs, 5,000 calls/sec peak, VNet integration
- 2 Standard units: 2 × $660 = $1,320/month
- Outbound transfer (100 GB): $8.70
Total: ~$1,329/month
```

#### Example 4: Enterprise Global API (Premium)
```
Scenario: Multi-region (3 regions), 4 units per region
- Region 1: 4 × $2,800 = $11,200
- Region 2: 4 × $2,800 = $11,200
- Region 3: 4 × $2,800 = $11,200
- Outbound transfer (1 TB): $87
Total: ~$33,687/month
```

### Key Takeaways

✅ **Consumption**: Best for serverless, variable traffic, cost-sensitive scenarios  
✅ **Developer**: Only for non-production environments  
✅ **Basic**: Entry-level production with SLA  
✅ **Standard**: Mid-tier with VNet and self-hosted gateway  
✅ **Premium**: Enterprise features, multi-region, high availability  
✅ **Isolated**: Regulatory compliance and enhanced isolation  

⚠️ **Important**: Always use Azure Pricing Calculator for accurate region-specific pricing  
⚠️ **SLA**: Only Basic and above have SLAs (99.95%+)  
⚠️ **Multi-region**: Premium tier only  
⚠️ **VNet**: Standard tier and above  

## Networking Configurations

Azure API Management offers multiple networking options to control how clients connect to your API gateway and how the gateway connects to backend services.

### Networking Options Overview

| Configuration | Inbound Access | Outbound Access | Tier Requirements | Use Case |
|--------------|----------------|-----------------|-------------------|----------|
| **No VNet (Default)** | Public | Public | All tiers | Simple public APIs |
| **Private Endpoint** | Private (via PE) | Public | Developer, Basic, Standard, Premium | Private client access with public backends |
| **External VNet Mode** | Public | VNet-routed | Standard, Premium | Public APIs with private backends |
| **Internal VNet Mode** | VNet only | VNet only | Premium | Fully private API infrastructure |

### Private Endpoints

Private Endpoints provide a secure, private network path for inbound client connections to API Management.

**Key Characteristics**:
- Creates a private IP address within your VNet for API Management
- Clients connect via the private IP instead of the public endpoint
- **Inbound traffic**: Flows through the Private Endpoint (private network)
- **Outbound traffic**: API Management can still reach public backend APIs over the internet
- Supported in Developer, Basic, Standard, and Premium tiers
- ❌ **Not supported** in Consumption tier

**When to Use**:
- Client applications must access API Management through private network only
- Backend APIs remain publicly accessible
- Need to restrict inbound access while maintaining outbound connectivity

### External Virtual Network Mode

External VNet mode deploys API Management into a VNet subnet while keeping the gateway endpoint publicly accessible.

**Key Characteristics**:
- API Management gateway remains publicly accessible from the internet
- Outbound connections can reach resources within the VNet and peered networks
- Requires Standard or Premium tier
- Gateway, developer portal, and management endpoint are public

**When to Use**:
- Need to access private backend services within a VNet
- Public API access is acceptable or required
- Hybrid scenarios with both public and private backends

### Internal Virtual Network Mode

Internal VNet mode makes API Management accessible only from within the virtual network.

**Key Characteristics**:
- **Both inbound and outbound** traffic is restricted to the VNet
- Gateway endpoint is only accessible from within the VNet or connected networks
- Requires Premium tier
- All components (gateway, developer portal, management) are private
- ❌ **Cannot** access public backend APIs without additional configuration (e.g., NAT gateway, firewall)

**When to Use**:
- Fully private API infrastructure requirements
- All backends are within the same VNet or connected networks
- Strict network isolation requirements

### Consumption Tier Limitations

The Consumption tier has significant networking limitations:
- ❌ No Private Endpoint support
- ❌ No virtual network integration
- ❌ No IP restrictions beyond built-in policies
- Only suitable for publicly accessible, serverless API scenarios

### Choosing the Right Configuration

```
Do clients need private-only access?
├── No → Use default (no VNet) or External VNet mode
└── Yes → Do backends need to be public?
    ├── Yes → Use Private Endpoint
    └── No → Use Internal VNet mode (Premium tier required)
```

## API Versioning

API versioning in Azure API Management allows you to manage multiple versions of an API that can coexist simultaneously, enabling clients to choose which version they want to use.

### Version Sets

A **version set** is a logical grouping of related API versions. It provides a unified way to manage multiple versions of an API while maintaining a consistent identity. Version sets allow you to:
- Group related API versions together under a single logical API
- Define how clients specify which version they want to use
- Maintain different versions simultaneously for backward compatibility
- Gradually migrate clients from older to newer versions

### Versioning Schemes

API Management supports three versioning schemes:

| Scheme | Description | Example |
|--------|-------------|----------|
| **Path** | Version is specified in the URL path | `/api/v1/orders` or `/api/v2/orders` |
| **Header** | Version is specified using a custom HTTP header | `api-version: v1` |
| **Query** | Version is specified as a query string parameter | `/api/orders?api-version=v1` |

### Header-Based Versioning

Header-based versioning is ideal when you want to:
- Keep URLs clean and consistent across versions
- Allow clients to specify versions without changing the request path
- Implement versioning in a way that doesn't affect URL routing or caching based on path

**Configuration steps for header-based versioning**:
1. Create a version set with the **Header** versioning scheme
2. Specify the header name (e.g., `api-version`)
3. Add API versions to the version set
4. Clients include the header in requests to specify the desired version

**Example request with header-based versioning**:
```bash
curl -X GET \
    "https://contoso.azure-api.net/orders" \
    -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
    -H "api-version: v2"
```

### Versioning vs. Revisions

It's important to understand the difference between versions and revisions:

| Aspect | Versions | Revisions |
|--------|----------|----------|
| **Purpose** | Breaking changes, major updates | Non-breaking changes, testing |
| **Client visibility** | Clients choose which version to use | Current revision is active; others are for testing |
| **Coexistence** | Multiple versions can be active simultaneously | Only one revision is current at a time |
| **Use case** | v1 and v2 APIs with different contracts | Testing changes before making them live |

### Best Practices for API Versioning

- **Use version sets for breaking changes**: When introducing changes that would break existing clients, create a new version within a version set rather than modifying the existing API.
- **Choose the appropriate versioning scheme**: Select header, path, or query versioning based on your client requirements and API design standards.
- **Document version differences**: Clearly communicate what changes exist between versions in your developer portal.
- **Maintain backward compatibility**: Support older versions for a reasonable deprecation period to give clients time to migrate.
- **Avoid using revisions for coexisting versions**: Revisions are designed for non-breaking changes and testing, not for maintaining multiple client-selectable versions.

## Operational Best Practices
- **Monitor usage**: Configure Application Insights or the built-in analytics to track latency, throttled requests, and subscription failures.
- **Automate deployment**: Use Azure Resource Manager (ARM) templates or Bicep to publish APIs/policies and manage environments consistently.
- **Secure secrets**: Store sensitive values in named values and mark them as secrets, then reference them securely inside policies with `{{secret-name}}`.
- **Design APIs for resiliency**: Use caching policies (`<cache-lookup>`/`<cache-store>`), rate limits, and retries to shield backends from spikes.
- **Document clearly**: Keep the developer portal updated with descriptions, sample payloads, and contact details to reduce support load. Use the portal's built-in documentation features rather than embedding documentation in service code.
- **Pin self-hosted gateway versions**: For production deployments, always use full version tags (e.g., `2.9.0`) following the `{major}.{minor}.{patch}` convention instead of `latest`, `v3`, or preview tags to ensure stable and predictable behavior.
- **Implement OAuth 2.0 authentication**: Use the `validate-jwt` policy to authenticate incoming requests with OAuth 2.0 tokens, ensuring only authorized users can access your APIs.
- **Enforce usage quotas**: Apply `rate-limit-by-key` policies to prevent abuse and ensure fair usage among API consumers by limiting the number of calls within specified time periods.
- **Manually define API operations**: Create blank APIs and manually define only the necessary operations rather than automatically exposing all backend services. This provides precise control over what is exposed, enhances security by following the principle of least privilege, and enables mock responses for testing without invoking backends.
- **Import existing APIs efficiently**: When exposing existing services, use the API import functionality to quickly onboard APIs by importing OpenAPI/Swagger definitions or WSDL files, saving time and reducing configuration errors.
- **Choose appropriate pricing tier**: Select the tier that matches your workload requirements, SLA needs, and budget. Start with lower tiers and scale up as needed.

## Practice Questions

### Question 1: Self-Hosted Gateway Container Image Tag

**Scenario**: You plan to use Azure API Management for Hybrid and multicloud API management. You need to create a self-hosted gateway for production.

**Question**: Which container image tag should you use?

**Options**:
- `2.9.0` ✓
- `v3`
- `latest`
- `V3-preview`

**Answer**: `2.9.0`

**Explanation**: 
In production, the version must be pinned to ensure stability and predictable behavior. The only way to achieve that is by using a tag that follows the semantic versioning convention `{major}.{minor}.{patch}` (e.g., `2.9.0`).

- The `v3` tag will result in always running the latest major version with every new feature and patch, which can introduce unexpected changes in production.
- The `latest` tag is used for evaluating the self-hosted gateway and should not be used in production as it continuously updates to the newest version.
- The `V3-preview` tag should be used only to run the latest preview container image for testing pre-release features, not for production workloads.

**Reference**: [Explore API Management - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/explore-api-management/)

### Question 2: OAuth 2.0 Authentication and Usage Quotas

**Scenario**: A company is using Azure API Management to expose their APIs to external partners. The company wants to ensure that the APIs are accessible only to users authenticated with OAuth 2.0, and that usage quotas are enforced to prevent abuse. You need to configure the API Management instance to meet the security and usage requirements.

**Question**: Which two actions should you perform?

**Options**:
- Configure a `validate-jwt` policy to authenticate incoming requests. ✓
- Deploy an Azure Application Gateway in front of the API Management instance.
- Implement IP filtering by defining access restriction policies.
- Set up a `rate-limit-by-key` policy to enforce call quotas. ✓

**Answer**: 
1. Configure a `validate-jwt` policy to authenticate incoming requests.
2. Set up a `rate-limit-by-key` policy to enforce call quotas.

**Explanation**: 
Configuring a `validate-jwt` policy is necessary to authenticate users with OAuth 2.0. This policy validates the JSON Web Token (JWT) in incoming requests, ensuring that only authenticated users can access the APIs.

Setting up a `rate-limit-by-key` policy helps enforce usage quotas by limiting the number of calls that can be made within a specified time period, preventing abuse and ensuring fair usage among partners.

- IP filtering does not address the OAuth 2.0 authentication requirement and is unrelated to usage quota enforcement.
- Deploying an Azure Application Gateway is not required for these specific needs; API Management can handle authentication and rate limiting directly through policies.

**Reference**: 
- [Quickstart: Create a new Azure API Management instance by using the Azure CLI](https://learn.microsoft.com/en-us/azure/api-management/get-started-create-service-instance-cli)
- [Authentication and authorization to APIs in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/authentication-authorization-overview)

### Question 3: Manual API Configuration with Security Policies

**Scenario**: You are a cloud solutions architect working for a company which has recently adopted Microsoft Azure API Management services to centralize the management of their APIs. The company has multiple backend services that provide information on courses, faculty, and student services. These services are consumed by various front-end applications, including the company's public website, student portal, and mobile apps. You need to ensure that the API Management instance is configured to expose only the necessary operations, maintain security, and provide the ability to mock responses for testing purposes without invoking the backend services.

**Question**: What should you do?

**Options**:
- Automatically expose all backend operations through the API Management and use Azure Active Directory B2C for authentication.
- Configure a wildcard operation in the API Management to handle all possible API requests and responses.
- Create a blank API and manually define the necessary operations, then implement policies to validate JWT tokens and limit call rates. ✓
- Import all backend services as APIs into the API Management instance and enable CORS to allow requests from the company's domains.

**Answer**: Create a blank API and manually define the necessary operations, then implement policies to validate JWT tokens and limit call rates.

**Explanation**: 
Creating a blank API and defining necessary operations manually allows for precise control over what is exposed through the API Management gateway. This approach enables you to:
- Expose only the specific operations required by front-end applications, following the principle of least privilege
- Implement mock responses for each operation independently, facilitating testing without invoking backend services
- Apply granular security policies such as JWT validation and rate limiting at the operation level

The other options are incorrect because:
- **Automatically exposing all backend operations** can lead to security risks by exposing unnecessary endpoints and does not provide the granular control needed for mocking specific responses.
- **Using a wildcard operation** makes the API vulnerable to security threats as it accepts any request pattern, and it does not provide the ability to define mock responses for specific operations.
- **Importing all backend services without filtering** exposes unnecessary operations and increases the attack surface. Simply enabling CORS does not address the requirements for selective operation exposure, security policies, or response mocking.

**Reference**: 
- [Explore Microsoft Graph - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/microsoft-graph/)
- [Manually add an API - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/explore-api-management/5-create-api-portal)

### Question 4: Exposing Internal Services to Partners

**Scenario**: You are a cloud solutions architect working for a company that is planning to expose their internal data processing service, which is currently hosted on Azure, to their partners via APIs. The service processes large datasets and provides analytics and reporting features. The company wants to ensure that the API is well-documented, access is securely controlled, and usage policies are enforced. You need to create an Azure API Management instance that allows secure and controlled access to the APIs with the ability to enforce usage policies and document the APIs for your partners.

**Question**: What three steps should you perform?

**Options**:
- Configure access to the APIs by setting up OAuth 2.0 user authorization in the Azure API Management instance. ✓
- Create an Azure API Management instance and import the existing API using the Azure portal's API import functionality. ✓
- Define the API manually in the Azure API Management instance and set up a mock API to simulate the backend until it's fully integrated.
- Document the APIs directly within the code of the data processing service to ensure automatic synchronization with the Azure API Management instance.
- Implement policies for the APIs in the Azure API Management instance to enforce rate limits and quotas. ✓

**Answer**: 
1. Create an Azure API Management instance and import the existing API using the Azure portal's API import functionality.
2. Configure access to the APIs by setting up OAuth 2.0 user authorization in the Azure API Management instance.
3. Implement policies for the APIs in the Azure API Management instance to enforce rate limits and quotas.

**Explanation**: 
These three steps provide a complete solution for securely exposing internal services to partners:

**Creating an Azure API Management instance and importing the existing API** is the foundational step. The import functionality allows you to quickly onboard existing APIs by importing OpenAPI/Swagger definitions, WSDL files, or manually configuring endpoints. This provides a direct way to expose the internal service to partners without recreating the API structure from scratch.

**Configuring OAuth 2.0 user authorization** provides secure access control for the APIs. OAuth 2.0 is an industry-standard protocol that allows partners to authenticate and obtain access tokens, ensuring that only authorized users can access the data processing service. This can be implemented using the `validate-jwt` policy in API Management.

**Implementing policies for rate limits and quotas** is essential for controlling API usage and protecting the backend service from being overwhelmed. Policies like `rate-limit` and `quota` ensure fair usage among partners, prevent abuse, and maintain service availability for all consumers.

The other options are incorrect because:
- **Setting up a mock API** does not address the immediate requirement to expose the actual existing service to partners; it's only useful for testing before the backend is ready.
- **Documenting APIs within the service code** is not the correct approach. API documentation should be managed through the API Management developer portal, where it can be easily accessed by partners. The developer portal automatically generates interactive documentation from the API definition, and additional descriptions can be added through the portal interface or API definition files.

**Reference**: 
- [Explore Microsoft Graph - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/microsoft-graph/)
- [Manually add an API - Training | Microsoft Learn](https://learn.microsoft.com/en-us/training/modules/explore-api-management/5-create-api-portal)

### Question 5: Private Network Access with Public Backends

**Scenario**: A company needs to ensure their Azure API Management instance can only be accessed through a private network connection from client applications, while backend APIs remain publicly accessible.

**Question**: Which networking configuration should you implement?

**Options**:
- Deploy API Management to the Consumption tier with IP restrictions
- Configure API Management with external virtual network mode
- Deploy a Private Endpoint for inbound connectivity to API Management ✓
- Configure API Management with internal virtual network mode

**Answer**: Deploy a Private Endpoint for inbound connectivity to API Management

**Explanation**: 
A Private Endpoint creates an alternative network path for inbound client connections to API Management while allowing the instance to make outbound connections to public backend APIs. This is the ideal solution when:
- Clients must connect through a private network
- Backend APIs need to remain publicly accessible
- You need to separate inbound and outbound network requirements

The other options are incorrect because:
- **Consumption tier with IP restrictions**: The Consumption tier doesn't support Private Endpoints or virtual network integration, so it cannot provide private network connectivity as required.
- **External virtual network mode**: External VNet mode keeps the API Management endpoint publicly accessible, which doesn't meet the requirement for private network access only. It's designed for scenarios where you need to reach private backends while keeping the gateway public.
- **Internal virtual network mode**: Internal VNet mode would make API Management only accessible from within the virtual network for both inbound and outbound traffic, preventing access to public backend APIs without additional configuration (like NAT gateway or firewall).

**Reference**: 
- [Use a virtual network with Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/virtual-network-concepts)
- [Connect privately to API Management using a private endpoint](https://learn.microsoft.com/en-us/azure/api-management/private-endpoint)

### Question 6: Multi-Tenant Rate Limiting and Quotas

**Scenario**: You are implementing a multi-tenant API solution in Azure API Management. Each tenant must have different rate limits and quotas. You want to minimize management overhead while ensuring proper isolation.

**Question**: What should you implement?

**Options**:
- Use a single product with conditional expressions in quota-by-key policy
- Implement rate limiting at the backend service level only
- Create separate products with different quota policies and assign subscriptions per tenant ✓
- Create separate API Management instances for each tenant

**Answer**: Create separate products with different quota policies and assign subscriptions per tenant

**Explanation**: 
Products with quota policies provide a manageable way to implement different limits per tenant through subscriptions, minimizing overhead while maintaining proper isolation. This approach allows you to:
- Define different rate limits and quotas at the product level
- Assign each tenant a subscription to the appropriate product
- Manage tenant-specific limits without complex policy logic
- Leverage built-in subscription management for tenant isolation

The other options are incorrect because:
- **Single product with conditional expressions**: While technically possible, using complex conditional expressions in a single policy increases complexity and maintenance overhead compared to separate products. As the number of tenants grows, the policy becomes increasingly difficult to manage and debug.
- **Backend-level rate limiting**: Backend-level rate limiting doesn't leverage API Management's built-in capabilities and increases complexity in backend services rather than centralizing in API Management. This approach also defeats the purpose of having an API gateway handle cross-cutting concerns like rate limiting.
- **Separate API Management instances**: Creating separate instances provides isolation but significantly increases management overhead and costs, violating the requirement to minimize management overhead. Each instance requires separate configuration, monitoring, and maintenance.

**Reference**: 
- [Products in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-add-products)
- [Advanced request throttling with Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-sample-flexible-throttling)

### Question 7: High-Volume IoT Telemetry with Auto-Scaling

**Scenario**: You are developing an API solution using Azure API Management. The solution must support high-volume IoT telemetry data ingestion with automatic scaling based on traffic, while minimizing costs.

**Question**: Which tier should you choose?

**Options**:
- Developer
- Consumption ✓
- Premium
- Basic v2

**Answer**: Consumption

**Explanation**: 
The **Consumption tier** is the correct choice because it automatically scales based on traffic and bills per execution, making it ideal for variable traffic patterns like IoT telemetry data while minimizing costs. Key benefits for this scenario:
- **Auto-scaling**: Scales from 0 to handle any volume of traffic automatically
- **Pay-per-use pricing**: Only pay for actual API calls (~$3.50 per million executions)
- **No fixed monthly cost**: Perfect for variable/unpredictable traffic patterns
- **Serverless architecture**: No infrastructure management required

The other options are incorrect because:
- **Developer tier**: The Developer tier is for non-production use cases and evaluations only. It doesn't offer an SLA, cannot scale automatically based on traffic (limited to 1 non-scalable unit), and is not suitable for production workloads.
- **Premium tier**: The Premium tier supports high-volume workloads but requires manual scaling configuration and has significantly higher fixed costs (~$2,800/month per unit), which doesn't meet the requirement to minimize costs.
- **Basic v2 tier**: The Basic v2 tier is designed for development and testing scenarios. While it has an SLA, it doesn't automatically scale based on traffic like the Consumption tier does.

**Reference**: 
- [Azure API Management pricing](https://azure.microsoft.com/en-us/pricing/details/api-management/)
- [Azure API Management tiers](https://learn.microsoft.com/en-us/azure/api-management/api-management-features)

### Question 8: OAuth 2.0 JWT Validation for Microsoft Entra ID

**Scenario**: You are configuring OAuth 2.0 authorization for APIs in Azure API Management. You need to validate JWT tokens from Microsoft Entra ID with minimal configuration while ensuring only tokens with specific audience claims are accepted.

**Question**: Which policy should you use?

**Options**:
- `authentication-certificate`
- `validate-jwt`
- `check-header`
- `validate-azure-ad-token` ✓

**Answer**: `validate-azure-ad-token`

**Explanation**: 
The `validate-azure-ad-token` policy is specifically designed for Microsoft Entra ID tokens, providing simplified configuration with built-in support for Microsoft Entra ID endpoints and token validation. This policy:
- Automatically discovers and uses Microsoft Entra ID's OpenID Connect configuration
- Requires minimal setup compared to the generic `validate-jwt` policy
- Provides built-in support for validating audience claims
- Handles Microsoft Entra ID-specific token formats and validation requirements

The other options are incorrect because:
- **`authentication-certificate`**: This policy is used for certificate-based authentication with backend services, not for validating OAuth 2.0 JWT tokens from identity providers. It's designed for mutual TLS scenarios where the API Management needs to present a client certificate to backend services.
- **`validate-jwt`**: While the `validate-jwt` policy can validate tokens from Microsoft Entra ID, it requires more manual configuration including explicitly specifying the OpenID configuration endpoint, issuers, and other settings. The `validate-azure-ad-token` policy provides the same functionality with less configuration overhead for Microsoft Entra ID specifically.
- **`check-header`**: This policy only verifies the presence and value of HTTP headers but cannot validate JWT token signatures, claims, or expiration times. It's a simple header check that doesn't provide any cryptographic validation of tokens.

**Example - validate-azure-ad-token policy**:
```xml
<policies>
    <inbound>
        <validate-azure-ad-token tenant-id="your-tenant-id">
            <audiences>
                <audience>api://your-api-client-id</audience>
            </audiences>
        </validate-azure-ad-token>
    </inbound>
</policies>
```

**Example - validate-jwt policy (more verbose)**:
```xml
<policies>
    <inbound>
        <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
            <openid-config url="https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration" />
            <audiences>
                <audience>api://your-api-client-id</audience>
            </audiences>
            <issuers>
                <issuer>https://sts.windows.net/{tenant-id}/</issuer>
            </issuers>
        </validate-jwt>
    </inbound>
</policies>
```

**Reference**: 
- [Validate Microsoft Entra token policy](https://learn.microsoft.com/en-us/azure/api-management/validate-azure-ad-token-policy)
- [Authentication and authorization to APIs in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/authentication-authorization-overview)

### Question 9: WebSocket API with JWT Validation

**Scenario**: You need to add a WebSocket API to Azure API Management for real-time stock trading updates. The API must support bidirectional communication and apply JWT validation to the initial handshake.

**Question**: Which tier and configuration should you use?

**Options**:
- Consumption tier with WebSocket passthrough enabled in gateway settings
- Any tier except Consumption with JWT validation policy applied to the onHandshake operation ✓
- Premium tier only with custom WebSocket handler policy in the backend section
- Standard tier with WebSocket protocol converter policy in the inbound section

**Answer**: Any tier except Consumption with JWT validation policy applied to the onHandshake operation

**Explanation**: 
WebSocket APIs are supported in all API Management tiers except Consumption, and security policies like JWT validation can be applied specifically to the `onHandshake` operation for authentication. This approach:
- Enables bidirectional communication for real-time scenarios like stock trading updates
- Applies security validation at the initial connection handshake
- Maintains the WebSocket connection after successful authentication
- Works with Developer, Basic, Standard, Premium, and Isolated tiers

The other options are incorrect because:
- **Consumption tier with WebSocket passthrough**: The Consumption tier does not support WebSocket APIs regardless of gateway settings configuration. WebSocket support requires a dedicated tier.
- **Premium tier only with custom WebSocket handler policy**: WebSocket support is available in all tiers except Consumption, not limited to Premium. It doesn't require custom handler policies in the backend section as WebSocket support is native to API Management.
- **Standard tier with WebSocket protocol converter policy**: WebSocket support is native in API Management and doesn't require protocol converter policies. While Standard tier does support WebSocket APIs, no additional protocol conversion configuration is needed.

**Reference**: 
- [WebSocket APIs in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/websocket-api)
- [API Management features and tier comparison](https://learn.microsoft.com/en-us/azure/api-management/api-management-features)

### Question 10: API Versioning with Custom Header

**Scenario**: You need to implement API versioning in Azure API Management where different versions of an API can coexist. Clients should specify the version using a custom header `api-version`.

**Question**: Which configuration should you implement?

**Options**:
- Create separate APIs with suffix naming like `apiv1` and `apiv2`
- Implement `choose` policy to route based on `api-version` header
- Configure revision management with header-based routing
- Configure version set with Header versioning scheme and header name `api-version` ✓

**Answer**: Configure version set with Header versioning scheme and header name `api-version`

**Explanation**: 
Version sets with Header versioning scheme allow clients to specify versions using custom headers, perfectly matching the requirement for `api-version` header-based versioning. This approach:
- Provides built-in versioning functionality specifically designed for managing multiple coexisting API versions
- Allows clients to specify the desired version via the `api-version` header
- Maintains unified management of all versions under a single logical API
- Requires minimal configuration compared to custom policy-based solutions

The other options are incorrect because:
- **Creating separate APIs with suffix naming**: Creating completely separate APIs (like `apiv1` and `apiv2`) lacks the unified management benefits of version sets and requires more manual configuration and maintenance. Each API would need to be managed independently without the relationship that version sets provide.
- **Implementing `choose` policy to route based on header**: While a `choose` policy could technically route requests based on the `api-version` header, version sets provide built-in versioning functionality specifically designed for this scenario with less complexity. Using policies for this purpose adds unnecessary complexity and doesn't leverage API Management's native versioning capabilities.
- **Configuring revision management with header-based routing**: Revisions are designed for non-breaking changes and testing purposes, not for maintaining multiple coexisting versions that clients can choose between. Revisions allow you to make changes safely and test them before making them live, but only one revision is "current" at any time.

**Reference**: 
- [Versions in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-versions)
- [Add multiple versions of your API](https://learn.microsoft.com/en-us/azure/api-management/api-management-get-started-publish-versions)

### Question 11: Developer Portal Customization

**Scenario**: A company wants to customize the developer portal in Azure API Management to match their corporate branding and add custom functionality.

**Question**: What approach should you recommend?

**Options**:
- Use the built-in portal customization widgets in the Azure portal only
- Apply custom CSS through Azure Resource Manager templates during deployment
- Configure custom themes through API Management REST API endpoints
- Self-host the developer portal and modify the source code directly ✓

**Answer**: Self-host the developer portal and modify the source code directly

**Explanation**: 
Self-hosting the developer portal allows full customization including modifying source code, adding custom functionality, and complete control over branding and features. The developer portal source code is available on GitHub and can be downloaded, modified, and hosted on your own infrastructure.

The other options are incorrect because:
- **Built-in customization widgets**: Built-in widgets provide limited options and don't allow adding custom functionality or extensive modifications. They are suitable only for basic branding changes like logos and color schemes.
- **ARM templates for custom CSS**: ARM templates are for infrastructure deployment, not for applying custom CSS or portal customization. They define Azure resources, not application styling.
- **REST API theme configuration**: The API Management REST API doesn't provide theme configuration endpoints for developer portal customization. The REST API is used for managing APIs, products, subscriptions, and other API Management resources.

**Reference**: 
- [Azure API Management developer portal overview](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-developer-portal)
- [Self-host the developer portal](https://learn.microsoft.com/en-us/azure/api-management/developer-portal-self-host)

### Question 12: Backend Error Handling with Cached Data

**Scenario**: You need to handle backend service errors gracefully in Azure API Management by returning a custom error response with cached data when the backend returns a 503 Service Unavailable error.

**Question**: Which policy section should contain your error handling logic?

**Options**:
- backend
- on-error ✓
- outbound
- inbound

**Answer**: on-error

**Explanation**: 
The **on-error** section is specifically designed to handle error conditions including backend failures. It executes when an error occurs during request processing, allowing you to implement custom error responses and return cached data when backends fail. This section is triggered when:
- The backend returns an error response (like 503 Service Unavailable)
- A policy throws an exception
- Any error occurs during the request lifecycle

The other options are incorrect because:
- **backend**: The backend section configures how to call the backend service but executes **before** the backend call is made. It cannot handle errors returned by the backend service because those errors occur after the backend section has completed.
- **outbound**: The outbound section processes **successful** responses from the backend. It does not execute when the backend returns an error like 503, making it unsuitable for error handling logic. The outbound section is skipped entirely when an error occurs.
- **inbound**: The inbound section processes incoming requests **before** they reach the backend. It cannot handle backend errors as these occur after inbound processing is complete. By the time a backend error occurs, the inbound section has already finished executing.

**Reference**: 
- [Error handling in Azure API Management policies](https://learn.microsoft.com/en-us/azure/api-management/api-management-error-handling-policies)
- [API Management policy reference](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies)

### Question 13: Authentication Policies for Backend Services

**Scenario**: You provide an Azure API Management managed web service to clients. The back-end web service implements HTTP Strict Transport Security (HSTS). Every request to the backend service must include a valid HTTP authorization header. You need to configure the Azure API Management instance with an authentication policy.

**Question**: Which two policies can you use?

**Options**:
- Basic Authentication ✓
- Digest Authentication
- Certificate Authentication ✓
- OAuth Client Credential Grant

**Answer**: Basic Authentication and Certificate Authentication

**Explanation**:

**Basic Authentication**:
Basic Authentication is a simple authentication scheme built into the HTTP protocol. It allows clients to authenticate themselves with a username and password. This policy can be used to include a valid HTTP authorization header in every request to the backend service, meeting the requirement for authentication.

**How it works**: The policy adds an `Authorization` header with the format `Basic <base64-encoded-credentials>` to outbound requests. This ensures every request to the backend includes the required HTTP authorization header.

**Certificate Authentication**:
Certificate Authentication involves using client certificates to authenticate clients. This policy can be used to ensure that every request to the backend service includes a valid HTTP authorization header, as the client certificate serves as a form of authentication. It is a suitable choice for configuring the Azure API Management instance with an authentication policy in this scenario.

**How it works**: The policy validates client certificates presented during the TLS handshake. When configured, it requires clients to provide a valid certificate, which serves as the authentication mechanism. This can be combined with other policies to add authorization headers if needed.

**Why the other options are incorrect**:

**Digest Authentication**:
Digest Authentication is another authentication scheme built into the HTTP protocol, but it is more secure than Basic Authentication. However, it does not directly address the need to include a valid HTTP authorization header in every request to the backend service, so it is not the most suitable choice for this scenario.

**Why not suitable**: While Digest Authentication does use HTTP headers for authentication, it's less commonly used in modern API scenarios and may not be supported by all backend services. The scenario specifically requires HTTP authorization headers, and Basic Authentication is more straightforward for this requirement.

**OAuth Client Credential Grant**:
OAuth Client Credential Grant is a flow in OAuth 2.0 that allows a client to authenticate itself and obtain an access token. While this policy can be used for authentication, it may not directly address the requirement to include a valid HTTP authorization header in every request to the backend service. Therefore, it may not be the most appropriate choice for this specific scenario.

**Why not suitable**: OAuth Client Credential Grant typically results in obtaining an access token that can be used in subsequent requests, but it doesn't automatically add HTTP authorization headers to every request. The scenario requires that "every request to the backend service must include a valid HTTP authorization header," which Basic and Certificate Authentication handle more directly.

**Reference**:
- [Authentication policies in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-authentication-policies)
- [API Management policy reference](https://learn.microsoft.com/en-us/azure/api-management/api-management-policies)

### Question 14: API Caching Policies for OAuth-Authenticated APIs

**Scenario**: A web service provides customer summary information for e-commerce partners. The web service is implemented as an Azure Function app with an HTTP trigger. Access to the API is provided by an Azure API Management instance configured in consumption plan mode. All API calls are authenticated by using OAuth. API calls must be cached. Customers must not be able to view cached data for other customers.

**Question**: You need to configure API Management policies for caching. How should you complete the policy statement?

**Options**:
- **Choice A**: `caching-type: Internal`, `downstream-caching-type: Private`, `vary-by-header: Authorization`
- **Choice B**: `caching-type: Public`, `downstream-caching-type: Expect`, `vary-by-header: Private`
- **Choice C**: `caching-type: Internal`, `downstream-caching-type: External`, `vary-by-header: Authorization`
- **Choice D**: `caching-type: External`, `downstream-caching-type: Private`, `vary-by-header: Authorization` ✓

**Answer**: **Choice D** - `caching-type: External`, `downstream-caching-type: Private`, `vary-by-header: Authorization`

**Explanation**: 

**Why Choice D is correct**:
The policy statement in Choice D specifies:
- **`caching-type: External`**: In the Consumption tier, only external caching is available (internal caching is not supported). External caching allows the cache to be shared across multiple instances of API Management while still respecting the `vary-by-header` setting for user-specific caching.
- **`downstream-caching-type: Private`**: This ensures that cached data is specific to each user and prevents intermediate proxies or CDNs from caching responses that could be served to other users. The `Private` directive instructs downstream caches (like browsers) to cache responses only for the specific user who made the request.
- **`vary-by-header: Authorization`**: This is critical for OAuth-authenticated APIs. It ensures that the cache creates separate entries based on the `Authorization` header, preventing one customer from seeing another customer's cached data. Each unique OAuth token will result in a separate cache entry.

**Why other choices are incorrect**:

**Choice A** - `caching-type: Internal`, `downstream-caching-type: Private`, `vary-by-header: Authorization`:
- **Incorrect**: The Consumption tier **does not support internal caching**. Internal caching is only available in Developer, Basic, Standard, and Premium tiers. Since the scenario explicitly states the API Management is in Consumption plan mode, internal caching cannot be used.
- The `downstream-caching-type: Private` and `vary-by-header: Authorization` settings are correct, but the incorrect `caching-type` makes this choice invalid.

**Choice B** - `caching-type: Public`, `downstream-caching-type: Expect`, `vary-by-header: Private`:
- **Incorrect**: `caching-type: Public` is not a valid value for this parameter. The valid options are `Internal` and `External`.
- **Incorrect**: `downstream-caching-type: Expect` is not a valid caching type. The valid values are `None`, `Private`, and `Public`.
- **Incorrect**: `vary-by-header: Private` doesn't make sense in this context. `Private` is not a valid HTTP header name. The `vary-by-header` should specify `Authorization` to ensure caching varies by the OAuth token.

**Choice C** - `caching-type: Internal`, `downstream-caching-type: External`, `vary-by-header: Authorization`:
- **Incorrect**: As with Choice A, `caching-type: Internal` is not supported in the Consumption tier.
- **Incorrect**: `downstream-caching-type: External` is not a valid caching type. The valid values are `None`, `Private`, and `Public`.
- The `vary-by-header: Authorization` setting is correct, but the other two parameters are invalid.

**Key Concepts**:

1. **Consumption Tier Caching Limitations**: The Consumption tier only supports external caching, not internal caching. This is important to remember when designing caching strategies for serverless API Management instances.

2. **OAuth and Cache Separation**: When using OAuth authentication, it's essential to vary the cache by the `Authorization` header to ensure each user's data is cached separately. This prevents security issues where one user could see another user's cached data.

3. **Downstream Caching Control**: The `downstream-caching-type: Private` setting adds the `Cache-Control: private` header to responses, instructing browsers and intermediate proxies to cache the response only for the specific user, not for multiple users.

**Example Policy Implementation**:
```xml
<policies>
    <inbound>
        <cache-lookup vary-by-header="Authorization" downstream-caching-type="private" />
    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <cache-store duration="3600" caching-type="external" />
        <base />
    </outbound>
</policies>
```

**Reference**:
- [Caching in Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/api-management-howto-cache)
- [Cache lookup policy](https://learn.microsoft.com/en-us/azure/api-management/cache-lookup-policy)
- [Cache store policy](https://learn.microsoft.com/en-us/azure/api-management/cache-store-policy)
- [API Management Consumption tier features](https://learn.microsoft.com/en-us/azure/api-management/api-management-features)
