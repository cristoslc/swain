---
id: swa-i0kd
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
# Update swain-stage SKILL.md: offer to install if tmux missing

If script reports 'tmux not found', offer to run brew install tmux; re-run subcommand if user accepts.


## Notes

**2026-03-18T03:36:19Z**

Updated swain-stage SKILL.md: prerequisite note updated, error handling section now distinguishes not-installed (offer brew install) vs not-in-session (inform only).
