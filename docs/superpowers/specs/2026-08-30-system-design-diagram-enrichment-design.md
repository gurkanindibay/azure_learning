---
type: Reference
title: "System Design Diagram Enrichment Design"
description: "Approved design for enriching substantive system-design material with Archify diagrams."
timestamp: 2026-08-30T00:00:00Z
---

# System Design Diagram Enrichment Design

## Goal

Enrich substantive system-design cases and source articles with accessible Archify diagrams that retain a static Markdown image and provide a link to an interactive HTML viewer.

## Scope

The enrichment covers 39 qualifying documents:

- Four original cases in `system-design-cases/cases/`.
- Twenty-six technical ByteByteGo chapters in `system-design-cases/bytebytego/`, excluding estimation, interview-method, and learning-summary chapters.
- Nine source articles in `articles/system-design-interview/`: large-scale notifications, delayed job scheduler, customer support platform, resumable uploads, real-time leaderboard, system-design interview framework, complete interview guide, real-world scenarios, and scenario questions.

The 24 short ByteByteGo blog posts, behavioral articles, and general study articles are excluded because they do not contain enough concrete architecture, workflow, or lifecycle material to warrant a standalone diagram.

## Artifact Convention

Each qualifying source document receives an artifact set in a local `resources/` directory:

- `<slug>.json`: typed Archify specification.
- `<slug>.html`: delivered interactive viewer.
- `<slug>.png`: static export embedded by Markdown.

The source document embeds the PNG near the section it explains, includes descriptive alt text and a short textual diagram description, and links to the HTML viewer with meaningful text. Existing Mermaid and external source images are retained when they provide useful original context.

## Diagram Selection

Each qualifying document receives one primary diagram selected from architecture, workflow, sequence, data flow, or lifecycle based on its critical path. A second diagram is added only if a separate lifecycle or protocol sequence is central to understanding the design.

Expected second diagrams cover delayed-job state and claim recovery, resumable-upload lifecycle, notification delivery sequence, real-time message delivery, payment processing, and customer-support ticket/AI escalation.

## Quality and Accessibility

Every diagram uses fresh, source-grounded wording and stable IDs, uses the Archify showcase quality profile, and stays under 12 primary nodes per diagram. Static output has a descriptive alt text and companion prose so the diagram remains understandable without color or visual rendering. Each candidate is validated, delivered, and visually checked with Archify before source Markdown is updated.

## Validation

For every artifact: run Archify `validate`, `deliver`, and `visual-check` commands. After source updates: run `python3 scripts/okf_migrate.py --check` and `python3 agent_tools/okf_tools.py check-links`. Existing unrelated link failures will be reported separately; no enrichment-introduced broken link is acceptable.