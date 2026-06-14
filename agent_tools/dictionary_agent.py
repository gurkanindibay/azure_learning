#!/usr/bin/env python3
"""
Agent 3: Reference Dictionary Agent

Identifies and adds novel/new concepts into the reference-dictionary.
Scans source documents for technical terms, checks if they already exist
in the dictionary, and generates new term entries following the repository
convention.

Each dictionary entry follows the template:
    ### term-name
    Definition → Key Characteristics → When to Use / When NOT → Also See

The agent:
    1. Reads a source document (article, takeaway, or architecture doc)
    2. Extracts technical terms using heuristics
    3. Checks which terms are already defined in reference-dictionary/
    4. For novel terms, generates entry templates with cross-references
    5. Places terms in the correct domain file (or creates a new one)

Usage:
    python3 agent_tools/dictionary_agent.py extract-terms <document.md> [--dry-run]
    python3 agent_tools/dictionary_agent.py check-term <term>
    python3 agent_tools/dictionary_agent.py list-domains
    python3 agent_tools/dictionary_agent.py add-term <term> --domain <file> [--definition "..."] [--dry-run]

Part of the coordinated agent workflow:
    Agent 1 (format) → Agent 2 (takeaways) → Agent 3 (dictionary)
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
REF_DIR = REPO_ROOT / "reference-dictionary"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# ── Dictionary domain files ─────────────────────────────────────────────────
# Loaded from config.yaml + auto-discovered from filesystem.
# To add a new domain:
#   1. Add entry to agent_tools/config.yaml under dictionary_domains (optional)
#   2. Or just create a new .md file in reference-dictionary/
#      and the agents will auto-discover it.
# See: agent_tools/config_loader.py

def _get_dictionary_domains() -> dict:
    """Lazy-load dictionary domains from config + auto-discovery."""
    _ensure_path()
    from agent_tools.config_loader import load_config
    return load_config().dictionary_domains


def _ensure_path():
    """Ensure repo root is on sys.path for imports."""
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


# ── Term extraction ─────────────────────────────────────────────────────────

# Patterns that suggest a technical term worth defining
TERM_PATTERNS = [
    # Bold terms: **Circuit Breaker**
    re.compile(r'\*\*([A-Z][A-Za-z\s/-]{2,50})\*\*'),
    # Backtick terms: `partition`
    re.compile(r'`([a-z][a-z_-]{2,40})`'),
    # Capitalized phrases (potential terms)
    re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b'),
    # Acronym definitions: "DLQ (Dead Letter Queue)"
    re.compile(r'\b([A-Z]{2,6})\s*\(([A-Za-z\s]+)\)'),
]

# Words to ignore (common words that aren't technical terms)
IGNORE_WORDS = {
    "the", "and", "for", "that", "this", "with", "from", "have", "are",
    "was", "not", "but", "all", "can", "has", "had", "been", "were",
    "they", "their", "them", "its", "will", "would", "could", "should",
    "about", "also", "into", "than", "then", "only", "other", "some",
    "such", "when", "which", "each", "more", "most", "very", "just",
    "over", "after", "before", "between", "through", "during", "before",
    "Azure", "API", "SQL", "HTTP", "JSON", "YAML", "REST", "GDPR",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Note",
    "Important", "Example", "Code", "Table", "Figure", "Chapter",
    "Section", "Part", "Introduction", "Conclusion", "Summary",
    "However", "Therefore", "Moreover", "Additionally", "Furthermore",
}

# Structural labels that appear in metadata blocks, tables, and content templates
STRUCTURAL_LABELS = {
    "source", "parent", "purpose", "also see", "taxonomy reference",
    "dictionary", "cross-reference", "key insight", "key concept",
    "root cause", "problem", "strategy", "tradeoff", "evidence",
    "result", "author", "published", "read time", "category",
    "contents", "references", "see also", "next steps",
    "getting started", "overview", "summary", "conclusion",
    "the first lie", "the second lie", "the third lie", "the fourth lie",
    "what it catches", "what it misses", "the math that lies",
    "failure rate vs slow-call rate", "the core boundary",
    "command side questions", "query side flexibility",
}


def extract_terms(content: str) -> list[dict]:
    """Extract candidate technical terms from document content.

    Returns list of {term, context, line_number, confidence} dicts.
    """
    # Strip frontmatter
    body = content
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end > 0:
            body = content[end + 5:]

    lines = body.split("\n")
    candidates: dict[str, dict] = {}

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```"):
            continue

        for pattern in TERM_PATTERNS:
            for match in pattern.finditer(stripped):
                term = match.group(1).strip()

                # Filter
                if len(term) < 3:
                    continue
                if term.lower() in IGNORE_WORDS:
                    continue
                if term.lower() in STRUCTURAL_LABELS:
                    continue
                if re.match(r'^https?://', term):
                    continue
                # Skip terms that look like they came from metadata labels
                # (single words that are common structural words)
                if len(term.split()) == 1 and term.lower() in {
                    "source", "parent", "purpose", "strategy", "tradeoff",
                    "overview", "contents", "summary", "introduction",
                }:
                    continue

                # Normalize
                term_lower = term.lower()

                if term_lower in candidates:
                    candidates[term_lower]["count"] += 1
                    if candidates[term_lower]["confidence"] < 3:
                        candidates[term_lower]["confidence"] += 1
                else:
                    # Get surrounding context
                    ctx_start = max(0, i - 1)
                    ctx_end = min(len(lines), i + 2)
                    context = " ".join(
                        l.strip() for l in lines[ctx_start:ctx_end] if l.strip()
                    )[:200]

                    candidates[term_lower] = {
                        "term": term,
                        "context": context,
                        "line": i + 1,
                        "count": 1,
                        "confidence": 1,  # 1=low, 2=medium, 3=high
                    }

    # Filter: only terms that appear multiple times or in important positions
    result = []
    for t in candidates.values():
        if t["count"] >= 2 or t["confidence"] >= 2:
            result.append(t)
        # Also include bold terms even if single occurrence
        elif t["confidence"] >= 1 and t["count"] == 1:
            result.append(t)

    # Sort by confidence then count
    result.sort(key=lambda x: (x["confidence"], x["count"]), reverse=True)
    return result[:30]  # Top 30 candidates


# ── Dictionary lookup ───────────────────────────────────────────────────────

def load_existing_terms() -> dict[str, str]:
    """Load all existing terms from reference-dictionary files.

    Terms are defined as ## headings (H2). ### headings are sub-sections.

    Returns {term_lower: domain_file} mapping.
    """
    existing: dict[str, str] = {}

    for domain_file in REF_DIR.glob("*.md"):
        if domain_file.name == "index.md":
            continue
        content = domain_file.read_text(encoding="utf-8")
        # Find all ## headings (term definitions) — skip H1, H3+
        for match in re.finditer(r'^##\s+(.+)$', content, re.MULTILINE):
            term = match.group(1).strip()
            # Skip structural headings (Contents, etc.)
            if term.lower() in ("contents", "also see", "key configuration",
                               "solutions", "when to use", "when not",
                               "when not to use", "key characteristics"):
                continue
            existing[term.lower()] = domain_file.name

    return existing


def find_domain_for_term(term: str) -> str | None:
    """Find which dictionary domain file a term should go in."""
    term_lower = term.lower()

    best_domain = None
    best_score = 0

    for domain_file, info in _get_dictionary_domains().items():
        score = 0
        for keyword in info["keywords"]:
            if keyword in term_lower:
                score += 1
            # Check individual words
            for word in keyword.split():
                if word in term_lower:
                    score += 0.5
        if score > best_score:
            best_score = score
            best_domain = domain_file

    if best_score >= 1:
        return best_domain
    return "architecture-patterns.md"  # Default catch-all


def term_exists(term: str) -> tuple[bool, str | None]:
    """Check if a term already exists in the dictionary.

    Returns (exists, domain_file).
    """
    existing = load_existing_terms()
    term_lower = term.lower()

    # Exact match
    if term_lower in existing:
        return True, existing[term_lower]

    # Fuzzy match (term is substring of existing)
    for existing_term, domain in existing.items():
        if term_lower in existing_term or existing_term in term_lower:
            return True, domain

    return False, None


# ── Term entry generation ────────────────────────────────────────────────────

def generate_term_entry(term: str, context: str, domain_file: str) -> str:
    """Generate a reference-dictionary entry for a term."""
    domain_info = _get_dictionary_domains().get(domain_file, {"title": "General"})

    lines = []
    anchor = term.lower().replace(" ", "-").replace("/", "-")

    lines.append(f"## {term}")
    lines.append("")
    lines.append(f"TODO: One-sentence definition of {term}.")
    lines.append("")
    lines.append("### Key Characteristics")
    lines.append("")
    lines.append(f"- TODO: Characteristic 1 of {term}")
    lines.append(f"- TODO: Characteristic 2 of {term}")
    lines.append(f"- TODO: Characteristic 3 of {term}")
    lines.append("")
    lines.append("### When to Use")
    lines.append("")
    lines.append(f"- TODO: When {term} is the right choice")
    lines.append("")
    lines.append("### When NOT to Use")
    lines.append("")
    lines.append(f"- TODO: When {term} is the wrong choice")
    lines.append("")
    lines.append("### Also see")
    lines.append("")
    lines.append("- TODO: Related terms")

    return "\n".join(lines)


def add_term_to_dictionary(
    term: str,
    domain_file: str,
    context: str = "",
    dry_run: bool = False,
) -> str | None:
    """Add a new term to the reference dictionary.

    Returns the domain file path, or None if term already exists.
    """
    exists, existing_domain = term_exists(term)
    if exists:
        print(f"  ⏭ Term '{term}' already exists in {existing_domain}")
        return None

    filepath = REF_DIR / domain_file
    if not filepath.exists():
        print(f"  ⚠ Domain file {domain_file} does not exist. Creating it.")
        # Create new domain file
        domain_info = _get_dictionary_domains().get(domain_file, {"title": domain_file.replace(".md", "").replace("-", " ").title()})
        filepath.write_text(
            f"---\n"
            f"type: Reference\n"
            f'title: "{domain_info["title"]}"\n'
            f'timestamp: {TODAY}T00:00:00Z\n'
            f"---\n\n"
            f"# {domain_info['title']}\n\n"
            f"> **Domain**: TODO\n"
            f"> **Parent**: [Reference Dictionary](index.md)\n\n"
            f"---\n\n"
            f"## Contents\n\n"
        )

    entry = generate_term_entry(term, context, domain_file)

    if dry_run:
        print(f"  [DRY-RUN] Would add '{term}' to {domain_file}:")
        for line in entry.split("\n")[:5]:
            print(f"    {line}")
        return domain_file

    # Append to domain file
    with open(filepath, "a") as f:
        f.write("\n---\n\n")
        f.write(entry)
        f.write("\n")

    return domain_file


# ── CLI ──────────────────────────────────────────────────────────────────────

def cmd_extract_terms(args: list[str]) -> int:
    """Extract novel terms from a document and add them to the dictionary."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/dictionary_agent.py extract-terms <document.md> [--dry-run]")
        return 1

    doc_rel = args[1]
    doc_path = REPO_ROOT / doc_rel
    if not doc_path.exists():
        print(f"File not found: {doc_rel}")
        return 1

    dry_run = "--dry-run" in args

    content = doc_path.read_text(encoding="utf-8")
    terms = extract_terms(content)

    print(f"Extracted {len(terms)} candidate terms from {doc_rel}")
    print()

    existing_terms = load_existing_terms()
    novel = []
    skip = []

    for t in terms:
        term = t["term"]
        exists, domain = term_exists(term)
        if exists:
            skip.append((term, domain))
        else:
            novel.append(t)

    print(f"Novel (new): {len(novel)}")
    print(f"Already defined: {len(skip)}")
    print()

    if not novel:
        print("No new terms to add.")
        return 0

    print("Novel terms to add:")
    for t in novel:
        domain = find_domain_for_term(t["term"])
        print(f"  • {t['term']:<30} → {domain}  (confidence: {t['confidence']}, count: {t['count']})")
        if t["context"]:
            print(f"    Context: {t['context'][:120]}...")

    print()

    if dry_run:
        print("[DRY-RUN] No files modified.")
        return 0

    added = 0
    for t in novel:
        domain = find_domain_for_term(t["term"])
        result = add_term_to_dictionary(t["term"], domain, t["context"])
        if result:
            added += 1

    print(f"\n✅ Added {added} new term(s) to reference-dictionary/")
    if added > 0:
        print("⚠ Remember to fill in the TODO sections for each term.")

    return 0


