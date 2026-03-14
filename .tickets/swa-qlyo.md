---
id: swa-qlyo
status: closed
deps: []
links: []
created: 2026-03-14T06:40:04Z
type: epic
priority: 2
assignee: cristos
external-ref: SPEC-041
---
# SPEC-041 implementation plan

Add reactive file watching for agent status; hooks-not-configured notice; graceful degradation


## Notes

**2026-03-14T06:40:41Z**

Completed: hooks already configured in .claude/settings.json. Added: hooks_configured() check, HOOKS_CONFIGURED constant, _agent_file_mtime tracker, 1s _check_agent_file interval for reactive re-render, hooks-not-configured notice in idle state.
