# Micode Snapshot

Captured: 2026-04-23 from https://github.com/vtemian/micode

## Overview

**Micode** is an OpenCode plugin (v0.10.0, MIT license) implementing a structured **Brainstorm → Plan → Implement** workflow with session continuity. It's built on the `@opencode-ai/plugin` SDK (TypeScript/Bun) and provides agents, tools, hooks, and a browser-based brainstorming UI (Octto).

- **License**: MIT (Copyright 2026 vtemian)
- **Language**: TypeScript, targeting Bun runtime
- **Build**: `bun build src/index.ts --outdir dist --target bun --external bun-pty`
- **Test**: `bun test` (Bun native test runner)
- **Quality gate**: Biome + ESLint + TypeScript + tests via `bun run check`

## Project Structure

```
micode/
├── .mindmodel/          # Project-specific coding pattern constraints
│   ├── manifest.yaml
│   ├── architecture/    # Layers, organization
│   ├── components/      # Shared patterns
│   ├── domain/          # Concepts
│   ├── ops/             # Database patterns
│   ├── patterns/        # Data-fetching, error-handling, logging, testing, validation
│   ├── stack/           # Backend, database, dependencies
│   └── style/           # Imports, naming, types
├── .opencode/agent/     # OpenCode agent configs (deployer.md)
├── src/
│   ├── agents/          # Agent config objects (pure data, no logic)
│   │   ├── commander.ts      # Primary orchestrator
│   │   ├── brainstormer.ts   # Design exploration (primary)
│   │   ├── planner.ts        # Micro-task plan creation (subagent)
│   │   ├── executor.ts       # Batch-first parallel execution (subagent)
│   │   ├── implementer.ts    # Single micro-task executor (subagent)
│   │   ├── reviewer.ts       # Code review (subagent)
│   │   ├── octto.ts          # Browser-based brainstorming (primary)
│   │   ├── bootstrapper.ts  # Branch creation for octto (subagent)
│   │   ├── codebase-locator.ts
│   │   ├── codebase-analyzer.ts
│   │   ├── pattern-finder.ts
│   │   ├── ledger-creator.ts
│   │   ├── artifact-searcher.ts
│   │   ├── project-initializer.ts
│   │   ├── probe.ts
│   │   └── mindmodel/        # Mindmodel generation/analysis agents
│   ├── hooks/           # Lifecycle hook factories
│   │   ├── auto-compact.ts       # Auto-summarize at 50% context
│   │   ├── ledger-loader.ts      # Inject continuity ledger into system prompt
│   │   ├── session-recovery.ts   # Recover from API errors
│   │   ├── context-injector.ts  # Inject ARCHITECTURE.md, CODE_STYLE.md
│   │   ├── comment-checker.ts    # Remove developer comments from code
│   │   ├── artifact-auto-index.ts
│   │   ├── fetch-tracker.ts
│   │   ├── file-ops-tracker.ts
│   │   ├── fragment-injector.ts  # User-defined prompt fragments
│   │   ├── mindmodel-injector.ts # Inject .mindmodel/ patterns
│   │   ├── constraint-reviewer.ts # Review code against mindmodel
│   │   └── token-aware-truncation.ts
│   ├── tools/           # Tool definitions
│   │   ├── spawn-agent.ts    # Parallel subagent spawning
│   │   ├── artifact-search.ts
│   │   ├── ast-grep/        # AST-aware search/replace
│   │   ├── batch-read.ts     # Parallel file reads
│   │   ├── btca/             # Library source search
│   │   ├── look-at.ts        # File structure extractor
│   │   ├── milestone-artifact-search.ts
│   │   ├── mindmodel-lookup.ts
│   │   ├── octto/            # Browser brainstorming tools
│   │   │   ├── brainstorm.ts
│   │   │   ├── session.ts
│   │   │   ├── processor.ts
│   │   │   ├── questions.ts
│   │   │   ├── responses.ts
│   │   │   ├── formatters.ts
│   │   │   ├── extractor.ts
│   │   │   ├── factory.ts
│   │   │   └── utils.ts
│   │   └── pty/              # Background terminal sessions
│   ├── octto/           # Browser-based brainstorming UI
│   │   ├── session/      # WebSocket session lifecycle
│   │   ├── state/        # Branch state persistence
│   │   └── ui/           # HTML bundle
│   ├── indexing/         # Milestone artifact classification/ingestion
│   ├── mindmodel/        # Mindmodel loader, classifier, formatter, review
│   ├── config-loader.ts  # Loads micode.json / opencode.json config
│   ├── config-schemas.ts # Valibot validation schemas
│   ├── index.ts          # Main plugin entry point
│   └── utils/            # Shared utilities
│       ├── config.ts     # Centralized tunables
│       ├── errors.ts     # Error extraction
│       ├── logger.ts     # Structured logging
│       └── model-limits.ts # Context window limits
├── tests/               # Mirrors src/ structure
├── CLAUDE.md            # Project rules / coding conventions
├── INSTALL_CLAUDE.md   # Installation instructions
├── package.json         # v0.10.0, MIT
├── biome.json           # Linting/formatting config
├── eslint.config.js     # ESLint config
├── lefthook.yml         # Git hooks config
└── tsconfig.json
```

## 1. Brainstorm-Plan-Implement Workflow

### Three-Phase Pipeline

The workflow is a linear pipeline: **Brainstorm → Plan → Implement**, with each phase producing artifacts that the next consumes.

**Phase 1: Brainstorm (primary agent)**
- User invokes brainstormer directly (or commander tells user to invoke it)
- Spawns research subagents (codebase-locator, codebase-analyzer, pattern-finder) in parallel
- Explores 2-3 approaches, recommends one
- Produces: `thoughts/shared/designs/YYYY-MM-DD-{topic}-design.md`
- Automatically hands off to planner on completion

**Phase 2: Plan (subagent)**
- Receives design document as input
- Does minimal research (mostly reads design doc directly)
- Calls `mindmodel_lookup` for project patterns first
- Creates micro-tasks: ONE file per task, grouped into parallel batches
- Produces: `thoughts/shared/plans/YYYY-MM-DD-{topic}.md`
- Each task has complete, copy-paste-ready code, exact file paths, and test commands

**Phase 3: Implement (subagent orchestration)**
- **Executor** parses the plan's batch structure and dependency graph
- For each batch:
  1. Fires ALL implementers in parallel (10-20 simultaneous via `spawn_agent`)
  2. Fires ALL reviewers in parallel
  3. Handles CHANGES_REQUESTED (max 3 review cycles, then marks BLOCKED)
  4. Moves to next batch only when all tasks pass or are blocked
- Implementer follows TDD: write test → verify fail → write code → verify pass
- No commits during implementation (executor batches commits)

### Quick-Mode Decision Tree

For trivial tasks, the workflow is skipped entirely:
- **Under 2 minutes**: Just do it (typo fix, version bump)
- **Small tasks**: Brief mental plan, then execute (simple function, failing test fix)
- **Complex**: Full brainstorm → plan → execute

### Octto (Browser-Based Brainstorming)

An alternative brainstorming path using a browser UI:
1. User invokes `/octto` or brainstormer detects interactive design needed
2. Bootstrapper subagent creates branch structure (2-4 branches with scopes)
3. `create_brainstorm` starts a WebSocket server + opens browser
4. Questions appear in browser with rich UI (pick_one, pick_many, slider, thumbs, etc.)
5. `await_brainstorm_complete` processes all answers asynchronously
6. `end_brainstorm` writes design document

## 2. Subagent Orchestration Mechanism

### Primary vs Subagent Modes

- **Primary agents** (commander, brainstormer, octto): Use the built-in `Task` tool to spawn subagents
- **Subagents** (planner, executor, implementer, reviewer, etc.): Use the `spawn_agent` tool to spawn other subagents

### Two Spawning Mechanisms

**Task tool** (for primary agents):
- Built into OpenCode, spawns synchronously
- Results available immediately when the subagent completes

**spawn_agent tool** (for subagents):
- Custom tool defined in `src/tools/spawn-agent.ts`
- Accepts an array of agents for **parallel execution** via `Promise.all`
- Creates OpenCode sessions via `ctx.client.session.create()`, sends prompt, retrieves messages
- Progress tracking with metadata updates
- Single agent: runs synchronously, returns immediately
- Multiple agents: all run in parallel, results concatenated

### Executor's Batch-First Pattern

The executor's orchestration is the most sophisticated:

```
For each batch in plan:
  1. spawn_agent([implementer_1, implementer_2, ..., implementer_N])  // ALL parallel
  2. spawn_agent([reviewer_1, reviewer_2, ..., reviewer_N])           // ALL parallel
  3. For failures: spawn_agent([fix_1, fix_2, ...])                    // parallel fixes
  4. spawn_agent([re_reviewer_1, re_reviewer_2, ...])                // parallel re-reviews
  5. Max 3 review cycles per task, then BLOCKED
```

### Available Agent Roster

| Agent | Mode | Purpose |
|-------|------|---------|
| commander | primary | Orchestrator, makes decisions |
| brainstormer | primary | Design exploration |
| octto | primary | Browser-based brainstorming |
| planner | subagent | Micro-task plan creation |
| executor | subagent | Batch-first parallel execution |
| implementer | subagent | Single micro-task (1 file + test) |
| reviewer | subagent | Code review |
| codebase-locator | subagent | Find file locations |
| codebase-analyzer | subagent | Deep code analysis |
| pattern-finder | subagent | Find existing patterns |
| ledger-creator | subagent | Session continuity ledgers |
| artifact-searcher | subagent | Search past work |
| bootstrapper | subagent | Create octto branches |
| probe | subagent | (Defined but not prominently used) |
| project-initializer | subagent | Generate project docs |
| mm-orchestrator | subagent | Mindmodel generation |
| mm-stack-detector | subagent | Detect tech stack |
| mm-pattern-discoverer | subagent | Find coding patterns |
| mm-constraint-writer | subagent | Write constraints |
| mm-constraint-reviewer | subagent | Review against constraints |
| mm-dependency-mapper | subagent | Map dependencies |
| mm-convention-extractor | subagent | Extract conventions |
| mm-domain-extractor | subagent | Extract domain concepts |
| mm-code-clusterer | subagent | Cluster code |
| mm-anti-pattern-detector | subagent | Detect anti-patterns |
| mm-example-extractor | subagent | Extract examples |

## 3. Git Worktree Isolation

### How It Works

The commander agent's workflow explicitly includes a worktree isolation phase:

```
<phase name="setup" trigger="before implementation starts">
  <action>Create git worktree for feature isolation</action>
  <command>git worktree add ../{feature-name} -b feature/{feature-name}</command>
  <rule>All implementation happens in worktree, not main</rule>
  <rule>Worktree path: parent directory of current repo</rule>
</phase>
```

Key points:
- Worktrees are created **before implementation starts** (after planning, before executing)
- Worktree location: parent directory of current repo (e.g., `../feature-name`)
- Branch naming: `feature/{feature-name}`
- **All implementation happens in the worktree, not on main**

### What Happens in the Worktree

The implementer agent executes within the worktree:
- Writes files to the worktree path
- Runs tests from the worktree
- Does NOT commit (executor handles batch commits after review)

### Limitations

Unlike swain's worktree system, micode's worktree isolation is:
- **Prompt-driven only** — there's no TypeScript code creating/managing worktrees
- The commander prompt instructs the agent to run `git worktree add`, but the actual execution depends on the LLM following instructions
- No automatic cleanup of worktrees after implementation
- No worktree state tracking or session management

## 4. Session Continuity Mechanisms

### Continuity Ledgers

Ledgers are the primary session continuity mechanism. They preserve state across context clears.

**Location**: `thoughts/ledgers/CONTINUITY_{session-name}.md`

**Ledger Format**:
```markdown
# Session: {session-name}
Updated: {ISO timestamp}

## Goal
{One sentence success criteria}

## Constraints
{Technical requirements, patterns, things to avoid}

## Progress
### Done
- [x] {Completed items}

### In Progress
- [ ] {Current work}

### Blocked
- {Issues}

## Key Decisions
- **{Decision}**: {Rationale}

## Next Steps
1. {Ordered list}

## File Operations
### Read
- `{paths read}`

### Modified
- `{paths written or edited}`

## Critical Context
- {Data, references needed to continue}

## Working Set
- Branch: `{branch-name}`
- Key files: `{paths}`
```

### Auto-Compaction

When context usage reaches 50% (configurable via `compactionThreshold` in `micode.json`):

1. **Detect**: `auto-compact.ts` monitors `message.updated` events, computes context usage ratio
2. **Summarize**: Calls `ctx.client.session.summarize()` to trigger OpenCode's built-in compaction
3. **Write Ledger**: Extracts the summary message and writes it to `thoughts/ledgers/CONTINUITY_{session}.md`
4. **Auto-Continue**: Sends a "Continue from where you left off" prompt with the summary context

### Ledger Injection

When a new session starts, the `ledger-loader.ts` hook:
1. Finds the latest `CONTINUITY_*.md` file (by modification time) in `thoughts/ledgers/`
2. Formats it as `<continuity-ledger>` XML block
3. Prepends it to the system prompt via the `chat.params` hook

### Session Recovery

`session-recovery.ts` handles recoverable API errors:
- `tool_result block(s) missing`
- `thinking blocks must be at the start`
- `thinking is not enabled`
- `content cannot be empty`
- `tool_result must follow tool_use`

Recovery process:
1. Identify error type
2. Deduplicate (prevent cascading recovery attempts)
3. Abort the session
4. Wait 500ms for settlement
5. Resume with "Continue from where you left off"
6. Show toast to user
7. Max 3 recovery attempts per error type

### Manual Ledger Creation

Users can run `/ledger` command to manually create/update a continuity ledger, which invokes the `ledger-creator` agent with iterative update rules:
- **Initial mode**: Create new ledger from scratch
- **Iterative mode**: Merge previous ledger content with new file operations and progress
- Ledgers track: Goal, Constraints, Progress (Done/In Progress/Blocked), Key Decisions, Next Steps, File Operations, Critical Context, Working Set

### Artifact Auto-Indexing

`artifact-auto-index.ts` hook automatically indexes files written to `thoughts/` directories:
- Designs, plans, and ledgers are classified and ingested into a SQLite search index
- The `artifact-search` and `milestone-artifact-search` tools allow agents to query past work

## 5. Key Configuration Files

### micode.json (User Config)

Location: `~/.config/opencode/micode.json` (supports JSONC with comments)

```jsonc
{
  "agents": {
    "brainstormer": { "model": "openai/gpt-4o", "temperature": 0.8 },
    "commander": {
      "maxTokens": 8192,
      "thinking": { "type": "enabled", "budgetTokens": 100000 }
    }
  },
  "features": {
    "mindmodelInjection": true
  },
  "compactionThreshold": 0.5,
  "fragments": {
    "commander": ["custom-instructions.md"]
  }
}
```

Model resolution priority:
1. Per-agent override in micode.json (highest)
2. Default model from opencode.json `"model"` field
3. Plugin default (fallback)

### .mindmodel/ (Project Patterns)

The `.mindmodel/` directory encodes project-specific coding patterns as markdown files:
- `architecture/layers.md`, `architecture/organization.md`
- `components/shared.md`
- `domain/concepts.md`
- `patterns/data-fetching.md`, `patterns/error-handling.md`, `patterns/logging.md`, `patterns/testing.md`, `patterns/validation.md`
- `stack/backend.md`, `stack/database.md`, `stack/dependencies.md`
- `style/imports.md`, `style/naming.md`, `style/types.md`
- `manifest.yaml`

Agents call `mindmodel_lookup` tool before writing code to check patterns. The `mindmodel-injector` hook automatically injects relevant patterns into the system prompt based on task keywords.

### opencode.json (Host Config)

Model configuration and provider info. The plugin reads `model` and `provider.models.*.limit.context` from this file.

### Thoughts Directory Structure

```
thoughts/
├── ledgers/
│   └── CONTINUITY_{session}.md    # Session state persistence
└── shared/
    ├── designs/
    │   └── YYYY-MM-DD-{topic}-design.md  # Brainstorm output
    └── plans/
        └── YYYY-MM-DD-{topic}.md          # Plan output
```

## Architecture Notes

### Plugin Architecture

Micode is an OpenCode plugin, not a standalone tool. It uses the `@opencode-ai/plugin` SDK to:
- Register agents via `config.agent` (overriding OpenCode defaults, demoting built-in agents to subagent mode)
- Hook into OpenCode lifecycle events (`chat.params`, `chat.message`, `tool.execute.after`, `event`, `experimental.session.compacting`, `experimental.chat.messages.transform`, `experimental.chat.system.transform`)
- Register custom tools (`spawn_agent`, `pty_*`, `mindmodel_lookup`, `batch_read`, `ast_grep_*`, etc.)
- Register commands (`/init`, `/mindmodel`, `/ledger`, `/search`)
- Add MCP servers (context7, perplexity, firecrawl - environment-gated)

### Key Design Decisions

1. **Agents are pure data** (AgentConfig objects) — no logic, just prompts and parameters
2. **Hooks are factories** — `createXHook(ctx: PluginInput) => { handlers }` with dependency injection
3. **Valibot schemas** for config validation at system boundaries
4. **PTY system** with graceful degradation (bun-pty loads optionally)
5. **Context window awareness** — monitors usage, auto-compacts at threshold, truncates tool outputs
6. **Think mode** — keywords like "think hard" enable 128k token thinking budget
7. **Fragment injection** — user-defined prompt fragments can override agent behavior per-agent
8. **Comment checking** — strips developer comments from code edits automatically
9. **All permissions allowed** — edit, bash, webfetch, external_directory all set to "allow"