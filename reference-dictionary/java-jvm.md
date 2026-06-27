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
