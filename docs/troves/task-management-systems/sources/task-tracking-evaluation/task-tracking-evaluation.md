---
source-id: "task-tracking-evaluation"
title: "Task Tracking & Prioritization in Claude Code: Evaluation Rubric"
type: local
path: "/Users/cristos/Downloads/task-tracking-evaluation.md"
fetched: 2026-03-22T00:00:00Z
hash: "d43afa116ac0137cc1cb2bc8c6a0a8626e328792159f73f043222c526e89bd3c"
notes: "Evaluation rubric from the original evaluator comparing 8 task management approaches for AI agent use"
---

# Task Tracking & Prioritization in Claude Code: Evaluation Rubric

## Rubric Criteria

Each method is scored **1–5** per criterion (1 = poor, 5 = excellent).

| # | Criterion | What it measures | Why it matters |
|---|-----------|-----------------|----------------|
| 1 | **Dependency Awareness** | Can tasks block/unblock each other? DAG support? Critical path? | Without this, the agent picks work out of order or starts blocked tasks |
| 2 | **Priority System** | Explicit priority levels, urgency scoring, or smart ordering? | Agents need a deterministic "what's next?" signal, not vibes |
| 3 | **Persistence Model** | Where does state live? Does it survive context compaction, `/clear`, session restarts? | Agent context windows are finite — task state must outlive them |
| 4 | **Agent-Native Design** | Built for AI agents, or human tooling with an adapter? | Human UIs assume visual scanning; agents need structured tool APIs |
| 5 | **Cross-Session Continuity** | Can a new conversation pick up where the last left off? | Long projects span many sessions — handoff fidelity is critical |
| 6 | **Human Readability** | Can a human inspect task state without the agent? | Debugging, auditing, onboarding collaborators |
| 7 | **Integration Effort** | Time from zero to working in Claude Code | High friction = never adopted |
| 8 | **Artifact Traceability** | Links between tasks and specs/PRDs/epics/design docs? | Without provenance, tasks float free of the "why" |
| 9 | **Multi-Agent / Collaboration** | Can multiple agents or humans share task state safely? | Parallel agent workflows and team use |
| 10 | **Portability** | Vendor lock-in? Works offline? Exportable? | You should own your task data, not rent it |

---

## Evaluated Methods

### 1. swain-do + tk (vendored bash ticket system)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 3 | `tk dep` creates directed dependencies; `tk ready` filters by closure. No critical path analysis. **No subtasks** — only one level of nesting (epic → task). Can't decompose tasks further. |
| Priority System | 2 | Numeric 0–4 scale, manually set and static. No urgency decay, no due-date weighting, no computed escalation based on blocked-task count. **No native due date field.** |
| Persistence | 5 | Markdown + YAML frontmatter in `.tickets/`. Git-committable, human-editable. |
| Agent-Native Design | 4 | Designed for agent use via swain skill layer. CLI interface is simple enough for LLM tool calls. |
| Cross-Session Continuity | 5 | Filesystem-based; any session reads `.tickets/`. Spec lineage via `--external-ref`. |
| Human Readability | 5 | Plain markdown files — readable with any text editor or `ls`. |
| Integration Effort | 3 | Requires swain ecosystem (swain-init, swain-doctor, skill vendoring). Non-trivial onboarding. |
| Artifact Traceability | 3 | `--external-ref` and `--tags spec:ID` store links, but this is just a string field — the *enforcement* of traceability comes from swain-design prompts, not tk itself. Any tool with a text field could do this. |
| Multi-Agent / Collaboration | 3 | File-based locking not mentioned; concurrent writes could conflict. Single-agent oriented. |
| Portability | 5 | Pure bash, zero dependencies, filesystem storage. Works anywhere with a shell. |
| **Total** | **38/50** | |

