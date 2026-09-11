---
type: Article
title: "Shopify Replaced Redis With MySQL. The Reason Is a Masterclass in System Design."
source: "https://medium.com/@kanishks772/shopify-replaced-redis-with-mysql-the-reason-is-a-masterclass-in-system-design-8edddfa71abb"
author:
  - "[[The Latency Gambler]]"
published: 2026-09-08
generated: { by: process:format-agent, at: 2026-09-11T00:00:00Z }
description: "How Shopify eliminated cross-system inventory reservation dual-write hazards by replacing Redis with MySQL 8 FOR UPDATE SKIP LOCKED and a bounded unit-level working pool."
tags:
  - clippings
  - databases
  - mysql
  - redis
  - concurrency
  - system-design
---

# Shopify Replaced Redis With MySQL. The Reason Is a Masterclass in System Design.

> **Author**: [The Latency Gambler](https://medium.com/@kanishks772)  
> **Published**: September 8, 2026  
> **Source**: [Medium](https://medium.com/@kanishks772/shopify-replaced-redis-with-mysql-the-reason-is-a-masterclass-in-system-design-8edddfa71abb)  
> **Free Link**: [Medium Friend Link](https://medium.com/@kanishks772/8edddfa71abb?sk=a42311fed35ca0415e84913c884c4e9c)  
> **Domain**: Databases, Concurrency, Locking Primitives, Relational Modeling, High-Throughput Checkout  
> **Related Takeaways**: [40. High-Contention Inventory Reservations: Redis to MySQL Relational Consolidation — Key Takeaways](../../system-design-architecture/databases/40-db-key-takeaways.md)

---

Shopify recently published a write-up on replacing Redis with MySQL for one of the most contention-heavy parts of their stack — inventory reservations at checkout — and it’s one of the cleanest system design stories I’ve read this year. Not because it’s exotic. Because it isn’t. The fix was one database feature, applied to a data model most engineers would never think to reach for.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*k_1mUxH8756NiagBDTsrqA.png)

*AI Generated Image*

Here’s the problem in one sentence: every time someone clicks “Complete purchase,” Shopify has milliseconds to decide whether that last unit is actually still available — and getting it wrong in either direction costs real money. Say yes when it’s gone, and two people bought the same item, which means a cancelled order and an apology email. Say no when it’s actually available, and you just lost a sale that should have happened. At Shopify’s scale — merchants hit a reported $5.1 million in sales per minute at peak on Black Friday 2025 — that’s not a hypothetical edge case, it’s a constant stream of transactions all racing for the same rows.

## The setup that used to exist

For years, the hold on an item during checkout lived in Redis, as a simple counter per item. Reserve a unit, decrement the count. Release it, increment it back. Redis is single-threaded, so those operations never overlap — no double-spend risk there.

The problem was everything else around it. The actual source of truth for inventory — the ledger — lived in MySQL. So a purchase touched two separate systems that had no way to commit together as one atomic operation:

```text
Checkout request
        │
        ▼
 ┌──────────────┐        ┌──────────────┐
 │    Redis     │        │    MySQL     │
 │ reservation  │        │  inventory   │
 │   counter    │        │    ledger    │
 └──────────────┘        └──────────────┘
        │                        │
        └──── no shared transaction ────┘
```

If a payment cleared and the process crashed before both writes landed, you’d end up in one of two bad states: the inventory ledger never got decremented (oversell risk), or the ledger got decremented while the Redis hold stayed in place, hiding stock that actually existed (lost sales). As Shopify grew, that narrow crash window stopped being rare.

## The obvious fix, and why it failed the first time

The obvious move is to put the reservation in MySQL right next to the ledger, so both changes happen inside one ACID transaction. No more cross-system inconsistency.

Shopify tried this once already, using the straightforward version: one row per item, with a quantity column you decrement. It didn’t survive contact with real traffic. During a flash sale, every buyer chasing the same popular item is fighting to lock the exact same row. MySQL only hands that row’s lock to one transaction at a time, so thousands of concurrent checkouts collapse into a single-file line — lock, wait, retry, repeat.

## The actual fix: stop sharing a row

The insight that made this work is almost embarrassingly simple once you see it: instead of one row holding a quantity, give every individual sellable unit its own row. Ten units in stock means ten rows. Reserving three units just means grabbing any three available rows and moving them out of the pool.

```text
Before: one row, one number             After: one row per unit
┌─────────────────────┐                 ┌────┐┌────┐┌────┐┌────┐┌────┐
│ item_id=42  qty=10  │                 │ u1 ││ u2 ││ u3 ││ u4 ││ u5 │  ...
└─────────────────────┘                 └────┘└────┘└────┘└────┘└────┘
   Everyone locks THIS row                Everyone locks a DIFFERENT row
```

That alone doesn’t fully solve it — a naive `SELECT ... FOR UPDATE` against these rows still makes one buyer wait behind another if they happen to select overlapping rows. The piece that removes the wait entirely is a MySQL 8 feature most engineers have never had a reason to use: `SKIP LOCKED`.

Normally, if your query wants a row someone else’s transaction has already locked, it blocks and waits its turn. `SKIP LOCKED` changes that behavior: if a row is locked, MySQL just skips over it and gives you the next available one instead. Nobody queues behind anybody.

```sql
BEGIN;

SELECT id
FROM inventory_units
WHERE product_id = 42
LIMIT 3
FOR UPDATE SKIP LOCKED;

-- move the returned unit rows into a "reserved" state
-- as part of the same transaction

COMMIT;
```

Run this concurrently from 500 different checkout sessions on the same hot product, and instead of 500 transactions queuing for one lock, each one grabs a handful of free rows nobody else has touched yet and commits independently. The contention that killed the single-row design mostly disappears, because there’s no longer a single hot row to contend over.

## Keeping it bounded

One row per unit doesn’t scale cleanly if a product has millions of units — you don’t want a literal million-row table just to represent one SKU’s stock. Shopify’s answer was to cap the working pool at roughly 1,000 rows per item and refill it from the underlying inventory ledger as it drains. Same one-row-per-unit trick, just applied to a bounded, replenished pool instead of the entire quantity at once.

## A minimal Go version of the idea

Here’s a stripped-down illustration in Go — not Shopify’s actual implementation, just my own sketch to show the shape of the pattern, including the bounded refill:

```go
package inventory

import (
	"context"
	"database/sql"
	"fmt"
)

// ReserveUnits grabs up to `qty` free unit rows for a product and marks
// them reserved, all inside one transaction. Returns the reserved row IDs.
func ReserveUnits(ctx context.Context, db *sql.DB, productID int64, qty int) ([]int64, error) {
	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback() // no-op if we commit successfully

	rows, err := tx.QueryContext(ctx, `
		SELECT id FROM inventory_units
		WHERE product_id = ? AND status = 'available'
		LIMIT ?
		FOR UPDATE SKIP LOCKED`, productID, qty)
	if err != nil {
		return nil, err
	}

	var ids []int64
	for rows.Next() {
		var id int64
		if err := rows.Scan(&id); err != nil {
			rows.Close()
			return nil, err
		}
		ids = append(ids, id)
	}
	rows.Close()

	if len(ids) < qty {
		return nil, fmt.Errorf("only %d of %d units available", len(ids), qty)
	}

	if _, err := tx.ExecContext(ctx, buildMarkReservedQuery(ids)); err != nil {
		return nil, err
	}

	return ids, tx.Commit()
}

// refillPoolIfLow tops the bounded working pool back up to poolSize
// by pulling from the ledger, so the table never has to hold every
// unit a product has ever had in stock.
func refillPoolIfLow(ctx context.Context, db *sql.DB, productID int64, poolSize int) error {
	var current int
	err := db.QueryRowContext(ctx, `
		SELECT COUNT(*) FROM inventory_units
		WHERE product_id = ? AND status = 'available'`, productID).Scan(&current)
	if err != nil {
		return err
	}

	if current >= poolSize/2 {
		return nil // pool is healthy, nothing to do
	}

	needed := poolSize - current
	_, err = db.ExecContext(ctx, `
		INSERT INTO inventory_units (product_id, status)
		SELECT ?, 'available' FROM ledger_free_units
		WHERE product_id = ? LIMIT ?`, productID, productID, needed)
	return err
}
```

The interesting part isn’t the SQL syntax — it’s the mental model shift. `FOR UPDATE` alone says "give me these rows, and make everyone else wait." `FOR UPDATE SKIP LOCKED` says "give me whatever's free, and don't make anyone wait on anyone else." That's the whole unlock.

## Why this is worth remembering

This wasn’t a story about needing a fancier database, a distributed lock service, or a bespoke queueing system. It was a story about recognizing that the *shape* of your data model determines whether your database contends with itself. A single counter row is a bottleneck by construction — every writer has to go through the same gate. Splitting that counter into individually lockable rows turns a serial bottleneck into something that parallelizes almost for free, as long as your database gives you a way to skip past what’s already taken.

The bigger takeaway for anyone doing system design interviews or actual production work: before reaching for a new piece of infrastructure, it’s worth asking whether the tool you already run — Postgres, MySQL, whatever’s already in your stack — has a feature you haven’t needed yet that solves the exact shape of your problem. In Shopify’s case, it did. It also let them delete an entire Redis cluster from the picture and get correctness guarantees, in the form of one real ACID transaction, that two separate systems could never give them.

*Source: “We replaced Redis with MySQL for inventory reservations and it scaled,” Shopify Engineering, May 2026.*
