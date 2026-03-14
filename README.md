# swain

**Decision support for the operator. Alignment support for the agent.**

Swain is a skill suite for solo developers who work with AI coding agents. It serves two audiences in every session:

- **You (the operator)** get a decision-support layer — what's active, what's blocked, what needs your judgment, and what the agent can handle autonomously. You make the calls; swain surfaces the right information at the right time.
- **Your agent** gets an alignment layer — structured artifacts on disk that say what was decided, what to build, what constraints apply, and where it left off. The agent reads these instead of guessing or asking you to repeat context.

Both layers are the same data: markdown files in git. Swain just presents them differently depending on who's looking.

Named for the *swain* in boat**swain** — the officer who keeps the rigging tight.

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

- **Design** (`/swain-design`) — create and evolve artifacts: Visions, Epics, Specs, Spikes, ADRs, Stories, Bugs, and more. Each has a lifecycle tracked in git (Draft → Approved → Implemented).
- **Execute** (`/swain-do`) — turn approved specs into tracked implementation plans with tasks and dependencies. When starting implementation work, swain-do automatically creates a linked git worktree so agent changes are isolated from your main workspace.
- **Ship** (`/swain-sync`, `/swain-release`) — fetch, rebase, commit with conventional messages, cut versioned releases. When running from a linked worktree, swain-sync lands the changes on `main` and prunes the worktree automatically.

Artifacts are markdown files in `docs/`. Phases are subdirectories. Transitions are commits. Everything is inspectable, diffable, and version-controlled.

## Isolated execution

Swain ships a `scripts/claude-sandbox` launcher that runs Claude Code inside an isolated environment — keeping agent file access and network calls contained:

```bash
# Tier 1: native platform sandboxing (default)
# macOS: sandbox-exec (Seatbelt), Linux: Landlock or bubblewrap
./scripts/claude-sandbox

# Tier 2: Docker container with bind-mounted project files
./scripts/claude-sandbox --docker
```

Both modes pass extra arguments through to `claude`. Configuration (`dockerImage`, `allowedDomains`) lives in `swain.settings.json`.

**Requirements:**
- Tier 1: no extra dependencies (uses OS-native sandboxing)
- Tier 2: Docker daemon running

## Skills

| Skill | What it does |
|-------|-------------|
| **swain-init** | One-time project setup — governance rules, task tracking, AGENTS.md |
| **swain-doctor** | Session-start health checks — auto-repairs config, permissions, stale state |
| **swain-session** | Context bookmarks and preferences across sessions |
| **swain-status** | Dashboard — active work, blockers, next steps, GitHub issues |
| **swain-design** | Artifact lifecycle — Vision, Epic, Spec, Spike, ADR, Story, Bug, Persona, Runbook, Journey, Design |
| **swain-search** | Evidence pools — collect and cache research sources as reusable markdown |
| **swain-do** | Task tracking — implementation plans, dependencies, progress |
| **swain-sync** | Fetch, rebase, commit, and push with conventional commit messages |
| **swain-push** | Deprecated alias for swain-sync |
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

## License

MIT
