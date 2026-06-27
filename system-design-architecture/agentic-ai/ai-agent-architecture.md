---
type: System Design
title: "AI Agent Architecture — Key Takeaways"
description: "User Request"
timestamp: 2026-06-14T00:00:00Z
---

# 21. AI Agent Architecture — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)  
> **Source**: [Hap Bilgi 15: AI Agent Mimarisi — Bir Yapay Zekâ Ajanı Nasıl Çalışır?](../../articles/linkedin/llm-agents.md)  
> **Also see**: [AI/ML Infrastructure](11-ai-ml-infrastructure.md), [Agentic AI — Enterprise Strategic Systems](17-agentic-ai-enterprise-strategic-systems.md)  
> **Taxonomy Reference**: §12 AI Applications

---

## Contents

- [agentarch-01: Brain — LLM as Decision Maker](#agentarch-01-brain--llm-as-decision-maker) — Chatbots generate text; agents generate decisions
- [agentarch-02: Planning — Task Decomposition](#agentarch-02-planning--task-decomposition) — Chain of Thought, Tree of Thoughts, ReAct, Reflexion
- [agentarch-03: Tools — External World Interaction](#agentarch-03-tools--external-world-interaction) — Tool calling ecosystem: APIs, code execution, browsers, MCP
- [agentarch-04: Memory — Short-Term & Long-Term](#agentarch-04-memory--short-term--long-term) — Context window vs vector databases and RAG
- [agentarch-05: Agent Loop — Continuous Decision Cycle](#agentarch-05-agent-loop--continuous-decision-cycle) — Perceive → Think → Plan → Act → Evaluate → Repeat
- [agentarch-06: Guardrails — Safety & Control Layer](#agentarch-06-guardrails--safety--control-layer) — Human-in-the-loop, sandboxing, cost limits, output validation

---

## agentarch-01: Brain — LLM as Decision Maker

> **Source**: [Article §"1. Brain (Beyin)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | Traditional chatbots only produce text — they can't decide **what action to take next** |
| **Root cause** | LLMs used as text generators rather than decision orchestrators |

### Chatbot vs Agent

| Aspect | Chatbot | AI Agent |
|:---|:---|:---|
| **Output** | Text response | Action decision |
| **Flow** | One-shot: prompt → response | Multi-step: perceive → decide → act → loop |
| **External world** | No interaction | Tools, APIs, code execution |
| **Role** | Text generator | Orchestrator |

**Strategy — The LLM as an orchestrator**:

```
User Request
    ↓
Analyze Intent
    ↓
Decide Next Action
    ↓
Create/Update Plan
```

The LLM evaluates the current state, decides which tool to invoke (or whether to replan), and produces structured decisions — not just free-form text.

> **Azure**: Azure OpenAI Service with function calling; Semantic Kernel for orchestration.

---

## agentarch-02: Planning — Task Decomposition

> **Source**: [Article §"2. Planning (Planlama)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | Real-world problems cannot be solved in a single step — naive agents fail on multi-step tasks |
| **Root cause** | No decomposition mechanism; the agent tries to answer complex queries directly |

### Planning Techniques

| Technique | Mechanism | Best For |
|:---|:---|:---|
| **Chain of Thought (CoT)** | Step-by-step reasoning in the prompt | Linear reasoning problems |
| **Tree of Thoughts (ToT)** | Branching exploration of multiple reasoning paths | Problems with multiple solution paths |
| **ReAct** | Interleaved Reasoning + Acting | Tasks requiring tool use + reasoning |
| **Reflexion** | Self-evaluation + verbal reinforcement learning | Iterative improvement from failures |

### Decomposition Example

```
"What's the weather?"
    ↓
Determine location
    ↓
Call weather API
    ↓
Process result
    ↓
Generate response
```

> **Azure**: Azure AI Agent Service with built-in planning; Semantic Kernel planners (Stepwise, Sequential). | **Taxonomy**: §12 AI Applications

---

## agentarch-03: Tools — External World Interaction

> **Source**: [Article §"3. Tools (Araçlar)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | An LLM alone cannot access the internet, run code, query databases, or touch the file system |
| **Root cause** | LLMs are stateless text models with no I/O beyond the prompt |

### Tool Calling Flow

```
LLM
    ↓
Tool Call (structured decision)
    ↓
API / Browser / Python / SQL
    ↓
Result
    ↓
LLM (processes result, decides next step)
```

### Tool Ecosystem

| Tool | Capability | Use Case |
|:---|:---|:---|
| **Web Search** | Real-time internet access | Current events, fact-checking |
| **REST API** | External service integration | CRM, payment, weather, notifications |
| **Python** | Code execution | Data analysis, calculations, file processing |
| **File System** | Read/write local files | Document processing, report generation |
| **SQL Database** | Structured data queries | Analytics, lookup, CRUD operations |
| **Browser Automation** | Web interaction | Form filling, scraping, UI testing |
| **Function Calling** | Native LLM-to-code bridge | Structured tool invocation |
| **MCP Server** | Standardized tool protocol | Cross-provider tool interoperability |

> The real power of modern AI Agents is not just the model — it's the **tool ecosystem** they can leverage.

> **Azure**: Azure Functions for custom tools; Logic Apps connectors; MCP servers on Azure Container Apps.

---

## agentarch-04: Memory — Short-Term & Long-Term

> **Source**: [Article §"4. Memory (Hafıza)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | An agent that starts every conversation from scratch is inefficient and frustrating |
| **Root cause** | Stateless LLMs have no built-in persistence across sessions |

### Two-Tier Memory Architecture

| Type | Storage | Scope | Mechanism |
|:---|:---|:---|:---|
| **Short-Term** | Context Window | Active conversation | Direct prompt injection; older messages summarized to preserve context |
| **Long-Term** | External store | Persistent knowledge | Vector DB, RAG, knowledge base, user preferences, documents |

### Short-Term Memory Flow

```
User Message
    ↓
Conversation Context (sliding window)
    ↓
LLM
```

When the conversation grows too long, older content is summarized to maintain context within token limits.

### Long-Term Memory Stores

- User preferences and history
- Documents and knowledge base
- Vector database (semantic search)
- RAG retrieval pipeline
- Enterprise data sources

> The agent retrieves relevant long-term memory on demand — it doesn't load everything into every prompt.

> **Azure**: Azure Cosmos DB for state; Azure AI Search (vector + hybrid); Azure Cache for Redis for session state. | **Also see**: [ai-01: RAG Architecture](11-ai-ml-infrastructure.md#ai-01-rag-architecture--stopping-ai-hallucinations)

---

## agentarch-05: Agent Loop — Continuous Decision Cycle

> **Source**: [Article §"5. Agent Loop (Karar Döngüsü)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | A single-response model stops after one answer — it cannot iterate toward a goal |
| **Root cause** | Chatbots are stateless request-response; agents need a stateful decision loop |

### The Agent Loop

```
Perceive State
    ↓
Think (evaluate)
    ↓
Plan (decompose)
    ↓
Use Tool (act)
    ↓
Evaluate Result
    ↓
Goal Complete?
    ├── No → Loop back to Perceive
    └── Yes → Generate final answer
```

> Think of an AI Agent as an **intelligent `while` loop**: it keeps deciding and acting until the goal is met.

### Key Properties

| Property | Description |
|:---|:---|
| **Stateful** | Maintains context across iterations |
| **Goal-oriented** | Doesn't stop until the objective is met or a termination condition triggers |
| **Self-correcting** | Evaluates tool results; can replan on failure |
| **Bounded** | Guardrails enforce max iterations, cost, and time limits |

> **Azure**: Azure AI Agent Service orchestrates the loop; Durable Functions for long-running agent workflows.

---

## agentarch-06: Guardrails — Safety & Control Layer

> **Source**: [Article §"6. Guardrails (Kontrol ve Güvenlik Katmanı)"](../../articles/linkedin/llm-agents.md)

| | |
|:---|:---|
| **Problem** | More agent autonomy → more risk: bad API calls, runaway costs, security breaches |
| **Root cause** | Agents given unrestricted authority without safety boundaries |

### Guardrail Categories

| Guardrail | Mechanism | Prevents |
|:---|:---|:---|
| **Authorization** | Scope verification per action | Unauthorized API calls |
| **Human-in-the-Loop** | Approval gate for critical actions | Irreversible damage |
| **Output Validation** | Schema/constraint checks on agent output | Malformed actions |
| **Token Limit** | Max tokens per turn/session | Runaway context growth |
| **Cost Limit** | Budget cap per session/month | Unbounded spending |
| **Sandbox** | Isolated execution environment | System compromise |
| **Sensitive Data Filtering** | PII/secret redaction | Data leakage |

### Why Guardrails Matter

A misconfigured agent can:
- Generate unnecessary costs (unbounded API calls)
- Make incorrect API calls to critical systems
- Execute unexpected operations in production environments

> In enterprise AI systems, the guardrail layer is often **as important as the model itself**.

> **Azure**: Azure AI Content Safety; Azure API Management policies; Azure Policy for resource governance.

---

## The AI Agent Formula

```
AI Agent = LLM + Planning + Tools + Memory + Loop + Guardrails
```

| Component | Role | Azure Implementation |
|:---|:---|:---|
| **Brain (LLM)** | Decision maker | Azure OpenAI Service + function calling |
| **Planning** | Task decomposition | Semantic Kernel planners, Azure AI Agent Service |
| **Tools** | External interaction | Azure Functions, Logic Apps, MCP servers on Container Apps |
| **Memory** | Short-term + long-term state | Cosmos DB, Azure AI Search (RAG), Cache for Redis |
| **Agent Loop** | Continuous decision cycle | Azure AI Agent Service, Durable Functions |
| **Guardrails** | Safety and control | AI Content Safety, API Management, Azure Policy |

---

## Quick Diagnostic Table

| Symptom | Likely Problem | Strategy | Ref |
|:---|:---|:---|:---:|
| "Agent gives one answer then stops — can't solve multi-step problems" | No agent loop | Implement perceive → decide → act → evaluate cycle | [`agentarch-05`](#agentarch-05-agent-loop--continuous-decision-cycle) |
| "Agent makes things up about recent events" | No tool access to real-time data | Add Web Search / API tools | [`agentarch-03`](#agentarch-03-tools--external-world-interaction) |
| "Agent forgets everything from previous conversations" | No long-term memory | Vector DB + RAG for persistent knowledge | [`agentarch-04`](#agentarch-04-memory--short-term--long-term) |
| "Agent runs unbounded — $500 bill from one session" | No guardrails | Token/cost limits, max iterations | [`agentarch-06`](#agentarch-06-guardrails--safety--control-layer) |
| "Agent calls wrong API with malformed payload" | No output validation | Schema validation + sandbox execution | [`agentarch-06`](#agentarch-06-guardrails--safety--control-layer) |
| "Complex multi-step reasoning fails halfway through" | No planning decomposition | Tree of Thoughts or ReAct prompting | [`agentarch-02`](#agentarch-02-planning--task-decomposition) |
| "Agent takes irreversible action without confirmation" | No human-in-the-loop | Approval gate for critical operations | [`agentarch-06`](#agentarch-06-guardrails--safety--control-layer) |
