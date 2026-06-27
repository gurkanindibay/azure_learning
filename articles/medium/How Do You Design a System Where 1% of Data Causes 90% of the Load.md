---
type: Article
title: "How Do You Design a System Where 1% of Data Causes 90% of the Load?"
source: "https://medium.com/@skilledcoder/how-do-you-design-a-system-where-1-of-data-causes-90-of-the-load-4412d508501f"
author:
  - "[[Skilled Coder]]"
published: 2026-04-12
created: 2026-06-27
description: "Taming Hot Keys, Celebrity Problems, and Skewed Workloads"
tags:
  - "clippings"
---
## Taming Hot Keys, Celebrity Problems, and Skewed Workloads

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-rWTBj4Na2gbCLt6hM_1RA.png)

> Read more such problems [**here**](https://theskilledcoder.com/system-design-problems-roadmap)

Your distributed cache handles 2 million requests per second. You’ve sharded it perfectly across 100 nodes — 20,000 requests per node. Everything works beautifully.

Then Taylor Swift tweets. That single cache key- `user:taylorswift` -gets 500,000 requests per second. One node is melting while the other 99 sit idle.

Your “perfect” distribution is worthless. One key brought down the whole system.

In almost every large-scale system, the data access pattern follows a power law: a tiny fraction of keys, users, or items attract the vast majority of traffic. Designing for the average case guarantees failure on the hot case.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*bShMYLnGdaLZHzejA7W8kw.png)

## Why Uniform Sharding Fails

Most distributed systems use some form of hash-based sharding: `shard = hash(key) % num_shards`. This distributes keys evenly but not load.

```c
# Seems fair: keys are evenly distributed
shard_0: [user:alice, user:bob, user:carol, ...]       # 20K keys
shard_1: [user:dave, user:eve, user:taylorswift, ...]   # 20K keys
shard_2: [user:frank, user:grace, user:henry, ...]      # 20K keys

# Reality: load is wildly uneven
shard_0: 20,000 req/s    # Normal
shard_1: 500,000 req/s   # taylorswift is here
shard_2: 18,000 req/s    # Normal
```

The problem isn’t how many keys each shard has. It’s how much traffic each key attracts. One celebrity, one viral post, one flash sale item can concentrate 25x the average load onto a single node.

## The Hot Spot Taxonomy

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*-Jx1N65MxW_lP4-plwyH-A.png)

## Principle 1: Replicate Hot Data

If one copy of a hot key can’t handle the load, make many copies.

### Read Replicas for Hot Keys

```c
# Single copy: one node handles all reads for taylorswift
cache.get("user:taylorswift")  # Always hits shard_1

# Replicated: spread reads across N copies
def get_hot_key(key):
    replica_id = random.randint(0, NUM_REPLICAS - 1)
    replica_key = f"{key}:replica:{replica_id}"

    result = cache.get(replica_key)
    if result:
        return result

    # Fallback to primary
    result = cache.get(key)
    return result

def set_hot_key(key, value):
    # Write to primary
    cache.set(key, value)
    # Fan out to all replicas
    for i in range(NUM_REPLICAS):
        cache.set(f"{key}:replica:{i}", value)
```

With 10 replicas, that 500K req/s celebrity key becomes 50K req/s per node perfectly manageable.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xngykQq4OS8M3EiY5zbEpQ.png)

> **The Write Amplification Trade-off**
> 
> Every write to a hot key must now update N replicas. For read-heavy hot keys (celebrity profiles, product pages), this is fine - reads outnumber writes 1000:1.
> 
> For write-heavy hot keys (counters, inventory), replication makes things worse. You need a different strategy (see Principle 3).

## Principle 2: Add a Local Cache Layer

Before any request hits the distributed cache or database, check a local in-process cache. Hot keys will naturally stay warm in every application instance.

```c
from functools import lru_cache
import time

# L1: In-process cache with short TTL
local_cache = {}  # key -> (value, expiry_time)

def get_with_local_cache(key, ttl_seconds=5):
    # L1: Check local cache first (microseconds)
    entry = local_cache.get(key)
    if entry and entry[1] > time.time():
        return entry[0]

    # L2: Check distributed cache (milliseconds)
    value = redis.get(key)
    if value:
        local_cache[key] = (value, time.time() + ttl_seconds)
        return value

    # L3: Database (tens of milliseconds)
    value = db.query(key)
    redis.setex(key, 300, value)
    local_cache[key] = (value, time.time() + ttl_seconds)
    return value
```

**Why This Works for Hot Keys**

If you have 50 application instances and a hot key has a 5-second local TTL:

- Without local cache: 500K req/s hit Redis
- With local cache: 50 instances × 1 miss every 5s = 10 req/s hit Redis

