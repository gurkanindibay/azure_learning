#!/usr/bin/env python3
"""
OKF (Open Knowledge Format) Migration Script
Applies OKF v0.1 standards to the azure_learning repository.

OKF Conformance Requirements:
1. Every non-reserved .md file → YAML frontmatter with `type`
2. Directory listings → index.md (not README.md)
3. Reserved: index.md, log.md

Usage:
  python scripts/okf_migrate.py           # Full migration
  python scripts/okf_migrate.py --check   # Validate OKF conformance
  python scripts/okf_migrate.py --dry-run # Preview changes only
"""

import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files/directories to EXCLUDE from migration
EXCLUDE_PATTERNS = [
    '.git/',
    '.github/',
    'scripts/',
    'agent_tools/',
    '.agents/',
    'AGENTS.md',
    '.copilot-instructions.md',
    'accessibility-guidelines.md',
    'architecture_taxonomy_reference.md',  # Auto-generated
]

# Reserved OKF filenames (must not have concept frontmatter)
RESERVED_FILENAMES = {'index.md', 'log.md'}

# Type mapping: directory prefix → OKF `type` value
TYPE_MAPPING = [
    ('architecture-general/', 'Architecture Pattern'),
    ('architecture-azure/', 'Azure Service'),
    ('system-design-architecture/', 'System Design'),
    ('system-design-cases/', 'System Design Case'),
    ('reference-dictionary/', 'Reference'),
    ('programming-languages/', 'Programming Guide'),
    ('articles/', 'Article'),
    ('videos/', 'Video Notes'),
    ('site-reliability-engineering/', 'SRE Guide'),
    ('unstructured-resources/', 'Unstructured Note'),
]

# Directories that should NOT get index.md (no README.md to rename, or not needed)
NO_INDEX_DIRS = {
    'articles/medium/',       # Articles are leaf content
    'articles/linkedin/',
    'articles/personal-blogs/',
    'articles/substack/',
    'unstructured-resources/articles/',
}

OKF_VERSION = '0.1'
TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%d')


def resolve_type(rel_path: str) -> str:
    """Map a file path to its OKF type based on directory."""
    for prefix, okf_type in TYPE_MAPPING:
        if rel_path.startswith(prefix):
            return okf_type
    return 'Reference'


