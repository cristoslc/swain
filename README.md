# swain

**Ship what actually matters — not just what the AI decided to build.**

AI agents can ship code fast. But the decisions that shape a project are still human calls. What to build, what to defer, which tradeoffs to accept. The problem is that those decisions are ephemeral. They live in the operator's head, in agent memories that aren't clear enough, and in context that's gone by the next session. So the agent guesses.

Swain captures the operator's decisions as artifacts in git: what was decided and why. When the AI makes decisions, swain makes those visible too, so you can review and course-correct. You bring judgment and vision. The AI brings throughput and execution.

The result is a project that maintains intent, not just one that accumulates code. The AI doesn't drift because the reasoning is right there on disk. You stop re-explaining context that should already be settled. When priorities shift, you trace back to *why* and adapt instead of starting over. Every session builds on the last.

> *Swain is in early development. It's actively used in production by its author, but expect rough edges and shifting APIs. Feedback and contributions welcome.*

Named for the *swain* in boat**swain**, the officer who keeps the rigging tight.

## Install

```bash
npx skills add cristoslc/swain
```

The installer detects which agent platforms you have (Claude Code, Cursor, Codex, etc.) and installs skills only for those platforms. Built on the [skills standard](https://github.com/anthropics/skills).

After installing, run `/swain-init` in your first session to set up governance rules and task tracking.

## What a session looks like

Two skills auto-run at the start of every session:

1. **swain-doctor** checks project health — governance rules, file permissions, stale config — and repairs what it finds.
2. **swain-session** restores your context bookmark from last time: where you left off, what was in progress.

Then you ask what's going on:

```
/swain-status
```

or

```
/swain where are we at in this project?
```

This shows active epics with progress, decisions waiting on you, implementation-ready items, blocked work, tasks, and GitHub issues — all in one view with clickable links.

From there, the core loop is:

- **Design** (`/swain-design`) — create and evolve artifacts: Visions, Initiatives, Epics, Specs, Spikes, ADRs, Personas, Runbooks, Journeys, and Designs. Each follows a lifecycle tracked in git — phases vary by type (e.g., Proposed → Ready → In Progress → Complete for specs).
- **Execute** (`/swain-do`) — turn approved specs into tracked implementation plans with tasks and dependencies. When starting implementation work, swain-do automatically creates a linked git worktree so agent changes are isolated from your main workspace.
- **Ship** (`/swain-sync`, `/swain-release`) — fetch, rebase, commit with conventional messages, cut versioned releases. When running from a linked worktree, swain-sync lands the changes on `main` and prunes the worktree automatically.

Artifacts are markdown files in `docs/`. Phases are subdirectories. Transitions are commits. Everything is inspectable, diffable, and version-controlled.

## Skills

| Skill | What it does |
|-------|-------------|
| **swain-init** | One-time project setup — governance rules, task tracking, AGENTS.md |
| **swain-doctor** | Session-start health checks — auto-repairs config, permissions, stale state |
| **swain-session** | Context bookmarks and preferences across sessions |
| **swain-status** | Dashboard — active work, blockers, next steps, GitHub issues |
| **swain-design** | Artifact lifecycle — Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Journey, Design |
| **swain-search** | Evidence pools — collect and cache research sources as reusable markdown |
| **swain-do** | Task tracking — implementation plans, dependencies, progress |
| **swain-sync** | Fetch, rebase, commit, and push with conventional commit messages |
| **swain-release** | Changelog, version bump, git tag |
| **swain-stage** | Tmux workspace layouts and animated status panel |
| **swain-keys** | Per-project SSH keys for git signing and auth |
| **swain-dispatch** | Offload artifacts to background agents via GitHub Issues |
| **swain-retro** | Capture learnings at EPIC completion or on demand |
| **swain-update** | Pull latest skills, reconcile config |
| **swain-help** | Quick reference and onboarding guidance |

All skills are invoked via `/swain-<name>` or by describing what you want — the `swain` meta-router figures out which skill to load.

## Configuration

Two-tier settings model — project defaults (checked in) and personal overrides (never committed):

- **Project:** `swain.settings.json` in the repo root
- **User:** `~/.config/swain/settings.json`

## Requirements

- **Git** and **Node.js** (for `npx skills` installer)
- **jq** — status and settings parsing

Optional:

- **tk** (ticket) — task tracking backend, vendored with swain
- **uv** — Python runner for design and status scripts
- **gh** — GitHub CLI for issue integration and releases
- **tmux** — workspace layouts (swain-stage only)
- **fswatch** — live artifact file watching

## Companion

[obra/superpowers](https://github.com/obra/superpowers) is a recommended companion for plan authoring. Not a dependency.

## Isolated execution with swain-box

`swain-box` launches Claude Code inside a Docker Sandbox — a hypervisor-level microVM per sandbox provided by Docker Desktop 4.58+. Each sandbox has a private Docker daemon and credential proxy, so the host filesystem and Docker socket are not exposed.

**Requirement:** Docker Desktop 4.58 or later (Docker Sandboxes feature).

### Shell function

Add to `~/.zshrc`:

```sh
swain-box() {
  docker sandbox run claude "${1:-$PWD}"
}
```

### Usage

```sh
swain-box                   # open sandbox for current directory
swain-box ~/my-project      # open sandbox for a specific project
```

### Sandbox management

```sh
docker sandbox ls           # list all sandboxes
docker sandbox rm <name>    # remove a sandbox
```

### Credentials

If using an API key, set `ANTHROPIC_API_KEY` in your environment — Docker Sandboxes injects it via its host-side proxy. If using a Claude Max subscription (OAuth), export the token in `~/.zshrc` and restart Docker Desktop to pick it up:

```sh
export CLAUDE_CODE_OAUTH_TOKEN="$(security find-generic-password -s "Claude Code-credentials" -w)"
```

Restart Docker Desktop after adding this so the sandbox proxy picks up the new environment variable.

### Native sandboxing (lighter alternative)

`scripts/claude-sandbox` uses `claude --sandbox` (macOS Seatbelt / Linux Landlock) — no Docker required, near-zero startup overhead. Use `swain-box` when you want full hypervisor-level isolation; use `claude-sandbox` for a lighter local sandbox.

## License

MIT
