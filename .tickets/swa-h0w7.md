---
id: swa-h0w7
status: closed
deps: []
links: []
created: 2026-03-17T17:10:22Z
type: epic
priority: 1
assignee: Cristos L-C
external-ref: SPEC-058
---
# Implement SPEC-058: Context-File Injection Heuristic Scanner

Build a standalone regex-based scanner for agentic context files (AGENTS.md, CLAUDE.md, .cursorrules, etc.) that detects prompt injection patterns across 10 categories (A-J) defined in SPIKE-020. Output: JSON findings with file path, line number, category, severity, and description. Zero external deps beyond Python 3 stdlib. Exit codes: 0=clean, 1=findings, 2=error.


## Notes

**2026-03-17T18:10:41Z**

Complete: implementation merged from worktree-agent-a4230991. 144 tests passing.
