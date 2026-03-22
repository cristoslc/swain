---
id: s1wd-pouq
status: closed
deps: [s1wd-knv4]
links: []
created: 2026-03-22T05:28:00Z
type: task
priority: 2
assignee: cristos
parent: s1wd-kjcb
tags: [spec:SPEC-148]
---
# Write test for swain-doctor skill-change detection

RED: Write test that simulates trunk commits touching skill files with varying diff sizes. Test must verify non-trivial changes emit warnings and trivial changes pass clean.


## Notes

**2026-03-22T05:30:28Z**

RED: 5 tests written, all fail (script not found). Test covers: non-trivial detection, trivial pass-through, multi-file, non-skill files, version bumps.
