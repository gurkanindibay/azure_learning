# General Architecture Documentation

This repository contains general software architecture documentation, patterns, and best practices that are cloud-agnostic. The structure follows the [Architecture Taxonomy Reference](10-practicality-taxonomy/architecture_taxonomy_reference.md).

## Structure

```
architecture-general/
├── 01-enterprise-strategic-architecture/   # Section 1: Enterprise & Strategic Architecture
├── 02-application-software-architecture/   # Section 2: Application & Software Architecture
│   ├── architectural-styles/               # Microservices, monolith, layered, etc.
│   ├── design-patterns/                    # Event sourcing, CQRS, and other patterns
│   └── domain-driven-design/               # DDD concepts: event storming, bounded contexts
├── 03-integration-communication-architecture/  # Section 3: Integration & Communication Architecture
│   ├── event-driven-messaging/             # Event-driven architecture patterns
│   │   ├── comparisons/                    # Queue vs pub/sub, broker comparisons
│   │   └── patterns/                       # Hybrid messaging patterns
│   └── messaging-patterns/                 # General messaging patterns
├── 04-data-analytics-ai-architecture/      # Section 4: Data, Analytics & AI Architecture
├── 05-cloud-infrastructure-platform-architecture/  # Section 5: Cloud, Infrastructure & Platform
│   └── networking/                         # Hub-spoke, network topology patterns
├── 06-security-architecture/               # Section 6: Security Architecture (Cross-Cutting)
├── 07-reliability-performance-operations/  # Section 7: Reliability, Performance & Operations
│   └── observability/                      # Monitoring, logging, tracing
│       └── metrics/                        # RPO/RTO, percentiles, measurements
├── 08-devops-delivery-runtime-architecture/    # Section 8: DevOps, Delivery & Runtime Architecture
├── 09-industry-specialized-architectures/  # Section 9: Industry & Specialized Architectures
├── 10-practicality-taxonomy/               # Section 10: Practicality Taxonomy (Abstraction Levels)
└── 11-architectural-qualities/             # Section 11: Architectural Qualities (Non-Functional)
```

## Taxonomy Alignment

This folder structure is organized according to the [Architecture Taxonomy Reference](10-practicality-taxonomy/architecture_taxonomy_reference.md):

| Folder | Taxonomy Section |
|--------|------------------|
| `01-enterprise-strategic-architecture/` | 1. Enterprise & Strategic Architecture |
| `02-application-software-architecture/` | 2. Application & Software Architecture |
| `03-integration-communication-architecture/` | 3. Integration & Communication Architecture |
| `04-data-analytics-ai-architecture/` | 4. Data, Analytics & AI Architecture |
| `05-cloud-infrastructure-platform-architecture/` | 5. Cloud, Infrastructure & Platform Architecture |
| `06-security-architecture/` | 6. Security Architecture (Cross-Cutting) |
| `07-reliability-performance-operations/` | 7. Reliability, Performance & Operations |
| `08-devops-delivery-runtime-architecture/` | 8. DevOps, Delivery & Runtime Architecture |
| `09-industry-specialized-architectures/` | 9. Industry & Specialized Architectures |
| `10-practicality-taxonomy/` | 10. Practicality Taxonomy (Abstraction Levels) |
| `11-architectural-qualities/` | 11. Architectural Qualities (Non-Functional) |

## Topics Covered

- **Enterprise Architecture**: Business, capability, value stream, and governance architecture
- **Application Architecture**: Design patterns (event sourcing), architectural styles, DDD
- **Integration Architecture**: Event-driven patterns, messaging comparisons, pub/sub vs queues
- **Data & AI Architecture**: Data lakes, warehouses, ML pipelines, analytics
- **Infrastructure Architecture**: Hub-spoke networking, topology patterns, cloud platforms
- **Security Architecture**: Authentication methods, identity, Zero Trust, and security principles
- **Reliability & Operations**: Observability techniques, tools, metrics, and best practices
- **DevOps & Runtime**: CI/CD, GitOps, deployment strategies
- **Industry Architectures**: Specialized patterns for different industries

## Related Repositories

- [architecture-azure](../architecture-azure/) - Azure-specific architecture documentation
