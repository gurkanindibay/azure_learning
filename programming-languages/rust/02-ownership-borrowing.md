---
type: Programming Guide
title: "Rust — Ownership & Borrowing"
description: "The cornerstone of Rust's memory safety guarantees: ownership, move semantics, borrowing, and an introduction to lifetimes."
tags: [rust, ownership, borrowing, lifetimes, memory-safety]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Ownership & Borrowing

## Table of Contents
- [Why Ownership?](#why-ownership)
- [Ownership Rules](#ownership-rules)
  - [The `Drop` Trait vs. The `new()` Convention](#the-drop-trait-vs-the-new-convention)
- [Move Semantics](#move-semantics)
- [Clone vs Copy](#clone-vs-copy)
- [Borrowing & References](#borrowing--references)
- [The Borrow Checker](#the-borrow-checker)
- [Slices](#slices)
- [Lifetimes — Introduction](#lifetimes--introduction)
- [Common Pitfalls](#common-pitfalls)

---

## Why Ownership?

Rust eliminates entire classes of bugs at **compile time** with no runtime overhead:

| Bug Class | How Rust Prevents It |
|-----------|---------------------|
| Use-after-free | Ownership ends at scope exit; no dangling pointers |
| Double-free | Each value has exactly one owner; drop called once |
| Data races | Borrow checker enforces exclusive mutable access |
| Null pointer dereference | References are always valid; use `Option<T>` instead of null |
| Buffer overflow | Slice bounds-checked at runtime |

---

## Ownership Rules

Three invariants the compiler enforces:

1. **Each value has exactly one owner.**
2. **When the owner goes out of scope, the value is dropped** (destructor called, memory freed).
3. **There can only be one owner at a time.**

```rust
{
    let s = String::from("hello"); // s owns the String
    // ... use s ...
} // s goes out of scope; String is dropped here
```

### The `Drop` Trait vs. The `new()` Convention

A common question for developers coming from languages like C++, Java, or C#: *is `drop` like `new`, and are they built into Rust?*

| Aspect | `Drop` | `new` |
|---|---|---|
| **What is it?** | A built-in trait (`std::ops::Drop`) | A convention for an associated function |
| **Compiler support?** | **Yes** — compiler automatically inserts drop calls at scope exit | **No** — it is standard user code |
| **Keyword?** | No keyword; `drop()` function in standard prelude | No keyword (unlike Java/C++/C#) |
| **Naming flexibility** | Fixed signature: `fn drop(&mut self)` | Any name: `new()`, `with_capacity()`, `default()` |

#### 1. `Drop` is Built-In and Compiler-Integrated
- **Automatic Destructor (RAII)**: When an owner leaves scope, the compiler automatically runs its `Drop::drop(&mut self)` implementation to free resources (heap memory, open file handles, sockets, locks).
- **Manual `.drop()` is forbidden**: You cannot write `x.drop()`; the compiler disallows manual invocation to prevent double-free bugs.
- **Early dropping with `std::mem::drop`**: To release a resource before scope exit, use the built-in function `drop(x)`, which takes ownership and lets the value drop:
  ```rust
  let lock = mutex.lock().unwrap();
  // ... work with protected data ...
  drop(lock); // explicitly drop lock early to unblock other threads
  ```

#### 2. `new` is NOT Built-In (It's a Convention)
- Rust has **no `new` keyword**.
- Structs are instantiated directly using struct literal syntax (`Point { x: 0, y: 0 }`).
- `Type::new(...)` is simply an associated function that the Rust community adopts as a constructor pattern:
  ```rust
  impl Rectangle {
      // Just a normal function returning Self — no special compiler magic:
      pub fn new(width: f64, height: f64) -> Self {
          Self { width, height }
      }
  }
  ```

---

## Move Semantics

Assigning or passing heap-allocated values **moves** ownership, not copies.

```rust
let s1 = String::from("hello");
let s2 = s1; // s1 is MOVED into s2

// println!("{}", s1); // ❌ compile error: value used after move
println!("{}", s2); // ✅
```

This is different from C++ (which copies by default) and C# (which reference-counts or GC-manages).

### Moving into functions

```rust
fn take_ownership(s: String) {
    println!("{s}");
} // s is dropped here

fn main() {
    let s = String::from("world");
    take_ownership(s);
    // println!("{s}"); // ❌ moved into the function
}
```

To retain ownership, either **clone** or **borrow**.

---

## Clone vs Copy

### Copy — stack-only, implicit

Types that are cheap to duplicate implement `Copy`. The value is bitwise-copied; no move occurs.

```rust
let x: i32 = 5;
let y = x;       // x is COPIED, not moved
println!("{x}"); // ✅ x is still valid
```

Types implementing `Copy`: `i32`, `f64`, `bool`, `char`, `(T, U)` where T & U are `Copy`, arrays of `Copy` types.

### Clone — explicit deep copy

```rust
let s1 = String::from("hello");
let s2 = s1.clone(); // explicit heap copy
println!("{s1} {s2}"); // ✅ both valid
```

> **Rule of thumb**: if `.clone()` is expensive (heap allocation), consider borrowing instead.

---

## Borrowing & References

A **reference** lets you refer to a value without taking ownership.

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
} // s is NOT dropped; it was borrowed

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s); // pass a reference
    println!("{s} has length {len}"); // ✅ s still valid
}
```

### Mutable References

```rust
fn append(s: &mut String) {
    s.push_str(" world");
}

fn main() {
    let mut s = String::from("hello");
    append(&mut s);
    println!("{s}"); // hello world
}
```

---

## The Borrow Checker

The compiler enforces these rules at any given point in the code:

| Rule | Details |
|------|---------|
| **Any number of shared references** | `&T` — read-only, many allowed |
| **Exactly one mutable reference** | `&mut T` — exclusive write access |
| **Not both at once** | No `&T` while `&mut T` is live |
| **References must not outlive the value** | Prevents dangling pointers |

```rust
let mut v = vec![1, 2, 3];

let r1 = &v;      // ✅ shared borrow
let r2 = &v;      // ✅ another shared borrow
println!("{r1:?} {r2:?}");
// r1, r2 go out of use here (Non-Lexical Lifetimes)

let r3 = &mut v;  // ✅ mutable borrow (r1/r2 no longer in use)
r3.push(4);
```

---

## Slices

Slices are **fat pointers** — a reference plus a length — that borrow part of a collection.

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];   // &str slice
let world: &str = &s[6..11];

let v = vec![1, 2, 3, 4, 5];
let middle: &[i32] = &v[1..4]; // [2, 3, 4]
```

String literals (`"hello"`) are already `&str` — slices of static program data.

---

## Lifetimes — Introduction

Lifetimes are the compile-time mechanism that ensures references don't outlive the data they point to. Most of the time they are **inferred** (lifetime elision).

```rust
// Elided (compiler infers)
fn first_word(s: &str) -> &str {
    &s[..s.find(' ').unwrap_or(s.len())]
}

// Explicit annotation — needed when compiler can't infer
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

> **`'a`** is a lifetime parameter: it says "the returned reference lives at least as long as both `x` and `y`."

Deep dive in [07 — Lifetimes](./07-lifetimes.md).

---

## Common Pitfalls

### Returning a reference to a local variable

```rust
fn bad() -> &String { // ❌ compile error
    let s = String::from("hello");
    &s // s is dropped at the end of this function!
}

fn good() -> String { // ✅ return owned value
    String::from("hello")
}
```

### Using a value after moving it into a closure

```rust
let s = String::from("hi");
let f = move || println!("{s}"); // s moved into closure
// println!("{s}"); // ❌ moved
f();
```

---

> **Previous**: [01 — Getting Started](./01-getting-started.md)  
> **Next**: [03 — Types & Control Flow](./03-types-and-control-flow.md)
