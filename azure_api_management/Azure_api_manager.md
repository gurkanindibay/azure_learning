# Azure API Manager

## Table of Contents
1. [Purpose](#purpose)
2. [Platform Overview](#platform-overview)
3. [Subscription Keys](#subscription-keys)
4. [Certificates](#certificates)
5. [Simple Usage Examples](#simple-usage-examples)
6. [Operational Best Practices](#operational-best-practices)
7. [Practice Questions](#practice-questions)

## Purpose
Azure API Manager (API Management) is the turnkey service on Microsoft Azure that lets teams publish, secure, transform, maintain, and monitor APIs. It is designed to sit between consumers (internal applications, partners, or external developers) and backend services, applying consistent security, routing, and transformation policies without touching the target APIs.

## Platform Overview
- **Gateway tier**: Handles inbound requests, enforces policies, and routes calls to backend services. It supports multi-region deployment, virtual network integration, and caching.
- **Publisher portal**: Used by platform owners to configure APIs, products, policies, and developer onboarding.
- **Developer portal**: Self-service interface where consumers discover APIs, read documentation, and obtain credentials.
- **Products**: Group APIs into packages with quotas, rate limits, and visibility rules. Consumers subscribe to products to receive a subscription key.

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
