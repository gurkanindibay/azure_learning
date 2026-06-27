---
type: Index
title: "Security"
description: "System-design problems and strategies for HSM integration, authentication, authorization, and Zero Trust security architecture."
timestamp: 2026-06-27T00:00:00Z
---

# Security

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for security architecture: HSM integration bottlenecks, authentication vs authorization, token management, mTLS, and Zero Trust patterns.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [hsm-integration-bottlenecks.md](hsm-integration-bottlenecks.md) | `hsm-01` – `hsm-10` | Horizontal scaling impossibility, Sync crypto in critical path, Connection pool isolation, PCI-DSS caching constraints, Cloud vs on-prem latency, Post-quantum migration |
| [authentication-authorization.md](authentication-authorization.md) | `auth-01` – `auth-07` | Identity vs auth vs authz, Sessions vs tokens, JWT signed-not-encrypted, OAuth2 delegation, mTLS service identity, Zero Trust |

## Cross-References

- **Dictionary**: [HSM/Cryptography](../../reference-dictionary/hsm-cryptography.md)
- **Azure**: [Azure Security](../../architecture-azure/security/), [Entra ID](../../architecture-azure/security/), [Key Vault](../../architecture-azure/security/)
- **Related**: [Resilience](../resilience/), [API & Network](../api-network/)
- **Taxonomy**: §6.1 Identity & Access Management, §6.2 Data Protection
