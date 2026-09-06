---
type: System Design Case
title: "URL Shortener"
description: "System design interview case for a global URL shortener with custom aliases and click analytics"
generated: { by: process:okf-migrate, at: 2026-07-15T00:00:00Z }
---

# URL Shortener

Create a URL shortener. Users should shorten their URLs and use that shortener to access the link. Users can also create their own custom short URL. Users could also see the access statistics.

## Phase 1 — Requirements Clarification (~5 min)

**Phase goal**: Confirm actors, P0 flows, failure paths, NFRs, and scope.

**How many users are projected to use it?**

Nearly 1 million URL creation per day is projected, and in total 100 million accesses are projected.

**Are there any projected peak hours?**

It's a global service and mostly the non-working hours, especially 20:00–22:00, are the peak hours related to e-shopping link usage.

**Are there any latency requirements related to the time between creation of the link and usage of it?**

There is no hard metric for this requirement.

**Do short URLs expire?**

Depends on the configuration. Default configuration should allow 1 month expiration time. After 2 months of expiration, the expired URLs cannot be used.

**Can anonymous users create and use the links?**

Both anonymous and non-anonymous users can create and use the link. However, to see the statistics, the link creator should be logged in and identified.

**What is the acceptable redirection latency?**

The redirect should feel instantaneous:

- p99 < 10 ms for URL redirections served by CDN
- p99 < 30 ms for requests served from Redis
- p99 < 50 ms for requests served from Cassandra

Creation latency SLA: p99 < 50 ms.

**What kind of analytics is needed?**

Total clicks per URL and optionally per-day breakdowns. Referrer and geographic data would be a nice bonus but not required for MVP.

**Which HTTP status code should be used for redirect?**

Default to 302 (temporary) unless the user configures it as permanent, then use 301.

**Do we need multi-region deployment?**

User base is global, hence we need low latency and high availability even if a whole region fails.

## Actors

- URL creator
- URL clicker

## Scenarios

1. User subscribe
2. Link creation
3. URL redirection
4. User login
5. Statistics collection
6. Statistics visualisation

## Phase 2 — Back-of-the-Envelope Math (~2 min)

**Phase goal**: Estimate QPS, storage, cache size, and let math eliminate impossible options.

### Traffic Estimates

Each day 1 million URL creation is projected.

```text
24 * 60 * 60 = 86,400 seconds
write = 1,000,000 / 86,400 ~= 12 req/s
read = 12 * 100 = 1,200 req/s
```

We can say that nearly 1 million URLs daily get traffic, and in this URL pool nearly 1,000 of them may be viral. In this case these 1,000 URLs may get ~80% of the traffic, which holds nearly 80 million daily traffic. These keys have the potential to create a thundering herd.

Peak times ~ 5x:

```text
write = 60 req/s
read  = 6,000 req/s
```

Statistics visualisation is normally used by admins.

```text
User count = 1,000,000 => checks screen 3 times each day
3,000,000 / 86,400 ~ 36 req/s
```

- Redirect p99 < 10 ms
- Needs to be highly available, multi-region
- Users should be directed to the nearest region. If there is an issue, users should be redirected to the nearest working region.
- 218 trillion possible URLs
- 208,000,000 days required to finish the URL pool, so 8 chars is sufficient for non-custom URLs
- URL creation will be idempotent, and generated short URLs have to be unique so that one short URL redirects to just one location

## MVP Scope

- Random and custom link creation
- Statistics API
- User subscription and login
- Statistics API will be accessed with user login

Reuse of expired links, advanced user dashboards, and social media integration will be handled in the next phase.

## Prioritization

1. URL redirection
2. Link creation
3. User login
4. User subscribe
5. Statistics collection
6. Statistics visualisation

## Phase 3 — Core Entities (~3 min)

**Phase goal**: Define the main entities, keys, relationships, and access patterns.

```sql
create table Url (
    url_part text PRIMARY KEY,
    original_url text,
    redirect_type tinyint,
    expiration_date timestamp,
    user_id bigint,
    user_region text,
    idempotency_key text,
    create_date timestamp
);

create table Click_Stat (
    url_part char(8),
    click_date datetime
);

Click_Stats_hourly {
    url_part char(8),
    click_hour datetime,
    region text,
    count number
};

CREATE TABLE click_stats_hourly (
    url_part text,
    bucket_hour timestamp,      -- e.g. 2026-07-15 14:00:00
    click_time timestamp,       -- exact click timestamp, e.g. 2026-07-15 14:23:17
    region text,
    count counter,
    PRIMARY KEY ((url_part, bucket_hour), click_time, region)
);

CREATE TABLE click_stats_daily (
    url_part text,
    bucket_day date,            -- e.g. 2026-07-15
    click_time timestamp,
    region text,
    count counter,
    PRIMARY KEY ((url_part, bucket_day), click_time, region)
);
```

