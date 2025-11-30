# Azure Container Apps - Notable Details & Key Concepts

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture Components](#architecture-components)
  - [Container Apps Environment](#container-apps-environment)
  - [Container Apps](#container-apps)
  - [Revisions](#revisions)
- [Scaling Capabilities](#scaling-capabilities)
  - [Scale to Zero](#scale-to-zero)
  - [KEDA-Based Scaling](#keda-based-scaling)
  - [Scaling Rules](#scaling-rules)
- [Networking](#networking)
  - [Ingress Configuration](#ingress-configuration)
  - [Internal vs External Ingress](#internal-vs-external-ingress)
  - [Custom Domains and Certificates](#custom-domains-and-certificates)
- [Dapr Integration](#dapr-integration)
- [Secrets Management](#secrets-management)
- [Observability](#observability)
- [Deployment Strategies](#deployment-strategies)
  - [Blue-Green Deployments](#blue-green-deployments)
  - [Traffic Splitting](#traffic-splitting)
- [Comparison with Other Services](#comparison-with-other-services)
- [Dynamic Sessions](#dynamic-sessions)
- [GPU Workload Profiles](#gpu-workload-profiles)
- [Common Use Cases](#common-use-cases)
- [Limitations and Constraints](#limitations-and-constraints)
- [Best Practices](#best-practices)

## Overview

Azure Container Apps is a fully managed serverless container service that enables you to run microservices and containerized applications without managing complex infrastructure. Built on top of Kubernetes, it abstracts away cluster management while providing powerful features like automatic scaling, traffic splitting, and built-in Dapr integration.

**Key Characteristics:**
- **Serverless**: No infrastructure management required
- **Kubernetes-based**: Built on AKS (Azure Kubernetes Service) but fully abstracted
- **Microservices-focused**: Designed for cloud-native applications
- **Event-driven**: Native support for KEDA scalers
- **Cost-effective**: Pay-per-second billing with scale-to-zero capability

## Key Features

### 1. Multiple Revisions
- Each deployment creates a new immutable revision
- Keep multiple revisions active simultaneously
- Split traffic between revisions for A/B testing or canary deployments
- Easy rollback to previous revisions

### 2. Built-in Service Discovery
- Automatic DNS-based service discovery within the environment
- Container apps can communicate using their app names
- No need for manual service registration

### 3. Managed Identity Support
- System-assigned and user-assigned managed identities
- Secure access to Azure resources without storing credentials
- Integrate with Key Vault, Storage, Cosmos DB, etc.

### 4. Multi-Container Support
- Run multiple containers in a single container app
- Share resources and network space
- Sidecar pattern support for auxiliary services

### 5. Job Support
- Run containers as scheduled or event-driven jobs
- Perfect for batch processing, data transformation, or maintenance tasks
- Automatic cleanup after completion

## Architecture Components

### Container Apps Environment

The **Container Apps Environment** is the secure boundary around a group of container apps. It provides:

- **Shared virtual network**: All apps in the environment share the same VNET
- **Log Analytics workspace**: Centralized logging for all apps
- **Dapr configuration**: Shared Dapr components and configuration
- **Resource isolation**: Apps in different environments are completely isolated

**Creating an Environment:**
```bash
az containerapp env create \
  --name myenv \
  --resource-group myResourceGroup \
  --location eastus
```

**Key Points:**
- Multiple container apps can share one environment
- Environments can be deployed into custom VNETs
- Supports internal-only environments (no public access)
- Each environment has its own control plane

### Container Apps

A **Container App** is the deployable unit containing:
- One or more container images
- Configuration (CPU, memory, environment variables)
- Scaling rules
- Ingress configuration
- Secrets

### Revisions

**Revisions** are immutable snapshots of a container app version:
- Created automatically on each deployment
- Can be activated or deactivated
- Support traffic splitting
- Named automatically or with custom names
- Retain their configuration permanently

**Revision Modes:**
- **Single**: Only one revision is active (default)
- **Multiple**: Multiple revisions can be active simultaneously

```bash
# Set revision mode to multiple
az containerapp revision set-mode \
  --name myapp \
  --resource-group myResourceGroup \
  --mode multiple
```

## Scaling Capabilities

### Scale to Zero

One of the most powerful features of Azure Container Apps:

**Benefits:**
- **Cost savings**: Pay only when processing requests
- **Efficiency**: No wasted resources during idle periods
- **Automatic**: No configuration needed for HTTP-triggered apps

**Behavior:**
- When no requests are coming in, replicas scale down to zero
- First request after scale-to-zero triggers cold start
- Cold start typically takes 2-5 seconds
- Subsequent requests are fast (warm instances)

**Configuration:**
```bash
az containerapp create \
  --name myapp \
  --min-replicas 0 \
  --max-replicas 10
```

**When NOT to use scale-to-zero:**
- Latency-sensitive applications requiring sub-second response times
- Applications with persistent connections (WebSockets, SignalR)
- Background processing that should run continuously

### KEDA-Based Scaling

Azure Container Apps uses **KEDA (Kubernetes Event-Driven Autoscaling)** for sophisticated scaling:

**What is KEDA?**

KEDA is an open-source Kubernetes-based event-driven autoscaler that extends the standard Kubernetes Horizontal Pod Autoscaler (HPA) capabilities. In Azure Container Apps, KEDA enables scaling based on external metrics, such as messages in a queue or events in a stream, providing a more dynamic and responsive scaling mechanism.

**Key Points About KEDA in Azure Container Apps:**

| Statement | Correct? | Explanation |
|-----------|----------|-------------|
| KEDA allows scaling based on external metrics (queue messages, stream events) | ✅ Yes | This is KEDA's primary purpose - enabling event-driven autoscaling based on external metrics |
| KEDA is exclusive to Azure Kubernetes Service (AKS) | ❌ No | While commonly used with AKS, KEDA can also be utilized in Azure Container Apps for event-driven autoscaling |
| KEDA scales only based on CPU usage | ❌ No | KEDA provides flexible scaling based on external metrics, not solely CPU usage |
| KEDA manages the lifecycle of underlying VMs | ❌ No | KEDA's focus is on enabling event-driven autoscaling for applications, not managing VM lifecycles |

**KEDA's Role:**
- **Event-Driven Scaling**: Scales containers based on external events and metrics
- **External Metrics Integration**: Connects to various event sources (queues, streams, databases)
- **Scale to Zero**: Supports scaling replicas to zero when no events are pending
- **Kubernetes Native**: Works seamlessly within Kubernetes environments including Azure Container Apps

**Supported Scalers:**
- HTTP requests
- Azure Service Bus queues/topics
- Azure Storage queues
- Azure Event Hubs
- Custom metrics (Prometheus, Azure Monitor)
- CPU and Memory utilization
- CRON expressions (schedule-based)

### Scaling Rules

**HTTP Scaling:**
```bash
az containerapp create \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50
```
- Scales based on concurrent HTTP requests
- Default concurrency: 10 requests per replica
- Ideal for web APIs and frontend applications

**Azure Queue Scaling:**
```bash
az containerapp create \
  --scale-rule-name queue-rule \
  --scale-rule-type azure-queue \
  --scale-rule-metadata "queueName=myqueue" \
                        "queueLength=5" \
  --scale-rule-auth "connection=connection-string-secret"
```
- Scales based on queue length
- Processes messages in parallel

**Service Bus Scaling:**
```bash
az containerapp create \
  --scale-rule-name servicebus-rule \
  --scale-rule-type azure-servicebus \
  --scale-rule-metadata "queueName=myqueue" \
                        "messageCount=10"
```

**CPU/Memory Scaling:**
```bash
az containerapp create \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata "type=Utilization" \
                        "value=70"
```

## Networking

### Ingress Configuration

**Ingress Types:**

1. **External Ingress**
   - Public endpoint accessible from the internet
   - Automatic HTTPS with managed certificates
   - Custom domains supported

2. **Internal Ingress**
   - Only accessible within the VNET
   - No public endpoint created
   - Ideal for backend services

```bash
# External ingress
az containerapp create \
  --ingress external \
  --target-port 8080

# Internal ingress
az containerapp create \
  --ingress internal \
  --target-port 8080
```

### Internal vs External Ingress

| Aspect | External | Internal |
|--------|----------|----------|
| **Accessibility** | Internet-facing | VNET only |
| **DNS** | Public DNS | Private DNS |
| **Use Case** | Frontend apps, public APIs | Backend services, databases |
| **Security** | Exposed to internet | Protected by VNET |
| **Custom Domain** | Supported | Supported |

### Custom Domains and Certificates

**Adding a Custom Domain:**
```bash
# Add custom domain
az containerapp hostname add \
  --hostname www.example.com \
  --name myapp \
  --resource-group myResourceGroup

# Bind SSL certificate
az containerapp hostname bind \
  --hostname www.example.com \
  --name myapp \
  --resource-group myResourceGroup \
  --certificate MyCertificate \
  --environment myenv
```

**Certificate Options:**
- Managed certificates (free, auto-renewed)
- Custom certificates from Key Vault
- Upload your own certificates

## Dapr Integration

**Dapr (Distributed Application Runtime)** is an open-source, portable runtime that simplifies building microservices applications. It provides building blocks for common distributed system patterns like service invocation, state management, pub/sub messaging, and observability. Dapr runs as a sidecar process alongside your application, exposing APIs that your code can call regardless of the programming language you use.

**What Dapr Does:**
- **Abstracts infrastructure**: Your code doesn't need to know if you're using Redis, Cosmos DB, or Service Bus
- **Simplifies microservices**: Handles service discovery, retries, and circuit breakers automatically
- **Language agnostic**: Works with any programming language via HTTP or gRPC APIs
- **Portable**: Same code works across cloud providers and on-premises

Dapr is built into Azure Container Apps, meaning you can enable it with a single flag:

**Benefits:**
- Service-to-service invocation
- State management
- Pub/sub messaging
- Bindings to external systems
- Observability and distributed tracing

**Enabling Dapr:**
```bash
az containerapp create \
  --name myapp \
  --enable-dapr \
  --dapr-app-id myapp \
  --dapr-app-port 8080 \
  --dapr-app-protocol http
```

**Common Dapr Components:**
- **State Store**: Azure Cosmos DB, Redis, Azure Table Storage
- **Pub/Sub**: Azure Service Bus, Event Hubs, Redis
- **Bindings**: Azure Blob Storage, Event Grid, Kafka

**Example - Service Invocation:**
```bash
# App A calls App B using Dapr
curl http://localhost:3500/v1.0/invoke/app-b/method/api/data
```

## Secrets Management

**Secrets** in Container Apps are securely stored and referenced:

**Adding Secrets:**
```bash
az containerapp create \
  --secrets "db-connection-string=Server=..." \
            "api-key=secretvalue123"
```

**Referencing Secrets:**
```bash
# In environment variables
az containerapp create \
  --env-vars "ConnectionString=secretref:db-connection-string"
```

**Key Vault Integration:**
```bash
az containerapp create \
  --secrets "my-secret=keyvaultref:https://myvault.vault.azure.net/secrets/mysecret,identityref:/subscriptions/.../Microsoft.ManagedIdentity/..."
```

**Best Practices:**
- Never hardcode secrets in environment variables
- Use Key Vault for sensitive secrets
- Use managed identity for Key Vault access
- Rotate secrets regularly

## Observability

### Logging

**Log Analytics Integration:**
- All container logs automatically sent to Log Analytics
- Application logs (stdout/stderr)
- System logs
- Revision history

**Querying Logs:**
```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "myapp"
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```

### Metrics

**Built-in Metrics:**
- Request count and latency
- Active replicas
- CPU and memory usage
- HTTP status codes

**Accessing Metrics:**
- Azure Portal metrics explorer
- Azure Monitor
- Application Insights integration

### Application Insights

**Enabling Application Insights:**
```bash
az containerapp create \
  --name myapp \
  --enable-app-insights \
  --app-insights-key <instrumentation-key>
```

**Benefits:**
- Distributed tracing
- Dependency tracking
- Live metrics
- Custom telemetry

## Deployment Strategies

### Blue-Green Deployments

Deploy a new version without affecting the current version:

```bash
# Deploy new revision (green)
az containerapp update \
  --name myapp \
  --image myimage:v2 \
  --revision-suffix green

# Test the green revision
# (it gets 0% traffic by default in multiple revision mode)

# Switch traffic to green
az containerapp ingress traffic set \
  --name myapp \
  --revision-weight latest=100
```

### Traffic Splitting

**Percentage-Based Traffic Split:**
```bash
az containerapp ingress traffic set \
  --name myapp \
  --revision-weight myapp--revision1=80 myapp--revision2=20
```

**Use Cases:**
- **Canary deployments**: Send 10% traffic to new version
- **A/B testing**: Split traffic 50/50 between versions
- **Gradual rollout**: Slowly increase traffic to new version
- **Feature flags**: Route specific users to specific versions

**Example - Gradual Rollout:**
```bash
# Step 1: Deploy new version with 0% traffic
az containerapp update --image myimage:v2

# Step 2: Send 10% traffic
az containerapp ingress traffic set \
  --revision-weight v1=90 v2=10

# Step 3: Increase to 50%
az containerapp ingress traffic set \
  --revision-weight v1=50 v2=50

# Step 4: Full cutover
az containerapp ingress traffic set \
  --revision-weight v2=100

# Step 5: Deactivate old revision
az containerapp revision deactivate --revision myapp--v1
```

## Comparison with Other Services

### Azure Container Apps vs Azure App Service

| Feature | Container Apps | App Service |
|---------|---------------|-------------|
| **Container Support** | Native, first-class | Supported, but limited |
| **Scaling** | KEDA-based, scale to zero | Auto-scale, min 1 instance |
| **Pricing** | Per-second consumption | Always running (min cost) |
| **Microservices** | Designed for it | Single app focus |
| **Dapr** | Built-in | Not supported |
| **Best For** | Cloud-native apps | Traditional web apps |

### Azure Container Apps vs Azure Kubernetes Service (AKS)

| Feature | Container Apps | AKS |
|---------|---------------|-----|
| **Management** | Fully managed | Self-managed clusters |
| **Complexity** | Low (abstracted) | High (full control) |
| **Scaling** | Automatic (KEDA) | Manual configuration |
| **Cost** | Pay per use | Pay for nodes 24/7 |
| **Control** | Limited | Full Kubernetes control |
| **Best For** | Simple microservices | Complex orchestration |

### Azure Container Apps vs Azure Container Instances (ACI)

| Feature | Container Apps | ACI |
|---------|---------------|-----|
| **Scaling** | Automatic | Manual |
| **Load Balancing** | Built-in | Manual setup |
| **Service Discovery** | Built-in | Not included |
| **Revisions** | Multiple versions | Single container |
| **Ingress** | Managed | DIY networking |
| **Best For** | Production microservices | Simple containers, batch jobs |

### Azure Container Apps vs Azure Functions

| Feature | Container Apps | Azure Functions |
|---------|---------------|-----------------|
| **Container Support** | Native | Limited (Premium/Dedicated) |
| **Programming Model** | Any | Functions SDK |
| **Execution Time** | Unlimited | 5-10 min (consumption) |
| **Microservices** | Excellent | Not designed for it |
| **Triggers** | HTTP, KEDA | 70+ built-in triggers |
| **Best For** | Long-running services | Event-driven functions |

## Dynamic Sessions

Azure Container Apps **dynamic sessions** provide instant access to secure, sandboxed environments designed specifically for running untrusted code at scale.

### Key Characteristics

- **Hyper-V Isolation**: Industry-standard Hyper-V isolation provides strong security boundaries between sessions
- **Sandboxed Environments**: Each session runs in a completely isolated environment
- **Scale Support**: Designed to handle running untrusted code at scale
- **Session Types**: Supports both Python code interpreter sessions and custom container sessions

### Session Types

| Session Type | Description | Use Case |
|--------------|-------------|----------|
| **Python Code Interpreter** | Pre-configured Python environment | Data analysis, ML inference, code execution |
| **Custom Container** | Bring your own container image | Custom runtimes, specialized tools |

### When to Use Dynamic Sessions

✅ **Use Dynamic Sessions When:**
- Running untrusted code from users
- Executing code that needs strong isolation
- Building multi-tenant code execution platforms
- Creating interactive coding environments (notebooks, REPLs)
- Running AI-generated code safely

❌ **Not Suitable For:**
- Long-running services (use regular Container Apps)
- Trusted application code
- Standard microservices workloads

### Comparison: Running Untrusted Code at Scale

| Solution | Hyper-V Isolation | Sandboxing | Session Management | Untrusted Code Support |
|----------|-------------------|------------|-------------------|------------------------|
| **Azure Container Apps Dynamic Sessions** | ✅ Yes | ✅ Strong | ✅ Built-in | ✅ Designed for it |
| **Azure Kubernetes Service (Pod Security Policies)** | ❌ No | ⚠️ Kubernetes-level only | ❌ Manual | ⚠️ Limited |
| **Azure App Service (Isolated Plan)** | ❌ No | ⚠️ Network isolation only | ❌ Not applicable | ❌ Not designed for it |
| **Azure Container Instances** | ✅ Yes (pod level) | ⚠️ Basic | ❌ Limited | ⚠️ Lacks specialized features |

> **Exam Tip**: When a question asks about running containers with strong isolation for executing untrusted code at scale with Hyper-V isolation and support for custom containers, **Azure Container Apps dynamic sessions** is the correct answer. Other options like AKS pod security policies, App Service isolated plans, or ACI container groups do not provide the same level of sandboxing and session management capabilities.

### Benefits Over Alternatives

1. **vs. AKS with Pod Security Policies**: Pod security policies in AKS provide security constraints at the Kubernetes level but do not offer Hyper-V isolation or the specialized sandboxing required for untrusted code execution.

2. **vs. App Service with Isolated Plan**: The isolated service plan provides network isolation for App Service but does not offer Hyper-V isolation or support for running untrusted code in sandboxed container environments.

3. **vs. Azure Container Instances**: ACI provides Hyper-V isolation at the pod level but lacks the specialized sandboxing features and session management capabilities required for running untrusted code at scale.

## GPU Workload Profiles

Azure Container Apps supports **serverless GPU workload profiles** that provide access to GPU resources for machine learning and AI workloads without managing infrastructure.

### Key Features

- **NVIDIA GPUs**: Access to NVIDIA A100 and T4 GPUs in a serverless environment
- **Scale-to-Zero**: Automatic scaling down to zero replicas when not in use, reducing costs
- **Built-in Data Governance**: Compliance and data governance features built into the platform
- **No Infrastructure Management**: Fully managed GPU resources without cluster administration

### GPU Types Available

| GPU Type | Best For | Key Characteristics |
|----------|----------|--------------------|
| **NVIDIA A100** | Large-scale ML training, high-performance inference | Highest performance, large memory |
| **NVIDIA T4** | Inference workloads, moderate training | Cost-effective, good balance of performance |

### When to Use GPU Workload Profiles

✅ **Use Container Apps Serverless GPUs When:**
- Running machine learning inference at scale
- Training ML models with variable demand
- Processing GPU-accelerated workloads intermittently
- Need scale-to-zero to minimize costs during idle periods
- Require data governance and compliance features
- Want to avoid managing GPU infrastructure

❌ **Consider Alternatives When:**
- Need persistent GPU allocation 24/7
- Require specialized Kubernetes configurations (use AKS with GPU nodes)
- Need GPU types not available in Container Apps

### Comparison: GPU Options for Containerized ML Workloads

| Solution | Scale-to-Zero | Data Governance | Infrastructure Management | Best For |
|----------|---------------|-----------------|---------------------------|----------|
| **Azure Container Apps (Serverless GPU)** | ✅ Yes | ✅ Built-in | ✅ Fully Managed | Dynamic ML workloads with variable demand |
| **Azure Kubernetes Service (GPU Node Pools)** | ❌ No | ⚠️ Manual setup | ❌ Self-managed | Full control, complex orchestration |
| **Azure Container Instances (GPU Preview)** | ❌ No | ⚠️ Limited | ✅ Managed | Simple, short-running GPU tasks |
| **Azure App Service** | N/A | N/A | N/A | ❌ No GPU support |

> **Exam Tip**: When a question asks about deploying containerized applications that require **GPU resources for machine learning workloads** with **scale-to-zero capabilities** and **data governance**, the correct answer is **Azure Container Apps with serverless GPU workload profiles**. AKS with GPU-enabled node pools requires infrastructure management and doesn't support scale-to-zero. Azure App Service doesn't support GPU compute. Azure Container Instances GPU support (preview) lacks serverless scale-to-zero capabilities.

### Example Configuration

```bash
# Create a Container Apps environment with GPU workload profile
az containerapp env create \
  --name myGpuEnv \
  --resource-group myResourceGroup \
  --location eastus \
  --enable-workload-profiles

# Add a GPU workload profile
az containerapp env workload-profile add \
  --name myGpuEnv \
  --resource-group myResourceGroup \
  --workload-profile-name gpu-profile \
  --workload-profile-type NC24-A100 \
  --min-nodes 0 \
  --max-nodes 5

# Deploy an app using the GPU profile
az containerapp create \
  --name myMlApp \
  --resource-group myResourceGroup \
  --environment myGpuEnv \
  --workload-profile-name gpu-profile \
  --image myregistry.azurecr.io/ml-inference:v1 \
  --min-replicas 0 \
  --max-replicas 10
```

## Common Use Cases

### 1. Microservices Architecture
- Multiple small services communicating via HTTP or Dapr
- Independent scaling per service
- Service discovery and load balancing built-in

### 2. API Backends
- RESTful APIs with automatic HTTPS
- Scale based on request volume
- Easy integration with frontends

### 3. Event-Driven Processing
- Process messages from Service Bus or Event Hubs
- Scale based on queue depth
- Scale to zero when no messages

### 4. Background Workers
- Long-running background tasks
- Scheduled jobs using CRON triggers
- Data processing pipelines

### 5. Web Applications
- Frontend applications (React, Vue, Angular)
- Static site hosting with API backends
- Progressive Web Apps (PWAs)

### 6. Batch Processing
- Use Container Apps Jobs for batch workloads
- Process large datasets
- ETL (Extract, Transform, Load) operations

## Limitations and Constraints

### Resource Limits (Per Container)

| Resource | Minimum | Maximum |
|----------|---------|---------|
| **CPU** | 0.25 vCPU | 4 vCPU |
| **Memory** | 0.5 GiB | 8 GiB |
| **Replicas** | 0 | 300 |
| **Container Size** | N/A | 4 GB compressed |

### Other Limitations

1. **Session Affinity**: Not supported (design for stateless apps)
2. **Privileged Containers**: Not allowed (no root access)
3. **Host Networking**: Not available (isolated networking)
4. **GPU Support**: Available via serverless GPU workload profiles (NVIDIA A100 and T4)
5. **Windows Containers**: Linux containers only
6. **Storage**: No persistent storage (use Azure Files or volumes)

### Network Limitations

- Maximum 600 concurrent connections per replica (HTTP/1.1)
- 300 concurrent streams per replica (HTTP/2)
- Request timeout: 240 seconds (4 minutes)
- Response size limit: None, but consider performance

## Best Practices

### Design

1. **Design for Statelessness**
   - Don't rely on local storage or in-memory state
   - Use external state stores (Redis, Cosmos DB)
   - Enable horizontal scaling without issues

2. **Implement Health Checks**
   - Use liveness and readiness probes
   - Return proper HTTP status codes
   - Check dependencies in health endpoints

3. **Use Multi-Container Apps Wisely**
   - Sidecar pattern for auxiliary services
   - Share resources efficiently
   - Be mindful of CPU/memory allocation

### Scaling

4. **Configure Appropriate Scale Rules**
   - Use KEDA scalers that match your workload
   - Set reasonable min/max replica counts
   - Test scale-to-zero behavior in dev/test first

5. **Optimize Cold Starts**
   - Minimize container image size
   - Use lighter base images (Alpine Linux)
   - Set min replicas > 0 for latency-sensitive apps

6. **Monitor Scaling Behavior**
   - Watch replica count metrics
   - Adjust scaling thresholds based on actual usage
   - Use Application Insights for performance tracking

### Security

7. **Use Managed Identities**
   - Avoid storing credentials in configuration
   - Use Azure AD authentication where possible
   - Rotate secrets regularly

8. **Secure Networking**
   - Use internal ingress for backend services
   - Deploy into custom VNETs for network isolation
   - Implement network policies

9. **Implement Least Privilege**
   - Grant minimum required permissions
   - Use RBAC for Azure resource access
   - Audit access regularly

### Operations

10. **Use CI/CD Pipelines**
    - Automate deployments with GitHub Actions or Azure DevOps
    - Implement testing in staging environments
    - Use revision management for rollbacks

11. **Implement Observability**
    - Enable Application Insights
    - Use structured logging
    - Set up alerts for critical metrics

12. **Version Your Images**
    - Use semantic versioning for container images
    - Tag images with commit SHAs
    - Avoid using `latest` tag in production

### Cost Optimization

13. **Leverage Scale-to-Zero**
    - Enable for non-production environments
    - Use for intermittent workloads
    - Monitor cold start impact

14. **Right-Size Resources**
    - Start with minimum resources and scale up
    - Monitor CPU and memory usage
    - Adjust based on actual needs

15. **Use Free Grants**
    - Consolidate workloads to maximize free tier usage
    - Use for dev/test environments
    - Monitor consumption in Azure Cost Management

## Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [KEDA Scalers Documentation](https://keda.sh/docs/scalers/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Azure Container Apps Samples](https://github.com/Azure-Samples/container-apps-samples)

## Related Topics

- Azure Kubernetes Service (AKS)
- Azure Container Instances (ACI)
- Azure App Service
- Dapr (Distributed Application Runtime)
- KEDA (Kubernetes Event-Driven Autoscaling)