def extract_title(lines: list[str], rel_path: str = '') -> str:
    """Extract title from first H1 heading, or derive from filename."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# ') and not stripped.startswith('## '):
            title = stripped[2:].strip()
            # Remove leading number prefix like "1. " or "01-"
            title = re.sub(r'^\d+[\.\-]\s*', '', title)
            return title
    if rel_path:
        stem = Path(rel_path).stem
        clean_stem = re.sub(r'^\d+[\.\-]\s*', '', stem)
        return clean_stem.replace('-', ' ').title()
    return ''


def extract_description(lines: list[str]) -> str:
    """Extract a one-line description from the content.
    
    Skips headings, TOC entries, table rows, metadata lines, images,
    bold labels, code fences, and other non-paragraph content.
    """
    for line in lines:
        stripped = line.strip()
        # Skip empty lines
        if not stripped:
            continue
        # Skip any heading
        if stripped.startswith('#'):
            continue
        # Skip metadata / blockquote lines
        if stripped.startswith('>'):
            continue
        # Skip table rows and horizontal rules
        if stripped.startswith('|') or stripped.startswith('---'):
            continue
        # Skip TOC entries and course navigation bullets
        if re.match(r'^[-*\d]', stripped) and ('](#' in stripped or '](images/' in stripped or '![](images/' in stripped or stripped.startswith('* *') or stripped.startswith('* **')):
            continue
        if re.search(r'^\d+/\d+\s+completed', stripped, re.IGNORECASE):
            continue
        # Skip short bold labels / chapter numbers like "**02**"
        if stripped.startswith('**') and (len(stripped) < 80 or re.match(r'^\*\*\d+\*\*$', stripped)):
            continue
        # Skip code fences
        if stripped.startswith('```'):
            continue
        # Skip Mermaid/PlantUML diagram directives and syntax
        _mermaid_keywords = ('graph ', 'sequenceDiagram', 'flowchart', 'classDiagram', 
                            'erDiagram', 'gantt', 'pie', 'stateDiagram', 'subgraph',
                            'end', 'style ', 'classDef ', 'click ', 'linkStyle ')
        if any(stripped.startswith(kw) for kw in _mermaid_keywords) and len(stripped) < 120:
            continue
        # Skip image lines and linked images
        if stripped.startswith('![') or stripped.startswith('[!['):
            continue
        # Found first real paragraph
        desc = stripped
        if len(desc) > 200:
            desc = desc[:197] + '...'
        return desc
    return ''


def extract_tags(rel_path: str) -> list[str]:
    """Derive tags from directory path components."""
    parts = Path(rel_path).parts
    tags = []
    
    # Map directory names to tags
    tag_map = {
        'compute': 'compute',
        'data': 'data',
        'networking': 'networking',
        'security': 'security',
        'integration': 'integration',
        'observability': 'observability',
        'governance': 'governance',
        'devops': 'devops',
        'migration': 'migration',
        'container-registry': 'containers',
        'cost-management': 'cost',
        'csharp': 'csharp',
        'dotnet-multi-threading': 'dotnet',
        'event-driven-messaging': 'event-driven',
        'api-architecture': 'api',
        'domain-driven-design': 'ddd',
        'design-patterns': 'design-patterns',
        'cqrs-event-driven': 'cqrs',
        'resilience': 'resilience',
        'ai-ml-llm': 'ai',
        'messaging': 'messaging',
        'caching': 'caching',
        'fintech': 'fintech',
        'media-processing': 'media',
        'hsm-cryptography': 'security',
        'data-concurrency': 'concurrency',
        'architecture-patterns': 'architecture',
        'azure-services': 'azure',
        'api-design': 'api',
        'system-design-cases': 'system-design',
        'bytebytego': 'system-design',
        'cases': 'system-design',
        'azure-cohort': 'azure',
        'unstructured-resources': 'notes',
    }
    
    for part in parts[:-1]:  # Exclude filename
        part_lower = part.lower()
        if part_lower in tag_map:
            tags.append(tag_map[part_lower])
        elif part_lower.startswith(('01-', '02-', '03-', '04-', '05-', '06-', '07-', '08-', '09-', '10-', '11-', '12-')):
            # Section directories like "01-enterprise-strategic-architecture"
            tags.append(part_lower.split('-', 1)[1] if '-' in part_lower else part_lower)
    
    # Deduplicate while preserving order
    seen = set()
    unique_tags = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    
    return unique_tags[:5]  # Max 5 tags


def has_frontmatter(content: str) -> bool:
    """Check if content already has YAML frontmatter."""
    return content.startswith('---\n') or content.startswith('---\r\n')


def add_frontmatter(content: str, rel_path: str, force: bool = False) -> str:
    """Add or regenerate OKF YAML frontmatter for a markdown file.
    
    Args:
        content: The full file content.
        rel_path: Relative path from repo root.
        force: If True, replace existing frontmatter entirely.
    
    Returns:
        Content with proper OKF frontmatter.
    """
    okf_type = resolve_type(str(rel_path))
    
    if has_frontmatter(content) and not force:
        # Only inject missing `type` — preserve existing frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            if not re.search(r'^type:\s*\S', fm_text, re.MULTILINE):
                new_fm = f'---\ntype: {okf_type}\n{fm_text}\n---'
                rest = content[fm_match.end():]
                return new_fm + rest
        return content
    
    # Determine body text (without any existing frontmatter)
    if has_frontmatter(content):
        # Strip existing frontmatter to get clean body
        fm_end = content.find('---\n', 3) + 4
        body = content[fm_end:].lstrip('\n')
    else:
        body = content
    
    # Extract metadata from body only (not from old frontmatter)
    body_lines = body.split('\n')
    title = extract_title(body_lines, rel_path=str(rel_path))
    description = extract_description(body_lines)
    tags = extract_tags(str(rel_path))
    
    # Build frontmatter
    fm_lines = ['---']
    fm_lines.append(f'type: {okf_type}')
    if title:
        fm_lines.append(f'title: "{title}"')
    if description:
        desc_escaped = description.replace('"', '\\"')
        fm_lines.append(f'description: "{desc_escaped}"')
    if tags:
        tag_str = ', '.join(tags)
        fm_lines.append(f'tags: [{tag_str}]')
    fm_lines.append(f'timestamp: {TODAY}T00:00:00Z')
    fm_lines.append('---')
    fm_lines.append('')
    
    return '\n'.join(fm_lines) + '\n' + body


def should_exclude(rel_path: str) -> bool:
    """Check if a file should be excluded from migration."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in rel_path:
            return True
    return False


