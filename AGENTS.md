# Agent Guide — Azure Learning Repository

> This file is intended for AI coding agents that work in this repository. Read it first, then consult `.github/copilot-instructions.md` for the full content-authoring rules.

---

## Project Overview

This repository is a **technical knowledge base** — not a traditional software project. It contains curated notes, patterns, case studies, and reference material covering Microsoft Azure services, cloud-agnostic architecture patterns, system design takeaways, a technical glossary, programming-language notes (currently C# / .NET concurrency), SRE resources, and source articles/videos.

Everything is written in **Markdown**. There is no application server, compiled artifacts, or package manager. The only executable code is a small Python 3 script that keeps the architecture taxonomy reference in sync.

### Repository Type

| Aspect | Value |
|--------|-------|
| Primary format | Markdown (`.md`) with YAML frontmatter (OKF v0.1) |
| OKF format | [Open Knowledge Format v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) |
| Programming language | Python 3.11 (automation only) |
| Build system | None |
| Test framework | None (validation via OKF check and GitHub Actions) |
| Deployment | None (static documentation repository) |
| CI/CD | GitHub Actions (`.github/workflows/sync-taxonomy.yml`) |

---

## Where the Rules Live

This file covers **agent-specific operational guidance** (environment, automation, validation, security). For all content-authoring rules, use `.github/copilot-instructions.md` as the base:

| Topic | File |
|---|---|
| Repository structure & directory purposes | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Content placement decision tree | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Taxonomy alignment (`§X.X` references) | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Cross-reference patterns & map | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Naming conventions | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Adding new content step-by-step | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Directory-specific checklists | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) |
| Azure service doc templates | [`architecture-azure/.copilot-instructions.md`](architecture-azure/.copilot-instructions.md) |
| General pattern & taxonomy templates | [`architecture-general/.copilot-instructions.md`](architecture-general/.copilot-instructions.md) |
| Diagram accessibility (WCAG 2.1 AA) | [`.github/accessibility-guidelines.md`](.github/accessibility-guidelines.md) |

---

## Technology Stack

- **Documentation**: Markdown, Mermaid diagrams, fenced code blocks with language tags.
- **Automation**: Python 3.11, standard library only (`os`, `re`, `sys`, `argparse`, `pathlib`, `datetime`). No `requirements.txt`, virtual environment, or external packages are required.
- **CI/CD**: GitHub Actions (`/.github/workflows/sync-taxonomy.yml`).
- **Editor**: `.vscode/settings.json`.

---

## Build and Test Commands

There is no build step. The only validation is the taxonomy sync check.

```bash
# Validate that the taxonomy reference is in sync
python scripts/sync_taxonomy_reference.py --check

# Regenerate the taxonomy reference (edit READMEs first, then run this)
python scripts/sync_taxonomy_reference.py

# Preview what would be generated without writing to disk
python scripts/sync_taxonomy_reference.py --dry-run
```

### Optional Pre-Commit Hook

```bash
cp scripts/hooks/pre-commit-taxonomy-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook runs only when `architecture-general/**/index.md` files are staged.

---

## Testing / Validation Workflow

1. After editing any `architecture-general/**/index.md`, run:
   ```bash
   python scripts/sync_taxonomy_reference.py --check
   ```
2. If the check fails, regenerate and stage the reference:
   ```bash
   python scripts/sync_taxonomy_reference.py
   git add architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md
   ```
3. Preview changes before committing:
   ```bash
   python scripts/sync_taxonomy_reference.py --dry-run
   ```
4. Verify relative Markdown links resolve correctly.
5. Ensure Mermaid diagrams follow `.github/accessibility-guidelines.md`.

---

## Automation Details

### Taxonomy Sync Script

File: `scripts/sync_taxonomy_reference.py`

- Scans `architecture-general/01-*/index.md` through `architecture-general/09-*/index.md`.
- Extracts H3 subsections and bullet items.
- Generates `architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md`.
- Appends static sections for abstraction levels, architectural qualities, and naming conventions.
- Deterministic except for the `**Last updated**` timestamp, which `--check` ignores.
- **Never edit the taxonomy reference file by hand.**

### GitHub Actions Workflow

File: `.github/workflows/sync-taxonomy.yml`

- **On PR** (when `architecture-general/**/index.md` changes): runs `--check` and fails if stale.
- **On push to `main`** (when `architecture-general/**/index.md` changes): if `--check` fails, regenerates and commits with `chore: auto-sync taxonomy reference [skip ci]`.

---

## Security Considerations

- No secrets or credentials are stored in the repository. `.gitignore` only ignores `.DS_Store` and `temp_file.txt`.
- The GitHub Actions workflow uses the automatic `GITHUB_TOKEN`; no custom secrets are needed.
- The taxonomy sync script uses only the Python standard library.
- Do not add `.env` files, API keys, connection strings, or personal access tokens.
- New automation scripts should be dependency-free or declare dependencies in a file such as `requirements.txt` and run in an isolated environment.

---

## Key Files for Agents

| File | Purpose |
|------|---------|
| `.github/copilot-instructions.md` | Base content-authoring rules: structure, placement, taxonomy, cross-references, naming, checklists |
| `.github/accessibility-guidelines.md` | WCAG 2.1 AA diagram and documentation accessibility rules |
| `architecture-general/.copilot-instructions.md` | Cloud-agnostic pattern guidelines and taxonomy alignment rules |
| `architecture-azure/.copilot-instructions.md` | Azure-specific service documentation guidelines |
| `architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md` | Auto-generated canonical taxonomy (do not edit directly) |
| `scripts/sync_taxonomy_reference.py` | Taxonomy sync automation |
| `scripts/okf_migrate.py` | OKF frontmatter migration and validation |
| `agents/okf_tools.py` | OKF bundle utilities (validate, search, list, check-links, stats, graph) |
| `agents/README.md` | OKF agent guide — enrichment & consumption patterns |
| `reference-dictionary/index.md` | Glossary usage, term template, and anchor conventions |

---

## OKF Agent Tools

This repository is an [OKF v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) bundle. Use the bundled agent tools:

```bash
python3 agents/okf_tools.py validate      # Validate OKF conformance
python3 agents/okf_tools.py list          # List all concepts by type
python3 agents/okf_tools.py search <kw>   # Search concepts by keyword
python3 agents/okf_tools.py check-links   # Check cross-reference integrity
python3 agents/okf_tools.py summary       # Generate bundle summary
python3 agents/okf_tools.py stats         # JSON statistics
python3 agents/okf_tools.py graph         # Export relationship graph (JSON)
```

See [`agents/README.md`](agents/README.md) for the full OKF agent guide including enrichment agent templates.

---

## Quick Reference

- **New Azure service doc**: See `architecture-azure/.copilot-instructions.md`.
- **New general pattern**: See `architecture-general/.copilot-instructions.md`; add `> **Taxonomy Reference**: §X.X ...`; run `python scripts/sync_taxonomy_reference.py` if you edited a README.
- **New system design takeaway**: See `.github/copilot-instructions.md` for ID conventions and required sections.
- **New term**: See `reference-dictionary/index.md`.
- **Any `architecture-general/**/index.md` change**: Run `python scripts/sync_taxonomy_reference.py --check`.
- **After any content change**: Run `python3 agents/okf_tools.py validate` to verify OKF conformance.

---

> **Remember**: This repository values accuracy, stable cross-references, and taxonomy alignment over volume. For content-authoring details, always check `.github/copilot-instructions.md` first.
