---
type: Programming Guide
title: "Rust — Async/Await & Tokio"
description: "The Future trait, async/await syntax, the Tokio runtime, tasks, channels, and common async patterns."
tags: [rust, async, await, tokio, future, runtime, async-std]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Async/Await & Tokio

## Table of Contents
- [Why Async?](#why-async)
- [Futures](#futures)
- [`async`/`await` Syntax](#asyncawait-syntax)
- [Runtimes — Tokio vs async-std](#runtimes--tokio-vs-async-std)
- [Tokio Tasks](#tokio-tasks)
- [Async Channels](#async-channels)
- [Timeouts & Cancellation](#timeouts--cancellation)
- [Common Async Patterns](#common-async-patterns)
- [Async Traits](#async-traits)
- [Pitfalls](#pitfalls)

---

## Why Async?

| Model | Cost per 10k concurrent operations |
|-------|-----------------------------------|
| OS Threads (blocking) | ~80 MB RAM, high context-switch overhead |
| Async tasks (Tokio) | ~2 MB RAM, minimal overhead |

Async Rust enables **high-throughput I/O-bound** applications (web servers, database clients, network services) with minimal resource usage — similar to Go's goroutines or .NET's async/await over the CLR thread pool.

---

## Futures

A `Future` is a value that represents a computation that might not have completed yet. Polling it drives it toward completion.

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}

pub enum Poll<T> {
    Ready(T),
    Pending,   // not done yet; will wake via Waker
}
```

You almost never implement `Future` manually — the compiler generates the state machine for you from `async`/`await`.

---

## `async`/`await` Syntax

`async fn` returns a `Future`. `await` suspends execution until the future is ready, yielding control back to the runtime (non-blocking).

```rust
async fn fetch_user(id: u64) -> Result<String, reqwest::Error> {
    let url = format!("https://api.example.com/users/{id}");
    let response = reqwest::get(&url).await?; // suspend here while waiting for I/O
    let body = response.text().await?;        // suspend again
    Ok(body)
}
```

Futures are **lazy** — they do nothing until polled by a runtime.

---

## Runtimes — Tokio vs async-std

| | Tokio | async-std |
|--|-------|-----------|
| Maturity | Very stable, widest ecosystem | Stable |
| Scheduler | Work-stealing multi-thread | Work-stealing multi-thread |
| I/O driver | epoll/kqueue/IOCP | epoll/kqueue/IOCP |
| Ecosystem | Axum, Hyper, Tonic, SQLx, ... | Smaller |
| Recommendation | ✅ Default choice | Alternative if std-like API preferred |

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

```rust
#[tokio::main]
async fn main() {
    // main is now async — Tokio runtime is set up automatically
    println!("Hello from async main!");
}

// Equivalent manual setup
fn main() {
    tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(async_main());
}

async fn async_main() {
    // ...
}
```

---

## Tokio Tasks

Tasks are **lightweight green threads** managed by Tokio (like goroutines):

```rust
use tokio::task;

#[tokio::main]
async fn main() {
    let handle = task::spawn(async {
        // runs concurrently — not in parallel by default on single-thread runtime
        42
    });

    let result = handle.await.unwrap();
    println!("Task returned: {result}");
}
```

### Concurrent Tasks

```rust
use tokio::task;

async fn fetch(id: u32) -> String {
    // simulate async I/O
    tokio::time::sleep(std::time::Duration::from_millis(100)).await;
    format!("data-{id}")
}

#[tokio::main]
async fn main() {
    // Launch 10 concurrent fetches
    let handles: Vec<_> = (0..10).map(|i| task::spawn(fetch(i))).collect();

    let results: Vec<String> = futures::future::join_all(handles)
        .await
        .into_iter()
        .map(|r| r.unwrap())
        .collect();

    println!("{results:?}");
}
```

### `join!` Macro — Concurrent, Not Sequential

```rust
let (a, b, c) = tokio::join!(fetch(1), fetch(2), fetch(3));
// All three run concurrently; total time ≈ max(each), not sum
```

---

## Async Channels

Tokio provides async-native channels:

```rust
use tokio::sync::mpsc;

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel::<String>(32); // buffer of 32

    let tx2 = tx.clone();

    tokio::spawn(async move {
        tx.send("hello".to_string()).await.unwrap();
    });

    tokio::spawn(async move {
        tx2.send("world".to_string()).await.unwrap();
    });

    while let Some(msg) = rx.recv().await {
        println!("Received: {msg}");
    }
}
```

### Other Tokio Channel Types

| Type | Use case |
|------|----------|
| `mpsc` | Multiple producers, single consumer |
| `oneshot` | Send exactly one value (e.g., request/response) |
| `broadcast` | One sender, many receivers (fan-out) |
| `watch` | Share the latest value (e.g., config updates) |

---

## Timeouts & Cancellation

```rust
use tokio::time::{timeout, Duration};

async fn slow_operation() -> String {
    tokio::time::sleep(Duration::from_secs(10)).await;
    "done".to_string()
}

#[tokio::main]
async fn main() {
    match timeout(Duration::from_secs(2), slow_operation()).await {
        Ok(result) => println!("Got: {result}"),
        Err(_)     => println!("Timed out!"),
    }
}
```

Tokio tasks are cancelled by dropping their `JoinHandle` or using `CancellationToken` (from `tokio-util`):

```rust
use tokio_util::sync::CancellationToken;

let token = CancellationToken::new();
let child = token.child_token();

tokio::spawn(async move {
    tokio::select! {
        _ = child.cancelled() => println!("Task cancelled"),
        _ = do_work()         => println!("Work done"),
    }
});

token.cancel(); // signal cancellation
```

---

## Common Async Patterns

### `select!` — Race Multiple Futures

```rust
tokio::select! {
    result = fetch(1) => println!("fetch 1 won: {result}"),
    result = fetch(2) => println!("fetch 2 won: {result}"),
    _ = tokio::signal::ctrl_c() => println!("Ctrl-C received"),
}
// Only one branch executes; others are dropped (cancelled)
```

### Streams — Async Iterators

```rust
use tokio_stream::{self as stream, StreamExt};

let mut s = stream::iter(vec![1, 2, 3]);
while let Some(item) = s.next().await {
    println!("{item}");
}
```

---

## Async Traits

`async fn` in traits requires the `async-trait` crate (or nightly):

```toml
[dependencies]
async-trait = "0.1"
```

```rust
use async_trait::async_trait;

#[async_trait]
trait DataFetcher {
    async fn fetch(&self, id: u64) -> Result<String, anyhow::Error>;
}

struct HttpFetcher;

#[async_trait]
impl DataFetcher for HttpFetcher {
    async fn fetch(&self, id: u64) -> Result<String, anyhow::Error> {
        Ok(format!("data-{id}"))
    }
}
```

> **Rust 1.75+**: `async fn` in traits is now supported natively without `async-trait` for non-object-safe cases.

---

## Pitfalls

### Holding a `MutexGuard` across `.await`

```rust
// ❌ std::Mutex guard is not Send — cannot hold across .await
let data = std::sync::Mutex::new(0);
let guard = data.lock().unwrap();
some_async_fn().await; // guard held here — may cross threads!

// ✅ Use tokio::sync::Mutex for async code
let data = tokio::sync::Mutex::new(0);
let mut guard = data.lock().await;
*guard += 1;
some_async_fn().await; // guard is Send ✅
```

### Blocking in Async Context

```rust
// ❌ Blocks the async runtime thread — starves other tasks
async fn bad() {
    std::thread::sleep(std::time::Duration::from_secs(1)); // BLOCKING!
}

// ✅ Use async sleep
async fn good() {
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
}

// ✅ For unavoidable blocking work (CPU-heavy or blocking I/O)
async fn cpu_heavy() -> i64 {
    tokio::task::spawn_blocking(|| {
        (0..1_000_000i64).sum() // runs on a dedicated thread pool
    }).await.unwrap()
}
```

---

> **Previous**: [10 — Concurrency](./10-concurrency.md)  
> **Next**: [12 — Unsafe Rust](./12-unsafe-rust.md)
