---
type: System Design
title: "News Feed System — Key Takeaways"
description: "Hybrid fanout, timeline caches, celebrity problem, and CAP trade-offs in social-media feed design"
timestamp: 2026-06-20T00:00:00Z
---

# 42. News Feed System — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Question 2: Design a Social Media News Feed System](../system-design-cases/cases/part-2-news-feed-system-design.md)
> **Purpose**: Extract reusable architectural patterns from designing a social-media news feed at hundreds-of-millions-of-users scale.

> **Also see**: [URL Shortener — Key Takeaways](case-studies/url-shortener.md) — Cache-aside, CAP split, unique key generation
> **Dictionary**: [Caching](../../reference-dictionary/caching.md), [Messaging](../../reference-dictionary/messaging.md)
> **Taxonomy Reference**: §3 Integration & Communication Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [feed-01](#feed-01) | Fanning out 1B posts/day to 300 followers each creates 300× write amplification | Hybrid fanout: push for normal users, pull for celebrities |
| [feed-02](#feed-02) | Feed must load in < 200 ms with hundreds of followees | Pre-computed Redis timeline sorted sets |
| [feed-03](#feed-03) | Celebrity posts would overload millions of timelines | Celebrity cache + on-demand pull at read time |
| [feed-04](#feed-04) | Author must see their own post immediately; followers tolerate slight lag | CAP split: CP own-profile write, AP follower feed |
| [feed-05](#feed-05) | Regional deployment without cross-region feed latency | Regional Redis timelines + per-region fanout workers |

---

## feed-01: Hybrid Fanout to Control Write Amplification

> **Source**: [§"High‑Level Architecture"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | 1B posts/day × 300 average followers ≈ 300B timeline insertions; pure push is unsustainable |
| **Root cause** | A small number of celebrities with millions of followers dominate write amplification |

**Strategy**: Use a **hybrid fanout model**:
- **Fanout on write (push)** for normal users (≤ 10k followers): when they post, write the post ID into every follower's timeline cache.
- **Fanout on read (pull)** for celebrities (> 10k followers): store the post only in the celebrity's own posts list; followers pull recent celebrity posts at feed-load time.

| Model | Writes per post | Read cost | Best for |
|:---|:---|:---|:---|
| **Push all** | O(followers) | O(1) | Small, close friend graphs |
| **Pull all** | O(1) | O(followees) | Read-rare, compute-cheap scenarios |
| **Hybrid** | O(followers) for 99%, O(1) for 1% | O(1) + O(celebs followed) | Realistic social networks |

| Tradeoff | Detail |
|:---|:---|
| **Complexity** | Two code paths, celebrity threshold tuning, and separate celebrity cache |
| **Cost reduction** | Eliminates ~90% of total fanout work vs push-all |
| **Threshold** | 10k followers is a starting point; tune with production metrics |

> **Also see**: [Message Brokers & Async](messaging/message-brokers-async.md) — Fanout-on-write vs fanout-on-read
> **Dictionary**: [Fanout on Write](../../reference-dictionary/architecture-patterns.md#fanout-on-write), [Fanout on Read](../../reference-dictionary/architecture-patterns.md#fanout-on-read), [Hybrid Fanout](../../reference-dictionary/architecture-patterns.md#hybrid-fanout)
> **Azure**: [Azure Event Hubs](../../architecture-azure/integration/event-hubs/) for high-throughput fanout events, [Azure Cache for Redis](../../architecture-azure/data/redis/) for timeline storage
> **Taxonomy**: §3 Integration & Communication Architecture

---

## feed-02: Pre-Computed Timeline Cache for Fast Reads

> **Source**: [§"Timeline Cache (Redis Sorted Sets)"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | Loading a feed by querying every followee's posts at read time is O(followees) and too slow |
| **Root cause** | Scatter-gather across hundreds of user timelines in Cassandra creates unpredictable latency |

**Strategy**: Maintain a **pre-computed timeline** per user in Redis as a sorted set (`timeline:{user_id}`) where the score is the post creation timestamp. Insert new post IDs on fanout, trim to the latest 1000, and read with `ZREVRANGE` for reverse-chronological pagination.

| Aspect | Design choice |
|:---|:---|
| **Key** | `timeline:{user_id}` |
| **Structure** | Redis Sorted Set: `post_id` → `created_at` timestamp (ms) |
| **Trim policy** | `ZREMRANGEBYRANK` to keep last 1000 entries |
| **Expiry** | 30-day idle TTL for inactive users |

| Tradeoff | Detail |
|:---|:---|
| **Memory cost** | Billions of timelines require a large Redis cluster, but latency drops to < 5 ms |
| **Write amplification** | Paid during fanout so reads stay cheap |
| **Pagination** | Cursor-based pagination by timestamp avoids offset duplication on live feeds |

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Eviction, TTL
> **Dictionary**: [Timeline Cache](../../reference-dictionary/caching.md#timeline-cache)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/redis/)
> **Taxonomy**: §4.0.1 Database Performance & Caching

---

## feed-03: Isolating Celebrity Load

> **Source**: [§"Celebrity Post Cache (Redis List)"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | A celebrity post read by millions of followers simultaneously creates a hot partition and cache storm |
| **Root cause** | Pulling celebrity posts on every feed load concentrates read traffic on a few celebrity user IDs |

**Strategy**: Store the latest N posts of each celebrity in a **dedicated Redis cluster** (`celebrity_posts:{celebrity_id}`). Use `LPUSH` on new post and `LTRIM` to keep the list bounded. Followers merge their normal timeline with celebrity posts fetched from this cache at read time.

| Aspect | Design choice |
|:---|:---|
| **Key** | `celebrity_posts:{celebrity_id}` |
| **Structure** | Redis List of post IDs, max 100 entries |
| **Refresh** | Lazy on read miss or background pre-warm |
| **Isolation** | Separate cluster prevents celebrity traffic from starving normal timelines |

| Tradeoff | Detail |
|:---|:---|
| **Read path complexity** | Feed load must merge two data sources: timeline + celebrity posts |
| **Staleness** | Celebrity cache refreshes eventually; acceptable for non-author viewers |
| **Operational isolation** | Dedicated cluster allows independent scaling and blast-radius containment |

> **Also see**: [Caching Architecture](caching/caching-architecture.md) — Hot partitions
> **Dictionary**: [Celebrity Cache](../../reference-dictionary/caching.md#celebrity-cache)
> **Azure**: [Azure Cache for Redis](../../architecture-azure/data/redis/) Enterprise tier for clustered isolation
> **Taxonomy**: §7.2 Performance Architecture

---

## feed-04: Operation-Specific Consistency Model

> **Source**: [§"Consistency vs. Availability Trade‑offs"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | Followers tolerate a few seconds of feed lag, but authors must see their own posts instantly |
| **Root cause** | Different stakeholders have different consistency requirements and latency budgets |

**Strategy**: Apply **CP semantics for the author** and **AP semantics for followers**.
- Own profile/timeline: synchronous Cassandra write + write-through to author's timeline cache.
- Follower feeds: asynchronous Kafka fanout with eventual consistency (target < 2–3 s p99).

| Path | Consistency | Mechanism |
|:---|:---|:---|
| **Post creation / own profile** | CP | Synchronous DB write + write-through cache |
| **Follower feed** | AP | Kafka fanout → Redis timeline update |
| **Celebrity posts** | AP | Celebrity cache updated synchronously, pulled by followers |

| Tradeoff | Detail |
|:---|:---|
| **User experience** | Authors get immediate feedback; followers get near-real-time updates |
| **Availability** | Feed reads remain highly available because Redis has no cross-partition coordination |
| **Complexity** | Two consistency paths require clear observability and alerts on fanout lag |

> **Also see**: [Concurrency & Transactions](concurrency-transactions/concurrency-transactions.md) — Consistency models
> **Dictionary**: [CAP Theorem](../../reference-dictionary/data-architecture.md#cap-theorem), [Write-Through](../../reference-dictionary/caching.md#write-through)
> **Azure**: [Azure Cosmos DB](../../architecture-azure/data/databases/) consistency levels, [Azure Event Hubs](../../architecture-azure/integration/event-hubs/) for fanout
> **Taxonomy**: §4.0 Data Architecture Fundamentals

---

## feed-05: Regional Deployment Without Cross-Region Feed Latency

> **Source**: [§"Deployment / CI‑CD"](../../articles/medium/PART%202%20%E2%80%94%20Distinguished%20Engineer%20%E2%80%94%20System%20Design%20Interview%20Questions%20%28URL%20Shortener%20%26%20News%20Feed%20Systems%29.md)

| | |
|:---|:---|
| **Problem** | A globally distributed user base needs < 200 ms feed loads from every region |
| **Root cause** | Round-tripping across regions to fetch timelines adds unacceptable latency |

**Strategy**: Deploy **active-active stacks in multiple regions**. Each user timeline lives in the region where that user's profile resides. Fanout workers in each region consume from Kafka and update local timelines. Users are routed to their home region via geo-DNS.

| Choice | Tradeoff |
|:---|:---|
| **Regional timelines** | Low latency for normal case; user traveling may need timeline rebuild |
| **Global Redis** | Consistent everywhere but higher write/read latency |
| **Rebuild on region change** | Expensive but rare; acceptable for social media UX |

| Tradeoff | Detail |
|:---|:---|
| **Consistency per region** | Within a region, timeline reads are strongly consistent locally |
| **Cross-region fanout** | Avoided by regional fanout workers; reduces bandwidth |
| **Disaster recovery** | Cassandra multi-DC replication preserves post durability; timelines can be rebuilt |

> **Also see**: [Resilience Patterns](resilience/resilience-patterns.md) — Active-active, blast radius
> **Dictionary**: [Active-Active](../../reference-dictionary/architecture-patterns.md#active-active)
> **Azure**: [Azure Traffic Manager](../../architecture-azure/networking/) for geo-routing, [Azure Cosmos DB](../../architecture-azure/data/databases/) multi-region writes, [Azure Cache for Redis](../../architecture-azure/data/redis/) regional clusters
> **Taxonomy**: §5.1 Cloud Architecture

---

> **Related topics**: [URL Shortener — Key Takeaways](case-studies/url-shortener.md) — Cache-aside, CAP split, unique key generation
