---
type: Programming Guide
title: "Rust — Getting Started"
description: "Installing the Rust toolchain, understanding Cargo, and setting up your first project."
tags: [rust, cargo, rustup, toolchain]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Getting Started

## Table of Contents
- [Installation](#installation)
- [Toolchain Components](#toolchain-components)
- [Cargo — The Build System & Package Manager](#cargo--the-build-system--package-manager)
- [Project Layout](#project-layout)
- [Hello, World!](#hello-world)
- [Useful Commands](#useful-commands)

---

## Installation

Rust is installed and managed through **`rustup`**, the official toolchain installer.

```bash
# Install rustup (Linux / macOS)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Verify installation
rustc --version
cargo --version
rustup --version
```

On Windows, download the installer from [rustup.rs](https://rustup.rs).

---

## Toolchain Components

| Tool | Purpose |
|------|---------|
| `rustc` | The Rust compiler |
| `cargo` | Build system + package manager |
| `rustup` | Toolchain manager (install/update/switch versions) |
| `rustfmt` | Automatic code formatter |
| `clippy` | Linter with idiomatic suggestions |
| `rust-analyzer` | Language server (IDE integration) |
| `cargo-doc` | Documentation generator |

### Managing Toolchain Versions

```bash
# Update to latest stable
rustup update stable

# Install nightly (needed for some experimental features)
rustup install nightly

# Override for a specific project
rustup override set nightly

# List installed toolchains
rustup toolchain list
```

---

## Cargo — The Build System & Package Manager

Cargo handles everything: compilation, dependency resolution, testing, documentation, and publishing.

```bash
# Create a new binary project
cargo new my-project

# Create a new library crate
cargo new my-lib --lib

# Build (debug mode)
cargo build

# Build (release — optimized)
cargo build --release

# Run the project
cargo run

# Run tests
cargo test

# Check for errors without producing a binary (fast)
cargo check

# Add a dependency
cargo add serde

# Generate and open documentation
cargo doc --open

# Format code
cargo fmt

# Lint
cargo clippy
```

### `Cargo.toml` — The Manifest

```toml
[package]
name    = "my-project"
version = "0.1.0"
edition = "2021"

[dependencies]
serde        = { version = "1", features = ["derive"] }
tokio        = { version = "1", features = ["full"] }
anyhow       = "1"

[dev-dependencies]
criterion = "0.5"

[profile.release]
opt-level = 3
lto       = true
```

> **Editions**: Rust editions (2015, 2018, 2021) are backwards-compatible language snapshots. Always start new projects with `edition = "2021"`.

---

## Project Layout

```
my-project/
├── Cargo.toml          # Manifest (dependencies, metadata)
├── Cargo.lock          # Pinned dependency versions (commit for binaries)
├── src/
│   ├── main.rs         # Binary entry point
│   └── lib.rs          # Library root (if also a lib crate)
├── tests/
│   └── integration.rs  # Integration tests
├── benches/
│   └── benchmark.rs    # Criterion benchmarks
└── examples/
    └── demo.rs         # Runnable examples (`cargo run --example demo`)
```

---

## Hello, World!

```rust
fn main() {
    println!("Hello, world!");

    // Variables are immutable by default
    let x = 5;
    let mut y = 10;  // `mut` makes it mutable
    y += x;
    println!("y = {y}");

    // Macros use `!` — println! is a macro, not a function
    eprintln!("This goes to stderr");
}
```

```bash
cargo run
# Hello, world!
# y = 15
```

---

## Useful Commands

```bash
# Search crates.io for packages
cargo search serde

# Show dependency tree
cargo tree

# Check for outdated dependencies
cargo install cargo-outdated && cargo outdated

# Security audit
cargo install cargo-audit && cargo audit

# Expand macros (requires nightly)
cargo install cargo-expand && cargo expand
```

---

> **Next**: [02 — Ownership & Borrowing](./02-ownership-borrowing.md)
