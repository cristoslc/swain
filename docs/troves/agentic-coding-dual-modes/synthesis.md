---
trove: agentic-coding-dual-modes
synthesized: 2026-04-07
sources: 8
related-troves:
  - opencode-crush-cli (opencode serve/run; Crush has no server mode)
  - claude-code-remote-interaction (claude -p; remote control; Agent SDK)
---

# Agentic coding environments — headful and headless modes

## Overview of the landscape (10 tools)

| Tool | Headful mode | Headless trigger | Output format | HTTP server? | Skills/extensions |
|---|---|---|---|---|---|
| **Claude Code** | Interactive TUI | `claude -p "prompt"` | text, JSON, stream-JSON | No (Agent SDK) | SKILL.md files in `.claude/skills/` |
| **opencode** | TUI (client/server) | `opencode serve` + `opencode run` | REST API, JSON | **Yes** | No native skills system |
| **Codex CLI** | Interactive TUI | `codex exec "prompt"` | text, JSONL | App Server + MCP Server | No skills; MCP only |
| **Gemini CLI** | Interactive TUI | `gemini -p "prompt"` or non-TTY | text, JSON, stream-JSON (JSONL) | No (ACP mode) | No skills; MCP only |
| **Qwen Code** | Interactive TUI | `qwen -p "prompt"` or non-TTY | text, JSON, stream-JSON | No (TypeScript SDK) | SKILL.md (Claude Code fork) |
| **Aider** | REPL terminal | `aider --message "..." --yes` | stdout text only | No (Python API) | No skills/extensions |
| **Goose** | Interactive TUI or desktop app | `goose run -t "prompt"` | text, JSON, stream-JSON | Yes (goosed server, internal) | Extensions (MCP) + Recipes (YAML) |
| **Amp** | VS Code extension or CLI (TTY) | `amp -x "prompt"` | text (stdout) | No | Toolboxes (shell scripts) + Agent Skills + MCP |
| **Cline** | VS Code extension or CLI (TTY) | `cline -y "task"` | text, JSON (`--json`) | No (ACP) | Skills (SKILL.md, on-demand) + MCP |
| **Plandex** | Terminal REPL | `plandex tell ... --full --apply --skip-menu` | text only | No (internal server) | No skills/extensions; model packs only |

*Coverage notes: Claude Code and opencode are covered in depth in the related troves
`claude-code-remote-interaction` and `opencode-crush-cli`. This trove covers the remaining 8 tools.*

---

## Theme 1 — The `-p` / `--prompt` flag is the universal headless trigger for CLI-first tools

Every Claude Code derivative (Claude Code, Gemini CLI, Qwen Code) uses `-p` / `--prompt`
to trigger headless mode. Goose uses `goose run -t`. Aider uses `--message`.
Amp uses `-x`. Cline uses `-y` or `--yolo`. Plandex has no single headless flag —
it uses a combination of automation-level and apply flags.

```bash
claude -p "review src/auth.py"           # Claude Code
gemini -p "review src/auth.py"            # Gemini CLI
qwen -p "review src/auth.py"              # Qwen Code
codex exec "review src/auth.py"           # Codex CLI
aider --message "review src/auth.py" --yes src/auth.py  # Aider
opencode run "review src/auth.py"         # opencode
goose run -t "review src/auth.py"         # Goose
amp -x "review src/auth.py"               # Amp
cline -y "review src/auth.py"             # Cline
plandex load src/auth.py && plandex tell "review src/auth.py" --full --apply --skip-menu  # Plandex
```

---

## Theme 2 — JSON / stream-JSON output is the standard for mainline CLI tools

| Tool | Flag | Format |
|---|---|---|
| Claude Code | `--output-format json` | JSON array of message objects |
| Claude Code | `--output-format stream-json` | JSONL events |
| Gemini CLI | `--output-format json` | Single JSON object |
| Gemini CLI | `--output-format stream-json` | JSONL events |
| Qwen Code | `--output-format json` | JSON array (buffered) |
| Qwen Code | `--output-format stream-json` | JSONL (streaming) |
| Codex CLI | `--json` | JSONL events |
| Goose | `--output-format json/stream-json` | Matches the claude/gemini pattern |
| Cline | `--json` | JSON output for scripting |
| Aider | none | Plain text only |
| Amp | none documented | Plain text only |
| Plandex | none | Plain text only |

Tools without JSON output (Aider, Amp, Plandex) are harder to compose in machine-driven pipelines.

---

## Theme 3 — Three architectures for "server mode"

### A. CLI-flag headless (pure subprocess model)
Claude Code, Gemini CLI, Qwen Code, Aider, Amp, Cline — start a fresh process per run.
No persistent server. State is carried via `--continue` / `--resume` session IDs.
Simple to orchestrate: call the binary in a loop.

### B. HTTP server (opencode and Goose)
opencode exposes a full public REST API (`opencode serve`). Goose runs an internal
server (`goosed`) used by the desktop app — not a public API but exposed via ACP
for external orchestration.

### C. REPL with internal server (Plandex)
Plandex runs an internal server that the CLI connects to. Tasks can run in the
background (`--bg`) and be reattached later (`plandex connect`). Multiple plans
can run in parallel as separate streams.

---

## Theme 4 — Session continuity in headless runs

| Tool | Session resume | Background tasks |
|---|---|---|
| **opencode** | `opencode run --attach http://localhost:4096` | Server handles persistence |
| **Claude Code** | `claude --continue` / `--resume <id>` | No |
| **Codex CLI** | `codex exec resume --last` / `codex exec resume <id>` | No |
| **Qwen Code** | `qwen --continue` / `--resume <id>` | No |
| **Gemini CLI** | Session management + checkpointing | No |
| **Aider** | No — each `--message` run is independent | No |
| **Goose** | `goose session --resume last` / `--fork` | Scheduled recipes (`goose schedule`) |
| **Amp** | Server-side Threads, accessible from any device | No |
| **Cline** | `--continue` / `--resume <id>` | No |
| **Plandex** | Plans are persistent on the Plandex server | `plandex tell --bg` + `plandex connect` |

