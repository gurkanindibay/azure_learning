---
type: Reference
title: "Azure Services"
description: "**Virtual Network** — Azure's fundamental private network building block, equivalent to a corporate LAN in the cloud. Every Azure resource that needs private connectivity is deployed into a VNet."
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Azure Services

> **Domain**: Azure networking, identity, compute, data, integration, and observability services.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

### Networking
| Term | Anchor |
|:---|:---|
| VNet (Virtual Network) | [`#vnet`](#vnet) |
| NSG (Network Security Group) | [`#nsg`](#nsg) |
| VNet Peering | [`#vnet-peering`](#vnet-peering) |
| Private Endpoint | [`#private-endpoint`](#private-endpoint) |
| ExpressRoute | [`#expressroute`](#expressroute) |
| VPN Gateway | [`#vpn-gateway`](#vpn-gateway) |
| Azure Firewall | [`#azure-firewall`](#azure-firewall) |

### Identity & Security
| Term | Anchor |
|:---|:---|
| Microsoft Entra ID | [`#entra-id`](#entra-id) |
| Managed Identity | [`#managed-identity`](#managed-identity) |
| Azure RBAC | [`#azure-rbac`](#azure-rbac) |
| Azure Key Vault | [`#key-vault`](#key-vault) |
| HSM (Hardware Security Module) | [`#hsm`](#hsm) |
| Zero Trust | [`#zero-trust`](#zero-trust) |

### Compute & Containers
| Term | Anchor |
|:---|:---|
| AKS (Azure Kubernetes Service) | [`#aks`](#aks) |
| Azure Functions | [`#azure-functions`](#azure-functions) |
| Azure App Service | [`#app-service`](#app-service) |
| Azure Container Apps | [`#container-apps`](#container-apps) |

### Data & Storage
| Term | Anchor |
|:---|:---|
| Azure Cosmos DB | [`#cosmos-db`](#cosmos-db) |
| Azure SQL Database | [`#sql-database`](#sql-database) |
| Blob Storage | [`#blob-storage`](#blob-storage) |
| Storage Redundancy (LRS/ZRS/GRS/GZRS) | [`#storage-redundancy`](#storage-redundancy) |

### Integration
| Term | Anchor |
|:---|:---|
| Azure Event Hubs | [`#event-hubs`](#event-hubs) |
| Azure Service Bus | [`#service-bus`](#service-bus) |
| Azure Event Grid | [`#event-grid`](#event-grid) |
| Azure API Management (APIM) | [`#apim`](#apim) |

### Observability
| Term | Anchor |
|:---|:---|
| Azure Monitor | [`#azure-monitor`](#azure-monitor) |
| Application Insights | [`#application-insights`](#application-insights) |
| Log Analytics / KQL | [`#log-analytics`](#log-analytics) |
| Distributed Tracing | [`#distributed-tracing`](#distributed-tracing) |

---

## Networking

### VNet

**Virtual Network** — Azure's fundamental private network building block, equivalent to a corporate LAN in the cloud. Every Azure resource that needs private connectivity is deployed into a VNet.

| Property | Detail |
|:---|:---|
| **Address space** | CIDR block (e.g., `10.0.0.0/16`) |
| **Subnets** | Logical segmentation of the address space |
| **Isolation** | Resources in different VNets are isolated by default |

**Also see**: [VNet Peering](#vnet-peering), [NSG](#nsg)

---

### NSG

**Network Security Group** — a stateful packet filter at the subnet or NIC level. Cloud-equivalent of firewall rules. Rules are prioritized (lower number = higher priority).

**Also see**: [Azure Firewall](#azure-firewall), [VNet](#vnet)

---

### VNet Peering

Direct, low-latency connection between two VNets using the **Microsoft backbone** (never traverses the public internet). Hub-and-spoke is the most common topology.

**Also see**: [VNet](#vnet)

---

### Private Endpoint

A **consumer-side NIC with a private IP** that connects to Azure PaaS services via Private Link. Traffic stays entirely within the VNet — no public internet exposure.

**Also see**: [VNet](#vnet)

---

### ExpressRoute

A **private, dedicated network connection** to Azure that never traverses the public internet. Higher reliability, lower latency, and predictable throughput compared to VPN.

| Peering Type | Use |
|:---|:---|
| **Microsoft Peering** | Microsoft 365, Dynamics 365, Azure PaaS |
| **Private Peering** | Azure IaaS and VNet-deployed services |

**Also see**: [VPN Gateway](#vpn-gateway)

---

### VPN Gateway

A **Virtual Network Gateway** establishing IPsec/IKE encrypted tunnels. Site-to-Site (S2S) connects on-premises to Azure; Point-to-Site (P2S) connects individual clients.

**Also see**: [ExpressRoute](#expressroute), [VNet](#vnet)

---

### Azure Firewall

Managed, **stateful firewall-as-a-service** for VNet traffic inspection. Layer 4–7 filtering with threat intelligence, FQDN filtering, and TLS inspection.

**Also see**: [NSG](#nsg)

---

## Identity & Security

### Entra ID

**Microsoft Entra ID** (formerly Azure AD) — Microsoft's cloud-based identity and access management service. Every Azure subscription trusts an Entra ID tenant.

**Also see**: [Managed Identity](#managed-identity), [Azure RBAC](#azure-rbac)

---

### Managed Identity

An **Azure-managed identity** that eliminates the need to store credentials in code. Resources authenticate to Azure services (Key Vault, Storage, SQL) without secrets.

| Type | Lifecycle |
|:---|:---|
| **System-Assigned (SAMI)** | Tied to a single resource — deleted with it |
| **User-Assigned (UAMI)** | Standalone — can be attached to multiple resources |

**Also see**: [Entra ID](#entra-id), [Key Vault](#key-vault)

---

### Azure RBAC

**Role-Based Access Control** for Azure resources. Roles (Owner, Contributor, Reader) are assigned at scopes: Management Group → Subscription → Resource Group → Resource.

**Also see**: [Entra ID](#entra-id)

---

### Key Vault

Centralized **secret, key, and certificate management** with HSM-backed storage. Never store connection strings, API keys, or certificates in code or config files.

**Also see**: [Managed Identity](#managed-identity), [HSM](#hsm)

---

### HSM

**Hardware Security Module** — a physically hardened, FIPS 140-3 validated device for cryptographic key protection. Azure offers both Dedicated HSM and fully-managed Managed HSM.

**Also see**: [Key Vault](#key-vault) · [HSM & Cryptography](hsm-cryptography.md)

---

### Zero Trust

Security model: **"never trust, always verify"** — verify every request regardless of source (internal or external). Core to Microsoft's security architecture.

---

## Compute & Containers

### AKS

**Azure Kubernetes Service** — managed Kubernetes with free control plane, automatic upgrades, and deep Azure integration (Entra ID, Key Vault, Monitor, networking).

| Feature | Detail |
|:---|:---|
| **Control plane** | Managed by Azure at no cost |
| **Node pools** | Groups of VMs with same configuration |
| **Scaling** | Cluster autoscaler, HPA, Virtual Nodes |

**Also see**: [Container Apps](#container-apps)

---

### Azure Functions

**Serverless, event-driven compute** — pay per execution. Ideal for event handlers, scheduled tasks, and lightweight APIs. Scales to zero when idle.

**Also see**: [App Service](#app-service), [Container Apps](#container-apps)

---

### App Service

Fully managed **PaaS for web apps, REST APIs, and mobile backends**. Deployment slots enable zero-downtime blue-green deployments.

**Also see**: [Azure Functions](#azure-functions)

---

### Container Apps

**Serverless containers** with built-in ingress, Dapr integration, and auto-scaling. Simpler than AKS for containerized apps that don't need full Kubernetes.

**Also see**: [AKS](#aks), [Azure Functions](#azure-functions)

---

## Data & Storage

### Cosmos DB

Globally distributed, **multi-model NoSQL database** with tunable consistency (Strong → Bounded Staleness → Session → Consistent Prefix → Eventual). Multi-region writes supported.

| Consistency Level | Behavior |
|:---|:---|
| **Strong** | Linearizable — highest consistency, highest latency |
| **Session** | Read-your-own-writes (default) |
| **Eventual** | Weakest — highest throughput |

**Also see**: [SQL Database](#sql-database)

---

### SQL Database

Fully managed **PaaS SQL Server** — single database, elastic pool, or serverless. Built-in high availability, automated backups, and AI-driven performance tuning.

**Also see**: [Cosmos DB](#cosmos-db)

---

### Blob Storage

**Object storage** for unstructured data — text, images, video, logs. Three storage account types: Block Blob (general purpose), Page Blob (VHDs), Append Blob (logs).

**Also see**: [Storage Redundancy](#storage-redundancy)

---

### Storage Redundancy

| Type | Copies | Protection |
|:---|:---|:---|
| **LRS** | 3 within single datacenter | Node failure |
| **ZRS** | 3 across 3 availability zones | Datacenter failure |
| **GRS** | LRS primary + async to secondary region (6 total) | Region failure |
| **GZRS** | ZRS primary + async to secondary region | Zone + region failure |

---

## Integration

### Event Hubs

**High-throughput telemetry streaming** — partitioned, pull-based, Kafka-compatible. Ideal for ingestion pipelines (millions of events/second).

**Also see**: [Service Bus](#service-bus), [Event Grid](#event-grid) · [Messaging](messaging.md)

---

### Service Bus

**Enterprise messaging** with queues (point-to-point) and topics/subscriptions (pub/sub). Supports sessions, duplicate detection, scheduled messages, and transactions.

**Also see**: [Event Hubs](#event-hubs), [Event Grid](#event-grid) · [Messaging](messaging.md)

---

### Event Grid

**Serverless event routing** — push-based discrete event distribution. Ideal for reactive, event-driven architectures connecting Azure resources.

**Also see**: [Event Hubs](#event-hubs), [Service Bus](#service-bus)

---

### APIM

**Azure API Management** — API gateway for managing, securing, publishing, and analyzing APIs. Enforces rate limiting, authentication, caching, and transformations at the gateway layer.

**Also see**: [API Design](api-design.md)

---

## Observability

### Azure Monitor

Unified monitoring platform: **metrics, logs, traces, alerts, autoscale, dashboards**. The single pane of glass for all Azure and application telemetry.

---

### Application Insights

**APM (Application Performance Management)** service — live telemetry for applications: request rates, response times, failure rates, dependencies, and exceptions.

**Also see**: [Azure Monitor](#azure-monitor), [Distributed Tracing](#distributed-tracing)

---

### Log Analytics

Centralized log storage and query engine using **KQL (Kusto Query Language)**. All Azure diagnostic logs, activity logs, and application logs land here.

**Also see**: [Azure Monitor](#azure-monitor)

---

### Distributed Tracing

**End-to-end visibility** of a request across multiple services — correlated via Operation ID. Essential for microservices debugging. Implemented via Application Insights + W3C Trace Context.

**Also see**: [Application Insights](#application-insights), [Azure Monitor](#azure-monitor)
