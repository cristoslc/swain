---
id: swa-wien
status: open
deps: [swa-5ckf, swa-k2f7]
links: []
created: 2026-03-13T23:28:32Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# GREEN: Implement xref subcommand

Add xref subcommand to cli.py with --json flag. Human-readable: format three sections (Cross-Reference Gaps, Missing Reciprocal Edges, Stale References) with artifact IDs and file paths. JSON: dump xref array from cache. Wire into argparse dispatch.

