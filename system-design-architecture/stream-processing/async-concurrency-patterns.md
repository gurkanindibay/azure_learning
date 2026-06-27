---
type: System Design
title: "Async & Concurrency Patterns"
description: "**Simplest fix (Java)**: Configure a named `ThreadPoolTaskExecutor` bean with explicit pool limits."
timestamp: 2026-06-14T00:00:00Z
---

# 8. Async & Concurrency Patterns

> **Parent**: [System Design Interview Reference](../index.md)  
> **Sources**: [Java Async Patterns](../../articles/medium/async-patterns-java/01-senior-java-concurrency-patterns.md), [.NET Async Patterns](../../articles/medium/async-patterns-java/02-dotnet-async-concurrency-patterns.md)

---

## async-01: Unbounded Thread Pool Exhaustion

> **Source**: [Java Async Patterns](../../articles/medium/async-patterns-java/01-senior-java-concurrency-patterns.md) — Pattern 1, [.NET Async Patterns](../../articles/medium/async-patterns-java/02-dotnet-async-concurrency-patterns.md) — Pattern 1

| | |
|:---|:---|
| **Problem** | Application uses default/unbounded thread pools for async work, leading to thread exhaustion under load |
| **Root cause** | `@Async` without named executor (Java) or `Task.Run` wrapping I/O work (.NET) |
| **Symptoms** | Thread pool saturation, request queuing, cascading failures, health check timeouts |

**Strategy**:

| Approach | Java/Spring | .NET | When to use |
|:---|:---|:---|:---|
| **Named executor** | `ThreadPoolTaskExecutor` with `@Bean("name")` | Hangfire `BackgroundJob.Enqueue()` | Background work — never use raw `Task.Run` |
| **Just await I/O** | Already idiomatic in Spring WebFlux/async controllers | Remove `Task.Run`; just `await` the I/O method | I/O-bound work on the request path |
| **Explicit bounds** | `setCorePoolSize / setMaxPoolSize / setQueueCapacity` | Hangfire worker count in config | Prevent unbounded thread/memory growth |

**Simplest fix (Java)**: Configure a named `ThreadPoolTaskExecutor` bean with explicit pool limits.  
**Simplest fix (.NET)**: Install Hangfire (3 lines of config). Replace `_ = Task.Run(...)` with `BackgroundJob.Enqueue(...)`.

