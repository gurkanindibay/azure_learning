---
type: Programming Guide
title: "Rust — Best Practices & Idioms"
description: "Idiomatic Rust patterns, API design guidelines, common anti-patterns, clippy rules, and project conventions."
tags: [rust, best-practices, idioms, clippy, rustfmt, api-design]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Best Practices & Idioms

## Table of Contents
- [Code Style & Tooling](#code-style--tooling)
- [Naming Conventions](#naming-conventions)
- [API Design Guidelines](#api-design-guidelines)
- [Common Idioms](#common-idioms)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Performance Tips](#performance-tips)
- [Workspace & Project Organization](#workspace--project-organization)
- [Useful `clippy` Lints](#useful-clippy-lints)

---

## Code Style & Tooling

```bash
# Format code (enforced by CI)
cargo fmt

# Lint with clippy
cargo clippy
cargo clippy -- -D warnings   # treat warnings as errors (for CI)

# Deny specific warnings in code
#![deny(clippy::unwrap_used)]    # ban .unwrap() in production code
#![deny(clippy::panic)]          # ban panic! in library code
#![warn(missing_docs)]           # require pub API documentation

# Check for common security issues
cargo audit

# Check for unused dependencies
cargo install cargo-machete && cargo machete
```

### `.cargo/config.toml` — Project-wide settings

```toml
[build]
rustflags = ["-D", "warnings"]   # fail build on any warning
```

---

## Naming Conventions

| Element | Convention | Examples |
|---------|-----------|---------|
| Types, traits, enums | `UpperCamelCase` | `HttpClient`, `UserError`, `ReadConfig` |
| Functions, methods, variables | `snake_case` | `get_user`, `max_retries`, `is_valid` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT` |
| Modules, crates | `snake_case` | `my_module`, `serde_json` |
| Lifetime parameters | `'lowercase` | `'a`, `'static`, `'lifetime` |
| Type parameters | Single uppercase | `T`, `E`, `K`, `V` |
| Conversion methods | `into_`, `to_`, `as_` | `into_string()`, `to_lowercase()`, `as_bytes()` |

### Conversion Method Semantics

| Prefix | Ownership | Expensive | Example |
|--------|-----------|-----------|---------|
| `as_` | Borrow → borrow | No (reinterpret) | `as_str()`, `as_bytes()` |
| `to_` | Borrow → owned | Yes (allocates) | `to_string()`, `to_vec()` |
| `into_` | Consumes self | No/cheap | `into_string()`, `into_vec()` |

---

## API Design Guidelines

### Prefer `&str` Over `&String` in Fn Parameters

```rust
// ❌ Unnecessarily restrictive — forces callers to have a String
fn greet(name: &String) { println!("Hello, {name}"); }

// ✅ Accepts &str, &String, String (via deref coercion), Cow<str>
fn greet(name: &str) { println!("Hello, {name}"); }
```

### Prefer `impl Iterator` Return Types

```rust
// ✅ Zero-cost, no allocation
fn evens(v: &[i32]) -> impl Iterator<Item = &i32> {
    v.iter().filter(|&&x| x % 2 == 0)
}

// ❌ Allocates a Vec unnecessarily
fn evens_vec(v: &[i32]) -> Vec<&i32> {
    v.iter().filter(|&&x| x % 2 == 0).collect()
}
```

### Implement Standard Traits Where Appropriate

```rust
use std::fmt;
use std::hash::Hash;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(u64);

impl fmt::Display for UserId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "user-{}", self.0)
    }
}

impl From<u64> for UserId {
    fn from(id: u64) -> Self { UserId(id) }
}
```

### Builder Pattern for Complex Construction

```rust
#[derive(Default)]
pub struct ClientBuilder {
    base_url: Option<String>,
    timeout: Option<std::time::Duration>,
    retries: u32,
}

impl ClientBuilder {
    pub fn new() -> Self { Self::default() }
    pub fn base_url(mut self, url: impl Into<String>) -> Self {
        self.base_url = Some(url.into()); self
    }
    pub fn timeout(mut self, d: std::time::Duration) -> Self {
        self.timeout = Some(d); self
    }
    pub fn retries(mut self, n: u32) -> Self { self.retries = n; self }
    pub fn build(self) -> Result<Client, BuildError> {
        Ok(Client {
            base_url: self.base_url.ok_or(BuildError::MissingUrl)?,
            timeout: self.timeout.unwrap_or(std::time::Duration::from_secs(30)),
            retries: self.retries,
        })
    }
}

let client = ClientBuilder::new()
    .base_url("https://api.example.com")
    .timeout(std::time::Duration::from_secs(10))
    .retries(3)
    .build()?;
```

---

## Common Idioms

### Use `?` Everywhere Possible

```rust
// ❌ Verbose
fn read() -> Result<String, io::Error> {
    match std::fs::read_to_string("f.txt") {
        Ok(s)  => Ok(s),
        Err(e) => Err(e),
    }
}

// ✅ Idiomatic
fn read() -> Result<String, io::Error> {
    Ok(std::fs::read_to_string("f.txt")?)
}
```

### Prefer `if let` and `while let` over `match` for Single Patterns

```rust
let opt: Option<i32> = Some(42);

// ❌ Verbose
match opt {
    Some(v) => println!("{v}"),
    None => {}
}

// ✅ Idiomatic
if let Some(v) = opt { println!("{v}"); }
```

### Use `entry` API for HashMap

```rust
use std::collections::HashMap;

let mut map: HashMap<String, Vec<i32>> = HashMap::new();

// ❌ Multiple lookups
if !map.contains_key("key") { map.insert("key".to_string(), vec![]); }
map.get_mut("key").unwrap().push(1);

// ✅ entry API — single lookup, no clone needed
map.entry("key".to_string()).or_default().push(1);
map.entry("other".to_string()).or_insert_with(|| vec![0]).push(1);
```

### Use Iterators over Explicit Loops

```rust
let data = vec![1, 2, 3, 4, 5];

// ❌
let mut sum = 0;
for x in &data { sum += x; }

// ✅
let sum: i32 = data.iter().sum();
let doubled: Vec<i32> = data.iter().map(|&x| x * 2).collect();
```

---

## Anti-Patterns to Avoid

### `.unwrap()` / `.expect()` in Library Code

```rust
// ❌ Library code — panics propagate to caller unexpectedly
pub fn parse_id(s: &str) -> u64 { s.parse().unwrap() }

// ✅ Return Result so callers can handle errors
pub fn parse_id(s: &str) -> Result<u64, std::num::ParseIntError> { s.parse() }
```

### Unnecessary Cloning

```rust
fn print_name(name: &str) { println!("{name}"); }

let s = String::from("Alice");
// ❌
print_name(&s.clone()); // clone is not needed
// ✅
print_name(&s);
```

### Premature `Arc<Mutex<T>>`

Don't reach for `Arc<Mutex<T>>` when single ownership or `Rc<RefCell<T>>` suffices. Only use `Arc<Mutex<T>>` when data is genuinely shared across threads.

### Locking and Holding Guards Too Long

```rust
let guard = mutex.lock().unwrap();
let value = *guard;
drop(guard); // release the lock ASAP before expensive work

expensive_computation(value); // lock not held here
```

---

## Performance Tips

| Tip | Why |
|-----|-----|
| Use `&str` instead of `String` params | Avoids allocation |
| Use iterators instead of collecting | Avoids intermediate `Vec` |
| Pre-allocate with `Vec::with_capacity(n)` | Avoids repeated reallocations |
| Use `HashMap::with_capacity(n)` | Same |
| Prefer `String::push_str` over `+` | `+` moves and allocates; `push_str` doesn't |
| Profile before optimizing | `cargo flamegraph`, `perf`, `cargo bench` |
| Use `#[inline]` sparingly | Compiler usually knows best |
| Check `cargo clippy` suggestions | Many point to performance improvements |
| Use `Cow<str>` to avoid cloning | Clone only when mutation is needed |
| Avoid `Box<dyn Fn>` in hot paths | Use generics for static dispatch |

---

## Workspace & Project Organization

For larger projects, use a Cargo **workspace** to manage multiple crates:

```
my-workspace/
├── Cargo.toml          # workspace root
├── crates/
│   ├── core/           # shared types & business logic
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   ├── api/            # HTTP API binary
│   │   ├── Cargo.toml
│   │   └── src/main.rs
│   └── worker/         # background worker binary
│       ├── Cargo.toml
│       └── src/main.rs
```

```toml
# workspace Cargo.toml
[workspace]
members = ["crates/core", "crates/api", "crates/worker"]
resolver = "2"

[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

# Consistent dependency versions across all crates:
# In each crate's Cargo.toml:
# tokio.workspace = true
# serde.workspace = true
```

---

## Useful `clippy` Lints

Enable these in `lib.rs` / `main.rs`:

```rust
#![warn(
    clippy::all,
    clippy::pedantic,
    clippy::cargo,
    missing_docs,
)]

// For stricter codebases:
#![deny(
    clippy::unwrap_used,
    clippy::expect_used,
    clippy::panic,
)]
```

| Lint | What It Catches |
|------|----------------|
| `clippy::unwrap_used` | `.unwrap()` calls |
| `clippy::clone_on_ref_ptr` | Unnecessary `.clone()` on `Arc`/`Rc` |
| `clippy::inefficient_to_string` | Use `.to_owned()` instead |
| `clippy::large_enum_variant` | Enum variants with very different sizes |
| `clippy::redundant_clone` | Clone that's immediately consumed |
| `clippy::needless_pass_by_value` | Params that could be references |
| `clippy::missing_errors_doc` | Public fn returning Result needs docs |

---

> **Previous**: [15 — CLI & Tooling](./15-cli-and-tooling.md)  
> **Back to Index**: [index.md](../index.md)
