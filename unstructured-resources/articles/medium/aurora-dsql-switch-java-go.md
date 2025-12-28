AWS Switched Aurora DSQL From JVM To Rust — And Got 10× More Throughput. What Actually Changed?
The Atomic Architect
The Atomic Architect

Following
13 min read
·
4 hours ago
56






Press enter or click to view image in full size

I used to defend the JVM like it was a family member. Not out of nostalgia, and not because I dislike other languages. I defended it because I’ve watched the JVM do “impossible” things in production when the workload is shaped right and the system is engineered with care.

Then I read the Aurora DSQL story and felt a very specific kind of doubt. Not the shallow “Java is slow” doubt that fuels internet wars. The deeper one, the kind that shows up when you realize you may have been arguing about the wrong problem.

Because the number wasn’t a cute improvement. It was the kind of number that forces you to stop talking and start asking what the system is really paying for. A hot component was rewritten, moved from JVM code to Rust, and throughput went up by roughly an order of magnitude.

If you’ve been around performance long enough, you know the rule. When someone claims 10×, one of three things is usually true: the old system was doing something catastrophically expensive, the new system changed architecture more than language, or the workload punishes one runtime and rewards the other.

The interesting part is that all three can be true at the same time. And when they are, “Rust is faster” becomes the least useful explanation you can give. So let’s talk about what actually changed, in the only way this topic is worth discussing.

The Moment The Number Didn’t Make Sense
A lot of people reacted the same way when they saw that claim. “Rust isn’t 10× faster than Java,” “the JVM JIT is extremely advanced,” “modern collectors can be highly efficient,” and “this has to be algorithmic.” All of those reactions are reasonable, and none of them make the number vanish.

That’s the trap. When a number feels “too big,” we start searching for one magical cause that explains everything. Object headers, inlining, allocators, escape analysis, pauses, or some single switch that supposedly flips performance from bad to good.

Those details matter, but they rarely create a 10× story by themselves. Ten-times stories usually come from removing a multiplier, not shaving a constant. You don’t get 10× by shaving nanoseconds off a call; you get 10× by deleting a whole category of “sometimes we stall and then everything stacks up.”

That kind of stall doesn’t show up in your median charts. It shows up in the tail, and then it quietly strangles throughput by forcing the system to carry unfinished work. If you understand that mechanism, you’ll understand why this rewrite could move the number so far.

What That Component Really Does
Let’s name the shape of the problem without drowning in internal terminology. Aurora DSQL is a distributed SQL database, which means transactions have to be decided, ordered, and committed across a fleet. In that path, there’s a component that behaves like an adjudicator, sitting in the middle of coordination.

It receives requests, fans out to other nodes, waits for enough replies, makes a decision, and moves forward. The expensive part isn’t “doing computation.” The expensive part is waiting, and the real cost of waiting is not just time — it’s the work you accumulate while you wait.

Queues build up, sockets stay open, state sticks around, and concurrency structures fill. A coordinated system doesn’t merely slow down when it stalls; it can reshape itself into something worse. That’s why “language choice” can matter more here than in a standalone service, not because one language is magical, but because predictability is a performance feature.

The 40-Host Lottery
Here’s the mental model that makes the whole story click. Every request in a distributed system is a lottery, and it’s rarely a lottery with one ticket. If your request fans out to many participants, you’ve just bought many tickets, and you only need one to lose.

Each participant is a chance for a bad moment. A scheduler delay, a page fault, a lock convoy, a noisy neighbor effect, a stalled buffer, or a runtime event that pauses progress. None of those have to happen often to matter, because you don’t need everyone to be slow — you only need one.

So the question becomes brutal and simple. How often does any participant have a bad moment during the window where your request is waiting? Because “rare per host” can become “common per request” when the fanout is large.

Here’s a simple way to see it. Assume each participant has a small chance of a stall in the relevant window, and compute the probability that at least one participant stalls when the request touches many participants.

Probability Of At Least One Stall

Per-Host Stall Chance     Fanout 10     Fanout 20     Fanout 40
0.1%                      ~1.0%         ~2.0%         ~3.9%
0.2%                      ~2.0%         ~3.9%         ~7.7%
0.5%                      ~4.9%         ~9.5%         ~18.2%
1.0%                      ~9.6%         ~18.2%        ~33.1%
Read the last row slowly. If each participant has a 1% stall chance, then roughly one third of requests see at least one stall at fanout 40. That’s not a corner case; it’s a structural property of the system.

