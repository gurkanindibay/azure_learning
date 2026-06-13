# Multithreading Concepts

Understanding the fundamentals of multithreading in .NET.

## Table of Contents
- [Overview](#overview)
- [Thread vs Task](#thread-vs-task)
- [ThreadPool](#threadpool)
- [Parallel Programming](#parallel-programming)
- [Thread Safety](#thread-safety)
- [Best Practices](#best-practices)

---

## Overview

Multithreading allows multiple operations to execute concurrently within a single application. .NET provides several abstractions for working with threads, from low-level Thread class to high-level Task-based operations.

**Key Concepts:**
- **Thread**: A unit of execution within a process
- **Concurrency**: Multiple operations making progress simultaneously
- **Parallelism**: Multiple operations executing simultaneously on different cores
- **Thread Safety**: Code that works correctly when accessed by multiple threads

---

## Thread vs Task

### Thread

Lower-level abstraction with direct OS thread mapping.

```csharp
public void ThreadExample()
{
    var thread = new Thread(() =>
    {
        Console.WriteLine($"Running on thread {Thread.CurrentThread.ManagedThreadId}");
        Console.WriteLine($"Is background: {Thread.CurrentThread.IsBackground}");
        Thread.Sleep(1000);
        Console.WriteLine("Thread work complete");
    });
    
    thread.Name = "WorkerThread";
    thread.IsBackground = true; // Won't prevent app termination
    thread.Start();
    
    thread.Join(); // Wait for completion
    Console.WriteLine("Thread has finished");
}
```

#### Thread Properties

```csharp
public void ThreadProperties()
{
    var thread = new Thread(() =>
    {
        Console.WriteLine($"Thread ID: {Thread.CurrentThread.ManagedThreadId}");
        Console.WriteLine($"Thread Name: {Thread.CurrentThread.Name}");
        Console.WriteLine($"Is Background: {Thread.CurrentThread.IsBackground}");
        Console.WriteLine($"Is ThreadPool: {Thread.CurrentThread.IsThreadPoolThread}");
        Console.WriteLine($"Priority: {Thread.CurrentThread.Priority}");
    })
    {
        Name = "MyThread",
        Priority = ThreadPriority.Normal,
        IsBackground = true
    };
    
    thread.Start();
    thread.Join();
}
```

#### Thread with Parameters

```csharp
public void ThreadWithParameter()
{
    var thread = new Thread(obj =>
    {
        string message = (string)obj;
        Console.WriteLine($"Message: {message}");
    });
    
    thread.Start("Hello from thread");
    thread.Join();
}
```

### Task

Higher-level abstraction using the ThreadPool.

```csharp
public async Task TaskExample()
{
    var task = Task.Run(() =>
    {
        Console.WriteLine($"Running on thread {Thread.CurrentThread.ManagedThreadId}");
        Console.WriteLine($"Is ThreadPool thread: {Thread.CurrentThread.IsThreadPoolThread}");
        Thread.Sleep(1000);
        Console.WriteLine("Task work complete");
        return 42;
    });
    
    int result = await task;
    Console.WriteLine($"Task result: {result}");
}
```

#### Task with Return Value

```csharp
public async Task<int> CalculateAsync()
{
    return await Task.Run(() =>
    {
        Thread.Sleep(1000);
        return 42 * 2;
    });
}

// Usage
int result = await CalculateAsync();
Console.WriteLine($"Result: {result}");
```

#### Task Continuations

```csharp
public async Task ContinuationExample()
{
    var task = Task.Run(() =>
    {
        Thread.Sleep(1000);
        return 42;
    });
    
    // Continue with another task
    var continuation = task.ContinueWith(t =>
    {
        Console.WriteLine($"Previous result: {t.Result}");
        return t.Result * 2;
    });
    
    int finalResult = await continuation;
    Console.WriteLine($"Final result: {finalResult}");
}
```

### Comparison

| Feature | Thread | Task |
|---------|--------|------|
| Abstraction Level | Low | High |
| Thread Management | Manual | Automatic (ThreadPool) |
| Resource Usage | Higher (dedicated thread) | Lower (shared threads) |
| Cancellation | Manual | Built-in (CancellationToken) |
| Exception Handling | Manual | Built-in propagation |
| Async/Await | No | Yes |
| Return Values | Difficult | Easy (Task<T>) |
| Composition | Difficult | Easy (Task.WhenAll, etc.) |
| **Recommendation** | Rare cases | Default choice |

---

## ThreadPool

The ThreadPool manages a pool of worker threads, reducing the overhead of thread creation.

### Basic ThreadPool Usage

```csharp
public void ThreadPoolExample()
{
    ThreadPool.QueueUserWorkItem(state =>
    {
        Console.WriteLine($"ThreadPool thread: {Thread.CurrentThread.ManagedThreadId}");
        Console.WriteLine($"Is ThreadPool: {Thread.CurrentThread.IsThreadPoolThread}");
        Thread.Sleep(1000);
        Console.WriteLine("Work complete");
    });
    
    // Wait for work to complete
    Thread.Sleep(2000);
}
```

### ThreadPool with State

```csharp
public void ThreadPoolWithState()
{
    var data = new { Id = 1, Name = "Task Data" };
    
    ThreadPool.QueueUserWorkItem(state =>
    {
        var taskData = (dynamic)state;
        Console.WriteLine($"Processing: {taskData.Name} (ID: {taskData.Id})");
    }, data);
    
    Thread.Sleep(1000);
}
```

### ThreadPool Configuration

```csharp
public void ConfigureThreadPool()
{
    // Get current settings
    ThreadPool.GetMaxThreads(out int maxWorkerThreads, out int maxIOThreads);
    ThreadPool.GetMinThreads(out int minWorkerThreads, out int minIOThreads);
    ThreadPool.GetAvailableThreads(out int availableWorkerThreads, out int availableIOThreads);
    
    Console.WriteLine($"Max threads: {maxWorkerThreads} worker, {maxIOThreads} I/O");
    Console.WriteLine($"Min threads: {minWorkerThreads} worker, {minIOThreads} I/O");
    Console.WriteLine($"Available: {availableWorkerThreads} worker, {availableIOThreads} I/O");
    
    // Set minimum threads (optional - usually not needed)
    ThreadPool.SetMinThreads(4, 4);
}
```

### Task.Run Uses ThreadPool

```csharp
public async Task TaskRunUsesThreadPool()
{
    // Task.Run automatically uses ThreadPool
    await Task.Run(() =>
    {
        Console.WriteLine($"Is ThreadPool thread: {Thread.CurrentThread.IsThreadPoolThread}");
        // Will print: True
    });
}
```

---

## Parallel Programming

### Parallel.For

```csharp
public void ParallelForExample()
{
    Parallel.For(0, 10, i =>
    {
        Console.WriteLine($"Processing {i} on thread {Thread.CurrentThread.ManagedThreadId}");
        Thread.Sleep(100);
    });
    
    Console.WriteLine("All iterations complete");
}
```

### Parallel.ForEach

```csharp
public void ParallelForEachExample()
{
    var items = Enumerable.Range(1, 10).ToList();
    
    Parallel.ForEach(items, item =>
    {
        Console.WriteLine($"Processing item {item} on thread {Thread.CurrentThread.ManagedThreadId}");
        Thread.Sleep(100);
    });
    
    Console.WriteLine("All items processed");
}
```

### Parallel.ForEach with Options

```csharp
public void ParallelWithOptions()
{
    var items = Enumerable.Range(1, 20).ToList();
    
    var options = new ParallelOptions
    {
        MaxDegreeOfParallelism = 4, // Limit to 4 concurrent threads
        CancellationToken = CancellationToken.None
    };
    
    Parallel.ForEach(items, options, item =>
    {
        Console.WriteLine($"Item {item} on thread {Thread.CurrentThread.ManagedThreadId}");
        Thread.Sleep(500);
    });
}
```

### Parallel.Invoke

```csharp
public void ParallelInvokeExample()
{
    Parallel.Invoke(
        () => {
            Console.WriteLine("Action 1");
            Thread.Sleep(1000);
        },
        () => {
            Console.WriteLine("Action 2");
            Thread.Sleep(1000);
        },
        () => {
            Console.WriteLine("Action 3");
            Thread.Sleep(1000);
        }
    );
    
    Console.WriteLine("All actions complete");
}
```

### PLINQ (Parallel LINQ)

```csharp
public void PLINQExample()
{
    var numbers = Enumerable.Range(1, 1000);
    
    // Parallel query
    var evenNumbers = numbers
        .AsParallel()
        .Where(n => n % 2 == 0)
        .Select(n => n * n)
        .ToList();
    
    Console.WriteLine($"Found {evenNumbers.Count} even numbers");
}
```

#### PLINQ with Degree of Parallelism

```csharp
public void PLINQWithDegree()
{
    var numbers = Enumerable.Range(1, 1000);
    
    var result = numbers
        .AsParallel()
        .WithDegreeOfParallelism(4) // Use max 4 threads
        .WithExecutionMode(ParallelExecutionMode.ForceParallelism)
        .Select(n => ExpensiveOperation(n))
        .ToList();
}

private int ExpensiveOperation(int n)
{
    Thread.Sleep(10);
    return n * n;
}
```

---

## Thread Safety

### Race Conditions

❌ **Not Thread-Safe:**
```csharp
public class UnsafeCounter
{
    private int _count = 0;
    
    public void Increment()
    {
        _count++; // NOT thread-safe
    }
    
    public int GetCount() => _count;
}

// Will have incorrect count due to race conditions
var counter = new UnsafeCounter();
Parallel.For(0, 1000, i => counter.Increment());
Console.WriteLine(counter.GetCount()); // Not 1000!
```

✅ **Thread-Safe with Lock:**
```csharp
public class SafeCounter
{
    private int _count = 0;
    private readonly object _lock = new object();
    
    public void Increment()
    {
        lock (_lock)
        {
            _count++;
        }
    }
    
    public int GetCount()
    {
        lock (_lock)
        {
            return _count;
        }
    }
}
```

✅ **Thread-Safe with Interlocked:**
```csharp
public class InterlockedCounter
{
    private int _count = 0;
    
    public void Increment()
    {
        Interlocked.Increment(ref _count);
    }
    
    public int GetCount() => _count;
}
```

### Thread-Local Storage

```csharp
public void ThreadLocalExample()
{
    var threadLocal = new ThreadLocal<int>(() =>
    {
        // Initialization per thread
        return Thread.CurrentThread.ManagedThreadId;
    });
    
    Parallel.For(0, 5, i =>
    {
        Console.WriteLine($"Iteration {i}: ThreadLocal value = {threadLocal.Value}");
    });
    
    threadLocal.Dispose();
}
```

### Concurrent Collections

```csharp
public void ConcurrentCollectionsExample()
{
    // Thread-safe collections
    var concurrentBag = new ConcurrentBag<int>();
    var concurrentQueue = new ConcurrentQueue<int>();
    var concurrentStack = new ConcurrentStack<int>();
    var concurrentDict = new ConcurrentDictionary<string, int>();
    
    // Add items in parallel
    Parallel.For(0, 100, i =>
    {
        concurrentBag.Add(i);
        concurrentQueue.Enqueue(i);
        concurrentStack.Push(i);
        concurrentDict.TryAdd($"key{i}", i);
    });
    
    Console.WriteLine($"Bag count: {concurrentBag.Count}");
    Console.WriteLine($"Queue count: {concurrentQueue.Count}");
    Console.WriteLine($"Stack count: {concurrentStack.Count}");
    Console.WriteLine($"Dictionary count: {concurrentDict.Count}");
}
```

---

## Best Practices

### 1. Prefer Task over Thread

```csharp
// ❌ Don't
var thread = new Thread(() => DoWork());
thread.Start();

// ✅ Do
await Task.Run(() => DoWork());
```

### 2. Use async/await for I/O

```csharp
// ❌ Don't block threads for I/O
Task.Run(() =>
{
    var data = File.ReadAllText("file.txt"); // Blocks ThreadPool thread
});

// ✅ Do use async I/O
await File.ReadAllTextAsync("file.txt"); // Doesn't block
```

### 3. Don't Create Too Many Tasks

```csharp
// ❌ Don't
var tasks = Enumerable.Range(0, 1000000)
    .Select(i => Task.Run(() => Process(i)))
    .ToArray();
await Task.WhenAll(tasks);

// ✅ Do use Parallel or limit concurrency
Parallel.ForEach(Enumerable.Range(0, 1000000), i => Process(i));
```

### 4. Use Cancellation Tokens

```csharp
public async Task LongRunningOperationAsync(CancellationToken token)
{
    for (int i = 0; i < 1000; i++)
    {
        token.ThrowIfCancellationRequested();
        await ProcessItemAsync(i);
    }
}
```

### 5. Avoid Shared Mutable State

```csharp
// ❌ Avoid
int counter = 0;
Parallel.For(0, 100, i => counter++); // Race condition

// ✅ Use thread-safe mechanisms
int counter = 0;
Parallel.For(0, 100, i => Interlocked.Increment(ref counter));
```

---

## Summary

- **Task** is preferred over **Thread** for most scenarios
- **ThreadPool** manages worker threads efficiently
- Use **Parallel** for CPU-bound parallelism
- Use **async/await** for I/O-bound operations
- Always consider **thread safety** when sharing state
- Use **concurrent collections** for thread-safe data structures

**Next:** [Semaphore](./05-Semaphore.md) | **Previous:** [APM Pattern](./03-APM-Pattern.md) | **Back to:** [README](./README.md)
