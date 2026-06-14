---
type: Reference
title: ".NET Multithreading & Concurrency"
description: "**Task-based Asynchronous Pattern** — the modern .NET async pattern using `Task`/`Task<T>` with `async`/`await`. TAP is the **only recommended async pattern** for new .NET development."
timestamp: 2026-06-14T00:00:00Z
---

# .NET Multithreading & Concurrency

> **Domain**: .NET threading models, async patterns, synchronization primitives, and concurrency best practices.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| TAP (Task-based Asynchronous Pattern) | [`#tap`](#tap) |
| Task / Task\<T\> | [`#task`](#task) |
| async / await | [`#async-await`](#async-await) |
| ThreadPool | [`#threadpool`](#threadpool) |
| ConfigureAwait(false) | [`#configureawait`](#configureawait) |
| SynchronizationContext | [`#synchronizationcontext`](#synchronizationcontext) |
| CancellationToken | [`#cancellationtoken`](#cancellationtoken) |
| SemaphoreSlim | [`#semaphoreslim`](#semaphoreslim) |
| Mutex | [`#mutex`](#mutex) |
| Monitor / lock | [`#monitor-lock`](#monitor-lock) |
| ReaderWriterLockSlim | [`#readerwriterlockslim`](#readerwriterlockslim) |
| Barrier | [`#barrier`](#barrier) |
| CountdownEvent | [`#countdownevent`](#countdownevent) |
| Channel\<T\> | [`#channel`](#channel) |
| Interlocked | [`#interlocked`](#interlocked) |
| Deadlock | [`#deadlock`](#deadlock) |
| EAP / APM (Legacy) | [`#eap-apm`](#eap-apm) |

---

## TAP

**Task-based Asynchronous Pattern** — the modern .NET async pattern using `Task`/`Task<T>` with `async`/`await`. TAP is the **only recommended async pattern** for new .NET development.

```csharp
public async Task<Order> GetOrderAsync(int id)
{
    return await db.Orders.FindAsync(id);
}
```

**Also see**: [Task](#task), [async/await](#async-await) · [EAP/APM](#eap-apm)

---

## Task

A higher-level async abstraction representing an **ongoing or completed asynchronous operation**. Tasks use the ThreadPool, support cancellation and composition, and are the foundation of TAP.

| Type | Returns | Use |
|:---|:---|:---|
| `Task` | No result | Fire-and-forget or signal completion |
| `Task<T>` | Typed result | Async operations that produce a value |

| Composition | Behavior |
|:---|:---|
| `Task.WhenAll` | Await all tasks to complete |
| `Task.WhenAny` | Await the first task to complete |

**Also see**: [TAP](#tap), [async/await](#async-await), [ThreadPool](#threadpool)

---

## async / await

Language-level support for writing **asynchronous code that reads like synchronous code**. `await` yields control until the awaited Task completes, then resumes.

| Rule | Why |
|:---|:---|
| **Async all the way** | Never mix `await` with `.Result` or `.Wait()` — causes deadlocks |
| **Async void = event handlers only** | Exceptions in `async void` cannot be caught by caller |
| **Return Task, not void** | Enables caller to await and handle exceptions |

**Also see**: [TAP](#tap), [Task](#task), [ConfigureAwait](#configureawait)

---

## ThreadPool

A **managed pool of reusable worker threads**. `Task.Run` and `ThreadPool.QueueUserWorkItem` schedule work on the ThreadPool. Avoid creating raw Threads — use the ThreadPool for all short-lived background work.

**Also see**: [Task](#task), [TAP](#tap)

---

## ConfigureAwait

`ConfigureAwait(false)` prevents **marshaling back to the original SynchronizationContext** after an await. Use in **library code** to avoid deadlocks. Do NOT use in UI-thread code that must return to the UI context.

```csharp
// Library code: always use ConfigureAwait(false)
var data = await httpClient.GetStringAsync(url).ConfigureAwait(false);
```

**Also see**: [SynchronizationContext](#synchronizationcontext), [Deadlock](#deadlock)

---

## SynchronizationContext

An abstraction that **marshals continuations to a specific threading model** (e.g., UI thread in WinForms/WPF, single-threaded context in ASP.NET Classic). In ASP.NET Core, there is no SynchronizationContext.

**Also see**: [ConfigureAwait](#configureawait), [async/await](#async-await)

---

## CancellationToken

A **cooperative cancellation mechanism** propagated through the async call chain. Created by `CancellationTokenSource`. Every cancellable async method should accept an optional CancellationToken.

```csharp
var cts = new CancellationTokenSource(TimeSpan.FromSeconds(30));
var result = await ProcessAsync(data, cts.Token);
```

**Also see**: [Task](#task), [TAP](#tap)

---

## SemaphoreSlim

A **lightweight, async-friendly semaphore** for throttling concurrency within a single process. Use `WaitAsync()` to asynchronously acquire. Ideal for limiting concurrent I/O operations.

```csharp
var semaphore = new SemaphoreSlim(10); // Max 10 concurrent
await semaphore.WaitAsync();
try { /* bounded work */ }
finally { semaphore.Release(); }
```

**Also see**: [Mutex](#mutex), [Monitor/lock](#monitor-lock)

---

## Mutex

A **cross-process mutual exclusion** primitive. Use for "only one instance" patterns. Heavier than `lock` — only use when cross-process synchronization is required.

**Also see**: [Monitor/lock](#monitor-lock), [SemaphoreSlim](#semaphoreslim)

---

## Monitor / lock

The **primary single-process mutual exclusion** mechanism. `lock(obj)` is syntactic sugar for `Monitor.Enter`/`Monitor.Exit` with a try-finally. Use for protecting critical sections.

```csharp
private readonly object _lock = new();
lock (_lock)
{
    // Critical section — one thread at a time
}
```

**Also see**: [Mutex](#mutex), [ReaderWriterLockSlim](#readerwriterlockslim), [Deadlock](#deadlock)

---

## ReaderWriterLockSlim

Allows **multiple concurrent readers OR one exclusive writer**. Writers wait until all readers exit. Supports upgradeable read locks (read → write atomically). Use when reads significantly outnumber writes.

**Also see**: [Monitor/lock](#monitor-lock)

---

## Barrier

**Phase synchronization** — all participants must reach the barrier before any can continue. Use for multi-step algorithms where each phase must complete across all threads before the next begins.

**Also see**: [CountdownEvent](#countdownevent)

---

## CountdownEvent

Signals when a **counter reaches zero**. Threads call `Signal()` to decrement; waiters call `Wait()` which blocks until the count hits zero. Use when waiting for N parallel operations to complete.

**Also see**: [Barrier](#barrier), [Task.WhenAll](#task)

---

## Channel\<T\>

`System.Threading.Channels.Channel<T>` — a **high-performance, thread-safe producer/consumer data structure** for passing data between tasks and threads. Modern replacement for `BlockingCollection<T>`.

Two modes: **Unbounded** (grows without limit, `WriteAsync` never blocks) and **Bounded** (fixed capacity with configurable backpressure — `Wait`, `DropOldest`, `DropNewest`, `DropWrite`). Supports `SingleReader`/`SingleWriter` optimizations that elide internal locks for ~30-50% throughput gain.

**Also see**: [Task](#task), [SemaphoreSlim](#semaphoreslim)

---

## Interlocked

**Atomic operations** for lock-free thread-safe code. No locks, no contention — hardware-level atomicity.

| Method | Use |
|:---|:---|
| `Interlocked.Increment` | Atomic counter increment |
| `Interlocked.Exchange` | Atomic swap |
| `Interlocked.CompareExchange` | CAS — atomic compare-and-swap |

**Also see**: [Monitor/lock](#monitor-lock)

---

## Deadlock

Two or more threads **waiting on each other forever**. Common cause in .NET: mixing `async`/`await` with `.Result` or `.Wait()` in SynchronizationContext environments.

**Also see**: [ConfigureAwait](#configureawait), [Monitor/lock](#monitor-lock)

---

## EAP / APM

| Pattern | Mechanism | Status |
|:---|:---|:---|
| **APM** | `BeginXxx`/`EndXxx` with `IAsyncResult` | Legacy — do not use |
| **EAP** | `MethodAsync()` + `MethodCompleted` event | Legacy — do not use |
| **TAP** | `async Task<T> MethodAsync()` | **Use this** |

**Also see**: [TAP](#tap)
