#!/usr/bin/env python3
"""
Agent 2: Key Takeaways Agent

Creates system-design-architecture takeaway files from source articles.
Extracts ID-prefixed key points, problem→strategy→tradeoff patterns,
and cross-references following the repository convention.

Produces files like:
    system-design-architecture/23-circuit-breaker-key-takeaways.md
    system-design-architecture/28-agent-harness-key-takeaways.md

The agent:
    1. Reads a source article (in articles/ or raw)
    2. Identifies key architectural concepts
    3. Assigns domain-prefixed IDs (cb-, cqrs-, harness-, docker-, etc.)
    4. Generates the structured takeaway file with Contents table
    5. Adds cross-references to related system-design files and reference-dictionary

This agent is OPTIONAL — not every article needs a takeaway file.

Usage:
    python3 agent_tools/takeaways_agent.py extract <article.md> [--prefix <domain>] [--dry-run]
    python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>
    python3 agent_tools/takeaways_agent.py list-domains

Part of the coordinated agent workflow:
    Agent 1 (format) → Agent 2 (takeaways) → Agent 3 (dictionary)
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ── Domain prefix registry ──────────────────────────────────────────────────
# Loaded from config.yaml + auto-discovered from filesystem.
# To add a new domain:
#   1. Add entry to agent_tools/config.yaml under takeaway_domains (optional)
#   2. Or just create a new *-key-takeaways.md file in system-design-architecture/
#      and the agents will auto-discover it.
# See: agent_tools/config_loader.py

def _get_domain_registry() -> dict:
    """Lazy-load domain registry from config + auto-discovery."""
    _ensure_path()
    from agent_tools.config_loader import load_config
    return load_config().takeaway_domains


def _get_domain_keywords() -> dict:
    """Lazy-load keyword mappings from config."""
    _ensure_path()
    from agent_tools.config_loader import load_config
    return load_config().takeaway_keywords


def _ensure_path():
    """Ensure repo root is on sys.path for imports."""
    import sys
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


# ── Next available number ───────────────────────────────────────────────────

def get_next_number() -> int:
    """Get the next available file number in system-design-architecture/."""
    sda_dir = REPO_ROOT / "system-design-architecture"
    existing = []
    for f in sda_dir.glob("*.md"):
        m = re.match(r'^(\d+)-', f.name)
        if m:
            existing.append(int(m.group(1)))
    return max(existing) + 1 if existing else 29


# ── Content extraction ──────────────────────────────────────────────────────

def extract_article_metadata(content: str, filepath: Path) -> dict:
    """Extract metadata from an article."""
    lines = content.split("\n")

    # Skip frontmatter
    body_start = 0
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end > 0:
            body_start = end + 5

    body_text = content[body_start:]
    body_lines = body_text.split("\n")

    title = ""
    author = ""
    source = str(filepath.relative_to(REPO_ROOT))

    for line in body_lines[:30]:
        stripped = line.strip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
        m = re.match(r'>\s*\*\*Author\*\*:\s*(.+)', stripped)
        if m:
            author = m.group(1).strip()

    # Extract section headings for takeaway candidates
    sections = []
    for i, line in enumerate(body_lines):
        m = re.match(r'^##\s+(.+)', line.strip())
        if m:
            sections.append({"heading": m.group(1).strip(), "line": i})

    return {
        "title": title,
        "author": author,
        "source": source,
        "sections": sections,
        "body_lines": body_lines,
    }


def suggest_prefix(content: str) -> list[tuple[str, float]]:
    """Suggest domain prefixes based on content keywords."""
    content_lower = content.lower()
    scores: dict[str, float] = {}

    for keyword, prefix in _get_domain_keywords().items():
        count = content_lower.count(keyword)
        if count > 0:
            scores[prefix] = scores.get(prefix, 0) + count

    # Sort by score descending
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:5]


# ── Takeaway file generation ────────────────────────────────────────────────

def generate_takeaway_file(
    article_path: Path,
    prefix: str,
    takeaways: list[dict],
    dry_run: bool = False,
) -> str | None:
    """Generate a system-design-architecture takeaway file.

    Args:
        article_path: Path to the source article
        prefix: Domain prefix (e.g., 'cb', 'cqrs')
        takeaways: List of takeaway dicts with {id, problem, concept, body}
        dry_run: If True, return content without writing

    Returns:
        Path of generated file, or content string if dry_run
    """
    article_rel = str(article_path.relative_to(REPO_ROOT))

    # Read article for metadata
    content = article_path.read_text(encoding="utf-8")
    meta = extract_article_metadata(content, article_path)

    # Build title
    domain_info = _get_domain_registry().get(prefix, {"desc": prefix.upper()})
    domain_desc = domain_info["desc"]
    title = f"{domain_desc} — Key Takeaways"

    # Determine file number and name
    num = get_next_number()
    filename = f"{num:02d}-{prefix}-key-takeaways.md"
    output_path = REPO_ROOT / "system-design-architecture" / filename

    # Build the document
    lines = []

    # Frontmatter
    lines.append("---")
    lines.append(f"type: System Design")
    lines.append(f'title: "{title}"')
    if meta["title"]:
        short_desc = meta["title"][:200]
        lines.append(f'description: "{short_desc}"')
    lines.append(f"timestamp: {TODAY}T00:00:00Z")
    lines.append("---")
    lines.append("")

    # H1
    lines.append(f"# {num}. {title}")
    lines.append("")

    # Metadata block
    lines.append(f"> **Parent**: [System Design Interview Reference](index.md)")
    lines.append(f"> **Source**: [{meta['title'] or article_path.stem}](../{article_rel})")
    if meta["author"]:
        lines.append(f"> **Author**: {meta['author']}")
    lines.append(f"> **Purpose**: Extract reusable architectural patterns and key takeaways from the source article.")
    lines.append("")

    # Cross-references (user should fill these in)
    lines.append("> **Also see**: [Related patterns] — TODO: fill in")
    lines.append("> **Dictionary**: [Reference Dictionary](../reference-dictionary/) — TODO: link relevant terms")
    lines.append(f"> **Taxonomy Reference**: § TODO")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Contents table
    lines.append("## Contents")
    lines.append("")
    for t in takeaways:
        cid = t["id"]
        problem = t.get("problem", "TODO")
        concept = t.get("concept", "TODO")
        anchor = cid.replace(" ", "-").lower()
        lines.append(f"- [{cid}: {problem}](#{anchor}) — {concept}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Individual takeaway sections
    for t in takeaways:
        cid = t["id"]
        anchor = cid.replace(" ", "-").lower()
        problem = t.get("problem", "TODO")
        concept = t.get("concept", "TODO")
        body = t.get("body", "")

        lines.append(f"## {cid}: {problem}")
        lines.append("")
        if "source_anchor" in t:
            lines.append(f"> **Source**: [{t['source_anchor']['text']}](../{article_rel}#{t['source_anchor']['anchor']})")
        else:
            lines.append(f"> **Source**: [{meta['title'] or 'Article'}](../{article_rel})")
        lines.append("")

        lines.append("| | |")
        lines.append("|:---|:---|")
        lines.append(f"| **Problem** | {problem} |")
        lines.append(f"| **Key Concept** | {concept} |")
        lines.append("")

        if body:
            lines.append(body)
            lines.append("")

        lines.append("---")
        lines.append("")

    output = "\n".join(lines)

    if dry_run:
        return output

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    return str(output_path.relative_to(REPO_ROOT))


# ── CLI ──────────────────────────────────────────────────────────────────────

def cmd_extract(args: list[str]) -> int:
    """Extract key takeaways from an article."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/takeaways_agent.py extract <article.md> [--prefix <domain>] [--dry-run]")
        return 1

    article_rel = args[1]
    article_path = REPO_ROOT / article_rel
    if not article_path.exists():
        print(f"File not found: {article_rel}")
        return 1

    # Parse flags
    prefix = None
    dry_run = False
    i = 2
    while i < len(args):
        if args[i] == "--prefix" and i + 1 < len(args):
            prefix = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    content = article_path.read_text(encoding="utf-8")

    # Suggest prefix if not provided
    if not prefix:
        suggestions = suggest_prefix(content)
        if suggestions:
            print("Suggested domain prefixes:")
            for p, score in suggestions:
                info = _get_domain_registry().get(p, {"desc": "unknown"})
                print(f"  {p:<10} {info['desc']:<30} (score: {score})")
            print()
            prefix = suggestions[0][0]
            print(f"Using: {prefix} (pass --prefix to override)")
        else:
            print("Could not determine a domain prefix. Use --prefix to specify one.")
            print(f"Available: {', '.join(sorted(_get_domain_registry().keys()))}")
            return 1

    if prefix not in _get_domain_registry():
        print(f"Unknown prefix: {prefix}")
        print(f"Available: {', '.join(sorted(DOMAIN_REGISTRY.keys()))}")
        return 1

    # Extract article structure
    meta = extract_article_metadata(content, article_path)
    print(f"Article: {meta['title']}")
    print(f"Sections found: {len(meta['sections'])}")
    print()

    # Build takeaways from sections (template — user fills in details)
    takeaways = []
    for i, sec in enumerate(meta["sections"], 1):
        takeaways.append({
            "id": f"{prefix}-{i:02d}",
            "problem": f"[From: {sec['heading'][:60]}]",
            "concept": "TODO: Fill in the key architectural concept",
            "source_anchor": {
                "text": f"§\"{sec['heading'][:40]}\"",
                "anchor": sec["heading"].lower().replace(" ", "-").replace("—", "").replace("'", ""),
            },
            "body": "> **Strategy**: TODO\n>\n> **Tradeoff**: TODO\n>\n> **Cross-reference**: TODO",
        })

    # Generate
    result = generate_takeaway_file(article_path, prefix, takeaways, dry_run=dry_run)

    if dry_run:
        print("── DRY RUN ──")
        print(result[:2000])
        print("...")
        print(f"\nWould write {len(takeaways)} takeaway(s) with prefix '{prefix}'.")
    else:
        print(f"✅ Created: {result}")
        print(f"   {len(takeaways)} takeaway(s) with prefix '{prefix}'")
        print()
        print("⚠ TODO: Edit the generated file to fill in:")
        print("   - Problem descriptions and key concepts for each takeaway")
        print("   - Strategy and Tradeoff sections")
        print("   - Cross-references (Also see, Dictionary, Taxonomy)")
        print(f"\n── Next Steps ──")
        print(f"   Agent 3 (dictionary):  python3 agent_tools/dictionary_agent.py extract-terms {result}")

    return 0


