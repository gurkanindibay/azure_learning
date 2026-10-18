# Rust Programming Language — Learning Plan

## Table of Contents

- [🎯 Overview](#overview)
- [🧪 Hands-on Practice Repository (`rust-practices`)](#hands-on-practice-repository-rust-practices)
- [📚 Learning Path](#learning-path)
  - [Phase 1: Foundations](#phase-1-foundations--weeks-13)
  - [Phase 2: Core Concepts](#phase-2-core-concepts--weeks-46)
  - [Phase 3: Systems Programming](#phase-3-systems-programming--weeks-79)
  - [Phase 4: Async & Concurrency](#phase-4-async--concurrency--weeks-1012)
  - [Phase 5: Ecosystem & Production](#phase-5-ecosystem--production--weeks-1316)
- [🚀 Quick Reference](#quick-reference)
- [📖 Additional Resources](#additional-resources)

---

## Overview

Rust is a systems programming language focused on three goals: **safety**, **speed**, and **concurrency**. Unlike C/C++, Rust guarantees memory safety without a garbage collector through its unique ownership model. It is increasingly relevant for:

- **Backend services** requiring high-throughput and low latency (competing with Go, Java)
- **Systems programming** (OS components, embedded, WebAssembly)
- **Cloud-native tooling** (many CNCF projects now written in Rust)
- **Azure SDK** contributions — Microsoft's Azure SDK for Rust is actively developed

This plan takes you from zero to production-ready Rust in ~16 weeks, with progressively deeper dives into the type system, memory model, async runtimes, and ecosystem.

---

## 🧪 Hands-on Practice Repository (`rust-practices`)

All practical exercises, runnable code examples, and test suites are maintained in the standalone repository **[`rust-practices`](https://github.com/gurkanindibay/rust-practices.git)**, integrated directly into this repository as a Git submodule at [`practices/`](./practices/).

### Quick Commands

```bash
# Run all practice tests across all 16 crates:
cargo test --manifest-path programming-languages/rust/practices/Cargo.toml

# Run Clippy checks across all crates:
cargo clippy --manifest-path programming-languages/rust/practices/Cargo.toml --all-targets

# Run a specific practice crate:
cargo run --manifest-path programming-languages/rust/practices/Cargo.toml -p c01_getting_started
cargo run --manifest-path programming-languages/rust/practices/Cargo.toml -p c06_error_handling
cargo run --manifest-path programming-languages/rust/practices/Cargo.toml -p c11_async_tokio
cargo run --manifest-path programming-languages/rust/practices/Cargo.toml -p c15_cli_and_tooling -- --help
cargo run --manifest-path programming-languages/rust/practices/Cargo.toml -p c16_best_practices
```

---

## Learning Path

### Phase 1: Foundations — Weeks 1–3

| # | Topic | Guide File | Practice Crate | Focus |
|---|-------|------------|----------------|-------|
| 01 | Installation & toolchain | [01-getting-started.md](./01-getting-started.md) | [`c01_getting_started`](./practices/crates/c01_getting_started) | `rustup`, `cargo`, project layout |
| 02 | Ownership & Borrowing | [02-ownership-borrowing.md](./02-ownership-borrowing.md) | [`c02_ownership_borrowing`](./practices/crates/c02_ownership_borrowing) | Move semantics, borrow checker, lifetimes intro |
| 03 | Basic Types & Control Flow | [03-types-and-control-flow.md](./03-types-and-control-flow.md) | [`c03_types_and_control_flow`](./practices/crates/c03_types_and_control_flow) | Scalars, tuples, arrays, `if let`, `match` |

### Phase 2: Core Concepts — Weeks 4–6

| # | Topic | Guide File | Practice Crate | Focus |
|---|-------|------------|----------------|-------|
| 04 | Structs, Enums & Pattern Matching | [04-structs-enums-patterns.md](./04-structs-enums-patterns.md) | [`c04_structs_enums_patterns`](./practices/crates/c04_structs_enums_patterns) | `impl` blocks, `Option`, `Result`, destructuring |
| 05 | Traits & Generics | [05-traits-and-generics.md](./05-traits-and-generics.md) | [`c05_traits_and_generics`](./practices/crates/c05_traits_and_generics) | Trait objects, `dyn`, monomorphization, bounds |
| 06 | Error Handling | [06-error-handling.md](./06-error-handling.md) | [`c06_error_handling`](./practices/crates/c06_error_handling) | `?` operator, `thiserror`, `anyhow`, custom errors |

### Phase 3: Systems Programming — Weeks 7–9

| # | Topic | Guide File | Practice Crate | Focus |
|---|-------|------------|----------------|-------|
| 07 | Lifetimes Deep Dive | [07-lifetimes.md](./07-lifetimes.md) | [`c07_lifetimes`](./practices/crates/c07_lifetimes) | Lifetime annotations, `'static`, variance |
| 08 | Smart Pointers & Interior Mutability | [08-smart-pointers.md](./08-smart-pointers.md) | [`c08_smart_pointers`](./practices/crates/c08_smart_pointers) | `Box`, `Rc`, `Arc`, `Cell`, `RefCell`, `Mutex` |
| 09 | Iterators & Closures | [09-iterators-closures.md](./09-iterators-closures.md) | [`c09_iterators_closures`](./practices/crates/c09_iterators_closures) | `Iterator` trait, lazy evaluation, `Fn`/`FnMut`/`FnOnce` |

### Phase 4: Async & Concurrency — Weeks 10–12

| # | Topic | Guide File | Practice Crate | Focus |
|---|-------|------------|----------------|-------|
| 10 | Concurrency Primitives | [10-concurrency.md](./10-concurrency.md) | [`c10_concurrency`](./practices/crates/c10_concurrency) | Threads, channels, `Mutex`, `RwLock`, `Arc` |
| 11 | Async/Await & Tokio | [11-async-tokio.md](./11-async-tokio.md) | [`c11_async_tokio`](./practices/crates/c11_async_tokio) | `Future`, executors, `tokio`, `async-std` |
| 12 | Unsafe Rust | [12-unsafe-rust.md](./12-unsafe-rust.md) | [`c12_unsafe_rust`](./practices/crates/c12_unsafe_rust) | Raw pointers, FFI, `unsafe` blocks, when to use |

### Phase 5: Ecosystem & Production — Weeks 13–16

| # | Topic | Guide File | Practice Crate | Focus |
|---|-------|------------|----------------|-------|
| 13 | Testing & Benchmarking | [13-testing-benchmarking.md](./13-testing-benchmarking.md) | [`c13_testing_benchmarking`](./practices/crates/c13_testing_benchmarking) | `#[test]`, `cargo test`, Criterion, property-based testing |
| 14 | Web & API Development | [14-web-development.md](./14-web-development.md) | [`c14_web_development`](./practices/crates/c14_web_development) | Axum, Actix-Web, SQLx, REST/gRPC patterns |
| 15 | CLI & Tooling | [15-cli-and-tooling.md](./15-cli-and-tooling.md) | [`c15_cli_and_tooling`](./practices/crates/c15_cli_and_tooling) | Clap, Serde, config management, release builds |
| 16 | Best Practices & Idioms | [16-best-practices.md](./16-best-practices.md) | [`c16_best_practices`](./practices/crates/c16_best_practices) | Idiomatic Rust, `clippy`, `rustfmt`, API design |


---

## Quick Reference

| Concept | Rust | C# Equivalent | Key Difference |
|---------|------|---------------|----------------|
| Memory management | Ownership + borrow checker | GC / `IDisposable` | No GC; deterministic drop |
| Nullability | `Option<T>` | `T?` (nullable) | Enforced at compile time |
| Error propagation | `Result<T, E>` + `?` | Exceptions | Errors are values; no stack unwinding by default |
| Async | `async`/`await` + runtime | `async`/`await` + CLR | Runtime (e.g. Tokio) must be chosen explicitly |
| Polymorphism (static) | Generics / monomorphization | Generics / JIT specialization | Zero-cost at runtime |
| Polymorphism (dynamic) | `dyn Trait` | `interface` | Explicit opt-in; slight overhead |
| Concurrency safety | Compile-time (`Send`/`Sync`) | Runtime locks | Data races caught at compile time |
| Build tool | `cargo` | `dotnet` CLI | Cargo also manages deps, testing, docs |

---

## Additional Resources

### Official

- [The Rust Book (rustbook)](https://doc.rust-lang.org/book/) — canonical learning resource
- [Rust By Example](https://doc.rust-lang.org/rust-by-example/) — code-first approach
- [Rustlings](https://github.com/rust-lang/rustlings) — interactive exercises
- [Rust Reference](https://doc.rust-lang.org/reference/) — language specification
- [std library docs](https://doc.rust-lang.org/std/) — standard library API reference

### Community & Advanced

- [Comprehensive Rust (Google)](https://google.github.io/comprehensive-rust/) — 4-day crash course
- [Rust Atomics and Locks (Mara Bos)](https://marabos.nl/atomics/) — concurrency deep dive
- [Zero to Production in Rust (Luca Palmieri)](https://www.zero2prod.com/) — production web services
- [Jon Gjengset — Crust of Rust (YouTube)](https://www.youtube.com/@jonhoo) — advanced concepts explained

### Azure & Cloud

- [Azure SDK for Rust](https://github.com/Azure/azure-sdk-for-rust) — official Azure client libraries
- [Rust on Azure Functions](https://docs.microsoft.com/azure/azure-functions/create-first-function-vs-code-other-languages) — serverless Rust
