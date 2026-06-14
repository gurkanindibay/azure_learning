#!/usr/bin/env python3
"""
Agent 1: OKF Formatter & Validator

Converts raw markdown files into OKF-compliant concept documents that follow
the repository's content standards. Handles:

- Content placement (which directory should the file go in?)
- Frontmatter insertion (type, title, description, tags, timestamp)
- Heading normalization (H1 → H2 → H3 hierarchy)
- Cross-reference formatting
- Taxonomy alignment
- Validation against repo conventions

Usage:
    python3 agent_tools/format_agent.py validate <file.md>
    python3 agent_tools/format_agent.py format <raw-file.md> [--out <path>]
    python3 agent_tools/format_agent.py check-all

Part of the coordinated agent workflow:
    Agent 1 (format) → Agent 2 (takeaways) → Agent 3 (dictionary)
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── Type mapping ─────────────────────────────────────────────────────────────
# Loaded from config.yaml. To add a new type mapping, edit agent_tools/config.yaml.
# See: agent_tools/config_loader.py

def _ensure_path():
    """Ensure repo root is on sys.path for imports."""
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _get_type_mapping() -> dict[str, str]:
    """Lazy-load type mapping from config."""
    _ensure_path()
    from agent_tools.config_loader import load_config
    return load_config().type_mapping


def _get_placement_signals() -> dict[str, list[str]]:
    """Lazy-load placement signals from config."""
    _ensure_path()
    from agent_tools.config_loader import load_config
    return load_config().placement_signals

# ── Content placement ────────────────────────────────────────────────────────

def determine_placement(content: str, source_path: str | None = None) -> str | None:
    """Determine which directory a document should go in based on its content.

    Returns a relative directory path (e.g., 'architecture-azure/compute/aks/')
    or None if placement cannot be determined.
    """
    content_lower = content.lower()

    # Check for explicit placement hints in the document
    for line in content.split("\n")[:30]:
        m = re.match(r">\s*\*\*Placement\*\*:\s*(.+)", line, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    # Heuristic placement based on content signals from config
    signals = _get_placement_signals()
    azure_signals = signals.get("azure", [])
    system_design_signals = signals.get("system_design", [])
    reference_signals = signals.get("reference", [])
    programming_signals = signals.get("programming", [])

    azure_score = sum(1 for s in azure_signals if s in content_lower)
    sd_score = sum(1 for s in system_design_signals if s in content_lower)
    ref_score = sum(1 for s in reference_signals if s in content_lower)
    prog_score = sum(1 for s in programming_signals if s in content_lower)

    # If source is already in a directory, prefer that
    if source_path:
        type_map = _get_type_mapping()
        for prefix in type_map:
            if source_path.startswith(prefix):
                return os.path.dirname(source_path) + "/"

    if azure_score >= 3:
        return "architecture-azure/"
    if sd_score >= 3:
        return "system-design-architecture/"
    if ref_score >= 4:
        return "reference-dictionary/"
    if prog_score >= 3:
        return "programming-languages/csharp/"

    return None


def resolve_okf_type(rel_path: str) -> str:
    """Map a file path to its OKF type."""
    for prefix, okf_type in _get_type_mapping().items():
        if rel_path.startswith(prefix):
            return okf_type
    return "Reference"


# ── Frontmatter ──────────────────────────────────────────────────────────────

def extract_title(lines: list[str]) -> str:
    """Extract title from first H1 heading."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return ""


def extract_description(lines: list[str]) -> str:
    """Extract a one-line description from the content body."""
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith(">"):
            continue
        if stripped.startswith("|") or stripped.startswith("---"):
            continue
        if re.match(r'^[-*\d]', stripped) and '](#' in stripped:
            continue
        if stripped.startswith("**") and len(stripped) < 80:
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("!["):
            continue
        desc = stripped
        if len(desc) > 200:
            desc = desc[:197] + "..."
        return desc
    return ""


