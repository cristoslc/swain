# Task Management Systems for AI Agents — Synthesis

Trove: `task-management-systems` | 5 sources | 2026-03-22

## The question

What task management systems exist for AI coding agents, how do they compare, and what gaps remain — particularly relative to swain-do + tk?

## Key findings

The evaluation rubric [task-tracking-evaluation] provides a structured 10-criterion comparison across 8 approaches, scoring each 1-5. The top scorer is **saga-mcp** (40/50), followed by **swain-do + tk** and **Claude Task Master** (tied at 38/50). The remaining approaches trail: External PM via MCP (37), Taskwarrior via MCP (36), Claude Code Built-in Tasks (33), File-Based Markdown (33), and blizzy78/mcp-task-manager (28).

### Three capability axes differentiate the field

The rubric identifies three capabilities as most differentiating:

1. **Project grouping / hierarchy** — saga-mcp and Claude Task Master support multi-level hierarchy; tk has flat tickets with one-level parent grouping only
2. **Subtask decomposition** — saga-mcp offers unlimited nesting; Claude Task Master has AI-driven decomposition; tk and Built-in Tasks are flat
3. **Computed priority** — Taskwarrior's urgency model is the most principled (multi-factor scoring across due date, age, dependency depth, tags, custom coefficients); no other standalone tool matches it; tk has static 0-4 priority only

### The landscape splits into three design philosophies

1. **Agent-native MCP servers** (saga-mcp, blizzy78, Claude Task Master): Purpose-built for LLM tool calls. Structured APIs, automatic dependency management, session recovery. Trade-off: binary/JSON storage reduces human inspectability.

2. **Human tools with MCP bridges** (Taskwarrior, Linear, Jira, GitHub Issues): Rich existing ecosystems adapted for agent use. Trade-off: verbose APIs, auth overhead, token cost, impedance mismatch between human UI assumptions and agent interaction patterns.

3. **File-based approaches** (tk, Built-in Tasks, todo-md-mcp, Planning with Files): Maximum portability, git-native, human-readable. Trade-off: no computed priority, limited dependency logic, concurrency risks.

### swain's position in the landscape

The rubric correctly identifies that **swain-do + tk scores 38/50 as a tool, but the swain-design ecosystem adds artifact traceability that no other approach matches**. The traceability score (3/5) applies to tk alone — the enforcement comes from swain-design's prompt-driven workflow, not from tk's data model.

This is both a strength and a weakness:
- **Strength**: No other approach links tasks to specs, epics, visions, and ADRs with the rigor that swain-design provides
- **Weakness**: The traceability is soft (prompt-enforced, not schema-enforced), and tk itself has no awareness of the artifact graph

### saga-mcp is the strongest standalone alternative

saga-mcp [saga-mcp] leads on structural capability: Projects > Epics > Tasks > Subtasks with auto-blocking dependencies, threaded comments, templates, activity logging, and a dashboard with natural language summary. 31 MCP tools with safety annotations. SQLite-backed (single .tracker.db file per project). The main weakness: binary storage means no git-diffable task changes and no human inspection without the tool.

### Claude Task Master has the largest community

At 26.1k GitHub stars and 100k+ monthly npm downloads [claude-task-master], Task Master has achieved significant adoption. Its PRD-to-tasks pipeline is the unique differentiator: write a PRD, and the AI decomposes it into tasks with dependencies and complexity scores. It supports selective tool loading (7 core, 15 standard, 36 all) to manage token costs. Weakness: requires an LLM API key for smart features (unless using Claude Code CLI).

### blizzy78 is a session planner, not a task tracker

blizzy78/mcp-task-manager [blizzy78-mcp-task-manager] is in-memory only — no persistence across sessions. Its value is in single-session orchestration with critical path analysis and the `current_task` tool for context recovery after history compaction. It's complementary to a persistent tracker, not a replacement.

### Taskwarrior MCP bridges are immature

The main Taskwarrior MCP server [mcp-server-taskwarrior] (44 stars) has only 3 tools (get_next_tasks, add_task, mark_task_done) and a known bug using unstable task IDs instead of UUIDs. The urgency algorithm remains the best prioritization model in the landscape, but the MCP interface doesn't expose it well. TaskWarrior-NG (meirm/taskwarrior-ng) is exploring a more complete bridge but is early-stage.

## Points of agreement

- **Agent-native design matters more than feature count.** Human tools with MCP adapters pay a persistent tax in token cost, auth complexity, and API verbosity.
- **Persistence must outlive the context window.** In-memory approaches (blizzy78) are useful for session orchestration but insufficient for multi-session projects.
- **Dependency management is table stakes.** Every serious tool supports task dependencies; the differentiator is whether they're manually managed or automatically resolved.
- **No single tool covers all 10 criteria well.** The highest score is 40/50 — there's room for a system that combines file-based readability with structured hierarchy and computed priority.

## Points of disagreement

- **Where should task data live?** SQLite (saga-mcp) vs. JSON files (Task Master, Built-in Tasks) vs. markdown (tk, file-based) vs. cloud (Linear, Jira). Each makes different trade-offs between queryability, diffability, human readability, and portability.
- **Should the AI decompose tasks?** Task Master says yes (PRD-to-tasks is the killer feature). The swain approach says the operator decides (decision support, not autonomous decomposition). This reflects deeper philosophical differences about agent autonomy.
- **Is artifact traceability a tool feature or a workflow feature?** The rubric says it's a workflow concern ("any tool with a text field can link to a spec"). Swain's position is that enforcement matters more than capability — traceability that isn't enforced is traceability that drifts.

## Gaps in the research

- **No head-to-head benchmarks.** The rubric scores are subjective ratings, not measured outcomes. A benchmark measuring actual agent task completion rates across tools would be more informative.
- **No cost analysis.** Token cost per task operation varies dramatically (External PM >> saga-mcp > file-based). This wasn't quantified.
- **Multi-agent coordination barely explored.** Only saga-mcp and External PM tools scored above 3/5 on multi-agent collaboration. As agent parallelism increases, this gap will matter more.
- **swain-design + swain-do ecosystem not evaluated as a unit.** The rubric scores tk in isolation, but the swain value proposition is the integrated ecosystem. A fair comparison would score the full stack.

## Related troves

- `kanban-tools` — covers the visualization layer (daymark-md) that complements task management; focused on markdown-backed kanban boards rather than task tracking systems
