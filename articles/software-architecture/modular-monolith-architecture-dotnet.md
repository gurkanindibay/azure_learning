---
type: Article
title: "Modular Monolith Architecture in C#: The Pragmatic Path to Scalable .NET Applications"
description: "Why a single deployment unit with strong internal module boundaries is often a better default than microservices for .NET applications."
source: "https://medium.com/@kevalbalar1995/modular-monolith-architecture-in-c-the-pragmatic-path-to-scalable-net-applications-a3e8726d347e"
author:
  - "[[Keval]]"
published: 2026-07-03
generated: { by: process:okf-migrate, at: 2026-07-04T00:00:00Z }
tags:
  - "clippings"
---
# I Stopped Building Microservices — Here’s Why Modular Monolith Changed Everything

Let me tell you about the worst project of my career.

It was 2021. We were building a SaaS platform for a fast-growing logistics company. The CTO had read about Netflix. The product owner had watched a YouTube video about Amazon. Everyone wanted microservices.

We delivered fourteen microservices. Each had its own database. Each had its own deployment pipeline. Each had its own monitoring dashboard. We were so proud.

Six months later, we were drowning.

A simple feature that should have taken two days took two weeks. Debugging required tracing requests across seven services. A minor database migration brought down three services simultaneously. We spent more time managing infrastructure than shipping code.

The team was miserable. The product was behind schedule. The CTO kept asking why things were so slow.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*NfiiJexki8B4pEtVSYYGqA.png)

## Why This Matters

### The Architecture Trap We All Fall Into

Here’s what I’ve learned after fifteen years of building software: we architects have a bias toward complexity.

We think we’re going to build the next Netflix. We think our system will need to handle millions of requests per second from day one. So we start with microservices. We Kubernetes everything. We distribute before we need to.

The reality is much more mundane. Most of us are building business applications. E-commerce platforms. Internal tools. B2B SaaS products. These systems need to be maintainable, testable, and reliable. They don’t need Google-scale infrastructure.

**Traditional monoliths** start simple, then descend into chaos. You’ve seen it. The codebase where changing the customer module breaks the inventory system. Where business logic lives in controllers because nobody knows where else to put it. Where one team’s deployment blocks another team’s deployment.

**Microservices** promised salvation. Independent teams! Technology diversity! Selective scaling! But the reality hit hard. Each service requires its own CI pipeline, deployment, monitoring, security review, and on-call rotation. Network calls add latency and failure modes. Distributed transactions become debugging nightmares. Your team spends more time managing complexity than shipping features.

The industry has started admitting what many of us have known for years: most organizations aren’t ready for microservices. A 2024 industry survey showed that over 40% of companies regret at least some of their microservices decisions.

The problem isn’t microservices. The problem is starting with them before you understand your domain boundaries or have the operational maturity to support them.

## The Third Way

A modular monolith is a single deployment unit organized internally into clear modules with strong boundaries. Think of it like a well-organized apartment building versus a sprawling suburban development.

In a **traditional monolith**, everything is tangled together. All the wiring runs everywhere. You can’t renovate one apartment without affecting the whole building.

In **microservices**, each apartment is a separate building with its own plumbing, electricity, and road access. You can renovate independently, but coordinating changes across buildings is complex.

In a **modular monolith**, you have one building, but each apartment has clearly defined walls, separate entrances, and explicit interfaces. You can remodel one apartment without affecting the others, as long as you respect the walls and don’t knock them down.

The key insight: **deployment boundaries are not the same as logical boundaries**. You can have clean, decoupled code without deploying thirty different services.

## Understanding the Fundamentals

### What Makes a Module a Module?

Before we dive into implementation, let’s get clear on what a module actually is in this context.

A module is a self-contained unit of business functionality. It encapsulates everything needed for that business capability — entities, business logic, data access, and API endpoints. In an e-commerce system, modules might include:

- Catalog: Products, categories, pricing, inventory
- Orders: Shopping cart, checkout, order tracking
- Customers: Registration, profiles, authentication
- Payments: Payment methods, transactions, refunds

