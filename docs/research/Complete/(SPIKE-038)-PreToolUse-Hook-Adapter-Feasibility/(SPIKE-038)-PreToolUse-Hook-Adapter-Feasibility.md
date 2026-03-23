---
title: "PreToolUse Hook Adapter Feasibility"
artifact: SPIKE-038
track: container
status: Complete
author: cristos
created: 2026-03-22
last-updated: 2026-03-23
question: "Can swain implement process governance gates (spec-read check, ADR compliance, skill invocation mandate) via PreToolUse hooks on each target platform, and what does the adapter look like?"
gate: Pre-MVP
parent-initiative: INITIATIVE-020
risks-addressed:
  - Hook APIs may not expose enough context for process-aware validation
  - Subagent coverage gaps (OpenCode #5894) may undermine enforcement
  - Per-platform adapter maintenance may be unsustainable
evidence-pool: "platform-hooks-validation@21aa91c"
linked-artifacts:
  - SPIKE-039
  - VISION-005
---

# PreToolUse Hook Adapter Feasibility

## Summary

**Go.** 4 of 5 target platforms support PreToolUse hooks capable of implementing process governance gates. Claude Code, Gemini CLI, Copilot CLI, and OpenCode all validated with working prototypes that block git commits unless ADR compliance passes. Codex CLI lacks a general PreToolUse hook (structural limitation — relies on Starlark execpolicy instead). The hook adapter is highly portable: only JSON field names differ across platforms. A shared core script with thin platform wrappers is viable. Critical finding: OpenCode's subagent hook bypass (#5894) is fixed in v1.2.20. Regex bypass risk discovered on OpenCode (agent inserted flags to evade `/git\s+commit\b/`) — use `/\bgit\b.*\bcommit\b/` across all platforms.

## Question

Can swain implement process governance gates (spec-read check, ADR compliance, skill invocation mandate) via PreToolUse hooks on each target platform, and what does the adapter look like?

## Go / No-Go Criteria

- **Go**: At least 2 platforms support PreToolUse hooks with enough context (tool name, arguments, and ideally session state) to implement a "block commit unless ADR check passed" gate
- **No-Go**: PreToolUse hooks are too coarse (no argument inspection) or too fragile (breaking API changes) to build reliable process gates on any platform

## Pivot Recommendation

If PreToolUse is insufficient, pivot to post-hoc audit only ([SPIKE-040](../../Proposed/(SPIKE-040)-Post-Hoc-Process-Audit-Pipeline/(SPIKE-040)-Post-Hoc-Process-Audit-Pipeline.md)) and accept that enforcement is reactive rather than preventive. Alternatively, investigate MCP-server-side validation (intercept tool calls at the MCP layer rather than the platform hook layer).

## Findings

### Claude Code — PreToolUse Hook (validated 2026-03-23)

**Verdict: Go.** PreToolUse hooks on Claude Code are fully capable of implementing process governance gates. The prototype `pretool-adr-gate.sh` demonstrates:

**What works:**
- Hook receives `tool_name` and `tool_input.command` — enough to identify `git commit` calls
- Hook can inspect staged files via `git diff --cached` to detect artifact changes
- Hook can run `adr-check.sh` on staged artifacts and block the commit if checks fail
- `permissionDecision: "deny"` with `reason` produces clear, actionable feedback to the agent
- Passthrough latency for non-commit commands: ~13ms (negligible)
- Multiple hooks: deny > ask > allow priority means a governance hook cannot be overridden by a permissive hook

**Prototype implementation:** `scripts/hooks/pretool-adr-gate.sh`
- Matches: `Bash` tool calls containing `git commit`
- Checks: staged files under `docs/` against `adr-check.sh`
- State: uses `.agents/hook-state/adr-check-passed` timestamp (5-min TTL) to avoid redundant checks
- Deny output: structured JSON with failing artifact paths and ADR violations

**Configuration (`.claude/settings.json`):**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/hooks/pretool-adr-gate.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Limitations observed:**
- Hook is stateless per-invocation — it receives only the current tool call, not session history. Cannot natively answer "did the agent read the spec earlier?" (confirms SPIKE-039 session-state tracker is needed for richer process gates)
- Hook runs on every `Bash` tool call matching the regex — the `git commit` check inside the script is the real filter. No tool-argument-level matcher in the config.
- Subagent tool calls DO fire hooks (Claude Code confirmed in trove) — no bypass gap like OpenCode
- `agent`-type hooks (spawning a subagent with full tool access) could provide session-state-aware enforcement but weren't tested in this spike

**Process gates achievable with this mechanism:**
1. **ADR compliance on commit** — validated, working prototype
2. **Lifecycle transition enforcement** — block commits that change artifact `status:` without the corresponding `git mv` to the phase directory
3. **Governance file protection** — deny edits to AGENTS.md, skill files (better done via deny rules, but hooks can provide richer error messages)
4. **Spec-read enforcement** — requires session state (SPIKE-039); hook alone can only check if spec file was modified, not if it was read

### Gemini CLI — BeforeTool Hook (validated 2026-03-23)

**Verdict: Go.** BeforeTool hooks on Gemini CLI work for process governance gates. Live-tested with `gemini -p` headless mode.

**What works:**
- Hook configured in `.gemini/settings.json` with `matcher: "run_shell_command"` — fires on every shell command
- Allow path confirmed: `accept: 1, reject: 0` in tool usage stats for non-commit commands
- Deny path confirmed: model retried for 2+ minutes against deny hook, command never executed — deterministic block
- Hook uses `decision: "allow"` / `decision: "deny"` (vs Claude Code's `permissionDecision`) — minor field name difference
- `$GEMINI_PROJECT_DIR` env var correctly resolves hook script path

**Prototype implementation:** `.gemini/hooks/adr-gate.sh` + `.gemini/settings.json`

**Configuration:**
```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command",
        "hooks": [
          {
            "name": "adr-gate",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/adr-gate.sh",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

**Key differences from Claude Code:**
- `decision` field instead of `permissionDecision`
- Matcher is regex on tool name (can match `write_file|replace` for broader gating)
- Hook fingerprinting: Gemini warns if a project hook's name or command changes — protects against agent self-modification
- Policy engine available as a declarative alternative for simple deny rules (no script needed, TOML-based)
- Exit code 2 = emergency brake (stronger signal than JSON deny)
- Model retries on deny (unlike Claude Code which denies once) — the hook must be idempotent

**Adapter portability:** The hook script logic is nearly identical to Claude Code's — only the JSON field name differs (`decision` vs `permissionDecision`). A single script could serve both with a platform detection preamble, or use two thin wrappers calling a shared core.

### Codex CLI — No PreToolUse Hook (structural limitation)

Codex CLI lacks a general PreToolUse hook. Enforcement relies on:
- **Execpolicy rules (Starlark):** Can block specific shell commands (`forbidden` decision), but cannot run arbitrary validation logic (e.g., call adr-check.sh)
- **Approval policies:** Gate tool execution but are binary (approve/deny), not logic-aware
- **UserPromptSubmit hook (v0.116.0):** Can block prompts before execution, but fires before the agent plans, not before individual tool calls

**Implication:** Codex requires a different enforcement strategy — either post-hoc audit (SPIKE-040) or an MCP-server-side gate that validates before returning results.

### Copilot CLI — PreToolUse Hook (validated 2026-03-23)

**Verdict: Go.** Copilot CLI v1.0.10 auto-discovers hooks from `.github/hooks/pre-tool-use.json` and enforces deny decisions.

**What works:**
- Hook auto-discovered from `.github/hooks/` — no config file changes needed
- `permissionDecision: "deny"` blocks tool calls deterministically
- Same `permissionDecision` / `permissionDecisionReason` field names as Claude Code
- Headless mode (`copilot -p "..." --allow-all-tools -s`) fires hooks identically to interactive
- 9/9 unit tests pass, 2/2 integration tests pass (allow + deny paths)

**Input format differences from Claude Code:**

| Field | Claude Code | Copilot CLI |
|---|---|---|
| Tool name | `tool_name` | `toolName` |
| Tool arguments | `tool_input` (object) | `toolArgs` (JSON string — needs extra parse) |
| Permission decision | `permissionDecision` | `permissionDecision` (same) |

**Prototype:** `.github/hooks/adr-gate.sh` + `.github/hooks/pre-tool-use.json`

**Notable:** Hosted coding agent (GitHub Actions) doesn't need hooks — it has structural enforcement (draft PR only, branch restrictions, validation pipeline). Hooks are for the CLI and VS Code surfaces.

### OpenCode — tool.execute.before Plugin Hook (validated 2026-03-23)

**Verdict: Go.** OpenCode v1.2.20 plugin hooks work for process governance. Subagent bypass (#5894) is **fixed**.

**What works:**
- Plugins in `.opencode/plugins/*.ts` auto-discovered and loaded (Bun/TypeScript native)
- Throwing from `tool.execute.before` blocks tool execution — error surfaced to model
- Model sees the error and adjusts behavior (deterministic block confirmed)
- **Subagent hook coverage confirmed** — hooks fire for BOTH primary agent and subagent tool calls (two different session IDs intercepted). The #5894 bypass is fixed in v1.2.20.

**Trove correction — hook signature:**
- Trove research was wrong: handler takes `(input, output)`, not `(input)`
- `input` contains: `{ tool, sessionID, callID }` — tool name and session metadata
- `output` contains: `{ args: { command, description } }` — actual tool arguments
- Must read `output.args.command` not `input.args.command`

**Regex bypass risk discovered:**
- The agent circumvented `/git\s+commit\b/` by inserting flags: `git -c core.hooksPath=/dev/null commit`
- Robust pattern needed: `/\bgit\b.*\bcommit\b/` instead of `/git\s+commit\b/`
- This risk applies to ALL platforms, not just OpenCode

**Prototype:** `.opencode/plugins/adr-gate.ts`

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
| Active | 2026-03-23 | 9293866 | Activated for Claude Code hook testing |
| Complete | 2026-03-23 | 09d824a | Go: 4/5 platforms validated with working prototypes |
