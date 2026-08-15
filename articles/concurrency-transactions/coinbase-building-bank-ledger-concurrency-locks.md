---
type: Article
title: "Coinbase Interview Question — Building a Bank Ledger: Concurrency, Locks, and Race Conditions"
description: "A comprehensive breakdown of bank ledger concurrency: lost updates, deadlocks, race conditions, atomic updates, lock ordering, optimistic vs pessimistic locking, append-only ledgers, and idempotency."
source: "https://medium.com/@emilyhustlenyc/coinbase-interview-question-building-a-bank-ledger-concurrency-locks-and-race-conditions-75eeb1a80e45"
author:
  - "[[Emily]]"
published: 2026-08-08
created: 2026-08-15
tags:
  - "concurrency"
  - "transactions"
  - "fintech"
  - "system-design"
  - "clippings"
---

# Coinbase Interview Question — Building a Bank Ledger: Concurrency, Locks, and Race Conditions

Two transfers fire in the same millisecond. Alice sends Bob 100 dollars. Bob sends Alice 100 dollars. Both succeed. Both accounts end up with the wrong balance, 100 dollars exists that did not exist before, and not a single error appears in your logs.

That is the version of this bug that gets caught, eventually, by an accountant. The version that does not get caught is worse.

I picked this one up as a Coinbase question: [**Design a bank account ledger**](https://prachub.com/interview-questions/design-a-bank-account-ledger?utm_source=medium&utm_campaign=v1012).

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*TtEgAHqzq0tCl79skl0iDQ.png)

It looks like a CRUD exercise for about first 90 seconds, which is roughly how long it takes before someone asks what happens when two transfers touch the same account at once. Everything interesting in this problem lives in that question.

What follows is the whole thing, built up one approach at a time. Every approach fixes the previous one and introduces a new problem. That progression is the actual content, because it is also what the interview is.

## Table of Contents

