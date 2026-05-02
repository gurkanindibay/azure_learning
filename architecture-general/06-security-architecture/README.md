# 6. Security Architecture (Cross-Cutting)

> **Taxonomy Reference**: §6 Security Architecture (see [architecture_taxonomy_reference.md](../10-practicality-taxonomy/architecture_taxonomy_reference.md))

This section covers security principles, identity management, network protection, and data security — cross-cutting concerns that apply across all other architecture domains.

---

## Contents

### [6.1 Security Foundations](./6.1-security-foundations/)

Core security principles and methodologies that underpin all other security topics.

| Topic | Description |
|-------|-------------|
| Zero Trust Architecture | "Never trust, always verify" security model |
| Defense in Depth | Layered security controls strategy |
| Threat Modeling | Systematic identification and mitigation of threats |
| Secure SDLC | Security integrated into software development lifecycle |

### [6.2 Identity Architecture](./6.2-identity/)

Identity and access management, authentication protocols, and authorization models.

| Document | Description |
|----------|-------------|
| [README.md](./6.2-identity/README.md) | Identity governance, federation, lifecycle, authorization models |
| [6.2.1 Authentication Methods](./6.2-identity/6.2.1-authentication-methods.md) | Method catalog, decision matrices, security comparisons |
| [6.2.2 Authentication Protocols](./6.2-identity/6.2.2-authentication-protocols.md) | Protocol deep dives — sequence diagrams, React + .NET code, token handling |

### [6.3 Network Security](./6.3-network-security/)

Network-level security controls from perimeter to micro-segmentation.

| Document | Description |
|----------|-------------|
| [README.md](./6.3-network-security/README.md) | Perimeter security, micro-segmentation, WAF, DDoS protection |
| [6.3.1 DMZ Architecture](./6.3-network-security/6.3.1-dmz-architecture.md) | DMZ design, topologies, and implementation guide |
| [6.3.2 Network Segmentation](./6.3-network-security/6.3.2-network-segmentation.md) | Zone models, VLAN design, micro-segmentation, Zero Trust segmentation |

### [6.4 Data Security](./6.4-data-security/)

Data protection at rest, in transit, and in use.

| Document | Description |
|----------|-------------|
| [6.4.0 Data Security Architecture](./6.4-data-security/6.4.0-data-security-architecture.md) | Encryption, key management, confidential computing, privacy-by-design |
| [6.4.1 PCI DSS Encryption Guide](./6.4-data-security/6.4.1-pci-dss-encryption-guide.md) | DEK/KEK hierarchy, HSM tokenization, PCI DSS operational controls |

---

## Related

- [Architecture Taxonomy Reference](../10-practicality-taxonomy/architecture_taxonomy_reference.md)
- [Azure Security](../../architecture-azure/security/) — Azure-specific security implementations
