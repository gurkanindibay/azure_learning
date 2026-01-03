# Architecture Taxonomy – Comprehensive Reference

This document is a **canonical markdown reference** for commonly recognized architecture types used in enterprise, cloud, and software engineering contexts. It is suitable for **architecture handbooks, governance boards, interviews, and internal standards**.

> **Auto-generated**: This file is automatically synchronized with README.md files in the architecture-general directory structure.
> 
> **Last updated**: 2026-01-04 02:25:00
> 
> **To regenerate**: Run `python scripts/sync_taxonomy_reference.py`

---

## Table of Contents


<details>
<summary><a href="#1-enterprise-strategic-architecture">1. Enterprise & Strategic Architecture</a></summary>

  - [1.1 Enterprise Architecture](#11-enterprise-architecture)
  - [1.2 Information Architecture](#12-information-architecture)
  - [1.3 Governance Architecture](#13-governance-architecture)
</details>

<details>
<summary><a href="#2-application-software-architecture">2. Application & Software Architecture</a></summary>

  - [2.1 Application Architecture Styles](#21-application-architecture-styles)
  - [2.2 Backend Architecture](#22-backend-architecture)
  - [2.3 Frontend Architecture](#23-frontend-architecture)
  - [2.4 Mobile Architecture](#24-mobile-architecture)
  - [2.5 Domain-Driven Design (DDD)](#25-domain-driven-design-ddd)
  - [2.6 Design Patterns](#26-design-patterns)
  - [2.7 Language Selection & Technology Choice](#27-language-selection-technology-choice)
</details>

<details>
<summary><a href="#3-integration-communication-architecture">3. Integration & Communication Architecture</a></summary>

  - [Architectural Paradigms](#architectural-paradigms)
  - [Messaging Patterns](#messaging-patterns)
  - [Core Documentation](#core-documentation)
  - [Detailed Guides](#detailed-guides)
  - [When to Use Each Integration Style](#when-to-use-each-integration-style)
  - [Pattern Selection Matrix](#pattern-selection-matrix)
</details>

<details>
<summary><a href="#4-data-analytics-ai-architecture">4. Data, Analytics & AI Architecture</a></summary>

  - [4.0 Data Architecture Fundamentals](#40-data-architecture-fundamentals)
  - [4.0.1 Database Performance & Caching](#401-database-performance-caching)
  - [4.1 Data Architecture](#41-data-architecture)
  - [4.2 Analytics Architecture](#42-analytics-architecture)
  - [4.3 Streaming & Real-Time Architecture](#43-streaming-real-time-architecture)
  - [4.4 AI / ML Architecture](#44-ai-ml-architecture)
</details>

<details>
<summary><a href="#5-cloud-infrastructure-platform-architecture">5. Cloud, Infrastructure & Platform Architecture</a></summary>

  - [5.1 Cloud Architecture](#51-cloud-architecture)
  - [5.2 Infrastructure Architecture](#52-infrastructure-architecture)
  - [5.3 Platform Architecture](#53-platform-architecture)
</details>

<details>
<summary><a href="#6-security-architecture-cross-cutting">6. Security Architecture (Cross-Cutting)</a></summary>

  - [6.1 Security Architecture](#61-security-architecture)
  - [6.2 Identity Architecture](#62-identity-architecture)
  - [6.3 Network Security Architecture](#63-network-security-architecture)
  - [6.4 Data Security Architecture](#64-data-security-architecture)
</details>

<details>
<summary><a href="#7-reliability-performance-operations">7. Reliability, Performance & Operations</a></summary>

  - [7.1 Reliability Architecture](#71-reliability-architecture)
  - [7.2 Performance Architecture](#72-performance-architecture)
  - [7.3 Observability Architecture](#73-observability-architecture)
</details>

<details>
<summary><a href="#8-devops-delivery-runtime-architecture">8. DevOps, Delivery & Runtime Architecture</a></summary>

  - [8.1 DevOps Architecture](#81-devops-architecture)
  - [8.2 Runtime & Deployment Architecture](#82-runtime-deployment-architecture)
  - [8.3 Git Branching Strategies](#83-git-branching-strategies)
</details>

<details>
<summary><a href="#9-industry-specialized-architectures">9. Industry & Specialized Architectures</a></summary>

  - [9.1 Industry Architectures](#91-industry-architectures)
  - [9.2 Specialized Architectures](#92-specialized-architectures)
</details>

<details>
<summary><a href="#10-practicality-taxonomy-abstraction-levels">10. Practicality Taxonomy (Abstraction Levels)</a></summary>


</details>

<details>
<summary><a href="#11-architectural-qualities-non-functional">11. Architectural Qualities (Non-Functional)</a></summary>

  - [1. Functional Suitability *(ISO)*](#1-functional-suitability-iso)
  - [2. Performance Efficiency *(ISO, SEI, NETAS)*](#2-performance-efficiency-iso-sei-netas)
  - [3. Compatibility *(ISO)*](#3-compatibility-iso)
  - [4. Usability *(ISO, SEI, NETAS)*](#4-usability-iso-sei-netas)
  - [5. Reliability *(ISO, SEI, NETAS)*](#5-reliability-iso-sei-netas)
  - [6. Security *(ISO, SEI, NETAS)*](#6-security-iso-sei-netas)
  - [7. Safety *(SEI)*](#7-safety-sei)
  - [8. Maintainability *(ISO, NETAS)*](#8-maintainability-iso-netas)
  - [9. Portability *(ISO, SEI)*](#9-portability-iso-sei)
  - [10. Scalability *(SEI, NETAS)*](#10-scalability-sei-netas)
  - [11. Deployability *(SEI, NETAS)*](#11-deployability-sei-netas)
  - [12. Manageability *(NETAS)*](#12-manageability-netas)
  - [13. Observability](#13-observability)
  - [14. Monitorability *(SEI, NETAS)*](#14-monitorability-sei-netas)
  - [15. Supportability *(NETAS)*](#15-supportability-netas)
  - [16. Sensibility *(NETAS)*](#16-sensibility-netas)
  - [17. Mobility *(SEI, NETAS)*](#17-mobility-sei-netas)
  - [18. Variability *(SEI)*](#18-variability-sei)
  - [19. Development Distributability *(SEI, NETAS)*](#19-development-distributability-sei-netas)
  - [20. Conceptual Integrity *(NETAS - Design Quality)*](#20-conceptual-integrity-netas-design-quality)
  - [21. Additional Quality Considerations](#21-additional-quality-considerations)
</details>

---

## 1. Enterprise & Strategic Architecture

### 1.1 Enterprise Architecture
- Business Architecture
- Capability Architecture
- Value Stream Architecture
- Organization Architecture
- Team Topologies & Conway's Law

### 1.2 Information Architecture
- Information Models
- Master Data Architecture
- Metadata Architecture
- Knowledge Architecture

### 1.3 Governance Architecture
- Architecture Governance
- IT Governance
- Data Governance
- Security Governance
- Architecture Taxonomy Reference

---
## 2. Application & Software Architecture

### 2.1 Application Architecture Styles
- Monolithic Architecture
- Modular Monolith
- Layered Architecture
- Clean Architecture
- Hexagonal (Ports & Adapters)
- Onion Architecture
- N-Tier Architecture

### 2.2 Backend Architecture
- REST-based Architecture
- GraphQL Architecture
- gRPC Architecture
- Backend-for-Frontend (BFF)
- Serverless Backend Architecture

### 2.3 Frontend Architecture
- Single Page Application (SPA)
- Server-Side Rendering (SSR / ISR)
- Micro-Frontend Architecture

### 2.4 Mobile Architecture
- Native Mobile Architecture
- Cross-Platform Architecture
- Offline-First Architecture

### 2.5 Domain-Driven Design (DDD)
- Strategic DDD (Bounded Contexts, Context Mapping)
- Tactical DDD (Entities, Value Objects, Aggregates)
- Ubiquitous Language
- Event Storming
- **DDD at Scale Case Study**

### 2.6 Design Patterns
- Event Sourcing
- CQRS
- Saga Pattern
- Strangler Fig Pattern

### 2.7 Language Selection & Technology Choice
- **Uber's Go vs Rust Decision**
- Decision frameworks and criteria for language selection
- 01-architectural-styles/ - Architecture style patterns
- 02-backend-architecture/ - Backend architecture (REST, GraphQL, gRPC, BFF, Serverless)
- 03-frontend-architecture/ - Frontend architecture (SPA, SSR, Micro-Frontends)
- 04-mobile-architecture/ - Mobile architecture (Native, Cross-Platform, Offline-First)
- 05-domain-driven-design/ - DDD concepts and event storming
- 06-design-patterns/ - Design patterns (Event Sourcing, CQRS, etc.)
- 07-language-selection/ - Language selection criteria and real-world case studies
- Architecture Taxonomy Reference

---
## 3. Integration & Communication Architecture

### Architectural Paradigms

### Messaging Patterns

### Core Documentation

### Detailed Guides

### When to Use Each Integration Style

### Pattern Selection Matrix
- Azure Integration Services - Azure-specific implementations
- Architecture Taxonomy Reference
- Reliability Patterns

---
## 4. Data, Analytics & AI Architecture

### 4.0 Data Architecture Fundamentals
- ACID Properties - Transaction guarantees
- BASE Properties - Distributed availability approach
- CAP Theorem - Distributed systems trade-offs

### 4.0.1 Database Performance & Caching
- PostgreSQL Performance & Caching Strategies - Modern PostgreSQL features and caching decisions
- Database Caching Patterns - General caching strategies and patterns

### 4.1 Data Architecture
- OLTP Architecture
- OLAP Architecture
- Polyglot Persistence
- Data Virtualization

### 4.2 Analytics Architecture
- Data Warehouse Architecture
- Data Lake Architecture
- Lakehouse Architecture
- Lambda Architecture
- Kappa Architecture

### 4.3 Streaming & Real-Time Architecture
- Real-Time Analytics Architecture
- Stream Processing Architecture
- Change Data Capture (CDC)

### 4.4 AI / ML Architecture
- Machine Learning Pipeline Architecture
- MLOps Architecture
- Feature Store Architecture
- Model Training Architecture
- Model Inference Architecture
- Vector Database Architecture
- Architecture Taxonomy Reference

---
## 5. Cloud, Infrastructure & Platform Architecture

### 5.1 Cloud Architecture
- Public Cloud Architecture
- Private Cloud Architecture
- Hybrid Cloud Architecture
- Multi-Cloud Architecture
- Edge Cloud Architecture

### 5.2 Infrastructure Architecture
- Bare Metal Architecture
- Virtualized Infrastructure
- Container Architecture
- Kubernetes Architecture

### 5.3 Platform Architecture
- Platform-as-a-Service (PaaS)
- Serverless Architecture
- Internal Developer Platform (IDP)
- Platform Engineering Architecture
- networking/ - Network topology, proxy, and load balancing patterns
- Hub-Spoke Network Architecture
- Proxy and Load Balancing Architecture
- Service Mesh Architecture
- scaling/ - System design evolution and scaling patterns
- Architecture Taxonomy Reference
- Azure Architecture - Azure-specific implementations

---
## 6. Security Architecture (Cross-Cutting)

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
- Micro-Segmentation
- Web Application Firewall (WAF)
- DDoS Protection Architecture

### 6.4 Data Security Architecture
- Encryption Architecture
- Key Management (HSM / KMS)
- Confidential Computing
- Privacy-by-Design Architecture
- 6.1-security-architecture.md - Zero Trust, Defense in Depth, Threat Modeling, Secure SDLC
- 6.2-identity-architecture.md - Identity Management, Authentication, Authorization, Federation, OAuth 2.0 + PKCE
- 6.3-network-security-architecture.md - Perimeter Security, Micro-Segmentation, WAF, DDoS Protection
- 6.4-data-security-architecture.md - Encryption Architecture, Key Management (HSM/KMS), Confidential Computing, Privacy-by-Design
- authentication-methods-overview.md - Authentication methods and patterns
- Architecture Taxonomy Reference
- Azure Security - Azure-specific security implementations

---
## 7. Reliability, Performance & Operations

### 7.1 Reliability Architecture
- High Availability (HA)
- Disaster Recovery (DR)
- Fault-Tolerant Architecture
- Chaos Engineering Architecture
- Resilience Patterns (Circuit Breaker, Retry, Bulkhead, etc.)

### 7.2 Performance Architecture
- Low-Latency Architecture
- Caching Architecture
- Load Balancing Architecture
- Edge Optimization
- **Tail Latency and Distributed Systems** (Case Study)
- **Language Transition Anti-Patterns** (Case Study)

### 7.3 Observability Architecture
- Logging Architecture
- Metrics Architecture
- Distributed Tracing
- Monitoring Architecture
- reliability-performance-operations-patterns.md - Comprehensive patterns reference
- 7.1-reliability-architecture/ - Reliability architecture patterns and practices
- 7.2-performance-architecture/ - Performance architecture patterns and practices
- tail-latency-distributed-systems.md - **Case study: Why variance matters more than speed (Aurora DSQL)**
- language-transition-anti-patterns.md - **Case study: When language rewrites don't help (Java to Go)**
- 7.3-observability-architecture/ - Observability concepts and practices
- Architecture Taxonomy Reference
- Azure Observability - Azure Monitor, Application Insights

---
## 8. DevOps, Delivery & Runtime Architecture

### 8.1 DevOps Architecture
- CI/CD Architecture
- GitOps Architecture
- Infrastructure as Code (IaC)
- Release Management Architecture

### 8.2 Runtime & Deployment Architecture
- Blue-Green Deployment
- Canary Deployment
- Feature Flag Architecture
- Rollback Architecture

### 8.3 Git Branching Strategies
- GitFlow - Scheduled releases with multiple branch types
- GitHub Flow - Simplified continuous delivery
- GitLab Flow - Environment-based deployments
- Trunk-Based Development - High-velocity continuous deployment
- Release Flow - Microsoft's large-scale approach
- Feature Branch Workflow - Simple isolated development
- Forking Workflow - Open source collaboration
- Architecture Taxonomy Reference
- Azure DevOps - Azure DevOps and ARM templates

---
## 9. Industry & Specialized Architectures

### 9.1 Industry Architectures
- Core Banking Architecture
- Payment Processing
- Trading Platforms
- Regulatory Compliance
- Security Architecture
- Healthcare Architecture
- Telecommunications Architecture
- Government Architecture
- E-commerce Architecture

### 9.2 Specialized Architectures
- Internet of Things (IoT)
- Digital Twin Architecture
- Blockchain Architecture
- Metaverse Architecture
- Gaming Architecture
- Architecture Taxonomy Reference

---
## 10. Practicality Taxonomy (Abstraction Levels)

This taxonomy classifies architectures by their **level of abstraction** and **proximity to implementation**. It helps distinguish between conceptual frameworks and deployment-ready patterns.

### 10.1 Conceptual Architecture (Strategic / Abstract)
High-level, technology-agnostic representations that focus on **business intent, capabilities, and relationships**. Used for stakeholder communication, governance, and strategic planning.

**Characteristics:**
- Technology-agnostic
- Business-aligned vocabulary
- Focus on "what" not "how"
- Long-term vision (3–5+ years)

**Examples:**
- Enterprise Architecture
- Business Architecture
- Capability Architecture
- Value Stream Architecture
- Information Architecture
- Governance Architecture

### 10.2 Logical Architecture (Design / Structural)
Technology-aware but vendor-neutral representations that define **components, boundaries, and interactions**. Bridges conceptual intent with implementation constraints.

**Characteristics:**
- Defines logical components and responsibilities
- Establishes integration patterns
- Technology-aware but not vendor-specific
- Medium-term horizon (1–3 years)

**Examples:**
- Application Architecture Styles (Layered, Hexagonal, Clean)
- Event-Driven Architecture
- API Architecture
- Data Architecture (OLTP/OLAP)
- Security Architecture (Zero Trust)
- Microservices Architecture

### 10.3 Physical / Implementation Architecture (Tactical / Concrete)
Vendor-specific, deployment-ready representations that define **actual technologies, configurations, and infrastructure**. Directly translatable to code and infrastructure.

**Characteristics:**
- Vendor/product-specific
- Includes concrete configurations
- Deployable and testable
- Short-term horizon (weeks–12 months)

**Examples:**
- Kubernetes Architecture
- Serverless Architecture (AWS Lambda, Azure Functions)
- CI/CD Architecture (GitHub Actions, Azure DevOps)
- Container Architecture (Docker, Podman)
- Cloud Architecture (Azure, AWS, GCP-specific)
- Infrastructure as Code (Terraform, Bicep)

### 10.4 Runtime / Operational Architecture (Execution / Live)
Represents the **actual running state** of systems, including real-time topology, traffic flows, and operational metrics.

**Characteristics:**
- Reflects live system state
- Dynamic and observable
- Includes operational concerns (scaling, failover)
- Continuous (real-time)

**Examples:**
- Blue-Green Deployment
- Canary Deployment
- Observability Architecture
- Chaos Engineering Architecture
- Load Balancing Architecture
- Disaster Recovery (Active-Active, Active-Passive)

---

### Practicality Spectrum Summary

| Level | Focus | Horizon | Audience |
|-------|-------|---------|----------|
| **Conceptual** | Business intent & capabilities | 3–5+ years | Executives, Business Stakeholders |
| **Logical** | Components & patterns | 1–3 years | Architects, Tech Leads |
| **Physical** | Technologies & configurations | Weeks–12 months | Engineers, DevOps |
| **Runtime** | Live state & operations | Real-time | SRE, Operations |

---

## 11. Architectural Qualities (Non-Functional)

These apply **across all architecture types**:

- Scalability
- Security
- Reliability & Resilience
- Performance
- Maintainability
- Extensibility
- Portability
- Compliance & Regulatory
- Sustainability (Green IT)

---

## Recommended Naming Convention

```
[Domain] + [Layer] + [Primary Concern]
```

### Examples
- Cloud-Native Event-Driven Backend Architecture
- Mobile + API + Zero Trust Security Architecture
- Lakehouse Analytics Data Architecture
- AI Inference Platform Architecture

---

**Status:** Living document – automatically synchronized with README.md files in architecture-general directory.
