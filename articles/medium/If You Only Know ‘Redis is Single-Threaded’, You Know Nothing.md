---
title: "If You Only Know ‘Redis is Single-Threaded’, You Know Nothing"
type: "Article"
source: "https://medium.com/@kanishks772/if-you-only-know-redis-is-single-threaded-you-know-nothing-0d0e4b7d56ec"
author:
  - "[[The Latency Gambler]]"
published: 2026-03-27
created: 2026-06-15
description: "More"
tags:
  - "clippings"
---
*Every engineer reaches for Redis. Almost none understand what’s running underneath it.*

“Redis is single-threaded” gets repeated so often it’s become a shorthand for understanding it. It isn’t. It’s a starting point and a misleading one if you stop there.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*RGSKDu-wJ3yrANnZ)

Ai Generated Image

Here’s what’s actually happening inside Redis at the architecture level.

## 1\. Single-Threaded, But Not Blocking: I/O Multiplexing

The reason Redis handles 100K+ concurrent connections on one thread isn’t because connections are cheap. It’s because Redis never waits on them.

Under the hood, Redis uses OS-level event loops `epoll` on Linux, `kqueue` on BSD/macOS. The model is called I/O multiplexing: one thread monitors all open file descriptors and reacts only when data is ready.

```c
Traditional multi-threaded server:
```
```c
Thread 1 ──► Connection A (waiting...)
Thread 2 ──► Connection B (waiting...)
Thread 3 ──► Connection C (working)Problem: threads block, context-switch, contend on locks
──────────────────────────────────────────
Redis event loop (single thread):
          ┌──────────────────────┐
          │     epoll/kqueue     │
          │  monitors all FDs    │
          └──────────┬───────────┘
                     │ "data ready on conn C"
                     ▼
          ┌──────────────────────┐
          │  Process conn C only │◄── no waiting, no blocking
          │  Return to loop      │
          └──────────────────────┘Result: zero locks, zero context switches,
        100% CPU time on actual work
```

This is why Redis hits microsecond latency while multi-threaded databases struggle with thread contention. The single thread isn’t a limitation, it’s a design choice that eliminates an entire class of coordination overhead.

## 2\. Hash Slots, Not Consistent Hashing

Redis Cluster is often assumed to use consistent hashing. It doesn’t.

It uses **16,384 fixed hash slots** with CRC16:

```c
# Redis key routing (simplified)
def get_slot(key: str) -> int:
    return crc16(key) % 16384
```
```c
# Each cluster node owns a range of slots:
# Node A: slots 0     – 5460
# Node B: slots 5461  – 10922
# Node C: slots 10923 – 16383
```
```c
Redis Cluster slot distribution:
```
```c
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Node A    │   │   Node B    │   │   Node C    │
│ slots 0–5460│   │5461–10922   │  │10923–16383  │
└─────────────┘   └─────────────┘   └─────────────┘
        ▲                 ▲                 ▲
        └────────────────┬┘                 │
                    CRC16(key) % 16384      │
                    routes here ────────────┘
```

When you rebalance, Redis moves slot ownership between nodes, it doesn’t rehash all existing keys. Adding a node means migrating a slice of slots. Predictable, bounded, operationally simple.

Consistent hashing is cleverer. Fixed slots are more controllable. Redis chose control.

## 3\. Fork + Copy-on-Write: How RDB Persistence Works Without Downtime

RDB snapshots seem like they should be expensive. Writing the entire memory state to disk while serving traffic should block everything.

It doesn’t, because of `fork()` and Linux Copy-on-Write:

```c
RDB snapshot sequence:
```
```c
Redis parent process (serving traffic)
         │
         │── fork() ──────────────────────────────────┐
         │                                            │
         ▼                                            ▼
Parent continues serving          Child process writes
writes/reads normally             memory snapshot to disk
         │                                            │
         │   Modified page? ──► OS duplicates it      │
         │   (COW kicks in)     only that page        │
         │                                            │
         │                       dump.rdb complete    │
         │◄──────────────────── child exits ──────────┘
         │
         continues
```

The child sees a consistent snapshot of memory at fork time. The parent keeps serving. Linux COW ensures only pages modified *after* the fork get duplicated in physical memory unchanged pages are shared. In practice, memory overhead is proportional to your write rate during the snapshot window, not your dataset size.

