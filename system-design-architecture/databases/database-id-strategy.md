---
type: System Design
title: "Database ID Generation Strategies"
description: "Clarifies the dual-layer ID strategy from sdi-50: expose non-enumerable UUIDs/ULIDs externally while keeping auto-increment BIGINTs internally for B-tree efficiency."
generated: { by: process:okf-migrate, at: 2026-07-11T00:00:00Z }
---

# Database ID Generation Strategies

> **Parent**: [Databases & Query Performance](index.md)  
> **Source**: [20 Design Interview Questions](../../../articles/databases/20-design-interview-questions.md) — Q#1 (UUID indexing); [System Design Interview Roadmap](../system-design-interview/interview-roadmap.md#sdi-06-id-strategy--soft-deletes) (`sdi-06`)  
> **Purpose**: Clarify the external/internal ID split referenced in [`sdi-50`](../system-design-interview/system-design-review-plan.md#sdi-50-id-strategy--uuid-external-auto-increment-internal).

---

## db-18: External UUID, Internal Auto-Increment

| | |
|:---|:---|
| **Problem** | Using a single ID type for both APIs and database primary keys forces a trade-off between security/privacy and storage/indexing performance. |
| **Root cause** | Auto-increment integers leak business metrics and are enumerable; random UUIDs fragment B-tree indexes and bloat storage. |

**Strategy — separate the two layers:**

| Layer | ID Type | Rationale |
|:---|:---|:---|
| **External / API** | UUID v4, UUID v7, ULID, or Snowflake | Non-enumerable, no coordination across services, safe to expose publicly |
| **Internal / DB PK** | Auto-increment `BIGINT` | Sequential inserts, compact 8 bytes, fast B-tree lookups and JOINs |

The external ID is stored as a secondary unique indexed column. All API requests resolve to the internal PK, which is never returned to clients.

---

## Why Auto-Increment IDs Fail as Public Identifiers

| Risk | Example |
|:---|:---|
| **Business intelligence leakage** | `GET /orders/1042` and `GET /orders/98723` reveal order volume to competitors. |
| **Enumeration attacks** | Sequential IDs let an attacker scrape every record by iterating IDs. |
| **Hot spots in distributed DBs** | Auto-increment requires coordination (a single counter) and concentrates inserts at the end of the B-tree. |

### Hot spots: range partitioning vs hash partitioning

The classic hot-spot problem is most visible when a distributed database uses **range partitioning**: every new ID lands at the leading edge of the highest range, so all writes converge on the same shard and the same B-tree leaf. That shard becomes the CPU, disk, and lock-contention bottleneck while other shards sit idle.

**Hash partitioning** on the auto-increment key removes the range-based hot spot by spreading inserts across shards more evenly, but it does **not** eliminate contention entirely:

| Remaining hot spot | Why it persists |
|:---|:---|
| **Rightmost B-tree leaf** | The primary index still appends sequentially; every insert still targets the trailing leaf page, which is constantly locked and rewritten. |
| **Time-ordered secondary indexes** | Indexes on `created_at` cluster near the current timestamp regardless of how the PK is partitioned, forming an append tail. |
| **ID allocation coordination** | Strictly monotonic IDs across nodes still need a central allocator, clock sync, or reserved ranges — any of which can become a bottleneck or failure point. |
| **Partition-leader amplification** | In leader-based distributed databases, writes still funnel through the partition leader. If inserts arrive faster than replication can follow, the leader becomes the hot spot. |

This is why the recommended split is **UUID/ULID externally, auto-increment `BIGINT` internally**: the external ID avoids both the security and coordination problems, while the internal ID keeps the single-node relational index compact and fast.

Auto-increment is still an excellent *internal* choice because sequential inserts keep the clustered index compact and because foreign-key relationships stay small (8 bytes vs. 16+ bytes per UUID).

---

## Why Random UUIDs Fail as Primary Keys

Standard UUIDv4 values are cryptographically random. In a B-tree primary key:

- Every `INSERT` lands at a random leaf page.
- Pages split frequently and become fragmented.
- Buffer pool efficiency drops because recently inserted rows are not physically near each other.
- Writes can be **2–5× slower** than sequential inserts once the index exceeds RAM.

See [`db-01: Random UUID Indexing`](query-performance.md#db-01-random-uuid-indexing) for mitigations such as UUIDv7/ULID and fill-factor tuning.

---

## Choosing an External ID Format

| Format | Sortable | Size | Collision risk | Best for |
|:---|:---:|:---:|:---|:---|
| **UUID v4** | No | 16 bytes | Negligible | Default non-enumerable public ID |
| **UUID v7** | Yes | 16 bytes | Negligible | Standard time-sortable ID (RFC 9562) |
| **ULID** | Yes | 16 bytes / 26 chars (Base32) | Negligible | URL-safe, lexicographically sortable IDs |
| **Snowflake** | Yes | 8 bytes | Negligible | High-throughput distributed generation with embedded timestamp |
| **KSUID** | Yes | 20 bytes | Negligible | Time-sortable with higher entropy than ULID |

**Guidance**:
- Prefer **UUIDv7** for new systems — it is the IETF standard and is time-sortable.
- Use **ULID** when you need a shorter, URL-safe string representation.
- Use **Snowflake** when you need Twitter-style IDs with embedded millisecond timestamps and datacenter/worker shards.
- Use **KSUID** when you need time-sortable IDs with high entropy and no worker coordination.
- Keep **UUIDv4** only when true randomness (no time leakage) is required.

### Snowflake ID

A [Snowflake ID](#snowflake-id) is a 64-bit integer designed for high-throughput distributed generation. It embeds a timestamp, datacenter ID, worker ID, and a per-worker sequence number.

| Field | Bits | Purpose |
|:---|:---:|:---|
| Sign / unused | 1 | Reserved, always 0 |
| Timestamp | 41 | Milliseconds since a custom epoch |
| Datacenter ID | 5 | Up to 32 datacenters |
| Worker ID | 5 | Up to 32 workers per datacenter |
| Sequence | 12 | Up to 4,096 IDs per worker per millisecond |

**Capacity**: ~69 years of millisecond timestamps and ~4.1 million unique IDs per second across the full datacenter/worker grid.

**Advantages**:
- Compact 8-byte storage (fits a `BIGINT`).
- Roughly time-ordered, which improves index locality.
- No central coordination at generation time once worker IDs are assigned.

**Risks**:
- Worker and datacenter IDs must be assigned and kept unique at deployment time.
- Clock skew or NTP step changes can produce out-of-order or duplicate IDs.
- Embedded timestamp reveals creation time and makes IDs guessable.

**Best for**: Twitter/X timelines, Discord messages, Instagram media IDs, and any high-write system where a compact numeric ID is acceptable.

### KSUID

A [KSUID](#ksuid) (K-Sortable Unique Identifier) is a 20-byte identifier that combines a timestamp with a large random payload. It was designed to provide ULID-like sortability with higher entropy and no worker coordination.

| Field | Size | Purpose |
|:---|:---:|:---|
| Timestamp | 4 bytes | Seconds since the KSUID epoch (2014-05-13) |
| Random payload | 16 bytes | Cryptographically random entropy |

**Capacity**: ~136 years of timestamps and $2^{128}$ (~$3.4 \times 10^{38}$) possible values per second.

**Advantages**:
- No central coordinator or worker IDs are required.
- Higher entropy than ULID (128 random bits vs. 80), making IDs less guessable.
- Time-sortable at one-second granularity.
- URL-safe Base62 string is 27 characters.

**Risks**:
- Larger than UUIDs and Snowflake IDs (20 bytes vs. 16 or 8).
- Time granularity is seconds, not milliseconds.
- Embedded timestamp reveals creation time.

**Best for**: Event streams, distributed logs, and systems that need sortable IDs without the operational complexity of worker ID assignment.

---

## Implementation Pattern

```sql
CREATE TABLE orders (
    id              BIGSERIAL PRIMARY KEY,        -- internal only
    public_id       UUID NOT NULL UNIQUE,        -- exposed in APIs
    user_id         BIGINT NOT NULL,
    total_cents     BIGINT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ                   -- soft delete
);

CREATE INDEX idx_orders_public_id ON orders(public_id);
```

```python
# API layer resolves public_id → internal id, then operates on internal id
order = db.execute(
    "SELECT id FROM orders WHERE public_id = :public_id AND deleted_at IS NULL",
    {"public_id": public_id}
)
# All downstream joins/foreign keys use order.id (BIGINT)
```

---

## Mapping External ↔ Internal IDs

| Direction | Mechanism | Where |
|:---|:---|:---|
| External → Internal | Unique index on `public_id` | API gateway / service entry point |
| Internal → External | Include `public_id` in read models / DTOs | Response serialization layer |
| Bulk export | Join on `public_id` in reporting queries | Analytics / admin exports |

**Avoid** exposing the internal `id` in:
- REST URLs (`/api/v1/orders/{public_id}` is safe; `/orders/{id}` is not).
- Webhook payloads sent to third parties.
- Client-side caches or logs.

---

## Tradeoffs

| Approach | Pros | Cons |
|:---|:---|:---|
| **External UUID + internal BIGINT** | Best of both worlds: secure public IDs and fast internal indexing | Extra column, extra index, mapping overhead at API boundary |
| **UUID only (PK + public)** | Simple schema, no mapping | Slower writes, larger indexes, bigger foreign keys |
| **Auto-increment only** | Fastest writes and smallest storage | Leaks volume, enumerable, hard to distribute |
| **UUIDv7/ULID as PK** | Time-sortable, better locality than UUIDv4 | Still 16 bytes per key and per foreign key; not as compact as BIGINT |

---

## When to Use Which

| Scenario | Recommended approach |
|:---|:---|
| New relational system with public APIs | External UUIDv7/ULID + internal `BIGSERIAL` |
| Internal microservice with no public exposure | Auto-increment `BIGINT` is sufficient |
| Distributed database requiring independent ID generation | UUIDv7, ULID, or Snowflake externally; internal shard-local sequences if needed |
| Existing system using UUID PK with performance problems | Add a `BIGINT` surrogate PK and keep UUID as secondary unique key |

---

## Related

- [`sdi-06`](../system-design-interview/interview-roadmap.md#sdi-06-id-strategy--soft-deletes): Original interview-roadmap coverage of ID strategy and soft deletes.
- [`sdi-50`](../system-design-interview/system-design-review-plan.md#sdi-50-id-strategy--uuid-external-auto-increment-internal): Review-plan check that prompted this clarification.
- [`db-01: Random UUID Indexing`](query-performance.md#db-01-random-uuid-indexing): Why random UUIDs hurt B-tree performance and how to mitigate.
- **Dictionary**: [Databases](../../reference-dictionary/databases.md), [Data Architecture](../../reference-dictionary/data-architecture.md)
- **Taxonomy**: §4.0 Data Architecture Fundamentals, §4.1 Data Architecture
