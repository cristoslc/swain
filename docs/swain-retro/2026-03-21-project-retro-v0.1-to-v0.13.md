# Retro: Swain Project — v1.0.0 through v0.13.0-alpha

**Date:** 2026-03-21
**Scope:** Full project history
**Period:** 2026-03-07 — 2026-03-21 (14 days)

## What is Swain?

Swain started from one premise: AI agents forget what you decided. They ship code fast, but the decisions that shape a project — what to build, what to defer, which tradeoffs to accept — are trapped in conversation context that doesn't survive the next session. So you re-explain. The agent guesses. Work drifts from intent.

Swain's original answer was decision artifacts in git. Specs, epics, ADRs, spikes, visions — durable records of what was decided and why, checked into the repo where agents can read them before acting. A dependency graph (specgraph) validates that downstream work aligns with upstream decisions. The operator makes a call once; the system enforces it automatically.

That artifact system is one skill (swain-design). But operating an agentic project surfaced problems beyond decision durability: sessions that lose context on window reset, project health that degrades between sessions, releases that need structure, security posture that nobody checks, research that's collected once and lost. Each problem became a skill. Swain grew to 16 skills — not by plan, but because each gap in the operational surface became apparent only after the previous one was filled.

The skills rely heavily on deterministic code that ships alongside them — bash scripts, a Python dependency graph engine, shell-based health checks, a vendored task tracker (tk). This isn't a collection of markdown prompts. The markdown orchestrates; the scripts execute. This is also why swain is built as a skills framework rather than a platform-specific plugin: the same skills run in Claude Code (primary), GitHub Copilot, OpenAI Codex, and opencode. Runtime portability matters because the operator shouldn't be locked to one agent runtime.

