---
name: swain-doctor
description: "Auto-invoked at session start when swain-preflight detects issues. Also user-invocable for on-demand health checks. Validates project health: governance rules, tool availability, memory directory, settings files, script permissions, .agents directory, and .tickets/ validation. Auto-migrates stale .beads/ directories to .tickets/ and removes them. Remediates issues across all swain skills. Idempotent — safe to run any time."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session-start health checks and repair
  version: 2.6.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

# Doctor

Session-start health checks for swain projects. Validates and repairs health across **all** swain skills — governance, tools, directories, settings, scripts, caches, and runtime state. Auto-migrates stale `.beads/` directories to `.tickets/` and removes them. Idempotent — run it every session; it only writes when repairs are needed.

## Consolidated check script (SPEC-192)

**Always run the consolidated script first** — it executes all checks in a single process, eliminating parallel tool-call cascade failures:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-doctor.sh"
```

The script outputs structured JSON with all check results. Parse it and present the summary table to the operator. Then use the individual sections below **only for remediation** of checks that reported `warning` or `advisory` status — do not re-run the detection steps.

If the script is not available (e.g., `.agents/bin/` symlinks not yet bootstrapped), fall back to running the checks below individually. In that case, run them **sequentially** (one Bash call at a time), never in parallel — parallel tool calls cascade-cancel on first error.

## Preflight integration

A lightweight shell script (`$REPO_ROOT/.agents/bin/swain-preflight.sh`) performs quick checks before invoking the full doctor. If preflight exits 0, swain-doctor is skipped for the session. If it exits 1, swain-doctor runs normally.

The preflight checks are a subset of this skill's checks — governance files, .agents directory, .tickets health, script permissions. It runs as pure bash with zero agent tokens. See AGENTS.md § Session startup for the invocation flow.

When invoked directly by the user (not via the auto-invoke flow), swain-doctor always runs regardless of preflight status.

## Session-start governance check

1. Detect the agent platform and locate the context file:

   | Platform | Context file | Detection |
   |----------|-------------|-----------|
   | Claude Code | `CLAUDE.md` (project root) | Default — use if no other platform detected |
   | Cursor | `.cursor/rules/swain-governance.mdc` | `.cursor/` directory exists |

2. Check whether governance rules are already present:

   ```bash
   grep -l "swain governance" CLAUDE.md AGENTS.md .cursor/rules/swain-governance.mdc 2>/dev/null
   ```

   If any file matches, governance is installed. Check freshness (step 3), then proceed to [Legacy skill cleanup](#legacy-skill-cleanup).

3. If governance markers found, check freshness:

   Extract the block between `<!-- swain governance` and `<!-- end swain governance -->` from the installed context file. Compare against the canonical source at `references/AGENTS.content.md` (same extraction, excluding marker lines).

   ```bash
   extract_gov() { awk '/<!-- swain governance/{f=1;next}/<!-- end swain governance/{f=0}f' "$1"; }
   INSTALLED_HASH=$(extract_gov "$GOV_FILE" | shasum -a 256 | cut -d' ' -f1)
   CANONICAL_HASH=$(extract_gov "references/AGENTS.content.md" | shasum -a 256 | cut -d' ' -f1)
   ```

   - **ok** — hashes match. Governance is current. Proceed to [Legacy skill cleanup](#legacy-skill-cleanup).
   - **stale** — hashes differ. Proceed to [Governance replacement](#governance-replacement) before Legacy skill cleanup.

4. If no marker match in step 2 (governance missing), run [Legacy skill cleanup](#legacy-skill-cleanup), then proceed to [Governance injection](#governance-injection).

## Legacy skill cleanup

Clean up renamed and retired skill directories using fingerprint checks. Read [references/legacy-cleanup.md](references/legacy-cleanup.md) for the full procedure. Data source: `references/legacy-skills.json`.

## Platform dotfolder cleanup

Remove dotfolder stubs (`.windsurf/`, `.cursor/`, etc.) for agent platforms that are not installed. Read [references/platform-cleanup.md](references/platform-cleanup.md) for the detection and cleanup procedure. Requires `jq`.

## Governance injection

Inject governance rules into the platform context file when missing. Read [references/governance-injection.md](references/governance-injection.md) for Claude Code and Cursor injection procedures. Source: `references/AGENTS.content.md`.

## Governance replacement

Replace a stale governance block with the current canonical version. Read [references/governance-injection.md § Stale governance replacement](references/governance-injection.md) for the replacement procedure. This runs when freshness check (step 3) detects a hash mismatch.

## Tickets directory validation

Validates `.tickets/` health — YAML frontmatter, stale locks. **Skip if `.tickets/` does not exist.** Read [references/tickets-validation.md](references/tickets-validation.md) for the full procedure.

## Stale .beads/ migration and cleanup

Auto-migrates `.beads/` → `.tickets/` if present. Skip if `.beads/` does not exist. Read [references/beads-migration.md](references/beads-migration.md) for the migration procedure.

## Governance content reference

The canonical governance rules live in `references/AGENTS.content.md`. Both swain-doctor and swain-init read from this single source of truth. If the upstream rules change in a future swain release, update that file and bump the skill version. The freshness check (step 3 of the governance check) will automatically detect the mismatch and offer replacement on the next session.

## Tool availability

Check required (`git`, `jq`) and optional (`tk`, `uv`, `gh`, `tmux`, `fswatch`) tools. Never install automatically. Read [references/tool-availability.md](references/tool-availability.md) for the check commands, degradation notes, and reporting format.

## Skill folder gitignore hygiene

Verify that vendored swain skill directories (`*/skills/swain/`, `*/skills/swain-*/`) are gitignored in consumer projects. Only targets swain-vendored directories — consumer projects' own skills remain tracked. **Skip if the current project is swain itself** (detected via `origin` remote containing `cristoslc/swain`). Read [references/gitignore-skill-folders.md](references/gitignore-skill-folders.md) for self-detection, `git check-ignore` commands, status values, and remediation.

## Runtime checks

Memory directory, settings validation, script permissions, `.agents` directory, status cache bootstrap, and SSH alias readiness. Read [references/runtime-checks.md](references/runtime-checks.md) for the full procedures and bash commands.

## tk health (extended .tickets checks)

Verify vendored tk is executable (at the sibling `swain-do/bin/tk` skill path) and check for stale lock files. **Skip if `.tickets/` does not exist.** See [references/tickets-validation.md](references/tickets-validation.md) for details.

## Operator bin/ symlinks (SPEC-214, ADR-019)

Auto-repair `bin/` symlinks for operator-facing scripts. Scans `skills/*/usr/bin/` manifest directories to discover which scripts need `bin/` symlinks. Each entry in `usr/bin/` is a symlink whose name is the operator command and whose target resolves to the actual script in `scripts/`. Adding a new operator script requires only a new entry in `usr/bin/` — no doctor code changes.

### Behavior

1. Scan `$SKILLS_ROOT/*/usr/bin/` for manifest entries
2. For each entry, ensure `bin/<name>` exists as a symlink resolving to the script
3. Auto-repair missing or stale symlinks; warn on real-file conflicts

### Status values

- **ok** — all symlinks present and correct, or repaired
- **warning** — at least one conflict (real file exists at `bin/<name>`)

## Lifecycle directory migration

Detect old phase directories from before ADR-003's three-track normalization. Read [references/lifecycle-migration.md](references/lifecycle-migration.md) for detection commands, remediation steps, and status values.

## Superpowers detection

Check whether superpowers skills are installed:

```bash
found=0
missing=0
missing_names=""
for skill in brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans; do
  if [ -f ".agents/skills/$skill/SKILL.md" ] || [ -f ".claude/skills/$skill/SKILL.md" ]; then
    found=$((found + 1))
  else
    missing=$((missing + 1))
    missing_names="$missing_names $skill"
  fi
