---
id: swa-qx7a
status: closed
deps: [swa-v8ib, swa-89y9]
links: []
created: 2026-03-17T18:11:24Z
type: task
priority: 1
assignee: cristos
parent: swa-vc4x
tags: [spec:SPEC-061]
---
# GREEN: Implement lightweight security diagnostic for swain-doctor

Script that runs critical-only context scan + tracked .env check. Outputs WARN/CRIT diagnostics in swain-doctor format.


## Notes

**2026-03-17T18:16:46Z**

GREEN complete: doctor_security_check.py implemented with scan_context_files_critical(), detect_tracked_env_files(), format_diagnostics(), format_env_diagnostics(), main(). Preflight check #12 added. All 270 tests pass (30 new + 240 existing).
