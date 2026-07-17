---
type: Article
title: "System Design Interview: How Would You Avoid Overselling Inventory During a Flash Sale?"
source: "https://codefarm0.medium.com/system-design-interview-how-would-you-avoid-overselling-inventory-during-a-flash-sale-1cf844eca0b9"
author:
- "[[Arvind Kumar]]"
published: 2026-06-22
created: 2026-07-17
description: "Race conditions, atomic updates, inventory reservation, and Redis-based edge protection for flash-sale inventory management."
tags:
- "clippings"
- "concurrency"
- "system-design"
---

# System Design Interview: How Would You Avoid Overselling Inventory During a Flash Sale?

Flash sales look simple from the customer’s perspective.

A user sees:

```c
Only 100 iPhones Left
```

They click **Buy Now**.

Payment succeeds.

Order confirmed.

Done.

But behind the scenes, thousands of users may be attempting to buy the same item at exactly the same time.

And that’s where things get interesting.

Imagine:

```c
Inventory Available = 100
```

Within the first few seconds:

```c
10,000 Users
```

click **Buy Now**.

The challenge isn’t processing payments.

The challenge is ensuring you never sell:

```c
101st iPhone
```

because once that happens, somebody is going to receive an apology email instead of a phone.

Let’s walk through how large-scale e-commerce platforms solve this problem.

> [Full story for non-members](https://codefarm0.medium.com/1cf844eca0b9?sk=1acffcd00f2ab68f98e075c34f1c6602) | [E-Books on Java/Microservices/Springboot](https://codefarm.in/ebooks) | [Whatsapp Group](https://www.whatsapp.com/channel/0029VbBoxXI5q08aIWZsUE2X)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-L_vOAQqyihmJ3FvbSyFsA.png)

## The Question

**Aadvik:** Imagine we’re running a flash sale for the latest iPhone.

We have exactly:

```c
Units
```

available.

The moment the sale starts:

```c
10,000 Users
```

click **Buy Now**.

How would you prevent overselling inventory?

**Unnati:** Before discussing solutions, I’d like to identify the core problem.

Most people think this is a scaling problem.

> It’s actually a consistency problem.

The challenge isn’t handling 10,000 users.

The challenge is ensuring inventory remains correct while 10,000 users are competing for the same 100 items.

**Aadvik:** What’s the most common mistake engineers make?

**Unnati:** Separating the inventory check from the inventory update.

Something like:

```c
if(stock > 0){
stock--;
}
```

Looks harmless.

But under concurrency it’s broken.

**Aadvik:** Show me.

**Unnati:**

Imagine:

```c
Stock = 1
```

User A arrives.

User B arrives.

At almost the same moment.

Both execute:

```c
SELECT stock
FROM inventory
WHERE product_id = 1;
```

Both receive:

```c
Stock = 1
```

Both proceed.

Both place orders.

Now:

```c
Inventory Sold = 2

Inventory Available = 1
```

We’ve oversold.

## The Root Cause

**Aadvik:** So what’s actually happening?

**Unnati:** A race condition.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9ohxltuHS1x45gXyxZzR4g.png)

Both users observed the same state.

Both made decisions based on stale information.

## Atomic Inventory Updates

**Aadvik:** What’s the simplest fix?

**Unnati:** Make the update atomic.

Instead of:

```c
Read Stock
Check Stock
Update Stock
```

we combine everything into a single operation.

**Aadvik:** Example?

**Unnati:**

```c
UPDATE inventory
SET stock = stock - 1
WHERE product_id = 1
AND stock > 0;
```

Now the database guarantees correctness.

**Aadvik:** Why?

**Unnati:** Because only one transaction can successfully decrement the last item.

Suppose:

```c
Stock = 1
```

Two requests arrive simultaneously.

Request A:

```c
UPDATE inventory
SET stock = stock - 1
WHERE stock > 0;
```

succeeds.

Stock becomes:

```c
0
```

Request B executes immediately afterward.

The condition:

```c
stock > 0
```

fails.

Rows updated:

```c
0
```

Request rejected.

No overselling.

## Is The Problem Solved?

**Aadvik:** Great.

Can we ship it?

**Unnati:** Not yet.

**Aadvik:** Why not?

**Unnati:** Because we haven’t discussed payment.

Imagine:

```c
Stock = 1
```

User reserves it.

Inventory becomes:

```c
0
```

Then payment fails.

Now the product is unavailable even though nobody actually bought it.

## Inventory Reservation

**Aadvik:** How do large platforms solve that?

**Unnati:** By separating:

```c
Reservation
```

from

```c
Purchase
```
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*h1TohVLMUH_EDpW0i8jWXQ.png)

Inventory first moves into a temporary reserved state.

Only after successful payment does it become purchased.

## Reservation Workflow

**Aadvik:** Walk me through it.

**Unnati:**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*BYfn4zSUK8tkgKmcxODRGg.png)

Now inventory isn’t permanently removed until payment succeeds.

## Reservation Expiry

**Aadvik:** What if the customer disappears?

Maybe they abandon checkout.

**Unnati:** Reservations must expire.

For example:

```c
Reservation Timeout = 10 Minutes
```

