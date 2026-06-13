# Events (ManualResetEvent & AutoResetEvent)

Event-based synchronization primitives for signaling between threads.

## Table of Contents
- [Overview](#overview)
- [AutoResetEvent](#autoresetevent)
- [ManualResetEvent](#manualresetevent)
- [ManualResetEventSlim](#manualreseteventslim)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

Event wait handles provide a way for threads to signal each other. One or more threads wait for a signal, and another thread signals the event to release them.

**Key Concepts:**
- **Signaled State**: Event is "on", threads can proceed
- **Non-Signaled State**: Event is "off", threads wait
- **AutoReset**: Automatically resets after releasing one thread
- **ManualReset**: Remains signaled until manually reset

---

## AutoResetEvent

Automatically resets after releasing a single waiting thread.

### Basic Usage

```csharp
public class WorkQueue
{
    private readonly Queue<string> _queue = new Queue<string>();
    private readonly AutoResetEvent _itemAvailable = new AutoResetEvent(false);
    private readonly object _lock = new object();
    
    public void Enqueue(string item)
    {
        lock (_lock)
        {
            _queue.Enqueue(item);
            Console.WriteLine($"Enqueued: {item}");
        }
        _itemAvailable.Set(); // Signal that item is available
    }
    
    public string Dequeue()
    {
        _itemAvailable.WaitOne(); // Wait for signal
        lock (_lock)
        {
            return _queue.Dequeue();
        }
    }
    
    public void Dispose()
    {
        _itemAvailable?.Dispose();
    }
}

// Usage: Producer-Consumer
var queue = new WorkQueue();

// Producer
var producer = Task.Run(() =>
{
    for (int i = 0; i < 5; i++)
    {
        queue.Enqueue($"Item {i}");
        Thread.Sleep(500);
    }
});

// Consumer
var consumer = Task.Run(() =>
{
    for (int i = 0; i < 5; i++)
    {
        string item = queue.Dequeue();
        Console.WriteLine($"Dequeued: {item}");
    }
});

await Task.WhenAll(producer, consumer);
queue.Dispose();
```

### With Timeout

```csharp
public class TimeoutQueue
{
    private readonly Queue<string> _queue = new Queue<string>();
    private readonly AutoResetEvent _signal = new AutoResetEvent(false);
    private readonly object _lock = new object();
    
    public void Enqueue(string item)
    {
        lock (_lock)
        {
            _queue.Enqueue(item);
        }
        _signal.Set();
    }
    
    public bool TryDequeue(out string item, TimeSpan timeout)
    {
        if (_signal.WaitOne(timeout))
        {
            lock (_lock)
            {
                if (_queue.Count > 0)
                {
                    item = _queue.Dequeue();
                    return true;
                }
            }
        }
        
        item = null;
        return false;
    }
}

// Usage
var queue = new TimeoutQueue();
queue.Enqueue("Item 1");

if (queue.TryDequeue(out string item, TimeSpan.FromSeconds(5)))
{
    Console.WriteLine($"Got: {item}");
}
else
{
    Console.WriteLine("Timeout waiting for item");
}
```

### Thread Pool Work

```csharp
public class ThreadPoolCoordinator
{
    private readonly AutoResetEvent _workReady = new AutoResetEvent(false);
    private readonly Queue<Action> _workItems = new Queue<Action>();
    private readonly object _lock = new object();
    private bool _shutdown;
    
    public ThreadPoolCoordinator()
    {
        // Start worker thread
        Task.Run(() => WorkerThread());
    }
    
    public void QueueWork(Action work)
    {
        lock (_lock)
        {
            _workItems.Enqueue(work);
        }
        _workReady.Set(); // Signal worker
    }
    
    private void WorkerThread()
    {
        while (!_shutdown)
        {
            _workReady.WaitOne(); // Wait for work
            
            Action work = null;
            lock (_lock)
            {
                if (_workItems.Count > 0)
                {
                    work = _workItems.Dequeue();
                }
            }
            
            work?.Invoke();
        }
    }
    
    public void Shutdown()
    {
        _shutdown = true;
        _workReady.Set(); // Wake up worker to check shutdown
    }
}
```

---

## ManualResetEvent

Remains signaled until manually reset, releasing all waiting threads.

### Basic Usage

```csharp
public class StartGate
{
    private readonly ManualResetEvent _startGate = new ManualResetEvent(false);
    
    public void WaitForStart()
    {
        Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} waiting...");
        _startGate.WaitOne();
        Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} started!");
    }
    
    public void Open()
    {
        Console.WriteLine("Opening gate - all threads go!");
        _startGate.Set();
    }
    
    public void Close()
    {
        _startGate.Reset();
    }
    
    public void Dispose()
    {
        _startGate?.Dispose();
    }
}

// Usage: Coordinate simultaneous start of multiple threads
var gate = new StartGate();

var tasks = Enumerable.Range(0, 5).Select(i => Task.Run(() =>
{
    gate.WaitForStart();
    // All threads start simultaneously
    Console.WriteLine($"Task {i} executing at {DateTime.Now:HH:mm:ss.fff}");
})).ToArray();

Thread.Sleep(2000); // Wait before opening gate
gate.Open(); // All threads start at once

await Task.WhenAll(tasks);
gate.Dispose();
```

### Service Initialization

```csharp
public class Service
{
    private readonly ManualResetEvent _initialized = new ManualResetEvent(false);
    private bool _isInitialized;
    
    public void Initialize()
    {
        Console.WriteLine("Initializing service...");
        Thread.Sleep(2000); // Simulate initialization
        
        _isInitialized = true;
        _initialized.Set(); // Signal initialization complete
        Console.WriteLine("Service initialized");
    }
    
    public void WaitForInitialization()
    {
        if (!_isInitialized)
        {
            Console.WriteLine("Waiting for initialization...");
            _initialized.WaitOne();
        }
    }
    
    public void DoWork()
    {
        WaitForInitialization();
        Console.WriteLine("Doing work...");
    }
    
    public void Dispose()
    {
        _initialized?.Dispose();
    }
}

// Usage: Multiple threads wait for service to initialize
var service = new Service();

// Start initialization in background
var initTask = Task.Run(() => service.Initialize());

// Multiple workers wait for initialization
var workers = Enumerable.Range(0, 5).Select(i => Task.Run(() =>
{
    service.DoWork(); // Will wait for initialization
})).ToArray();

await Task.WhenAll(workers.Concat(new[] { initTask }));
```

### Pause/Resume Pattern

```csharp
public class PausableWorker
{
    private readonly ManualResetEvent _pauseEvent = new ManualResetEvent(true);
    private bool _shouldStop;
    
    public void Pause()
    {
        Console.WriteLine("Pausing...");
        _pauseEvent.Reset();
    }
    
    public void Resume()
    {
        Console.WriteLine("Resuming...");
        _pauseEvent.Set();
    }
    
    public void Stop()
    {
        _shouldStop = true;
        Resume(); // Ensure not blocked
    }
    
    public void DoWork()
    {
        for (int i = 0; !_shouldStop; i++)
        {
            _pauseEvent.WaitOne(); // Wait if paused
            
            if (_shouldStop) break;
            
            Console.WriteLine($"Working: {i}");
            Thread.Sleep(500);
        }
        
        Console.WriteLine("Worker stopped");
    }
}

// Usage
var worker = new PausableWorker();
var workerTask = Task.Run(() => worker.DoWork());

await Task.Delay(2000);
worker.Pause();

await Task.Delay(2000);
worker.Resume();

await Task.Delay(2000);
worker.Stop();

await workerTask;
```

---

## ManualResetEventSlim

Lightweight version for shorter wait times.

### Basic Usage

```csharp
public class LightweightGate
{
    private readonly ManualResetEventSlim _gate = new ManualResetEventSlim(false);
    
    public void Wait()
    {
        _gate.Wait();
    }
    
    public bool Wait(TimeSpan timeout)
    {
        return _gate.Wait(timeout);
    }
    
    public void Open()
    {
        _gate.Set();
    }
    
    public void Close()
    {
        _gate.Reset();
    }
    
    public bool IsSet => _gate.IsSet;
    
    public void Dispose()
    {
        _gate?.Dispose();
    }
}

// Usage: Better performance for short waits
var gate = new LightweightGate();

var tasks = Enumerable.Range(0, 10).Select(i => Task.Run(() =>
{
    Console.WriteLine($"Task {i} waiting");
    gate.Wait();
    Console.WriteLine($"Task {i} proceeding");
})).ToArray();

Thread.Sleep(1000);
gate.Open();

await Task.WhenAll(tasks);
gate.Dispose();
```

### With Cancellation

```csharp
public void WaitWithCancellation(CancellationToken cancellationToken)
{
    var gate = new ManualResetEventSlim(false);
    
    try
    {
        // Wait with cancellation support
        gate.Wait(cancellationToken);
    }
    catch (OperationCanceledException)
    {
        Console.WriteLine("Wait was cancelled");
    }
    finally
    {
        gate.Dispose();
    }
}
```

---

## Use Cases

### 1. Producer-Consumer with Multiple Consumers

```csharp
public class WorkDispatcher
{
    private readonly Queue<Action> _workQueue = new Queue<Action>();
    private readonly AutoResetEvent _workAvailable = new AutoResetEvent(false);
    private readonly object _lock = new object();
    private bool _shutdown;
    
    public void AddWork(Action work)
    {
        lock (_lock)
        {
            _workQueue.Enqueue(work);
        }
        _workAvailable.Set();
    }
    
    public void Worker(int workerId)
    {
        while (true)
        {
            _workAvailable.WaitOne();
            
            if (_shutdown) break;
            
            Action work = null;
            lock (_lock)
            {
                if (_workQueue.Count > 0)
                {
                    work = _workQueue.Dequeue();
                }
                else if (_workQueue.Count > 0)
                {
                    // More work available, signal next worker
                    _workAvailable.Set();
                }
            }
            
            if (work != null)
            {
                Console.WriteLine($"Worker {workerId} executing work");
                work();
            }
        }
    }
    
    public void Shutdown()
    {
        _shutdown = true;
        _workAvailable.Set(); // Wake up all workers
    }
}

// Usage
var dispatcher = new WorkDispatcher();

// Start workers
var workers = Enumerable.Range(0, 3).Select(i => 
    Task.Run(() => dispatcher.Worker(i))).ToArray();

// Add work
for (int i = 0; i < 10; i++)
{
    int taskId = i;
    dispatcher.AddWork(() =>
    {
        Console.WriteLine($"Executing task {taskId}");
        Thread.Sleep(500);
    });
}

Thread.Sleep(6000);
dispatcher.Shutdown();
```

### 2. Batch Processing Coordinator

```csharp
public class BatchCoordinator
{
    private readonly ManualResetEvent _batchReady = new ManualResetEvent(false);
    private readonly List<string> _batch = new List<string>();
    private readonly object _lock = new object();
    private const int BatchSize = 5;
    
    public void AddItem(string item)
    {
        bool shouldSignal = false;
        
        lock (_lock)
        {
            _batch.Add(item);
            Console.WriteLine($"Added {item} ({_batch.Count}/{BatchSize})");
            
            if (_batch.Count >= BatchSize)
            {
                shouldSignal = true;
            }
        }
        
        if (shouldSignal)
        {
            _batchReady.Set();
        }
    }
    
    public List<string> WaitForBatch()
    {
        _batchReady.WaitOne();
        
        lock (_lock)
        {
            var result = new List<string>(_batch);
            _batch.Clear();
            _batchReady.Reset();
            return result;
        }
    }
}

// Usage
var coordinator = new BatchCoordinator();

// Processor waits for full batches
var processor = Task.Run(() =>
{
    for (int i = 0; i < 3; i++)
    {
        var batch = coordinator.WaitForBatch();
        Console.WriteLine($"Processing batch of {batch.Count} items");
        Thread.Sleep(1000);
    }
});

// Producer adds items
var producer = Task.Run(() =>
{
    for (int i = 0; i < 15; i++)
    {
        coordinator.AddItem($"Item{i}");
        Thread.Sleep(200);
    }
});

await Task.WhenAll(processor, producer);
```

### 3. Application Startup Coordination

```csharp
public class ApplicationStartup
{
    private readonly ManualResetEvent _configLoaded = new ManualResetEvent(false);
    private readonly ManualResetEvent _databaseReady = new ManualResetEvent(false);
    private readonly ManualResetEvent _cacheWarmed = new ManualResetEvent(false);
    
    public void LoadConfiguration()
    {
        Console.WriteLine("Loading configuration...");
        Thread.Sleep(1000);
        _configLoaded.Set();
        Console.WriteLine("Configuration loaded");
    }
    
    public void InitializeDatabase()
    {
        _configLoaded.WaitOne(); // Wait for config
        Console.WriteLine("Initializing database...");
        Thread.Sleep(1500);
        _databaseReady.Set();
        Console.WriteLine("Database ready");
    }
    
    public void WarmupCache()
    {
        _databaseReady.WaitOne(); // Wait for database
        Console.WriteLine("Warming up cache...");
        Thread.Sleep(1000);
        _cacheWarmed.Set();
        Console.WriteLine("Cache warmed");
    }
    
    public void WaitForStartup()
    {
        WaitHandle.WaitAll(new[] { _configLoaded, _databaseReady, _cacheWarmed });
        Console.WriteLine("Application startup complete!");
    }
}

// Usage
var startup = new ApplicationStartup();

var tasks = new[]
{
    Task.Run(() => startup.LoadConfiguration()),
    Task.Run(() => startup.InitializeDatabase()),
    Task.Run(() => startup.WarmupCache())
};

startup.WaitForStartup();
Console.WriteLine("Application ready to serve requests");
```

---

## Best Practices

### 1. Dispose Events

```csharp
public class EventManager : IDisposable
{
    private readonly ManualResetEvent _event = new ManualResetEvent(false);
    
    public void Dispose()
    {
        _event?.Dispose();
    }
}

// Or use using statement
using (var evt = new ManualResetEvent(false))
{
    // Use event
}
```

### 2. Choose Right Event Type

```csharp
// ✅ AutoResetEvent - One thread at a time
// Good for: Work queues, one-at-a-time processing

// ✅ ManualResetEvent - All waiting threads
// Good for: Start gates, initialization flags

// ✅ ManualResetEventSlim - Short waits, better performance
// Good for: In-process coordination with short wait times
```

### 3. Avoid Deadlocks with Timeouts

```csharp
// ✅ Good - Use timeout
if (!_event.WaitOne(TimeSpan.FromSeconds(30)))
{
    throw new TimeoutException("Operation timed out");
}

// ❌ Risky - Infinite wait
_event.WaitOne(); // Could block forever
```

### 4. Use WaitHandle.WaitAll/WaitAny

```csharp
var events = new WaitHandle[] 
{ 
    event1, 
    event2, 
    event3 
};

// Wait for all
WaitHandle.WaitAll(events);

// Wait for any one
int index = WaitHandle.WaitAny(events);
Console.WriteLine($"Event {index} was signaled");
```

### 5. Prefer Async Alternatives When Possible

```csharp
// ⚠️ Events block threads
var mre = new ManualResetEvent(false);
mre.WaitOne(); // Blocks thread

// ✅ Better for async code
var tcs = new TaskCompletionSource<bool>();
await tcs.Task; // Doesn't block thread
```

---

## Events vs Other Synchronization

| Feature | AutoResetEvent | ManualResetEvent | SemaphoreSlim | Monitor.Wait/Pulse |
|---------|----------------|------------------|---------------|-------------------|
| Multiple Waiters | One at a time | All released | Up to count | One or all |
| Auto Reset | ✅ Yes | ❌ No | ❌ No | ❌ No |
| Cross-Process | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Async Support | ❌ No | ❌ No | ✅ Yes | ❌ No |
| Performance | Medium | Medium | Fast | Fastest |

---

## Summary

- **AutoResetEvent**: One waiting thread released, auto-resets
- **ManualResetEvent**: All waiting threads released, manual reset
- **ManualResetEventSlim**: Lightweight version for short waits
- Good for thread signaling and coordination
- Always dispose when done
- Consider async alternatives (Task, TaskCompletionSource) for modern code

**Next:** [Barrier](./10-Barrier.md) | **Previous:** [ReaderWriterLockSlim](./08-ReaderWriterLock.md) | **Back to:** [README](./README.md)
