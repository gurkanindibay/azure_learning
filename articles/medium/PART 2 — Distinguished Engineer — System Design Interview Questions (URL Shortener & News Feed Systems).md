---
type: Article
title: "PART 2 — Distinguished Engineer — System Design Interview Questions (URL Shortener & News Feed Systems)"
source: "https://medium.com/@rameshwar.blog/part-2-distinguished-engineer-system-design-interview-questions-ec2cec657e11"
author:
  - "[[Rameshwar Singh]]"
published: 2026-05-06
created: 2026-06-20
description: "More"
tags:
  - "clippings"
---

# PART 2 — Distinguished Engineer — System Design Interview Questions

> System design interviews for senior and distinguished engineering roles focus on the candidate’s ability to architect large-scale, complex systems under real-world constraints. Altogether, this technical blog will equip the candidate with a  
> deep understanding of how to discuss, justify and diagram robust solutions to the complex system design problems.

***Let’s get started!***

## Question 1: Design a URL Shortener Service (like TinyURL)

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

## Question 2: Design a Social Media News Feed System

**Answer:** Let's first understand the problem statement followed by our step-by-step and structured approach towards solutioning.

**Problem Statement:** We need to design the core newsfeed system for a social media platform (like LinkedIn/Facebook/X) that aggregates and displays a personalised stream of posts from accounts a user follows. The feed must support millions of concurrent users, deliver new posts with low latency, handle both organic and viral content and offer features like likes, comments and real‑time updates. The platform will have global scale with high availability.

> *Now, before jumping into the solution, you should ask clarifying questions. Here is an example conversation below —*

## Clarifying Questions & Answers (With Interviewer)

> **Candidate:** Before I dive into the design, I have several questions to clarify the scope, scale and detailed requirements.
> 
> **Interviewer:** Sure. go ahead.
> 
> **Candidate**: What type of content appears in the feed?  
> **Interviewer**: Only text, image and short video posts created by users. No ads, stories or recommended content (for now).
> 
> **Candidate**: Is the feed chronological or algorithmically ranked?  
> **Interviewer**: We should start with a reverse‑chronological feed and then later we can introduce a relevance model, but for now assume the feed timeline order by creation time.
> 
> **Candidate:** Do we need real‑time feed updates (push) or is the pull‑on‑refresh sufficient?  
> **Interviewer:** Pull on refresh is the minimum need for this system. We can later add notification of “new posts available” via WebSockets, but pull must return all recent posts within <200ms.
> 
> **Candidate:** What scale are we targeting here?  
> **Interviewer:** 500 million daily active users (DAU), each follows on average 300 accounts. Users create 2 posts per day on average and load their feed ~10 times per day.
> 
> **Candidate:** Are there any privacy settings?  
> **Interviewer:** Yes, user’s posts can be public, friends only or based on a custom list. The feed must respect visibility rules.
> 
> **Candidate:** Should the feed support likes/comments and do those affect the feed itself?  
> **Interviewer:** Likes and comments exist but they don’t change the feed ordering. The feed remains purely chronological. However, we need to show like/comment counts on each post.
> 
> **Candidate:** How quickly should a new post appear in followers’ feeds after creation?  
> **Interviewer:** Within 2–3 seconds (p99), but eventual consistency (up to 10 seconds) is acceptable for non‑celebrity users(content producers).
> 
> **Candidate:** Any storage limits for posts?  
> **Interviewer:** Text up to 10KB, images/videos up to 100MB. Media is stored separately from metadata.
> 
> **Candidate**: Thank! Now I have a clear picture. I’ll list my assumptions and proceed with the architecture followed by detailed solution.

## Assumptions

