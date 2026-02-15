# GitHub Copilot Instructions - Azure Learning Repository

> **Repository Type**: Technical documentation (NOT a code repository)  
> **Focus**: Cloud architecture, software engineering patterns, and .NET multithreading

## Quick Start for AI Agents

### Repository Structure

```
azure_learning/
├── architecture-azure/      # Azure-specific (Physical/Implementation layer)
├── architecture-general/    # Cloud-agnostic patterns (Conceptual/Logical layer)
├── dotNet_multi_threading/  # .NET concurrency patterns
└── scripts/                 # Taxonomy sync automation
```

### Where to Add Content (Decision Tree)

```
Is it Azure-specific?
  ├─ YES → architecture-azure/
  │   └─ Which category? compute/, data/, networking/, security/, integration/, etc.
  │
  └─ NO → Is it .NET multithreading?
      ├─ YES → dotNet_multi_threading/
      └─ NO → architecture-general/
          └─ Reference taxonomy: See section below
```

### Subdirectory-Specific Instructions

**IMPORTANT**: Each major section has detailed instructions:
- [`architecture-azure/.copilot-instructions.md`](../architecture-azure/.copilot-instructions.md) - Azure service documentation
- [`architecture-general/.copilot-instructions.md`](../architecture-general/.copilot-instructions.md) - Taxonomy alignment rules

## Core Principles

### 1. Documentation Focus

This is a **knowledge base**, not executable code. Assist with:
- Writing clear, technical documentation
- Creating comprehensive markdown files
- Organizing content hierarchically
- Adding Mermaid diagrams for architecture visualizations

### 2. Taxonomy Alignment

**All content MUST align with the Architecture Taxonomy**:
- 📖 [`architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md`](../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md)
- Use `§X.X` format when referencing taxonomy sections
- Example: `> **Taxonomy Reference**: §3.3 Event-Driven & Messaging`

### 3. Content Quality Standards

- ✅ Technically accurate and current
- ✅ Proper heading hierarchy (H1 → H2 → H3)
- ✅ Include TOC for documents >200 lines
- ✅ Use comparison tables for alternatives
- ✅ Code blocks with language tags
- ✅ Reference official documentation
- ✅ Include practical examples and case studies

## Cross-Reference Patterns

Link between general patterns and Azure implementations:

### From general → Azure
```markdown
> **Azure Implementation**: See [Azure Event Hubs](../architecture-azure/integration/event-hubs/) for Azure-specific details.
```

### From Azure → general
```markdown
> **General Pattern**: [Event-Driven Architecture](../architecture-general/03-integration-communication-architecture/)
> **Taxonomy**: [§3.3 Event-Driven & Messaging](../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md)
```

### Taxonomy Section References
```markdown
> **Taxonomy Reference**: §2 Application & Software Architecture (see [architecture_taxonomy_reference.md](../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md))
```

**Real example**: See [`architecture-general/02-application-software-architecture/07-language-selection/01-uber-go-vs-rust-case-study.md`](../architecture-general/02-application-software-architecture/07-language-selection/01-uber-go-vs-rust-case-study.md)

## Developer Workflows

### Adding New Content

1. **Determine location** using decision tree above
2. **Check taxonomy alignment** - Which §X.X section?
3. **Use appropriate template** (see below)
4. **Add cross-references** to related content
5. **Update parent README.md** with link to new doc
6. **Run taxonomy sync** if you modified `architecture-general/**/README.md`

### Taxonomy Synchronization

The taxonomy reference is **auto-generated** from README.md files:

```bash
# Regenerate from all README.md files
python scripts/sync_taxonomy_reference.py

# Check if sync is needed (for CI/CD)
python scripts/sync_taxonomy_reference.py --check

# Preview without writing
python scripts/sync_taxonomy_reference.py --dry-run
```

**When to sync**:
- ✅ After editing any `architecture-general/**/README.md`
- ✅ Before committing changes to README files
- ⚠️ GitHub Actions auto-checks on PRs (`.github/workflows/sync-taxonomy.yml`)

### Pre-commit Hook (Optional)

Install to automatically check taxonomy sync:

```bash
cp scripts/hooks/pre-commit-taxonomy-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This prevents commits with out-of-sync taxonomy references.

### Language and Technology Selection

When discussing language or technology choices:
1. **Consider organizational factors**: Team size, hiring constraints, velocity requirements
2. **Reference case studies**: See [`architecture-general/02-application-software-architecture/07-language-selection/`](../architecture-general/02-application-software-architecture/07-language-selection/)
3. **Balance trade-offs**: Raw performance vs team productivity vs operational simplicity
4. **Document decisions**: Create ADRs (Architecture Decision Records) for significant choices
5. **Learn from real-world examples**: Uber, Netflix, Amazon case studies provide valuable insights

## Naming Conventions

- **Files**: Use kebab-case: `azure-event-hubs-tiers.md`
- **Directories**: Use kebab-case: `event-hubs/`, `service-bus/`
- **Headings**: Use Title Case for H1, Sentence case for others

## Documentation Templates

### Service Documentation Structure
```markdown
# Service Name

## Overview
Brief description of the service

## Key Features
- Feature 1
- Feature 2

## Architecture
[Mermaid diagram]

## Use Cases
When to use this service

## Pricing Tiers (if applicable)
Comparison table

## Best Practices
Recommendations

## Related Services
Links to related documentation
```

### Comparison Documentation Structure
```markdown
# Service A vs Service B

## Overview
Brief comparison summary

## Feature Comparison
| Feature | Service A | Service B |
|---------|-----------|-----------|

## When to Use Each
Decision criteria

## Migration Considerations
If applicable
```

### Case Study Documentation Structure
```markdown
# Case Study: Organization Name - Decision Title

> **Source**: [Origin]
> **Timeframe**: When this decision was made
> **Relevance**: Current applicability

## Overview
Brief summary of the decision

## The Context
What problem was being solved

## The Decision Matrix
Comparison table of options

## Real-World Implementation
How it was actually implemented

## Key Lessons Learned
Actionable takeaways

## Modern Context
Is this still relevant today?

## Related Documentation
Links to related concepts
```

## Related Instructions

- See `architecture-azure/.copilot-instructions.md` for Azure-specific guidance
- See `architecture-general/.copilot-instructions.md` for general architecture guidance

## Key Reference Documents

- **Architecture Taxonomy**: See `architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md` for comprehensive architecture type definitions, naming conventions, and classification standards