This is why coordination collapses in surprising ways. It’s also why a runtime that is perfectly fine for one workload can feel painful for another: not because it’s slow, but because it’s occasionally surprising.

Why One Stall Turns Into Throughput Collapse
Now let’s connect the stall to throughput. When one participant stalls, the coordinator can’t complete the decision, so the request lives longer. While it lives longer, it holds resources: memory, sockets, in-flight bookkeeping, and attention from concurrency mechanisms.

Meanwhile, new requests arrive, and they also start holding resources. They also fan out, and they also buy more lottery tickets. If the system accumulates unfinished work faster than it drains it, it hits a queueing cliff that looks like “sudden slowdown.”

This is the part engineers feel but often struggle to describe cleanly. At low load, a stall is just a stall. At higher load, a stall becomes a multiplier, because it increases time-in-system, which increases in-flight work, which increases the chance of hitting stalls again.

Benchmarks often measure how fast you run when nothing goes wrong. Distributed systems are mostly about how you behave when something does go wrong, because something always does.

The Diagram That Explains The Whole Story
This is the simplest diagram I know that captures the difference between “fast” and “high throughput.” It’s a coordinator in the middle, fanning out and waiting for enough replies.

Client Request
     |
     v
+-------------+        Fanout        +---------+
| Adjudicator |--------------------->| Node A  |
+-------------+ \------------------->| Node B  |
       |        \------------------->| Node C  |
       |         \------------------>| Node D  |
       |          \--------------->  | Node ...|
       v
Decision Requires Enough Responses
       |
       v
Commit / Reply
Now add one realistic detail: sometimes one node has a bad moment. That single bad moment delays the decision, which increases the number of in-flight requests, which increases the system’s internal pressure.

Node C Stall
     |
     v
Coordinator Waits Longer
     |
     v
More Requests Arrive During The Wait
     |
     v
In-Flight Work Grows
     |
     v
More Fanout, More Chances For Another Stall
     |
     v
Throughput Drops Even If Median Latency Looks Calm
If you have ever watched throughput collapse while the median stays “fine,” this is why. The system isn’t merely slower; it’s carrying more unfinished work, and that changes everything.

Rust Didn’t Add Speed; It Removed Surprise
This is the uncomfortable truth that annoys both camps. The JVM can be astonishingly fast, and LLVM can be astonishingly fast. In many hot paths, both can produce excellent machine code.

The bigger difference is what becomes hard to do by accident. Rust forces you to confront ownership and lifetimes, and it pushes you toward shapes that often reduce allocation churn and reduce unpredictable memory behavior. That doesn’t mean Rust is automatically fast; it means certain “surprise generators” become less likely if you write in the style Rust nudges you toward.

In a coordinated component, that matters. A coordinated system doesn’t reward peak speed as much as it rewards steady progress. Predictability is throughput, because predictability prevents backlog, and backlog is the real enemy.

The Allocation Story People Get Wrong
A lot of discussions get stuck on a misleading simplification. One side says “GC is expensive,” and the other side says “allocation on the JVM is basically a pointer bump.” Both can be true, depending on the workload, and neither is the whole story.

The issue is rarely that allocation itself is slow. The issue is what the system must do as the set of live objects grows and the memory graph becomes complex. Tracing costs, compaction costs, remembered set costs, and poor locality can become visible, and they become even more costly when a coordination component is sensitive to any stalls at all.

Also, in coordinated systems, the cost of a stall is not just the time you lost. The cost is that you delayed a decision, and that delay held resources long enough for the system to accumulate more in-flight work. When in-flight work grows, you get more fanout pressure, more contention pressure, and the same stall becomes easier to trigger again.

That is why some engineers honestly experience modern GC as a net speedup. If they have spare memory and the majority of objects die young, the trade can be excellent. But if the system is high-residency and coordination-heavy, even modest unpredictability can turn into a throughput problem.

The Memory Layout Tax
People love to argue about object headers because it’s tangible. But the bigger cost is often layout, because layout determines locality, and locality determines how many cache misses you pay for.

