---
type: System Design Case
title: "Question 1: Design a URL Shortener Service (like TinyURL)"
source: "https://medium.com/@rameshwar.blog/part-2-distinguished-engineer-system-design-interview-questions-ec2cec657e11"
author:
  - "[[Rameshwar Singh]]"
published: 2026-05-06
created: 2026-06-21
description: "System design walkthrough for a high-scale URL shortening service: requirements, key generation, cache-aside redirect flow, analytics, multi-region deployment, and trade-offs."
tags:
  - "clippings"
---

# Question 1: Design a URL Shortener Service (like TinyURL)

**Answer:** Let's first understand the problem statement followed by our step-by-step and structured approach towards solutioning.

**Problem Statement:** We need to design a high‑scale URL shortening service (like Bitly or TinyURL) that converts a long URL into a short unique alias. When a user accesses the short URL the service redirects them to the original long URL. The system must handle billions of URLs, serve redirections with very low latency and support optional features such as custom aliases, expiration, and basic click analytics.

> *Now, before jumping into the solution, you should ask clarifying questions. Here is an example conversation below —*

## Clarifying Questions & Answers (With Interviewer)

> **Candidate:** Before I dive into the design, I have several questions to clarify the scope, scale and detailed requirements.
> 
> **Interviewer:** Sure. go ahead.
> 
> **Candidate**: *What is the expected read-to-write ratio?*  
> **Interviewer**: Heavily read‑dominant; you can assume it as 100:1.
> 
> **Candidate:** *Should we support custom short aliases in addition to auto‑generated ones?*  
> **Interviewer:** Yes, users can optionally propose a custom alias, but it must be unique. If taken, you must reject the request.
> 
> **Candidate:** *Do short URLs ever expire or do they live forever?*  
> **Interviewer:** Both cases are possible for this scenario: users can set an optional TTL for each URL. After expiry, the alias should no longer redirect.
> 
> **Candidate:** *Are we building a service for general public use or only for the authenticated users?*  
> **Interviewer:** Anyone can shorten a URL anonymously, but you’ll need an account for management (update/delete) and to see detailed analytics.
> 
> **Candidate:** *What kind of analytics do we need?*  
> **Interviewer**: Total clicks per short URL and optionally per‑day breakdowns. Referrer and geographic data would be a nice bonus but not required for the MVP.
> 
> **Candidate:** *What’s the scale we’re targeting?*  
> **Interviewer**: 100 million new URLs per month and around 10 billion redirects per month. Peak traffic can spike to 5× the average.
> 
> **Candidate:** *What’s an acceptable redirection latency?*  
> **Interviewer**: The redirect should feel instantaneous; ideally p99 < 10 ms from any edge location worldwide.
> 
> **Candidate:** *What HTTP status code should we use for redirects?*  
> **Interviewer**: Default to 301 (permanent) unless the user explicitly marks it as temporary then use 302.
> 
> **Candidate:** *Are there any special security requirements, like blocking malicious URLs?*  
> **Interviewer**: Yes, validate that the long URL is a valid HTTP/HTTPS link. Integrate with a blocklist to reject known phishing/malware domains.
> 
> **Candidate:** *Do we need multi‑region deployment?*  
> **Interviewer**: Our user base is global; hence we do need low latency everywhere and high availability even if a whole region fails.
> 
> **Candidate:** *Is there a specific short URL length we should target?*  
> **Interviewer**: Short as possible but must support trillions of unique values; 7‑character Base62 seems reasonable and gives 62⁷ ≈ 3.5 trillion combinations.
> 
> **Candidate**: Thank you! With these clarifications, I have now good enough information to move forward. I’ll start writing down my assumptions and proceed with the technical solution.

## Assumptions

- **Traffic pattern:** Heavily read‑dominant — ~100:1 read/write ratio.
- **Short URL length:** 7 characters (Base62 encoding gives 62⁷ ≈ 3.5 trillion unique values).
- **Link Lifecycle:** Once created, short URLs are mostly immutable (no frequent updates).
- **Alias uniqueness:** System‑assigned aliases are globally unique; custom aliases are checked for uniqueness before acceptance.
- **Redirection:** Permanent redirects (HTTP 301) by default, with optional temporary redirects (302).
- **User accounts:** Optional; anonymous shortening is allowed, but advanced analytics/management require authentication.
- **Expiry:** URLs can have an optional TTL, after which they are automatically removed.
- **Global access:** Users from all over the world, no regional restrictions.
- **Scale:** 100 million new URLs created per month, 10 billion redirects per month.

