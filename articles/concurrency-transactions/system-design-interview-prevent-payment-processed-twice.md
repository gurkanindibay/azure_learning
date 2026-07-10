---
type: Article
title: "System Design Interview: How Would You Prevent a Payment from Being Processed Twice?"
description: "Interview walkthrough covering idempotency keys, business vs. retry identity, atomic persistence, gateway transaction references, and layered duplicate protection in payment systems."
source: "https://medium.com/javarevisited/system-design-interview-how-would-you-prevent-a-payment-from-being-processed-twice-724aded39642"
author:
  - "[[Arvind Kumar]]"
published: 2026-06-17
created: 2026-07-10
tags:
  - "clippings"
---

# System Design Interview: How Would You Prevent a Payment from Being Processed Twice?

There are some system design questions that look deceptively simple.

This is one of them.

Most engineers hear the question and immediately answer:

> *“Use an idempotency key.”*

That’s not wrong.

But it’s also not the complete answer.

In a real interview, mentioning idempotency keys is usually where the discussion starts, not where it ends.

An experienced interviewer will keep digging:

- How is the key generated?
- Who generates it?
- What happens if two requests arrive simultaneously?
- What if the payment gateway succeeds but your service crashes?
- What if the client sends a different key for the same order?
- What happens in a microservices architecture?
- What if Kafka delivers the same event twice?

Let’s walk through one such interview discussion.

> [Full story for non-members](https://codefarm0.medium.com/724aded39642?sk=a5066c685cdc63fd7b92a87c11c23416) | [E-Books on Java/Microservices/Springboot](https://codefarm.in/ebooks) | [Whatsapp Group](https://www.whatsapp.com/channel/0029VbBoxXI5q08aIWZsUE2X)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Z2g29cjGft6zSyM5r3wsCw.png)

> Check the short video explanation — [link](https://www.instagram.com/reel/DZr8qBmxZMx/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA%3D%3D)

## The Question

**Aadvik:** Let’s say we’re building an online payment platform.

A customer clicks **Pay Now**.

The payment gateway successfully processes the payment.

However, before the response reaches the client, the request times out.

The customer doesn’t know whether the payment succeeded and clicks **Pay Now** again.

How would you prevent the customer from being charged twice?

**Sara:** Before discussing solutions, I’d like to identify the real problem.

The problem isn’t duplicate clicks.

The problem is uncertainty.

The payment may have succeeded, but the client doesn’t know that.

Whenever a distributed system enters an uncertain state, retries become inevitable.

The challenge is making retries safe.

**Aadvik:** Fair enough.

What’s your solution?

**Sara:** I’d introduce idempotency.

Every payment attempt should carry an identifier that remains unchanged across retries.

The server can then recognize whether it’s seeing a new request or a retry of an existing one.

**Aadvik:** Who generates this identifier? The client or the server?

**Sara:** Usually the client.

The client is the component performing the retry, so it must have a stable identifier that it can reuse.

**Aadvik:** How exactly would you generate it?

**Sara:** There are two common approaches.

The first approach is generating a unique identifier for the payment attempt.

For example:

```c
String idempotencyKey = UUID.randomUUID().toString();
```

The important detail is that the key is generated once for the payment attempt and reused for every retry.

**Aadvik:** But every payment attempt gets a new UUID.

Could we derive the key from payment attributes instead?

Something like:

```c
customerId + orderId + amount + currency
```

**Sara:** Yes, that’s another valid approach.

For example:

```c
String rawValue =
        customerId +
        orderId +
        amount +
        currency;
```
```c
String idempotencyKey =
        sha256(rawValue);
```

Now every retry automatically generates the same key because the payment attributes remain unchanged.

**Aadvik:** That sounds better. Why don’t we always do that?

**Sara:** Because business semantics become complicated.

Imagine:

```c
OrderId = ORD-1001
Amount = ₹1000
```

The customer attempts payment.

The payment fails.

Five minutes later, the customer tries again using a different payment method.

Should this be considered:

- the same payment attempt?
- a new payment attempt?

Different businesses answer that question differently.

Once the idempotency key is derived from business attributes, duplicate detection becomes tightly coupled with business rules.

**Aadvik:** So what do payment systems typically do?

**Sara:** Most mature payment systems separate two concepts.

### Business Identity

Examples:

```c
OrderId
PaymentIntentId
BookingId
InvoiceId
```

### Retry Identity

Example:

```c
IdempotencyKey
```

These solve different problems.

The business identifier represents what the customer is paying for.

The idempotency key represents a particular execution attempt that may be retried.

**Aadvik:** Walk me through the request flow.

**Sara:**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*zMndYRrlREWQxAml_DnqQA.png)

The first request executes normally.

Now let’s see what happens when the client retries.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*U85V-stHyBV_7KMdI-Zp3g.png)

The payment is not executed again.

The previously stored result is returned.

**Aadvik:** Where would you store the idempotency key?

**Sara:** Most commonly in a database.

For example:

```c
CREATE TABLE payment_requests (
    idempotency_key VARCHAR(255) UNIQUE,
    order_id VARCHAR(255),
    status VARCHAR(50),
    response JSON,
    created_at TIMESTAMP
);
```