### Storage Estimates

- URL record size: 90 bytes
- Click stat record size: 40 bytes

**URL**: Nearly 50 million rows (30 days expiration + extended periods) => 4.5 GB. With replicas and indexes it can be up to ~3x = 13.5 GB.

**Stats**: 100 million clicks a day * 40 bytes => 4 GB/day => 120 GB/month. With indexes and replication overhead nearly 500 GB/month. Monthly archival: a backend process can create daily stats and record them in a separate table — deferred from this design review due to time constraints. With indexes and replicas it can be up to 315 GB/month.

## Phase 4 — API Design (~5 min)

**Phase goal**: Versioned endpoints with idempotency, pagination, and structured errors.

We can use REST services. All connections will be HTTPS.

### Endpoints

#### Create URL

```http
POST /v1/createUrl
Header: idempotency-key
```

Request:

```json
{
    "user_id": 0,
    "ttl_day": 30
}
```

Response:

```json
{
    "full_url": "https://short.example/abc12345",
    "expiration_time": "2026-08-15T00:00:00Z"
}
```

Return codes:

- 200 => success
- 500 => any system errors

#### Create Custom URL

```http
POST /v1/createCustomUrl
Header: idempotency-key
```

Request:

```json
{
    "user_id": 0,
    "custom_url": "my-link",
    "ttl_day": 30
}
```

Response:

```json
{
    "full_url": "https://short.example/my-link",
    "expiration_time": "2026-08-15T00:00:00Z"
}
```

Return codes:

- 200 => success
- 409 => custom URL collision
- 500 => any system errors

#### Redirect

```http
GET <main_url>/<short_uri>/
```

- 302 with original URL
- 404 if not found
- 410 if expired

#### Statistics

```http
GET /v1/<short_uri>/statsList?startDate=<start_date>&finishDate=<finish_date>
```

Request:

```json
{
    "access_token": "<jwt_token>"
}
```

Response:

```json
{
    "day": "2026-07-15",
    "count": 1234
}
```

In `statsList`, users can only see their own URL statistics.

#### Login

```http
POST /v1/login
```

Request:

```json
{
    "email": "<user_name>",
    "password": "<password>"
}
```

Response:

```json
{
    "access_token": "<access_token>"
}
```

#### Subscribe

```http
POST /v1/subscribe
```

Request:

```json
{
    "name": "<name>",
    "surname": "<surname>",
    "email": "<email>",
    "password": "<password>"
}
```

Response:

```json
{}
```

Return codes:

- 200 => success
- 409 => already subscribed
- 500 => system error

## Phase 5 — High-Level Design (5–7 min)

**Phase goal**: Entry point, async path, database choice, caching, and load balancing.

Security: OIDC Connect + OIDC with PKCE. Static pages will be SPA. JWT tokens will be validated on API Gateway.

Components:

- Global CDN + load balancer — latency-based routing (Cloudflare)
  - Edge cache for popular redirects; redirect is handled directly on edge; stats endpoint could be called from app server set
- Regional API gateway — authentication, rate limiting, TLS termination, input validation, load balancing
- App Server Set
- Redis Cluster
- Cassandra / MongoDB

All application layers are stateless so we can scale horizontally. Since we are not using a relational database, the database layer is also horizontally scalable.

Cassandra is my choice for database since it serves sufficiently in this scenario; there is no strict consistency requirement like a payment system.

We can use cache-aside strategy to effectively use the cache. We can arrange the TTL with our needs accordingly; if we can reserve sufficient memory for our Redis cluster, we can increase TTL to increase the chance of a cache hit.

All APIs should be async and non-blocking to prevent thread pool exhaustion.

### Unique URL Generation

Custom and non-custom URLs will be stored in different tables and managed differently since they have different consistency and uniqueness requirements across regions.

#### Non-Custom URLs

We will use 8 English characters to generate the URL. URLs will be created within the application servers, and when we horizontally scale each server, I will create a Snowflake-like distributed ID generator which provides uniqueness across all servers globally.

I will create a pool of unique URLs, and when a new URL creation request comes, I will reserve and give the URL at request time. With this design, I aim to lower the URL generation overhead.

