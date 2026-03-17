---
id: aa-yilt
status: closed
deps: [aa-74g3]
links: []
created: 2026-03-17T17:13:35Z
type: task
priority: 2
assignee: cristos
tags: [spec:SPEC-059]
---
# GREEN — Implement scanner availability checker

Implement scanner_availability.py at skills/swain-security-check/scripts/scanner_availability.py. Per-scanner PATH detection, OS detection (Darwin/Linux), install command generation, semgrep uv-run fallback. Must complete in <1s with no network calls.


## Notes

**2026-03-17T17:15:59Z**

GREEN phase complete. Implemented scanner_availability.py at skills/swain-security-check/scripts/scanner_availability.py. All 27 tests pass in 0.02s. Features: ScannerResult dataclass, check_scanner (PATH check), check_semgrep (PATH + uv fallback), detect_os (Darwin/Linux), get_install_command per OS, check_all_scanners aggregate, format_report for doctor output, CLI entry point.
