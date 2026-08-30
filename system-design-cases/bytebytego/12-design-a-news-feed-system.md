---
type: System Design Case
title: "Design A News Feed System"
description: "Design a high-scale social media news feed system (like Facebook or Twitter) featuring hybrid fan-out architecture (Push vs. Pull), multi-tier Redis caching, graph query decoupling, and high-throughput timeline aggregation."
tags: [system-design, distributed-systems, news-feed, fan-out, redis, social-graph, caching, scalability]
timestamp: 2026-08-22T00:00:00Z
---

# Design A News Feed System

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 12  
> **Topic**: Social News Feeds, Fan-Out on Write (Push) vs. Fan-Out on Read (Pull), Multi-Tier Timeline Caching

---

## 1. Understand the Problem and Establish Design Scope

A news feed system aggregates status updates, photos, videos, and activities from friends and followed entities into an interactive, constantly updating timeline (e.g., Facebook News Feed, Twitter Home Timeline, Instagram Feed).

```mermaid
flowchart LR
    subgraph Flow1["1. Feed Publishing (Write Path)"]
        AUTHOR["Author (Alice)"] -->|POST /v1/me/feed| PUB["Feed Publishing Service"]
        PUB -->|Fan-Out to Friends' Inboxes| INBOXES["Followers' Timeline Caches"]
    end

    subgraph Flow2["2. News Feed Retrieval (Read Path)"]
        FOLLOWER["Follower (Bob)"] -->|GET /v1/me/feed| READ["News Feed Service"]
        READ -->|Fetch Pre-Aggregated IDs| INBOXES
    end
```

---

### Interview Clarification & Scope

> **Candidate:** What are the primary features supported?  
> **Interviewer:** Users can **publish posts** (text and media) and **view a scrolling news feed** of their friends' posts in reverse chronological order.
>
> **Candidate:** What is the platform scale?  
> **Interviewer:** **10 Million Daily Active Users (DAU)**. An average user has $500$ friends, but celebrity users can have millions of followers.
>
> **Candidate:** What are the latency requirements?  
> **Interviewer:** Loading the news feed should be fast ($< 200\text{ ms}$).

---

### Requirements Summary

#### Functional Requirements
1. **Feed Publishing**: A user creates a post containing text, images, or videos.
2. **News Feed Retrieval**: A user fetches their personal feed populated by friends' recent posts.
3. **Sorting**: Strict reverse chronological ordering by post creation timestamp.

#### Non-Functional Requirements
- **Low Read Latency**: Feed rendering must complete in $< 200\text{ ms}$.
- **High Availability**: Temporary background worker delays must not disrupt feed reading.
- **Celebrity / Hotspot Defense**: System must handle users with millions of followers without cascading memory exhaustion.

---

## 2. Core Fan-Out Models Comparison

The core architectural decision in feed design is **how and when posts are distributed to followers' timeline inboxes**.

```mermaid
flowchart TD
    subgraph PushModel["1. Fan-Out on Write (Push Model)"]
        P_POST["User Publishes Post"] --> P_WORK["Fan-Out Worker"]
        P_WORK -->|Iterate all followers| P_IN1["Friend 1 Inbox Cache"]
        P_WORK -->|Iterate all followers| P_IN2["Friend 2 Inbox Cache"]
        P_WORK -->|Iterate all followers| P_INN["Friend N Inbox Cache"]
    end

    subgraph PullModel["2. Fan-Out on Read (Pull Model)"]
        R_USER["User Opens Feed"] --> R_SVC["Feed Aggregator"]
        R_SVC -->|Query friends' latest posts| R_DB1["Friend 1 Posts"]
        R_SVC -->|Query friends' latest posts| R_DB2["Friend 2 Posts"]
        R_SVC -->|Merge-sort N streams| R_SORT["Sorted Timeline"]
    end
```

### Trade-Off Comparison Matrix

| Dimension | Fan-Out on Write (Push) | Fan-Out on Read (Pull) | Hybrid Architecture (Recommended) |
|:---|:---|:---|:---|
| **Write Latency** | Slow (High write amplification for large follower counts) | **Instant ($O(1)$ database insert)** | Fast for 99.9% of users |
| **Read Latency** | **Ultra-Fast ($O(1)$ read from Redis list)** | Slow ($O(N)$ multi-table fetch & sort) | **Ultra-Fast ($< 50\text{ ms}$)** |
| **Celebrity Problem** | **Catastrophic** (1 tweet by a celebrity triggers 50M cache writes) | None | **Celebrity posts merged dynamically on read** |
| **Inactive Users** | Wastes memory pushing posts to dormant users | **Zero wasted compute** | Inactive user inboxes evicted via TTL |

---

### The Hybrid Fan-Out Strategy

```mermaid
flowchart TD
    NEW_POST["User Creates New Post"] --> CHECK{"Is Author a Celebrity / Hotspot?<br/>(e.g., > 100k Followers)"}
    
    CHECK -->|No: Standard User| PUSH["<b>Fan-Out on Write (Push)</b><br/>Inject post_id into all followers' Redis inboxes."]
    CHECK -->|Yes: Celebrity| PULL["<b>Fan-Out on Read (Pull)</b><br/>Save post to celebrity's outbox only.<br/>Do NOT fan-out."]
    
    READER["Follower Requests News Feed"] --> MERGE["Merge-Sort Engine"]
    MERGE --> GET_INBOX["1. Read pre-computed Redis Inbox (Standard friends)"]
    MERGE --> GET_CELEB["2. Fetch latest posts from followed Celebrities"]
    MERGE --> COMBINE["Combine, Rank & Return Top 20 Posts"]
```

---

## 3. High-Level Architecture & End-to-End Flows

