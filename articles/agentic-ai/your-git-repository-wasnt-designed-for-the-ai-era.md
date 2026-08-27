---
type: Article
title: "Your Git Repository Wasn’t Designed for the AI Era"
description: "Why traditional Git hosting architectures with application-level replication break under AI coding agent workloads (high push volume, disposable repo proliferation, read concurrency spikes), and how log-first architectures using object storage WALs solve these scalability limits."
source: "https://medium.com/@kanishks772/your-git-repository-wasnt-designed-for-the-ai-era-bed59063d3bf"
author: "The Latency Gambler"
published: 2026-08-22
timestamp: 2026-08-26T00:00:00Z
tags:
  - "clippings"
  - "git"
  - "agentic-ai"
  - "system-design"
  - "distributed-systems"
  - "storage-architecture"
---

# Your Git Repository Wasn’t Designed for the AI Era

> **Source**: [Medium — The Latency Gambler](https://medium.com/@kanishks772/your-git-repository-wasnt-designed-for-the-ai-era-bed59063d3bf)  
> **Reference Blog**: [Cursor Blog — Git at any scale (Vicent Martí)](https://cursor.com/blog/git-at-any-scale)  
> **Key Takeaways**: [39. Git Repository Infrastructure for the AI Agent Era](../../system-design-architecture/agentic-ai/39-agentic-key-takeaways.md)  
> **Dictionary**: [Log-First Storage Architecture](../../reference-dictionary/architecture-patterns.md#log-first-storage-architecture), [Application-Level Replication](../../reference-dictionary/architecture-patterns.md#application-level-replication), [Disposable Repositories](../../reference-dictionary/ai-ml-llm.md#disposable-repositories)

Git turns 21 this year, and for most of its life it worked exactly the way it was supposed to: a handful of humans, each opening a handful of branches, pushing a handful of times a day. Then coding agents showed up, and the assumptions baked into Git’s design 20 years ago started to crack.

This isn’t a knock on Git the tool. It’s about what happens when the *usage pattern* around a distributed version control system changes faster than the infrastructure hosting it does.

![Abstract illustration depicting human developers and automated AI coding agents interacting with cloud-based version control infrastructure](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*PHtNd367bEekAhro6SzXWA.png)

## Git Was Built for a Very Different Workload

Git was designed to manage the Linux kernel: a decentralized project with many independent maintainers, each working offline for stretches, syncing occasionally. That shaped everything underneath it: repositories are self-contained, every clone is a full copy of history, and the storage format (packfiles: compressed, delta-encoded blobs of commits, trees, and file contents) was optimized for a single machine’s disk, not a data center.

Hosting Git at company scale—GitHub, GitLab, and everyone after them—has always meant working *around* that design, not with it. The core problem: a Git repository’s data is a directed acyclic graph (DAG). To do almost anything (list commits, diff two trees, fetch a file) you have to walk that graph pointer by pointer. You can’t jump straight to what you need; each step tells you where the next one is.

```python
# Simplified: why you can't just "look up" a file at a commit
def walk_to_file(commit_sha, path):
    commit = fetch_object(commit_sha)      # round-trip 1
    tree = fetch_object(commit.tree_sha)   # round-trip 2
    for part in path.split("/"):
        entry = tree.find(part)
        tree = fetch_object(entry.sha)     # round-trip N
    return tree  # now a blob
```

On a laptop, with everything on local disk, this is instant. Distribute those objects across a network or a cluster of machines, and every one of those round trips adds latency. Multiply that by thousands of repositories and you have the entire history of why Git hosting infrastructure is hard.

## What Agents Change

None of this was fatal when the number of repositories and the rate of pushes stayed within human bounds. Coding agents break both assumptions at once:

- **Push volume goes up**: An agent iterating on a task can push far more often than a person typing code by hand.
- **Repository count explodes**: Agents frequently spin up small, disposable repositories for a sandboxed experiment, a throwaway branch, a one-off fix—most of which are touched once and abandoned.
- **Read concurrency spikes**: CI pipelines, review agents, and background jobs all want a consistent view of the same commit, often within seconds of it landing.

Most production Git hosting today handles this with **application-level replication**: keep a small number of full copies of each repository (often three) on fast local disks across different machines, and use a consensus protocol to make sure a push is only accepted once a majority of copies agree they have it.

```text
PUSH ──▶         ┌─────────────┐
                 │ Coordinator │
                 └──────┬──────┘
                         │ fan out packfile
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
     ┌─────────┐   ┌─────────┐   ┌─────────┐
     │ Replica │   │ Replica │   │ Replica │
     │    A    │   │    B    │   │    C    │
     └─────────┘   └─────────┘   └─────────┘
           │             │             │
           └─────────────┴─────────────┘
                  majority ack required
                  before push succeeds
```

This works, but it has a fixed floor and a low ceiling. Every repository—even one an agent created for a five-minute experiment—needs its full quota of replicas, or the system can’t guarantee consistency. Scale the replica count up to handle a busy monorepo’s CI traffic, and the consensus protocol itself gets slower, because every step waits on the slowest machine in the group. You end up paying a tax on both ends: idle repositories that cost as much to keep consistent as busy ones, and busy repositories that can’t scale past what the consensus protocol tolerates.

## A Different Shape: Log First, Filesystem Second

The alternative several newer systems are converging on flips the source of truth. Instead of the on-disk copies being authoritative and requiring a live protocol to keep them agreeing, a write-ahead log (WAL) in object storage (S3-compatible or similar) becomes the one true record. A push isn’t acknowledged until it’s durably written to that log. Everything else—the local, fast, on-disk Git repository that actually serves clones and fetches—becomes a disposable cache that can be rebuilt from the log at any time.

```text
git push
      │
      ▼
┌───────────────┐        ┌──────────────────────┐
│ Local NVMe    │──────▶│ Write-ahead log       │
│ (fast reads,  │  also  │ in object storage    │
│  disposable)  │  write │ (durable source of   │
└───────────────┘        │truth, cheap to scale)│
      ▲                  └──────────────────────┘
      │ rebuild on demand         │
      └───────────────────────────┘
        replicas materialize from the log,
        not from each other
```

The practical upside: a repository that’s barely used doesn’t need three permanently warm copies sitting around—it can be rebuilt from the log the moment someone fetches it. A repository under heavy CI load can be replicated far more widely than a fixed-quorum design would tolerate, because reads don’t need a live consensus round trip; they just need to check whether their local cache is behind the log. Consistency comes from the log being the single source of truth, not from every copy staying in lockstep in real time.

## The Takeaway

None of this means Git itself needs replacing: the client, the object model, the workflow developers already know all still hold up. What’s changing is the hosting layer underneath it, because the traffic pattern it was quietly optimized for—a bounded number of humans, pushing at human speed—no longer describes how a lot of code gets written. Infrastructure tuned for that old pattern doesn’t fail loudly; it just gets slower and more expensive exactly as agentic workflows push repository counts and push volumes upward.

---

*This article discusses concepts and architecture patterns described in Cursor’s engineering blog post, “Git at any scale” by Vicent Martí:* [*https://cursor.com/blog/git-at-any-scale*](https://cursor.com/blog/git-at-any-scale)
