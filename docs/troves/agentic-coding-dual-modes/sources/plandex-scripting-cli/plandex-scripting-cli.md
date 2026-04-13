---
source-id: plandex-scripting-cli
type: web
url: https://docs.plandex.ai/cli-reference/
title: "CLI Reference | Plandex Docs"
fetched: 2026-04-07T02:30:02Z
supplemental-urls:
  - https://plandex.ai/
  - https://github.com/plandex-ai/plandex
---

# Plandex — Terminal Coding Agent with Scripting and Autonomy Levels

**Plandex** is an open-source, terminal-based AI coding agent designed for large
projects and complex multi-file tasks. It uses a server-client architecture and runs
a persistent REPL. Both a cloud service and self-hosted option are available.

---

## Dual-mode overview

Plandex does not have a distinct "interactive" vs. "headless" binary — it is a REPL
with a **five-level autonomy system** that controls how much human approval is required.

| Autonomy level | Flag | What it automates |
|---|---|---|
| **None** | `--no-auto` | Step-by-step; confirms every action |
| **Basic** | `--basic` | Auto-continue plans; no other automation |
| **Plus** | `--plus` | Auto-update context, smart context, auto-commit |
| **Semi-Auto** | `--semi` | Auto-load context from project map |
| **Full-Auto** | `--full` | Auto-apply, auto-exec, auto-debug |

Full-Auto is the closest equivalent to headless mode in other tools.

---

## Scripting / non-interactive usage

Plandex has no dedicated "headless" flag. Unattended automation uses a combination of:

```bash
# Full auto-mode: apply changes, exec commands, auto-debug
plandex tell "Add OAuth2 to the login flow" --full --apply --commit --skip-menu

# Background task (non-blocking)
plandex tell "Refactor auth module" --bg

# Skip the interactive changes review menu
plandex tell "..." --skip-menu

# Auto-approve branch creation in scripts
plandex checkout feature-branch -y

# Build changes without interactive confirmation
plandex build --apply --commit
```

**Key flags for scripting:**

| Flag | Command | Effect |
|---|---|---|
| `--full` | `tell`, `continue`, `build` | Full-Auto: apply + exec + debug |
| `--apply` / `-a` | `tell`, `continue`, `build` | Auto-apply changes to project files |
| `--skip-menu` | `tell`, `continue`, `build` | Skip interactive pending-changes menu |
| `--commit` / `-c` | `tell`, `apply` | Auto-commit after applying |
| `--bg` | `tell`, `continue` | Run in background (non-blocking) |
| `--yes` / `-y` | `checkout` | Auto-confirm branch creation |
| `--auto-exec` | `tell`, `continue` | Auto-execute commands without confirmation |
| `--debug [n]` | `tell`, `continue` | Auto-run and debug failing commands (default 5 tries) |

---

## Full automation example (CI/CD pattern)

```bash
# Load relevant files into context
plandex load src/ -r

# Run the task in full auto mode
plandex tell -f task.txt --full --apply --commit --skip-menu

# Apply and commit any remaining pending changes
plandex apply --full --commit
```

---

## Output

Plandex outputs plain text only. There is no `--json` or `--output-format` flag.
For machine-readable results, parse stdout or capture the git diff after a run.

---

## Session continuity / background tasks

Plandex has a unique **background task / stream** system:

```bash
plandex ps                           # list active and recently finished streams
plandex connect <stream-id>          # attach to a running stream
plandex stop <stream-id>             # stop a running stream
plandex tell "..." --bg              # start a task in the background
```

Tasks run as server-side streams. Multiple plans can run in parallel.
Plans use **branches** (like git branches) to isolate experiments:

```bash
plandex checkout experiment-branch
plandex tell "Try the new approach"
plandex diff                        # review changes
plandex apply                       # or plandex reject
```

---

## Version control / sandbox model

Plandex's key differentiator is its **diff review sandbox**:
- Changes are staged in a pending state before application.
- `plandex diff` shows the diff before applying.
- `plandex rewind <n>` rolls back to a prior state.
- Full history tracked via `plandex log`.

This makes Plandex safer for large refactors — changes can be reviewed and
partially rejected before touching the working tree.

---

## Context management

Plandex has a sophisticated context management system:

```bash
plandex load src/ -r                  # load directory recursively
plandex load . --map                  # load project map (signatures only)
plandex load https://...              # load URL
cat output | plandex load             # load piped output
```

**Smart context** (`--smart-context`): loads only files relevant to each step,
rather than the entire project. This is Plandex's answer to large context costs.

Context window: 2M token effective window with 20M+ token project map indexing
via Tree-sitter.

---

## Model packs (multi-model support)

Plandex uses multiple models for different roles in a single plan:

```bash
plandex --daily           # balanced capability/cost/speed
plandex --reasoning       # reasoning model for planning
plandex --strong          # highest capability (Opus 4, GPT-5)
plandex --cheap           # cost-optimized
plandex --gemini-planner  # Gemini 2.5 Pro for planning
plandex --o3-planner      # OpenAI o3 for planning
plandex --opus-planner    # Anthropic Opus 4 for planning
```

Each plan uses distinct models for: planning, coding, building, and committing.
This is Plandex's skills-adjacent feature — model routing rather than tool routing.

---

## Skills dimension summary

| Dimension | Plandex |
|---|---|
| Skills/plugin name | No skills or extensions system |
| Extension mechanism | None; capability comes from model selection + tool flags |
| Custom tool support | No MCP integration documented |
| Closest equivalent to skills | Model packs — assign specialized models per task role |
| Context customization | `.plandexignore`, manual context loading, smart context |
| Notable gap | No MCP, no plugin system, no custom tool injection |