A background service will prepare the unique URLs and assure uniqueness as well. In this service we can also manage expiration. Expired URLs will not be used, but since we need to assure uniqueness, we need to check the expired ones; they will remain in the table.

After creation we need to check if the URL exists already. While parallel URL creation may cause a race condition, since we are using Snowflake-style URL generation, we can assure all regions have separate URL pools. Therefore, if we can assure that a URL is unique in a region, then it is unique globally as well. We can give an ID for each region to provide uniqueness across all regions.

#### Custom URLs

For custom URLs, I will use consistency level `ALL`, which will provide a unique custom URL on demand. There is no 8 char limit for custom URLs. However, they have to be unique just like the non-custom URLs.

In that case, the custom URL uniqueness is assured at global level.

To avoid race conditions we can use Light Weight Transactions (LWT) with a statement like below. Custom URIs can be up to 50 chars.

```sql
create table custom_url (
    url_part varchar2(100) primary key,
    user_id number,
    created_date datetime
);

INSERT INTO custom_url (url_part)
VALUES (<custom_uri>)
IF NOT EXISTS;
```

We can use write CL as `ALL` for the custom URL scenario, and this assures the uniqueness of the URL.

We can have a read consistency level of `ONE` as well. We may have stale data, but since our main focus is performance, it is acceptable for us.

#### Idempotency

Inside `/v1/createUrl` we can get the idempotency key from the header so that in a retry scenario, if the URL was created, we can return the created URL. In the custom URL scenario, we fetch the URL from the DB for the same user and return it.

### Statistics Service

Statistics are collected using Kafka and written into the `Click_stat` table. Each night a batch job can be executed to save the results inside a statistics summary table hourly to serve the stats effectively for the long term.

For instant counts, especially in an hourly window to identify hot URLs, we can use Kafka with Flink. We can write them both to Cassandra and Redis.

We can use Kubernetes for orchestration so that we can use auto-scale policies to manage scalability.

Inside Cloudflare we need to use a load-balancing algorithm that is geo-aware, latency-based, and sensitive to regional failover. On the API gateway before the app servers, we can use latency-based health-check performing load balancing.

### Failure Analysis

If response times increase, we can prioritise URL redirection over other scenarios. If we separate URL creation pods from redirection pods, in case of performance degradation we can throttle statistics, login, subscribe, and even link creation for some time to open space for redirection.

In redirection, most probably the database will be the bottleneck. After getting some space to work, we can work on the DB and address the issue.

Since Cassandra is highly available, we don't need to use additional sharding.

### Data Access Patterns

While accessing URLs, we will query by `url_part` for both custom and non-custom URLs. We can use `url_part` for URL tables.

For the statistics tables:

- `click_stats_hourly`: `url_part` and `bucket_hour` are the partition keys
- `click_stats_daily`: `url_part` and `bucket_day` are the partition keys

We will use `click_stats_daily` for the stats API and `click_stats_hourly` for heatmaps inside dashboards.

## Phase 6 — Deep Dive (~15 min)

**Phase goal**: Consistency, scaling, latency, failures, observability, and the 10× scale check.

The following deep-dive topics are covered in subsections below:

