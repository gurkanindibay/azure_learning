---
type: Article
title: "API Gateway Becomes a Bottleneck: System Design Deep Dive on Gateway Scaling, Authentication Overhead, Edge Caching, and Request Routing Optimization"
description: "Deep dive into why API gateways become single points of failure under 10x traffic spikes: resolving in-path JWT verification CPU saturation, per-request connection overhead, synchronous logging I/O, and Redis rate-limiting bottlenecks through auth sidecars, connection pooling, and hybrid token buckets."
source: "https://codefarm0.medium.com/api-gateway-becomes-a-bottleneck-system-design-deep-dive-on-gateway-scaling-authentication-cfff15529317"
author: "Arvind Kumar"
published: 2026-08-03
created: 2026-09-21
tags:
  - api-gateway
  - system-design
  - authentication
  - connection-pooling
  - rate-limiting
  - edge-caching
  - request-coalescing
---

# API Gateway Becomes a Bottleneck: System Design Deep Dive on Gateway Scaling, Authentication Overhead, Edge Caching, and Request Routing Optimization

*The API gateway was the single point of entry for all services. It handled authentication, rate limiting, routing, logging, and request transformation. Traffic grew 10x. The gateway CPU hit 100%. Every API call slowed from 5ms to 3 seconds. And because every request passed through the gateway, the entire platform went down together.*

The API gateway is the most common single point of failure in microservice architectures. It is also the most overloaded component. Every request hits it. Every cross-cutting concern runs in it. And when it slows down, every downstream service is affected simultaneously.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*An0za01OSMwgCSEP6D8oZA.png)

The outage was not caused by any single service. It was caused by the gateway doing too much work per request and running out of CPU. The fix is not to scale the gateway vertically — it is to redesign what the gateway does and how it does it.

Interviewers love this question because it tests whether you can identify the single most critical bottleneck in a microservice system:

## Concepts at a Glance

- Gateway responsibilities — why gateways become overloaded
- Authentication offloading — moving auth to a dedicated sidecar or service
- Connection pooling — reusing upstream connections instead of creating new ones
- Edge caching — caching responses at the gateway to reduce downstream calls
- Request coalescing — combining duplicate requests into one
- Asynchronous processing — moving non-critical work off the request path
- Horizontal scaling with session awareness

In the previous episode, we explored cascading microservice failures and resilience patterns. Today, we tackle the gateway — the most critical bottleneck in any microservice system.

Let’s watch how the conversation unfolds.

---

## The Scenario

**Arvind (Interviewer):**  
Your platform has 50 microservices. All traffic goes through an API Gateway. Traffic grew from 10K requests per second to 100K RPS. The gateway now runs at 100% CPU. Every API call takes 2–3 seconds.

Users report timeouts. Downstream services report connection refused errors because the gateway’s connection pool is exhausted. The gateway team keeps adding more instances, but the CPU stays at 100%.

What is happening inside the gateway? How would you fix this without rewriting the entire system?

**Kiran (Candidate):**  
Let me trace what the gateway does for each request.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*BWWEg6dJibRhWA3FZvBIQQ.png)

Each request triggers:

1. **JSON body parsing** — CPU and memory allocation
2. **JWT validation** — RSA signature verification is CPU-intensive (~0.5–1ms per verification)
3. **Auth service call** — network round trip + auth processing
4. **Rate limit check** — Redis call per request
5. **Synchronous logging** — I/O on the request path
6. **Request transformation** — header manipulation, body rewriting
7. **New upstream connection** — TCP + TLS handshake for every request
8. **Response transformation** — another CPU cycle

At 100K RPS, the gateway is doing 800K operations per second. Each operation adds latency. Combined, they saturate the CPU.

---

## Problem 1: Authentication on the Request Path

**Arvind:**  
Where do we start?

**Kiran:**  
Authentication. JWT verification is the single most CPU-intensive operation the gateway performs.

**Solution options**:

1. **Auth sidecar**: Deploy an auth proxy as a sidecar alongside each gateway instance. The sidecar verifies JWTs locally using cached public keys. No network calls to AuthService. JWT verification drops from ~1ms to ~0.05ms.
2. **Separate auth gateway**: Deploy a dedicated auth gateway tier. The first tier only validates tokens and returns a signed “pre-verified” context token. The second tier (API gateway) trusts this token and does not re-verify. The auth gateway scales independently.
3. **Token introspection cache**: Cache token validation results. If the same token is used within 5 minutes, skip re-validation. For access tokens with short TTLs, this has high cache hit rates.

