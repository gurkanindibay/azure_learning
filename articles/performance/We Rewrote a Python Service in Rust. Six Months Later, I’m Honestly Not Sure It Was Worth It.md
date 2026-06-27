---
type: Article
title: "We Rewrote a Python Service in Rust. Six Months Later, I’m Honestly Not Sure It Was Worth It"
source: "https://medium.com/@the_atomic_architect/python-to-rust-rewrite-worth-it-57afd7c588e4"
author:
  - "[[The Atomic Architect]]"
published: 2026-06-25
created: 2026-06-27
description: "A production post-mortem of a Python-to-Rust rewrite: real latency, memory, and cost wins, the hidden velocity and hiring costs, and a decision framework for when a rewrite is actually justified."
tags:
  - "performance"
  - "rust"
  - "python"
  - "microservices"
  - "rewrite"
  - "gil"
  - "tokio"
  - "clippings"
---

# We Rewrote a Python Service in Rust. Six Months Later, I’m Honestly Not Sure It Was Worth It

The service hasn’t paged anyone in four months. The dashboards are flat and green, and every number I set out to move has moved. So why do I keep opening the old project board late at night and wondering if I made a mistake?

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*r_8wFtZK4QW3jcelpbTZdQ.png)

The wins were real. So were the costs.(generate by author)

Last summer I was the loudest voice in the room arguing for this rewrite. I built the benchmark deck. I drew the cost graph everyone nodded at. I was so sure.

Now I’m the one with the doubts, and that switch is the most interesting thing that happened in the whole project. So let me walk you through it honestly, including the parts the conference talks quietly leave out.

