---
source-id: "swain-ecosystem-extended-analysis"
title: "Swain Integrated Ecosystem: Extended Task Tracking Evaluation"
type: local
path: "docs/troves/task-management-systems/sources/swain-ecosystem-extended-analysis/swain-ecosystem-extended-analysis.md"
fetched: 2026-03-22T00:00:00Z
hash: "50c9711c99929c9dc2cd0787527b25afe85268ca22f80a19e12dfc917cbd7280"
notes: "Extended evaluation of swain-design + swain-do + tk as integrated ecosystem, following the original evaluator rubric format"
---

# Swain Integrated Ecosystem: Extended Task Tracking Evaluation

## Context

The original evaluation (from the original evaluator) scored **swain-do + tk** as a standalone task tracker, arriving at **38/50**. That score was fair for tk in isolation -- but it evaluated the engine while ignoring the car it's built into. This document re-evaluates the **full swain stack** as an integrated ecosystem: swain-design (artifact lifecycle), swain-do (execution tracking), swain-status (dashboard), swain-session (cross-session continuity), tk (the CLI backend), and the supporting scripts (specgraph/chart.sh, specwatch, adr-check, relink, spec-verify, design-check). The same 10-criterion rubric is applied, but now the unit of analysis is the ecosystem, not just the ticket CLI.

---

