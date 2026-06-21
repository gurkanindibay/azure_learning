# Agent Guide — System Design Cases

> This directory holds **original system-design interview cases** written by the repository owner, structured in the same style as the Medium source articles in `articles/medium/`.
>
> Unlike `articles/`, which stores saved external source material, this directory is for **your own case write-ups**.

## Content Type

- Each case is an OKF concept document with `type: System Design Case`.
- Cases are **full interview answers**, not terse takeaways. They mirror the section order of `cases/part-2-url-shortener-system-design.md` and the other Part 2/3 cases.

## File Organization

```
system-design-cases/
├── cases/            # Individual case files
├── templates/        # Reusable templates
├── index.md          # Directory index
└── README.md         # Human guide
```

## Naming Convention

- Files: kebab-case, prefixed by part number — `part-1-rate-limiter.md`, `part-4-web-crawler.md`.
- Headings: H1 = case title; H2 = major sections; H3 = subsections.

## Required Sections

1. Problem Statement
2. Clarifying Questions & Answers
3. Assumptions
4. Constraints
5. Functional Requirements
6. Non-Functional Requirements
7. Back-of-the-Envelope Estimations
8. High-Level Architecture
9. API Design
10. Data Model
11. Tech Stack Options
12. Consistency vs. Availability Trade-offs
13. Failure Modes & Mitigations
14. Security
15. Monitoring & Observability
16. Deployment / CI-CD
17. Cost / Operational Trade-offs
18. Testing Strategies
19. Alternative Approaches
20. References (link back to source articles, official docs, or related repo files)

## Cross-References

- Link relevant terms to `../reference-dictionary/`.
- Link Azure implementations to `../architecture-azure/`.
- Link extracted patterns to `../system-design-architecture/`.

## Validation

After adding or editing a case:

```bash
python3 scripts/okf_migrate.py --check
```
