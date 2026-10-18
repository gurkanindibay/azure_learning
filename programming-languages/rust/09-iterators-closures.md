---
type: Programming Guide
title: "Rust — Iterators & Closures"
description: "The Iterator trait, lazy evaluation, chaining adaptors, closures and their Fn trait variants."
tags: [rust, iterators, closures, functional-programming, lazy-evaluation]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Iterators & Closures

## Table of Contents
- [Closures](#closures)
- [Closure Traits — `Fn`, `FnMut`, `FnOnce`](#closure-traits--fn-fnmut-fnonce)
- [Iterators](#iterators)
- [Creating Iterators](#creating-iterators)
- [Iterator Adaptors (Lazy)](#iterator-adaptors-lazy)
- [Consuming Adaptors (Eager)](#consuming-adaptors-eager)
- [Custom Iterators](#custom-iterators)
- [Performance — Zero-Cost Abstractions](#performance--zero-cost-abstractions)

---

## Closures

Closures are anonymous functions that **capture** variables from their surrounding scope.

```rust
let x = 5;

// Short closure — type inferred
let add = |n| n + x;
println!("{}", add(10)); // 15

// Explicit types
let square = |n: i32| -> i32 { n * n };

// Multi-line closure
let process = |data: Vec<i32>| {
    let sum: i32 = data.iter().sum();
    println!("sum = {sum}");
    sum
};
```

### Capture Modes

| Capture | How | When |
|---------|-----|------|
| By reference (`&T`) | Default if closure only reads | No ownership needed |
| By mutable reference (`&mut T`) | Default if closure mutates | No ownership needed |
| By value (move) | Explicit `move` keyword | Required when crossing thread boundaries |

```rust
let mut count = 0;
let mut increment = || { count += 1; }; // captures &mut count
increment();
increment();
println!("{count}"); // 2

// Move closure — takes ownership
let name = String::from("Alice");
let greet = move || println!("Hello, {name}!");
// name is moved into greet — can no longer use name here
greet();
```

---

## Closure Traits — `Fn`, `FnMut`, `FnOnce`

Every closure implements one or more of:

| Trait | Can call | Captures |
|-------|---------|---------|
| `FnOnce` | Once (consumes captures) | By value |
| `FnMut` | Multiple times (mutates captures) | By mutable reference |
| `Fn` | Multiple times (read-only) | By reference |

All closures implement `FnOnce`. Closures that don't consume captures also implement `FnMut`. Closures that don't mutate captures also implement `Fn`.

```rust
fn apply_once<F: FnOnce() -> String>(f: F) -> String { f() }
fn apply_mut<F: FnMut() -> i32>(mut f: F) -> i32 { f() + f() }
fn apply<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 { f(x) }

// Storing closures in structs
struct Cacher<T: Fn(i32) -> i32> {
    calculation: T,
    value: Option<i32>,
}

impl<T: Fn(i32) -> i32> Cacher<T> {
    fn new(calc: T) -> Self { Cacher { calculation: calc, value: None } }
    fn value(&mut self, arg: i32) -> i32 {
        match self.value {
            Some(v) => v,
            None => {
                let v = (self.calculation)(arg);
                self.value = Some(v);
                v
            }
        }
    }
}
```

---

## Iterators

The `Iterator` trait provides a lazy sequence of values:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // 80+ default methods (map, filter, fold, ...)
}
```

### Getting Iterators from Collections

```rust
let v = vec![1, 2, 3];

let iter  = v.iter();      // &T — borrows elements
let iter  = v.iter_mut(); // &mut T — mutable borrow
let iter  = v.into_iter(); // T — consumes the vector, takes ownership
```

---

## Iterator Adaptors (Lazy)

Adaptors transform iterators. They are **lazy** — no work happens until a consuming adaptor is called.

```rust
let v = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

let result: Vec<i32> = v.iter()
    .filter(|&&x| x % 2 == 0)   // keep evens
    .map(|&x| x * x)             // square
    .take(3)                     // first 3
    .collect();                  // ← consuming adaptor; drives the chain

println!("{result:?}"); // [4, 16, 36]
```

### Common Adaptors

| Adaptor | Description |
|---------|-------------|
| `.map(f)` | Transform each element |
| `.filter(pred)` | Keep elements where predicate is true |
| `.flat_map(f)` | Map then flatten one level |
| `.flatten()` | Flatten nested iterators |
| `.take(n)` | First n elements |
| `.skip(n)` | Skip n elements |
| `.enumerate()` | Add index: yields `(usize, T)` |
| `.zip(other)` | Pair elements from two iterators |
| `.chain(other)` | Append another iterator |
| `.peekable()` | Look ahead without consuming |
| `.cloned()` | Clone each `&T` to get `T` |
| `.copied()` | Copy each `&T` (T: Copy) |
| `.step_by(n)` | Take every nth element |
| `.windows(n)` | Overlapping slices of length n |
| `.chunks(n)` | Non-overlapping slices of length n |

---

## Consuming Adaptors (Eager)

These drive the iterator to completion:

```rust
let v = vec![1, 2, 3, 4, 5];

let sum: i32  = v.iter().sum();          // 15
let product   = v.iter().product::<i32>(); // 120
let count     = v.iter().count();         // 5
let max       = v.iter().max();           // Some(5)
let min       = v.iter().min();           // Some(1)

let has_even  = v.iter().any(|&x| x % 2 == 0);   // true
let all_pos   = v.iter().all(|&x| x > 0);         // true
let first_big = v.iter().find(|&&x| x > 3);       // Some(4)
let pos       = v.iter().position(|&x| x == 3);   // Some(2)

// collect into different types
let set: std::collections::HashSet<i32> = v.iter().copied().collect();
let s: String = ['a','b','c'].iter().collect();

// fold — general reduction
let factorial = (1..=5).fold(1_u64, |acc, x| acc * x); // 120

// for_each — side effects
v.iter().for_each(|x| print!("{x} "));
```

---

## Custom Iterators

```rust
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Fibonacci {
    fn new() -> Self { Fibonacci { a: 0, b: 1 } }
}

impl Iterator for Fibonacci {
    type Item = u64;

    fn next(&mut self) -> Option<u64> {
        let next = self.a + self.b;
        self.a = self.b;
        self.b = next;
        Some(self.a) // infinite iterator — never returns None
    }
}

let first_10: Vec<u64> = Fibonacci::new().take(10).collect();
println!("{first_10:?}"); // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

// All Iterator default methods are available for free!
let sum: u64 = Fibonacci::new().take(20).sum();
```

---

## Performance — Zero-Cost Abstractions

Iterator chains compile to the same assembly as hand-written loops. There is no virtual dispatch, no allocation, and no intermediate collection.

```rust
// These two are equivalent at the machine-code level:

// Iterator chain
let sum: i32 = (0..1_000_000).filter(|x| x % 2 == 0).map(|x| x * x).sum();

// Manual loop
let mut sum = 0i32;
for x in 0..1_000_000 {
    if x % 2 == 0 { sum += x * x; }
}
```

The compiler unrolls, inlines, and vectorizes iterator chains as aggressively as hand-written loops.

---

> **Previous**: [08 — Smart Pointers](./08-smart-pointers.md)  
> **Next**: [10 — Concurrency](./10-concurrency.md)