Each module should be independently understandable. A developer should be able to understand how the Orders module works without understanding how Catalog works, just as you can understand the checkout process at a store without knowing how they stock the shelves.

## Domain-Driven Design and Bounded Contexts

Domain-Driven Design (DDD) provides the vocabulary for this. The concept of **bounded contexts** is crucial here: within its own boundary, a term like “Customer” has a specific meaning. The Orders module might care about the customer’s shipping address and payment history. The Marketing module might care about the customer’s preferences and engagement history. Same customer, different contexts.

This is okay. In fact, it’s essential. When we try to create one universal “Customer” model that works for everyone, we end up with bloated, coupled code. By letting each module define its own version of a customer, we keep things clean and focused.

## The Shared Kernel

Some things need to be shared across modules. Authentication. Logging. Common data types. Base classes. This is the **shared kernel —** infrastructure that multiple modules safely depend on.

The key word is “safely.” The shared kernel should contain only things that are stable and truly cross-cutting. It should never contain business logic. If you find yourself putting domain concepts in the shared kernel, you’ve likely identified a bounded context incorrectly.

## How It Works

### The Project Structure That Changed Everything

I’ve tried many ways to structure modular monoliths, and this pattern has worked best for my teams:

Solution.ModularMonolith/  
├── src/  
│ ├── Host/  
│ │ └── Api/ # Entry point and bootstrapping  
│ ├── Modules/  
│ │ ├── Catalog/  
│ │ │ ├── Catalog.Api/ # Controllers and API concerns  
│ │ │ ├── Catalog.Core/ # Business logic and entities  
│ │ │ ├── Catalog.Infrastructure/ # Data access and external services  
│ │ │ └── Catalog.Contracts/ # Public interfaces and DTOs  
│ │ └── Orders/  
│ │ ├── Orders.Api/  
│ │ ├── Orders.Core/  
│ │ ├── Orders.Infrastructure/  
│ │ └── Orders.Contracts/  
│ └── Shared/  
│ ├── Shared.Kernel/ # Common utilities and base classes  
│ ├── Shared.Infrastructure/ # Cross-cutting infrastructure  
│ └── Shared.Contracts/ # Shared data contracts  
└── tests/  
├── Modules/  
│ ├── Catalog.UnitTests/  
│ └── Orders.UnitTests/  
└── IntegrationTests/

This structure enforces module boundaries at the compilation level. The Catalog module cannot reference the Orders module’s internal implementation — it can only reference its contracts.

## Module Communication Patterns

Modules need to talk to each other. In a modular monolith, this can happen in several ways:

Direct Interface Calls (Synchronous)

The simplest approach. One module calls another through a well-defined interface. The Orders module asks the Catalog module to validate stock levels. The call is just a method call — no network, no serialization, no latency.

The beauty of this in a modular monolith is that you get the performance of in-process communication with the decoupling of an interface. You can mock the Catalog module in tests. You can replace the implementation without changing the Orders module. But you can also inspect the call stack and debug like a normal application.

Event-Driven Communication (Asynchronous)

For true decoupling, use an in-memory event bus. When an order is confirmed, the Orders module publishes an `OrderConfirmed` event. The Inventory module handles this event and reserves the items. The Orders module doesn't need to know about Inventory—it just publishes events.

This is the same pattern used in microservices, but without the network overhead. The event bus is in-memory, so the events are delivered almost instantly. You get the decoupling benefits of asynchronous communication without the operational complexity.

## Real-World Examples

### Shopify: Processing 30TB Per Minute

Shopify processes massive transaction volumes using modular monolith principles. At the scale they operate — over a million requests per minute — they’ve proven that modular monoliths can handle enterprise-level load.

Their key insight is worth repeating: even at Shopify’s scale, the operational simplicity of a single deployment unit outweighed the benefits of distributed services. They maintain strong internal boundaries while keeping deployment simple. They’ve demonstrated that you can run a massive e-commerce platform on a modular monolith, and then selectively extract services only when scaling demands it.

