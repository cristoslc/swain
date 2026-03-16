# Kanban Tools for Markdown — Synthesis

Evidence pool: `kanban-tools` | 17 sources | 2026-03-15

## The question

Should swain build daymark-md, or does an existing tool already solve the problem of visualizing a tree of markdown artifacts — each with YAML frontmatter tracking lifecycle phases — as an interactive kanban board?

## Key finding: nothing in the landscape does what daymark proposes

The research surveyed 9 existing tools across 4 categories (CLI/TUI boards, VS Code extensions, Obsidian plugins, self-hosted web apps). **None of them operate in daymark's design space.** The landscape splits into two fundamentally different models, and daymark occupies a third that no existing tool addresses.

### Model 1: Board-owns-the-data (task managers)

Tools: kanban-md [004], kanban-tui [008], Agent Kanban [007], Tasks.md [010], taskell [012]

These tools **create and manage their own task files or databases**. You interact with the board, and it writes the data. The board is the source of truth. They compete with `tk` (ticket), not with daymark.

- kanban-md: Go binary, markdown files with frontmatter, but it _creates_ task files — it doesn't read existing ones
- kanban-tui: SQLite backend, agent-friendly CLI, but no filesystem/frontmatter awareness
- Agent Kanban: VS Code + Copilot task workflow, directory-based lanes, own file format
- Tasks.md: Docker-based, directory-per-lane, own file structure
- taskell: Single-file board (headings = columns, lists = tasks)

**None of these can read an existing folder of artifacts and derive a board from their frontmatter.**

### Model 2: Board-inside-the-editor (plugins)

Tools: Obsidian Kanban [005], md-board [006]

These are editor plugins that render kanban views inside a specific application.

- Obsidian Kanban: Board _is_ a special markdown file within Obsidian. Cards are list items, not external files. Locked to Obsidian.
- md-board: Closest to daymark — reads a folder of markdown files as a board. But columns come from **subdirectory names**, not frontmatter fields. No multi-track, no phase ordering, no lifecycle awareness. 8 installs, very early stage, VS Code only.

### Model 3: Filesystem-reader with lifecycle awareness (daymark's niche)

Tools: daymark-md [001-003] (proposed, not yet built)

Daymark proposes a model where:
1. **Your existing files are the source of truth** — no new data format, no shadow state
2. **A configurable frontmatter field drives columns** — not directory names, not inline tokens
3. **Multiple tracks with different phase sequences** — implementable, container, standing artifacts each follow their own lifecycle
4. **Forward-only transition enforcement** — optional, per-track
5. **Phase subdirectory awareness** — can move files between subdirectories on transition
6. **Standalone local web app** — no editor lock-in, `uvx daymark-md` and go

**No existing tool offers this combination.** The closest is md-board [006], but it uses directories for columns (not frontmatter), has no multi-track support, no phase ordering, and requires VS Code.

## Points of agreement across the landscape

- **Markdown + frontmatter is the right data format** for developer-facing project management. Every tool in the survey either uses it or wishes it did (fd93 essay [011] explicitly identifies the lack of frontmatter as the key limitation of pure-filesystem kanban).
- **Local-first, no-database** is a strong trend. Most new tools reject cloud sync and external databases.
- **Agent-friendliness** is a 2025-2026 differentiator. kanban-md, kanban-tui, and Agent Kanban all market agent compatibility. Daymark doesn't need to be agent-operated (swain agents use `tk` for task tracking), but it should be agent-_readable_ (its config and file state should be inspectable via CLI).
- **File watching + live update** is table stakes. Every tool with a UI supports it.

## Points of disagreement

- **What "markdown kanban" means**: Some tools store the board _as_ markdown (taskell, Obsidian Kanban). Others store tasks _as_ markdown files (kanban-md, Tasks.md, Agent Kanban). Daymark reads _existing_ markdown files and _derives_ a board. These are three different things with the same label.
- **Directory vs frontmatter for column assignment**: md-board and Tasks.md use directories. Daymark uses a frontmatter field. For swain, frontmatter is authoritative (swain-design writes `status:` to frontmatter), and directory placement is a derived/optional signal.

## Near-miss alternatives [017]

A second research pass looked beyond kanban tools at headless CMS tools, knowledge bases, and content dashboards that read markdown frontmatter.

### Front Matter CMS (VS Code extension) — closest near-miss

Front Matter CMS has a dashboard that shows markdown files as cards in a grid, can **group by a custom frontmatter field** (including `status`), and filter by any field. This is the closest existing tool to what daymark does.

