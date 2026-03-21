# Retro: EPIC-031 Skill Audit Remediation

**Date:** 2026-03-21
**Scope:** EPIC-031 — Skill Audit Remediation (all 9 child specs + SPIKE-033 + DESIGN-003)
**Period:** 2026-03-18 (audit) — 2026-03-21 (completion)
**Terminal state:** Complete

## Changes Made

### Commit `902fc0d` — Universal find-based script discovery (SPEC-072)

Converted hardcoded `$REPO_ROOT/skills/...` paths to `find`-based discovery in 8 SKILL.md files. The core problem: `git rev-parse --show-toplevel` returns the worktree root in a linked worktree, not the main repo root where skills live. Every `$REPO_ROOT/skills/swain-foo/scripts/bar.sh` silently failed in worktrees.

**Files changed:** swain-doctor, swain-status, swain-security-check, swain-session, swain-do, swain-stage, swain-sync, swain-retro SKILL.md files (44 insertions, 40 deletions).

**Pattern applied:**
```bash
# Before
bash "$REPO_ROOT/skills/swain-status/scripts/swain-status.sh"

# After
SCRIPT="$(find "$REPO_ROOT" -path '*/swain-status/scripts/swain-status.sh' -print -quit 2>/dev/null)"
bash "$SCRIPT"
```

### Commit `38fa2c5` — Progressive disclosure cleanup (SPEC-079)

Extracted 3 large procedural sections from swain-doctor SKILL.md into reference files, reducing it from 406 to 266 lines (target was <350).

**New files created:**
- `skills/swain-doctor/references/lifecycle-migration.md` (34 lines) — lifecycle phase migration detection and repair
- `skills/swain-doctor/references/worktree-detection.md` (41 lines) — awk-based worktree state detection
- `skills/swain-doctor/references/initiative-migration.md` (74 lines) — epic-to-initiative parent guided migration

Each section replaced with a one-line pointer: `Read [references/X.md] for Y.`

### Commit `9062633` — SPIKE-033 routing disambiguation findings

Investigated the audit's concern about overlapping skill trigger phrases. Found the problem narrower than expected — Claude Code's description-based routing plus SPEC-073's enrichment handle most cases. Added a single disambiguation hint to the swain meta-router (2 lines):

> When intent includes an artifact type name alongside a question word, prefer swain-design over swain-help.

**Recommendation: No-Go** on a full disambiguation framework.

### Commit `e7590e7` — EPIC-031 lifecycle table updated to Complete

### Specs verified as already complete (7 of 9)

The agent found that 7 of 9 specs were already implemented by prior work:

| Spec | What was already done | When |
|------|----------------------|------|
| SPEC-080 | swain-push directories already deleted, no references remain | Pre-audit |
| SPEC-074 | swain-dispatch already has `repository_dispatch` trigger and unquoted heredoc | Prior fix |
| SPEC-075 | swain-sync already has Write/Glob in allowed-tools, correct worktree pruning | Prior fix |
| SPEC-076 | swain-update already uses find-based discovery, detects install location | Prior fix |
| SPEC-073 | All 18 skills already have 50-150 word descriptions with 3+ trigger phrases | Audit enrichment pass |
| SPEC-077 | AskUserQuestion, ExitWorktree, Skill already in correct allowed-tools | Prior fix |
| SPEC-078 | Status cache already at `.agents/status-cache.json` with migration fallback | Prior migration |

## Reflection

### What went well

**Audit-driven decomposition.** Grouping by cross-cutting theme (paths, descriptions, tools, state, disclosure) rather than per-skill was the right call. SPEC-072 alone touched 8 skills — a per-skill decomposition would have created 8+ overlapping specs instead of one focused one.

**Pre-implementation detection worked.** The agent correctly identified 7 specs as already complete and didn't waste time re-implementing them. It verified each against acceptance criteria before closing. This validates the swain-do retroactive-close workflow.

**SPIKE-033 delivered a clear No-Go.** The research was structured (overlap map, internals analysis, candidate evaluation) and arrived at a concrete recommendation with one actionable enhancement instead of analysis paralysis.

### What was surprising

**78% of the audit specs were already done.** The 2026-03-18 audit identified issues that had already been fixed in the interval between audit creation and EPIC execution. This suggests the audit was either slightly stale or the normal development cadence was already addressing these issues organically.

**swain-doctor was 406 lines.** It had accumulated procedural blocks that no agent at runtime ever needs — migration scripts, awk blocks, initiative repair logic. The 266-line result is materially more readable and the references are still accessible when needed.

### What would change

**Run the audit against HEAD, not a snapshot.** The audit was written on 2026-03-18 and the EPIC was executed on 2026-03-21. Three days of active development meant 7 of 9 specs were stale by execution time. A pre-execution verification step (or a staler-than-N-days warning in swain-do) would have flagged this earlier and saved the agent from verifying each one.

**skill-creator evals need a non-interactive mode fix.** The automated eval harness (`scripts.run_eval`) uses `claude -p` which doesn't trigger skills in headless mode — all should-trigger queries returned 0%. This is a systematic limitation, not a description quality issue. The eval framework needs a different approach for skill trigger testing (possibly direct description-matching rather than end-to-end invocation).

### Patterns observed

**Audit-to-execution gap is a recurring theme.** This is the same pattern seen in SPIKE-022 -> SPEC-114 (spike findings not back-propagated). Design artifacts describe a state of the world that may have changed by the time implementation begins. The pre-implementation detection in swain-do is the right mitigation — it's doing its job here.

**Progressive disclosure pays off every time.** Every time large procedural blocks are extracted to references, the resulting SKILL.md is materially better. This should be a standing practice during skill development, not just an audit remediation.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| (no new memories) | -- | Learnings are structural: pre-implementation detection validated (already in swain-do), progressive disclosure reinforced (already a practice). skill-creator eval limitation is a bug, not a memory — filed implicitly via the retro. |
