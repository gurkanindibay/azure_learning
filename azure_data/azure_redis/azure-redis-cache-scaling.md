# Azure Cache for Redis - Scaling and Memory Options

## Overview

Azure Cache for Redis provides an in-memory data store based on Redis software. When your caching needs exceed the memory limits of a single Redis instance, Azure provides clustering capabilities to scale horizontally.

## Memory Limits by Tier

| Tier | Maximum Memory |
|------|---------------|
| Basic | Up to 53 GB |
| Standard | Up to 53 GB |
| Premium | Up to 120 GB (single instance) |
| Premium with Clustering | Up to 1.2 TB (10 shards × 120 GB) |
| Enterprise | Up to 100 GB per node |
| Enterprise Flash | Up to 1.5 TB per node |

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
