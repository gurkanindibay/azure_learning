# Azure Kubernetes Service (AKS) Overview

## Table of Contents

- [What is Azure Kubernetes Service?](#what-is-azure-kubernetes-service)
- [Key Features](#key-features)
- [AKS Architecture](#aks-architecture)
- [Node Pools](#node-pools)
- [Networking Models](#networking-models)
- [Scaling Options](#scaling-options)
- [Exam Scenario: Migrating Azure Functions to AKS](#exam-scenario-migrating-azure-functions-to-aks)
- [Security Features](#security-features)
- [Monitoring and Observability](#monitoring-and-observability)
- [Upgrade and Maintenance](#upgrade-and-maintenance)
- [Storage Options](#storage-options)
- [Cost Optimization](#cost-optimization)
- [Common Use Cases](#common-use-cases)
- [Best Practices](#best-practices)
- [AKS vs. Self-Managed Kubernetes](#aks-vs-self-managed-kubernetes)
- [Pricing](#pricing)
- [Getting Started](#getting-started)
- [Troubleshooting](#troubleshooting)
- [Practice Questions](#practice-questions)
  - [Question 1: Recommending AKS Scaling Solution for Linux Containers](#question-1-recommending-aks-scaling-solution-for-linux-containers)
  - [Question 2: Deploying a New Containerized Application to Specific Nodes](#question-2-deploying-a-new-containerized-application-to-specific-nodes)
  - [Question 3: Deploying a YAML File to AKS](#question-3-deploying-a-yaml-file-to-aks)
- [References](#references)
- [Related Topics](#related-topics)

---

## What is Azure Kubernetes Service?

Azure Kubernetes Service (AKS) is a managed Kubernetes service that simplifies deploying, managing, and scaling containerized applications using Kubernetes on Azure. AKS reduces the complexity and operational overhead of managing Kubernetes by offloading much of that responsibility to Azure.

---

## Key Features

### 1. Managed Control Plane

- **Free Control Plane**: Azure manages the Kubernetes control plane at no cost
- **Automatic Updates**: Kubernetes version updates and security patches
- **High Availability**: Built-in SLA for control plane availability
- **Automatic Scaling**: Control plane scales automatically

### 2. Integrated Azure Services

- **Azure Active Directory (Entra ID)**: Integration for authentication and RBAC
- **Azure Monitor**: Container Insights for monitoring and logging
- **Azure Container Registry (ACR)**: Seamless integration for container images
- **Azure Key Vault**: Secrets management integration
- **Azure Policy**: Governance and compliance enforcement

### 3. Flexible Deployment Options

- **Multiple Node Pools**: Support for different VM sizes and OS types
- **Virtual Nodes**: Serverless compute with Azure Container Instances
- **Spot Instances**: Cost savings with Azure Spot Virtual Machines
- **ARM64 Support**: Support for ARM-based workloads

### 4. Enterprise-Grade Security

- **Network Policies**: Azure Network Policy or Calico
- **Private Clusters**: Control plane with private IP addresses
- **Azure AD Pod Identity**: Pod-level identity integration
- **Secrets Store CSI Driver**: Direct Key Vault integration
- **Image Scanning**: Built-in vulnerability scanning

### 5. Developer Tools

- **Visual Studio Code**: Azure Kubernetes Service extension
- **Azure CLI**: Command-line management
- **kubectl**: Native Kubernetes CLI support
- **Helm**: Package manager integration
- **Draft**: Streamlined development workflows

---

## AKS Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Subscription                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              AKS Cluster (Managed)                 │    │
│  │                                                     │    │
│  │  ┌─────────────────────────────────────────────┐  │    │
│  │  │  Control Plane (Managed by Azure)          │  │    │
│  │  │  - API Server                               │  │    │
│  │  │  - Scheduler                                │  │    │
│  │  │  - Controller Manager                       │  │    │
│  │  │  - etcd                                     │  │    │
│  │  └─────────────────────────────────────────────┘  │    │
│  │                                                     │    │
│  │  ┌─────────────────────────────────────────────┐  │    │
│  │  │  Node Pools (Customer Managed)             │  │    │
│  │  │                                             │  │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │    │
│  │  │  │  Node 1  │  │  Node 2  │  │  Node 3  │ │  │    │
│  │  │  │          │  │          │  │          │ │  │    │
│  │  │  │  Pods    │  │  Pods    │  │  Pods    │ │  │    │
│  │  │  └──────────┘  └──────────┘  └──────────┘ │  │    │
│  │  └─────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────┐  ┌─────────┐  ┌──────────────┐        │
│  │    ACR     │  │  Azure  │  │  Key Vault   │        │
│  │  Registry  │  │ Monitor │  │              │        │
│  └────────────┘  └─────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## Node Pools

### System Node Pools

- **Purpose**: Run critical system pods (CoreDNS, metrics-server, tunnelfront)
- **Requirements**: Minimum of 2 nodes recommended
- **VM Size**: Minimum 2 vCPUs and 4 GB memory
- **Taints**: System node pools can have taints to dedicate them to system workloads

### User Node Pools

- **Purpose**: Run application workloads
- **Flexibility**: Multiple user node pools with different configurations
- **Scaling**: Can scale to zero
- **OS Support**: Linux and Windows Server

### Node Pool Configuration Options

| Feature | Description |
|---------|-------------|
| **VM Size** | Choose from Azure VM sizes (Standard_DS2_v2, etc.) |
| **OS Type** | Linux or Windows Server |
| **Mode** | System or User |
| **Availability Zones** | Spread nodes across multiple zones |
| **Max Pods** | Maximum pods per node (default: 30) |
| **Node Taints** | Kubernetes taints for scheduling |
| **Node Labels** | Custom labels for workload placement |

---

## Networking Models

### 1. Kubenet (Basic Networking)

**Characteristics:**
- Default networking option
- Nodes get IP addresses from Azure VNet subnet
- Pods get IP addresses from a separate address space
- Network Address Translation (NAT) for pod traffic
- User-defined routes (UDRs) are automatically configured

**Pros:**
- ✅ Simple to configure
- ✅ Efficient IP address usage
- ✅ Lower cost

**Cons:**
- ❌ Pods are not directly accessible from VNet
- ❌ Limited to 400 nodes per cluster
- ❌ More complex routing

**Best For:**
- Development and testing
- Smaller clusters
- Cost-sensitive deployments

### 2. Azure CNI (Advanced Networking)

**Characteristics:**
- Pods get IP addresses directly from VNet subnet
- Pods are first-class citizens in the VNet
- Direct connectivity between pods and VNet resources
- No NAT required

**Pros:**
- ✅ Direct VNet connectivity
- ✅ Simplified network policies
- ✅ Better performance
- ✅ Support for larger clusters

**Cons:**
- ❌ Requires more IP addresses
- ❌ More complex planning
- ❌ Higher cost

**Best For:**
- Production workloads
- Enterprise scenarios
- Hybrid connectivity requirements

### 3. Azure CNI Overlay

**Characteristics:**
- Combines benefits of Kubenet and Azure CNI
- Nodes get VNet IPs, pods use private CIDR
- Overlay network for pod-to-pod communication
- Up to 1000 nodes per cluster

**Pros:**
- ✅ Efficient IP usage
- ✅ Scales better than Kubenet
- ✅ Simpler than Azure CNI

**Best For:**
- Large clusters with IP constraints
- Balance between simplicity and scale

---

## Scaling Options

### Cluster Autoscaler

Automatically adjusts the number of nodes based on resource requests:

```yaml
# Enable cluster autoscaler
az aks nodepool update \
  --resource-group myResourceGroup \
  --cluster-name myAKSCluster \
  --name nodepool1 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 10
```

**How It Works:**
1. Monitors pods that cannot be scheduled due to insufficient resources
2. Adds nodes when pods are pending
3. Removes nodes when they are underutilized

### Horizontal Pod Autoscaler (HPA)

Automatically scales the number of pod replicas based on metrics:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Key Points:**
- HPA is a core component of Kubernetes that dynamically adjusts the number of pod replicas
- Can scale based on CPU, memory, or custom metrics
- When used alongside KEDA, HPA can scale workloads in response to event-based triggers (e.g., Azure Queue Storage messages)
- KEDA acts as a metrics adapter, feeding external event metrics into Kubernetes' HPA to drive autoscaling decisions

### Vertical Pod Autoscaler (VPA)

Automatically adjusts CPU and memory requests/limits for containers.

### KEDA (Kubernetes Event-Driven Autoscaling)

KEDA enables event-driven scaling for Kubernetes workloads, including the ability to **scale from zero** — which replicates the serverless, on-demand model used in the Azure Functions Consumption plan.

**Key Features:**
- **Scale to/from Zero**: Unlike standard HPA, KEDA can scale workloads down to zero replicas when there are no events
- **Event-Driven**: Supports native integration with Azure Queue Storage triggers, Service Bus, Event Hubs, and more
- **Metrics Adapter**: KEDA monitors queue length (or other event sources) and exposes metrics to HPA, allowing Kubernetes to adjust pod count accordingly
- **Networking Support**: Works with both kubenet and Azure CNI networking models

**How KEDA Works:**
1. KEDA monitors external event sources (e.g., Azure Queue Storage)
2. Exposes custom metrics to the Kubernetes metrics API
3. HPA uses these metrics to make scaling decisions
4. Pods scale up/down based on event volume (including scaling to zero)

**Example: Azure Queue Storage Trigger**
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: azure-queue-scaledobject
spec:
  scaleTargetRef:
    name: myapp-deployment
  minReplicaCount: 0   # Scale to zero when no messages
  maxReplicaCount: 10
  triggers:
  - type: azure-queue
    metadata:
      queueName: myqueue
      queueLength: "5"  # Scale when queue has 5+ messages
      connectionFromEnv: AZURE_STORAGE_CONNECTION_STRING
```

**Installing KEDA on AKS:**
```bash
# Add KEDA Helm repository
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

# Install KEDA
helm install keda kedacore/keda --namespace keda --create-namespace

# Or enable KEDA add-on (preview)
az aks update \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --enable-keda
```

---

## Exam Scenario: Migrating Azure Functions to AKS

### Scenario

You have an Azure Functions microservice app named App1 that is hosted in the **Consumption plan**. App1 uses an **Azure Queue Storage trigger**.

You plan to migrate App1 to an Azure Kubernetes Service (AKS) cluster.

**Requirements:**
- Use the same scaling mechanism as the current deployment (event-driven, scale to zero)
- Support kubenet and Azure Container Networking Interface (CNI) networking

### Solution: Required Actions

| Action | Required | Explanation |
|--------|----------|-------------|
| **Install KEDA** | ✅ Yes | KEDA enables event-driven scaling including scale-from-zero, replicating the Azure Functions Consumption plan behavior. KEDA supports Azure Queue Storage triggers natively. |
| **Configure HPA** | ✅ Yes | HPA works with KEDA to dynamically adjust pod replicas based on queue metrics. KEDA feeds external event metrics to HPA for scaling decisions. |
| Configure Cluster Autoscaler | ❌ No | Cluster autoscaler adjusts node count based on pod scheduling needs, not external events. It doesn't handle event-driven scaling or scale-to-zero. |
| Configure Virtual Node Add-on | ❌ No | Virtual nodes allow bursting into Azure Container Instances but don't support event-driven autoscaling. It's a compute scaling feature, not an event-based trigger mechanism. |
| Install Virtual Kubelet | ❌ No | Virtual Kubelet is the underlying open-source component used by virtual nodes add-on. Microsoft recommends using the managed virtual node add-on instead of direct Virtual Kubelet installation. |

### Key Concepts Comparison

| Feature | Cluster Autoscaler | HPA | KEDA |
|---------|-------------------|-----|------|
| **What it scales** | Nodes | Pods | Pods |
| **Scaling trigger** | Pod scheduling pressure | CPU/Memory/Custom metrics | External events |
| **Scale to zero** | ❌ No | ❌ No | ✅ Yes |
| **Event-driven** | ❌ No | ❌ No (needs KEDA) | ✅ Yes |
| **Azure Queue support** | ❌ No | Via KEDA | ✅ Native |

### Virtual Nodes vs KEDA

| Aspect | Virtual Nodes | KEDA |
|--------|---------------|------|
| **Purpose** | Burst compute capacity | Event-driven scaling |
| **Mechanism** | Provisions ACI instances | Scales pod replicas |
| **Scale to zero** | ❌ No | ✅ Yes |
| **Event-driven** | ❌ No | ✅ Yes |
| **Use case** | Handle compute spikes | Serverless-like behavior |

### References

- [KEDA Concepts](https://keda.sh/docs/2.0/concepts)
- [KEDA on AKS](https://learn.microsoft.com/en-us/azure/aks/keda-about)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale)
- [AKS Cluster Autoscaler](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [AKS Virtual Nodes](https://learn.microsoft.com/en-us/azure/aks/virtual-nodes-portal)

---

## Security Features

### Azure AD Integration

```bash
# Create AKS cluster with Azure AD integration
az aks create \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --enable-aad \
  --aad-admin-group-object-ids <admin-group-id> \
  --enable-azure-rbac
```

### Azure RBAC for Kubernetes

- **Cluster Admin**: Full control over cluster resources
- **Cluster User**: Read-only access to cluster resources
- **Azure Kubernetes Service RBAC Admin**: Admin access to namespace
- **Azure Kubernetes Service RBAC Writer**: Read/write access to namespace
- **Azure Kubernetes Service RBAC Reader**: Read-only access to namespace

### Network Security

1. **Network Policies**
   - Control pod-to-pod communication
   - Support for Azure Network Policy or Calico

2. **Private Clusters**
   - API server with private IP
   - No public endpoint exposure

3. **API Server Authorized IP Ranges**
   - Restrict API server access to specific IP ranges

4. **Azure Firewall Integration**
   - Control egress traffic from cluster

### Secrets Management

1. **Azure Key Vault Provider for Secrets Store CSI Driver**
   ```yaml
   apiVersion: secrets-store.csi.x-k8s.io/v1
   kind: SecretProviderClass
   metadata:
     name: azure-keyvault
   spec:
     provider: azure
     parameters:
       keyvaultName: "myKeyVault"
       objects: |
         array:
           - |
             objectName: secret1
             objectType: secret
   ```

2. **Workload Identity**
   - Pod-level identity for accessing Azure resources
   - Federated identity credentials

---

## Monitoring and Observability

### Container Insights

```bash
# Enable Container Insights
az aks enable-addons \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --addons monitoring
```

**Features:**
- Real-time performance monitoring
- Container logs aggregation
- Resource utilization tracking
- Alerts and notifications
- Workbook templates

### Prometheus and Grafana

- **Azure Monitor managed service for Prometheus**: Collect and analyze metrics
- **Azure Managed Grafana**: Visualize metrics and logs
- Native integration with AKS

### Logging

1. **Container Logs**: Stdout/stderr from containers
2. **Kubernetes Events**: Cluster events and state changes
3. **Audit Logs**: API server audit logs
4. **Node Logs**: System logs from nodes

---

## Upgrade and Maintenance

### Kubernetes Version Upgrades

```bash
# Check available versions
az aks get-upgrades --resource-group myResourceGroup --name myAKSCluster

# Upgrade cluster
az aks upgrade \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --kubernetes-version 1.28.0
```

### Upgrade Strategies

1. **Manual Upgrades**: Full control over timing
2. **Auto-Upgrade Channels**:
   - `rapid`: Latest supported version
   - `stable`: N-1 minor version
   - `patch`: Latest patch for current minor version
   - `node-image`: Node image updates only

### Maintenance Windows

Configure when AKS can perform maintenance:

```bash
az aks maintenanceconfiguration add \
  --resource-group myResourceGroup \
  --cluster-name myAKSCluster \
  --name default \
  --weekday Monday \
  --start-hour 1
```

---

## Storage Options

### Persistent Volume Types

| Storage Class | Use Case | Performance | Redundancy |
|--------------|----------|-------------|------------|
| **Azure Disk** | Single pod access | High | LRS, ZRS |
| **Azure Files** | Shared access | Medium | LRS, ZRS, GRS |
| **Azure Blob** | Object storage | High | LRS, ZRS, GRS |
| **Azure NetApp Files** | Enterprise NAS | Very High | Built-in |

### Dynamic Provisioning

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-disk-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: managed-csi
  resources:
    requests:
      storage: 10Gi
```

---

## Cost Optimization

### 1. Right-Sizing

- Use appropriate VM sizes for workloads
- Implement resource requests and limits
- Monitor actual usage with Container Insights

### 2. Azure Spot VMs

- Use spot instances for fault-tolerant workloads
- Up to 90% cost savings
- Best for batch jobs, dev/test environments

```bash
az aks nodepool add \
  --resource-group myResourceGroup \
  --cluster-name myAKSCluster \
  --name spotnodepool \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 0 \
  --max-count 10
```

### 3. Virtual Nodes

Virtual nodes allow AKS clusters to **elastically burst to Azure Container Instances (ACI)**, dramatically reducing the time required to provision compute resources during scale-out operations.

#### Key Benefits of Virtual Nodes:
- **Rapid Provisioning**: Containers start in seconds (vs. minutes for VM-based nodes)
- **Serverless Compute**: No need to manage underlying virtual machines
- **Pay-Per-Use**: Only pay for the running time of containers
- **Unlimited Scale**: Burst capacity without pre-provisioning nodes
- **Linux Container Support**: Full support for autoscaling Linux containers

#### How Virtual Nodes Work:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AKS Cluster                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Standard Node Pool                            │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │    │
│  │  │  Node 1  │  │  Node 2  │  │  Node 3  │  (VM-based)           │    │
│  │  └──────────┘  └──────────┘  └──────────┘                       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │               Virtual Node (Powered by ACI)                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │    │
│  │  │Container │  │Container │  │Container │  │Container │  ...    │    │
│  │  │ (Burst)  │  │ (Burst)  │  │ (Burst)  │  │ (Burst)  │        │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │    │
│  │                                                                  │    │
│  │  ✓ Seconds to provision    ✓ No VM management                   │    │
│  │  ✓ Unlimited burst         ✓ Pay only when running              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Enable Virtual Nodes:

```bash
# Enable virtual nodes on an AKS cluster
az aks enable-addons \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --addons virtual-node \
  --subnet-name myVirtualNodeSubnet
```

#### Virtual Nodes vs Virtual Kubelet:

| Aspect | Virtual Nodes | Virtual Kubelet |
|--------|---------------|------------------|
| **Type** | Managed AKS add-on | Open-source project |
| **Recommended** | ✅ Yes | ❌ Use virtual nodes instead |
| **Management** | Azure-managed | Self-managed |
| **Integration** | Native AKS integration | Manual configuration |

> **Note**: Virtual Kubelet is the underlying open-source technology that powers virtual nodes in AKS. Microsoft recommends using the managed **virtual nodes add-on** instead of deploying Virtual Kubelet directly.

### 4. Cluster Autoscaler

- Scale nodes based on demand
- Remove unused nodes automatically

### 5. Reserved Instances

- Commit to 1 or 3 years for significant discounts
- Up to 72% savings compared to pay-as-you-go

---

## Common Use Cases

### 1. Microservices Architecture

Deploy and manage distributed microservices with:
- Service discovery
- Load balancing
- State management (Dapr)
- API gateways

### 2. Batch Processing

Run parallel batch jobs with:
- Job scheduling
- Auto-scaling
- Spot instances for cost savings

### 3. CI/CD Pipelines

Build and deploy applications with:
- GitOps workflows (Flux, ArgoCD)
- Automated testing
- Rolling updates

### 4. Machine Learning

Train and serve ML models with:
- GPU-enabled node pools
- Distributed training
- Model serving infrastructure

### 5. Event-Driven Applications

Process events and messages with:
- KEDA for auto-scaling
- Azure Event Grid integration
- Queue-based processing

---

## Best Practices

### 1. Cluster Design

✅ Separate system and user node pools  
✅ Use multiple node pools for different workload types  
✅ Enable availability zones for high availability  
✅ Plan IP address space carefully (especially with Azure CNI)  
✅ Implement proper network segmentation

### 2. Security

✅ Enable Azure AD integration  
✅ Use Azure RBAC for authorization  
✅ Implement network policies  
✅ Use private clusters for sensitive workloads  
✅ Integrate with Azure Key Vault for secrets  
✅ Enable audit logging  
✅ Scan container images for vulnerabilities

### 3. Monitoring

✅ Enable Container Insights  
✅ Set up alerts for critical metrics  
✅ Monitor resource utilization  
✅ Collect and analyze logs  
✅ Track cluster health and performance

### 4. Resource Management

✅ Define resource requests and limits for all containers  
✅ Use namespaces to organize workloads  
✅ Implement resource quotas  
✅ Use horizontal pod autoscaling  
✅ Enable cluster autoscaler

### 5. High Availability

✅ Deploy across multiple availability zones  
✅ Use pod disruption budgets  
✅ Implement liveness and readiness probes  
✅ Configure multiple replicas for critical workloads  
✅ Use anti-affinity rules for pod distribution

### 6. Upgrades

✅ Test upgrades in non-production environments  
✅ Review release notes before upgrading  
✅ Enable auto-upgrade for patch versions  
✅ Configure maintenance windows  
✅ Have a rollback plan

---

## AKS vs. Self-Managed Kubernetes

| Aspect | AKS | Self-Managed |
|--------|-----|--------------|
| **Control Plane** | Managed by Azure (Free) | Self-managed (Cost + Effort) |
| **Updates** | Automated options | Manual process |
| **Scaling** | Built-in autoscaling | Manual configuration |
| **Monitoring** | Integrated with Azure Monitor | Requires setup |
| **Security** | Azure AD, RBAC integration | Manual integration |
| **Support** | Microsoft support | Community or vendor |
| **Cost** | Pay only for nodes | Pay for all infrastructure |
| **Complexity** | Lower | Higher |

---

## Pricing

### Control Plane

- **Free**: Control plane is provided at no cost
- **Standard Tier**: SLA-backed uptime (99.95% with AZ, 99.9% without)
- **Premium Tier**: Additional features (planned)

### Node Costs

- Pay for VM instances used as nodes
- Pricing based on VM size and region
- Additional costs for:
  - Storage (disks, files)
  - Networking (bandwidth, load balancers)
  - Public IP addresses
  - Azure Monitor (if enabled)

### Cost Estimation

```
Monthly Cost = (Node Count × Node VM Cost) + Storage + Networking + Monitoring
```

**Example:**
- 3 nodes × Standard_D2s_v3 ($70/month each) = $210
- 100 GB Premium SSD = $15
- Load balancer = $20
- Container Insights = $15
- **Total: ~$260/month**

---

## Getting Started

### Create an AKS Cluster

```bash
# Create resource group
az group create --name myResourceGroup --location eastus

# Create AKS cluster
az aks create \
  --resource-group myResourceGroup \
  --name myAKSCluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --network-plugin azure \
  --enable-managed-identity

# Get credentials
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

# Verify connection
kubectl get nodes
```

### Deploy an Application

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
  selector:
    app: nginx
```

```bash
# Apply configuration
kubectl apply -f nginx-deployment.yaml

# Get service external IP
kubectl get service nginx-service
```

---

## Troubleshooting

### Common Issues

1. **Pods Not Starting**
   - Check pod events: `kubectl describe pod <pod-name>`
   - Verify resource requests and limits
   - Check node capacity

2. **Networking Issues**
   - Verify network policies
   - Check service endpoints: `kubectl get endpoints`
   - Review NSG rules

3. **Authentication Errors**
   - Verify Azure AD configuration
   - Check RBAC permissions
   - Regenerate credentials if needed

4. **Performance Issues**
   - Review Container Insights metrics
   - Check resource utilization
   - Verify pod distribution across nodes

### Diagnostic Tools

```bash
# Get cluster info
kubectl cluster-info

# Check node status
kubectl get nodes -o wide

# View events
kubectl get events --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods

# Get pod logs
kubectl logs <pod-name>

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash
```

---

## Practice Questions

### Question 1: Recommending AKS Scaling Solution for Linux Containers

#### Scenario

You have an Azure subscription. You need to recommend an Azure Kubernetes Service (AKS) solution that will use **Linux nodes**.

The solution must meet the following requirements:
- **Minimize the time** it takes to provision compute resources during scale-out operations
- **Support autoscaling** of Linux containers
- **Minimize administrative effort**

**Question:** Which scaling option should you recommend?

---

#### Options

A. Horizontal Pod Autoscaler  
B. Cluster Autoscaler  
C. Virtual Nodes  
D. Virtual Kubelet

---

**Correct Answer:** **C. Virtual Nodes**

---

### Detailed Explanation

#### Why Virtual Nodes is Correct ✅

Virtual nodes in Azure Kubernetes Service (AKS), powered by Virtual Kubelet, allow the AKS cluster to **elastically burst to Azure Container Instances (ACI)**. This dramatically reduces the time required to provision compute resources during scale-out operations because **containers can start in seconds**, unlike traditional AKS nodes which require VM provisioning.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Scaling Time Comparison                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Traditional Node Scaling (Cluster Autoscaler):                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Request → Provision VM → Boot OS → Pull Image → Start Container │   │
│  │                                                                   │   │
│  │  Time: Minutes (typically 3-10 minutes)                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Virtual Nodes (Burst to ACI):                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  Request → Start Container on ACI                                 │   │
│  │                                                                   │   │
│  │  Time: Seconds                                                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

##### Key Benefits for This Scenario:

| Requirement | How Virtual Nodes Meets It |
|-------------|---------------------------|
| **Minimize provisioning time** | Containers start in seconds (vs. minutes for VM-based nodes) |
| **Support Linux autoscaling** | Full support for autoscaling Linux containers |
| **Minimize admin effort** | No need to manage underlying VMs or node infrastructure |

---

#### Why Other Options Are Incorrect ❌

##### ❌ A. Horizontal Pod Autoscaler (HPA)

| Aspect | Details |
|--------|--------|
| **What it does** | Scales the number of pods within a node pool based on CPU or custom metrics |
| **Why incorrect** | Does not provide or manage underlying compute resources |
| **Limitation** | Assumes enough nodes already exist to schedule the pods |

HPA is useful for scaling pods, but it **cannot provision new compute capacity** — it only adjusts pod replicas within existing nodes.

---

##### ❌ B. Cluster Autoscaler

| Aspect | Details |
|--------|--------|
| **What it does** | Automatically increases/decreases the number of VM nodes in a node pool |
| **Why incorrect** | Still involves provisioning VMs, which is **slower** than virtual nodes |
| **Limitation** | Requires more management overhead; nodes take minutes to provision |

While cluster autoscaler can add nodes automatically, each new node requires **VM provisioning** (typically 3-10 minutes), which doesn't meet the "minimize time" requirement.

---

##### ❌ D. Virtual Kubelet

| Aspect | Details |
|--------|--------|
| **What it is** | The underlying open-source technology used by virtual nodes |
| **Why incorrect** | Not a standalone option in AKS; requires manual deployment and configuration |
| **Recommendation** | Use the managed **virtual nodes add-on** instead |

Virtual Kubelet is the open-source project that enables virtual nodes, but you **shouldn't deploy it directly** in AKS. Instead, enable the virtual nodes add-on which abstracts the complexity and integrates natively with ACI.

---

### Scaling Options Comparison

| Option | Scales | Provisioning Time | Admin Effort | Best For |
|--------|--------|-------------------|--------------|----------|
| **Virtual Nodes** | Containers to ACI | Seconds | ✅ Minimal | Burst workloads, rapid scaling |
| **Cluster Autoscaler** | VM Nodes | Minutes | Medium | Steady growth, predictable loads |
| **Horizontal Pod Autoscaler** | Pod replicas | N/A (uses existing nodes) | Low | Scaling within capacity |
| **Virtual Kubelet** | Containers | Seconds | ❌ High (manual) | Not recommended directly |

---

### Reference Links

**Official Documentation:**
- [AKS Virtual Nodes](https://learn.microsoft.com/en-us/azure/aks/virtual-nodes)
- [Virtual Nodes CLI](https://learn.microsoft.com/en-us/azure/aks/virtual-nodes-cli)
- [AKS Scaling Concepts - Virtual Nodes](https://learn.microsoft.com/en-us/azure/aks/concepts-scale#virtual-nodes)
- [Cluster Autoscaler](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler?tabs=azure-cli)
- [Horizontal Pod Autoscaler Concepts](https://learn.microsoft.com/en-us/azure/aks/concepts-scale#horizontal-pod-autoscaler)
- [Virtual Kubelet](https://virtual-kubelet.io)

**Domain:** Design Infrastructure Solutions

---

### Question 2: Deploying a New Containerized Application to Specific Nodes

#### Scenario

You have created an Azure Kubernetes Service (AKS) cluster with the following settings:

| Setting | Value |
|---------|-------|
| **Cluster Name** | getcloudskillscluster |
| **Node Pool** | agentpool (System) |
| **Node Count** | 2 |
| **Node Size** | Standard_DS2_v2 |

An application has been deployed to the node pool in a containerized format.

You need to deploy another containerized application called "getcloudskillsapp2" that should run on **four nodes**, each of size **"DS3 v2"**.

**Question:** What is the **first step** you need to take to meet this requirement?

---

#### Options

A. Modify the autoscale settings for the Kubernetes cluster  
B. Upgrade the cluster  
C. Enable virtual nodes for the cluster  
D. Create a new node pool

---

**Correct Answer:** **D. Create a new node pool**

---

### Detailed Explanation

#### Why Create a New Node Pool is Correct ✅

Creating a new node pool is the correct first step because:

1. **Different VM Size Required**: The existing node pool uses `Standard_DS2_v2`, but the new application requires `Standard_DS3_v2` nodes
2. **Specific Node Count**: The new application needs exactly 4 nodes dedicated to it
3. **Workload Isolation**: Node pools allow you to run different workloads with different resource requirements on separate sets of nodes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AKS Cluster: getcloudskillscluster                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Existing System Node Pool (agentpool):                                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  VM Size: Standard_DS2_v2    |    Node Count: 2                  │   │
│  │  ┌─────────────┐  ┌─────────────┐                                │   │
│  │  │   Node 1    │  │   Node 2    │                                │   │
│  │  │ (Existing   │  │ (Existing   │                                │   │
│  │  │  App Pods)  │  │  App Pods)  │                                │   │
│  │  └─────────────┘  └─────────────┘                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  New User Node Pool (to be created):                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  VM Size: Standard_DS3_v2    |    Node Count: 4                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │  Node 1  │ │  Node 2  │ │  Node 3  │ │  Node 4  │            │   │
│  │  │ (app2)   │ │ (app2)   │ │ (app2)   │ │ (app2)   │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

##### How to Create a New Node Pool:

```bash
# Azure CLI command to create a new node pool
az aks nodepool add \
    --resource-group <resource-group> \
    --cluster-name getcloudskillscluster \
    --name app2pool \
    --node-count 4 \
    --node-vm-size Standard_DS3_v2 \
    --mode User
```

---

#### Why Other Options Are Incorrect ❌

##### ❌ A. Modify the autoscale settings for the Kubernetes cluster

| Aspect | Details |
|--------|---------|
| **What it does** | Adjusts the number of nodes in a cluster based on workload demand |
| **Why incorrect** | Autoscaling settings are for dynamic scaling, not for specifying node sizes or creating dedicated nodes for a new application |
| **Limitation** | Cannot change VM sizes or guarantee specific number of nodes for a particular application |

Autoscaling helps manage resource allocation dynamically but doesn't help deploy a new application to specific nodes with specific VM sizes.

---

##### ❌ B. Upgrade the cluster

| Aspect | Details |
|--------|---------|
| **What it does** | Updates the Kubernetes version or underlying infrastructure |
| **Why incorrect** | Upgrading doesn't change node configurations or add nodes with different sizes |
| **Limitation** | This is a maintenance operation, not a deployment or scaling operation |

Cluster upgrades are for keeping the Kubernetes version current, not for adding new compute resources.

---

##### ❌ C. Enable virtual nodes for the cluster

| Aspect | Details |
|--------|---------|
| **What it does** | Provides serverless compute by bursting to Azure Container Instances |
| **Why incorrect** | Virtual nodes don't provide dedicated VMs with specific sizes |
| **Limitation** | Virtual nodes run on ACI, not on dedicated DS3 v2 VMs as required |

Virtual nodes are excellent for rapid scaling and burst workloads but don't meet the requirement of running on four dedicated nodes of a specific VM size.

---

### Key Concepts: Node Pool Management

| Concept | Description |
|---------|-------------|
| **System Node Pool** | Runs critical system pods (CoreDNS, metrics-server); at least one required per cluster |
| **User Node Pool** | Runs application workloads; can have different VM sizes and configurations |
| **Multiple Node Pools** | Allows different workloads to run on appropriate hardware |
| **Node Selectors/Taints** | Used to schedule specific pods to specific node pools |

---

### When to Create a New Node Pool

| Scenario | Solution |
|----------|----------|
| Application needs different VM size | Create new node pool with required VM size |
| Need dedicated nodes for specific workload | Create user node pool with taints/labels |
| Running Windows containers alongside Linux | Create Windows node pool |
| Cost optimization with Spot VMs | Create node pool with Spot instances |
| Different availability zone requirements | Create node pool in specific zones |

---

### Reference Links

**Official Documentation:**
- [AKS Node Pools Overview](https://learn.microsoft.com/en-us/azure/aks/create-node-pools)
- [Add Node Pools to AKS](https://learn.microsoft.com/en-us/azure/aks/create-node-pools#add-a-node-pool)
- [Manage Node Pools](https://learn.microsoft.com/en-us/azure/aks/manage-node-pools)
- [Multiple Node Pools](https://learn.microsoft.com/en-us/azure/aks/use-multiple-node-pools)

**Domain:** Design Infrastructure Solutions

---

### Question 3: Deploying a YAML File to AKS

#### Scenario

You deploy an Azure Kubernetes Service (AKS) cluster named **AKS1**.

You need to deploy a YAML file to AKS1.

**Solution:** From Azure CLI, you run `az aks`.

**Question:** Does this meet the goal?

---

#### Options

A. Yes  
B. No

---

**Correct Answer:** **B. No**

---

### Detailed Explanation

#### Why "No" is Correct ✅

The `az aks` command in Azure CLI is used for **managing AKS clusters** (creating, updating, deleting, scaling), but it **does not directly deploy YAML files** to an AKS cluster.

To deploy a YAML file to an AKS cluster, you must use **`kubectl`**, which is the Kubernetes command-line tool for interacting with Kubernetes clusters.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Tool Responsibilities                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  az aks (Azure CLI):                                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ✅ Create AKS cluster                                            │   │
│  │  ✅ Delete AKS cluster                                            │   │
│  │  ✅ Scale cluster                                                 │   │
│  │  ✅ Get credentials (kubeconfig)                                  │   │
│  │  ✅ Manage node pools                                             │   │
│  │  ✅ Enable/disable add-ons                                        │   │
│  │  ✅ Upgrade cluster                                               │   │
│  │  ❌ Deploy applications/YAML files                                │   │
│  │  ❌ Manage pods, services, deployments                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  kubectl (Kubernetes CLI):                                               │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ❌ Create AKS cluster                                            │   │
│  │  ❌ Delete AKS cluster                                            │   │
│  │  ✅ Deploy YAML files                                             │   │
│  │  ✅ Manage pods, services, deployments                            │   │
│  │  ✅ View logs                                                     │   │
│  │  ✅ Execute commands in pods                                      │   │
│  │  ✅ Scale deployments                                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

#### Correct Solution: Using kubectl ✅

##### Step 1: Get AKS Credentials

Before you can use `kubectl` with your AKS cluster, you need to configure it with cluster credentials:

```bash
# Get AKS credentials and configure kubectl
az aks get-credentials --resource-group myResourceGroup --name AKS1
```

This command:
- Downloads the Kubernetes configuration
- Merges it with your `~/.kube/config` file
- Sets AKS1 as the current context

##### Step 2: Deploy YAML File

```bash
# Deploy the YAML file to AKS
kubectl apply -f deployment.yaml
```

##### Example YAML File (deployment.yaml):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: nginx
```

##### Step 3: Verify Deployment

```bash
# Check deployment status
kubectl get deployments

# Check pods
kubectl get pods

# Check services
kubectl get services

# Detailed information
kubectl describe deployment nginx-deployment
```

---

#### Command Comparison

| Task | Correct Tool | Command |
|------|--------------|---------|
| **Create AKS cluster** | `az aks` | `az aks create --resource-group myRG --name myAKS` |
| **Get cluster credentials** | `az aks` | `az aks get-credentials --resource-group myRG --name myAKS` |
| **Deploy YAML file** | `kubectl` | `kubectl apply -f deployment.yaml` |
| **Delete resources in cluster** | `kubectl` | `kubectl delete -f deployment.yaml` |
| **Scale deployment** | `kubectl` | `kubectl scale deployment nginx --replicas=5` |
| **View pod logs** | `kubectl` | `kubectl logs <pod-name>` |
| **Add node pool** | `az aks` | `az aks nodepool add --cluster-name myAKS --name pool2` |
| **Upgrade cluster** | `az aks` | `az aks upgrade --resource-group myRG --name myAKS` |

---

#### Key Concepts

| Concept | Description |
|---------|-------------|
| **Azure CLI (az aks)** | Manages the AKS **infrastructure** (cluster lifecycle, nodes, networking) |
| **kubectl** | Manages **workloads** running inside the Kubernetes cluster (pods, services, deployments) |
| **YAML Manifest** | Declarative configuration file that defines Kubernetes resources |
| **kubeconfig** | Configuration file that contains cluster connection details and credentials |

---

#### Common Workflow

```bash
# 1. Create AKS cluster (Azure CLI)
az aks create \
  --resource-group myResourceGroup \
  --name AKS1 \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys

# 2. Get credentials (Azure CLI)
az aks get-credentials --resource-group myResourceGroup --name AKS1

# 3. Deploy application (kubectl)
kubectl apply -f deployment.yaml

# 4. Monitor deployment (kubectl)
kubectl get pods -w

# 5. Get service endpoint (kubectl)
kubectl get service nginx-service

# Later: Scale node pool if needed (Azure CLI)
az aks nodepool scale \
  --resource-group myResourceGroup \
  --cluster-name AKS1 \
  --name nodepool1 \
  --node-count 5
```

---

#### Why You Cannot Use "az aks" to Deploy YAML ❌

The `az aks` command set doesn't include any subcommands for deploying YAML files or managing Kubernetes resources. Available `az aks` subcommands include:

- `az aks create` - Create cluster
- `az aks delete` - Delete cluster
- `az aks get-credentials` - Get credentials
- `az aks nodepool` - Manage node pools
- `az aks update` - Update cluster
- `az aks upgrade` - Upgrade cluster
- `az aks scale` - Scale node count
- `az aks enable-addons` - Enable add-ons

**None of these deploy YAML files.**

---

### Reference Links

**Official Documentation:**
- [Deploy to AKS using kubectl](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- [kubectl apply command](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#apply)
- [az aks command reference](https://learn.microsoft.com/en-us/cli/azure/aks)
- [kubectl overview](https://kubernetes.io/docs/reference/kubectl/)
- [AKS get-credentials](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-get-credentials)

**Domain:** Design Infrastructure Solutions / Implement and Manage Infrastructure

---

## References

- [AKS Documentation](https://learn.microsoft.com/en-us/azure/aks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AKS Best Practices](https://learn.microsoft.com/en-us/azure/aks/best-practices)
- [AKS Networking](https://learn.microsoft.com/en-us/azure/aks/concepts-network)
- [AKS Security](https://learn.microsoft.com/en-us/azure/aks/concepts-security)
- [AKS Virtual Nodes](https://learn.microsoft.com/en-us/azure/aks/virtual-nodes)
- [AKS Scaling Concepts](https://learn.microsoft.com/en-us/azure/aks/concepts-scale)

---

## Related Topics

- [AKS Microservices State Management](./aks-microservices-state-management.md)
- [Azure Container Registry](../../azure_container_registry/azure-container-registry-acr.md)
- [Azure Container Apps Overview](../azure_container_apps/azure-container-apps-overview.md)
- [Azure Container Instances](../azure_container_instances/azure-container-instances-aci.md)
- [Azure Monitor Details](../../azure_application_insights/azure-monitor-details.md)
