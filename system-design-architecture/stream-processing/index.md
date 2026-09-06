
# Stream Processing

> **Parent**: [System Design Interview Reference](../index.md)

Patterns and strategies for stream processing architectures: Apache Flink fundamentals (Lambda vs Kappa, exactly-once, windowing) and async concurrency patterns across Java and .NET runtimes.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [stream-processing-flink.md](stream-processing-flink.md) | `flink-01` – `flink-05` | Lambda vs Kappa, Batch as special case of streaming, Stateful exactly-once, Windowing, Barrier snapshots |
| [netflix-ads-event-processing-takeaways.md](netflix-ads-event-processing-takeaways.md) | `flink-06` – `flink-15` | Transient KV metadata registry, Canonical event publisher, Flink sessionization, Stream-stream joins, Route-to-data, In-stream dedup, Shadow canary cutovers |
| [async-concurrency-patterns.md](async-concurrency-patterns.md) | `async-01` – `async-04` | Thread pool exhaustion, Parallel I/O, Post-commit dispatch, Silent failures |

## Cross-References

- **Dictionary**: [Messaging](../../reference-dictionary/messaging.md)
- **Azure**: [Event Hubs](../../architecture-azure/integration/), [Azure Stream Analytics](../../architecture-azure/data/)
- **Related**: [Messaging](../messaging/), [JVM & Runtime](../jvm-runtime/), [Performance](../performance/)
- **Taxonomy**: §3.3 Event-Driven & Messaging