If payment isn’t completed:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*0xBOCPNHk62ZUeOZ9goN4w.png)

The inventory is released back into the pool.

## The Next Scaling Problem

**Aadvik:** Let’s make this bigger.

Suppose:

```c
100 Units

100,000 Buyers
```

Would you still let every request directly hit the database?

**Unnati:** Probably not.

Now the database itself becomes the bottleneck.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xsNw9YOBQVZUWQCgzsTplg.png)

Even if the database correctly rejects requests, it still has to process every attempt.

That creates enormous pressure.

## Queue-Based Processing

**Aadvik:** What’s a better design?

**Unnati:** Introduce a queue.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*mQ_nCsWcB4jnlIyMVrWkIg.png)

Instead of directly competing for inventory, requests enter a queue.

Workers process them sequentially.

This dramatically reduces contention.

**Aadvik:** Isn’t that slower?

**Unnati:** Slightly.

But it provides fairness and correctness.

For flash sales, correctness matters more than shaving off a few milliseconds.

## The Interview Trap

**Aadvik:** Let’s say we have:

```c
100 Units

100,000 Requests
```

Would you really place all 100,000 requests into Kafka?

**Unnati:** Not necessarily.

Because 99,900 requests have no chance of succeeding.

**Aadvik:** Interesting.

What would you do?

**Unnati:** I’d move inventory protection closer to the edge.

Many flash-sale systems preload inventory into Redis.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FhfaIFj9D4amSRGj-fjXqg.png)

Redis becomes the first gate.

If Redis says:

```c
Stock = 0
```

the request is rejected immediately.

It never reaches Kafka.

It never reaches the database.

## Redis Atomic Decrement

**Aadvik:** How does Redis help?

**Unnati:** Redis supports atomic operations.

Example:

```c
DECR iphone_stock
```

Suppose:

```c
iphone_stock = 100
```

The first 100 requests succeed.

Request 101 receives:

```c
Out Of Stock
```

immediately.

No database involvement.

## What If Redis Crashes?

**Aadvik:** Now I’m worried.

What if Redis crashes after reducing inventory?

**Unnati:** Great question.

Redis should not be the source of truth.

The database remains the source of truth.

Redis is only used for traffic shaping.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*TsGWpTLBYhcqt8fn88DizA.png)

Eventually inventory must be persisted consistently in the database.

## Preventing Duplicate Purchases

**Aadvik:** Another scenario.

A user clicks Buy Now ten times.

Or refreshes repeatedly.

What happens?

**Unnati:** We need idempotency.

Each purchase request should carry:

```c
OrderId

or

Purchase Token
```

Duplicate requests return the existing result instead of creating new reservations.

Exactly, the same principle we use in [payment systems](https://medium.com/javarevisited/system-design-interview-how-would-you-prevent-a-payment-from-being-processed-twice-724aded39642).

## Multi-Region Challenge

**Aadvik:** Let’s say inventory is sold globally.

US, Europe, and Asia all participate.

Any concerns?

**Unnati:** Absolutely.

Inventory becomes globally shared state.

![](https://miro.medium.com/v2/resize:fit:1180/format:webp/1*wt1ggsK_ZSDME_MmliPtOg.png)

Now consistency becomes critical.

The system must ensure:

```c
Total Sold <= Total Inventory
```

across all regions.

This often leads to inventory partitioning, centralized allocation, or inventory tokens.

## The Real Production Design

**Aadvik:** If you were designing a modern flash-sale platform, what would the architecture look like?

**Unnati:**

![](https://miro.medium.com/v2/resize:fit:1380/format:webp/1*wyhwfKvM_kgJxdzAAKdaww.png)

Each layer solves a different problem.

- Redis absorbs traffic spikes.
- Queue ensures controlled processing.
- Reservation prevents payment failures from consuming inventory permanently.
- Database maintains correctness.
- Idempotency prevents duplicate purchases.

## Lets Conclude

**Aadvik:** Summarize your solution.

**Unnati:**

1. Never separate inventory checks from inventory updates.
2. Use atomic inventory decrements.
3. Introduce inventory reservations.
4. Release reservations when payment expires.
5. Use queues during flash-sale traffic spikes.
6. Use Redis to reject impossible purchases early.
7. Keep the database as the source of truth.
8. Make purchase requests idempotent.
9. Design assuming tens of thousands of concurrent buyers.

The challenge isn’t handling thousands of users.

The challenge is ensuring that when the last iPhone is sold, every remaining user receives a rejection — not a confirmation email.

That’s what separates a scalable flash-sale platform from a customer support nightmare.

> *Liked this deep dive story? If Yes Please* ***👏 Clap(50)*** *|* ***📤 Share*** *|* ***🔔 Follow***

***Below is a collection of all related stories in one place***

## [List: 15 System Design Interview Scenarios | Curated by Arvind Kumar | Medium](https://codefarm0.medium.com/list/15-system-design-interview-scenarios-23f298ce71ad?source=post_page-----1cf844eca0b9---------------------------------------)

### 15 System Design Interview Scenarios · 15 System Design Interview Scenarios which are absolute must if you are going…

codefarm0.medium.com