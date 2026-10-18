---
type: Programming Guide
title: "Rust — Web & API Development"
description: "Building REST and gRPC APIs with Axum and Actix-Web, async database access with SQLx, and common web patterns."
tags: [rust, web, axum, actix-web, sqlx, rest, grpc, tonic, tower]
generated: { by: agent:antigravity, at: 2026-10-17T00:00:00Z }
---

# Rust — Web & API Development

## Table of Contents
- [Framework Comparison](#framework-comparison)
- [Axum — Getting Started](#axum--getting-started)
- [Routing & Handlers](#routing--handlers)
- [Extractors](#extractors)
- [State Management](#state-management)
- [Middleware with Tower](#middleware-with-tower)
- [Error Handling in Axum](#error-handling-in-axum)
- [Database Access with SQLx](#database-access-with-sqlx)
- [gRPC with Tonic](#grpc-with-tonic)
- [Full Example — REST CRUD API](#full-example--rest-crud-api)

---

## Framework Comparison

| | Axum | Actix-Web |
|--|------|-----------|
| Runtime | Tokio | Actix (actor-based, built on Tokio) |
| Extractors | Type-safe, composable | Macro-based |
| Middleware | Tower ecosystem | Actix middleware |
| Community | Growing fast (Tokio team) | Very mature |
| Performance | Excellent | Excellent |
| Learning curve | Moderate | Steeper |
| Recommendation | ✅ Default for new projects | ✅ If battle-tested is critical |

---

## Axum — Getting Started

```toml
[dependencies]
axum       = "0.7"
tokio      = { version = "1", features = ["full"] }
serde      = { version = "1", features = ["derive"] }
serde_json = "1"
tower      = "0.4"
tower-http = { version = "0.5", features = ["trace", "cors"] }
```

```rust
use axum::{Router, routing::get};

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(root_handler))
        .route("/health", get(health_handler));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Listening on http://0.0.0.0:3000");
    axum::serve(listener, app).await.unwrap();
}

async fn root_handler() -> &'static str {
    "Hello, World!"
}

async fn health_handler() -> axum::Json<serde_json::Value> {
    axum::Json(serde_json::json!({ "status": "ok" }))
}
```

---

## Routing & Handlers

```rust
use axum::{Router, routing::{get, post, put, delete}};

let app = Router::new()
    .route("/users",        get(list_users).post(create_user))
    .route("/users/:id",    get(get_user).put(update_user).delete(delete_user))
    .route("/users/:id/posts", get(list_user_posts));

// Path parameters
use axum::extract::Path;

async fn get_user(Path(id): Path<u64>) -> String {
    format!("User {id}")
}

// Multiple path params
async fn get_post(Path((user_id, post_id)): Path<(u64, u64)>) -> String {
    format!("User {user_id}, Post {post_id}")
}
```

---

## Extractors

Extractors deserialize parts of the HTTP request into Rust types:

```rust
use axum::extract::{Path, Query, Json};
use serde::Deserialize;

#[derive(Deserialize)]
struct Pagination {
    page: Option<u32>,
    per_page: Option<u32>,
}

#[derive(Deserialize)]
struct CreateUserRequest {
    name: String,
    email: String,
}

// Query string: GET /users?page=2&per_page=20
async fn list_users(Query(params): Query<Pagination>) -> String {
    let page = params.page.unwrap_or(1);
    let per_page = params.per_page.unwrap_or(20);
    format!("page={page}, per_page={per_page}")
}

// JSON body: POST /users
async fn create_user(Json(payload): Json<CreateUserRequest>) -> String {
    format!("Creating user: {} <{}>", payload.name, payload.email)
}
```

---

## State Management

Share database pools and other resources across handlers:

```rust
use axum::extract::State;
use std::sync::Arc;

#[derive(Clone)]
struct AppState {
    db: Arc<sqlx::PgPool>,
    config: Arc<Config>,
}

async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<u64>,
) -> Result<axum::Json<User>, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id as i64)
        .fetch_one(&*state.db)
        .await?;
    Ok(axum::Json(user))
}

let state = AppState {
    db: Arc::new(pool),
    config: Arc::new(config),
};

let app = Router::new()
    .route("/users/:id", get(get_user))
    .with_state(state);
```

---

## Middleware with Tower

Axum uses the **Tower** middleware ecosystem:

```rust
use tower_http::{trace::TraceLayer, cors::CorsLayer};
use tower::ServiceBuilder;

let app = Router::new()
    .route("/", get(root_handler))
    .layer(
        ServiceBuilder::new()
            .layer(TraceLayer::new_for_http())
            .layer(CorsLayer::permissive())
    );
```

### Custom Middleware

```rust
use axum::{middleware::{self, Next}, response::Response, extract::Request};

async fn auth_middleware(
    request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token = request
        .headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok());

    match token {
        Some(t) if validate_token(t) => Ok(next.run(request).await),
        _ => Err(StatusCode::UNAUTHORIZED),
    }
}

let protected = Router::new()
    .route("/admin", get(admin_handler))
    .layer(middleware::from_fn(auth_middleware));
```

---

## Error Handling in Axum

Implement `IntoResponse` for custom error types:

```rust
use axum::{response::{IntoResponse, Response}, http::StatusCode, Json};
use serde_json::json;

#[derive(Debug)]
enum AppError {
    NotFound,
    Unauthorized,
    Internal(anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            AppError::NotFound      => (StatusCode::NOT_FOUND, "Not found"),
            AppError::Unauthorized  => (StatusCode::UNAUTHORIZED, "Unauthorized"),
            AppError::Internal(e)   => {
                tracing::error!("Internal error: {e:?}");
                (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error")
            }
        };
        (status, Json(json!({ "error": message }))).into_response()
    }
}

// Enable ? from anyhow::Error in handlers
impl<E: Into<anyhow::Error>> From<E> for AppError {
    fn from(e: E) -> Self { AppError::Internal(e.into()) }
}
```

---

## Database Access with SQLx

SQLx provides **compile-time verified SQL** queries:

```toml
[dependencies]
sqlx = { version = "0.7", features = ["runtime-tokio", "postgres", "macros"] }
```

```bash
# Set DATABASE_URL for compile-time checking
export DATABASE_URL="postgres://user:pass@localhost/mydb"
cargo sqlx migrate add create_users
cargo sqlx migrate run
```

```rust
use sqlx::PgPool;

#[derive(sqlx::FromRow, serde::Serialize)]
struct User {
    id: i64,
    name: String,
    email: String,
}

async fn create_pool(url: &str) -> PgPool {
    PgPool::connect(url).await.expect("Failed to connect to database")
}

async fn create_user(pool: &PgPool, name: &str, email: &str) -> sqlx::Result<User> {
    // Compile-time SQL verification — typos caught at build time!
    sqlx::query_as!(
        User,
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
        name, email
    )
    .fetch_one(pool)
    .await
}

async fn find_user(pool: &PgPool, id: i64) -> sqlx::Result<Option<User>> {
    sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(pool)
        .await
}
```

### Migrations

```sql
-- migrations/20240101_create_users.sql
CREATE TABLE users (
    id    BIGSERIAL PRIMARY KEY,
    name  TEXT      NOT NULL,
    email TEXT      NOT NULL UNIQUE
);
```

```rust
// Run at startup
sqlx::migrate!("./migrations").run(&pool).await?;
```

---

## gRPC with Tonic

```toml
[dependencies]
tonic = "0.11"
prost = "0.12"

[build-dependencies]
tonic-build = "0.11"
```

```proto
// proto/greeter.proto
syntax = "proto3";
package greeter;

service Greeter {
    rpc SayHello (HelloRequest) returns (HelloReply);
}

message HelloRequest { string name = 1; }
message HelloReply   { string message = 1; }
```

```rust
// build.rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::compile_protos("proto/greeter.proto")?;
    Ok(())
}

// server
use tonic::{transport::Server, Request, Response, Status};

pub mod greeter { tonic::include_proto!("greeter"); }
use greeter::{greeter_server::{Greeter, GreeterServer}, HelloRequest, HelloReply};

#[derive(Default)]
pub struct MyGreeter {}

#[tonic::async_trait]
impl Greeter for MyGreeter {
    async fn say_hello(&self, request: Request<HelloRequest>) -> Result<Response<HelloReply>, Status> {
        let reply = HelloReply { message: format!("Hello {}!", request.into_inner().name) };
        Ok(Response::new(reply))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    Server::builder()
        .add_service(GreeterServer::new(MyGreeter::default()))
        .serve("[::1]:50051".parse()?)
        .await?;
    Ok(())
}
```

---

## Full Example — REST CRUD API

```rust
use axum::{Router, routing::{get, post}, extract::{Path, State, Json}, http::StatusCode};
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use std::sync::Arc;

#[derive(Serialize, sqlx::FromRow)]
struct Todo { id: i64, title: String, done: bool }

#[derive(Deserialize)]
struct CreateTodo { title: String }

type Db = Arc<PgPool>;

async fn list_todos(State(db): State<Db>) -> Json<Vec<Todo>> {
    let todos = sqlx::query_as!(Todo, "SELECT * FROM todos ORDER BY id")
        .fetch_all(&**db).await.unwrap();
    Json(todos)
}

async fn create_todo(State(db): State<Db>, Json(body): Json<CreateTodo>) -> (StatusCode, Json<Todo>) {
    let todo = sqlx::query_as!(Todo,
        "INSERT INTO todos (title, done) VALUES ($1, false) RETURNING *",
        body.title
    ).fetch_one(&**db).await.unwrap();
    (StatusCode::CREATED, Json(todo))
}

#[tokio::main]
async fn main() {
    let pool = Arc::new(PgPool::connect("postgres://localhost/todos").await.unwrap());
    let app = Router::new()
        .route("/todos", get(list_todos).post(create_todo))
        .with_state(pool);
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
```

---

> **Previous**: [13 — Testing & Benchmarking](./13-testing-benchmarking.md)  
> **Next**: [15 — CLI & Tooling](./15-cli-and-tooling.md)
