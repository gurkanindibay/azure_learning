# Azure Container Apps - Deployment from Source Code

## Overview

Azure Container Apps (ACA) provides multiple ways to deploy containerized applications. One of the most convenient methods is deploying directly from source code using a Dockerfile.

## Deployment Methods

### Using `az containerapp up` with Source Code

The `az containerapp up` command is a convenient way to build and deploy container apps directly from source code. When you have a Dockerfile in your repository, you can use this command to:

1. Build the container image from the Dockerfile
2. Push the image to a container registry
3. Create or update the container app
4. Deploy the application

**Command:**
```bash
az containerapp up --source .
```

The `--source .` parameter tells the command to use the current directory (which should contain the Dockerfile) as the source for building the container image.

### Other Container App Commands

- **`az containerapp env create`**: Creates a Container Apps environment (the infrastructure boundary for container apps), but doesn't deploy an app
- **`az containerapp create`**: Creates a container app, but requires additional parameters:
  - `--image`: Requires a pre-built container image reference (e.g., from ACR or Docker Hub)
  - `--containername`: Not a valid parameter for this command

## Practice Question

**Scenario:**
Your company is developing an application that includes a backend web API service. The development team has decided to use Azure Container Apps to host the API. They have a Dockerfile in the root of their repository that defines the containerized app.

**Question:**
You need to deploy the container app using the Dockerfile. What should you do?

**Options:**

1. ❌ Use the `az containerapp env create` command with the `--name` parameter.
   - **Incorrect**: This command only creates the Container Apps environment, not the actual container app.

2. ❌ Use the `az containerapp create` command with the `--image` parameter.
   - **Incorrect**: This requires a pre-built container image. It doesn't build from a Dockerfile.

3. ❌ Use the `az containerapp create` command with the `--containername` parameter.
   - **Incorrect**: This parameter doesn't exist for this command and doesn't fulfill the requirement.

4. ✅ Use the `az containerapp up` command with the `--source .` parameter.
   - **Correct**: This command builds and deploys the container app using the Dockerfile in the root of the repository.

## Key Takeaways

- **`az containerapp up`** is the simplest way to deploy from source code with a Dockerfile
- The command handles the entire workflow: build, push, and deploy
- The `--source` parameter specifies the directory containing the Dockerfile
- This approach is ideal for rapid development and deployment scenarios

## Azure Container Apps Pricing

### Consumption Plan (Pay-as-you-go)

Azure Container Apps uses a **consumption-based pricing model** with two main components:

#### 1. Resource Consumption

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

#### 2. Request Charges

- **Price**: $0.40 per million requests
- First 2 million requests per month are **free**
- Counts HTTP requests and scale operations

**Example:**
```
10 million requests per month:
- First 2M: Free
- Remaining 8M: 8 × $0.40 = $3.20/month
```

### Free Grant

Azure Container Apps includes a **monthly free grant** per subscription:

- **180,000 vCPU-seconds** (~50 hours of 1 vCPU)
- **360,000 GiB-seconds** (~100 hours of 1 GiB memory)
- **2 million requests**

### Pricing Tiers Comparison

| Component | Price | Free Grant | Billing Unit |
|-----------|-------|------------|-------------|
| **vCPU** | $0.000024/second | 180,000 vCPU-seconds/month | Per second |
| **Memory** | $0.000003/GiB/second | 360,000 GiB-seconds/month | Per second |
| **Requests** | $0.40/million | 2 million/month | Per request |

### Cost Optimization Tips

1. **Use scale-to-zero**: Containers that aren't processing requests don't incur compute charges
2. **Right-size resources**: Allocate only what you need (min 0.25 vCPU, 0.5 GiB)
3. **Enable autoscaling**: Scale based on HTTP traffic, CPU, memory, or custom metrics
4. **Use replicas efficiently**: Set appropriate min/max replica counts
5. **Leverage free grants**: Small dev/test workloads may run within free tier
6. **Monitor usage**: Use Azure Cost Management to track spending

### Scaling Configuration

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

### Use Case Cost Examples

#### Example 1: Small API (Dev/Test)
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

#### Example 2: Production Web App
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

#### Example 3: Event-Driven Processing
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

### Additional Costs

**Not included in Container Apps pricing:**
- **Networking**: Virtual network integration, private endpoints
- **Storage**: Persistent storage volumes (Azure Files, etc.)
- **Container Registry**: Azure Container Registry costs
- **Observability**: Log Analytics workspace data ingestion and retention
- **Custom domains**: Free, but SSL certificates may have costs
- **Load testing**: Separate Azure Load Testing service costs

### Key Benefits

✅ **Pay per second**: No rounding to hours  
✅ **Scale to zero**: No cost when idle  
✅ **No infrastructure management**: No VM costs  
✅ **Free grant**: Good for development and small workloads  
✅ **Predictable pricing**: Easy to estimate based on usage  
✅ **No minimum commitment**: True consumption model  

## Additional Resources

- [Quickstart: Build and deploy from local source code to Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/quickstart-code-to-cloud)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Apps Pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/)
- [Billing in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/billing)

## Related Topics

- Azure Container Registry (ACR) integration
- Container Apps environments
- Dockerfile best practices
- CI/CD pipelines with Azure Container Apps