def is_reserved(filename: str) -> bool:
    """Check if filename is an OKF reserved name."""
    return filename in RESERVED_FILENAMES


def is_poor_description(desc: str) -> bool:
    """Check if a description looks like an accidentally extracted TOC item, table label, etc."""
    if not desc:
        return False
    # TOC entries and navigation links
    if re.match(r'^[-*\d]', desc) and ('](#' in desc or '](images/' in desc or '![](images/' in desc or desc.startswith('* *') or desc.startswith('* **')):
        return True
    if re.search(r'^\d+/\d+\s+completed', desc, re.IGNORECASE):
        return True
    if desc.startswith('[![') or desc.startswith('!['):
        return True
    # Bold labels
    if desc.startswith('**') and (len(desc) < 80 or re.match(r'^\*\*\d+\*\*$', desc)):
        return True
    # Table header-lines or separator-only
    if desc.startswith('|') or desc.startswith('---'):
        return True
    # Code fences and Mermaid/PlantUML directives
    if desc.startswith('```'):
        return True
    _mermaid_keywords = ('graph ', 'sequenceDiagram', 'flowchart', 'classDiagram', 
                         'erDiagram', 'gantt', 'pie', 'stateDiagram', 'subgraph',
                         'end', 'style ', 'classDef ', 'click ', 'linkStyle ')
    if any(desc.startswith(kw) for kw in _mermaid_keywords) and len(desc) < 120:
        return True
    # Leaked YAML frontmatter keys in description body
    if re.match(r'^(type|title|description|tags|timestamp|resource|okf_version):\s', desc):
        return True
    return False


def migrate_file(filepath: Path, dry_run: bool = False) -> dict:
    """Add OKF frontmatter to a single concept .md file."""
    rel_path = filepath.relative_to(REPO_ROOT)
    
    if should_exclude(str(rel_path)):
        return {'status': 'skipped', 'reason': 'excluded', 'file': str(rel_path)}
    
    if is_reserved(filepath.name):
        return {'status': 'skipped', 'reason': 'reserved', 'file': str(rel_path)}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fully OKF-conformant with good metadata
    force_regenerate = False
    if has_frontmatter(content):
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            has_type = bool(re.search(r'^type:\s*\S', fm_text, re.MULTILINE))
            if has_type:
                desc_match = re.search(r'^description:\s*"?(.*?)"?\s*$', fm_text, re.MULTILINE)
                if desc_match and not is_poor_description(desc_match.group(1).strip('"')):
                    return {'status': 'skipped', 'reason': 'already_okf', 'file': str(rel_path)}
                # Has type but poor/missing description — force regenerate
                force_regenerate = True
    
    new_content = add_frontmatter(content, rel_path, force=force_regenerate)
    
    if dry_run:
        fm_end = new_content.find('---\n\n', 4) + 5
        preview = new_content[fm_end:fm_end+200] if fm_end > 5 else new_content[:200]
        return {
            'status': 'would_migrate',
            'file': str(rel_path),
            'type': resolve_type(str(rel_path)),
            'title': extract_title(content.split('\n'), rel_path=str(rel_path)),
            'preview': preview
        }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return {'status': 'migrated', 'file': str(rel_path)}


