---
id: aa-2t3i
status: closed
deps: []
links: []
created: 2026-03-17T17:12:53Z
type: task
priority: 1
assignee: cristos
tags: [spec:SPEC-062, tdd:red]
---
# RED — Write tests for keyword-based threat surface detection

Write failing tests for title keyword detection in threat_surface.py. Keywords: auth, login, password, token, secret, key, encrypt, certificate, permission, role, sanitize, validate, escape. Test that 'Add JWT token validation middleware' returns is_security_sensitive=true with category auth.


## Notes

**2026-03-17T17:14:03Z**

RED confirmed: 17 keyword tests fail against stub, 3 non-security tests pass. Tests cover all 14 spec keywords, case insensitivity, category dedup, multi-category, and 3 negative cases.
