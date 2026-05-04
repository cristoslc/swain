---
source-id: "codex-noninteractive-docs"
title: "Non-interactive mode | Codex CLI — OpenAI Developers"
type: web
url: "https://developers.openai.com/codex/noninteractive"
fetched: 2026-04-07T02:08:17Z
hash: "319576619977e0d302f5853191d626bad403c8948a01a48d771ef90d3f125e12"
---

# Non-interactive mode — Codex CLI

Non-interactive mode lets you run Codex from scripts (CI jobs, pipelines) without opening the interactive TUI. Invoked with `codex exec`.

## When to use `codex exec`

- Run as part of a pipeline (CI, pre-merge checks, scheduled jobs).
- Produce output that can be piped into other tools.
- Run with explicit, pre-set sandbox and approval settings.

## Basic usage

```bash
codex exec "summarize the repository structure and list the top 5 risky areas"
```

Codex streams progress to `stderr` and prints only the final agent message to `stdout`:

```bash
codex exec "generate release notes for the last 10 commits" | tee release-notes.md
```

Use `--ephemeral` to avoid persisting session rollout files:

```bash
codex exec --ephemeral "triage this repository and suggest next steps"
```

## Permissions and safety

By default, `codex exec` runs in a **read-only sandbox**.

- Allow edits: `codex exec --full-auto "<task>"`
- Allow broader access: `codex exec --sandbox danger-full-access "<task>"`

## Machine-readable output (JSON Lines)

```bash
codex exec --json "summarize the repo structure" | jq
```

`--json` makes `stdout` a JSONL stream. Event types: `thread.started`, `turn.started`, `turn.completed`, `turn.failed`, `item.*`, `error`.

Sample stream:
```json
{"type":"thread.started","thread_id":"..."}
{"type":"turn.started"}
{"type":"item.started","item":{"id":"item_1","type":"command_execution","command":"bash -lc ls","status":"in_progress"}}
{"type":"item.completed","item":{"id":"item_3","type":"agent_message","text":"Repo contains docs, sdk, and examples directories."}}
{"type":"turn.completed","usage":{"input_tokens":24763,"cached_input_tokens":24448,"output_tokens":122}}
```

Write only the final message to a file: `-o <path>` / `--output-last-message <path>`.

## Structured output with schema

```bash
codex exec "Extract project metadata" \
  --output-schema ./schema.json \
  -o ./project-metadata.json
```

Output conforms to the schema, safe for downstream parsing.

## Authentication in CI

- Set `CODEX_API_KEY` as a secret environment variable (recommended).
- `CODEX_API_KEY` is only supported in `codex exec`.

```bash
CODEX_API_KEY=<api-key> codex exec --json "triage open bug reports"
```

## Resuming a non-interactive session

```bash
codex exec "review the change for race conditions"
codex exec resume --last "fix the race conditions you found"
# or with specific session:
codex exec resume <SESSION_ID>
```

## Git repository required

Codex requires a git repo to prevent destructive changes. Override with `codex exec --skip-git-repo-check`.

## Example: CI auto-fix workflow (GitHub Actions)

```yaml
name: Codex auto-fix on CI failure
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
jobs:
  auto-fix:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Codex
        run: npm i -g @openai/codex
      - name: Authenticate Codex
        run: codex login --api-key "$OPENAI_API_KEY"
      - name: Run Codex
        run: |
          codex exec --full-auto --sandbox workspace-write \
            "Read the repository, run the test suite, identify the minimal change needed to make all tests pass, implement only that change, and stop."
      - name: Verify tests
        run: npm test --silent
      - name: Create pull request
        if: success()
        uses: peter-evans/create-pull-request@v6
```

## Architecture notes

Codex also exposes an **App Server** mode (`codex app-server`) and can run as an **MCP server** (`codex mcp-server`), allowing orchestration via the Agents SDK. These are the "server" counterparts to the interactive TUI and CLI modes.
