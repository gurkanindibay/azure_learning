---
type: Index
title: "Case Studies"
description: "Real-world system design case studies: Uber architecture, news feed design, URL shortener, and data mesh architecture."
timestamp: 2026-06-27T00:00:00Z
---

# Case Studies

> **Parent**: [System Design Interview Reference](../index.md)

Concrete system design case studies drawn from real-world architectures: Uber's dispatch system, news feed design, URL shortener, and data mesh architectural patterns.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [uber-architecture.md](uber-architecture.md) | `uber-01` – `uber-11` | Decomposition, Geo-partitioning (H3), Ring buffer, LSM vs B-Tree, Dispatch engine, Kalman filter, Map rendering |
| [news-feed.md](news-feed.md) | `feed-01` – `feed-05` | Hybrid fanout, Timeline cache, Celebrity cache, CAP split, Regional deployment |
| [url-shortener.md](url-shortener.md) | `url-01` – `url-05` | Pre-allocated ID ranges, Base62 encoding, Cache-aside redirection, Custom alias atomicity, Async analytics |
| [data-mesh-medallion.md](data-mesh-medallion.md) | `mesh-01` – `mesh-14` | Data Mesh failure modes, Practical decentralization, Semantic layer, Federated governance, Data Fabric, Medallion Architecture |

## Cross-References

- **Dictionary**: [Architecture Patterns](../../reference-dictionary/architecture-patterns.md), [Messaging](../../reference-dictionary/messaging.md)
- **Azure**: [Azure Data Services](../../architecture-azure/data/)
- **Related**: [System Design Interview](../system-design-interview/), [Databases](../databases/), [Messaging](../messaging/)
- **Taxonomy**: §2.1 Application Architecture Patterns