### Amazon’s “Microservices Back” Movement

This one is telling. Amazon famously pioneered microservices. They literally wrote the book on it. And yet, in recent years, they’ve transitioned certain services back to monolithic architectures.

Why? Because the operational costs of distribution sometimes exceed the benefits. When a service has simple scaling requirements and clear internal boundaries, the overhead of running it as a separate microservice isn’t justified.

If Amazon, of all companies, is pulling back from microservices in some cases, maybe we should think twice before adopting them universally.

## Architecture and Implementation

### Step 1: Identify Your Bounded Contexts

Start by mapping your business domain. Don’t start with code. Start with whiteboards and sticky notes. Identify the major business capabilities in your system.

For an e-commerce platform:

- Customer Management (registration, profiles, preferences)
- Catalog Management (products, categories, pricing)
- Order Processing (cart, checkout, fulfillment)
- Payment Processing (payment methods, transactions)
- Inventory Management (stock levels, warehouse operations)

These bounded contexts should feel natural to your business stakeholders. The test of a good bounded context is that a business person can understand it without understanding code.

### Step 2: Design Module Boundaries

For each bounded context, define three things:

1. **What belongs inside the module** (entities, business logic, data access)
2. **What the module exposes** (public interfaces, DTOs, events)
3. **What the module depends on** (other modules, shared infrastructure)

The key insight here: define the dependencies before writing code. This prevents the natural tendency to make everything public and accessible. If you define what others can use ahead of time, you think more carefully about your module’s design.

### Step 3: Create the Project Structure

Set up the physical project structure from earlier. Use.NET 8 with Central Package Management. This ensures consistent dependencies across modules and prevents version conflicts.

### Step 4: Define Module Contracts

The Contracts project is your module’s public API. It should contain only DTOs, interface definitions, and event types. No implementation details. No database entities. No infrastructure references.

Here’s a simple example:

```csharp
// Catalog.Contracts/ICatalogService.cs
public interface ICatalogService
{
    Task<ProductDto> GetProductAsync(int productId);
    Task<bool> UpdateStockAsync(int productId, int quantity);
}

// Catalog.Contracts/ProductDto.cs
public record ProductDto(
    int Id,
    string Name,
    decimal Price,
    int StockQuantity
);
```

That’s it. Other modules don’t need to know about your repositories, your database, or your business logic. They just need to know what you can do for them.

### Step 5: Implement Core Business Logic

The Core project contains your business logic, entities, and domain services — all private to the module. Other modules can’t access these directly, and that’s the point.

The entities here are your domain objects. They contain business logic and enforce business rules. They raise domain events when important things happen. They’re completely unaware of infrastructure.

### Step 6: Implement Infrastructure

The Infrastructure project handles data access, external service integrations, and caching. It implements the interfaces defined in the Core project.

The important thing here: the Core project doesn’t reference Infrastructure. The Infrastructure project references Core. This keeps your business logic free of infrastructure concerns and makes testing easier.

### Step 7: Wire Up the API

The Api project contains controllers that expose module functionality via HTTP endpoints. These controllers orchestrate calls to the Core layer and handle HTTP concerns — serialization, validation, status codes.

### Step 8: Configure Dependency Injection

In your host’s Program.cs, register each module:

```csharp
builder.Services
    .AddCatalogModule()
    .AddOrdersModule()
    .AddInventoryModule();
```

Each module registers its own services, its own DbContext, and its own event handlers. This keeps the host clean and makes it clear what modules your application includes.

### Step 9: Enforce Module Boundaries

This is where the rubber meets the road. Use architecture tests to ensure developers don’t violate module boundaries:

```csharp
[Test]
public void CatalogModule_Should_NotReference_OrdersModule_Internals()
{
    // This test fails if someone accidentally references Orders.Core from Catalog.Core
}
```

Run these tests in CI. If a developer tries to bypass the architecture, the build fails. This prevents the gradual erosion of boundaries that kills most modular monolith implementations.

## Best Practices

### 1\. Start with Modular Monolith as Default

