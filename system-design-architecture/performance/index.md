---
type: Index
title: "Runtime Performance"
description: "System-design problems and strategies for microservices runtime performance, language selection tradeoffs, and measurement-driven optimization."
timestamp: 2026-06-27T00:00:00Z
---

# Runtime Performance

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for optimizing microservices runtime performance: language selection tradeoffs (Java, Go, Python, Rust), measurement-driven architecture, and rewrite decisions.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [microservices-runtime-performance.md](microservices-runtime-performance.md) | `perf-01` – `perf-08` | Virtual threads vs goroutines, Leyden AOT, TCP_NODELAY, Benchmark methodology, Runtime shape selection, Measurement-driven architecture |
| [python-to-rust-rewrite.md](python-to-rust-rewrite.md) | `perf-09` – `perf-12` | Python GIL bottleneck, Rewrite velocity tax, Rust compile-time cost, Async Rust shared mutable state, Native extension middle path |
| [rust-logic-errors-takeaways.md](rust-logic-errors-takeaways.md) | `perf-13` – `perf-16` | Compiler guarantee boundaries, wildcard match hazards, exhaustive matching policy, fail-open vs fail-closed behavior |

## Cross-References

- **Dictionary**: [Java/JVM](../../reference-dictionary/java-jvm.md)
- **Related**: [JVM & Runtime](../jvm-runtime/), [Software Architecture](../software-architecture/)
- **Taxonomy**: §7.2 Performance Architecture
