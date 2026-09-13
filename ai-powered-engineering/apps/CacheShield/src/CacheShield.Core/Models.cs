namespace CacheShield.Core;

public enum CacheTier
{
    Memory,
    File,
    Distributed
}

public class CacheEntry<T>
{
    public string Key { get; set; } = string.Empty;
    public T? Value { get; set; }
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
    public DateTime? ExpiresAtUtc { get; set; }
    public int AccessCount { get; set; } = 0;
    public CacheTier Tier { get; set; } = CacheTier.Memory;

    public bool IsExpired()
    {
        return ExpiresAtUtc.HasValue && DateTime.UtcNow > ExpiresAtUtc.Value;
    }
}

public class CacheMetrics
{
    public int TotalItems { get; set; }
    public long Hits { get; set; }
    public long Misses { get; set; }
    public double HitRatio => (Hits + Misses) > 0 ? (double)Hits / (Hits + Misses) : 0.0;
}

public interface ICacheStorage
{
    Task<CacheEntry<T>?> GetAsync<T>(string key, CancellationToken ct = default);
    Task SetAsync<T>(string key, T value, TimeSpan? ttl = null, CancellationToken ct = default);
    Task<bool> RemoveAsync(string key, CancellationToken ct = default);
    Task ClearAsync(CancellationToken ct = default);
    Task<int> GetCountAsync(CancellationToken ct = default);
}

public interface ICacheManager
{
    Task<T?> GetOrSetAsync<T>(string key, Func<Task<T>> factory, TimeSpan? ttl = null, CancellationToken ct = default);
    Task<CacheMetrics> GetMetricsAsync(CancellationToken ct = default);
}