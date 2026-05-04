---
source-id: amazon-q-kiro-cli
type: web
url: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-reference.html
title: "Amazon Q / Kiro CLI Command Reference — AWS Docs"
fetched: 2026-04-07T13:54:00Z
supplemental-urls:
  - https://dev.to/aws/the-essential-guide-to-installing-amazon-q-developer-cli-on-linux-headless-and-desktop-3bo7
  - https://github.com/aws/amazon-q-developer-cli/issues/808
notes: "AWS docs page returned empty body; content synthesized from command reference snippets and community sources"
---

# Amazon Q Developer CLI / Kiro CLI — Headless Mode

**Amazon Q Developer CLI** was rebranded to **Kiro CLI** in November 2025.
Functionality is identical across the rename. The underlying binary changed from
`q` to `kiro`; both names appear in documentation. This source covers both.

The CLI is AWS's agentic terminal assistant. Its primary use case is AWS-native
workflows — IAM, CloudFormation, CodeWhisperer lineage, and GitHub-integrated tasks.
It is distinct from the general-purpose coding agents; it is AWS-specific by design.

---

## Dual-mode overview

| Mode | Trigger | Description |
|---|---|---|
| **Interactive** | `q chat` / `kiro chat` (TTY) | Conversational TUI with context retention, multi-turn session |
| **Non-interactive** | `q chat --no-interactive "prompt"` | Single-shot; exits on completion |

---

## Headless mode

```bash
# Basic non-interactive execution
q chat --no-interactive --trust-all-tools "Show me the current directory"

# Session resume
q chat --resume

# Agent invocation
q chat --agent my-agent "Help me with AWS CLI"

# With Kiro CLI (post-rebrand)
kiro chat --no-interactive --trust-all-tools "List running EC2 instances"
```

**Key flags:**

| Flag | Effect |
|---|---|
| `--no-interactive` | Suppress interactive prompts; single-shot execution |
| `--trust-all-tools` | Auto-approve all tool calls (required for CI) |
| `--resume` | Resume the most recent session |
| `--agent <name>` | Use a specific named agent configuration |

---

## Authentication in CI/CD

**Authentication is the primary headless obstacle** for Amazon Q / Kiro CLI.

- Default auth uses an OAuth device flow (browser required).
- IAM role authentication works in AWS-managed environments (EC2, Lambda, CodeBuild)
  that have an appropriate Amazon Q policy attached.
- **No API key or PAT authentication** is supported for direct CI/CD use on external machines.
- Community workaround: complete OAuth once locally, copy session tokens to the CI
  machine alongside `--no-interactive`. The AWS team has noted this is not recommended.
- This is a known gap: GitHub issue #808 explicitly requests `--no-interactive` flag
  for scripting and CI/CD use, filed as a feature request.

---

## Skills / extensions

Amazon Q / Kiro CLI uses a different extensibility model than MCP-based tools:

- **Agents** — predefined workflow configurations selectable via `--agent <name>`.
  Agents encapsulate system prompts, tool sets, and context rules.
- **No MCP integration** documented in public CLI docs.
- **No user-defined skills/extensions** — the skill surface is AWS-internal.

The tool's extensibility is designed around AWS service integrations, not
open-ended tool plugins.

---

## Output

The CLI does not document a `--json` or `--output-format` flag.
Output is plain text to stdout. Machine-readable output requires shell parsing.

---

## Permissions model

- `--trust-all-tools` — bypasses all per-tool approval prompts.
- Without this flag, each tool invocation requires interactive confirmation.
- No fine-grained tool allowlist/denylist flags documented (contrast with
  Continue CLI's `--allow`, `--ask`, `--exclude` system).

---

## Skills dimension summary

| Dimension | Amazon Q / Kiro CLI |
|---|---|
| Skills/plugin name | "Agents" (named workflow configurations) |
| Extension mechanism | AWS-internal; no open MCP or custom plugins |
| Headless maturity | Low — OAuth blocks CI; `--no-interactive` is recent |
| JSON output | Not documented |
| Primary differentiator | Deep AWS-native integrations (IAM, EC2, CodeBuild) |
| Notable gap | CI/CD authentication path is unsupported without IAM roles |
