# Event Sourcing Pattern

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Traditional CRUD vs Event Sourcing](#traditional-crud-vs-event-sourcing)
- [Core Concepts](#core-concepts)
- [Visual Representation](#visual-representation)
- [Benefits](#benefits)
- [Challenges](#challenges)
- [When to Use](#when-to-use)
- [When NOT to Use](#when-not-to-use)
- [Implementation Example](#implementation-example)
- [Event Store Options](#event-store-options)
- [Related Patterns](#related-patterns)
- [References](#references)

## Overview

**Event Sourcing** is an architectural pattern where the state of an application is determined by a sequence of **events** rather than storing just the current state. Instead of updating a record in place, every state change is captured as an immutable event and appended to an event log.

> "Don't store the current state—store the events that led to the current state."

## How It Works

```
Traditional Approach:
────────────────────
Account Balance: $500  →  UPDATE to $400  →  Current state: $400
                          (Previous state lost!)


Event Sourcing Approach:
────────────────────────
Event Log:
┌─────┬─────────────────────┬─────────┬──────────┐
│ ID  │ Event Type          │ Amount  │ Balance  │
├─────┼─────────────────────┼─────────┼──────────┤
│ 1   │ AccountOpened       │ $0      │ $0       │
│ 2   │ MoneyDeposited      │ +$1000  │ $1000    │
│ 3   │ MoneyWithdrawn      │ -$200   │ $800     │
│ 4   │ MoneyWithdrawn      │ -$300   │ $500     │
│ 5   │ MoneyWithdrawn      │ -$100   │ $400     │  ← Current state
└─────┴─────────────────────┴─────────┴──────────┘

Current Balance = Replay all events = $400
Full history preserved!
```

## Traditional CRUD vs Event Sourcing

| Aspect | Traditional CRUD | Event Sourcing |
|--------|-----------------|----------------|
| **Storage** | Current state only | All events (history) |
| **Updates** | Overwrite existing data | Append new event |
| **History** | Lost (unless audited) | Complete audit trail |
| **Query** | Direct read | Replay events or read model |
| **Debugging** | "What happened?" Unknown | Full event replay |
| **Storage Size** | Smaller | Larger (all events) |
| **Complexity** | Simple | More complex |

## Core Concepts

### 1. Events

Events are **immutable facts** that have happened. They are named in **past tense**.

```csharp
// Good event names (past tense - facts)
OrderPlaced
PaymentReceived
ItemShipped
UserRegistered

// Bad event names (commands - not facts)
PlaceOrder      // ❌ This is a command
ProcessPayment  // ❌ This is a command
```

### 2. Event Store

The append-only log where all events are persisted.

```
┌─────────────────────────────────────────────────────────┐
│                     Event Store                          │
├─────────────────────────────────────────────────────────┤
│ Stream: Order-12345                                      │
│ ┌─────┬──────────────────┬────────────────────────────┐ │
│ │ Seq │ Event Type       │ Data                       │ │
│ ├─────┼──────────────────┼────────────────────────────┤ │
│ │ 1   │ OrderCreated     │ {customerId: "C1", ...}    │ │
│ │ 2   │ ItemAdded        │ {productId: "P1", qty: 2}  │ │
│ │ 3   │ ItemAdded        │ {productId: "P2", qty: 1}  │ │
│ │ 4   │ OrderSubmitted   │ {timestamp: "..."}         │ │
│ │ 5   │ PaymentReceived  │ {amount: 150.00}           │ │
│ │ 6   │ OrderShipped     │ {trackingId: "TRK123"}     │ │
│ └─────┴──────────────────┴────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3. Aggregate

The domain object whose state is rebuilt by replaying events.

```csharp
public class Order
{
    public Guid Id { get; private set; }
    public OrderStatus Status { get; private set; }
    public List<OrderItem> Items { get; private set; } = new();
    public decimal Total { get; private set; }

    // Rebuild state from events
    public void Apply(OrderCreated e) 
    {
        Id = e.OrderId;
        Status = OrderStatus.Created;
    }

    public void Apply(ItemAdded e) 
    {
        Items.Add(new OrderItem(e.ProductId, e.Quantity, e.Price));
        Total += e.Price * e.Quantity;
    }

    public void Apply(OrderShipped e) 
    {
        Status = OrderStatus.Shipped;
    }
}
```

### 4. Projections (Read Models)

Materialized views optimized for queries, built by processing events.

```
Events → Projection → Read Model (Database/Cache)

┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Event Store    │────►│   Projection    │────►│   Read Model     │
│                  │     │   (Handler)     │     │   (SQL/NoSQL)    │
│ OrderCreated     │     │                 │     │                  │
│ ItemAdded        │     │ Process events  │     │ Orders table     │
│ PaymentReceived  │     │ Update view     │     │ - OrderId        │
│ OrderShipped     │     │                 │     │ - Status         │
└──────────────────┘     └─────────────────┘     │ - Total          │
                                                 │ - ItemCount      │
                                                 └──────────────────┘
```

## Visual Representation

```
                              Event Sourcing Architecture
═══════════════════════════════════════════════════════════════════════════

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │   Client    │         │   Client    │         │   Client    │
    └──────┬──────┘         └──────┬──────┘         └──────┬──────┘
           │                       │                       │
           │ Commands              │ Commands              │ Queries
           ▼                       ▼                       │
    ┌─────────────────────────────────────────┐            │
    │           Command Handler               │            │
    │                                         │            │
    │  1. Load aggregate (replay events)      │            │
    │  2. Execute business logic              │            │
    │  3. Generate new events                 │            │
    │  4. Append to event store               │            │
    └─────────────────┬───────────────────────┘            │
                      │                                    │
                      │ Append Events                      │
                      ▼                                    │
    ┌─────────────────────────────────────────┐            │
    │            Event Store                  │            │
    │  ┌───────────────────────────────────┐  │            │
    │  │ [E1] [E2] [E3] [E4] [E5] [E6]     │  │            │
    │  │  ──────────────────────────────►  │  │            │
    │  │         Append-only log           │  │            │
    │  └───────────────────────────────────┘  │            │
    └─────────────────┬───────────────────────┘            │
                      │                                    │
                      │ Publish Events                     │
                      ▼                                    │
    ┌─────────────────────────────────────────┐            │
    │          Event Bus / Broker             │            │
    │       (Kafka, Event Hubs, etc.)         │            │
    └───┬─────────────┬─────────────┬─────────┘            │
        │             │             │                      │
        ▼             ▼             ▼                      │
    ┌───────┐    ┌───────┐    ┌───────────┐               │
    │Proj 1 │    │Proj 2 │    │Proj 3     │               │
    │       │    │       │    │           │               │
    └───┬───┘    └───┬───┘    └─────┬─────┘               │
        │            │              │                      │
        ▼            ▼              ▼                      │
    ┌───────┐    ┌───────┐    ┌───────────┐               │
    │Read   │    │Read   │    │Read       │◄──────────────┘
    │Model 1│    │Model 2│    │Model 3    │   Queries
    │(SQL)  │    │(Redis)│    │(Elastic)  │
    └───────┘    └───────┘    └───────────┘
```

## Benefits

| Benefit | Description |
|---------|-------------|
| **Complete Audit Trail** | Every change is recorded—perfect for compliance |
| **Time Travel** | Reconstruct state at any point in time |
| **Debug & Replay** | Reproduce bugs by replaying events |
| **Event Replay** | Rebuild read models or fix corrupted data |
| **Temporal Queries** | "What was the balance on March 15?" |
| **Decoupled Systems** | Events can trigger multiple downstream processes |
| **No Data Loss** | Never lose information—events are immutable |

## Challenges

| Challenge | Mitigation |
|-----------|------------|
| **Eventual Consistency** | Read models may lag behind writes |
| **Event Schema Evolution** | Use versioning, upcasting |
| **Storage Growth** | Implement snapshots for long-lived aggregates |
| **Complexity** | Only use where benefits outweigh costs |
| **Querying** | Requires separate read models (CQRS) |
| **Learning Curve** | Team needs to understand event-driven thinking |

### Snapshots (Performance Optimization)

For aggregates with many events, periodically save snapshots:

```
Without Snapshots:
─────────────────
Load Order → Replay 10,000 events → Current state (slow!)

With Snapshots:
───────────────
Load Order → Load snapshot (event 9,900) → Replay 100 events → Current state (fast!)

┌────────────────────────────────────────────────────────────┐
│ Event Store                                                 │
│ [E1][E2]...[E9900][SNAPSHOT][E9901][E9902]...[E10000]       │
│                      ↑                                      │
│              Snapshot at E9900                              │
│              (Serialized aggregate state)                   │
└────────────────────────────────────────────────────────────┘
```

## When to Use

✅ **Good fit for:**
- Financial systems (audit trail required)
- Order management / e-commerce
- Booking systems (reservations, tickets)
- Gaming (replay, undo/redo)
- Collaboration tools (version history)
- Systems requiring temporal queries
- Complex domain with business rules

## When NOT to Use

❌ **Poor fit for:**
- Simple CRUD applications
- Systems where history doesn't matter
- High-frequency updates with no audit needs
- Teams unfamiliar with event-driven architecture
- Prototypes or MVPs (adds complexity)

## Implementation Example

### Event Definitions

```csharp
// Base event
public abstract record DomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTime Timestamp { get; init; } = DateTime.UtcNow;
}

// Concrete events
public record AccountOpened(Guid AccountId, string Owner) : DomainEvent;
public record MoneyDeposited(Guid AccountId, decimal Amount) : DomainEvent;
public record MoneyWithdrawn(Guid AccountId, decimal Amount) : DomainEvent;
```

### Aggregate with Event Sourcing

```csharp
public class BankAccount
{
    public Guid Id { get; private set; }
    public string Owner { get; private set; }
    public decimal Balance { get; private set; }
    
    private readonly List<DomainEvent> _uncommittedEvents = new();
    
    // Rebuild from history
    public static BankAccount FromHistory(IEnumerable<DomainEvent> events)
    {
        var account = new BankAccount();
        foreach (var e in events)
        {
            account.Apply(e);
        }
        return account;
    }
    
    // Command: Open account
    public void Open(Guid id, string owner)
    {
        if (Id != Guid.Empty) throw new InvalidOperationException("Already opened");
        
        var @event = new AccountOpened(id, owner);
        Apply(@event);
        _uncommittedEvents.Add(@event);
    }
    
    // Command: Deposit money
    public void Deposit(decimal amount)
    {
        if (amount <= 0) throw new ArgumentException("Amount must be positive");
        
        var @event = new MoneyDeposited(Id, amount);
        Apply(@event);
        _uncommittedEvents.Add(@event);
    }
    
    // Command: Withdraw money
    public void Withdraw(decimal amount)
    {
        if (amount > Balance) throw new InvalidOperationException("Insufficient funds");
        
        var @event = new MoneyWithdrawn(Id, amount);
        Apply(@event);
        _uncommittedEvents.Add(@event);
    }
    
    // Apply events to state
    private void Apply(DomainEvent @event)
    {
        switch (@event)
        {
            case AccountOpened e:
                Id = e.AccountId;
                Owner = e.Owner;
                Balance = 0;
                break;
            case MoneyDeposited e:
                Balance += e.Amount;
                break;
            case MoneyWithdrawn e:
                Balance -= e.Amount;
                break;
        }
    }
    
    public IEnumerable<DomainEvent> GetUncommittedEvents() => _uncommittedEvents;
    public void ClearUncommittedEvents() => _uncommittedEvents.Clear();
}
```

### Usage

```csharp
// Create new account
var account = new BankAccount();
account.Open(Guid.NewGuid(), "John Doe");
account.Deposit(1000);
account.Withdraw(200);
account.Deposit(500);

// Save events to store
var events = account.GetUncommittedEvents();
await eventStore.AppendAsync("account-123", events);
account.ClearUncommittedEvents();

// Later: Rebuild from history
var history = await eventStore.LoadAsync("account-123");
var rehydrated = BankAccount.FromHistory(history);
Console.WriteLine($"Balance: {rehydrated.Balance}"); // $1300
```

## Event Store Options

| Technology | Type | Best For |
|------------|------|----------|
| **EventStoreDB** | Purpose-built | Full event sourcing features |
| **Apache Kafka** | Log-based | High-throughput streaming |
| **Azure Event Hubs** | Managed service | Azure-native solutions |
| **Azure Cosmos DB** | Change feed | Multi-model with event support |
| **PostgreSQL** | RDBMS | Simple implementations |
| **MongoDB** | Document DB | Flexible schema events |
| **Marten** | .NET library | PostgreSQL-based for .NET |

## Related Patterns

| Pattern | Relationship |
|---------|--------------|
| **CQRS** | Often used together—separate read/write models |
| **Domain-Driven Design** | Aggregates and domain events |
| **Saga Pattern** | Long-running transactions across services |
| **Outbox Pattern** | Reliable event publishing |
| **Event-Driven Architecture** | Events as integration mechanism |

### Event Sourcing + CQRS

```
┌─────────────────────────────────────────────────────────────────┐
│                    CQRS + Event Sourcing                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Commands                              Queries                 │
│      │                                     │                    │
│      ▼                                     ▼                    │
│  ┌───────────┐                      ┌───────────┐              │
│  │  Command  │                      │   Query   │              │
│  │  Handler  │                      │  Handler  │              │
│  └─────┬─────┘                      └─────┬─────┘              │
│        │                                  │                    │
│        ▼                                  │                    │
│  ┌───────────┐     Events           ┌─────▼─────┐              │
│  │  Event    │─────────────────────►│   Read    │              │
│  │  Store    │     (Projections)    │   Model   │              │
│  │ (Write)   │                      │  (Read)   │              │
│  └───────────┘                      └───────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## References

- [Martin Fowler - Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- [Microsoft - Event Sourcing Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [EventStoreDB Documentation](https://www.eventstore.com/docs/)
- [Greg Young - CQRS and Event Sourcing](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)
- [Vaughn Vernon - Implementing Domain-Driven Design](https://www.amazon.com/Implementing-Domain-Driven-Design-Vaughn-Vernon/dp/0321834577)
