---
type: Article
title: "I Increased the Database Connection Pool. Then My API Got Slower."
source: "https://medium.com/@the_atomic_architect/database-connection-pool-makes-api-slower-65341840d5cc"
author:
  - "[[The Atomic Architect]]"
published: 2026-09-24
generated: { by: process:format-agent, at: 2026-09-27T00:00:00Z }
description: "Why increasing connection pool size often degrades API performance instead of boosting throughput, exploring database resource contention, Little's Law, and connection backpressure."
tags:
  - clippings
  - databases
  - postgresql
  - connection-pooling
  - performance
  - spring-boot
  - hikaricp
---

# I Increased the Database Connection Pool. Then My API Got Slower.

> **Author**: [The Atomic Architect](https://medium.com/@the_atomic_architect)  
> **Published**: September 24, 2026  
> **Source**: [Medium](https://medium.com/@the_atomic_architect/database-connection-pool-makes-api-slower-65341840d5cc)  
> **Domain**: Databases, Connection Pooling, Concurrency Control, Latency Breakdown, Capacity Planning  
> **Related Takeaways**: [41. Database Connection Pool Sizing & Contention: Sizing for Capacity vs. Concurrency Gate — Key Takeaways](../../system-design-architecture/databases/41-db-key-takeaways.md)

---

## I thought more connections meant more concurrency. PostgreSQL had a different opinion.

At 10:42 AM, our API was slow.

Not catastrophically slow.

Just slow enough to annoy everyone.

Requests that normally finished in around 150 milliseconds were taking 700ms.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*mTiXuNui0Cka2t8e0MUkBw.png)

Some were crossing the one-second mark.

The application CPU wasn’t particularly high.

Memory looked normal.

There wasn’t an obvious error spike.

And PostgreSQL wasn’t screaming either.

So I did what seemed like the obvious thing.

I opened the Spring Boot configuration.

And found this:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
```

Ten connections.

Ten.

That looked suspicious.

The application had more traffic now.

More requests.

More concurrent users.

More work.

Surely ten database connections couldn’t be enough.

So I changed it.

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50
```

Restarted the application.

Sent traffic through it again.

And waited for the latency graph to come down.

Instead…

It went up.

The API got slower.

Not slightly slower.

Noticeably slower.

And that was the moment I learned one of the most dangerous lessons in backend engineering:

> *A database connection isn’t a unit of performance.*

I had been treating connections like workers.

They weren’t.

They were competing for the same database.

And I had just invited 40 more competitors into the room.

---

## The configuration looked harmless

If you’ve worked with Spring Boot, you’ve probably seen something like:

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
```

The name itself makes the decision feel obvious.

**maximum-pool-size.**

Want more throughput?

Increase it.

10 → 20.

20 → 50.

50 → 100.

It almost feels like adding CPU cores.

But a connection pool doesn’t create database capacity.

It creates more ways for application threads to talk to the database at the same time.

That distinction is tiny when you’re reading configuration.

It’s enormous when you’re running production traffic.

---

## What actually happens when a request needs the database?

Let’s start with a normal Spring Boot request.

Imagine:

```text
GET /payments/12345

Request reaches application
        ↓
Controller
        ↓
Service
        ↓
Repository
        ↓
DataSource
        ↓
Connection Pool
        ↓
PostgreSQL
```

The repository needs a database connection.

HikariCP finds an available connection.

```text
Application Thread
        │
        ▼
    HikariCP
        │
        ▼
   Connection 
        │
        ▼
   PostgreSQL
```

The query runs.

The result comes back.

The connection is returned to the pool.

Simple.

But now imagine 100 requests arriving at roughly the same time.

And your pool has only 10 connections.

You don’t suddenly get 100 database operations.

You get something more like:

```text
100 application requests
          │
          ▼
     HikariCP pool
          │
    ┌─────┴─────┐
    │           │
10 running   90 waiting
```

At first glance, that looks terrible.

Why would we deliberately make 90 requests wait?

So naturally, I increased the pool.

And that is where my intuition went wrong.

I was thinking about the application.

The database was thinking about itself.

My mental model was:

```text
More connections
        ↓
More queries at once
        ↓
Less waiting
        ↓
Lower latency
```

PostgreSQL’s reality is closer to:

```text
More connections
        ↓
More concurrent work
        ↓
More contention
        ↓
More CPU / memory / I/O pressure
        ↓
Queries take longer
        ↓
Connections stay busy longer
        ↓
More requests wait
```

And now we’re in a feedback loop.

The pool didn’t create capacity.

It exposed more work to a system that already had finite capacity.

---

## The first mistake: treating waiting as failure

This is something I think a lot of backend developers get wrong.

If 90 requests are waiting for a database connection, it looks like the connection pool is the bottleneck.

But waiting isn’t necessarily the problem.

Sometimes waiting is the mechanism that protects the database.

Think about a restaurant.

Imagine the kitchen can comfortably cook 10 orders at once.

You have two options.

### Option A

Allow only 10 orders into the kitchen.

Everyone else waits outside.

### Option B

Allow 100 orders into the kitchen.

Now everyone is standing around the chefs.

Ingredients are everywhere.

People are bumping into each other.

The kitchen is overloaded.

The chefs are slower.

And somehow the customers are still waiting.

Increasing the number of people inside didn’t increase the number of meals the kitchen could cook.

It just made the kitchen more crowded.

A database connection pool can behave similarly.

---

## PostgreSQL doesn’t have infinite capacity

This sounds obvious.

But configuration often makes us forget it.

PostgreSQL has:

- CPU
- RAM
- Disk I/O
- Shared buffers
- Caches
- Locks
- Indexes
- Background processes
- Connection overhead
- Network overhead
- Query planning
- Execution resources

And all of your concurrent queries are competing for those resources.

If 10 queries are running, PostgreSQL has one workload.

If 50 queries are running, PostgreSQL has a different workload.

And 50 isn’t automatically five times faster than 10.

Sometimes it’s slower.

Much slower.

---

## So I ran the experiment again

Instead of guessing, I wanted numbers.

Imagine a simple endpoint:

```java
@GetMapping("/payments/{id}")
public Payment getPayment(@PathVariable Long id) {
    return paymentService.getPayment(id);
}
```

The service:

```java
public Payment getPayment(Long id) {
    return paymentRepository.findById(id)
        .orElseThrow();
}
```

And PostgreSQL:

```sql
SELECT *
FROM payments
WHERE id = ?;
```

Nothing complicated.

I put the endpoint under concurrent load.

Then changed only the pool size.

The exact numbers will vary enormously by hardware, query complexity, traffic pattern, and database configuration, so the point isn’t the particular numbers.

The shape is what matters.

Something like this can happen:

```text
Pool Size     Throughput      Avg Latency
5             820 req/s       115 ms
10            1,180 req/s      98 ms
20            1,260 req/s     105 ms
40            1,250 req/s     160 ms
80            1,210 req/s     290 ms
```

Notice what happened.

Increasing the pool helped.

Then it stopped helping.

Then it started hurting.

There was a curve.

```text
peak
                  /\
                 /  \
                /    \
_______________/      \____________

 too few       sweet       too many
connections     spot       connections
```

That’s the part configuration tutorials rarely show you.

There isn’t a magical pool size.

There is a workload-dependent operating point.

---

## But why?

Let’s take one query.

Suppose it takes:

**10 ms**

If the database can comfortably execute several such queries concurrently, increasing concurrency can improve throughput.

You keep the CPU busy.

You keep the system productive.

Great.

But eventually you reach saturation.

Imagine the database CPU is already near capacity.

Now another query arrives.

Then another.

Then another.

They all need CPU.

They may need memory.

They may need disk.

They may wait for locks.

They may compete for shared resources.

The database doesn’t suddenly acquire more CPU because Hikari has another 30 connections.

The queries simply compete harder.

---

## Connection ≠ CPU core

This was my biggest mental mistake.

I was unconsciously thinking:

**10 connections ≈ 10 workers**

Then:

**50 connections ≈ 50 workers**

But that’s not how database performance works.

A connection is primarily a communication channel between the application and database.

It doesn’t represent a dedicated CPU core.

It doesn’t mean PostgreSQL can perform one completely independent operation at maximum speed per connection.

And it certainly doesn’t mean:

`maximumPoolSize = 100`

means:

> *PostgreSQL can efficiently execute 100 queries simultaneously.*

The database still has finite resources.

---

## And then there is the connection itself

Opening a database connection isn’t free.

A PostgreSQL connection has memory and process/session overhead.

- Authentication happens.
- Session state exists.
- Resources are allocated.
- Network state exists.
- The database must keep track of the connection.

This doesn’t mean:

> *Never have many connections.*

PostgreSQL can absolutely handle many connections.

The point is simply that connections have a cost.

And if your application creates a huge number of them because you’re trying to fix latency, you may be treating a symptom by increasing another source of pressure.

---

## HikariCP isn’t the database

This distinction matters.

HikariCP is a connection pool.

It manages connections for your application.

It doesn’t manufacture database capacity.

```text
Spring Boot
          │
          ▼
     HikariCP
┌────┬────┬────┐
│ C1 │ C2 │ C3 │ ...
└────┴────┴────┘
          │
          ▼
      PostgreSQL
```

Hikari can:

- Avoid repeatedly opening new connections
- Make connection acquisition efficient
- Control application-level concurrency
- Improve predictability

But if PostgreSQL is already saturated, Hikari cannot turn:

**8 CPU cores into 80 CPU cores**

It can only decide how many application requests are allowed to compete for those resources at once.

And suddenly maximumPoolSize starts looking less like a performance setting...

and more like a concurrency-control setting.

---

## Then I looked at connection acquisition time

This was the clue I should have looked at earlier.

Suppose your application is slow.

You see:

**API latency = 800ms**

That number doesn’t tell you where the 800ms went.

Maybe:

```text
Connection acquisition = 600ms
SQL execution         = 20ms
Java processing       = 10ms
Network               = 5ms
```

Now increasing the pool might be exactly the wrong move.

The bottleneck isn’t acquiring connections.

The bottleneck is what happens after the connection is acquired.

This is why you can’t tune a connection pool from API latency alone.

You have to break the request down.

---

## The request has a hidden timeline

Imagine:

```text
Request arrives
      │
      ├── Controller: 2ms
      ├── Service: 3ms
      ├── Wait for connection: 15ms
      ├── SQL execution: 600ms
      ├── Mapping: 4ms
      └── Response: 2ms

Total: 626ms
```

Increasing the pool may reduce:

**15ms**

while doing absolutely nothing about:

**600ms**

And if more concurrent queries make those 600ms queries become 800ms…

you just made the API worse.

---

## Then there was the hidden killer: slow queries

This is where pool sizing gets really interesting.

Imagine you have:

- 10 connections
- 50ms queries

A connection becomes available quickly.

Now imagine one query starts taking:

**2 seconds**

Maybe:

- It lost an index.
- The query planner changed.
- The database is under load.
- It is scanning millions of rows.

That connection is now occupied for 2 seconds.

If enough queries behave like this, the pool fills.

Then application threads wait.

The symptoms look like:

> *We need more connections.*

But the underlying problem might actually be:

> *Our queries became slower.*

Adding connections can hide that problem temporarily.

And sometimes make it worse.

---

## The pool can amplify a database problem

Imagine PostgreSQL is struggling.

A query starts taking longer.

The application notices connection waits.

Someone increases:

`maximum-pool-size: 10`

to:

`maximum-pool-size: 50`

Now more queries can enter PostgreSQL simultaneously.

Those queries compete for resources.

CPU rises.

I/O rises.

Lock contention may rise.

Query latency rises.

Connections stay occupied longer.

The pool fills again.

Someone sees the pool filling.

They increase it again.

```text
10
 ↓
30
 ↓
50
 ↓
100
```

And now the system is digging itself deeper.

A nasty feedback loop:

```text
Slow database
     ↓
Connections stay busy
     ↓
Pool waits increase
     ↓
Increase pool size
     ↓
More concurrent DB work
     ↓
Database contention increases
     ↓
Queries get slower
     ↓
Connections stay busy even longer
```

The attempted fix becomes part of the problem.

---

## Then I discovered the other side of the equation

Suppose your application has:

- 4 Spring Boot instances
- `maximumPoolSize = 50`

Did you configure 50 database connections?

No.

Potentially:

**4 × 50 = 200 connections**

Now imagine Kubernetes scales to:

**10 instances**

Suddenly:

**10 × 50 = 500 connections**

This is where application-level configuration collides with infrastructure-level scaling.

One service might look reasonable in isolation.

Production isn’t one service.

It’s:

```text
Instance 1 → 50
Instance 2 → 50
Instance 3 → 50
...
Instance 10 → 50
```

And PostgreSQL sees the combined workload.

---

## The database sees the fleet, not your YAML file

Your Spring Boot application sees:

`maximumPoolSize = 50`

PostgreSQL sees:

- Service A connections
- Service B connections
- Service C connections
- Background jobs
- Admin tools
- Monitoring systems
- Migration processes

The database receives the aggregate workload.

And that means pool sizing is not purely an application decision.

It is a system-wide capacity decision.

---

## Then there’s the queue you don’t see

Suppose all 50 connections are busy.

The 51st request waits.

```text
Application threads

T1  ─────► DB
T2  ─────► DB
T3  ─────► DB
...
T50 ─────► DB

T51 ───┐
T52 ───┤
T53 ───┤  WAITING
T54 ───┘
```

There are two kinds of concurrency:

1. Application concurrency
2. Database concurrency

They are not the same thing.

Sometimes the queue is exactly what prevents the database from being overwhelmed.

---

## This is why timeouts matter

Suppose a request waits forever for a connection.

That’s terrible.

A pool should have sensible timeout behavior.

```yaml
spring:
  datasource:
    hikari:
      connection-timeout: 3000
```

The exact value depends on your workload.

The important idea is:

> *Fail reasonably instead of allowing unlimited waiting.*

Otherwise you can get cascading failures.

```text
Database slows
      ↓
Queries take longer
      ↓
Connections stay occupied
      ↓
Pool fills
      ↓
Application threads wait
      ↓
Latency rises
      ↓
More requests accumulate
      ↓
Memory/thread pressure rises
      ↓
Application becomes unhealthy
```

---

## And this is where backpressure enters the story

We often discuss backpressure in:

- Kafka
- Queues
- Reactive Streams
- Event-driven systems

But connection pools provide a simple form of backpressure too.

A bounded pool effectively says:

> *Wait. The database is busy.*

An oversized pool says:

> *Sure, everyone come in.*

And sometimes the first behavior is healthier.

---

## But then how do you choose the pool size?

This is where people usually want a magic number.

10? 20? 50? 100?

There isn’t one.

Anyone who tells you:

> *Your Hikari pool should always be 20.*

is giving you a number without knowing your workload.

Pool sizing depends on:

- Database CPU
- Query execution time
- Read/write ratio
- Number of application instances
- Database limits
- Transaction duration
- Lock contention
- Traffic patterns
- Connection overhead
- Downstream dependencies

And one of the most useful concepts here is **Little’s Law**.

The basic relationship is:

$$\text{Concurrency} \approx \text{Throughput} \times \text{Latency}$$

Suppose your system processes:

**1,000 requests/second**

and average database work per request is:

**20ms**

Then:

$$1000 \times 0.020 = 20$$

Roughly 20 units of work are in flight.

It’s not a magical formula.

It’s a way to think.

---

## The best pool size is usually discovered, not guessed

Instead of asking:

> *What number should I put here?*

Ask:

> *What happens as I increase it?*

Run controlled tests.

Try: 5, 10, 15, 20, 30, 40.

Measure:

- Throughput
- p50 latency
- p95 latency
- p99 latency
- Connection acquisition time
- Query execution time
- Database CPU
- Database I/O
- Lock waits
- Error rate

Then look for the curve.

```text
Pool 5  → Underutilized
Pool 10 → Better
Pool 15 → Better
Pool 20 → Peak
Pool 30 → Flat
Pool 40 → Worse
```

That’s useful information.

Much more useful than:

> *Someone on Reddit said 30 is optimal.*

---

## The p99 told me more than the average

Another trap.

Imagine:

**Pool = 10**
- Average latency = 100ms
- p99 = 800ms

Then:

**Pool = 30**
- Average latency = 110ms
- p99 = 1.5s

The average barely moved.

The tail got dramatically worse.

That’s what users feel.

The 1% of requests that suffer the longest waits are often what determine whether an application feels fast or randomly slow.

Database contention frequently appears in:

- p95
- p99

before it becomes obvious in averages.

---

## Then I looked at the SQL

And this was embarrassing.

After all that tuning, the slowest queries weren’t exactly mysterious.

One:
- Was missing an index.

Another:
- Was fetching more data than necessary.

Another:
- Was doing significantly more work than required.

And one endpoint:
- Held a transaction open longer than expected.

The connection pool wasn’t the real problem.

It was simply where the problem became visible.

A connection pool is often the messenger.

Don’t shoot the messenger.

---

## Long transactions are especially nasty

Imagine:

```java
@Transactional
public void processPayment() {

    Payment payment = repository.findById(id);

    // some processing

    callExternalService();

    // more processing

    repository.save(payment);
}
```

Timeline:

```text
Acquire connection
      ↓
SELECT
      ↓
Wait 800ms for external API
      ↓
UPDATE
      ↓
COMMIT
      ↓
Release connection
```

The SQL might only consume a few milliseconds.

The connection remains occupied throughout the entire transaction.

Now multiply that by hundreds of requests.

Suddenly the pool appears too small.

Again, the pool may not be the original problem.

The transaction boundary might be.

---

## The connection pool can expose bad architecture

This is why I stopped treating Hikari configuration as a simple tuning exercise.

If an application needs 200 simultaneous database connections to survive normal traffic, I want to know why.

Maybe:

- N+1 queries exist.
- Transactions are too long.
- Queries are slow.
- Unnecessary round trips occur.
- Indexes are missing.
- Work is over-parallelized.

The pool can hide these problems.

Until traffic grows.

---

## There is also a connection pool inside your connection pool

The system might look like:

```text
Spring Boot
     │
 HikariCP
     │
     ▼
 PgBouncer
     │
     ▼
PostgreSQL
```

There may be multiple concurrency-control layers:

- HikariCP
- PgBouncer
- PostgreSQL `max_connections`
- Kubernetes replicas

This can be useful.

It can also become confusing if nobody knows which layer is actually limiting the system.

---

## More isn’t always more in distributed systems

This lesson appears everywhere.

- More threads can slow an application.
- More Kafka consumers can increase contention.
- More retries can create outages.
- More replicas can overwhelm dependencies.
- More cache misses can drive database traffic.
- More database connections can overload PostgreSQL.

The common mistake is believing:

**More resources = More performance**

Real systems behave more like:

```text
Resources
     ↓
Useful concurrency
     ↓
Saturation point
     ↓
Contention
     ↓
Collapse
```

Every shared resource eventually reaches a point where additional concurrency stops helping.

---

## What I would monitor now

If I had to investigate a slow Spring Boot API tomorrow, I would not start by changing:

`maximum-pool-size`

I would start by measuring.

### Application metrics

- Request rate
- p50 latency
- p95 latency
- p99 latency
- Thread pool utilization
- Connection acquisition time
- Active connections
- Idle connections
- Pending connection requests

### PostgreSQL metrics

- CPU
- Memory
- Active sessions
- Query duration
- Locks
- I/O
- Cache hit ratio
- Slow queries
- Connection count

### Query-level analysis

`EXPLAIN ANALYZE`

And the key question would be:

> *Are we waiting for a connection?*

Or:

> *Are we waiting for the database?*

Those are completely different problems.

---

## The configuration change I made taught me something

I originally thought:

`maximum-pool-size: 10`

meant:

> *Only 10 requests can use the database.*

It doesn’t.

It’s saying something closer to:

> *This application instance can hold up to this many database connections.*

And the real outcome depends on:

- Request volume
- Query duration
- Transaction duration
- Application replica count
- Database capacity
- Other workloads sharing the database

That is why the same pool size can be perfect for one service and disastrous for another.

---

## The fix wasn’t “put it back to 10”

This is important.

The lesson is not:

> *Small connection pools are good.*

That’s simply replacing one oversimplification with another.

The actual lesson is:

> *Size the pool for the workload and the capacity of the database, then verify with measurements.*

Maybe:

- 10 is too small.
- 30 is correct.
- 50 is appropriate.
- PgBouncer is needed.
- Read replicas are needed.
- Caching is needed.
- Queries need optimization.
- Transactions need shortening.
- Database resources need scaling.

Performance tuning is rarely:

**Change one number**

It’s usually:

```text
Measure
   ↓
Form hypothesis
   ↓
Change one thing
   ↓
Measure again
   ↓
Keep or revert
```

---

## The uncomfortable conclusion

That day, I started with a slow API.

I found:

`maximum-pool-size: 10`

and thought:

> *There aren’t enough connections.*

So I changed it to:

`maximum-pool-size: 50`

And accidentally made the database work harder.

Nothing was broken.

HikariCP was doing exactly what I told it to do.

Spring Boot was doing exactly what I configured.

PostgreSQL was doing exactly what PostgreSQL does.

The mistake was in my mental model.

I thought the connection pool was a gas pedal.

It wasn’t.

It was a gate.

And opening the gate wider doesn’t make the road wider.

It just lets more cars onto the same road.

---

## The database doesn’t care how optimistic your configuration is

This is probably the sentence I wish I’d understood earlier:

> *Your application can request more concurrency than your database can profitably handle.*

That’s the trap.

A pool of 100 can make the application look more concurrent.

It doesn’t mean the database can process 100 queries efficiently.

And a pool of 5 doesn’t necessarily mean your application is underpowered.

It might mean you’re deliberately keeping database concurrency within a range the system can sustain.

The right number isn’t the largest number that doesn’t immediately crash.

It’s the number that allows the entire system to operate efficiently under the workload you actually have.

---

## And now, when I see this

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 50
```

I don’t think:

> *Nice. 50 connections.*

I think:

- Why 50?
- What is the database capacity?
- How many application instances are running?
- How long do transactions last?
- What is the average query time?
- What does p99 look like?
- How many queries does one request generate?
- Are connections actually the bottleneck?
- What happens when Kubernetes scales from 4 pods to 20?
- What happens during a traffic spike?
- What happens when a query suddenly becomes 10× slower?

Those questions are far more valuable than the number itself.

---

## Because database performance has a strange rule

Sometimes the fastest way to process more work…

is to allow less work to happen simultaneously.

That sounds wrong until you watch a saturated database.

You don’t always need more concurrency.

Sometimes you need:

- Better queries
- Shorter transactions
- Fewer round trips
- Better indexes
- Caching
- More database capacity

And sometimes, yes…

a larger connection pool.

But you don’t know which one you need by staring at `maximumPoolSize`.

You know by measuring where the time actually goes.

I increased the connection pool because I thought the database was waiting for my application.

It turned out my application was waiting for the database.

And those two sentences sound almost identical.

They’re not.

One tells you to add connections.

The other tells you to investigate the database.

That difference can be the difference between fixing a production incident…

and making it worse.

So the next time an API gets slow and someone says:

> *“Increase the database connection pool.”*

I wouldn’t immediately say no.

I’d ask one question first:

> ***Are we waiting for a connection, or are we waiting for the database?***

Because until you know that…

you’re not tuning the connection pool.

You’re guessing.
