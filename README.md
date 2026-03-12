# swain

Persistent project state for solo developers working with AI coding agents.

AI agents lose context between sessions. You plan a feature, implement half of it, come back tomorrow — and the agent doesn't know what was decided, what's blocked, or what to do next. Swain keeps structured state on disk so your agent can pick up where you left off.

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

This shows active epics with progress, decisions waiting on you, implementation-ready items, blocked work, tasks, and GitHub issues — all in one view with clickable links.

From there, the core loop is:

- **Design** (`/swain-design`) — create and evolve artifacts: Visions, Epics, Specs, Spikes, ADRs, Stories, Bugs, and more. Each has a lifecycle tracked in git (Draft → Approved → Implemented).
- **Execute** (`/swain-do`) — turn approved specs into tracked implementation plans with tasks and dependencies.
- **Ship** (`/swain-push`, `/swain-release`) — commit with conventional messages, cut versioned releases.

Artifacts are markdown files in `docs/`. Phases are subdirectories. Transitions are commits. Everything is inspectable, diffable, and version-controlled.

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
| **swain-push** | Commit and push with conventional commit messages |
| **swain-release** | Changelog, version bump, git tag |
| **swain-stage** | Tmux workspace layouts and animated status panel |
| **swain-keys** | Per-project SSH keys for git signing and auth |
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

- **bd** ([beads](https://beads.dev)) — task tracking backend, installed automatically by swain-do on first use
- **uv** — Python runner for design and status scripts
- **gh** — GitHub CLI for issue integration and releases
- **tmux** — workspace layouts (swain-stage only)
- **fswatch** — live artifact file watching

## Companion

[obra/superpowers](https://github.com/obra/superpowers) is a recommended companion for plan authoring. Not a dependency.

## License

MIT
