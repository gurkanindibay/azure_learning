# Azure API Manager

## Table of Contents
1. [Purpose](#purpose)
2. [Platform Overview](#platform-overview)
3. [Subscription Keys](#subscription-keys)
4. [Certificates](#certificates)
5. [Simple Usage Examples](#simple-usage-examples)
6. [Operational Best Practices](#operational-best-practices)

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

## Operational Best Practices
- **Monitor usage**: Configure Application Insights or the built-in analytics to track latency, throttled requests, and subscription failures.
- **Automate deployment**: Use Azure Resource Manager (ARM) templates or Bicep to publish APIs/policies and manage environments consistently.
- **Secure secrets**: Store sensitive values in named values and mark them as secrets, then reference them securely inside policies with `{{secret-name}}`.
- **Design APIs for resiliency**: Use caching policies (`<cache-lookup>`/`<cache-store>`), rate limits, and retries to shield backends from spikes.
- **Document clearly**: Keep the developer portal updated with descriptions, sample payloads, and contact details to reduce support load.
