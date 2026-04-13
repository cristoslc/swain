---
source-id: goose-cli-headless-extensions
type: web
url: https://deepwiki.com/block/goose/3.2-command-line-interface
title: "Command-Line Interface | block/goose | DeepWiki"
fetched: 2026-04-07T02:30:01Z
supplemental-urls:
  - https://block.github.io/goose/docs/tutorials/headless-goose/
  - https://aitoolanalysis.com/goose-ai-review/
---

# Goose CLI — Headless Mode, Extensions, and Recipes

**Goose** is Block's (formerly Square) open-source agentic coding tool, written in Rust,
licensed under Apache 2.0. It targets the full development workflow: build, test,
debug, and deploy — not just code suggestions.

---

## Dual-mode overview

| Mode | Trigger | Description |
|---|---|---|
| **Interactive** | `goose session` | Persistent TUI chat. Uses rustyline for input. Supports slash commands, tab completion, and session forking. |
| **Headless** | `goose run -t "prompt"` | Single-turn, non-interactive execution. Accepts text, file paths, or piped stdin. Exits when done. |

---

## Headless mode

```bash
# Text prompt
goose run -t "Fix TypeScript errors in src/components/"

# From a file
goose run -i instructions.txt

# Piped stdin
cat task.md | goose run

# With specific extension enabled
goose run --with-builtin developer -t "Check system logs for errors"

# With a recipe
goose run --recipe automation-recipe.yaml
```

**Key flags:**
- `-t` / `--text` — inline prompt
- `-i` / `--input` — file path with instructions
- `--with-builtin <name>` — load a specific built-in extension for this run
- `--no-session` — skip session persistence (stateless run)
- `--output-format text|json|stream-json` — machine-readable output (same pattern as Claude Code)

**Environment variables for automation:**

| Variable | Purpose |
|---|---|
| `GOOSE_MODE=auto` | Non-interactive execution; skips all approval prompts |
| `MAX_TURNS=<n>` | Cap the number of agent turns |
| `CONTEXT_STRATEGY=<strategy>` | How to handle context limits |
| `GOOSE_DISABLE_SESSION_NAMING=true` | Skip the LLM call that names the session |

**Auto-approve equivalent:**
Setting `GOOSE_MODE=auto` removes all approval gates. Goose cannot prompt for
permission in this mode; risky operations either use default permissions or fail.

---

## Output formats

| Format | Flag | Notes |
|---|---|---|
| Plain text | default | Human-readable streaming output |
| JSON | `--output-format json` | Buffered; single JSON object on completion |
| Stream-JSON | `--output-format stream-json` | JSONL events as they arrive |

The JSON/stream-JSON output follows the same event-stream model as Claude Code and Gemini CLI.

---

## Session continuity

Headless runs are stateless by default (`--no-session`) or can persist:

```bash
goose session --resume last  # resume most recent session
goose session --resume <name-or-id>  # resume by name or ID
```

Sessions can also be **forked**: `goose session --fork` creates a new session
branching from an existing conversation's history.

---

## Extensions (skills/plugin system)

Goose's extensibility layer is called **extensions**. Extensions are MCP servers —
either built-in or custom — that add tools the agent can call.

**Built-in extensions:**
- `developer` — file editing, shell commands (the default coding toolkit)
- `computer-controller` — GUI automation
- Platform integrations (GitHub, Jira, Google Drive, etc.)

**Extension types:**
| Type | How configured | Use case |
|---|---|---|
| Built-in | `--with-builtin <name>` or `config.yaml` | Standard tools shipped with Goose |
| Stdio MCP | Command in config | External process communicating via stdio |
| HTTP/SSE MCP | URL in config | Remote MCP server |

**In-session commands:**
```
/extension <cmd>   # dynamically add a stdio extension mid-session
/builtin <name>    # enable a built-in extension mid-session
/mode auto|approve|smart_approve|chat
```

---

## Recipes (reusable parameterized workflows)

Recipes are YAML files that package prompt, extensions, parameters, and instructions
into a reusable workflow:

```yaml
# automation-recipe.yaml
title: "Automated Code Quality Check"
name: "code-quality"
description: "Linting, security scanning, test coverage analysis"
prompt: "Perform a comprehensive code quality analysis including linting, security scanning, test coverage analysis, and generate an improvement plan"
instructions: |
  You are an expert code quality engineer. ...
parameters:
  - name: target_dir
    description: "Directory to analyze"
    required: true
```

**Recipe commands:**
```bash
goose run --recipe code-quality.yaml --params target_dir=src/
goose recipe list    # list available recipes
goose recipe validate recipe.yaml
```

Recipes can call **sub-recipes**, enabling composable pipeline automation.
A parent recipe coordinates; child recipes handle platform-specific details.

**Recipes in headless mode must include a `prompt` field** — execution fails without one.

---

## Server architecture

Goose has a backend server (`goosed`) with REST and WebSocket APIs.
This is used internally by the desktop Electron app and is not the same as opencode's
public HTTP API. External clients can also use the **ACP (Agent Client Protocol)**
for structured agent orchestration.

---

## Skills dimension summary

| Dimension | Goose |
|---|---|
| Skills/plugin name | Extensions (MCP-based) |
| Built-in extensions | `developer`, `computer-controller`, platform integrations |
| Custom extension | Implement as an MCP server (stdio or HTTP) |
| Reusable workflows | Recipes (YAML, parameterized, composable) |
| Scheduled runs | `goose schedule add` — cron-based recipe scheduling |
| In-session skill loading | `/extension` and `/builtin` slash commands |
