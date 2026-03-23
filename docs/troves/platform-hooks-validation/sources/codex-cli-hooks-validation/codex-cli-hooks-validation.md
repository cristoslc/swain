---
source-id: "codex-cli-hooks-validation"
title: "OpenAI Codex CLI — Sandbox, Approval, and Validation Mechanisms"
type: web
url: "https://developers.openai.com/codex/concepts/sandboxing"
fetched: 2026-03-22
---

# OpenAI Codex CLI — Sandbox, Approval, and Validation Mechanisms

## Overview

Codex CLI (OpenAI, Apache 2.0, Rust) leads with kernel-level sandboxing as its primary enforcement mechanism: Apple Seatbelt on macOS, Landlock + Seccomp-BPF on Linux, Restricted Tokens on Windows. Layered on top: approval policies (untrusted/on-request/never/granular), Starlark-based execpolicy rules for shell command gating, a nascent hooks engine (5 events), protected paths (.git, .agents, .codex always read-only), enterprise requirements.toml, and full MCP support. AGENTS.md is advisory.

---

## 1. Sandbox System

**Nature: Deterministic (kernel-level, code-enforced).**

### Platform Implementations

**macOS — Apple Seatbelt:**
- Uses `/usr/bin/sandbox-exec` with dynamically generated SBPL profiles
- Writable roots enumerated; `.git` forced to read-only
- Network: binary (full or none) — no per-domain granularity at seatbelt level
- Debug: `codex sandbox --full-auto -- COMMAND`

**Linux — Landlock + Seccomp:**
- Separate helper binary `codex-linux-sandbox`
- **Landlock** (LSM, kernel 5.13+): filesystem access control; grants read universally, restricts writes to whitelisted roots + `/dev/null`
- **Seccomp-BPF** (kernel 3.5+): syscall filtering
  - Blocked: `SYS_connect`, `SYS_accept`, `SYS_bind`, `SYS_listen`, `SYS_sendto`, `SYS_sendmsg`, `ptrace`, `init_module`, `delete_module`, `reboot`
- No external dependencies or setuid binaries (pure Rust)
- `prctl(PR_SET_PDEATHSIG)` kills sandboxed children if parent dies
- v0.115.0: prefers system bubblewrap when available

**Windows — Restricted Token (experimental).**

### Three Sandbox Modes

| Mode | Filesystem | Network |
|---|---|---|
| `read-only` | Read everywhere, no writes | Blocked |
| `workspace-write` (default) | Read/write in workspace + `/tmp` + configured roots | Blocked by default |
| `danger-full-access` | Full machine access | Enabled |

### Protected Paths (always read-only, recursive)

- `.git/` — prevents hook injection
- `.agents/` — prevents instruction tampering
- `.codex/` — prevents config tampering

### Bypass

v0.106.0 patched a zsh-fork bypass. `--dangerously-bypass-approvals-and-sandbox` / `--yolo` disables everything — intended for externally hardened VMs only.

---

## 2. Approval Policies

**Nature: Deterministic (code-enforced gate).**

| Policy | Behavior |
|---|---|
| `untrusted` | Prompts for everything except safe reads |
| `on-request` (default) | Auto-approves within sandbox; prompts for violations |
| `never` | No prompts; CI/CD automation only |
| `granular` | Per-category: `sandbox_approval`, `rules`, `mcp_elicitations`, `request_permissions`, `skill_approval` |

- `--full-auto` = `--ask-for-approval on-request --sandbox workspace-write`
- v0.104.0: distinct approval IDs per command in multi-step execution
- v0.105.0: granular rejection with feedback (model adjusts)
- v0.113.0: model can formally request elevated permissions via `request_permissions` tool
- v0.115.0: Guardian subagent routes approval reviews

---

## 3. Execpolicy Rules (Starlark)

**Nature: Deterministic (code-enforced).**

Written in Starlark (Python-like, sandboxed, no side effects).

Files: `~/.codex/rules/default.rules` and `rules/` under team config locations.

```python
prefix_rule(
    pattern = ["git", ["push", "force-push"]],
    decision = "forbidden",
    justification = "No force pushing allowed",
)
```

### Decisions

- `allow` (default)
- `prompt` (require approval)
- `forbidden` (block without prompting)

