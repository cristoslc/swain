---
id: swa-wien
status: closed
deps: [swa-5ckf, swa-k2f7]
links: []
created: 2026-03-13T23:28:32Z
type: task
priority: 1
assignee: cristos
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement xref subcommand

Add xref subcommand to cli.py with --json flag. Human-readable: format three sections (Cross-Reference Gaps, Missing Reciprocal Edges, Stale References) with artifact IDs and file paths. JSON: dump xref array from cache. Wire into argparse dispatch.


## Notes

**2026-03-14T04:28:25Z**

Completed: cmd_xref implemented in cli.py — all 47 tests pass

**2026-03-14T04:32:10Z**

Completed: implemented in xref.py (commit b7f504c), integrated in graph.py/cli.py (commits 8aaef5e, 2f29ff8), 47/47 tests passing
