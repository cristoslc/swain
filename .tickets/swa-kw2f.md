---
id: swa-kw2f
status: open
deps: [swa-wien]
links: []
created: 2026-03-13T23:28:32Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# Integration: verify xref against known repo discrepancies

Run specgraph.py build then specgraph.py xref on the live repo. Verify known discrepancies are detected (check body mentions vs frontmatter for a sample of artifacts). Verify no false positives from non-artifact patterns. Verify --json output parses correctly. Final acceptance gate for SPEC-032.