- **Traffic:** 500M DAU, each averages 10 feed loads/day → 5B feed requests daily. ~58,000 feed reads/sec average, peak 5× ≈ 290,000 reads/sec.
- **Writes**: 500M DAU × 2 posts/day = 1B new posts/day, ~11,600 posts/sec average, peak ~50,000 posts/sec.
- **Social graph:** Average 300 followers per user. 1% of users are “celebrities” with >1 million followers.
- **Feed ordering:** Reverse‑chronological by post creation time. No algorithmic re‑ranking in MVP.
- **Visibility**: Checked at write time (for push) and read time (for pull) to enforce privacy.
- **Latency**: Feed load p99 <200ms; post creation acknowledged <100ms.
- **Media Type**: Images/video hosted on a CDN, post metadata only stored in databases.

## Constraints

- **High availability:** 99.95% uptime for feed reads/writes.
- **Low latency:** Feed must load quickly globally, requiring edge caching and multi‑region deployment.
- **Eventual consistency:** Feeds may lag behind post creation by a few seconds; strong consistency needed only for the post author’s own timeline.
- **Cost**: Storage required for billions of posts, cache for active timelines and bandwidth for media must be optimised.
- **Write amplification:** Fanning out posts from celebrities to millions of followers is expensive; a hybrid approach is required in this case.

## Functional Requirements

**Post creation:** Users can publish text, image or video posts.

**Follow/Unfollow:** Users can follow/unfollow other accounts. The user’s own feed needs to update accordingly.

**Feed retrieval:** Return a paginated list of recent posts from all followed accounts, in reverse‑chronological order.

**Like/Comment:** Users can like and comment on posts; aggregated counts are shown on the post.

**Privacy:** Posts respect visibility settings(only intended audiences can see).

**Real‑time notifications:** Alert users that new feed items are available (this is a stretch requirement).

## Non‑Functional Requirements

- **Scalability:** Horizontal scaling to handle spikes and long‑term growth, especially for celebrity post fanout.
- **Performance**: p99 feed load <200ms; post creation p99 <100ms.
- **Consistency**: Causal consistency for feed updates; strong consistency for post creation and own‑profile views.
- **Durability**: Once a post is created, it must not be lost.
- **Security**: Authentication, rate limiting, spam detection, content moderation hooks to be integreted in the system.
- **Operability**: Distributed tracing, comprehensive metrics, automated capacity planning.

## Back-of-the-Envelope Estimations

![Back of the Envelop Estimation Notes](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*rpgVb_TxO_Umhm7IYyITYw.png)

Back of the Envelop Estimation Notes

> We can see that the biggest challenge is the ‘write‑side fanout’! We must distribute ~3.5M feed insertions per second to followers’ timeline caches. For celebrities, we will avoid write fanout entirely for now.

## High‑Level Architecture

**The system will have a hybrid fanout model:**

- **Fanout on write** (push) for users with small to medium follower count (≤ 10k). When they post, the post ID is written directly into the Redis timeline of each follower.
- **Fanout on read** (pull) for high‑profile users (celebrities). Their posts are only stored in their own “user‑posts” timeline. When a follower(of a celebrity) loads their feed, the system will merge the below:
1. Their pre‑computed timeline (regular users’ posts)
2. Recent posts from followed celebrities (fetched on‑demand, rate‑limited).

> This hybrid design will help minimise the write amplification while keeping read latency low.

### Architecture diagram:

![High Level Architecture Design](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*1YHZkvCdt_7SrldUQhbs7A.png)

High Level Architecture Design

### Key flows:

**Post Creation & Fanout (Write Path)**

![Sequence Diagram — Write Path](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*8iwc70kwlbySgiCPNh1rIA.png)

Sequence Diagram — Write Path

**Feed Retrieval (Read Path)**

![Sequence Diagram — Read Path](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*1fE6ZvbaBOLq28gFH86iwQ.png)

Sequence Diagram — Read Path

> **CelebsCache** is a separate Redis cluster keyed by celebrity ID, holding their latest N posts. This cluster will be refreshed when a celebrity posts and read via a lazy caching approach on feed load (or a background job that do pre‑warms for celebrities!).

## API Design

All endpoints are versioned (`/api/v1`) and use OAuth 2.0 bearer tokens.

### Create Post API

