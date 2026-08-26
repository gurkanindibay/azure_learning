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
| Append-Only Ledger | [`#append-only-ledger`](#append-only-ledger) |
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
| Lock Contention | [`#lock-contention`](#lock-contention) |
| Lock Ordering | [`#lock-ordering`](#lock-ordering) |
| Lock-Transaction Inversion | [`#lock-transaction-inversion`](#lock-transaction-inversion) |
| Lost Update | [`#lost-update`](#lost-update) |
| Optimistic Locking | [`#optimistic-locking`](#optimistic-locking) |
| Overselling | [`#overselling`](#overselling) |
| Pessimistic Locking | [`#pessimistic-locking`](#pessimistic-locking) |
| Read-Your-Own-Writes | [`#read-your-own-writes`](#read-your-own-writes) |
| Saga Pattern | [`#saga-pattern`](#saga-pattern) |
| Two-Phase Commit (2PC) | [`#two-phase-commit-2pc`](#two-phase-commit-2pc) |
| Sharding | [`#sharding`](#sharding) |
| Gene-Based Sharding | [`#gene-based-sharding`](#gene-based-sharding) |
| Vector Clocks | [`#vector-clocks`](#vector-clocks) |
| Wait-For Graph | [`#wait-for-graph`](#wait-for-graph) |
| CRDT (Conflict-free Replicated Data Type) | [`#crdt-conflict-free-replicated-data-type`](#crdt-conflict-free-replicated-data-type) |
| Impossible State | [`#impossible-state`](#impossible-state) |
| Task Claiming | [`#task-claiming`](#task-claiming) |
| PACELC Theorem | [`#pacelc-theorem`](#pacelc-theorem) |
| Quorum | [`#quorum`](#quorum) |
| Shard Key | [`#shard-key`](#shard-key) |
| Two Generals Problem | [`#two-generals-problem`](#two-generals-problem) |
| Operational Transformation (OT) | [`#operational-transformation-ot`](#operational-transformation-ot) |
| Chandy-Lamport Algorithm | [`#chandy-lamport-algorithm`](#chandy-lamport-algorithm) |
| FOR UPDATE SKIP LOCKED | [`#for-update-skip-locked`](#for-update-skip-locked) |

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

## Append-Only Ledger

An immutable data store architecture where financial or state transitions are recorded strictly as chronological, signed entry rows (inserts) rather than in-place updates. The current state (e.g., account balance) is derived by aggregating historical entries (`SUM(amount)`), eliminating lost updates and lock contention by construction.

### Key Characteristics
- **No in-place updates**: Writes are strictly append-only `INSERT` operations; existing rows are never modified or deleted
- **Complete audit trail**: Full historical lineage and point-in-time reconstructibility are built into the data model
- **Invariant enforcement**: Entries are created in balanced pairs (double-entry bookkeeping) where debits and credits sum to zero
- **Eliminates write-write conflicts**: Concurrent inserts do not block or deadlock on row-level update locks

### When to Use
- Core banking, ledger, and payment accounting systems requiring strict auditability and compliance
- High-write environments where row locks on mutable balances create unacceptable latency and contention
- Systems where historical point-in-time balance reconstruction is a regulatory requirement

### When NOT to Use
- Low-complexity CRUD applications where mutable entities with simple audit logs are sufficient
- Extremely read-heavy workloads without snapshotting or caching infrastructure (where raw aggregation on massive tables would degrade latency)

**Also see**: [Ledger (Double-Entry)](fintech.md#ledger-double-entry), [Balance Snapshot](fintech.md#balance-snapshot), [Lost Update](#lost-update)

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

**Also see**: [Distributed Lock](#distributed-lock), [Fencing Token](#fencing-token), [Lock-Transaction Inversion](#lock-transaction-inversion)

---

## Lock-Transaction Inversion

A distributed concurrency anti-pattern where a distributed lock is released before the underlying database transaction commits. This occurs frequently when mixing distributed locks with declarative transaction management (such as Spring `@Transactional`), creating an unshielded race window where concurrent workers acquire the newly released lock and observe uncommitted or stale database state.

```
❌ Inverted Order:
Acquire Lock → Begin DB Tx → Execute Operations → Release Lock ❌ → DB Commit (Too Late!)
                                                 ▲
                                     [Race Window for Contenders]

✅ Aligned Order:
Acquire Lock → Begin DB Tx → Execute Operations → DB Commit → Release Lock ✅
```

### Key Characteristics
- **Boundary mismatch**: The outer synchronization scope (distributed lock) closes before the inner persistence scope (DB transaction) finishes
- **Invisible in single-threaded tests**: Only manifests under high-concurrency multi-instance load when contested resources are updated
- **Fixed via programmatic transaction wrappers**: Solved by using `TransactionTemplate` or explicit commit callbacks to release the lock in a `finally` block strictly after transaction commit

### When to Use (Awareness / Prevention)
- Designing transactional endpoints that synchronize on distributed locks (coupons, inventory, seat reservation, wallet balances)
- Code reviews for frameworks utilizing proxy-based declarative transactions (`@Transactional`, Python context managers)

### When NOT to Use
- Pure read-only queries with no transactional mutations
- Systems relying solely on database-level row locks (`SELECT ... FOR UPDATE`) where transaction commit automatically releases locks

**Also see**: [Distributed Lock](#distributed-lock), [Double-Booking Problem](#double-booking-problem), [Atomic Conditional Update](#atomic-conditional-update), [Safe Lock Release (Lua Script)](caching.md#safe-lock-release-lua-script)

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

## Gene-Based Sharding

A sharding strategy where a routing "gene" — typically the low-order bits of a user or tenant identifier — is embedded directly into each record's primary key (e.g., a Snowflake ID). This enables **zero-lookup routing**: the shard location is deterministically extracted from the ID itself, without querying an external mapping service.

### Key Characteristics
- **Embedded routing**: Bits 10–21 of a 64-bit Snowflake ID carry the shard gene extracted from `user_id & 0xFFF`
- **Co-location guarantee**: All records sharing the same gene map to the same shard — user-history queries hit exactly one shard
- **Zero-lookup**: Given any record ID, the application computes `(id >> 10) & 0xFFF` to determine the shard — no external index needed
- **Multi-pattern support**: Optimizes the primary access pattern (user-bound queries); secondary patterns (merchant, order-no lookup) use a secondary index

### When to Use
- Order management systems with multiple query patterns where one pattern dominates (~80% of queries)
- When eliminating the latency and operational cost of an external shard-routing service is valuable
- When the ID generation system can be modified to embed routing bits

### When NOT to Use
- When the dominant query pattern changes frequently — the gene is baked into every ID and is expensive to change
- When ID opacity is a hard requirement (embedded genes reveal routing topology)
- When multiple co-location dimensions are equally important — gene-based sharding optimizes for one dimension

### Also see
- [Shard Key](#shard-key) · [Composite Shard Key](databases.md#composite-shard-key) · [Snowflake ID](databases.md#snowflake-id) · [Sharding & Partitioning Strategies](../system-design-architecture/databases/sharding-partitioning-strategies.md)

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

## Lock Ordering

A deterministic concurrency control technique where all transactions acquire locks on multiple resources in a globally agreed-upon total order (such as ascending primary key or resource ID). Because every concurrent transaction acquires resources in identical sequence, circular wait conditions in the transaction wait-for graph become mathematically impossible, eliminating deadlocks.

```sql
-- Acquire row locks in strict ascending ID order
SELECT id, balance_minor
  FROM accounts
 WHERE id = ANY(:sorted_ids)
 ORDER BY id
   FOR UPDATE;
```

### Key Characteristics
- **Mathematical deadlock immunity**: Prevents cycles in the database's wait-for graph by enforcing an acyclic lock dependency tree
- **Universal requirement**: Must be enforced across all code paths, background batch jobs, and administrative scripts touching the resources
- **Application vs database ordering**: Sorting IDs in application code before locking guarantees total ordering independent of query planner optimizations

### When to Use
- Multi-resource transactions (e.g., transferring funds between Account A and Account B, or reserving multiple inventory items)
- Bidirectional concurrent operations where Transaction 1 accesses (A then B) while Transaction 2 accesses (B then A)
- Systems experiencing deadlock errors under high concurrency

### When NOT to Use
- Single-resource mutations where deadlocks are impossible
- Workloads using optimistic concurrency control (OCC) or append-only architectures where exclusive locks are avoided entirely

**Also see**: [Wait-For Graph](#wait-for-graph), [Pessimistic Locking](#pessimistic-locking), [Lock Contention](#lock-contention)

---

## Lost Update

A concurrency race condition where two or more transactions concurrently read the same baseline state, compute a new state independently, and overwrite the row sequentially without mutual exclusion. The later write obliterates the modification made by the earlier transaction without detecting the intervening change.

```sql
-- Lost update scenario under READ COMMITTED:
-- T1 reads balance = 500
-- T2 reads balance = 500
-- T1 writes balance = 400 (deducting 100)
-- T2 writes balance = 400 (deducting 100)
-- Result: 200 withdrawn, but balance shows 400 instead of 300!
```

### Key Characteristics
- **Silent data corruption**: Neither transaction throws an error or fails validation, masking the failure from logs and monitoring
- **Standard isolation vulnerability**: Occurs by default in `READ COMMITTED` isolation because transactions provide atomicity, not mutual exclusion
- **Mitigation spectrum**: Solved via atomic conditional updates, pessimistic locks (`SELECT ... FOR UPDATE`), optimistic locking (`version` checks), or append-only ledgers

### When to Address
- Any read-modify-write workflow involving shared counters, balances, inventory quantities, or state flags
- Financial and billing services where missed updates lead directly to financial loss

### When NOT a Problem
- Workloads using atomic in-place expressions (`UPDATE ... SET val = val + :delta`)
- Systems operating under true `SERIALIZABLE` isolation with retry loops on serialization failures

**Also see**: [Atomic Conditional Update](#atomic-conditional-update), [Optimistic Locking](#optimistic-locking), [Pessimistic Locking](#pessimistic-locking), [Append-Only Ledger](#append-only-ledger)

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

---

## PACELC Theorem

An **extension of the CAP theorem** that addresses its main limitation: CAP only describes the tradeoff during a network **P**artition (P). PACELC asks: "**E**lse" — when there is no partition, what is the tradeoff? The answer: **L**atency vs **C**onsistency. This means every distributed system makes two choices: (1) during a Partition: Availability or Consistency; (2) Else (normal operation): Latency or Consistency.

```
PACELC Decision Matrix:
              ┌─ During Partition (P):
              │   A (Availability) — continue serving, risk inconsistency
              │   C (Consistency)  — block writes, ensure correctness
System ───────┤
              └─ Else (no partition):
                  L (Latency)      — return quickly, risk staleness
                  C (Consistency)  — coordinate, pay latency cost
```

### Key Characteristics
- **Two-dimensional classification**: Systems are PC/EC (strong consistency always), PA/EL (available and fast), or PC/EL (consistent during partitions, fast during normal operation)
- **Explains real-world database behavior**: DynamoDB is PA/EL (highly available, eventually consistent by default). Spanner is PC/EC (strongly consistent always, pays latency cost of TrueTime). Cosmos DB is tunable PA/EL–PC/EC.
- **Bridges theory and practice**: Most candidates can recite CAP but cannot explain why their "strongly consistent" system with read replicas and async replication is actually PA/EL

### When to Use (in system design)
- When justifying database choice: "We chose Cosmos DB with session consistency because our users need read-your-own-writes but can tolerate cross-region staleness"
- When explaining why a system with read replicas cannot claim strong consistency: "Async replication means our secondaries lag; during normal operation we traded consistency (C) for latency (L)"

### When NOT to Use
- In single-node systems — PACELC only applies to distributed (replicated/partitioned) databases
- As a crutch to avoid concrete latency numbers — always quantify: "p99 write latency increases from 5ms to 50ms with synchronous replication"

### Also see
- [CAP Theorem](#cap-theorem) · [Consistency Models](#consistency-models) · [Eventual Consistency](#eventual-consistency) · [Strong Consistency](#strong-consistency) · [Quorum](#quorum)

---

## Quorum

A **minimum number of replicas that must acknowledge a read or write operation** for it to be considered successful in a distributed system. Quorum-based replication uses the formula **R + W > N** to ensure that read and write sets overlap, guaranteeing that at least one replica with the latest data is consulted on every read.

Where:
- **R**: number of replicas that must respond to a read
- **W**: number of replicas that must acknowledge a write
- **N**: total number of replica nodes

### Key Characteristics
- **R + W > N**: guarantees strong consistency — every read sees the latest write because the read and write quorums overlap by at least one node
- **R + W ≤ N**: allows stale reads but reduces latency — reads may hit replicas that haven't received the latest write
- **Tunable**: by adjusting R and W, you trade consistency for latency without changing the replication topology
- **Quorum is per-operation**: a system can use different R/W values for different operations (e.g., strict quorum for payments, relaxed quorum for analytics)

### When to Use
- Distributed databases that need configurable consistency levels (Cassandra, DynamoDB, Cosmos DB)
- Leaderless replication models where any replica can accept writes
- Systems where you need to reason formally about consistency guarantees

### When NOT to Use
- Single-primary replication (master-slave) — the primary is the single source of truth, quorum is unnecessary
- When strong consistency is always required — use synchronous replication or a consensus algorithm (Raft/Paxos) instead
- Very small clusters (N ≤ 2) — quorum provides little benefit over simple primary-backup

### Also see
- [PACELC Theorem](#pacelc-theorem) · [Strong Consistency](#strong-consistency) · [Synchronous Replication](data-architecture.md#synchronous-replication) · [Asynchronous Replication](data-architecture.md#asynchronous-replication)

---

## Read-Your-Own-Writes

A **session-level consistency guarantee** that ensures a user always sees the effects of their own updates after writing — even if other users may observe stale data. It is the minimum consistency level required for any user-facing system where a user expects to see their own changes reflected immediately.

### Key Characteristics
- **Per-session guarantee**: only the writing user is guaranteed to see their own writes; other users may see eventually consistent data
- **Sticky connection**: typically implemented by routing a user's requests to the same replica (session stickiness) or by ensuring the write replica is consulted on subsequent reads
- **Stronger than eventual, weaker than strong**: does not guarantee that User B sees User A's writes — only that each user sees their own

### When to Use
- User profile updates where the user expects to see their change immediately after saving
- Social media posts where the author must see their own post appear, even if followers see it seconds later
- E-commerce shopping carts — the user adding items must see them in their cart right away

### When NOT to Use
- Financial ledgers where all parties must see the same state atomically (use strong consistency)
- Multi-user collaborative editing where everyone must see each other's changes in real time
- Systems where session stickiness is infeasible (stateless serverless functions with no routing affinity)

### Also see
- [Causal Consistency](#causal-consistency) · [Consistency Model](#consistency-model) · [PACELC Theorem](#pacelc-theorem) · [Eventual Consistency](cqrs-event-driven.md)

---

## Wait-For Graph

A directed dependency graph maintained internally by database transaction managers to detect deadlocks. Nodes represent active transactions, and directed edges ($T_1 \to T_2$) indicate that transaction $T_1$ is blocked waiting for a lock currently held by transaction $T_2$.

### Key Characteristics
- **Cycle detection**: A directed cycle in the graph ($T_1 \to T_2 \to T_1$) indicates an unresolvable deadlock
- **Victim termination**: When the database deadlock detector identifies a cycle (after a configurable timeout like Postgres `deadlock_timeout`), it aborts one transaction (the "victim") and rolls it back
- **Acyclic enforcement via lock ordering**: If all transactions acquire locks in total order, incoming edges only point from lower-order to higher-order resources, making cycles structurally impossible

### When to Use / Consider
- Tuning database engine timeout parameters (`deadlock_timeout`, `innodb_lock_wait_timeout`)
- Diagnosing database locks, latency spikes, and aborted transactions under high load

**Also see**: [Lock Ordering](#lock-ordering), [Lock Contention](#lock-contention), [Pessimistic Locking](#pessimistic-locking)

---

## Shard Key

The column or combination of columns used to determine which shard a row belongs to in a horizontally partitioned database. The shard key is the single most important design decision in sharding — a poor choice creates hotspots, cross-shard queries, and migration pain.

### Key Characteristics
- **Routing function**: The shard key is fed into a hash or range function to produce the shard identifier
- **Immutable**: Once chosen, changing the shard key requires a full data migration
- **Query locality**: Queries that include the shard key target a single shard; queries without it must scatter-gather across all shards

### When to Use
- Selecting a shard key during database horizontal scaling design
- Evaluating whether an existing key satisfies dispersion, business relevance, and stability requirements

### When NOT to Use
- When a single-column key cannot satisfy all access patterns — consider a composite shard key or gene-based sharding
- Before understanding the full query workload (at least 80% of queries should include the key)

### Also see
- [Gene-Based Sharding](#gene-based-sharding) · [Sharding](#sharding) · [Composite Shard Key](databases.md#composite-shard-key)

---

## Two Generals Problem

A **fundamental thought experiment in distributed systems** that proves it is impossible for two parties to reach consensus over an unreliable communication channel with absolute certainty. Two generals must coordinate an attack via messengers who may be captured; no finite exchange of messages can guarantee both generals know the other received the plan — there is always a last message whose acknowledgment cannot be confirmed.

### Key Characteristics
- **Unsolvable in the general case**: No protocol can guarantee both parties agree with 100% certainty over an unreliable channel
- **Maps to distributed systems**: Producer-consumer acknowledgment, two-phase commit, and TCP handshakes all face the same fundamental limitation — you can never be certain the last acknowledgment was received
- **Practical mitigation**: Systems accept probabilistic guarantees (timeouts, retries, idempotency) rather than absolute certainty
- **Originally formulated by Akkoyunlu et al. (1975) and named by Jim Gray (1978)**

### When to Use
- Understanding why exactly-once delivery is theoretically impossible in the general case
- Explaining why at-least-once with idempotency is the pragmatic choice over exactly-once
- Designing systems where the uncertainty of acknowledgment is explicitly accounted for

### When NOT to Use
- As an excuse to avoid building idempotency — the theoretical impossibility of perfect coordination is precisely why idempotency is mandatory
- To argue that distributed systems are inherently unreliable and therefore not worth engineering rigorously

### Also see
- [Two-Phase Commit (2PC)](#two-phase-commit-2pc) · [Quorum](#quorum) · [At-Least-Once Semantics](messaging.md#at-least-once-semantics) · [Idempotency](cqrs-event-driven.md#idempotency)

---

## Operational Transformation (OT)

An **optimistic concurrency control and conflict resolution algorithm** designed for real-time collaborative editing (such as Google Docs) where multiple users edit the same text document concurrently over a network without locking.

### Key Characteristics
- **Operation-based representation**: Changes are expressed as atomic operations (e.g., `Insert(pos, char)`, `Delete(pos)`) rather than entire document snapshots
- **Transformation function**: When client operations arrive out of order, the server transforms the incoming operation's index based on previously applied operations ($T(Op_A, Op_B) \rightarrow (Op_A', Op_B')$) to ensure intention preservation
- **Central coordination server**: Requires a single authoritative server to sequence revision numbers and broadcast transformed operations to all connected clients
- **Convergence**: Guarantees that all client documents converge to the identical character string once all operations are received and transformed

### When to Use
- Collaborative rich-text and code editors requiring fine-grained character insertion/deletion synchronization (Google Docs, Etherpad)
- Centralized collaborative environments where client-server latency is low and an authoritative sequencing server exists

### When NOT to Use
- Decentralized, peer-to-peer (P2P) distributed systems without a central server (use Conflict-free Replicated Data Types / CRDTs instead)
- Complex nested non-text data structures where defining mathematical transformation matrix pairs becomes prohibitively complex

### Also see
- [CRDT (Conflict-free Replicated Data Type)](#crdt-conflict-free-replicated-data-type) · [WebSocket](api-design.md#websocket)

---

## Chandy-Lamport Algorithm

A foundational distributed systems algorithm designed by Leslie Lamport and K. Mani Chandy (1985) to capture a **consistent global snapshot** of a running distributed system (both node states and in-flight communication channel states) **without freezing or pausing execution**. It is the theoretical backbone behind distributed checkpointing in modern stream processing engines (such as Apache Flink's Asynchronous Barrier Snapshotting / ABS), distributed debugging, and state recovery.

### Key Characteristics
- **Non-blocking Execution**: The distributed system continues processing live incoming requests and mutating state while the global snapshot is captured asynchronously in the background.
- **Marker-Based Recording**: An initiator node records its local state and sends a special control message (**marker**) along all its outgoing channels. When any process receives a marker for the first time on an incoming channel, it immediately snapshots its own local state and forwards the marker along all outgoing channels.
- **In-Flight Channel State Capture**: To capture in-flight messages without a global clock, a process logs incoming messages received on a channel between the moment it saved its own state and the moment it receives the marker on that specific channel (requires FIFO channel ordering).
- **Causal Consistency**: Guarantees that the captured global snapshot represents a valid, causally consistent system state that satisfies the "happened-before" relation (no effect is recorded without its causal cause).
- **Foundation for Exactly-Once Stream Processing**: Modern stream processors (like Apache Flink) adapt Chandy-Lamport into lightweight barrier alignment algorithms, checkpointing state across operators to provide deterministic exactly-once fault recovery.

### When to Use
- **Distributed State Checkpointing & Savepoints**: Stateful stream processing engines (Apache Flink, Kafka Streams state backends) capturing consistent operator state for recovery.
- **Consistent Global Backups & Recovery**: Distributed databases and storage clusters requiring point-in-time state recovery without taking system downtime.
- **Distributed Deadlock & Termination Detection**: Inspecting stable global properties (e.g., deadlock, token loss, termination) across a distributed network of communicating processes.

### When NOT to Use
- Single-node database engines where local Write-Ahead Logging (WAL) or snapshot isolation (MVCC) provides simpler point-in-time recovery.
- Systems with non-FIFO, unsequenced, or lossy communication channels where marker boundaries cannot be preserved without additional protocol layers.
- Purely stateless distributed services where state is delegated entirely to an external datastore.

### Also see
- [Lamport Clocks](#lamport-clocks) · [Vector Clocks](#vector-clocks) · [Two-Phase Commit (2PC)](#two-phase-commit-2pc) · [Apache Flink](messaging.md#apache-flink) · [Watermarking](messaging.md#watermarking) · [Exactly-Once Semantics](messaging.md#exactly-once-semantics)

---

## FOR UPDATE SKIP LOCKED

A SQL row-level locking extension (supported in PostgreSQL 9.5+, MySQL 8.0+, Oracle, and MS SQL Server via `WITH (READPAST, UPDLOCK)`) that instructs the database engine to acquire exclusive locks only on matching unlocked rows while **silently skipping** any rows currently locked by other concurrent transactions. It transforms a relational database table into a high-throughput, distributed, concurrency-safe work queue without lock contention or serialization bottlenecks.

```sql
UPDATE jobs
   SET state = 'CLAIMED', lease_owner = :worker_id, lease_expires_at = now() + interval '60 seconds'
 WHERE job_id IN (
     SELECT job_id
       FROM jobs
      WHERE state = 'PENDING' AND run_at <= now()
      ORDER BY run_at
      LIMIT 50
      FOR UPDATE SKIP LOCKED
 )
RETURNING *;
```

### Key Characteristics
- **Non-Blocking Contention Resolution**: Unlike standard `FOR UPDATE` (which forces competing transactions to wait and serialize) or `NOWAIT` (which throws serialization errors on lock conflict), `SKIP LOCKED` skips locked rows seamlessly, returning immediately with available rows.
- **Disjoint Batch Allocation**: Multiple competing worker processes can execute the exact same query concurrently and receive mutually exclusive, non-overlapping subsets of pending tasks.
- **Zero External Coordination**: Eliminates the need for dedicated distributed lock managers (e.g., Redis Redlock, ZooKeeper) or separate message brokers when managing persistent work queues in relational databases.
- **Index Dependency**: Must be backed by a selective index (e.g., a partial index `WHERE state = 'PENDING'`); full table scans with `SKIP LOCKED` can lock large index ranges and degrade performance.

### When to Use
- **Distributed Job & Task Queues**: Multiple worker processes polling a relational table for pending tasks (e.g., delayed job schedulers, email dispatchers, payment settlement batches).
- **Work Stealing & Sharded Workers**: Sweeping expired leases or abandoned tasks concurrently without worker collision.
- **Relational Work Queues under Moderate Throughput**: Systems handling thousands of tasks per second directly within PostgreSQL, MySQL, or SQL Server before reaching the scale threshold that justifies dedicated brokers (Kafka/RabbitMQ).

### When NOT to Use
- **High-Throughput Event Streaming**: Workloads requiring tens of thousands to millions of events per second (use Kafka, Event Hubs, or Pulsar).
- **Strict FIFO Processing across Workers**: When strict global chronological ordering must be maintained and skipping a locked row would violate domain invariants (use single-partition queues or keyed partition brokers).
- **Data Warehousing & OLAP**: Analytical batch queries where reading a complete, consistent snapshot of all matching data is required.

### Also see
- [Task Claiming](#task-claiming) · [Pessimistic Locking](#pessimistic-locking) · [Lease-Based Lock](#lease-based-lock) · [Delayed Job Scheduler](architecture-patterns.md#delayed-job-scheduler)
