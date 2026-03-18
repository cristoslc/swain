---
id: swa-7ibz
status: closed
deps: []
links: []
created: 2026-03-18T03:27:34Z
type: task
priority: 2
assignee: cristos
parent: swa-d083
tags: [spec:SPEC-066]
---
# Update swain-stage require_tmux() for binary + session checks

Add binary presence check before session check. When tmux not found: 'tmux not found — install with brew install tmux'. When installed but not in session: 'tmux not active — swain-stage requires a tmux session. Start tmux first.'


## Notes

**2026-03-18T03:29:31Z**

Updated require_tmux() in swain-stage.sh: added which tmux binary check before TMUX session check, with spec-compliant messages for each case
