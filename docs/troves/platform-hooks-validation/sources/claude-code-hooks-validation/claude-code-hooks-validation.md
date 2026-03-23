---
source-id: "claude-code-hooks-validation"
title: "Claude Code — Hooks, Permissions, and Validation Mechanisms"
type: web
url: "https://code.claude.com/docs/en/hooks"
fetched: 2026-03-22
---

# Claude Code — Hooks, Permissions, and Validation Mechanisms

## Overview

Claude Code (Anthropic) provides a layered enforcement architecture: shell/HTTP/prompt/agent hooks at 24 lifecycle events, a hierarchical permission system with deny-always-wins semantics, OS-level sandboxing (bubblewrap on Linux, seatbelt on macOS), managed settings for enterprise lockdown, and advisory instruction files (CLAUDE.md / AGENTS.md). MCP tools are subject to the same permission and hook enforcement as built-in tools.

---

## 1. Hooks System

**Nature: Deterministic (code-enforced).** Hooks are shell commands, HTTP endpoints, prompt evaluations, or agent callbacks that execute real code outside the model's control flow.

### 24 Hook Events

| Event | Can Block? (exit code 2) | Matcher target |
|---|---|---|
| **PreToolUse** | Yes — blocks tool call | Tool name (regex) |
| **PostToolUse** | No — tool already ran | Tool name |
| **PostToolUseFailure** | No | Tool name |
| **PermissionRequest** | Yes — denies permission | Tool name |
| **UserPromptSubmit** | Yes — blocks prompt, erases from context | No matcher (always fires) |
| **Stop** | Yes — prevents stop, continues conversation | No matcher |
| **SubagentStart** | No (observability only) | Agent type |
| **SubagentStop** | Yes — prevents stop | Agent type |
| **SessionStart** | No | startup\|resume\|clear\|compact |
| **SessionEnd** | No | Exit reason |
| **Notification** | No | Notification type |
| **TeammateIdle** | Yes — teammate continues | No matcher |
| **TaskCompleted** | Yes — task not marked complete | No matcher |
| **ConfigChange** | Yes (except policy_settings) | Config source |
| **PreCompact** | No | manual\|auto |
| **PostCompact** | No | manual\|auto |
| **WorktreeCreate** | Yes — creation fails | No matcher |
| **WorktreeRemove** | No | No matcher |
| **Elicitation** | Yes | MCP server name |
| **ElicitationResult** | Yes | MCP server name |
| **InstructionsLoaded** | No | Load reason |
| **StopFailure** | No | Error type |

### Hook Handler Types

- `command` — shell script, receives JSON on stdin
- `http` — POST to URL
- `prompt` — single-turn LLM eval
- `agent` — spawns subagent with tool access

### Exit Code Semantics

- `0` — Success; stdout parsed as JSON for structured decision/reason
- `2` — Blocking error; target action aborted where supported
- Other — Non-blocking error; stderr shown in verbose mode

### PreToolUse — Key Enforcement Hook

Receives `tool_name`, `tool_input` (full arguments), and `tool_use_id`. Can return:

- `permissionDecision: "deny"` — blocks the tool call
- `permissionDecision: "allow"` — auto-approves
- `permissionDecision: "ask"` — forces user confirmation
- `updatedInput: {...}` — modifies tool arguments before execution (requires `permissionDecision: "allow"`)

### Priority When Multiple Hooks Fire

**deny > ask > allow.** If any hook returns deny, the operation is blocked regardless of other hooks.

### Configuration Locations