def migrate_readme_to_index(dirpath: Path, dry_run: bool = False) -> dict:
    """Rename README.md to index.md in a directory."""
    readme = dirpath / 'README.md'
    index = dirpath / 'index.md'
    rel_dir = str(dirpath.relative_to(REPO_ROOT))
    
    if not readme.exists():
        return {'status': 'no_readme', 'dir': rel_dir}
    
    if index.exists() and not dry_run:
        return {'status': 'skipped', 'reason': 'index_exists', 'dir': rel_dir}
    
    if dry_run:
        return {'status': 'would_rename', 'from': str(readme.relative_to(REPO_ROOT)), 'to': str(index.relative_to(REPO_ROOT))}
    
    # Read README content
    with open(readme, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Write to index.md
    with open(index, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Remove README.md
    readme.unlink()
    
    return {'status': 'renamed', 'from': str(readme.relative_to(REPO_ROOT)), 'to': str(index.relative_to(REPO_ROOT))}


def find_all_readme_dirs() -> list[Path]:
    """Find all directories containing README.md."""
    dirs = []
    for root, _, files in os.walk(REPO_ROOT):
        if 'README.md' in files:
            root_path = Path(root)
            rel = str(root_path.relative_to(REPO_ROOT))
            
            # Skip excluded dirs
            if should_exclude(rel + '/'):
                continue
            
            # Skip leaf article directories
            skip = False
            for no_idx in NO_INDEX_DIRS:
                if rel + '/' == no_idx or (rel + '/').startswith(no_idx):
                    skip = True
                    break
            if skip:
                continue
            
            # Skip the repo root (we'll create that manually)
            if rel == '.':
                continue
            
            dirs.append(root_path)
    
    return sorted(dirs)


def find_all_concept_files() -> list[Path]:
    """Find all concept .md files (non-reserved, non-excluded)."""
    files = []
    for root, _, filenames in os.walk(REPO_ROOT):
        for fname in filenames:
            if not fname.endswith('.md'):
                continue
            if is_reserved(fname):
                continue
            if fname == 'README.md':
                continue  # README.md is being renamed to index.md
            
            filepath = Path(root) / fname
            rel = str(filepath.relative_to(REPO_ROOT))
            
            if should_exclude(rel):
                continue
            
            # Also skip if the file no longer exists (was renamed)
            if not filepath.exists():
                continue
            
            files.append(filepath)
    
    return sorted(files)


def create_root_index(dry_run: bool = False):
    """Create bundle-root index.md with OKF version declaration."""
    index_path = REPO_ROOT / 'index.md'
    
    content = f"""---
okf_version: "{OKF_VERSION}"
---

# Azure Learning Knowledge Bundle

> **OKF Bundle**: This repository follows the [Open Knowledge Format (OKF) v{OKF_VERSION}](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) for agent-friendly knowledge representation.

A technical knowledge base covering Microsoft Azure services, cloud-agnostic architecture patterns, system design strategies, programming language guides (.NET, C#), SRE practices, and AI/agentic systems. Content is organized by domain and cross-referenced for both human and AI agent consumption.

## Architecture Patterns

* [Architecture — General](/architecture-general/) — Cloud-agnostic architectural patterns, taxonomy-aligned across 12 sections
* [Architecture — Azure](/architecture-azure/) — Azure-specific service deep-dives, tier comparisons, and implementation guides

## System Design

* [System Design Architecture](/system-design-architecture/) — Problem → strategy reference with domain-prefixed IDs and Azure mappings
* [System Design Cases](/system-design-cases/) — Original interview case write-ups in the style of the Medium source articles

## Reference

* [Reference Dictionary](/reference-dictionary/) — Single-source technical glossary with stable anchors for cross-referencing

## Programming Languages

* [C# / .NET](/programming-languages/csharp/) — .NET concurrency patterns, multithreading, and best practices

## Operations

* [Site Reliability Engineering](/site-reliability-engineering/) — SRE practices, incident management, and AIOps

## Source Material

* [Articles](/articles/) — Source articles organized by platform (Medium, LinkedIn, Substack)
* [Videos](/videos/) — Video-based learning resources with structured notes
"""
    
    if dry_run:
        print(f"[DRY-RUN] Would create: {index_path}")
        return
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[CREATED] {index_path}")


def create_root_log(dry_run: bool = False):
    """Create bundle-root log.md."""
    log_path = REPO_ROOT / 'log.md'
    
    content = f"""# Bundle Update Log

## {TODAY}
* **Update**: Applied OKF v{OKF_VERSION} frontmatter to all concept documents.
* **Update**: Renamed README.md files to index.md per OKF conventions.
* **Creation**: Added bundle-root index.md and log.md.

## Prior
* **Initialization**: Repository established as a technical knowledge base.
"""
    
    if dry_run:
        print(f"[DRY-RUN] Would create: {log_path}")
        return
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[CREATED] {log_path}")


def validate_conformance() -> tuple[int, int, list[str]]:
    """Check OKF conformance. Returns (pass_count, fail_count, errors)."""
    errors = []
    fail_count = 0
    pass_count = 0
    
    concept_files = find_all_concept_files()
    
    for filepath in concept_files:
        rel = str(filepath.relative_to(REPO_ROOT))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not has_frontmatter(content):
            errors.append(f"  FAIL [{rel}]: Missing YAML frontmatter")
            fail_count += 1
            continue
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            errors.append(f"  FAIL [{rel}]: Unparseable frontmatter")
            fail_count += 1
            continue
        
        fm_text = match.group(1)
        
        # Check for required `type` field
        type_match = re.search(r'^type:\s*(.+)', fm_text, re.MULTILINE)
        if not type_match or not type_match.group(1).strip():
            errors.append(f"  FAIL [{rel}]: Missing or empty 'type' field")
            fail_count += 1
            continue
        
        pass_count += 1
    
    return pass_count, fail_count, errors


def main():
    parser = argparse.ArgumentParser(description='OKF Migration Tool')
    parser.add_argument('--check', action='store_true', help='Validate OKF conformance')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    args = parser.parse_args()
    
    if args.check:
        print("Validating OKF conformance...\n")
        pass_count, fail_count, errors = validate_conformance()
        
        for err in errors:
            print(err)
        
        print(f"\nResults: {pass_count} passed, {fail_count} failed")
        
        if fail_count > 0:
            print("\n❌ Bundle is NOT OKF conformant.")
            sys.exit(1)
        else:
            print("\n✅ Bundle is OKF conformant.")
        return
    
    dry_run = args.dry_run
    if dry_run:
        print("=== OKF Migration -- DRY RUN ===\n")
    else:
        print("=== OKF Migration ===\n")
    
    # Step 1: Create root infrastructure
    print("\n── Root Infrastructure ──")
    create_root_index(dry_run=dry_run)
    create_root_log(dry_run=dry_run)
    
    # Step 2: Rename README.md → index.md
    print("\n── README → index Migration ──")
    readme_dirs = find_all_readme_dirs()
    for dirpath in readme_dirs:
        result = migrate_readme_to_index(dirpath, dry_run=dry_run)
        if result['status'] in ('renamed', 'would_rename'):
            print(f"  {'[DRY-RUN] ' if dry_run else ''}{result['from']} → {result['to']}")
    
    # Step 3: Add frontmatter to concept files
    print("\n── Frontmatter Migration ──")
    concept_files = find_all_concept_files()
    migrated = 0
    skipped = 0
    
    for filepath in concept_files:
        result = migrate_file(filepath, dry_run=dry_run)
        if result['status'] in ('migrated', 'would_migrate'):
            migrated += 1
            if dry_run:
                print(f"  [DRY-RUN] {result['file']} (type: {result['type']}, title: {result.get('title', 'N/A')})")
        elif result['status'] == 'skipped':
            skipped += 1
    
    print(f"\n  {'Would migrate' if dry_run else 'Migrated'}: {migrated}, Skipped: {skipped}")
    
    if dry_run:
        print("\n[DRY-RUN] No files were modified. Run without --dry-run to apply changes.")
    else:
        print("\n✅ OKF migration complete!")
        print("Run 'python scripts/okf_migrate.py --check' to validate conformance.")


if __name__ == '__main__':
    main()