**Precedence: most restrictive wins** (`forbidden` > `prompt` > `allow`).

Shell handling: safe script splitting via tree-sitter for `&&`, `||`, `;`, `|` chains.

Enterprise: admins enforce from `requirements.toml`.

Test: `codex execpolicy check --pretty --rules ~/.codex/rules/default.rules -- git push --force`

---

## 4. Hooks Engine

**Nature: Deterministic for blocking hooks.**

Introduced v0.99.0–v0.116.0, experimental.

| Event | Can Block? | Version |
|---|---|---|
| `SessionStart` | No (injects context) | v0.114.0 |
| `Stop` | Yes (can block with reason) | v0.114.0 |
| `AfterAgent` | No (observe) | v0.99.0 |
| `AfterToolUse` | No (observe) | v0.100.0 |
| `UserPromptSubmit` | Yes (can block or augment) | v0.116.0 |

Configuration: `[[hooks]]` arrays in `config.toml` with `event` and `command` fields.

Execution: synchronous, blocks turn progression. Matching hooks run in parallel, results aggregated. Hook messages are ephemeral (not persisted to history).

**Notable absence: No PreToolUse hook.** Codex relies on the sandbox + approval policy + execpolicy rules for pre-execution gating rather than a general-purpose pre-tool hook.

---

## 5. Configuration

**Precedence (highest to lowest):**
1. CLI flags and `-c key=value`
2. Profile values (`--profile`)
3. Project config (`.codex/config.toml`, trusted projects only)
4. User config (`~/.codex/config.toml`)
5. System config (`/etc/codex/config.toml`)
6. Built-in defaults

**Enterprise:** `requirements.toml` — admin constraints, restricts available choices after config merge.

### AGENTS.md (Advisory)

- Global: `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`
- Project: `AGENTS.md` in repo root or nested directories
- Max 32 KiB combined
- Prompt-injected; compliance depends on model reasoning

---

## 6. Network Isolation

**Nature: Deterministic (kernel-level).**

- Default: blocked in `workspace-write` and `read-only` modes
- macOS: Seatbelt blocks all network
- Linux: Seccomp blocks connect/accept/bind/listen/sendto/sendmsg
- Fine-grained: permission profiles with `allowed_domains`, `denied_domains`, `allow_unix_sockets`
- Managed proxy (Codex Cloud): domain presets filter through proxy layer

---

## 7. MCP Support

Full MCP support (experimental). Transports: STDIO, Streamable HTTP.

- `enabled_tools` / `disabled_tools` per server
- MCP tools with side effects trigger approval prompts
- Enterprise: `requirements.toml` restricts which MCP servers are permitted
- `codex mcp-server` exposes Codex itself over stdio for multi-agent orchestration

---

## Summary Matrix

| Mechanism | Deterministic? | Can Block? | Agent Bypassable? |
|---|---|---|---|
| **Sandbox (seatbelt/landlock/seccomp)** | Yes (kernel) | Yes | No |
| **Approval policy** | Yes (code) | Yes | No (unless `--yolo`) |
| **Execpolicy rules (Starlark)** | Yes (code) | Yes (`forbidden` blocks) | No |
| **Hooks (blocking: Stop, UserPromptSubmit)** | Yes (code) | Yes | No |
| **Network isolation** | Yes (kernel) | Yes | No |
| **Protected paths (.git, .agents, .codex)** | Yes (sandbox) | Yes (read-only) | No |
| **requirements.toml (enterprise)** | Yes (code) | Yes | No |
| **AGENTS.md** | No (prompt) | No | Yes |

## Sources

- [GitHub repo](https://github.com/openai/codex)
- [Sandbox docs](https://developers.openai.com/codex/concepts/sandboxing)
- [Approval & security](https://developers.openai.com/codex/agent-approvals-security)
- [Config reference](https://developers.openai.com/codex/config-reference)
- [CLI reference](https://developers.openai.com/codex/cli/reference)
- [MCP docs](https://developers.openai.com/codex/mcp)
- [Rules/execpolicy](https://developers.openai.com/codex/exec-policy)
- [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Deep sandbox analysis (Pierce Freeman)](https://pierce.dev/notes/a-deep-dive-on-agent-sandboxes)
- [Hooks engine PR](https://github.com/openai/codex/pull/13276)
