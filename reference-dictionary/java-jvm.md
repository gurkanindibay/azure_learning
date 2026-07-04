---
type: Reference
title: "Java JVM & Memory Management"
description: "Core JVM memory concepts — heap, stack, metaspace, garbage collection, and common OutOfMemoryError scenarios — for backend engineers running Java and Spring Boot services."
timestamp: 2026-06-15T00:00:00Z
---

# Java JVM & Memory Management

> **Domain**: Java Virtual Machine memory layout, garbage collection, thread memory, and production troubleshooting signals.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| JVM Heap Memory | [`#jvm-heap-memory`](#jvm-heap-memory) |
| Young Generation | [`#young-generation`](#young-generation) |
| Old Generation | [`#old-generation`](#old-generation) |
| Stack Memory | [`#stack-memory`](#stack-memory) |
| Metaspace | [`#metaspace`](#metaspace) |
| PermGen | [`#permgen`](#permgen) |
| Garbage Collection | [`#garbage-collection`](#garbage-collection) |
| Minor GC | [`#minor-gc`](#minor-gc) |
| Major GC | [`#major-gc`](#major-gc) |
| Full GC | [`#full-gc`](#full-gc) |
| GC Pause | [`#gc-pause`](#gc-pause) |
| G1GC | [`#g1gc`](#g1gc) |
| ZGC | [`#zgc`](#zgc) |
| OutOfMemoryError | [`#outofmemoryerror`](#outofmemoryerror) |
| Memory Leak | [`#memory-leak`](#memory-leak) |
| ThreadLocal | [`#threadlocal`](#threadlocal) |
| Heap Dump | [`#heap-dump`](#heap-dump) |
| Java Flight Recorder | [`#java-flight-recorder`](#java-flight-recorder) |
| HashMap | [`#hashmap`](#hashmap) |
| Treeification | [`#treeification`](#treeification) |
| Virtual Threads | [`#virtual-threads`](#virtual-threads) |
| Leyden AOT | [`#leyden-aot`](#leyden-aot) |
| Helidon SE | [`#helidon-se`](#helidon-se) |
| Thread Pinning | [`#thread-pinning`](#thread-pinning) |
| Carrier Thread | [`#carrier-thread`](#carrier-thread) |

---

## JVM Heap Memory

### jvm-heap-memory

The **primary runtime memory area where Java objects live**. Every object created with `new` is allocated on the heap, and the heap is shared across all threads in a JVM process.

```bash
java -Xms2G -Xmx4G -jar app.jar
```

| Flag | Meaning |
|:---|:---|
| `-Xms` | Initial heap size |
| `-Xmx` | Maximum heap size |

**Also see**: [Young Generation](#young-generation), [Old Generation](#old-generation), [Garbage Collection](#garbage-collection)

---

## Young Generation

### young-generation

The **area of the heap for newly allocated objects**. Most objects die quickly here; the garbage collector runs frequently and cheaply in this region.

| Sub-area | Purpose |
|:---|:---|
| Eden | Where new objects are first allocated |
| Survivor 0 / Survivor 1 | Holding area for objects that survive a Minor GC |

**Also see**: [Minor GC](#minor-gc), [Old Generation](#old-generation)

---

## Old Generation

### old-generation

The **area of the heap for long-lived objects** that survive multiple Young Generation GC cycles. Also called the tenured generation. Collections here are slower and less frequent.

**Also see**: [Major GC](#major-gc), [Full GC](#full-gc)

---

## Stack Memory

### stack-memory

**Per-thread memory** that stores method call frames, local variables, and partial execution state. Each thread gets its own stack; frames are pushed on method entry and popped on exit.

```bash
-Xss512k
```

**Also see**: [OutOfMemoryError](#outofmemoryerror)

---

## Metaspace

### metaspace

The **off-heap region that stores class metadata, method metadata, and ClassLoader information** (replaced PermGen in Java 8). Unlike PermGen, Metaspace grows dynamically using native memory by default.

```bash
-XX:MetaspaceSize=256m
-XX:MaxMetaspaceSize=512m
```

**Also see**: [PermGen](#permgen), [OutOfMemoryError](#outofmemoryerror)

---

## PermGen

### permgen

The **permanent generation** used before Java 8 to store class metadata. Removed in Java 8 and replaced by [Metaspace](#metaspace), largely because PermGen had a fixed size that was hard to size correctly.

**Also see**: [Metaspace](#metaspace)

---

## Garbage Collection

### garbage-collection

The **automatic process by which the JVM reclaims memory occupied by objects that are no longer reachable**. GC removes unused objects so developers do not manage memory manually.

**Also see**: [Minor GC](#minor-gc), [Major GC](#major-gc), [Full GC](#full-gc), [G1GC](#g1gc), [ZGC](#zgc)

---

## Minor GC

### minor-gc

A **garbage collection event that cleans the Young Generation**. It is fast and frequent because most objects in Eden are short-lived.

**Also see**: [Young Generation](#young-generation), [Garbage Collection](#garbage-collection)

---

## Major GC

### major-gc

A **garbage collection event that cleans the Old Generation**. Slower than Minor GC because old objects are more likely to survive and the Old Generation is usually larger.

**Also see**: [Old Generation](#old-generation), [Full GC](#full-gc)

---

## Full GC

### full-gc

A **garbage collection event that cleans the entire heap**, including both Young and Old Generations. It is the most expensive type of GC and can cause long or noticeable application pauses.

**Also see**: [Major GC](#major-gc), [OutOfMemoryError](#outofmemoryerror)

---

## GC Pause

### gc-pause

A **stop-the-world pause** during which application threads are suspended while the garbage collector reclaims memory. GC pauses are the dominant cause of tail-latency spikes in managed runtimes when collection events are long or frequent.

### Key Characteristics
- **Stop-the-world**: most collectors pause all application threads during at least part of the collection.
- **Tail-latency sensitive**: p99/p99.9 latency often moves more than median latency because of outliers caused by pauses.
- **Collector-dependent**: G1GC targets a maximum pause time; ZGC aims for sub-10 ms pauses; Full GC events are typically the longest.

### When to Use
- N/A — GC pauses are a property of managed runtimes, not a feature to adopt.
- Measure them with GC logs, JFR, or APM tools before deciding on tuning or language changes.

### When NOT to Use
- Do not ignore GC pause metrics when latency SLAs are strict.
- Do not assume "no GC" is the only fix; tuning, collector selection, and heap sizing often suffice.

**Also see**: [Garbage Collection](#garbage-collection), [Full GC](#full-gc), [G1GC](#g1gc), [ZGC](#zgc)

---

## G1GC

### g1gc

**Garbage-First Garbage Collector** — the default collector in modern Java. Designed for large heaps with a target maximum pause time.

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
```

**Also see**: [Garbage Collection](#garbage-collection), [ZGC](#zgc)

---

## ZGC

### zgc

**Ultra-low latency garbage collector** designed for very large heaps and pause times under 10 ms. Best for latency-sensitive, large-scale applications.

**Also see**: [Garbage Collection](#garbage-collection), [G1GC](#g1gc)

---

## OutOfMemoryError

### outofmemoryerror

A **fatal JVM error thrown when the runtime cannot allocate memory** for an object or native resource. Common variants include:

| Variant | Cause |
|:---|:---|
| `Java heap space` | Heap exhausted |
| `GC overhead limit exceeded` | GC spends too much time reclaiming tiny amounts of memory |
| `Metaspace` | Class metadata exhausted |
| `Unable to create new native thread` | Too many threads / native memory exhausted |

**Also see**: [JVM Heap Memory](#jvm-heap-memory), [Metaspace](#metaspace), [Memory Leak](#memory-leak)

---

## Memory Leak

### memory-leak

A condition where **objects are no longer needed but remain referenced**, preventing the garbage collector from reclaiming them. Common Java causes include static collections, unclosed resources, [ThreadLocal](#threadlocal) misuse, and caches without eviction.

**Also see**: [OutOfMemoryError](#outofmemoryerror), [Heap Dump](#heap-dump)

---

## ThreadLocal

### threadlocal

A Java mechanism that **provides thread-local variables**, giving each thread its own isolated instance. Misuse — especially in thread pools — can cause [memory leaks](#memory-leak) because values are not automatically removed when a thread is reused.

**Also see**: [Memory Leak](#memory-leak)

---

## Heap Dump

### heap-dump

A **snapshot of all objects on the JVM heap** at a point in time. Used with tools such as Eclipse MAT or VisualVM to diagnose [memory leaks](#memory-leak) and [OutOfMemoryError](#outofmemoryerror) crashes.

```bash
jmap -dump:live,format=b,file=heap.hprof PID
```

**Also see**: [JVM Heap Memory](#jvm-heap-memory), [Memory Leak](#memory-leak), [Java Flight Recorder](#java-flight-recorder)

---

## Java Flight Recorder

### java-flight-recorder

A **low-overhead profiling and diagnostics framework** built into the JVM. JFR records detailed runtime events (GC, thread, memory, I/O) and is useful for production troubleshooting without heavy overhead.

**Also see**: [Heap Dump](#heap-dump), [Garbage Collection](#garbage-collection)

---

## HashMap

### hashmap

A **hash-table-based key-value map** in the Java Collections Framework. It hashes keys to indices in an internal array of buckets; each bucket stores a linked list of entries that share the same index. Java 8+ upgrades a bucket to a Red-Black Tree when the chain grows beyond a threshold and the backing array is large enough.

### Key Characteristics

- **Average O(1)** `get`, `put`, and `remove` — under uniform hashing and reasonable load factor.
- **Worst-case O(n)** when all keys collide and treeification does not apply.
- **Not thread-safe**; use `ConcurrentHashMap` for concurrent access.
- **Allows one `null` key** and multiple `null` values.

### When to Use

- Fast in-memory lookups by a well-distributed key.
- Caches, indexes, and deduplication sets where keys are immutable and hash-friendly.

### When NOT to Use

- As a production cache without bounds or eviction (use Caffeine or similar instead).
- With untrusted or attacker-controlled keys unless collision risk is mitigated.
- When iteration order must be predictable (use `LinkedHashMap` instead).

**Also see**: [Treeification](#treeification), [Hash Collision](../reference-dictionary/databases.md#hash-collision), [Red-Black Tree](../reference-dictionary/databases.md#red-black-tree)

---

## Treeification

### treeification

The **internal Java HashMap mechanism** that converts a bucket's linked-list collision chain into a Red-Black Tree when the chain exceeds `TREEIFY_THRESHOLD = 8` and the backing array capacity is at least `MIN_TREEIFY_CAPACITY = 64`.

### Key Characteristics

- Reduces worst-case lookup from **O(n)** to **O(log n)** for heavily colliding buckets.
- Only triggers when **both** threshold conditions are met; otherwise the map resizes instead.
- Adds per-entry memory overhead compared to a linked list.

### When to Use

- Treeification is automatic; you do not invoke it directly. You size and hash so that it can help when collisions occur.

### When NOT to Use

- Do not rely on treeification to fix a bad `hashCode()`. Prevention is cheaper than adaptive repair.
- Do not assume small HashMaps are protected; below capacity 64 they resize rather than treeify.

**Also see**: [HashMap](#hashmap), [Red-Black Tree](../reference-dictionary/databases.md#red-black-tree)

---

## Virtual Threads

**Project Loom Virtual Threads** — lightweight JVM-managed threads introduced in Java 21. Unlike platform threads (1:1 mapped to OS threads, ~1 MB stack each), virtual threads are managed by the JVM and mapped many-to-few onto platform threads (~hundreds of bytes each). When a virtual thread blocks on I/O, the JVM unmounts it and reassigns the carrier platform thread to another virtual thread.

### Key Characteristics
- Available since Java 21 (JEP 444) as a standard feature
- `Thread.ofVirtual().start(task)` or `Executors.newVirtualThreadPerTaskExecutor()`
- No pool needed — virtual threads are cheap enough to create one-per-task
- Automatic unmounting on blocking I/O (socket read/write, `Thread.sleep()`, `LockSupport.park()`)
- **Pinning risk**: `synchronized` blocks and native calls (JNI) pin the virtual thread to its carrier, blocking the OS thread

### When to Use
- High-concurrency I/O-bound services (HTTP handlers, database calls, message consumers)
- Replacing reactive/async programming models (callback hell) with synchronous-style code
- When you need goroutine-level concurrency scale in Java without rearchitecting to reactive streams

### When NOT to Use
- CPU-bound workloads (virtual threads don't add CPU parallelism — use platform threads + ForkJoinPool)
- Code with pervasive `synchronized` blocks (pinning degrades throughput)
- Pre-Java 21 runtimes (not available; use reactive or CompletableFuture)

### Also see
- [Task / async-await](dotnet-multithreading.md#task) — .NET equivalent async pattern
- [Leyden AOT](#leyden-aot) — complementary startup optimization
- [Helidon SE](#helidon-se) — framework that uses virtual threads for request handling

---

## Leyden AOT

**Project Leyden Ahead-of-Time Compilation** — a JVM feature that captures JIT-optimized native code during training runs and replays it on subsequent starts via an AOT cache. Reduces the JVM warmup penalty (interpreting bytecode, C1/C2 profiling) while retaining peak throughput.

### Key Characteristics
- Two-phase workflow: **training** (record) → **production** (replay from cache)
- JVM flags: `-XX:AOTTraining` (record), `-XX:AOTCache` (replay)
- Cache is version-specific: same JDK version, JVM flags, and classpath required
- Complementary to GraalVM Native Image (Leyden improves JVM startup; GraalVM compiles ahead-of-time to a standalone binary)
- Part of Project Leyden (JEP 483), targeting JDK 24+

### When to Use
- Serverless / containerized Java services with cold-start constraints
- Auto-scaling scenarios where new instances must reach peak throughput quickly
- Services with predictable code paths (training covers production behavior)

### When NOT to Use
- Long-running monolithic services with stable load (JIT eventually reaches similar peak)
- Frequently changing codebases (cache invalidation overhead)
- Environments where cache portability is required (cache is JDK-version-specific)

### Also see
- [Virtual Threads](#virtual-threads) — complementary concurrency optimization
- [Helidon SE](#helidon-se) — lightweight framework that benefits from AOT

---

## Helidon SE

**Helidon SE** — Oracle's lightweight, reactive Java microservices framework. Helidon SE (Standard Edition) provides a minimal web server without dependency injection, designed for small footprint and fast startup. Helidon 4 uses Java virtual threads for request handling, making blocking code efficient at high concurrency.

### Key Characteristics
- Two editions: **SE** (minimal, no DI) and **MP** (MicroProfile, full Jakarta EE)
- Helidon SE WebServer is a compact, programmatic API — no annotations, no classpath scanning
- Built-in support for virtual threads (Helidon 4+)
- ~5 MB hello-world JAR; fast startup even without AOT
- Native integration with Oracle JDK and Leyden AOT

### When to Use
- Small, high-throughput HTTP services where framework overhead matters
- When comparing Java microservice performance to Go (Helidon SE is the closest Java equivalent to Go's `net/http` in terms of framework weight)
- Greenfield services that want virtual threads without Spring Boot's dependency graph

### When NOT to Use
- Teams invested in Spring Boot ecosystem (Spring Boot 3.2+ also supports virtual threads)
- Applications requiring extensive middleware (Helidon MP is the fuller alternative)
- When you need a large ecosystem of third-party integrations (Spring has more)

### Also see
- [Virtual Threads](#virtual-threads) — the concurrency model Helidon SE uses
- [Leyden AOT](#leyden-aot) — complementary startup optimization
- [Azure App Service](azure-services.md#app-service) — deployment target

---

## Thread Pinning

**Thread Pinning** — a failure mode in JVM Virtual Threads where a virtual thread becomes permanently bound to its carrier OS thread and **cannot be unmounted**, even when blocked on I/O. The carrier thread is held captive, defeating the purpose of virtual threads and reintroducing the platform-thread starvation problem.

Pinning occurs in two situations:
1. The virtual thread holds a `synchronized` monitor lock while blocking
2. The virtual thread executes a native method (JNI/FFI)

```java
// ❌ PINS the carrier thread — OS thread blocked until lock released
synchronized(lock) {
    result = db.query();  // IO here holds the carrier thread hostage
}

// ✅ Virtual thread parks correctly — carrier thread freed immediately
lock.lock();
try {
    result = db.query();  // virtual thread unmounted; carrier runs other VTs
} finally {
    lock.unlock();
}
```

### Key Characteristics
- Silent by default — pinning does not throw an exception or produce a log warning
- Detection: `-Djdk.tracePinnedThreads=full` JVM flag emits stack traces on pin events
- JFR event `jdk.VirtualThreadPinned` available for monitoring
- Common in legacy code using `synchronized` on database/HTTP I/O paths
- Go channels and goroutines have no equivalent pinning risk — scheduler-awareness is native

### When to Use
- Understanding thread pinning is required before enabling virtual threads in any service with existing synchronized blocks

### When NOT to Use
- (Not a pattern to use — a failure mode to detect and eliminate)

### Also see
- [Virtual Threads](#virtual-threads) — the feature thread pinning undermines
- [Carrier Thread](#carrier-thread) — the OS thread that gets pinned
- [Goroutine](concurrency-runtimes.md#goroutine) — Go's scheduler-native alternative with no pinning concept

---

## Carrier Thread

**Carrier Thread** — in the JVM Virtual Threads model, a carrier thread is the **OS-level platform thread** that a virtual thread is currently mounted onto and executing on. The JVM scheduler mounts and unmounts virtual threads onto carrier threads as they become runnable or block.

```
Virtual Thread lifecycle on a carrier:

  [Runnable] ──mount──▶ [Running on Carrier-1] ──IO block──▶ [Parked]
       ▲                                                          │
       └──────────────────────unmount◀────────────────────────────┘
  Carrier-1 is immediately free to run another virtual thread
```

### Key Characteristics
- Carrier threads form a fixed pool (default: `ForkJoinPool`, size = CPU count)
- A virtual thread is only consuming CPU when mounted on a carrier
- Unmounting on I/O block is the core mechanism enabling high concurrency — carrier threads are never wasted waiting
- **Pinning breaks unmounting**: if the virtual thread holds a `synchronized` lock, the carrier cannot be freed (see [Thread Pinning](#thread-pinning))
- Configurable via `jdk.virtualThreadScheduler.parallelism` system property

### When to Use
- When diagnosing virtual thread performance: check carrier thread pool saturation, not virtual thread count
- Tuning: `jdk.virtualThreadScheduler.parallelism` controls the carrier pool size for CPU-heavy virtual-thread workloads

### When NOT to Use
- Carrier threads are an implementation detail of the JVM; application code should not interact with them directly

### Also see
- [Virtual Threads](#virtual-threads) — the feature carrier threads support
- [Thread Pinning](#thread-pinning) — failure mode where carrier threads get stuck
- [Goroutine](concurrency-runtimes.md#goroutine) — Go's equivalent where OS threads are the implicit carrier pool

