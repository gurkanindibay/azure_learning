---
type: Reference
title: "Data, Concurrency & Transactions"
description: "The four guarantees of a reliable database transaction:"
timestamp: 2026-06-14T00:00:00Z
---

# Data, Concurrency & Transactions

> **Domain**: Database transactions, isolation levels, locking, distributed transactions, and sharding.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| ACID Transactions | [`#acid-transactions`](#acid-transactions) |
| Isolation Levels | [`#isolation-levels`](#isolation-levels) |
| Double-Booking Problem | [`#double-booking-problem`](#double-booking-problem) |
| Pessimistic Locking | [`#pessimistic-locking`](#pessimistic-locking) |
| Optimistic Locking | [`#optimistic-locking`](#optimistic-locking) |
| Fencing Token | [`#fencing-token`](#fencing-token) |
| Saga Pattern | [`#saga-pattern`](#saga-pattern) |
| Sharding | [`#sharding`](#sharding) |

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

**Also see**: [Optimistic Locking](#optimistic-locking)

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
