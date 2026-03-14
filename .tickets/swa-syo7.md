---
id: swa-syo7
status: open
deps: [swa-mnln, swa-v45a, swa-t89z, swa-55pl, swa-cij6, swa-dfgu, swa-4bn2]
links: []
created: 2026-03-13T23:27:46Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# Wire all subcommands into CLI dispatch

Update cli.py to dispatch each subcommand to its queries.py function. Pass show_all and show_all_edges flags. Pass repo_root for filesystem checks (scope architecture-overview.md). Remove placeholder stubs.