done
```

### Status values and response

- **ok** — all superpowers skills detected. No output.
- **partial** — some skills present, some missing. List the missing ones, then prompt (see below). A partial install may indicate a failed update — note this in the prompt.
- **missing** — no superpowers skills found. Prompt the user.

**When status is `missing` or `partial`**, ask:

> Superpowers (`obra/superpowers`) is not installed [or: partially installed — N of 6 skills missing]. It provides TDD, brainstorming, plan writing, and verification skills that swain chains into during implementation and design work.
>
> Install superpowers now? (yes/no)

If the user says **yes**:
```bash
npx skills add obra/superpowers
```
Report success or failure. On success, update status to **ok**.

If the user says **no**, note "Superpowers: skipped" and continue. They can install later: `npx skills add obra/superpowers`.

Superpowers is strongly recommended but not required. Declining is always allowed.

## Stale worktree detection

Enumerate all linked worktrees and classify their health. **Skip if the repo has no linked worktrees.** Read [references/worktree-detection.md](references/worktree-detection.md) for the detection commands, classification rules, and status values.

## Epics without parent-initiative (migration advisory)

This is a non-blocking advisory check. It does not gate any other checks.

### Detection

```bash
# Find Active EPICs that have a parent-vision but no parent-initiative field
grep -rl "parent-vision:" docs/epic/ 2>/dev/null | while read f; do
  if ! grep -q "parent-initiative:" "$f"; then
    echo "$f"
  fi