- **Request:** `POST /api/v1/posts`
- **Body (multipart/form-data):** `content` (text, max 10KB), `media` (optional file), `visibility` (public/friends/private).
- **Response** `201`:
```c
{
  "post_id": "p_abc123",
  "author_id": "u_42",
  "created_at": "2026-05-02T12:00:00Z",
  "content": "Hello world!",
  "media_url": "https://cdn.social.com/media/img123.jpg"
}
```

### Get Feed API

- **Request**: `GET /api/v1/feed?cursor=<timestamp>&limit=20`

> Cursor is the `created_at` timestamp of the last post seen (for reverse‑chronological pagination requirement).

- **Response** `200`:
```c
{
  "data": [
    {
      "post_id": "p_xyz",
      "author": { "id": "u_100", "name": "Jane" },
      "content": "…",
      "created_at": "2026-05-02T11:59:00Z",
      "like_count": 59,
      "comment_count": 17,
      "media_url": null
    }
  ],
  "next_cursor": "2026-05-02T11:58:30Z"
}
```

### Follow/Unfollow API

- **Request(Follow)**: `POST /api/v1/users/{id}/follow`
- **Request(Unfollow)**: `DELETE /api/v1/users/{id}/follow`
- **Response:** Update user’s social graph & trigger asynchronous fanout of future posts from that user (or cleanup on unfollow).

### Like/Comment API

- **Request(Like)**: `POST /api/v1/posts/{id}/like`
- **Request(Comment)**: `POST /api/v1/posts/{id}/comments`
- **Response(Like):** Return updated counts. Counts are updated in Posts DB and eventually reflected in feed hydration.

## Data Model

### Posts Table (Cassandra)

![Posts Table Schema](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*FaE3giAPoTRvCeMTRqCrBg.png)

Posts Table Schema

### Materialised view (user\_posts\_by\_time)

![Materialised view user_posts_by_time](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*NfdAeJ68fEHuhW59xb5SYw.png)

Materialised view user\_posts\_by\_time

### Social Graph DB (Neptune / Composite DB)

- Stored as a graph for efficient traversals. For the MVP we can model follow relationships in a wide‑column store (Cassandra) with two tables:
- `followers` (followee\_id → set<follower\_id>) & `following` (follower\_id → set<followee\_id>). A follower count table will be maintained to decide celebrity status.

### Timeline Cache (Redis Sorted Sets)

- **Key**: `timeline:{user_id}`
- **Members**: `post_id` with score = `created_at` timestamp (milliseconds). Sorted by score descending for reverse‑chronological order.
- **Max size per timeline**: 1000 posts. Older posts are trimmed on insertion.
- **Expiry**: idle timelines TTL 30 days.

### Celebrity Post Cache (Redis List)

