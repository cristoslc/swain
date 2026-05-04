---
source-id: "open-ralph-wiggum"
title: "Open Ralph Wiggum — Multi-Agent Autonomous Loop CLI"
type: repository
url: "https://github.com/Th0rgal/open-ralph-wiggum"
fetched: 2026-04-06T16:00:00Z
hash: "b5af10f887a43096a4a2f2d71a026cbb5a92fecf5fef3dda43298385fc3294ab"
highlights:
  - "open-ralph-wiggum.md"
selective: true
notes: "Most comprehensive open-source implementation; supports Claude Code, Codex, Copilot CLI, OpenCode; agent rotation; tasks mode"
---

# Open Ralph Wiggum — Multi-Agent Autonomous Loop CLI

**Tagline:** Autonomous Agentic Loop for Claude Code, Codex, Copilot CLI & OpenCode.

Open Ralph Wiggum implements the Ralph Wiggum technique as a full-featured CLI. It wraps any supported AI coding agent in a persistent development loop. No plugins required.

## The core mechanism

```bash
# The essence of the Ralph loop:
while true; do
  claude-code "Build feature X. Output <promise>DONE</promise> when complete."
done
```

The AI doesn't talk to itself between iterations. It sees the same prompt each time, but the codebase has changed from previous iterations. This creates a feedback loop where the agent iteratively improves its work until all tests pass.

## Supported agents

| Agent | Flag | Description |
|-------|------|-------------|
| Claude Code | `--agent claude-code` | Anthropic's Claude Code CLI |
| Codex | `--agent codex` | OpenAI's Codex CLI |
| Copilot CLI | `--agent copilot` | GitHub Copilot CLI |
| OpenCode | `--agent opencode` | Default — open-source AI coding assistant |

## Install

```bash
npm install -g @th0rgal/ralph-wiggum
```

## Quick start

```bash
ralph "Build a REST API with tests. Output <promise>COMPLETE</promise> when all tests pass." \
  --agent claude-code --max-iterations 20
```

## Key features

- **Multi-agent support** — switch with `--agent` flag.
- **Self-correcting loops** — agent sees its previous work and fixes its own mistakes.
- **Tasks mode** — break complex projects into a structured task list (`.ralph/ralph-tasks.md`).
- **Live monitoring** — check progress from another terminal with `--status`.
- **Mid-loop hints** — inject guidance with `--add-context` without stopping.
- **Agent rotation** — cycle through agent/model combinations per iteration with `--rotation`.
- **Struggle detection** — warns when agent is stuck (no progress, repeated errors).

## CLI options (key flags)

| Option | Purpose |
|--------|---------|
| `--agent` | Agent: opencode, claude-code, codex, copilot |
| `--max-iterations N` | Stop after N iterations |
| `--completion-promise T` | Text that signals completion (default: COMPLETE) |
| `--tasks` | Enable tasks mode for structured task tracking |
| `--rotation` | Agent/model rotation list (e.g. `opencode:claude-sonnet-4,claude-code:claude-sonnet-4`) |
| `--allow-all` | Auto-approve all tool permissions (default: on) |
| `--no-allow-all` | Require interactive permission prompts |
| `--add-context` | Add mid-loop guidance for next iteration |
| `--status` | Show dashboard of active loop |

## Tasks mode

Tasks are stored in `.ralph/ralph-tasks.md`. Ralph works on one task per iteration:

```markdown
# Ralph Tasks
- [ ] Set up project structure
- [x] Initialize git repository
- [/] Implement user authentication
```

Status markers: `[ ]` not started, `[/]` in progress, `[x]` complete.

## State files (in `.ralph/`)

- `ralph-loop.state.json` — active loop state.
- `ralph-history.json` — iteration history and metrics.
- `ralph-context.md` — pending context for next iteration.
- `ralph-tasks.md` — task list for tasks mode.
- `ralph-questions.json` — pending answers to agent questions.

## Prompt quality guidance

**Include verifiable success criteria:**

```markdown
Build a REST API for todos with:
- CRUD endpoints (GET, POST, PUT, DELETE)
- Input validation
- Tests for each endpoint

Run tests after changes. Output <promise>COMPLETE</promise> when all tests pass.
```

**JSON feature list (recommended for complex projects).** JSON format reduces the chance of agents redefining success criteria compared to Markdown. Each feature object has `description`, `steps`, and `passes: false` — the agent flips `passes` to `true` when done.

## When to use

**Good for:** tasks with automatic verification (tests, linters, type checking), well-defined tasks with clear completion criteria, greenfield projects, iterative refinement.

**Not good for:** tasks requiring human judgment, unclear success criteria, production debugging.

## Agent rotation

```bash
ralph "Build a REST API" \
  --rotation "opencode:claude-sonnet-4,claude-code:claude-sonnet-4" \
  --max-iterations 10
```

Cycles through entries round-robin. `--agent` and `--model` are ignored when `--rotation` is set.

## How it works (diagram)

```
ralph sends prompt  →  agent modifies files  →  ralph checks for <promise>
       ↑                                                    |
       └──────────── same prompt, new codebase ────────────┘
                     (until promise found or max iterations)
```

## License

MIT
