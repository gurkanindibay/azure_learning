using CacheShield.Core;
using CacheShield.Infrastructure;
using CacheShield.Services;
using Xunit;

namespace CacheShield.Tests;

public class CacheManagerTests
{
    [Fact]
    public async Task GetOrSetAsync_CalculatesHitsAndMisses()
    {
        var storage = new MemoryCacheStorage();
        var manager = new CacheManager(storage);

        // First call: Miss
        var v1 = await manager.GetOrSetAsync("item1", () => Task.FromResult("Value 1"));
        Assert.Equal("Value 1", v1);

        // Second call: Hit
        var v2 = await manager.GetOrSetAsync("item1", () => Task.FromResult("New Computed"));
        Assert.Equal("Value 1", v2); // Retained cached value

        var metrics = await manager.GetMetricsAsync();
        Assert.Equal(1, metrics.Hits);
        Assert.Equal(1, metrics.Misses);
        Assert.Equal(0.5, metrics.HitRatio, precision: 2);
    }
}