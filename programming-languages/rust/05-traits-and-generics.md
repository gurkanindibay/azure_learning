---
type: Programming Guide
title: "Rust — Traits & Generics"
description: "Defining shared behaviour with traits, writing generic functions and structs, trait objects, and derived traits."
tags: [rust, traits, generics, polymorphism, dyn, monomorphization]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Traits & Generics

## Table of Contents
- [Traits](#traits)
- [Default Implementations](#default-implementations)
- [Derived Traits](#derived-traits)
- [Trait Bounds](#trait-bounds)
- [Generics](#generics)
- [Static vs Dynamic Dispatch](#static-vs-dynamic-dispatch)
- [Common Standard Traits](#common-standard-traits)
- [Newtype Pattern](#newtype-pattern)

---

## Traits

A **trait** defines shared behaviour — similar to interfaces in C# but more powerful.

```rust
pub trait Summary {
    fn summarize(&self) -> String;
}

struct NewsArticle {
    title: String,
    content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}: {}...", self.title, &self.content[..50])
    }
}

struct Tweet {
    username: String,
    content: String,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("@{}: {}", self.username, self.content)
    }
}
```

### Traits as Parameters (`impl Trait`)

```rust
// Syntactic sugar for a trait bound
pub fn notify(item: &impl Summary) {
    println!("{}", item.summarize());
}
```

---

## Default Implementations

Traits can provide a default body that implementors can override:

```rust
pub trait Summary {
    fn author(&self) -> String;

    // Default implementation calls author()
    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.author())
    }
}

struct Tweet { username: String, content: String }

impl Summary for Tweet {
    fn author(&self) -> String { self.username.clone() }
    // summarize() is inherited — no need to implement it
}
```

---

## Derived Traits

The `#[derive]` macro auto-generates boilerplate implementations:

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}

let p1 = Point { x: 1, y: 2 };
let p2 = p1.clone();
println!("{p1:?}");
assert_eq!(p1, p2);
```

| Trait | Purpose | Derive? |
|-------|---------|---------|
| `Debug` | `{:?}` formatting | ✅ |
| `Display` | `{}` formatting | ❌ manual |
| `Clone` | `.clone()` | ✅ |
| `Copy` | implicit bitwise copy | ✅ (requires Clone) |
| `PartialEq` / `Eq` | `==` / `!=` | ✅ |
| `PartialOrd` / `Ord` | `<` / `>` / sorting | ✅ |
| `Hash` | use in `HashMap` keys | ✅ |
| `Default` | `T::default()` | ✅ |
| `Serialize` / `Deserialize` | JSON/binary via `serde` | ✅ (external crate) |

---

## Trait Bounds

Restrict generic parameters to types that implement certain traits:

```rust
// Verbose syntax
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}

// `where` clause (cleaner for multiple bounds)
fn compare_and_display<T>(t: T, u: T)
where
    T: std::fmt::Display + PartialOrd,
{
    if t > u { println!("{t} is larger") }
    else      { println!("{u} is larger") }
}
```

### Blanket Implementations

Implement a trait for all types satisfying a bound:

```rust
// From std: implement ToString for anything that implements Display
impl<T: fmt::Display> ToString for T {
    fn to_string(&self) -> String { format!("{}", self) }
}
```

---

## Generics

Generics allow code reuse over different types without runtime overhead.

```rust
struct Stack<T> {
    elements: Vec<T>,
}

impl<T> Stack<T> {
    pub fn new() -> Self {
        Stack { elements: Vec::new() }
    }

    pub fn push(&mut self, item: T) {
        self.elements.push(item);
    }

    pub fn pop(&mut self) -> Option<T> {
        self.elements.pop()
    }

    pub fn is_empty(&self) -> bool {
        self.elements.is_empty()
    }
}

let mut int_stack: Stack<i32> = Stack::new();
int_stack.push(1);
int_stack.push(2);

let mut str_stack: Stack<&str> = Stack::new();
str_stack.push("hello");
```

---

## Static vs Dynamic Dispatch

### Static Dispatch — Monomorphization (zero-cost)

The compiler generates a concrete version of the function for each type used:

```rust
fn notify_static(item: &impl Summary) {
    println!("{}", item.summarize());
}
// Compiles to notify_static_NewsArticle, notify_static_Tweet, ...
```

### Dynamic Dispatch — Trait Objects (`dyn Trait`)

Enables runtime polymorphism via vtable at the cost of an indirect call:

```rust
fn notify_dynamic(item: &dyn Summary) {
    println!("{}", item.summarize());
}

// Heterogeneous collection
let items: Vec<Box<dyn Summary>> = vec![
    Box::new(NewsArticle { title: "News".into(), content: "content here...".into() }),
    Box::new(Tweet { username: "user".into(), content: "tweet".into() }),
];

for item in &items {
    println!("{}", item.summarize());
}
```

| | Static (`impl Trait`) | Dynamic (`dyn Trait`) |
|---|---|---|
| Dispatch | Compile-time | Runtime (vtable) |
| Performance | Zero-cost | Slight overhead |
| Code size | Larger (monomorphized) | Smaller |
| Heterogeneous collection | ❌ | ✅ |
| Object safe required | ❌ | ✅ |

> **Object safety**: a trait is object-safe if its methods don't return `Self` and have no generic type parameters.

---

## Common Standard Traits

```rust
use std::fmt;

// Display — user-facing formatting
impl fmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}

// From / Into — type conversions
struct Wrapper(i32);
impl From<i32> for Wrapper {
    fn from(val: i32) -> Self { Wrapper(val) }
}
let w: Wrapper = 42.into(); // Into is auto-implemented when From exists

// Iterator
struct Counter { count: u32 }
impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        if self.count < 5 { self.count += 1; Some(self.count) }
        else { None }
    }
}
```

---

## Newtype Pattern

Wrapping a type to enforce different semantics or implement external traits:

```rust
struct Meters(f64);
struct Kilograms(f64);

impl fmt::Display for Meters {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} m", self.0)
    }
}

let d = Meters(1.5);
println!("{d}"); // 1.5 m
```

Benefits:
- **Type safety**: prevents mixing incompatible units
- **Orphan rule workaround**: implement external traits on wrapped external types

---

> **Previous**: [04 — Structs, Enums & Patterns](./04-structs-enums-patterns.md)  
> **Next**: [06 — Error Handling](./06-error-handling.md)
