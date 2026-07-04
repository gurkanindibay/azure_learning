---
type: Article
title: "HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory"
source: "https://blog.stackademic.com/hyperloglog-the-algorithm-that-counts-billions-with-just-12-kb-of-memory-8e346a9916c6"
author: "Anurag Goel"
published: 2026-06-27
created: 2026-07-03
description: "HyperLogLog is a probabilistic algorithm that estimates the number of unique items in a massive dataset using a tiny fraction of the memory a traditional approach would require — with less than 2% error. Used by Redis, Google Analytics, and Mixpanel."
tags:
  - "algorithms"
  - "databases"
  - "redis"
  - "cardinality-estimation"
  - "probabilistic-data-structures"
---

# HyperLogLog: The Algorithm That Counts Billions with Just 12 KB of Memory

> **Source**: [Stackademic](https://blog.stackademic.com/hyperloglog-the-algorithm-that-counts-billions-with-just-12-kb-of-memory-8e346a9916c6)
> **Author**: Anurag Goel
> **Published**: 2026-06-27
>
> **TL;DR:** HyperLogLog is a probabilistic algorithm that estimates the number of unique items in a massive dataset using a tiny fraction of the memory a traditional approach would require — with less than 2% error. Used by Redis, Google Analytics, and Mixpanel, it's one of the most elegant engineering solutions in Big Data.

---

## Table of Contents

1. [The Problem: Counting Unique Things at Scale](#the-problem-counting-unique-things-at-scale)
2. [The Intuition: Finger Counting with Probability](#the-intuition-finger-counting-with-probability)
3. [Evolution of the Algorithm](#evolution-of-the-algorithm)
   - Flajolet-Martin
   - LogLog
   - SuperLogLog
   - HyperLogLog
4. [How HyperLogLog Works (Step by Step)](#how-hyperloglog-works-step-by-step)
5. [Go Implementation with Redis](#go-implementation-with-redis)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Pros and Cons](#pros-and-cons)
8. [When Should You Use HyperLogLog?](#when-should-you-use-hyperloglog)
9. [Conclusion](#conclusion)

---

## The Problem: Counting Unique Things at Scale

Imagine you run a streaming platform with 500 million users. Every day, your product manager asks: **"How many unique users played this song today?"**

Simple question. Brutally expensive answer — if you do it naively.

The traditional database approach would look something like this:

```sql
SELECT COUNT(DISTINCT user_id)
FROM play_events
WHERE song_id = 'xyz'
  AND played_at >= CURRENT_DATE;
```

This works fine when you have thousands of records. But at hundreds of millions of events per day, this query:

- **Scans billions of rows**
- **Consumes gigabytes of RAM** (to maintain the set of unique user IDs seen so far)
- **Slows down under concurrent load**
- **Becomes prohibitively expensive** to run in real-time

The core challenge is that to count *unique* items exactly, you need to *remember every item you've ever seen*. As your data scales, so does your memory requirement — linearly.

This is the problem HyperLogLog was designed to solve.

---

## The Intuition: Finger Counting with Probability

Before diving into the algorithm, let's build intuition with a thought experiment.

Suppose you're counting unique visitors at a large exhibition. Instead of writing down every name or phone number, you ask each visitor for the **last 6 digits of their phone number** and observe something unusual about those digits.

You notice:

- How likely is it that a random 6-digit number has **no trailing zeros**? Very likely — roughly 9/10 numbers.
- How likely is a number to end in **at least one zero**? About 1/10.
- At least **two zeros**? About 1/100.
- At least **three zeros**? About 1/1000.

So if the *longest trailing zero sequence* you've seen is **3**, it's statistically likely you've seen around **1,000 people**.

This is the core insight:

> **The maximum number of leading zeros observed in a set of hashed values is a probabilistic estimator of how many unique values have been seen.**

You don't need to store every number. You only need to track **one integer** — the maximum run of leading zeros. That's your "finger count."

---

## Evolution of the Algorithm

HyperLogLog didn't appear overnight. It's the culmination of three progressive improvements, each fixing a flaw in the previous version.

### 1. Flajolet-Martin Algorithm (1985)

The original paper introduced the leading-zeros idea. Every input element is:

1. Hashed into a **binary string** using a hash function (to ensure uniform distribution)
2. The number of **leading zeros** is counted
3. The **maximum** leading-zero count `L` is tracked

**Cardinality Estimate:**

```
Cardinality ≈ 2^L / 0.77351
```

The `0.77351` is a correction factor derived mathematically to reduce bias.

**The flaw:** A single unlucky hash value with many leading zeros can wildly skew the estimate upward. One bad apple spoils the whole barrel.

### 2. LogLog (2003)

Durand and Flajolet fixed the single-hash bias by introducing **multiple independent estimates**.

**Approach:** Use `M` separate hash functions (or equivalently, split one hash into `M` buckets using the first few bits). Compute `L` for each bucket independently, then take the **geometric mean**.

**Cardinality Estimate:**

```
Cardinality ≈ α_M × M × 2^(average of all L values)
```

Where `α_M` is a bucket-count-specific correction factor.

**Standard Error:** `1.3 / √M`

With 1024 buckets, that's roughly **4% error** — a massive improvement.

**The flaw:** Geometric mean is still sensitive to outlier buckets with abnormally high `L` values.

### 3. SuperLogLog (2007)

The fix? **Throw away the outliers.**

SuperLogLog discards the top 30% of `L` values across buckets and computes the mean using only the remaining 70%.

**Standard Error:** `1.05 / √M`

**The flaw:** You now need to store and sort *all* bucket values to identify and remove the top 30% — which partially defeats the memory-efficiency purpose.

### 4. HyperLogLog — The Final Form (2007)

Flajolet et al. realized there's a mathematically elegant solution that doesn't require discarding values at all: **use the harmonic mean instead of the geometric mean**.

The harmonic mean ($n / \sum(1/x_i)$) naturally gives less weight to large outliers. No sorting. No discarding. Just a smarter average.

**Standard Error:** `1.04 / √M`

This is the version used in production systems today.

---

## How HyperLogLog Works (Step by Step)

Here's the complete algorithm in plain English:

1. Choose `M` buckets (`M` is usually a power of 2, e.g., 1024 or 2048)
2. For each incoming element:
   - Hash it to a uniform binary string
   - Use the first $\log_2(M)$ bits to determine the bucket index
   - Count the leading zeros in the remaining bits
   - Update the bucket's stored value if this count is higher
3. To estimate cardinality:
   - Compute $2^{\text{bucket\_value}}$ for each bucket
   - Take the harmonic mean across all buckets
   - Multiply by $\alpha_M \times M^2$
   - Apply small/large range corrections if needed

**Visual Representation:**

```
Input: "user_12345"
         ↓
    Hash Function
         ↓
Binary: 00101101 11001010 01110110 ...
         ↓
First 10 bits → Bucket Index: 5
Remaining bits: 11001010 01110110 ...
Leading zeros in remaining: 0
         ↓
Bucket[5] = max(Bucket[5], 0+1) = 1
```

After processing millions of users, each bucket holds a small integer. The harmonic mean of $2^{\text{bucket\_value}}$ across all buckets gives your cardinality estimate.

---

## Go Implementation with Redis

Redis natively supports HyperLogLog via three commands:

- `PFADD` — add elements
- `PFCOUNT` — get estimated count
- `PFMERGE` — merge multiple HLL counters

Redis uses up to **12 KB of memory** per HLL structure and supports up to **$2^{64}$ unique elements** with a standard error of **0.81%**.

### Basic Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    "github.com/redis/go-redis/v9"
)

func main() {
    ctx := context.Background()
    rdb := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    defer rdb.Close()

    // Add unique visitors to today's page view counter
    err := rdb.PFAdd(ctx, "visitors:homepage:2024-01-15",
        "user_001", "user_002", "user_003", "user_001", // user_001 visits twice
    ).Err()
    if err != nil {
        log.Fatal(err)
    }

    // Get approximate unique visitor count
    count, err := rdb.PFCount(ctx, "visitors:homepage:2024-01-15").Result()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Unique visitors today: ~%d\n", count)
    // Output: Unique visitors today: ~3 (not 4, because user_001 is deduplicated)
}
```

### Funnel Analytics with HyperLogLog

A powerful real-world pattern: track how many unique users pass through each stage of your conversion funnel.

```go
package main

import (
    "context"
    "fmt"
    "log"
    "github.com/redis/go-redis/v9"
)

type FunnelTracker struct {
    rdb  *redis.Client
    ctx  context.Context
    date string
}

func NewFunnelTracker(rdb *redis.Client, date string) *FunnelTracker {
    return &FunnelTracker{
        rdb:  rdb,
        ctx:  context.Background(),
        date: date,
    }
}

// TrackStep records a user reaching a specific funnel step
func (f *FunnelTracker) TrackStep(step string, userID string) error {
    key := fmt.Sprintf("funnel:%s:%s", step, f.date)
    return f.rdb.PFAdd(f.ctx, key, userID).Err()
}

// GetStepCount returns approximate unique users at a funnel step
func (f *FunnelTracker) GetStepCount(step string) (int64, error) {
    key := fmt.Sprintf("funnel:%s:%s", step, f.date)
    return f.rdb.PFCount(f.ctx, key).Result()
}

// GetFunnelReport returns counts for all steps in sequence
func (f *FunnelTracker) GetFunnelReport(steps []string) (map[string]int64, error) {
    report := make(map[string]int64)
    for _, step := range steps {
        count, err := f.GetStepCount(step)
        if err != nil {
            return nil, fmt.Errorf("error getting count for step %s: %w", step, err)
        }
        report[step] = count
    }
    return report, nil
}

func main() {
    rdb := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    defer rdb.Close()

    tracker := NewFunnelTracker(rdb, "2024-01-15")

    // Simulate users moving through a purchase funnel
    funnelEvents := []struct {
        step   string
        userID string
    }{
        {"homepage", "u1"}, {"homepage", "u2"}, {"homepage", "u3"},
        {"homepage", "u4"}, {"homepage", "u5"},
        {"product_page", "u1"}, {"product_page", "u2"}, {"product_page", "u3"},
        {"add_to_cart", "u1"}, {"add_to_cart", "u2"},
        {"checkout", "u1"},
        {"purchase", "u1"},
    }

    for _, event := range funnelEvents {
        if err := tracker.TrackStep(event.step, event.userID); err != nil {
            log.Printf("Error tracking event: %v", err)
        }
    }

    // Generate funnel report
    steps := []string{"homepage", "product_page", "add_to_cart", "checkout", "purchase"}
    report, err := tracker.GetFunnelReport(steps)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println("\n=== Conversion Funnel Report ===")
    fmt.Printf("%-20s %10s %15s\n", "Step", "Users", "Drop-off")
    prevCount := int64(0)
    for i, step := range steps {
        count := report[step]
        dropoff := ""
        if i > 0 && prevCount > 0 {
            dropoffPct := float64(prevCount-count) / float64(prevCount) * 100
            dropoff = fmt.Sprintf("%.1f%%", dropoffPct)
        }
        fmt.Printf("%-20s %10d %15s\n", step, count, dropoff)
        prevCount = count
    }
}
```

**Sample Output:**

```
=== Conversion Funnel Report ===
Step                      Users         Drop-off
homepage                      5                
product_page                  3           40.0%
add_to_cart                   2           33.3%
checkout                      1           50.0%
purchase                      1            0.0%
```

### Merging HLL Counters Across Time Windows

```go
package main

import (
    "context"
    "fmt"
    "log"
    "github.com/redis/go-redis/v9"
)

// MergeWeeklyVisitors combines 7 daily HLL counters into a weekly total
// This is far more memory-efficient than storing all user IDs for 7 days
func MergeWeeklyVisitors(rdb *redis.Client, dates []string, page string) (int64, error) {
    ctx := context.Background()

    // Build source keys for each day
    sourceKeys := make([]string, len(dates))
    for i, date := range dates {
        sourceKeys[i] = fmt.Sprintf("visitors:%s:%s", page, date)
    }

    // Merge all daily counters into a weekly counter
    weeklyKey := fmt.Sprintf("visitors:%s:weekly", page)
    err := rdb.PFMerge(ctx, weeklyKey, sourceKeys...).Err()
    if err != nil {
        return 0, fmt.Errorf("failed to merge HLL counters: %w", err)
    }

    // Get the weekly unique visitor count
    count, err := rdb.PFCount(ctx, weeklyKey).Result()
    if err != nil {
        return 0, fmt.Errorf("failed to count merged HLL: %w", err)
    }
    return count, nil
}

func main() {
    rdb := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })
    defer rdb.Close()

    ctx := context.Background()

    // Simulate a week of daily visitor data
    days := []struct {
        date  string
        users []string
    }{
        {"2024-01-09", []string{"u1", "u2", "u3", "u4"}},
        {"2024-01-10", []string{"u2", "u5", "u6"}},         // u2 returns
        {"2024-01-11", []string{"u1", "u7", "u8", "u9"}},   // u1 returns
        {"2024-01-12", []string{"u10", "u11"}},
        {"2024-01-13", []string{"u3", "u12", "u13", "u14"}}, // u3 returns
        {"2024-01-14", []string{"u15", "u16"}},
        {"2024-01-15", []string{"u1", "u2", "u17"}},        // u1, u2 return
    }

    dates := make([]string, len(days))
    for i, day := range days {
        dates[i] = day.date
        key := fmt.Sprintf("visitors:homepage:%s", day.date)
        ifaceUsers := make([]interface{}, len(day.users))
        for j, u := range day.users {
            ifaceUsers[j] = u
        }
        rdb.PFAdd(ctx, key, ifaceUsers...)
    }

    weeklyUnique, err := MergeWeeklyVisitors(rdb, dates, "homepage")
    if err != nil {
        log.Fatal(err)
    }

    // The merge automatically deduplicates returning users across days!
    fmt.Printf("Weekly unique visitors (with deduplication): ~%d\n", weeklyUnique)
    // Even though u1, u2, u3 appeared on multiple days,
    // they are counted only ONCE in the weekly total
}
```

### Pure Go HyperLogLog (Without Redis)

If you want an in-process HLL without a Redis dependency:

```go
package main

import (
    "fmt"
    "strconv"
    "github.com/axiomhq/hyperloglog"
)

func main() {
    hll := hyperloglog.New16() // 16-bit precision (~0.5% error)

    // Simulate adding 1 million user IDs with ~20% being duplicates
    fmt.Println("Adding 1,000,000 events (800k unique users)...")

    for i := 0; i < 800_000; i++ {
        userID := "user_" + strconv.Itoa(i)
        hll.Insert([]byte(userID))
    }

    // Simulate 200,000 repeat visits from the first 200,000 users
    for i := 0; i < 200_000; i++ {
        userID := "user_" + strconv.Itoa(i)
        hll.Insert([]byte(userID))
    }

    estimate := hll.Estimate()
    actual := uint64(800_000)
    errorPct := float64(int64(estimate)-int64(actual)) / float64(actual) * 100

    fmt.Printf("Actual unique users:    %d\n", actual)
    fmt.Printf("HLL estimate:           %d\n", estimate)
    fmt.Printf("Error:                  %.2f%%\n", errorPct)

    // Serialize to bytes for storage (extremely compact!)
    data, _ := hll.MarshalBinary()
    fmt.Printf("HLL size in memory:     %d bytes\n", len(data))
}
```

**Sample Output:**

```
Adding 1,000,000 events (800k unique users)...
Actual unique users:    800000
HLL estimate:           801243
Error:                  0.16%
HLL size in memory:     49160 bytes (~48 KB)
```

Compare that to storing 800,000 user IDs as strings (~6–8 MB minimum). **HLL achieves 99.84% accuracy at 0.6% of the memory cost.**

---

## Real-World Use Cases

### 1. Unique Visitor Counting (Analytics Platforms)

Google Analytics, Mixpanel, and Amplitude use HyperLogLog internally for their "unique users" metric. When you see "1.2M unique monthly active users" in your dashboard, that number was almost certainly computed with HLL.

### 2. Social Media View Counts

YouTube, Spotify, and TikTok display view/play counts that must be deduplicated in real time. Storing every user-video interaction pair at scale is impractical; HLL provides a near-instantaneous estimate.

### 3. Network Monitoring & DDoS Detection

Load balancers and firewalls use HLL to count unique IP addresses hitting an endpoint. A sudden spike in the unique IP estimate can trigger DDoS mitigation — all tracked with minimal overhead.

### 4. Database Query Optimization

PostgreSQL uses HLL internally for the query planner to estimate `COUNT(DISTINCT ...)` — helping it choose optimal join strategies without a full table scan.

### 5. E-commerce Funnel Analysis

As shown in the code above, separate HLL counters per funnel step provide real-time insight into where users drop off — without maintaining a full user-event table in fast storage.

---

## Pros and Cons

### ✅ Pros

| Benefit | Detail |
|:---|:---|
| **Tiny memory footprint** | Redis uses ≤12 KB regardless of dataset size |
| **Sub-linear time complexity** | O(1) per insert, O(M) to estimate |
| **Mergeable** | HLL counters can be combined without losing accuracy |
| **Built-in to major systems** | Redis, Cassandra, PostgreSQL all support it natively |
| **Streaming-friendly** | Works on infinite data streams — no need to buffer |

### ❌ Cons

| Limitation | Detail |
|:---|:---|
| **Approximate only** | ~1–2% error — unsuitable for billing, legal counts |
| **Not enumerable** | You can't retrieve which elements were added |
| **Hash function dependent** | Poor hash functions destroy accuracy |
| **Small sets are less accurate** | Below ~100 elements, error can be higher |

---

## When Should You Use HyperLogLog?

**Use HLL when:**

- You need approximate unique counts over large datasets
- Memory efficiency is critical
- Real-time or near-real-time results are required
- 1–2% error is acceptable (analytics, dashboards, monitoring)
- You need to merge counts across time windows or dimensions

**Don't use HLL when:**

- You need an exact count (billing, voting, legal compliance)
- Your dataset is small enough to count exactly in memory
- You need to enumerate or retrieve the actual unique elements
- Your error tolerance is below 0.5%

A useful mental model: **HLL is the analytics tool, not the ledger.** It tells you roughly how many. If you need to know *exactly* how many, use a proper counting structure.

---

## Conclusion

HyperLogLog is one of those rare algorithms that feels almost magical once you understand it. The journey from Flajolet-Martin's leading-zero observation to the harmonic mean optimization is a beautiful example of how mathematical insight can replace brute-force computation.

To recap the key ideas:

- **The core trick:** The maximum run of leading zeros in hashed values is a probabilistic estimator of unique count
- **The key fix:** Using harmonic mean across multiple buckets eliminates outlier bias elegantly
- **The practical result:** Counting billions of unique items in ~12 KB of RAM with <1% error

Whether you're building an analytics dashboard, a real-time monitoring system, or a recommendation engine, HyperLogLog is a tool worth having in your engineering toolkit.

---

## Further Reading

- [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) — Original paper by Flajolet et al.
- [Redis HyperLogLog Documentation](https://redis.io/docs/data-types/probabilistic/hyperloglogs/)
- [HyperLogLog in Practice (Google)](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/) — Google's engineering improvements

> **Related Dictionary Terms**: [HyperLogLog](../../reference-dictionary/databases.md#hyperloglog), [Cardinality Estimation](../../reference-dictionary/databases.md#cardinality-estimation), [Bloom Filter](../../reference-dictionary/databases.md#bloom-filter)
> **Takeaways**: [Redis Internals — Key Takeaways](../../system-design-architecture/caching/redis-internals.md)
