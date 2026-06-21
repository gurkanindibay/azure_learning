# System Design Cases

> Original system-design interview cases written and maintained here, structured like the Medium source articles in [`articles/medium/`](../articles/medium/).

## Purpose

`articles/` stores external source material. This directory is for **your own** system-design interview answers, case studies, and practice problems.

Each case follows a consistent interview-ready structure so you can compare approaches, reuse patterns, and later extract key takeaways into [`system-design-architecture/`](../system-design-architecture/).

## Directory Layout

| Path | Purpose |
|:---|:---|
| `cases/` | Individual case write-ups |
| `templates/` | Reusable templates for new cases |
| `index.md` | Directory index and quick navigation |

## Naming Convention

- `part-N-<system-name>.md` — e.g., `part-1-rate-limiter.md`, `part-4-web-crawler.md`
- Use kebab-case and keep the title descriptive.

## Getting Started

1. Copy `templates/system-design-case-template.md` into `cases/`.
2. Rename it using the convention above.
3. Fill in each section.
4. Run `python3 scripts/okf_migrate.py --check` to validate.

## Relationship to Other Directories

- Source material → [`articles/`](../articles/)
- Extracted patterns & key takeaways → [`system-design-architecture/`](../system-design-architecture/)
- Term definitions → [`reference-dictionary/`](../reference-dictionary/)
- Azure implementations → [`architecture-azure/`](../architecture-azure/)
