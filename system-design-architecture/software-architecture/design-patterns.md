---
type: System Design
title: "Software Design Patterns — Key Takeaways"
description: "Architect-curated GoF and enterprise patterns — Creational, Structural, Behavioral, Enterprise, and Resilience — with problem→strategy→tradeoff structure."
generated: { by: process:okf-migrate, at: 2026-06-19T00:00:00Z }
---

# Software Design Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [The Architect's Secret: The Patterns That Solve 90% of Real-World Problems](../../articles/medium/The%20Architect%E2%80%99s%20Secret%20The%20Patterns%20That%20Solve%2090%25%20of%20Real-World%20Problems.md)
> **Taxonomy Reference**: §2.2 Software Design Patterns & Code Quality

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`dp-01`](#dp-01-shared-resource-multiple-instantiation) | Shared Resource Multiple Instantiation | Singleton |
| [`dp-02`](#dp-02-complex-object-creation-scattered-across-clients) | Complex Object Creation Scattered Across Clients | Factory Method |
| [`dp-03`](#dp-03-telescoping-constructors-for-complex-objects) | Telescoping Constructors for Complex Objects | Builder |
| [`dp-04`](#dp-04-integrating-incompatible-interfaces) | Integrating Incompatible Interfaces | Adapter |
| [`dp-05`](#dp-05-adding-cross-cutting-behaviors-without-subclassing) | Adding Cross-Cutting Behaviors Without Subclassing | Decorator |
| [`dp-06`](#dp-06-controlling-access-and-lazy-initialization) | Controlling Access and Lazy Initialization | Proxy |
| [`dp-07`](#dp-07-swappable-algorithms-at-runtime) | Swappable Algorithms at Runtime | Strategy |
| [`dp-08`](#dp-08-decoupling-producers-from-consumers) | Decoupling Producers from Consumers | Observer |
| [`dp-09`](#dp-09-encapsulating-requests-for-queuing-and-undo) | Encapsulating Requests for Queuing and Undo | Command |
| [`dp-10`](#dp-10-leaky-data-access-in-domain-logic) | Leaky Data Access in Domain Logic | Repository |
| [`dp-11`](#dp-11-distributed-transaction-across-microservices) | Distributed Transaction Across Microservices | Saga |
| [`dp-12`](#dp-12-choosing-the-right-pattern) | Choosing the Right Pattern | Decision Checklist & Anti-patterns |

---

## dp-01: Shared Resource Multiple Instantiation

| | |
|:---|:---|
| **Problem** | A shared resource (config, connection pool, cache manager) is instantiated multiple times, causing inconsistency and wasted resources. |
| **Root cause** | No enforcement of a single instantiation point; each caller creates its own instance. |

**Strategy**: Apply the **Singleton** pattern — private constructor, static volatile field, double-checked locking.

```java
public final class ConfigManager {
    private static volatile ConfigManager instance;
    public static ConfigManager getInstance() {
        if (instance == null) {
            synchronized (ConfigManager.class) {
                if (instance == null) instance = new ConfigManager();
            }
        }
        return instance;
    }
}
```

**Tradeoff**: Enforces a single source-of-truth, but introduces hidden global state that makes unit testing harder and increases tight coupling. Prefer framework-managed singletons (Spring `@Bean`, CDI) over hand-rolled ones.

**Cross-references**: [Architecture Patterns — Singleton](../../reference-dictionary/architecture-patterns.md#singleton)

---

## dp-02: Complex Object Creation Scattered Across Clients

| | |
|:---|:---|
| **Problem** | Creation logic for protocol-specific clients (HTTP/gRPC/Kafka) is duplicated across calling code, making substitution and testing difficult. |
| **Root cause** | Callers are coupled to concrete implementations via `new`. |

**Strategy**: Apply the **Factory Method** pattern — a static or interface method encapsulates object creation, returning an interface type.

```java
public class NotificationFactory {
    public static Notification create(String type) {
        switch (type) {
            case "email": return new EmailNotification();
            case "sms":   return new SMSNotification();
            default: throw new IllegalArgumentException("unknown: " + type);
        }
    }
}
```

**Tradeoff**: Decouples creation from usage and enables plugin-style extensibility, but adds an indirection layer. Avoid creating factories for trivial constructors — the overhead is not justified.

**Cross-references**: [Architecture Patterns — Factory Method](../../reference-dictionary/architecture-patterns.md#factory-method)

---

## dp-03: Telescoping Constructors for Complex Objects

| | |
|:---|:---|
| **Problem** | Objects with many optional fields lead to constructor explosions or invalid intermediate states when using setters. |
| **Root cause** | No structured way to assemble objects step-by-step while enforcing immutability. |

**Strategy**: Apply the **Builder** pattern — a nested `Builder` class accumulates fields and produces the final immutable object via `build()`.

```java
User u = new User.Builder().name("Alice").email("a@x").age(30).build();
```

**Tradeoff**: Produces clean, readable, safe construction and easy validation in `build()`. Can be boilerplate-heavy if not generated (Lombok `@Builder` mitigates this).

**Cross-references**: [Architecture Patterns — Builder](../../reference-dictionary/architecture-patterns.md#builder-pattern)

---

## dp-04: Integrating Incompatible Interfaces

| | |
|:---|:---|
| **Problem** | A legacy `CSVReader` or third-party SDK uses a different interface than the internal domain contract, requiring translation on every call site. |
| **Root cause** | External interface does not match the internally agreed abstraction. |

**Strategy**: Apply the **Adapter** pattern — a wrapper class implements the internal interface and delegates to the legacy object.

```java
class CSVReaderAdapter implements RowReader {
    private final LegacyCSVReader delegate;
    public Optional<Map<String,String>> read() {
        String[] row = delegate.readRow();
        return Optional.of(Map.of("col1", row[0]));
    }
}
```

**Tradeoff**: Encapsulates all legacy integration code in one place; keeps the new codebase clean and interface-driven. Adds an extra indirection layer — only justified when adapting truly incompatible interfaces.

**Cross-references**: [Architecture Patterns — Adapter](../../reference-dictionary/architecture-patterns.md#adapter-pattern)

---

## dp-05: Adding Cross-Cutting Behaviors Without Subclassing

| | |
|:---|:---|
| **Problem** | Logging, caching, metrics, and audit need to be applied to existing implementations without modifying their code or creating class explosion through inheritance. |
| **Root cause** | Subclassing couples behavior to a specific class; violates Single Responsibility Principle if mixed into the original. |

**Strategy**: Apply the **Decorator** pattern — wrap the original implementation with a class that adds behavior before/after delegating.

```java
class LoggingStore implements DataStore {
    private final DataStore delegate;
    public void save(String k, String v) {
        log.info("saving: {}", k);
        delegate.save(k, v);
    }
}
```

**Tradeoff**: Composable behaviors (logging, metrics, validation) that keep Single Responsibility intact. Deep decorator chains become hard to debug; trace the chain when diagnosing unexpected behavior.

**Cross-references**: [Architecture Patterns — Decorator](../../reference-dictionary/architecture-patterns.md#decorator-pattern)

---

## dp-06: Controlling Access and Lazy Initialization

| | |
|:---|:---|
| **Problem** | Loading a resource (disk image, remote stub) eagerly wastes memory/latency when it might not be needed, or access to it must be gated by security checks. |
| **Root cause** | Direct object references cannot intercept access or defer initialization. |

**Strategy**: Apply the **Proxy** pattern — a stand-in object creates the real object on first access (virtual proxy) or intercepts calls for permission checks (protection proxy).

```java
class ImageProxy implements Image {
    private RealImage real;
    public void display() {
        if (real == null) real = new RealImage(); // lazy load
        real.display();
    }
}
```

**Tradeoff**: Transparent lazy initialization and access control. Can obscure performance costs — a proxy that triggers a network call on `display()` surprises callers who expect a cheap local operation.

**Cross-references**: [Architecture Patterns — Proxy](../../reference-dictionary/architecture-patterns.md#proxy-pattern)

---

## dp-07: Swappable Algorithms at Runtime

| | |
|:---|:---|
| **Problem** | Business rules (discount calculation, payment routing, sorting) vary by context and must be swapped without modifying calling code. |
| **Root cause** | Hardcoded `if/else` chains couple the algorithm to the client, violating Open/Closed Principle. |

**Strategy**: Apply the **Strategy** pattern — define a common interface; inject the desired algorithm at construction or call time.

```java
class Checkout {
    private final DiscountStrategy strategy;
    double total(double price) { return strategy.apply(price); }
}
// Inject: new Checkout(new SeasonalDiscount())
```

**Tradeoff**: Open/Closed compliance; algorithm variants are independently testable. Unnecessary complexity when only one strategy will ever exist — prefer the inline implementation.

**Cross-references**: [Architecture Patterns — Strategy](../../reference-dictionary/architecture-patterns.md#strategy-pattern)

---

## dp-08: Decoupling Producers from Consumers

| | |
|:---|:---|
| **Problem** | A domain event (user registered, payment processed) must trigger multiple downstream actions, but tightly coupling the producer to each consumer breaks the Single Responsibility Principle and makes adding listeners expensive. |
| **Root cause** | Direct method calls couple the event source to its handlers. |

**Strategy**: Apply the **Observer** pattern — an event bus holds a list of listeners; the publisher calls `publish(event)` without knowing consumers.

```java
class EventBus {
    private final List<Listener> listeners = new CopyOnWriteArrayList<>();
    void register(Listener l) { listeners.add(l); }
    void publish(Event e)     { listeners.forEach(l -> l.onEvent(e)); }
}
```

**Tradeoff**: Loose coupling; easy to extend with new listeners without changing the publisher. Memory leaks occur if listeners are never removed. Unpredictable ordering and "control-flow spaghetti" can emerge in large systems — prefer an explicit message broker for cross-service events.

**Cross-references**: [Architecture Patterns — Observer](../../reference-dictionary/architecture-patterns.md#observer-pattern) · [Messaging Dictionary](../../reference-dictionary/messaging.md)

---

## dp-09: Encapsulating Requests for Queuing and Undo

| | |
|:---|:---|
| **Problem** | Actions need to be queued, retried, audited, or undone. A raw method call cannot be stored, serialized, or replayed. |
| **Root cause** | Method invocations are ephemeral — they carry no state that can be persisted or deferred. |

**Strategy**: Apply the **Command** pattern — encapsulate each request as an object; submit to an executor or queue for deferred execution.

```java
class SaveUserCommand implements Command {
    public void execute() { repo.save(user); }
}
ExecutorService es = Executors.newSingleThreadExecutor();
es.submit(() -> new SaveUserCommand(repo, user).execute());
```

**Tradeoff**: Enables job scheduling, message-based work queues, GUI undo. Overhead of object creation is unjustified for trivial, synchronous, non-replayable operations.

**Cross-references**: [Architecture Patterns — Command](../../reference-dictionary/architecture-patterns.md#command-pattern)

---

## dp-10: Leaky Data Access in Domain Logic

| | |
|:---|:---|
| **Problem** | Domain objects directly query JPA/JDBC/NoSQL — persistence details leak into business logic, making it untestable and tightly coupled to one data store. |
| **Root cause** | No abstraction boundary between the domain model and its persistence mechanism. |

**Strategy**: Apply the **Repository** pattern — an interface exposes domain-specific query methods; persistence technology is hidden behind the interface.

```java
public interface UserRepository {
    Optional<User> findById(String id);
    void save(User u);
}
```

**Tradeoff**: Single place to change persistence strategy; trivially mockable in tests. Anemic repositories that only mirror CRUD and leaky abstractions that expose DB internals (e.g., `EntityManager`) negate the benefit.

**Cross-references**: [Architecture Patterns — Repository](../../reference-dictionary/architecture-patterns.md#repository-pattern)

---

## dp-11: Distributed Transaction Across Microservices

| | |
|:---|:---|
| **Problem** | An order flow spanning Order → Payment → Inventory → Shipping services requires atomicity, but two-phase commit (2PC) across microservices destroys availability and is impractical. |
| **Root cause** | Distributed ACID transactions require all participants to block until the coordinator commits — unacceptable under partial failure. |

**Strategy**: Apply the **Saga** pattern — decompose the transaction into a sequence of local transactions, each publishing an event; if a step fails, execute compensating transactions to undo earlier steps.

**Tradeoff**: Avoids 2PC; better availability and resilience under partial failure. Compensating transactions are sometimes hard to design (some actions are not reversible). Requires careful failure handling and observability into saga state.

**Cross-references**: [Data Concurrency — Saga Pattern](../../reference-dictionary/data-concurrency.md#saga-pattern) · [CQRS for Fintech](cqrs-fintech/cqrs-fintech.md)

---

## dp-12: Choosing the Right Pattern

| | |
|:---|:---|
| **Problem** | Teams apply patterns blindly (Golden Hammer), introduce CQRS/Saga prematurely, or build over-abstracted codebases that are impossible to navigate. |
| **Root cause** | Pattern selection driven by familiarity or fashion rather than the actual problem. |

**Strategy**: Apply the decision checklist:
1. **Define the exact pain** — resist pattern-fitting until the problem is specific.
2. **Verify the pattern solves that pain directly** — don't force-fit.
3. **Evaluate side effects** — testability, operability, complexity.
4. **Start simple; refactor into the pattern when needed** — YAGNI applies.
5. **Document the trade-offs** for future maintainers.

**Anti-patterns to avoid**:
- **Golden Hammer** — applying a favourite pattern everywhere.
- **Over-abstraction** — too many small interfaces and factories that make the codebase hard to navigate.
- **Premature optimization** — implementing CQRS/Saga for a small monolith before a real need arises.
- **Silent failures** — using Circuit Breaker without observability; you won't know when it trips.

**Tradeoff**: Principled pattern selection yields maintainable, testable, scalable systems. Undisciplined selection introduces complexity and hidden costs that outlast the original problem.

**Cross-references**: [Resilience Patterns](resilience/resilience-patterns.md) · [Pragmatic System Design](system-design-interview/pragmatic-takeaways.md) · [Architecture Patterns Dictionary](../../reference-dictionary/architecture-patterns.md)
