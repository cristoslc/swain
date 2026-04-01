---
id: e0wpls-87jg
status: closed
deps: []
links: []
created: 2026-04-01T02:57:57Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-gqvt
tags: [spec:SPEC-216]
---
# RED: arg parsing — no args exits 2, flags accepted

Write failing tests for: (1) no args → usage + exit 2, (2) --repo-root path flag accepted, (3) --worktree-root path flag accepted. Tests live in tests/detect-worktree-links/. Run and confirm RED before implementing.


## Notes

**2026-04-01T02:58:34Z**

RED confirmed — 5/5 tests fail (script not found, exit 127). Tests written in tests/detect-worktree-links/test_args.sh.
