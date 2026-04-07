---
trove: agentic-coding-dual-modes
synthesized: 2026-04-07
sources: 4
related-troves:
  - opencode-crush-cli (opencode serve/run; Crush has no server mode)
  - claude-code-remote-interaction (claude -p; remote control; Agent SDK)
---

# Agentic coding environments — headful and headless modes

## Overview of the landscape (6 tools)

| Tool | Headful mode | Headless trigger | Output format | HTTP server? |
|---|---|---|---|---|
| **Claude Code** | Interactive TUI | `claude -p "prompt"` | text, JSON, stream-JSON | No (Agent SDK for programmatic use) |
| **opencode** | TUI (client/server) | `opencode serve` + `opencode run` | REST API, JSON | **Yes** — full HTTP API |
| **Codex CLI** | Interactive TUI | `codex exec "prompt"` | text, JSONL | App Server + MCP Server mode |
| **Gemini CLI** | Interactive TUI | `gemini -p "prompt"` or non-TTY | text, JSON, stream-JSON (JSONL) | No (ACP mode for IDE) |
| **Qwen Code** | Interactive TUI | `qwen -p "prompt"` or non-TTY | text, JSON, stream-JSON | No (TypeScript SDK for embedding) |
| **Aider** | REPL terminal | `aider --message "..."` + `--yes` | stdout text | No (Python API only) |

*Coverage notes: Claude Code and opencode are covered in depth in the related troves `claude-code-remote-interaction` and `opencode-crush-cli`. This trove covers Codex CLI, Gemini CLI, Aider, and Qwen Code.*

---

## Theme 1 — The `-p` / `--prompt` flag is the universal headless trigger

Every Claude Code derivative (Claude Code, Gemini CLI, Qwen Code) uses `-p` / `--prompt` to trigger headless mode. Codex uses `codex exec`. Aider uses `--message`. The pattern is consistent: supply the prompt on the command line, suppress interactive UI, print result to stdout, exit.

This matters for automation: any of these tools can be called from a shell script the same way.

```bash
claude -p "review src/auth.py"        # Claude Code
gemini -p "review src/auth.py"         # Gemini CLI
qwen -p "review src/auth.py"           # Qwen Code
codex exec "review src/auth.py"        # Codex CLI
aider --message "review src/auth.py" src/auth.py --yes  # Aider
opencode run "review src/auth.py"      # opencode
```

---

## Theme 2 — JSON / stream-JSON output is the machine-readable standard

Claude Code, Gemini CLI, Qwen Code, and Codex CLI all offer structured JSON output for automation. The schemas differ but the shape is similar:

| Tool | Flag | Format |
|---|---|---|
| Claude Code | `--output-format json` | JSON array of message objects |
| Claude Code | `--output-format stream-json` | JSONL events |
| Gemini CLI | `--output-format json` | Single JSON object (`response`, `stats`) |
| Gemini CLI | `--output-format stream-json` | JSONL events (`init`, `message`, `tool_use`, `tool_result`, `result`) |
| Qwen Code | `--output-format json` | JSON array (buffered) |
| Qwen Code | `--output-format stream-json` | JSONL (streaming) |
| Codex CLI | `--json` | JSONL events (`thread.started`, `turn.*`, `item.*`) |

Aider outputs plain text only — no machine-readable format. Use its Python API for structured access.

---

## Theme 3 — Three architectures for "server mode"

There is no single pattern for how these tools handle persistent or remote execution. Three distinct approaches exist:

### A. CLI-flag headless (pure subprocess model)
Claude Code, Gemini CLI, Qwen Code, Aider — start a fresh process per run. No persistent server. State is carried via `--continue` / `--resume` session IDs backed by local files. Simple to orchestrate: just call the binary in a loop.

### B. HTTP server (opencode only)
opencode decouples its TUI from its server completely. `opencode serve` runs a standalone HTTP server with a full REST API. Multiple clients can connect. The `/tui` endpoint lets an external process programmatically drive the TUI. This is architecturally the most powerful for multi-client and remote scenarios.

### C. App Server + MCP Server (Codex CLI)
Codex has an `app-server` mode (runs a server for the Codex desktop app) and can run as an MCP server, allowing orchestration via the Agents SDK. This is a middle ground — not a general HTTP API, but a structured server interface for specific integration patterns.

---

## Theme 4 — Session continuity in headless runs

Tools differ on how well they support multi-step headless workflows:

- **opencode**: `opencode run --attach http://localhost:4096` reuses a running server; avoids MCP cold-boot on every run.
- **Codex CLI**: `codex exec resume --last` or `codex exec resume <SESSION_ID>` chains runs.
- **Claude Code**: `claude --continue` or `claude --resume <id>` continues prior sessions.
- **Qwen Code**: `qwen --continue` or `qwen --resume <id>` restores full conversation history, tool outputs, and compression checkpoints.
- **Gemini CLI**: Session management and checkpointing supported; specifics in related docs.
- **Aider**: No session resumption — each `--message` run is independent. Multi-step scripting requires the Python API with a persistent `Coder` object.

---

## Theme 5 — Auto-approval is mandatory for unattended automation

All tools require some form of "yes to everything" flag for CI use. Without it, interactive prompts block execution.

| Tool | Auto-approve flag |
|---|---|
| Claude Code | `--dangerously-skip-permissions` |
| opencode | permissions config in `opencode.json` |
| Codex CLI | `codex exec --full-auto` |
| Gemini CLI | sandboxing + approval settings |
| Qwen Code | `--yolo` / `-y` or `--approval-mode auto_edit` |
| Aider | `--yes` |

---

## Points of agreement

- All tools work in both interactive and non-interactive modes.
- All tools use the same codebase for both modes — headless is not a separate binary.
- All tools support plain text output as the default headless format.
- All tools auto-commit changes (or can be configured to) during headless runs.
- All tools require a git repository (or can be configured to bypass that check).

---

## Points of disagreement

- **HTTP server**: Only opencode exposes a persistent HTTP REST API. All others are subprocess-only.
- **Session persistence**: Qwen Code and Claude Code have the most complete session-resume stories for multi-step headless workflows. Aider has the weakest.
- **Structured output**: Aider has no JSON output mode. All others do.
- **Origin**: Qwen Code is explicitly a Claude Code fork and mirrors its headless design closely. Gemini CLI and opencode are independent reimplementations. Aider predates them all.

---

## Gaps

- No source covers permission model comparison across tools (what each allows/blocks headlessly).
- No source covers performance characteristics (startup time, cold-boot cost, MCP initialization overhead).
- Crush (charmbracelet) has no documented headless mode — confirmed absent. See `opencode-crush-cli` trove.
- This trove does not cover IDE-embedded agents (Cursor, Cline, Windsurf) which have a different dual-mode story (GUI vs. background agent mode).