## Constraints

- **Latency:** Redirect must complete in < 10 ms (p99) from edge locations.
- **Availability**: 99.99% uptime for redirection (reads); 99.9% for writes.
- **Durability**: No accepted long URL may be lost; all mappings must persist.
- **Uniqueness**: No two different long URLs shall ever receive the same alias.
- **Domain**: We own a fixed domain (like short.ly ). Each short URL includes only the token after the
- **Cost**: Infrastructure must be optimised for a read‑heavy and high‑throughput workload.

## Functional Requirements

**Shorten URL:** Given a long URL, return a short URL with a unique, auto‑generated alias.

**Custom alias (optional):** Allow users to propose a custom alias; reject if already taken.

**Expiry (optional):** Support setting a TTL for the short URL.

**Redirection:** Resolve a short alias and issue a 301/302 redirect to the original URL.

**Click analytics:** Track the number of clicks per short URL, optionally with referrer/geo data.

**URL management:** Allow authenticated users to update, delete or view their own short URLs.

## Non‑Functional Requirements

- **Scalability**: Horizontal scaling to handle traffic spikes(for instance 100M DAUs, 1B total URLs) and long‑term growth.
- **Availability:** ~99.99% uptime; minimal downtime on redirects.
- **Performance**: p99 latency < 10 ms for uncached redirects, < 2 ms when served from cache.
- **Consistency**: Strong consistency for alias assignment; eventual consistency acceptable for analytics. Additionally, read-after-write is not strictly required; eventual consistency is acceptable (short delay  
	in new URL propagation).
- **Operability**: Health checks, metrics, logging & distributed tracing.
- **Security**: DDoS protection, input validation, rate limiting & phishing/malware prevention.

## Back of the Envelope Estimations

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9NkXiMl_ZHPTWP6NQrcsHQ.png)

These numbers show a read‑heavy service that can fit state in a few terabytes, easily cacheable in memory, and manageable with a handful of application servers.

**Storage estimation (5‑year horizon):**

- Total URLs over 5 years = 100M/month \* 60 months = 6 billion.
- **Per record:** alias (7 bytes) + original URL (avg 100‑500 bytes, let’s use 200) + metadata (user\_id, timestamps, TTL, flags) ≈ 100 bytes → roughly 300 bytes per mapping.
- **Raw data:** 6 × 10⁹ × 300 bytes ≈ 1.8 TB.
- **Plus overhead/indexes:** ~3 TB total. DynamoDB or Cassandra will comfortably handle this with 3x replication.

**Cache sizing:**

- Assuming 20% of all URLs are “actively accessed” on a given day that is 6B total URLs (after 5 years) × 20% = 1.2B active. But realistically, most activity is on recent URLs — a better model: the last 100 million URLs (one month’s worth) account for 90% of redirects. So cache should hold ~100 million entries.
- **Each cache entry:** alias (7) + original URL (200) + Redis overhead → ~250 bytes.
- Memory = 100M × 250 bytes = 25 GB. With 2 DCs, each Redis cluster needs ~30 GB (including replication). Easily fits on a couple of nodes.

**Throughput:**

- **Average redirects per second:** 10B / (30\*24\*3600) ≈ 3850 req/s. Peak ~20k req/s.
- Each redirect involves one Redis `GET` (cache hit) or one DynamoDB `GetItem` (miss) + Redis `SET` + Kafka produce. At 20k req/s, a few dozen application instances are enough.

## High‑Level Architecture

The architecture needs to separate the **writes (shortening)** and **reads (redirect) mechanisms**, while analytics will be handled asynchronously.

Below are detailed sequence diagrams for key flows and a deployment diagram.

![Sequence Diagram — URL Shortening High Level Flow](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*uCmC5g3Qj_nI2eGBv55M0w.png)

Sequence Diagram — URL Shortening High Level Flow

### Key Generation Service

The KeyGen service uses a fleet of workers, each holding an exclusive range of 64‑bit integer IDs. A worker converts its next integer to a Base62 7‑char string. Ranges are allocated by a simple coordinator (or via a database sequence). If a worker crashes, its unused range is lost (acceptable because the namespace is 3.5 trillion). See diagram below:

