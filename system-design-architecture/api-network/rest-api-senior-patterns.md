---
type: System Design
title: "REST API Senior Patterns — Key Takeaways"
description: "Production-grade patterns for partial updates (JSON Merge Patch), ETag-based concurrency control, and sparse fieldsets — the patterns that make a REST API contract-grade."
timestamp: 2026-06-23T00:00:00Z
---

# 46. REST API Senior Patterns — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Stop Designing REST APIs Like a Mid-Level Dev](../../../articles/medium/stop-designing-rest-apis-advanced-patterns-senior-engineers.md)
> **Also see**: [API Design Patterns](api-network/api-design-patterns.md), [APIs & Network Design](api-network/api-network-design.md), [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md)
> **Taxonomy**: §8.3 API Design

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [apipat-10](#apipat-10-patch-vs-put--partial-updates-with-json-merge-patch) | PUT silently wipes fields the client did not include | PATCH + RFC 7396 JSON Merge Patch |
| [apipat-11](#apipat-11-etag-based-optimistic-concurrency-control) | Concurrent updates silently overwrite each other | ETag + `If-Match` + 412 Precondition Failed |
| [apipat-12](#apipat-12-sparse-fieldsets--client-driven-field-selection) | Mobile clients receive 15 fields when they need 2 | `?fields=` query parameter (sparse fieldsets) |

---

## apipat-10: PATCH vs PUT — Partial Updates with JSON Merge Patch

> **Source**: [Article §"Mistake 2 — Using PUT When You Mean PATCH"](../../../articles/medium/stop-designing-rest-apis-advanced-patterns-senior-engineers.md)

| | |
|:---|:---|
| **Problem** | `PUT /users/{id}` with a partial body silently sets every missing field to `null` — a client updating only `email` inadvertently wipes `username`, `phone`, and `address` |
| **Root cause** | PUT replaces the **entire** resource; it is semantically incorrect for partial updates |
| **Scale impact** | Any client that sends an incomplete body causes silent data loss with no error, no warning, and no way to detect the corruption without a diff |

**Strategy**: Accept `PATCH` requests with `Content-Type: application/merge-patch+json` (RFC 7396). Load the current resource from the database, apply only the fields present in the patch body, and persist the result.

```java
@PatchMapping(value = "/users/{id}", consumes = "application/merge-patch+json")
public ResponseEntity<UserResponse> patchUser(
        @PathVariable Long id,
        @RequestBody JsonMergePatch patch) {
    User existing = userService.findById(id);
    UserRequest current = UserRequest.from(existing);
    JsonNode targetNode = objectMapper.valueToTree(current);
    JsonNode patchedNode = patch.apply(targetNode);
    UserRequest patched = objectMapper.treeToValue(patchedNode, UserRequest.class);
    return ResponseEntity.ok(UserResponse.from(userService.update(id, patched)));
}
```

Client sends only the changed field:

```http
PATCH /users/42
Content-Type: application/merge-patch+json

{"email": "new@example.com"}
```

**Tradeoff**: JSON Merge Patch cannot express "set a field to `null`" — a `null` value in the patch means *remove this field*, not *set it to null*. Use **JSON Patch** (RFC 6902, `Content-Type: application/json-patch+json`) for resources that have nullable fields requiring explicit null assignment.

> **Also see**: [JSON Merge Patch](../../reference-dictionary/api-design.md#json-merge-patch) · [apipat-03: Idempotency](api-network/api-design-patterns.md#apipat-03-idempotency--preventing-double-charges) · [Idempotency-Key](../../reference-dictionary/api-design.md#idempotency-key)

---

## apipat-11: ETag-Based Optimistic Concurrency Control

> **Source**: [Article §"Mistake 3 — No Concurrency Control on Updates"](../../../articles/medium/stop-designing-rest-apis-advanced-patterns-senior-engineers.md)

| | |
|:---|:---|
| **Problem** | Two clients load the same resource simultaneously, both modify it, and both save — the second save silently overwrites the first client's changes |
| **Root cause** | No concurrency token; last write wins with no detection mechanism at the HTTP layer |
| **Scale impact** | Any concurrent edit path results in permanent, undetected data loss; no error is surfaced to either client |

**Strategy**: Return an `ETag` header (entity tag tied to the resource version) on every `GET`. Require the client to include `If-Match: <etag>` on every `PUT`/`PATCH`. If the server's current version differs from the client's `If-Match` value, return **412 Precondition Failed** — the client must reload and re-apply its changes.

```java
@GetMapping("/products/{id}")
public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
    Product product = productService.findById(id);
    String etag = "\"" + product.getVersion() + "\"";  // maps to JPA @Version
    return ResponseEntity.ok()
        .eTag(etag)                                     // Response: ETag: "5"
        .body(ProductResponse.from(product));
}

@PutMapping("/products/{id}")
public ResponseEntity<ProductResponse> updateProduct(
        @PathVariable Long id,
        @RequestHeader("If-Match") String ifMatch,
        @Valid @RequestBody UpdateProductRequest request) {
    Product product = productService.findById(id);
    String currentEtag = "\"" + product.getVersion() + "\"";
    if (!currentEtag.equals(ifMatch)) {
        return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED).build(); // 412
    }
    return ResponseEntity.ok(ProductResponse.from(productService.update(id, request)));
}
```

**Tradeoff**: Every write workflow now requires a GET before the PUT (GET → modify → PUT with `If-Match`). This is an extra round-trip but is acceptable for resources with low update frequency. For high-frequency collaborative editing, consider conflict-free replicated data types (CRDTs) or operational transforms instead.

> **Azure**: Cosmos DB exposes `_etag` on every document; pass it via `If-Match` in the Cosmos SDK or REST API — the platform enforces optimistic concurrency natively.
> **Also see**: [ETag](../../reference-dictionary/api-design.md#etag) · [Optimistic Locking](../../reference-dictionary/data-concurrency.md#optimistic-locking) · [tx-02: Isolation Levels](concurrency-transactions/concurrency-transactions.md)

---

## apipat-12: Sparse Fieldsets — Client-Driven Field Selection

> **Source**: [Article §"Mistake 4 — No Field Selection"](../../../articles/medium/stop-designing-rest-apis-advanced-patterns-senior-engineers.md)

| | |
|:---|:---|
| **Problem** | A mobile client loading a user list needs only `id` and `name`; the API returns 15 fields — every field is serialized, transmitted, and parsed even though 13 are immediately discarded |
| **Root cause** | A single fixed response shape cannot serve clients with different bandwidth constraints and field requirements simultaneously |
| **Scale impact** | 80%+ payload reduction achievable on mobile paths; avoids endpoint proliferation (creating `/users/minimal`, `/users/summary`, etc. for each consumer) |

**Strategy**: Accept an optional `?fields=` query parameter containing a comma-separated list of field names. Return only the requested fields; fall back to the full response when the parameter is absent (preserves backward compatibility).

```java
@GetMapping("/users")
public ResponseEntity<Page<Map<String, Object>>> getUsers(
        Pageable pageable,
        @RequestParam(required = false) Set<String> fields) {
    return ResponseEntity.ok(userService.findAll(pageable).map(user -> {
        Map<String, Object> full = Map.of(
            "id",        user.getId(),
            "name",      user.getName(),
            "email",     user.getEmail(),
            "role",      user.getRole(),
            "createdAt", user.getCreatedAt()
        );
        if (fields == null || fields.isEmpty()) return full;  // Backward-compatible
        return full.entrySet().stream()
            .filter(e -> fields.contains(e.getKey()))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }));
}
```

Client requests exactly what it needs:

```http
GET /users?fields=id,name
→ [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
```

**Tradeoff**: Field filtering in the Java layer still fetches all columns from the database. For high-traffic list endpoints where the full row scan is expensive, combine with database-level projection (`SELECT id, name FROM users`) and a dedicated query method. This adds implementation complexity but eliminates the unnecessary I/O cost.

> **Also see**: [Sparse Fieldsets](../../reference-dictionary/api-design.md#sparse-fieldsets) · [Pagination (Cursor vs Offset)](../../reference-dictionary/api-design.md#pagination-cursor-vs-offset) · [apipat-04: Pagination](api-network/api-design-patterns.md#apipat-04-pagination--cursor-vs-offset)
