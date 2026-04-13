---
title: "Consolidate swain-init inline bash into a single preflight script"
artifact: SPEC-301
track: implementable
status: Active
author: cristos
created: 2026-04-04
last-updated: 2026-04-04
priority-weight: medium
type: enhancement
parent-epic: EPIC-048
parent-initiative: ""
linked-artifacts:
  - SPEC-196
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Consolidate swain-init inline bash into a single preflight script

## Problem Statement

swain-init's SKILL.md has 32 inline bash blocks across 677 lines. Each block is a check (marker file, uv, tk, pre-commit, superpowers, tmux, shell launcher, governance, README, etc.) that the LLM reads and runs one at a time. This has two costs:

1. **Token overhead** --- the LLM parses hundreds of lines of shell code it does not need to reason about. The checks are rote, not creative.
2. **Fragility** --- each block lives in the skill file with no test coverage. Changes mean editing code inside prose.

## Desired Outcomes

One script --- `swain-init-preflight.sh` --- runs every check and emits JSON. The skill file reads that JSON and decides what to do (ask the user, skip, proceed) instead of running raw shell inline. The skill file shrinks, the checks gain test coverage, and the LLM spends tokens on choices rather than on `command -v uv`.

## External Behavior

**Before:**
```
LLM reads SKILL.md → runs bash block 1 → interprets → runs bash block 2 → ... → runs bash block 32
```

**After:**
```
LLM reads SKILL.md → runs swain-init-preflight.sh → reads JSON → makes decisions per phase
```

The preflight script checks everything that can be checked without user input:

- `.swain-init` marker existence and version
- CLAUDE.md / AGENTS.md state (fresh, migrated, standard, split)
- `uv` availability
- vendored `tk` path and health
- `.beads/` migration candidacy
- `usr/bin/` manifest directories for operator symlinks
- `.pre-commit-config.yaml` existence
- `pre-commit` framework availability
- superpowers installation status
- tmux availability
- shell type, rc file, existing launcher detection
- installed agentic runtimes
- governance block presence in AGENTS.md
- README.md existence and artifact tree density
- `.agents/` directory state

The script outputs one JSON object with a key per check. The skill file's phases become decision logic over that JSON --- not shell runs.

## Acceptance Criteria

1. Given swain-init-preflight.sh exists at `.agents/bin/swain-init-preflight.sh`, when run from a repo root, then it exits 0 and emits valid JSON to stdout.

2. Given the preflight JSON, when the skill file processes Phase 0 (already-initialized detection), then it reads `marker.exists`, `marker.last_version`, and `marker.current_version` from JSON instead of running inline shell.

3. Given the preflight JSON, when the skill file processes Phase 1 (CLAUDE.md migration), then it reads `migration.state` (one of: `fresh`, `migrated`, `standard`, `split`) from JSON instead of running inline shell.

4. Given the preflight JSON, when the skill file processes Phase 2 (dependencies), then it reads `uv.available`, `tk.path`, `tk.healthy`, `beads.exists`, and `bin_manifests[]` from JSON instead of running inline shell.

5. Given the preflight JSON, when the skill file processes Phases 3-4 (pre-commit, superpowers, tmux, launcher), then it reads the corresponding keys from JSON instead of running inline shell.

6. Given the preflight JSON, when the skill file processes Phase 5 (governance), then it reads `governance.installed` from JSON instead of running inline grep.

7. Given the preflight script, when any individual check fails (e.g., jq not installed, permission error), then the script still completes and reports the failure in the JSON output (partial results, not hard failure).

8. Given the refactored SKILL.md, when counted, then it contains fewer than 10 inline bash blocks (down from 32). The remaining blocks are for actions that mutate state (file writes, installs, symlink creation) --- not for read-only checks.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- The preflight script is read-only --- it checks state but never changes it. All writes (file creation, installs, symlinks) stay in the skill file or in action scripts.
- The JSON schema is noted in the script header so future editors know what each key means.
- The script must run without jq (use Python or pure bash for JSON output) since jq may not be present on first run.
- [SPEC-196]((SPEC-196)-Shell-Level-Marker-Check-for-Init-Fast-Path/(SPEC-196)-Shell-Level-Marker-Check-for-Init-Fast-Path.md) handles the launcher-side shortcut (skip init entirely). This spec handles the init-side cleanup (less inline bash when init does run).
- Phase 0 fast-path (marker check) may move into the launcher per SPEC-196; the preflight script still includes it so init works on its own.

## Implementation Approach

1. Create `swain-init-preflight.sh` with one function per check. Each function adds to a JSON structure. Use Python for JSON output (`python3 -c "import json; ..."`) to skip the jq dependency.
2. Refactor SKILL.md to call the preflight script once at the top, then branch on JSON fields.
3. Move remaining write commands (file writes, installs) into small scripts where they don't already exist.
4. Add tests for the preflight script: fresh project, already-init project, split CLAUDE.md/AGENTS.md state, missing uv, broken tk.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-04 | | Initial creation; operator-requested |
