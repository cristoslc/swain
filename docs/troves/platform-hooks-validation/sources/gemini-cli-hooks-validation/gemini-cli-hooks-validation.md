---
source-id: "gemini-cli-hooks-validation"
title: "Gemini CLI — Hooks, Policy Engine, and Validation Mechanisms"
type: web
url: "https://geminicli.com/docs/hooks/"
fetched: 2026-03-22
---

# Gemini CLI — Hooks, Policy Engine, and Validation Mechanisms

## Overview

Gemini CLI (Google, Apache 2.0) provides the richest deterministic enforcement surface of any platform studied: a synchronous hook system with 10+ events, a TOML-based policy engine with five priority tiers including OS-owned admin policies, multi-platform sandboxing (seatbelt, Docker, gVisor, LXC), approval mode gating, and an extensions system that bundles hooks + policies + MCP servers. GEMINI.md context files are advisory.

---

## 1. Hook System

**Nature: Deterministic (code-enforced).** Hooks are external scripts (bash, Python, Node.js, etc.) executed synchronously in the agent loop. The CLI waits for all matching hooks to complete before continuing. Enabled by default since v0.26.0 (Jan 2026).

### 10+ Hook Events

| Event | Trigger | Can Block? | Mechanism |
|---|---|---|---|
| `SessionStart` | Session init, resume, `/clear` | No (advisory) | Injects context via `additionalContext` |
| `SessionEnd` | CLI exit, session clear | No (best-effort) | Observability only |
| `BeforeAgent` | After user prompt, before planning | **Yes** | `decision: "deny"` or exit code 2 |
| `AfterAgent` | After final model response | **Yes** | `decision: "deny"` triggers retry with `reason` as correction prompt |
| `BeforeModel` | Before LLM API request | **Yes** | Exit code 2 aborts turn; can mock response |
| `AfterModel` | After LLM response | **Yes** | Exit code 2 discards response; can replace |
| `BeforeToolSelection` | Before tool decision | **Yes (filter)** | Can set `toolConfig.mode` to `NONE` or whitelist `allowedFunctionNames` |
| `BeforeTool` | Before tool execution | **Yes** | `decision: "deny"` or exit code 2 blocks; can rewrite `tool_input` |
| `AfterTool` | After tool execution | **Yes** | `decision: "deny"` hides output from agent; can chain tools via `tailToolCallRequest` |
| `PreCompress` | Before context compression | No (async) | Observability |
| `Notification` | System alerts | No | Observability only |

### Exit Code Semantics

- `0` — Success; stdout parsed as JSON
- `2` — Emergency brake; action aborted; stderr becomes rejection reason
- Other — Warning; non-fatal, CLI proceeds with original parameters

### Configuration

