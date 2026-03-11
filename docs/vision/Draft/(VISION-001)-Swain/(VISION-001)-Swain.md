---
title: "Swain"
artifact: VISION-001
status: Draft
product-type: personal
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
depends-on: []
evidence-pool: ""
---

# Swain

## Target Audience

Two personas, one workflow:

- **PERSONA-001: Swain Project Developer** — the operator. A solo developer working with AI coding agents. Makes decisions; delegates implementation. The bottleneck is always the operator's decision throughput, not the agent's implementation speed.
- **PERSONA-002: AI Coding Agent** — the implementation partner. Any AI coding agent (Claude Code, OpenCode, Codex, Gemini CLI, or future runtimes). Stateless across sessions, needs structured alignment information to execute correctly. Swain treats the agent as a black box.

## Value Proposition

Swain is a decision-support and implementation-alignment system for solo developers who work with AI coding agents.

**For the operator**, everything swain does supports decision-making: capturing and structuring intent into artifacts, surfacing what needs attention, providing review contexts, tracking what decisions unblock what work, and confirming that implementations match intent.

**For the agent**, swain provides alignment information — structured specs with acceptance criteria, scope boundaries, constraints, and dependency graphs — then verifies outcomes against those criteria. The agent's internal operational mode (how it plans, what tools it uses, what task backend it runs) is deliberately opaque to swain. Any agent that can read markdown and follow structured instructions can participate.

The two core questions that drive the entire system:

1. **"What needs a decision?"** — the operator's question. Swain surfaces artifacts requiring human judgment (spec approvals, spike verdicts, ADR decisions, triage) ordered by downstream impact.
2. **"What's ready for implementation?"** — the agent's question. Swain provides approved, unblocked artifacts with clear acceptance criteria and scope boundaries.

## Problem Statement

AI coding agents are fast at implementation but operate statelessly across sessions. Without a structured system of record, the developer loses track of project state, decisions pile up unresolved, and agents implement against stale or ambiguous intent. The gap isn't code quality — it's the coordination layer between human decisions and agent execution.

Existing tools don't fit:
- **Issue trackers** (GitHub Issues, Jira, Linear) are designed for teams, not for operator+agent workflows. They track work items, not decision contexts.
- **Project management tools** (Notion, Trello) require manual maintenance that drifts from code reality.
- **AI-native tools** (Cursor rules, Claude CLAUDE.md) handle code-level context but not project-level decision flow.

## Existing Landscape

Swain occupies a gap between three categories:

- **Spec-driven development tools** (GitHub Spec Kit, Kiro) — focused on individual spec→code pipelines. Don't address multi-artifact project state, decision backlogs, or cross-session continuity.
- **AI agent frameworks** (Claude Code, OpenCode, Codex) — provide the runtime but not the coordination layer. Each starts fresh; none maintain project-level state across sessions.
- **Personal project management** (todo.txt, Backlog.md, Taskwarrior) — lightweight task tracking without the structured artifact model that agents need for alignment.

## Build vs. Buy

Tier 3: build from scratch. No existing tool combines structured artifact lifecycle management, agent-readable specs, decision-support workflows, and stateless-agent coordination. The closest candidates (GitHub Spec Kit, Kiro) cover spec→code but not the decision layer or cross-session state.

Swain is implemented as a skill ecosystem for Claude Code (and potentially other agent runtimes), not as a standalone application. This keeps the maintenance surface small — skills are markdown instructions + shell scripts, not a separate codebase to deploy and operate.

## Maintenance Budget

Solo developer, spare time. Architectural constraint: skills are stateless markdown + shell scripts. No servers, no databases, no deployed infrastructure. State lives in the git repository (artifacts, frontmatter) and ephemeral caches (JSON files in the Claude Code memory directory). This keeps maintenance near zero — the repo *is* the system.

## Artifact Model

Swain's artifacts fall into five tiers based on their role in the decision→implementation pipeline:

| Tier | Purpose | Types | Consumer |
|------|---------|-------|----------|
| **Direction** | Define what to build and why | VISION, JOURNEY, PERSONA | Operator |
| **Coordination** | Group and sequence related work | EPIC | Both |
| **Implementation** | Define work for agents to execute | SPEC, BUG | Agent (primary), Operator (approval) |
| **Research** | Reduce uncertainty before committing | SPIKE, ADR | Both |
| **Reference** | Operational and design documentation | RUNBOOK, DESIGN | Both |

Direction-tier artifacts inform the operator's decisions. Implementation-tier artifacts align the agent's execution. Coordination and research artifacts bridge the two — they help the operator decide *what* to build and the agent understand *how* it fits together.

## Success Metrics

- The operator can assess "what needs my decision?" in under 30 seconds (via `/status`)
- An agent starting a fresh session can identify the next implementable work item and begin execution without conversational back-and-forth
- Artifact state is the single source of truth — no mental models, no side-channel notes, no stale dashboards
- Adding a new AI agent runtime requires zero changes to swain's artifact model (agent is a black box)

## Non-Goals

- **Not a team tool.** Swain is designed for solo developer + agent(s). Multi-user workflows, permissions, role-based access, and team dashboards are out of scope.
- **Not an agent runtime.** Swain provides alignment information and verification. It does not execute code, manage processes, or orchestrate agent behavior.
- **Not a replacement for git.** Git is the persistence layer. Swain structures what goes into git and reads what comes out, but doesn't replace version control workflows.
- **Not prescriptive about agent choice.** Any agent that reads markdown can use swain artifacts. No agent-specific integrations in the core model.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | — | Initial creation from SPIKE-003 philosophical reframe |
