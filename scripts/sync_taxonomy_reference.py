#!/usr/bin/env python3
"""
Sync Architecture Taxonomy Reference

This script automatically generates/updates the architecture_taxonomy_reference.md
file by aggregating content from all README.md files in the architecture-general
directory structure.

Usage:
    python scripts/sync_taxonomy_reference.py [--dry-run] [--check]

Options:
    --dry-run   Preview changes without writing to file
    --check     Check if taxonomy is in sync (useful for CI/CD)
"""

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
ARCHITECTURE_GENERAL_DIR = BASE_DIR / "architecture-general"
TAXONOMY_FILE = ARCHITECTURE_GENERAL_DIR / "10-practicality-taxonomy" / "architecture_taxonomy_reference.md"

# Directory mapping to taxonomy sections (order matters)
DIRECTORY_MAPPING = [
    ("01-enterprise-strategic-architecture", "1. Enterprise & Strategic Architecture"),
    ("02-application-software-architecture", "2. Application & Software Architecture"),
    ("03-integration-communication-architecture", "3. Integration & Communication Architecture"),
    ("04-data-analytics-ai-architecture", "4. Data, Analytics & AI Architecture"),
    ("05-cloud-infrastructure-platform-architecture", "5. Cloud, Infrastructure & Platform Architecture"),
    ("06-security-architecture", "6. Security Architecture (Cross-Cutting)"),
    ("07-reliability-performance-operations", "7. Reliability, Performance & Operations"),
    ("08-devops-delivery-runtime-architecture", "8. DevOps, Delivery & Runtime Architecture"),
    ("09-industry-specialized-architectures", "9. Industry & Specialized Architectures"),
    ("10-practicality-taxonomy", "10. Practicality Taxonomy (Abstraction Levels)"),
    ("11-architectural-qualities", "11. Architectural Qualities (Non-Functional)"),
]


def read_readme(dir_path: Path) -> str | None:
    """Read README.md from a directory if it exists."""
    readme_path = dir_path / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return None


def extract_content_from_readme(content: str) -> dict:
    """Extract structured content from a README.md file."""
    result = {
        "title": "",
        "description": "",
        "subsections": [],
    }
    
    lines = content.strip().split("\n")
    
    # Extract title (first H1)
    for line in lines:
        if line.startswith("# "):
            result["title"] = line[2:].strip()
            break
    
    # Extract description (first paragraph after title)
    in_description = False
    description_lines = []
    for line in lines:
        if line.startswith("# "):
            in_description = True
            continue
        if in_description:
            if line.strip() == "":
                if description_lines:
                    break
                continue
            if line.startswith("#"):
                break
            description_lines.append(line.strip())
    result["description"] = " ".join(description_lines)
    
    # Extract subsections (H3 headers and their bullet points)
    current_subsection = None
    for line in lines:
        if line.startswith("### "):
            if current_subsection:
                result["subsections"].append(current_subsection)
            current_subsection = {
                "title": line[4:].strip(),
                "items": []
            }
        elif current_subsection and line.strip().startswith("- "):
            # Extract just the item name (before any arrows or links)
            item = line.strip()[2:]
            # Remove markdown links and arrows
            item = re.sub(r'\s*→.*$', '', item)
            item = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', item)
            item = item.strip()
            if item:
                current_subsection["items"].append(item)
    
    if current_subsection:
        result["subsections"].append(current_subsection)
    
    return result