**Strengths**: Fully offline, git-native, human-readable. The swain-design *ecosystem* provides artifact traceability (but that's swain-design, not tk).
**Weaknesses**:
- **No subtasks** — epic → task is the only hierarchy. Multi-level decomposition requires workarounds.
- **No project grouping** — all tickets in one flat `.tickets/` directory. Tags are the only organizing mechanism.
- **Static priority** — set once, never recomputed. No due dates, urgency decay, or dependency-weighted escalation.
- **Ecosystem coupling** — you adopt swain as a whole or not at all.

---

### 2. Claude Code Built-in Tasks (TaskCreate/TaskUpdate/TaskList/TaskGet)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 4 | DAG via `addBlocks`/`addBlockedBy`. No critical path or auto-scheduling. |
| Priority System | 2 | No explicit priority field. Ordering is implicit (by ID). Metadata workaround possible. |
| Persistence | 4 | JSON in `~/.claude/tasks/`. Survives compaction. Not project-scoped by default. |
| Agent-Native Design | 5 | First-party, built into Claude Code's tool set. Zero friction for the agent. |
| Cross-Session Continuity | 4 | Shared via `CLAUDE_CODE_TASK_LIST_ID` env var. Requires explicit setup. |
| Human Readability | 2 | Raw JSON files. No CLI viewer, no pretty-print. |
| Integration Effort | 5 | Already available — zero setup. |
| Artifact Traceability | 1 | No concept of specs, PRDs, or external references. Tasks are standalone. |
| Multi-Agent / Collaboration | 4 | File-based locking for concurrent access. Designed for multi-session use. |
| Portability | 2 | Tied to Claude Code runtime. Not easily consumed by other tools. |
| **Total** | **33/50** | |

**Strengths**: Zero setup, native DAG support, multi-session locking. The agent uses it reflexively — no skill invocation needed.
**Weaknesses**: No priority system, no artifact traceability, poor human readability. Tasks exist in a vacuum with no connection to design intent.

---

### 3. Claude Task Master (task-master-ai)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 4 | Dependencies with automatic "next task" resolution. |
| Priority System | 4 | Complexity scoring + priority ordering. AI-driven decomposition. |
| Persistence | 4 | JSON files in project directory. Git-committable. |
| Agent-Native Design | 5 | Built for AI-driven dev. PRD-in, tasks-out. MCP server or CLI. |
| Cross-Session Continuity | 4 | Project-local JSON. Any session can read. |
| Human Readability | 3 | JSON files; CLI provides formatted output. Not as clean as markdown. |
| Integration Effort | 4 | `npm install -g task-master-ai` or MCP config. Well-documented. |
| Artifact Traceability | 4 | Tasks trace back to PRD sections. Subtask decomposition preserves lineage. |
| Multi-Agent / Collaboration | 3 | File-based, no locking mentioned. Single-agent oriented. |
| Portability | 3 | Requires Node.js. Supports multiple AI providers but needs an LLM API key for decomposition. |
| **Total** | **38/50** | |

**Strengths**: PRD-to-tasks pipeline is compelling — feed it a doc, get a structured plan. 25k+ GitHub stars; active community. Good for greenfield projects.
**Weaknesses**: Requires Node.js + AI API key for smart features. JSON is less human-friendly than markdown.

---

### 4. saga-mcp (SQLite Jira-like for agents)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 5 | Auto-blocking/unblocking when dependencies complete. |
| Priority System | 4 | Explicit priority fields. |
| Persistence | 5 | SQLite per project (`.tracker.db`). Durable, queryable, single-file. |
| Agent-Native Design | 5 | 22 MCP tools. Built for agent workflows. Activity logging + dashboard. |
| Cross-Session Continuity | 5 | SQLite file persists across everything. |
| Human Readability | 2 | SQLite binary — need a viewer or the MCP tools to inspect. |
| Integration Effort | 4 | MCP config. Auto-creates DB on first use. No API keys. |
| Artifact Traceability | 3 | Project > Epic > Task > Subtask hierarchy. No external doc refs. |
| Multi-Agent / Collaboration | 3 | SQLite supports concurrent reads but writes need care. |
| Portability | 4 | SQLite is universal. No cloud dependency. |
| **Total** | **40/50** | |

**Strengths**: Richest data model of the standalone options. Auto-blocking is a killer feature — agents don't need to manually check dependency status. Activity logging provides audit trail.
**Weaknesses**: Binary storage means you can't git-diff task changes. No design doc linkage.

---

### 5. External PM Tools via MCP (Linear, GitHub Issues, Jira, Notion)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 3 | Varies. Linear has relations; GitHub Issues has loose references; Jira has full linking. |
| Priority System | 4 | All have built-in priority systems designed for human teams. |
| Persistence | 5 | Cloud-hosted, backed up, highly durable. |
| Agent-Native Design | 2 | Human-first tools with MCP adapters. Noisy APIs, rate limits, auth overhead. |
| Cross-Session Continuity | 5 | Cloud state is always current. |
| Human Readability | 5 | Full web UIs, mobile apps, dashboards, notifications. |
| Integration Effort | 3 | MCP setup + auth tokens/OAuth. Some are official (Linear, GitHub, Notion), others community. |
| Artifact Traceability | 3 | Depends on team discipline. Tools support linking but don't enforce it. |
| Multi-Agent / Collaboration | 5 | Designed for teams. Concurrent access is core. |
| Portability | 2 | Vendor-locked. Data export varies. Requires internet. |
| **Total** | **37/50** | |

**Strengths**: Best for teams where humans also need visibility. You already have Notion connected. If your org uses Linear or Jira, this creates a single source of truth.
**Weaknesses**: Round-trip latency, rate limits, auth complexity. The agent pays a token tax describing/parsing rich API responses. Offline = dead.

---

### 6. Taskwarrior via MCP

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 4 | Native `depends:` field. Urgency coefficient system factors in dependencies. |
| Priority System | 5 | H/M/L priorities + multi-factor urgency scoring (due date, age, blocks, tags, etc.). Most sophisticated priority model of any option. |
| Persistence | 5 | Local file-based (`~/.task/`). Syncs via Taskserver or third-party. |
| Agent-Native Design | 2 | Human-first CLI. MCP bridges add agent access but the API surface is large and idiosyncratic. |
| Cross-Session Continuity | 5 | Filesystem state persists indefinitely. |
| Human Readability | 4 | Excellent CLI output. `task next` is immediately useful. Reports are customizable. |
| Integration Effort | 3 | Requires Taskwarrior installed + MCP server. omniwaifu's version has 22 tools — capable but complex. |
| Artifact Traceability | 2 | Tags and annotations can link to docs, but no structured spec/PRD system. |
| Multi-Agent / Collaboration | 2 | Single-user design. Taskserver sync exists but isn't agent-aware. |
| Portability | 4 | Open source, runs everywhere, plain-text storage. But Taskwarrior itself is a dependency. |
| **Total** | **36/50** | |

**Strengths**: The urgency scoring is genuinely brilliant — it weights due dates, dependency chains, age, and custom coefficients to surface the single most important task. Battle-tested over 15+ years.
**Weaknesses**: The MCP bridges are immature (ID vs UUID bugs noted). Human-first design means the agent fights an interface not designed for it.

---

### 7. File-Based Markdown (todo-md-mcp, Planning with Files, Nick Tune's approach)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 1 | None in todo-md-mcp. Implicit via phase ordering in Planning with Files. |
| Priority System | 1 | Manual ordering only. No computed priority. |
| Persistence | 5 | Markdown files. Git-native, survives everything. |
| Agent-Native Design | 3 | Simple enough for agents. Planning with Files specifically handles context compaction recovery. |
| Cross-Session Continuity | 5 | Files persist. Planning with Files auto-recovers after `/clear`. |
| Human Readability | 5 | Peak readability — it's just markdown with checkboxes. |
| Integration Effort | 5 | Near-zero. A markdown file and maybe a CLAUDE.md rule. |
| Artifact Traceability | 2 | Manual cross-references at best. |
| Multi-Agent / Collaboration | 1 | No concurrency handling. Merge conflicts on shared files. |
| Portability | 5 | A text file. Maximum portability. |
| **Total** | **33/50** | |

**Strengths**: Lowest possible friction. Great for solo work on small-medium projects. Git diff shows exactly what changed. Nick Tune's hook-driven evolution shows this can scale with discipline.
**Weaknesses**: No dependency logic, no priority computation. Relies entirely on the agent (or human) to maintain ordering discipline. Breaks down with complexity.

---

### 8. blizzy78/mcp-task-manager (in-memory, session-scoped)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Dependency Awareness | 5 | Subtask sequencing, parallel task support, critical path analysis. |
| Priority System | 3 | Implicit via sequence ordering. No explicit priority field. |
| Persistence | 1 | In-memory only. Lost on session end. |
| Agent-Native Design | 5 | `SINGLE_AGENT=true` mode with `current_task` for context-compacted agents. |
| Cross-Session Continuity | 1 | None. Session-scoped by design. |
| Human Readability | 2 | Only visible through MCP tool calls. |
| Integration Effort | 5 | `npx -y @blizzy/mcp-task-manager`. One line. |
| Artifact Traceability | 1 | No external references. |
| Multi-Agent / Collaboration | 2 | Single-agent mode is the primary use case. |
| Portability | 3 | Node.js dependency. But ephemeral — nothing to export. |
| **Total** | **28/50** | |

**Strengths**: Best critical path analysis. The `current_task` tool for context-compacted agents is a clever design. Perfect for single-session complex tasks.
**Weaknesses**: Ephemeral. If your session dies, everything is gone. Not a task tracker — more of a session planner.

---

## Summary Rankings

| Rank | Method | Score | Best For |
|------|--------|-------|----------|
| 1 | **saga-mcp** | 40 | Complex projects needing structured hierarchy (Project > Epic > Task > Subtask) without cloud dependencies |
| 2 | **swain-do + tk** | 38 | Spec-driven projects within the swain ecosystem (traceability comes from swain-design, not tk) |
| 2 | **Claude Task Master** | 38 | PRD-driven greenfield development with AI-powered decomposition |
| 4 | **External PM via MCP** | 37 | Teams where humans need visibility alongside agent work |
| 5 | **Taskwarrior via MCP** | 36 | Power users who want sophisticated urgency scoring |
| 6 | **Built-in Tasks** | 33 | Quick, no-setup task tracking within/across sessions |
| 6 | **File-Based Markdown** | 33 | Maximum simplicity, solo work, small projects |
| 8 | **blizzy78 (in-memory)** | 28 | Single-session complex orchestration with critical path needs |

> **Note on revised scores:** swain-do/tk was initially scored 43/50. After scrutiny, scores were corrected downward for Priority System (4→2: static only, no due dates), Dependency Awareness (4→3: no subtasks), and Artifact Traceability (5→3: traceability is a swain-design feature, not tk's). saga-mcp now leads on structural capability.

---

## Decision Framework

```
Do you need cross-session persistence?
  NO  --> blizzy78/mcp-task-manager (session planner)
  YES -->
    Do you need artifact/spec traceability?
      YES -->
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

---

## Key Capability Gaps: Projects, Subtasks, and Computed Priority

These three capabilities emerged as the most differentiating across all methods:

| Method | Projects | Subtasks | Computed Priority |
|--------|----------|----------|-------------------|
| **saga-mcp** | Yes (Project → Epic → Task → Subtask) | Yes, multi-level | No (static fields) |
| **Claude Task Master** | Yes (project-scoped JSON) | Yes (AI-driven decomposition) | Yes (complexity scoring) |
| **Jira via MCP** | Yes (full project hierarchy) | Yes (unlimited nesting) | Yes (JQL + sprint planning) |
| **Linear via MCP** | Yes (Team → Project → Issue → Sub-issue) | Yes (sub-issues) | Yes (priority + cycle-based) |
| **Taskwarrior** | Yes (`project:` with dot hierarchy: `project:auth.jwt.tests`) | No (flat tasks + deps) | **Yes — best in class** (multi-factor urgency) |
| **Built-in Tasks** | No | No (flat with DAG) | No |
| **tk (swain-do)** | No | No (one-level parent only) | No |
| **File-Based Markdown** | No | No | No |
| **blizzy78** | No | Yes (sequenced subtasks) | No |

## Next Steps: What to Investigate

1. **saga-mcp** — Install and test. Best local data model with subtasks + projects + auto-blocking. Main concern: can you inspect state without the agent (SQLite readability)?
2. **Claude Task Master** — Test PRD decomposition quality. Is the AI-driven task breakdown actually useful or a gimmick? 25k stars suggests real value.
3. **Taskwarrior urgency model** — Even if the MCP bridges are immature, the urgency scoring math is worth studying as a design reference for any system.
4. **Linear via MCP** — Evaluate if team visibility (beyond solo agent use) is a requirement. If others need to see task state, this is the strongest option.

## Deep Dive: Taskwarrior

### Pros

- **Extremely flexible** — filters, custom reports, UDAs (User Defined Attributes), and hooks mean you can mold it to almost any workflow
- **CLI-native** — fast, scriptable, composable with other Unix tools
- **Urgency algorithm** — automatically surfaces what matters most via multi-factor scoring (priority, due date, age, dependency depth, tags, custom coefficients) without manual sorting
- **Plain text data** — `~/.task/` is easy to back up, version control, inspect, and migrate
- **Offline-first** — no internet dependency; sync is optional
- **Rich metadata model** — projects (with dot-hierarchy like `project:auth.jwt`), tags, priorities, dependencies, annotations, recurrence all built in
- **Battle-tested** — 15+ years of active development and community

### Cons

- **Steep learning curve** — the filter syntax and configuration options are powerful but dense
- **Sync is painful** — Taskserver (taskd) is notoriously difficult to self-host; this has been a top complaint for years. Many users resort to Syncthing or similar file-sync workarounds
- **No built-in GUI** — third-party frontends (taskwarrior-tui, Inthe.AM, Foreground) exist but none are polished enough to be "the" answer
- **Urgency tuning** — the default urgency coefficients rarely match what people actually want; requires experimentation to dial in
- **Recurring tasks** — the recurrence model has known quirks and edge cases
- **Taskwarrior 3 uncertainty** — the Rust rewrite (taskchampion) has been in progress for a long time, leaving the future somewhat unclear
- **Single-user oriented** — no real team/collaboration features
- **No subtasks** — flat task model with dependencies only; no hierarchical decomposition

### Competitor Landscape

| Tool | Style | Strength | Weakness vs Taskwarrior |
|------|-------|----------|------------------------|
| **Todoist** | SaaS, GUI/mobile | Polished UI, natural language input, cross-platform sync | No urgency scoring, vendor-locked, no CLI power |
| **Things 3** | macOS/iOS native | Beautiful design, great for personal GTD | Apple-only, no CLI, no extensibility |
| **Org-mode** (Emacs) | Text-based, editor-integrated | Notes + tasks + agenda unified; incredibly powerful | Requires Emacs; even steeper learning curve |
| **todo.txt** | CLI, plain text | Much simpler — just a text file with conventions | No dependencies, no urgency, no reports |
| **Obsidian Tasks** | Markdown-based | Tasks embedded in notes, good for knowledge workers | No dependency logic, no computed priority |
| **TickTick** | SaaS, GUI/mobile | Habit tracking, calendar integration, Pomodoro built in | SaaS dependency, weaker CLI story |
| **Linear** | SaaS, team-oriented | Best-in-class for software team issue tracking | Cloud-only, team-oriented (overkill for solo) |
| **Notion** | SaaS, flexible | Tasks as part of broader workspace; very customizable | Slow, cloud-only, no urgency model |

### How to Choose

- **Want power + CLI?** → Taskwarrior or Org-mode
- **Want simplicity + CLI?** → todo.txt
- **Want polish + mobile?** → Todoist, Things, or TickTick
- **Want tasks embedded in notes?** → Org-mode or Obsidian
- **Need team collaboration?** → Linear, Notion, or Todoist Business

Taskwarrior's sweet spot is **power users who live in the terminal** and want full control over their task model. If that's not you, the overhead may not be worth it.

### Relevance to This Evaluation

Taskwarrior's urgency scoring remains the most principled prioritization model of any option evaluated here. Even if the MCP bridges are immature (ID vs UUID bugs), the urgency math — weighting due dates, dependency chains, age, and custom coefficients — is worth studying as a design reference for any agent-native task system. The main gap for agent use is that Taskwarrior was designed for humans typing commands, not for structured tool APIs.

---

## Notes

- **Hybrid approaches work well.** You could use built-in Tasks for session-level orchestration while syncing milestones to Linear/Notion for human visibility.
- **Taskwarrior's urgency model** is worth studying even if you don't adopt it — the multi-factor scoring (priority + due + age + dependency depth + tags) is the most principled prioritization system in this list.
- **Artifact traceability is a workflow concern, not a tool feature.** Any tool with a text/tag field can link to a spec. The question is whether the *process* enforces it. swain-design does this via prompt engineering, not via tk.
- **Context window cost** matters. External PM tools (Jira, Linear) return verbose JSON that eats tokens. File-based and CLI approaches are leaner.
