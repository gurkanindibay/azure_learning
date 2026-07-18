---
type: Article
title: "URL Shortener Suddenly Crashes During IPL Finals: How Will You Fix?"
source: "https://codefarm0.medium.com/url-shortener-suddenly-crashes-during-ipl-finals-how-will-you-fix-3347c9911ba3"
author:
  - "Arvind Kumar"
published: 2026-07-13
created: 2026-07-18
description: "System design interview scenario covering CDN edge caching for redirects, Redis hot-key mitigation, local in-memory caching, request coalescing, and stateless horizontal scaling under viral traffic."
tags:
  - caching
  - system-design
  - interview
---

# URL Shortener Suddenly Crashes During IPL Finals: How Will You Fix?

If you’ve already gone through the basics of designing a URL Shortener, you know how services like TinyURL or Bitly generate a short URL, store the mapping, and redirect users to the original URL.

In case you haven’t read it yet, here’s the foundational design:

> **Designing a URL Shortener (TinyURL):**  
> [https://codefarm0.medium.com/designing-a-url-shortener-tinyurl-cb3bcfe79dd2](https://codefarm0.medium.com/designing-a-url-shortener-tinyurl-cb3bcfe79dd2)

But real-world system design interviews rarely stop there.

Most interviewers assume you already know the basic architecture.

What they really want to test is how your design behaves under **unexpected scale**.

Can your system survive when traffic suddenly increases by **1000x**?

Can it handle one URL becoming viral overnight?

Can it continue serving millions of users without downtime?

Let’s move one step ahead.

> [Full story for non-members](https://codefarm0.medium.com/3347c9911ba3?sk=a2de26b779c66373bd25bc553e3ca889)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*qY_AF-BtIZdYvudC84qovg.png)

## Interview Scenario

Imagine you’ve joined a system design interview.

Your interviewer decides not to ask you to design a URL Shortener from scratch.

Instead, they present a production incident.

> *“Your URL Shortener has been running perfectly for months. During the IPL Finals, a celebrity posts one shortened URL on social media. Within minutes, tens of millions of users click that same link. Suddenly, users start reporting that the redirect service is failing.”*

How would you debug the issue?

More importantly…

How would you redesign the system so it never happens again?

Let’s see how the conversation unfolds.

## Interview Conversation

**Arvind (Interviewer):**

Hi Nisha.

Let’s assume your team has already built a URL Shortener similar to TinyURL.

The service handles millions of URLs every day without any issues.

Now imagine it’s the IPL Final.

A celebrity shares one of your shortened URLs on social media.

Within five minutes, that single URL receives nearly **25 million redirect requests**.

Your dashboards start showing increased latency, users report failures, and the redirect service begins timing out.

How would you approach this problem?

**Nisha (Candidate):**

The first thing I’d avoid is jumping directly to a solution.

Whenever production systems fail under heavy traffic, I first want to understand **where the bottleneck is**.

A URL Shortener redirect is actually a very simple operation.

There is no complex business logic.

Every request simply asks one question:

> *“Given this short URL, what is the original URL?”*

Because of that simplicity, failures usually happen due to infrastructure bottlenecks rather than application logic.

So before redesigning anything, I’d first walk through the request lifecycle.

**Arvind:**

Walk me through the request flow first.

**Nisha:**

Whenever a user clicks a shortened URL, the request usually follows this path:

Every redirect is simply a lookup.

There is no business logic.

The faster we answer this lookup, the better.

**Arvind:**

So why would this architecture fail?

**Nisha:**

Because every request asks for exactly the same key.

For example:

```
abc123
```

Instead of millions of different keys,

Redis suddenly receives millions of requests for **one single key**.

This is called a **Hot Key**.

Even though Redis is extremely fast, one node becomes overloaded while other Redis nodes remain almost idle.

**Arvind:**

Interesting.

What happens if Redis becomes overloaded?

**Nisha:**

Then cache lookups become slower.

Some requests timeout.

Those requests fall back to the database.

Now instead of handling thousands of queries,

the database suddenly starts receiving millions.

That’s when everything begins collapsing.

The database isn’t actually the original problem.

It’s only the victim.

**Arvind:**

Good observation.

How would you reduce database traffic?

**Nisha:**

The first layer I’d improve is caching.

Instead of making Redis answer every request,

I’d push the data even closer to users.

That means using a CDN.

**Arvind:**

CDN?

For redirects?

**Nisha:**

Yes.

Most people associate CDNs only with images and videos.

But redirect responses can also be cached.

==For popular URLs, CDN edge servers can directly return the HTTP redirect without contacting our backend.==

Now millions of requests never even reach our servers.

**Arvind:**

Suppose the redirect isn’t cacheable.

What next?

**Nisha:**

Then Redis becomes critical.

Instead of having one Redis instance,

I’d use Redis Cluster.

However…

Redis Cluster alone doesn’t completely solve Hot Keys.

Because the same key still belongs to one shard.

That shard remains overloaded.

**Arvind:**

Exactly.

So what’s the solution?

**Nisha:**

There are multiple strategies.

### 1. Local In-Memory Cache

Each redirect service instance stores extremely popular URLs in memory.

```
abc123
↓
Service 1 Memory
Service 2 Memory
Service 3 Memory
Service 4 Memory
```

Now Redis is contacted only occasionally.

### 2. Cache Replication

Popular keys can be replicated across multiple Redis nodes instead of existing on only one shard.

Traffic gets distributed.

### 3. Request Coalescing

If one backend request is already fetching the URL,

all other requests wait for that same result instead of generating duplicate database queries.

**Arvind:**

Nice.

Now imagine traffic doubles again.

What would you scale?

**Nisha:**

The redirect service should always be stateless.

That allows horizontal scaling.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-46msYrFZyjhO7EUd1CVfQ.png)

Whenever CPU increases,

Kubernetes or Auto Scaling Groups simply launch more redirect instances.

No session migration is required.

**Arvind:**

Would database scaling help?

**Nisha:**

Yes, but only after cache optimization.

A URL shortener is an extremely read-heavy system.

Ideally:

- 99.9% of requests should never touch the database.
- Redis serves almost everything.
- Database acts as the source of truth.

If database reads are still high, I’d introduce read replicas.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*4x0-YdS64_7R_dR77jkKBw.png)