> **Azure**: Azure Functions host.json `maxConcurrentRequests` | **General**: [Bulkhead Pattern](../../../architecture-general/07-reliability-performance-operations/bulkhead-pattern.md)  
> **Related**: [Producer-Consumer with Backpressure](large-data-processing/large-data-constraints.md#proc-03-producer-consumer-with-backpressure) — bounded queues prevent memory exhaustion in data pipelines

---

## async-02: Sequential I/O Calls Instead of Parallel

> **Source**: [Java Async Patterns](../../articles/medium/async-patterns-java/01-senior-java-concurrency-patterns.md) — Pattern 2, [.NET Async Patterns](../../articles/medium/async-patterns-java/02-dotnet-async-concurrency-patterns.md) — Pattern 2

| | |
|:---|:---|
| **Problem** | Multiple independent I/O calls executed sequentially, causing unnecessary latency |
| **Root cause** | `await` each call one after another instead of starting all in parallel |
| **Symptoms** | Response time = sum of all call times instead of max |

**Strategy**:

| Approach | Java/Spring | .NET | Performance gain |
|:---|:---|:---|:---|
| **Parallel execution** | `CompletableFuture.allOf()` | Start all tasks, then `await Task.WhenAll()` | 54% faster (650ms → 300ms example) |
| **Graceful degradation** | `.exceptionally()` fallback | `try/catch` with partial results | Return partial data instead of 500 |

**Example**:

```
Sequential: await A (200ms) → await B (150ms) → await C (300ms) = 650ms
Parallel:   var tA=A(); var tB=B(); var tC=C(); await Task.WhenAll(tA,tB,tC) = 300ms
```

**Key insight**: For independent I/O calls, start all tasks before awaiting any. Each `await` before the next call is unnecessary latency the user pays for.

> **Azure**: Azure Functions fan-out/fan-in pattern | **General**: [Scatter-Gather Pattern](../../../architecture-general/03-integration-communication-architecture/scatter-gather-pattern.md)

---

## async-03: Side Effects Before Transaction Commit

> **Source**: [Java Async Patterns](../../articles/medium/async-patterns-java/01-senior-java-concurrency-patterns.md) — Pattern 3, [.NET Async Patterns](../../articles/medium/async-patterns-java/02-dotnet-async-concurrency-patterns.md) — Pattern 3

| | |
|:---|:---|
| **Problem** | Async side effects (emails, notifications) fire before database transaction commits |
| **Root cause** | `@EventListener` fires immediately (Java) or `Task.Run` placed above `SaveChangesAsync` (.NET) |
| **Symptoms** | Customer receives confirmation email for order that was rolled back |

**Strategy**:

| Approach | Java/Spring | .NET | Complexity |
|:---|:---|:---|:---|
| **Commit first, fire after** | `@TransactionalEventListener(phase = AFTER_COMMIT)` | `await SaveChangesAsync()` first, THEN `BackgroundJob.Enqueue()` | Minimal |
| **Domain events** | Spring Application Events | MediatR `INotification` published after save | Medium |
| **Interceptor pattern** | Built into Spring via phases | `SaveChangesInterceptor.SavedChangesAsync` | Heavy (DDD) |

**Java phases**: `AFTER_COMMIT` ✅ | `AFTER_ROLLBACK` ❌ | `AFTER_COMPLETION` | `BEFORE_COMMIT`

**Simplest fix (.NET)**: Move `await _dbContext.SaveChangesAsync()` **above** the fire-and-forget line. Commit first, fire after — that's the entire fix.

> **Azure**: Azure Service Bus transactions + deferred messages | **General**: [Saga Pattern](../../../architecture-general/03-integration-communication-architecture/messaging-patterns/saga-pattern.md)

---

## async-04: Silent Async Failures

> **Source**: [Java Async Patterns](../../articles/medium/async-patterns-java/01-senior-java-concurrency-patterns.md) — Pattern 4, [.NET Async Patterns](../../articles/medium/async-patterns-java/02-dotnet-async-concurrency-patterns.md) — Pattern 4

| | |
|:---|:---|
| **Problem** | Fire-and-forget async tasks fail silently with no logging or alerting |
| **Root cause** | `void @Async` methods (Java) or unobserved `Task.Run` (.NET) swallow exceptions |
| **Symptoms** | Search index never updated, discovered via support tickets days later |

**Strategy**:

| Approach | Java/Spring | .NET | Complexity |
|:---|:---|:---|:---|
| **Global handler** | `AsyncUncaughtExceptionHandler` | `TaskScheduler.UnobservedTaskException` | Wire at startup |
| **try/catch in task** | Return `CompletableFuture<Void>` | Wrap body in `try/catch` + `_logger.LogError()` | Minimal |
| **Built-in retries** | Spring Retry `@Retryable` | Hangfire `[AutomaticRetry(Attempts = 3)]` | One attribute |

**Simplest fix (.NET)**: Put `try/catch` around the body of every background method. Log the exception. Hangfire's `[AutomaticRetry]` attribute gives retries for free.

> **Azure**: Azure Functions retry policies + dead-letter queues | **General**: [Retry Pattern](../../../architecture-general/07-reliability-performance-operations/retry-pattern.md), [Circuit Breaker](../../../architecture-general/07-reliability-performance-operations/circuit-breaker-pattern.md)

---

## Mental Model: Ownership & Lifecycle

| Dimension | Key Questions | Simple Answer |
|:---|:---|:---|
| **Ownership** | What pool owns this work? What happens when it's full? | Hangfire (durable, visible) or named executor — never raw `Task.Run` |
| **Lifecycle** | When does it run? What if it throws? Who observes the failure? | After `SaveChangesAsync`; `try/catch` + log + retry attribute |

---

## Pattern Selection Guide

| # | Pattern | Java/Spring | .NET (Simple) | When to use |
|:---|:---|:---|:---|:---|
| 1 | **Bounded concurrency** | Named `ThreadPoolTaskExecutor` | Hangfire `BackgroundJob.Enqueue()` | Always — never raw defaults |
| 2 | **Parallel composition** | `CompletableFuture.allOf()` | `Task.WhenAll()` | Multiple independent I/O calls |
| 3 | **Post-commit dispatch** | `@TransactionalEventListener(AFTER_COMMIT)` | `SaveChangesAsync()` first, then fire | Any transactional side effect |
| 4 | **Error observability** | `AsyncUncaughtExceptionHandler` | `try/catch` + `[AutomaticRetry]` | Every background task |

---

## Action Plan

1. **Remove raw `Task.Run`** from I/O — just `await` the method directly or use Hangfire
2. **Fix sequential awaits** — start all tasks, then `await Task.WhenAll()`
3. **Move `SaveChangesAsync` above** fire-and-forget — commit first, fire after
4. **Wrap every background task** in `try/catch` — log failures, add retry attribute

**Key principle**: Concurrency isn't a feature you sprinkle on — it's a system you design. .NET's `async/await` already gives you the model. Hangfire gives you durable background jobs. Use them.