---
id: aa-6hlo
status: closed
deps: [aa-yilt]
links: []
created: 2026-03-17T17:13:35Z
type: task
priority: 2
assignee: cristos
tags: [spec:SPEC-059]
---
# GREEN — Implement swain-doctor scanner diagnostic

Add scanner availability diagnostic to swain-doctor. INFO severity, non-blocking. Should report missing scanners with install hints.


## Notes

**2026-03-17T17:17:00Z**

GREEN phase complete. Added scanner availability check to swain-preflight.sh as check #11. INFO severity, non-blocking (advisory only, does not add to issues[] array). Verified: preflight exits 0 when only scanner issues present. Added 3 format_report tests. All 30 tests pass. Real system test shows 2/4 scanners found on this machine (gitleaks, semgrep via uv).
