---
id: swa-mrut
status: closed
deps: [swa-jspu]
links: []
created: 2026-03-17T18:11:23Z
type: task
priority: 1
assignee: cristos
parent: swa-hlaj
tags: [spec:SPEC-060]
---
# REFACTOR: Verify all acceptance criteria and clean up

End-to-end verification. Repo-level hygiene checks (gitignore, tracked secrets).


## Notes

**2026-03-17T18:20:06Z**

REFACTOR complete. All SPEC-060 acceptance criteria verified:
1. Gitleaks findings normalized with remediation (test_gitleaks_findings_normalized)
2. OSV-scanner invocation for CVE scanning (test_osv_scanner_invocation)
3. Context-file injection findings alongside scanner findings (test_context_file_scanner_always_runs, test_context_file_findings_normalized)
4. Semgrep ai-best-practices config (test_semgrep_invocation, test_semgrep_findings_normalized)
5. Missing scanner skipped with hint (test_missing_scanner_appears_in_skipped)
6. SKILL.md created with valid frontmatter
7. JSON + markdown report outputs (TestJSONReport, TestMarkdownReport classes)
Script executable, end-to-end smoke test passes, all 283 repo tests pass.
