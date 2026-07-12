---
type: System Design Review
title: "URL Shortener Interview Case Review"
description: "Evaluation, correctness findings, and improvement guidance for the URL shortener system design interview case"
timestamp: 2026-07-12T00:00:00Z
---

# URL Shortener Interview Case Review

> **Case reviewed**: [URL Shortener Interview Case](url-shorterner.md)
> **Overall grade**: 6.5/10
> **Potential after revision**: 8/10

## Executive assessment

This is a solid first-pass system design response. It identifies the main actors and workflows, estimates average and peak traffic, prioritizes redirection, proposes cache-aside reads, separates stateless application services, considers multi-region deployment, and includes failure handling and observability.

The main weaknesses are correctness and distributed-systems details. The design currently mixes an MVP scale of about 100 million clicks per day with billion-scale assumptions, does not store the destination URL in the core entity, uses an unsafe check-then-write code-generation strategy, and leaves global uniqueness and expiration semantics unresolved.

## What works well

- Redirection is correctly treated as the highest-priority workflow.
- Average and peak traffic are estimated instead of relying only on qualitative claims.
- The design recognizes that the read path needs caching and that the application tier can scale horizontally.
- Multi-region availability is considered early.
- Statistics are recognized as lower priority than serving redirects.
- The failure analysis proposes separating redirect capacity from creation and administrative workloads.
- Authentication and gateway responsibilities are included.

## Critical findings

### 1. Random code generation has a concurrency race

The case proposes generating a random eight-character code and checking whether it already exists. Two concurrent requests can generate the same code, both observe that it is unused, and then both attempt to write it. This is a classic check-then-write race.

Use one of these approaches instead:

- Allocate disjoint numeric ranges to workers and encode IDs with Base62.
- Use a distributed ID generator such as a Snowflake-style generator and encode the result.
- Use a database conditional insert and retry when a collision occurs.

Custom aliases must also be protected by an atomic uniqueness constraint. A Redis `SET NX` check alone should not be the source of truth.

### 2. The URL entity does not contain the destination

The redirect endpoint is present, but the `Url` entity has no `original_url` or destination field. The mapping needs to store the value to which the short URL redirects.

A minimal mapping should contain:

```text
short_code
original_url
owner_id
created_at
expires_at
redirect_type
status
home_region
```

Choose one public identifier. `public_id` and `url_part` may be redundant if the short code itself is the external key.

### 3. Global uniqueness is not designed

The requirements call for nearest-region routing and regional failover, but assigning a `user_region` field does not guarantee that a code is globally unique.

Explain where uniqueness is established:

- One authoritative home region allocates each code.
- Region-specific ranges or prefixes are allocated in advance.
- A globally coordinated ID generator allocates disjoint IDs.
- Custom aliases are routed to an authoritative region for conditional creation.

Cassandra's availability does not by itself solve conflicting active-active writes.

### 4. Consistency requirements are understated

The redirect read path may use eventual consistency because mappings are generally immutable. Creation has a strict invariant: two active destinations must never own the same short code.

Describe consistency by operation:

| Operation | Consistency expectation | Mechanism |
|:--|:--|:--|
| Create generated code | Globally unique | Distributed allocation or conditional insert |
| Create custom alias | Strong uniqueness | Authoritative conditional write |
| Redirect | Low latency and high availability | Cache-first read with database fallback |
| Analytics | Eventually consistent | Asynchronous event stream and aggregation |

### 5. HyperLogLog does not count total clicks

HyperLogLog estimates distinct cardinality. It is useful for approximate unique visitors, not for total click counts.

Use durable counters or asynchronous click events for total clicks and daily click counts. Use HyperLogLog only when the product needs an estimate of unique visitors.

### 6. Expiration conflicts with 301 redirects and code reuse

A cached 301 response can remain in browsers and CDNs after the mapping expires. Reusing the same code after two months could send different users to different destinations depending on which cache they hit.

Choose and state one policy:

- Never reuse codes; return `410 Gone` after expiration.
- Reuse only after a tombstone and a cache-safety period longer than every possible cache lifetime.
- Use `302` or `307` for expiring or mutable links and reserve `301` for permanent mappings.

For an interview answer, never reusing a code is the simplest and safest choice.

## Calculation and assumption corrections

