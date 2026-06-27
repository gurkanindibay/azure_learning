---
type: Article
title: "PostgreSQL 18’s Async I/O Isn’t Just Faster — It Changes How You Think About Slow Queries"
source: "https://medium.com/@the_atomic_architect/postgresql-18-async-io-slow-queries-d62e106fd676"
author:
  - "[[The Atomic Architect]]"
published: 2026-06-07
created: 2026-06-18
timestamp: 2026-06-18T00:00:00Z
description: "PostgreSQL 18's asynchronous I/O subsystem changes the traditional index-first mental model for cold, scan-heavy queries."
tags:
  - "clippings"
  - "postgresql"
  - "async-io"
  - "query-performance"
---

# PostgreSQL 18’s Async I/O Isn’t Just Faster — It Changes How You Think About Slow Queries

*The speedup is real. The more interesting part is what it does to the index reflex most of us have been running on for years.*

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ts-r34E18N1Br2OdKn6mMw.gif)

For most of my career, a slow query meant one thing: open the plan, find the sequential scan, and make it go away. Add an index, rewrite the join, push a filter down — anything to stop Postgres from reading the whole table. That instinct served me well, and it also quietly trained me to treat the I/O layer as a fixed cost I could not touch. PostgreSQL 18 is the first release that made me question the reflex itself. Its new asynchronous I/O subsystem does not just shave milliseconds; it changes which queries deserve to be called slow in the first place. By the end of this you will know where that shift is real and where it is closer to marketing.

## The Reflex Postgres Just Made Me Question

Here is the mental model I carried for years. A sequential scan is the enemy. Random access through an index is virtuous. If the planner picks a seq scan over a big table, something is wrong, and my job is to fix it.

That model was never wrong, exactly. It rested on an assumption that has now changed. The assumption was that Postgres reads one block, waits for the disk, then reads the next. On spinning disks, and even on SSDs sitting behind a network, that waiting dominated everything. A scan over a cold ten-gigabyte table felt slow because the CPU spent most of its life idle, staring at the disk.

So we optimized to avoid touching the disk at all. That is what an index really buys you on cold data: fewer blocks read. PostgreSQL 18 attacks the same problem from the other side. Instead of reading fewer blocks, it learns to read many blocks at once.

## What Async I/O Actually Changed Under the Hood

Before 18, Postgres leaned on the operating system’s readahead to guess what it would need next. The OS is a decent guesser, but it cannot see your query plan, so it often guessed wrong.

PostgreSQL 18 adds a real asynchronous I/O subsystem. A backend can now queue several read requests and keep working while the storage layer fills them in, with the data landing directly in shared buffers. You pick the mechanism with a new setting, `io_method`, which has three values.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Z8tGb4k2SqGxs4iKKLfLZw.png)

```c
# postgresql.conf — changing this requires a restart
io_method = 'worker'      # default: dedicated background I/O processes
# io_method = 'io_uring'  # modern Linux only, usually the fastest
# io_method = 'sync'      # the old pre-18 behavior, if you want it back
```

The `worker` method is the default and runs everywhere. The `io_uring` method talks to the Linux kernel directly and tends to be quickest on kernels that support it. The `sync` value is an escape hatch back to the way Postgres always behaved. One catch worth circling: this is not a runtime knob. You set it in the config and restart.

```c
Pre-18 (synchronous):
  read block -> wait -> read block -> wait -> read block -> wait
  the CPU idles while one disk request finishes at a time
PostgreSQL 18 (async):
  queue: block, block, block, block ...   all in flight
  results land in shared buffers as the storage returns them
```

The diagram is the whole idea. Same scan, same number of blocks, but the waiting is overlapped instead of serialized.

## Where the Speedup Shows Up, and Where It Quietly Does Not

This is the part most headlines skip, and it is the part that actually changes your decisions.

Async I/O in 18 covers reads only. Writes, including the write-ahead log, are still synchronous. And it does not accelerate every read either. The supported paths are sequential scans, bitmap heap scans, and maintenance work like VACUUM. Plain index lookups — the random single-row access your transactional endpoints lean on — are not in this first release.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*OA8Pt1jE08Dzv5W87t1JKA.png)

There is a second limit that matters even more in practice. The gains come from hiding disk latency. If the data you are scanning already sits in shared buffers or the OS cache, there was never any waiting to hide. To see a real difference, the data being read has to be larger than your cache. A benchmark on a table that fits in memory will show you almost nothing, and you will wrongly conclude the feature is hype.

The project’s own benchmarks report up to two to three times better throughput in specific read-heavy, disk-bound cases. That is a real number for the right workload. It is also not your number until you measure it on yours.

## Why a Sequential Scan Is No Longer Automatically the Enemy

Put those two facts together and the old reflex starts to wobble.

If a large sequential scan can saturate your storage bandwidth instead of dribbling out one blocking read at a time, the gap between “scan the table” and “use an index” narrows on cold data. For analytical queries over data that does not fit in memory, a fast scan can be the right plan, not a failure of one. The knob that controls how many concurrent reads Postgres will issue, `effective_io_concurrency`, used to be a forgotten setting with a default of 1. In 18 it defaults to 16, which tells you plainly how the project's own thinking moved.

I want to be fair about the other side. For a typical transactional service, this changes very little. If your hot path is cached index lookups and your real bottleneck is write throughput or lock contention, async reads will not touch your p99 latency. The index reflex is still correct far more often than not. What 18 does is carve out a real class of queries — big, cold, scan-heavy reads — where the old instinct now costs you more than it saves.

## What I Would Actually Tune Before Trusting It

If you are on 18 and want to feel this for yourself, here is a short and honest path.

Leave `io_method` on `worker` unless you are on a recent Linux kernel and willing to test, in which case try `io_uring` and compare directly. Then look at `effective_io_concurrency`. The new default of 16 is reasonable, but the right value depends on your storage. High-latency cloud volumes often reward going higher; a single local NVMe may not.

```c
-- New in 18: watch asynchronous I/O while a heavy query runs
SELECT * FROM pg_aios;
```

Then run a real query from your workload against a table larger than `shared_buffers`, with a cold cache, and compare it against `io_method = 'sync'`. That one A/B test will tell you more than any blog post, including this one. Do not assume the speedup until you have seen it on your own data and your own disks.

## The Habit That Actually Changed

The lasting thing about PostgreSQL 18 is not a faster database. It is a small dent in a habit. For years the safe move was to treat every sequential scan as a bug to be indexed away. That move is still usually right, but it is no longer automatically right, and knowing the difference is now part of the job.

If your team has already shipped 18 and measured something surprising — a query that got faster, or one that stubbornly did not — I would honestly like to hear which way it went and what your storage looked like.

## Reference Pack

- PostgreSQL 18 official release notes (the asynchronous I/O entry under the performance section)
- PostgreSQL 18 release announcement from the PostgreSQL Global Development Group
- The pganalyze write-up on accelerating disk reads with asynchronous I/O in Postgres 18
- The Aiven engineering post on why Postgres 18 put asynchronous I/O in the database
- PostgreSQL documentation for the `pg_aios` system view and the `io_method`, `io_workers`, and `effective_io_concurrency` settings
