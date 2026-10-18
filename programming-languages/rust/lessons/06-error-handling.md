---
type: Programming Guide
title: "Rust — Error Handling"
description: "Idiomatic error handling with Result<T,E>, the ? operator, and popular crates like thiserror and anyhow."
tags: [rust, error-handling, result, thiserror, anyhow]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Error Handling

## Table of Contents
- [Philosophy](#philosophy)
- [Unrecoverable Errors — `panic!`](#unrecoverable-errors--panic)
- [Recoverable Errors — `Result<T, E>`](#recoverable-errors--resultte)
- [The `?` Operator](#the--operator)
- [Custom Error Types](#custom-error-types)
- [`thiserror` — Ergonomic Custom Errors](#thiserror--ergonomic-custom-errors)
- [`anyhow` — Application-Level Error Handling](#anyhow--application-level-error-handling)
- [When to Use What](#when-to-use-what)

---

## Philosophy

Rust separates errors into two categories:

| Category | Mechanism | When |
|----------|-----------|------|
| **Unrecoverable** | `panic!` | Bugs, broken invariants, programmer errors |
| **Recoverable** | `Result<T, E>` | Expected failure modes (IO, parsing, network) |

Unlike exceptions (C#, Java), errors in Rust are **values** — they appear in function signatures and must be explicitly handled by callers. This makes error paths visible and forces conscious decisions.

---

## Unrecoverable Errors — `panic!`

```rust
// Explicit panic
panic!("index out of bounds: {}", index);

// Panic macros
let v = vec![1, 2, 3];
v[99]; // panics at runtime in debug and release

// .unwrap() / .expect() — panic if None or Err
let value = some_option.expect("should have a value here");
```

Use `panic!` only when:
- An invariant is violated that cannot be recovered from
- In tests
- In examples/prototypes where error handling adds noise

Set `RUST_BACKTRACE=1` to print the backtrace on panic.

---

## Recoverable Errors — `Result<T, E>`

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = match File::open("username.txt") {
        Ok(file) => file,
        Err(e)   => return Err(e),
    };

    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_)  => Ok(s),
        Err(e) => Err(e),
    }
}
```

### Combinators

```rust
let content = std::fs::read_to_string("data.txt")
    .map(|s| s.trim().to_string())          // transform Ok value
    .map_err(|e| format!("IO error: {e}"))  // transform Err value
    .unwrap_or_default();                    // fallback

// and_then — chain fallible operations
let parsed: Result<i32, _> = "42"
    .parse::<i32>()
    .and_then(|n| if n > 0 { Ok(n) } else { Err("must be positive".parse::<i32>().unwrap_err()) });
```

---

## The `?` Operator

`?` is syntactic sugar that unwraps `Ok` or **early-returns** the `Err` (after applying `From` conversion):

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("username.txt")?; // early return on Err
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

// Even shorter using std helpers
fn read_username_from_file_v2() -> Result<String, io::Error> {
    std::fs::read_to_string("username.txt")
}
```

`?` also works in functions returning `Option<T>`:

```rust
fn first_even(numbers: &[i32]) -> Option<i32> {
    Some(*numbers.iter().find(|&&x| x % 2 == 0)?)
}
```

### `?` in `main`

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let content = std::fs::read_to_string("config.toml")?;
    println!("{content}");
    Ok(())
}
```

---

## Custom Error Types

Implementing the `std::error::Error` trait manually:

```rust
use std::fmt;

#[derive(Debug)]
pub enum AppError {
    NotFound(String),
    ParseError(String),
    IoError(std::io::Error),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::NotFound(name)   => write!(f, "Not found: {name}"),
            AppError::ParseError(msg)  => write!(f, "Parse error: {msg}"),
            AppError::IoError(e)       => write!(f, "IO error: {e}"),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::IoError(e) => Some(e),
            _ => None,
        }
    }
}

// Enable ? conversion from io::Error to AppError
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self { AppError::IoError(e) }
}

fn load_file(path: &str) -> Result<String, AppError> {
    let content = std::fs::read_to_string(path)?; // io::Error → AppError via From
    Ok(content)
}
```

---

## `thiserror` — Ergonomic Custom Errors

`thiserror` eliminates the boilerplate above. Best for **library** crates.

```toml
[dependencies]
thiserror = "1"
```

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("IO error")]
    IoError(#[from] std::io::Error),
}

fn load_file(path: &str) -> Result<String, AppError> {
    Ok(std::fs::read_to_string(path)?) // IoError variant via #[from]
}
```

---

## `anyhow` — Application-Level Error Handling

`anyhow` provides a single opaque error type. Best for **application** (binary) crates where you want to propagate any error without defining types.

```toml
[dependencies]
anyhow = "1"
```

```rust
use anyhow::{Context, Result, bail, ensure};

fn parse_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read config file: {path}"))?;

    let config: Config = serde_json::from_str(&content)
        .context("Invalid JSON in config")?;

    ensure!(config.port > 0, "port must be positive, got {}", config.port);

    Ok(config)
}

fn main() -> Result<()> {
    let config = parse_config("config.json")?;
    println!("Running on port {}", config.port);
    Ok(())
}
```

Key helpers:
- `.context("msg")` — attaches a message to any error
- `.with_context(|| ...)` — lazy (computed only on error)
- `bail!("msg")` — return an error immediately
- `ensure!(cond, "msg")` — assert or return error

---

## When to Use What

| Situation | Recommendation |
|-----------|---------------|
| Prototype / examples | `.unwrap()` / `.expect()` is fine |
| Library crate | `thiserror` with typed enum errors |
| Application (binary) | `anyhow` for ergonomic propagation |
| Unrecoverable invariant | `panic!` / `assert!` |
| Converting between error types | `impl From<E>` or `#[from]` |

---

> **Previous**: [05 — Traits & Generics](./05-traits-and-generics.md)  
> **Next**: [07 — Lifetimes Deep Dive](./07-lifetimes.md)
