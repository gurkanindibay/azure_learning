---
name: okf-format
description: 'Format raw markdown into OKF-compliant concept documents. Use when adding a new document, converting external content to OKF, validating files against repo conventions, or determining correct placement for new content.'
argument-hint: 'File to format or validate'
user-invocable: true
---

# OKF Format & Validate

Converts raw markdown into OKF-compliant concept documents following the azure_learning repository standards.

## Quick Start

```bash
python3 agent_tools/format_agent.py format <raw-file.md>
python3 agent_tools/format_agent.py validate <file.md>
```

## Procedure

### 1. Analyze content and determine placement

Use the decision tree from `.github/copilot-instructions.md`:
- Azure-specific → `architecture-azure/`
- Cloud-agnostic patterns → `architecture-general/`
- System design → `system-design-architecture/`
- Term definitions → `reference-dictionary/`
- Programming → `programming-languages/<language>/`
- Articles → `articles/<domain>/`
- Video notes → `videos/`
- Raw drafts → `unstructured-resources/`

### 2. Add OKF frontmatter

```yaml
---
type: <Azure Service | Architecture Pattern | System Design | Reference | ...>
title: "<title>"
description: "<one-line summary>"
timestamp: <ISO 8601>
---
```

### 3. Normalize markdown

- H1 → H2 → H3 hierarchy (no skips)
- Blank lines around headings
- Language tags on code blocks
- Working cross-references
- For substantial architecture, workflow, sequence, data-flow, or lifecycle diagrams, create an Archify specification and HTML viewer under the document's local `resources/` directory. Validate with `node bin/archify.mjs validate <type> <spec.json> --quality showcase --repo-root <repository> --json` and deliver with `node bin/archify.mjs deliver <type> <spec.json> <output.html> --quality showcase --repo-root <repository> --json`.
- Embed the delivered PNG with standard Markdown and link the HTML viewer separately; use Mermaid for small inline diagrams when a standalone Archify artifact is unnecessary.

### 4. Validate

```bash
python3 agent_tools/format_agent.py validate <output-path>
```

## Tools

- [Format Agent](../../../agent_tools/format_agent.py) — Main executable
- [Config](../../../agent_tools/config.yaml) — Type mappings and placement signals
- [OKF Spec](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
