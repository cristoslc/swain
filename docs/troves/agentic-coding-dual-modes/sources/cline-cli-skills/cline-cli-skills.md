---
source-id: cline-cli-skills
type: web
url: https://docs.cline.bot/cline-cli/overview
title: "Cline CLI Overview + Skills | Cline Documentation"
fetched: 2026-04-07T02:30:02Z
supplemental-urls:
  - https://docs.cline.bot/customization/skills
  - https://deepwiki.com/cline/cline
---

# Cline — CLI with Headless Mode and Skills System

**Cline** (formerly Claude Dev) is an open-source coding agent available as a VS Code
extension (Apache 2.0) and a standalone CLI (`npm install -g cline`). The extension has
5M+ developer installs. Both targets share the same core engine.

---

## Dual-mode overview

| Mode | Trigger | Description |
|---|---|---|
| **Interactive** | `cline` (TTY) | Rich TUI with Plan/Act toggle, slash commands, `@file` mentions, syntax-highlighted diffs |
| **Headless** | `cline -y "task"`, `cline --json "task"`, piped input, or redirected output | Automated execution; exits when task completes |

---

## Headless mode

```bash
# Auto-approve all actions (YOLO mode)
cline -y "Run tests and fix any failures"

# Machine-readable JSON output
cline --json "List all TODO comments" | jq '.text'

# Piped input
cat README.md | cline "Summarize this document"

# Chain multiple headless runs
git diff | cline -y "explain these changes" | cline -y "write a commit message"

# Plan mode (analysis without code changes)
cline -p "Review this approach"

# Act mode (direct execution)
cline -a "Implement the changes"
```

**Mode detection table:**

| Invocation | Mode | Reason |
|---|---|---|
| `cline` | Interactive | No arguments, TTY |
| `cline "task"` | Interactive | TTY connected |
| `cline -y "task"` | Headless | YOLO flag forces headless |
| `cline --json "task"` | Headless | JSON flag forces headless |
| `cat file \| cline "task"` | Headless | stdin is piped |
| `cline "task" > output.txt` | Headless | stdout redirected |

**For CI/CD, configure the provider non-interactively:**
```bash
cline auth -p anthropic -k sk-ant-xxxxx -m claude-sonnet-4-5-20250929
```

---

## Output formats

| Format | Flag | Notes |
|---|---|---|
| Plain text | default | Streaming text |
| JSON | `--json` | Structured output for scripting; use with `jq` |

The JSON output schema is not fully documented in public docs; described as "structured output for parsing."

---

## Session continuity

- `cline --continue` or `cline --resume <id>` — resume a prior conversation
- Headless sessions can chain tasks via piped workflows
- No persistent server mode — each invocation starts fresh unless resumed

---

## ACP: Editor integrations

Cline CLI supports the **Agent Client Protocol (ACP)** — run it as a backend for
any ACP-compatible editor:

```bash
# Zed
cline --acp

# Neovim (agentic.nvim)
cline --acp
```

This gives editors full access to Cline's Skills, Hooks, and MCP integrations
without VS Code as a dependency.

---

## Plan/Act modes

Cline has two distinct operational phases:
- **Plan mode**: Analysis and planning without modifying files
- **Act mode**: Execution and code changes

In interactive mode, toggle with `Tab`. In headless mode, use `-p` or `-a`.

---

## Skills system

Skills are **modular instruction sets** stored as SKILL.md files. They extend Cline's
capabilities for specific tasks and load on-demand — not at every invocation.

**Progressive loading:**

| Load level | When | Token cost |
|---|---|---|
| Metadata | Always at startup | ~100 tokens per skill |
| Instructions | When skill matches the user's request | Under 5k tokens |
| Resources | As referenced in instructions | Effectively unlimited |

**Skill structure:**
```
my-skill/
├── SKILL.md           # Required: name, description frontmatter + instructions
├── docs/              # Optional: extended docs, troubleshooting, platform guides
│   └── advanced.md
├── templates/         # Optional: config files, code scaffolding
│   └── config.yaml
└── scripts/           # Optional: validation, data processing, API interactions
    └── validate.py
```

**SKILL.md format:**
```markdown
---
name: aws-cdk-deploy
description: Deploy applications to AWS using CDK. Use when deploying, updating infrastructure, or managing AWS resources.
---

# AWS CDK Deploy

When deploying, follow this workflow: ...
```

**How skills activate:**
1. Cline receives a user message.
2. It scans all loaded skill descriptions (~100 tokens each).
3. If the message matches a skill's description, Cline calls the `use_skill` tool.
4. The full SKILL.md body loads — instructions, and referenced docs/scripts on demand.

**Storage locations:**
- Project skills: `.cline/skills/` (version-controlled; team-shared)
- Global skills: `~/.cline/skills/`
- Also discovered in `.clinerules/skills/` and `.claude/skills/`

Skills are **togglable** — enable/disable per project without deleting.
Scripts in `scripts/` run natively; only their output enters the context window.

**Comparison to Claude Code skills:**
Cline's Skills are structurally identical to Claude Code's SKILL.md convention —
same frontmatter, same directory layout, same `.claude/skills/` discovery path.
This enables shared skill libraries across both tools.

---

## MCP integration

```bash
# Cline can create new MCP servers on demand
"add a tool that..."  # Cline builds and installs an MCP server
```

Cline's MCP support is one of its strongest features. It can:
1. Configure existing MCP servers from `cline.mcp.json`
2. Build and install new MCP servers when the user asks for new capabilities

---

## Auto-approval

```bash
cline -y "task"         # approve all file changes and commands
cline --yolo "task"     # same as -y
```

The `Shift+Tab` shortcut in interactive mode toggles auto-approve for a session.

---

## Skills dimension summary

| Dimension | Cline |
|---|---|
| Skills/plugin name | "Skills" (SKILL.md files, on-demand loading) |
| Extension mechanism | MCP (including self-created servers) + Skills |
| Skill discovery | `.cline/skills/`, `~/.cline/skills/`, `.claude/skills/` |
| Skill activation | Semantic matching against description in frontmatter |
| Skill isolation | Loaded per-request; dormant skills use only ~100 tokens |
| Claude Code compat | `.claude/skills/` is a shared discovery path |
| Additional customization | Hooks (lifecycle triggers), Workflows (scripted sequences), Rules (always-on context) |
