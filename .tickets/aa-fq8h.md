---
id: aa-fq8h
status: closed
deps: [aa-2t3i, aa-grtp, aa-wp4f]
links: []
created: 2026-03-17T17:13:05Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-062, tdd:green]
---
# GREEN — Implement threat surface detection function

Implement detect_threat_surface() in skills/swain-security-check/scripts/threat_surface.py to pass all RED tests. Input: task metadata (title, description, tags, spec_criteria, file_paths). Output: is_security_sensitive bool + matched categories list.


## Notes

**2026-03-17T17:17:12Z**

GREEN confirmed: 59/59 tests pass. Implementation covers all 4 detection signals: tag-based (4 security tags), keyword-based (14 keywords via compiled regex with stem matching), spec-criteria scanning, and file-path pattern matching (auth/, crypto/, middleware/auth, .env*, credentials*, secret*, dependency manifests). Categories are deduplicated and sorted. False positive rate: 0/20 (0%).
