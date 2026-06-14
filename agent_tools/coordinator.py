#!/usr/bin/env python3
"""
OKF Agent Coordinator

Orchestrates the three agents to process new documents in a coordinated workflow:

    Agent 1 (format_agent)    → Formats raw markdown into OKF-compliant concepts
    Agent 2 (takeaways_agent) → [Optional] Extracts system-design takeaways
    Agent 3 (dictionary_agent)→ Adds novel terms to the reference dictionary

Full workflow:
    python3 agent_tools/coordinator.py process <raw-file.md> [--no-takeaways]

Individual steps:
    python3 agent_tools/coordinator.py step format <file.md>
    python3 agent_tools/coordinator.py step takeaways <article.md> --prefix <domain>
    python3 agent_tools/coordinator.py step dictionary <file.md>

Usage:
    python3 agent_tools/coordinator.py process <raw-file.md>    # Full pipeline
    python3 agent_tools/coordinator.py process <raw-file.md> --no-takeaways  # Skip takeaways
    python3 agent_tools/coordinator.py validate-all             # Run all validations
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agent_tools"


def run_agent(agent_name: str, *args: str) -> tuple[int, str, str]:
    """Run an agent script and return (exit_code, stdout, stderr)."""
    script = AGENTS_DIR / f"{agent_name}.py"
    cmd = ["python3", str(script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    return result.returncode, result.stdout, result.stderr


def print_step(step_num: int, title: str):
    """Print a formatted step header."""
    print()
    print("=" * 70)
    print(f"  STEP {step_num}: {title}")
    print("=" * 70)


def cmd_process(args: list[str]) -> int:
    """Run the full coordinated pipeline."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/coordinator.py process <raw-file.md> [--no-takeaways] [--placement <dir>]")
        print()
        print("Full workflow:")
        print("  1. Format & Validate — converts raw markdown to OKF concept")
        print("  2. Key Takeaways    — [optional] extracts system-design takeaways")
        print("  3. Dictionary       — adds novel terms to reference-dictionary")
        print()
        print("Options:")
        print("  --no-takeaways    Skip the takeaways step")
        print("  --placement <dir> Force placement directory")
        return 1

    source = args[1]
    source_path = Path(source)
    if not source_path.is_absolute():
        source_path = REPO_ROOT / source

    if not source_path.exists():
        print(f"❌ File not found: {source}")
        return 1

    no_takeaways = "--no-takeaways" in args
    placement = None
    for i, a in enumerate(args):
        if a == "--placement" and i + 1 < len(args):
            placement = args[i + 1]

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           OKF Agent Coordinator — Full Pipeline                 ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  Source: {source_path.name:<52} ║")
    print(f"║  Pipeline: Format → {'Takeaways → ' if not no_takeaways else ''}Dictionary{'     ' if no_takeaways else '           '} ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    # ── Step 1: Format & Validate ──
    print_step(1, "Format & Validate (Agent 1)")
    fmt_args = ["format", str(source_path)]
    if placement:
        fmt_args.extend(["--placement", placement])
    code, stdout, stderr = run_agent("format_agent", *fmt_args)

    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if code != 0:
        print("\n❌ Format step failed. Aborting pipeline.")
        return code

    # Extract the output path from the formatter output
    output_path = None
    for line in stdout.split("\n"):
        m = re.search(r'Formatted and written to: (.+\.md)', line)
        if m:
            output_path = m.group(1).strip()
            break

    if not output_path:
        # Try to find the output file
        for line in stdout.split("\n"):
            m = re.search(r'→\s+(\S+\.md)', line)
            if m:
                output_path = m.group(1).strip()
                break

    if not output_path:
        print("\n⚠ Could not determine output path from formatter. Skipping remaining steps.")
        return 1

    print(f"\n📄 Output file: {output_path}")

    # ── Step 2: Key Takeaways (optional) ──
    takeaways_output = None
    if not no_takeaways:
        # Only run takeaways for articles or documents that seem suitable
        if "articles/" in output_path or "unstructured-resources/" in output_path:
            print_step(2, "Key Takeaways (Agent 2)")
            code, stdout, stderr = run_agent("takeaways_agent", "extract", output_path, "--dry-run")
            print(stdout)

            # Check if takeaways would be useful
            if "Suggested domain prefixes:" in stdout and "score:" in stdout:
                print("\n📝 Takeaways can be generated for this article.")
                print("   To generate, run:")
                print(f"   python3 agent_tools/takeaways_agent.py extract {output_path}")
            else:
                print("\n⏭ No strong takeaways signal detected. Skipping (use --force-takeaways to override).")
        else:
            print_step(2, "Key Takeaways — SKIPPED")
            print(f"   File is in '{output_path.split('/')[0]}/', not an article directory.")
            print("   Takeaways are typically generated from articles/ or unstructured-resources/.")
    else:
        print_step(2, "Key Takeaways — SKIPPED (--no-takeaways)")

    # ── Step 3: Reference Dictionary ──
    print_step(3 if not no_takeaways else 2, "Reference Dictionary (Agent 3)")
    code, stdout, stderr = run_agent("dictionary_agent", "extract-terms", output_path)
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    # ── Final validation ──
    print()
    print("=" * 70)
    print("  FINAL: Cross-Agent Validation")
    print("=" * 70)
    code, stdout, stderr = run_agent("okf_tools", "validate")
    print(stdout)

    # ── Step 4: Domain Discovery ──
    print()
    print("=" * 70)
    print("  STEP 4: Domain Discovery")
    print("=" * 70)
    code, stdout, stderr = run_agent("discovery_agent")
    print(stdout)
    if "Nothing new to discover" not in stdout:
        print("\n💡 New domains discovered! Run to register:")
        print("   python3 agent_tools/discovery_agent.py --apply")

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  Pipeline Complete                                              ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  Formatted:  {output_path:<48} ║")
    if takeaways_output:
        print(f"║  Takeaways:  {takeaways_output:<48} ║")
    print(f"║  Dictionary: Terms extracted & added                           ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  Next: Edit TODO sections, run taxonomy sync, commit           ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    return 0


def cmd_step(args: list[str]) -> int:
    """Run a single agent step."""
    if len(args) < 2:
        print("Usage: python3 agent_tools/coordinator.py step <agent> [agent-args...]")
        print()
        print("Agents:")
        print("  format <file.md>           Run format agent")
        print("  takeaways <article.md>     Run takeaways agent")
        print("  dictionary <file.md>       Run dictionary agent")
        return 1

    agent_map = {
        "format": "format_agent",
        "takeaways": "takeaways_agent",
        "dictionary": "dictionary_agent",
    }

    agent = args[1]
    if agent not in agent_map:
        print(f"Unknown agent: {agent}")
        print(f"Available: {', '.join(agent_map)}")
        return 1

    script_name = agent_map[agent]
    agent_args = args[2:] if len(args) > 2 else []

    code, stdout, stderr = run_agent(script_name, *agent_args)
    print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    return code


def cmd_validate_all(args: list[str]) -> int:
    """Run all validation checks."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           Full Repository Validation                            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    errors = 0

    # OKF Conformance
    print("── OKF Conformance ──")
    code, stdout, stderr = run_agent("okf_tools", "validate")
    print(stdout)
    if code != 0:
        errors += 1

    # Format validation
    print("── Format Standards ──")
    code, stdout, stderr = run_agent("format_agent", "validate", "--all")
    # Only show issues
    for line in stdout.split("\n"):
        if line.startswith("ISSUES") or line.startswith("  -") or line.startswith("Total"):
            print(line)
    if code != 0:
        errors += 1

    # Cross-reference check
    print("── Cross-References ──")
    code, stdout, stderr = run_agent("okf_tools", "check-links")
    # Show only first 10 broken links
    shown = 0
    for line in stdout.split("\n"):
        if line.startswith("BROKEN"):
            if shown < 10:
                print(line)
            shown += 1
        elif line.startswith("✅") or line.startswith("❌"):
            print(line)
    if shown > 10:
        print(f"  ... and {shown - 10} more broken links")
    if code != 0:
        errors += 1

    # Taxonomy sync
    print("── Taxonomy Sync ──")
    result = subprocess.run(
        ["python3", "scripts/sync_taxonomy_reference.py", "--check"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        errors += 1

    print()
    if errors == 0:
        print("✅ All validations passed!")
    else:
        print(f"❌ {errors} validation(s) failed.")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("OKF Agent Coordinator")
        print()
        print("Commands:")
        print("  process <raw-file.md>    Run the full 3-agent pipeline")
        print("  step <agent> <args...>   Run a single agent step")
        print("  validate-all             Run all validations")
        print()
        print("Agents:")
        print("  Agent 1 (format_agent)     Format raw files into OKF markdown")
        print("  Agent 2 (takeaways_agent)  Create system-design takeaway files")
        print("  Agent 3 (dictionary_agent) Add novel terms to reference-dictionary")
        return 1

    cmd = sys.argv[1]
    if cmd == "process":
        return cmd_process(sys.argv[1:])
    elif cmd == "step":
        return cmd_step(sys.argv[1:])
    elif cmd == "validate-all":
        return cmd_validate_all(sys.argv[1:])
    else:
        print(f"Unknown command: {cmd}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
