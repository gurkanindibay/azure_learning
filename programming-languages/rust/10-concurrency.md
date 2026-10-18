---
type: Programming Guide
title: "Rust — Concurrency"
description: "Threads, channels, Mutex, RwLock, Arc, and the Send/Sync marker traits that enforce thread safety at compile time."
tags: [rust, concurrency, threads, channels, mutex, rwlock, arc, send, sync]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Concurrency

## Table of Contents
- [Rust's Concurrency Guarantees](#rusts-concurrency-guarantees)
- [Threads](#threads)
- [`Send` and `Sync` Traits](#send-and-sync-traits)
- [Channels — Message Passing](#channels--message-passing)
- [`Mutex<T>` — Shared State](#mutext--shared-state)
- [`RwLock<T>` — Reader-Writer Lock](#rwlockt--readerwriter-lock)
- [`Condvar` — Condition Variables](#condvar--condition-variables)
- [Thread-local Storage](#thread-local-storage)
- [Rayon — Data Parallelism](#rayon--data-parallelism)
- [Common Patterns](#common-patterns)

---

## Rust's Concurrency Guarantees

Rust prevents data races at **compile time** through its type system:
- **No shared mutable state** without synchronization (enforced by `Send`/`Sync`)
- **Ownership rules** prevent concurrent mutation and aliasing simultaneously
- **No implicit sharing** — all sharing must go through explicit types (`Arc`, channels)

This eliminates an entire class of bugs that C, C++, Java, and C# find only at runtime (or not at all).

---

## Threads

```rust
use std::thread;
use std::time::Duration;

// Spawn a thread — returns JoinHandle<T>
let handle = thread::spawn(|| {
    for i in 0..5 {
        println!("thread: {i}");
        thread::sleep(Duration::from_millis(10));
    }
});

for i in 0..3 {
    println!("main: {i}");
}

handle.join().unwrap(); // wait for the thread to finish
```

### Moving Data into Threads

The `move` keyword transfers ownership of captured variables into the thread:

```rust
let data = vec![1, 2, 3];

let handle = thread::spawn(move || {
    println!("{data:?}"); // data moved into the closure
});

// println!("{data:?}"); // ❌ data was moved
handle.join().unwrap();
```

---

## `Send` and `Sync` Traits

These are **marker traits** (no methods) that the compiler enforces automatically:

| Trait | Meaning | Example |
|-------|---------|---------|
| `Send` | Ownership can be transferred to another thread | `String`, `Vec<T>`, `Mutex<T>` |
| `Sync` | A `&T` can be shared between threads (T is safe to reference concurrently) | `i32`, `Arc<T>`, `Mutex<T>` |
| Not `Send` | Must stay on the same thread | `Rc<T>`, `Cell<T>`, `RefCell<T>` |
| Not `Sync` | `&T` cannot cross threads | `Cell<T>`, `RefCell<T>`, `*mut T` |

The compiler automatically derives `Send`/`Sync` for types where all fields are `Send`/`Sync`. You cannot accidentally share non-thread-safe types across threads.

---

## Channels — Message Passing

Channels implement the **CSP (Communicating Sequential Processes)** model: threads communicate by sending messages, not by sharing memory.

### `std::sync::mpsc` — Multiple Producer, Single Consumer

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();

// Multiple senders
let tx2 = tx.clone();

thread::spawn(move || { tx.send("hello from thread 1").unwrap(); });
thread::spawn(move || { tx2.send("hello from thread 2").unwrap(); });

for received in rx { // rx is an iterator; stops when all senders are dropped
    println!("Got: {received}");
}
```

### Bounded Channel (backpressure)

```rust
let (tx, rx) = mpsc::sync_channel(10); // buffer of 10 — sender blocks when full

thread::spawn(move || {
    for i in 0..20 {
        tx.send(i).unwrap(); // blocks if buffer full
    }
});

for val in rx {
    println!("{val}");
}
```

For more powerful async channels, use `tokio::sync::mpsc` (see [11 — Async/Tokio](./11-async-tokio.md)).

---

## `Mutex<T>` — Shared State

`Mutex<T>` wraps data and enforces exclusive access through a lock:

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));

let handles: Vec<_> = (0..10).map(|_| {
    let counter = Arc::clone(&counter);
    thread::spawn(move || {
        let mut num = counter.lock().unwrap(); // blocks until lock acquired
        *num += 1;
        // Lock released automatically when `num` (MutexGuard) is dropped
    })
}).collect();

for h in handles { h.join().unwrap(); }
println!("Result: {}", *counter.lock().unwrap()); // 10
```

### Avoiding Deadlocks

```rust
// ❌ Deadlock: locking the same mutex twice in the same thread
let m = Mutex::new(0);
let g1 = m.lock().unwrap();
// let g2 = m.lock().unwrap(); // blocks forever — g1 never released

// ✅ Drop the guard before trying to lock again
drop(g1);
let g2 = m.lock().unwrap();
```

### Poisoned Mutex

If a thread panics while holding the lock, the mutex becomes **poisoned**. `lock()` returns `Err` from that point. Use `.unwrap()` or handle the error:

```rust
let result = counter.lock();
match result {
    Ok(guard)  => { /* use guard */ }
    Err(poisoned) => {
        let guard = poisoned.into_inner(); // recover the guard anyway
        // ...
    }
}
```

---

## `RwLock<T>` — Reader-Writer Lock

Allows **many concurrent readers** or **one exclusive writer**:

```rust
use std::sync::{Arc, RwLock};

let config = Arc::new(RwLock::new(String::from("initial")));

// Multiple concurrent readers
let c = Arc::clone(&config);
thread::spawn(move || {
    let data = c.read().unwrap();
    println!("reader 1: {data}");
});

// Exclusive writer — blocks while any reader holds a lock
*config.write().unwrap() = String::from("updated");
```

Use `RwLock` when reads are frequent and writes are rare. If writes are frequent, `Mutex` is simpler and often faster.

---

## `Condvar` — Condition Variables

Coordinates threads by waiting for a condition to become true:

```rust
use std::sync::{Arc, Mutex, Condvar};

let pair = Arc::new((Mutex::new(false), Condvar::new()));
let pair2 = Arc::clone(&pair);

// Waiting thread
thread::spawn(move || {
    let (lock, cvar) = &*pair2;
    let mut started = lock.lock().unwrap();
    while !*started {
        started = cvar.wait(started).unwrap(); // atomically releases lock and waits
    }
    println!("Worker: signal received!");
});

// Signal thread
thread::sleep(Duration::from_millis(100));
let (lock, cvar) = &*pair;
*lock.lock().unwrap() = true;
cvar.notify_one(); // wake up one waiting thread
```

---

## Thread-local Storage

`thread_local!` defines storage that is unique to each thread:

```rust
use std::cell::RefCell;

thread_local! {
    static REQUEST_ID: RefCell<u64> = RefCell::new(0);
}

fn set_request_id(id: u64) {
    REQUEST_ID.with(|r| *r.borrow_mut() = id);
}

fn get_request_id() -> u64 {
    REQUEST_ID.with(|r| *r.borrow())
}
```

---

## Rayon — Data Parallelism

[Rayon](https://docs.rs/rayon) provides parallel iterators with minimal code change:

```toml
[dependencies]
rayon = "1"
```

```rust
use rayon::prelude::*;

let v: Vec<i32> = (0..1_000_000).collect();

// Sequential
let sum: i64 = v.iter().map(|&x| x as i64 * x as i64).sum();

// Parallel — just change iter() to par_iter()
let par_sum: i64 = v.par_iter().map(|&x| x as i64 * x as i64).sum();

assert_eq!(sum, par_sum);
```

Rayon automatically manages a thread pool sized to the number of CPU cores.

---

## Common Patterns

### Worker Pool

```rust
use std::sync::{Arc, Mutex};
use std::sync::mpsc;

let (tx, rx) = mpsc::channel::<Box<dyn FnOnce() + Send>>();
let rx = Arc::new(Mutex::new(rx));

let workers: Vec<_> = (0..4).map(|id| {
    let rx = Arc::clone(&rx);
    thread::spawn(move || loop {
        let job = rx.lock().unwrap().recv();
        match job {
            Ok(job) => { println!("Worker {id} executing"); job(); }
            Err(_)  => { println!("Worker {id} shutting down"); break; }
        }
    })
}).collect();

// Submit jobs
tx.send(Box::new(|| println!("Job 1"))).unwrap();
tx.send(Box::new(|| println!("Job 2"))).unwrap();

drop(tx); // close channel — workers will drain then exit
for w in workers { w.join().unwrap(); }
```

---

> **Previous**: [09 — Iterators & Closures](./09-iterators-closures.md)  
> **Next**: [11 — Async/Await & Tokio](./11-async-tokio.md)
