---
source-id: "qwen-code-headless-docs"
title: "Headless Mode | Qwen Code Docs"
type: web
url: "https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/"
fetched: 2026-04-07T02:08:17Z
hash: "0169e8b209d22dea8469d962a62bbb444f95767c6e27e9e83f890071d1a3f6fa"
---

# Headless Mode — Qwen Code

Headless mode allows running Qwen Code programmatically from scripts and automation tools without any interactive UI. Ideal for scripting, CI/CD pipelines, and building AI-powered tools.

## Triggering headless mode

Use the `--prompt` / `-p` flag:

```bash
qwen --prompt "What is machine learning?"
qwen -p "What is machine learning?"
```

Or pipe input via stdin (auto-detected as non-TTY):

```bash
echo "Explain this code" | qwen
cat README.md | qwen --prompt "Summarize this documentation"
```

## Session continuity in headless mode

Headless sessions can resume previous context:

```bash
# Continue the most recent session for this project
qwen --continue -p "Run the tests again and summarize failures"

# Resume a specific session ID
qwen --resume 123e4567-e89b-12d3-a456-426614174000 -p "Apply the follow-up refactor"
```

Session data is project-scoped JSONL under `~/.qwen/projects/<sanitized-cwd>/chats`. Resuming restores conversation history, tool outputs, and chat-compression checkpoints.

## Output formats

### Text (default)

Standard human-readable output.

### JSON

Buffers all messages and outputs as a JSON array when the session completes. Includes `system`, `assistant`, and `result` message types.

```bash
qwen -p "What is the capital of France?" --output-format json
```

### Stream-JSON (JSONL)

Emits JSON messages immediately as they occur:

```bash
qwen -p "Explain TypeScript" --output-format stream-json
```

Add `--include-partial-messages` for real-time partial content events (for UI updates):

```bash
qwen -p "Write a Python script" --output-format stream-json --include-partial-messages
```

### Input format

`--input-format stream-json` enables bidirectional JSON message protocol via stdin (for SDK integration, currently under construction).

## Key CLI options

| Option | Description |
|---|---|
| `--prompt` / `-p` | Trigger headless mode |
| `--output-format` / `-o` | `text`, `json`, or `stream-json` |
| `--input-format` | `text` or `stream-json` |
| `--include-partial-messages` | Stream partial content in stream-json mode |
| `--yolo` / `-y` | Auto-approve all actions |
| `--approval-mode` | Set approval mode (`auto_edit`, etc.) |
| `--all-files` / `-a` | Include all files in context |
| `--include-directories` | Additional directories for context |
| `--continue` | Resume most recent session for this project |
| `--resume [sessionId]` | Resume a specific session |

## Automation examples

```bash
# Code review
cat src/auth.py | qwen -p "Review for security issues" > review.txt

# Commit message generation
git diff --cached | qwen -p "Write a concise commit message" --output-format json | jq -r '.response'

# Batch analysis
for file in src/*.py; do
    cat "$file" | qwen -p "Find potential bugs" --output-format json \
      | jq -r '.response' > "reports/$(basename "$file").txt"
done

# PR review
git diff origin/main...HEAD | qwen -p "Review for bugs and quality" > pr-review.txt

# Release notes
git log --oneline v1.0.0..HEAD | qwen -p "Generate release notes" --output-format json | jq -r '.response'
```

## Architecture notes

Qwen Code is a Claude Code derivative (fork). Its headless mode closely mirrors Claude Code's `-p` flag design. Like Claude Code (and unlike opencode), it does not expose an HTTP server. Scripting is purely via CLI flags or SDK.

The TypeScript SDK supports bidirectional stream-json communication for programmatic embedding. A Java SDK (alpha) is also available.
