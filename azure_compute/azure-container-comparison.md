# Azure Container Instances (ACI) vs Azure Container Apps (ACA)

## TL;DR
- **Azure Container Instances (ACI)**: A single-container (or container group) serverless compute for running containers on demand with hypervisor isolation and per-second billing. Great for simple, stateless workloads, burst compute and jobs, and fast ephemeral containers.
- **Azure Container Apps (ACA)**: A fully managed serverless container platform powered by Kubernetes, Dapr, and KEDA. Designed for microservices, event-driven apps, scale-to-zero, traffic splitting, and production usage with advanced autoscaling and networking.

---

## Quick summary table

| Category | Azure Container Instances (ACI) | Azure Container Apps (ACA) |
|---------|----------------------------------|------------------------------|
| Compute model | Per-container or container group, hypervisor isolated single pod | Serverless, Kubernetes-based (managed), microservices patterns supported |
| Orchestration | None (no built-in orchestration). Container group concept but no native scaling abstractions | Managed orchestration with features: revisions, traffic split, Dapr integration, KEDA for event-driven scaling |
| Scaling | Manual (create multiple instances) or via other services (AKS Virtual Kubelet) | Autoscale including scale-to-zero (KEDA), vertical and horizontal auto-scaling |
| Networking & Ingress | Public FQDN or VNet integration for private access. No built-in service mesh | Ingress with traffic splitting, internal/external ingress, virtual network support; fine-grained HTTP routing |
| Service capabilities | Ideal for simple single containers, short-lived jobs, CI tasks | Ideal for microservices, long-running services, event-driven workloads and scheduled jobs |
| Security & Isolation | Hyper-V isolation per container group | Multi-tenant platform with managed controls; support for Managed Identities, VNet, RBAC, Dapr security features |
| DevOps & Lifecycle | CLI, Portal; update by creating new instance or changing configuration | CI/CD friendly (revisions), containerapp CLI and portal, GitHub Actions or pipelines recommended |
| Logging & Monitoring | Integration with Log Analytics via diagnostic settings; container logs via CLI/portal | Built-in Log Analytics integration, improved observability with Dapr and App insights |
| Pricing | Per-second billing based on CPU, memory and storage | Consumption-based billing (vCPU/s, memory/s, requests), free allocation; Dedicated / Savings Plans available |

---

## Detailed comparison

### 1) Overview
- ACI (Azure Container Instances): Lightweight container runtime. Use when you need to run a container quickly with minimal platform management and do not require Kubernetes features (e.g., autoscaling, service discovery). ACI gives per-container-group hypervisor isolation and provides simple networking, persistent storage options (Azure file shares) and quick deployments.

- ACA (Azure Container Apps): Serverless container platform for building microservices and event-driven apps without the operational overhead of managing Kubernetes infrastructure. ACA provides features such as scale-to-zero, Dapr integration (service invocation, state stores, pub/sub), KEDA-based event-driven autoscaling, and easy traffic management and rollouts.

### 2) Compute model & architecture
- ACI:
  - Deploy container group(s) with 1+ containers sharing the same lifecycle and local network.
  - Hyper-V isolation provides strong isolation between groups.
  - No native service orchestration (no built-in load balancing / scaling beyond new instances).
  - Useful as a compute building block; often paired with AKS (Virtual Kubelet) for burst capacity.

- ACA:
  - Runs on a managed Kubernetes escrow provided by Azure behind the scenes.
  - You get Kubernetes-like patterns (microservices, labeling, service discovery) without K8s control plane management.
  - Integrations: Dapr for building distributed apps; KEDA for autoscaling; Envoy for HTTP fronting.

### 3) Orchestration & Features
- ACI:
  - No built-in orchestration — create individual containers or groups, build replication manually.
  - No native traffic splitting or progressive rollout support; updates require new instance deploy or manual replacement.

- ACA:
  - Revisions and traffic splitting — can route a percentage of traffic to different revisions for canary/blue-green deployments.
  - KEDA integration for event-driven scaling.
  - Dapr integration for service invocation, state, pub/sub, bindings.
  - Native support for scheduled jobs and background jobs.

### 4) Scaling
- ACI:
  - Manual scaling or via external orchestrators. Not a true autoscaling serverless platform; you can provision multiple ACI instances programmatically, but not simple scale-to-zero.

- ACA:
  - Autoscale horizontally and can scale-to-zero; supports multiple scaling rules (HTTP traffic, CPU, custom KEDA triggers).
  - Works for event-driven scaling and microservices where usage might be idle and needs to scale based on event sources.

### 5) Networking & Ingress
- ACI:
  - Optionally exposes a container using a public FQDN and open port mapping.
  - Can join an Azure virtual network for private access, limited host networking capabilities compared to K8s.
  - No built-in load balancer other than per-instance public IP or FQDN. For more advanced routing, combine with Azure Application Gateway or other services.

- ACA:
  - Ingress supports managed HTTP ingress and internal ingress for secure microservice communication.
  - Revisions + traffic split allows routing rules. Works well with custom domains, TLS, and path-based routing.
  - Supports VNet integration and granular network controls.

### 6) Storage & Volumes
- ACI:
  - Supports mounting Azure File shares and emptyDir-like volumes for container groups.
  - Good for simple apps where shared storage is enough.

- ACA:
  - Supports mounting storage through managed Azure offerings and stateful capabilities via Dapr state stores and external storage services (Azure blob, Azure files) — also recommended to prefer external stores for durability.

### 7) Security & Isolation
- ACI:
  - Strong hypervisor isolation by default (security boundary for container groups).
  - Managed identity support for accessing Azure resources.

- ACA:
  - Container Apps runs on a managed platform with shared infrastructure but includes multiple enterprise-grade security and governance features (Entra ID, Managed Identities, secure networking, secrets management).
  - Use Dapr with mTLS and App Identity for cross-application security.