Only writes go to the primary.

Reads can be distributed.

**Arvind:**

Suppose one URL becomes globally viral.

How would you detect it before users complain?

**Nisha:**

I’d monitor:

- Redis Hot Key metrics
- Cache hit ratio
- Redirect latency (P95/P99)
- Database QPS
- Connection pool usage
- CDN cache hit percentage
- Error rate
- Auto Scaling events

The moment one URL starts generating abnormal traffic,

I’d proactively replicate it or preload caches.

**Arvind:**

Excellent.

Can you summarize your approach?

**Nisha:**

Absolutely.

My troubleshooting order would be:

```
User Click
      │
      ▼
Check CDN Hit Ratio
      │
      ▼
Check Redis Hot Keys
      │
      ▼
Check Cache Hit Rate
      │
      ▼
Check Database Read QPS
      │
      ▼
Check Connection Pool
      │
      ▼
Scale Stateless Redirect Services
```

## Let's Conclude

The key insight is that a URL shortener is overwhelmingly **read-heavy**. During viral events, the challenge isn't storing data — it's serving the same tiny piece of data millions of times with minimal latency.

The winning architecture combines **CDN edge caching**, **Redis**, **local in-memory caching for hot keys**, **stateless horizontal scaling**, and a **database used primarily as the source of truth**, ensuring the system stays responsive even when one link suddenly becomes internet-famous.

> **Related**: [List: 22 Scenarios for System Design Interview](https://medium.com/@codefarm0/list/22-scenarios-for-system-design-interview-93dfe2489e13) (Curated by Arvind Kumar)