Many Java systems naturally become object graphs over time. Objects point to objects, which point to objects, and even when the JIT does a great job, the CPU still has to chase pointers. Pointer chasing is a tax you pay in memory stalls, not in instruction counts.

Rust tends to nudge teams toward packed state: vectors of structs, contiguous buffers, indices instead of pointers, and predictable iteration. It doesn’t guarantee it, but it makes it easier to adopt without fighting the language’s default style.

Here’s the simplest contrast.

Object Graph Layout (Pointer Chasing)

[Obj A] -> [Obj B] -> [Obj C] -> [Obj D] -> [Obj E]
  scattered across memory pages, unpredictable access

Packed Layout (Contiguous)

[ A | B | C | D | E | F | G | H | I | J ]
  predictable stride, cache-friendly, stable iteration
This is why some rewrites feel like magic. They didn’t just “make code faster.” They made memory behave, and the CPU is obsessed with memory behavior.

The Benchmark That Makes People Argue
I’ll keep this deliberately simple, because the point is not to win a debate. The point is to see the multiplier clearly.

In a coordinator that fans out to many participants, the system’s throughput is highly sensitive to the probability of stalls. Even if stalls are rare per participant, the probability that at least one participant stalls in a request window rises quickly as fanout grows.

That table earlier is already the benchmark. It’s a stability benchmark, not a microbenchmark. It tells you how often your requests fall into the slow path that holds resources and creates backlog.

Now add one more reality: a stall doesn’t need to be massive to hurt throughput. It just needs to be long enough to cause work to pile up, because the pile-up increases the chance of the next request encountering the same pressure. This is how systems “suddenly” get slow even when nothing obvious changed.

So when you ask what changed in the rewrite, the most plausible high-level answer is not “each request became 10× cheaper.” The plausible answer is “far fewer requests fell into the slow path that creates backlog,” which can absolutely produce a large throughput gain.

A JVM Engineer Would Object Right Here
And they should, because the JVM has weapons. Inlining can be extremely aggressive, speculative optimizations can be extremely powerful, and allocation can be very efficient. With the right workload and enough breathing room, JVM systems can be among the fastest you will ever run.

So why could a Rust rewrite still win by a large factor in this specific story? Because this is not a single-thread loop chasing peak speed. This is a coordination-heavy component inside a distributed database, where variance is a throughput killer.

In that world, “how fast you run when you’re running” matters less than “how reliably you keep running.” A system can have amazing peak speed and still lose if it has frequent stalls that amplify across fanout.

Two Code Shapes That Can Change The Outcome
Now let’s ground this in code, not ideology. First, a very common Java style that is readable and idiomatic, but tends to allocate intermediate structures and create object shapes that are not locality-friendly as the program evolves.

This is not “bad Java.” This is how many teams naturally end up writing when they move fast and add features.

import java.util.*;
import java.util.stream.*;

final class AdjudicatorJava {
  record Vote(long txnId, int nodeId, long ts, boolean ok) {}

  long decide(List<List<Vote>> batches) {
    Map<Long, List<Vote>> byTxn =
      batches.stream()
        .flatMap(List::stream)
        .collect(Collectors.groupingBy(Vote::txnId));

    long committed = 0;
    for (var e : byTxn.entrySet()) {
      long txn = e.getKey();
      var votes = e.getValue();
      long okCount = votes.stream().filter(Vote::ok).count();
      if (okCount >= quorum(votes.size())) {
        committed += apply(txn, votes);
      }
    }
    return committed;
  }

  int quorum(int n) { return (n / 2) + 1; }
  long apply(long txn, List<Vote> votes) { return txn ^ votes.size(); }
}
Now compare a Rust-leaning shape that tends to keep state packed and iteration predictable. Again, this isn’t about clever tricks; it’s about creating a data layout that reduces unpredictable memory behavior in a hot coordinator path.

