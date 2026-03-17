---
id: aa-grtp
status: closed
deps: []
links: []
created: 2026-03-17T17:13:05Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-062, tdd:red]
---
# RED — Write tests for tag-based and SPEC-criteria detection

Write failing tests for tag-based detection (security, auth, crypto, input-validation tags) and SPEC acceptance criteria keyword matching. Task with tag 'security' should always be true regardless of title.


## Notes

**2026-03-17T17:14:43Z**

RED confirmed: 12 tests fail against stub (6 tag-based, 6 spec-criteria), 4 pass (non-security and edge cases). Covers security/auth/crypto/input-validation tags, mixed tags, criteria keywords, case insensitivity.
