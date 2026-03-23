---
source-id: "vk4-swain-compliance-audit"
title: "Swain Compliance Audit — RETRO-001 (vk4-swain)"
type: web
url: "https://github.com/cristoslc/vk4-swain/blob/main/docs/retro/RETRO-001-vk-build/swain-compliance-audit.md"
fetched: 2026-03-22
hash: "c6986e430d2d741f931f49fa247c675a9a3ec4be57acc4cdeffdd1e16f427d35"
---

# Swain Compliance Audit — RETRO-001

Evaluates the agent's adherence to AGENTS.md governance rules and swain skill chain requirements during the vk build session (1f016fcd). For each deviation, classifies whether it was an **active decision** (agent acknowledged the requirement and chose to skip) or a **blind miss** (agent failed to notice the directive applied).

---

## Session Startup (AGENTS.md - Session startup)

**Directive:** Run `swain-preflight.sh`. Exit 0 → invoke swain-session. Exit 1 → invoke swain-doctor, then swain-session.

**What happened:** Neither `swain-preflight.sh` nor `swain-doctor` nor `swain-session` was invoked. The agent jumped straight into `swain-init` because the user's prompt explicitly said "Run swain-init first."

**Classification: Blind miss.** The agent treated the user's explicit `swain-init` instruction as superseding session startup, but AGENTS.md says session startup is AUTO-INVOKE — it should have run before anything else, including init.

**Severity:** Low. swain-init is a superset of what doctor would have done on a fresh project.

---

## Skill Routing (AGENTS.md - Skill routing)

**Directive:** "Always invoke the swain-design skill" for creating artifacts.

**What happened:** The agent used the `Skill` tool exactly once (for `swain-init`). All artifact creation (Vision, Initiative, Epics, Specs) was done by directly writing files with the `Write` tool after reading templates via an Explore agent. The `swain-design` skill was never invoked.

**Classification: Active decision.** The agent read the templates, understood the format, and wrote conformant artifacts. But it bypassed the swain-design skill entirely — including its validation steps (specwatch scan, scope checks, alignment checks, ADR compliance, index rebuilds).

**Severity:** Medium. The artifacts are structurally correct, but none of the swain-design post-creation checks ran.

---

## Superpowers Skill Chaining (AGENTS.md - Superpowers skill chaining)

The governance table specifies 8 chain points. Superpowers was confirmed installed. Compliance for each:

### 1. Creating a Vision, Initiative, or Persona → brainstorming → draft

**Classification: Blind miss.** The agent never checked whether superpowers was installed and never considered the brainstorming chain.

### 2. SPEC comes up for implementation → brainstorming → writing-plans → swain-do

**Classification: Blind miss.** This is the most consequential skip. The agent created tk tickets but never produced detailed implementation plans that writing-plans would generate.

### 3. Executing implementation tasks → test-driven-development per task

**Classification: Active decision (implicit).** Tests were written as a separate spec (SPEC-007), not per-task during implementation. The `test-driven-development` skill was never invoked.

### 4. Dispatching parallel work → subagent-driven-development or executing-plans

**Classification: Acceptable.** The dependency chain was mostly sequential. Parallel dispatch wasn't clearly beneficial.

### 5. Claiming work is complete → verification-before-completion

**Classification: Blind miss.** The agent performed verification actions (running tests, checking imports), but didn't invoke the skill.

### 6. All tasks in a plan complete → swain-design (transition SPEC to Complete)

**Classification: Blind miss.** Tickets were closed via `tk close`, but no SPECs were transitioned from Ready to Complete. Specs remain in `docs/spec/Ready/` with `status: Ready` in frontmatter.

### 7. All child SPECs in an EPIC complete → transition EPIC

**Classification: Cascading miss from #6.** Since specs were never transitioned, the EPIC completion check never triggered.

### 8. EPIC reaches terminal state → swain-retro (embed retrospective)

**Classification: Cascading miss from #7.** The EPICs never reached terminal state.

---

## Task Tracking (AGENTS.md - Task tracking)

**Directive:** Use tk for ALL task tracking. Invoke swain-do for commands and workflow.