That’s a 50,000x reduction in downstream pressure. The hotter the key, the more effective local caching becomes.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Qm5tbarto9P6JYQsiNZxmg.png)

## Principle 3: Shard the Hot Key Itself

For write-heavy hot keys (counters, inventory), you can’t just replicate, you need to split the single key into many sub-keys and aggregate later.

**Example: Global Like Counter**

```c
# ❌ Single counter: all writes hit one key
redis.incr("post:viral:likes")  # 100K writes/sec on ONE node

# ✅ Sharded counter: spread writes across N sub-keys
NUM_COUNTER_SHARDS = 100

def increment_like(post_id):
    shard = random.randint(0, NUM_COUNTER_SHARDS - 1)
    redis.incr(f"post:{post_id}:likes:shard:{shard}")

def get_like_count(post_id):
    total = 0
    pipe = redis.pipeline()
    for shard in range(NUM_COUNTER_SHARDS):
        pipe.get(f"post:{post_id}:likes:shard:{shard}")
    results = pipe.execute()
    return sum(int(r or 0) for r in results)
```

100K writes/sec on one key becomes 1K writes/sec across 100 keys on potentially 100 different nodes.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*XPgS1eA84-PTEPJ2i2JAYw.png)

***When to Shard a Key***

*Shard the key when:*

- *Write-heavy: Counters, inventory, rate limiters where many writers contend*
- *Known hot: You can identify the hot key in advance (e.g., a flash sale product)*
- *Aggregation is acceptable: Reading requires summing shards, adding latency*

*Don’t shard when reads must be instant and atomic — use replication instead.*

## Principle 4: Detect and Adapt to Hot Spots

You can’t always predict which keys will be hot. A random tweet goes viral. An obscure product gets mentioned on TV. You need systems that detect hot spots and adapt automatically.

**Hot Key Detection**

```c
# Track access frequency in a streaming fashion
from collections import defaultdict
import time

class HotKeyDetector:
    def __init__(self, window_seconds=60, threshold=100):
        self.counts = defaultdict(int)
        self.window = window_seconds
        self.threshold = threshold
        self.last_reset = time.time()

    def record_access(self, key):
        # Reset window periodically
        if time.time() - self.last_reset > self.window:
            self.counts.clear()
            self.last_reset = time.time()

        self.counts[key] += 1

        if self.counts[key] == self.threshold:
            self.promote_to_hot(key)

    def promote_to_hot(self, key):
        # Automatically replicate this key
        value = cache.get(key)
        for i in range(NUM_REPLICAS):
            cache.set(f"{key}:replica:{i}", value, ttl=300)
        hot_key_registry.add(key)
```

**Adaptive Request Routing**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*45NInT2w5anjMGEDK5gmrQ.png)

## Principle 5: Isolate Hot Paths

Don’t let hot keys share infrastructure with normal keys. Give them their own dedicated resources so a spike in hot traffic can’t starve cold queries.

**Dedicated Hot-Key Tier**

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*HmbHnKj0whe-8hTSSMpWPg.png)

**Why Isolation Matters**

Without isolation, a viral tweet competes with normal cache reads for the same network bandwidth, CPU, and memory. The hot key’s traffic creates:

- Connection pool exhaustion for the hot shard
- Increased latency for all keys on the same node
- Cascading failures if the hot node goes down and traffic redistributes

With isolation, the hot tier can be scaled independently. Add more replicas, more memory, more bandwidth, without touching the normal tier.

## Real-World Patterns

### Case 1: Twitter’s Fan-Out Problem

When a celebrity with 50 million followers tweets, Twitter can’t fan-out the tweet to 50 million timelines in real-time. Instead:

- Normal users: Fan-out on write. When you tweet, push to all followers’ timelines.
- Celebrity users: Fan-out on read. Don’t pre-push. When a follower loads their timeline, merge the celebrity’s tweets at read time.

This hybrid approach means celebrity tweets don’t cause a write storm to millions of cache entries.

### Case 2: Database Hot Rows

A popular product’s page gets hammered. Every view increments a view counter. Every purchase decrements inventory. The database row becomes a bottleneck

### Case 3: CDN & Cache Stampede

When a popular cached item expires, hundreds of concurrent requests all miss the cache simultaneously and hit the origin server. This is the thundering herd or cache stampede problem.

## What’s Next?

This problem give rise to many follow ups

- How do you handle hot keys in a distributed database like DynamoDB or Cassandra?
- What if the hot key changes every few minutes (trending content)?
- How do you prevent thundering herd when the primary copy of a hot key fails?
- How do rate limiters handle hot keys?

We will dicuss in detail in upcoming posts

Or explore 100+ [**HLD**](https://theskilledcoder.com/system-design-problems-roadmap) **&** [**LLD**](https://theskilledcoder.com/lld-problems-roadmap) questions where similar scenarios are broken down in detail and much more content.