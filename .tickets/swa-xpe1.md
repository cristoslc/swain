---
id: swa-xpe1
status: closed
deps: []
links: []
created: 2026-03-13T23:26:49Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-n4vm
tags: [spec:SPEC-031]
---
# RED: OSC 8 link helper tests

Write failing tests for art_link, file_link, artifact_link helpers. Test TTY detection gating (escape sequences emitted when isatty, plain text when not). Test link formatting matches bash output.


## Notes

**2026-03-14T04:08:19Z**

Completed: implemented in 6eb4eea (specgraph Python rewrite). All 118 tests pass.
