---
name: okf-dictionary
description: 'Add novel technical terms to the reference-dictionary. Use when a new concept needs a glossary entry, a term is used but never defined, or building out the technical glossary with definitions and cross-references.'
argument-hint: 'Document to extract terms from'
user-invocable: true
---

# OKF Reference Dictionary

Extracts technical terms from documents and adds novel ones to the `reference-dictionary/` glossary.

## Quick Start

```bash
python3 agent_tools/dictionary_agent.py extract-terms <document.md> --dry-run
python3 agent_tools/dictionary_agent.py check-term "<term>"
python3 agent_tools/dictionary_agent.py list-domains
```

## Procedure

### 1. Extract candidate terms

```bash
python3 agent_tools/dictionary_agent.py extract-terms <file> --dry-run
```

Review the list — filter out false positives (structural labels, common words).

### 2. Check which terms are novel

```bash
python3 agent_tools/dictionary_agent.py check-term "<term>"
```

Already-defined terms are skipped. Novel terms get placed in the correct domain file.

### 3. Add entries

Each term entry follows this structure:
```markdown
## <Term Name>

<Definition>

### Key Characteristics
- ...

### When to Use
- ...

### When NOT to Use
- ...

### Also see
- [Related](file.md#anchor)
```

### 4. Update the Contents table

Add the new term to the Contents table at the top of the domain file.

## Dictionary Domain Files

| File | Domain |
|:---|:---|
| `resilience.md` | Circuit breakers, retries, bulkheads |
| `messaging.md` | Kafka, RabbitMQ, queues, topics |
| `caching.md` | Redis, TTL, eviction, stampede |
| `cqrs-event-driven.md` | CQRS, event sourcing, projections |
| `ai-ml-llm.md` | LLM, RAG, embeddings, transformers |
| `architecture-patterns.md` | Catch-all for general patterns |

## Tools

- [Dictionary Agent](../../agent_tools/dictionary_agent.py) — Main executable
- [Config](../../agent_tools/config.yaml) — Dictionary domain registry
- [Discovery Skill](../okf-domain-discovery/SKILL.md) — Register new dictionary domains
