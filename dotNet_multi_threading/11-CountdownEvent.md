# CountdownEvent

Signals when a counter reaches zero, useful for waiting on multiple operations.

## Table of Contents
- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Dynamic Operations](#dynamic-operations)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

CountdownEvent represents a synchronization primitive that is signaled when its count reaches zero. It's useful when you need to wait for a specific number of operations to complete.

**Key Concepts:**
- **Initial Count**: Number of signals required
- **Signal()**: Decrements the count
- **Wait()**: Blocks until count reaches zero
- **AddCount()**: Dynamically increase count
- **Reset()**: Reset the count to initial value

---

## Basic Usage

### Simple Countdown

```csharp
public class SimpleCountdown
{
    public void ProcessItems(IEnumerable<string> items)
    {
        var itemList = items.ToList();
        
        using (var countdown = new CountdownEvent(itemList.Count))
        {
            foreach (var item in itemList)
            {
                // Don't await - start all tasks concurrently
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await ProcessItemAsync(item);
                        Console.WriteLine($"Completed: {item}");
                    }
                    finally
                    {
                        countdown.Signal(); // Decrement counter
                    }
                });
            }
            
            // Wait for all to complete
            countdown.Wait();
            Console.WriteLine("All items processed!");
        }
    }
    
    private async Task ProcessItemAsync(string item)
    {
        await Task.Delay(Random.Shared.Next(500, 2000));
    }
}

// Usage
var processor = new SimpleCountdown();
var items = Enumerable.Range(1, 10).Select(i => $"Item{i}");
processor.ProcessItems(items);
```

### With Timeout

```csharp
public class TimeoutCountdown
{
    public bool ProcessWithTimeout(IEnumerable<string> items, TimeSpan timeout)
    {
        var itemList = items.ToList();
        
        using (var countdown = new CountdownEvent(itemList.Count))
        {
            foreach (var item in itemList)
            {
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await ProcessItemAsync(item);
                        Console.WriteLine($"Completed: {item}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error processing {item}: {ex.Message}");
                    }
                    finally
                    {
                        if (!countdown.IsSet)
                        {
                            countdown.Signal();
                        }
                    }
                });
            }
            
            // Wait with timeout
            if (countdown.Wait(timeout))
            {
                Console.WriteLine("All items completed successfully");
                return true;
            }
            else
            {
                Console.WriteLine("Timeout - not all items completed");
                return false;
            }
        }
    }
    
    private async Task ProcessItemAsync(string item)
    {
        await Task.Delay(Random.Shared.Next(500, 2000));
    }
}
```

### Batch Processing

```csharp
public class BatchProcessor
{
    public async Task ProcessBatchAsync(IEnumerable<string> items)
    {
        var itemList = items.ToList();
        
        using (var countdown = new CountdownEvent(itemList.Count))
        {
            var startTime = DateTime.Now;
            
            foreach (var item in itemList)
            {
                _ = Task.Run(async () =>
                {
                    try
                    {
                        await ProcessItemAsync(item);
                    }
                    finally
                    {
                        countdown.Signal();
                        Console.WriteLine($"Progress: {countdown.InitialCount - countdown.CurrentCount}/{countdown.InitialCount}");
                    }
                });
            }
            
            // Wait for all
            await Task.Run(() => countdown.Wait());
            
            var elapsed = DateTime.Now - startTime;
            Console.WriteLine($"Batch complete in {elapsed.TotalSeconds:F2}s");
        }
    }
    
    private async Task ProcessItemAsync(string item)
    {
        await Task.Delay(Random.Shared.Next(500, 1500));
    }
}

// Usage
var processor = new BatchProcessor();
var items = Enumerable.Range(1, 20).Select(i => $"Item{i}");
await processor.ProcessBatchAsync(items);
```

---

## Dynamic Operations

### Adding Count Dynamically

```csharp
public class DynamicTaskCoordinator
{
    public void ProcessWithDynamicTasks()
    {
        using (var countdown = new CountdownEvent(1)) // Start with 1
        {
            for (int i = 0; i < 5; i++)
            {
                countdown.AddCount(); // Add count for each new task
                int taskId = i;
                
                Task.Run(() =>
                {
                    Console.WriteLine($"Task {taskId} starting");
                    Thread.Sleep(Random.Shared.Next(500, 1500));
                    
                    // Spawn additional work
                    if (taskId < 3)
                    {
                        countdown.AddCount();
                        Task.Run(() =>
                        {
                            Console.WriteLine($"  Subtask of {taskId}");
                            Thread.Sleep(500);
                            countdown.Signal();
                        });
                    }
                    
                    Console.WriteLine($"Task {taskId} complete");
                    countdown.Signal();
                });
            }
            
            countdown.Signal(); // Signal initial count
            countdown.Wait(); // Wait for all
            Console.WriteLine("All tasks and subtasks completed!");
        }
    }
}

// Usage
var coordinator = new DynamicTaskCoordinator();
coordinator.ProcessWithDynamicTasks();
```

### Try Add Count

```csharp
public class SafeDynamicProcessor
{
    private CountdownEvent _countdown;
    private bool _isCompleted;
    private readonly object _lock = new object();
    
    public void StartProcessing()
    {
        _countdown = new CountdownEvent(1);
        _isCompleted = false;
        
        // Initial work items
        for (int i = 0; i < 5; i++)
        {
            AddWorkItem($"Initial-{i}");
        }
        
        // Signal initial count
        _countdown.Signal();
    }
    
    public void AddWorkItem(string item)
    {
        bool added = false;
        
        lock (_lock)
        {
            if (!_isCompleted && !_countdown.IsSet)
            {
                _countdown.AddCount();
                added = true;
            }
        }
        
        if (added)
        {
            Task.Run(() =>
            {
                Console.WriteLine($"Processing {item}");
                Thread.Sleep(Random.Shared.Next(500, 1000));
                
                // Potentially add more work
                if (Random.Shared.Next(100) < 30) // 30% chance
                {
                    AddWorkItem($"Dynamic-{Guid.NewGuid().ToString()[..8]}");
                }
                
                countdown.Signal();
            });
        }
    }
    
    public void WaitForCompletion()
    {
        _countdown.Wait();
        
        lock (_lock)
        {
            _isCompleted = true;
        }
        
        _countdown.Dispose();
        Console.WriteLine("All work completed");
    }
}
```

---

## Use Cases

### 1. File Processing

```csharp
public class FileProcessor
{
    public void ProcessFiles(string directory, string pattern)
    {
        var files = Directory.GetFiles(directory, pattern);
        
        using (var countdown = new CountdownEvent(files.Length))
        {
            foreach (var file in files)
            {
                Task.Run(async () =>
                {
                    try
                    {
                        await ProcessFileAsync(file);
                        Console.WriteLine($"Processed: {Path.GetFileName(file)}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error processing {Path.GetFileName(file)}: {ex.Message}");
                    }
                    finally
                    {
                        countdown.Signal();
                    }
                });
            }
            
            Console.WriteLine($"Processing {files.Length} files...");
            countdown.Wait();
            Console.WriteLine("All files processed!");
        }
    }
    
    private async Task ProcessFileAsync(string filePath)
    {
        var content = await File.ReadAllTextAsync(filePath);
        // Process content
        await Task.Delay(Random.Shared.Next(100, 500));
        
        // Write processed content
        var outputPath = Path.Combine(
            Path.GetDirectoryName(filePath),
            "processed_" + Path.GetFileName(filePath));
        await File.WriteAllTextAsync(outputPath, content.ToUpper());
    }
}

// Usage
var processor = new FileProcessor();
processor.ProcessFiles("./data", "*.txt");
```

### 2. Download Manager

```csharp
public class DownloadManager
{
    private readonly HttpClient _client = new HttpClient();
    
    public class DownloadResult
    {
        public string Url { get; set; }
        public bool Success { get; set; }
        public long BytesDownloaded { get; set; }
        public TimeSpan Duration { get; set; }
    }
    
    public List<DownloadResult> DownloadAll(IEnumerable<string> urls)
    {
        var urlList = urls.ToList();
        var results = new List<DownloadResult>();
        var resultsLock = new object();
        
        using (var countdown = new CountdownEvent(urlList.Count))
        {
            foreach (var url in urlList)
            {
                Task.Run(async () =>
                {
                    var result = new DownloadResult { Url = url };
                    var sw = Stopwatch.StartNew();
                    
                    try
                    {
                        var data = await _client.GetByteArrayAsync(url);
                        result.BytesDownloaded = data.Length;
                        result.Success = true;
                        Console.WriteLine($"Downloaded {url}: {data.Length} bytes");
                    }
                    catch (Exception ex)
                    {
                        result.Success = false;
                        Console.WriteLine($"Failed {url}: {ex.Message}");
                    }
                    finally
                    {
                        sw.Stop();
                        result.Duration = sw.Elapsed;
                        
                        lock (resultsLock)
                        {
                            results.Add(result);
                        }
                        
                        countdown.Signal();
                    }
                });
            }
            
            countdown.Wait();
        }
        
        // Print summary
        Console.WriteLine($"\n=== Download Summary ===");
        Console.WriteLine($"Total: {results.Count}");
        Console.WriteLine($"Success: {results.Count(r => r.Success)}");
        Console.WriteLine($"Failed: {results.Count(r => !r.Success)}");
        Console.WriteLine($"Total bytes: {results.Sum(r => r.BytesDownloaded):N0}");
        Console.WriteLine($"Avg time: {results.Average(r => r.Duration.TotalSeconds):F2}s");
        
        return results;
    }
}

// Usage
var manager = new DownloadManager();
var urls = new[]
{
    "https://example.com/file1.jpg",
    "https://example.com/file2.jpg",
    "https://example.com/file3.jpg",
    "https://example.com/file4.jpg",
    "https://example.com/file5.jpg"
};

var results = manager.DownloadAll(urls);
```

### 3. Test Runner

```csharp
public class TestRunner
{
    public class TestResult
    {
        public string TestName { get; set; }
        public bool Passed { get; set; }
        public string Error { get; set; }
        public TimeSpan Duration { get; set; }
    }
    
    public List<TestResult> RunTests(IEnumerable<Action> tests)
    {
        var testList = tests.ToList();
        var results = new ConcurrentBag<TestResult>();
        
        using (var countdown = new CountdownEvent(testList.Count))
        {
            for (int i = 0; i < testList.Count; i++)
            {
                int testIndex = i;
                var test = testList[i];
                
                Task.Run(() =>
                {
                    var result = new TestResult
                    {
                        TestName = $"Test_{testIndex + 1}"
                    };
                    
                    var sw = Stopwatch.StartNew();
                    
                    try
                    {
                        test();
                        result.Passed = true;
                        Console.WriteLine($"✓ {result.TestName} passed");
                    }
                    catch (Exception ex)
                    {
                        result.Passed = false;
                        result.Error = ex.Message;
                        Console.WriteLine($"✗ {result.TestName} failed: {ex.Message}");
                    }
                    finally
                    {
                        sw.Stop();
                        result.Duration = sw.Elapsed;
                        results.Add(result);
                        countdown.Signal();
                    }
                });
            }
            
            Console.WriteLine($"Running {testList.Count} tests...");
            countdown.Wait();
        }
        
        // Print summary
        var resultList = results.ToList();
        var passed = resultList.Count(r => r.Passed);
        var failed = resultList.Count(r => !r.Passed);
        
        Console.WriteLine($"\n=== Test Summary ===");
        Console.WriteLine($"Total: {resultList.Count}");
        Console.WriteLine($"Passed: {passed} ({passed * 100.0 / resultList.Count:F1}%)");
        Console.WriteLine($"Failed: {failed}");
        Console.WriteLine($"Duration: {resultList.Sum(r => r.Duration.TotalSeconds):F2}s");
        
        return resultList;
    }
}

// Usage
var runner = new TestRunner();
var tests = new Action[]
{
    () => { Thread.Sleep(100); /* Test 1 */ },
    () => { Thread.Sleep(150); /* Test 2 */ },
    () => { Thread.Sleep(120); throw new Exception("Test failed"); },
    () => { Thread.Sleep(110); /* Test 4 */ },
    () => { Thread.Sleep(130); /* Test 5 */ }
};

var results = runner.RunTests(tests);
```

### 4. Database Migration Coordinator

```csharp
public class MigrationCoordinator
{
    public void RunMigrations(List<Action> migrations)
    {
        using (var countdown = new CountdownEvent(migrations.Count))
        {
            var successCount = 0;
            var lockObj = new object();
            
            for (int i = 0; i < migrations.Count; i++)
            {
                int migrationId = i;
                var migration = migrations[i];
                
                Task.Run(() =>
                {
                    try
                    {
                        Console.WriteLine($"Migration {migrationId + 1}: Starting");
                        migration();
                        Console.WriteLine($"Migration {migrationId + 1}: Success");
                        
                        lock (lockObj)
                        {
                            successCount++;
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Migration {migrationId + 1}: Failed - {ex.Message}");
                    }
                    finally
                    {
                        countdown.Signal();
                    }
                });
            }
            
            countdown.Wait();
            
            Console.WriteLine($"\n=== Migration Summary ===");
            Console.WriteLine($"Total: {migrations.Count}");
            Console.WriteLine($"Success: {successCount}");
            Console.WriteLine($"Failed: {migrations.Count - successCount}");
        }
    }
}
```

---

## Best Practices

### 1. Always Dispose

```csharp
// ✅ Good - using statement
using (var countdown = new CountdownEvent(initialCount))
{
    // Use countdown
}

// ✅ Good - explicit disposal
var countdown = new CountdownEvent(initialCount);
try
{
    // Use countdown
}
finally
{
    countdown.Dispose();
}
```

### 2. Handle Exceptions in Worker Tasks

```csharp
// ✅ Good - Always signal, even on exception
Task.Run(async () =>
{
    try
    {
        await DoWorkAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
    }
    finally
    {
        countdown.Signal(); // Critical: Always signal
    }
});
```

### 3. Check IsSet Before Signal

```csharp
// ✅ Good - Safe signaling
if (!countdown.IsSet)
{
    countdown.Signal();
}

// ⚠️ Bad - Can throw if already signaled
countdown.Signal();
```

### 4. Use Timeout for Safety

```csharp
// ✅ Good - with timeout
if (countdown.Wait(TimeSpan.FromSeconds(30)))
{
    Console.WriteLine("All operations completed");
}
else
{
    Console.WriteLine("Timeout - some operations did not complete");
}

// ⚠️ Risky - infinite wait
countdown.Wait();
```

### 5. Monitor Progress

```csharp
public void ProcessWithProgress(List<string> items)
{
    using (var countdown = new CountdownEvent(items.Count))
    {
        foreach (var item in items)
        {
            Task.Run(() =>
            {
                try
                {
                    ProcessItem(item);
                }
                finally
                {
                    countdown.Signal();
                    
                    int remaining = countdown.CurrentCount;
                    int completed = countdown.InitialCount - remaining;
                    int percent = (completed * 100) / countdown.InitialCount;
                    
                    Console.WriteLine($"Progress: {completed}/{countdown.InitialCount} ({percent}%)");
                }
            });
        }
        
        countdown.Wait();
    }
}
```

### 6. Consider Task.WhenAll for Simple Cases

```csharp
// ❌ Don't use CountdownEvent for simple cases
using (var countdown = new CountdownEvent(tasks.Count))
{
    foreach (var task in tasks)
    {
        task.ContinueWith(t => countdown.Signal());
    }
    countdown.Wait();
}

// ✅ Better - Task.WhenAll
await Task.WhenAll(tasks);
```

---

## CountdownEvent vs Alternatives

| Feature | CountdownEvent | Task.WhenAll | Barrier | Semaphore |
|---------|----------------|--------------|---------|-----------|
| Wait for N operations | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Multiple phases | ❌ No | ❌ No | ✅ Yes | ❌ No |
| Dynamic count | ✅ Yes | ❌ No | ✅ Yes | N/A |
| Async-friendly | ⚠️ No | ✅ Yes | ⚠️ No | ✅ Yes (Slim) |
| Progress tracking | ✅ Easy | ⚠️ Manual | ❌ No | N/A |

---

## Summary

- **CountdownEvent**: Waits for N signals before releasing
- Perfect for waiting on a known number of operations
- Can dynamically add to the count
- Always signal in finally blocks
- Monitor progress via CurrentCount
- Consider Task.WhenAll for pure async scenarios
- Always dispose when done

**Next:** [Best Practices](./12-Best-Practices.md) | **Previous:** [Barrier](./10-Barrier.md) | **Back to:** [README](./README.md)
