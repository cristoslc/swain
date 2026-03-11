# swain

Agent skills for governance, spec management, and execution tracking — built on the [skills standard](https://github.com/anthropics/skills).

Named for the *swain* in boat**swain** — the officer who keeps the rigging tight and the standards enforced.

## Why swain?

AI coding agents are great at implementing things, but they lose context between sessions. You plan a feature, write half of it, come back tomorrow — and the agent has no idea what was decided, what's in progress, or what's blocked.

Swain gives your project **persistent, structured state** that survives across agent sessions and works with any agent that supports the skills standard.

| Without swain | With swain |
|---------------|------------|
| "What was I working on?" — dig through git log | `/swain-status` shows active work, blockers, and next steps |
| Feature ideas live in your head or scattered notes | Artifacts on disk with explicit phases and dependencies |
| Agent implements the wrong thing because context was lost | Specs define what to build; agents read them before coding |
| You approve something verbally, next session nobody remembers | Phase transitions are committed — decisions are in git history |
| Research findings evaporate after the session | Evidence pools cached as markdown, reusable across sessions |

Swain is for **solo dev + AI agent** workflows. It's not a replacement for GitHub Issues or Jira — it's the layer that keeps your agent productive between sessions.

## Install

```bash
npx skills add cristoslc/swain
```

This installs all skills into your project's `.claude/skills/` directory.

## Skills

| Skill | Description |
|-------|-------------|
| **swain-doctor** | Session-start health checks. Validates governance rules, repairs `.beads/.gitignore`, cleans up legacy skill directories, and untracks runtime files that leaked into git. Idempotent — runs every session, only writes when repairs are needed. |
| **swain-design** | Artifact lifecycle management. Create, validate, and transition documentation artifacts (Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey) through their lifecycle phases. Includes dependency graphing, stale reference detection, and audit tooling. |
| **swain-search** | Evidence pool collection. Collects sources from the web, local files, and media, normalizes them to markdown, and caches them in reusable evidence pools. Artifacts reference pools with commit-hash pinning for reproducibility. |
| **swain-do** | Execution tracking. Bootstraps and operates bd (beads) — a git-backed issue tracker — as the external task backend. Translates abstract operations (create plan, add task, set dependency) into concrete CLI commands. Handles TDD-structured implementation plans. |
| **swain-release** | Release automation. Detects versioning context from git history, generates changelogs from conventional commits, bumps version files, and creates annotated tags. Works across any repo. |
| **swain-push** | Commit and push. Stages changes, generates conventional-commit messages from diffs, handles merge conflicts with sensible defaults (local project wins over upstream scaffolding), and pushes. |
| **swain-help** | Contextual help. Answers questions about swain skills, artifacts, and workflows. Provides a quick reference cheat sheet and onboarding orientation after project setup. |
| **swain-session** | Session management. Restores terminal tab name, user preferences, and context bookmarks on session start. Auto-invoked via AGENTS.md. Agent-agnostic. |
| **swain-stage** | Tmux workspace manager. Layout presets (focus, review, browse), pane management, and an animated MOTD status panel showing project state and agent activity. Requires tmux. |
| **swain-update** | Self-updater. Pulls the latest swain skills via npx (git fallback) and invokes swain-doctor to reconcile governance and project health. |

## Configuration

Swain uses a two-tier settings model:

- **Project:** `swain.settings.json` in the repo root — team defaults, checked in
- **User:** `~/.config/swain/settings.json` — personal overrides, never committed

```json
{
  "editor": "auto",
  "fileBrowser": "auto",
  "terminal": { "tabNameFormat": "{project} @ {branch}" },
  "stage": {
    "motd": { "refreshInterval": 5, "spinnerStyle": "braille" },
    "defaultLayout": "focus"
  }
}
```

## Requirements

- Node.js (for `npx skills`)
- [uv](https://docs.astral.sh/uv/) (manages Python execution for swain-design and swain-do scripts)
- Git
- [jq](https://jqlang.github.io/jq/) (for settings and status file parsing)
- **Optional:** tmux (for swain-stage workspace management)

## Companion

[obra/superpowers](https://github.com/obra/superpowers) is a recommended companion install for plan authoring (brainstorming, writing-plans). Not a dependency — swain works without it.

## License

MIT
