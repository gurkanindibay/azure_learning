# Semaphore and SemaphoreSlim

Controls access to a resource pool with a maximum count. Useful for throttling concurrent operations.

## Table of Contents
- [Overview](#overview)
- [SemaphoreSlim (Recommended)](#semaphoreslim-recommended)
- [Semaphore](#semaphore)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

A semaphore is a synchronization primitive that limits the number of threads that can access a resource or pool of resources concurrently.

**Key Concepts:**
- **Initial Count**: Current number of available slots
- **Maximum Count**: Maximum number of threads that can enter
- **WaitOne/WaitAsync**: Decrements count and blocks if zero
- **Release**: Increments count and signals waiting threads

---

## SemaphoreSlim (Recommended)

Lightweight, async-friendly version suitable for single-process scenarios.

### Basic Usage

```csharp
public class RateLimiter
{
    private readonly SemaphoreSlim _semaphore;
    
    public RateLimiter(int maxConcurrent)
    {
        _semaphore = new SemaphoreSlim(maxConcurrent, maxConcurrent);
    }
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        await _semaphore.WaitAsync(); // Wait for available slot
        try
        {
            return await operation();
        }
        finally
        {
            _semaphore.Release(); // Release slot
        }
    }
    
    public int AvailableSlots => _semaphore.CurrentCount;
}

// Usage
var limiter = new RateLimiter(maxConcurrent: 3);
var result = await limiter.ExecuteAsync(async () =>
{
    await Task.Delay(1000);
    return "Complete";
});
```

### Limiting Concurrent API Calls

```csharp
public class ThrottledApiClient
{
    private readonly HttpClient _client;
    private readonly SemaphoreSlim _semaphore;
    
    public ThrottledApiClient(int maxConcurrentRequests)
    {
        _client = new HttpClient();
        _semaphore = new SemaphoreSlim(maxConcurrentRequests, maxConcurrentRequests);
    }
    
    public async Task<string> GetAsync(string url)
    {
        await _semaphore.WaitAsync();
        try
        {
            Console.WriteLine($"Making request to {url} " +
                            $"(Available slots: {_semaphore.CurrentCount})");
            return await _client.GetStringAsync(url);
        }
        finally
        {
            _semaphore.Release();
            Console.WriteLine($"Request complete (Available slots: {_semaphore.CurrentCount})");
        }
    }
}

// Usage: Limit to 5 concurrent requests
var client = new ThrottledApiClient(maxConcurrentRequests: 5);

var urls = Enumerable.Range(1, 20)
    .Select(i => $"https://api.example.com/data/{i}");

var tasks = urls.Select(url => client.GetAsync(url));
var results = await Task.WhenAll(tasks);

Console.WriteLine($"Downloaded {results.Length} items");
```

### Download Throttling Example

```csharp
public class ThrottledDownloader
{
    private readonly SemaphoreSlim _semaphore;
    private readonly HttpClient _client;
    
    public ThrottledDownloader(int maxConcurrentDownloads)
    {
        _semaphore = new SemaphoreSlim(maxConcurrentDownloads);
        _client = new HttpClient();
    }
    
    public async Task<byte[]> DownloadAsync(string url)
    {
        await _semaphore.WaitAsync();
        try
        {
            Console.WriteLine($"Downloading {url}");
            var data = await _client.GetByteArrayAsync(url);
            Console.WriteLine($"Completed {url} ({data.Length} bytes)");
            return data;
        }
        finally
        {
            _semaphore.Release();
        }
    }
    
    public async Task<List<byte[]>> DownloadAllAsync(IEnumerable<string> urls)
    {
        var tasks = urls.Select(url => DownloadAsync(url));
        var results = await Task.WhenAll(tasks);
        return results.ToList();
    }
}

// Usage: Maximum 3 concurrent downloads
var downloader = new ThrottledDownloader(maxConcurrentDownloads: 3);
var urls = new[]
{
    "https://example.com/file1.jpg",
    "https://example.com/file2.jpg",
    "https://example.com/file3.jpg",
    "https://example.com/file4.jpg",
    "https://example.com/file5.jpg",
};

var files = await downloader.DownloadAllAsync(urls);
Console.WriteLine($"Downloaded {files.Count} files");
```

### With Cancellation Token

```csharp
public async Task<T> ExecuteWithCancellationAsync<T>(
    Func<Task<T>> operation, 
    CancellationToken cancellationToken)
{
    await _semaphore.WaitAsync(cancellationToken);
    try
    {
        return await operation();
    }
    finally
    {
        _semaphore.Release();
    }
}
```

### With Timeout

```csharp
public async Task<T> ExecuteWithTimeoutAsync<T>(
    Func<Task<T>> operation, 
    TimeSpan timeout)
{
    if (!await _semaphore.WaitAsync(timeout))
    {
        throw new TimeoutException("Could not acquire semaphore within timeout");
    }
    
    try
    {
        return await operation();
    }
    finally
    {
        _semaphore.Release();
    }
}
```

### Database Connection Pool Simulation

```csharp
public class ConnectionPool
{
    private readonly SemaphoreSlim _semaphore;
    private readonly int _maxConnections;
    
    public ConnectionPool(int maxConnections)
    {
        _maxConnections = maxConnections;
        _semaphore = new SemaphoreSlim(maxConnections, maxConnections);
    }
    
    public async Task<T> ExecuteQueryAsync<T>(Func<Task<T>> query)
    {
        Console.WriteLine($"Waiting for connection " +
                         $"({_maxConnections - _semaphore.CurrentCount}/{_maxConnections} in use)");
        
        await _semaphore.WaitAsync();
        try
        {
            Console.WriteLine($"Acquired connection " +
                            $"({_maxConnections - _semaphore.CurrentCount}/{_maxConnections} in use)");
            return await query();
        }
        finally
        {
            _semaphore.Release();
            Console.WriteLine($"Released connection " +
                            $"({_maxConnections - _semaphore.CurrentCount}/{_maxConnections} in use)");
        }
    }
}

// Usage
var pool = new ConnectionPool(maxConnections: 5);

var queries = Enumerable.Range(1, 20).Select(async i =>
{
    return await pool.ExecuteQueryAsync(async () =>
    {
        Console.WriteLine($"Executing query {i}");
        await Task.Delay(Random.Shared.Next(100, 500));
        return $"Result {i}";
    });
});

var results = await Task.WhenAll(queries);
```

---

## Semaphore

Cross-process capable semaphore. Heavier than SemaphoreSlim but works across process boundaries.

### Basic Usage

```csharp
public void SemaphoreExample()
{
    using (var semaphore = new Semaphore(3, 3)) // 3 concurrent threads
    {
        var tasks = Enumerable.Range(0, 10).Select(i => Task.Run(() =>
        {
            Console.WriteLine($"Task {i} waiting...");
            semaphore.WaitOne(); // Blocks until slot available
            try
            {
                Console.WriteLine($"Task {i} acquired semaphore");
                Thread.Sleep(1000);
            }
            finally
            {
                Console.WriteLine($"Task {i} releasing semaphore");
                semaphore.Release();
            }
        })).ToArray();
        
        Task.WaitAll(tasks);
    }
}
```

### Named Semaphore (Cross-Process)

```csharp
public class CrossProcessLimiter
{
    private readonly Semaphore _semaphore;
    
    public CrossProcessLimiter(string name, int maxCount)
    {
        // Create or open named semaphore
        _semaphore = new Semaphore(maxCount, maxCount, $"Global\\{name}");
    }
    
    public void Execute(Action action)
    {
        Console.WriteLine($"Process {Process.GetCurrentProcess().Id} waiting...");
        _semaphore.WaitOne();
        try
        {
            Console.WriteLine($"Process {Process.GetCurrentProcess().Id} executing");
            action();
        }
        finally
        {
            _semaphore.Release();
            Console.WriteLine($"Process {Process.GetCurrentProcess().Id} released");
        }
    }
    
    public void Dispose()
    {
        _semaphore?.Dispose();
    }
}

// Usage: Limit resource access across multiple application instances
var limiter = new CrossProcessLimiter("MyAppResourceLimit", maxCount: 3);

limiter.Execute(() =>
{
    // Only 3 instances across all processes can execute this simultaneously
    Console.WriteLine("Accessing shared resource");
    Thread.Sleep(2000);
});

limiter.Dispose();
```

### With Timeout

```csharp
public bool TryExecute(Action action, TimeSpan timeout)
{
    if (_semaphore.WaitOne(timeout))
    {
        try
        {
            action();
            return true;
        }
        finally
        {
            _semaphore.Release();
        }
    }
    
    Console.WriteLine("Could not acquire semaphore within timeout");
    return false;
}
```

---

## Use Cases

### 1. Rate Limiting API Calls

```csharp
public class ApiRateLimiter
{
    private readonly SemaphoreSlim _semaphore;
    private readonly int _requestsPerSecond;
    private readonly Queue<DateTime> _requestTimes;
    private readonly object _lock = new object();
    
    public ApiRateLimiter(int requestsPerSecond)
    {
        _requestsPerSecond = requestsPerSecond;
        _semaphore = new SemaphoreSlim(requestsPerSecond);
        _requestTimes = new Queue<DateTime>();
    }
    
    public async Task<T> ExecuteAsync<T>(Func<Task<T>> operation)
    {
        await _semaphore.WaitAsync();
        
        try
        {
            // Wait if we've exceeded rate limit
            lock (_lock)
            {
                while (_requestTimes.Count >= _requestsPerSecond)
                {
                    var oldestRequest = _requestTimes.Peek();
                    var elapsed = DateTime.UtcNow - oldestRequest;
                    
                    if (elapsed < TimeSpan.FromSeconds(1))
                    {
                        var delay = TimeSpan.FromSeconds(1) - elapsed;
                        Thread.Sleep(delay);
                    }
                    
                    _requestTimes.Dequeue();
                }
                
                _requestTimes.Enqueue(DateTime.UtcNow);
            }
            
            return await operation();
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
```

### 2. Limiting Database Connections

```csharp
public class DatabasePool
{
    private readonly SemaphoreSlim _connectionSemaphore;
    
    public DatabasePool(int maxConnections)
    {
        _connectionSemaphore = new SemaphoreSlim(maxConnections);
    }
    
    public async Task<T> QueryAsync<T>(string sql, Func<IDbConnection, Task<T>> query)
    {
        await _connectionSemaphore.WaitAsync();
        IDbConnection connection = null;
        
        try
        {
            connection = CreateConnection(); // Get connection from pool
            await connection.OpenAsync();
            return await query(connection);
        }
        finally
        {
            connection?.Close();
            _connectionSemaphore.Release();
        }
    }
    
    private IDbConnection CreateConnection()
    {
        // Create actual database connection
        return new SqlConnection("connection-string");
    }
}
```

### 3. Parallel File Processing with Limit

```csharp
public class FileProcessor
{
    private readonly SemaphoreSlim _semaphore;
    
    public FileProcessor(int maxConcurrentFiles)
    {
        _semaphore = new SemaphoreSlim(maxConcurrentFiles);
    }
    
    public async Task ProcessFilesAsync(IEnumerable<string> filePaths)
    {
        var tasks = filePaths.Select(async filePath =>
        {
            await _semaphore.WaitAsync();
            try
            {
                await ProcessFileAsync(filePath);
            }
            finally
            {
                _semaphore.Release();
            }
        });
        
        await Task.WhenAll(tasks);
    }
    
    private async Task ProcessFileAsync(string filePath)
    {
        Console.WriteLine($"Processing {filePath}");
        var content = await File.ReadAllTextAsync(filePath);
        // Process content
        await Task.Delay(100); // Simulate processing
        Console.WriteLine($"Completed {filePath}");
    }
}

// Usage: Process max 5 files concurrently
var processor = new FileProcessor(maxConcurrentFiles: 5);
var files = Directory.GetFiles("./data", "*.txt");
await processor.ProcessFilesAsync(files);
```

---

## Best Practices

### 1. Always Release in Finally Block

```csharp
// ✅ Good
await _semaphore.WaitAsync();
try
{
    await DoWorkAsync();
}
finally
{
    _semaphore.Release(); // Always releases, even on exception
}
```

### 2. Prefer SemaphoreSlim Over Semaphore

```csharp
// ✅ Use SemaphoreSlim for async code
private readonly SemaphoreSlim _semaphore = new SemaphoreSlim(5, 5);

public async Task ExecuteAsync()
{
    await _semaphore.WaitAsync();
    // ...
}

// ❌ Avoid Semaphore unless you need cross-process
private readonly Semaphore _semaphore = new Semaphore(5, 5);
```

### 3. Don't Release More Than You Acquired

```csharp
// ❌ Bad - will throw exception
_semaphore.Release(2); // But only acquired once!

// ✅ Good - release exactly once per acquisition
await _semaphore.WaitAsync();
try
{
    // work
}
finally
{
    _semaphore.Release(); // Exactly one release
}
```

### 4. Use CancellationToken

```csharp
public async Task ExecuteAsync(CancellationToken cancellationToken)
{
    await _semaphore.WaitAsync(cancellationToken);
    try
    {
        // Work that respects cancellation
        await DoWorkAsync(cancellationToken);
    }
    finally
    {
        _semaphore.Release();
    }
}
```

### 5. Dispose Properly

```csharp
public class ResourceManager : IDisposable
{
    private readonly SemaphoreSlim _semaphore;
    
    public ResourceManager(int maxConcurrent)
    {
        _semaphore = new SemaphoreSlim(maxConcurrent);
    }
    
    public void Dispose()
    {
        _semaphore?.Dispose();
    }
}

// Usage
using (var manager = new ResourceManager(5))
{
    // Use manager
}
```

### 6. Monitor Available Count

```csharp
public class MonitoredSemaphore
{
    private readonly SemaphoreSlim _semaphore;
    
    public int AvailableSlots => _semaphore.CurrentCount;
    public int MaxSlots { get; }
    public int UsedSlots => MaxSlots - AvailableSlots;
    
    public MonitoredSemaphore(int maxConcurrent)
    {
        MaxSlots = maxConcurrent;
        _semaphore = new SemaphoreSlim(maxConcurrent, maxConcurrent);
    }
    
    public async Task ExecuteAsync(Func<Task> operation)
    {
        Console.WriteLine($"Semaphore: {UsedSlots}/{MaxSlots} in use");
        await _semaphore.WaitAsync();
        try
        {
            await operation();
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
```

---

## Summary

- **SemaphoreSlim**: Lightweight, async-friendly, single-process
- **Semaphore**: Cross-process capable, heavier weight
- Use for throttling concurrent operations
- Perfect for rate limiting, connection pooling, resource limiting
- Always release in finally block
- Prefer SemaphoreSlim unless you need cross-process synchronization

**Next:** [Mutex](./06-Mutex.md) | **Previous:** [Multithreading Concepts](./04-Multithreading-Concepts.md) | **Back to:** [README](./README.md)
