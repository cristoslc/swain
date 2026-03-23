# Platform Hooks and Validation — Synthesis

## Scope

This trove maps the **deterministic enforcement surfaces** across five agentic coding platforms (Claude Code, Gemini CLI, OpenAI Codex CLI, GitHub Copilot, OpenCode) with a specific lens: which mechanisms can swain use to make **process governance unskippable** — ADR compliance checks, lifecycle transitions, artifact creation requirements, skill invocation mandates, and similar workflow enforcement. Security sandboxing is catalogued but is not the primary concern; process compliance is.

---

## Key Findings

### Theme 1: PreToolUse hooks are the universal enforcement primitive

Every platform provides a mechanism to intercept tool calls before execution and block them. This is the hook swain would use to enforce "did you read the spec?" or "did you run the ADR compliance check?" before allowing implementation work.

| Platform | PreToolUse Mechanism | Blocking? | Subagent Coverage? |
|----------|---------------------|-----------|-------------------|
| **Claude Code** | `PreToolUse` hook (24 events total) | Yes (exit 2 or `deny`) | Yes (SubagentStart/Stop hooks exist) |
| **Gemini CLI** | `BeforeTool` hook + policy engine | Yes (exit 2 or `deny`) | Unclear (policy covers all tool calls; hooks may not fire for sub-agents) |
| **Codex CLI** | No PreToolUse hook; relies on execpolicy + approval | Partial (execpolicy `forbidden` blocks shell; no general pre-tool) | No general mechanism |
| **Copilot** | `PreToolUse` hook (VS Code + CLI) | Yes (`deny`) | VS Code: SubagentStart/Stop hooks; Coding agent: N/A (no subagents) |
| **OpenCode** | `tool.execute.before` plugin hook | Yes (throw) | **No — subagents bypass hooks (#5894)** |

**Implication for swain:** PreToolUse is the right abstraction for process gates. Claude Code and Copilot have the most complete coverage (including subagents). OpenCode has a critical subagent bypass. Codex lacks a general PreToolUse hook entirely, relying instead on its sandbox + execpolicy for enforcement.

### Theme 2: Two distinct enforcement architectures — hooks vs. policy engines

Platforms split into two camps for how they gate tool execution:

**Hook-first (Claude Code, Copilot, OpenCode):** External scripts run before each tool call. The hook receives tool name + arguments and returns allow/deny/ask. Hooks are general-purpose — any logic can run. But hooks must be installed and configured per-project.

**Policy-first (Gemini CLI, Codex CLI):** Declarative rule files (TOML or Starlark) evaluated against every tool call. Rules match on tool name, argument patterns, command prefixes. No custom code needed — just declarations. But rules can only express pattern matches, not arbitrary validation logic (e.g., "check if the spec file was read in this session").

**Hybrid is possible:** Gemini CLI has both hooks AND a policy engine. Claude Code's permission system (allow/deny rules) acts as a lightweight policy layer alongside hooks. The strongest enforcement combines both: policy rules for structural constraints (never force-push, never write to .env) and hooks for process-aware validation (was the spec consulted? did the ADR check pass?).

### Theme 3: Process enforcement requires session-state awareness — most hooks don't have it

The fundamental challenge for swain's process governance is that most hook mechanisms are **stateless** — they see the current tool call but not the session history. A PreToolUse hook can check "is this tool call allowed?" but not "has the agent read the spec artifact earlier in this session?"

**Session-state-aware mechanisms:**
- **Claude Code** `agent` hooks — spawn a subagent with full tool access that can inspect session state
- **Claude Code** `prompt` hooks — single-turn LLM eval that could check context
- **Gemini CLI** `BeforeAgent` hook — fires after user prompt, before planning; can inject context and deny the turn
- **Gemini CLI** `AfterAgent` hook — fires after response; can deny and trigger retry with correction prompt
- **OpenCode** event hooks (30+ events) — observe session events but cannot block

**Stateless mechanisms (most PreToolUse hooks):**
- Shell command hooks receive tool_name + tool_input but not session history
- Policy rules match patterns, not accumulated state

**Implication for swain:** Process enforcement (did you follow the workflow?) requires either (a) a stateful hook that can query session history, or (b) an external state tracker that hooks consult. Claude Code's `agent` hook type is uniquely suited — it can spawn a subagent that checks whether the session has consulted required artifacts. For other platforms, swain would need an MCP server or external service that tracks session state and hooks query it.

### Theme 4: Instruction files are universally advisory — never trust them for enforcement

Every platform has an instruction file mechanism. None enforce compliance:

| Platform | Instruction File | Enforcement |
|----------|-----------------|-------------|
| Claude Code | CLAUDE.md / AGENTS.md | Advisory (prompt) |
| Gemini CLI | GEMINI.md | Advisory (prompt) |
| Codex CLI | AGENTS.md | Advisory (prompt) |
| Copilot | copilot-instructions.md / AGENTS.md | Advisory (prompt) |
| OpenCode | SKILL.md / rules | Advisory (prompt) |

This confirms the agent-alignment-monitoring trove's core finding: documentary governance fails. The model can ignore any instruction file. Process enforcement must use code-level mechanisms (hooks, policies, permission rules) — never instruction files alone.

### Theme 5: Permission deny rules are the strongest portable constraint

All five platforms support deny rules that the agent cannot override:

| Platform | Deny Mechanism | Override Protection |
|----------|---------------|-------------------|
| **Claude Code** | `permissions.deny` rules | Even `bypassPermissions` cannot override deny |
| **Gemini CLI** | Policy engine `deny` rules | Admin tier (root-owned) cannot be overridden |
| **Codex CLI** | Execpolicy `forbidden` rules | Most-restrictive-wins; enterprise `requirements.toml` |
| **Copilot** | Enterprise policies | Admin-only; disable agents entirely |
| **OpenCode** | Permission `"deny"` values | Code-enforced at tool execute time |

Deny rules can prevent specific actions (never force-push, never write to governance files) but cannot enforce positive requirements (must read the spec, must run compliance check). For positive requirements, hooks are needed.

### Theme 6: The coding-agent (hosted) model has fundamentally different enforcement

GitHub Copilot's coding agent runs in a fully sandboxed GitHub Actions environment with structural constraints no other platform matches:
- **Draft PR only** — cannot merge its own work
- **Cannot self-approve** — mandatory human review
- **Branch restrictions** — only `copilot/` prefix branches
- **Validation pipeline** — CodeQL, secret scanning, advisory DB run automatically

This "output validation" model is architecturally different from "input gating" (hooks). Swain could use both: hooks gate process during execution, and a post-hoc validation pipeline checks the output before it merges. The post-hoc model accepts that agents will skip process and validates after the fact — matching intervention path #4 from the alignment trove.

---

## Points of Agreement

- **Instruction files are advisory everywhere.** No platform enforces AGENTS.md, CLAUDE.md, GEMINI.md, or copilot-instructions.md at the code level. Unanimous.
- **PreToolUse is the common hook point.** 4 of 5 platforms offer it (Codex lacks it but compensates with execpolicy). It's the natural place for process gates.
- **Deny rules are universally unbypassable.** Every platform's deny mechanism is code-enforced and cannot be overridden by the model.
- **MCP tools are subject to the same enforcement** as built-in tools on every platform that supports MCP (all five).

## Points of Disagreement

- **Hook architecture:** Claude Code/Copilot use shell-command hooks; Gemini CLI uses shell hooks + policy engine; Codex uses Starlark rules; OpenCode uses TypeScript plugin hooks. No portable hook format exists.
- **Subagent coverage:** Claude Code covers subagents; OpenCode explicitly does not (#5894); others are unclear.
- **Sandbox philosophy:** Codex and Gemini lead with sandboxing; Claude Code offers it optionally; Copilot uses it for terminal commands; OpenCode has none built-in. But sandboxing is about security isolation, not process enforcement.
- **Enterprise control depth:** Claude Code (managed settings), Gemini CLI (admin policies), and Codex (requirements.toml) offer deep enterprise lockdown. Copilot delegates to GitHub org policies. OpenCode has no enterprise tier.

## Gaps

- **No cross-platform hook standard.** Each platform has its own hook format, event names, and configuration. Swain would need per-platform adapters for hook-based enforcement.
- **No session-state-aware hook standard.** Only Claude Code's `agent` hook type can inspect session context. Others are stateless.
- **No "positive requirement" enforcement primitive.** All platforms can deny actions but none natively support "require X before allowing Y" — this must be built in hook logic.
- **Subagent hook coverage is inconsistent.** OpenCode has a known bypass; Gemini CLI and Codex coverage is unclear.
- **No post-hoc process audit tool.** Copilot's validation pipeline is closest (CodeQL, secret scanning) but doesn't cover process compliance (did the agent follow the workflow?). Swain's specwatch / design-check fills this gap.

---

## Cross-Links to Existing Troves

- **`agent-alignment-monitoring`** — This trove answers the gap identified there: "No comparison of enforcement mechanisms." The four intervention paths (hooks, skill gating, artifact-as-input, post-hoc audit) now have concrete platform mechanisms mapped to them.
- **`portable-framework-patterns`** — The lack of a cross-platform hook standard means hook-based enforcement is per-platform, unlike AGENTS.md/MCP which are portable.

---

## Relevance to Swain

This trove is the evidence base for building unskippable process governance. The synthesis suggests a **layered enforcement strategy**:

1. **Deny rules** (portable, all platforms) — prevent specific harmful actions: never edit governance files, never skip commit signing, never force-push
2. **PreToolUse hooks** (per-platform adapters) — enforce positive requirements: must read spec before implementation, must run ADR compliance check before committing, must invoke required skills
3. **Session-state tracker** (MCP server or external service) — provide the session context that stateless hooks need: which artifacts were consulted, which skills were invoked, which lifecycle transitions occurred
4. **Post-hoc audit** (CI/validation pipeline) — validate process compliance after the fact for platforms where pre-execution enforcement is weak or for catching what hooks miss

The strongest enforcement combines layers 1–3 on Claude Code (which has the richest hook system including stateful `agent` hooks) with layer 4 as a universal backstop. For other platforms, layer 2 requires per-platform adapter work, making layer 4 relatively more important.

**Priority for swain implementation:**
- **Immediate** (Claude Code): PreToolUse hooks for process gates + managed settings for deny rules
- **Near-term** (Gemini CLI): Policy engine rules + BeforeTool hooks (richest second platform)
- **Medium-term** (Copilot, Codex, OpenCode): PreToolUse hooks where available; execpolicy for Codex; await subagent fix for OpenCode
- **Universal**: MCP-based session-state tracker that any platform's hooks can query; post-hoc audit pipeline
