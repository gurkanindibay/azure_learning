# Azure Container Instances (ACI) - Pricing Tiers

## Overview

Azure Container Instances (ACI) uses a **pay-per-use** pricing model rather than traditional pricing tiers. You are charged based on the resources allocated to your container instances and the duration they run.

## Pricing Model

### Resource-Based Pricing

ACI charges are calculated based on:

1. **vCPU (Virtual CPU)**
   - Charged per second of usage
   - Measured in vCPU-seconds
   - Minimum allocation: 0.1 vCPU
   - Maximum allocation: 4 vCPUs per container group

2. **Memory (RAM)**
   - Charged per second of usage
   - Measured in GB-seconds
   - Minimum allocation: 0.1 GB
   - Maximum allocation: 16 GB per container group

3. **Duration**
   - Billed per second
   - Billing starts when the first container's image begins to pull
   - Billing stops when the container group terminates

## Container Types

### Linux Containers

**Standard Pricing:**
- **vCPU**: ~$0.0000125 per vCPU-second (~$0.045 per vCPU-hour)
- **Memory**: ~$0.0000014 per GB-second (~$0.005 per GB-hour)

**Example Calculation (Linux):**
- 1 vCPU, 1 GB RAM, running for 1 hour
- vCPU cost: 1 × 3600 seconds × $0.0000125 = $0.045
- Memory cost: 1 × 3600 seconds × $0.0000014 = $0.005
- **Total: $0.05 per hour**

### Windows Containers

**Standard Pricing:**
- **vCPU**: ~$0.000025 per vCPU-second (~$0.09 per vCPU-hour)
- **Memory**: ~$0.0000028 per GB-second (~$0.01 per GB-hour)

**Example Calculation (Windows):**
- 1 vCPU, 1 GB RAM, running for 1 hour
- vCPU cost: 1 × 3600 seconds × $0.000025 = $0.09
- Memory cost: 1 × 3600 seconds × $0.0000028 = $0.01
- **Total: $0.10 per hour**

> **Note:** Windows containers cost approximately **2x** more than Linux containers

## Additional Costs

### GPU Resources (Linux Only)

For workloads requiring GPU acceleration:

**K80 GPU:**
- ~$0.000277 per GPU-second (~$1.00 per GPU-hour)

**P100 GPU:**
- ~$0.000694 per GPU-second (~$2.50 per GPU-hour)

**V100 GPU:**
- ~$0.001111 per GPU-second (~$4.00 per GPU-hour)

### Networking

**Virtual Network Integration:**
- Standard Azure Virtual Network pricing applies
- No additional ACI-specific networking charges for VNet integration

**Public IP Address:**
- Standard Azure Public IP pricing applies
- Dynamic Public IP: Small hourly charge (~$0.005/hour)

### Storage

**Volume Mounts:**
- **Azure Files**: Standard Azure Files storage pricing
- **GitRepo**: No additional charge (uses temporary storage)
- **EmptyDir**: No additional charge (uses temporary storage)
- **Secret**: No additional charge (uses temporary storage)

**Image Pull:**
- Egress charges may apply when pulling images from registries outside Azure
- No charge for pulling from Azure Container Registry in the same region

## Regional Pricing Variations

Pricing varies by Azure region. Common patterns:

- **US East, US West, North Europe, West Europe**: Standard pricing (baseline)
- **Asia Pacific regions**: Typically 10-20% higher
- **Brazil, South Africa**: Typically 20-30% higher
- **Australia**: Typically 15-25% higher

> Always check the Azure Pricing Calculator for region-specific pricing

## Cost Optimization Strategies

### 1. Right-Sizing Resources

```yaml
# Conservative allocation
resources:
  requests:
    cpu: 0.5
    memoryInGb: 0.5
  limits:
    cpu: 1.0
    memoryInGb: 1.0
```

- Start with minimal resources
- Monitor and adjust based on actual usage
- Avoid over-provisioning

### 2. Container Lifecycle Management

- **Terminate when not needed**: Stop containers that aren't actively processing
- **Use restart policies wisely**: Set appropriate restart policies (Always, OnFailure, Never)
- **Implement auto-shutdown**: For dev/test workloads, implement scheduled shutdown

### 3. Choose Linux Over Windows

- Use Linux containers when possible (50% cost savings)
- Only use Windows containers when specifically required

### 4. Optimize Container Start Time

