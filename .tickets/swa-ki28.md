---
id: swa-ki28
status: open
deps: []
links: []
created: 2026-04-14T01:31:20Z
type: task
priority: 2
assignee: Cristos L-C
parent: swa-qc20
tags: [spec:SPEC-305]
---
# Write consumer gitignore block (.swain/session/ only)

swain-init proposes a managed block for .gitignore containing .swain/session/ and .swain-init. Markers: # >>> swain managed >>> and # <<< swain managed <<<. Show diff before write, ask confirmation. Non-interactive override flag for CI. Upgrades diff existing blocks. Test: clean repos get block appended. Decline leaves file alone. Re-runs are no-ops. Older blocks upgrade. Only .swain/session/ is gitignored — rest of .swain/ is tracked.


## Notes

**2026-04-14T01:38:10Z**

Updated scope per ADR-042: .swain-init is now tracked (removed from gitignore block). Peer-agent dirs not gitignored. Block contains only .swain/session/. Also: remove inline symlinking from bin/swain create_session_worktree(), remove swain-doctor symlink repair check, and don't set core.hooksPath.

**2026-04-14T01:38:27Z**

Per ADR-042 (already reflected in SPEC-305 v4): gitignore block contains only .swain/session/. Also remove create_session_worktree() symlinking and swain-doctor symlink repair.