## Evaluation: Swain Integrated Ecosystem (swain-design + swain-do + tk + supporting skills)

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Dependency Awareness** | 4 | tk provides directed dependencies (`tk dep`), `tk ready` for closure-aware filtering, and `tk blocked` for visibility. Still no critical path analysis. Still no subtasks (one level of parent only). **But**: swain-design adds a second, higher-order dependency layer -- EPIC-to-SPEC decomposition is enforced, `depends-on-artifacts` in frontmatter creates cross-artifact blocking, `chart.sh ready` surfaces artifact-level readiness across the entire Vision-to-Spec hierarchy, and child-artifact propagation auto-promotes lagging children when parents transition. The combination gives you dependency awareness at two granularities: artifact-level (strategic) and task-level (tactical). The gap remains: no computed critical path at either layer. |
| **Priority System** | 3 | tk itself is still static numeric 0-4. **But**: swain-design adds `priority-weight` (high/medium/low) on Visions, Initiatives, Epics, and Specs with explicit cascading rules (Vision -> Initiative -> Epic -> Spec, with per-level overrides). `chart.sh recommend` produces a ranked artifact view that factors in priority weight, lifecycle phase, and focus lane. swain-status surfaces this as actionable "what's next" guidance. Still no urgency decay, no due-date weighting, no dynamic recomputation based on blocked-task count. The priority model is richer than tk alone but still fundamentally operator-set rather than computed. |
| **Persistence** | 5 | Unchanged. Markdown + YAML frontmatter everywhere: `.tickets/` for tasks, `docs/` for artifacts. Git-committable, human-editable. Lifecycle tables with commit-hash stamps provide an immutable audit trail baked into the artifacts themselves. Session state persists in `.agents/session.json`. Everything survives context compaction, `/clear`, session restarts, and machine reboots. |
| **Agent-Native Design** | 5 | This is where the ecosystem evaluation diverges most from tk-alone. The skill layer (swain-do, swain-design, swain-status, swain-session) is purpose-built for AI agent consumption. AGENTS.md provides routing rules so any agent that reads it knows which skill handles which intent. swain-do wraps tk with agent-friendly conventions (term mapping, operating rules, anti-patterns). swain-design enforces artifact ceremonies that an agent follows procedurally -- complexity tier detection, fast-path eligibility, superpowers chaining. The `swain-do: required` frontmatter field is a machine-readable trigger. `ticket-query` provides structured JSON output for programmatic use. The entire system assumes the primary operator is an AI agent, with human oversight at decision points. |
| **Cross-Session Continuity** | 5 | Filesystem-based persistence is the foundation, but the ecosystem adds active continuity mechanisms. swain-session restores terminal context, bookmarks, and focus lanes on startup. Session bookmarks leave breadcrumbs for the next session. `--external-ref` on tk epics creates immutable links from task plans back to their source specs. The artifact graph on disk is always current -- any new agent session reads `docs/` and `.tickets/` and has full context. Pre-plan implementation detection scans for unmerged branches, git history, and deliverable files from prior sessions before creating redundant work. |
| **Human Readability** | 5 | Artifacts are plain markdown with YAML frontmatter -- readable in any text editor, Typora, GitHub's web UI, or `cat`. Lifecycle tables in artifacts show phase history with commit hashes. `list-<type>.md` index files provide navigable tables of all artifacts by type and phase. `tk show` renders ticket details. `swain chart` produces terminal-rendered hierarchy trees. swain-status outputs a dashboard with OSC 8 hyperlinks for clickable artifact links in supporting terminals. Everything is designed to be inspectable without the agent running. |
| **Integration Effort** | 3 | Honest assessment: this is still non-trivial. `swain-init` handles onboarding and `swain-doctor` validates the setup, but adopting swain means adopting an ecosystem -- skill files, directory conventions, AGENTS.md governance, frontmatter schemas, lifecycle phases, specwatch, chart.sh. The payoff is high, but the ramp-up is real. A new project needs to understand the Vision -> Initiative -> Epic -> Spec hierarchy, the four execution tiers, the phase transition workflow, and the skill routing rules. This is not a `npm install` situation. The offsetting factor: once set up, `swain-doctor` catches configuration drift and `swain-preflight.sh` auto-validates on every session start. |
| **Artifact Traceability** | 5 | **This is the ecosystem's strongest differentiator.** The original evaluation correctly noted that tk's `--external-ref` and `--tags spec:ID` are just string fields. But the integrated ecosystem enforces traceability structurally: (1) Every SPEC traces to a parent Epic or Initiative. Every Epic traces to a Vision or Initiative. The hierarchy is validated on creation. (2) `artifact-refs` provides typed, commit-pinned cross-references with staleness tracking. (3) Lifecycle tables record every phase transition with commit hashes -- you can trace any artifact's full history through git. (4) specwatch continuously validates cross-references and flags stale links. (5) `chart.sh scope` shows the full ancestry chain from any artifact to its Vision root. (6) Supersession creates tracked provenance chains with back-reference updates. (7) ADR compliance checks run on creation and transitions. (8) Spike back-propagation scans for invalidated assumptions in sibling artifacts. This is not "a text field that could link to a spec" -- it's an enforced relationship model with 11 artifact types, typed references, commit pinning, staleness detection, and automated validation. |
| **Multi-Agent / Collaboration** | 4 | tk provides atomic claim via mkdir-based locking (`tk claim` uses `mkdir` for atomic lock acquisition). Worktree isolation gives each agent its own branch and working directory, preventing file-level conflicts. swain-do's execution strategy supports subagent-driven development -- dispatching parallel agents on independent tasks with worktree-artifact mapping recorded in tk notes. The superpowers chain provides structured multi-agent orchestration. The gap: no distributed locking across machines (mkdir locks are local), no real-time conflict resolution, and the worktree model requires git. Still, for a single-machine multi-agent workflow, this is well-designed. |
| **Portability** | 4 | tk itself is pure bash with zero dependencies. Artifacts are plain markdown. But the full ecosystem includes Python scripts (specgraph), shell scripts that assume a specific directory layout, and the skill file format that's specific to Claude Code (or agents that read AGENTS.md). The data is fully portable -- you can read every artifact and ticket with any text editor. The *automation* is tied to the swain skill ecosystem. No cloud dependency, no API keys, fully offline. Downgraded from 5 because the skill layer is a meaningful dependency for getting the full value. |
| **Total** | **43/50** | |

---

## Strengths

- **Deep artifact traceability is structural, not optional.** The 11-type artifact hierarchy with enforced parent references, typed cross-references, commit-pinned staleness tracking, and continuous validation (specwatch, adr-check, design-check) creates a provenance graph that no other evaluated tool matches. Tasks don't float free of "why" -- they're anchored to specs, which are anchored to epics, which are anchored to visions.

