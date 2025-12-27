# Tactical Domain-Driven Design

## Table of Contents

- [Overview](#overview)
- [Building Blocks](#building-blocks)
- [Entities](#entities)
- [Value Objects](#value-objects)
- [Aggregates](#aggregates)
- [Domain Events](#domain-events)
- [Repositories](#repositories)
- [Domain Services](#domain-services)
- [Factories](#factories)
- [Modules](#modules)
- [Putting It All Together](#putting-it-all-together)
- [Common Pitfalls](#common-pitfalls)
- [References](#references)

## Overview

**Tactical Domain-Driven Design** provides the building blocks for implementing a rich domain model within a bounded context. While Strategic DDD focuses on the big picture, Tactical DDD focuses on the implementation details.

> "Tactical patterns help us write code that expresses the domain model in a way that is both correct and maintainable."  
> — Eric Evans

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tactical DDD Building Blocks                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│   │  Entities   │  │   Value     │  │ Aggregates  │                │
│   │             │  │  Objects    │  │             │                │
│   │ Identity +  │  │ Immutable   │  │ Consistency │                │
│   │ Lifecycle   │  │ Equality by │  │ Boundary    │                │
│   │             │  │ attributes  │  │             │                │
│   └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                      │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│   │  Domain     │  │Repositories │  │  Domain     │                │
│   │  Events     │  │             │  │  Services   │                │
│   │             │  │ Collection  │  │             │                │
│   │ Something   │  │ Abstraction │  │ Stateless   │                │
│   │ happened    │  │             │  │ Operations  │                │
│   └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                      │
│   ┌─────────────┐  ┌─────────────┐                                  │
│   │ Factories   │  │  Modules    │                                  │
│   │             │  │             │                                  │
│   │ Complex     │  │ Organize    │                                  │
│   │ Creation    │  │ Model       │                                  │
│   └─────────────┘  └─────────────┘                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Building Blocks

| Building Block | Purpose | Key Characteristic |
|----------------|---------|-------------------|
| **Entity** | Model things with identity | Tracked by ID, mutable |
| **Value Object** | Model descriptive attributes | Immutable, no identity |
| **Aggregate** | Group of entities/values | Consistency boundary |
| **Domain Event** | Record something that happened | Immutable fact |
| **Repository** | Access to aggregates | Collection abstraction |
| **Domain Service** | Operations that don't fit entities | Stateless |
| **Factory** | Complex object creation | Encapsulate construction |
| **Module** | Organize the model | Namespace/package |

## Entities

An **Entity** is an object defined primarily by its identity, rather than its attributes.

### Characteristics

- Has a unique **identity** that persists over time
- Identity remains constant even if attributes change
- Two entities are equal if they have the same identity
- Has a **lifecycle** (created, modified, deleted)

### Example: Customer Entity

```python
class Customer:
    """Entity - identified by customer_id"""
    
    def __init__(self, customer_id: CustomerId, name: str, email: Email):
        self._id = customer_id
        self._name = name
        self._email = email
        self._status = CustomerStatus.ACTIVE
        self._created_at = datetime.utcnow()
    
    @property
    def id(self) -> CustomerId:
        return self._id
    
    def change_email(self, new_email: Email) -> None:
        """Business logic for email change"""
        if self._status == CustomerStatus.SUSPENDED:
            raise CustomerSuspendedException()
        self._email = new_email
    
    def suspend(self) -> None:
        self._status = CustomerStatus.SUSPENDED
    
    def __eq__(self, other) -> bool:
        """Entities are equal if IDs match"""
        if not isinstance(other, Customer):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)
```

```csharp
// C# Example
public class Customer : Entity<CustomerId>
{
    public string Name { get; private set; }
    public Email Email { get; private set; }
    public CustomerStatus Status { get; private set; }
    
    public Customer(CustomerId id, string name, Email email) : base(id)
    {
        Name = name ?? throw new ArgumentNullException(nameof(name));
        Email = email ?? throw new ArgumentNullException(nameof(email));
        Status = CustomerStatus.Active;
    }
    
    public void ChangeEmail(Email newEmail)
    {
        if (Status == CustomerStatus.Suspended)
            throw new CustomerSuspendedException();
        
        Email = newEmail;
        AddDomainEvent(new CustomerEmailChangedEvent(Id, newEmail));
    }
}
```

## Value Objects

A **Value Object** is an object that describes some characteristic and has no conceptual identity.

### Characteristics

- **Immutable** - cannot be changed after creation
- **Equality by attributes** - two value objects are equal if all attributes are equal
- **No identity** - tracked by what they are, not who they are
- **Self-validating** - always in a valid state
- **Side-effect free** - operations return new instances

### Example: Money Value Object

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)  # Immutable
class Money:
    """Value Object - no identity, immutable"""
    
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")
    
    def add(self, other: 'Money') -> 'Money':
        """Returns new Money instance"""
        if self.currency != other.currency:
            raise CurrencyMismatchException()
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        return Money(self.amount * factor, self.currency)
```

```csharp
// C# Example
public record Money
{
    public decimal Amount { get; }
    public string Currency { get; }
    
    public Money(decimal amount, string currency)
    {
        if (amount < 0)
            throw new ArgumentException("Amount cannot be negative");
        if (string.IsNullOrEmpty(currency) || currency.Length != 3)
            throw new ArgumentException("Currency must be 3-letter code");
        
        Amount = amount;
        Currency = currency.ToUpper();
    }
    
    public Money Add(Money other)
    {
        if (Currency != other.Currency)
            throw new CurrencyMismatchException();
        return new Money(Amount + other.Amount, Currency);
    }
    
    public Money Multiply(decimal factor) => new(Amount * factor, Currency);
}
```

### Common Value Objects

| Value Object | Attributes | Example |
|--------------|------------|---------|
| **Money** | amount, currency | `Money(100.00, "USD")` |
| **Address** | street, city, zip, country | `Address("123 Main", "NYC", "10001", "US")` |
| **DateRange** | start, end | `DateRange(jan1, jan31)` |
| **Email** | value | `Email("user@example.com")` |
| **PhoneNumber** | countryCode, number | `PhoneNumber("+1", "5551234567")` |
| **Coordinates** | latitude, longitude | `Coordinates(40.7128, -74.0060)` |

## Aggregates

An **Aggregate** is a cluster of domain objects that are treated as a single unit for data changes.

### Key Concepts

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Aggregate Structure                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │                     Order Aggregate                      │       │
│   │  ┌───────────────────────────────────────────────────┐  │       │
│   │  │               Aggregate Root                       │  │       │
│   │  │                  (Order)                           │  │       │
│   │  │  - Enforces invariants                            │  │       │
│   │  │  - Entry point for all changes                    │  │       │
│   │  │  - Controls access to internal entities           │  │       │
│   │  └───────────────────────────────────────────────────┘  │       │
│   │                         │                                │       │
│   │           ┌─────────────┼─────────────┐                 │       │
│   │           │             │             │                 │       │
│   │           ▼             ▼             ▼                 │       │
│   │    ┌──────────┐  ┌──────────┐  ┌──────────┐            │       │
│   │    │OrderLine │  │OrderLine │  │ Shipping │            │       │
│   │    │  (Entity)│  │  (Entity)│  │  Address │            │       │
│   │    │          │  │          │  │  (Value) │            │       │
│   │    └──────────┘  └──────────┘  └──────────┘            │       │
│   │                                                         │       │
│   │   Boundary: All changes go through Order (root)        │       │
│   └─────────────────────────────────────────────────────────┘       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Aggregate Rules

| Rule | Description |
|------|-------------|
| **Single Root** | Each aggregate has exactly one root entity |
| **External References** | Outside objects only reference the root |
| **Root Controls Access** | All modifications go through the root |
| **Transactional Boundary** | One aggregate = one transaction |
| **Reference by ID** | Aggregates reference other aggregates by ID only |
| **Eventual Consistency** | Between aggregates, use eventual consistency |

### Example: Order Aggregate

```python
class Order:
    """Aggregate Root"""
    
    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id  # Reference by ID
        self._lines: List[OrderLine] = []
        self._status = OrderStatus.DRAFT
        self._shipping_address: Optional[Address] = None
        self._events: List[DomainEvent] = []
    
    @property
    def id(self) -> OrderId:
        return self._id
    
    @property
    def total(self) -> Money:
        return sum((line.subtotal for line in self._lines), Money(0, "USD"))
    
    def add_line(self, product_id: ProductId, quantity: int, unit_price: Money) -> None:
        """All modifications go through the aggregate root"""
        if self._status != OrderStatus.DRAFT:
            raise OrderNotModifiableException()
        
        # Enforce invariant: max 10 lines per order
        if len(self._lines) >= 10:
            raise TooManyLinesException()
        
        line = OrderLine(
            line_id=OrderLineId.generate(),
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )
        self._lines.append(line)
        self._events.append(OrderLineAddedEvent(self._id, line.id))
    
    def remove_line(self, line_id: OrderLineId) -> None:
        if self._status != OrderStatus.DRAFT:
            raise OrderNotModifiableException()
        
        line = next((l for l in self._lines if l.id == line_id), None)
        if line is None:
            raise LineNotFoundException()
        
        self._lines.remove(line)
    
    def submit(self, shipping_address: Address) -> None:
        """Transition order from DRAFT to SUBMITTED"""
        if self._status != OrderStatus.DRAFT:
            raise InvalidStateTransitionException()
        
        if not self._lines:
            raise EmptyOrderException()
        
        self._shipping_address = shipping_address
        self._status = OrderStatus.SUBMITTED
        self._events.append(OrderSubmittedEvent(self._id, self.total))
    
    def pull_events(self) -> List[DomainEvent]:
        events = self._events.copy()
        self._events.clear()
        return events


class OrderLine:
    """Entity within the Order aggregate"""
    
    def __init__(self, line_id: OrderLineId, product_id: ProductId, 
                 quantity: int, unit_price: Money):
        self._id = line_id
        self._product_id = product_id
        self._quantity = quantity
        self._unit_price = unit_price
    
    @property
    def id(self) -> OrderLineId:
        return self._id
    
    @property
    def subtotal(self) -> Money:
        return self._unit_price.multiply(self._quantity)
```

### Aggregate Design Guidelines

```
Small Aggregates:
─────────────────
✓ Faster to load
✓ Less contention
✓ Better scalability

Reference by ID:
────────────────
┌─────────┐         ┌─────────┐
│  Order  │         │Customer │
│         │  ──ID──►│         │
│customer │         │         │
│  _id    │         │         │
└─────────┘         └─────────┘

NOT direct reference:
┌─────────┐         ┌─────────┐
│  Order  │         │Customer │
│         │  ──X──►│         │
│customer │ object  │         │
└─────────┘         └─────────┘
```

## Domain Events

A **Domain Event** captures something that happened in the domain that domain experts care about.

### Characteristics

- Named in **past tense** (OrderPlaced, PaymentReceived)
- **Immutable** - facts cannot change
- Contains all relevant data
- Used for loose coupling between aggregates

### Example

```python
@dataclass(frozen=True)
class OrderSubmittedEvent:
    """Domain Event - something that happened"""
    
    order_id: OrderId
    customer_id: CustomerId
    total_amount: Money
    occurred_at: datetime
    
    def __init__(self, order_id: OrderId, customer_id: CustomerId, 
                 total_amount: Money):
        object.__setattr__(self, 'order_id', order_id)
        object.__setattr__(self, 'customer_id', customer_id)
        object.__setattr__(self, 'total_amount', total_amount)
        object.__setattr__(self, 'occurred_at', datetime.utcnow())


# Event Handler
class OrderSubmittedHandler:
    def __init__(self, notification_service: NotificationService,
                 inventory_service: InventoryService):
        self._notifications = notification_service
        self._inventory = inventory_service
    
    def handle(self, event: OrderSubmittedEvent) -> None:
        # Send confirmation email
        self._notifications.send_order_confirmation(event.order_id)
        
        # Reserve inventory
        self._inventory.reserve_for_order(event.order_id)
```

## Repositories

A **Repository** provides a collection-like interface for accessing aggregates.

### Characteristics

- One repository per aggregate root
- Abstracts persistence details
- Returns fully reconstituted aggregates
- Supports querying

### Example

```python
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    """Repository interface in domain layer"""
    
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        pass
    
    @abstractmethod
    def save(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> List[Order]:
        pass


# Implementation in infrastructure layer
class SqlOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        record = self._session.query(OrderRecord)\
            .filter(OrderRecord.id == str(order_id))\
            .first()
        
        if record is None:
            return None
        
        return self._to_domain(record)
    
    def save(self, order: Order) -> None:
        record = self._to_record(order)
        self._session.merge(record)
        self._session.commit()
    
    def _to_domain(self, record: OrderRecord) -> Order:
        """Map from persistence to domain model"""
        # ... mapping logic
        pass
```

## Domain Services

A **Domain Service** encapsulates domain logic that doesn't naturally fit within an entity or value object.

### When to Use Domain Services

| Use Domain Service When | Example |
|------------------------|---------|
| Operation involves multiple aggregates | Transfer money between accounts |
| Logic doesn't belong to any single entity | Calculate shipping cost |
| Stateless operation | Validate business rules |
| External dependency needed | Check credit score |

### Example

```python
class TransferService:
    """Domain Service - stateless, involves multiple aggregates"""
    
    def __init__(self, account_repository: AccountRepository,
                 exchange_service: ExchangeRateService):
        self._accounts = account_repository
        self._exchange = exchange_service
    
    def transfer(self, from_id: AccountId, to_id: AccountId, 
                 amount: Money) -> TransferResult:
        source = self._accounts.find_by_id(from_id)
        destination = self._accounts.find_by_id(to_id)
        
        if source is None or destination is None:
            raise AccountNotFoundException()
        
        # Convert currency if needed
        if source.currency != amount.currency:
            amount = self._exchange.convert(amount, source.currency)
        
        # Domain logic
        source.withdraw(amount)
        
        if destination.currency != amount.currency:
            amount = self._exchange.convert(amount, destination.currency)
        
        destination.deposit(amount)
        
        # Save both aggregates
        self._accounts.save(source)
        self._accounts.save(destination)
        
        return TransferResult.success(from_id, to_id, amount)
```

## Factories

A **Factory** encapsulates complex object creation logic.

### When to Use Factories

- Complex construction logic
- Creating aggregates with many parts
- Need to enforce invariants during creation
- Want to hide implementation details

### Example

```python
class OrderFactory:
    """Factory for creating Order aggregates"""
    
    def __init__(self, id_generator: IdGenerator,
                 pricing_service: PricingService):
        self._id_generator = id_generator
        self._pricing = pricing_service
    
    def create_from_cart(self, cart: ShoppingCart, 
                         customer_id: CustomerId) -> Order:
        """Create order from shopping cart"""
        order_id = self._id_generator.generate_order_id()
        order = Order(order_id, customer_id)
        
        for item in cart.items:
            price = self._pricing.get_price(item.product_id)
            order.add_line(item.product_id, item.quantity, price)
        
        return order
    
    def reconstitute(self, record: OrderRecord) -> Order:
        """Reconstitute order from persistence record"""
        # Used by repository to rebuild aggregate from storage
        order = Order.__new__(Order)
        order._id = OrderId(record.id)
        order._customer_id = CustomerId(record.customer_id)
        order._status = OrderStatus(record.status)
        order._lines = [self._reconstitute_line(l) for l in record.lines]
        return order
```

## Modules

**Modules** (packages/namespaces) organize the domain model into cohesive units.

### Module Organization

```
order_context/
├── domain/
│   ├── model/
│   │   ├── order.py          # Order aggregate
│   │   ├── order_line.py     # OrderLine entity
│   │   └── shipping.py       # Shipping value objects
│   ├── events/
│   │   ├── order_submitted.py
│   │   └── order_cancelled.py
│   ├── services/
│   │   └── pricing_service.py
│   └── repositories/
│       └── order_repository.py  # Interface
├── application/
│   ├── commands/
│   │   └── submit_order.py
│   └── handlers/
│       └── submit_order_handler.py
└── infrastructure/
    ├── persistence/
    │   └── sql_order_repository.py  # Implementation
    └── messaging/
        └── event_publisher.py
```

## Putting It All Together

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tactical DDD in Action                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Application Layer                                                  │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  SubmitOrderHandler                                          │   │
│   │    - Orchestrates use case                                   │   │
│   │    - Uses repository to load/save                            │   │
│   │    - Publishes domain events                                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   Domain Layer                                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Order (Aggregate Root)                                      │   │
│   │    │                                                         │   │
│   │    ├── OrderLine (Entity)                                    │   │
│   │    │     └── Money (Value Object)                            │   │
│   │    │                                                         │   │
│   │    ├── Address (Value Object)                                │   │
│   │    │                                                         │   │
│   │    └── raises OrderSubmittedEvent (Domain Event)             │   │
│   │                                                              │   │
│   │  OrderRepository (Interface)                                 │   │
│   │  PricingService (Domain Service)                             │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   Infrastructure Layer                                               │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  SqlOrderRepository (Implementation)                         │   │
│   │  EventPublisher                                              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Common Pitfalls

| Pitfall | Problem | Solution |
|---------|---------|----------|
| **Anemic Domain Model** | Entities are just data containers | Put behavior in entities |
| **Large Aggregates** | Loading entire object graph | Keep aggregates small |
| **Crossing Aggregate Boundaries** | Direct references between aggregates | Use IDs, domain events |
| **Leaking Persistence** | ORM entities in domain | Separate domain from infrastructure |
| **Missing Value Objects** | Primitive obsession | Extract value objects |
| **God Repository** | Repository with too many query methods | Use specifications/CQRS |

## References

- **Domain-Driven Design** - Eric Evans (2003)
- **Implementing Domain-Driven Design** - Vaughn Vernon (2013)
- **Patterns, Principles, and Practices of Domain-Driven Design** - Scott Millett (2015)
- [Effective Aggregate Design](https://www.dddcommunity.org/library/vernon_2011/) - Vaughn Vernon
- [DDD Reference](https://www.domainlanguage.com/ddd/reference/) - Eric Evans
