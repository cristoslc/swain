---
id: swain-6oa
status: open
deps: []
links: []
created: 2026-03-12T13:19:56Z
type: feature
priority: 2
---
# Reactive status via Claude Code hooks

swain-status/MOTD panel should react to Claude's actual activity instead of relying on stale cache or explicit motd update calls. Claude Code exposes hooks (PostToolUse, SubagentStart/Stop, Stop, SessionStart/End) that receive full JSON context on stdin. Wire these hooks to write stage-status.json so the MOTD panel updates in real-time. Key pieces: (1) Configure hooks in .claude/settings.json to fire a shell script on PostToolUse/Stop/Subagent events, (2) Script parses hook JSON and writes stage-status.json with tool name, context, working/idle state, (3) MOTD already polls stage-status.json every 5s — no changes needed on the display side. This closes the gap between what Claude is doing and what the dashboard shows.


