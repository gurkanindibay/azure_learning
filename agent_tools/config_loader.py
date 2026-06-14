#!/usr/bin/env python3
"""
Agent Configuration Loader

Loads domain registries from config.yaml and auto-discovers domains
from the filesystem. Provides a unified API for all 3 coordinated agents.

Key principle: The filesystem IS the source of truth.
- When a new file like `system-design-architecture/29-foo-key-takeaways.md`
  appears, the takeaways agent auto-discovers the `foo` prefix.
- When a new file like `reference-dictionary/new-domain.md` appears,
  the dictionary agent auto-discovers it.
- config.yaml provides descriptions, keywords, and hints — auto-discovery
  fills in what config.yaml doesn't cover.

Usage:
    from agent_tools.config_loader import load_config
    cfg = load_config()

    # Agent 1: Format agent
    cfg.type_mapping        # dict: dir_prefix → OKF type
    cfg.placement_signals   # dict: category → [keywords]

    # Agent 2: Takeaways agent
    cfg.takeaway_domains    # dict: prefix → {file, desc, keywords}
    cfg.takeaway_keywords   # dict: keyword → prefix

    # Agent 3: Dictionary agent
    cfg.dictionary_domains  # dict: filename → {title, keywords}
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


# ── Simple YAML parser (no PyYAML dependency) ───────────────────────────────

def _parse_yaml(text: str) -> dict[str, Any]:
    """Parse a simple YAML document into nested dicts/lists.
    
    Handles: scalars, lists, nested mappings. Does NOT handle anchors,
    aliases, multi-line scalars (|, >), tags, or complex types.
    """
    lines = text.split("\n")
    result: dict[str, Any] = {}
    stack: list[dict[str, Any]] = [result]
    current_key: str | None = None
    current_list: list[Any] | None = None
    indent_stack: list[int] = [-1]

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line or line.strip().startswith("#"):
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Pop stack until we find the right parent
        while indent_stack and indent <= indent_stack[-1]:
            if len(stack) > 1:
                stack.pop()
            indent_stack.pop()
            current_list = None

        parent = stack[-1]

        # List item: "- value"
        if stripped.startswith("- "):
            value = _parse_yaml_value(stripped[2:].strip())
            if current_list is None:
                # Shouldn't happen in a mapping context, but handle gracefully
                continue
            current_list.append(value)
            continue

        # Key: value (or key:)
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if val:
                # Scalar value
                if current_list is not None:
                    # Flush list
                    parent[current_key] = current_list  # type: ignore[index]
                    current_list = None
                parent[key] = _parse_yaml_value(val)
                current_key = None
            else:
                # Could be a nested mapping or a list
                # Peek ahead to determine
                current_key = key
                current_list = None

                # Check next non-comment line
                # We'll determine on the next iteration
                # For now, set up for potential list
                pass

    # Don't leave a pending list
    return result


def _parse_yaml_value(val: str) -> Any:
    """Parse a YAML scalar value."""
    val = val.strip()
    if val in ("true", "True", "yes"):
        return True
    if val in ("false", "False", "no"):
        return False
    if val in ("null", "~", ""):
        return None
    # Unquoted string
    if (val.startswith('"') and val.endswith('"')) or \
       (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val


def _build_nested_yaml(lines: list[str]) -> dict[str, Any]:
    """Build nested structure from indented YAML lines.
    
    Handles indentation-based nesting, lists, and nested mappings.
    """
    result: dict[str, Any] = {}
    # Stack of (indent, container, key_if_list)
    stack: list[tuple[int, dict[str, Any] | list[Any], str | None]] = [(-1, result, None)]

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line or line.strip().startswith("#"):
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Pop stack to find the right parent based on indent
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()

        parent_indent, parent_container, list_key = stack[-1]

        # List item: "- value"
        if stripped.startswith("- "):
            val = _parse_yaml_value(stripped[2:].strip())
            if isinstance(parent_container, list):
                parent_container.append(val)
            elif list_key is not None:
                # Parent is a dict with a pending list key
                if list_key not in parent_container or not isinstance(parent_container[list_key], list):
                    parent_container[list_key] = []  # type: ignore[index]
                parent_container[list_key].append(val)  # type: ignore[index]
            continue

        # Key: value (or key:)
        if ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if not isinstance(parent_container, dict):
                continue

            if val:
                # Scalar value
                parent_container[key] = _parse_yaml_value(val)
            else:
                # Peek ahead to determine if this starts a list or nested mapping
                next_indent = _peek_next_indent(lines, raw_line)
                if next_indent is not None and next_indent > indent:
                    # Check if next line is a list item
                    next_line = _peek_next_line(lines, raw_line)
                    if next_line is not None and next_line.strip().startswith("- "):
                        # This key will hold a list
                        parent_container[key] = []
                        stack.append((indent, parent_container[key], key))  # type: ignore[arg-type]
                    else:
                        # This key will hold a nested mapping
                        nested: dict[str, Any] = {}
                        parent_container[key] = nested
                        stack.append((indent, nested, None))
                else:
                    # Empty value or same-indent next — treat as None
                    parent_container[key] = None

    return result


def _peek_next_line(lines: list[str], current_line: str) -> str | None:
    """Peek at the next non-comment line."""
    found = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not found:
            if line.rstrip() == current_line:
                found = True
            continue
        return line
    return None


def _peek_next_indent(lines: list[str], current_line: str) -> int | None:
    """Peek at the indent of the next non-comment line."""
    found_current = False
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not found_current:
            if line.rstrip() == current_line:
                found_current = True
            continue
        return len(line) - len(line.lstrip())
    return None


# ── Config class ────────────────────────────────────────────────────────────

class AgentConfig:
    """Unified configuration for all 3 agents.
    
    Fields are populated from config.yaml and auto-discovered from the filesystem.
    """

    def __init__(self):
        # Load from YAML
        yaml_data = self._load_yaml_file(CONFIG_PATH)

        # ── Agent 1: Format Agent ──
        self.type_mapping: dict[str, str] = {}
        for prefix, otype in yaml_data.get("type_mapping", {}).items():
            if isinstance(otype, str):
                self.type_mapping[prefix] = otype

        sig = yaml_data.get("placement_signals", {})
        self.placement_signals: dict[str, list[str]] = {}
        if isinstance(sig, dict):
            for cat, words in sig.items():
                if isinstance(words, list):
                    self.placement_signals[cat] = [str(w) for w in words]

        # ── Agent 2: Takeaways Agent ──
        self.takeaway_domains: dict[str, dict] = {}
        td = yaml_data.get("takeaway_domains", {})
        if isinstance(td, dict):
            for prefix, info in td.items():
                if isinstance(info, dict):
                    self.takeaway_domains[prefix] = info

        self.takeaway_keywords: dict[str, str] = {}
        tk = yaml_data.get("takeaway_keywords", {})
        if isinstance(tk, dict):
            for kw, prefix in tk.items():
                self.takeaway_keywords[kw] = str(prefix)

        # ── Agent 3: Dictionary Agent ──
        self.dictionary_domains: dict[str, dict] = {}
        dd = yaml_data.get("dictionary_domains", {})
        if isinstance(dd, dict):
            for filename, info in dd.items():
                if isinstance(info, dict):
                    self.dictionary_domains[filename] = info

        # ── Auto-discovery from filesystem ──
        self._autodiscover_takeaway_domains()
        self._autodiscover_dictionary_domains()

    @staticmethod
    def _load_yaml_file(path: Path) -> dict[str, Any]:
        """Load and parse a YAML file."""
        if not path.exists():
            print(f"Warning: Config file not found: {path}")
            return {}
        return _build_nested_yaml(path.read_text(encoding="utf-8").split("\n"))

    def _autodiscover_takeaway_domains(self):
        """Scan system-design-architecture/ for *-key-takeaways.md files.
        
        Extract domain prefix from filename:
            "29-foo-key-takeaways.md" → prefix "foo"
        Only registers files that don't already have a config entry
        (matched by filename, not by prefix key).
        """
        sda = REPO_ROOT / "system-design-architecture"
        if not sda.is_dir():
            return

        # Build set of already-registered filenames
        registered_files = {info.get("file", "") for info in self.takeaway_domains.values()}

        for f in sorted(sda.glob("*-key-takeaways.md")):
            if f.name in registered_files:
                continue  # Already in config

            m = re.match(r'\d+-(.+)-key-takeaways\.md$', f.name)
            if m:
                prefix = m.group(1)
                if prefix not in self.takeaway_domains:
                    desc = prefix.replace("-", " ").title()
                    self.takeaway_domains[prefix] = {
                        "file": f.name,
                        "desc": desc,
                        "auto": True,
                    }

    def _autodiscover_dictionary_domains(self):
        """Scan reference-dictionary/ for *.md files.
        
        Auto-register any domain file not in config.yaml.
        """
        ref_dir = REPO_ROOT / "reference-dictionary"
        if not ref_dir.is_dir():
            return

        for f in sorted(ref_dir.glob("*.md")):
            if f.name == "index.md":
                continue
            if f.name not in self.dictionary_domains:
                # Auto-register with derived title
                title = f.stem.replace("-", " ").title()
                self.dictionary_domains[f.name] = {
                    "title": title,
                    "keywords": [],
                    "auto": True,
                }

    def resolve_type(self, rel_path: str) -> str:
        """Resolve OKF type from a file path."""
        for prefix, otype in self.type_mapping.items():
            if rel_path.startswith(prefix):
                return otype
        return "Reference"

    def find_takeaway_domain(self, prefix: str) -> dict | None:
        """Find a takeaway domain by prefix."""
        return self.takeaway_domains.get(prefix)

    def find_dictionary_domain(self, keyword: str) -> str | None:
        """Find which dictionary domain file a term should go in."""
        best_file = None
        best_score = 0.0
        kw_lower = keyword.lower()

        for filename, info in self.dictionary_domains.items():
            score = 0.0
            for kw in info.get("keywords", []):
                if kw in kw_lower:
                    score += 1.0
                for word in kw.split():
                    if word in kw_lower:
                        score += 0.5
            if score > best_score:
                best_score = score
                best_file = filename

        if best_score >= 1.0:
            return best_file
        return "architecture-patterns.md"  # Default catch-all

    def suggest_takeaway_prefix(self, content: str) -> list[tuple[str, float]]:
        """Suggest domain prefixes based on content keywords."""
        content_lower = content.lower()
        scores: dict[str, float] = {}

        for keyword, prefix in self.takeaway_keywords.items():
            count = content_lower.count(keyword)
            if count > 0:
                scores[prefix] = scores.get(prefix, 0.0) + count

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:5]


# ── Singleton ────────────────────────────────────────────────────────────────

_config: AgentConfig | None = None


def load_config() -> AgentConfig:
    """Load (or return cached) agent configuration."""
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def reload_config() -> AgentConfig:
    """Force reload configuration from disk."""
    global _config
    _config = AgentConfig()
    return _config


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Agent Configuration Loader")
        print()
        print("Usage:")
        print("  python3 agent_tools/config_loader.py              Show current config")
        print("  python3 agent_tools/config_loader.py --domains    List takeaway domains")
        print("  python3 agent_tools/config_loader.py --dict       List dictionary domains")
        print("  python3 agent_tools/config_loader.py --types      List type mappings")
        sys.exit(0)

    cfg = load_config()

    if "--domains" in sys.argv:
        print("Takeaway Domains (prefix → description):")
        for pfx in sorted(cfg.takeaway_domains):
            info = cfg.takeaway_domains[pfx]
            tag = " [auto]" if info.get("auto") else ""
            print(f"  {pfx:<12} {info['desc']:<35} ({info['file']}){tag}")
        print(f"\n  Total: {len(cfg.takeaway_domains)} domain(s)")

    elif "--dict" in sys.argv:
        print("Dictionary Domains (file → title):")
        for fname in sorted(cfg.dictionary_domains):
            info = cfg.dictionary_domains[fname]
            tag = " [auto]" if info.get("auto") else ""
            kw_count = len(info.get("keywords", []))
            print(f"  {fname:<35} {info['title']:<35} ({kw_count} keywords){tag}")
        print(f"\n  Total: {len(cfg.dictionary_domains)} domain(s)")

    elif "--types" in sys.argv:
        print("Type Mappings (prefix → type):")
        for prefix, otype in cfg.type_mapping.items():
            print(f"  {prefix:<40} {otype}")
        print(f"\n  Total: {len(cfg.type_mapping)} type(s)")

    else:
        print("Agent Configuration Summary")
        print(f"  Type mappings:         {len(cfg.type_mapping)}")
        print(f"  Takeaway domains:      {len(cfg.takeaway_domains)}")
        print(f"  Takeaway keywords:     {len(cfg.takeaway_keywords)}")
        print(f"  Dictionary domains:    {len(cfg.dictionary_domains)}")
        print(f"  Placement categories:  {len(cfg.placement_signals)}")
        print()
        print("Auto-discovered:")
        auto_td = sum(1 for d in cfg.takeaway_domains.values() if d.get("auto"))
        auto_dd = sum(1 for d in cfg.dictionary_domains.values() if d.get("auto"))
        print(f"  Takeaway domains:      {auto_td}")
        print(f"  Dictionary domains:    {auto_dd}")
