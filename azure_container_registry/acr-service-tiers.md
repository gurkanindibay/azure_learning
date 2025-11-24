# Azure Container Registry Service Tiers

## Table of Contents

- [Overview](#overview)
- [Service Tiers Comparison](#service-tiers-comparison)
- [Basic Tier](#basic-tier)
- [Standard Tier](#standard-tier)
- [Premium Tier](#premium-tier)
- [Detailed Feature Comparison](#detailed-feature-comparison)
- [Storage and Bandwidth](#storage-and-bandwidth)
- [Performance Characteristics](#performance-characteristics)
- [Security Features by Tier](#security-features-by-tier)
- [Choosing the Right Tier](#choosing-the-right-tier)
- [Pricing Considerations](#pricing-considerations)
- [Upgrading Between Tiers](#upgrading-between-tiers)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure Container Registry (ACR) offers three service tiers: **Basic**, **Standard**, and **Premium**. Each tier provides different levels of storage, throughput, and features to meet varying workload requirements. All tiers include the same programmatic capabilities, such as Azure Active Directory authentication integration, image deletion, and webhooks.

## Service Tiers Comparison

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| **Included Storage** | 10 GiB | 100 GiB | 500 GiB |
| **Total Storage Limit** | Unlimited | Unlimited | Unlimited |
| **Bandwidth (per month)** | N/A | N/A | N/A |
| **ReadOps/Min** | 1,000 | 3,000 | 10,000 |
| **WriteOps/Min** | 100 | 500 | 2,000 |
| **Webhooks** | 2 | 10 | 500 |
| **Geo-replication** | ❌ | ❌ | ✅ |
| **Availability Zones** | ❌ | ❌ | ✅ |
| **Content Trust (signing)** | ❌ | ❌ | ✅ |
| **Private Link** | ❌ | ❌ | ✅ |
| **Customer-Managed Keys** | ❌ | ❌ | ✅ |
| **Repository-scoped permissions** | ❌ | ❌ | ✅ |
| **Token authentication** | ❌ | ❌ | ✅ |
| **Encryption at rest** | ✅ | ✅ | ✅ (+ customer keys) |
| **Best For** | Dev/Test | Production (single region) | Enterprise, Global |

## Basic Tier

### Characteristics

- **Entry-level tier** for learning and development
- **10 GiB included storage** (can expand with additional cost)
- **Lower throughput** compared to Standard and Premium
- **Basic features only** - no advanced security or geo-replication
- **2 webhooks** maximum

### Performance Limits

- **Read Operations**: Up to 1,000 per minute
- **Write Operations**: Up to 100 per minute
- Suitable for light workloads

### When to Use

✅ **Use Basic tier when:**
- Development and testing environments
- Learning Azure Container Registry
- Low-frequency image pulls/pushes
- Single developer or small team
- Cost is primary concern
- No geo-replication needed

❌ **Don't use Basic when:**
- Production workloads with high availability requirements
- Need geo-replication
- Require advanced security features
- High-throughput scenarios

### Code Example

```bash
# Create Basic tier registry
az acr create \
  --resource-group myResourceGroup \
  --name mybasicregistry \
  --sku Basic \
  --location eastus

# Login to registry
az acr login --name mybasicregistry

# Tag and push image
docker tag myapp:latest mybasicregistry.azurecr.io/myapp:v1
docker push mybasicregistry.azurecr.io/myapp:v1
```

### Cost Example

- **Base price**: ~$5/month
- **Additional storage**: ~$0.10 per GiB/month above included 10 GiB
- **Operations**: Included in base price

## Standard Tier

### Characteristics

- **Production-ready** for single-region deployments
- **100 GiB included storage**
- **Higher throughput** than Basic
- **10 webhooks** for automation
- Still lacks advanced features like geo-replication

### Performance Limits

- **Read Operations**: Up to 3,000 per minute (3x Basic)
- **Write Operations**: Up to 500 per minute (5x Basic)
- Suitable for moderate production workloads

### When to Use

✅ **Use Standard tier when:**
- Production applications (single region)
- Moderate image pull/push frequency
- Need more webhooks for CI/CD integration
- Larger storage requirements (up to 100 GiB included)
- Better performance than Basic required
- Team-based development

❌ **Don't use Standard when:**
- Need geo-replication for global distribution
- Require private endpoints
- Need content trust/image signing
- Require zone redundancy

### Code Example

```bash
# Create Standard tier registry
az acr create \
  --resource-group myResourceGroup \
  --name mystandardregistry \
  --sku Standard \
  --location eastus

# Configure multiple webhooks for CI/CD
az acr webhook create \
  --registry mystandardregistry \
  --name webhook1 \
  --actions push delete \
  --uri https://myapp.azurewebsites.net/webhook

az acr webhook create \
  --registry mystandardregistry \
  --name webhook2 \
  --actions push \
  --uri https://myapp-staging.azurewebsites.net/webhook
```

### Use Case Example: CI/CD Pipeline

```yaml
# Azure DevOps Pipeline
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  registry: 'mystandardregistry.azurecr.io'
  imageName: 'myapp'
  tag: '$(Build.BuildId)'

steps:
- task: Docker@2
  displayName: 'Build and Push'
  inputs:
    command: buildAndPush
    repository: $(imageName)
    containerRegistry: mystandardregistry
    tags: |
      $(tag)
      latest
```

### Cost Example

- **Base price**: ~$20/month
- **Additional storage**: ~$0.10 per GiB/month above included 100 GiB
- **Better value** for production workloads

## Premium Tier

### Characteristics

- **Enterprise-grade** container registry
- **500 GiB included storage**
- **Highest throughput** and performance
- **Advanced security features**
- **Geo-replication** for global distribution
- **Availability zone support** for high availability
- **500 webhooks** for complex automation
- **Private Link** support for VNet integration
- **Customer-managed encryption keys**
- **Repository-scoped permissions** for fine-grained access control
- **Token authentication** for enhanced security

### Performance Limits

- **Read Operations**: Up to 10,000 per minute (10x Basic)
- **Write Operations**: Up to 2,000 per minute (20x Basic)
- Optimized for high-scale production workloads

### Advanced Features

#### 1. Geo-Replication

Replicate registry across multiple Azure regions for:
- Low-latency access globally
- Regional redundancy
- Disaster recovery

```bash
# Enable geo-replication to multiple regions
az acr replication create \
  --registry mypremiumregistry \
  --location westus

az acr replication create \
  --registry mypremiumregistry \
  --location westeurope

az acr replication create \
  --registry mypremiumregistry \
  --location southeastasia

# List replications
az acr replication list \
  --registry mypremiumregistry \
  --output table
```

**How Geo-Replication Works:**
- Single registry endpoint with automatic routing
- Images automatically replicated to all regions
- Kubernetes pulls from nearest region
- No code changes needed

#### 2. Private Link (Private Endpoints)

Connect registry to VNet using private IP addresses:
- No public internet exposure
- Traffic stays on Microsoft backbone
- Enhanced security

```bash
# Create private endpoint
az network private-endpoint create \
  --name myACRPrivateEndpoint \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet mySubnet \
  --private-connection-resource-id $(az acr show --name mypremiumregistry --query id -o tsv) \
  --group-id registry \
  --connection-name myACRConnection

# Disable public network access
az acr update \
  --name mypremiumregistry \
  --public-network-enabled false
```

#### 3. Content Trust (Image Signing)

Sign container images for integrity verification:

```bash
# Enable content trust
export DOCKER_CONTENT_TRUST=1
export DOCKER_CONTENT_TRUST_SERVER=https://mypremiumregistry.azurecr.io

# Push signed image
docker push mypremiumregistry.azurecr.io/myapp:signed

# Only signed images can be pulled
docker pull mypremiumregistry.azurecr.io/myapp:signed
```

#### 4. Customer-Managed Keys (CMK)

Encrypt registry with your own encryption keys:

```bash
# Create Key Vault and key
az keyvault create \
  --name mykeyvault \
  --resource-group myResourceGroup

az keyvault key create \
  --vault-name mykeyvault \
  --name myregkey \
  --kty RSA \
  --size 2048

# Enable customer-managed key encryption
az acr encryption create \
  --resource-group myResourceGroup \
  --registry-name mypremiumregistry \
  --key-encryption-key myregkey \
  --identity [system/user-assigned-identity]
```

#### 5. Repository-Scoped Permissions

Fine-grained access control per repository:

```bash
# Create token with specific repository permissions
az acr token create \
  --name mytoken \
  --registry mypremiumregistry \
  --repository myapp content/read content/write \
  --repository otherapp content/read

# Generate credentials
az acr token credential generate \
  --name mytoken \
  --registry mypremiumregistry
```

#### 6. Availability Zones

Enable zone redundancy for high availability:

```bash
# Create Premium registry with zone redundancy
az acr create \
  --resource-group myResourceGroup \
  --name mypremiumregistry \
  --sku Premium \
  --zone-redundancy enabled \
  --location eastus
```

### When to Use

✅ **Use Premium tier when:**
- **Global applications** requiring low-latency access worldwide
- **Enterprise production** workloads
- **High availability** requirements (99.99% SLA with availability zones)
- **Advanced security** needs (private endpoints, CMK, signing)
- **High throughput** scenarios (thousands of pulls/pushes per minute)
- **Compliance** requirements for encryption and access control
- **Multi-region deployments**
- **Large-scale Kubernetes clusters**

### Complete Example: Enterprise Setup

```bash
# 1. Create Premium registry with zone redundancy
az acr create \
  --resource-group production-rg \
  --name myenterprise registry \
  --sku Premium \
  --location eastus \
  --zone-redundancy enabled

# 2. Enable geo-replication
az acr replication create --registry myenterpriseregistry --location westeurope
az acr replication create --registry myenterpriseregistry --location eastasia

# 3. Set up private endpoint
az network private-endpoint create \
  --name acrPrivateEndpoint \
  --resource-group production-rg \
  --vnet-name production-vnet \
  --subnet acr-subnet \
  --private-connection-resource-id $(az acr show --name myenterpriseregistry --query id -o tsv) \
  --group-id registry \
  --connection-name acrConnection

# 4. Disable public access
az acr update --name myenterpriseregistry --public-network-enabled false

# 5. Enable customer-managed encryption
az acr encryption create \
  --resource-group production-rg \
  --registry-name myenterpriseregistry \
  --key-encryption-key mykey \
  --identity system

# 6. Configure webhooks for automation
for i in {1..10}; do
  az acr webhook create \
    --registry myenterpriseregistry \
    --name webhook$i \
    --actions push \
    --uri https://app$i.mycompany.com/webhook
done
```

### Cost Example

- **Base price**: ~$500/month
- **Geo-replication**: Additional cost per replica region (~$500/region/month)
- **Additional storage**: ~$0.10 per GiB/month above included 500 GiB
- **Private endpoints**: Additional Azure Private Link charges

**Cost Calculation Example:**
```
Premium registry in East US: $500/month
+ Geo-replication to West Europe: $500/month
+ Geo-replication to Southeast Asia: $500/month
+ 200 GiB additional storage: $20/month
+ Private endpoints (2): ~$15/month
-------------------------------------------
Total: ~$1,535/month
```

## Detailed Feature Comparison

### Networking Features

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Public endpoint | ✅ | ✅ | ✅ |
| Private endpoint (VNet) | ❌ | ❌ | ✅ |
| Service endpoint | ❌ | ❌ | ✅ |
| Firewall rules | ✅ | ✅ | ✅ |
| IP whitelisting | ✅ | ✅ | ✅ |
| Azure Private Link | ❌ | ❌ | ✅ |

### Authentication & Security

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Azure AD authentication | ✅ | ✅ | ✅ |
| Service principal | ✅ | ✅ | ✅ |
| Managed identity | ✅ | ✅ | ✅ |
| Admin user (deprecated) | ✅ | ✅ | ✅ |
| Token authentication | ❌ | ❌ | ✅ |
| Repository-scoped tokens | ❌ | ❌ | ✅ |
| Content trust (signing) | ❌ | ❌ | ✅ |
| Customer-managed keys | ❌ | ❌ | ✅ |
| Azure RBAC | ✅ | ✅ | ✅ |
| Repository-scoped RBAC | ❌ | ❌ | ✅ |

### High Availability & Disaster Recovery

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Availability zones | ❌ | ❌ | ✅ |
| Geo-replication | ❌ | ❌ | ✅ |
| SLA | 99.9% | 99.9% | 99.99% (with zones) |
| Regional redundancy | ❌ | ❌ | ✅ |

### Image Management

| Feature | Basic | Standard | Premium |
|---------|-------|----------|---------|
| Image push/pull | ✅ | ✅ | ✅ |
| Image delete | ✅ | ✅ | ✅ |
| Image lock | ✅ | ✅ | ✅ |
| Image quarantine | ✅ | ✅ | ✅ |
| Artifact cache | ❌ | ❌ | ✅ |
| OCI artifacts | ✅ | ✅ | ✅ |
| Helm charts | ✅ | ✅ | ✅ |

## Storage and Bandwidth

### Storage Characteristics

| Tier | Included Storage | Additional Storage Cost | Total Limit |
|------|------------------|------------------------|-------------|
| Basic | 10 GiB | $0.10/GiB/month | Unlimited |
| Standard | 100 GiB | $0.10/GiB/month | Unlimited |
| Premium | 500 GiB | $0.10/GiB/month | Unlimited |

**Storage Billing:**
- Charged for average daily storage usage
- Includes all layers, manifests, and tags
- Soft-deleted images count toward storage
- Geo-replicated storage counts per region

**Example Storage Calculation:**
```
Scenario: 750 GiB total storage in Premium tier

Included: 500 GiB (covered by base price)
Additional: 250 GiB × $0.10 = $25/month

With geo-replication to 2 additional regions:
250 GiB × $0.10 × 3 regions = $75/month additional storage
```

### Bandwidth

- **Ingress (push)**: Free for all tiers
- **Egress (pull)**: Charged based on Azure bandwidth pricing
- **Same region**: Typically free
- **Cross-region**: Standard Azure egress charges apply

**Bandwidth Optimization Tips:**
1. Use geo-replication (Premium) to minimize egress charges
2. Deploy registry in same region as compute resources
3. Use artifact cache to reduce external pulls

## Performance Characteristics

### Throughput Comparison

```
Premium: ████████████████████ 10,000 read ops/min
Standard: ███████              3,000 read ops/min
Basic:    ██                   1,000 read ops/min

Premium: ████████████████████ 2,000 write ops/min
Standard: █████                  500 write ops/min
Basic:    █                      100 write ops/min
```

### Real-World Performance Impact

**Scenario: Kubernetes Cluster with 100 Nodes**

**Basic Tier:**
- 1,000 read ops/min ÷ 100 nodes = 10 pulls/node/min
- Deployment rollout: **Slow** (throttling likely)
- Result: ❌ Not suitable

**Standard Tier:**
- 3,000 read ops/min ÷ 100 nodes = 30 pulls/node/min
- Deployment rollout: **Moderate** (may experience throttling)
- Result: ⚠️ Marginal for large clusters

**Premium Tier:**
- 10,000 read ops/min ÷ 100 nodes = 100 pulls/node/min
- Deployment rollout: **Fast** (no throttling)
- Result: ✅ Recommended

### Latency Considerations

**Without Geo-Replication (Basic/Standard):**
```
US East → ACR (US East) → Kubernetes (US East): ~1-5ms
Europe → ACR (US East) → Kubernetes (Europe): ~100-200ms ❌
Asia → ACR (US East) → Kubernetes (Asia): ~200-300ms ❌
```

**With Geo-Replication (Premium):**
```
US East → ACR (US East) → Kubernetes (US East): ~1-5ms ✅
Europe → ACR (Europe) → Kubernetes (Europe): ~1-5ms ✅
Asia → ACR (Asia) → Kubernetes (Asia): ~1-5ms ✅
```

## Security Features by Tier

### Basic & Standard Security

**Available Features:**
- Azure AD authentication
- RBAC at registry level
- Network firewall rules
- Microsoft-managed encryption at rest
- TLS 1.2 encryption in transit
- Vulnerability scanning (via Microsoft Defender)

**Limitations:**
- ❌ No private endpoints
- ❌ No customer-managed encryption keys
- ❌ No content trust/signing
- ❌ No repository-scoped permissions

### Premium Security

**All Basic/Standard features PLUS:**

**1. Private Link Integration**
```bash
# Isolate registry on private network
az acr update \
  --name mypremiumregistry \
  --public-network-enabled false \
  --default-action Deny
```

**2. Customer-Managed Keys**
```bash
# Use your own encryption keys
az acr encryption create \
  --registry mypremiumregistry \
  --key-encryption-key mykey \
  --identity system
```

**3. Content Trust**
```bash
# Sign and verify images
export DOCKER_CONTENT_TRUST=1
docker push mypremiumregistry.azurecr.io/secure-app:v1
```

**4. Repository-Scoped Access**
```bash
# Fine-grained permissions per repository
az acr token create \
  --name deploy-token \
  --registry mypremiumregistry \
  --repository app1 content/read metadata/read \
  --repository app2 content/write
```

## Choosing the Right Tier

### Decision Matrix

```
Need geo-replication or private endpoints?
│
├─ YES → Premium (required)
│
└─ NO
   │
   ├─ Production workload with moderate throughput?
   │  └─ YES → Standard
   │
   └─ NO
      │
      └─ Dev/Test or learning?
         └─ YES → Basic
```

### Tier Selection by Scenario

| Scenario | Recommended Tier | Reason |
|----------|------------------|---------|
| **Learning ACR** | Basic | Cost-effective, full API support |
| **Development** | Basic or Standard | Depends on team size and frequency |
| **Single-region production** | Standard | Good performance, reasonable cost |
| **Multi-region production** | Premium | Geo-replication required |
| **Enterprise compliance** | Premium | Private Link, CMK required |
| **High-scale Kubernetes** | Premium | Performance and availability |
| **Global application** | Premium | Low latency via geo-replication |
| **CI/CD pipelines** | Standard or Premium | Depends on scale and regions |

### Key Decision Factors

**Choose Basic if:**
- Budget is primary concern
- Learning or experimenting
- Low pull/push frequency (<1,000 ops/min)
- Single developer or small team
- No advanced features needed

**Choose Standard if:**
- Production app in single region
- Moderate throughput (up to 3,000 read ops/min)
- Need more webhooks for CI/CD
- Larger storage needs (up to 100 GiB included)
- Cost-performance balance

**Choose Premium if:**
- Global application
- Compliance requirements (private endpoints, CMK)
- High availability (zone redundancy)
- High throughput (>3,000 ops/min)
- Content trust/image signing needed
- Fine-grained access control required

## Pricing Considerations

### Monthly Cost Estimates (US Regions)

**Basic:**
- Base: ~$5/month
- Total: ~$5-15/month (including typical storage)

**Standard:**
- Base: ~$20/month
- Total: ~$20-40/month (including typical storage)

**Premium:**
- Base: ~$500/month
- Geo-replication: +$500/region/month
- Total: ~$500-2,000+/month (depending on replicas and storage)

### Cost Optimization Strategies

1. **Start Small, Scale Up**
   ```bash
   # Begin with Basic or Standard
   az acr create --sku Standard
   
   # Upgrade when needed
   az acr update --sku Premium
   ```

2. **Use Appropriate Tier per Environment**
   - Development: Basic
   - Staging: Standard
   - Production: Premium (if needed)

3. **Lifecycle Management**
   ```bash
   # Clean up old images to reduce storage costs
   az acr repository show-tags \
     --name myregistry \
     --repository myapp \
     --output table
   
   az acr repository delete \
     --name myregistry \
     --image myapp:old-tag
   ```

4. **Monitor Usage**
   ```bash
   # Check storage usage
   az acr show-usage \
     --name myregistry \
     --output table
   ```

## Upgrading Between Tiers

### Upgrade Process

**Upgrading is seamless** - no downtime or data migration required:

```bash
# Upgrade from Basic to Standard
az acr update \
  --name myregistry \
  --sku Standard

# Upgrade from Standard to Premium
az acr update \
  --name myregistry \
  --sku Premium
```

### Important Notes

- ✅ **Upgrading** is always supported and instant
- ✅ No downtime during upgrade
- ✅ All existing images, tags, and configurations preserved
- ⚠️ **Downgrading** is supported but may lose Premium/Standard features
- ⚠️ Cannot downgrade if using Premium-only features (geo-replication, private endpoints)

### Downgrade Considerations

```bash
# Downgrade from Premium to Standard
# NOTE: Must remove Premium-only features first

# 1. Remove geo-replications
az acr replication list --registry myregistry --output table
az acr replication delete --registry myregistry --name westeurope
az acr replication delete --registry myregistry --name eastasia

# 2. Remove private endpoints
az network private-endpoint delete --name acrPrivateEndpoint

# 3. Disable customer-managed key
az acr encryption update \
  --resource-group myResourceGroup \
  --registry myregistry \
  --key-encryption-key ""

# 4. Now downgrade
az acr update --name myregistry --sku Standard
```

## Exam Questions and Scenarios

### Question 1: Global Application

**Scenario:** You have a production application deployed across three Azure regions: East US, West Europe, and Southeast Asia. You need low-latency container image pulls in all regions.

**Question:** Which ACR tier should you use?

**Answer:** **Premium**

**Reasoning:**
- ✅ Only Premium supports geo-replication
- ✅ Enables low-latency pulls from all regions
- ✅ Automatic image replication across regions
- ❌ Basic and Standard don't support geo-replication

### Question 2: Private Network Requirement

**Scenario:** Your company security policy requires that container registry must not be accessible from public internet and must use private IP addresses within your VNet.

**Question:** Which tier and features should you use?

**Answer:** **Premium with Private Link (Private Endpoints)**

**Reasoning:**
- ✅ Only Premium supports Private Link/Private Endpoints
- ✅ Enables VNet integration with private IP
- ✅ Can disable public access completely
- ❌ Basic and Standard only support public endpoints

### Question 3: Development Environment

**Scenario:** Your team is learning Azure Container Registry for a new project. You need to experiment with pushing and pulling images but have a limited budget.

**Question:** Which tier is most appropriate?

**Answer:** **Basic**

**Reasoning:**
- ✅ Cost-effective for learning and development
- ✅ Full API compatibility (same as Premium)
- ✅ Sufficient for development workloads
- ✅ Can upgrade later when moving to production

### Question 4: High-Scale Kubernetes

**Scenario:** You run a large Kubernetes cluster with 500 nodes that need to pull images during rolling updates. You're experiencing throttling with your current registry.

**Question:** What should you do?

**Answer:** **Upgrade to Premium tier**

**Reasoning:**
- ✅ Premium offers 10,000 read ops/min (vs 3,000 for Standard)
- ✅ Can handle large cluster scale
- ✅ Prevents throttling during deployments
- ⚠️ Standard's 3,000 ops/min insufficient for 500 nodes

## Best Practices

### General Best Practices

1. **Start with Appropriate Tier**
   - Development: Basic
   - Production (single region): Standard
   - Enterprise/Global: Premium

2. **Monitor Performance**
   ```bash
   # Monitor registry metrics
   az monitor metrics list \
     --resource $(az acr show --name myregistry --query id -o tsv) \
     --metric TotalPullCount TotalPushCount StorageUsed
   ```

3. **Implement Image Lifecycle Policies**
   ```bash
   # Automatic cleanup of old images
   az acr task create \
     --name cleanup \
     --registry myregistry \
     --cmd "acr purge --filter 'myapp:.*' --ago 30d --untagged" \
     --schedule "0 0 * * *"
   ```

4. **Use Appropriate Authentication**
   ```bash
   # Use managed identity for AKS
   az aks update \
     --name myakscluster \
     --resource-group myResourceGroup \
     --attach-acr myregistry
   ```

### Premium Tier Best Practices

1. **Optimize Geo-Replication**
   - Place replicas in regions where you have compute resources
   - Don't over-replicate (each replica costs extra)

2. **Leverage Private Endpoints**
   ```bash
   # Use private endpoints for production
   az acr update \
     --name myregistry \
     --public-network-enabled false
   ```

3. **Implement Content Trust**
   ```bash
   # Sign critical images
   export DOCKER_CONTENT_TRUST=1
   docker push myregistry.azurecr.io/production-app:v1
   ```

4. **Use Repository-Scoped Permissions**
   ```bash
   # Grant minimal permissions per service
   az acr token create \
     --name service1-token \
     --registry myregistry \
     --repository service1 content/read
   ```

5. **Enable Zone Redundancy**
   ```bash
   # For maximum availability
   az acr create \
     --sku Premium \
     --zone-redundancy enabled
   ```

## References

- [Azure Container Registry service tiers](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-skus)
- [Geo-replication in Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-geo-replication)
- [Azure Container Registry pricing](https://azure.microsoft.com/en-us/pricing/details/container-registry/)
- [Private endpoint for Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-private-link)
- [Content trust in Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-content-trust)
- [Encrypt registry using customer-managed key](https://learn.microsoft.com/en-us/azure/container-registry/tutorial-enable-customer-managed-keys)
