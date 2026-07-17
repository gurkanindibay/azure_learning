---
type: Reference
title: "Design Patterns & Software Engineering Principles"
description: "A **creational pattern** that ensures a class has only one instance and provides a global access point to it."
timestamp: 2026-07-04T00:00:00Z
---

# Design Patterns & Software Engineering Principles

> **Domain**: Gang of Four (GoF) design patterns, software engineering principles, and architectural decision-making.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Singleton | [`#singleton`](#singleton) |
| Factory Method | [`#factory-method`](#factory-method) |
| Builder Pattern | [`#builder-pattern`](#builder-pattern) |
| Adapter Pattern | [`#adapter-pattern`](#adapter-pattern) |
| Decorator Pattern | [`#decorator-pattern`](#decorator-pattern) |
| Proxy Pattern | [`#proxy-pattern`](#proxy-pattern) |
| Strategy Pattern | [`#strategy-pattern`](#strategy-pattern) |
| Observer Pattern | [`#observer-pattern`](#observer-pattern) |
| Command Pattern | [`#command-pattern`](#command-pattern) |
| Repository Pattern | [`#repository-pattern`](#repository-pattern) |
| Golden Hammer | [`#golden-hammer`](#golden-hammer) |
| YAGNI | [`#yagni`](#yagni) |
| Separation of Concerns | [`#separation-of-concerns`](#separation-of-concerns) |
| Fail Fast | [`#fail-fast`](#fail-fast) |
| Single Source of Truth | [`#single-source-of-truth`](#single-source-of-truth) |
| Loose Coupling | [`#loose-coupling`](#loose-coupling) |
| Immutability | [`#immutability`](#immutability) |
| Scalability | [`#scalability`](#scalability) |
| Architecture Decision Record | [`#architecture-decision-record`](#architecture-decision-record) |
| Anti-pattern | [`#anti-pattern`](#anti-pattern) |
| Service Provider Interface (SPI) | [`#service-provider-interface`](#service-provider-interface) |

---

## Singleton

A **creational pattern** that ensures a class has only one instance and provides a global access point to it. Used for shared resources — configuration managers, connection pools, cache managers — where a single source-of-truth is required.

### Key Characteristics
- Private constructor prevents external instantiation
- Static volatile field + double-checked locking for thread safety
- Lazy initialization: instance created on first access

### When to Use
- JVM-scoped shared resources: feature-flag services, config managers
- Framework-managed singletons (Spring `@Bean`, CDI) preferred over hand-rolled ones

### When NOT to Use
- When the "single instance" assumption will change (e.g., tests need separate instances)
- For objects with mutable state accessed by many threads — leads to contention and hidden coupling

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-01-shared-resource-multiple-instantiation)

---

## Factory Method

A **creational pattern** that defines an interface for creating objects but lets subclasses or a factory function decide which concrete class to instantiate. Clients are decoupled from the creation logic.

### Key Characteristics
- Static factory function or an abstract `createX()` method in a base class
- Returns an interface type, not a concrete type
- Creation logic is centralised — easy to extend via new cases

### When to Use
- Creating protocol-specific clients (HTTP/gRPC/Kafka) based on config
- Plugin architectures where the set of implementations varies at runtime
- When mocking in tests requires swapping implementations

### When NOT to Use
- For trivial, unconditional `new Foo()` calls — the indirection adds no value

### Also see
- [Builder Pattern](#builder-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-02-complex-object-creation-scattered-across-clients)

---

## Builder Pattern

A **creational pattern** that constructs complex objects step-by-step using a fluent API, separating construction from representation and enabling immutability.

### Key Characteristics
- Nested `Builder` class accumulates optional/required fields
- `build()` validates and returns the fully constructed, immutable object
- Eliminates telescoping constructors and invalid intermediate states

### When to Use
- Complex DTOs or value objects with many optional fields
- Constructing requests to external services or configuration objects
- When immutability is required and setter-based construction is unsafe

### When NOT to Use
- Simple objects with ≤2 fields — a plain constructor is clearer
- When the object is mutable by design

### Also see
- [Factory Method](#factory-method) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-03-telescoping-constructors-for-complex-objects)

---

## Adapter Pattern

A **structural pattern** that converts the interface of an existing class into the interface that clients expect. Used to integrate legacy systems or third-party SDKs without modifying them.

### Key Characteristics
- Implements the target interface; holds a reference to the adaptee
- Translates method calls from the target contract to the legacy API
- Encapsulates all integration/translation code in one place

### When to Use
- Wrapping legacy `CSVReader`, third-party SDKs, or external APIs to match internal contracts
- When a domain abstraction must remain clean and external changes should be isolated

### When NOT to Use
- When the interfaces are already compatible — adds unnecessary indirection
- When the legacy code will be replaced soon and temporary coupling is acceptable

### Also see
- [Anti-Corruption Layer](architecture-patterns.md#anti-corruption-layer) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-04-integrating-incompatible-interfaces)

---

## Decorator Pattern

A **structural pattern** that adds behavior to an object dynamically by wrapping it with another object that implements the same interface. Used for cross-cutting concerns (logging, caching, metrics) without modifying the original class.

### Key Characteristics
- Decorator implements the same interface as the wrapped component
- Delegates the core operation to the inner component, adding behavior before/after
- Decorators can be composed in chains

### When to Use
- Adding logging, metrics, caching, or audit to repository or service implementations
- When subclassing would create class explosion for each combination of behaviors

### When NOT to Use
- Deep chains (>3 layers) — hard to debug; prefer an AOP framework instead
- When the added behavior is unconditional and permanent — just modify the class

### Also see
- [Proxy Pattern](#proxy-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-05-adding-cross-cutting-behaviors-without-subclassing)

---

## Proxy Pattern

A **structural pattern** that provides a surrogate for another object to control access, enable lazy initialization, or intercept calls for security/logging. The proxy and the real object share the same interface.

### Key Characteristics
- Virtual proxy: defers creation of the real object until first use
- Protection proxy: checks permissions before delegating
- Remote proxy: marshals calls to a remote object (gRPC stubs)

### When to Use
- Lazy loading of expensive resources (images, large datasets)
- Security checkpoints before delegating to a sensitive operation
- gRPC/stub proxies and remote service clients

### When NOT to Use
- When the proxy introduces unexpected latency that callers cannot anticipate
- When caching is the main goal — prefer the [Decorator Pattern](#decorator-pattern) for explicit caching wrappers

### Also see
- [Decorator Pattern](#decorator-pattern) · [Ambassador Pattern](architecture-patterns.md#ambassador-pattern) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-06-controlling-access-and-lazy-initialization)

---

## Strategy Pattern

A **behavioral pattern** that defines a family of algorithms, encapsulates each as an object, and makes them interchangeable. Clients select or inject the desired strategy at construction or runtime.

### Key Characteristics
- Common interface implemented by each concrete strategy
- Strategy is injected into the context (composition over inheritance)
- Open/Closed Principle: add new strategies without modifying the client

### When to Use
- Payment routing: choose strategy based on currency, region, or dynamic rules
- Discount calculation, sorting, risk scoring where the algorithm varies by context
- When algorithm variants need independent testing

### When NOT to Use
- When only one strategy will ever exist — inline the algorithm
- When the strategy selection logic itself becomes more complex than the algorithms

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-07-swappable-algorithms-at-runtime)

---

## Observer Pattern

A **behavioral pattern** that defines a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified automatically.

### Key Characteristics
- Subject maintains a list of observers (listeners); observers register/unregister
- Decouples the event source from its handlers — the publisher knows nothing about consumers
- `CopyOnWriteArrayList` or similar thread-safe collection for concurrent listener registration

### When to Use
- Domain events within a single JVM (user registered, payment processed)
- Reactive UIs where model changes must propagate to multiple view components
- Simple pub/sub within a monolith

### When NOT to Use
- Cross-service events — use an explicit message broker (Kafka, Service Bus) for durability, ordering, and replay
- When listener ordering matters — Observer does not guarantee it
- Watch for memory leaks: always deregister listeners when the consumer is destroyed

### Also see
- [Messaging Dictionary](messaging.md) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-08-decoupling-producers-from-consumers)

---

## Command Pattern

A **behavioral pattern** that encapsulates a request as a standalone object containing all information needed to execute the action. Enables queuing, scheduling, auditing, retry, and undo.

### Key Characteristics
- Command object holds the action, its parameters, and a reference to the receiver
- Commands can be serialized, stored, and replayed
- An `execute()` method is the single invocation point

### When to Use
- Job schedulers and message-based work queues
- GUI actions with undo/redo support
- Audit logs where each state-changing action must be persisted

### When NOT to Use
- Trivial, synchronous, non-replayable operations — the object creation overhead is not justified
- When all you need is a `Runnable` lambda — avoid the formalism

### Also see
- [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-09-encapsulating-requests-for-queuing-and-undo)

---

## Repository Pattern

An **enterprise pattern** that abstracts data access behind a domain-oriented interface. The repository maps domain objects to and from the persistence store, keeping the domain model pure and decoupled from persistence technology.

### Key Characteristics
- Interface exposes domain-specific query methods (`findByEmail`, `findActiveOrders`)
- The implementation encapsulates JPA/JDBC/NoSQL details
- Trivially mockable in unit tests — swap with an in-memory implementation

### When to Use
- Any domain where you want to swap persistence technology without touching business logic
- Domain-Driven Design contexts where the domain model must remain clean
- When unit-testing domain logic without a database

### When NOT to Use
- Anemic repositories that only mirror CRUD add indirection with no benefit — use the ORM directly
- Leaky abstractions that expose `EntityManager` or query builders negate the purpose

### Also see
- [DDD](architecture-patterns.md#ddd) · [Database Per Service](architecture-patterns.md#database-per-service) · [CQRS](cqrs-event-driven.md#cqrs) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-10-leaky-data-access-in-domain-logic)

---

## Golden Hammer

An **anti-pattern** where a familiar pattern or tool is applied to every problem regardless of fit. The name comes from "if all you have is a hammer, everything looks like a nail."

### Key Characteristics
- Pattern applied out of habit or comfort, not because it solves the current problem
- Results in over-engineered, hard-to-understand codebases
- Often accompanied by over-abstraction

### When to Use
- N/A — this is an anti-pattern. Recognise and avoid it.

### When NOT to Use
- Always — prefer matching the solution to the actual problem

### Also see
- [YAGNI](#yagni) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-12-choosing-the-right-pattern) · [Pragmatic System Design](../system-design-architecture/18-pragmatic-system-design-takeaways.md)

---

## YAGNI

**You Aren't Gonna Need It** — an extreme programming principle stating that a feature or abstraction should not be added until it is actually needed. Prevents speculative complexity.

### Key Characteristics
- Defer implementation until there is a concrete, current requirement
- Refactor into a pattern when the need arises, not in anticipation of it
- Pairs with KISS (Keep It Simple, Stupid) and incremental design

### When to Use
- When considering whether to add CQRS, Saga, or a complex pattern to a simple domain
- When tempted to build a "framework" for a one-time use case

### When NOT to Use
- Security and compliance requirements — do not defer security controls under YAGNI
- Public API contracts — breaking changes are expensive; design them carefully upfront

### Also see
- [Golden Hammer](#golden-hammer) · [Design Patterns Key Takeaways](../system-design-architecture/39-design-patterns-key-takeaways.md#dp-12-choosing-the-right-pattern)

---

## Separation of Concerns

A design principle that assigns each module, class, or service one well-defined responsibility, keeping internal cohesion high and external coupling low.

### Key Characteristics
- Each component has a single reason to change
- Boundaries are drawn along responsibilities, not along implementation details
- Changes in one concern do not cascade into unrelated concerns

### When to Use
- When a module grows large enough that its tests, reviews, and deployments span multiple teams
- When business capabilities can be clearly distinguished

### When NOT to Use
- When over-separation creates more interfaces and deployment units than a small team can operate
- When premature abstraction hides a simple, cohesive workflow

### Also see
- [Loose Coupling](#loose-coupling) · [Bounded Context](architecture-patterns.md#bounded-context) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-02-separation-of-concerns)

---

## Fail Fast

A reliability principle that detects invalid state or unexpected conditions as early as possible, at the closest boundary to where the problem originates.

### Key Characteristics
- Validates inputs and assumptions at system boundaries
- Rejects bad state before it can propagate downstream
- Surfaces failures loudly rather than swallowing exceptions

### When to Use
- At API boundaries, message consumers, and dependency calls
- In distributed systems where defect cost grows exponentially with distance from source

### When NOT to Use
- When aggressive failure prevents graceful degradation that users depend on
- When it replaces proper error handling with panic-driven code

### Also see
- [Defense in Depth](resilience.md#defense-in-depth) · [Circuit Breaker](resilience.md#circuit-breaker) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-04-fail-fast)

---

## Single Source of Truth

A data principle stating that every important fact has exactly one authoritative location. Derived stores may cache or project the fact, but they do not redefine it.

### Key Characteristics
- One system owns writes for each fact
- Read replicas, caches, search indices, and warehouses are fed from the source
- Eliminates reconciliation drift between competing authorities

### When to Use
- When multiple teams or systems need consistent views of the same entity
- In event-sourced or CDC-driven architectures

### When NOT to Use
- When the single writer becomes a contention or availability bottleneck that cannot be partitioned
- When the domain genuinely requires independent bounded contexts with their own truths

### Also see
- [CQRS](cqrs-event-driven.md#cqrs-command-query-responsibility-segregation) · [Event Sourcing](cqrs-event-driven.md#event-sourcing) · [Dual-Write Problem](cqrs-event-driven.md#dual-write-problem) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-05-single-source-of-truth)

---

## Loose Coupling

An architectural principle in which components interact through stable, well-defined contracts so that changes to one component do not force changes in others.

### Key Characteristics
- Contracts are explicit: schemas, APIs, event schemas, or protocols
- Components can be deployed, scaled, and replaced independently
- Asynchronous communication is preferred where eventual consistency is acceptable

### When to Use
- Microservices, modular monoliths, and multi-team codebases
- Any system where deployment independence is a goal

### When NOT to Use
- When a tightly-knit algorithm or transaction must remain consistent and fast
- When contract governance overhead exceeds the value of independence

### Also see
- [Separation of Concerns](#separation-of-concerns) · [API Gateway](api-design.md) · [Message Brokers](../system-design-architecture/05-message-brokers-async.md) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-06-loose-coupling)

---

## Immutability

A design principle that avoids mutating state in place by creating new versions of data and preserving history.

### Key Characteristics
- State changes produce new values rather than modifying existing ones
- Eliminates a large class of concurrency bugs and reproducibility issues
- Enables event sourcing, audit trails, and content-addressed artifacts

### When to Use
- Distributed systems with shared state
- ML/AI pipelines where reproducibility depends on frozen datasets, models, and prompts

### When NOT to Use
- When storage cost or query patterns make append-only data impractical
- When every operation must update a single current value and history adds no value

### Also see
- [Event Sourcing](cqrs-event-driven.md#event-sourcing) · [Immutability in Java](java-jvm.md) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-07-immutability)

---

## Scalability

The ability of a system to absorb growth in load — 10x, 100x, or more — without requiring fundamental architectural changes.

### Key Characteristics
- Horizontal scale: add more nodes rather than bigger nodes
- Stateless services, careful partitioning, and elastic resources
- Caching, asynchronous processing, and database sharding planned before they are urgently needed

### When to Use
- Products with planned growth, viral potential, or seasonal spikes
- Any architecture review that asks "what happens if this succeeds?"

### When NOT to Use
- As premature optimization for products with unproven demand
- When horizontal elasticity adds more operational complexity than the team can support

### Also see
- [Vertical vs Horizontal Scaling](#) · [Caching](caching.md) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md#arch-09-scalability-by-design)

---

## Architecture Decision Record

A **lightweight document** that captures a significant architectural decision, the context in which it was made, the options considered, and the consequences of the chosen option. Often abbreviated as **ADR**.

### Key Characteristics
- One ADR per decision, kept close to the code or in a dedicated `docs/adr/` folder
- Explains not just *what* was decided but *why*, including rejected alternatives
- Provides a durable record for future maintainers and reviewers

### When to Use
- When choosing between technologies, patterns, or tradeoffs that will be hard to reverse
- When deliberately violating a standard principle, to document the rationale

### When NOT to Use
- For trivial decisions that are obvious to the whole team
- As a substitute for discussion — ADRs capture consensus, not replace it

### Also see
- [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md) · [Technical Debt](architecture-patterns.md#technical-debt)

---

## Anti-pattern

A **common response to a recurring problem** that is usually ineffective and risks being highly counterproductive. Anti-patterns look like solutions but create more problems than they solve.

### Key Characteristics
- Repeatedly observed in real systems
- Often arises from deadline pressure, habit, or misunderstanding a pattern
- Naming an anti-pattern helps teams recognize and avoid it

### When to Use
- In code reviews and architecture reviews to label recurring problematic solutions
- When teaching patterns by contrasting them with what *not* to do

### When NOT to Use
- As a vague insult for any code you dislike — label only well-documented, recurring problems
- To discourage pragmatic shortcuts that are explicitly temporary and tracked

### Also see
- [Golden Hammer](#golden-hammer) · [Architecture Principles Key Takeaways](../system-design-architecture/40-arch-key-takeaways.md)

---

## Service Provider Interface (SPI)

A **pluggable extension mechanism** where a platform defines a set of interfaces (the contract) and allows external modules to provide implementations that are discovered and loaded at runtime. SPIs enable platforms to remain pure and extensible while customer-specific or use-case-specific logic lives in isolated, decoupled modules.

### Key Characteristics
- The platform defines the *what* (interface/contract); extensions define the *how* (implementation)
- Implementations are discovered via service loader mechanisms (e.g., Java `ServiceLoader`, .NET dependency injection conventions)
- Clean API boundaries ensure that changes in extension modules do not ripple into the core platform
- Enables zero-copy processing by exposing lifecycle hook points within the core engine

### When to Use
- Platforms that need to support custom processing logic without forking the core codebase
- Enterprise products where different customers require different data transformation, security, or compliance rules
- When you need to upstream field-driven innovations as first-class platform features

### When NOT to Use
- Simple applications where the overhead of a plugin architecture outweighs its benefits
- When extensibility points are unlikely to ever vary across deployments
- Performance-critical hot paths where even a virtual dispatch overhead is unacceptable

### Also see
- [Strategy Pattern](#strategy-pattern)
- [Decorator Pattern](#decorator-pattern)
- [Loose Coupling](#loose-coupling)
- [Forward Deployed Engineer (FDE)](architecture-patterns.md#forward-deployed-engineer)
