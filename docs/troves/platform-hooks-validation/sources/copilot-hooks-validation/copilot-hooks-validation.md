---
source-id: "copilot-hooks-validation"
title: "GitHub Copilot — Hooks, Policies, and Validation Mechanisms"
type: web
url: "https://docs.github.com/en/copilot/reference/hooks-configuration"
fetched: 2026-03-22
---

# GitHub Copilot — Hooks, Policies, and Validation Mechanisms

## Overview

GitHub Copilot spans two distinct agentic surfaces: **VS Code agent mode** (local) and **Copilot coding agent** (GitHub-hosted, autonomous). The local surface provides hooks (PreToolUse deny), approval gates, terminal sandboxing, enterprise policies, and MCP support. The hosted surface provides fundamentally different enforcement: ephemeral sandboxed VMs, draft-PR-only output, branch restrictions, validation pipelines (CodeQL, secret scanning, advisory DB), and mandatory human review. `copilot-instructions.md` is advisory on both surfaces.

---

## 1. Copilot Agent Mode (VS Code — Local)

### Hooks System

**Nature: Deterministic (code-enforced).**

8 lifecycle events in VS Code, 6 in CLI/coding agent:

| Hook | Trigger | Can Block? |
|---|---|---|
| **SessionStart** | New/resumed session | VS Code: inject context |
| **SessionEnd / Stop** | Session terminates | VS Code: can block stop |
| **UserPromptSubmitted** | User sends prompt | No |
| **PreToolUse** | Before any tool call | **Yes — can deny** |
| **PostToolUse** | After tool completes | VS Code: can block result |
| **ErrorOccurred** | Error during execution | No |
| **PreCompact** (VS Code only) | Before compaction | No |
| **SubagentStart/Stop** (VS Code only) | Subagent lifecycle | Start: inject; Stop: can block |

### PreToolUse — Critical Enforcement Hook

Input (stdin JSON): `timestamp`, `cwd`, `toolName`, `toolArgs`.

Output (stdout JSON):
```json
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Blocked dangerous command"
}
```

Decisions: `"allow"`, `"deny"` (deterministic block), `"ask"` (user prompt; not processed in CLI). Multiple hooks: **most restrictive wins**.

Configuration: `.github/hooks/*.json` (repository), `~/.copilot/hooks/` (user-level). VS Code also reads `.claude/settings.json` format (cross-compatibility).

### Approval Gates

| Gate | Type | Can Block? |
|---|---|---|
| Terminal command approval | Deterministic | Yes |
| File edit review (diff editor) | Deterministic | Yes |
| Sensitive file protection (glob) | Deterministic | Yes |
| Tool approval scopes (session/workspace/user) | Deterministic | Yes |
| URL/domain approval | Deterministic | Yes |
| Terminal sandboxing (macOS/Linux) | Deterministic | Yes |
| Workspace trust / restricted mode | Deterministic | Yes (disables agents entirely) |
| Enterprise policies | Deterministic | Yes (admin-only) |

### Permission Modes

- **Default Approvals** — uses configured settings per tool
- **Bypass Approvals** — auto-approves all (warning banner)
- **Autopilot** — auto-approves AND drives iteration without intermediate review

### Enterprise Policy Controls

- `ChatAgentMode` — disable agents entirely
- `ChatAgentExtensionTools` — restrict extension tools
- `ChatToolsTerminalEnableAutoApprove` — disable terminal auto-approval
- `ChatToolsEligibleForAutoApproval` — require manual approval for specific tools
- `ChatToolsAutoApprove` — disable global auto-approval

### Agent Self-Modification Risk

The agent has file edit access and can theoretically modify hook scripts during a session. Mitigation: disable `chat.tools.edits.autoApprove` so edits to hook files require manual approval.

---

## 2. Copilot Coding Agent (GitHub-Hosted — Autonomous)

### Structural Enforcement

All deterministic, code-enforced:

| Mechanism | Description |
|---|---|
| **Draft PR only** | Agent cannot mark PR as "Ready for review" |
| **Cannot self-approve or merge** | Requester also cannot approve |
| **Branch restrictions** | Only `copilot/` prefix branches; cannot push to main/protected |
| **Branch protection rules** | Standard required checks apply |
| **Firewall** | Outbound connections restricted (admin-configurable) |
| **Workflow approval gate** | Actions don't trigger until human clicks "Approve and run workflows" |
| **Write-access gate** | Only write-access users can trigger |
| **Prompt injection filtering** | Hidden characters filtered from input |
| **Content exclusions** | Admin-configured exclusions honored |

