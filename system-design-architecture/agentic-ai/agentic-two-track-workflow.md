---
type: System Design
title: "Agentic Two-Track Workflow: Key Takeaways"
description: "Architectural patterns for human-agent collaboration using a spec track (high-attention) paired with an implementation track (low-attention), grounded in Theory of Constraints and Kanban."
generated: { by: process:okf-migrate, at: 2026-06-25T00:00:00Z }
---

# 50. Agentic Two-Track Workflow — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [You don't need ten agents. You need two tracks.](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md) — by Hugo Baraúna (@hugobarauna, Jun 2026)
> **Purpose**: Reusable architectural patterns for structuring human-agent collaboration workflows, identifying bottlenecks, and bounding parallelism correctly.
> **Taxonomy Reference**: §12 AI Applications, §2 Application Software Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [agentic-11](#agentic-11-two-track-workflow--attention-weighted-parallelism) | "10 agents running gives 10x output" | Two-track workflow: pair high-attention with low-attention tracks |
| [agentic-12](#agentic-12-spec-track--human-dense-front-loading) | Agent starts building from vague input | Spec track: externalize tacit knowledge before implementation begins |
| [agentic-13](#agentic-13-spec-creation-is-the-throughput-constraint) | 10 implementation agents waiting for specs | Theory of Constraints applied to agentic pipelines |
| [agentic-14](#agentic-14-non-delegatable-verification-and-ux) | Implementation done but product isn't ready | Verification and UX require irreducible human judgment |
| [agentic-15](#agentic-15-kanban-wip-control-in-agentic-development) | Multiple specs started but none finished | Stop starting, start finishing — bound WIP to one spec at a time |

---

## agentic-11: Two-Track Workflow — Attention-Weighted Parallelism

> **Source**: [The two tracks](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#the-two-tracks)

| | |
|:---|:---|
| **Problem** | Developers run 10 coding agents in parallel assuming more agents = more throughput, but productivity does not scale because human attention is the finite resource |
| **Root cause** | All parallel tracks need the same cognitive intensity if they all require constant human input. You cannot run 10 high-attention tracks in parallel with one human |

**Strategy — Pair tracks by attention demand, not by compute availability**:

```
Spec Track (high-attention):
  Feature idea → agent brainstorm → clarification dialogue
  → PRD (functional spec) → technical design → implementation plan
  [Requires: sustained human focus throughout]

Implementation Track (low-attention):
  Implementation plan → agent executes tasks autonomously
  → periodic review checkpoints
  [Requires: sporadic human attention for review only]

Parallel execution:
  While implementation agent builds Feature N,
  human focuses on spec for Feature N+1.
```

| Track | Attention demand | Parallelism limit | Human role |
|:---|:---|:---|:---|
| Spec | Continuous | 1 at a time | Driver: answers questions, validates design |
| Implementation | Sporadic | Multiple possible (but spec-bounded) | Reviewer: periodic check-ins |

**Tradeoff**: Maximum natural parallelism for a solo developer is 2 tracks (1 spec + 1 implementation) — adding more implementation agents is waste if spec bandwidth is exhausted; adding more spec agents requires additional human attention that doesn't exist.

**Also see**:
- [agentic-13](#agentic-13-spec-creation-is-the-throughput-constraint) — why spec bandwidth caps total throughput
- [Two-Track Agentic Workflow](../../reference-dictionary/ai-ml-llm.md#two-track-agentic-workflow)

---

## agentic-12: Spec Track — Human-Dense Front-Loading

> **Source**: [The spec track](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#the-two-tracks)

| | |
|:---|:---|
| **Problem** | Agent begins implementation from a vague feature description ("build a sponsorship management module") and produces wrong, incomplete, or unrevisionable code |
| **Root cause** | Feature requirements are **tacit knowledge** — they exist in the developer's head as assumptions, constraints, and design opinions that haven't been externalized. Agents cannot infer tacit knowledge from brief prompts |

**Strategy — Iterative dialogue loop to externalize tacit knowledge before any code is written**:

```
Step 1 — Brainstorm (idea → PRD):
  Developer: "Here's my feature idea (2-3 sentences)"
  Agent: asks clarifying questions, reads codebase
  Developer: answers; agent probes further
  Output: PRD (product requirements document)

Step 2 — Technical design (PRD → implementation plan):
  Agent: proposes technical design based on PRD + codebase
  Developer: reviews, asks questions, approves
  Output: implementation plan with engineering tasks
```

**Tradeoff**: Front-loads human time (full attention required upfront) in exchange for agent autonomy in the implementation track. The cost is time-to-first-line-of-code; the benefit is that the implementation track runs with minimal interruptions and produces reviewable, correct output.

**Also see**:
- [agentic-11](#agentic-11-two-track-workflow--attention-weighted-parallelism)
- [Agent Harness](../../reference-dictionary/ai-ml-llm.md#agent-harness) — scaffolding that holds the implementation plan as structured context

---

## agentic-13: Spec Creation Is the Throughput Constraint

> **Source**: [Specs are the first bottleneck](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#why-only-two-agents)

| | |
|:---|:---|
| **Problem** | A team provisions 10 implementation agents expecting 10x throughput, but actual feature delivery rate does not improve proportionally |
| **Root cause** | **Theory of Constraints**: system throughput equals the slowest stage. Spec creation is a serial, human-intensive activity — a single developer can only produce one spec at a time, regardless of how many implementation agents are available |

**Strategy — Identify and optimise the actual bottleneck, not the most visible parallel stage**:

```
Agentic pipeline stages:
  [Spec creation] → [Implementation] → [Verification]
       ↑                                      ↑
  Human serial            Human serial (code review, QA, UX)
  (hard bottleneck)       (hard bottleneck)

  Implementation agents only speed up the middle stage.
  Adding agents when the bottleneck is at spec or verification
  is waste (excess WIP, queuing, coordination overhead).
```

| Scaling lever | Effect on bottleneck | Verdict |
|:---|:---|:---|
| More implementation agents | None — spec creation unchanged | Waste if spec-bounded |
| More humans writing specs | Reduces spec bottleneck | Effective (team, not solo) |
| Better spec tooling | Reduces spec time per feature | Effective |
| Skip spec → vibe coding | Removes bottleneck | Only valid for throwaway code |

**Tradeoff**: Optimising implementation (the non-bottleneck) gives marginal gains; optimising spec quality gives compounding gains because each better spec enables a more autonomous implementation run. The cost is resisting the instinct to add more agents.

**Also see**:
- [agentic-11](#agentic-11-two-track-workflow--attention-weighted-parallelism)
- [agentic-14](#agentic-14-non-delegatable-verification-and-ux)

---

## agentic-14: Non-Delegatable Verification and UX

> **Source**: [Finishing the code isn't finishing the work](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#why-only-two-agents), [You can't delegate UX](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#why-only-two-agents)

| | |
|:---|:---|
| **Problem** | Implementation agent reports "done" but the feature is not shippable — code review, functional testing, and UI iteration still block delivery |
| **Root cause** | Software delivery has three phases: specification, implementation, and verification. Agents can automate implementation. Specification requires externalization of tacit knowledge (see [agentic-12](#agentic-12-spec-track--human-dense-front-loading)). Verification requires subjective human judgment: "Is this a great product?" is an irreducibly opinionated question |

**Strategy — Model verification as a non-parallelisable human phase, not an afterthought**:

```
Delivery pipeline (realistic):
  Spec (human-dense) → Implementation (agent-dense) → Verification (human-dense)
                                                              ↑
                                      Code review + functional QA + UX iteration

  UX loop specifically:
    Agent generates front-end code → Human evaluates feel/flow/product opinion
    → Human iterates → Agent applies changes → Human re-evaluates
    (Cannot be delegated: product quality is subjective and opinionated)
```

**Tradeoff**: Adding more implementation agents accelerates the middle phase, but verification throughput is bounded by human capacity. Designing the workflow without verification time budgeted leads to a hidden queue that cancels out implementation speed gains.

**Also see**:
- [Human Ownership](../../reference-dictionary/ai-ml-llm.md#human-ownership) — assigning named human accountability to each agent-produced output
- [Review Gate](../../reference-dictionary/ai-ml-llm.md#review-gate)
- [agentic-06](agentic-ai/enterprise-strategic-systems.md#agentic-06-human-in-the-decision--ai-as-reasoning-partner)

---

## agentic-15: Kanban WIP Control in Agentic Development

> **Source**: [Evolution, not disruption](../../articles/agentic-ai/You don't need ten agents. You need two tracks..md#evolution-not-disruption)

| | |
|:---|:---|
| **Problem** | Developer starts writing three specs in parallel to "keep agents busy", resulting in none of the specs being finished, no implementation agents starting, and high cognitive overhead |
| **Root cause** | WIP accumulation in the spec stage applies the same failure mode known from Kanban: starting multiple parallel high-attention tasks creates context-switching cost that exceeds the parallelism benefit |

**Strategy — Apply "stop starting, start finishing" to the spec stage**:

```
Anti-pattern (WIP accumulation):
  Spec A (50%) → Spec B (30%) → Spec C (20%)
  ↓ no implementation agents started
  ↓ high context switching when revisiting each spec

Correct (bounded WIP):
  Spec A (100%) → Start Implementation Agent A
                → Begin Spec B (100%) → Start Implementation Agent B
                                      → Begin Spec C ...
```

| WIP level | Spec quality | Implementation starts | Developer cognitive load |
|:---|:---|:---|:---|
| 1 spec at a time | High (sustained focus) | On schedule | Low |
| 2+ specs in parallel | Degraded (split attention) | Delayed | High |

**Tradeoff**: Keeping WIP at 1 spec feels slow when agents are idle, but it maximises spec quality (which is the input quality for the implementation track) and reduces overall cycle time.

**Established basis**: "Stop starting, start finishing" is the core Kanban pull-principle. Theory of Constraints (Goldratt) formalises why optimising a non-bottleneck stage increases WIP without improving throughput. Dual-Track Development (Marty Cagan) is the product management origin of separating discovery (spec) from delivery (implementation).

**Also see**:
- [agentic-13](#agentic-13-spec-creation-is-the-throughput-constraint)
- [Two-Track Agentic Workflow](../../reference-dictionary/ai-ml-llm.md#two-track-agentic-workflow)
