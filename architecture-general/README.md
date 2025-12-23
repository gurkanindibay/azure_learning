# General Architecture Documentation

This repository contains general software architecture documentation, patterns, and best practices that are cloud-agnostic. The structure follows the [Architecture Taxonomy Reference](reference/architecture_taxonomy_reference.md).

## Structure

```
architecture-general/
├── application-architecture/           # Section 2: Application & Software Architecture
│   ├── architectural-styles/           # Microservices, monolith, layered, etc.
│   ├── design-patterns/                # Event sourcing, CQRS, and other patterns
│   └── domain-driven-design/           # DDD concepts: event storming, bounded contexts
├── integration-architecture/           # Section 3: Integration & Communication Architecture
│   ├── event-driven-messaging/         # Event-driven architecture patterns
│   │   ├── comparisons/                # Queue vs pub/sub, broker comparisons
│   │   └── patterns/                   # Hybrid messaging patterns
│   └── messaging-patterns/             # General messaging patterns
├── infrastructure-architecture/        # Section 5: Cloud, Infrastructure & Platform
│   └── networking/                     # Hub-spoke, network topology patterns
├── security-architecture/              # Section 6: Security Architecture (Cross-Cutting)
│                                       # Authentication, identity, security principles
├── reliability-operations/             # Section 7: Reliability, Performance & Operations
│   └── observability/                  # Monitoring, logging, tracing
│       └── metrics/                    # RPO/RTO, percentiles, measurements
└── reference/                          # Reference materials and taxonomy
```

## Taxonomy Alignment

This folder structure is organized according to the [Architecture Taxonomy Reference](reference/architecture_taxonomy_reference.md):

| Folder | Taxonomy Section |
|--------|------------------|
| `application-architecture/` | 2. Application & Software Architecture |
| `integration-architecture/` | 3. Integration & Communication Architecture |
| `infrastructure-architecture/` | 5. Cloud, Infrastructure & Platform Architecture |
| `security-architecture/` | 6. Security Architecture (Cross-Cutting) |
| `reliability-operations/` | 7. Reliability, Performance & Operations |

## Topics Covered

- **Application Architecture**: Design patterns (event sourcing), architectural styles, DDD
- **Integration Architecture**: Event-driven patterns, messaging comparisons, pub/sub vs queues
- **Infrastructure Architecture**: Hub-spoke networking, topology patterns
- **Security Architecture**: Authentication methods and security principles
- **Reliability & Operations**: Observability techniques, tools, metrics, and best practices

## Related Repositories

- [architecture-azure](../architecture-azure/) - Azure-specific architecture documentation