- **Two-layer dependency model.** Artifact-level dependencies (`depends-on-artifacts`, parent hierarchy, `chart.sh ready`) handle strategic ordering. Task-level dependencies (`tk dep`, `tk ready`) handle tactical ordering. This separation means you can reason about "which spec should we work on next?" independently from "which task within this spec is unblocked?"

- **Agent-native from the ground up.** Unlike tools adapted for agent use via MCP bridges, swain was designed for AI agents as the primary operator. Skill routing, frontmatter triggers, complexity tier detection, and the term-mapping abstraction layer all reflect this.

- **Git-native audit trail.** Lifecycle tables with commit-hash stamps, git-mv for phase transitions, and the lifecycle hash stamping convention create an immutable, git-diff-able history of every decision and state change.

- **Multi-agent orchestration.** Worktree isolation, atomic task claiming, and subagent dispatch with artifact mapping provide real (not theoretical) multi-agent support for single-machine workflows.

## Weaknesses

- **No subtasks.** tk supports one level of nesting (epic -> task). Multi-level decomposition requires workarounds. saga-mcp's Project > Epic > Task > Subtask hierarchy remains superior here.

- **No computed priority.** Priority is operator-set at both layers. There is no urgency decay, no due-date weighting, no dependency-weighted escalation. Taskwarrior's multi-factor urgency scoring remains the gold standard.

- **No due dates.** Neither tk nor swain-design has a native due-date field.

- **Ecosystem adoption cost.** You adopt swain as an ecosystem or not at all. The artifact types, lifecycle phases, skill routing, directory conventions, and frontmatter schemas represent a significant learning curve.

- **No distributed locking.** mkdir-based locks are machine-local.

- **Skill layer portability.** The full value requires Claude Code (or an agent that reads AGENTS.md and can invoke skills). The data is portable; the automation is not.

---

## Score Comparison: tk-Only vs. Integrated Ecosystem

| Criterion | tk-Only | Integrated | Delta | What Changed |
|-----------|---------|------------|-------|--------------|
| Dependency Awareness | 3 | 4 | +1 | swain-design adds artifact-level dependencies, `depends-on-artifacts`, `chart.sh ready`, child propagation |
| Priority System | 2 | 3 | +1 | `priority-weight` cascading, `chart.sh recommend`, swain-status actionable guidance |
| Persistence | 5 | 5 | 0 | Already maxed |
| Agent-Native Design | 4 | 5 | +1 | Skill routing, AGENTS.md governance, term mapping, frontmatter triggers, complexity tier detection |
| Cross-Session Continuity | 5 | 5 | 0 | Already maxed |
| Human Readability | 5 | 5 | 0 | Already maxed |
| Integration Effort | 3 | 3 | 0 | Ecosystem adoption cost is real in both cases |
| Artifact Traceability | 3 | 5 | **+2** | Typed cross-references, commit-pinned staleness, specwatch validation, enforced hierarchy, ADR compliance, supersession chains |
| Multi-Agent / Collaboration | 3 | 4 | +1 | Worktree isolation, atomic claiming, subagent dispatch |
| Portability | 5 | 4 | **-1** | Skill layer dependency reduces portability of the automation |
| **Total** | **38** | **43** | **+5** | |

---

## Updated Summary Rankings

| Rank | Method | Score | Best For |
|------|--------|-------|----------|
| **1** | **Swain Integrated Ecosystem** | **43** | **Spec-driven projects needing deep artifact traceability, lifecycle governance, and agent-native task orchestration** |
| 2 | saga-mcp | 40 | Complex projects needing structured hierarchy without ecosystem adoption |
| 3 | swain-do + tk (standalone) | 38 | Projects using swain where you only evaluate the task layer |
| 3 | Claude Task Master | 38 | PRD-driven greenfield development with AI-powered decomposition |
| 5 | External PM via MCP | 37 | Teams where humans need visibility alongside agent work |
| 6 | Taskwarrior via MCP | 36 | Power users who want sophisticated urgency scoring |
| 7 | Built-in Tasks | 33 | Quick, no-setup task tracking within/across sessions |
| 7 | File-Based Markdown | 33 | Maximum simplicity, solo work, small projects |
| 9 | blizzy78 (in-memory) | 28 | Single-session complex orchestration with critical path needs |

