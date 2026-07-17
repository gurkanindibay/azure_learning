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

**Performance degradation when key content falls in mid-window positions** of an LLM's context. Also known as the **"Lost in the Middle"** phenomenon (Stanford research): models attend strongly to beginning and end of context, but mid-window content is effectively invisible. Even million-token windows suffer instruction-following degradation as context grows — 30%+ performance drops are documented.

| Mitigation | Mechanism |
|:---|:---|
| Compaction | Summarize history; preserve architectural decisions, discard redundant outputs |
| Observation Masking | Hide old tool outputs while keeping tool calls visible |
| JIT Retrieval | Load data dynamically via search rather than full-file reads |
| Sub-Agent Delegation | Subagents return 1,000–2,000 token condensed summaries |

**When to use**: Multi-turn agents, long-running tasks, context-heavy workflows.  
**When NOT to use**: Single-call LLM usage, short conversations.  
**Also see**: [Agent Harness](#agent-harness), [LLM](#llm), [Token](#token)

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
- [agentic-11 in system-design-architecture](../system-design-architecture/50-agentic-two-track-workflow-key-takeaways.md#agentic-11-two-track-workflow--attention-weighted-parallelism)

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
- [agentic-11 in system-design-architecture](../system-design-architecture/50-agentic-two-track-workflow-key-takeaways.md#agentic-11-two-track-workflow--attention-weighted-parallelism)

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
- [agentic-19 in system-design-architecture](../system-design-architecture/57-agentic-loop-engineering-key-takeaways.md#agentic-19-loop-viability-test--four-conditions)

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
- [agentic-20 in system-design-architecture](../system-design-architecture/57-agentic-loop-engineering-key-takeaways.md#agentic-20-loop-build-order--prove-before-scheduling)

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
- [agentic-21 in system-design-architecture](../system-design-architecture/57-agentic-loop-engineering-key-takeaways.md#agentic-21-cost-per-accepted-change--the-loop-efficiency-metric)

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
- [agentic-17 in system-design-architecture](../system-design-architecture/57-agentic-loop-engineering-key-takeaways.md#agentic-17-verify-gate--the-heart-of-the-loop)

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
