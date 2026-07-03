---
type: Article
title: "How to Guarantee API Idempotency Under High Concurrency"
description: "Prevent duplicate orders, duplicate payments, and data inconsistencies in distributed systems using token-based idempotency, Redis atomic Lua scripts, optimistic locking, and state machines."
source: "https://medium.com/@umeshcapg/how-to-guarantee-api-idempotency-achieving-idempotency-under-high-concurrency-ed3854aa49c2"
author: "Umesh Kumar Yadav"
published: 2026-06-12
created: 2026-07-03
tags:
  - api-design
  - idempotency
  - redis
  - concurrency
  - distributed-systems
---

# How to Guarantee API Idempotency Under High Concurrency

*Prevent duplicate orders, duplicate payments, and data inconsistencies in distributed systems.*

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*c2qz2ZQcNQ-QqFGi3V4bcQ.png)


Imagine a customer clicks the **“Pay Now”** button three times because the page appears frozen.

Or a mobile application automatically retries a request because of a network timeout.

Or two microservices simultaneously process the same message from a queue.

Without proper safeguards, your system may:

- Create duplicate orders
- Charge customers multiple times
- Process the same business event repeatedly
- Corrupt critical financial data

This is where **API Idempotency** becomes essential.

In modern distributed systems, idempotency is not just a nice-to-have feature — it is a fundamental design principle for building reliable and scalable applications.

In this article, we’ll explore:

- What API idempotency means
- Why duplicate requests occur
- Various idempotency implementation strategies
- How to handle idempotency under high concurrency
- A practical Spring Boot + Redis implementation

## What Is API Idempotency?

The term *idempotent* originates from mathematics.

An operation is considered **idempotent** if executing it multiple times produces the same result as executing it once.

In API design, idempotency means:

> *Multiple identical requests should have the same effect as a single request.*

Regardless of how many times the client sends the request, the server should ensure that the business operation is executed only once.

## Example 1: Order Creation

Suppose a user clicks the **Create Order** button twice.

## Without Idempotency

Request #1 → Order Created → Order ID 1001

Request #2 → Order Created → Order ID 1002

Result:

❌ Duplicate orders

## With Idempotency

Request #1 → Order Created → Order ID 1001

Request #2 → Duplicate Request Detected

Result:

✅ Only one order exists

## Example 2: Payment Processing

A user submits a payment request.

Due to network issues, the client retries the request.

## Without Idempotency

Payment Request #1 → ₹100 deducted

Payment Request #2 → ₹100 deducted again

Result:

❌ Customer charged twice

## With Idempotency

Payment Request #1 → ₹100 deducted

Payment Request #2 → Already Processed

Result:

✅ Customer charged once

## Why Do Idempotency Problems Occur?

Before solving the problem, we must understand its causes.

## 1\. Network Instability

Network failures may cause:

- Packet loss
- Request timeout
- Delayed responses

The client assumes the request failed and retries it.

Result:

Multiple identical requests reach the server.

## 2\. User Actions

Users often:

- Double-click buttons
- Refresh pages
- Navigate backward and resubmit forms

These actions can trigger duplicate requests.

## 3\. Retry Mechanisms

Many systems automatically retry failed requests.

Examples:

- Nginx retries
- Feign retries
- RPC retries
- Service mesh retries

These retries improve availability but increase the risk of duplicate execution.

## 4\. Scheduled Tasks

Poorly designed scheduling systems may execute the same task multiple times.

Example:

Two scheduler nodes accidentally trigger the same job.

## 5\. Message Queue Redelivery

Systems such as:

- Kafka
- RabbitMQ
- RocketMQ

typically guarantee **at-least-once delivery**.

This means a message may be consumed more than once.

## 6\. High-Concurrency Scenarios

When multiple requests operate on the same resource simultaneously:

- Race conditions occur
- Duplicate business operations become possible

## Frontend Strategies for Idempotency

Frontend solutions improve user experience but should never be the only protection mechanism.

## Disable Buttons After Submission

Once a user submits a request:

- Disable the button
- Show a loading spinner

Example:

```c
submitBtn.disabled = true;
```

Benefits:

- Prevents accidental double-clicks
- Reduces duplicate requests

Limitation:

❌ Cannot prevent retries from other clients or network failures.

## PRG Pattern (POST → Redirect → GET)

The PRG pattern prevents duplicate form submissions caused by page refreshes.

## Workflow

## Step 1

User submits form:

```c
POST /orders
```

## Step 2

Server processes request and responds:

```c
302 Found
Location: /orders/success
```

## Step 3

Browser automatically sends:

```c
GET /orders/success
```

## Step 4

If the user refreshes the page:

Only the GET request is repeated.

Result:

✅ No duplicate POST request

## Token-Based Idempotency

One of the most popular solutions.

The idea:

Every business operation must carry a unique token.

The token can only be consumed once.

## Workflow

## Step 1: Generate Token

Client requests:

```c
GET /token
```

Server returns:

```c
{
  "token":"01HXA1M3AZTYA8..."
}
```

## Step 2: Store Token

Store token in Redis.

Example:

```c
token:01HXA1M3AZTYA8...
```

Expiration:

```c
5 minutes
```

## Step 3: Submit Request

```c
POST /orders
```

Headers:

```c
Token: 01HXA1M3AZTYA8...
```

