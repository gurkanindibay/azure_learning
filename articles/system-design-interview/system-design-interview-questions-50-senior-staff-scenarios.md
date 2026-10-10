---
type: Article
title: "System Design Interview Questions: 50 Senior & Staff-Level Scenarios on Scaling, Databases, Caching & Failure"
source: "https://medium.com/engineering-playbook/system-design-interview-questions-50-senior-staff-level-scenarios-on-scaling-databases-caching-b6f6df9253ac"
author:
  - "Devrim Özçay (ProdRescue By Devrim)"
published: 2026-10-04
created: 2026-10-10
description: "50 senior and staff-level system design interview scenarios covering bottlenecks, connection storms, cache stampedes, replication lag, backpressure, load shedding, idempotency, transactional outbox, multi-region partitions, and cascading failure."
tags:
  - "system-design"
  - "system-design-interview"
  - "scalability"
  - "caching"
  - "databases"
  - "resilience"
  - "distributed-systems"
---

# System Design Interview Questions: 50 Senior & Staff-Level Scenarios on Scaling, Databases, Caching & Failure

> **Author**: Devrim Özçay (ProdRescue By Devrim)  
> **Source**: [Medium / Engineering Playbook](https://medium.com/engineering-playbook/system-design-interview-questions-50-senior-staff-level-scenarios-on-scaling-databases-caching-b6f6df9253ac)  
> **Published**: October 4, 2026  
> **Related Takeaways**: [50 Senior & Staff-Level Scenarios — Key Takeaways](../../system-design-architecture/system-design-interview/50-senior-staff-scenarios-takeaways.md)

![System Design Interview Questions](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*jTP5oGe1NqLfG13W1PeVnQ.png)

> *Most candidates can design a system that works. Senior interviews ask what happens after it becomes successful enough to break.*


I have watched system design interviews follow the same pattern repeatedly. The candidate starts well, draws an API gateway, adds several stateless services, puts PostgreSQL underneath them, introduces Redis for caching, Kafka for asynchronous work, and a load balancer in front. For the first fifteen minutes, almost every reasonably experienced backend engineer can produce an architecture that looks credible.

Then the interviewer changes one number.

Traffic grows from 10,000 requests per second to 200,000. One customer suddenly generates 30% of all writes. Redis disappears for five minutes. A PostgreSQL replica falls 40 seconds behind. Kafka has 80 million messages of lag. The payment provider times out after receiving a request. One region loses connectivity to another while both continue receiving traffic.

The boxes on the diagram remain the same, but the interview changes completely.

That is the part worth preparing for. Senior and staff system design interviews are less about knowing which infrastructure products exist and more about understanding where the architecture stops behaving correctly.

Here are 50 scenarios I would prepare for.

## 1. Your API grows from 1,000 to 100,000 requests per second. What do you scale first?

I would not immediately scale anything. First I would identify which resource approaches saturation as traffic increases.

Application CPU, database connections, database IOPS, cache throughput, network bandwidth, downstream APIs, queue processing, and lock contention can all become bottlenecks at different points. Scaling should follow evidence about the constrained resource rather than traffic numbers alone.

## 2. When does horizontal application scaling stop helping?

When the bottleneck exists in a shared dependency or serialized resource. Adding another application instance does not help if every instance eventually waits for the same saturated database, lock, partition, or external API.

Horizontal scaling can actually make the shared bottleneck worse because more instances generate more concurrency against it.

## 3. Your stateless API scales from 20 to 200 instances and PostgreSQL collapses. Why?

The application tier gained concurrency much faster than the database gained capacity. Each new instance may open its own connection pool and generate additional simultaneous queries.

If 20 instances each maintain 20 database connections, the theoretical pool capacity is 400. Increasing to 200 instances can push that number toward 4,000 even though the database did not become ten times stronger.

## 4. How would you prevent application autoscaling from overwhelming PostgreSQL?

I would treat database concurrency as a bounded system resource. Connection-pool sizing, global capacity assumptions, autoscaling limits, query optimization, caching, read replicas, and admission control can all contribute.

The important idea is that application replicas cannot be scaled independently from downstream capacity. Autoscaling policy belongs to system design, not just infrastructure configuration.

## 5. When should you introduce a cache?

When repeated computation or data access is expensive enough that avoiding it materially improves latency, throughput, or downstream capacity.

I would also ask how stale the cached value may become, what a cache miss costs, how invalidation works, and what happens if the cache disappears. A cache creates another copy of state, so performance improvement comes with consistency and failure questions.

## 6. Redis normally handles 95% of reads and suddenly goes down. What happens?

The remaining system can receive roughly the workload Redis was absorbing. If PostgreSQL normally handles only 5% of reads, sending nearly all traffic to it can create a massive load increase.

This is why “fallback to the database” is not automatically a resilient design. The fallback needs enough capacity or the system needs another degradation strategy.

## 7. How would you survive a cache outage without destroying the database?

Possible strategies include rate limiting, request shedding, stale local data, controlled fallback, partial feature degradation, or protecting particularly expensive database operations.

The correct strategy depends on what the system can safely stop doing. Availability sometimes means preserving core functionality rather than attempting every request until every dependency fails.

## 8. What is a cache stampede?

Many requests simultaneously discover that a popular cached value expired and all attempt to rebuild it from the backing store.

A single expired key can therefore create a burst large enough to overload the database. Request coalescing, expiration jitter, stale-while-revalidate approaches, or proactive refresh can reduce the risk.

## 9. When would you add a read replica?

When read workload meaningfully constrains the primary and the relevant reads can tolerate the replica’s consistency behavior.

A replica is not free capacity for every query. Replication lag means some reads may return older state, so the architecture needs to decide which operations can safely use it.

## 10. A customer updates their profile and immediately reads the old value. What happened?

The write may have committed on the primary while the following read was routed to a replica that had not caught up.

This is a read-after-write consistency issue. Session-level routing, temporary primary reads, replication-position awareness, or product-level tolerance for staleness are possible approaches depending on requirements.

## 11. Why not send every read to replicas?

Some reads require stronger freshness, and replicas themselves have finite capacity. Additional replicas also create operational, replication, and cost overhead.

The useful question is which read paths can tolerate staleness. Read scaling should follow consistency requirements rather than a blanket rule.

## 12. Your primary database cannot handle write traffic anymore. What do you do?

I would first determine why writes are expensive. Missing indexes, excessive indexes, lock contention, inefficient transactions, unnecessary updates, large payloads, and poor data models can all create a write bottleneck before sharding becomes necessary.

Sharding an inefficient workload creates several inefficient databases plus distributed-systems complexity. I would exhaust simpler capacity improvements before introducing that cost.

## 13. When should you shard a database?

When the workload or dataset can no longer meet requirements economically or operationally within the useful limits of a single database architecture, and partitioning the data creates enough benefit to justify the complexity.

Sharding changes joins, transactions, migrations, routing, rebalancing, operational tooling, and failure recovery. It should solve a demonstrated scaling problem.

## 14. How would you choose a shard key?

I want a key that distributes load reasonably, supports important access patterns, and avoids excessive cross-shard operations.

Data volume alone is not enough. A shard key that evenly distributes rows but sends half of production traffic to one shard still produces a bad architecture.

## 15. What is a hot shard?

A hot shard receives significantly more workload than others. One tenant, geographic region, product, or key range may generate disproportionate traffic.

The cluster can have enormous aggregate unused capacity while the hot shard is saturated. Distribution problems cannot always be solved by adding generic capacity.

## 16. How would you handle one customer producing 30% of all traffic?

First I would determine whether that customer’s data or workload can be subdivided without violating required ordering or transaction boundaries.

Large tenants sometimes need additional partitioning, dedicated capacity, per-tenant limits, or a different routing strategy. Multi-tenant architecture has to account for customers that are not remotely equal in size.

## 17. What is consistent hashing useful for?

Consistent hashing can distribute keys across nodes while reducing how many keys need to move when nodes are added or removed compared with simple modulo-based approaches.

It is useful in distributed caches and partitioned systems, although practical implementations often use virtual nodes or other balancing mechanisms. Knowing the algorithm matters less than understanding the redistribution problem it addresses.

## 18. When would you use asynchronous processing?

When the caller does not need the final operation to complete before receiving a useful response, or when expensive work can be moved away from the synchronous request path.

Queues can smooth bursts and isolate processing, but they introduce delayed completion, retries, duplicate processing, backlog management, and observability requirements. Asynchrony moves complexity rather than eliminating it.

## 19. Your API puts work onto Kafka and returns 202. Is the operation successful?

It means the system accepted the request according to whatever durability boundary exists at that point. It does not necessarily mean the business operation completed.

The API contract should distinguish acceptance from completion. Clients may need an operation identifier or status endpoint to observe eventual outcome.

## 20. Kafka has 50 million messages of lag. Is adding consumers enough?

Only if consumers are the constrained resource and additional parallelism is available. Partition count, database capacity, external APIs, and per-message processing time can all limit useful scaling.

If the consumer group is waiting on an already saturated database, additional consumers can worsen recovery.

## 21. How would you calculate backlog recovery time?

I would compare the consumer’s sustainable processing rate with the continuing producer rate. Only the excess processing capacity drains the existing backlog.

If producers generate 40,000 messages per second and consumers process 50,000, the backlog shrinks at approximately 10,000 per second, not 50,000. That difference can turn an apparently powerful consumer fleet into a multi-hour recovery.

## 22. What is backpressure?

Backpressure controls what happens when work enters a system faster than it can be processed.

Without it, queues, memory, threads, or downstream requests can grow until another resource fails. A resilient system needs a deliberate answer to overload rather than unlimited accumulation.

## 23. Would you prefer dropping requests or allowing a queue to grow indefinitely?

Neither is universally correct. For some workloads, rejecting excess traffic quickly protects the service and gives clients a clear signal. For others, durable buffering is valuable because the work can be completed later.

The queue still needs a bounded operational model. Infinite backlog is simply delayed failure.

## 24. What is load shedding?

Load shedding deliberately rejects or degrades some work when the system approaches a dangerous capacity boundary.

This can preserve critical functionality during overload. Serving 80% of important requests successfully can be better than accepting 100% and allowing the entire system to collapse.

## 25. How would you design rate limiting?

I would first define what is being limited: IP, user, API key, tenant, endpoint, cost unit, or another identity. Then I would choose an algorithm and storage model matching the scale and consistency requirement.

A global “100 requests per second” limit is often too simplistic. One expensive request can consume more resources than hundreds of cheap reads.

## 26. Where should rate limiting happen?

As close to the entry point as practical when the goal is protecting downstream capacity, while service-specific limits may still exist deeper in the architecture.

API gateways can reject obvious excess traffic before it consumes application resources. Internal services may additionally need protection from trusted callers that can still generate overload.

## 27. What happens if the rate limiter itself goes down?

The system needs a fail-open or fail-closed policy appropriate to the protected operation.

A public content API might temporarily fail open to preserve availability, while an expensive or security-sensitive operation may need stricter behavior. The rate limiter is itself a dependency with a failure mode.

## 28. How would you design an idempotent payment endpoint?

I would associate a unique idempotency identifier with the logical payment attempt and durably record its state. Repeated requests using the same identifier should return or continue the same logical operation rather than create another charge.

Concurrency matters. Two replicas receiving the same key simultaneously require an atomic uniqueness or state-transition mechanism.

## 29. The payment provider times out. Did the payment fail?

You cannot know from the timeout. The provider may never have received the request, may still be processing it, or may have completed the charge while the response was lost.

The architecture needs reconciliation, idempotency, or a status lookup rather than blindly assuming failure and issuing another charge.

## 30. How would you prevent overselling the final item in inventory?

The authoritative inventory transition needs concurrency control. Atomic conditional updates, database locking, optimistic concurrency, reservations, or other coordination strategies can enforce the invariant.

Checking `stock > 0` and later performing a separate decrement without protection allows concurrent requests to observe the same inventory.

## 31. Would you use a distributed Redis lock for inventory?

Possibly in some architectures, but I would first ask whether the authoritative database can enforce the invariant directly.

Database constraints or atomic state transitions can often provide simpler durability and correctness. Distributed locks introduce lease expiry, stale ownership, and additional failure modes.

## 32. What is eventual consistency and where would you accept it?

It allows different parts of the system to temporarily observe different versions of state while converging over time.

I would accept it where temporary staleness does not violate important business invariants, such as many analytics, feeds, recommendations, or noncritical profile propagation workflows. The acceptable inconsistency window should still be explicit.

## 33. Where would you require stronger consistency?

Operations involving unique ownership, money movement, inventory allocation, permission changes, or other strict invariants may require stronger coordination.

The correct consistency level belongs to the business operation rather than the entire architecture. One product can contain both strongly and eventually consistent workflows.

## 34. What happens if your system writes to the database and publishes to Kafka separately?

One operation can succeed while the other fails. You can end up with database state that nobody downstream learns about or an event describing a change that never committed.

This dual-write problem is why patterns such as transactional outbox exist. The local database transaction can persist both business state and the intent to publish.

## 35. Does transactional outbox guarantee each event is published exactly once?

A publisher can send the event successfully and crash before marking the outbox record as published. The event can therefore be sent again after restart.

The pattern is commonly combined with idempotent consumers. Reliable systems often embrace at-least-once delivery and make repeated processing safe.

## 36. How would you design a notification system for 100 million users?

I would separate acceptance, scheduling, preference evaluation, delivery preparation, provider interaction, retries, and status tracking rather than sending notifications synchronously from the request.

Then I would partition work according to delivery characteristics and protect external providers with rate and concurrency controls. A provider outage should create controlled backlog rather than millions of request threads.

## 37. How would you design URL shortening at massive scale?

I would first establish read/write ratio, redirect latency, identifier requirements, expiration behavior, abuse protection, and consistency expectations.

The interesting follow-up is rarely generating short strings. It is how mappings are partitioned, cached, replicated, protected from hot links, and served when parts of the storage system are unavailable.

## 38. How would you handle a viral URL receiving millions of requests per second?

I would attempt to serve it as far from the primary database as possible using appropriate caching layers or edge infrastructure.

One hot object should not repeatedly require an authoritative database lookup. The design should recognize skew because real traffic is rarely distributed evenly across every object.

## 39. How would you design a feed system?

I would begin by clarifying fan-out model, freshness requirements, celebrity-scale accounts, ranking, pagination, and read/write patterns.

Pure fan-out-on-write can become expensive for accounts with millions of followers, while pure fan-out-on-read can make reads expensive. Hybrid strategies are common because user distributions are highly uneven.

## 40. What is the celebrity problem in feed architecture?

A celebrity with 100 million followers can make ordinary fan-out-on-write enormously expensive. One post could require a huge number of timeline updates.

Large accounts may therefore use a different delivery path where their content is merged at read time or handled specially. System design often improves when extreme workloads are treated explicitly rather than forcing one algorithm onto every user.

## 41. How would you design multi-region writes?

I would first ask whether the same logical data needs to accept writes concurrently in multiple regions. If it does, conflict resolution, replication, ordering, consistency, and partition behavior become central.

Multi-region architecture is not merely deploying the same service twice. Data semantics determine whether active-active operation is actually safe.

## 42. What happens if two regions lose connectivity but both remain online?

If both continue accepting writes to the same logical data, conflicting state can develop. The architecture must decide whether availability during the partition is more important than preventing those conflicts.

Different operations may choose differently. Reading a product catalog and transferring money do not need identical partition behavior.

## 43. How would you handle conflicting writes after regions reconnect?

That depends entirely on the data model. Last-write-wins may be acceptable for some fields but dangerous for financial or ownership state.

Versioning, conflict-free structures, application-level merge logic, or stronger coordination may be appropriate. “Resolve the conflict” is not a complete design until the business semantics are defined.

## 44. Why can wall-clock timestamps be dangerous for conflict resolution?

Clocks on different machines are not perfectly synchronized. Clock skew can make a later timestamp fail to correspond to the actual causal order of operations.

Physical timestamps remain useful, but correctness mechanisms should understand their limitations. Distributed ordering sometimes requires version or logical information beyond wall-clock time.

## 45. How would you design graceful degradation?

I would classify functionality according to what must remain available and what can be reduced, delayed, served stale, or disabled during dependency failure.

For an e-commerce system, browsing might continue from cached data while recommendations disappear and some write operations become temporarily unavailable. Graceful degradation is a product decision expressed through architecture.

## 46. What is a cascading failure?

A failure in one component creates additional load or resource pressure elsewhere, causing more components to fail.

A slow database can exhaust application connection pools, which increases request latency, which triggers retries, which increases traffic, which pushes the database further into overload. The original database slowdown is only the first step of the incident.

## 47. How would you stop a cascading failure?

Timeouts, bounded retries, circuit breakers, concurrency limits, load shedding, backpressure, resource isolation, and graceful degradation can all interrupt different parts of the chain.

The correct protection depends on the failure path. Adding every resilience pattern without understanding interactions can create a system that is harder to predict.

## 48. What would you monitor in a large distributed system?

I would start with customer-facing throughput, errors, and latency, then connect those signals to resource saturation, dependency behavior, queues, database health, cache behavior, replication lag, and business completion metrics.

Monitoring should allow an engineer to move from “customers are failing” toward the constrained component quickly. Thousands of metrics are less useful than a smaller set with clear causal relationships.

## 49. The system is healthy according to every dashboard, but customers say it is broken. What do you do?

I would question what the dashboards define as health. HTTP 200 rates may look perfect while asynchronous workflows never complete, replicas return stale information, or business state is incorrect.

Infrastructure health is only a proxy for the customer outcome. Mature observability includes business-level correctness and completion signals.

## 50. What separates a senior system design answer from a staff-level answer?

A senior engineer can usually design the major components, explain bottlenecks, select reasonable storage, and reason about failures. A strong staff-level answer also examines organizational and operational consequences: ownership boundaries, migration strategy, cost, blast radius, capacity evolution, multi-region behavior, and what happens when assumptions change two years later.

The architecture becomes less about finding the “correct” diagram and more about making expensive trade-offs explicit. That is usually where the most interesting part of the interview begins.

## The Diagram Is Usually the Easy Part

I used to think system design interviews were mainly about knowing enough architecture patterns. Learn caching, queues, sharding, replication, load balancing, consistent hashing, rate limiting, and a few popular designs, then combine the right components during the interview. That works surprisingly well until the interviewer begins attacking the assumptions behind those components.

Redis solves the database-read problem until Redis disappears. Kafka absorbs a burst until producers permanently generate work faster than consumers can process it. Read replicas increase capacity until a workflow requires read-after-write consistency. Horizontal scaling works until every new application instance creates another database connection pool. Multi-region deployment improves geographic availability until the regions disagree about who owns the same piece of state.

None of those technologies failed. The architecture failed to define what should happen when its assumptions stopped being true.

That changed how I approach these interviews. I start with the workload and the invariants, then identify the finite resources and failure boundaries before adding infrastructure. If payment must never be duplicated, that requirement influences idempotency before Kafka enters the conversation. If users can tolerate a feed being 20 seconds stale, that fact can eliminate expensive consistency mechanisms before the database is selected.

The best system design answers I have heard rarely contain the largest number of boxes. They contain fewer unexplained assumptions. The candidate knows what each component protects, what it costs, what happens when it disappears, and which part of the architecture becomes the next bottleneck after it succeeds.

That is a much harder skill to memorize, which is precisely why senior and staff interviews eventually move there.

## Go Deeper

If you’re preparing for senior or staff system design interviews and want deeper follow-ups around databases, caching, queues, consistency, scaling, failure recovery, and architecture trade-offs, I built the **Senior System Design Interview Playbook: Follow-Ups, Trade-Offs & Architecture Patterns** for this exact stage of the interview:

## [Senior System Design Interview Playbook: Follow-Ups, Trade-Offs & Architecture Patterns](https://devrimozcay.gumroad.com/l/ekqckb?source=post_page-----b6f6df9253ac-----------------------------------------)

### The Hard Part Starts After You Draw the Architecture You know the usual system design components. PostgreSQL, Redis…

devrimozcay.gumroad.com

For broader senior and staff interview preparation across system design, coding, production reasoning, and behavioral rounds:

## [Senior & Staff Software Engineer Interview Bundle: Coding, System Design & Behavioral](https://devrimozcay.gumroad.com/l/kzfrlu?source=post_page-----b6f6df9253ac-----------------------------------------)

### Prepare for the Entire Senior & Staff Interview Loop A Senior or Staff interview is rarely lost because you know…

devrimozcay.gumroad.com

I also publish deeper notes on system design, backend architecture, distributed systems, Java, production failures, and senior engineering here:

## [Devrim | ProdRescue By Devrim | Substack](https://substack.com/@devrimozcay1?source=post_page-----b6f6df9253ac-----------------------------------------)

### I break down real production failures, architecture tradeoffs & Staff-level decisions. Backend, distributed systems…

substack.com
