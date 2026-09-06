
# APIs & Network Design

> **Parent**: [System Design Interview Reference](../index.md)

Problems and strategies for API design, versioning, rate limiting, network infrastructure (reverse proxies, load balancers, API gateways), and production API patterns.

## Files

| File | ID Range | Topics |
|:---|:---|:---|
| [api-network-design.md](api-network-design.md) | `api-01` – `api-16` | Versioning, Rate limiting, Large uploads, Async tasks, Consistent hash routing, API deprecation, Multi-tenant limits, Upload sessions, Idempotent chunks, Chunk size selection, Direct-to-storage uploads |
| [api-design-patterns.md](api-design-patterns.md) | `apipat-01` – `apipat-06` | Four pillars, Versioning, Idempotency, Cursor pagination, RFC 7807 errors, Rate limiting |
| [rest-api-senior-patterns.md](rest-api-senior-patterns.md) | `apipat-07` – `apipat-12` | Expand-Contract, Contract-first, HATEOAS, Health checks, JSON Merge Patch, ETag concurrency, Sparse fieldsets |
| [api-idempotency-high-concurrency.md](api-idempotency-high-concurrency.md) | `apipat-13` – `apipat-18` | Idempotency as business guarantee, Defense in depth, Unique identifiers + DB constraints, State machines, Optimistic locking, Redis Lua atomic tokens |
| [reverse-proxy-lb-gateway.md](reverse-proxy-lb-gateway.md) | `gw-01` – `gw-06` | Reverse proxy, Load balancer, API gateway, L4 vs L7, Production layering, Decision matrix |

## Cross-References

- **Dictionary**: [API Design](../../reference-dictionary/api-design.md)
- **Azure**: [Azure Networking](../../architecture-azure/networking/), [Front Door](../../architecture-azure/networking/)
- **Related**: [Resilience](../resilience/), [Security](../security/)
- **Taxonomy**: §3.3 Event-Driven & Messaging
