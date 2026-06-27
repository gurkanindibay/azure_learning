---
type: Reference
title: "API Design Patterns"
description: "The mechanism for evolving an API without breaking existing clients."
timestamp: 2026-06-14T00:00:00Z
---

# API Design Patterns

> **Domain**: API versioning, rate limiting, pagination, error design, and compatibility patterns.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| API Versioning | [`#api-versioning`](#api-versioning) |
| Rate Limiting | [`#rate-limiting`](#rate-limiting) |
| Pagination (Cursor vs Offset) | [`#pagination-cursor-vs-offset`](#pagination-cursor-vs-offset) |
| RFC 7807 Problem Details | [`#rfc-7807-problem-details`](#rfc-7807-problem-details) |
| Expand-Contract Pattern | [`#expand-contract-pattern`](#expand-contract-pattern) |
| Idempotency-Key | [`#idempotency-key`](#idempotency-key) |
| HATEOAS | [`#hateoas`](#hateoas) |
| Long-Running Operations | [`#long-running-operations`](#long-running-operations) |
| Contract-First Design | [`#contract-first-design`](#contract-first-design) |
| Consistent Hashing | [`#consistent-hashing`](#consistent-hashing) |
| Nagle's Algorithm / TCP_NODELAY | [`#nagles-algorithm--tcp_nodelay`](#nagles-algorithm--tcp_nodelay) |
| ETag | [`#etag`](#etag) |
| JSON Merge Patch | [`#json-merge-patch`](#json-merge-patch) |
| Sparse Fieldsets | [`#sparse-fieldsets`](#sparse-fieldsets) |
| Migration-Driven Deprecation | [`#migration-driven-deprecation`](#migration-driven-deprecation) |
| Deprecation Header | [`#deprecation-header`](#deprecation-header) |
| Hierarchical Rate Limiting | [`#hierarchical-rate-limiting`](#hierarchical-rate-limiting) |
| Sunset Header | [`#sunset-header`](#sunset-header) |
| API Gateway | [`#api-gateway`](#api-gateway) |
| Hotlinking | [`#hotlinking`](#hotlinking) |
| Faceted Search | [`#faceted-search`](#faceted-search) |

---

## API Versioning

The mechanism for evolving an API without breaking existing clients.

| Strategy | Mechanism | Pros | Cons |
|:---|:---|:---|:---|
| **URL path** | `/v1/users`, `/v2/users` | Explicit, CDN-friendly | URL pollution |
| **Accept header** | `Accept: application/vnd.api+json;version=2` | Clean URLs, REST-pure | Hard to test in browser |
| **Query param** | `/users?version=2` | Simple | Not RESTful, not recommended |
| **Stripe two-tiered** | URL path + API-Key date pin | Zero breaking changes | Complex key management |

### Deprecation Lifecycle

```
Announce (Sunset header) → Signal (Deprecation header) → Notify (warning) → Retire (410 Gone)
```

**Also see**: [Expand-Contract Pattern](#expand-contract-pattern), [Contract-First Design](#contract-first-design)

---

## Rate Limiting

Controls the number of requests a client can make in a time window, protecting the API from abuse and ensuring fair resource allocation.

### Algorithms

| Algorithm | Mechanism | Limitation |
|:---|:---|:---|
| **Fixed Window** | Count requests in fixed intervals | Double-burst at boundaries |
| **Sliding Window Log** | Timestamp per request in Redis sorted set | Memory-intensive |
| **Sliding Window Counter** | Weighted count based on previous window | Approximate but efficient |
| **Token Bucket** | Tokens refill at steady rate; burst allowed | Best balance of accuracy and performance |
| **Leaky Bucket** | Fixed output rate; queue overflows rejected | Smooths but doesn't allow bursts |

### Communication Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 743
X-RateLimit-Reset: 1620336000
Retry-After: 3600
```

> Every response must include rate limit headers. A 429 response must always include `Retry-After`.

**Also see**: [Resilience](resilience.md)

---

## Pagination (Cursor vs Offset)

| Aspect | Offset (`LIMIT x OFFSET y`) | Cursor / Keyset (`WHERE id > ? LIMIT x`) |
|:---|:---|:---|
| **Performance** | Degrades with depth (scans skipped rows) | Stable — uses index seek |
| **Stability** | Duplicates/misses on insert/delete | Stable — cursor is a fixed point |
| **Jump to page N** | Yes | No (forward/backward only) |
| **Use case** | Static data, admin tools, search engine results | Live feeds, infinite scroll, real-time data |

> **The +1 Fetch Trick**: Request `N+1` items but return `N`. If the extra item exists → there's a next page.

**Also see**: [Data & Concurrency](data-concurrency.md)

---

## RFC 7807 Problem Details

Standardized error response format for HTTP APIs. Every error response must be actionable.

```json
{
  "type": "https://api.example.com/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account 12345 has balance 50.00 USD. Required: 100.00 USD.",
  "instance": "/transfers/txn-abc-123",
  "request_id": "req-xyz-456",
  "error_code": "INSUFFICIENT_FUNDS"
}
```

| Field | Purpose |
|:---|:---|
| `type` | URI to human-readable error documentation |
| `title` | Short, human-readable summary |
| `status` | HTTP status code |
| `detail` | Human-readable explanation specific to this occurrence |
| `instance` | URI identifying the specific request |
| `request_id` | Correlation ID for debugging |
| `error_code` | Machine-readable code for client logic |

**Also see**: [Contract-First Design](#contract-first-design)

---

## Expand-Contract Pattern

A backward-compatible evolution strategy for API changes.

```
Phase 1: EXPAND — Support both old and new fields (dual-write or computed)
Phase 2: MIGRATE — All consumers move to new fields
Phase 3: CONTRACT — Remove old fields (only when no consumers remain)
```

**Rule**: **Never remove or rename a field**. Always add new fields, migrate consumers, then remove.

**Also see**: [API Versioning](#api-versioning)

---

## Idempotency-Key

A unique key per business intent sent by the client. The server stores the key + response. On retry, the server returns the stored response without re-executing.

```
POST /transfers
Idempotency-Key: txn-abc-123
```

> Idempotency keys must be tied to the **business action** — not the HTTP request, session, or client instance.

**Also see**: [CQRS & Event-Driven: Idempotency](cqrs-event-driven.md#idempotency) · [Data & Concurrency](data-concurrency.md)

---

## HATEOAS

**Hypermedia as the Engine of Application State** — API responses include links to related actions the client can take next. Enables discoverability and reduces client hard-coding of URLs.

```json
{
  "id": "txn-123",
  "status": "pending",
  "_links": {
    "self": { "href": "/transfers/txn-123" },
    "cancel": { "href": "/transfers/txn-123/cancel" },
    "status": { "href": "/transfers/txn-123/status" }
  }
}
```

**When to use**: Public APIs with multiple client types. **When to skip**: Internal service-to-service communication, performance-critical paths.

---

## Long-Running Operations

Pattern for operations that exceed typical HTTP timeout. **Return 202 Accepted immediately**, provide a job ID, and let the client poll or receive a webhook when complete.

```
POST /exports          → 202 Accepted + { "job_id": "exp-456", "status_url": "/exports/exp-456" }
GET  /exports/exp-456  → 200 { "status": "processing", "progress": 65 }
                      → 200 { "status": "complete", "result_url": "..." }
```

**Also see**: [Messaging](messaging.md)

---

## Contract-First Design

Define the API contract (OpenAPI/Swagger) **before** writing implementation. The contract is the source of truth for both server and client.

| Benefit | Detail |
|:---|:---|
| **Single source of truth** | Both teams work from the same spec |
| **Client SDK generation** | Auto-generate from OpenAPI |
| **Validation** | Contract testing before integration |

**Also see**: [API Versioning](#api-versioning), [Expand-Contract Pattern](#expand-contract-pattern)

---

## Consistent Hashing

A distributed hashing technique that minimizes key redistribution when nodes are added or removed. Used for request affinity, distributed caching, and partition assignment.

| Property | Detail |
|:---|:---|
| **Ring structure** | Hash space organized as a circle |
| **Node addition** | Only ~1/N keys remapped |
| **Virtual nodes** | Multiple points per physical node for even distribution |

**Also see**: [Caching](caching.md) · [Messaging: Partition](messaging.md#partition)

---

## Nagle's Algorithm / TCP_NODELAY

**Nagle's Algorithm** — a TCP optimization (RFC 896) that buffers small outgoing packets to coalesce them into larger segments before transmission. Disabled by setting the socket option `TCP_NODELAY=true`.

### Key Characteristics
- **Enabled by default** (`TCP_NODELAY=false`) on most platforms, including JVM sockets
- Waits for ACK of previous packet OR until buffer fills to MSS (Maximum Segment Size) before sending
- Reduces TCP header overhead for workloads that produce many small writes (e.g., telnet, character-by-character)
- **Go's `net/http` disables Nagle by default** since Go 1.7 for HTTP servers
- The interaction with HTTP/1.1 persistent connections and multi-write responses can add 40+ ms of artificial latency

### When to Use (TCP_NODELAY=true)
- HTTP services writing complete responses (headers + body) — the response is one logical unit; buffering adds latency
- Latency-sensitive APIs where 40 ms is unacceptable
- Services using persistent HTTP/1.1 connections with multi-write response patterns

### When NOT to Use (TCP_NODELAY=false, Nagle enabled)
- Workloads that produce many tiny writes where TCP header overhead dominates (rare for HTTP services)
- Interactive terminal protocols (telnet, SSH) where the original optimization was designed

### Also see
- [Virtual Threads](../reference-dictionary/java-jvm.md#virtual-threads) — concurrency model that interacts with socket I/O
- [Azure Services: Application Gateway](../reference-dictionary/azure-services.md#application-gateway) — L7 proxy that terminates TCP connections

---

## ETag

An opaque string token (entity tag) that the server attaches to a resource response to identify a specific version of that resource. Clients include the token in subsequent conditional requests to detect whether the resource has changed since it was last loaded.

### Key Characteristics
- Returned by the server as a response header: `ETag: "5"` (weak: `W/"5"`)
- Clients send `If-Match: "5"` on write requests; server rejects stale writes with **412 Precondition Failed**
- Clients send `If-None-Match: "5"` on read requests; server returns **304 Not Modified** (no body) if unchanged — saves bandwidth
- In JPA/Hibernate, the `@Version` field maps directly to the ETag value with zero extra infrastructure
- ETags are the standard HTTP mechanism for **optimistic concurrency control** at the API layer

### When to Use
- Any `PUT` or `PATCH` endpoint where concurrent updates from multiple clients must be detected
- `GET` endpoints on resources that change infrequently — `304 Not Modified` eliminates redundant payload delivery
- Collaborative editing workflows where the client must be informed that a conflict has occurred

### When NOT to Use
- High-frequency write paths where the mandatory GET → modify → PUT round-trip is prohibitively expensive (consider CRDTs or operational transforms instead)
- Internal service-to-service calls where the caller controls all write paths and concurrency is handled at the database layer

### Also see
- [Optimistic Locking](data-concurrency.md#optimistic-locking) — database-level equivalent
- [apipat-11: ETag-Based Optimistic Concurrency Control](../system-design-architecture/46-rest-api-senior-patterns-key-takeaways.md#apipat-11-etag-based-optimistic-concurrency-control)

---

## JSON Merge Patch

A partial-update format for HTTP APIs standardized in **RFC 7396**. A JSON Merge Patch document contains only the fields the client wants to change. Fields present in the patch body are updated; fields absent from the patch are left unchanged; fields set to `null` in the patch are removed.

```http
PATCH /users/42
Content-Type: application/merge-patch+json

{"email": "new@example.com"}
```

Only `email` is changed — all other fields remain exactly as they were.

### Key Characteristics
- Content type: `application/merge-patch+json` (IANA-registered)
- Simpler than JSON Patch (RFC 6902): no op codes, no arrays of operations — just a partial object
- Merge semantics: missing key = leave unchanged; explicit `null` = delete the key
- Correct alternative to `PUT` when only a subset of fields should be modified
- Supported natively by libraries such as Jackson (`JsonMergePatch`) and Jakarta JSON-P

### When to Use
- PATCH endpoints where clients update a subset of scalar fields on a resource
- Mobile or low-bandwidth clients that should send minimal payloads
- Any endpoint currently using PUT for partial updates — switch to PATCH + JSON Merge Patch

### When NOT to Use
- Resources with nullable fields that legitimately need to be set to `null` — use **JSON Patch** (RFC 6902) instead, as `null` in a merge patch means "remove the field"
- Arrays: merge patch replaces the entire array rather than merging elements

### Also see
- [Idempotency-Key](#idempotency-key)
- [apipat-10: PATCH vs PUT](../system-design-architecture/46-rest-api-senior-patterns-key-takeaways.md#apipat-10-patch-vs-put--partial-updates-with-json-merge-patch)

---

## Sparse Fieldsets

A pattern that lets clients declare exactly which fields they need in a response using a `?fields=` query parameter. The server filters the response to include only the requested fields, reducing payload size without requiring separate endpoints per consumer.

```http
GET /users?fields=id,name
→ [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
```

### Key Characteristics
- Implemented as an optional query parameter — existing clients that omit it receive the full response (backward-compatible)
- Reduces payload size by 80%+ on mobile paths where clients render only a few fields from a large resource
- A single endpoint serves multiple consumers with different field requirements, eliminating endpoint proliferation
- Conceptually equivalent to GraphQL field selection — REST can achieve the same result with one query parameter
- Server-side filtering in memory is simple; add database-level projection (`SELECT id, name FROM ...`) for high-traffic endpoints

### When to Use
- List endpoints (`GET /users`, `GET /products`) consumed by multiple clients with different field needs
- Mobile or low-bandwidth clients that render only a small subset of resource fields
- Public APIs where you want to minimize overfetching without adopting GraphQL

### When NOT to Use
- Resources with a small, fixed field set where the savings are negligible
- Security-sensitive fields that should never be returned — apply field-level authorization before filtering, not after

### Also see
- [Pagination (Cursor vs Offset)](#pagination-cursor-vs-offset)
- [apipat-12: Sparse Fieldsets](../system-design-architecture/46-rest-api-senior-patterns-key-takeaways.md#apipat-12-sparse-fieldsets--client-driven-field-selection)


---

## Migration-Driven Deprecation

The practice of treating API deprecation as an active migration management exercise rather than a passive communication exercise. A version is not truly "deprecated" until all consumers have migrated and the version is actually disabled — not merely when a notice is posted.

### Key Characteristics
- Deprecation is a project with an owner, a timeline, and success criteria — not a status label
- Requires per-client traffic tracking to identify unmigrated consumers
- Includes active outreach and migration support for high-volume consumers
- Enforced with a hard sunset date (not an indefinite "we'll remove it someday")
- The version is disabled on the sunset date regardless of remaining traffic percentage
- Security-critical versions use an accelerated timeline (≤ 30 days) regardless of migration completeness

### When to Use
- Any time a new API version is released and the old version needs to be retired
- Especially when the deprecated version has a known security vulnerability
- When previous "soft" deprecations have failed to drive adoption of the new version

### When NOT to Use
- Internal APIs with a single known consumer — coordinate directly instead of running the full process
- Prototype or sandbox APIs with no production consumers

### Also see
- [API Versioning](#api-versioning)
- [Deprecation Header](#deprecation-header)
- [Sunset Header](#sunset-header)
- [api-06: API Deprecation as Migration Strategy](../system-design-architecture/04-api-network-design.md#api-06-api-deprecation-as-migration-strategy)

---

## Hierarchical Rate Limiting

Applying rate limits at multiple layers of the request path — edge/gateway, service, and endpoint — so that abusive traffic is rejected as early as possible while still protecting individual backends.

### Key Characteristics
- **Defense in depth**: A single layer failing does not collapse the whole system
- **Progressive granularity**: Global → per-IP → per-API-key → per-user → per-endpoint → per-method+endpoint
- **Early rejection**: The edge/gateway tier blocks scrapers before they consume compute, DB connections, or bandwidth
- **Independent counters**: Each layer uses its own counter/key so a hot key in one layer does not starve another

### When to Use
- Public APIs with mixed client types and abuse patterns
- Microservices where the gateway alone cannot protect expensive downstream calls
- When different endpoints have very different costs (e.g., `/upload` vs `/health`)

### When NOT to Use
- Simple internal APIs where a single per-client limit is sufficient
- When operational complexity of multiple limit sets exceeds the risk of abuse

### Example Tiers
| Tier | Key | Limit example | Purpose |
|:---|:---|:---|:---|
| **Global** | — | 10,000 req/s | Protect infrastructure |
| **Per IP** | `rate:ip:{ip}` | 100 req/min | Block scrapers/single-source floods |
| **Per API Key** | `rate:key:{api_key}` | 1,000 req/min | Enforce customer plan |
| **Per User** | `rate:user:{user_id}` | 50 req/min | Fairness across users |
| **Per Endpoint** | `rate:key:{api_key}:{endpoint}` | 10 req/s | Protect expensive endpoints |
| **Per Method + Endpoint** | `rate:key:{api_key}:POST:/upload` | 5 req/min | Granular control |

**Also see**: [Rate Limiting](#rate-limiting) · [api-09: Hot Key Problem in Distributed Rate Limiters](../system-design-architecture/04-api-network-design.md#api-09-hot-key-problem-in-distributed-rate-limiters) · [gw-03: API Gateway](../system-design-architecture/16-reverse-proxy-lb-api-gateway.md#gw-03-api-gateway--when-api-lifecycle-management-is-the-priority)

---

## Deprecation Header

An HTTP response header defined in **RFC 8594** that signals to API clients that the endpoint they called is deprecated. The value is a date indicating when the deprecation was announced.

```http
Deprecation: Sat, 01 Jan 2026 00:00:00 GMT
Link: <https://api.example.com/v2/users>; rel="successor-version"
```

### Key Characteristics
- Defined in RFC 8594 alongside the `Sunset` header
- Machine-readable: API clients and gateway middleware can detect and log deprecated calls automatically without reading documentation
- The value is the deprecation *announcement* date — it does **not** indicate the removal date; use `Sunset` for that
- Conventionally paired with a `Link` header pointing to the successor resource or migration guide
- Should be added to every response from the deprecated version — not only error responses
- Can be injected centrally by an API gateway (e.g., Azure API Management policy) without modifying service code

### When to Use
- Every V1 response from the moment V2 is released and V1 is officially deprecated
- In API gateways to apply the header centrally without touching service code

### When NOT to Use
- Do not use as a substitute for a sunset date — `Deprecation` alone without `Sunset` sends no urgency signal

### Also see
- [Sunset Header](#sunset-header)
- [API Versioning](#api-versioning)
- [Migration-Driven Deprecation](#migration-driven-deprecation)

---

## Sunset Header

An HTTP response header defined in **RFC 8594** that communicates the date and time at which an API endpoint will be permanently removed. Unlike `Deprecation`, `Sunset` creates urgency by specifying a hard deadline.

```http
Sunset: Fri, 01 Jan 2027 00:00:00 GMT
Deprecation: Sat, 01 Jan 2026 00:00:00 GMT
```

### Key Characteristics
- Defined in RFC 8594 alongside the `Deprecation` header
- Machine-readable: clients and monitoring tools can alert when the sunset date is approaching
- Should be returned on every deprecated endpoint's response alongside `Deprecation`
- After the sunset date, the server should return **410 Gone** (not 404) to distinguish intentional removal from resource not found
- Some API gateway products (e.g., Azure API Management) support automatic Sunset header injection and traffic reporting per deprecated operation

### When to Use
- All deprecated API versions where a hard retirement date has been set
- Security-critical deprecations where a short sunset window (≤ 30 days) needs to be communicated urgently

### When NOT to Use
- Do not set a `Sunset` date before the migration path is ready — clients have nowhere to go and will be broken on a date they cannot avoid

### Also see
- [Deprecation Header](#deprecation-header)
- [API Versioning](#api-versioning)
- [Migration-Driven Deprecation](#migration-driven-deprecation)
- [api-08: Security-Triggered Forced Sunset](../system-design-architecture/04-api-network-design.md#api-08-security-triggered-forced-sunset)

---

## API Gateway

An infrastructure component that sits between clients and backend services, providing cross-cutting concerns such as **authentication, rate limiting, request routing, SSL termination, and protocol translation**.

### Key Characteristics

- Single entry point for external clients
- Centralizes auth validation, logging, and monitoring
- Hides internal service topology
- Often paired with load balancers and WAFs

### When to Use

- Multiple client types (mobile, web, third-party) access the same backend
- Need centralized authentication, rate limiting, or routing

### When NOT to Use

- As a single point of failure without redundancy
- For internal service-to-service communication (prefer service mesh or direct mTLS)

### Also see

- [Rate Limiting](api-design.md#rate-limiting)
- [Reverse Proxy, LB & API Gateway](../system-design-architecture/16-reverse-proxy-lb-api-gateway.md)

---

## Hotlinking

Directly embedding or linking to a resource hosted on another server without re-hosting it. The consuming site gets the benefit (image, video, file) while the hosting site pays the bandwidth and infrastructure costs.

### Key Characteristics
- **Bandwidth theft**: Origin server serves traffic for external sites
- **Common targets**: Images, videos, downloadable files
- **Prevention**: Signed URLs, referrer checks, watermarking, CDN rules

### When to Use
- Intentional sharing with explicit permission (e.g., CDN-hosted assets with hotlink protection)

### When NOT to Use
- Without permission, as it consumes the origin's resources
- For resources whose origin must remain hidden or whose URLs should not be guessable

**Also see**: [API Gateway](#api-gateway) · [CDN](../reference-dictionary/caching.md#cache-aside-pattern)

---

## Faceted Search

A search interface that lets users refine results by applying multiple filters (facets) such as category, brand, price range, and rating.

### Key Characteristics
- Facets are derived from the current result set and update as filters are applied
- Requires a search index that supports aggregations (e.g., Elasticsearch, Azure Cognitive Search)
- Combines full-text relevance with structured, multi-dimensional filtering

### When to Use
- E-commerce catalogs, document repositories, and media libraries
- Any large collection where users browse by multiple dimensions

### When NOT to Use
- Small datasets where simple keyword search is sufficient
- When facet-computation latency exceeds user expectations

### Also see
- [API Gateway](#api-gateway)

