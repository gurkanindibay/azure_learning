# Azure Kubernetes Service (AKS) Overview

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

### Vertical Pod Autoscaler (VPA)

Automatically adjusts CPU and memory requests/limits for containers.

### KEDA (Kubernetes Event-Driven Autoscaling)

Scale based on external metrics and events (queues, databases, etc.).

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

- Serverless compute with Azure Container Instances
- Pay only for running time
- Burst capacity without managing nodes

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

## References

- [AKS Documentation](https://learn.microsoft.com/en-us/azure/aks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AKS Best Practices](https://learn.microsoft.com/en-us/azure/aks/best-practices)
- [AKS Networking](https://learn.microsoft.com/en-us/azure/aks/concepts-network)
- [AKS Security](https://learn.microsoft.com/en-us/azure/aks/concepts-security)

---

## Related Topics

- [AKS Microservices State Management](./aks-microservices-state-management.md)
- [Azure Container Registry](../../azure_container_registry/azure-container-registry-acr.md)
- [Azure Container Apps Overview](../azure_container_apps/azure-container-apps-overview.md)
- [Azure Container Instances](../azure_container_instances/azure-container-instances-aci.md)
- [Azure Monitor Details](../../azure_application_insights/azure-monitor-details.md)