- **Key**: `celebrity_posts:{celebrity_id}` (list of post IDs, max 100). [Lpush](https://redis.io/docs/latest/commands/lpush/) on new post, [Ltrim](https://redis.io/docs/latest/commands/ltrim/). TTL = 7 days with lazy refresh on read miss.

### Analytics / Counters

- Like/comment counts stored in Cassandra as counter columns (or a separate Redis hash for hot counts).

### Design Deep Dives

## Tech Stack Options

- **Backend**: Go (fast, concurrency) or Java with reactive frameworks.
- **API Gateway/CDN**: CloudFront + Application Load Balancer.
- **Container Orchestration**: Kubernetes (EKS/GKE).
- **Primary Data Store**: Apache Cassandra (for posts, social graph) — horizontally scalable, multi‑DC.
- **Graph Database**: Amazon Neptune (optional; for complex graph queries we can start with Cassandra).
- **Timeline Cache:** Redis Cluster (managed ElastiCache) — each shard holds a fraction of user timelines.
- **Celebrity Cache**: Redis (separate cluster to isolate celebrity load).
- **Message Queue:** Apache Kafka (high throughput, durability).
- **Fanout Workers:** Kubernetese‑deployed consumers (Go).
- **Media Storage:** S3 + CloudFront CDN.
- **Monitoring**: Prometheus, Grafana, Elasticsearch, OpenTelemetry.

## Consistency vs. Availability Trade‑offs

### Post creation & own profile:

- **Strong consistency required:** after posting, the author must see their own post immediately on their profile or timeline. The write to Cassandra is synchronous and the post is directly inserted into the author’s own timeline cache (write‑through). So we have CP(Consistency & PArtition Tolerence) for this step.

### Feed (followers):

- The hybrid fanout model is AP(Availability & Partition Tolerance) — eventual consistency. A post appears in followers’ feeds after the fanout worker processes the Kafka event (usually under 1 second). During a Kafka/fanout delay, followers won’t see the new post, which is acceptable.
- For celebrity posts, they are pulled at feed read time, so the moment the post is written to Cassandra and the celebrity cache is updated (eventually), all followers will see it on next refresh.
- Feed reads query Redis sorted sets and have no cross‑partition coordination; they are highly available.

### Social graph changes:

- Follow/unfollow is strongly consistent (Cassandra write). However, the effect on fanout (stop receiving future posts) is asynchronous: a fanout worker cleans up the timeline after an unfollow event. Again, eventual consistency is should be fine.

Hence writes to the post author are CP while feeds are AP.

## Failure Modes & Mitigations

### Decision Tree (for feed read resilience):

![Feed read resilience- Decision Tree](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*UlUhB3thoJVRd9FPo-JAMw.png)

Feed read resilience- Decision Tree

## Security

- **Authentication**: OAuth 2.0 / JWT tokens; short‑lived access tokens.
- **Authorization**: Full CRUD on own posts; read only for feeds. Privacy checks at fanout time (store only for permitted followers) and at read time (filter by visibility). This ensures users cannot see friends‑only posts from non‑friends.
- **Rate limiting**: Per user per endpoint (for instance, 10 post creations/minute, 100 feed loads/minute) to prevent abuse.
- **Input validation:** Sanitize text content, scan uploaded media for malware.
- **Spam/Abuse:** Integrate async moderation using ML model; flag or remove offensive content.
- **Encryption**: HTTPS everywhere; media URLs signed with short‑lived tokens to prevent [hotlinking](https://en.wikipedia.org/wiki/Inline_linking).

## Monitoring & Observability

### Golden Signals:

- Feed read latency p50/p99, fanout lag (Kafka consumer offset lag).
- Post creation success/error rate.
- Cache hit ratios (timeline, celebrity).
- Throughput of Kafka topics.

### Business Metrics:

- Posts created/min, feed loads/min.
- Follows/unfollows per user.
- Celebrity fanout timings.

### Distributed Tracing:

- Trace from API gateway through fanout, Kafka, to cache updates (we can use OpenTelemetry for this).

### Alerts:

- Fanout lag > 5 seconds triggers scaling.
- Redis cluster CPU > 80%.
- Cassandra pending compactions high.
- p99 feed latency > 300ms for 5 minutes.

## Deployment / CI‑CD

![Deployment Design — CI/CD](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*ONpvy81WaYKy8OkSn5R_9Q.png)

Deployment Design — CI/CD

- **Multi‑Region Active‑Active:** Deploy full stack in at least 3 regions (for instance deploy in us‑east, eu‑west & ap‑southeast). Route users via geo‑DNS (Route 53) to nearest region.
- **Cassandra**: Multi‑region replication with NetworkTopologyStrategy, RF=3 in each DC. Writes use local quorum; reads local quorum (for feed, can use [ONE](https://docs.apigee.com/private-cloud/v4.53.01/about-cassandra-replication-factor-and-consistency-level) for faster reads, risking stale data).
- **Redis timelines:** Regional clusters only; feed loads are served locally. Fanout writes must update followers’ timelines in all regions where they reside. This can be achieved by having fanout workers in each region consume from a global Kafka (or by regional Kafka topics).
- Fanout writes only to the local region’s Redis; feeds are local and always consistent per region because a user’s timeline is stored where that user’s profile lives. If a user moves region, their timeline may need migration (rare, can be rebuilt). Alternatively, use a global Redis (cross‑region) but latency increases. For social media, it’s acceptable that a user loads their feed from the region they logged in from; their timeline is built in that region (via fanout or migration). This is a design choice!
- **CI/CD:** GitOps with ArgoCD & canary deployments.
- **Testing**: Integration tests with staging environment. Load tests using custom scripts.

## Cost/Operational Trade‑offs

**Fanout‑on‑write vs. Fanout‑on‑read:**

- *Full fanout on write* (push for all) would generate 300× more writes to Redis (for each post, 300 insertions), leading to a huge Redis cluster and network costs. For celebrities, 1M \* 11.6k posts would become impossible to handle.
- *Full fanout on read* (pull for all) would make feed load very slow (fetching from 300+ user timelines, merging). Not acceptable for latency.

> **Hybrid balances both the above scenarios:** normal users (99% of writes) fanout on write; celebrities (1% of users, but high followers) fanout on read. Reduces total fanout work by ~90% while keeping feed load fast. The cost is additional complexity and a separate celebrity cache.

**Timeline cache vs. DB‑only:**

- Without cache, every feed load would require heavy Cassandra joins. Redis adds cost but reduces latency from 100ms+ to <5ms per timeline fetch.

**Regional fanout vs. global fanout:**

- If timelines are regional, fanout only needs to write to one region’s cache, reducing cross‑region traffic. However, if a user travels, their feed may be empty until rebuilt. We can rebuild on first feed load by pulling from their followed users’ timelines (expensive but rare). Acceptable trade‑off!

**Media storage:**

S3 intelligent‑tiering and CDN keep will keep costs manageable.

## Testing Strategies

- **Unit tests:** Write tests fortimeline merge logic, visibility filtering & cursor pagination.
- **Integration tests:** Spin up Cassandra, Redis, Kafka in containers; test full post‑to‑feed flow.
- **Load tests:** Simulate 300k concurrent feed reads while injecting 50k posts/sec; measure p99 latency and fanout lag.
- **Chaos/Resilience tests:** Kill Redis primaries, Kafka brokers; simulate network partitions between regions.
- **Soak tests:** Run typical workload for 48h to detect memory leaks and Cassandra compaction issues.
- **Canary testing:** Deploy new fanout algorithm to 1% users and compare feed freshness/latency.

## Alternative Approaches

### Pure push (fanout on write) for all users:

Not scalable for celebrities; leads to hot partitions and unbounded write amplification.

### Pure pull (fanout on read) for all:

In this case, no fanout service, but feed load time grows linearly with number of followees. For 300 followees, merging is acceptable (<100ms) if caches are fast; but with 1000+ followers it will degrade significantly. Some platforms (like early Twitter) used a read‑based approach before switching.

### Materialised feeds in a columnar store:

Pre‑compute and store feeds in a wide‑column database (for instance, HBase). Each user’s feed is a row with many columns (post IDs). This is similar to Redis timelines but on disk, less performant.

### Graph database for feed generation:

Query the social graph directly at read time to fetch recent posts. This is slow without extensive caching.

### Use a timeline as an event stream (Kafka topic per user):

Each user’s feed is now a compacted Kafka topic. Reads become streaming consumers, too heavy for simple pull.

### Real‑time push via WebSockets:

Add server‑sent events or WebSocket connection to push new posts to active clients, reducing the need for frequent polling. Our design can be extended with this!

## References

[https://redis.io/docs/latest/commands/zremrangebyrank/](https://redis.io/docs/latest/commands/zremrangebyrank/)

[https://redis.io/docs/latest/commands/zadd/](https://redis.io/docs/latest/commands/zadd/)

[https://redis.io/docs/latest/commands/zrevrange/](https://redis.io/docs/latest/commands/zrevrange/)

[https://kafka.apache.org/42/design/design/](https://kafka.apache.org/42/design/design/)