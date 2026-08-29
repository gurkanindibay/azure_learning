# Agent Guide — Azure Learning Repository

> This repository is an [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle. This file is the **Kimi Code root agent guide**. It does not duplicate the detailed rules; instead it points to the skill, tool, and instruction files that govern each task.

---

## Project Overview

This is a **technical knowledge base**, not a traditional software project. It contains curated notes, patterns, case studies, and reference material covering Azure services, cloud-agnostic architecture, system design takeaways, a technical glossary, programming-language notes, SRE resources, and source articles/videos.

| Aspect | Value |
|--------|-------|
| Primary format | Markdown (`.md`) with YAML frontmatter (OKF v0.1) |
| Programming language | Python 3.11 (automation only) |
| Build system | None |
| Test framework | None — validation is via `okf_migrate.py`, `sync_taxonomy_reference.py`, and GitHub Actions |
| Deployment | None (static documentation repository) |
| CI/CD | GitHub Actions (`.github/workflows/sync-taxonomy.yml`) |

---

## How This Repository Is Organized for Agents

The repo uses a **skills + tools + instructions** pattern. Do not duplicate guidance from these files; read and follow them by reference.

| Layer | Location | Purpose |
|:---|:---|:---|
| **Instructions** | `.github/copilot-instructions.md` | Base content-authoring rules: placement, taxonomy, cross-references, naming, checklists |
| **Skills** | `.github/skills/okf-*/SKILL.md` | Task-specific workflows (format, takeaways, dictionary, domain discovery) |
| **Tools** | `agent_tools/` | Python scripts that implement the skill workflows |
| **Validation** | `scripts/okf_migrate.py`, `scripts/sync_taxonomy_reference.py` | OKF conformance and taxonomy sync checks |

For the full architecture of the agent tooling, see [`agent_tools/README.md`](agent_tools/README.md).

### Architecture Diagram Guidance

When creating a document with a substantial architecture, workflow, sequence, data-flow, or lifecycle diagram, use Archify as the primary diagram authoring tool. Store the Archify specification and delivered HTML viewer under the document's local `resources/` directory, validate with `node bin/archify.mjs validate ... --quality showcase --repo-root <repository>`, and deliver with `node bin/archify.mjs deliver ...`. Embed the generated PNG with standard Markdown for reliable rendering, and link the HTML viewer separately for interactive exploration. Use Mermaid for small inline explanatory diagrams when a standalone Archify artifact is not warranted.

---

## Base Instructions

Always start from `.github/copilot-instructions.md` for content-authoring rules:

| Topic | File |
|---|---|
| Repository structure & directory purposes | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Content placement decision tree | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Taxonomy alignment (`§X.X` references) | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Cross-reference patterns & map | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Naming conventions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Step-by-step adding new content | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Directory-specific checklists | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Azure service doc templates | [`architecture-azure/.copilot-instructions.md`](architecture-azure/.copilot-instructions.md) |
| General pattern & taxonomy templates | [`architecture-general/.copilot-instructions.md`](architecture-general/.copilot-instructions.md) |
| Diagram accessibility (WCAG 2.1 AA) | [`.github/accessibility-guidelines.md`](.github/accessibility-guidelines.md) |

---

## Skills

Each skill is a task workflow. Read the linked `SKILL.md` before performing that task.

| Skill | Purpose | Detailed Procedure |
|:---|:---|:---|
| `okf-format` | Format raw markdown into an OKF-compliant concept document and determine correct placement | [`.github/skills/okf-format/SKILL.md`](.github/skills/okf-format/SKILL.md) |
| `okf-takeaways` | Extract system-design takeaways from source articles into `system-design-architecture/` | [`.github/skills/okf-takeaways/SKILL.md`](.github/skills/okf-takeaways/SKILL.md) |
| `okf-dictionary` | Add novel technical terms to `reference-dictionary/` | [`.github/skills/okf-dictionary/SKILL.md`](.github/skills/okf-dictionary/SKILL.md) |
| `okf-domain-discovery` | Discover and register new domains in `agent_tools/config.yaml` | [`.github/skills/okf-domain-discovery/SKILL.md`](.github/skills/okf-domain-discovery/SKILL.md) |

---

## Tools

Skills are implemented by the Python scripts in `agent_tools/`. For command reference and architecture, see [`agent_tools/README.md`](agent_tools/README.md).

| Tool | Maps to Skill | Purpose |
|:---|:---|:---|
| `agent_tools/format_agent.py` | `okf-format` | Format & validate OKF concept documents |
| `agent_tools/takeaways_agent.py` | `okf-takeaways` | Extract takeaways and assign domain-prefixed IDs |
| `agent_tools/dictionary_agent.py` | `okf-dictionary` | Extract terms and add novel ones to the dictionary |
| `agent_tools/discovery_agent.py` | `okf-domain-discovery` | Detect and register new domains |
| `agent_tools/coordinator.py` | All skills | Run the full enrichment pipeline in sequence |
| `agent_tools/okf_tools.py` | — | Bundle introspection: validate, list, search, check-links, summary |
| `agent_tools/config.yaml` | All skills | Single source of truth for domain/type registries |

---

## Validation Commands

There is no build step. Run these checks after making changes.

```bash
# OKF conformance: frontmatter, index.md, reserved files
python scripts/okf_migrate.py --check

# Taxonomy sync (run after editing any architecture-general/**/README.md)
python scripts/sync_taxonomy_reference.py --check

# Regenerate taxonomy reference when needed
python scripts/sync_taxonomy_reference.py
```

### Full Enrichment Pipeline

```bash
# Process a raw document through format → takeaways → dictionary → discovery
python3 agent_tools/coordinator.py process <file.md>

# Skip takeaways extraction
python3 agent_tools/coordinator.py process <file.md> --no-takeaways

# Validate the entire bundle
python3 agent_tools/coordinator.py validate-all
```

### Optional Pre-Commit Hook

```bash
cp scripts/hooks/pre-commit-taxonomy-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook runs only when `architecture-general/**/README.md` files are staged.

---

## Security Considerations

- No secrets or credentials are stored in the repository. `.gitignore` only ignores `.DS_Store` and `temp_file.txt`.
- The GitHub Actions workflow uses the automatic `GITHUB_TOKEN`; no custom secrets are needed.
- Automation scripts use only the Python standard library unless declared otherwise.
- Do not add `.env` files, API keys, connection strings, or personal access tokens.
- New automation scripts should be dependency-free or declare dependencies in a file such as `requirements.txt` and run in an isolated environment.

---

## Key Files for Agents

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Base content-authoring rules |
| `.github/accessibility-guidelines.md` | WCAG 2.1 AA diagram and documentation accessibility rules |
| `architecture-general/.copilot-instructions.md` | Cloud-agnostic pattern guidelines and taxonomy alignment rules |
| `architecture-azure/.copilot-instructions.md` | Azure-specific service documentation guidelines |
| `.github/skills/okf-format/SKILL.md` | Format & validate OKF documents |
| `.github/skills/okf-takeaways/SKILL.md` | Extract system-design takeaways |
| `.github/skills/okf-dictionary/SKILL.md` | Add dictionary terms |
| `.github/skills/okf-domain-discovery/SKILL.md` | Register new domains |
| `agent_tools/README.md` | Full agent-tool architecture, commands, and examples |
| `agent_tools/config.yaml` | Domain/type registry source of truth |
| `scripts/okf_migrate.py` | OKF conformance validation and migration |
| `scripts/sync_taxonomy_reference.py` | Taxonomy sync automation |
| `architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md` | Auto-generated canonical taxonomy (do not edit directly) |
| `reference-dictionary/index.md` | Glossary usage, term template, and anchor conventions |

---

## Quick Reference

- **Format or validate a document**: follow [`okf-format`](.github/skills/okf-format/SKILL.md) → run `python3 agent_tools/format_agent.py validate <file.md>`.
- **Extract takeaways from an article**: follow [`okf-takeaways`](.github/skills/okf-takeaways/SKILL.md) → run `python3 agent_tools/takeaways_agent.py extract <article.md> --prefix <domain>`.
- **Add dictionary terms**: follow [`okf-dictionary`](.github/skills/okf-dictionary/SKILL.md) → run `python3 agent_tools/dictionary_agent.py extract-terms <file.md> --dry-run`.
- **Register a new domain**: follow [`okf-domain-discovery`](.github/skills/okf-domain-discovery/SKILL.md) → run `python3 agent_tools/discovery_agent.py --apply`.
- **Run full pipeline**: `python3 agent_tools/coordinator.py process <file.md>`.
- **After any edit**: `python scripts/okf_migrate.py --check`.
- **After `architecture-general/**/README.md` edits**: `python scripts/sync_taxonomy_reference.py --check`.

---

> **Remember**: This repository values accuracy, stable cross-references, and taxonomy alignment over volume. For content-authoring details, start with `.github/copilot-instructions.md`; for task workflows, use the `.github/skills/` files; for implementation, use the `agent_tools/` scripts.
