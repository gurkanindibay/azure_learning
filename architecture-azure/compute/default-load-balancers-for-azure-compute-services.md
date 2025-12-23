# Default Load Balancers for Azure Compute Services

## Table of Contents

- [Overview](#overview)
- [Azure Container Apps](#azure-container-apps)
- [Azure App Service](#azure-app-service)
- [Azure Functions](#azure-functions)
- [Azure Container Instances](#azure-container-instances)
- [Comparison Table](#comparison-table)
- [Key Takeaways](#key-takeaways)
- [When to Add External Load Balancers](#when-to-add-external-load-balancers)
- [Load Balancing Architecture Patterns](#load-balancing-architecture-patterns)
- [Best Practices](#best-practices)

## Overview

Azure compute services have varying levels of built-in load balancing capabilities. Understanding which services include automatic load balancing versus which require manual configuration is crucial for architecture planning and cost optimization.

**Load balancing** refers to efficiently distributing incoming network traffic across multiple instances of your application to ensure high availability, scalability, and optimal resource utilization.

## Azure Container Apps

### Built-in Load Balancing: ✅ Yes (Fully Managed)

Azure Container Apps provides **built-in ingress and load balancing** with no separate load balancer configuration required.

#### Key Features

**Ingress Proxy:**
- Scalable edge ingress proxy built into the Container Apps environment
- Handles TLS termination, load balancing, and traffic splitting
- No need to create Azure Load Balancer, public IP address, or any other Azure resources for incoming HTTP/TCP traffic

**Default Ingress Mode:**
- 2 ingress proxy instances by default
- Auto-scales up to 10 instances based on load
- Each instance allocated up to 1 vCPU and 2 GB memory
- No additional billing for default ingress scaling

**Premium Ingress Mode:**
- For high-scale applications
- Configurable for even greater capacity

**Load Balancing Capabilities:**
```
1. TLS Termination
   - Decrypts TLS traffic at ingress
   - Reduces container resource consumption
   - Supports custom domains and certificates

2. Traffic Splitting
   - Load balance between active revisions
   - Percentage-based distribution
   - Supports blue-green deployments and A/B testing

3. Session Affinity
   - Routes clients to the same replica
   - Useful for stateful applications
```

#### Ingress Configuration

**External Ingress:**
```bash
# Public endpoint accessible from internet
az containerapp create \
  --name myapp \
  --ingress external \
  --target-port 8080
```

**Internal Ingress:**
```bash
# Only accessible within VNET
az containerapp create \
  --name myapp \
  --ingress internal \
  --target-port 8080
```

#### Traffic Distribution

**Automatic Distribution:**
- HTTP/HTTPS requests distributed across replicas
- Built-in health checks ensure traffic goes to healthy instances
- Supports HTTP/1.1, HTTP/2, WebSocket, and gRPC

**Traffic Splitting Example:**
```bash
# Split traffic between revisions (canary deployment)
az containerapp ingress traffic set \
  --name myapp \
  --revision-weight revision1=80 revision2=20
```

#### Architecture

```
Internet/VNET
    ↓
Ingress Proxy (Auto-scaled 2-10 instances)
    ↓
TLS Termination + Load Balancing
    ↓
Container App Replicas (Auto-scaled 0-300)
```

**Important Notes:**
- When you enable ingress, you don't need to create Azure Load Balancer
- Ingress handles all routing, load balancing, and TLS termination
- Default request timeout: 240 seconds
- Supports up to 600 concurrent connections per replica (HTTP/1.1)
- Supports up to 300 concurrent streams per replica (HTTP/2)

**Reference:** [Configure ingress for Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)

---

## Azure App Service

### Built-in Load Balancing: ✅ Yes (Platform-Managed)

Azure App Service includes **automatic load balancing** when your app scales to multiple instances.

#### Key Features

**Built-in Azure Load Balancer:**
- Automatically distributes traffic across instances when scaled out
- No manual configuration required
- Part of the App Service platform infrastructure

**Load Balancing Characteristics:**
```
1. Automatic Distribution
   - Uses Azure Load Balancer behind the scenes
   - Layer 4 (TCP) load balancing
   - Hash-based distribution algorithm

2. Session Affinity (ARR Affinity)
   - Application Request Routing cookies
   - Routes clients to the same instance
   - Enabled by default
   - Can be disabled for stateless apps
```

#### Scaling and Load Balancing

**Manual Scaling:**
```bash
# Scale to 3 instances
az appservice plan update \
  --name myplan \
  --resource-group myResourceGroup \
  --number-of-workers 3
```

**Automatic Scaling (Premium V2/V3 plans):**
```bash
# Enable automatic scaling
az appservice plan update \
  --name myplan \
  --resource-group myResourceGroup \
  --elastic-scale true \
  --max-elastic-worker-count 10
```

**Automatic Scaling Features:**
- Platform monitors HTTP traffic load
- Adds instances automatically based on demand
- Pre-warms instances to avoid cold starts
- Per-second billing
- Maximum 30 instances (Premium V2/V3)

#### Session Affinity Behavior

**With ARR Affinity Enabled (Default):**
```
Client Request
    ↓
Azure Load Balancer
    ↓
Instance 1 (assigned to client)
    ↓
Subsequent Requests → Same Instance 1
```

**With ARR Affinity Disabled:**
```
Client Request
    ↓
Azure Load Balancer
    ↓
Any Available Instance (load balanced)
```

**Disable ARR Affinity:**
- Navigate to App Service → Configuration → General Settings
- Set Session Affinity to **Off**
- Recommended for stateless applications with automatic scaling

#### Architecture

```
Internet
    ↓
Azure Load Balancer (Built-in)
    ↓
App Service Instances (1-30)
```

**Load Distribution Algorithm:**
- 5-tuple hash by default (source IP, source port, destination IP, destination port, protocol)
- Can use 2-tuple or 3-tuple with session affinity

**Important Notes:**
- Minimum 1 instance always running (unlike Container Apps)
- Basic tier: up to 3 instances
- Standard tier: up to 10 instances
- Premium tier: up to 30 instances
- Isolated tier (ASE): up to 100 instances

**Reference:** [Automatic scaling in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling)

---

## Azure Functions

### Built-in Load Balancing: ✅ Yes (Platform-Managed)

Azure Functions includes **built-in load balancing** across all hosting plans.

#### Key Features

**Platform-Managed Load Distribution:**
- Automatic distribution of function executions across instances
- No explicit load balancer configuration required
- Built into the Functions runtime and hosting infrastructure

**Scaling and Load Balancing by Plan:**

| Hosting Plan | Scaling Type | Load Balancing | Max Instances |
|--------------|--------------|----------------|---------------|
| **Consumption** | Event-driven automatic | Built-in | 200 (Windows), 100 (Linux) |
| **Premium** | Event-driven automatic | Built-in | 100 |
| **Dedicated (App Service)** | Manual/Autoscale | Built-in | 10-30 |
| **Flex Consumption** | Per-function automatic | Built-in | 1000 |

#### Event-Driven Scaling

**How It Works:**
```
1. Functions monitors incoming events
2. Built-in scale controller decides when to add/remove instances
3. Function executions distributed across available instances
4. Each trigger type has specific thresholds:
   - Queue: Message age and queue length
   - HTTP: Number of concurrent requests
   - Event Hubs: Number of unprocessed events
```

**Example - HTTP Trigger Load Balancing:**
```
HTTP Requests
    ↓
Azure Functions Infrastructure (Built-in LB)
    ↓
Function Instances (Auto-scaled)
    ↓
Function Executions (Distributed)
```

#### Concurrency and Load Distribution

**Per-Instance Concurrency:**
- Functions can handle multiple invocations concurrently on a single instance
- Default concurrency varies by trigger type
- Configurable via `host.json`

**Node.js Specific:**
```json
{
  "FUNCTIONS_WORKER_PROCESS_COUNT": "4"
}
```
- Increases worker processes from 1 to max 10
- Evenly distributes invocations across workers
- Useful for CPU-intensive functions

#### Target-Based Scaling

**For Event Hubs and Storage Queues:**
- Platform calculates unprocessed events/messages
- Divides by target threshold per instance
- Automatically scales to optimal instance count
- Ensures balanced partition/message distribution

**Example Configuration (host.json):**
```json
{
  "extensions": {
    "eventHubs": {
      "targetUnprocessedEventThreshold": 50,
      "maxEventBatchSize": 100
    }
  }
}
```

#### Architecture

**Consumption Plan:**
```
Events (HTTP, Queue, Event Hub, etc.)
    ↓
Scale Controller (Monitoring)
    ↓
Function Host Instances (Auto-scaled)
    ↓
Load-balanced Function Executions
```

**Premium Plan:**
```
Events
    ↓
Pre-warmed Instances (Always ready)
    ↓
Scale Controller
    ↓
Additional Instances (Auto-scaled)
    ↓
Load-balanced Executions
```

**Important Notes:**
- No separate Azure Load Balancer resource created
- Load balancing happens at the platform level
- Event-driven scaling automatically handles load distribution
- Cold starts in Consumption plan (mitigated in Premium with pre-warmed instances)
- HTTP Functions exposed through Azure's infrastructure with automatic load balancing

**Reference:** [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)

---

## Azure Container Instances

### Built-in Load Balancing: ❌ No

Azure Container Instances **does NOT include built-in load balancing**. Each container instance operates independently.

#### Key Characteristics

**No Native Load Balancing:**
- Each container instance gets its own public IP or FQDN
- No automatic traffic distribution between instances
- Each instance is completely isolated
- Designed for single-container scenarios or sidecar patterns

**Important Limitation:**
> **Azure Load Balancer** - Placing an Azure Load Balancer in front of container instances in a networked container group is NOT supported.

**Unsupported Scenarios:**
```
❌ Azure Load Balancer in front of ACI
❌ Global virtual network peering
❌ Public IP with VNet-deployed containers
❌ Multiple instances behind a load balancer
```

#### When to Use ACI

**Best Use Cases:**
```
1. Simple container jobs
2. Batch processing
3. Build agents
4. Task-based workloads
5. Development/testing
6. Isolated single containers
```

**NOT Recommended For:**
```
❌ Production microservices requiring load balancing
❌ High-availability applications
❌ Applications needing traffic distribution
❌ Applications requiring auto-scaling with load balancing
```

#### Manual Load Balancing Options

If you need load balancing with ACI, you must manually configure external services:

**Option 1: Azure Application Gateway**
```
Internet
    ↓
Azure Application Gateway (Layer 7)
    ↓
Multiple ACI Instances (Manually configured)
```

**Option 2: Azure Traffic Manager**
```
DNS Query
    ↓
Azure Traffic Manager (DNS-based)
    ↓
Multiple ACI Instances (Different regions)
```

**Option 3: Azure Front Door**
```
Internet
    ↓
Azure Front Door (Global Layer 7)
    ↓
Multiple ACI Instances (Multi-region)
```

#### Networking Options

**Public Access:**
```bash
# Each instance gets its own public IP
az container create \
  --name mycontainer1 \
  --image myimage \
  --ip-address Public
```

**VNet Integration:**
```bash
# Deploy into VNet (no public IP)
az container create \
  --name mycontainer \
  --image myimage \
  --vnet myvnet \
  --subnet mysubnet
```

**Important VNet Limitations:**
- Must use NAT Gateway for outbound connectivity
- Cannot place Azure Load Balancer in front of VNet-deployed instances
- No public IP or DNS label when deployed to VNet
- Subnet can only contain container groups (no other resources)

#### Architecture

**Single Instance (Typical ACI Usage):**
```
Internet
    ↓
Public IP/FQDN
    ↓
Single ACI Container Group
```

**Manual Load Balanced (Requires External Service):**
```
Internet
    ↓
Application Gateway / Traffic Manager / Front Door
    ↓
ACI Instance 1    ACI Instance 2    ACI Instance 3
(Separate IPs)   (Separate IPs)   (Separate IPs)
```

#### Migration Path

**If you need load balancing, consider:**
1. **Azure Container Apps** - Built-in load balancing, auto-scaling, microservices-ready
2. **Azure Kubernetes Service (AKS)** - Full orchestration with ingress controllers
3. **Azure App Service Containers** - Managed platform with built-in scaling

**Reference:** [Virtual network scenarios and resources for ACI](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-virtual-network-concepts)

---

## Comparison Table

| Service | Default Load Balancer | Type | Configuration Required | Max Instances | Best For |
|---------|----------------------|------|----------------------|---------------|----------|
| **Azure Container Apps** | ✅ Built-in | Managed Ingress Proxy (Layer 7) | Minimal (enable ingress) | 300 | Production microservices, APIs, web apps |
| **Azure App Service** | ✅ Built-in | Azure Load Balancer (Layer 4) | Automatic with scaling | 30 (Premium) | Web applications, APIs, backends |
| **Azure Functions** | ✅ Built-in | Platform-managed | None | 200 (Consumption) | Event-driven, serverless functions |
| **Azure Container Instances** | ❌ None | N/A - Manual setup required | External service needed | N/A | Simple containers, batch jobs, CI/CD agents |

### Feature Comparison

| Feature | Container Apps | App Service | Azure Functions | Container Instances |
|---------|---------------|-------------|-----------------|---------------------|
| **Automatic Load Balancing** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Auto-scaling** | ✅ Yes (0-300) | ✅ Yes (1-30) | ✅ Yes | ❌ No |
| **Scale to Zero** | ✅ Yes | ❌ No | ✅ Yes (Consumption) | N/A |
| **Traffic Splitting** | ✅ Yes | ✅ Limited | ❌ No | ❌ No |
| **Session Affinity** | ✅ Yes | ✅ Yes (ARR) | ❌ No | N/A |
| **TLS Termination** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Manual |
| **Health Checks** | ✅ Built-in | ✅ Built-in | ✅ Built-in | ❌ Manual |
| **Custom Domains** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Limited |
| **Public IP per Instance** | ❌ No | ❌ No | ❌ No | ✅ Yes |

---

## Key Takeaways

### Services with Built-in Load Balancing

**1. Azure Container Apps** ⭐ Recommended for New Cloud-Native Apps
- Most comprehensive built-in load balancing
- Layer 7 ingress with TLS termination
- Traffic splitting and blue-green deployments
- No separate load balancer costs
- Best for microservices and cloud-native applications

**2. Azure App Service** ⭐ Recommended for Traditional Web Apps
- Automatic load balancing with scaling
- Simple configuration
- Proven track record for web applications
- ARR affinity for stateful apps

**3. Azure Functions** ⭐ Recommended for Event-Driven Workloads
- Built-in distribution of function executions
- Event-driven auto-scaling
- No infrastructure management
- Best for serverless, event-driven scenarios

### Services Without Built-in Load Balancing

**4. Azure Container Instances** ⚠️ Not Recommended for Load-Balanced Apps
- No built-in load balancing
- Each instance is independent
- Best for simple, single-container scenarios
- Migrate to Container Apps for production workloads needing load balancing

---

## When to Add External Load Balancers

Even services with built-in load balancing might benefit from external load balancers for advanced scenarios:

### Azure Application Gateway

**Use with App Service/Container Apps when you need:**
- Web Application Firewall (WAF)
- Advanced path-based routing
- SSL offloading at scale
- Multiple site hosting
- URL rewrite capabilities

```
Internet
    ↓
Azure Application Gateway (WAF + Layer 7 LB)
    ↓
App Service / Container Apps (Built-in LB)
```

### Azure Traffic Manager

**Use for multi-region deployments:**
- Global DNS-based load balancing
- Geographic routing
- Priority-based failover
- Performance-based routing

```
DNS Query
    ↓
Azure Traffic Manager (Global DNS LB)
    ↓
Region 1: App Service     Region 2: Container Apps
```

### Azure Front Door

**Use for global applications:**
- Global Layer 7 load balancing
- CDN integration
- Web Application Firewall at edge
- SSL offloading
- Fast failover

```
Internet (Global)
    ↓
Azure Front Door (Global L7 LB + CDN + WAF)
    ↓
Multiple Regions: Container Apps + App Service
```

---

## Load Balancing Architecture Patterns

### Pattern 1: Single Region Web Application

**Recommended: App Service or Container Apps**
```
Internet
    ↓
Built-in Load Balancer
    ↓
App Service / Container Apps Instances
    ↓
Azure SQL / Cosmos DB
```

**No additional load balancer needed** - Use built-in capabilities.

### Pattern 2: Multi-Region Web Application

**Recommended: Traffic Manager + App Service/Container Apps**
```
Internet
    ↓
Azure Traffic Manager (DNS)
    ↓
├─ Region 1: App Service (Built-in LB)
├─ Region 2: App Service (Built-in LB)
└─ Region 3: App Service (Built-in LB)
```

### Pattern 3: Microservices Architecture

**Recommended: Azure Container Apps**
```
Internet
    ↓
Azure Front Door (Optional)
    ↓
Container Apps Environment
    ├─ API Gateway App (Ingress: External)
    │   ↓
    ├─ Service A (Ingress: Internal)
    ├─ Service B (Ingress: Internal)
    └─ Service C (Ingress: Internal)
```

**All load balancing handled by Container Apps environment** - No additional load balancers needed.

### Pattern 4: Serverless Event-Driven

**Recommended: Azure Functions**
```
Event Sources (Queue, Event Hub, HTTP)
    ↓
Azure Functions (Built-in LB)
    ↓
Function Instances (Auto-scaled)
```

### Pattern 5: Hybrid Architecture

**Mix of Services:**
```
Internet
    ↓
Azure Application Gateway (WAF)
    ↓
├─ Container Apps (Microservices)
├─ App Service (Web UI)
└─ Azure Functions (Background Processing)
```

---

## Best Practices

### For Azure Container Apps

1. **Use Built-in Ingress**
   - Enable external ingress for public-facing apps
   - Use internal ingress for backend services
   - No need for external load balancers in most cases

2. **Configure Traffic Splitting**
   - Use for blue-green deployments
   - Implement canary releases
   - A/B testing without additional tools

3. **Enable Session Affinity When Needed**
   - Only for stateful applications
   - Understand the trade-offs with scaling

### For Azure App Service

1. **Disable ARR Affinity for Stateless Apps**
   - Improves load distribution
   - Better autoscaling performance
   - Recommended for automatic scaling

2. **Use Automatic Scaling (Premium V2/V3)**
   - Set appropriate min/max instances
   - Let platform handle scaling decisions
   - Configure always-ready instances

3. **Monitor AutomaticScalingInstanceCount Metric**
   - Track actual instance count
   - Understand scaling patterns
   - Optimize configuration

### For Azure Functions

1. **Choose the Right Hosting Plan**
   - Consumption: Cost-effective, cold starts
   - Premium: Pre-warmed, VNet integration
   - Dedicated: Predictable costs, manual scaling

2. **Optimize Concurrency Settings**
   - Configure per trigger type
   - Use `host.json` settings appropriately
   - Balance throughput vs. resource usage

3. **Use Target-Based Scaling**
   - For Event Hubs and Storage Queues
   - Set appropriate thresholds
   - Monitor unprocessed events

### For Azure Container Instances

1. **Don't Use for Load-Balanced Production Apps**
   - Migrate to Container Apps instead
   - Use only for simple scenarios
   - Consider batch jobs and CI/CD agents

2. **If Load Balancing is Required**
   - Use Azure Application Gateway (Layer 7)
   - Use Azure Traffic Manager (DNS-based)
   - Use Azure Front Door (Global)
   - Manage instances manually

3. **Consider Alternatives**
   - Container Apps for microservices
   - AKS for complex orchestration
   - App Service for traditional web apps

---

## Decision Tree

```
Need compute service?
    ↓
Is it containerized?
    ↓
├─ YES
│  ├─ Need load balancing + auto-scaling?
│  │  ├─ YES → Azure Container Apps (Built-in LB)
│  │  └─ NO → Azure Container Instances (No LB)
│  │
│  └─ Complex orchestration needed?
│     └─ YES → Azure Kubernetes Service
│
└─ NO
   ├─ Event-driven/Serverless?
   │  └─ YES → Azure Functions (Built-in LB)
   │
   └─ Traditional web app?
      └─ YES → Azure App Service (Built-in LB)
```

---

## Cost Implications

### No Additional Load Balancer Costs

**Services with built-in load balancing:**
- ✅ **Container Apps**: No separate LB charges (ingress included)
- ✅ **App Service**: LB included in plan pricing
- ✅ **Azure Functions**: LB included in compute costs

### Additional Costs When Using External Load Balancers

**If you add Application Gateway:**
- Fixed cost per gateway instance
- Data processing charges
- WAF charges (if enabled)

**If you add Traffic Manager:**
- DNS query charges
- Health check charges

**If you add Azure Front Door:**
- Data transfer charges
- Request charges
- WAF charges (if enabled)

---

## References

### Official Microsoft Documentation

- [Azure Container Apps Ingress](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Azure Container Apps Networking](https://learn.microsoft.com/en-us/azure/container-apps/networking)
- [Azure App Service Automatic Scaling](https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling)
- [Azure Functions Scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Azure Functions Concurrency](https://learn.microsoft.com/en-us/azure/azure-functions/functions-concurrency)
- [Azure Container Instances VNet Concepts](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-virtual-network-concepts)
- [Azure Load Balancer Overview](https://learn.microsoft.com/en-us/azure/load-balancer/load-balancer-overview)
- [Load Balancing Options in Azure](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)

### Related Documentation in This Repository

- [Azure Container Apps Overview](./azure_container_apps/azure-container-apps-overview.md)
- [Azure Container Comparison](./azure_container_instances/azure-container-comparison.md)
- [Azure Functions Hosting Plans](./azure_functions/azure-functions-hosting-plans.md)
- [App Service Pricing Tiers](./azure_app_service/app-service-pricing-tiers.md)
- [Azure Load Balancing Services Comparison](../load_balancing_solutions/azure-load-balancing-services-comparison.md)

---

**Last Updated**: November 25, 2025
**Document Version**: 1.0
