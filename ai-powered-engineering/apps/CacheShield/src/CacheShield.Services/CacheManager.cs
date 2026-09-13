using CacheShield.Core;

namespace CacheShield.Services;

public class CacheManager : ICacheManager
{
    private readonly ICacheStorage _storage;
    private long _hits;
    private long _misses;

    public CacheManager(ICacheStorage storage)
    {
        _storage = storage;
    }

    public async Task<T?> GetOrSetAsync<T>(string key, Func<Task<T>> factory, TimeSpan? ttl = null, CancellationToken ct = default)
    {
        var existing = await _storage.GetAsync<T>(key, ct);
        if (existing != null)
        {
            Interlocked.Increment(ref _hits);
            return existing.Value;
        }

        Interlocked.Increment(ref _misses);
        var freshValue = await factory();
        await _storage.SetAsync(key, freshValue, ttl, ct);
        return freshValue;
    }

    public async Task<CacheMetrics> GetMetricsAsync(CancellationToken ct = default)
    {
        var count = await _storage.GetCountAsync(ct);
        return new CacheMetrics
        {
            TotalItems = count,
            Hits = Interlocked.Read(ref _hits),
            Misses = Interlocked.Read(ref _misses)
        };
    }
}