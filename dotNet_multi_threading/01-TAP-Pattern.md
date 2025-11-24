# TAP (Task-based Asynchronous Pattern)

**The Modern Standard** - Introduced in .NET Framework 4.0 and refined with async/await in C# 5.0.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Basic Usage](#basic-usage)
- [Cancellation Support](#cancellation-support)
- [Progress Reporting](#progress-reporting)
- [Best Practices](#best-practices)

---

## Overview

TAP is the recommended asynchronous programming pattern in modern .NET. It provides a cleaner, more maintainable way to write asynchronous code compared to older patterns.

**Benefits:**
- Natural, sequential code flow despite asynchronous operations
- Compiler-generated state machines handle complexity
- Better exception handling and propagation
- Built-in support for cancellation and progress reporting
- Composable with LINQ and other functional patterns

---

## Key Features

- Uses `Task` and `Task<T>` types
- `async` and `await` keywords for cleaner code
- Built-in cancellation support via `CancellationToken`
- Exception handling through try-catch blocks
- Seamless integration with synchronization context

---

## Basic Usage

### Simple Async Method

```csharp
public async Task<string> DownloadDataAsync(string url)
{
    using (var client = new HttpClient())
    {
        // await suspends execution until the task completes
        string result = await client.GetStringAsync(url);
        return result;
    }
}
```

### Calling Async Methods

```csharp
public async Task ProcessDataAsync()
{
    try
    {
        string data = await DownloadDataAsync("https://api.example.com/data");
        Console.WriteLine($"Downloaded: {data.Length} characters");
    }
    catch (HttpRequestException ex)
    {
        Console.WriteLine($"Error: {ex.Message}");
    }
}
```

### Multiple Async Operations

**Sequential Execution:**
```csharp
public async Task<string> GetCombinedDataAsync()
{
    var data1 = await DownloadDataAsync("https://api.example.com/data1");
    var data2 = await DownloadDataAsync("https://api.example.com/data2");
    return data1 + data2;
}
```

**Concurrent Execution:**
```csharp
public async Task<string> GetCombinedDataConcurrentAsync()
{
    var task1 = DownloadDataAsync("https://api.example.com/data1");
    var task2 = DownloadDataAsync("https://api.example.com/data2");
    
    // Both downloads happen concurrently
    await Task.WhenAll(task1, task2);
    
    return task1.Result + task2.Result;
}
```

---

## Cancellation Support

### Basic Cancellation

```csharp
public async Task<string> DownloadWithCancellationAsync(
    string url, 
    CancellationToken token)
{
    using (var client = new HttpClient())
    {
        var response = await client.GetAsync(url, token);
        return await response.Content.ReadAsStringAsync();
    }
}
```

### Using CancellationTokenSource

```csharp
// Cancel after timeout
var cts = new CancellationTokenSource();
cts.CancelAfter(TimeSpan.FromSeconds(5)); // Cancel after 5 seconds

try
{
    var data = await DownloadWithCancellationAsync(
        "https://api.example.com/data", 
        cts.Token);
}
catch (OperationCanceledException)
{
    Console.WriteLine("Operation was cancelled");
}
```

### Manual Cancellation

```csharp
var cts = new CancellationTokenSource();

// Cancel from another thread or UI button
var downloadTask = Task.Run(async () =>
{
    await DownloadWithCancellationAsync("https://api.example.com/data", cts.Token);
});

// Simulate user clicking cancel button
await Task.Delay(2000);
cts.Cancel();
```

### Cancellation in Loops

```csharp
public async Task ProcessItemsAsync(
    IEnumerable<string> items, 
    CancellationToken token)
{
    foreach (var item in items)
    {
        // Check for cancellation
        token.ThrowIfCancellationRequested();
        
        await ProcessItemAsync(item);
    }
}
```

---

## Progress Reporting

### Using IProgress<T>

```csharp
public async Task ProcessLargeFileAsync(
    string path, 
    IProgress<int> progress)
{
    var lines = await File.ReadAllLinesAsync(path);
    int totalLines = lines.Length;
    
    for (int i = 0; i < totalLines; i++)
    {
        // Process line
        await ProcessLineAsync(lines[i]);
        
        // Report progress
        int percentComplete = (i + 1) * 100 / totalLines;
        progress?.Report(percentComplete);
    }
}
```

### Progress with Details

```csharp
public class DownloadProgress
{
    public long BytesDownloaded { get; set; }
    public long TotalBytes { get; set; }
    public int PercentComplete => (int)((BytesDownloaded * 100) / TotalBytes);
    public TimeSpan ElapsedTime { get; set; }
}

public async Task DownloadWithProgressAsync(
    string url, 
    string destinationPath,
    IProgress<DownloadProgress> progress)
{
    using (var client = new HttpClient())
    using (var response = await client.GetAsync(url, HttpCompletionOption.ResponseHeadersRead))
    using (var stream = await response.Content.ReadAsStreamAsync())
    using (var fileStream = File.Create(destinationPath))
    {
        var totalBytes = response.Content.Headers.ContentLength ?? -1;
        var buffer = new byte[8192];
        long bytesDownloaded = 0;
        var stopwatch = Stopwatch.StartNew();
        
        int bytesRead;
        while ((bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length)) > 0)
        {
            await fileStream.WriteAsync(buffer, 0, bytesRead);
            bytesDownloaded += bytesRead;
            
            progress?.Report(new DownloadProgress
            {
                BytesDownloaded = bytesDownloaded,
                TotalBytes = totalBytes,
                ElapsedTime = stopwatch.Elapsed
            });
        }
    }
}
```

### Usage Example

```csharp
// Simple progress
var progress = new Progress<int>(percent => 
{
    Console.WriteLine($"Progress: {percent}%");
});

await ProcessLargeFileAsync("large-file.txt", progress);

// Detailed progress
var downloadProgress = new Progress<DownloadProgress>(p =>
{
    Console.WriteLine($"Downloaded {p.BytesDownloaded:N0} / {p.TotalBytes:N0} bytes " +
                      $"({p.PercentComplete}%) - Elapsed: {p.ElapsedTime:mm\\:ss}");
});

await DownloadWithProgressAsync(
    "https://example.com/large-file.zip",
    "local-file.zip",
    downloadProgress);
```

---

## Best Practices

### 1. Always Use Async All the Way

❌ **Bad:**
```csharp
public string GetData()
{
    return DownloadDataAsync().Result; // Blocks thread, can cause deadlocks
}
```

✅ **Good:**
```csharp
public async Task<string> GetDataAsync()
{
    return await DownloadDataAsync();
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
public async Task<string> LibraryMethodAsync()
{
    // Don't need to return to original context in libraries
    var data = await DownloadDataAsync().ConfigureAwait(false);
    var processed = await ProcessDataAsync(data).ConfigureAwait(false);
    return processed;
}
```

### 4. Handle Exceptions Properly

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
```

### 5. Use Task.WhenAll for Concurrent Operations

```csharp
public async Task<List<string>> DownloadMultipleAsync(IEnumerable<string> urls)
{
    var tasks = urls.Select(url => DownloadDataAsync(url));
    var results = await Task.WhenAll(tasks);
    return results.ToList();
}
```

### 6. Provide Cancellation Support

```csharp
public async Task<string> ProcessDataAsync(
    string input,
    CancellationToken cancellationToken = default)
{
    // Always accept and pass through cancellation tokens
    var data = await DownloadDataAsync(input, cancellationToken);
    return await TransformDataAsync(data, cancellationToken);
}
```

### 7. Don't Mix Blocking and Async Code

❌ **Bad:**
```csharp
public void ProcessData()
{
    var task = ProcessDataAsync();
    task.Wait(); // Can cause deadlocks
}
```

✅ **Good:**
```csharp
public async Task ProcessDataAsync()
{
    await ProcessDataInternalAsync();
}
```

---

## Common Patterns

### Timeout Pattern

```csharp
public async Task<string> DownloadWithTimeoutAsync(string url, TimeSpan timeout)
{
    using (var cts = new CancellationTokenSource(timeout))
    {
        try
        {
            return await DownloadDataAsync(url, cts.Token);
        }
        catch (OperationCanceledException)
        {
            throw new TimeoutException($"Download exceeded {timeout.TotalSeconds} seconds");
        }
    }
}
```

### Retry Pattern

```csharp
public async Task<T> RetryAsync<T>(
    Func<Task<T>> operation,
    int maxRetries = 3,
    TimeSpan delay = default)
{
    delay = delay == default ? TimeSpan.FromSeconds(1) : delay;
    
    for (int i = 0; i < maxRetries; i++)
    {
        try
        {
            return await operation();
        }
        catch (Exception ex) when (i < maxRetries - 1)
        {
            Console.WriteLine($"Attempt {i + 1} failed: {ex.Message}. Retrying...");
            await Task.Delay(delay);
        }
    }
    
    // Last attempt without catching
    return await operation();
}
```

### Lazy Initialization Pattern

```csharp
public class DataService
{
    private readonly SemaphoreSlim _initLock = new SemaphoreSlim(1, 1);
    private Task<Data> _initTask;
    
    public async Task<Data> GetDataAsync()
    {
        if (_initTask != null)
            return await _initTask;
        
        await _initLock.WaitAsync();
        try
        {
            if (_initTask == null)
            {
                _initTask = InitializeDataAsync();
            }
        }
        finally
        {
            _initLock.Release();
        }
        
        return await _initTask;
    }
    
    private async Task<Data> InitializeDataAsync()
    {
        await Task.Delay(1000); // Simulate initialization
        return new Data();
    }
}
```

---

## Summary

TAP with async/await is the modern standard for asynchronous programming in .NET. Key points:

- Use `async Task` or `async Task<T>` for asynchronous methods
- Always `await` asynchronous operations
- Support cancellation with `CancellationToken`
- Report progress with `IProgress<T>`
- Follow best practices to avoid deadlocks and performance issues
- Use `ConfigureAwait(false)` in library code

**Next:** [EAP Pattern](./02-EAP-Pattern.md) | **Back to:** [README](./README.md)
