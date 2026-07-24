---
type: Reference
title: "Concurrency Models & Language Runtimes"
description: "**GOMAXPROCS** — a Go runtime environment variable that sets the maximum number of OS threads that can execute Go code simultaneously."
timestamp: 2026-07-04T00:00:00Z
---

# Concurrency Models & Language Runtimes

> **Domain**: Concurrency primitives, language runtime schedulers, async I/O models, and parallelism fundamentals.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| GOMAXPROCS | [`#gomaxprocs`](#gomaxprocs) |
| Goroutine | [`#goroutine`](#goroutine) |
| M:N Scheduling | [`#mn-scheduling`](#mn-scheduling) |
| Tokio | [`#tokio`](#tokio) |
| Event Loop | [`#event-loop`](#event-loop) |
| Context Switching | [`#context-switching`](#context-switching) |
| Borrow Checker | [`#borrow-checker`](#borrow-checker) |
| Exhaustiveness Checking | [`#exhaustiveness-checking`](#exhaustiveness-checking) |
| Amdahl's Law | [`#amdahls-law`](#amdahls-law) |
| Actor Model | [`#actor-model`](#actor-model) |
| I/O-bound vs CPU-bound | [`#io-bound-vs-cpu-bound`](#io-bound-vs-cpu-bound) |
| Thread Pool Sizing Formula | [`#thread-pool-sizing-formula`](#thread-pool-sizing-formula) |
| Race Condition | [`#race-condition`](#race-condition) |
| Wildcard Match Arm | [`#wildcard-match-arm`](#wildcard-match-arm) |

---

## GOMAXPROCS

**GOMAXPROCS** — a Go runtime environment variable that sets the maximum number of OS threads that can execute Go code simultaneously. Controls the parallelism of the Go scheduler's work-stealing across goroutines.

### Key Characteristics
- Default: `runtime.NumCPU()` (all available CPUs)
- Set via `GOMAXPROCS=N` environment variable or `runtime.GOMAXPROCS(n)` in code
- Does NOT limit goroutine count (goroutines are multiplexed onto GOMAXPROCS OS threads)
- Critical for containerized environments where the container's CPU limit is less than the host's CPU count

### When to Use
- Explicit CPU affinity in benchmarks (matching Java's `ActiveProcessorCount`)
- Containerized Go services where `runtime.NumCPU()` sees the host CPUs, not container limits
- Performance tuning: reducing GOMAXPROCS can reduce GC pressure in CPU-saturated services

### When NOT to Use
- Default is usually correct for non-containerized deployments on dedicated hardware
- Setting GOMAXPROCS > actual available CPUs provides no benefit and may increase scheduling overhead

### Also see
- [Virtual Threads](java-jvm.md) — Java's concurrency model counterpart
- [Azure Container Apps](azure-services.md#container-apps) — containerized deployment target

---

## Goroutine

**Goroutine** — Go's fundamental unit of concurrency. A goroutine is a user-space, lightweight execution context managed entirely by the Go runtime scheduler. It starts with a ~2 KB stack (compared to ~512 KB–1 MB for OS threads) and grows dynamically. When a goroutine blocks on I/O, the Go scheduler parks it and runs another goroutine on the same OS thread — no kernel context switch required.

```go
func getOrder(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    order := db.FindOrder(id) // goroutine yields here, does not block OS thread
    json.NewEncoder(w).Encode(order)
}
// 10,000 of these running costs ~20 MB total stack
// Java platform threads equivalent: ~10 GB
```

### Key Characteristics
- Initial stack ~2 KB; grows in small increments as needed (unlike fixed OS thread stacks)
- Multiplexed onto OS threads via the Go runtime's M:N scheduler (see [M:N Scheduling](#mn-scheduling))
- Channels provide goroutine-safe communication and synchronization — no `synchronized` locks, no pinning risk
- Count is not limited by OS constraints: 50,000+ goroutines is routine in production
- Managed by `GOMAXPROCS` OS-thread pool (see [GOMAXPROCS](#gomaxprocs))

### When to Use
- Any concurrent I/O operation in Go — the idiomatic model is one goroutine per task
- High-concurrency HTTP handlers, background workers, pipeline stages

### When NOT to Use
- Not applicable outside Go (Java equivalent: [Virtual Threads](java-jvm.md); .NET equivalent: async/await tasks)
- Goroutines shared across FFI/CGo boundaries require extra care — CGo calls block the OS thread

### Also see
- [GOMAXPROCS](#gomaxprocs) — controls the OS-thread pool goroutines run on
- [M:N Scheduling](#mn-scheduling) — the scheduling model behind goroutines

---

## M:N Scheduling

**M:N Scheduling** (also: *many-to-many threading*) — a concurrency model where M user-space execution contexts (goroutines, virtual threads, fibers) are multiplexed onto N OS threads, where M >> N. The user-space scheduler decides which lightweight context runs on which OS thread, yielding cooperatively or preemptively when a context blocks.

```
M:N Model (e.g., Go goroutines)
================================
Goroutine-1  ╲
Goroutine-2   ╲
Goroutine-3    ──▶  OS Thread-1  (user-space scheduling; no syscall on yield)
Goroutine-4   ╱
Goroutine-5  ╱

vs.

1:1 Model (Java platform threads, pre-Loom)
============================================
Request-1  ──▶  OS Thread-1  (kernel scheduler; syscall on every context switch)
Request-2  ──▶  OS Thread-2
Request-3  ──▶  OS Thread-3
```

### Key Characteristics
- **Low memory footprint**: user-space contexts start at KBs vs OS thread stacks at hundreds of KBs
- **Cheap context switch**: switching between user-space contexts is a function call, not a kernel syscall
- **High multiplexing**: tens of thousands of logical tasks can share a handful of OS threads
- **Implementations**: Go goroutines (runtime scheduler), Java Virtual Threads (JVM carrier threads), Erlang processes, Kotlin coroutines

### When to Use
- I/O-bound, high-concurrency services where tasks spend most of their time waiting
- When per-task memory cost matters (microservices, serverless, embedded)

### When NOT to Use
- Pure CPU-bound workloads benefit more from N = CPU-count platform threads; extra scheduling overhead from M:N adds no value
- When the runtime does not support M:N natively (pre-Loom Java with platform threads is 1:1)

### Also see
- [Goroutine](#goroutine) — Go's implementation of M:N scheduling
- [GOMAXPROCS](#gomaxprocs) — controls N (OS thread count) in Go's M:N model

---

## Tokio

**Tokio** — Rust's asynchronous runtime, providing the event loop, task scheduler, I/O driver, and timer infrastructure needed to run async Rust code in production.

### Key Characteristics
- **Work-stealing scheduler**: tasks are distributed across a pool of OS threads; idle threads steal work from busy threads.
- **Async/await**: built on Rust `async`/`await` and `Future`; the runtime polls tasks to completion.
- **Zero-cost abstractions**: async code compiles to state machines without pervasive runtime allocation.
- **Ecosystem**: `tokio::sync` (channels, locks), `tokio::time`, `tokio::net`, and `tokio::task` cover most async service needs.

### When to Use
- High-concurrency network services in Rust where many connections are handled concurrently on a small thread pool.
- CPU- and latency-sensitive services that benefit from Rust's ownership model plus async I/O.

### When NOT to Use
- For blocking or CPU-bound work without spawning it on a dedicated thread pool (`spawn_blocking`), or it will stall the async runtime.
- As a default choice when the team has no Rust operational experience; the safety gains come with a learning curve.

### Also see
- [Goroutine](#goroutine) · [Event Loop](#event-loop) · [Global Interpreter Lock](data-concurrency.md#global-interpreter-lock)

---

## Event Loop

A concurrency pattern where a single thread continuously polls for and dispatches events or I/O operations, avoiding the need for locks by processing work sequentially. Redis's `ae.c` is a canonical example: ~300 lines of C that powers millions of production systems.

### Key Characteristics

- **Single-threaded by design**: Eliminates lock contention and race conditions entirely — complexity requires justification, not the other way around
- **Event-driven polling**: Continuously checks for network I/O, timers, and signals in a main loop (`aeProcessEvents`)
- **Non-blocking I/O**: Uses mechanisms like `epoll`/`kqueue`/`select` to handle many connections without thread-per-connection overhead

### When to Use

- CPU-light, I/O-heavy workloads where request processing is fast relative to I/O wait time
- Systems where data structure access benefits from lock-free semantics (e.g., in-memory data stores)
- When operational simplicity and debuggability outweigh raw throughput on multi-core machines

### When NOT to Use

- CPU-bound workloads that cannot saturate a single core fast enough for latency requirements
- When vertical scaling limits are hit and horizontal scaling across cores is the only option
- Systems with blocking operations that cannot be offloaded to background threads or async I/O

### Also see

- [Single-Threaded Architecture](dotnet-multithreading.md#single-threaded-architecture)
- [Async I/O patterns](dotnet-multithreading.md)

---

## Context Switching

Also called **time-slicing** — the operating system's mechanism for achieving concurrency on a single CPU core. The OS assigns small time slots (quanta) to each task, pauses the task, saves its state (registers, program counter), and switches to the next task. From the outside it looks like parallel work; under the hood it is extremely fast turn-taking.

### Key Characteristics
- **Single-core**: only one instruction executes at any given clock cycle.
- **Responsiveness, not throughput**: total wall-clock time is not reduced — tasks simply don't wait in line.
- **Overhead**: each switch costs CPU cycles to save/restore context; excessive switching causes thrashing.

### When to Use
- I/O-bound workloads where the CPU would otherwise sit idle during waits.
- Any modern OS scheduler — it is the default mechanism for multitasking.

### When NOT to Use
- As a replacement for true parallelism when CPU-bound work needs throughput, not just responsiveness.

### Also see
- [Concurrency](databases.md#concurrency) · [Parallelism](ai-ml-llm.md#parallelism) · [Event Loop](#event-loop)

---

## Borrow Checker

Rust's **borrow checker** is a compile-time analysis that enforces ownership, borrowing, and lifetime rules so invalid memory access and data races are rejected before execution.

### Key Characteristics
- Enforces aliasing and mutation constraints (`many readers` or `one writer`, not both simultaneously).
- Validates reference lifetimes to prevent dangling pointers and use-after-free.
- Runs at compile time and emits errors before binaries are produced.

### When to Use
- Building Rust services where memory safety and race safety need to be structural guarantees.
- Refactoring unsafe pointer-heavy code paths into ownership-safe abstractions.

### When NOT to Use
- As a substitute for business-logic review; it verifies memory/concurrency safety, not policy correctness.
- As a reason to skip domain-invariant tests on critical decision paths.

### Also see
- [Tokio](#tokio) · [Race Condition](#race-condition) · [Fail Fast](design-patterns.md#fail-fast)

---

## Exhaustiveness Checking

**Exhaustiveness checking** is a compiler guarantee that pattern matching over enums/sum types covers every variant, preventing unhandled-case omissions at compile time.

### Key Characteristics
- Fails compilation when one or more variants are not matched explicitly.
- Most effective when wildcard/catch-all branches are avoided in critical logic.
- Converts "future enum expansion" from a runtime surprise into a compile-time decision point.

### When to Use
- Authorization, pricing, workflow-state, and compliance rules modeled with enums.
- Evolving domains where new variants are expected over time.

### When NOT to Use
- As a blanket excuse to over-model simple two-state logic where explicit branching is already clear.
- With permissive wildcard branches in policy-critical paths, because that bypasses the protection.

### Also see
- [Wildcard Match Arm](#wildcard-match-arm) · [Borrow Checker](#borrow-checker) · [Least Privilege](security-iam.md#least-privilege)

---

## Amdahl's Law

A formula that defines the **maximum theoretical speedup** achievable by parallelizing a program, given that a fraction of it remains serial. If fraction $p$ can be parallelized and $N$ processors are available, the speedup $S$ is:

$$S = \frac{1}{(1-p) + \frac{p}{N}}$$

### Key Characteristics
- **Serial bottleneck**: the $(1-p)$ term dominates as $N \to \infty$.
- **Hard ceiling**: if 50% of code is sequential, max speedup is **2×** — even with infinite cores.
- **Profiling prerequisite**: you must measure the serial fraction before investing in parallelization.

### When to Use
- As a sanity check before any parallelization effort.
- Capacity planning: estimate how many cores are worth paying for.

### When NOT to Use
- When the workload is I/O-bound — Amdahl's Law models CPU parallelism, not I/O concurrency.

### Also see
- [I/O-bound vs CPU-bound](#io-bound-vs-cpu-bound) · [Parallelism](ai-ml-llm.md#parallelism) · [Concurrency](databases.md#concurrency)

---

## Actor Model

A concurrency model where **actors** are the universal primitives. Each actor has its own private state, processes messages sequentially from its mailbox, and communicates only via asynchronous message passing — never through shared memory. This eliminates shared-state concurrency bugs by design.

### Key Characteristics
- **No shared state**: each actor's state is private; messages are the only communication channel.
- **Isolation**: actors can fail independently without corrupting other actors.
- **Examples**: Erlang/Elixir processes, Akka (JVM), Ruby Ractors, Orleans (.NET).

### When to Use
- Systems requiring high fault tolerance and isolation (telecom, financial middleware).
- Workloads with naturally independent units of work that communicate via messages.

### When NOT to Use
- Simple single-threaded applications where actor overhead adds complexity without benefit.
- CPU-bound workflows that need shared-memory parallelism for maximum throughput.

### Also see
- [Concurrency](databases.md#concurrency) · [Race Condition](#race-condition)

---

## I/O-bound vs CPU-bound

A fundamental classification of workloads that determines which concurrency model to apply:

| Type | Bottleneck | Best Approach |
|:---|:---|:---|
| **I/O-bound** | Waiting for disk, network, or database | Concurrency (async I/O, event loop) |
| **CPU-bound** | Processor throughput | Parallelism (multiple cores, worker pools) |

### Key Characteristics
- **I/O-bound**: CPU sits idle during waits — measured by response time, not CPU utilization.
- **CPU-bound**: CPU is the limiting resource — measured by throughput, not latency.
- **Most web apps are I/O-bound**: database, cache, and external APIs account for 80–95% of response time.

### When to Use
- As the first diagnostic step in any performance investigation: profile to determine which bottleneck you have before choosing a concurrency model.

### When NOT to Use
- As a rigid rule — many real workloads are mixed. Profile, don't assume.

### Also see
- [Amdahl's Law](#amdahls-law) · [Concurrency](databases.md#concurrency) · [Parallelism](ai-ml-llm.md#parallelism)

---

## Race Condition

A bug where the correctness of a program depends on the **relative timing or interleaving** of concurrent operations. When two threads or processes access shared mutable state without proper synchronization, the result is non-deterministic and depends on which operation "wins the race."

### Key Characteristics
- **Non-deterministic**: the same input can produce different outputs on different runs.
- **Hard to reproduce**: timing-dependent bugs may pass unit tests and only appear under load.
- **Caused by shared mutable state**: single-threaded event loops and actor models avoid this by design.

### When to Use
- The term is diagnostic, not prescriptive. Recognize race conditions as a signal to add synchronization (mutex, atomic operation) or to redesign to avoid shared state.

### When NOT to Use
- Do not accept race conditions as "rare" — they tend to manifest at the worst possible time (production peak load).

### Also see
- [Lock Contention](data-concurrency.md#lock-contention) · [Actor Model](#actor-model) · [Mutex](dotnet-multithreading.md#mutex)

---

## Wildcard Match Arm

A **wildcard match arm** (for example `_ => ...`) is a catch-all branch in pattern matching that handles all currently unmatched and future variants with one default behavior.

### Key Characteristics
- Reduces immediate code verbosity but hides domain intent for newly added variants.
- Keeps compilation green when enum variants evolve, which can mask logic drift.
- Useful for non-critical fallback behavior, risky for policy or entitlement logic.

### When to Use
- Non-critical display formatting or telemetry classification where generic fallback is acceptable.
- Temporary compatibility shims with explicit follow-up cleanup.

### When NOT to Use
- Authorization, billing, risk, compliance, or routing decisions where each variant needs intentional handling.
- Long-lived code paths where silent defaulting can become latent production defects.

### Also see
- [Exhaustiveness Checking](#exhaustiveness-checking) · [Defensive Programming](resilience.md#defensive-programming) · [Architecture Decision Record](design-patterns.md#architecture-decision-record)

---

## Thread Pool Sizing Formula

### thread-pool-sizing-formula

A heuristic for estimating the initial thread count for a thread pool based on the workload classification (I/O-bound vs CPU-bound) and the ratio of wait time to compute time.

```text
Threads = CPU Cores × Target CPU Utilization × (1 + Wait Time / Compute Time)
```

### Key Characteristics
- **I/O-bound workloads**: the wait/compute ratio is high (e.g., 8:1 for network calls), so more threads than CPU cores make sense — threads spend most of their time blocked on I/O, not competing for CPU
- **CPU-bound workloads**: the wait/compute ratio approaches 0, so threads ≈ CPU cores × utilization target
- **Starting point only**: the formula provides a reasoned baseline; production values must come from load testing under realistic conditions
- **Target utilization < 100%**: always leave headroom for GC, OS tasks, and workload spikes

### Example

| Parameter | Value |
|:---|:---|
| CPU cores | 16 |
| Target utilization | 80% (0.8) |
| Wait/Compute ratio | 8:1 |
| **Result** | 16 × 0.8 × (1 + 8) ≈ **115 threads** |

### When to Use
- Initial capacity planning for thread pools before load testing
- System design interviews and architecture discussions to justify thread count decisions
- Comparing language runtimes (the formula is language-agnostic)

### When NOT to Use
- As a replacement for load testing — real systems have variable wait times, gateway throttling, and GC pauses the formula cannot capture
- With virtual threads / goroutines (M:N scheduling) — the formula models OS-thread-level parallelism, not user-space task multiplexing
- For dynamic workloads where thread counts should be runtime-adjustable

### Also see
- [I/O-bound vs CPU-bound](#io-bound-vs-cpu-bound) · [Amdahl's Law](#amdahls-law) · [Virtual Threads](java-jvm.md#virtual-threads) · [Backpressure](resilience.md#backpressure)
