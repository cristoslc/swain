---
title: "Superpowers–Swain Skill Mapping"
artifact: SPIKE-004
track: container
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-12
question: "How do superpowers' skills map to swain's, and should swain be retired, integrated with, or maintained alongside superpowers?"
gate: Pre-decision
risks-addressed:
  - Redundant maintenance of two overlapping skill ecosystems
  - Missing best-in-class agent alignment techniques
evidence-pool:
linked-artifacts:
  - EPIC-004
---

# Superpowers–Swain Skill Mapping

## Question

How do obra/superpowers' skills and workflow steps map to swain's skill ecosystem? Based on this mapping, should swain be retired in favor of superpowers, should superpowers skills be adopted within swain, or should the two systems coexist with clear boundaries?

## Go / No-Go Criteria

- **Go (Retire swain):** Superpowers covers ≥80% of swain's functional surface AND swain's unique capabilities (lifecycle management, evidence pools, release automation) are either unneeded or easily replaced.
- **Go (Integrate):** Clear complementary surfaces with <20% overlap, no architectural conflicts, and a feasible co-installation model.
- **No-Go (Status quo):** Significant architectural conflicts that make co-installation impractical without major refactoring of one or both systems.

## Pivot Recommendation

If neither retirement nor integration is feasible, swain continues independently and cherry-picks specific techniques from superpowers (e.g., anti-rationalization patterns, subagent review stages) as documentation improvements rather than skill imports.

## Findings

### 1. System-Level Comparison

| Dimension | Superpowers (v5.0.1) | Swain |
|-----------|----------------------|-------|
| **Primary metaphor** | "Superpowers for your agent" — structured implementation workflow | "Decision support for operator, alignment for agent" — lifecycle governance |
| **Scope** | Implementation workflow: design → plan → execute → review → merge | Full project lifecycle: governance, research, design, tracking, release, session |
| **Artifact types** | 2: Design specs, Implementation plans | 11: Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey, Design |
| **Task tracking** | Platform built-in (TodoWrite) | External CLI (bd/beads) |
| **Enforcement style** | Anti-rationalization tables, hard gates, pressure-tested loophole closing | Structured artifacts + skill routing + specwatch/specgraph tooling |
| **Multi-platform** | Claude Code, Cursor, Codex, OpenCode, Gemini CLI | Claude Code only |
| **Installation** | Plugin marketplaces / manual clone | npx skills / git clone |
| **License** | MIT | — |

### 2. Skill-by-Skill Mapping

#### Superpowers skills → Swain equivalents

| Superpowers Skill | Swain Equivalent | Overlap | Notes |
|-------------------|-----------------|---------|-------|
| **using-superpowers** (session bootstrap) | **swain-doctor** + **swain-session** | Partial | Superpowers hooks session start to enforce skill discovery. Swain runs health checks + context restoration. Different concerns. |
| **brainstorming** (Socratic design) | **swain-design** (artifact creation) | Moderate | Both produce specs from conversation. Superpowers uses Socratic Q&A with hard gates. Swain uses templated artifacts with lifecycle phases. Superpowers is more opinionated about the conversation flow; swain is more opinionated about the output format. |
| **writing-plans** (implementation plans) | **swain-do** (execution tracking) | Moderate | Both bridge specs → tasks. Superpowers generates detailed plans with exact code. Swain delegates to bd for tracking. Superpowers plans are more prescriptive (2-5 min tasks with code). |
| **subagent-driven-development** (parallel execution) | No equivalent | None | Swain has no subagent dispatch for implementation. This is a significant superpowers strength. |
| **executing-plans** (fallback execution) | **swain-do** (task execution) | Low | Superpowers fallback for no-subagent environments. Swain's primary execution path. |
| **dispatching-parallel-agents** (parallel investigations) | No equivalent | None | Swain doesn't have explicit parallel agent dispatch for research or debugging. |
| **using-git-worktrees** (isolated workspaces) | No equivalent | None | Swain has no worktree management skill. |
| **finishing-a-development-branch** (branch completion) | **swain-push** (commit & push) | Low | Superpowers handles full branch lifecycle (test, merge/PR/keep/discard, cleanup). Swain handles commit message generation and push. Superpowers is broader. |
| **requesting-code-review** / **receiving-code-review** | No equivalent | None | Swain has no code review workflow. |
| **test-driven-development** (strict TDD) | Referenced in implementation plans but not a standalone skill | Low | Superpowers enforces RED-GREEN-REFACTOR with deletion of pre-test code. Swain's implementation-plans.md references TDD but doesn't enforce it. |
| **systematic-debugging** (root cause analysis) | No equivalent | None | Swain has no debugging methodology skill. |
| **verification-before-completion** (evidence-based completion) | **spec-verify.sh** (acceptance criteria verification) | Moderate | Both require evidence before claiming completion. Superpowers is broader (any task). Swain is spec-specific. |
| **writing-skills** (skill creation) | **skill-creator** (external, not swain-native) | Low | Different approaches to meta-skill creation. |

