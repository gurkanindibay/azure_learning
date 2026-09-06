
# Runtime Performance

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for optimizing microservices runtime performance: language selection tradeoffs (Java, Go, Python, Rust), measurement-driven architecture, and rewrite decisions.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [microservices-runtime-performance.md](microservices-runtime-performance.md) | `perf-01` – `perf-06` | Virtual threads vs goroutines, Leyden AOT, TCP_NODELAY, Benchmark methodology, Runtime shape selection, Measurement-driven architecture |
| [python-to-rust-rewrite.md](python-to-rust-rewrite.md) | `perf-07` – `perf-12` | Python GIL bottleneck, Rewrite velocity tax, Rust compile-time cost, Async Rust shared mutable state, Native extension middle path |
| [rust-logic-errors-takeaways.md](rust-logic-errors-takeaways.md) | `perf-13` – `perf-16` | Compiler guarantee boundaries, wildcard match hazards, exhaustive matching policy, fail-open vs fail-closed behavior |
| [cpu-memory-latency-takeaways.md](cpu-memory-latency-takeaways.md) | `perf-17` – `perf-20` | Memory wall & CPU stalls, CPU cache hierarchy (L1/L2/L3), sequential access & prefetching vs pointer chasing, false sharing, cache-friendly data layouts |

## Cross-References

- **Dictionary**: [Java/JVM](../../reference-dictionary/java-jvm.md), [Concurrency Models & Runtimes](../../reference-dictionary/concurrency-runtimes.md)
- **Related**: [JVM & Runtime](../jvm-runtime/), [Software Architecture](../software-architecture/)
- **Taxonomy**: §7.2 Performance Architecture
