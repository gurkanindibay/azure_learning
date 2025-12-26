# Application Architecture Styles

## Table of Contents

- [Overview](#overview)
- [1. Monolithic Architecture](#1-monolithic-architecture)
- [2. Modular Monolith](#2-modular-monolith)
- [3. Layered Architecture](#3-layered-architecture)
- [4. N-Tier Architecture](#4-n-tier-architecture)
- [5. Clean Architecture](#5-clean-architecture)
- [6. Hexagonal Architecture (Ports & Adapters)](#6-hexagonal-architecture-ports--adapters)
- [7. Onion Architecture](#7-onion-architecture)
- [Architecture Comparison](#architecture-comparison)
- [Decision Guide](#decision-guide)

---

## Overview

Application architecture styles define how software components are organized, how they communicate, and how responsibilities are distributed. Choosing the right architecture impacts:

- **Maintainability** - How easy is it to modify and extend?
- **Testability** - How easy is it to write and run tests?
- **Scalability** - How well does it handle growth?
- **Team Organization** - How does it affect team structure?
- **Deployment** - How is the application deployed and updated?

---

## 1. Monolithic Architecture

### Definition

A **Monolithic Architecture** is a traditional unified model where all application components are interconnected and interdependent, deployed as a single unit.

### Structure

```
┌─────────────────────────────────────────┐
│           Monolithic Application        │
├─────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  User   │ │  Order  │ │ Product │   │
│  │ Module  │ │ Module  │ │ Module  │   │
│  └────┬────┘ └────┬────┘ └────┬────┘   │
│       │           │           │         │
│  ┌────┴───────────┴───────────┴────┐   │
│  │       Shared Database           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| Deployment | Single deployable unit |
| Database | Typically single shared database |
| Communication | In-process function calls |
| Scaling | Vertical scaling (scale the entire app) |
| Technology | Single technology stack |

### Advantages

- ✅ Simple to develop initially
- ✅ Easy to test end-to-end
- ✅ Simple deployment process
- ✅ No network latency between components
- ✅ Simple debugging and tracing

### Disadvantages

- ❌ Difficult to scale individual components
- ❌ Large codebase becomes hard to maintain
- ❌ Long deployment cycles
- ❌ Technology stack lock-in
- ❌ Single point of failure

### When to Use

- Small to medium applications
- Startups with limited resources
- Applications with simple domain logic
- Teams with limited microservices experience
- Proof of concepts or MVPs

---

## 2. Modular Monolith

### Definition

A **Modular Monolith** is a monolithic application that is internally divided into loosely coupled modules, each encapsulating a specific business domain.

### Structure

```
┌─────────────────────────────────────────────────────┐
│              Modular Monolith Application           │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ User Module │  │Order Module │  │Product Module│ │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │ │
│  │ │   API   │ │  │ │   API   │ │  │ │   API   │ │ │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │ │
│  │ │ Domain  │ │  │ │ Domain  │ │  │ │ Domain  │ │ │
│  │ ├─────────┤ │  │ ├─────────┤ │  │ ├─────────┤ │ │
│  │ │  Data   │ │  │ │  Data   │ │  │ │  Data   │ │ │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │        │
│  ┌──────┴────────────────┴────────────────┴──────┐ │
│  │        Shared Infrastructure / Database       │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Module Communication Rules

```
┌─────────────────────────────────────────────────────┐
│                  Communication Rules                │
├─────────────────────────────────────────────────────┤
│  ✅ Modules communicate through well-defined APIs  │
│  ✅ Each module owns its data                       │
│  ✅ No direct database access across modules        │
│  ❌ No sharing of internal classes                  │
│  ❌ No circular dependencies                        │
└─────────────────────────────────────────────────────┘
```

### Characteristics

| Aspect | Description |
|--------|-------------|
| Deployment | Single deployable unit |
| Database | Shared or separate schemas per module |
| Communication | In-process via public APIs |
| Boundaries | Clear module boundaries enforced |
| Evolution | Easier path to microservices |

### Advantages

- ✅ Better code organization than traditional monolith
- ✅ Enforced boundaries between domains
- ✅ Easier to understand and maintain
- ✅ Can evolve to microservices if needed
- ✅ Single deployment simplicity

### Disadvantages

- ❌ Still deployed as a single unit
- ❌ Requires discipline to maintain boundaries
- ❌ Still shares the same process/runtime
- ❌ Cannot scale modules independently

### When to Use

- Medium to large applications needing better organization
- Teams planning potential migration to microservices
- Applications with clear domain boundaries
- When you want monolith simplicity with better structure

---

## 3. Layered Architecture

### Definition

**Layered Architecture** (also called N-Layer) organizes code into horizontal layers, where each layer has a specific responsibility and can only communicate with adjacent layers.

### Structure

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│   (UI, Controllers, Views, DTOs)        │
└────────────────────┬────────────────────┘
                     │ ▼
┌────────────────────┴────────────────────┐
│         Business Logic Layer            │
│   (Services, Business Rules, Workflow)  │
└────────────────────┬────────────────────┘
                     │ ▼
┌────────────────────┴────────────────────┐
│         Data Access Layer               │
│   (Repositories, ORM, Data Mappers)     │
└────────────────────┬────────────────────┘
                     │ ▼
┌────────────────────┴────────────────────┐
│              Database                   │
└─────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| Presentation | User interface and input handling | Controllers, Views, API endpoints |
| Business Logic | Core business rules and workflows | Services, Validators, Domain logic |
| Data Access | Data persistence and retrieval | Repositories, ORMs, Query builders |
| Database | Data storage | SQL Server, PostgreSQL, MongoDB |

### Dependency Flow

```
┌─────────────────────────────────────────────────────┐
│              Dependency Direction                   │
│                                                     │
│    Presentation ──► Business ──► Data Access       │
│                                                     │
│    ✅ Top layers depend on lower layers            │
│    ❌ Lower layers should NOT depend on upper      │
└─────────────────────────────────────────────────────┘
```

### Advantages

- ✅ Simple and well-understood pattern
- ✅ Separation of concerns
- ✅ Easy to develop and test layers independently
- ✅ Common skillset among developers
- ✅ Good for CRUD-heavy applications

### Disadvantages

- ❌ Can lead to "leaky abstractions"
- ❌ Changes often require updates across all layers
- ❌ Database-centric thinking
- ❌ Business logic can leak into other layers
- ❌ Tight coupling between layers

### When to Use

- Simple CRUD applications
- Teams familiar with traditional patterns
- Applications with straightforward business logic
- Rapid development projects

---

## 4. N-Tier Architecture

### Definition

**N-Tier Architecture** physically separates application layers into different tiers (servers/deployments), enabling independent scaling and deployment.

### Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        N-Tier Architecture                  │
└─────────────────────────────────────────────────────────────┘

    Client Tier              Application Tier           Data Tier
   ┌───────────┐            ┌───────────────┐        ┌───────────┐
   │           │            │               │        │           │
   │  Browser  │◄──HTTP────►│  Web Server   │        │  Database │
   │           │            │  (IIS/Nginx)  │        │  Server   │
   └───────────┘            └───────┬───────┘        └─────▲─────┘
                                    │                      │
   ┌───────────┐            ┌───────▼───────┐              │
   │           │            │               │              │
   │  Mobile   │◄──HTTP────►│  App Server   │◄────SQL─────►│
   │   App     │            │ (API/Services)│              │
   └───────────┘            └───────────────┘              │
                                                           │
                            ┌───────────────┐              │
                            │    Cache      │◄─────────────┘
                            │   (Redis)     │
                            └───────────────┘
```

### Common Tier Configurations

| Configuration | Description |
|--------------|-------------|
| 2-Tier | Client + Database |
| 3-Tier | Client + Application Server + Database |
| N-Tier | Multiple application tiers (Web, API, Services, etc.) |

### Characteristics

| Aspect | Description |
|--------|-------------|
| Deployment | Each tier deployed separately |
| Communication | Network calls between tiers |
| Scaling | Each tier scales independently |
| Security | Network boundaries between tiers |
| Maintenance | Tiers can be updated independently |

### Advantages

- ✅ Independent scaling of tiers
- ✅ Better security through network isolation
- ✅ Flexibility in technology choices per tier
- ✅ High availability configurations
- ✅ Clear deployment boundaries

### Disadvantages

- ❌ Network latency between tiers
- ❌ More complex infrastructure
- ❌ Harder to debug across tiers
- ❌ Higher operational complexity
- ❌ Requires more DevOps expertise

### When to Use

- Enterprise applications requiring scalability
- Applications with high availability requirements
- When different tiers need different scaling strategies
- Security-sensitive applications

---

## 5. Clean Architecture

### Definition

**Clean Architecture** (proposed by Robert C. Martin) emphasizes separation of concerns through concentric layers with dependencies pointing inward toward the domain.

### Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│    ┌─────────────────────────────────────────────────────┐     │
│    │            Frameworks & Drivers (Outer)             │     │
│    │    UI, Database, Web Frameworks, External APIs      │     │
│    │  ┌─────────────────────────────────────────────┐   │     │
│    │  │         Interface Adapters                  │   │     │
│    │  │    Controllers, Gateways, Presenters        │   │     │
│    │  │  ┌─────────────────────────────────────┐   │   │     │
│    │  │  │      Application Business Rules      │   │   │     │
│    │  │  │         Use Cases / Services         │   │   │     │
│    │  │  │  ┌─────────────────────────────┐    │   │   │     │
│    │  │  │  │   Enterprise Business Rules  │    │   │   │     │
│    │  │  │  │      Entities / Domain       │    │   │   │     │
│    │  │  │  └─────────────────────────────┘    │   │   │     │
│    │  │  └─────────────────────────────────────┘   │   │     │
│    │  └─────────────────────────────────────────────┘   │     │
│    └─────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Dependencies point INWARD ───────────────────────────────────────►
```

### The Dependency Rule

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE DEPENDENCY RULE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Source code dependencies must point ONLY INWARD               │
│                                                                 │
│  Inner layers:                                                  │
│    ✅ Know nothing about outer layers                          │
│    ✅ Define interfaces that outer layers implement            │
│    ✅ Contain business rules and entities                      │
│                                                                 │
│  Outer layers:                                                  │
│    ✅ Depend on inner layers                                   │
│    ✅ Implement interfaces defined by inner layers             │
│    ✅ Handle infrastructure concerns                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Details

| Layer | Purpose | Contains |
|-------|---------|----------|
| Entities | Core business objects | Domain models, business rules |
| Use Cases | Application-specific logic | Interactors, application services |
| Interface Adapters | Convert data formats | Controllers, presenters, gateways |
| Frameworks | External tools | UI, DB, frameworks, drivers |

### Project Structure Example

```
src/
├── Domain/                 # Entities (innermost)
│   ├── Entities/
│   └── ValueObjects/
├── Application/            # Use Cases
│   ├── Interfaces/
│   ├── UseCases/
│   └── DTOs/
├── Infrastructure/         # Interface Adapters + Frameworks
│   ├── Persistence/
│   ├── ExternalServices/
│   └── Messaging/
└── Presentation/           # UI / API
    ├── Controllers/
    └── ViewModels/
```

### Advantages

- ✅ Framework independence
- ✅ Highly testable (domain can be tested without UI/DB)
- ✅ UI independence
- ✅ Database independence
- ✅ External agency independence

### Disadvantages

- ❌ More complex structure
- ❌ More boilerplate code
- ❌ Steeper learning curve
- ❌ Over-engineering for simple applications
- ❌ Requires discipline to maintain

### When to Use

- Complex domain logic applications
- Long-lived applications requiring maintainability
- Applications where business rules change frequently
- Teams practicing Domain-Driven Design (DDD)

---

## 6. Hexagonal Architecture (Ports & Adapters)

### Definition

**Hexagonal Architecture** (proposed by Alistair Cockburn) isolates the application core from external concerns using ports (interfaces) and adapters (implementations).

### Structure

```
                    Primary/Driving Adapters
                    (Input)
                           │
            ┌──────────────┼──────────────┐
            │              ▼              │
            │  ┌─────────────────────┐   │
   REST ────┼─►│   Primary Ports     │   │
   API      │  │   (Interfaces)      │   │
            │  └──────────┬──────────┘   │
            │             │              │
   GraphQL ─┼────────────►│              │
            │             ▼              │
            │  ┌─────────────────────┐   │
   CLI ─────┼─►│   Application       │   │
            │  │   Core              │   │
            │  │   (Domain Logic)    │   │
            │  └──────────┬──────────┘   │
   Message  │             │              │
   Queue ───┼────────────►│              │
            │             ▼              │
            │  ┌─────────────────────┐   │
            │  │  Secondary Ports    │◄──┼──── Database
            │  │  (Interfaces)       │   │     Adapter
            │  └─────────────────────┘   │
            │             │              │◄──── Email
            │             ▼              │      Adapter
            └─────────────┼──────────────┘
                          │              │◄──── Cache
                Secondary/Driven Adapters│      Adapter
                (Output)
```

### Ports and Adapters Explained

| Concept | Description | Examples |
|---------|-------------|----------|
| **Primary Ports** | Interfaces for driving the application | IOrderService, IUserService |
| **Primary Adapters** | Implement input mechanisms | REST Controller, CLI, Message Handler |
| **Secondary Ports** | Interfaces for things the app needs | IRepository, IEmailSender |
| **Secondary Adapters** | Implement external dependencies | SQLRepository, SmtpEmailSender |

### Code Structure Example

```
src/
├── Core/                          # The Hexagon
│   ├── Domain/
│   │   ├── Order.cs
│   │   └── Customer.cs
│   ├── Ports/
│   │   ├── Driving/              # Primary Ports (Input)
│   │   │   ├── IOrderService.cs
│   │   │   └── ICustomerService.cs
│   │   └── Driven/               # Secondary Ports (Output)
│   │       ├── IOrderRepository.cs
│   │       └── INotificationService.cs
│   └── Services/
│       └── OrderService.cs       # Implements Driving Ports
│
├── Adapters/
│   ├── Driving/                  # Primary Adapters
│   │   ├── Web/
│   │   │   └── OrderController.cs
│   │   └── CLI/
│   │       └── OrderCLI.cs
│   └── Driven/                   # Secondary Adapters
│       ├── Persistence/
│       │   └── SqlOrderRepository.cs
│       └── Notifications/
│           └── EmailNotificationService.cs
```

### Advantages

- ✅ Clear separation between core and infrastructure
- ✅ Easy to swap adapters (change database, UI, etc.)
- ✅ Highly testable (mock adapters for testing)
- ✅ Technology-agnostic core
- ✅ Supports multiple input channels

### Disadvantages

- ❌ Additional complexity and abstractions
- ❌ More interfaces and classes
- ❌ Can be over-engineering for simple apps
- ❌ Learning curve for new team members

### When to Use

- Applications with multiple input channels (API, CLI, Events)
- When infrastructure may change (database, external services)
- Complex business logic that needs isolation
- Applications requiring high testability

---

## 7. Onion Architecture

### Definition

**Onion Architecture** (proposed by Jeffrey Palermo) is similar to Clean Architecture, with concentric layers and dependencies pointing toward the center, with a strong emphasis on domain-centric design.

### Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                        │
│              (UI, Database, External Services)                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Application Layer                      │   │
│  │           (Application Services, DTOs, CQRS)             │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │              Domain Services Layer               │    │   │
│  │  │        (Domain Services, Business Rules)         │    │   │
│  │  │  ┌─────────────────────────────────────────┐    │    │   │
│  │  │  │          Domain Model Layer              │    │    │   │
│  │  │  │     (Entities, Value Objects, Enums)     │    │    │   │
│  │  │  └─────────────────────────────────────────┘    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

All dependencies point INWARD toward the Domain Model
```

### Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| Domain Model | Core business entities and rules | None |
| Domain Services | Complex business operations | Domain Model |
| Application | Orchestration and use cases | Domain Services, Domain Model |
| Infrastructure | Technical implementations | All inner layers |

### Key Principles

```
┌─────────────────────────────────────────────────────────────────┐
│                  ONION ARCHITECTURE PRINCIPLES                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. The Domain Model is at the center                          │
│                                                                 │
│  2. All dependencies point toward the center                   │
│                                                                 │
│  3. Inner layers define interfaces, outer layers implement     │
│                                                                 │
│  4. Infrastructure is in the outermost layer                   │
│                                                                 │
│  5. Coupling is toward the center (domain)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure Example

```
src/
├── Domain/                    # Center - Domain Model
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Enums/
│   └── Exceptions/
├── Domain.Services/           # Domain Services
│   └── PricingService.cs
├── Application/               # Application Layer
│   ├── Interfaces/           
│   │   ├── IOrderRepository.cs
│   │   └── IEmailService.cs
│   ├── Services/
│   │   └── OrderApplicationService.cs
│   └── DTOs/
└── Infrastructure/            # Outermost Layer
    ├── Persistence/
    │   └── OrderRepository.cs
    ├── Email/
    │   └── SmtpEmailService.cs
    └── Web/
        └── Controllers/
```

### Advantages

- ✅ Strong domain focus
- ✅ Testable without infrastructure
- ✅ Flexible and adaptable to change
- ✅ Clear separation of concerns
- ✅ Infrastructure can be easily replaced

### Disadvantages

- ❌ More complex than layered architecture
- ❌ Additional abstraction layers
- ❌ Can feel bureaucratic for simple projects
- ❌ Requires understanding of DDD concepts

### When to Use

- Domain-driven design projects
- Complex business domains
- Applications with rich domain logic
- Long-lived enterprise applications

---

## Architecture Comparison

### Feature Comparison Matrix

| Feature | Monolithic | Modular Monolith | Layered | N-Tier | Clean | Hexagonal | Onion |
|---------|------------|------------------|---------|--------|-------|-----------|-------|
| **Complexity** | Low | Medium | Low | Medium | High | High | High |
| **Testability** | Low | Medium | Medium | Medium | High | High | High |
| **Maintainability** | Low | Medium | Medium | Medium | High | High | High |
| **Scalability** | Low | Low | Low | High | Medium | Medium | Medium |
| **Coupling** | High | Medium | Medium | Low | Low | Low | Low |
| **Learning Curve** | Low | Low | Low | Medium | High | High | High |
| **Domain Focus** | Low | Medium | Low | Low | High | High | High |

### Deployment Comparison

| Architecture | Deployment Unit | Scaling Strategy |
|-------------|-----------------|------------------|
| Monolithic | Single unit | Vertical |
| Modular Monolith | Single unit | Vertical |
| Layered | Single unit (logical) | Vertical |
| N-Tier | Multiple tiers | Horizontal per tier |
| Clean | Single or multiple | Depends on implementation |
| Hexagonal | Single or multiple | Depends on implementation |
| Onion | Single or multiple | Depends on implementation |

### Dependency Direction

```
┌──────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY DIRECTIONS                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layered:     UI → Business → Data → Database                   │
│               (Top to Bottom)                                    │
│                                                                  │
│  Clean:       Outer → Inner (toward Entities)                   │
│               Infrastructure → Use Cases → Entities              │
│                                                                  │
│  Hexagonal:   Adapters → Ports → Core                           │
│               External → Interfaces → Domain                     │
│                                                                  │
│  Onion:       Outside → Inside (toward Domain Model)            │
│               Infrastructure → App → Domain Services → Domain    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Clean vs Hexagonal vs Onion

| Aspect | Clean | Hexagonal | Onion |
|--------|-------|-----------|-------|
| **Creator** | Robert C. Martin | Alistair Cockburn | Jeffrey Palermo |
| **Core Concept** | Dependency Rule | Ports & Adapters | Domain-centric layers |
| **Focus** | Use Cases | Input/Output isolation | Domain Model |
| **Layers** | 4 concentric | Hexagon with adapters | 4 concentric |
| **Key Metaphor** | Circles | Hexagon with ports | Onion layers |

> **Note**: Clean, Hexagonal, and Onion architectures share similar principles and are often used interchangeably. The key insight from all three is **dependency inversion** - the domain/core should not depend on external concerns.

---

## Decision Guide

### When to Choose Each Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION FLOWCHART                           │
└─────────────────────────────────────────────────────────────────┘

Start
  │
  ▼
Is it a simple CRUD app? ──Yes──► Layered or Monolithic
  │
  No
  │
  ▼
Need physical tier separation? ──Yes──► N-Tier
  │
  No
  │
  ▼
Complex domain logic? ──Yes──┬──► Clean / Hexagonal / Onion
  │                          │
  No                         └──► With DDD: Onion
  │
  ▼
Need better organization ──Yes──► Modular Monolith
but keep single deployment?
  │
  No
  │
  ▼
Default ──────────────────────► Layered (simple)
                                or Modular Monolith (medium)
```

### Quick Reference Guide

| Scenario | Recommended Architecture |
|----------|-------------------------|
| MVP / Prototype | Monolithic |
| Simple CRUD App | Layered |
| Complex Business Logic | Clean / Hexagonal / Onion |
| Enterprise with Scaling Needs | N-Tier |
| Potential Microservices Migration | Modular Monolith |
| Multiple Input Channels | Hexagonal |
| Domain-Driven Design | Onion or Clean |
| Team New to Architecture | Layered → Modular Monolith |

### Evolution Path

```
Monolithic ──► Modular Monolith ──► Microservices
     │                │
     │                └──► Clean / Hexagonal / Onion
     │                     (Better internal architecture)
     ▼
  Layered (if simple CRUD focus)
```

---

## Related Topics

- [Domain-Driven Design](../domain-driven-design/)
- [Design Patterns](../design-patterns/)
- [Microservices Architecture](../../03-integration-communication-architecture/)

---

## References

- Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*
- Cockburn, A. (2005). *Hexagonal Architecture*
- Palermo, J. (2008). *The Onion Architecture*
- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*