### Validation Pipeline (all deterministic)

1. **CodeQL** — static analysis for security vulnerabilities
2. **GitHub Advisory Database** — malware, High/Critical CVEs in dependencies
3. **Secret scanning** — API keys, tokens, sensitive data
4. **Copilot code review** — second-opinion AI review
5. **Custom validation tools** — configurable from repo settings

### Sandbox Constraints

- Read-only repo access (except `copilot/*` branches)
- Internet controlled by firewall
- Cannot run direct git commands
- Cannot access multiple repos per task
- One PR per task
- Treated as outside collaborator

### Environment Definition

`copilot-setup-steps.yml` — location: `.github/workflows/copilot-setup-steps.yml`. Job MUST be named `copilot-setup-steps`. Defines runners, dependencies, tools.

---

## 3. copilot-instructions.md

**Nature: Advisory (prompt-based).**

| File | Location | Scope |
|---|---|---|
| Repository-wide | `.github/copilot-instructions.md` | All Copilot in repo |
| Path-specific | `.github/instructions/*.instructions.md` | Files matching glob |
| Organization-wide | Org settings | All repos in org |
| Personal | IDE settings | Individual user |

Path-specific frontmatter: `applyTo: "**/*.ts"`, `excludeAgent: "code-review"`.

Cannot block or prevent actions. Users can disable in IDE settings.

---

## 4. MCP Support

Supported across: VS Code (v1.99+), Visual Studio, JetBrains, Xcode, Eclipse, Copilot CLI, Copilot coding agent (Enterprise).

Transports: HTTP/SSE (remote), Stdio (local), Docker containers.

Configuration: `.vscode/mcp.json` (repo), `settings.json` (personal), `~/.copilot/mcp-config.json` (CLI).

Security:
- Explicit trust per MCP server required
- Configuration changes trigger re-auth
- MCP server sandboxing available (macOS/Linux) for stdio
- Organization policy: "MCP servers in Copilot" — disabled by default for Business/Enterprise

---

## 5. Custom Agents (`.agent.md`)

Defined in `.github/agents/`. Frontmatter specifies: tools the agent can use, instructions (advisory), hooks (scoped to that agent).

---

## Summary Matrix

### VS Code Agent Mode

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Hooks (PreToolUse deny)** | Yes (code) | Yes | No (but agent can edit hook files if edits auto-approved) |
| **Approval gates** | Yes (code) | Yes | Yes (via Bypass/Autopilot mode) |
| **Terminal sandbox** | Yes (OS) | Yes | No |
| **Enterprise policies** | Yes (code) | Yes | No |
| **Workspace trust** | Yes (code) | Yes (disables agents) | No |
| **copilot-instructions.md** | No (prompt) | No | Yes |

### Copilot Coding Agent (GitHub-Hosted)

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Draft PR enforcement** | Yes (platform) | Yes | No |
| **Branch restrictions** | Yes (platform) | Yes | No |
| **Validation pipeline** | Yes (code) | Yes | No |
| **Firewall** | Yes (platform) | Yes | No |
| **Workflow approval gate** | Yes (platform) | Yes | No (unless auto-configured) |
| **copilot-instructions.md** | No (prompt) | No | Yes |

## Sources

- [About Copilot Coding Agent](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent)
- [Hooks Configuration Reference](https://docs.github.com/en/copilot/reference/hooks-configuration)
- [VS Code Agent Hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)
- [Introducing Copilot Agent Mode](https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode)
- [VS Code Copilot Security](https://code.visualstudio.com/docs/copilot/security)
- [Adding Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Extending Copilot with MCP](https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol/extending-copilot-chat-with-mcp)
- [VS Code MCP Servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
- [Configure Validation Tools](https://github.blog/changelog/2026-03-18-configure-copilot-coding-agents-validation-tools/)
- [awesome-copilot Hooks](https://github.com/github/awesome-copilot/blob/main/docs/README.hooks.md)
- [Custom Agents Configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