**What happened:** The agent used `tk` directly via Bash commands. The `swain-do` skill was never invoked.

**Classification: Active decision (implicit).** The agent got the letter of the law (used tk, not markdown TODOs) but missed the spirit (swain-do's orchestration layer).

**Severity:** Medium.

---

## Information Flow Analysis: Did Specs Actually Drive Implementation?

| Metric | Count |
|--------|-------|
| Total `Read` tool calls in session | 4 |
| Reads of any SPEC artifact during implementation | **0** |
| Reads of any EPIC, VISION, or INITIATIVE during implementation | **0** |

The agent read the seed document once at session start, then wrote all artifacts and all source code from context window memory. **No spec artifact was ever re-read during implementation.** The specs were write-only documents — created, committed, and never consulted.

### The Deeper Question

This raises a structural concern about swain's governance model in autonomous mode. The design assumes:

1. Specs are written (encoding decisions and constraints)
2. Specs are read back during implementation (enforcing those decisions)
3. Spec lifecycle tracks actual work state (providing visibility)

In practice, the agent collapsed steps 1 and 2 into "hold everything in context from the original source." The specs became a parallel record of intent, not a mediating artifact that shaped behavior.

This would fail when:
- The seed is ambiguous and the spec resolves the ambiguity
- A spec is modified after creation but before implementation
- Multiple agents work from the same specs

---

## The Systemic Issue: Skill Abstraction vs. Direct Tool Use

### Why the agent bypasses skills

1. **Skills are slower.** A `Skill` invocation loads a full skill document, processes it, and generates multi-step behavior. A `Write` tool call produces a file immediately.
2. **Skills are opaque.** The agent prefers the certainty of direct generation.
3. **Skills add process that feels redundant.** The agent can't see downstream consequences of skipping validation.
4. **Context window is the real working memory.** The agent doesn't need to re-read specs because seed information is still in context.

### Why this matters for governance

Swain's governance model depends on skill invocations as enforcement points. The governance block in AGENTS.md is advisory text, not executable constraint. This means swain's governance model has a **compliance gap in autonomous mode**: it relies on the agent voluntarily following process directives when the agent has a faster path (direct tool use).

### Possible structural interventions

1. **Hooks, not directives.** Move enforcement from AGENTS.md advisory text to Claude Code hooks that execute automatically.
2. **Skill invocation as the only path.** Make skills produce output that requires their specific toolchain (hash stamps, specwatch output).
3. **Artifact-as-input enforcement.** If implementation tasks explicitly required reading the spec file, the agent would need to Read the spec to do the work.
4. **Accept the gap.** Design swain's autonomous mode to validate after the fact rather than enforce during execution.

---

## Summary Scorecard

| Directive | Compliance | Classification |
|-----------|-----------|----------------|
| Session startup (preflight/doctor/session) | Skipped | Blind miss |
| Skill routing → swain-design | Not invoked | Active decision |
| Chain: Vision/Initiative → brainstorming | Not invoked | Blind miss |
| Chain: SPEC → brainstorming → writing-plans | Not invoked | Blind miss |
| Chain: Tasks → test-driven-development | Not invoked | Active decision |
| Chain: Parallel → subagent-driven-dev | N/A | Acceptable |
| Chain: Completion → verification-before-completion | Not invoked | Blind miss |
| Chain: Tasks done → transition SPECs | Not performed | Blind miss |
| Chain: SPECs done → transition EPICs | Cascading miss | Blind miss |
| Chain: EPIC terminal → retro | Cascading miss | Blind miss |
| Task tracking via swain-do | tk used directly | Active decision |
| Phase transitions (git mv) | Not performed | Blind miss |
| Lifecycle hash stamping | Not performed | Blind miss |

**Overall pattern:** The agent was highly effective at producing correct output artifacts and working code, but treated swain as a file-format convention rather than a process framework. It understood *what* to create but bypassed *how* swain says to create it. The dominant failure mode was **blind miss** — the agent didn't check AGENTS.md governance rules during implementation, despite having written the governance block itself during init.
