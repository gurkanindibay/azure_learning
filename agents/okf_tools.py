#!/usr/bin/env python3
"""
OKF Tools — Dependency-free utilities for working with OKF bundles.

Designed for the azure_learning repository. No external dependencies beyond
the Python 3.11+ standard library.

Usage:
    python3 agents/okf_tools.py validate      # Validate OKF conformance
    python3 agents/okf_tools.py list          # List all concepts by type
    python3 agents/okf_tools.py search <kw>   # Search concepts by keyword
    python3 agents/okf_tools.py check-links   # Check cross-reference integrity
    python3 agents/okf_tools.py summary       # Generate a bundle summary
    python3 agents/okf_tools.py stats         # Statistics about the bundle
    python3 agents/okf_tools.py graph         # Export a graph of relationships (JSON)
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {'.git', '.github', 'scripts', '__pycache__', '.venv', 'agents'}
EXCLUDE_FILES = {'AGENTS.md', 'log.md', 'accessibility-guidelines.md'}
RESERVED = {'index.md', 'log.md'}

# Files that serve as directory indices
INDEX_FILES = {'index.md'}


# ── OKF Document ─────────────────────────────────────────────────────────────

class OKFDocument:
    """Parse and represent an OKF concept document."""

    def __init__(self, path: Path, frontmatter: dict[str, Any], body: str):
        self.path = path
        self.frontmatter = frontmatter
        self.body = body

    @classmethod
    def parse(cls, path: Path) -> OKFDocument | None:
        """Parse an OKF markdown file. Returns None for non-OKF files."""
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return None

        if not text.startswith("---\n"):
            return None

        parts = text.split("\n---", 2)
        if len(parts) < 2:
            return None

        fm_text = parts[0][4:]  # Strip leading "---\n"
        body = parts[1][1:] if len(parts) > 1 and parts[1].startswith("\n") else (parts[1] if len(parts) > 1 else "")

        # Simple YAML parsing for frontmatter (no PyYAML dependency)
        fm = _parse_simple_yaml(fm_text)

        return cls(path, fm, body)

    @property
    def rel_path(self) -> str:
        return str(self.path.relative_to(REPO_ROOT))

    @property
    def concept_type(self) -> str:
        return str(self.frontmatter.get("type", ""))

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title", self.path.stem))

    @property
    def description(self) -> str:
        return str(self.frontmatter.get("description", ""))

    @property
    def tags(self) -> list[str]:
        tags = self.frontmatter.get("tags", [])
        if isinstance(tags, list):
            return [str(t) for t in tags]
        return []

    @property
    def links(self) -> list[str]:
        """Extract markdown links from the body."""
        return re.findall(r'\]\(([^)]+)\)', self.body)

    def validate(self) -> list[str]:
        """Validate OKF conformance. Returns list of issues (empty = valid)."""
        issues = []
        if not self.concept_type:
            issues.append("Missing 'type' field")
        return issues


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a simple YAML mapping without PyYAML dependency.
    
    Handles: strings, lists, quoted strings. Does NOT handle nested objects
    or complex YAML features.
    """
    result: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # List continuation
        if stripped.startswith("- ") and current_key:
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        # Key: value
        if ":" in stripped:
            # Flush previous list
            if current_key and current_list:
                result[current_key] = current_list
                current_list = []
                current_key = None

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value.startswith("[") and value.endswith("]"):
                # Inline list: [a, b, c]
                items = value[1:-1].split(",")
                result[key] = [i.strip().strip('"').strip("'") for i in items if i.strip()]
            elif not value:
                # Start of a multi-line list
                current_key = key
                current_list = []
            else:
                result[key] = value.strip().strip('"').strip("'")

    # Flush final list
    if current_key and current_list:
        result[current_key] = current_list

    return result


# ── Bundle Operations ────────────────────────────────────────────────────────

def iter_concepts(root: Path | None = None) -> list[OKFDocument]:
    """Iterate all OKF concept documents in the bundle."""
    if root is None:
        root = REPO_ROOT

    concepts = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for fname in filenames:
            if not fname.endswith(".md"):
                continue
            if fname in RESERVED or fname in EXCLUDE_FILES:
                continue

            filepath = Path(dirpath) / fname
            doc = OKFDocument.parse(filepath)
            if doc:
                concepts.append(doc)

    return concepts


