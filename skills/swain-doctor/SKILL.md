---
name: swain-doctor
description: "Auto-invoked at session start when swain-preflight detects issues. Also user-invocable for on-demand health checks. Validates project health: governance rules, tool availability, memory directory, settings files, script permissions, .agents directory, and .tickets/ validation. Auto-migrates stale .beads/ directories to .tickets/ and removes them. Remediates issues across all swain skills. Idempotent — safe to run any time."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session-start health checks and repair
  version: 3.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: low -->

# Doctor

Session-start health checks for swain projects. The consolidated script is authoritative for all detection. This skill file defines how to run the script and how to remediate each check.

## Running the script

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-doctor.sh"
```

The script outputs structured JSON with `{ checks: [...], summary: {...} }`. Each check has `name`, `status`, `message`, and optional `detail`. Parse it and present the summary table to the operator. Then use the remediation sections below **only for checks that reported `warning` or `advisory` status** — do not re-run detection.

To auto-fix flat-file artifacts: `bash "$REPO_ROOT/.agents/bin/swain-doctor.sh" --fix-flat-artifacts`

If the script is unavailable (e.g., `.agents/bin/` symlinks not yet bootstrapped), fall back to running checks from the script source at `skills/swain-doctor/scripts/swain-doctor.sh`. Run checks **sequentially** (one Bash call at a time), never in parallel — parallel tool calls cascade-cancel on first error.

## Preflight integration

A lightweight shell script (`$REPO_ROOT/.agents/bin/swain-preflight.sh`) performs quick checks before invoking the full doctor. If preflight exits 0, swain-doctor is skipped for the session. If it exits 1, swain-doctor runs normally.

When invoked directly by the user (not via auto-invoke), swain-doctor always runs regardless of preflight status.

## Governance content reference

The canonical governance rules live in `references/AGENTS.content.md`. Both swain-doctor and swain-init read from this single source of truth. If the upstream rules change in a future swain release, update that file and bump the skill version.

---

# Remediation by check name

Each section below corresponds to a check name emitted by the script. Only consult the relevant section when the check status is `warning` or `advisory`.

## governance

**Injection (missing):** Read [references/governance-injection.md](references/governance-injection.md) for Claude Code and Cursor injection procedures. Source: `references/AGENTS.content.md`.

**Replacement (stale):** The script auto-repairs stale governance blocks when both markers (`<!-- swain governance -->` and `<!-- end swain governance -->`) are present. If auto-repair fails (markers missing), read [references/governance-injection.md § Stale governance replacement](references/governance-injection.md) for manual replacement.

## legacy_skills

Clean up renamed and retired skill directories using fingerprint checks. Read [references/legacy-cleanup.md](references/legacy-cleanup.md) for the full procedure. Data source: `references/legacy-skills.json`.

## agents_directory

Create `.agents/` with `mkdir -p .agents`. This directory is used by swain-do for configuration and by swain-design scripts for logs.

## tickets

Validates `.tickets/` health — YAML frontmatter, stale locks. Read [references/tickets-validation.md](references/tickets-validation.md) for repair procedures.

## beads_migration

Auto-migrates `.beads/` → `.tickets/` if present. Read [references/beads-migration.md](references/beads-migration.md) for the migration procedure.

## tools

Required tools: `git`, `jq`. Optional: `tk`, `uv`, `gh`, `tmux`, `fswatch`. Never install automatically. Read [references/tool-availability.md](references/tool-availability.md) for degradation notes and install instructions.

## settings

If `swain.settings.json` is missing, create it with default content. If it contains invalid JSON, fix the syntax. User settings live at `${XDG_CONFIG_HOME:-$HOME/.config}/swain/settings.json`.

## script_permissions

The script auto-repairs missing execute permissions on `.sh` and `.py` files in the skill tree. No manual remediation needed — advisory status means it already fixed them.

## memory_directory

The script auto-creates the memory directory if missing. If creation fails, manually create:
```bash
mkdir -p "$HOME/.claude/projects/$(echo "$REPO_ROOT" | tr '/' '-')/memory"
```

## superpowers

When status is `warning` (missing or partial), ask the operator:

> Superpowers (`obra/superpowers`) is not installed [or: partially installed]. It provides TDD, brainstorming, plan writing, and verification skills that swain chains into.
>
> Install superpowers now? (yes/no)

If yes: `npx skills add obra/superpowers`. If no, note "Superpowers: skipped" and continue.

## epics_initiative

Non-blocking advisory. Report the count and suggest:

> N Epic(s) have `parent-vision` but no `parent-initiative`. Adding `parent-initiative` links is optional but recommended. To run the guided migration, ask: "run the initiative migration."

Read [references/initiative-migration.md](references/initiative-migration.md) for the full 6-step guided migration workflow.

## readme

Report: `README.md missing — swain alignment loop has no public intent anchor. Run swain-init to seed one.`

## artifact_indexes

The script auto-repairs stale indexes via `rebuild-index.sh`. If the rebuild script is unavailable or a rebuild fails, check that `.agents/bin/rebuild-index.sh` exists and is executable. Re-run `swain-doctor` after fixing the symlink.

## evidence_pools

If `docs/evidence-pools/` exists, run the trove migration:
```bash
bash "$REPO_ROOT/.agents/bin/migrate-to-troves.sh" --dry-run  # preview
bash "$REPO_ROOT/.agents/bin/migrate-to-troves.sh"            # migrate
```

## worktrees

Stale worktrees (branch already merged into HEAD) can be pruned: `git worktree remove <path>`. Orphaned worktrees (directory missing) can be pruned: `git worktree prune`. Stale lockfiles and unclaimed worktrees are reported in the detail field. Read [references/worktree-detection.md](references/worktree-detection.md) for classification rules.

## lifecycle_dirs

Old phase directories from before ADR-003's three-track normalization. Read [references/lifecycle-migration.md](references/lifecycle-migration.md) for detection commands, remediation steps, and the migration script.

## tk_health

If vendored tk is not found or not executable, try: `/swain update` to reinstall skills. The expected path is `<skills-root>/swain-do/bin/tk`.

## operator_bin_symlinks

The script auto-repairs missing or stale `bin/` symlinks. Conflicts (real file exists at `bin/<name>`) require manual resolution — rename or remove the conflicting file, then re-run doctor.

## commit_signing

The script auto-enables commit signing when a signing key is detected at `~/.ssh/swain_signing`. If no key exists, run `/swain-keys` to provision one.

## ssh_readiness

Runs `scripts/ssh-readiness.sh --check`. Issues are reported in the detail field. Common fixes: verify `~/.ssh/config.d/` includes the project-specific SSH alias, check key permissions (`chmod 600`), ensure the key is added to the remote host.

## crash_debris

The script auto-removes stale `.git/index.lock` files. Other crash debris (orphaned temp files, partial merges) is reported for manual cleanup. Review the detail field for specific file paths and remove them if safe.

## agents_bin_symlinks

The script auto-repairs missing and stale `.agents/bin/` symlinks. Broken symlinks are removed. Conflicts (real files) are reported for manual resolution.

## flat_artifacts

Flat-file artifacts sit directly in phase directories instead of their own folders. Run with `--fix-flat-artifacts` to auto-migrate: `bash "$REPO_ROOT/.agents/bin/swain-doctor.sh" --fix-flat-artifacts`. Each artifact gets a folder named `(<ID>)-<Title>/`.

## swain_symlink

If `bin/swain` symlink is missing but the script exists at `<skills-root>/swain/scripts/swain`, create it:
```bash
ln -sf "$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$SKILLS_ROOT/swain/scripts/swain" "$REPO_ROOT/bin")" "$REPO_ROOT/bin/swain"
```
If the symlink is broken (target missing), the swain skill may need reinstalling: `/swain update`.

## branch_model

Advisory — swain recommends a trunk+release branch model (ADR-013). `trunk` is the development branch; `release` is the distribution branch updated via squash-merge at release time. To adopt it, run `.agents/bin/migrate-to-trunk-release.sh` (or `--dry-run` to preview). This is optional — swain works with any branch model, but sync and release features assume trunk+release when configured.

## platform_dotfolders

Remove dotfolder stubs for uninstalled agent platforms. Read [references/platform-cleanup.md](references/platform-cleanup.md) for the detection and cleanup procedure. Requires `jq`. The script reports which dotfolders are orphaned — verify they contain only installer symlinks before removing.

## skill_gitignore

Vendored swain skill folders should be gitignored in consumer projects. Read [references/gitignore-skill-folders.md](references/gitignore-skill-folders.md) for the remediation procedure. Append these entries to `.gitignore`:
```
.claude/skills/swain/
.claude/skills/swain-*/
.agents/skills/swain/
.agents/skills/swain-*/
```

Skipped automatically when running in the swain source repo.

---

## Summary report

After all checks complete, output a concise summary table:

```
swain-doctor summary:
  Governance ......... ok
  Legacy cleanup ..... ok (nothing to clean)
  Platform dotfolders  ok (nothing to clean)
  .agents directory .. ok
  .tickets/ .......... ok
  Stale .beads/ ...... ok (not present)
  Tools .............. ok (1 optional missing: fswatch)
  Settings ........... ok
  Script perms ....... ok
  Memory directory ... ok
  Superpowers ........ ok (6/6 skills detected)
  Epics w/o initiative advisory (3 epics — see note below)
  README ............. ok
  Artifact indexes ... ok
  Evidence pools ..... ok
  Worktrees .......... ok
  Lifecycle dirs ..... ok
  tk health .......... ok
  Operator bin/ ...... ok
  Commit signing ..... ok
  SSH readiness ...... ok
  Crash debris ....... ok
  .agents/bin/ ....... ok
  Flat artifacts ..... ok
  swain symlink ...... ok
  Branch model ....... ok
  Skill gitignore .... ok

3 checks performed repairs. 0 issues remain.
```

Use these status values:
- **ok** — nothing to do.
- **advisory** — auto-repaired or informational (give specifics).
- **warning** — issue found, user action recommended (give specifics).
- **skipped** — check could not run (e.g., jq missing for JSON validation).

If any checks have warnings, list them below the table with remediation steps from the sections above.
