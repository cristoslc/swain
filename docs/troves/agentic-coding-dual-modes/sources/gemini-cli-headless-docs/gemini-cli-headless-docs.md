---
source-id: "gemini-cli-headless-docs"
title: "Headless mode reference | Gemini CLI"
type: web
url: "https://geminicli.com/docs/cli/headless/"
fetched: 2026-04-07T02:08:17Z
hash: "770937a761a0e089128519e6e70091e5f77ae8183a54e8fad79135cbb4b4b9f8"
---

# Headless mode reference — Gemini CLI

Headless mode provides a programmatic interface to Gemini CLI, returning structured text or JSON output without an interactive terminal UI.

## How it triggers

Headless mode activates when:
- The CLI is run in a **non-TTY environment** (e.g., piped in a script), OR
- The `-p` / `--prompt` flag is passed with a query.

```bash
gemini -p "Explain the repository structure"
```

## Output formats

Specify with `--output-format`:

### JSON output

Returns a single JSON object:
- `response`: (string) The model's final answer.
- `stats`: (object) Token usage and API latency metrics.
- `error`: (object, optional) Error details if the request failed.

### Streaming JSON (JSONL)

Returns a stream of newline-delimited JSON events:

| Event type | Description |
|---|---|
| `init` | Session metadata (session ID, model) |
| `message` | User and assistant message chunks |
| `tool_use` | Tool call requests with arguments |
| `tool_result` | Output from executed tools |
| `error` | Non-fatal warnings and system errors |
| `result` | Final outcome with aggregated stats and per-model token usage |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | General error or API failure |
| `42` | Input error (invalid prompt or arguments) |
| `53` | Turn limit exceeded |

## Additional notes

- Gemini CLI also supports **ACP mode** (`gemini acp`) for IDE integration via the Agent Client Protocol.
- **Remote subagents** are supported — the CLI can delegate tasks to remote agent instances.
- **Checkpointing** allows resuming interrupted sessions.
- **Plan mode** (also available in headless context) restricts the agent to analysis before executing changes.
- Free tier: Gemini 2.5 Pro available with a personal Google account.
