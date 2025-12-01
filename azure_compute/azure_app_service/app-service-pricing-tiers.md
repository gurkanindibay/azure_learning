# Azure App Service Pricing Tiers

## Table of Contents

- [Overview](#overview)
- [Pricing Tiers Comparison](#pricing-tiers-comparison)
- [Free Tier (F1)](#free-tier-f1)
- [Shared Tier (D1)](#shared-tier-d1)
- [Basic Tier (B1, B2, B3)](#basic-tier-b1-b2-b3)
- [Standard Tier (S1, S2, S3)](#standard-tier-s1-s2-s3)
- [Premium Tier (P1v2, P2v2, P3v2, P1v3, P2v3, P3v3)](#premium-tier-p1v2-p2v2-p3v2-p1v3-p2v3-p3v3)
- [Isolated Tier (I1v2, I2v2, I3v2)](#isolated-tier-i1v2-i2v2-i3v2)
- [Detailed Feature Comparison](#detailed-feature-comparison)
  - [Networking Features Deep Dive](#networking-features-deep-dive)
- [Compute Resources by Tier](#compute-resources-by-tier)
- [Choosing the Right Tier](#choosing-the-right-tier)
- [Scaling Options](#scaling-options)
- [Cost Considerations](#cost-considerations)
- [Changing Between Tiers](#changing-between-tiers)
- [Exam Questions and Scenarios](#exam-questions-and-scenarios)
- [Custom Domains and TLS/SSL Certificates](#custom-domains-and-tlsssl-certificates)
- [Best Practices](#best-practices)
- [References](#references)

## Overview

Azure App Service offers six pricing tiers (also called SKUs or service plans), each designed for different workload types and requirements. The tier you choose determines the compute resources, features, and pricing for your web apps.

## Pricing Tiers Comparison

| Feature | Free | Shared | Basic | Standard | Premium | Isolated |
|---------|------|--------|-------|----------|---------|----------|
| **Target Audience** | Dev/Test | Dev/Test | Production | Production | Enterprise | Dedicated Env |
| **Shared/Dedicated Compute** | Shared | Shared | Dedicated | Dedicated | Dedicated | Dedicated |
| **Apps per Plan** | 10 | 100 | Unlimited | Unlimited | Unlimited | Unlimited |
| **Maximum Instances** | 1 | 1 | Up to 3 | Up to 10 | Up to 30 | Up to 100 |
| **Storage** | 1 GB | 1 GB | 10 GB | 50 GB | 250 GB | 1 TB |
| **Custom Domain** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **SSL/TLS** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Auto Scale** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Deployment Slots** | ❌ | ❌ | ❌ | 5 | 20 | 20 |
| **Backup/Restore** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Traffic Manager** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **VNet Integration** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Private Endpoints** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **App Service Environment** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **SLA** | None | None | 99.95% | 99.95% | 99.95% | 99.95% |

## Free Tier (F1)

### Characteristics

- **No cost** - completely free
- **Shared compute** - runs on shared VMs with other customers
- **60 CPU minutes/day** quota (resets daily)
- **1 GB disk space**
- **1 GB memory**
- **Maximum 10 apps** per subscription
- **No custom domains** or SSL
- **No SLA**

### When to Use

✅ **Use Free tier when:**
- Learning Azure App Service
- Building proof-of-concepts
- Development and testing
- Very low-traffic personal projects
- Demos and tutorials

❌ **Don't use Free when:**
- Production workloads
- Need custom domains
- Require SSL/TLS
- Need guaranteed uptime
- High-traffic applications

### Code Example

```bash
# Create Free tier App Service Plan
az appservice plan create \
  --name myFreeAppServicePlan \
  --resource-group myResourceGroup \
  --location eastus \
  --sku FREE

# Create web app
az webapp create \
  --name myFreeWebApp \
  --resource-group myResourceGroup \
  --plan myFreeAppServicePlan
```

### Limitations

- ⏱️ 60 CPU minutes per day limit
- 🌐 No custom domains (only .azurewebsites.net)
- 🔒 No SSL support for custom domains
- 💾 Limited to 1 GB storage
- 📊 No metrics or diagnostics
- ⚡ Apps may be stopped after idle period

## Shared Tier (D1)

### Characteristics

- **Low cost** - minimal monthly fee
- **Shared compute** - still runs on shared infrastructure
- **240 CPU minutes/day** quota
- **1 GB disk space**
- **1 GB memory**
- **Maximum 100 apps** per plan
- **Custom domains** supported
- **No SSL/TLS** for custom domains
- **No SLA**

### When to Use

✅ **Use Shared tier when:**
- Low-traffic websites
- Need custom domain without SSL
- Simple development sites
- Budget-constrained projects
- Testing with custom domains

❌ **Don't use Shared when:**
- Production workloads
- Need SSL/TLS
- Require predictable performance
- High-traffic sites

### Code Example

```bash
# Create Shared tier App Service Plan
az appservice plan create \
  --name mySharedPlan \
  --resource-group myResourceGroup \
  --sku SHARED

# Create web app with custom domain (no SSL)
az webapp create \
  --name mySharedApp \
  --resource-group myResourceGroup \
  --plan mySharedPlan

# Add custom domain
az webapp config hostname add \
  --webapp-name mySharedApp \
  --resource-group myResourceGroup \
  --hostname www.mysite.com
```

### Limitations

- ⏱️ 240 CPU minutes per day limit
- 🔒 No SSL for custom domains
- 📊 Limited diagnostics
- 🔄 No auto-scaling
- 💪 Shared compute resources
- 📉 No SLA

## Basic Tier (B1, B2, B3)

### Characteristics

- **Dedicated compute** - your own VM instances
- **No CPU minute quotas**
- **10 GB disk space**
- **Custom domains** with **SSL/TLS** support
- **Manual scaling** up to 3 instances
- **99.95% SLA**
- Three SKUs: B1, B2, B3 (increasing compute power)

### SKU Specifications

| SKU | Cores | Memory | Price (approx) |
|-----|-------|--------|----------------|
| B1 | 1 | 1.75 GB | ~$55/month |
| B2 | 2 | 3.5 GB | ~$110/month |
| B3 | 4 | 7 GB | ~$220/month |

### When to Use

✅ **Use Basic tier when:**
- Production workloads with predictable traffic
- Need SSL/TLS on custom domains
- Small to medium-sized applications
- Don't need auto-scaling
- Budget-conscious production apps
- Development/staging environments

❌ **Don't use Basic when:**
- Need auto-scaling
- Require deployment slots
- Need advanced networking (VNet integration)
- High-availability requirements
- Traffic spikes are common

### Code Example

```bash
# Create Basic B1 App Service Plan
az appservice plan create \
  --name myBasicPlan \
  --resource-group myResourceGroup \
  --sku B1 \
  --location eastus

# Create web app
az webapp create \
  --name myBasicApp \
  --resource-group myResourceGroup \
  --plan myBasicPlan \
  --runtime "DOTNETCORE:8.0"

# Add custom domain with SSL
az webapp config hostname add \
  --webapp-name myBasicApp \
  --resource-group myResourceGroup \
  --hostname www.mysite.com

# Enable HTTPS only
az webapp update \
  --name myBasicApp \
  --resource-group myResourceGroup \
  --https-only true

# Scale manually to 2 instances
az appservice plan update \
  --name myBasicPlan \
  --resource-group myResourceGroup \
  --number-of-workers 2
```

### Typical Use Cases

**Small Business Website:**
- B1 tier for cost optimization
- Custom domain with SSL
- Predictable traffic pattern
- No need for auto-scaling

**Internal Company Portal:**
- B2 tier for better performance
- 2-3 instances for redundancy
- Limited external traffic

## Standard Tier (S1, S2, S3)

### Characteristics

- **Dedicated compute** with better performance
- **50 GB disk space**
- **Auto-scaling** up to 10 instances
- **5 deployment slots** for staging
- **Backup and restore** capabilities
- **Traffic Manager** integration
- **VNet integration** for hybrid connectivity
- **99.95% SLA**

### SKU Specifications

| SKU | Cores | Memory | Price (approx) |
|-----|-------|--------|----------------|
| S1 | 1 | 1.75 GB | ~$70/month |
| S2 | 2 | 3.5 GB | ~$140/month |
| S3 | 4 | 7 GB | ~$280/month |

### Key Features

#### 1. Auto-Scaling

```bash
# Create Standard tier with auto-scaling
az appservice plan create \
  --name myStandardPlan \
  --resource-group myResourceGroup \
  --sku S1

# Configure auto-scale rule (scale based on CPU)
az monitor autoscale create \
  --resource-group myResourceGroup \
  --name autoScaleRule \
  --resource $(az appservice plan show --name myStandardPlan --resource-group myResourceGroup --query id -o tsv) \
  --min-count 2 \
  --max-count 10 \
  --count 2

az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name autoScaleRule \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name autoScaleRule \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

#### 2. Deployment Slots

```bash
# Create staging slot
az webapp deployment slot create \
  --name myStandardApp \
  --resource-group myResourceGroup \
  --slot staging

# Deploy to staging
az webapp deployment source config \
  --name myStandardApp \
  --resource-group myResourceGroup \
  --slot staging \
  --repo-url https://github.com/myrepo/myapp \
  --branch develop \
  --manual-integration

# Swap staging to production (zero downtime)
az webapp deployment slot swap \
  --name myStandardApp \
  --resource-group myResourceGroup \
  --slot staging
```

#### 3. Backup and Restore

```bash
# Configure automatic backups
az webapp config backup create \
  --resource-group myResourceGroup \
  --webapp-name myStandardApp \
  --container-url "https://mystorageaccount.blob.core.windows.net/backups?sp=racwd&st=..." \
  --backup-name mybackup \
  --frequency 1d \
  --retain-one true \
  --retention 30

# Restore from backup
az webapp config backup restore \
  --resource-group myResourceGroup \
  --webapp-name myStandardApp \
  --backup-name mybackup \
  --container-url "https://mystorageaccount.blob.core.windows.net/backups?..."
```

#### 4. VNet Integration

```bash
# Integrate with Virtual Network
az webapp vnet-integration add \
  --name myStandardApp \
  --resource-group myResourceGroup \
  --vnet myVNet \
  --subnet appServiceSubnet
```

### When to Use

✅ **Use Standard tier when:**
- Production applications with variable traffic
- Need auto-scaling capabilities
- Require deployment slots (staging/production)
- Need backup and disaster recovery
- Hybrid connectivity (VNet integration)
- Blue-green deployments
- Traffic spikes are expected

❌ **Don't use Standard when:**
- Need more than 10 instances (use Premium)
- Require private endpoints (use Premium)
- Need App Service Environment (use Isolated)
- Very high-performance requirements

### Typical Use Cases

**E-commerce Website:**
- S2 or S3 tier
- Auto-scaling: 2-10 instances based on traffic
- Deployment slots for safe releases
- VNet integration for backend database

**SaaS Application:**
- S2 tier with auto-scaling
- 5 deployment slots (dev, test, staging, prod, hotfix)
- Automated backups
- Traffic Manager for multi-region

## Premium Tier (P1v2, P2v2, P3v2, P1v3, P2v3, P3v3)

### Characteristics

- **High-performance dedicated compute**
- **250 GB disk space**
- **Auto-scaling** up to 30 instances
- **20 deployment slots**
- **Advanced networking** features
- **Private endpoints** support
- **Enhanced security** features
- **99.95% SLA**
- **V2 and V3 variants** (V3 is newer and faster)

### SKU Specifications

#### Premium V2

| SKU | Cores | Memory | Price (approx) |
|-----|-------|--------|----------------|
| P1v2 | 1 | 3.5 GB | ~$140/month |
| P2v2 | 2 | 7 GB | ~$280/month |
| P3v2 | 4 | 14 GB | ~$560/month |

#### Premium V3

| SKU | Cores | Memory | Price (approx) |
|-----|-------|--------|----------------|
| P1v3 | 2 | 8 GB | ~$200/month |
| P2v3 | 4 | 16 GB | ~$400/month |
| P3v3 | 8 | 32 GB | ~$800/month |

**Note**: Premium V3 offers better price-performance ratio than V2.

### Key Premium Features

#### 1. Private Endpoints

```bash
# Create Premium tier plan
az appservice plan create \
  --name myPremiumPlan \
  --resource-group myResourceGroup \
  --sku P1v3

# Create private endpoint
az network private-endpoint create \
  --name appServicePrivateEndpoint \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet privateEndpointSubnet \
  --private-connection-resource-id $(az webapp show --name myPremiumApp --resource-group myResourceGroup --query id -o tsv) \
  --group-id sites \
  --connection-name appServiceConnection

# Disable public access
az webapp update \
  --name myPremiumApp \
  --resource-group myResourceGroup \
  --set publicNetworkAccess=Disabled
```

#### 2. Advanced Auto-Scaling

```bash
# Scale up to 30 instances
az monitor autoscale create \
  --resource-group myResourceGroup \
  --name premiumAutoScale \
  --resource $(az appservice plan show --name myPremiumPlan --resource-group myResourceGroup --query id -o tsv) \
  --min-count 5 \
  --max-count 30 \
  --count 5

# Multiple scaling rules
# Scale on CPU
az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name premiumAutoScale \
  --condition "Percentage CPU > 75 avg 5m" \
  --scale out 5

# Scale on Memory
az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name premiumAutoScale \
  --condition "Percentage Memory > 80 avg 5m" \
  --scale out 5

# Scale on HTTP Queue Length
az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name premiumAutoScale \
  --condition "Http Queue Length > 100 avg 5m" \
  --scale out 3
```

#### 3. Multiple Deployment Slots

```bash
# Create multiple slots for different environments
az webapp deployment slot create --name myPremiumApp --resource-group myResourceGroup --slot development
az webapp deployment slot create --name myPremiumApp --resource-group myResourceGroup --slot testing
az webapp deployment slot create --name myPremiumApp --resource-group myResourceGroup --slot staging
az webapp deployment slot create --name myPremiumApp --resource-group myResourceGroup --slot hotfix
az webapp deployment slot create --name myPremiumApp --resource-group myResourceGroup --slot canary

# Progressive deployment: canary -> staging -> production
az webapp deployment slot swap --name myPremiumApp --resource-group myResourceGroup --slot canary --target-slot staging
az webapp deployment slot swap --name myPremiumApp --resource-group myResourceGroup --slot staging --target-slot production
```

### When to Use

✅ **Use Premium tier when:**
- Enterprise production applications
- Need private endpoints for security
- High-scale applications (>10 instances)
- Large memory requirements
- Complex deployment strategies (>5 slots)
- High-performance requirements
- Advanced networking features
- Compliance requirements for network isolation

### Typical Use Cases

**Enterprise Web Application:**
- P2v3 or P3v3 tier
- Private endpoints for security
- Auto-scaling: 5-30 instances
- 10+ deployment slots for complex CI/CD

**High-Traffic API:**
- P3v3 tier
- 30 instances maximum
- Private endpoint access
- VNet integration with backend services

## Isolated Tier (I1v2, I2v2, I3v2)

### Characteristics

- **Dedicated App Service Environment (ASE)** v3
- **Completely isolated and dedicated** infrastructure
- **1 TB disk space**
- **Auto-scaling** up to 100 instances
- **20 deployment slots**
- **Private by default** (runs in your VNet)
- **Highest security** and compliance
- **99.95% SLA** (or 99.99% with zone redundancy)
- **Most expensive** tier

### SKU Specifications

| SKU | Cores | Memory | Price (approx) |
|-----|-------|--------|----------------|
| I1v2 | 2 | 8 GB | ~$400/month |
| I2v2 | 4 | 16 GB | ~$800/month |
| I3v2 | 8 | 32 GB | ~$1,600/month |

**Additional Cost**: App Service Environment v3 stamp fee (~$1,000/month)

### App Service Environment (ASE) Features

**Complete Network Isolation:**
- Runs entirely within your VNet
- No public endpoints by default
- Full control over network security groups
- Can use internal load balancer (ILB)

```bash
# Create App Service Environment v3
az appservice ase create \
  --name myASE \
  --resource-group myResourceGroup \
  --vnet-name myVNet \
  --subnet aseSubnet \
  --kind asev3

# Create Isolated tier App Service Plan in ASE
az appservice plan create \
  --name myIsolatedPlan \
  --resource-group myResourceGroup \
  --app-service-environment myASE \
  --sku I1v2 \
  --per-site-scaling

# Create web app in ASE
az webapp create \
  --name myIsolatedApp \
  --resource-group myResourceGroup \
  --plan myIsolatedPlan
```

### When to Use

✅ **Use Isolated tier when:**
- **Regulatory compliance** (HIPAA, PCI DSS, FedRAMP)
- **Complete network isolation** required
- **High-scale enterprise** applications
- **Dedicated infrastructure** for single organization
- **Advanced security** requirements
- **Internal-only applications**
- **Need >30 instances** per app
- **Multi-tenant security** concerns

❌ **Don't use Isolated when:**
- Budget constraints (very expensive)
- Standard network isolation sufficient
- Don't need dedicated environment
- Less than enterprise scale

### Typical Use Cases

**Healthcare Application (HIPAA):**
- I2v2 or I3v2 tier
- Complete network isolation
- PHI data protection
- Compliance requirements

**Financial Services (PCI DSS):**
- Isolated environment
- Internal load balancer
- No public internet access
- Audit and compliance logging

**Government Applications:**
- FedRAMP compliance
- Dedicated infrastructure
- Zone redundancy
- Up to 100 instances

## Detailed Feature Comparison

### Networking Features

| Feature | Free | Shared | Basic | Standard | Premium | Isolated |
|---------|------|--------|-------|----------|---------|----------|
| Custom Domain | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SSL/TLS | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| VNet Integration | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Private Endpoints | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ (native) |
| Hybrid Connections | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Service Endpoints | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Internal Load Balancer | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

#### Networking Features Deep Dive

Understanding the differences between App Service networking options is critical for choosing the right solution:

| Feature | Direction | Purpose | On-Premises Connectivity | Requirements |
|---------|-----------|---------|--------------------------|--------------|
| **Hybrid Connections** | Outbound | Connect App Service to on-premises/external resources | ✅ Direct (via Service Bus Relay) | Hybrid Connection Manager on-premises |
| **VNet Integration** | Outbound | Connect App Service to Azure VNet resources | ⚠️ Requires VPN/ExpressRoute | VNet in same region |
| **Private Endpoints** | Inbound | Allow VNet resources to access App Service privately | ❌ Not for outbound | Premium tier or higher |
| **App Service Environment** | Both | Complete network isolation in your VNet | ⚠️ Requires VPN/ExpressRoute | Isolated tier, dedicated infrastructure |

**Hybrid Connections:**
- Uses Azure Service Bus Relay for secure outbound connections
- Connects over port 443 (HTTPS) - no firewall changes needed
- Ideal for connecting to on-premises databases, APIs, or services
- Requires Hybrid Connection Manager installed on an on-premises Windows server
- No VPN or ExpressRoute required

**VNet Integration:**
- Enables outbound connectivity from App Service to resources in an Azure VNet
- Does NOT provide direct on-premises connectivity (requires VPN Gateway or ExpressRoute)
- Does NOT allow inbound connections from VNet to App Service
- Available in Standard tier and above

**Private Endpoints:**
- Provides a private IP address for your App Service within a VNet
- Used for **inbound** connections - allows resources in VNet to reach App Service
- Does NOT enable App Service to connect outbound to on-premises resources
- Available in Premium tier and above

**App Service Environment (ASE):**
- Fully isolated, dedicated environment running in your VNet
- Supports Internal Load Balancer for complete private access
- Complex to set up and significantly more expensive
- Best for high-security or compliance requirements

### Deployment Features

| Feature | Free | Shared | Basic | Standard | Premium | Isolated |
|---------|------|--------|-------|----------|---------|----------|
| Deployment Slots | ❌ | ❌ | ❌ | 5 | 20 | 20 |
| Git/GitHub Deploy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Azure DevOps | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| FTP/FTPS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Local Git | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| WebDeploy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Monitoring & Management

| Feature | Free | Shared | Basic | Standard | Premium | Isolated |
|---------|------|--------|-------|----------|---------|----------|
| Metrics | Limited | Limited | ✅ | ✅ | ✅ | ✅ |
| Application Insights | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Backup/Restore | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| Cloning | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Diagnostic Logs | Limited | Limited | ✅ | ✅ | ✅ | ✅ |

## Compute Resources by Tier

### Performance Comparison

```
Isolated (I3v2): ████████████████████████████████ 8 cores, 32 GB RAM
Premium (P3v3):  ████████████████████████████████ 8 cores, 32 GB RAM
Premium (P2v3):  ████████████████ 4 cores, 16 GB RAM
Premium (P1v3):  ████████ 2 cores, 8 GB RAM
Standard (S3):   ████████ 4 cores, 7 GB RAM
Standard (S2):   ████ 2 cores, 3.5 GB RAM
Standard (S1):   ██ 1 core, 1.75 GB RAM
Basic (B3):      ████████ 4 cores, 7 GB RAM
Basic (B2):      ████ 2 cores, 3.5 GB RAM
Basic (B1):      ██ 1 core, 1.75 GB RAM
Shared (D1):     █ Shared, 1 GB RAM
Free (F1):       █ Shared, 1 GB RAM
```

### Storage Capacity

```
Isolated:  ████████████████████ 1 TB (1000 GB)
Premium:   █████ 250 GB
Standard:  ██ 50 GB
Basic:     █ 10 GB
Shared:    1 GB
Free:      1 GB
```

## Choosing the Right Tier

### Decision Tree

```
Start
│
├─ Need complete network isolation? (ASE)
│  └─ YES → Isolated
│  └─ NO → Continue
│
├─ Need private endpoints?
│  └─ YES → Premium
│  └─ NO → Continue
│
├─ Need auto-scaling or deployment slots?
│  └─ YES → Standard or Premium
│  └─ NO → Continue
│
├─ Production workload?
│  └─ YES → Basic (minimum)
│  └─ NO → Continue
│
├─ Need custom domain?
│  └─ YES → Shared (no SSL) or Basic (with SSL)
│  └─ NO → Free
```

### Selection Matrix by Use Case

| Use Case | Recommended Tier | Reasoning |
|----------|------------------|-----------|
| **Learning/POC** | Free | No cost, full API support |
| **Personal Blog** | Free or Shared | Low traffic, minimal cost |
| **Small Business Site** | Basic (B1/B2) | Custom domain + SSL, predictable cost |
| **Production Web App** | Standard (S1/S2) | Auto-scale, deployment slots, VNet |
| **E-commerce Site** | Standard (S2/S3) or Premium | High traffic, scaling, slots |
| **Enterprise SaaS** | Premium (P2v3/P3v3) | High scale, private endpoints |
| **High-Compliance App** | Isolated | Complete isolation, compliance |
| **Microservices** | Premium or Isolated | Multiple apps, advanced networking |
| **API Gateway** | Standard or Premium | Auto-scale, high throughput |
| **Internal Portal** | Basic or Standard | VNet integration, moderate traffic |

## Scaling Options

### Vertical Scaling (Scale Up/Down)

Change to a different tier or SKU:

```bash
# Scale up from Basic to Standard
az appservice plan update \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --sku S1

# Scale up within same tier
az appservice plan update \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --sku S3
```

### Horizontal Scaling (Scale Out/In)

Add or remove instances:

```bash
# Manual scale out
az appservice plan update \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --number-of-workers 5

# Auto-scale (Standard tier and above)
az monitor autoscale create \
  --resource-group myResourceGroup \
  --name myAutoScaleRule \
  --resource $(az appservice plan show --name myAppServicePlan --resource-group myResourceGroup --query id -o tsv) \
  --min-count 2 \
  --max-count 10 \
  --count 3
```

### Scaling Limits by Tier

| Tier | Manual Scaling | Auto-Scaling | Max Instances |
|------|----------------|--------------|---------------|
| Free | ❌ | ❌ | 1 |
| Shared | ❌ | ❌ | 1 |
| Basic | ✅ | ❌ | 3 |
| Standard | ✅ | ✅ | 10 |
| Premium | ✅ | ✅ | 30 |
| Isolated | ✅ | ✅ | 100 |

## Cost Considerations

### Monthly Cost Estimates (USD, East US)

**Development/Testing:**
- Free: $0
- Shared (D1): ~$10
- Basic (B1): ~$55

**Production (Small to Medium):**
- Basic (B2): ~$110
- Standard (S1): ~$70
- Standard (S2): ~$140

**Production (Large Scale):**
- Premium (P1v3): ~$200
- Premium (P2v3): ~$400
- Premium (P3v3): ~$800

**Enterprise/Isolated:**
- Isolated (I1v2): ~$1,400 (includes ASE)
- Isolated (I2v2): ~$1,800
- Isolated (I3v2): ~$2,600

### Cost Optimization Strategies

1. **Use Appropriate Tier for Environment**
   ```bash
   # Development
   az appservice plan create --sku B1
   
   # Production
   az appservice plan create --sku P1v3
   ```

2. **Share App Service Plans**
   ```bash
   # Multiple apps can share one plan
   az webapp create --plan sharedPlan --name app1
   az webapp create --plan sharedPlan --name app2
   az webapp create --plan sharedPlan --name app3
   ```

3. **Use Auto-Scaling Effectively**
   ```bash
   # Scale down during off-hours
   az monitor autoscale rule create \
     --condition "Time hour < 8 or hour > 18" \
     --scale to 1
   ```

4. **Reserved Instances** (Premium/Isolated)
   - 1-year or 3-year commitment
   - Up to 55% savings
   - Available for Premium v2/v3 and Isolated

## Changing Between Tiers

### Upgrade Path

```bash
# Free → Shared
az appservice plan update --name myPlan --resource-group myRG --sku SHARED

# Shared → Basic
az appservice plan update --name myPlan --resource-group myRG --sku B1

# Basic → Standard
az appservice plan update --name myPlan --resource-group myRG --sku S1

# Standard → Premium
az appservice plan update --name myPlan --resource-group myRG --sku P1v3

# Note: Cannot directly move to Isolated (requires ASE)
```

### Upgrade Considerations

- ✅ **Upgrading** is always supported
- ✅ No downtime during tier changes
- ✅ All settings and data preserved
- ⚠️ Cannot downgrade from Isolated to other tiers
- ⚠️ Some features lost when downgrading (slots, VNet, etc.)

### Downgrade Restrictions

```bash
# Before downgrading from Standard to Basic:
# 1. Remove deployment slots
az webapp deployment slot list --name myApp --resource-group myRG
az webapp deployment slot delete --name myApp --resource-group myRG --slot staging

# 2. Disable auto-scale
az monitor autoscale delete --name myAutoScale --resource-group myRG

# 3. Remove VNet integration
az webapp vnet-integration remove --name myApp --resource-group myRG

# 4. Now downgrade
az appservice plan update --name myPlan --resource-group myRG --sku B1
```

## Exam Questions and Scenarios

### Question 1: Auto-Scaling Requirement

**Scenario:** Your web application experiences high traffic during business hours (8 AM - 6 PM) and minimal traffic at night. You need to automatically scale instances based on CPU usage.

**Question:** What is the minimum tier you need?

**Answer:** **Standard (S1)**

**Reasoning:**
- ✅ Standard tier supports auto-scaling
- ❌ Basic tier only supports manual scaling
- ✅ Can configure time-based and metric-based scaling
- ✅ Cost-effective for this scenario

### Question 2: Deployment Slots

**Scenario:** Your team needs to deploy updates to a staging environment, test them, and then swap to production with zero downtime. You need at least 3 slots (dev, staging, production).

**Question:** Which tier should you choose?

**Answer:** **Standard tier (minimum)**

**Reasoning:**
- ✅ Standard provides 5 deployment slots
- ✅ Supports slot swapping for zero-downtime deployments
- ❌ Basic doesn't support deployment slots
- ⚠️ Premium provides 20 slots if you need more

### Question 3: Network Isolation

**Scenario:** Your company's security policy requires that the web application must not be accessible from the public internet and must run entirely within your private network.

**Question:** Which tier and configuration do you need?

**Answer:** **Isolated tier with App Service Environment**

**Reasoning:**
- ✅ Isolated tier runs in dedicated ASE within your VNet
- ✅ Can use Internal Load Balancer (no public endpoints)
- ✅ Complete network isolation
- ⚠️ Premium with private endpoints provides partial isolation but not complete

### Question 4: On-Premises Database Connectivity

**Scenario:** You are deploying a web application to Azure App Service that needs to connect to an on-premises SQL Server database through a secure connection. The on-premises network cannot be exposed to the internet.

**Question:** Which networking feature should you use?

**Options:**

1. ❌ **App Service Environment**
   - **Incorrect**: App Service Environment provides network isolation but requires significant infrastructure changes and VPN/ExpressRoute setup for on-premises connectivity, making it overly complex for this scenario.

2. ✅ **Hybrid Connections (Correct Answer)**
   - **Correct**: Hybrid Connections provide secure connectivity to on-premises resources without requiring VPN or exposing the on-premises network to the internet, using an outbound connection over port 443 through Service Bus Relay.

3. ❌ **Private Endpoints**
   - **Incorrect**: Private Endpoints are used for inbound connections to App Service from a VNet, not for App Service to connect outbound to on-premises resources.

4. ❌ **Virtual Network Integration**
   - **Incorrect**: Virtual Network Integration enables outbound connections from App Service to Azure VNet resources but doesn't directly provide connectivity to on-premises resources without additional VPN setup.

**Key Points:**
- Hybrid Connections use an outbound HTTPS connection (port 443) via Azure Service Bus Relay
- No firewall changes needed on the on-premises network
- Requires installing Hybrid Connection Manager on an on-premises server
- Works with Standard, Premium, and Isolated tiers

### Question 5: Cost Optimization

**Scenario:** You have 10 small web applications that together use less than 4 GB of memory and 2 CPU cores. They all have similar traffic patterns.

**Question:** What's the most cost-effective approach?

**Answer:** **Single Standard or Premium plan shared by all 10 apps**

**Reasoning:**
- ✅ All apps can share one App Service Plan
- ✅ One S2 or P1v3 plan cheaper than 10 separate B1 plans
- ✅ Combined resources sufficient for all apps
- 💰 Significant cost savings

### Question 5: Securing Custom Domain with HTTPS

**Scenario:** You have an Azure App Service web app that requires a custom domain name. You have already verified domain ownership and created a CNAME record pointing to the web app.

**Question:** What should you do next to secure the custom domain with HTTPS?

**Options:**

1. ❌ Configure the web app to use HTTPS only in the TLS/SSL settings
   - **Incorrect**: The 'HTTPS Only' setting forces HTTPS but requires a certificate to be already bound to the custom domain, so this cannot be the immediate next step.

2. ✅ Add a TLS/SSL binding using either an App Service certificate or an uploaded certificate
   - **Correct**: After configuring the custom domain, you must create a TLS/SSL binding by either purchasing an App Service certificate, uploading your own certificate, or using a free App Service managed certificate to enable HTTPS.

3. ❌ Create an Azure Key Vault to store the SSL certificate
   - **Incorrect**: While Key Vault can store certificates, the immediate next step is to bind a certificate to the custom domain, whether it's stored in Key Vault or uploaded directly.

4. ❌ Enable HTTPS redirect in the custom domain settings
   - **Incorrect**: HTTPS redirect can only be enabled after a TLS/SSL certificate is bound to the custom domain; it's not the next step but rather a subsequent configuration.

## Custom Domains and TLS/SSL Certificates

### Overview

Securing your Azure App Service web app with HTTPS requires proper configuration of custom domains and TLS/SSL certificates. The process involves several steps that must be completed in the correct order.

### Steps to Secure a Custom Domain with HTTPS

1. **Verify Domain Ownership** - Prove you own the domain
2. **Create DNS Records** - Add CNAME or A record pointing to your web app
3. **Add Custom Domain** - Configure the custom domain in App Service
4. **Add TLS/SSL Binding** - Bind a certificate to enable HTTPS
5. **Enable HTTPS Only** - Force all traffic to use HTTPS (optional)

### Certificate Options

| Certificate Type | Description | Cost | Management |
|-----------------|-------------|------|------------|
| **Free App Service Managed Certificate** | Auto-provisioned by Azure | Free | Fully managed |
| **App Service Certificate** | Purchased through Azure | Paid | Managed renewal |
| **Uploaded Certificate** | Your own certificate (e.g., from CA) | Varies | Manual renewal |
| **Key Vault Certificate** | Certificate stored in Azure Key Vault | Varies | Centralized management |

### Adding a TLS/SSL Binding

```bash
# Step 1: Add custom domain (after DNS verification)
az webapp config hostname add \
  --webapp-name myWebApp \
  --resource-group myResourceGroup \
  --hostname www.mydomain.com

# Step 2: Create a free managed certificate
az webapp config ssl create \
  --name myWebApp \
  --resource-group myResourceGroup \
  --hostname www.mydomain.com

# Step 3: Bind the certificate to the custom domain
az webapp config ssl bind \
  --name myWebApp \
  --resource-group myResourceGroup \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI

# Step 4: (Optional) Enable HTTPS only
az webapp update \
  --name myWebApp \
  --resource-group myResourceGroup \
  --https-only true
```

### SSL/TLS Binding Types

| Binding Type | Description | Use Case |
|--------------|-------------|----------|
| **SNI SSL** | Server Name Indication - modern standard | Most applications |
| **IP SSL** | Dedicated IP address for SSL | Legacy clients that don't support SNI |

### Tier Requirements for Custom Domains and SSL

| Feature | Free | Shared | Basic | Standard+ |
|---------|------|--------|-------|----------|
| Custom Domain | ❌ | ✅ | ✅ | ✅ |
| SSL/TLS Certificate | ❌ | ❌ | ✅ | ✅ |
| Free Managed Certificate | ❌ | ❌ | ✅ | ✅ |

### Common Mistakes

⚠️ **Wrong Order of Operations:**
- Cannot enable "HTTPS Only" before binding a certificate
- Cannot bind a certificate before adding the custom domain
- DNS records must be configured before domain verification

⚠️ **Tier Limitations:**
- Free tier does not support custom domains
- Shared tier supports custom domains but NOT SSL/TLS
- Basic tier and above support both custom domains and SSL/TLS

## Best Practices

### General Best Practices

1. **Start Small, Scale Up**
   ```bash
   # Begin with lower tier
   az appservice plan create --sku B1
   
   # Monitor and upgrade as needed
   az appservice plan update --sku S1
   ```

2. **Use Deployment Slots** (Standard+)
   ```bash
   # Always test in staging before production
   az webapp deployment slot create --slot staging
   az webapp deployment slot swap --slot staging
   ```

3. **Enable Auto-Scaling** (Standard+)
   ```bash
   # Configure based on metrics
   az monitor autoscale create \
     --min-count 2 \
     --max-count 10 \
     --condition "Percentage CPU > 70"
   ```

4. **Monitor Performance**
   ```bash
   # Use Application Insights
   az monitor app-insights component create \
     --app myAppInsights \
     --resource-group myResourceGroup \
     --location eastus
   
   az webapp config appsettings set \
     --name myWebApp \
     --resource-group myResourceGroup \
     --settings APPINSIGHTS_INSTRUMENTATIONKEY=<key>
   ```

5. **Implement Health Checks**
   ```bash
   # Configure health check endpoint
   az webapp config set \
     --name myWebApp \
     --resource-group myResourceGroup \
     --health-check-path "/health"
   ```

### Security Best Practices

1. **Always Use HTTPS** (Basic+)
   ```bash
   az webapp update \
     --name myWebApp \
     --resource-group myResourceGroup \
     --https-only true
   ```

2. **Use Managed Identity**
   ```bash
   az webapp identity assign \
     --name myWebApp \
     --resource-group myResourceGroup
   ```

3. **Enable Private Endpoints** (Premium+)
   ```bash
   az network private-endpoint create \
     --name appPrivateEndpoint \
     --resource-group myResourceGroup \
     --vnet-name myVNet \
     --subnet privateSubnet
   ```

4. **Restrict Access with IP Rules**
   ```bash
   az webapp config access-restriction add \
     --name myWebApp \
     --resource-group myResourceGroup \
     --rule-name "Office IP" \
     --action Allow \
     --ip-address 203.0.113.0/24 \
     --priority 100
   ```

### Cost Optimization Best Practices

1. **Share Plans Across Apps**
2. **Use Reserved Instances** (1-3 year commitment)
3. **Implement Auto-Scaling** with appropriate min/max
4. **Stop Dev/Test Apps** when not in use
5. **Monitor and Right-Size** regularly

## References

- [App Service pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/windows/)
- [App Service plan overview](https://learn.microsoft.com/en-us/azure/app-service/overview-hosting-plans)
- [Scale up an app in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/manage-scale-up)
- [Get started with autoscale in Azure](https://learn.microsoft.com/en-us/azure/azure-monitor/autoscale/autoscale-get-started)
- [Set up staging environments in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots)
- [App Service Environment overview](https://learn.microsoft.com/en-us/azure/app-service/environment/overview)
