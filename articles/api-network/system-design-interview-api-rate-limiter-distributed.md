---
type: Article
title: "System Design Interview: How Would You Implement an API Rate Limiter in a Distributed Environment?"
source: "https://codefarm0.medium.com/system-design-interview-how-would-you-implement-an-api-rate-limiter-in-a-distributed-environment-6a79f9208305"
author:
  - "[[Arvind Kumar]]"
published: 2026-06-21
created: 2026-06-26
description: "A realistic interview walkthrough of distributed API rate limiting: fixed-window vs sliding-window vs token-bucket, Redis shared counters, Lua atomicity, hot keys, multi-tenant plans, and multi-region tradeoffs."
tags:
  - "clippings"
  - "system-design"
  - "rate-limiting"
  - "api-design"
---

# System Design Interview: How Would You Implement an API Rate Limiter in a Distributed Environment?

Rate limiting is one of those topics that sounds deceptively simple.

Most engineers hear the question and immediately answer:

> *“Store request counts in Redis.”*

That’s not wrong.

But it’s only the beginning.

In a real system design interview, once you mention Redis, the interviewer starts asking tougher questions:

- What happens when requests hit different servers?
- Why not store counters in memory?
- Which rate-limiting algorithm would you choose?
- How do you handle bursts?
- What happens when Redis fails?
- How do you rate limit across regions?
- Should the API Gateway enforce limits or individual services?

Let’s walk through a realistic interview discussion.

> [Full story for non-members](https://codefarm0.medium.com/6a79f9208305?sk=5346f9063f862877b39a6617f51b0309) | [E-Books on Java/Microservices/Springboot](https://codefarm.in/ebooks) | [Whatsapp Group](https://www.whatsapp.com/channel/0029VbBoxXI5q08aIWZsUE2X)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*GfOlCLLLJPdIwKHQpEIHFQ.png)


## The Question

**Aadvik:** Imagine your public API suddenly receives 100,000 requests per second.

Some requests come from legitimate customers.

Others come from bots, scrapers, or abusive clients.

How would you implement rate limiting in a distributed environment?

**Priya:** Before discussing implementation, I’d like to clarify the goal.

Rate limiting isn’t primarily about blocking users.

It’s about protecting shared resources and ensuring fair usage.

Without rate limiting, a single client could consume capacity that should be available to thousands of other users.

**Aadvik:** Fair enough.

What’s the simplest implementation?

**Priya:** A fixed window counter.

For example:

```c
100 requests per minute
```

Every request increments a counter.

Once the counter reaches 100, subsequent requests are rejected.

**Aadvik:** Sounds simple.

How would you implement that?

**Priya:** Something like:

```c
counter++;
```

and reject requests when:

```c
counter > 100
```

within the current minute.

**Aadvik:** Would that work in production?

**Priya:** Not in a distributed system.

**Aadvik:** Why?

**Priya:** Because requests don’t always hit the same server.

Imagine:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*K7J3djHxi5S3P74cdEZMJA.png)

If each server maintains its own counter:

Server 1:

```c
100 requests
```

Server 2:

```c
100 requests
```

Server 3:

```c
100 requests
```

The client has effectively made:

```c
300 requests
```

while every server believes the limit is still:

```c
100 requests
```

The rate limit is no longer accurate.

## Shared State

**Aadvik:** How do we solve that?

**Priya:** The counters must live in a shared datastore.

Most commonly Redis.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*dZI4f-aXkJfNIfmYdilJsw.png)

Every request updates the same counter regardless of which server handles it.

Now all instances share a consistent view of usage.

## Fixed Window Problems

**Aadvik:** Great.

Let’s assume:

```c
100 requests per minute
```

using a fixed window.

Any issues?

**Priya:** Yes.

Boundary problems.

Suppose a user sends:

```c
100 requests at 12:00:59
```

and then:

```c
100 requests at 12:01:01
```

They’ve effectively sent:

```c
200 requests
```

within two seconds.

Yet both windows technically respect the limit.

**Aadvik:** So the limit is correct but still unfair.

**Priya:** Exactly.

That’s one reason many systems move beyond fixed windows.

## Sliding Window

**Aadvik:** What’s the next improvement?

**Priya:** Sliding Window.

Instead of measuring usage in discrete windows, we continuously evaluate activity over the last minute.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Uex4p_f_1WusSHw11f6y7w.png)

This removes abrupt boundary effects.

However, it introduces new challenges.

**Aadvik:** Such as?

**Priya:** Storage and computation.

To implement an exact sliding window, we need timestamps for every request.

At large scale:

```c
100,000 requests/sec
```

that becomes expensive.

## Token Bucket

**Aadvik:** Which algorithm do large systems typically prefer?

**Priya:** Token Bucket.

It’s one of the most widely used algorithms because it supports bursts while still enforcing long-term limits.

**Aadvik:** Explain how it works.

