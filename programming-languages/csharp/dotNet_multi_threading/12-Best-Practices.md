# Best Practices and Guidelines

Comprehensive best practices for .NET asynchronous and multithreading programming.

## Table of Contents
- [Async/Await Best Practices](#asyncawait-best-practices)
- [Thread Safety](#thread-safety)
- [Choosing the Right Tool](#choosing-the-right-tool)
- [Performance Tips](#performance-tips)
- [Common Pitfalls](#common-pitfalls)
- [Testing and Debugging](#testing-and-debugging)

---

## Async/Await Best Practices

### 1. Always Use Async All the Way

❌ **Bad:**
```csharp
public string GetData()
{
    return DownloadDataAsync().Result; // Blocks thread, can cause deadlocks
}

public void ProcessData()
{
    var task = ProcessDataAsync();
    task.Wait(); // Can cause deadlocks
}
```

✅ **Good:**
```csharp
public async Task<string> GetDataAsync()
{
    return await DownloadDataAsync();
}

public async Task ProcessDataAsync()
{
    await ProcessDataInternalAsync();
}
```

### 2. Avoid Async Void (Except Event Handlers)

❌ **Bad:**
```csharp
public async void ProcessData() // Exceptions can't be caught
{
    await SomeOperationAsync();
}
```

✅ **Good:**
```csharp
public async Task ProcessDataAsync()
{
    await SomeOperationAsync();
}

// Exception: Event handlers must be async void
private async void Button_Click(object sender, EventArgs e)
{
    try
    {
        await ProcessDataAsync();
    }
    catch (Exception ex)
    {
        // Handle exception in event handler
        LogError(ex);
    }
}
```

### 3. Use ConfigureAwait(false) in Libraries

```csharp
// In library code
public async Task<string> LibraryMethodAsync()
{
    // Don't need to return to original context in libraries
    var data = await DownloadDataAsync().ConfigureAwait(false);
    var processed = await ProcessDataAsync(data).ConfigureAwait(false);
    return processed;
}

// In application code (UI apps)
public async Task ButtonClickAsync()
{
    var data = await GetDataAsync(); // Need context to update UI
    textBox.Text = data; // Must be on UI thread
}
```

### 4. Don't Mix Blocking and Async Code

❌ **Bad:**
```csharp
public async Task BadMixAsync()
{
    Task.Run(() => DoWork()).Wait(); // Mixing async and blocking
    Thread.Sleep(1000); // Blocking in async method
}
```

✅ **Good:**
```csharp
public async Task GoodAsync()
{
    await Task.Run(() => DoWork());
    await Task.Delay(1000);
}
```

### 5. Provide Cancellation Support

```csharp
public async Task<string> ProcessDataAsync(
    string input,
    CancellationToken cancellationToken = default)
{
    // Always accept and pass through cancellation tokens
    var data = await DownloadDataAsync(input, cancellationToken);
    
    // Check cancellation periodically
    cancellationToken.ThrowIfCancellationRequested();
    
    return await TransformDataAsync(data, cancellationToken);
}

// Usage
var cts = new CancellationTokenSource();
cts.CancelAfter(TimeSpan.FromSeconds(30));

try
{
    var result = await ProcessDataAsync("input", cts.Token);
}
catch (OperationCanceledException)
{
    Console.WriteLine("Operation was cancelled");
}
```

### 6. Handle Exceptions Properly

```csharp
public async Task<string> SafeDownloadAsync(string url)
{
    try
    {
        return await DownloadDataAsync(url);
    }
    catch (HttpRequestException ex)
    {
        // Handle specific exceptions
        Console.WriteLine($"Network error: {ex.Message}");
        return null;
    }
    catch (Exception ex)
    {
        // Log unexpected exceptions
        Console.WriteLine($"Unexpected error: {ex.Message}");
        throw;
    }
}

// Handle exceptions in parallel operations
public async Task ProcessAllAsync(IEnumerable<string> items)
{
    var tasks = items.Select(async item =>
    {
        try
        {
            await ProcessItemAsync(item);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error processing {item}: {ex.Message}");
            // Handle or log, but don't let one failure stop others
        }
    });
    
    await Task.WhenAll(tasks);
}
```

### 7. Use Task.WhenAll for Concurrent Operations

```csharp
// ❌ Sequential execution
var result1 = await DownloadAsync("url1");
var result2 = await DownloadAsync("url2");
var result3 = await DownloadAsync("url3");

// ✅ Concurrent execution
var task1 = DownloadAsync("url1");
var task2 = DownloadAsync("url2");
var task3 = DownloadAsync("url3");

await Task.WhenAll(task1, task2, task3);

var results = new[] { task1.Result, task2.Result, task3.Result };
```

---

## Thread Safety

### 1. Prefer Immutable Data

```csharp
// ✅ Immutable - thread-safe by design
public class UserData
{
    public string Name { get; init; }
    public int Age { get; init; }
}

// ❌ Mutable - needs synchronization
public class UserData
{
    public string Name { get; set; }
    public int Age { get; set; }
}
```

### 2. Use Concurrent Collections

```csharp
// ✅ Thread-safe without locks
private readonly ConcurrentDictionary<string, int> _cache = new();
private readonly ConcurrentQueue<string> _queue = new();
private readonly ConcurrentBag<int> _bag = new();

public void AddToCache(string key, int value)
{
    _cache.TryAdd(key, value);
}

// ❌ Don't use regular collections without synchronization
private readonly Dictionary<string, int> _cache = new();
public void AddToCache(string key, int value)
{
    _cache[key] = value; // Not thread-safe!
}
```

### 3. Use Interlocked for Simple Operations

```csharp
// ✅ Lock-free atomic operations
private int _counter;

public void Increment()
{
    Interlocked.Increment(ref _counter);
}

public int GetAndReset()
{
    return Interlocked.Exchange(ref _counter, 0);
}

// ❌ Don't use lock for simple counters
private int _counter;
private readonly object _lock = new object();

public void Increment()
{
    lock (_lock)
    {
        _counter++; // Overkill for simple increment
    }
}
```

### 4. Minimize Lock Scope

```csharp
// ❌ Bad - Lock held during I/O
lock (_lock)
{
    var data = ReadFromDatabase(); // Slow I/O inside lock
    ProcessData(data);
    SaveToDatabase(data);
}

// ✅ Good - Minimal lock duration
var data = ReadFromDatabase();

lock (_lock)
{
    ProcessData(data); // Only thread-unsafe operation in lock
}

SaveToDatabase(data);
```

### 5. Avoid Nested Locks

```csharp
// ❌ Bad - Nested locks can cause deadlocks
private readonly object _lock1 = new();
private readonly object _lock2 = new();

public void Method1()
{
    lock (_lock1)
    {
        lock (_lock2) // Can deadlock with Method2
        {
            // Work
        }
    }
}

public void Method2()
{
    lock (_lock2)
    {
        lock (_lock1) // Can deadlock with Method1
        {
            // Work
        }
    }
}

// ✅ Good - Always acquire locks in same order
public void Method1()
{
    lock (_lock1)
    {
        lock (_lock2)
        {
            // Work
        }
    }
}

public void Method2()
{
    lock (_lock1) // Same order
    {
        lock (_lock2)
        {
            // Work
        }
    }
}
```

---

## Choosing the Right Tool

### Synchronization Primitive Selection

```csharp
// Critical section (single process)
lock (_lockObject) { /* critical section */ }

// Critical section (cross-process)
using (var mutex = new Mutex(false, "Global\\MyMutex"))
{
    mutex.WaitOne();
    try { /* critical section */ }
    finally { mutex.ReleaseMutex(); }
}

// Limit concurrent access
var semaphore = new SemaphoreSlim(5, 5);
await semaphore.WaitAsync();
try { /* limited access */ }
finally { semaphore.Release(); }

// Many readers, few writers
_rwLock.EnterReadLock();
try { /* read data */ }
finally { _rwLock.ExitReadLock(); }

// Signal between threads
_event.Set(); // Signal
_event.WaitOne(); // Wait

// Coordinate phases
barrier.SignalAndWait(); // All threads sync here

// Wait for N operations
countdown.Signal(); // One operation complete
countdown.Wait(); // Wait for all
```

### Decision Table

| Scenario | Use |
|----------|-----|
| Protect critical section (single process) | `lock` or `Monitor` |
| Protect critical section (cross-process) | `Mutex` |
| Limit concurrent access to N | `SemaphoreSlim` |
| Many readers, few writers | `ReaderWriterLockSlim` |
| Signal one waiting thread | `AutoResetEvent` |
| Signal all waiting threads | `ManualResetEvent` |
| Synchronize through phases | `Barrier` |
| Wait for N signals | `CountdownEvent` |
| Wait for any/all async operations | `Task.WhenAny` / `Task.WhenAll` |
| Simple counter | `Interlocked` |
| Thread-safe collection | `ConcurrentDictionary`, etc. |

---

## Performance Tips

### 1. Use async for I/O, not CPU Work

```csharp
// ✅ Good - async for I/O
public async Task<string> DownloadAsync(string url)
{
    using var client = new HttpClient();
    return await client.GetStringAsync(url);
}

// ❌ Bad - async wrapper around CPU work
public async Task<int> CalculateAsync(int n)
{
    return await Task.Run(() =>
    {
        // CPU-bound work in Task.Run is wasteful
        return Fibonacci(n);
    });
}

// ✅ Good - synchronous for CPU work
public int Calculate(int n)
{
    return Fibonacci(n);
}
```

### 2. Avoid Creating Unnecessary Tasks

```csharp
// ❌ Bad - Too many tasks
var tasks = Enumerable.Range(0, 1000000)
    .Select(i => Task.Run(() => Process(i)))
    .ToArray();
await Task.WhenAll(tasks);

// ✅ Good - Use Parallel for CPU-bound work
Parallel.ForEach(Enumerable.Range(0, 1000000), 
    new ParallelOptions { MaxDegreeOfParallelism = Environment.ProcessorCount },
    i => Process(i));

// ✅ Good - Limit concurrency for I/O
var semaphore = new SemaphoreSlim(10); // Max 10 concurrent
var tasks = items.Select(async item =>
{
    await semaphore.WaitAsync();
    try { return await ProcessAsync(item); }
    finally { semaphore.Release(); }
});
await Task.WhenAll(tasks);
```

### 3. Use ValueTask for Hot Paths

```csharp
// ✅ Good - ValueTask for frequently synchronous results
public ValueTask<int> GetCachedValueAsync(string key)
{
    if (_cache.TryGetValue(key, out int value))
    {
        return new ValueTask<int>(value); // No allocation
    }
    
    return new ValueTask<int>(LoadFromDatabaseAsync(key));
}

// Usage
int value = await GetCachedValueAsync("key");
```

### 4. Pool and Reuse Objects

```csharp
// ✅ Good - Use ArrayPool
var pool = ArrayPool<byte>.Shared;
var buffer = pool.Rent(4096);
try
{
    // Use buffer
}
finally
{
    pool.Return(buffer);
}

// ✅ Good - Use ObjectPool
private readonly ObjectPool<StringBuilder> _stringBuilderPool = 
    ObjectPool.Create<StringBuilder>();

public string BuildString()
{
    var sb = _stringBuilderPool.Get();
    try
    {
        sb.Append("data");
        return sb.ToString();
    }
    finally
    {
        sb.Clear();
        _stringBuilderPool.Return(sb);
    }
}
```

### 5. Avoid Async State Machines When Not Needed

```csharp
// ❌ Unnecessary async/await
public async Task<string> GetDataAsync()
{
    return await _service.GetDataAsync();
}

// ✅ Better - Return task directly
public Task<string> GetDataAsync()
{
    return _service.GetDataAsync();
}
```

---

## Common Pitfalls

### 1. Deadlocks

```csharp
// ❌ Deadlock - Blocking on async code with synchronization context
public void Deadlock()
{
    var task = DownloadAsync();
    task.Wait(); // Deadlocks in UI apps!
}

// ✅ Fix 1 - Use async all the way
public async Task NoDeadlockAsync()
{
    await DownloadAsync();
}

// ✅ Fix 2 - Use ConfigureAwait(false) in library code
public void NoDeadlock()
{
    var task = DownloadWithConfigureAwaitAsync();
    task.Wait(); // OK because ConfigureAwait(false) used
}

private async Task DownloadWithConfigureAwaitAsync()
{
    await DownloadAsync().ConfigureAwait(false);
}
```

### 2. Captured Variables in Loops

```csharp
// ❌ Bad - Captured variable
for (int i = 0; i < 10; i++)
{
    Task.Run(() => Console.WriteLine(i)); // All print 10!
}

// ✅ Good - Copy to local variable
for (int i = 0; i < 10; i++)
{
    int copy = i;
    Task.Run(() => Console.WriteLine(copy)); // Prints 0-9
}
```

### 3. Not Disposing Resources

```csharp
// ❌ Bad - Resource leak
var semaphore = new SemaphoreSlim(5);
// ...forgot to dispose

// ✅ Good - Always dispose
using var semaphore = new SemaphoreSlim(5);
// Automatically disposed

// ✅ Good - Dispose in finally
var semaphore = new SemaphoreSlim(5);
try
{
    // Use semaphore
}
finally
{
    semaphore.Dispose();
}
```

### 4. Swallowing Exceptions

```csharp
// ❌ Bad - Lost exceptions
_ = Task.Run(async () =>
{
    await DoWorkAsync(); // Exception lost!
});

// ✅ Good - Handle exceptions
_ = Task.Run(async () =>
{
    try
    {
        await DoWorkAsync();
    }
    catch (Exception ex)
    {
        Log.Error(ex);
    }
});

// ✅ Good - Observe task
var task = Task.Run(async () => await DoWorkAsync());
// Later...
try
{
    await task;
}
catch (Exception ex)
{
    Log.Error(ex);
}
```

### 5. Assuming Thread Affinity

```csharp
// ❌ Bad - Thread-local storage across await
[ThreadStatic]
private static int _threadValue;

public async Task BadAsync()
{
    _threadValue = 42;
    await Task.Delay(100);
    // _threadValue might not be 42! Different thread might resume.
}

// ✅ Good - Use AsyncLocal for async context
private static AsyncLocal<int> _asyncValue = new AsyncLocal<int>();

public async Task GoodAsync()
{
    _asyncValue.Value = 42;
    await Task.Delay(100);
    // _asyncValue.Value is still 42 - follows async context
}
```

---

## Testing and Debugging

### 1. Test Concurrent Code

```csharp
[Test]
public async Task TestThreadSafeCounter()
{
    var counter = new ThreadSafeCounter();
    
    // Run many concurrent increments
    var tasks = Enumerable.Range(0, 1000)
        .Select(_ => Task.Run(() => counter.Increment()));
    
    await Task.WhenAll(tasks);
    
    Assert.AreEqual(1000, counter.Value);
}
```

### 2. Test Cancellation

```csharp
[Test]
public async Task TestCancellation()
{
    var cts = new CancellationTokenSource();
    
    var task = LongRunningOperationAsync(cts.Token);
    
    // Cancel after short delay
    await Task.Delay(100);
    cts.Cancel();
    
    // Should throw OperationCanceledException
    await Assert.ThrowsAsync<OperationCanceledException>(() => task);
}
```

### 3. Use Timeout in Tests

```csharp
[Test]
public async Task TestWithTimeout()
{
    var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    
    // Test should complete within 5 seconds
    await ProcessDataAsync(cts.Token);
}
```

### 4. Enable Debugging Features

```csharp
// In development, enable synchronization context checks
#if DEBUG
    if (SynchronizationContext.Current != null)
    {
        Console.WriteLine("Warning: Synchronization context present");
    }
#endif
```

---

## Quick Reference Checklist

### Before Committing Code

- [ ] All async methods named with `Async` suffix
- [ ] No `async void` (except event handlers)
- [ ] ConfigureAwait(false) used in library code
- [ ] Cancellation tokens accepted where appropriate
- [ ] No blocking calls (.Result, .Wait()) in async code
- [ ] Exceptions properly handled
- [ ] Resources properly disposed
- [ ] No race conditions on shared state
- [ ] Appropriate synchronization primitives used
- [ ] Tests cover concurrent scenarios
- [ ] Deadlock scenarios considered
- [ ] Performance characteristics understood

---

## Summary

**Async/Await:**
- Use async all the way down
- Avoid async void
- Use ConfigureAwait(false) in libraries
- Always handle cancellation

**Thread Safety:**
- Prefer immutable data
- Use concurrent collections
- Minimize lock scope
- Avoid nested locks

**Performance:**
- async for I/O, not CPU work
- Limit task creation
- Pool and reuse objects
- Use appropriate concurrency level

**Common Pitfalls:**
- Watch for deadlocks
- Handle captured variables correctly
- Always dispose resources
- Don't swallow exceptions

**Testing:**
- Test concurrent scenarios
- Test cancellation
- Use timeouts
- Enable debugging features

---

**Previous:** [CountdownEvent](./11-CountdownEvent.md) | **Back to:** [README](./README.md)
