# Azure Container Apps - Pricing

## Table of Contents

- [Overview](#overview)
- [Pricing Plans Comparison](#pricing-plans-comparison)
- [Consumption Plan (Pay-as-you-go)](#consumption-plan-pay-as-you-go)
  - [1. Resource Consumption](#1-resource-consumption)
  - [2. Request Charges](#2-request-charges)
- [Dedicated Plan (Workload Profiles)](#dedicated-plan-workload-profiles)
  - [Workload Profile Types](#workload-profile-types)
  - [Dedicated Plan Pricing](#dedicated-plan-pricing)
  - [When to Choose Dedicated Plan](#when-to-choose-dedicated-plan)
- [Free Grant](#free-grant)
- [Pricing Tiers Comparison](#pricing-tiers-comparison)
- [Cost Optimization Tips](#cost-optimization-tips)
- [Scaling Configuration](#scaling-configuration)
- [Use Case Cost Examples](#use-case-cost-examples)
  - [Example 1: Small API (Dev/Test)](#example-1-small-api-devtest)
  - [Example 2: Production Web App](#example-2-production-web-app)
  - [Example 3: Event-Driven Processing](#example-3-event-driven-processing)
- [Additional Costs](#additional-costs)
- [Key Benefits](#key-benefits)
- [Additional Resources](#additional-resources)
- [Related Topics](#related-topics)

## Overview

Azure Container Apps offers **two pricing models**: 

1. **Consumption Plan** - Pay-as-you-go based on actual resource usage (vCPU-seconds, GiB-seconds, requests)
2. **Dedicated Plan (Workload Profiles)** - Reserved capacity with predictable costs and enhanced performance

This document provides detailed information about both pricing models, cost optimization strategies, and real-world cost examples.

## Pricing Plans Comparison

| Feature | Consumption Plan | Dedicated Plan (Workload Profiles) |
|---------|------------------|-------------------------------------|
| **Pricing Model** | Pay per second of usage | Fixed monthly cost per profile |
| **Billing** | vCPU-seconds + GiB-seconds + requests | Per workload profile instance |
| **Scale to Zero** | ✅ Yes | ❌ No (always running) |
| **Free Grant** | ✅ Yes (180K vCPU-sec, 360K GiB-sec, 2M requests) | ❌ No |
| **Min vCPU/Memory** | 0.25 vCPU / 0.5 GiB | 4 vCPU / 8 GiB (Dedicated-D4) |
| **Max vCPU/Memory** | 4 vCPU / 8 GiB | 32 vCPU / 128 GiB (Dedicated-D32) |
| **Resource Isolation** | Shared infrastructure | Dedicated compute nodes |
| **Network Performance** | Standard | Enhanced |
| **SLA** | 99.95% | 99.95% |
| **Cost Predictability** | Variable (usage-based) | Fixed (reserved capacity) |
| **Best For** | Variable workloads, dev/test | Predictable workloads, high-performance needs |
| **Starting Price** | ~$0/month (with free grant) | ~$216/month (Dedicated-D4) |

## Consumption Plan (Pay-as-you-go)

### 1. Resource Consumption

**vCPU Charges:**
- **Price**: ~$0.000024 per vCPU per second
- **Monthly estimate (1 vCPU)**: ~$17.28/month (730 hours)
- Billed per second for actual usage
- Minimum allocation: 0.25 vCPU
- Maximum per container: 4 vCPU

**Memory Charges:**
- **Price**: ~$0.000003 per GiB per second
- **Monthly estimate (1 GiB)**: ~$2.16/month (730 hours)
- Billed per second for actual usage
- Minimum allocation: 0.5 GiB
- Maximum per container: 8 GiB

**Example Cost Calculation:**
```
Container with 1 vCPU and 2 GiB memory running 24/7:
- vCPU cost: 1 × $0.000024 × 2,592,000 seconds = ~$62.21/month
- Memory cost: 2 × $0.000003 × 2,592,000 seconds = ~$15.55/month
- Total: ~$77.76/month
```

### 2. Request Charges

- **Price**: $0.40 per million requests
- First 2 million requests per month are **free**
- Counts HTTP requests and scale operations

**Example:**
```
10 million requests per month:
- First 2M: Free
- Remaining 8M: 8 × $0.40 = $3.20/month
```

## Dedicated Plan (Workload Profiles)

The **Dedicated Plan** (also called Workload Profiles environment) provides reserved, dedicated compute capacity for your container apps. Unlike the Consumption plan where you pay per second of usage, the Dedicated plan charges a **fixed monthly cost** for pre-allocated compute nodes.

### Key Characteristics

- **Reserved Capacity**: Pay for dedicated compute nodes whether you use them or not
- **Enhanced Performance**: Dedicated hardware with better network throughput
- **No Scale-to-Zero**: Nodes are always running, cannot scale to zero
- **Higher Resource Limits**: Up to 32 vCPU and 128 GiB memory per container
- **No Free Grant**: Free monthly grants don't apply to dedicated plan
- **Predictable Costs**: Fixed monthly cost regardless of actual usage

### Workload Profile Types

Azure Container Apps offers multiple workload profile SKUs with different resource allocations:

| Profile Type | vCPU | Memory | Price/Month* | Use Case |
|--------------|------|--------|--------------|----------|
| **Dedicated-D4** | 4 vCPU | 8 GiB | ~$216 | Small production workloads |
| **Dedicated-D8** | 8 vCPU | 16 GiB | ~$432 | Medium production workloads |
| **Dedicated-D16** | 16 vCPU | 32 GiB | ~$864 | Large production workloads |
| **Dedicated-D32** | 32 vCPU | 128 GiB | ~$1,728 | High-performance workloads |
| **Dedicated-E4** | 4 vCPU | 32 GiB | ~$259 | Memory-intensive workloads |
| **Dedicated-E8** | 8 vCPU | 64 GiB | ~$518 | Memory-intensive workloads |
| **Dedicated-E16** | 16 vCPU | 128 GiB | ~$1,037 | High-memory workloads |

*Prices are approximate and vary by region. Based on East US pricing as of 2025.

### Dedicated Plan Pricing

#### D-Series (Compute-Optimized)
```
Dedicated-D4: 4 vCPU, 8 GiB
- Base cost: ~$216/month per node
- Suitable for: General-purpose applications

Dedicated-D8: 8 vCPU, 16 GiB
- Base cost: ~$432/month per node
- Suitable for: Higher throughput applications

Dedicated-D16: 16 vCPU, 32 GiB
- Base cost: ~$864/month per node
- Suitable for: CPU-intensive workloads

Dedicated-D32: 32 vCPU, 128 GiB
- Base cost: ~$1,728/month per node
- Suitable for: Maximum performance requirements
```

#### E-Series (Memory-Optimized)
```
Dedicated-E4: 4 vCPU, 32 GiB (8:1 memory-to-vCPU ratio)
- Base cost: ~$259/month per node
- Suitable for: In-memory caching, data processing

Dedicated-E8: 8 vCPU, 64 GiB
- Base cost: ~$518/month per node
- Suitable for: Large in-memory datasets

Dedicated-E16: 16 vCPU, 128 GiB
- Base cost: ~$1,037/month per node
- Suitable for: High-memory databases, analytics
```

### Billing Model

Unlike Consumption plan's per-second billing:
- **Fixed cost per node per month** regardless of utilization
- **Scale by adding nodes**: Add more profile instances to handle more load
- **No request charges**: HTTP requests are included
- **24/7 charges**: Billed for full month even if containers are idle

**Example Cost Calculation:**
```
2 × Dedicated-D8 nodes (8 vCPU, 16 GiB each):
- 2 × $432 = $864/month
- Total capacity: 16 vCPU, 32 GiB
- Cost is the same whether you use 10% or 100% of capacity
```

### When to Choose Dedicated Plan

#### ✅ Choose Dedicated Plan When:

1. **Predictable, Consistent Workloads**
   - Applications running 24/7 at steady load
   - Cost is more predictable than consumption billing
   
2. **High Resource Requirements**
   - Need more than 4 vCPU or 8 GiB per container
   - Consumption plan limits are insufficient
   
3. **Enhanced Performance Needs**
   - Require dedicated compute resources
   - Need consistent, predictable performance
   - Higher network throughput requirements
   
4. **Resource Isolation**
   - Regulatory compliance requiring dedicated infrastructure
   - Avoid noisy neighbor issues
   
5. **Cost Optimization at Scale**
   - High-utilization scenarios where fixed cost < consumption cost
   - Example: App using 4 vCPU + 8 GiB 24/7 costs ~$78/month on consumption vs $216/month dedicated (but with reserved capacity)

#### ❌ Choose Consumption Plan When:

1. **Variable or Intermittent Workloads**
   - Event-driven processing
   - Dev/test environments
   - Applications with idle periods
   
2. **Scale-to-Zero Requirements**
   - Need to eliminate costs during idle times
   - Occasional batch processing
   
3. **Smaller Resource Needs**
   - 0.25-4 vCPU, 0.5-8 GiB is sufficient
   
4. **Unpredictable Traffic**
   - Spiky or seasonal workloads
   - Can't estimate consistent load

### Cost Comparison Example

**Scenario**: Web API running 24/7 with 2 replicas at 2 vCPU, 4 GiB each

#### Consumption Plan:
```
2 replicas × 2 vCPU × $0.000024 × 2,592,000 sec = $249.98
2 replicas × 4 GiB × $0.000003 × 2,592,000 sec = $62.21
Total: ~$312/month (plus request charges)
```

#### Dedicated Plan (1 × D8 node):
```
1 × Dedicated-D8 (8 vCPU, 16 GiB) = $432/month
Total capacity available: 8 vCPU, 16 GiB
You can run 2 replicas (2 vCPU, 4 GiB each) = 4 vCPU, 8 GiB used
Remaining capacity: 4 vCPU, 8 GiB for other apps or scaling
```

**Analysis**: Consumption is cheaper (~$312 vs $432), but Dedicated provides:
- Reserved capacity for burst scaling
- Consistent performance
- Can run additional apps on same node

### Mixed Workload Strategy

You can combine both plans in the same environment:
- **Dedicated Plan**: For core, steady-state workloads
- **Consumption Plan**: For variable, event-driven workloads

**Example Architecture:**
```
Environment with Workload Profiles:
├─ Dedicated-D8 node ($432/month)
│  └─ Production API (steady 24/7 load)
│
└─ Consumption Plan (pay-as-you-go)
   ├─ Background job processor (scale-to-zero)
   └─ Dev/test applications
```

## Free Grant

Azure Container Apps includes a **monthly free grant** per subscription:

- **180,000 vCPU-seconds** (~50 hours of 1 vCPU)
- **360,000 GiB-seconds** (~100 hours of 1 GiB memory)
- **2 million requests**

## Pricing Tiers Comparison

Azure Container Apps operates on a **single consumption-based pricing model** (no traditional "tiers" like Basic/Standard/Premium), but understanding resource allocation levels helps estimate costs:

### Resource Allocation Options

| Resource Type | Minimum | Maximum | Price | Free Grant |
|---------------|---------|---------|-------|------------|
| **vCPU** | 0.25 vCPU | 4 vCPU per container | $0.000024/second | 180,000 vCPU-seconds/month (~50 hours of 1 vCPU) |
| **Memory** | 0.5 GiB | 8 GiB per container | $0.000003/GiB/second | 360,000 GiB-seconds/month (~100 hours of 1 GiB) |
| **Requests** | - | Unlimited | $0.40/million | 2 million/month |
| **Replicas** | 0 (scale-to-zero) | 300 per app | Included in compute costs | N/A |

### Common Configuration Tiers (Estimated Monthly Costs)

#### Tier 1: Minimal (Dev/Test)
**Configuration:**
- 0.25 vCPU, 0.5 GiB memory
- Min replicas: 0 (scale-to-zero)
- Max replicas: 3
- Usage: 8 hours/day, 5 days/week (~160 hours/month)
- Requests: 500K/month

**Monthly Cost:** ~$0-5/month
- Often covered entirely by free grant
- Ideal for: Development, testing, personal projects

#### Tier 2: Small Production
**Configuration:**
- 0.5 vCPU, 1 GiB memory
- Min replicas: 1
- Max replicas: 5
- Usage: 24/7 with 2 average replicas
- Requests: 3 million/month

**Monthly Cost:** ~$48/month
- vCPU: 2 × 0.5 × $0.000024 × 2,592,000 sec = $62.21
- Memory: 2 × 1 × $0.000003 × 2,592,000 sec = $15.55
- Requests: (3M - 2M) × $0.40 = $0.40
- Subtotal: $78.16 - free grant ≈ **$48/month**
- Ideal for: Small production APIs, internal tools

#### Tier 3: Medium Production
**Configuration:**
- 1 vCPU, 2 GiB memory
- Min replicas: 2
- Max replicas: 10
- Usage: 24/7 with 3 average replicas
- Requests: 10 million/month

**Monthly Cost:** ~$237/month
- vCPU: 3 × 1 × $0.000024 × 2,592,000 sec = $186.62
- Memory: 3 × 2 × $0.000003 × 2,592,000 sec = $46.66
- Requests: (10M - 2M) × $0.40 = $3.20
- Total: **$236.48/month**
- Ideal for: Production web apps, APIs with moderate traffic

#### Tier 4: Large Production
**Configuration:**
- 2 vCPU, 4 GiB memory
- Min replicas: 3
- Max replicas: 20
- Usage: 24/7 with 5 average replicas
- Requests: 50 million/month

**Monthly Cost:** ~$1,416/month
- vCPU: 5 × 2 × $0.000024 × 2,592,000 sec = $622.08
- Memory: 5 × 4 × $0.000003 × 2,592,000 sec = $155.52
- Requests: (50M - 2M) × $0.40 = $19.20
- Total: **$1,796.80/month**
- Ideal for: High-traffic applications, enterprise workloads

#### Tier 5: High-Performance/Enterprise
**Configuration:**
- 4 vCPU, 8 GiB memory
- Min replicas: 5
- Max replicas: 50
- Usage: 24/7 with 10 average replicas
- Requests: 200 million/month

**Monthly Cost:** ~$5,594/month
- vCPU: 10 × 4 × $0.000024 × 2,592,000 sec = $2,488.32
- Memory: 10 × 8 × $0.000003 × 2,592,000 sec = $622.08
- Requests: (200M - 2M) × $0.40 = $79.20
- Total: **$3,189.60/month**
- Ideal for: Mission-critical applications, high-scale services

### Workload Pattern Comparison

| Workload Type | Configuration | Scale Strategy | Est. Monthly Cost |
|---------------|---------------|----------------|-------------------|
| **Dev/Test API** | 0.25 vCPU, 0.5 GiB | Scale to zero, intermittent use | $0-10 |
| **Event-Driven Processor** | 1 vCPU, 2 GiB | Scale to zero, burst processing | $10-50 |
| **Low-Traffic Web App** | 0.5 vCPU, 1 GiB | Min 1 replica | $40-80 |
| **Production API** | 1 vCPU, 2 GiB | Min 2, avg 3 replicas | $200-300 |
| **High-Traffic Web App** | 2 vCPU, 4 GiB | Min 3, avg 5 replicas | $700-1,000 |
| **Enterprise Microservices** | 2-4 vCPU, 4-8 GiB | Min 5, avg 10+ replicas | $1,500-5,000+ |

### Key Pricing Factors

1. **Resource Allocation**: Higher vCPU and memory = higher costs
2. **Replica Count**: More replicas = proportionally higher costs
3. **Uptime**: 24/7 vs scale-to-zero dramatically affects costs
4. **Request Volume**: Minimal impact after 2M free requests
5. **Scaling Efficiency**: Proper min/max settings optimize costs

### Comparison with Other Azure Compute Services

| Service | Pricing Model | Min Cost | Best For |
|---------|---------------|----------|----------|
| **Container Apps** | Per-second consumption | $0 (scale-to-zero) | Modern cloud-native apps, microservices |
| **App Service Basic** | Fixed tier | ~$55/month | Traditional web apps, steady workloads |
| **Azure Functions Consumption** | Per-execution + duration | $0 (1M free) | Event-driven, serverless functions |
| **AKS (Kubernetes)** | Per node + management | ~$73/month (1 node) | Complex orchestration, full control |
| **Container Instances** | Per-second | $0 | Simple containers, batch jobs |

## Cost Optimization Tips

1. **Use scale-to-zero**: Containers that aren't processing requests don't incur compute charges
2. **Right-size resources**: Allocate only what you need (min 0.25 vCPU, 0.5 GiB)
3. **Enable autoscaling**: Scale based on HTTP traffic, CPU, memory, or custom metrics
4. **Use replicas efficiently**: Set appropriate min/max replica counts
5. **Leverage free grants**: Small dev/test workloads may run within free tier
6. **Monitor usage**: Use Azure Cost Management to track spending

## Scaling Configuration

```bash
az containerapp create \
  --name myapp \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image myimage:latest \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```

**Cost Impact:**
- Min replicas = 0: Pay only when serving traffic (scale-to-zero)
- Min replicas > 0: Pay for minimum instances 24/7

## Use Case Cost Examples

### Example 1: Small API (Dev/Test)
```
Configuration:
- 0.25 vCPU, 0.5 GiB memory
- Scale to zero when idle
- 8 hours/day active, 5 days/week (~160 hours/month)
- 500K requests/month

Cost:
- vCPU: 0.25 × $0.000024 × 576,000 sec = $3.46
- Memory: 0.5 × $0.000003 × 576,000 sec = $0.86
- Requests: Free (under 2M)
Total: ~$4.32/month (after free grant, may be $0)
```

### Example 2: Production Web App
```
Configuration:
- 1 vCPU, 2 GiB memory
- Min 2 replicas, max 10 replicas
- Average 3 replicas running 24/7
- 5 million requests/month

Cost:
- vCPU: 3 × 1 × $0.000024 × 2,592,000 sec = $186.62
- Memory: 3 × 2 × $0.000003 × 2,592,000 sec = $46.66
- Requests: (5M - 2M) × $0.40 = $1.20
Total: ~$234.48/month
```

### Example 3: Event-Driven Processing
```
Configuration:
- 2 vCPU, 4 GiB memory
- Scale to zero
- Processes events 2 hours/day (~60 hours/month)
- 100K requests/month

Cost:
- vCPU: 2 × $0.000024 × 216,000 sec = $10.37
- Memory: 4 × $0.000003 × 216,000 sec = $2.59
- Requests: Free
Total: ~$12.96/month
```

## Additional Costs

**Not included in Container Apps pricing:**
- **Networking**: Virtual network integration, private endpoints
- **Storage**: Persistent storage volumes (Azure Files, etc.)
- **Container Registry**: Azure Container Registry costs
- **Observability**: Log Analytics workspace data ingestion and retention
- **Custom domains**: Free, but SSL certificates may have costs
- **Load testing**: Separate Azure Load Testing service costs

## Key Benefits

✅ **Pay per second**: No rounding to hours  
✅ **Scale to zero**: No cost when idle  
✅ **No infrastructure management**: No VM costs  
✅ **Free grant**: Good for development and small workloads  
✅ **Predictable pricing**: Easy to estimate based on usage  
✅ **No minimum commitment**: True consumption model  

## Additional Resources

- [Azure Container Apps Pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/)
- [Billing in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/billing)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Azure Cost Management](https://azure.microsoft.com/en-us/services/cost-management/)

## Related Topics

- [Azure Container Apps Deployment Methods](./aca-deployment-from-source.md)
- [Azure Container Apps Overview](./azure-container-apps-overview.md)
- Cost optimization strategies
- Scaling and performance tuning
