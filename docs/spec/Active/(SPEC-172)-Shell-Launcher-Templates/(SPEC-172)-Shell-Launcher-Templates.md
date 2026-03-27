---
title: "Shell Launcher Templates"
artifact: SPEC-172
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
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Shell Launcher Templates

## Problem Statement

The shell function that launches swain is currently hand-maintained in each user's rc file and hardcoded to Claude Code. When CLI flags change (as happened with `-p` vs positional arg), every user has to debug and fix it manually. With five supported runtimes (ADR-017), we need a canonical source of truth for each runtime's launcher function across all supported shells.

## Desired Outcomes

A set of inspectable, version-controlled template files — organized by runtime and shell — that contain the exact launcher function code. When any runtime's CLI interface changes, updating one template file propagates the fix to all future installations. The directory structure makes it clear which runtime and shell each template targets.

## External Behavior

**File location:** `skills/swain-init/templates/launchers/{runtime}/swain.{shell}`

**Directory structure:**
```
skills/swain-init/templates/launchers/
├── claude/
│   ├── swain.zsh
│   ├── swain.bash
│   └── swain.fish
├── gemini/
│   ├── swain.zsh
│   ├── swain.bash
│   └── swain.fish
├── codex/
│   ├── swain.zsh
│   ├── swain.bash
│   └── swain.fish
├── copilot/
│   ├── swain.zsh
│   ├── swain.bash
│   └── swain.fish
└── crush/
    ├── swain.zsh
    ├── swain.bash
    └── swain.fish
```

**Per-runtime launcher commands** (from SPIKE-047):

| Runtime | Interactive launch | Permission bypass |
|---------|-------------------|-------------------|
| Claude Code | `claude --dangerously-skip-permissions '/swain-init'` | `--dangerously-skip-permissions` |
| Gemini CLI | `gemini -y -i '/swain-init'` | `-y` (yolo) |
| Codex CLI | `codex --yolo '/swain-init'` | `--yolo` |
| Copilot CLI | `copilot --yolo -i '/swain-init'` | `--yolo` |
| Crush | `crush --yolo` (no initial prompt) | `--yolo` |

**Template content requirements:**
- Each template contains a complete, copy-pasteable shell function named `swain`
- The function handles two contexts: inside tmux (launch directly) and outside tmux (wrap in `tmux new-session`)
- Each file includes a header comment identifying the runtime, shell, and swain version
- Crush templates omit the initial prompt (Partial support per ADR-017) and include a comment explaining why

## Acceptance Criteria

1. **Given** the templates directory, **when** I list `skills/swain-init/templates/launchers/`, **then** I see 5 runtime subdirectories each containing `swain.zsh`, `swain.bash`, and `swain.fish` (15 files total).

2. **Given** `claude/swain.zsh` is sourced outside tmux, **when** I run `swain`, **then** it wraps in `tmux new-session` with `claude --dangerously-skip-permissions '/swain-init'`.

3. **Given** `gemini/swain.zsh` is sourced inside tmux, **when** I run `swain`, **then** it executes `gemini -y -i '/swain-init'` directly.

4. **Given** `codex/swain.bash` is sourced, **when** I run `type swain`, **then** it shows `codex --yolo '/swain-init'` with tmux handling.

5. **Given** `copilot/swain.fish` exists, **when** I read it, **then** it uses `copilot --yolo -i '/swain-init'` with fish `if not set -q TMUX` syntax.

6. **Given** `crush/swain.zsh` is sourced, **when** I run `swain`, **then** it launches `crush --yolo` without an initial prompt, and the template includes a comment explaining Crush's partial support.

7. **Given** any template file, **when** I read it, **then** the header comments identify the runtime, shell, and swain version.

8. **Given** each `.zsh` and `.bash` template, **when** I run `zsh -n` / `bash -n` on it, **then** it passes syntax validation.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Only zsh, bash, and fish shells per ADR-017 criteria. Directory structure supports adding more.
- Templates use hardcoded flags — no variable substitution or templating engine.
- The function name is always `swain`.
- Crush templates document the partial support limitation inline.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
| Active | 2026-03-27 | — | Revised for multi-runtime support (ADR-017, SPIKE-047) |
