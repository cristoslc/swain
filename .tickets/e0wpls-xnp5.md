---
id: e0wpls-xnp5
status: closed
deps: []
links: []
created: 2026-04-01T03:06:12Z
type: task
priority: 2
assignee: cristos
parent: e0wpls-2avd
tags: [spec:SPEC-217]
---
# RED: tests for piped-input and standalone modes

Write failing tests: (1) piped detector output rewrites markdown link, (2) standalone mode detects+resolves in one pass, (3) idempotent — second run produces no changes, (4) UNRESOLVABLE exits 1


## Notes

**2026-04-01T03:06:41Z**

RED confirmed — 8/9 tests fail (script missing). test_resolve.sh written.
