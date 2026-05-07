# Synthesis: oh-my-opencode-slim

A synthesis of 12 sources covering the oh-my-opencode-slim OpenCode plugin — a slimmed, token-optimized fork of oh-my-opencode that implements a specialist-agent operating model on top of the OpenCode runtime.

## Key Findings

### Agent Operating Model

The plugin defines seven core agents under one orchestrator. Each specialist has a distinct role with explicit delegation rules embedded in the orchestrator's prompt:

- **Orchestrator** is both the primary coding agent and the delegator. It follows a 6-phase workflow: Understand, Path Selection, Delegation Check, Split/Parallelize, Execute, Verify.
- **Explorer** handles codebase reconnaissance at 2x speed and half cost. Good for scouting unknowns but not for single-file lookups.
- **Librarian** is tuned for external documentation retrieval — 10x better at finding up-to-date library docs. Uses MCPs (websearch, context7, grep_app).
- **Oracle** is the strongest agent: 5x better decision-making, used for architecture, hard debugging, code review, and simplification. Same cost as orchestrator.
- **Designer** handles UI/UX at 10x quality. Uses `agent-browser` skill.
- **Fixer** handles fast, bounded implementation at 2x speed, half cost, 0.8x quality. Primary use case is test writing and scoped code changes.
- **Council** is the consensus engine (3x+ cost, 3x slower). Runs multiple councillor models in parallel, returns synthesized verdicts. Intentionally under-delegated-to by the orchestrator (highest-cost path).

Observer is optional (disabled by default) — handles visual analysis of images, PDFs, and diagrams to save main context tokens.

### Configuration Architecture

Configuration is layered: project-local → user plugin config (`.jsonc` prefers `.json`) → OpenCode core config. Notable design decisions:

- **Presets** are first-class: install generates both OpenAI and OpenCode Go presets. Runtime switching via `/preset` command.
- **JSONC** support (comments, trailing commas) with auto-precedence.
- **Prompt overriding** via markdown files: `{agent}.md` replaces entire prompt, `{agent}_append.md` appends. Preset-scoped overrides take priority.
- **Custom agents**: unknown `agents` keys with `model` + `prompt` + optional `orchestratorPrompt` become registered subagents.
- **Permission model**: MCP access per-agent via `mcps` array with wildcard/exclusion syntax. Plugin auto-generates allow/deny rules.
- **Fallback chains**: model arrays + `fallback.chains` config create ordered provider failover for foreground agents.

### Session Architecture

The plugin maintains sophisticated session state:

- **Resumable child sessions**: Short aliases (`exp-1`, `ora-1`) remind the orchestrator of prior specialist sessions. In-memory only, scoped to parent session, auto-cleanup stale entries.
- **Read context tracking**: Files read through `read` tool tracked per child session; shown in orchestrator context with line counts. Helps route related follow-ups to the right session.
- **Depth tracking**: `SubagentDepthTracker` prevents unbounded nesting. Council is treated as a leaf agent.
- **Foreground fallback**: `ForegroundFallbackManager` switches models on rate-limit errors (non-interactive sessions only).

### Tool Surface

Beyond standard file/shell tools, the plugin ships:

- **apply_patch rescue**: Patch rewriting, tolerant matching, EOL preservation, bounded LCS fallback, path-boundary enforcement.
- **webfetch**: URL fetching with content extraction, cross-origin redirect blocking, secondary-model summarization fallback. Uses jsdom + readability + turndown.
- **ast_grep**: AST-aware search and replace across 25 languages. Understands code structure, not just text.
- **Todo continuation**: Auto-continue with configurable cooldowns (3s default) and max continuations (5). Direct `/auto-continue` command bypasses LLM round-trip.

### Multiplexer Integration

Live pane visualization for child sessions:

- **Tmux**: Full layout control (main-vertical, main-horizontal, tiled, even-horizontal, even-vertical). Configurable pane sizing.
- **Zellij**: Creates dedicated `opencode-agents` tab.
- **Auto-detect**: `type: "auto"` picks the active multiplexer.
- **Graceful shutdown**: Ctrl+C before kill-pane with 250ms delay.
- Requires `--port` flag (workaround for opencode#9099).

### MCP Integration

Three built-in MCP servers:
- `websearch` (Exa AI) — real-time web search
- `context7` — up-to-date library documentation
- `grep_app` — GitHub code search

Orchestrator gets `* !context7` by default. Librarian is the only agent with full MCP access (websearch + context7 + grep_app). All other agents get none by default. Global `disabled_mcps` can cut all external calls.

### Hook Chain

The plugin injects 15+ hooks into OpenCode's lifecycle:

| Hook | Function |
|------|----------|
| `chat.message` | Track session→agent mapping |
| `experimental.chat.system.transform` | Inject orchestrator prompt for serve-mode |
| `experimental.chat.messages.transform` | Rewrite display names, strip images, inject phase reminders, filter skills, inject session/todo context |
| `tool.execute.before` | apply_patch rescue, task session injection |
| `tool.execute.after` | Retry guidance, JSON recovery, todo tracking, post-file nudges, session cleanup (all fail-open) |
| `command.execute.before` | Direct `/auto-continue`, `/interview`, `/preset` interception |
| `event` | Session lifecycle: created/deleted/status for multiplexer, Divoom, depth tracking |

### Communication Discipline

The orchestrator prompt enforces strict communication rules:
- No preamble, no summaries unless asked, no code explanations unless asked
- No flattery ("Great question!" banned)
- Honest pushback when user's approach seems problematic
- One-word answers permitted
- Brief delegation notices: "Checking docs via @librarian..." not "I'm going to delegate to @librarian because..."

## Points of Agreement

- Specialist delegation improves quality, speed, and cost over monolithic model use.
- Fast models (GPT-5.4-mini, Minimax M2.7) are sufficient for Explorer, Librarian, and Fixer — these are throughput-bound, not reasoning-bound.
- Council is the most expensive path and should be gated conservatively.
- Session reuse saves both time and tokens; fresh sessions only when context diverges too far.
- The orchestrator workflow is intentionally rigid (6 phases) to prevent the model from skipping delegation checks.

## Points of Disagreement

None identified across the sources — this is a single, cohesive project with a clear architecture.

## Gaps

- **Comparison to parent fork**: The exact token savings vs upstream oh-my-opencode are not quantified in the docs. References to "consumes much less tokens" and the `.slim/` directory suggest tooling exists but numbers aren't published.
- **Custom agent lifecycle**: How custom agents interact with hooks, session management, and fallback chains is documented in config but not deeply explored in runtime examples.
- **Error recovery depth**: JSON error recovery and apply_patch rescue are mentioned as best-effort; their actual success rates and failure modes aren't benchmarked.
- **Multi-project multiplexing**: The omos() bash helper enables multiple projects via random ports, but there's no discussion of how session isolation works when two orchestrator sessions target the same codebase.
