---
name: swain-init
description: "One-time project onboarding for swain. Migrates existing CLAUDE.md content to AGENTS.md (with the @AGENTS.md include pattern), verifies vendored tk (ticket) for task tracking, configures pre-commit security hooks (gitleaks default), and offers to add swain governance rules. Run once when adopting swain in a new project — use swain-doctor for ongoing per-session health checks."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion
metadata:
  short-description: One-time swain project onboarding
  version: 3.1.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Project Onboarding

One-time setup for adopting swain in a project. This skill is **not idempotent** — it migrates files and installs tools. For per-session health checks, use swain-doctor.

Run all phases in order. If a phase detects its work is already done, skip it and move to the next.

## Phase 1: CLAUDE.md → AGENTS.md migration

Goal: establish the `@AGENTS.md` include pattern so project instructions live in AGENTS.md (which works across Claude Code, GitHub, and other tools that read AGENTS.md natively).

### Step 1.1 — Survey existing files

```bash
cat CLAUDE.md 2>/dev/null; echo "---SEPARATOR---"; cat AGENTS.md 2>/dev/null
```

Classify the current state:

| CLAUDE.md | AGENTS.md | State |
|-----------|-----------|-------|
| Missing or empty | Missing or empty | **Fresh** — no migration needed |
| Contains only `@AGENTS.md` | Any | **Already migrated** — skip to Phase 2 |
| Has real content | Missing or empty | **Standard** — migrate CLAUDE.md → AGENTS.md |
| Has real content | Has real content | **Split** — needs merge (ask user) |

### Step 1.2 — Migrate

**Fresh state:** Create both files.

```
# CLAUDE.md
@AGENTS.md
```

```
# AGENTS.md
(empty — governance will be added in Phase 3)
```

**Already migrated:** Skip to Phase 2.

**Standard state:**

1. Copy CLAUDE.md content to AGENTS.md (preserve everything).
2. If CLAUDE.md contains a `<!-- swain governance -->` block, strip it from the AGENTS.md copy — it will be re-added cleanly in Phase 3.
3. Replace CLAUDE.md with:

```
@AGENTS.md
```

Tell the user:
> Migrated your CLAUDE.md content to AGENTS.md and replaced CLAUDE.md with `@AGENTS.md`. Your existing instructions are preserved — Claude Code reads AGENTS.md via the include directive.

**Split state:** Both files have content. Ask the user:

> Both CLAUDE.md and AGENTS.md have content. How should I proceed?
> 1. **Merge** — append CLAUDE.md content to the end of AGENTS.md, then replace CLAUDE.md with `@AGENTS.md`
> 2. **Keep AGENTS.md** — discard CLAUDE.md content, replace CLAUDE.md with `@AGENTS.md`
> 3. **Abort** — leave both files as-is, skip migration

If merge: append CLAUDE.md content (minus any `<!-- swain governance -->` block) to AGENTS.md, replace CLAUDE.md with `@AGENTS.md`.

## Phase 2: Verify dependencies

Goal: ensure uv is available and the vendored tk script is accessible.

### Step 2.1 — Check uv availability

```bash
command -v uv
```

If uv is found, skip to Step 2.2.