```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "write_file|replace",
        "hooks": [
          {
            "name": "security-check",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/security.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

Environment variables: `GEMINI_PROJECT_DIR`, `GEMINI_SESSION_ID`, `GEMINI_CWD`.

### Hook Fingerprinting (Security)

Project-level hooks are fingerprinted — if a hook's name or command changes, it is treated as new/untrusted and the user is warned before execution. **Code-enforced** security gate.

---

## 2. Policy Engine

**Nature: Deterministic (code-enforced, with OS-level admin tier).**

TOML-based rule system that evaluates every tool call before execution.

### Five-Tier Priority System

| Tier | Base Value | Source |
|---|---|---|
| Default | 1 | Built-in CLI policies |
| Extension | 2 | Extension-defined policies |
| Workspace | 3 | `.gemini/policies/*.toml` |
| User | 4 | `~/.gemini/policies/*.toml` |
| Admin | 5 | System directories (root-owned) |

Formula: `final_priority = tier_base + (toml_priority / 1000)`. Admin tier always wins.

### Rule Schema

```toml
[[rule]]
toolName = "run_shell_command"
mcpName = "my-server"
toolAnnotations = { destructiveHint = true }
argsPattern = '"command":"(git|npm)'
commandPrefix = "git"
commandRegex = "git (commit|push)"
decision = "allow"   # allow | deny | ask_user
priority = 100
deny_message = "Custom message"
modes = ["autoEdit"]
interactive = true
subagent = "generalist"
```

### Decisions

- `allow` — auto-execute
- `deny` — block; global deny also removes tool from model's available set
- `ask_user` — prompt; treated as `deny` in non-interactive mode

### Admin Tier Enforcement (OS-level)

- Admin policy directories must be owned by root (UID 0) with no group/other write access
- Windows: standard users must lack Write/Modify ACLs
- Failed ownership checks cause Admin tier to be **ignored entirely** (prevents privilege escalation)
- **Policy Integrity Manager**: SHA-256 hash of all active policy files (paths + content); detects unauthorized modifications

### Known Issue

[Issue #20469](https://github.com/google-gemini/gemini-cli/issues/20469): policy rules may be ignored in non-interactive mode with `--approval-mode auto_edit`.

---

## 3. Permission/Sandbox System

**Nature: Deterministic (OS-enforced).**

### Approval Modes

- `default` — Prompts user for each tool call
- `auto_edit` — Auto-approves edit tools; prompts for shell commands
- `plan` — Read-only mode (experimental); write tools denied
- `yolo` — Auto-approves all (enables sandbox by default)

### Sandbox Modes

| Platform | Technology | Isolation Level |
|---|---|---|
| macOS | `sandbox-exec` (Seatbelt) | 6 profiles from `permissive-open` to `strict-proxied` |
| Linux | Docker/Podman | Container-based process isolation |
| Linux | gVisor/runsc | User-space kernel; intercepts all syscalls |
| Linux | LXC/LXD (experimental) | Full-system container |
| Windows | `icacls` Low Mandatory Level | Persistent filesystem ACLs |

Custom profiles supported: `.gemini/sandbox-macos-custom.sb` (Seatbelt), `.gemini/sandbox.Dockerfile` (Docker).

### Enforcement Settings

- `security.disableYoloMode` — prevents `--yolo` even if flagged (code-enforced)
- `security.disableAlwaysAllow` — removes "Always allow" dialog option (code-enforced)
- `tools.exclude` — disable specific tools entirely (code-enforced, removed from model's set)

---

## 4. Extensions System

Extensions bundle: MCP servers, context files, hooks, custom commands, themes, sub-agents, agent skills, and excluded tools.

Install via: `gemini extensions install <github-url>`

Extensions can:
- Define policy rules (Extension tier, base priority 2)
- Bundle hooks that intercept agent actions
- Exclude built-in tools
- Provide MCP servers with approval settings

Extension-bundled hooks and policies are code-enforced. Extension-bundled context files are advisory.

---

## 5. MCP Support

Full MCP support with three transports: Stdio, SSE, Streamable HTTP.

- Default: user confirmation required per tool call
- `trust: true` bypasses confirmation (code-enforced skip)
- `includeTools` / `excludeTools` per server; `excludeTools` takes precedence
- MCP tools subject to the same policy engine as built-in tools
- Environment sanitization: CLI redacts `*TOKEN*`, `*SECRET*`, `*PASSWORD*`

---

## 6. GEMINI.md Context Files

**Nature: Advisory (prompt-based).**

Hierarchical: `~/.gemini/GEMINI.md` (global) → project root → subdirectories. Supports `@path/to/file.md` imports and `$VAR_NAME` substitution. Concatenated into system prompt. Cannot enforce actions.

---

## Summary Matrix

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Hooks (BeforeTool, BeforeAgent)** | Yes (code) | Yes | No |
| **Policy Engine (TOML)** | Yes (code) | Yes (deny blocks; removes tool) | No |
| **Admin Policies (OS-owned)** | Yes (code + OS) | Yes (highest tier) | No (requires root) |
| **Approval Modes** | Yes (code) | Yes | No |
| **Sandbox (Seatbelt/Docker/gVisor)** | Yes (OS) | Yes | No |
| **`tools.exclude`** | Yes (code) | Yes (tool removed) | No |
| **`security.disableYoloMode`** | Yes (code) | Yes | No |
| **Hook fingerprinting** | Yes (code) | Yes (warns on untrusted) | No |
| **Policy integrity (SHA-256)** | Yes (code) | Yes (detects tampering) | No |
| **GEMINI.md** | No (prompt) | No | Yes |
| **MCP `excludeTools`** | Yes (code) | Yes (hidden from model) | No |

## Sources

- [Gemini CLI GitHub](https://github.com/google-gemini/gemini-cli)
- [Hooks Overview](https://geminicli.com/docs/hooks/)
- [Hooks Reference](https://geminicli.com/docs/hooks/reference/)
- [Writing Hooks](https://geminicli.com/docs/hooks/writing-hooks/)
- [Configuration Reference](https://geminicli.com/docs/reference/configuration/)
- [Sandbox Documentation](https://geminicli.com/docs/cli/sandbox/)
- [Policy Engine Reference](https://geminicli.com/docs/reference/policy-engine/)
- [MCP Server Documentation](https://geminicli.com/docs/tools/mcp-server/)
- [Extensions Documentation](https://geminicli.com/docs/extensions/)
- [Policy Engine Blog](https://aipositive.substack.com/p/secure-gemini-cli-with-the-policy)
