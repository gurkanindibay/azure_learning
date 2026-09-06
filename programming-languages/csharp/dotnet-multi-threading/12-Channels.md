---
type: Programming Guide
title: "System.Threading.Channels"
description: "High-performance, thread-safe producer/consumer data structures for passing data between tasks and threads."
tags: [csharp, dotnet]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# System.Threading.Channels

High-performance, thread-safe producer/consumer data structures for passing data between tasks and threads.

## Table of Contents
- [Overview](#overview)
- [Channel Types](#channel-types)
- [Basic Usage](#basic-usage)
- [Bounded vs Unbounded Channels](#bounded-vs-unbounded-channels)
- [Backpressure and Flow Control](#backpressure-and-flow-control)
- [Advanced Patterns](#advanced-patterns)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

`System.Threading.Channels` (introduced in .NET Core 3.0, available via NuGet for earlier versions) provides a set of high-performance, thread-safe data structures designed for producer/consumer scenarios. Channels are the modern replacement for `BlockingCollection<T>` and hand-rolled producer/consumer queues.

**Key Concepts:**
- **Channel<T>**: The core abstraction — a pipe with a reader and a writer
- **ChannelWriter<T>**: The write-side handle (producer)
- **ChannelReader<T>**: The read-side handle (consumer)
- **BoundedChannelOptions**: Controls capacity and backpressure behavior
- **UnboundedChannelOptions**: For unbounded (grow-as-needed) channels

> **Taxonomy Reference**: §2.1 Application Architecture Patterns (Concurrency & Threading)  
> **Namespace**: `System.Threading.Channels` | **NuGet**: `System.Threading.Channels`

---

## Channel Types

Channels come in two fundamental flavors:

| Type | Behavior | When to Use |
|:---|:---|:---|
| **Unbounded** | Grows without limit; `WriteAsync` never waits | Fire-and-forget, logging, when producer shouldn't block |
| **Bounded** | Fixed capacity; `WriteAsync` waits when full | Backpressure control, memory-constrained scenarios |

### Creation Options

```csharp
// Unbounded — simplest, no capacity limit
var unbounded = Channel.CreateUnbounded<Message>();

// Bounded — fixed capacity with backpressure
var bounded = Channel.CreateBounded<Message>(new BoundedChannelOptions(100)
{
    FullMode = BoundedChannelFullMode.Wait  // Producer waits when full
});

// Bounded with drop behavior
var dropOldest = Channel.CreateBounded<Message>(new BoundedChannelOptions(100)
{
    FullMode = BoundedChannelFullMode.DropOldest  // Drop oldest item
});

// Single-reader, single-writer optimized
var optimized = Channel.CreateUnbounded<Message>(
    new UnboundedChannelOptions
    {
        SingleReader = true,
        SingleWriter = true
    });
```

---

## Basic Usage

### Simple Producer/Consumer

```csharp
var channel = Channel.CreateUnbounded<int>();

// Producer
async Task ProduceAsync(ChannelWriter<int> writer)
{
    for (int i = 0; i < 10; i++)
    {
        await writer.WriteAsync(i);
        Console.WriteLine($"Produced: {i}");
    }
    writer.Complete(); // Signal no more data
}

// Consumer
async Task ConsumeAsync(ChannelReader<int> reader)
{
    await foreach (var item in reader.ReadAllAsync())
    {
        Console.WriteLine($"Consumed: {item}");
    }
}

var producer = ProduceAsync(channel.Writer);
var consumer = ConsumeAsync(channel.Reader);
await Task.WhenAll(producer, consumer);
```

### Multiple Producers / Multiple Consumers

```csharp
var channel = Channel.CreateBounded<int>(new BoundedChannelOptions(100)
{
    FullMode = BoundedChannelFullMode.Wait
});

// Multiple producers — safe by default
var producers = Enumerable.Range(0, 3).Select(async id =>
{
    for (int i = 0; i < 5; i++)
    {
        await channel.Writer.WriteAsync(i);
        Console.WriteLine($"Producer {id}: {i}");
    }
});

// Multiple consumers — one gets each item (load-balanced)
var consumers = Enumerable.Range(0, 2).Select(async id =>
{
    await foreach (var item in channel.Reader.ReadAllAsync())
    {
        Console.WriteLine($"Consumer {id}: {item}");
        await Task.Delay(100); // Simulate work
    }
});

await Task.WhenAll(producers);
channel.Writer.Complete(); // Complete AFTER all producers finish
await Task.WhenAll(consumers);
```

---

## Bounded vs Unbounded Channels

### Unbounded Channel

```csharp
var channel = Channel.CreateUnbounded<WorkItem>();

// WriteAsync never waits — items always accepted
await channel.Writer.WriteAsync(new WorkItem());

// Use when:
// - Producer rate is unpredictable
// - You can tolerate memory growth
// - You want fire-and-forget semantics
```

### Bounded Channel with Backpressure

```csharp
var channel = Channel.CreateBounded<WorkItem>(new BoundedChannelOptions(50)
{
    FullMode = BoundedChannelFullMode.Wait
});

// WriteAsync will asynchronously wait when channel is full
await channel.Writer.WriteAsync(new WorkItem()); // May block!

// Use when:
// - Memory usage must be bounded
// - You want natural backpressure on producers
// - You have predictable throughput
```

---

## Backpressure and Flow Control

### `BoundedChannelFullMode` Options

| Mode | Behavior | Use Case |
|:---|:---|:---|
| `Wait` | `WriteAsync` waits until space available | Default; natural backpressure |
| `DropNewest` | Silently drops the newest item | Sampling; best-effort delivery |
| `DropOldest` | Silently drops the oldest item | Latest-value-is-best (e.g., stock price) |
| `DropWrite` | Silently drops the item being written | When producer handles its own retry |

### Implementing Backpressure with `WaitToWriteAsync`

```csharp
async Task ProduceWithBackpressureAsync(ChannelWriter<WorkItem> writer, WorkItem item)
{
    // Poll/wait until space is available (with timeout)
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
    
    if (await writer.WaitToWriteAsync(cts.Token))
    {
        writer.TryWrite(item);
    }
    else
    {
        // Handle timeout — drop, retry, or throttle
        Console.WriteLine("Channel full for 5s — dropping item");
    }
}
```

### Consumer-Side Flow Control with `WaitToReadAsync`

```csharp
async Task ConsumeWithPollAsync(ChannelReader<WorkItem> reader)
{
    while (await reader.WaitToReadAsync())
    {
        while (reader.TryRead(out var item))
        {
            await ProcessAsync(item);
        }
    }
    // Channel is completed and empty
}
```

> **Note**: `await foreach (var item in reader.ReadAllAsync())` is syntactic sugar for the `WaitToReadAsync` + `TryRead` pattern above.

---

## Advanced Patterns

### 1. Pipeline Pattern (Fan-Out/Fan-In)

```csharp
// Stage 1: Read → [Stage 2: Process] → Stage 3: Write
var stage1 = Channel.CreateBounded<string>(100);
var stage2 = Channel.CreateBounded<ProcessedData>(100);

async Task Stage1_ReadAsync()
{
    foreach (var line in File.ReadLines("input.txt"))
    {
        await stage1.Writer.WriteAsync(line);
    }
    stage1.Writer.Complete();
}

async Task Stage2_ProcessAsync(int concurrency)
{
    var tasks = Enumerable.Range(0, concurrency).Select(async _ =>
    {
        await foreach (var line in stage1.Reader.ReadAllAsync())
        {
            var processed = ProcessLine(line);
            await stage2.Writer.WriteAsync(processed);
        }
    });
    await Task.WhenAll(tasks);
    stage2.Writer.Complete();
}

async Task Stage3_WriteAsync()
{
    await foreach (var data in stage2.Reader.ReadAllAsync())
    {
        await File.AppendAllTextAsync("output.txt", data.ToString());
    }
}
```

### 2. Broadcast Pattern (Single-Producer, Multi-Consumer Each Gets Every Item)

Channels don't natively broadcast — but you can build it:

```csharp
async Task BroadcastAsync<T>(
    ChannelReader<T> source,
    params ChannelWriter<T>[] targets)
{
    await foreach (var item in source.ReadAllAsync())
    {
        var writeTasks = targets.Select(t => t.WriteAsync(item));
        await Task.WhenAll(writeTasks);
    }
    foreach (var target in targets)
        target.Complete();
}
```

### 3. Try Operations (Non-Blocking)

```csharp
// Non-blocking write attempt
if (writer.TryWrite(item))
{
    // Item written
}
else
{
    // Channel full — handle immediately
}

// Non-blocking read attempt
if (reader.TryRead(out var item))
{
    // Process item
}
else
{
    // Nothing available — do other work or yield
}

// Batch read — drain items efficiently
while (reader.TryRead(out var item))
{
    ProcessBatch(item);
}
```

### 4. Cancellation Support

```csharp
async Task ProduceWithCancellationAsync(
    ChannelWriter<int> writer,
    CancellationToken cancellationToken)
{
    for (int i = 0; i < 1000; i++)
    {
        cancellationToken.ThrowIfCancellationRequested();
        await writer.WriteAsync(i, cancellationToken);
    }
    writer.Complete();
}

async Task ConsumeWithCancellationAsync(
    ChannelReader<int> reader,
    CancellationToken cancellationToken)
{
    try
    {
        await foreach (var item in reader.ReadAllAsync(cancellationToken))
        {
            // Process
        }
    }
    catch (OperationCanceledException)
    {
        Console.WriteLine("Consumption cancelled");
    }
}
```

### 5. Single-Reader / Single-Writer Optimization

```csharp
var channel = Channel.CreateUnbounded<Message>(
    new UnboundedChannelOptions
    {
        SingleReader = true,  // I'm the only reader — skip locking
        SingleWriter = true,  // I'm the only writer — skip locking
        AllowSynchronousContinuations = true  // Inline continuations
    });
```

- `SingleReader = true` / `SingleWriter = true`: Elides internal locks when only one reader/writer exists, improving throughput by ~30-50%
- `AllowSynchronousContinuations = true`: Allows continuations to run inline on the calling thread (faster but can cause deadlocks if misused — only use with care)

---

## Use Cases

| Scenario | Channel Config | Why |
|:---|:---|:---|
| **Request queue** | Bounded (100), `Wait` | Natural backpressure when overwhelmed |
| **Event log buffer** | Unbounded, `SingleWriter` | Never block the logger; one writer thread |
| **Stock price feed** | Bounded (1), `DropOldest` | Only latest price matters |
| **Pipeline stages** | Bounded (1000), `Wait` | Flow control between stages |
| **Telemetry sampling** | Bounded (100), `DropNewest` | Keep recent data; drop under load |
| **Background job queue** | Unbounded | Accept all jobs; process eventually |
| **Real-time processing** | Bounded (50), `Wait` | Predictable latency and memory |

---

## Best Practices

### ✅ DO

- **Call `Complete()`** on the writer when done producing so consumers can exit cleanly
- **Use bounded channels** in production to avoid unbounded memory growth
- **Use `SingleReader/SingleWriter`** when you're certain about thread access patterns
- **Prefer `await foreach`** over manual `WaitToReadAsync` for simplicity
- **Pass `CancellationToken`** to `WriteAsync`, `ReadAllAsync`, and `WaitToReadAsync`
- **Use `TryWrite`/`TryRead`** when you need non-blocking behavior

### ❌ DON'T

- **Don't forget to call `Complete()`** — consumers will wait forever
- **Don't use unbounded channels** for workload queues in production without memory monitoring
- **Don't share a `Channel<T>`** across unrelated subsystems — pass `ChannelWriter<T>` or `ChannelReader<T>` only
- **Don't use `AllowSynchronousContinuations = true`** unless you fully understand the reentrancy implications
- **Don't call `Complete()`** from multiple threads without coordination — it can throw
- **Don't write to a completed channel** — `WriteAsync` will throw `ChannelClosedException`

### Common Mistakes

```csharp
// ❌ Wrong: Completing writer inside consumer deadlock-prone scope
var channel = Channel.CreateUnbounded<int>();
var consumer = Task.Run(async () =>
{
    await foreach (var item in channel.Reader.ReadAllAsync())
    {
        channel.Writer.Complete(); // BAD — consumer shouldn't complete writer
    }
});

// ✅ Right: Producer completes the writer
var channel = Channel.CreateUnbounded<int>();
var producer = Task.Run(async () =>
{
    for (int i = 0; i < 10; i++)
        await channel.Writer.WriteAsync(i);
    channel.Writer.Complete(); // GOOD
});
var consumer = Task.Run(async () =>
{
    await foreach (var item in channel.Reader.ReadAllAsync())
        Console.WriteLine(item);
});
await Task.WhenAll(producer, consumer);
```

### Performance Considerations

| Optimization | Impact | When |
|:---|:---|:---|
| `SingleReader = true` | ~30-50% throughput gain | Exactly 1 reader thread |
| `SingleWriter = true` | ~30-50% throughput gain | Exactly 1 writer thread |
| `TryWrite` + `TryRead` | Avoids async overhead | Hot path, batch operations |
| Bounded (reasonable size) | Predictable latency | Production workloads |
| `AllowSynchronousContinuations` | Reduced context-switching | High-throughput, single-threaded |

---

> **Related**: [TAP Pattern](./01-TAP-Pattern.md) | [Multithreading Concepts](./04-Multithreading-Concepts.md) | [Best Practices](./13-Best-Practices.md)  
> **Further Reading**: [System.Threading.Channels Docs](https://learn.microsoft.com/en-us/dotnet/api/system.threading.channels) | [An Introduction to System.Threading.Channels](https://devblogs.microsoft.com/dotnet/an-introduction-to-system-threading-channels/)
