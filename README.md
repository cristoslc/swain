# swain

Agent governance, spec management, and execution tracking skills for AI coding agents.

Named for the boatswain's mate — the officer who maintains rigging and enforces standards.

## Install

```bash
npx skills add cristoslc/swain
```

This installs all skills into your project's `.claude/skills/` directory:

- **governance** — Always-on routing rules, protocols, and conventions
- **spec-management** — Artifact lifecycle (Vision, Epic, Spec, Story, ADR, Spike, Bug, etc.)
- **execution-tracking** — External task management integration (bd/beads)
- **release** — Version bump, changelog, and git tagging

## Requirements

- Node.js (for `npx skills`)
- Python 3 (for spec-management and execution-tracking scripts)
- Git

## Companion

[obra/superpowers](https://github.com/obra/superpowers) is a recommended companion install for plan authoring (brainstorming, writing-plans). Not a dependency — swain works without it.

## License

MIT
