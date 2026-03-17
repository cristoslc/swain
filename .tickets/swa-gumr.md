---
id: swa-gumr
status: closed
deps: []
links: []
created: 2026-03-17T18:11:23Z
type: task
priority: 1
assignee: cristos
parent: swa-hlaj
tags: [spec:SPEC-060]
---
# RED: Write tests for unified report format (JSON + markdown)

Test severity bucketing, per-finding format (source scanner, file, line, description, remediation), and summary line.


## Notes

**2026-03-17T18:15:43Z**

RED complete: Tests for unified report format included in tests/test_security_check.py — TestUnifiedFindingFormat (required fields, severity validation), TestSeverityBucketing, TestSummaryLine, TestJSONReport (structure, valid JSON, fields, counts), TestMarkdownReport (summary, findings, skipped, remediation), TestExitCodes (0/1/2, --json flag). All fail as expected.
