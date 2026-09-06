---
type: Article
title: "Idempotency Keys Prevent Duplicate Side Effects"
description: "How idempotency keys, deduplication state, and downstream key propagation make retries safe under network timeouts."
generated: { by: process:okf-migrate, at: 2026-07-10T00:00:00Z }
source: "https://medium.com/javarevisited/interviewer-if-your-backend-handles-850-requests-per-second-and-network-timeouts-happen-how-do-413b8b988456"
author: "Umesh Kumar Yadav"
published: 2026-05-08
---

# Idempotency Keys Prevent Duplicate Side Effects

> **Original title**: Interviewer: If your backend handles 850 requests per second, and network timeouts happen, how do you stop duplicates from escaping downstream?
> **Source**: [Medium article](https://medium.com/javarevisited/interviewer-if-your-backend-handles-850-requests-per-second-and-network-timeouts-happen-how-do-413b8b988456)
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*lGao_XPFTfdpSA409YqafQ.png)

In distributed systems handling high throughput — such as 850 requests per second — network timeouts are inevitable. When a request times out, the client cannot determine whether the server processed the request before the failure. Retrying the request risks creating duplicate side effects downstream.

Many developers assume “exactly-once” delivery is guaranteed by infrastructure. In practice, it is a myth. This article explains how to achieve *effectively once* processing using idempotency in Spring Boot applications.

## 1\. Operation Identity: The Idempotency Key

The foundation of idempotency is a unique identifier for each business operation.

- The client generates a UUID for the operation.
- This UUID travels as an idempotency key in the request header (Idempotency-Key) or payload.
- The server uses this key to identify repeated requests.

Without an idempotency key, identical payloads appear as independent operations, leading to duplicates (e.g., charging a customer twice).

**Example: Idempotency Key in a Spring Boot Controller**

```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

private final OrderService orderService;
    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @RequestHeader(value = "Idempotency-Key", required = true) String idempotencyKey,
            @RequestBody OrderRequest request) {
        
        return ResponseEntity.ok(orderService.processOrder(idempotencyKey, request));
    }
}
```

**Client-side (example with RestTemplate or WebClient):**

```java
String idempotencyKey = UUID.randomUUID().toString();
HttpHeaders headers = new HttpHeaders();
headers.add("Idempotency-Key", idempotencyKey);
```

## 2\. Deduplication State Management

You must persist the idempotency key and operation status to detect duplicates. Recommended approaches:

- **Redis** for high-performance distributed locking and caching (ideal at 850+ RPS).
- **Database unique constraint** within a transaction for simpler scenarios.

Store: key, status (IN\_PROGRESS, COMPLETED, FAILED), timestamp, and cached response.

**Redis Implementation with Spring Data Redis**

```java
@Service
@RequiredArgsConstructor
public class IdempotencyService {

private final StringRedisTemplate redisTemplate;
    private static final Duration LOCK_TTL = Duration.ofSeconds(30);
    private static final Duration RESULT_TTL = Duration.ofMinutes(10);
    public IdempotencyResult checkAndProceed(String key, Supplier<OrderResponse> operation) {
        String lockKey = "idempotency:lock:" + key;
        String resultKey = "idempotency:result:" + key;
        // Try to acquire lock
        Boolean acquired = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "locked", LOCK_TTL);
        if (Boolean.FALSE.equals(acquired)) {
            // Another request is processing - wait or return cached result
            String cached = redisTemplate.opsForValue().get(resultKey);
            if (cached != null) {
                return IdempotencyResult.fromCached(cached);
            }
            throw new IdempotencyConflictException("Request already in progress");
        }
        try {
            OrderResponse result = operation.get();
            String serialized = serialize(result);
            redisTemplate.opsForValue().set(resultKey, serialized, RESULT_TTL);
            return IdempotencyResult.success(result);
        } finally {
            redisTemplate.delete(lockKey); // Release lock
        }
    }
}
```

**Usage in Service Layer:**

```sql
@Service
@RequiredArgsConstructor
public class OrderService {

private final IdempotencyService idempotencyService;
    private final OrderRepository repository;
    @Transactional
    public OrderResponse processOrder(String idempotencyKey, OrderRequest request) {
        return idempotencyService.checkAndProceed(idempotencyKey, () -> {
            // Business logic
            Order order = new Order(...);
            order = repository.save(order);
            // Publish events, call third-party APIs, etc.
            return OrderResponse.from(order);
        });
    }
}
```

**Alternative: Database Unique Constraint**

```java
CREATE TABLE idempotency_records (
    idempotency_key VARCHAR(36) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    response_payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Use @Transactional with a unique index to handle duplicates at the database level.

## 3\. Propagating Idempotency Downstream

Your service is rarely the final destination. You must forward the original idempotency key.

- When calling third-party APIs, pass the same key.
- When publishing events to Kafka/RabbitMQ, include the key in event metadata.
- **Never generate a new UUID on retry.**

**Example: Forwarding Key to Downstream Service**

```java
@Service
public class PaymentClient {

public PaymentResult charge(PaymentRequest req, String originalIdempotencyKey) {
        HttpHeaders headers = new HttpHeaders();
        headers.add("Idempotency-Key", originalIdempotencyKey); // Same key!
        
        return restTemplate.postForObject("/payments", 
                new HttpEntity<>(req, headers), PaymentResult.class);
    }
}
```

**Kafka Event Example:**

```java
event.setMetadata(Map.of("idempotencyKey", originalKey));
kafkaTemplate.send("order-events", event);
```

## 4\. Understanding the “Fake Guarantee” of Exactly-Once Delivery

Network partitions, node crashes, and message broker retries make true exactly-once delivery mathematically impossible at the infrastructure level. Systems offer:

- **At-most-once**: Risk of data loss.
- **At-least-once**: Risk of duplicates.

The practical solution is **at-least-once delivery + strict idempotency** on the consumer side. This combination delivers *effectively once* semantics.

## Best Practices and Considerations

1. **Key Lifetime**: Expire idempotency records after a reasonable window (e.g., 24 hours for financial operations).
2. **Error Handling**: Distinguish between transient failures and permanent ones. Retry only on transient errors.
3. **Monitoring**: Track duplicate request rates and lock contention.
4. **Security**: Validate that the idempotency key belongs to the authenticated user to prevent replay attacks across users.
5. **Testing**: Simulate network timeouts and concurrent requests with the same key.

## Conclusion

Idempotency is not optional for production-grade backend systems. By combining a client-provided idempotency key, fast deduplication storage (Redis), and consistent key propagation downstream, you can safely handle retries even at high throughput.

Implementing these patterns early prevents costly production incidents and builds confidence during system failures.

**Further Reading & Resources:**

- Spring Data Redis Documentation
- Idempotency patterns by AWS and Google Cloud
- “Designing Data-Intensive Applications” by Martin Kleppmann (chapter on distributed systems guarantees)

*This implementation has been battle-tested in services processing thousands of requests per second. Adopt it, test thoroughly, and sleep better during peak traffic.*

## 🔖 Thanks for reading.

- If you enjoyed this article, please consider giving it a clap.👏
- I would appreciate hearing your thoughts in the comments below! 💭
- Follow me for ongoing learning and connection!🔔
- For Interview preparation, please visit [**https://codestutorial.com**](https://codestutorial.com/)**. I hope that it will be helpful.**