# Mutex

Provides mutual exclusion for cross-process synchronization. Only one thread can hold the mutex at a time.

## Table of Contents
- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Named Mutex (Cross-Process)](#named-mutex-cross-process)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

A Mutex (Mutual Exclusion) is a synchronization primitive that ensures only one thread can access a resource at a time. Unlike locks, mutexes can work across process boundaries.

**Key Concepts:**
- **Ownership**: Thread that acquires mutex "owns" it
- **Named Mutex**: Can be shared across processes
- **WaitOne**: Acquires the mutex (blocks if unavailable)
- **ReleaseMutex**: Releases ownership
- **Cross-Process**: Works across application instances

---

## Basic Usage

### Simple Mutex

```csharp
public void SimpleMutexExample()
{
    using (var mutex = new Mutex())
    {
        var tasks = Enumerable.Range(0, 5).Select(i => Task.Run(() =>
        {
            Console.WriteLine($"Task {i} waiting for mutex...");
            mutex.WaitOne(); // Acquire mutex
            try
            {
                Console.WriteLine($"Task {i} acquired mutex");
                Thread.Sleep(1000);
                Console.WriteLine($"Task {i} releasing mutex");
            }
            finally
            {
                mutex.ReleaseMutex(); // Release mutex
            }
        })).ToArray();
        
        Task.WaitAll(tasks);
    }
}
```

### Mutex with Timeout

```csharp
public class MutexWithTimeout
{
    private readonly Mutex _mutex = new Mutex();
    
    public bool TryExecute(Action action, TimeSpan timeout)
    {
        if (_mutex.WaitOne(timeout))
        {
            try
            {
                action();
                return true;
            }
            finally
            {
                _mutex.ReleaseMutex();
            }
        }
        
        Console.WriteLine("Could not acquire mutex within timeout");
        return false;
    }
    
    public void Dispose()
    {
        _mutex?.Dispose();
    }
}

// Usage
var mutexHelper = new MutexWithTimeout();

if (mutexHelper.TryExecute(() =>
{
    Console.WriteLine("Executing critical section");
    Thread.Sleep(2000);
}, TimeSpan.FromSeconds(5)))
{
    Console.WriteLine("Execution completed");
}
else
{
    Console.WriteLine("Timeout waiting for mutex");
}
```

---

## Named Mutex (Cross-Process)

### Single Instance Application

```csharp
public class SingleInstanceApp
{
    private static Mutex _mutex;
    
    public static bool TryAcquireSingleInstance(string appName)
    {
        try
        {
            // Try to create a new mutex with the given name
            _mutex = new Mutex(true, $"Global\\{appName}", out bool createdNew);
            return createdNew;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error creating mutex: {ex.Message}");
            return false;
        }
    }
    
    public static void ReleaseSingleInstance()
    {
        try
        {
            _mutex?.ReleaseMutex();
        }
        catch (ApplicationException)
        {
            // Mutex was not owned by this thread
        }
        finally
        {
            _mutex?.Dispose();
        }
    }
}

// Usage in Program.cs or Main
class Program
{
    static void Main(string[] args)
    {
        const string APP_NAME = "MyUniqueApplicationName";
        
        if (!SingleInstanceApp.TryAcquireSingleInstance(APP_NAME))
        {
            Console.WriteLine("Application is already running!");
            Console.WriteLine("Press any key to exit...");
            Console.ReadKey();
            return;
        }
        
        try
        {
            Console.WriteLine("Application started successfully");
            Console.WriteLine("Press any key to exit...");
            
            // Run your application
            RunApplication();
            
            Console.ReadKey();
        }
        finally
        {
            SingleInstanceApp.ReleaseSingleInstance();
        }
    }
    
    static void RunApplication()
    {
        // Your application logic here
        Console.WriteLine("Running application...");
    }
}
```

### Opening Existing Named Mutex

```csharp
public class NamedMutexHelper
{
    public static bool TryOpenExisting(string name, out Mutex mutex)
    {
        try
        {
            return Mutex.TryOpenExisting($"Global\\{name}", out mutex);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error opening mutex: {ex.Message}");
            mutex = null;
            return false;
        }
    }
    
    public static Mutex CreateOrOpen(string name)
    {
        return new Mutex(false, $"Global\\{name}");
    }
}

// Usage
if (NamedMutexHelper.TryOpenExisting("MyAppMutex", out Mutex existingMutex))
{
    Console.WriteLine("Mutex already exists");
    existingMutex.Dispose();
}
else
{
    Console.WriteLine("Mutex does not exist, creating new one");
    using (var mutex = NamedMutexHelper.CreateOrOpen("MyAppMutex"))
    {
        // Use mutex
    }
}
```

### Cross-Process Resource Protection

```csharp
public class SharedResourceManager
{
    private readonly Mutex _mutex;
    private readonly string _resourceName;
    
    public SharedResourceManager(string resourceName)
    {
        _resourceName = resourceName;
        _mutex = new Mutex(false, $"Global\\{resourceName}_Mutex");
    }
    
    public void AccessResource(Action<string> action)
    {
        Console.WriteLine($"Process {Process.GetCurrentProcess().Id}: Waiting for mutex...");
        
        _mutex.WaitOne();
        try
        {
            Console.WriteLine($"Process {Process.GetCurrentProcess().Id}: Acquired mutex");
            action(_resourceName);
            Thread.Sleep(1000); // Simulate work
        }
        finally
        {
            Console.WriteLine($"Process {Process.GetCurrentProcess().Id}: Releasing mutex");
            _mutex.ReleaseMutex();
        }
    }
    
    public void Dispose()
    {
        _mutex?.Dispose();
    }
}

// Usage: Run this in multiple instances
var manager = new SharedResourceManager("SharedFile");

manager.AccessResource(resourceName =>
{
    Console.WriteLine($"Accessing shared resource: {resourceName}");
    // Only one process can execute this at a time
    File.AppendAllText($"{resourceName}.txt", 
        $"Process {Process.GetCurrentProcess().Id} accessed at {DateTime.Now}\n");
});

manager.Dispose();
```

---

## Use Cases

### 1. Single Instance Application

Prevent multiple instances of your application from running simultaneously.

```csharp
public class SingleInstanceManager : IDisposable
{
    private readonly Mutex _mutex;
    private readonly bool _hasHandle;
    
    public SingleInstanceManager(string uniqueAppId)
    {
        _mutex = new Mutex(true, $"Global\\{uniqueAppId}", out _hasHandle);
    }
    
    public bool IsFirstInstance => _hasHandle;
    
    public void Dispose()
    {
        if (_hasHandle)
        {
            _mutex?.ReleaseMutex();
        }
        _mutex?.Dispose();
    }
}

// Usage
using (var instanceManager = new SingleInstanceManager("MyApp_v1.0"))
{
    if (!instanceManager.IsFirstInstance)
    {
        MessageBox.Show("Application is already running!");
        return;
    }
    
    // Run application
    Application.Run(new MainForm());
}
```

### 2. Protecting Shared File Access

```csharp
public class SharedFileWriter
{
    private readonly Mutex _mutex;
    private readonly string _filePath;
    
    public SharedFileWriter(string filePath)
    {
        _filePath = filePath;
        var mutexName = $"Global\\FileWriter_{Path.GetFileName(filePath)}";
        _mutex = new Mutex(false, mutexName);
    }
    
    public void WriteToFile(string content)
    {
        _mutex.WaitOne();
        try
        {
            // Safe to write - no other process can write simultaneously
            File.AppendAllText(_filePath, content + Environment.NewLine);
            Console.WriteLine($"Written: {content}");
        }
        finally
        {
            _mutex.ReleaseMutex();
        }
    }
    
    public void Dispose()
    {
        _mutex?.Dispose();
    }
}

// Usage across multiple processes
var writer = new SharedFileWriter("shared-log.txt");

for (int i = 0; i < 10; i++)
{
    writer.WriteToFile($"Process {Process.GetCurrentProcess().Id}: Entry {i}");
    Thread.Sleep(100);
}

writer.Dispose();
```

### 3. License Management

```csharp
public class LicenseManager
{
    private readonly Mutex _licenseMutex;
    private readonly int _maxConcurrentUsers;
    
    public LicenseManager(string productName, int maxConcurrentUsers)
    {
        _maxConcurrentUsers = maxConcurrentUsers;
        _licenseMutex = new Mutex(false, $"Global\\{productName}_License");
    }
    
    public bool TryAcquireLicense(TimeSpan timeout)
    {
        Console.WriteLine("Attempting to acquire license...");
        
        if (_licenseMutex.WaitOne(timeout))
        {
            Console.WriteLine("License acquired successfully");
            return true;
        }
        
        Console.WriteLine("All licenses are in use. Please try again later.");
        return false;
    }
    
    public void ReleaseLicense()
    {
        try
        {
            _licenseMutex.ReleaseMutex();
            Console.WriteLine("License released");
        }
        catch (ApplicationException)
        {
            Console.WriteLine("License was not acquired by this instance");
        }
    }
    
    public void Dispose()
    {
        _licenseMutex?.Dispose();
    }
}

// Usage
var licenseManager = new LicenseManager("MyProduct", maxConcurrentUsers: 5);

if (licenseManager.TryAcquireLicense(TimeSpan.FromSeconds(10)))
{
    try
    {
        // Use the application
        Console.WriteLine("Application running...");
        Thread.Sleep(5000);
    }
    finally
    {
        licenseManager.ReleaseLicense();
    }
}
else
{
    Console.WriteLine("Could not acquire license");
}

licenseManager.Dispose();
```

### 4. Database Schema Migration Lock

```csharp
public class MigrationManager
{
    private readonly Mutex _migrationMutex;
    
    public MigrationManager(string databaseName)
    {
        _migrationMutex = new Mutex(false, $"Global\\DBMigration_{databaseName}");
    }
    
    public void RunMigrations(Action migrationAction)
    {
        Console.WriteLine("Waiting to acquire migration lock...");
        _migrationMutex.WaitOne();
        
        try
        {
            Console.WriteLine("Migration lock acquired - running migrations");
            migrationAction();
            Console.WriteLine("Migrations completed");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Migration failed: {ex.Message}");
            throw;
        }
        finally
        {
            _migrationMutex.ReleaseMutex();
            Console.WriteLine("Migration lock released");
        }
    }
    
    public void Dispose()
    {
        _migrationMutex?.Dispose();
    }
}

// Usage: Multiple app instances will wait for migrations to complete
var migrationManager = new MigrationManager("MyDatabase");

migrationManager.RunMigrations(() =>
{
    // Run database migrations
    // Only one instance across all processes can run this
    Console.WriteLine("Applying migration 001...");
    Thread.Sleep(1000);
    Console.WriteLine("Applying migration 002...");
    Thread.Sleep(1000);
});

migrationManager.Dispose();
```

---

## Best Practices

### 1. Always Release in Finally Block

```csharp
// ✅ Good
mutex.WaitOne();
try
{
    // Critical section
}
finally
{
    mutex.ReleaseMutex();
}
```

### 2. Handle Abandoned Mutexes

```csharp
public void SafeMutexAcquisition(Mutex mutex)
{
    try
    {
        mutex.WaitOne();
    }
    catch (AbandonedMutexException ex)
    {
        // Previous owner terminated without releasing
        Console.WriteLine("Mutex was abandoned - recovering");
        // Mutex is now acquired, continue safely
    }
    
    try
    {
        // Critical section
    }
    finally
    {
        mutex.ReleaseMutex();
    }
}
```

### 3. Use Global Prefix for Cross-Process

```csharp
// ✅ Good - Works across user sessions
var mutex = new Mutex(false, "Global\\MyAppMutex");

// ⚠️ Limited - Only within same user session
var mutex = new Mutex(false, "Local\\MyAppMutex");
```

### 4. Prefer Lock for Single-Process

```csharp
// ❌ Don't use Mutex for single-process synchronization
private readonly Mutex _mutex = new Mutex();

// ✅ Use lock instead (faster, lighter)
private readonly object _lock = new object();

lock (_lock)
{
    // Critical section
}
```

### 5. Dispose Properly

```csharp
public class MutexManager : IDisposable
{
    private readonly Mutex _mutex;
    private bool _disposed;
    
    public MutexManager(string name)
    {
        _mutex = new Mutex(false, $"Global\\{name}");
    }
    
    public void Execute(Action action)
    {
        if (_disposed)
            throw new ObjectDisposedException(nameof(MutexManager));
            
        _mutex.WaitOne();
        try
        {
            action();
        }
        finally
        {
            _mutex.ReleaseMutex();
        }
    }
    
    public void Dispose()
    {
        if (_disposed) return;
        
        _mutex?.Dispose();
        _disposed = true;
    }
}
```

### 6. Use Meaningful Names

```csharp
// ✅ Good - Descriptive and unique
var mutex = new Mutex(false, "Global\\MyCompany_MyApp_v1.0_MainInstance");

// ❌ Bad - Too generic, potential conflicts
var mutex = new Mutex(false, "Global\\App");
```

---

## Mutex vs Lock vs SemaphoreSlim

| Feature | Mutex | Lock (Monitor) | SemaphoreSlim |
|---------|-------|---------------|---------------|
| Cross-Process | ✅ Yes | ❌ No | ❌ No |
| Async Support | ❌ No | ❌ No | ✅ Yes |
| Performance | Slower | Fastest | Fast |
| Named | ✅ Yes | ❌ No | ❌ No |
| Multiple Entries | ❌ No (1) | ❌ No (1) | ✅ Yes (N) |
| Use Case | Cross-process | Single-process | Throttling |

---

## Summary

- **Mutex**: Cross-process mutual exclusion
- **Named Mutex**: Share across application instances
- Perfect for single-instance applications
- Heavier than lock/monitor - use only when cross-process needed
- Always release in finally block
- Handle `AbandonedMutexException` gracefully
- Prefer `lock` for single-process scenarios

**Next:** [Monitor and Lock](./07-Monitor-Lock.md) | **Previous:** [Semaphore](./05-Semaphore.md) | **Back to:** [README](./README.md)
