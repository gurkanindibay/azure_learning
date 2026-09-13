using CacheShield.Core;
using CacheShield.Infrastructure;
using Xunit;

namespace CacheShield.Tests;

public class MemoryCacheStorageTests
{
    [Fact]
    public async Task SetAndGetAsync_ReturnsValidEntry()
    {
        var storage = new MemoryCacheStorage();
        await storage.SetAsync("k1", "Hello World");

        var result = await storage.GetAsync<string>("k1");

        Assert.NotNull(result);
        Assert.Equal("Hello World", result.Value);
        Assert.Equal(1, result.AccessCount);
    }

    [Fact]
    public async Task GetAsync_ExpiredEntry_ReturnsNullAndEvicts()
    {
        var storage = new MemoryCacheStorage();
        // Set with negative TTL so it is immediately expired
        await storage.SetAsync("expired", 123, TimeSpan.FromMilliseconds(-100));

        var result = await storage.GetAsync<int>("expired");

        Assert.Null(result);
    }

    [Fact]
    public async Task RemoveAsync_RemovesKeyFromStorage()
    {
        var storage = new MemoryCacheStorage();
        await storage.SetAsync("del", 456);

        var removed = await storage.RemoveAsync("del");
        var result = await storage.GetAsync<int>("del");

        Assert.True(removed);
        Assert.Null(result);
    }
}