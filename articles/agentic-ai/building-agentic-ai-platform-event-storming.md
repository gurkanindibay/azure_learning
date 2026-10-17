---
type: Article
title: "Building an Agentic AI Platform to Facilitate Event Storming Sessions"
description: "Iterative development of a multi-agent AI platform (StormSpace) that autonomously facilitates Event Storming sessions — from a single chat agent through to a customisable orchestrated subagent system."
generated: { by: process:format-agent, at: 2026-10-13T22:56:00+03:00 }
---

# Building an Agentic AI Platform to Facilitate Event Storming Sessions

> **Author**: Matt Bentley
> **Published**: 2026-10-12
> **Source**: [Medium — gitconnected](https://medium.com/gitconnected/building-an-agentic-ai-platform-to-facilitate-event-storming-sessions-590f1d528ecb)
> **Related**: [System Design → Agentic AI](../../system-design-architecture/agentic-ai/42-agentic-key-takeaways.md)
> **Tags**: agentic-ai, event-storming, multi-agent, orchestrator, domain-driven-design, autonomous-agent, .net

---

## Table of Contents

- [Overview](#overview)
- [Event Storming Basics](#event-storming-basics)
- [StormSpace — The Application](#stormspace--the-application)
- [AI Agents](#ai-agents)
- [Iterative Development Process](#iterative-development-process)
  - [Iteration 1: Single Agent Assistant](#iteration-1-single-agent-assistant)
  - [Iteration 2: Single Agent Autonomous Facilitator](#iteration-2-single-agent-autonomous-facilitator)
  - [Iteration 3: Context-Driven System Prompt](#iteration-3-context-driven-system-prompt)
  - [Iteration 4: Agentic (Multi-Agent) Facilitator](#iteration-4-agentic-multi-agent-facilitator)
  - [Iteration 5: Extended Agent Integration Options](#iteration-5-extended-agent-integration-options)
  - [Iteration 6: Customisable Agentic Platform](#iteration-6-customisable-agentic-platform)
- [Key Lessons](#key-lessons)

---

## Overview

Event Storming (ES) is a collaborative technique for modelling complex software systems. The prescriptive process produces a high barrier to entry — skilled facilitators are scarce. LLMs understand both software architecture and ES deeply, making them ideal facilitators.

This article documents six iterative design cycles that transformed a basic chat assistant into a fully autonomous, customisable multi-agent facilitation platform built on top of the **StormSpace** collaborative whiteboard application.

---

## Event Storming Basics

Event Storming is structured around a sequence of five phases, each modelled with sticky-note types:

| Note Type | Colour | Meaning |
|:---|:---|:---|
| Event | Orange | Something that happened in the past (e.g., *Item Added to Basket*) |
| Command | Blue | What triggered the event (automated or manual) |
| User Role | Yellow (small) | Actor who issued a manual command |
| Policy | Pink | Business rules / logic following an event |
| Concern | Red | Open questions to revisit |
| Aggregate | Yellow | Data structures responsible for consistency |

**Phases**:

1. **Set Context** — Define domain boundary, business goal, actors, and session scope.
2. **Identify Events** — Brainstorm past-tense domain events, arrange chronologically.
3. **Add Commands & Policies** — Identify triggers and resulting business rules.
4. **Define Aggregates** — Group behaviour around core domain objects.
5. **Break It Down** — Identify bounded contexts, subdomains, and integration boundaries.

> The ES approach forces teams to focus on **behaviour first** and data models last — a deliberate inversion of the common (flawed) instinct to start with a schema.

---

## StormSpace — The Application

StormSpace is a real-time collaborative web app for running ES sessions:

- **Frontend**: HTML canvas for sticky-note manipulation
- **Backend**: ASP.NET + SignalR for real-time multi-user board updates
- **Persistence**: Event Sourcing — all board actions are stored as an event stream, enabling full history replay and undo

### Five Guided Phases

StormSpace guides each board through all five ES phases with phase-aware tooling and state tracking.

---

## AI Agents

> An AI agent is an AI component that can independently decide what actions to take and use connected tools to achieve a user-provided goal.

Key building blocks:

- **System Prompt** — defines role, behaviours, and guardrails
- **Tools** — custom functions exposed to the agent (read/write board operations, phase transitions, etc.)
- **LLM** — the underlying reasoning model

### Custom Toolbox

StormSpace exposes its existing business logic as agent tools (via the Microsoft Agent Framework — MAF):

- `GetBoardState` / `GetRecentEvents`
- `CreateNote`, `MoveNote`, `EditNote`, `DeleteNote`
- `CompleteAutonomousSession`
- `DelegateToAgent`, `AskQuestion`, `RequestBoardReview`

MAF handles tool-to-LLM plumbing, message routing, and inter-agent communication in .NET.

---

## Iterative Development Process

### Iteration 1: Single Agent Assistant

**Goal**: Validate that a single agent can orchestrate the StormSpace toolbox within an ES context.

**Approach**: One MAF agent, all tools, GPT-5.6 Terra, a long system prompt defining the facilitator persona. Tool-call progress was surfaced to the UI in real time via SignalR events.

**Result**: Impressive out-of-the-box. The agent managed board state correctly and adopted the inquisitive facilitator persona.

**Lesson**: A basic single-agent assistant proves viability quickly.

---

### Iteration 2: Single Agent Autonomous Facilitator

**Goal**: Have the agent act autonomously — initiating turns without being prompted.

**Trigger conditions** (whichever fires first):

- **User Activity Debounce**: board change → 30 s of inactivity
- **Timer**: 3 minutes since the previous agent turn

**Autonomous prompt template**:

```
[AUTONOMOUS_FACILITATOR_LOOP]
Autonomous facilitator loop trigger: { userActivityDebounce | timer}.
Review the board and recent activity before acting.

- Call GetRecentEvents as well as GetBoardState so you can tell whether a phase has just started or changed.
- Ask at most one concise question or perform one small facilitation move.
- When a phase has just started, you may perform a small starter demonstration example.
- Autonomous facilitation must not delete existing notes or connections.
- If there is nothing meaningful to add right now, do not call any tools and return an empty response.
- If the workshop is clearly complete, use the CompleteAutonomousSession tool.
```

**Implementation**: Background thread in the StormSpace API — simple to host for small scale; should be a separate process for scale-out.

**Lesson**: Autonomous triggering that mirrors a human facilitator's cadence is the key differentiator.

---

### Iteration 3: Context-Driven System Prompt

**Problem**: As boards grew, the agent hallucinated and missed key concepts. The monolithic system prompt (covering all 5 phases) was too long for complex, domain-rich boards.

**Solutions**:

- **Phase-Specific Instructions** — system prompt includes rules only for the *current* ES phase, reducing cognitive load on the model.
- **Custom Board Context** — teams configure domain-specific context (vocabulary, rules) per board; injected into the system prompt at runtime.

**Lesson**: A dynamic, phase-scoped system prompt dramatically improves accuracy on complex domains. Context injection of domain knowledge compensates for niche vocabulary that the LLM doesn't know.

---

### Iteration 4: Agentic (Multi-Agent) Facilitator

**Problem**: The single agent was doing too much simultaneously — architecture guidance, facilitation, explanation, board manipulation, review, cleanup, demonstrations, and domain advice. AI agents perform best with a single focused role.

**Solution**: Orchestrated subagent pattern:

```
Facilitator (Orchestrator)
    └── DelegateToAgent ──→ Specialist Subagents
                              ├── Board Manager
                              ├── Reviewer
                              ├── Demonstrator
                              └── Explainer
```

Custom `DelegateToAgent` tool — the Facilitator decides which agent to delegate to based on the task.

Each subagent has:
- Its own focused system prompt
- A limited tool set (only what it needs)
- Phase activation configuration (active only in relevant phases)
- An independently chosen LLM — cheaper/faster models (GPT-5.6 Luna) could replace Terra for most subagents.

**Lesson**: Decomposing roles across specialised subagents improves quality, reduces latency, and lowers cost. The orchestrated subagent pattern scales naturally to complex domains.

---

### Iteration 5: Extended Agent Integration Options

**Problem**: Domain-expert responsibilities were still mixed into phase-managing agents.

**Solution**: Dedicated **Domain Expert** agent:

- Read-only tool access (cannot manipulate boards)
- Other agents call `AskQuestion` to request domain guidance before making board changes
- `RequestBoardReview` tool allows any agent to ask a specialist to review specific areas

**Result**: Agents converse and collaborate, just as human participants would in an ES session. This emergent behaviour arises naturally from the tool architecture.

**Lesson**: Separating domain knowledge (read-only) from board manipulation (write) agents enables safe, expert-informed collaboration. `AskQuestion` and `RequestBoardReview` are powerful coordination primitives.

---

### Iteration 6: Customisable Agentic Platform

**Goal**: Surface agent configuration to end users so they can tune the platform for their domain.

**Capabilities exposed to users** (per board):
- System prompt per agent
- Tool set per agent per ES phase
- Integration patterns (Delegate, AskQuestion, Review)
- Agent roster (add/remove agents)

**Example use case**: For a particularly complex domain, split the Domain Expert into role-specific agents — Software Architect, Risk Manager, Accountant, Warehouse Manager.

**Result**: A fully customisable agentic platform that adapts to any domain complexity.

**Lesson**: Exposing agent configuration to power users enables them to build the optimal agentic behaviour for their specific context — without requiring engineering involvement.

---

## Key Lessons

| # | Lesson |
|:---|:---|
| 1 | Prove viability with a single agent before adding complexity |
| 2 | Autonomous triggers modelled on human facilitator behaviour are the key differentiator |
| 3 | Phase-scoped system prompts reduce hallucination on complex boards |
| 4 | Custom domain context injected at runtime compensates for niche vocabulary |
| 5 | Multi-agent decomposition by role improves quality, speed, and cost simultaneously |
| 6 | A dedicated read-only Domain Expert agent prevents knowledge-driven errors without risk |
| 7 | Exposing agent configuration to super-users unlocks domain-specific optimisation |
| 8 | Building agentic systems is hard — even frontier models have limitations; granular roles are the lever |

---

> **Source code**: [GitHub — matt-bentley/StormSpace](https://github.com/matt-bentley/StormSpace)
> **Dictionary**: [Event Storming](../../reference-dictionary/cqrs-event-driven.md#event-storming) · [Orchestrated Subagent Pattern](../../reference-dictionary/ai-ml-llm.md#orchestrated-subagent-pattern) · [Phase-Specific System Prompt](../../reference-dictionary/ai-ml-llm.md#phase-specific-system-prompt) · [Domain Expert Agent](../../reference-dictionary/ai-ml-llm.md#domain-expert-agent) · [Autonomous Facilitator Loop](../../reference-dictionary/ai-ml-llm.md#autonomous-facilitator-loop)
