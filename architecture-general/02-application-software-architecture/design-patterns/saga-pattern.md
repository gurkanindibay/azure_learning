# Saga Pattern

## Table of Contents

- [Overview](#overview)
- [The Problem: Distributed Transactions](#the-problem-distributed-transactions)
- [Saga Types](#saga-types)
- [Choreography-Based Saga](#choreography-based-saga)
- [Orchestration-Based Saga](#orchestration-based-saga)
- [Compensating Transactions](#compensating-transactions)
- [Implementation Examples](#implementation-examples)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [When to Use](#when-to-use)

---

## Overview

The **Saga Pattern** is a design pattern for managing data consistency across microservices in distributed transaction scenarios. Instead of using a single ACID transaction, a saga breaks the transaction into a sequence of local transactions, each with a compensating transaction to undo changes if something fails.

### Key Concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SAGA PATTERN OVERVIEW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional Transaction (ACID)        Saga Pattern                         │
│  ────────────────────────────          ────────────                         │
│                                                                             │
│  ┌─────────────────────────┐           T1 ──► T2 ──► T3 ──► T4             │
│  │    Single Transaction   │                                                │
│  │    All or Nothing       │           If T3 fails:                         │
│  │    Locks Resources      │           T1 ──► T2 ──► T3 ✗                  │
│  └─────────────────────────┘                    │                           │
│                                                 ▼                           │
│                                           C2 ◄── C1                         │
│                                        (Compensate)                         │
│                                                                             │
│  Legend:                                                                    │
│  T = Transaction (forward)                                                  │
│  C = Compensation (rollback)                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Problem: Distributed Transactions

### Why Not 2PC (Two-Phase Commit)?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROBLEMS WITH 2PC IN MICROSERVICES                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  2PC (Two-Phase Commit)                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   Coordinator                                                       │   │
│  │       │                                                             │   │
│  │       ├──► Prepare? ──► Service A ──► Ready ──┐                    │   │
│  │       ├──► Prepare? ──► Service B ──► Ready ──┼──► Commit All      │   │
│  │       └──► Prepare? ──► Service C ──► Ready ──┘                    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Problems:                                                                  │
│  ❌ Synchronous - all services must be available                           │
│  ❌ Locks resources during entire transaction                              │
│  ❌ Single point of failure (coordinator)                                  │
│  ❌ Latency increases with more participants                               │
│  ❌ Not suitable for long-running transactions                             │
│  ❌ Doesn't work well across different databases/services                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Saga Solution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SAGA APPROACH                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Each service:                                                              │
│  ✅ Completes its local transaction                                        │
│  ✅ Publishes an event or calls next service                               │
│  ✅ Has a compensating action for rollback                                 │
│                                                                             │
│  Properties:                                                                │
│  • ACD (Atomicity, Consistency, Durability) - no Isolation                 │
│  • Eventual Consistency                                                     │
│  • Asynchronous                                                             │
│  • Decentralized                                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Saga Types

### Comparison

| Aspect | Choreography | Orchestration |
|--------|--------------|---------------|
| **Coordination** | Decentralized (events) | Centralized (orchestrator) |
| **Coupling** | Loose | Tighter to orchestrator |
| **Complexity** | Simple for few steps | Better for complex flows |
| **Visibility** | Harder to track | Easy to monitor |
| **Single Point of Failure** | No | Yes (orchestrator) |
| **Testing** | Harder | Easier |

---

## Choreography-Based Saga

In choreography, each service publishes domain events that trigger the next step. No central coordinator.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHOREOGRAPHY-BASED SAGA                                  │
│                    (E-Commerce Order Example)                               │
└─────────────────────────────────────────────────────────────────────────────┘

SUCCESS FLOW:
─────────────

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Order   │     │ Payment  │     │Inventory │     │ Shipping │
│ Service  │     │ Service  │     │ Service  │     │ Service  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ OrderCreated   │                │                │
     │───────────────►│                │                │
     │                │                │                │
     │                │ PaymentCompleted                │
     │                │───────────────►│                │
     │                │                │                │
     │                │                │ InventoryReserved
     │                │                │───────────────►│
     │                │                │                │
     │◄───────────────┼────────────────┼────────────────│
     │                        OrderShipped              │


FAILURE FLOW (Payment Failed):
──────────────────────────────

┌──────────┐     ┌──────────┐     ┌──────────┐
│  Order   │     │ Payment  │     │Inventory │
│ Service  │     │ Service  │     │ Service  │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ OrderCreated   │                │
     │───────────────►│                │
     │                │                │
     │                │ PaymentFailed  │
     │◄───────────────│                │
     │                │                │
     │ OrderCancelled │                │
     │  (Compensate)  │                │
     │                │                │
```

### Event Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHOREOGRAPHY EVENT FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         Message Bus / Event Broker                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  OrderCreated ──► PaymentService listens                           │   │
│  │                                                                     │   │
│  │  PaymentCompleted ──► InventoryService listens                     │   │
│  │  PaymentFailed ──► OrderService listens (compensate)               │   │
│  │                                                                     │   │
│  │  InventoryReserved ──► ShippingService listens                     │   │
│  │  InventoryFailed ──► PaymentService listens (refund)               │   │
│  │                                                                     │   │
│  │  ShipmentCreated ──► OrderService listens (complete)               │   │
│  │  ShipmentFailed ──► InventoryService listens (release)             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pros and Cons

| Pros | Cons |
|------|------|
| ✅ Loose coupling | ❌ Hard to understand flow |
| ✅ No single point of failure | ❌ Difficult to track/debug |
| ✅ Simple for few services | ❌ Cyclic dependencies risk |
| ✅ Services are autonomous | ❌ Testing is challenging |

---

## Orchestration-Based Saga

In orchestration, a central **Saga Orchestrator** coordinates the entire flow, telling each service what to do.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION-BASED SAGA                                 │
│                    (E-Commerce Order Example)                               │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────────┐
                         │  Saga Orchestrator  │
                         │   (Order Saga)      │
                         └──────────┬──────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │   Payment   │          │  Inventory  │          │  Shipping   │
    │   Service   │          │   Service   │          │   Service   │
    └─────────────┘          └─────────────┘          └─────────────┘


ORCHESTRATOR FLOW:
──────────────────

┌───────────────────┐
│ Saga Orchestrator │
└─────────┬─────────┘
          │
          │ 1. ProcessPayment()
          │──────────────────────►┌──────────────┐
          │                       │   Payment    │
          │◄──────────────────────│   Service    │
          │    PaymentResult      └──────────────┘
          │
          │ 2. ReserveInventory()
          │──────────────────────►┌──────────────┐
          │                       │  Inventory   │
          │◄──────────────────────│   Service    │
          │    ReservationResult  └──────────────┘
          │
          │ 3. CreateShipment()
          │──────────────────────►┌──────────────┐
          │                       │   Shipping   │
          │◄──────────────────────│   Service    │
          │    ShipmentResult     └──────────────┘
          │
          ▼
    [Saga Complete]
```

### State Machine Representation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAGA STATE MACHINE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌─────────────┐                                          │
│                    │   PENDING   │                                          │
│                    └──────┬──────┘                                          │
│                           │ Start                                           │
│                           ▼                                                 │
│                    ┌─────────────┐                                          │
│            ┌───────│  PAYMENT    │───────┐                                  │
│            │       │  PENDING    │       │                                  │
│            │       └─────────────┘       │                                  │
│      Failed│                             │Success                           │
│            ▼                             ▼                                  │
│     ┌─────────────┐              ┌─────────────┐                            │
│     │  CANCELLED  │              │  INVENTORY  │───────┐                    │
│     └─────────────┘       ┌──────│  PENDING    │       │                    │
│            ▲              │      └─────────────┘       │Success             │
│            │        Failed│                            ▼                    │
│            │              ▼                     ┌─────────────┐             │
│            │       ┌─────────────┐              │  SHIPPING   │──────┐      │
│            │       │  PAYMENT    │       ┌─────│  PENDING    │      │      │
│            │       │  REFUNDING  │       │     └─────────────┘      │      │
│            │       └──────┬──────┘       │Failed                    │Success│
│            │              │              ▼                          ▼      │
│            │              │       ┌─────────────┐            ┌───────────┐ │
│            └──────────────┴──────►│ COMPENSATING│            │ COMPLETED │ │
│                                   └─────────────┘            └───────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pros and Cons

| Pros | Cons |
|------|------|
| ✅ Clear flow visibility | ❌ Single point of failure |
| ✅ Easier to debug/trace | ❌ Additional infrastructure |
| ✅ Centralized error handling | ❌ Orchestrator can become complex |
| ✅ Better for complex workflows | ❌ Tighter coupling to orchestrator |
| ✅ Easier testing | ❌ Risk of becoming a "god" service |

---

## Compensating Transactions

Compensating transactions undo the effects of a previously completed transaction. They are **semantic rollbacks**, not database rollbacks.

### Compensation Rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPENSATION DESIGN RULES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. MUST be idempotent (safe to retry)                                     │
│                                                                             │
│  2. MUST be retryable (handle transient failures)                          │
│                                                                             │
│  3. Order: Execute compensations in REVERSE order                          │
│     T1 → T2 → T3 (fails)                                                   │
│     C2 → C1 (compensate in reverse)                                        │
│                                                                             │
│  4. Some actions cannot be compensated (send email, SMS)                   │
│     → Use "pivot transactions" or accept business impact                   │
│                                                                             │
│  5. Compensation may need manual intervention                              │
│     → Design for human-in-the-loop when needed                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example Compensations

| Action | Compensation |
|--------|-------------|
| Create Order | Cancel Order |
| Reserve Inventory | Release Inventory |
| Charge Payment | Refund Payment |
| Book Flight | Cancel Booking |
| Create User Account | Deactivate Account |
| Send Confirmation Email | Send Cancellation Email |

### Non-Compensatable Actions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIVOT TRANSACTIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Some actions cannot be undone:                                             │
│  • Sending emails/SMS                                                       │
│  • External API calls (payment processed by bank)                          │
│  • Physical actions (item shipped)                                          │
│                                                                             │
│  Strategy: Place non-compensatable actions LAST (pivot point)              │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                                                                    │    │
│  │   Compensatable      │  Pivot Transaction  │  Non-compensatable   │    │
│  │   ─────────────      │  ─────────────────  │  ──────────────────  │    │
│  │   Reserve Stock ────►│  Charge Card ──────►│  Send Confirmation   │    │
│  │   Create Order       │  (Point of no      │  Notify Warehouse    │    │
│  │                      │   return)          │                      │    │
│  │                      │                     │                      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Examples

### Orchestrator Implementation (C#)

```csharp
public class OrderSaga
{
    private readonly IPaymentService _paymentService;
    private readonly IInventoryService _inventoryService;
    private readonly IShippingService _shippingService;
    private readonly ISagaRepository _sagaRepository;

    public async Task<SagaResult> ExecuteAsync(CreateOrderCommand command)
    {
        var saga = new SagaState(command.OrderId);
        
        try
        {
            // Step 1: Process Payment
            saga.CurrentStep = SagaStep.PaymentPending;
            await _sagaRepository.SaveAsync(saga);
            
            var paymentResult = await _paymentService.ProcessPaymentAsync(
                command.OrderId, 
                command.Amount
            );
            
            if (!paymentResult.Success)
            {
                saga.CurrentStep = SagaStep.Cancelled;
                await _sagaRepository.SaveAsync(saga);
                return SagaResult.Failed("Payment failed");
            }
            
            saga.PaymentId = paymentResult.PaymentId;
            saga.CurrentStep = SagaStep.PaymentCompleted;
            await _sagaRepository.SaveAsync(saga);

            // Step 2: Reserve Inventory
            saga.CurrentStep = SagaStep.InventoryPending;
            await _sagaRepository.SaveAsync(saga);
            
            var inventoryResult = await _inventoryService.ReserveAsync(
                command.OrderId, 
                command.Items
            );
            
            if (!inventoryResult.Success)
            {
                // Compensate: Refund payment
                await CompensateAsync(saga);
                return SagaResult.Failed("Inventory reservation failed");
            }
            
            saga.ReservationId = inventoryResult.ReservationId;
            saga.CurrentStep = SagaStep.InventoryReserved;
            await _sagaRepository.SaveAsync(saga);

            // Step 3: Create Shipment
            saga.CurrentStep = SagaStep.ShippingPending;
            await _sagaRepository.SaveAsync(saga);
            
            var shippingResult = await _shippingService.CreateShipmentAsync(
                command.OrderId, 
                command.ShippingAddress
            );
            
            if (!shippingResult.Success)
            {
                // Compensate: Release inventory, refund payment
                await CompensateAsync(saga);
                return SagaResult.Failed("Shipping creation failed");
            }

            saga.CurrentStep = SagaStep.Completed;
            await _sagaRepository.SaveAsync(saga);
            
            return SagaResult.Succeeded();
        }
        catch (Exception ex)
        {
            await CompensateAsync(saga);
            throw;
        }
    }

    private async Task CompensateAsync(SagaState saga)
    {
        saga.CurrentStep = SagaStep.Compensating;
        await _sagaRepository.SaveAsync(saga);
        
        // Compensate in reverse order
        if (saga.ReservationId.HasValue)
        {
            await _inventoryService.ReleaseReservationAsync(saga.ReservationId.Value);
        }
        
        if (saga.PaymentId.HasValue)
        {
            await _paymentService.RefundAsync(saga.PaymentId.Value);
        }
        
        saga.CurrentStep = SagaStep.Compensated;
        await _sagaRepository.SaveAsync(saga);
    }
}
```

### Choreography Implementation (Event Handlers)

```csharp
// Payment Service - Listens for OrderCreated
public class PaymentEventHandler : IEventHandler<OrderCreatedEvent>
{
    private readonly IPaymentProcessor _paymentProcessor;
    private readonly IEventPublisher _eventPublisher;

    public async Task HandleAsync(OrderCreatedEvent @event)
    {
        try
        {
            var result = await _paymentProcessor.ProcessAsync(
                @event.OrderId, 
                @event.Amount
            );

            if (result.Success)
            {
                await _eventPublisher.PublishAsync(new PaymentCompletedEvent
                {
                    OrderId = @event.OrderId,
                    PaymentId = result.PaymentId
                });
            }
            else
            {
                await _eventPublisher.PublishAsync(new PaymentFailedEvent
                {
                    OrderId = @event.OrderId,
                    Reason = result.FailureReason
                });
            }
        }
        catch (Exception ex)
        {
            await _eventPublisher.PublishAsync(new PaymentFailedEvent
            {
                OrderId = @event.OrderId,
                Reason = ex.Message
            });
        }
    }
}

// Inventory Service - Listens for PaymentCompleted
public class InventoryEventHandler : 
    IEventHandler<PaymentCompletedEvent>,
    IEventHandler<ShippingFailedEvent>  // Compensation
{
    public async Task HandleAsync(PaymentCompletedEvent @event)
    {
        var result = await _inventoryService.ReserveAsync(@event.OrderId);
        
        if (result.Success)
        {
            await _eventPublisher.PublishAsync(new InventoryReservedEvent
            {
                OrderId = @event.OrderId,
                ReservationId = result.ReservationId
            });
        }
        else
        {
            // Trigger compensation
            await _eventPublisher.PublishAsync(new InventoryFailedEvent
            {
                OrderId = @event.OrderId
            });
        }
    }

    // Compensation handler
    public async Task HandleAsync(ShippingFailedEvent @event)
    {
        await _inventoryService.ReleaseReservationAsync(@event.OrderId);
        
        await _eventPublisher.PublishAsync(new InventoryReleasedEvent
        {
            OrderId = @event.OrderId
        });
    }
}
```

### Using MassTransit Saga State Machine

```csharp
public class OrderSagaState : SagaStateMachineInstance
{
    public Guid CorrelationId { get; set; }
    public string CurrentState { get; set; }
    public Guid OrderId { get; set; }
    public Guid? PaymentId { get; set; }
    public Guid? ReservationId { get; set; }
}

public class OrderSagaStateMachine : MassTransitStateMachine<OrderSagaState>
{
    public State PaymentPending { get; private set; }
    public State InventoryPending { get; private set; }
    public State ShippingPending { get; private set; }
    public State Completed { get; private set; }
    public State Compensating { get; private set; }
    public State Failed { get; private set; }

    public Event<OrderCreated> OrderCreated { get; private set; }
    public Event<PaymentCompleted> PaymentCompleted { get; private set; }
    public Event<PaymentFailed> PaymentFailed { get; private set; }
    public Event<InventoryReserved> InventoryReserved { get; private set; }
    public Event<InventoryFailed> InventoryFailed { get; private set; }

    public OrderSagaStateMachine()
    {
        InstanceState(x => x.CurrentState);

        Event(() => OrderCreated, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => PaymentCompleted, x => x.CorrelateById(m => m.Message.OrderId));
        Event(() => PaymentFailed, x => x.CorrelateById(m => m.Message.OrderId));

        Initially(
            When(OrderCreated)
                .Then(context => context.Instance.OrderId = context.Data.OrderId)
                .Send(context => new ProcessPayment(context.Data.OrderId, context.Data.Amount))
                .TransitionTo(PaymentPending)
        );

        During(PaymentPending,
            When(PaymentCompleted)
                .Then(context => context.Instance.PaymentId = context.Data.PaymentId)
                .Send(context => new ReserveInventory(context.Instance.OrderId))
                .TransitionTo(InventoryPending),
            When(PaymentFailed)
                .TransitionTo(Failed)
        );

        During(InventoryPending,
            When(InventoryReserved)
                .Send(context => new CreateShipment(context.Instance.OrderId))
                .TransitionTo(ShippingPending),
            When(InventoryFailed)
                .Send(context => new RefundPayment(context.Instance.PaymentId.Value))
                .TransitionTo(Compensating)
        );
    }
}
```

---

## Error Handling

### Retry Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RETRY STRATEGIES                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. IMMEDIATE RETRY                                                         │
│     For transient failures (network blip)                                   │
│     Retry immediately, limited attempts                                     │
│                                                                             │
│  2. EXPONENTIAL BACKOFF                                                     │
│     Wait 1s, 2s, 4s, 8s... between retries                                 │
│     Good for temporary unavailability                                       │
│                                                                             │
│  3. CIRCUIT BREAKER                                                         │
│     Stop calling failing service temporarily                                │
│     Prevent cascade failures                                                │
│                                                                             │
│  4. DEAD LETTER QUEUE                                                       │
│     After max retries, move to DLQ                                         │
│     Manual intervention or scheduled retry                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Handling Stuck Sagas

```csharp
public class SagaTimeoutHandler
{
    public async Task HandleStuckSagasAsync()
    {
        // Find sagas stuck in intermediate states
        var stuckSagas = await _sagaRepository
            .GetSagasInStateAsync(
                states: new[] { "PaymentPending", "InventoryPending" },
                olderThan: TimeSpan.FromMinutes(30)
            );

        foreach (var saga in stuckSagas)
        {
            // Option 1: Retry the current step
            if (saga.RetryCount < MaxRetries)
            {
                await RetryCurrentStepAsync(saga);
            }
            // Option 2: Compensate and fail
            else
            {
                await CompensateAndFailAsync(saga);
            }
        }
    }
}
```

---

## Best Practices

### 1. Design for Idempotency

```csharp
public async Task HandlePaymentAsync(ProcessPaymentCommand command)
{
    // Check if already processed
    var existing = await _paymentRepository
        .GetByIdempotencyKeyAsync(command.IdempotencyKey);
    
    if (existing != null)
        return existing.Result; // Return existing result
    
    // Process new payment
    var result = await ProcessNewPaymentAsync(command);
    
    // Store with idempotency key
    await _paymentRepository.SaveWithIdempotencyKeyAsync(
        command.IdempotencyKey, 
        result
    );
    
    return result;
}
```

### 2. Use Correlation IDs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CORRELATION ID TRACKING                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Every message/event in the saga carries the same CorrelationId            │
│                                                                             │
│  OrderCreated       { CorrelationId: "abc-123", OrderId: "..." }           │
│       │                                                                     │
│       ▼                                                                     │
│  PaymentCompleted   { CorrelationId: "abc-123", PaymentId: "..." }         │
│       │                                                                     │
│       ▼                                                                     │
│  InventoryReserved  { CorrelationId: "abc-123", ReservationId: "..." }     │
│                                                                             │
│  Benefits:                                                                  │
│  • Trace entire saga flow in logs                                          │
│  • Debug failures easily                                                    │
│  • Correlate across services                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3. Persist Saga State

```
Always persist saga state between steps:
• Know where you are if service restarts
• Resume from last successful step
• Audit trail of saga progress
```

### 4. Monitor and Alert

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SAGA MONITORING                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Metrics to Track:                                                          │
│  • Saga success/failure rate                                                │
│  • Average saga duration                                                    │
│  • Sagas in each state (detect bottlenecks)                                │
│  • Compensation frequency                                                   │
│  • Stuck sagas count                                                        │
│                                                                             │
│  Alerts:                                                                    │
│  • Saga taking too long                                                     │
│  • High failure rate                                                        │
│  • Compensation failures                                                    │
│  • Dead letter queue growth                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## When to Use

### Good Fit

- ✅ Multi-service transactions
- ✅ Long-running business processes
- ✅ When 2PC is not feasible
- ✅ Eventual consistency is acceptable
- ✅ Services use different databases

### Not a Good Fit

- ❌ Single service operations
- ❌ Strong consistency required
- ❌ Simple CRUD operations
- ❌ Synchronous response needed

---

## Related Patterns

- [Event Sourcing Pattern](./event-sourcing-pattern.md)
- [CQRS Pattern](./cqrs-pattern.md)
- [Outbox Pattern](./outbox-pattern.md)

---

## References

- Richardson, C. *Microservices Patterns* - Chapter 4: Managing Transactions with Sagas
- Microsoft. *Saga distributed transactions pattern - Azure Architecture Center*
- Garcia-Molina, H. & Salem, K. (1987). *Sagas* - Princeton University
