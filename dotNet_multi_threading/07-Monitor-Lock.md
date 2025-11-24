# Monitor and Lock

The `lock` keyword is syntactic sugar for `Monitor.Enter` and `Monitor.Exit`. Used for protecting critical sections within a single process.

## Table of Contents
- [Overview](#overview)
- [Lock Statement](#lock-statement)
- [Monitor Class](#monitor-class)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

Monitor and lock provide mutual exclusion for thread synchronization within a single process. The `lock` statement is the preferred way to use Monitor in most scenarios.

**Key Concepts:**
- **Critical Section**: Code that must not execute concurrently
- **Lock Object**: Reference type used as synchronization point
- **Ownership**: Only one thread can hold the lock at a time
- **Reentrancy**: Same thread can acquire lock multiple times

---

## Lock Statement

### Basic Usage

```csharp
public class BankAccount
{
    private decimal _balance;
    private readonly object _lock = new object();
    
    public void Deposit(decimal amount)
    {
        lock (_lock)
        {
            decimal temp = _balance;
            Thread.Sleep(1); // Simulate work
            _balance = temp + amount;
            Console.WriteLine($"Deposited {amount:C}, Balance: {_balance:C}");
        }
    }
    
    public bool Withdraw(decimal amount)
    {
        lock (_lock)
        {
            if (_balance >= amount)
            {
                decimal temp = _balance;
                Thread.Sleep(1); // Simulate work
                _balance = temp - amount;
                Console.WriteLine($"Withdrew {amount:C}, Balance: {_balance:C}");
                return true;
            }
            
            Console.WriteLine($"Insufficient funds for {amount:C}");
            return false;
        }
    }
    
    public decimal GetBalance()
    {
        lock (_lock)
        {
            return _balance;
        }
    }
}

// Usage
var account = new BankAccount();

var tasks = new[]
{
    Task.Run(() => account.Deposit(100)),
    Task.Run(() => account.Deposit(50)),
    Task.Run(() => account.Withdraw(30)),
    Task.Run(() => account.Withdraw(20))
};

await Task.WhenAll(tasks);
Console.WriteLine($"Final balance: {account.GetBalance():C}");
```

### Thread-Safe Counter

```csharp
public class Counter
{
    private int _count;
    private readonly object _lock = new object();
    
    public void Increment()
    {
        lock (_lock)
        {
            _count++;
        }
    }
    
    public void Decrement()
    {
        lock (_lock)
        {
            _count--;
        }
    }
    
    public int GetValue()
    {
        lock (_lock)
        {
            return _count;
        }
    }
    
    public void Add(int value)
    {
        lock (_lock)
        {
            _count += value;
        }
    }
}

// Usage
var counter = new Counter();

Parallel.For(0, 1000, i =>
{
    counter.Increment();
});

Console.WriteLine($"Counter: {counter.GetValue()}"); // Will be 1000
```

### Thread-Safe Collection Wrapper

```csharp
public class SafeList<T>
{
    private readonly List<T> _list = new List<T>();
    private readonly object _lock = new object();
    
    public void Add(T item)
    {
        lock (_lock)
        {
            _list.Add(item);
        }
    }
    
    public bool Remove(T item)
    {
        lock (_lock)
        {
            return _list.Remove(item);
        }
    }
    
    public T[] ToArray()
    {
        lock (_lock)
        {
            return _list.ToArray();
        }
    }
    
    public int Count
    {
        get
        {
            lock (_lock)
            {
                return _list.Count;
            }
        }
    }
    
    public void ForEach(Action<T> action)
    {
        T[] snapshot;
        lock (_lock)
        {
            snapshot = _list.ToArray();
        }
        
        // Process outside lock to avoid deadlocks
        foreach (var item in snapshot)
        {
            action(item);
        }
    }
}

// Usage
var list = new SafeList<int>();

Parallel.For(0, 100, i =>
{
    list.Add(i);
});

Console.WriteLine($"Added {list.Count} items");

list.ForEach(item => Console.WriteLine(item));
```

---

## Monitor Class

### Monitor.TryEnter

```csharp
public class ResourceManager
{
    private readonly object _lock = new object();
    
    public bool TryProcessResource(TimeSpan timeout)
    {
        if (Monitor.TryEnter(_lock, timeout))
        {
            try
            {
                // Critical section
                Console.WriteLine("Processing resource");
                Thread.Sleep(2000);
                return true;
            }
            finally
            {
                Monitor.Exit(_lock);
            }
        }
        
        Console.WriteLine("Could not acquire lock within timeout");
        return false;
    }
}

// Usage
var manager = new ResourceManager();

var tasks = Enumerable.Range(0, 5).Select(i => Task.Run(() =>
{
    if (manager.TryProcessResource(TimeSpan.FromSeconds(1)))
    {
        Console.WriteLine($"Task {i} completed");
    }
    else
    {
        Console.WriteLine($"Task {i} timed out");
    }
})).ToArray();

Task.WaitAll(tasks);
```

### Monitor.Wait and Pulse (Producer-Consumer)

```csharp
public class MessageQueue
{
    private readonly Queue<string> _queue = new Queue<string>();
    private readonly object _lock = new object();
    
    public void Enqueue(string message)
    {
        lock (_lock)
        {
            _queue.Enqueue(message);
            Console.WriteLine($"Enqueued: {message}");
            Monitor.Pulse(_lock); // Signal one waiting thread
        }
    }
    
    public string Dequeue()
    {
        lock (_lock)
        {
            while (_queue.Count == 0)
            {
                Console.WriteLine("Queue empty, waiting...");
                Monitor.Wait(_lock); // Release lock and wait for signal
            }
            
            string message = _queue.Dequeue();
            Console.WriteLine($"Dequeued: {message}");
            return message;
        }
    }
    
    public int Count
    {
        get
        {
            lock (_lock)
            {
                return _queue.Count;
            }
        }
    }
}

// Usage: Producer-Consumer pattern
var queue = new MessageQueue();

// Producer
var producer = Task.Run(() =>
{
    for (int i = 0; i < 5; i++)
    {
        Thread.Sleep(500);
        queue.Enqueue($"Message {i}");
    }
});

// Consumers
var consumers = Enumerable.Range(0, 3).Select(id => Task.Run(() =>
{
    for (int i = 0; i < 2; i++)
    {
        string message = queue.Dequeue();
        Console.WriteLine($"Consumer {id} got: {message}");
    }
})).ToArray();

await Task.WhenAll(consumers.Concat(new[] { producer }));
```

### Monitor.PulseAll

```csharp
public class EventBroadcaster
{
    private readonly object _lock = new object();
    private bool _eventRaised;
    
    public void WaitForEvent()
    {
        lock (_lock)
        {
            while (!_eventRaised)
            {
                Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} waiting...");
                Monitor.Wait(_lock);
            }
            
            Console.WriteLine($"Thread {Thread.CurrentThread.ManagedThreadId} received event");
        }
    }
    
    public void RaiseEvent()
    {
        lock (_lock)
        {
            _eventRaised = true;
            Console.WriteLine("Event raised - notifying all threads");
            Monitor.PulseAll(_lock); // Wake up all waiting threads
        }
    }
    
    public void Reset()
    {
        lock (_lock)
        {
            _eventRaised = false;
        }
    }
}

// Usage
var broadcaster = new EventBroadcaster();

// Start multiple waiting threads
var waiters = Enumerable.Range(0, 5).Select(i => Task.Run(() =>
{
    broadcaster.WaitForEvent();
})).ToArray();

// Wait a bit, then raise event
await Task.Delay(2000);
broadcaster.RaiseEvent();

await Task.WhenAll(waiters);
```

---

## Use Cases

### 1. Singleton Pattern (Thread-Safe)

```csharp
public sealed class Singleton
{
    private static Singleton _instance;
    private static readonly object _lock = new object();
    
    private Singleton()
    {
        // Private constructor
        Console.WriteLine("Singleton instance created");
    }
    
    public static Singleton Instance
    {
        get
        {
            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                    {
                        _instance = new Singleton();
                    }
                }
            }
            
            return _instance;
        }
    }
    
    public void DoWork()
    {
        Console.WriteLine("Singleton doing work");
    }
}

// Usage: Safe in multithreaded environment
Parallel.For(0, 10, i =>
{
    var instance = Singleton.Instance;
    instance.DoWork();
});
```

### 2. Lazy Initialization

```csharp
public class ExpensiveResource
{
    private ExpensiveObject _resource;
    private readonly object _lock = new object();
    
    public ExpensiveObject Resource
    {
        get
        {
            if (_resource == null)
            {
                lock (_lock)
                {
                    if (_resource == null)
                    {
                        Console.WriteLine("Initializing expensive resource...");
                        Thread.Sleep(1000); // Simulate expensive initialization
                        _resource = new ExpensiveObject();
                    }
                }
            }
            
            return _resource;
        }
    }
}

// Better: Use Lazy<T>
public class ExpensiveResource
{
    private readonly Lazy<ExpensiveObject> _resource = 
        new Lazy<ExpensiveObject>(() =>
        {
            Console.WriteLine("Initializing expensive resource...");
            Thread.Sleep(1000);
            return new ExpensiveObject();
        });
    
    public ExpensiveObject Resource => _resource.Value;
}
```

### 3. Cache with Expiration

```csharp
public class TimedCache<TKey, TValue>
{
    private readonly Dictionary<TKey, CacheEntry> _cache = new Dictionary<TKey, CacheEntry>();
    private readonly object _lock = new object();
    private readonly TimeSpan _expirationTime;
    
    private class CacheEntry
    {
        public TValue Value { get; set; }
        public DateTime ExpirationTime { get; set; }
    }
    
    public TimedCache(TimeSpan expirationTime)
    {
        _expirationTime = expirationTime;
    }
    
    public void Add(TKey key, TValue value)
    {
        lock (_lock)
        {
            _cache[key] = new CacheEntry
            {
                Value = value,
                ExpirationTime = DateTime.UtcNow.Add(_expirationTime)
            };
        }
    }
    
    public bool TryGet(TKey key, out TValue value)
    {
        lock (_lock)
        {
            if (_cache.TryGetValue(key, out var entry))
            {
                if (DateTime.UtcNow < entry.ExpirationTime)
                {
                    value = entry.Value;
                    return true;
                }
                
                // Expired, remove it
                _cache.Remove(key);
            }
            
            value = default;
            return false;
        }
    }
    
    public void Clear()
    {
        lock (_lock)
        {
            _cache.Clear();
        }
    }
}

// Usage
var cache = new TimedCache<string, string>(TimeSpan.FromSeconds(5));

cache.Add("key1", "value1");

if (cache.TryGet("key1", out string value))
{
    Console.WriteLine($"Found: {value}");
}
```

### 4. Event Aggregator

```csharp
public class EventAggregator
{
    private readonly Dictionary<Type, List<Delegate>> _handlers = 
        new Dictionary<Type, List<Delegate>>();
    private readonly object _lock = new object();
    
    public void Subscribe<T>(Action<T> handler)
    {
        lock (_lock)
        {
            if (!_handlers.TryGetValue(typeof(T), out var handlers))
            {
                handlers = new List<Delegate>();
                _handlers[typeof(T)] = handlers;
            }
            
            handlers.Add(handler);
        }
    }
    
    public void Publish<T>(T message)
    {
        List<Delegate> handlersCopy;
        
        lock (_lock)
        {
            if (!_handlers.TryGetValue(typeof(T), out var handlers))
                return;
            
            handlersCopy = new List<Delegate>(handlers);
        }
        
        // Invoke outside lock to avoid deadlocks
        foreach (var handler in handlersCopy)
        {
            ((Action<T>)handler)(message);
        }
    }
}

// Usage
var aggregator = new EventAggregator();

aggregator.Subscribe<string>(msg => Console.WriteLine($"Handler 1: {msg}"));
aggregator.Subscribe<string>(msg => Console.WriteLine($"Handler 2: {msg}"));

aggregator.Publish("Hello, World!");
```

---

## Best Practices

### 1. Use Private Lock Object

```csharp
// ✅ Good - Private lock object
public class MyClass
{
    private readonly object _lock = new object();
    
    public void DoWork()
    {
        lock (_lock)
        {
            // Critical section
        }
    }
}

// ❌ Bad - Locking on this
public class MyClass
{
    public void DoWork()
    {
        lock (this) // External code can lock on this too!
        {
            // Critical section
        }
    }
}
```

### 2. Keep Lock Duration Short

```csharp
// ❌ Bad - Long lock duration
lock (_lock)
{
    var data = ReadDataFromDatabase(); // Slow I/O inside lock
    ProcessData(data);
    SaveToDatabase(data);
}

// ✅ Good - Minimal lock duration
var data = ReadDataFromDatabase();

lock (_lock)
{
    ProcessData(data); // Only thread-unsafe operation in lock
}

SaveToDatabase(data);
```

### 3. Avoid Calling External Code in Lock

```csharp
// ❌ Bad - External code in lock (can cause deadlocks)
lock (_lock)
{
    externalObject.Method(); // Unknown behavior
}

// ✅ Good - Copy data, then call external code
T dataCopy;
lock (_lock)
{
    dataCopy = _data.Clone();
}

externalObject.Method(dataCopy);
```

### 4. Don't Lock on String or Type

```csharp
// ❌ Bad - String literals are interned
private const string _lockString = "MyLock";
lock (_lockString) { } // All code with same string shares lock!

// ❌ Bad - Type objects are global
lock (typeof(MyClass)) { }

// ✅ Good - Private object instance
private readonly object _lock = new object();
lock (_lock) { }
```

### 5. Use lock Over Monitor When Possible

```csharp
// ✅ Preferred - lock statement
lock (_lock)
{
    // Critical section
}

// ⚠️ Only use Monitor when you need advanced features
bool lockTaken = false;
try
{
    Monitor.TryEnter(_lock, timeout, ref lockTaken);
    if (lockTaken)
    {
        // Critical section
    }
}
finally
{
    if (lockTaken)
        Monitor.Exit(_lock);
}
```

### 6. Avoid Nested Locks (Deadlock Risk)

```csharp
// ❌ Bad - Nested locks can cause deadlocks
object lock1 = new object();
object lock2 = new object();

// Thread 1
lock (lock1)
{
    lock (lock2) // Can deadlock with Thread 2
    {
        // Work
    }
}

// Thread 2
lock (lock2)
{
    lock (lock1) // Can deadlock with Thread 1
    {
        // Work
    }
}

// ✅ Good - Always acquire locks in same order
lock (lock1)
{
    lock (lock2)
    {
        // Work
    }
}
```

### 7. Consider lock-free alternatives

```csharp
// For simple operations, use Interlocked
private int _counter;
Interlocked.Increment(ref _counter);

// For collections, use concurrent collections
private readonly ConcurrentDictionary<string, int> _dict = 
    new ConcurrentDictionary<string, int>();
```

---

## Lock vs Other Synchronization

| Feature | lock/Monitor | Mutex | SemaphoreSlim |
|---------|-------------|--------|---------------|
| Cross-Process | ❌ No | ✅ Yes | ❌ No |
| Async Support | ❌ No | ❌ No | ✅ Yes |
| Performance | ⚡ Fastest | Slower | Fast |
| Multiple Entries | ❌ No (1) | ❌ No (1) | ✅ Yes (N) |
| Recursion | ✅ Yes | ✅ Yes | ❌ No |
| Best For | Critical sections | Cross-process | Throttling |

---

## Summary

- **lock**: Preferred for most single-process synchronization
- **Monitor**: Low-level alternative with advanced features (Wait/Pulse)
- Fast and efficient within single process
- Always use private lock objects
- Keep lock duration minimal
- Avoid external calls within locks
- Watch for deadlocks with nested locks

**Next:** [ReaderWriterLockSlim](./08-ReaderWriterLock.md) | **Previous:** [Mutex](./06-Mutex.md) | **Back to:** [README](./README.md)
