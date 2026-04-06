---
name: swain-init
description: "Project onboarding and session entry point for swain. On first run, performs full onboarding: migrates CLAUDE.md to AGENTS.md, verifies vendored tk, configures pre-commit security hooks, and offers swain governance rules — then writes a .swain-init marker. On subsequent runs, detects the marker and runs the per-session fast path (greeting, focus lane, session state). Use as a single entry point — it routes automatically. Triggers also on: 'session', 'session info', 'focus on', 'tab name'."
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

## Preflight

Before any phase, run the preflight script to gather environment state. This single call replaces all inline check blocks — phases below read from the JSON output instead of running shell commands.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PREFLIGHT_SCRIPT="$(find "$REPO_ROOT" -path '*/swain-init/scripts/swain-init-preflight.sh' -print -quit 2>/dev/null)"
PREFLIGHT_JSON=$( bash "$PREFLIGHT_SCRIPT" --repo-root "$REPO_ROOT" 2>/dev/null )
echo "$PREFLIGHT_JSON"
```

Store `PREFLIGHT_JSON` for use in all phases below. Every decision references a field from this JSON — do not run additional check commands unless performing a mutation.

## Phase 0: Already-initialized detection

Read `marker.action` from the preflight JSON.

- **`"delegate"`** — same major version. Tell the user:
  > Project already initialized (swain `marker.release_version`, init v`marker.last_version`). Delegating to swain-session.

  Skip to **Phase 7 (Session Start)** below. Do not run Phases 1–6.

- **`"upgrade"`** — newer major version available. Tell the user:
  > Project was initialized with swain `marker.last_release_version` (init v`marker.last_version`). Current: `marker.release_version` (init v`marker.current_version`). Consider running `/swain update` to pick up new features.
  > Starting session.

  Skip to **Phase 7 (Session Start)** below. Do not re-run onboarding — upgrades are handled by swain-update, not swain-init.

- **`"onboard"`** — no marker found. Proceed with full onboarding (Phases 1–6).

## Phase 1: CLAUDE.md → AGENTS.md migration

Goal: establish the `@AGENTS.md` include pattern so project instructions live in AGENTS.md (which works across Claude Code, GitHub, and other tools that read AGENTS.md natively).

Read `migration.state` from the preflight JSON.

### If `"fresh"`

Create both files:

- **CLAUDE.md:** `@AGENTS.md`
- **AGENTS.md:** `# AGENTS.md` (empty — governance added in Phase 5)

### If `"migrated"`

Skip to Phase 2.

### If `"standard"`

1. Copy CLAUDE.md content to AGENTS.md (preserve everything).
2. If CLAUDE.md contains a `<!-- swain governance -->` block, strip it from the AGENTS.md copy — it will be re-added cleanly in Phase 5.
3. Replace CLAUDE.md with `@AGENTS.md`.

Tell the user:
> Migrated your CLAUDE.md content to AGENTS.md and replaced CLAUDE.md with `@AGENTS.md`. Your existing instructions are preserved — Claude Code reads AGENTS.md via the include directive.

### If `"split"`

Both files have content. Ask the user:

> Both CLAUDE.md and AGENTS.md have content. How should I proceed?
> 1. **Merge** — append CLAUDE.md content to the end of AGENTS.md, then replace CLAUDE.md with `@AGENTS.md`
> 2. **Keep AGENTS.md** — discard CLAUDE.md content, replace CLAUDE.md with `@AGENTS.md`
> 3. **Abort** — leave both files as-is, skip migration

If merge: append CLAUDE.md content (minus any `<!-- swain governance -->` block) to AGENTS.md, replace CLAUDE.md with `@AGENTS.md`.

## Phase 2: Verify dependencies

### Step 2.1 — uv

Read `uv.available` from the preflight JSON.

