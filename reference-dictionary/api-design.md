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
- [Virtual Threads](../reference-dictionary/architecture-patterns.md#virtual-threads) — concurrency model that interacts with socket I/O
- [Azure Services: Application Gateway](../reference-dictionary/azure-services.md#application-gateway) — L7 proxy that terminates TCP connections