def iter_indexes(root: Path | None = None) -> list[Path]:
    """Iterate all index.md files in the bundle."""
    if root is None:
        root = REPO_ROOT

    indexes = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if "index.md" in filenames:
            indexes.append(Path(dirpath) / "index.md")

    return indexes


# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_validate() -> int:
    """Validate OKF conformance of the entire bundle."""
    concepts = iter_concepts()
    passed = 0
    failed = 0

    for doc in concepts:
        issues = doc.validate()
        if issues:
            failed += 1
            print(f"FAIL [{doc.rel_path}]: {', '.join(issues)}")
        else:
            passed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        print("❌ Bundle is NOT OKF conformant.")
        return 1
    else:
        print("✅ Bundle is OKF conformant.")
        return 0


def cmd_list() -> int:
    """List all concepts grouped by type."""
    concepts = iter_concepts()
    grouped: dict[str, list[OKFDocument]] = defaultdict(list)

    for doc in concepts:
        grouped[doc.concept_type or "Unknown"].append(doc)

    for ctype in sorted(grouped):
        docs = grouped[ctype]
        print(f"\n## {ctype} ({len(docs)})")
        for doc in sorted(docs, key=lambda d: d.title):
            desc = doc.description[:80] + "..." if len(doc.description) > 80 else doc.description
            print(f"  * [{doc.title}]({doc.rel_path})" + (f" — {desc}" if desc else ""))

    print(f"\nTotal: {len(concepts)} concepts across {len(grouped)} types")
    return 0


def cmd_search(keyword: str) -> int:
    """Search concepts by keyword in title, description, tags, and body."""
    concepts = iter_concepts()
    keyword_lower = keyword.lower()
    results = []

    for doc in concepts:
        score = 0
        if keyword_lower in doc.title.lower():
            score += 10
        if keyword_lower in doc.description.lower():
            score += 5
        if any(keyword_lower in tag.lower() for tag in doc.tags):
            score += 8
        if keyword_lower in doc.body.lower():
            score += 1

        if score > 0:
            results.append((score, doc))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print(f"No results found for '{keyword}'.")
        return 1

    print(f"Search results for '{keyword}':\n")
    for score, doc in results:
        desc = doc.description[:100] + "..." if len(doc.description) > 100 else doc.description
        print(f"  [{doc.title}]({doc.rel_path}) (score: {score})")
        print(f"    Type: {doc.concept_type}  |  Tags: {', '.join(doc.tags) if doc.tags else 'none'}")
        if desc:
            print(f"    {desc}")
        print()

    print(f"Found {len(results)} result(s).")
    return 0


def cmd_check_links() -> int:
    """Check cross-reference integrity — find broken internal links."""
    concepts = iter_concepts()
    broken = 0

    # Build set of all valid target paths
    valid_paths: set[str] = set()
    for doc in concepts:
        valid_paths.add(doc.rel_path)

    # Also add directory paths (for index.md references)
    for idx in iter_indexes():
        rel = str(idx.relative_to(REPO_ROOT))
        valid_paths.add(rel)

    for doc in concepts:
        for link in doc.links:
            # Only check internal links (no scheme)
            if "://" in link:
                continue
            # Skip anchor-only links
            if link.startswith("#"):
                continue

            # Resolve relative link
            link_path = link.split("#")[0] if "#" in link else link
            if not link_path:
                continue

            doc_dir = doc.path.parent
            try:
                resolved = (doc_dir / link_path).resolve().relative_to(REPO_ROOT)
            except ValueError:
                # Path goes outside repo
                continue

            if str(resolved) not in valid_paths:
                # Check if it's a directory (might have index.md)
                dir_path = str(resolved)
                if f"{dir_path}/index.md" not in valid_paths:
                    broken += 1
                    print(f"BROKEN [{doc.rel_path}]: link to '{link_path}' (resolved: {resolved})")
                    if broken >= 30:
                        print("... (truncated at 30)")
                        return 1

    if broken == 0:
        print("✅ All internal cross-references resolve correctly.")
        return 0
    else:
        print(f"\n❌ {broken} broken cross-reference(s) found.")
        return 1


