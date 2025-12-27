# CQRS Pattern (Command Query Responsibility Segregation)

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Architecture](#architecture)
- [Implementation Approaches](#implementation-approaches)
- [Code Examples](#code-examples)
- [When to Use CQRS](#when-to-use-cqrs)
- [CQRS with Event Sourcing](#cqrs-with-event-sourcing)
- [Advantages and Disadvantages](#advantages-and-disadvantages)
- [Best Practices](#best-practices)

---

## Overview

**CQRS (Command Query Responsibility Segregation)** is an architectural pattern that separates read and write operations into different models. It was introduced by Greg Young as an evolution of CQS (Command Query Separation) principle by Bertrand Meyer.

### CQS vs CQRS

| Aspect | CQS | CQRS |
|--------|-----|------|
| Scope | Method level | Architecture level |
| Definition | Methods either change state OR return data | Separate models for reads and writes |
| Complexity | Simple principle | Architectural pattern |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CQS PRINCIPLE (Method Level)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Command: void AddItem(item)     ──► Changes state, returns nothing        │
│  Query:   Item GetItem(id)       ──► Returns data, no side effects         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Concepts

### Commands

Commands represent the **intent to change** the system state. They are imperative and named with verbs.

```
┌─────────────────────────────────────────┐
│              COMMANDS                   │
├─────────────────────────────────────────┤
│  • CreateOrder                          │
│  • UpdateCustomerAddress                │
│  • CancelReservation                    │
│  • AddItemToCart                        │
│  • ProcessPayment                       │
├─────────────────────────────────────────┤
│  Characteristics:                       │
│  ✓ Change state                         │
│  ✓ Return void or acknowledgment        │
│  ✓ Can be rejected/validated            │
│  ✓ Usually processed one at a time      │
└─────────────────────────────────────────┘
```

### Queries

Queries represent **requests for data**. They are read-only and should have no side effects.

```
┌─────────────────────────────────────────┐
│               QUERIES                   │
├─────────────────────────────────────────┤
│  • GetOrderById                         │
│  • GetCustomerOrders                    │
│  • SearchProducts                       │
│  • GetDashboardSummary                  │
│  • GetInventoryReport                   │
├─────────────────────────────────────────┤
│  Characteristics:                       │
│  ✓ Read-only                            │
│  ✓ Return data (DTOs/ViewModels)        │
│  ✓ No side effects                      │
│  ✓ Can be cached                        │
│  ✓ Can be executed in parallel          │
└─────────────────────────────────────────┘
```

---

## Architecture

### Basic CQRS Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BASIC CQRS ARCHITECTURE                             │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌───────────────┐
                              │    Client     │
                              └───────┬───────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
           ┌───────────────┐                   ┌───────────────┐
           │   Commands    │                   │    Queries    │
           │  (Write API)  │                   │  (Read API)   │
           └───────┬───────┘                   └───────┬───────┘
                   │                                   │
                   ▼                                   ▼
           ┌───────────────┐                   ┌───────────────┐
           │   Command     │                   │    Query      │
           │   Handlers    │                   │   Handlers    │
           └───────┬───────┘                   └───────┬───────┘
                   │                                   │
                   ▼                                   ▼
           ┌───────────────┐                   ┌───────────────┐
           │  Write Model  │                   │  Read Model   │
           │   (Domain)    │                   │ (Projections) │
           └───────┬───────┘                   └───────┬───────┘
                   │                                   │
                   ▼                                   ▼
           ┌───────────────┐                   ┌───────────────┐
           │  Write Store  │ ──── Sync ────►  │  Read Store   │
           │ (Normalized)  │                   │(Denormalized) │
           └───────────────┘                   └───────────────┘
```

### CQRS with Separate Databases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CQRS WITH SEPARATE DATABASES                             │
└─────────────────────────────────────────────────────────────────────────────┘

    Write Side                                          Read Side
    ──────────                                          ─────────

┌─────────────────┐                              ┌─────────────────┐
│  Command API    │                              │   Query API     │
└────────┬────────┘                              └────────┬────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐                              ┌─────────────────┐
│ Command Handler │                              │  Query Handler  │
│                 │                              │                 │
│ • Validation    │                              │ • Simple reads  │
│ • Business logic│                              │ • No logic      │
│ • Domain events │                              │ • Direct queries│
└────────┬────────┘                              └────────┬────────┘
         │                                                │
         ▼                                                ▼
┌─────────────────┐                              ┌─────────────────┐
│   Write DB      │                              │    Read DB      │
│   (SQL Server)  │                              │   (MongoDB)     │
│   Normalized    │                              │  Denormalized   │
└────────┬────────┘                              └─────────────────┘
         │                                                ▲
         │        ┌─────────────────────────┐            │
         └───────►│   Synchronization       │────────────┘
                  │   (Events/Messaging)    │
                  └─────────────────────────┘
```

### Synchronization Strategies

| Strategy | Description | Consistency |
|----------|-------------|-------------|
| **Synchronous** | Update read model in same transaction | Strong |
| **Asynchronous** | Update via events/messaging | Eventual |
| **Hybrid** | Critical reads sync, others async | Mixed |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SYNCHRONIZATION APPROACHES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. SAME DATABASE, DIFFERENT TABLES                                         │
│     ┌────────────────────────────────────────┐                              │
│     │           Single Database              │                              │
│     │  ┌──────────────┐  ┌──────────────┐   │                              │
│     │  │ Write Tables │  │ Read Views   │   │                              │
│     │  │ (Normalized) │  │(Denormalized)│   │                              │
│     │  └──────────────┘  └──────────────┘   │                              │
│     └────────────────────────────────────────┘                              │
│     ✅ Simple  ✅ Strong consistency  ❌ Same scaling                        │
│                                                                             │
│  2. SEPARATE DATABASES (Event-Driven)                                       │
│     ┌──────────────┐      Events      ┌──────────────┐                     │
│     │   Write DB   │ ────────────────►│   Read DB    │                     │
│     │   (SQL)      │                  │  (NoSQL)     │                     │
│     └──────────────┘                  └──────────────┘                     │
│     ✅ Independent scaling  ✅ Optimized stores  ❌ Eventual consistency    │
│                                                                             │
│  3. CHANGE DATA CAPTURE (CDC)                                               │
│     ┌──────────────┐      CDC         ┌──────────────┐                     │
│     │   Write DB   │ ────────────────►│   Read DB    │                     │
│     │              │   (Debezium)     │              │                     │
│     └──────────────┘                  └──────────────┘                     │
│     ✅ No code changes  ✅ Reliable  ❌ Infrastructure complexity           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Approaches

### Level 1: Single Model with Separate Interfaces

Simplest form - same database, different access patterns.

```
┌─────────────────────────────────────────────────────────────────┐
│                      LEVEL 1: BASIC                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │ ICommandService │         │  IQueryService  │               │
│  └────────┬────────┘         └────────┬────────┘               │
│           │                           │                         │
│           └───────────┬───────────────┘                         │
│                       ▼                                         │
│              ┌─────────────────┐                                │
│              │  Single Model   │                                │
│              │  Single Database│                                │
│              └─────────────────┘                                │
│                                                                 │
│  Benefits: Simple, easy to implement                            │
│  Use when: Starting out, simple domains                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Level 2: Separate Read/Write Models

Different models, same or different databases.

```
┌─────────────────────────────────────────────────────────────────┐
│                     LEVEL 2: SEPARATE MODELS                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Write Model    │         │   Read Model    │               │
│  │  (Rich Domain)  │         │   (DTOs/Views)  │               │
│  └────────┬────────┘         └────────┬────────┘               │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │   Write Store   │ ──────► │   Read Store    │               │
│  └─────────────────┘  Sync   └─────────────────┘               │
│                                                                 │
│  Benefits: Optimized for each concern                           │
│  Use when: Different read/write patterns                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Level 3: Event Sourcing + CQRS

Full event-driven with event store.

```
┌─────────────────────────────────────────────────────────────────┐
│                  LEVEL 3: EVENT SOURCING + CQRS                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Commands ──► Aggregate ──► Events ──► Event Store              │
│                                              │                  │
│                                              ▼                  │
│                                    ┌─────────────────┐          │
│                                    │   Projections   │          │
│                                    └────────┬────────┘          │
│                                             │                   │
│                              ┌──────────────┼──────────────┐    │
│                              ▼              ▼              ▼    │
│                        ┌─────────┐    ┌─────────┐    ┌─────────┐│
│                        │ Read DB │    │ Search  │    │ Cache   ││
│                        │  (SQL)  │    │(Elastic)│    │ (Redis) ││
│                        └─────────┘    └─────────┘    └─────────┘│
│                                                                 │
│  Benefits: Complete audit trail, multiple projections           │
│  Use when: Complex domains, audit requirements                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Examples

### Command and Query Interfaces

```csharp
// Commands - Intent to change state
public interface ICommand { }

public record CreateOrderCommand(
    Guid CustomerId,
    List<OrderItem> Items,
    Address ShippingAddress
) : ICommand;

public record CancelOrderCommand(Guid OrderId, string Reason) : ICommand;

// Queries - Request for data
public interface IQuery<TResult> { }

public record GetOrderByIdQuery(Guid OrderId) : IQuery<OrderDto>;

public record GetCustomerOrdersQuery(
    Guid CustomerId,
    int Page,
    int PageSize
) : IQuery<PagedResult<OrderSummaryDto>>;
```

### Command Handler

```csharp
public interface ICommandHandler<TCommand> where TCommand : ICommand
{
    Task HandleAsync(TCommand command, CancellationToken ct = default);
}

public class CreateOrderCommandHandler : ICommandHandler<CreateOrderCommand>
{
    private readonly IOrderRepository _orderRepository;
    private readonly IEventPublisher _eventPublisher;

    public CreateOrderCommandHandler(
        IOrderRepository orderRepository,
        IEventPublisher eventPublisher)
    {
        _orderRepository = orderRepository;
        _eventPublisher = eventPublisher;
    }

    public async Task HandleAsync(CreateOrderCommand command, CancellationToken ct)
    {
        // Validation
        if (!command.Items.Any())
            throw new ValidationException("Order must have at least one item");

        // Create domain entity
        var order = Order.Create(
            command.CustomerId,
            command.Items,
            command.ShippingAddress
        );

        // Persist
        await _orderRepository.AddAsync(order, ct);

        // Publish domain events
        await _eventPublisher.PublishAsync(new OrderCreatedEvent(
            order.Id,
            order.CustomerId,
            order.TotalAmount,
            order.CreatedAt
        ), ct);
    }
}
```

### Query Handler

```csharp
public interface IQueryHandler<TQuery, TResult> where TQuery : IQuery<TResult>
{
    Task<TResult> HandleAsync(TQuery query, CancellationToken ct = default);
}

public class GetOrderByIdQueryHandler : IQueryHandler<GetOrderByIdQuery, OrderDto>
{
    private readonly IReadDbContext _readDb;

    public GetOrderByIdQueryHandler(IReadDbContext readDb)
    {
        _readDb = readDb;
    }

    public async Task<OrderDto> HandleAsync(GetOrderByIdQuery query, CancellationToken ct)
    {
        // Direct read from optimized read store
        var order = await _readDb.Orders
            .AsNoTracking()
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == query.OrderId, ct);

        return order ?? throw new NotFoundException($"Order {query.OrderId} not found");
    }
}
```

### Read Model Projection (Event Handler)

```csharp
public class OrderProjection : 
    IEventHandler<OrderCreatedEvent>,
    IEventHandler<OrderItemAddedEvent>,
    IEventHandler<OrderCancelledEvent>
{
    private readonly IReadDbContext _readDb;

    public async Task HandleAsync(OrderCreatedEvent @event, CancellationToken ct)
    {
        var orderReadModel = new OrderReadModel
        {
            Id = @event.OrderId,
            CustomerId = @event.CustomerId,
            TotalAmount = @event.TotalAmount,
            Status = "Created",
            CreatedAt = @event.CreatedAt
        };

        _readDb.Orders.Add(orderReadModel);
        await _readDb.SaveChangesAsync(ct);
    }

    public async Task HandleAsync(OrderCancelledEvent @event, CancellationToken ct)
    {
        var order = await _readDb.Orders.FindAsync(@event.OrderId);
        order.Status = "Cancelled";
        order.CancelledAt = @event.CancelledAt;
        order.CancellationReason = @event.Reason;
        
        await _readDb.SaveChangesAsync(ct);
    }
}
```

### Mediator Pattern Integration

```csharp
// Using MediatR library
public class OrdersController : ControllerBase
{
    private readonly IMediator _mediator;

    public OrdersController(IMediator mediator) => _mediator = mediator;

    [HttpPost]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderCommand command)
    {
        await _mediator.Send(command);
        return Accepted();
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<OrderDto>> GetOrder(Guid id)
    {
        var order = await _mediator.Send(new GetOrderByIdQuery(id));
        return Ok(order);
    }
}
```

---

## When to Use CQRS

### Good Candidates

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WHEN TO USE CQRS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ GOOD FIT                                                                │
│                                                                             │
│  • Read/write ratio is highly skewed (many reads, few writes)              │
│  • Read and write models have different shapes                             │
│  • Complex domain with rich business logic                                  │
│  • Need to scale reads and writes independently                            │
│  • Multiple views/projections of the same data                             │
│  • Event-driven architecture already in place                              │
│  • Collaborative domains with many concurrent users                        │
│  • Performance optimization needed for queries                             │
│                                                                             │
│  ❌ NOT A GOOD FIT                                                          │
│                                                                             │
│  • Simple CRUD applications                                                 │
│  • Small teams or simple domains                                            │
│  • Strong consistency is critical everywhere                                │
│  • Read and write patterns are similar                                      │
│  • Limited development resources                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Domain Examples

| Domain | Why CQRS Works |
|--------|----------------|
| E-commerce | Product catalog (read-heavy), Order processing (write-heavy) |
| Banking | Account queries (optimized views), Transactions (audit trail) |
| Social Media | Feed generation (complex projections), Posts (simple writes) |
| Reporting | Dashboards (pre-computed), Data entry (normalized) |

---

## CQRS with Event Sourcing

CQRS is often combined with Event Sourcing for a powerful architecture.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CQRS + EVENT SOURCING                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    Command                   Event Store                   Projections
    ───────                   ───────────                   ───────────

┌────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  Command   │           │    Events       │           │   Read Model    │
│            │           │                 │           │                 │
│CreateOrder │──────────►│ OrderCreated    │──────────►│ Orders Table    │
│            │  Append   │ ItemAdded       │  Project  │                 │
└────────────┘           │ ItemAdded       │           └─────────────────┘
                         │ OrderShipped    │                    
                         └─────────────────┘           ┌─────────────────┐
                                   │                   │ Customer Orders │
                                   │──────────────────►│    Summary      │
                                   │         Project   └─────────────────┘
                                   │
                                   │                   ┌─────────────────┐
                                   └──────────────────►│   Analytics     │
                                             Project   │    Cube         │
                                                       └─────────────────┘
```

### Benefits of Combining

| Benefit | Description |
|---------|-------------|
| **Multiple Projections** | Create different read models from same events |
| **Temporal Queries** | Query state at any point in time |
| **Event Replay** | Rebuild read models by replaying events |
| **Audit Trail** | Complete history of all changes |
| **Debugging** | Understand exactly what happened |

---

## Advantages and Disadvantages

### Advantages

| Advantage | Description |
|-----------|-------------|
| **Optimized Queries** | Read models tailored for specific queries |
| **Independent Scaling** | Scale reads and writes separately |
| **Simplified Models** | Each model focused on one concern |
| **Performance** | Denormalized read models = fast queries |
| **Flexibility** | Multiple read models for different needs |
| **Team Separation** | Different teams can work on read/write |

### Disadvantages

| Disadvantage | Description |
|--------------|-------------|
| **Complexity** | More moving parts to manage |
| **Eventual Consistency** | Reads may be stale |
| **Synchronization** | Need to keep models in sync |
| **Learning Curve** | Team needs to understand pattern |
| **Overhead** | May be overkill for simple apps |
| **Debugging** | Harder to trace issues across models |

---

## Best Practices

### 1. Start Simple

```
┌─────────────────────────────────────────────────────────────────┐
│  Don't start with full CQRS + Event Sourcing                   │
│                                                                 │
│  Evolution Path:                                                │
│  1. Single model with query/command separation                  │
│  2. Add read-optimized views/projections                        │
│  3. Separate databases if needed                                │
│  4. Add event sourcing if audit/temporal queries needed         │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Handle Eventual Consistency

```csharp
// Option 1: Return command result with ID, client polls for completion
public record CreateOrderResult(Guid OrderId, string Status);

// Option 2: Use correlation ID for tracking
public record CreateOrderCommand(Guid CorrelationId, ...);

// Option 3: Websockets/SignalR for push notifications
await _hubContext.Clients.User(userId)
    .SendAsync("OrderCreated", orderId);
```

### 3. Design Read Models for Queries

```
┌─────────────────────────────────────────────────────────────────┐
│  READ MODEL DESIGN PRINCIPLES                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ One read model per query/view                               │
│  ✅ Denormalize for performance                                 │
│  ✅ Pre-compute aggregations                                    │
│  ✅ Include all data needed by the query                        │
│  ❌ Don't reuse write model entities                            │
│  ❌ Don't add business logic to read models                     │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Idempotent Event Handlers

```csharp
public async Task HandleAsync(OrderCreatedEvent @event, CancellationToken ct)
{
    // Check if already processed (idempotency)
    if (await _readDb.Orders.AnyAsync(o => o.Id == @event.OrderId, ct))
        return;

    // Process event...
}
```

---

## Related Patterns

- [Event Sourcing Pattern](./event-sourcing-pattern.md)
- [Saga Pattern](./saga-pattern.md)
- [Mediator Pattern](./mediator-pattern.md)

---

## References

- Young, G. (2010). *CQRS Documents*
- Microsoft. *CQRS Pattern - Azure Architecture Center*
- Fowler, M. *CQRS - martinfowler.com*