def generate_toc() -> str:
    """Generate table of contents."""
    toc_sections = []
    
    for dir_name, section_title in DIRECTORY_MAPPING:
        dir_path = ARCHITECTURE_GENERAL_DIR / dir_name
        readme_content = read_readme(dir_path)
        
        if not readme_content:
            continue
            
        content = extract_content_from_readme(readme_content)
        
        # Create anchor from section title
        anchor = section_title.lower()
        anchor = re.sub(r'[^a-z0-9\s-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'-+', '-', anchor)
        
        subsection_links = []
        for subsection in content["subsections"]:
            sub_anchor = subsection["title"].lower()
            sub_anchor = re.sub(r'[^a-z0-9\s-]', '', sub_anchor)
            sub_anchor = re.sub(r'\s+', '-', sub_anchor)
            sub_anchor = re.sub(r'-+', '-', sub_anchor)
            subsection_links.append(f'  - [{subsection["title"]}](#{sub_anchor})')
        
        toc_entry = f"""<details>
<summary><a href="#{anchor}">{section_title}</a></summary>

{chr(10).join(subsection_links)}
</details>"""
        toc_sections.append(toc_entry)
    
    return "\n\n".join(toc_sections)


def generate_section_content(dir_name: str, section_title: str) -> str:
    """Generate content for a single taxonomy section."""
    dir_path = ARCHITECTURE_GENERAL_DIR / dir_name
    readme_content = read_readme(dir_path)
    
    if not readme_content:
        return ""
    
    content = extract_content_from_readme(readme_content)
    
    lines = [f"## {section_title}"]
    
    for subsection in content["subsections"]:
        lines.append(f"\n### {subsection['title']}")
        for item in subsection["items"]:
            lines.append(f"- {item}")
    
    lines.append("\n---")
    
    return "\n".join(lines)


def generate_static_sections() -> dict:
    """Return static sections that don't come from READMEs."""
    return {
        "header": """# Architecture Taxonomy – Comprehensive Reference

This document is a **canonical markdown reference** for commonly recognized architecture types used in enterprise, cloud, and software engineering contexts. It is suitable for **architecture handbooks, governance boards, interviews, and internal standards**.

> **Auto-generated**: This file is automatically synchronized with README.md files in the architecture-general directory structure.
> 
> **Last updated**: {timestamp}
> 
> **To regenerate**: Run `python scripts/sync_taxonomy_reference.py`

---

## Table of Contents

""",
        "practicality_taxonomy": """## 10. Practicality Taxonomy (Abstraction Levels)

This taxonomy classifies architectures by their **level of abstraction** and **proximity to implementation**. It helps distinguish between conceptual frameworks and deployment-ready patterns.

### 10.1 Conceptual Architecture (Strategic / Abstract)
High-level, technology-agnostic representations that focus on **business intent, capabilities, and relationships**. Used for stakeholder communication, governance, and strategic planning.

**Characteristics:**
- Technology-agnostic
- Business-aligned vocabulary
- Focus on "what" not "how"
- Long-term vision (3–5+ years)

**Examples:**
- Enterprise Architecture
- Business Architecture
- Capability Architecture
- Value Stream Architecture
- Information Architecture
- Governance Architecture

### 10.2 Logical Architecture (Design / Structural)
Technology-aware but vendor-neutral representations that define **components, boundaries, and interactions**. Bridges conceptual intent with implementation constraints.

**Characteristics:**
- Defines logical components and responsibilities
- Establishes integration patterns
- Technology-aware but not vendor-specific
- Medium-term horizon (1–3 years)

**Examples:**
- Application Architecture Styles (Layered, Hexagonal, Clean)
- Event-Driven Architecture
- API Architecture
- Data Architecture (OLTP/OLAP)
- Security Architecture (Zero Trust)
- Microservices Architecture

### 10.3 Physical / Implementation Architecture (Tactical / Concrete)
Vendor-specific, deployment-ready representations that define **actual technologies, configurations, and infrastructure**. Directly translatable to code and infrastructure.

**Characteristics:**
- Vendor/product-specific
- Includes concrete configurations
- Deployable and testable
- Short-term horizon (weeks–12 months)

**Examples:**
- Kubernetes Architecture
- Serverless Architecture (AWS Lambda, Azure Functions)
- CI/CD Architecture (GitHub Actions, Azure DevOps)
- Container Architecture (Docker, Podman)
- Cloud Architecture (Azure, AWS, GCP-specific)
- Infrastructure as Code (Terraform, Bicep)

### 10.4 Runtime / Operational Architecture (Execution / Live)
Represents the **actual running state** of systems, including real-time topology, traffic flows, and operational metrics.

**Characteristics:**
- Reflects live system state
- Dynamic and observable
- Includes operational concerns (scaling, failover)
- Continuous (real-time)

**Examples:**
- Blue-Green Deployment
- Canary Deployment
- Observability Architecture
- Chaos Engineering Architecture
- Load Balancing Architecture
- Disaster Recovery (Active-Active, Active-Passive)

---

### Practicality Spectrum Summary

| Level | Focus | Horizon | Audience |
|-------|-------|---------|----------|
| **Conceptual** | Business intent & capabilities | 3–5+ years | Executives, Business Stakeholders |
| **Logical** | Components & patterns | 1–3 years | Architects, Tech Leads |
| **Physical** | Technologies & configurations | Weeks–12 months | Engineers, DevOps |
| **Runtime** | Live state & operations | Real-time | SRE, Operations |

---
""",
        "qualities": """## 11. Architectural Qualities (Non-Functional)

These apply **across all architecture types**:

- Scalability
- Security
- Reliability & Resilience
- Performance
- Maintainability
- Extensibility
- Portability
- Compliance & Regulatory
- Sustainability (Green IT)

---
""",
        "naming_convention": """## Recommended Naming Convention

```
[Domain] + [Layer] + [Primary Concern]
```

### Examples
- Cloud-Native Event-Driven Backend Architecture
- Mobile + API + Zero Trust Security Architecture
- Lakehouse Analytics Data Architecture
- AI Inference Platform Architecture

---

**Status:** Living document – automatically synchronized with README.md files in architecture-general directory.
""",
    }


def generate_full_taxonomy() -> str:
    """Generate the complete taxonomy reference document."""
    static = generate_static_sections()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sections = []
    
    # Header with TOC
    sections.append(static["header"].format(timestamp=timestamp))
    sections.append(generate_toc())
    sections.append("\n---\n")
    
    # Generate dynamic sections from READMEs (sections 1-9)
    for dir_name, section_title in DIRECTORY_MAPPING[:9]:
        section_content = generate_section_content(dir_name, section_title)
        if section_content:
            sections.append(section_content)
    
    # Add static detailed sections (10-11)
    sections.append(static["practicality_taxonomy"])
    sections.append(static["qualities"])
    sections.append(static["naming_convention"])
    
    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Architecture Taxonomy Reference with README.md files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to file"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if taxonomy is in sync (exit code 1 if out of sync)"
    )
    args = parser.parse_args()
    
    print("🔍 Scanning README.md files in architecture-general/...")
    
    new_content = generate_full_taxonomy()
    
    if args.dry_run:
        print("\n📄 Generated content preview:\n")
        print("=" * 60)
        print(new_content[:2000])
        print("\n... (truncated)")
        print("=" * 60)
        print(f"\n✅ Dry run complete. Total length: {len(new_content)} characters")
        return 0
    
    if args.check:
        if TAXONOMY_FILE.exists():
            current_content = TAXONOMY_FILE.read_text(encoding="utf-8")
            # Remove timestamp line for comparison
            current_clean = re.sub(r'\*\*Last updated\*\*:.*\n', '', current_content)
            new_clean = re.sub(r'\*\*Last updated\*\*:.*\n', '', new_content)
            
            if current_clean.strip() == new_clean.strip():
                print("✅ Taxonomy reference is in sync with README.md files")
                return 0
            else:
                print("❌ Taxonomy reference is OUT OF SYNC with README.md files")
                print("   Run 'python scripts/sync_taxonomy_reference.py' to update")
                return 1
        else:
            print("❌ Taxonomy reference file does not exist")
            return 1
    
    # Write the file
    TAXONOMY_FILE.parent.mkdir(parents=True, exist_ok=True)
    TAXONOMY_FILE.write_text(new_content, encoding="utf-8")
    
    print(f"✅ Updated: {TAXONOMY_FILE.relative_to(BASE_DIR)}")
    print(f"   Total sections: {len(DIRECTORY_MAPPING)}")
    print(f"   Total characters: {len(new_content)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
