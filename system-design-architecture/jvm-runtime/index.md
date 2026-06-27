---
type: Index
title: "JVM & Runtime Performance"
description: "System-design problems and strategies for JVM memory management, GC tuning, Java vs Go threading models, and microservices runtime performance."
timestamp: 2026-06-27T00:00:00Z
---

# JVM & Runtime Performance

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for JVM-based systems: memory management, garbage collection tuning, thread model comparisons (Java vs Go), and microservices runtime performance optimization.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [jvm-memory-gc.md](jvm-memory-gc.md) | `jvm-01` – `jvm-09` | Heap allocation rate, Stack overflow, Metaspace leaks, Full GC storms, Memory leaks, Thread explosion, HashMap collisions |
| [jvm-thread-model-vs-go.md](jvm-thread-model-vs-go.md) | `jvm-10` – `jvm-13` | Java 1:1 thread model ceiling, Go M:N goroutine scheduler, Virtual Thread pinning trap, Spring Boot 3.2 migration path |

## Cross-References

- **Dictionary**: [Java/JVM](../../reference-dictionary/java-jvm.md), [.NET Multithreading](../../reference-dictionary/dotnet-multithreading.md)
- **Related**: [Performance](../performance/), [Concurrency & Transactions](../concurrency-transactions/)
- **Taxonomy**: §2.3 Concurrency & Asynchronous Processing