The unique constraint is critical.

Without it, duplicate requests can still slip through.

**Aadvik:** Suppose I implement it like this:

```c
if (!exists(key)) {
    processPayment();
    save(key);
}
```

Would that work?

**Sara:** No. That implementation contains a race condition.

**Aadvik:** Explain.

**Sara:** Imagine two identical requests arrive at the same time.

Both contain the same idempotency key.

Thread A executes:

```c
exists(key)
```

and receives:

```c
false
```

Before it inserts anything, Thread B also executes:

```c
exists(key)
```

and receives:

```c
false
```

Now both requests proceed to process the payment.

The customer gets charged twice.

**Aadvik:** How would you fix it?

**Sara:** The operation must be atomic.

Instead of:

```c
Check
Then Insert
```

we do:

```c
Insert
Or Fail
```

For example:

```c
INSERT INTO payment_requests (
    idempotency_key
)
VALUES (
    ?
);
```

The unique constraint guarantees only one request succeeds.

The winner processes the payment.

The loser retrieves the existing result.

**Aadvik:** Let’s make it harder.

Suppose the payment gateway successfully charges the customer.

Immediately after that, our service crashes.

The result never gets stored.

What happens now?

**Sara:** That’s one of the most important failure scenarios.

![](https://miro.medium.com/v2/resize:fit:1212/format:webp/1*W3ln1H6mJlOOzu7DuFSD9g.png)

When the customer retries, the idempotency table may not contain any record.

At first glance, the system may attempt to charge the customer again.

**Aadvik:** So how do real payment systems avoid this?

**Sara:** By introducing another layer of protection.

A merchant transaction identifier.

For example:

```c
ORDER-1001
```

Every request sent to the payment gateway includes this identifier.

If the service retries after a crash, the same transaction ID is sent again.

The gateway recognizes that it has already processed:

```c
ORDER-1001
```

and returns the existing result instead of charging again.

This protects us even if our own service loses state.

**Aadvik:** Earlier you mentioned business identifiers and idempotency keys separately.

Can you explain why that’s important?

**Sara:** Absolutely.

Consider this scenario.

First request:

```c
OrderId = ORD-1001
IdempotencyKey = abc123
```

Later, because of a client bug:

```c
OrderId = ORD-1001
IdempotencyKey = xyz789
```

These are different idempotency keys.

From the idempotency system’s perspective, they look like two completely different operations.

Without additional safeguards, both requests could be processed.

That’s why many payment systems also enforce uniqueness at the business level.

For example:

```c
CREATE UNIQUE INDEX idx_order_id
ON payments(order_id);
```

Even if the client generates a different idempotency key, the same order cannot be charged twice.

**Aadvik:** So there are multiple protection layers?

**Sara:** Exactly.

![](https://miro.medium.com/v2/resize:fit:1212/format:webp/1*HSDJavAjnj1uj0sCyHoX1A.png)

Each layer protects against a different failure mode.

No single mechanism is sufficient by itself.

**Aadvik:** Let’s move to microservices.

Suppose payment succeeds and an event is published.

What changes?

**Sara:** Now duplicate requests aren’t the only concern.

Duplicate events become a concern too.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*1P8rSTaqRW_NDjWNtJOM4g.png)

Kafka may deliver the same event more than once.

If downstream services aren’t idempotent:

- Rewards may be credited twice.
- Ledger entries may be duplicated.
- Customers may receive duplicate notifications.

Every consumer must implement duplicate protection.

**Aadvik:** Final question.

Can we truly achieve exactly-once processing?

**Sara:** Not literally.

Distributed systems operate in an environment where retries are unavoidable.

Requests can be delivered multiple times.

Messages can be delivered multiple times.

What we actually achieve is:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*gEGHMprzRD7cRioOGXUXhQ.png)

We don’t stop duplicates from arriving.

We ensure duplicates produce the same outcome.

That’s how modern payment systems achieve exactly-once payment behavior.

## Interview Summary

**Aadvik:** Summarize your solution.

**Sara:**

1. Use an idempotency key for retry protection.
2. Reuse the same key across retries.
3. Store keys using atomic operations.
4. Return the previous response for duplicate requests.
5. Maintain a business identifier such as OrderId or PaymentIntentId.
6. Use transaction references with external payment gateways.
7. Make downstream consumers idempotent.
8. Assume retries, crashes, and duplicate messages will happen.

The goal isn’t preventing retries.

The goal is ensuring that no matter how many retries occur, the customer is charged exactly once.

> *Liked this deep dive story? If Yes Please* ***👏 Clap(50)*** *|* ***📤 Share*** *|* ***🔔 Follow***

***Below is a collection of all related stories in one place***

## [List: 15 System Design Interview Scenarios | Curated by Arvind Kumar | Medium](https://codefarm0.medium.com/list/15-system-design-interview-scenarios-23f298ce71ad?source=post_page-----724aded39642---------------------------------------)

### 15 System Design Interview Scenarios · 15 System Design Interview Scenarios which are absolute must if you are going…

codefarm0.medium.com