**Priya:** Imagine every client owns a bucket.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*pD8ocR1S2eXz3YZptJn2vQ.png)

Tokens are added continuously.

For example:

```c
10 tokens per second
```

Every request consumes one token.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*C3eizh2wNQaxFkf57J9maw.png)

If the bucket is empty:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Tuzt23pZ2CoPCcqaSjB97A.png)

## Why Is Token Bucket Popular?

**Aadvik:** Why is this better?

**Priya:** Because it allows controlled bursts.

Suppose:

```c
Bucket Capacity = 100
```
```c
Refill Rate = 10/sec
```

If a client hasn’t made requests recently, the bucket fills.

When traffic suddenly spikes:

```c
100 requests
```

can be served immediately.

After that, requests are constrained by the refill rate.

This provides a better user experience than abruptly rejecting every burst.

## Redis Implementation

**Aadvik:** How would you implement Token Bucket using Redis?

**Priya:** Redis gives us two important things:

1. Shared state
2. Atomic operations

The bucket state can be stored as:

```c
userId
tokensRemaining
lastRefillTimestamp
```

Each request:

1. Calculates how many tokens should have been added.
2. Updates the bucket.
3. Consumes a token.
4. Accepts or rejects the request.

All within a Lua script.

**Aadvik:** Why Lua?

**Priya:** Atomicity.

Without Lua:

```c
Read Bucket
```
```c
Update BucketWrite Bucket
```

can suffer race conditions.

Multiple requests may consume the same token.

Lua ensures the entire operation executes atomically.

## The Hot Key Problem

**Aadvik:** Let’s say one API key generates 50,000 requests per second.

Any concerns?

**Priya:** Definitely.

Now Redis becomes a bottleneck.

Every request is updating the same key.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*hvk5x-0efPHkJQdWRJ0BZg.png)

This creates a hot key.

The rate limiter itself becomes the scaling bottleneck.

**Aadvik:** How would you address that?

**Priya:** Options include:

- Sharding
- Local token caches
- Hierarchical rate limiting
- Gateway-level enforcement

The exact solution depends on traffic characteristics.

## Where Should Rate Limiting Live?

**Aadvik:** Should every microservice implement rate limiting?

**Priya:** Usually no.

I prefer enforcing limits at the edge.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*DlUyzN0qEvAnAab6_fObcg.png)

The gateway rejects abusive traffic before it reaches internal services.

This saves compute, database connections, and network bandwidth.

## Multi-Tenant Limits

**Aadvik:** Let’s make it more realistic.

Suppose we offer plans.

Free:

```c
100 req/min
```

Pro:

```c
1000 req/min
```

Enterprise:

```c
Unlimited
```

How would you support that?

**Priya:** The bucket parameters become configurable.

For example:

```c
Free
Capacity = 100
Refill = 100/min
```
```c
Pro
Capacity = 1000
Refill = 1000/min
```

Different users simply receive different bucket configurations.

The algorithm remains identical.

## Redis Failure

**Aadvik:** What happens when Redis goes down?

**Priya:** That’s an important operational decision.

We have two options.

### Fail Closed

```c
Redis Down
```
```c
Reject Requests
```

Protects the platform.

But impacts availability.

### Fail Open

```c
Redis Down
```
```c
Allow Requests
```

Maintains availability.

But risks abuse.

**Aadvik:** Which would you choose?

**Priya:** For customer-facing APIs, most businesses prefer fail-open for a short period.

An outage caused by the rate limiter itself is usually worse than temporarily allowing extra traffic.

## Multi-Region Challenge

**Aadvik:** Let’s say we’re running in:

- US-East
- Europe
- Asia

How does rate limiting work now?

**Priya:** Now we’re balancing consistency against latency.

![](https://miro.medium.com/v2/resize:fit:1368/format:webp/1*pFI6F8njLqciDrb-Dffm6A.png)

A globally consistent counter increases latency.

Regional counters improve performance but sacrifice perfect accuracy.

Many systems accept slight inaccuracies in exchange for lower latency.

## Lets Conclude

**Aadvik:** Summarize your design.

**Priya:**

1. Enforce limits at the API Gateway.
2. Use Redis for shared distributed counters.
3. Prefer Token Bucket for burst handling.
4. Use Lua scripts for atomic updates.
5. Support plan-specific bucket configurations.
6. Monitor for hot keys.
7. Decide fail-open versus fail-closed behavior.
8. Consider regional tradeoffs in global deployments.

The goal isn’t preventing users from calling APIs.

The goal is ensuring that every user gets a fair share of platform resources while protecting the system from abuse.

## Interview Summary

Most engineers think rate limiting is:

```c
counter++
```

In reality, large-scale rate limiting is about:

- Fairness
- Distributed state
- Atomicity
- Bursty traffic
- Failure handling
- Global consistency

The algorithm is only one part of the solution.

The real challenge is making it work reliably across hundreds of servers, millions of users, and multiple regions.
