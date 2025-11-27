# Azure Cache for Redis - Scaling and Memory Options

## Overview

Azure Cache for Redis provides an in-memory data store based on Redis software. When your caching needs exceed the memory limits of a single Redis instance, Azure provides clustering capabilities to scale horizontally.

## Table of Contents

- [Memory Limits by Tier](#memory-limits-by-tier)
- [Pricing Factors](#pricing-factors)
- [Redis Cluster Feature](#redis-cluster-feature)
- [Alternative: Enterprise Tiers](#alternative-enterprise-tiers)
- [Azure Architecture Patterns for Caching](#azure-architecture-patterns-for-caching)
- [Best Practices for Large Caches](#best-practices-for-large-caches)
- [Common Misconceptions](#common-misconceptions)
- [Exam Tips (AZ-204)](#exam-tips-az-204)
- [References](#references)

## Memory Limits by Tier

| Tier | Maximum Memory |
|------|---------------|
| Basic | Up to 53 GB |
| Standard | Up to 53 GB |
| Premium | Up to 120 GB (single instance) |
| Premium with Clustering | Up to 1.2 TB (10 shards × 120 GB) |
| Enterprise | Up to 100 GB per node |
| Enterprise Flash | Up to 1.5 TB per node |

## Pricing Factors

Azure Cache for Redis pricing is based on three key factors:

| Factor | Description |
|--------|-------------|
| **Region** | Pricing varies by Azure region |
| **Pricing Tier** | Basic, Standard, Premium, Enterprise, or Enterprise Flash |
| **Hours** | Charged by the hour of usage |

### What Does NOT Affect Pricing

| Factor | Affects Cost? |
|--------|--------------|
| Consumed storage | ❌ No |
| Per transaction | ❌ No |
| Number of connections | ❌ No |

### Key Point

Redis Cache is charged **by the hour**, varies **by region**, and depends on the **tier** you choose. Unlike some other Azure services, you are not charged based on storage consumption or transaction counts.

**Reference:** [Azure Cache for Redis Pricing](https://azure.microsoft.com/en-us/pricing/details/cache/)

## Redis Cluster Feature

When you need more than 120 GB of memory cache on the Premium tier, the **Redis Cluster** feature is the solution.

### Key Points

- **Premium tier exclusive**: Clustering is only available on Premium tier
- **Up to 10 shards**: You can configure 1-10 shards in a cluster
- **Maximum 1.2 TB**: With 10 shards at 120 GB each, you get up to 1.2 TB of memory
- **Automatic data distribution**: Redis automatically distributes data across shards using hash slots
- **No application code changes**: The clustering is transparent to your application (when using cluster-aware clients)

### How to Scale with Clustering

1. **Enable Clustering**: When creating or scaling a Premium cache, enable the clustering option
2. **Add Shards**: Each shard adds another 120 GB of available memory
3. **Example**: To get 500 GB, implement Redis Cluster with at least 5 shards (5 × 120 GB = 600 GB)

### Shard Configuration Example

| Shards | Total Memory Available |
|--------|----------------------|
| 1 | 120 GB |
| 2 | 240 GB |
| 3 | 360 GB |
| 4 | 480 GB |
| 5 | 600 GB |
| 10 | 1.2 TB |

## Alternative: Enterprise Tiers

For even larger memory requirements or advanced features, consider:

### Enterprise Tier
- Higher availability with active geo-replication
- Redis modules support (RediSearch, RedisBloom, RedisTimeSeries)
- Up to 100 GB per node with clustering support

### Enterprise Flash Tier
- Uses a combination of RAM and NVMe flash storage
- Cost-effective for large datasets
- Up to 1.5 TB per node
- Ideal for datasets with varying access patterns

## Azure Architecture Patterns for Caching

### Cache-Aside Pattern

The **Cache-Aside pattern** is specifically designed to increase application performance using a cache service. It loads data on demand into a cache from a data store.

#### How It Works

```
┌─────────────────┐      1. Request Data      ┌─────────────────┐
│                 │ ──────────────────────────▶│                 │
│   Application   │                            │      Cache      │
│                 │ ◀──────────────────────────│    (Redis)      │
│                 │      2. Cache Hit/Miss     │                 │
└────────┬────────┘                            └─────────────────┘
         │                                              ▲
         │ 3. If Cache Miss,                           │
         │    Query Data Store                          │
         ▼                                              │
┌─────────────────┐                                    │
│                 │      4. Store in Cache             │
│   Data Store    │ ────────────────────────────────────┘
│   (Database)    │
│                 │
└─────────────────┘
```

#### Pattern Flow

1. **Check Cache First**: Application checks if the requested data exists in the cache
2. **Cache Hit**: If data is found, return it directly (fast path)
3. **Cache Miss**: If data is not found:
   - Query the underlying data store
   - Store the retrieved data in the cache
   - Return the data to the caller
4. **Data Invalidation**: When data changes, invalidate or update the cached entry

#### Benefits

| Benefit | Description |
|---------|-------------|
| **Improved Performance** | Reduces load on the data store by serving repeated requests from cache |
| **Reduced Latency** | In-memory access is significantly faster than database queries |
| **Data Consistency** | Helps maintain consistency between cache and data store |
| **On-Demand Loading** | Only caches data that is actually requested |

#### Code Example (C#)

```csharp
public async Task<Product> GetProductAsync(string productId)
{
    // 1. Try to get from cache
    var cachedProduct = await _cache.GetStringAsync(productId);
    
    if (cachedProduct != null)
    {
        // Cache hit - return cached data
        return JsonSerializer.Deserialize<Product>(cachedProduct);
    }
    
    // 2. Cache miss - get from database
    var product = await _database.Products.FindAsync(productId);
    
    if (product != null)
    {
        // 3. Store in cache for future requests
        await _cache.SetStringAsync(
            productId,
            JsonSerializer.Serialize(product),
            new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10)
            });
    }
    
    return product;
}
```

### Other Related Patterns

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| **Cache-Aside** | Load data on demand into cache | General caching for read-heavy workloads |
| **Sharding** | Distribute data across multiple databases | Horizontal scaling of data storage |
| **Static Content Hosting** | Serve static content from cloud storage | Offload static files from web servers |
| **Sidecar** | Deploy helper components alongside main app | Logging, monitoring, proxying |

### Practice Question: Azure Architecture Patterns

**Question:**

Which Azure Architecture pattern is specifically designed to increase application performance using a cache service?

**Options:**

A) Sharding pattern

B) Cache-aside pattern ✅

C) Static content hosting pattern

D) Sidecar pattern

---

**Correct Answer: B) Cache-aside pattern**

---

**Explanation:**

The **Cache-Aside pattern** is designed to load data on demand into a cache from a data store. This improves performance by serving repeated requests from the fast in-memory cache and also helps maintain consistency between data held in the cache and data in the underlying data store.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Sharding pattern** | ❌ Incorrect - Sharding is about distributing data across multiple databases/partitions for horizontal scaling, not specifically for caching |
| **B) Cache-aside pattern** | ✅ **Correct** - Specifically designed to improve performance by loading data on demand into a cache |
| **C) Static content hosting pattern** | ❌ Incorrect - This pattern is about deploying static content to cloud storage and serving it directly to clients, not about caching dynamic data |
| **D) Sidecar pattern** | ❌ Incorrect - Sidecar is about deploying helper components (like logging, monitoring) alongside your main application in a separate process |

**Reference:** [Cache-Aside pattern - Microsoft Docs](https://docs.microsoft.com/en-us/azure/architecture/patterns/cache-aside)

---

## Best Practices for Large Caches

1. **Evaluate your data model**: Ensure you're caching appropriately sized data
2. **Set TTL (Time-to-Live)**: Implement expiration policies to prevent unbounded growth
3. **Monitor memory usage**: Use Azure Monitor to track memory consumption
4. **Consider data eviction policies**: Configure appropriate eviction when memory is full
5. **Use clustering for horizontal scaling**: Preferred over managing multiple independent caches

## Common Misconceptions

❌ **Creating multiple Redis servers and manually sharding in your application** - While possible, this adds complexity and is not the recommended approach when Redis Cluster is available.

❌ **Auto-scaling feature for Redis nodes** - Azure Cache for Redis does not have automatic horizontal scaling. Shard count must be configured manually.

❌ **Using SQL Database instead** - Caching and persistent storage serve different purposes. Moving cached data to SQL defeats the purpose of in-memory caching.

## Exam Tips (AZ-204)

- Remember that **Redis Cluster supports up to 10 shards**
- Maximum memory with clustering: **1.2 TB** (10 × 120 GB)
- Clustering is a **Premium tier feature**
- Enterprise tiers offer additional features beyond just memory scaling

## References

- [Azure Cache for Redis pricing tiers](https://docs.microsoft.com/azure/azure-cache-for-redis/cache-overview#pricing)
- [How to configure clustering for Premium Azure Cache for Redis](https://docs.microsoft.com/azure/azure-cache-for-redis/cache-how-to-premium-clustering)
- [Best practices for Azure Cache for Redis](https://docs.microsoft.com/azure/azure-cache-for-redis/cache-best-practices)
