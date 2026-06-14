#!/usr/bin/env python3
"""
Domain Discovery Agent

Scans the repository for new domains that are present on the filesystem
but not yet registered in agent_tools/config.yaml. Automatically updates
the configuration when new domains are found.

This agent is designed to be run:
- Manually:        python3 agent_tools/discovery_agent.py
- After new files: python3 agent_tools/discovery_agent.py --apply
- As a dry run:    python3 agent_tools/discovery_agent.py --dry-run
- By the coordinator after processing a new document

How it works:
1. Scans system-design-architecture/ for *-key-takeaways.md files
2. Scans reference-dictionary/ for *.md files (excluding index.md)
3. Compares with agent_tools/config.yaml
4. For each new domain, generates sensible defaults:
   - Prefix from filename
   - Description from filename (humanized)
   - Keywords from filename words + content analysis
   - Suggested placement in config.yaml sections

Usage:
    python3 agent_tools/discovery_agent.py                # Show undiscovered domains
    python3 agent_tools/discovery_agent.py --dry-run      # Preview changes to config
    python3 agent_tools/discovery_agent.py --apply        # Update config.yaml
    python3 agent_tools/discovery_agent.py --watch <file> # Discover from a new file
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "agents" / "config.yaml"
SDA_DIR = REPO_ROOT / "system-design-architecture"
REF_DIR = REPO_ROOT / "reference-dictionary"

# ── Domain detection ─────────────────────────────────────────────────────────

def find_takeaway_files() -> list[Path]:
    """Find all *-key-takeaways.md files in system-design-architecture/."""
    if not SDA_DIR.is_dir():
        return []
    return sorted(SDA_DIR.glob("*-key-takeaways.md"))


def find_dictionary_files() -> list[Path]:
    """Find all .md files in reference-dictionary/ (excluding index.md)."""
    if not REF_DIR.is_dir():
        return []
    return sorted(
        f for f in REF_DIR.glob("*.md")
        if f.name != "index.md"
    )


def extract_prefix(filename: str) -> str:
    """Extract domain prefix from a takeaway filename.
    
    "29-mesh-key-takeaways.md" → "mesh"
    "23-circuit-breaker-key-takeaways.md" → "circuit-breaker"
    """
    m = re.match(r'\d+-(.+)-key-takeaways\.md$', filename)
    if m:
        return m.group(1)
    return filename.replace("-key-takeaways.md", "")


def humanize(text: str) -> str:
    """Convert a kebab-case string to Title Case.
    
    "circuit-breaker" → "Circuit Breaker"
    "api-design" → "Api Design"
    """
    words = text.replace("-", " ").replace("_", " ").split()
    # Common acronyms to uppercase
    acronyms = {"ai", "ml", "llm", "api", "hsm", "cqrs", "sql", "dlq", "ttl",
                "sdk", "cli", "ui", "db", "lb", "cdc", "pki", "tls", "ssl",
                "hls", "dash", "grpc", "ddd", "mvcc", "pci", "rto", "rpo"}
    result = []
    for w in words:
        if w.lower() in acronyms:
            result.append(w.upper())
        else:
            result.append(w.capitalize())
    return " ".join(result)


def extract_keywords_from_content(filepath: Path, max_keywords: int = 8) -> list[str]:
    """Extract likely keywords from a file's content.
    
    Looks for:
    - Bold terms (**Term**)
    - Backtick terms (`term`)
    - Repeated significant words
    - Domain-specific patterns
    """
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    # Skip frontmatter
    body = content
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end > 0:
            body = content[end + 5:]

    words = re.findall(r'\b[a-z][a-z-]{3,20}\b', body.lower())

    # Boost words from bold/backtick
    bold_terms = re.findall(r'\*\*([A-Za-z][A-Za-z\s/-]{3,40})\*\*', body)
    backtick_terms = re.findall(r'`([a-z][a-z_-]{2,30})`', body)

    # Count occurrences
    stopwords = {"the", "and", "for", "that", "this", "with", "from", "have",
                 "are", "was", "not", "but", "all", "can", "has", "had", "been",
                 "were", "they", "their", "them", "its", "will", "would", "could",
                 "should", "about", "also", "into", "than", "then", "only", "other",
                 "some", "such", "when", "which", "each", "more", "most", "very",
                 "just", "over", "after", "before", "between", "through"}

    word_counts = Counter(w for w in words if w not in stopwords)

    # Add bold/backtick terms with boosted weight
    for t in bold_terms:
        word_counts[t.lower()] += 5
    for t in backtick_terms:
        word_counts[t.lower()] += 3

    # Filter: prefer multi-word terms, domain-relevant words
    keywords = []
    for word, count in word_counts.most_common(max_keywords * 2):
        if len(word) >= 4 and count >= 2:
            keywords.append(word)
        if len(keywords) >= max_keywords:
            break

    return keywords[:max_keywords]


# ── Config file management ───────────────────────────────────────────────────

def load_config_raw() -> list[str]:
    """Load config.yaml as raw lines (preserving comments and structure)."""
    if CONFIG_PATH.exists():
        return CONFIG_PATH.read_text(encoding="utf-8").split("\n")
    return []


def save_config_raw(lines: list[str]):
    """Save raw lines back to config.yaml."""
    CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_section_bounds(lines: list[str], section_name: str) -> tuple[int, int] | None:
    """Find the line range of a top-level YAML section in config.yaml.
    
    Returns (start_line, end_line) where start_line is the section header
    and end_line is the last line of the section (exclusive).
    """
    in_section = False
    start = None
    indent = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not in_section:
            if stripped.startswith(f"{section_name}:"):
                in_section = True
                start = i
                indent = len(line) - len(line.lstrip())
        else:
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent and stripped:
                return (start, i)

    if in_section and start is not None:
        return (start, len(lines))
    return None


def add_takeaway_domain_to_config(prefix: str, filename: str, desc: str,
                                   keywords: list[str]) -> bool:
    """Add a new takeaway domain entry to config.yaml.
    
    Returns True if successful, False if filename already registered.
    """
    lines = load_config_raw()

    # Check if filename already exists (by filename match, not prefix)
    registered_files, _ = load_registered_domains()
    if filename in registered_files:
        return False

    # Also check inline in the raw config for duplicate filenames
    for line in lines:
        if f'file: "{filename}"' in line or f"file: '{filename}'" in line:
            return False

    # Find the takeaway_domains section
    bounds = find_section_bounds(lines, "takeaway_domains")
    if bounds is None:
        print("  ⚠ Could not find takeaway_domains section in config.yaml")
        return False

    start, end = bounds

    # Find the last domain entry before the end of the section
    insert_at = end
    for i in range(end - 1, start, -1):
        if lines[i].strip() and not lines[i].strip().startswith("#"):
            insert_at = i + 1
            break

    # Determine indent level (look at surrounding entries)
    entry_indent = "  "  # default
    for i in range(start + 1, end):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#") and ":" in stripped:
            entry_indent = " " * (len(lines[i]) - len(lines[i].lstrip()))
            break

    # Build new entry
    new_lines = [
        f"{entry_indent}{prefix}:",
        f"{entry_indent}  file: \"{filename}\"",
        f"{entry_indent}  desc: \"{desc}\"",
    ]
    if keywords:
        kw_str = ", ".join(keywords[:6])
        new_lines.append(f"{entry_indent}  keywords: [{kw_str}]")

    # Insert
    lines[insert_at:insert_at] = [""] + new_lines
    save_config_raw(lines)
    return True


def add_dictionary_domain_to_config(filename: str, title: str,
                                     keywords: list[str]) -> bool:
    """Add a new dictionary domain entry to config.yaml.
    
    Returns True if successful, False if filename already registered.
    """
    lines = load_config_raw()

    # Check if filename already exists
    _, registered_files = load_registered_domains()
    if filename in registered_files:
        return False

    bounds = find_section_bounds(lines, "dictionary_domains")
    if bounds is None:
        print("  ⚠ Could not find dictionary_domains section in config.yaml")
        return False

    start, end = bounds
    insert_at = end
    for i in range(end - 1, start, -1):
        if lines[i].strip() and not lines[i].strip().startswith("#"):
            insert_at = i + 1
            break

    entry_indent = "  "
    for i in range(start + 1, end):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#") and ":" in stripped:
            entry_indent = " " * (len(lines[i]) - len(lines[i].lstrip()))
            break

    new_lines = [
        f"{entry_indent}{filename}:",
        f"{entry_indent}  title: \"{title}\"",
    ]
    if keywords:
        kw_lines = _format_keyword_list(keywords, entry_indent, max_per_line=5)
        new_lines.append(f"{entry_indent}  keywords:")
        new_lines.extend(kw_lines)

    lines[insert_at:insert_at] = [""] + new_lines
    save_config_raw(lines)
    return True


def _format_keyword_list(keywords: list[str], indent: str,
                          max_per_line: int = 5) -> list[str]:
    """Format a keyword list for YAML with line wrapping."""
    result = []
    for i in range(0, len(keywords), max_per_line):
        chunk = keywords[i:i + max_per_line]
        kw_str = ", ".join(f'"{kw}"' if " " in kw else kw for kw in chunk)
        prefix = f"{indent}    - " if i == 0 else f"{indent}      "
        result.append(f"{prefix}{kw_str}")
    return result


def _get_parent_section(lines: list[str], target_line: str) -> str:
    """Find which top-level section a line belongs to."""
    current_section = ""
    target = target_line.strip()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0 and stripped.endswith(":"):
            current_section = stripped[:-1]
        if stripped == target:
            return current_section
    return ""


# ── Discovery logic ──────────────────────────────────────────────────────────

def load_registered_domains() -> tuple[set[str], set[str]]:
    """Load domains explicitly registered in config.yaml (the file).
    
    Does NOT include auto-discovered entries from config_loader (those
    are in-memory only). The discovery agent's job is to write those
    auto-discovered entries into config.yaml so they become permanent.
    
    Returns (takeaway_filenames, dictionary_filenames).
    """
    raw = load_config_raw()

    takeaway_files: set[str] = set()
    dict_files: set[str] = set()
    current_section = ""

    for line in raw:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Track top-level sections
        if indent == 0 and stripped.endswith(":"):
            current_section = stripped[:-1]

        # Extract file references from takeaway_domains
        if current_section == "takeaway_domains":
            m = re.match(r'file:\s*"([^"]+)"', stripped)
            if m:
                takeaway_files.add(m.group(1))
            m = re.match(r"file:\s*'([^']+)'", stripped)
            if m:
                takeaway_files.add(m.group(1))

        # Extract filename keys from dictionary_domains
        if current_section == "dictionary_domains":
            if indent == 2 and stripped.endswith(":") and ".md" in stripped:
                fname = stripped[:-1].strip()
                dict_files.add(fname)

    return takeaway_files, dict_files


def discover_new_domains() -> dict[str, list[dict]]:
    """Discover new domains not yet in config.yaml.
    
    Returns {
        "takeaways": [{prefix, file, desc, keywords}],
        "dictionary": [{file, title, keywords}],
    }
    """
    registered_files_td, registered_files_dd = load_registered_domains()

    # Discover new takeaway domains (match by filename, not prefix)
    new_takeaways = []
    for f in find_takeaway_files():
        if f.name in registered_files_td:
            continue
        prefix = extract_prefix(f.name)
        keywords = extract_keywords_from_content(f)
        new_takeaways.append({
            "prefix": prefix,
            "file": f.name,
            "desc": humanize(prefix),
            "keywords": keywords,
        })

    # Discover new dictionary domains (match by filename)
    new_dict = []
    for f in find_dictionary_files():
        if f.name in registered_files_dd:
            continue
        title = humanize(f.stem)
        keywords = extract_keywords_from_content(f)
        new_dict.append({
            "file": f.name,
            "title": title,
            "keywords": keywords,
        })

    return {"takeaways": new_takeaways, "dictionary": new_dict}


# ── CLI ──────────────────────────────────────────────────────────────────────

def cmd_show(args: list[str]) -> int:
    """Show undiscovered domains."""
    discovered = discover_new_domains()
    td = discovered["takeaways"]
    dd = discovered["dictionary"]

    if not td and not dd:
        print("✅ All domains are registered in config.yaml. Nothing new to discover.")
        return 0

    if td:
        print(f"\n📝 New Takeaway Domains ({len(td)}):")
        print(f"   {'Prefix':<20} {'File':<45} {'Description'}")
        print(f"   {'-'*18}  {'-'*43}  {'-'*25}")
        for d in td:
            print(f"   {d['prefix']:<20} {d['file']:<45} {d['desc']}")
            if d["keywords"]:
                print(f"   {'':20} Keywords: {', '.join(d['keywords'][:6])}")

    if dd:
        print(f"\n📚 New Dictionary Domains ({len(dd)}):")
        print(f"   {'File':<40} {'Title'}")
        print(f"   {'-'*38}  {'-'*25}")
        for d in dd:
            print(f"   {d['file']:<40} {d['title']}")
            if d["keywords"]:
                print(f"   {'':40} Keywords: {', '.join(d['keywords'][:6])}")

    print(f"\n💡 To register these domains, run:")
    print(f"   python3 agent_tools/discovery_agent.py --apply")
    return 0


def cmd_dry_run(args: list[str]) -> int:
    """Preview changes to config.yaml."""
    discovered = discover_new_domains()
    td = discovered["takeaways"]
    dd = discovered["dictionary"]

    if not td and not dd:
        print("✅ All domains are registered. No changes needed.")
        return 0

    print("── Preview of config.yaml changes ──\n")

    for d in td:
        print(f"  # New takeaway domain (auto-discovered)")
        print(f"  {d['prefix']}:")
        print(f"    file: \"{d['file']}\"")
        print(f"    desc: \"{d['desc']}\"")
        if d["keywords"]:
            print(f"    keywords: [{', '.join(d['keywords'][:6])}]")
        print()

    for d in dd:
        print(f"  # New dictionary domain (auto-discovered)")
        print(f"  {d['file']}:")
        print(f"    title: \"{d['title']}\"")
        if d["keywords"]:
            print(f"    keywords:")
            for kw in d["keywords"][:6]:
                print(f"      - {kw}")
        print()

    print(f"── {len(td) + len(dd)} new domain(s) would be registered ──")
    return 0


def cmd_apply(args: list[str]) -> int:
    """Apply domain discoveries to config.yaml."""
    discovered = discover_new_domains()
    td = discovered["takeaways"]
    dd = discovered["dictionary"]

    if not td and not dd:
        print("✅ All domains are registered. Nothing to apply.")
        return 0

    added_td = 0
    added_dd = 0

    for d in td:
        ok = add_takeaway_domain_to_config(
            d["prefix"], d["file"], d["desc"], d["keywords"]
        )
        if ok:
            print(f"  ✅ Registered takeaway domain: {d['prefix']} → {d['file']}")
            added_td += 1
        else:
            print(f"  ⏭ Already registered: {d['prefix']}")

    for d in dd:
        ok = add_dictionary_domain_to_config(
            d["file"], d["title"], d["keywords"]
        )
        if ok:
            print(f"  ✅ Registered dictionary domain: {d['file']} → {d['title']}")
            added_dd += 1
        else:
            print(f"  ⏭ Already registered: {d['file']}")

    print(f"\n✅ Added {added_td} takeaway + {added_dd} dictionary domain(s) to config.yaml")

    # Reload config cache
    try:
        from agent_tools.config_loader import reload_config
        reload_config()
        print("   Config cache reloaded.")
    except Exception:
        pass

    return 0


def cmd_watch(args: list[str]) -> int:
    """Watch a specific new file and suggest domain registration."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/discovery_agent.py --watch <new-file.md>")
        return 1

    filepath = Path(args[1])
    if not filepath.is_absolute():
        filepath = REPO_ROOT / args[1]

    if not filepath.exists():
        print(f"❌ File not found: {args[1]}")
        return 1

    rel = str(filepath.relative_to(REPO_ROOT))

    if "system-design-architecture/" in rel and "key-takeaways" in filepath.name:
        prefix = extract_prefix(filepath.name)
        keywords = extract_keywords_from_content(filepath)
        print(f"📝 New takeaway file detected: {filepath.name}")
        print(f"   Suggested prefix:  {prefix}")
        print(f"   Suggested description: {humanize(prefix)}")
        if keywords:
            print(f"   Suggested keywords: {', '.join(keywords[:6])}")
        print()
        print(f"   To register: python3 agent_tools/discovery_agent.py --apply")

    elif "reference-dictionary/" in rel:
        title = humanize(filepath.stem)
        keywords = extract_keywords_from_content(filepath)
        print(f"📚 New dictionary file detected: {filepath.name}")
        print(f"   Suggested title: {title}")
        if keywords:
            print(f"   Suggested keywords: {', '.join(keywords[:6])}")
        print()
        print(f"   To register: python3 agent_tools/discovery_agent.py --apply")

    else:
        print(f"ℹ File {rel} is not in a domain-tracked directory.")
        print(f"   Tracked directories: system-design-architecture/, reference-dictionary/")

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        return cmd_show(sys.argv[1:])

    cmd = sys.argv[1]
    if cmd == "--dry-run":
        return cmd_dry_run(sys.argv[1:])
    elif cmd == "--apply":
        return cmd_apply(sys.argv[1:])
    elif cmd == "--watch":
        return cmd_watch(sys.argv[1:])
    elif cmd in ("--help", "-h"):
        print("Domain Discovery Agent")
        print()
        print("Discovers new domains from the filesystem and registers them in config.yaml.")
        print()
        print("Usage:")
        print("  python3 agent_tools/discovery_agent.py              Show undiscovered domains")
        print("  python3 agent_tools/discovery_agent.py --dry-run    Preview config changes")
        print("  python3 agent_tools/discovery_agent.py --apply      Update config.yaml")
        print("  python3 agent_tools/discovery_agent.py --watch <f>  Analyze a new file")
        return 0
    else:
        print(f"Unknown option: {cmd}")
        print("Usage: python3 agent_tools/discovery_agent.py [--dry-run|--apply|--watch <file>]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