def cmd_check_term(args: list[str]) -> int:
    """Check if a term exists in the dictionary."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/dictionary_agent.py check-term <term>")
        return 1

    term = args[1]
    exists, domain = term_exists(term)

    if exists:
        print(f"✅ '{term}' is defined in reference-dictionary/{domain}")
    else:
        print(f"❌ '{term}' is NOT in the dictionary.")
        suggested_domain = find_domain_for_term(term)
        print(f"   Suggested domain: {suggested_domain}")
        print(f"   To add: python3 agent_tools/dictionary_agent.py add-term '{term}' --domain {suggested_domain}")

    return 0 if exists else 1


def cmd_add_term(args: list[str]) -> int:
    """Add a single term to the dictionary."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/dictionary_agent.py add-term <term> --domain <file> [--definition \"...\"] [--dry-run]")
        return 1

    term = args[1]
    domain = "architecture-patterns.md"
    dry_run = False

    i = 2
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    result = add_term_to_dictionary(term, domain, dry_run=dry_run)
    if result:
        print(f"✅ Added '{term}' to reference-dictionary/{result}")
    return 0


def cmd_list_domains(args: list[str]) -> int:
    """List all dictionary domain files."""
    print(f"{'File':<35} {'Title':<35} {'Terms'}")
    print("-" * 90)
    for domain_file in sorted(_get_dictionary_domains()):
        info = _get_dictionary_domains()[domain_file]
        filepath = REF_DIR / domain_file
        count = 0
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            count = len(re.findall(r'^###\s+\S', content, re.MULTILINE))
        print(f"  {domain_file:<35} {info['title']:<35} {count}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Agent 3: Reference Dictionary Agent")
        print()
        print("Commands:")
        print("  extract-terms <doc.md>    Extract and add novel terms from a document")
        print("  check-term <term>         Check if a term exists in the dictionary")
        print("  add-term <term>           Add a single term")
        print("  list-domains              List all dictionary domain files")
        return 1

    cmd = sys.argv[1]
    if cmd == "extract-terms":
        return cmd_extract_terms(sys.argv[1:])
    elif cmd == "check-term":
        return cmd_check_term(sys.argv[1:])
    elif cmd == "add-term":
        return cmd_add_term(sys.argv[1:])
    elif cmd == "list-domains":
        return cmd_list_domains(sys.argv[1:])
    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