Rather than build skills for development methodology (TDD, brainstorming, code review, plan writing), swain uses [obra/superpowers](https://github.com/obra/superpowers) as a complementary install and chains into it at defined integration points — brainstorming before artifact creation, TDD during implementation, verification before completion claims.

Named for the *swain* in boat**swain**, the officer who keeps the rigging tight. Built and used by a single operator. Distributed as an open-source skills package (`npx skills add cristoslc/swain`) but not yet validated for use by anyone other than its author.

## How it grew: evolution by commit

The timeline below traces how swain evolved from a single skill to a 16-skill framework. Measured in commits rather than calendar time, because agentic development compresses timelines in ways that dates don't convey. (The entire history spans 14 calendar days.)

| Commits | Days | Release | What was added | Why |
|---------|------|---------|---------------|-----|
| 1–13 | 2 | **v1.0.0** | Spec management, execution tracking (beads), release automation, swain- namespace, legacy cleanup | The original premise: write specs, track implementation against them, ship releases. Three skills. |
| 14–81 | 4 | **v2.0.0** | Meta-router, swain-doctor, swain-session, swain-stage, swain-status, swain-init, swain-help, swain-search, swain-keys, specgraph, specwatch | Operating a project across sessions revealed that decision artifacts alone aren't enough — you need health checks, session continuity, research collection, onboarding, and a way to visualize the dependency graph. The skill count tripled. |
| 82–400 | 2 | **v3.0.0 / 0.4.0** | Superpowers integration, vendored tk (replacing beads), specgraph as knowledge graph with alignment checking, sandbox launcher (claude-sandbox), worktree lifecycle, MOTD panel, model routing, agent dispatch, retrospectives, security scanning | The longest stretch. Superpowers brought in TDD/brainstorming/verification rather than building equivalents. Beads was replaced by tk when it couldn't scale. The sandbox and worktree work addressed safe autonomy — letting agents run without the operator watching. Security scanning followed because autonomous agents need guardrails. Versioning reset to 0.x to reflect alpha status. |
| 401–442 | 1 | **0.5.0** | Initiative artifact type, priority-weight cascade, vision-weighted recommendations, attention tracking, focus lanes | The artifact graph answered "what exists?" but not "what matters most?" Initiatives added a strategic layer between visions and epics. Priority weights let the operator say "security matters more than polish" and have recommendations follow. |
| 443–469 | 1 | **0.6.0** | Trove redesign (hierarchical sources), swain chart CLI, lens framework, VisionTree renderer | Research troves outgrew flat file lists. The chart CLI made the artifact graph inspectable from the terminal. |
| 470–481 | 1 | **0.7.0** | Pane-aware tmux tab naming, project identity enforcement | Small release. Tmux integration matured — tabs show which repo/branch/worktree you're in per-pane. |
| 482–621 | 3 | **0.8.0** | Security scanning (5 scanners + 2 built-in), Docker sandbox (swain-box) with multi-step auth UX, TRAIN artifact type, design integrity checking | The largest feature release. Security went from "not considered" to a layered system integrated into doctor, sync, and completion workflows. swain-box grew from a proof-of-concept into a real launcher. |
| 622–696 | <1 | **0.9.0** | Trunk+release branch model, merge-with-retry (replacing rebase-then-push), roadmap renderer (Eisenhower quadrants, Gantt, dependency graph) | Born from a retro: parallel worktree agents were losing data during rebase. The fix (merge-with-retry) required rethinking the branch model entirely. The roadmap renderer made the prioritization layer visible. |
| 697–732 | <1 | **0.10.0–0.13.0** | CLI roadmap, auto-detecting trunk branch, data contracts (ADR-014), Jinja2 changelog templates, universal find-based script discovery, skill audit remediation | Consolidation. Fixing what broke under velocity — scripts that assumed they knew their own path, changelogs that agents couldn't reliably categorize, skills that drifted from their specs. |

**Pattern:** Each release era solved the problems created by the previous one. Decision artifacts created the need for a dependency graph. The dependency graph created the need for prioritization. Prioritization created the need for a roadmap renderer. Parallel agents created the need for safe landing. Each layer was unforeseeable until the previous layer was in use.

## Summary

730 non-merge commits across 13 releases in 14 days, built almost entirely through agentic development — the operator directing AI agents, making design decisions, and reviewing output while agents handled implementation. The operator estimates this produced 10x–100x more progress than solo development would have.

## Artifacts

| Metric | Count |
|--------|-------|
| Releases | 13 (1.0.0 → 0.13.0-alpha) |
| Non-merge commits | 730 |
| Swain skills | 16 |
| Artifact types | 10 (Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Design, Journey) |
| Prior retros | 6 |
| Active Visions | 3 (Operator Cognitive Support, Safe Autonomy, Swain) |

## Reflection

### What went well

**Agentic development velocity is real.** 730 commits in 14 days, covering scope that would normally take months of solo work. The operator-as-decision-maker / agent-as-implementer pattern worked: the operator shaped every design decision while agents handled file operations, lifecycle management, cross-referencing, and implementation.

**Persisted artifacts as durable context.** This is the validating meta-pattern for swain itself. Retros were referenced across sessions — the EPIC-038 retro was read 5+ times during the SPIKE-022 → SPEC-114 session, each reading surfacing new insights. Spikes, ADRs, and specs survived context window resets and session boundaries. The artifact graph provided continuity that ephemeral conversation context cannot. Without persisted artifacts, the iterative deepening that produced merge-with-retry (from retro → spike → ADR → spec → implementation) would not have been possible.

**Retro-driven development.** 4 of the 6 retros directly produced implementation work. The EPIC-038 retro led to SPIKE-022, which led to ADR-011/013 and SPEC-114. The v0.10.0 retro led to the Jinja2 changelog template. The spike-findings retro led to SPEC-116/117 (read-before-reasoning, evidence-basis rules). Retros aren't just reflection — they're a discovery mechanism for what to build next.

### What was surprising

**Agentic development has addictive qualities.** The tight feedback loop of "describe → see it built → describe the next thing" creates a compulsion similar to gaming addiction. The operator has had to actively moderate this, with only partial success. This is a genuinely novel phenomenon that isn't well-understood yet.

**Scope explosion was unpredictable.** The operator might have predicted "framework-level scope eventually" but not within two weeks. Each capability created the context for the next — specgraph enabled prioritization, prioritization required initiatives, initiatives required visions, visions required attention tracking. The cost of building dropped dramatically but the cost of deciding what to build stayed constant.

**730 commits is a lot.** Slightly inflated by lifecycle hash stamps and artifact transitions, but mostly meaningful. The volume itself is surprising even to the person who produced it.

### What would change

**Move out of bash earlier.** Some scripts have grown to sizes that make the operator nervous. specgraph was rewritten in Python (3.0.0), but chart.sh and other scripts accumulated complexity under agentic velocity without the review pressure that slower-paced development provides.

**Enforce TDD earlier.** The operator wanted a much better TDD cycle but hasn't figured out how to do TDD on skills, let alone a skill framework. Goal-orientation and enforced-TDD were identified as desirable earlier than they were adopted.

**Read and review more code personally.** Agentic velocity means the operator is approving output faster than they can deeply understand it. The agent writes code the operator hasn't read — a trust gap that accumulates.

**Open question: is this worth continuing?** The operator is genuinely skeptical that swain will work for anyone besides them. The alternative — adopting existing tooling — is tempting but likely leads back to heavy customization... which is how swain started. The "customize existing tooling back into swain" loop is the classic framework author's dilemma.

### Patterns observed (synthesized from 6 prior retros)

#### 1. Agent overcomplicates, operator simplifies

Appears in 4/6 retros. The agent's instinct is to build new infrastructure; the operator's instinct is to use existing primitives correctly. Examples:
- SPIKE-022: three-layer mitigation strategy → "just use merge" (operator: "this must be a solved problem")
- EPIC-038: reactive spec-per-screenshot → architecture-first decomposition (operator: "do we need to rebuild the specs?")
- v0.10.0: agent couldn't reliably bucket changelog entries → Jinja2 template to make categories structural
- EPIC-031: SPIKE-033 recommended No-Go on a disambiguation framework — the simple fix was 2 lines

**Implication:** The operator's highest-value contribution is simplification. Agents naturally accrete complexity; the operator prunes it.

#### 2. Forward-linking is natural, back-propagation is not

Appears in 3/6 retros. Agents naturally link new artifacts to their dependencies but never go back to update old artifacts when new evidence arrives.
- SPIKE-032 invalidated SPEC-067 AC-8, but SPEC-067 was never updated
- DESIGN-005 superseded DESIGN-002, caught only by manual operator inspection
- 7 of 9 audit specs in EPIC-031 were already done by the time execution started — the audit was stale

**Implication:** The system validates at creation time but doesn't re-evaluate when context changes. Every mitigation so far (spike completion hooks, same-type overlap checks, pre-implementation detection) addresses a specific instance of this general pattern.

#### 3. Velocity vs. integrity tradeoff

Appears in 3/6 retros. Autonomous execution optimizes for throughput at the cost of semantic correctness.
- VISION-002: 8 artifacts in one session, but a semantic conflict between spike findings and spec ACs was missed
- EPIC-038: worktree agents reported success in isolation, but the merged result was incomplete
- verification-before-completion was skipped during rapid execution despite being mandatory in AGENTS.md

**Implication:** The superpowers chain (brainstorming → TDD → verification) exists precisely to counter this. The chain was specified but not always followed. Making it structural rather than advisory is the remaining gap.

#### 4. Persisted artifacts enable iterative deepening

Appears in 2/6 retros explicitly, but is the foundational pattern for the entire project.
- EPIC-038 retro was referenced 5+ times across sessions, each reading surfacing new insights
- Retros directly produced 4 implementation streams (SPIKE-022, Jinja2 template, SPEC-116/117, evidence-basis rule)
- Spike research troves (18 sources for multi-agent collision vectors) built durable knowledge bases

**Implication:** This validates swain's core thesis. Artifacts that survive context window resets and session boundaries enable a depth of analysis that ephemeral conversation cannot. The framework's complexity is justified by this capability — but only if the artifacts are actually read and maintained.

#### 5. Research before rendering

Appears in 2/6 retros. Jumping to implementation before understanding the problem space costs time.
- Mermaid quadrantChart limitations: 45 minutes of trial and error that upfront research would have prevented
- ADR-005 wasn't read until the operator asked why cherry-pick was being used — should have been the first thing read

**Implication:** The "read before reasoning" rule (SPEC-116) and "evidence basis for all actions" rule (SPEC-117) are direct responses. These are now governance rules, not just retro observations.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_agentic_addiction.md | feedback | Agentic development has addictive qualities — the operator may need help moderating session length and scope |
| project_retro_swain_viability.md | project | Operator uncertain about swain's viability beyond personal use — "customize existing tooling back into swain" loop |