```mermaid
flowchart TD
    subgraph Ingress["Client & Edge"]
        CLIENT["Web / Mobile Clients"] --> LB["Layer 7 Load Balancer"]
    end

    subgraph WebTier["Stateless Web Tier"]
        LB --> API["API Gateway"]
        API --> POST_SVC["Post Service"]
        API --> FEED_SVC["News Feed Service"]
    end

    subgraph AsyncTier["Async Processing & Fan-Out"]
        POST_SVC --> MQ["Fan-Out Message Queue (Kafka)"]
        MQ --> FANOUT_WORKERS["Fan-Out Worker Fleet"]
    end

    subgraph CacheTier["Multi-Tier Cache Storage"]
        FANOUT_WORKERS --> FEED_CACHE[("News Feed Cache<br/>(Redis: user_id -> List of post_ids)")]
        POST_SVC --> POST_CACHE[("Post Content Cache<br/>(Redis: post_id -> JSON)")]
        API --> GRAPH_CACHE[("Friendship Graph Cache<br/>(user_id -> List of friend_ids)")]
    end

    subgraph PersistentTier["Relational / Distributed DB"]
        POST_SVC --> DB_POST[("Post Database")]
        API --> DB_USER[("User & Graph DB")]
    end

    FEED_SVC <--> FEED_CACHE & POST_CACHE
```

---

### End-to-End Sequence Flows

#### 1. Feed Publishing Flow
```mermaid
sequenceDiagram
    autonumber
    actor Alice as Author (Alice)
    participant GW as API Gateway
    participant PS as Post Service
    participant MQ as Fan-Out Queue
    participant FW as Fan-Out Workers
    participant Cache as Redis Inboxes

    Alice->>GW: POST /v1/me/feed (content: "Hello World", media_ids: [...])
    GW->>PS: Save Post
    PS->>PS: Save to Post DB & Post Content Cache
    PS->>MQ: Publish "NewPostEvent (user: Alice, post_id: 101)"
    PS-->>Alice: 200 OK (Post Created)

    MQ->>FW: Consume NewPostEvent
    FW->>FW: Fetch Alice's friends from Graph Cache
    loop For Each Non-Celebrity Friend
        FW->>Cache: LPUSH feed:friend_id 101 (LTRIM 500)
    end
```

#### 2. News Feed Retrieval Flow
```mermaid
sequenceDiagram
    autonumber
    actor Bob as Follower (Bob)
    participant GW as API Gateway
    participant FS as News Feed Service
    participant FC as News Feed Cache
    participant PC as Post Content Cache
    participant CDN as CDN (Media Assets)

    Bob->>GW: GET /v1/me/feed?page=1&limit=20
    GW->>FS: Fetch Feed for Bob
    FS->>FC: LRANGE feed:bob 0 19 (Returns list of 20 post_ids)
    FS->>PC: MGET post:101, post:102, ... (Batch fetch post metadata)
    FS-->>GW: Rendered Feed JSON (Hydrated with author info & media URLs)
    GW-->>Bob: 200 OK
    Bob->>CDN: Fetch images/videos directly from Edge CDN
```

---

## 4. Multi-Tier Cache Architecture

To serve millions of requests with sub-50ms latency, data is partitioned into **specialized cache layers**:

```mermaid
classDiagram
    class NewsFeedCache {
        +user_id: Long
        +post_ids: List~Long~
        +LTRIM(user_id, 0, 500)
    }

    class PostContentCache {
        +post_id: Long
        +author_id: Long
        +content: String
        +media_urls: List~String~
        +created_at: Timestamp
    }

    class SocialGraphCache {
        +user_id: Long
        +friend_ids: Set~Long~
        +following_celebrity_ids: Set~Long~
    }

    class ActionCache {
        +post_id: Long
        +like_count: Integer
        +comment_count: Integer
    }
```

- **News Feed Cache**: Stores only lightweight arrays of `post_id`s (e.g., max 500 post IDs per user $\approx 4\text{ KB}$ per active user).
- **Post Content Cache**: Stores the actual text and media URLs, avoiding redundant storage in every friend's feed list.
- **Social Graph Cache**: Maintains friend relationships for fast follower list retrieval during fan-out.

---

## 5. Architectural Summary

```mermaid
mindmap
  root((News Feed System))
    Fan-Out Strategy
      Hybrid Push/Pull Model
      Push for normal users (fast reads)
      Pull on-demand for celebrities
    Cache Tiering
      News Feed Cache: List of post_ids
      Post Content Cache: Hydrated metadata
      Graph Cache: Friend relationships
    Scalability
      Kafka Message Queues buffer fan-out spikes
      Redis LTRIM keeps inboxes capped at 500 posts
      CDN delivers static photos and video chunks
```

| Subsystem | Architectural Decision | Core Rationale |
|:---|:---|:---|
| **Fan-Out Model** | Hybrid Push-Pull Model | Eliminates write amplification for celebrities while maintaining instant $O(1)$ feed reads for standard users. |
| **Feed Storage** | Redis `ZSET` / `LIST` (ID-only) | Drastically minimizes RAM usage by storing only 64-bit `post_id` pointers in user timelines. |
| **Decoupling** | Asynchronous Kafka Queue | Shields the API write path from slow fan-out operations to thousands of followers. |
| **Media Delivery** | Edge CDN (Cloudflare / CloudFront) | Prevents heavy video/photo downloads from hitting application web servers. |

---

## References

1. Serving Facebook Multifeed: Efficiency and Performance Gains: https://engineering.fb.com/
2. Scaling Twitter: Timelines at Scale: https://blog.twitter.com/engineering/en_us/topics/infrastructure/2013/timelines-at-scale
3. Redis Data Structures as a News Feed: https://redis.io/solutions/use-cases/
