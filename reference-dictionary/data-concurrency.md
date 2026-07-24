---
type: Reference
title: "Data, Concurrency & Transactions"
description: "Database transactions, isolation levels, locking primitives, and concurrency guarantees."
timestamp: 2026-06-14T00:00:00Z
---

# Data, Concurrency & Transactions

> **Domain**: Database transactions, isolation levels, locking, distributed transactions, and sharding.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| asyncio | [`#asyncio`](#asyncio) |
| ACID Transactions | [`#acid-transactions`](#acid-transactions) |
| Atomic Conditional Update | [`#atomic-conditional-update`](#atomic-conditional-update) |
| Atomic Increment | [`#atomic-increment`](#atomic-increment) |
| Causal Consistency | [`#causal-consistency`](#causal-consistency) |
| Causal Ordering | [`#causal-ordering`](#causal-ordering) |
| Change Data Capture (CDC) | [`#change-data-capture`](#change-data-capture) |
| Compensating Transaction | [`#compensating-transaction`](#compensating-transaction) |
| Deterministic Key | [`#deterministic-key`](#deterministic-key) |
| Distributed Lock | [`#distributed-lock`](#distributed-lock) |
| Double-Booking Problem | [`#double-booking-problem`](#double-booking-problem) |
| Exclusion Constraint | [`#exclusion-constraint`](#exclusion-constraint) |
| Fencing Token | [`#fencing-token`](#fencing-token) |
| Global Interpreter Lock (GIL) | [`#global-interpreter-lock`](#global-interpreter-lock) |
| Inventory Reservation | [`#inventory-reservation`](#inventory-reservation) |
| Isolation Levels | [`#isolation-levels`](#isolation-levels) |
| Lamport Clocks | [`#lamport-clocks`](#lamport-clocks) |
| Lease-Based Lock | [`#lease-based-lock`](#lease-based-lock) |
| Optimistic Locking | [`#optimistic-locking`](#optimistic-locking) |
| Overselling | [`#overselling`](#overselling) |
| Pessimistic Locking | [`#pessimistic-locking`](#pessimistic-locking) |
| Saga Pattern | [`#saga-pattern`](#saga-pattern) |
| Two-Phase Commit (2PC) | [`#two-phase-commit-2pc`](#two-phase-commit-2pc) |
| Sharding | [`#sharding`](#sharding) |
| Vector Clocks | [`#vector-clocks`](#vector-clocks) |
| CRDT (Conflict-free Replicated Data Type) | [`#crdt-conflict-free-replicated-data-type`](#crdt-conflict-free-replicated-data-type) |
| Impossible State | [`#impossible-state`](#impossible-state) |
| Lock Contention | [`#lock-contention`](#lock-contention) |
| Task Claiming | [`#task-claiming`](#task-claiming) |

---

## ACID Transactions

The four guarantees of a reliable database transaction:

| Property | Meaning |
|:---|:---|
| **Atomicity** | All operations succeed or all roll back — no partial commits |
| **Consistency** | Transaction moves database from one valid state to another |
| **Isolation** | Concurrent transactions don't interfere |
| **Durability** | Committed data survives crashes |

**Also see**: [Isolation Levels](#isolation-levels), [Saga Pattern](#saga-pattern)

---

## Atomic Conditional Update

A single SQL `UPDATE` statement that changes a row only if a predicate is still true, relying on the database to guarantee atomicity. The application checks the affected-row count to determine success or failure.

```sql
UPDATE inventory
SET available = false
WHERE room_id = 101 AND available = true;
```

If one row is updated, the booking succeeded; if zero, the resource was already taken.

### Key Characteristics
- Atomic check-and-set in one round trip
- No explicit transaction-level lock required for many scenarios
- Affected-row count tells the application whether it won the race

### When to Use
- Single-row flag flips (for example, `available` → `booked`)
- Low-to-moderate contention where `SELECT ... FOR UPDATE` is unnecessary
- Databases without exclusion-constraint support

### When NOT to Use
- Multi-row or multi-table invariants (use serializable isolation or compensating logic)
- Complex business rules that cannot be expressed in a single predicate

**Also see**: [Pessimistic Locking](#pessimistic-locking), [Optimistic Locking](#optimistic-locking), [Exclusion Constraint](#exclusion-constraint)

---

## Atomic Increment

A database operation that modifies a numeric column in place (e.g., `SET counter = counter + 1`) as a single atomic action, without reading the current value into application memory first. Combined with deduplication, the increment fires only on the first observation of an event, preventing double-counting from retries.

```sql
-- Atomic increment: no read-before-write, no race condition
UPDATE posts SET like_count = like_count + 1 WHERE id = ?;

-- Atomic increment with dedup guard:
-- Track processed eventId in same transaction
INSERT INTO processed_events (event_id) VALUES (?);
UPDATE posts SET like_count = like_count + 1 WHERE id = ?;
```

### Key Characteristics
- **In-place mutation**: The database performs the arithmetic, not the application — eliminates the read-modify-write race window
- **Affected-row count**: Zero rows affected means the WHERE predicate failed (e.g., row deleted), not a duplicate
- **Dedup pairing**: Must be paired with deduplication tracking (idempotency key or event ID) to prevent the same increment from firing twice

### When to Use
- Counter updates in event-driven systems where retries can cause duplicate increments
- Like counts, view counts, and engagement metrics that must remain accurate under at-least-once delivery
- Any numeric column that should be mutated, not overwritten

### When NOT to Use
- When the increment requires complex business logic or conditional branching
- When the counter must be part of a multi-row invariant (use serializable isolation instead)

**Also see**: [Atomic Conditional Update](#atomic-conditional-update), [Idempotency](../cqrs-event-driven.md#idempotency), [Atomic Deduplication](../messaging.md#atomic-deduplication)

---

## Change Data Capture (CDC)

A mechanism that observes and propagates changes made to a database (inserts, updates, deletes) to downstream consumers in near real time, typically by reading the transaction log.

### Key Characteristics
- **Log-based**: reads the database's native transaction log (WAL, binlog) for low overhead
- **Event-driven**: emits change events that downstream systems can consume
- **Decouples producers from consumers**: applications do not need to publish events explicitly

### When to Use
- Triggering downstream workflows after a database commit
- Keeping caches, search indexes, or read models synchronized
- Reliable event emission when the outbox pattern is not in place

### When NOT to Use
- When the database does not expose a transaction log or CDC connector
- As a replacement for transactional business logic; events describe what happened, they do not enforce correctness

**Also see**: [Outbox Pattern](cqrs-event-driven.md#outbox-pattern), [Event-Driven Architecture](cqrs-event-driven.md#event-driven-architecture)

---

## Compensating Transaction

An **undo operation** that reverses the effect of a previously committed step in a distributed transaction. Used by the [Saga pattern](#saga-pattern) when a later step fails and the system cannot rely on a global rollback.

### Key Characteristics
- **Applies to already-committed work** — unlike a database rollback, it is a new business action
- **Must be idempotent** — the same compensation may be retried after a crash
- **Must be deterministic** — given the same original step, it always produces the same reversal
- **May be partial** — some steps (e.g., a notification) cannot be undone, only acknowledged

### Example

```
Step 1: Reserve inventory  →  success
Step 2: Charge payment     →  success
Step 3: Create shipment    →  failure
Compensate: Refund payment →  success
Compensate: Release inventory →  success
```

### When to Use
- Distributed sagas where steps cross service or database boundaries
- Business operations that are irreversible by simple rollback (external payments, inventory reservations)

### When NOT to Use
- Inside a single ACID database transaction (use normal rollback)
- When the business domain has no well-defined reversal semantics

### Also see
- [Saga Pattern](#saga-pattern) · [Idempotency](cqrs-event-driven.md#idempotency)

---

## Distributed Lock

A coordination primitive used across multiple processes or nodes to grant temporary, mutually exclusive access to a shared resource. Implementations include Redis Redlock, ZooKeeper ephemeral sequential nodes, and etcd leases.

> **Key insight**: Distributed locks are **best-effort coordination mechanisms**, not correctness guarantees. They reduce contention and improve latency but cannot enforce long-lived invariants when lease expiry, GC pauses, clock skew, or network jitter occur.

### Key Characteristics
- **Lease-based**: most implementations rely on a TTL or session that can expire
- **Best-effort**: safety depends on timing, fencing tokens, and correct client behavior
- **Useful for**: reducing hot-key contention, preventing thundering herd, deduplicating background jobs

### When to Use
- Non-critical serialization (cache refresh, job deduplication)
- High-contention paths where database locks would be too expensive
- As an optimization layered over already-correct database invariants

### When NOT to Use
- As the sole correctness mechanism for financial or inventory bookings
- When critical-section duration can exceed the lock lease window
- Without a fencing token or equivalent stale-operation guard

**Also see**: [Lease-Based Lock](#lease-based-lock), [Fencing Token](#fencing-token), [Pessimistic Locking](#pessimistic-locking)

---

## Isolation Levels

Controls how transaction changes are visible to other concurrent transactions.

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Performance |
|:---|:---:|:---:|:---:|:---|
| **Read Uncommitted** | ✅ Yes | ✅ Yes | ✅ Yes | Fastest |
| **Read Committed** | ❌ No | ✅ Yes | ✅ Yes | Fast |
| **Repeatable Read** | ❌ No | ❌ No | ✅ Yes | Moderate |
| **Serializable** | ❌ No | ❌ No | ❌ No | Slowest |

> **Fintech default**: Repeatable Read for balance checks; Serializable for ledger posting.

**Also see**: [ACID Transactions](#acid-transactions), [Double-Booking Problem](#double-booking-problem)

---

## Lease-Based Lock

A lock that is valid only for a bounded time window (lease/TTL). The holder must renew the lease before it expires; otherwise the resource becomes available to other contenders.

### Key Characteristics
- Automatic expiry prevents stuck locks after client crashes
- Renewal heartbeats are sensitive to GC pauses, network jitter, and clock skew
- Lease duration is a tradeoff between safety (longer) and throughput/availability (shorter)

### When to Use
- Distributed resource coordination with bounded critical sections
- Environments where clients may fail without releasing locks explicitly

### When NOT to Use
- When the protected operation's duration is unpredictable or can exceed the lease
- As the only guard for correctness-critical invariants

**Also see**: [Distributed Lock](#distributed-lock), [Fencing Token](#fencing-token)

---

## Double-Booking Problem

When two concurrent transactions **check availability and then act**, both seeing "available" before either reserves — resulting in overbooking.

```
TX1: SELECT seats WHERE id=5 → 1 available
TX2: SELECT seats WHERE id=5 → 1 available  (same time)
TX1: UPDATE seats SET booked=true → success
TX2: UPDATE seats SET booked=true → success  ← DOUBLE BOOKING
```

### Solutions

| Strategy | Mechanism | When |
|:---|:---|:---|
| **Pessimistic locking** | `SELECT ... FOR UPDATE` | High contention |
| **Optimistic locking** | Version column + retry on conflict | Low contention |
| **Unique constraint** | Database-level guard | Always (defense in depth) |
| **Serializable isolation** | Database serializes conflicting TXs | Critical financial operations |

**Also see**: [Pessimistic Locking](#pessimistic-locking), [Optimistic Locking](#optimistic-locking), [Isolation Levels](#isolation-levels)

---

## Exclusion Constraint

A PostgreSQL constraint that prevents rows from satisfying a given operator expression at the same time. Commonly used with the `gist` index to prevent overlapping date ranges for the same resource.

```sql
EXCLUDE USING gist (
  room_id WITH =,
  daterange(start_date, end_date) WITH &&
);
```

### Key Characteristics
- Enforces range-based uniqueness (for example, no overlapping bookings)
- Uses a GiST index and operator class (`&&` for range overlap)
- Database-native guarantee, not dependent on application logic

### When to Use
- Booking systems with date ranges (hotel rooms, rental cars, conference rooms)
- Any domain where "no overlap" is the invariant

### When NOT to Use
- Databases that do not support exclusion constraints (use application-level checks or serialized locking instead)
- Simple single-value uniqueness scenarios where a unique constraint is sufficient

**Also see**: [Atomic Conditional Update](#atomic-conditional-update), [Double-Booking Problem](#double-booking-problem)

---

## Fencing Token

A **monotonically increasing token** issued with a distributed lock. The resource server rejects operations with stale tokens, preventing a GC-paused or clock-drifted lock holder from corrupting data.

```
Lock service:  Lock acquired → token: 42
Client:        Write(key, value, token=42)
Resource:      Accept — token 42 ≥ last_seen 41
---
GC pause...
---
Old client:    Write(key, value, token=42)
Resource:      Reject — token 42 < last_seen 43 (another holder already wrote)
```

**Also see**: [Optimistic Locking](#optimistic-locking), [Lease-Based Lock](#lease-based-lock), [Distributed Lock](#distributed-lock)

---

## Optimistic Locking

Assumes conflicts are rare, reads freely, and checks a **version column** at write time. If the version changed, the write fails and the caller retries.

```sql
UPDATE accounts
SET balance = balance - 100, version = version + 1
WHERE id = 123 AND version = 5;
-- If 0 rows updated → conflict → retry
```

| When to Use | When NOT |
|:---|:---|
| Low contention | High contention (too many retries) |
| Read-heavy workloads | Financial limit reservation |
| User profile updates | Monetary balance changes |

**Also see**: [Pessimistic Locking](#pessimistic-locking), [Double-Booking Problem](#double-booking-problem)

---

## Pessimistic Locking

Locks a row **before** reading or writing — other transactions must wait. Use `SELECT ... FOR UPDATE` in PostgreSQL.

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 123 FOR UPDATE;
-- Other TXs trying FOR UPDATE on id=123 wait here
UPDATE accounts SET balance = balance - 100 WHERE id = 123;
COMMIT;
```

| When to Use | When NOT |
|:---|:---|
| High contention on the same rows | Read-heavy, low-contention workloads |
| Financial operations (limit reservation) | Reporting/dashboard queries |
| Money movement | Search/browse endpoints |

**Also see**: [Optimistic Locking](#optimistic-locking), [Double-Booking Problem](#double-booking-problem)

---

## Saga Pattern

A sequence of **local transactions** where each step publishes an event that triggers the next step. If a step fails, **compensating transactions** undo the preceding steps.

| Type | Mechanism |
|:---|:---|
| **Choreography** | Services react to events directly — decentralized |
| **Orchestration** | A central saga orchestrator coordinates steps |

| Step | Success | Compensation (on failure) |
|:---|:---|:---|
| 1. Reserve inventory | `InventoryReserved` | `ReleaseInventory` |
| 2. Charge payment | `PaymentCaptured` | `RefundPayment` |
| 3. Create shipment | `ShipmentCreated` | `CancelShipment` |

**Also see**: [ACID Transactions](#acid-transactions) · [CQRS & Event-Driven](cqrs-event-driven.md#event-driven-architecture)

---

## Sharding

Splitting a database into **independent partitions (shards)** based on a shard key. Each shard holds a subset of data. Enables horizontal scaling beyond single-instance limits.

| Strategy | Mechanism | Use Case |
|:---|:---|:---|
| **Hash sharding** | `hash(key) % N` | Even distribution, no hotspots |
| **Range sharding** | `A-M → shard-1, N-Z → shard-2` | Range queries on the shard key |
| **Geo sharding** | By region | Data locality / compliance |

> **Tradeoff**: Sharding adds operational complexity. Exhaust indexing, caching, read replicas, and vertical scaling first.

**Also see**: [ACID Transactions](#acid-transactions)

---

## Two-Phase Commit (2PC)

A distributed transaction protocol that coordinates multiple participants through a coordinator to achieve an atomic commit. In phase one the coordinator asks every participant whether it can commit; in phase two it instructs all participants to commit or abort.

### Key Characteristics
- **Atomic across participants**: all nodes commit or all abort
- **Blocking**: participants hold locks while waiting for the coordinator's final decision
- **Coordinator is a single point of failure**: if the coordinator crashes after prepare, participants must wait until it recovers

### When to Use
- Strong consistency is non-negotiable across separate databases or services
- Short-lived transactions with a small, known set of participants

### When NOT to Use
- Long-running transactions (locks are held for the duration)
- High-availability paths where coordinator failure would be unacceptable
- Scenarios where eventual consistency and compensations are acceptable — prefer the Saga pattern

**Also see**: [Saga Pattern](#saga-pattern), [Compensating Transaction](#compensating-transaction), [ACID Transactions](#acid-transactions)

---

## CRDT (Conflict-free Replicated Data Type)

A data structure designed so that **concurrent updates on different replicas can be merged automatically without coordination**, while still guaranteeing eventual consistency. CRDTs sidestep the need for locks or consensus during partitions.

### Key Characteristics
- **Conflict freedom**: by construction, all valid merge orders produce the same result
- **Two main families**: state-based (merge whole states) and operation-based (replay operations)
- **Eventual consistency without coordination**: replicas converge after they exchange updates

### When to Use
- Active-active multi-region systems where partitions are expected
- Collaborative editing, counters, shopping carts, presence indicators and flags

### When NOT to Use
- When strong consistency or linearizability is required (e.g., financial balances)
- When the data type cannot be expressed as a CRDT without losing business semantics

**Also see**: [ACID Transactions](#acid-transactions), [CAP Theorem](../reference-dictionary/data-architecture.md#cap-theorem), [Eventual Consistency](cqrs-event-driven.md)

---

## Causal Ordering

A partial ordering guarantee in which events are ordered only if they are causally related (for example, a reply depends on the message it answers). Independent events may be observed in different orders on different replicas.

### Key Characteristics
- Preserves **happens-before** relationships rather than a global total order
- Weaker than linearizability but stronger than eventual consistency
- Does not require synchronized clocks

### When to Use
- Real-time messaging per-conversation order
- Comment threads and collaborative editing
- Systems where global ordering is infeasible

### When NOT to Use
- Financial ledgers requiring a strict total order
- Workflows that require linearizable reads

### Also see
- [Message Ordering](messaging.md#message-ordering) · [Eventual Consistency](cqrs-event-driven.md)

---

## Causal Consistency

A consistency model for distributed systems that guarantees all nodes observe causally related operations in the same order while allowing independent (concurrent) operations to be observed in different orders.

### Key Characteristics
- Preserves **happens-before** relationships between events.
- Weaker than linearizability or serializability, but stronger than eventual consistency.
- Enables higher availability and lower latency than strong consistency.
- Tolerates delayed or out-of-order messages as long as causal dependencies are respected.

### When to Use
- Collaborative editing, comment threads, and real-time messaging.
- Distributed databases and event-sourced systems where only related events must be ordered.
- Scenarios where a global total order is unnecessary or too expensive.

### When NOT to Use
- Financial or inventory systems requiring a strict total order of all events.
- Use cases requiring linearizable reads and writes across all nodes.

### Also see
- [Causal Ordering](#causal-ordering) · [Consistency Model](#consistency-model) · [Vector Clocks](#vector-clocks)
- Azure implementation: [Azure Cosmos DB consistency levels](../architecture-azure/data/databases/azure_cosmosdb/cosmosdb_consistency_levels.md) — Session consistency is the closest match (causal-ordering guarantees scoped to a session)

---

## Deterministic Key

A primary key or unique identifier derived from business data (e.g., `SHA256(userId + postId)`) rather than generated randomly or via auto-increment. For idempotent systems, deterministic keys ensure that all retries of the same logical action produce the same key, causing the database to safely reject duplicates via unique constraint violations.

### Key Characteristics
- **Business-derived**: The key is a function of the business identity — same action → same key across all retries
- **Database-enforced uniqueness**: The storage engine, not application code, rejects duplicates
- **Producer responsibility**: The producer must compute the key before the first publish attempt
- **No central coordinator needed**: Each producer independently computes the same key for the same action

### When to Use
- Event-driven systems where at-least-once delivery can produce duplicate messages
- Idempotent write paths where auto-increment keys would silently create duplicate rows
- Systems where the business identity (userId + postId, orderId + version) is stable and known at event creation time

### When NOT to Use
- When the business identity is not known until after the database write (e.g., the DB assigns the ID)
- When the key would be excessively large (hash it instead)

**Also see**: [Idempotency](../cqrs-event-driven.md#idempotency), [Event ID](../cqrs-event-driven.md#event-id), [Atomic Conditional Update](#atomic-conditional-update)

---

## Consistency Model

A contract that defines the rules and ordering guarantees for read and write operations in a distributed or concurrent system.

### Key Characteristics
- Determines what values readers can observe after writers complete.
- Ranges from strong guarantees (linearizability, serializability) to weak guarantees (eventual, causal).
- Directly trades off correctness, latency, availability, and partition tolerance.

### When to Use
- Selecting a database, cache, or messaging system.
- Designing concurrency and replication semantics.

### When NOT to Use
- Do not mix multiple consistency models in the same invariant without explicit handling.

### Also see
- [Causal Consistency](#causal-consistency) · [Isolation Levels](#isolation-levels) · [Eventual Consistency](cqrs-event-driven.md)

---

## Lamport Clocks

Logical timestamps assigned to events in a distributed system to establish a partial ordering of events based on happened-before relationships.

### Key Characteristics
- Each process maintains a monotonic counter.
- The counter increments on local events and is propagated with messages.
- Receivers advance their clock to `max(local, received) + 1`.
- Can determine happened-before relationships but cannot distinguish concurrent events.

### When to Use
- Simple causal ordering when only one-way dependencies matter.
- Distributed logging, debugging, and basic event sequencing.

### When NOT to Use
- When you need to detect concurrency or compare unrelated events precisely (use vector clocks).

### Also see
- [Vector Clocks](#vector-clocks) · [Causal Ordering](#causal-ordering)

---

## Vector Clocks

A mechanism that uses an array of per-process logical counters to track causal dependencies and determine whether two events are ordered or concurrent.

### Key Characteristics
- Each process has its own entry in the vector.
- Local events increment the process's own counter.
- Receiving a message merges vectors by taking element-wise maximums.
- Enables precise detection of happened-before relationships and concurrency.

### When to Use
- Causal consistency implementations.
- Distributed databases, collaborative editing, and event sourcing.
- Conflict resolution where knowing whether events are concurrent is required.

### When NOT to Use
- Systems with a very large number of processes (storage and network overhead grow).
- Systems that only need a simple monotonic ordering (Lamport clocks suffice).

### Also see
- [Lamport Clocks](#lamport-clocks) · [Causal Consistency](#causal-consistency) · [CRDT](#crdt-conflict-free-replicated-data-type)

---

## Inventory Reservation

Temporarily setting aside stock for an in-flight checkout or order, reducing the quantity available to other buyers until the order is confirmed or the reservation expires.

### Key Characteristics
- Usually performed at checkout rather than at cart-add to avoid inventory hoarding
- Paired with a TTL or timeout to release abandoned reservations
- Must be atomic to prevent overselling

### When to Use
- E-commerce checkout flows
- Ticketing, hotel, and rental booking systems

### When NOT to Use
- Low-value items where occasional oversell is acceptable
- Systems without a reliable reservation-expiry mechanism

### Also see
- [Atomic Conditional Update](#atomic-conditional-update) · [Overselling](#overselling) · [Saga Pattern](#saga-pattern)
- **Caution**: the reservation expiry/cleanup mechanism is itself a distributed coordination problem. In multi-replica environments, a naive cron-based cleanup job will run N times and cause duplicate releases. Use leader election, distributed locks, or TTL-based expiration in the data store (Redis `EXPIRE`, `FOR UPDATE SKIP LOCKED`) to ensure only one process releases expired reservations.

---

## Overselling

Selling more units of a product than are actually in stock because concurrent checkouts did not enforce inventory invariants.

### Key Characteristics
- Caused by **check-then-act** races across multiple application instances
- Prevented by atomic conditional updates, pessimistic locking, or database constraints
- Most likely during flash sales and viral traffic spikes

### When to Use
- N/A — overselling is a failure mode to prevent, not a pattern to adopt

### When NOT to Use
- Never acceptable when stock counts are hard business constraints

### Also see
- [Double-Booking Problem](#double-booking-problem) · [Atomic Conditional Update](#atomic-conditional-update) · [Inventory Reservation](#inventory-reservation)

---

## asyncio

Python’s standard-library **asynchronous I/O framework** for writing single-threaded concurrent code using coroutines and an event loop.

### Key Characteristics
- **Cooperative multitasking**: coroutines yield control at `await` points, allowing one thread to multiplex many I/O-bound tasks.
- **Single-threaded**: does not bypass Python’s [Global Interpreter Lock](#global-interpreter-lock) for CPU-bound work.
- **Built-in primitives**: `async`/`await`, `asyncio.gather`, `asyncio.Queue`, `asyncio.Lock`.

### When to Use
- High-concurrency I/O-bound services (network clients, web servers, database drivers).
- Many simultaneous connections where each connection spends most of its time waiting.

### When NOT to Use
- CPU-bound workloads — the GIL still serializes Python bytecode execution.
- As a drop-in replacement for threads or multiprocessing without measuring where time is actually spent.

**Also see**: [Global Interpreter Lock](#global-interpreter-lock) · [Pessimistic Locking](#pessimistic-locking)

---

## Global Interpreter Lock

A **mutex** in CPython that ensures only one thread executes Python bytecode at a time. It protects access to Python objects and simplifies memory management, but it prevents true thread-level parallelism for CPU-bound Python code.

### Key Characteristics
- **Per-process**: each Python process has its own GIL.
- **Bytecode-level**: the lock is held around Python bytecode execution, not around native code or I/O syscalls.
- **Workarounds**: multiprocessing (separate processes), C extensions that release the GIL, or rewriting the hot path in a GIL-free language.

### When to Use
- The GIL is not a choice — it is a property of CPython. Design around it when using CPython for CPU-bound concurrency.

### When NOT to Use
- Do not try to "remove" the GIL by adding more threads to a CPU-bound workload.
- Do not assume asyncio solves CPU parallelism; it solves I/O concurrency.

**Also see**: [asyncio](#asyncio) · [Pessimistic Locking](#pessimistic-locking) · [Two-Phase Commit (2PC)](#two-phase-commit-2pc)

---

## Impossible State

A system state that must **never occur under any concurrency, failure, or retry scenario** — negative inventory, orders for nonexistent products, customers charged twice. Preventing impossible states, not maximizing throughput, is the primary architectural driver of high-traffic transactional systems.

**Scaling handles volume. Impossible-state prevention handles correctness. They are orthogonal problems.**

### Key Characteristics
- **Cross-component**: impossible states arise from disagreement between independently-deployed services, not from bugs in any single service.
- **Not a happy-path concern**: the happy path is easy. Every edge case — retry, timeout, crash, partition — can produce a path into an impossible state.
- **Design inversion**: design from the impossible states outward. For each component, ask "what state must never exist here?" and build the guardrail that prevents it.
- **Observable**: impossible states must be detectable. If you can't monitor for them, you can't be confident they're prevented.

### When to Use
- E-commerce checkout and inventory management
- Payment and financial transaction systems
- Any system where duplicate or phantom records cause real money loss

### When NOT to Use
- Read-heavy, eventually-consistent workloads where occasional duplicates are tolerable
- Systems where all state is fully reconstructable from an authoritative source

### Also see
- [Double-Booking Problem](#double-booking-problem) · [Overselling](#overselling) · [Inventory Reservation](#inventory-reservation) · [Idempotency](../../reference-dictionary/cqrs-event-driven.md#idempotency)

---

## Lock Contention

A performance bottleneck that occurs when **multiple threads compete for the same lock**. While one thread holds the lock, all other threads block — serializing execution that was intended to be parallel. High contention can make a multi-threaded program slower than its single-threaded equivalent.

### Key Characteristics
- **Serialization point**: the lock becomes a choke point — throughput is bounded by the critical section duration.
- **Amplified by lock granularity**: coarse-grained locks (e.g., one lock for an entire data structure) increase contention; fine-grained locks reduce it but add complexity.
- **Measurable**: high lock contention shows up as thread blocking time in profilers and elevated context-switch rates.

### When to Use
- The term is diagnostic. When profiling reveals threads spending significant time waiting for locks, reduce contention by: shrinking critical sections, using lock-free data structures, or switching to an actor/event-loop model.

### When NOT to Use
- Do not add more threads to a lock-contended system — it makes the problem worse.
- Do not confuse lock contention with correctness bugs (race conditions).

### Also see
- [Race Condition](../concurrency-runtimes.md#race-condition) · [Mutex](../dotnet-multithreading.md#mutex) · [Pessimistic Locking](#pessimistic-locking) · [Actor Model](../architecture-patterns.md#actor-model)

---

## Task Claiming

### task-claiming

A distributed coordination pattern where multiple workers compete for tasks by atomically updating a shared state in the database. The worker whose UPDATE succeeds owns the task; all others move on. This provides **exactly-once task ownership** without a dedicated message broker or distributed lock service.

```sql
UPDATE sms_tasks
SET status = 'PROCESSING', worker = 'server-3'
WHERE id = ? AND status = 'PENDING';
```

If zero rows are updated, another worker already claimed the task.

### Key Characteristics
- **Atomic guard**: the `WHERE status = 'PENDING'` clause acts as an optimistic lock — only one worker can transition the row from PENDING to PROCESSING
- **Database as coordination point**: no additional infrastructure needed beyond the existing database
- **Self-healing**: stuck PROCESSING tasks can be recovered by a scheduled job that resets tasks older than a timeout back to PENDING
- **Row-level locking**: the UPDATE acquires a brief row lock; at very high throughput this can create database contention

### When to Use
- Batch processing across multiple application servers where a message broker is not available
- Work-queue patterns backed by a relational database (e.g., email delivery, SMS campaigns, report generation)
- As a fallback when the primary message broker is unavailable

### When NOT to Use
- High-throughput systems (>10K tasks/sec) — database contention becomes a bottleneck; use Kafka/RabbitMQ with consumer groups instead
- When tasks are stateless and idempotent (claiming adds unnecessary database writes)
- When the database is already a scaling bottleneck (don't add more load to a struggling DB)

### Also see
- [Optimistic Locking](#optimistic-locking) — the underlying mechanism that makes task claiming atomic
- [Pessimistic Locking](#pessimistic-locking) — the heavier alternative (SELECT FOR UPDATE)
- [Distributed Lock](#distributed-lock) — a more general but heavier-weight alternative
