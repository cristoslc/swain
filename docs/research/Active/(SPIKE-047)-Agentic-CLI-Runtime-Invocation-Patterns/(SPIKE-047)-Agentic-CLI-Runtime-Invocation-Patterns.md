---
title: "Agentic CLI Runtime Invocation Patterns"
artifact: SPIKE-047
track: container
status: Active
author: cristos
created: 2026-03-26
last-updated: 2026-03-26
question: "What are the exact CLI invocation patterns (command, flags, initial prompt mechanism, tmux compatibility) for each agentic runtime swain targets?"
gate: Pre-Implementation
risks-addressed:
  - Shell launcher templates hardcode Claude Code flags — adding runtimes without research risks broken templates
  - No ADR defines which runtimes swain supports — scope creep or missing runtimes
evidence-pool: ""
linked-artifacts:
  - SPEC-172
  - EPIC-045
---

# Agentic CLI Runtime Invocation Patterns

## Summary

**Go.** All five candidate runtimes (Claude Code, Gemini CLI, Codex CLI, GitHub Copilot CLI, Crush) are compatible with swain's shell launcher pattern. Four support interactive mode with an initial prompt; Crush requires AGENTS.md auto-invoke as a fallback. Decision recorded in ADR-017. Templates should be structured as `launchers/{runtime}/swain.{shell}` to accommodate the runtime x shell matrix.

## Question

What are the exact CLI invocation patterns (command, flags, initial prompt mechanism, tmux compatibility) for each agentic runtime swain targets — specifically Claude Code, Gemini CLI, Codex CLI, opencode, and GitHub Copilot CLI?

## Go / No-Go Criteria

- **Go:** For each runtime, we can document: (1) the binary/command name, (2) flags for non-interactive permission bypass, (3) how to pass an initial prompt as a positional arg, and (4) whether tmux wrapping works.
- **No-Go:** If a runtime lacks interactive mode or cannot accept an initial prompt, it gets flagged as "unsupported" with a documented reason.

## Pivot Recommendation

If most runtimes can't accept an initial prompt, restructure the templates to launch the runtime bare and rely on AGENTS.md / project-level config for session initialization instead of a positional arg.

## Findings

### Compatibility matrix

| Runtime | Binary | Interactive + prompt | Non-interactive | Permission bypass | tmux | Reads AGENTS.md |
|---------|--------|---------------------|-----------------|-------------------|------|-----------------|
| Claude Code | `claude` | `claude "prompt"` (positional) | `claude -p "prompt"` | `--dangerously-skip-permissions` | Yes | Yes (native) |
| Gemini CLI | `gemini` | `gemini -i "prompt"` | `gemini -p "prompt"` | `-y` / `--yolo` | Yes | Via `context.fileName` setting |
| Codex CLI | `codex` | `codex "prompt"` (positional) | `codex exec "prompt"` | `--full-auto` / `--dangerously-bypass-approvals-and-sandbox` | Yes (`--no-alt-screen`) | Yes (native) |
| Copilot CLI | `copilot` | `copilot -i "prompt"` | `copilot -p "prompt"` | `--yolo` / `--allow-all` | Yes | Yes (native) |
| Crush (was opencode) | `crush` | Interactive TUI only | `crush run "prompt"` (positional) | `--yolo` (interactive); auto in `run` mode | Yes (Bubble Tea) | Yes (native) |

### Per-runtime details

#### Claude Code (v2.1.85)

- **Install:** `npm install -g @anthropic-ai/claude-code`
- **Interactive launch:** `claude "prompt"` — positional arg starts interactive session with prompt pre-filled
- **Permission bypass:** `--dangerously-skip-permissions` (full bypass) or `--allow-dangerously-skip-permissions` (makes bypass available as option)
- **Key flags:** `--chrome` (browser extension), `--model <model>`, `-c`/`--continue` (resume), `-n`/`--name` (session name), `--add-dir <dirs>`
- **tmux:** First-class support. `--tmux` flag (tied to `--worktree`). Works fine inside existing tmux panes.
- **AGENTS.md:** Native support
- **Launcher pattern:** `claude --dangerously-skip-permissions --chrome '/swain-init'`

#### Gemini CLI (v0.35.2)

