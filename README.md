# swain

Agent governance, spec management, and execution tracking skills for AI coding agents.

Named for the boatswain's mate — the officer who maintains rigging and enforces standards.

## Install

```bash
npx skills add cristoslc/swain
```

This installs all skills into your project's `.claude/skills/` directory.

## Skills

| Skill | Description |
|-------|-------------|
| **swain-config** | Session-start governance injector. Ensures your project's context file (CLAUDE.md or Cursor rules) has the routing rules that make other swain skills discoverable. Idempotent — runs every session, only writes on first use. |
| **swain-design** | Artifact lifecycle management. Create, validate, and transition documentation artifacts (Vision, Epic, Story, Spec, ADR, Spike, Bug, Persona, Runbook, Journey) through their lifecycle phases. Includes dependency graphing, stale reference detection, and audit tooling. |
| **swain-do** | Execution tracking. Bootstraps and operates bd (beads) — a git-backed issue tracker — as the external task backend. Translates abstract operations (create plan, add task, set dependency) into concrete CLI commands. Handles TDD-structured implementation plans. |
| **swain-release** | Release automation. Detects versioning context from git history, generates changelogs from conventional commits, bumps version files, and creates annotated tags. Works across any repo. |
| **swain-push** | Commit and push. Stages changes, generates conventional-commit messages from diffs, handles merge conflicts with sensible defaults (local project wins over upstream scaffolding), and pushes. |
| **swain-update** | Self-updater. Pulls the latest swain skills via npx (git fallback) and reconciles governance rules. |

## Requirements

- Node.js (for `npx skills`)
- Python 3 (for swain-design and swain-do scripts)
- Git

## Companion

[obra/superpowers](https://github.com/obra/superpowers) is a recommended companion install for plan authoring (brainstorming, writing-plans). Not a dependency — swain works without it.

## License

MIT