- **Use smaller base images**: Reduces image pull time (which is billable)
- **Leverage Azure Container Registry**: Images in the same region = faster pulls, no egress
- **Pre-cache dependencies**: Build optimized images with dependencies included

### 5. Batch Processing

```yaml
# Example: Process multiple items per container instance
restartPolicy: OnFailure
```

- Process multiple work items per container instance
- Use appropriate restart policies for batch jobs
- Minimize container creation overhead

### 6. Use Azure Spot Instances (Preview)

- Save up to 70% compared to standard ACI pricing
- Best for fault-tolerant, flexible workloads
- May be evicted when Azure needs capacity

### 7. Regional Selection

- Deploy in regions with lower pricing
- Balance cost with latency requirements
- Consider compliance and data residency needs

## Billing Examples

### Example 1: Short-Running Task

**Scenario:** Data processing job
- Configuration: 2 vCPU, 4 GB RAM, Linux
- Duration: 5 minutes (300 seconds)

**Calculation:**
- vCPU: 2 × 300 × $0.0000125 = $0.0075
- Memory: 4 × 300 × $0.0000014 = $0.00168
- **Total: ~$0.009 (less than 1 cent)**

### Example 2: Long-Running Service

**Scenario:** API backend
- Configuration: 1 vCPU, 2 GB RAM, Linux
- Duration: 30 days continuous (720 hours)

**Calculation:**
- vCPU: 1 × 2,592,000 seconds × $0.0000125 = $32.40
- Memory: 2 × 2,592,000 seconds × $0.0000014 = $7.26
- **Total: ~$39.66 per month**

### Example 3: Development Environment

**Scenario:** Testing environment
- Configuration: 1 vCPU, 1 GB RAM, Windows
- Duration: 8 hours/day, 20 days/month (160 hours)

**Calculation:**
- vCPU: 1 × 576,000 seconds × $0.000025 = $14.40
- Memory: 1 × 576,000 seconds × $0.0000028 = $1.61
- **Total: ~$16.01 per month**

## Cost Comparison with Alternatives

| Service | Use Case | Relative Cost | Notes |
|---------|----------|---------------|-------|
| ACI | Short-lived tasks, burst workloads | Baseline | Pay per second |
| Azure Kubernetes Service (AKS) | Long-running, complex orchestration | Higher initial | Cost-effective at scale |
| Azure App Service | Web apps, APIs | Similar | Includes platform features |
| Azure Functions (Container) | Event-driven | Lower for sporadic | Consumption-based |
| Virtual Machines | Full control | Higher | 24/7 runtime costs |

## Free Tier & Limits

**Azure Free Tier:**
- ACI is **not included** in the Azure Free Tier
- All usage is billable from the first second

**Service Limits:**
- Maximum containers per container group: 60
- Maximum container groups per subscription per region: 100 (can be increased)
- Maximum vCPU per container group: 4
- Maximum memory per container group: 16 GB

## Monitoring and Cost Management

### Azure Cost Management

- **Set budgets**: Create budget alerts for ACI spending
- **Use tags**: Tag container groups for cost allocation
- **Monitor metrics**: Track CPU and memory utilization

### Cost Tracking Tips

```yaml
# Tag container groups for cost allocation
tags:
  Environment: Production
  Project: WebAPI
  CostCenter: Engineering
  Owner: TeamA
```

### Azure Advisor Recommendations

- Review Azure Advisor for ACI cost optimization suggestions
- Check for underutilized resources
- Implement recommended right-sizing

## Best Practices Summary

1. ✅ **Use Linux containers** when possible
2. ✅ **Right-size resources** - start small, scale as needed
3. ✅ **Implement proper lifecycle management** - stop when not needed
4. ✅ **Optimize images** - smaller images = faster starts = lower costs
5. ✅ **Use ACR in same region** - faster, no egress charges
6. ✅ **Tag everything** - enable cost tracking and allocation
7. ✅ **Monitor usage** - use Azure Monitor to track actual resource consumption
8. ✅ **Consider alternatives** - evaluate if ACI is the most cost-effective option

## Additional Resources

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure Container Instances Pricing Page](https://azure.microsoft.com/pricing/details/container-instances/)
- [Azure Cost Management Documentation](https://docs.microsoft.com/azure/cost-management-billing/)
- [ACI Resource Limits](https://docs.microsoft.com/azure/container-instances/container-instances-quotas)

---

> **Last Updated:** December 2025
> 
> **Note:** Pricing information is approximate and subject to change. Always verify current pricing using the Azure Pricing Calculator or Azure Portal.
