# GitHub Copilot Instructions - Azure Learning Repository

> **Repository Type**: Technical documentation (NOT a code repository)  
> **Focus**: Cloud architecture, software engineering patterns, and .NET multithreading

## Repository Structure

```
azure_learning/
├── architecture-azure/      # Azure-specific (Physical/Implementation layer)
├── architecture-general/    # Cloud-agnostic patterns (Conceptual/Logical layer)
├── dotNet_multi_threading/  # .NET concurrency patterns
├── site-reliability-engineering/  # SRE resources and infographics
├── unstructured-resources/  # Articles and evolving architecture notes
└── scripts/                 # Taxonomy sync automation (Python, no deps)
```

### Subdirectory Instructions

Each major section has detailed guidance — **read these before contributing**:
- [`architecture-azure/.copilot-instructions.md`](../architecture-azure/.copilot-instructions.md) — Azure service docs, tier comparisons, templates
- [`architecture-general/.copilot-instructions.md`](../architecture-general/.copilot-instructions.md) — Taxonomy alignment rules, pattern templates

## Content Placement

```
Is it Azure-specific?
  ├─ YES → architecture-azure/  (compute/, data/, networking/, security/, integration/, etc.)
  └─ NO → Is it .NET multithreading?
      ├─ YES → dotNet_multi_threading/
      └─ NO → architecture-general/  (align with taxonomy §X.X section)
```

## Taxonomy Alignment

**All content MUST align with the [Architecture Taxonomy](../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md)**.

- Reference taxonomy sections using `§X.X` format: `> **Taxonomy Reference**: §3.3 Event-Driven & Messaging`
- The taxonomy file is **auto-generated** — never edit it directly

## Automation

### Taxonomy Sync (run after editing any `architecture-general/**/README.md`)

```bash
python scripts/sync_taxonomy_reference.py          # Regenerate
python scripts/sync_taxonomy_reference.py --check   # CI check (exit 1 if stale)
python scripts/sync_taxonomy_reference.py --dry-run  # Preview
```

- GitHub Actions validates sync on PRs (`.github/workflows/sync-taxonomy.yml`)
- Optional pre-commit hook: `cp scripts/hooks/pre-commit-taxonomy-check.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`

## Content Standards

- Proper heading hierarchy (H1 → H2 → H3)
- TOC for documents >200 lines
- Comparison tables for alternatives
- Code blocks with language tags
- Mermaid diagrams for architecture visualizations
- Reference official Microsoft/vendor documentation
- Include practical examples and case studies

## Cross-References

Link between general patterns and Azure implementations:

| Direction | Pattern |
|-----------|---------|
| General → Azure | `> **Azure Implementation**: See [Service Name](../architecture-azure/category/service/)` |
| Azure → General | `> **General Pattern**: [Pattern Name](../architecture-general/section/)`<br>`> **Taxonomy**: §X.X Section Name` |

Example: [`01-uber-go-vs-rust-case-study.md`](../architecture-general/02-application-software-architecture/07-language-selection/01-uber-go-vs-rust-case-study.md)

## Naming Conventions

- **Files**: kebab-case — `azure-event-hubs-tiers.md`
- **Directories**: kebab-case — `event-hubs/`, `service-bus/`
- **Headings**: Title Case for H1, Sentence case for others

## Adding New Content

1. **Determine location** using content placement tree above
2. **Check taxonomy alignment** — which `§X.X` section?
3. **Use templates** from subdirectory `.copilot-instructions.md` files (service doc, comparison, case study)
4. **Add cross-references** to related content
5. **Update parent README.md** with link to new doc
6. **Run taxonomy sync** if you modified any `architecture-general/**/README.md`