- [Observability](#observability)
- [Caching and Hot Keys](#caching-and-hot-keys)
- [Expiration Conflicts](#expiration-conflicts)
- [Security and Abuse Prevention](#security)
- [Multi-Region and Failover](#multi-region-and-failover)

The remaining deep-dive topics are covered inside Phase 5:

- Unique URL generation and consistency → [Unique URL Generation](#unique-url-generation)
- Statistics service and async analytics → [Statistics Service](#statistics-service)
- Failure analysis → [Failure Analysis](#failure-analysis)
- Data access patterns → [Data Access Patterns](#data-access-patterns)

## Observability

Since p99 < 10 ms for redirection, we need to use full-fledged tools like Dynatrace to track, and if it passes a threshold, we can create alarms.

The following statistics will be tracked.

### Service Metrics

- CDN and Redis cache hit ratio
- Cache miss and origin lookup latency
- Redirect success and expired link rate
- Rate limit count
- Code collision retries and custom alias conflicts
- Regional failover event
- Click event publish failures and analytics lag
- Hot key rate and cache stampede events

### Business Metrics

- Clicks per link
- Daily link click frequency

### Alerts

- Redirect success < 80% hourly
- Regional failover event > 1 in one day
- Analytics lag > 10 min
- Cache stampede event / total requests > 10%

### Tracing Strategy

A Dynatrace or Elastic APM-like tool can be used to trace all the services and short URL requests. Since these tools have advanced tracing capabilities, it is easy to trace all the services, and alarms can be defined to detect and solve problems proactively.

## Expiration Conflicts

For links redirected with 301, there is a risk they stay in browsers and CDNs. It is safe not to reuse a short URL after expiration. In that case we return 410 Gone after expiration.

Mostly try to use 302 and 307 for links likely to expire. Reserve 301 for permanent links. After deletion of permanent links, if a redirect request comes, 410 should be returned.

## Caching and Hot Keys

Both CDN and Redis will cache the URIs. For viral, frequently accessed links, we will redirect the link on Cloudflare without accessing app servers.

If there is a cache miss on CDN, the request will come to the app server. If the URI exists, we will return from Redis; otherwise we will update the cache (cache-aside) and return 302 with the URL. After returning 302, the Cloudflare cache will be updated. Cloudflare should be configured to cache redirects.

```text
CDN expire time < Redis expire time < URL expire time
```

For frequently accessed URLs, CDN and Redis expire times can converge to the URL expire time. In a future version, we can create a popular links service to manage the TTL of URLs both on Redis and CDN using the stored statistics.

To avoid thundering herd for popular links, we can provide a background process to revalidate these links before they expire. Additionally, we can throttle and prevent additional requests from accessing the database when a cache expires, making them wait for the first one to complete to avoid a database fetch.

When the link is deleted or expired, we will return 410.

Viral links should be handled specially to prevent thundering herd to the database. Therefore, their expiration time will be a minimum of one day, and if traffic continues, the cache will be revalidated one hour before expiration.

When cache expires on CDN, the request will be passed down. If found in Redis, the `original_url` will be returned and this URL will be cached on CDN as well.

When cache expires on Redis, the cache-aside logic is executed and `original_url` is fetched from the database and cached on Redis. To avoid thundering herd, the database fetch process should be handled using a pool or a queue, and only the first request should be sent to the database while others wait. After data is written to Redis, all others should be returned from Redis.

When a link expiration or deletion happens, Redis and CDN caches should be deleted as well. The Redis key will be deleted on the app server by the deletion code. The CDN cache can be deleted using the Cloudflare API.

## Security

While creating a URL, `original_url` should be validated using a cloud service like Microsoft Defender Threat Intelligence or Cloudflare Threat Intelligence. With this check we can prevent schemes like `file:`, `javascript:`, etc. Additionally, we can validate these fixed schemes inside the code while creating the link to add additional security.

Additionally, we can use Cloudflare WAF to prevent redirection to malicious sites.

If a user reports a URL as suspicious, it will be added to the suspicious activity queue and re-evaluated using the threat intelligence software again. Even if the threat intelligence sees this as safe, if there is a high level of flagging, an alarm can be created and these links can be flagged as suspicious for admin action.

Rate limiting will be handled both by Cloudflare and API gateway. In the API gateway we can apply both user-level and global rate limits. Hot URLs are already identified using the statistics infrastructure. Therefore, we can take action for a hot link that is getting a high click number, identify abuse, and even invalidate this key if it is not paid.

To protect our system further, we can limit the URL count that an account can create.

For anonymously created links, we need to limit the click rate, and after passing the fair usage quota, 429 will be returned.

We will have a scheduled background check to revalidate links using Microsoft Defender Threat Intelligence or Cloudflare Threat Intelligence, and block and delete the link from the database and caches. In that case, when the short link is accessed, we will return 410.

## Multi-Region and Failover

Links are created in their respective region. All links will be replicated and be eventually consistent in seconds in a normal network environment.

If a region fails, the geographically closest region will be the failover region. It will serve both its own traffic and the failed region's traffic.

During region failover, the failover region will use the failed region code while creating links for requests coming from the failed region.

## Phase 7 — Trade-offs (2–3 min)

**Phase goal**: Limitations, alternatives, deferred scope, and next bottleneck.

### Trade-offs and MVP Scope

- **Scoped out of MVP**: Reuse of expired links, advanced user dashboards, social media integration.
- **Consistency vs latency**: Custom-alias writes use `CL=ALL` for global uniqueness; redirect reads use cache-first with eventual consistency for speed.
- **Cost vs correctness**: Analytics are asynchronous and approximate where acceptable, keeping the redirect path cheap and fast.
- **Next bottleneck**: As viral links grow, per-key hot-key load and cache-stampede events will likely be the first scaling challenge.
















