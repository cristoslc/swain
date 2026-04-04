---
title: "Retro: SPEC-257 swain-init preflight consolidation"
artifact: RETRO-2026-04-04-spec-257-init-preflight
track: standing
status: Active
created: 2026-04-04
last-updated: 2026-04-04
scope: "SPEC-257 implementation — extracting inline bash from swain-init into a preflight script"
period: "2026-04-04"
linked-artifacts:
  - SPEC-257
  - EPIC-048
---

# Retro: SPEC-257 swain-init preflight consolidation

## Summary

Extracted 32 inline bash check blocks from `swain-init/SKILL.md` into a single `swain-init-preflight.sh` script that emits JSON. Refactored the skill file to consume that JSON for decisions, keeping only 8 mutation blocks. Test suite covers 9 scenarios with 38 assertions.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-257 | Consolidate swain-init inline bash into preflight script | Implemented |

## Reflection

### What went well

The existing skill infrastructure made this smooth. The `scripts/` directory convention, the `.agents/bin/` bootstrap symlink loop, and the `test-*` prefix skip pattern meant no plumbing work was needed — just drop the script in the right place and it wires up automatically. Tests passed on the first run.

### What was surprising

The `.claude/skills/` directory is npm-installed and gitignored, so worktrees don't contain it. The preflight script uses `find` across `.`, `.claude`, and `.agents` to locate `SKILL.md` for version detection. This is a known pattern but easy to forget when writing new scripts that need to resolve skill paths.

### What would change

The python3 JSON serialization passes 29 positional arguments from shell variables. Adding a new check means updating both the shell function and the python3 argument index — a sync point that will eventually cause a bug. A cleaner approach: write each check's result to a temp file as a JSON fragment, then merge them at the end. Or use an associative-array-to-JSON pattern.

### Patterns observed

This is the same refactoring pattern as `swain-session-greeting.sh` — extract read-only checks from a skill file into a script, have the LLM operate on structured JSON instead of running shell inline. This pattern is proving effective for reducing token overhead and making checks testable. It could become a standard approach for all skill files with heavy inline bash.

## SPEC candidates

1. **Standardize skill-to-script extraction pattern** — codify the "preflight script emits JSON, skill file consumes JSON" pattern as a convention in ADR or DESIGN form. This would guide future skill authors and prevent ad-hoc approaches.

2. **Harden preflight arg-passing with temp-file merge** — replace the 29-positional-arg python3 call in `swain-init-preflight.sh` with per-check JSON fragments merged at the end. Eliminates the fragile index-sync requirement.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Skill-to-script extraction pattern | Pattern observation | Extract read-only checks to script, emit JSON, skill consumes JSON — proven in session-greeting and now init-preflight |
| Positional arg fragility | SPEC candidate | 29-arg python3 call will break when checks are added; temp-file merge is safer |
| Worktree skill path resolution | Pattern observation | Scripts must `find` across multiple roots because `.claude/skills/` is gitignored |