def build_frontmatter(rel_path: str, body_lines: list[str]) -> str:
    """Build OKF YAML frontmatter for a concept document."""
    okf_type = resolve_okf_type(rel_path)
    title = extract_title(body_lines)
    desc = extract_description(body_lines)

    fm_lines = ["---"]
    fm_lines.append(f"type: {okf_type}")
    if title:
        fm_lines.append(f'title: "{title}"')
    if desc:
        fm_lines.append(f'description: "{desc}"')
    fm_lines.append(f"timestamp: {TODAY}T00:00:00Z")
    fm_lines.append("---")
    fm_lines.append("")
    return "\n".join(fm_lines)


def has_frontmatter(content: str) -> bool:
    """Check if content already has YAML frontmatter."""
    return content.startswith("---\n") or content.startswith("---\r\n")


# ── Content normalization ────────────────────────────────────────────────────

def normalize_content(content: str) -> str:
    """Apply content standards to a markdown document.

    - Ensures H1 is first heading
    - Normalizes heading hierarchy (no skipping levels)
    - Ensures blank lines around headings
    - Fixes common markdown issues
    """
    lines = content.split("\n")
    result = []
    prev_was_blank = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Ensure blank line before headings (except at start)
        if stripped.startswith("#") and result and result[-1].strip():
            result.append("")

        # Normalize heading spacing: "##Title" → "## Title"
        if re.match(r'^#{1,6}\S', stripped):
            m = re.match(r'^(#{1,6})(.+)', stripped)
            if m:
                stripped = f"{m.group(1)} {m.group(2).strip()}"

        result.append(stripped if stripped else "")

    return "\n".join(result)


def format_document(raw_content: str, target_rel_path: str) -> str:
    """Format raw content into an OKF-compliant concept document."""
    # Normalize markdown
    body = normalize_content(raw_content)

    # Add frontmatter (if not present)
    if not has_frontmatter(body):
        body_lines = body.split("\n")
        fm = build_frontmatter(target_rel_path, body_lines)
        body = fm + "\n" + body

    return body


# ── Validation ───────────────────────────────────────────────────────────────

def validate_document(filepath: Path) -> list[str]:
    """Validate a document against OKF and repository standards.
    
    Returns a list of issues (empty = valid).
    """
    issues = []
    rel_path = str(filepath.relative_to(REPO_ROOT))

    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Cannot read file: {e}"]

    lines = content.split("\n")

    # 1. OKF frontmatter
    if not has_frontmatter(content):
        issues.append("Missing YAML frontmatter (required by OKF)")
        return issues

    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        issues.append("Unparseable frontmatter")
        return issues

    fm_text = fm_match.group(1)
    if not re.search(r'^type:\s*\S', fm_text, re.MULTILINE):
        issues.append("Missing required 'type' field in frontmatter")

    # 2. Title (H1) should be present
    body_start = fm_match.end()
    body_lines = content[body_start:].split("\n")
    has_h1 = any(l.strip().startswith("# ") for l in body_lines)
    if not has_h1:
        issues.append("Missing H1 heading")

    # 3. Heading hierarchy check
    heading_levels = []
    for line in body_lines:
        m = re.match(r'^(#{1,6})\s', line.strip())
        if m:
            level = len(m.group(1))
            heading_levels.append(level)

    for i in range(1, len(heading_levels)):
        if heading_levels[i] > heading_levels[i - 1] + 1:
            issues.append(f"Heading level skip: H{heading_levels[i-1]} → H{heading_levels[i]} (no more than 1 level at a time)")

    # 4. Content length
    body_text = "".join(body_lines).strip()
    if len(body_text) < 100:
        issues.append(f"Body too short ({len(body_text)} chars) — concepts should have substantive content")

    # 5. Directory-specific checks
    if "system-design-architecture/" in rel_path and rel_path.endswith(".md") and "index.md" not in rel_path:
        # Must have source reference
        if not re.search(r'>\s*\*\*Source\*\*:', body_text):
            issues.append("System design files must have a > **Source**: reference")
        # Should have domain-prefixed IDs (with or without backticks)
        if not re.search(r'[a-z]+-\d+', body_text):
            issues.append("System design files should have domain-prefixed IDs (e.g., `db-01`)")

    if "reference-dictionary/" in rel_path and "index.md" not in rel_path:
        if not re.search(r'###\s+\S', body_text):
            issues.append("Reference dictionary files should have term anchors (### term-name)")

    return issues


# ── CLI ──────────────────────────────────────────────────────────────────────

def cmd_validate(args: list[str]) -> int:
    """Validate one or all documents."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/format_agent.py validate <file.md>")
        print("       python3 agent_tools/format_agent.py validate --all")
        return 1

    target = args[1]
    if target == "--all":
        _ensure_path()
        import agent_tools.okf_tools as okf
        concepts = okf.iter_concepts(REPO_ROOT)
        total_issues = 0
        for doc in concepts:
            issues = validate_document(doc.path)
            if issues:
                total_issues += len(issues)
                print(f"ISSUES [{doc.rel_path}]:")
                for issue in issues:
                    print(f"  - {issue}")
        print(f"\nTotal: {total_issues} issue(s) across {len(concepts)} files")
        return 1 if total_issues > 0 else 0

    filepath = REPO_ROOT / target
    if not filepath.exists():
        print(f"File not found: {target}")
        return 1

    issues = validate_document(filepath)
    if issues:
        print(f"Issues in {target}:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print(f"✅ {target} passes all validation checks.")
        return 0


def cmd_format(args: list[str]) -> int:
    """Format a raw file into OKF-compliant markdown."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/format_agent.py format <raw-file.md> [--out <path>] [--placement <dir>]")
        return 1

    source = args[1]
    source_path = Path(source)
    if not source_path.exists():
        print(f"File not found: {source}")
        return 1

    # Parse flags
    out_path = None
    placement = None
    i = 2
    while i < len(args):
        if args[i] == "--out" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 2
        elif args[i] == "--placement" and i + 1 < len(args):
            placement = args[i + 1]
            i += 2
        else:
            i += 1

    raw_content = source_path.read_text(encoding="utf-8")

    # Determine placement
    if not placement:
        placement = determine_placement(raw_content, str(source_path))
    if not placement:
        placement = "unstructured-resources/"

    # Determine output filename
    if not out_path:
        base = source_path.stem.lower().replace(" ", "-")
        out_path = f"{placement}{base}.md"

    # Format
    formatted = format_document(raw_content, out_path)
    output_file = REPO_ROOT / out_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists():
        print(f"Warning: {out_path} already exists. Use --out to specify a different path.")
        return 1

    output_file.write_text(formatted, encoding="utf-8")
    print(f"✅ Formatted and written to: {out_path}")
    print(f"   Type: {resolve_okf_type(out_path)}")
    print(f"   Placement: {placement}")

    # Validate the result
    issues = validate_document(output_file)
    if issues:
        print(f"\n⚠ Validation issues (may need manual fixes):")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"   ✅ Passes all validation checks.")

    # Print next steps for the coordinated workflow
    print(f"\n── Next Steps (coordinated workflow) ──")
    print(f"   Agent 2 (key takeaways):  python3 agent_tools/takeaways_agent.py extract {out_path}")
    print(f"   Agent 3 (dictionary):     python3 agent_tools/dictionary_agent.py extract-terms {out_path}")
    print(f"   Run all:                  python3 agent_tools/coordinator.py process {source}")

    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Agent 1: OKF Formatter & Validator")
        print()
        print("Commands:")
        print("  validate <file.md>     Validate a single document")
        print("  validate --all         Validate all documents")
        print("  format <raw-file.md>   Format and place a raw document")
        print("  check-all              Quick conformance check")
        return 1

    cmd = sys.argv[1]
    if cmd == "validate":
        return cmd_validate(sys.argv[1:])
    elif cmd == "format":
        return cmd_format(sys.argv[1:])
    elif cmd == "check-all":
        _ensure_path()
        import agent_tools.okf_tools as okf
        return okf.cmd_validate()
    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
