---
type: Article
title: "Torvalds Said Rust Doesn't Fix Logic Errors. Six Months Into My Own Rust Migration, I Think He's Right"
source: "https://medium.com/@the_atomic_architect/torvalds-rust-logic-errors-6d2a45451ca7"
author:
  - "[[The Atomic Architect]]"
published: 2026-07-16
created: 2026-07-18
description: "A Rust migration post-mortem showing where compiler guarantees stop: memory safety improves, but wildcard match arms and defaults can still hide business-logic failures."
tags:
  - "performance"
  - "rust"
  - "logic-errors"
  - "type-safety"
  - "clippings"
---

# Torvalds Said Rust Doesn't Fix Logic Errors. Six Months Into My Own Rust Migration, I Think He's Right

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*H5gLSMcULfHVHpDPVXUF9A.png)

I watched the clip from Open Source Summit India three times before I let myself agree with it, because agreeing with it meant giving something up. Someone asked Torvalds the obvious fan question, the one every Rust convert wants answered a certain way. Doesn't Rust just make the kernel better, full stop, end of discussion. He didn't say no, which would have been easy to argue with. He said something narrower and far more uncomfortable to sit with. Rust fixes a category of bugs. It does not fix you.

The line that actually stayed with me was blunt in a way I wasn't ready for. Rust, in his words, does not think for you. Bad logic written in a memory-safe language is still bad logic, it's just wrapped in a compiler that trusts your intentions more than it questions your reasoning. Six months ago I would have argued with that sentence in the comments of whatever post carried it. I had just finished migrating an authorization service from Python to Rust, and I was still riding the high of watching the borrow checker catch things Python would have shipped straight into production without blinking.

Now I have a different bug living in my head, and it's a more uncomfortable one, because it showed up after the migration had already been declared a win by everyone including me.

## The Bug Rust Actually Killed, No Argument

I want to give Rust its full due before I take anything away from it, because what follows isn't an exaggeration built to make a better story. The old Python service had a simple, almost boring shape. A request came in, we looked up the user's tier, fetched a policy tied to that tier, and evaluated whether the action was allowed. It looked like nothing. It looked like the kind of code nobody reviews twice.

```python
policy = policies.get(user.tier)
decision = evaluate(policy, req.resource, req.action)
```

For most users, across most of two years, this worked without complaint. For one narrow class of freshly migrated accounts, `user.tier` could quietly come back as `None`, and `policies.get(None)` returned `None` right back without so much as a warning. `evaluate` then walked into a branch nobody had written a test for, because nobody had imagined a policy that didn't exist being handed to a function that assumed it always would. That bug was completely legal Python. It compiled by definition, because Python checks syntax, not intent, and it ran fine for a long stretch of production traffic right up until the exact account that finally triggered it.

Rewriting that lookup in Rust made the entire bug class structurally impossible, and not through discipline, willpower, or a stricter code review process. It happened through the type signature itself refusing to let the gap exist.

```rust
fn policy_for(tier: Option<Tier>) -> Policy {
    match tier {
        Some(t) => lookup(t),
        None => Policy::default_safe(),
    }
}
```

You cannot forget the missing case here even if you wanted to, because the compiler will not build the function without an arm for it. That is a real, structural, undeniable win, and I will defend it against anyone who wants to tell me the rewrite was pointless hype chasing. If this were the whole story, Torvalds would be wrong and I'd have a very different article to write.

## The Bug Rust Let Straight Through the Front Door

Here is the one Torvalds would recognize immediately, because it isn't a memory bug at all, and it isn't even a Rust-specific mistake. It's a decision dressed up as code, one that nobody in the room ever flagged as a decision at the moment it was made. Four months after the rewrite shipped and everyone had moved on to the next project, we added a new customer tier. Nothing dramatic on paper, just a new kind of account with its own set of policy rules that product had been asking for.

The match arm handling tiers had looked, up until that point, roughly like this, written by someone reasoning carefully about exactly two tiers because that was the entire universe at the time.

```rust
fn policy_for(tier: &Tier) -> Policy {
    match tier {
        Tier::Free => Policy::restricted(),
        Tier::Pro => Policy::standard(),
        _ => Policy::standard(),
    }
}
```

Nobody revisited that wildcard arm in the months between writing it and the new tier landing, because the compiler had absolutely nothing left to say about it. It was green. It was approved. It looked exactly as correct as every other line around it. When `Tier::Partner` landed, this function compiled without a single warning, and every partner account silently received the standard policy instead of the one the product team had specifically designed for them. Nothing crashed. Nobody got paged. It just quietly did the wrong thing, with the compiler's full blessing, for weeks before a support ticket surfaced it. The borrow checker had nothing to say. The type checker had nothing to say. A business rule had walked in wearing the compiler's approval as a disguise, and the disguise worked perfectly.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*vY8KHBoAY-hO9TXgbz6m9w.png)

