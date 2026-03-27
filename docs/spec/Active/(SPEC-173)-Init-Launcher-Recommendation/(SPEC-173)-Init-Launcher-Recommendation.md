---
title: "Init Launcher Recommendation"
artifact: SPEC-173
track: implementable
status: Active
author: cristos
created: 2026-03-26
last-updated: 2026-03-27
priority-weight: ""
type: feature
parent-epic: EPIC-045
parent-initiative: ""
linked-artifacts:
  - ADR-017
  - SPIKE-047
depends-on-artifacts:
  - SPEC-175
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Init Launcher Recommendation

## Problem Statement

swain-init onboards a project but doesn't help the user set up the shell command to actually launch swain. Users have to discover and hand-write the launcher function, which leads to bugs (the `-p` flag incident) and friction. With five supported runtimes (ADR-017), the init flow needs to detect which runtime(s) the user has installed and recommend the right one.

## Desired Outcomes

After swain-init completes onboarding, the user has a working `swain` command in their shell that launches their preferred agentic runtime — or has explicitly declined the offer. The experience mirrors Phase 4 (superpowers): detect current state, show what will change, ask permission, apply.

## External Behavior

**New phase in swain-init:** Phase 4.5 (between superpowers/tmux and governance).

**Step 1 — Detect shell runtime:**

```bash
SHELL_NAME=$(basename "$SHELL")
```

Map to template shell extension. If the detected shell has no matching template, warn and skip.

**Step 2 — Detect installed agentic runtimes:**

```bash
command -v claude >/dev/null 2>&1 && RUNTIMES="$RUNTIMES claude"
command -v gemini >/dev/null 2>&1 && RUNTIMES="$RUNTIMES gemini"
command -v codex >/dev/null 2>&1 && RUNTIMES="$RUNTIMES codex"
command -v copilot >/dev/null 2>&1 && RUNTIMES="$RUNTIMES copilot"
command -v crush >/dev/null 2>&1 && RUNTIMES="$RUNTIMES crush"
```

**Step 3 — Check for existing launcher:**

Check if `swain` is already defined in the user's rc file (same detection as before). If found, report "Shell launcher: already installed" and skip.

**Step 4 — Select runtime and show template:**

- If exactly one runtime is found, offer it directly.
- If multiple runtimes are found, present a numbered list and ask which one to use. Default to `claude` if available.
- If no runtimes are found, warn and skip.

Read the template from `skills/swain-init/templates/launchers/{runtime}/swain.{shell}` and present it:

> **Shell launcher** — Add a `swain` command to your shell?
>
> Detected runtime: Claude Code. Here's what will be added to `~/.zshrc`:
>
> ```zsh
> [template content]
> ```
>
> Install? (yes/no)

**Step 5 — Install:**

If yes, append the template content to the appropriate rc file. Tell the user to `source` or restart.

**Step 6 — Update summary:**

Add to Phase 6.4 summary: `Shell launcher: [installed (runtime)/skipped/already present/no runtime found/unsupported shell]`

## Acceptance Criteria

1. **Given** only `claude` is installed, **when** swain-init runs and the user accepts, **then** the claude template is appended to the rc file.

2. **Given** `claude` and `gemini` are both installed, **when** swain-init runs, **then** it presents a choice between the two and installs the selected one.

3. **Given** `~/.zshrc` already contains a `swain()` function, **when** swain-init runs, **then** it reports "already installed" and does not modify the file.

4. **Given** `$SHELL` is `/bin/bash`, **when** swain-init runs, **then** it offers templates from the `{runtime}/swain.bash` path and targets `~/.bashrc`.

5. **Given** no supported runtimes are installed, **when** swain-init runs, **then** it warns that no agentic CLI was found and skips without error.

6. **Given** the user declines, **when** swain-init completes, **then** the summary shows "Shell launcher: skipped" and no rc file was modified.

7. **Given** the user accepts the `crush` runtime, **when** the template is shown, **then** the preview includes a note about Crush's partial support (no initial prompt).

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Does not reload the shell.
- Does not modify existing launcher functions — detect-and-skip only.
- Detection uses `command -v` for runtimes and `grep` for existing functions.
- Changes to swain-init SKILL.md require worktree isolation per AGENTS.md skill change discipline.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
| Active | 2026-03-27 | — | Revised for multi-runtime support (ADR-017, SPIKE-047) |
