---
type: Article
title: "Stop Designing REST APIs Like a Mid-Level Dev: 4 Advanced Patterns Senior Engineers Use Instead"
description: "Four production-grade REST API patterns — idempotency keys, JSON Merge Patch, ETag-based concurrency control, and sparse fieldsets — that separate good APIs from contract-grade APIs."
generated: { by: process:okf-migrate, at: 2026-03-16T00:00:00Z }
source: "https://blog.stackademic.com/stop-designing-rest-apis-like-a-mid-level-dev-4advanced-patterns-senior-engineers-use-instead-c8ecbd116b27"
author: "HabibWahid"
---
Your API is versioned, paginated, and validated. Now learn what separates a good API from one that handles real production contracts.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*VD646uNCd14RQjsd2WI6rw.png)

Eight months into my backend career, I thought I had REST figured out. DTOs, proper status codes, pagination, versioning — I had read the articles, applied the patterns, and my APIs passed every code review.

Then a principal engineer reviewed my payment service API. She didn’t comment on what was wrong. She asked a question: “What happens when a client retries a failed payment request? What happens when two clients update the same record at the same time? What does your API tell clients when an endpoint is going away?”

I didn’t have answers. The API worked perfectly in isolation. It had never been designed to handle the messy reality of distributed clients, concurrent requests, and evolving contracts.

That conversation taught me the difference between an API that is built and an API that is designed. Today, I’ll share the 4 advanced patterns that principal engineers apply after the basics are covered.

## The Problem with “Good Enough” APIs

Most developers who have levelled up past the basics write APIs that look like this:

```c
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

  @PostMapping
  public ResponseEntity<OrderResponse> createOrder(
          @Valid @RequestBody CreateOrderRequest request) {
      Order order = orderService.create(request);
      return ResponseEntity.status(HttpStatus.CREATED).body(OrderResponse.from(order));
  }

  @PutMapping("/{id}")
  public ResponseEntity<OrderResponse> updateOrder(
          @PathVariable Long id,
          @Valid @RequestBody UpdateOrderRequest request) {
      Order order = orderService.update(id, request);
      return ResponseEntity.ok(OrderResponse.from(order));
  }
}
```

This is better than a junior’s API. But it still has serious problems:

- No idempotency protection — retried POST requests create duplicate orders
- PUT replaces entirely — clients accidentally wipe fields they didn’t intend to change
- No concurrency control — two simultaneous updates silently overwrite each other
- No field selection — clients download all fields even when they need only two

Let’s fix each of these with patterns that principal engineers apply from day one.

## Mistake 1: No Idempotency on Write Operations

**The Problem:** A mobile client submits a payment. The network drops before the response arrives. The client retries. Your server processes the payment twice. The user is charged twice. There is no way to detect this from the server side.

```c
// ❌ No idempotency — every retry creates a new order
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(
        @Valid @RequestBody CreateOrderRequest request) {
    Order order = orderService.create(request);
    return ResponseEntity.status(HttpStatus.CREATED).body(OrderResponse.from(order));
    // Client retried because network timed out?
    // Two orders created. Two charges processed. No way to know.
}
```

**What Senior Engineers Do:** Require a client-generated idempotency key on every write operation. Store the result of the first execution and return it for every duplicate — without running the logic again.

```c
// ✅ Idempotency key prevents duplicate processing
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(
        @RequestHeader("Idempotency-Key") String idempotencyKey,
        @Valid @RequestBody CreateOrderRequest request) {

    // Already processed? Return the cached result immediately
    return idempotencyService.findResult(idempotencyKey)
        .map(cached -> ResponseEntity.ok(cached))
        .orElseGet(() -> {
            Order order = orderService.create(request);
            OrderResponse response = OrderResponse.from(order);
            // Cache the result against this key - expires after 24 hours
            idempotencyService.save(idempotencyKey, response);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        });
}
```
```c
// Idempotency service — stores results keyed by client-generated ID
@Service
@RequiredArgsConstructor
public class IdempotencyService {

    private final IdempotencyRepository repository;

    public Optional<OrderResponse> findResult(String key) {
        return repository.findByKey(key).map(IdempotencyRecord::getResponse);
    }

    public void save(String key, OrderResponse response) {
        repository.save(new IdempotencyRecord(key, response,
            LocalDateTime.now().plusHours(24)));
    }
}
```

**Why This Matters:**

- Mobile clients and load balancers retry failed requests — without idempotency, retries are dangerous
- The client generates the key, so the server never needs to distinguish a retry from a new request
- Identical key + identical request = same response, zero reprocessing
- Stripe, PayPal, and every major payment API require idempotency keys — it is an industry standard for write operations

## Mistake 2: Using PUT When You Mean PATCH