def cmd_summary() -> int:
    """Generate a human-readable bundle summary."""
    concepts = iter_concepts()
    indexes = iter_indexes()

    print("# OKF Bundle Summary\n")
    print(f"**Bundle**: azure_learning")
    print(f"**OKF Version**: v0.1")
    print(f"**Root**: {REPO_ROOT}")
    print()

    # Counts by type
    type_counts: dict[str, int] = defaultdict(int)
    tag_counts: dict[str, int] = defaultdict(int)
    for doc in concepts:
        type_counts[doc.concept_type] += 1
        for tag in doc.tags:
            tag_counts[tag] += 1

    print(f"## Statistics\n")
    print(f"| Metric | Count |")
    print(f"|:---|---:|")
    print(f"| Total concepts | {len(concepts)} |")
    print(f"| Concept types | {len(type_counts)} |")
    print(f"| Unique tags | {len(tag_counts)} |")
    print(f"| Index files | {len(indexes)} |")
    print()

    print(f"## Concepts by Type\n")
    for ctype in sorted(type_counts, key=type_counts.get, reverse=True):
        print(f"| {ctype} | {type_counts[ctype]} |")

    print(f"\n## Top Tags\n")
    for tag in sorted(tag_counts, key=tag_counts.get, reverse=True)[:20]:
        print(f"| {tag} | {tag_counts[tag]} |")

    return 0


def cmd_stats() -> int:
    """Print detailed statistics about the bundle."""
    concepts = iter_concepts()

    total_body_chars = sum(len(doc.body) for doc in concepts)
    total_links = sum(len(doc.links) for doc in concepts)
    type_counts: dict[str, int] = defaultdict(int)
    for doc in concepts:
        type_counts[doc.concept_type] += 1

    print(json.dumps({
        "total_concepts": len(concepts),
        "total_types": len(type_counts),
        "total_body_chars": total_body_chars,
        "total_body_kb": round(total_body_chars / 1024, 1),
        "total_links": total_links,
        "avg_body_chars": round(total_body_chars / len(concepts)) if concepts else 0,
        "avg_links_per_concept": round(total_links / len(concepts), 1) if concepts else 0,
        "types": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
    }, indent=2))
    return 0


def cmd_graph() -> int:
    """Export a graph of concept relationships as JSON."""
    concepts = iter_concepts()

    nodes = []
    edges = []
    path_to_id: dict[str, int] = {}

    for i, doc in enumerate(concepts):
        path_to_id[doc.rel_path] = i
        nodes.append({
            "id": i,
            "path": doc.rel_path,
            "type": doc.concept_type,
            "title": doc.title,
            "tags": doc.tags,
        })

    for doc in concepts:
        src_id = path_to_id[doc.rel_path]
        for link in doc.links:
            if "://" in link or link.startswith("#"):
                continue
            link_path = link.split("#")[0] if "#" in link else link
            if not link_path:
                continue

            doc_dir = doc.path.parent
            try:
                resolved = str((doc_dir / link_path).resolve().relative_to(REPO_ROOT))
            except ValueError:
                continue

            if resolved in path_to_id:
                edges.append({"source": src_id, "target": path_to_id[resolved]})

    print(json.dumps({"nodes": nodes, "edges": edges}, indent=2))
    return 0


# ── Main ─────────────────────────────────────────────────────────────────────

COMMANDS = {
    "validate": (cmd_validate, "Validate OKF conformance"),
    "list": (cmd_list, "List all concepts grouped by type"),
    "search": (cmd_search, "Search concepts by keyword"),
    "check-links": (cmd_check_links, "Check cross-reference integrity"),
    "summary": (cmd_summary, "Generate a bundle summary"),
    "stats": (cmd_stats, "Statistics about the bundle (JSON)"),
    "graph": (cmd_graph, "Export concept relationship graph (JSON)"),
}


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 agents/okf_tools.py <command> [args]")
        print("\nCommands:")
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:<15} {desc}")
        return 1

    cmd_name = sys.argv[1]
    if cmd_name not in COMMANDS:
        print(f"Unknown command: {cmd_name}")
        print(f"Available: {', '.join(COMMANDS)}")
        return 1

    cmd_fn, _ = COMMANDS[cmd_name]
    if cmd_name == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 agents/okf_tools.py search <keyword>")
            return 1
        return cmd_fn(sys.argv[2])
    else:
        return cmd_fn()


if __name__ == "__main__":
    sys.exit(main())
