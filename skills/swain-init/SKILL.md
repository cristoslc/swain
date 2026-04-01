---
name: swain-init
description: "Project onboarding and session entry point for swain. On first run, performs full onboarding: migrates CLAUDE.md to AGENTS.md, verifies vendored tk, configures pre-commit security hooks, and offers swain governance rules — then writes a .swain-init marker. On subsequent runs, detects the marker and delegates directly to swain-session. Use as a single entry point — it routes automatically."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion, Skill
metadata:
  short-description: One-time swain project onboarding
  version: 4.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Project Onboarding

One-time setup for adopting swain in a project. This skill is **not idempotent** — it migrates files and installs tools. For per-session health checks, use swain-doctor.

## Phase 0: Already-initialized detection

Before running onboarding, check for the `.swain-init` marker file:

```bash
cat .swain-init 2>/dev/null
```

### If `.swain-init` exists

The project has already been initialized. Parse the file (JSON format) and check the latest entry in the `history` array:

```bash
LAST_VERSION=$(jq -r '.history[-1].version' .swain-init 2>/dev/null)
CURRENT_VERSION=$(find . .claude .agents -path '*/swain-init/SKILL.md' -print -quit 2>/dev/null | xargs head -20 2>/dev/null | grep 'version:' | awk '{print $2}')
```

**Version comparison:**

- **Same major version** (e.g., both `4.x.x`): Project is current. Tell the user:
  > Project already initialized (swain $LAST_VERSION). Delegating to swain-session.

  Invoke the **swain-session** skill and stop. Do not run Phases 1–6.

- **Newer major version available** (e.g., initialized with `3.x.x`, current is `4.x.x`): Suggest upgrade. Tell the user:
  > Project was initialized with swain $LAST_VERSION (current: $CURRENT_VERSION). Consider running `/swain update` to pick up new features.
  > Starting session.

  Invoke the **swain-session** skill and stop. Do not re-run onboarding — upgrades are handled by swain-update, not swain-init.

### If `.swain-init` does not exist

Proceed with full onboarding (Phases 1–6).

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
> The vendored tk script was not found. This usually means the swain-do skill was not fully installed. Try running `/swain update` to reinstall skills.

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

### Step 2.4 — Operator bin/ symlinks (SPEC-214, ADR-019)

