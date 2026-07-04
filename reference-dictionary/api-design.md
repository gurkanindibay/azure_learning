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
| ETag | [`#etag`](#etag) |
| JSON Merge Patch | [`#json-merge-patch`](#json-merge-patch) |
| Sparse Fieldsets | [`#sparse-fieldsets`](#sparse-fieldsets) |
| Migration-Driven Deprecation | [`#migration-driven-deprecation`](#migration-driven-deprecation) |
| Hierarchical Rate Limiting | [`#hierarchical-rate-limiting`](#hierarchical-rate-limiting) |
| Deprecation Header | [`#deprecation-header`](#deprecation-header) |
| Sunset Header | [`#sunset-header`](#sunset-header) |
| Hotlinking | [`#hotlinking`](#hotlinking) |
| Faceted Search | [`#faceted-search`](#faceted-search) |
| Chunked Upload | [`#chunked-upload`](#chunked-upload) |
| Backward Compatibility | [`#backward-compatibility`](#backward-compatibility) |
| Resumable Upload | [`#resumable-upload`](#resumable-upload) |
| Upload Session | [`#upload-session`](#upload-session) |
| Direct Upload | [`#direct-upload`](#direct-upload) |
| Pre-signed URL | [`#pre-signed-url`](#pre-signed-url) |
| Checksum | [`#checksum`](#checksum) |
| WebSocket | [`#websocket`](#websocket) |
| PRG Pattern | [`#prg-pattern`](#prg-pattern) |
| Lazy Subscription | [`#lazy-subscription`](#lazy-subscription) |
| Stateful Gateway | [`#stateful-gateway`](#stateful-gateway) |
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

---

## Chunked Upload

A technique for uploading large files by splitting them into smaller, independently uploaded pieces (chunks). Each chunk is a separate HTTP request, so failure of one chunk does not require restarting the entire file.

### Key Characteristics
- **Failure isolation**: Only the failed chunk is retried, not the entire file
- **Resume capability**: Combined with an Upload Session, enables resumable uploads
- **Parallel uploads**: Multiple chunks can be uploaded concurrently for faster throughput
- **Common sizes**: 5–64 MB per chunk, depending on network conditions

### When to Use
- Files larger than 100 MB
- Uploads over unreliable or mobile networks
- Any scenario where upload progress must survive network interruptions

### When NOT to Use
- Small files (<1 MB) where chunking overhead exceeds the benefit
- Single-shot uploads where the connection is guaranteed reliable

### Also see
- [Resumable Upload](#resumable-upload) · [Upload Session](#upload-session)

---

## Backward Compatibility

The discipline of ensuring that **a new version of an API, schema, or contract does not break existing consumers**. In API design, backward compatibility means existing clients continue to function without modification. In event-driven systems (Kafka), it means existing consumers can still deserialize and process events produced with a new schema version.

Backward compatibility is not optional for shared contracts — it is a **hard requirement** when multiple independent teams depend on the same interface. Breaking backward compatibility silently is the fastest way to cause cascading production incidents across teams.

### Key Characteristics
- **Additive changes are safe**: Adding optional fields, new endpoints, or new event types does not break existing consumers
- **Removal or redefinition is breaking**: Removing a field, changing its type, or redefining its semantics breaks consumers
- **Enforced at registration time**: Schema registries reject incompatible schema changes before data is published
- **Deprecation, not deletion**: Breaking changes follow a deprecate→migrate→remove lifecycle with a published window

### When to Use
- Any public API, shared event stream, or library interface with consumers outside your team
- Kafka topics consumed by multiple independent teams — schema changes must be backward-compatible
- REST/gRPC APIs where clients cannot be forced to upgrade simultaneously

### When NOT to Use
- Internal code with a single consumer owned by the same team
- Prototypes where the interface is still evolving rapidly
- When you control both producer and consumer and can deploy atomically

### Also see
- [Contract-First Design](#contract-first-design) · [API Versioning](#api-versioning) · [Expand-Contract Pattern](#expand-contract-pattern) · [Migration-Driven Deprecation](#migration-driven-deprecation) · [Schema Contract](../messaging.md#schema-contract-event-as-public-api) · [Direct Upload](#direct-upload)

---

## Resumable Upload

The ability to continue an upload from the point of interruption rather than restarting from the beginning. Built on chunked uploads and upload sessions, it ensures users never lose progress when networks fail.

### Key Characteristics
- **Requires chunking**: The file must be split into independent chunks
- **Requires session tracking**: Server must persist which chunks have been received
- **Resume query**: After reconnect, client queries `GET /upload/session/{id}` to discover missing chunks
- **User-facing**: The primary UX benefit is that users never see "start over" after a network drop

### When to Use
- User-facing upload features (Google Drive, YouTube, Dropbox)
- Mobile apps where connectivity is intermittent
- Large file transfers (>100 MB) over the public internet

### When NOT to Use
- Server-to-server transfers over private, reliable networks
- Tiny files where restart cost is negligible

### Also see
- [Chunked Upload](#chunked-upload) · [Upload Session](#upload-session) · [Direct Upload](#direct-upload)

---

## Upload Session

A server-side state object that tracks the progress of a chunked upload. Identified by a unique session ID, it records which chunks have been received and which are still missing, enabling resume after interruption.

### Key Characteristics
- **Session ID**: A unique identifier (e.g., `UPLOAD-12345`) created at upload initiation
- **Chunk tracking**: Maintains a list of uploaded chunk numbers and total expected chunks
- **Persistent**: Survives browser refresh, app restart, and device reboot (stored in DB or Redis)
- **Metadata**: Stores fileName, totalSize, totalChunks, uploadedChunks, and checksums

### When to Use
- Any chunked upload that must survive network interruption
- Multi-session uploads where the same file is uploaded across multiple user sessions

### When NOT to Use
- Single-request uploads where the entire file fits in one HTTP request
- Ephemeral uploads where restart-from-scratch is acceptable

### Also see
- [Chunked Upload](#chunked-upload) · [Resumable Upload](#resumable-upload) · [Idempotency-Key](#idempotency-key)

---

## Direct Upload

A pattern where the client uploads file bytes directly to object storage (S3, Azure Blob, GCS) using a pre-signed URL, bypassing the application server entirely for the data transfer phase.

### Key Characteristics
- **Bypasses app servers**: Application servers never see file bytes — only metadata flows through them
- **Scales independently**: Object storage handles bandwidth; app servers handle business logic
- **Requires pre-signed URL**: A time-limited, cryptographically signed URL granting temporary write access
- **Post-upload hook**: Client notifies the app server after upload completes for validation and processing

### When to Use
- High-throughput upload scenarios (100K+ concurrent users)
- Files >100 MB where proxying through app servers would saturate bandwidth
- Multi-region uploads where upload should terminate close to the user

### When NOT to Use
- Uploads requiring real-time server-side transformation during transfer
- Scenarios where the storage layer cannot be exposed to clients (air-gapped environments)

### Also see
- [Pre-signed URL](#pre-signed-url) · [Chunked Upload](#chunked-upload) · [Resumable Upload](#resumable-upload)

---

## Pre-signed URL

A time-limited, cryptographically signed URL that grants temporary access to a specific object storage operation (upload or download) without requiring the caller to have permanent credentials.

### Key Characteristics
- **Time-bound**: Expires after a configurable duration (typically minutes to hours)
- **Scoped**: Limited to a single object and operation (GET, PUT)
- **Signature-based**: Signed with the storage account's secret key; tampering invalidates the URL
- **Azure equivalent**: Shared Access Signature (SAS) tokens
- **AWS equivalent**: S3 Pre-signed URLs

### When to Use
- Direct upload from browser/mobile to object storage
- Temporary read access to private objects (e.g., "Download report" links)
- Avoiding credential distribution to client devices

### When NOT to Use
- Long-lived access (use IAM/managed identities instead)
- Operations requiring audit of every access (pre-signed URLs are self-contained credentials)

### Also see
- [Direct Upload](#direct-upload) · [Chunked Upload](#chunked-upload)

---

## Checksum

A fixed-size hash (e.g., SHA-256, MD5) computed from data to verify its integrity after transmission or storage. Used in upload systems to detect corruption before accepting a chunk.

### Key Characteristics
- **Deterministic**: Same input always produces the same checksum
- **Tamper-evident**: Any change to the data produces a different checksum
- **Per-chunk validation**: Each chunk carries its own checksum for independent verification
- **Common algorithms**: SHA-256, MD5 (legacy), CRC32 (fast but weak)

### When to Use
- Verifying chunk integrity before assembly
- Detecting transmission errors over unreliable networks
- End-to-end data integrity from client to storage

### When NOT to Use
- As a security mechanism (checksums detect errors, not malicious tampering — use HMAC or digital signatures for security)
- When the transport layer already provides integrity (TLS) and corruption risk is negligible

### Also see
- [Chunked Upload](#chunked-upload) · [ETag](#etag)

---

## WebSocket

A full-duplex communication protocol over a single TCP connection, initiated by an HTTP upgrade handshake. Unlike HTTP's request-response model, WebSocket maintains a persistent connection where either the client or server can push data at any time — eliminating polling overhead for real-time applications.

### Key Characteristics
- **Full-duplex**: Both client and server can send messages independently after the handshake
- **Persistent connection**: One TCP connection stays open, avoiding repeated TLS handshakes and HTTP headers
- **Low latency**: Sub-millisecond message delivery after the initial connection — ideal for real-time updates
- **Event-driven**: Server pushes updates to clients when state changes, rather than clients polling for changes

### When to Use
- Real-time leaderboards, live scores, and dashboards where polling would waste bandwidth
- Chat applications, collaborative editing, and multi-player game state sync
- Server-to-client push notifications (as an alternative to Server-Sent Events when bidirectional communication is needed)
- Financial tickers and trading platforms requiring sub-second price updates

### When NOT to Use
- Infrequent updates (polling every 30s is simpler and more robust)
- One-way server-to-client only (Server-Sent Events are simpler and auto-reconnect)
- When the client or network doesn't support WebSocket (use long-polling or SSE as fallback)
- When connection count scales to millions — connection management (heartbeats, reconnection, load balancer timeout tuning) becomes a significant operational burden

### Also see
- [Rate Limiting](#rate-limiting) · [Long-Running Operations](#long-running-operations) · [Leaderboard Pattern](../architecture-patterns.md#leaderboard-pattern)

## PRG Pattern

The **POST-Redirect-GET** pattern — a web application design pattern that prevents duplicate form submissions caused by page refreshes. After processing a POST request, the server responds with a 302 redirect to a GET endpoint, so that subsequent page refreshes only repeat the safe GET request.

### Key Characteristics
- **Prevents double-submission on refresh**: The browser's address bar points to the GET URL after redirect, not the POST endpoint
- **Two HTTP round-trips**: POST → 302 Redirect → GET (adds latency compared to a direct POST response)
- **Server-side state needed**: The GET endpoint must have access to the result of the POST operation (via session, query params, or path params)
- **UX improvement, not security**: PRG prevents accidental resubmissions from the same user on the same browser; it does NOT prevent duplicate requests from other clients, network retries, or API consumers

### When to Use
- Traditional server-rendered web applications with HTML form submissions
- Any flow where the user might refresh the page after submitting (order confirmation, payment, registration)
- Combined with token-based idempotency as a defense-in-depth strategy

### When NOT to Use
- SPAs and mobile apps — these use client-side routing and API calls, not browser form submissions; token-based idempotency is the primary mechanism
- As the sole idempotency mechanism — it only protects against browser refresh, not against network retries, message queue redelivery, or concurrent API requests

### Also see
- [Idempotency-Key](../api-design.md#idempotency-key) · [API Idempotency](../cqrs-event-driven.md#api-idempotency) · [Token-Based Idempotency](../cqrs-event-driven.md#token-based-idempotency)

---

## Lazy Subscription

A **presence and real-time subscription strategy** where clients subscribe only to the entities currently rendered on screen (visible friends, visible chunk of member list, active DMs) rather than subscribing to the entire social graph. When the user scrolls or opens a new DM, the subscription set updates dynamically.

### Key Characteristics
- **Viewport-bounded**: Subscriptions cover ~50–200 entities, not the full social graph (which may contain 100K+ entities per user)
- **Dynamic**: Subscribe/unsubscribe as the UI changes (scroll, tab switch, DM open/close)
- **Decouples fanout from graph size**: System load scales with concurrent user count, not with total social connections
- **Client-driven**: The client tracks what's visible and issues subscribe/unsubscribe calls

### When to Use
- Presence systems where fanout would otherwise multiply by thousands of watchers per status change
- Real-time indicators (typing, read receipts, live cursors, viewer counts) at scale
- Any system where the set of "things I care about right now" is much smaller than "things I could theoretically care about"

### When NOT to Use
- Small social graphs where full subscription is simpler and the fanout is manageable
- Systems where the full set of subscriptions must always be known (e.g., notification delivery to all followers)
- When the subscription churn (rapid scroll, rapid tab switching) overwhelms the subscription management system

### Also see
- [Presence Service](#presence-service) · [Fanout on Write](messaging.md#fanout-on-write) · [Fanout on Read](messaging.md#fanout-on-read) · [WebSocket](api-design.md#websocket)

---

## Stateful Gateway

A **connection-termination pattern** where each gateway server holds live session state in memory — which users are connected, their current status, and what subscriptions they hold. This is the opposite of a stateless gateway that must query a database or cache for every event.

### Key Characteristics
- **In-memory session state**: Connection, status, subscriptions held in process memory; no external lookup per event
- **Connection affinity**: A user's WebSocket is pinned to one gateway for the session duration
- **Pub/sub for cross-gateway communication**: Events are published to an internal message bus; other gateways subscribe to topics relevant to their connected clients
- **No cross-gateway discovery needed**: Gateways only need to know what topics to subscribe to, not which other gateways exist

### When to Use
- Real-time systems with persistent connections (chat, presence, collaborative editing, gaming)
- When per-event database lookups would bottleneck at scale
- Platforms where connection count dominates event count (games, chat apps)

### When NOT to Use
- Request/response APIs where connections are ephemeral (stateless gateways are simpler)
- When gateway failure would cause unacceptable data loss (stateful gateways risk losing session state on crash)
- Small systems where the operational complexity of pub/sub coordination exceeds the benefit

### Also see
- [Presence Service](#presence-service) · [WebSocket](api-design.md#websocket) · [API Gateway](networking.md#api-gateway) · [Load Balancer](#load-balancer) · [Exponential Backoff](resilience.md#exponential-backoff)