## Where the Compiler's Job Actually Stops

I keep coming back to a rough dividing line, and it's not one I'd have accepted from myself a year ago, back when I still talked about Rust the way people talk about a diet that finally worked.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*RX7eWrN5nqTurl8zcT3wCQ.png)

```text
+---------------------------------------------------------+
|                WHAT THE COMPILER GUARDS                  |
|   use-after-free   data races   dangling pointers        |
|   null derefs   buffer overruns   unsynchronized state   |
+---------------------------------------------------------+
                           |
                           |   this is where the guarantee stops
                           v
+---------------------------------------------------------+
|                 WHAT ONLY YOU GUARD                       |
|   is this the right policy for this case                 |
|   did we handle the new variant on purpose                |
|   does this default still make sense months later         |
+---------------------------------------------------------+
```

The wildcard arm sits squarely inside that second box, and no version of Rust, no lint, no clippy warning was ever going to move it into the first one. It was a perfectly legal decision by every rule the compiler enforces, and it happened to be the wrong business decision, and the language had no stake in that distinction whatsoever. What would have caught it wasn't Rust as a general concept. It was Rust used one specific way, with the escape hatch removed on purpose.

```rust
fn policy_for(tier: &Tier) -> Policy {
    match tier {
        Tier::Free => Policy::restricted(),
        Tier::Pro => Policy::standard(),
        Tier::Enterprise => Policy::standard(),
    }
}
```

Drop the wildcard, and the day someone adds `Tier::Partner`, this exact function refuses to compile until an actual human looks at it and consciously decides what a partner account deserves. That's the entire trick, and it's a smaller trick than most Rust marketing lets on. Exhaustiveness checking only protects you the moment you stop handing yourself a way around it, and most teams, mine included, hand themselves that way around it constantly without noticing.

## Why This Argument Is Bigger Than the Kernel

Torvalds was talking specifically about mixed C and Rust codebases, where the guarantees only apply inside the Rust boundary and evaporate completely the second you cross into C. That's a narrow, specific, kernel-shaped problem. But he's made a second point recently that lands from a different angle and hits the same nerve. He drew a hard line that a Rust panic inside the kernel is simply not acceptable, no exceptions carved out for the usual fail-fast argument that Rust developers lean on everywhere else.

Sit with that for a second, because it's the part people skip past. Panic is Rust's own built-in safety valve for exactly the kind of situation my wildcard arm created, an unhandled case the type system never saw coming and never could have. Even that valve had to be restricted by human policy, because an unhandled panic in production looks identical to a bug from the perspective of whoever gets the alert. You cannot fully outsource judgment to the language's own escape hatches either, not even the escape hatches the language ships specifically to catch you.

A memory-safe language changes which mistakes become structurally impossible to make. It says absolutely nothing about which mistakes are merely unlikely, unreviewed, quietly convenient, or comfortable enough to leave alone for eight months until someone adds a new enum variant.

## What Actually Changed for Me, and What I'd Say to the Rust Crowd

I didn't come out of this thinking the migration was a mistake, and I'm not writing this to hand ammunition to anyone still defending a legacy service out of habit. The rewritten service is faster, it runs on a fraction of the memory it used to need, and an entire category of production incidents genuinely cannot happen anymore. I'd make the same call again tomorrow with the same information. What changed is quieter and harder to put in a benchmark table. I stopped crediting the language for judgment calls that were always, only, mine to make.

Every wildcard arm, every `unwrap_or_default`, every catch-all pattern is a spot where I am actively choosing to stop thinking and asking the compiler to stop thinking there too. The compiler will agree instantly and without complaint, because it was never built to have an opinion on whether that was the right moment to stop. If you've ever felt a little superior watching a team ship a null-pointer bug in a language you consider beneath yours, I'd ask you to go find the nearest wildcard match arm in your own Rust codebase before you finish that thought.

Torvalds has spent three decades watching extremely careful engineers ship extremely careful logic errors, in every language he's ever maintained code in, C included, and now Rust too. I think that's exactly why the line landed the way it did for me. It wasn't a takedown of Rust dressed up as kernel gossip. It was a plain description of every language that has ever existed, including the one I had just spent six months publicly proving myself right about.

So here's the question I genuinely don't have a comfortable answer to yet, and I'd rather ask it than pretend I do. How many wildcard arms are sitting in your own codebase right now, fully compiled, fully green, sitting quietly under a passing test suite, waiting for the one input nobody thought to name out loud.
