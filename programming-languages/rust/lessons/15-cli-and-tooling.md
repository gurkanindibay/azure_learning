---
type: Programming Guide
title: "Rust — CLI & Tooling"
description: "Building command-line tools with Clap, serialization with Serde, configuration management, and release optimization."
tags: [rust, cli, clap, serde, configuration, release-builds]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — CLI & Tooling

## Table of Contents
- [Serde — Serialization & Deserialization](#serde--serialization--deserialization)
- [Clap — Command-Line Argument Parsing](#clap--command-line-argument-parsing)
- [Configuration Management](#configuration-management)
- [Logging & Tracing](#logging--tracing)
- [File & I/O Operations](#file--io-operations)
- [Release Optimization](#release-optimization)
- [Cross-compilation](#cross-compilation)

---

## Serde — Serialization & Deserialization

Serde is the de-facto standard for serialization in Rust. It works with JSON, TOML, YAML, MessagePack, Bincode, and many more formats.

```toml
[dependencies]
serde      = { version = "1", features = ["derive"] }
serde_json = "1"
toml       = "0.8"
```

```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
struct Config {
    name: String,
    port: u16,
    #[serde(default)]          // use Default::default() if missing
    workers: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    secret: Option<String>,
    #[serde(rename = "max-connections")]
    max_connections: u32,
}

// JSON
let config = Config {
    name: "my-service".to_string(),
    port: 8080,
    workers: 4,
    secret: None,
    max_connections: 100,
};

let json = serde_json::to_string_pretty(&config).unwrap();
println!("{json}");

let parsed: Config = serde_json::from_str(&json).unwrap();

// TOML
let toml_str = toml::to_string(&config).unwrap();
let from_toml: Config = toml::from_str(&toml_str).unwrap();
```

### Custom Serialization

```rust
use serde::{Serializer, Deserializer, de::Error as DeError};
use chrono::{DateTime, Utc};

fn serialize_dt<S: Serializer>(dt: &DateTime<Utc>, s: S) -> Result<S::Ok, S::Error> {
    s.serialize_str(&dt.to_rfc3339())
}

fn deserialize_dt<'de, D: Deserializer<'de>>(d: D) -> Result<DateTime<Utc>, D::Error> {
    let s = String::deserialize(d)?;
    DateTime::parse_from_rfc3339(&s).map(|dt| dt.with_timezone(&Utc)).map_err(DeError::custom)
}

#[derive(Serialize, Deserialize)]
struct Event {
    #[serde(serialize_with = "serialize_dt", deserialize_with = "deserialize_dt")]
    created_at: DateTime<Utc>,
}
```

---

## Clap — Command-Line Argument Parsing

```toml
[dependencies]
clap = { version = "4", features = ["derive"] }
```

```rust
use clap::{Parser, Subcommand, Args, ValueEnum};

#[derive(Parser, Debug)]
#[command(name = "mytool", version, about = "A sample CLI tool")]
struct Cli {
    /// Increase verbosity (-v, -vv, -vvv)
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Start the server
    Start(StartArgs),
    /// Generate configuration
    Init {
        /// Output path
        #[arg(short, long, default_value = "config.toml")]
        output: String,
    },
}

#[derive(Args, Debug)]
struct StartArgs {
    /// Listening port
    #[arg(short, long, default_value_t = 8080)]
    port: u16,

    /// Number of worker threads
    #[arg(short, long, default_value_t = num_cpus::get())]
    workers: usize,

    /// Log level
    #[arg(long, value_enum, default_value_t = LogLevel::Info)]
    log_level: LogLevel,
}

#[derive(ValueEnum, Clone, Debug)]
enum LogLevel { Debug, Info, Warn, Error }

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Start(args) => {
            println!("Starting on port {} with {} workers", args.port, args.workers);
        }
        Commands::Init { output } => {
            println!("Writing config to {output}");
        }
    }
}
```

```bash
mytool --help
mytool start --port 9090 --workers 8
mytool init --output ./myconfig.toml
mytool -vvv start
```

---

## Configuration Management

### `config` crate — Multi-source Configuration

```toml
[dependencies]
config = "0.14"
serde  = { version = "1", features = ["derive"] }
```

```rust
use config::{Config, Environment, File};
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct Settings {
    database_url: String,
    server: ServerSettings,
}

#[derive(Deserialize, Debug)]
struct ServerSettings {
    port: u16,
    host: String,
}

fn load_config() -> Result<Settings, config::ConfigError> {
    Config::builder()
        // Default config file
        .add_source(File::with_name("config/default"))
        // Environment-specific override
        .add_source(File::with_name(&format!("config/{}", std::env::var("APP_ENV").unwrap_or("development".into()))).required(false))
        // Environment variables override everything (APP_DATABASE_URL, APP_SERVER__PORT)
        .add_source(Environment::with_prefix("APP").separator("__"))
        .build()?
        .try_deserialize()
}
```

### `.env` Files

```toml
[dependencies]
dotenvy = "0.15"
```

```rust
fn main() {
    dotenvy::dotenv().ok(); // load .env file if present
    let db_url = std::env::var("DATABASE_URL").expect("DATABASE_URL must be set");
}
```

---

## Logging & Tracing

The `tracing` crate is the ecosystem standard (structured, async-aware):

```toml
[dependencies]
tracing            = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
```

```rust
use tracing::{info, warn, error, debug, instrument};

#[instrument(skip(password))] // creates a span for this function call
async fn login(username: &str, password: &str) -> Result<User, AuthError> {
    info!(user = username, "Login attempt");
    let user = db_find_user(username).await?;
    if !verify_password(password, &user.hash) {
        warn!(user = username, "Failed login");
        return Err(AuthError::InvalidPassword);
    }
    info!(user = username, "Login successful");
    Ok(user)
}

fn init_tracing() {
    tracing_subscriber::fmt()
        .with_env_filter("info,myapp=debug")  // RUST_LOG env var also works
        .with_target(true)
        .with_thread_ids(true)
        .init();
}
```

---

## File & I/O Operations

```rust
use std::fs;
use std::io::{self, BufRead, Write};

// Read entire file
let content = fs::read_to_string("data.txt")?;

// Write file
fs::write("output.txt", "hello world")?;

// Buffered line-by-line reading
let file = fs::File::open("data.csv")?;
let reader = io::BufReader::new(file);
for line in reader.lines() {
    let line = line?;
    println!("{line}");
}

// Buffered writing (efficient for many small writes)
let file = fs::File::create("out.txt")?;
let mut writer = io::BufWriter::new(file);
for i in 0..1000 {
    writeln!(writer, "line {i}")?;
}
writer.flush()?; // ensure all buffered data is written

// Path manipulation
use std::path::{Path, PathBuf};
let path = Path::new("/home/user/data");
let file = path.join("file.txt");
println!("{}", file.display()); // /home/user/data/file.txt
println!("{:?}", file.extension()); // Some("txt")
println!("{}", path.exists());
```

---

## Release Optimization

```toml
[profile.release]
opt-level     = 3        # maximum optimization (default)
lto           = "thin"   # Link-Time Optimization — further reduces binary & improves perf
codegen-units = 1        # single codegen unit — better optimization, slower compile
strip         = true     # strip debug symbols — smaller binary
panic         = "abort"  # smaller binary; no unwinding stack on panic

[profile.release-with-debug]
inherits = "release"
debug    = true          # useful for profiling (perf, flamegraph)
strip    = false
```

```bash
cargo build --release             # optimized binary
cargo build --profile release-with-debug  # profiling build

# Binary size inspection
cargo install cargo-bloat
cargo bloat --release --crates    # which crates contribute most to binary size

# Size optimized (e.g., for WebAssembly or embedded)
# opt-level = "s"  (optimize for size)
# opt-level = "z"  (aggressive size, slower runtime)
```

---

## Cross-compilation

```bash
# Add target
rustup target add x86_64-unknown-linux-musl
rustup target add aarch64-unknown-linux-gnu
rustup target add wasm32-unknown-unknown

# Build for target
cargo build --release --target x86_64-unknown-linux-musl  # static Linux binary
cargo build --release --target wasm32-unknown-unknown

# Cross (Docker-based cross-compilation tool)
cargo install cross
cross build --release --target aarch64-unknown-linux-gnu
```

### `.cargo/config.toml` for Default Targets

```toml
[build]
target = "x86_64-unknown-linux-musl"

[target.x86_64-unknown-linux-musl]
linker = "x86_64-linux-musl-gcc"
```

---

> **Previous**: [14 — Web Development](./14-web-development.md)  
> **Next**: [16 — Best Practices & Idioms](./16-best-practices.md)