Amp's server-side thread model is unique — threads are accessible across devices
and teammates. Plandex's background streams are the only subprocess model where
tasks survive terminal closure without a full HTTP server.

---

## Theme 5 — Auto-approval is mandatory for unattended automation

| Tool | Auto-approve flag |
|---|---|
| Claude Code | `--dangerously-skip-permissions` |
| opencode | `opencode.json` permissions config |
| Codex CLI | `codex exec --full-auto` |
| Gemini CLI | sandboxing + approval settings |
| Qwen Code | `--yolo` / `-y` / `--approval-mode auto_edit` |
| Aider | `--yes` |
| Goose | `GOOSE_MODE=auto` env var |
| Amp | `amp permissions edit` (configure rules upfront) |
| Cline | `-y` / `--yolo` |
| Plandex | `--full` (Full-Auto mode) + `--apply` + `--skip-menu` |

Plandex has no single "skip everything" flag. Achieving full automation requires
combining `--full`, `--apply`, `--skip-menu`, and `--commit`.

---

## Theme 6 — The skills/extensions dimension

This is a new dimension not covered in the original synthesis. Tools differ significantly
in how they support reusable custom behaviors.

### Skills (markdown instruction files, on-demand)
- **Claude Code** — SKILL.md files in `.claude/skills/`; on-demand loading via `use_skill` tool.
- **Qwen Code** — Inherits Claude Code's skill mechanism (fork).
- **Cline** — Same SKILL.md convention; `.cline/skills/` or `.claude/skills/` (cross-tool compatible).
- **Amp** — "Agent Skills" (instruction files); `.claude/skills/` as a fallback path for compatibility.

All four tools share the same fundamental skill architecture: a markdown file with
YAML frontmatter (`name`, `description`) and a body of instructions. Cline's progressive
loading (metadata always loaded, instructions only when triggered) is the most token-efficient
design.

### Extensions (MCP servers / tool plugins)
- **Goose** — Extensions are MCP servers. Built-ins (`developer`, `computer-controller`),
  plus any stdio or HTTP MCP server. Loaded at session start; can be added mid-session via `/extension`.
- **Cline** — MCP servers configured in `cline.mcp.json`. Cline can also build new MCP servers on demand.
- **Claude Code**, **Codex CLI**, **Gemini CLI**, **Qwen Code** — MCP integration via standard MCP config.
- **Plandex**, **Aider** — No MCP or extension system.

### Toolboxes (shell scripts, lightweight)
- **Amp only** — Toolboxes are shell scripts (or any executable) in a directory. Each executable
  self-describes via `TOOLBOX_ACTION=describe` and executes via `TOOLBOX_ACTION=execute`.
  No server, no JSON-RPC, no manifest. Lowest barrier to custom tooling.

### Recipes / workflows (reusable parameterized pipelines)
- **Goose** — Recipes are YAML files with `title`, `prompt`, `instructions`, and `parameters`.
  Can call sub-recipes. Runnable headlessly. Schedulable with cron via `goose schedule`.
- **Cline** — "Workflows" (scripted slash-command sequences). Less powerful than Goose recipes.
- **Others** — No equivalent.

---

## Points of agreement (updated, 8-tool set)

- All tools work in both interactive and non-interactive modes.
- All tools share the same codebase for both modes — headless is not a separate binary.
- All tools support plain text output as the default headless format.
- All tools require some form of explicit "auto-approve" configuration for CI use.
- Most tools auto-commit or can be configured to; Plandex requires explicit `--commit`.
- All tools that follow Claude Code's architecture (Qwen Code, Cline, Amp) share compatible SKILL.md conventions.

---

## Points of disagreement (updated)

- **JSON output**: Claude Code, Gemini CLI, Qwen Code, Codex CLI, Goose, and Cline all support JSON.
  Aider, Amp, and Plandex do not.
- **HTTP server**: Only opencode exposes a public REST API. Goose has a server but it's internal.
  All others are subprocess-only.
- **Session persistence**: Amp's server-side threads are accessible across devices and teammates.
  Plandex's background streams can survive terminal closure. All others are local-file-based.
- **Skills system**: Claude Code, Qwen Code, Cline, and Amp share a markdown-based skill convention.
  Goose uses a separate YAML recipe system. Plandex and Aider have no skill/extension system.
- **Extension/MCP support**: Goose, Cline, Claude Code have the strongest MCP stories.
  Plandex and Aider have none. Amp has both MCP and the simpler Toolboxes mechanism.
- **Origin**: Qwen Code is a Claude Code fork. Cline is independent but deliberately
  compatible. Goose, Plandex, and Amp are fully independent architectures.
- **Model routing**: Plandex is unique in using different models for different roles within a
  single plan (planner, coder, builder). No other tool in this set does explicit per-role model assignment.

---

## Gaps

- No source covers permission model comparison across tools in depth.
- No source covers startup time and cold-boot costs (MCP initialization overhead is a known pain point).
- Crush (charmbracelet) has no documented headless mode — confirmed absent. See `opencode-crush-cli` trove.
- Amazon Q Developer CLI has a headless mode but is not covered here — primarily an AWS-integration tool.
- IDE-embedded agents (Cursor, Windsurf, Copilot CLI) are not covered — they have a different dual-mode story.
- Amp's headless output format is underdocumented; the absence of `--json` is a notable gap.
- Plandex's scripting story is cobbled together from multiple flags; a dedicated headless mode is an open issue.
