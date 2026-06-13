# EAP (Event-based Asynchronous Pattern)

**Legacy Pattern** - Common in older .NET Framework code and some UI components.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Basic Usage](#basic-usage)
- [Converting EAP to TAP](#converting-eap-to-tap)
- [When You'll Encounter EAP](#when-youll-encounter-eap)

---

## Overview

The Event-based Asynchronous Pattern was the recommended pattern before TAP was introduced. While it's now considered legacy, you'll still encounter it in older codebases and some .NET Framework components.

**Characteristics:**
- Uses events for completion notification
- Method names end with `Async` (e.g., `DownloadStringAsync`)
- Separate event for completion (e.g., `DownloadStringCompleted`)
- Cancellation through `CancelAsync()` method
- No language-level support (no async/await)

---

## Key Features

- **Async Methods**: End with `Async` suffix
- **Completion Events**: Named `[Method]Completed`
- **Progress Events**: Optional `ProgressChanged` event
- **Cancellation**: `CancelAsync()` method
- **Event Args**: Contains result, error, and cancellation status

---

## Basic Usage

### Simple EAP Implementation

```csharp
public class DataDownloader
{
    private WebClient _client = new WebClient();
    
    // Completion event
    public event EventHandler<DownloadStringCompletedEventArgs> DownloadCompleted;
    
    // Async method
    public void DownloadDataAsync(string url)
    {
        _client.DownloadStringCompleted += (sender, e) =>
        {
            if (e.Error != null)
            {
                Console.WriteLine($"Error: {e.Error.Message}");
            }
            else if (e.Cancelled)
            {
                Console.WriteLine("Operation cancelled");
            }
            else
            {
                // Raise custom event with result
                DownloadCompleted?.Invoke(this, e);
            }
        };
        
        _client.DownloadStringAsync(new Uri(url));
    }
    
    // Cancellation method
    public void CancelAsync()
    {
        _client.CancelAsync();
    }
}
```

### Using EAP

```csharp
var downloader = new DataDownloader();

downloader.DownloadCompleted += (sender, e) =>
{
    Console.WriteLine($"Downloaded: {e.Result}");
};

downloader.DownloadDataAsync("https://api.example.com/data");
```

### WebClient EAP Example

```csharp
public void DownloadFileExample()
{
    using (var client = new WebClient())
    {
        // Subscribe to completion event
        client.DownloadFileCompleted += (sender, e) =>
        {
            if (e.Error != null)
            {
                Console.WriteLine($"Error: {e.Error.Message}");
            }
            else if (e.Cancelled)
            {
                Console.WriteLine("Download cancelled");
            }
            else
            {
                Console.WriteLine("Download completed successfully");
            }
        };
        
        // Subscribe to progress event
        client.DownloadProgressChanged += (sender, e) =>
        {
            Console.WriteLine($"Progress: {e.ProgressPercentage}% " +
                            $"({e.BytesReceived}/{e.TotalBytesToReceive} bytes)");
        };
        
        // Start async download
        client.DownloadFileAsync(
            new Uri("https://example.com/file.zip"),
            "local-file.zip");
    }
}
```

### BackgroundWorker EAP Example

```csharp
public void ProcessDataWithBackgroundWorker()
{
    var worker = new BackgroundWorker
    {
        WorkerReportsProgress = true,
        WorkerSupportsCancellation = true
    };
    
    // Do work in background
    worker.DoWork += (sender, e) =>
    {
        var bgWorker = sender as BackgroundWorker;
        
        for (int i = 1; i <= 100; i++)
        {
            // Check for cancellation
            if (bgWorker.CancellationPending)
            {
                e.Cancel = true;
                break;
            }
            
            // Simulate work
            Thread.Sleep(50);
            
            // Report progress
            bgWorker.ReportProgress(i);
        }
        
        e.Result = "Processing complete";
    };
    
    // Progress changed
    worker.ProgressChanged += (sender, e) =>
    {
        Console.WriteLine($"Progress: {e.ProgressPercentage}%");
    };
    
    // Work completed
    worker.RunWorkerCompleted += (sender, e) =>
    {
        if (e.Error != null)
        {
            Console.WriteLine($"Error: {e.Error.Message}");
        }
        else if (e.Cancelled)
        {
            Console.WriteLine("Operation was cancelled");
        }
        else
        {
            Console.WriteLine($"Result: {e.Result}");
        }
    };
    
    // Start async operation
    worker.RunWorkerAsync();
    
    // Can cancel later
    // worker.CancelAsync();
}
```

---

## Converting EAP to TAP

### Using TaskCompletionSource

```csharp
public static Task<string> DownloadStringTaskAsync(string url)
{
    var tcs = new TaskCompletionSource<string>();
    var client = new WebClient();
    
    client.DownloadStringCompleted += (sender, e) =>
    {
        if (e.Error != null)
            tcs.SetException(e.Error);
        else if (e.Cancelled)
            tcs.SetCanceled();
        else
            tcs.SetResult(e.Result);
            
        client.Dispose();
    };
    
    client.DownloadStringAsync(new Uri(url));
    return tcs.Task;
}

// Usage with async/await
string data = await DownloadStringTaskAsync("https://api.example.com/data");
```

### Generic EAP to TAP Converter

```csharp
public static class EAPExtensions
{
    public static Task<T> ToTaskAsync<T>(
        Action<EventHandler<AsyncCompletedEventArgs<T>>> subscribe,
        Action<EventHandler<AsyncCompletedEventArgs<T>>> unsubscribe,
        Action start)
    {
        var tcs = new TaskCompletionSource<T>();
        
        EventHandler<AsyncCompletedEventArgs<T>> handler = null;
        handler = (sender, e) =>
        {
            unsubscribe(handler);
            
            if (e.Error != null)
                tcs.SetException(e.Error);
            else if (e.Cancelled)
                tcs.SetCanceled();
            else
                tcs.SetResult(e.Result);
        };
        
        subscribe(handler);
        start();
        
        return tcs.Task;
    }
}
```

### BackgroundWorker to Task

```csharp
public static Task<T> RunAsync<T>(Func<BackgroundWorker, T> workFunc)
{
    var tcs = new TaskCompletionSource<T>();
    var worker = new BackgroundWorker();
    
    worker.DoWork += (sender, e) =>
    {
        try
        {
            e.Result = workFunc((BackgroundWorker)sender);
        }
        catch (Exception ex)
        {
            tcs.SetException(ex);
        }
    };
    
    worker.RunWorkerCompleted += (sender, e) =>
    {
        if (e.Error != null)
            tcs.SetException(e.Error);
        else if (e.Cancelled)
            tcs.SetCanceled();
        else
            tcs.SetResult((T)e.Result);
            
        worker.Dispose();
    };
    
    worker.RunWorkerAsync();
    return tcs.Task;
}

// Usage
var result = await RunAsync(worker =>
{
    // Do work
    Thread.Sleep(1000);
    return "Complete";
});
```

---

## When You'll Encounter EAP

### Common EAP Components

1. **WebClient** (Legacy)
   ```csharp
   WebClient.DownloadStringAsync()
   WebClient.DownloadFileAsync()
   ```

2. **BackgroundWorker** (WinForms/WPF)
   ```csharp
   BackgroundWorker.RunWorkerAsync()
   ```

3. **SmtpClient** (Legacy)
   ```csharp
   SmtpClient.SendAsync()
   ```

4. **PictureBox** (WinForms)
   ```csharp
   PictureBox.LoadAsync()
   ```

### Migration Strategy

When you encounter EAP code:

1. **If possible, replace with modern alternatives:**
   - `WebClient` → `HttpClient`
   - `BackgroundWorker` → `Task.Run` with async/await
   - `SmtpClient` → `MailKit` or modern alternatives

2. **If you must use EAP:**
   - Wrap it with `TaskCompletionSource` as shown above
   - Create async-friendly wrappers
   - Isolate EAP code in compatibility layers

---

## Comparison: EAP vs TAP

| Feature | EAP | TAP |
|---------|-----|-----|
| Language Support | No | Yes (async/await) |
| Composability | Poor | Excellent |
| Error Handling | Event args | try-catch |
| Cancellation | CancelAsync() | CancellationToken |
| Progress | Events | IProgress<T> |
| Readability | Event callbacks | Sequential code |
| Modern .NET | Legacy | Recommended |

---

## Best Practices

### 1. Don't Create New EAP Code

EAP is legacy. Always use TAP for new code.

### 2. Wrap EAP When Needed

```csharp
public class ModernDataDownloader
{
    public async Task<string> DownloadAsync(string url)
    {
        // Wrap legacy EAP in TAP
        return await DownloadStringTaskAsync(url);
    }
}
```

### 3. Handle All Event Cases

When working with EAP, always check:
- `e.Error` for exceptions
- `e.Cancelled` for cancellation
- The actual result

```csharp
client.DownloadCompleted += (sender, e) =>
{
    if (e.Error != null)
    {
        // Handle error
    }
    else if (e.Cancelled)
    {
        // Handle cancellation
    }
    else
    {
        // Process result
        var result = e.Result;
    }
};
```

### 4. Clean Up Resources

```csharp
var client = new WebClient();
try
{
    var tcs = new TaskCompletionSource<string>();
    client.DownloadStringCompleted += (sender, e) =>
    {
        // Handle completion
        client.Dispose(); // Clean up
    };
    client.DownloadStringAsync(new Uri(url));
    await tcs.Task;
}
catch
{
    client.Dispose(); // Clean up on error too
    throw;
}
```

---

## Summary

- EAP is a legacy pattern using events for async operations
- Use `TaskCompletionSource` to convert EAP to TAP
- Avoid creating new EAP code - use TAP instead
- When maintaining legacy code, wrap EAP in TAP for better integration

**Next:** [APM Pattern](./03-APM-Pattern.md) | **Previous:** [TAP Pattern](./01-TAP-Pattern.md) | **Back to:** [README](./README.md)