Create `bin/` symlinks for all operator-facing scripts declared in `skills/*/usr/bin/` manifest directories. This is the same logic swain-doctor uses for auto-repair.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BIN_DIR="$REPO_ROOT/bin"
for manifest_dir in "$REPO_ROOT"/skills/*/usr/bin; do
  [ -d "$manifest_dir" ] || continue
  for entry in "$manifest_dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    cmd_name="$(basename "$entry")"
    script_path="$(cd "$manifest_dir" && readlink -f "$cmd_name" 2>/dev/null || true)"
    [ -z "$script_path" ] || [ ! -f "$script_path" ] && continue
    rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$script_path" "$BIN_DIR" 2>/dev/null || echo "")"
    [ -z "$rel_path" ] && continue
    if [ -L "$BIN_DIR/$cmd_name" ]; then
      echo "already linked: $cmd_name"
    elif [ -e "$BIN_DIR/$cmd_name" ]; then
      echo "conflict — bin/$cmd_name exists as a real file; skipping"
    else
      mkdir -p "$BIN_DIR"
      ln -sf "$rel_path" "$BIN_DIR/$cmd_name"
      echo "created bin/$cmd_name"
    fi
  done
done
```

Tell the user which operator commands are now available in `bin/`.

If no `usr/bin/` manifest directories are found, skip silently.

## Phase 2.5: Branch model

swain recommends a **trunk+release** branch model (see ADR-013):

- **trunk** — development branch; agents land work here via merge-with-retry
- **release** — default/distribution branch; updated from trunk via squash-merge at release time

Tell the user:

> swain recommends a trunk+release branch model (ADR-013). If you'd like to adopt it, run `scripts/migrate-to-trunk-release.sh` (or `--dry-run` to preview). This is optional — swain works with any branch model, but sync and release features assume trunk+release when configured.

This phase is informational only — do not modify branches automatically. The operator decides whether to adopt the model.

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

### Step 4.4 — Tmux

Check if tmux is installed:

```bash
which tmux
```

If tmux is **already installed**, report "tmux: already installed" and continue to Phase 5.

If tmux is **not found**, ask the user:

> tmux is not installed. swain-session (tab naming) uses tmux when available. It is optional — swain works without it, but session tab-naming will be unavailable.
>
> Install tmux now? (yes/no)

If the user says **yes**:

```bash
brew install tmux
```

If the install succeeds, tell the user:
> tmux installed. Workspace layout and tab naming features are now available.

If the install fails, warn:
> tmux installation failed. You can install it manually: `brew install tmux`

If the user says **no**, note "tmux: skipped" and continue to Phase 4.5.

## Phase 4.5: Shell launcher

Goal: offer to install a `swain` shell function so the user can launch swain with a single command. Templates are stored per-runtime, per-shell in `templates/launchers/{runtime}/swain.{shell}` (relative to this skill's directory) — inspect them to see exactly what gets added. Supported runtimes are defined in ADR-017.

### Step 4.5.1 — Detect shell runtime

```bash
SHELL_NAME=$(basename "$SHELL")
```

Supported shells: `zsh`, `bash`, `fish`. If the detected shell is not in this list, tell the user:

> Shell launcher templates are available for zsh, bash, and fish. Your shell ($SHELL_NAME) is not yet supported — skipping launcher setup.

Skip to Phase 5.

### Step 4.5.2 — Check for existing launcher

Map the shell to its rc file and detection pattern:

| Shell | RC file | Detection pattern |
|-------|---------|-------------------|
| zsh | `~/.zshrc` | `grep -q 'swain\s*()' ~/.zshrc 2>/dev/null` |
| bash | `~/.bashrc` | `grep -q 'swain\s*()' ~/.bashrc 2>/dev/null` |
| fish | `~/.config/fish/config.fish` | `grep -q 'function swain' ~/.config/fish/config.fish 2>/dev/null` |

If the pattern matches, report "Shell launcher: already installed" and skip to Phase 5. Do not modify existing functions.

### Step 4.5.3 — Detect installed agentic runtimes

```bash
RUNTIMES=""
command -v claude >/dev/null 2>&1 && RUNTIMES="$RUNTIMES claude"
command -v gemini >/dev/null 2>&1 && RUNTIMES="$RUNTIMES gemini"
command -v codex >/dev/null 2>&1 && RUNTIMES="$RUNTIMES codex"
command -v copilot >/dev/null 2>&1 && RUNTIMES="$RUNTIMES copilot"
command -v crush >/dev/null 2>&1 && RUNTIMES="$RUNTIMES crush"
```

If no runtimes are found, tell the user:

> No supported agentic CLI runtimes found (checked: claude, gemini, codex, copilot, crush). Install one first, then re-run `/swain-init`.

Skip to Phase 5.

### Step 4.5.4 — Select runtime

- **One runtime found:** Offer it directly.
- **Multiple runtimes found:** Present a numbered list and ask which one to use. Default to `claude` if available.

Locate the template:

```bash
TEMPLATE_DIR="$(find . .claude .agents -path '*/swain-init/templates/launchers' -type d -print -quit 2>/dev/null)"
TEMPLATE_FILE="$TEMPLATE_DIR/$SELECTED_RUNTIME/swain.$SHELL_NAME"
```

### Step 4.5.5 — Show template and offer installation

Read the template file content and present it to the user:

> **Shell launcher** — Add a `swain` command to your shell?
>
> Detected runtime: [runtime name]. Here's what will be added to `<rc-file>`:
>
> ```<shell>
> <template content>
> ```
>
> Install? (yes/no)

For Crush templates, add a note: "Crush has partial support — it cannot accept an initial prompt, so session initialization relies on AGENTS.md auto-invoke directives."

### Step 4.5.6 — Install

If the user accepts, append the template content to the rc file:

```bash
cat "$TEMPLATE_FILE" >> <rc-file>
```

Tell the user:

> Shell launcher installed. Run `source <rc-file>` (or restart your shell) to activate the `swain` command.

If the user declines, note "Shell launcher: skipped" and continue to Phase 5.

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

Read the canonical governance content from the sibling `swain-doctor/references/AGENTS.content.md`. Locate it by searching for the file relative to the installed skills directory:

```bash
find .claude/skills .agents/skills skills -path '*/swain-doctor/references/AGENTS.content.md' -print -quit 2>/dev/null
```

Append the full contents of that file to AGENTS.md.

Tell the user:
> Governance rules added to AGENTS.md. These ensure swain skills are routable and conventions are enforced. You can customize anything outside the `<!-- swain governance -->` markers.

## Phase 5.5: README seeding and artifact proposals (SPEC-207)

Goal: ensure every swain project has a README, and offer to bootstrap artifacts from it when the artifact tree is empty.

### Step 5.5.1 — Check for README

```bash
[ -f "README.md" ] && echo "exists" || echo "missing"
```

### Step 5.5.2 — Seed README if missing

If README.md does not exist, determine the project's context and seed one:

**Context detection:**
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HAS_CODE=$(find "$REPO_ROOT" -maxdepth 3 \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.go' -o -name '*.rs' -o -name '*.sh' \) -not -path '*/node_modules/*' -not -path '*/.git/*' -print -quit 2>/dev/null)
HAS_ARTIFACTS=$(find "$REPO_ROOT/docs" -name '*.md' -path '*/Active/*' -print -quit 2>/dev/null)
```

