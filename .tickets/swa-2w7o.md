---
id: swa-2w7o
status: closed
deps: [swa-vdow, swa-gumr]
links: []
created: 2026-03-17T18:11:23Z
type: task
priority: 1
assignee: cristos
parent: swa-hlaj
tags: [spec:SPEC-060]
---
# GREEN: Implement scanner orchestration and report compilation

Wire context_file_scanner.py, scanner_availability.py, and external scanner CLIs. Normalize all findings. JSON+markdown output.


## Notes

**2026-03-17T18:18:21Z**

GREEN complete: security_check.py implemented at skills/swain-security-check/scripts/security_check.py. All 43 tests pass. All 283 tests in repo pass. Implements: run_scan() orchestrator, gitleaks/semgrep/osv-scanner/trivy integration, context-file-scanner integration, repo-hygiene checks (.gitignore + tracked .env), bucket_by_severity(), format_summary_line(), format_json_report(), format_markdown_report(), main() CLI with exit codes 0/1/2.
