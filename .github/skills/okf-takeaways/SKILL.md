---
name: okf-takeaways
description: 'Create a takeaway file only if all three conditions are true: (1) the article contains at least 3 reusable architectural concepts, (2) it has a clear problem → strategy → tradeoff structure, and (3) it matches a registered domain prefix. Otherwise, stop and report "Not eligible for takeaways."'
argument-hint: 'Article to extract takeaways from'
user-invocable: true
---

# OKF Key Takeaways

Extracts architectural patterns from source articles and creates structured takeaway files in `system-design-architecture/`.

## Quick Start

```bash
python3 agent_tools/takeaways_agent.py extract <article.md> --prefix <domain>
  # If <article.md> does not exist, or the output path cannot be written, report the error and do not create partial files.
python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>
  # If suggest-prefix returns no confident prefix, stop and report "No suitable domain prefix found." Do not guess a prefix or create an output file.
python3 agent_tools/takeaways_agent.py list-domains
```

## Procedure

### 1. Identify suitable articles

Create a takeaway file only when the article meets ALL three conditions:
- Contains at least 3 reusable architectural concepts
- Has a clear problem → strategy → tradeoff structure
- Matches a registered domain prefix listed in ../../agent_tools/config.yaml

If any condition is not met, stop and report "Not eligible for takeaways." If no registered prefix matches the article, stop and report "No suitable domain prefix found." Do not create a file or invent a new prefix unless the project explicitly instructs you to register one.

### 2. Determine domain prefix

```bash
python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>
```

Use only a prefix listed in ../../../agent_tools/config.yaml. If no registered prefix matches the article, stop and report "No suitable domain prefix found" instead of inventing one. Registered prefixes (examples): cb (Circuit Breaker), cqrs (CQRS), harness (Agent Harness), docker, broker, resilience, and [more](../../../agent_tools/config.yaml).

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

Create one takeaway file per article. Number takeaway entries sequentially starting at 01 within that file, and use the same domain prefix for all entries in that file.

## <prefix>-01: Problem Title
| | |
|:---|:---|
| **Problem** | ... |
| **Root cause** | ... |

**Strategy**: ...
**Tradeoff**: ...
```

### 4. Add cross-references

Perform cross-references in this order. If any item is unavailable, omit it rather than inventing it.

1. **Link to system-design files**: Add links to the 2-3 most relevant files in `system-design-architecture/` that directly support the same architectural pattern; use only existing paths.
2. **Reference dictionary terms**: Reference glossary terms from the project dictionary files in `reference-dictionary/` and only use terms that exist there.
3. **Map to Azure services**: Add Azure service mappings only when the article explicitly names or clearly implies a Microsoft Azure service; do not invent service mappings.
4. **Align with taxonomy**: Align the takeaway file with the taxonomy section listed in the current system-design index file, using the exact section numbers from that file; if the section is unavailable, do not guess.

## Tools

- [Takeaways Agent](../../../agent_tools/takeaways_agent.py) — Main executable
- [Config](../../../agent_tools/config.yaml) — Domain prefix registry
- [Discovery Skill](../okf-domain-discovery/SKILL.md) — Register new domains
