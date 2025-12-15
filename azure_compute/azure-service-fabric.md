# Azure Service Fabric

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Deployment Options](#deployment-options)
- [Service Types](#service-types)
- [Health Monitoring and Automatic Repair](#health-monitoring-and-automatic-repair)
- [Application Lifecycle Management](#application-lifecycle-management)
- [When to Use Azure Service Fabric](#when-to-use-azure-service-fabric)
- [Comparison with Other Azure Compute Services](#comparison-with-other-azure-compute-services)
- [Exam Scenario: Microservices Architecture Requirements](#exam-scenario-microservices-architecture-requirements)
- [References](#references)

---

## Overview

**Azure Service Fabric** is a distributed systems platform that makes it easy to package, deploy, and manage scalable and reliable microservices and containers. It is designed for building and managing enterprise-grade, cloud-native applications composed of microservices running at high density on a shared pool of machines (called a cluster).

Service Fabric addresses the significant challenges in developing and managing distributed applications by providing:
- A runtime for building distributed, scalable, stateless, and stateful microservices
- Comprehensive application lifecycle management capabilities
- Built-in support for reliable, low-latency, and hyper-scale operations

---

## Key Features

### 1. Microservices Support
- **Stateless Services**: Services that don't maintain state between requests
- **Stateful Services**: Services that maintain reliable state using Reliable Collections
- **Actor Model**: Support for virtual actor pattern through Reliable Actors

### 2. Low-Latency and Hyper-Scale Operations
- Designed to handle millions of requests per second with low latency
- Supports high-density hosting of services
- Efficient resource utilization across cluster nodes

### 3. Independent Service Upgrades
- **Rolling Upgrades**: Update services without downtime
- **Independent Deployment**: Each microservice can be upgraded independently
- **Version Management**: Multiple versions of services can coexist during upgrades
- **Automatic Rollback**: Failed upgrades can automatically roll back to previous versions

### 4. Automatic Repair and Self-Healing
- **Health Monitoring**: Continuous monitoring of service health
- **Automatic Failover**: Services are automatically moved to healthy nodes
- **Repair Policies**: Define policies for automatic repairs to microservices
- **Replica Management**: Automatic recreation of failed replicas

### 5. Orchestration Capabilities
- Service placement and load balancing
- Resource governance and balancing
- Fault tolerance and high availability
- Service discovery and routing

---

## Deployment Options

| Deployment Type | Description | Use Case |
|-----------------|-------------|----------|
| **Azure Service Fabric (Managed Clusters)** | Fully managed Service Fabric clusters in Azure | Cloud-native deployments with minimal management overhead |
| **Azure Service Fabric (Standard Clusters)** | Self-managed clusters in Azure | More control over cluster configuration |
| **On-Premises** | Deploy on your own data center infrastructure | Hybrid scenarios, data sovereignty requirements |
| **Other Clouds** | Deploy on AWS, GCP, or other cloud providers | Multi-cloud strategies |
| **Development Machines** | Local cluster for development and testing | Development and debugging |

### Hybrid Deployment Support
> **Key Capability**: Azure Service Fabric can be deployed both **in Azure** and **on-premises**, making it ideal for hybrid deployment scenarios where applications need to run across cloud and on-premises environments.

---

## Service Types

### Stateless Services
- No persistent state stored within the service
- All instances are equivalent and can handle any request
- Ideal for web front-ends, API gateways, and stateless processing

### Stateful Services
- Maintain state using Reliable Collections (Reliable Dictionary, Reliable Queue)
- State is automatically replicated across nodes for high availability
- Enables low-latency data access by co-locating compute and data
- Ideal for session state, caching, real-time analytics, and transactional workloads

### Guest Executables
- Run existing applications (EXE files) as services
- No code changes required to existing applications
- Useful for lift-and-shift scenarios

### Containers
- Run Windows or Linux containers
- Integrate container orchestration with Service Fabric features
- Combine containers with native Service Fabric services

---

## Health Monitoring and Automatic Repair

### Health Model
Service Fabric provides a rich health model with three health states:
1. **OK**: The entity is healthy
2. **Warning**: The entity has issues but can still function
3. **Error**: The entity is unhealthy

### Health Policies
```json
{
  "healthPolicy": {
    "maxPercentUnhealthyDeployedApplications": 0,
    "defaultServiceTypeHealthPolicy": {
      "maxPercentUnhealthyServices": 0,
      "maxPercentUnhealthyPartitionsPerService": 0,
      "maxPercentUnhealthyReplicasPerPartition": 0
    }
  }
}
```

### Automatic Repair Actions
- **Replica Restart**: Automatically restart failed replicas
- **Service Relocation**: Move services to healthy nodes
- **Node Deactivation**: Remove unhealthy nodes from the cluster
- **Cluster Repair**: Automated cluster-level repairs

---

## Application Lifecycle Management

### Application Model
```
Application
├── Service Type 1
│   ├── Partition 1
│   │   ├── Replica 1 (Primary)
│   │   ├── Replica 2 (Secondary)
│   │   └── Replica 3 (Secondary)
│   └── Partition 2
│       └── ...
└── Service Type 2
    └── ...
```

### Upgrade Modes

| Mode | Description |
|------|-------------|
| **Monitored** | Automatic rolling upgrade with health monitoring |
| **UnmonitoredAuto** | Automatic rolling upgrade without health checks |
| **UnmonitoredManual** | Manual approval required for each upgrade domain |

### Rolling Upgrade Process
1. Update one upgrade domain at a time
2. Perform health checks after each domain
3. Proceed to next domain only if health checks pass
4. Automatic rollback if health degradation detected

---

## When to Use Azure Service Fabric

### ✅ Ideal Use Cases

| Scenario | Why Service Fabric |
|----------|-------------------|
| **Microservices Architecture** | Native support for building and managing microservices |
| **Hybrid Deployments** | Deploy on-premises and in Azure with same platform |
| **Low-Latency Requirements** | Designed for high-performance, low-latency operations |
| **Stateful Services** | Built-in support for reliable, distributed state |
| **Independent Upgrades** | Rolling upgrades with zero downtime |
| **Self-Healing Systems** | Automatic health monitoring and repair |
| **High-Density Hosting** | Efficient resource utilization |

### ❌ When NOT to Use

| Scenario | Better Alternative |
|----------|-------------------|
| Simple, short-lived containers | Azure Container Instances |
| Workflow automation and integration | Azure Logic Apps |
| Standard Kubernetes workloads | Azure Kubernetes Service (AKS) |
| Simple web applications | Azure App Service |

---

## Comparison with Other Azure Compute Services

| Feature | Service Fabric | Container Apps | Container Instances | Logic Apps | VM Scale Sets |
|---------|---------------|----------------|---------------------|------------|---------------|
| **Microservices Native Support** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **On-Premises Deployment** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No |
| **Hybrid Deployment** | ✅ Yes | ❌ No | ❌ No | ❌ Limited | ❌ No |
| **Low-Latency Operations** | ✅ Yes | ✅ Yes | ⚠️ Limited | ❌ No | ⚠️ Depends |
| **Hyper-Scale** | ✅ Yes | ✅ Yes | ⚠️ Limited | ❌ No | ✅ Yes |
| **Independent Service Upgrades** | ✅ Yes | ✅ Yes (Revisions) | ❌ No | N/A | ⚠️ Requires additional tools |
| **Automatic Repair Policies** | ✅ Built-in | ⚠️ Limited (Kubernetes-based) | ❌ No | N/A | ⚠️ Limited |
| **Stateful Services** | ✅ Yes (Native) | ⚠️ Limited (via Dapr) | ❌ No | ❌ No | ❌ No |
| **Rolling Upgrades** | ✅ Yes | ✅ Yes (Traffic Splitting) | ❌ No | N/A | ✅ Yes |
| **Complex Orchestration** | ✅ Yes | ✅ Yes (Managed Kubernetes) | ❌ No | ❌ No | ⚠️ Requires extra setup |
| **Scale-to-Zero** | ❌ No | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **Event-Driven Scaling (KEDA)** | ❌ No | ✅ Yes | ❌ No | ⚠️ Triggers-based | ❌ No |
| **Dapr Integration** | ❌ No | ✅ Built-in | ❌ No | ❌ No | ❌ No |

### Why Not Azure Container Apps?
- Excellent choice for **cloud-native microservices** with managed Kubernetes
- Supports microservices patterns with Dapr integration and KEDA autoscaling
- **Does NOT support on-premises deployment** - Azure-only service
- Limited native stateful service support (requires Dapr state stores)
- Automatic repair is Kubernetes-based, not as granular as Service Fabric's health policies
- Best suited when you need **serverless container platform** without hybrid requirements

### Why Not Azure Container Instances?
- Designed for running containers without managing infrastructure
- **Does NOT support** complex orchestration features:
  - Automatic repair
  - Rolling upgrades
  - Stateful service support
- Lacks built-in capabilities for large-scale microservices management
- No hybrid deployment support

### Why Not Azure Logic Apps?
- Primarily used for building **automated workflows and integrations**
- Uses a serverless model for integration scenarios
- **NOT designed** for running microservices
- **NOT suitable** for scalable, low-latency application components

### Why Not Azure VM Scale Sets?
- Supports scaling virtual machines and can run containerized workloads
- **Does NOT provide** a native microservices framework
- Managing microservices independently requires **additional orchestration layers**
- Health and upgrade management requires **extra tools and configuration**
- Less suitable compared to Service Fabric for microservices architectures

---

## Exam Scenario: Microservices Architecture Requirements

### Question
You are designing a microservices architecture that will support a web application.

The solution must meet the following requirements:
- Deploy the solution on-premises and to Azure
- Support low-latency and hyper-scale operations
- Allow independent upgrades to each microservice
- Set policies for performing automatic repairs to the microservices

What should you recommend?

| Option | Correct? |
|--------|----------|
| Azure Container Instance | ❌ |
| Azure Logic App | ❌ |
| **Azure Service Fabric** | ✅ |
| Azure virtual machine scale set | ❌ |

### Explanation

**Azure Service Fabric** is the correct answer because:

1. **Distributed Systems Platform**: Specifically designed for building and managing scalable, reliable microservices-based applications

2. **Low-Latency and Hyper-Scale**: Built to support low-latency operations at hyper-scale

3. **Independent Upgrades**: Enables independent deployment and upgrades of microservices through rolling upgrades

4. **Automatic Repair**: Includes built-in health monitoring and automatic repair policies

5. **Hybrid Deployment**: Can be deployed both in Azure AND on-premises, directly satisfying the hybrid deployment requirement

6. **Enterprise-Grade**: Ideal for stateful and stateless microservices with mature orchestration capabilities for complex, enterprise-grade architectures

---

## References

- [Azure Service Fabric Overview](https://learn.microsoft.com/en-us/azure/service-fabric/service-fabric-overview)
- [Azure Service Fabric Application Upgrade](https://learn.microsoft.com/en-us/azure/service-fabric/service-fabric-application-upgrade)
- [Service Fabric Health Monitoring](https://learn.microsoft.com/en-us/azure/service-fabric/service-fabric-health-introduction)
- [Service Fabric Cluster Deployment](https://learn.microsoft.com/en-us/azure/service-fabric/service-fabric-cluster-creation-via-portal)
- [Reliable Services Overview](https://learn.microsoft.com/en-us/azure/service-fabric/service-fabric-reliable-services-introduction)
- [Azure Container Instances Overview](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-overview)
- [Azure Logic Apps Overview](https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-overview)
- [Azure Virtual Machine Scale Sets Overview](https://learn.microsoft.com/en-us/azure/virtual-machine-scale-sets/overview)