**Seeding strategy:**
- **No code, no artifacts** — Interview the operator: "What does this project do?" Write the README from their answer.
- **Code exists, no artifacts** — Infer project purpose from code (read entry points, package.json/pyproject.toml/go.mod, etc.). Present a draft README to the operator for editing.
- **Artifacts exist, no README** — Compile from Active Visions, Designs, Journeys, and Personas. Present a draft to the operator for editing.

Present the draft to the operator. They can approve, edit, or skip. If they skip, note "README: skipped" in the summary and swain-doctor will flag it on future sessions.

### Step 5.5.3 — Propose seed artifacts from README

If README.md exists (or was just created) but the artifact tree is empty or thin (fewer than 3 Active artifacts across Vision, Design, Journey, and Persona types):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ACTIVE_COUNT=$(find "$REPO_ROOT/docs" -path "*/Active/*" -name "*.md" 2>/dev/null | grep -cE "\(VISION|DESIGN|JOURNEY|PERSONA\)" || echo "0")
```

If `ACTIVE_COUNT < 3`, read the README and extract intent claims using semantic analysis. Propose seed artifacts:

- **Vision** — from the README's description of what the project does and why.
- **Personas** — from who the README addresses and what problems it describes.
- **Journeys** — from usage flows, examples, or "getting started" paths.
- **Designs** — from architectural or structural claims.

Present each proposal individually. The operator approves, edits, or rejects each one. Approved artifacts are created via swain-design. Rejected proposals are silently dropped.

**Semantic extraction:** Read the entire README as prose. No convention-based sections, no operator-placed markers. Any claim in the README is a potential intent source — install instructions, feature descriptions, behavioral claims, architectural statements.

## Phase 6: Finalize

### Step 6.1 — Create .agents directory

```bash
mkdir -p .agents
```

This directory is used by swain-do for configuration and by swain-design scripts for logs.

### Step 6.1.1 — Bootstrap .agents/bin/ (ADR-019)

Create `.agents/bin/` and populate it with symlinks for all agent-facing scripts in the skill tree. This gives skills a stable, O(1) resolution path instead of `find`-based lookups.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_BIN="$REPO_ROOT/.agents/bin"
mkdir -p "$AGENTS_BIN"
OPERATOR_SCRIPTS="swain swain-box"
for skill_scripts_dir in "$REPO_ROOT"/skills/*/scripts; do
  [ -d "$skill_scripts_dir" ] || continue
  for script in "$skill_scripts_dir"/*; do
    [ -f "$script" ] && [ -x "$script" ] || continue
    script_name="$(basename "$script")"
    case "$script_name" in test-*) continue ;; esac
    echo " $OPERATOR_SCRIPTS " | grep -q " $script_name " && continue
    rel_path="$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$script" "$AGENTS_BIN" 2>/dev/null)" || continue
    ln -sf "$rel_path" "$AGENTS_BIN/$script_name"
  done
done
```

