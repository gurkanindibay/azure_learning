---
type: Article
title: "Elasticsearch Is Dead in 2026. Instacart Just Proved It"
source: "https://medium.com/@kanishks772/elasticsearch-is-dead-in-2026-instacart-just-proved-it-3d728dbf9a83"
author:
  - "[[The Latency Gambler]]"
published: 2026-08-16
generated: { by: process:okf-migrate, at: 2026-09-11T00:00:00Z }
description: "Why Instacart replaced Elasticsearch and FAISS with PostgreSQL (GIN indexes and pgvector) for write-heavy grocery catalog search and how relational normalization cut write workload by 10x."
tags:
  - clippings
  - databases
  - search
  - postgresql
  - elasticsearch
  - pgvector
---

# Elasticsearch Is Dead in 2026. Instacart Just Proved It

> **Author**: [The Latency Gambler](https://medium.com/@kanishks772)  
> **Published**: August 16, 2026  
> **Source**: [Medium](https://medium.com/@kanishks772/elasticsearch-is-dead-in-2026-instacart-just-proved-it-3d728dbf9a83)  
> **Domain**: Databases, Search Engines, Full-Text Indexing, Vector Search, Relational Modeling  
> **Related Takeaways**: [39. Search Architecture at Scale: Elasticsearch vs. PostgreSQL Relational Consolidation — Key Takeaways](../../system-design-architecture/databases/39-db-key-takeaways.md)

---

Instacart ripped Elasticsearch out of its search stack and replaced it with plain PostgreSQL. That alone is a notable engineering decision. What makes it worth studying isn’t the “Elasticsearch bad” headline it’s the specific, unglamorous reason a document-search engine lost to a relational database: write volume, not query complexity.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xQlNpvRBgVcyv7Ias2HNXw.png)

## The problem was never search quality

Instacart’s catalog spans billions of items across thousands of retailers, and grocery inventory is about as write-heavy as data gets prices, stock, and discounts change constantly throughout the day. Elasticsearch’s document model is denormalized by design, which is great for read-heavy workloads but means even a small update, like one item’s price, can require rewriting and re-indexing the entire document it lives in. At Instacart’s scale, that indexing load grew so heavy that the cluster struggled to keep up, and fixing bad data that slipped through could take days to correct. Layering in richer ML-driven ranking features only added to the indexing burden and dragged read performance down with it.

```text
Elasticsearch: denormalized documents       PostgreSQL: normalized tables

price changes on one item                    price changes on one item
        │                                             │
        ▼                                             ▼
 rewrite/re-index the entire                   single UPDATE to one row
 product document                              in one table
        │                                             │
        ▼                                             ▼
 indexing load grows with                      unrelated product attributes
 every unrelated field                         stay untouched
```

## The move, and the actual numbers behind it

Instacart shifted full-text search onto sharded, heavily normalized Postgres instances, using GIN indexes and a customized ranking function for text matching. Because product attributes and ML feature data now lived in separate, joinable tables instead of one bloated document, the normalized model alone cut write workload by roughly 10x compared to the old denormalized approach.

The bigger structural change was architectural, not just relational: Instacart pushed computation down to where the data lived, instead of pulling data up into the application layer to be joined and filtered there. Combined with running Postgres on NVMe storage, that shift alone made search roughly twice as fast.

```sql
-- Old shape: fetch broadly, join and filter in the application layer
results = elasticsearch.search(query)
availability = availability_service.get(results.ids)
final = app_layer_join_and_filter(results, availability)

-- New shape: push the join and filter into the database itself
SELECT p.*, ts_rank(p.search_vector, query) AS rank
FROM products p
JOIN inventory i ON i.product_id = p.id
WHERE i.available = true AND p.search_vector @@ query
ORDER BY rank DESC;
```

## Semantic search hit the same wall, for different reasons

Full-text search wasn’t the only piece. Instacart had also bolted on a separate vector search service using FAISS for semantic queries like “healthy foods,” with results merged into the final list at the application layer. That setup came with its own tax: FAISS couldn’t filter by attributes at query time, so it had to overfetch and filter afterward, sometimes dropping relevant results in the process. It also needed a separate approximate-nearest-neighbor index for every retailer hundreds of indexes to maintain and running two systems side by side meant a constant risk of them drifting out of sync.

The fix mirrored the first one: consolidate into the database already handling everything else, using pgvector instead of a standalone vector store. This is the part worth being honest about, because it wasn’t a clean sweep Instacart’s own benchmarking found pgvector was marginally slower than FAISS on raw lookup speed for its largest retailers. What it won on instead was recall quality, the ability to filter by live inventory and attributes in the same query, and no longer maintaining two systems that had to agree with each other.

## What actually improved, and what it means

In production testing, the consolidated system cut zero-result searches by 6% through better recall, which translated into a real, measurable revenue gain from shoppers finding what they were looking for instead of hitting dead ends.

None of this makes Elasticsearch a bad piece of technology it remains a strong default for plenty of read-heavy and log-analytics workloads it was built for. What Instacart’s case actually demonstrates is narrower and more useful than “Elasticsearch is dead”: when a workload is write-heavy, already running on a relational database you trust operationally, and needs search results joined tightly against live, fast-changing data, a specialized search engine’s core selling point flexible, document-level indexing can quietly become its most expensive liability. Consolidating onto the database already doing everything else won, not because Postgres is a better search engine in the abstract, but because it was the right engine for exactly this shape of problem.
