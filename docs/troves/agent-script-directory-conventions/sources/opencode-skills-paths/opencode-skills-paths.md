---
source-type: web-page
title: "Agent Skills — OpenCode"
url: https://opencode.ai/docs/skills/
fetched: 2026-04-06
---

# OpenCode Skills Paths

OpenCode (by SST) supports the Agent Skills standard alongside Claude-compatible and native paths.

## Discovery locations

1. `.opencode/skills/<name>/SKILL.md` — project-level native.
2. `~/.config/opencode/skills/<name>/SKILL.md` — global native.
3. `.claude/skills/<name>/SKILL.md` — project Claude-compatible.
4. `~/.claude/skills/<name>/SKILL.md` — global Claude-compatible.
5. **`.agents/skills/<name>/SKILL.md`** — project agent-compatible.
6. **`~/.agents/skills/<name>/SKILL.md`** — global agent-compatible.

## Key observations

- `.agents/skills/` is recognized as the cross-tool interoperability standard.
- OpenCode walks up from CWD to git worktree root, collecting all matching skills.
- Three parallel conventions coexist: native (`.opencode/`), Claude (`.claude/`), agent standard (`.agents/`).
- No mention of `.agents/bin/` or any top-level bin directory.