### 8) Observability & Developer Experience
- ACI:
  - Simple CLI and Portal support for logs and status; integrate with Log Analytics and standard Azure Monitor components.
  - Limited built-in observability features beyond container logs and metrics.

- ACA:
  - Deeper integration with Log Analytics; you get revision-level metrics, advanced tracing and observability (Dapr provides telemetry hooks).
  - `az containerapp` CLI and `az containerapp up` provide quick developer workflows and `containerapp revision` for traffic management.

### 9) Pricing
- ACI:
  - Per-second billing for CPU and memory plus storage/network; no always-on minimums (but there is no scale-to-zero concept to lower cost for idle apps if you leave them running).

- ACA:
  - Consumption-based pricing, free tier allocation, and options for dedicated plans (single tenant) and savings plan. Scale-to-zero helps reduce costs for idle microservices.

### 10) Integrations & Extensibility
- ACI:
  - Works well with Azure Container Registry (ACR), Azure Functions (as a backend for long-running processes), Azure Logic Apps, and AKS Virtual Nodes.

- ACA:
  - Strongly integrated with Dapr, KEDA, Envoy, ACR, Azure Event Grid, Service Bus, and Logic Apps; supports advanced microservice patterns and connects well to serverless ecosystems.

### 11) Use Cases (when to use which)
- Use ACI when:
  - You need a single-container or small multi-container group to run quickly without orchestration.
  - For running ephemeral workload: CI/CD tasks, simple cron jobs, one-off scripts, or demonstration environments.
  - When you require strong isolation and minimal environment management.

- Use ACA when:
  - You are building microservices, event-driven backends, or distributed apps that benefit from autoscaling, traffic splitting, and Dapr-based service patterns.
  - You want scale-to-zero and consumption-based billing to reduce cost during idle times.
  - You need built-in features like in-cluster traffic splitting, service discovery, and application-level telemetry.

### 12) Limitations & Notes
- ACI:
  - Not designed for multi-container orchestration with service discovery patterns.
  - While you can run multi-container groups, advanced orchestration features (scaling, traffic routing, progressive rollouts) are not provided.

- ACA:
  - It is opinionated: it abstracts away Kubernetes detail but you cannot access Kubernetes API directly.
  - For very high-control use cases or custom K8s operators, AKS is a better fit.

---

## Examples: Quick CLI snippets

### Azure Container Instances (ACI) — Quick create
```bash
az group create --name myResourceGroup --location eastus
az container create \
  --resource-group myResourceGroup \
  --name aci-demo \
  --image mcr.microsoft.com/azuredocs/aci-helloworld \
  --dns-name-label aci-demo \
  --ports 80 \
  --os-type Linux \
  --memory 1.5 \
  --cpu 1

# View logs
az container logs --resource-group myResourceGroup --name aci-demo

# Delete
az container delete --resource-group myResourceGroup --name aci-demo
```

### Azure Container Apps (ACA) — Quick create (az containerapp up)
```bash
# Install/upgrade extension
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights

# Create a resource group and deploy
az group create --name myContainerApps --location centralus
az containerapp up \
  --name my-container-app \
  --resource-group myContainerApps \
  --location centralus \
  --environment 'my-container-apps' \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --target-port 80 \
  --ingress external \
  --query properties.configuration.ingress.fqdn

# Upgrade with new revision and split traffic
az containerapp update --name my-container-app --resource-group myContainerApps --image myregistry.azurecr.io/myapp:v2
# Then use revision/traffic commands to split traffic if needed
```

---

## Decision checklist — when to choose which
- Choose ACI if:
  - You require straightforward container runtime with minimal management.
  - Your workload is a single container or simple container group.
  - You need burst compute for AKS (virtual nodes) or ad-hoc/ephemeral jobs.

- Choose ACA if:
  - You're building microservices that require autoscaling, service discovery, event driven behavior, and traffic management.
  - You prefer a serverless developer experience with built-in microservices features.
  - You want to take advantage of Dapr or KEDA in production.

---

## Migration/Hybrid patterns
- Move from ACI to ACA:
  - If your app evolves to require microservices features, traffic management, and autoscaling, repackage your containers into ACA and leverage your environment to manage networking, traffic and state.

- Use both together:
  - Use ACI for one-off workloads, data processing jobs or for AKS burst capacity, and use ACA for the main microservices.

---

## Pros & Cons (short)
- ACI Pros: Quick deploy, simple, hypervisor isolation, low-ops, ideal for ephemeral or burst workloads.
- ACI Cons: No built-in autoscaling orchestration, limited application dev features.

- ACA Pros: Serverless microservices framework, Dapr/KEDA support, scale-to-zero, ingress and traffic management, built-in observability.
- ACA Cons: Opinionated; no direct Kubernetes API access, more complex than ACI for simple container runs.

---

## Frequently asked questions (short)
- Can ACA access Kubernetes API? No — ACA abstracts K8s; use AKS if you need K8s control plane.
- Is ACI autoscaling? Not natively — you can script or use Virtual Kubelet with AKS for bursting.
- Which is cheaper? ACA can be cheaper for microservices that scale-to-zero. ACI may be cheaper for single short-running tasks depending on usage.

---

## References
- https://learn.microsoft.com/azure/container-instances/
- https://learn.microsoft.com/azure/container-apps/
- https://learn.microsoft.com/azure/container-apps/compare-options
- Official quickstarts: `az container create` and `az containerapp up` documents

---

If you want, I can also:
- Add sample Bicep or Terraform templates for both ACI and ACA
- Provide a migration plan from ACI to ACA (or from AKS to ACA)
- Add a pricing comparison scenario with cost examples for a sample workload

Let me know which next step you'd like to take!