#### Swain skills with NO superpowers equivalent

| Swain Skill | What It Does | Why Superpowers Lacks It |
|-------------|-------------|------------------------|
| **swain-design** (full artifact lifecycle) | 11 artifact types with lifecycle phases, cross-references, dependency graphs | Superpowers only has specs and plans — no epics, ADRs, journeys, personas, etc. |
| **swain-search** (evidence pools) | Collect, normalize, cache research sources as reusable evidence | Superpowers has no research infrastructure |
| **swain-release** (release automation) | Changelog, version bump, git tag | Superpowers has no release skill |
| **swain-status** (project dashboard) | Cross-cutting status: epics, progress, GitHub issues, next steps | Superpowers has no project-level status view |
| **swain-doctor** (health checks) | Governance validation, gitignore hygiene, legacy cleanup | Superpowers has basic session hooks only |
| **swain-stage** (tmux workspace) | Layout presets, pane management, MOTD panel | Superpowers has no terminal management |
| **swain-keys** (SSH provisioning) | Per-project git signing keys | Superpowers has no key management |
| **swain-update** (self-updater) | Pull latest skills, reconcile governance | Superpowers uses marketplace updates |
| **specwatch.sh / specgraph.sh** (artifact tooling) | Stale reference detection, dependency visualization | No equivalent — superpowers doesn't have a dependency graph |
| **adr-check.sh** (ADR compliance) | Cross-checks artifacts against adopted ADRs | No ADR system at all |

### 3. Overlap Analysis

**Meaningful overlap exists in 3 areas:**

1. **Spec authoring:** Both systems produce specifications from conversation. Superpowers' brainstorming is more structured (Socratic Q&A, spec review loop with subagent). Swain-design is more flexible (11 artifact types, lifecycle phases, cross-references).

2. **Implementation planning → execution:** Both bridge specs to tasks. Superpowers generates detailed plans with exact code snippets and dispatches subagents. Swain delegates to bd for tracking and leaves implementation details to the agent.

3. **Completion verification:** Both require evidence before declaring work done. Superpowers is broader (any task). Swain's spec-verify.sh is acceptance-criteria-specific.

### 4. Gap Analysis

**Superpowers has that swain lacks:**
- Subagent-driven development (multi-agent implementation with review stages)
- Parallel agent dispatch
- Git worktree management
- Code review workflow (requesting + receiving)
- Strict TDD enforcement with anti-rationalization
- Systematic debugging methodology
- Anti-rationalization engineering (exhaustive loophole closing in every skill)
- Multi-platform support

**Swain has that superpowers lacks:**
- Full artifact lifecycle (11 types vs. 2)
- Evidence pool collection and caching
- Release automation
- Project status dashboard
- Session management (tmux, bookmarks, preferences)
- Health checks and governance validation
- Dependency graph tooling (specwatch, specgraph)
- ADR system and compliance checking
- Terminal workspace management

### 5. Conflict Analysis

**Potential conflicts if co-installed:**

| Concern | Risk | Severity |
|---------|------|----------|
| **Session startup** | Both want to run at session start. Superpowers hooks SessionStart; swain auto-invokes doctor + session. Could race or produce conflicting instructions. | Medium |
| **Spec format** | Superpowers saves to `docs/superpowers/specs/`. Swain saves to `docs/spec/<Phase>/`. Different formats, different frontmatter. | Low (different paths) |
| **Plan format** | Superpowers saves to `docs/superpowers/plans/`. Swain uses bd. Different systems entirely. | Low (different paths) |
| **Task tracking** | Superpowers uses TodoWrite. Swain uses bd. If both are active, tasks could be tracked in two places. | Medium |
| **Skill invocation priority** | Superpowers demands skills be checked before ANY response with even 1% applicability. Swain routes via AGENTS.md. Both want to be the primary routing layer. | High |
| **TDD enforcement** | Superpowers deletes code written before tests. Swain doesn't enforce TDD at skill level. If superpowers TDD skill activates during swain-tracked work, it could disrupt the workflow. | Medium |

### 6. Recommendations

#### A) Should swain be retired?

**No.** The two systems are more complementary than overlapping.

