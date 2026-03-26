---
id: s1gsf-78db
status: closed
deps: [s1gsf-kuzk]
links: []
created: 2026-03-26T02:25:29Z
type: task
priority: 2
assignee: cristos
parent: s1gsf-t0yb
tags: [spec:SPEC-168]
---
# Add advisory to swain-preflight.sh

Add lightweight non-blocking advisory check to preflight script: if not swain repo and skill folders exist but are not gitignored, emit advisory.


## Notes

**2026-03-26T02:28:05Z**

Added check 9c to preflight: non-blocking advisory when skill folders exist but are not gitignored. Swain self-detection skips the check.
