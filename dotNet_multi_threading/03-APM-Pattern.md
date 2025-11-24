# APM (Asynchronous Programming Model)

**Oldest Pattern** - Also known as the "Begin/End" pattern, found in legacy .NET code.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Basic Usage](#basic-usage)
- [Converting APM to TAP](#converting-apm-to-tap)
- [When You'll Encounter APM](#when-youll-encounter-apm)

---

## Overview

The Asynchronous Programming Model (APM) is the oldest asynchronous pattern in .NET, dating back to .NET Framework 1.0. It uses pairs of `BeginXxx` and `EndXxx` methods with callback-based completion.

**Characteristics:**
- Pairs of methods: `BeginXxx` and `EndXxx`
- Uses `IAsyncResult` interface
- Callback-based completion
- More complex and error-prone than modern patterns
- No language-level support

---

## Key Features

- **Begin Method**: Starts the async operation, returns `IAsyncResult`
- **End Method**: Completes the operation, returns the result
- **IAsyncResult**: Represents the async operation
- **AsyncCallback**: Optional callback delegate
- **AsyncState**: Optional state object passed to callback

---

## Basic Usage

### FileStream APM Example

```csharp
public void ReadFileAPM(string path)
{
    FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, 
                                  FileShare.Read, 4096, true);
    byte[] buffer = new byte[4096];
    
    // Begin asynchronous read
    fs.BeginRead(buffer, 0, buffer.Length, (IAsyncResult result) =>
    {
        // This callback runs when the read completes
        FileStream stream = (FileStream)result.AsyncState;
        
        try
        {
            int bytesRead = stream.EndRead(result);
            Console.WriteLine($"Read {bytesRead} bytes");
            
            // Process buffer here
            ProcessData(buffer, bytesRead);
        }
        finally
        {
            stream.Close();
        }
    }, fs); // Pass FileStream as state object
}
```

### HttpWebRequest APM Example

```csharp
public void DownloadDataAPM(string url)
{
    var request = (HttpWebRequest)WebRequest.Create(url);
    
    // Begin getting response
    request.BeginGetResponse(ar =>
    {
        try
        {
            HttpWebRequest req = (HttpWebRequest)ar.AsyncState;
            HttpWebResponse response = (HttpWebResponse)req.EndGetResponse(ar);
            
            using (var stream = response.GetResponseStream())
            using (var reader = new StreamReader(stream))
            {
                string content = reader.ReadToEnd();
                Console.WriteLine($"Downloaded: {content.Length} characters");
            }
        }
        catch (WebException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }, request);
}
```

### Socket APM Example

```csharp
public void ConnectSocketAPM(string host, int port)
{
    var socket = new Socket(AddressFamily.InterNetwork, 
                           SocketType.Stream, 
                           ProtocolType.Tcp);
    var endpoint = new IPEndPoint(IPAddress.Parse(host), port);
    
    // Begin async connect
    socket.BeginConnect(endpoint, ar =>
    {
        try
        {
            Socket sock = (Socket)ar.AsyncState;
            sock.EndConnect(ar);
            Console.WriteLine("Connected successfully");
            
            // Now can begin sending/receiving data
        }
        catch (SocketException ex)
        {
            Console.WriteLine($"Connection failed: {ex.Message}");
        }
    }, socket);
}
```

### APM with Manual Waiting

```csharp
public byte[] ReadFileSynchronouslyUsingAPM(string path)
{
    using (FileStream fs = new FileStream(path, FileMode.Open))
    {
        byte[] buffer = new byte[fs.Length];
        
        // Begin async operation
        IAsyncResult result = fs.BeginRead(buffer, 0, buffer.Length, null, null);
        
        // Wait for completion (blocking)
        result.AsyncWaitHandle.WaitOne();
        
        // Get result
        int bytesRead = fs.EndRead(result);
        
        return buffer;
    }
}
```

---

## Converting APM to TAP

### Using Task.Factory.FromAsync

This is the recommended way to convert APM to TAP.

```csharp
public static Task<int> ReadTaskAsync(
    FileStream stream, 
    byte[] buffer, 
    int offset, 
    int count)
{
    return Task<int>.Factory.FromAsync(
        stream.BeginRead,
        stream.EndRead,
        buffer,
        offset,
        count,
        null);
}

// Modern usage with async/await
public async Task ProcessFileAsync(string path)
{
    using (var fs = new FileStream(path, FileMode.Open))
    {
        byte[] buffer = new byte[4096];
        int bytesRead = await ReadTaskAsync(fs, buffer, 0, buffer.Length);
        Console.WriteLine($"Read {bytesRead} bytes");
    }
}
```

### Generic APM to TAP Wrapper

```csharp
public static class APMExtensions
{
    public static Task<TResult> FromAPM<TResult>(
        Func<AsyncCallback, object, IAsyncResult> begin,
        Func<IAsyncResult, TResult> end)
    {
        return Task<TResult>.Factory.FromAsync(begin, end, null);
    }
}

// Usage
var data = await APMExtensions.FromAPM<int>(
    (callback, state) => stream.BeginRead(buffer, 0, buffer.Length, callback, state),
    ar => stream.EndRead(ar));
```

### HttpWebRequest APM to TAP

```csharp
public static Task<WebResponse> GetResponseAsync(this WebRequest request)
{
    return Task<WebResponse>.Factory.FromAsync(
        request.BeginGetResponse,
        request.EndGetResponse,
        null);
}

// Usage
public async Task<string> DownloadStringAsync(string url)
{
    var request = WebRequest.Create(url);
    using (var response = await request.GetResponseAsync())
    using (var stream = response.GetResponseStream())
    using (var reader = new StreamReader(stream))
    {
        return await reader.ReadToEndAsync();
    }
}
```

### Socket APM to TAP

```csharp
public static class SocketExtensions
{
    public static Task ConnectAsync(this Socket socket, IPEndPoint endpoint)
    {
        return Task.Factory.FromAsync(
            socket.BeginConnect,
            socket.EndConnect,
            endpoint,
            null);
    }
    
    public static Task<int> ReceiveAsync(
        this Socket socket, 
        byte[] buffer, 
        int offset, 
        int size)
    {
        return Task<int>.Factory.FromAsync(
            (callback, state) => socket.BeginReceive(buffer, offset, size, 
                                                     SocketFlags.None, callback, state),
            socket.EndReceive,
            null);
    }
}

// Usage
public async Task CommunicateAsync(string host, int port)
{
    using (var socket = new Socket(AddressFamily.InterNetwork, 
                                   SocketType.Stream, 
                                   ProtocolType.Tcp))
    {
        var endpoint = new IPEndPoint(IPAddress.Parse(host), port);
        await socket.ConnectAsync(endpoint);
        
        byte[] buffer = new byte[1024];
        int received = await socket.ReceiveAsync(buffer, 0, buffer.Length);
        Console.WriteLine($"Received {received} bytes");
    }
}
```

### Manual Conversion with TaskCompletionSource

```csharp
public static Task<TResult> FromAPMManual<TResult>(
    Func<AsyncCallback, object, IAsyncResult> begin,
    Func<IAsyncResult, TResult> end)
{
    var tcs = new TaskCompletionSource<TResult>();
    
    try
    {
        begin(ar =>
        {
            try
            {
                var result = end(ar);
                tcs.SetResult(result);
            }
            catch (Exception ex)
            {
                tcs.SetException(ex);
            }
        }, null);
    }
    catch (Exception ex)
    {
        tcs.SetException(ex);
    }
    
    return tcs.Task;
}
```

---

## When You'll Encounter APM

### Common APM APIs

1. **FileStream**
   ```csharp
   BeginRead / EndRead
   BeginWrite / EndWrite
   ```

2. **HttpWebRequest** (Legacy)
   ```csharp
   BeginGetResponse / EndGetResponse
   BeginGetRequestStream / EndGetRequestStream
   ```

3. **Socket**
   ```csharp
   BeginConnect / EndConnect
   BeginSend / EndSend
   BeginReceive / EndReceive
   ```

4. **Stream Classes**
   ```csharp
   BeginRead / EndRead
   BeginWrite / EndWrite
   ```

5. **Delegate.BeginInvoke** (Removed in .NET Core)
   ```csharp
   BeginInvoke / EndInvoke
   ```

### Modern Alternatives

| APM API | Modern Alternative |
|---------|-------------------|
| FileStream.BeginRead | FileStream.ReadAsync |
| HttpWebRequest | HttpClient |
| Socket APM methods | Socket.ConnectAsync, etc. |
| Delegate.BeginInvoke | Task.Run |

---

## APM Patterns

### Polling Pattern

```csharp
public void PollingExample(string path)
{
    using (var fs = new FileStream(path, FileMode.Open))
    {
        byte[] buffer = new byte[1024];
        IAsyncResult result = fs.BeginRead(buffer, 0, buffer.Length, null, null);
        
        // Poll until complete
        while (!result.IsCompleted)
        {
            Console.WriteLine("Still reading...");
            Thread.Sleep(100);
        }
        
        int bytesRead = fs.EndRead(result);
        Console.WriteLine($"Read complete: {bytesRead} bytes");
    }
}
```

### Wait Handle Pattern

```csharp
public void WaitHandleExample(string path)
{
    using (var fs = new FileStream(path, FileMode.Open))
    {
        byte[] buffer = new byte[1024];
        IAsyncResult result = fs.BeginRead(buffer, 0, buffer.Length, null, null);
        
        // Wait with timeout
        if (result.AsyncWaitHandle.WaitOne(TimeSpan.FromSeconds(5)))
        {
            int bytesRead = fs.EndRead(result);
            Console.WriteLine($"Read {bytesRead} bytes");
        }
        else
        {
            Console.WriteLine("Timeout waiting for read");
        }
    }
}
```

### Callback Pattern

```csharp
public void CallbackExample(string path)
{
    using (var fs = new FileStream(path, FileMode.Open))
    {
        byte[] buffer = new byte[1024];
        
        fs.BeginRead(buffer, 0, buffer.Length, ar =>
        {
            int bytesRead = fs.EndRead(ar);
            Console.WriteLine($"Callback: Read {bytesRead} bytes");
        }, null);
        
        // Don't close here - would close before callback executes
    }
}
```

---

## Best Practices

### 1. Don't Create New APM Code

APM is legacy. Always use TAP (async/await) for new code.

### 2. Convert APM to TAP

Use `Task.Factory.FromAsync` to wrap APM methods:

```csharp
// Instead of using APM directly
public async Task<int> ReadAsync(Stream stream, byte[] buffer)
{
    return await Task<int>.Factory.FromAsync(
        stream.BeginRead,
        stream.EndRead,
        buffer,
        0,
        buffer.Length,
        null);
}
```

### 3. Always Call End Method

```csharp
// Always pair BeginXxx with EndXxx
IAsyncResult result = stream.BeginRead(buffer, 0, buffer.Length, null, null);
try
{
    int bytesRead = stream.EndRead(result); // Must call EndRead
}
catch (Exception ex)
{
    // Handle exceptions from EndRead
}
```

### 4. Handle Exceptions in Callbacks

```csharp
stream.BeginRead(buffer, 0, buffer.Length, ar =>
{
    try
    {
        int bytesRead = stream.EndRead(ar);
        // Process data
    }
    catch (Exception ex)
    {
        // Handle exceptions - they won't propagate automatically
        Console.WriteLine($"Error: {ex.Message}");
    }
}, null);
```

---

## Comparison: APM vs TAP

| Feature | APM | TAP |
|---------|-----|-----|
| Introduced | .NET 1.0 | .NET 4.0 |
| Method Pattern | BeginXxx/EndXxx | XxxAsync |
| Language Support | No | Yes (async/await) |
| Error Handling | Manual in callbacks | try-catch |
| Composability | Very Poor | Excellent |
| Cancellation | No standard way | CancellationToken |
| Readability | Poor (callback hell) | Excellent |
| Modern .NET | Legacy | Recommended |

---

## Summary

- APM is the oldest async pattern using Begin/End method pairs
- Use `Task.Factory.FromAsync` to convert APM to TAP
- Never create new APM code - use TAP instead
- APM is largely replaced by modern async methods in .NET Core/.NET 5+

**Next:** [Multithreading Concepts](./04-Multithreading-Concepts.md) | **Previous:** [EAP Pattern](./02-EAP-Pattern.md) | **Back to:** [README](./README.md)
