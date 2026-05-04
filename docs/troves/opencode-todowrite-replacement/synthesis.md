# OpenCode todowrite Replacement — Synthesis

Trove: `opencode-todowrite-replacement` | 7 sources | 2026-04-30

## The question

How to replace OpenCode's `todowrite` tool with a persistent, file-based alternative that works reliably with open-weight models and integrates with swain's existing `tk` ticket system -- not bound to a single session.

## Key findings

### Open-weight models struggle with OpenCode's todowrite tool

Multiple GitHub issues document systemic failures when open-weight LLMs attempt to use the `todowrite` tool [opencode-todowrite-issues]:

1. **Stringified JSON errors**: Models send the `todos` array parameter as a JSON string instead of a native array. This is the most frequent failure mode (issues #7512, #1373, #10813).
2. **Tool name confusion**: Models generate `todowrite`, `TodoWrite`, `update_plan`, `TodoRead` -- variants that don't match the actual tool name `todowrite` (issue #234, issue #12938, obra/superpowers#654).
3. **Empty parameter strictness**: Some models fail when calling tools with `{}` in strict mode (issue #11357).
4. **Subagent exclusion**: The `todowrite` tool is deliberately disabled for subagents, and even explicit config enabling doesn't reliably fix this (issue #12938).

These failures often require multiple retries to get the tool call right -- wasting tokens, time, and the operator's patience.

### OpenCode supports full tool replacement

OpenCode's tool system allows complete replacement of built-in tools [opencode-custom-tools-docs, opencode-tools-docs]:

1. **By filename collision**: Place a TypeScript file named `todowrite.ts` in `.opencode/tools/` and it takes precedence over the built-in `todowrite`.
2. **By plugin collision**: A plugin tool with the same name also takes precedence [opencode-plugins-docs].
3. **By permission denial**: Built-in tools can be denied via `opencode.json` permissions without providing a replacement [opencode-tools-docs].

The replacement tool can invoke any external process via `Bun.$` -- including `tk`, the swain ticket CLI.

### Existing trove confirms tk's role in the ecosystem

The `task-management-systems` trove evaluates 8 task management approaches for AI agents. Its synthesis ranks `swain-do + tk` tied for second place (38/50) and notes: "No other approach links tasks to specs, epics, visions, and ADRs with the rigor that swain-design provides." The main weakness identified: flat hierarchy with one-level parent grouping only, and static 0-4 priority with no computed urgency.

### OpenCode has a pending feature request for todo persistence

Issue #18071 [opencode-persistent-todo-issue] requests exactly what we need -- persistent todo storage across sessions -- but proposes a new JSON-based format (`opencode/todo.json`). This would create yet another task tracking format, adding complexity rather than leveraging swain's existing investment in `tk`. The request validates the need for persistence beyond session boundaries.

### tk provides a ready-made persistent backend

tk stores tickets as markdown files in `.tickets/` with:
- **Status management**: open, in_progress, closed.
- **Dependency tracking**: `dep`, `undep`, `dep tree`, `dep cycle` detection.
- **Priority**: 0-4 numeric scale.
- **Tags**: comma-separated, searchable.
- **Atomic claiming**: `tk claim` with lockfile prevents concurrent modifications.
- **Human readability**: markdown files are git-diffable and inspectable in any editor.

tk commands are simple enough for open-weight models to run via bash:
- `tk create "task title" -p 0 -t feature` -- create a ticket.
- `tk start <id>` -- set to in_progress.
- `tk close <id>` -- complete it.
- `tk show <id>` -- read status.
- `tk ready` -- list tasks ready to work on.

### Implementation approach

Three options, from simplest to most integrated:

**Option A -- Bash proxy (simplest)**: Replace `todowrite` with a tool that shells out to `tk` for each operation. The custom tool maps `todowrite` semantics (todos array) onto `tk` commands. Pros: minimal code, trivially debuggable. Cons: the model still needs to use the todowrite parameter schema correctly.

**Option B -- Bash proxy with parameter simplification**: Same as A, but use a flat command string instead of a structured todos array to avoid the stringified-JSON problem entirely. A single `command` parameter like `create "title" --priority high` is easier for open-weight models.

**Option C -- Full integration via plugin**: A TypeScript plugin that intercepts `todo.updated` events and syncs to tk, or replaces the tool entirely with a tk-native interface. Pros: can handle both the tool name collision path and the event hook path. Cons: more code.

## Points of agreement

- **Open-weight models need simpler tool schemas**. The stringified-JSON bug class affects multiple tools (todowrite, bash) across multiple model families. Replacing todowrite with a bash-wrapping tool avoids the structured-parameter problem entirely.
- **Persistence must cross session boundaries**. The in-memory todowrite is adequate for single-session work but fails for any task that spans sessions. tk's file-based persistence solves this natively.
- **Tool replacement is supported and documented**. OpenCode explicitly documents name-collision-based tool replacement. This is a supported extension point, not a hack.
- **tk's markdown format aligns with swain's principles**. Human-readable, git-diffable, no binary blobs -- the same philosophy that drives swain's artifact system.

## Points of disagreement

- **Which replacement approach?** Option A (preserve todowrite schema, proxy to tk) keeps the tool transparent but risks the same parameter errors. Option B (flat command string) is most reliable for open-weight models but diverges from todowrite conventions. Option C (plugin with event hooks) is most complete but most complex.
- **Should we disable or replace?** Disabling `todowrite` via permissions and having the model use bash+tkit directly is simplest but loses the "task tracking" semantic grouping. Replacing it preserves the concept but adds maintenance burden.

## Gaps in the research

- **No empirical comparison of tool reliability across approaches**. We know open-weight models fail on todowrite, but we don't have measured failure rates for Option A vs B vs C.
- **No cost analysis of retries**. Every failed tool call wastes tokens. Quantifying the cost difference between todowrite (multiple retries) and a bash-wrapped tk call (single attempt) would strengthen the case.
- **`todo.updated` event hook behavior untested**. The plugin docs mention a `todo.updated` hook, but no examples exist. Whether it fires for custom tool implementations is unknown.
- **tk's subcommand help output was not captured** as a CLI tool source in this trove. Full tk documentation should be referenced from the `task-management-systems` trove.

## Related troves

- `task-management-systems` -- comprehensive evaluation of 8 task management approaches, places `swain-do + tk` at 38/50. Covers saga-mcp, Claude Task Master, Taskwarrior, and tk in detail.
- `kanban-tools` -- covers markdown-backed kanban boards (daymark-md), complementary visualization layer for tk tasks.
- `subtask2-opencode-commands` -- covers OpenCode custom commands and the TUI command system, relevant for extension patterns.
- `ollama-cloud-dispatch-workers` -- covers open-weight model dispatch through Ollama Cloud, directly relevant to the model families that fail on todowrite.