## 4\. LFU With an 8-Bit Counter

When Redis uses LFU (Least Frequently Used) eviction, it tracks access frequency per key. Storing a real counter for millions of keys would be prohibitive.

Instead, Redis uses a **Morris probabilistic counter** just 8 bits per key:

```c
# Morris counter: increment with decreasing probability
# Counter value c → actual frequency ~ 2^c
```
```c
def morris_increment(counter: int) -> int:
    # Higher counter = lower probability of incrementing
    # Prevents saturation while approximating log scale
    probability = 1.0 / (counter * 10 + 1)
    if random() < probability:
        return counter + 1
    return counter
```

The counter also **decays over time** stale-popular keys don’t hold top position forever. A key that was hot six hours ago and untouched since will eventually lose out to a key that’s actively used now.

8 bits per key. Logarithmic approximation. Time decay. That’s a full LFU system in a single byte.

## 5\. UNLINK Is Not DEL

Most engineers use `DEL` to remove keys. For small keys, the difference is irrelevant. For large keys say, a list with five million elements `DEL` blocks the main thread while it frees memory.

`UNLINK` doesn't:

```c
DEL large_key:
   Main thread ──► unlinks key ──► frees all memory ──► resumes
                                   (blocks here for large keys)
```
```c
UNLINK large_key:
   Main thread ──► removes key from keyspace ──► resumes immediately
                                                  │
                              background thread ◄─┘
                              handles memory free async
```
```c
# In production: prefer UNLINK over DEL for large data structures
# Sets, sorted sets, hashes, lists with many elements
```
```c
# Slow for large keys:
redis_client.delete("large_set")# Non-blocking:
redis_client.unlink("large_set")
```

The key disappears from the keyspace instantly. The memory gets cleaned up asynchronously. Main thread never stalls.

## 6\. Client-Side Caching With Server Invalidation (Redis 6+)

The standard pattern is: cache a value locally, set a TTL, hope it stays fresh. When the TTL expires, fetch again. It’s simple, but it’s guesswork on freshness.

Redis 6 introduced **TRACKING** server-assisted client-side caching:

```c
Without TRACKING:
```
```c
Client ──► GET key ──► Redis ──► value
Client caches locally (TTL-based guessing)
Client reads stale data until TTL expires
──────────────────────────────────────────With TRACKING:
Client ──► CLIENT TRACKING ON ──► Redis
Client ──► GET key ──► Redis ──► value (client caches it)Later:
App updates key ──► Redis
Redis ──► invalidation message ──► Client
Client ──► cache evicted, fetch fresh on next readResult: zero stale reads, fewer round trips
```

This is a meaningful architecture shift. Instead of clients polling or relying on TTLs, the server pushes invalidations. Fewer round trips *and* guaranteed freshness previously a contradiction.

## The Bigger Picture

```c
Redis internals at a glance:
```
```c
┌─────────────────────────────────────────────────────┐
│                    REDIS PROCESS                    │
│                                                     │
│  ┌────────────────────────────────────┐             │
│  │  Event Loop (epoll/kqueue)         │ ← 1 thread  │
│  │  I/O multiplexing, no blocking     │             │
│  └────────────────────────────────────┘             │
│                                                     │
│  ┌──────────────┐  ┌───────────────────┐            │
│  │ RDB snapshot │  │ UNLINK cleanup    │ ← bg thread│
│  │ (fork/COW)   │  │ async free        │            │
│  └──────────────┘  └───────────────────┘            │
│                                                     │
│  ┌─────────────────────────────────────┐            │
│  │ Cluster: 16,384 fixed hash slots    │            │
│  │ Eviction: 8-bit Morris LFU counter  │            │
│  │ Client cache: TRACKING invalidation │            │
│  └─────────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

## The Takeaway

“Single-threaded” describes one thread handling commands. It says nothing about event-driven I/O, background persistence, probabilistic eviction, async deletion, or server-pushed cache invalidation.

Every one of these is a deliberate design decision with a specific tradeoff. Understanding them changes how you configure Redis, how you structure your keys, and how you debug it when something goes wrong.

Most engineers use Redis correctly. The ones who understand the internals use it *well*.

*Follow for more writing on databases, distributed systems, and the engineering decisions hiding behind simple abstractions.*