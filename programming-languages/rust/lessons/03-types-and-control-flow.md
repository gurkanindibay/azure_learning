---
type: Programming Guide
title: "Rust — Basic Types & Control Flow"
description: "Scalar types, compound types, variables, shadowing, and all control flow expressions in Rust."
tags: [rust, types, control-flow, pattern-matching, match]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Basic Types & Control Flow

## Table of Contents
- [Variables & Mutability](#variables--mutability)
- [Scalar Types](#scalar-types)
- [Compound Types](#compound-types)
- [Shadowing](#shadowing)
- [Functions](#functions)
- [Control Flow](#control-flow)
- [Pattern Matching with `match`](#pattern-matching-with-match)

---

## Variables & Mutability

```rust
let x = 5;          // immutable — cannot reassign
let mut y = 5;      // mutable
y = 10;             // ✅

const MAX: u32 = 100_000; // must have type annotation; computed at compile time
```

---

## Scalar Types

| Category | Types | Literals |
|----------|-------|---------|
| Signed integers | `i8`, `i16`, `i32`, `i64`, `i128`, `isize` | `42_i32`, `-100` |
| Unsigned integers | `u8`, `u16`, `u32`, `u64`, `u128`, `usize` | `255_u8` |
| Floating point | `f32`, `f64` (default) | `3.14_f64` |
| Boolean | `bool` | `true`, `false` |
| Character | `char` (4 bytes, Unicode scalar) | `'A'`, `'😀'` |

```rust
let n: i64 = 1_000_000; // underscores for readability
let b = 0b1111_0000;    // binary
let o = 0o77;           // octal
let h = 0xFF;           // hex
let f: f64 = 2.0;
let c: char = '中';
```

### Integer Overflow

- **Debug builds**: panic on overflow
- **Release builds**: wrap around (two's complement)
- Use `wrapping_add`, `checked_add`, `saturating_add` for explicit control

---

## Compound Types

### Tuple

Fixed-length, heterogeneous collection:

```rust
let tup: (i32, f64, char) = (42, 3.14, 'z');
let (x, y, z) = tup;       // destructuring
let first = tup.0;          // index access
```

### Array

Fixed-length, homogeneous, stored on the stack:

```rust
let arr: [i32; 5] = [1, 2, 3, 4, 5];
let zeroes = [0; 100]; // [0, 0, ..., 0] × 100
println!("{}", arr[0]);
println!("len = {}", arr.len());
```

> Use `Vec<T>` (heap-allocated) when length is dynamic.

### `str` and `String`

```rust
let s_literal: &str = "hello";        // string slice, lives in binary
let s_owned: String = String::from("hello"); // heap-allocated, growable
let s_from_lit: String = s_literal.to_string();
let back_to_slice: &str = &s_owned;
```

---

## Shadowing

Shadowing re-declares a variable in the same scope (different from `mut`):

```rust
let x = 5;
let x = x + 1;         // new x = 6
let x = x * 2;         // new x = 12

// Shadowing can change type — mut cannot
let spaces = "   ";
let spaces = spaces.len(); // spaces: usize = 3
```

---

## Functions

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b // last expression is the implicit return value (no semicolon!)
}

fn greet(name: &str) {
    println!("Hello, {name}!");
    // returns () implicitly
}

// Returning multiple values via tuple
fn min_max(v: &[i32]) -> (i32, i32) {
    (*v.iter().min().unwrap(), *v.iter().max().unwrap())
}
```

> **Expressions vs Statements**: `a + b` without `;` is an expression (has a value). Adding `;` makes it a statement (returns `()`).

---

## Control Flow

### `if` — An Expression

```rust
let number = 7;
if number % 2 == 0 {
    println!("even");
} else {
    println!("odd");
}

// if as an expression
let label = if number > 0 { "positive" } else { "non-positive" };
```

### Loops

```rust
// `loop` — infinite loop with break value
let result = loop {
    let x = expensive_computation();
    if x > 100 {
        break x * 2; // loop returns this value
    }
};

// `while`
let mut n = 3;
while n != 0 {
    print!("{n} ");
    n -= 1;
}

// `for` — preferred for collections
let arr = [10, 20, 30];
for element in arr {
    println!("{element}");
}

// Range
for i in 0..5 {         // 0, 1, 2, 3, 4
    print!("{i} ");
}
for i in (0..5).rev() { // 4, 3, 2, 1, 0
    print!("{i} ");
}
```

---

## Pattern Matching with `match`

`match` is exhaustive — the compiler forces you to handle every case.

```rust
let number = 3;
match number {
    1       => println!("one"),
    2 | 3   => println!("two or three"),
    4..=10  => println!("four through ten"),
    _       => println!("something else"), // wildcard — must handle remainder
}
```

### Matching on `Option<T>`

```rust
fn divide(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 { None } else { Some(a / b) }
}

match divide(10.0, 2.0) {
    Some(result) => println!("Result: {result}"),
    None         => println!("Division by zero"),
}
```

### `if let` — Concise Single-Pattern Match

```rust
let opt: Option<i32> = Some(42);
if let Some(val) = opt {
    println!("Got {val}");
}
```

### `while let`

```rust
let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() {
    println!("{top}");
}
```

---

> **Previous**: [02 — Ownership & Borrowing](./02-ownership-borrowing.md)  
> **Next**: [04 — Structs, Enums & Patterns](./04-structs-enums-patterns.md)
