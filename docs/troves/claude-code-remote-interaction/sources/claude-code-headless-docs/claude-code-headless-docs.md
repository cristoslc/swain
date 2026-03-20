---
source-id: "claude-code-headless-docs"
title: "Run Claude Code programmatically — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/headless"
fetched: 2026-03-20T00:00:00Z
hash: "eac7a3c8e1853c7cd4ce4dd6d207f2418d1c30fea48bd66c75ecb978d5277efe"
---

# Run Claude Code programmatically

Use the Agent SDK to run Claude Code programmatically from the CLI, Python, or TypeScript.

The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code. Available as a CLI for scripts and CI/CD, or as Python and TypeScript packages for full programmatic control.

The CLI was previously called "headless mode." The `-p` flag and all CLI options work the same way.

## Basic usage

Add the `-p` (or `--print`) flag to run non-interactively:

```bash
claude -p "Find and fix the bug in auth.py" --allowedTools "Read,Edit,Bash"
```

All CLI options work with `-p`, including:
- `--continue` for continuing conversations
- `--allowedTools` for auto-approving tools
- `--output-format` for structured output

## Structured output

Use `--output-format` to control response format:

- `text` (default): plain text
- `json`: structured JSON with result, session ID, metadata
- `stream-json`: newline-delimited JSON for real-time streaming

```bash
claude -p "Summarize this project" --output-format json
```

For schema-conformant output, combine `--output-format json` with `--json-schema`:

```bash
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'
```

## Streaming

Use `--output-format stream-json` with `--verbose` and `--include-partial-messages` for token-level streaming:

```bash
claude -p "Explain recursion" --output-format stream-json --verbose --include-partial-messages
```

When an API request fails with a retryable error, Claude Code emits a `system/api_retry` event before retrying.

## Auto-approve tools

```bash
claude -p "Run tests and fix failures" --allowedTools "Bash,Read,Edit"
```

## Continue conversations

```bash
# First request
claude -p "Review this codebase for performance issues"

# Continue most recent conversation
claude -p "Now focus on database queries" --continue

# Resume a specific session
session_id=$(claude -p "Start a review" --output-format json | jq -r '.session_id')
claude -p "Continue that review" --resume "$session_id"
```

## Customize system prompt

```bash
gh pr diff "$1" | claude -p \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities." \
  --output-format json
```

## Key capabilities for automation

- Non-interactive execution via `-p` flag
- Structured JSON output with optional schema conformance
- Tool auto-approval for unattended operation
- Session continuation across invocations
- Stream processing for real-time output
- System prompt customization for specialized agents