If `false`, install:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If installation fails, tell the user:
> uv installation failed. You can install it manually (https://docs.astral.sh/uv/getting-started/installation/) — swain scripts require uv for Python execution.

Skip the rest of Phase 2 on failure (don't block init on uv, but warn that scripts will not function without it).

### Step 2.2 — Vendored tk

Read `tk.path` and `tk.healthy` from the preflight JSON.

If `tk.path` is null or `tk.healthy` is false, tell the user:
> The vendored tk script was not found or is broken. This usually means the swain-do skill was not fully installed. Try running `/swain update` to reinstall skills.

### Step 2.3 — Migrate from beads (if applicable)

Read `beads.exists` and `beads.has_backup` from the preflight JSON.

If `beads.exists` is true and `beads.has_backup` is true, offer migration:

> Found existing `.beads/` data. Migrate tasks to tk?
> This will convert `.beads/backup/issues.jsonl` to `.tickets/` markdown files.

If user agrees, run migration:
```bash
TK_BIN="$(cd "$(dirname "$(find . .claude .agents -path '*/swain-do/bin/tk' -print -quit 2>/dev/null)")" && pwd)"
export PATH="$TK_BIN:$PATH"
cp .beads/backup/issues.jsonl .beads/issues.jsonl 2>/dev/null
ticket-migrate-beads
ls .tickets/*.md 2>/dev/null | wc -l
```

Tell the user the results and that `.beads/` can be removed after verification.

If `beads.exists` is false, skip. tk creates `.tickets/` on first `tk create`.

### Step 2.4 — Operator bin/ symlinks (SPEC-214, ADR-019)

Read `bin_manifests` from the preflight JSON. For each entry, create `bin/` symlinks:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BIN_DIR="$REPO_ROOT/bin"
SKILLS_ROOT="$REPO_ROOT/.agents/skills"
for manifest_dir in "$SKILLS_ROOT"/*/usr/bin; do
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

If `bin_manifests` is empty, skip silently.

## Phase 3: Pre-commit security hooks

Goal: configure pre-commit hooks for secret scanning so credentials are caught before they enter git history. Default scanner is gitleaks; additional scanners (TruffleHog, Trivy, OSV-Scanner) are opt-in.

### Step 3.1 — Check for existing config

Read `precommit.config_exists` from the preflight JSON.

**If true:** Present the current `.pre-commit-config.yaml` content and ask:

> Found existing `.pre-commit-config.yaml`. How should I proceed?
> 1. **Merge** — add swain's gitleaks hook alongside your existing hooks
> 2. **Skip** — leave pre-commit config unchanged
> 3. **Replace** — overwrite with swain's default config (your existing hooks will be lost)

If user chooses Skip, skip to Phase 4.

**If false:** Proceed to Step 3.2.

### Step 3.2 — Install pre-commit framework

Read `precommit.framework` from the preflight JSON.

If false, install:

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

Run `pre-commit install` to activate the hooks.

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

Goal: offer to install `obra/superpowers` if it is not already present.

### Step 4.1 — Detect superpowers

Read `superpowers.installed` from the preflight JSON.

If true, report "Superpowers: already installed" and skip to Phase 4.4.

### Step 4.2 — Offer installation

Ask the user:

> Superpowers (`obra/superpowers`) is not installed. It provides TDD, brainstorming, plan writing, and verification skills that swain chains into during implementation and design work.
>
> Install superpowers now? (yes/no)

If the user says **no**, note "Superpowers: skipped" and continue to Phase 4.4. They can always install later: `npx skills add obra/superpowers`.

### Step 4.3 — Install

```bash
npx skills add obra/superpowers
```

If the install succeeds, tell the user:
> Superpowers installed. Brainstorming, TDD, plan writing, and verification skills are now available.

If it fails, warn:
> Superpowers installation failed. You can retry manually: `npx skills add obra/superpowers`

Continue to Phase 4.4 regardless.

### Step 4.4 — Tmux

Read `tmux.installed` from the preflight JSON.

If true, report "tmux: already installed" and continue to Phase 4.5.

If false, ask the user:

> tmux is not installed. swain uses tmux for tab naming when available. It is optional — swain works without it, but session tab-naming will be unavailable.
>
> Install tmux now? (yes/no)

If yes:

```bash
brew install tmux
```

If the install succeeds, tell the user:
> tmux installed. Workspace layout and tab naming features are now available.

If the install fails, warn:
> tmux installation failed. You can install it manually: `brew install tmux`

If no, note "tmux: skipped" and continue to Phase 4.5.

## Phase 4.5: Shell launcher

Goal: offer to install a `swain` shell function so the user can launch swain with a single command. Templates are stored per-runtime, per-shell in `templates/launchers/{runtime}/swain.{shell}` (relative to this skill's directory) — inspect them to see exactly what gets added. Supported runtimes are defined in ADR-017.

### Step 4.5.1 — Detect shell

Read `launcher.shell` from the preflight JSON.

Supported shells: `zsh`, `bash`, `fish`. If the shell is not in this list, tell the user:

> Shell launcher templates are available for zsh, bash, and fish. Your shell (`launcher.shell`) is not yet supported — skipping launcher setup.

Skip to Phase 5.

### Step 4.5.2 — Check for existing launcher

Read `launcher.already_installed` from the preflight JSON.

If true, report "Shell launcher: already installed" and skip to Phase 5. Do not modify existing functions.

### Step 4.5.3 — Detect runtimes

Read `launcher.runtimes` from the preflight JSON.

If the array is empty, tell the user:

> No supported agentic CLI runtimes found (checked: claude, gemini, codex, copilot, crush). Install one first, then re-run `/swain-init`.

Skip to Phase 5.

### Step 4.5.4 — Select runtime

- **One runtime found:** Offer it directly.
- **Multiple runtimes found:** Present a numbered list and ask which one to use. Default to `claude` if available.

Read `launcher.template_dir` from the preflight JSON. Construct the template path:

```
$TEMPLATE_DIR/$SELECTED_RUNTIME/swain.$SHELL_NAME
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

If the user accepts, append the template content to the rc file (read `launcher.rc_file` from preflight JSON, e.g. `cat "$TEMPLATE_FILE" >> "$RC_FILE"`).

Tell the user:

> Shell launcher installed. Run `source <rc-file>` (or restart your shell) to activate the `swain` command.

If the user declines, note "Shell launcher: skipped" and continue to Phase 5.

## Phase 5: Swain governance

Goal: add swain's routing and governance rules to AGENTS.md.

### Step 5.1 — Check for existing governance

Read `governance.installed` from the preflight JSON.

If true, governance is already installed. Tell the user and skip to Phase 5.5.

### Step 5.2 — Ask permission

Ask the user:

> Ready to add swain governance rules to AGENTS.md. These rules:
> - Route artifact requests (specs, stories, ADRs, etc.) to swain-design
> - Route task tracking to swain-do (using tk)
> - Enforce the pre-implementation protocol (plan before code)
> - Prefer swain skills over built-in alternatives
>
> Add governance rules to AGENTS.md? (yes/no)

If no, skip to Phase 5.5.

### Step 5.3 — Inject governance

Read the canonical governance content from `swain-doctor/references/AGENTS.content.md` (search `.claude/skills`, `.agents/skills`, and `skills` directories for the file). Append the full contents of that file to AGENTS.md.

Tell the user:
> Governance rules added to AGENTS.md. These ensure swain skills are routable and conventions are enforced. You can customize anything outside the `<!-- swain governance -->` markers.

## Phase 5.5: README seeding and artifact proposals (SPEC-207)

Goal: ensure every swain project has a README, and offer to bootstrap artifacts from it when the artifact tree is empty.

### Step 5.5.1 — Check for README

Read `readme.exists` from the preflight JSON.

### Step 5.5.2 — Seed README if missing

If `readme.exists` is false, determine the project's context using `readme.has_code` and `readme.has_artifacts` from the preflight JSON:

- **No code, no artifacts** — Interview the operator: "What does this project do?" Write the README from their answer.
- **Code exists, no artifacts** — Infer project purpose from code (read entry points, package.json/pyproject.toml/go.mod, etc.). Present a draft README to the operator for editing.
- **Artifacts exist, no README** — Compile from Active Visions, Designs, Journeys, and Personas. Present a draft to the operator for editing.

Present the draft to the operator. They can approve, edit, or skip. If they skip, note "README: skipped" in the summary and swain-doctor will flag it on future sessions.

### Step 5.5.3 — Propose seed artifacts from README

Read `readme.active_count` from the preflight JSON.

If `readme.active_count < 3` and README.md exists, read the README and extract intent claims using semantic analysis. Propose seed artifacts:

- **Vision** — from the README's description of what the project does and why.
- **Personas** — from who the README addresses and what problems it describes.
- **Journeys** — from usage flows, examples, or "getting started" paths.
- **Designs** — from architectural or structural claims.

Present each proposal individually. The operator approves, edits, or rejects each one. Approved artifacts are created via swain-design. Rejected proposals are silently dropped.

**Semantic extraction:** Read the entire README as prose. No convention-based sections, no operator-placed markers. Any claim in the README is a potential intent source — install instructions, feature descriptions, behavioral claims, architectural statements.

## Phase 6: Finalize

### Step 6.1 — Create .agents directory

Create `.agents/` if it does not exist (`mkdir -p .agents`). This directory is used by swain-do for configuration and by swain-design scripts for logs.

### Step 6.1.1 — Bootstrap .agents/bin/ (ADR-019)

Create `.agents/bin/` and populate it with symlinks for all agent-facing scripts in the skill tree:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
AGENTS_BIN="$REPO_ROOT/.agents/bin"
SKILLS_ROOT="$REPO_ROOT/.agents/skills"
mkdir -p "$AGENTS_BIN"
OPERATOR_SCRIPTS="swain swain-box"
for skill_scripts_dir in "$SKILLS_ROOT"/*/scripts; do
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

Add `.agents/bin/` and `.agents/session.json` to `.gitignore` if not already present (consumer projects should not track these).

### Step 6.2 — Run swain-doctor

Invoke the **swain-doctor** skill. This validates `.tickets/` health, checks stale locks, removes legacy skill directories, and ensures governance is correctly installed.

### Step 6.3 — Onboarding

Invoke the **swain-help** skill in onboarding mode to give the user a guided orientation of what they just installed.

### Step 6.4 — Write `.swain-init` marker

After all onboarding phases complete, write the `.swain-init` marker file. Read `marker.current_version` from the preflight JSON for the skill version and `marker.release_version` for the release version.

If `.swain-init` already exists (partial re-init), read it and append to the history array. Otherwise create a new file:

```json
{
  "history": [
    {
      "version": "4.0.0",
      "release": "v0.29.0-alpha",
      "timestamp": "2026-03-26T18:30:00Z",
      "action": "init"
    }
  ]
}
```

For upgrades (future use by swain-update), append an entry with `"action": "upgrade"` instead.

Write the file and ensure `.swain-init` is in `.gitignore` (it's project-local state, not shared).

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

After successful onboarding, proceed to **Phase 7 (Session Start)** below.

## Phase 7: Session Start (ADR-023)

This phase runs every time — both after fresh onboarding (Phase 6) and on the already-initialized fast path (Phase 0). It replaces the former swain-session startup sequence.

### Step 7.1 — Fast greeting

Run the fast greeting script. It calls the session preflight internally for all read-only state, then applies lightweight mutations (tab naming, lock cleanup). No subprocess chain — one preflight pass.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-greeting.sh" --json
```

The greeting emits structured JSON:

```json
{
  "greeting": true,
  "branch": "trunk",
  "dirty": false,
  "isolated": false,
  "bookmark": "Left off implementing the bootstrap script",
  "focus": "VISION-001",
  "tab": "project @ branch",
  "warnings": []
}
```

The session preflight (called internally by the greeting) also gathers previous session state. To access it directly:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PREFLIGHT_JSON=$( bash "$REPO_ROOT/.agents/bin/swain-session-preflight.sh" --repo-root "$REPO_ROOT" 2>/dev/null )
```

**After receiving the greeting JSON:**

1. Present the greeting to the operator — branch, dirty state, bookmark (if any), focus lane (if any), and warnings.

2. If `bookmark` is not null, display it:
   > **Resuming session** — Last time: {bookmark}

3. If `isolated` is `false`, **do not create a worktree now** — worktree creation is deferred to swain-do task dispatch (SPEC-195).

**If `$TMUX` is NOT set** (detected by absence of `tab` in the JSON), check whether tmux is installed:
- **tmux not installed:** Offer to install it (`brew install tmux`).
- **tmux installed but not in a session:** Show: `[note] Not in a tmux session — session tab and pane features unavailable`

### Step 7.2 — Session state init

Read `prev_session` from the session preflight JSON (or call the preflight directly if the greeting didn't expose it). If `prev_session.exists` is true, display its focus lane, walkaway note, and decision count. Ask the operator: "Continue previous session or start fresh?"

If starting fresh (or no previous session):

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-state.sh" init \
  --focus "<FOCUS-ID>" \
  --session-roadmap "$(pwd)/SESSION-ROADMAP.md" \
  --repo-root "$REPO_ROOT"
```

### Step 7.3 — Focus lane

The focus lane scopes recommendations to a single vision or initiative. It is set when the operator decides what to work on.

**If the greeting JSON included a `focus` value:** Confirm with the operator:
> Focus lane: {focus}. Continue with this focus, or change?

**If no focus is set:** Ask the operator what they want to work on. Resolve names to artifact IDs:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/chart.sh" --ids --flat 2>/dev/null | grep -i "<name>"
```

If exactly one match, use it. If multiple, ask the operator to clarify. If no match, tell the operator and offer to create one.

Set the focus:

```bash
bash "$REPO_ROOT/.agents/bin/swain-focus.sh" set <RESOLVED-ID>
```

Display the focus artifact context:

```bash
bash "$REPO_ROOT/.agents/bin/artifact-context.sh" <RESOLVED-ID> 2>/dev/null
```

The focus lane is stored in `.agents/session.json` under the `focus_lane` key and persists across the session.

### Step 7.4 — Session purpose text

When the operator launches with free text (e.g., `swain new bug about timestamps`), the launcher passes it as part of the initial prompt: `/swain-init Session purpose: new bug about timestamps`.

When session purpose text is present:
1. Write it as the session bookmark note (using swain-bookmark.sh)
2. Display it: `**Session purpose:** <text>`

Detection: if the skill is invoked with text containing "Session purpose: ", extract everything after that prefix.

For runtimes that don't support initial prompts, check the `SWAIN_PURPOSE` environment variable as a fallback.

### Worktree / branch changes

When an agent enters a worktree or switches branches, re-run the bootstrap with `--path` to update the tab name:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-bootstrap.sh" --path "$NEW_WORKDIR" --skip-worktree --auto
```

## Re-running init

If the user runs `/swain-init` on a project that's already set up, Phase 0 reads the preflight JSON's `marker.action` field and skips to Phase 7 (Session Start) — no onboarding phases run, no interactive prompts appear. This lets users build muscle memory around `/swain-init` as a single entry point.

To force re-onboarding, delete `.swain-init` and re-run.