==**The Problem:**== ==PUT replaces an entire resource. If a client sends a PUT request with only the fields it wants to change, every field not included in the request is silently set to null. Partial updates require partial replacement — that is what PATCH exists for.==

```c
// ❌ PUT replaces everything — missing fields become null
@PutMapping("/users/{id}")
public ResponseEntity<UserResponse> updateUser(
        @PathVariable Long id,
        @RequestBody UpdateUserRequest request) {
    // Client sends only {"email": "new@email.com"}
    // username, phone, address → all set to null silently
    return ResponseEntity.ok(UserResponse.from(userService.update(id, request)));
}
```

**What Senior Engineers Do:** Use PATCH with `JsonMergePatch` for partial updates. Only the fields present in the request are modified. Missing fields stay exactly as they were.

```c
// ✅ PATCH updates only what the client sends
@PatchMapping(value = "/users/{id}",
              consumes = "application/merge-patch+json")
public ResponseEntity<UserResponse> patchUser(
        @PathVariable Long id,
        @RequestBody JsonMergePatch patch) {

    // Load current state
    User existing = userService.findById(id);
    UserRequest currentRequest = UserRequest.from(existing);

    // Apply only the fields present in the patch
    UserRequest patched = applyPatch(patch, currentRequest);
    return ResponseEntity.ok(
        UserResponse.from(userService.update(id, patched)));
}

private UserRequest applyPatch(JsonMergePatch patch, UserRequest target)
        throws JsonPatchException, JsonProcessingException {
    JsonNode targetNode = objectMapper.valueToTree(target);
    JsonNode patchedNode = patch.apply(targetNode);
    return objectMapper.treeToValue(patchedNode, UserRequest.class);
}
```

Client sends only what changed:

```c
PATCH /users/42
Content-Type: application/merge-patch+json

{"email": "new@email.com"}
// username, phone, address - untouched. Only email updated.
```

**Why This Matters:**

- PUT and PATCH are semantically different — using PUT for partial updates is incorrect REST
- `application/merge-patch+json` is the RFC 7396 standard content type for partial updates
- Clients send minimal payloads — no need to fetch the full resource before updating one field
- Accidental data loss from missing fields becomes structurally impossible

## Mistake 3: No Concurrency Control on Updates

**The Problem:** Two clients load the same resource simultaneously. Both modify it. The first saves successfully. The second saves over it — silently overwriting the first client’s change. No error is thrown. Data is permanently lost.

```c
// ❌ Last write wins — first client's changes silently overwritten
@PutMapping("/products/{id}")
public ResponseEntity<ProductResponse> updateProduct(
        @PathVariable Long id,
        @RequestBody UpdateProductRequest request) {
    // Client A loaded version 1, changed price to $20
    // Client B loaded version 1, changed stock to 50
    // Client A saves → version 2, price $20, stock original
    // Client B saves → version 2, price original, stock 50
    // Client A's price change is gone. No error. No warning.
    return ResponseEntity.ok(ProductResponse.from(productService.update(id, request)));
}
```

**What Senior Engineers Do:** Use ETags for optimistic concurrency. The server sends an ETag with every response. Clients must include it in updates. If the resource has changed since the client loaded it, the server rejects the update with 412.

```c
// ✅ ETag-based concurrency — stale updates rejected cleanly
@GetMapping("/products/{id}")
public ResponseEntity<ProductResponse> getProduct(@PathVariable Long id) {
    Product product = productService.findById(id);
    String eTag = "\"" + product.getVersion() + "\"";

    return ResponseEntity.ok()
        .eTag(eTag)  // Sends ETag: "5" in response header
        .body(ProductResponse.from(product));
}

@PutMapping("/products/{id}")
public ResponseEntity<ProductResponse> updateProduct(
        @PathVariable Long id,
        @RequestHeader("If-Match") String ifMatch,
        @Valid @RequestBody UpdateProductRequest request) {

    Product product = productService.findById(id);
    String currentETag = "\"" + product.getVersion() + "\"";
    // Client's ETag doesn't match current version - resource changed since they loaded it

    if (!currentETag.equals(ifMatch)) {
        return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED)
            .body(null);  // 412 - "Someone else changed this. Reload and try again."
    }
    return ResponseEntity.ok(
        ProductResponse.from(productService.update(id, request)));
}
```

**Why This Matters:**

- Lost updates are silent in every API without concurrency control — ETag makes them visible
- 412 Precondition Failed gives clients a clear signal to reload and resolve the conflict
- `product.getVersion()` maps directly to JPA's `@Version` field — zero extra infrastructure
- GitHub, Google Drive, and every collaborative API use ETags — clients already know how to handle them

## Mistake 4: No Field Selection — Always Sending Everything

