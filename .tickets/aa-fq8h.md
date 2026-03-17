---
id: aa-fq8h
status: open
deps: [aa-2t3i, aa-grtp, aa-wp4f]
links: []
created: 2026-03-17T17:13:05Z
type: task
priority: 1
assignee: Cristos L-C
tags: [spec:SPEC-062, tdd:green]
---
# GREEN — Implement threat surface detection function

Implement detect_threat_surface() in skills/swain-security-check/scripts/threat_surface.py to pass all RED tests. Input: task metadata (title, description, tags, spec_criteria, file_paths). Output: is_security_sensitive bool + matched categories list.