Add `.agents/bin/` and `.agents/session.json` to `.gitignore` if not already present (consumer projects should not track these):

```bash
grep -qx '.agents/bin/' .gitignore 2>/dev/null || echo '.agents/bin/' >> .gitignore
grep -qx '.agents/session.json' .gitignore 2>/dev/null || echo '.agents/session.json' >> .gitignore
```

### Step 6.2 — Run swain-doctor

Invoke the **swain-doctor** skill. This validates `.tickets/` health, checks stale locks, removes legacy skill directories, and ensures governance is correctly installed.

### Step 6.3 — Onboarding

Invoke the **swain-help** skill in onboarding mode to give the user a guided orientation of what they just installed.

### Step 6.4 — Write `.swain-init` marker

After all onboarding phases complete, write the `.swain-init` marker file. This is the authoritative record that init has run.

```bash
CURRENT_VERSION=$(find . .claude .agents -path '*/swain-init/SKILL.md' -print -quit 2>/dev/null | xargs head -20 2>/dev/null | grep 'version:' | awk '{print $2}')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

If `.swain-init` already exists (partial re-init), read it and append to the history array. Otherwise create a new file:

```json
{
  "history": [
    {
      "version": "4.0.0",
      "timestamp": "2026-03-26T18:30:00Z",
      "action": "init"
    }
  ]
}
```

For upgrades (future use by swain-update), append an entry with `"action": "upgrade"` instead.

Write the file and ensure it is gitignored (it's project-local state, not shared):

```bash
grep -q '.swain-init' .gitignore 2>/dev/null || echo '.swain-init' >> .gitignore
```

### Step 6.5 — Summary

Report what was done:

> **swain init complete.**
>
> - CLAUDE.md → `@AGENTS.md` include pattern: [done/skipped/already set up]
> - tk (ticket) verified: [done/not found]
> - Beads migration: [done/skipped/no beads found]
> - Pre-commit security hooks: [done/skipped/already configured]
> - Superpowers: [installed/skipped/already present]
> - tmux: [installed/skipped/already present]
> - Shell launcher: [installed (runtime)/skipped/already present/no runtime found/unsupported shell]
> - Swain governance in AGENTS.md: [done/skipped/already present]
> - README: [seeded/already present/skipped]
> - Artifact proposals from README: [N proposed, M accepted/skipped/not applicable]
> - Init marker: written (.swain-init)

### Step 6.6 — Start session

After successful onboarding, invoke the **swain-session** skill to start the first session. This ensures the user lands in a fully active session regardless of whether they entered via `/swain-init` or `/swain-session`.

## Re-running init

If the user runs `/swain-init` on a project that's already set up, Phase 0 reads `.swain-init` and delegates directly to swain-session — no onboarding phases run, no interactive prompts appear. This lets users build muscle memory around `/swain-init` as a single entry point.

To force re-onboarding, delete `.swain-init` and re-run.
