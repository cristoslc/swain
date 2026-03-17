---
id: aa-xyxy
status: closed
deps: []
links: []
created: 2026-03-17T17:12:36Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-058]
---
# RED — Tests for categories E-G (persistence, encoding obfuscation, hidden Unicode)

Write pytest tests for context file scanner categories E (persistence mechanisms), F (base64/encoding obfuscation), G (hidden Unicode). SPEC-058.


## Notes

**2026-03-17T17:14:58Z**

RED complete: 32 tests fail (E=12, F=9, G=11 detection), 5 pass (benign/negative). All expected to fail pending GREEN implementation.
