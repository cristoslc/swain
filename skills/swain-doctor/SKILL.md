---
name: swain-doctor
description: "ALWAYS invoke this skill at the START of every session before doing any other work. Validates project health: governance rules, tool availability, memory directory, settings files, script permissions, .agents directory, and .tickets/ validation. Auto-migrates stale .beads/ directories to .tickets/ and removes them. Remediates issues across all swain skills. Idempotent — safe to run every session."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session-start health checks and repair
  version: 2.4.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

# Doctor

Session-start health checks for swain projects. Validates and repairs health across **all** swain skills — governance, tools, directories, settings, scripts, caches, and runtime state. Auto-migrates stale `.beads/` directories to `.tickets/` and removes them. Idempotent — run it every session; it only writes when repairs are needed.

Run checks in the order listed below. Collect all findings into a summary table at the end.

## Preflight integration

A lightweight shell script (`skills/swain-doctor/scripts/swain-preflight.sh`) performs quick checks before invoking the full doctor. If preflight exits 0, swain-doctor is skipped for the session. If it exits 1, swain-doctor runs normally.

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

   If any file matches, governance is already installed. Proceed to [Legacy skill cleanup](#legacy-skill-cleanup).

3. If no match, run [Legacy skill cleanup](#legacy-skill-cleanup), then proceed to [Governance injection](#governance-injection).

## Legacy skill cleanup

Clean up renamed and retired skill directories using fingerprint checks. Read [references/legacy-cleanup.md](references/legacy-cleanup.md) for the full procedure. Data source: `skills/swain-doctor/references/legacy-skills.json`.

## Platform dotfolder cleanup

Remove dotfolder stubs (`.windsurf/`, `.cursor/`, etc.) for agent platforms that are not installed. Read [references/platform-cleanup.md](references/platform-cleanup.md) for the detection and cleanup procedure. Requires `jq`.

## Governance injection

Inject governance rules into the platform context file when missing. Read [references/governance-injection.md](references/governance-injection.md) for Claude Code and Cursor injection procedures. Source: `skills/swain-doctor/references/AGENTS.content.md`.

## Tickets directory validation

Validates `.tickets/` health — YAML frontmatter, stale locks. **Skip if `.tickets/` does not exist.** Read [references/tickets-validation.md](references/tickets-validation.md) for the full procedure.

## Stale .beads/ migration and cleanup

Auto-migrates `.beads/` → `.tickets/` if present. Skip if `.beads/` does not exist. Read [references/beads-migration.md](references/beads-migration.md) for the migration procedure.

## Governance content reference

The canonical governance rules live in `skills/swain-doctor/references/AGENTS.content.md`. Both swain-doctor and swain-init read from this single source of truth. If the upstream rules change in a future swain release, update that file and bump the skill version. Consumers who want the updated rules can delete the `<!-- swain governance -->` block from their context file and re-run this skill.

## Tool availability

Check required (`git`, `jq`) and optional (`tk`, `uv`, `gh`, `tmux`, `fswatch`) tools. Never install automatically. Read [references/tool-availability.md](references/tool-availability.md) for the check commands, degradation notes, and reporting format.

## Runtime checks

Memory directory, settings validation, script permissions, .agents directory, and status cache bootstrap. Read [references/runtime-checks.md](references/runtime-checks.md) for the full procedures and bash commands.

## tk health (extended .tickets checks)

Verify vendored tk is executable at `skills/swain-do/bin/tk` and check for stale lock files. **Skip if `.tickets/` does not exist.** See [references/tickets-validation.md](references/tickets-validation.md) for details.

## Lifecycle directory migration

Detect old phase directories from before ADR-003's three-track normalization. Old directory names: `Draft/`, `Planned/`, `Review/`, `Approved/`, `Testing/`, `Implemented/`, `Adopted/`, `Deprecated/`, `Archived/`, `Sunset/`, `Validated/`.

### Detection

```bash
OLD_PHASES="Draft Planned Review Approved Testing Implemented Adopted Deprecated Archived Sunset Validated"
for dir in docs/*/; do
  for phase in $OLD_PHASES; do
    if [[ -d "${dir}${phase}" ]]; then
      # Check for non-empty (ignore hidden files)
      if find "${dir}${phase}" -maxdepth 1 -not -name '.*' -print -quit 2>/dev/null | grep -q .; then
        echo "  Old directory: ${dir}${phase}"
      fi
    fi
  done
done
```

### Remediation

1. List each old directory and its artifact count.
2. Explain: "ADR-003 normalized artifact lifecycle phases into three tracks. Old phase directories need migration."
3. Check for the migration script: `skills/swain-design/scripts/migrate-lifecycle-dirs.py`
   - If available: offer to run `uv run python3 skills/swain-design/scripts/migrate-lifecycle-dirs.py --dry-run` first, then the real migration.
   - If unavailable: provide manual `git mv` instructions using the phase mapping from ADR-003.
4. After migration, clean up empty old directories.

### Status values

- **ok** — no old directories found
- **repaired** — migration script ran successfully
- **warning** — old directories found, user chose not to migrate now

## Superpowers detection

Check whether superpowers skills are installed:

```bash
SUPERPOWERS_SKILLS="brainstorming writing-plans test-driven-development verification-before-completion subagent-driven-development executing-plans"
found=0
missing=0
missing_names=""
for skill in $SUPERPOWERS_SKILLS; do
  if ls .agents/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md 2>/dev/null | head -1 | grep -q .; then
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

Enumerate all linked worktrees and classify their health. **Skip if the repo has no linked worktrees** (i.e., `git worktree list --porcelain` returns only the main worktree entry) — this check produces no output in a clean repo.

### Detection

```bash
git worktree list --porcelain
```

Parse each linked worktree (exclude the main worktree — the first entry in the output):

```bash
git worktree list --porcelain | awk '
  /^worktree / { path=$2 }
  /^branch /   { branch=$2 }
  /^$/         { if (path != "") print path, branch; path=""; branch="" }
' | tail -n +2
```

For each linked worktree:

1. **Orphaned** — directory does not exist on disk (`[ ! -d "$path" ]`):
   - WARN: "Orphaned worktree: `<path>` (directory missing). Clean up with: `git worktree prune`"

2. **Stale (merged)** — directory exists and branch is fully merged into `main`:
   ```bash
   git merge-base --is-ancestor "$branch" origin/main
   ```
   - WARN: "Stale worktree: `<path>` (branch `<branch>` already merged into main). Safe to remove:
     `git worktree remove <path> && git branch -d <branch>`"

3. **Active (unmerged)** — directory exists and branch has commits not in `main`:
   - INFO: "Active worktree: `<path>` (branch `<branch>`, N commits ahead of main). Do not remove — work in progress."

Do not remove any worktree automatically. All output is advisory.

### Status values

- **ok** — no linked worktrees, or all are active
- **warning** — one or more stale or orphaned worktrees found (provide cleanup commands per item)

## Summary report

After all checks complete, output a concise summary table:

```
swain-doctor summary:
  Governance ......... ok
  Legacy cleanup ..... ok (nothing to clean)
  Platform dotfolders  ok (nothing to clean)
  .tickets/ .......... ok
  Stale .beads/ ...... ok (not present)
  Tools .............. ok (1 optional missing: fswatch)
  Memory directory ... ok
  Settings ........... ok
  Script permissions . ok
  .agents directory .. ok
  Status cache ....... seeded
  tk health .......... ok
  Worktrees .......... ok
  Superpowers ........ ok (6/6 skills detected)

3 checks performed repairs. 0 issues remain.
```

Use these status values:
- **ok** — nothing to do
- **repaired** — issue found and fixed automatically
- **warning** — issue found, user action recommended (give specifics)
- **skipped** — check could not run (e.g., jq missing for JSON validation)

If any checks have warnings, list them below the table with remediation steps.