done
```

### Response

If any EPICs are found without `parent-initiative`:

> **Advisory:** N Epic(s) have a `parent-vision` but no `parent-initiative`. The INITIATIVE artifact type is now available as a mid-level container between Vision and Epic. Adding `parent-initiative` links is optional but recommended for projects using prioritization features (`specgraph recommend`, `specgraph decision-debt`).
>
> To add the link, edit each Epic's frontmatter and add:
> ```yaml
> parent-initiative: INITIATIVE-NNN
> ```
>
> This check is informational — no action required. To run the guided migration, ask: "how do I fix the initiative migration?" or "run the initiative migration".

### Guided migration workflow

Read [references/initiative-migration.md](references/initiative-migration.md) for the full 6-step guided migration workflow (scan, cluster, create initiatives, re-parent, set weights, verify).

### Status values

- **ok** — all Active EPICs already have `parent-initiative`, or no EPICs exist
- **advisory** — one or more Active EPICs lack `parent-initiative` (non-blocking)

## README existence check

Verify that `README.md` exists at the repo root. The README is the most public statement of project intent and serves as an ambient input to swain's alignment loop. A missing README means the alignment loop has no public intent anchor.

### Detection

```bash
[ -f "README.md" ] && echo "ok" || echo "missing"
```

### Status values and response

- **ok** — README.md exists. Silent.
- **warning** — README.md missing. Report: `README.md missing — swain alignment loop has no public intent anchor. Run swain-init to seed one.`

This is an existence check only — no content analysis. Content reconciliation is handled by swain-session (session start), swain-retro (retrospective), and swain-release (release gate).

## Evidence Pool → Trove Migration

Detect unmigrated evidence pools:
- If `docs/evidence-pools/` exists: warn and offer to run migration
- If any artifact frontmatter contains `evidence-pool:`: warn and offer migration
- If both `docs/troves/` and `docs/evidence-pools/` exist: warn about incomplete migration

Migration script: `bash "$REPO_ROOT/.agents/bin/migrate-to-troves.sh"`
Dry run first: `bash "$REPO_ROOT/.agents/bin/migrate-to-troves.sh" --dry-run`

## Summary report

After all checks complete, output a concise summary table:

```
swain-doctor summary:
  Governance ......... ok
  Legacy cleanup ..... ok (nothing to clean)
  Platform dotfolders  ok (nothing to clean)
  .tickets/ .......... ok
  Stale .beads/ ...... ok (not present)
  Skill gitignore .... ok
  Tools .............. ok (1 optional missing: fswatch)
  Memory directory ... ok
  Settings ........... ok
  Script permissions . ok
  .agents directory .. ok
  Status cache ....... seeded
  tk health .......... ok
  Lifecycle dirs ..... ok
  Epics w/o initiative advisory (3 epics — see note below)
  Worktrees .......... ok
  README ............. ok
  Superpowers ........ ok (6/6 skills detected)

3 checks performed repairs. 0 issues remain.
```

Use these status values:
- **ok** — nothing to do
- **repaired** — issue found and fixed automatically
- **warning** — issue found, user action recommended (give specifics)
- **skipped** — check could not run (e.g., jq missing for JSON validation)

If any checks have warnings, list them below the table with remediation steps.
