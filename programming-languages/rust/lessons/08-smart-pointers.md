---
type: Programming Guide
title: "Rust — Smart Pointers & Interior Mutability"
description: "Box<T>, Rc<T>, Arc<T>, Cell<T>, RefCell<T>, Mutex<T>, and the patterns they enable."
tags: [rust, smart-pointers, box, rc, arc, refcell, mutex, interior-mutability]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Smart Pointers & Interior Mutability

## Table of Contents
- [What Are Smart Pointers?](#what-are-smart-pointers)
- [`Box<T>` — Heap Allocation](#boxt--heap-allocation)
- [`Rc<T>` — Reference Counted (Single-thread)](#rct--reference-counted-single-thread)
- [`Arc<T>` — Atomic Reference Counted (Multi-thread)](#arct--atomic-reference-counted-multi-thread)
- [Interior Mutability — `Cell<T>` & `RefCell<T>`](#interior-mutability--cellt--refcellt)
- [`Mutex<T>` & `RwLock<T>`](#mutext--rwlockt)
- [`Cow<T>` — Clone-on-Write](#cowt--clone-on-write)
- [Choosing the Right Pointer](#choosing-the-right-pointer)

---

## What Are Smart Pointers?

Smart pointers implement `Deref` and `Drop` traits. `Deref` allows them to behave like regular references. `Drop` runs cleanup when they go out of scope.

| Type | Ownership | Thread-safe | Mutability |
|------|-----------|-------------|-----------|
| `Box<T>` | Single | ✅ (if T: Send) | Mutable |
| `Rc<T>` | Shared | ❌ | Immutable (use `RefCell` to mutate) |
| `Arc<T>` | Shared | ✅ | Immutable (use `Mutex` to mutate) |
| `Cell<T>` | Single | ❌ | Interior (Copy types only) |
| `RefCell<T>` | Single | ❌ | Interior (runtime borrow checking) |
| `Mutex<T>` | Shared | ✅ | Interior (thread-safe, blocking) |
| `RwLock<T>` | Shared | ✅ | Interior (many readers or one writer) |

---

## `Box<T>` — Heap Allocation

`Box<T>` stores data on the heap and owns it. Use when:
- The type's size is not known at compile time (e.g., recursive types)
- You have a large value and want to avoid stack copies

```rust
// Recursive type — must be boxed to have a known size
#[derive(Debug)]
enum List {
    Cons(i32, Box<List>),
    Nil,
}

let list = List::Cons(1,
    Box::new(List::Cons(2,
        Box::new(List::Nil))));
println!("{list:?}");

// Trait objects
let b: Box<dyn std::fmt::Display> = Box::new(42);
println!("{b}");
```

`Box<T>` implements `Deref` so you can use it like a normal reference:

```rust
let x = Box::new(5);
let y = *x; // Deref coercion: dereferences to 5
```

---

## `Rc<T>` — Reference Counted (Single-thread)

Multiple owners of the same heap value (in single-threaded code):

```rust
use std::rc::Rc;

let a = Rc::new(5);
let b = Rc::clone(&a); // increments reference count, doesn't deep-copy
let c = Rc::clone(&a);

println!("count = {}", Rc::strong_count(&a)); // 3
println!("a={a}, b={b}, c={c}");
// a, b, c dropped → count reaches 0 → value freed
```

`Rc<T>` is **not thread-safe** (`not Send`). Use `Arc<T>` across threads.

### `Rc<RefCell<T>>` — Shared Mutable Data (Single Thread)

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(vec![1, 2, 3]));

let a = Rc::clone(&shared);
let b = Rc::clone(&shared);

a.borrow_mut().push(4);
b.borrow_mut().push(5);

println!("{:?}", shared.borrow()); // [1, 2, 3, 4, 5]
```

---

## `Arc<T>` — Atomic Reference Counted (Multi-thread)

`Arc<T>` is `Rc<T>` with atomic (thread-safe) reference counting:

```rust
use std::sync::Arc;
use std::thread;

let data = Arc::new(vec![1, 2, 3]);

let handles: Vec<_> = (0..3).map(|_| {
    let data = Arc::clone(&data);
    thread::spawn(move || {
        println!("{:?}", data);
    })
}).collect();

for h in handles { h.join().unwrap(); }
```

### `Arc<Mutex<T>>` — Shared Mutable Data (Multi-thread)

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));

let handles: Vec<_> = (0..10).map(|_| {
    let counter = Arc::clone(&counter);
    thread::spawn(move || {
        let mut val = counter.lock().unwrap(); // blocks until lock acquired
        *val += 1;
    })
}).collect();

for h in handles { h.join().unwrap(); }
println!("counter = {}", *counter.lock().unwrap()); // 10
```

---

## Interior Mutability — `Cell<T>` & `RefCell<T>`

**Interior mutability** allows mutation through a shared (`&`) reference. The borrow rules are enforced at **runtime** instead of compile time.

### `Cell<T>` — Copy Types, No Borrow

```rust
use std::cell::Cell;

let cell = Cell::new(42);
cell.set(100);               // mutate through shared reference
let val = cell.get();        // copy the value
println!("{val}");           // 100
```

### `RefCell<T>` — Dynamic Borrow Checking

```rust
use std::cell::RefCell;

let data = RefCell::new(vec![1, 2, 3]);

// Immutable borrow
let r = data.borrow();
println!("{:?}", *r);
drop(r); // release borrow before taking a mutable one

// Mutable borrow
data.borrow_mut().push(4);
println!("{:?}", data.borrow()); // [1, 2, 3, 4]
```

**Panics at runtime** if borrow rules are violated (two mutable borrows, or mutable + immutable simultaneously):

```rust
let cell = RefCell::new(0);
let r1 = cell.borrow_mut();
// let r2 = cell.borrow_mut(); // ❌ panics: already mutably borrowed
```

---

## `Mutex<T>` & `RwLock<T>`

Covered in depth in [10 — Concurrency](./10-concurrency.md). Brief comparison:

```rust
use std::sync::{Mutex, RwLock};

// Mutex: exclusive access (one reader OR one writer)
let m = Mutex::new(0);
*m.lock().unwrap() += 1;

// RwLock: multiple readers OR one writer
let rw = RwLock::new(0);
{
    let r1 = rw.read().unwrap(); // many readers at once
    let r2 = rw.read().unwrap();
    println!("{} {}", *r1, *r2);
} // readers released
*rw.write().unwrap() = 42;  // exclusive write
```

---

## `Cow<T>` — Clone-on-Write

`Cow<'a, B>` is either a borrowed reference or an owned value — it clones lazily only when mutation is needed:

```rust
use std::borrow::Cow;

fn ensure_no_trailing_slash(s: &str) -> Cow<str> {
    if s.ends_with('/') {
        Cow::Owned(s.trim_end_matches('/').to_string()) // clone only if needed
    } else {
        Cow::Borrowed(s) // zero-copy when no change needed
    }
}

let clean = ensure_no_trailing_slash("https://example.com/");
println!("{clean}"); // https://example.com
```

---

## Choosing the Right Pointer

```
Single owner, heap allocation?      → Box<T>
Multiple owners, single thread?     → Rc<T>
Multiple owners, multiple threads?  → Arc<T>
Mutate through shared ref, Copy T?  → Cell<T>
Mutate through shared ref, non-Copy? → RefCell<T> (single thread)
                                       Mutex<T>   (multi thread)
Many readers, occasional writer?    → RwLock<T>
Avoid clone when data unchanged?    → Cow<'a, B>
```

---

> **Previous**: [07 — Lifetimes](./07-lifetimes.md)  
> **Next**: [09 — Iterators & Closures](./09-iterators-closures.md)