> **👉 Not a medium-members,** [**Read the Article here**](https://medium.com/@the_atomic_architect/python-to-rust-rewrite-worth-it-57afd7c588e4?sk=cd1236d8d1092e7d18df9db11d3153d7)

## The Part Where I Tell You It Actually Worked

I want to be fair to Rust before I start picking at it, because the wins were real, and they were not small.

The service was a request-processing layer sitting between our public API and Postgres. High concurrency, lots of small CPU-bound transforms, JSON in, JSON out, all day long. In Python it was a respectable but tired piece of software.

Here is what changed after we shipped the Rust version. These are production p99 figures over a steady week, same traffic shape, same database underneath.

```text
Metric                        Python (asyncio)   Rust (tokio)
─────────────────────────────────────────────────────────────
p99 latency                   240 ms             19 ms
Memory per instance           ~1.2 GB            ~110 MB
Pods to hold peak load        12                 3
Sustained throughput          1x (baseline)      ~3.4x
Monthly compute (service)     baseline           down ~58%
```

People fixate on the latency drop, but the memory and the pod count are where the money actually lived. We went from this shape:

```text
         ┌──────────────┐
         │ Load Balancer│
         └──────┬───────┘
                │
  ┌──────┬──────┼──────┬──────┐
  ▼      ▼      ▼      ▼      ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│ py │ │ py │ │ py │ │ py │ │ py │   …12 pods
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘   ~1.2 GB each
  └──────┴──────┼──────┴──────┘
                ▼
         ┌──────────────┐
         │   Postgres   │
         └──────────────┘
```

down to this one:

```text
         ┌──────────────┐
         │ Load Balancer│
         └──────┬───────┘
                │
  ┌────────┼────────┐
  ▼        ▼        ▼
┌────┐   ┌────┐   ┌────┐
│ rs │   │ rs │   │ rs │      3 pods
└─┬──┘   └─┬──┘   └─┬──┘      ~110 MB each
  └────────┼────────┘
           ▼
    ┌──────────────┐
    │   Postgres   │
    └──────────────┘
```

Same picture, a fraction of the footprint. The on-call channel got quiet. The [garbage-collection pauses](../../reference-dictionary/java-jvm.md#garbage-collection) that used to smear our tail latencies simply vanished, because there is no garbage collector left to pause.

If the story ended here, I’d be writing a victory lap and you’d be forwarding it to your skeptical tech lead. It does not end here, and that’s the part worth your time.

## Why We Touched a Working Service at All

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Fd4PecOR9ykMfqGoPPOGkw.png)

Many workers, one lock — and a single serialized lane.(generate by author)

The honest trigger was not performance. It was an incident I still feel a little sick about.

Under a sudden traffic spike, our Python workers started fighting each other for the [GIL](../../reference-dictionary/data-concurrency.md#global-interpreter-lock) on the heaviest transform path. Latency ballooned, retries stacked on top of retries, and a service that looked perfectly healthy at the median fell over at the tail, exactly when customers were watching.

I remember staring at a latency graph that looked like a heart monitor going flat, refreshing it as if refreshing would change the numbers. It didn’t. We scaled out, prayed, and limped through.

The transform itself was simple. The problem was that simple work, multiplied by real concurrency, walked straight into the one thing Python does not want you to think about.

```python
# Conceptually, this is what every worker was doing.
def handle(req):
    payload = parse(req.body)          # cheap
    enriched = normalize(payload)      # CPU-bound, and this is the part that hurt
    return serialize(enriched)
```

That `normalize` call was pure CPU work. Threads couldn't help because of the GIL, and multiprocessing helped a little while eating memory and adding its own coordination cost.

We were scaling horizontally to paper over a vertical problem, and the cloud bill had started to notice. So Rust, for this exact shape of pain, was an honest fit. Not a fashionable choice. A fitting one. Hold on to that distinction, because it turns out to be the whole argument.

## The Bill Nobody Put in the Proposal

Here is what my benchmark deck did not have a slide for.

The first cost is compile times, and nothing prepares a Python team for the moment a one-line change triggers a forty-second wait. Our clean build settled around six to eight minutes, and incremental builds during normal work landed between forty and ninety seconds depending on what you touched.

That doesn’t sound like much until you count how many times you compile while chasing a single bug. The edit-run-edit loop that lets you hold a whole problem in your head, the quiet flow state Python gives you for free, Rust takes that away for a few months. You get it back, but slower, and through a different door.

The second cost is subtler and more expensive. The language makes you say out loud things Python let you leave unsaid.

Shared mutable state is the classic example. In Python, a cache shared across requests is almost nothing.

```python
cache = {}

def get_or_compute(key):
    if key in cache:
        return cache[key]
    value = expensive(key)
    cache[key] = value
    return value
```

Five lines, and anyone on the team reads it in one glance. Here is the honest Rust equivalent for the same cache shared across async tasks.

```rust
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

let cache: Arc<Mutex<HashMap<String, Value>>> =
    Arc::new(Mutex::new(HashMap::new()));

// we are going inside each async task
let cache = Arc::clone(&cache);
async move {
    {
        let guard = cache.lock().unwrap();
        if let Some(v) = guard.get(&key) {
            return v.clone();
        }
    } // so hey devs, we purposely dropped guard dropped here

    let value = expensive(&key).await;
    cache.lock().unwrap().insert(key.clone(), value.clone());
    value
}
```

The idea is identical. The line count is not, and that inner scope block, the one that forces the lock to drop before the await, is not decoration.

We learned why it matters by deadlocking a staging environment first. That is the real tax. Not that Rust is hard, but that Rust makes you pay attention to costs Python had quietly been charging to a future invoice.

Sometimes that future invoice really was an outage waiting to happen. And sometimes it was never going to come due at all, and we paid the full price anyway.

## The Velocity Tax Is Real and Nobody Warns You

For roughly three months, we shipped slower. Measurably, visibly slower.

A feature that would have been an afternoon’s change in Python became a two-day change in Rust, not because the logic was harder, but because the team was relearning how to express logic at all.

The codebase grew, too. The Python service was around 2,800 lines, and the Rust port landed near 4,600 for the same behavior.

More lines isn’t automatically worse, and a lot of those extra lines are error handling Python simply skipped until it crashed in front of a user. But it is still more surface to read, review, and carry on your shoulders.

Then there was the new engineer. Strong, comfortable in Python and Go, joined us mid-migration. In our old stack they’d have opened a meaningful pull request within days. In the Rust service it took closer to three weeks before they were landing real changes without pairing.

That cost never shows up on a latency chart. Your hiring pool narrows. Your onboarding lengthens. The “anyone can jump in and fix this” quality you didn’t know you valued gets quietly more expensive, every single month, forever.

## The Uncomfortable Question I Avoided for Months

Here is the part that will annoy half the people who read it, and I’ve decided I don’t care.

A lot of Rust rewrites happening across our industry right now are not engineering decisions. They are status decisions wearing an engineering costume.

We rewrite in Rust because it feels serious. Because it looks impressive in a postmortem and even better on a résumé. Because saying “we run on Rust” buys a kind of credibility that saying “we run on boring Python” does not, regardless of what the workload actually needs.

I know this because part of my own motivation was exactly that, and I didn’t admit it to myself until long after we shipped. I wanted the hard thing. I wanted to be the person who did the hard thing.

That’s not a technical reason. That’s ego, and I had quietly let it sit in the driver’s seat of a decision that cost two engineers most of a quarter. The performance problem was real, but my certainty was partly performance of a different kind.

If you are about to rewrite something in Rust, the most useful question isn’t whether Rust is faster. It obviously is. The useful question is whether you’d still want to do it if nobody would ever know you did.

### So, Was It Worth It?

For this service, yes. Probably. The workload was genuinely CPU-bound and genuinely concurrent, the GIL was a real wall and not an imagined one, and the savings were large enough that the velocity hit paid for itself inside two quarters.

But “probably yes, for this one service” is a far smaller claim than the one I was making last summer. I was halfway to believing Rust was the answer to a question we hadn’t carefully asked.

For maybe a third of the services I’d been eyeing for the same treatment, the honest answer is no. They wait on the network and the database, not the CPU. Rust would make them faster on paper and slower to change in practice, and they change constantly, which is the worst possible trade dressed up as a good one.

### When You Should Actually Reach for This

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Y_pBveAbHzLa52cxvr2eug.png)

It depends on the shape of the pain, not the hype.(generate by author)

Let me give the fairest version of both sides, because a one-sided rewrite story is just marketing with footnotes.

Reach for Rust when your bottleneck is genuinely CPU or memory, when the service is stable enough that you aren’t rewriting a moving target, when latency tails actually cost you money or sleep, and when you can absorb a quarter of slower delivery to buy years of lower operating cost. Those conditions held for us, and the result was real.

Stay in Python, or reach for Go, when the work is I/O-bound, when the service changes weekly, when your team’s fluency is your actual moat, or when the performance problem is really an algorithm problem in a costume. We caught one service where a missing index, not the language, was the entire story, and a rewrite would have buried that lesson under a pile of new syntax.

There’s a middle path I badly undervalued, too. Rewriting the one hot function instead of the whole service. A small [native extension](../../reference-dictionary/architecture-patterns.md#native-extension) at the exact bottleneck would have bought a large share of the win at a fraction of the cost, and I dismissed it because it wasn’t exciting enough. Again, ego. Not engineering.

### What I’d Tell the Version of Me Who Started This

The rewrite worked, and I would do it again for this service. I would also do it far more quietly, with less certainty, and with a much smaller appetite for repeating it everywhere.

The thing I got wrong was never the technology. Rust delivered exactly what it promised, line for line. The thing I got wrong was treating a tool that fit one problem as a strategy for all of them, and letting the exciting answer impersonate the correct one.

The best engineering decision is rarely the most impressive one. Sometimes it’s a long rewrite in a language that makes you earn every line, and sometimes it’s an index, a profiler, and a quiet afternoon nobody will ever clap for.

The hard part is being honest with yourself about which one you’re actually looking at, especially when the answer that flatters you and the answer that’s true are not the same answer.

We got lucky this time. They happened to line up. I’m just no longer sure they will next time, and sitting with that uncertainty might be the only thing from this whole project I’d refuse to give back.
