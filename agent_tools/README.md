# OKF Agent Tools — Azure Learning Repository

> **OKF Bundle**: This repository is an [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle.  
> **Agent Source**: The patterns below are derived from [GoogleCloudPlatform/knowledge-catalog/agents/](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/agents).

---

## Skills vs Tools — Clear Distinction

This repository uses two distinct concepts:

| Concept | Location | What it is | How to use |
|:---|:---|:---|:---|
| **Skills** | `.github/skills/` | Task workflows with bundled instructions | Slash commands in Copilot Chat (`/okf-format`, `/okf-takeaways`, etc.) |
| **Tools** | `agent_tools/` | Python scripts that implement the logic | Run from terminal or invoked by skills |
| **Instructions** | `.github/copilot-instructions.md`, `AGENTS.md` | Always-on guidance for Copilot | Loaded automatically |

### Why Skills, Not Agents?

- **Skills** are on-demand workflows with bundled scripts — perfect for task-oriented operations like "format this document" or "extract takeaways"
- **Agents** (`.agent.md`) are persistent personas with tool restrictions — better suited for long-running assistant roles (not needed here since each task is self-contained)

## 🤖 GitHub Copilot Integration

### Slash Commands (Skills)

Type `/` in Copilot Chat to access these skills:

| Slash Command | Skill | What it does |
|:---|:---|:---|
| `/okf-format` | [`.github/skills/okf-format/`](../.github/skills/okf-format/SKILL.md) | Format raw markdown into OKF-compliant concepts |
| `/okf-takeaways` | [`.github/skills/okf-takeaways/`](../.github/skills/okf-takeaways/SKILL.md) | Extract system-design takeaways from articles |
| `/okf-dictionary` | [`.github/skills/okf-dictionary/`](../.github/skills/okf-dictionary/SKILL.md) | Add novel terms to reference-dictionary |
| `/okf-domain-discovery` | [`.github/skills/okf-domain-discovery/`](../.github/skills/okf-domain-discovery/SKILL.md) | Discover and register new domains |

Skills are also **auto-loaded** by Copilot when their description matches your request — you don't always need to type the slash command.

### Terminal Commands (Tools)

```bash
python3 agent_tools/format_agent.py format <file.md>       # Format & validate
python3 agent_tools/takeaways_agent.py extract <file.md>    # Extract takeaways
python3 agent_tools/dictionary_agent.py extract-terms <f>   # Add dictionary terms
python3 agent_tools/discovery_agent.py --apply              # Register new domains
python3 agent_tools/coordinator.py process <file.md>        # Run all 4 steps
```

## Coordinated Agent Workflow

When adding a new document to the repository, three agents work in coordination:

```
┌─────────────────────┐
│   Raw Document       │
│   (article, note,    │
│    external source)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Agent 1: format_agent.py                   │
│  Format & Validate                          │
│  • Converts raw markdown to OKF format      │
│  • Determines placement (which directory)   │
│  • Adds YAML frontmatter with type/title    │
│  • Normalizes heading hierarchy             │
│  • Validates against repo standards         │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Agent 2: takeaways_agent.py  [OPTIONAL]    │
│  Key Takeaways                              │
│  • Extracts architectural patterns          │
│  • Assigns domain-prefixed IDs              │
│  • Generates system-design-architecture/    │
│    takeaway file with Contents table        │
│  • Adds cross-references                    │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Agent 3: dictionary_agent.py               │
│  Reference Dictionary                       │
│  • Extracts technical terms from document   │
│  • Checks which terms are already defined   │
│  • Adds novel terms to reference-dictionary │
│  • Places terms in correct domain file      │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  coordinator.py                             │
│  • Runs all agents in sequence              │
│  • Validates cross-references               │
│  • Runs taxonomy sync                       │
└─────────────────────────────────────────────┘
```

### Quick Start

```bash
# Full pipeline — process a raw document through all agents
python3 agent_tools/coordinator.py process my-raw-article.md

# Skip the takeaways step
python3 agent_tools/coordinator.py process my-raw-article.md --no-takeaways

# Run individual agents
python3 agent_tools/format_agent.py format my-article.md
python3 agent_tools/takeaways_agent.py extract articles/medium/my-article.md --prefix cb
python3 agent_tools/dictionary_agent.py extract-terms system-design-architecture/23-circuit-breaker-key-takeaways.md

# Validate everything
python3 agent_tools/coordinator.py validate-all
```

### Agent Files

| File | Agent | Purpose |
|:---|:---|:---|
| `format_agent.py` | Agent 1 | Format raw markdown into OKF-compliant concepts |
| `takeaways_agent.py` | Agent 2 | Create system-design takeaway files from articles |
| `dictionary_agent.py` | Agent 3 | Add novel terms to the reference dictionary |
| `discovery_agent.py` | Discovery | Auto-discover new domains from the filesystem |
| `coordinator.py` | Orchestrator | Run all agents in coordinated sequence (+ discovery) |
| `okf_tools.py` | Utilities | Bundle introspection (validate, search, stats) |
| `config.yaml` | Configuration | Single source of truth for all domain registries |
| `config_loader.py` | Configuration | Config loader with auto-discovery from filesystem |
| `SKILL.md` | Skill Definition | AI agent instructions for domain discovery |

---

## Domain Discovery

When new files are added to `system-design-architecture/` or `reference-dictionary/`, the discovery agent automatically detects new domains and offers to register them in `config.yaml`.

```bash
# Show undiscovered domains
python3 agent_tools/discovery_agent.py

# Preview what would be added to config.yaml
python3 agent_tools/discovery_agent.py --dry-run

# Register all discovered domains
python3 agent_tools/discovery_agent.py --apply

# Analyze a specific new file
python3 agent_tools/discovery_agent.py --watch system-design-architecture/29-mesh-key-takeaways.md
```

**No code changes needed** — just create the file and run `--apply`.

The coordinator runs discovery automatically after processing a new document.

See [`SKILL.md`](SKILL.md) for the full AI agent instructions.

---

In the OKF ecosystem, there are two kinds of agents:

| Agent Type | Direction | What it does |
|:---|:---|:---|
| **Enrichment Agent** | Writes INTO an OKF bundle | Creates or updates concept documents with YAML frontmatter and structured markdown bodies |
| **Consumption Agent** | Reads FROM an OKF bundle | Loads concepts into context, builds search indexes, generates visualizations, answers questions |

This repository is **both**:
- A **target** for enrichment agents (you can write agents that add new concepts)
- A **source** for consumption agents (AI coding assistants, search tools, graph viewers)

---

## How AI Agents Consume This Repository

### Direct Consumption (Zero Tooling)

OKF bundles are plain markdown files with YAML frontmatter. Any AI agent can:

1. **List concepts**: Walk the directory tree, read `index.md` files for progressive disclosure
2. **Read a concept**: Open any `.md` file — YAML frontmatter gives `type`, `title`, `description`, `tags`, `timestamp`; body is standard markdown
3. **Follow cross-references**: Standard markdown links between concepts express relationships
4. **Search by type**: Filter files by their `type` field (e.g., "System Design", "Azure Service", "Reference")

### With the GitHub Copilot / VS Code Agent

The `.github/copilot-instructions.md` and `AGENTS.md` files instruct coding agents how to navigate this bundle. When a coding agent is asked about a topic:

1. It searches `index.md` files for relevant sections
2. It opens concept documents by their `type` and `title`
3. It follows cross-references to related concepts
4. It uses `reference-dictionary/` for term definitions

### With a Custom Consumption Agent

```python
# Minimal consumption agent — loads all concepts from the bundle
import yaml
from pathlib import Path

def load_okf_bundle(root: Path) -> list[dict]:
    """Load all OKF concept documents from a bundle."""
    concepts = []
    for md_file in root.rglob("*.md"):
        if md_file.name in ("index.md", "log.md"):
            continue
        text = md_file.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2] if len(parts) > 2 else ""
            concepts.append({
                "path": str(md_file.relative_to(root)),
                "frontmatter": fm,
                "body": body,
            })
    return concepts

# Usage
bundle = load_okf_bundle(Path("."))
# Filter by type
system_design = [c for c in bundle if c["frontmatter"].get("type") == "System Design"]
# Search by tag
azure_concepts = [c for c in bundle if "azure" in c["frontmatter"].get("tags", [])]
```

---

## How to Write an Enrichment Agent for This Repository

### Minimal Enrichment Agent Template

```python
#!/usr/bin/env python3
"""Minimal OKF enrichment agent for the azure_learning bundle."""

import yaml
from datetime import datetime, timezone
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent.parent

def write_concept(
    rel_path: str,
    concept_type: str,
    title: str,
    description: str,
    body: str,
    tags: list[str] | None = None,
    resource: str | None = None,
) -> Path:
    """Write an OKF concept document to the bundle."""
    filepath = BUNDLE_ROOT / rel_path
    filepath.parent.mkdir(parents=True, exist_ok=True)

    fm = {
        "type": concept_type,
        "title": title,
        "description": description,
        "tags": tags or [],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if resource:
        fm["resource"] = resource

    fm_yaml = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
    content = f"---\n{fm_yaml}\n---\n\n{body}"

    filepath.write_text(content, encoding="utf-8")
    return filepath


def read_concept(rel_path: str) -> dict | None:
    """Read an existing OKF concept document."""
    filepath = BUNDLE_ROOT / rel_path
    if not filepath.exists():
        return None
    text = filepath.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        fm = yaml.safe_load(parts[1]) or {}
        body = parts[2] if len(parts) > 2 else ""
        return {"frontmatter": fm, "body": body, "path": rel_path}
    return {"frontmatter": {}, "body": text, "path": rel_path}


# Example: enrich a concept with AI-generated content
def enrich_with_llm(rel_path: str, prompt: str):
    """Template for LLM-powered enrichment.
    
    Replace this with your actual LLM call (OpenAI, Vertex AI, etc.)
    """
    existing = read_concept(rel_path)
    if not existing:
        print(f"Concept not found: {rel_path}")
        return

    # Call your LLM here with the existing content as context
    # enriched_body = your_llm.generate(
    #     system="You are a cloud architecture expert.",
    #     prompt=f"Enrich this concept:\n\n{existing['body']}\n\n{prompt}"
    # )

    # For now, just print what would happen
    print(f"Would enrich: {rel_path}")
    print(f"  Type: {existing['frontmatter'].get('type')}")
    print(f"  Title: {existing['frontmatter'].get('title')}")
    print(f"  Prompt: {prompt}")


if __name__ == "__main__":
    enrich_with_llm(
        "architecture-azure/integration/event-hubs/azure-event-hubs-tiers.md",
        "Add a section on cost optimization for high-throughput scenarios."
    )
```

### Enrichment Workflow

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ Source Data   │ ──▶ │ Enrichment    │ ──▶ │ OKF Bundle   │
│ (BigQuery,    │     │ Agent         │     │ (this repo)  │
│  Web, Docs,   │     │ (LLM-powered) │     │              │
│  GitHub)      │     │               │     │              │
└──────────────┘     └───────────────┘     └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Validation   │
                      │ (okf_migrate │
                      │  --check)    │
                      └──────────────┘
```

### Adding a New Concept (Manual Enrichment)

1. **Choose the right directory** using the [content placement tree](../.github/copilot-instructions.md)
2. **Create the markdown file** with OKF frontmatter:
   ```markdown
   ---
   type: Azure Service
   title: "My New Azure Service"
   description: "A brief one-line summary of this service."
   tags: [compute, networking]
   timestamp: 2026-06-15T00:00:00Z
   ---

   # My New Azure Service

   Content goes here...
   ```
3. **Update the parent `index.md`** with a link to the new concept
4. **Add cross-references** to related concepts
5. **Run validation**: `python3 scripts/okf_migrate.py --check`
6. **Run taxonomy sync** if in `architecture-general/`: `python3 scripts/sync_taxonomy_reference.py`

---

## OKF Agent Architecture (from Google's Reference Implementation)

The [Google OKF enrichment agent](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) uses this architecture:

```
agents/enrichment/
├── src/
│   ├── agent_runner.py      # CLI entrypoint with modes (doc, table, context_overlay)
│   ├── engine.py            # LLM agents (Vertex Gemini)
│   ├── common.py            # Shared helpers
│   ├── modes/               # Mode-specific logic
│   └── tools/               # Tool implementations
└── eval/                    # Evaluation metrics
```

### Core OKF Components (Vendor-Neutral)

These are the OKF-specific abstractions, portable to any agent framework:

| Component | Source File | Purpose |
|:---|:---|:---|
| `OKFDocument` | `bundle/document.py` | Parse/serialize/validate OKF markdown files |
| `write_concept_doc` | `tools/bundle_tools.py` | Write a concept document with frontmatter validation |
| `read_existing_doc` | `tools/bundle_tools.py` | Read existing concept for refinement |
| `regenerate_indexes` | `bundle/index.py` | Auto-generate `index.md` from concept frontmatter |
| `Source` (ABC) | `sources/base.py` | Pluggable source interface (BigQuery, web, files) |
| `ConceptRef` | `sources/base.py` | Identifies a concept: id, type, resource, hint |

### Agent Tools (Mapped to Google ADK)

| Tool | Purpose |
|:---|:---|
| `list_concepts` | List all concepts from the active source |
| `read_concept_raw` | Fetch raw metadata for a concept |
| `sample_rows` | Sample data rows from a table concept |
| `read_existing_doc` | Read an already-written OKF document |
| `write_concept_doc` | Write/overwrite an OKF concept document |
| `fetch_url` | Fetch a web page (web ingestion agent) |

---

## Bundled Utilities

### `okf_tools.py`

A dependency-free Python toolkit for working with this OKF bundle. See [`okf_tools.py`](okf_tools.py).

```bash
# Validate the bundle
python3 agent_tools/okf_tools.py validate

# List all concepts grouped by type
python3 agent_tools/okf_tools.py list

# Search concepts by keyword
python3 agent_tools/okf_tools.py search "circuit breaker"

# Check cross-reference integrity
python3 agent_tools/okf_tools.py check-links

# Generate an index summary
python3 agent_tools/okf_tools.py summary
```

### `okf_migrate.py` (repo root)

The migration and validation tool for OKF conformance:

```bash
python3 scripts/okf_migrate.py --check    # Validate OKF conformance
python3 scripts/okf_migrate.py --dry-run  # Preview changes
python3 scripts/okf_migrate.py            # Apply frontmatter to new files
```

---

## Integration with AI Coding Agents

### VS Code / GitHub Copilot

This repo is configured for AI coding agents via:
- [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) — content-authoring rules
- [`AGENTS.md`](../AGENTS.md) — agent operational guidance

When an AI agent works in this repo, it:
1. Reads these instruction files first
2. Uses `index.md` files for progressive disclosure
3. Reads concept documents by following cross-references
4. Runs `okf_migrate.py --check` after making changes

### Custom Agent Integration (MCP)

To expose this bundle to an MCP-compatible agent, create an MCP server that wraps the OKF tools:

```json
{
  "mcpServers": {
    "okf-azure-learning": {
      "command": "python3",
      "args": ["agent_tools/okf_tools.py", "serve"],
      "cwd": "/path/to/azure_learning"
    }
  }
}
```

---

## References

- [OKF Specification v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [Google OKF Enrichment Agent](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
- [Google Knowledge Catalog Agents](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/agents)
- [Metadata as Code (kcmd)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/agents/mdcode)
