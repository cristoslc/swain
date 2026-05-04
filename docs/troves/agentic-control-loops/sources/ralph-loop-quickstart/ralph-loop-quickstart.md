---
source-id: "ralph-loop-quickstart"
title: "Ralph Loop Quickstart — PRD-Driven Autonomous Development"
type: repository
url: "https://github.com/coleam00/ralph-loop-quickstart"
fetched: 2026-04-06T16:00:00Z
hash: "5538a602c0b3feaf3fd79886125c4ef1eb9c537b6bc8d68977a2093db49f07a6"
highlights:
  - "ralph-loop-quickstart.md"
selective: true
notes: "Practical guide emphasizing PRD quality, bash loop (fresh context per iteration), agent-browser integration"
---

# Ralph Loop Quickstart — PRD-Driven Autonomous Development

**Key thesis:** The official Anthropic Ralph plugin has a fundamental flaw — it runs everything in a single context window. The correct approach uses a bash loop to start a fresh context window per iteration.

## Why fresh context matters

The official Ralph Wiggum plugin for Claude Code runs everything in a **single context window**:

- Context gets bloated over time.
- Increased hallucination risk as context fills up.
- No true separation between iterations.
- Manual compaction may be needed mid-run.

The bash loop method (`ralph.sh`) starts a **fresh context window** for each iteration. This is the correct approach for long-running autonomous tasks.

## The process

### Step 1 — Create your PRD with `/create-prd`

An interactive Claude command that:

1. Asks discovery questions one at a time (problem, audience, core features, tech stack, architecture, UI/UX, auth, integrations, success criteria).
2. Generates `prd.md` with complete requirements and a JSON task list.
3. Updates `PROMPT.md` with project-specific start/build commands.
4. Updates `.claude/settings.json` with permissions for required CLI tools.
5. Creates `activity.md` for progress logging.

### Step 2 — Verify before running

Review `prd.md` (are tasks atomic and ordered?), `PROMPT.md` (correct start command?), and `.claude/settings.json` (all CLI tools permitted?). **This is critical.** Quality of the Ralph run depends entirely on quality of the PRD and configuration.

### Step 3 — Run the loop

```bash
./ralph.sh 20   # 20 = max iterations
```

Each iteration:
1. Reads `PROMPT.md` and feeds it to Claude.
2. Claude works on one task from `prd.md`.
3. Verifies with agent-browser (visual verification via screenshot).
4. Updates task status and logs to `activity.md`.
5. Commits the change.
6. Repeats with a fresh context window.

Loop exits when: all tasks have `"passes": true` (outputs `<promise>COMPLETE</promise>`), or max iterations reached.

## JSON task format (from `prd.md`)

```json
[
  {
    "category": "setup",
    "description": "Initialize Next.js project with TypeScript",
    "steps": [
      "Run create-next-app with TypeScript template",
      "Install additional dependencies",
      "Verify dev server starts"
    ],
    "passes": false
  }
]
```

Task requirements:
- **Atomic** — one logical unit of work.
- **Verifiable** — clear success criteria.
- **Ordered** — respects dependencies.
- **Categorized** — setup, feature, integration, styling, testing.

## Settings configuration

`.claude/settings.json` is updated by `/create-prd` based on tech stack. Example permissions:

- `Bash(prisma:*)` for Prisma CLI.
- `Bash(supabase:*)` for Supabase CLI.
- `Bash(vercel:*)` for Vercel CLI.
- `Bash(docker compose:*)` for Docker workflows.

## Monitoring

While Ralph runs, you can monitor:

- `activity.md` — detailed log of what was accomplished each iteration.
- `screenshots/` — visual verification of each completed task.
- Git commits — one commit per task with clear messages.
- Terminal output — real-time progress.

## Best practices

1. **Plan thoroughly.** Don't skip discovery questions. A well-defined PRD is the difference between a successful Ralph run and wasted API credits.
2. **Keep scope tight.** Ralph is for proof of concepts, not production applications.
3. **Verify before running.** Always review `prd.md`, `PROMPT.md`, and settings before starting.
4. **Start with fewer iterations.** Use 10-20 initially. Run more if needed.
5. **Monitor the first few iterations.** Watch 2-3 iterations to confirm: dev server starts, agent-browser can access localhost, tasks are marked passing correctly.
6. **Use sandboxing.** The default settings enable sandboxing for isolation.

## When to use Ralph Wiggum

**Ideal for:** starting from scratch, building proof of concepts with clearly defined scope, greenfield development, projects where you can define "done" precisely.

**Not ideal for:** complex existing codebases, vibe coding without clear goals, ambiguous requirements, situations requiring frequent human judgment.

## Dependencies

- [Bun](https://bun.sh) runtime.
- At least one AI coding agent CLI (Claude Code, Codex, Copilot CLI, or OpenCode).
- [Vercel Agent Browser CLI](https://github.com/vercel-labs/agent-browser) — optional, for visual verification.

## Reference links

- [Original Ralph Wiggum technique by Geoffrey Huntley](https://ghuntley.com/ralph/)
- [Anthropic's long-running agents post](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
