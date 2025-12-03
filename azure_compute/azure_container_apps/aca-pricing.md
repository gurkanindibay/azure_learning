# Azure Container Apps - Pricing

## Table of Contents

- [Overview](#overview)
- [Consumption Plan (Pay-as-you-go)](#consumption-plan-pay-as-you-go)
  - [1. Resource Consumption](#1-resource-consumption)
  - [2. Request Charges](#2-request-charges)
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

Azure Container Apps uses a **consumption-based pricing model** that charges only for the resources you use. This document provides detailed information about pricing, cost optimization strategies, and real-world cost examples.

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

## Free Grant

Azure Container Apps includes a **monthly free grant** per subscription:

- **180,000 vCPU-seconds** (~50 hours of 1 vCPU)
- **360,000 GiB-seconds** (~100 hours of 1 GiB memory)
- **2 million requests**

## Pricing Tiers Comparison

| Component | Price | Free Grant | Billing Unit |
|-----------|-------|------------|-------------|
| **vCPU** | $0.000024/second | 180,000 vCPU-seconds/month | Per second |
| **Memory** | $0.000003/GiB/second | 360,000 GiB-seconds/month | Per second |
| **Requests** | $0.40/million | 2 million/month | Per request |

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