#[derive(Clone, Copy)]
struct Vote {
    txn_id: u64,
    node_id: u16,
    ts: u64,
    ok: bool,
}
struct Arena<T> {
    items: Vec<T>,
}
impl<T> Arena<T> {
    fn new() -> Self { Self { items: Vec::new() } }
    fn push(&mut self, v: T) -> usize {
        let id = self.items.len();
        self.items.push(v);
        id
    }
    fn get(&self, id: usize) -> &T { &self.items[id] }
}
struct AdjudicatorRust {
    votes: Arena<Vote>,
    txn_index: Vec<(u64, usize, usize)>, // (txn_id, start, len)
}
impl AdjudicatorRust {
    fn decide(&mut self, incoming: &[Vote]) -> u64 {
        let start = self.votes.items.len();
        for &v in incoming {
            self.votes.push(v);
        }
        let end = self.votes.items.len();
        self.build_index(start, end);
        let mut committed = 0u64;
        for &(txn_id, s, len) in &self.txn_index {
            let mut ok = 0usize;
            for i in 0..len {
                if self.votes.get(s + i).ok { ok += 1; }
            }
            if ok >= ((len / 2) + 1) {
                committed ^= txn_id ^ (len as u64);
            }
        }
        committed
    }
    fn build_index(&mut self, _start: usize, _end: usize) {
        self.txn_index.clear(); // imagine this is built from sorted votes
    }
}
In real systems the story is more complex, but the point remains. Compact data and predictable access patterns reduce the probability of bad moments, and in coordination-heavy code, reducing bad moments can move throughput more than any micro-optimization.

The Inlining Debate Is A Distraction Here
Inlining debates are fun, and they’re not useless. But they mostly change how fast you run while you’re running. The Aurora DSQL story, as described, reads like a story about how often you stop running.

If you change the probability of stalls, you change the number of requests that fall into the slow path. If you change the number of requests that fall into the slow path, you change backlog behavior. If you change backlog behavior, you can change throughput by a large factor.

This is why the same conversation keeps looping in circles online. People argue peak speed, while the system is telling a story about tail amplification.

The Part Many People Quietly Skip
A rewrite like this is almost never “only a language change.” When you rewrite a hot component, you simplify, delete layers, choose different data structures, move boundaries, and remove costs you had normalized. Even if you swear you didn’t, the act of rewriting changes what you tolerate.

So yes, architecture matters, and algorithm choices matter. But here’s the twist that makes this story relevant: language nudges architecture. Java nudges many teams toward object graphs unless they actively fight it; Rust nudges many teams toward packed state unless they actively fight it.

In a coordinator that lives in the land of fanout and tail, those nudges can change the probability of stalls. And probability is the hidden axis in distributed performance.

Where Java Still Wins
If you read this and conclude “Java is slow,” you missed the point. The JVM is often brutally fast, and it can be the right choice for performance and for engineering throughput, especially when systems evolve for years and teams need strong abstraction and tooling.

Low-level control is not free. It is paid later, in complexity, in maintainability, and in the cost of change. Many systems win overall because the JVM lets teams ship reliably without paying that cost upfront.

But if your hottest bottleneck is a coordination-heavy path where variance is a throughput killer, you must respect the multiplier. Coordinated systems don’t reward best-case performance; they punish worst-case surprises.

What Actually Changed, In One Sentence
Here is the sentence that explains the whole story without tribal noise.

The rewrite didn’t win because Rust is “faster.” The rewrite won because it made stalls rarer, and in a coordinated system, making stalls rarer is one of the highest-leverage performance changes you can make.

That’s it.

Reduce variance and the system breathes. Reduce variance and queues shrink. Reduce variance and your fleet stops acting unpredictable under pressure.

Once the fleet stops acting unpredictable, numbers can jump in ways that look impossible from the outside.

The Closing Question That Actually Matters
If you’re still thinking, “So should I rewrite my Java service in Rust,” that’s not the real question. The better question is where your system is buying the 40-host lottery, and what your real stalls are.

If your stalls come from network and storage, language won’t save you. If your stalls come from a coordinator that accumulates backlog because its worst moments amplify across fanout, a rewrite can move the universe.

If you disagree, I want the disagreement, because this topic deserves useful arguments. Which part do you think is wrong: the fanout math, the backlog story, the memory layout angle, or the idea that variance is the hidden lever?

Because this is why the Aurora DSQL story spread. It isn’t Rust versus Java. It’s the uncomfortable realization that “fast” and “high throughput” are not the same thing, and most of us have spent too long optimizing the wrong one.

Source: https://medium.com/@the_atomic_architect/aws-aurora-dsql-jvm-to-rust-10x-throughput-866810077ffd