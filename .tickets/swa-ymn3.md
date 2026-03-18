---
id: swa-ymn3
status: closed
deps: [swa-8t7a, swa-y6fi, swa-f3eb]
links: []
created: 2026-03-18T11:54:33Z
type: task
priority: 2
assignee: cristos
parent: swa-62fm
tags: [spec:SPEC-067]
---
# Write test suite for swain-box (all 12 ACs)

Write shell-based tests covering: AC-1 docker missing, AC-2 docker sandbox unavailable, AC-3 PWD default, AC-4 explicit path, AC-5 missing path rejected, AC-6 sandbox idempotency, AC-7 API key forwarding, AC-8 Max sub CLAUDE_CODE_OAUTH_TOKEN path, AC-9 --docker removed, AC-10 dockerfile removed, AC-11 Tier 1 unaffected, AC-12 shell function documented. Tests in scripts/test-swain-box.sh or similar.


## Notes

**2026-03-18T12:01:38Z**

20/20 tests pass. scripts/test-swain-box.sh covers all 12 ACs. Uses PATH-injected fake docker binary for isolation. Handles macOS /tmp symlink edge case.
