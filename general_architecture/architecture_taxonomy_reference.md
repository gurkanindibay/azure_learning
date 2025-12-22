# Architecture Taxonomy – Comprehensive Reference

This document is a **canonical markdown reference** for commonly recognized architecture types used in enterprise, cloud, and software engineering contexts. It is suitable for **architecture handbooks, governance boards, interviews, and internal standards**.

---

## 1. Enterprise & Strategic Architecture

### 1.1 Enterprise Architecture
- Business Architecture
- Capability Architecture
- Value Stream Architecture
- Organization Architecture

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
- RPC Architecture
- Backend-for-Frontend (BFF)
- Serverless Backend Architecture

### 2.3 Frontend Architecture
- Web Architecture
- Single Page Application (SPA)
- Server-Side Rendering (SSR / ISR)
- Micro-Frontend Architecture
- Edge-rendered Architecture

### 2.4 Mobile Architecture
- Native Mobile Architecture
- Cross-Platform Architecture
- Offline-First Architecture
- Mobile Backend Architecture
- Super-App Architecture

---

## 3. Integration & Communication Architecture

### 3.1 Integration Architecture
- Point-to-Point Integration
- Hub-and-Spoke Architecture
- Enterprise Service Bus (ESB)
- API-Led Architecture
- B2B / EDI Architecture

### 3.2 API Architecture
- REST API Architecture
- GraphQL API Architecture
- AsyncAPI Architecture
- OpenAPI-driven Architecture
- API Gateway Architecture

### 3.3 Event-Driven Architecture
- Event Streaming Architecture
- Event Sourcing
- CQRS (Command Query Responsibility Segregation)
- Pub/Sub Architecture
- Reactive Architecture

### 3.4 Messaging Architecture
- Message Queue Architecture
- Broker-based Architecture
- Stream Processing Architecture

---

## 4. Data, Analytics & AI Architecture

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

---

## 7. Reliability, Performance & Operations

### 7.1 Reliability Architecture
- High Availability (HA)
- Disaster Recovery (DR)
- Fault-Tolerant Architecture
- Chaos Engineering Architecture

### 7.2 Performance Architecture
- Low-Latency Architecture
- Caching Architecture
- Load Balancing Architecture
- Edge Optimization

### 7.3 Observability Architecture
- Logging Architecture
- Metrics Architecture
- Distributed Tracing
- Monitoring Architecture

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

---

## 9. Industry & Specialized Architectures

### 9.1 Industry Architectures
- Financial Services Architecture
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

---

## 10. Architectural Qualities (Non-Functional)

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

**Status:** Living document – intended to evolve with organizational and industry needs.

