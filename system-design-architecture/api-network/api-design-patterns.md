---
type: System Design
title: "API Design Patterns — Key Takeaways"
description: "/v1/charges          ← Major version in URL (rarely changes)"
timestamp: 2026-06-14T00:00:00Z
---

# 20. API Design Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)  
> **Source**: [The API Design Patterns Nobody Teaches You](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)  
> **Also see**: [APIs & Network Design](api-network/api-network-design.md), [Reverse Proxy, LB & API Gateway](api-network/reverse-proxy-lb-gateway.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md)

---

## apipat-01: The Four Pillars of a Well-Designed API

> **Source**: [Article §"What Makes an API Well-Designed"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| Pillar | Meaning | Violation Example |
|:---|:---|:---|
| **Predictable** | Consistent naming and behavior across endpoints | `GET /getUser` vs `POST /fetch_orders` |
| **Backward-Compatible** | Old clients never break after changes | Renaming a field without deprecation period |
| **Resilient** | Graceful partial failure handling | Returning 500 with no retry guidance |
| **Self-Documenting** | Obvious behavior without external docs | `POST /process` — process what? |

> **Azure**: Azure API Management enforces consistent naming conventions via policies and OpenAPI validation.

---

## apipat-02: API Versioning Strategies

> **Source**: [Article §"Pattern 1 — API Versioning"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

### Strategy Comparison

| Strategy | Mechanism | Pros | Cons |
|:---|:---|:---|:---|
| **URL path** | `/v1/users`, `/v2/users` | Explicit, easy to route, CDN-friendly | URL pollution |
| **Accept header** | `Accept: application/vnd.api+json;version=2` | Clean URLs, REST-purist | Hard to test in browser |
| **Query param** | `/users?version=2` | Simple | Not RESTful; not recommended |
| **Stripe two-tiered** | URL path + per-API-key date pin (`2023-10-16`) | Zero breaking changes ever | Complex key management |

### Stripe's Two-Tiered Versioning

```
/v1/charges          ← Major version in URL (rarely changes)
API-Key: sk_xxx      ← Pinned to a date-based version (2023-10-16)

When Stripe makes a change:
  → Date ticks forward
  → Your existing key stays on old version FOREVER
  → Code from 3 years ago still works
  → You explicitly upgrade the key when ready
```

### Deprecation Lifecycle

| Phase | Action | Timeline |
|:---|:---|:---|
| **Announce** | Public deprecation notice | Min 6 months for public APIs |
| **Signal** | Add `Sunset` + `Deprecation` headers to old version responses | Throughout deprecation window |
| **Notify** | Email developers still using old version | Before shutdown |
| **Retire** | Turn off old version | After sunset date |

### Gateway Adapter Pattern

```
/v1/*  ──▶ v1 adapter ──▶ core logic
/v2/*  ──▶ v2 adapter ──▶ core logic
                             ↑
                    Single business logic,
                    adapters transform I/O
```

> **Azure**: Azure API Management supports version sets, revisioning, and header-based routing. | **Taxonomy**: §8.3 API Design

---

## apipat-03: Idempotency — Preventing Double Charges

> **Source**: [Article §"Pattern 2 — Idempotency"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| | |
|:---|:---|
| **Problem** | Network timeout on `POST /payments` → client retries → double charge |
| **Root cause** | `POST` is not idempotent; no server-side deduplication |
| **Scale impact** | 0.1% failure rate × 100K daily payments = 100 double-charges/day |

### HTTP Method Idempotency

| Method | Idempotent? | Safe to Retry? |
|:---|:---:|:---:|
| `GET` | ✅ | ✅ Always |
| `PUT` (full body) | ✅ | ✅ Same result every time |
| `DELETE` | ✅ | ✅ Resource gone, doesn't matter how often |
| `POST` | ❌ | ❌ Creates a new resource each call |
| `PATCH` | ❌ | ❌ Depends on patch semantics |

### Idempotency-Key Pattern (Stripe Gold Standard)

```python
import hashlib, json
import redis

r = redis.Redis()


def handle_payment(request_body: dict, idempotency_key: str):
    cache_key = f"idempotency:{idempotency_key}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)  # Return same response, no double charge

    result = process_payment(request_body)  # actual payment logic
    r.setex(cache_key, 86400, json.dumps(result))  # store for 24h
    return result
```

### Key Design Decisions

| Decision | Recommendation | Rationale |
|:---|:---|:---|
| **Key generation** | Client generates UUID | Decentralized, no coordination |
| **Storage** | Redis / distributed cache | Fast lookups, TTL support |
| **TTL** | 24 hours | Covers retry window; prevents unbounded storage |
| **Collision handling** | Return stored response | Safe — same logical action |
| **Scope** | Per-endpoint or global | Define in API contract |

> **Azure**: Azure Cache for Redis for idempotency key storage; Service Bus duplicate detection (configurable window). | **Also see**: [tx-03: Distributed Locks](concurrency-transactions/concurrency-transactions.md#tx-03-distributed-locks)

---

## apipat-04: Pagination — Cursor vs Offset

> **Source**: [Article §"Pattern 3 — Pagination"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| | |
|:---|:---|
| **Problem** | `LIMIT 20 OFFSET 10000` scans 10,020 rows, discards 10,000; data shift causes duplicates |
| **Root cause** | Offset is a row position, not a data anchor — insertions/deletions shift everything |

### Offset vs Cursor

| Aspect | Offset (`LIMIT/OFFSET`) | Cursor (keyset) |
|:---|:---|:---|
| **Query** | `SELECT * FROM t LIMIT 20 OFFSET 10000` | `SELECT * FROM t WHERE id > :cursor LIMIT 21` |
| **Index usage** | Full scan of skipped rows | Seeks directly via PK index |
| **Data shift** | ❌ Duplicates & gaps | ✅ Stable bookmark |
| **Deep pages** | ❌ Degrades linearly | ✅ Constant time |
| **Stateless** | ✅ | ❌ Needs cursor from previous page |

### Cursor Implementation

```python
def get_users(cursor: str = None, limit: int = 20):
    query = db.query(User).order_by(User.id)
    if cursor:
        decoded_id = decode_cursor(cursor)  # base64 decode
        query = query.filter(User.id > decoded_id)
    users = query.limit(limit + 1).all()       # Fetch N+1
    has_more = len(users) > limit
    users = users[:limit]                       # Trim to limit
    return {
        "data": [u.to_dict() for u in users],
        "next_cursor": encode_cursor(users[-1].id) if has_more else None,
        "has_more": has_more,
    }
```

### The +1 Fetch Trick

```
Request:  limit=20
Query:    LIMIT 21          ← fetch one extra
Result:   21 rows → has_more=true, return first 20
          20 rows → has_more=false, return all 20

Avoids an expensive COUNT(*) query.
```

> **Azure**: Cosmos DB continuation tokens are a built-in cursor mechanism. | **Also see**: [db-02: Paginating Through Large Datasets](databases/query-performance.md#db-02-paginating-through-large-datasets)

---

## apipat-05: Error Design — RFC 7807

> **Source**: [Article §"Pattern 4 — Error Design"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| | |
|:---|:---|
| **Problem** | `{"error": "bad request"}` leaves clients guessing — which field? retryable? |
| **Root cause** | Errors treated as afterthoughts, not as part of the API contract |

### HTTP Status Code Decision Tree

```
Input invalid syntax?     ──▶ 400 Bad Request
Validation rule failed?   ──▶ 422 Unprocessable Entity
No auth token?            ──▶ 401 Unauthorized
Token valid, no access?   ──▶ 403 Forbidden
Resource missing?         ──▶ 404 Not Found
Conflict with state?      ──▶ 409 Conflict
Rate limited?             ──▶ 429 Too Many Requests
Code crashed?             ──▶ 500 Internal Server Error
Downstream service down?  ──▶ 503 Service Unavailable
```

### 401 vs 403 — The Security Split

| Code | Meaning | When |
|:---|:---|:---|
| **401** | "I don't know you" | Missing/invalid token |
| **403** | "I know you, but no" | Authenticated but unauthorized |

> ⚠️ Don't leak user existence info by returning 403 when it should be 401.

### RFC 7807 Response Structure

```json
{
  "type":       "https://api.example.com/errors/insufficient-funds",
  "title":      "Insufficient Funds",
  "status":     422,
  "detail":     "Account acc_123 has insufficient balance.",
  "instance":   "/payments/pmt_456",
  "request_id": "req_abc789",
  "error_code": "INSUFFICIENT_FUNDS"
}
```

| Field | Purpose |
|:---|:---|
| `type` | URL to documentation for this error type |
| `title` | Human-readable, same for all instances of this error |
| `status` | HTTP status code (redundant but useful in logs) |
| `detail` | Instance-specific explanation |
| `instance` | The exact URL that triggered the error |
| `request_id` | **Critical** — log correlation ID for 2am incidents |
| `error_code` | Machine-readable code for client `switch` logic |

> **Never expose stack traces in production.**  
> **Azure**: Azure API Management can transform error responses to RFC 7807 format via policies.

---

## apipat-06: Rate Limiting — Communication Is Key

> **Source**: [Article §"Pattern 5 — Rate Limiting & Throttling"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| | |
|:---|:---|
| **Problem** | Client hits limit, gets bare 429 with no info → hammers harder or opens ticket |
| **Solution** | Communicate limits clearly on EVERY response, not just on 429s |

### Mandatory Rate Limit Headers

| Header | Purpose | Required On |
|:---|:---|:---|
| `X-RateLimit-Limit` | Total requests per window | Every response |
| `X-RateLimit-Remaining` | How many left | Every response |
| `X-RateLimit-Reset` | Unix timestamp for window reset | Every response |
| `Retry-After` | Seconds until next allowed request | 429 responses only |

### Algorithm Comparison

| Algorithm | Burst Handling | Memory | Best For |
|:---|:---|:---|:---|
| **Token bucket** | Allows bursts, enforces average | $O(1)$ | Most APIs (default choice) |
| **Leaky bucket** | No bursts, fixed output rate | $O(1)$ | Expensive/CPU-bound services |
| **Sliding window** | Smooth, no boundary exploit | $O(1)$ with counters | Strict enforcement |

### Tiered Limits by Key & Endpoint

```
Free tier key:    100 req/min  for /users/{id}
                  10 req/min   for /search          ← expensive endpoint
Paid tier key:    10,000 req/min for /users/{id}
                  1,000 req/min for /search
```

### Graceful Degradation (Don't Always 429)

For non-critical endpoints, serve **stale/cached data** with a `Warning` header instead of rejecting outright.

> **Azure**: API Management rate-limit / quota policies, partitionable by key. | **Also see**: [api-02: Rate Limiting](api-network/api-network-design.md#api-02-rate-limiting)

---

## apipat-07: Backward Compatibility & Expand-Contract

> **Source**: [Article §"Pattern 6 — Backward Compatibility & Breaking Changes"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

### Breaking vs Non-Breaking Changes

| Breaking ❌ | Non-Breaking ✅ |
|:---|:---|
| Removing a response field | Adding optional response field |
| Renaming a field | Creating a new endpoint |
| Changing field type (`int` → `string`) | Adding optional query parameters |
| Changing HTTP method | Adding optional request fields |
| Adding a required request field | |
| Changing status codes clients depend on | |
| Changing error code strings | |

> ⚠️ **Adding enum values** can break strict clients that exhaustively `switch` on enum values. Stripe documents this as a breaking change.

### Expand-Contract Pattern

| Phase | Action | Response |
|:---|:---|:---|
| **1. Expand** | Add new field, keep old one; mark old `@Deprecated` | `{"user_name": "alice", "username": "alice"}` |
| **2. Migrate** | Give consumers time to update (weeks internal, months public); monitor old field usage | Same response; both fields present |
| **3. Contract** | Remove old field only after all consumers migrated | `{"username": "alice"}` |

```
Phase 1 (EXPAND):  Both fields present, old deprecated
Phase 2 (MIGRATE): Clients update to new field
Phase 3 (CONTRACT): Old field removed
                    ↑
         Never skip Phase 2 — it's the safety net.
```

> **Azure**: API Management schema validation policies catch breaking changes in API revisions.

---

## apipat-08: Contract-First Design (OpenAPI)

> **Source**: [Article §"Pattern 7 — API Contract-First Design"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

| | |
|:---|:---|
| **Problem** | Code-first → teams guess requirements, APIs drift, frontend blocks on backend |
| **Solution** | Write OpenAPI spec first; both sides work in parallel against the contract |

### Contract-First vs Code-First

```
CONTRACT-FIRST (parallel):
  OpenAPI Spec ──┬── Frontend: mock server, build UI
                 └── Backend: implement to spec, unit tests
                 └── Merge → Contract Tests → Deploy

CODE-FIRST (sequential, blocking):
  Backend builds → Backend writes docs → Frontend starts → Integration hell
```

### OpenAPI $ref — Define Once, Reuse Everywhere

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        created_at:
          type: string
          format: date-time

paths:
  /users/{id}:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'  # Reuse
```

### Contract-First Workflow

| Step | Action | Tool |
|:---|:---|:---|
| 1. Write spec | Define endpoints, schemas, errors, auth | Stoplight, Swagger Editor |
| 2. Review | Team agrees on contract | PR review |
| 3. Generate mocks | Frontend works against realistic data | Prism, OpenAPI Mock |
| 4. Generate SDKs | Auto-generate client libraries | openapi-generator |
| 5. Contract tests | Verify implementation matches spec | Dredd, Pact |
| 6. Deploy | Both sides integrated | — |

> **Azure**: API Management imports OpenAPI specs directly; Azure API Center catalogs all organization specs.

---

## apipat-09: Bonus Patterns

> **Source**: [Article §"Bonus: Six More API Patterns"](../../../articles/medium/api-design-patterns-nobody-teaches-you.md)

### Pattern Summary

| Pattern | What It Is | Example |
|:---|:---|:---|
| **HATEOAS** | Responses include links to next actions | GitHub API: `_links: { "next": "/users?page=2" }` |
| **Partial Responses** | Clients request only needed fields | `GET /users/123?fields=id,name,email` |
| **Bulk Operations** | Accept batches instead of N calls | `POST /users/batch` with per-item success/failure |
| **Long-Running Operations** | Return `202 Accepted` + job ID; client polls | Async export, report generation |
| **Health Check Endpoints** | `/health` (liveness) + `/ready` (readiness) + `/metrics` (Prometheus) | K8s probes, on-call sanity |
| **Date-Based Versioning** | `2023-10-16` instead of `v2.1.3` | Stripe API keys; honest about when the contract changed |

### Health Check Endpoint Design

| Endpoint | Purpose | Must Be | Used By |
|:---|:---|:---|:---|
| `/health` | Is the process alive? | Fast, public, no deps | Load balancer, K8s liveness probe |
| `/ready` | Can it serve traffic? | Checks DB/Redis/upstream deps | K8s readiness probe, traffic routing |
| `/metrics` | Prometheus scrape endpoint | Counters, histograms, gauges | Monitoring, alerting, autoscaling |

> **Azure**: Application Insights live metrics, App Service Health Check, AKS liveness/readiness probes.

---

## Quick Reference Matrix

| Concern | Pattern | Key Mechanism | Azure Implementation |
|:---|:---|:---|:---|
| Versioning | URL path + date-pinned keys | API Gateway adapters | API Management version sets |
| Double charges | Idempotency-Key | Redis dedup, 24h TTL | Cache for Redis, Service Bus duplicate detection |
| Large datasets | Cursor pagination | `WHERE id > :cursor LIMIT N+1` | Cosmos DB continuation tokens |
| Error clarity | RFC 7807 | `type`, `detail`, `request_id`, `error_code` | API Management policy transforms |
| Rate limiting | Token bucket + headers | `X-RateLimit-*` on every response | API Management rate-limit policies |
| Field evolution | Expand-Contract | Deprecate → Migrate → Remove | API Management schema validation |
| API lifecycle | Contract-first | OpenAPI spec → mock → test → deploy | API Center, API Management import |
| Retry safety | Idempotency-Key | Client-generated UUID, server dedup | — |
| Deep pagination | Keyset pagination | Primary key index seek | — |
| Client discovery | HATEOAS | Response-embedded links | — |
