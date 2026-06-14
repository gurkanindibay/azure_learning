---
name: okf-takeaways
description: 'Extract key architectural takeaways from articles into system-design-architecture files. Use when processing a new article to create ID-prefixed takeaway files with problem→strategy→tradeoff sections.'
argument-hint: 'Article to extract takeaways from'
user-invocable: true
---

# OKF Key Takeaways

Extracts architectural patterns from source articles and creates structured takeaway files in `system-design-architecture/`.

## Quick Start

```bash
python3 agent_tools/takeaways_agent.py extract <article.md> --prefix <domain>
python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>
python3 agent_tools/takeaways_agent.py list-domains
```

## Procedure

### 1. Identify suitable articles

This step is **optional** — only articles with distinct architectural patterns need takeaways. Criteria:
- Contains 3+ reusable architectural concepts
- Has clear problem → strategy → tradeoff patterns
- Relates to an existing domain prefix

### 2. Determine domain prefix

```bash
python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>
```

Registered prefixes: cb (Circuit Breaker), cqrs (CQRS), harness (Agent Harness), docker, broker, resilience, and [more](../../agent_tools/takeaways_agent.py).

### 3. Generate the takeaway file

Uses the template:
```markdown
---
type: System Design
title: "<Domain> — Key Takeaways"
---

# <NN>. <Domain> — Key Takeaways

> **Parent**: [System Design Interview Reference](index.md)
> **Source**: [Article](../articles/...)

## Contents
| ID | Problem | Key Concept |
|:---|:---|:---|

## <prefix>-01: Problem Title
| | |
|:---|:---|
| **Problem** | ... |
| **Root cause** | ... |

**Strategy**: ...
**Tradeoff**: ...
```

### 4. Add cross-references

- Link to related system-design files
- Reference dictionary terms
- Map to Azure services where applicable
- Align with taxonomy (§X.X)

## Tools

- [Takeaways Agent](../../agent_tools/takeaways_agent.py) — Main executable
- [Config](../../agent_tools/config.yaml) — Domain prefix registry
- [Discovery Skill](../okf-domain-discovery/SKILL.md) — Register new domains
