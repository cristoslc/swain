---
title: "Doctor Single-Script Consolidation"
artifact: SPIKE-049
track: container
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
question: "Can swain-doctor's initial diagnostics be consolidated into a single deterministic shell script invocation, eliminating the current pattern of many LLM-generated bash commands?"
gate: Pre-MVP
parent-initiative: INITIATIVE-003
risks-addressed:
  - Token waste on deterministic diagnostic work
  - Session startup latency from sequential LLM tool calls
  - Non-reproducibility of LLM-driven diagnostic sequencing
---

# Doctor Single-Script Consolidation

## Summary

<!-- Final-pass section: populated when transitioning to Complete. -->

## Question

Can swain-doctor's initial diagnostics be consolidated into a single deterministic shell script invocation, eliminating the current pattern of many LLM-generated bash commands?

Today swain-doctor runs as a skill that instructs the LLM to execute 15+ sequential bash commands — governance hash comparison, tool availability, directory checks, script permissions, SSH readiness, worktree enumeration, etc. Each command is a separate tool call, consuming tokens and adding latency. The existing `swain-preflight.sh` already demonstrates the pattern: pure bash, zero agent tokens, structured exit codes.

The question is how far we can push this. Can we build a single `swain-doctor.sh` that runs ALL checks and emits structured JSON, so the LLM only needs to:
1. Run one script
2. Parse the JSON output
3. Handle any items that need user interaction (prompts, confirmations)

## Go / No-Go Criteria

- **Go**: A single script can perform ≥80% of current doctor checks deterministically, emitting structured JSON that the LLM can act on. Remaining checks that require LLM judgment (e.g., "should we install superpowers?") are clearly separated as interactive items in the output.
- **No-Go**: More than 30% of checks require LLM judgment or dynamic decision-making that can't be pre-scripted (e.g., complex repair strategies that vary by context).

## Pivot Recommendation

If full consolidation isn't feasible, adopt a two-tier model: a "diagnostic tier" script that collects all state into JSON (single tool call), followed by a "remediation tier" where the LLM processes only the items that need interaction. This still halves the tool calls.

## Findings

### Current state analysis

The current doctor skill (`swain-doctor/SKILL.md`) defines these check categories:

| Check | Deterministic? | Needs LLM? | Notes |
|-------|---------------|------------|-------|
| Governance hash comparison | Yes | No | Pure sha256 comparison |
| Legacy skill cleanup | Yes | No | Fingerprint matching against JSON |
| Platform dotfolder cleanup | Yes | No | Directory existence + jq |
| .tickets/ validation | Yes | No | YAML frontmatter + lock check |
| .beads/ migration | Yes | No | Directory rename |
| Tool availability | Yes | No | `command -v` checks |
| Script permissions | Yes | Repair only | `chmod +x` is deterministic |
| .agents directory | Yes | No | mkdir -p |
| Status cache bootstrap | Yes | No | File existence check |
| SSH alias readiness | Yes | Repair only | Already has `--repair` flag |
| tk health | Yes | No | Binary check + lock scan |
| swain-box symlink | Yes | Repair only | ln -sf |
| Lifecycle dir migration | Yes | No | Directory scan |
| Worktree detection | Yes | No | `git worktree list` parsing |
| Epics w/o initiative | Yes | No (advisory) | grep scan |
| Evidence pool migration | Yes | No (advisory) | Directory existence |
| Superpowers detection | Detect: Yes | Install prompt: Yes | `npx skills add` needs confirmation |
| Governance injection/replacement | Detect: Yes | Confirm: Maybe | Could auto-repair if stale |

**Key observation:** ~90% of checks are fully deterministic. Only superpowers installation and possibly governance injection genuinely need user interaction.

### Investigation threads

1. **Audit `swain-preflight.sh`** — what pattern does it establish? How much of doctor does it already cover?
2. **Design the JSON output schema** — what structure lets the LLM handle interactive items with minimal parsing?
3. **Identify repair actions that can be auto-applied** — SSH repair, symlink creation, permission fixes are all safe to auto-apply. Which ones need confirmation?
4. **Measure token savings** — compare current doctor session (tool calls, tokens) vs. single-script approach.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation |
