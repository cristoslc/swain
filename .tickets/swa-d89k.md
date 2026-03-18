---
id: swa-d89k
status: closed
deps: []
links: []
created: 2026-03-18T03:35:20Z
type: task
priority: 2
assignee: cristos
parent: swa-d083
tags: [spec:SPEC-066]
---
# Update swain-session SKILL.md: distinguish not-installed vs. not-in-session

Check 'which tmux' first. If not found: offer to install. If found but TMUX unset: show [note] as before (no install offer).


## Notes

**2026-03-18T03:36:39Z**

Updated swain-session SKILL.md Step 1: checks 'which tmux' when TMUX unset. Not installed: offer to run brew install. Installed but not in session: show [note] as before.
