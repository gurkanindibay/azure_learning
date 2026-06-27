---
name: okf-domain-discovery
description: 'Discover and register domains whose prefix is absent from agent_tools/config.yaml at the start of the run when files are added to system-design-architecture/ or reference-dictionary/. Use when: a new takeaway file is created, a new dictionary file appears, after running the coordinator pipeline, during repository maintenance.'
argument-hint: 'Check for undiscovered domains or register new ones'
user-invocable: true
---

# Skill: OKF Domain Discovery

Run discovery only on new or modified files under `system-design-architecture/` and `reference-dictionary/` since the last successful run; do not scan unrelated repository paths. Ensures `agent_tools/config.yaml` stays in sync with the filesystem.

## When to Use

- After creating a new takeaway file in `system-design-architecture/` (e.g., `29-mesh-key-takeaways.md`)
- After creating a new dictionary file in `reference-dictionary/` (e.g., `security-iam.md`)
- After running the coordinator pipeline (`python3 agent_tools/coordinator.py process ...`)
- During repository maintenance, scan only files under `system-design-architecture/` and `reference-dictionary/` and compare their discovered domain prefixes against `agent_tools/config.yaml`

## Procedure

### Step 1: Scan for undiscovered domains

```bash
python3 agent_tools/discovery_agent.py
```

If the command exits with a non-zero status, prints an error, or does not produce a parseable result, stop immediately and report the failure; do not continue to `--dry-run` or `--apply`.

If output is "✅ All domains are registered", no action needed.

### Step 2: Review suggested registrations

```bash
python3 agent_tools/discovery_agent.py --dry-run
```

Review the suggested prefix, description, and keywords for each new domain. If a discovered domain already exists in `agent_tools/config.yaml`, keep the existing entry and do not overwrite it unless the user explicitly asks for an update.

### Step 3: Register the domains

```bash
python3 agent_tools/discovery_agent.py --apply
```

### Step 4: Verify

```bash
python3 agent_tools/takeaways_agent.py list-domains    # For takeaway domains
python3 agent_tools/dictionary_agent.py list-domains    # For dictionary domains
```

### Single file analysis

```bash
python3 agent_tools/discovery_agent.py --watch system-design-architecture/29-mesh-key-takeaways.md
```

## Scripts

- [Discovery Agent](../../../agent_tools/discovery_agent.py) — Main executable that performs discovery and config updates
- [Config Loader](../../../agent_tools/config_loader.py) — Config loader with auto-discovery at runtime
- [Config File](../../../agent_tools/config.yaml) — Single source of truth for all domain registrations

## References

- [Agent Configuration](../../../agent_tools/config.yaml) — Domain registries source of truth
- [Takeaways Agent](../../../agent_tools/takeaways_agent.py) — Uses registered takeaway domains
- [Dictionary Agent](../../../agent_tools/dictionary_agent.py) — Uses registered dictionary domains
