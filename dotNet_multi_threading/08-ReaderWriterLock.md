# ReaderWriterLockSlim

Optimizes scenarios with many readers and few writers. Allows multiple concurrent readers but exclusive writer access.

## Table of Contents
- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Lock Types](#lock-types)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

ReaderWriterLockSlim is designed for scenarios where data is read frequently but written infrequently. It allows multiple threads to read concurrently while ensuring exclusive access for writes.

**Key Concepts:**
- **Read Lock**: Multiple threads can hold simultaneously
- **Write Lock**: Exclusive access, blocks all readers and writers
- **Upgradeable Read Lock**: Can upgrade to write lock atomically
- **Performance**: Better than lock() for read-heavy scenarios

---

## Basic Usage

### Simple Read/Write

```csharp
public class CachedDataStore
{
    private readonly Dictionary<string, string> _cache = new Dictionary<string, string>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    public string Read(string key)
    {
        _lock.EnterReadLock();
        try
        {
            return _cache.TryGetValue(key, out string value) ? value : null;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void Write(string key, string value)
    {
        _lock.EnterWriteLock();
        try
        {
            _cache[key] = value;
            Console.WriteLine($"Written: {key} = {value}");
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public void Dispose()
    {
        _lock?.Dispose();
    }
}

// Usage: Multiple readers, occasional writer
var store = new CachedDataStore();

// Writer task
var writerTask = Task.Run(() =>
{
    for (int i = 0; i < 5; i++)
    {
        store.Write($"key{i}", $"value{i}");
        Thread.Sleep(500);
    }
});

// Multiple reader tasks
var readerTasks = Enumerable.Range(0, 10).Select(i => Task.Run(() =>
{
    for (int j = 0; j < 20; j++)
    {
        var value = store.Read($"key{j % 5}");
        if (value != null)
        {
            Console.WriteLine($"Reader {i} read: {value}");
        }
        Thread.Sleep(100);
    }
})).ToArray();

await Task.WhenAll(readerTasks.Concat(new[] { writerTask }));
store.Dispose();
```

### With Try Pattern

```csharp
public class SafeDataStore
{
    private readonly Dictionary<string, string> _data = new Dictionary<string, string>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    public bool TryRead(string key, out string value, TimeSpan timeout)
    {
        if (_lock.TryEnterReadLock(timeout))
        {
            try
            {
                return _data.TryGetValue(key, out value);
            }
            finally
            {
                _lock.ExitReadLock();
            }
        }
        
        Console.WriteLine("Could not acquire read lock within timeout");
        value = null;
        return false;
    }
    
    public bool TryWrite(string key, string value, TimeSpan timeout)
    {
        if (_lock.TryEnterWriteLock(timeout))
        {
            try
            {
                _data[key] = value;
                return true;
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }
        
        Console.WriteLine("Could not acquire write lock within timeout");
        return false;
    }
}
```

---

## Lock Types

### Upgradeable Read Lock

Allows upgrading from read to write lock atomically.

```csharp
public class SmartCache
{
    private readonly Dictionary<string, string> _cache = new Dictionary<string, string>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    public void UpdateIfExists(string key, string newValue)
    {
        // Enter upgradeable read lock first
        _lock.EnterUpgradeableReadLock();
        try
        {
            if (_cache.ContainsKey(key))
            {
                // Upgrade to write lock
                _lock.EnterWriteLock();
                try
                {
                    _cache[key] = newValue;
                    Console.WriteLine($"Updated {key} to {newValue}");
                }
                finally
                {
                    _lock.ExitWriteLock();
                }
            }
            else
            {
                Console.WriteLine($"Key {key} not found");
            }
        }
        finally
        {
            _lock.ExitUpgradeableReadLock();
        }
    }
    
    public string GetOrAdd(string key, Func<string> valueFactory)
    {
        // Try read first
        _lock.EnterUpgradeableReadLock();
        try
        {
            if (_cache.TryGetValue(key, out string value))
            {
                return value;
            }
            
            // Need to add - upgrade to write lock
            _lock.EnterWriteLock();
            try
            {
                // Double-check after acquiring write lock
                if (_cache.TryGetValue(key, out value))
                {
                    return value;
                }
                
                value = valueFactory();
                _cache[key] = value;
                Console.WriteLine($"Added {key} = {value}");
                return value;
            }
            finally
            {
                _lock.ExitWriteLock();
            }
        }
        finally
        {
            _lock.ExitUpgradeableReadLock();
        }
    }
}

// Usage
var cache = new SmartCache();

var tasks = Enumerable.Range(0, 10).Select(i => Task.Run(() =>
{
    var value = cache.GetOrAdd($"key{i % 3}", () => $"value{i % 3}");
    Console.WriteLine($"Task {i} got: {value}");
})).ToArray();

await Task.WhenAll(tasks);
```

### Recursion

```csharp
public class RecursiveCache
{
    private readonly Dictionary<int, int> _cache = new Dictionary<int, int>();
    private readonly ReaderWriterLockSlim _lock = 
        new ReaderWriterLockSlim(LockRecursionPolicy.SupportsRecursion);
    
    public int Fibonacci(int n)
    {
        _lock.EnterReadLock();
        try
        {
            if (_cache.TryGetValue(n, out int cached))
            {
                return cached;
            }
        }
        finally
        {
            _lock.ExitReadLock();
        }
        
        // Calculate and cache
        _lock.EnterWriteLock();
        try
        {
            // Double-check
            if (_cache.TryGetValue(n, out int cached))
            {
                return cached;
            }
            
            int result;
            if (n <= 1)
            {
                result = n;
            }
            else
            {
                // Recursive calls will re-enter the lock
                result = Fibonacci(n - 1) + Fibonacci(n - 2);
            }
            
            _cache[n] = result;
            return result;
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
}

// Note: Recursion should be avoided if possible for performance
```

---

## Use Cases

### 1. Configuration Manager

```csharp
public class ConfigurationManager
{
    private readonly Dictionary<string, string> _config = new Dictionary<string, string>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    public string GetSetting(string key)
    {
        _lock.EnterReadLock();
        try
        {
            return _cache.TryGetValue(key, out string value) ? value : null;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void UpdateSetting(string key, string value)
    {
        _lock.EnterWriteLock();
        try
        {
            _config[key] = value;
            Console.WriteLine($"Configuration updated: {key} = {value}");
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public Dictionary<string, string> GetAllSettings()
    {
        _lock.EnterReadLock();
        try
        {
            return new Dictionary<string, string>(_config);
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void LoadFromFile(string path)
    {
        var settings = File.ReadAllLines(path)
            .Select(line => line.Split('='))
            .Where(parts => parts.Length == 2)
            .ToDictionary(parts => parts[0].Trim(), parts => parts[1].Trim());
        
        _lock.EnterWriteLock();
        try
        {
            _config.Clear();
            foreach (var setting in settings)
            {
                _config[setting.Key] = setting.Value;
            }
            Console.WriteLine($"Loaded {_config.Count} settings");
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public void Dispose()
    {
        _lock?.Dispose();
    }
}

// Usage: Many reads, few writes
var config = new ConfigurationManager();
config.LoadFromFile("config.txt");

// Many reader threads
var readers = Enumerable.Range(0, 100).Select(i => Task.Run(() =>
{
    var value = config.GetSetting("DatabaseConnection");
    // Use value
})).ToArray();

// Occasional writer
var writer = Task.Run(async () =>
{
    await Task.Delay(1000);
    config.UpdateSetting("DatabaseConnection", "new-connection-string");
});

await Task.WhenAll(readers.Concat(new[] { writer }));
```

### 2. In-Memory Cache

```csharp
public class MemoryCache<TKey, TValue>
{
    private readonly Dictionary<TKey, CacheItem> _cache = new Dictionary<TKey, CacheItem>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    private class CacheItem
    {
        public TValue Value { get; set; }
        public DateTime ExpirationTime { get; set; }
        public int HitCount { get; set; }
    }
    
    public bool TryGet(TKey key, out TValue value)
    {
        _lock.EnterUpgradeableReadLock();
        try
        {
            if (_cache.TryGetValue(key, out var item))
            {
                if (DateTime.UtcNow < item.ExpirationTime)
                {
                    // Upgrade to write lock to update hit count
                    _lock.EnterWriteLock();
                    try
                    {
                        item.HitCount++;
                    }
                    finally
                    {
                        _lock.ExitWriteLock();
                    }
                    
                    value = item.Value;
                    return true;
                }
                
                // Expired - upgrade to write lock to remove
                _lock.EnterWriteLock();
                try
                {
                    _cache.Remove(key);
                }
                finally
                {
                    _lock.ExitWriteLock();
                }
            }
            
            value = default;
            return false;
        }
        finally
        {
            _lock.ExitUpgradeableReadLock();
        }
    }
    
    public void Add(TKey key, TValue value, TimeSpan expiration)
    {
        _lock.EnterWriteLock();
        try
        {
            _cache[key] = new CacheItem
            {
                Value = value,
                ExpirationTime = DateTime.UtcNow.Add(expiration),
                HitCount = 0
            };
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public void Clear()
    {
        _lock.EnterWriteLock();
        try
        {
            _cache.Clear();
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public Dictionary<TKey, int> GetStatistics()
    {
        _lock.EnterReadLock();
        try
        {
            return _cache.ToDictionary(
                kvp => kvp.Key,
                kvp => kvp.Value.HitCount);
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void Dispose()
    {
        _lock?.Dispose();
    }
}
```

### 3. User Session Store

```csharp
public class SessionStore
{
    private readonly Dictionary<string, UserSession> _sessions = 
        new Dictionary<string, UserSession>();
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    
    public class UserSession
    {
        public string UserId { get; set; }
        public DateTime LastActivity { get; set; }
        public Dictionary<string, object> Data { get; set; } = 
            new Dictionary<string, object>();
    }
    
    public UserSession GetSession(string sessionId)
    {
        _lock.EnterReadLock();
        try
        {
            return _sessions.TryGetValue(sessionId, out var session) ? session : null;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
    
    public void CreateSession(string sessionId, string userId)
    {
        _lock.EnterWriteLock();
        try
        {
            _sessions[sessionId] = new UserSession
            {
                UserId = userId,
                LastActivity = DateTime.UtcNow
            };
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public void UpdateLastActivity(string sessionId)
    {
        _lock.EnterUpgradeableReadLock();
        try
        {
            if (_sessions.TryGetValue(sessionId, out var session))
            {
                _lock.EnterWriteLock();
                try
                {
                    session.LastActivity = DateTime.UtcNow;
                }
                finally
                {
                    _lock.ExitWriteLock();
                }
            }
        }
        finally
        {
            _lock.ExitUpgradeableReadLock();
        }
    }
    
    public void RemoveExpiredSessions(TimeSpan timeout)
    {
        _lock.EnterWriteLock();
        try
        {
            var expired = _sessions
                .Where(kvp => DateTime.UtcNow - kvp.Value.LastActivity > timeout)
                .Select(kvp => kvp.Key)
                .ToList();
            
            foreach (var sessionId in expired)
            {
                _sessions.Remove(sessionId);
            }
            
            Console.WriteLine($"Removed {expired.Count} expired sessions");
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
    
    public int GetActiveSessionCount()
    {
        _lock.EnterReadLock();
        try
        {
            return _sessions.Count;
        }
        finally
        {
            _lock.ExitReadLock();
        }
    }
}
```

---

## Best Practices

### 1. Always Exit Locks in Finally

```csharp
// ✅ Good
_lock.EnterReadLock();
try
{
    // Read operation
}
finally
{
    _lock.ExitReadLock();
}
```

### 2. Minimize Lock Duration

```csharp
// ❌ Bad - Long operation in lock
_lock.EnterReadLock();
try
{
    var data = _cache[key];
    ProcessData(data); // Slow operation in lock
    return data;
}
finally
{
    _lock.ExitReadLock();
}

// ✅ Good - Copy data, release lock, then process
string data;
_lock.EnterReadLock();
try
{
    data = _cache[key];
}
finally
{
    _lock.ExitReadLock();
}

ProcessData(data);
return data;
```

### 3. Use Upgradeable Lock Carefully

```csharp
// ✅ Good - Check under upgradeable lock before upgrading
_lock.EnterUpgradeableReadLock();
try
{
    if (NeedsUpdate())
    {
        _lock.EnterWriteLock();
        try
        {
            PerformUpdate();
        }
        finally
        {
            _lock.ExitWriteLock();
        }
    }
}
finally
{
    _lock.ExitUpgradeableReadLock();
}
```

### 4. Dispose Properly

```csharp
public class DataStore : IDisposable
{
    private readonly ReaderWriterLockSlim _lock = new ReaderWriterLockSlim();
    private bool _disposed;
    
    public void Dispose()
    {
        if (_disposed) return;
        
        _lock?.Dispose();
        _disposed = true;
    }
}
```

### 5. Avoid Recursion Unless Necessary

```csharp
// ❌ Avoid - Recursion has performance cost
var lock = new ReaderWriterLockSlim(LockRecursionPolicy.SupportsRecursion);

// ✅ Prefer - No recursion (default)
var lock = new ReaderWriterLockSlim();
```

### 6. Consider ConcurrentDictionary for Simple Cases

```csharp
// ✅ For simple read/write scenarios, ConcurrentDictionary is easier
private readonly ConcurrentDictionary<string, string> _cache = 
    new ConcurrentDictionary<string, string>();

// No explicit locking needed
_cache.TryGetValue(key, out var value);
_cache.TryAdd(key, value);
```

---

## Performance Comparison

### Read-Heavy Workload (90% reads, 10% writes)

```csharp
// ReaderWriterLockSlim - Excellent
// Multiple readers can proceed simultaneously

// lock (Monitor) - Good but not optimal
// Each read acquires exclusive lock

// ConcurrentDictionary - Excellent
// Lock-free reads in many cases
```

### Write-Heavy Workload (90% writes, 10% reads)

```csharp
// ReaderWriterLockSlim - Overhead not justified
// lock (Monitor) - Better choice
// ConcurrentDictionary - Best for high concurrency
```

---

## Summary

- **ReaderWriterLockSlim**: Multiple readers, exclusive writers
- Perfect for read-heavy scenarios
- Upgradeable lock allows atomic read-to-write transition
- More overhead than simple lock - only use when beneficial
- Always exit locks in finally blocks
- Consider ConcurrentDictionary for simpler scenarios

**Next:** [Events (ManualReset & AutoReset)](./09-Events.md) | **Previous:** [Monitor and Lock](./07-Monitor-Lock.md) | **Back to:** [README](./README.md)