---

## Problem 2: Per-Request Connection Overhead

**Arvind:**  
What is the second biggest bottleneck?

**Kiran:**  
Connection management. Every request to an upstream service creates a new TCP connection with a TLS handshake.

**Solution**:

1. **Connection pooling**: Maintain a pool of pre-warmed HTTP connections to each upstream service. Requests reuse connections instead of creating new ones. Pool size = 20–50 connections per upstream. This eliminates TCP + TLS overhead for most requests.
2. **HTTP/2 multiplexing**: A single HTTP/2 connection handles multiple concurrent requests on separate streams. No connection overhead per request. HTTP/2 also supports header compression and server push.
3. **Keep-alive with aggressive reuse**: Configure keep-alive timeouts long enough (60s) to maximize connection reuse. Monitor connection reuse ratio. Target >99% reuse.

---

## Problem 3: Synchronous Logging and Analytics

**Arvind:**  
What about logging and analytics? Every request is logged.

**Kiran:**  
Synchronous logging is a hidden performance killer.

**Solution**: Move all logging, analytics, and audit trail writes off the request path. Use an in-memory buffer to enqueue log events in microseconds. A background worker batches and ships logs asynchronously.

---

## Problem 4: Rate Limiting Design

**Arvind:**  
Rate limiting is critical. How do we make it efficient?

**Kiran:**  
Distributed rate limiting with Redis is a common bottleneck. Every request does a Redis round trip.

**Solution**: Use a hybrid token bucket. Each gateway instance maintains a local token bucket that is periodically synchronized with a global Redis counter (every 100ms instead of per request). This reduces Redis load from 100K ops/sec to 10 ops/sec.

---

## Full Architecture

**Arvind:**  
Design the optimized gateway architecture.

**Kiran:**

**Key decisions**:

- **Edge CDN**: Cache responses at the edge. Read-heavy APIs see 70%+ cache hit rates at the CDN level. These requests never reach the gateway.
- **Tier 1 (Auth Gateway)**: Dedicated stateless tier. Only verifies tokens. Uses ECDSA instead of RSA (ECDSA verification is ~10x faster for the same security level). Local LRU cache for token validation results.
- **Tier 2 (Lightweight Gateway)**: After auth is offloaded, the gateway only routes, rate-limits (local), and logs (async). Connection pooling with HTTP/2 eliminates per-request connection overhead.
- **Hybrid rate limiting**: Local token buckets synchronized with Redis every 100ms instead of per request. Reduces Redis load by 99.99%.
- **Async logging**: In-memory buffer with batch flush. No I/O on the request path.
- **Request coalescing**: If the same request is already in-flight (same cache key), subsequent requests wait for the first response instead of duplicating the call.

**Arvind:**  
What monitoring matters for the gateway?

**Kiran:**

1. **Gateway CPU per request** — The most important metric. Track CPU microseconds consumed per request. A rising trend means new features are being added to the gateway without considering the performance cost.
2. **Connection reuse ratio** — Percentage of requests that reuse an existing connection. Target >99%. Below 90% means connection pooling is not working.
3. **Auth verification latency (p50, p99)** — If auth is offloaded, this should be <1ms. If it rises, the auth tier needs scaling.
4. **Local rate limiter sync latency** — Time to sync with Redis every 100ms. If this exceeds 10ms, the sync interval is too aggressive.
5. **Cache hit ratio at each tier** — CDN hit rate, auth cache hit rate, response cache hit rate. A dropping hit rate indicates cache configuration issues.
6. **Request latency breakdown** — How much time is spent in each gateway phase: parsing, auth, rate limiting, routing, upstream call, response transformation. This reveals which phase is the bottleneck.
7. **Gateway error rate by upstream** — Which upstream services cause the most gateway errors. A failing upstream can make the gateway appear to be the problem.

---

## Conclusion

The API gateway is the single most overloaded component in a microservice architecture. Every request hits it. Every cross-cutting concern runs in it. When it fails, the entire platform fails.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*tBdV6HMgi7bGCmIr5eDlMQ.png)

**The most important design rule**: The gateway should do as little work as possible on the request path. Every microsecond spent in the gateway is a microsecond that every user of every service pays. Move work off the request path. Cache aggressively. Pool connections. And never, ever do synchronous I/O in the gateway’s request handler.