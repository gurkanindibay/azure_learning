---
type: Programming Guide
title: "Rust — Lifetimes Deep Dive"
description: "Explicit lifetime annotations, lifetime elision rules, 'static, struct lifetimes, and variance."
tags: [rust, lifetimes, borrow-checker, 'static, variance]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Lifetimes Deep Dive

## Table of Contents
- [What Are Lifetimes?](#what-are-lifetimes)
- [Lifetime Elision Rules](#lifetime-elision-rules)
- [Explicit Lifetime Annotations](#explicit-lifetime-annotations)
- [Lifetimes in Structs](#lifetimes-in-structs)
- [Lifetime Subtyping](#lifetime-subtyping)
- [`'static` Lifetime](#static-lifetime)
- [Higher-Ranked Trait Bounds (HRTB)](#higher-ranked-trait-bounds-hrtb)
- [Common Errors & Fixes](#common-errors--fixes)

---

## What Are Lifetimes?

A **lifetime** is a label the compiler uses to track how long a reference is valid. It does not affect runtime — lifetimes are erased before compilation finishes.

```text
              ┌── lifetime of s1 begins
let s1 = String::from("long string");
let result;
{
    let s2 = String::from("xyz"); ──┐
    result = longest(&s1, &s2); ◄──┘ s2's lifetime
} // s2 dropped — if result pointed to s2, use-after-free!
println!("{result}"); // compiler rejects if result could have been s2
```

The borrow checker guarantees `result` cannot outlive the data it refers to.

---

## Lifetime Elision Rules

The compiler infers lifetimes in most cases following three rules. Annotations are only required when the compiler cannot determine them:

| Rule | Description |
|------|-------------|
| **Rule 1** | Each reference parameter gets its own lifetime parameter |
| **Rule 2** | If there is exactly one input lifetime, it is assigned to all output lifetimes |
| **Rule 3** | If one of the input lifetimes is `&self` / `&mut self`, that lifetime is assigned to all output lifetimes |

```rust
// Elided — compiler applies rules automatically
fn first_word(s: &str) -> &str { &s[..] }

// Equivalent explicit form
fn first_word<'a>(s: &'a str) -> &'a str { &s[..] }
```

---

## Explicit Lifetime Annotations

Needed when the compiler cannot infer which input lifetime should flow to the output:

```rust
// Without annotation: compiler can't decide — does output live as long as x or y?
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

`'a` means: "the returned reference is valid for the **shorter** of x's and y's lifetimes."

```rust
fn main() {
    let string1 = String::from("long string");
    let result;
    {
        let string2 = String::from("xyz");
        result = longest(string1.as_str(), string2.as_str());
        println!("longest: {result}"); // ✅ result used inside string2's scope
    }
    // println!("{result}"); // ❌ string2 dropped; result could be dangling
}
```

### Multiple Lifetime Parameters

```rust
fn first_from_pair<'a, 'b>(pair: (&'a str, &'b str)) -> &'a str {
    pair.0 // returns only from the first, which lives 'a
}
```

---

## Lifetimes in Structs

Structs holding references must declare lifetime parameters:

```rust
struct Important<'a> {
    text: &'a str, // this struct cannot outlive the str it points to
}

impl<'a> Important<'a> {
    fn announce(&self, announcement: &str) -> &str {
        println!("Attention: {announcement}");
        self.text // Rule 3 applies — returns 'a (self's lifetime)
    }
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence;
    {
        let i = Important {
            text: novel.split('.').next().expect("Could not find '.'"),
        };
        first_sentence = i.announce("breaking news");
        println!("{first_sentence}");
    } // i dropped, but novel still alive — text still valid ✅
}
```

---

## Lifetime Subtyping

`'long: 'short` means `'long` **outlives** `'short`:

```rust
fn longer_ref<'short, 'long: 'short>(
    short_lived: &'short str,
    long_lived: &'long str,
) -> &'short str {
    // 'long: 'short means we can coerce &'long to &'short safely
    if long_lived.len() > short_lived.len() {
        long_lived  // coerced to &'short
    } else {
        short_lived
    }
}
```

---

## `'static` Lifetime

`'static` means the reference is valid for the **entire program duration**. String literals are the most common example:

```rust
let s: &'static str = "I am static"; // stored in the binary
```

### `'static` bounds on traits

Common in multithreading where types are sent across thread boundaries:

```rust
use std::thread;

fn spawn_thread<T: Send + 'static>(data: T) {
    thread::spawn(move || {
        println!("{:?}", data);
    });
}
```

`T: 'static` means T does not contain any non-static references — not that T must live forever (an owned `String` satisfies `'static`).

---

## Higher-Ranked Trait Bounds (HRTB)

Used when a closure or trait must work for **any** lifetime, not a specific one:

```rust
// fn(&str) -> &str must work for any possible lifetime of the input
fn apply<F>(f: F, s: &str) -> &str
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    f(s)
}

let result = apply(|s: &str| &s[..3], "hello");
println!("{result}"); // hel
```

`for<'a>` is pronounced "for any lifetime 'a".

---

## Common Errors & Fixes

### Error: "returns a value referencing data owned by the current function"

```rust
// ❌
fn bad() -> &str {
    let s = String::from("owned");
    &s // s dropped at end of function!
}

// ✅ — return owned value
fn good() -> String {
    String::from("owned")
}

// ✅ — return reference to a static
fn also_good() -> &'static str {
    "static string literal"
}
```

### Error: "lifetime may not live long enough"

```rust
struct Cache<'a> {
    data: &'a str,
}

// ❌ impl without matching lifetime
// impl Cache {
//     fn get(&self) -> &str { self.data }
// }

// ✅
impl<'a> Cache<'a> {
    fn get(&self) -> &'a str { self.data }
}
```

### Solving with Owned Types

When lifetime annotations become complex, consider using `String` instead of `&str`, or `Arc<T>` instead of `&T`:

```rust
// Instead of lifetime-annotated struct with &str:
struct Config<'a> { name: &'a str }

// Use owned type — simpler, more flexible:
struct Config { name: String }
```

---

> **Previous**: [06 — Error Handling](./06-error-handling.md)  
> **Next**: [08 — Smart Pointers & Interior Mutability](./08-smart-pointers.md)
