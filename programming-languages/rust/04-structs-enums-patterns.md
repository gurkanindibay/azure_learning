---
type: Programming Guide
title: "Rust — Structs, Enums & Pattern Matching"
description: "Defining custom data types with structs and enums, implementing methods, and leveraging exhaustive pattern matching."
tags: [rust, structs, enums, pattern-matching, option, result]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Structs, Enums & Pattern Matching

## Table of Contents
- [Structs](#structs)
- [Methods with `impl`](#methods-with-impl)
- [Enums](#enums)
- [`Option<T>`](#optiont)
- [`Result<T, E>`](#resultte)
- [Advanced Pattern Matching](#advanced-pattern-matching)
- [Destructuring](#destructuring)

---

## Structs

### Named-field Struct

```rust
struct Rectangle {
    width: f64,
    height: f64,
}

let rect = Rectangle { width: 30.0, height: 50.0 };
println!("width = {}", rect.width);
```

### Struct Update Syntax

```rust
let rect2 = Rectangle {
    width: 10.0,
    ..rect // copy remaining fields from rect
};
```

### Tuple Structs

Useful for newtype patterns (wrapper types):

```rust
struct Meters(f64);
struct Kilograms(f64);

let distance = Meters(5.0);
let weight = Kilograms(70.0);
// distance = weight; // ❌ type-safe — different types!
```

### Unit-like Structs

Structs with no fields, useful for implementing traits:

```rust
struct AlwaysEqual;
```

### Debug Printing

```rust
#[derive(Debug)]
struct Point { x: i32, y: i32 }

let p = Point { x: 10, y: 20 };
println!("{p:?}");   // Point { x: 10, y: 20 }
println!("{p:#?}");  // pretty-printed
```

---

## Methods with `impl`

```rust
struct Rectangle { width: f64, height: f64 }

impl Rectangle {
    // Associated function (constructor) — called with Rectangle::new(...)
    pub fn new(width: f64, height: f64) -> Self {
        Self { width, height }
    }

    // Method — takes &self (immutable borrow)
    pub fn area(&self) -> f64 {
        self.width * self.height
    }

    // Mutable method — takes &mut self
    pub fn scale(&mut self, factor: f64) {
        self.width  *= factor;
        self.height *= factor;
    }

    // Consuming method — takes self (moves out of caller)
    pub fn into_square(self) -> Rectangle {
        let side = f64::sqrt(self.area());
        Rectangle { width: side, height: side }
    }
}

let mut r = Rectangle::new(3.0, 4.0);
println!("area = {}", r.area());
r.scale(2.0);
```

> **Note on `new`**: Unlike C++, Java, or C#, Rust does not have a `new` keyword or a built-in constructor mechanism. `Type::new(...)` is purely an idiomatic community naming convention for an associated function returning `Self`. For details on destruction and cleanup, see [02 — Ownership & Borrowing](./02-ownership-borrowing.md#the-drop-trait-vs-the-new-convention).

---

## Enums

Rust enums are **algebraic data types** — each variant can carry different data.

```rust
#[derive(Debug)]
enum Shape {
    Circle(f64),           // radius
    Rectangle(f64, f64),   // width, height
    Triangle { base: f64, height: f64 }, // named fields
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r)               => std::f64::consts::PI * r * r,
            Shape::Rectangle(w, h)         => w * h,
            Shape::Triangle { base, height } => 0.5 * base * height,
        }
    }
}

let shapes = vec![
    Shape::Circle(5.0),
    Shape::Rectangle(4.0, 6.0),
    Shape::Triangle { base: 3.0, height: 8.0 },
];

for s in &shapes {
    println!("{s:?} → area = {:.2}", s.area());
}
```

---

## `Option<T>`

`Option<T>` replaces null. Defined in std:

```rust
enum Option<T> {
    Some(T),
    None,
}
```

### Common Methods

```rust
let some_value: Option<i32> = Some(42);
let no_value: Option<i32>   = None;

// Unwrap (panics if None — avoid in production)
let v = some_value.unwrap();

// Safe alternatives
let v = some_value.unwrap_or(0);          // default value
let v = some_value.unwrap_or_default();   // T::default()
let v = some_value.unwrap_or_else(|| expensive_default()); // lazy

// Map & chain
let doubled = some_value.map(|x| x * 2);    // Some(84)
let squared = some_value
    .filter(|&x| x > 0)
    .map(|x| x * x);                         // Some(1764)

// Convert to Result
let result: Result<i32, &str> = some_value.ok_or("no value");

// if let (idiomatic)
if let Some(val) = some_value {
    println!("Got {val}");
}
```

---

## `Result<T, E>`

`Result<T, E>` models fallible operations:

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

```rust
use std::num::ParseIntError;

fn parse_positive(s: &str) -> Result<u32, String> {
    s.parse::<i32>()
        .map_err(|e: ParseIntError| e.to_string())
        .and_then(|n| {
            if n >= 0 { Ok(n as u32) }
            else      { Err("negative number".to_string()) }
        })
}

match parse_positive("42") {
    Ok(n)    => println!("Parsed: {n}"),
    Err(msg) => eprintln!("Error: {msg}"),
}
```

The `?` operator (covered in [06 — Error Handling](./06-error-handling.md)) makes propagating errors ergonomic.

---

## Advanced Pattern Matching

### Guards

```rust
let num = 7;
match num {
    n if n < 0  => println!("negative: {n}"),
    0           => println!("zero"),
    n if n % 2 == 0 => println!("positive even: {n}"),
    n           => println!("positive odd: {n}"),
}
```

### Binding with `@`

```rust
match num {
    n @ 1..=10 => println!("small: {n}"),
    n @ 11..=100 => println!("medium: {n}"),
    _ => println!("large"),
}
```

### Nested Enum Matching

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

fn process(msg: Message) {
    match msg {
        Message::Quit => println!("quit"),
        Message::Move { x, y } => println!("move to ({x},{y})"),
        Message::Write(text) => println!("write: {text}"),
        Message::ChangeColor(r, g, b) => println!("color ({r},{g},{b})"),
    }
}
```

---

## Destructuring

```rust
// Tuple
let (a, b, c) = (1, 2.0, "three");

// Struct
struct Point { x: i32, y: i32 }
let p = Point { x: 0, y: 7 };
let Point { x, y } = p;

// Nested
let ((feet, inches), Point { x, y }) = ((3, 10), Point { x: 3, y: -10 });

// Ignore fields with `..`
struct Verbose { a: i32, b: i32, c: i32 }
let v = Verbose { a: 1, b: 2, c: 3 };
let Verbose { a, .. } = v; // ignore b and c
```

---

> **Previous**: [03 — Types & Control Flow](./03-types-and-control-flow.md)  
> **Next**: [05 — Traits & Generics](./05-traits-and-generics.md)
