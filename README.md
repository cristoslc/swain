# swain

**Ship what actually matters — not just what the AI decided to build.**

AI agents can ship code fast. But the decisions that shape a project are still human calls. What to build, what to defer, which tradeoffs to accept. The problem is that those decisions are ephemeral. They live in the operator's head, in agent memories that aren't clear enough, and in context that's gone by the next session. So the agent guesses.

Swain captures the operator's decisions as artifacts in git: what was decided and why. When the AI makes decisions, swain makes those visible too, so you can review and course-correct. You bring judgment and vision. The AI brings throughput and execution.

The result is a project that maintains intent, not just one that accumulates code. The AI doesn't drift because the reasoning is right there on disk — and swain actively protects it. Once you've made a call, downstream work is checked against that decision automatically. You're only interrupted when something might violate it. One decision up front, automated integrity checking downstream. You stop re-explaining context that should already be settled. When priorities shift, you trace back to *why* and adapt instead of starting over. Every session builds on the last.

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
2. **swain-init** restores your context, proposes a focus lane, and generates a SESSION-ROADMAP.md scoped to your current work area.

Sessions have a bounded lifecycle: **start → work → close**. swain-init owns session startup — context restoration, focus lane selection, and worktree detection. On close, **swain-teardown** fires a retro, merges worktree branches, cleans up worktrees, and writes a walk-away signal so the next session knows where you left off.

Then you ask what's going on:

```
/swain-roadmap
```

or

```
/swain where are we at in this project?
```

This shows active epics with progress, decisions waiting on you, implementation-ready items, blocked work, tasks, and GitHub issues — all in one view with clickable links.

From there, the core loop is:

- **Design** (`/swain-design`) — create and evolve artifacts: Visions, Initiatives, Epics, Specs, Spikes, ADRs, Personas, Runbooks, Journeys, and Designs. Each follows a lifecycle tracked in git — phases vary by type (e.g., Proposed → Ready → In Progress → Complete for specs).
- **Execute** (`/swain-do`) — turn approved specs into tracked implementation plans with tasks and dependencies. The `bin/swain` launcher creates a linked git worktree before the agent starts, so all changes are isolated from your main workspace.
- **Ship** (`/swain-sync`, `/swain-release`) — fetch, merge, commit with conventional messages, cut versioned releases. When running from a linked worktree, swain-sync merges and pushes to `trunk`, then marks the worktree for cleanup. `bin/swain` prunes it after the session ends.

Artifacts are markdown files in `docs/`. Phases are subdirectories. Transitions are commits. Everything is inspectable, diffable, and version-controlled.

## Skills

| Skill | What it does |
|-------|-------------|
| **swain-init** | Session entry point — onboarding, context restoration, focus lane, worktree detection |
| **swain-doctor** | Session-start health checks — auto-repairs config, permissions, stale state |
| **swain-design** | Artifact lifecycle — Vision, Initiative, Epic, Spec, Spike, ADR, Persona, Runbook, Journey, Design |
| **swain-search** | Evidence pools — collect and cache research sources as reusable markdown |
| **swain-do** | Task tracking — implementation plans, dependencies, bookmarks, decisions, progress |
| **swain-roadmap** | Status dashboard and roadmap — active work, blockers, next steps, priorities |
| **swain-sync** | Fetch, rebase, commit, and push with conventional commit messages |
| **swain-release** | Changelog, version bump, git tag |
| **swain-keys** | Per-project SSH keys for git signing and auth |
| **swain-retro** | Capture learnings at EPIC completion or on demand |
| **swain-teardown** | Full session shutdown — retro, merge worktrees, cleanup, close session |
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
- **fswatch** — live artifact file watching

## Isolated execution with swain-box

> **Experimental.** swain-box is under active redesign. OAuth is broken in Docker Sandboxes, and the launcher is being reworked to support both microVM and container isolation modes. See open issues for current status.

`swain-box` launches Claude Code inside a Docker Sandbox — a hypervisor-level microVM per sandbox provided by Docker Desktop 4.58+.

`scripts/swain-box` ships with swain. After running `swain-init` (or `swain-doctor`) in your project, a `./swain-box` symlink is created at the project root pointing to the script.

### Native sandboxing (lighter alternative)

`scripts/claude-sandbox` uses `claude --sandbox` (macOS Seatbelt / Linux Landlock) — no Docker required, near-zero startup overhead.

## License

MIT
