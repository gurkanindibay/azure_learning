# Hub-Spoke Network Architecture

## Overview
A **hub-spoke network** is a network topology where multiple isolated networks (spokes) connect to a central network (hub). All shared services, security controls, and external connectivity are centralized in the hub, while application workloads reside in the spokes.

This pattern is widely used in **Azure enterprise architectures** to provide strong isolation, centralized security, and controlled connectivity.

---

## Core Concept

- **Hub**: Central VNet that provides shared services and connectivity
- **Spokes**: Application VNets that consume services from the hub
- **No direct spoke-to-spoke connectivity by default**

All traffic entering or leaving the environment flows through the hub.

---

## Logical Topology

```
                Spoke VNet (App A)
                        |
                        |
Spoke VNet (App B) ---- Hub VNet ---- Spoke VNet (App C)
                        |
                        |
                 On‑prem / Internet
```

---

## Components in the Hub

The hub VNet typically hosts:

- Azure Firewall or Network Virtual Appliances (NVA)
- VPN Gateway and/or ExpressRoute Gateway
- Azure Bastion (secure admin access)
- DNS services (Azure DNS Private Resolver, AD DS)
- Identity infrastructure (AD / Entra-integrated services)
- Logging, monitoring, and shared tooling

The hub acts as the **control and inspection plane**.

---

## Components in the Spokes

Each spoke VNet usually contains:

- Application workloads
- Databases and storage services
- Microservices or APIs
- Environment separation (Dev / Test / Prod)
- Subscription or team-level isolation

Spokes are:
- Isolated from each other by default
- Connected only to the hub using VNet peering

---

## Connectivity and Traffic Flow

| Traffic Type | Allowed | Notes |
|-------------|--------|------|
| Spoke → Hub | Yes | Via VNet peering |
| Hub → Spoke | Yes | Shared services access |
| Spoke → Internet | Yes | Routed through hub firewall |
| Spoke → Spoke | No (default) | Possible via hub routing |
| On‑prem → Spoke | Yes | VPN / ExpressRoute through hub |

User Defined Routes (UDRs) are typically used to force traffic through the hub firewall.

---

## Azure Implementation Details

Key Azure features used:

- VNet Peering (hub ↔ spoke)
- User Defined Routes (UDRs)
- Azure Firewall or NVA
- VPN Gateway / ExpressRoute Gateway
- Private Endpoints and Private DNS zones

The hub is usually deployed once per region.

---

## Advantages

- Centralized security and inspection
- Strong workload isolation
- Clear ownership boundaries
- Easier compliance and auditing
- Well-understood and widely adopted pattern

This is the **default enterprise network architecture** in Azure.

---

## Disadvantages

- Manual routing configuration
- Increased operational complexity at scale
- Hub can become a bottleneck if not sized correctly
- Requires careful UDR and peering management

At large scale, operational overhead can become significant.

---

## Hub-Spoke vs Flat Network

| Feature | Flat Network | Hub-Spoke |
|------|-------------|----------|
| Isolation | Low | High |
| Security | Distributed | Centralized |
| Routing | Simple | Moderate |
| Enterprise readiness | Low | High |

---

## Hub-Spoke vs Azure Virtual WAN

| Feature | Hub-Spoke | Azure Virtual WAN |
|------|-----------|------------------|
| Hub management | Customer-managed | Microsoft-managed |
| Routing | Manual (UDRs/BGP) | Automatic |
| Scale | Small–Medium | Large / Global |
| Cost | Lower | Higher |
| Flexibility | High | Moderate |

---

## When Hub-Spoke Is the Right Choice

Use hub-spoke when:

- You have a small to medium number of VNets
- You need fine-grained routing control
- Cost optimization is important
- Branch connectivity is limited
- You want maximum architectural flexibility

Typical scale:
- 3–20 VNets
- 1–2 Azure regions

---

## Decision Checklist

- Do you need centralized security? → Yes
- Do you want isolated application networks? → Yes
- Do you want full routing control? → Yes
- Do you have limited global scale? → Yes

If most answers are yes, hub-spoke is a good fit.

---

## One-Line Summary

**A hub-spoke network centralizes connectivity and security in a shared hub while keeping application networks isolated in spokes.**

---

## Related Azure Exams

- AZ-305: Designing Microsoft Azure Infrastructure Solutions
- AZ-700: Designing and Implementing Microsoft Azure Networking Solutions

---

*Author: Gürkan İndibay*

