---
source-id: "swain-ecosystem-extended-analysis"
title: "Swain Integrated Ecosystem: Extended Task Tracking Evaluation"
type: local
path: "docs/troves/task-management-systems/sources/swain-ecosystem-extended-analysis/swain-ecosystem-extended-analysis.md"
fetched: 2026-03-22T00:00:00Z
hash: "299094be48c92c36a53a9d0454f189fede86815462b2d0220dad9e320541cf54"
notes: "Extended evaluation of swain-design + swain-do + tk as integrated ecosystem, following original rubric format"
---

# Swain Integrated Ecosystem: Extended Task Tracking Evaluation

## Context

The original evaluation scored **swain-do + tk** at **38/50** as an isolated task tracker. This re-evaluates the **full stack**: swain-design (artifact lifecycle) + swain-do (execution tracking) + tk (CLI backend) + supporting tools (specgraph, specwatch, adr-check). Same rubric, broader unit of analysis.

**Important caveat:** swain's traceability and lifecycle conventions are prompt-guided, not schema-enforced. An agent can skip any step. The value comes from consistent conventions and validation scripts that *detect* drift, not from hard gates that *prevent* it.

---

### 1a. swain-design + swain-do + tk (integrated ecosystem)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 4 | tk: `tk dep`, `tk ready`, `tk blocked`. swain-design adds artifact-level dependencies (`depends-on-artifacts`, `chart.sh ready`). Two granularities: artifact (strategic) and task (tactical). Still no critical path analysis, still no subtasks. |
| Priority System | 3 | tk: static 0-4. swain-design adds `priority-weight` (high/medium/low) with cascading rules and `chart.sh recommend`. Still operator-set, not computed. No urgency decay, no due dates. |
| Persistence | 5 | Same as tk-only. Markdown + YAML + git everywhere. |
| Agent-Native Design | 5 | Skill layer is purpose-built for agents. AGENTS.md routing, frontmatter triggers (`swain-do: required`), complexity tier detection, structured JSON via `ticket-query`. Human oversight at decision points. |
| Cross-Session Continuity | 5 | Same filesystem foundation. swain-session adds bookmarks and focus lane restoration. `--external-ref` links task plans to source specs. |
| Human Readability | 5 | Same as tk-only. Markdown everywhere, `list-*.md` indexes, `swain chart` trees. |
| Integration Effort | 3 | `swain-init` + `swain-doctor` help, but adopting swain means learning 11 artifact types, lifecycle phases, skill routing, and directory conventions. Not a `npm install`. |
| Artifact Traceability | 4 | Parent references validated on creation. `artifact-refs` with commit-pinned staleness. specwatch detects stale links. `chart.sh scope` traces ancestry. **But**: all of this is convention-guided, not hard-enforced. Agents can bypass it. The validation scripts catch drift after the fact, not prevent it. Upgraded from 3 (tk-only) because the conventions and detection tooling are substantial, but not 5 because there are no hard guarantees. |
| Multi-Agent / Collaboration | 4 | mkdir-based atomic claiming. Worktree isolation per agent. Subagent dispatch with artifact mapping. Gap: local-only locking, no distributed coordination. |
| Portability | 4 | Data is fully portable (markdown + git). Automation requires Claude Code or compatible agent. No cloud dependency. -1 from tk-only because the skill layer is a meaningful dependency. |
| **Total** | **42/50** | |

**Strengths**: Artifact traceability conventions are the main differentiator — tasks connect to specs, epics, and visions through validated parent references and cross-reference scanning. Two-layer dependency model (artifact + task). Agent-native from the ground up. Git-native audit trail via lifecycle tables.

**Weaknesses**:
- **No subtasks** — one level of nesting only. saga-mcp's hierarchy is superior.
- **No computed priority** — Taskwarrior's urgency model remains the gold standard.
- **No due dates** — time pressure is implicit.
- **Traceability is soft** — prompt-guided conventions with after-the-fact validation, not hard schema enforcement. An agent that ignores the skill instructions breaks the chain silently.
- **Ecosystem adoption cost** — you adopt swain as a whole or not at all.

---

## Score Comparison: tk-Only vs. Integrated Ecosystem

| Criterion | tk-Only | Integrated | Delta | What Changed |
|-----------|---------|------------|-------|--------------|
| Dependency Awareness | 3 | 4 | +1 | Artifact-level deps via `depends-on-artifacts` and `chart.sh ready` |
| Priority System | 2 | 3 | +1 | `priority-weight` cascading, `chart.sh recommend` |
| Agent-Native Design | 4 | 5 | +1 | Skill routing, AGENTS.md governance, frontmatter triggers |
| Artifact Traceability | 3 | 4 | +1 | Cross-reference validation, commit-pinned staleness, specwatch — but no hard enforcement |
| Multi-Agent / Collaboration | 3 | 4 | +1 | Worktree isolation, atomic claiming, subagent dispatch |
| Portability | 5 | 4 | -1 | Skill layer is a dependency |
| **Total** | **38** | **42** | **+4** | |

Persistence, Cross-Session Continuity, Human Readability, Integration Effort unchanged.

---

## Updated Summary Rankings

| Rank | Method | Score | Best For |
|------|--------|-------|----------|
| **1** | **Swain Integrated Ecosystem** | **42** | Spec-driven projects wanting artifact traceability conventions and agent-native task orchestration |
| 2 | saga-mcp | 40 | Structured hierarchy (Project > Epic > Task > Subtask) without ecosystem adoption |
| 3 | swain-do + tk (standalone) | 38 | Within swain, evaluating the task layer only |
| 3 | Claude Task Master | 38 | PRD-driven greenfield development with AI-powered decomposition |
| 5 | External PM via MCP | 37 | Teams where humans need visibility alongside agent work |
| 6 | Taskwarrior via MCP | 36 | Power users who want sophisticated urgency scoring |
| 7 | Built-in Tasks | 33 | Quick, no-setup task tracking |
| 7 | File-Based Markdown | 33 | Maximum simplicity, solo work |
| 9 | blizzy78 (in-memory) | 28 | Single-session orchestration with critical path |

> **Note**: The gap between swain (42) and saga-mcp (40) is narrow. saga-mcp wins on subtasks and standalone simplicity. Swain wins on artifact traceability and agent-native design. Neither has computed priority.

---

## Updated Capability Gap Matrix

| Method | Projects | Subtasks | Computed Priority | Artifact Lifecycle | Traceability |
|--------|----------|----------|-------------------|-------------------|--------------|
| **Swain Ecosystem** | Yes (Vision > Initiative > Epic > Spec) | No (one-level parent) | No (cascading weight) | Yes (11 types, 3 tracks, prompt-guided) | Convention + validation scripts |
| saga-mcp | Yes (Project > Epic > Task > Subtask) | Yes, multi-level | No (static) | No | No |
| Claude Task Master | Yes (project-scoped JSON) | Yes (AI decomposition) | Yes (complexity scoring) | No | Partial (PRD tracing) |
| Taskwarrior | Yes (`project:` dot hierarchy) | No (flat + deps) | **Yes -- best in class** | No | No |
| Built-in Tasks | No | No (flat with DAG) | No | No | No |
| tk (standalone) | No | No (one-level parent) | No | No | No |

---

## Updated Decision Framework

```
Do you need cross-session persistence?
  NO  --> blizzy78/mcp-task-manager (session planner)
  YES -->
    Do you need artifact/spec traceability?
      YES -->
        Already using swain? --> Swain Integrated Ecosystem
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
