# 6. Security Architecture (Cross-Cutting)

This section covers security principles, identity management, and data protection.

## Subsections

### 6.1 Security Architecture
- Zero Trust Architecture
- Defense in Depth
- Threat Modeling Architecture
- Secure SDLC Architecture

### 6.2 Identity Architecture
- Identity and Access Management (IAM)
- Federated Identity Architecture
- Single Sign-On (SSO)
- Managed Identity Architecture
- OAuth 2.0 with PKCE

### 6.3 Network Security Architecture
- Perimeter Security Architecture
- **Demilitarized Zone (DMZ) Architecture**
- Micro-Segmentation
- Web Application Firewall (WAF)
- DDoS Protection Architecture

### 6.4 Data Security Architecture
- Encryption Architecture
- Key Management (HSM / KMS)
- Confidential Computing
- Privacy-by-Design Architecture

## Contents

- **[6.1-security-foundations/](./6.1-security-foundations/)** - Zero Trust, Defense in Depth, Threat Modeling, Secure SDLC
  - [README.md](./6.1-security-foundations/README.md) - Security Architecture foundations
- **[6.2-identity/](./6.2-identity/)** - Identity, Authentication & Authorization
  - [README.md](./6.2-identity/README.md) - Identity Architecture — governance, federation, lifecycle, authorization models
  - [6.2.1-authentication-methods.md](./6.2-identity/6.2.1-authentication-methods.md) - Authentication method catalog, decision matrices, security comparisons
  - [6.2.2-authentication-protocols.md](./6.2-identity/6.2.2-authentication-protocols.md) - Protocol deep dives — sequence diagrams, React + .NET code, token handling
- **[6.3-network-security/](./6.3-network-security/)** - Network Security
  - [README.md](./6.3-network-security/README.md) - Perimeter Security, Micro-Segmentation, WAF, DDoS Protection
  - [6.3.1-dmz-architecture.md](./6.3-network-security/6.3.1-dmz-architecture.md) - Comprehensive DMZ design, topologies, and implementation guide
- **[6.4-data-security/](./6.4-data-security/)** - Data Security
  - [README.md](./6.4-data-security/README.md) - Encryption Architecture, Key Management (HSM/KMS), Confidential Computing, Privacy-by-Design

## Related

- [Architecture Taxonomy Reference](../10-practicality-taxonomy/architecture_taxonomy_reference.md)
- [Azure Security](../../architecture-azure/security/) - Azure-specific security implementations