**Why it's not enough:**
- **Grid layout, not kanban columns** — you see cards filtered by status, but not columns showing all statuses at once with cards in each. You'd have to mentally reconstruct the lifecycle by toggling filters.
- **No drag-and-drop transitions** — you edit the status field in a form panel, not by dragging a card between columns.
- **No multi-track lifecycle** — single flat collection, no concept of different artifact types following different phase sequences.
- **No phase ordering or forward-only enforcement**.
- **VS Code only** — not a standalone web app.

If Front Matter CMS added a kanban layout option, it would be a serious contender. But that's a feature request on someone else's roadmap, not something swain can depend on.

### Everything else: not close

- **Git-based headless CMS tools** (Decap, TinaCMS, Sveltia): Designed for static site content editing, not project lifecycle. Editorial list views, no board layouts.
- **Datasette + markdown-to-sqlite**: Could theoretically ingest frontmatter into SQLite and render a board via plugin. But adds SQLite as an intermediary, loses real-time file watching, and requires custom plugin development. More complexity, no benefit.
- **Knowledge bases** (Foam, Dendron): Note-taking tools with graph visualization. No lifecycle boards.
- **Markdown++**: Browser-based content panel. Table view only, no board layout.

## Gaps in the research

- **Obsidian Dataview + custom CSS**: Obsidian's Dataview plugin can query frontmatter fields and render results as tables. Combined with custom CSS snippets or the "Cards" CSS hack, some users approximate a kanban view inside Obsidian. This is fragile, Obsidian-locked, and doesn't support drag-and-drop transitions — but worth noting as the most creative workaround in the community.
- **No generic "frontmatter-to-board" web tool was found** beyond daymark's own design docs. After two passes (kanban tools + broader CMS/dashboard/knowledge-base tools), this appears to be a genuinely unoccupied niche.

## Verdict from swain's perspective

**Build daymark-md.** The research confirms:

1. **No existing tool reads arbitrary markdown files, groups them by a configurable frontmatter field, and renders a multi-track kanban board.** This is not a crowded space with a clear winner — it's an empty space.
2. **Swain's data model (frontmatter-driven lifecycle phases, multiple tracks, phase subdirectories) is unique enough** that adapting an existing tool would mean forking it and rewriting the core data layer — more work than building daymark's focused feature set from scratch.
3. **The architecture is small and well-scoped**: scanner + mutator + watcher + static frontend. Python + starlette + watchfiles. No framework dependencies, no build step. This is a weekend-to-week project, not a multi-month platform build.
4. **The tool has standalone value beyond swain**: any project using markdown files with a status-like frontmatter field can use it. Blog pipelines, documentation workflows, research note management. This makes it worth publishing as a PyPI package.

### Integration model: daymark + swain-status + swain-do

Daymark is not independent from swain-status — it's the **visual control surface** that augments swain-status's CLI dashboard. The integration path:

1. **Daymark** = visual operator console. Drag a card (e.g., SPEC-014 from Proposed → Ready) and it writes the frontmatter change to disk.
2. **swain-status** = reactive watcher. Detects phase transitions on disk (via filesystem events or polling) and interprets them as lifecycle events.
3. **swain-do** = downstream executor. When swain-status detects a meaningful transition (e.g., a SPEC entering Ready), it kicks off implementation tracking — creating a plan, ingesting tasks.

This makes the operator's workflow: **see the board → drag a card → swain reacts**. The visual surface becomes the primary way the operator steers artifact lifecycle, with swain-status and swain-do handling the reactive downstream work.

## Reactive loop feasibility

The second research question: can swain reliably detect and respond to frontmatter changes on disk — whether from daymark, manual vim edits, or any other tool?

### The core challenge: file change ≠ lifecycle transition

Filesystem watchers (watchfiles [013], watchdog) report "this file was modified." They don't report "the `status` field changed from `Proposed` to `Ready`." Swain needs a **frontmatter diff layer** between the raw filesystem event and the downstream reaction.

### Architecture of the diff layer

```
filesystem event (file modified)
    → debounce (100-500ms, handled by watchfiles [013])
    → re-parse frontmatter (python-frontmatter [016])
    → compare to cached frontmatter snapshot
    → if column_field changed: emit transition event
    → if column_field unchanged: ignore (body-only edit, metadata change, etc.)
```