For new projects, default to a modular monolith. As Martin Fowler observed, all successful microservice architectures he’s seen emerged from monolithic systems — not the other way around. Starting with a modular monolith gives you time to understand your domain before distributing it.

### 2\. Define Bounded Contexts Carefully

Use Domain-Driven Design to identify bounded contexts before writing code. These boundaries should reflect business capabilities, not technical concerns. The wrong boundaries lead to constant cross-module communication, which defeats the purpose.

### 3\. Enforce Module Boundaries Religiously

Use separate project assemblies for each module. Implement architecture tests that fail the build if boundaries are violated. Make it painful to bypass the architecture. This is the only way to prevent the gradual erosion of boundaries.

### 4\. Keep Contracts Minimal and Stable

Module contracts should be minimal and stable. When you change a contract, all dependent modules may need updates. This is the same as microservices — contract stability is crucial for independent evolution.

### 5\. Use Explicit Dependencies

Each module should explicitly declare its dependencies on other modules via Contracts projects. No implicit dependencies. No depending on implementation details. Make the dependencies visible and enforced.

### 6\. Consider Event-Driven Communication

Use events for cross-module communication to reduce coupling. An in-memory event bus works well within a modular monolith. You get the decoupling benefits of asynchronous communication without the operational complexity.

### 7\. Implement Shared Infrastructure Carefully

Cross-cutting concerns like authentication, logging, caching, and configuration should live in shared infrastructure projects. Keep business logic separate. The shared kernel should be small and stable.

## Common Mistakes

### 1\. Creating “Modules” by Technical Layer

Organizing modules by technical layer (e.g., “DataAccess” module, “Services” module) defeats the purpose. Modules should be organized by business capability. If you can’t explain to a business person what your module does, your boundaries are wrong.

### 2\. Allowing Direct Database Access Across Modules

Modules should not directly access each other’s database tables. This creates hidden coupling. If the Orders module queries the Products table directly, you’ve defeated the purpose of module boundaries.

### 3\. Sharing Domain Entities Across Modules

Each module should own its domain entities. Sharing entities across modules creates tight coupling. The Orders module’s concept of a product should be separate from the Catalog module’s concept.

### 4\. Starting with Microservices Too Early

Starting with microservices before you understand your domain boundaries or have the operational maturity to support them leads to failure. Start with a modular monolith. Extract services only when scale justifies the complexity.

### 5\. Ignoring Database Isolation

Even in a modular monolith, each module should have clear database ownership. Use separate schemas or separate databases within the same server. This maintains the option of extracting services later.

## Performance Considerations

### In-Process Communication

One of the biggest advantages of modular monoliths is in-process communication. Cross-module calls happen as method calls, not network requests. This can reduce request processing time by hundreds of milliseconds compared to microservices.

### Database Performance

Modules can share database connections and leverage transaction boundaries for optimal performance. Query optimization across module boundaries is possible when needed. You’re not limited by network latency.

### Caching

Data can be cached at the application level and shared across modules. Cache invalidation strategies are simpler without distributed cache consistency concerns. In-memory caches work well within a modular monolith.

### Scaling Considerations

A modular monolith scales vertically more efficiently than horizontal scaling. You can scale your modular monolith to handle significant load before needing to extract services. Most applications never need to go further.

## Conclusion

The architecture wars are finally over. The modular monolith has emerged as the pragmatic middle ground — offering the clean boundaries and team autonomy of microservices without the crippling operational complexity.

For most teams and most projects, this is the sweet spot. It gives you the discipline to build maintainable, testable systems while keeping deployment simple. It lets you evolve to distributed services when — and only when — the scale justifies the complexity.

Your next project deserves a modular monolith.

Start with strong boundaries from day one. Use Domain-Driven Design to identify your bounded contexts. Structure your.NET 8 solution with clear module separation. Enforce boundaries with architecture tests. Then, when your system is running and your team is growing, you can extract modules selectively — based on real operational needs, not on hype.

The pattern is proven. The tools are mature. The choice is clear.

Build better systems. Start simpler. Evolve smarter.