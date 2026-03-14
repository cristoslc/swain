---
id: swa-c9lc
status: open
deps: []
links: []
created: 2026-03-13T23:28:02Z
type: task
priority: 1
assignee: Cristos L-C
parent: swa-1wrf
tags: [spec:SPEC-032]
---
# RED: Body scanner tests

Write failing tests for body text ID extraction. Cases: basic TYPE-NNN patterns, self-references (excluded), non-artifact patterns like UTF-8/SHA-256 (filtered by known-ID check), IDs in code blocks, IDs in URLs, multiple mentions of same ID (deduped). Function signature: scan_body(body_text, known_ids, self_id) -> set[str].