Superpowers excels at the **implementation inner loop**: disciplined TDD, subagent dispatch, code review, debugging, and branch management. It enforces engineering rigor during coding.

Swain excels at the **project outer loop**: artifact lifecycle, research, release automation, governance, status tracking, and session management. It provides the strategic layer that tells agents *what* to build and *why*.

Retiring swain would lose:
- The entire artifact type system (11 types vs. superpowers' 2)
- Evidence pool research infrastructure
- Release automation
- Project-level status and dependency tracking
- ADR system and compliance checking
- Session/workspace management
- Governance and health checks

These are not things superpowers plans to cover — they're outside its stated scope.

#### B) How to leverage superpowers' skills within swain

**Recommended integration model: three-layer with contested middle**

The two systems don't split cleanly into inner/outer. Superpowers' brainstorming and writing-plans skills are higher-order design and planning activities — they overlap directly with swain-design and swain-do. The honest model has three layers:

**Layer model:**

```
┌───────────────────────────────────────────────────┐
│  SWAIN only (project governance)                  │
│  Vision, Epic, Journey, Persona, ADR, Runbook     │
│  Evidence pools, status, release, session, doctor  │
├───────────────────────────────────────────────────┤
│  OVERLAP (design & planning)                      │
│  swain-design spec authoring ↔ brainstorming      │
│  swain-do planning ↔ writing-plans                │
│  spec-verify ↔ verification-before-completion     │
├───────────────────────────────────────────────────┤
│  SUPERPOWERS only (implementation discipline)     │
│  TDD, subagent dispatch, worktrees, code review   │
│  systematic debugging, parallel agents            │
└───────────────────────────────────────────────────┘
```

**The contested middle layer is the key integration question.** Both systems want to drive spec authoring and implementation planning. The options:

**Option 1 — Swain owns structure, superpowers owns conversation flow:** Swain-design controls artifact format, lifecycle, and cross-references. When superpowers is present, its brainstorming skill drives the *conversation* that produces a spec (Socratic Q&A, spec review subagent), but the output gets captured into swain's artifact format with proper frontmatter, lifecycle table, and parent references. Similarly, writing-plans generates the plan content but swain-do wraps it with bd tracking.

**Option 2 — Let superpowers lead the middle layer entirely:** When superpowers is installed, swain-design defers to brainstorming for spec creation and swain-do defers to writing-plans for plan creation. Swain still provides the governance wrapper (lifecycle phases, cross-references, indexes) but doesn't drive the design conversation. Risk: superpowers' spec format (date-prefixed files in `docs/superpowers/specs/`) diverges from swain's artifact model.

**Option 3 — Cherry-pick techniques, don't import skills:** Instead of co-installing, swain adopts the *patterns* from superpowers that it lacks — anti-rationalization tables in swain-do, subagent dispatch in implementation plans, Socratic questioning in swain-design's artifact creation flow — as enhancements to existing swain skills. No runtime dependency on superpowers.

**Chosen: Option 1** (operator decision, 2026-03-12)

Option 1 preserves both systems' strengths: swain owns artifact structure and lifecycle; superpowers drives conversation flow and implementation discipline where it's stronger.

### 7. Integration Design (Option 1, refined)

The following integration points reflect operator decisions on where each system leads.

#### 1. Brainstorming — selective, not universal

Superpowers' Socratic brainstorming flow is valuable but heavy. It should not fire for every artifact type. Routing by artifact:

| Artifact type | Brainstorming flow? | Rationale |
|---------------|-------------------|-----------|
| **Vision** | Yes — full Socratic | Visions benefit from deep interrogation of goals, audience, and success metrics |
| **Persona** | Yes — full Socratic | Personas need probing to avoid shallow archetypes |
| **Epic** | Quick draft first, then offer | Epics often have enough context from their parent Vision. Start with a quick output, ask "want to interrogate this further?" |
| **Story** | No | Stories are derived from Epics/Journeys — the thinking already happened |
| **Spike** | No | Spikes define a question, not a design — brainstorming adds overhead |
| **ADR** | No | ADRs record a decision already made, not discover one |
| **SPEC** | No — see below | SPECs are being thinned; the design conversation happens at Epic/Vision level |
| **Bug, Runbook, Design, Journey** | No | Structured templates are sufficient |

All artifacts stay in swain's format and structure regardless of whether brainstorming drove the conversation.

#### 2. SPECs — thin contract, not implementation plan

**Operator decision:** SPECs remain as thin contracts — acceptance criteria, linked ADRs, cross-references, verification gate. The heavy implementation-plan section that SPECs currently carry is replaced by superpowers' writing-plans output. A SPEC answers "what must be true"; a superpowers plan answers "how to make it true."

The workflow becomes:
1. swain-design creates the SPEC (thin: acceptance criteria, scope, dependencies, ADR links)
2. When implementation begins, superpowers' writing-plans generates the detailed execution plan from the SPEC's acceptance criteria
3. swain-do wraps the plan with bd tracking (see point 3 below)
4. spec-verify.sh still gates Testing → Implemented against the SPEC's acceptance criteria

This eliminates the current redundancy where SPECs carry both the contract and the plan.

#### 3. Task tracking — swain mediates, superpowers doesn't touch TodoWrite

**Operator decision:** Superpowers' use of TodoWrite is unacceptable for agent swarm coordination. TodoWrite is ephemeral and per-session; bd persists across sessions and agents.

Integration model: **swain-do intercepts at the plan level.** When superpowers' writing-plans produces a plan, swain-do ingests the tasks and creates bd items from them. Subagents report progress against bd, not TodoWrite. Superpowers doesn't need to know about bd — swain-do is the adapter layer.

This requires swain-do to:
- Parse superpowers plan format (checkbox tasks with metadata)
- Create bd tasks with appropriate labels (spec, story references)
- Provide a status view that subagents can update

#### 4. Execution — prefer subagent-driven development

When superpowers is installed, subagent-driven development is the preferred execution strategy. Swain-do's bd-tracked serial execution is the fallback when superpowers is absent or when a task is too simple to warrant subagent overhead.

#### 5. TDD — adopt superpowers' enforcement

Adopt superpowers' strict RED-GREEN-REFACTOR with anti-rationalization tables for all implementation work, regardless of which system initiated it. This is a swain skill enhancement, not a runtime dependency — the TDD discipline gets baked into swain-do's implementation methodology.

#### 6. Worktrees — adopt for spec implementation

Use superpowers' worktree skill when implementing specs. Swain tracks the branch-to-artifact relationship (which worktree implements which SPEC).

#### 7. Code review — adopt for transition gate

Use superpowers' code review skills (requesting + receiving) as part of the SPEC Testing → Implemented transition. The spec compliance reviewer checks against SPEC acceptance criteria; the code quality reviewer checks implementation.

#### 8. Session startup — lightweight preflight before doctor

**Operator decision:** swain-doctor is too token-heavy to run every session. Replace the auto-invoke with a lightweight preflight script:

```
swain-preflight (shell script, ~0 tokens if clean)
  ├── exit 0 → skip doctor, proceed to superpowers bootstrap → swain-session
  └── exit 1 + reason → invoke swain-doctor → superpowers bootstrap → swain-session
```

The preflight checks: governance files exist, gitignore is sane, no known broken state. Only invokes the full doctor when something's actually wrong. Doctor becomes on-demand rather than every-session.

#### 9. Completion verification — broaden to all tasks

Adopt superpowers' verification-before-completion pattern to cover any task, not just SPEC acceptance criteria. "No completion claims without fresh verification evidence" becomes a universal rule in swain-do.

### 8. What stays swain-only (no overlap)

- Full artifact lifecycle (11 types, lifecycle phases, cross-references)
- Evidence pools
- Release automation
- Project status dashboard
- Session/workspace management (tmux, bookmarks, preferences)
- Dependency graph tooling (specwatch, specgraph)
- ADR system and compliance checking

### 9. Open questions for downstream work

| # | Question | Status | Resolution |
|---|----------|--------|------------|
| 1 | SPEC template revision: how thin? | **Resolved** | Drop implementation plan section. Everything else stays (acceptance criteria, ADR links, cross-references, verification gate, lifecycle). |
| 2 | Plan ingestion format: parser contract between superpowers plan output and swain-do bd creation? | **Open — spike for EPIC-004** | Needs investigation of superpowers' plan output format to design the adapter. |
| 3 | Preflight script scope: what does it check, how to keep it zero-token when clean? | **Open — resolve in EPIC-004** | Design decision, not research. |
| 4 | Superpowers detection: how does swain know superpowers is installed? | **Resolved** | Skill directory presence check. |
| 5 | Anti-rationalization adoption: which swain skills get tables first? | **Resolved** | swain-do is the primary target. Others as needed — the technique is well-understood and can be applied incrementally. |

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-12 | — | Created directly in Active — research conducted in this session |
| Complete | 2026-03-12 | e94bb4b | Research findings complete; Option 1 (swain owns structure, superpowers owns conversation) chosen |
