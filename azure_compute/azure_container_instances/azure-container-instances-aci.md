# Azure Container Instances (ACI)

## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Container Groups](#container-groups)
  - [Container Instances](#container-instances)
  - [Resource Allocation](#resource-allocation)
- [Container Restart Policies](#container-restart-policies)
  - [Policy Types](#policy-types)
  - [OnFailure Policy](#onfailure-policy)
  - [Always Policy](#always-policy)
  - [Never Policy](#never-policy)
  - [Policy Comparison](#policy-comparison)
- [Creating Container Instances](#creating-container-instances)
  - [Basic Container Creation](#basic-container-creation)
  - [Container Group Creation](#container-group-creation)
  - [With Restart Policy](#with-restart-policy)
- [Managing Container Instances](#managing-container-instances)
  - [Restart Containers](#restart-containers)
  - [Stop Containers](#stop-containers)
  - [Start Containers](#start-containers)
  - [Delete Containers](#delete-containers)
  - [View Logs](#view-logs)
  - [Execute Commands](#execute-commands)
- [Container Group Features](#container-group-features)
  - [Multi-Container Groups](#multi-container-groups)
  - [Networking](#networking)
  - [Storage Volumes](#storage-volumes)
  - [Environment Variables](#environment-variables)
  - [Secret Volumes](#secret-volumes)
- [Deployment Methods](#deployment-methods)
- [Common Scenarios](#common-scenarios)
- [Best Practices](#best-practices)
- [Key Takeaways](#key-takeaways)
- [References](#references)

## Overview

Azure Container Instances (ACI) is a service that enables you to run containers directly on Azure without managing virtual machines or adopting higher-level orchestration services. It's the fastest and simplest way to run a container in Azure.

**Key Features:**
- Fast startup times (seconds)
- Per-second billing
- Hypervisor-level security
- Custom sizes (CPU and memory)
- Persistent storage with Azure Files
- Linux and Windows containers
- Public IP connectivity and DNS name
- Virtual network deployment

**Use Cases:**
- Simple applications and task automation
- Build and test environments
- Batch jobs and data processing
- Event-driven applications
- Development and testing
- CI/CD build agents

## Key Concepts

### Container Groups

A **container group** is a collection of containers that get scheduled on the same host machine. Containers in a container group share:
- Lifecycle
- Resources
- Local network
- Storage volumes

Similar to a pod in Kubernetes.

**Example:**
```
Container Group: myapp-group
├── Container 1: web (nginx)
├── Container 2: app (node.js)
└── Container 3: sidecar (logging agent)
```

### Container Instances

A **container instance** is a single container running within a container group. Each instance can:
- Run a different container image
- Have different resource allocations
- Be exposed on different ports
- Have specific restart policies (group-level)

### Resource Allocation

Resources are allocated at the container level:
- **CPU**: Specified in cores (0.5, 1, 2, etc.)
- **Memory**: Specified in GB (0.5, 1, 2, 4, etc.)
- **GPU**: Optional GPU resources (Premium tier)

## Container Restart Policies

Restart policies define how containers behave when their processes terminate. The policy is set at the **container group level** and applies to all containers in the group.

### Policy Types

Azure Container Instances supports three restart policies:

1. **OnFailure** - Restart only on failure (non-zero exit code)
2. **Always** - Always restart regardless of exit code
3. **Never** - Never restart (run once)

### OnFailure Policy

**Description:** Containers restart only when the process terminates with a **non-zero exit code** (error condition).

**Use Cases:**
- Batch jobs that may fail and need retry
- Data processing tasks with error handling
- Background workers that should recover from failures
- Tasks that need automatic recovery on errors

**Behavior:**
- Exit code 0 (success) → Container stops, no restart
- Exit code ≠ 0 (failure) → Container restarts
- Ideal for tasks that should complete successfully

**Example:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy OnFailure
```

**Use case example - Data processing:**
```bash
az container create \
  --resource-group data-processing-rg \
  --name data-processor \
  --image mycompany.azurecr.io/data-processor:latest \
  --restart-policy OnFailure \
  --cpu 2 \
  --memory 4
```

If the data processing fails (database connection error, file not found, etc.), the container automatically restarts. If processing completes successfully (exit code 0), the container stops.

### Always Policy

**Description:** Containers **always restart** regardless of exit code (success or failure).

**Use Cases:**
- Long-running services
- Web servers and APIs
- Monitoring agents
- Continuous background processes
- Services that should never stop

**Behavior:**
- Exit code 0 (success) → Container restarts
- Exit code ≠ 0 (failure) → Container restarts
- Container runs indefinitely until manually stopped

**Example:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Always
```

**Use case example - Web API:**
```bash
az container create \
  --resource-group web-api-rg \
  --name web-api \
  --image nginx:latest \
  --restart-policy Always \
  --cpu 1 \
  --memory 1.5 \
  --dns-name-label my-web-api \
  --ports 80 443
```

The web server should always be running. If it crashes or stops for any reason, it automatically restarts.

### Never Policy

**Description:** Containers **never restart** and run at most once.

**Use Cases:**
- One-time tasks
- Database migrations
- Backup operations
- Deployment scripts
- Short-lived batch jobs that shouldn't retry

**Behavior:**
- Exit code 0 (success) → Container stops, no restart
- Exit code ≠ 0 (failure) → Container stops, no restart
- Container runs exactly once

**Example:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Never
```

**Use case example - Database migration:**
```bash
az container create \
  --resource-group migration-rg \
  --name db-migration \
  --image mycompany.azurecr.io/db-migration:v1.0 \
  --restart-policy Never \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    DB_HOST=mydbserver.database.azure.com \
    DB_NAME=production
```

The migration should run once. Whether it succeeds or fails, you want to review logs before attempting again.

### Policy Comparison

| Restart Policy | Exit Code 0 (Success) | Exit Code ≠ 0 (Failure) | Use Case |
|----------------|----------------------|------------------------|----------|
| **OnFailure** ✅ | Stop (no restart) | Restart automatically | Batch jobs, tasks that should succeed |
| **Always** | Restart automatically | Restart automatically | Long-running services, web servers |
| **Never** | Stop (no restart) | Stop (no restart) | One-time tasks, migrations |

**Decision Tree:**

```
Do you want the container to run continuously?
├── YES → Use "Always"
│         (web servers, APIs, monitoring)
│
└── NO → Is this a task that might fail and should retry?
          ├── YES → Use "OnFailure"
          │         (batch jobs, data processing)
          │
          └── NO → Use "Never"
                    (one-time scripts, migrations)
```

## Creating Container Instances

### Basic Container Creation

```bash
# Simple container with default settings
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image nginx:latest
```

### Container Group Creation

```bash
# Container with specific resources
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --cpu 2 \
  --memory 4 \
  --os-type Linux
```

### With Restart Policy

#### Example 1: OnFailure (Task that should succeed) ✅

```bash
# Correct answer for the exam question
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy OnFailure
```

**Why this is correct:**
- Containers restart only when process terminates due to **error** (non-zero exit code)
- Matches requirement: "restart when the process executed in the container group terminates due to an error"
- Appropriate for tasks that should complete successfully but may fail

#### Example 2: Always (Continuous service) ❌ for the scenario

```bash
# This is INCORRECT for the exam question
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Always
```

**Why this is incorrect for the scenario:**
- Containers restart **always**, even on successful completion (exit code 0)
- Requirement specifies: "restart when terminates due to an error"
- "Always" would restart even without errors
- Appropriate for services that should run indefinitely, not error-based restart

#### Example 3: Never (One-time task) ❌ for the scenario

```bash
# This is INCORRECT for the exam question
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Never
```

**Why this is incorrect:**
- Containers **never restart**, even on failure
- Requirement specifies restart on error
- Appropriate for one-time tasks only

## Managing Container Instances

### Restart Containers

```bash
# Manually restart all containers in a container group
az container restart \
  --name mycontainer \
  --resource-group myResourceGroup
```

```bash
# Restart without waiting for completion
az container restart \
  --name mycontainer \
  --resource-group myResourceGroup \
  --no-wait
```

**Important:** The `az container restart` command **manually restarts** containers. It does **NOT** define or configure a restart policy. The restart policy is defined during container creation with `az container create --restart-policy`.

### Stop Containers

```bash
# Stop container group
az container stop \
  --name mycontainer \
  --resource-group myResourceGroup
```

### Start Containers

```bash
# Start stopped container group
az container start \
  --name mycontainer \
  --resource-group myResourceGroup
```

### Delete Containers

```bash
# Delete container group
az container delete \
  --name mycontainer \
  --resource-group myResourceGroup \
  --yes
```

### View Logs

```bash
# View container logs
az container logs \
  --name mycontainer \
  --resource-group myResourceGroup

# View logs for specific container in group
az container logs \
  --name mycontainer \
  --resource-group myResourceGroup \
  --container-name sidecar
```

### Execute Commands

```bash
# Execute command in running container
az container exec \
  --name mycontainer \
  --resource-group myResourceGroup \
  --exec-command "/bin/bash"

# Execute specific command
az container exec \
  --name mycontainer \
  --resource-group myResourceGroup \
  --exec-command "ls -la /app"
```

## Container Group Features

### Multi-Container Groups

Deploy multiple containers that share resources:

```bash
# Deploy using YAML file
az container create \
  --resource-group myResourceGroup \
  --file multi-container-group.yaml
```

**multi-container-group.yaml:**
```yaml
apiVersion: 2021-09-01
location: eastus
name: myContainerGroup
properties:
  containers:
  - name: web
    properties:
      image: nginx:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1.5
      ports:
      - port: 80
        protocol: TCP
  - name: sidecar
    properties:
      image: fluent/fluentd:latest
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
  restartPolicy: Always
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - port: 80
      protocol: TCP
tags: null
type: Microsoft.ContainerInstance/containerGroups
```

### Networking

```bash
# Public IP with DNS label
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image nginx:latest \
  --dns-name-label myapp-unique \
  --ports 80 443

# Multiple ports
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --ports 80 8080 443

# Virtual network deployment (requires delegation)
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image nginx:latest \
  --vnet myVNet \
  --subnet mySubnet
```

### Storage Volumes

```bash
# Mount Azure Files share
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key <storage-key> \
  --azure-file-volume-share-name myshare \
  --azure-file-volume-mount-path /mnt/data

# Empty directory volume (ephemeral)
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --command-line "/bin/sh -c 'echo hello > /data/test.txt && cat /data/test.txt'"
```

### Environment Variables

```bash
# Pass environment variables
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --environment-variables \
    APP_ENV=production \
    LOG_LEVEL=info \
    DATABASE_HOST=mydb.database.azure.com

# Secure environment variables
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --secure-environment-variables \
    DB_PASSWORD=mySecurePassword123 \
    API_KEY=abc123xyz
```

### Secret Volumes

```bash
# Mount secrets as files (using YAML)
az container create \
  --resource-group myResourceGroup \
  --file container-with-secrets.yaml
```

**container-with-secrets.yaml:**
```yaml
apiVersion: 2021-09-01
location: eastus
name: myapp
properties:
  containers:
  - name: app
    properties:
      image: myapp:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1.5
      volumeMounts:
      - name: secrets
        mountPath: /mnt/secrets
        readOnly: true
  volumes:
  - name: secrets
    secret:
      mysecret: <base64-encoded-secret>
      mykey: <base64-encoded-key>
  restartPolicy: OnFailure
  osType: Linux
type: Microsoft.ContainerInstance/containerGroups
```

## Deployment Methods

### 1. Azure CLI

```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image nginx:latest \
  --restart-policy Always
```

### 2. Azure Portal

1. Navigate to Container Instances
2. Click "Create"
3. Fill in details (name, image, resources)
4. Configure networking and restart policy
5. Review and create

### 3. ARM Template

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2021-09-01",
      "name": "mycontainer",
      "location": "[resourceGroup().location]",
      "properties": {
        "containers": [
          {
            "name": "web",
            "properties": {
              "image": "nginx:latest",
              "resources": {
                "requests": {
                  "cpu": 1,
                  "memoryInGb": 1.5
                }
              },
              "ports": [
                {
                  "port": 80,
                  "protocol": "TCP"
                }
              ]
            }
          }
        ],
        "restartPolicy": "OnFailure",
        "osType": "Linux",
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "port": 80,
              "protocol": "TCP"
            }
          ]
        }
      }
    }
  ]
}
```

### 4. PowerShell

```powershell
New-AzContainerGroup `
  -ResourceGroupName myResourceGroup `
  -Name mycontainer `
  -Image nginx:latest `
  -RestartPolicy OnFailure `
  -Cpu 1 `
  -MemoryInGB 1.5
```

### 5. Docker CLI (experimental)

```bash
# Login to Azure
docker login azure

# Create ACI context
docker context create aci myacicontext

# Use ACI context
docker context use myacicontext

# Run container in ACI
docker run -d -p 80:80 nginx:latest
```

## Common Scenarios

### Scenario 1: Batch Processing with Error Recovery

**Requirement:** Process files from storage, restart on failure

```bash
az container create \
  --resource-group batch-processing-rg \
  --name file-processor \
  --image mycompany.azurecr.io/file-processor:latest \
  --restart-policy OnFailure \
  --cpu 2 \
  --memory 4 \
  --azure-file-volume-account-name mystorageaccount \
  --azure-file-volume-account-key <key> \
  --azure-file-volume-share-name input-files \
  --azure-file-volume-mount-path /data/input \
  --environment-variables \
    BATCH_SIZE=100 \
    OUTPUT_PATH=/data/output
```

### Scenario 2: Long-Running Web Service

**Requirement:** Web API that should always be available

```bash
az container create \
  --resource-group web-services-rg \
  --name customer-api \
  --image mycompany.azurecr.io/customer-api:v2.0 \
  --restart-policy Always \
  --cpu 2 \
  --memory 3.5 \
  --dns-name-label customer-api-prod \
  --ports 80 443 \
  --environment-variables \
    ASPNETCORE_ENVIRONMENT=Production \
    ASPNETCORE_URLS="http://+:80" \
  --secure-environment-variables \
    ConnectionStrings__Database="Server=..." \
    API_KEY="..."
```

### Scenario 3: One-Time Database Migration

**Requirement:** Run migration script once, no retry

```bash
az container create \
  --resource-group migration-rg \
  --name schema-migration-v5 \
  --image mycompany.azurecr.io/db-migrator:latest \
  --restart-policy Never \
  --cpu 1 \
  --memory 2 \
  --environment-variables \
    MIGRATION_VERSION=5 \
    TARGET_DATABASE=production \
  --secure-environment-variables \
    DB_CONNECTION_STRING="Server=..."

# Check logs after completion
az container logs \
  --name schema-migration-v5 \
  --resource-group migration-rg
```

### Scenario 4: Multi-Container Application

**Requirement:** Web app with sidecar logging

```yaml
# multi-container-app.yaml
apiVersion: 2021-09-01
location: eastus
name: webapp-with-logging
properties:
  containers:
  - name: webapp
    properties:
      image: myapp:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
      ports:
      - port: 8080
        protocol: TCP
      volumeMounts:
      - name: logs
        mountPath: /var/log/app
  - name: log-forwarder
    properties:
      image: fluent/fluentd:latest
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
      volumeMounts:
      - name: logs
        mountPath: /var/log/app
        readOnly: true
  volumes:
  - name: logs
    emptyDir: {}
  restartPolicy: Always
  osType: Linux
  ipAddress:
    type: Public
    dnsNameLabel: mywebapp
    ports:
    - port: 8080
      protocol: TCP
type: Microsoft.ContainerInstance/containerGroups
```

```bash
az container create \
  --resource-group myResourceGroup \
  --file multi-container-app.yaml
```

## Best Practices

1. **Choose appropriate restart policy**: Match policy to workload type (service vs task)
2. **Use OnFailure for batch jobs**: Allow automatic recovery from transient failures
3. **Use Always for services**: Ensure continuous availability of web apps and APIs
4. **Use Never for one-time tasks**: Prevent unwanted retries for migrations or scripts
5. **Right-size resources**: Allocate appropriate CPU and memory to avoid over-provisioning
6. **Use ACR for private images**: Store custom images in Azure Container Registry
7. **Implement health checks**: Monitor container health and restart if needed
8. **Use managed identities**: Avoid hardcoding credentials
9. **Mount persistent storage**: Use Azure Files for data that persists beyond container lifecycle
10. **Use secure environment variables**: Protect sensitive configuration values
11. **Set appropriate DNS labels**: Make services easily accessible
12. **Monitor with Azure Monitor**: Track container metrics and logs
13. **Use virtual network deployment**: Isolate containers for security
14. **Tag container groups**: Organize resources with meaningful tags
15. **Implement proper logging**: Use stdout/stderr for application logs

## Key Takeaways

### ✅ Correct Answer for Exam Question:

```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy OnFailure
```

**Why OnFailure is correct:**
- Restarts containers **only when process terminates due to an error** (non-zero exit code)
- Matches requirement: "containers must restart when the process executed in the container group terminates due to an error"
- Appropriate for tasks that should succeed but may fail

### ❌ Why Other Answers Are Incorrect:

**1. Always Policy:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Always
```
- ❌ Restarts on **both success AND failure**
- Does not match requirement (restart only on error)

**2. Never Policy:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image mycontainerimage \
  --restart-policy Never
```
- ❌ **Never restarts**, even on failure
- Opposite of requirement (need restart on error)

**3. Manual Restart Command:**
```bash
az container restart \
  --name mycontainer \
  --resource-group myResourceGroup \
  --no-wait
```
- ❌ Manually restarts containers, does NOT define restart policy
- Used for on-demand restarts, not automatic behavior

### Restart Policy Quick Reference:

| Policy | Restart on Success (exit 0) | Restart on Failure (exit ≠ 0) | Use For |
|--------|------------------------------|--------------------------------|---------|
| **OnFailure** ✅ | No | Yes | **Tasks that may fail and need retry** |
| **Always** | Yes | Yes | Long-running services |
| **Never** | No | No | One-time operations |

### Key Points:
- Restart policy is set **during container creation** with `--restart-policy`
- Policy applies to **entire container group**, not individual containers
- `az container restart` is for **manual restarts**, not policy configuration
- Choose **OnFailure** when you want automatic recovery from errors only
- Choose **Always** for continuous services
- Choose **Never** for one-time tasks

### Remember:
- Container groups = collection of containers with shared resources
- Restart policy = automatic behavior when process terminates
- OnFailure = restart only on error (non-zero exit code) ✅
- Always = restart regardless of exit code
- Never = never restart automatically
- Manual restart ≠ restart policy

## Azure Container Instances Pricing

### Pricing Model

Azure Container Instances uses a **pay-per-second** pricing model based on:
1. **Resource allocation** (vCPU and memory)
2. **Operating system** (Linux or Windows)
3. **Duration** (billed per second)

**Key Points:**
- Billed for resources **allocated**, not used
- Charged from container start to stop/termination
- Minimum billing: 1 second
- Billed per second (no rounding to hours)

### Linux Container Pricing

#### Standard Pricing (Most Regions)

| Resource | Price per Second | Price per Hour | Price per Month (730 hrs) |
|----------|------------------|----------------|---------------------------|
| **vCPU** | $0.0000125 | $0.045 | ~$32.85 |
| **Memory (GB)** | $0.0000014 | $0.005 | ~$3.65 |

#### Resource Allocation Limits

- **Minimum**: 0.5 vCPU, 0.5 GB memory
- **Maximum (per container)**: 4 vCPU, 16 GB memory
- **Maximum (per container group)**: 4 vCPU, 16 GB memory

#### Cost Examples (Linux)

**Example 1: Small Task (1 vCPU, 1 GB)**
```
Configuration: 1 vCPU, 1 GB memory
Duration: 1 hour

Cost calculation:
- vCPU: 1 × $0.045 = $0.045
- Memory: 1 × $0.005 = $0.005
Total: $0.05/hour or ~$36.50/month (24/7)
```

**Example 2: Data Processing (2 vCPU, 4 GB)**
```
Configuration: 2 vCPU, 4 GB memory
Duration: 30 minutes (1,800 seconds)

Cost calculation:
- vCPU: 2 × $0.0000125 × 1,800 = $0.045
- Memory: 4 × $0.0000014 × 1,800 = $0.010
Total: $0.055 per run
```

**Example 3: Batch Job (4 vCPU, 8 GB)**
```
Configuration: 4 vCPU, 8 GB memory
Duration: 10 runs × 15 minutes each = 2.5 hours/day

Daily cost:
- vCPU: 4 × $0.045 × 2.5 = $0.45
- Memory: 8 × $0.005 × 2.5 = $0.10
Total: $0.55/day or ~$16.50/month
```

### Windows Container Pricing

#### Standard Pricing (Most Regions)

| Resource | Price per Second | Price per Hour | Price per Month (730 hrs) |
|----------|------------------|----------------|---------------------------|
| **vCPU** | $0.0000222 | $0.08 | ~$58.40 |
| **Memory (GB)** | $0.0000028 | $0.01 | ~$7.30 |

**Note**: Windows containers cost approximately **1.8x more** than Linux containers

#### Cost Examples (Windows)

**Example 1: .NET Framework App (2 vCPU, 4 GB)**
```
Configuration: 2 vCPU, 4 GB memory
Duration: 24/7 (730 hours/month)

Monthly cost:
- vCPU: 2 × $58.40 = $116.80
- Memory: 4 × $7.30 = $29.20
Total: ~$146.00/month
```

### GPU-Enabled Containers (Preview)

**Availability**: Limited regions (US East, West Europe, etc.)

| GPU SKU | vCPU | Memory | Price per Hour |
|---------|------|--------|----------------|
| **K80** | 1 | 1.5 GB | ~$0.70 |
| **P100** | 1 | 5.5 GB | ~$1.20 |
| **V100** | 1 | 5.5 GB | ~$3.00 |

**Use Cases**: ML inference, rendering, scientific computing

### Pricing Comparison: ACI vs ACA

| Feature | **ACI** | **ACA** |
|---------|---------|----------|
| **Billing model** | Resource allocation | Resource consumption |
| **Scale to zero** | ❌ No (manual stop required) | ✅ Yes (automatic) |
| **vCPU pricing** | $0.0000125/sec (Linux) | $0.000024/sec |
| **Memory pricing** | $0.0000014/GB/sec (Linux) | $0.000003/GB/sec |
| **Minimum cost (1vCPU, 1GB, 1hr)** | ~$0.05 | ~$0.10 (when active) |
| **Best for** | Short-lived tasks, batch jobs | Long-running services with variable load |
| **Free tier** | ❌ No | ✅ Yes (monthly grant) |
| **Request charges** | ❌ No | ✅ Yes ($0.40/million after 2M) |
| **Orchestration** | ❌ Limited | ✅ Built-in (Dapr, ingress, etc.) |

### When to Choose ACI vs ACA

#### Choose **ACI** when:
- ✅ Running short-lived, batch, or scheduled tasks
- ✅ Need quick, simple container deployment
- ✅ Fixed resource requirements (no autoscaling needed)
- ✅ Running Windows containers
- ✅ Want simpler pricing (no request charges)
- ✅ Lower cost for continuous small workloads

**Example**: Database migrations, CI/CD build agents, data processing jobs

#### Choose **ACA** when:
- ✅ Running microservices or web applications
- ✅ Need automatic scaling (including scale-to-zero)
- ✅ Variable or unpredictable traffic patterns
- ✅ Need built-in ingress, load balancing, and service discovery
- ✅ Want to integrate with Dapr, KEDA, Envoy
- ✅ Multiple interconnected containers

**Example**: REST APIs, web apps, event-driven applications, microservices

### Cost Optimization Strategies

#### 1. Right-Size Resources
```bash
# Start with minimum, monitor, then adjust
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image myapp:latest \
  --cpu 0.5 \
  --memory 0.5
```

#### 2. Use Appropriate Restart Policy
```bash
# For one-time tasks, use Never to avoid unnecessary charges
az container create \
  --resource-group myResourceGroup \
  --name batch-job \
  --image myapp:latest \
  --restart-policy Never
```

#### 3. Stop Containers When Not Needed
```bash
# Stop long-running containers during off-hours
az container stop --name mycontainer --resource-group myResourceGroup

# Start when needed
az container start --name mycontainer --resource-group myResourceGroup
```

#### 4. Use Linux Instead of Windows
- Linux containers cost ~45% less than Windows
- Use Linux unless you specifically need Windows features

#### 5. Schedule Batch Jobs Efficiently
```bash
# Run during off-peak hours
# Use Azure Logic Apps or Functions to schedule
# Example: Run ACI via ARM template deployment
```

#### 6. Monitor and Delete Unused Containers
```bash
# List all container groups
az container list --output table

# Delete unused containers
az container delete --name unused --resource-group myResourceGroup --yes
```

#### 7. Use Container Groups Efficiently
```yaml
# Share resources across containers in the same group
apiVersion: 2021-09-01
properties:
  containers:
  - name: app
    properties:
      resources:
        requests:
          cpu: 1.5
          memoryInGb: 2
  - name: sidecar
    properties:
      resources:
        requests:
          cpu: 0.5
          memoryInGb: 0.5
# Total: 2 vCPU, 2.5 GB (instead of separate container groups)
```

### Real-World Cost Scenarios

#### Scenario 1: Daily Backup Job
```
Requirement: Run backup task daily for 30 minutes
Configuration: 1 vCPU, 2 GB memory, Linux

Daily cost:
- vCPU: 1 × $0.0000125 × 1,800 seconds = $0.0225
- Memory: 2 × $0.0000014 × 1,800 seconds = $0.0050
Total: $0.0275/day or ~$0.83/month
```

#### Scenario 2: CI/CD Build Agent
```
Requirement: 10 builds/day, 10 minutes each
Configuration: 2 vCPU, 4 GB memory, Linux

Daily cost:
- Duration: 10 × 600 seconds = 6,000 seconds
- vCPU: 2 × $0.0000125 × 6,000 = $0.15
- Memory: 4 × $0.0000014 × 6,000 = $0.034
Total: $0.184/day or ~$5.52/month
```

#### Scenario 3: Development Environment
```
Requirement: Running 8 hours/day, 5 days/week
Configuration: 1 vCPU, 2 GB memory, Linux

Monthly cost (160 hours):
- vCPU: 1 × $0.045 × 160 = $7.20
- Memory: 2 × $0.005 × 160 = $1.60
Total: ~$8.80/month
```

#### Scenario 4: Always-On Monitoring Agent
```
Requirement: Running 24/7
Configuration: 0.5 vCPU, 0.5 GB memory, Linux

Monthly cost (730 hours):
- vCPU: 0.5 × $32.85 = $16.43
- Memory: 0.5 × $3.65 = $1.83
Total: ~$18.26/month

Note: For always-on workloads, consider ACA with scale-to-zero
or Azure App Service for potentially lower costs
```

### Additional Costs to Consider

**Not included in ACI pricing:**
- ❌ **Networking**: Outbound data transfer (first 5 GB/month free, then ~$0.087/GB)
- ❌ **Virtual Network**: No additional cost for VNet injection
- ❌ **Storage**: Azure Files volumes (separate storage account costs)
- ❌ **Container Registry**: Azure Container Registry costs (if using ACR)
- ❌ **Monitoring**: Azure Monitor / Log Analytics data ingestion (~$2.30/GB)
- ❌ **Public IP**: Included (no separate charge)
- ❌ **DNS labels**: Included (no separate charge)

### Pricing Estimation Tool

**Formula for Linux containers:**
```
Hourly Cost = (vCPU × $0.045) + (Memory_GB × $0.005)
Monthly Cost = Hourly Cost × Hours_Running_Per_Month
```

**Formula for Windows containers:**
```
Hourly Cost = (vCPU × $0.08) + (Memory_GB × $0.01)
Monthly Cost = Hourly Cost × Hours_Running_Per_Month
```

**Calculator Example:**
```bash
# Linux: 2 vCPU, 3 GB, 200 hours/month
Hourly = (2 × $0.045) + (3 × $0.005) = $0.105
Monthly = $0.105 × 200 = $21.00
```

### Key Takeaways

✅ **Pay per second**: Very granular billing  
✅ **No hidden costs**: Simple pricing model  
✅ **Linux is cheaper**: ~45% less than Windows  
✅ **Stop = $0**: No cost when stopped (unlike VMs with storage)  
✅ **Good for short tasks**: Cost-effective for batch jobs  
⚠️ **No scale-to-zero**: Must manually stop containers  
⚠️ **Continuous use**: Consider alternatives (ACA, App Service) for 24/7 workloads  
⚠️ **Resource allocation**: Billed for allocated resources, not actual usage  

## References

- [Azure Container Instances documentation](https://learn.microsoft.com/en-us/azure/container-instances/)
- [Restart policies in Azure Container Instances](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-restart-policy)
- [Run containerized tasks with restart policies](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-restart-policy)
- [Deploy multi-container groups](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-multi-container-group)
- [Mount Azure Files volume](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-volume-azure-files)
- [Set environment variables](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-environment-variables)
- [Container Instances pricing](https://azure.microsoft.com/en-us/pricing/details/container-instances/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
