---
type: System Design
title: "Agentic AI — Key Takeaways"
description: "Production agentic engineering requires explicit verification, context architecture, harness design, and human ownership."
timestamp: 2026-09-06T00:00:00Z
---

# 29. Agentic AI — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [Google’s New SDLC Guide Draws a Hard Line Between Vibe Coding and Agentic Engineering](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md)
> **Dictionary**: [AI/ML, LLM & Agentic AI](../reference-dictionary/ai-ml-llm.md)
> **Taxonomy Reference**: §12.1 AI Application Patterns

## Contents

| ID | Problem | Key concept |
|:---|:---|:---|
| [agentic-55](#agentic-55-verification-is-the-boundary-between-prototyping-and-engineering) | AI-generated changes look correct but are weakly verified | Verification as an architectural boundary |
| [agentic-56](#agentic-56-production-correctness-exceeds-prototype-correctness) | Prototype workflows are applied to high-stakes production code | Separate speed goals from correctness goals |
| [agentic-57](#agentic-57-output-correctness-does-not-prove-process-correctness) | Passing outputs can hide flawed reasoning paths | Combine deterministic and trajectory evaluation |
| [agentic-58](#agentic-58-the-harness-controls-agent-behavior) | Teams blame the model for failures caused by its runtime | Treat the harness as the product surface |
| [agentic-59](#agentic-59-context-is-a-versioned-system-design-decision) | Irrelevant context dilutes instructions and raises cost | Govern static and dynamic context |
| [agentic-60](#agentic-60-load-specialized-knowledge-on-demand) | Large universal prompts become noisy and expensive | Package procedural knowledge as skills |
| [agentic-61](#agentic-61-human-attention-belongs-at-the-80-20-boundary) | Agents handle common cases while missing system-specific edge cases | Reserve human judgment for ambiguity and boundaries |
| [agentic-62](#agentic-62-orchestration-requires-a-different-control-model) | Line-by-line supervision caps agent throughput | Move from conductor to orchestrator with evidence |
| [agentic-63](#agentic-63-agentic-engineering-trades-capex-for-lower-marginal-cost) | Fast experimentation accumulates hidden rework and operations debt | Invest before debt compounds |
| [agentic-64](#agentic-64-specification-and-feedback-loops-make-autonomy-governable) | Delegation without constraints scales failure rather than delivery | Use specifications, tests, and feedback loops as controls |

## agentic-55: Verification is the boundary between prototyping and engineering

> **Source**: [Verification boundary](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#the-spectrum-where-are-you-actually-operating)

| | |
|:---|:---|
| **Problem** | Prompt-and-accept workflows can produce fluent code without proving that it is correct. |
| **Key Concept** | Verification is the boundary between vibe coding and agentic engineering, independent of model choice. |

**Strategy**: Make tests, evaluation, and review explicit stages in every production agent workflow.

**Tradeoff**: Verification adds latency and implementation cost, but converts invisible failures into observable decisions.

**Cross-reference**: [Verification Loop (AI)](../reference-dictionary/ai-ml-llm.md#verification-loop-ai) · [Agent Harness](agent-harness.md)

## agentic-56: Production correctness exceeds prototype correctness

> **Source**: [Production risk](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#why-vibe-coding-isnt-enough-anymore)

| | |
|:---|:---|
| **Problem** | A workflow optimized to get prototypes running quickly is reused for payment, identity, healthcare, and data systems. |
| **Key Concept** | Prototype velocity and production correctness are different optimization targets. |

**Strategy**: Classify work by risk and require stronger specifications, tests, and review gates as impact increases.

**Tradeoff**: Risk-based controls slow low-risk work when applied too broadly, so teams need an explicit threshold rather than one process for everything.

**Cross-reference**: [Review Gate](../reference-dictionary/ai-ml-llm.md#review-gate) · [Accountability Gap](agentic-accountability.md)

## agentic-57: Output correctness does not prove process correctness

> **Source**: [Evaluation spectrum](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#the-spectrum-where-are-you-actually-operating)

| | |
|:---|:---|
| **Problem** | A correct result can be reached through an unsafe or accidental sequence of actions. |
| **Key Concept** | Production evaluation needs deterministic output checks and trajectory checks on the agent’s path. |

**Strategy**: Test final artifacts while recording and evaluating tool calls, assumptions, and intermediate decisions.

**Tradeoff**: Trajectory evaluation improves diagnosability but increases telemetry volume, rubric design effort, and evaluation cost.

**Cross-reference**: [Agent Tracing](../reference-dictionary/ai-ml-llm.md#agent-tracing) · [Evidence-Based Stopping](../reference-dictionary/ai-ml-llm.md#evidence-based-stopping)

## agentic-58: The harness controls agent behavior

> **Source**: [Agent = Model + Harness](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#agent-model-harness)

| | |
|:---|:---|
| **Problem** | Model upgrades are used to address failures caused by missing tools, weak context, absent guardrails, or poor execution policy. |
| **Key Concept** | The agent is the model plus the surrounding harness: tools, context, memory, sandboxes, orchestration, and observability. |

**Strategy**: Diagnose the harness before changing the model, and measure harness changes independently.

**Tradeoff**: A stronger harness improves reliability but becomes an operational system that must be maintained and tested.

**Cross-reference**: [Agent Harness](../reference-dictionary/ai-ml-llm.md#agent-harness) · [Agent Harness](agent-harness.md)

## agentic-59: Context is a versioned system-design decision

> **Source**: [Context Engineering](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#context-engineering-the-real-competitive-moat)

| | |
|:---|:---|
| **Problem** | Loading every instruction and document into every request wastes tokens and buries high-signal information. |
| **Key Concept** | The static-versus-dynamic context split is an architectural policy, not prompt configuration. |

**Strategy**: Keep stable constraints small and retrieve task-specific knowledge on demand; version and review the policy.

**Tradeoff**: Dynamic retrieval reduces noise and cost but introduces retrieval misses, freshness concerns, and more runtime behavior to observe.

**Cross-reference**: [Context Engineering](../reference-dictionary/ai-ml-llm.md#context-engineering) · [Context Governor](../reference-dictionary/ai-ml-llm.md#context-governor)

## agentic-60: Load specialized knowledge on demand

> **Source**: [Agent Skills](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#context-engineering-the-real-competitive-moat)

| | |
|:---|:---|
| **Problem** | A universal system prompt cannot contain every domain rule without becoming costly and noisy. |
| **Key Concept** | Skills package procedural knowledge and load it only when task matching requires it. |

**Strategy**: Define skills with explicit triggers, constraints, examples, and verification expectations.

**Tradeoff**: On-demand specialization keeps the base context lean but makes trigger coverage and skill versioning part of correctness.

**Cross-reference**: [Context Engineering](../reference-dictionary/ai-ml-llm.md#context-engineering) · [Workflow Files](../reference-dictionary/ai-ml-llm.md#workflow-files)

## agentic-61: Human attention belongs at the 80/20 boundary

> **Source**: [The 80% Problem](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#the-80-problem-why-speed-is-the-trap)

| | |
|:---|:---|
| **Problem** | Agents generate common-case code quickly but miss implicit business rules, edge cases, and cross-service contracts. |
| **Key Concept** | Human review should concentrate on ambiguity, architecture, and system boundaries rather than rechecking every generated line equally. |

**Strategy**: Make institutional knowledge explicit and route high-uncertainty changes through targeted human review and evaluation.

**Tradeoff**: Focused review increases leverage, but requires accurate risk classification and does not eliminate the need for baseline automated checks.

**Cross-reference**: [Human Ownership](../reference-dictionary/ai-ml-llm.md#human-ownership) · [Accountability Gap](agentic-accountability.md)

## agentic-62: Orchestration requires a different control model

> **Source**: [Conductor and orchestrator modes](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#conductor-or-orchestrator-the-role-transition-that-is-already-happening)

| | |
|:---|:---|
| **Problem** | A developer who personally directs every interaction cannot scale parallel agent work. |
| **Key Concept** | Orchestrator mode replaces continuous supervision with precise goals, decomposition, asynchronous execution, and evidence-based review. |

**Strategy**: Move work into isolated sandboxes and pull request outputs only after harness checks and evaluation complete.

**Tradeoff**: Throughput rises, but developers lose immediate visibility and need stronger observability, ownership, and rollback mechanisms.

**Cross-reference**: [Agent Sandboxing](../reference-dictionary/ai-ml-llm.md#agent-sandboxing) · [Multi-Agent Coordination Patterns](../reference-dictionary/ai-ml-llm.md#multi-agent-coordination-patterns)

## agentic-63: Agentic engineering trades CapEx for lower marginal cost

> **Source**: [Agentic engineering economics](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#the-economics-no-one-is-talking-about-plainly)

| | |
|:---|:---|
| **Problem** | Unstructured speed avoids upfront investment but accumulates token waste, debugging, and rework. |
| **Key Concept** | Agentic engineering front-loads specification, harness, context, and evaluation infrastructure to reduce the cost of accepted changes later. |

**Strategy**: Estimate the crossover point where recurring rework exceeds the cost of building shared controls, then invest before that point.

**Tradeoff**: The infrastructure pays back only at sufficient scale; prototypes and low-stakes work may rationally remain lightweight.

**Cross-reference**: [Cost Per Accepted Change](../reference-dictionary/ai-ml-llm.md#cost-per-accepted-change) · [Technical Deflation](../reference-dictionary/ai-ml-llm.md#technical-deflation)

## agentic-64: Specification and feedback loops make autonomy governable

> **Source**: [What this means going forward](../articles/agentic-ai/google-new-sdlc-guide-vibe-coding-agentic-engineering.md#what-this-means-going-forward)

| | |
|:---|:---|
| **Problem** | Delegating work without constraints scales unobserved failure instead of reliable delivery. |
| **Key Concept** | Autonomy is governable when goals, boundaries, tests, feedback, and human ownership are explicit. |

**Strategy**: Treat specifications, harness policies, verification loops, and review gates as the control plane for agent execution.

**Tradeoff**: More structure limits improvisation and requires maintenance, but it makes behavior repeatable enough to improve systematically.

**Cross-reference**: [Loop Contract](../reference-dictionary/ai-ml-llm.md#loop-contract) · [Review Gate](../reference-dictionary/ai-ml-llm.md#review-gate) · [Agentic Loop Engineering](agentic-loop-engineering.md)
