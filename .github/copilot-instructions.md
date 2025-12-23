# GitHub Copilot Instructions - Azure Learning Repository

## Repository Overview

This is a **technical documentation repository** focused on cloud architecture and software engineering concepts. It contains detailed markdown documentation, NOT executable code.

## Repository Structure

```
azure_learning/
├── architecture-azure/      # Azure-specific architecture documentation
├── architecture-general/    # Cloud-agnostic architecture patterns
└── dotNet_multi_threading/  # .NET multithreading concepts
```

## Content Guidelines

### When Assisting with This Repository

1. **Documentation Focus**: This is a knowledge base, not a code repository. Assist with:
   - Writing clear, technical documentation
   - Creating comprehensive markdown files
   - Organizing content hierarchically
   - Adding diagrams using Mermaid syntax

2. **Technical Accuracy**: Ensure all information is:
   - Technically accurate and up-to-date
   - Well-structured with proper headings
   - Include practical examples where applicable
   - Reference official documentation when relevant

3. **Markdown Best Practices**:
   - Use proper heading hierarchy (H1 → H2 → H3)
   - Include table of contents for long documents
   - Use tables for comparisons
   - Use code blocks with appropriate language tags
   - Use Mermaid diagrams for architecture visualizations

### Cross-Reference Patterns

- Azure-specific implementations should reference general patterns in `architecture-general/`
- General patterns can link to Azure implementations in `architecture-azure/`
- Use relative links for cross-repository references: `../architecture-azure/`

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

## Related Instructions

- See `architecture-azure/.copilot-instructions.md` for Azure-specific guidance
- See `architecture-general/.copilot-instructions.md` for general architecture guidance
