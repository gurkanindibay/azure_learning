---
type: System Design
title: "AI Agent Architecture — Key Takeaways"
description: "Graph engineering patterns for multi-agent coordination: progression from prompts to graphs, maker-checker validation, parallel factor fanout, and multi-model tier architecture."
timestamp: 2026-08-06T00:00:00Z
---

# 36. AI Agent Architecture — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [How to Use Graph Engineering to Build a Multi-Factor Alpha Model](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md)
> **Also see**: [AI Agent Architecture — Core Patterns](ai-agent-architecture.md), [Agent Harness](agent-harness.md), [Agentic Loop Engineering](agentic-loop-engineering.md)
> **Dictionary**: [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai), [Agent Loop](../../reference-dictionary/ai-ml-llm.md#agent-loop), [Verification Loop](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai), [LLM-as-Judge](../../reference-dictionary/ai-ml-llm.md#llm-as-judge)
> **Taxonomy Reference**: §12 AI Applications

---

## Contents

- [agentarch-07: Graph Engineering — Agent Coordination as a Graph](#agentarch-07-graph-engineering--agent-coordination-as-a-graph) — Prompts → Loops → Swarms → Graphs
- [agentarch-08: Maker-Checker Pattern — Separate Generation from Validation](#agentarch-08-maker-checker-pattern--separate-generation-from-validation) — Maker never validates maker's own work
- [agentarch-09: Parallel Agent Fanout with Sequential Coordination](#agentarch-09-parallel-agent-fanout-with-sequential-coordination) — Seven factor agents in parallel → four coordination nodes in sequence
- [agentarch-10: Node-Scoped Failure Isolation](#agentarch-10-node-scoped-failure-isolation) — When a node breaks, the rest of the graph keeps running
- [agentarch-11: Multi-Model Tier Architecture](#agentarch-11-multi-model-tier-architecture) — Fast models for construction, strong reasoning models for validation
- [agentarch-12: Budget Transparency in Agent Systems](#agentarch-12-budget-transparency-in-agent-systems) — Advisory caps vs hard-kill switches

---

## agentarch-07: Graph Engineering — Agent Coordination as a Graph

> **Source**: [§"Part 1: What Graph Engineering Actually Is"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-1-what-graph-engineering-actually-is)

| | |
|:---|:---|
| **Problem** | Multi-agent systems built with scripts break when one agent needs to wait on another, when state must persist across cycles, or when agents need to run in parallel. Every retail quant who tried to build a multi-agent system hit these three walls. |
| **Root cause** | Scripts are linear execution models. They have no native concept of parallelism, state persistence, or failure isolation. Coordination logic is hand-written glue code that becomes the primary debugging surface. |

### The Progression

| Stage | Coordination Model | Failure Mode |
|:---|:---|:---|
| **Prompts** | Human is the loop | Nothing survives when laptop closes |
| **Loops** | Script wraps prompt, fires on schedule | Single-agent; parallelism requires duplication |
| **Swarms** | Multiple agents with hand-written Python glue | Glue code becomes the debugging bottleneck |
| **Graphs** | Nodes are agents, edges are data handoffs | Failure scoped to node, not pipeline |

**Strategy — Design coordination as a graph, not a script**:

A graph makes parallel execution native, state persistent, and failure scoped to individual nodes. When a node breaks, the rest of the graph keeps running. You patch the broken node by describing the failure in plain English rather than chasing a stack trace.

**Tradeoff**: Graph-based coordination requires a runtime that can execute the graph (e.g., Slate Programs). The infrastructure investment pays off when the number of agents exceeds what a single developer can manually coordinate — roughly 4+ agents with inter-dependencies.

> **Dictionary**: [Agent Loop](../../reference-dictionary/ai-ml-llm.md#agent-loop), [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai)

---

## agentarch-08: Maker-Checker Pattern — Separate Generation from Validation

> **Source**: [§"Part 2: The Tool That Runs The Graph"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-2-the-tool-that-runs-the-graph), [§"Part 3: The Multi-Factor Alpha Graph"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-3-the-multi-factor-alpha-graph)

| | |
|:---|:---|
| **Problem** | When the same agent (or same model) both generates output and validates it, errors compound silently. In quantitative finance, this means false alpha signals survive into production. |
| **Root cause** | Self-validation lacks an adversarial perspective. The generating model carries the same blind spots into the validation step. |

**Strategy — Assign generation and validation to different nodes running on different model tiers**:

- **Maker nodes** (factor construction): Run on fast, cost-effective models (e.g., Claude Sonnet)
- **Checker nodes** (validator, regime auditor, risk decomposer): Run on stronger reasoning models (e.g., Claude Opus)
- The checker runs Newey-West t-tests, bootstrap resampling (10,000 iterations), and factor decomposition — statistical gates the maker cannot bypass

This is the `/goal` pattern: one node writes, another verifies, a third runs both, a fourth grades whether outputs match. If they don't match, the graph loops back with the specific mismatch as feedback.

**Tradeoff**: Stronger reasoning models cost more per token. However, the cost is amortized because the checker only runs after all parallel maker nodes complete — it processes a smaller, filtered input set. In practice, ~80% of promising signals get rejected at the validation gate, so the checker is filtering, not generating.

> **Dictionary**: [LLM-as-Judge](../../reference-dictionary/ai-ml-llm.md#llm-as-judge), [Verification Loop](../../reference-dictionary/ai-ml-llm.md#verification-loop-ai)

---

## agentarch-09: Parallel Agent Fanout with Sequential Coordination

> **Source**: [§"Part 3: The Multi-Factor Alpha Graph"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-3-the-multi-factor-alpha-graph)

| | |
|:---|:---|
| **Problem** | Multi-factor models require seven independent factor computations (market beta, size, value, momentum, profitability, investment, low volatility). Running them sequentially wastes time; running them in parallel without coordination produces inconsistent outputs. |
| **Root cause** | Factor computations are independent (no data dependencies between them), but validation, regime auditing, and portfolio construction depend on ALL factor outputs being complete. |

**Strategy — Fan out in parallel, sync at a barrier, then coordinate sequentially**:

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  Market  │ │   Size   │ │  Value   │ │ Momentum │ │Profitab. │ │Investm.  │ │ Low Vol  │
│  Beta    │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     └────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘
                                        │
                                  ┌─────▼─────┐
                                  │  SYNC     │  ← Barrier: all 7 must complete
                                  └─────┬─────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
            ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
            │  Validator   │──▶│   Regime     │──▶│  Portfolio   │──▶ Risk Decomp.
            │              │   │  Auditor     │   │ Constructor  │
            └──────────────┘   └──────────────┘   └──────────────┘
```

**Key design decisions**:
- Parallel nodes have no inter-dependencies → no deadlock risk
- The sync barrier is implicit in the graph structure (edges define data flow)
- Sequential coordination nodes form a pipeline where each stage filters before passing to the next
- State persists to filesystem between cycles (timestamped run directories)

**Tradeoff**: This pattern requires all parallel nodes to complete before any coordination begins. If one factor agent is slow (e.g., rate-limited on balance sheet parsing), it becomes the critical path. Mitigation: per-node timeouts with graceful degradation (the graph runs with partial factor sets rather than dying entirely).

> **Dictionary**: [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai)

---

## agentarch-10: Node-Scoped Failure Isolation

> **Source**: [§"Part 1: What Graph Engineering Actually Is"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-1-what-graph-engineering-actually-is), [§"Step 11: Debug When It Breaks"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#step-11-debug-when-it-breaks)

| | |
|:---|:---|
| **Problem** | In script-based multi-agent systems, when one agent fails (e.g., rate-limited while parsing 500 balance sheets), the entire pipeline dies. Debugging means reading a stack trace and guessing which agent was upstream of the crash. |
| **Root cause** | Scripts have pipeline-scoped failure, not node-scoped failure. There is no boundary between "this agent failed" and "the system is dead." |

**Strategy — Scope failure to individual graph nodes**:

In a graph, when a node breaks, the rest of the graph keeps running. The failed node is patched independently by describing the failure in plain English to the graph runtime. Examples from the article:

| Failure | Patch |
|:---|:---|
| Value agent blocked on non-US balance sheets | Added currency normalization step to the node |
| Momentum agent returned zero signals in hostile regimes | Added fallback that widens momentum lookback window |
| Portfolio constructor violated sector neutrality | Added projection step to enforce neutrality |

**Tradeoff**: Node-scoped failure means partial results can propagate (a missing factor). The downstream coordination nodes must be designed to handle incomplete inputs — the validator already rejects factors, so a missing factor is treated the same as a rejected one. This requires explicit handling, not implicit assumptions.

> **Dictionary**: [Resilience Stack](../../reference-dictionary/resilience.md) — related: circuit breaker, graceful degradation

---

## agentarch-11: Multi-Model Tier Architecture

> **Source**: [§"Part 3: The Multi-Factor Alpha Graph"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-3-the-multi-factor-alpha-graph), [§"Step 5: Connect Your Models"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#step-5-connect-your-models)

| | |
|:---|:---|
| **Problem** | Using the same model for all agent nodes wastes money on simple tasks and under-powers complex ones. Factor construction (data retrieval, sorting, regression) needs less reasoning depth than statistical validation (Newey-West t-tests, Hidden Markov Model regime detection). |
| **Root cause** | Single-model architectures treat all agent tasks as equal-complexity. In reality, coordination/validation nodes require stronger reasoning than data-processing nodes. |

**Strategy — Assign models to nodes based on task complexity**:

| Tier | Model | Nodes | Reasoning Need |
|:---|:---|:---|:---|
| **Fast** | Claude Sonnet | 7 factor construction agents | Data retrieval, sorting, regression, spread computation |
| **Strong** | Claude Opus | Validator, Regime Auditor, Risk Decomposer | Statistical testing, regime detection, factor decomposition |

**Key principle**: The maker never validates the maker's own work — not just in terms of which node does what, but which *model tier* powers the node. A Sonnet-built factor must be validated by an Opus-powered validator.

**Tradeoff**: Multi-tier architectures increase operational complexity (two model subscriptions, two cost profiles). The cost is justified when validation gates reject ~80% of signals — the strong tier processes filtered data, not raw data. If rejection rates drop below 30%, the architecture may be over-engineered for the problem.

> **Dictionary**: [LLM-as-Judge](../../reference-dictionary/ai-ml-llm.md#llm-as-judge), [Agentic AI](../../reference-dictionary/ai-ml-llm.md#agentic-ai)

---

## agentarch-12: Budget Transparency in Agent Systems

> **Source**: [§"Part 5: What Actually Happened When I Ran It"](../../articles/agentic-ai/graph-engineering-multi-factor-alpha-model.md#part-5-what-actually-happened-when-i-ran-it)

| | |
|:---|:---|
| **Problem** | Most agent frameworks silently pretend budget caps are enforced when they are not. When a $30/run cap is actually advisory, silent pretense leads to runaway costs that compound daily. |
| **Root cause** | Real-time cost metering primitives do not exist in most LLM API infrastructures. Budgets are enforced as stated caps plus self-reported spend that gets summed and flagged — not as hard abort mid-run. |

**Strategy — Be explicit about what layer of enforcement the budget actually provides**:

The Slate runtime explicitly told the author: the $30/run cap is advisory (stated cap + self-reported spend tracking), not a hard kill switch. It offered to design a hard abort mechanism if needed. This transparency lets the operator make an informed decision:

- **Advisory cap**: Suitable when occasional overruns are acceptable and the primary goal is cost visibility
- **Hard abort**: Necessary when costs must never exceed a threshold (e.g., compliance budgets)

**Tradeoff**: Hard abort mechanisms add complexity (real-time cost tracking, mid-run cancellation with state preservation). Advisory caps are simpler but require operator discipline. The right choice depends on whether cost overruns are a financial risk or an inconvenience.

> **Dictionary**: [Guardrails (AI)](../../reference-dictionary/ai-ml-llm.md#guardrails-ai)
