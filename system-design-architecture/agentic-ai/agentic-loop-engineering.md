---
type: System Design
title: "Agentic Loop Engineering — Key Takeaways"
description: "Six reusable patterns for building production agentic loops: loop anatomy, verify gate, maker/checker separation, loop viability test, build order, and cost-per-accepted-change metric."
generated: { by: process:okf-migrate, at: 2026-06-26T00:00:00Z }
---

# 57. Agentic Loop Engineering — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Loops explained: Claude, GPT, Mira and what actually works](../../articles/agentic-ai/loops-explained-claude-gpt-mira-what-actually-works.md) — by @AnatoliKopadze (Jun 2026)
> **Purpose**: Reusable architectural patterns for designing, building, and evaluating agentic loops in AI-assisted workflows.
> **Taxonomy Reference**: §12 AI Applications, §2 Application Software Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [agentic-16](#agentic-16-loop-anatomy--five-phase-self-running-cycle) | AI used one request at a time — human is the engine | Five-phase loop: DISCOVER → PLAN → EXECUTE → VERIFY → ITERATE |
| [agentic-17](#agentic-17-verify-gate--the-heart-of-the-loop) | Loop without a check = agent agreeing with itself | Hard gate: deterministic test, measurable condition, or rubric score |
| [agentic-18](#agentic-18-makerchecker-sub-agent-separation) | The model that produced work is too generous grading it | Split maker (cheap/fast) from checker (strict/strong) |
| [agentic-19](#agentic-19-loop-viability-test--four-conditions) | Loop setup cost never pays back | Build only when all 4 conditions hold |
| [agentic-20](#agentic-20-loop-build-order--prove-before-scheduling) | Scheduling unproven loops causes runaway billing | manual → skill → loop+gate → schedule |
| [agentic-21](#agentic-21-cost-per-accepted-change--the-loop-efficiency-metric) | Loops tracked by tokens but not accepted results | Track cost per accepted change; below 50% accept rate costs more than it saves |

---

## agentic-16: Loop Anatomy — Five-Phase Self-Running Cycle

| | |
|:---|:---|
| **Problem** | AI used one request at a time: every step requires a human decision, and work stops the moment the human stops |
| **Root cause** | No mechanism for the AI to evaluate its own output and continue without human intervention |

**Strategy**: Hand the AI a *goal* rather than an *instruction*. A real loop runs five phases without human involvement:

```
DISCOVER  →  work out what needs doing
PLAN      →  decide how to do it
EXECUTE   →  do the work
VERIFY    →  check it against the goal
ITERATE   →  not done yet? feed result back and repeat
```

Three phases do all the real work — Verify, State, and the Stop Condition. Verify turns repetition into progress. State prevents repeating the same mistake forever. The stop condition prevents a runaway that drains your account.

**Tradeoff**: Every pass re-reads the full accumulated context. A loop of 10 iterations does not cost 10 equal prompts — it costs 10 prompts each growing larger than the last. A fleet of parallel agents multiplies this cost further.

**Related files**:
- [agentic-11 Two-Track Workflow](agentic-ai/agentic-two-track-workflow.md#agentic-11-two-track-workflow--attention-weighted-parallelism) — the human-level attention model for running loops alongside spec work
- [agentic-ai/agent-harness.md](agentic-ai/agent-harness.md) — the five building blocks (automation, skill, sub-agents, connectors, verifier) that implement a production loop

**Dictionary terms**:
- [Agent Loop](../../reference-dictionary/ai-ml-llm.md#agent-loop)
- [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai)
- [Verification Loop (AI)](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai)

---

## agentic-17: Verify Gate — The Heart of the Loop

| | |
|:---|:---|
| **Problem** | A loop without a real check on the output does not produce progress — the agent agrees with itself on repeat |
| **Root cause** | The same model that generated the output evaluates it; self-evaluation is systematically over-generous |

**Strategy**: Every loop must have a hard gate with objective pass/fail semantics. Choose in order of preference:

1. **Deterministic gate** — test suite passes, type checker clean, linter clean, build succeeds
2. **Measurable condition** — a specific metric crosses a defined threshold
3. **Rubric score** — the model scores each criterion (must hit ≥ 8/10 on all to pass)

Without one of these, the loop exits on the first result that looks plausible, not the first result that actually meets the goal.

**Tradeoff**: No gate → silent billing with no progress. An LLM-as-judge gate adds token cost per iteration but catches semantic issues that deterministic checks miss. Rubric scoring is the weakest option because the grading model can be gamed by superficially polished output.

**Related files**:
- [agentic-ai/agent-harness.md](agentic-ai/agent-harness.md) — `harness-06`: verification loops improve output quality 2–3×
- [resilience/circuit-breaker-honesty.md](resilience/circuit-breaker-honesty.md) — same core principle: a gate that stops the bad path early rather than letting it compound

**Dictionary terms**:
- [Verification Loop (AI)](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai)
- [LLM-as-Judge](../../reference-dictionary/ai-ml-llm.md#llm-as-judge)
- [Review Gate](../../reference-dictionary/ai-ml-llm.md#review-gate)
- [Premature Loop Exit](../../reference-dictionary/ai-ml-llm.md#premature-loop-exit)

---

## agentic-18: Maker/Checker Sub-agent Separation

| | |
|:---|:---|
| **Problem** | Single-agent loops only catch surface-level mistakes; the model that produced the work is too generous grading its own output |
| **Root cause** | Self-critique is structurally weak — the agent is motivated to confirm its own correctness and has no independent perspective |

**Strategy**: Split the loop into two sub-agents:
- **Maker** (cheap, fast model) — produces the work
- **Checker** (stronger model, stricter instructions) — reviews independently

The maker never sees the checker's rubric. The checker never participates in production. On higher-effort runs, the checker uses a larger model; on lower-effort runs, a smaller model with a strict rubric suffices.

**Tradeoff**: Doubles token cost because two models process the same context on each iteration. Justified when quality is the bottleneck and reject rate would otherwise be high. Not justified for high-volume, low-stakes work where accept rate is already above 80%.

**Related files**:
- [agentic-11 Two-Track Workflow](agentic-ai/agentic-two-track-workflow.md#agentic-11-two-track-workflow--attention-weighted-parallelism) — same principle at the human level: separate the specifier from the implementer
- [agentic-ai/agent-harness.md](agentic-ai/agent-harness.md) — `harness-06` verification loops and `harness-01` three-level engineering

**Dictionary terms**:
- [LLM-as-Judge](../../reference-dictionary/ai-ml-llm.md#llm-as-judge)
- [Verification Loop (AI)](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai)
- [Agent Harness](../../reference-dictionary/ai-ml-llm.md#agent-harness)

---

## agentic-19: Loop Viability Test — Four Conditions

| | |
|:---|:---|
| **Problem** | Loops built for unsuitable tasks never pay back their setup cost; a good manual prompt would have been faster and cheaper |
| **Root cause** | Loops are compelling in demos but most tasks lack the structural properties that make automation compound positively |

**Strategy**: Build a loop **only when all four conditions hold**:

| Condition | Threshold | If Not Met |
|:---|:---|:---|
| **Task repeats** | At least weekly | Setup cost never pays back → manual prompt |
| **Auto-reject exists** | Test, type check, build, or hard rule | Loop just spins → manual prompt |
| **Agent can do it end-to-end** | No mid-task hand-off to a human | Human still in the critical path → manual prompt |
| **"Done" is objective** | Not a matter of taste or judgment | Human reviewer wins → manual prompt |

Missing **one** condition means keeping it as a manual prompt. All four must hold for a loop to be worthwhile.

**Tradeoff**: Honest application of this test eliminates most candidates. The gain is avoiding the class of loops that run indefinitely, produce low-accept-rate output, and drain token budgets before anyone notices.

**Related files**:
- [agentic-13 Spec Creation Is the Throughput Constraint](agentic-ai/agentic-two-track-workflow.md#agentic-13-spec-creation-is-the-throughput-constraint) — loops are bounded by their weakest condition; identify the bottleneck first
- [agentic-ai/ai-agent-architecture.md](agentic-ai/ai-agent-architecture.md) — full agent architecture that underpins whether condition 3 (end-to-end capability) is met

**Dictionary terms**:
- [Loop Viability Test](../../reference-dictionary/ai-ml-llm.md#loop-viability-test)
- [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai)
- [Agent Loop](../../reference-dictionary/ai-ml-llm.md#agent-loop)

---

## agentic-20: Loop Build Order — Prove Before Scheduling

| | |
|:---|:---|
| **Problem** | Scheduling an unproven loop creates a machine that runs, bills, and fails silently while you are not watching |
| **Root cause** | A schedule adds a trigger and cadence but does not improve reliability; unreliable work run on a schedule is still unreliable, now at scale and cost |

**Strategy**: Build in strict sequence — never skip a step:

```
1. Manual run   — prove the task works reliably at least once by hand
2. Skill        — save the instructions as a reusable file the loop reads every run
3. Loop         — add the verify gate and the hard stop condition
4. Schedule     — only after steps 1–3 are solid
```

**Tradeoff**: Longer path to full automation. The payoff is avoiding the **premature loop exit** failure mode: the loop schedules, runs undetected, exits early without completing work, and bills for nothing — sometimes hundreds of iterations before anyone checks.

**Related files**:
- [agentic-17](#agentic-17-verify-gate--the-heart-of-the-loop) — the gate that makes step 3 real
- [agentic-ai/agent-harness.md](agentic-ai/agent-harness.md) — `harness-01` three-level engineering follows the same staged reliability-before-automation approach

**Dictionary terms**:
- [Loop Build Order](../../reference-dictionary/ai-ml-llm.md#loop-build-order)
- [Premature Loop Exit](../../reference-dictionary/ai-ml-llm.md#premature-loop-exit)
- [Agent Harness](../../reference-dictionary/ai-ml-llm.md#agent-harness)

---

## agentic-21: Cost Per Accepted Change — The Loop Efficiency Metric

| | |
|:---|:---|
| **Problem** | Teams track token spend and loop count but cannot tell whether the loop is actually useful — only that it ran |
| **Root cause** | Token spend measures activity, not value. A loop that generates 10 results and 6 are discarded spent 60% of its budget on waste |

**Strategy**: Instrument every production loop with **cost per accepted change** — the total token cost of all iterations divided by the count of results that passed review and were kept.

```
cost per accepted change = total_tokens_spent / accepted_results_count
```

Target threshold: keep accept rate above **50%**. Below that threshold, the loop costs more in token spend and human review time than it saves. Above that threshold, the loop delivers compounding returns.

**Tradeoff**: Measuring this requires a result-auditing step that the loop does not provide automatically. Someone must mark results as accepted or rejected after each run — low overhead for small-volume loops, meaningful overhead for high-frequency automation. The alternative (tracking only token spend) creates the illusion of productivity.

**Related files**:
- [agentic-17](#agentic-17-verify-gate--the-heart-of-the-loop) — a strong verify gate raises the accept rate by catching bad work before human review
- [agentic-18](#agentic-18-makerchecker-sub-agent-separation) — maker/checker raises quality at the cost of doubling per-iteration token spend; justified only if it raises the accept rate proportionally

**Dictionary terms**:
- [Cost Per Accepted Change](../../reference-dictionary/ai-ml-llm.md#cost-per-accepted-change)
- [Token](../../reference-dictionary/ai-ml-llm.md#token)
- [Verification Loop (AI)](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai)