This is straightforward to build. The cache is an in-memory dict of `{path: {field: value}}`, populated on startup by scanning all files (which daymark's scanner already does), and updated on each processed change event.

### Event-driven vs polling [014]

| Approach | Latency | Reliability | Complexity |
|----------|---------|-------------|------------|
| **watchfiles** (FSEvents/inotify) | ~100ms | Good with debouncing; known pitfalls with atomic saves, git operations | Moderate — need frontmatter cache + diff |
| **Polling** (re-scan every N seconds) | 1-5s | Very high — no platform quirks | Low — just re-scan and diff |
| **Git hooks** (post-commit) [015] | Until commit | Very high — atomic, no duplicates | Low — diff HEAD vs HEAD~1 |
| **Hybrid** (watch + git hook backstop) | ~100ms + commit validation | Highest | Moderate |

**Recommendation for swain:** Start with **polling** (re-scan every 2-3 seconds). It's simpler, more reliable, and swain's `docs/` folder is small enough that the scan cost is negligible. If latency matters later, add watchfiles as an optimization. Git hooks add a reliability backstop for committed changes.

The key insight from the research [014]: for fewer than ~100 files (swain's typical artifact count), polling with content comparison is simpler and equally reliable as event-driven watching. Filesystem watchers shine for large directory trees — swain doesn't need that.

### Where does the watcher live?

Three options for where the reactive watcher component runs:

1. **Inside daymark**: Daymark already scans files and watches for changes. It could emit lifecycle events as a side effect. But this couples swain's reactivity to daymark being running — if the operator edits files without daymark open, no reaction.

2. **Inside swain-status**: A new `swain-status --watch` mode that polls the docs directory, maintains a frontmatter cache, and triggers swain-do on transitions. Runs independently of daymark. This is the right home — swain-status already understands artifact lifecycle.

3. **Standalone daemon**: A separate `swain-watch` process. More operational overhead for questionable benefit over option 2.

**Recommendation:** Option 2. `swain-status --watch` (or a dedicated swain-watch mode) polls `docs/`, diffs frontmatter, and reacts. Daymark is purely visual — it writes frontmatter and that's it. The watcher catches the change regardless of whether it came from daymark, vim, or `swain-design`.

### What reactions make sense?

Not every frontmatter change should trigger a downstream action. The watcher needs a **reaction map** — configurable rules for which transitions trigger which actions:

| Transition | Reaction |
|-----------|----------|
| SPEC: Proposed → Ready | Prompt operator: "SPEC-014 is ready. Create implementation plan?" |
| SPEC: Ready → Active | Run swain-do to create task tracking |
| EPIC: all child SPECs complete | Prompt operator: "All specs for EPIC-021 are complete. Transition to Complete?" |
| Any artifact → terminal state | Archive notification, update status dashboard |

The watcher should **prompt the operator, not act autonomously** — except for read-only reactions (updating the dashboard). Autonomous actions (creating tasks, transitioning other artifacts) need operator confirmation. This preserves the swain principle: "decision support for the operator."

### Feasibility verdict

**The reactive loop is feasible and well within reach.** The building blocks are all standard:

- File scanning + frontmatter parsing: `python-frontmatter` [016]
- Change detection: polling (simplest) or watchfiles [013] (faster)
- Transition diffing: in-memory cache + field comparison
- Downstream triggering: shell out to `tk` or invoke swain-do

The hard part isn't technical — it's designing the reaction map so swain is helpful without being noisy. That's a UX question, not an engineering question.

### Risks to monitor

- **Scope creep toward task management**: Daymark should stay a _viewer and transitioner_ of existing files, not evolve into a task manager that competes with tk. The "what it doesn't do" section in the Vision [002] is load-bearing — but "trigger downstream workflows via phase transitions" is firmly in scope.
- **Frontend complexity**: "Static HTML + vanilla JS + CSS, no build step" is the right call for v1. Resist the pull toward React/Vue/Svelte until the interaction model is validated.
- **Noisy reactions**: The watcher must not spam the operator with prompts for every minor frontmatter edit. The reaction map needs sensible defaults and a way to suppress noise (e.g., only react to `column_field` changes, not arbitrary frontmatter edits).
- **Source ambiguity**: The watcher can't distinguish "operator dragged in daymark" from "agent ran swain-design." Both are frontmatter writes. This is actually fine — the watcher reacts to the *state change*, not the *source*. But reactions that would create infinite loops (swain-do writes frontmatter → watcher triggers swain-do again) must be guarded against.