- [A Real Problem, and Three Different Races](#a-real-problem-and-three-different-races)
- [Part 1: The Schema, and the One Decision People Get Wrong Before They Start](#part-1-the-schema-and-the-one-decision-people-get-wrong-before-they-start)
- [Part 2: The Ladder](#part-2-the-ladder)
  - [Approach 1: Read, Modify, Write (Broken)](#approach-1-read-modify-write-broken)
  - [Approach 2: The Atomic Update Most People Skip Past](#approach-2-the-atomic-update-most-people-skip-past)
  - [Approach 3: Pessimistic Locking, and the Deadlock It Hands You](#approach-3-pessimistic-locking-and-the-deadlock-it-hands-you)
  - [Approach 4: Lock Ordering](#approach-4-lock-ordering)
  - [Approach 5: Optimistic Locking, and the Hot Row](#approach-5-optimistic-locking-and-the-hot-row)
  - [Approach 6: Stop Updating Balances Entirely](#approach-6-stop-updating-balances-entirely)
  - [Approach 7: Making Derived Balances Fast Again](#approach-7-making-derived-balances-fast-again)
- [Part 3: Idempotency, Which Is Not a Locking Problem](#part-3-idempotency-which-is-not-a-locking-problem)
- [Part 4: When the Two Accounts Live on Different Shards](#part-4-when-the-two-accounts-live-on-different-shards)
- [Part 5: Trade-offs, Side by Side](#part-5-trade-offs-side-by-side)
- [Key Takeaways](#key-takeaways)
- [Homework](#homework)

---

## A Real Problem, and Three Different Races

Most write-ups of this problem treat “concurrency” as one thing with one fix. It is three separate failures with three different fixes, and conflating them is the single most common way this interview goes sideways.

### Race 1: The Lost Update

Alice has 500 dollars. Two withdrawals of 100 arrive at once.

```sql
T1: SELECT balance FROM accounts WHERE id = 1   ->  500
T2: SELECT balance FROM accounts WHERE id = 1   ->  500
T1: UPDATE accounts SET balance = 400 WHERE id = 1
T2: UPDATE accounts SET balance = 400 WHERE id = 1
```

Alice withdrew 200 and has 400 dollars. The bank invented 100 dollars.

Here is the part worth saying out loud, because it is the belief that causes this bug in production: **wrapping both statements in a transaction does not fix this.** At `READ COMMITTED`, which is the default in Postgres and effectively the default everywhere, both transactions legally read 500. They are not violating isolation. They are doing exactly what you asked. A transaction gives you atomicity, not mutual exclusion, and those are not the same guarantee.

### Race 2: The Deadlock

You fix race 1 with locks. Now Alice pays Bob while Bob pays Alice.

```text
T1 (A -> B):  locks account A, waits for B
T2 (B -> A):  locks account B, waits for A
```

Neither transaction is wrong. Both are textbook correct. They will wait for each other until the database’s deadlock detector kills one of them, which in Postgres is after `deadlock_timeout`, defaulting to one full second. Under real load this is not an occasional error, it is a latency cliff, and it gets worse exactly when traffic gets heavier.

### Race 3: The Double Spend

A client sends a transfer, the response times out somewhere in the network, the client retries. Two transfers exist. Both are individually valid. Both locked correctly. Both committed correctly.

This one matters because **no amount of locking fixes it.** Race 3 is not a mutual exclusion problem, it is an identity problem: the system cannot tell that two requests mean the same thing. Candidates who reach for a bigger lock here are solving the wrong problem, and interviewers notice.

Three races. Locks fix the first. Lock ordering fixes the second. Only idempotency fixes the third.

---

## Part 1: The Schema, and the One Decision People Get Wrong Before They Start

```sql
CREATE TABLE accounts (
    id             BIGINT PRIMARY KEY,
    currency       CHAR(3) NOT NULL,
    balance_minor  BIGINT  NOT NULL,
    version        BIGINT  NOT NULL DEFAULT 0
);

CREATE TABLE transfers (
    id               UUID PRIMARY KEY,
    idempotency_key  TEXT UNIQUE NOT NULL,
    from_account     BIGINT NOT NULL,
    to_account       BIGINT NOT NULL,
    amount_minor     BIGINT NOT NULL CHECK (amount_minor > 0),
    state            TEXT   NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE entries (
    id            BIGSERIAL PRIMARY KEY,
    transfer_id   UUID   NOT NULL REFERENCES transfers(id),
    account_id    BIGINT NOT NULL REFERENCES accounts(id),
    amount_minor  BIGINT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Three things in there are load bearing.

**Money is an integer.** `balance_minor` is cents, or paise, or satoshis. Never a float, never a double. Floating point cannot represent 0.10 exactly, and in a system whose entire job is being exactly right about money, "close enough" is the one thing you cannot ship. If a candidate writes `DECIMAL` I move on. If a candidate writes `FLOAT` we are going to have a conversation about it, and that conversation is now the interview.

**Entries are signed, and they come in pairs.** A transfer writes two rows: one negative on the sender, one positive on the receiver. The invariant is that for any `transfer_id`, the entries sum to zero. That is double entry bookkeeping, it is six hundred years old, and it exists precisely because it makes a whole category of bug detectable with one query:

```sql
SELECT transfer_id FROM entries GROUP BY transfer_id HAVING SUM(amount_minor) <> 0;
```

Any row that comes back is corruption. In production this runs continuously and pages someone.

`idempotency_key` **is** `UNIQUE`. Hold that thought, it does more work later than it looks like it should.

---

## Part 2: The Ladder

### Approach 1: Read, Modify, Write (Broken)

```java
long balance = accountDao.getBalance(from);     // 500
if (balance < amount) throw new InsufficientFunds();
accountDao.setBalance(from, balance - amount);  // 400
accountDao.setBalance(to, getBalance(to) + amount);
```

This is race 1, written out. It is also the code running in production somewhere right now.

The window between the read and the write is where the money goes missing. Adding `BEGIN` and `COMMIT` around it does not close the window, for the reason above.

### Approach 2: The Atomic Update Most People Skip Past

Before reaching for locks, notice that the database will do this for you in one statement:

```sql
UPDATE accounts
   SET balance_minor = balance_minor - :amount
 WHERE id = :from
   AND balance_minor >= :amount;
```

There is no window, because there is no read. The row is read and written inside a single statement, and the engine takes the row lock for you for the duration. The balance check rides along in the `WHERE` clause, so **a row count of 0 means insufficient funds**, and you never had to fetch the balance to find out.

I bring this up because a lot of candidates jump straight from “naive” to “distributed lock with Redis” and skip the entire middle of the ladder, where most real systems actually live. Reaching for infrastructure before reaching for the database you already have is a pattern interviewers read as inexperience, and they are usually right.

What this does not solve: you have two accounts to update, so you still have two statements, and two statements in two transactions in opposite orders is still race 2.

### Approach 3: Pessimistic Locking, and the Deadlock It Hands You

```sql
BEGIN;

SELECT id, balance_minor
  FROM accounts
 WHERE id IN (:from, :to)
   FOR UPDATE;

-- business rules here: limits, holds, currency checks, fraud flags

UPDATE accounts SET balance_minor = balance_minor - :amt WHERE id = :from;
UPDATE accounts SET balance_minor = balance_minor + :amt WHERE id = :to;
INSERT INTO entries (transfer_id, account_id, amount_minor) VALUES 
  (:tid, :from, -:amt), 
  (:tid, :to, +:amt);

COMMIT;
```

`FOR UPDATE` takes an exclusive row lock held until commit. Now the whole read-decide-write sequence is serialized per account, and you can put arbitrary business logic in the middle, which the one-line `UPDATE` did not let you do. That flexibility is the real reason to pay for pessimistic locking.

And there is a bug in it that is very easy to miss.

`WHERE id IN (:from, :to)` **does not specify a lock order.** The database locks the rows in whatever order the query plan produces them, which can depend on the index, the statistics, even the direction of a scan. A transfer from account 7 to account 3 and a transfer from account 3 to account 7 can genuinely grab their locks in opposite orders, and then you are in race 2.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*jSDv90Tzj3JCy71m4JwFdA.png)

### Approach 4: Lock Ordering

The fix is to make every transaction in the system acquire account locks in the same order. Ascending account ID is the obvious choice, and any total order works as long as it is genuinely universal.

```sql
SELECT id, balance_minor
  FROM accounts
 WHERE id = ANY(:ids)
 ORDER BY id
   FOR UPDATE;
```

The reason this works is worth stating precisely, because “it avoids deadlock” is a description and the interviewer wants the mechanism: **deadlock requires a cycle in the wait-for graph. If every transaction acquires locks in the same total order, a cycle is impossible**, because a cycle would require some transaction to hold a higher ID while waiting on a lower one, which the ordering forbids. It is not a mitigation that makes deadlock rarer. It is a proof that makes it unreachable.

One caveat that is worth knowing and that almost nobody mentions: `ORDER BY ... FOR UPDATE` is the form you will see everywhere, and in practice Postgres locks in the sorted order, but the ordering is a property of the plan rather than a documented guarantee about lock acquisition. If you want the guarantee rather than the observed behaviour, sort the IDs in application code and lock them one statement at a time:

```java
List<Long> ids = Stream.of(from, to).sorted().toList();
for (Long id : ids) {
    dao.lockAccount(id);   // SELECT ... WHERE id = ? FOR UPDATE
}
```

More round trips, and an ordering you can actually reason about. Which one you pick is a judgement call, but knowing that the difference exists is the part that reads as senior.

Whichever form you use, it has to be universal. Every transaction, including the batch jobs, including the admin tooling, including the migration script someone writes at 2am. One code path that locks in a different order and the proof collapses, and it collapses probabilistically, which means it collapses in production and not in your tests.

The cost: `FOR UPDATE` serializes every transaction touching a hot account. If ten thousand people pay the same merchant during a sale, they queue single file, and your throughput on that account is one over the transaction duration. Which brings us to the next rung, and then to the rung that actually solves it.

### Approach 5: Optimistic Locking, and the Hot Row

Assume conflicts are rare. Detect them instead of preventing them.

```sql
UPDATE accounts
   SET balance_minor = :new_balance,
       version       = version + 1
 WHERE id = :id
   AND version = :version_i_read;
```

Row count 1, you won. Row count 0, someone changed the row underneath you, so throw away your work, re-read, and retry.

Under low contention this beats pessimistic locking, because nobody ever waits. Readers are never blocked. The happy path is a single statement.

Under high contention it is worse, and it is worth being specific about why, because “it does not scale” is not an answer. On a hot row, every concurrent writer reads the same version, one commits, and **every other transaction retries, reads the new version, and collides again.** You have not removed the queue, you have replaced it with a retry storm that also burns CPU and connection pool slots. Latency does not degrade gracefully, it falls off a cliff, and it does so under exactly the load you built the system for.

The honest framing: optimistic locking is correct everywhere and appropriate where conflicts are rare. A consumer’s own checking account is a fine candidate. A merchant settlement account during Black Friday is not.

### Approach 6: Stop Updating Balances Entirely

Here is the move that makes the whole problem class disappear, and it is the one I would most want a candidate to arrive at.

Every approach so far has been a different strategy for safely updating a mutable balance. So do not have one.

```sql
BEGIN;

INSERT INTO transfers (id, idempotency_key, from_account, to_account, amount_minor, state)
VALUES (:tid, :key, :from, :to, :amt, 'POSTED');

INSERT INTO entries (transfer_id, account_id, amount_minor) VALUES
    (:tid, :from, -:amt),
    (:tid, :to,   +:amt);

COMMIT;
```

No `UPDATE`. Anywhere. The balance is not stored, it is derived:

```sql
SELECT SUM(amount_minor) FROM entries WHERE account_id = :id;
```

And now say the sentence that this whole section exists for: **you cannot lose an update if you never update.** Race 1 is gone by construction. Race 2 is gone too, because inserts do not block other inserts, so there is no lock to acquire out of order and no wait-for graph to form a cycle in. Two rungs of the ladder deleted, not mitigated.

You also get something you did not have before. The ledger is append-only, so history is immutable and complete. Every balance the account has ever had is reconstructible. Corrections happen by posting a reversing entry, not by editing the past, which is both a good engineering property and, as it happens, a legal requirement in most of the places this software runs.

Two objections, and you should raise both yourself rather than wait:

1. `SUM` **over ten million rows is slow.** Correct. That is Approach 7.
2. **Overdraft checks need a consistent read.** Also correct, and this is the subtle one. Preventing a balance from going negative means reading the balance and writing an entry atomically with respect to other writers, which is the serialization you just removed. The real answer is not to pretend otherwise. It is holds: post a `HOLD` entry that reserves the funds, and compute available balance as posted balance minus active holds. The hold is itself an insert, so the append-only property survives, and settlement converts the hold into a posted entry later. This is how card authorizations have always worked, and it is why the pending charge on your card is a real thing and not a UI convenience.

For accounts that genuinely must never go negative under any interleaving, you serialize that one account and accept the cost, which is fine, because it is now a decision you make per account rather than an architecture you impose on all of them.

### Approach 7: Making Derived Balances Fast Again

Snapshot periodically, sum the tail.

```sql
CREATE TABLE balance_snapshots (
    account_id      BIGINT PRIMARY KEY,
    as_of_entry_id  BIGINT NOT NULL,
    balance_minor   BIGINT NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL
);

SELECT s.balance_minor + COALESCE(SUM(e.amount_minor), 0) AS current_balance
  FROM balance_snapshots s
  LEFT JOIN entries e
    ON e.account_id = s.account_id
   AND e.id > s.as_of_entry_id
 WHERE s.account_id = :id
 GROUP BY s.balance_minor;
```

A background job advances the snapshot. Reads stay fast because the tail is small. Writes stay contention-free because they are still inserts.

The property that makes this safe, and it is the reason to prefer it over a cached balance column: **the snapshot is an optimization, not a source of truth.** If it is stale, wrong, or deleted entirely, the correct balance is still recoverable by summing entries from zero. A cache you can rebuild from durable truth is a completely different risk profile from a mutable balance you have to keep correct, and that distinction is most of what separates a ledger that survives an incident from one that does not.

---

## Part 3: Idempotency, Which Is Not a Locking Problem

Back to race 3. The client retried and you charged twice.

The fix is the `UNIQUE` constraint from the schema:

```sql
INSERT INTO transfers (id, idempotency_key, from_account, to_account, amount_minor, state) 
VALUES (:tid, :key, :from, :to, :amt, 'POSTED');
```

Second attempt with the same key violates the constraint. Catch it, look up the original transfer, return the original result.

```java
try {
    return postTransfer(key, from, to, amount);
} catch (UniqueViolation e) {
    return transfers.findByIdempotencyKey(key);   // return the ORIGINAL outcome
}
```

Three details separate a working implementation from one that looks like it works:

1. **Return the original result, not an error.** A retry is the client asking “did this happen?” The answer is yes, here is what happened. Returning 409 Conflict makes the client’s retry logic your problem, and their handling of it will be worse than yours.
2. **Scope the key to the caller.** Make it `UNIQUE (api_client_id, idempotency_key)`. Two customers picking the same UUID is unlikely. Two customers both using `order-1001` is common.
3. **Handle the simultaneous case, and understand what actually happens.** People assume the second insert fails immediately. It does not. In Postgres, the duplicate insert **blocks** on the unique index until the first transaction resolves, then either raises the violation (first one committed) or succeeds (first one rolled back). So the second request waits, which is the behaviour you want, and it is worth knowing that the index is doing the serialization for you.

The real edge case is one rung further in. If the transfer is inserted as `PENDING` and committed early, then settled by later work, the retry does not find a missing row. It finds a row that exists but has no outcome yet. Returning that as a success is wrong, and returning it as a failure is also wrong. The retry has to either wait for the terminal state or return a `202`-shaped "in progress, poll here" response, and your API contract has to have a way to say that. This is exactly where a follow-up question lands, and "the row will be there" is not an answer to it.

What I like about this solution is that **the concurrency control is the constraint.** No lock, no Redis, no coordination service. The database’s unique index is already a serialization point with the exact semantics needed, and it is durable, transactional, and free. Reaching for a distributed lock when a unique constraint does the job is the most common overengineering in this problem.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*As6SSk4f5Mv4tooZkSseDw.png)

---

## Part 4: When the Two Accounts Live on Different Shards

Everything above assumed one database. Now the sender is on shard 3 and the receiver is on shard 8, and the single atomic transaction is gone.

**Two-phase commit (2PC):** Correct, and mostly the wrong choice. It holds locks across a network round trip, the coordinator is a failure point, and an in-doubt transaction after a coordinator crash blocks rows until a human intervenes. It exists, it works, and you should be able to say why you are not using it.

**Saga with compensation:** Debit the sender, credit the receiver, and post a compensating credit if the second step fails. Eventually consistent, no distributed locks, no coordinator.

The obvious objection is that between the two steps the money is nowhere, and the books do not balance. And the answer to that is the nicest thing in this entire problem: **give the in-flight money a real account.**

```text
Step 1 (shard 3):  Alice        -100
                   Clearing     +100
Step 2 (shard 8):  Clearing     -100
                   Bob          +100
```

The clearing account is an ordinary ledger account. At every instant, in every partial state, every entry pair still sums to zero and the books still balance. In-flight money is not an inconsistency to be tolerated, it is a balance you can query, alert on, and reconcile against. If the clearing account’s balance is not near zero and trending to zero, something is stuck, and you know within minutes instead of at month end.

That is double-entry bookkeeping solving a distributed systems problem, six centuries after it was invented for a different one.

**Or avoid the problem:** Shard by user/tenant so most transfers land within a single shard. Or route every account to a single-writer partition, so ordering is local and free. Distributed correctness you did not need is still complexity you maintain forever.

---

## Part 5: Trade-offs, Side by Side

| Approach | Fixes | Cost | Use When |
|:---|:---|:---|:---|
| **Read, modify, write** | Nothing | Silent corruption | Never |
| **Atomic conditional UPDATE** | Lost update | No room for multi-step business logic | Simple single-account changes |
| **`SELECT FOR UPDATE`** | Lost update | Serializes hot accounts; deadlocks without ordering | Multi-step logic, low contention |
| **Lock ordering** | Deadlock | None worth mentioning | Always, wherever multiple locks are acquired |
| **Optimistic versioning** | Lost update, no waiting | Retry storms and latency cliffs on hot rows | Conflicts are genuinely rare |
| **Append-only entries** | Lost update and deadlock structurally | Reads need snapshots; overdrafts need holds | Ledgers, essentially always |
| **Unique idempotency key** | Duplicate submission | Needs a retry path for in-flight/pending states | Every mutating API |
| **Saga + clearing account** | Cross-shard atomicity | Eventual consistency; requires reconciliation | Accounts live on different shards |

---

## Key Takeaways

1. **Concurrency in a ledger is three problems, not one:** Lost updates, deadlocks, and duplicate submissions have three different fixes, and a solution to one is not a solution to another.
2. **A transaction is not a lock:** `BEGIN` and `COMMIT` give you atomicity. At `READ COMMITTED` they do not give you mutual exclusion, and assuming they do is how lost updates reach production.
3. **Lock ordering is a proof, not a mitigation:** A total order on acquisition makes a wait-for cycle unreachable.
4. **The best fix for a class of bug is usually to make the class unreachable:** Append-only entries do not defend against lost updates; they make lost updates undefined.
5. **Derived state you can rebuild beats cached state you must maintain:** A wrong snapshot is a performance problem. A wrong balance column is an incident.
6. **Use the database you already have:** A unique constraint solves idempotency without adding extra coordination infrastructure.
7. **Reach for distribution last:** Most of this problem is solved before introducing a second machine.

---

## Homework

Take the append-only design and add these, in order. Each one breaks something the previous one assumed:

1. **Multi-currency:** Alice holds USD, Bob holds EUR. Where does the exchange rate live, what happens when it moves between quote and settlement, and which account absorbs the difference? *(Hint: it is another clearing account, and it has a name.)*
2. **Reversals:** A transfer needs to be undone three days later. You cannot delete the entries. Write the reversal, and then work out what `SUM` returns for the account's balance as of two days ago.
3. **Overdraft with holds:** Implement the hold and settle flow. Then decide what happens to a hold that is never settled, and what the timeout should be.
4. **The reconciliation job:** Write the queries that would have caught the bug from the first paragraph of this article. There are at least three, and the fastest one to run is not the most thorough one.