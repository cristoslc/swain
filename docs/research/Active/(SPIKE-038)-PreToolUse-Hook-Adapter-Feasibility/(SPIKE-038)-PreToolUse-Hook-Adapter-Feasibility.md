---
title: "PreToolUse Hook Adapter Feasibility"
artifact: SPIKE-038
track: container
status: Active
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

### Gemini CLI — BeforeTool Hook (not yet tested)

Trove data suggests BeforeTool hooks are structurally equivalent to Claude Code's PreToolUse. Key differences:
- Matcher is a regex on tool name (e.g., `write_file|replace`)
- Can rewrite `tool_input` via `hookSpecificOutput.tool_input`
- Exit code 2 is an "emergency brake" — stronger than JSON deny
- Policy engine provides a declarative alternative for simple deny rules (no script needed)
- Hook fingerprinting adds security (warns on modified hooks)

**Next step:** Install test hooks on Gemini CLI and validate the same ADR-gate pattern.

### Codex CLI — No PreToolUse Hook (structural limitation)

Codex CLI lacks a general PreToolUse hook. Enforcement relies on:
- **Execpolicy rules (Starlark):** Can block specific shell commands (`forbidden` decision), but cannot run arbitrary validation logic (e.g., call adr-check.sh)
- **Approval policies:** Gate tool execution but are binary (approve/deny), not logic-aware
- **UserPromptSubmit hook (v0.116.0):** Can block prompts before execution, but fires before the agent plans, not before individual tool calls

**Implication:** Codex requires a different enforcement strategy — either post-hoc audit (SPIKE-040) or an MCP-server-side gate that validates before returning results.

### Copilot — PreToolUse Hook (not yet tested)

Trove data confirms PreToolUse hooks exist in both VS Code agent mode and Copilot CLI. Same protocol as Claude Code (stdin JSON, stdout JSON with `permissionDecision`). Key differences:
- Hosted coding agent has structural enforcement (draft PR only, branch restrictions) that doesn't need hooks
- VS Code agent can edit hook scripts during a session — self-modification risk

**Next step:** Test hook installation and deny behavior on Copilot CLI.

### OpenCode — tool.execute.before Plugin Hook (not yet tested)

Plugin hooks exist but have a critical subagent bypass (#5894). Testing needed to confirm:
- Whether the bypass is still present in v1.2.20
- Whether permission-system deny rules (which are separate from hooks) cover the gap

**Next step:** Test plugin hook + permission deny on OpenCode.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-22 | 730b957 | Initial creation |
| Active | 2026-03-23 | 9293866 | Activated for Claude Code hook testing |
