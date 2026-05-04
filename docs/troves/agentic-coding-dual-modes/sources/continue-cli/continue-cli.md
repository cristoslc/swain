---
source-id: continue-cli
type: web
url: https://docs.continue.dev/guides/cli
title: "How to Use Continue CLI (cn) | Continue Docs"
fetched: 2026-04-07T13:54:13Z
supplemental-urls:
  - https://blog.continue.dev/beyond-code-generation-how-continue-enables-ai-code-review-at-scale
---

# Continue CLI (`cn`) — Headless Mode, Permissions, and Hub Agents

**Continue** is an open-source AI coding platform (Apache 2.0) with IDE extensions
for VS Code and JetBrains plus a standalone CLI (`cn`). The CLI is designed for
scripting, automation, and GitHub CI/CD integration.

---

## Dual-mode overview

| Mode | Trigger | Description |
|---|---|---|
| **Interactive** | `cn` (TTY) | TUI with `@` file mentions and `/` slash commands |
| **Headless** | `cn -p "prompt"` | Outputs final response only; Unix pipeline-friendly |

---

## Headless mode

```bash
# Inline prompt
cn -p "Generate a conventional commit name for the current git changes"

# Pipe input
echo "$(git diff) Generate a conventional commit message" | cn -p > commit-message.txt

# Use a Hub agent configuration
cn --config continuedev/review-bot

# Apply custom rules on top of a Hub agent
cn --config continuedev/default --rule security-standards

# Headless code review from a diff
cn -p "Review this code for security issues" < changes.diff

# Session resume
cn --resume
```

In headless mode (`-p`), `cn` outputs only the final response to stdout —
no UI chrome, no streaming indicator. This follows the Unix philosophy and
makes piping and redirection clean.

---

## Authentication for CI/CD

```bash
export CONTINUE_API_KEY=<your-api-key>
cn -p "Run checks on this diff" < changes.diff
```

`CONTINUE_API_KEY` enables fully non-interactive operation — no login prompt.
Organization-scoped API keys are available for team automations.

---

## Output format

Continue CLI does not document a `--json` or `--output-format` flag.
Output is plain text. The `-p` flag makes it suitable for pipeline use;
the output can be captured and processed by downstream tools.

---

## Session continuity

```bash
cn --resume   # resume the most recent session
```

Sessions are local-file-based. No server-side persistence.

---

## Permissions system

Continue CLI has the most fine-grained per-session permission flags of any tool
in this trove:

```bash
# Always allow the Write tool without asking
cn --allow Write()

# Always ask before running curl
cn --ask Bash(curl*)

# Never use the Fetch tool
cn --exclude Fetch

# Glob patterns supported
cn --allow "shell(npm run test:*)"
```

Permissions accumulate in `~/.continue/permissions.yaml` across sessions.
The tool starts with minimal permissions and promotes approved calls over time.

This design targets the "team CI setup" use case: lock down permissions once in
a config file, commit it, and every CI run is constrained to the approved tool surface.

---

## Configuration

`cn` shares `config.yaml` with the Continue IDE extensions — one config,
all interfaces:

```bash
cn --config continuedev/default-cli-config   # Hub agent
cn --config ~/.continue/config.yaml           # local config
cn --rule nate/spanish                        # add a rule from Mission Control
```

The `/config` slash command and `/model` command are available in interactive mode
to switch configurations without restarting.

---

## GitHub CI Integration (Checks)

Continue's flagship CI feature is **Checks** — agent-as-GitHub-status-check:

```yaml
# .continue/checks/security-review.md
---
name: Security Review
trigger: pull_request
---
Review the changed files for security issues. Flag any SQL injection risks,
unsafe deserialization, or exposed secrets.
```

On every PR, `cn` runs as a GitHub Actions step and posts a green/red
status check with a suggested diff if issues are found. This is the most
direct CI/CD headless integration of any tool in this trove.

---

## Skills / extensions

| Dimension | Continue CLI |
|---|---|
| Skills/plugin name | "Checks" (CI agents), "Rules" (always-on context), "Prompts" (slash-command shortcuts) |
| Extension mechanism | MCP tools (configured in `config.yaml`) |
| Hub agents | Pre-built agents on the Continue Hub (`continuedev/review-bot`, etc.) |
| Tool permissions | Session-level + persistent `permissions.yaml`; glob-pattern allow/ask/exclude |
| Rules | Markdown files with rules that are always included in context |
| Checks | Agent-as-CI-check in `.continue/checks/` — unique among all tools in this set |

---

## Skills dimension summary

| Dimension | Continue |
|---|---|
| Headless trigger | `cn -p "prompt"` |
| CI authentication | `CONTINUE_API_KEY` env var |
| Output format | Plain text only |
| Permission system | `--allow`, `--ask`, `--exclude` with glob patterns; persists to file |
| Unique feature | GitHub Checks — agents as PR status checks |
| Skills/plugin name | Rules + Checks + Hub agents + MCP |
| Claude Code compat | No shared skill convention documented |
