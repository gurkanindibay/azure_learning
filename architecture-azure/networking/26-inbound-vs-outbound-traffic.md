---
type: Azure Service
title: "Inbound vs Outbound Traffic in Azure Networking"
description: "Teams often describe traffic direction from different viewpoints:"
tags: [networking]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# Inbound vs Outbound Traffic in Azure Networking

## Why this is confusing

Teams often describe traffic direction from different viewpoints:
- From the client perspective ("I am sending")
- From the server/workload perspective ("I am receiving")

In Azure design and security rules, direction is normally judged from the protected resource's perspective (subnet, NIC, VM, app, or service endpoint).

## The simple rule

- Inbound traffic: packets entering your protected resource
- Outbound traffic: packets leaving your protected resource

A fast memory aid:
- Inbound = coming in to the workload
- Outbound = going out from the workload

## Ingress vs egress terminology

In most networking contexts, the terms are equivalent:
- **Ingress** = **Inbound**
- **Egress** = **Outbound**

The same perspective rule applies: direction is always relative to the protected resource (VM, subnet, firewall, or app).

Examples:
- Internet to app: ingress/inbound to the app
- App to external API: egress/outbound from the app

Nuance:
- In Kubernetes, **Ingress** can also refer to a specific API object/controller used to publish HTTP/HTTPS routes, but directionally it still represents incoming traffic.

Simple ASCII direction diagram:

```text
			 Internet / External Network
						|
						|  inbound (to workload)
						v
			   +------------------------+
			   |      Your Workload     |
			   |    (VM / App / Subnet) |
			   +------------------------+
						|
						|  outbound (from workload)
						v
			 Internet / External Network
```

## Direction by perspective (same flow, different wording)

| Flow | Client says | Workload says | Correct from workload perspective |
|---|---|---|---|
| User opens `https://app.contoso.com` | "I send request" | "App receives request" | Inbound to app |
| App calls `https://api.partner.com` | "App sends request" | "Internet endpoint receives request" | Outbound from app |
| Admin SSH/RDP to VM | "I connect to VM" | "VM receives connection" | Inbound to VM |
| VM downloads package updates | "VM connects to repo" | "VM sends traffic out" | Outbound from VM |

## Azure services and traffic direction

| Azure service | Mainly controls | Inbound/Outbound notes |
|---|---|---|
| NSG | Subnet/NIC allow-deny rules | Has separate inbound and outbound rule sets; stateful behavior allows return traffic for established flows |
| Azure Firewall | Centralized filtering/NAT | Filters both directions; DNAT is typically used for inbound publishing, network/application rules for outbound control |
| NAT Gateway | Internet egress for subnets | Outbound only (egress/SNAT), does not accept unsolicited inbound internet traffic |
| Azure Load Balancer | L4 traffic distribution | Inbound load-balancing and outbound SNAT scenarios |
| Application Gateway / Front Door | L7 web entry | Primarily inbound HTTP/HTTPS entry, can proxy onward traffic to backends |
| WAF | HTTP/HTTPS inspection | Protects inbound web traffic (OWASP-oriented controls) |

## Stateful behavior that reduces confusion

NSGs and Azure Firewall are stateful. If outbound traffic is allowed and a session is established, response packets are allowed back without needing an explicit reverse-direction allow rule for that same session.

Example:
1. VM sends outbound HTTPS to an external API (TCP 443).
2. Return packets from that API are allowed back as part of established state.
3. This does not mean all inbound internet traffic is open.

## Quick design checklist

When defining a rule, ask in this order:
1. What is the protected resource (subnet, NIC, app, private endpoint)?
2. Is traffic entering or leaving that resource?
3. Is this a new connection initiation, or return traffic for an existing session?
4. Which control plane should enforce it (NSG, Firewall, WAF, NAT Gateway, Load Balancer)?

## Common mistakes

- Treating return traffic as "new inbound" and over-adding rules
- Using NAT Gateway expecting inbound publishing (it is egress-focused)
- Mixing client perspective with workload perspective while writing NSG rules
- Assuming "internet-facing app" means all backend subnets need inbound internet access

## Practical examples

### Example 1: Public web app on Application Gateway

- Internet user to Application Gateway: inbound
- Application Gateway to backend VM/private app: outbound from gateway, inbound to backend
- Backend response to gateway/user: return traffic for established sessions

### Example 2: Private VM calling Azure Storage through Private Endpoint

- VM to storage private endpoint IP: outbound from VM, inbound to private endpoint
- Storage response: return traffic
- No public inbound internet exposure required

## Related reading

- [Networking Fundamentals](01-networking-fundamentals.md)
- [Security Services Comparison](12-network-security-services-comparison.md)
- [Azure Firewall](13-azure-firewall-overview.md)
- [Azure Load Balancer](16-azure-load-balancer.md)
- [Azure Application Gateway](17-azure-application-gateway.md)
