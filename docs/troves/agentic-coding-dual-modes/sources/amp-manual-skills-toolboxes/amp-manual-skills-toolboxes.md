---
source-id: amp-manual-skills-toolboxes
type: web
url: https://ampcode.com/manual
title: "Amp Owner's Manual — Amp"
fetched: 2026-04-07T02:30:07Z
supplemental-urls:
  - https://hamel.dev/notes/coding-agents/amp.html
  - https://www.stackhawk.com/blog/secure-code-with-amp-by-sourcegraph/
---

# Amp — Headless Mode, Skills, and Toolboxes

**Amp** is a coding agent originally built by Sourcegraph. It is now a standalone
company. Available as a VS Code extension and a CLI (`npm install -g @sourcegraph/amp`).

---

## Dual-mode overview

| Mode | Interface | Description |
|---|---|---|
| **Interactive** | VS Code extension or `amp` CLI (TTY) | Full chat UI, thread management, Oracle/subagent support |
| **Headless** | `amp -x "prompt"` or piped input | Non-interactive; exits on completion |

---

## Headless mode

```bash
# Inline prompt
amp -x "what files in this folder are markdown?"

# Pipe input
cat diff.patch | amp -x "summarize these changes"
```

**For CI/CD pipelines:**
```bash
export AMP_API_KEY=<your-token>
amp -x "run tests and fix any failures"
```

The `AMP_API_KEY` env var is the non-interactive authentication path; no OAuth flow.

**Note:** As of mid-2026, Amp is deprecating its VS Code editor extension to focus on
the CLI and web UI. Future headless features will be CLI-first.

---

## Output

Amp does not document a `--json` or `--output-format` flag in the manual.
Headless output is plain text to stdout. Use shell pipelines to process output.

---

## Session continuity

Amp's primary session model is **Threads** — server-side conversation history,
accessible from any device:

- Threads are stored on Sourcegraph's servers.
- Resume by referencing a thread in the UI or CLI.
- **Handoff**: Like Claude Code's `/compact` but more interactive — Amp generates a
  summarized prompt you edit before starting a fresh thread.
- **Message queueing**: Queue messages to be delivered after the agent's current turn
  completes (CLI: `queue` command from the command palette).

---

## Tools and extensibility

### Toolboxes

Toolboxes are Amp's lightweight extension mechanism — simpler than MCP servers.

A toolbox is a directory of executable files. Each executable:
1. When called with `TOOLBOX_ACTION=describe`, prints its description to stdout.
2. When called with `TOOLBOX_ACTION=execute`, performs the tool's action.

```bash
# Example: a toolbox tool that formats code
#!/bin/bash
if [ "$TOOLBOX_ACTION" = "describe" ]; then
  echo "Format the current project using prettier"
elif [ "$TOOLBOX_ACTION" = "execute" ]; then
  npx prettier --write .
fi
```

Amp loads all toolbox executables at startup and presents them to the agent.
No manifest file or schema is required. The tool describes itself via stdout.

**Key difference from MCP**: Toolboxes need no server infrastructure or JSON-RPC.
A shell script or compiled binary is sufficient.

### Agent Skills

Skills in Amp are **instruction files** that tell Amp how to approach specific tasks.
They are similar in concept to Claude Code's SKILL.md files.

Skills can include bundled resources (scripts, templates) in the same directory.
The agent can access these relative to the skill file path.

Skills are referenced from `AGENTS.md` (or `CLAUDE.md` as a fallback). Amp reads
`CLAUDE.md` when no `AGENTS.md` is found, enabling cross-tool compatibility.

### Scoped Instructions

Instruction files (in `AGENTS.md` or referenced skill files) can use YAML front matter
with `globs` to scope guidance to specific file types:

```yaml
---
globs:
  - '**/*.ts'
  - '**/*.tsx'
---
Follow these TypeScript conventions:
- Never use the `any` type
- Use strict mode
```

When Amp reads a file matching the glob, it loads the scoped instructions.
When no matching file is in context, the instructions are ignored.

### MCP Integration

Amp supports MCP servers, following the standard MCP protocol.

### Oracle

Oracle is a specialized reasoning subagent. Ask Amp to "use the oracle" to engage
a more capable (more expensive) model for a specific reasoning step.

### Subagents

Amp can spawn parallel subagents for independent subtasks:
```
Use 3 subagents to convert these CSS files to Tailwind
```

### Librarian

The Librarian is a specialized subagent that aggressively crawls repositories or
documentation sites to gather context for working with unfamiliar codebases.

---

## Auto-approval

Amp's permission system is configured via `amp permissions edit` — opens the
permissions rules in `$EDITOR`. No single "skip all permissions" flag is documented.
In CI/CD environments, configure permissions rules before running headlessly.

---

## Skills dimension summary

| Dimension | Amp |
|---|---|
| Skills/plugin name | "Agent Skills" (instruction files) + "Toolboxes" (self-describing executables) |
| Extension mechanism | Toolboxes (shell scripts with TOOLBOX_ACTION protocol) + MCP |
| Scoped instructions | Yes — YAML glob front matter in markdown files |
| Thread persistence | Server-side threads, sharable across devices and team |
| Special subagents | Oracle (high-reasoning model), Librarian (deep context search), parallel subagents |
| CLAUDE.md compat | Yes — falls back to CLAUDE.md when AGENTS.md is absent |