If missing, install:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If installation fails, tell the user:
> uv installation failed. You can install it manually (https://docs.astral.sh/uv/getting-started/installation/) — swain scripts require uv for Python execution.

Then skip the rest of Phase 2 (don't block init on uv, but warn that scripts will not function without it).

### Step 2.2 — Verify vendored tk

tk (ticket) is vendored in the swain skill tree — no external installation is needed.

```bash
TK_PATH="$(find . .claude .agents -path '*/swain-do/bin/tk' -print -quit 2>/dev/null)"
test -x "$TK_PATH" && echo "tk found at $TK_PATH" || echo "tk not found"
```

If found, verify it runs:

```bash
"$TK_PATH" help >/dev/null 2>&1 && echo "tk works" || echo "tk broken"
```

If tk is not found or broken, tell the user:
> The vendored tk script was not found at `skills/swain-do/bin/tk`. This usually means the swain-do skill was not fully installed. Try running `/swain update` to reinstall skills.

### Step 2.3 — Migrate from beads (if applicable)

Check if this project has existing beads data:

```bash
test -d .beads && echo "beads found" || echo "no beads"
```

If `.beads/` exists:

1. Check for backup data: `ls .beads/backup/issues.jsonl 2>/dev/null`
2. If backup exists, offer migration:
   > Found existing `.beads/` data. Migrate tasks to tk?
   > This will convert `.beads/backup/issues.jsonl` to `.tickets/` markdown files.
3. If user agrees, run migration:
   ```bash
   TK_BIN="$(cd "$(dirname "$TK_PATH")" && pwd)"
   export PATH="$TK_BIN:$PATH"
   cp .beads/backup/issues.jsonl .beads/issues.jsonl 2>/dev/null  # migrate-beads expects this location
   ticket-migrate-beads
   ```
4. Verify: `ls .tickets/*.md 2>/dev/null | wc -l`
5. Tell the user the results and that `.beads/` can be removed after verification.

If `.beads/` does not exist, skip this step. tk creates `.tickets/` on first `tk create`.

## Phase 3: Pre-commit security hooks

Goal: configure pre-commit hooks for secret scanning so credentials are caught before they enter git history. Default scanner is gitleaks; additional scanners (TruffleHog, Trivy, OSV-Scanner) are opt-in.

### Step 3.1 — Check for existing `.pre-commit-config.yaml`

```bash
test -f .pre-commit-config.yaml && echo "exists" || echo "missing"
```

**If exists:** Present the current config and ask:

> Found existing `.pre-commit-config.yaml`. How should I proceed?
> 1. **Merge** — add swain's gitleaks hook alongside your existing hooks
> 2. **Skip** — leave pre-commit config unchanged
> 3. **Replace** — overwrite with swain's default config (your existing hooks will be lost)

If user chooses Skip, skip to Phase 4.

**If missing:** Proceed to Step 3.2.

### Step 3.2 — Check pre-commit framework

```bash
command -v pre-commit && pre-commit --version
```

If `pre-commit` is not found, install it:

```bash
uv tool install pre-commit
```

If uv is unavailable or installation fails, warn:
> pre-commit framework not available. You can install it manually (`uv tool install pre-commit` or `pip install pre-commit`). Skipping hook setup.

Skip to Phase 4 if pre-commit cannot be installed.

### Step 3.3 — Create or update `.pre-commit-config.yaml`

The default config enables gitleaks:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

If the user requested additional scanners (via `--scanner` flags or when asked), add their hooks:

**TruffleHog (opt-in):**
```yaml
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.88.1
    hooks:
      - id: trufflehog
        args: ['--results=verified,unknown']
```

**Trivy (opt-in):**
```yaml
  - repo: https://github.com/cebidhem/pre-commit-trivy
    rev: v1.0.0
    hooks:
      - id: trivy-fs
        args: ['--severity', 'HIGH,CRITICAL', '--scanners', 'vuln,license']
```

**OSV-Scanner (opt-in):**
```yaml
  - repo: https://github.com/nicjohnson145/pre-commit-osv-scanner
    rev: v0.0.1
    hooks:
      - id: osv-scanner
```

Write the config file. If merging with an existing config, append the new repo entries to the existing `repos:` list.

### Step 3.4 — Install hooks

```bash
pre-commit install
```

### Step 3.5 — Update swain.settings.json

Read the existing `swain.settings.json` (if any) and add the `sync.scanners` key:

```json
{
  "sync": {
    "scanners": {
      "gitleaks": { "enabled": true },
      "trufflehog": { "enabled": false },
      "trivy": { "enabled": false, "scanners": ["vuln", "license"], "severity": "HIGH,CRITICAL" },
      "osv-scanner": { "enabled": false }
    }
  }
}
```

Set `enabled: true` for any scanners the user opted into. Merge with existing settings — do not overwrite other keys.

Tell the user:
> Pre-commit hooks configured with gitleaks (default). Scanner settings saved to `swain.settings.json`. To enable additional scanners later, edit `swain.settings.json` and re-run `/swain-init`.

## Phase 4: Superpowers companion

Goal: offer to install `obra/superpowers` if it is not already present. Superpowers provides TDD enforcement, brainstorming, plan writing, and verification skills that swain chains into — the full AGENTS.md workflow depends on them being installed.

### Step 4.1 — Detect superpowers

```bash
ls .agents/skills/brainstorming/SKILL.md .claude/skills/brainstorming/SKILL.md 2>/dev/null | head -1
```

If any result is returned, superpowers is already installed. Report "Superpowers: already installed" and skip to Phase 5.

### Step 4.2 — Offer installation

Ask the user:

> Superpowers (`obra/superpowers`) is not installed. It provides TDD, brainstorming, plan writing, and verification skills that swain chains into during implementation and design work.
>
> Install superpowers now? (yes/no)

If the user says **no**, note "Superpowers: skipped" and continue to Phase 5. They can always install later: `npx skills add obra/superpowers`.

### Step 4.3 — Install

```bash
npx skills add obra/superpowers
```

If the install succeeds, tell the user:
> Superpowers installed. Brainstorming, TDD, plan writing, and verification skills are now available.

If it fails, warn:
> Superpowers installation failed. You can retry manually: `npx skills add obra/superpowers`

Continue to Phase 5 regardless.

## Phase 5: Swain governance

Goal: add swain's routing and governance rules to AGENTS.md.

### Step 5.1 — Check for existing governance

```bash
grep -l "swain governance" AGENTS.md CLAUDE.md 2>/dev/null
```

If found in either file, governance is already installed. Tell the user and skip to Phase 6.

### Step 5.2 — Ask permission

Ask the user:

> Ready to add swain governance rules to AGENTS.md. These rules:
> - Route artifact requests (specs, stories, ADRs, etc.) to swain-design
> - Route task tracking to swain-do (using tk)
> - Enforce the pre-implementation protocol (plan before code)
> - Prefer swain skills over built-in alternatives
>
> Add governance rules to AGENTS.md? (yes/no)

If no, skip to Phase 6.

### Step 5.3 — Inject governance

Read the canonical governance content from `skills/swain-doctor/references/AGENTS.content.md`. Locate it by searching for the file relative to the installed skills directory:

```bash
find .claude/skills .agents/skills skills -path '*/swain-doctor/references/AGENTS.content.md' -print -quit 2>/dev/null
```

Append the full contents of that file to AGENTS.md.

Tell the user:
> Governance rules added to AGENTS.md. These ensure swain skills are routable and conventions are enforced. You can customize anything outside the `<!-- swain governance -->` markers.

## Phase 6: Finalize

### Step 6.1 — Create .agents directory

```bash
mkdir -p .agents
```

This directory is used by swain-do for configuration and by swain-design scripts for logs.

### Step 6.2 — Run swain-doctor

Invoke the **swain-doctor** skill. This validates `.tickets/` health, checks stale locks, removes legacy skill directories, and ensures governance is correctly installed.

### Step 6.3 — Onboarding

Invoke the **swain-help** skill in onboarding mode to give the user a guided orientation of what they just installed.

### Step 6.4 — Summary

Report what was done:

> **swain init complete.**
>
> - CLAUDE.md → `@AGENTS.md` include pattern: [done/skipped/already set up]
> - tk (ticket) verified: [done/not found]
> - Beads migration: [done/skipped/no beads found]
> - Pre-commit security hooks: [done/skipped/already configured]
> - Superpowers: [installed/skipped/already present]
> - Swain governance in AGENTS.md: [done/skipped/already present]

## Re-running init

If the user runs `/swain init` on a project that's already set up, each phase will detect its work is done and skip. The only interactive phase is governance injection (Phase 5), which checks for the `<!-- swain governance -->` marker before asking.

To force a fresh governance block, delete the `<!-- swain governance -->` ... `<!-- end swain governance -->` section from AGENTS.md and re-run.
