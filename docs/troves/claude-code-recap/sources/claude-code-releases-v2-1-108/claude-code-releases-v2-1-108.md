---
title: "Claude Code v2.1.108 Release Notes"
source-url: "https://github.com/anthropics/claude-code/releases"
source-type: web-page
fetched: 2026-04-14
transcript-source: convert-to-markdown
---

# Claude Code v2.1.108 Release Notes

**Version:** 2.1.108
**Released:** April 14, 2026

## Recap Feature (Primary Entry)

> Added recap feature to provide context when returning to a session, configurable in `/config` and manually invocable with `/recap`; force with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` if telemetry disabled.

## Other Changes in This Release

**Prompt Caching:**
- Added `ENABLE_PROMPT_CACHING_1H` env var to opt into 1-hour prompt cache TTL on API key, Bedrock, Vertex, and Foundry (`ENABLE_PROMPT_CACHING_1H_BEDROCK` is deprecated but still honored).
- Added `FORCE_PROMPT_CACHING_5M` to force 5-minute TTL.

**Slash Command Discovery:**
- The model can now discover and invoke built-in slash commands like `/init`, `/review`, and `/security-review` via the Skill tool.

**Command Improvements:**
- `/undo` is now an alias for `/rewind`.
- Improved `/model` to warn before switching models mid-conversation, since the next response re-reads the full history uncached.
- Improved `/resume` picker to default to sessions from the current directory; press `Ctrl+A` to show all projects.

**Error Messages:**
- Server rate limits are now distinguished from plan usage limits.
- 5xx/529 errors show a link to status.claude.com.
- Unknown slash commands suggest the closest match.

**Performance & UI:**
- Reduced memory footprint for file reads, edits, and syntax highlighting by loading language grammars on demand.
- Added "verbose" indicator when viewing the detailed transcript (`Ctrl+O`).
- Added a warning at startup when prompt caching is disabled via `DISABLE_PROMPT_CACHING*` env vars.
- Added OS CA certificate store trust by default (set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs).

**Bug Fixes:**
- Fixed paste not working in the `/login` code prompt (regression in 2.1.105).
- Fixed several Remote Control issues: worktrees removed on session crash, connection failures not persisting in transcript, spurious "Disconnected" indicator in brief mode for local sessions.
- Fixed `/remote-control` failing over SSH when only `CLAUDE_CODE_ORGANIZATION_UUID` is set.
- Multiple additional fixes for Agent tool permissions, Bash tool output, session restoration, terminal escape codes, transcript writes, and plugin auto-updates.

## Related Earlier Change (v2.1.69, March 5, 2026)

> Changed resuming after compaction to no longer produce a preamble recap before continuing.

This earlier change removed the automatic "here's what happened" preamble that appeared after compaction resumed. The new `/recap` command in v2.1.108 is a distinct, on-demand (and auto-triggered-on-return) feature — not related to compaction preambles.
