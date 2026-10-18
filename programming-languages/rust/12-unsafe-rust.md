---
type: Programming Guide
title: "Rust — Unsafe Rust"
description: "When and how to use unsafe Rust: raw pointers, FFI, unsafe blocks, and safety invariants."
tags: [rust, unsafe, ffi, raw-pointers, memory]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Unsafe Rust

## Table of Contents
- [What Is Unsafe Rust?](#what-is-unsafe-rust)
- [The Five Unsafe Superpowers](#the-five-unsafe-superpowers)
- [Raw Pointers](#raw-pointers)
- [Unsafe Functions & Blocks](#unsafe-functions--blocks)
- [FFI — Calling C from Rust](#ffi--calling-c-from-rust)
- [FFI — Calling Rust from C](#ffi--calling-rust-from-c)
- [Global Mutable State](#global-mutable-state)
- [Implementing Unsafe Traits](#implementing-unsafe-traits)
- [Guidelines & Safety Comments](#guidelines--safety-comments)

---

## What Is Unsafe Rust?

Unsafe Rust does **not** disable the borrow checker. It grants access to five additional capabilities that safe Rust cannot express. The vast majority of code should never use `unsafe`.

**Safe Rust guarantees** (always hold):
- No dangling references
- No data races
- No buffer overflows (panics instead)

**Unsafe Rust** opts out of some compile-time checks for specific operations where the programmer vouches for correctness.

---

## The Five Unsafe Superpowers

| Capability | Description |
|-----------|-------------|
| Dereference raw pointers | `*const T` / `*mut T` |
| Call unsafe functions or methods | Including `extern` C functions |
| Access or modify a mutable static variable | Global mutable state |
| Implement an unsafe trait | `Send`, `Sync`, `GlobalAlloc` |
| Access fields of `union` types | Used in FFI |

---

## Raw Pointers

Raw pointers are like C pointers: nullable, not lifetime-tracked, can alias freely.

```rust
let mut val = 5;

// Creating raw pointers is safe; dereferencing requires unsafe
let r1 = &val as *const i32;     // immutable raw pointer
let r2 = &mut val as *mut i32;   // mutable raw pointer

// Dereferencing — unsafe block required
unsafe {
    println!("r1 = {}", *r1);
    *r2 = 10;
    println!("r2 = {}", *r2);
}

// From a box — take ownership back
let boxed = Box::new(42i32);
let raw = Box::into_raw(boxed); // raw: *mut i32, Box dropped (leak without below)
unsafe {
    println!("raw = {}", *raw);
    drop(Box::from_raw(raw)); // reconstruct Box so it's properly freed
}
```

---

## Unsafe Functions & Blocks

An `unsafe fn` signals to callers that they must uphold invariants the compiler cannot check:

```rust
/// # Safety
/// The caller must ensure `ptr` points to a valid, aligned `i32`
/// that lives at least as long as the returned reference.
unsafe fn raw_ref<'a>(ptr: *const i32) -> &'a i32 {
    &*ptr
}

fn main() {
    let x = 42i32;
    let r = unsafe { raw_ref(&x as *const i32) };
    println!("{r}");
}
```

Minimize `unsafe` scope — the block should be as small as possible:

```rust
// ❌ Large unsafe block — hard to audit
unsafe {
    let result = ffi_function();
    let text = String::from("hello");  // safe — no need to be here
    process(&text, result);
}

// ✅ Minimal unsafe block
let result = unsafe { ffi_function() };
let text = String::from("hello");
process(&text, result);
```

---

## FFI — Calling C from Rust

```rust
// Link to the C standard library
extern "C" {
    fn abs(input: i32) -> i32;
    fn strlen(s: *const std::os::raw::c_char) -> usize;
}

fn main() {
    let x = unsafe { abs(-5) };
    println!("abs(-5) = {x}");
}
```

### Linking to a Custom C Library

```toml
# Cargo.toml
[build-dependencies]
cc = "1"
```

```rust
// build.rs
fn main() {
    cc::Build::new().file("src/mylib.c").compile("mylib");
}
```

```rust
// src/main.rs
extern "C" {
    fn my_c_function(x: i32) -> i32;
}

fn main() {
    let result = unsafe { my_c_function(42) };
    println!("{result}");
}
```

### Type Correspondence

| C type | Rust type |
|--------|-----------|
| `int` | `std::os::raw::c_int` |
| `char *` | `*const std::os::raw::c_char` |
| `void *` | `*mut std::ffi::c_void` |
| `size_t` | `usize` |
| `uint8_t` | `u8` |

Use the `bindgen` crate to auto-generate FFI bindings from C headers.

---

## FFI — Calling Rust from C

```rust
// Mark as C-compatible (no name mangling, C ABI)
#[no_mangle]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}
```

```toml
# Cargo.toml — produce a C-compatible shared/static library
[lib]
crate-type = ["cdylib"]  # or "staticlib"
```

```c
// C header (rust_add.h)
extern int rust_add(int a, int b);
```

---

## Global Mutable State

Mutable statics require `unsafe` to read or write:

```rust
static mut COUNTER: u32 = 0;

fn increment() {
    unsafe {
        COUNTER += 1; // unsafe — not thread-safe!
    }
}
```

Prefer thread-safe alternatives:

```rust
use std::sync::atomic::{AtomicU32, Ordering};

static COUNTER: AtomicU32 = AtomicU32::new(0);

fn increment() {
    COUNTER.fetch_add(1, Ordering::Relaxed); // safe, no unsafe block needed
}

fn get() -> u32 {
    COUNTER.load(Ordering::Relaxed)
}
```

Or use `OnceLock` / `LazyLock` for one-time initialization:

```rust
use std::sync::OnceLock;

static CONFIG: OnceLock<String> = OnceLock::new();

fn get_config() -> &'static str {
    CONFIG.get_or_init(|| "default-config".to_string())
}
```

---

## Implementing Unsafe Traits

`unsafe trait` marks a trait where the implementor must uphold invariants the compiler cannot verify:

```rust
unsafe trait Aligned {
    fn is_aligned(&self) -> bool;
}

struct AlignedBuffer([u8; 64]);

// The programmer vouches this is always 64-byte aligned
unsafe impl Aligned for AlignedBuffer {
    fn is_aligned(&self) -> bool { true }
}
```

The most common unsafe traits are `Send` and `Sync`. Only implement them manually when you have a type that is safe to share across threads but the compiler can't automatically determine it (e.g., a wrapper around a raw pointer):

```rust
struct MySafePtr(*mut i32);

// We know this is safe because our API guarantees exclusive access
unsafe impl Send for MySafePtr {}
unsafe impl Sync for MySafePtr {}
```

---

## Guidelines & Safety Comments

Every `unsafe` block should have a `// SAFETY:` comment explaining why it is correct:

```rust
let v: Vec<i32> = vec![1, 2, 3];
let ptr = v.as_ptr();

// SAFETY: `ptr` is non-null and points to the first element of `v`.
// `v` is alive for the duration of this scope. The offset 0 is within bounds.
let first = unsafe { &*ptr };
println!("{first}");
```

### Encapsulate Unsafe Behind Safe APIs

The best pattern is to write a small `unsafe` core and expose a fully safe public API:

```rust
pub struct MyBuffer {
    ptr: *mut u8,
    len: usize,
    cap: usize,
}

impl MyBuffer {
    pub fn new(capacity: usize) -> Self {
        let layout = std::alloc::Layout::array::<u8>(capacity).unwrap();
        // SAFETY: capacity > 0; layout is valid
        let ptr = unsafe { std::alloc::alloc(layout) };
        MyBuffer { ptr, len: 0, cap: capacity }
    }

    pub fn push(&mut self, byte: u8) {
        assert!(self.len < self.cap, "buffer overflow");
        // SAFETY: len < cap; ptr is valid for cap bytes; offset in bounds
        unsafe { *self.ptr.add(self.len) = byte; }
        self.len += 1;
    }
}

impl Drop for MyBuffer {
    fn drop(&mut self) {
        let layout = std::alloc::Layout::array::<u8>(self.cap).unwrap();
        // SAFETY: ptr was allocated with the same layout
        unsafe { std::alloc::dealloc(self.ptr, layout); }
    }
}
```

---

> **Previous**: [11 — Async/Await & Tokio](./11-async-tokio.md)  
> **Next**: [13 — Testing & Benchmarking](./13-testing-benchmarking.md)