## Step 4: Verify Token

Server:

1. Checks whether token exists
2. Deletes token atomically
3. Executes business logic

If token already used:

```c
{
  "message":"Duplicate request"
}
```

## Server-Side Idempotency Strategies

Frontend protection alone is insufficient.

True idempotency must be enforced on the server.

## 1\. Unique Business Identifiers

Every request carries a globally unique ID.

Examples:

```c
OrderNo
TransactionId
RequestId
ReferenceId
```

When the server receives a request:

```c
SELECT *
FROM orders
WHERE request_id = ?
```

If already exists:

Reject request.

This is commonly used when integrating ERP systems and payment gateways.

## 2\. Request Parameter Verification

Certain parameters can help detect duplicate submissions.

Example:

```c
{
  "timestamp":"1710845000"
}
```

The server rejects requests outside a valid time window.

However:

⚠️ Timestamp alone is not sufficient because it does not guarantee uniqueness.

## 3\. State Machine Design

A state machine naturally prevents invalid state transitions.

Example Order States:

```c
CREATED
PAID
SHIPPED
COMPLETED
```

If an order is already PAID:

```c
PAID -> PAID
```

is invalid.

Therefore:

Duplicate payment requests are rejected.

## 4\. Optimistic Locking

Optimistic locking prevents concurrent modifications.

Database table:

```c
CREATE TABLE product (
    id BIGINT,
    stock INT,
    version INT
);
```

Update SQL:

```c
UPDATE product
SET stock = stock - 1,
    version = version + 1
WHERE id = ?
AND version = ?
```

Only one request succeeds.

Others fail and retry.

This ensures consistency under concurrency.

## How to Achieve Idempotency Under High Concurrency

This is where many implementations fail.

Consider:

100 users submit the same request simultaneously.

If token validation is not atomic:

Thread A:

- Checks token exists

Thread B:

- Checks token exists

Both pass validation.

Both execute business logic.

Result:

❌ Duplicate processing

## The Correct Approach: Atomic Operations

Use Redis atomic commands.

Examples:

```c
SETNX
GETDEL
Lua Script
```

Atomicity guarantees:

Only one thread can consume the token.

## Why Lua Scripts?

Redis executes Lua scripts as a single atomic operation.

Example:

```c
if redis.call('get', KEYS[1]) == KEYS[2]
then
   return redis.call('del', KEYS[1])
else
   return 0
end
```

This combines:

- Validation
- Deletion

into one operation.

Result:

✅ No race condition

## Spring Boot + Redis Implementation

Let’s implement token-based idempotency.

## Dependencies

```c
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>

<dependency>
    <groupId>com.github.f4b6a3</groupId>
    <artifactId>ulid-creator</artifactId>
    <version>5.2.0</version>
</dependency>
```

## Generate Token

```c
public String generateToken(
        String accountSecret,
        String operationType) {

    String token =
        UlidCreator.getUlid().toString();
    String key =
        String.format(
            "idempotent:%s:%s:%s",
            accountSecret,
            operationType,
            token);
    redisTemplate.opsForValue()
            .set(key,
                 "VALID",
                 5,
                 TimeUnit.MINUTES);
    return token;
}
```

## Validate Token

```c
String script =
"if redis.call('get', KEYS[1]) then " +
" return redis.call('del', KEYS[1]) " +
"else return 0 end";
```

Execute Lua:

```c
Long result =
redisTemplate.execute(
    redisScript,
    Collections.singletonList(key));

return result != null && result > 0;
```

Only one request can successfully consume the token.

## Business Logic

```c
public String createOrder(
        OrderRequest request,
        String token) {

    if (!validateToken(token)) {
        throw new RuntimeException(
            "Duplicate request");
    }
    return "Order Created";
}
```

## High-Concurrency Test

Imagine three concurrent requests arriving with the same token.

## Request A

Token validation succeeds

Order created

## Request B

Token already deleted

Rejected

## Request C

Token already deleted

Rejected

Result:

```c
Success: 1
Failed : 2
```

Exactly one order is created.

This is true idempotency.

## Best Practices

For critical financial systems:

Combine multiple techniques:

## Payment Systems

- Unique transaction ID
- State machine
- Redis token
- Database unique index

## Order Systems

- Request ID
- Token mechanism
- Optimistic locking

## Message Consumers

- Message ID
- Consumption record table
- Redis deduplication

## Distributed Systems

- Redis atomic operations
- Database constraints
- Saga state tracking

Never rely on a single protection mechanism.

## Conclusion

Idempotency is one of the most important design principles in modern distributed systems.

Without it, systems become vulnerable to:

- Duplicate orders
- Duplicate payments
- Data inconsistencies
- Concurrency issues

Common implementation approaches include:

- Frontend button disabling
- PRG (POST/Redirect/GET)
- Unique request identifiers
- State machines
- Optimistic locking
- Token-based validation
- Redis atomic operations

For high-concurrency business scenarios such as payments, inventory deduction, and order creation, a **Redis-based token mechanism combined with atomic Lua scripts** is one of the most effective solutions.

The key takeaway is simple:

> *Idempotency is not just a technical implementation.*
> 
> *It is a business guarantee that ensures an operation produces the same outcome regardless of how many times it is requested.*

Design it carefully, test it under concurrency, and combine multiple safeguards to build truly reliable systems.