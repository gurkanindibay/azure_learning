---
type: Programming Guide
title: "Rust — Testing & Benchmarking"
description: "Unit tests, integration tests, doctests, property-based testing with proptest, and benchmarking with Criterion."
tags: [rust, testing, benchmarking, criterion, proptest, cargo-test]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Testing & Benchmarking

## Table of Contents
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Doc Tests](#doc-tests)
- [Test Attributes & Helpers](#test-attributes--helpers)
- [Testing Async Code](#testing-async-code)
- [Property-based Testing — `proptest`](#property-based-testing--proptest)
- [Benchmarking — Criterion](#benchmarking--criterion)
- [Code Coverage](#code-coverage)

---

## Unit Tests

Unit tests live in the same file, in a `#[cfg(test)]` module (excluded from release builds):

```rust
pub fn add(a: i32, b: i32) -> i32 { a + b }

pub fn divide(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 { None } else { Some(a / b) }
}

#[cfg(test)]
mod tests {
    use super::*; // bring module items into scope

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
        assert_eq!(add(-1, 1), 0);
    }

    #[test]
    fn test_divide_ok() {
        assert_eq!(divide(10.0, 2.0), Some(5.0));
    }

    #[test]
    fn test_divide_by_zero() {
        assert_eq!(divide(10.0, 0.0), None);
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_panics() {
        let _ = 1 / 0; // panics
    }
}
```

```bash
cargo test                  # run all tests
cargo test test_add         # run tests matching "test_add"
cargo test -- --nocapture   # show println! output
cargo test -- --test-threads=1  # run sequentially
```

---

## Integration Tests

Integration tests live in `tests/` and test the public API as an external consumer:

```
my-project/
├── src/
│   └── lib.rs
└── tests/
    ├── basic.rs
    └── edge_cases.rs
```

```rust
// tests/basic.rs
use my_project::add; // test the public API

#[test]
fn integration_test_add() {
    assert_eq!(add(1, 2), 3);
}
```

```bash
cargo test --test basic       # run only tests/basic.rs
cargo test --tests            # run all integration tests
```

---

## Doc Tests

Rust doc tests execute code examples in documentation comments, keeping docs accurate:

```rust
/// Adds two numbers together.
///
/// # Examples
///
/// ```
/// use my_project::add;
/// assert_eq!(add(2 + 2), 4);
/// ```
///
/// ```
/// // This example is expected to panic
/// # use my_project::add;
/// add(i32::MAX, 1); // overflows in debug
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

```bash
cargo test --doc   # run doc tests only
```

Lines prefixed with `#` are hidden in rendered docs but executed in tests.

---

## Test Attributes & Helpers

```rust
#[test]
#[ignore]                        // skip unless --ignored flag
fn expensive_test() { /* ... */ }

#[test]
#[should_panic]                  // test passes if it panics
fn must_panic() { panic!("boom") }

#[test]
#[should_panic(expected = "overflow")]
fn panics_with_message() { panic!("integer overflow") }
```

### Assertion Macros

```rust
assert!(condition);
assert!(condition, "message with {}", value);
assert_eq!(left, right);
assert_ne!(left, right);

// Floating point — use epsilon comparison
assert!((result - expected).abs() < 1e-9);

// Structured error output with pretty-printer
assert_eq!(complex_struct, expected_struct);
```

### Test Helpers & Fixtures

```rust
fn setup_db() -> Database {
    let db = Database::in_memory();
    db.seed_test_data();
    db
}

#[test]
fn test_query() {
    let db = setup_db();
    let result = db.query("SELECT 1");
    assert!(result.is_ok());
}
```

---

## Testing Async Code

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
tokio-test = "0.4"
```

```rust
#[cfg(test)]
mod tests {
    use super::*;

    // Option 1: tokio::test macro
    #[tokio::test]
    async fn test_async_function() {
        let result = async_fetch(1).await;
        assert!(result.is_ok());
    }

    // Option 2: block_on for sync test runners
    #[test]
    fn test_with_block_on() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let result = rt.block_on(async_fetch(1));
        assert!(result.is_ok());
    }

    // Mocking with tokio-test
    #[test]
    fn test_channel_behavior() {
        let mut mock = tokio_test::io::Builder::new()
            .read(b"hello")
            .write(b"world")
            .build();
        // use mock in place of a real TcpStream
    }
}
```

---

## Property-based Testing — `proptest`

Instead of writing specific inputs, define properties that must always hold and let proptest generate thousands of random test cases:

```toml
[dev-dependencies]
proptest = "1"
```

```rust
use proptest::prelude::*;

fn sort_and_dedup(mut v: Vec<i32>) -> Vec<i32> {
    v.sort();
    v.dedup();
    v
}

proptest! {
    #[test]
    fn result_is_sorted(v: Vec<i32>) {
        let result = sort_and_dedup(v);
        for w in result.windows(2) {
            prop_assert!(w[0] <= w[1], "not sorted: {:?}", w);
        }
    }

    #[test]
    fn no_duplicates_after_dedup(v: Vec<i32>) {
        let result = sort_and_dedup(v);
        let unique: std::collections::HashSet<_> = result.iter().collect();
        prop_assert_eq!(unique.len(), result.len());
    }

    // Custom strategy
    #[test]
    fn add_commutative(a in -1000i32..=1000, b in -1000i32..=1000) {
        prop_assert_eq!(add(a, b), add(b, a));
    }
}
```

---

## Benchmarking — Criterion

```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "my_benchmark"
harness = false
```

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn bench_fibonacci(c: &mut Criterion) {
    c.bench_function("fib 20", |b| {
        b.iter(|| fibonacci(black_box(20)))
    });
}

fn bench_fibonacci_group(c: &mut Criterion) {
    let mut group = c.benchmark_group("fibonacci");
    for i in [10u64, 15, 20, 25].iter() {
        group.bench_with_input(format!("fib {i}"), i, |b, i| {
            b.iter(|| fibonacci(black_box(*i)))
        });
    }
    group.finish();
}

criterion_group!(benches, bench_fibonacci, bench_fibonacci_group);
criterion_main!(benches);
```

```bash
cargo bench                          # run all benchmarks
cargo bench fib                      # run benchmarks matching "fib"
cargo bench -- --save-baseline main  # save baseline for comparison
cargo bench -- --baseline main       # compare against saved baseline
```

Criterion generates HTML reports in `target/criterion/`.

---

## Code Coverage

```bash
# Install tarpaulin (Linux only)
cargo install cargo-tarpaulin

# Generate coverage report
cargo tarpaulin --out html

# Or use llvm-cov (cross-platform, nightly)
rustup component add llvm-tools-preview
cargo install cargo-llvm-cov
cargo llvm-cov --html
```

---

> **Previous**: [12 — Unsafe Rust](./12-unsafe-rust.md)  
> **Next**: [14 — Web Development](./14-web-development.md)