**The Problem:** A mobile client loading a user list needs only `id` and `name`. Your API returns 15 fields, including address, preferences, and metadata. Every field is serialized, transmitted, and parsed — even the ones that are immediately discarded.

```c
// ❌ All fields returned regardless of what the client needs
@GetMapping("/users")
public ResponseEntity<Page<UserResponse>> getUsers(Pageable pageable) {
    return ResponseEntity.ok(
        userService.findAll(pageable).map(UserResponse::from));
    // Mobile client needs 2 fields. Gets 15. 13 fields wasted on every request.
}
```

**What Senior Engineers Do:** Accept a `fields` query parameter. Return only the requested fields. Clients get lean payloads; bandwidth and parse time drop dramatically.

```c
// ✅ Sparse fieldsets — clients request exactly what they need
@GetMapping("/users")
public ResponseEntity<Page<Map<String, Object>>> getUsers(
        Pageable pageable,
        @RequestParam(required = false) Set<String> fields) {

    Page<User> users = userService.findAll(pageable);

    Page<Map<String, Object>> response = users.map(user -> {
        Map<String, Object> full = Map.of(
            "id",        user.getId(),
            "name",      user.getName(),
            "email",     user.getEmail(),
            "role",      user.getRole(),
            "createdAt", user.getCreatedAt()
        );
        // Return only requested fields - or all fields if none specified
        if (fields == null || fields.isEmpty()) return full;

        return full.entrySet().stream()
            .filter(e -> fields.contains(e.getKey()))
            .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    });

    return ResponseEntity.ok(response);
}
```

Client requests only what it needs:

```c
GET /users?fields=id,name
[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
// 2 fields. Not 15.
```

**Why This Matters:**

- Mobile clients on slow connections download only what they render — response size drops by 80%+
- A single endpoint serves multiple clients with different field requirements — no endpoint proliferation
- The pattern is the foundation of GraphQL — REST can implement it with one query parameter
- `fields` being optional means existing clients who don't send it still receive the full response

***If you have enjoyed this article, you can continue reading part 2 of this article from here.***

## [Stop Designing REST APIs Like a Mid-Level Dev: 4Advanced Patterns Senior Engineers Use Instead…](https://blog.stackademic.com/stop-designing-rest-apis-like-a-mid-level-dev-4advanced-patterns-senior-engineers-use-instead-1990a61f2df6?source=post_page-----c8ecbd116b27---------------------------------------)

### Idempotency, ETags, and field selection make your API correct. These five patterns make it survive — cascading…

blog.stackademic.com

## From Good API to Contract-Grade API

The difference between a good API and a contract-grade API is not whether it works — it is whether it handles the conditions real distributed systems create: retries, concurrent edits, partial updates, bandwidth constraints, and evolving contracts.

**Before:**

```c
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(
        @Valid @RequestBody CreateOrderRequest request) {
    return ResponseEntity.status(201).body(OrderResponse.from(orderService.create(request)));
    // Retry = duplicate order. Concurrent edit = lost update.
    // Mobile payload = 15 fields. V1 removal = surprise outage.
}
```

**After:**

```c
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(
        @RequestHeader("Idempotency-Key") String key,  // Retry-safe
        @Valid @RequestBody CreateOrderRequest request) {

    return idempotencyService.findResult(key)
        .map(ResponseEntity::ok)
        .orElseGet(() -> {
            OrderResponse response = OrderResponse.from(orderService.create(request));
            idempotencyService.save(key, response);    // Cached for retries
            return ResponseEntity.status(201).body(response);
        });
    // PATCH for partial updates — no accidental null overwrites
    // ETag on reads — concurrent edits return 412, not silent corruption
    // ?fields=id,name — mobile gets 2 fields, not 15
}
```

## Your Action Plan

Don’t apply all five at once. Here’s the order that delivers the most impact fastest:

**Week 1:** Add `Idempotency-Key` to every POST endpoint that creates or charges — one header prevents an entire class of duplicate-processing bugs.

**Week 2:** Audit every PUT endpoint — replace partial updates with PATCH and `JsonMergePatch`.

**Week 3:** Add `@Version` to your most-updated entities and wire ETag headers to their GET and PUT endpoints.

**Week 4:** Add `?fields=` support to your highest-traffic list endpoints — measure the payload size reduction.

The next time you write a `@PostMapping`, ask: "What happens if this request arrives twice?" That question alone will change how you design APIs at every level.

These patterns aren’t advanced for their own sake. They are the difference between an API that works in development and one that holds up to the reality of distributed clients, unreliable networks, and systems that need to evolve without breaking the teams that depend on them.

Which of these patterns is missing from your most critical endpoint right now? Drop it in the comments.