- `62^8` is approximately 218 trillion, not 208 billion.
- The theoretical namespace does not remove collision risk when codes are randomly generated. Collision probability follows the birthday paradox, so collision handling is still required.
- 50 million URL records at 90 bytes each are approximately 4.5 GB before indexes, replication, metadata, and storage overhead. The stated 2.4 GB estimate is low.
- The click-stat estimate of 4 GB per day is only the raw payload size. Replication, indexes, partitions, compression, and retention add significant overhead.
- Define whether 100 million accesses means per day, per month, or total. The case uses it as a daily number in some places.
- A peak multiplier of five is acceptable as an initial assumption, but state how long the peak lasts and whether viral links can create a much higher per-key burst.
- Define the scope of the 10 ms p99 target. A global end-to-end p99 below 10 ms is usually unrealistic because network latency alone may exceed it. Use a regional service-processing target and a separate CDN or edge target.

## Additional design improvements

### Redirect path

Add a CDN or edge cache explicitly. Redis alone will not protect the service when one celebrity or campaign link becomes a hot key.

Recommended flow:

1. Resolve the request at the nearest healthy edge or region.
2. Check the CDN or edge cache.
3. Check the regional Redis cache.
4. On a miss, read the URL mapping store and populate the cache.
5. Return the redirect immediately.
6. Publish a click event asynchronously.

Add request coalescing, stale-while-revalidate, or hot-key replication to control cache stampedes.

### Storage model

Cassandra requires query-driven tables. Avoid one unbounded click-stat partition per URL. Bucket aggregates by URL and time:

```text
ClickAggregate
- short_code
- day_bucket
- click_count
- optional_unique_visitor_sketch
```

Use hour buckets for exceptionally hot links. An auto-incrementing bigint is also not a natural choice for an active-active Cassandra design; use a distributed ID, ULID, UUID, or avoid the internal ID.

### API design

Make methods and contracts explicit:

```text
POST /v1/urls
GET  /{short_code}
GET  /v1/urls/{short_code}/stats?from=...&to=...
POST /v1/users
POST /v1/sessions
```

Include request and response bodies, authorization rules, validation errors, `404` behavior, expired-link behavior, and `409 Conflict` for a custom-alias collision. Add an idempotency key to URL creation so a client retry after a timeout does not accidentally create multiple links.

### Security and abuse prevention

Validate destination URL schemes and block unsafe protocols. Add rate limits for anonymous creation, per-account quotas, abuse reporting, malware or phishing checks, and protection for the statistics endpoint. Do not expose statistics to a caller merely because they know the short code.

### Load balancing and observability

Use latency-based or geo-aware global routing with health checks and regional failover. Round robin may be acceptable inside a homogeneous region, but it is not sufficient as the global routing strategy.

Track at least:

- Redirect success rate and expired-link rate
- Regional redirect p50, p95, and p99 latency
- CDN and Redis hit ratios
- Cache-miss and origin lookup latency
- Hot-key rate and cache-stampede events
- Code-collision retries and custom-alias conflicts
- Click-event publish failures and analytics lag
- Regional failover events
- Rate-limit and abuse-block counts

## Recommended target architecture

```text
Client
  |
Global latency-based routing and CDN
  |
  +--> Edge cache for popular redirects
  |
Regional redirect service
  |
  +--> Regional Redis cache
  |      |
  |      +--> Regional URL mapping store
  |
  +--> Asynchronous click-event producer
           |
           +--> Event stream
                  |
                  +--> Daily aggregation store
                  +--> Optional unique-visitor sketches
```

Creation uses a separate correctness-sensitive path:

```text
Create request
  |
  +--> Validate and authorize
  +--> Allocate a globally unique short code
  +--> Conditionally store short_code -> original_url
  +--> Replicate the mapping
  +--> Return the short URL
```

## Suggested interview presentation order

1. Clarify scale, expiration, ownership, custom aliases, and redirect semantics.
2. Estimate average, peak, and viral-link traffic.
3. Design the redirect path first because it has the strictest latency requirement.
4. Design collision-free code generation and custom-alias reservation.
5. Explain storage partitioning, replication, and regional ownership.
6. Move click analytics off the synchronous redirect path.
7. Cover cache stampedes, regional failures, abuse, and observability.
8. Revisit the bottleneck and explain which trade-offs you would make for MVP.

## Final assessment

The case demonstrates good architectural instincts and is a credible starting point for a mid-level system-design interview. It would currently lose points on uniqueness under concurrency, missing destination data, multi-region write ownership, expiration semantics, and analytics correctness.

After correcting those areas, the response would be strong enough to target approximately 8/10. The most important improvement is to make the correctness invariants explicit before discussing infrastructure: every active short code maps to exactly one destination, creation is idempotent, expired codes are not ambiguously reused, and analytics cannot delay redirects.
