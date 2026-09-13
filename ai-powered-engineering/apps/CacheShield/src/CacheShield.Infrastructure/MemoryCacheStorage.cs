using System.Collections.Concurrent;
using CacheShield.Core;

namespace CacheShield.Infrastructure;

public class MemoryCacheStorage : ICacheStorage
{
    private readonly ConcurrentDictionary<string, object> _store = new(StringComparer.OrdinalIgnoreCase);

    public Task<CacheEntry<T>?> GetAsync<T>(string key, CancellationToken ct = default)
    {
        if (_store.TryGetValue(key, out var raw) && raw is CacheEntry<T> entry)
        {
            if (entry.IsExpired())
            {
                _store.TryRemove(key, out _);
                return Task.FromResult<CacheEntry<T>?>(null);
            }

            entry.AccessCount++;
            return Task.FromResult<CacheEntry<T>?>(entry);
        }

        return Task.FromResult<CacheEntry<T>?>(null);
    }

    public Task SetAsync<T>(string key, T value, TimeSpan? ttl = null, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(key))
        {
            throw new ArgumentException("Cache key cannot be null or whitespace.", nameof(key));
        }

        var entry = new CacheEntry<T>
        {
            Key = key,
            Value = value,
            ExpiresAtUtc = ttl.HasValue ? DateTime.UtcNow.Add(ttl.Value) : null
        };

        _store[key] = entry;
        return Task.CompletedTask;
    }

    public Task<bool> RemoveAsync(string key, CancellationToken ct = default)
    {
        return Task.FromResult(_store.TryRemove(key, out _));
    }

    public Task ClearAsync(CancellationToken ct = default)
    {
        _store.Clear();
        return Task.CompletedTask;
    }

    public Task<int> GetCountAsync(CancellationToken ct = default)
    {
        // Clean up any expired keys on count query
        foreach (var pair in _store)
        {
            if (pair.Value is CacheEntry<object> e && e.IsExpired())
            {
                _store.TryRemove(pair.Key, out _);
            }
        }

        return Task.FromResult(_store.Count);
    }
}