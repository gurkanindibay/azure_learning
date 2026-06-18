---
type: Reference
title: "Databases & Database Engines"
description: "Database engine internals, configuration parameters, and storage-layer concepts."
timestamp: 2026-06-18T00:00:00Z
---

# Databases & Database Engines

> **Domain**: Database engine internals, storage subsystem behavior, and configuration parameters that affect query execution.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| effective_io_concurrency | [`#effective-io-concurrency`](#effective-io-concurrency) |
| io_method | [`#io-method`](#io-method) |
| io_uring | [`#io-uring`](#io-uring) |
| pg_aios | [`#pg-aios`](#pg-aios) |
| shared_buffers | [`#shared-buffers`](#shared-buffers) |

---

## effective_io_concurrency {#effective-io-concurrency}

A PostgreSQL configuration parameter that tells the query planner how many disk I/O operations the storage layer can execute concurrently. In PostgreSQL 18 the default changed from `1` to `16`, reflecting the assumption that asynchronous I/O can overlap multiple reads.

### Key Characteristics
- Higher values let the planner choose plans that issue more parallel reads
- The optimal value depends on storage latency and throughput, not CPU count
- Only affects planning for read operations that benefit from overlapping I/O

### When to Use
- High-latency cloud volumes where queuing many reads hides round-trip time
- Analytical workloads with cold, scan-heavy queries

### When NOT to Use
- Single local NVMe devices that already saturate bandwidth with few concurrent reads
- Cached or index-bound transactional workloads where disk latency is not the bottleneck

**Also see**: [io_method](#io-method), [io_uring](#io-uring), [shared_buffers](#shared-buffers)

---

## io_method {#io-method}

A PostgreSQL 18 configuration parameter that selects the asynchronous I/O implementation used by the database backend. Changing it requires a server restart.

### Key Characteristics
- `worker` (default): dedicated background I/O processes; portable across operating systems
- `io_uring`: uses the Linux kernel's `io_uring` interface; typically fastest on recent Linux kernels
- `sync`: pre-18 synchronous behavior; escape hatch for regression testing or compatibility

### When to Use
- `worker` as the safe default everywhere
- `io_uring` on recent Linux when benchmarking confirms lower latency
- `sync` only when reproducing pre-18 behavior or investigating a regression

### When NOT to Use
- Do not switch to `io_uring` without a direct A/B benchmark on your workload
- Do not assume the default is wrong; measure first

**Also see**: [io_uring](#io-uring), [effective_io_concurrency](#effective-io-concurrency), [pg_aios](#pg-aios)

---

## io_uring {#io-uring}

A Linux kernel asynchronous I/O interface that lets user-space applications submit many I/O requests and collect completions through shared ring buffers, avoiding per-syscall overhead and enabling efficient overlap of disk latency.

### Key Characteristics
- Submission and completion queues are shared between user space and kernel space
- Supports read, write, and other operations beyond legacy `aio`
- Requires a recent Linux kernel and appropriate permissions

### When to Use
- High-throughput, latency-sensitive storage workloads on Linux
- PostgreSQL 18 deployments where benchmarking shows `io_method = 'io_uring'` outperforms `worker`

### When NOT to Use
- Non-Linux operating systems (use `worker` instead)
- Kernels without stable `io_uring` support
- Workloads where the bottleneck is not disk I/O latency

**Also see**: [io_method](#io-method), [effective_io_concurrency](#effective-io-concurrency)

---

## pg_aios {#pg-aios}

A system view introduced in PostgreSQL 18 that exposes runtime statistics about asynchronous I/O operations.

### Key Characteristics
- Shows in-flight and completed async I/O requests
- Useful for validating that async I/O is active during heavy queries
- Complements `EXPLAIN (ANALYZE, BUFFERS)` for I/O troubleshooting

### When to Use
- Verify async I/O behavior after changing `io_method` or `effective_io_concurrency`
- Correlate query latency with actual async I/O activity

### When NOT to Use
- Not a substitute for `EXPLAIN ANALYZE` for query-plan tuning
- Not meaningful for workloads using `io_method = 'sync'`

**Also see**: [io_method](#io-method), [effective_io_concurrency](#effective-io-concurrency)

---

## shared_buffers {#shared-buffers}

The region of memory PostgreSQL uses to cache table and index blocks. Data already present in `shared_buffers` can be served without reading from disk.

### Key Characteristics
- The primary PostgreSQL cache layer
- Persists across transactions and connections
- Tuned with `shared_buffers` in `postgresql.conf`; typical production values range from 25% to 40% of RAM

### When to Use
- Reduce disk reads for frequently accessed data
- Size large enough to hold hot working set

### When NOT to Use
- Not a query result cache; it caches raw blocks, not query outputs
- Oversizing can starve the OS page cache and hurt performance

**Also see**: [effective_io_concurrency](#effective-io-concurrency)
