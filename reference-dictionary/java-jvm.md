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
| CallerRunsPolicy | [`#callerrunspolicy`](#callerrunspolicy) |
| Stream Gatherers | [`#stream-gatherers`](#stream-gatherers) |
| Scoped Values | [`#scoped-values`](#scoped-values) |
| Structured Concurrency | [`#structured-concurrency`](#structured-concurrency) |
| Foreign Function & Memory API | [`#foreign-function-and-memory-api`](#foreign-function-and-memory-api) |
| Compact Object Headers | [`#compact-object-headers`](#compact-object-headers) |
| Generational ZGC | [`#generational-zgc`](#generational-zgc) |
| Lazy Constants | [`#lazy-constants`](#lazy-constants) |

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

---

## CallerRunsPolicy

### callerrunspolicy

A `ThreadPoolExecutor` **rejection policy** in Java that, when the work queue is full and the pool is at maximum capacity, makes the **calling (producer) thread execute the task directly** instead of rejecting it or throwing an exception.

```java
new ThreadPoolExecutor(
    corePoolSize, maxPoolSize,
    keepAlive, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(5000),
    new ThreadPoolExecutor.CallerRunsPolicy()
);
```

### Key Characteristics
- **Automatic backpressure**: when the producer thread executes the task, it cannot submit more tasks until the current one completes — naturally slowing production
- **No data loss**: tasks are never silently dropped or rejected; the caller absorbs the work
- **Feedback loop**: the slowdown propagates upstream to the producer, which may be a batch loop, a message consumer, or a scheduler
- **Thread context inversion**: the producer thread temporarily becomes a worker, which can cause unexpected behavior if the producer is a request-serving thread (e.g., Tomcat HTTP thread)

### When to Use
- Offline batch jobs, scheduled processing, data migration, and SMS/email campaigns where the producer is a dedicated worker thread
- Bounded queue scenarios where you want flow control without additional coordination code
- Systems where tasks must never be silently discarded

### When NOT to Use
- **Request-serving threads**: Tomcat, Jetty, or Netty HTTP threads — if they start executing batch work, the server stops accepting new HTTP requests, freezing the website
- Low-latency APIs where the caller cannot afford to block on task execution
- When the task execution time is unpredictable or unbounded (the caller may block indefinitely)

### Also see
- [Backpressure](resilience.md#backpressure) — the general pattern that CallerRunsPolicy implements locally
- [Bounded Queue](resilience.md#backpressure) — the queue strategy that pairs with this policy
- [Virtual Threads](#virtual-threads) — an alternative concurrency model that avoids thread-pool sizing entirely

---

## Stream Gatherers

### stream-gatherers

An extension point for the Java Stream API (JEP 461/473/485) that enables developers to define **custom intermediate stream operations** with managed state, short-circuiting, and transformation capabilities (one-to-one, one-to-many, many-to-one, and many-to-many).

### Key Characteristics
- Extends intermediate pipeline capabilities beyond built-in operators (`map`, `filter`, `flatMap`)
- Invoked via `stream.gather(Gatherer)`
- Built-in gatherers in `java.util.stream.Gatherers` include `windowFixed(n)`, `windowSliding(n)`, `fold()`, `scan()`, and `mapConcurrent()`
- Supports parallel execution and stateful, ordered streaming without breaking stream laziness

### When to Use
- Implementing custom chunking, sliding windows, deduplication, or running totals directly in stream pipelines
- When avoiding premature collection into intermediate in-memory lists (e.g. `Collectors.groupingBy()`)

### When NOT to Use
- For simple mapping or filtering operations where standard `map()` and `filter()` suffice
- When terminal aggregation into collections is all that is required (use `Collector`)

### Also see
- [Virtual Threads](#virtual-threads) — concurrency model for streaming pipelines

---

## Scoped Values

### scoped-values

A lightweight, immutable mechanism (JEP 429/446/481/487) for **sharing contextual data safely and efficiently within and across threads** without the memory and safety drawbacks of `ThreadLocal`.

### Key Characteristics
- Immutable: bound values cannot be modified during the scope execution
- Automatically bounded lifetime: values are popped when the `run()` or `call()` scope ends
- Replaces `ThreadLocal` with negligible memory overhead, making it safe for millions of Virtual Threads
- Supports rebinding in child scopes without mutating the parent binding

### When to Use
- Propagating request metadata, tenant identifiers, security principals, and distributed tracing spans across method calls and subtasks
- Virtual-thread-heavy applications where `ThreadLocal` causes unbounded memory growth

### When NOT to Use
- When mutable state must be updated during execution (use dedicated mutable request context objects instead)
- On legacy JDK versions (< Java 21)

### Also see
- [ThreadLocal](#threadlocal) — legacy alternative with mutability and leak risks
- [Virtual Threads](#virtual-threads) — primary concurrency use case for Scoped Values
- [Structured Concurrency](#structured-concurrency) — propagates scoped values to child tasks

---

## Structured Concurrency

### structured-concurrency

A concurrency paradigm (JEP 428/453/480/499) that treats **groups of concurrent subtasks executing in separate threads as a single unit of work**, ensuring that subtasks are created, joined, and cancelled within a deterministic syntactic scope.

### Key Characteristics
- Implemented via `StructuredTaskScope` in `java.util.concurrent`
- Core policies include `ShutdownOnFailure` (fail-fast: cancel siblings on first error) and `ShutdownOnSuccess` (race: return first successful result)
- Guaranteed cleanup: try-with-resources blocks ensure all child virtual threads are terminated before exiting
- Preserves call hierarchy and relationship in thread dumps and diagnostic tooling

### When to Use
- Fan-out/fan-in aggregation requests (e.g., API gateway calling multiple microservices concurrently)
- Ensuring sibling tasks are short-circuited and cancelled immediately if any critical task fails

### When NOT to Use
- Fire-and-forget background worker threads that must outlive the HTTP request lifecycle
- Asynchronous event-driven messaging queues where tasks are decoupled across time

### Also see
- [Virtual Threads](#virtual-threads) — underlying lightweight execution threads
- [Scoped Values](#scoped-values) — inherited across structured scopes

---

## Foreign Function & Memory API

### foreign-function-and-memory-api

A modern Java API (JEP 454, Project Panama) that enables Java programs to **interoperate with native code and off-heap memory safely, efficiently, and without the risks of JNI**.

### Key Characteristics
- Pure Java interface for allocating off-heap memory (`Arena`, `MemorySegment`, `MemoryLayout`)
- Binds and executes C/native functions via `Linker` and `SymbolLookup` without writing C JNI wrappers
- Explicit memory lifetime governance through confined, shared, or automatic arenas
- Prevents use-after-free and dangling pointer bugs common in unmanaged C integration

### When to Use
- Interfacing with native C/C++ libraries: machine learning frameworks (ONNX, LibTorch), high-performance databases (RocksDB), graphics engines, or hardware drivers
- Managing large off-heap memory caches to avoid JVM GC overhead

### When NOT to Use
- Standard enterprise CRUD applications where native performance is unnecessary
- Cross-platform codebases where native dependencies complicate portability

### Also see
- [Metaspace](#metaspace) — off-heap class metadata region
- [JVM Heap Memory](#jvm-heap-memory) — managed memory counterpart

---

## Compact Object Headers

### compact-object-headers

An optimization in the HotSpot JVM (JEP 450/490, Project Lilliput) that **compresses the 64-bit object header from 128 bits (16 bytes) down to 64 bits (8 bytes)**.

### Key Characteristics
- Encodes the Mark Word and Class Pointer (Klass Word) into a single 64-bit header
- Reduces memory consumption by 10% to 20% across large-heap and object-intensive workloads
- Improves CPU L1/L2 cache density by fitting more live object references per cache line
- Enabled via `-XX:+UnlockExperimentalVMOptions -XX:+UseCompactObjectHeaders`

### When to Use
- Memory-constrained cloud containers (e.g. Kubernetes pods with strict RAM limits)
- High-throughput services allocating millions of small, short-lived domain and DTO objects

### When NOT to Use
- 32-bit JVM architectures (already use small headers)
- Systems requiring unsupported legacy JVMTI agents incompatible with compressed headers

### Also see
- [JVM Heap Memory](#jvm-heap-memory) — primary beneficiary of reduced header size
- [Generational ZGC](#generational-zgc) — complementary garbage collection optimization

---

## Generational ZGC

### generational-zgc

An enhancement to the Z Garbage Collector (JEP 439) that **separates the heap into young and old generations**, retaining sub-millisecond pause times while significantly reducing CPU overhead and improving allocation throughput.

### Key Characteristics
- Preserves ZGC's core guarantee of sub-1ms stop-the-world pauses
- Exploits the weak generational hypothesis (most objects die young), collecting young generations frequently with low CPU overhead
- Enabled via `-XX:+UseZGC -XX:+ZGenerational`
- Eliminates "allocation stall" spikes that affected single-generation ZGC under rapid allocation bursts

### When to Use
- Latency-critical microservices requiring strict p99/p99.9 SLAs (<10ms) under heavy traffic
- Large heaps (e.g. 16 GB to terabytes) where G1GC pause times exceed tolerance

### When NOT to Use
- Ultra-small heaps (<512 MB) where Serial GC or G1GC has lower baseline memory footprint
- Batch processing jobs where raw batch throughput is prioritized over latency pauses

### Also see
- [ZGC](#zgc) — single-generation predecessor
- [G1GC](#g1gc) — default throughput-balanced collector
- [GC Pause](#gc-pause) — the metric minimized by Generational ZGC

---

## Lazy Constants

### lazy-constants

A Java language and runtime preview feature that provides a **thread-safe, high-performance abstraction for lazy initialization of constants and singleton resources** without manual synchronization or double-checked locking boilerplate.

### Key Characteristics
- Provided via `java.lang.Lazy` (or computed constants abstraction)
- Guarantees exactly-once evaluation of the supplier in multi-threaded environments
- Replaces error-prone double-checked locking and `volatile` synchronization patterns
- Enables the HotSpot JIT compiler to fold constant references once initialized

### When to Use
- Heavy resource initialization (e.g., database connection factories, cryptographic engines, large configuration maps) that should only run when first accessed
- Thread-safe singleton patterns without synchronization overhead on subsequent reads

### When NOT to Use
- Simple, cheap values that can be safely initialized statically at class-load time
- Values that change dynamically over the application lifecycle (use caching abstractions instead)

### Also see
- [CallerRunsPolicy](#callerrunspolicy) — concurrency policy
- [HashMap](#hashmap) — common data structure initialized lazily


