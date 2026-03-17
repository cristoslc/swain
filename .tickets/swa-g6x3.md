---
id: swa-g6x3
status: closed
deps: [swa-30s7, swa-maj1]
links: []
created: 2026-03-17T18:11:24Z
type: task
priority: 1
assignee: cristos
parent: swa-cdhc
tags: [spec:SPEC-063]
---
# GREEN: Implement security briefing generator with OWASP reference data

Python module with category-to-OWASP mapping and markdown output. Bundled reference data, no external deps.


## Notes

**2026-03-17T18:15:08Z**

GREEN confirmed: 42/42 tests pass, 282/282 total tests pass with zero regressions. Implemented security_briefing.py with CATEGORY_GUIDANCE mapping (auth->A07, input-validation->A03, crypto->A02, external-data->A08, agent-context->swain-specific, dependency-change->A06, secrets->A07+specific) and generate_security_briefing() that delegates to detect_threat_surface() and produces markdown output.