def cmd_suggest_prefix(args: list[str]) -> int:
    """Suggest a domain prefix for an article."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/takeaways_agent.py suggest-prefix <article.md>")
        return 1

    article_path = REPO_ROOT / args[1]
    if not article_path.exists():
        print(f"File not found: {args[1]}")
        return 1

    content = article_path.read_text(encoding="utf-8")
    suggestions = suggest_prefix(content)

    for prefix, score in suggestions:
        info = _get_domain_registry().get(prefix, {"desc": "unknown", "file": "?"})
        print(f"  {prefix:<12} {info['desc']:<35} score={score}  (file: {info['file']})")

    return 0


def cmd_list_domains(args: list[str]) -> int:
    """List all domain prefixes."""
    print(f"{'Prefix':<12} {'Description':<35} {'File'}")
    print("-" * 80)
    for prefix in sorted(_get_domain_registry()):
        info = _get_domain_registry()[prefix]
        print(f"  {prefix:<12} {info['desc']:<35} {info['file']}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Agent 2: Key Takeaways Agent")
        print()
        print("Commands:")
        print("  extract <article.md>       Extract takeaways from an article")
        print("  suggest-prefix <article.md> Suggest domain prefix")
        print("  list-domains               List all domain prefixes")
        return 1

    cmd = sys.argv[1]
    if cmd == "extract":
        return cmd_extract(sys.argv[1:])
    elif cmd == "suggest-prefix":
        return cmd_suggest_prefix(sys.argv[1:])
    elif cmd == "list-domains":
        return cmd_list_domains(sys.argv[1:])
    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
