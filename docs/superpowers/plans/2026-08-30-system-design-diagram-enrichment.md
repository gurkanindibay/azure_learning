---
type: Reference
title: "System Design Diagram Enrichment Implementation Plan"
description: "Implementation plan for Archify enrichment of substantive system-design cases and source articles."
generated: { by: process:okf-migrate, at: 2026-08-30T00:00:00Z }
---

# System Design Diagram Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add validated Archify static and interactive diagrams to every approved substantive system-design document.

**Architecture:** Each document owns a source-grounded primary Archify artifact in its local `resources/` directory. Markdown embeds the artifact PNG near the explained design, gives an accessible textual description, and links to the delivered HTML; a small set of lifecycle- or sequence-heavy cases receive a second artifact.

**Tech Stack:** Markdown, JSON, Archify CLI, Node.js, Python 3 standard-library validation scripts.

## Global Constraints

- Preserve original content and existing images or Mermaid diagrams.
- Create one primary diagram per qualifying document; add a second only for delayed jobs, resumable uploads, notifications, chat, payments, and customer support.
- Store `<slug>.json`, `<slug>.html`, and `<slug>.png` in the source document's local `resources/` directory.
- Use `meta.quality_profile: "showcase"`, fresh IDs and wording, a maximum of 12 primary nodes, and an appropriate diagram type.
- Embed each PNG with descriptive alt text, add a prose diagram description, and provide a meaningful interactive HTML link.
- Run Archify `validate`, `deliver`, and `visual-check` on every artifact before updating source Markdown.
- Finish with `python3 scripts/okf_migrate.py --check` and `python3 agent_tools/okf_tools.py check-links`.

---

### Task 1: Establish artifact conventions and enrich original cases

**Files:**
- Create: Local `resources/` artifacts for all files in `system-design-cases/cases/`.
- Modify: All four Markdown files in `system-design-cases/cases/`.

**Diagram matrix:**

| Document | Primary | Secondary |
|:---|:---|:---|
| `part-2-url-shortener-system-design.md` | Global redirect architecture | Redirect read sequence |
| `part-2-news-feed-system-design.md` | Hybrid feed architecture | — |
| `part-3-e-commerce-platform-system-design.md` | Commerce order architecture | — |
| `part-3-real-time-messaging-system-design.md` | Real-time messaging architecture | Message delivery sequence |

- [ ] **Step 1: Read an Archify architecture schema/example and sequence schema/example**
- [ ] **Step 2: Author each primary JSON, validate it, deliver HTML/PNG, and visual-check it**
- [ ] **Step 3: Author, validate, deliver, and visual-check the two listed secondary diagrams**
- [ ] **Step 4: Embed each PNG and add accessible description and HTML link in its source document**
- [ ] **Step 5: Run `python3 agent_tools/format_agent.py validate` for all four changed source documents**

### Task 2: Enrich ByteByteGo distributed-systems foundations and product systems

**Files:**
- Create/modify: local artifacts and Markdown for chapters 02, 05-13, 20, 23-24, and 27-29 in `system-design-cases/bytebytego/`.

**Diagram matrix:**

| Group | Primary diagrams | Secondary diagrams |
|:---|:---|:---|
| Scaling/control | Scale evolution, rate limiter, consistent-hash ring, key-value store, ID generation | — |
| Product/real-time | URL shortener, crawler, notification, feed, chat, message queue | Notification delivery sequence; chat delivery sequence |
| Correctness | Hotel reservation, email delivery, payment, digital wallet, stock exchange | Payment processing sequence |

- [ ] **Step 1: Author the primary artifact per listed chapter, validate, deliver, and visual-check it**
- [ ] **Step 2: Author and validate the three listed secondary sequence artifacts**
- [ ] **Step 3: Embed each artifact PNG, description, and HTML link next to the matching source architecture section**
- [ ] **Step 4: Run `python3 agent_tools/format_agent.py validate` for all changed chapter documents**

### Task 3: Enrich ByteByteGo content, storage, geo, and data platforms

**Files:**
- Create/modify: local artifacts and Markdown for chapters 14-19, 21-22, 25-26 in `system-design-cases/bytebytego/`.

**Diagram matrix:**

| Group | Primary diagrams |
|:---|:---|
| Content/storage | Autocomplete, YouTube, Google Drive, S3-like storage |
| Geo-spatial | Proximity service, nearby friends, Google Maps |
| Data/operations | Metrics and alerting, ad-click aggregation, gaming leaderboard |

- [ ] **Step 1: Author the primary artifact per listed chapter, validate, deliver, and visual-check it**
- [ ] **Step 2: Embed each artifact PNG, description, and HTML link next to the matching source architecture section**
- [ ] **Step 3: Run `python3 agent_tools/format_agent.py validate` for all changed chapter documents**

### Task 4: Enrich qualifying system-design interview source articles

**Files:**
- Create/modify: local artifacts and Markdown for the nine approved documents under `articles/system-design-interview/`.

**Diagram matrix:**

| Document | Primary | Secondary |
|:---|:---|:---|
| `million-notifications-system-design.md` | Notification architecture | Delivery/retry sequence |
| `amazon-interview-question-design-a-delayed-job-scheduler.md` | Durable scheduler architecture | Job state and lease lifecycle |
| `customer-support-ai-platform-system-design-interview.md` | Support platform architecture | Ticket-to-AI/human escalation workflow |
| `resumable-uploads-chunking-large-files.md` | Resumable-upload architecture | Upload session lifecycle |
| `real-time-leaderboard-design.md` | Leaderboard architecture | — |
| `design-system-interviews.md` | Seven-phase interview workflow | — |
| `complete-system-design-interview-guide-2026.md` | Constraint-driven architecture decision workflow | — |
| `real-world-system-design-scenarios-part-1.md` | Scenario-family decision map | — |
| `22-design-interview-questions/01-22-scenario-based-system-design-questions.md` | Scenario-family decision map | — |

- [ ] **Step 1: Author, validate, deliver, and visual-check all primary artifacts**
- [ ] **Step 2: Author, validate, deliver, and visual-check all five listed secondary artifacts**
- [ ] **Step 3: Embed each artifact PNG, description, and HTML link in the appropriate article section**
- [ ] **Step 4: Run `python3 agent_tools/format_agent.py validate` for all nine changed articles**

### Task 5: Validate the complete enrichment

**Files:**
- Verify: all created artifact JSON, HTML, and PNG files and all 39 changed Markdown documents.

- [ ] **Step 1: Run `python3 scripts/okf_migrate.py --check`**

Expected: Exit code 0.

- [ ] **Step 2: Run `python3 agent_tools/okf_tools.py check-links`**

Expected: No broken links introduced under `system-design-cases/` or `articles/system-design-interview/`; record unrelated existing failures separately.

- [ ] **Step 3: Review the working-tree diff with `git diff --check` and inspect the artifact inventory**

Expected: No whitespace errors; every qualifying document has a PNG embed, HTML link, and its local artifact set.