- **Install:** `npm install -g @google/gemini-cli` or `brew install gemini-cli`
- **Interactive launch:** `gemini -i "prompt"` — executes prompt then drops to REPL
- **Permission bypass:** `-y` / `--yolo` (auto-accept all) or `--approval-mode yolo`
- **Key flags:** `-s`/`--sandbox` (Seatbelt on macOS), `-m <model>`, `-r <id>` (resume), `--include-directories`
- **tmux:** Works (Ink/React TUI provides proper PTY)
- **AGENTS.md:** Supported via `settings.json` → `context.fileName: ["AGENTS.md"]`. Also reads `GEMINI.md` natively.
- **Launcher pattern:** `gemini -y -i '/swain-init'`

#### Codex CLI (OpenAI, Rust-based)

- **Install:** `npm install -g @openai/codex` or `brew install --cask codex`
- **Interactive launch:** `codex "prompt"` — positional arg in TUI mode
- **Permission bypass:** `--full-auto` (sandboxed, model-driven) or `--dangerously-bypass-approvals-and-sandbox` (full bypass, alias `--yolo`)
- **Key flags:** `-C <dir>` (set working dir), `--json` (JSONL events), `-m <model>`, `--no-alt-screen` (for multiplexers)
- **tmux:** Works with `--no-alt-screen`
- **AGENTS.md:** Native support. Also imports Claude-style config from `.claude/` directories.
- **Launcher pattern:** `codex --full-auto "prompt"` or `codex --yolo "prompt"`

#### GitHub Copilot CLI (v1.0.11)

- **Install:** Built into `gh` CLI (`gh copilot`) or standalone `copilot` binary via Homebrew
- **Interactive launch:** `copilot -i "prompt"` — executes prompt then stays open
- **Permission bypass:** `--yolo` / `--allow-all` (all permissions) or granular `--allow-all-tools`, `--allow-all-paths`
- **Key flags:** `--no-ask-user` (fully autonomous), `--autopilot` (continuation without input), `--model <model>`, `--resume`/`--continue`, `--no-auto-update`
- **tmux:** Works. Has `--no-alt-screen` flag. `-p` mode is completely headless.
- **AGENTS.md:** Native support. Also reads `.github/copilot-instructions.md`.
- **Launcher pattern:** `copilot --yolo -i '/swain-init'`

#### Crush (formerly opencode, v0.x — active)

- **Install:** `brew install charmbracelet/tap/crush` or `npm install -g @charmland/crush` or `go install github.com/charmbracelet/crush@latest`
- **Note:** `opencode` repo is archived. Crush is the active successor maintained by Charm.
- **Interactive launch:** TUI only (no initial prompt flag for interactive mode)
- **Non-interactive:** `crush run "prompt"` — positional arg, auto-approves permissions
- **Permission bypass:** `--yolo` (interactive mode); `run` subcommand auto-approves implicitly
- **Key flags:** `--cwd <dir>`, `-m <model>`, `-q` (quiet), `-v` (verbose)
- **tmux:** Works (Bubble Tea framework, proper terminal handling)
- **AGENTS.md:** Native support. Also reads `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`.
- **Limitation:** No interactive-with-initial-prompt mode. `crush run` is fire-and-forget.
- **Launcher pattern:** `crush --yolo` (interactive, no initial prompt) or `crush run '/swain-init'` (non-interactive)

### Key observations

1. **All five runtimes are compatible** with some form of launcher template. All work in tmux. All read or can be configured to read AGENTS.md.

2. **Initial prompt mechanism varies:**
   - Positional arg for interactive: Claude Code, Codex
   - `-i` flag for interactive: Gemini, Copilot
   - No interactive-with-prompt: Crush (only `crush run` which is non-interactive)

3. **Permission bypass flag names converge on `--yolo`:** Gemini, Codex, Copilot, and Crush all support `--yolo`. Claude Code uses `--dangerously-skip-permissions`.

4. **Template structure implication:** Templates need a two-dimensional matrix: `{shell} x {runtime}`. Since the function body varies significantly per runtime (different flags, different prompt mechanisms), the cleanest approach is one template file per runtime containing all three shell variants, or a directory structure like `launchers/{runtime}/swain.{shell}`.

5. **Crush caveat:** The interactive mode cannot accept an initial prompt. Investigated thoroughly: no startup hooks, no init scripts, no config-driven auto-prompt. Issue #441 (requesting `-p` for interactive mode) was closed NOT_PLANNED. Best path: AGENTS.md auto-invoke directive ("at session start, execute /swain-init") — same pattern swain already uses for Claude Code session startup. Alternative: custom command `.crush/commands/swain-init.md` reduces friction to `/swain-init`. Crush stays at Partial support per ADR-017.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-26 | — | Initial creation |