![Key Generation Service Flow](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*KtTNWHnuj_hGAxtSwYoDbA.png)

Key Generation Service Flow

### Custom Alias Flow (Conflict Check)

![Custom Alias Conflict Check Flow](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*pdOXoq0OhpKrchOGFX0CsQ.png)

Custom Alias Conflict Check Flow

### Redirect Flow with Cache‑Aside Pattern and Analytics

![Redirect Flow with Analytics](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*wQRkl7Dk7B00dQtv1VYoNA.png)

Redirect Flow with Analytics

### High‑Level Deployment Diagram (Multi‑Region)

![Depoloyment Design](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*MMO7MuVEXe-PTalCvbrg-w.png)

Deployment Design

## API Design

All APIs will be versioned (`/api/v1`) and served over HTTPS.

### Shorten a URL(base API)

`POST /api/v1/urls`

**Request body:**

```c
{
  "long_url": "https://example.com/very-long-path?param=value",
  "custom_alias": "optional-alias",       // optional
  "expiry_seconds": 86400                 // optional TTL
}
```

**Response (201 Created):**

```c
{
  "short_url": "https://short.domain/abc123",
  "alias": "abc123",
  "long_url": "https://...",
  "created_at": "2026-05-01T10:00:00Z",
  "expires_at": "2026-05-02T10:00:00Z"   // if set
}
```

**Errors:** 400 (invalid URL), 409 (custom alias taken), 429 (rate limited).

### Redirect API

**Request:** `GET /api/v1/urls/{alias}`

**Response:** 301 Moved Permanently (or 302) with `Location` header set to the original URL.

**Errors**: If alias not found or expired: 404.

### Get Statistics API

**Request:** `GET /api/v1/urls/{alias}/stats` Requires authentication (API key/JWT).

**Response:**

```c
{
  "alias": "abc123",
  "total_clicks": 12345,
  "clicks_per_day": {"2026-04-30": 120, ...}
}
```

### Delete/Update URL (authenticated) API

`DELETE /api/v1/urls/{alias}`, `PUT /api/v1/urls/{alias}` (to change the target URL) – restricted to the owner.

### Rate limiting headers(applicable to all above APIs):

- `X-RateLimit-Limit: 10`
- `X-RateLimit-Remaining: 9`
- `X-RateLimit-Reset: 1620000000`

## Data Model

### Primary Store: URL Mappings (DynamoDB)

![Data Model: ShortenedURL Table](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ilq2jqAwlK5_U3Pi0JwnJA.png)

Data Model: ShortenedURL Table

- **Access pattern:** `GetItem` by `alias` for redirection. Global table with multi‑region replication for high availability and low‑latency reads worldwide.

### Cache: Redis

- Key: `alias:{alias}` → value: `original_url`
- TTL set to remaining lifetime of the URL (or a fixed hot‑window like 24h). Write‑through from the Shorten Service when a new URL is created or refreshed on cache miss.

### Analytics Store: ClickHouse

- Table `click_events`:
![Data Model: Click_Events Table](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-xh-SWlcoqPfWSHWP9FCqw.png)

Data Model: Click\_Events Table

### Design Deep Dives

## Tech Stack Options

