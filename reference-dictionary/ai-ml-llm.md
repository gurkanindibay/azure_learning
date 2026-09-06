---
type: Reference
title: "AI/ML, LLM & Agentic AI"
description: "A **Large Language Model** — a foundation model that generates text probabilistically from training data. LLMs power chatbots, code assistants, and AI agents."
timestamp: 2026-06-14T00:00:00Z
---

# AI/ML, LLM & Agentic AI

> **Domain**: LLM infrastructure, RAG architecture, AI agents, prompt engineering, and AI-assisted development.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| LLM (Large Language Model) | [`#llm`](#llm) |
| RAG (Retrieval-Augmented Generation) | [`#rag`](#rag) |
| Vector Database | [`#vector-database`](#vector-database) |
| Embedding | [`#embedding`](#embedding) |
| Chunking Strategy | [`#chunking-strategy`](#chunking-strategy) |
| Grounding | [`#grounding`](#grounding) |
| Hallucination | [`#hallucination`](#hallucination) |
| Guardrails (AI) | [`#guardrails-ai`](#guardrails-ai) |
| Agentic AI | [`#agentic-ai`](#agentic-ai) |
| Agent Loop | [`#agent-loop`](#agent-loop) |
| Tool Calling | [`#tool-calling`](#tool-calling) |
| MCP (Model Context Protocol) | [`#mcp`](#mcp) |
| Chain of Thought (CoT) | [`#chain-of-thought`](#chain-of-thought) |
| Hybrid Intelligence | [`#hybrid-intelligence`](#hybrid-intelligence) |
| Agent Harness | [`#agent-harness`](#agent-harness) |
| Context Rot (Lost in the Middle) | [`#context-rot`](#context-rot) |
| Scaffolding (LLM) | [`#scaffolding-llm`](#scaffolding-llm) |
| Verification Loop (AI) | [`#verification-loop-ai`](#verification-loop-ai) |
| Technical Deflation | [`#technical-deflation`](#technical-deflation) |
| Five Levels of AI-Assisted Dev | [`#five-levels`](#five-levels) |
| Dark Factory | [`#dark-factory`](#dark-factory) |
| Accountability Gap | [`#accountability-gap`](#accountability-gap) |
| Context Freshness | [`#context-freshness`](#context-freshness) |
| Human Ownership | [`#human-ownership`](#human-ownership) |
| Owner Tag | [`#owner-tag`](#owner-tag) |
| Review Gate | [`#review-gate`](#review-gate) |
| Token | [`#token`](#token) |
| LLM-as-Judge | [`#llm-as-judge`](#llm-as-judge) |
| Context Engineering | [`#context-engineering`](#context-engineering) |
| Vibe Coding | [`#vibe-coding`](#vibe-coding) |
| Trajectory Evaluation | [`#trajectory-evaluation`](#trajectory-evaluation) |
| Agent Skills | [`#agent-skills`](#agent-skills) |
| Ralph Loop | [`#ralph-loop`](#ralph-loop) |
| Two-Track Agentic Workflow | [`#two-track-agentic-workflow`](#two-track-agentic-workflow) |
| Attention-Weighted Parallelism | [`#attention-weighted-parallelism`](#attention-weighted-parallelism) |
| Loop Viability Test | [`#loop-viability-test`](#loop-viability-test) |
| Loop Build Order | [`#loop-build-order`](#loop-build-order) |
| Cost Per Accepted Change | [`#cost-per-accepted-change`](#cost-per-accepted-change) |
| Premature Loop Exit | [`#premature-loop-exit`](#premature-loop-exit) |
| Prompt Caching | [`#prompt-caching`](#prompt-caching) |
| Workflow Files | [`#workflow-files`](#workflow-files) |
| Persistent Session Memory | [`#persistent-session-memory`](#persistent-session-memory) |
| Subagent | [`#subagent`](#subagent) |
| Multi-Agent Coordination Patterns | [`#multi-agent-coordination-patterns`](#multi-agent-coordination-patterns) |
| Agent Sandboxing | [`#agent-sandboxing`](#agent-sandboxing) |
| Agent Permissions | [`#agent-permissions`](#agent-permissions) |
| Pre-Tool Hook | [`#pre-tool-hook`](#pre-tool-hook) |
| Prompt Injection | [`#prompt-injection`](#prompt-injection) |
| Pre-Commit Gate | [`#pre-commit-gate`](#pre-commit-gate) |
| Agent Tracing | [`#agent-tracing`](#agent-tracing) |
| Agent Metrics | [`#agent-metrics`](#agent-metrics) |
| Token Compression | [`#token-compression`](#token-compression) |
| Type-Specific Compression | [`#type-specific-compression`](#type-specific-compression) |
| Reversible Compression (LLM) | [`#reversible-compression-llm`](#reversible-compression-llm) |
| Graph Engineering | [`#graph-engineering`](#graph-engineering) |
| Maker-Checker Pattern (AI Agents) | [`#maker-checker-pattern-ai`](#maker-checker-pattern-ai) |
| Loop Engineering | [`#loop-engineering`](#loop-engineering) |
| Swarm (AI Agents) | [`#swarm-ai-agents`](#swarm-ai-agents) |
| Agent Graph | [`#agent-graph`](#agent-graph) |
| Multi-Model Tier Architecture | [`#multi-model-tier-architecture`](#multi-model-tier-architecture) |
| Context Injection | [`#context-injection`](#context-injection) |
| Action Surfaces | [`#action-surfaces`](#action-surfaces) |
| Loop Contract | [`#loop-contract`](#loop-contract) |
| Evidence-Based Stopping | [`#evidence-based-stopping`](#evidence-based-stopping) |
| Structure-Aware Chunking | [`#structure-aware-chunking`](#structure-aware-chunking) |
| Semantic Chunking | [`#semantic-chunking`](#semantic-chunking) |
| Chunk Inspection Audit | [`#chunk-inspection-audit`](#chunk-inspection-audit) |
| Context Governor | [`#context-governor`](#context-governor) |
| Cognitive Debris | [`#cognitive-debris`](#cognitive-debris) |
| Context Working Set | [`#context-working-set`](#context-working-set) |
| Context Pruning | [`#context-pruning`](#context-pruning) |
| Semantic Contamination | [`#semantic-contamination`](#semantic-contamination) |
| MoE (Mixture of Experts) | [`#moe`](#moe) |
| Demand Paging for MoE Weights | [`#demand-paging-moe-weights`](#demand-paging-moe-weights) |
| Read-Compute Overlapping (Inference) | [`#read-compute-overlapping-inference`](#read-compute-overlapping-inference) |
| Vector Search (ANN) | [`#vector-search-ann`](#vector-search-ann) |
| KB-Gap Detector | [`#kb-gap-detector`](#kb-gap-detector) |
| Grounding Rate | [`#grounding-rate`](#grounding-rate) |
| Reopen-Gated Auto-Resolution Rate | [`#reopen-gated-auto-resolution-rate`](#reopen-gated-auto-resolution-rate) |
| Model Routing by Complexity | [`#model-routing-by-complexity`](#model-routing-by-complexity) |
| Graceful Spend Degradation (LLM) | [`#graceful-spend-degradation-llm`](#graceful-spend-degradation-llm) |
| Copilot Acceptance Rate | [`#copilot-acceptance-rate`](#copilot-acceptance-rate) |
| Generative Watermarking | [`#generative-watermarking`](#generative-watermarking) |
| Content Credentials (C2PA) | [`#content-credentials-c2pa`](#content-credentials-c2pa) |
| G-Value (Watermark Scoring) | [`#g-value-watermark-scoring`](#g-value-watermark-scoring) |
| Disposable Repositories | [`#disposable-repositories`](#disposable-repositories) |
| Collaborative Filtering | [`#collaborative-filtering`](#collaborative-filtering) |
| Matrix Factorization | [`#matrix-factorization`](#matrix-factorization) |
| Cold-Start Problem (Recommendation Systems) | [`#cold-start-problem-recommendation-systems`](#cold-start-problem-recommendation-systems) |
| Acoustic Feature Extraction | [`#acoustic-feature-extraction`](#acoustic-feature-extraction) |
| Latent Factors | [`#latent-factors`](#latent-factors) |


---

## LLM

A **Large Language Model** — a foundation model that generates text probabilistically from training data. LLMs power chatbots, code assistants, and AI agents.

| Property | Detail |
|:---|:---|
| **Input** | Prompt (system + user messages) |
| **Output** | Probabilistic text completion |
| **Cost driver** | Input + output tokens |
| **Limitation** | No inherent fact-checking — prone to hallucination |

**Also see**: [RAG](#rag), [Hallucination](#hallucination), [Token](#token)

---

## RAG

**Retrieval-Augmented Generation** — an architecture that grounds LLM responses in retrieved documents rather than relying solely on training data. Reduces hallucination by providing factual context at inference time.

```
User query → Embedding → Vector search → Retrieve top-K docs → Inject into prompt → LLM generates grounded response
```

| Component | Role |
|:---|:---|
| **Embedding model** | Converts text → vectors for semantic search |
| **Vector DB** | Stores and queries document embeddings |
| **Chunking** | Splits documents into searchable units |
| **Grounding** | Injects retrieved docs into the LLM prompt |

**Also see**: [Vector Database](#vector-database), [Embedding](#embedding), [Grounding](#grounding)

---

## Vector Database

A database optimized for storing and querying **vector embeddings** for similarity search. Unlike traditional DBs that match exact values, vector DBs find "semantically similar" items.

| Algorithm | Speed | Recall | Memory | Best For |
|:---|:---|:---|:---|:---|
| **HNSW** | Very fast | High | High | Low-dim, high-recall needs |
| **IVF + PQ** | Fast | Lower | Low | High-dim, disk-backed |
| **DiskANN** | Medium | Very high | Very low | Billion-scale, SSD-based |

**Also see**: [Embedding](#embedding), [RAG](#rag)

---

## Embedding

A **dense vector representation** of text, images, or other data — generated by an embedding model. Similar items map to nearby points in vector space, enabling semantic (meaning-based) rather than keyword search.

**Also see**: [Vector Database](#vector-database), [RAG](#rag)

---

## Chunking Strategy

How documents are split into searchable units for vector indexing. Poor chunking = poor retrieval quality.

| Strategy | Mechanism | Best For |
|:---|:---|:---|
| **Fixed-size** | Split every N tokens | Simple, predictable |
| **Semantic** | Split at section/paragraph boundaries | Preserving meaning |
| **Overlapping sliding window** | Overlap adjacent chunks | Preserving cross-boundary context |
| **Hierarchical** | Chunk → summary → document parent | Multi-level retrieval |

**Also see**: [RAG](#rag), [Vector Database](#vector-database)

---

## Grounding

Anchoring LLM output in **retrieved facts and documents** to reduce hallucination. The grounding spectrum: Pure LLM → RAG + Prompting → RAG + Validation → Human-in-loop.

**Also see**: [RAG](#rag), [Hallucination](#hallucination)

---

## Hallucination

When an LLM generates **plausible-sounding but factually incorrect** content. Mitigated by RAG, grounding, guardrails, and human-in-the-loop validation.

**Also see**: [Grounding](#grounding), [RAG](#rag), [Guardrails](#guardrails-ai)

---

## Guardrails (AI)

Validation layers that **check LLM output before returning to the user** — catching hallucinations, policy violations, or incorrect formats. Guardrails are the safety net between generation and delivery.

**Also see**: [Hallucination](#hallucination), [Grounding](#grounding)

---

## Agentic AI

AI that **perceives, plans, uses tools, and iterates toward goals** — fundamentally different from one-shot chatbots. Agentic AI operates in continuous loops rather than single request-response cycles.

**Also see**: [Agent Loop](#agent-loop), [Tool Calling](#tool-calling)

---

## Agent Loop

The continuous cycle of an AI agent: **Perceive → Think → Plan → Act → Evaluate → Repeat**. Each iteration refines the agent's understanding and moves it closer to the goal.

**Also see**: [Agentic AI](#agentic-ai), [Tool Calling](#tool-calling)

---

## Tool Calling

An LLM's ability to **invoke external tools** (APIs, code execution, web browsers) via structured function calls. Tools give agents the ability to act beyond text generation.

**Also see**: [Agent Loop](#agent-loop), [MCP](#mcp)

---

## MCP

**Model Context Protocol** — a standardized protocol for cross-provider tool interoperability. Allows AI agents to use tools from any provider that implements the MCP standard (vs. vendor-locked function calling).

**Also see**: [Tool Calling](#tool-calling), [Agentic AI](#agentic-ai)

---

## Chain of Thought

A prompting technique where the LLM is instructed to **reason step-by-step** before producing the final answer. For linear problems, CoT significantly improves accuracy.

**Also see**: [Agent Loop](#agent-loop)

---

## Hybrid Intelligence

Combining **deterministic rules** (calculations, risk scores, thresholds) with **AI reasoning** (interpretation, context, narrative). The deterministic engine provides ground truth; AI adds explainability.

**Also see**: [Agentic AI](#agentic-ai)

---

## Agent Harness

The **complete software infrastructure wrapping an LLM** — orchestration loop, tools, memory, context management, state persistence, error handling, guardrails, and verification loops. The harness is what transforms a stateless LLM into a production-capable agent.

> "If you're not the model, you're the harness." — Vivek Trivedy, LangChain

| Component | Role |
|:---|:---|
| Orchestration Loop | ReAct/TAO cycle: assemble prompt → call LLM → parse output → execute tools → repeat |
| Tools | Schema-defined external capabilities (APIs, code exec, web access) |
| Memory | Multi-tier: short-term (session), long-term (cross-session files/DBs) |
| Context Management | Compaction, masking, JIT retrieval, sub-agent delegation |
| Verification Loops | Rules-based (tests), visual (screenshots), LLM-as-judge |
| Guardrails | Input/output/tool validation; permission enforcement |

**When to use**: Any production agent beyond a single prompt-and-response.  
**When NOT to use**: Simple chatbots, single-call LLM usage, prototypes.  
**Also see**: [Agentic AI](#agentic-ai), [Agent Loop](#agent-loop), [Context Rot](#context-rot), [Scaffolding (LLM)](#scaffolding-llm), [Verification Loop](#verification-loop-ai)

---

## Context Rot

The **silent, progressive performance degradation of an AI agent or LLM as context accumulates over time**, caused by a combination of attention displacement (**"Lost in the Middle"** phenomenon) and the accumulation of **cognitive debris** (stale assumptions, obsolete tool outputs, superseded hypotheses, and semantic contamination). Rather than failing loudly with a crash, the agent degrades quietly: it hallucinating from badly managed context, violates earlier constraints, cites outdated evidence, and makes confident errors over an unpruned working set.

| Failure Mechanism | Manifestation | Mitigation |
|:---|:---|:---|
| **Attention Displacement** | Mid-window tokens receive diminished attention weights | Compaction, observation masking, JIT retrieval |
| **Cognitive Debris Accumulation** | Stale tool traces and expired hypotheses crowd out decisive evidence | Context governor, dynamic pruning, stale-memory decay |
| **Semantic Contamination** | Plausible, semantically similar but incorrect chunks pollute prompt distribution | Relevance routing, domain classifier gating, hard negative filtering |
| **Context Landfill** | Prompt treated as passive append-only log rather than governed working set | Explicit context lifecycle, evidence state tables, working-set isolation |

### Key Characteristics
- **Deceptive stability**: The agent produces superficially coherent, confident responses while operating over contaminated working memory.
- **Quantity paradox**: Larger context windows reduce curation pressure, often accelerating degradation rather than fixing it.
- **Systems-level defect**: Caused by the absence of context lifecycle management (admit, retain, prune, evict, audit) rather than poor model weights.

### When to Use
- Multi-turn agents, long-horizon workflows, production RAG, coding assistants, and operational troubleshooting agents.

### When NOT to Use
- Single-turn queries or stateless completions where no historical context or tool traces accumulate.

### Also see
- [Context Engineering](#context-engineering)
- [Context Governor](#context-governor)
- [Cognitive Debris](#cognitive-debris)
- [Context Working Set](#context-working-set)
- [Context Pruning](#context-pruning)
- [Semantic Contamination](#semantic-contamination)
- [Agent Harness](#agent-harness)
- [Token](#token)

---

## Scaffolding (LLM)

**Temporary infrastructure that enables an LLM to perform capabilities it cannot yet do natively** — analogous to construction scaffolding. As models improve, scaffolding is removed. The co-evolution principle: models are now post-trained with specific harnesses in the loop; changing tool implementations can degrade performance because of this tight coupling.

| Principle | Implication |
|:---|:---|
| Scaffolding is temporary | Remove as models internalize the capability |
| Co-evolution | Models trained with specific harnesses; tool changes may break expectations |
| Future-proofing test | If performance scales with better models without adding harness complexity, the design is sound |

**When to use**: Gap-filling for model limitations that will be resolved by future model versions.  
**When NOT to use**: Permanent architectural decisions (use harness instead).  
**Also see**: [Agent Harness](#agent-harness), [Agentic AI](#agentic-ai)

---

## Verification Loop (AI)

A **self-checking mechanism that validates agent output before delivery** — improving quality by 2–3x according to Claude Code's creator. Three approaches: **rules-based** (tests, linters, type checkers — deterministic ground truth), **visual** (screenshots via Playwright for UI tasks), and **LLM-as-judge** (separate subagent evaluates semantic output quality).

| Type | Mechanism | Latency | Determinism |
|:---|:---|:---|:---|
| Rules-Based | Tests, linters, schemas | Low | Deterministic |
| Visual | Screenshots via browser automation | Medium | Deterministic |
| LLM-as-Judge | Subagent semantic evaluation | High | Probabilistic |

**When to use**: Any agent whose output must be correct (code generation, data transformation, UI work).  
**When NOT to use**: Exploratory/conversational agents where correctness is subjective.  
**Also see**: [Agent Harness](#agent-harness), [Guardrails](#guardrails-ai), [Agent Loop](#agent-loop)

---

## Technical Deflation

The **exponentially declining cost of code** due to AI — reshaping how organizations think about tech debt, build-vs-buy, and engineering headcount. Code that was expensive yesterday may be near-free tomorrow.

**Also see**: [Five Levels](#five-levels), [Dark Factory](#dark-factory)

---

## Five Levels

The **Five Levels of AI-Assisted Development** — an NHTSA-inspired maturity model:

| Level | Name | Human Role |
|:---|:---|:---|
| **L0** | Autocomplete | Coder types; AI suggests |
| **L1** | Chat-based assistance | Coder asks; AI answers |
| **L2** | Pair programming | AI and human collaborate on code |
| **L3** | Code review at scale | Human reviews AI-generated code |
| **L4** | Spec-driven development | Spec is truth; AI generates code |
| **L5** | Dark Factory | Fully autonomous; no human involved |

> **Level 2 Trap**: 90% of AI-native developers plateau at L2, believing pair-programming is the end-state.

**Also see**: [Dark Factory](#dark-factory), [Technical Deflation](#technical-deflation)

---

## Dark Factory

**Level 5** on the AI-assisted development scale — fully autonomous software generation with **no human involvement**. Code is produced, tested, and deployed entirely by AI.

**Also see**: [Five Levels](#five-levels)

---

## Accountability Gap

The **absence of a named owner for AI-generated output**. In production agentic systems, every recommendation, report, or generated artifact can be wrong, stale, or hallucinated; without pre-assigned ownership, failures become unactionable because no individual or team is accountable for verifying the output before it ships.

### Key Characteristics
- No named owner is attached to the generated artifact.
- Post-mortems stall at "the model got it wrong".
- Stale or hallucinated output reaches users because generation outpaces validation.

### When to Use
- Use the term when diagnosing why AI failures are unactionable in production.

### When NOT to Use
- Do not use it for failures where an owner is already clearly defined.

### Also see
- [Agentic AI](#agentic-ai)
- [Human Ownership](#human-ownership)
- [Review Gate](#review-gate)

---

## Context Freshness

The **degree to which an AI agent's source context is still current** at the moment it generates output. Freshness is critical because agents retrieve or reason over documents, databases, and conversation history that can become outdated.

### Key Characteristics
- Agents produce output based on retrieved or injected context.
- Context ages; a document that was correct last quarter may be wrong today.
- A `context_as_of` timestamp makes staleness visible.

### When to Use
- Any agent pipeline where decisions depend on time-sensitive data.

### When NOT to Use
- Not needed when the underlying knowledge is static or versioned independently.

### Also see
- [RAG](#rag)
- [Grounding](#grounding)
- [Context Rot](#context-rot)

---

## Human Ownership

The **practice of assigning a named person to every AI-generated output** before it is shipped. The owner is the individual who would put their name on the output and is accountable for its accuracy, freshness, and appropriateness.

### Key Characteristics
- One named human is responsible for each artifact.
- Ownership is recorded before the output is released.
- The owner is expected to approve or reject the output at the review gate.

### When to Use
- Use for any AI-generated artifact that affects users, decisions, or downstream systems.

### When NOT to Use
- Skip for low-stakes, exploratory, or internal-only outputs where no one would act on the result.

### Also see
- [Accountability Gap](#accountability-gap)
- [Agentic AI](#agentic-ai)
- [Owner Tag](#owner-tag)

---

## Owner Tag

A **metadata label that attaches a named human owner to an AI-generated artifact** at the point of generation. The tag travels with the output through the pipeline and is checked at the review gate.

```python
{
    "output": response,
    "owner": "priya.sharma@company.com",
    "context_as_of": "2026-06-01",
    "reviewed": False
}
```

### Key Characteristics
- Embedded in the artifact metadata at generation time.
- Maps the output to a real person or team.
- Consumed by the review gate before shipping.

### When to Use
- Use in any production pipeline where accountability is required.

### When NOT to Use
- Not needed for anonymous or low-stakes internal drafts.

### Also see
- [Human Ownership](#human-ownership)
- [Review Gate](#review-gate)

---

## Review Gate

A **system-enforced checkpoint that blocks AI-generated output from shipping until a named owner explicitly approves it**. The gate turns "would you put your name on this?" from a cultural norm into an architectural invariant.

### Key Characteristics
- Blocks release unless the owner tag is present and approved.
- Produces an audit log of who approved what and when.
- Operates independently of team culture or busy schedules.

### When to Use
- Use for high-stakes or externally visible AI output.

### When NOT to Use
- Skip for internal experiments where review overhead exceeds risk.

### Also see
- [Guardrails (AI)](#guardrails-ai)
- [Verification Loop (AI)](#verification-loop-ai)
- [Owner Tag](#owner-tag)

---

## Token

The **unit of text** consumed or generated by an LLM. Tokens drive cost (input + output), context window limits, and prompt engineering strategies. ~1 token ≈ ¾ of an English word.

**Also see**: [LLM](#llm)

---

## LLM-as-Judge

A **verification pattern where a separate LLM instance evaluates the output of another agent or model**, acting as a semantic quality reviewer. One of the three verification approaches in agent harness design: rules-based (tests, linters), visual (screenshots), and LLM-as-judge.

| Property | Detail |
|:---|:---|
| **Mechanism** | Secondary LLM call evaluates output against a rubric or criteria |
| **Determinism** | Probabilistic — unlike rules-based checks |
| **Cost** | Adds extra LLM inference latency and token cost |
| **Strength** | Catches semantic issues linters and tests cannot detect |

### Key Characteristics
- Implemented as a subagent receiving the primary agent's output and an evaluation rubric
- Complements rather than replaces deterministic verification (tests, linters)
- Boris Cherny (Claude Code creator): verification loops improve quality by 2–3×

### When to Use
- Output correctness is hard to verify with deterministic rules
- Semantic quality matters (report accuracy, code explanation coherence, narrative quality)
- Latency and token budget allow additional inference

### When NOT to Use
- High-throughput, low-latency pipelines where extra inference is too costly
- Outputs fully verifiable by deterministic rules (tests, schemas)
- Short-form outputs where over-verification adds no practical value

### Also see
- [Verification Loop (AI)](#verification-loop-ai)
- [Agent Harness](#agent-harness)
- [Guardrails (AI)](#guardrails-ai)

---

## Context Engineering

The **discipline of managing what information an LLM sees and when** — the middle layer between prompt engineering (what instructions you write) and harness engineering (the full application infrastructure). Context engineering controls the assembly, compression, and positioning of information within the LLM's context window.

| Concern | Technique |
|:---|:---|
| Context rot prevention | Position key content at beginning and end of context |
| Window pressure | Compaction: summarize history, discard redundant tool outputs |
| Stale tool outputs | Observation masking: hide old outputs while keeping tool call records |
| Full-file loading | JIT retrieval: grep/glob/head dynamically instead of loading full files |
| Context exhaustion | Sub-agent delegation: subagents return 1,000–2,000 token condensed summaries |

> Anthropic's goal: find the **smallest possible set of high-signal tokens** that maximize the likelihood of the desired outcome.

### Key Characteristics
- Distinct from prompt engineering (what you write) and harness engineering (the infrastructure)
- Directly addresses context rot and "Lost in the Middle" degradation
- Increasingly critical as agents handle longer-horizon, multi-tool tasks

### When to Use
- Multi-turn or long-running agents with tool calls
- Tasks producing large volumes of intermediate tool output
- High-accuracy requirements where context quality directly affects output quality

### When NOT to Use
- Single-call LLM usage with short prompts
- Conversational chat without tool calls or long context history

### Also see
- [Agent Harness](#agent-harness)
- [Context Rot](#context-rot)
- [Scaffolding (LLM)](#scaffolding-llm)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Ralph Loop

An **Anthropic-developed two-phase pattern for long-running agentic tasks that span multiple context windows**. An **Initializer Agent** runs once to set up the environment; a **Coding Agent** runs in each subsequent session, using git history and progress files to orient itself and continue work without a long-lived process.

```
Initializer Agent (runs once):
  → create environment setup (init script)
  → write progress file + feature list
  → make initial git commit

Coding Agent (runs each session):
  → read git log + progress file to orient
  → pick highest-priority incomplete feature
  → implement → commit → write session summary
  → exit (filesystem provides continuity)
```

The filesystem acts as persistent memory across context windows. Git commits are checkpoints; progress files are structured scratchpads.

### Key Characteristics
- Separates environment setup (once) from iterative execution (per session)
- Each Coding Agent session is context-window-bounded and self-contained
- No long-lived agent processes required — safe to restart or run in CI/CD
- Git log and progress files provide the continuity mechanism

### When to Use
- Multi-session coding tasks (refactoring, feature implementation across many files)
- Long-horizon tasks that exceed a single context window
- Scheduled or CI/CD-triggered agentic workflows

### When NOT to Use
- Short tasks that complete within a single context window
- Non-code tasks where git commits do not provide meaningful checkpoints

### Also see
- [Agent Harness](#agent-harness)
- [Scaffolding (LLM)](#scaffolding-llm)
- [Context Rot](#context-rot)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Two-Track Agentic Workflow

An **agentic development pattern that pairs a high-attention spec track with a low-attention implementation track**, enabling a single developer to run both in parallel by matching cognitive demand to available attention. Adapted from Marty Cagan's Dual-Track Development for AI-assisted software development.

```
Spec Track (high-attention):
  Idea → dialogue with agent → PRD → technical design → implementation plan
  [Human attention: continuous]

Implementation Track (low-attention):
  Implementation plan → agent executes autonomously
  → periodic human review checkpoints
  [Human attention: sporadic]

Parallel execution:
  While agent implements Feature N → human writes spec for Feature N+1
```

### Key Characteristics
- Maximum natural parallelism for a solo developer is 2 tracks (1 spec + 1 implementation)
- The spec track externalises tacit knowledge through iterative agent dialogue before any code is written
- Throughput is bounded by the spec track (Theory of Constraints), not by the number of implementation agents
- Verification (code review, functional QA, UX iteration) is a third non-delegatable phase that caps total delivery rate

### When to Use
- Solo developers or indie builders who hold both product and code decisions
- Features that are intended to live in production (not throwaway/vibe-coded work)
- Contexts where spec quality is the primary determinant of implementation quality

### When NOT to Use
- Throwaway or exploratory code where a spec would cost more than the code itself
- Team settings where dedicated PMs write specs (implementation plan step still applies, but PRD step is done externally)
- Single-file or trivial features where the implementation plan fits in one sentence

### Also see
- [Agent Harness](#agent-harness)
- [Five Levels of AI-Assisted Dev](#five-levels)
- [Verification Loop (AI)](#verification-loop-ai)
- [Attention-Weighted Parallelism](#attention-weighted-parallelism)
- [agentic-11 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-two-track-workflow.md#agentic-11-two-track-workflow--attention-weighted-parallelism)

---

## Attention-Weighted Parallelism

The principle that **tasks should be parallelised by matching their cognitive-attention demand to available human focus, not by maximising computational concurrency**. Two tasks with different attention profiles (one continuous, one sporadic) can run in parallel with a single human; two high-attention tasks cannot.

### Key Characteristics
- Attention is the finite resource in human-agent collaboration, not compute
- High-attention tasks (spec creation, UX iteration) are serially bounded per human
- Low-attention tasks (agent implementation, background builds) can be run alongside high-attention tasks
- Exceeding attention capacity creates context-switching overhead that degrades all tasks in flight

### When to Use
- Designing human-agent collaboration workflows
- Deciding how many parallel workstreams a single developer can sustain
- Prioritising where to apply automation (automate low-attention tasks first to free attention budget)

### When NOT to Use
- Pure computational parallelism problems where no human attention is required
- Team settings where attention cost is distributed across multiple people

### Also see
- [Two-Track Agentic Workflow](#two-track-agentic-workflow)
- [agentic-11 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-two-track-workflow.md#agentic-11-two-track-workflow--attention-weighted-parallelism)

---

## Loop Viability Test

A **four-condition checklist that determines whether a task warrants an agentic loop** rather than a well-crafted manual prompt. A loop is worth building only when all four conditions hold simultaneously.

| Condition | Minimum Bar | If Not Met |
|:---|:---|:---|
| **Task repeats** | At least weekly | Setup cost never pays back |
| **Auto-reject exists** | Test, type check, build, or hard rule | Loop spins without progress |
| **Agent can do it end-to-end** | No mid-task human hand-off | Human still in critical path |
| **"Done" is objective** | Not a matter of taste | Human judgment is required |

### Key Characteristics
- All four conditions must hold; missing one makes a manual prompt cheaper and more reliable
- The test eliminates most candidates; most tasks that feel like loop candidates fail condition 2 or 4
- Applying this filter before building prevents the class of loops that bill silently without delivering value

### When to Use
- Before investing time in loop design and tooling for any recurring AI task
- When evaluating whether to automate an AI workflow that currently runs manually

### When NOT to Use
- Skip the test for one-off tasks — a loop is already ruled out
- Do not use it as a reason to over-engineer a task that a single good prompt handles correctly

### Also see
- [Agent Loop](#agent-loop)
- [Loop Build Order](#loop-build-order)
- [agentic-19 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-loop-engineering.md#agentic-19-loop-viability-test--four-conditions)

---

## Loop Build Order

The **four-step sequence for building a reliable agentic loop**: prove manual reliability first, extract the instructions into a reusable skill, wrap in a loop with a verify gate and stop condition, then and only then put it on a schedule. Skipping any step produces a loop that bills silently while delivering nothing.

```
1. Manual run   — prove the task works reliably at least once by hand
2. Skill        — save instructions as a reusable file the loop reads every run
3. Loop         — add the verify gate + hard stop condition
4. Schedule     — only after steps 1–3 are solid
```

### Key Characteristics
- Each step validates the next; a schedule makes unreliable work run at scale, not more reliably
- The skill step is what makes automation maintainable — instructions live in one place, not embedded in a schedule nobody updates
- The verify gate and stop condition in step 3 are what distinguish a loop from a cron job that calls an LLM

### When to Use
- Any time a recurring AI task graduates from manual prompt to scheduled automation
- Building agentic pipelines that will run unsupervised

### When NOT to Use
- Do not apply to one-off tasks — the build order is for tasks that will recur
- Do not skip directly to step 4 even when time is tight; step 3 is what prevents runaway billing

### Also see
- [Agent Loop](#agent-loop)
- [Loop Viability Test](#loop-viability-test)
- [Premature Loop Exit](#premature-loop-exit)
- [agentic-20 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-loop-engineering.md#agentic-20-loop-build-order--prove-before-scheduling)

---

## Cost Per Accepted Change

The **efficiency metric for agentic loops**: the total token cost across all iterations divided by the number of results that passed review and were kept. This metric distinguishes a productive loop (high accept rate) from an expensive treadmill (high token spend, low accepted output).

```
cost per accepted change = total_tokens_spent / accepted_results_count
```

**Threshold**: an accept rate below **50%** means the loop costs more — in tokens and in human review time — than the value it produces.

### Key Characteristics
- Tokens spent or iterations run measure activity, not value; cost per accepted change measures return on loop investment
- Requires a result-auditing step outside the loop itself: a human or system marks each result accepted or rejected
- A strong verify gate raises the accept rate by blocking bad work before human review; maker/checker separation further raises quality

### When to Use
- Instrumenting any production agentic loop to determine whether it is worth running
- Comparing loop configurations (single-agent vs maker/checker, different verify gates) on a common efficiency basis

### When NOT to Use
- Exploratory or experimental loops where accept/reject judgment is not yet defined
- Loops with very small iteration counts where the metric has high variance

### Also see
- [Token](#token)
- [Verification Loop (AI)](#verification-loop-ai)
- [LLM-as-Judge](#llm-as-judge)
- [agentic-21 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-loop-engineering.md#agentic-21-cost-per-accepted-change--the-loop-efficiency-metric)

---

## Premature Loop Exit

A **silent failure mode** in agentic loops where the agent declares the task complete — and exits — before the work is actually done. Named by engineer Geoffrey Huntley as the "Ralph Wiggum loop", after the character who reports "I'm helping" while not actually helping. The loop then keeps running on its next scheduled trigger and billing for nothing.

### Key Characteristics
- The agent satisfies itself (not the verify gate) that the goal is met and returns a success signal prematurely
- Without a hard verify gate, the loop has no way to catch the false success
- The failure is silent: no error is raised, billing continues, and output quality silently degrades
- Distinct from the [Ralph Loop](#ralph-loop), which is a beneficial multi-context-window agentic pattern from Anthropic

### When to Use
- Use the term when diagnosing loops that appear to complete but produce incomplete or incorrect output
- Use it as the primary motivation for requiring a hard verify gate in every production loop

### When NOT to Use
- Do not apply to loops that fail with an explicit error — premature exit is specifically the *false success* case

### Also see
- [Verification Loop (AI)](#verification-loop-ai)
- [Review Gate](#review-gate)
- [Loop Build Order](#loop-build-order)
- [agentic-17 in system-design-architecture](../system-design-architecture/agentic-ai/agentic-loop-engineering.md#agentic-17-verify-gate--the-heart-of-the-loop)

---

## Prompt Caching

The **LLM provider feature that stores the stable prefix of a conversation** (system prompt, config files, tool definitions) so that subsequent turns only pay for the variable portion. The first call populates the cache at full cost; every subsequent turn within the cache window is cheaper and lower-latency.

```
Turn 1: [stable prefix: 2000 tok] + [message] → full cost, cache warm
Turn 2: [cache hit:   2000 tok] + [message] → reduced cost
Turn N: [cache hit:   2000 tok] + [message] → reduced cost
```

### Key Characteristics
- Rewards quality, not quantity — clean stable prefixes are cheap; bloated ones are still expensive
- Caches expire after a provider-defined idle period; next turn after expiry pays full cost
- Most effective when config and workflow files are kept short and stable

### When to Use
- Multi-turn agent sessions where the same system prompt, config, and tool schemas repeat every turn

### When NOT to Use
- Single-call LLM usage — no second turn to benefit from the cache
- Sessions where the stable prefix changes every turn

### Also see
- [Token](#token)
- [Workflow Files](#workflow-files)
- [Agent Harness](#agent-harness)

---

## Workflow Files

**Task-specific instruction files loaded on demand** — distinct from always-active config files (CLAUDE.md / AGENTS.md). Workflow files explain how to perform one specific task type (write tests, review a PR, migrate a database) and are only loaded when the agent needs that procedure.

### Key Characteristics
- Loaded on demand, not every session
- Written by humans based on real work — AI-generated workflow files under-perform human-written ones (SkillsBench: 86 tasks, 11 domains)
- A smaller model with good workflow files can outperform a larger model without them
- Generic AI-generated instructions add noise without clear guidance

### When to Use
- Repeated task types that benefit from standardized procedures
- Onboarding new agents to project-specific workflows

### When NOT to Use
- One-off tasks with no repetition — the write cost exceeds the reuse benefit
- Tasks where the correct procedure changes every time

### Also see
- [Context Engineering](#context-engineering)
- [Agent Harness](#agent-harness)
- [Prompt Caching](#prompt-caching)

---

## Persistent Session Memory

**Cross-session state that survives between agent invocations** — typically implemented as a `MEMORY.md` file or a searchable indexed store. Unlike the context window (which resets each session), persistent memory carries architectural decisions, conventions, and known issues forward so the developer does not repeat themselves.

### Key Characteristics
- The simplest form: a short `MEMORY.md` file in the project root, read at session start and updated during work
- If the memory file grows too large, it creates the same context-rot problem as a bloated config — keep it short
- For larger projects: searchable indexed memory where past sessions are stored and queried on demand

### When to Use
- Multi-session projects where decisions compound across sessions
- When re-explaining project context to the agent costs more than maintaining a memory file

### When NOT to Use
- Single-session tasks — no cross-session state is needed
- When memory file size exceeds what the agent can usefully process

### Also see
- [Context Rot](#context-rot)
- [Context Freshness](#context-freshness)

---

## Subagent

A **smaller, focused agent created by a parent agent for one specific job** — given a narrow task, a limited toolset, and a fresh context window. When the subagent finishes, it returns only a compressed summary (not every intermediate step) to the parent.

### Key Characteristics
- Fresh context window — subagent's intermediate tool outputs do not pollute the parent's context
- Parallel execution — multiple subagents can run simultaneously
- Conflict prevention — Git worktrees give each subagent its own file copy when editing shared files
- Returns a 1,000–2,000 token condensed summary to the parent

### When to Use
- Side tasks that produce large intermediate output (security review, test generation, docs update)
- When multiple independent tasks can run in parallel

### When NOT to Use
- Trivial tasks where subagent invocation latency exceeds the work itself
- When the parent needs every intermediate detail from the subtask

### Also see
- [Agent Harness](#agent-harness)
- [Agent Loop](#agent-loop)
- [Multi-Agent Coordination Patterns](#multi-agent-coordination-patterns)
- [Context Rot](#context-rot)

---

## Multi-Agent Coordination Patterns

**Three canonical patterns for organizing multiple agents** to handle tasks that a single agent cannot effectively perform alone. The handoff between agents — the size and quality of context passed — is the primary determinant of success.

| Pattern | Structure | Best For |
|:---|:---|:---|
| **Planner / Executor** | One agent creates the plan; another executes it | When reasoning before acting improves quality |
| **Router / Specialist** | One agent classifies the request; domain specialists handle each category | Predictability, lower cost, easier debugging per specialist |
| **Map-Reduce** | Task splits into parallel pieces; agents work concurrently; one agent merges results | Large content reviews, code review at scale, document analysis |

### Key Characteristics
- Real workflows combine all three patterns
- The Router/Specialist pattern is the most predictable — each specialist has a narrow prompt and smaller toolset
- Map-Reduce is the most expensive to debug when reducers merge inconsistent outputs
- Handoff context must be Goldilocks-sized: too little and the next agent loses the goal; too much and it loses focus

### When to Use
- When a single agent cannot handle the full task scope or quality requirements
- When parallel execution is needed for throughput

### When NOT to Use
- Tasks completable by a single well-prompted agent — multi-agent adds handoff complexity and cost

### Also see
- [Subagent](#subagent)
- [Agentic AI](#agentic-ai)
- [Agent Harness](#agent-harness)

---

## Agent Sandboxing

**Restrictions on what an agent can access**, enforced outside the model at the OS or container level — the agent cannot argue or prompt-engineer its way past the walls. Limits filesystem read/write paths, network access, and credential visibility so that when the agent makes a mistake, the blast radius is bounded.

### Key Characteristics
- Enforced at OS/container level, not inside the model — the sandbox does not care what the agent wants
- Strongest isolation: Docker container with no network access, no host credentials, no outbound connections unless explicitly whitelisted
- Complements but does not replace permission lists — sandboxing limits damage if something bad runs; permissions try to prevent it from running

### When to Use
- Any production agent with tool access to the filesystem or network
- When running agents on cloned repositories or untrusted code

### When NOT to Use
- Read-only agents that only consume trusted API responses — sandbox overhead exceeds risk

### Also see
- [Agent Permissions](#agent-permissions)
- [Pre-Tool Hook](#pre-tool-hook)
- [Prompt Injection](#prompt-injection)

---

## Agent Permissions

**An allow-list and deny-list that controls what an agent can do without asking for human approval each time**. Project-level permissions define safe actions (run tests, read files, standard Git operations); user-level deny lists block dangerous actions regardless of context (read .env, rm -rf, force-push to main, curl | sh).

### Key Characteristics
- Two layers: project-level allow (safe for this repo) + user-level deny (never allowed anywhere)
- Agents may try bad shortcuts when a command fails — permissions are the first safety net
- Any agent with tool access needs permissions; this is not optional

### When to Use
- Any agent deployment where tool access exists

### When NOT to Use
- Agents with no tool access — permissions have nothing to gate

### Also see
- [Agent Sandboxing](#agent-sandboxing)
- [Pre-Tool Hook](#pre-tool-hook)
- [Prompt Injection](#prompt-injection)

---

## Pre-Tool Hook

A **check that fires after the agent produces a tool call but before the tool executes** — the last safe moment to reject or transform a dangerous command. Most critical for shell (Bash) commands, where one bad command can delete files, expose secrets, or run untrusted code.

### Key Characteristics
- Timing is the defining property: post-decision, pre-execution
- Scans for: suspicious Unicode look-alikes, dangerous file paths, pipe-to-shell patterns (`curl | sh`), ANSI injection, force-destructive flags
- Hooks do not replace sandboxing — if a hook misses something, the sandbox limits blast radius

### When to Use
- Any agent with shell command access
- Whenever the agent operates on production or shared infrastructure

### When NOT to Use
- Agents limited to read-only API calls — hook overhead exceeds risk

### Also see
- [Agent Sandboxing](#agent-sandboxing)
- [Agent Permissions](#agent-permissions)
- [Prompt Injection](#prompt-injection)
- [Guardrails (AI)](#guardrails-ai)

---

## Prompt Injection

An **attack where adversarial instructions are embedded in external content** that the agent reads and follows — agent config files in cloned repos, MCP server metadata, web page content, or retrieved documents. The agent treats injected instructions as legitimate because its design goal is to follow instructions from its context.

### Key Characteristics
- Not a model vulnerability — a trust-boundary problem: the agent reads external content and cannot distinguish principal from adversarial instructions
- Threat vectors: agent config files in cloned repos, untrusted MCP servers, Unicode look-alike characters, web content injection
- Mitigation: treat agent config files like code (review before trusting); never auto-trust MCP servers from external sources; sanitize retrieved web content

### When to Use
- Any agent that reads external files, web content, or cloned repositories
- Whenever designing agent security boundaries

### When NOT to Use
- Fully air-gapped agents operating only on trusted, internally-authored content

### Also see
- [Agent Sandboxing](#agent-sandboxing)
- [Pre-Tool Hook](#pre-tool-hook)
- [Guardrails (AI)](#guardrails-ai)

---

## Pre-Commit Gate

A **set of automated checks that block a commit from entering Git history** unless all checks pass. For agentic workflows, this is more valuable than for humans — agents hit the error, read the message, fix the code, and retry without frustration. The gate becomes a teaching mechanism, not just a blocker.

### Key Characteristics
- Typical gates: secret detection, YAML validation, linter, formatter, security scanner (bandit, semgrep)
- Correction loop: agent fails → reads error → fixes code → retries → passes
- Complements CI gates — pre-commit protects local history; CI protects the shared repo

### When to Use
- Any agent that produces code and commits to version control
- When agent output quality must be verified before it enters shared history

### When NOT to Use
- Non-code agent output (reports, summaries) where Git is not the delivery mechanism

### Also see
- [Guardrails (AI)](#guardrails-ai)
- [Verification Loop (AI)](#verification-loop-ai)
- [Review Gate](#review-gate)

---

## Agent Tracing

**The structured record of an agent's full execution path** from first request to final result — every tool call, subagent invocation, input/output at each step, and model reasoning at key decision points. A tree visualization (parent → child tool calls) is more useful than a flat log for debugging.

### Key Characteristics
- Records actual behavior, not what the agent claimed it did
- Tree-structured to show causality — which step caused which sub-step
- Enables line-by-line post-mortem debugging of agent failures

### When to Use
- Debugging agent failures where the final output is wrong but the intermediate path is unknown
- Auditing agent behavior in production systems

### When NOT to Use
- Trivial single-call LLM usage where there is no multi-step path to trace

### Also see
- [Agent Metrics](#agent-metrics)
- [Agent Loop](#agent-loop)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Agent Metrics

**Quantitative signals that measure agent behavior and outcomes** — divided into proxy signals (what the agent did) and outcome signals (whether the work succeeded). Proxy signals surface problems; outcome signals are the only real measure of value.

| Metric Type | Examples | What It Shows |
|:---|:---|:---|
| **Proxy signals** | Latency, token cost, tool call count, loop iteration count, failure count | How the agent behaved |
| **Outcome signals** | Tests pass in CI, PR merged, deploy succeeded, rollback occurred | Whether the work actually succeeded |

### Key Characteristics
- "Task complete" from the agent is a claim, not an outcome signal — the agent may be wrong
- Proxy metrics catch runaway loops, stuck agents, and cost spikes
- Outcome metrics require CI/CD integration and are harder to instrument but matter more

### When to Use
- Any production agent deployment — without metrics, you cannot distinguish productive from unproductive sessions

### When NOT to Use
- One-off or exploratory agent use where the human directly observes the outcome

### Also see
- [Agent Tracing](#agent-tracing)
- [Cost Per Accepted Change](#cost-per-accepted-change)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Dual-Agent Framework

An **AI agent architecture** where two specialized agents work in tandem: one acts as a **discovery agent** ("Archaeologist") that analyzes codebases, logs, and schemas to map implicit dependencies and generate integration topology maps, while the other acts as an **adversarial testing agent** ("Shadow Adversary") that morphs production traffic to test extreme boundary conditions. A deterministic HITL (Human-In-The-Loop) validation layer gates all state mutations.

### Key Characteristics
- Agent A (Discovery): Statically analyzes artifacts (DDLs, OpenAPI specs, Kafka schemas, log traces) to produce draft integration maps
- Agent B (Adversarial): Replays morphed production traffic in a shadow environment, generating edge-case payloads traditional fuzzing would miss
- The FDE/Human acts as orchestrator and ultimate validator, not just a consumer of agent output
- State reconciliation is handled by a deterministic validation layer; LLM agents are triggered only on divergence to propose root-cause hypotheses

### When to Use
- Legacy system migrations with undocumented state transitions and zero data lineage
- High-stakes cutovers requiring 99.99%+ data-migration accuracy
- When manual debugging and test-script writing would take weeks

### When NOT to Use
- Simple migrations where source and target schemas are well-documented and aligned
- When the agent orchestration overhead exceeds the time saved — a single developer can still be faster for small, well-understood systems
- Environments where security policy prohibits replaying production data in test environments

### Also see
- [Agentic AI](#agentic-ai)
- [Agent Harness](#agent-harness)
- [Shadow Testing](resilience.md#shadow-testing)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Plan and Execute

An agent orchestration pattern where a **Planner** model first emits an immutable, structured plan (typically a Directed Acyclic Graph of execution steps in a strict JSON schema), and a separate deterministic **Executor** state machine walks through each step sequentially. Unlike raw ReAct loops, Plan & Execute separates planning from execution, enabling auditability, resumability, and prevention of infinite loop divergence.

### Key Characteristics

- **Plan-first, execute-second**: The Planner emits a DAG of steps before any tool is called; the Executor never deviates from the plan without invoking a Replanner
- **Deterministic execution engine**: Steps are walked by a state machine (e.g., LangGraph-backed), not an LLM, ensuring predictable transitions
- **Dynamic replanning on failure**: If a step fails or invalidates the plan, a Replanner node modifies the remaining DAG nodes rather than allowing an unbounded loop
- **Inner ReAct for tool interactions**: Each DAG node may spin up a lightweight, context-confined ReAct agent for mechanical tool calls, but the outer orchestration remains deterministic

### When to Use

- When building production-grade agents for Tier 1 systems where non-deterministic loops are unacceptable (e.g., financial reconciliation, compliance automation)
- When the problem space has a well-structured decomposition into discrete, verifiable steps
- When you need audit trails and resumability after failures

### When NOT to Use

- For simple, single-step tool calls where the overhead of DAG construction outweighs the benefit
- When the problem is highly exploratory and the plan cannot be determined upfront
- When latency is critical and the Planner → Executor → Replanner pipeline adds unacceptable overhead

### Also see

- [Agentic AI](#agentic-ai)
- [Agent Loop](#agent-loop)
- [ReAct (Reasoning + Acting)](#react-reasoning--acting)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Memory Fabric

A **hierarchical memory architecture** for AI agents that treats agent context like a classic computer memory hierarchy: Short-Term (in-flight execution state), Mid-Term (on-demand vector retrieval of relevant schemas/specs), and Long-Term (append-only audit logs). This keeps the active LLM context window slim and fast while providing compliance-grade traceability.

### Key Characteristics

- **Short-Term Memory (Graph State)**: Thread-safe state objects passed between orchestration nodes, holding only current execution telemetry (transaction IDs, discrepancies, tool logs)
- **Mid-Term Memory (Vector RAG)**: A retrieval layer over the enterprise catalog — the agent queries a vector database to fetch only the relevant OpenAPI specs, DDLs, or documentation needed for the current execution branch
- **Long-Term Memory (Audit Database)**: An append-only datastore (e.g., PostgreSQL) that asynchronously persists every state transition, LLM prompt token, tool payload, and internal thought trace for compliance and debugging
- **Context window optimization**: By tiering memory, the active prompt context stays lean, avoiding model degradation and astronomical token costs from dumping entire enterprise state into one window

### When to Use

- When agents operate across multiple enterprise services with large, heterogeneous data schemas
- When compliance requires full auditability of every agent decision and state transition
- When cost control on LLM token usage is a priority

### When NOT to Use

- For simple, single-domain agents with small, static context requirements
- When the added retrieval latency of mid-term vector queries outweighs the benefit
- When audit logging overhead is unacceptable for high-frequency, low-value transactions

### Also see

- [Agentic AI](#agentic-ai)
- [RAG (Retrieval-Augmented Generation)](#rag)
- [Vector Database](#vector-database)
- [Context Rot](#context-rot)

---

## ReAct (Reasoning + Acting)

An agent loop pattern that interleaves **Reasoning** (the LLM thinks about what to do next) with **Acting** (the LLM calls a tool and observes the result) in a continuous cycle. The agent generates a thought, executes a tool, ingests the observation, and repeats. While simple and flexible, raw ReAct loops are non-deterministic, prone to infinite loops under tokenization noise, and suffer from cognitive drift over long tool execution traces.

### Key Characteristics

- **Interleaved think-act-observe cycle**: Each iteration produces a reasoning trace, a tool call, and an observation that feeds into the next cycle
- **Non-deterministic**: The same input can produce different tool-call sequences across runs due to LLM stochasticity
- **Prone to loop divergence**: Under high token noise or ambiguous observations, the agent may enter infinite loops or drift away from the original goal
- **Self-correcting potential**: When wrapped with error injection (feeding stack traces back into context), ReAct agents can self-correct failed tool calls

### When to Use

- For exploratory or research tasks where flexibility is more important than determinism
- As inner execution loops within a larger deterministic orchestration (e.g., Hybrid Plan & Execute)
- When the problem space is open-ended and cannot be decomposed into a fixed plan upfront

### When NOT to Use

- For Tier 1 production systems where non-deterministic behavior is unacceptable (use Plan & Execute instead)
- When the tool execution trace is long — cognitive drift and context rot degrade reliability
- When strict auditability and reproducibility are required

### Also see

- [Agentic AI](#agentic-ai)
- [Agent Loop](#agent-loop)
- [Plan and Execute](#plan-and-execute)
- [Tool Calling](#tool-calling)

---

## Agentic Engineering

The practice of building software systems where AI agents function as non-deterministic, asynchronous co-processors within a larger deterministic enterprise architecture. Rather than treating LLMs as siloed magic boxes, agentic engineering focuses on building the **deterministic control planes, memory fabrics, and validation loops** that allow agents to operate autonomously, safely, and at enterprise scale.

### Key Characteristics

- **Deterministic wrappers around non-deterministic cores**: Type-safe schema boundaries, sandbox validation, and approval gates constrain agent outputs before they reach production
- **Cognitive distributed architectures**: Agents handle high-verifiability, low-context tactical execution; humans retain strategic judgment, architectural boundary design, and client trust interfaces
- **Compressed deployment lifecycles**: Agent-driven tooling for discovery, shadow testing, and state verification can compress multi-day refactoring efforts into hours of supervised execution
- **Role transformation**: The engineer shifts from "writer of code" to "editor of intent" — spending cognitive energy on system-level optimization rather than mechanical boilerplate

### When to Use

- When integrating AI agents into enterprise production pipelines that require safety, auditability, and determinism
- When scaling Forward Deployed Engineering teams that handle repetitive schema mapping, state reconciliation, and shadow testing
- When the goal is to compress the software development lifecycle through agent-augmented workflows

### When NOT to Use

- For quick prototypes or throwaway scripts where the overhead of validation gates outweighs the benefit
- When the team lacks the infrastructure maturity to build sandbox isolation and approval pipelines
- When the problem is purely deterministic and traditional automation (without LLMs) is simpler and more reliable

### Also see

- [Agentic AI](#agentic-ai)
- [Agent Harness](#agent-harness)
- [Agent Loop](#agent-loop)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Token Compression

A **pre-processing technique that reduces the number of tokens sent to an LLM** by applying content-type-aware compression to tool outputs, logs, and retrieval chunks before they reach the model. Unlike prompt trimming or model switching, token compression inserts a layer between the agent and the model that reduces what gets billed without changing the agent's code.

```
Agent output (10K tokens) → Type detector → Compressor → LLM receives (1.2K tokens) → billed for 1.2K
                                                                     ↓
                                                            Original cached locally
```

### Key Characteristics
- **Sits in the critical path** between the agent harness and the LLM API call
- **Content-type-aware**: JSON, code, and prose each get compressed differently
- **Non-destructive by design**: the original payload is cached and retrievable on demand
- **Transparent to agent code**: wraps the existing call path with no agent rewrite required

### When to Use
- Agent pipelines where tool outputs, logs, or RAG chunks dominate token spend
- Production workloads where 5–10× token savings on verbose inputs meaningfully reduce cost
- When model quality is limited by context noise rather than model capability

### When NOT to Use
- Short prompts where compression overhead exceeds token savings
- Workflows where every token of the original payload is genuinely needed for reasoning
- When the added latency (~tens of milliseconds) is unacceptable for real-time use cases

### Also see
- [Type-Specific Compression](#type-specific-compression)
- [Reversible Compression (LLM)](#reversible-compression-llm)
- [Token](#token)
- [Agent Harness](#agent-harness)

---

## Type-Specific Compression

A **compression strategy that routes content through separate reduction paths based on detected content type** — structural deduplication for JSON, AST-aware reduction for source code, and semantic summarization for natural-language prose. Each path is tuned for that type's information density and structural redundancy.

| Content Type | Compression Strategy | Example Reduction |
|:---|:---|:---|
| **JSON / Structured** | Collapse repeated keys, array sampling, field pruning | 10K → ~1K tokens |
| **Source Code** | Strip comments, preserve function signatures, AST-aware reduction | 5K → ~800 tokens |
| **Natural Language** | Semantic summarization, entity extraction, key-claim preservation | 3K → ~500 tokens |

### Key Characteristics
- Each compression path is independently tunable and benchmarkable
- A content-type detector gates entry to the correct compression path
- Compression quality is path-dependent — a JSON compressor misbehaves on free-form text
- Modular design allows incremental improvement of individual compressors

### When to Use
- Pipelines that handle heterogeneous content (logs + code + prose) in a single agent workflow
- When uniform compression produces uneven results across content types
- When you need to benchmark compression quality per content type independently

### When NOT to Use
- Homogeneous pipelines where a single compression strategy is sufficient
- When the added routing complexity outweighs the per-type optimization benefit
- When content types cannot be reliably detected at runtime

### Also see
- [Token Compression](#token-compression)
- [Chunking Strategy](#chunking-strategy)
- [Context Rot](#context-rot)

---

## Reversible Compression (LLM)

A **compression model where the original payload is cached locally and can be retrieved on demand by the LLM** — shifting compression from a destructive operation to a lazy-loading pattern. The model reasons over the compressed version first, requesting the full original only when the compressed form is insufficient for accurate reasoning.

```
Compressed payload → LLM reasons → Answer sufficient? → Yes → Done
                                     → No → Model requests original → Retrieve from cache → Re-reason
```

### Key Characteristics
- **Two-tier architecture**: compressed payload (tier 1) + cached original (tier 2)
- **Model-initiated retrieval**: the LLM decides when it needs more detail, triggered by ambiguous references or missing values
- **TTL-based eviction**: cached originals expire; storage cost is temporary and bounded
- **Requires model awareness**: the model must be prompted or trained to recognize when compression caused information loss

### When to Use
- High-stakes agent reasoning where compression could cause silent errors if the model confidently answers from incomplete context
- Workflows where the cost of an incorrect answer far exceeds the cost of occasional full-context retrieval
- When you need to balance token savings against accuracy guarantees

### When NOT to Use
- When the model lacks the capability to reliably detect information loss from compressed context
- For latency-critical paths where the round-trip for on-demand retrieval is unacceptable
- When cache storage costs (even temporary) exceed token savings for the expected workload

### Also see
- [Token Compression](#token-compression)
- [Type-Specific Compression](#type-specific-compression)
- [Agent Loop](#agent-loop)
- [Context Rot](#context-rot)

---

## Graph Engineering

The practice of designing **AI agent coordination as a directed graph** where nodes are specialized agents and edges are data handoffs. Graph engineering is the fourth stage in the progression: Prompts → Loops → Swarms → Graphs. Unlike scripts, graphs make parallel execution native, state persistent, and failure scoped to individual nodes rather than the entire pipeline.

```
Prompts (human is the loop)
  → Loops (script wraps prompt, fires on schedule)
    → Swarms (multiple agents, hand-written glue code)
      → Graphs (nodes=agents, edges=data handoffs, runtime coordinates)
```

### Key Characteristics
- **Nodes are agents**: Each node owns one job and passes outputs through the graph
- **Edges define data flow**: The runtime knows when to parallelize, wait, retry, or escalate
- **Parallel is native**: Seven factor agents can fire simultaneously without hand-written concurrency code
- **Node-scoped failure**: When a node breaks, the rest of the graph keeps running; you patch the broken node independently
- **State persistence**: File system as shared memory across cycles (timestamped run directories)

### When to Use
- Multi-agent systems with 4+ agents that have inter-dependencies
- Workloads that must run on a schedule (daily, hourly) with persistent state between cycles
- Systems where coordination glue code has become the primary debugging surface

### When NOT to Use
- Single-agent workloads where a simple loop suffices
- Ad-hoc, one-shot tasks that do not repeat
- Systems where agents have no dependencies and can run independently

### Also see
- [Agent Loop](#agent-loop)
- [Agentic AI](#agentic-ai)
- [Agent Harness](#agent-harness)
- [Swarm (AI Agents)](#swarm-ai-agents)

---

## Maker-Checker Pattern (AI Agents)

An **AI agent coordination pattern** that assigns generation and validation to different nodes running on different model tiers, ensuring the maker never validates its own work. The checker runs statistical gates (t-tests, bootstrap resampling, factor decomposition) that the maker cannot bypass.

### Key Characteristics
- **Maker nodes**: Run on fast, cost-effective models for data processing and construction
- **Checker nodes**: Run on stronger reasoning models for statistical validation and decomposition
- **Gate mechanism**: If check fails, the graph loops back with specific mismatch as feedback
- **Filtering effect**: ~80% of signals get rejected at validation gates — the checker processes filtered data, not raw data

### When to Use
- Quantitative or analytical pipelines where false positives are costly
- Multi-stage agent workflows requiring independent verification
- Systems where the generating model's blind spots would compound silently

### When NOT to Use
- Creative or subjective tasks where there is no objective correctness criterion
- Single-model pipelines where the cost of a second model tier is not justified
- Low-stakes generation where errors are acceptable

### Also see
- [LLM-as-Judge](#llm-as-judge)
- [Verification Loop (AI)](#verification-loop-ai)
- [Multi-Model Tier Architecture](#multi-model-tier-architecture)

---

## Loop Engineering

The practice of **wrapping AI prompts in scheduled scripts with state persistence**, enabling an agent to survive after the laptop closes. Loop engineering is Stage 2 in the Prompts → Loops → Swarms → Graphs progression. One agent, one job, running forever on a schedule.

### Key Characteristics
- **Schedule-driven**: Fires on a timer (daily, hourly) rather than on human demand
- **Stateful**: Maintains history across cycles via filesystem or database
- **Survivable**: Continues running after the developer disconnects
- **Single-agent**: One specialized agent per loop; parallelism requires Stage 3 (Swarms)

### When to Use
- Recurring analytical tasks (daily signal generation, periodic data extraction)
- Any task where the human should not need to be at the keyboard for the system to run
- First step beyond ad-hoc prompting before committing to full graph architecture

### When NOT to Use
- One-shot tasks that will never repeat
- Tasks requiring multi-agent coordination (graduate to Swarms or Graphs)
- Tasks where state persistence across cycles is not needed

### Also see
- [Graph Engineering](#graph-engineering)
- [Agent Loop](#agent-loop)
- [Swarm (AI Agents)](#swarm-ai-agents)

---

## Swarm (AI Agents)

A **collection of specialized AI agents running in parallel**, coordinated by hand-written glue code. Swarms are Stage 3 in the Prompts → Loops → Swarms → Graphs progression. Multiple agents with distinct roles (signal generation, validation, execution) work together, but coordination logic is explicit Python code rather than declarative graph edges.

### Key Characteristics
- **Role specialization**: Each agent has one job (generator, validator, executor)
- **Manual coordination**: Python glue code handles parallelism, sequencing, and error handling
- **Debugging bottleneck**: As agent count grows, the glue code becomes the primary failure surface
- **Transition point**: When debugging coordination exceeds time spent on research, graduate to Graphs

### When to Use
- 2-4 specialized agents that need parallel execution
- When you have working single-agent loops and need to add complementary roles
- Before investing in graph infrastructure — validate the multi-agent pattern first

### When NOT to Use
- Single-agent tasks (use Loops)
- 5+ agents with inter-dependencies (graduate to Graphs)
- When coordination glue code already dominates debugging time

### Also see
- [Graph Engineering](#graph-engineering)
- [Loop Engineering](#loop-engineering)
- [Agentic AI](#agentic-ai)

---

## Agent Graph

A **coordination structure where nodes are AI agents and edges define data handoffs and execution order**. The graph runtime handles parallelism, sequencing, retries, and failure isolation — the developer describes the structure once and the graph runs itself on a schedule.

### Key Characteristics
- **Declarative coordination**: Describe graph structure in plain English; runtime generates the execution code
- **Native parallelism**: Fan-out nodes run simultaneously without manual concurrency management
- **Barrier synchronization**: Sequential nodes wait for all parallel predecessors to complete
- **State persistence**: Filesystem as shared memory; each cycle reads prior cycle state
- **Budget enforcement**: Per-run cost caps with explicit transparency about enforcement level

### When to Use
- Scheduled multi-agent pipelines (daily signal generation, periodic research)
- Systems where failure in one agent should not kill the entire pipeline
- Workloads requiring different model tiers for different task complexities

### When NOT to Use
- Ad-hoc, one-shot tasks
- Simple linear pipelines without parallelism or failure isolation needs
- When the runtime infrastructure cost exceeds the value of automation

### Also see
- [Graph Engineering](#graph-engineering)
- [Multi-Model Tier Architecture](#multi-model-tier-architecture)
- [Agent Harness](#agent-harness)

---

## Multi-Model Tier Architecture

An **AI agent design pattern** that assigns different language model strengths to different agent nodes based on task complexity. Fast, cost-effective models handle data processing and construction; stronger reasoning models handle validation, decomposition, and statistical testing.

| Tier | Model Type | Typical Tasks |
|:---|:---|:---|
| **Fast** | Cost-effective (e.g., Claude Sonnet) | Data retrieval, sorting, regression, spread computation |
| **Strong** | Reasoning-heavy (e.g., Claude Opus) | Statistical testing, regime detection, factor decomposition |

### Key Characteristics
- **Task-complexity alignment**: Model strength matches node responsibility
- **Cost optimization**: Strong models only run on filtered, smaller input sets
- **Independent verification**: Different model tiers for maker vs checker prevent blind-spot compounding
- **Cost profile**: Two separate model subscriptions with distinct per-token pricing

### When to Use
- Multi-stage agent pipelines where task complexity varies significantly across nodes
- Systems where validation and quality gates must run on stronger reasoning than construction
- When cost optimization matters and not all nodes need the most expensive model

### When NOT to Use
- Uniform-complexity tasks where all nodes need the same reasoning depth
- Single-model pipelines where the operational overhead of multiple subscriptions isn't justified
- When the cost difference between tiers is negligible for the workload

### Also see
- [Maker-Checker Pattern (AI Agents)](#maker-checker-pattern-ai)
- [LLM-as-Judge](#llm-as-judge)
- [Agent Graph](#agent-graph)

---

## Context Injection

The **harness component that assembles and delivers the information an agent needs before it starts a task** — system instructions, retrieved documents, prior conversation turns, loaded skills, and any task-specific policy. Context injection determines what the model sees at the start of each turn, shaping its behavior before any tool is called.

### Key Characteristics
- **Pre-turn assembly**: All relevant context is gathered and injected before the model is invoked
- **Multi-source**: Draws from instructions, RAG retrieval, session memory, skill files, and policy documents
- **Selective**: Injects only what is relevant to the current task — over-injection causes context rot
- **Stateless by default**: Each turn starts fresh; persistence across turns requires explicit state management

### When to Use
- Any multi-turn agent where the model needs task-specific knowledge before acting
- When the agent's behavior depends on retrieved documents or prior conversation state
- When you need to inject guardrails or policy constraints before the model reasons

### When NOT to Use
- Single-call LLM usage where the prompt alone carries all needed context
- When injection overhead (RAG latency, file reads) exceeds the value of the context

### Also see
- [Agent Harness](#agent-harness)
- [Context Engineering](#context-engineering)
- [Context Rot](#context-rot)
- [RAG](#rag)

---

## Action Surfaces

The **set of external capabilities an agent is permitted to invoke** — APIs, browser control, shell access, code execution sandboxes, database connections, and MCP-style tools. Action surfaces define the boundary between what the agent can think and what it can actually do in the world.

### Key Characteristics
- **Schema-defined**: Each action surface has a typed interface (function signature, OpenAPI spec, MCP tool schema)
- **Permission-gated**: Not all surfaces are available to all agents — access is scoped by role and task
- **Observable**: Every invocation is logged with inputs, outputs, and timing for auditability
- **Bounded blast radius**: Surfaces should grant the minimum capability needed (read-only replica, not production write)

### When to Use
- Any agent that needs to act beyond text generation
- When designing the tool layer of an agent harness
- When you need to reason about what an agent can and cannot do

### When NOT to Use
- Read-only agents that only generate text — no action surfaces needed
- When a single, well-scoped tool call is simpler than a full surface abstraction

### Also see
- [Agent Harness](#agent-harness)
- [Tool Calling](#tool-calling)
- [MCP](#mcp)
- [Agent Sandboxing](#agent-sandboxing)

---

## Loop Contract

A **written specification defined before an agentic loop starts** that captures the goal, scope, verifier, state, stop condition, escalation path, and budget. The loop contract turns implicit stopping logic into an explicit, checkable agreement — preventing the pattern of discovering the stopping logic by watching the agent run forever in a terminal.

### Key Characteristics
- **Pre-defined, not discovered**: Written before the loop starts, not inferred from observing its behavior
- **Seven components**: Goal, scope, verifier, state, stop condition, escalation path, budget
- **Operator test**: If the agent cannot produce proof that it has met the contract, the loop is not done
- **Escalation-aware**: Specifies who or what gets control when the loop cannot resolve on its own

### When to Use
- Any production agentic loop where unbounded execution is unacceptable
- When multiple team members need a shared understanding of loop completion criteria
- Before deploying a loop that will run unsupervised

### When NOT to Use
- Exploratory or one-shot tasks where the stopping condition is self-evident
- Loops so simple that a contract would cost more to write than the loop costs to run

### Also see
- [Loop Engineering](#loop-engineering)
- [Agent Loop](#agent-loop)
- [Loop Viability Test](#loop-viability-test)
- [Verification Loop (AI)](#verification-loop-ai)

---

## Evidence-Based Stopping

The **core discipline of loop engineering**: stop a loop only when external, checkable evidence confirms the work is done — not when the model claims confidence. Evidence can be passing tests, valid schema output, resolvable citations, metrics above threshold, clean diffs, or human sign-off. "The agent says it's finished" is not a stopping condition.

### Key Characteristics
- **External verification**: Stopping conditions are checked outside the model, not by the model
- **Deterministic gates**: Prefer tests, schemas, and linters over model self-assessment
- **Specific feedback**: When evidence fails, the loop receives a concrete explanation of what went wrong (not just pass/fail)
- **Budget-aware**: Evidence checks are gated by cost — add verification only where the cost of a bad output exceeds the cost of checking

### When to Use
- Any agentic loop where correctness matters more than speed
- When the model's self-assessment of "done" has proven unreliable
- As a design principle for all verification loops

### When NOT to Use
- Exploratory or creative tasks where there is no objective correctness criterion
- When deterministic checks are impossible and only human judgment can determine completion

### Also see
- [Loop Engineering](#loop-engineering)
- [Verification Loop (AI)](#verification-loop-ai)
- [Loop Contract](#loop-contract)
- [LLM-as-Judge](#llm-as-judge)

---

## Structure-Aware Chunking

A **document decomposition strategy** for vector indexing that splits text along syntactic and structural document boundaries (such as paragraphs, section headers, list blocks, or Markdown headings) and maintains a calibrated sliding overlap window, rather than cutting blindly across fixed character or token counts. This ensures condition-consequence clauses, full ideas, and complete assertions remain intact within individual retrieved chunks.

### Key Characteristics
- **Structure-respecting**: Uses natural text delimiters (`\n\n`, header hierarchy, table bounds) instead of arbitrary offsets
- **Semantic integrity**: Prevents splitting conditional clauses away from their outcomes or qualifiers
- **Sliding overlap buffer**: Retains a small cross-boundary buffer (e.g. 50–100 characters) across consecutive chunks to preserve boundary context
- **Empirical quality gains**: Slashes chunk count requirements while significantly improving retrieval accuracy and human-rated answer relevance

### When to Use
- Production RAG pipelines indexing structured or formatted prose (policy documents, legal agreements, technical documentation, knowledge base articles)
- When character- or fixed-token-based chunking produces disjointed chunks that degrade retrieval precision
- To reduce total chunks needed per LLM prompt while improving answer groundedness

### When NOT to Use
- Unstructured single-line log streams, raw memory dumps, or binary blobs without document hierarchy
- Extremely short texts (e.g. single tweets or SMS) where the entire document already fits in a single chunk

### Also see
- [Chunking Strategy](#chunking-strategy)
- [Semantic Chunking](#semantic-chunking)
- [Chunk Inspection Audit](#chunk-inspection-audit)
- [RAG](#rag)

---

## Semantic Chunking

A **dynamic chunking technique** that determines document cut boundaries based on embedding distance or semantic similarity between neighboring sentences, placing split points where the semantic meaning between adjacent sentences drifts beyond a calibrated threshold.

### Key Characteristics
- **Distance-based splitting**: Computes sentence-level embeddings and splits when cosine distance exceeds a dynamic or static threshold
- **Adaptive chunk lengths**: Produces variable-sized chunks corresponding to natural topic shifts in text
- **Sensitivity to input noise**: Highly vulnerable to OCR artifacts, malformed line breaks, and missing punctuation, which cause spurious over-fragmentation
- **Requires size clamping**: Demands explicit minimum (floor) and maximum (ceiling) size constraints to prevent ultra-thin or overly bloated chunks

### When to Use
- Long-form, cleanly edited narrative essays, research papers, or transcriptions with pristine punctuation and clear topical shifts
- Scenarios where explicit document headers or paragraph breaks are absent or unreliable

### When NOT to Use
- Noisy OCR outputs, scanned PDFs, or uncleaned HTML with erratic line breaks (where simpler structure-aware paragraph chunking performs significantly better)
- Latency-sensitive ingestion pipelines where computing per-sentence embeddings adds prohibitive computational cost

### Also see
- [Structure-Aware Chunking](#structure-aware-chunking)
- [Chunking Strategy](#chunking-strategy)
- [Embedding](#embedding)
- [RAG](#rag)

---

## Chunk Inspection Audit

A **systematic qualitative debugging methodology** for RAG pipelines where engineers inspect the raw, unadorned text of retrieved chunks for failing queries sentence-by-sentence, rather than relying solely on aggregate similarity scores or reflexively migrating embedding models.

### Key Characteristics
- **Data-first diagnostics**: Focuses on whether the required factual context was fully present inside any single retrieved chunk
- **Prevents model churn**: Eliminates premature engineering cycles spent swapping embedding models when the true defect is severed chunk text
- **Failure-mode isolation**: Separates chunking defects (half-thoughts indexed) from retriever defects (wrong chunks ranked) and generation defects (hallucination despite good context)

### When to Use
- Whenever a RAG system performs poorly or hits an accuracy plateau in production despite tuning similarity thresholds
- When evaluating the top 20–50 failing queries during offline RAG evaluation cycles
- Before undertaking any embedding model migration or vector database re-indexing initiative

### When NOT to Use
- Automated real-time online query serving (use lightweight cross-encoder rerankers or retrieval validation guards for inline gating)

### Also see
- [Structure-Aware Chunking](#structure-aware-chunking)
- [RAG](#rag)
- [Guardrails (AI)](#guardrails-ai)
- [Context Engineering](#context-engineering)

---

## Context Governor

An **architectural runtime subsystem that enforces admission, retention, prioritization, and eviction policies on information entering an agent's active context window**. Rather than allowing raw tool outputs, conversational history, and retrieved documents to accumulate into an unmanaged prompt, a context governor applies explicit evaluation rules (e.g. relevance scoring, freshness decay, authority ranking, character budgets, document count limits, and contradiction detection) to construct a high-signal working context for each reasoning step.

### Key Characteristics
- **Six-policy evaluation**: Evaluates candidates against relevance, freshness, authority, specificity, traceability, and compression safety.
- **Budget enforcement**: Caps document counts and character/token limits to prevent mid-window attention degradation.
- **Stale-memory penalties**: Applies mathematical recency penalties to older retrieved passages or unverified previous turns.
- **Pre-inference gatekeeping**: Sits between retrieval/tools and the LLM generation step to ensure "governed context first, LLM second."

### When to Use
- Multi-turn operational agents (troubleshooting, customer support, coding agents) where sessions span tens or hundreds of tool calls.
- High-stakes RAG systems where contradictory or outdated documentation must not pollute reasoning.

### When NOT to Use
- Single-step stateless LLM prompts or simple conversational bots with small, clean conversation histories.

### Also see
- [Context Rot](#context-rot)
- [Context Engineering](#context-engineering)
- [Context Working Set](#context-working-set)
- [Context Pruning](#context-pruning)
- [Cognitive Debris](#cognitive-debris)
- [Agent Harness](#agent-harness)

---

## Cognitive Debris

The **accumulation of obsolete, partially relevant, superseded, or noisy information in an agent's working context** that degrades reasoning quality without causing explicit runtime exceptions or syntax crashes. Cognitive debris includes old tool outputs, expired environment assumptions, superseded intermediate plans, unverified hypotheses, and summaries that have dropped critical constraints or uncertainties.

### Key Characteristics
- **Silent degradation**: Does not trigger exceptions; instead, produces plausible-sounding but factually corrupted or obsolete answers.
- **Attention competition**: Every token of debris consumes attention bandwidth, shifting the model's output probability distribution.
- **Context landfill effect**: Arises when information enters an agent freely (via tools/retrieval) but lacks an explicit eviction or garbage-collection lifecycle.

### When to Use
- Diagnosing and mitigating drift, ungrounded confidence, or repeated obsolete actions in long-running agent workflows.

### When NOT to Use
- Stateless, single-turn prompts where context is constructed fresh on every request.

### Also see
- [Context Rot](#context-rot)
- [Context Governor](#context-governor)
- [Semantic Contamination](#semantic-contamination)
- [Context Pruning](#context-pruning)

---

## Context Working Set

The **compact, high-signal, task-aligned operational state actively maintained in an agent's prompt window at any given moment**, conceptually analogous to an operating system's virtual memory working set. The context working set contains only the current objective, confirmed facts, active constraints, validated evidence, and immediate next decisions, while offloading complete conversational transcripts, raw logs, and historical tool traces to external persistence or archive stores.

### Key Characteristics
- **Active state vs history**: Strictly separates the active operational state (what is true now) from execution history (the chronological record of past actions).
- **Just-in-Time (JIT) retrieval**: Pulls detailed historical artifacts into the working set only when explicitly required by a specific sub-task.
- **Bounded footprint**: Kept intentionally well below model context limits to maintain peak instruction-following fidelity.

### When to Use
- Architecture of long-horizon software engineering agents, autonomous troubleshooting systems, and multi-agent coordination pipelines.

### When NOT to Use
- Simple interactive chats where preserving the natural, literal dialogue stream is the primary user expectation.

### Also see
- [Context Governor](#context-governor)
- [Context Rot](#context-rot)
- [Persistent Session Memory](#persistent-session-memory)
- [Token Compression](#token-compression)

---

## Context Pruning

The **proactive removal, masking, or compaction of low-value, stale, or superseded context items from an agent's working memory before prompt assembly**. Context pruning algorithms score items by semantic relevance, apply decay penalties for age/staleness, enforce document count and character budgets, and evict non-decisive passages to prevent context bloat.

### Key Characteristics
- **Observation masking**: Hides bulky, intermediate tool execution outputs while retaining lightweight summaries or status codes.
- **Score-based eviction**: Ranks candidate context items and discards items below dynamic relevance thresholds or beyond budget ceilings.
- **Freshness discounting**: Penalizes items from earlier turns unless explicitly re-validated by recent tool confirmations.

### When to Use
- Multi-step agent loops that execute numerous shell commands, API calls, or database queries.
- Long-horizon workflows where full transcript inclusion would cause context exhaustion or attention dilution.

### When NOT to Use
- Short prompts where all historical turns fit comfortably and remain directly relevant to the current query.

### Also see
- [Context Governor](#context-governor)
- [Context Rot](#context-rot)
- [Token Compression](#token-compression)
- [Type-Specific Compression](#type-specific-compression)

---

## Semantic Contamination

A **subtle failure mode in RAG and agent systems where retrieved passages or memory fragments are semantically similar to the topic but factually irrelevant, outdated, or contradictory**, skewing the LLM's probability distribution toward plausible hallucinations. Unlike random noise, semantic contamination is especially dangerous because the model treats high-similarity text as authoritative evidence.

### Key Characteristics
- **Hard negative vulnerability**: Occurs when similarity search surfaces documents that share domain terminology (e.g. OSPF vs BGP routing incidents) but describe different entities, versions, or contexts.
- **Misplaced confidence**: The model generates fluent, authoritative explanations based on the contaminated context rather than detecting the mismatch.
- **Mitigation by classifier gating**: Requires domain routing classifiers, structured entity constraints, or cross-encoder rerankers before context admission.

### When to Use
- Designing and auditing RAG retrieval pipelines, multi-domain knowledge bases, and multi-turn agent memory architectures.

### When NOT to Use
- Systems where the knowledge base is strictly homogeneous and version-locked with zero semantic overlap across disparate domains.

### Also see
- [Context Rot](#context-rot)
- [Cognitive Debris](#cognitive-debris)
- [Context Governor](#context-governor)
- [Guardrails (AI)](#guardrails-ai)
- [Structure-Aware Chunking](#structure-aware-chunking)

---

## MoE

**Mixture of Experts** — a neural network architecture that replaces dense feed-forward network (FFN) layers with multiple parallel sub-networks called **experts**, coordinated by a parameterized gating **router**. For each incoming token, the router dynamically selects a sparse subset (e.g., top-2 or top-8 of 64+ experts) to execute, enabling models to scale total parameter count into hundreds of billions while keeping active compute per token equivalent to a much smaller dense model.

| Property | Dense Architecture | MoE Architecture |
|:---|:---|:---|
| **Parameter Usage** | 100% of parameters active per token | Sparse subset (~5–15%) active per token |
| **Compute Cost** | Scales directly with total parameter size | Scales with active parameter subset |
| **Memory Footprint** | RAM must hold active parameters (all weights) | RAM holds all weights by default, or resident core under demand paging |
| **Routing Mechanism** | Fixed static layer execution | Dynamic softmax gating / top-K routing per layer |

### Key Characteristics
- **Total vs. Active parameters**: Total parameters (e.g. 284B) provide immense model capacity and zero-shot reasoning, while active parameters (e.g. ~10B) keep token generation FLOPS low.
- **Sparse activation**: Compute is localized to selected expert sub-networks at each layer step.
- **Routing divergence**: Different tokens follow different expert execution paths dynamically.

### When to Use
- Scaling LLM capacity and knowledge density while maintaining low per-token inference latency.
- Multi-domain foundation models requiring specialized sub-network knowledge without exploding training/inference compute.

### When NOT to Use
- Ultra-small models where dense layer execution is already fast and routing overhead adds latency.
- Scenarios where fine-tuning frameworks lack multi-expert parallelization support.

### Also see
- [LLM](#llm)
- [Demand Paging for MoE Weights](#demand-paging-moe-weights)
- [Read-Compute Overlapping (Inference)](#read-compute-overlapping-inference)

---

## Demand Paging for MoE Weights

An **inference optimization technique that keeps only the core model architecture (attention, layer norms, router) resident in RAM while streaming sparse expert weight slices on demand from flash storage (SSD/NVMe/UFS)** just-in-time when selected by the router. This decouples memory capacity constraints from total model parameter count, allowing 280B+ parameter MoE models to run on 12GB RAM edge devices without compression, quantization loss, or parameter pruning.

```
Token State → In-RAM Router → Top-K Expert IDs → Stream Weight Slices from Flash Storage → Compute Layer Activations → Evict Ephemeral Buffer
```

### Key Characteristics
- **Byte-identical fidelity**: Produces exact, uncompromised mathematical results identical to running the full model resident in memory.
- **Strictly bounded RAM**: Memory usage depends only on the resident core plus the working buffer for active experts.
- **Bandwidth-bound execution**: Shifts the hardware bottleneck from RAM capacity to sequential flash storage throughput.

### When to Use
- Deploying large sparse MoE models to memory-constrained hardware (smartphones, edge appliances, developer laptops).
- Running zero-shot or complex reasoning frontier models where model accuracy cannot be sacrificed to aggressive quantization.

### When NOT to Use
- Dense architectures where all parameters are active on every token (no sparsity to exploit).
- High-throughput multi-tenant server inference where all model weights can fit into high-bandwidth GPU VRAM.

### Also see
- [MoE (Mixture of Experts)](#moe)
- [Read-Compute Overlapping (Inference)](#read-compute-overlapping-inference)
- [Token Compression](#token-compression)

---

## Read-Compute Overlapping (Inference)

An **asynchronous I/O pipelining pattern for storage-bound inference where flash storage reads for subsequent expert weights occur concurrently in the background while the CPU/GPU executes matrix computations for the current layer**. By overlapping storage transfer with compute, idle execution stalls are minimized and generation latency is improved.

| Aspect | Synchronous Weight Loading | Read-Compute Overlapping |
|:---|:---|:---|
| **I/O Handling** | Blocking reads on critical path | Background non-blocking DMA / asynchronous I/O |
| **Compute Utilization** | Compute sits idle during storage reads | Compute active while next layer's weights transfer |
| **Throughput** | Depressed (<1 tok/s on slow flash) | Higher throughput bounded only by max storage throughput |

### Key Characteristics
- **Asynchronous pipeline**: Decouples I/O prefetching threads from execution kernels.
- **Speculative prefetching**: Can speculatively fetch candidate experts based on early token state or layer lookahead.
- **Hot-expert caching**: Complemented by an LRU memory cache for frequently invoked expert weights.

### When to Use
- Storage-streamed inference architectures (e.g. BigMoeOnEdge, FlashLLM) where flash read latency dominates token time.
- Edge runtimes with multi-core CPUs where background I/O threads can run without stealing compute cycles.

### When NOT to Use
- In-memory GPU inference where all weights already reside in ultra-fast VRAM (HBM/GDDR).
- Hardware environments with single-threaded blocking storage controllers.

### Also see
- [MoE (Mixture of Experts)](#moe)
- [Demand Paging for MoE Weights](#demand-paging-moe-weights)

---

## Vector Search (ANN)

**Approximate Nearest Neighbor (ANN) vector search** is an algorithmic indexing and retrieval approach that finds the $k$ closest high-dimensional embedding vectors to a given query vector in sub-linear time ($O(\log N)$ or $O(\sqrt{N})$), sacrificing a tiny fraction of accuracy (recall) in exchange for orders-of-magnitude faster query speeds compared to brute-force exact linear scans ($O(N \cdot d)$).

```
Brute-force (Flat Exact): Check all N points ──▶ O(N * d) operations (Slow for large N)

HNSW Graph (ANN):
Layer 2: Fast highway jumps between sparse cluster centroids
Layer 1: Medium granularity navigation
Layer 0: Local dense graph traversal to nearest neighbor
──▶ O(log N) search complexity
```

### Key Characteristics
- **Graph-based and quantization algorithms**: Dominant indexing methods include **HNSW** (Hierarchical Navigable Small World graphs for high recall and microsecond latency), **IVF** (Inverted File indexing with Voronoi cells), and **PQ** (Product Quantization for extreme vector memory compression).
- **Tunable recall/latency parameter**: Retrieval accuracy (recall@k) is tuned via search parameters (e.g., `efSearch` in HNSW or `nprobe` in IVF) to trade off milliseconds for precision.
- **Normalization optimization**: When vectors are $L_2$-normalized to unit length, cosine similarity computation simplifies directly to inner product (dot product), avoiding expensive per-vector square root calculations.
- **Scalability**: Enables searching across millions to billions of vectors across vector databases (e.g., Qdrant, Milvus, Pinecone, FAISS, Azure AI Search).

### When to Use
- Semantic caching pipelines containing $>20{,}000$ cached query embeddings where linear scanning exceeds the 10–20ms latency threshold.
- RAG (Retrieval-Augmented Generation) document search over large corpus collections.
- Real-time recommendation systems, multimodal image/text retrieval, and duplicate content detection.

### When NOT to Use
- Small collections ($<10{,}000$ vectors) where exact brute-force matrix multiplication (e.g., `np.dot` / `faiss.IndexFlatIP`) is simpler, requires zero index build time, and guarantees 100% recall.
- Exact constraint matching (e.g., searching for exact IDs or strict boolean filtering without semantic ambiguity).

### Also see
- [Vector Database](#vector-database) · [Embedding](#embedding) · [RAG (Retrieval-Augmented Generation)](#rag) · [Semantic Cache](caching.md#semantic-cache)

---

## KB-Gap Detector

A **batch telemetry and data-mining system that analyzes customer support ticket resolutions to detect missing, outdated, or contradicted knowledge base (KB) documentation**. By identifying queries resolved purely via agent tribal knowledge (no KB article cited) or queries where customers escalated, the detector clusters unaddressed topics, drafts new documentation using an LLM, and surfaces them to human knowledge managers for validation and publication.

```
Resolved Tickets ──▶ Log Resolution Source (KB Article vs Agent Tribal vs Escalated)
                          │
                          ▼
Batch Clustering ──▶ Identify Frequent Clusters with Missing/Contradicted KB Articles
                          │
                          ▼
LLM Proposal     ──▶ Auto-Draft Proposed KB Article
                          │
                          ▼
Human Review     ──▶ Knowledge Manager Approves / Edits ──▶ Published to Live KB
```

### Key Characteristics
- **Feedback loop closure**: Turns daily customer support operations into an automated documentation improvement engine.
- **Asynchronous batch execution**: Runs on scheduled off-peak batches (e.g., daily or weekly) rather than blocking real-time customer request paths.
- **Human-in-the-loop publishing**: LLM generates candidate article drafts and identifies conflicting legacy documents, but human knowledge managers retain publishing authority.

### When to Use
- Customer support and service desk platforms where knowledge base decay leads to falling first-contact resolution rates.
- Enterprise RAG systems where domain knowledge rapidly evolves and manual documentation cannot keep pace with new product features or error modes.

### When NOT to Use
- Purely static, unchanging documentation corpora where all topics are already exhaustively documented.
- Real-time synchronous query routing paths (gap analysis is inherently a batch aggregate workload).

### Also see
- [RAG (Retrieval-Augmented Generation)](#rag) · [Grounding](#grounding) · [Grounding Rate](#grounding-rate)

---

## Grounding Rate

An **AI observability metric measuring the percentage of generative model outputs that are strictly grounded in verified retrieval context (citations) versus ungrounded free-form generation**. A declining grounding rate serves as an early warning signal of retrieval failures, knowledge base staleness, or prompt drift.

$$\text{Grounding Rate} = \frac{\text{Responses with Validated Context Citations}}{\text{Total Generative Responses}} \times 100\%$$

| Metric Level | Interpretation | Action Required |
|:---|:---|:---|
| **High (>95%)** | Safe; model answers strictly from verified knowledge sources | Normal operation |
| **Moderate (80–95%)** | Increased reliance on general model training data | Inspect retrieval queries and top-k thresholds |
| **Low (<80%)** | Critical trust risk; high hallucination probability | Enable strict fallback/escalation gate |

### Key Characteristics
- **Hallucination canary**: Directly correlates with factual accuracy and contractual compliance in enterprise support systems.
- **Citation validation**: Verifies that generated assertions map to specific retrieved text spans rather than generic plausibility.

### When to Use
- Continuous monitoring of enterprise RAG systems, customer support bots, and compliance-sensitive conversational agents.
- Automated evaluation pipelines (e.g., LLM-as-Judge, Ragas) during CI/CD prompt deployments.

### When NOT to Use
- Creative writing, brainstorming, or open-ended code generation tasks where external document retrieval is not expected.

### Also see
- [Grounding](#grounding) · [Hallucination](#hallucination) · [LLM-as-Judge](#llm-as-judge) · [RAG (Retrieval-Augmented Generation)](#rag)

---

## Reopen-Gated Auto-Resolution Rate

An **outcome-based customer support metric that measures the percentage of customer tickets resolved by an automated AI system without requiring human escalation or customer reopening within a defined time window (e.g., 7 days)**. Unlike naive resolution rates (which count any closed bot session), reopen-gated resolution exposes "silent failures" where customers were deflected or frustrated rather than helped.

$$\text{Reopen-Gated Auto-Resolution Rate} = \frac{\text{Tickets Resolved by Bot with No Reopen in } N \text{ Days}}{\text{Total Ingested Inquiries}} \times 100\%$$

### Key Characteristics
- **Lagged metric**: Requires an evaluation delay equal to the observation window (typically 7 to 14 days) to achieve finalized accuracy.
- **Anti-gaming defense**: Prevents support teams from artificially inflating deflection rates by prematurely closing unresolved tickets.
- **Customer satisfaction correlation**: Strongly aligns with true Net Promoter Score (NPS) and Customer Effort Score (CES).

### When to Use
- Measuring ROI and operational impact of customer-facing AI resolvers and chatbots.
- Tuning confidence escalation thresholds — balancing raw deflection against repeat contact rates.

### When NOT to Use
- Immediate, real-time alerting dashboards (use leading indicators like escalation rate and CSAT thumbs-down instead).

### Also see
- [Copilot Acceptance Rate](#copilot-acceptance-rate) · [Grounding Rate](#grounding-rate)

---

## Model Routing by Complexity

An **architectural pattern that dynamically routes incoming inference requests to different model tiers (small/fast SLMs vs large frontier reasoning models) or cache layers based on semantic query complexity, task type, and cost constraints**.

```
User Request ──▶ Complexity Classifier / Semantic Router
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
  [Exact/Semantic   [Small SLM /    [Frontier LLM /
     Cache]           Fast Tier]      Reasoning Tier]
 (Cost: $0.00)     (Cost: $0.001)    (Cost: $0.030)
 (Latency: 5ms)    (Latency: 200ms)  (Latency: 2.5s)
```

### Key Characteristics
- **Cost optimization**: Drastically reduces blended token cost (e.g., 60–80% savings) by avoiding expensive frontier models for routine FAQ queries.
- **Latency tiering**: Delivers sub-second response times for common questions while allocating latency budgets only to complex multi-step reasoning.
- **Fallback cascading**: If a smaller model outputs low confidence or fails guardrail checks, the request cascades up to the next tier.

### When to Use
- High-throughput production AI applications with bimodal query distributions (many simple queries + occasional complex investigations).
- Multi-tenant enterprise platforms where service-level tiers determine model allocation.

### When NOT to Use
- Single-purpose tasks where all queries have uniform complexity.
- Scenarios where classifier overhead exceeds the execution time/cost savings of smaller models.

### Also see
- [Multi-Model Tier Architecture](#multi-model-tier-architecture) · [Semantic Cache](caching.md#semantic-cache) · [Graceful Spend Degradation (LLM)](#graceful-spend-degradation-llm)

---

## Graceful Spend Degradation (LLM)

A **cost-governance and resilience pattern where an AI platform dynamically degrades generative features to lower-cost or zero-token fallback modes when pre-allocated monthly or hourly spending budgets approach hard limits**.

| Spend Status | Operational Mode | System Behavior | Token Cost |
|:---|:---|:---|:---|
| **Normal (<80% Budget)** | Full Generative AI | Interactive RAG generation with personalized synthesis | Standard |
| **Warning (80–95% Budget)** | Throttled / Tiered | Strict semantic caching + smaller SLM model routing | -60% |
| **Critical (>95% Budget)** | Link-Only Fallback | Returns top-3 direct KB search links (no LLM generation) | Zero ($0) |

### Key Characteristics
- **Zero-downtime cost ceiling**: Enforces strict financial boundaries without taking the underlying platform offline.
- **MVP survivability**: Leverages non-AI baseline architecture (search engines, deterministic routing) as the durable fallback tier.
- **Per-feature isolation**: Allows non-critical background features (e.g., batch article generation) to pause while preserving interactive customer-facing paths.

### When to Use
- SaaS applications offering AI capabilities with fixed subscription pricing or tight margin requirements.
- Mitigating financial denial-of-wallet (DoW) attacks or viral traffic spikes.

### When NOT to Use
- Mission-critical systems where continuous high-accuracy generative reasoning is legally or contractually mandatory regardless of cost.

### Also see
- [Model Routing by Complexity](#model-routing-by-complexity) · [Cost Per Accepted Change](#cost-per-accepted-change) · [Circuit Breaker](resilience.md#circuit-breaker)

---

## Copilot Acceptance Rate

A **productivity and telemetry metric measuring the proportion of AI-generated suggestions (code completions, support reply drafts, summaries) that human operators accept as-is, edit before sending, or discard entirely**.

$$\text{Acceptance Rate} = \frac{\text{Accepted (As-Is)} + (\alpha \times \text{Edited})}{\text{Total Generated Suggestions}} \times 100\%$$

| Category | Definition | Implication |
|:---|:---|:---|
| **Accepted As-Is** | Used without any manual modification | High relevance and tone alignment |
| **Accepted with Edits** | Modified by human before submission | Useful foundation; slight style/detail drift |
| **Discarded** | Completely rejected or overwritten | Irrelevant, incorrect, or hallucinated suggestion |

### Key Characteristics
- **Human-in-the-loop efficiency signal**: Indicates whether an AI copilot is saving operator time or creating cognitive review overhead.
- **Prompt fine-tuning feedback**: Discarded and heavily edited suggestions highlight specific categories where context retrieval or system prompts require refinement.

### When to Use
- Evaluating developer AI coding tools (Copilot, Cursor) and customer support agent assistance workbenches.
- A/B testing prompt modifications, grounding context strategies, and new foundation models.

### When NOT to Use
- Autonomous agent loops operating without direct human interaction.

### Also see
- [Human Ownership](#human-ownership) · [Review Gate](#review-gate) · [Reopen-Gated Auto-Resolution Rate](#reopen-gated-auto-resolution-rate)

---

## Generative Watermarking

An **inference-time model alignment and attribution technique** (pioneered by Google DeepMind's SynthID-Text) that embeds an imperceptible, machine-detectable statistical signature into AI-generated text or media during autoregressive token/pixel generation without degrading output quality or changing semantic meaning.

```
Context Window Tokens + Secret Key → Pseudorandom Seed → Calculate G-Values for Vocabulary → Bias Sampling Logits → Watermarked Output
```

### Key Characteristics
- **Statistical embedding**: Subtle positive bias applied to pseudo-randomly scored candidate tokens ($g$-values) across sequence steps.
- **Model-free verification**: Detectors require only the secret watermarking key $K$ and text tokenization to calculate statistical confidence ($\bar{g} > 0.5$), eliminating the need to load large model weights during verification.
- **Human-imperceptible**: Preserves natural language fluency and probabilistic diversity without injecting visible markers or fixed boilerplate tokens.
- **Statistical decay**: Detection confidence is proportional to sequence length (strongest on >100 tokens) and degrades under heavy token-level rewriting or back-translation.

### When to Use
- Complying with synthetic media transparency regulations (e.g., EU AI Act Article 50).
- Establishing provenance and attribution for enterprise generative AI outputs and customer-facing chatbots.

### When NOT to Use
- Extremely short completions (single-word, code syntax keywords) where statistical variation obscures watermark signals.
- Security boundary enforcement where adversaries control the entire transformation pipeline and can execute full structural paraphrasing.

### Also see
- [G-Value (Watermark Scoring)](#g-value-watermark-scoring) · [Content Credentials (C2PA)](#content-credentials-c2pa) · [Token](#token)

---

## Content Credentials (C2PA)

An **open industry standard (Coalition for Content Provenance and Authenticity)** for attaching cryptographically signed, tamper-evident provenance metadata manifests to digital media assets (images, audio, video, documents) detailing generation models, timestamps, editing history, and organizational attribution.

| Component | Role | Mechanism |
|:---|:---|:---|
| **C2PA Manifest** | Provenance Record | JSON-LD assertions describing asset lineage, ingredients, and tool actions |
| **Trust Anchor / Certificate** | Authenticity & Non-Repudiation | X.509 cryptographic digital signatures validating publishing entity |
| **Container Segment** | Storage & Portability | Standardized binary segments (e.g., JPEG APP11 / JUMBF boxes, MP4 moov atoms) |
| **Client Verifier** | Decentralized Audit | Client-side viewer verifying cryptographic hashes without central server dependencies |

### Key Characteristics
- **Cryptographic non-repudiation**: Verifies whether an asset was produced by an authenticated system (e.g., Google Generative AI, Anthropic Claude) and detects post-generation payload modifications.
- **Interoperable chain of custody**: Records chained edits across cooperating tools (e.g., generated in Midjourney/Gemini → retouched in Adobe Photoshop).
- **Format-dependent retention**: Stored in standard metadata segments that can be stripped or dropped by non-compliant re-encoders or image sanitization scripts.

### When to Use
- Multimodal asset provenance tracking, publisher attribution, and deepfake verification.
- Enterprise audit compliance, intellectual property protection, and copyright provenance pipelines.

### When NOT to Use
- Raw unformatted text files (JSON, plain text) that lack containerized binary metadata segments.
- Systems requiring watermark survival after aggressive metadata stripping or format conversions.

### Also see
- [Generative Watermarking](#generative-watermarking) · [Zero Trust](security-iam.md#zero-trust) · [HSM & Cryptography](hsm-cryptography.md)

---

## G-Value (Watermark Scoring)

A **pseudo-random watermark score $\in [0, 1)$ assigned to vocabulary tokens** during generative text watermarking (such as SynthID-Text), derived deterministically from a secret key and a sliding window of preceding context tokens to bias sampling selection.

$$\bar{g} = \frac{1}{N} \sum_{i=1}^{N} g(w_i) \quad \begin{cases} \bar{g} \approx 0.50 & \text{Unwatermarked Text (Uniform Distribution)} \\ \bar{g} > 0.50 & \text{Watermarked Text (Biased Sampling)} \end{cases}$$

### Key Characteristics
- **Deterministic reproducibility**: Anyone with the secret watermarking key can reconstruct the exact $g$-values for a given token sequence.
- **Hypothesis testing metric**: The sample mean $\bar{g}$ over $N$ tokens serves as a test statistic to accept or reject the null hypothesis of unwatermarked text.
- **Logit modulation**: Used during inference to tilt token probabilities toward higher-scoring tokens without truncating valid vocabulary options.

### When to Use
- Implementing and evaluating statistical watermark detectors for generative language models.
- Auditing watermarking false-positive rates and detector sensitivity across varying prompt domains.

### When NOT to Use
- Deterministic token generation modes (greedy search / temperature = 0) where sampling probability biasing is inactive.

### Also see
- [Generative Watermarking](#generative-watermarking) · [Token](#token) · [LLM](#llm)

---

## Disposable Repositories

**Ephemeral, short-lived Git repositories** created dynamically by autonomous AI coding agents or automated CI workflows for isolated experimentation, throwaway test execution, or single-turn task iterations, which are abandoned or discarded shortly after completion.

| Dimension | Persistent Enterprise Repository | Disposable Agent Repository |
|:---|:---|:---|
| **Lifecycle** | Months to years | Minutes to hours (5–60 min) |
| **Mutation Rate** | Human pacing (10s of commits/day) | Rapid automated bursts (100s of commits/hour) |
| **Storage Strategy** | Multi-node quorum replication with high-availability disks | Ephemeral local caches backed by cloud object storage WAL |
| **Decommissioning** | Deliberate archiving & compliance audit | Automated TTL-based garbage collection |

### Key Characteristics
- **Short-Lived Ephemerality**: Created on-demand for sandboxed execution without requiring permanent cluster provisioning.
- **Resource Inefficiency Under Quorum Replication**: In traditional Git hosting, allocating full 3-node replica sets for thousands of disposable repos creates severe resource waste (the "fixed floor" problem).
- **Log-First Compatibility**: Thrives in log-first storage architectures where dormant or abandoned repos reside cost-effectively in cloud object storage at zero active compute cost.

### When to Use
- **AI Coding Agent Sandboxing**: Providing isolated, dependency-clean environments for agents running speculative refactorings or code generation tasks.
- **Dynamic CI/CD Build Isolation**: Branch-per-PR ephemeral testing environments that must spin up and tear down in seconds.

### When NOT to Use
- **Monolithic Core Repositories**: Long-term enterprise codebases requiring strict compliance audit trails, permanent historical branch tracking, and multi-region read replicas.

### Also see
- [Log-First Storage Architecture](architecture-patterns.md#log-first-storage-architecture) · [Application-Level Replication](architecture-patterns.md#application-level-replication) · [Agent Harness](#agent-harness) · [Verification Loop (AI)](#verification-loop-ai)

---

## Collaborative Filtering

A recommendation algorithm paradigm that predicts a user's interest in items by collecting preferences and behavioral data (ratings, clicks, playlist co-occurrences, purchases) from many other users. It operates on the fundamental assumption that users who agreed in the past will agree in the future.

| Type | Input Signal | Advantage | Primary Challenge |
|:---|:---|:---|:---|
| **Explicit Collaborative Filtering** | 1–5 star ratings, thumbs up/down, survey reviews | High confidence of user sentiment | Extreme data sparsity (<1% rated) |
| **Implicit Collaborative Filtering** | Streams, playlist additions, page views, dwell time | Abundant, non-intrusive data volume | Ambiguity of negative signals (not streamed ≠ disliked) |

### Key Characteristics
- **Domain Independence**: Requires no metadata or deep domain knowledge about the items themselves (e.g., audio waveform or lyrics).
- **Emergent Pattern Discovery**: Captures serendipitous and contextual relationships (e.g., tracks frequently placed together in "focus study" playlists) that explicit genre taxonomy misses.
- **Sparsity & Cold-Start Susceptibility**: Fails for new items or new users with zero interaction history.

### When to Use
- Large-scale user interaction platforms (e-commerce, music streaming, social feeds) with millions of active users and rich historical interaction data.
- Generating candidate sets for personalized recommendations based on social proof and crowd behavior.

### When NOT to Use
- Day-zero launches of new items or unproven creators where interaction data is completely absent (use content-based filtering or acoustic CNN feature extraction instead).
- Niche, low-volume catalogs where user overlap is near zero.

### Also see
- [Matrix Factorization](#matrix-factorization) · [Latent Factors](#latent-factors) · [Cold-Start Problem (Recommendation Systems)](#cold-start-problem-recommendation-systems) · [Embedding](#embedding)

---

## Matrix Factorization

A class of collaborative filtering algorithms that decomposes a large, sparse user-item interaction matrix into the product of two lower-dimensional dense matrices representing **latent factor embeddings** for users and items.

| Algorithm | Optimization Approach | Best Suited For | Scalability |
|:---|:---|:---|:---|
| **SVD / SVD++** | Gradient Descent (SGD) minimizing squared error | Explicit ratings (Netflix Prize style) | Moderate (single-node or distributed SGD) |
| **Implicit ALS (Alternating Least Squares)** | Convex optimization alternating between user and item matrices | Large-scale implicit feedback (streams, clicks) | Extremely high (embarrassingly parallel on Spark/Ray) |
| **BPR (Bayesian Personalized Ranking)** | Pairwise ranking optimization | Personalized top-N item ranking | High |

### Key Characteristics
- **Dimensionality Reduction**: Projects massive, millions-wide sparse matrices into compact $k$-dimensional latent vectors ($k \approx 50\text{–}300$).
- **Latent Factor Discovery**: Uncovers hidden mathematical dimensions (e.g., acoustic energy, era vibes, contextual mood) without manual tagging.
- **Geometric Proximity**: Recommendation reduces to an efficient inner product ($\hat{r}_{ui} = \vec{u}_u^T \vec{v}_i$) or cosine distance search in latent space.

### When to Use
- Recommender systems processing hundreds of millions of user-item interactions where scalable dimensionality reduction is necessary.
- Offline batch recommendation pipelines pre-computing latent embeddings for large catalogs.

### When NOT to Use
- Dynamic, real-time context-heavy sessions where user intent shifts rapidly within seconds (use sequential/session-based transformers instead).
- Datasets where item content (text, audio, images) is the only available signal.

### Also see
- [Collaborative Filtering](#collaborative-filtering) · [Latent Factors](#latent-factors) · [Vector Search (ANN)](#vector-search-ann)

---

## Cold-Start Problem (Recommendation Systems)

The structural failure mode in recommendation engines where the system cannot draw inferences or generate reliable recommendations for entities (users or items) that have **insufficient historical interaction data**.

| Variant | Constraint | Primary Mitigation Strategy |
|:---|:---|:---|
| **Item Cold-Start** | Brand-new items have 0 views, 0 streams, 0 purchases | Content-based feature extraction (Audio CNNs, NLP text embeddings, image embeddings) |
| **User Cold-Start** | New users have 0 clicks, 0 history, no profile | Onboarding preference quiz, demographic defaults, popularity-based exploration |
| **System Cold-Start** | Brand-new platform launch with no users or logs | Knowledge graphs, rule-based heuristics, curated editorial seeds |

### Key Characteristics
- **Sparsity Barrier**: Collaborative filtering algorithms rely entirely on historical co-occurrences and collapse when column/row vectors are all zeros.
- **Exploration vs. Exploitation Dilemma**: The system must allocate traffic to unproven items (exploration) to gather data without degrading overall user experience (exploitation).
- **Multi-Modal Triangulation**: Robust architectures bridge cold starts by cascading from raw media content (audio/text) to cultural NLP, and finally to collaborative filtering as data matures.

### When to Use
- Designing fallback pipelines and multi-signal routing strategies for user onboarding and item ingestion workflows.

### When NOT to Use
- Catalogs with fully static inventories where all items and users have dense historical interactions.

### Also see
- [Collaborative Filtering](#collaborative-filtering) · [Acoustic Feature Extraction](#acoustic-feature-extraction) · [Embedding](#embedding)

---

## Acoustic Feature Extraction

The process of extracting dense numerical representations and acoustic signatures (tempo, musical key, harmonic structure, timbre, loudness, energy) directly from raw audio waveforms using signal processing and deep convolutional neural networks (CNNs).

| Method | Input Format | Extracted Features | Primary Advantage |
|:---|:---|:---|:---|
| **DSP / Fourier Transform (STFT)** | Time-domain audio (.wav / .mp3) | Mel-spectrograms, MFCCs, Chroma vectors | Deterministic, zero model training needed |
| **Deep Audio CNN** | 2D Mel-Spectrogram image | Latent acoustic embeddings, genre/mood logits | Captures complex multi-layered acoustic patterns |
| **Self-Supervised Audio Transformers** | Raw audio waveforms | High-dimensional contextual audio embeddings | Generalizes across cross-genre acoustic styles |

### Key Characteristics
- **Zero-History Content Analysis**: Operates strictly on the physical audio waveform, making it completely independent of user engagement or social metadata.
- **2D Visual Analogy**: Mel-spectrograms represent frequency over time as 2D matrices, enabling standard Computer Vision architectures (ResNet, ConvNet) to process audio.
- **Latent Space Projection**: Trained to project acoustic vectors directly into the same latent space used by collaborative filtering models.

### When to Use
- Solving the item cold-start problem for newly ingested music, podcasts, or sound clips.
- Audio similarity search, genre classification, and audio fingerprinting.

### When NOT to Use
- Text-only or metadata-rich domains where textual NLP or interaction graphs provide higher-fidelity social signals.

### Also see
- [Cold-Start Problem (Recommendation Systems)](#cold-start-problem-recommendation-systems) · [Embedding](#embedding) · [Vector Database](#vector-database)

---

## Latent Factors

Abstract, unobserved mathematical dimensions discovered by dimensionality reduction and matrix factorization algorithms that capture underlying patterns, affinities, and relationships in high-dimensional data.

| Property | Manifest (Observable) Features | Latent (Hidden) Factors |
|:---|:---|:---|
| **Definition** | Explicit attributes (e.g., Genre: Jazz, BPM: 120, Year: 1975) | Mathematical coordinates discovered through matrix decomposition |
| **Interpretability** | Human-readable and intuitive | Abstract linear combinations (e.g., Factor 47 captures "acoustic melancholia") |
| **Dimensionality** | High and sparse (millions of tags) | Low and dense (typically 50–300 continuous floats) |
| **Computation** | Manual tagging or rule-based parsing | Unsupervised or self-supervised matrix optimization |

### Key Characteristics
- **Implicit Semantic Capture**: Latent factors naturally discover nuanced contextual groupings that humans feel but rarely tag explicitly.
- **Dense Vector Arithmetic**: Enables vector addition, cosine similarity, and algebraic taste operations (e.g., $\vec{v}_{\text{user}} - \vec{v}_{\text{pop}} + \vec{v}_{\text{indie}}$).
- **Noise Reduction**: Filtering out low-variance dimensions acts as a regularizer, removing idiosyncratic noise from sparse interaction matrices.

### When to Use
- Recommender systems, topic modeling (LDA), dimensionality reduction (PCA/SVD), and collaborative filtering embeddings.

### When NOT to Use
- Systems requiring strict explainability and regulatory compliance where every decision parameter must be explicitly human-auditable.

### Also see
- [Matrix Factorization](#matrix-factorization) · [Collaborative Filtering](#collaborative-filtering) · [Embedding](#embedding)

---

## Vibe Coding

An AI-assisted development workflow in which a developer accepts generated code with minimal specification, verification, or understanding of the implementation. It is useful for low-stakes prototypes but does not provide the controls required for production correctness.

### Key Characteristics
- **Prompt-and-accept flow**: The developer asks for a change, runs the result, and feeds failures back to the model.
- **Low upfront cost**: Little specification or evaluation infrastructure is required.
- **Verification boundary**: Without deterministic tests and trajectory evaluation, sophisticated tooling can still be vibe coding.

### When to Use
- Low-risk prototypes, experiments, and disposable tools where production correctness and long-term maintenance are not primary constraints.

### When NOT to Use
- Payment, authentication, healthcare, data integrity, or other production workflows where failures are costly or difficult to detect.

### Also see
- [Agentic AI](#agentic-ai) · [Verification Loop (AI)](#verification-loop-ai) · [Technical Deflation](#technical-deflation)

---

## Trajectory Evaluation

Evaluation of the sequence of reasoning and tool-use steps an agent took, in addition to checking whether its final output is correct. It detects unsafe assumptions, unnecessary actions, or process failures that can be hidden by a correct result.

### Key Characteristics
- **Path-aware**: Reviews tool calls, intermediate decisions, and state transitions.
- **Complementary**: Does not replace deterministic tests of the final artifact.
- **Diagnostic**: Helps identify where an agent diverged before the final failure or accidental success.

### When to Use
- Production coding agents, long-running workflows, and high-impact tasks where the path matters as much as the result.

### When NOT to Use
- Simple, deterministic transformations whose complete behavior is already covered by cheap automated tests.

### Also see
- [Verification Loop (AI)](#verification-loop-ai) · [Agent Tracing](#agent-tracing) · [Evidence-Based Stopping](#evidence-based-stopping)

---

## Agent Skills

Structured, portable packages of procedural knowledge that an agent loads when a task matches their trigger conditions. Skills keep specialized instructions, constraints, examples, and verification rules out of the universal system context until they are needed.

### Key Characteristics
- **On-demand loading**: Specialized knowledge is retrieved for relevant tasks rather than injected into every request.
- **Explicit triggers**: A skill declares when it applies and what behavior it governs.
- **Versioned procedure**: The package can be reviewed and changed independently of the base agent prompt.

### When to Use
- Agents serving multiple domains or repositories with distinct workflows, policies, and technical conventions.

### When NOT to Use
- A single stable instruction that applies to every task and is cheaper and clearer to keep in the base context.

### Also see
- [Context Engineering](#context-engineering) · [Workflow Files](#workflow-files) · [Agent Harness](#agent-harness)



