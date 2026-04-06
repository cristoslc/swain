---
source-type: web-page
title: "Agent Skills — Codex (OpenAI Developers)"
url: https://developers.openai.com/codex/skills
fetched: 2026-04-06
---

# Codex Skills Discovery

OpenAI's Codex CLI implementation of the Agent Skills standard.

## Discovery locations

Codex scans for skills across multiple scopes:

| Scope | Path | Use Case |
|-------|------|----------|
| REPO (CWD) | `$CWD/.agents/skills` | Skills specific to immediate working directory |
| REPO (Parent) | `$CWD/../.agents/skills` | Skills for nested repository structures |
| REPO (Root) | `$REPO_ROOT/.agents/skills` | Org-wide skills throughout repository |
| USER | `$HOME/.agents/skills` | Personal skill collection across repos |
| ADMIN | `/etc/codex/skills` | System-wide defaults for all users |
| SYSTEM | Bundled | Built-in skills provided by OpenAI |

## Key conventions

- Discovery path is **`.agents/skills`** — not `.agents/bin/` or `.agents/scripts/`.
- Within each skill: `scripts/`, `references/`, `assets/` subdirectories.
- System "follows the symlink target when scanning these locations."
- `agents/openai.yaml` for UI metadata, invocation policy, and tool dependencies.

## Notable

Codex uses `.agents/skills/` as the canonical path, establishing `.agents/` as the standard top-level directory for agent infrastructure. The `scripts/` subdirectory lives within each skill, not as a top-level aggregation point.