- **API services:** Go (high performance, low GC) or Java (with Spring WebFlux) for non‑blocking I/O.
- **Cache:** Redis Cluster (AWS ElastiCache/ similar or self‑managed).
- **Primary DB:** Amazon DynamoDB (managed, auto‑scaling, multi‑region) or Apache Cassandra.
- **Message Queue:** Apache Kafka for click event ingestion.
- **Stream Processing:** Apache Flink (exactly‑once processing for accurate counts).
- **Analytics DB:** [ClickHouse](https://clickhouse.com/docs/intro) (fast OLAP). (You can use DuckDB for local performance OLAP tests)
- **Key Generation:** [Snowflake‑inspired ID](https://en.wikipedia.org/wiki/Snowflake_ID) generator deployed as a set of co‑located services that pre‑allocate ID blocks.
- **API Gateway / Load Balancing:** AWS ALB + Global Accelerator or CloudFront for edge caching/TLS.
- **Container Orchestration:** Kubernetes (EKS/GKE) for all stateless services.
- **Observability:** Prometheus, Grafana, OpenTelemetry, Elasticsearch for logs.
- **CI/CD:** GitHub Actions / ArgoCD, container registries, infrastructure as code (Terraform).

## Consistency vs. Availability Trade‑offs

**Write path (shortening):**

- Uniqueness is critical — duplicate aliases would break the service. For system‑generated aliases, the Key Generation Service pre‑allocates guaranteed‑unique IDs, so no check is necessary at write time → strong consistency without coordination.
- For custom aliases, we must perform an atomic check‑and‑set. Using [DynamoDB](https://en.wikipedia.org/wiki/Amazon_DynamoDB) with `ConditionExpression` (`attribute_not_exists(alias)`) ensures strong consistency (serialisable isolation). If the custom alias is taken, the request fails immediately (CP over AP).

**Read path (redirection):**

- The service prioritises availability and low latency. Redis serves the vast majority of reads, with eventual consistency between cache and DB. A cache miss falls back to the strongly consistent DB.
- In a rare case of DB outage, we can serve stale data from the cache (contingency), sacrificing strict consistency for availability. This is an acceptable AP trade‑off.

> **CAP summary:** Shortening is CP (with a twist of pre‑generation to avoid coordination); redirection is AP (via caching).

## Failure Modes & Mitigations

![Failure Handling Scenarios](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*2viDJUNfwZ-mWB2TmBOK-g.png)

Failure Handling Scenarios

### Cache failure

![Cache failure decision tree](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*jXrj8ACHmbYLnjB8ANPvbA.png)

Cache failure decision tree

We also need to cover race condition during custom alias creation: Two clients can propose the same alias simultaneously. DynamoDB’s `ConditionExpression` ensures only one succeeds atomically; the other gets a 409 Conflict. No application‑level locking needed.

### KeyGen coordinator failure:

If the range allocator (for example, a single PostgreSQL instance) fails, workers continue using their existing, unexhausted ranges. They can operate for hours before depleting. A standby coordinator with an auto‑increment sequence in a replicated DB (e.g., CockroachDB or multi‑Aurora) will eliminate this [SPOF](https://en.wikipedia.org/wiki/Single_point_of_failure).

## Security

- **Transport**: Enforce HTTPS everywhere ([HSTS](https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security)).
- **Input validation**: Reject non‑HTTP/HTTPS URLs (prevent `javascript:` or `file:` schemes).
- **Validate URL format**, length limits (2048 chars) and blocklist known malicious domains (via integration with a threat intelligence feed).
- **Authentication & Authorisation**: Anonymous users can shorten; authenticated users (OAuth2/OIDC) can manage.
- **API keys for programmatic access**, scoped to specific functions.
- **Rate Limiting:** Global rate limit per IP and per API key.
- **Prevent abuse:** e.g., 10 URL creations per minute per IP; 1000 redirects/min per IP.
- **Abuse reporting**: Users can flag short URLs for review; admin API to disable.

> A third‑party API like Google Safe Browsing can be called asynchronously before creating the short URL; if flagged, the request is rejected.)

## Monitoring & Observability

### Golden signals:

- **Latency**: p50/p99 of shorten and redirect APIs.
- **Throughput**: requests per second per endpoint.
- **Error rate**: 4xx/5xx ratios.
- **Saturation**: CPU, memory, Redis connection pool, DB consumed read/write capacity.

### Business metrics:

- Number of URLs created per minute, redirects per minute, cache hit ratio.
- Daily active aliases, total aliases.

### Logs:

- Structured JSON logs (correlation IDs) shipped to Elasticsearch.

### Distributed Tracing:

- OpenTelemetry traces across all services (Kafka -> Flink -> DB).

### Alerts:

- p99 redirect latency > 10 ms.
- Cache hit ratio drops below 90%.
- Key Generation Service unavailable.
- DB write throttling events.

## Deployment & CI/CD

![Deployment Design — CI/CD](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*WX6JDuZWG3I0s-OTzkixOw.png)

Deployment Design — CI/CD

### Infrastructure as Code:

- Terraform defines all cloud resources. Kubernetes manifests (Helm) deploy the applications.

### CI Pipeline (GitHub Actions):

- Run unit tests, linting, static analysis.
- Build container images, tag with git SHA, push to registry.
- Run integration tests (spin up ephemeral environment).

### CD Pipeline (ArgoCD):

- Monitor Helm chart repository; deploy to staging first.
- **Promote to production via canary deployment:** redirect 5% → 25% → 100% of traffic while monitoring error/latency metrics.
- Automated rollback on metric degradation.

### Multi‑region Deployment:

- Deploy independent stacks in two or more AWS regions.
- Use Route 53 latency‑based routing.
- DynamoDB global tables replicate mappings.
- Redis clusters to be region‑local.

## Cost / Operational Trade‑offs

### Option A: Use managed services (DynamoDB, ElastiCache, MSK)

- ***Pros***: Low operational burden, auto‑scaling, built‑in HA.
- ***Cons***: Higher per‑operation cost. At 10B redirects/month, DynamoDB read costs can become significant.
- ***Mitigation***: Heavy caching (Redis) reduces DB reads by ~90%; reserve capacity for predictable throughput.

### Option B: Self‑managed Cassandra + Redis on Kubernetes

- ***Pros***: Lower marginal cost at scale, more control.
- ***Cons***: Requires expert operational effort, durability tuning, backup/restore automation.

### Pre‑generation of keys vs. on‑the‑fly hashing

- **Pre‑generating (token service)** eliminates collision checks and makes writes simpler, but requires a stateful service that must be highly available. It also wastes some keys if a node loses its allocated block (acceptable at 62⁷ space).
- **On‑the‑fly hashing (e.g., MD5 of long URL +** [**salt**](https://en.wikipedia.org/wiki/Salt_\(cryptography\))**)** introduces collision risk; handling collisions ([linear probing](https://en.wikipedia.org/wiki/Linear_probing)) complicates the DB and slows down URLs.

> For our current scenario we can choose pre‑generation for its predictable performance and simplicity.

### Cache eviction policy

- [LRU eviction](https://bytebytego.com/guides/top-8-cache-eviction-strategies/) with TTL expiry. Sufficient memory for active set is essential; monitoring active aliases prevents surprise evictions. Over‑provisioning cache by ~30% gives headroom for viral events.

## Testing Strategies

### Unit tests:

- Cover ID encoding/decoding, URL validation, business logic.
- Base62 encoding, URL validator, KeyGen logic.

### Integration tests:

Test API ↔ DB ↔ Cache interactions using test containers (DynamoDB local, Redis).

### Load tests:

Simulate realistic traffic (for instance, 20k redirects/s) using k6 or [Locust](https://locust.io/). Verify p99 latency under load and no cache breakdown.

### Chaos engineering(Resilience Tests):

- Kill Redis primary, measure failover time.
- Induce DB primary node failure, observe read/write behaviour.
- Block network to Key Generation Service, verify graceful degradation (writes queue up).

### Soak tests:

- Run 3x normal load for 24 hours to detect memory leaks or DB capacity exhaustion.

### Security tests:

Penetration testing, fuzzing of URL inputs, SQL/NoSQL injection attempts.

### Component tests:

- DynamoDB Local + Redis testcontainer, verify alias creation and redirection.

### Contract tests:

For Kafka schema evolution (Avro), ensure producer/consumer compatibility.

### Performance tests:

K6 script that mimics 10k concurrent users creating and redirecting. Measure p95/p99.

## Alternative Approaches

### Hash‑based URL shortening (no token service):

- Compute a hash (SHA‑256) of the long URL, take first 7 chars of base64‑encoded hash. Check for collisions. Simpler architecture, but requires read‑before‑write and collision retries, which is problematic at high scale.

### Relational database (PostgreSQL) as primary store:

- Viable for smaller scale, but sharding and cross‑region replication are complex. DynamoDB/Cassandra offer better horizontal scaling and built‑in multi‑region.

### Using ZooKeeper/etcd for ID generation:

- Instead of a custom token service, use distributed coordination to assign ID ranges. This adds a new distributed consensus dependency; can be used but overkill for a simple counter.

### Lambda‑based serverless architecture:

- AWS Lambda + API Gateway + DynamoDB. This design is good for spiky workloads but cold starts may violate latency SLO; Provisioned Concurrency can mitigate but costs increase. We should prefer containerised services for consistent performance and control.

### Edge redirect with Cloudflare Workers:

- Short URL redirects can be entirely served from edge (KV store). Extremely low latency, but limits analytics richness and custom alias logic. Our architecture uses CDN caching for basic edge acceleration but keeps redirect logic centralised for full control.