`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, managed policy settings, plugin `hooks.json`, skill/agent frontmatter.

### Can the agent bypass hooks?

No. Hooks run in the runtime outside the model's control. However, hooks configured at user/project level can be disabled by `disableAllHooks: true` or overridden by `allowManagedHooksOnly: true` in managed settings.

---

## 2. Permission System

**Nature: Deterministic (code-enforced).**

### Evaluation Order (first match wins)

1. **Hooks** run first — can allow, deny, or pass through
2. **Deny rules** checked — **even `bypassPermissions` cannot override deny rules**
3. **Permission mode** applied
4. **Allow rules** checked
5. **`canUseTool` callback** (SDK only)

### Rule Syntax

`Tool` or `Tool(specifier)` with glob wildcards:

- `Bash(npm run *)` — matches commands starting with `npm run`
- `Read(./.env)` — matches reading `.env`
- `Edit(/src/**/*.ts)` — matches editing TypeScript files under src
- `WebFetch(domain:example.com)` — matches fetch to domain
- `mcp__puppeteer__puppeteer_navigate` — matches specific MCP tool

### Permission Modes

| Mode | Behavior |
|---|---|
| `default` | Prompts on first use |
| `acceptEdits` | Auto-approves file edits |
| `plan` | No tool execution at all |
| `dontAsk` | Denies anything not pre-approved (SDK only) |
| `bypassPermissions` | Approves everything except deny-listed tools |

### Key Security Properties

- Deny rules **always win**, even in `bypassPermissions` mode
- Bash rule matching is shell-operator-aware: `Bash(safe-cmd *)` won't match `safe-cmd && other-cmd`
- Read/Edit deny rules only apply to Claude's built-in file tools, NOT to Bash subprocesses (use sandbox for OS-level enforcement)
- Settings precedence: Managed (highest) > CLI args > Local > Project > User (lowest)

---

## 3. Sandboxing (OS-Level)

**Nature: Deterministic (OS-enforced).**

Two isolation boundaries:
1. **Filesystem isolation** — restricts write/read access to designated directories; covers all subprocesses
2. **Network isolation** — enforces approved server connections only via proxy server outside the sandbox

Key settings:
- `sandbox.enabled: true`
- `sandbox.autoAllowBashIfSandboxed: true`
- `sandbox.allowUnsandboxedCommands: false` — disables the `dangerouslyDisableSandbox` escape hatch
- `sandbox.filesystem.allowWrite/denyWrite/allowRead/denyRead` — path-level controls
- `sandbox.network.allowedDomains` — domain allowlist
- `sandbox.network.allowManagedDomainsOnly` — restricts to managed-settings domains only

Sandbox reduces permission prompts by 84% (Anthropic testing).

---

## 4. Managed Settings (Enterprise)

**Nature: Deterministic (code-enforced, cannot be overridden).**

Location: `/Library/Application Support/ClaudeCode/managed-settings.json` (macOS), registry (Windows), or server-managed.

Can enforce:
- `allowManagedHooksOnly` — only managed hooks run
- `allowManagedPermissionRulesOnly` — only managed permission rules apply
- `allowManagedMcpServersOnly` — only managed MCP servers available
- `disableBypassPermissionsMode` — prevents bypass mode
- `sandbox.network.allowManagedDomainsOnly`
- `sandbox.filesystem.allowManagedReadPathsOnly`

---

## 5. CLAUDE.md / AGENTS.md

**Nature: Advisory (prompt-based).**

Injected into system prompt. Cannot block tool execution, deny permissions, or enforce constraints deterministically. The model may deviate from instructions.

---

## 6. MCP Integration

MCP tools are named `mcp__<server>__<tool>` and are subject to the **same permission system and hooks** as built-in tools.

- Permission rules can target MCP tools: `mcp__puppeteer` (all), `mcp__puppeteer__puppeteer_navigate` (specific)
- PreToolUse hooks can match MCP tools via regex
- Managed settings control MCP availability: `allowedMcpServers`, `deniedMcpServers`, `allowManagedMcpServersOnly`
- Elicitation events are hookable and blockable

---

## Summary Matrix

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Hooks (PreToolUse)** | Yes (code) | Yes | No |
| **Permission rules (deny)** | Yes (code) | Yes (deny always wins) | No (Read deny circumventable via Bash without sandbox) |
| **Sandbox** | Yes (OS kernel) | Yes | No |
| **Permission modes** | Yes (code) | Yes | No |
| **Managed settings** | Yes (code) | Yes (cannot be overridden) | No |
| **CLAUDE.md / AGENTS.md** | No (prompt) | No | Yes |
| **MCP server-side logic** | Depends on impl | Depends | No (if server enforces) |

## Sources

- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Agent SDK hooks guide](https://platform.claude.com/docs/en/agent-sdk/hooks)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Configure permissions (SDK)](https://platform.claude.com/docs/en/agent-sdk/permissions)
- [Configure permissions (Claude Code)](https://code.claude.com/docs/en/permissions)
- [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [Claude Code plugins](https://claude.com/blog/claude-code-plugins)
- [MCP in Claude Code](https://code.claude.com/docs/en/mcp)
