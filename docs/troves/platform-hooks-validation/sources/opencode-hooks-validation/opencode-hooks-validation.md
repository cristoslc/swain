---
source-id: "opencode-hooks-validation"
title: "OpenCode — Plugin Hooks, Permissions, and Validation Mechanisms"
type: web
url: "https://opencode.ai/docs/plugins/"
fetched: 2026-03-22
---

# OpenCode — Plugin Hooks, Permissions, and Validation Mechanisms

## Overview

OpenCode (SST, TypeScript/Bun) provides a plugin-based hook system with `tool.execute.before` and `tool.execute.after` hooks, a config-driven permission system with pattern-based rules across 12+ tool categories, tree-sitter AST parsing for bash command analysis, file integrity locking, MCP support, and an external sandbox plugin. No built-in kernel-level sandboxing. Skills and rules files are advisory. A critical open issue (#5894) means subagent tool calls bypass all plugin hooks.

---

## 1. Plugin Hook System

**Nature: Deterministic (code-enforced) — with critical subagent bypass.**

### Hook Types

| Hook | Trigger | Can Block? |
|---|---|---|
| `tool.execute.before` | Before any tool runs | Yes (throw to block) |
| `tool.execute.after` | After tool completes | No (post-hoc) |
| Event hooks (30+ events) | System events | No (observational) |

### Plugin Structure

```typescript
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input) => {
      if (input.tool === "read" && input.args.filePath.includes(".env")) {
        throw new Error("Cannot read .env files")  // BLOCKS the action
      }
    },
    "tool.execute.after": async (input, output) => {
      // post-execution logging
    },
    event: {
      "session.idle": async (event) => { /* ... */ },
      "file.edited": async (event) => { /* ... */ },
      "permission.asked": async (event) => { /* ... */ },
    }
  }
}
```

### Plugin Loading

- Project-level: `.opencode/plugins/`
- Global: `~/.config/opencode/plugins/`
- npm packages: specified in `opencode.json` `plugin` array, auto-installed via Bun

### CRITICAL: Subagent Hook Bypass

**[Issue #5894](https://github.com/anomalyco/opencode/issues/5894)** (open): `tool.execute.before` hooks fire only for primary agent tool calls. Subagents spawned via the `task` tool bypass all plugin hooks entirely. Any security policy implemented via plugins can be circumvented by the agent delegating work to a subagent. **Unresolved security gap.**

---

## 2. Permission System

**Nature: Deterministic (config-driven, code-enforced).**

### Permission Values

| Value | Behavior |
|---|---|
| `"allow"` | Runs immediately |
| `"ask"` | Suspends session, prompts user (once/always/reject) |
| `"deny"` | Throws error, tool execution fails |

### 12+ Gated Tool Categories

| Key | Controls |
|---|---|
| `edit` | All file modifications |
| `bash` | Shell commands (command-level patterns) |
| `read` | File reading |
| `glob`, `grep`, `list` | File search |
| `webfetch`, `websearch` | Network access |
| `task` | Subagent invocation (glob patterns) |
| `skill` | Skill loading |
| `lsp` | Language server |
| `external_directory` | Paths outside worktree |
| `doom_loop` | Infinite recursion prevention |
| `todoread`, `todowrite` | Task management |

### Pattern-Based Rules

```json
{
  "permission": {
    "edit": {
      "*": "deny",
      "packages/web/src/content/docs/*.mdx": "allow"
    },
    "bash": {
      "*": "allow",
      "git commit *": "deny",
      "rm -rf *": "deny"
    }
  }
}
```

**First matching rule wins** (declaration order).

### Permission Merge Hierarchy

1. Default agent permissions (built into agent definition)
2. Global config
3. Project config
4. Session-level rules (runtime `Session.setPermission()`)

### Agent-Level Defaults

| Agent | edit | bash |
|---|---|---|
| **build** (default) | allow | allow |
| **plan** | ask | ask |
| **explore** (subagent) | deny | allow |
| **general** (subagent) | allow | allow |
| **compaction/title/summary** | deny all | deny all |

---

## 3. Bash Command Analysis (Tree-Sitter)

**Nature: Deterministic (code-enforced).**

Commands parsed via tree-sitter AST before subprocess execution. Commands `cd`, `rm`, `cp`, `mv`, `mkdir`, `touch`, `chmod`, `chown`, `cat` have arguments resolved via `fs.realpath` for external directory detection.

Limitation: only specific commands analyzed; unanalyzed pipes/subshells may escape detection.

---

## 4. File Integrity Locking

**Nature: Deterministic (code-enforced).**

Three-part locking:
- `FileTime.read()` — records mtime/ctime/size state
- `FileTime.assert()` — validates unchanged
- `FileTime.withLock()` — serializes via per-file semaphore

Prevents concurrent modification races.

---

## 5. MCP Support

Full MCP support with local (stdio) and remote (HTTP, OAuth) servers.

```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true
    }
  }
}
```

MCP tools controllable via `tools` config (glob patterns) and `permission` config.

**Caveat:** DeepWiki analysis notes MCP tool permissions may not have the same code-level enforcement depth as built-in tools.

---

## 6. Sandbox / Isolation

**No built-in kernel-level sandboxing.**

### Snapshot System (Recovery, not isolation)

`"snapshot": true` — tracks changes via internal git repository. Enables rollback. Not isolation.

### External Sandbox Plugin

[opencode-sandbox](https://github.com/thisisryanswift/opencode-sandbox) (Apache-2.0):
- Ephemeral containers per session
- Replaces built-in tools with sandbox-aware versions
- Git-based sync (`.gitignore` respected, `.env` files stay on host)
- Transparent path translation
- Providers: Daytona, E2B, Sprites, Docker

### Proposed (Not Implemented)

[Issue #12674](https://github.com/anomalyco/opencode/issues/12674): containerized execution via Docker/Firecracker. Not yet in core.

---

## 7. Configuration

Config file: `opencode.json` (JSONC).

### Merge Hierarchy (lowest to highest)

1. Remote (`.well-known/opencode`)
2. Global (`~/.config/opencode/opencode.json`)
3. Custom (`OPENCODE_CONFIG` env var)
4. Project (`opencode.json`)
5. Inline (`OPENCODE_CONFIG_CONTENT` env var)

Variable substitution: `{env:VAR_NAME}`, `{file:./path}`.

### Skills and Rules (Advisory)

SKILL.md files in `.agents/skills/` or `$HOME/.agents/skills`. Prompt-based, not enforced.

---

## 8. Known Bypass Vectors

1. **Subagent hook bypass** (#5894) — critical
2. **`ctx.extra?.bypassCwdCheck`** — ReadTool respects this context field
3. **AST parsing limits** — only specific commands analyzed
4. **Symlink TOCTOU** — `fs.realpath` resolution could race
5. **Direct `@` mentions** — user invocations bypass `task` permission restrictions (by design)

---

## Summary Matrix

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Plugin hooks (`tool.execute.before`)** | Yes (code) | Yes (throw) | Yes (subagent bypass #5894) |
| **Permission system** | Yes (config+code) | Yes (deny) | No (except subagent gap) |
| **Bash AST analysis** | Yes (code) | Yes (external_directory) | Partially (unanalyzed commands) |
| **File integrity locking** | Yes (code) | Yes (race prevention) | No |
| **Sandbox plugin** | Yes (container) | Yes (tool replacement) | No |
| **Skills / rules files** | No (prompt) | No | Yes |
| **MCP tool permissions** | Partially | Depends | Uncertain enforcement depth |

## Sources

- [OpenCode GitHub (sst/opencode)](https://github.com/sst/opencode)
- [OpenCode Docs — Config](https://opencode.ai/docs/config/)
- [OpenCode Docs — Permissions](https://opencode.ai/docs/permissions/)
- [OpenCode Docs — Tools](https://opencode.ai/docs/tools/)
- [OpenCode Docs — Plugins](https://opencode.ai/docs/plugins/)
- [OpenCode Docs — Custom Tools](https://opencode.ai/docs/custom-tools/)
- [OpenCode Docs — MCP Servers](https://opencode.ai/docs/mcp-servers/)
- [Issue #5894 — Subagent hook bypass](https://github.com/anomalyco/opencode/issues/5894)
- [Issue #12674 — Sandboxing proposal](https://github.com/anomalyco/opencode/issues/12674)
- [opencode-sandbox plugin](https://github.com/thisisryanswift/opencode-sandbox)