---

## Key Insight: Evaluating Ecosystems vs. Components

The original evaluation correctly identified that "artifact traceability is a workflow concern, not a tool feature" and that "any tool with a text/tag field can link to a spec." This is true -- but it understates what happens when traceability is *structurally enforced* rather than *optionally available*.

The swain ecosystem doesn't just allow you to link tasks to specs. It:

1. **Requires** parent references on artifact creation and validates they exist
2. **Continuously validates** cross-references via specwatch scans
3. **Automatically updates** back-references when artifacts are superseded
4. **Pins references to specific commits** with staleness detection
5. **Enforces lifecycle ceremonies** -- phase transitions run ADR compliance checks, alignment checks, and verification gates
6. **Cascades state changes** -- completing all child SPECs auto-completes the parent EPIC, which triggers a retrospective

No other evaluated system provides this level of structural enforcement. saga-mcp has the richest standalone data model. Taskwarrior has the best priority algorithm. But neither connects task execution to a governed artifact lifecycle with validated provenance chains.

The tradeoff is real: you pay for this with ecosystem adoption cost and reduced portability of the automation layer. For a solo operator or small team doing spec-driven development with AI agents, that tradeoff pays off. For a team that needs to onboard quickly or share task state with non-agent tooling, saga-mcp or an external PM tool may be the better fit.

---

## Updated Capability Gap Matrix

| Method | Projects | Subtasks | Computed Priority | Artifact Lifecycle | Enforced Traceability |
|--------|----------|----------|-------------------|-------------------|----------------------|
| **Swain Ecosystem** | Yes (Vision > Initiative > Epic > Spec) | No (one-level parent in tk) | No (cascading weight, not computed) | **Yes -- 11 types, 3 tracks, enforced transitions** | **Yes -- specwatch, commit pins, ADR checks** |
| saga-mcp | Yes (Project > Epic > Task > Subtask) | Yes, multi-level | No (static fields) | No | No |
| Claude Task Master | Yes (project-scoped JSON) | Yes (AI-driven decomposition) | Yes (complexity scoring) | No | Partial (PRD tracing) |
| Jira via MCP | Yes (full project hierarchy) | Yes (unlimited nesting) | Yes (JQL + sprint planning) | No (manual workflow configs) | Depends on team discipline |
| Linear via MCP | Yes (Team > Project > Issue > Sub-issue) | Yes (sub-issues) | Yes (priority + cycle-based) | No | Depends on team discipline |
| Taskwarrior | Yes (`project:` dot hierarchy) | No (flat tasks + deps) | **Yes -- best in class** | No | No |
| Built-in Tasks | No | No (flat with DAG) | No | No | No |
| tk (standalone) | No | No (one-level parent) | No | No | No |
| File-Based Markdown | No | No | No | No | No |
| blizzy78 | No | Yes (sequenced subtasks) | No | No | No |

---

## Updated Decision Framework

```
Do you need cross-session persistence?
  NO  --> blizzy78/mcp-task-manager (session planner)
  YES -->
    Do you need artifact/spec traceability?
      YES -->
        Do you need ENFORCED traceability with lifecycle governance?
          YES --> Swain Integrated Ecosystem
          NO  -->
            Already using swain? --> swain-do + tk
            Starting fresh?     --> Claude Task Master (PRD-driven)
      NO -->
        Do humans also need to see task state?
          YES -->
            Team uses Linear/Jira/GitHub? --> External PM via MCP
            Solo / small team?            --> saga-mcp or Notion
          NO -->
            Need dependency logic?
              YES --> Built-in Tasks or saga-mcp
              NO  --> File-based markdown
```
