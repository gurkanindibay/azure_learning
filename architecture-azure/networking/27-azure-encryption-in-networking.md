---
type: Azure Service
title: "Azure Encryption in Networking Context"
description: "Network security is not only about segmentation and filtering. It also requires protecting data:"
tags: [networking]
timestamp: 2026-06-14T00:00:00Z
---

# Azure Encryption in Networking Context

> Source: [Azure encryption (Microsoft Learn)](https://learn.microsoft.com/en-us/training/modules/security-virtual-networks/10-azure-encryption)

## Why this matters for networking

Network security is not only about segmentation and filtering. It also requires protecting data:

- At rest: when stored on disks, databases, and storage services.
- In transit: when moving between clients, regions, VNets, and on-premises networks.

## Summary of Azure encryption models

Azure supports both client-side and server-side encryption:

- Client-side encryption: Data is encrypted before Azure receives it. You keep full control of keys.
- Server-side encryption:
  - Service-managed keys: Lowest operational overhead.
  - Customer-managed keys (CMK): Keys managed by you, typically with Azure Key Vault.
  - Customer-controlled hardware key scenarios (HYOK): Highest control, higher complexity, limited support.

## Encryption at rest

Key points from the module:

- Azure uses AES-256 broadly for data-at-rest protection across IaaS, PaaS, and SaaS services.
- Managed Disks, snapshots, and images are encrypted by default.
- Azure Storage Service Encryption (SSE) automatically encrypts and decrypts blob/file data transparently.
- Azure SQL supports:
  - Transparent Data Encryption (TDE) for database files/logs.
  - Always Encrypted for client-side protection of sensitive columns.
  - Column-level encryption for granular scenarios.
- Azure Cosmos DB encrypts data at rest by default, with optional CMK.
- Azure Data Lake supports at-rest encryption by default and can use customer-managed keys.

## Encryption in transit

Azure provides multiple in-transit protections relevant to networking:

- MACsec at the data-link layer for Azure backbone traffic outside Microsoft-controlled physical boundaries (enabled by default).
- TLS for client-to-service and service-to-service encryption.
- HTTPS enforcement options for Azure Storage transactions and SAS usage.
- SMB 3.0 encryption for Azure Files and SMB traffic over VNets.
- VM management sessions:
  - RDP secured with TLS.
  - SSH for secure Linux VM administration.
- VPN encryption:
  - Site-to-site: IPsec/IKE tunnels.
  - Point-to-site: encrypted tunnels such as SSTP, with certificate-based options.

## Key management with Azure Key Vault

The module highlights key management as the control point of any encryption strategy:

- Use Azure Key Vault to manage and control access to encryption keys.
- Prefer CMK + Key Vault where regulatory, separation-of-duties, or rotation policies require stronger key governance.

## Practical architecture guidance

Use this quick decision model:

- Need strongest data ownership guarantees: Prefer client-side encryption or CMK with Key Vault.
- Need low operational overhead: Start with service-managed keys, then move to CMK where required.
- Designing hybrid connectivity: Pair VPN/ExpressRoute security controls with IPsec/TLS and strict key governance.
- Protecting storage access paths: Enforce HTTPS-only, use private endpoints where possible, and disable unnecessary public access.

## Related networking topics

- [Private Endpoints Guide](03-private-endpoints-guide.md)
- [VPN vs Private Link](06-vpn-private-link-guide.md)
- [ExpressRoute & BGP](07-expressroute-bgp-guide.md)
- [Security Services Comparison](12-network-security-services-comparison.md)
- [Azure Firewall](13-azure-firewall-overview.md)
